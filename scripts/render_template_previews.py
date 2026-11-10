# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import contextlib
import fcntl
import importlib
import math
import os
import select
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np
import trimesh
from PIL import Image, ImageDraw

from agent.template_registry import TEMPLATE_REGISTRY
from sdk import AssetContext, Box, Cylinder, Mesh, Sphere
from sdk._core.v0.assets import resolve_mesh_path
from sdk._core.v0.geometry_qc import _origin_to_mat4, compute_part_world_transforms

os.environ.setdefault("PYOPENGL_PLATFORM", "egl")


class RenderBackendError(RuntimeError):
    """The requested production renderer could not produce a usable image."""


_XVFB_LOCK = threading.RLock()
_XVFB_LOCK_PATH = Path("/tmp/articraft-visual-qc-xvfb.lock")
_XVFB_STATE = threading.local()


def validate_render_image(path: Path) -> dict[str, float | int]:
    """Reject missing, empty, corrupt, or unreadably low-contrast renderer output.

    A handful of bright pixels is not sufficient evidence that a headless render
    is usable.  In particular, the old check accepted an almost-black local
    mechanism crop, which made dark CAD materials look disconnected to
    reviewers.  Keep the check backend-independent and report simple
    luminance statistics for the visual-QA report.
    """

    if not path.is_file() or path.stat().st_size <= 0:
        raise RenderBackendError(f"render output is missing or empty: {path}")
    try:
        with Image.open(path) as image:
            rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    except Exception as exc:
        raise RenderBackendError(f"render output is unreadable: {path}: {exc}") from exc
    if rgb.ndim != 3 or rgb.shape[0] < 2 or rgb.shape[1] < 2:
        raise RenderBackendError(f"render output has invalid dimensions: {path}")
    peak = int(rgb.max(initial=0))
    nonblack_fraction = float(np.count_nonzero(rgb.max(axis=2) > 8) / (rgb.shape[0] * rgb.shape[1]))
    luminance = (
        0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
    )
    mean_luminance = float(luminance.mean())
    p05, p95 = (float(v) for v in np.percentile(luminance, (5, 95)))
    contrast_span = p95 - p05
    if peak <= 8 or nonblack_fraction < 0.01 or contrast_span < 18.0:
        raise RenderBackendError(
            f"render output is black/near-black or low-contrast: {path} "
            f"(peak={peak}, nonblack_fraction={nonblack_fraction:.6f}, "
            f"mean_luminance={mean_luminance:.1f}, contrast_span={contrast_span:.1f})"
        )
    return {
        "width": int(rgb.shape[1]),
        "height": int(rgb.shape[0]),
        "bytes": int(path.stat().st_size),
        "peak": peak,
        "nonblack_fraction": nonblack_fraction,
        "mean_luminance": mean_luminance,
        "contrast_span": contrast_span,
    }


def _start_xvfb() -> tuple[subprocess.Popen[bytes], str]:
    executable = shutil.which("Xvfb")
    if executable is None:
        raise RenderBackendError(
            "VTK rendering needs DISPLAY; Xvfb was not found for automatic headless startup"
        )
    read_fd, write_fd = os.pipe()
    process: subprocess.Popen[bytes] | None = None
    try:
        process = subprocess.Popen(
            [
                executable,
                "-displayfd",
                str(write_fd),
                "-screen",
                "0",
                "1280x1024x24",
                "-nolisten",
                "tcp",
            ],
            pass_fds=(write_fd,),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        os.close(write_fd)
        write_fd = -1
        ready, _, _ = select.select([read_fd], [], [], 10.0)
        if not ready:
            raise RenderBackendError("Xvfb did not publish a display within 10 seconds")
        display_number = os.read(read_fd, 64).decode("ascii", errors="replace").strip()
        if not display_number.isdigit():
            detail = ""
            if process.poll() is not None and process.stderr is not None:
                detail = process.stderr.read().decode("utf-8", errors="replace").strip()
            raise RenderBackendError(f"Xvfb startup failed: {detail or display_number!r}")
        return process, f":{display_number}"
    except Exception:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2.0)
        raise
    finally:
        os.close(read_fd)
        if write_fd >= 0:
            os.close(write_fd)


@contextlib.contextmanager
def headless_render_display(renderer: str) -> Iterator[None]:
    """Serialize headless VTK batches; one in-process batch owns its Xvfb."""

    if renderer not in {"vtk", "auto"} or os.environ.get("DISPLAY"):
        yield
        return
    if getattr(_XVFB_STATE, "depth", 0):
        _XVFB_STATE.depth += 1
        try:
            yield
        finally:
            _XVFB_STATE.depth -= 1
        return
    with _XVFB_LOCK:
        _XVFB_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _XVFB_LOCK_PATH.open("a+") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            xvfb: subprocess.Popen[bytes] | None = None
            _XVFB_STATE.depth = 1
            try:
                xvfb, display = _start_xvfb()
                os.environ["DISPLAY"] = display
                yield
            finally:
                os.environ.pop("DISPLAY", None)
                _XVFB_STATE.depth = 0
                if xvfb is not None and xvfb.poll() is None:
                    xvfb.terminate()
                    try:
                        xvfb.wait(timeout=3.0)
                    except subprocess.TimeoutExpired:
                        xvfb.kill()
                        xvfb.wait(timeout=3.0)
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


DEFAULT_SLUGS = (
    "barrier_gate_boom",
    "barrier_gate_leaf_gate",
    "bicycle_crankset_and_pedal_assembly",
    "blender_countertop",
    "immersion_blender",
    "box_fan_with_control_knob",
    "camcorder_with_flipout_screen",
    "camera_flash",
    "camera_lens",    "cantilever_articulated_arm",
    "car_sunroof_cassette_soft_top",    "ceiling_fan",
    "ceiling_light_fixture_adjustable",
    "chest_freezer_with_hinged_lid",
    "coaxial_rotary_stack",
    "crane_tower",
    "desk_with_drawer",
    "desk_with_drawer_card_catalog",
    "desktop_monitor_with_tilt_swivel_stand",
    "desktop_pc_tower",
)

VIEW_DIRECTIONS = (
    # +Y is the modern default.  Legacy source families may declare
    # ``__preview_front_axis__ = "-y"`` in their template module.
    ("front_iso", np.array([1.25, 1.35, 0.85], dtype=float)),
    ("rear_iso", np.array([-1.15, -1.25, 0.8], dtype=float)),
    ("side", np.array([1.9, 0.1, 0.45], dtype=float)),
)


def _semantic_view_directions(module: object) -> dict[str, np.ndarray]:
    """Resolve semantic camera names without imposing one front axis globally."""
    directions = {name: direction.copy() for name, direction in VIEW_DIRECTIONS}
    front_axis = getattr(module, "__preview_front_axis__", "+y")
    if front_axis == "+y":
        return directions
    if front_axis == "-y":
        directions["front_iso"] = np.array([1.25, -1.35, 0.85], dtype=float)
        directions["rear_iso"] = np.array([-1.15, 1.25, 0.8], dtype=float)
        return directions
    if front_axis == "+z":
        directions["front_iso"] = np.array([1.05, 0.80, 1.45], dtype=float)
        directions["rear_iso"] = np.array([-1.00, -0.75, -1.35], dtype=float)
        directions["side"] = np.array([1.90, 0.45, 0.12], dtype=float)
        return directions
    if front_axis == "-z":
        directions["front_iso"] = np.array([1.05, 0.80, -1.45], dtype=float)
        directions["rear_iso"] = np.array([-1.00, -0.75, 1.35], dtype=float)
        directions["side"] = np.array([1.90, 0.45, -0.12], dtype=float)
        return directions
    raise ValueError(
        f"Unsupported __preview_front_axis__={front_axis!r}; "
        "expected one of '+y', '-y', '+z', or '-z'"
    )


def _parse_seeds(spec: str) -> list[int]:
    seeds: list[int] = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            start_s, end_s = chunk.split("-", 1)
            start = int(start_s)
            end = int(end_s)
            if end < start:
                raise ValueError(f"Invalid seed range: {chunk}")
            seeds.extend(range(start, end + 1))
        else:
            seeds.append(int(chunk))
    return seeds


def _matrix(value: object) -> np.ndarray:
    return np.asarray(value, dtype=float)


def _primitive_mesh(geometry: object) -> trimesh.Trimesh | None:
    if isinstance(geometry, Box):
        return trimesh.creation.box(extents=geometry.size)
    if isinstance(geometry, Cylinder):
        return trimesh.creation.cylinder(
            radius=geometry.radius, height=geometry.length, sections=40
        )
    if isinstance(geometry, Sphere):
        return trimesh.creation.uv_sphere(radius=geometry.radius, count=(24, 24))
    return None


def _mesh_geometry(geometry: object, *, assets: AssetContext | None) -> trimesh.Trimesh | None:
    if isinstance(geometry, Mesh):
        if geometry.source_geometry is not None:
            mesh = _primitive_mesh(geometry.source_geometry)
            if mesh is not None and geometry.source_transform is not None:
                mesh.apply_transform(_matrix(geometry.source_transform))
            return mesh
        path_text = geometry.materialized_path or geometry.filename
        if path_text:
            path = Path(path_text)
            if not path.is_absolute() and geometry.materialized_path is None:
                path = resolve_mesh_path(path, assets=assets, ensure_dir=False)
            if path.exists():
                loaded = trimesh.load(path, force="mesh")
                if isinstance(loaded, trimesh.Trimesh):
                    return loaded
    return _primitive_mesh(geometry)


def _rgba(material: object) -> tuple[float, float, float, float]:
    rgba = getattr(material, "rgba", None)
    if isinstance(rgba, tuple | list) and len(rgba) >= 3:
        values = tuple(float(v) for v in rgba)
        if len(values) == 3:
            return (values[0], values[1], values[2], 1.0)
        return (values[0], values[1], values[2], values[3])
    return (0.68, 0.70, 0.72, 1.0)


def _camera_pose(center: np.ndarray, radius: float, direction_scale: np.ndarray) -> np.ndarray:
    pose = np.eye(4)
    pose[:3, 3] = center + direction_scale * radius
    direction = center - pose[:3, 3]
    direction = direction / np.linalg.norm(direction)
    up = np.array([0.0, 0.0, 1.0])
    right = np.cross(direction, up)
    if np.linalg.norm(right) < 1e-6:
        right = np.array([1.0, 0.0, 0.0])
    right = right / np.linalg.norm(right)
    up = np.cross(right, direction)
    pose[:3, :3] = np.stack([right, up, -direction], axis=1)
    return pose


def _render_scene(
    meshes: Iterable[tuple[trimesh.Trimesh, tuple[float, float, float, float]]], out: Path
) -> None:
    renderer_mode = getattr(_render_scene, "renderer_mode", "vtk")
    if renderer_mode == "auto":
        renderer_mode = "vtk"
    if renderer_mode == "software":
        _render_scene_software(meshes, out)
    elif renderer_mode == "vtk":
        _render_scene_vtk(meshes, out)
    elif renderer_mode == "egl":
        try:
            _render_scene_egl(meshes, out)
        except ModuleNotFoundError as exc:
            raise RenderBackendError(
                "EGL renderer requested but pyrender is unavailable; refusing software fallback"
            ) from exc
    else:
        raise ValueError(f"Unknown renderer: {renderer_mode}")
    validate_render_image(out)


def _render_scene_egl(
    meshes: Iterable[tuple[trimesh.Trimesh, tuple[float, float, float, float]]], out: Path
) -> None:
    import pyrender

    mesh_items = list(meshes)
    if not mesh_items:
        raise ValueError("No renderable meshes")

    scene = pyrender.Scene(bg_color=(0.02, 0.025, 0.03, 1.0), ambient_light=(0.35, 0.35, 0.35))
    combined = trimesh.util.concatenate([mesh for mesh, _ in mesh_items])
    center = np.asarray(combined.bounding_box.centroid, dtype=float)
    radius = float(np.linalg.norm(combined.bounding_box.extents)) or 1.0

    for mesh, color in mesh_items:
        material = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=color,
            metallicFactor=0.0,
            roughnessFactor=0.65,
        )
        scene.add(pyrender.Mesh.from_trimesh(mesh, material=material, smooth=False))

    camera = pyrender.PerspectiveCamera(yfov=math.radians(42.0))
    pose = _camera_pose(center, radius, _render_scene.direction)  # type: ignore[attr-defined]
    scene.add(camera, pose=pose)
    scene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=3.5), pose=pose)

    renderer = pyrender.OffscreenRenderer(900, 700)
    color, _depth = renderer.render(scene)
    renderer.delete()
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(color).save(out)


def _render_scene_vtk(
    meshes: Iterable[tuple[trimesh.Trimesh, tuple[float, float, float, float]]], out: Path
) -> None:
    """Headless z-buffer renderer for reliable CAD-shell preview images."""

    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray

    mesh_items = list(meshes)
    if not mesh_items:
        raise ValueError("No renderable meshes")

    renderer = vtk.vtkRenderer()
    # Neutral studio gray keeps dark materials and thin guide elements legible.
    # The previous near-black background was especially harmful for mechanism
    # evidence, where only a subset of the parent structure is shown.
    renderer.SetBackground(0.86, 0.88, 0.92)
    renderer.SetAmbient(0.34, 0.34, 0.34)

    for mesh, color in mesh_items:
        vertices = np.ascontiguousarray(np.asarray(mesh.vertices, dtype=np.float64))
        faces = np.ascontiguousarray(np.asarray(mesh.faces, dtype=np.int64))
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(vertices, deep=True))
        cells_data = np.empty((len(faces), 4), dtype=np.int64)
        cells_data[:, 0] = 3
        cells_data[:, 1:] = faces
        cells = vtk.vtkCellArray()
        cells.SetCells(
            len(faces),
            numpy_to_vtkIdTypeArray(cells_data.ravel(), deep=True),
        )
        poly = vtk.vtkPolyData()
        poly.SetPoints(points)
        poly.SetPolys(cells)

        normals = vtk.vtkPolyDataNormals()
        normals.SetInputData(poly)
        normals.ConsistencyOn()
        normals.AutoOrientNormalsOn()
        normals.SplittingOff()
        normals.ComputePointNormalsOn()
        normals.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        rgb = tuple(float(v) for v in color[:3])
        actor.GetProperty().SetColor(*rgb)
        actor.GetProperty().SetOpacity(float(color[3]))
        actor.GetProperty().SetInterpolationToPhong()
        renderer.AddActor(actor)

    combined = trimesh.util.concatenate([mesh for mesh, _ in mesh_items])
    center = np.asarray(combined.bounding_box.centroid, dtype=float)
    radius = max(float(np.linalg.norm(combined.bounding_box.extents)) * 0.5, 1e-3)
    direction = np.asarray(_render_scene.direction, dtype=float)  # type: ignore[attr-defined]
    direction /= np.linalg.norm(direction)
    distance = radius / math.sin(math.radians(42.0 / 2.0)) * 1.16

    camera = renderer.GetActiveCamera()
    camera.SetPosition(*(center + direction * distance))
    camera.SetFocalPoint(*center)
    camera.SetViewUp(0.0, 0.0, 1.0)
    camera.SetViewAngle(42.0)

    key = vtk.vtkLight()
    key.SetLightTypeToCameraLight()
    key.SetIntensity(0.92)
    renderer.AddLight(key)
    fill = vtk.vtkLight()
    fill.SetLightTypeToSceneLight()
    fill.SetPosition(*(center + np.array([-1.4, -1.0, 1.8]) * radius))
    fill.SetFocalPoint(*center)
    fill.SetIntensity(0.55)
    renderer.AddLight(fill)

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(900, 700)
    window.AddRenderer(renderer)
    renderer.ResetCameraClippingRange()
    window.Render()

    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetInputBufferTypeToRGB()
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    out.parent.mkdir(parents=True, exist_ok=True)
    writer.SetFileName(str(out))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    renderer.RemoveAllViewProps()
    window.Finalize()


def _render_scene_software(
    meshes: Iterable[tuple[trimesh.Trimesh, tuple[float, float, float, float]]], out: Path
) -> None:
    """Dependency-free orthographic fallback for authoring contact sheets."""

    mesh_items = list(meshes)
    if not mesh_items:
        raise ValueError("No renderable meshes")

    direction = np.asarray(_render_scene.direction, dtype=float)  # type: ignore[attr-defined]
    direction /= np.linalg.norm(direction)
    forward = -direction
    world_up = np.array([0.0, 0.0, 1.0])
    right = np.cross(forward, world_up)
    if np.linalg.norm(right) < 1e-6:
        right = np.array([1.0, 0.0, 0.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    up /= np.linalg.norm(up)

    projected_sets: list[tuple[np.ndarray, np.ndarray, trimesh.Trimesh, tuple[float, ...]]] = []
    all_xy: list[np.ndarray] = []
    for mesh, color in mesh_items:
        vertices = np.asarray(mesh.vertices, dtype=float)
        xy = np.column_stack((vertices @ right, vertices @ up))
        depth = vertices @ forward
        projected_sets.append((xy, depth, mesh, color))
        all_xy.append(xy)

    bounds_points = np.concatenate(all_xy, axis=0)
    xy_min = bounds_points.min(axis=0)
    xy_max = bounds_points.max(axis=0)
    span = np.maximum(xy_max - xy_min, 1e-6)
    width, height, margin = 900, 700, 46
    scale = min((width - 2 * margin) / span[0], (height - 2 * margin) / span[1])
    center = (xy_min + xy_max) * 0.5

    polygons: list[tuple[float, list[tuple[float, float]], tuple[int, int, int]]] = []
    light = np.array([0.35, -0.45, 0.82], dtype=float)
    light /= np.linalg.norm(light)
    for xy, depth, mesh, color in projected_sets:
        screen = (xy - center) * scale
        screen[:, 0] += width * 0.5
        screen[:, 1] = height * 0.5 - screen[:, 1]
        base = np.asarray(color[:3], dtype=float)
        if base.max(initial=0.0) <= 1.0:
            base *= 255.0
        for face, normal in zip(
            np.asarray(mesh.faces), np.asarray(mesh.face_normals), strict=False
        ):
            # The fallback used to paint every triangle, including faces on the
            # far side of a closed CAD solid.  Mean-depth sorting is not a full
            # z-buffer, so those back faces could be painted over the visible
            # skin as large dark triangles.  Cull faces whose outward normal
            # points away from the camera before sorting.  This also preserves
            # genuinely visible inner walls of an open shell: their normals
            # point toward the camera when seen through the opening.
            if float(np.dot(normal, direction)) <= 1e-8:
                continue
            pts = [(float(screen[i, 0]), float(screen[i, 1])) for i in face]
            shade = 0.50 + 0.50 * abs(float(np.dot(normal, light)))
            rgb = tuple(int(np.clip(channel * shade, 22, 245)) for channel in base)
            polygons.append((float(np.mean(depth[face])), pts, rgb))

    image = Image.new("RGB", (width, height), (18, 22, 28))
    draw = ImageDraw.Draw(image)
    for _depth, points, rgb in sorted(polygons, key=lambda item: item[0]):
        draw.polygon(points, fill=rgb, outline=(34, 38, 44))
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)


def _joint_pose(model: object, pose_name: str) -> dict[str, float]:
    values: dict[str, float] = {}
    for joint in getattr(model, "joints", getattr(model, "articulations", ())):
        joint_type = getattr(getattr(joint, "articulation_type", None), "value", "")
        limits = getattr(joint, "motion_limits", None)
        if joint_type == "fixed" or limits is None:
            continue
        lower = float(getattr(limits, "lower", 0.0) or 0.0)
        upper_raw = getattr(limits, "upper", lower)
        upper = lower if upper_raw is None else float(upper_raw)
        if pose_name == "closed":
            value = lower
        elif pose_name == "mid":
            value = lower + (upper - lower) * 0.5
        elif pose_name == "max":
            value = upper
        else:
            raise ValueError(f"Unknown pose: {pose_name}")
        values[str(joint.name)] = value
    return values


def render_model_previews(
    slug: str,
    seed: int,
    out_dir: Path,
    *,
    poses: tuple[str, ...],
    views: tuple[str, ...],
    pose_views: tuple[tuple[str, str], ...] | None = None,
) -> list[Path]:
    stem = TEMPLATE_REGISTRY[slug]
    module = importlib.import_module(f"agent.templates.{slug}")
    config = module.config_from_seed(seed)
    assets = AssetContext(out_dir / "assets" / f"{slug}_seed_{seed}")
    model = getattr(module, f"build_{stem}")(config, assets=assets)
    local_meshes: list[tuple[str, trimesh.Trimesh, tuple[float, float, float, float]]] = []
    for part in model.parts:
        for visual in part.visuals:
            mesh = _mesh_geometry(visual.geometry, assets=getattr(part, "assets", None) or assets)
            if mesh is None:
                continue
            mesh = mesh.copy()
            mesh.apply_transform(_matrix(_origin_to_mat4(visual.origin)))
            local_meshes.append((part.name, mesh, _rgba(visual.material)))

    written: list[Path] = []
    directions = _semantic_view_directions(module)
    requested = pose_views or tuple((pose, view) for pose in poses for view in views)
    meshes_by_pose: dict[str, list[tuple[trimesh.Trimesh, tuple[float, float, float, float]]]] = {}
    for pose_name, view_name in requested:
        if pose_name not in meshes_by_pose:
            world = compute_part_world_transforms(model, _joint_pose(model, pose_name))
            pose_meshes: list[tuple[trimesh.Trimesh, tuple[float, float, float, float]]] = []
            for part_name, local_mesh, color in local_meshes:
                part_tf = world.get(part_name)
                if part_tf is None:
                    continue
                mesh = local_mesh.copy()
                mesh.apply_transform(_matrix(part_tf))
                pose_meshes.append((mesh, color))
            meshes_by_pose[pose_name] = pose_meshes
        _render_scene.direction = directions[view_name]  # type: ignore[attr-defined]
        out = out_dir / slug / f"seed_{seed}_{pose_name}_{view_name}.png"
        _render_scene(meshes_by_pose[pose_name], out)
        written.append(out)
    return written


def render_mechanism_evidence(
    slug: str,
    seed: int,
    out_dir: Path,
    *,
    poses: tuple[str, ...],
    views: tuple[str, ...],
    pose_views: tuple[tuple[str, str], ...] | None = None,
    renderer: str = "vtk",
) -> list[Path]:
    """Render enlarged local evidence for hidden/active mechanisms.

    This is deliberately a visual-QA aid, not a second geometry validator.  It
    reuses the exact model and sampled joint pose used by the normal preview,
    but keeps only mechanism-bearing elements so a hidden bilateral guide,
    hinge barrel, pivot, or fold-out support is legible to a reviewer.  The
    complete model remains the source of truth for sweep and clearance tests.
    """

    stem = TEMPLATE_REGISTRY[slug]
    module = importlib.import_module(f"agent.templates.{slug}")
    config = module.config_from_seed(seed)
    assets = AssetContext(out_dir / "assets" / f"{slug}_seed_{seed}")
    model = getattr(module, f"build_{stem}")(config, assets=assets)

    # Keep mechanism names plus the active part's complete local geometry.  A
    # complete active part is important for showing that a rail/hinge belongs
    # to a real drawer, door, shelf, or counter rather than a floating proxy.
    tokens = (
        "guide",
        "track",
        "rail",
        "runner",
        "glide",
        "hinge",
        "knuckle",
        "axle",
        "pivot",
        "bearing",
        "spindle",
        "support",
        "bracket",
        "pocket",
        "well",
        "stop",
        "shoe",
        "stile",
        "deck",
        "mullion",
    )
    active_parts = (
        "door",
        "drawer",
        "fold_out_counter",
        "rotating_shelf",
        "pull_out_shelf",
        "tasting_shelf",
    )
    # Rack/content evidence is useful in the same local frame as a mechanism,
    # but only include the compact source-backed rack elements, never the full
    # carcass which would occlude the active parts again.
    rack_parts = ("display_bottle", "peg_bottle", "glassware")
    structural_visual_tokens = (
        "base",
        "plinth",
        "side",
        "back",
        "bottom",
        "top",
        "deck",
        "panel",
        "stile",
        "post",
        "frame",
        "cavity",
        "socket",
        "mount",
        "riser",
        "receiver",
    )
    local_meshes: list[tuple[str, trimesh.Trimesh, tuple[float, float, float, float]]] = []
    for part in model.parts:
        if slug == "makeup" and part.name == "lid":
            # The outer lid hinge is not part of the palette mechanism under
            # review and otherwise appears as a floating barrel after the lid
            # shell is intentionally filtered from the local evidence view.
            continue
        # Makeup names its complete moving drawers/leaves palette_N.  Keep the
        # whole active palette plus only the case-side mechanism and structural
        # supports.  This prevents a local drawer view from degenerating into
        # floating runner rods with the carcass reaction path filtered away.
        is_makeup_active = slug == "makeup" and part.name.startswith("palette_")
        is_active = is_makeup_active or any(part.name.startswith(prefix) for prefix in active_parts)
        is_rack_content = any(part.name.startswith(prefix) for prefix in rack_parts)
        is_structural_parent = part.name in {
            "carcass",
            "cabinet",
            "cabinet_body",
            "case_body",
        }
        for visual in part.visuals:
            makeup_context = slug == "makeup" and (
                visual.name == "case_frame_base"
                or visual.name.startswith("case_corner_post_")
                or visual.name.startswith("closure_support_stile_")
                or visual.name.startswith("drawer_support_deck_")
                or visual.name.startswith("drawer_guide_")
                or visual.name.startswith("fan_pivot_")
                or visual.name.startswith("accordion_root_")
                or visual.name.startswith("flip_knuckle_")
                or visual.name == "internal_palette_deck"
            )
            if slug == "makeup":
                if not is_active and not makeup_context:
                    continue
            elif (
                not is_active
                and not is_rack_content
                and not (
                    is_structural_parent
                    and any(
                        token in visual.name.lower() for token in structural_visual_tokens
                    )
                )
                and not any(
                    token in visual.name.lower()
                    for token in (*tokens, "rack", "bottle", "peg", "shelf")
                )
            ):
                continue
            mesh = _mesh_geometry(
                visual.geometry,
                assets=getattr(part, "assets", None) or assets,
            )
            if mesh is None:
                continue
            mesh = mesh.copy()
            mesh.apply_transform(_matrix(_origin_to_mat4(visual.origin)))
            local_meshes.append((part.name, mesh, _rgba(visual.material)))

    if not local_meshes:
        return []
    _render_scene.renderer_mode = renderer  # type: ignore[attr-defined]
    directions = _semantic_view_directions(module)
    written: list[Path] = []
    requested = pose_views or tuple((pose, view) for pose in poses for view in views)
    meshes_by_pose: dict[str, list[tuple[trimesh.Trimesh, tuple[float, float, float, float]]]] = {}
    for pose_name, view_name in requested:
        if pose_name in meshes_by_pose:
            meshes = meshes_by_pose[pose_name]
        else:
            world = compute_part_world_transforms(model, _joint_pose(model, pose_name))
            meshes = []
            for part_name, local_mesh, color in local_meshes:
                part_tf = world.get(part_name)
                if part_tf is None:
                    continue
                mesh = local_mesh.copy()
                mesh.apply_transform(_matrix(part_tf))
                meshes.append((mesh, color))
            meshes_by_pose[pose_name] = meshes
        direction = directions.get(view_name)
        if direction is None:
            raise ValueError(f"Unknown view: {view_name}")
        _render_scene.direction = direction  # type: ignore[attr-defined]
        out = out_dir / slug / f"seed_{seed}_{pose_name}_{view_name}_mechanism.png"
        _render_scene(meshes, out)
        written.append(out)
    return written


def make_contact_sheet(paths: list[Path], out: Path) -> None:
    if not paths:
        raise RenderBackendError("cannot build a contact sheet without rendered views")
    thumbs: list[Image.Image] = []
    for path in paths:
        img = Image.open(path).convert("RGB")
        img.thumbnail((300, 234))
        canvas = Image.new("RGB", (300, 260), (232, 235, 240))
        canvas.paste(img, ((300 - img.width) // 2, 0))
        draw = ImageDraw.Draw(canvas)
        draw.text((8, 240), path.parent.name + "/" + path.stem, fill=(30, 35, 45))
        thumbs.append(canvas)

    # Do not pad one- or two-view smoke sheets with empty columns.  The empty
    # background can dominate percentile-based
    # render-health checks and falsely classify a valid object as low contrast.
    cols = min(3, len(thumbs))
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 300, rows * 260), (232, 235, 240))
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % cols) * 300, (i // cols) * 260))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    validate_render_image(out)


def render_contact_sheet(
    slug: str,
    seeds: Iterable[int],
    out_dir: Path,
    *,
    poses: tuple[str, ...] = ("closed", "mid", "max"),
    views: tuple[str, ...] = ("front_iso", "side"),
    pose_views: tuple[tuple[str, str], ...] | None = None,
    pose_views_by_seed: dict[int, tuple[tuple[str, str], ...]] | None = None,
    mechanism_evidence_seeds: Iterable[int] = (),
    mechanism_evidence_plan: dict[int, tuple[tuple[str, str], ...]] | None = None,
    renderer: str = "vtk",
) -> tuple[list[Path], Path]:
    """Render deterministic articulated previews for the visual-QA pipeline."""

    if slug not in TEMPLATE_REGISTRY:
        raise ValueError(f"Unknown template slug: {slug}")
    _render_scene.renderer_mode = renderer  # type: ignore[attr-defined]
    sheet_views: list[Path] = []
    evidence_views: list[Path] = []
    evidence_seeds = {int(seed) for seed in mechanism_evidence_seeds}
    evidence_plan = mechanism_evidence_plan or {}
    with headless_render_display(renderer):
        for seed in seeds:
            seed = int(seed)
            sheet_views.extend(
                render_model_previews(
                    slug,
                    seed,
                    out_dir,
                    poses=poses,
                    views=views,
                    pose_views=(pose_views_by_seed or {}).get(seed, pose_views),
                )
            )
            if seed in evidence_seeds or seed in evidence_plan:
                # Side evidence exposes depth, bilateral runners, pocket
                # receivers, and pivot/hinge clearances for active modules.
                module = importlib.import_module(f"agent.templates.{slug}")
                choices_fn = getattr(module, "slot_choices_for_seed", None)
                choice_text = " ".join(
                    str(item).lower() for item in (choices_fn(seed) if callable(choices_fn) else ())
                )
                local_view = (
                    ("side",)
                    if any(
                        token in choice_text
                        for token in (
                            "drawer",
                            "sliding",
                            "pocket",
                            "pull_out",
                            "pullout",
                            "rotating",
                            "fold_out",
                            "foldout",
                            "counter",
                            "stem_rack",
                        )
                    )
                    else ("front_iso",)
                )
                requested_evidence = evidence_plan.get(seed)
                evidence = render_mechanism_evidence(
                    slug,
                    seed,
                    out_dir,
                    poses=("max",),
                    views=local_view,
                    pose_views=requested_evidence,
                    renderer=renderer,
                )
                if not evidence:
                    raise RenderBackendError(
                        f"hidden mechanism requested but no local evidence geometry found: {slug}"
                    )
                evidence_views.extend(evidence)
        contact_sheet = out_dir / "contact_sheet.png"
        make_contact_sheet(sheet_views, contact_sheet)
    return [*sheet_views, *evidence_views], contact_sheet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slugs", default=",".join(DEFAULT_SLUGS))
    parser.add_argument("--seeds", default="0-2")
    parser.add_argument("--out", type=Path, default=Path("template_preview_renders"))
    parser.add_argument(
        "--poses",
        default="closed",
        help="Comma-separated poses from closed,mid,max.",
    )
    parser.add_argument(
        "--views",
        default=",".join(name for name, _ in VIEW_DIRECTIONS),
        help="Comma-separated views from front_iso,rear_iso,side.",
    )
    parser.add_argument(
        "--renderer",
        choices=("auto", "software", "vtk", "egl"),
        default="vtk",
        help=(
            "Renderer backend (default: vtk). Headless VTK starts one temporary Xvfb; "
            "EGL never falls back to software."
        ),
    )
    args = parser.parse_args()
    _render_scene.renderer_mode = args.renderer  # type: ignore[attr-defined]

    slugs = [slug.strip() for slug in args.slugs.split(",") if slug.strip()]
    seeds = _parse_seeds(args.seeds)
    poses = tuple(p.strip() for p in args.poses.split(",") if p.strip())
    views = tuple(v.strip() for v in args.views.split(",") if v.strip())
    unknown_poses = sorted(set(poses) - {"closed", "mid", "max"})
    unknown_views = sorted(set(views) - {name for name, _ in VIEW_DIRECTIONS})
    if unknown_poses:
        raise SystemExit(f"Unknown pose(s): {', '.join(unknown_poses)}")
    if unknown_views:
        raise SystemExit(f"Unknown view(s): {', '.join(unknown_views)}")
    missing = [slug for slug in slugs if slug not in TEMPLATE_REGISTRY]
    if missing:
        raise SystemExit(f"Unknown template slug(s): {', '.join(missing)}")

    all_paths: list[Path] = []
    with headless_render_display(args.renderer):
        for slug in slugs:
            for seed in seeds:
                paths = render_model_previews(slug, seed, args.out, poses=poses, views=views)
                all_paths.extend(paths)
                print(f"{slug} seed={seed}: {len(paths)} views")

        make_contact_sheet(all_paths, args.out / "contact_sheet.png")
    print(args.out / "contact_sheet.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
