#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Publish safely convertible native materials as a standalone texture-set catalog.

The source normalized catalog and its packages are immutable inputs.  Conversion
workers write isolated staging packages under the derived output root; only
successful, hash-verified results are promoted into the derived library.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from articraft.appearance.catalog import (
    MaterialCatalog,
    _load_snapshot_manifest,
    _validate_strict_normalized_row,
)
from articraft.appearance.normalized import (
    NORMALIZED_CATALOG_MANIFEST_SCHEMA,
    NORMALIZED_CATALOG_SCHEMA,
    NORMALIZED_PACKAGE_SCHEMA,
    NORMALIZER_VERSION,
    RUNTIME_PROFILE_POLICY_VERSION,
    atomic_json,
    atomic_jsonl,
    canonical_json_sha256,
    generic_eligibility,
    logical_catalog_snapshot_sha256,
    native_runtime_allowlist_sha256,
    safe_relative_path,
)

JOB_SCHEMA = "articraft-native-texture-conversion-job/v1"
RESULT_SCHEMA = "articraft-native-texture-conversion-result/v1"
WORKER_METADATA_SCHEMA = NORMALIZED_PACKAGE_SCHEMA
CONVERSION_VERSION = "articraft-native-texture-converter/v1"
DERIVATION_SCHEMA = "articraft-native-texture-set-derivation/v1"
REPORT_SCHEMA = "articraft-native-texture-set-publication/v1"
RESULT_PREFIX = "ARTICRAFT_NATIVE_TEXTURE_CONVERT\t"
SAFE_SCHEMA = "articraft-native-bake-eligibility/v1"
SAFE_DECISION = "reusable_texture_set"
CLASSIFIER_VERSION = "articraft-native-bake-classifier/v1"
CHANNELS = ("base_color", "metallic", "roughness", "normal")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"JSONL row is not an object at {path}:{line_number}")
        rows.append(value)
    return rows


def _require_sha256(value: object, *, field: str) -> str:
    text = str(value or "").strip()
    if _SHA256_RE.fullmatch(text) is None:
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return text


def _contained(root: Path, path: Path, *, field: str, strict: bool) -> Path:
    canonical_root = root.resolve(strict=True)
    candidate = path.resolve(strict=strict)
    try:
        candidate.relative_to(canonical_root)
    except ValueError as exc:
        raise ValueError(f"{field} must stay inside workspace_root") from exc
    return candidate


def _relative_to(root: Path, path: Path, *, field: str) -> str:
    try:
        return path.resolve(strict=False).relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(f"{field} must stay inside workspace_root") from exc


def _source_manifest(catalog: Path, source_root: Path) -> dict[str, Any]:
    value = _load_snapshot_manifest(catalog, root=source_root, strict_normalized=True)
    if value is None:
        raise ValueError("source catalog must have a normalized immutable manifest")
    return value


def _worker_job(
    source: Mapping[str, Any],
    safe: Mapping[str, Any],
    *,
    source_catalog_sha256: str,
    workspace_root: Path,
    output_root: Path,
) -> dict[str, Any]:
    material_id = str(source["material_id"])
    category = str(source["category_slug"])
    source_relative = safe_relative_path(
        source.get("normalized_blend_path"),
        field=f"{material_id}.normalized_blend_path",
    )
    source_package = (Path(str(source["_source_root"])) / source_relative).resolve(strict=True)
    if _sha256_file(source_package) != source.get("sha256"):
        raise ValueError(f"source package SHA mismatch for {material_id}")
    source_workspace_relative = _relative_to(
        workspace_root, source_package, field=f"{material_id}.source_blend_path"
    )
    safe_input_sha = _require_sha256(
        safe.get("input_sha256"), field=f"{material_id}.eligibility_input_sha256"
    )
    work_identity = canonical_json_sha256(
        {
            "conversion_version": CONVERSION_VERSION,
            "eligibility_input_sha256": safe_input_sha,
            "material_id": material_id,
            "source_blend_sha256": source["sha256"],
        }
    )
    work_dir = output_root / ".conversion" / "work" / work_identity[:16]
    output_relative = _relative_to(workspace_root, work_dir, field=f"{material_id}.output_dir")
    tile_size = source.get("texture_size_m")
    if (
        isinstance(tile_size, bool)
        or not isinstance(tile_size, (int, float))
        or not math.isfinite(float(tile_size))
        or float(tile_size) <= 0.0
    ):
        raise ValueError(f"safe material {material_id} has no positive texture_size_m")
    job = {
        "material_id": material_id,
        "display_name": str(source.get("display_name") or material_id),
        "category_slug": category,
        "source_blend_path": source_workspace_relative,
        "source_blend_sha256": str(source["sha256"]),
        "output_dir": output_relative,
        "texture_size_m": float(tile_size),
        "catalog_sha256": source_catalog_sha256,
        "eligibility_input_sha256": safe_input_sha,
        "eligibility_decision": SAFE_DECISION,
    }
    job["conversion_input_sha256"] = canonical_json_sha256(
        {"conversion_version": CONVERSION_VERSION, **job}
    )
    job["_source_row"] = dict(source)
    job["_safe_row"] = dict(safe)
    return job


def load_conversion_jobs(
    *,
    source_catalog: Path,
    source_root: Path,
    safe_jsonl: Path,
    workspace_root: Path,
    output_root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    workspace = workspace_root.resolve(strict=True)
    source_library = _contained(workspace, source_root, field="source_root", strict=True)
    output = _contained(workspace, output_root, field="output_root", strict=False)
    if (
        output == source_library
        or output in source_library.parents
        or source_library in output.parents
    ):
        raise ValueError("output_root must be independent from source_root")
    catalog = _contained(workspace, source_catalog, field="source_catalog", strict=True)
    safe_path = _contained(workspace, safe_jsonl, field="safe_jsonl", strict=True)
    try:
        catalog.relative_to(source_library)
    except ValueError as exc:
        raise ValueError("source_catalog must stay inside source_root") from exc

    # The immutable manifest authenticates the whole catalog.  Validate the
    # selected strict rows and package hashes below; hashing every unrelated
    # package would make a two-material conversion scan the entire library.
    manifest = _source_manifest(catalog, source_library)
    catalog_sha = _sha256_file(catalog)
    safe_sha = _sha256_file(safe_path)
    source_rows: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl(catalog):
        material_id = str(row.get("material_id") or "").strip()
        if not material_id or material_id in source_rows:
            raise ValueError(f"source catalog has invalid/duplicate material_id {material_id!r}")
        row["_source_root"] = str(source_library)
        source_rows[material_id] = row

    jobs: list[dict[str, Any]] = []
    seen_safe: set[str] = set()
    for safe in _read_jsonl(safe_path):
        material_id = str(safe.get("material_id") or "").strip()
        if not material_id or material_id in seen_safe:
            raise ValueError(f"safe JSONL has invalid/duplicate material_id {material_id!r}")
        seen_safe.add(material_id)
        source = source_rows.get(material_id)
        if source is None:
            raise ValueError(f"safe material is absent from source catalog: {material_id}")
        expected = {
            "schema_version": SAFE_SCHEMA,
            "classifier_version": CLASSIFIER_VERSION,
            "decision": SAFE_DECISION,
            "catalog_sha256": catalog_sha,
            "package_relative_path": source.get("normalized_blend_path"),
            "package_sha256": source.get("sha256"),
            "category_slug": source.get("category_slug"),
            "display_name": source.get("display_name"),
        }
        for field, wanted in expected.items():
            if safe.get(field) != wanted:
                raise ValueError(
                    f"safe/source mismatch for {material_id}: {field}={safe.get(field)!r}, "
                    f"expected {wanted!r}"
                )
        if source.get("material_profile") != "native_procedural":
            raise ValueError(f"safe material is not native_procedural: {material_id}")
        _validate_strict_normalized_row(
            source,
            line_number=1,
            root=source_library,
        )
        jobs.append(
            _worker_job(
                source,
                safe,
                source_catalog_sha256=catalog_sha,
                workspace_root=workspace,
                output_root=output,
            )
        )
    jobs.sort(key=lambda row: str(row["material_id"]))
    provenance = {
        "source_catalog_path": catalog.relative_to(source_library).as_posix(),
        "source_catalog_sha256": catalog_sha,
        "source_logical_snapshot_sha256": manifest["logical_snapshot_sha256"],
        "source_raw_catalog": dict(manifest["raw_catalog"]),
        "safe_jsonl_sha256": safe_sha,
        "safe_material_count": len(jobs),
    }
    return provenance, jobs


def _public_job(job: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in job.items()
        if not key.startswith("_") and key != "conversion_input_sha256"
    }


def _run_worker_batch(
    rows: Sequence[dict[str, Any]],
    *,
    bpy_python: Path,
    worker: Path,
    workspace_root: Path,
    timeout_seconds: float,
) -> list[dict[str, Any]]:
    payload = {
        "schema_version": JOB_SCHEMA,
        "conversion_version": CONVERSION_VERSION,
        "workspace_root": str(workspace_root),
        "materials": [_public_job(row) for row in rows],
    }
    completed = subprocess.run(
        (str(bpy_python.resolve()), str(worker.resolve())),
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout_seconds,
        cwd=workspace_root,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "conversion worker failed").strip()
        raise RuntimeError(detail[-4000:])
    results: list[dict[str, Any]] = []
    for line in completed.stdout.splitlines():
        if not line.startswith(RESULT_PREFIX):
            continue
        value = json.loads(line[len(RESULT_PREFIX) :])
        if not isinstance(value, dict):
            raise RuntimeError("conversion worker emitted a non-object result")
        results.append(value)
    expected_ids = [str(row["material_id"]) for row in rows]
    observed_ids = [str(row.get("material_id") or "") for row in results]
    if sorted(observed_ids) != sorted(expected_ids) or len(observed_ids) != len(set(observed_ids)):
        raise RuntimeError("conversion worker result set does not match its input batch")
    return results


def _batch_failure(job: Mapping[str, Any], exc: Exception) -> dict[str, Any]:
    return {
        "schema_version": RESULT_SCHEMA,
        "conversion_version": CONVERSION_VERSION,
        "status": "failure",
        "failure_codes": ["worker_batch_failure", type(exc).__name__],
        "material_id": job["material_id"],
        "source_blend_path": job["source_blend_path"],
        "source_blend_sha256": job["source_blend_sha256"],
        "catalog_sha256": job["catalog_sha256"],
        "eligibility_input_sha256": job["eligibility_input_sha256"],
        "conversion_input_sha256": None,
        "output": None,
        "reopen_qa": None,
    }


def _run_isolated_batch(
    rows: Sequence[dict[str, Any]],
    *,
    bpy_python: Path,
    worker: Path,
    workspace_root: Path,
    timeout_seconds: float,
) -> list[dict[str, Any]]:
    try:
        return _run_worker_batch(
            rows,
            bpy_python=bpy_python,
            worker=worker,
            workspace_root=workspace_root,
            timeout_seconds=timeout_seconds,
        )
    except Exception as exc:
        if len(rows) == 1:
            return [_batch_failure(rows[0], exc)]
        middle = len(rows) // 2
        return [
            *_run_isolated_batch(
                rows[:middle],
                bpy_python=bpy_python,
                worker=worker,
                workspace_root=workspace_root,
                timeout_seconds=timeout_seconds,
            ),
            *_run_isolated_batch(
                rows[middle:],
                bpy_python=bpy_python,
                worker=worker,
                workspace_root=workspace_root,
                timeout_seconds=timeout_seconds,
            ),
        ]


def _validate_result(
    result: Mapping[str, Any],
    job: Mapping[str, Any],
    *,
    workspace_root: Path,
    allow_published: bool = True,
) -> dict[str, Any]:
    material_id = str(job["material_id"])
    expected = {
        "schema_version": RESULT_SCHEMA,
        "conversion_version": CONVERSION_VERSION,
        "material_id": material_id,
        "source_blend_path": job["source_blend_path"],
        "source_blend_sha256": job["source_blend_sha256"],
        "catalog_sha256": job["catalog_sha256"],
        "eligibility_input_sha256": job["eligibility_input_sha256"],
    }
    for field, wanted in expected.items():
        if result.get(field) != wanted:
            raise ValueError(
                f"stale conversion result for {material_id}: {field}={result.get(field)!r}"
            )
    if result.get("status") not in {"success", "failure"}:
        raise ValueError(f"invalid conversion status for {material_id}")
    if result.get("status") == "success" and result.get("conversion_input_sha256") != job.get(
        "conversion_input_sha256"
    ):
        raise ValueError(f"conversion input SHA mismatch for {material_id}")
    validated = dict(result)
    published = result.get("publisher")
    if allow_published and isinstance(published, Mapping):
        blend = workspace_root / safe_relative_path(
            published.get("blend_path"), field=f"{material_id}.publisher.blend_path"
        )
        metadata = workspace_root / safe_relative_path(
            published.get("metadata_path"), field=f"{material_id}.publisher.metadata_path"
        )
        if _sha256_file(blend.resolve(strict=True)) != published.get("blend_sha256"):
            raise ValueError(f"published blend hash mismatch for {material_id}")
        if _sha256_file(metadata.resolve(strict=True)) != published.get("metadata_sha256"):
            raise ValueError(f"published metadata hash mismatch for {material_id}")
        catalog_row = published.get("catalog_row")
        if (
            not isinstance(catalog_row, Mapping)
            or catalog_row.get("material_id") != material_id
            or catalog_row.get("material_profile") != "texture_set"
            or catalog_row.get("sha256") != published.get("blend_sha256")
        ):
            raise ValueError(f"published catalog row mismatch for {material_id}")
        return validated
    if result.get("status") == "failure":
        return validated
    output = result.get("output")
    if not isinstance(output, Mapping):
        raise ValueError(f"successful conversion lacks output for {material_id}")
    expected_dir = workspace_root / str(job["output_dir"])
    blend = workspace_root / safe_relative_path(
        output.get("blend_path"), field=f"{material_id}.output.blend_path"
    )
    metadata = workspace_root / safe_relative_path(
        output.get("metadata_path"), field=f"{material_id}.output.metadata_path"
    )
    if (
        blend.parent.resolve(strict=True) != expected_dir.resolve(strict=True)
        or metadata.parent != blend.parent
    ):
        raise ValueError(f"worker output path mismatch for {material_id}")
    if _sha256_file(blend) != output.get("blend_sha256"):
        raise ValueError(f"worker blend hash mismatch for {material_id}")
    if _sha256_file(metadata) != output.get("metadata_sha256"):
        raise ValueError(f"worker metadata hash mismatch for {material_id}")
    worker_metadata = json.loads(metadata.read_text(encoding="utf-8"))
    if not isinstance(worker_metadata, dict) or worker_metadata.get("schema_version") != (
        WORKER_METADATA_SCHEMA
    ):
        raise ValueError(f"worker metadata schema mismatch for {material_id}")
    return validated


def _read_checkpoint(
    path: Path,
    jobs: Mapping[str, Mapping[str, Any]],
    *,
    workspace_root: Path,
) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return rows
    for candidate in _read_jsonl(path):
        material_id = str(candidate.get("material_id") or "")
        job = jobs.get(material_id)
        if job is None:
            continue
        try:
            rows[material_id] = _validate_result(candidate, job, workspace_root=workspace_root)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
    return rows


def run_conversions(
    jobs: Sequence[dict[str, Any]],
    *,
    checkpoint: Path,
    bpy_python: Path,
    worker: Path,
    workspace_root: Path,
    workers: int,
    batch_size: int,
    timeout_seconds: float,
    resume: bool,
) -> list[dict[str, Any]]:
    jobs_by_id = {str(row["material_id"]): row for row in jobs}
    existing = (
        _read_checkpoint(checkpoint, jobs_by_id, workspace_root=workspace_root) if resume else {}
    )
    if checkpoint.exists() and not resume:
        raise ValueError(f"checkpoint already exists; use --resume: {checkpoint}")
    pending = [job for job in jobs if job["material_id"] not in existing]
    batches = [pending[index : index + batch_size] for index in range(0, len(pending), batch_size)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                _run_isolated_batch,
                batch,
                bpy_python=bpy_python,
                worker=worker,
                workspace_root=workspace_root,
                timeout_seconds=timeout_seconds,
            ): batch
            for batch in batches
        }
        for future in concurrent.futures.as_completed(futures):
            batch_jobs = {str(row["material_id"]): row for row in futures[future]}
            for raw in future.result():
                material_id = str(raw.get("material_id") or "")
                job = batch_jobs.get(material_id)
                if job is None:
                    raise RuntimeError(f"worker returned unexpected material_id {material_id!r}")
                existing[material_id] = _validate_result(
                    raw, job, workspace_root=workspace_root, allow_published=False
                )
            atomic_jsonl(checkpoint, (existing[key] for key in sorted(existing)))
    if len(existing) != len(jobs):
        raise RuntimeError(f"conversion checkpoint is incomplete: {len(existing)} of {len(jobs)}")
    return [existing[str(job["material_id"])] for job in jobs]


def _channel_rows(worker_metadata: Mapping[str, Any]) -> list[dict[str, Any]]:
    source = worker_metadata.get("baked_channels")
    if not isinstance(source, Mapping) or set(source) != set(CHANNELS):
        raise ValueError("worker metadata does not contain the four canonical channels")
    rows: list[dict[str, Any]] = []
    for channel in CHANNELS:
        value = source[channel]
        if not isinstance(value, Mapping) or value.get("packed") is not True:
            raise ValueError(f"worker channel {channel} is not packed")
        rows.append(
            {
                "colorspace": str(value.get("colorspace") or ""),
                "image_name": str(value.get("image_name") or f"Articraft_{channel}_1K"),
                "node_path": f"root/Articraft {channel}",
                "packed": True,
                "png_sha256": _require_sha256(
                    value.get("png_sha256"), field=f"worker channel {channel}.png_sha256"
                ),
                "resolution": list(value.get("resolution") or ()),
                "role": channel,
                "source_basename": f"{channel}.png",
            }
        )
    return rows


def _strict_metadata_and_row(
    job: Mapping[str, Any],
    result: Mapping[str, Any],
    worker_metadata: Mapping[str, Any],
    *,
    blend_relative: Path,
    metadata_relative: Path,
    blend_sha256: str,
    worker_metadata_sha256: str,
    provenance: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    source = dict(job["_source_row"])
    source.pop("_source_root", None)
    safe = dict(job["_safe_row"])
    material_id = str(job["material_id"])
    category = str(job["category_slug"])
    tile_size = float(job["texture_size_m"])
    channels = _channel_rows(worker_metadata)
    channel_counts = {channel: 1 for channel in CHANNELS}
    node_qa = {
        "status": "pass",
        "issues": [],
        "node_tree_count": 1,
        "node_count": 8,
        "output_surface_connected": True,
        "principled_bsdf_count": 1,
        "glass_bsdf_count": 0,
        "shader_node_count": 1,
        "image_texture_count": 4,
        "procedural_texture_node_count": 0,
        "packed_image_count": 4,
        "unpacked_image_count": 0,
    }
    material_name = f"ArticraftTextureSet_{hashlib.sha256(material_id.encode()).hexdigest()[:16]}"
    reopen_qa = {
        "status": "pass",
        "issues": [],
        "material_count": 1,
        "material_names": [material_name],
        "packed_image_count": 4,
        "unpacked_image_count": 0,
        "true_displacement_link_count": 0,
    }
    eligibility = generic_eligibility(
        display_name=str(job["display_name"]),
        category_slug=category,
        profile="texture_set",
        tile_size_m=tile_size,
        qa_status="pass",
    )
    mapping = {
        "coordinate_source": "baked_canonical_uv",
        "coordinate_unit": "meter",
        "generic_box_projection_allowed": False,
        "mapping_profile": "metric_uv_tangent",
        "model_uvs_are_not_baked": True,
        "normal_space": "tangent",
        "requires_uv": True,
        "tile_size_m": tile_size,
    }
    source_displacement = source.get("displacement_policy")
    displacement = (
        dict(source_displacement)
        if isinstance(source_displacement, Mapping)
        else {
            "normal_and_bump_preserved": True,
            "policy": "disconnect_true_displacement",
            "removed_output_link_count": 0,
            "source_output_link_count": 0,
        }
    )
    displacement["policy"] = "disconnect_true_displacement"
    derivation = {
        "schema_version": DERIVATION_SCHEMA,
        "conversion_version": CONVERSION_VERSION,
        "conversion_input_sha256": job["conversion_input_sha256"],
        "worker_bpy_version": result.get("bpy_version"),
        "worker_metadata_sha256": worker_metadata_sha256,
        "source_material_profile": "native_procedural",
        "source_normalized_blend_path": source["normalized_blend_path"],
        "source_normalized_blend_sha256": source["sha256"],
        "source_normalized_catalog_sha256": provenance["source_catalog_sha256"],
        "safe_list_sha256": provenance["safe_jsonl_sha256"],
        "eligibility": {
            "classifier_version": safe["classifier_version"],
            "decision": safe["decision"],
            "input_sha256": safe["input_sha256"],
            "reason_codes": list(safe.get("reason_codes") or ()),
        },
        "bake": dict(worker_metadata.get("bake") or {}),
        "maps": {
            row["role"]: {
                "png_sha256": row["png_sha256"],
                "resolution": row["resolution"],
            }
            for row in channels
        },
    }
    source_provenance = source.get("provenance")
    source_provenance = dict(source_provenance) if isinstance(source_provenance, Mapping) else {}
    source_provenance["parent_normalized_blend_path"] = source["normalized_blend_path"]
    source_provenance["parent_normalized_blend_sha256"] = source["sha256"]
    metadata = {
        "schema_version": NORMALIZED_PACKAGE_SCHEMA,
        "material_id": material_id,
        "category_slug": category,
        "display_name": str(job["display_name"]),
        "material_profile": "texture_set",
        "normalization_class": "normalizable",
        "texture_size_m": tile_size,
        "texture_size_source": "source_normalized_catalog.texture_size_m",
        "mapping_contract": mapping,
        "eligibility": eligibility,
        "displacement_policy": displacement,
        "material_repairs": {},
        "optical_policy": None,
        "channel_qa": {"channels": channels, "channel_counts": channel_counts},
        "node_qa": node_qa,
        "package": {
            "blend_path": blend_relative.as_posix(),
            "blend_sha256": blend_sha256,
            "bpy_version": result.get("bpy_version"),
            "source_material_name": source.get("display_name"),
            "available_material_names": [material_name],
            "reopen_qa": reopen_qa,
        },
        "source": source_provenance,
        "normalizer": {
            "version": NORMALIZER_VERSION,
            "source_preserved": False,
            "shader_graph_policy": "native_baked_to_texture_set",
        },
        "derivation": derivation,
    }
    source_payload = source.get("source")
    source_payload = dict(source_payload) if isinstance(source_payload, Mapping) else {}
    row = {
        "schema_version": NORMALIZED_CATALOG_SCHEMA,
        "material_id": material_id,
        "category_slug": category,
        "display_name": str(job["display_name"]),
        "provider": str(source.get("provider") or "blenderkit"),
        "license": str(source.get("license") or "unknown"),
        "asset_base_id": str(source.get("asset_base_id") or material_id),
        "tags": list(source.get("tags") or source_payload.get("tags") or ()),
        "source": source_payload,
        "normalized_blend_path": blend_relative.as_posix(),
        "normalized_metadata_path": metadata_relative.as_posix(),
        "sha256": blend_sha256,
        "material_profile": "texture_set",
        "normalization_class": "normalizable",
        "texture_size_m": tile_size,
        "mapping_contract": mapping,
        "eligibility": eligibility,
        "eligible_for_generic": eligibility["eligible_for_generic"],
        "restrictions": eligibility["restrictions"],
        "quarantine_reason": eligibility["quarantine_reason"],
        "normalization_version": NORMALIZER_VERSION,
        "channels": channels,
        "displacement_policy": displacement,
        "material_repairs": {},
        "optical_policy": None,
        "package_reopen_qa": reopen_qa,
        "active": True,
        "validation": eligibility["validation"],
        "selection_scope": eligibility["selection_scope"],
        "allowed_component_roles": eligibility["allowed_component_roles"],
        "excluded_component_roles": eligibility["excluded_component_roles"],
        "material_subtype": eligibility["material_subtype"],
        "qa_flags": eligibility["qa_flags"],
        "recommended_use": eligibility["recommended_use"],
        "semantic_advisories": eligibility["semantic_advisories"],
        "recommended_component_roles": eligibility["recommended_component_roles"],
        "semantic_risk_reason": eligibility["semantic_risk_reason"],
        "channel_qa": metadata["channel_qa"],
        "node_qa": node_qa,
        "provenance": source_provenance,
        "normalizer": metadata["normalizer"],
        "derivation": derivation,
        "runtime_enabled": True,
        "runtime_profile": {
            "enabled": True,
            "native_allowlisted": False,
            "policy_version": RUNTIME_PROFILE_POLICY_VERSION,
            "reason": "texture_set_qa_pass",
        },
    }
    return metadata, row


def _publish_success(
    job: Mapping[str, Any],
    result: Mapping[str, Any],
    *,
    workspace_root: Path,
    output_root: Path,
    provenance: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    output = result["output"]
    assert isinstance(output, Mapping)
    worker_blend = workspace_root / safe_relative_path(
        output["blend_path"], field=f"{job['material_id']}.output.blend_path"
    )
    worker_metadata_path = workspace_root / safe_relative_path(
        output["metadata_path"], field=f"{job['material_id']}.output.metadata_path"
    )
    worker_metadata_sha = _sha256_file(worker_metadata_path)
    worker_metadata = json.loads(worker_metadata_path.read_text(encoding="utf-8"))
    identity = canonical_json_sha256(
        {"conversion_version": CONVERSION_VERSION, "material_id": job["material_id"]}
    )[:16]
    content = canonical_json_sha256(
        {
            "conversion_input_sha256": job["conversion_input_sha256"],
            "safe_list_sha256": provenance["safe_jsonl_sha256"],
            "worker_blend_sha256": output["blend_sha256"],
        }
    )[:16]
    relative_dir = Path("packages") / str(job["category_slug"]) / identity / content
    blend_relative = relative_dir / "material.blend"
    metadata_relative = relative_dir / "metadata.json"
    destination = output_root / relative_dir
    staging_parent = output_root / ".conversion" / "publish"
    staging_parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{identity}-", dir=staging_parent))
    try:
        staged_blend = staging / "material.blend"
        shutil.copy2(worker_blend, staged_blend)
        blend_sha = _sha256_file(staged_blend)
        if blend_sha != output["blend_sha256"]:
            raise ValueError(f"blend changed while publishing {job['material_id']}")
        metadata, row = _strict_metadata_and_row(
            job,
            result,
            worker_metadata,
            blend_relative=blend_relative,
            metadata_relative=metadata_relative,
            blend_sha256=blend_sha,
            worker_metadata_sha256=worker_metadata_sha,
            provenance=provenance,
        )
        atomic_json(staging / "metadata.json", metadata)
        if destination.exists():
            existing_blend = destination / "material.blend"
            existing_metadata = destination / "metadata.json"
            if _sha256_file(existing_blend) != blend_sha or _sha256_file(
                existing_metadata
            ) != _sha256_file(staging / "metadata.json"):
                raise FileExistsError(f"derived package collision: {destination}")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.rename(staging, destination)
        publisher = {
            "blend_path": _relative_to(
                workspace_root, destination / "material.blend", field="published blend"
            ),
            "blend_sha256": blend_sha,
            "metadata_path": _relative_to(
                workspace_root, destination / "metadata.json", field="published metadata"
            ),
            "metadata_sha256": _sha256_file(destination / "metadata.json"),
            "catalog_row": row,
        }
        return row, publisher
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)


def publish_packages(
    jobs: Sequence[dict[str, Any]],
    results: Sequence[dict[str, Any]],
    *,
    checkpoint: Path,
    workspace_root: Path,
    output_root: Path,
    provenance: Mapping[str, Any],
) -> list[dict[str, Any]]:
    jobs_by_id = {str(job["material_id"]): job for job in jobs}
    checkpoint_rows = {str(row["material_id"]): dict(row) for row in results}
    catalog_rows: list[dict[str, Any]] = []
    for result in results:
        if result["status"] != "success":
            continue
        material_id = str(result["material_id"])
        job = jobs_by_id[material_id]
        published = result.get("publisher")
        if isinstance(published, Mapping):
            row = dict(published["catalog_row"])
        else:
            row, publisher = _publish_success(
                job,
                result,
                workspace_root=workspace_root,
                output_root=output_root,
                provenance=provenance,
            )
            checkpoint_rows[material_id]["publisher"] = publisher
            atomic_jsonl(
                checkpoint,
                (checkpoint_rows[key] for key in sorted(checkpoint_rows)),
            )
        catalog_rows.append(row)
    catalog_rows.sort(key=lambda row: (str(row["category_slug"]), str(row["material_id"])))
    return catalog_rows


def _publish_catalog(
    rows: Sequence[dict[str, Any]],
    *,
    output_root: Path,
    provenance: Mapping[str, Any],
) -> tuple[Path, str, str]:
    if not rows:
        raise ValueError("no successful conversions; refusing to publish an empty catalog")
    staging_parent = output_root / ".conversion"
    staging_parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".catalog-", dir=staging_parent))
    try:
        catalog = staging / "materials.jsonl"
        atomic_jsonl(catalog, rows)
        catalog_sha = _sha256_file(catalog)
        raw = provenance["source_raw_catalog"]
        raw_sha = _require_sha256(raw["sha256"], field="source raw catalog SHA")
        allowlist_sha = native_runtime_allowlist_sha256(())
        logical_sha = logical_catalog_snapshot_sha256(
            catalog_file_sha256=catalog_sha,
            raw_catalog_sha256=raw_sha,
            native_allowlist_sha256=allowlist_sha,
            normalizer_version=NORMALIZER_VERSION,
        )
        manifest = {
            "schema_version": NORMALIZED_CATALOG_MANIFEST_SCHEMA,
            "logical_snapshot_sha256": logical_sha,
            "materials_file": {
                "material_count": len(rows),
                "path": "materials.jsonl",
                "sha256": catalog_sha,
            },
            "raw_catalog": dict(raw),
            "native_runtime_allowlist_sha256": allowlist_sha,
            "normalizer_version": NORMALIZER_VERSION,
            "runtime_profile_policy_version": RUNTIME_PROFILE_POLICY_VERSION,
            "derivation": {
                "schema_version": DERIVATION_SCHEMA,
                "conversion_version": CONVERSION_VERSION,
                "source_normalized_catalog_path": provenance["source_catalog_path"],
                "source_normalized_catalog_sha256": provenance["source_catalog_sha256"],
                "source_logical_snapshot_sha256": provenance["source_logical_snapshot_sha256"],
                "safe_list_sha256": provenance["safe_jsonl_sha256"],
            },
        }
        atomic_json(staging / "manifest.json", manifest)
        destination = output_root / "catalogs" / logical_sha
        if destination.exists():
            if (
                _sha256_file(destination / "materials.jsonl") != catalog_sha
                or json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
                != manifest
            ):
                raise FileExistsError(f"derived catalog snapshot collision: {destination}")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.rename(staging, destination)
        atomic_json(
            output_root / "catalogs" / "latest.json",
            {
                "catalog_path": f"catalogs/{logical_sha}/materials.jsonl",
                "logical_snapshot_sha256": logical_sha,
                "manifest_path": f"catalogs/{logical_sha}/manifest.json",
            },
        )
        return destination / "materials.jsonl", logical_sha, catalog_sha
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)


def default_workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_source_root() -> Path:
    return default_workspace_root() / ".artifacts" / "pbr_material_library" / "normalized"


def default_output_root() -> Path:
    return (
        default_workspace_root()
        / ".artifacts"
        / "pbr_material_library"
        / "derived_texture_sets"
        / "native_baked_v1"
    )


def default_bpy_python() -> Path:
    return default_workspace_root() / ".cache" / "bpy-5.2-venv" / "bin" / "python"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--safe-jsonl", required=True, type=Path)
    parser.add_argument("--workspace-root", type=Path, default=default_workspace_root())
    parser.add_argument("--source-root", type=Path, default=default_source_root())
    parser.add_argument("--output-root", type=Path, default=default_output_root())
    parser.add_argument("--bpy-python", type=Path, default=default_bpy_python())
    parser.add_argument(
        "--worker",
        type=Path,
        default=Path(__file__).with_name("_bpy_convert_native_texture_set_worker.py"),
    )
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.workers < 1 or args.batch_size < 1 or args.timeout <= 0:
        raise SystemExit("workers, batch-size, and timeout must be positive")
    if args.resume and not args.execute:
        raise SystemExit("--resume requires --execute")
    workspace = args.workspace_root.resolve(strict=True)
    source_root = args.source_root.resolve(strict=True)
    output_root = args.output_root.resolve(strict=False)
    provenance, jobs = load_conversion_jobs(
        source_catalog=args.catalog,
        source_root=source_root,
        safe_jsonl=args.safe_jsonl,
        workspace_root=workspace,
        output_root=output_root,
    )
    plan: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA,
        "mode": "execute" if args.execute else "dry_run",
        "conversion_version": CONVERSION_VERSION,
        **provenance,
        "output_root": _relative_to(workspace, output_root, field="output_root"),
        "writes_source_catalog_or_packages": False,
        "planned_material_count": len(jobs),
        "workers": args.workers,
        "batch_size": args.batch_size,
    }
    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, sort_keys=True))
        return 0
    if not args.bpy_python.is_file() or not args.worker.is_file():
        raise SystemExit("bpy Python or conversion worker is missing")
    output_root.mkdir(parents=True, exist_ok=True)
    checkpoint = output_root / ".conversion" / "conversion_results.jsonl"
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    results = run_conversions(
        jobs,
        checkpoint=checkpoint,
        bpy_python=args.bpy_python,
        worker=args.worker,
        workspace_root=workspace,
        workers=args.workers,
        batch_size=args.batch_size,
        timeout_seconds=args.timeout,
        resume=args.resume,
    )
    rows = publish_packages(
        jobs,
        results,
        checkpoint=checkpoint,
        workspace_root=workspace,
        output_root=output_root,
        provenance=provenance,
    )
    catalog, logical_sha, catalog_sha = _publish_catalog(
        rows, output_root=output_root, provenance=provenance
    )
    strict = MaterialCatalog.from_jsonl(catalog, library_root=output_root, strict_normalized=True)
    failures = [row for row in results if row["status"] == "failure"]
    summary = {
        **plan,
        "converted_success_count": len(rows),
        "conversion_failure_count": len(failures),
        "failure_material_ids": sorted(str(row["material_id"]) for row in failures),
        "catalog_path": catalog.relative_to(output_root).as_posix(),
        "catalog_sha256": catalog_sha,
        "logical_snapshot_sha256": logical_sha,
        "strict_reader_material_count": len(strict.records),
        "checkpoint_path": checkpoint.relative_to(output_root).as_posix(),
    }
    atomic_json(output_root / ".conversion" / "summary.json", summary)
    for job in jobs:
        work_dir = workspace / str(job["output_dir"])
        if work_dir.is_dir():
            shutil.rmtree(work_dir)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
