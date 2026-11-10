# SPDX-License-Identifier: Apache-2.0

"""Read the normalized, provider-aware material catalog used by seed builds."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from .normalized import (
    MATERIAL_PROFILES,
    NORMALIZED_CATALOG_MANIFEST_SCHEMA,
    NORMALIZED_CATALOG_SCHEMA,
    NORMALIZED_PACKAGE_SCHEMA,
    NORMALIZER_VERSION,
    RUNTIME_PROFILE_POLICY_VERSION,
    contained_file,
    logical_catalog_snapshot_sha256,
    safe_relative_path,
)


def _text(value: object, *, field: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ValueError(f"catalog row has no {field}")
    return result


def _nested(row: dict[str, Any], *paths: tuple[str, ...]) -> object | None:
    for path in paths:
        value: object = row
        for key in path:
            if not isinstance(value, dict) or key not in value:
                break
            value = value[key]
        else:
            if value not in (None, ""):
                return value
    return None


def _tokens(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        values = value.replace(",", " ").split()
    elif isinstance(value, (list, tuple)):
        values = [str(item) for item in value]
    else:
        values = []
    return tuple(sorted({item.strip().lower() for item in values if item.strip()}))


def _string_items(value: object) -> tuple[str, ...]:
    if isinstance(value, dict):
        values = value.keys()
    elif isinstance(value, str):
        values = value.replace(",", " ").split()
    elif isinstance(value, (list, tuple, set, frozenset)):
        values = value
    else:
        values = ()
    return tuple(sorted({str(item).strip() for item in values if str(item).strip()}))


def _optional_text(value: object) -> str | None:
    result = str(value or "").strip()
    return result or None


def _optional_positive_float(value: object, *, field: str) -> float | None:
    if value in (None, ""):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"catalog {field} must be a positive finite number") from exc
    if not (0.0 < result < float("inf")):
        raise ValueError(f"catalog {field} must be a positive finite number")
    return result


def _optional_bool(value: object, *, field: str) -> bool | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in {"true", "yes", "1", "active", "pass", "passed"}:
            return True
        if normalized in {"false", "no", "0", "inactive", "fail", "failed"}:
            return False
    raise ValueError(f"catalog {field} must be a boolean")


def _material_profile(row: dict[str, Any]) -> str:
    explicit = _optional_text(
        _nested(
            row,
            ("material_profile",),
            ("normalization", "material_profile"),
            ("metadata", "material_profile"),
        )
    )
    if explicit is not None:
        profile = explicit.casefold()
        if profile not in MATERIAL_PROFILES:
            raise ValueError(f"catalog has unsupported material_profile: {explicit!r}")
        return profile

    # Raw BlenderKit catalogs predate the normalized schema.  Their provider
    # metadata is enough to preserve the intended two-profile classification.
    procedural = _nested(row, ("source", "parameters", "procedural"), ("parameters", "procedural"))
    if procedural is True:
        return "native_procedural"
    return "texture_set"


def _record_active(row: dict[str, Any]) -> bool:
    value = _nested(
        row,
        ("active",),
        ("validation", "active"),
        ("retrieval", "active"),
        ("eligible_for_generic",),
        ("eligibility", "eligible_for_generic"),
    )
    parsed = _optional_bool(value, field="active")
    return True if parsed is None else parsed


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_snapshot_manifest(
    source_path: Path,
    *,
    root: Path,
    strict_normalized: bool,
) -> dict[str, Any] | None:
    manifest_path = source_path.with_name("manifest.json")
    relative_parts = source_path.relative_to(root).parts
    is_snapshot_path = (
        len(relative_parts) == 3
        and relative_parts[0] == "catalogs"
        and re.fullmatch(r"[0-9a-f]{64}", relative_parts[1]) is not None
        and relative_parts[2] == "materials.jsonl"
    )
    if not manifest_path.is_file():
        if strict_normalized and is_snapshot_path:
            raise ValueError(
                f"immutable normalized catalog snapshot lacks manifest: {manifest_path}"
            )
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid normalized catalog manifest: {manifest_path}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError(f"normalized catalog manifest is not an object: {manifest_path}")
    if manifest.get("schema_version") != NORMALIZED_CATALOG_MANIFEST_SCHEMA:
        raise ValueError(f"unsupported normalized catalog manifest schema: {manifest_path}")
    materials = manifest.get("materials_file")
    raw_catalog = manifest.get("raw_catalog")
    if not isinstance(materials, dict) or not isinstance(raw_catalog, dict):
        raise ValueError(f"normalized catalog manifest lacks file/raw provenance: {manifest_path}")
    catalog_sha = str(materials.get("sha256") or "")
    raw_sha = str(raw_catalog.get("sha256") or "")
    allowlist_sha = str(manifest.get("native_runtime_allowlist_sha256") or "")
    logical_sha = str(manifest.get("logical_snapshot_sha256") or "")
    if materials.get("path") != "materials.jsonl" or catalog_sha != _sha256(source_path):
        raise ValueError(
            f"normalized catalog manifest materials file SHA mismatch: {manifest_path}"
        )
    material_count = sum(
        bool(line.strip()) for line in source_path.read_text(encoding="utf-8").splitlines()
    )
    if materials.get("material_count") != material_count:
        raise ValueError(f"normalized catalog manifest material count mismatch: {manifest_path}")
    if manifest.get("normalizer_version") != NORMALIZER_VERSION:
        raise ValueError(
            f"normalized catalog manifest normalizer version mismatch: {manifest_path}"
        )
    if manifest.get("runtime_profile_policy_version") != RUNTIME_PROFILE_POLICY_VERSION:
        raise ValueError(f"normalized catalog manifest runtime policy mismatch: {manifest_path}")
    expected_logical_sha = logical_catalog_snapshot_sha256(
        catalog_file_sha256=catalog_sha,
        raw_catalog_sha256=raw_sha,
        native_allowlist_sha256=allowlist_sha,
        normalizer_version=NORMALIZER_VERSION,
    )
    if logical_sha != expected_logical_sha:
        raise ValueError(f"normalized catalog logical snapshot SHA mismatch: {manifest_path}")
    if is_snapshot_path and relative_parts[1] != logical_sha:
        raise ValueError("normalized catalog directory does not match logical snapshot SHA")
    return manifest


_TILE_SIZE_MISSING_REASON = "texture set has no trustworthy real-world tile size"
_TILE_SIZE_MISSING_RESTRICTIONS = [
    "requires_metric_uv",
    "tangent_space_normal",
    "tile_size_missing",
    "true_displacement_disabled",
]


def _require_tile_size_missing_quarantine(
    row: dict[str, Any],
    *,
    material_id: str,
) -> None:
    """Validate the sole strict texture-set exception to a positive tile size."""

    eligibility = row.get("eligibility")
    validation = row.get("validation")
    runtime_profile = row.get("runtime_profile")
    node_qa = row.get("node_qa")
    if not all(
        isinstance(value, dict) for value in (eligibility, validation, runtime_profile, node_qa)
    ):
        raise ValueError(
            f"normalized catalog {material_id} has an incomplete tile_size_missing quarantine"
        )
    assert isinstance(eligibility, dict)
    assert isinstance(validation, dict)
    assert isinstance(runtime_profile, dict)
    assert isinstance(node_qa, dict)
    issues = node_qa.get("issues")
    has_missing_tile_warning = isinstance(issues, list) and any(
        isinstance(issue, dict)
        and issue.get("code") == "texture_size_m_missing"
        and issue.get("severity") == "warning"
        for issue in issues
    )
    expected_validation = {
        "active": False,
        "reasons": [_TILE_SIZE_MISSING_REASON],
        "status": "quarantined",
    }
    consistent = (
        "texture_size_m" in row
        and row.get("texture_size_m") is None
        and row.get("normalization_class") == "quarantine"
        and row.get("active") is False
        and row.get("runtime_enabled") is False
        and row.get("eligible_for_generic") is False
        and row.get("selection_scope") == "quarantined"
        and row.get("quarantine_reason") == _TILE_SIZE_MISSING_REASON
        and row.get("restrictions") == _TILE_SIZE_MISSING_RESTRICTIONS
        and validation == expected_validation
        and eligibility.get("active") is False
        and eligibility.get("eligible_for_generic") is False
        and eligibility.get("selection_scope") == "quarantined"
        and eligibility.get("quarantine_reason") == _TILE_SIZE_MISSING_REASON
        and eligibility.get("restrictions") == _TILE_SIZE_MISSING_RESTRICTIONS
        and eligibility.get("validation") == expected_validation
        and runtime_profile.get("enabled") is False
        and runtime_profile.get("native_allowlisted") is False
        and runtime_profile.get("policy_version") == RUNTIME_PROFILE_POLICY_VERSION
        and runtime_profile.get("reason") == "technical_qa_inactive"
        and node_qa.get("status") == "warn"
        and has_missing_tile_warning
    )
    if not consistent:
        raise ValueError(
            f"normalized catalog {material_id} has an inconsistent tile_size_missing quarantine"
        )


def _require_mapping_contract(
    row: dict[str, Any],
    *,
    material_id: str,
    material_profile: str,
) -> dict[str, Any]:
    mapping = row.get("mapping_contract")
    if not isinstance(mapping, dict):
        raise ValueError(f"normalized catalog {material_id} has no mapping_contract")
    expected = (
        {
            "mapping_profile": "metric_uv_tangent",
            "normal_space": "tangent",
            "requires_uv": True,
        }
        if material_profile == "texture_set"
        else {
            "mapping_profile": "native_node_graph",
            "normal_space": "native",
            "requires_uv": False,
        }
    )
    for field, expected_value in expected.items():
        if mapping.get(field) != expected_value:
            raise ValueError(
                f"normalized catalog {material_id} mapping_contract.{field} "
                f"must be {expected_value!r}"
            )
    for field, expected_value in {
        "coordinate_unit": "meter",
        "generic_box_projection_allowed": False,
        "model_uvs_are_not_baked": True,
    }.items():
        if mapping.get(field) != expected_value:
            raise ValueError(
                f"normalized catalog {material_id} mapping_contract.{field} "
                f"must be {expected_value!r}"
            )
    if material_profile == "texture_set":
        mapping_tile_value = mapping.get("tile_size_m")
        declared_tile_value = row.get("texture_size_m")
        if mapping_tile_value is None or declared_tile_value is None:
            if (
                "tile_size_m" not in mapping
                or mapping_tile_value is not None
                or declared_tile_value is not None
            ):
                raise ValueError(
                    f"normalized catalog {material_id} texture_set requires one consistent "
                    "positive texture_size_m or an explicit tile_size_missing quarantine"
                )
            _require_tile_size_missing_quarantine(row, material_id=material_id)
            return mapping
        tile_size = _optional_positive_float(
            mapping_tile_value,
            field=f"{material_id}.mapping_contract.tile_size_m",
        )
        declared_size = _optional_positive_float(
            declared_tile_value,
            field=f"{material_id}.texture_size_m",
        )
        if tile_size is None or declared_size is None or tile_size != declared_size:
            raise ValueError(
                f"normalized catalog {material_id} texture_set requires one consistent "
                "positive texture_size_m"
            )
    return mapping


def _validate_strict_normalized_row(
    row: dict[str, Any],
    *,
    line_number: int,
    root: Path,
) -> None:
    """Reject raw/partial rows before they can enter a canary retrieval pool."""

    schema = row.get("schema_version")
    if schema != NORMALIZED_CATALOG_SCHEMA:
        raise ValueError(
            f"catalog row {line_number} is not a normalized material row: "
            f"expected schema_version {NORMALIZED_CATALOG_SCHEMA!r}, got {schema!r}"
        )
    material_id = _text(row.get("material_id"), field="material_id")
    category = _text(row.get("category_slug"), field="category_slug")
    version = _text(row.get("normalization_version"), field="normalization_version")
    if version != NORMALIZER_VERSION:
        raise ValueError(
            f"normalized catalog {material_id} uses unsupported normalization_version "
            f"{version!r}; expected {NORMALIZER_VERSION!r}"
        )
    profile_text = _text(row.get("material_profile"), field="material_profile").casefold()
    if profile_text not in MATERIAL_PROFILES:
        raise ValueError(
            f"normalized catalog {material_id} has unsupported material_profile: {profile_text!r}"
        )
    mapping = _require_mapping_contract(
        row,
        material_id=material_id,
        material_profile=profile_text,
    )

    relative = safe_relative_path(
        row.get("normalized_blend_path"),
        field=f"{material_id}.normalized_blend_path",
    )
    expected_prefix = ("packages", category)
    content_parts = relative.parts[2:-1]
    if (
        relative.parts[:2] != expected_prefix
        or relative.name != "material.blend"
        or len(content_parts) != 2
        or any(re.fullmatch(r"[0-9a-f]{16}", part) is None for part in content_parts)
    ):
        raise ValueError(
            f"normalized catalog {material_id} package must be a content-addressed "
            f"packages/{category}/.../material.blend path"
        )
    metadata_relative = safe_relative_path(
        row.get("normalized_metadata_path"),
        field=f"{material_id}.normalized_metadata_path",
    )
    if metadata_relative.parent != relative.parent or metadata_relative.name != "metadata.json":
        raise ValueError(
            f"normalized catalog {material_id} metadata must be metadata.json beside material.blend"
        )
    metadata_path = contained_file(
        root,
        metadata_relative.as_posix(),
        field=f"{material_id}.normalized_metadata_path",
    )
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"normalized metadata for {material_id} is invalid JSON: {exc}") from exc
    if (
        not isinstance(metadata, dict)
        or metadata.get("schema_version") != NORMALIZED_PACKAGE_SCHEMA
    ):
        raise ValueError(
            f"normalized metadata for {material_id} must use schema_version "
            f"{NORMALIZED_PACKAGE_SCHEMA!r}"
        )
    metadata_package = metadata.get("package")
    metadata_normalizer = metadata.get("normalizer")
    if not isinstance(metadata_package, dict) or not isinstance(metadata_normalizer, dict):
        raise ValueError(f"normalized metadata for {material_id} is missing package/normalizer")

    expected_sha = str(row.get("sha256") or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        raise ValueError(f"normalized catalog {material_id} requires a lowercase SHA-256")
    consistency_checks = {
        "material_id": (metadata.get("material_id"), material_id),
        "category_slug": (metadata.get("category_slug"), category),
        "material_profile": (metadata.get("material_profile"), profile_text),
        "mapping_contract": (metadata.get("mapping_contract"), mapping),
        "package.blend_path": (metadata_package.get("blend_path"), relative.as_posix()),
        "package.blend_sha256": (metadata_package.get("blend_sha256"), expected_sha),
        "normalizer.version": (metadata_normalizer.get("version"), version),
    }
    for field, (actual, expected) in consistency_checks.items():
        if actual != expected:
            raise ValueError(
                f"normalized catalog/metadata mismatch for {material_id} {field}: "
                f"{actual!r} != {expected!r}"
            )
    if profile_text == "texture_set" and row.get("texture_size_m") is None:
        if (
            metadata.get("texture_size_m") is not None
            or metadata.get("texture_size_source") is not None
            or metadata.get("normalization_class") != "quarantine"
        ):
            raise ValueError(
                f"normalized catalog/metadata mismatch for {material_id} "
                "tile_size_missing quarantine"
            )

    displacement = row.get("displacement_policy")
    if not isinstance(displacement, dict) or displacement.get("policy") != (
        "disconnect_true_displacement"
    ):
        raise ValueError(f"normalized catalog {material_id} must disconnect true displacement")
    if metadata.get("displacement_policy") != displacement:
        raise ValueError(
            f"normalized catalog/metadata mismatch for {material_id} displacement_policy"
        )

    active = row.get("active")
    validation = row.get("validation")
    eligibility = row.get("eligibility")
    node_qa = row.get("node_qa")
    channels = row.get("channels")
    channel_qa = row.get("channel_qa")
    if not isinstance(active, bool):
        raise ValueError(f"normalized catalog {material_id} active must be a boolean")
    if not isinstance(validation, dict) or not isinstance(eligibility, dict):
        raise ValueError(f"normalized catalog {material_id} lacks validation/eligibility QA")
    if not isinstance(node_qa, dict) or node_qa.get("status") not in {"pass", "warn", "fail"}:
        raise ValueError(f"normalized catalog {material_id} has invalid node_qa status")
    if not isinstance(channels, list) or not isinstance(channel_qa, dict):
        raise ValueError(f"normalized catalog {material_id} lacks channel QA")
    if channel_qa.get("channels") != channels:
        raise ValueError(f"normalized catalog {material_id} channel QA is inconsistent")
    if validation.get("active") is not active or eligibility.get("active") is not active:
        raise ValueError(f"normalized catalog {material_id} active/QA flags are inconsistent")
    expected_status = "active" if active else "quarantined"
    if validation.get("status") != expected_status:
        raise ValueError(
            f"normalized catalog {material_id} validation.status must be {expected_status!r}"
        )
    generic_eligible = row.get("eligible_for_generic")
    if not isinstance(generic_eligible, bool):
        raise ValueError(f"normalized catalog {material_id} eligible_for_generic must be a boolean")
    if eligibility.get("eligible_for_generic") is not generic_eligible:
        raise ValueError(f"normalized catalog {material_id} eligible_for_generic is inconsistent")
    quarantine_reason = row.get("quarantine_reason")
    selection_scope = row.get("selection_scope")
    if selection_scope != eligibility.get("selection_scope"):
        raise ValueError(f"normalized catalog {material_id} selection_scope is inconsistent")
    valid_scopes = (
        {"generic"}
        if generic_eligible
        else {
            "semantic_restricted",
            "role_restricted",
            "quarantined",
        }
    )
    if selection_scope not in valid_scopes:
        raise ValueError(
            f"normalized catalog {material_id} selection_scope {selection_scope!r} is invalid"
        )
    if not active and (generic_eligible or selection_scope != "quarantined"):
        raise ValueError(
            f"normalized catalog {material_id} technical inactive row must be quarantined"
        )
    if active and selection_scope == "quarantined":
        raise ValueError(f"normalized catalog {material_id} active row cannot be quarantined")
    if row.get("restrictions") != eligibility.get("restrictions"):
        raise ValueError(f"normalized catalog {material_id} restrictions are inconsistent")
    if row.get("quarantine_reason") != eligibility.get("quarantine_reason"):
        raise ValueError(f"normalized catalog {material_id} quarantine_reason is inconsistent")
    if row.get("semantic_risk_reason") != eligibility.get("semantic_risk_reason"):
        raise ValueError(f"normalized catalog {material_id} semantic risk is inconsistent")
    if active and (node_qa.get("status") == "fail" or quarantine_reason not in (None, "")):
        raise ValueError(f"normalized catalog {material_id} active row failed QA/quarantine")
    if not active and not str(quarantine_reason or "").strip():
        raise ValueError(f"normalized catalog {material_id} inactive row lacks quarantine_reason")
    if metadata.get("eligibility") != eligibility or metadata.get("node_qa") != node_qa:
        raise ValueError(f"normalized catalog/metadata QA mismatch for {material_id}")

    runtime_enabled = row.get("runtime_enabled")
    runtime_profile = row.get("runtime_profile")
    if not isinstance(runtime_enabled, bool) or not isinstance(runtime_profile, dict):
        raise ValueError(f"normalized catalog {material_id} lacks runtime qualification")
    if runtime_profile.get("enabled") is not runtime_enabled:
        raise ValueError(f"normalized catalog {material_id} runtime_enabled is inconsistent")
    if runtime_profile.get("policy_version") != RUNTIME_PROFILE_POLICY_VERSION:
        raise ValueError(f"normalized catalog {material_id} runtime policy version is invalid")
    native_allowlisted = runtime_profile.get("native_allowlisted")
    if not isinstance(native_allowlisted, bool):
        raise ValueError(f"normalized catalog {material_id} native allowlist flag is invalid")
    qa_pass = active and node_qa.get("status") == "pass"
    expected_runtime_enabled = qa_pass and (
        profile_text == "texture_set"
        or (profile_text == "native_procedural" and native_allowlisted)
    )
    if runtime_enabled is not expected_runtime_enabled:
        raise ValueError(
            f"normalized catalog {material_id} runtime qualification contradicts profile/QA"
        )


@dataclass(frozen=True, slots=True)
class MaterialPhysicsReference:
    """Content-addressed reference to one lazily loaded physics sidecar."""

    path: str
    sha256: str
    risk_tier: str
    reference_conditions_id: str
    schema_version: str = "articraft-pbr-material-physics-ref/v1"

    def canonical_row(self) -> dict[str, str]:
        return {
            "schema_version": self.schema_version,
            "path": self.path,
            "sha256": self.sha256,
            "risk_tier": self.risk_tier,
            "reference_conditions_id": self.reference_conditions_id,
        }


@dataclass(frozen=True, slots=True)
class MaterialPhysics:
    """Verified physics proxy loaded from a formal-library sidecar."""

    material_id: str
    material_class_id: str
    density_kg_m3: float
    youngs_modulus_pa: float
    poissons_ratio: float
    static_friction_coefficient: float
    dynamic_friction_coefficient: float
    restitution_coefficient: float
    risk_tier: str
    warnings: tuple[str, ...]
    reference_conditions_id: str
    estimates: Mapping[str, Any]
    provenance: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class MaterialRecord:
    """One downloadable Blender material package in the logical library."""

    material_id: str
    category_slug: str
    blend_path: Path
    sha256: str
    license: str
    provider: str
    asset_base_id: str
    display_name: str
    tags: tuple[str, ...] = ()
    source_category_slug: str | None = None
    source_description: str | None = None
    material_profile: str = "texture_set"
    texture_size_m: float | None = None
    active: bool = True
    runtime_enabled: bool = True
    runtime_profile_reason: str | None = None
    native_runtime_allowlisted: bool = False
    generic_eligible: bool = True
    restrictions: tuple[str, ...] = ()
    quarantine_reason: str | None = None
    normalization_version: str | None = None
    channels: tuple[str, ...] = ()
    mapping_profile: str | None = None
    normal_space: str | None = None
    requires_uv: bool | None = None
    displacement_policy: str | None = None
    validation_status: str | None = None
    selection_scope: str | None = None
    semantic_risk_reason: str | None = None
    material_class_id: str | None = None
    physics_ref: MaterialPhysicsReference | None = None

    @property
    def eligible_for_generic(self) -> bool:
        """Whether this technically active package is safe for a generic surface pool."""

        return self.generic_eligible

    @property
    def search_tokens(self) -> frozenset[str]:
        text = " ".join((self.display_name, *self.tags)).lower()
        normalized = "".join(char if char.isalnum() else " " for char in text)
        return frozenset(normalized.split())

    def canonical_row(self, *, library_root: Path) -> dict[str, Any]:
        return {
            "asset_base_id": self.asset_base_id,
            "blend_path": self.blend_path.relative_to(library_root).as_posix(),
            "category_slug": self.category_slug,
            "display_name": self.display_name,
            "license": self.license,
            "active": self.active,
            "runtime_enabled": self.runtime_enabled,
            "runtime_profile_reason": self.runtime_profile_reason,
            "native_runtime_allowlisted": self.native_runtime_allowlisted,
            "eligible_for_generic": self.generic_eligible,
            "channels": list(self.channels),
            "displacement_policy": self.displacement_policy,
            "material_id": self.material_id,
            "material_profile": self.material_profile,
            "material_class_id": self.material_class_id,
            "mapping_profile": self.mapping_profile,
            "normal_space": self.normal_space,
            "normalization_version": self.normalization_version,
            "provider": self.provider,
            "quarantine_reason": self.quarantine_reason,
            "requires_uv": self.requires_uv,
            "restrictions": list(self.restrictions),
            "selection_scope": self.selection_scope,
            "semantic_risk_reason": self.semantic_risk_reason,
            "sha256": self.sha256,
            "source_category_slug": self.source_category_slug,
            "tags": list(self.tags),
            "texture_size_m": self.texture_size_m,
            "validation_status": self.validation_status,
            "physics_ref": (
                None if self.physics_ref is None else self.physics_ref.canonical_row()
            ),
        }


@dataclass(frozen=True, slots=True)
class MaterialCatalog:
    """Immutable catalog snapshot with verified package paths and hashes."""

    records: tuple[MaterialRecord, ...]
    library_root: Path
    snapshot_sha256: str
    source_path: Path
    schema_version: str | None = None
    normalization_version: str | None = None
    strict_normalized: bool = False
    manifest_path: Path | None = None
    catalog_file_sha256: str | None = None
    raw_catalog_sha256: str | None = None
    native_runtime_allowlist_sha256: str | None = None

    def by_category(self, category_slug: str) -> tuple[MaterialRecord, ...]:
        return tuple(record for record in self.records if record.category_slug == category_slug)

    @classmethod
    def from_jsonl(
        cls,
        path: Path,
        *,
        library_root: Path | None = None,
        verify_hashes: bool = True,
        strict_normalized: bool = False,
    ) -> MaterialCatalog:
        """Load a catalog, optionally enforcing the normalized-library contract.

        ``strict_normalized=True`` is the production seed-build boundary.  The
        default remains available for explicit legacy/downloader tooling; it
        must not be used by canary or dataset seed generation.
        """

        source_path = path.resolve(strict=True)
        inferred_root = source_path.parent.parent
        if source_path.parent.parent.name == "catalogs":
            inferred_root = source_path.parents[2]
        root = (library_root or inferred_root).resolve(strict=True)
        try:
            source_path.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"catalog is outside its library root: {source_path}") from exc
        manifest = _load_snapshot_manifest(
            source_path,
            root=root,
            strict_normalized=strict_normalized,
        )

        records: list[MaterialRecord] = []
        seen_ids: set[str] = set()
        for line_number, raw in enumerate(source_path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            row = json.loads(raw)
            if not isinstance(row, dict):
                raise ValueError(f"catalog row {line_number} is not an object")
            if strict_normalized:
                _validate_strict_normalized_row(
                    row,
                    line_number=line_number,
                    root=root,
                )
            material_id = _text(
                _nested(
                    row,
                    ("material_id",),
                    ("package_id",),
                    ("source", "asset_base_id"),
                ),
                field="material_id",
            )
            if material_id in seen_ids:
                raise ValueError(f"duplicate material_id in catalog: {material_id}")
            seen_ids.add(material_id)
            category = _text(
                _nested(
                    row,
                    ("category_slug",),
                    ("requested_category_slug",),
                    ("profile", "category_slug"),
                    ("category",),
                ),
                field="category_slug",
            )
            relative = (
                _text(row.get("normalized_blend_path"), field="normalized_blend_path")
                if strict_normalized
                else _text(
                    _nested(
                        row,
                        ("package_blend_path",),
                        ("normalized_blend_path",),
                        ("relative_path",),
                        ("selected_file", "relative_path"),
                    ),
                    field="blend path",
                )
            )
            blend_path = (root / relative).resolve(strict=True)
            try:
                blend_path.relative_to(root)
            except ValueError as exc:
                raise ValueError(f"catalog package escapes library root: {relative}") from exc
            expected_sha = str(
                _nested(
                    row,
                    ("sha256",),
                    ("download_sha256",),
                    ("validation", "sha256"),
                    ("selected_file", "sha256"),
                )
                or ""
            ).strip()
            must_verify_hash = verify_hashes or strict_normalized
            actual_sha = (
                _sha256(blend_path) if must_verify_hash or not expected_sha else expected_sha
            )
            if expected_sha and must_verify_hash and expected_sha != actual_sha:
                raise ValueError(
                    f"catalog hash mismatch for {material_id}: {expected_sha} != {actual_sha}"
                )
            source = row.get("source") if isinstance(row.get("source"), dict) else {}
            material_profile = _material_profile(row)
            texture_size_value = (
                row.get("texture_size_m")
                if strict_normalized
                else _nested(
                    row,
                    ("texture_size_m",),
                    ("mapping_contract", "tile_size_m"),
                    ("normalization", "texture_size_m"),
                    ("source", "parameters", "textureSizeMeters"),
                    ("parameters", "textureSizeMeters"),
                )
            )
            texture_size = _optional_positive_float(
                texture_size_value,
                field="texture_size_m",
            )
            mapping_profile = _optional_text(
                _nested(
                    row,
                    ("mapping_profile",),
                    ("mapping_contract", "mapping_profile"),
                )
            )
            requires_uv = _optional_bool(
                _nested(row, ("requires_uv",), ("mapping_contract", "requires_uv")),
                field="requires_uv",
            )
            eligibility = row.get("eligibility")
            eligibility = eligibility if isinstance(eligibility, dict) else {}
            displacement = row.get("displacement_policy")
            if isinstance(displacement, dict):
                displacement_policy = _optional_text(displacement.get("policy"))
            else:
                displacement_policy = _optional_text(displacement)
            channel_qa = row.get("channel_qa")
            channel_qa = channel_qa if isinstance(channel_qa, dict) else {}
            validation = row.get("validation")
            validation = validation if isinstance(validation, dict) else {}
            tags = _tokens(row.get("tags") or source.get("tags") or ())
            active = _record_active(row)
            runtime_profile = row.get("runtime_profile")
            runtime_profile = runtime_profile if isinstance(runtime_profile, dict) else {}
            runtime_enabled = _optional_bool(
                row.get("runtime_enabled"),
                field="runtime_enabled",
            )
            if runtime_enabled is None:
                # Legacy catalogs have no signed native allowlist.  Texture
                # sets retain their historical active behavior, while native
                # procedural packages stay out of runtime until migrated into
                # an explicit snapshot policy.
                runtime_enabled = active and material_profile == "texture_set"
            native_runtime_allowlisted = _optional_bool(
                runtime_profile.get("native_allowlisted"),
                field="runtime_profile.native_allowlisted",
            )
            records.append(
                MaterialRecord(
                    material_id=material_id,
                    category_slug=category,
                    blend_path=blend_path,
                    sha256=actual_sha,
                    license=_text(
                        _nested(row, ("license",), ("source", "license")) or "unknown",
                        field="license",
                    ),
                    provider=str(row.get("provider") or "blenderkit"),
                    asset_base_id=str(
                        row.get("asset_base_id") or source.get("asset_base_id") or material_id
                    ),
                    display_name=str(
                        row.get("display_name")
                        or row.get("name")
                        or source.get("display_name")
                        or material_id
                    ),
                    tags=tags,
                    source_category_slug=(
                        str(source.get("category")) if source.get("category") else None
                    ),
                    source_description=(
                        str(source.get("description")) if source.get("description") else None
                    ),
                    material_profile=material_profile,
                    texture_size_m=texture_size,
                    active=active,
                    runtime_enabled=runtime_enabled,
                    runtime_profile_reason=(
                        _optional_text(runtime_profile.get("reason"))
                        or (
                            "legacy_texture_set_active"
                            if runtime_enabled
                            else "legacy_runtime_unqualified"
                        )
                    ),
                    native_runtime_allowlisted=bool(native_runtime_allowlisted),
                    generic_eligible=(
                        bool(row.get("eligible_for_generic")) if strict_normalized else active
                    ),
                    restrictions=_string_items(
                        row.get("restrictions") or eligibility.get("restrictions") or ()
                    ),
                    quarantine_reason=_optional_text(
                        row.get("quarantine_reason") or eligibility.get("quarantine_reason")
                    ),
                    normalization_version=_optional_text(
                        _nested(
                            row,
                            ("normalization_version",),
                            ("normalizer", "version"),
                            ("normalization", "version"),
                        )
                    ),
                    channels=_string_items(row.get("channels") or channel_qa.get("channels") or ()),
                    mapping_profile=mapping_profile,
                    normal_space=_optional_text(
                        _nested(row, ("normal_space",), ("mapping_contract", "normal_space"))
                    ),
                    requires_uv=requires_uv,
                    displacement_policy=displacement_policy,
                    validation_status=_optional_text(
                        row.get("validation_status")
                        or validation.get("status")
                        or _nested(row, ("node_qa", "status"))
                    ),
                    selection_scope=_optional_text(
                        row.get("selection_scope") or eligibility.get("selection_scope")
                    ),
                    semantic_risk_reason=_optional_text(
                        row.get("semantic_risk_reason") or eligibility.get("semantic_risk_reason")
                    ),
                )
            )
        if not records:
            raise ValueError(f"material catalog is empty: {source_path}")
        records.sort(key=lambda record: (record.category_slug, record.material_id))
        canonical = [record.canonical_row(library_root=root) for record in records]
        digest_payload: object = canonical
        if strict_normalized and manifest is None:
            digest_payload = {
                "normalization_version": NORMALIZER_VERSION,
                "records": canonical,
                "schema_version": NORMALIZED_CATALOG_SCHEMA,
            }
        digest = (
            str(manifest["logical_snapshot_sha256"])
            if manifest is not None
            else hashlib.sha256(
                json.dumps(digest_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
        )
        materials_manifest = manifest.get("materials_file") if manifest is not None else None
        raw_manifest = manifest.get("raw_catalog") if manifest is not None else None
        return cls(
            tuple(records),
            root,
            digest,
            source_path,
            NORMALIZED_CATALOG_SCHEMA if strict_normalized else None,
            NORMALIZER_VERSION if strict_normalized else None,
            strict_normalized,
            source_path.with_name("manifest.json") if manifest is not None else None,
            (str(materials_manifest["sha256"]) if isinstance(materials_manifest, dict) else None),
            str(raw_manifest["sha256"]) if isinstance(raw_manifest, dict) else None,
            (str(manifest["native_runtime_allowlist_sha256"]) if manifest is not None else None),
        )


def write_catalog(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    """Small deterministic writer used by downloader tests and normalization jobs."""

    payload = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(payload, encoding="utf-8")
    os.replace(temporary, path)
