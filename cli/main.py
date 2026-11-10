# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen
from collections.abc import Callable
from pathlib import Path
from shutil import which

from agent import runner as agent_runner
from agent.providers.factory import infer_provider_from_model_id
from articraft.values import PROVIDER_VALUES, THINKING_LEVEL_VALUES
from cli import compile_all as compile_all_cli
from cli import compile_record as compile_record_cli
from cli import dataset as dataset_cli
from cli import env as env_cli
from cli import external as external_cli
from cli import hooks as hooks_cli
from cli import pre_commit as pre_commit_cli
from cli import template as template_cli
from cli import workbench as workbench_cli
from cli.common import provider_for_record_image, refresh_dataset_manifest_if_member
from storage.repo import StorageRepo
from storage.search import SearchIndex

DEFAULT_MODEL = os.environ.get("RFWA_MODEL") or os.environ.get("ARTICRAFT_MODEL") or "gpt-5.5-2026-04-23"
DEFAULT_THINKING = os.environ.get("RFWA_THINKING_LEVEL") or os.environ.get("ARTICRAFT_THINKING_LEVEL") or "high"

DatasetDispatchKey = tuple[str, str | None]
DatasetArgBuilder = Callable[[argparse.Namespace], list[str]]
DatasetDispatchEntry = tuple[str, ...] | DatasetArgBuilder


def _infer_provider(model_id: str) -> str:
    provider = infer_provider_from_model_id(model_id)
    if provider is not None:
        return provider
    raise ValueError(
        f"Unable to infer provider for model '{model_id}'. "
        "Pass --provider explicitly or use a known OpenAI, Gemini, Anthropic, or OpenRouter model ID."
    )


def _model_and_provider(args: argparse.Namespace) -> tuple[str, str]:
    model_id = str(args.model or DEFAULT_MODEL)
    provider = str(args.provider or _infer_provider(model_id))
    return model_id, provider


def _dataset(args: argparse.Namespace, argv: list[str]) -> int:
    return dataset_cli.main(["--repo-root", str(args.repo_root), *argv])


def _workbench(args: argparse.Namespace, argv: list[str]) -> int:
    return workbench_cli.main(["--repo-root", str(args.repo_root), *argv])


def _external(args: argparse.Namespace) -> int:
    external_args = list(args.external_args)
    if not external_args:
        external_args = ["--help"]
    return external_cli.main(["--repo-root", str(args.repo_root), *external_args])


def _template(args: argparse.Namespace) -> int:
    template_args = list(args.template_args)
    if not template_args:
        template_args = ["--help"]
    return template_cli.main(["--repo-root", str(args.repo_root), *template_args])


def _run_init(args: argparse.Namespace) -> int:
    env_cli.main([str(args.repo_root)])
    dataset_status = _dataset(args, ["init-storage"])
    if dataset_status != 0:
        return dataset_status
    workbench_status = _workbench(args, ["init-storage"])
    if workbench_status != 0:
        return workbench_status
    check_status = _dataset(args, ["validate-format"])
    if check_status != 0:
        return check_status
    return _dataset(args, ["build-manifest"])


def _run_status(args: argparse.Namespace) -> int:
    dataset_status = _dataset(args, ["status"])
    if dataset_status != 0:
        return dataset_status
    return _workbench(args, ["status"])


def _run_generate(args: argparse.Namespace) -> int:
    try:
        model_id, provider = _model_and_provider(args)
    except ValueError as exc:
        print(str(exc))
        return 1
    argv = [
        "--repo-root",
        str(args.repo_root),
        "--prompt",
        args.prompt,
        "--provider",
        provider,
        "--model",
        model_id,
        "--thinking",
        args.thinking_level,
    ]
    if args.image:
        argv.extend(["--image", args.image])
    if args.max_cost_usd is not None:
        argv.extend(["--max-cost-usd", str(args.max_cost_usd)])
    return agent_runner.main(argv)


def _run_draft(args: argparse.Namespace) -> int:
    try:
        model_id, provider = _model_and_provider(args)
    except ValueError as exc:
        print(str(exc))
        return 1
    argv = [
        "init-record",
        args.prompt,
        "--provider",
        provider,
        "--model-id",
        model_id,
        "--thinking-level",
        args.thinking_level,
    ]
    if args.image:
        argv.extend(["--image", args.image])
    if args.max_cost_usd is not None:
        argv.extend(["--max-cost-usd", str(args.max_cost_usd)])
    if args.label:
        argv.extend(["--label", args.label])
    for tag in args.tags or []:
        argv.extend(["--tag", tag])
    if args.record_id:
        argv.extend(["--record-id", args.record_id])
    return _workbench(args, argv)


def _run_rerun(args: argparse.Namespace) -> int:
    argv = ["rerun-record", args.record]
    if args.model:
        argv.extend(["--model-id", args.model])
    if args.thinking_level:
        argv.extend(["--thinking-level", args.thinking_level])
    if args.max_cost_usd is not None:
        argv.extend(["--max-cost-usd", str(args.max_cost_usd)])
    return _workbench(args, argv)


def _run_edit(args: argparse.Namespace) -> int:
    repo = StorageRepo(args.repo_root)
    try:
        record_id = _resolve_record_id(args.repo_root, args.record)
        image_provider = provider_for_record_image(
            repo,
            record_id,
            provider_override=args.provider,
        )
        image_path = agent_runner._resolve_image_path(
            args.image,
            provider=image_provider,
        )
    except Exception as exc:
        print(str(exc))
        return 1

    outcome = asyncio.run(
        agent_runner.edit_record(
            repo_root=args.repo_root,
            parent_record_id=record_id,
            edit_prompt=args.prompt,
            image_path=image_path,
            provider=args.provider,
            model_id=args.model,
            thinking_level=args.thinking_level,
            max_turns=args.max_turns,
            max_cost_usd=args.max_cost_usd,
            record_id=getattr(args, "record_id", None),
            label=getattr(args, "label", None),
            tags=list(getattr(args, "tags", None) or []),
        )
    )
    if outcome.exit_code != 0:
        print(outcome.message or "Edit failed.")
        return outcome.exit_code

    record = repo.read_json(repo.layout.record_metadata_path(outcome.record_id), default={}) or {}
    revision_id = record.get("active_revision_id") if isinstance(record, dict) else None
    refresh_dataset_manifest_if_member(repo, outcome.record_id)
    stats = SearchIndex(repo).rebuild()
    print(
        f"edited mode=fork parent_record_id={record_id} "
        f"record_id={outcome.record_id} revision_id={revision_id or '(unknown)'} "
        f"run_id={outcome.run_id}"
    )
    print(
        f"search_index={stats.path} "
        f"records={stats.record_count} "
        f"categories={stats.category_count} "
        f"workbench_entries={stats.workbench_entry_count}"
    )
    return 0


def _run_compile(args: argparse.Namespace) -> int:
    argv = [
        "--repo-root",
        str(args.repo_root),
        "--target",
        args.target,
        args.record,
    ]
    if args.validate:
        argv.append("--validate")
    if args.strict_geom_qc:
        argv.append("--strict-geom-qc")
    return compile_record_cli.main(argv)


def _run_compile_all(args: argparse.Namespace) -> int:
    argv = [
        "--repo-root",
        str(args.repo_root),
        "--target",
        args.target,
        "--concurrency",
        args.concurrency,
    ]
    if args.force:
        argv.append("--force")
    if args.strict:
        argv.append("--strict")
    if args.limit is not None:
        argv.extend(["--limit", str(args.limit)])
    if args.dry_run:
        argv.append("--dry-run")
    if args.verify_assets:
        argv.append("--verify-assets")
    return compile_all_cli.main(argv)


def _resolve_record_id(repo_root: Path, record_ref: str) -> str:
    repo = StorageRepo(repo_root)
    candidate = Path(record_ref).expanduser()
    if candidate.exists():
        resolved = candidate.resolve()
        records_root = repo.layout.records_root.resolve()
        try:
            relative = resolved.relative_to(records_root)
        except ValueError as exc:
            raise ValueError(f"Record path must be inside {records_root}") from exc
        if len(relative.parts) != 1 or not resolved.is_dir():
            raise ValueError(f"Record path must point to a direct child of {records_root}")
        return relative.parts[0]
    record_id = record_ref.strip()
    if not record_id:
        raise ValueError("Record reference is required.")
    if repo.layout.record_metadata_path(record_id).exists():
        return record_id
    raise ValueError(f"Record not found: {record_ref}")


def _ensure_viewer_inputs(args: argparse.Namespace, data_root: Path) -> int:
    # validate-format is a soft preflight for the viewer: pre-existing malformed
    # records (e.g. a record.json referencing a missing traces dir) should NOT
    # stop the viewer from serving the rest of the dataset. Warn and continue,
    # or skip entirely with --skip-validate.
    if getattr(args, "skip_validate", False):
        print("viewer: skipping data validate-format (--skip-validate).")
    elif dataset_cli.main(["--repo-root", str(data_root), "validate-format"]) != 0:
        print(
            "viewer: data validate-format reported problems (e.g. pre-existing "
            "malformed records). This does NOT block the viewer; continuing to "
            "serve. Fix the records or pass --skip-validate to suppress this."
        )
    print("viewer: building dataset manifest...", flush=True)
    status = dataset_cli.main(["--repo-root", str(data_root), "build-manifest"])
    if status != 0:
        return status
    print("viewer: rebuilding search index...", flush=True)
    return workbench_cli.main(["--repo-root", str(data_root), "rebuild-search-index"])


def _normalize_viewer_target(target: str) -> str:
    normalized = str(target or "/").strip() or "/"
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    return normalized


def _viewer_url(args: argparse.Namespace, *, dev_frontend: bool = False) -> str:
    port = "5173" if dev_frontend else str(args.port)
    return f"http://{args.host}:{port}{_normalize_viewer_target(args.target)}"


def _viewer_health_url(args: argparse.Namespace) -> str:
    host = args.host
    if host in {"0.0.0.0", "::", "[::]"}:
        host = "127.0.0.1"
    return f"http://{host}:{args.port}/health"


def _viewer_is_healthy(
    args: argparse.Namespace,
    expected_data_root: Path | None = None,
    timeout: float = 1.0,
) -> bool:
    try:
        with urlopen(_viewer_health_url(args), timeout=timeout) as response:
            if response.status != 200:
                return False
            payload = json.loads(response.read().decode("utf-8"))
            if expected_data_root is None:
                return True
            return Path(str(payload.get("repo_root", ""))).resolve() == expected_data_root.resolve()
    except (OSError, URLError, ValueError):
        return False


def _wait_for_viewer(
    args: argparse.Namespace,
    process: subprocess.Popen,
    expected_data_root: Path,
    timeout: float = 20.0,
) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _viewer_is_healthy(args, expected_data_root, timeout=0.5):
            return True
        if process.poll() is not None:
            return False
        time.sleep(0.2)
    return False


def _run_viewer(args: argparse.Namespace) -> int:
    configured_data_root = getattr(args, "data_root", None)
    data_root = (
        Path(configured_data_root).expanduser().resolve()
        if configured_data_root
        else args.repo_root
    )
    fast = bool(getattr(args, "fast", False))
    if _viewer_is_healthy(args, data_root):
        print(f"Viewer already running: {_viewer_url(args)}")
        return 0

    dist_index = args.repo_root / "viewer" / "web" / "dist" / "index.html"
    if not fast and not which("npm"):
        print("npm is required for viewer/web. Install Node.js and npm first.")
        return 1
    node_modules = args.repo_root / "viewer" / "web" / "node_modules"
    if not fast and not node_modules.is_dir():
        print("viewer: installing frontend dependencies...", flush=True)
        status = subprocess.call(["npm", "--prefix", "viewer/web", "install"], cwd=args.repo_root)
        if status != 0:
            return status
    if fast:
        if not dist_index.exists():
            print("viewer: --fast requires an existing viewer/web/dist/index.html; run without --fast once.")
            return 1
        print("viewer: fast mode; reusing existing manifest, search index, and frontend build.")
    else:
        status = _ensure_viewer_inputs(args, data_root)
        if status != 0:
            return status

    env = dict(os.environ)
    env["ARTICRAFT_REPO_ROOT"] = str(data_root)
    if fast:
        env["ARTICRAFT_VIEWER_SKIP_SEARCH_INDEX"] = "1"

    if args.dev:
        api = subprocess.Popen(
            [
                "uv",
                "run",
                "python",
                "-m",
                "uvicorn",
                "viewer.api.app:app",
                "--reload",
                "--host",
                args.host,
                "--port",
                str(args.port),
            ],
            cwd=args.repo_root,
            env=env,
        )
        frontend_env = dict(env)
        frontend_env["ARTICRAFT_VIEWER_API_HOST"] = args.host
        frontend_env["ARTICRAFT_VIEWER_API_PORT"] = str(args.port)
        try:
            print(f"Viewer URL: {_viewer_url(args, dev_frontend=True)}")
            return subprocess.call(
                ["npm", "--prefix", "viewer/web", "run", "dev"],
                cwd=args.repo_root,
                env=frontend_env,
            )
        finally:
            api.terminate()
    if not fast:
        print("viewer: building frontend...", flush=True)
        status = subprocess.call(["npm", "--prefix", "viewer/web", "run", "build"], cwd=args.repo_root)
    else:
        status = 0
    if status != 0:
        return status
    api = subprocess.Popen(
        [
            "uv",
            "run",
            "python",
            "-m",
            "uvicorn",
            "viewer.api.app:app",
            "--host",
            args.host,
            "--port",
            str(args.port),
        ],
        cwd=args.repo_root,
        env=env,
    )
    if not _wait_for_viewer(args, api, data_root):
        api.terminate()
        print(
            f"viewer: API did not become healthy within 20s at {_viewer_health_url(args)}. "
            "Check the API output above and whether the port is already in use."
        )
        return 1
    print(f"Viewer URL: {_viewer_url(args)}", flush=True)
    try:
        return api.wait()
    except KeyboardInterrupt:
        api.terminate()
        return 130


def _run_view(args: argparse.Namespace) -> int:
    configured_data_root = getattr(args, "data_root", None)
    data_root = (
        Path(configured_data_root).expanduser().resolve()
        if configured_data_root
        else args.repo_root
    )
    try:
        record_id = _resolve_record_id(data_root, args.record)
    except ValueError as exc:
        print(str(exc))
        return 1
    args.target = f"/viewer?record={record_id}"
    return _run_viewer(args)


def _run_dataset_batch_new(args: argparse.Namespace) -> int:
    batch_name = args.name.strip()
    if not batch_name:
        print("Batch name is required.")
        return 1
    spec_path = args.repo_root / "data" / "batch_specs" / f"{batch_name}.csv"
    if spec_path.exists():
        print(f"Batch spec already exists: {spec_path}")
        return 1
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(
        "row_id,category_slug,category_title,prompt,provider,model_id,"
        "thinking_level,max_turns,max_cost_usd,label\n",
        encoding="utf-8",
    )
    print(f"Created {spec_path}")
    return 0


def _run_dataset_run(args: argparse.Namespace) -> int:
    try:
        model_id, provider = _model_and_provider(args)
    except ValueError as exc:
        print(str(exc))
        return 1
    argv = [
        "run-single",
        args.prompt,
        "--category-slug",
        args.category_slug,
        "--provider",
        provider,
        "--model-id",
        model_id,
        "--thinking-level",
        args.thinking_level,
    ]
    if args.image:
        argv.extend(["--image", args.image])
    if args.dataset_id:
        argv.extend(["--dataset-id", args.dataset_id])
    if args.record_id:
        argv.extend(["--record-id", args.record_id])
    if args.max_cost_usd is not None:
        argv.extend(["--max-cost-usd", str(args.max_cost_usd)])
    return _dataset(args, argv)


def _run_dataset_batch(args: argparse.Namespace) -> int:
    argv = [
        "run-batch",
        args.spec,
        "--row-concurrency",
        args.row_concurrency,
        "--subprocess-concurrency",
        args.subprocess_concurrency,
    ]
    if args.max_cost_usd is not None:
        argv.extend(["--max-cost-usd", str(args.max_cost_usd)])
    if args.resume:
        argv.append("--resume")
        argv.extend(["--resume-policy", args.resume_policy])
    if args.allow_resume_spec_mismatch:
        argv.append("--allow-resume-spec-mismatch")
    if args.qc_blurb:
        argv.extend(["--qc-blurb", args.qc_blurb])
    if args.keep_awake:
        argv.append("--keep-awake")
    return _dataset(args, argv)


def _dataset_promote_args(args: argparse.Namespace) -> list[str]:
    return [
        "promote-record",
        args.record,
        args.category_title,
        *(["--dataset-id", args.dataset_id] if args.dataset_id else []),
    ]


def _dataset_category_upsert_args(args: argparse.Namespace) -> list[str]:
    return [
        "upsert-category",
        "--category-slug",
        args.category_slug,
        *(["--title", args.title] if args.title else []),
        *(["--description", args.description] if args.description else []),
        *(["--target-sdk-version", args.target_sdk_version] if args.target_sdk_version else []),
    ]


def _dataset_category_delete_args(args: argparse.Namespace) -> list[str]:
    return [
        "delete-category",
        "--category-slug",
        args.category_slug,
        *(["--execute"] if args.execute else []),
        *(["--confirm-slug", args.confirm_slug] if args.confirm_slug else []),
    ]


def _dataset_record_delete_args(args: argparse.Namespace) -> list[str]:
    argv = ["delete-record"]
    candidate = Path(args.record).expanduser()
    if candidate.exists() or "/" in args.record:
        argv.extend(["--record-path", args.record])
    else:
        argv.extend(["--record-id", args.record])
    if args.execute:
        argv.append("--execute")
    if args.confirm_record_id:
        argv.extend(["--confirm-record-id", args.confirm_record_id])
    return argv


def _dataset_supercategory_upsert_args(args: argparse.Namespace) -> list[str]:
    return [
        "upsert-supercategory",
        "--supercategory-slug",
        args.supercategory_slug,
        *(["--title", args.title] if args.title else []),
        *(["--description", args.description] if args.description else []),
    ]


def _dataset_supercategory_set_args(args: argparse.Namespace) -> list[str]:
    return [
        "set-supercategory",
        "--category-slug",
        args.category_slug,
        "--supercategory-slug",
        args.supercategory_slug,
    ]


def _dataset_supercategory_clear_args(args: argparse.Namespace) -> list[str]:
    return ["clear-supercategory", "--category-slug", args.category_slug]


def _dataset_supercategory_delete_args(args: argparse.Namespace) -> list[str]:
    return [
        "delete-supercategory",
        "--supercategory-slug",
        args.supercategory_slug,
        *(["--execute"] if args.execute else []),
        *(["--confirm-slug", args.confirm_slug] if args.confirm_slug else []),
    ]


_DATASET_DISPATCH: dict[DatasetDispatchKey, DatasetDispatchEntry] = {
    ("status", None): ("status",),
    ("validate", None): ("validate",),
    ("manifest", None): ("build-manifest",),
    ("promote", None): _dataset_promote_args,
    ("category", "upsert"): _dataset_category_upsert_args,
    ("category", "delete"): _dataset_category_delete_args,
    ("record", "delete"): _dataset_record_delete_args,
    ("supercategory", "list"): ("list-supercategories",),
    ("supercategory", "upsert"): _dataset_supercategory_upsert_args,
    ("supercategory", "set"): _dataset_supercategory_set_args,
    ("supercategory", "clear"): _dataset_supercategory_clear_args,
    ("supercategory", "delete"): _dataset_supercategory_delete_args,
}


def _dataset_dispatch_key(args: argparse.Namespace) -> DatasetDispatchKey:
    command = args.dataset_command
    match command:
        case "category":
            return (command, args.category_command)
        case "record":
            return (command, args.record_command)
        case "supercategory":
            return (command, args.supercategory_command)
        case _:
            return (command, None)


def _run_dataset_dispatch(args: argparse.Namespace) -> int:
    key = _dataset_dispatch_key(args)
    entry = _DATASET_DISPATCH.get(key)
    if entry is None:
        print(f"Unsupported dataset command: {key[0]} {key[1] or ''}".rstrip())
        return 1
    argv = list(entry) if isinstance(entry, tuple) else entry(args)
    return _dataset(args, argv)


def _run_data_check(args: argparse.Namespace) -> int:
    return _dataset(args, ["validate-format"])


def _run_env_bootstrap(args: argparse.Namespace) -> int:
    return env_cli.main([str(args.repo_root)])


def _run_hooks(args: argparse.Namespace) -> int:
    return hooks_cli.main([args.hooks_command])


def _run_internal_pre_commit(args: argparse.Namespace) -> int:
    return pre_commit_cli.main([args.pre_commit_cli_command, *args.paths])


def _add_repo_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root containing the data/ directory.",
    )


def _add_generation_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--provider", choices=PROVIDER_VALUES)
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model ID to use.")
    parser.add_argument(
        "--thinking-level",
        "--thinking",
        default=DEFAULT_THINKING,
        choices=THINKING_LEVEL_VALUES,
        help="Thinking budget level.",
    )
    parser.add_argument("--image", default=None, help="Optional reference image.")
    parser.add_argument("--max-cost-usd", type=float, default=None)


def _add_internal_edit_options(
    parser: argparse.ArgumentParser,
    *,
    allow_record_id: bool,
    allow_label: bool,
) -> None:
    parser.add_argument("--provider", choices=PROVIDER_VALUES, default=None)
    parser.add_argument("--model", default=None, help="Optional model override.")
    parser.add_argument("--thinking-level", "--thinking", default=None)
    parser.add_argument("--max-turns", type=int, default=None)
    parser.add_argument("--image", default=None, help="Optional new edit reference image.")
    parser.add_argument("--max-cost-usd", type=float, default=None)
    if allow_record_id:
        parser.add_argument("--record-id", default=None, help="Optional child record ID.")
    if allow_label:
        parser.add_argument("--label", default=None)
        parser.add_argument("--tag", dest="tags", action="append", default=None)


def _add_internal_pre_commit_commands(subparsers: argparse._SubParsersAction) -> None:
    pre_commit = subparsers.add_parser("pre-commit")
    pre_commit_sub = pre_commit.add_subparsers(dest="pre_commit_command", required=True)
    for command in ("forbidden-paths", "secrets", "smoke-tests", "data-format", "data-check"):
        pre_commit_cmd = pre_commit_sub.add_parser(command)
        pre_commit_cmd.add_argument("paths", nargs="*")
        mapped_command = "data-format" if command == "data-check" else command
        pre_commit_cmd.set_defaults(
            func=_run_internal_pre_commit,
            pre_commit_cli_command=mapped_command,
        )


def _build_internal_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="articraft internal")
    subparsers = parser.add_subparsers(dest="internal_command", required=True)
    _add_internal_pre_commit_commands(subparsers)
    return parser


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="articraft")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Initialize local Articraft storage and env.")
    _add_repo_root(init)
    init.set_defaults(func=_run_init)

    status = subparsers.add_parser("status", help="Show dataset and workbench status.")
    _add_repo_root(status)
    status.set_defaults(func=_run_status)

    generate = subparsers.add_parser("generate", help="Generate a workbench record from a prompt.")
    _add_repo_root(generate)
    generate.add_argument("prompt")
    _add_generation_options(generate)
    generate.set_defaults(func=_run_generate)

    draft = subparsers.add_parser("draft", help="Create a draft workbench record.")
    _add_repo_root(draft)
    draft.add_argument("prompt")
    _add_generation_options(draft)
    draft.add_argument("--label", default=None)
    draft.add_argument("--tag", dest="tags", action="append", default=None)
    draft.add_argument("--record-id", default=None)
    draft.set_defaults(func=_run_draft)

    rerun = subparsers.add_parser("rerun", help="Re-run an existing record.")
    _add_repo_root(rerun)
    rerun.add_argument("record")
    rerun.add_argument("--model", default=None, help="Optional model override.")
    rerun.add_argument("--thinking-level", "--thinking", default=None)
    rerun.add_argument("--max-cost-usd", type=float, default=None)
    rerun.set_defaults(func=_run_rerun)

    fork = subparsers.add_parser("fork", help="Edit an existing record as a copy.")
    _add_repo_root(fork)
    fork.add_argument("record")
    fork.add_argument("prompt")
    _add_internal_edit_options(fork, allow_record_id=True, allow_label=True)
    fork.set_defaults(func=_run_edit)

    compile_one = subparsers.add_parser("compile", help="Compile one record.")
    _add_repo_root(compile_one)
    compile_one.add_argument("record")
    compile_one.add_argument("--target", choices=("full", "visual"), default="full")
    compile_one.add_argument("--validate", action="store_true")
    compile_one.add_argument("--strict-geom-qc", action="store_true")
    compile_one.set_defaults(func=_run_compile)

    compile_all = subparsers.add_parser("compile-all", help="Compile queued records.")
    _add_repo_root(compile_all)
    compile_all.add_argument("--target", choices=("full", "visual"), default="visual")
    compile_all.add_argument("--force", action="store_true")
    compile_all.add_argument("--strict", action="store_true")
    compile_all.add_argument("--limit", type=int, default=None)
    compile_all.add_argument("--concurrency", default="auto")
    compile_all.add_argument("--dry-run", action="store_true")
    compile_all.add_argument("--verify-assets", action="store_true")
    compile_all.set_defaults(func=_run_compile_all)

    viewer = subparsers.add_parser("viewer", help="Start the local viewer.")
    _add_repo_root(viewer)
    viewer.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="Data repository to show; defaults to --repo-root.",
    )
    viewer.add_argument("--dev", action="store_true")
    viewer.add_argument("--host", default="127.0.0.1")
    viewer.add_argument("--port", default="8765")
    viewer.add_argument("--target", default="/")
    viewer.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip the data validate-format preflight so the viewer serves even "
        "if some pre-existing records are malformed.",
    )
    viewer.add_argument(
        "--fast",
        action="store_true",
        help="Reuse the existing manifest, search index, and frontend build for quick startup.",
    )
    viewer.set_defaults(func=_run_viewer)

    view = subparsers.add_parser("view", help="Open the viewer focused on one record.")
    _add_repo_root(view)
    view.add_argument("record")
    view.add_argument("--data-root", type=Path, default=None)
    view.add_argument("--dev", action="store_true")
    view.add_argument("--host", default="127.0.0.1")
    view.add_argument("--port", default="8765")
    view.add_argument("--fast", action="store_true")
    view.set_defaults(func=_run_view)

    data = subparsers.add_parser("data", help="Data validation commands.")
    data_sub = data.add_subparsers(dest="data_command", required=True)
    data_check = data_sub.add_parser("check", help="Validate checked-in data format.")
    _add_repo_root(data_check)
    data_check.set_defaults(func=_run_data_check)

    external = subparsers.add_parser(
        "external",
        help="External agent data authoring commands.",
        add_help=False,
    )
    _add_repo_root(external)
    external.add_argument("external_args", nargs=argparse.REMAINDER)
    external.set_defaults(func=_external)

    template = subparsers.add_parser("template", help="Procedural template batch commands.")
    _add_repo_root(template)
    template.add_argument("template_args", nargs=argparse.REMAINDER)
    template.set_defaults(func=_template)

    dataset = subparsers.add_parser("dataset", help="Dataset commands.")
    dataset_sub = dataset.add_subparsers(dest="dataset_command", required=True)
    for name, help_text in (
        ("status", "Show dataset status."),
        ("validate", "Validate dataset entries."),
        ("manifest", "Build the dataset manifest."),
    ):
        child = dataset_sub.add_parser(name, help=help_text)
        _add_repo_root(child)
        child.set_defaults(func=_run_dataset_dispatch)

    dataset_run = dataset_sub.add_parser("run", help="Generate one dataset record.")
    _add_repo_root(dataset_run)
    dataset_run.add_argument("prompt")
    dataset_run.add_argument("--category-slug", required=True)
    dataset_run.add_argument("--dataset-id", default=None)
    dataset_run.add_argument("--record-id", default=None)
    _add_generation_options(dataset_run)
    dataset_run.set_defaults(func=_run_dataset_run)

    dataset_batch = dataset_sub.add_parser("batch", help="Run a tracked batch CSV.")
    _add_repo_root(dataset_batch)
    dataset_batch.add_argument("spec")
    dataset_batch.add_argument("--row-concurrency", default="auto")
    dataset_batch.add_argument("--subprocess-concurrency", default="auto")
    dataset_batch.add_argument("--max-cost-usd", type=float, default=None)
    dataset_batch.add_argument("--resume", action="store_true")
    dataset_batch.add_argument(
        "--resume-policy",
        default="failed_or_pending",
        choices=("failed_or_pending", "failed_only", "all"),
    )
    dataset_batch.add_argument("--allow-resume-spec-mismatch", action="store_true")
    dataset_batch.add_argument("--qc-blurb", default=None)
    dataset_batch.add_argument("--keep-awake", action="store_true")
    dataset_batch.set_defaults(func=_run_dataset_batch)

    dataset_batch_new = dataset_sub.add_parser("batch-new", help="Create a new batch CSV.")
    _add_repo_root(dataset_batch_new)
    dataset_batch_new.add_argument("name")
    dataset_batch_new.set_defaults(func=_run_dataset_batch_new)

    dataset_promote = dataset_sub.add_parser("promote", help="Promote a record into a category.")
    _add_repo_root(dataset_promote)
    dataset_promote.add_argument("record")
    dataset_promote.add_argument("category_title")
    dataset_promote.add_argument("--dataset-id", default=None)
    dataset_promote.set_defaults(func=_run_dataset_dispatch)

    category = dataset_sub.add_parser("category", help="Dataset category admin.")
    category_sub = category.add_subparsers(dest="category_command", required=True)
    category_upsert = category_sub.add_parser("upsert")
    _add_repo_root(category_upsert)
    category_upsert.add_argument("category_slug")
    category_upsert.add_argument("--title", default=None)
    category_upsert.add_argument("--description", default=None)
    category_upsert.add_argument("--target-sdk-version", default=None)
    category_upsert.set_defaults(func=_run_dataset_dispatch)
    category_delete = category_sub.add_parser("delete")
    _add_repo_root(category_delete)
    category_delete.add_argument("category_slug")
    category_delete.add_argument("--execute", action="store_true")
    category_delete.add_argument("--confirm-slug", default=None)
    category_delete.set_defaults(func=_run_dataset_dispatch)

    record = dataset_sub.add_parser("record", help="Dataset record admin.")
    record_sub = record.add_subparsers(dest="record_command", required=True)
    record_delete = record_sub.add_parser("delete")
    _add_repo_root(record_delete)
    record_delete.add_argument("record")
    record_delete.add_argument("--execute", action="store_true")
    record_delete.add_argument("--confirm-record-id", default=None)
    record_delete.set_defaults(func=_run_dataset_dispatch)

    supercategory = dataset_sub.add_parser("supercategory", help="Dataset supercategory admin.")
    super_sub = supercategory.add_subparsers(dest="supercategory_command", required=True)
    super_list = super_sub.add_parser("list")
    _add_repo_root(super_list)
    super_list.set_defaults(func=_run_dataset_dispatch)
    super_upsert = super_sub.add_parser("upsert")
    _add_repo_root(super_upsert)
    super_upsert.add_argument("supercategory_slug")
    super_upsert.add_argument("--title", default=None)
    super_upsert.add_argument("--description", default=None)
    super_upsert.set_defaults(func=_run_dataset_dispatch)
    super_set = super_sub.add_parser("set")
    _add_repo_root(super_set)
    super_set.add_argument("category_slug")
    super_set.add_argument("supercategory_slug")
    super_set.set_defaults(func=_run_dataset_dispatch)
    super_clear = super_sub.add_parser("clear")
    _add_repo_root(super_clear)
    super_clear.add_argument("category_slug")
    super_clear.set_defaults(func=_run_dataset_dispatch)
    super_delete = super_sub.add_parser("delete")
    _add_repo_root(super_delete)
    super_delete.add_argument("supercategory_slug")
    super_delete.add_argument("--execute", action="store_true")
    super_delete.add_argument("--confirm-slug", default=None)
    super_delete.set_defaults(func=_run_dataset_dispatch)

    workbench = subparsers.add_parser("workbench", help="Workbench commands.")
    workbench_sub = workbench.add_subparsers(dest="workbench_command", required=True)
    wb_status = workbench_sub.add_parser("status")
    _add_repo_root(wb_status)
    wb_status.set_defaults(func=lambda args: _workbench(args, ["status"]))
    wb_search = workbench_sub.add_parser("search-index")
    _add_repo_root(wb_search)
    wb_search.set_defaults(func=lambda args: _workbench(args, ["rebuild-search-index"]))

    env = subparsers.add_parser("env", help="Environment helpers.")
    env_sub = env.add_subparsers(dest="env_command", required=True)
    bootstrap = env_sub.add_parser("bootstrap")
    _add_repo_root(bootstrap)
    bootstrap.set_defaults(func=_run_env_bootstrap)

    hooks = subparsers.add_parser("hooks", help="Git hook helpers.")
    hooks_sub = hooks.add_subparsers(dest="hooks_command", required=True)
    for command in ("install", "check", "post-commit-record-authors"):
        hook_cmd = hooks_sub.add_parser(command)
        hook_cmd.set_defaults(func=_run_hooks, hooks_command=command)

    return parser


def main(argv: list[str] | None = None) -> int:
    args_list = sys.argv[1:] if argv is None else argv
    if args_list and args_list[0] == "internal":
        parser = _build_internal_parser()
        args = parser.parse_args(args_list[1:])
        return args.func(args)
    if args_list and args_list[0] == "external":
        return external_cli.main(args_list[1:] or ["--help"])
    parser = _build_parser()
    args = parser.parse_args(args_list)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
