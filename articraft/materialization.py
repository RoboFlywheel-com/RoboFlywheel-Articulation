# SPDX-License-Identifier: Apache-2.0

"""Deterministic, receipt-free export of portable template seed assets."""

from __future__ import annotations

import json
import math
import os
import random
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PureWindowsPath
from typing import Any, Callable, Mapping, Sequence

from articraft.appearance.retrieval import AppearanceRequest, appearance_requests_from_model
from articraft.appearance.unified_runtime import (
    PHYSICS_FIELDS,
    UnifiedMaterial,
    UnifiedMaterialLibrary,
    load_unified_material_library,
    sha256_file,
    validate_png_texture,
)

APPEARANCE_SCHEMA = "articraft-seed-appearance/v1"
PHYSICS_SCHEMA = "articraft-seed-physics/v1"
SAMPLING_ALGORITHM = "local-random-choice/v1"

_SLUG_RE = re.compile(r"^[A-Za-z0-9_]+$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SPEC_FIELDS = (
    "kind",
    "alpha_mode",
    "alpha_cutoff",
    "emission_color",
    "emission_strength",
    "text",
    "uv_offset",
    "uv_scale",
    "uv_rotation_rad",
)

_MODEL_SOURCE = """from __future__ import annotations

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


class AssetExportError(RuntimeError):
    """A seed could not be exported as a complete portable asset."""


@dataclass(frozen=True, slots=True)
class _CompiledSeed:
    object_model: object
    urdf_xml: str


@dataclass(frozen=True, slots=True)
class _SelectedMaterial:
    material: UnifiedMaterial
    material_class_id: str
    selection_group_key: str
    pool_count: int
    pool_sha256: str
    draw_order: int
    selection_index: int


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
        raise AssetExportError(f"{field_name} must be a contained POSIX relative path")
    return relative


def _contained_file(root: Path, value: object, *, field_name: str) -> Path:
    relative = _safe_relative(value, field_name=field_name)
    try:
        resolved = (root / relative).resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise AssetExportError(
            f"{field_name} escapes or is missing from the seed workspace"
        ) from exc
    if not resolved.is_file():
        raise AssetExportError(f"{field_name} must resolve to a regular file")
    return resolved


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_json_bytes(value))


def _finite_json(value: object, *, field_name: str) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise AssetExportError(f"{field_name} contains a non-finite value")
        return value
    if isinstance(value, Enum):
        return _finite_json(value.value, field_name=field_name)
    if isinstance(value, Mapping):
        return {
            str(key): _finite_json(item, field_name=f"{field_name}.{key}")
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [
            _finite_json(item, field_name=f"{field_name}[{index}]")
            for index, item in enumerate(value)
        ]
    raise AssetExportError(f"{field_name} is not JSON serializable")


def _appearance_only_spec(value: object) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for field_name in _SPEC_FIELDS:
        if not hasattr(value, field_name):
            raise AssetExportError(f"appearance_only spec lacks {field_name}")
        payload[field_name] = _finite_json(
            getattr(value, field_name),
            field_name=f"appearance_only.{field_name}",
        )
    return payload


def select_material(
    library: UnifiedMaterialLibrary,
    request: AppearanceRequest,
    *,
    rng: random.Random,
    draw_order: int,
) -> _SelectedMaterial:
    """Choose directly from one exact-class pool using the seed-local RNG."""

    material_class_id = request.material_class_id
    if material_class_id is None:
        raise AssetExportError("only physical appearance requests enter material sampling")
    candidates = library.load_pool(material_class_id)
    group = request.selection_group_key or request.surface_key
    material = rng.choice(candidates)
    return _SelectedMaterial(
        material=material,
        material_class_id=material_class_id,
        selection_group_key=group,
        pool_count=len(candidates),
        pool_sha256=library.pool_sha256(material_class_id),
        draw_order=int(draw_order),
        selection_index=candidates.index(material),
    )


def _compile_ordinary_model(
    *,
    slug: str,
    stem: str,
    seed: int,
    workspace: Path,
) -> _CompiledSeed:
    """Execute a generator once and compile ordinary URDF without checks or Full."""

    try:
        from agent.compiler import load_model_globals
        from sdk._core.v0.assets import activate_asset_session, asset_session_for_script
        from sdk.v0._urdf_export import compile_object_to_urdf_xml

        workspace.mkdir(parents=True, exist_ok=False)
        script = workspace / "model.py"
        script.write_text(
            _MODEL_SOURCE.format(slug=slug, stem=stem, seed=int(seed)),
            encoding="utf-8",
        )
        with activate_asset_session(asset_session_for_script(script)):
            globals_dict = load_model_globals(script, sdk_package="sdk")
            object_model = globals_dict.get("object_model")
            if object_model is None:
                raise AssetExportError("template did not produce object_model")
            urdf_xml = compile_object_to_urdf_xml(
                object_model,
                asset_root=workspace,
                include_physical_collisions=True,
                validate=True,
            )
    except AssetExportError:
        raise
    except Exception as exc:
        raise AssetExportError(f"template {slug!r} seed {seed} failed to compile: {exc}") from exc
    if not isinstance(urdf_xml, str) or not urdf_xml.strip():
        raise AssetExportError("template did not compile into URDF")
    return _CompiledSeed(object_model=object_model, urdf_xml=urdf_xml)


def _validated_output_directory(
    path: Path,
    *,
    output_root: Path,
    field_name: str,
    create: bool,
) -> Path:
    """Return a real directory contained by output_root, rejecting link ancestors."""

    if path.is_symlink():
        raise AssetExportError(f"{field_name} must not be a symlink")
    if create:
        path.mkdir(parents=False, exist_ok=True)
    if not path.exists():
        raise AssetExportError(f"{field_name} does not exist")
    if path.is_symlink() or not path.is_dir():
        raise AssetExportError(f"{field_name} must be a real directory")
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(output_root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise AssetExportError(f"{field_name} escapes the output root") from exc
    if resolved != path.absolute():
        raise AssetExportError(f"{field_name} must not contain symlink components")
    return resolved


def _copy_file(
    source: Path,
    destination: Path,
    *,
    expected_sha256: str | None,
    dedup_by_sha256: dict[str, Path],
) -> dict[str, Any]:
    digest = sha256_file(source)
    if expected_sha256 is not None and digest != expected_sha256:
        raise AssetExportError(f"source SHA mismatch while copying {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if not destination.is_file() or sha256_file(destination) != digest:
            raise AssetExportError(f"asset destination collision: {destination}")
    else:
        existing = dedup_by_sha256.get(digest)
        if existing is not None:
            try:
                os.link(existing, destination)
            except OSError:
                shutil.copyfile(existing, destination)
        else:
            shutil.copyfile(source, destination)
    if sha256_file(destination) != digest:
        raise AssetExportError(f"copied asset SHA mismatch: {destination}")
    dedup_by_sha256.setdefault(digest, destination)
    return {
        "path": destination.as_posix(),
        "sha256": digest,
        "size_bytes": destination.stat().st_size,
    }


def _xml_asset_paths(urdf_xml: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    try:
        root = ET.fromstring(urdf_xml)
    except ET.ParseError as exc:
        raise AssetExportError(f"compiled URDF is invalid XML: {exc}") from exc
    meshes: set[str] = set()
    textures: set[str] = set()
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        filename = element.attrib.get("filename")
        if filename is None:
            continue
        if tag == "mesh":
            meshes.add(filename)
        elif tag == "texture":
            textures.add(filename)
    return tuple(sorted(meshes)), tuple(sorted(textures))


def _copy_urdf_assets(
    urdf_xml: str,
    *,
    workspace: Path,
    seed_root: Path,
    dedup_by_sha256: dict[str, Path],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mesh_rows: list[dict[str, Any]] = []
    texture_rows: list[dict[str, Any]] = []
    meshes, textures = _xml_asset_paths(urdf_xml)
    (seed_root / "assets" / "meshes").mkdir(parents=True, exist_ok=True)
    (seed_root / "assets" / "textures").mkdir(parents=True, exist_ok=True)
    for raw in meshes:
        relative = _safe_relative(raw, field_name="URDF mesh filename")
        if relative.suffix.lower() != ".obj" or relative.parts[:2] != ("assets", "meshes"):
            raise AssetExportError(f"URDF mesh must be an OBJ under assets/meshes: {raw}")
        source = _contained_file(workspace, relative.as_posix(), field_name="URDF mesh")
        receipt = _copy_file(
            source,
            seed_root / relative,
            expected_sha256=None,
            dedup_by_sha256=dedup_by_sha256,
        )
        receipt["path"] = relative.as_posix()
        mesh_rows.append(receipt)
    for raw in textures:
        relative = _safe_relative(raw, field_name="URDF texture filename")
        if relative.parts[:2] != ("assets", "textures") or relative.suffix.lower() == ".blend":
            raise AssetExportError(f"URDF texture must be under assets/textures: {raw}")
        source = _contained_file(workspace, relative.as_posix(), field_name="URDF texture")
        receipt = _copy_file(
            source,
            seed_root / relative,
            expected_sha256=None,
            dedup_by_sha256=dedup_by_sha256,
        )
        receipt["path"] = relative.as_posix()
        texture_rows.append(receipt)
    return mesh_rows, texture_rows


def _material_file_tail(material: UnifiedMaterial, source_path: str, sha256: str) -> Path:
    relative = _safe_relative(source_path, field_name="catalog texture path")
    parts = relative.parts
    try:
        key_index = parts.index(material.material_key)
    except ValueError:
        return Path("files") / f"{sha256}.png"
    tail = Path(*parts[key_index + 1 :])
    if not tail.parts:
        return Path("files") / f"{sha256}.png"
    return _safe_relative(tail.as_posix(), field_name="material texture output path")


def _rewrite_paths(value: object, replacements: Mapping[str, str]) -> object:
    if isinstance(value, list):
        return [_rewrite_paths(item, replacements) for item in value]
    if isinstance(value, dict):
        rewritten: dict[str, Any] = {}
        for key, item in value.items():
            if key == "path" and isinstance(item, str) and item in replacements:
                rewritten[key] = replacements[item]
            else:
                rewritten[key] = _rewrite_paths(item, replacements)
        return rewritten
    return value


def _copy_material_textures(
    material: UnifiedMaterial,
    *,
    library: UnifiedMaterialLibrary,
    seed_root: Path,
    dedup_by_sha256: dict[str, Path],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    directory = Path("assets") / "textures" / f"mat_{material.material_key}"
    replacements: dict[str, str] = {}
    receipts: list[dict[str, Any]] = []
    channels = material.appearance.get("channels")
    if not isinstance(channels, Mapping):
        raise AssetExportError(f"material {material.material_id!r} has invalid channels")
    runtime_paths = {
        str(channel.get("path") or "")
        for channel in channels.values()
        if isinstance(channel, Mapping) and channel.get("kind") == "texture"
    }
    if "" in runtime_paths:
        raise AssetExportError(f"material {material.material_id!r} has an empty channel path")
    files = material.appearance.get("files")
    if not isinstance(files, list):
        raise AssetExportError(f"material {material.material_id!r} has invalid appearance.files")
    file_rows: dict[str, Mapping[str, Any]] = {}
    for row in files:
        if not isinstance(row, Mapping):
            raise AssetExportError(f"material {material.material_id!r} has invalid file receipt")
        source_path = str(row.get("path") or "")
        if source_path in file_rows:
            raise AssetExportError(
                f"material {material.material_id!r} repeats file receipt {source_path!r}"
            )
        file_rows[source_path] = row
    missing = sorted(runtime_paths - file_rows.keys())
    if missing:
        raise AssetExportError(
            f"material {material.material_id!r} channel file is absent from appearance.files: "
            f"{missing[0]}"
        )
    if runtime_paths:
        (seed_root / directory).mkdir(parents=True, exist_ok=True)
    for row in sorted(
        (file_rows[path] for path in runtime_paths),
        key=lambda item: str(item.get("path") or ""),
    ):
        source_path = str(row.get("path") or "")
        expected_sha = str(row.get("sha256") or "")
        if _SHA256_RE.fullmatch(expected_sha) is None:
            raise AssetExportError(f"material {material.material_id!r} file SHA is invalid")
        source = library.texture_source(material, source_path, expected_sha)
        relative = directory / _material_file_tail(material, source_path, expected_sha)
        receipt = _copy_file(
            source,
            seed_root / relative,
            expected_sha256=expected_sha,
            dedup_by_sha256=dedup_by_sha256,
        )
        receipt["path"] = relative.as_posix()
        for field_name in (
            "kind",
            "role",
            "decoded_pixel_sha256",
            "width",
            "height",
            "colorspace",
            "normal_convention",
        ):
            if field_name in row:
                receipt[field_name] = row[field_name]
        receipts.append(receipt)
        replacements[source_path] = relative.as_posix()
    rewritten = {
        field_name: _rewrite_paths(material.appearance[field_name], replacements)
        for field_name in (
            "representation",
            "texture_runtime_enabled",
            "mapping_contract",
            "texture_size_m",
            "channels",
            "factors",
        )
        if field_name in material.appearance
    }
    rewritten["files"] = [dict(receipt) for receipt in receipts]
    for channel_name, channel in rewritten.get("channels", {}).items():
        if isinstance(channel, dict) and channel.get("kind") == "texture":
            path = channel.get("path")
            if not isinstance(path, str) or path not in replacements.values():
                raise AssetExportError(
                    f"material {material.material_id!r} channel {channel_name} was not copied"
                )
    if receipts:
        rewritten["texture_directory"] = directory.as_posix()
    return rewritten, receipts


def _material_metadata(material: UnifiedMaterial) -> dict[str, Any]:
    row = material.record
    return {
        "material_id": material.material_id,
        "material_key": material.material_key,
        "material_class_id": material.material_class_id,
        "category_slug": row.get("category_slug"),
        "display_name": row.get("display_name"),
        "provider": row.get("provider"),
        "license": row.get("license"),
    }


def _appearance_only_binding(
    request: AppearanceRequest,
    *,
    seed_root: Path,
) -> dict[str, Any]:
    texture = request.texture
    texture_receipt: dict[str, Any] | None = None
    if texture is not None:
        relative = _safe_relative(texture, field_name="appearance-only texture")
        if relative.parts[:2] != ("assets", "textures"):
            raise AssetExportError("appearance-only texture must be under assets/textures")
        copied = _contained_file(
            seed_root,
            relative.as_posix(),
            field_name="appearance-only texture",
        )
        texture_receipt = {
            "path": relative.as_posix(),
            "sha256": sha256_file(copied),
            "size_bytes": copied.stat().st_size,
        }
    spec = request.appearance_only
    if spec is None:
        raise AssetExportError("appearance-only request has no AppearanceOnlySpec")
    return {
        "appearance": {
            "material_name": request.material_name,
            "rgba": None if request.rgba is None else list(request.rgba),
            "spec": _appearance_only_spec(spec),
            "texture": texture_receipt,
        },
        "appearance_only": True,
        "kind": "appearance_only",
        "material": None,
        "material_class_id": None,
        "selection": None,
        "surface_key": request.surface_key,
    }


def _pbr_binding(
    request: AppearanceRequest,
    selected: _SelectedMaterial,
    *,
    portable_appearance: dict[str, Any],
) -> dict[str, Any]:
    return {
        "appearance": portable_appearance,
        "appearance_only": False,
        "kind": "pbr_material",
        "material": _material_metadata(selected.material),
        "material_class_id": selected.material.material_class_id,
        "selection": {
            "algorithm": SAMPLING_ALGORITHM,
            "candidate_count": selected.pool_count,
            "draw_order": selected.draw_order,
            "group_key": selected.selection_group_key,
            "pool_sha256": selected.pool_sha256,
            "selection_index": selected.selection_index,
        },
        "surface_key": request.surface_key,
    }


def _physics_binding(
    request: AppearanceRequest,
    material: UnifiedMaterial | None,
) -> dict[str, Any]:
    appearance_only = material is None
    values = (
        {field_name: None for field_name in PHYSICS_FIELDS}
        if appearance_only
        else {field_name: material.physics_values[field_name] for field_name in PHYSICS_FIELDS}
    )
    return {
        "appearance_only": appearance_only,
        "material_class_id": None if material is None else material.material_class_id,
        "material_id": None if material is None else material.material_id,
        "surface_key": request.surface_key,
        "values": values,
    }


def _template_sha256(repo_root: Path, slug: str) -> str:
    template = repo_root / "agent" / "templates" / f"{slug}.py"
    if not template.is_file():
        raise AssetExportError(f"template module does not exist: {template}")
    return sha256_file(template)


def _materialize_seed(
    *,
    repo_root: Path,
    slug: str,
    stem: str,
    seed: int,
    material_seed: int,
    library: UnifiedMaterialLibrary,
    geometry_root: Path,
    seed_root: Path,
    compile_seed: Callable[..., _CompiledSeed],
) -> None:
    compiled = compile_seed(slug=slug, stem=stem, seed=seed, workspace=geometry_root)
    requests = appearance_requests_from_model(compiled.object_model, require_all=True)
    if not requests:
        raise AssetExportError("template has no visual appearance requests")
    seed_root.mkdir(parents=True, exist_ok=False)
    dedup_by_sha256: dict[str, Path] = {}
    mesh_rows, authored_texture_rows = _copy_urdf_assets(
        compiled.urdf_xml,
        workspace=geometry_root,
        seed_root=seed_root,
        dedup_by_sha256=dedup_by_sha256,
    )
    (seed_root / "model.urdf").write_bytes(compiled.urdf_xml.encode("utf-8"))
    model_sha = sha256_file(seed_root / "model.urdf")

    material_payloads: dict[str, tuple[dict[str, Any], list[dict[str, Any]]]] = {}
    appearance_bindings: list[dict[str, Any]] = []
    physics_bindings: list[dict[str, Any]] = []
    pbr_texture_rows: list[dict[str, Any]] = []
    material_groups: dict[tuple[str, str], AppearanceRequest] = {}
    for request in requests:
        if request.asset_type == "appearance_only":
            continue
        if request.asset_type not in {"pbr_material", "optical_material"}:
            raise AssetExportError(
                f"visual {request.surface_key!r} is neither PBR nor appearance-only"
            )
        material_class_id = request.material_class_id
        if material_class_id is None:
            raise AssetExportError(f"visual {request.surface_key!r} has no material class")
        group_key = request.selection_group_key or request.surface_key
        material_groups.setdefault((group_key, material_class_id), request)

    rng = random.Random(int(material_seed))
    selected_groups: dict[tuple[str, str], _SelectedMaterial] = {}
    for draw_order, group_key in enumerate(sorted(material_groups)):
        selected_groups[group_key] = select_material(
            library,
            material_groups[group_key],
            rng=rng,
            draw_order=draw_order,
        )

    for request in requests:
        if request.asset_type == "appearance_only":
            appearance_bindings.append(_appearance_only_binding(request, seed_root=seed_root))
            physics_bindings.append(_physics_binding(request, None))
            continue
        material_class_id = request.material_class_id
        if material_class_id is None:  # guarded while building material_groups
            raise AssertionError("material request lost its class")
        group_key = (request.selection_group_key or request.surface_key, material_class_id)
        selected = selected_groups[group_key]
        cached = material_payloads.get(selected.material.material_id)
        if cached is None:
            cached = _copy_material_textures(
                selected.material,
                library=library,
                seed_root=seed_root,
                dedup_by_sha256=dedup_by_sha256,
            )
            material_payloads[selected.material.material_id] = cached
            pbr_texture_rows.extend(cached[1])
        appearance_bindings.append(_pbr_binding(request, selected, portable_appearance=cached[0]))
        physics_bindings.append(_physics_binding(request, selected.material))

    appearance_bindings.sort(key=lambda row: str(row["surface_key"]))
    physics_bindings.sort(key=lambda row: str(row["surface_key"]))
    common = {
        "library": {
            "catalog_sha256": library.catalog_sha256,
            "manifest_sha256": library.manifest_sha256,
            "pointer_sha256": library.pointer_sha256,
            "pool_index_sha256": library.pool_index_sha256,
            "snapshot_sha256": library.snapshot_sha256,
        },
        "material_seed": int(material_seed),
        "model_urdf_sha256": model_sha,
        "seed": int(seed),
        "slug": slug,
        "template_sha256": _template_sha256(repo_root, slug),
    }
    appearance_payload = {
        "schema_version": APPEARANCE_SCHEMA,
        **common,
        "authoritative": True,
        "sampling_algorithm": SAMPLING_ALGORITHM,
        "assets": {
            "meshes": sorted(mesh_rows, key=lambda row: str(row["path"])),
            "textures": sorted(
                authored_texture_rows + pbr_texture_rows,
                key=lambda row: str(row["path"]),
            ),
        },
        "bindings": appearance_bindings,
    }
    physics_payload = {
        "schema_version": PHYSICS_SCHEMA,
        **common,
        "fields": list(PHYSICS_FIELDS),
        "bindings": physics_bindings,
    }
    _write_json(seed_root / "appearance.json", appearance_payload)
    _write_json(seed_root / "physics.json", physics_payload)
    _validate_seed_tree(seed_root)


def _validate_seed_tree(seed_root: Path) -> None:
    required = ("model.urdf", "appearance.json", "physics.json")
    for name in required:
        if not (seed_root / name).is_file():
            raise AssetExportError(f"seed export is missing {name}")
    appearance = json.loads((seed_root / "appearance.json").read_text(encoding="utf-8"))
    physics = json.loads((seed_root / "physics.json").read_text(encoding="utf-8"))
    appearance_keys = [row.get("surface_key") for row in appearance.get("bindings", [])]
    physics_rows = physics.get("bindings", [])
    physics_keys = [row.get("surface_key") for row in physics_rows]
    if appearance_keys != physics_keys or appearance_keys != sorted(appearance_keys):
        raise AssetExportError("appearance and physics bindings do not align")
    assets = appearance.get("assets")
    if not isinstance(assets, dict):
        raise AssetExportError("appearance assets must be an object")
    seen_asset_paths: set[str] = set()
    asset_receipts: dict[str, dict[str, Any]] = {}
    verified_pbr_payloads: set[tuple[str, str, int, int]] = set()
    for kind in ("meshes", "textures"):
        rows = assets.get(kind)
        if not isinstance(rows, list):
            raise AssetExportError(f"appearance assets.{kind} must be a list")
        for row in rows:
            if not isinstance(row, dict):
                raise AssetExportError(f"appearance assets.{kind} row must be an object")
            relative = _safe_relative(row.get("path"), field_name=f"assets.{kind} path")
            if relative.as_posix() in seen_asset_paths:
                raise AssetExportError(f"appearance repeats asset path {relative.as_posix()}")
            seen_asset_paths.add(relative.as_posix())
            asset_receipts[relative.as_posix()] = row
            source = _contained_file(
                seed_root,
                relative.as_posix(),
                field_name=f"assets.{kind} file",
            )
            texture_kind = row.get("kind") if kind == "textures" else None
            if texture_kind is not None:
                if texture_kind != "standardized_map":
                    raise AssetExportError("seed PBR textures must be standardized runtime maps")
                try:
                    validate_png_texture(
                        source,
                        row,
                        field_name=f"appearance PBR texture {relative.as_posix()!r}",
                        verified_payloads=verified_pbr_payloads,
                    )
                except ValueError as exc:
                    raise AssetExportError(str(exc)) from exc
            else:
                if row.get("sha256") != sha256_file(source):
                    raise AssetExportError(f"appearance assets.{kind} SHA mismatch")
                if row.get("size_bytes") != source.stat().st_size:
                    raise AssetExportError(f"appearance assets.{kind} size mismatch")
    for row in physics_rows:
        values = row.get("values")
        if (
            not isinstance(values, dict)
            or len(values) != len(PHYSICS_FIELDS)
            or set(values) != set(PHYSICS_FIELDS)
        ):
            raise AssetExportError("physics binding does not contain exactly six canonical fields")
        if row.get("appearance_only") and any(value is not None for value in values.values()):
            raise AssetExportError("appearance-only physics values must all be null")
    referenced_pbr_paths: set[str] = set()
    for binding in appearance.get("bindings", []):
        if binding.get("appearance_only"):
            texture = binding.get("appearance", {}).get("texture")
            if texture is not None and texture.get("path") not in seen_asset_paths:
                raise AssetExportError("appearance-only texture is absent from asset receipts")
            continue
        portable_appearance = binding.get("appearance", {})
        files = portable_appearance.get("files")
        if not isinstance(files, list):
            raise AssetExportError("PBR binding files must be a list")
        file_receipts: dict[str, dict[str, Any]] = {}
        for file_row in files:
            if not isinstance(file_row, dict):
                raise AssetExportError("PBR binding file receipt must be an object")
            relative = _safe_relative(file_row.get("path"), field_name="PBR binding file path")
            asset_row = asset_receipts.get(relative.as_posix())
            if asset_row is None:
                raise AssetExportError("PBR binding file is absent from asset receipts")
            receipt_fields = {
                "sha256",
                "decoded_pixel_sha256",
                "size_bytes",
                "width",
                "height",
                "colorspace",
                "role",
                "kind",
                "normal_convention",
            }
            if any(file_row.get(field) != asset_row.get(field) for field in receipt_fields):
                raise AssetExportError("PBR binding and asset file receipts disagree")
            file_receipts[relative.as_posix()] = file_row
        channels = portable_appearance.get("channels")
        if not isinstance(channels, dict):
            raise AssetExportError("PBR binding has no channels")
        channel_texture_paths: set[str] = set()
        for channel_name, channel in channels.items():
            if isinstance(channel, dict) and channel.get("kind") == "texture":
                path = channel.get("path")
                if path not in seen_asset_paths:
                    raise AssetExportError("PBR channel texture is absent from asset receipts")
                file_row = file_receipts.get(str(path))
                if file_row is None:
                    raise AssetExportError(
                        "PBR channel texture is absent from binding file receipts"
                    )
                if channel.get("sha256") != file_row.get("sha256"):
                    raise AssetExportError(
                        "PBR channel texture SHA disagrees with its file receipt"
                    )
                if channel.get("colorspace") != file_row.get("colorspace"):
                    raise AssetExportError(
                        "PBR channel texture colorspace disagrees with its file receipt"
                    )
                channel_texture_paths.add(str(path))
                if channel_name == "normal" and (
                    channel.get("normal_convention") != "opengl_tangent"
                    or file_row.get("normal_convention") != "opengl_tangent"
                ):
                    raise AssetExportError("PBR normal texture convention is not OpenGL tangent")
        if channel_texture_paths != set(file_receipts):
            raise AssetExportError("PBR binding files are not the runtime channel closure")
        referenced_pbr_paths.update(channel_texture_paths)
    published_pbr_paths = {
        path for path, row in asset_receipts.items() if row.get("kind") == "standardized_map"
    }
    if referenced_pbr_paths != published_pbr_paths:
        raise AssetExportError("PBR binding and asset texture sets disagree")
    for path in seed_root.rglob("*"):
        if path.is_symlink():
            raise AssetExportError(f"seed export contains a symlink: {path}")
        if path.is_file() and path.suffix.lower() == ".blend":
            raise AssetExportError("seed export must not contain Blender packages")
    mesh_root = seed_root / "assets" / "meshes"
    if any(path.is_file() and path.suffix.lower() != ".obj" for path in mesh_root.rglob("*")):
        raise AssetExportError("assets/meshes may contain only OBJ files")


def export_template_assets(
    *,
    repo_root: Path,
    slug: str,
    stem: str,
    seeds: Sequence[int],
    out_root: Path,
    material_seed: int | None = None,
    library_pointer: Path | None = None,
    _compile_seed: Callable[..., _CompiledSeed] = _compile_ordinary_model,
    _load_library: Callable[[Path], UnifiedMaterialLibrary] = load_unified_material_library,
) -> tuple[Path, ...]:
    """Build every requested seed privately, then publish only complete seed trees."""

    if _SLUG_RE.fullmatch(slug) is None or _SLUG_RE.fullmatch(stem) is None:
        raise ValueError("template slug and stem must be Python identifiers")
    ordered_seeds = tuple(sorted({int(seed) for seed in seeds}))
    if not ordered_seeds:
        raise ValueError("at least one seed is required")
    repo = Path(repo_root).resolve(strict=True)
    output = Path(os.path.abspath(Path(out_root).expanduser()))
    if output.resolve(strict=False) != output:
        raise AssetExportError("output root must not contain symlink components")
    category = output / slug
    staging_parent = output / ".staging"
    targets = tuple(category / f"seed_{seed}" for seed in ordered_seeds)
    existing = [target for target in targets if target.exists() or target.is_symlink()]
    if existing:
        raise FileExistsError(f"seed export target already exists: {existing[0]}")
    for ancestor, field_name in (
        (category, "template output directory"),
        (staging_parent, "staging directory"),
    ):
        if ancestor.is_symlink():
            raise AssetExportError(f"{field_name} must not be a symlink")
        if ancestor.exists() and not ancestor.is_dir():
            raise AssetExportError(f"{field_name} must be a directory")

    pointer = (
        Path(library_pointer).expanduser()
        if library_pointer is not None
        else repo / "pbr_material_library" / "unified" / "latest.json"
    )
    output.mkdir(parents=True, exist_ok=True)
    if output.is_symlink() or not output.is_dir():
        raise AssetExportError("output root must be a real directory")
    staging_parent = _validated_output_directory(
        staging_parent,
        output_root=output,
        field_name="staging directory",
        create=True,
    )
    staging = Path(tempfile.mkdtemp(prefix=f"{slug}-", dir=staging_parent))
    staging = _validated_output_directory(
        staging,
        output_root=staging_parent,
        field_name="private staging directory",
        create=False,
    )
    published: list[Path] = []
    category_existed = category.exists()
    try:
        library = _load_library(pointer)
        staged_seeds: list[Path] = []
        for seed in ordered_seeds:
            geometry_root = staging / "geometry" / f"seed_{seed}"
            staged_seed = staging / "publish" / f"seed_{seed}"
            _materialize_seed(
                repo_root=repo,
                slug=slug,
                stem=stem,
                seed=seed,
                material_seed=seed if material_seed is None else int(material_seed),
                library=library,
                geometry_root=geometry_root,
                seed_root=staged_seed,
                compile_seed=_compile_seed,
            )
            staged_seeds.append(staged_seed)

        raced = [target for target in targets if target.exists() or target.is_symlink()]
        if raced:
            raise FileExistsError(f"seed export target appeared during build: {raced[0]}")
        category = _validated_output_directory(
            category,
            output_root=output,
            field_name="template output directory",
            create=True,
        )
        try:
            for staged_seed, target in zip(staged_seeds, targets, strict=True):
                category = _validated_output_directory(
                    category,
                    output_root=output,
                    field_name="template output directory",
                    create=False,
                )
                target = category / target.name
                if target.exists() or target.is_symlink():
                    raise FileExistsError(f"seed export target appeared during publish: {target}")
                staged_seed.replace(target)
                published.append(target)
        except Exception:
            for target in published:
                shutil.rmtree(target, ignore_errors=True)
            published.clear()
            if not category_existed:
                try:
                    category.rmdir()
                except OSError:
                    pass
            raise
        return targets
    finally:
        shutil.rmtree(staging, ignore_errors=True)
        try:
            staging_parent.rmdir()
        except OSError:
            pass
