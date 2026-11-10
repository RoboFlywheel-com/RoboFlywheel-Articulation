# SPDX-License-Identifier: Apache-2.0

"""RFW-A command line: author once, sample procedurally, validate before release."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from rfwa.generators import configuration, construction_provenance, describe, registered_stem
from rfwa.revision import check_generator, release_generator, write_json


def _print(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rfwa", description="RFW-A articulated generator toolkit")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="RFW-A source checkout")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("generators", help="list bundled generators; listing does not certify validity")
    inspect = sub.add_parser(
        "inspect", help="inspect blueprint, declared choices and resolved config"
    )
    inspect.add_argument("slug")
    config = sub.add_parser(
        "config", help="resolve a generator configuration without geometry or APIs"
    )
    config.add_argument("slug")
    config.add_argument("--seed", type=int, default=0)
    for name in ("check", "release"):
        cmd = sub.add_parser(
            name,
            help="check generation success rate (90% by default)"
            if name == "check"
            else "run all stages and gate generator release",
        )
        cmd.add_argument("slug")
        if name == "check":
            cmd.add_argument("--stage", choices=("random-16", "random-36", "corner"), required=True)
        cmd.add_argument("--state-root", type=Path, default=None)
        cmd.add_argument("--workers", type=int, default=1)
        cmd.add_argument("--timeout", type=float, default=120)
        cmd.add_argument(
            "--strict",
            action="store_true",
            help="require all cases, complete coverage and provenance",
        )
        cmd.add_argument("--pass-threshold", type=float, default=0.90)
    sample = sub.add_parser("sample", help="build deterministic seeds without model inference")
    sample.add_argument("slug")
    sample.add_argument(
        "--seeds", default="0", help="comma-separated seeds or inclusive ranges, e.g. 0-3,9"
    )
    sample.add_argument("--out", type=Path, required=True)
    sample.add_argument("--workers", type=int, default=1)
    sample.add_argument("--timeout", type=float, default=120)
    sample.add_argument(
        "--library-pointer",
        type=Path,
        help="frozen material-library latest.json; enables PBR/physics export",
    )
    sample.add_argument("--material-seed", type=int, default=None)
    imp = sub.add_parser(
        "import-source", help="copy an existing source record, preserving metadata"
    )
    imp.add_argument("--from-repo", type=Path, required=True)
    imp.add_argument("record_ids", nargs="+")
    # Keep command-specific help and flags owned by the working inherited engines.
    for name, help_text in (
        ("author", "source-map-init/check, design-init and pipeline-status authoring tools"),
        ("source", "source-asset generation, external agent workflow and record management"),
        ("edit", "directed component, count, material and dimensional editing"),
    ):
        cmd = sub.add_parser(name, help=help_text, add_help=False)
        cmd.add_argument("args", nargs=argparse.REMAINDER)
    return parser


def _sample(args: argparse.Namespace, root: Path) -> int:
    from agent.template_check import mechanical_hash
    from agent.template_sweep import parse_seed_spec, run_seed_outcomes

    stem = registered_stem(args.slug)
    seeds = parse_seed_spec(args.seeds)
    if not seeds:
        raise ValueError("at least one seed is required")
    output = args.out.expanduser().resolve()
    manifest = output / "sampling.json"
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"sampling output must be empty: {output}")
    if args.material_seed is not None and args.library_pointer is None:
        raise ValueError("--material-seed requires --library-pointer")
    if args.library_pointer is not None:
        from articraft.materialization import export_template_assets

        # The material exporter intentionally leaves mechanical checks to its caller.
        # Validate the requested seeds before binding appearance/physical annotations.
        with tempfile.TemporaryDirectory(prefix="rfwa-material-validation-", dir="/tmp") as raw:
            outcomes = run_seed_outcomes(
                slug=args.slug,
                stem=stem,
                seeds=seeds,
                repo_root=root,
                max_workers=args.workers,
                compile_timeout_s=args.timeout,
                motion_qc=True,
                artifact_root=Path(raw),
            )
        results = []
        for outcome in outcomes:
            result = outcome.to_dict()
            # Validation artifacts lived in the private temporary directory.
            result["artifact_dir"] = None
            if outcome.verdict == "pass":
                try:
                    paths = export_template_assets(
                        repo_root=root,
                        slug=args.slug,
                        stem=stem,
                        seeds=[outcome.seed],
                        out_root=output,
                        library_pointer=args.library_pointer,
                        material_seed=args.material_seed,
                    )
                    if len(paths) != 1:
                        raise RuntimeError("material export did not return exactly one asset")
                    result["artifact_dir"] = str(paths[0])
                    result["path"] = str(paths[0])
                except (ValueError, OSError, RuntimeError) as exc:
                    result.update(
                        verdict="fail",
                        failure_type="material_export_error",
                        failure_type_normalized="material_export_error",
                        failure_details=str(exc),
                    )
            results.append(result)
    else:
        if (output / args.slug).exists():
            raise FileExistsError(f"generator output already exists: {output / args.slug}")
        outcomes = run_seed_outcomes(
            slug=args.slug,
            stem=stem,
            seeds=seeds,
            repo_root=root,
            max_workers=args.workers,
            compile_timeout_s=args.timeout,
            motion_qc=True,
            artifact_root=output,
        )
        results = [outcome.to_dict() for outcome in outcomes]
    passed_count = sum(result["verdict"] == "pass" for result in results)
    failed_count = len(outcomes) - passed_count
    passed = failed_count == 0
    report = {
        "schema": "rfwa-sampling/v1",
        "generator": args.slug,
        "mechanical_hash": mechanical_hash(root, args.slug, stem),
        "construction_provenance": construction_provenance(args.slug, root),
        "status": "pass" if passed else "partial" if passed_count else "fail",
        "passed": passed_count,
        "skipped": failed_count,
        "model_inference": False,
        "material_grounding": args.library_pointer is not None,
        "release_status": "not_evaluated",
        "results": results,
    }
    write_json(manifest, report)
    _print(report)
    return 0 if passed_count else 1


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    raw_args = list(sys.argv[1:] if argv is None else argv)
    # Forward options verbatim, including leading --help/--spec flags.
    offset = 2 if raw_args[:1] == ["--repo-root"] else 0
    if raw_args and raw_args[0].startswith("--repo-root="):
        offset = 1
    if len(raw_args) > offset and raw_args[offset] in {"author", "source", "edit"}:
        args = parser.parse_args(raw_args[: offset + 1])
        args.args = raw_args[offset + 1 :]
    else:
        args = parser.parse_args(raw_args)
    root = args.repo_root.expanduser().resolve()
    try:
        if args.command == "generators":
            from agent.template_registry import TEMPLATE_REGISTRY

            _print(sorted(TEMPLATE_REGISTRY))
        elif args.command == "inspect":
            _print(describe(args.slug, root))
        elif args.command == "config":
            _print(configuration(args.slug, args.seed))
        elif args.command in {"check", "release"}:
            if args.workers < 1 or args.timeout <= 0:
                raise ValueError("workers and timeout must be positive")
            if not 0 < args.pass_threshold <= 1:
                raise ValueError("pass threshold must be in (0, 1]")
            options = dict(
                state_root=args.state_root or root / ".artifacts" / "rfwa",
                workers=args.workers,
                timeout=args.timeout,
                strict=args.strict,
                pass_threshold=args.pass_threshold,
            )
            report = (
                check_generator(root, args.slug, args.stage, **options)
                if args.command == "check"
                else release_generator(root, args.slug, **options)
            )
            _print(report)
            return (
                0
                if report.get("verdict") == "pass"
                or report.get("status") in {"released", "ready_for_sampling"}
                else 1
            )
        elif args.command == "sample":
            if args.workers < 1 or args.timeout <= 0:
                raise ValueError("workers and timeout must be positive")
            return _sample(args, root)
        elif args.command == "import-source":
            from rfwa.sources import import_record

            for record_id in args.record_ids:
                print(import_record(args.from_repo.expanduser().resolve(), root, record_id))
        elif args.command == "author":
            from cli.template import main as author

            return author(["--repo-root", str(root), *(args.args or ["--help"])])
        elif args.command == "source":
            from dotenv import load_dotenv

            load_dotenv(root / ".env", override=False)
            from cli.main import main as source

            forwarded = args.args or ["--help"]
            if forwarded[0].startswith("-"):
                return source(forwarded)
            return source([forwarded[0], "--repo-root", str(root), *forwarded[1:]])
        elif args.command == "edit":
            from specific_editing.pipeline import main as edit

            return edit(args.args or ["--help"])
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"rfwa: {exc}", file=sys.stderr)
        return 1
    return 0
