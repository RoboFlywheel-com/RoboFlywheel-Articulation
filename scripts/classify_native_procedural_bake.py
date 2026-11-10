#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Conservatively find native materials reusable as generic texture sets.

The command is read-only with respect to the normalized catalog and packages.
By default it verifies and prints a plan. ``--execute`` runs a pinned Blender
worker and writes a content-frozen report; ``--resume`` continues that report.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable, Mapping, Sequence

CLASSIFIER_VERSION = "articraft-native-bake-classifier/v1"
REPORT_SCHEMA = "articraft-native-bake-eligibility-report/v1"
RESULT_SCHEMA = "articraft-native-bake-eligibility/v1"
SAFE_DECISION = "reusable_texture_set"
WORKER_PREFIX = "ARTICRAFT_NATIVE_BAKE_SCAN\t"
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _safe_relative_path(value: object, *, field: str) -> Path:
    text = str(value or "").strip()
    posix = PurePosixPath(text)
    windows = PureWindowsPath(text)
    if (
        not text
        or "\\" in text
        or posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or any(part in {"", ".", ".."} for part in posix.parts)
    ):
        raise ValueError(f"{field} must be a safe POSIX relative path: {text!r}")
    return Path(*posix.parts)


def _contained_file(root: Path, value: object, *, field: str) -> Path:
    candidate = (root / _safe_relative_path(value, field=field)).resolve(strict=True)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{field} escapes the material library") from exc
    if not candidate.is_file():
        raise ValueError(f"{field} is not a file: {candidate}")
    return candidate


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"invalid JSON object at {path}:{line_number}")
        rows.append(value)
    return rows


def load_native_jobs(catalog_path: Path, library_root: Path) -> tuple[str, list[dict[str, Any]]]:
    root = library_root.resolve(strict=True)
    catalog = catalog_path.resolve(strict=True)
    try:
        catalog.relative_to(root)
    except ValueError as exc:
        raise ValueError("catalog must stay inside library_root") from exc
    catalog_sha256 = _sha256_file(catalog)
    jobs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(catalog.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"catalog row {line_number} is not an object")
        if row.get("material_profile") != "native_procedural":
            continue
        material_id = str(row.get("material_id") or "").strip()
        if not material_id or material_id in seen:
            raise ValueError(f"invalid or duplicate native material_id at row {line_number}")
        seen.add(material_id)
        expected_sha256 = str(row.get("sha256") or "")
        if _SHA256_RE.fullmatch(expected_sha256) is None:
            raise ValueError(f"{material_id} lacks a valid package SHA-256")
        package = _contained_file(
            root,
            row.get("normalized_blend_path"),
            field=f"{material_id}.normalized_blend_path",
        )
        observed_sha256 = _sha256_file(package)
        if observed_sha256 != expected_sha256:
            raise ValueError(f"normalized package SHA mismatch for {material_id}")
        node_qa = row.get("node_qa")
        node_qa = node_qa if isinstance(node_qa, Mapping) else {}
        displacement = row.get("displacement_policy")
        displacement = displacement if isinstance(displacement, Mapping) else {}
        source = row.get("source")
        source = source if isinstance(source, Mapping) else {}
        parameters = source.get("parameters")
        parameters = parameters if isinstance(parameters, Mapping) else {}
        job = {
            "material_id": material_id,
            "display_name": str(row.get("display_name") or ""),
            "category_slug": str(row.get("category_slug") or ""),
            "package_path": str(package),
            "package_relative_path": package.relative_to(root).as_posix(),
            "package_sha256": expected_sha256,
            "catalog_sha256": catalog_sha256,
            "node_qa_status": str(node_qa.get("status") or ""),
            "texture_size_m": row.get("texture_size_m"),
            "source_true_displacement_link_count": int(
                displacement.get("source_output_link_count") or 0
            ),
            "optical_policy_present": row.get("optical_policy") is not None,
            "source_animated": parameters.get("animated") is True,
        }
        job["input_sha256"] = _canonical_sha256(
            {
                "classifier_version": CLASSIFIER_VERSION,
                **{key: value for key, value in job.items() if key != "package_path"},
            }
        )
        jobs.append(job)
    jobs.sort(key=lambda row: str(row["material_id"]))
    return catalog_sha256, jobs


def _batches(rows: Sequence[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [list(rows[index : index + size]) for index in range(0, len(rows), size)]


def _run_worker_batch(
    rows: Sequence[dict[str, Any]],
    *,
    bpy_python: Path,
    worker: Path,
    timeout_seconds: float,
) -> list[dict[str, Any]]:
    payload = {"classifier_version": CLASSIFIER_VERSION, "materials": list(rows)}
    completed = subprocess.run(
        (str(bpy_python.absolute()), str(worker.resolve())),
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout_seconds,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "worker failed").strip()
        raise RuntimeError(detail[-4000:])
    results: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        if line.startswith(WORKER_PREFIX):
            value = json.loads(line[len(WORKER_PREFIX) :])
            if not isinstance(value, dict):
                raise RuntimeError("Blender worker emitted a non-object result")
            results.append(value)
    if len(results) != len(rows):
        raise RuntimeError(f"Blender worker returned {len(results)} of {len(rows)} results")
    return results


def _validate_result(result: Mapping[str, Any], job: Mapping[str, Any]) -> dict[str, Any]:
    expected = {
        "schema_version": RESULT_SCHEMA,
        "classifier_version": CLASSIFIER_VERSION,
        "material_id": job["material_id"],
        "catalog_sha256": job["catalog_sha256"],
        "package_sha256": job["package_sha256"],
        "input_sha256": job["input_sha256"],
    }
    for field, wanted in expected.items():
        if result.get(field) != wanted:
            raise RuntimeError(
                f"worker result mismatch for {job['material_id']}: {field}={result.get(field)!r}"
            )
    if result.get("decision") not in {
        SAFE_DECISION,
        "component_bake_only",
        "keep_native",
        "review",
    }:
        raise RuntimeError(f"worker returned an invalid decision for {job['material_id']}")
    return dict(result)


def _resume_rows(path: Path, jobs: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    resumed: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl(path):
        material_id = str(row.get("material_id") or "")
        job = jobs.get(material_id)
        if job is None:
            continue
        try:
            resumed[material_id] = _validate_result(row, job)
        except RuntimeError:
            continue
    return resumed


def classify(
    jobs: Sequence[dict[str, Any]],
    *,
    output_dir: Path,
    bpy_python: Path,
    worker: Path,
    workers: int,
    batch_size: int,
    timeout_seconds: float,
    resume: bool,
) -> list[dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = output_dir / "scan_results.jsonl"
    jobs_by_id = {str(row["material_id"]): row for row in jobs}
    existing = _resume_rows(checkpoint, jobs_by_id) if resume else {}
    if checkpoint.exists() and not resume:
        raise ValueError(f"report already exists; use --resume: {checkpoint}")
    pending = [row for row in jobs if row["material_id"] not in existing]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                _run_worker_batch,
                batch,
                bpy_python=bpy_python,
                worker=worker,
                timeout_seconds=timeout_seconds,
            ): batch
            for batch in _batches(pending, batch_size)
        }
        for future in concurrent.futures.as_completed(futures):
            batch = futures[future]
            batch_jobs = {str(row["material_id"]): row for row in batch}
            for raw_result in future.result():
                material_id = str(raw_result.get("material_id") or "")
                if material_id not in batch_jobs:
                    raise RuntimeError(f"worker returned unexpected material_id {material_id!r}")
                existing[material_id] = _validate_result(raw_result, batch_jobs[material_id])
            _atomic_jsonl(
                checkpoint,
                (existing[key] for key in sorted(existing)),
            )
    if len(existing) != len(jobs):
        raise RuntimeError(f"scan is incomplete: {len(existing)} of {len(jobs)}")
    return [existing[str(job["material_id"])] for job in jobs]


def default_bpy_python() -> Path:
    return Path(__file__).resolve().parents[1] / ".cache" / "bpy-5.2-venv" / "bin" / "python"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--library-root", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--bpy-python", type=Path, default=default_bpy_python())
    parser.add_argument(
        "--worker", type=Path, default=Path(__file__).with_name("_bpy_native_bake_scan_worker.py")
    )
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.workers < 1 or args.batch_size < 1 or args.timeout <= 0:
        raise SystemExit("workers, batch-size, and timeout must be positive")
    if args.resume and not args.execute:
        raise SystemExit("--resume requires --execute")
    root = args.library_root.resolve(strict=True)
    catalog_sha256, jobs = load_native_jobs(args.catalog, root)
    output_dir = args.output_dir or (root / "reports" / "bake_eligibility" / catalog_sha256)
    output_dir = output_dir.resolve(strict=False)
    try:
        output_dir.relative_to(root)
    except ValueError as exc:
        raise SystemExit("output-dir must stay inside library-root") from exc
    plan: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA,
        "classifier_version": CLASSIFIER_VERSION,
        "mode": "execute" if args.execute else "dry_run",
        "catalog_path": str(args.catalog.resolve(strict=True).relative_to(root)),
        "catalog_sha256": catalog_sha256,
        "native_material_count": len(jobs),
        "verified_package_count": len(jobs),
        "output_dir": str(output_dir.relative_to(root)),
        "writes_catalog_or_packages": False,
    }
    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, sort_keys=True))
        return 0
    if not args.bpy_python.is_file() or not args.worker.is_file():
        raise SystemExit("bpy Python or Blender worker is missing")
    results = classify(
        jobs,
        output_dir=output_dir,
        bpy_python=args.bpy_python,
        worker=args.worker,
        workers=args.workers,
        batch_size=args.batch_size,
        timeout_seconds=args.timeout,
        resume=args.resume,
    )
    safe = [row for row in results if row["decision"] == SAFE_DECISION]
    safe.sort(key=lambda row: str(row["material_id"]))
    _atomic_jsonl(output_dir / "safe_materials.jsonl", safe)
    safe_sha256 = _sha256_file(output_dir / "safe_materials.jsonl")
    summary = {
        **plan,
        "scanned_count": len(results),
        "safe_count": len(safe),
        "safe_material_ids": [row["material_id"] for row in safe],
        "safe_materials_path": "safe_materials.jsonl",
        "safe_materials_sha256": safe_sha256,
        "scan_complete": True,
    }
    _atomic_json(output_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
