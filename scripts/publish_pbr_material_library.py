#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Publish an immutable unified material/physics library from offline artifacts.

The publisher deliberately keeps the source normalization and classification
artifacts immutable.  Only runtime-enabled, assigned materials enter the
formal library. Runtime snapshots contain a manifest, material-class pools,
the package files referenced by those pools, and one hash-bound physics
sidecar per concrete material. Every package is copied into the release
namespace with a hard link when source and destination share a filesystem;
EXDEV is the sole copy fallback.
"""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import errno
import fcntl
import hashlib
import json
import math
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG_POINTER = (
    REPO_ROOT / ".artifacts/pbr_material_library/normalized/catalogs/latest.json"
)
DEFAULT_ASSIGNMENT_POINTER = REPO_ROOT / (
    ".artifacts/pbr_material_library/normalized/"
    "material_class_reassessment_8412_registry127_v16_20260811/latest-review.json"
)
DEFAULT_REGISTRY = REPO_ROOT / "data/material_classes_v1.json"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "pbr_material_library"
DEFAULT_PHYSICS_RUN = REPO_ROOT / (
    ".artifacts/pbr_material_physics/qwen38_high_v2/snapshots/"
    "470f938ed1e7217054d00466a92d68b9756700ecbecee9e5fe9d66396d6e35f5"
)

PUBLISHER_VERSION = "articraft-pbr-library-publisher/v4"
RELEASE_SCHEMA = "articraft-pbr-material-library-release/v3"
POINTER_SCHEMA = "articraft-pbr-material-library-pointer/v3"
POOL_SCHEMA = "articraft-material-class-pool/v3"
POOL_INDEX_SCHEMA = "articraft-material-class-pool-index/v3"
LEGACY_RELEASE_SCHEMA = "articraft-pbr-material-library-release/v2"
LEGACY_POOL_INDEX_SCHEMA = "articraft-material-class-pool-index/v2"
LEGACY_PUBLISHER_VERSION = "articraft-pbr-library-publisher/v3"
PHYSICS_RUN_SCHEMA = "articraft-pbr-material-physics-run/v1"
PHYSICS_ANNOTATION_SCHEMA = "articraft-pbr-material-physics-annotation/v1"
PHYSICS_REF_SCHEMA = "articraft-pbr-material-physics-ref/v1"
PHYSICS_SIDECAR_SCHEMA = "articraft-pbr-material-physics-sidecar/v1"
PHYSICS_INDEX_SCHEMA = "articraft-pbr-material-physics-index/v1"
REGISTRY_REMOVAL_AUDIT_SCHEMA = "articraft-material-class-registry-removal-audit/v1"
REGISTRY_SCHEMA = "articraft-material-class-registry/v1"
ASSIGNMENTS_SCHEMA = "articraft-material-class-assignments/v1"
POLICY_VERSION = "exact-material-class-pool/v1"
RUNTIME_ASSIGNMENT_DIGEST_SCHEMA = "articraft-pbr-runtime-assignment-digest/v1"
NORMALIZED_CATALOG_MANIFEST_SCHEMA = "articraft-normalized-material-catalog-manifest/v1"
NORMALIZER_VERSION = "articraft-pbr-normalizer/v1"
RUNTIME_PROFILE_POLICY_VERSION = "articraft-material-runtime-profile/v1"

_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_CLASS_RE = re.compile(r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$")
RUNTIME_MATERIAL_RECORD_FIELDS = frozenset(
    {
        "asset_base_id",
        "material_id",
        "material_class_id",
        "category_slug",
        "blend_path",
        "blend_sha256",
        "blend_size_bytes",
        "metadata_path",
        "metadata_sha256",
        "metadata_size_bytes",
        "display_name",
        "license",
        "provider",
        "material_profile",
        "mapping_profile",
        "texture_size_m",
        "normal_space",
        "requires_uv",
        "physics_ref",
    }
)
LEGACY_RUNTIME_MATERIAL_RECORD_FIELDS = RUNTIME_MATERIAL_RECORD_FIELDS - {"physics_ref"}


@dataclass(frozen=True, slots=True)
class CatalogInput:
    catalog_path: Path
    manifest_path: Path
    library_root: Path
    manifest: dict[str, Any]
    manifest_sha256: str


@dataclass(frozen=True, slots=True)
class AssignmentInput:
    snapshot_dir: Path
    manifest_path: Path
    assignments_path: Path
    decisions_path: Path
    review_path: Path
    manifest: dict[str, Any]
    manifest_sha256: str


@dataclass(frozen=True, slots=True)
class PhysicsInput:
    snapshot_dir: Path
    manifest: dict[str, Any]
    manifest_sha256: str
    run: dict[str, Any]
    run_sha256: str
    index_sha256: str
    audit_sha256: str
    jobs_sha256: str
    annotations: dict[str, dict[str, Any]]
    annotation_sha256: dict[str, str]


@dataclass(frozen=True, slots=True)
class BaseAppearanceInput:
    """Immutable v2 appearance snapshot to which physics was annotated."""

    snapshot_dir: Path
    manifest_path: Path
    pool_index_path: Path
    logical_snapshot_sha256: str
    manifest_sha256: str
    pool_index_sha256: str
    material_records: dict[str, dict[str, Any]]


_PHYSICS_FIELDS = (
    "density_kg_m3",
    "youngs_modulus_pa",
    "poissons_ratio",
    "static_friction_coefficient",
    "dynamic_friction_coefficient",
    "restitution_coefficient",
)


def _validate_physics_annotation(record: Mapping[str, Any], *, material_id: str) -> None:
    physics = record.get("physics")
    estimates = record.get("estimates")
    if not isinstance(physics, dict) or set(physics) != set(_PHYSICS_FIELDS):
        raise ValueError(f"physics annotation values are incomplete: {material_id}")
    if not isinstance(estimates, dict) or set(estimates) != set(_PHYSICS_FIELDS):
        raise ValueError(f"physics annotation estimates are incomplete: {material_id}")
    numeric: dict[str, float] = {}
    for field in _PHYSICS_FIELDS:
        value = physics[field]
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError(f"physics annotation {field} is not finite: {material_id}")
        number = float(value)
        numeric[field] = number
        if field in {"density_kg_m3", "youngs_modulus_pa"} and number <= 0:
            raise ValueError(f"physics annotation {field} must be positive: {material_id}")
        if field == "poissons_ratio" and not (0.0 <= number < 0.5):
            raise ValueError(f"physics annotation poissons_ratio is out of bounds: {material_id}")
        if field in {"static_friction_coefficient", "dynamic_friction_coefficient"} and number < 0:
            raise ValueError(f"physics annotation {field} must be nonnegative: {material_id}")
        if field == "restitution_coefficient" and not (0.0 <= number <= 1.0):
            raise ValueError(f"physics annotation restitution is out of bounds: {material_id}")
        estimate = estimates[field]
        required = {"low", "value", "high", "confidence", "applicability", "basis"}
        if not isinstance(estimate, dict) or set(estimate) != required:
            raise ValueError(f"physics annotation {field} estimate schema mismatch: {material_id}")
        try:
            low = float(estimate["low"])
            point = float(estimate["value"])
            high = float(estimate["high"])
            confidence = float(estimate["confidence"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"physics annotation {field} estimate is not numeric: {material_id}"
            ) from exc
        if not all(math.isfinite(item) for item in (low, point, high, confidence)):
            raise ValueError(f"physics annotation {field} estimate is not finite: {material_id}")
        if not low <= point <= high or point != number or not 0.0 <= confidence <= 1.0:
            raise ValueError(f"physics annotation {field} interval/value mismatch: {material_id}")
        if (
            estimate["applicability"]
            not in {
                "native",
                "effective_proxy",
                "not_physically_native",
            }
            or not str(estimate["basis"] or "").strip()
        ):
            raise ValueError(f"physics annotation {field} evidence is invalid: {material_id}")
    if numeric["static_friction_coefficient"] < numeric["dynamic_friction_coefficient"]:
        raise ValueError(f"physics annotation static friction is below dynamic: {material_id}")


@dataclass(frozen=True, slots=True)
class PackageSource:
    material_id: str
    material_class_id: str
    category_slug: str
    blend_relative: str
    metadata_relative: str
    blend_path: Path
    metadata_path: Path
    expected_blend_sha256: str
    license: str
    provider: str
    display_name: str
    material_profile: str
    mapping_profile: str | None
    texture_size_m: float | None
    normal_space: str | None
    requires_uv: bool
    asset_base_id: str
    provenance: dict[str, Any]


@dataclass(frozen=True, slots=True)
class PackageResult:
    runtime_record: dict[str, Any]
    hardlinked_file_count: int
    copied_file_count: int
    package_bytes: int


def _canonical_json_bytes(value: object, *, pretty: bool = False) -> bytes:
    options: dict[str, Any] = {
        "ensure_ascii": False,
        "sort_keys": True,
    }
    if pretty:
        options["indent"] = 2
    else:
        options["separators"] = (",", ":")
    return (json.dumps(value, **options) + "\n").encode("utf-8")


def _canonical_json_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _write_json(path: Path, value: object) -> str:
    payload = _canonical_json_bytes(value, pretty=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return _sha256_bytes(payload)


def _contained(path: Path, *, root: Path, strict: bool) -> Path:
    resolved_root = root.resolve(strict=True)
    resolved = path.resolve(strict=strict)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"path escapes workspace {resolved_root}: {resolved}") from exc
    return resolved


def _safe_relative(value: object, *, field: str) -> Path:
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
        raise ValueError(f"{field} must be a contained POSIX relative path: {text!r}")
    return Path(*posix.parts)


def _contained_join(
    root: Path,
    value: object,
    *,
    field: str,
    strict: bool,
) -> Path:
    relative = _safe_relative(value, field=field)
    resolved_root = root.resolve(strict=True)
    resolved = (resolved_root / relative).resolve(strict=strict)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"{field} escapes {resolved_root}: {value!r}") from exc
    return resolved


def _require_sha(value: object, *, field: str) -> str:
    text = str(value or "")
    if _SHA_RE.fullmatch(text) is None:
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return text


def _relative_to_workspace(path: Path, workspace_root: Path) -> str:
    return path.resolve(strict=True).relative_to(workspace_root.resolve(strict=True)).as_posix()


def _logical_catalog_sha(
    *,
    catalog_file_sha256: str,
    raw_catalog_sha256: str,
    native_allowlist_sha256: str,
    normalizer_version: str,
) -> str:
    return _canonical_json_sha256(
        {
            "catalog_file_sha256": _require_sha(catalog_file_sha256, field="catalog_file_sha256"),
            "native_allowlist_sha256": _require_sha(
                native_allowlist_sha256, field="native_allowlist_sha256"
            ),
            "normalizer_version": normalizer_version,
            "raw_catalog_sha256": _require_sha(raw_catalog_sha256, field="raw_catalog_sha256"),
            "schema_version": NORMALIZED_CATALOG_MANIFEST_SCHEMA,
        }
    )


def load_catalog_input(pointer_path: Path, *, workspace_root: Path) -> CatalogInput:
    pointer = _contained(pointer_path, root=workspace_root, strict=True)
    value = _json_object(pointer)
    if "catalog_path" in value:
        base = pointer.parent.parent if pointer.parent.name == "catalogs" else pointer.parent
        catalog = _contained_join(
            base,
            value["catalog_path"],
            field="catalog pointer catalog_path",
            strict=True,
        )
        manifest = _contained_join(
            base,
            value["manifest_path"],
            field="catalog pointer manifest_path",
            strict=True,
        )
        pointer_sha = _require_sha(
            value.get("logical_snapshot_sha256"),
            field="catalog pointer logical_snapshot_sha256",
        )
    elif pointer.name == "materials.jsonl":
        catalog = pointer
        manifest = pointer.with_name("manifest.json").resolve(strict=True)
        pointer_sha = ""
    else:
        raise ValueError(f"unsupported catalog input: {pointer}")
    catalog = _contained(catalog, root=workspace_root, strict=True)
    manifest = _contained(manifest, root=workspace_root, strict=True)
    manifest_value = _json_object(manifest)
    if manifest_value.get("schema_version") != NORMALIZED_CATALOG_MANIFEST_SCHEMA:
        raise ValueError("normalized catalog manifest schema mismatch")
    logical_sha = _require_sha(
        manifest_value.get("logical_snapshot_sha256"),
        field="catalog manifest logical_snapshot_sha256",
    )
    if pointer_sha and pointer_sha != logical_sha:
        raise ValueError("catalog pointer and manifest snapshot mismatch")
    if catalog.parent.name != logical_sha or catalog.name != "materials.jsonl":
        raise ValueError("normalized catalog path is not content-addressed")
    library_root = catalog.parents[2].resolve(strict=True)
    _contained(library_root, root=workspace_root, strict=True)
    return CatalogInput(
        catalog_path=catalog,
        manifest_path=manifest,
        library_root=library_root,
        manifest=manifest_value,
        manifest_sha256=_sha256_file(manifest),
    )


def load_assignment_input(pointer_path: Path, *, workspace_root: Path) -> AssignmentInput:
    pointer = _contained(pointer_path, root=workspace_root, strict=True)
    value = _json_object(pointer)
    if "snapshot_path" in value:
        base = pointer.parent
        snapshot = _contained_join(
            base,
            value["snapshot_path"],
            field="assignment pointer snapshot_path",
            strict=True,
        )
        pointer_sha = _require_sha(
            value.get("logical_snapshot_sha256"),
            field="assignment pointer logical_snapshot_sha256",
        )
    elif pointer.is_dir():
        snapshot = pointer
        pointer_sha = ""
    else:
        raise ValueError(f"unsupported assignment input: {pointer}")
    manifest_path = _contained(snapshot / "manifest.json", root=workspace_root, strict=True)
    manifest = _json_object(manifest_path)
    logical_sha = _require_sha(
        manifest.get("logical_snapshot_sha256"),
        field="assignment manifest logical_snapshot_sha256",
    )
    if pointer_sha and pointer_sha != logical_sha:
        raise ValueError("assignment pointer and manifest snapshot mismatch")
    if snapshot.name != logical_sha:
        raise ValueError("assignment snapshot path is not content-addressed")
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise ValueError("assignment manifest lacks files table")
    resolved: dict[str, Path] = {}
    for name in ("assignments.json", "decisions.jsonl", "review.jsonl"):
        path = _contained(snapshot / name, root=workspace_root, strict=True)
        metadata = files.get(name)
        if not isinstance(metadata, dict):
            raise ValueError(f"assignment manifest lacks {name}")
        expected = _require_sha(metadata.get("sha256"), field=f"assignment {name} SHA")
        if _sha256_file(path) != expected:
            raise ValueError(f"assignment source {name} SHA mismatch")
        resolved[name] = path
    return AssignmentInput(
        snapshot_dir=snapshot,
        manifest_path=manifest_path,
        assignments_path=resolved["assignments.json"],
        decisions_path=resolved["decisions.jsonl"],
        review_path=resolved["review.jsonl"],
        manifest=manifest,
        manifest_sha256=_sha256_file(manifest_path),
    )


def load_registry(
    path: Path,
    *,
    workspace_root: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], str, str]:
    source = _contained(path, root=workspace_root, strict=True)
    source_bytes = source.read_bytes()
    value = json.loads(source_bytes)
    if not isinstance(value, dict) or value.get("schema_version") != REGISTRY_SCHEMA:
        raise ValueError("material class registry schema mismatch")
    if value.get("policy_version", POLICY_VERSION) != POLICY_VERSION:
        raise ValueError("material class registry policy mismatch")
    rows = value.get("classes")
    if not isinstance(rows, list) or not rows:
        raise ValueError("material class registry is empty")
    by_id: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"registry class[{index}] must be an object")
        class_id = str(row.get("material_class_id") or "")
        category = str(row.get("parent_category") or "")
        if _CLASS_RE.fullmatch(class_id) is None or not category:
            raise ValueError(f"invalid registry class[{index}]")
        if class_id.split(".", 1)[0] != category:
            raise ValueError(f"registry class parent mismatch: {class_id}")
        if class_id in by_id:
            raise ValueError(f"duplicate material_class_id: {class_id}")
        by_id[class_id] = dict(row)
    document = {
        "schema_version": REGISTRY_SCHEMA,
        "policy_version": POLICY_VERSION,
        "classes": [by_id[class_id] for class_id in sorted(by_id)],
    }
    logical_sha = _sha256_bytes(_canonical_json_bytes(document))
    return document, by_id, logical_sha, _sha256_bytes(source_bytes)


def load_runtime_assignments(
    source: AssignmentInput,
    *,
    registry_by_id: Mapping[str, Mapping[str, Any]],
) -> tuple[
    dict[str, str],
    int,
    collections.Counter[str],
    collections.Counter[str],
]:
    assignments_value = _json_object(source.assignments_path)
    assignments_snapshot_sha = _sha256_bytes(_canonical_json_bytes(assignments_value))
    if source.manifest.get("assignments_snapshot_sha256") != assignments_snapshot_sha:
        raise ValueError("assignment document logical SHA mismatch")
    if assignments_value.get("schema_version") != ASSIGNMENTS_SCHEMA:
        raise ValueError("assignment document schema mismatch")
    if assignments_value.get("policy_version") != POLICY_VERSION:
        raise ValueError("assignment document policy mismatch")
    if assignments_value.get("registry_snapshot_sha256") != source.manifest.get(
        "registry_snapshot_sha256"
    ):
        raise ValueError("assignment document registry snapshot mismatch")
    if assignments_value.get("catalog_snapshot_sha256") != source.manifest.get(
        "catalog_snapshot_sha256"
    ):
        raise ValueError("assignment document catalog snapshot mismatch")
    source_rows = assignments_value.get("assignments")
    if not isinstance(source_rows, list):
        raise ValueError("assignment source lacks assignments")
    source_map: dict[str, str] = {}
    source_class_counts: collections.Counter[str] = collections.Counter()
    for index, row in enumerate(source_rows):
        if not isinstance(row, dict) or set(row) != {"material_id", "material_class_id"}:
            raise ValueError(f"invalid source assignment[{index}]")
        material_id = str(row["material_id"])
        class_id = str(row["material_class_id"])
        if material_id in source_map:
            raise ValueError(f"duplicate source assignment: {material_id}")
        source_map[material_id] = class_id
        source_class_counts[class_id] += 1

    selected: dict[str, str] = {}
    runtime_review = 0
    seen_decisions: set[str] = set()
    decision_class_counts: collections.Counter[str] = collections.Counter()
    with source.decisions_path.open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            row = json.loads(raw)
            if not isinstance(row, dict):
                raise ValueError(f"decision line {line_number} is not an object")
            material_id = str(row.get("material_id") or "")
            if not material_id or material_id in seen_decisions:
                raise ValueError(f"duplicate or empty decision material_id at line {line_number}")
            seen_decisions.add(material_id)
            decision_class_id = str(row.get("material_class_id") or "")
            if decision_class_id:
                decision_class_counts[decision_class_id] += 1
            if row.get("runtime_enabled") is not True:
                continue
            if row.get("status") == "review":
                runtime_review += 1
                continue
            if row.get("status") != "assigned":
                raise ValueError(f"unknown runtime decision status for {material_id}")
            class_id = str(row.get("material_class_id") or "")
            if class_id not in registry_by_id:
                raise ValueError(f"runtime assignment uses unknown class: {class_id}")
            if source_map.get(material_id) != class_id:
                raise ValueError(f"runtime decision/assignment mismatch: {material_id}")
            selected[material_id] = class_id
    summary = source.manifest.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("assignment manifest lacks summary")
    if summary.get("runtime_assigned_material_count") != len(selected):
        raise ValueError("runtime assigned count disagrees with assignment manifest")
    if summary.get("runtime_review_material_count") != runtime_review:
        raise ValueError("runtime review count disagrees with assignment manifest")
    logical_identity = {
        field: source.manifest.get(field)
        for field in (
            "schema_version",
            "builder_version",
            "policy_version",
            "registry_snapshot_sha256",
            "catalog_snapshot_sha256",
            "assignments_snapshot_sha256",
            "decisions_sha256",
            "review_sha256",
            "runtime_ready",
        )
    }
    if _sha256_bytes(_canonical_json_bytes(logical_identity)) != source.manifest.get(
        "logical_snapshot_sha256"
    ):
        raise ValueError("assignment source logical snapshot SHA mismatch")
    return selected, runtime_review, source_class_counts, decision_class_counts


def _audit_zero_assignment_class_removal(
    *,
    source_registry_by_id: Mapping[str, Mapping[str, Any]],
    source_registry_sha256: str,
    target_registry_by_id: Mapping[str, Mapping[str, Any]],
    target_registry_sha256: str,
    allowed_removals: Sequence[str],
    source_class_counts: Mapping[str, int],
    decision_class_counts: Mapping[str, int],
    assignment_snapshot_sha256: str,
) -> dict[str, Any]:
    allowed = tuple(str(class_id) for class_id in allowed_removals)
    if not allowed:
        raise ValueError("registry drift requires explicit zero-assignment class removals")
    if len(allowed) != len(set(allowed)):
        raise ValueError("zero-assignment class removal allowlist contains duplicates")
    invalid = sorted(class_id for class_id in allowed if _CLASS_RE.fullmatch(class_id) is None)
    if invalid:
        raise ValueError(f"invalid zero-assignment class removal IDs: {invalid}")

    source_ids = set(source_registry_by_id)
    target_ids = set(target_registry_by_id)
    added = sorted(target_ids - source_ids)
    if added:
        raise ValueError(f"target registry adds classes during removal audit: {added}")
    changed = sorted(
        class_id
        for class_id in source_ids & target_ids
        if dict(source_registry_by_id[class_id]) != dict(target_registry_by_id[class_id])
    )
    if changed:
        raise ValueError(f"target registry changes retained class definitions: {changed}")
    removed = sorted(source_ids - target_ids)
    if removed != sorted(allowed):
        raise ValueError(
            "target registry removals do not match the explicit zero-assignment allowlist: "
            f"removed={removed}, allowed={sorted(allowed)}"
        )

    referenced = {
        class_id: {
            "assignment_count": int(source_class_counts.get(class_id, 0)),
            "decision_count": int(decision_class_counts.get(class_id, 0)),
        }
        for class_id in removed
        if source_class_counts.get(class_id, 0) or decision_class_counts.get(class_id, 0)
    }
    if referenced:
        raise ValueError(f"removed classes have nonzero source assignment references: {referenced}")

    return {
        "schema_version": REGISTRY_REMOVAL_AUDIT_SCHEMA,
        "source_assignment_snapshot_sha256": assignment_snapshot_sha256,
        "source_registry_snapshot_sha256": source_registry_sha256,
        "target_registry_snapshot_sha256": target_registry_sha256,
        "removed_zero_assignment_class_ids": removed,
        "removed_classes": [
            {
                "material_class_id": class_id,
                "definition": dict(source_registry_by_id[class_id]),
                "source_assignment_count": 0,
                "source_decision_count": 0,
            }
            for class_id in removed
        ],
        "removed_source_assignment_count": 0,
        "removed_source_decision_count": 0,
    }


def _scan_subset_catalog(
    *,
    source: CatalogInput,
    selected: Mapping[str, str],
    registry_by_id: Mapping[str, Mapping[str, Any]],
) -> tuple[list[PackageSource], str, collections.Counter[str], collections.Counter[str]]:
    source_digest = hashlib.sha256()
    subset_digest = hashlib.sha256()
    found: set[str] = set()
    all_ids: set[str] = set()
    packages: list[PackageSource] = []
    license_counts: collections.Counter[str] = collections.Counter()
    provider_counts: collections.Counter[str] = collections.Counter()
    with source.catalog_path.open("rb") as source_handle:
        for line_number, raw in enumerate(source_handle, 1):
            source_digest.update(raw)
            if not raw.strip():
                continue
            row = json.loads(raw)
            if not isinstance(row, dict):
                raise ValueError(f"catalog row {line_number} is not an object")
            material_id = str(row.get("material_id") or "")
            if not material_id or material_id in all_ids:
                raise ValueError(f"duplicate or empty catalog material_id at line {line_number}")
            all_ids.add(material_id)
            class_id = selected.get(material_id)
            if class_id is None:
                continue
            if row.get("runtime_enabled") is not True:
                raise ValueError(f"selected catalog row is not runtime-enabled: {material_id}")
            category = str(row.get("category_slug") or "")
            if registry_by_id[class_id]["parent_category"] != category:
                raise ValueError(f"catalog/class parent mismatch for {material_id}")
            blend_relative = _safe_relative(
                row.get("normalized_blend_path"),
                field=f"{material_id}.normalized_blend_path",
            ).as_posix()
            metadata_relative = _safe_relative(
                row.get("normalized_metadata_path"),
                field=f"{material_id}.normalized_metadata_path",
            ).as_posix()
            blend_rel_path = Path(blend_relative)
            metadata_rel_path = Path(metadata_relative)
            if (
                blend_rel_path.name != "material.blend"
                or metadata_rel_path.name != "metadata.json"
                or blend_rel_path.parent != metadata_rel_path.parent
            ):
                raise ValueError(f"catalog package pair is malformed: {material_id}")
            blend_path = _contained_join(
                source.library_root,
                blend_relative,
                field=f"{material_id}.normalized_blend_path",
                strict=True,
            )
            metadata_path = _contained_join(
                source.library_root,
                metadata_relative,
                field=f"{material_id}.normalized_metadata_path",
                strict=True,
            )
            expected_sha = _require_sha(row.get("sha256"), field=f"{material_id}.sha256")
            license_value = str(
                row.get("license")
                or (row.get("provenance") or {}).get("license")
                or (row.get("source") or {}).get("license")
                or "unknown"
            )
            provider = str(row.get("provider") or "blenderkit")
            display_name = str(row.get("display_name") or "").strip()
            if not display_name:
                raise ValueError(f"selected catalog row lacks display_name: {material_id}")
            material_profile = str(row.get("material_profile") or "").strip()
            if not material_profile:
                raise ValueError(f"selected catalog row lacks material_profile: {material_id}")
            mapping_contract = row.get("mapping_contract")
            if not isinstance(mapping_contract, dict):
                raise ValueError(f"selected catalog row lacks mapping_contract: {material_id}")
            mapping_profile_value = row.get("mapping_profile")
            if mapping_profile_value in (None, ""):
                mapping_profile_value = mapping_contract.get("mapping_profile")
            mapping_profile = str(mapping_profile_value).strip() if mapping_profile_value else None
            normal_space_value = row.get("normal_space")
            if normal_space_value in (None, ""):
                normal_space_value = mapping_contract.get("normal_space")
            normal_space = str(normal_space_value).strip() if normal_space_value else None
            requires_uv_value = row.get("requires_uv")
            if requires_uv_value is None:
                requires_uv_value = mapping_contract.get("requires_uv")
            if not isinstance(requires_uv_value, bool):
                raise ValueError(f"selected catalog row has invalid requires_uv: {material_id}")
            texture_size_value = row.get("texture_size_m")
            texture_size_m: float | None
            if texture_size_value is None:
                texture_size_m = None
            elif isinstance(texture_size_value, bool) or not isinstance(
                texture_size_value, (int, float)
            ):
                raise ValueError(f"selected catalog row has invalid texture_size_m: {material_id}")
            else:
                texture_size_m = float(texture_size_value)
                if texture_size_m <= 0:
                    raise ValueError(
                        f"selected catalog row has non-positive texture_size_m: {material_id}"
                    )
            provenance = row.get("provenance")
            if not isinstance(provenance, dict):
                raise ValueError(f"selected catalog row lacks provenance: {material_id}")
            packages.append(
                PackageSource(
                    material_id=material_id,
                    material_class_id=class_id,
                    category_slug=category,
                    blend_relative=blend_relative,
                    metadata_relative=metadata_relative,
                    blend_path=blend_path,
                    metadata_path=metadata_path,
                    expected_blend_sha256=expected_sha,
                    license=license_value,
                    provider=provider,
                    display_name=display_name,
                    material_profile=material_profile,
                    mapping_profile=mapping_profile,
                    texture_size_m=texture_size_m,
                    normal_space=normal_space,
                    requires_uv=requires_uv_value,
                    asset_base_id=str(row.get("asset_base_id") or material_id),
                    provenance=dict(provenance),
                )
            )
            found.add(material_id)
            license_counts[license_value] += 1
            provider_counts[provider] += 1
            subset_digest.update(raw)
    materials_file = source.manifest.get("materials_file")
    if not isinstance(materials_file, dict):
        raise ValueError("source catalog manifest lacks materials_file")
    if source_digest.hexdigest() != _require_sha(
        materials_file.get("sha256"), field="source catalog file SHA"
    ):
        raise ValueError("source normalized catalog file SHA mismatch")
    if materials_file.get("material_count") != len(all_ids):
        raise ValueError("source normalized catalog material count mismatch")
    missing = sorted(set(selected) - found)
    if missing:
        raise ValueError(f"runtime assignments missing from normalized catalog: {missing[:5]}")
    if len(packages) != len(selected):
        raise ValueError("published catalog is not an exact runtime-assigned subset")
    relative_paths = [
        relative
        for package in packages
        for relative in (package.blend_relative, package.metadata_relative)
    ]
    if len(relative_paths) != len(set(relative_paths)):
        raise ValueError("selected normalized packages have colliding paths")
    return packages, subset_digest.hexdigest(), license_counts, provider_counts


def _link_or_copy(source: Path, destination: Path) -> str:
    try:
        os.link(source, destination)
    except OSError as exc:
        if exc.errno != errno.EXDEV:
            raise
        shutil.copy2(source, destination)
        return "copy"
    source_stat = source.stat()
    destination_stat = destination.stat()
    if (
        source_stat.st_dev != destination_stat.st_dev
        or source_stat.st_ino != destination_stat.st_ino
    ):
        raise RuntimeError(f"hard-link identity verification failed: {destination}")
    return "hardlink"


def _publish_one_package(package: PackageSource, *, staging: Path) -> PackageResult:
    metadata_bytes = package.metadata_path.read_bytes()
    metadata_sha = _sha256_bytes(metadata_bytes)
    metadata = json.loads(metadata_bytes)
    if not isinstance(metadata, dict):
        raise ValueError(f"normalized metadata is not an object: {package.material_id}")
    metadata_package = metadata.get("package")
    metadata_source = metadata.get("source")
    if not isinstance(metadata_package, dict) or not isinstance(metadata_source, dict):
        raise ValueError(f"normalized metadata is incomplete: {package.material_id}")
    expected_metadata = {
        "material_id": package.material_id,
        "category_slug": package.category_slug,
        "package.blend_path": package.blend_relative,
        "package.blend_sha256": package.expected_blend_sha256,
        "source.license": package.license,
    }
    actual_metadata = {
        "material_id": metadata.get("material_id"),
        "category_slug": metadata.get("category_slug"),
        "package.blend_path": metadata_package.get("blend_path"),
        "package.blend_sha256": metadata_package.get("blend_sha256"),
        "source.license": metadata_source.get("license"),
    }
    if actual_metadata != expected_metadata:
        raise ValueError(f"catalog/package metadata mismatch: {package.material_id}")
    blend_sha = _sha256_file(package.blend_path)
    if blend_sha != package.expected_blend_sha256:
        raise ValueError(f"normalized blend SHA mismatch: {package.material_id}")

    destination_blend = _contained_join(
        staging,
        package.blend_relative,
        field=f"{package.material_id}.published blend",
        strict=False,
    )
    destination_metadata = _contained_join(
        staging,
        package.metadata_relative,
        field=f"{package.material_id}.published metadata",
        strict=False,
    )
    destination_blend.parent.mkdir(parents=True, exist_ok=True)
    blend_mode = _link_or_copy(package.blend_path, destination_blend)
    metadata_mode = _link_or_copy(package.metadata_path, destination_metadata)
    if blend_mode == "copy" and _sha256_file(destination_blend) != blend_sha:
        raise RuntimeError(f"copied blend verification failed: {package.material_id}")
    if metadata_mode == "copy" and _sha256_file(destination_metadata) != metadata_sha:
        raise RuntimeError(f"copied metadata verification failed: {package.material_id}")
    blend_size = package.blend_path.stat().st_size
    metadata_size = package.metadata_path.stat().st_size
    return PackageResult(
        runtime_record={
            "asset_base_id": package.asset_base_id,
            "material_id": package.material_id,
            "material_class_id": package.material_class_id,
            "category_slug": package.category_slug,
            "blend_path": package.blend_relative,
            "blend_sha256": blend_sha,
            "blend_size_bytes": blend_size,
            "metadata_path": package.metadata_relative,
            "metadata_sha256": metadata_sha,
            "metadata_size_bytes": metadata_size,
            "display_name": package.display_name,
            "license": package.license,
            "provider": package.provider,
            "material_profile": package.material_profile,
            "mapping_profile": package.mapping_profile,
            "texture_size_m": package.texture_size_m,
            "normal_space": package.normal_space,
            "requires_uv": package.requires_uv,
        },
        hardlinked_file_count=int(blend_mode == "hardlink") + int(metadata_mode == "hardlink"),
        copied_file_count=int(blend_mode == "copy") + int(metadata_mode == "copy"),
        package_bytes=blend_size + metadata_size,
    )


def _publish_packages(
    packages: Sequence[PackageSource],
    *,
    staging: Path,
    workers: int,
) -> tuple[list[dict[str, Any]], int, int, int]:
    results: list[PackageResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(_publish_one_package, package, staging=staging) for package in packages
        ]
        for completed, future in enumerate(concurrent.futures.as_completed(futures), 1):
            results.append(future.result())
            if completed % 500 == 0 or completed == len(futures):
                print(f"[publish] verified and staged {completed}/{len(futures)} packages")
    results.sort(key=lambda row: row.runtime_record["material_id"])
    return (
        [row.runtime_record for row in results],
        sum(row.hardlinked_file_count for row in results),
        sum(row.copied_file_count for row in results),
        sum(row.package_bytes for row in results),
    )


def _file_metadata(path: Path, *, root: Path, row_count: int | None = None) -> dict[str, Any]:
    value: dict[str, Any] = {
        "path": path.relative_to(root).as_posix(),
        "sha256": _sha256_file(path),
        "size_bytes": path.stat().st_size,
    }
    if row_count is not None:
        value["row_count"] = row_count
    return value


def _atomic_pointer(path: Path, value: object) -> None:
    payload = _canonical_json_bytes(value, pretty=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_base_appearance_input(
    manifest_path: Path,
    *,
    workspace_root: Path,
) -> BaseAppearanceInput:
    """Verify the v2 appearance baseline used by the annotation run.

    A manifest path is deliberately used instead of ``latest.json`` so a
    successful v3 migration cannot make a subsequent deterministic republish
    depend on the mutable current pointer. Production libraries do not need to
    retain this historical input; a republish caller must supply its archive.
    """

    workspace = workspace_root.resolve(strict=True)
    resolved_manifest = _contained(manifest_path, root=workspace, strict=True)
    if resolved_manifest.name != "manifest.json" or not resolved_manifest.is_file():
        raise ValueError("base appearance input must be an immutable v2 manifest.json")
    snapshot = resolved_manifest.parent.resolve(strict=True)
    manifest = _json_object(resolved_manifest)
    logical_sha = _require_sha(
        manifest.get("logical_snapshot_sha256"),
        field="base appearance logical snapshot SHA",
    )
    identity = manifest.get("identity")
    if (
        manifest.get("schema_version") != LEGACY_RELEASE_SCHEMA
        or manifest.get("publisher_version") != LEGACY_PUBLISHER_VERSION
        or manifest.get("logical_snapshot_sha256") != logical_sha
        or not isinstance(identity, dict)
        or identity.get("schema_version") != LEGACY_RELEASE_SCHEMA
        or identity.get("publisher_version") != LEGACY_PUBLISHER_VERSION
        or _canonical_json_sha256(identity) != logical_sha
    ):
        raise ValueError("base appearance manifest is not a content-addressed v2 release")
    files = manifest.get("files")
    receipt = files.get("pool_index") if isinstance(files, dict) else None
    if not isinstance(receipt, dict) or set(files) != {"pool_index"}:
        raise ValueError("base appearance manifest has invalid v2 control files")
    pool_index = _contained_regular_file(
        snapshot,
        receipt.get("path"),
        field="base appearance pool index",
    )
    if pool_index.parent.parent != snapshot:
        raise ValueError("base appearance pool index is outside its snapshot")
    pool_index_sha = _require_sha(receipt.get("sha256"), field="base pool index SHA")
    if (
        pool_index.stat().st_size != receipt.get("size_bytes")
        or _sha256_file(pool_index) != pool_index_sha
    ):
        raise ValueError("base appearance pool index receipt mismatch")
    pool_index_value = _json_object(pool_index)
    rows = pool_index_value.get("pools")
    if (
        pool_index_value.get("schema_version") != LEGACY_POOL_INDEX_SCHEMA
        or pool_index_value.get("policy_version") != POLICY_VERSION
        or pool_index_value.get("logical_snapshot_sha256") != logical_sha
        or pool_index_value.get("material_count") != identity.get("material_count")
        or pool_index_value.get("class_count") != identity.get("class_count")
        or not isinstance(rows, list)
        or len(rows) != identity.get("class_count")
    ):
        raise ValueError("base appearance pool index identity mismatch")

    material_records: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("base appearance pool index row is malformed")
        class_id = str(row.get("material_class_id") or "")
        pool_path = _contained_regular_file(
            snapshot,
            row.get("pool_path"),
            field=f"base appearance pool {class_id!r}",
        )
        if pool_path.stat().st_size != row.get("pool_size_bytes") or _sha256_file(
            pool_path
        ) != _require_sha(row.get("pool_sha256"), field="base pool SHA"):
            raise ValueError(f"base appearance pool receipt mismatch: {class_id}")
        pool = _json_object(pool_path)
        materials = pool.get("materials")
        if (
            pool.get("schema_version") != "articraft-material-class-pool/v2"
            or pool.get("policy_version") != POLICY_VERSION
            or pool.get("material_class_id") != class_id
            or pool.get("material_count") != row.get("material_count")
            or not isinstance(materials, list)
            or len(materials) != row.get("material_count")
        ):
            raise ValueError(f"base appearance pool document mismatch: {class_id}")
        for material in materials:
            if (
                not isinstance(material, dict)
                or set(material) != LEGACY_RUNTIME_MATERIAL_RECORD_FIELDS
            ):
                raise ValueError(f"base appearance material row is malformed: {class_id}")
            material_id = str(material.get("material_id") or "")
            if (
                not material_id
                or material_id in material_records
                or material.get("material_class_id") != class_id
            ):
                raise ValueError(f"base appearance material identity mismatch: {material_id}")
            material_records[material_id] = material
    if len(material_records) != identity.get("material_count"):
        raise ValueError("base appearance material count mismatch")
    return BaseAppearanceInput(
        snapshot_dir=snapshot,
        manifest_path=resolved_manifest,
        pool_index_path=pool_index,
        logical_snapshot_sha256=logical_sha,
        manifest_sha256=_sha256_file(resolved_manifest),
        pool_index_sha256=pool_index_sha,
        material_records=material_records,
    )


def load_physics_input(
    snapshot_dir: Path,
    *,
    workspace_root: Path,
    expected_material_ids: set[str],
    expected_formal_snapshot_sha256: str,
    expected_formal_manifest_sha256: str | None = None,
    expected_formal_pool_index_sha256: str | None = None,
) -> PhysicsInput:
    """Verify a completed annotation run and its exact material bijection."""

    workspace = workspace_root.resolve(strict=True)
    snapshot = _contained(snapshot_dir, root=workspace, strict=True)
    if not snapshot.is_dir():
        raise ValueError("physics annotation input must be a snapshot directory")
    paths = {
        name: _contained_regular_file(snapshot, name, field=f"physics {name}")
        for name in (
            "manifest.json",
            "run.json",
            "audit.json",
            "index.jsonl",
            "jobs.jsonl",
            "COMPLETE.json",
        )
    }
    manifest = _json_object(paths["manifest.json"])
    run = _json_object(paths["run.json"])
    audit = _json_object(paths["audit.json"])
    complete = _json_object(paths["COMPLETE.json"])
    for field, value in (
        ("manifest", manifest),
        ("run", run),
        ("audit", audit),
        ("COMPLETE", complete),
    ):
        if value.get("schema_version") != PHYSICS_RUN_SCHEMA:
            raise ValueError(f"physics {field} schema mismatch")
    if manifest.get("status") != "complete" or complete.get("status") != "complete":
        raise ValueError("physics annotation run is not complete")
    manifest_sha = _sha256_file(paths["manifest.json"])
    run_sha = _sha256_file(paths["run.json"])
    audit_sha = _sha256_file(paths["audit.json"])
    index_sha = _sha256_file(paths["index.jsonl"])
    jobs_sha = _sha256_file(paths["jobs.jsonl"])
    receipts = {
        "manifest_sha256": manifest_sha,
        "run_file_sha256": run_sha,
        "audit_sha256": audit_sha,
        "index_sha256": index_sha,
        "jobs_file_sha256": jobs_sha,
    }
    for field, actual in receipts.items():
        owner = complete if field == "manifest_sha256" else manifest
        if _require_sha(owner.get(field), field=f"physics {field}") != actual:
            raise ValueError(f"physics {field} mismatch")
    if (
        complete.get("run_file_sha256") != run_sha
        or complete.get("audit_sha256") != audit_sha
        or complete.get("index_sha256") != index_sha
        or complete.get("jobs_file_sha256") != jobs_sha
        or run.get("jobs_file_sha256") != jobs_sha
    ):
        raise ValueError("physics COMPLETE receipts disagree")
    expected_count = len(expected_material_ids)
    for field, value in (
        ("manifest", manifest),
        ("run", run),
        ("audit", audit),
        ("COMPLETE", complete),
    ):
        count_key = "expected_count" if field == "audit" else "material_count"
        if value.get(count_key) != expected_count:
            raise ValueError(f"physics {field} material count mismatch")
    if (
        audit.get("valid_count") != expected_count
        or audit.get("missing_count") != 0
        or audit.get("invalid_or_extra_count") != 0
        or audit.get("failures") != []
    ):
        raise ValueError("physics audit is not a complete valid bijection")
    if run.get("formal_snapshot_sha256") != expected_formal_snapshot_sha256:
        raise ValueError("physics run is bound to a different base appearance snapshot")
    if manifest.get("formal_snapshot_sha256") != expected_formal_snapshot_sha256:
        raise ValueError("physics manifest is bound to a different base appearance snapshot")
    if (
        expected_formal_manifest_sha256 is not None
        and run.get("formal_manifest_sha256") != expected_formal_manifest_sha256
    ):
        raise ValueError("physics run formal manifest provenance mismatch")
    if (
        expected_formal_pool_index_sha256 is not None
        and run.get("formal_pool_index_sha256") != expected_formal_pool_index_sha256
    ):
        raise ValueError("physics run formal pool index provenance mismatch")

    annotations: dict[str, dict[str, Any]] = {}
    annotation_sha256: dict[str, str] = {}
    seen_paths: set[str] = set()
    with paths["index.jsonl"].open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            row = json.loads(raw)
            if not isinstance(row, dict):
                raise ValueError(f"physics index line {line_number} is not an object")
            material_id = str(row.get("material_id") or "")
            if not material_id or material_id in annotations:
                raise ValueError(f"physics index repeats material_id at line {line_number}")
            record_relative = str(row.get("record_path") or "")
            if record_relative in seen_paths:
                raise ValueError("physics index repeats record_path")
            seen_paths.add(record_relative)
            record_path = _contained_regular_file(
                snapshot, record_relative, field=f"physics record line {line_number}"
            )
            record_sha = _require_sha(row.get("record_sha256"), field="physics record SHA")
            if _sha256_file(record_path) != record_sha:
                raise ValueError(f"physics record SHA mismatch: {material_id}")
            record = _json_object(record_path)
            if (
                record.get("schema_version") != PHYSICS_ANNOTATION_SCHEMA
                or record.get("material_id") != material_id
                or record.get("material_class_id") != row.get("material_class_id")
                or record.get("quality", {}).get("risk_tier") != row.get("risk_tier")
                or record.get("input", {}).get("formal_snapshot_sha256")
                != expected_formal_snapshot_sha256
            ):
                raise ValueError(f"physics annotation provenance mismatch: {material_id}")
            _validate_physics_annotation(record, material_id=material_id)
            annotations[material_id] = record
            annotation_sha256[material_id] = record_sha
    if set(annotations) != expected_material_ids:
        missing = sorted(expected_material_ids - set(annotations))
        extra = sorted(set(annotations) - expected_material_ids)
        raise ValueError(
            f"physics/material bijection mismatch: missing={missing[:3]} extra={extra[:3]}"
        )
    return PhysicsInput(
        snapshot_dir=snapshot,
        manifest=manifest,
        manifest_sha256=manifest_sha,
        run=run,
        run_sha256=run_sha,
        index_sha256=index_sha,
        audit_sha256=audit_sha,
        jobs_sha256=jobs_sha,
        annotations=annotations,
        annotation_sha256=annotation_sha256,
    )


def publish_library(
    *,
    catalog_pointer: Path,
    assignment_pointer: Path,
    registry_path: Path,
    physics_run: Path,
    base_appearance_manifest: Path,
    assignment_registry_path: Path | None = None,
    allowed_zero_assignment_class_removals: Sequence[str] = (),
    output_root: Path,
    workspace_root: Path,
    workers: int = 16,
    expected_material_count: int | None = None,
    expected_class_count: int | None = None,
    expected_nonempty_class_count: int | None = None,
    expected_empty_class_count: int | None = None,
) -> dict[str, Any]:
    if workers < 1:
        raise ValueError("workers must be positive")
    workspace = workspace_root.resolve(strict=True)
    catalog_source = load_catalog_input(catalog_pointer, workspace_root=workspace)
    assignment_source = load_assignment_input(assignment_pointer, workspace_root=workspace)
    _registry, registry_by_id, registry_sha, registry_file_sha = load_registry(
        registry_path,
        workspace_root=workspace,
    )
    if assignment_source.manifest.get("catalog_snapshot_sha256") != (
        catalog_source.manifest.get("logical_snapshot_sha256")
    ):
        raise ValueError("classification snapshot does not target the normalized catalog")
    source_registry_sha = _require_sha(
        assignment_source.manifest.get("registry_snapshot_sha256"),
        field="classification registry snapshot SHA",
    )
    registry_removal_audit: dict[str, Any] | None = None
    assignment_registry_file_sha: str | None = None
    if source_registry_sha == registry_sha:
        if assignment_registry_path is not None or allowed_zero_assignment_class_removals:
            raise ValueError("registry removal controls were supplied without registry drift")
        (
            selected,
            runtime_review_count,
            _source_class_counts,
            _decision_class_counts,
        ) = load_runtime_assignments(
            assignment_source,
            registry_by_id=registry_by_id,
        )
    else:
        # A migration may proceed without the historical registry document when
        # every class actually referenced by the frozen decisions still exists
        # in the target registry and no removal audit is requested.  The old
        # registry digest remains bound by the assignment snapshot.
        if assignment_registry_path is None and not allowed_zero_assignment_class_removals:
            (
                selected,
                runtime_review_count,
                _source_class_counts,
                _decision_class_counts,
            ) = load_runtime_assignments(
                assignment_source,
                registry_by_id=registry_by_id,
            )
            missing_target_classes = sorted(set(selected.values()) - set(registry_by_id))
            if missing_target_classes:
                raise ValueError(
                    f"runtime assignments use removed material classes: {missing_target_classes}"
                )
        elif assignment_registry_path is None:
            raise ValueError("classification registry drift requires the bound assignment registry")
        else:
            (
                _assignment_registry,
                assignment_registry_by_id,
                assignment_registry_sha,
                assignment_registry_file_sha,
            ) = load_registry(assignment_registry_path, workspace_root=workspace)
            if assignment_registry_sha != source_registry_sha:
                raise ValueError(
                    "assignment registry does not match the classification snapshot registry"
                )
            (
                selected,
                runtime_review_count,
                source_class_counts,
                decision_class_counts,
            ) = load_runtime_assignments(
                assignment_source,
                registry_by_id=assignment_registry_by_id,
            )
            registry_removal_audit = _audit_zero_assignment_class_removal(
                source_registry_by_id=assignment_registry_by_id,
                source_registry_sha256=assignment_registry_sha,
                target_registry_by_id=registry_by_id,
                target_registry_sha256=registry_sha,
                allowed_removals=allowed_zero_assignment_class_removals,
                source_class_counts=source_class_counts,
                decision_class_counts=decision_class_counts,
                assignment_snapshot_sha256=assignment_source.manifest["logical_snapshot_sha256"],
            )
            missing_target_classes = sorted(set(selected.values()) - set(registry_by_id))
            if missing_target_classes:
                raise ValueError(
                    f"runtime assignments use removed material classes: {missing_target_classes}"
                )
    if expected_material_count is not None and len(selected) != expected_material_count:
        raise ValueError(
            f"expected {expected_material_count} runtime assignments, found {len(selected)}"
        )
    if expected_class_count is not None and len(registry_by_id) != expected_class_count:
        raise ValueError(f"expected {expected_class_count} classes, found {len(registry_by_id)}")

    output_parent = _contained(output_root.parent, root=workspace, strict=True)
    output = _contained(output_parent / output_root.name, root=workspace, strict=False)
    output.mkdir(parents=True, exist_ok=True)
    lock_path = _contained(output / ".publish.lock", root=workspace, strict=False)
    with lock_path.open("a+b") as lock_handle:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        staging = Path(tempfile.mkdtemp(prefix=".publish-staging-", dir=output))
        staging = _contained(staging, root=workspace, strict=True)
        try:
            (
                packages,
                selected_catalog_rows_sha,
                license_counts,
                provider_counts,
            ) = _scan_subset_catalog(
                source=catalog_source,
                selected=selected,
                registry_by_id=registry_by_id,
            )
            source_raw = catalog_source.manifest.get("raw_catalog")
            if not isinstance(source_raw, dict):
                raise ValueError("normalized source manifest lacks raw catalog provenance")
            raw_catalog_sha = _require_sha(source_raw.get("sha256"), field="raw catalog SHA")
            native_allowlist_sha = _require_sha(
                catalog_source.manifest.get("native_runtime_allowlist_sha256"),
                field="native runtime allowlist SHA",
            )
            normalizer_version = str(catalog_source.manifest.get("normalizer_version") or "")
            if normalizer_version != NORMALIZER_VERSION:
                raise ValueError("unsupported source normalizer version")
            if catalog_source.manifest.get("runtime_profile_policy_version") != (
                RUNTIME_PROFILE_POLICY_VERSION
            ):
                raise ValueError("unsupported source runtime profile policy")
            source_catalog_logical_sha = _logical_catalog_sha(
                catalog_file_sha256=_require_sha(
                    catalog_source.manifest["materials_file"]["sha256"],
                    field="source catalog file SHA",
                ),
                raw_catalog_sha256=raw_catalog_sha,
                native_allowlist_sha256=native_allowlist_sha,
                normalizer_version=normalizer_version,
            )
            if source_catalog_logical_sha != catalog_source.manifest.get("logical_snapshot_sha256"):
                raise ValueError("source normalized catalog logical SHA mismatch")
            runtime_assignment_document = {
                "schema_version": RUNTIME_ASSIGNMENT_DIGEST_SCHEMA,
                "policy_version": POLICY_VERSION,
                "source_assignment_snapshot_sha256": assignment_source.manifest[
                    "logical_snapshot_sha256"
                ],
                "source_registry_snapshot_sha256": registry_sha,
                "assignments": [
                    {"material_id": material_id, "material_class_id": selected[material_id]}
                    for material_id in sorted(selected)
                ],
            }
            runtime_assignment_sha = _canonical_json_sha256(runtime_assignment_document)

            by_class_ids: dict[str, list[str]] = {
                class_id: [] for class_id in sorted(registry_by_id)
            }
            for material_id, class_id in selected.items():
                by_class_ids[class_id].append(material_id)
            for material_ids in by_class_ids.values():
                material_ids.sort()
            nonempty_count = sum(bool(material_ids) for material_ids in by_class_ids.values())
            empty_ids = [class_id for class_id, ids in by_class_ids.items() if not ids]
            if empty_ids:
                raise ValueError(
                    "formal PBR library v3 requires every material class pool to be non-empty: "
                    f"{empty_ids}"
                )
            if (
                expected_nonempty_class_count is not None
                and nonempty_count != expected_nonempty_class_count
            ):
                raise ValueError(
                    f"expected {expected_nonempty_class_count} nonempty classes, "
                    f"found {nonempty_count}"
                )
            if expected_empty_class_count is not None and len(empty_ids) != (
                expected_empty_class_count
            ):
                raise ValueError(
                    f"expected {expected_empty_class_count} empty classes, found {len(empty_ids)}"
                )

            base_appearance = load_base_appearance_input(
                base_appearance_manifest,
                workspace_root=workspace,
            )
            if set(base_appearance.material_records) != set(selected):
                missing = sorted(set(selected) - set(base_appearance.material_records))
                extra = sorted(set(base_appearance.material_records) - set(selected))
                raise ValueError(
                    "base appearance/runtime assignment bijection mismatch: "
                    f"missing={missing[:3]} extra={extra[:3]}"
                )
            for material_id, material_class_id in selected.items():
                if base_appearance.material_records[material_id].get("material_class_id") != (
                    material_class_id
                ):
                    raise ValueError(f"base appearance/class assignment mismatch: {material_id}")
            physics_source = load_physics_input(
                physics_run,
                workspace_root=workspace,
                expected_material_ids=set(selected),
                expected_formal_snapshot_sha256=(base_appearance.logical_snapshot_sha256),
                expected_formal_manifest_sha256=base_appearance.manifest_sha256,
                expected_formal_pool_index_sha256=base_appearance.pool_index_sha256,
            )

            runtime_records, hardlink_count, copy_count, package_bytes = _publish_packages(
                packages,
                staging=staging,
                workers=workers,
            )
            records_by_id = {str(record["material_id"]): record for record in runtime_records}
            if len(records_by_id) != len(runtime_records) or set(records_by_id) != set(selected):
                raise RuntimeError("published runtime records do not exactly cover assignments")
            for material_id, runtime_record in records_by_id.items():
                if runtime_record != base_appearance.material_records[material_id]:
                    raise ValueError(
                        f"runtime material differs from the physics-bound base appearance: "
                        f"{material_id}"
                    )
            physics_rows: list[dict[str, Any]] = []
            risk_tier_counts: collections.Counter[str] = collections.Counter()
            for material_id in sorted(records_by_id):
                annotation = physics_source.annotations[material_id]
                if annotation.get("material_class_id") != selected[material_id]:
                    raise ValueError(f"physics/class assignment mismatch: {material_id}")
                material_key = hashlib.sha256(material_id.encode("utf-8")).hexdigest()
                relative = Path("physics/by-id") / material_key[:2] / f"{material_key}.json"
                quality = annotation.get("quality")
                estimates = annotation.get("estimates")
                physics = annotation.get("physics")
                if (
                    not isinstance(quality, dict)
                    or not isinstance(estimates, dict)
                    or not isinstance(physics, dict)
                ):
                    raise ValueError(f"physics annotation payload is incomplete: {material_id}")
                risk_tier = str(quality.get("risk_tier") or "")
                if risk_tier not in {"low", "medium", "high"}:
                    raise ValueError(f"physics annotation risk tier is invalid: {material_id}")
                warnings = quality.get("warnings")
                if not isinstance(warnings, list) or any(
                    not isinstance(item, str) for item in warnings
                ):
                    raise ValueError(f"physics annotation warnings are invalid: {material_id}")
                sidecar = {
                    "schema_version": PHYSICS_SIDECAR_SCHEMA,
                    "material_id": material_id,
                    "material_class_id": selected[material_id],
                    "source_material_class_id": annotation["material_class_id"],
                    "reference_conditions_id": annotation["reference_conditions_id"],
                    "physics": physics,
                    "estimates": estimates,
                    "quality": {"risk_tier": risk_tier, "warnings": warnings},
                    "provenance": {
                        "annotation_record_sha256": physics_source.annotation_sha256[material_id],
                        "annotation_run_sha256": physics_source.run_sha256,
                        "annotation_manifest_sha256": physics_source.manifest_sha256,
                        "annotation_index_sha256": physics_source.index_sha256,
                        "annotation_model_run": annotation.get("model_run"),
                        "annotation_interpretation": annotation.get("interpretation"),
                        "source_input": annotation.get("input"),
                    },
                }
                sidecar_path = staging / relative
                sidecar_sha = _write_json(sidecar_path, sidecar)
                physics_ref = {
                    "schema_version": PHYSICS_REF_SCHEMA,
                    "path": relative.as_posix(),
                    "sha256": sidecar_sha,
                    "risk_tier": risk_tier,
                    "reference_conditions_id": annotation["reference_conditions_id"],
                }
                records_by_id[material_id]["physics_ref"] = physics_ref
                risk_tier_counts[risk_tier] += 1
                physics_rows.append({"material_id": material_id, **physics_ref})
            runtime_material_records_sha = _canonical_json_sha256(
                {
                    "schema_version": "articraft-pbr-runtime-material-record-set/v1",
                    "materials": runtime_records,
                }
            )
            runtime_physics_records_sha = _canonical_json_sha256(
                {
                    "schema_version": PHYSICS_INDEX_SCHEMA,
                    "annotation_run_sha256": physics_source.run_sha256,
                    "materials": physics_rows,
                }
            )

            by_class_records: dict[str, list[dict[str, Any]]] = {
                class_id: [] for class_id in sorted(registry_by_id)
            }
            for material_id in sorted(selected):
                by_class_records[selected[material_id]].append(records_by_id[material_id])

            identity = {
                "schema_version": RELEASE_SCHEMA,
                "publisher_version": PUBLISHER_VERSION,
                "source_normalized_catalog_snapshot_sha256": (
                    catalog_source.manifest["logical_snapshot_sha256"]
                ),
                "source_material_class_assignment_snapshot_sha256": (
                    assignment_source.manifest["logical_snapshot_sha256"]
                ),
                "source_registry_snapshot_sha256": registry_sha,
                "selected_catalog_rows_sha256": selected_catalog_rows_sha,
                "runtime_assignment_sha256": runtime_assignment_sha,
                "runtime_material_records_sha256": runtime_material_records_sha,
                "base_appearance_snapshot_sha256": (base_appearance.logical_snapshot_sha256),
                "physics_record_count": len(physics_rows),
                "runtime_physics_records_sha256": runtime_physics_records_sha,
                "source_physics_annotation_run_sha256": physics_source.run_sha256,
                "source_physics_annotation_manifest_sha256": physics_source.manifest_sha256,
                "source_physics_annotation_index_sha256": physics_source.index_sha256,
                "source_physics_annotation_audit_sha256": physics_source.audit_sha256,
                "source_physics_annotation_jobs_sha256": physics_source.jobs_sha256,
                "material_count": len(packages),
                "class_count": len(by_class_records),
            }
            if registry_removal_audit is not None:
                identity["registry_removal_audit_sha256"] = _canonical_json_sha256(
                    registry_removal_audit
                )
            release_sha = _canonical_json_sha256(identity)

            pool_rows: list[dict[str, Any]] = []
            for class_id, material_records in by_class_records.items():
                definition = registry_by_id[class_id]
                relative = Path("pools") / "by-class" / f"{class_id}.json"
                pool_path = staging / relative
                pool_document = {
                    "schema_version": POOL_SCHEMA,
                    "policy_version": POLICY_VERSION,
                    "material_class_id": class_id,
                    "parent_category": definition["parent_category"],
                    "material_count": len(material_records),
                    "materials": material_records,
                }
                pool_sha = _write_json(pool_path, pool_document)
                pool_rows.append(
                    {
                        "material_class_id": class_id,
                        "parent_category": definition["parent_category"],
                        "material_count": len(material_records),
                        "pool_path": relative.as_posix(),
                        "pool_sha256": pool_sha,
                        "pool_size_bytes": pool_path.stat().st_size,
                    }
                )
            pool_index = {
                "schema_version": POOL_INDEX_SCHEMA,
                "policy_version": POLICY_VERSION,
                "logical_snapshot_sha256": release_sha,
                "material_count": len(packages),
                "class_count": len(pool_rows),
                "nonempty_class_count": nonempty_count,
                "empty_class_count": 0,
                "pools": pool_rows,
            }
            pool_index_path = staging / "pools" / "index.json"
            pool_index_sha = _write_json(pool_index_path, pool_index)
            physics_index = {
                "schema_version": PHYSICS_INDEX_SCHEMA,
                "logical_snapshot_sha256": release_sha,
                "annotation_run_sha256": physics_source.run_sha256,
                "material_count": len(physics_rows),
                "risk_tier_counts": dict(sorted(risk_tier_counts.items())),
                "materials": physics_rows,
            }
            physics_index_path = staging / "physics" / "index.json"
            physics_index_sha = _write_json(physics_index_path, physics_index)
            controls = {
                "pool_index": {
                    **_file_metadata(pool_index_path, root=staging, row_count=len(pool_rows)),
                    "sha256": pool_index_sha,
                },
                "physics_index": {
                    **_file_metadata(physics_index_path, root=staging, row_count=len(physics_rows)),
                    "sha256": physics_index_sha,
                },
            }
            provenance = {
                "source_normalized_catalog": {
                    "workspace_path": _relative_to_workspace(
                        catalog_source.catalog_path, workspace
                    ),
                    "logical_snapshot_sha256": catalog_source.manifest["logical_snapshot_sha256"],
                    "manifest_sha256": catalog_source.manifest_sha256,
                },
                "source_material_class_assignments": {
                    "workspace_path": _relative_to_workspace(
                        assignment_source.snapshot_dir, workspace
                    ),
                    "logical_snapshot_sha256": assignment_source.manifest[
                        "logical_snapshot_sha256"
                    ],
                    "manifest_sha256": assignment_source.manifest_sha256,
                },
                "source_registry": {
                    "workspace_path": _relative_to_workspace(
                        _contained(registry_path, root=workspace, strict=True), workspace
                    ),
                    "file_sha256": registry_file_sha,
                    "logical_snapshot_sha256": registry_sha,
                },
                "source_physics_annotations": {
                    "workspace_path": _relative_to_workspace(
                        physics_source.snapshot_dir, workspace
                    ),
                    "run_sha256": physics_source.run_sha256,
                    "manifest_sha256": physics_source.manifest_sha256,
                    "index_sha256": physics_source.index_sha256,
                    "audit_sha256": physics_source.audit_sha256,
                    "jobs_sha256": physics_source.jobs_sha256,
                },
                "base_appearance_release": {
                    "workspace_path": _relative_to_workspace(
                        base_appearance.manifest_path, workspace
                    ),
                    "logical_snapshot_sha256": (base_appearance.logical_snapshot_sha256),
                    "manifest_sha256": base_appearance.manifest_sha256,
                    "pool_index_sha256": base_appearance.pool_index_sha256,
                },
            }
            if registry_removal_audit is not None:
                assert assignment_registry_path is not None
                assert assignment_registry_file_sha is not None
                provenance["source_assignment_registry"] = {
                    "workspace_path": _relative_to_workspace(
                        _contained(
                            assignment_registry_path,
                            root=workspace,
                            strict=True,
                        ),
                        workspace,
                    ),
                    "file_sha256": assignment_registry_file_sha,
                    "logical_snapshot_sha256": source_registry_sha,
                }
                provenance["registry_removal_audit"] = registry_removal_audit

            manifest = {
                "schema_version": RELEASE_SCHEMA,
                "publisher_version": PUBLISHER_VERSION,
                "logical_snapshot_sha256": release_sha,
                "identity": identity,
                "files": controls,
                "summary": {
                    "material_count": len(packages),
                    "package_file_count": len(packages) * 2,
                    "package_bytes": package_bytes,
                    "class_count": len(pool_rows),
                    "nonempty_class_count": nonempty_count,
                    "empty_class_count": len(empty_ids),
                    "empty_material_class_ids": empty_ids,
                    "excluded_runtime_review_material_count": runtime_review_count,
                    "license_counts": dict(sorted(license_counts.items())),
                    "provider_counts": dict(sorted(provider_counts.items())),
                    "physics_material_count": len(physics_rows),
                    "physics_risk_tier_counts": dict(sorted(risk_tier_counts.items())),
                },
                "provenance": provenance,
                "storage_policy": {
                    "package_files": "hardlink_same_filesystem_copy_only_on_exdev",
                    "runtime_lookup": "latest_to_pool_index_to_exact_class_pool",
                    "source_artifacts_deleted": False,
                },
            }
            manifest_path = staging / "manifest.json"
            manifest_sha = _write_json(manifest_path, manifest)

            snapshots = output / "snapshots"
            snapshots.mkdir(parents=True, exist_ok=True)
            destination = snapshots / release_sha
            published_new = not destination.exists()
            if published_new:
                os.replace(staging, destination)
            else:
                existing_manifest = destination / "manifest.json"
                if (
                    not existing_manifest.is_file()
                    or _sha256_file(existing_manifest) != manifest_sha
                ):
                    raise FileExistsError(f"immutable release collision: {destination}")
                shutil.rmtree(staging)
            pointer = output / "latest.json"
            pointer_value = {
                "schema_version": POINTER_SCHEMA,
                "logical_snapshot_sha256": release_sha,
                "snapshot_path": destination.relative_to(output).as_posix(),
                "manifest_path": (destination / "manifest.json").relative_to(output).as_posix(),
                "manifest_sha256": manifest_sha,
                "pool_index_path": (destination / controls["pool_index"]["path"])
                .relative_to(output)
                .as_posix(),
                "pool_index_sha256": pool_index_sha,
                "physics_index_path": (destination / controls["physics_index"]["path"])
                .relative_to(output)
                .as_posix(),
                "physics_index_sha256": physics_index_sha,
            }
            _atomic_pointer(pointer, pointer_value)
            return {
                "schema_version": "articraft-pbr-material-library-publication-result/v3",
                "output_root": output.as_posix(),
                "pointer_path": pointer.as_posix(),
                "snapshot_path": destination.as_posix(),
                "logical_snapshot_sha256": release_sha,
                "manifest_sha256": manifest_sha,
                "source_normalized_catalog_snapshot_sha256": catalog_source.manifest[
                    "logical_snapshot_sha256"
                ],
                "source_material_class_assignment_snapshot_sha256": (
                    assignment_source.manifest["logical_snapshot_sha256"]
                ),
                "source_registry_snapshot_sha256": registry_sha,
                "selected_catalog_rows_sha256": selected_catalog_rows_sha,
                "runtime_assignment_sha256": runtime_assignment_sha,
                "runtime_material_records_sha256": runtime_material_records_sha,
                "pool_index_sha256": pool_index_sha,
                "physics_index_sha256": physics_index_sha,
                "material_count": len(packages),
                "class_count": len(pool_rows),
                "nonempty_class_count": nonempty_count,
                "empty_class_count": len(empty_ids),
                "empty_material_class_ids": empty_ids,
                "package_file_count": len(packages) * 2,
                "package_bytes": package_bytes,
                "hardlinked_file_count": hardlink_count,
                "copied_file_count": copy_count,
                "published_new": published_new,
                "registry_removal_audit": registry_removal_audit,
                "validation": "source_full_hash_and_direct_pool_packages_verified",
            }
        finally:
            if staging.exists():
                shutil.rmtree(staging)


def _contained_regular_file(root: Path, value: object, *, field: str) -> Path:
    relative = _safe_relative(value, field=field)
    resolved_root = root.resolve(strict=True)
    lexical = resolved_root / relative
    cursor = resolved_root
    for part in relative.parts:
        cursor /= part
        if cursor.is_symlink():
            raise ValueError(f"{field} must not traverse a symlink: {value!r}")
    resolved = lexical.resolve(strict=True)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"{field} escapes {resolved_root}: {value!r}") from exc
    if not resolved.is_file():
        raise ValueError(f"{field} is not a regular file: {resolved}")
    return resolved


def _runtime_record_package_bytes(
    record: object,
    *,
    snapshot: Path,
    verify_hashes: bool,
) -> tuple[str, int]:
    if not isinstance(record, dict) or set(record) != RUNTIME_MATERIAL_RECORD_FIELDS:
        raise ValueError("formal pool runtime material record has invalid fields")
    material_id = str(record.get("material_id") or "").strip()
    if not material_id:
        raise ValueError("formal pool runtime material record lacks material_id")
    for field in (
        "asset_base_id",
        "material_class_id",
        "category_slug",
        "display_name",
        "license",
        "provider",
        "material_profile",
    ):
        if not str(record.get(field) or "").strip():
            raise ValueError(f"formal pool runtime material {material_id} lacks {field}")
    for field in ("mapping_profile", "normal_space"):
        value = record.get(field)
        if value is not None and not str(value).strip():
            raise ValueError(f"formal pool runtime material {material_id} has invalid {field}")
    texture_size = record.get("texture_size_m")
    if texture_size is not None and (
        isinstance(texture_size, bool)
        or not isinstance(texture_size, (int, float))
        or float(texture_size) <= 0
    ):
        raise ValueError(f"formal pool runtime material {material_id} has invalid texture_size_m")
    if not isinstance(record.get("requires_uv"), bool):
        raise ValueError(f"formal pool runtime material {material_id} has invalid requires_uv")

    package_paths: dict[str, Path] = {}
    package_bytes = 0
    for kind in ("blend", "metadata"):
        size = record.get(f"{kind}_size_bytes")
        if isinstance(size, bool) or not isinstance(size, int) or size < 1:
            raise ValueError(f"formal pool runtime material {material_id} has invalid {kind} size")
        expected_sha = _require_sha(
            record.get(f"{kind}_sha256"), field=f"runtime material {kind} SHA"
        )
        package_path = _contained_regular_file(
            snapshot,
            record.get(f"{kind}_path"),
            field=f"runtime material {kind}_path",
        )
        if package_path.stat().st_size != size:
            raise ValueError(f"formal package size mismatch: {package_path}")
        if verify_hashes and _sha256_file(package_path) != expected_sha:
            raise ValueError(f"formal package SHA mismatch: {package_path}")
        package_paths[kind] = package_path
        package_bytes += size
    if (
        package_paths["blend"].name != "material.blend"
        or package_paths["metadata"].name != "metadata.json"
        or package_paths["blend"].parent != package_paths["metadata"].parent
    ):
        raise ValueError(f"formal pool runtime material {material_id} has malformed package paths")
    return material_id, package_bytes


def validate_library(
    pointer_path: Path,
    *,
    workspace_root: Path,
    verify_package_hashes: bool = True,
) -> dict[str, Any]:
    workspace = workspace_root.resolve(strict=True)
    pointer = _contained(pointer_path, root=workspace, strict=True)
    pointer_value = _json_object(pointer)
    pointer_fields = {
        "schema_version",
        "logical_snapshot_sha256",
        "snapshot_path",
        "manifest_path",
        "manifest_sha256",
        "pool_index_path",
        "pool_index_sha256",
        "physics_index_path",
        "physics_index_sha256",
    }
    if (
        pointer_value.get("schema_version") != POINTER_SCHEMA
        or set(pointer_value) != pointer_fields
    ):
        raise ValueError("formal PBR library pointer schema mismatch")
    root = pointer.parent.resolve(strict=True)
    snapshot = _contained_join(
        root,
        pointer_value["snapshot_path"],
        field="library pointer snapshot_path",
        strict=True,
    )
    logical_sha = _require_sha(
        pointer_value["logical_snapshot_sha256"], field="pointer logical snapshot SHA"
    )
    if not snapshot.is_dir():
        raise ValueError("formal PBR library snapshot path is not a directory")
    manifest_path = _contained_regular_file(
        root,
        pointer_value["manifest_path"],
        field="library pointer manifest_path",
    )
    pool_index_path = _contained_regular_file(
        root,
        pointer_value["pool_index_path"],
        field="library pointer pool_index_path",
    )
    physics_index_path = _contained_regular_file(
        root,
        pointer_value["physics_index_path"],
        field="library pointer physics_index_path",
    )
    if (
        manifest_path.parent != snapshot
        or pool_index_path.parent.parent != snapshot
        or physics_index_path.parent.parent != snapshot
    ):
        raise ValueError("formal PBR library control files are outside the selected snapshot")
    manifest_sha = _sha256_file(manifest_path)
    if manifest_sha != _require_sha(pointer_value["manifest_sha256"], field="manifest SHA"):
        raise ValueError("formal PBR library manifest SHA mismatch")
    pool_index_sha = _sha256_file(pool_index_path)
    if pool_index_sha != _require_sha(pointer_value["pool_index_sha256"], field="pool index SHA"):
        raise ValueError("formal PBR library pool index SHA mismatch")
    physics_index_sha = _sha256_file(physics_index_path)
    if physics_index_sha != _require_sha(
        pointer_value["physics_index_sha256"], field="physics index SHA"
    ):
        raise ValueError("formal PBR library physics index SHA mismatch")

    manifest = _json_object(manifest_path)
    identity = manifest.get("identity")
    if manifest.get("schema_version") != RELEASE_SCHEMA or not isinstance(identity, dict):
        raise ValueError("formal PBR library release schema mismatch")
    if (
        _canonical_json_sha256(identity) != logical_sha
        or manifest.get("logical_snapshot_sha256") != logical_sha
    ):
        raise ValueError("formal PBR library content address mismatch")
    for field in (
        "source_normalized_catalog_snapshot_sha256",
        "source_material_class_assignment_snapshot_sha256",
        "source_registry_snapshot_sha256",
        "selected_catalog_rows_sha256",
        "runtime_assignment_sha256",
        "runtime_material_records_sha256",
        "base_appearance_snapshot_sha256",
        "runtime_physics_records_sha256",
        "source_physics_annotation_run_sha256",
        "source_physics_annotation_manifest_sha256",
        "source_physics_annotation_index_sha256",
        "source_physics_annotation_audit_sha256",
        "source_physics_annotation_jobs_sha256",
    ):
        _require_sha(identity.get(field), field=f"release identity {field}")
    if identity.get("physics_record_count") != identity.get("material_count"):
        raise ValueError("formal PBR library physics identity count mismatch")
    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != {"pool_index", "physics_index"}:
        raise ValueError("formal PBR library v3 manifest must publish pool and physics indexes")
    receipt = files["pool_index"]
    if not isinstance(receipt, dict):
        raise ValueError("formal PBR library pool index receipt is malformed")
    if (
        receipt.get("path") != pool_index_path.relative_to(snapshot).as_posix()
        or receipt.get("sha256") != pool_index_sha
        or receipt.get("size_bytes") != pool_index_path.stat().st_size
    ):
        raise ValueError("formal PBR library pool index receipt mismatch")
    physics_receipt = files["physics_index"]
    if (
        not isinstance(physics_receipt, dict)
        or physics_receipt.get("path") != physics_index_path.relative_to(snapshot).as_posix()
        or physics_receipt.get("sha256") != physics_index_sha
        or physics_receipt.get("size_bytes") != physics_index_path.stat().st_size
    ):
        raise ValueError("formal PBR library physics index receipt mismatch")

    pool_index = _json_object(pool_index_path)
    pool_index_fields = {
        "schema_version",
        "policy_version",
        "logical_snapshot_sha256",
        "material_count",
        "class_count",
        "nonempty_class_count",
        "empty_class_count",
        "pools",
    }
    pool_rows = pool_index.get("pools")
    if (
        pool_index.get("schema_version") != POOL_INDEX_SCHEMA
        or pool_index.get("policy_version") != POLICY_VERSION
        or set(pool_index) != pool_index_fields
        or pool_index.get("logical_snapshot_sha256") != logical_sha
        or not isinstance(pool_rows, list)
    ):
        raise ValueError("formal PBR library pool index schema mismatch")
    class_count = pool_index.get("class_count")
    material_count = pool_index.get("material_count")
    if (
        isinstance(class_count, bool)
        or not isinstance(class_count, int)
        or class_count < 1
        or isinstance(material_count, bool)
        or not isinstance(material_count, int)
        or material_count < 1
        or len(pool_rows) != class_count
        or pool_index.get("nonempty_class_count") != class_count
        or pool_index.get("empty_class_count") != 0
        or receipt.get("row_count") != class_count
    ):
        raise ValueError("formal PBR library v3 requires all indexed pools to be non-empty")

    expected_pool_row_fields = {
        "material_class_id",
        "parent_category",
        "material_count",
        "pool_path",
        "pool_sha256",
        "pool_size_bytes",
    }
    seen_class_ids: set[str] = set()
    seen_material_ids: set[str] = set()
    validated_runtime_records: list[dict[str, Any]] = []
    package_bytes = 0
    indexed_material_count = 0
    previous_class_id: str | None = None
    for row in pool_rows:
        if not isinstance(row, dict) or set(row) != expected_pool_row_fields:
            raise ValueError("formal PBR library pool index row is malformed")
        class_id = str(row.get("material_class_id") or "")
        parent_category = str(row.get("parent_category") or "")
        count = row.get("material_count")
        if (
            _CLASS_RE.fullmatch(class_id) is None
            or class_id.split(".", 1)[0] != parent_category
            or class_id in seen_class_ids
            or (previous_class_id is not None and class_id <= previous_class_id)
            or isinstance(count, bool)
            or not isinstance(count, int)
            or count < 1
        ):
            raise ValueError(f"formal PBR library has invalid class pool row: {class_id!r}")
        seen_class_ids.add(class_id)
        previous_class_id = class_id
        expected_relative = f"pools/by-class/{class_id}.json"
        if row.get("pool_path") != expected_relative:
            raise ValueError(f"formal PBR library pool path is not canonical: {class_id}")
        pool_path = _contained_regular_file(snapshot, expected_relative, field="class pool path")
        if pool_path.stat().st_size != row.get("pool_size_bytes"):
            raise ValueError(f"formal PBR library pool size mismatch: {class_id}")
        if _sha256_file(pool_path) != _require_sha(row.get("pool_sha256"), field="pool SHA"):
            raise ValueError(f"formal PBR library pool SHA mismatch: {class_id}")
        pool = _json_object(pool_path)
        pool_fields = {
            "schema_version",
            "policy_version",
            "material_class_id",
            "parent_category",
            "material_count",
            "materials",
        }
        materials = pool.get("materials")
        if (
            pool.get("schema_version") != POOL_SCHEMA
            or pool.get("policy_version") != POLICY_VERSION
            or set(pool) != pool_fields
            or pool.get("material_class_id") != class_id
            or pool.get("parent_category") != parent_category
            or pool.get("material_count") != count
            or not isinstance(materials, list)
            or len(materials) != count
        ):
            raise ValueError(f"formal PBR library pool document mismatch: {class_id}")
        material_ids: list[str] = []
        for material in materials:
            material_id, material_bytes = _runtime_record_package_bytes(
                material,
                snapshot=snapshot,
                verify_hashes=verify_package_hashes,
            )
            if (
                material.get("material_class_id") != class_id
                or material.get("category_slug") != parent_category
            ):
                raise ValueError(f"formal PBR library material/pool class mismatch: {material_id}")
            if material_id in seen_material_ids:
                raise ValueError(f"formal PBR library repeats material_id: {material_id}")
            seen_material_ids.add(material_id)
            material_ids.append(material_id)
            validated_runtime_records.append(material)
            package_bytes += material_bytes
        if material_ids != sorted(material_ids):
            raise ValueError(f"formal PBR library pool is not deterministically sorted: {class_id}")
        indexed_material_count += count
    if indexed_material_count != material_count:
        raise ValueError("formal PBR library pool material count mismatch")
    validated_runtime_records.sort(key=lambda record: str(record["material_id"]))
    runtime_material_records_sha = _canonical_json_sha256(
        {
            "schema_version": "articraft-pbr-runtime-material-record-set/v1",
            "materials": validated_runtime_records,
        }
    )
    if identity.get("runtime_material_records_sha256") != runtime_material_records_sha:
        raise ValueError("formal PBR library runtime material record digest mismatch")

    physics_index = _json_object(physics_index_path)
    physics_rows = physics_index.get("materials")
    expected_physics_index_fields = {
        "schema_version",
        "logical_snapshot_sha256",
        "annotation_run_sha256",
        "material_count",
        "risk_tier_counts",
        "materials",
    }
    if (
        physics_index.get("schema_version") != PHYSICS_INDEX_SCHEMA
        or set(physics_index) != expected_physics_index_fields
        or physics_index.get("logical_snapshot_sha256") != logical_sha
        or physics_index.get("annotation_run_sha256")
        != identity.get("source_physics_annotation_run_sha256")
        or physics_index.get("material_count") != material_count
        or not isinstance(physics_rows, list)
        or len(physics_rows) != material_count
    ):
        raise ValueError("formal PBR library physics index mismatch")
    physics_by_id: dict[str, dict[str, Any]] = {}
    risk_counts: collections.Counter[str] = collections.Counter()
    runtime_by_id = {
        str(material["material_id"]): material for material in validated_runtime_records
    }
    physics_ref_fields = {
        "schema_version",
        "path",
        "sha256",
        "risk_tier",
        "reference_conditions_id",
    }
    for row in physics_rows:
        if not isinstance(row, dict) or set(row) != {"material_id", *physics_ref_fields}:
            raise ValueError("formal PBR library physics index row is malformed")
        material_id = str(row.get("material_id") or "")
        if material_id in physics_by_id or material_id not in seen_material_ids:
            raise ValueError(f"formal PBR library physics index identity mismatch: {material_id}")
        expected_key = hashlib.sha256(material_id.encode("utf-8")).hexdigest()
        expected_path = f"physics/by-id/{expected_key[:2]}/{expected_key}.json"
        if row.get("schema_version") != PHYSICS_REF_SCHEMA or row.get("path") != expected_path:
            raise ValueError(f"formal PBR library physics path is not canonical: {material_id}")
        sidecar_path = _contained_regular_file(snapshot, expected_path, field="physics sidecar")
        if _sha256_file(sidecar_path) != _require_sha(row.get("sha256"), field="physics SHA"):
            raise ValueError(f"formal PBR library physics SHA mismatch: {material_id}")
        sidecar = _json_object(sidecar_path)
        risk_tier = str(row.get("risk_tier") or "")
        expected_sidecar_fields = {
            "schema_version",
            "material_id",
            "material_class_id",
            "source_material_class_id",
            "reference_conditions_id",
            "physics",
            "estimates",
            "quality",
            "provenance",
        }
        quality = sidecar.get("quality")
        provenance = sidecar.get("provenance")
        expected_provenance_fields = {
            "annotation_record_sha256",
            "annotation_run_sha256",
            "annotation_manifest_sha256",
            "annotation_index_sha256",
            "annotation_model_run",
            "annotation_interpretation",
            "source_input",
        }
        if (
            set(sidecar) != expected_sidecar_fields
            or sidecar.get("schema_version") != PHYSICS_SIDECAR_SCHEMA
            or sidecar.get("material_id") != material_id
            or sidecar.get("material_class_id")
            != runtime_by_id[material_id].get("material_class_id")
            or sidecar.get("source_material_class_id") != sidecar.get("material_class_id")
            or not isinstance(quality, dict)
            or set(quality) != {"risk_tier", "warnings"}
            or quality.get("risk_tier") != risk_tier
            or risk_tier not in {"low", "medium", "high"}
            or not isinstance(quality.get("warnings"), list)
            or any(not isinstance(item, str) for item in quality["warnings"])
            or sidecar.get("reference_conditions_id") != row.get("reference_conditions_id")
            or not str(sidecar.get("reference_conditions_id") or "").strip()
            or not isinstance(provenance, dict)
            or set(provenance) != expected_provenance_fields
            or provenance.get("annotation_run_sha256")
            != identity.get("source_physics_annotation_run_sha256")
            or provenance.get("annotation_manifest_sha256")
            != identity.get("source_physics_annotation_manifest_sha256")
            or provenance.get("annotation_index_sha256")
            != identity.get("source_physics_annotation_index_sha256")
            or not isinstance(provenance.get("source_input"), dict)
            or provenance["source_input"].get("formal_snapshot_sha256")
            != identity.get("base_appearance_snapshot_sha256")
        ):
            raise ValueError(f"formal PBR library physics sidecar mismatch: {material_id}")
        _require_sha(
            provenance.get("annotation_record_sha256"),
            field=f"physics annotation record SHA for {material_id}",
        )
        _validate_physics_annotation(sidecar, material_id=material_id)
        physics_by_id[material_id] = row
        risk_counts[risk_tier] += 1
    if set(physics_by_id) != seen_material_ids:
        raise ValueError("formal PBR library physics/material bijection mismatch")
    for material in validated_runtime_records:
        index_row = physics_by_id[str(material["material_id"])]
        if material.get("physics_ref") != {field: index_row[field] for field in physics_ref_fields}:
            raise ValueError("formal PBR library pool/physics descriptor mismatch")
    if physics_index.get("risk_tier_counts") != dict(sorted(risk_counts.items())):
        raise ValueError("formal PBR library physics risk counts mismatch")
    expected_runtime_physics_sha = _canonical_json_sha256(
        {
            "schema_version": PHYSICS_INDEX_SCHEMA,
            "annotation_run_sha256": physics_index["annotation_run_sha256"],
            "materials": physics_rows,
        }
    )
    if identity.get("runtime_physics_records_sha256") != expected_runtime_physics_sha:
        raise ValueError("formal PBR library runtime physics digest mismatch")

    summary = manifest.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("formal PBR library manifest lacks summary")
    expected_summary = {
        "material_count": material_count,
        "package_file_count": material_count * 2,
        "package_bytes": package_bytes,
        "class_count": class_count,
        "nonempty_class_count": class_count,
        "empty_class_count": 0,
        "physics_material_count": material_count,
    }
    for field, expected in expected_summary.items():
        if summary.get(field) != expected:
            raise ValueError(f"formal manifest summary {field} mismatch")

    audit_sha = identity.get("registry_removal_audit_sha256")
    if audit_sha is not None:
        provenance = manifest.get("provenance")
        audit = provenance.get("registry_removal_audit") if isinstance(provenance, dict) else None
        if not isinstance(audit, dict) or _canonical_json_sha256(audit) != _require_sha(
            audit_sha, field="registry removal audit SHA"
        ):
            raise ValueError("formal registry removal audit mismatch")
        if audit.get("schema_version") != REGISTRY_REMOVAL_AUDIT_SCHEMA or audit.get(
            "target_registry_snapshot_sha256"
        ) != identity.get("source_registry_snapshot_sha256"):
            raise ValueError("formal registry removal audit target mismatch")

    return {
        "schema_version": "articraft-pbr-material-library-validation/v3",
        "valid": True,
        "logical_snapshot_sha256": logical_sha,
        "manifest_sha256": manifest_sha,
        "pool_index_sha256": pool_index_sha,
        "physics_index_sha256": physics_index_sha,
        **expected_summary,
        "package_hashes_verified": verify_package_hashes,
    }


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def _nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be nonnegative")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    publish = subparsers.add_parser("publish", help="publish an immutable formal library")
    publish.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG_POINTER)
    publish.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENT_POINTER)
    publish.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    publish.add_argument(
        "--physics-run",
        type=Path,
        default=DEFAULT_PHYSICS_RUN,
        help="completed 8,295-record physics annotation snapshot",
    )
    publish.add_argument(
        "--base-appearance-manifest",
        type=Path,
        required=True,
        help=(
            "external archived v2 manifest.json bound by the physics run; not "
            "needed for normal runtime use"
        ),
    )
    publish.add_argument(
        "--assignment-registry",
        type=Path,
        help="registry snapshot bound by --assignments when auditing class removals",
    )
    publish.add_argument(
        "--allow-zero-assignment-class-removal",
        action="append",
        default=[],
        metavar="MATERIAL_CLASS_ID",
        help="explicitly allow one zero-reference class to be removed (repeatable)",
    )
    publish.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    publish.add_argument("--workers", type=_positive_int, default=16)
    publish.add_argument("--expect-material-count", type=_positive_int, default=8295)
    publish.add_argument("--expect-class-count", type=_positive_int, default=124)
    publish.add_argument("--expect-nonempty-class-count", type=_positive_int, default=124)
    publish.add_argument("--expect-empty-class-count", type=_nonnegative_int, default=0)

    validate = subparsers.add_parser("validate", help="validate a published formal library")
    validate.add_argument("--library", type=Path, default=DEFAULT_OUTPUT_ROOT / "latest.json")
    validate.add_argument(
        "--skip-package-hashes",
        action="store_true",
        help="validate sizes and containment without rereading every package payload",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "publish":
        result = publish_library(
            catalog_pointer=args.catalog,
            assignment_pointer=args.assignments,
            registry_path=args.registry,
            physics_run=args.physics_run,
            base_appearance_manifest=args.base_appearance_manifest,
            assignment_registry_path=args.assignment_registry,
            allowed_zero_assignment_class_removals=(args.allow_zero_assignment_class_removal),
            output_root=args.output_root,
            workspace_root=REPO_ROOT,
            workers=args.workers,
            expected_material_count=args.expect_material_count,
            expected_class_count=args.expect_class_count,
            expected_nonempty_class_count=args.expect_nonempty_class_count,
            expected_empty_class_count=args.expect_empty_class_count,
        )
    else:
        result = validate_library(
            args.library,
            workspace_root=REPO_ROOT,
            verify_package_hashes=not args.skip_package_hashes,
        )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
