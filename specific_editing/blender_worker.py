# SPDX-License-Identifier: Apache-2.0

"""Self-contained Blender worker for paper-quality specific-editing renders.

Run with Blender, not the repository Python environment::

    blender --background --python blender_worker.py -- --config render_jobs.json

The JSON document contains one imported GLB and any number of perspective
studio-camera jobs.  This module intentionally imports only Blender and Python
standard-library modules so it remains isolated from the generator runtime.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import bpy
from mathutils import Matrix, Vector

_BLENDER_SUFFIX_RE = re.compile(r"(?:\.\d{3})+$")


class WorkerError(RuntimeError):
    """Raised for an invalid worker config or a failed Blender operation."""


def _worker_arguments() -> argparse.Namespace:
    arguments = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="JSON render-job configuration")
    return parser.parse_args(arguments)


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise WorkerError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise WorkerError(f"{label} must be finite")
    return result


def _unit_interval(value: Any, label: str) -> float:
    result = _number(value, label)
    if not 0.0 <= result <= 1.0:
        raise WorkerError(f"{label} must be in [0, 1]")
    return result


def _positive(value: Any, label: str) -> float:
    result = _number(value, label)
    if result <= 0.0:
        raise WorkerError(f"{label} must be positive")
    return result


def _integer(value: Any, label: str, *, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise WorkerError(f"{label} must be an integer")
    if not minimum <= value <= maximum:
        raise WorkerError(f"{label} must be in [{minimum}, {maximum}]")
    return value


def _rgba(value: Any, label: str) -> tuple[float, float, float, float]:
    if not isinstance(value, list) or len(value) not in {3, 4}:
        raise WorkerError(f"{label} must contain 3 or 4 numeric values")
    channels = tuple(_unit_interval(item, f"{label}[{index}]") for index, item in enumerate(value))
    return channels + (1.0,) if len(channels) == 3 else channels  # type: ignore[return-value]


def _background(value: Any) -> tuple[float, float, float]:
    if not isinstance(value, list) or len(value) not in {3, 4}:
        raise WorkerError("background must contain 3 or 4 numeric values")
    channels = tuple(_number(item, f"background[{index}]") for index, item in enumerate(value))
    if any(item < 0.0 for item in channels):
        raise WorkerError("background channels cannot be negative")
    divisor = 255.0 if any(item > 1.0 for item in channels) else 1.0
    if any(item > 255.0 if divisor == 255.0 else item > 1.0 for item in channels):
        raise WorkerError("background channels must be in [0, 1] or [0, 255]")
    return tuple(item / divisor for item in channels[:3])


def _camera_matrix(value: Any, label: str) -> tuple[tuple[float, ...], ...]:
    if not isinstance(value, list) or len(value) != 4:
        raise WorkerError(f"{label} must be a 4x4 row-major array")
    rows: list[tuple[float, ...]] = []
    for row_index, row in enumerate(value):
        if not isinstance(row, list) or len(row) != 4:
            raise WorkerError(f"{label}[{row_index}] must contain four values")
        rows.append(
            tuple(
                _number(item, f"{label}[{row_index}][{column_index}]")
                for column_index, item in enumerate(row)
            )
        )
    if any(abs(rows[3][index]) > 1e-6 for index in range(3)) or abs(rows[3][3] - 1.0) > 1e-6:
        raise WorkerError(f"{label} must be an affine matrix with last row [0, 0, 0, 1]")
    matrix = Matrix(rows)
    if abs(matrix.to_3x3().determinant()) <= 1e-8:
        raise WorkerError(f"{label} has a singular camera basis")
    return tuple(rows)


def _vector3(value: Any, label: str) -> tuple[float, float, float]:
    if not isinstance(value, list) or len(value) != 3:
        raise WorkerError(f"{label} must contain three numeric values")
    return tuple(_number(item, f"{label}[{index}]") for index, item in enumerate(value))


def _path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise WorkerError(f"{label} must be a non-empty path string")
    return Path(value).expanduser().resolve()


def _validate_materials(value: Any) -> dict[str, dict[str, Any]]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise WorkerError("materials must be an object keyed by imported material name")
    result: dict[str, dict[str, Any]] = {}
    allowed = {"rgba", "metallic", "roughness", "transmission", "ior", "pbr"}
    for material_name, raw_spec in value.items():
        if not isinstance(material_name, str) or not material_name.strip():
            raise WorkerError("materials keys must be non-empty strings")
        if not isinstance(raw_spec, dict):
            raise WorkerError(f"materials[{material_name!r}] must be an object")
        unknown = sorted(set(raw_spec) - allowed)
        if unknown:
            raise WorkerError(
                f"materials[{material_name!r}] has unknown fields: {', '.join(unknown)}"
            )
        spec: dict[str, Any] = {}
        if "rgba" in raw_spec:
            spec["rgba"] = _rgba(raw_spec["rgba"], f"materials[{material_name!r}].rgba")
        for field in ("metallic", "roughness", "transmission"):
            if field in raw_spec:
                spec[field] = _unit_interval(
                    raw_spec[field], f"materials[{material_name!r}].{field}"
                )
        if "ior" in raw_spec:
            ior = _number(raw_spec["ior"], f"materials[{material_name!r}].ior")
            if not 1.0 <= ior <= 3.0:
                raise WorkerError(f"materials[{material_name!r}].ior must be in [1, 3]")
            spec["ior"] = ior
        if "pbr" in raw_spec:
            spec["pbr"] = _validate_pbr(raw_spec["pbr"], f"materials[{material_name!r}].pbr")
        if not spec:
            raise WorkerError(f"materials[{material_name!r}] must override at least one field")
        result[material_name.strip()] = spec
    return result


def _validate_pbr_channel(channel_name: str, value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise WorkerError(f"{label} must be an object")
    kind = value.get("kind")
    if kind == "none":
        if set(value) != {"kind"} or channel_name != "normal":
            raise WorkerError(f"{label} has an invalid none channel")
        return {"kind": "none"}
    if kind == "factor":
        if set(value) != {"kind", "value"} or channel_name == "normal":
            raise WorkerError(f"{label} has an invalid factor channel")
        if channel_name == "base_color":
            factor: Any = _rgba(value.get("value"), f"{label}.value")
        elif channel_name == "ior":
            factor = _number(value.get("value"), f"{label}.value")
            if not 1.0 <= factor <= 3.0:
                raise WorkerError(f"{label}.value must be in [1, 3]")
        else:
            factor = _unit_interval(value.get("value"), f"{label}.value")
        return {"kind": "factor", "value": factor}
    if kind == "texture":
        if set(value) != {"kind", "path", "colorspace"}:
            raise WorkerError(f"{label} has invalid texture fields")
        source = _path(value.get("path"), f"{label}.path")
        if not source.is_file() or source.suffix.lower() != ".png":
            raise WorkerError(f"{label}.path must resolve to a PNG file")
        colorspace = value.get("colorspace")
        expected = "sRGB" if channel_name == "base_color" else "Non-Color"
        if colorspace != expected:
            raise WorkerError(f"{label}.colorspace must be {expected}")
        return {"kind": "texture", "path": source, "colorspace": colorspace}
    raise WorkerError(f"{label}.kind must be factor, texture, or none")


def _validate_pbr(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise WorkerError(f"{label} must be an object")
    allowed = {"material_id", "material_class_id", "tile_size_m", "channels"}
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise WorkerError(f"{label} has unknown fields: {', '.join(unknown)}")
    material_id = value.get("material_id")
    material_class_id = value.get("material_class_id")
    if not isinstance(material_id, str) or not material_id.strip():
        raise WorkerError(f"{label}.material_id must be a non-empty string")
    if not isinstance(material_class_id, str) or not material_class_id.strip():
        raise WorkerError(f"{label}.material_class_id must be a non-empty string")
    raw_channels = value.get("channels")
    if not isinstance(raw_channels, dict) or not raw_channels:
        raise WorkerError(f"{label}.channels must be a non-empty object")
    allowed_channels = {
        "base_color",
        "metallic",
        "roughness",
        "normal",
        "alpha",
        "transmission",
        "ior",
    }
    unknown_channels = sorted(set(raw_channels) - allowed_channels)
    if unknown_channels:
        raise WorkerError(f"{label}.channels has unknown fields: {', '.join(unknown_channels)}")
    channels = {
        str(name): _validate_pbr_channel(str(name), channel, f"{label}.channels.{name}")
        for name, channel in raw_channels.items()
    }
    return {
        "material_id": material_id.strip(),
        "material_class_id": material_class_id.strip(),
        "tile_size_m": _positive(value.get("tile_size_m"), f"{label}.tile_size_m"),
        "channels": channels,
    }


def _load_config(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WorkerError(f"config does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise WorkerError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise WorkerError("config root must be a JSON object")

    input_glb = _path(document.get("input_glb"), "input_glb")
    if not input_glb.is_file():
        raise WorkerError(f"input_glb does not exist: {input_glb}")
    if input_glb.suffix.lower() != ".glb":
        raise WorkerError("input_glb must have a .glb extension")

    size = document.get("image_size")
    if not isinstance(size, list) or len(size) != 2:
        raise WorkerError("image_size must be [width, height]")
    image_size = (
        _integer(size[0], "image_size[0]", minimum=16, maximum=16384),
        _integer(size[1], "image_size[1]", minimum=16, maximum=16384),
    )

    raw_jobs = document.get("jobs")
    if not isinstance(raw_jobs, list) or not raw_jobs:
        raise WorkerError("jobs must be a non-empty array")
    jobs: list[dict[str, Any]] = []
    outputs: set[Path] = set()
    for index, raw_job in enumerate(raw_jobs):
        if not isinstance(raw_job, dict):
            raise WorkerError(f"jobs[{index}] must be an object")
        output = _path(raw_job.get("output"), f"jobs[{index}].output")
        if output.suffix.lower() != ".png":
            raise WorkerError(f"jobs[{index}].output must have a .png extension")
        if output in outputs:
            raise WorkerError(f"jobs[{index}].output is duplicated: {output}")
        outputs.add(output)
        jobs.append(
            {
                "output": output,
                "camera_matrix": _camera_matrix(
                    raw_job.get("camera_matrix"), f"jobs[{index}].camera_matrix"
                ),
                "frame_center": _vector3(
                    raw_job.get("frame_center"), f"jobs[{index}].frame_center"
                ),
                "frame_scale": _positive(raw_job.get("frame_scale"), f"jobs[{index}].frame_scale"),
                "focal_length_mm": _positive(
                    raw_job.get("focal_length_mm", 60.0),
                    f"jobs[{index}].focal_length_mm",
                ),
            }
        )

    return {
        "input_glb": input_glb,
        "background": _background(document.get("background", [255, 255, 255])),
        "image_size": image_size,
        "samples": _integer(document.get("samples", 64), "samples", minimum=1, maximum=4096),
        "materials": _validate_materials(document.get("materials")),
        "jobs": jobs,
    }


def _srgb_to_linear(value: float) -> float:
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def _set_if_present(owner: Any, field: str, value: Any) -> None:
    if hasattr(owner, field):
        setattr(owner, field, value)


def _configure_cycles_device() -> tuple[str, tuple[str, ...]]:
    addon = bpy.context.preferences.addons.get("cycles")
    if addon is None:
        raise WorkerError("Blender was built without the Cycles addon")
    preferences = addon.preferences
    for backend in ("OPTIX", "CUDA"):
        try:
            preferences.compute_device_type = backend
            preferences.refresh_devices()
        except (RuntimeError, TypeError):
            continue
        selected = tuple(device for device in preferences.devices if device.type == backend)
        if not selected:
            continue
        for device in preferences.devices:
            device.use = device.type == backend
        return backend, tuple(device.name for device in selected)
    raise WorkerError("Cycles found no OptiX or CUDA render device")


def _configure_scene(config: dict[str, Any]) -> bpy.types.Scene:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    backend, device_names = _configure_cycles_device()
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    scene.cycles.samples = config["samples"]
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.012
    scene.cycles.adaptive_min_samples = min(16, config["samples"])
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
    scene.cycles.max_bounces = 8
    scene.cycles.diffuse_bounces = 3
    scene.cycles.glossy_bounces = 4
    scene.cycles.transmission_bounces = 6
    scene.cycles.transparent_max_bounces = 8
    _set_if_present(scene.cycles, "use_light_tree", True)
    scene["specific_editing_cycles_backend"] = backend
    scene["specific_editing_cycles_devices"] = ", ".join(device_names)
    width, height = config["image_size"]
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 35
    scene.render.film_transparent = True
    _set_if_present(scene.render, "film_transparent_glass", True)
    _set_if_present(scene.render, "use_file_extension", True)

    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0

    view_layer = scene.view_layers[0]
    _set_if_present(view_layer, "use_pass_shadow", True)
    _set_if_present(view_layer.cycles, "use_pass_shadow_catcher", True)

    world = bpy.data.worlds.new("SpecificEditingWorld")
    world.use_nodes = True
    background_node = world.node_tree.nodes.get("Background")
    if background_node is None:
        raise WorkerError("factory World node tree does not contain a Background node")
    background_node.inputs["Color"].default_value = (0.72, 0.72, 0.72, 1.0)
    background_node.inputs["Strength"].default_value = 0.42
    scene.world = world

    # Preserve film alpha so the host can composite an exact sRGB background
    # after AgX display conversion and supersampling.
    scene.use_nodes = False
    return scene


def _import_glb(input_glb: Path) -> list[bpy.types.Object]:
    result = bpy.ops.import_scene.gltf(filepath=str(input_glb))
    if "FINISHED" not in result:
        raise WorkerError(f"Blender failed to import GLB: {input_glb}")
    mesh_objects = [item for item in bpy.context.scene.objects if item.type == "MESH"]
    if not mesh_objects:
        raise WorkerError(f"GLB contains no mesh objects: {input_glb}")
    for item in tuple(bpy.context.scene.objects):
        if item.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(item, do_unlink=True)
    return mesh_objects


def _canonical_material_name(name: str) -> str:
    return _BLENDER_SUFFIX_RE.sub("", name)


def _principled_node(material: bpy.types.Material) -> bpy.types.Node:
    material.use_nodes = True
    for node in material.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            return node
    raise WorkerError(f"material {material.name!r} has no Principled BSDF node")


def _set_unlinked_input(
    material: bpy.types.Material, node: bpy.types.Node, name: str, value: Any
) -> None:
    socket = node.inputs.get(name)
    if socket is None:
        raise WorkerError(f"material {material.name!r} Principled BSDF lacks input {name!r}")
    for link in tuple(socket.links):
        material.node_tree.links.remove(link)
    socket.default_value = value


def _link_input(
    material: bpy.types.Material,
    node: bpy.types.Node,
    input_name: str,
    output: bpy.types.NodeSocket,
) -> None:
    socket = node.inputs.get(input_name)
    if socket is None:
        raise WorkerError(f"material {material.name!r} Principled BSDF lacks input {input_name!r}")
    for link in tuple(socket.links):
        material.node_tree.links.remove(link)
    material.node_tree.links.new(output, socket)


def _image_texture_node(
    material: bpy.types.Material,
    *,
    channel_name: str,
    source: Path,
    colorspace: str,
) -> bpy.types.Node:
    try:
        image = bpy.data.images.load(str(source), check_existing=True)
        image.colorspace_settings.name = colorspace
    except (OSError, RuntimeError, TypeError) as exc:
        raise WorkerError(f"cannot load PBR {channel_name} texture {source}: {exc}") from exc
    node = material.node_tree.nodes.new("ShaderNodeTexImage")
    node.name = f"SpecificEditing_{channel_name}"
    node.label = channel_name.replace("_", " ").title()
    node.image = image
    node.extension = "REPEAT"
    node.interpolation = "Linear"
    return node


def _apply_pbr_channel(
    material: bpy.types.Material,
    principled: bpy.types.Node,
    channel_name: str,
    channel: dict[str, Any],
) -> None:
    socket_names = {
        "base_color": "Base Color",
        "metallic": "Metallic",
        "roughness": "Roughness",
        "alpha": "Alpha",
        "transmission": "Transmission Weight",
        "ior": "IOR",
    }
    kind = channel["kind"]
    if kind == "none":
        return
    if kind == "factor":
        value = channel["value"]
        if channel_name == "base_color":
            material.diffuse_color = value
        _set_unlinked_input(material, principled, socket_names[channel_name], value)
        return

    texture = _image_texture_node(
        material,
        channel_name=channel_name,
        source=channel["path"],
        colorspace=channel["colorspace"],
    )
    if channel_name == "normal":
        normal = material.node_tree.nodes.new("ShaderNodeNormalMap")
        normal.name = "SpecificEditing_NormalMap"
        normal.inputs["Strength"].default_value = 0.45
        material.node_tree.links.new(texture.outputs["Color"], normal.inputs["Color"])
        _link_input(material, principled, "Normal", normal.outputs["Normal"])
        return
    _link_input(material, principled, socket_names[channel_name], texture.outputs["Color"])


def _pbr_factor(spec: dict[str, Any], channel_name: str, fallback: float) -> float:
    channel = spec.get("pbr", {}).get("channels", {}).get(channel_name, {})
    if channel.get("kind") == "factor":
        return float(channel["value"])
    return float(fallback)


def _apply_one_material(material: bpy.types.Material, spec: dict[str, Any]) -> None:
    node = _principled_node(material)
    rgba = spec.get("rgba")
    if rgba is not None:
        linear_rgba = (*(_srgb_to_linear(channel) for channel in rgba[:3]), rgba[3])
        material.diffuse_color = linear_rgba
        _set_unlinked_input(material, node, "Base Color", linear_rgba)
        _set_unlinked_input(material, node, "Alpha", rgba[3])
    if "metallic" in spec:
        _set_unlinked_input(material, node, "Metallic", spec["metallic"])
    if "roughness" in spec:
        _set_unlinked_input(material, node, "Roughness", spec["roughness"])
    if "transmission" in spec:
        _set_unlinked_input(material, node, "Transmission Weight", spec["transmission"])
    if "ior" in spec:
        _set_unlinked_input(material, node, "IOR", spec["ior"])

    pbr = spec.get("pbr")
    if pbr is not None:
        material.name = f"{material.name}__{pbr['material_class_id']}"
        for channel_name, channel in pbr["channels"].items():
            _apply_pbr_channel(material, node, channel_name, channel)

        material_class_id = pbr["material_class_id"]
        if material_class_id.startswith("glass."):
            is_smoked = "smoked" in material_class_id
            glass_color = (0.55, 0.62, 0.65, 1.0) if is_smoked else (0.95, 0.98, 1.0, 1.0)
            _set_unlinked_input(material, node, "Base Color", glass_color)
            _set_unlinked_input(material, node, "Roughness", 0.10 if is_smoked else 0.04)
            _set_unlinked_input(material, node, "Specular IOR Level", 0.50)
            _set_unlinked_input(material, node, "Alpha", 1.0)
            _set_unlinked_input(material, node, "Transmission Weight", 1.0)
            material.diffuse_color = (*material.diffuse_color[:3], 1.0)

    alpha_fallback = float(rgba[3]) if rgba is not None else float(material.diffuse_color[3])
    alpha = _pbr_factor(spec, "alpha", alpha_fallback)
    transmission = _pbr_factor(
        spec,
        "transmission",
        float(spec.get("transmission", node.inputs["Transmission Weight"].default_value)),
    )
    material.use_transparent_shadow = True
    if alpha < 0.999:
        is_glass = pbr is not None and pbr["material_class_id"].startswith("glass.")
        _set_if_present(
            material,
            "surface_render_method",
            "BLENDED" if is_glass else "DITHERED",
        )
        _set_if_present(material, "blend_method", "BLEND" if is_glass else "HASHED")
        _set_if_present(material, "shadow_method", "HASHED")
    if transmission > 0.0:
        _set_if_present(material, "use_screen_refraction", True)
        _set_if_present(material, "use_raytrace_refraction", True)
        _set_if_present(material, "refraction_depth", 0.02)


def _metric_cube_uv(mesh_object: bpy.types.Object, tile_size_m: float) -> None:
    if mesh_object.type != "MESH":
        return
    bpy.ops.object.select_all(action="DESELECT")
    mesh_object.select_set(True)
    bpy.context.view_layer.objects.active = mesh_object
    try:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.cube_project(
            cube_size=tile_size_m,
            correct_aspect=True,
            clip_to_bounds=False,
            scale_to_bounds=False,
        )
    except RuntimeError as exc:
        raise WorkerError(f"metric UV projection failed for {mesh_object.name!r}: {exc}") from exc
    finally:
        if mesh_object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")


def _objects_using_material(material: bpy.types.Material) -> list[bpy.types.Object]:
    return [
        item
        for item in bpy.context.scene.objects
        if item.type == "MESH"
        and any(slot.material == material for slot in getattr(item, "material_slots", ()))
    ]


def _apply_material_overrides(overrides: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    if not overrides:
        return {}
    imported = tuple(bpy.data.materials)
    applied: dict[str, list[str]] = {}
    claimed: dict[int, str] = {}
    for requested_name, spec in overrides.items():
        requested_canonical = _canonical_material_name(requested_name)
        matches = [
            material
            for material in imported
            if material.name == requested_name
            or _canonical_material_name(material.name) == requested_canonical
        ]
        if not matches:
            available = ", ".join(sorted(material.name for material in imported)) or "<none>"
            raise WorkerError(
                f"material override {requested_name!r} matched no imported material; "
                f"available: {available}"
            )
        for material in matches:
            pointer = material.as_pointer()
            prior = claimed.get(pointer)
            if prior is not None and prior != requested_name:
                raise WorkerError(
                    f"material overrides {prior!r} and {requested_name!r} both match "
                    f"imported material {material.name!r}"
                )
            claimed[pointer] = requested_name
            if "pbr" in spec:
                for mesh_object in _objects_using_material(material):
                    _metric_cube_uv(mesh_object, spec["pbr"]["tile_size_m"])
            _apply_one_material(material, spec)
        applied[requested_name] = sorted(material.name for material in matches)
    return applied


def _scene_bounds(
    mesh_objects: list[bpy.types.Object],
) -> tuple[Vector, Vector, Vector, float]:
    corners = [
        item.matrix_world @ Vector(corner) for item in mesh_objects for corner in item.bound_box
    ]
    lower = Vector(tuple(min(corner[axis] for corner in corners) for axis in range(3)))
    upper = Vector(tuple(max(corner[axis] for corner in corners) for axis in range(3)))
    center = (lower + upper) * 0.5
    radius = max((upper - lower).length * 0.5, 1e-4)
    return lower, upper, center, radius


def _add_bevels(mesh_objects: list[bpy.types.Object]) -> None:
    for mesh_object in mesh_objects:
        dimensions = [abs(float(value)) for value in mesh_object.dimensions if abs(value) > 1e-8]
        if not dimensions:
            continue
        width = min(min(dimensions) * 0.08, max(dimensions) * 0.004, 0.004)
        if width <= 1e-6:
            continue
        modifier = mesh_object.modifiers.new(name="SpecificEditingEdgeBevel", type="BEVEL")
        modifier.width = width
        modifier.segments = 3
        modifier.limit_method = "ANGLE"
        modifier.angle_limit = math.radians(28.0)
        _set_if_present(modifier, "harden_normals", True)


def _create_camera(scene: bpy.types.Scene) -> bpy.types.Object:
    data = bpy.data.cameras.new("SpecificEditingCamera")
    data.type = "PERSP"
    data.sensor_fit = "VERTICAL"
    data.sensor_height = 32.0
    data.dof.use_dof = False
    camera = bpy.data.objects.new("SpecificEditingCamera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    return camera


def _create_area_light(
    scene: bpy.types.Scene,
    name: str,
    *,
    shape: str,
    color: tuple[float, float, float],
) -> bpy.types.Object:
    data = bpy.data.lights.new(name, type="AREA")
    data.shape = shape
    data.color = color
    data.use_shadow = True
    _set_if_present(data, "normalize", True)
    _set_if_present(data, "use_contact_shadow", True)
    light = bpy.data.objects.new(name, data)
    scene.collection.objects.link(light)
    return light


def _aim_area_light(
    light: bpy.types.Object,
    *,
    location: Vector,
    target: Vector,
    size: float,
    energy_scale: float,
) -> None:
    light.location = location
    direction = target - light.location
    if direction.length <= 1e-8:
        direction = Vector((0.0, 0.0, -1.0))
    light.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    light.data.size = max(size, 1e-3)
    if light.data.shape == "RECTANGLE":
        light.data.size_y = max(size * 0.34, 1e-3)
    distance = max(direction.length, size)
    light.data.energy = max(2.0, energy_scale * distance * distance)
    _set_if_present(light.data, "contact_shadow_distance", max(size * 0.35, 1e-4))
    _set_if_present(light.data, "shadow_soft_size", max(size * 0.08, 1e-4))


def _place_studio_lights(
    lights: tuple[bpy.types.Object, bpy.types.Object, bpy.types.Object],
    camera: bpy.types.Object,
    target: Vector,
    frame_scale: float,
) -> None:
    basis = camera.matrix_world.to_3x3()
    right = basis @ Vector((1.0, 0.0, 0.0))
    up = basis @ Vector((0.0, 1.0, 0.0))
    back = basis @ Vector((0.0, 0.0, 1.0))
    world_up = Vector((0.0, 0.0, 1.0))
    floor_right = right - world_up * right.dot(world_up)
    if floor_right.length <= 1e-8:
        floor_right = Vector((1.0, 0.0, 0.0))
    floor_right.normalize()
    floor_camera = back - world_up * back.dot(world_up)
    if floor_camera.length <= 1e-8:
        floor_camera = Vector((0.0, -1.0, 0.0))
    floor_camera.normalize()
    key, fill, rim = lights
    # One overhead key gives a coherent studio shadow.  Fill and rim lights
    # shape the material response without introducing secondary shadow lobes.
    fill.data.use_shadow = False
    rim.data.use_shadow = False
    _aim_area_light(
        key,
        location=target
        + (-0.30 * floor_right - 0.18 * floor_camera + 1.72 * world_up) * frame_scale,
        target=target,
        size=0.62 * frame_scale,
        energy_scale=18.0,
    )
    _aim_area_light(
        fill,
        location=target + (1.02 * right + 0.36 * up + 0.58 * back) * frame_scale,
        target=target,
        size=1.38 * frame_scale,
        energy_scale=3.5,
    )
    _aim_area_light(
        rim,
        location=target + (0.32 * right + 0.88 * up - 1.06 * back) * frame_scale,
        target=target,
        size=0.82 * frame_scale,
        energy_scale=5.5,
    )


def _create_studio_floor(
    scene: bpy.types.Scene,
    *,
    lower: Vector,
    center: Vector,
    radius: float,
) -> bpy.types.Object:
    floor_z = lower.z - max(radius * 0.0025, 1e-5)
    bpy.ops.mesh.primitive_plane_add(
        size=max(radius * 40.0, 1.0),
        location=(center.x, center.y, floor_z),
    )
    floor = bpy.context.object
    floor.name = "SpecificEditingStudioFloor"
    material = bpy.data.materials.new("SpecificEditingStudioFloorMaterial")
    material.use_nodes = True
    principled = _principled_node(material)
    _set_unlinked_input(material, principled, "Base Color", (0.82, 0.82, 0.82, 1.0))
    _set_unlinked_input(material, principled, "Roughness", 0.92)
    _set_unlinked_input(material, principled, "Specular IOR Level", 0.18)
    floor.data.materials.append(material)
    floor.is_shadow_catcher = True
    return floor


def _shadow_paths(output: Path) -> tuple[Path, Path, str]:
    shadow_with = output.with_name(f"{output.stem}__shadow_with_0001.png")
    shadow_clean = output.with_name(f"{output.stem}__shadow_clean.png")
    file_prefix = f"{output.stem}__shadow_with_"
    return shadow_with, shadow_clean, file_prefix


def _configure_shadow_compositor(
    scene: bpy.types.Scene,
    *,
    output_dir: Path,
    file_prefix: str,
) -> tuple[bpy.types.Node, bpy.types.Node, bpy.types.Node]:
    scene.use_nodes = True
    nodes = scene.node_tree.nodes
    links = scene.node_tree.links
    nodes.clear()
    layers = nodes.new("CompositorNodeRLayers")
    composite = nodes.new("CompositorNodeComposite")
    file_output = nodes.new("CompositorNodeOutputFile")
    file_output.base_path = str(output_dir)
    file_output.format.file_format = "PNG"
    file_output.format.color_mode = "RGBA"
    file_output.format.color_depth = "8"
    file_output.file_slots[0].path = file_prefix
    links.new(layers.outputs["Image"], composite.inputs["Image"])
    links.new(layers.outputs["Shadow Catcher"], file_output.inputs[0])
    return layers, composite, file_output


def _connect_composite(
    scene: bpy.types.Scene,
    composite: bpy.types.Node,
    output: bpy.types.NodeSocket,
) -> None:
    for link in tuple(composite.inputs["Image"].links):
        scene.node_tree.links.remove(link)
    scene.node_tree.links.new(output, composite.inputs["Image"])


def _render_jobs(
    scene: bpy.types.Scene,
    mesh_objects: list[bpy.types.Object],
    jobs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    camera = _create_camera(scene)
    lights = (
        _create_area_light(
            scene,
            "SpecificEditingKey",
            shape="RECTANGLE",
            color=(1.0, 0.94, 0.87),
        ),
        _create_area_light(
            scene,
            "SpecificEditingFill",
            shape="DISK",
            color=(0.80, 0.88, 1.0),
        ),
        _create_area_light(
            scene,
            "SpecificEditingRim",
            shape="DISK",
            color=(1.0, 0.98, 0.93),
        ),
    )
    lower, _upper, object_target, object_radius = _scene_bounds(mesh_objects)
    _create_studio_floor(
        scene,
        lower=lower,
        center=object_target,
        radius=object_radius,
    )
    receipts: list[dict[str, Any]] = []
    for index, job in enumerate(jobs):
        output: Path = job["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        camera.matrix_world = Matrix(job["camera_matrix"])
        frame_target = Vector(job["frame_center"])
        frame_scale = job["frame_scale"]
        camera.data.lens = job["focal_length_mm"]
        camera.data.clip_start = max(min(object_radius, frame_scale) * 1e-3, 1e-5)
        camera.data.clip_end = max(
            (camera.location - frame_target).length + object_radius * 4.0,
            frame_scale * 30.0,
            10.0,
        )
        _place_studio_lights(lights, camera, frame_target, frame_scale)
        shadow_with, shadow_clean, file_prefix = _shadow_paths(output)
        layers, composite, file_output = _configure_shadow_compositor(
            scene,
            output_dir=output.parent,
            file_prefix=file_prefix,
        )
        scene.render.filepath = str(output)
        result = bpy.ops.render.render(write_still=True)
        if (
            "FINISHED" not in result
            or not output.is_file()
            or output.stat().st_size <= 64
            or not shadow_with.is_file()
            or shadow_with.stat().st_size <= 64
        ):
            raise WorkerError(f"jobs[{index}] did not produce a valid PNG: {output}")

        file_output.mute = True
        _connect_composite(scene, composite, layers.outputs["Shadow Catcher"])
        for mesh_object in mesh_objects:
            mesh_object.hide_render = True
        try:
            scene.render.filepath = str(shadow_clean)
            clean_result = bpy.ops.render.render(write_still=True)
        finally:
            for mesh_object in mesh_objects:
                mesh_object.hide_render = False
        if (
            "FINISHED" not in clean_result
            or not shadow_clean.is_file()
            or shadow_clean.stat().st_size <= 64
        ):
            raise WorkerError(f"jobs[{index}] did not produce a clean shadow baseline")
        receipts.append(
            {
                "output": str(output),
                "bytes": output.stat().st_size,
                "shadow_with": str(shadow_with),
                "shadow_clean": str(shadow_clean),
            }
        )
        print(f"[specific_editing] rendered {output}", flush=True)
    return receipts


def main() -> int:
    arguments = _worker_arguments()
    config_path = Path(arguments.config).expanduser().resolve()
    config = _load_config(config_path)
    scene = _configure_scene(config)
    mesh_objects = _import_glb(config["input_glb"])
    _add_bevels(mesh_objects)
    applied_materials = _apply_material_overrides(config["materials"])
    renders = _render_jobs(
        scene,
        mesh_objects,
        config["jobs"],
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "input_glb": str(config["input_glb"]),
                "mesh_object_count": len(mesh_objects),
                "materials": applied_materials,
                "renders": renders,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except WorkerError as exc:
        print(f"specific_editing Blender worker error: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(2) from exc
