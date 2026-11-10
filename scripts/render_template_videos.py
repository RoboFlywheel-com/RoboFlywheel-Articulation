# SPDX-License-Identifier: Apache-2.0

"""Render articulation videos (MP4) for procedural template seeds.

Each seed is rendered as a short clip where every actuated joint sweeps
synchronously lower -> upper -> lower (smooth cosine ease). Forward kinematics
reuses the SDK's own ``compute_part_world_transforms`` so the motion matches the
exported URDF. Rendering is headless via pyrender's EGL backend; encoding uses
imageio + imageio-ffmpeg.

Mimic joints are resolved automatically by the FK pass and must not be posed
directly, so only non-mimic REVOLUTE/PRISMATIC/CONTINUOUS joints are driven.

This script builds models directly from the template modules (no compiled
records / URDF needed) and writes everything under --out, so it works even when
the repo filesystem is full. The imageio-ffmpeg binary is loaded from --deps
(default ``~/.articraft_render_deps``) and
injected onto sys.path before imageio is imported. Run it from the repo root so
``scripts``/``cli``/``sdk`` resolve on sys.path:

    uv run python scripts/render_template_videos.py \\
        --slugs ceiling_fan,camera_lens --seeds 1-5
"""

from __future__ import annotations

import argparse
import colorsys
import importlib
import math
import os
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image

os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

# Reuse the proven helpers from the still-image preview renderer.
from agent.template_registry import TEMPLATE_REGISTRY  # noqa: E402
from scripts.render_template_previews import (  # noqa: E402
    _matrix,
    _mesh_geometry,
    _parse_seeds,
    _rgba,
)
from sdk import AssetContext  # noqa: E402
from sdk._core.v0.geometry_qc import (  # noqa: E402
    _origin_to_mat4,
    compute_part_world_transforms,
)

VIEW_DIRECTIONS = {
    "front_iso": np.array([1.25, -1.35, 0.85], dtype=float),
    "rear_iso": np.array([-1.15, 1.25, 0.8], dtype=float),
    "side": np.array([0.1, -1.9, 0.45], dtype=float),
}

# Articulation types we actively drive. Mimic joints are skipped (FK resolves
# them); FIXED joints never move.
_DRIVEN_TYPES = ("REVOLUTE", "PRISMATIC", "CONTINUOUS")
# Fallback half-range for continuous / limit-less joints (radians or metres).
_CONTINUOUS_RANGE = 2.0 * math.pi

# Per-part palette ported verbatim from the viewer's "Part colors" mode
# (viewer/web/src/components/viewer3d/SceneCanvas.tsx SEGMENTATION_PALETTE).
# Link order == model.parts order (URDF exporter preserves it 1:1), so coloring
# part i by segment_color_for_index(i) matches what the viewer shows.
_SEGMENTATION_PALETTE = (
    (0xFF, 0x5A, 0x36),
    (0x00, 0xB3, 0xFF),
    (0xFF, 0xD4, 0x00),
    (0x16, 0xC4, 0x7F),
    (0xFF, 0x2F, 0x92),
    (0x7C, 0x5C, 0xFF),
    (0xFF, 0x8A, 0x00),
    (0x00, 0xC2, 0xA8),
    (0xFF, 0x6B, 0x6B),
    (0x14, 0x5A, 0xF2),
    (0xC4, 0xFF, 0x0E),
    (0xFF, 0x3D, 0x77),
)

# Viewer scene background (#e8edf5, from useThreeScene.ts VIEWPORT_BACKGROUND),
# so clips match the viewer instead of sitting on black.
_VIEWER_BG = (0xE8 / 255.0, 0xED / 255.0, 0xF5 / 255.0, 1.0)

# Vertical field of view (deg) and how much the framed sphere underfills it
# (1.0 = sphere exactly touches top/bottom; >1 leaves margin).
_YFOV_DEG = 42.0
_FILL_MARGIN = 1.05

# Three studio key/fill/rim directions (world frame; light shines toward origin).
_LIGHT_RIG = (
    (np.array([1.0, -1.2, 1.4], dtype=float), 3.2),  # key, upper front-right
    (np.array([-1.5, -0.3, 0.4], dtype=float), 1.1),  # fill, low left
    (np.array([-0.4, 1.4, 1.2], dtype=float), 1.8),  # rim, upper back
)


def segment_color_for_index(index: int) -> tuple[float, float, float, float]:
    """Replicate the viewer's segmentColorForIndex (sRGB, 0..1, opaque).

    base = palette[i % 12]; for wrap k = i // 12 the viewer applies
    offsetHSL(+0.07*k hue, +0.06 saturation, 0). We work in sRGB (what pyrender
    consumes); for i < 12 (the common case) this is the exact palette color.
    """
    r, g, b = (c / 255.0 for c in _SEGMENTATION_PALETTE[index % len(_SEGMENTATION_PALETTE)])
    wrap = index // len(_SEGMENTATION_PALETTE)
    if wrap:
        h, lum, s = colorsys.rgb_to_hls(r, g, b)
        h = (h + 0.07 * wrap) % 1.0
        s = min(1.0, s + 0.06)
        r, g, b = colorsys.hls_to_rgb(h, lum, s)
    return (r, g, b, 1.0)


def _resolve_template(slug: str) -> tuple[object, object]:
    """Return (module, build_fn) for a slug. Registry membership is optional.

    Some complete template modules (e.g. robotic_leg) are not in
    TEMPLATE_REGISTRY; fall back to the module's own ``build_<slug>`` (or the
    single non-seeded ``build_*``). Rendering does not require registration or a
    passing sweep.
    """
    module = importlib.import_module(f"agent.templates.{slug}")
    stem = TEMPLATE_REGISTRY.get(slug, slug)
    build_fn = getattr(module, f"build_{stem}", None)
    if build_fn is None:
        cands = [
            n for n in dir(module) if n.startswith("build_") and not n.startswith("build_seeded_")
        ]
        if len(cands) == 1:
            build_fn = getattr(module, cands[0])
    if build_fn is None or not hasattr(module, "config_from_seed"):
        raise ValueError(f"template {slug!r} lacks build_<stem>/config_from_seed")
    return module, build_fn


def _rotate_about_z(vec: np.ndarray, theta: float) -> np.ndarray:
    """Spin a direction vector around the vertical (Z) axis -> turntable orbit.

    Keeps the elevation angle fixed (Z component unchanged) and rotates azimuth,
    so the camera circles the object at a constant height and distance.
    """
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    x, y, z = float(vec[0]), float(vec[1]), float(vec[2])
    return np.array([cos_t * x - sin_t * y, sin_t * x + cos_t * y, z], dtype=float)


def _camera_pose(center: np.ndarray, distance: float, direction: np.ndarray) -> np.ndarray:
    pose = np.eye(4)
    unit = direction / (np.linalg.norm(direction) or 1.0)
    pose[:3, 3] = center + unit * distance
    forward = -unit
    up = np.array([0.0, 0.0, 1.0])
    right = np.cross(forward, up)
    if np.linalg.norm(right) < 1e-6:
        right = np.array([1.0, 0.0, 0.0])
    right = right / np.linalg.norm(right)
    up = np.cross(right, forward)
    pose[:3, :3] = np.stack([right, up, -forward], axis=1)
    return pose


def _joint_drive_spec(model: object) -> list[tuple[str, float, float]]:
    """Return (name, lower, upper) for each joint we actively pose."""
    specs: list[tuple[str, float, float]] = []
    for joint in getattr(model, "joints", []) or []:
        if getattr(joint, "mimic", None) is not None:
            continue
        atype = str(getattr(joint, "articulation_type", "")).rsplit(".", 1)[-1].upper()
        if atype not in _DRIVEN_TYPES:
            continue
        limit = getattr(joint, "limit", None) or getattr(joint, "motion_limits", None)
        lower = getattr(limit, "lower", None)
        upper = getattr(limit, "upper", None)
        if lower is None or upper is None or upper - lower <= 1e-9:
            # Continuous / unbounded joint: sweep a symmetric default range.
            lower, upper = 0.0, _CONTINUOUS_RANGE
        specs.append((str(getattr(joint, "name", "")), float(lower), float(upper)))
    return specs


def _local_visuals(
    model: object,
    color_mode: str,
) -> list[tuple[str, trimesh.Trimesh, tuple[float, float, float, float]]]:
    """Meshes baked into their owning part's local frame (visual.origin applied).

    color_mode='segment' colors every visual of part i with the viewer's
    per-link palette color (matches "Part colors"); 'material' uses the
    template's own material rgba (default gray when unset).
    """
    items: list[tuple[str, trimesh.Trimesh, tuple[float, float, float, float]]] = []
    for part_index, part in enumerate(model.parts):
        part_assets = getattr(part, "assets", None)
        seg_color = segment_color_for_index(part_index)
        for visual in part.visuals:
            mesh = _mesh_geometry(visual.geometry, assets=part_assets)
            if mesh is None:
                continue
            mesh = mesh.copy()
            mesh.apply_transform(_matrix(_origin_to_mat4(visual.origin)))
            color = seg_color if color_mode == "segment" else _rgba(visual.material)
            items.append((part.name, mesh, color))
    return items


def _posed_world_meshes(
    locals_: list[tuple[str, trimesh.Trimesh, tuple[float, float, float, float]]],
    world: dict[str, object],
) -> list[tuple[trimesh.Trimesh, tuple[float, float, float, float]]]:
    out: list[tuple[trimesh.Trimesh, tuple[float, float, float, float]]] = []
    for part_name, mesh, color in locals_:
        part_tf = world.get(part_name)
        if part_tf is None:
            continue
        m = mesh.copy()
        m.apply_transform(_matrix(part_tf))
        out.append((m, color))
    return out


def _bounds_union(
    meshes_a: list[tuple[trimesh.Trimesh, object]],
    meshes_b: list[tuple[trimesh.Trimesh, object]],
) -> tuple[np.ndarray, float]:
    combined = trimesh.util.concatenate([m for m, _ in meshes_a] + [m for m, _ in meshes_b])
    center = np.asarray(combined.bounding_box.centroid, dtype=float)
    radius = float(np.linalg.norm(combined.bounding_box.extents)) or 1.0
    return center, radius


def _render_seed_video(
    slug: str,
    seed: int,
    out_dir: Path,
    *,
    frames: int,
    fps: int,
    size: tuple[int, int],
    view: str,
    orbit_revolutions: float,
    color_mode: str,
    ssaa: int,
    writer_kwargs: dict,
) -> Path | None:
    import imageio.v2 as imageio
    import pyrender

    module, build_fn = _resolve_template(slug)
    config = module.config_from_seed(seed)
    assets = AssetContext(out_dir / "assets" / f"{slug}_seed_{seed}")
    model = build_fn(config, assets=assets)

    locals_ = _local_visuals(model, color_mode)
    if not locals_:
        print(f"  [skip] {slug} seed={seed}: no renderable meshes")
        return None

    drive = _joint_drive_spec(model)

    # Stable camera: union of closed (all-lower) and open (all-upper) bounds.
    closed = {n: lo for n, lo, _ in drive}
    opened = {n: hi for n, _, hi in drive}
    center, radius = _bounds_union(
        _posed_world_meshes(locals_, compute_part_world_transforms(model, closed)),
        _posed_world_meshes(locals_, compute_part_world_transforms(model, opened)),
    )
    base_dir = VIEW_DIRECTIONS[view]
    # Fit the union bounding sphere (radius = 0.5 * AABB diagonal) to the vertical
    # FOV so the object fills the frame; vertical is limiting for wide aspects.
    cam_distance = 0.5 * radius / math.sin(math.radians(_YFOV_DEG / 2.0)) * _FILL_MARGIN

    width, height = size
    ssaa = max(1, int(ssaa))
    renderer = pyrender.OffscreenRenderer(width * ssaa, height * ssaa)
    out_path = out_dir / slug / f"{slug}_seed_{seed}.mp4"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # World-fixed studio key/fill/rim poses (only orientation matters for a
    # directional light, so the radius arg is arbitrary).
    light_poses = [(_camera_pose(center, 1.0, d), intensity) for d, intensity in _LIGHT_RIG]

    writer = imageio.get_writer(out_path, fps=fps, **writer_kwargs)
    try:
        for i in range(frames):
            frac = i / frames
            # Smooth cosine ease: joints sweep 0 -> 1 -> 0 across the full clip.
            phase = 0.5 - 0.5 * math.cos(2.0 * math.pi * frac)
            joint_pos = {n: lo + (hi - lo) * phase for n, lo, hi in drive}
            world = compute_part_world_transforms(model, joint_pos)
            meshes = _posed_world_meshes(locals_, world)

            # Turntable orbit: spin the (fixed-distance) camera around Z.
            cam_dir = _rotate_about_z(base_dir, 2.0 * math.pi * orbit_revolutions * frac)
            cam_pose = _camera_pose(center, cam_distance, cam_dir)

            scene = pyrender.Scene(bg_color=_VIEWER_BG, ambient_light=(0.4, 0.4, 0.4))
            for mesh, color in meshes:
                material = pyrender.MetallicRoughnessMaterial(
                    baseColorFactor=color, metallicFactor=0.0, roughnessFactor=0.55
                )
                scene.add(pyrender.Mesh.from_trimesh(mesh, material=material, smooth=False))
            cam = pyrender.PerspectiveCamera(yfov=math.radians(_YFOV_DEG))
            scene.add(cam, pose=cam_pose)
            # Three-point studio rig + a soft camera headlight so no orbit angle
            # falls into full shadow.
            for pose, intensity in light_poses:
                scene.add(
                    pyrender.DirectionalLight(color=np.ones(3), intensity=intensity), pose=pose
                )
            scene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=0.8), pose=cam_pose)
            color_buf, _ = renderer.render(scene)
            if ssaa > 1:
                color_buf = np.asarray(
                    Image.fromarray(color_buf).resize((width, height), Image.LANCZOS)
                )
            writer.append_data(color_buf)
    finally:
        writer.close()
        renderer.delete()

    print(f"  {slug} seed={seed}: {frames}f, {len(drive)} driven joints -> {out_path}")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render template articulation MP4s.")
    parser.add_argument("--slugs", required=True, help="Comma-separated template slugs.")
    parser.add_argument("--seeds", default="1-5", help="Seed list/ranges, e.g. '1-5' or '1,3,5'.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("/tmp/articraft_render_out"),
        help="Output directory.",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=144,
        help="Frames per open-close cycle / full orbit (144 @ 24fps = 6s).",
    )
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument(
        "--ssaa",
        type=int,
        default=2,
        help="Supersampling factor: render at ssaa x resolution then downscale (2 = 4K->1080p).",
    )
    parser.add_argument(
        "--color-mode",
        choices=("segment", "material"),
        default="segment",
        help="'segment' = viewer Part-colors palette per link; 'material' = template's own rgba.",
    )
    parser.add_argument(
        "--view",
        choices=tuple(VIEW_DIRECTIONS),
        default="front_iso",
        help="Base camera direction (orbit starts here).",
    )
    parser.add_argument(
        "--orbit",
        type=float,
        default=0.5,
        help="Turntable revolutions over the clip (0.5 = 180 deg sweep; 1.0 = full 360; 0 = static).",
    )
    parser.add_argument(
        "--deps",
        type=Path,
        default=Path.home() / ".articraft_render_deps",
        help="Dir containing imageio-ffmpeg (injected on sys.path so MP4 encoding works).",
    )
    args = parser.parse_args()

    if args.deps and args.deps.exists():
        sys.path.insert(0, str(args.deps))

    slugs = [s.strip() for s in args.slugs.split(",") if s.strip()]
    seeds = _parse_seeds(args.seeds)
    bad: list[str] = []
    for s in slugs:
        try:
            _resolve_template(s)
        except (ImportError, ValueError) as exc:
            bad.append(f"{s} ({exc})")
    if bad:
        raise SystemExit("Unusable template slug(s): " + "; ".join(bad))

    writer_kwargs = dict(
        codec="libx264",
        pixelformat="yuv420p",
        macro_block_size=8,
        ffmpeg_log_level="error",
        output_params=["-crf", "17", "-preset", "slow"],
    )

    written: list[Path] = []
    for slug in slugs:
        for seed in seeds:
            path = _render_seed_video(
                slug,
                seed,
                args.out,
                frames=args.frames,
                fps=args.fps,
                size=(args.width, args.height),
                view=args.view,
                orbit_revolutions=args.orbit,
                color_mode=args.color_mode,
                ssaa=args.ssaa,
                writer_kwargs=writer_kwargs,
            )
            if path is not None:
                written.append(path)

    print(f"\nDone: {len(written)} clips under {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
