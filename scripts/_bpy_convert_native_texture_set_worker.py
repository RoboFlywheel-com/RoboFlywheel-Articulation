#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Convert conservatively eligible native materials into packed texture sets.

The worker reads one batch JSON object from stdin and emits one prefixed JSON
result per material.  A malformed or unsupported material fails independently;
the source package is never modified and an output is published only after all
four 1K maps and reopen QA succeed.
"""

from __future__ import annotations

import collections
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Mapping, Sequence

JOB_SCHEMA = "articraft-native-texture-conversion-job/v1"
RESULT_SCHEMA = "articraft-native-texture-conversion-result/v1"
METADATA_SCHEMA = "articraft-normalized-material-package/v1"
NORMALIZER_VERSION = "articraft-pbr-normalizer/v1"
CONVERSION_VERSION = "articraft-native-texture-converter/v1"
RESULT_PREFIX = "ARTICRAFT_NATIVE_TEXTURE_CONVERT\t"
SAFE_DECISION = "reusable_texture_set"
RESOLUTION = 1024
UV_LAYER_NAME = "ArticraftCanonicalUV"
CHANNELS = ("base_color", "metallic", "roughness", "normal")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")

_PROCEDURAL_TEXTURE_TYPES = frozenset(
    {
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
)
_ALLOWED_LINKED_PRINCIPLED_INPUTS = frozenset({"Base Color", "Metallic", "Roughness", "Normal"})
_UNSUPPORTED_PRINCIPLED_WEIGHTS = (
    "Anisotropic",
    "Anisotropic IOR Level",
    "Clearcoat",
    "Coat Weight",
    "Sheen",
    "Sheen Weight",
    "Subsurface",
    "Subsurface Weight",
    "Thin Film Weight",
    "Transmission",
    "Transmission Weight",
)
_FORBIDDEN_LINKED_NODE_TYPES = frozenset(
    {
        "AMBIENT_OCCLUSION",
        "ATTRIBUTE",
        "BEVEL",
        "BSDF_GLASS",
        "BSDF_HAIR",
        "BSDF_HAIR_PRINCIPLED",
        "BSDF_REFRACTION",
        "CAMERA",
        "FRESNEL",
        "GEOMETRY",
        "GROUP",
        "HAIR_INFO",
        "HOLDOUT",
        "LAYER_WEIGHT",
        "LIGHT_PATH",
        "NEW_GEOMETRY",
        "NORMAL",
        "OBJECT_INFO",
        "PARTICLE_INFO",
        "POINT_INFO",
        "SCRIPT",
        "TANGENT",
        "TEX_ENVIRONMENT",
        "TEX_IES",
        "TEX_POINTDENSITY",
        "TEX_SKY",
        "VECT_TRANSFORM",
        "VECTOR_TRANSFORM",
        "VERTEX_COLOR",
        "VOLUME_ABSORPTION",
        "VOLUME_INFO",
        "VOLUME_PRINCIPLED",
        "VOLUME_SCATTER",
    }
)
_SIMPLE_LINKED_NODE_TYPES = frozenset(
    {
        "BSDF_PRINCIPLED",
        "MAPPING",
        "NORMAL_MAP",
        "OUTPUT_MATERIAL",
        "TEX_COORD",
        "TEX_IMAGE",
        "UVMAP",
    }
)


class ConversionFailure(RuntimeError):
    def __init__(self, *codes: str) -> None:
        super().__init__(", ".join(codes))
        self.codes = tuple(sorted(set(codes))) or ("conversion_failure",)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def safe_relative_path(value: object, *, field: str) -> Path:
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
        raise ValueError(f"{field} must be a safe POSIX relative path")
    return Path(*posix.parts)


def _contained(root: Path, relative: Path, *, must_exist: bool) -> Path:
    candidate = (root / relative).resolve(strict=must_exist)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("path escapes workspace_root") from exc
    return candidate


def _require_sha256(value: object, *, field: str) -> str:
    text = str(value or "")
    if _SHA256_RE.fullmatch(text) is None:
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return text


def prepare_job(raw: Mapping[str, Any], workspace_root: Path) -> dict[str, Any]:
    material_id = str(raw.get("material_id") or "").strip()
    if not material_id:
        raise ValueError("material_id is required")
    if raw.get("eligibility_decision") != SAFE_DECISION:
        raise ValueError("eligibility_decision must be reusable_texture_set")
    source_relative = safe_relative_path(raw.get("source_blend_path"), field="source_blend_path")
    output_relative = safe_relative_path(raw.get("output_dir"), field="output_dir")
    source = _contained(workspace_root, source_relative, must_exist=True)
    output = _contained(workspace_root, output_relative, must_exist=False)
    if not source.is_file():
        raise ValueError("source_blend_path is not a file")
    if output == source or output in source.parents:
        raise ValueError("output_dir overlaps the source package")
    tile_size = raw.get("texture_size_m")
    if not isinstance(tile_size, (int, float)) or not math.isfinite(float(tile_size)):
        raise ValueError("texture_size_m must be finite")
    if float(tile_size) <= 0.0:
        raise ValueError("texture_size_m must be positive")
    job = {
        "material_id": material_id,
        "display_name": str(raw.get("display_name") or ""),
        "category_slug": str(raw.get("category_slug") or ""),
        "source_blend_path": source_relative.as_posix(),
        "source_blend_sha256": _require_sha256(
            raw.get("source_blend_sha256"), field="source_blend_sha256"
        ),
        "output_dir": output_relative.as_posix(),
        "texture_size_m": float(tile_size),
        "catalog_sha256": _require_sha256(raw.get("catalog_sha256"), field="catalog_sha256"),
        "eligibility_input_sha256": _require_sha256(
            raw.get("eligibility_input_sha256"), field="eligibility_input_sha256"
        ),
        "eligibility_decision": SAFE_DECISION,
        "_source": source,
        "_output": output,
    }
    job["conversion_input_sha256"] = canonical_sha256(
        {
            "conversion_version": CONVERSION_VERSION,
            **{k: v for k, v in job.items() if not k.startswith("_")},
        }
    )
    return job


def graph_failure_codes(facts: Mapping[str, Any]) -> list[str]:
    """Pure conservative rule engine used by the bpy scan and unit tests."""

    failures: list[str] = []
    if facts.get("material_count") != 1:
        failures.append("material_count_not_one")
    if not facts.get("has_node_tree"):
        failures.append("material_has_no_node_tree")
    if facts.get("active_output_count") != 1 or facts.get("connected_surface_output_count") != 1:
        failures.append("surface_output_not_unique")
    if facts.get("surface_terminal_type") != "BSDF_PRINCIPLED":
        failures.append("surface_not_direct_single_principled")
    if int(facts.get("procedural_texture_node_count") or 0):
        failures.append("procedural_texture_present")
    if int(facts.get("volume_link_count") or 0):
        failures.append("volume_output_connected")
    if int(facts.get("displacement_link_count") or 0):
        failures.append("displacement_output_connected")
    if facts.get("animated_or_driven"):
        failures.append("animated_or_driven_graph")
    if facts.get("alpha_linked") or not facts.get("alpha_opaque"):
        failures.append("surface_not_opaque")
    if facts.get("emission_linked") or facts.get("emission_nonzero"):
        failures.append("emission_not_zero")
    if facts.get("unsupported_principled_inputs"):
        failures.append("nonstandard_principled_input")
    if facts.get("forbidden_linked_node_types"):
        failures.append("complex_or_component_dependent_node")
    if facts.get("complex_linked_node_types"):
        failures.append("complex_linked_node_graph")
    if facts.get("non_simple_standard_channel_sources"):
        failures.append("standard_channel_source_not_direct_image")
    if facts.get("normal_input_not_simple_tangent_normal_map"):
        failures.append("normal_input_not_simple_tangent_normal_map")
    if int(facts.get("unused_image_node_count") or 0):
        failures.append("unused_or_ambiguous_image_node")
    if int(facts.get("unpacked_image_count") or 0):
        failures.append("source_image_not_packed")
    if int(facts.get("nonstatic_image_count") or 0):
        failures.append("source_image_not_static_file_or_tiled")
    if int(facts.get("nonflat_image_count") or 0):
        failures.append("source_image_projection_not_flat")
    if int(facts.get("nonrepeat_image_count") or 0):
        failures.append("source_image_extension_not_repeat")
    if int(facts.get("non_uv_image_coordinate_count") or 0):
        failures.append("source_image_coordinate_not_uv_or_unlinked")
    return sorted(set(failures))


def _is_packed(image: Any) -> bool:
    return getattr(image, "packed_file", None) is not None or bool(
        getattr(image, "packed_files", None)
    )


def _has_animation(owner: Any) -> bool:
    animation = getattr(owner, "animation_data", None)
    return bool(animation and (getattr(animation, "action", None) or animation.drivers))


def _input_active(socket: Any) -> bool:
    if socket.is_linked:
        return True
    value = getattr(socket, "default_value", 0.0)
    if isinstance(value, (int, float)):
        return math.isfinite(float(value)) and abs(float(value)) > 1e-6
    return bool(value)


def _emission_nonzero(principled: Any) -> tuple[bool, bool]:
    color = principled.inputs.get("Emission Color") or principled.inputs.get("Emission")
    strength = principled.inputs.get("Emission Strength")
    linked = bool((color and color.is_linked) or (strength and strength.is_linked))
    color_value = tuple(getattr(color, "default_value", (0.0, 0.0, 0.0, 1.0)))
    strength_value = float(getattr(strength, "default_value", 1.0))
    nonzero = strength_value > 1e-6 and any(abs(float(value)) > 1e-6 for value in color_value[:3])
    return linked, nonzero


def _default_vector(socket: Any) -> tuple[float, ...]:
    return tuple(float(value) for value in socket.default_value)


def _mapping_is_identity(node: Any) -> bool:
    expected = {
        "Location": (0.0, 0.0, 0.0),
        "Rotation": (0.0, 0.0, 0.0),
        "Scale": (1.0, 1.0, 1.0),
    }
    for name, wanted in expected.items():
        socket = node.inputs.get(name)
        if socket is None or socket.is_linked:
            return False
        actual = _default_vector(socket)
        if len(actual) < 3 or any(abs(actual[index] - wanted[index]) > 1e-6 for index in range(3)):
            return False
    return True


def _socket_is_direct_uv(socket: Any, *, allow_identity_mapping: bool = True) -> bool:
    if len(socket.links) != 1:
        return False
    source = socket.links[0].from_socket
    node = source.node
    if node.type == "UVMAP":
        return True
    if node.type == "TEX_COORD":
        return str(source.name).strip().casefold() == "uv"
    if node.type == "MAPPING" and allow_identity_mapping and _mapping_is_identity(node):
        vector = node.inputs.get("Vector")
        return bool(
            vector
            and vector.is_linked
            and _socket_is_direct_uv(vector, allow_identity_mapping=False)
        )
    return False


def _coordinate_is_strict_uv(node: Any) -> bool:
    vector = node.inputs.get("Vector")
    return bool(vector and vector.is_linked and _socket_is_direct_uv(vector))


def inspect_source_package(bpy: Any, source: Path) -> tuple[Any | None, dict[str, Any]]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(source), link=False) as (data_from, data_to):
        names = sorted(str(name) for name in data_from.materials if name)
        data_to.materials = names
    materials = [material for material in data_to.materials if material is not None]
    facts: dict[str, Any] = {"material_count": len(materials)}
    if len(materials) != 1:
        facts["has_node_tree"] = False
        return None, facts
    material = materials[0]
    facts["has_node_tree"] = bool(material.use_nodes and material.node_tree is not None)
    if not facts["has_node_tree"]:
        return material, facts
    tree = material.node_tree
    nodes = list(tree.nodes)
    active_outputs = [
        node
        for node in nodes
        if node.type == "OUTPUT_MATERIAL" and getattr(node, "is_active_output", True)
    ]
    connected = [
        node
        for node in active_outputs
        if node.inputs.get("Surface") is not None and node.inputs["Surface"].is_linked
    ]
    terminal = None
    if len(connected) == 1 and len(connected[0].inputs["Surface"].links) == 1:
        terminal = connected[0].inputs["Surface"].links[0].from_node
        while terminal is not None and terminal.type == "REROUTE":
            terminal = (
                terminal.inputs[0].links[0].from_node if terminal.inputs[0].is_linked else None
            )
    principled = terminal if terminal is not None and terminal.type == "BSDF_PRINCIPLED" else None
    unsupported: list[str] = []
    alpha_linked = False
    alpha_opaque = False
    emission_linked = False
    emission_nonzero = False
    if principled is not None:
        for socket in principled.inputs:
            if socket.is_linked and socket.name not in _ALLOWED_LINKED_PRINCIPLED_INPUTS:
                unsupported.append(f"{socket.name}:linked")
        for name in _UNSUPPORTED_PRINCIPLED_WEIGHTS:
            socket = principled.inputs.get(name)
            if socket is not None and _input_active(socket):
                unsupported.append(name)
        alpha = principled.inputs.get("Alpha")
        alpha_linked = bool(alpha and alpha.is_linked)
        alpha_opaque = bool(
            alpha is not None
            and not alpha.is_linked
            and abs(float(alpha.default_value) - 1.0) <= 1e-6
        )
        emission_linked, emission_nonzero = _emission_nonzero(principled)
    used_image_nodes: set[int] = set()
    non_simple_sources: list[str] = []
    normal_not_simple = False
    if principled is not None:
        for name in ("Base Color", "Metallic", "Roughness"):
            socket = principled.inputs.get(name)
            if socket is None or not socket.is_linked:
                continue
            if (
                len(socket.links) != 1
                or socket.links[0].from_node.type != "TEX_IMAGE"
                or socket.links[0].from_socket.name != "Color"
            ):
                non_simple_sources.append(name)
            else:
                used_image_nodes.add(int(socket.links[0].from_node.as_pointer()))
        normal = principled.inputs.get("Normal")
        if normal is not None and normal.is_linked:
            normal_map = normal.links[0].from_node if len(normal.links) == 1 else None
            color = normal_map.inputs.get("Color") if normal_map is not None else None
            strength = normal_map.inputs.get("Strength") if normal_map is not None else None
            if (
                normal_map is None
                or normal_map.type != "NORMAL_MAP"
                or str(getattr(normal_map, "space", "")) != "TANGENT"
                or strength is None
                or strength.is_linked
                or abs(float(strength.default_value) - 1.0) > 1e-6
                or color is None
                or len(color.links) != 1
                or color.links[0].from_node.type != "TEX_IMAGE"
                or color.links[0].from_socket.name != "Color"
            ):
                normal_not_simple = True
            else:
                used_image_nodes.add(int(color.links[0].from_node.as_pointer()))
    linked_types = {
        str(node.type)
        for node in nodes
        if any(socket.is_linked for socket in node.inputs)
        or any(socket.is_linked for socket in node.outputs)
    }
    images = [node for node in nodes if node.type == "TEX_IMAGE"]
    volume_links = sum(
        len(node.inputs["Volume"].links)
        for node in active_outputs
        if node.inputs.get("Volume") is not None
    )
    displacement_links = sum(
        len(node.inputs["Displacement"].links)
        for node in active_outputs
        if node.inputs.get("Displacement") is not None
    )
    facts.update(
        {
            "active_output_count": len(active_outputs),
            "connected_surface_output_count": len(connected),
            "surface_terminal_type": getattr(terminal, "type", None),
            "procedural_texture_node_count": sum(
                node.type in _PROCEDURAL_TEXTURE_TYPES for node in nodes
            ),
            "volume_link_count": volume_links,
            "displacement_link_count": displacement_links,
            "animated_or_driven": _has_animation(material) or _has_animation(tree),
            "alpha_linked": alpha_linked,
            "alpha_opaque": alpha_opaque,
            "emission_linked": emission_linked,
            "emission_nonzero": emission_nonzero,
            "unsupported_principled_inputs": sorted(set(unsupported)),
            "forbidden_linked_node_types": sorted(linked_types & _FORBIDDEN_LINKED_NODE_TYPES),
            "complex_linked_node_types": sorted(linked_types - _SIMPLE_LINKED_NODE_TYPES),
            "non_simple_standard_channel_sources": sorted(non_simple_sources),
            "normal_input_not_simple_tangent_normal_map": normal_not_simple,
            "image_texture_count": len(images),
            "unused_image_node_count": sum(
                int(node.as_pointer()) not in used_image_nodes for node in images
            ),
            "unpacked_image_count": sum(
                node.image is None or not _is_packed(node.image) for node in images
            ),
            "nonstatic_image_count": sum(
                node.image is None or node.image.source not in {"FILE", "TILED"} for node in images
            ),
            "nonflat_image_count": sum(
                str(getattr(node, "projection", "")).upper() != "FLAT" for node in images
            ),
            "nonrepeat_image_count": sum(
                str(getattr(node, "extension", "")).upper() != "REPEAT" for node in images
            ),
            "non_uv_image_coordinate_count": sum(
                not _coordinate_is_strict_uv(node) for node in images
            ),
            "node_type_counts": dict(
                sorted(collections.Counter(node.type for node in nodes).items())
            ),
        }
    )
    facts["_principled"] = principled
    return material, facts


def _canonical_plane(bpy: Any) -> Any:
    mesh = bpy.data.meshes.new("ArticraftCanonicalBakePlane")
    mesh.from_pydata(
        [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)],
        [],
        [(0, 1, 2, 3)],
    )
    mesh.update()
    uv = mesh.uv_layers.new(name=UV_LAYER_NAME)
    coordinates = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
    for loop in mesh.loops:
        uv.data[loop.index].uv = coordinates[loop.vertex_index]
    obj = bpy.data.objects.new("ArticraftCanonicalBakePlane", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj


def _bind_images_to_uv(tree: Any) -> None:
    coordinate = tree.nodes.new("ShaderNodeUVMap")
    coordinate.name = "Articraft Canonical UV"
    coordinate.uv_map = UV_LAYER_NAME
    for node in tree.nodes:
        if node.type != "TEX_IMAGE":
            continue
        vector = node.inputs.get("Vector")
        if vector is None:
            raise ConversionFailure("source_image_has_no_vector_input")
        for link in tuple(vector.links):
            tree.links.remove(link)
        tree.links.new(coordinate.outputs["UV"], vector)
        node.projection = "FLAT"
        node.extension = "REPEAT"


def _configure_bake_scene(bpy: Any) -> None:
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 1
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"


def _new_target_image(bpy: Any, channel: str) -> Any:
    image = bpy.data.images.new(
        f"Articraft_{channel}_1K",
        width=RESOLUTION,
        height=RESOLUTION,
        alpha=True,
        float_buffer=False,
    )
    image.colorspace_settings.name = "sRGB" if channel == "base_color" else "Non-Color"
    image["articraft_channel"] = channel
    image["articraft_resolution"] = RESOLUTION
    return image


def _activate_target_node(tree: Any, image: Any) -> Any:
    for node in tree.nodes:
        node.select = False
    target = tree.nodes.new("ShaderNodeTexImage")
    target.name = f"Articraft Bake Target {image['articraft_channel']}"
    target.image = image
    target.select = True
    tree.nodes.active = target
    return target


def _bake_scalar_or_color(
    bpy: Any, material: Any, principled: Any, channel: str, image: Any
) -> None:
    tree = material.node_tree
    output = next(
        node
        for node in tree.nodes
        if node.type == "OUTPUT_MATERIAL" and getattr(node, "is_active_output", True)
    )
    surface = output.inputs["Surface"]
    original = surface.links[0].from_socket
    source_name = {"base_color": "Base Color", "metallic": "Metallic", "roughness": "Roughness"}[
        channel
    ]
    source_input = principled.inputs[source_name]
    target = _activate_target_node(tree, image)
    emission = tree.nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 1.0
    if source_input.is_linked:
        tree.links.new(source_input.links[0].from_socket, emission.inputs["Color"])
    else:
        value = source_input.default_value
        if isinstance(value, (int, float)):
            emission.inputs["Color"].default_value = (float(value), float(value), float(value), 1.0)
        else:
            emission.inputs["Color"].default_value = tuple(value)
    for link in tuple(surface.links):
        tree.links.remove(link)
    tree.links.new(emission.outputs["Emission"], surface)
    try:
        bpy.ops.object.bake(
            type="EMIT",
            margin=8,
            use_selected_to_active=False,
            use_clear=True,
            uv_layer=UV_LAYER_NAME,
        )
    finally:
        for link in tuple(surface.links):
            tree.links.remove(link)
        tree.links.new(original, surface)
        tree.nodes.remove(emission)
        tree.nodes.remove(target)


def _bake_normal(bpy: Any, material: Any, image: Any) -> None:
    tree = material.node_tree
    target = _activate_target_node(tree, image)
    try:
        bpy.ops.object.bake(
            type="NORMAL",
            normal_space="TANGENT",
            normal_r="POS_X",
            normal_g="POS_Y",
            normal_b="POS_Z",
            margin=8,
            use_selected_to_active=False,
            use_clear=True,
            uv_layer=UV_LAYER_NAME,
        )
    finally:
        tree.nodes.remove(target)


def _write_pack_maps(images: Mapping[str, Any], temp_dir: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for channel in CHANNELS:
        image = images[channel]
        path = temp_dir / f"{channel}.png"
        image.filepath_raw = str(path)
        image.file_format = "PNG"
        image.save()
        if not path.is_file() or path.stat().st_size < 16:
            raise ConversionFailure("baked_png_missing")
        png_sha256 = sha256_file(path)
        image.pack()
        if not _is_packed(image):
            raise ConversionFailure("baked_image_pack_failed")
        rows[channel] = {
            "image_name": str(image.name),
            "colorspace": str(image.colorspace_settings.name),
            "packed": True,
            "png_sha256": png_sha256,
            "resolution": [RESOLUTION, RESOLUTION],
        }
    return rows


def _build_derived_material(bpy: Any, job: Mapping[str, Any], images: Mapping[str, Any]) -> Any:
    identity = hashlib.sha256(str(job["material_id"]).encode("utf-8")).hexdigest()[:16]
    material = bpy.data.materials.new(f"ArticraftTextureSet_{identity}")
    material.use_nodes = True
    tree = material.node_tree
    tree.nodes.clear()
    output = tree.nodes.new("ShaderNodeOutputMaterial")
    principled = tree.nodes.new("ShaderNodeBsdfPrincipled")
    uv = tree.nodes.new("ShaderNodeUVMap")
    uv.uv_map = UV_LAYER_NAME
    tree.links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    normal_map = tree.nodes.new("ShaderNodeNormalMap")
    normal_map.space = "TANGENT"
    # Leave this empty so Blender follows the active UV map that the runtime
    # creates (ArticraftMetricUV); the canonical plane exists only during bake.
    normal_map.uv_map = ""
    for channel in CHANNELS:
        node = tree.nodes.new("ShaderNodeTexImage")
        node.name = f"Articraft {channel}"
        node.image = images[channel]
        node.projection = "FLAT"
        node.extension = "REPEAT"
        tree.links.new(uv.outputs["UV"], node.inputs["Vector"])
        if channel == "base_color":
            tree.links.new(node.outputs["Color"], principled.inputs["Base Color"])
        elif channel == "metallic":
            tree.links.new(node.outputs["Color"], principled.inputs["Metallic"])
        elif channel == "roughness":
            tree.links.new(node.outputs["Color"], principled.inputs["Roughness"])
        else:
            tree.links.new(node.outputs["Color"], normal_map.inputs["Color"])
            tree.links.new(normal_map.outputs["Normal"], principled.inputs["Normal"])
    material["articraft_schema"] = METADATA_SCHEMA
    material["articraft_material_id"] = str(job["material_id"])
    material["articraft_material_profile"] = "texture_set"
    material["articraft_texture_size_m"] = float(job["texture_size_m"])
    material["articraft_true_displacement"] = "disconnected"
    material.use_fake_user = True
    return material


def _purge_to_derived(bpy: Any, derived: Any) -> None:
    for obj in tuple(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for material in tuple(bpy.data.materials):
        if material != derived:
            bpy.data.materials.remove(material)
    bpy.data.orphans_purge(do_recursive=True)


def _reopen_qa(bpy: Any, blend_path: Path, expected_material_id: str) -> dict[str, Any]:
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))
    materials = list(bpy.data.materials)
    issues: list[str] = []
    packed_channels: list[str] = []
    unpacked = 0
    displacement = 0
    surface_connected = False
    if len(materials) != 1:
        issues.append("reopen_material_count_not_one")
    else:
        material = materials[0]
        if not material.use_fake_user:
            issues.append("reopen_material_fake_user_missing")
        if material.get("articraft_schema") != METADATA_SCHEMA:
            issues.append("reopen_material_schema_mismatch")
        if material.get("articraft_material_id") != expected_material_id:
            issues.append("reopen_material_identity_mismatch")
        if material.node_tree is None:
            issues.append("reopen_node_tree_missing")
        else:
            for node in material.node_tree.nodes:
                if node.type == "OUTPUT_MATERIAL" and getattr(node, "is_active_output", True):
                    surface = node.inputs.get("Surface")
                    surface_connected = bool(surface and surface.is_linked)
                    socket = node.inputs.get("Displacement")
                    displacement += len(socket.links) if socket is not None else 0
                if node.type == "TEX_IMAGE" and node.image is not None:
                    channel = str(node.image.get("articraft_channel") or "")
                    if not _is_packed(node.image):
                        unpacked += 1
                    if str(getattr(node, "projection", "")).upper() != "FLAT":
                        issues.append("reopen_image_projection_not_flat")
                    if str(getattr(node, "extension", "")).upper() != "REPEAT":
                        issues.append("reopen_image_extension_not_repeat")
                    if channel:
                        packed_channels.append(channel)
            normal_maps = [node for node in material.node_tree.nodes if node.type == "NORMAL_MAP"]
            if len(normal_maps) != 1 or str(normal_maps[0].uv_map or ""):
                issues.append("reopen_normal_map_contract_mismatch")
    if bpy.data.objects:
        issues.append("reopen_objects_present")
    if not surface_connected:
        issues.append("reopen_surface_unconnected")
    if unpacked:
        issues.append("reopen_unpacked_images")
    if displacement:
        issues.append("reopen_displacement_connected")
    if sorted(packed_channels) != sorted(CHANNELS):
        issues.append("reopen_channel_set_mismatch")
    return {
        "status": "pass" if not issues else "fail",
        "issues": sorted(set(issues)),
        "material_count": len(materials),
        "material_fake_user": bool(len(materials) == 1 and materials[0].use_fake_user),
        "object_count": len(bpy.data.objects),
        "surface_connected": surface_connected,
        "unpacked_image_count": unpacked,
        "displacement_link_count": displacement,
        "channels": sorted(packed_channels),
    }


def _metadata(
    job: Mapping[str, Any],
    *,
    channel_rows: Mapping[str, Any],
    blend_sha256: str,
    qa: Mapping[str, Any],
    bpy_version: str,
) -> dict[str, Any]:
    output = Path(str(job["output_dir"]))
    channel_qa_rows = [
        {
            "colorspace": channel_rows[channel]["colorspace"],
            "image_name": channel_rows[channel]["image_name"],
            "node_path": f"root/Articraft {channel}",
            "packed": True,
            "role": channel,
            "source_basename": None,
        }
        for channel in CHANNELS
    ]
    eligibility = {
        "active": True,
        "allowed_component_roles": [],
        "eligible_for_generic": True,
        "excluded_component_roles": [],
        "material_subtype": None,
        "qa_flags": ["derived_from_safe_native"],
        "quarantine_reason": None,
        "recommended_component_roles": [],
        "recommended_use": [],
        "restrictions": [
            "requires_metric_uv",
            "tangent_space_normal",
            "true_displacement_disabled",
        ],
        "selection_scope": "generic",
        "semantic_advisories": [],
        "semantic_risk_reason": None,
        "validation": {"active": True, "reasons": [], "status": "active"},
    }
    node_qa = {
        "glass_bsdf_count": 0,
        "image_texture_count": len(CHANNELS),
        "issues": [],
        "node_count": 8,
        "node_tree_count": 1,
        "output_surface_connected": True,
        "packed_image_count": len(CHANNELS),
        "principled_bsdf_count": 1,
        "procedural_texture_node_count": 0,
        "shader_node_count": 1,
        "status": "pass",
        "unpacked_image_count": 0,
    }
    mapping_contract = {
        "coordinate_source": "baked_canonical_uv",
        "coordinate_unit": "meter",
        "generic_box_projection_allowed": False,
        "mapping_profile": "metric_uv_tangent",
        "model_uvs_are_not_baked": True,
        "normal_space": "tangent",
        "requires_uv": True,
        "tile_size_m": job["texture_size_m"],
    }
    displacement_policy = {
        "normal_and_bump_preserved": True,
        "policy": "disconnect_true_displacement",
        "removed_output_link_count": 0,
        "source_output_link_count": 0,
    }
    return {
        "schema_version": METADATA_SCHEMA,
        "material_id": job["material_id"],
        "display_name": job["display_name"],
        "category_slug": job["category_slug"],
        "material_profile": "texture_set",
        "source": {
            "blend_path": job["source_blend_path"],
            "blend_sha256": job["source_blend_sha256"],
            "catalog_sha256": job["catalog_sha256"],
            "eligibility_input_sha256": job["eligibility_input_sha256"],
        },
        "normalizer": {
            "version": NORMALIZER_VERSION,
            "source_preserved": False,
            "shader_graph_policy": "derived_texture_set_from_safe_native",
        },
        "converter": {
            "version": CONVERSION_VERSION,
            "bpy_version": bpy_version,
            "conversion_input_sha256": job["conversion_input_sha256"],
        },
        "derivation": {
            "kind": "native_procedural_to_texture_set",
            "source_material_profile": "native_procedural",
            "eligibility_decision": SAFE_DECISION,
        },
        "bake": {
            "resolution": [RESOLUTION, RESOLUTION],
            "uv_layer": UV_LAYER_NAME,
            "uv_layout": "canonical_unit_plane",
            "channels": list(CHANNELS),
            "true_displacement": False,
        },
        "texture_size_m": job["texture_size_m"],
        "texture_size_source": "derived_from_source_texture_size_m",
        "normalization_class": "derived_texture_set",
        "mapping_contract": mapping_contract,
        "displacement_policy": displacement_policy,
        "eligibility": eligibility,
        "node_qa": node_qa,
        "channel_qa": {
            "channel_counts": {channel: 1 for channel in CHANNELS},
            "channels": channel_qa_rows,
        },
        "material_repairs": {},
        "optical_policy": None,
        "channels": channel_qa_rows,
        "baked_channels": dict(channel_rows),
        "package": {
            "blend_path": (output / "material.blend").as_posix(),
            "blend_sha256": blend_sha256,
            "metadata_path": (output / "metadata.json").as_posix(),
        },
        "reopen_qa": dict(qa),
    }


def convert_one(bpy: Any, workspace_root: Path, job: Mapping[str, Any]) -> dict[str, Any]:
    source = job["_source"]
    output = job["_output"]
    assert isinstance(source, Path) and isinstance(output, Path)
    if output.exists():
        raise ConversionFailure("output_dir_already_exists")
    source_before = sha256_file(source)
    if source_before != job["source_blend_sha256"]:
        raise ConversionFailure("source_blend_sha256_mismatch")
    material, facts = inspect_source_package(bpy, source)
    failures = graph_failure_codes(facts)
    if failures:
        raise ConversionFailure(*failures)
    assert material is not None
    principled = facts.pop("_principled")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.staging-", dir=output.parent))
    try:
        temp_maps = staging / "_temp_maps"
        temp_maps.mkdir()
        _configure_bake_scene(bpy)
        plane = _canonical_plane(bpy)
        plane.data.materials.append(material)
        _bind_images_to_uv(material.node_tree)
        images = {channel: _new_target_image(bpy, channel) for channel in CHANNELS}
        for channel in ("base_color", "metallic", "roughness"):
            _bake_scalar_or_color(bpy, material, principled, channel, images[channel])
        _bake_normal(bpy, material, images["normal"])
        channel_rows = _write_pack_maps(images, temp_maps)
        derived = _build_derived_material(bpy, job, images)
        _purge_to_derived(bpy, derived)
        blend_path = staging / "material.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False, compress=True)
        if not blend_path.is_file() or blend_path.stat().st_size < 64:
            raise ConversionFailure("derived_blend_missing")
        shutil.rmtree(temp_maps)
        qa = _reopen_qa(bpy, blend_path, str(job["material_id"]))
        if qa["status"] != "pass":
            raise ConversionFailure(*qa["issues"])
        blend_sha256 = sha256_file(blend_path)
        bpy_version = ".".join(str(value) for value in bpy.app.version)
        metadata = _metadata(
            job,
            channel_rows=channel_rows,
            blend_sha256=blend_sha256,
            qa=qa,
            bpy_version=bpy_version,
        )
        metadata_path = staging / "metadata.json"
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        metadata_sha256 = sha256_file(metadata_path)
        if sha256_file(source) != source_before:
            raise ConversionFailure("source_blend_changed")
        os.replace(staging, output)
        return {
            "schema_version": RESULT_SCHEMA,
            "conversion_version": CONVERSION_VERSION,
            "status": "success",
            "failure_codes": [],
            "material_id": job["material_id"],
            "source_blend_path": job["source_blend_path"],
            "source_blend_sha256": source_before,
            "catalog_sha256": job["catalog_sha256"],
            "eligibility_input_sha256": job["eligibility_input_sha256"],
            "conversion_input_sha256": job["conversion_input_sha256"],
            "bpy_version": bpy_version,
            "resolution": [RESOLUTION, RESOLUTION],
            "channels": list(CHANNELS),
            "output": {
                "blend_path": (Path(str(job["output_dir"])) / "material.blend").as_posix(),
                "blend_sha256": blend_sha256,
                "metadata_path": (Path(str(job["output_dir"])) / "metadata.json").as_posix(),
                "metadata_sha256": metadata_sha256,
            },
            "reopen_qa": qa,
        }
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)


def failure_result(
    raw: Mapping[str, Any], codes: Sequence[str], *, bpy_version: str
) -> dict[str, Any]:
    source_path = str(raw.get("source_blend_path") or "")
    if source_path.startswith("/") or ".." in PurePosixPath(source_path).parts:
        source_path = ""
    return {
        "schema_version": RESULT_SCHEMA,
        "conversion_version": CONVERSION_VERSION,
        "status": "failure",
        "failure_codes": sorted(set(str(code) for code in codes)),
        "material_id": str(raw.get("material_id") or ""),
        "source_blend_path": source_path,
        "source_blend_sha256": str(raw.get("source_blend_sha256") or ""),
        "catalog_sha256": str(raw.get("catalog_sha256") or ""),
        "eligibility_input_sha256": str(raw.get("eligibility_input_sha256") or ""),
        "conversion_input_sha256": None,
        "bpy_version": bpy_version,
        "resolution": [RESOLUTION, RESOLUTION],
        "channels": [],
        "output": None,
        "reopen_qa": None,
    }


def _overlapping_outputs(prepared: Sequence[tuple[int, Mapping[str, Any]]]) -> set[int]:
    conflicts: set[int] = set()
    for position, (index, first) in enumerate(prepared):
        first_path = first["_output"]
        assert isinstance(first_path, Path)
        for other_index, second in prepared[position + 1 :]:
            second_path = second["_output"]
            assert isinstance(second_path, Path)
            if (
                first_path == second_path
                or first_path in second_path.parents
                or second_path in first_path.parents
            ):
                conflicts.update({index, other_index})
    return conflicts


def main() -> int:
    import bpy  # type: ignore[import-not-found]

    bpy_version = ".".join(str(value) for value in bpy.app.version)
    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON job: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != JOB_SCHEMA:
        raise SystemExit(f"job must use schema_version {JOB_SCHEMA}")
    if payload.get("conversion_version") != CONVERSION_VERSION:
        raise SystemExit(f"job must use conversion_version {CONVERSION_VERSION}")
    workspace_root = Path(str(payload.get("workspace_root") or "")).resolve(strict=True)
    current_workspace = Path.cwd().resolve(strict=True)
    try:
        workspace_root.relative_to(current_workspace)
    except ValueError as exc:
        raise SystemExit("workspace_root must stay inside the current working directory") from exc
    materials = payload.get("materials")
    if not isinstance(materials, Sequence) or isinstance(materials, (str, bytes)):
        raise SystemExit("materials must be a list")
    raw_rows = [row if isinstance(row, Mapping) else {} for row in materials]
    prepared: list[tuple[int, Mapping[str, Any]]] = []
    immediate: dict[int, dict[str, Any]] = {}
    for index, raw in enumerate(raw_rows):
        try:
            prepared.append((index, prepare_job(raw, workspace_root)))
        except (OSError, ValueError) as exc:
            immediate[index] = failure_result(
                raw,
                ["invalid_job", type(exc).__name__],
                bpy_version=bpy_version,
            )
    conflicts = _overlapping_outputs(prepared)
    jobs_by_index = dict(prepared)
    for index, raw in enumerate(raw_rows):
        if index in immediate:
            result = immediate[index]
        elif index in conflicts:
            result = failure_result(raw, ["overlapping_output_dirs"], bpy_version=bpy_version)
        else:
            job = jobs_by_index[index]
            try:
                result = convert_one(bpy, workspace_root, job)
            except ConversionFailure as exc:
                result = failure_result(job, exc.codes, bpy_version=bpy_version)
            except Exception as exc:  # one bad material must not abort a batch
                result = failure_result(
                    job,
                    ["conversion_exception", type(exc).__name__],
                    bpy_version=bpy_version,
                )
        print(RESULT_PREFIX + json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
