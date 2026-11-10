# SPDX-License-Identifier: Apache-2.0

"""Pure helpers for building a normalized, source-preserving PBR catalog.

The raw provider download is immutable input.  A normalization run writes a
separate package plus a relocatable metadata sidecar and catalog row.  This
module intentionally has no :mod:`bpy` dependency so catalog validation and
planning remain testable in an ordinary Python process.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable, Mapping

NORMALIZED_CATALOG_SCHEMA = "articraft-normalized-material-catalog/v1"
NORMALIZED_PACKAGE_SCHEMA = "articraft-normalized-material-package/v1"
NORMALIZED_CATALOG_MANIFEST_SCHEMA = "articraft-normalized-material-catalog-manifest/v1"
NORMALIZER_VERSION = "articraft-pbr-normalizer/v1"
RUNTIME_PROFILE_POLICY_VERSION = "articraft-material-runtime-profile/v1"
MATERIAL_PROFILES = frozenset({"texture_set", "native_procedural"})

# These are technically valid active materials, but their macro-pattern,
# intended object, or strong directionality is not interchangeable with an
# arbitrary surface in the same BlenderKit category.  These entries are soft
# retrieval hints only: a technically valid material remains active and
# category-retrievable.  This is deliberately separate from hard technical
# quarantine.
_SEMANTIC_RISK_PATTERNS: tuple[tuple[str, str, tuple[str, ...], tuple[str, ...]], ...] = (
    (
        "fabric pattern 07",
        "checkered towel/picnic-scale weave requires an explicitly compatible patterned fabric surface",
        ("semantic_pattern_match_required", "requires_direction_axis"),
        ("fabric_panel", "table_linen", "upholstery"),
    ),
    (
        "book pattern",
        "coarse book-cover textile is not interchangeable with yarn, thread, or arbitrary fabric",
        ("explicit_component_role_only", "not_for_yarn_or_thread"),
        ("book_cover", "fabric_panel", "upholstery"),
    ),
    (
        "diamond grid glass panel green yellow",
        "colored diamond grid and metal framing encode an architectural panel rather than generic glass",
        (
            "planar_panel_only",
            "requires_direction_axis",
            "semantic_pattern_match_required",
        ),
        ("glass_panel", "partition", "window"),
    ),
    (
        "crystal gloss glass",
        "layered crystal/rainbow optics are intended for decorative optical glass rather than generic glazing or containers",
        ("explicit_component_role_only", "semantic_optics_match_required"),
        ("crystal", "decorative_glass", "jewelry"),
    ),
    (
        "brushed black metal",
        "strong brushed grain requires a declared local material direction",
        ("requires_direction_axis",),
        (),
    ),
    (
        "fossil reef",
        "deep fossilized reef relief is specific to terrain, rock, wall, or underwater surfaces",
        ("high_relief_surface", "semantic_use_match_required"),
        ("ground", "rock", "terrain", "wall"),
    ),
    (
        "forest leaves 02",
        "moss, leaves, twigs, and debris encode a forest-floor surface rather than generic organic matter",
        ("ground_surface_only", "high_relief_surface", "semantic_use_match_required"),
        ("ground", "landscape", "terrain"),
    ),
    (
        "industrial dark tech frame",
        "modular sci-fi panel framing is an object-scale architectural motif rather than generic plastic",
        (
            "planar_panel_only",
            "requires_direction_axis",
            "semantic_pattern_match_required",
        ),
        ("architectural_panel", "sci_fi_panel", "tech_frame"),
    ),
    (
        "matte tire rubber",
        "automotive tire surface is intended for tire or wheel components",
        ("explicit_component_role_only",),
        ("tire", "wheel"),
    ),
    (
        "pebbled basketball rubber",
        "basketball-specific pebble pattern and recessed seams require a sports-ball surface",
        ("explicit_component_role_only", "semantic_pattern_match_required"),
        ("basketball", "sports_ball"),
    ),
    (
        "american walnut",
        "natural walnut grain requires a declared local material direction",
        ("requires_direction_axis",),
        (),
    ),
    (
        "polished oak planks",
        "plank seams and grain direction require a floor/panel-style UV layout",
        ("floor_or_panel_only", "requires_direction_axis"),
        ("floor", "panel"),
    ),
    (
        "wood wood",
        "strong natural oak grain requires a declared local material direction",
        ("requires_direction_axis",),
        (),
    ),
    (
        "dark wood",
        "strong directional wood pattern requires an explicitly oriented host surface",
        ("requires_direction_axis",),
        (),
    ),
    (
        "glossy blue plastic horizontal grooves",
        "strong directional macro-grooves require an explicitly aligned product surface",
        ("requires_direction_axis", "semantic_pattern_match_required"),
        (),
    ),
    (
        "cyan geometric patterned plastic",
        "decorative geometric motif is not a generic plastic base surface",
        ("semantic_pattern_match_required",),
        (),
    ),
)


def sha256_file(path: Path) -> str:
    """Return the SHA-256 of *path* without loading the whole file in memory."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_sha256(payload: object) -> str:
    """Hash a JSON value using the same canonical form used by catalog rows."""

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def native_runtime_allowlist_sha256(material_ids: Iterable[str]) -> str:
    """Hash the canonical native-procedural runtime allowlist.

    The digest describes the normalized set rather than a particular text-file
    serialization, so whitespace and input ordering cannot change a catalog
    snapshot.
    """

    normalized = sorted({str(value).strip() for value in material_ids if str(value).strip()})
    return canonical_json_sha256(
        {
            "material_ids": normalized,
            "policy_version": RUNTIME_PROFILE_POLICY_VERSION,
        }
    )


def logical_catalog_snapshot_sha256(
    *,
    catalog_file_sha256: str,
    raw_catalog_sha256: str,
    native_allowlist_sha256: str,
    normalizer_version: str = NORMALIZER_VERSION,
) -> str:
    """Return the content identity used for ``catalogs/<sha>/`` snapshots."""

    for field, value in {
        "catalog_file_sha256": catalog_file_sha256,
        "raw_catalog_sha256": raw_catalog_sha256,
        "native_allowlist_sha256": native_allowlist_sha256,
    }.items():
        if re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ValueError(f"{field} must be 64 lowercase hexadecimal characters")
    return canonical_json_sha256(
        {
            "catalog_file_sha256": catalog_file_sha256,
            "native_allowlist_sha256": native_allowlist_sha256,
            "normalizer_version": normalizer_version,
            "raw_catalog_sha256": raw_catalog_sha256,
            "schema_version": NORMALIZED_CATALOG_MANIFEST_SCHEMA,
        }
    )


def safe_relative_path(value: object, *, field: str) -> Path:
    """Parse a portable library-relative path and reject traversal/drive syntax."""

    text = str(value or "").strip()
    windows = PureWindowsPath(text)
    posix = PurePosixPath(text)
    if (
        not text
        or "\\" in text
        or posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or any(part in {"", ".", ".."} for part in posix.parts)
    ):
        raise ValueError(f"{field} must be a safe POSIX library-relative path: {text!r}")
    return Path(*posix.parts)


def contained_file(root: Path, relative: object, *, field: str) -> Path:
    """Resolve an existing file and prove that symlinks do not escape *root*."""

    canonical_root = root.resolve(strict=True)
    candidate = (canonical_root / safe_relative_path(relative, field=field)).resolve(strict=True)
    try:
        candidate.relative_to(canonical_root)
    except ValueError as exc:
        raise ValueError(f"{field} escapes the material library: {relative!r}") from exc
    if not candidate.is_file():
        raise ValueError(f"{field} is not a file: {relative!r}")
    return candidate


def atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Atomically write deterministic, human-readable JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
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


def atomic_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    """Atomically write deterministic JSONL in the caller-provided order."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(
                    json.dumps(
                        row,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    + "\n"
                )
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def source_parameters(row: Mapping[str, Any]) -> dict[str, Any]:
    """Return provider parameters from either normalized or API-style rows."""

    source = row.get("source")
    if isinstance(source, Mapping):
        parameters = source.get("parameters")
        if isinstance(parameters, Mapping):
            return dict(parameters)
    parameters = row.get("parameters")
    if isinstance(parameters, Mapping):
        return dict(parameters)
    return {}


def material_profile(
    parameters: Mapping[str, Any],
    *,
    image_texture_count: int | None = None,
    procedural_node_count: int | None = None,
) -> str:
    """Classify a provider material without inventing a third shader family."""

    if parameters.get("procedural") is True:
        return "native_procedural"
    if parameters.get("purePbr") is True and parameters.get("procedural") is False:
        return "texture_set"
    if procedural_node_count is not None and procedural_node_count > 0:
        return "native_procedural"
    if image_texture_count is not None and image_texture_count > 0:
        return "texture_set"
    return "native_procedural"


def texture_size_m(parameters: Mapping[str, Any]) -> float | None:
    """Read a positive provider-declared real-world tile period in metres."""

    value = parameters.get("textureSizeMeters")
    if value in (None, ""):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not 0.0 < parsed < 1_000_000.0:
        return None
    return parsed


def generic_eligibility(
    *,
    display_name: str,
    category_slug: str = "",
    profile: str,
    tile_size_m: float | None,
    qa_status: str,
) -> dict[str, Any]:
    """Describe whether a material may enter ordinary component retrieval.

    Semantic risks are audit metadata and soft ranking hints only.  They never
    make a technically valid material inactive or remove it from category-wide
    retrieval.  Only a concrete normalization/QA failure makes the material
    inactive and technically quarantined.
    """

    if profile not in MATERIAL_PROFILES:
        raise ValueError(f"unsupported material profile: {profile!r}")
    restrictions = (
        [
            "requires_metric_uv",
            "tangent_space_normal",
            "true_displacement_disabled",
        ]
        if profile == "texture_set"
        else ["preserve_native_node_graph"]
    )
    technical_failure_reason: str | None = None
    semantic_risk_reason: str | None = None
    qa_flags: list[str] = []
    recommended_use: list[str] = []
    semantic_advisories: list[str] = []
    recommended_component_roles: list[str] = []
    selection_scope = "generic"
    allowed_component_roles: list[str] = []
    excluded_component_roles: list[str] = []
    material_subtype: str | None = None
    normalized_name = " ".join(re.findall(r"[a-z0-9]+", str(display_name).casefold()))
    for (
        pattern,
        candidate_reason,
        candidate_restrictions,
        candidate_roles,
    ) in _SEMANTIC_RISK_PATTERNS:
        if pattern in normalized_name:
            semantic_risk_reason = candidate_reason
            qa_flags.append("semantic_macro_pattern")
            semantic_advisories.extend(candidate_restrictions)
            recommended_component_roles.extend(candidate_roles)
            recommended_use.append(candidate_reason)
            break
    if "matte tire rubber" in normalized_name:
        recommended_use.append("best matched to wheel or tire components")
    if category_slug == "fabric":
        semantic_advisories.append("prefer_surface_fabric_over_yarn_or_thread")
        if "book pattern" in normalized_name:
            material_subtype = "book_cover_textile"
        elif "plain white flat" in normalized_name:
            material_subtype = "upholstery_flat_weave"
        else:
            material_subtype = "woven_fabric"
    if qa_status == "fail":
        technical_failure_reason = "material failed normalization node/channel QA"
        restrictions.append("qa_failure")
        selection_scope = "quarantined"
    if profile == "texture_set" and tile_size_m is None:
        technical_failure_reason = (
            technical_failure_reason or "texture set has no trustworthy real-world tile size"
        )
        restrictions.append("tile_size_missing")
        selection_scope = "quarantined"
    active = technical_failure_reason is None
    eligible_for_generic = active
    return {
        "active": active,
        "eligible_for_generic": eligible_for_generic,
        "selection_scope": selection_scope,
        "allowed_component_roles": sorted(set(allowed_component_roles)),
        "excluded_component_roles": excluded_component_roles,
        "material_subtype": material_subtype,
        "qa_flags": sorted(set(qa_flags)),
        "recommended_use": recommended_use,
        "semantic_advisories": sorted(set(semantic_advisories)),
        "recommended_component_roles": sorted(set(recommended_component_roles)),
        "semantic_risk_reason": semantic_risk_reason,
        "restrictions": sorted(set(restrictions)),
        "quarantine_reason": technical_failure_reason,
        "validation": {
            "active": active,
            "status": "active" if active else "quarantined",
            "reasons": [technical_failure_reason] if technical_failure_reason else [],
        },
    }


def normalized_package_paths(
    *,
    material_id: str,
    category_slug: str,
    source_sha256: str,
) -> tuple[Path, Path]:
    """Return deterministic content-addressed package and sidecar paths."""

    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", category_slug):
        raise ValueError(f"invalid category_slug: {category_slug!r}")
    if not re.fullmatch(r"[0-9a-f]{64}", source_sha256):
        raise ValueError("source_sha256 must be 64 lowercase hexadecimal characters")
    identity = hashlib.sha256(f"{NORMALIZER_VERSION}\0{material_id}".encode("utf-8")).hexdigest()[
        :16
    ]
    directory = Path("packages") / category_slug / identity / source_sha256[:16]
    return directory / "material.blend", directory / "metadata.json"


@dataclass(frozen=True, slots=True)
class SourceMaterial:
    """One hash-verified raw catalog entry."""

    material_id: str
    category_slug: str
    display_name: str
    license: str
    provider: str
    asset_base_id: str
    raw_relative_path: Path
    raw_path: Path
    raw_sha256: str
    row: dict[str, Any]
    row_sha256: str

    @property
    def parameters(self) -> dict[str, Any]:
        return source_parameters(self.row)

    @property
    def planned_profile(self) -> str:
        return material_profile(self.parameters)

    @property
    def declared_texture_size_m(self) -> float | None:
        return texture_size_m(self.parameters)


def _required_text(value: object, *, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"catalog row has no {field}")
    return text


def _raw_relative_path(row: Mapping[str, Any]) -> object:
    selected = row.get("selected_file")
    if isinstance(selected, Mapping) and selected.get("relative_path"):
        return selected["relative_path"]
    for key in ("package_blend_path", "relative_path"):
        if row.get(key):
            return row[key]
    raise ValueError("catalog row has no raw blend path")


def _declared_source_sha256(row: Mapping[str, Any]) -> str:
    selected = row.get("selected_file")
    if isinstance(selected, Mapping) and selected.get("sha256"):
        return str(selected["sha256"]).strip().lower()
    for key in ("sha256", "download_sha256"):
        if row.get(key):
            return str(row[key]).strip().lower()
    validation = row.get("validation")
    if isinstance(validation, Mapping) and validation.get("sha256"):
        return str(validation["sha256"]).strip().lower()
    return ""


def load_source_catalog(catalog_path: Path, *, library_root: Path) -> tuple[SourceMaterial, ...]:
    """Load raw rows, reject path escapes, and verify every source package hash."""

    root = library_root.resolve(strict=True)
    source_path = catalog_path.resolve(strict=True)
    try:
        source_path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"catalog is outside its library root: {source_path}") from exc

    records: list[SourceMaterial] = []
    seen: set[str] = set()
    for line_number, line in enumerate(source_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid catalog JSON at line {line_number}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"catalog row {line_number} is not an object")
        material_id = _required_text(row.get("material_id"), field="material_id")
        if material_id in seen:
            raise ValueError(f"duplicate material_id in source catalog: {material_id}")
        seen.add(material_id)
        category_slug = _required_text(row.get("category_slug"), field="category_slug")
        relative = safe_relative_path(
            _raw_relative_path(row), field=f"{material_id}.raw blend path"
        )
        raw_path = contained_file(root, relative.as_posix(), field=f"{material_id}.raw blend")
        actual_sha256 = sha256_file(raw_path)
        expected_sha256 = _declared_source_sha256(row)
        if expected_sha256 and expected_sha256 != actual_sha256:
            raise ValueError(
                f"source hash mismatch for {material_id}: {expected_sha256} != {actual_sha256}"
            )
        source = row.get("source") if isinstance(row.get("source"), dict) else {}
        records.append(
            SourceMaterial(
                material_id=material_id,
                category_slug=category_slug,
                display_name=str(
                    row.get("display_name")
                    or row.get("name")
                    or source.get("display_name")
                    or material_id
                ),
                license=str(row.get("license") or source.get("license") or "unknown"),
                provider=str(row.get("provider") or "blenderkit"),
                asset_base_id=str(source.get("asset_base_id") or material_id),
                raw_relative_path=relative,
                raw_path=raw_path,
                raw_sha256=actual_sha256,
                row=row,
                row_sha256=canonical_json_sha256(row),
            )
        )
    if not records:
        raise ValueError(f"source material catalog is empty: {source_path}")
    records.sort(key=lambda item: (item.category_slug, item.material_id))
    return tuple(records)
