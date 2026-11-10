# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import concurrent.futures
import difflib
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from agent.runner import create_workbench_draft_record
from agent.template_check import CHECK_STAGES, TemplateCheckError
from agent.template_pipeline import (
    TemplatePipelineError,
    TemplatePipelineService,
)
from agent.template_policy import (
    overlap_policy_result,
    rigid_seed_detail,
)
from agent.template_registry import TEMPLATE_REGISTRY
from agent.template_sweep import (
    DEFAULT_COMPILE_TIMEOUT_S,
    DEFAULT_PASS_THRESHOLD,
    DEFAULT_SEED_COUNT,
    disconnected_geometry_warning_details,
    parse_seed_spec,
    report_to_json,
    run_sweep,
    stderr_progress_reporter,
    write_report,
)
from articraft.materialization import AssetExportError, export_template_assets
from cli.common import add_data_root_argument, warn_if_post_commit_hook_missing
from cli.external import _compile_record, _refresh_external_record, _validate_external_record
from storage.collections import CollectionStore
from storage.dataset_workflow import promote_record_workflow
from storage.datasets import DatasetStore
from storage.queries import StorageQueries
from storage.records import RecordStore
from storage.repo import StorageRepo
from storage.revisions import active_model_path
from storage.search import SearchIndex

ALLOWED_EXTERNAL_AGENTS = ("codex", "claude-code")
DEFAULT_PROVIDER_BY_AGENT = {
    "codex": "openai",
    "claude-code": "anthropic",
}

GENERIC_MODEL_TEMPLATE = """from __future__ import annotations

import agent.templates.{slug} as _template_module
from agent.templates.{slug} import (
    build_{stem},
    config_from_seed,
    run_{stem}_tests,
)
from sdk import AssetContext

SEED = {seed}
CONFIG = config_from_seed(SEED)
ASSETS = AssetContext.from_script(__file__)
TEMPLATE_DOMAIN = getattr(_template_module, "TEMPLATE_DOMAIN", None)


def build_object_model():
    return build_{stem}(CONFIG, assets=ASSETS)


def run_tests():
    return run_{stem}_tests(object_model, CONFIG)


object_model = build_object_model()
"""


def _write_template_model(model_path: Path, *, slug: str, stem: str, seed: int) -> None:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    body = GENERIC_MODEL_TEMPLATE.format(slug=slug, stem=stem, seed=seed)
    model_path.write_text(body, encoding="utf-8")


def batch_template(
    repo_root: Path,
    *,
    slug: str,
    stem: str,
    seeds: list[int],
    agent: str,
    category_slug: str | None,
    dry_run: bool,
    max_workers: int | None = None,
) -> int:
    if dry_run:
        for seed in seeds:
            prompt = f"seeded {slug} {seed}"
            print(f"[seed={seed}] dry-run: would create record for prompt={prompt!r}")
        print(f"batch dry-run completed for {len(seeds)} seed(s)")
        return 0

    repo = StorageRepo(repo_root)
    repo.ensure_layout()
    provider = DEFAULT_PROVIDER_BY_AGENT[agent]
    record_store = RecordStore(repo)
    failures: list[str] = []

    workers = max_workers if max_workers is not None else min(len(seeds), 8)
    workers = max(1, min(workers, len(seeds)))

    # One compile per seed, in three phases:
    #   1. serial, fast I/O: create each seed's draft record + write model.py.
    #   2. parallel, slow CPU: compile each record ONCE at target="full" with
    #      validate + motion QC, each in its own timeout subprocess (SIGKILL on
    #      hang) so one degenerate seed cannot wedge the batch. That single
    #      compile does BOTH jobs the old two-pass flow split apart -- the
    #      gate's acceptance checks (full baseline + motion QC) AND materializing
    #      the record's collision-inclusive ("full") assets.
    #   3. serial, fast I/O: accept (finalize) or reject (delete record) each
    #      seed. A rejected seed leaves no orphan draft, matching the old gate
    #      which rejected before any record was materialized.
    # Shared-state writes (record create/finalize/delete, dataset promote,
    # search index) all stay serial; only the per-record compile -- which writes
    # only into its own materialization cache -- runs in parallel.
    print(
        f"generating {len(seeds)} seed(s) for {slug} "
        f"(one full compile + motion QC per seed, {workers} workers)..."
    )

    # Phase 1: create drafts + write model.py (serial).
    prepared: list[tuple[int, str, Path]] = []
    for seed in seeds:
        prompt = f"seeded {slug} {seed}"
        try:
            record_dir = create_workbench_draft_record(
                repo_root=repo_root,
                prompt_text=prompt,
                provider=provider,
                model_id=None,
                thinking_level=None,
                sdk_package="sdk",
                label=f"{stem}_seed_{seed}",
                tags=["template_batch", slug],
                record_id=None,
                external_agent=agent,
            )
        except ValueError as exc:
            failures.append(f"seed={seed}: init failed: {exc}")
            continue
        record_id = record_dir.name
        _write_template_model(active_model_path(repo, record_id), slug=slug, stem=stem, seed=seed)
        prepared.append((seed, record_id, record_dir))

    # Phase 2: compile each record (parallel, timeout-isolated subprocess).
    def _compile_seed(item: tuple[int, str, Path]) -> tuple[int, int, str | None]:
        seed, _record_id, record_dir = item
        try:
            status = _compile_record(
                repo_root,
                record_dir,
                target="full",
                validate=True,
                motion_qc=True,
                use_compile_timeout=True,
            )
            return seed, status, None
        except Exception as exc:  # noqa: BLE001 — isolate a per-seed compile crash
            return seed, 1, str(exc)

    compile_status: dict[int, tuple[int, str | None]] = {}
    if prepared:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            for seed, status, err in executor.map(_compile_seed, prepared):
                compile_status[seed] = (status, err)

    # Phase 3: accept or reject each seed (serial).
    for seed, record_id, _record_dir in prepared:
        status, err = compile_status[seed]
        if status != 0:
            record_store.delete_record(record_id)
            detail = f": {err}" if err else ""
            failures.append(
                f"seed={seed}: rejected (compile/QC failed){detail}; removed {record_id}"
            )
            print(f"[seed={seed}] REJECTED (compile/QC failed); record removed")
            continue

        errors = _validate_external_record(repo, record_id)
        if errors:
            record_store.delete_record(record_id)
            failures.append(
                f"seed={seed}: rejected (validation failed): {'; '.join(errors)}; "
                f"removed {record_id}"
            )
            print(f"[seed={seed}] REJECTED (validation failed); record removed")
            continue

        if category_slug:
            _refresh_external_record(
                repo,
                record_id,
                final_status="external_finalized",
            )
            try:
                entry, category, _, _stats = promote_record_workflow(
                    repo,
                    DatasetStore(repo),
                    StorageQueries(repo),
                    record_id=record_id,
                    category_title=None,
                    category_slug=category_slug,
                    dataset_id=None,
                    promoted_at=datetime.now(timezone.utc)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z"),
                )
            except ValueError as exc:
                failures.append(f"seed={seed}: promote failed for {record_id}: {exc}")
                continue
            CollectionStore(repo).ensure_workbench()
            print(
                f"[seed={seed}] finalized into category={category.get('slug') or category_slug}: "
                f"{record_id} dataset_id={entry.get('dataset_id')}"
            )
        else:
            _refresh_external_record(repo, record_id, final_status="external_ready")
            print(f"[seed={seed}] ready: {record_id}")

    stats = SearchIndex(repo).rebuild()
    print(
        f"search_index={stats.path} records={stats.record_count} "
        f"categories={stats.category_count} workbench_entries={stats.workbench_entry_count}"
    )

    if failures:
        print("batch completed with failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"batch completed successfully for {len(seeds)} seed(s)")
    return 0


def _strip_build_cache(seed_dir: Path) -> None:
    """Remove CadQuery's build cache from an exported seed.

    The cache sits under ``assets/.cadquery_cache/`` and holds duplicate copies
    of meshes that are already written to ``assets/meshes/``, so shipping it
    would roughly double each seed's mesh bytes for no benefit.
    """
    cache_dir = seed_dir / "assets" / ".cadquery_cache"
    if cache_dir.exists():
        shutil.rmtree(cache_dir, ignore_errors=True)


def _gen_one_seed(
    slug: str,
    stem: str,
    seed: int,
    seed_dir: Path,
    motion_qc: bool = True,
) -> tuple[int, bool, str | None]:
    """Materialize one seed into ``seed_dir``. Returns (seed, ok, error).

    The compile runs in a timeout-isolated subprocess so a seed that hangs in
    non-interruptible geometry QC is SIGKILL'd and skipped rather than wedging
    the whole run. Writing ``model.py`` inside ``seed_dir`` makes the SDK's
    asset session root that directory, so generated meshes land beside it and
    the URDF references them relatively -- the seed folder is self-contained.

    ``motion_qc=False`` drops the sampled-pose gate only. The rest-pose contract
    is untouched: the authored tests still run overlap and isolated-part checks
    in the current pose, the rigid-body and disconnected-geometry rejections
    still apply, and a seed that compiles into an unarticulated body is still
    refused. What it gives up is exactly the actuated-pose collision sweep.
    """
    from agent.compiler import compile_urdf_report_maybe_timeout

    try:
        seed_dir.mkdir(parents=True, exist_ok=True)
        script = seed_dir / "model.py"
        script.write_text(
            GENERIC_MODEL_TEMPLATE.format(slug=slug, stem=stem, seed=seed), encoding="utf-8"
        )
        report = compile_urdf_report_maybe_timeout(
            script,
            sdk_package="sdk",
            run_checks=True,
            ignore_geom_qc=False,
            target="full",
            motion_qc=motion_qc,
        )
        overlap_policy = overlap_policy_result(
            repo_root=Path(__file__).resolve().parents[1],
            slug=slug,
            allowances=getattr(
                getattr(report, "test_report", None),
                "allowances",
                (),
            ),
        )
        if overlap_policy["detail"] is not None:
            return (
                seed,
                False,
                overlap_policy["detail"],
            )
        # Same keep/reject rules the template check uses, so gen-seeds can never
        # export a seed the mechanical checker would reject.
        rigid = rigid_seed_detail(report.urdf_xml or "")
        if rigid:
            return seed, False, f"RigidSeed: {rigid}"
        # A part that fell into islands is a broken asset, and the compiler only
        # warns about it.
        disconnected = disconnected_geometry_warning_details(report.warnings or ())
        if disconnected:
            return seed, False, f"DisconnectedGeometry: {disconnected}"
        (seed_dir / "model.urdf").write_text(report.urdf_xml, encoding="utf-8")
        (seed_dir / "compile_report.json").write_text(
            json.dumps(report.signal_bundle.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        _strip_build_cache(seed_dir)
        return seed, True, None
    except Exception as exc:  # noqa: BLE001 — isolate a per-seed failure
        return seed, False, f"{type(exc).__name__}: {exc}"


def gen_seeds(
    *,
    slug: str,
    stem: str,
    seeds: list[int],
    out_root: Path,
    export_namespace: str | None = None,
    max_workers: int | None = None,
    motion_qc: bool = True,
) -> int:
    """Generate seeds straight into a clean per-category export tree.

    Unlike ``batch``, this touches no record store and no search index: each
    seed is a self-contained folder under ``<out>/<export_namespace>/seed_<n>/``. Seeds are
    regenerable from (slug, seed), so the export is disposable output rather
    than canonical data.
    """
    out_root.mkdir(parents=True, exist_ok=True)
    namespace = export_namespace or slug
    relative_namespace = Path(namespace)
    if (
        relative_namespace.is_absolute()
        or not relative_namespace.parts
        or ".." in relative_namespace.parts
    ):
        raise ValueError("export_namespace must be a safe relative path")
    final_category_dir = out_root / relative_namespace
    final_category_dir.parent.mkdir(parents=True, exist_ok=True)
    staging_root = out_root / ".staging"
    staging_root.mkdir(parents=True, exist_ok=True)
    category_dir = Path(tempfile.mkdtemp(prefix=f"{slug}-", dir=staging_root))

    workers = max_workers if max_workers is not None else min(len(seeds), 8)
    workers = max(1, min(workers, len(seeds)))
    gate = "motion QC" if motion_qc else "rest-pose checks only"
    print(
        f"gen-seeds {slug}: {len(seeds)} seed(s) -> staged for {final_category_dir} "
        f"(one full compile + {gate} per seed, {workers} workers)"
    )

    results: list[tuple[int, bool, str | None]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(
            executor.map(
                lambda seed: _gen_one_seed(
                    slug, stem, seed, category_dir / f"seed_{seed}", motion_qc
                ),
                seeds,
            )
        )

    kept = [seed for seed, ok, _ in results if ok]
    rejected = [(seed, err) for seed, ok, err in results if not ok]

    # Formal exports are all-or-nothing. A partial replacement would make a
    # category look current even though some requested seeds failed QC.
    rejected_path = out_root / "_rejected" / f"{slug}.jsonl"
    if rejected:
        rejected_path.parent.mkdir(parents=True, exist_ok=True)
        with rejected_path.open("a", encoding="utf-8") as handle:
            for seed, err in rejected:
                handle.write(json.dumps({"seed": seed, "error": err}) + "\n")
                print(f"[seed={seed}] REJECTED: {(err or '')[:160]}")

    print(f"gen-seeds {slug}: kept {len(kept)}/{len(seeds)}, rejected {len(rejected)}")
    if rejected:
        print(f"  rejected seeds logged to {rejected_path}")
        shutil.rmtree(category_dir, ignore_errors=True)
        print(f"gen-seeds {slug}: existing export left unchanged", file=sys.stderr)
        return 1

    backup_dir = staging_root / f"{slug}-previous"
    shutil.rmtree(backup_dir, ignore_errors=True)
    try:
        if final_category_dir.exists():
            final_category_dir.replace(backup_dir)
        category_dir.replace(final_category_dir)
    except Exception:
        if backup_dir.exists() and not final_category_dir.exists():
            backup_dir.replace(final_category_dir)
        raise
    finally:
        shutil.rmtree(backup_dir, ignore_errors=True)
    print(f"gen-seeds {slug}: atomically replaced {final_category_dir}")
    return 0


def batch_ferris_wheel(
    repo_root: Path,
    *,
    seeds: list[int],
    agent: str,
    category_slug: str | None,
    dry_run: bool,
) -> int:
    return batch_template(
        repo_root,
        slug="ferris_wheel",
        stem=TEMPLATE_REGISTRY["ferris_wheel"],
        seeds=seeds,
        agent=agent,
        category_slug=category_slug,
        dry_run=dry_run,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="articraft template")
    add_data_root_argument(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)

    batch = subparsers.add_parser(
        "batch", help="Batch-generate records from a procedural template."
    )
    batch_sub = batch.add_subparsers(dest="template_name", required=True)

    for slug in TEMPLATE_REGISTRY:
        sp = batch_sub.add_parser(slug, help=f"Batch-generate seeded {slug} records.")
        sp.add_argument(
            "--seeds",
            required=True,
            help="Seed list/ranges, e.g. '1-20' or '1,3,5-8'.",
        )
        sp.add_argument("--agent", default="codex", choices=ALLOWED_EXTERNAL_AGENTS)
        sp.add_argument(
            "--category-slug",
            default=None,
            help="Optional dataset category slug. When set, records are finalized and promoted.",
        )
        sp.add_argument(
            "--dry-run",
            action="store_true",
            help="Print the planned batch without creating records.",
        )
        sp.add_argument(
            "--max-workers",
            type=int,
            default=None,
            help=(
                "Parallel compile workers for the per-seed compiles. Defaults to "
                "min(len(seeds), 8). Raise it when generating one category at a "
                "time; keep it low when fanning out many categories in parallel "
                "(outer parallelism x this must not oversubscribe the cores)."
            ),
        )

    gen = subparsers.add_parser(
        "gen-seeds",
        help=(
            "Generate seeds into a clean per-category export tree. Unlike `batch`, "
            "this writes no records and touches no search index."
        ),
    )
    # No `choices=` here: the registry is ~500 entries and would bury the help
    # text. Slugs are validated in main() with a targeted error instead.
    gen.add_argument(
        "slugs",
        nargs="*",
        metavar="SLUG",
        help="One or more template slugs. Omit when using --all.",
    )
    gen.add_argument(
        "--all",
        action="store_true",
        help="Generate for every template in the registry.",
    )
    gen.add_argument(
        "--seeds",
        required=True,
        help="Seed list/ranges, e.g. '0-99' or '1,3,5-8'.",
    )
    gen.add_argument(
        "--out",
        type=Path,
        required=True,
        help=(
            "Export root (keep it outside the repo; seeds are regenerable output, "
            "not canonical data). Seeds land in <out>/<slug>/seed_<n>/. "
            "Suggested: /tmp/rfwa-seed-exports"
        ),
    )
    gen.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help=(
            "Parallel compile workers. Defaults to min(len(seeds), 8). Keep it low "
            "when fanning out many categories in parallel (outer parallelism x this "
            "must not oversubscribe the cores)."
        ),
    )
    gen.add_argument(
        "--no-motion-qc",
        action="store_true",
        help=(
            "Drop the sampled-pose (actuated) collision gate. Rest-pose overlap, "
            "isolated-part, disconnected-geometry, and rigid-body rejections all "
            "still apply, so exported seeds are still articulated and still clean "
            "at rest -- they are simply not proven collision-free while moving."
        ),
    )

    export_assets = subparsers.add_parser(
        "export-assets",
        help="Compile ordinary template seeds with portable PBR appearance and physics JSON.",
    )
    export_assets.add_argument("slug", help="Template module slug registered in TEMPLATE_REGISTRY.")
    export_assets.add_argument(
        "--seeds",
        required=True,
        help="Seed list/ranges, e.g. '0-9' or '1,3,5-8'.",
    )
    export_assets.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Export root; outputs are written to <out>/<slug>/seed_<n>/.",
    )
    export_assets.add_argument(
        "--material-seed",
        type=int,
        default=None,
        help="Optional shared material seed. By default each geometry seed is used.",
    )
    export_assets.add_argument(
        "--library-pointer",
        type=Path,
        default=None,
        help="Unified library pointer; defaults to pbr_material_library/unified/latest.json.",
    )

    sweep = subparsers.add_parser(
        "compile-sweep",
        help="Run multi-seed full-baseline compile sweep for a procedural template.",
    )
    sweep.add_argument("slug", choices=sorted(TEMPLATE_REGISTRY.keys()))
    sweep.add_argument(
        "--seeds",
        default=f"0-{DEFAULT_SEED_COUNT - 1}",
        help=(f"Seed list/ranges; defaults to '0-{DEFAULT_SEED_COUNT - 1}' (DEFAULT_SEED_COUNT)."),
    )
    sweep.add_argument(
        "--pass-threshold",
        type=float,
        default=DEFAULT_PASS_THRESHOLD,
        help=(f"Minimum pass_rate required for verdict=pass (default {DEFAULT_PASS_THRESHOLD})."),
    )
    sweep.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help=(
            "ProcessPoolExecutor worker count. Defaults to min(len(seeds), 8); "
            "use 1 to run sequentially in the current process."
        ),
    )
    sweep.add_argument(
        "--sdk-package", default="sdk", help="SDK package to load (defaults to 'sdk')."
    )
    sweep.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional file path to write the JSON report to (in addition to stdout).",
    )
    sweep.add_argument(
        "--state-dir",
        type=Path,
        default=None,
        help=(
            "Directory to persist per-slug streak state across sweeps. "
            "Defaults to <repo_root>/.articraft/template_sweep_state when omitted. "
            "Pass an empty string to disable streak tracking."
        ),
    )
    sweep.add_argument(
        "--compile-timeout",
        type=float,
        default=DEFAULT_COMPILE_TIMEOUT_S,
        help=(
            "Per-seed wall-time budget in seconds. Each seed compile runs in a "
            "fresh subprocess that is SIGKILL'd on timeout; the seed is marked "
            "compile_timeout in the JSON. Set to 0 to disable timeouts ("
            f"in-process ProcessPool path). Default {DEFAULT_COMPILE_TIMEOUT_S:.0f}s."
        ),
    )
    sweep.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-seed stderr progress lines.",
    )
    sweep.add_argument(
        "--no-motion-qc",
        action="store_true",
        help=(
            "Disable the harness-owned sampled-pose overlap gate "
            "(harness_motion_qc). By default every seed compile also checks "
            "part overlaps at joint-limit poses."
        ),
    )

    check = subparsers.add_parser(
        "check",
        help="Run cumulative random-16, random-36, or corner template checks.",
    )
    check.add_argument("slug", help="Template module slug registered in TEMPLATE_REGISTRY.")
    check.add_argument("--stage", required=True, choices=CHECK_STAGES)
    check.add_argument(
        "--pass-threshold",
        type=float,
        default=DEFAULT_PASS_THRESHOLD,
        help=(
            f"Minimum cumulative random pass rate (default {DEFAULT_PASS_THRESHOLD}). "
            "Design-backed strict templates enforce a floor of 0.90."
        ),
    )
    check.add_argument("--max-workers", type=int, default=None)
    check.add_argument(
        "--compile-timeout",
        type=float,
        default=DEFAULT_COMPILE_TIMEOUT_S,
        help=f"Per-seed wall-time budget (default {DEFAULT_COMPILE_TIMEOUT_S:.0f}s).",
    )
    check.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Cache root; defaults to <repo-root>/.cache/template_check.",
    )
    check.add_argument(
        "--expected-quality-contract-sha256",
        default=None,
        help=(
            "Expected pre-repair seed-quality contract. A mismatch blocks sweep "
            "and returns next_stage=preflight."
        ),
    )
    check.add_argument("--out", type=Path, default=None)
    check.add_argument("--quiet", action="store_true")

    source_map_init = subparsers.add_parser(
        "source-map-init",
        help="Scaffold a strict SourceMap covering every active source in one picture subcategory.",
    )
    source_map_init.add_argument("slug")
    source_map_init.add_argument("--records-root", type=Path, required=True)
    source_map_init.add_argument("--picture-category", required=True)
    source_map_init.add_argument("--picture-subcategory", required=True)
    source_map_init.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Defaults to articraft_template_authoring/source_maps/<slug>.md.",
    )

    source_map_check = subparsers.add_parser(
        "source-map-check",
        help="Strictly audit source coverage, reviews, candidates, revisions, and source spans.",
    )
    source_map_check.add_argument("--source-map", type=Path, required=True)
    source_map_check.add_argument("--records-root", type=Path, required=True)

    design = subparsers.add_parser(
        "design-init",
        help="Scaffold a compact TemplateDesign JSON from a complete strict SourceMap.",
    )
    design.add_argument("slug")
    design.add_argument("--source-map", type=Path, required=True)
    design.add_argument("--records-root", type=Path, required=True)
    design.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Defaults to articraft_template_authoring/designs/<slug>.json.",
    )

    return parser


def _resolve_state_dir(repo_root: Path, override: Path | None) -> Path | None:
    """Resolve the per-slug streak-state directory.

    Passing an empty string on the CLI maps to override=Path('') which we treat
    as 'disable streak tracking' (returns None). Otherwise default to
    `<repo_root>/.articraft/template_sweep_state`.
    """
    if override is None:
        return Path(repo_root) / ".articraft" / "template_sweep_state"
    text = str(override).strip()
    if not text or text == ".":
        return None
    return Path(text)


def compile_sweep(
    *,
    slug: str,
    stem: str,
    seeds: list[int],
    pass_threshold: float,
    max_workers: int | None,
    sdk_package: str,
    out_path: Path | None,
    state_dir: Path | None,
    compile_timeout_s: float,
    quiet: bool,
    motion_qc: bool = True,
) -> int:
    progress = None if quiet else stderr_progress_reporter(total=len(seeds))
    try:
        report = run_sweep(
            slug=slug,
            stem=stem,
            seeds=seeds,
            sdk_package=sdk_package,
            pass_threshold=pass_threshold,
            max_workers=max_workers,
            progress=progress,
            state_dir=state_dir,
            compile_timeout_s=compile_timeout_s,
            motion_qc=motion_qc,
        )
    except (FileNotFoundError, AttributeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    payload = report_to_json(report)
    print(payload)
    if out_path is not None:
        write_report(report, out_path=out_path)
    return 0 if report.verdict == "pass" else 1


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "export-assets":
        if args.slug not in TEMPLATE_REGISTRY:
            print(f"Unknown template slug: {args.slug}", file=sys.stderr)
            return 2
        try:
            seeds = parse_seed_spec(args.seeds)
            paths = export_template_assets(
                repo_root=args.repo_root,
                slug=args.slug,
                stem=TEMPLATE_REGISTRY[args.slug],
                seeds=seeds,
                out_root=args.out,
                material_seed=args.material_seed,
                library_pointer=args.library_pointer,
            )
        except (AssetExportError, FileExistsError, OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        for seed, path in zip(sorted(set(seeds)), paths, strict=True):
            print(f"exported seed={seed} path={path}")
        return 0

    if args.command == "source-map-init":
        out_path = args.out or (
            args.repo_root / "articraft_template_authoring" / "source_maps" / f"{args.slug}.md"
        )
        try:
            service = TemplatePipelineService(
                repo_root=args.repo_root,
                records_root=args.records_root,
            )
            payload = service.source_map_init(
                slug=args.slug,
                picture_category=args.picture_category,
                picture_subcategory=args.picture_subcategory,
                out_path=out_path,
            )
        except (OSError, TemplatePipelineError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if args.command == "source-map-check":
        service = TemplatePipelineService(
            repo_root=args.repo_root,
            records_root=args.records_root,
        )
        payload = service.source_map_check(
            slug=args.source_map.stem,
            source_map=args.source_map,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if payload["verdict"] == "pass" else 1

    if args.command == "design-init":
        out_path = args.out or (
            args.repo_root / "articraft_template_authoring" / "designs" / f"{args.slug}.json"
        )
        try:
            service = TemplatePipelineService(
                repo_root=args.repo_root,
                records_root=args.records_root,
            )
            payload = service.design_init(
                slug=args.slug,
                source_map=args.source_map.resolve(),
                out_path=out_path,
            )
        except (OSError, TemplatePipelineError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if args.command == "check":
        if args.slug not in TEMPLATE_REGISTRY:
            print(f"Unknown template slug: {args.slug}", file=sys.stderr)
            return 2
        progress = (
            None
            if args.quiet
            else stderr_progress_reporter(total=16 if args.stage == "random-16" else 36)
        )
        try:
            service = TemplatePipelineService(
                repo_root=args.repo_root,
                records_root=(args.repo_root / "data" / "records"),
            )
            report = service.run_check(
                slug=args.slug,
                stem=TEMPLATE_REGISTRY[args.slug],
                stage=args.stage,
                pass_threshold=float(args.pass_threshold),
                max_workers=None if args.max_workers is None else int(args.max_workers),
                compile_timeout_s=float(args.compile_timeout),
                cache_dir=args.cache_dir,
                progress=progress,
                expected_quality_contract_sha256=(args.expected_quality_contract_sha256),
            )
        except (OSError, AttributeError, TemplateCheckError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        payload = json.dumps(report, ensure_ascii=False, indent=2)
        print(payload)
        if args.out is not None:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(payload + "\n", encoding="utf-8")
        return 0 if report["verdict"] == "pass" else 1

    if args.command == "gen-seeds":
        try:
            seeds = parse_seed_spec(args.seeds)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2

        if args.all:
            if args.slugs:
                print("Pass either --all or explicit slugs, not both.", file=sys.stderr)
                return 2
            slugs = sorted(TEMPLATE_REGISTRY)
        elif args.slugs:
            slugs = list(args.slugs)
            unknown = [s for s in slugs if s not in TEMPLATE_REGISTRY]
            if unknown:
                print(f"Unknown template slug(s): {', '.join(unknown)}", file=sys.stderr)
                for slug in unknown:
                    near = difflib.get_close_matches(slug, TEMPLATE_REGISTRY, n=5, cutoff=0.6)
                    near += [
                        k for k in TEMPLATE_REGISTRY if slug.lower() in k.lower() and k not in near
                    ][:5]
                    if near:
                        print(f"  {slug} -> did you mean: {', '.join(near[:5])}", file=sys.stderr)
                return 2
        else:
            print("Pass at least one slug, or --all.", file=sys.stderr)
            return 2

        out_root = args.out.expanduser().resolve()
        workers = None if args.max_workers is None else int(args.max_workers)
        # Categories run one after another; the parallelism is across each
        # category's seeds. Driving many categories at once is still fine --
        # run this per slug under `xargs -P` for process-level isolation.
        failed: list[str] = []
        for slug in slugs:
            if gen_seeds(
                slug=slug,
                stem=TEMPLATE_REGISTRY[slug],
                seeds=seeds,
                out_root=out_root,
                export_namespace=slug,
                max_workers=workers,
                motion_qc=not args.no_motion_qc,
            ):
                failed.append(slug)
        if len(slugs) > 1:
            print(f"\ngen-seeds: {len(slugs) - len(failed)}/{len(slugs)} categories produced seeds")
            if failed:
                print(f"  no seeds kept for: {', '.join(failed)}")
        return 1 if failed else 0

    if args.command == "compile-sweep":
        try:
            seeds = parse_seed_spec(args.seeds)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        state_dir = _resolve_state_dir(args.repo_root, args.state_dir)
        return compile_sweep(
            slug=args.slug,
            stem=TEMPLATE_REGISTRY[args.slug],
            seeds=seeds,
            pass_threshold=float(args.pass_threshold),
            max_workers=(None if args.max_workers is None else int(args.max_workers)),
            sdk_package=str(args.sdk_package),
            out_path=args.out,
            state_dir=state_dir,
            compile_timeout_s=float(args.compile_timeout),
            quiet=bool(args.quiet),
            motion_qc=not bool(args.no_motion_qc),
        )

    if args.command != "batch" or args.template_name not in TEMPLATE_REGISTRY:
        parser.error("Unsupported template command")

    try:
        seeds = parse_seed_spec(args.seeds)
    except ValueError as exc:
        print(str(exc))
        return 1

    if not args.dry_run:
        warn_if_post_commit_hook_missing(args.repo_root)

    return batch_template(
        args.repo_root,
        slug=args.template_name,
        stem=TEMPLATE_REGISTRY[args.template_name],
        seeds=seeds,
        agent=args.agent,
        category_slug=str(args.category_slug or "").strip() or None,
        dry_run=bool(args.dry_run),
        max_workers=(None if args.max_workers is None else int(args.max_workers)),
    )
