# SPDX-License-Identifier: Apache-2.0

"""Teaser render worker (runs inside Blender's bundled Python).

Like _blender_worker.py, but visuals carry real sampled PBR materials from the
unified material library (base_color/metallic/roughness/normal textures +
factor channels). Meshes have no authored UVs, so the worker synthesizes a
hard-binned triplanar "canonical metric UV" layer that reproduces the viewer's
articraft-triplanar-v1 shader (object-space position / tile_size, pow(n,6)
weights approximated by dominant-axis binning).

Invoked as:
    blender -b -P scripts/_teaser_blender_worker.py -- <job_dir>

Reads <job_dir>/job.json and renders one PNG per camera pose into
<job_dir>/frames/.
"""

import json
import math
import os
import sys

import bpy
import mathutils


def _argv_job_dir() -> str:
    argv = sys.argv
    if "--" not in argv:
        raise SystemExit("expected: blender -b -P _teaser_blender_worker.py -- <job_dir>")
    return argv[argv.index("--") + 1]


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _mat(flat16: list) -> mathutils.Matrix:
    return mathutils.Matrix([flat16[0:4], flat16[4:8], flat16[8:12], flat16[12:16]])


def _reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def _enable_gpu(scene, samples: int) -> None:
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    chosen = "NONE"
    for backend in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
            if any(d.type == backend for d in prefs.devices):
                chosen = backend
                break
        except (TypeError, RuntimeError):
            continue
    enabled = 0
    for dev in prefs.devices:
        dev.use = dev.type == chosen
        enabled += int(dev.use)
    scene.cycles.device = "GPU" if enabled else "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    # Glass needs deep transmission bounces to read as glass.
    scene.cycles.max_bounces = 24
    scene.cycles.transmission_bounces = 16
    scene.cycles.transparent_max_bounces = 16
    try:
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
    except TypeError:
        pass
    print(f"[blender] compute={chosen} devices_enabled={enabled} device={scene.cycles.device}")


def _setup_world(world_spec: dict) -> None:
    world = bpy.data.worlds.new("studio")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    mix = nt.nodes.new("ShaderNodeMixShader")
    light_path = nt.nodes.new("ShaderNodeLightPath")
    cam_bg = nt.nodes.new("ShaderNodeBackground")
    fill_bg = nt.nodes.new("ShaderNodeBackground")

    bg_color = world_spec.get("bg_color", [0.91, 0.93, 0.96])
    cam_bg.inputs[0].default_value = (*(_srgb_to_linear(c) for c in bg_color), 1.0)
    cam_bg.inputs[1].default_value = float(world_spec.get("bg_strength", 1.0))
    fill_bg.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
    fill_bg.inputs[1].default_value = float(world_spec.get("fill_strength", 0.35))

    nt.links.new(light_path.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(fill_bg.outputs["Background"], mix.inputs[1])
    nt.links.new(cam_bg.outputs["Background"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])


def _add_area_light(name: str, loc, target, energy: float, size: float) -> None:
    data = bpy.data.lights.new(name, type="AREA")
    data.energy = energy
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    direction = mathutils.Vector(target) - mathutils.Vector(loc)
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _new_principled(name: str, color, roughness: float) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (
        *(_srgb_to_linear(c) for c in color),
        1.0,
    )
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def _add_ground(ground_spec: dict, center) -> None:
    if not ground_spec.get("enabled", True):
        return
    z = float(ground_spec.get("z", 0.0))
    size = float(ground_spec.get("size", 100.0))
    color = ground_spec.get("color", [0.16, 0.18, 0.21])
    roughness = float(ground_spec.get("roughness", 0.82))
    mesh = bpy.data.meshes.new("ground")
    obj = bpy.data.objects.new("ground", mesh)
    bpy.context.collection.objects.link(obj)
    verts = [
        (center[0] - size, center[1] - size, z),
        (center[0] + size, center[1] - size, z),
        (center[0] + size, center[1] + size, z),
        (center[0] - size, center[1] + size, z),
    ]
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    mesh.update()
    mesh.materials.append(_new_principled("Studio Ground", color, roughness))


def _add_backdrop(backdrop_spec: dict) -> bpy.types.Object | None:
    """Studio backdrop plane centered at the origin; repositioned per frame."""
    if not backdrop_spec.get("enabled", True):
        return None
    height = float(backdrop_spec.get("height", 4.0))
    width = float(backdrop_spec.get("width", 8.0))
    color = backdrop_spec.get("color", [0.32, 0.35, 0.40])
    roughness = float(backdrop_spec.get("roughness", 0.72))
    mesh = bpy.data.meshes.new("backdrop")
    obj = bpy.data.objects.new("backdrop", mesh)
    bpy.context.collection.objects.link(obj)
    verts = [
        (-width / 2, 0.0, -height / 2),
        (width / 2, 0.0, -height / 2),
        (width / 2, 0.0, height / 2),
        (-width / 2, 0.0, height / 2),
    ]
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    mesh.update()
    mesh.materials.append(_new_principled("Studio Backdrop", color, roughness))
    return obj


def _pose_backdrop(obj, backdrop_spec: dict, center, cam_pose: list) -> None:
    """Place the backdrop behind the object, facing the camera."""
    offset = float(backdrop_spec.get("offset", 2.5))
    cam_x, cam_y = float(cam_pose[3]), float(cam_pose[7])
    az = math.atan2(cam_y - center[1], cam_x - center[0])
    obj.location = (
        center[0] - math.cos(az) * offset,
        center[1] - math.sin(az) * offset,
        float(backdrop_spec.get("z", 0.0)) + float(backdrop_spec.get("height", 4.0)) / 2.0,
    )
    obj.rotation_euler = (0.0, 0.0, az + math.pi / 2.0)


def _apply_triplanar_uv(obj: bpy.types.Object, tile_size_m: float) -> None:
    """Hard-binned triplanar UV mirroring the viewer's articraft-triplanar-v1.

    X face: uv=(y*sign(nx), z); Y face: uv=(-x*sign(ny), z); Z face:
    uv=(x*sign(nz), y) — all in object space, divided by the tile size.
    """
    mesh = obj.data
    layer = mesh.uv_layers.new(name="ArticraftMetricUV")
    if layer is None:
        return
    inv = 1.0 / max(float(tile_size_m or 1.0), 1e-9)
    verts = mesh.vertices
    for poly in mesh.polygons:
        n = poly.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        if ax >= ay and ax >= az:
            sx = 1.0 if n.x >= 0.0 else -1.0
            uv_fn = lambda p: (p.y * sx, p.z)
        elif ay >= az:
            sy = 1.0 if n.y >= 0.0 else -1.0
            uv_fn = lambda p: (-p.x * sy, p.z)
        else:
            sz = 1.0 if n.z >= 0.0 else -1.0
            uv_fn = lambda p: (p.x * sz, p.y)
        for li in poly.loop_indices:
            p = verts[mesh.loops[li].vertex_index].co
            u, v = uv_fn(p)
            layer.data[li].uv = (u * inv, v * inv)


def _make_flat_material(name: str, spec: dict) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    def setv(key: str, value) -> None:
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = value

    lin = tuple(_srgb_to_linear(c) for c in spec["base_color"])
    opacity = float(spec.get("opacity", 1.0))
    transmission = float(spec.get("transmission", 0.0))
    setv("Base Color", (*lin, 1.0))
    setv("Metallic", float(spec.get("metallic", 0.0)))
    setv("Roughness", float(spec.get("roughness", 0.5)))
    setv("IOR", float(spec.get("ior", 1.45)))
    setv("Alpha", opacity)
    setv("Transmission Weight", transmission)
    setv("Transmission", transmission)
    setv("Coat Weight", float(spec.get("clearcoat", 0.0)))
    setv("Clearcoat", float(spec.get("clearcoat", 0.0)))
    setv("Coat Roughness", float(spec.get("clearcoat_roughness", 0.2)))
    if opacity < 0.999 or transmission > 0.01:
        mat.blend_method = "BLEND"
    return mat


def _make_pbr_material(name: str, spec: dict) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")

    tex_nodes = {}
    for channel in ("base_color", "metallic", "roughness", "normal"):
        entry = (spec.get("textures") or {}).get(channel)
        if not entry or not os.path.isfile(entry["path"]):
            continue
        image = bpy.data.images.load(entry["path"])
        image.colorspace_settings.name = (
            "sRGB" if entry.get("colorspace") == "sRGB" else "Non-Color"
        )
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = image
        node.interpolation = "Smart"
        tex_nodes[channel] = node

    factors = spec.get("factors") or {}

    if "base_color" in tex_nodes:
        nt.links.new(tex_nodes["base_color"].outputs["Color"], bsdf.inputs["Base Color"])
    else:
        fallback = factors.get("base_color") or [0.74, 0.74, 0.72, 1.0]
        bsdf.inputs["Base Color"].default_value = tuple(
            _srgb_to_linear(float(c)) for c in fallback[:3]
        ) + (1.0,)

    for channel, socket in (("metallic", "Metallic"), ("roughness", "Roughness")):
        if channel in tex_nodes:
            sep = nt.nodes.new("ShaderNodeSeparateXYZ")
            nt.links.new(tex_nodes[channel].outputs["Color"], sep.inputs[0])
            nt.links.new(sep.outputs["X"], bsdf.inputs[socket])
        elif channel in factors:
            bsdf.inputs[socket].default_value = float(factors[channel])

    if "normal" in tex_nodes:
        normal_map = nt.nodes.new("ShaderNodeNormalMap")
        normal_map.inputs["Strength"].default_value = float(
            factors.get("normal_scale", 1.0)
        )
        nt.links.new(tex_nodes["normal"].outputs["Color"], normal_map.inputs["Color"])
        nt.links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])

    ior = float(factors.get("ior", 1.45))
    transmission = float(factors.get("transmission", 0.0))
    alpha = float(factors.get("alpha", 1.0))
    emission = factors.get("emission") or [0.0, 0.0, 0.0, 1.0]
    emission_strength = float(factors.get("emission_strength", 0.0))

    # Optical (glass-family) materials: transparency is conveyed by the
    # material class, not by a per-material factor -- force a glassy read.
    if spec.get("optical"):
        transmission = max(transmission, 0.9)
        if "roughness" not in tex_nodes and "roughness" not in factors:
            bsdf.inputs["Roughness"].default_value = 0.05
        if alpha >= 0.999:
            alpha = 0.999  # keep traceable transmission instead of pure opacity

    def setv(key: str, value) -> None:
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = value

    setv("IOR", ior)
    setv("Alpha", alpha)
    setv("Transmission Weight", transmission)
    setv("Transmission", transmission)
    setv("Coat Weight", 0.15 if transmission > 0.5 else 0.0)
    setv("Coat Roughness", 0.05)
    setv("Emission Color", tuple(_srgb_to_linear(float(c)) for c in emission[:3]) + (1.0,))
    setv("Emission", tuple(_srgb_to_linear(float(c)) for c in emission[:3]) + (1.0,))
    setv("Emission Strength", emission_strength)

    if alpha < 0.999 or transmission > 0.01:
        mat.blend_method = "BLEND"
    return mat


def _import_visual(job_dir: str, visual: dict) -> bpy.types.Object:
    path = os.path.join(job_dir, visual["mesh"])
    before = set(bpy.context.scene.objects)
    bpy.ops.wm.ply_import(filepath=path)
    new = [o for o in bpy.context.scene.objects if o not in before]
    obj = new[0]
    obj.data.materials.clear()
    spec = visual["spec"]
    if spec.get("kind") == "pbr":
        material = _make_pbr_material(spec.get("material_id") or visual["mesh"], spec)
    else:
        material = _make_flat_material(visual["mesh"], spec)
    obj.data.materials.append(material)
    for poly in obj.data.polygons:
        poly.use_smooth = False
    _apply_triplanar_uv(obj, spec.get("tile_size_m", 1.0))
    return obj


def main() -> None:
    job_dir = _argv_job_dir()
    with open(os.path.join(job_dir, "job.json")) as fh:
        job = json.load(fh)

    _reset_scene()
    scene = bpy.context.scene
    render = job["render"]
    _enable_gpu(scene, int(render.get("samples", 96)))

    scene.render.resolution_x = int(render["width"])
    scene.render.resolution_y = int(render["height"])
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = job.get("view_transform", "AgX")
    try:
        scene.view_settings.look = job.get("view_look", "AgX - Medium High Contrast")
    except (TypeError, ValueError):
        pass
    scene.render.film_transparent = False
    scene.render.use_persistent_data = True

    _setup_world(job.get("world", {}))

    center = job["camera"]["center"]
    _add_ground(job.get("ground", {}), center)
    backdrop = _add_backdrop(job.get("backdrop", {}))
    for i, light in enumerate(job.get("lights", [])):
        _add_area_light(
            f"key_{i}", light["loc"], center, float(light["energy"]), float(light.get("size", 5.0))
        )

    cam_data = bpy.data.cameras.new("cam")
    cam_data.sensor_fit = "VERTICAL"
    cam_data.angle_y = math.radians(float(job["camera"]["angle_y_deg"]))
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    cam_poses = job["camera"]["poses"]

    cam_dists = [math.dist(pose[3:16:4][:3], center) for pose in cam_poses]
    orbit_r = min(cam_dists) if cam_dists else 1.0
    cam_data.clip_start = max(1e-5, 1e-3 * orbit_r)
    cam_data.clip_end = max(1e-2, 1e3 * orbit_r)

    parts_world = job["parts_world"]
    objects = []
    for visual in job["visuals"]:
        objects.append((_import_visual(job_dir, visual), int(visual["part"])))

    frames_dir = os.path.join(job_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    n_frames = len(cam_poses)
    for f in range(n_frames):
        for obj, part_index in objects:
            obj.matrix_world = _mat(parts_world[part_index][f])
        cam.matrix_world = _mat(cam_poses[f])
        if backdrop is not None:
            _pose_backdrop(backdrop, job.get("backdrop", {}), center, cam_poses[f])
        scene.render.filepath = os.path.join(frames_dir, f"frame_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
    print(f"[blender] rendered {n_frames} frames -> {frames_dir}")


if __name__ == "__main__":
    main()
