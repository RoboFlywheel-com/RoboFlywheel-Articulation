# SPDX-License-Identifier: Apache-2.0

"""Render teaser stills with pool-sampled unified PBR materials.

For every (slug, seed): build the template model, run the appearance pipeline
(exact-class pool sampling with a seed-local RNG, identical to
articraft/materialization.py), bake each visual's mesh to PLY, and hand a job
to Blender Cycles (_teaser_blender_worker.py) for a high-resolution studio
still. Appearance-only visuals keep the viewer's flat material mapping.

Usage:
    uv run python scripts/render_teaser_materials.py \
        --slugs Astronomy_Return_capsule --seeds 18,89 \
        --out /tmp/extracted/teaser_renders
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from articraft.appearance.retrieval import (  # noqa: E402
    _OPTICAL_MATERIAL_CLASS_PARENTS,
    appearance_requests_from_model,
)
from articraft.appearance.unified_runtime import (  # noqa: E402
    UnifiedMaterialLibrary,
    load_unified_material_library,
)
from articraft.materialization import select_material  # noqa: E402
from scripts.render_template_videos import (  # noqa: E402
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
)
from scripts.render_template_videos_blender import (  # noqa: E402
    _detect_gpu_count,
    _flat16,
    _resolve_material_spec,
)
from sdk import AssetContext  # noqa: E402
from sdk._core.v0.assets import AssetSession, activate_asset_session  # noqa: E402
from sdk._core.v0.geometry_qc import _origin_to_mat4, compute_part_world_transforms  # noqa: E402

_DEFAULT_BLENDER = os.environ.get("BLENDER_PATH", "blender")
_WORKER = Path(__file__).resolve().parent / "_teaser_blender_worker.py"
_LIBRARY_POINTER = REPO_ROOT / "pbr_material_library" / "unified" / "latest.json"

# Viewer front/rear 3/4 studio directions.
_VIEW_DIRECTIONS = {
    "front_iso": np.array([1.25, -1.35, 0.85], dtype=float),
    "rear_iso": np.array([-1.15, 1.25, 0.8], dtype=float),
    "side": np.array([0.1, -1.9, 0.45], dtype=float),
}


def _surface_key(part_name: str, visual, index: int) -> str:
    visual_name = getattr(visual, "name", None) or f"visual_{index}"
    return f"{part_name}::{visual_name}"


def _pbr_spec(library: UnifiedMaterialLibrary, material, cache: dict) -> dict:
    material_id = material.material_id
    cached = cache.get(material_id)
    if cached is not None:
        return cached
    appearance = material.appearance
    channels = appearance.get("channels") or {}
    contract = appearance.get("mapping_contract") or {}
    tile_size = appearance.get("texture_size_m") or contract.get("tile_size_m") or 1.0
    textures = {}
    factors = {}
    for channel_name, channel in channels.items():
        if not isinstance(channel, dict):
            continue
        if channel.get("kind") == "texture":
            source = library.texture_source(
                material, str(channel.get("path") or ""), str(channel.get("sha256") or "")
            )
            textures[channel_name] = {
                "path": str(source),
                "colorspace": str(channel.get("colorspace") or "Non-Color"),
            }
        else:
            factors[channel_name] = channel.get("value")
    spec = {
        "kind": "pbr",
        "material_id": material_id,
        "material_class_id": material.material_class_id,
        "optical": material.material_class_id.split(".", 1)[0] in _OPTICAL_MATERIAL_CLASS_PARENTS,
        "tile_size_m": float(tile_size),
        "textures": textures,
        "factors": factors,
    }
    cache[material_id] = spec
    return spec


def _sample_materials(library, model, material_seed: int):
    """Group-sampled materials, mirroring materialization._materialize_seed."""
    requests = appearance_requests_from_model(model, require_all=True)
    if not requests:
        raise RuntimeError("template produced no appearance requests")
    by_surface = {request.surface_key: request for request in requests}

    material_groups: dict[tuple[str, str], object] = {}
    for request in requests:
        if request.asset_type == "appearance_only":
            continue
        if request.material_class_id is None:
            raise RuntimeError(f"visual {request.surface_key!r} has no material class")
        group_key = request.selection_group_key or request.surface_key
        material_groups.setdefault((group_key, request.material_class_id), request)

    rng = random.Random(int(material_seed))
    selected: dict[tuple[str, str], object] = {}
    for draw_order, group_key in enumerate(sorted(material_groups)):
        selected[group_key] = select_material(
            library, material_groups[group_key], rng=rng, draw_order=draw_order
        )
    return by_surface, material_groups, selected


def _build_job(
    *,
    slug: str,
    seed: int,
    material_seed: int,
    library,
    job_dir: Path,
    views: list[str],
    pose_phase: float,
    width: int,
    height: int,
    samples: int,
    overrides: dict | None = None,
) -> dict:
    module, build_fn = _resolve_template(slug)
    config = module.config_from_seed(seed)
    assets = AssetContext(job_dir / "assets" / f"{slug}_seed_{seed}")
    with activate_asset_session(AssetSession(assets.root, mesh_subdir=assets.mesh_subdir)):
        model = build_fn(config, assets=assets)

    by_surface, _groups, selected = _sample_materials(library, model, material_seed)

    slug_overrides = (overrides or {}).get(slug) or {}
    for group_key, sel in list(selected.items()):
        override_id = slug_overrides.get(sel.material.material_class_id)
        if override_id:
            selected[group_key] = replace(
                sel,
                material=library.materials_by_id[override_id],
                selection_index=-1,
            )

    # Meshes baked into their owning part's local frame (visual.origin applied).
    extracted = []  # (surface_key, part_name, part_index, mesh)
    spec_cache: dict[str, dict] = {}
    for part_index, part in enumerate(model.parts):
        part_assets = getattr(part, "assets", None)
        for visual_index, visual in enumerate(part.visuals):
            mesh = _mesh_geometry(visual.geometry, assets=part_assets)
            if mesh is None:
                continue
            mesh = mesh.copy()
            mesh.apply_transform(_matrix(_origin_to_mat4(visual.origin)))
            extracted.append(
                (_surface_key(part.name, visual, visual_index), part.name, part_index, mesh)
            )
    if not extracted:
        raise RuntimeError(f"{slug} seed {seed} produced no visual meshes")

    visuals = []
    meshes_dir = job_dir / "meshes"
    meshes_dir.mkdir(parents=True, exist_ok=True)
    material_report = {}
    for i, (surface_key, part_name, part_index, mesh) in enumerate(extracted):
        request = by_surface.get(surface_key)
        rel = f"meshes/vis_{i:04d}.ply"
        mesh.export(job_dir / rel)
        if request is None:
            raise RuntimeError(f"surface {surface_key!r} missing from appearance requests")
        if request.asset_type == "appearance_only":
            spec = {
                "kind": "flat",
                **_resolve_material_spec(request.material_name or "", request.rgba),
            }
        else:
            group_key = (
                request.selection_group_key or request.surface_key,
                request.material_class_id,
            )
            sel = selected[group_key]
            spec = _pbr_spec(library, sel.material, spec_cache)
            material_report[surface_key] = {
                "material_id": sel.material.material_id,
                "material_class_id": sel.material.material_class_id,
                "physics": sel.material.physics_values,
                "selection_index": sel.selection_index,
                "pool_count": sel.pool_count,
            }
        visuals.append({"mesh": rel, "spec": spec, "part": part_index})

    # Single exhibit pose pinned at pose_phase of each joint's travel.
    drive = _joint_drive_spec(model)
    joint_pos = {n: lo + (hi - lo) * pose_phase for n, lo, hi in drive}
    world = compute_part_world_transforms(model, joint_pos)

    local_meshes = [(part_name, mesh, None) for _sk, part_name, _pi, mesh in extracted]
    posed = _posed_world_meshes(local_meshes, world)
    if not posed:
        raise RuntimeError(f"{slug} seed {seed} produced no posed meshes")
    center, radius = _bounds_union(posed, posed)
    sphere_r = max(0.5 * radius, 1e-9)
    cam_distance = 0.5 * radius / math.sin(math.radians(_YFOV_DEG / 2.0)) * _FILL_MARGIN

    aabb_min = np.min([mesh.bounds[0] for mesh, _c in posed], axis=0)

    parts_world = []
    for part in model.parts:
        mat = world.get(part.name)
        parts_world.append([_flat16(mat if mat is not None else np.eye(4))] * len(views))

    cam_poses = []
    for view in views:
        direction = _VIEW_DIRECTIONS[view]
        cam_poses.append(_flat16(_camera_pose(center, cam_distance, direction)))

    # Studio key/fill/rim rig matching the material-preview look:
    # Key 1050W / Fill 700W / Rim 900W on a ~1.5 m scene, rescaled by distance^2.
    light_rig = (
        (np.array([-3.4, -4.2, 5.0], dtype=float), 19.8, 0.50),
        (np.array([4.0, -2.2, 2.8], dtype=float), 21.7, 0.55),
        (np.array([1.2, 2.8, 4.3], dtype=float), 31.4, 0.45),
    )
    lights = []
    for d, gain, size_frac in light_rig:
        d = d / (np.linalg.norm(d) or 1.0)
        dist = 3.0 * sphere_r
        lights.append(
            {
                "loc": (center + d * dist).tolist(),
                "energy": gain * dist * dist,
                "size": size_frac * dist,
            }
        )

    ground_z = float(aabb_min[2]) - 1e-3
    job = {
        "render": {"width": width, "height": height, "samples": samples},
        "view_transform": "AgX",
        "view_look": "AgX - Medium High Contrast",
        "world": {
            "bg_color": [0.30, 0.32, 0.37],
            "bg_strength": 1.0,
            "fill_strength": 0.75,
        },
        "ground": {
            "enabled": True,
            "z": ground_z,
            "size": 50.0 * sphere_r,
            "color": [0.38, 0.41, 0.46],
            "roughness": 0.82,
        },
        "backdrop": {
            "enabled": True,
            "z": ground_z,
            "height": 1.6 * cam_distance,
            "width": 2.2 * cam_distance,
            "offset": 3.0 * sphere_r,
            "color": [0.56, 0.59, 0.64],
            "roughness": 0.72,
        },
        "camera": {"center": center.tolist(), "angle_y_deg": _YFOV_DEG, "poses": cam_poses},
        "visuals": visuals,
        "parts_world": parts_world,
        "teaser": {
            "slug": slug,
            "seed": int(seed),
            "material_seed": int(material_seed),
            "pose_phase": float(pose_phase),
            "materials": material_report,
        },
    }
    with open(job_dir / "job.json", "w") as fh:
        json.dump(job, fh)
    return job


def _render_job(blender: str, job_dir: Path, gpu_id) -> tuple[bool, str]:
    env = dict(os.environ)
    if gpu_id is not None:
        env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    proc = subprocess.run(
        [
            blender,
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
        return False, f"blender exit {proc.returncode}\n{proc.stdout[-1500:]}\n{proc.stderr[-800:]}"
    frames = sorted((job_dir / "frames").glob("frame_*.png"))
    if not frames:
        return False, f"no frames produced\n{proc.stdout[-800:]}"
    return True, f"gpu {gpu_id}: {len(frames)} frame(s)"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slugs", required=True, help="Comma-separated template slugs.")
    parser.add_argument("--seeds", default="18,1018", help="Geometry seeds, e.g. '18,1018'.")
    parser.add_argument(
        "--seed-views",
        default="front_iso,rear_iso",
        help="One camera view per seed (cycled), e.g. 'front_iso,rear_iso'.",
    )
    parser.add_argument(
        "--material-seeds",
        default="",
        help="Pool-sampling seeds; defaults to the geometry seed of each job.",
    )
    parser.add_argument("--out", type=Path, default=Path("/tmp/extracted/teaser_renders"))
    parser.add_argument("--views", default="front_iso", help="Comma-separated camera views.")
    parser.add_argument(
        "--pose-phase",
        type=float,
        default=0.45,
        help="Joint travel fraction for the exhibit pose (0=closed, 1=open).",
    )
    parser.add_argument("--width", type=int, default=2048)
    parser.add_argument("--height", type=int, default=2048)
    parser.add_argument("--samples", type=int, default=128)
    parser.add_argument("--workers", type=int, default=8, help="Parallel Blender processes.")
    parser.add_argument("--gpu-ids", default="", help="Comma-separated GPU ids.")
    parser.add_argument("--blender", default=_DEFAULT_BLENDER)
    parser.add_argument("--keep-jobs", action="store_true", help="Keep job dirs after render.")
    parser.add_argument(
        "--overrides",
        type=Path,
        default=None,
        help="JSON file: {slug: {material_class_id: material_id}} to pin chosen materials.",
    )
    args = parser.parse_args()

    if not Path(args.blender).exists():
        raise SystemExit(f"Blender binary not found: {args.blender}")

    slugs = [s.strip() for s in args.slugs.split(",") if s.strip()]
    seeds = _parse_seeds(args.seeds)
    seed_views = [v.strip() for v in args.seed_views.split(",") if v.strip()]
    material_seeds = (
        {int(s) for s in args.material_seeds.split(",") if s.strip()}
        if args.material_seeds.strip()
        else None
    )
    views = [v.strip() for v in args.views.split(",") if v.strip()]
    unknown_views = sorted(set(views + seed_views) - set(_VIEW_DIRECTIONS))
    if unknown_views:
        raise SystemExit(f"Unknown view(s): {', '.join(unknown_views)}")

    library = load_unified_material_library(_LIBRARY_POINTER)
    overrides = {}
    if args.overrides is not None:
        with open(args.overrides) as fh:
            overrides = json.load(fh)
    args.out.mkdir(parents=True, exist_ok=True)
    jobs_root = args.out / "_jobs"
    jobs_root.mkdir(parents=True, exist_ok=True)

    jobs = []  # (job_dir, final_dir, name_stem, view)
    for slug in slugs:
        for seed_idx, seed in enumerate(seeds):
            seed_view = seed_views[seed_idx % len(seed_views)] if seed_views else views[0]
            material_seed = seed if material_seeds is None else sorted(material_seeds)[0]
            job_dir = jobs_root / f"{slug}_seed{seed}"
            if job_dir.exists():
                shutil.rmtree(job_dir)
            job_dir.mkdir(parents=True)
            try:
                _build_job(
                    slug=slug,
                    seed=seed,
                    material_seed=material_seed,
                    library=library,
                    job_dir=job_dir,
                    views=[seed_view],
                    pose_phase=args.pose_phase,
                    width=args.width,
                    height=args.height,
                    samples=args.samples,
                    overrides=overrides,
                )
            except Exception as exc:  # noqa: BLE001
                print(f"[SKIP] {slug} seed {seed}: {exc}", flush=True)
                shutil.rmtree(job_dir, ignore_errors=True)
                continue
            final_dir = args.out / slug
            final_dir.mkdir(parents=True, exist_ok=True)
            jobs.append((job_dir, final_dir, f"{slug}_seed{seed}", seed_view))

    if not jobs:
        raise SystemExit("no renderable jobs")

    if args.gpu_ids.strip():
        gpu_ids = [int(x) for x in args.gpu_ids.split(",") if x.strip()]
    else:
        gpu_ids = list(range(_detect_gpu_count()))
    n_workers = max(1, min(args.workers, len(gpu_ids) or 1))

    def run_one(index, item):
        job_dir, final_dir, stem, view = item
        gpu_id = gpu_ids[index % len(gpu_ids)] if gpu_ids else None
        ok, detail = _render_job(args.blender, job_dir, gpu_id)
        if not ok:
            return False, f"[FAIL] {stem}: {detail}"
        frames = sorted((job_dir / "frames").glob("frame_*.png"))
        for k, frame in enumerate(frames):
            shutil.copyfile(frame, final_dir / f"{stem}_{view}.png")
        # Keep the material sampling receipt next to the stills.
        with open(job_dir / "job.json") as fh:
            receipt = json.load(fh).get("teaser", {})
        with open(final_dir / f"{stem}_materials.json", "w") as fh:
            json.dump(receipt, fh, indent=1)
        return True, f"[OK] {stem} -> {final_dir} ({len(frames)} view(s))"

    failures = []
    with ThreadPoolExecutor(max_workers=n_workers) as pool:
        futures = {pool.submit(run_one, i, item): item for i, item in enumerate(jobs)}
        for future in as_completed(futures):
            ok, message = future.result()
            print(message, flush=True)
            if not ok:
                failures.append(message)

    if not args.keep_jobs:
        for job_dir, _final, _stem, _view in jobs:
            shutil.rmtree(job_dir, ignore_errors=True)

    print(f"\nDone: {len(jobs) - len(failures)}/{len(jobs)} jobs rendered -> {args.out}")
    if failures:
        print(f"{len(failures)} failure(s)")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
