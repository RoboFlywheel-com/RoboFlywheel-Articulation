# SPDX-License-Identifier: Apache-2.0

"""Render template articulation MP4s with Blender Cycles (GPU path tracing).

Studio-quality variant of render_template_videos.py: instead of pyrender's flat
forward shading, this drives a real Blender Cycles scene (soft shadows, ambient
occlusion, global illumination, OptiX denoise) for a look close to the Articraft
showcase (articraft3d.github.io).

All scene math is shared with the pyrender script (FK world matrices, turntable
camera poses, the viewer's per-link segment palette). This orchestrator runs in
the project venv: it builds the model, bakes per-frame transforms, exports each
part mesh to PLY + a job.json, then spawns Blender (its own bundled Python) to
path-trace one PNG per frame, and finally encodes the frames to MP4.

    uv run python scripts/render_template_videos_blender.py \\
        --slugs robotic_leg --seeds 1-5

Procedural templates are mostly material-less, so parts are colored with the
viewer segment palette by default; Cycles still adds the shadows/AO/GI that make
it read as a studio render rather than a flat one.
"""

from __future__ import annotations

import argparse
import json
import math  # noqa: E402
import os
import queue
import re  # noqa: E402
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

# Reuse every bit of scene math from the pyrender renderer so the two stay in
# lockstep (same FK, same orbit, same palette, same framing).
from scripts.render_template_videos import (
    _FILL_MARGIN,
    _YFOV_DEG,
    _bounds_union,
    _camera_pose,
    _joint_drive_spec,
    _matrix,
    _mesh_geometry,
    _parse_seeds,
    _posed_world_meshes,
    _resolve_template,
    _rotate_about_z,
    segment_color_for_index,
)
from sdk import AssetContext  # noqa: E402
from sdk._core.v0.assets import (  # noqa: E402
    AssetSession,
    activate_asset_session,
)
from sdk._core.v0.geometry_qc import (  # noqa: E402
    _origin_to_mat4,
    compute_part_world_transforms,
)

_DEFAULT_BLENDER = os.environ.get("BLENDER_PATH", "blender")
_WORKER = Path(__file__).resolve().parent / "_blender_worker.py"


def _flat16(mat: object) -> list[float]:
    arr = np.asarray(mat, dtype=float).reshape(4, 4)
    return [float(v) for v in arr.flatten()]


def _scene_extents(local_meshes, model, closed, opened, mid):
    """Union AABB (min corner, max corner) over closed/open/mid poses."""
    mins = []
    maxs = []
    for joints in (closed, opened, mid):
        for mesh, _ in _posed_world_meshes(
            local_meshes, compute_part_world_transforms(model, joints)
        ):
            bounds = mesh.bounds
            mins.append(bounds[0])
            maxs.append(bounds[1])
    return np.min(mins, axis=0), np.max(maxs, axis=0)


def _mat_rgba(material):
    rgba = getattr(material, "rgba", None)
    if rgba is None:
        rgba = getattr(material, "color", None)
    return tuple(float(v) for v in rgba) if rgba is not None else None


def _resolve_material_ref(ref, lookup: dict):
    """Resolve a visual's material to (name, rgba).

    Visuals reference materials by NAME (e.g. 'armor', 'metal'); the actual rgba
    lives in model.materials. This is exactly what the viewer/URDF do, and why
    the viewer shows colors where naive ``visual.material.rgba`` reads None.
    """
    if isinstance(ref, str):
        mat = lookup.get(ref)
        return ref, (_mat_rgba(mat) if mat is not None else None)
    if ref is not None:
        return str(getattr(ref, "name", "") or ""), _mat_rgba(ref)
    return "", None


def _resolve_material_spec(name: str, rgba) -> dict:
    """Port of viewer/web/.../materials.ts resolveVisualMaterialSpec.

    Maps a URDF material (name + rgba) to PBR params identical to the viewer:
    neutral gray default, named presets (glass/metal/reflector/bakelite/felt),
    and the bright-neutral softening. Lets material-bearing templates render the
    same way the viewer/showcase does.
    """
    spec = {
        "base_color": [0.74, 0.74, 0.72],
        "opacity": 1.0,
        "metallic": 0.05,
        "roughness": 0.48,
        "transmission": 0.0,
        "ior": 1.45,
        "clearcoat": 0.0,
        "clearcoat_roughness": 0.2,
    }
    if rgba is not None:
        spec["base_color"] = [float(c) for c in rgba[:3]]
        spec["opacity"] = float(rgba[3]) if len(rgba) >= 4 else 1.0

    low = (name or "").lower()
    tokens = {t for t in re.split(r"[^a-z0-9]+", low) if t}
    transparent_desc = tokens & {
        "clear",
        "glass",
        "transparent",
        "translucent",
        "smoked",
        "frosted",
    }
    transparent_plastic = tokens & {"polycarbonate", "acrylic", "plexi", "plexiglass", "lexan"}
    if transparent_desc or (transparent_plastic and spec["opacity"] < 0.999):
        spec.update(
            metallic=0.0,
            roughness=0.08,
            transmission=max(0.45, 1.0 - spec["opacity"] * 0.55),
            ior=1.45,
            clearcoat=0.9,
            clearcoat_roughness=0.06,
        )
        return spec
    if "reflector" in low:
        spec.update(
            metallic=0.9,
            roughness=0.18,
            opacity=max(spec["opacity"], 0.78),
            clearcoat=0.18,
            clearcoat_roughness=0.12,
        )
        return spec
    if "brass" in low or "metal" in low:
        spec.update(metallic=0.88, roughness=0.22, clearcoat=0.16, clearcoat_roughness=0.18)
        return spec
    if "bakelite" in low:
        spec.update(metallic=0.02, roughness=0.38, clearcoat=0.24, clearcoat_roughness=0.2)
        return spec
    if "felt" in low:
        spec.update(metallic=0.0, roughness=0.92, clearcoat=0.0)

    c = spec["base_color"]
    if (
        max(c) > 0.78
        and max(c) - min(c) < 0.08
        and spec["metallic"] <= 0.2
        and spec["transmission"] <= 0.01
    ):
        target = [0.82, 0.82, 0.78]
        spec["base_color"] = [c[i] + (target[i] - c[i]) * 0.38 for i in range(3)]
        spec["roughness"] = max(spec["roughness"], 0.62)
        spec["clearcoat"] = min(spec["clearcoat"], 0.08)
    return spec


def _segment_spec(rgb) -> dict:
    """Flat-ish colored plastic for the viewer's per-part palette (segment mode)."""
    return {
        "base_color": [float(c) for c in rgb[:3]],
        "opacity": 1.0,
        "metallic": 0.0,
        "roughness": 0.5,
        "transmission": 0.0,
        "ior": 1.45,
        "clearcoat": 0.0,
        "clearcoat_roughness": 0.2,
    }


def _extract_visuals(model, color_mode):
    """[(part_name, part_index, local_mesh, pbr_spec)] for every renderable visual."""
    lookup = {}
    for mat in getattr(model, "materials", []) or []:
        nm = getattr(mat, "name", None)
        if isinstance(nm, str):
            lookup[nm] = mat
    out = []
    for i, part in enumerate(model.parts):
        part_assets = getattr(part, "assets", None)
        seg = segment_color_for_index(i)
        for visual in part.visuals:
            mesh = _mesh_geometry(visual.geometry, assets=part_assets)
            if mesh is None:
                continue
            mesh = mesh.copy()
            mesh.apply_transform(_matrix(_origin_to_mat4(visual.origin)))
            if color_mode == "segment":
                spec = _segment_spec(seg)
            else:
                name, rgba = _resolve_material_ref(getattr(visual, "material", None), lookup)
                spec = _resolve_material_spec(name, rgba)
            out.append((part.name, i, mesh, spec))
    return out


def _build_job(
    slug,
    seed,
    out_dir,
    job_dir,
    *,
    frames,
    view,
    view_dir,
    orbit_revolutions,
    color_mode,
    width,
    height,
    samples,
    pose_phase=None,
):
    module, build_fn = _resolve_template(slug)
    config = module.config_from_seed(seed)
    assets = AssetContext(out_dir / "assets" / f"{slug}_seed_{seed}")
    # Templates that compile inside build (e.g. clamp_joint_limits) resolve
    # relative mesh refs against model.assets; without an active session the
    # meshes land in an ephemeral temp root and that resolve fails.
    with activate_asset_session(
        AssetSession(assets.root, mesh_subdir=assets.mesh_subdir)
    ):
        model = build_fn(config, assets=assets)

    extracted = _extract_visuals(model, color_mode)  # [(part_name, part_index, mesh, spec)]
    if not extracted:
        return None
    local_meshes = [(pn, mesh, None) for pn, _pi, mesh, _spec in extracted]

    part_index = {part.name: i for i, part in enumerate(model.parts)}
    drive = _joint_drive_spec(model)
    closed = {n: lo for n, lo, _ in drive}
    opened = {n: hi for n, _, hi in drive}
    mid = {n: 0.5 * (lo + hi) for n, lo, hi in drive}

    center, radius = _bounds_union(
        _posed_world_meshes(local_meshes, compute_part_world_transforms(model, closed)),
        _posed_world_meshes(local_meshes, compute_part_world_transforms(model, opened)),
    )
    cam_distance = 0.5 * radius / math.sin(math.radians(_YFOV_DEG / 2.0)) * _FILL_MARGIN
    base_dir = np.asarray(
        view_dir
        if view_dir is not None
        else {
            "front_iso": [1.25, -1.35, 0.85],
            "rear_iso": [-1.15, 1.25, 0.8],
            "side": [0.1, -1.9, 0.45],
        }[view],
        dtype=float,
    )
    sphere_r = 0.5 * radius
    aabb_min, _aabb_max = _scene_extents(local_meshes, model, closed, opened, mid)

    # Export one PLY per visual (local frame; visual.origin already baked in).
    visuals = []
    meshes_dir = job_dir / "meshes"
    meshes_dir.mkdir(parents=True, exist_ok=True)
    for i, (_part_name, part_idx, mesh, spec) in enumerate(extracted):
        rel = f"meshes/vis_{i:04d}.ply"
        mesh.export(job_dir / rel)
        visuals.append({"mesh": rel, "spec": spec, "part": part_idx})

    # Per-part world matrix and camera pose for every frame.
    parts_world = [[None] * frames for _ in model.parts]
    cam_poses = []
    for f in range(frames):
        frac = f / frames
        # The sweep starts and ends at each joint's lower limit, so frame 0 is the
        # fully-closed pose. For a still (`--frames 1`) that is often the least
        # recognisable configuration of the category -- a garlic press reads as two
        # bare sticks closed, and shows its chamber and plunger only once opened.
        # `--pose-phase` pins every frame to a fixed point of the same travel.
        if pose_phase is None:
            phase = 0.5 - 0.5 * math.cos(2.0 * math.pi * frac)
        else:
            phase = pose_phase
        joint_pos = {n: lo + (hi - lo) * phase for n, lo, hi in drive}
        world = compute_part_world_transforms(model, joint_pos)
        for part in model.parts:
            mat = world.get(part.name)
            parts_world[part_index[part.name]][f] = (
                _flat16(mat) if mat is not None else _flat16(np.eye(4))
            )
        cam_dir = _rotate_about_z(base_dir, 2.0 * math.pi * orbit_revolutions * frac)
        cam_poses.append(_flat16(_camera_pose(center, cam_distance, cam_dir)))

    # Studio lights scaled to the scene; energy ~ distance^2 so size cancels out.
    # One overhead-front key (soft shadow lands under the object) + a gentle fill.
    light_dirs = [([0.3, -0.7, 1.6], 45.0), ([-0.6, -0.9, 0.5], 12.0)]
    lights = []
    for d, gain in light_dirs:
        d = np.asarray(d, dtype=float)
        d = d / (np.linalg.norm(d) or 1.0)
        dist = 3.0 * sphere_r
        loc = (center + d * dist).tolist()
        lights.append({"loc": loc, "energy": gain * dist * dist, "size": 1.5 * sphere_r})

    job = {
        "render": {"width": width, "height": height, "samples": samples, "frames": frames},
        "view_transform": "Standard",
        # Viewer background (#e8edf5) for camera rays; dim neutral fill for light.
        "world": {"bg_color": [0.9098, 0.9294, 0.9608], "bg_strength": 1.0, "fill_strength": 0.35},
        "ground": {"enabled": True, "z": float(aabb_min[2]) - 1e-3, "size": 50.0 * sphere_r},
        "camera": {"center": center.tolist(), "angle_y_deg": _YFOV_DEG, "poses": cam_poses},
        "visuals": visuals,
        "parts_world": parts_world,
    }
    job["lights"] = lights
    with open(job_dir / "job.json", "w") as fh:
        json.dump(job, fh)
    return job


def _encode(job_dir: Path, out_path: Path, fps: int, writer_kwargs: dict) -> bool:
    import imageio.v2 as imageio

    frames_dir = job_dir / "frames"
    frame_files = sorted(frames_dir.glob("frame_*.png"))
    if not frame_files:
        return False
    out_path.parent.mkdir(parents=True, exist_ok=True)
    writer = imageio.get_writer(out_path, fps=fps, **writer_kwargs)
    try:
        for fp in frame_files:
            writer.append_data(imageio.imread(fp))
    finally:
        writer.close()
    return True


def _detect_gpu_count() -> int:
    try:
        out = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, timeout=15)
        n = sum(1 for line in out.stdout.splitlines() if line.strip().startswith("GPU "))
        return n or 1
    except (OSError, subprocess.SubprocessError):
        return 1


def _render_clip(args, job_dir: Path, out_path: Path, gpu_id, writer_kwargs, label: str):
    """Run Blender (pinned to one GPU) then encode the frames. Thread-safe."""
    env = dict(os.environ)
    if gpu_id is not None:
        env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    proc = subprocess.run(
        [
            args.blender,
            "-b",
            "--factory-startup",
            "-noaudio",
            "-P",
            str(_WORKER),
            "--",
            str(job_dir),
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    if proc.returncode != 0:
        return (
            None,
            f"[FAIL] {label}: blender exit {proc.returncode}\n{proc.stdout[-1000:]}\n{proc.stderr[-500:]}",
        )
    if _encode(job_dir, out_path, args.fps, writer_kwargs):
        if not args.keep_frames:
            shutil.rmtree(job_dir / "frames", ignore_errors=True)
        return out_path, f"{label}: {args.frames}f cycles (gpu {gpu_id}) -> {out_path}"
    return None, f"[FAIL] {label}: no frames produced"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render template MP4s with Blender Cycles.")
    parser.add_argument("--slugs", required=True, help="Comma-separated template slugs.")
    parser.add_argument("--seeds", default="1-5", help="Seed list/ranges, e.g. '1-5'.")
    parser.add_argument("--out", type=Path, default=Path("/tmp/articraft_render_out"))
    parser.add_argument("--frames", type=int, default=144, help="144 @ 24fps = 6s.")
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--samples", type=int, default=48, help="Cycles samples (OptiX-denoised).")
    parser.add_argument("--orbit", type=float, default=0.5, help="Turntable revolutions (0.5=180).")
    parser.add_argument(
        "--pose-phase",
        type=float,
        default=None,
        help=(
            "Pin every frame to a fixed point of the joint travel, 0=closed .. 1=open, "
            "instead of sweeping. Use for stills/contact sheets: frame 0 of the sweep is "
            "the fully-closed pose, which hides the mechanism on hinged categories. "
            "0.45 is a good default for a two-arm press."
        ),
    )
    parser.add_argument("--view", choices=("front_iso", "rear_iso", "side"), default="front_iso")
    parser.add_argument(
        "--view-dir",
        default="",
        help="Custom camera START direction 'x,y,z' (overrides --view); orbit begins here.",
    )
    parser.add_argument("--color-mode", choices=("segment", "material"), default="material")
    parser.add_argument("--blender", default=_DEFAULT_BLENDER, help="Path to the Blender binary.")
    parser.add_argument(
        "--deps", type=Path, default=Path.home() / ".articraft_render_deps"
    )
    parser.add_argument(
        "--keep-frames", action="store_true", help="Keep PNG frames after encoding."
    )
    parser.add_argument(
        "--skip-existing", action="store_true", help="Skip clips whose output mp4 already exists."
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Parallel Blender processes (one GPU each). 0 = use all detected GPUs.",
    )
    parser.add_argument(
        "--gpu-ids",
        default="",
        help="Comma-separated GPU ids to use (default: 0..N-1 from nvidia-smi).",
    )
    args = parser.parse_args()

    if args.deps and args.deps.exists():
        sys.path.insert(0, str(args.deps))
    if not Path(args.blender).exists():
        raise SystemExit(f"Blender binary not found: {args.blender}")

    slugs = [s.strip() for s in args.slugs.split(",") if s.strip()]
    seeds = _parse_seeds(args.seeds)
    view_dir = [float(x) for x in args.view_dir.split(",")] if args.view_dir.strip() else None
    writer_kwargs = dict(
        codec="libx264",
        pixelformat="yuv420p",
        macro_block_size=8,
        ffmpeg_log_level="error",
        output_params=["-crf", "17", "-preset", "slow"],
    )

    # GPU pool: --gpu-ids overrides; otherwise 0..N-1, capped to --workers.
    if args.gpu_ids.strip():
        all_gpus = [int(x) for x in args.gpu_ids.split(",") if x.strip()]
    else:
        all_gpus = list(range(_detect_gpu_count()))
    n_workers = len(all_gpus) if args.workers <= 0 else min(args.workers, len(all_gpus))
    gpu_ids = all_gpus[:n_workers] or [None]

    # Phase 1: build every job (model + FK transforms + PLYs) in the venv.
    clips = []  # (job_dir, out_path, label)
    for slug in slugs:
        for seed in seeds:
            final_mp4 = args.out / slug / f"{slug}_seed_{seed}.mp4"
            if args.skip_existing and final_mp4.exists():
                print(f"  [have] {slug} seed={seed}", flush=True)
                continue
            job_dir = args.out / "_blender_jobs" / f"{slug}_seed_{seed}"
            if job_dir.exists():
                shutil.rmtree(job_dir)
            job_dir.mkdir(parents=True, exist_ok=True)
            try:
                job = _build_job(
                    slug,
                    seed,
                    args.out,
                    job_dir,
                    frames=args.frames,
                    view=args.view,
                    view_dir=view_dir,
                    orbit_revolutions=args.orbit,
                    pose_phase=args.pose_phase,
                    color_mode=args.color_mode,
                    width=args.width,
                    height=args.height,
                    samples=args.samples,
                )
            except Exception as exc:  # noqa: BLE001 - one bad template must not kill the batch
                print(f"  [build-FAIL] {slug} seed={seed}: {type(exc).__name__}: {exc}")
                continue
            if job is None:
                print(f"  [skip] {slug} seed={seed}: no renderable meshes")
                continue
            clips.append(
                (job_dir, args.out / slug / f"{slug}_seed_{seed}.mp4", f"{slug} seed={seed}")
            )

    print(f"Built {len(clips)} jobs; rendering on GPUs {gpu_ids} ({len(gpu_ids)}-way parallel)...")

    # Phase 2: render in parallel, each clip pinned to one free GPU.
    gpu_q: queue.Queue = queue.Queue()
    for g in gpu_ids:
        gpu_q.put(g)

    def _task(job_dir, out_path, label):
        g = gpu_q.get()
        try:
            return _render_clip(args, job_dir, out_path, g, writer_kwargs, label)
        finally:
            gpu_q.put(g)

    written = []
    with ThreadPoolExecutor(max_workers=len(gpu_ids)) as ex:
        futures = [ex.submit(_task, jd, op, lbl) for jd, op, lbl in clips]
        for fut in as_completed(futures):
            out_path, msg = fut.result()
            print("  " + msg)
            if out_path is not None:
                written.append(out_path)

    print(f"\nDone: {len(written)}/{len(clips)} clips under {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
