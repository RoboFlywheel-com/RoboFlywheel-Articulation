# SPDX-License-Identifier: Apache-2.0

"""Fast runtime access to immutable material-class pools."""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any, Iterable

from .catalog import MaterialPhysics, MaterialPhysicsReference, MaterialRecord

POINTER_SCHEMA = "articraft-pbr-material-library-pointer/v3"
RELEASE_SCHEMA = "articraft-pbr-material-library-release/v3"
POOL_INDEX_SCHEMA = "articraft-material-class-pool-index/v3"
POOL_SCHEMA = "articraft-material-class-pool/v3"
PHYSICS_INDEX_SCHEMA = "articraft-pbr-material-physics-index/v1"
PHYSICS_SIDECAR_SCHEMA = "articraft-pbr-material-physics-sidecar/v1"
PHYSICS_REF_SCHEMA = "articraft-pbr-material-physics-ref/v1"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class LoadedMaterialPools:
    pointer_path: Path
    pointer_sha256: str
    snapshot_root: Path
    library_snapshot_sha256: str
    manifest_sha256: str
    pool_index_sha256: str
    physics_index_sha256: str
    physics_annotation_run_sha256: str
    pools: dict[str, tuple[MaterialRecord, ...]]
    pool_sha256: dict[str, str]

    def load_physics(self, material: MaterialRecord) -> MaterialPhysics:
        """Load and verify only the selected material's physics sidecar."""

        reference = material.physics_ref
        if reference is None:
            raise ValueError(f"material {material.material_id!r} has no physics reference")
        sidecar_path = _relative_path(
            self.snapshot_root,
            reference.path,
            field=f"material {material.material_id!r} physics path",
        )
        if _sha256(sidecar_path) != reference.sha256:
            raise ValueError(f"material {material.material_id!r} physics SHA mismatch")
        value = _json_object(sidecar_path, field=f"material {material.material_id!r} physics")
        if value.get("schema_version") != PHYSICS_SIDECAR_SCHEMA:
            raise ValueError(f"material {material.material_id!r} physics schema mismatch")
        if value.get("material_id") != material.material_id:
            raise ValueError(f"material {material.material_id!r} physics identity mismatch")
        if (
            value.get("material_class_id") != value.get("source_material_class_id")
            or value.get("material_class_id") != material.material_class_id
        ):
            raise ValueError(f"material {material.material_id!r} physics class provenance mismatch")
        quality = value.get("quality")
        if not isinstance(quality, dict) or quality.get("risk_tier") != reference.risk_tier:
            raise ValueError(f"material {material.material_id!r} physics risk mismatch")
        if value.get("reference_conditions_id") != reference.reference_conditions_id:
            raise ValueError(f"material {material.material_id!r} physics conditions mismatch")
        physics = value.get("physics")
        estimates = value.get("estimates")
        provenance = value.get("provenance")
        if not isinstance(physics, dict) or not isinstance(estimates, dict) or not isinstance(
            provenance, dict
        ):
            raise ValueError(f"material {material.material_id!r} physics payload is incomplete")
        fields = (
            "density_kg_m3",
            "youngs_modulus_pa",
            "poissons_ratio",
            "static_friction_coefficient",
            "dynamic_friction_coefficient",
            "restitution_coefficient",
        )
        values: dict[str, float] = {}
        for field in fields:
            try:
                values[field] = float(physics[field])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"material {material.material_id!r} physics {field} is invalid"
                ) from exc
            number = values[field]
            if not math.isfinite(number):
                raise ValueError(f"material {material.material_id!r} physics {field} is not finite")
            if field in {"density_kg_m3", "youngs_modulus_pa"} and number <= 0:
                raise ValueError(f"material {material.material_id!r} physics {field} is not positive")
            if field == "poissons_ratio" and not 0.0 <= number < 0.5:
                raise ValueError(f"material {material.material_id!r} Poisson ratio is out of range")
            if field in {"static_friction_coefficient", "dynamic_friction_coefficient"} and number < 0:
                raise ValueError(f"material {material.material_id!r} friction is negative")
            if field == "restitution_coefficient" and not 0.0 <= number <= 1.0:
                raise ValueError(f"material {material.material_id!r} restitution is out of range")
            estimate = estimates.get(field)
            required_estimate_fields = {
                "low", "value", "high", "confidence", "applicability", "basis"
            }
            if not isinstance(estimate, dict) or set(estimate) != required_estimate_fields:
                raise ValueError(f"material {material.material_id!r} {field} estimate is malformed")
            try:
                low, point, high, confidence = (
                    float(estimate[key]) for key in ("low", "value", "high", "confidence")
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"material {material.material_id!r} {field} estimate is invalid") from exc
            if (
                not all(math.isfinite(item) for item in (low, point, high, confidence))
                or not low <= point <= high
                or point != number
                or not 0.0 <= confidence <= 1.0
                or estimate["applicability"] not in {
                    "native", "effective_proxy", "not_physically_native"
                }
                or not str(estimate["basis"] or "").strip()
            ):
                raise ValueError(f"material {material.material_id!r} {field} estimate is inconsistent")
        if values["static_friction_coefficient"] < values["dynamic_friction_coefficient"]:
            raise ValueError(f"material {material.material_id!r} static friction is below dynamic")
        warnings = quality.get("warnings")
        if not isinstance(warnings, list) or any(not isinstance(item, str) for item in warnings):
            raise ValueError(f"material {material.material_id!r} physics warnings are invalid")
        return MaterialPhysics(
            material_id=material.material_id,
            material_class_id=str(value["material_class_id"]),
            risk_tier=reference.risk_tier,
            warnings=tuple(warnings),
            reference_conditions_id=reference.reference_conditions_id,
            estimates=estimates,
            provenance=provenance,
            **values,
        )


def load_material_physics(
    library: LoadedMaterialPools,
    material: MaterialRecord,
) -> MaterialPhysics:
    """Public lazy loader used after deterministic material selection."""

    return library.load_physics(material)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_object(path: Path, *, field: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {field} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a JSON object: {path}")
    return value


def _sha(value: object, *, field: str) -> str:
    text = str(value or "")
    if _SHA256_RE.fullmatch(text) is None:
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return text


def _relative_path(root: Path, value: object, *, field: str, must_exist: bool = True) -> Path:
    text = str(value or "").strip()
    relative = Path(text)
    windows = PureWindowsPath(text)
    if (
        not text
        or "\\" in text
        or relative.is_absolute()
        or windows.is_absolute()
        or bool(windows.drive)
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise ValueError(f"{field} must be a contained POSIX relative path")
    candidate = root / relative
    if must_exist:
        resolved = candidate.resolve(strict=True)
        try:
            resolved.relative_to(root.resolve(strict=True))
        except ValueError as exc:
            raise ValueError(f"{field} escapes the formal library snapshot") from exc
        return resolved
    return candidate.absolute()


def _required_text(value: object, *, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} must be a non-empty string")
    return text


def _optional_text(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None


def _material_record(
    row: object,
    *,
    snapshot_root: Path,
    material_class_id: str,
) -> MaterialRecord:
    if not isinstance(row, dict):
        raise ValueError(f"pool {material_class_id!r} material row must be an object")
    required = {
        "asset_base_id",
        "blend_path",
        "blend_sha256",
        "blend_size_bytes",
        "category_slug",
        "display_name",
        "license",
        "mapping_profile",
        "material_class_id",
        "material_id",
        "material_profile",
        "metadata_path",
        "metadata_sha256",
        "metadata_size_bytes",
        "normal_space",
        "provider",
        "requires_uv",
        "texture_size_m",
        "physics_ref",
    }
    if set(row) != required:
        raise ValueError(f"pool {material_class_id!r} material row fields do not match v3")
    row_class = _required_text(row["material_class_id"], field="material_class_id")
    if row_class != material_class_id:
        raise ValueError(f"pool {material_class_id!r} contains a different material class")
    category = _required_text(row["category_slug"], field="category_slug")
    if category != material_class_id.split(".", 1)[0]:
        raise ValueError(f"pool {material_class_id!r} crosses parent category")
    for size_field in ("blend_size_bytes", "metadata_size_bytes"):
        value = row[size_field]
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"{size_field} must be a positive integer")
    requires_uv = row["requires_uv"]
    if not isinstance(requires_uv, bool):
        raise ValueError("requires_uv must be boolean")
    texture_size = row["texture_size_m"]
    if texture_size is not None:
        texture_size = float(texture_size)
        if texture_size <= 0.0:
            raise ValueError("texture_size_m must be positive")
    blend_path = _relative_path(
        snapshot_root,
        row["blend_path"],
        field="blend_path",
        must_exist=False,
    )
    _relative_path(
        snapshot_root,
        row["metadata_path"],
        field="metadata_path",
        must_exist=False,
    )
    _sha(row["metadata_sha256"], field="metadata_sha256")
    physics_ref = row["physics_ref"]
    expected_physics_ref_fields = {
        "schema_version",
        "path",
        "sha256",
        "risk_tier",
        "reference_conditions_id",
    }
    if not isinstance(physics_ref, dict) or set(physics_ref) != expected_physics_ref_fields:
        raise ValueError(f"pool {material_class_id!r} material physics_ref is malformed")
    if physics_ref.get("schema_version") != PHYSICS_REF_SCHEMA:
        raise ValueError(f"pool {material_class_id!r} material physics_ref schema mismatch")
    physics_path = str(physics_ref.get("path") or "")
    _relative_path(snapshot_root, physics_path, field="physics_ref.path", must_exist=False)
    risk_tier = _required_text(physics_ref.get("risk_tier"), field="physics_ref.risk_tier")
    if risk_tier not in {"low", "medium", "high"}:
        raise ValueError("physics_ref.risk_tier must be low, medium, or high")
    reference_conditions_id = _required_text(
        physics_ref.get("reference_conditions_id"),
        field="physics_ref.reference_conditions_id",
    )
    return MaterialRecord(
        material_id=_required_text(row["material_id"], field="material_id"),
        category_slug=category,
        blend_path=blend_path,
        sha256=_sha(row["blend_sha256"], field="blend_sha256"),
        license=_required_text(row["license"], field="license"),
        provider=_required_text(row["provider"], field="provider"),
        asset_base_id=_required_text(row["asset_base_id"], field="asset_base_id"),
        display_name=_required_text(row["display_name"], field="display_name"),
        material_profile=_required_text(row["material_profile"], field="material_profile"),
        texture_size_m=texture_size,
        active=True,
        runtime_enabled=True,
        generic_eligible=True,
        mapping_profile=_optional_text(row["mapping_profile"]),
        normal_space=_optional_text(row["normal_space"]),
        requires_uv=requires_uv,
        displacement_policy="disconnect_true_displacement",
        validation_status="published",
        selection_scope="exact_pool",
        material_class_id=material_class_id,
        physics_ref=MaterialPhysicsReference(
            path=physics_path,
            sha256=_sha(physics_ref.get("sha256"), field="physics_ref.sha256"),
            risk_tier=risk_tier,
            reference_conditions_id=reference_conditions_id,
        ),
    )


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_material_pools(
    pointer_path: Path,
    material_class_ids: Iterable[str],
) -> LoadedMaterialPools:
    """Load only requested v3 pools; packages and physics sidecars remain lazy."""

    requested = tuple(sorted(set(material_class_ids)))
    if any(not material_class_id for material_class_id in requested):
        raise ValueError("requested material_class_ids must be non-empty")
    if pointer_path.name != "latest.json" or pointer_path.is_symlink():
        raise ValueError("formal material library input must be a regular latest.json")
    pointer = pointer_path.resolve(strict=True)
    library_root = pointer.parent.resolve(strict=True)
    value = _json_object(pointer, field="formal material library pointer")
    if value.get("schema_version") != POINTER_SCHEMA:
        raise ValueError("formal material library pointer schema mismatch")
    logical_sha256 = _sha(value.get("logical_snapshot_sha256"), field="snapshot SHA")
    snapshot_root = _relative_path(
        library_root,
        value.get("snapshot_path"),
        field="snapshot_path",
    )
    if not snapshot_root.is_dir():
        raise ValueError("formal material library snapshot path is not a directory")

    manifest_path = _relative_path(
        library_root,
        value.get("manifest_path"),
        field="manifest_path",
    )
    if manifest_path.parent != snapshot_root:
        raise ValueError("formal material library manifest is outside its snapshot")
    manifest_sha256 = _sha(value.get("manifest_sha256"), field="manifest_sha256")
    if _sha256(manifest_path) != manifest_sha256:
        raise ValueError("formal material library manifest SHA mismatch")
    manifest = _json_object(manifest_path, field="formal material library manifest")
    if manifest.get("schema_version") != RELEASE_SCHEMA:
        raise ValueError("formal material library release schema mismatch")
    identity = manifest.get("identity")
    if (
        not isinstance(identity, dict)
        or _canonical_sha256(identity) != logical_sha256
        or manifest.get("logical_snapshot_sha256") != logical_sha256
    ):
        raise ValueError("formal material library manifest content address mismatch")

    files = manifest.get("files")
    pool_receipt = files.get("pool_index") if isinstance(files, dict) else None
    if not isinstance(pool_receipt, dict):
        raise ValueError("formal material library manifest lacks pool_index")
    physics_receipt = files.get("physics_index") if isinstance(files, dict) else None
    if not isinstance(physics_receipt, dict):
        raise ValueError("formal material library manifest lacks physics_index")
    physics_index_path = _relative_path(
        snapshot_root,
        physics_receipt.get("path"),
        field="manifest physics_index path",
    )
    physics_index_sha256 = _sha(
        physics_receipt.get("sha256"), field="manifest physics_index SHA"
    )
    if _sha256(physics_index_path) != physics_index_sha256:
        raise ValueError("formal material library physics index SHA mismatch")
    physics_index = _json_object(physics_index_path, field="formal material physics index")
    if (
        physics_index.get("schema_version") != PHYSICS_INDEX_SCHEMA
        or physics_index.get("logical_snapshot_sha256") != logical_sha256
    ):
        raise ValueError("formal material library physics index schema mismatch")
    physics_annotation_run_sha256 = _sha(
        physics_index.get("annotation_run_sha256"), field="physics annotation run SHA"
    )
    pointer_physics_index = _relative_path(
        library_root,
        value.get("physics_index_path"),
        field="pointer physics_index_path",
    )
    if pointer_physics_index != physics_index_path:
        raise ValueError("formal material library physics index paths disagree")
    if _sha(value.get("physics_index_sha256"), field="pointer physics index SHA") != (
        physics_index_sha256
    ):
        raise ValueError("formal material library physics index SHAs disagree")
    pool_index_path = _relative_path(
        snapshot_root,
        pool_receipt.get("path"),
        field="manifest pool_index path",
    )
    pointer_pool_index = _relative_path(
        library_root,
        value.get("pool_index_path"),
        field="pointer pool_index_path",
    )
    if pointer_pool_index != pool_index_path:
        raise ValueError("formal material library pool index paths disagree")
    pool_index_sha256 = _sha(
        pool_receipt.get("sha256"),
        field="manifest pool_index SHA",
    )
    if _sha(value.get("pool_index_sha256"), field="pointer pool_index SHA") != pool_index_sha256:
        raise ValueError("formal material library pool index SHAs disagree")
    if _sha256(pool_index_path) != pool_index_sha256:
        raise ValueError("formal material library pool index SHA mismatch")
    pool_index = _json_object(pool_index_path, field="formal material pool index")
    if pool_index.get("schema_version") != POOL_INDEX_SCHEMA:
        raise ValueError("formal material pool index schema mismatch")
    if pool_index.get("logical_snapshot_sha256") != logical_sha256:
        raise ValueError("formal material pool index snapshot mismatch")
    if pool_index.get("empty_class_count") != 0:
        raise ValueError("formal material pool index contains empty classes")
    rows = pool_index.get("pools")
    if not isinstance(rows, list) or not rows:
        raise ValueError("formal material pool index has no pools")
    entries: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"formal material pool index row {index} is invalid")
        material_class_id = _required_text(
            row.get("material_class_id"),
            field=f"pools[{index}].material_class_id",
        )
        if material_class_id in entries:
            raise ValueError(f"formal material pool index repeats {material_class_id!r}")
        count = row.get("material_count")
        if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            raise ValueError(f"formal material pool {material_class_id!r} must be non-empty")
        entries[material_class_id] = row
    if pool_index.get("class_count") != len(entries):
        raise ValueError("formal material pool index class count mismatch")

    missing = sorted(set(requested) - set(entries))
    if missing:
        raise ValueError(f"formal material library has no pool {missing[0]!r}")
    pools: dict[str, tuple[MaterialRecord, ...]] = {}
    pool_hashes: dict[str, str] = {}
    for material_class_id in requested:
        entry = entries[material_class_id]
        pool_path = _relative_path(
            snapshot_root,
            entry.get("pool_path"),
            field=f"pool {material_class_id!r} path",
        )
        expected_sha = _sha(entry.get("pool_sha256"), field=f"pool {material_class_id!r} SHA")
        if _sha256(pool_path) != expected_sha:
            raise ValueError(f"formal material pool {material_class_id!r} SHA mismatch")
        document = _json_object(pool_path, field=f"formal material pool {material_class_id!r}")
        if document.get("schema_version") != POOL_SCHEMA:
            raise ValueError(f"formal material pool {material_class_id!r} schema mismatch")
        if document.get("material_class_id") != material_class_id:
            raise ValueError(f"formal material pool {material_class_id!r} identity mismatch")
        material_rows = document.get("materials")
        if not isinstance(material_rows, list) or not material_rows:
            raise ValueError(f"formal material pool {material_class_id!r} is empty")
        records = tuple(
            _material_record(
                row,
                snapshot_root=snapshot_root,
                material_class_id=material_class_id,
            )
            for row in material_rows
        )
        if document.get("material_count") != len(records) or entry.get("material_count") != len(
            records
        ):
            raise ValueError(f"formal material pool {material_class_id!r} count mismatch")
        if tuple(sorted(records, key=lambda row: row.material_id)) != records:
            raise ValueError(f"formal material pool {material_class_id!r} is not canonical")
        if len({record.material_id for record in records}) != len(records):
            raise ValueError(f"formal material pool {material_class_id!r} repeats material IDs")
        pools[material_class_id] = records
        pool_hashes[material_class_id] = expected_sha

    return LoadedMaterialPools(
        pointer_path=pointer,
        pointer_sha256=_sha256(pointer),
        snapshot_root=snapshot_root,
        library_snapshot_sha256=logical_sha256,
        manifest_sha256=manifest_sha256,
        pool_index_sha256=pool_index_sha256,
        physics_index_sha256=physics_index_sha256,
        physics_annotation_run_sha256=physics_annotation_run_sha256,
        pools=pools,
        pool_sha256=pool_hashes,
    )
