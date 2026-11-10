# SPDX-License-Identifier: Apache-2.0

"""Shared Blender helpers for legacy material-physics preview rendering."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

METRIC_UV_LAYER_NAME = "ArticraftMetricUV"
METRIC_UV_NODE_NAME = "Articraft Metric UV"


class PreviewMaterialError(RuntimeError):
    """A material preview cannot be represented by the pinned runtime contract."""


@dataclass(frozen=True, slots=True)
class _RuntimeMaterialMapping:
    material_profile: str
    mode: str
    texture_size_m: float | None
    coordinate_space: str | None = None
    uv_method: str | None = None
    rotation_deg: float = 0.0
    offset: tuple[float, float] = (0.0, 0.0)
    preserve_node_graph: bool = False
    opaque: bool = False


def _normalize_name(value: object) -> str:
    return "".join(character.casefold() for character in str(value) if character.isalnum())


def _material_has_surface_output(material: Any) -> bool:
    if not material.use_nodes or material.node_tree is None:
        return False
    for node in material.node_tree.nodes:
        if node.type != "OUTPUT_MATERIAL" or not getattr(node, "is_active_output", True):
            continue
        surface = node.inputs.get("Surface")
        if surface is not None and surface.is_linked:
            return True
    return False


def _choose_library_material(materials: Sequence[Any], display_name: object) -> Any:
    wanted = _normalize_name(display_name)

    def rank(material: Any) -> tuple[int, int, int, str]:
        name = _normalize_name(material.name)
        exact = int(bool(wanted) and name == wanted)
        contains = int(bool(wanted) and (wanted in name or name in wanted))
        usable = int(_material_has_surface_output(material))
        return (-exact, -contains, -usable, material.name.casefold())

    usable = [material for material in materials if material is not None]
    if not usable:
        raise PreviewMaterialError("Blender material package contains no Material datablock")
    return min(usable, key=rank)


def _node_trees(root: Any) -> tuple[Any, ...]:
    pending = [root]
    seen: set[int] = set()
    result: list[Any] = []
    while pending:
        tree = pending.pop()
        pointer = int(tree.as_pointer())
        if pointer in seen:
            continue
        seen.add(pointer)
        result.append(tree)
        for node in tree.nodes:
            nested = getattr(node, "node_tree", None)
            if nested is not None:
                pending.append(nested)
    return tuple(result)


def _disconnect_true_displacement(material: Any) -> int:
    if not material.use_nodes or material.node_tree is None:
        return 0
    removed = 0
    tree = material.node_tree
    for node in tree.nodes:
        if node.type != "OUTPUT_MATERIAL":
            continue
        socket = node.inputs.get("Displacement")
        if socket is None:
            continue
        for link in tuple(socket.links):
            tree.links.remove(link)
            removed += 1
    return removed


def _metric_uv_coordinate_node(tree: Any) -> Any:
    for node in tree.nodes:
        if node.type == "UVMAP" and node.name == METRIC_UV_NODE_NAME:
            node.uv_map = METRIC_UV_LAYER_NAME
            return node
    node = tree.nodes.new("ShaderNodeUVMap")
    node.label = METRIC_UV_NODE_NAME
    node.name = METRIC_UV_NODE_NAME
    node.uv_map = METRIC_UV_LAYER_NAME
    return node


def _bind_metric_uv_images(material: Any) -> int:
    if not material.use_nodes or material.node_tree is None:
        raise PreviewMaterialError("texture_set material has no node tree")
    image_count = 0
    for tree in _node_trees(material.node_tree):
        image_nodes = [node for node in tree.nodes if node.type == "TEX_IMAGE"]
        if not image_nodes:
            continue
        coordinate = _metric_uv_coordinate_node(tree).outputs.get("UV")
        if coordinate is None:
            raise PreviewMaterialError("metric UVMap node has no UV output")
        for node in image_nodes:
            vector = node.inputs.get("Vector")
            if vector is None:
                raise PreviewMaterialError(f"image texture {node.name!r} has no Vector input")
            for link in tuple(vector.links):
                tree.links.remove(link)
            tree.links.new(coordinate, vector)
            if hasattr(node, "projection"):
                node.projection = "FLAT"
            if hasattr(node, "projection_blend"):
                node.projection_blend = 0.0
            if hasattr(node, "extension"):
                node.extension = "REPEAT"
            image_count += 1
    if image_count == 0:
        raise PreviewMaterialError("texture_set material contains no Image Texture nodes")
    return image_count


def _triangle_area_3d(
    first: Sequence[float], second: Sequence[float], third: Sequence[float]
) -> float:
    ab = tuple(float(second[index]) - float(first[index]) for index in range(3))
    ac = tuple(float(third[index]) - float(first[index]) for index in range(3))
    cross = (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )
    return 0.5 * math.sqrt(sum(value * value for value in cross))


def _triangle_area_2d(
    first: Sequence[float], second: Sequence[float], third: Sequence[float]
) -> float:
    ab_x = float(second[0]) - float(first[0])
    ab_y = float(second[1]) - float(first[1])
    ac_x = float(third[0]) - float(first[0])
    ac_y = float(third[1]) - float(first[1])
    return 0.5 * abs(ab_x * ac_y - ab_y * ac_x)


def _metric_uv_scale_factor(
    *, surface_area_m2: float, uv_area: float, texture_size_m: float
) -> float:
    values = (surface_area_m2, uv_area, texture_size_m)
    if not all(math.isfinite(value) and value > 0.0 for value in values):
        raise PreviewMaterialError("metric UV areas and texture_size_m must be positive and finite")
    desired_uv_area = surface_area_m2 / (texture_size_m * texture_size_m)
    return math.sqrt(desired_uv_area / uv_area)


def _apply_scale_to_mesh(obj: Any, mathutils: Any) -> None:
    scale = tuple(float(value) for value in obj.scale)
    if not all(math.isfinite(value) and value > 0.0 for value in scale):
        raise PreviewMaterialError(f"mesh object {obj.name!r} has an invalid scale {scale!r}")
    if any(abs(value - 1.0) > 1e-12 for value in scale):
        obj.data.transform(mathutils.Matrix.Diagonal((*scale, 1.0)))
        obj.scale = (1.0, 1.0, 1.0)
        obj.data.update()


def _smart_project_metric_uv(
    bpy: Any,
    obj: Any,
    mathutils: Any,
    mapping: _RuntimeMaterialMapping,
) -> float:
    if mapping.texture_size_m is None:
        raise PreviewMaterialError("metric UV mapping has no texture_size_m")
    mesh = obj.data
    if not mesh.polygons:
        raise PreviewMaterialError(f"mesh object {obj.name!r} has no polygon surface to unwrap")
    _apply_scale_to_mesh(obj, mathutils)

    if bpy.context.object is not None and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    previous = mesh.uv_layers.get(METRIC_UV_LAYER_NAME)
    if previous is not None:
        mesh.uv_layers.remove(previous)
    uv_layer = mesh.uv_layers.new(name=METRIC_UV_LAYER_NAME)
    mesh.uv_layers.active = uv_layer
    uv_layer.active_render = True

    try:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        result = bpy.ops.uv.smart_project(
            angle_limit=math.radians(66.0),
            island_margin=0.02,
        )
    finally:
        if bpy.context.object is not None and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    if "FINISHED" not in result:
        raise PreviewMaterialError(f"smart UV projection failed for mesh object {obj.name!r}")

    uv_layer = mesh.uv_layers.get(METRIC_UV_LAYER_NAME)
    if uv_layer is None:
        raise PreviewMaterialError(f"smart UV projection removed metric UV layer for {obj.name!r}")
    mesh.uv_layers.active = uv_layer
    uv_layer.active_render = True

    mesh.calc_loop_triangles()
    surface_area = 0.0
    uv_area = 0.0
    used_loops: set[int] = set()
    for triangle in mesh.loop_triangles:
        vertices = [mesh.vertices[index].co for index in triangle.vertices]
        surface_area += _triangle_area_3d(*vertices)
        loop_indices = tuple(int(index) for index in triangle.loops)
        coordinates = [uv_layer.data[index].uv for index in loop_indices]
        uv_area += _triangle_area_2d(*coordinates)
        used_loops.update(loop_indices)
    factor = _metric_uv_scale_factor(
        surface_area_m2=surface_area,
        uv_area=uv_area,
        texture_size_m=mapping.texture_size_m,
    )
    if not used_loops:
        raise PreviewMaterialError(f"smart UV projection emitted no loops for {obj.name!r}")

    center_x = sum(float(uv_layer.data[index].uv[0]) for index in used_loops) / len(used_loops)
    center_y = sum(float(uv_layer.data[index].uv[1]) for index in used_loops) / len(used_loops)
    angle = math.radians(mapping.rotation_deg)
    cosine, sine = math.cos(angle), math.sin(angle)
    for index in used_loops:
        uv = uv_layer.data[index].uv
        scaled_x = (float(uv[0]) - center_x) * factor
        scaled_y = (float(uv[1]) - center_y) * factor
        uv[0] = center_x + scaled_x * cosine - scaled_y * sine + mapping.offset[0]
        uv[1] = center_y + scaled_x * sine + scaled_y * cosine + mapping.offset[1]
    mesh.update()
    return factor
