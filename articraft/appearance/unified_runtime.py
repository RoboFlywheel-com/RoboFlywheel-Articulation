# SPDX-License-Identifier: Apache-2.0

"""Strict, lazy runtime access to portable unified PBR materials."""

from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from dataclasses import dataclass, field
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping

from PIL import Image, UnidentifiedImageError

UNIFIED_POINTER_SCHEMA = "articraft-unified-pbr-material-pointer/v1"
UNIFIED_RELEASE_SCHEMA = "articraft-unified-pbr-material-release/v1"
UNIFIED_CATALOG_SCHEMA = "articraft-unified-pbr-material-catalog/v1"
UNIFIED_MATERIAL_SCHEMA = "articraft-unified-pbr-material-record/v1"
UNIFIED_POOL_INDEX_SCHEMA = "articraft-unified-pbr-material-class-pool-index/v1"
UNIFIED_POOL_SCHEMA = "articraft-unified-pbr-material-class-pool/v1"
STANDARD_PBR_REPRESENTATION = "standard_pbr"
CANONICAL_MAPPING_PROFILE = "canonical_metric_uv/v1"

PHYSICS_FIELDS = (
    "density_kg_m3",
    "youngs_modulus_pa",
    "poissons_ratio",
    "static_friction_coefficient",
    "dynamic_friction_coefficient",
    "restitution_coefficient",
)
CORE_CHANNELS = ("base_color", "metallic", "roughness", "normal")

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_MATERIAL_CLASS_RE = re.compile(r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$")
_CHANNEL_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _json_object(path: Path, *, field_name: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {field_name} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a JSON object: {path}")
    return value


def _required_text(value: object, *, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} must be a non-empty string")
    return text


def _required_sha(value: object, *, field_name: str) -> str:
    text = str(value or "")
    if _SHA256_RE.fullmatch(text) is None:
        raise ValueError(f"{field_name} must be a lowercase SHA-256")
    return text


def _safe_relative(value: object, *, field_name: str) -> Path:
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
        raise ValueError(f"{field_name} must be a contained POSIX relative path")
    return relative


def _contained_path(
    root: Path,
    value: object,
    *,
    field_name: str,
    must_exist: bool = True,
) -> Path:
    relative = _safe_relative(value, field_name=field_name)
    candidate = root / relative
    if not must_exist:
        return candidate.absolute()
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise ValueError(f"{field_name} escapes or is missing from the unified snapshot") from exc
    return resolved


def _finite_number(value: object, *, field_name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field_name} must be finite")
    return number


def _positive_integer(value: object, *, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _validate_physics(value: object, *, material_id: str) -> dict[str, float]:
    if not isinstance(value, Mapping):
        raise ValueError(f"material {material_id!r} physics.values must be an object")
    physics = {
        field_name: _finite_number(
            value.get(field_name),
            field_name=f"material {material_id!r} physics.{field_name}",
        )
        for field_name in PHYSICS_FIELDS
    }
    if physics["density_kg_m3"] <= 0 or physics["youngs_modulus_pa"] <= 0:
        raise ValueError(f"material {material_id!r} density and Young's modulus must be positive")
    if not 0.0 <= physics["poissons_ratio"] < 0.5:
        raise ValueError(f"material {material_id!r} Poisson ratio is out of range")
    if (
        physics["static_friction_coefficient"] < 0
        or physics["dynamic_friction_coefficient"] < 0
        or physics["static_friction_coefficient"] < physics["dynamic_friction_coefficient"]
    ):
        raise ValueError(f"material {material_id!r} friction coefficients are inconsistent")
    if not 0.0 <= physics["restitution_coefficient"] <= 1.0:
        raise ValueError(f"material {material_id!r} restitution is out of range")
    return physics


def _validate_mapping(value: object, *, material_id: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"material {material_id!r} has no portable mapping_contract")
    if value.get("profile") != CANONICAL_MAPPING_PROFILE:
        raise ValueError(f"material {material_id!r} mapping profile is not portable")
    if value.get("coordinate_unit") != "meter":
        raise ValueError(f"material {material_id!r} mapping coordinate unit must be meter")
    if value.get("normal_space") != "tangent":
        raise ValueError(f"material {material_id!r} mapping normal space must be tangent")
    if value.get("normal_convention") != "opengl_tangent":
        raise ValueError(f"material {material_id!r} normal convention must be OpenGL tangent")
    if value.get("requires_uv") is not True:
        raise ValueError(f"material {material_id!r} portable mapping must require UVs")
    tile_size = _finite_number(
        value.get("tile_size_m"),
        field_name=f"material {material_id!r} mapping tile_size_m",
    )
    if tile_size <= 0:
        raise ValueError(f"material {material_id!r} mapping tile_size_m must be positive")
    return json.loads(json.dumps(value, ensure_ascii=False))


def _validate_factor(value: object, *, field_name: str) -> object:
    if isinstance(value, (list, tuple)):
        if not value:
            raise ValueError(f"{field_name} factor must not be empty")
        return [_finite_number(item, field_name=field_name) for item in value]
    return _finite_number(value, field_name=field_name)


@dataclass(frozen=True, slots=True)
class UnifiedTextureReceipt:
    path: str
    sha256: str
    decoded_pixel_sha256: str
    size_bytes: int
    width: int
    height: int
    colorspace: str
    role: str
    kind: str
    normal_convention: str | None


def _texture_receipt(value: Mapping[str, Any], *, field_name: str) -> UnifiedTextureReceipt:
    path = _safe_relative(value.get("path"), field_name=f"{field_name}.path").as_posix()
    if Path(path).suffix.lower() != ".png":
        raise ValueError(f"{field_name}.path must name a PNG file")
    kind = _required_text(value.get("kind"), field_name=f"{field_name}.kind")
    if kind not in {"standardized_map", "source_map"}:
        raise ValueError(f"{field_name}.kind is not a published texture kind")
    role = _required_text(value.get("role"), field_name=f"{field_name}.role")
    colorspace = _required_text(value.get("colorspace"), field_name=f"{field_name}.colorspace")
    normal_convention_value = value.get("normal_convention")
    normal_convention = (
        None
        if normal_convention_value is None
        else _required_text(
            normal_convention_value,
            field_name=f"{field_name}.normal_convention",
        )
    )
    if normal_convention not in {None, "opengl_tangent"}:
        raise ValueError(f"{field_name}.normal_convention must be OpenGL tangent")
    if kind == "standardized_map":
        expected_colorspace = "sRGB" if role in {"base_color", "emission"} else "Non-Color"
        if colorspace != expected_colorspace:
            raise ValueError(f"{field_name}.colorspace must be {expected_colorspace} for {role}")
        if role == "normal" and normal_convention != "opengl_tangent":
            raise ValueError(f"{field_name}.normal_convention is required for a normal map")
    return UnifiedTextureReceipt(
        path=path,
        sha256=_required_sha(value.get("sha256"), field_name=f"{field_name}.sha256"),
        decoded_pixel_sha256=_required_sha(
            value.get("decoded_pixel_sha256"),
            field_name=f"{field_name}.decoded_pixel_sha256",
        ),
        size_bytes=_positive_integer(
            value.get("size_bytes"), field_name=f"{field_name}.size_bytes"
        ),
        width=_positive_integer(value.get("width"), field_name=f"{field_name}.width"),
        height=_positive_integer(value.get("height"), field_name=f"{field_name}.height"),
        colorspace=colorspace,
        role=role,
        kind=kind,
        normal_convention=normal_convention,
    )


def validate_png_texture(
    path: Path,
    receipt: UnifiedTextureReceipt | Mapping[str, Any],
    *,
    field_name: str,
    verified_payloads: set[tuple[str, str, int, int]] | None = None,
) -> UnifiedTextureReceipt:
    """Validate one content-addressed PNG against its decoded-pixel receipt."""

    normalized = (
        receipt
        if isinstance(receipt, UnifiedTextureReceipt)
        else _texture_receipt(receipt, field_name=field_name)
    )
    source = Path(path)
    if not source.is_file() or source.suffix.lower() != ".png":
        raise ValueError(f"{field_name} must resolve to a PNG file")
    if source.stat().st_size != normalized.size_bytes:
        raise ValueError(f"{field_name} size mismatch")
    if sha256_file(source) != normalized.sha256:
        raise ValueError(f"{field_name} SHA mismatch")

    payload_key = (
        normalized.sha256,
        normalized.decoded_pixel_sha256,
        normalized.width,
        normalized.height,
    )
    if verified_payloads is not None and payload_key in verified_payloads:
        return normalized
    try:
        with Image.open(source) as image:
            if image.format != "PNG":
                raise ValueError("decoded image format is not PNG")
            dimensions = (int(image.width), int(image.height))
            image.verify()
        if dimensions != (normalized.width, normalized.height):
            raise ValueError(
                f"declared dimensions {(normalized.width, normalized.height)} "
                f"do not match decoded dimensions {dimensions}"
            )
        with Image.open(source) as image:
            if image.format != "PNG":
                raise ValueError("decoded image format is not PNG")
            rgba = image.convert("RGBA")
            payload = b"RGBA\0" + struct.pack(">II", rgba.width, rgba.height) + rgba.tobytes()
    except (OSError, SyntaxError, UnidentifiedImageError) as exc:
        raise ValueError(f"{field_name} is not a decodable PNG: {exc}") from exc
    decoded_sha = hashlib.sha256(payload).hexdigest()
    if decoded_sha != normalized.decoded_pixel_sha256:
        raise ValueError(f"{field_name} decoded pixel SHA mismatch")
    if verified_payloads is not None:
        verified_payloads.add(payload_key)
    return normalized


@dataclass(frozen=True, slots=True)
class UnifiedMaterial:
    material_id: str
    material_key: str
    material_class_id: str
    appearance: dict[str, Any]
    physics_values: dict[str, float]
    file_sha256: dict[str, str]
    file_receipts: dict[str, UnifiedTextureReceipt]
    record: dict[str, Any]


@dataclass(frozen=True, slots=True)
class _PoolReceipt:
    material_class_id: str
    material_count: int
    path: Path
    sha256: str


@dataclass(slots=True)
class UnifiedMaterialLibrary:
    pointer_path: Path
    pointer_sha256: str
    snapshot_root: Path
    snapshot_sha256: str
    manifest_sha256: str
    catalog_sha256: str
    pool_index_sha256: str
    materials_by_id: dict[str, UnifiedMaterial]
    _pool_receipts: dict[str, _PoolReceipt] = field(repr=False)
    _pool_cache: dict[str, tuple[UnifiedMaterial, ...]] = field(default_factory=dict, repr=False)
    _verified_textures: set[tuple[str, str, int, int]] = field(default_factory=set, repr=False)

    def pool_sha256(self, material_class_id: str) -> str:
        receipt = self._pool_receipts.get(material_class_id)
        if receipt is None:
            raise ValueError(f"unified material library has no pool {material_class_id!r}")
        return receipt.sha256

    def load_pool(self, material_class_id: str) -> tuple[UnifiedMaterial, ...]:
        cached = self._pool_cache.get(material_class_id)
        if cached is not None:
            return cached
        receipt = self._pool_receipts.get(material_class_id)
        if receipt is None:
            raise ValueError(f"unified material library has no pool {material_class_id!r}")
        relative = receipt.path.relative_to(self.snapshot_root)
        pool_path = _contained_path(
            self.snapshot_root,
            relative.as_posix(),
            field_name=f"pool {material_class_id!r} path",
        )
        if sha256_file(pool_path) != receipt.sha256:
            raise ValueError(f"unified pool {material_class_id!r} SHA mismatch")
        document = _json_object(pool_path, field_name=f"pool {material_class_id!r}")
        if document.get("schema_version") != UNIFIED_POOL_SCHEMA:
            raise ValueError(f"unified pool {material_class_id!r} schema mismatch")
        if document.get("logical_snapshot_sha256") != self.snapshot_sha256:
            raise ValueError(f"unified pool {material_class_id!r} snapshot mismatch")
        if document.get("material_class_id") != material_class_id:
            raise ValueError(f"unified pool {material_class_id!r} identity mismatch")
        rows = document.get("materials")
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"unified pool {material_class_id!r} is empty")
        candidates: list[UnifiedMaterial] = []
        identities: list[tuple[str, str]] = []
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                raise ValueError(f"unified pool {material_class_id!r} row {index} is invalid")
            material_id = _required_text(
                row.get("material_id"),
                field_name=f"pool {material_class_id!r} material_id",
            )
            material_key = _required_sha(
                row.get("material_key"),
                field_name=f"pool {material_class_id!r} material_key",
            )
            material = self.materials_by_id.get(material_id)
            if material is None or material.material_key != material_key:
                raise ValueError(
                    f"unified pool {material_class_id!r} does not join catalog material {material_id!r}"
                )
            if material.material_class_id != material_class_id:
                raise ValueError(f"unified pool {material_class_id!r} crosses material classes")
            identities.append((material_id, material_key))
            candidates.append(material)
        if identities != sorted(identities) or len(set(identities)) != len(identities):
            raise ValueError(f"unified pool {material_class_id!r} is not canonical")
        if len(candidates) != receipt.material_count or document.get("material_count") != len(
            candidates
        ):
            raise ValueError(f"unified pool {material_class_id!r} count mismatch")
        result = tuple(candidates)
        self._pool_cache[material_class_id] = result
        return result

    def texture_source(self, material: UnifiedMaterial, relative_path: str, sha256: str) -> Path:
        expected = _required_sha(sha256, field_name="texture SHA")
        receipt = material.file_receipts.get(relative_path)
        if receipt is None or receipt.sha256 != expected:
            raise ValueError(
                f"material {material.material_id!r} texture is absent from appearance.files"
            )
        source = _contained_path(
            self.snapshot_root,
            relative_path,
            field_name=f"material {material.material_id!r} texture path",
        )
        validate_png_texture(
            source,
            receipt,
            field_name=f"material {material.material_id!r} texture",
            verified_payloads=self._verified_textures,
        )
        return source


def _catalog_material(row: object) -> UnifiedMaterial:
    if not isinstance(row, dict):
        raise ValueError("unified catalog material row must be an object")
    if row.get("schema_version") != UNIFIED_MATERIAL_SCHEMA:
        raise ValueError("unified catalog material schema mismatch")
    material_id = _required_text(row.get("material_id"), field_name="material_id")
    material_key = _required_sha(row.get("material_key"), field_name="material_key")
    material_class_id = _required_text(row.get("material_class_id"), field_name="material_class_id")
    if _MATERIAL_CLASS_RE.fullmatch(material_class_id) is None:
        raise ValueError(f"material {material_id!r} has an invalid material_class_id")
    appearance = row.get("appearance")
    if not isinstance(appearance, dict):
        raise ValueError(f"material {material_id!r} appearance must be an object")
    if appearance.get("representation") != STANDARD_PBR_REPRESENTATION:
        raise ValueError(f"material {material_id!r} is not standard_pbr")
    if appearance.get("texture_runtime_enabled") is not True:
        raise ValueError(f"material {material_id!r} is not texture-runtime enabled")
    mapping = _validate_mapping(appearance.get("mapping_contract"), material_id=material_id)

    files = appearance.get("files")
    if not isinstance(files, list):
        raise ValueError(f"material {material_id!r} appearance.files must be a list")
    file_sha256: dict[str, str] = {}
    file_receipts: dict[str, UnifiedTextureReceipt] = {}
    normalized_files: list[dict[str, Any]] = []
    for index, file_row in enumerate(files):
        if not isinstance(file_row, Mapping):
            raise ValueError(f"material {material_id!r} appearance.files[{index}] is invalid")
        field_name = f"material {material_id!r} appearance.files[{index}]"
        receipt = _texture_receipt(file_row, field_name=field_name)
        previous_receipt = file_receipts.setdefault(receipt.path, receipt)
        if previous_receipt != receipt:
            raise ValueError(
                f"material {material_id!r} repeats a file path with different receipts"
            )
        previous = file_sha256.setdefault(receipt.path, receipt.sha256)
        if previous != receipt.sha256:
            raise ValueError(f"material {material_id!r} repeats a file path with different hashes")
        normalized_row = dict(file_row)
        normalized_row.update(
            {
                "path": receipt.path,
                "sha256": receipt.sha256,
                "decoded_pixel_sha256": receipt.decoded_pixel_sha256,
                "size_bytes": receipt.size_bytes,
                "width": receipt.width,
                "height": receipt.height,
                "colorspace": receipt.colorspace,
                "role": receipt.role,
                "kind": receipt.kind,
            }
        )
        if receipt.normal_convention is not None:
            normalized_row["normal_convention"] = receipt.normal_convention
        normalized_files.append(normalized_row)

    channels = appearance.get("channels")
    if not isinstance(channels, dict) or any(channel not in channels for channel in CORE_CHANNELS):
        raise ValueError(f"material {material_id!r} lacks required PBR channels")
    normalized_channels: dict[str, dict[str, Any]] = {}
    for channel, raw in channels.items():
        if _CHANNEL_RE.fullmatch(str(channel)) is None or not isinstance(raw, Mapping):
            raise ValueError(f"material {material_id!r} has an invalid channel")
        kind = raw.get("kind")
        normalized = dict(raw)
        if kind == "texture":
            path = _safe_relative(
                raw.get("path"),
                field_name=f"material {material_id!r} channel {channel} path",
            ).as_posix()
            digest = _required_sha(
                raw.get("sha256"),
                field_name=f"material {material_id!r} channel {channel} SHA",
            )
            if file_sha256.get(path) != digest:
                raise ValueError(
                    f"material {material_id!r} channel {channel} is absent from appearance.files"
                )
            colorspace = _required_text(
                raw.get("colorspace"),
                field_name=f"material {material_id!r} channel {channel} colorspace",
            )
            if channel == "base_color" and colorspace != "sRGB":
                raise ValueError(f"material {material_id!r} base_color must use sRGB")
            if channel in {"metallic", "roughness", "normal"} and colorspace != "Non-Color":
                raise ValueError(f"material {material_id!r} channel {channel} must be Non-Color")
            receipt = file_receipts[path]
            if receipt.kind != "standardized_map" or receipt.role != str(channel):
                raise ValueError(
                    f"material {material_id!r} channel {channel} does not reference its standardized map"
                )
            if receipt.colorspace != colorspace:
                raise ValueError(
                    f"material {material_id!r} channel {channel} colorspace disagrees with its file"
                )
            if (
                channel == "normal"
                and raw.get("normal_convention", "opengl_tangent") != "opengl_tangent"
            ):
                raise ValueError(f"material {material_id!r} normal channel convention is invalid")
            normalized["path"] = path
            normalized["sha256"] = digest
        elif kind == "factor" and channel != "normal":
            normalized["value"] = _validate_factor(
                raw.get("value"),
                field_name=f"material {material_id!r} channel {channel}",
            )
        elif kind == "none" and channel == "normal":
            normalized = {"kind": "none"}
        else:
            raise ValueError(f"material {material_id!r} channel {channel} has invalid kind")
        normalized_channels[str(channel)] = normalized

    normalized_appearance = json.loads(json.dumps(appearance, ensure_ascii=False))
    normalized_appearance["channels"] = normalized_channels
    normalized_appearance["mapping_contract"] = mapping
    normalized_appearance["files"] = normalized_files
    physics = row.get("physics")
    values = physics.get("values") if isinstance(physics, Mapping) else None
    normalized_record = json.loads(json.dumps(row, ensure_ascii=False))
    normalized_record["appearance"] = normalized_appearance
    return UnifiedMaterial(
        material_id=material_id,
        material_key=material_key,
        material_class_id=material_class_id,
        appearance=normalized_appearance,
        physics_values=_validate_physics(values, material_id=material_id),
        file_sha256=file_sha256,
        file_receipts=file_receipts,
        record=normalized_record,
    )


def _manifest_file_receipt(
    manifest: Mapping[str, Any],
    name: str,
) -> Mapping[str, Any] | None:
    files = manifest.get("files")
    receipt = files.get(name) if isinstance(files, Mapping) else None
    return receipt if isinstance(receipt, Mapping) else None


def load_unified_material_library(pointer_path: Path) -> UnifiedMaterialLibrary:
    """Load the immutable catalog and pool index; class pools and PNGs stay lazy."""

    raw_pointer = Path(pointer_path).expanduser()
    if raw_pointer.is_symlink():
        raise ValueError("unified material pointer must not be a symlink")
    pointer = raw_pointer.resolve(strict=True)
    if pointer.name != "latest.json" or pointer.parent.name != "unified":
        raise ValueError("unified material pointer must be unified/latest.json")
    # Published pointer paths are relative to pbr_material_library, not to the
    # nested unified/ directory that contains latest.json.
    library_root = pointer.parent.parent.resolve(strict=True)
    value = _json_object(pointer, field_name="unified material pointer")
    if value.get("schema_version") != UNIFIED_POINTER_SCHEMA:
        raise ValueError("unified material pointer schema mismatch")
    snapshot_sha = _required_sha(
        value.get("logical_snapshot_sha256"), field_name="logical snapshot SHA"
    )
    snapshot_root = _contained_path(
        library_root,
        value.get("snapshot_path"),
        field_name="snapshot_path",
    )
    if not snapshot_root.is_dir() or snapshot_root.name != snapshot_sha:
        raise ValueError("unified material snapshot path/content address mismatch")

    paths: dict[str, Path] = {}
    hashes: dict[str, str] = {}
    for name in ("manifest", "catalog", "pool_index"):
        paths[name] = _contained_path(
            library_root,
            value.get(f"{name}_path"),
            field_name=f"{name}_path",
        )
        try:
            paths[name].relative_to(snapshot_root)
        except ValueError as exc:
            raise ValueError(f"unified {name} is outside its snapshot") from exc
        hashes[name] = _required_sha(
            value.get(f"{name}_sha256"),
            field_name=f"{name}_sha256",
        )
        if sha256_file(paths[name]) != hashes[name]:
            raise ValueError(f"unified {name} SHA mismatch")
    expected_paths = {
        "manifest": snapshot_root / "manifest.json",
        "catalog": snapshot_root / "catalog.json",
        "pool_index": snapshot_root / "pools" / "index.json",
    }
    for name, expected in expected_paths.items():
        if paths[name] != expected.resolve(strict=True):
            raise ValueError(f"unified {name} pointer path mismatch")

    manifest = _json_object(paths["manifest"], field_name="unified manifest")
    catalog = _json_object(paths["catalog"], field_name="unified catalog")
    pool_index = _json_object(paths["pool_index"], field_name="unified pool index")
    if manifest.get("schema_version") != UNIFIED_RELEASE_SCHEMA:
        raise ValueError("unified release schema mismatch")
    if catalog.get("schema_version") != UNIFIED_CATALOG_SCHEMA:
        raise ValueError("unified catalog schema mismatch")
    if pool_index.get("schema_version") != UNIFIED_POOL_INDEX_SCHEMA:
        raise ValueError("unified pool index schema mismatch")
    for name, document in (
        ("manifest", manifest),
        ("catalog", catalog),
        ("pool index", pool_index),
    ):
        if document.get("logical_snapshot_sha256") != snapshot_sha:
            raise ValueError(f"unified {name} snapshot mismatch")
    identity = catalog.get("identity")
    if not isinstance(identity, Mapping) or _canonical_sha256(identity) != snapshot_sha:
        raise ValueError("unified catalog identity digest mismatch")
    if manifest.get("identity") != identity:
        raise ValueError("unified manifest/catalog identities disagree")

    for name in ("catalog", "pool_index"):
        receipt = _manifest_file_receipt(manifest, name)
        if receipt is None:
            continue
        receipt_path = _contained_path(
            snapshot_root,
            receipt.get("path"),
            field_name=f"manifest {name} path",
        )
        if receipt_path != paths[name] or receipt.get("sha256") != hashes[name]:
            raise ValueError(f"unified manifest {name} receipt mismatch")

    rows = catalog.get("materials")
    if not isinstance(rows, list) or not rows:
        raise ValueError("unified catalog has no materials")
    materials = [_catalog_material(row) for row in rows]
    material_ids = [row.material_id for row in materials]
    if material_ids != sorted(material_ids) or len(set(material_ids)) != len(material_ids):
        raise ValueError("unified catalog materials are not canonical")
    material_keys = [row.material_key for row in materials]
    if len(set(material_keys)) != len(material_keys):
        raise ValueError("unified catalog repeats material keys")
    materials_by_id = {row.material_id: row for row in materials}
    summary = catalog.get("summary")
    if not isinstance(summary, Mapping):
        raise ValueError("unified catalog summary must be an object")
    if summary.get("material_count") not in (None, len(materials)):
        raise ValueError("unified catalog material count mismatch")

    pool_rows = pool_index.get("pools")
    if not isinstance(pool_rows, list) or not pool_rows:
        raise ValueError("unified pool index has no pools")
    receipts: dict[str, _PoolReceipt] = {}
    ordered_classes: list[str] = []
    indexed_count = 0
    for index, row in enumerate(pool_rows):
        if not isinstance(row, Mapping):
            raise ValueError(f"unified pool index row {index} is invalid")
        material_class_id = _required_text(
            row.get("material_class_id"),
            field_name=f"pool index row {index} material_class_id",
        )
        if _MATERIAL_CLASS_RE.fullmatch(material_class_id) is None:
            raise ValueError(f"unified pool index class {material_class_id!r} is invalid")
        count = row.get("material_count")
        if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
            raise ValueError(f"unified pool {material_class_id!r} must be non-empty")
        expected_name = hashlib.sha256(material_class_id.encode("utf-8")).hexdigest() + ".json"
        pool_path = _contained_path(
            snapshot_root,
            row.get("pool_path"),
            field_name=f"pool {material_class_id!r} path",
        )
        if pool_path.name != expected_name or pool_path.parent.name != "by-class":
            raise ValueError(f"unified pool {material_class_id!r} path is not content-safe")
        if material_class_id in receipts:
            raise ValueError(f"unified pool index repeats {material_class_id!r}")
        receipts[material_class_id] = _PoolReceipt(
            material_class_id=material_class_id,
            material_count=count,
            path=pool_path,
            sha256=_required_sha(
                row.get("pool_sha256"),
                field_name=f"pool {material_class_id!r} SHA",
            ),
        )
        ordered_classes.append(material_class_id)
        indexed_count += count
    if ordered_classes != sorted(ordered_classes):
        raise ValueError("unified pool index is not canonical")
    if pool_index.get("class_count") not in (None, len(receipts)):
        raise ValueError("unified pool index class count mismatch")
    if pool_index.get("material_count") not in (None, indexed_count):
        raise ValueError("unified pool index material count mismatch")
    if indexed_count != len(materials):
        raise ValueError("unified pool index does not cover the catalog exactly once")

    return UnifiedMaterialLibrary(
        pointer_path=pointer,
        pointer_sha256=sha256_file(pointer),
        snapshot_root=snapshot_root,
        snapshot_sha256=snapshot_sha,
        manifest_sha256=hashes["manifest"],
        catalog_sha256=hashes["catalog"],
        pool_index_sha256=hashes["pool_index"],
        materials_by_id=materials_by_id,
        _pool_receipts=receipts,
    )
