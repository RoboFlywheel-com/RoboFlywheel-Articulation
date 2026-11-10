# SPDX-License-Identifier: Apache-2.0

"""Blender-side render worker (runs inside Blender's bundled Python).

Invoked as:
    blender -b -P scripts/_blender_worker.py -- <job_dir>

Reads <job_dir>/job.json (written by render_template_videos_blender.py), builds a
studio Cycles scene, and renders one PNG per frame into <job_dir>/frames/. The
orchestrator then encodes the frames to MP4. All scene math (FK world matrices,
camera orbit poses, per-part segment colors) is precomputed by the orchestrator;
this script only realizes it in Blender and path-traces it.

Kept dependency-free beyond bpy/mathutils so it runs in Blender's own Python.
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
        raise SystemExit("expected: blender -b -P _blender_worker.py -- <job_dir>")
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
    try:
        # OptiX AI denoiser fails to initialize on some driver/Blender combos
        # ("Failed to create OptiX denoiser"); OIDN is the stable fallback.
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
    except TypeError:
        pass
    print(f"[blender] compute={chosen} devices_enabled={enabled} device={scene.cycles.device}")


def _setup_world(world_spec: dict) -> None:
    """Decouple the visible background from the lighting environment.

    Camera rays see a fixed bright background (the viewer's #e8edf5), while
    lighting rays see only a dim neutral fill -- so part colors stay saturated
    instead of being washed out by a bright white environment.
    """
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


def _add_ground(ground_spec: dict, center) -> None:
    if not ground_spec.get("enabled", True):
        return
    z = float(ground_spec.get("z", 0.0))
    size = float(ground_spec.get("size", 100.0))
    mesh = bpy.data.meshes.new("ground")
    obj = bpy.data.objects.new("ground", mesh)
    bpy.context.collection.objects.link(obj)
    from bpy_extras.object_utils import object_data_add  # noqa: F401

    verts = [
        (center[0] - size, center[1] - size, z),
        (center[0] + size, center[1] - size, z),
        (center[0] + size, center[1] + size, z),
        (center[0] - size, center[1] + size, z),
    ]
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    mesh.update()
    obj.is_shadow_catcher = True


def _make_material(name: str, spec: dict) -> bpy.types.Material:
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
    # Blender 4.x renamed these sockets; setv() silently skips absent names.
    setv("Transmission Weight", transmission)
    setv("Transmission", transmission)
    setv("Coat Weight", float(spec.get("clearcoat", 0.0)))
    setv("Clearcoat", float(spec.get("clearcoat", 0.0)))
    setv("Coat Roughness", float(spec.get("clearcoat_roughness", 0.2)))
    if opacity < 0.999 or transmission > 0.01:
        mat.blend_method = "BLEND"
    return mat


def _import_visual(job_dir: str, visual: dict) -> bpy.types.Object:
    path = os.path.join(job_dir, visual["mesh"])
    before = set(bpy.context.scene.objects)
    bpy.ops.wm.ply_import(filepath=path)
    new = [o for o in bpy.context.scene.objects if o not in before]
    obj = new[0]
    obj.data.materials.clear()
    obj.data.materials.append(_make_material(visual["mesh"], visual["spec"]))
    for poly in obj.data.polygons:
        poly.use_smooth = False
    return obj


def main() -> None:
    job_dir = _argv_job_dir()
    with open(os.path.join(job_dir, "job.json")) as fh:
        job = json.load(fh)

    _reset_scene()
    scene = bpy.context.scene
    render = job["render"]
    _enable_gpu(scene, int(render.get("samples", 48)))

    scene.render.resolution_x = int(render["width"])
    scene.render.resolution_y = int(render["height"])
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = job.get("view_transform", "Standard")
    scene.render.film_transparent = False
    # Reuse device data/BVH across frames: only object transforms change between
    # frames, so Cycles refits the BVH instead of rebuilding it -> much faster.
    scene.render.use_persistent_data = True

    _setup_world(job.get("world", {}))

    center = job["camera"]["center"]
    _add_ground(job.get("ground", {}), center)
    for i, light in enumerate(job.get("lights", [])):
        _add_area_light(
            f"key_{i}", light["loc"], center, float(light["energy"]), float(light.get("size", 5.0))
        )

    # Camera (vertical-fit FOV; per-frame poses drive the orbit).
    cam_data = bpy.data.cameras.new("cam")
    cam_data.sensor_fit = "VERTICAL"
    cam_data.angle_y = math.radians(float(job["camera"]["angle_y_deg"]))
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    cam_poses = job["camera"]["poses"]

    # Scale the near/far planes to the scene. Blender's defaults (0.1m / 100m)
    # clip small templates away entirely: a ~30mm capsule is framed from ~50mm,
    # which sits in front of the default near plane and renders as bare
    # background. Derive the planes from the actual orbit radius instead.
    cam_dists = [
        math.dist(pose[3:16:4][:3], center) for pose in cam_poses
    ]
    orbit_r = min(cam_dists) if cam_dists else 1.0
    cam_data.clip_start = max(1e-5, 1e-3 * orbit_r)
    cam_data.clip_end = max(1e-2, 1e3 * orbit_r)

    parts_world = job["parts_world"]  # parts_world[part][frame] = flat16
    objects = []  # (blender_obj, part_index)
    for visual in job["visuals"]:
        objects.append((_import_visual(job_dir, visual), int(visual["part"])))

    frames_dir = os.path.join(job_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    n_frames = int(render["frames"])
    for f in range(n_frames):
        for obj, part_index in objects:
            obj.matrix_world = _mat(parts_world[part_index][f])
        cam.matrix_world = _mat(cam_poses[f])
        scene.render.filepath = os.path.join(frames_dir, f"frame_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
    print(f"[blender] rendered {n_frames} frames -> {frames_dir}")


if __name__ == "__main__":
    main()
