#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Build a source-preserving, Blender-inspected PBR material catalog.

Raw BlenderKit downloads are immutable.  The default invocation only validates
and prints a deterministic plan.  ``--execute`` is required before this script
opens Blender files or writes normalized packages/catalog metadata.

The normalized package preserves the provider shader graph except that true
surface displacement is disconnected by default (normal/bump data stays
intact).  It adds an explicit ``texture_set`` or ``native_procedural`` profile
and records the real-world tile period plus channel/node QA.  Texture sets use
metric UVs because their normal maps are tangent-space; BOX projection is not
a valid generic fallback.  UVs remain a consumer responsibility and are not
baked into any generator mesh here.
"""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import importlib.util
import json
import math
import multiprocessing
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

# Blender's standalone Python does not add the repository root when a script
# file under ``scripts/`` is executed directly.
_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))

try:
    from articraft.appearance.normalized import (  # noqa: E402
        MATERIAL_PROFILES,
        NORMALIZED_CATALOG_MANIFEST_SCHEMA,
        NORMALIZED_CATALOG_SCHEMA,
        NORMALIZED_PACKAGE_SCHEMA,
        NORMALIZER_VERSION,
        RUNTIME_PROFILE_POLICY_VERSION,
        SourceMaterial,
        atomic_json,
        atomic_jsonl,
        canonical_json_sha256,
        generic_eligibility,
        load_source_catalog,
        logical_catalog_snapshot_sha256,
        material_profile,
        native_runtime_allowlist_sha256,
        normalized_package_paths,
        sha256_file,
        texture_size_m,
    )
except ModuleNotFoundError:
    # The pinned Blender 5.2 environment intentionally contains bpy and the
    # renderer, not Articraft's CAD stack (for example manifold3d).  Importing
    # ``articraft.appearance.normalized`` normally executes the package
    # ``__init__`` first, which would pull that unrelated stack into this
    # source-preserving normalizer.  Load the pure helper module directly only
    # when bpy is available; ordinary Python must still surface missing project
    # dependencies instead of silently hiding them.
    if importlib.util.find_spec("bpy") is None:
        raise
    _helpers_path = _REPOSITORY_ROOT / "articraft" / "appearance" / "normalized.py"
    _helpers_spec = importlib.util.spec_from_file_location(
        "_articraft_normalized_helpers", _helpers_path
    )
    if _helpers_spec is None or _helpers_spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"could not load normalized material helpers: {_helpers_path}")
    _helpers = importlib.util.module_from_spec(_helpers_spec)
    sys.modules[_helpers_spec.name] = _helpers
    _helpers_spec.loader.exec_module(_helpers)
    MATERIAL_PROFILES = _helpers.MATERIAL_PROFILES
    NORMALIZED_CATALOG_SCHEMA = _helpers.NORMALIZED_CATALOG_SCHEMA
    NORMALIZED_CATALOG_MANIFEST_SCHEMA = _helpers.NORMALIZED_CATALOG_MANIFEST_SCHEMA
    NORMALIZED_PACKAGE_SCHEMA = _helpers.NORMALIZED_PACKAGE_SCHEMA
    NORMALIZER_VERSION = _helpers.NORMALIZER_VERSION
    RUNTIME_PROFILE_POLICY_VERSION = _helpers.RUNTIME_PROFILE_POLICY_VERSION
    SourceMaterial = _helpers.SourceMaterial
    atomic_json = _helpers.atomic_json
    atomic_jsonl = _helpers.atomic_jsonl
    canonical_json_sha256 = _helpers.canonical_json_sha256
    generic_eligibility = _helpers.generic_eligibility
    load_source_catalog = _helpers.load_source_catalog
    logical_catalog_snapshot_sha256 = _helpers.logical_catalog_snapshot_sha256
    material_profile = _helpers.material_profile
    native_runtime_allowlist_sha256 = _helpers.native_runtime_allowlist_sha256
    normalized_package_paths = _helpers.normalized_package_paths
    sha256_file = _helpers.sha256_file
    texture_size_m = _helpers.texture_size_m

Inspection = dict[str, Any]
Normalizer = Callable[[SourceMaterial, Path], Inspection]

_CHANNEL_PRIORITY = (
    "alpha",
    "metallic",
    "roughness",
    "specular",
    "normal",
    "height",
    "ambient_occlusion",
    "base_color",
    "emission",
)
_CHANNEL_ALIASES: dict[str, frozenset[str]] = {
    "base_color": frozenset({"albedo", "basecolor", "base", "diff", "diffuse", "color", "colour"}),
    "roughness": frozenset({"rough", "roughness", "gloss", "glossiness"}),
    "specular": frozenset({"spec", "specular", "reflectance"}),
    "metallic": frozenset({"metal", "metallic", "metalness"}),
    "normal": frozenset({"normal", "nor", "nrm"}),
    "height": frozenset({"height", "disp", "displacement", "bump"}),
    "ambient_occlusion": frozenset({"ao", "ambientocclusion", "occlusion", "occ"}),
    "alpha": frozenset({"alpha", "opacity", "mask", "transparency"}),
    "emission": frozenset({"emit", "emission", "emissive"}),
}
_SCALAR_CHANNELS = frozenset(
    {"roughness", "specular", "metallic", "normal", "height", "ambient_occlusion"}
)
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_OPTICAL_IOR_POLICY: dict[str, tuple[float, str]] = {
    "amethyst bottle glass": (2.45, "high_ior_risk"),
    "olive bottle glass": (1.65, "elevated_ior_risk"),
    "dark green bottle glass": (1.50, "reference_baseline"),
}


def _tokens(value: object) -> frozenset[str]:
    return frozenset(_TOKEN_RE.findall(str(value or "").casefold()))


def _normalize_name(value: object) -> str:
    return " ".join(_TOKEN_RE.findall(str(value or "").casefold()))


def _surface_connected(material: Any) -> bool:
    if material.node_tree is None:
        return False
    for node in material.node_tree.nodes:
        if getattr(node, "type", "") != "OUTPUT_MATERIAL":
            continue
        if not getattr(node, "is_active_output", True):
            continue
        socket = node.inputs.get("Surface")
        if socket is not None and socket.is_linked:
            return True
    return False


def _choose_material(materials: Sequence[Any], display_name: str) -> Any:
    wanted = _normalize_name(display_name)

    def rank(material: Any) -> tuple[int, int, int, str]:
        name = _normalize_name(material.name)
        return (
            -int(bool(wanted) and name == wanted),
            -int(bool(wanted) and (wanted in name or name in wanted)),
            -int(_surface_connected(material)),
            material.name.casefold(),
        )

    available = [material for material in materials if material is not None]
    if not available:
        raise ValueError("Blender package contains no Material datablock")
    return min(available, key=rank)


def _node_trees(root: Any) -> tuple[tuple[str, Any], ...]:
    pending = [("root", root)]
    seen: set[int] = set()
    result: list[tuple[str, Any]] = []
    while pending:
        label, tree = pending.pop()
        pointer = int(tree.as_pointer())
        if pointer in seen:
            continue
        seen.add(pointer)
        result.append((label, tree))
        nested_rows = []
        for node in tree.nodes:
            nested = getattr(node, "node_tree", None)
            if nested is not None:
                nested_rows.append((f"{label}/{node.name}", nested))
        pending.extend(sorted(nested_rows, key=lambda item: item[0], reverse=True))
    return tuple(result)


def _downstream_tokens(tree: Any, image_node: Any) -> frozenset[str]:
    """Collect socket/node names reachable from an image texture in one tree."""

    pending: list[tuple[Any, int]] = []
    for output in image_node.outputs:
        for link in output.links:
            pending.append((link, 0))
    seen_links: set[int] = set()
    found: set[str] = set()
    while pending:
        link, depth = pending.pop(0)
        pointer = int(link.as_pointer())
        if pointer in seen_links or depth > 12:
            continue
        seen_links.add(pointer)
        node = link.to_node
        found.update(_tokens(link.to_socket.name))
        found.update(_tokens(node.name))
        found.update(_tokens(getattr(node, "label", "")))
        found.update(_tokens(getattr(node, "bl_idname", "")))
        for output in node.outputs:
            for next_link in output.links:
                pending.append((next_link, depth + 1))
    return frozenset(found)


def _channel_role(tree: Any, node: Any, image: Any) -> str:
    downstream = _downstream_tokens(tree, node)
    labels = _tokens(
        " ".join(
            (
                str(getattr(node, "name", "")),
                str(getattr(node, "label", "")),
                str(getattr(image, "name", "")),
                Path(str(getattr(image, "filepath", "") or "")).name,
            )
        )
    )
    evidence = downstream | labels
    for role in _CHANNEL_PRIORITY:
        if evidence & _CHANNEL_ALIASES[role]:
            return role
    return "unclassified"


def _is_packed(image: Any) -> bool:
    if getattr(image, "packed_file", None) is not None:
        return True
    packed_files = getattr(image, "packed_files", None)
    return bool(packed_files)


def _inspection_issues(
    *,
    profile: str,
    output_surface_connected: bool,
    shader_node_count: int,
    image_texture_count: int,
    channels: Sequence[Mapping[str, Any]],
    unpacked_images: Sequence[str],
    texture_period_m: float | None,
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    def add(severity: str, code: str, detail: str) -> None:
        issues.append({"severity": severity, "code": code, "detail": detail})

    if not output_surface_connected:
        add("error", "surface_output_unconnected", "active Material Output has no surface link")
    if shader_node_count < 1:
        add("error", "shader_node_missing", "node graph contains no shader node")
    if profile == "texture_set" and image_texture_count < 1:
        add("error", "texture_set_without_images", "texture-set profile has no image textures")
    if profile == "texture_set" and texture_period_m is None:
        add(
            "warning",
            "texture_size_m_missing",
            "provider did not declare a positive real-world texture tile period",
        )
    if unpacked_images:
        add(
            "error",
            "external_images_unpacked",
            "normalized packages may not depend on external image paths: "
            + ", ".join(sorted(unpacked_images)),
        )
    for channel in channels:
        role = str(channel["role"])
        colorspace = str(channel["colorspace"])
        if role == "unclassified":
            add(
                "warning",
                "image_channel_unclassified",
                f"could not infer the role of image {channel['image_name']!r}",
            )
        if role in _SCALAR_CHANNELS and "non-color" not in colorspace.casefold():
            add(
                "warning",
                "scalar_channel_colorspace",
                f"{role} image {channel['image_name']!r} uses {colorspace!r}",
            )
        if role == "base_color" and "srgb" not in colorspace.casefold():
            add(
                "warning",
                "base_color_colorspace",
                f"base-color image {channel['image_name']!r} uses {colorspace!r}",
            )
    return sorted(issues, key=lambda row: (row["severity"], row["code"], row["detail"]))


def _inspect_material(material: Any, source: SourceMaterial, bpy: Any) -> Inspection:
    if material.node_tree is None:
        trees: tuple[tuple[str, Any], ...] = ()
    else:
        trees = _node_trees(material.node_tree)

    nodes = [(tree_path, tree, node) for tree_path, tree in trees for node in tree.nodes]
    image_rows: list[dict[str, Any]] = []
    unpacked: set[str] = set()
    for tree_path, tree, node in nodes:
        if getattr(node, "type", "") != "TEX_IMAGE" or node.image is None:
            continue
        image = node.image
        packed = _is_packed(image)
        image_name = str(image.name)
        if not packed:
            unpacked.add(image_name)
        image_rows.append(
            {
                "colorspace": str(image.colorspace_settings.name),
                "image_name": image_name,
                "node_path": f"{tree_path}/{node.name}",
                "packed": packed,
                "role": _channel_role(tree, node, image),
                "source_basename": Path(str(image.filepath or "")).name or None,
            }
        )
    image_rows.sort(
        key=lambda row: (
            str(row["role"]),
            str(row["image_name"]),
            str(row["node_path"]),
        )
    )
    image_rows = list({canonical_json_sha256(row): row for row in image_rows}.values())
    image_rows.sort(
        key=lambda row: (
            str(row["role"]),
            str(row["image_name"]),
            str(row["node_path"]),
        )
    )

    principled_count = sum(node.type == "BSDF_PRINCIPLED" for _, _, node in nodes)
    glass_count = sum(node.type == "BSDF_GLASS" for _, _, node in nodes)
    shader_count = sum(
        str(getattr(node, "type", "")).startswith("BSDF_")
        or getattr(node, "type", "")
        in {"ADD_SHADER", "EMISSION", "HOLDOUT", "MIX_SHADER", "SUBSURFACE_SCATTERING"}
        for _, _, node in nodes
    )
    procedural_count = sum(
        getattr(node, "type", "")
        in {
            "TEX_BRICK",
            "TEX_CHECKER",
            "TEX_GRADIENT",
            "TEX_MAGIC",
            "TEX_MUSGRAVE",
            "TEX_NOISE",
            "TEX_POINTDENSITY",
            "TEX_SKY",
            "TEX_VORONOI",
            "TEX_WAVE",
            "TEX_WHITE_NOISE",
        }
        for _, _, node in nodes
    )
    profile = material_profile(
        source.parameters,
        image_texture_count=len(image_rows),
        procedural_node_count=procedural_count,
    )
    period = texture_size_m(source.parameters)
    output_connected = _surface_connected(material)
    issues = _inspection_issues(
        profile=profile,
        output_surface_connected=output_connected,
        shader_node_count=shader_count,
        image_texture_count=len(image_rows),
        channels=image_rows,
        unpacked_images=tuple(unpacked),
        texture_period_m=period,
    )
    status = (
        "fail"
        if any(row["severity"] == "error" for row in issues)
        else "warn"
        if issues
        else "pass"
    )
    return {
        "material_profile": profile,
        "texture_size_m": period,
        "texture_size_source": (
            "source.parameters.textureSizeMeters" if period is not None else None
        ),
        "channels": image_rows,
        "channel_counts": dict(
            sorted(collections.Counter(str(row["role"]) for row in image_rows).items())
        ),
        "node_qa": {
            "status": status,
            "issues": issues,
            "node_tree_count": len(trees),
            "node_count": len(nodes),
            "output_surface_connected": output_connected,
            "principled_bsdf_count": principled_count,
            "glass_bsdf_count": glass_count,
            "shader_node_count": shader_count,
            "image_texture_count": len(image_rows),
            "procedural_texture_node_count": procedural_count,
            "packed_image_count": sum(bool(row["packed"]) for row in image_rows),
            "unpacked_image_count": len(unpacked),
        },
        "bpy_version": ".".join(str(value) for value in bpy.app.version),
    }


def _disconnect_true_displacement(material: Any) -> int:
    """Disconnect true displacement while leaving normal/bump branches intact."""

    if material.node_tree is None:
        return 0
    removed = 0
    for node in material.node_tree.nodes:
        if getattr(node, "type", "") != "OUTPUT_MATERIAL":
            continue
        displacement = node.inputs.get("Displacement")
        if displacement is None:
            continue
        for link in tuple(displacement.links):
            material.node_tree.links.remove(link)
            removed += 1
    return removed


def _force_opaque_alpha(material: Any) -> dict[str, Any]:
    """Repair the known Plain White Flat alpha wiring for ordinary opaque use."""

    links_removed = 0
    inputs_set = 0
    if material.node_tree is not None:
        for _tree_path, tree in _node_trees(material.node_tree):
            for node in tree.nodes:
                if getattr(node, "type", "") != "BSDF_PRINCIPLED":
                    continue
                alpha = node.inputs.get("Alpha")
                if alpha is None:
                    continue
                for link in tuple(alpha.links):
                    tree.links.remove(link)
                    links_removed += 1
                alpha.default_value = 1.0
                inputs_set += 1
    if hasattr(material, "diffuse_color"):
        material.diffuse_color[3] = 1.0
    render_setting = "alpha_one"
    if hasattr(material, "blend_method"):
        material.blend_method = "OPAQUE"
        render_setting = "OPAQUE"
    elif hasattr(material, "surface_render_method"):
        # Blender 4.2+ removed the OPAQUE enum.  Alpha=1 is opaque; DITHERED is
        # the non-blended surface path used when the property is available.
        material.surface_render_method = "DITHERED"
        render_setting = "DITHERED_with_alpha_one"
    return {
        "policy": "force_ordinary_opaque",
        "alpha_links_removed": links_removed,
        "principled_alpha_inputs_set": inputs_set,
        "alpha_value": 1.0,
        "render_setting": render_setting,
    }


def _clamp_bump_input(tree: Any, socket: Any, *, limit: float, suffix: str) -> str:
    if socket.is_linked:
        source_link = tuple(socket.links)[0]
        source_socket = source_link.from_socket
        tree.links.remove(source_link)
        clamp = tree.nodes.new("ShaderNodeMath")
        clamp.operation = "MINIMUM"
        clamp.name = f"Articraft {suffix} Limit"
        clamp.label = f"Articraft {suffix} <= {limit:g}"
        clamp.inputs[1].default_value = limit
        tree.links.new(source_socket, clamp.inputs[0])
        tree.links.new(clamp.outputs[0], socket)
        return "inserted_minimum_node"
    socket.default_value = min(float(socket.default_value), limit)
    return "clamped_default"


def _repair_native_cork(material: Any) -> dict[str, Any]:
    """Give the known cork group meter-like object coordinates and bounded bump."""

    vector_links_added = 0
    bump_repairs: list[dict[str, Any]] = []
    if material.node_tree is not None:
        root = material.node_tree
        texture_coordinate = None
        for node in root.nodes:
            if node.type == "TEX_COORD" and node.label == "Articraft Component Local Meters":
                texture_coordinate = node
                break
        for node in root.nodes:
            if getattr(node, "type", "") != "GROUP":
                continue
            vector = node.inputs.get("Vector")
            if vector is None or vector.is_linked:
                continue
            if texture_coordinate is None:
                texture_coordinate = root.nodes.new("ShaderNodeTexCoord")
                texture_coordinate.name = "Articraft Component Local Meters"
                texture_coordinate.label = "Articraft Component Local Meters"
            object_output = texture_coordinate.outputs.get("Object")
            if object_output is not None:
                root.links.new(object_output, vector)
                vector_links_added += 1
        for tree_path, tree in _node_trees(root):
            for node in tuple(tree.nodes):
                if getattr(node, "type", "") != "BUMP":
                    continue
                row: dict[str, Any] = {"node_path": f"{tree_path}/{node.name}"}
                strength = node.inputs.get("Strength")
                distance = node.inputs.get("Distance")
                if strength is not None:
                    row["strength"] = _clamp_bump_input(
                        tree, strength, limit=0.35, suffix="Cork Bump Strength"
                    )
                if distance is not None:
                    row["distance"] = _clamp_bump_input(
                        tree, distance, limit=0.002, suffix="Cork Bump Distance"
                    )
                bump_repairs.append(row)
    return {
        "policy": "component_local_meter_object_coordinates",
        "group_vector_links_added": vector_links_added,
        "coordinate_output": "TextureCoordinate.Object",
        "bump_strength_max": 0.35,
        "bump_distance_max_m": 0.002,
        "bump_repairs": bump_repairs,
    }


def _optical_policy(source: SourceMaterial) -> dict[str, Any] | None:
    normalized = _normalize_name(source.display_name)
    selected: tuple[float, str] | None = None
    for name, policy in _OPTICAL_IOR_POLICY.items():
        if name in normalized:
            selected = policy
            break
    if selected is None:
        return None
    observed_ior, risk = selected
    return {
        "coordinate_graph_policy": "preserve_source_object_graph",
        "observed_ior": observed_ior,
        "risk": risk,
        "optional_ior_clamp": {
            "enabled_by_default": False,
            "recommended_max": 1.60,
        },
    }


def _reopen_normalized_package(
    destination: Path,
    *,
    source: SourceMaterial,
    expected_profile: str,
    bpy: Any,
) -> dict[str, Any]:
    """Reopen a saved package and prove it is self-contained and identifiable."""

    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(destination), link=False) as (data_from, data_to):
        names = sorted(str(name) for name in data_from.materials if name)
        data_to.materials = list(names)
    materials = [material for material in data_to.materials if material is not None]
    issues: list[dict[str, str]] = []

    def add(code: str, detail: str) -> None:
        issues.append({"severity": "error", "code": code, "detail": detail})

    if len(materials) != 1:
        add(
            "normalized_material_count",
            f"expected exactly one Material datablock after reopen, found {len(materials)}",
        )
    material = materials[0] if len(materials) == 1 else None
    packed_images: set[str] = set()
    unpacked_images: set[str] = set()
    displacement_links = 0
    if material is not None:
        expected_properties = {
            "articraft_schema": NORMALIZED_PACKAGE_SCHEMA,
            "articraft_material_id": source.material_id,
            "articraft_material_profile": expected_profile,
            "articraft_true_displacement": "disconnected",
        }
        for key, expected in expected_properties.items():
            actual = material.get(key)
            if actual != expected:
                add("package_identity_mismatch", f"{key}={actual!r}, expected {expected!r}")
        if not _surface_connected(material):
            add("surface_output_unconnected", "reopened material has no active surface link")
        if material.node_tree is not None:
            for _tree_path, tree in _node_trees(material.node_tree):
                for node in tree.nodes:
                    if getattr(node, "type", "") == "TEX_IMAGE" and node.image is not None:
                        if _is_packed(node.image):
                            packed_images.add(str(node.image.name))
                        else:
                            unpacked_images.add(str(node.image.name))
                    if getattr(node, "type", "") == "OUTPUT_MATERIAL":
                        displacement = node.inputs.get("Displacement")
                        if displacement is not None:
                            displacement_links += len(displacement.links)
        if unpacked_images:
            add(
                "external_images_unpacked",
                "reopened package depends on external images: "
                + ", ".join(sorted(unpacked_images)),
            )
        if displacement_links:
            add(
                "true_displacement_reconnected",
                f"reopened package has {displacement_links} Material Output displacement links",
            )
    issues.sort(key=lambda row: (row["code"], row["detail"]))
    return {
        "status": "fail" if issues else "pass",
        "issues": issues,
        "material_count": len(materials),
        "material_names": names,
        "packed_image_count": len(packed_images),
        "unpacked_image_count": len(unpacked_images),
        "true_displacement_link_count": displacement_links,
    }


def _normalize_blend_package(source: SourceMaterial, destination: Path) -> Inspection:
    try:
        import bpy  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - exercised in Blender smoke runs
        raise RuntimeError("--execute must run in a Python environment that provides bpy") from exc

    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(source.raw_path), link=False) as (data_from, data_to):
        names = sorted(str(name) for name in data_from.materials if name)
        available_names = tuple(names)
        data_to.materials = list(names)
    selected = _choose_material(tuple(data_to.materials), source.display_name)
    selected_source_name = str(selected.name)
    source_displacement_links = 0
    if selected.node_tree is not None:
        for node in selected.node_tree.nodes:
            if getattr(node, "type", "") != "OUTPUT_MATERIAL":
                continue
            displacement = node.inputs.get("Displacement")
            if displacement is not None:
                source_displacement_links += len(displacement.links)
    removed_displacement_links = _disconnect_true_displacement(selected)
    normalized_name = _normalize_name(source.display_name)
    material_repairs: dict[str, Any] = {}
    if "cork with scratches and imperfections" in normalized_name:
        material_repairs["native_cork"] = _repair_native_cork(selected)
    if "plain white flat" in normalized_name:
        material_repairs["opaque_alpha"] = _force_opaque_alpha(selected)
    inspection = _inspect_material(selected, source, bpy)
    inspection["source_material_name"] = selected_source_name
    inspection["available_material_names"] = list(available_names)
    inspection["displacement_policy"] = {
        "policy": "disconnect_true_displacement",
        "source_output_link_count": source_displacement_links,
        "removed_output_link_count": removed_displacement_links,
        "normal_and_bump_preserved": True,
    }
    inspection["material_repairs"] = material_repairs
    inspection["optical_policy"] = _optical_policy(source)

    if inspection["node_qa"]["unpacked_image_count"]:
        raise ValueError(
            f"{source.material_id} contains unpacked external images; raw package kept unchanged"
        )
    identity = canonical_json_sha256(
        {"material_id": source.material_id, "source_sha256": source.raw_sha256}
    )[:16]
    selected.name = f"ArticraftPBR_{identity}"
    selected["articraft_schema"] = NORMALIZED_PACKAGE_SCHEMA
    selected["articraft_material_id"] = source.material_id
    selected["articraft_material_profile"] = inspection["material_profile"]
    selected["articraft_true_displacement"] = "disconnected"
    if inspection["texture_size_m"] is not None:
        selected["articraft_texture_size_m"] = float(inspection["texture_size_m"])
    # A normalized package intentionally contains a standalone Material
    # datablock and no scene object.  Keep it alive across orphan purge/save so
    # consumers can append it directly from the content-addressed .blend.
    selected.use_fake_user = True

    for material in tuple(bpy.data.materials):
        if material != selected:
            bpy.data.materials.remove(material)
    bpy.data.orphans_purge(do_recursive=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), check_existing=False, compress=True)
    if not destination.is_file() or destination.stat().st_size < 64:
        raise ValueError(f"Blender did not write normalized package: {destination}")
    package_reopen_qa = _reopen_normalized_package(
        destination,
        source=source,
        expected_profile=str(inspection["material_profile"]),
        bpy=bpy,
    )
    inspection["package_reopen_qa"] = package_reopen_qa
    if package_reopen_qa["status"] != "pass":
        raise ValueError(
            f"normalized package reopen QA failed for {source.material_id}: "
            f"{package_reopen_qa['issues']}"
        )
    return inspection


def _safe_output_root(library_root: Path, output_root: Path) -> Path:
    root = library_root.resolve(strict=True)
    output = output_root.resolve(strict=False)
    try:
        relative = output.relative_to(root)
    except ValueError as exc:
        raise ValueError("normalized output root must stay inside the source library root") from exc
    if not relative.parts or relative.parts[0] == "raw":
        raise ValueError("normalized output root must be separate from the raw source tree")
    return output


def _source_catalog_relative(catalog_path: Path, library_root: Path) -> str:
    source = catalog_path.resolve(strict=True)
    root = library_root.resolve(strict=True)
    try:
        return source.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("source catalog must stay inside the source library root") from exc


def _read_existing_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or not row.get("material_id"):
            raise ValueError(f"invalid normalized catalog row at {path}:{line_number}")
        rows.append(row)
    return rows


def _latest_catalog_path(output_root: Path) -> Path | None:
    """Resolve the mutable convenience pointer to an immutable snapshot."""

    pointer = output_root / "catalogs" / "latest.json"
    if pointer.is_file():
        payload = json.loads(pointer.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"invalid normalized catalog pointer: {pointer}")
        snapshot = str(payload.get("logical_snapshot_sha256") or "")
        if re.fullmatch(r"[0-9a-f]{64}", snapshot) is None:
            raise ValueError(f"invalid normalized catalog pointer digest: {pointer}")
        path = output_root / "catalogs" / snapshot / "materials.jsonl"
        if not path.is_file():
            raise ValueError(f"normalized catalog pointer target is missing: {path}")
        return path
    legacy = output_root / "catalog" / "materials.jsonl"
    return legacy if legacy.is_file() else None


def _runtime_profile(
    row: Mapping[str, Any],
    *,
    native_runtime_material_ids: frozenset[str],
) -> dict[str, Any]:
    """Compute the hard runtime qualification independently from semantic hints."""

    material_id = str(row.get("material_id") or "").strip()
    profile = str(row.get("material_profile") or "").strip()
    node_qa = row.get("node_qa")
    qa_status = str(node_qa.get("status") or "") if isinstance(node_qa, Mapping) else ""
    active = row.get("active") is True
    native_allowlisted = material_id in native_runtime_material_ids
    if not active:
        enabled = False
        reason = "technical_qa_inactive"
    elif qa_status != "pass":
        enabled = False
        reason = "runtime_requires_qa_pass"
    elif profile == "texture_set":
        enabled = True
        reason = "texture_set_qa_pass"
    elif profile == "native_procedural" and native_allowlisted:
        enabled = True
        reason = "native_procedural_explicit_allowlist"
    elif profile == "native_procedural":
        enabled = False
        reason = "native_procedural_not_allowlisted"
    else:
        enabled = False
        reason = "unsupported_material_profile"
    return {
        "enabled": enabled,
        "native_allowlisted": native_allowlisted,
        "policy_version": RUNTIME_PROFILE_POLICY_VERSION,
        "reason": reason,
    }


def _with_runtime_profile(
    row: Mapping[str, Any],
    *,
    native_runtime_material_ids: frozenset[str],
) -> dict[str, Any]:
    updated = dict(row)
    runtime_profile = _runtime_profile(
        updated,
        native_runtime_material_ids=native_runtime_material_ids,
    )
    updated["runtime_enabled"] = runtime_profile["enabled"]
    updated["runtime_profile"] = runtime_profile
    return updated


def _normalized_source_provenance(
    rows: Sequence[Mapping[str, Any]],
    *,
    fallback_catalog_path: str,
    fallback_catalog_sha256: str,
) -> tuple[str, str]:
    paths: set[str] = set()
    hashes: set[str] = set()
    for row in rows:
        provenance = row.get("provenance")
        if not isinstance(provenance, Mapping):
            continue
        path = str(provenance.get("catalog_path") or "").strip()
        digest = str(provenance.get("catalog_sha256") or "").strip()
        if path:
            paths.add(path)
        if re.fullmatch(r"[0-9a-f]{64}", digest):
            hashes.add(digest)
    if len(paths) == 1 and len(hashes) == 1:
        return next(iter(paths)), next(iter(hashes))
    return fallback_catalog_path, fallback_catalog_sha256


def snapshot_existing_normalized_catalog(
    *,
    catalog_path: Path,
    library_root: Path,
    execute: bool,
    native_runtime_material_ids: Iterable[str] = (),
) -> dict[str, Any]:
    """Migrate a legacy normalized catalog into an immutable snapshot.

    This is a metadata-only operation: existing packages and the source
    ``catalog/materials.jsonl`` are read and verified but never rewritten.
    """

    root = library_root.resolve(strict=True)
    source = catalog_path.resolve(strict=True)
    try:
        source_relative = source.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("normalized catalog must stay inside its library root") from exc
    rows = _read_existing_rows(source)
    known_ids = {str(row["material_id"]) for row in rows}
    native_ids = frozenset(
        str(value).strip() for value in native_runtime_material_ids if str(value).strip()
    )
    unknown = sorted(native_ids - known_ids)
    if unknown:
        raise ValueError(f"unknown native runtime allowlist material IDs: {unknown}")
    non_native = sorted(
        material_id
        for material_id in native_ids
        if next(
            str(row.get("material_profile") or "")
            for row in rows
            if str(row["material_id"]) == material_id
        )
        != "native_procedural"
    )
    if non_native:
        raise ValueError(f"native runtime allowlist contains non-native materials: {non_native}")

    migrated_rows: list[dict[str, Any]] = []
    for row in rows:
        material_id = str(row["material_id"])
        if row.get("schema_version") != NORMALIZED_CATALOG_SCHEMA:
            raise ValueError(f"legacy normalized row {material_id} has unsupported schema")
        if row.get("normalization_version") != NORMALIZER_VERSION:
            raise ValueError(f"legacy normalized row {material_id} has unsupported normalizer")
        for field in ("normalized_blend_path", "normalized_metadata_path"):
            relative = Path(str(row.get(field) or ""))
            if relative.is_absolute() or ".." in relative.parts or not relative.parts:
                raise ValueError(f"legacy normalized row {material_id} has unsafe {field}")
            target = (root / relative).resolve(strict=True)
            try:
                target.relative_to(root)
            except ValueError as exc:
                raise ValueError(
                    f"legacy normalized row {material_id} {field} escapes root"
                ) from exc
        blend_path = (root / str(row["normalized_blend_path"])).resolve(strict=True)
        if sha256_file(blend_path) != str(row.get("sha256") or ""):
            raise ValueError(f"legacy normalized row {material_id} package hash mismatch")
        migrated_rows.append(
            _with_runtime_profile(
                row,
                native_runtime_material_ids=native_ids,
            )
        )
    migrated_rows.sort(
        key=lambda row: (str(row.get("category_slug") or ""), str(row["material_id"]))
    )
    source_file_sha = sha256_file(source)
    raw_catalog_path, raw_catalog_sha = _normalized_source_provenance(
        migrated_rows,
        fallback_catalog_path=source_relative,
        fallback_catalog_sha256=source_file_sha,
    )
    allowlist_sha = native_runtime_allowlist_sha256(native_ids)
    summary: dict[str, Any] = {
        "mode": "execute" if execute else "dry_run",
        "migration": "legacy_normalized_catalog_to_immutable_snapshot",
        "source_catalog": source_relative,
        "source_catalog_sha256": source_file_sha,
        "raw_catalog": raw_catalog_path,
        "raw_catalog_sha256": raw_catalog_sha,
        "catalog_material_count": len(migrated_rows),
        "runtime_enabled_count": sum(row.get("runtime_enabled") is True for row in migrated_rows),
        "native_runtime_allowlist_sha256": allowlist_sha,
        "native_runtime_material_ids": sorted(native_ids),
        "packages_mutated": False,
        "source_catalog_mutated": False,
    }
    if not execute:
        return summary

    staging = Path(tempfile.mkdtemp(prefix=".snapshot-normalized-", dir=root))
    try:
        output_catalog, output_manifest, logical_sha, catalog_sha = _publish_catalog_snapshot(
            staging=staging,
            output=root,
            rows=migrated_rows,
            source_catalog_path=raw_catalog_path,
            source_catalog_sha256=raw_catalog_sha,
            native_allowlist_sha256=allowlist_sha,
        )
        summary.update(
            {
                "logical_snapshot_sha256": logical_sha,
                "output_catalog": output_catalog.relative_to(root).as_posix(),
                "output_catalog_sha256": catalog_sha,
                "output_manifest": output_manifest.relative_to(root).as_posix(),
                "output_manifest_sha256": sha256_file(output_manifest),
            }
        )
        return summary
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _validate_inspection(source: SourceMaterial, inspection: Mapping[str, Any]) -> None:
    profile = str(inspection.get("material_profile") or "")
    if profile not in MATERIAL_PROFILES:
        raise ValueError(f"{source.material_id} produced invalid material_profile {profile!r}")
    channels = inspection.get("channels")
    node_qa = inspection.get("node_qa")
    if not isinstance(channels, list) or not isinstance(node_qa, dict):
        raise ValueError(f"{source.material_id} inspection lacks channel/node QA")
    if node_qa.get("status") not in {"pass", "warn", "fail"}:
        raise ValueError(f"{source.material_id} inspection has invalid node QA status")
    if inspection.get("texture_size_m") is not None:
        value = float(inspection["texture_size_m"])
        if value <= 0.0:
            raise ValueError(f"{source.material_id} has non-positive texture_size_m")
    displacement = inspection.get("displacement_policy")
    if not isinstance(displacement, dict):
        raise ValueError(f"{source.material_id} inspection lacks displacement policy")
    if displacement.get("policy") != "disconnect_true_displacement":
        raise ValueError(f"{source.material_id} uses an unsupported displacement policy")
    if not isinstance(inspection.get("material_repairs", {}), dict):
        raise ValueError(f"{source.material_id} inspection has invalid material repairs")
    package_reopen_qa = inspection.get("package_reopen_qa")
    if not isinstance(package_reopen_qa, dict) or package_reopen_qa.get("status") not in {
        "pass",
        "fail",
    }:
        raise ValueError(f"{source.material_id} inspection lacks package reopen QA")


def _load_reusable_normalized_package(
    source: SourceMaterial,
    *,
    output: Path,
    package_relative: Path,
    metadata_relative: Path,
    allow_qa_failures: bool,
) -> tuple[dict[str, Any], str] | None:
    """Validate and reuse an existing immutable package without opening Blender.

    A content-addressed package is reusable only when both files exist and the
    metadata proves that it was produced from the same material/source bytes by
    the current normalization and shader-graph policies.  Any partial or stale
    package is a hard error: immutable paths are never repaired in place.
    """

    package_path = output / package_relative
    metadata_path = output / metadata_relative
    package_directory = package_path.parent
    if metadata_path.parent != package_directory:
        raise ValueError(f"normalized package paths diverge for {source.material_id}")
    if not package_directory.exists():
        return None
    _validate_package_directory(
        package_directory,
        context=f"append-only normalized package for {source.material_id}",
    )

    canonical_output = output.resolve(strict=True)
    for field, path in (("material.blend", package_path), ("metadata.json", metadata_path)):
        resolved = path.resolve(strict=True)
        try:
            resolved.relative_to(canonical_output)
        except ValueError as exc:
            raise ValueError(
                f"existing normalized {field} escapes output root for {source.material_id}"
            ) from exc
        if not resolved.is_file():
            raise ValueError(f"existing normalized {field} is not a file for {source.material_id}")

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"existing normalized metadata is invalid JSON for {source.material_id}: {exc}"
        ) from exc
    if not isinstance(metadata, dict):
        raise ValueError(f"existing normalized metadata is not an object for {source.material_id}")

    package = metadata.get("package")
    metadata_source = metadata.get("source")
    normalizer = metadata.get("normalizer")
    mapping = metadata.get("mapping_contract")
    node_qa = metadata.get("node_qa")
    eligibility = metadata.get("eligibility")
    channel_qa = metadata.get("channel_qa")
    displacement = metadata.get("displacement_policy")
    if not all(
        isinstance(value, dict)
        for value in (
            package,
            metadata_source,
            normalizer,
            mapping,
            node_qa,
            eligibility,
            channel_qa,
            displacement,
        )
    ):
        raise ValueError(
            f"existing normalized metadata lacks required contracts for {source.material_id}"
        )
    assert isinstance(package, dict)
    assert isinstance(metadata_source, dict)
    assert isinstance(normalizer, dict)
    assert isinstance(mapping, dict)
    assert isinstance(node_qa, dict)
    assert isinstance(eligibility, dict)
    assert isinstance(channel_qa, dict)
    assert isinstance(displacement, dict)

    compatibility = {
        "schema_version": (metadata.get("schema_version"), NORMALIZED_PACKAGE_SCHEMA),
        "material_id": (metadata.get("material_id"), source.material_id),
        "category_slug": (metadata.get("category_slug"), source.category_slug),
        "display_name": (metadata.get("display_name"), source.display_name),
        "source.blend_sha256": (metadata_source.get("blend_sha256"), source.raw_sha256),
        "source.provider": (metadata_source.get("provider"), source.provider),
        "source.asset_base_id": (metadata_source.get("asset_base_id"), source.asset_base_id),
        "package.blend_path": (package.get("blend_path"), package_relative.as_posix()),
        "normalizer.version": (normalizer.get("version"), NORMALIZER_VERSION),
        "normalizer.source_preserved": (normalizer.get("source_preserved"), True),
        "normalizer.shader_graph_policy": (
            normalizer.get("shader_graph_policy"),
            "provider_graph_preserved",
        ),
        "displacement_policy.policy": (
            displacement.get("policy"),
            "disconnect_true_displacement",
        ),
        "mapping_contract.coordinate_unit": (mapping.get("coordinate_unit"), "meter"),
        "mapping_contract.generic_box_projection_allowed": (
            mapping.get("generic_box_projection_allowed"),
            False,
        ),
        "mapping_contract.model_uvs_are_not_baked": (
            mapping.get("model_uvs_are_not_baked"),
            True,
        ),
    }
    for field, (actual, expected) in compatibility.items():
        if actual != expected:
            raise ValueError(
                f"existing normalized metadata is incompatible for {source.material_id}: "
                f"{field}={actual!r}, expected {expected!r}"
            )

    profile = str(metadata.get("material_profile") or "")
    if profile not in MATERIAL_PROFILES:
        raise ValueError(
            f"existing normalized metadata has invalid profile for {source.material_id}: {profile!r}"
        )
    profile_mapping = (
        {
            "mapping_profile": "metric_uv_tangent",
            "normal_space": "tangent",
            "requires_uv": True,
        }
        if profile == "texture_set"
        else {
            "mapping_profile": "native_node_graph",
            "normal_space": "native",
            "requires_uv": False,
        }
    )
    for field, expected in profile_mapping.items():
        if mapping.get(field) != expected:
            raise ValueError(
                f"existing normalized metadata is incompatible for {source.material_id}: "
                f"mapping_contract.{field}={mapping.get(field)!r}, expected {expected!r}"
            )
    qa_status = node_qa.get("status")
    if qa_status not in {"pass", "warn", "fail"}:
        raise ValueError(f"existing normalized metadata has invalid QA for {source.material_id}")
    if qa_status == "fail" and not allow_qa_failures:
        raise ValueError(
            f"existing normalized package failed QA for {source.material_id}; "
            "use --allow-qa-failures only for diagnostic catalogs"
        )
    tile_size_missing_quarantine = False
    if profile == "texture_set":
        tile_size = metadata.get("texture_size_m")
        mapping_tile_size = mapping.get("tile_size_m")
        if tile_size is None and mapping_tile_size is None:
            expected_reason = "texture set has no trustworthy real-world tile size"
            validation = eligibility.get("validation")
            restrictions = eligibility.get("restrictions")
            tile_size_missing_quarantine = (
                qa_status != "fail"
                and metadata.get("normalization_class") == "quarantine"
                and metadata.get("texture_size_source") is None
                and eligibility.get("active") is False
                and eligibility.get("eligible_for_generic") is False
                and eligibility.get("selection_scope") == "quarantined"
                and eligibility.get("quarantine_reason") == expected_reason
                and isinstance(restrictions, list)
                and "tile_size_missing" in restrictions
                and isinstance(validation, dict)
                and validation.get("active") is False
                and validation.get("status") == "quarantined"
                and validation.get("reasons") == [expected_reason]
            )
            if not tile_size_missing_quarantine:
                raise ValueError(
                    "existing texture-set metadata has an inconsistent tile-size-missing "
                    f"quarantine for {source.material_id}"
                )
        elif (
            isinstance(tile_size, bool)
            or not isinstance(tile_size, (int, float))
            or not math.isfinite(float(tile_size))
            or float(tile_size) <= 0.0
            or mapping_tile_size != tile_size
        ):
            raise ValueError(
                f"existing texture-set metadata has invalid tile size for {source.material_id}"
            )

    expected_active = qa_status != "fail" and not tile_size_missing_quarantine
    if eligibility.get("active") is not expected_active:
        raise ValueError(
            f"existing normalized eligibility/QA is inconsistent for {source.material_id}"
        )
    channels = channel_qa.get("channels")
    if not isinstance(channels, list):
        raise ValueError(f"existing normalized channel QA is invalid for {source.material_id}")
    reopen_qa = package.get("reopen_qa")
    if not isinstance(reopen_qa, dict) or reopen_qa.get("status") != "pass":
        raise ValueError(
            f"existing normalized package reopen QA is not pass for {source.material_id}"
        )

    expected_package_sha = str(package.get("blend_sha256") or "")
    if re.fullmatch(r"[0-9a-f]{64}", expected_package_sha) is None:
        raise ValueError(f"existing normalized metadata lacks package SHA for {source.material_id}")
    actual_package_sha = sha256_file(package_path)
    if actual_package_sha != expected_package_sha:
        raise ValueError(
            f"existing normalized package hash mismatch for {source.material_id}: "
            f"{actual_package_sha} != {expected_package_sha}"
        )
    return metadata, actual_package_sha


def _package_metadata(
    source: SourceMaterial,
    inspection: Mapping[str, Any],
    *,
    source_catalog_path: str,
    source_catalog_sha256: str,
    normalized_blend_path: Path,
    normalized_blend_sha256: str,
) -> dict[str, Any]:
    profile = str(inspection["material_profile"])
    period = inspection.get("texture_size_m")
    eligibility = generic_eligibility(
        display_name=source.display_name,
        category_slug=source.category_slug,
        profile=profile,
        tile_size_m=float(period) if period is not None else None,
        qa_status=str(inspection["node_qa"]["status"]),
    )
    normalization_class = (
        "quarantine"
        if eligibility["quarantine_reason"]
        else (
            "semantic_risk"
            if eligibility["semantic_risk_reason"]
            else "native"
            if profile == "native_procedural"
            else "normalizable"
        )
    )
    coordinate_source = "native_node_graph"
    if "native_cork" in inspection.get("material_repairs", {}):
        coordinate_source = "component_local_object_meters"
    elif source.category_slug == "glass":
        coordinate_source = "preserved_source_object_graph"
    return {
        "schema_version": NORMALIZED_PACKAGE_SCHEMA,
        "material_id": source.material_id,
        "category_slug": source.category_slug,
        "display_name": source.display_name,
        "material_profile": profile,
        "normalization_class": normalization_class,
        "texture_size_m": period,
        "texture_size_source": inspection.get("texture_size_source"),
        "mapping_contract": {
            "coordinate_unit": "meter",
            "mapping_profile": (
                "metric_uv_tangent" if profile == "texture_set" else "native_node_graph"
            ),
            "tile_size_m": period,
            "requires_uv": profile == "texture_set",
            "normal_space": "tangent" if profile == "texture_set" else "native",
            "coordinate_source": coordinate_source,
            "generic_box_projection_allowed": False,
            "model_uvs_are_not_baked": True,
        },
        "eligibility": eligibility,
        "displacement_policy": inspection["displacement_policy"],
        "material_repairs": inspection.get("material_repairs", {}),
        "optical_policy": inspection.get("optical_policy"),
        "channel_qa": {
            "channels": inspection["channels"],
            "channel_counts": inspection.get("channel_counts", {}),
        },
        "node_qa": inspection["node_qa"],
        "package": {
            "blend_path": normalized_blend_path.as_posix(),
            "blend_sha256": normalized_blend_sha256,
            "bpy_version": inspection.get("bpy_version"),
            "source_material_name": inspection.get("source_material_name"),
            "available_material_names": inspection.get("available_material_names", []),
            "reopen_qa": inspection["package_reopen_qa"],
        },
        "source": {
            "provider": source.provider,
            "license": source.license,
            "asset_base_id": source.asset_base_id,
            "catalog_path": source_catalog_path,
            "catalog_sha256": source_catalog_sha256,
            "catalog_row_sha256": source.row_sha256,
            "blend_path": source.raw_relative_path.as_posix(),
            "blend_sha256": source.raw_sha256,
        },
        "normalizer": {
            "version": NORMALIZER_VERSION,
            "source_preserved": True,
            "shader_graph_policy": "provider_graph_preserved",
        },
    }


def _catalog_row(
    source: SourceMaterial,
    metadata: Mapping[str, Any],
    *,
    normalized_blend_path: Path,
    normalized_metadata_path: Path,
    normalized_blend_sha256: str,
) -> dict[str, Any]:
    source_payload = source.row.get("source")
    source_payload = dict(source_payload) if isinstance(source_payload, dict) else {}
    source_payload.setdefault("asset_base_id", source.asset_base_id)
    source_payload.setdefault("category", source.category_slug)
    tags = source_payload.get("tags") or source.row.get("tags") or []
    return {
        "schema_version": NORMALIZED_CATALOG_SCHEMA,
        "material_id": source.material_id,
        "category_slug": source.category_slug,
        "display_name": source.display_name,
        "provider": source.provider,
        "license": source.license,
        "asset_base_id": source.asset_base_id,
        "tags": tags,
        "source": source_payload,
        "normalized_blend_path": normalized_blend_path.as_posix(),
        "normalized_metadata_path": normalized_metadata_path.as_posix(),
        "sha256": normalized_blend_sha256,
        "material_profile": metadata["material_profile"],
        "normalization_class": metadata["normalization_class"],
        "texture_size_m": metadata["texture_size_m"],
        "mapping_contract": metadata["mapping_contract"],
        "eligibility": metadata["eligibility"],
        "eligible_for_generic": metadata["eligibility"]["eligible_for_generic"],
        "restrictions": metadata["eligibility"]["restrictions"],
        "quarantine_reason": metadata["eligibility"]["quarantine_reason"],
        "normalization_version": metadata["normalizer"]["version"],
        "channels": metadata["channel_qa"]["channels"],
        "displacement_policy": metadata["displacement_policy"],
        "material_repairs": metadata["material_repairs"],
        "optical_policy": metadata["optical_policy"],
        "package_reopen_qa": metadata["package"]["reopen_qa"],
        "active": metadata["eligibility"]["active"],
        "validation": metadata["eligibility"]["validation"],
        "selection_scope": metadata["eligibility"]["selection_scope"],
        "allowed_component_roles": metadata["eligibility"]["allowed_component_roles"],
        "excluded_component_roles": metadata["eligibility"]["excluded_component_roles"],
        "material_subtype": metadata["eligibility"]["material_subtype"],
        "qa_flags": metadata["eligibility"]["qa_flags"],
        "recommended_use": metadata["eligibility"]["recommended_use"],
        "semantic_advisories": metadata["eligibility"]["semantic_advisories"],
        "recommended_component_roles": metadata["eligibility"]["recommended_component_roles"],
        "semantic_risk_reason": metadata["eligibility"]["semantic_risk_reason"],
        "channel_qa": metadata["channel_qa"],
        "node_qa": metadata["node_qa"],
        "provenance": metadata["source"],
        "normalizer": metadata["normalizer"],
    }


def _commit_staged_file(staged: Path, destination: Path) -> bool:
    """Publish one package file append-only; return whether a new file was added."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if not destination.is_file() or sha256_file(destination) != sha256_file(staged):
            raise FileExistsError(
                "append-only normalized target already exists with different content: "
                f"{destination}"
            )
        staged.unlink()
        return False
    os.replace(staged, destination)
    return True


_PACKAGE_FILENAMES = frozenset({"material.blend", "metadata.json"})


def _validate_package_directory(directory: Path, *, context: str) -> dict[str, Path]:
    """Require one ordinary, self-contained normalized package directory."""

    if directory.is_symlink() or not directory.is_dir():
        raise FileExistsError(f"{context} is not an ordinary directory: {directory}")
    entries = {entry.name: entry for entry in directory.iterdir()}
    if set(entries) != _PACKAGE_FILENAMES:
        raise FileExistsError(
            f"{context} must contain exactly {sorted(_PACKAGE_FILENAMES)}; "
            f"found {sorted(entries)} at {directory}"
        )
    for name, path in entries.items():
        if path.is_symlink() or not path.is_file():
            raise FileExistsError(f"{context} {name} is not an ordinary file: {path}")
    return entries


def _commit_staged_package_directory(
    *,
    staged_package: Path,
    staged_metadata: Path,
    destination_package: Path,
    destination_metadata: Path,
) -> tuple[int, int]:
    """Publish one immutable package pair with a single directory rename.

    The rename occurs within the normalized output filesystem.  A concurrent
    publisher may win the destination race; in that case every file must be
    present and byte-identical before the staged directory is discarded.
    """

    staged_directory = staged_package.parent
    destination_directory = destination_package.parent
    if (
        staged_metadata.parent != staged_directory
        or destination_metadata.parent != destination_directory
        or staged_package.name != "material.blend"
        or destination_package.name != "material.blend"
        or staged_metadata.name != "metadata.json"
        or destination_metadata.name != "metadata.json"
    ):
        raise ValueError("normalized package publication paths do not form one package pair")
    staged_entries = _validate_package_directory(
        staged_directory,
        context="staged normalized package",
    )
    destination_directory.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.rename(staged_directory, destination_directory)
        return 2, 0
    except OSError:
        if not destination_directory.exists():
            raise

    destination_entries = _validate_package_directory(
        destination_directory,
        context="append-only normalized package",
    )
    for name in sorted(_PACKAGE_FILENAMES):
        if sha256_file(destination_entries[name]) != sha256_file(staged_entries[name]):
            raise FileExistsError(
                "append-only normalized package already exists with different content: "
                f"{destination_entries[name]}"
            )
    shutil.rmtree(staged_directory)
    return 0, 2


def _publish_catalog_snapshot(
    *,
    staging: Path,
    output: Path,
    rows: Sequence[Mapping[str, Any]],
    source_catalog_path: str,
    source_catalog_sha256: str,
    native_allowlist_sha256: str,
) -> tuple[Path, Path, str, str]:
    """Atomically publish a content-addressed immutable catalog snapshot.

    Independent CLI transactions must use a single catalog writer.  Internal
    ``--workers`` only produce package directories and never call this helper.
    """

    staged_snapshot = staging / "catalog-snapshot"
    staged_catalog = staged_snapshot / "materials.jsonl"
    atomic_jsonl(staged_catalog, rows)
    catalog_file_sha256 = sha256_file(staged_catalog)
    logical_snapshot_sha256 = logical_catalog_snapshot_sha256(
        catalog_file_sha256=catalog_file_sha256,
        raw_catalog_sha256=source_catalog_sha256,
        native_allowlist_sha256=native_allowlist_sha256,
    )
    manifest = {
        "schema_version": NORMALIZED_CATALOG_MANIFEST_SCHEMA,
        "logical_snapshot_sha256": logical_snapshot_sha256,
        "materials_file": {
            "material_count": len(rows),
            "path": "materials.jsonl",
            "sha256": catalog_file_sha256,
        },
        "native_runtime_allowlist_sha256": native_allowlist_sha256,
        "normalizer_version": NORMALIZER_VERSION,
        "raw_catalog": {
            "path": source_catalog_path,
            "sha256": source_catalog_sha256,
        },
        "runtime_profile_policy_version": RUNTIME_PROFILE_POLICY_VERSION,
    }
    staged_manifest = staged_snapshot / "manifest.json"
    atomic_json(staged_manifest, manifest)

    destination = output / "catalogs" / logical_snapshot_sha256
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        expected = {
            "materials.jsonl": staged_catalog,
            "manifest.json": staged_manifest,
        }
        for name, staged_path in expected.items():
            published = destination / name
            if not published.is_file() or published.read_bytes() != staged_path.read_bytes():
                raise FileExistsError(
                    f"immutable catalog snapshot collision at {destination / name}"
                )
        shutil.rmtree(staged_snapshot)
    else:
        os.replace(staged_snapshot, destination)

    catalog_path = destination / "materials.jsonl"
    manifest_path = destination / "manifest.json"
    atomic_json(
        output / "catalogs" / "latest.json",
        {
            "catalog_path": catalog_path.relative_to(output).as_posix(),
            "logical_snapshot_sha256": logical_snapshot_sha256,
            "manifest_path": manifest_path.relative_to(output).as_posix(),
        },
    )
    return (
        catalog_path,
        manifest_path,
        logical_snapshot_sha256,
        catalog_file_sha256,
    )


def normalize_library(
    *,
    catalog_path: Path,
    library_root: Path,
    output_root: Path,
    execute: bool,
    material_ids: Iterable[str] = (),
    limit: int | None = None,
    overwrite: bool = False,
    allow_qa_failures: bool = False,
    workers: int = 1,
    continue_on_error: bool = False,
    normalizer: Normalizer | None = None,
    native_runtime_material_ids: Iterable[str] = (),
) -> dict[str, Any]:
    """Plan or execute a deterministic normalized-library transaction."""

    if isinstance(workers, bool) or workers < 1:
        raise ValueError("workers must be a positive integer")
    if normalizer is not None and workers != 1:
        raise ValueError("injected normalizer requires workers=1")

    root = library_root.resolve(strict=True)
    output = _safe_output_root(root, output_root)
    source_catalog_relative = _source_catalog_relative(catalog_path, root)
    source_catalog_hash = sha256_file(catalog_path.resolve(strict=True))
    all_records = list(load_source_catalog(catalog_path, library_root=root))
    native_runtime_ids = frozenset(
        str(value).strip() for value in native_runtime_material_ids if str(value).strip()
    )
    known_material_ids = {record.material_id for record in all_records}
    unknown_native_ids = sorted(native_runtime_ids - known_material_ids)
    if unknown_native_ids:
        raise ValueError(f"unknown native runtime allowlist material IDs: {unknown_native_ids}")
    profiles_by_id = {record.material_id: record.planned_profile for record in all_records}
    non_native_ids = sorted(
        material_id
        for material_id in native_runtime_ids
        if profiles_by_id[material_id] != "native_procedural"
    )
    if non_native_ids:
        raise ValueError(
            f"native runtime allowlist contains non-native materials: {non_native_ids}"
        )
    native_allowlist_hash = native_runtime_allowlist_sha256(native_runtime_ids)
    records = list(all_records)
    requested = tuple(
        dict.fromkeys(str(value).strip() for value in material_ids if str(value).strip())
    )
    if requested:
        requested_set = set(requested)
        missing = sorted(requested_set - known_material_ids)
        if missing:
            raise ValueError(f"unknown --material-id values: {missing}")
        records = [record for record in records if record.material_id in requested_set]
    if limit is not None:
        if limit < 1:
            raise ValueError("limit must be positive")
        records = records[:limit]

    profile_counts = collections.Counter(record.planned_profile for record in records)
    texture_size_missing = sum(
        record.planned_profile == "texture_set" and record.declared_texture_size_m is None
        for record in records
    )
    package_plan: list[tuple[SourceMaterial, Path, Path, tuple[dict[str, Any], str] | None]] = []
    for source in records:
        package_relative, metadata_relative = normalized_package_paths(
            material_id=source.material_id,
            category_slug=source.category_slug,
            source_sha256=source.raw_sha256,
        )
        reusable = _load_reusable_normalized_package(
            source,
            output=output,
            package_relative=package_relative,
            metadata_relative=metadata_relative,
            allow_qa_failures=allow_qa_failures,
        )
        package_plan.append((source, package_relative, metadata_relative, reusable))
    planned_reused_count = sum(reusable is not None for *_, reusable in package_plan)
    summary: dict[str, Any] = {
        "mode": "execute" if execute else "dry_run",
        "normalizer_version": NORMALIZER_VERSION,
        "source_catalog": source_catalog_relative,
        "source_catalog_sha256": source_catalog_hash,
        "selected_count": len(records),
        "planned_profile_counts": dict(sorted(profile_counts.items())),
        "planned_texture_size_missing": texture_size_missing,
        "planned_reused_normalized_count": planned_reused_count,
        "planned_normalizer_call_count": len(package_plan) - planned_reused_count,
        "workers": workers,
        "continue_on_error": continue_on_error,
        "output_root": output.relative_to(root).as_posix(),
        "output_catalog_pattern": (
            output / "catalogs" / "<logical_snapshot_sha256>" / "materials.jsonl"
        )
        .relative_to(root)
        .as_posix(),
        "native_runtime_allowlist_sha256": native_allowlist_hash,
        "native_runtime_material_ids": sorted(native_runtime_ids),
        "packages_append_only": True,
        "catalog_publication_single_writer_required": True,
        "overwrite_requested_but_packages_remain_append_only": bool(overwrite),
        "raw_sources_mutated": False,
    }
    if not execute:
        return summary

    output.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".normalize-pbr-", dir=output))
    staged: list[tuple[Path, Path, Path, Path]] = []
    rows_by_index: dict[int, dict[str, Any]] = {}
    normalized_rows_by_index: dict[int, dict[str, Any]] = {}
    failures_by_index: dict[int, dict[str, str]] = {}
    reused_normalized_count = 0
    newly_published_package_files = 0
    reused_package_files = 0

    def record_failure(index: int, source: SourceMaterial, exc: Exception) -> None:
        message = str(exc).replace(str(staging), "<staging>")
        failures_by_index[index] = {
            "material_id": source.material_id,
            "category_slug": source.category_slug,
            "error_type": type(exc).__name__,
            "message": message,
        }

    def process_inspection(
        index: int,
        source: SourceMaterial,
        package_relative: Path,
        metadata_relative: Path,
        inspection: Mapping[str, Any],
    ) -> None:
        nonlocal newly_published_package_files, reused_package_files
        staged_package = staging / package_relative
        _validate_inspection(source, inspection)
        qa_status = str(inspection["node_qa"]["status"])
        if qa_status == "fail" and not allow_qa_failures:
            raise ValueError(
                f"node QA failed for {source.material_id}; "
                "use --allow-qa-failures only for diagnostic catalogs"
            )
        if not staged_package.is_file():
            raise ValueError(f"normalizer did not write package for {source.material_id}")
        normalized_hash = sha256_file(staged_package)
        metadata = _package_metadata(
            source,
            inspection,
            source_catalog_path=source_catalog_relative,
            source_catalog_sha256=source_catalog_hash,
            normalized_blend_path=package_relative,
            normalized_blend_sha256=normalized_hash,
        )
        staged_metadata = staging / metadata_relative
        atomic_json(staged_metadata, metadata)
        publication = (
            staged_package,
            staged_metadata,
            output / package_relative,
            output / metadata_relative,
        )
        if continue_on_error:
            added, reused = _commit_staged_package_directory(
                staged_package=publication[0],
                staged_metadata=publication[1],
                destination_package=publication[2],
                destination_metadata=publication[3],
            )
            newly_published_package_files += added
            reused_package_files += reused
        else:
            staged.append(publication)
        row = _catalog_row(
            source,
            metadata,
            normalized_blend_path=package_relative,
            normalized_metadata_path=metadata_relative,
            normalized_blend_sha256=normalized_hash,
        )
        rows_by_index[index] = row
        normalized_rows_by_index[index] = row

    try:
        work: list[tuple[int, SourceMaterial, Path, Path]] = []
        for index, (source, package_relative, metadata_relative, reusable) in enumerate(
            package_plan
        ):
            if reusable is not None:
                metadata, normalized_hash = reusable
                rows_by_index[index] = _catalog_row(
                    source,
                    metadata,
                    normalized_blend_path=package_relative,
                    normalized_metadata_path=metadata_relative,
                    normalized_blend_sha256=normalized_hash,
                )
                reused_normalized_count += 1
                continue
            work.append((index, source, package_relative, metadata_relative))

        if workers == 1:
            normalize_one = normalizer or _normalize_blend_package
            for index, source, package_relative, metadata_relative in work:
                try:
                    inspection = normalize_one(source, staging / package_relative)
                    process_inspection(
                        index, source, package_relative, metadata_relative, inspection
                    )
                except Exception as exc:
                    if not continue_on_error:
                        raise
                    record_failure(index, source, exc)
        else:
            context = multiprocessing.get_context("spawn")
            with concurrent.futures.ProcessPoolExecutor(
                max_workers=workers,
                mp_context=context,
            ) as executor:
                futures = {
                    executor.submit(
                        _normalize_blend_package,
                        source,
                        staging / package_relative,
                    ): (index, source, package_relative, metadata_relative)
                    for index, source, package_relative, metadata_relative in work
                }
                for future in concurrent.futures.as_completed(futures):
                    index, source, package_relative, metadata_relative = futures[future]
                    try:
                        inspection = future.result()
                        process_inspection(
                            index, source, package_relative, metadata_relative, inspection
                        )
                    except Exception as exc:
                        if not continue_on_error:
                            for pending in futures:
                                pending.cancel()
                            raise
                        record_failure(index, source, exc)

        new_rows = [rows_by_index[index] for index in sorted(rows_by_index)]
        normalized_rows = [
            normalized_rows_by_index[index] for index in sorted(normalized_rows_by_index)
        ]
        failures = [failures_by_index[index] for index in sorted(failures_by_index)]

        latest_catalog = _latest_catalog_path(output)
        existing_rows = _read_existing_rows(latest_catalog) if latest_catalog is not None else []
        existing_by_id = {str(row["material_id"]): row for row in existing_rows}
        failed_material_ids = {row["material_id"] for row in failures}
        for material_id in failed_material_ids:
            existing_by_id.pop(material_id, None)
        existing_by_id.update({str(row["material_id"]): row for row in new_rows})
        merged_rows = sorted(
            (
                _with_runtime_profile(
                    row,
                    native_runtime_material_ids=native_runtime_ids,
                )
                for row in existing_by_id.values()
            ),
            key=lambda row: (str(row.get("category_slug") or ""), str(row["material_id"])),
        )
        for staged_package, staged_metadata, destination_package, destination_metadata in staged:
            added, reused = _commit_staged_package_directory(
                staged_package=staged_package,
                staged_metadata=staged_metadata,
                destination_package=destination_package,
                destination_metadata=destination_metadata,
            )
            newly_published_package_files += added
            reused_package_files += reused

        failure_report_path: Path | None = None
        failure_report_sha256: str | None = None
        if continue_on_error:
            failure_report = {
                "schema_version": "articraft-pbr-normalization-failures/v1",
                "source_catalog": source_catalog_relative,
                "source_catalog_sha256": source_catalog_hash,
                "selected_count": len(records),
                "failure_count": len(failures),
                "failures": failures,
            }
            failure_report_digest = canonical_json_sha256(failure_report)
            failure_report_path = (
                output / "reports" / "normalization_failures" / f"{failure_report_digest}.json"
            )
            staged_failure_report = staging / "normalization_failures.json"
            atomic_json(staged_failure_report, failure_report)
            _commit_staged_file(staged_failure_report, failure_report_path)
            failure_report_sha256 = sha256_file(failure_report_path)
        all_normalizer_calls_failed = bool(work) and len(failures) == len(work)
        published_existing_only = all_normalizer_calls_failed and not new_rows and bool(merged_rows)
        if all_normalizer_calls_failed and not new_rows and not merged_rows:
            report_hint = (
                failure_report_path.relative_to(root).as_posix()
                if failure_report_path is not None
                else "unavailable"
            )
            raise RuntimeError(
                "all selected material normalizations failed; no normalized catalog "
                f"snapshot was published; failure report: {report_hint}"
            )
        (
            output_catalog,
            output_manifest,
            logical_snapshot_sha256,
            output_catalog_sha256,
        ) = _publish_catalog_snapshot(
            staging=staging,
            output=output,
            rows=merged_rows,
            source_catalog_path=source_catalog_relative,
            source_catalog_sha256=source_catalog_hash,
            native_allowlist_sha256=native_allowlist_hash,
        )
        summary.update(
            {
                "normalized_count": len(normalized_rows),
                "reused_normalized_count": reused_normalized_count,
                "normalization_failure_count": len(failures),
                "normalization_failures": failures,
                "normalization_failures_path": (
                    failure_report_path.relative_to(root).as_posix()
                    if failure_report_path is not None
                    else None
                ),
                "normalization_failures_sha256": failure_report_sha256,
                "accounted_selected_count": (
                    reused_normalized_count + len(normalized_rows) + len(failures)
                ),
                "all_normalizer_calls_failed": all_normalizer_calls_failed,
                "published_existing_only": published_existing_only,
                "catalog_material_count": len(merged_rows),
                "runtime_enabled_count": sum(
                    row.get("runtime_enabled") is True for row in merged_rows
                ),
                "newly_published_package_files": newly_published_package_files,
                "reused_package_files": reused_package_files,
                "preexisting_reused_package_files": reused_normalized_count * 2,
                "normalized_profile_counts": dict(
                    sorted(
                        collections.Counter(
                            str(row["material_profile"]) for row in normalized_rows
                        ).items()
                    )
                ),
                "qa_status_counts": dict(
                    sorted(
                        collections.Counter(
                            str(row["node_qa"]["status"]) for row in normalized_rows
                        ).items()
                    )
                ),
                "package_reopen_status_counts": dict(
                    sorted(
                        collections.Counter(
                            str(row["package_reopen_qa"]["status"]) for row in normalized_rows
                        ).items()
                    )
                ),
                "normalization_class_counts": dict(
                    sorted(
                        collections.Counter(
                            str(row["normalization_class"]) for row in normalized_rows
                        ).items()
                    )
                ),
                "logical_snapshot_sha256": logical_snapshot_sha256,
                "output_catalog": output_catalog.relative_to(root).as_posix(),
                "output_catalog_sha256": output_catalog_sha256,
                "output_manifest": output_manifest.relative_to(root).as_posix(),
                "output_manifest_sha256": sha256_file(output_manifest),
            }
        )
        return summary
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True, help="raw catalog JSONL")
    parser.add_argument(
        "--library-root",
        type=Path,
        default=None,
        help="source library root (default: catalog parent parent)",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="separate normalized tree (default: LIBRARY_ROOT/normalized)",
    )
    parser.add_argument("--material-id", action="append", default=[])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--snapshot-existing-normalized",
        action="store_true",
        help=(
            "metadata-only migration of an existing normalized catalog into an immutable "
            "catalogs/<logical-sha>/ snapshot"
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "compatibility flag only; content-addressed packages and catalog snapshots "
            "remain append-only and are never overwritten"
        ),
    )
    parser.add_argument("--allow-qa-failures", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument(
        "--native-runtime-material-id",
        action="append",
        default=[],
        help=(
            "explicitly qualify one native_procedural material for zero-token runtime; "
            "repeat for multiple IDs"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    catalog = args.catalog.expanduser().resolve(strict=True)
    root = (
        args.library_root.expanduser().resolve(strict=True)
        if args.library_root is not None
        else catalog.parent.parent.resolve(strict=True)
    )
    if args.snapshot_existing_normalized:
        if args.output_root is not None or args.material_id or args.limit is not None:
            raise ValueError(
                "--snapshot-existing-normalized does not accept --output-root, --material-id, "
                "or --limit"
            )
        summary = snapshot_existing_normalized_catalog(
            catalog_path=catalog,
            library_root=root,
            execute=bool(args.execute),
            native_runtime_material_ids=args.native_runtime_material_id,
        )
    else:
        output = (
            args.output_root.expanduser() if args.output_root is not None else root / "normalized"
        )
        summary = normalize_library(
            catalog_path=catalog,
            library_root=root,
            output_root=output,
            execute=bool(args.execute),
            material_ids=args.material_id,
            limit=args.limit,
            overwrite=bool(args.overwrite),
            allow_qa_failures=bool(args.allow_qa_failures),
            workers=args.workers,
            continue_on_error=bool(args.continue_on_error),
            native_runtime_material_ids=args.native_runtime_material_id,
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if not args.execute:
        print("Dry run only. Add --execute to inspect and write packages.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
