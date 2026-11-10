# SPDX-License-Identifier: Apache-2.0

"""Render 2 still previews (rest pose + mid-range pose) per procedural template.

For each slug (seed 1) this bakes two posed scenes and path-traces one 1024x1024
PNG each with Blender Cycles (GPU / OptiX), reusing the studio scene worker
scripts/_blender_worker.py and the FK/palette helpers from the video renderers.

Poses (per the preview spec):
  * rest: every driven joint at 0 clamped into its limits; mimic followers derive
    automatically from the FK pass.
  * mid:  every non-mimic movable joint at the middle of its range,
    (lower+upper)/2; CONTINUOUS joints at +45 deg; FIXED stays put. Respect
    pose_gate: if a gated joint's gating joint mid value does not satisfy the
    gate, hold the gated joint at rest (0, clamped).

One Blender process per GPU, a work queue over all (slug x pose-pair) jobs.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import queue
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from scripts.render_template_videos import (
    _FILL_MARGIN,
    _YFOV_DEG,
    _camera_pose,
    _resolve_template,
)
from scripts.render_template_videos_blender import (
    _extract_visuals,
    _flat16,
)
from sdk import AssetContext
from sdk._core.v0.assets import AssetSession, activate_asset_session
from sdk._core.v0.geometry_qc import (
    _origin_to_mat4,
    compute_part_world_transforms,
)

_WORKER = Path(__file__).resolve().parent / "_blender_worker.py"
_CONT_MID = math.pi / 4.0  # +45 deg for continuous / unbounded joints

# base 3/4 view direction (world frame; light shines toward origin)
_BASE_DIR = np.array([1.25, -1.35, 0.85], dtype=float)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _drive_specs(model) -> list[tuple[str, float, float, bool]]:
    """[(name, lower, upper, is_continuous)] for each non-mimic movable joint."""
    out: list[tuple[str, float, float, bool]] = []
    for j in getattr(model, "joints", []) or []:
        if getattr(j, "mimic", None) is not None:
            continue
        atype = str(getattr(j, "articulation_type", "")).rsplit(".", 1)[-1].upper()
        if atype not in ("REVOLUTE", "PRISMATIC", "CONTINUOUS"):
            continue
        limit = getattr(j, "limit", None) or getattr(j, "motion_limits", None)
        lo = getattr(limit, "lower", None)
        hi = getattr(limit, "upper", None)
        cont = atype == "CONTINUOUS" or lo is None or hi is None or (hi - lo) <= 1e-9
        if cont:
            lo, hi = 0.0, _CONT_MID  # placeholder range; mid handled specially
        out.append((str(getattr(j, "name", "")), float(lo), float(hi), bool(cont)))
    return out


def _pose_rest(specs) -> dict[str, float]:
    return {n: _clamp(0.0, lo, hi) for n, lo, hi, _c in specs}


def _pose_mid(model, specs) -> dict[str, float]:
    mid = {}
    for n, lo, hi, cont in specs:
        mid[n] = _CONT_MID if cont else 0.5 * (lo + hi)
    # pose_gate: hold gated joint at rest if the gating joint's mid does not
    # satisfy the gate.
    lim = {n: (lo, hi) for n, lo, hi, _c in specs}
    for j in getattr(model, "joints", []) or []:
        gate = getattr(j, "pose_gate", None)
        name = getattr(j, "name", None)
        if gate is None or name not in mid:
            continue
        gating = getattr(gate, "joint", None)
        gv = mid.get(gating)
        if gv is None or not gate.satisfied_by(gv):
            lo, hi = lim[name]
            mid[name] = _clamp(0.0, lo, hi)
    return mid


def _build_job(slug: str, seed: int, out_dir: Path, job_dir: Path, *, samples: int, res: int):
    module, build_fn = _resolve_template(slug)
    config = module.config_from_seed(seed)
    assets_root = out_dir / "assets" / f"{slug}_seed_{seed}"
    assets = AssetContext(assets_root)
    # Activate an asset session on the SAME root as the model's AssetContext.
    # Templates that register meshes via mesh_from_geometry() write into the
    # active session, while build-time exact-collision probes (e.g.
    # Music_Headphone's _solve_tilt_clearance) resolve mesh files through the
    # model's AssetContext -- without this the two point at different trees and
    # the probe dies with "Mesh file not found".
    with activate_asset_session(AssetSession(assets_root)):
        model = build_fn(config, assets=assets)

    extracted = _extract_visuals(model, "segment")  # [(pn, part_idx, local_mesh, spec)]
    if not extracted:
        return None

    part_index = {part.name: i for i, part in enumerate(model.parts)}
    specs = _drive_specs(model)
    rest = _pose_rest(specs)
    mid = _pose_mid(model, specs)
    poses = [rest, mid]  # frame 0 = rest, frame 1 = mid

    # world transforms per pose
    worlds = [compute_part_world_transforms(model, p) for p in poses]

    # scene bounds over both poses (for camera framing + ground plane)
    mins, maxs = [], []
    for w in worlds:
        for _pn, _pi, mesh, _spec in extracted:
            tf = w.get(_pn)
            if tf is None:
                continue
            m = mesh.copy()
            m.apply_transform(np.asarray(tf, dtype=float))
            b = m.bounds
            mins.append(b[0])
            maxs.append(b[1])
    if not mins:
        return None
    aabb_min = np.min(mins, axis=0)
    aabb_max = np.max(maxs, axis=0)
    center = 0.5 * (aabb_min + aabb_max)
    radius = float(np.linalg.norm(aabb_max - aabb_min) * 0.5) or 1.0

    cam_distance = 0.5 * radius / math.sin(math.radians(_YFOV_DEG / 2.0)) * _FILL_MARGIN
    cam_pose = _flat16(_camera_pose(center, cam_distance, _BASE_DIR))

    # export one PLY per visual (local frame; visual.origin already baked in)
    meshes_dir = job_dir / "meshes"
    meshes_dir.mkdir(parents=True, exist_ok=True)
    visuals = []
    for i, (_pn, part_idx, mesh, spec) in enumerate(extracted):
        rel = f"meshes/vis_{i:04d}.ply"
        mesh.export(job_dir / rel)
        visuals.append({"mesh": rel, "spec": spec, "part": part_idx})

    n_frames = len(poses)
    parts_world = [[None] * n_frames for _ in model.parts]
    for f, w in enumerate(worlds):
        for part in model.parts:
            mat = w.get(part.name)
            parts_world[part_index[part.name]][f] = (
                _flat16(mat) if mat is not None else _flat16(np.eye(4))
            )

    sphere_r = 0.5 * radius
    light_dirs = [([0.3, -0.7, 1.6], 45.0), ([-0.6, -0.9, 0.5], 12.0)]
    lights = []
    for d, gain in light_dirs:
        d = np.asarray(d, dtype=float)
        d = d / (np.linalg.norm(d) or 1.0)
        dist = 3.0 * sphere_r
        loc = (center + d * dist).tolist()
        lights.append({"loc": loc, "energy": gain * dist * dist, "size": 1.5 * sphere_r})

    job = {
        "render": {"width": res, "height": res, "samples": samples, "frames": n_frames},
        "view_transform": "Standard",
        "world": {"bg_color": [0.9098, 0.9294, 0.9608], "bg_strength": 1.0, "fill_strength": 0.35},
        "ground": {"enabled": True, "z": float(aabb_min[2]) - 1e-3, "size": 50.0 * sphere_r},
        "camera": {"center": center.tolist(), "angle_y_deg": _YFOV_DEG, "poses": [cam_pose] * n_frames},
        "visuals": visuals,
        "parts_world": parts_world,
        "lights": lights,
    }
    with open(job_dir / "job.json", "w") as fh:
        json.dump(job, fh)
    return {"driven": len(specs)}


def _render_job(blender: str, job_dir: Path, gpu_id, label: str):
    env = dict(os.environ)
    if gpu_id is not None:
        env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    proc = subprocess.run(
        [blender, "-b", "--factory-startup", "-noaudio", "-P", str(_WORKER), "--", str(job_dir)],
        capture_output=True,
        text=True,
        env=env,
    )
    compute_line = ""
    for ln in proc.stdout.splitlines():
        if ln.startswith("[blender] compute="):
            compute_line = ln.strip()
    if proc.returncode != 0:
        return False, f"[FAIL] {label}: blender exit {proc.returncode}\n{proc.stdout[-800:]}\n{proc.stderr[-400:]}", compute_line
    return True, f"{label}: ok (gpu {gpu_id}) {compute_line}", compute_line


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--slugs-file", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--blender", default="/tmp/blender-4.2.21-linux-x64/blender")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--samples", type=int, default=64)
    p.add_argument("--res", type=int, default=1024)
    p.add_argument("--gpus", default="0,1,2,3,4,5,6,7")
    p.add_argument("--last", default="", help="Comma-separated slugs to build/render LAST.")
    p.add_argument("--probe", action="store_true", help="Render only the first slug (GPU probe).")
    args = p.parse_args()

    if not Path(args.blender).exists():
        raise SystemExit(f"Blender not found: {args.blender}")

    slugs = [ln.strip() for ln in Path(args.slugs_file).read_text().splitlines() if ln.strip()]
    last = [s.strip() for s in args.last.split(",") if s.strip()]
    slugs = [s for s in slugs if s not in last] + [s for s in slugs if s in last]
    if args.probe:
        slugs = slugs[:1]

    gpu_ids = [int(x) for x in args.gpus.split(",") if x.strip()] or [None]
    args.out.mkdir(parents=True, exist_ok=True)
    jobs_root = args.out / "_jobs"
    jobs_root.mkdir(parents=True, exist_ok=True)

    # Phase 1: build + bake every job in this (single-threaded) python process.
    built = []  # (slug, job_dir)
    build_fail = {}
    for slug in slugs:
        job_dir = jobs_root / slug
        if job_dir.exists():
            shutil.rmtree(job_dir)
        job_dir.mkdir(parents=True, exist_ok=True)
        try:
            info = _build_job(slug, args.seed, args.out, job_dir, samples=args.samples, res=args.res)
        except Exception as exc:  # noqa: BLE001
            build_fail[slug] = f"{type(exc).__name__}: {exc}"
            print(f"  [build-FAIL] {slug}: {build_fail[slug]}", flush=True)
            continue
        if info is None:
            build_fail[slug] = "no renderable meshes"
            print(f"  [skip] {slug}: no renderable meshes", flush=True)
            continue
        built.append((slug, job_dir))
        print(f"  [built] {slug}: {info['driven']} driven joints", flush=True)

    print(f"Built {len(built)}/{len(slugs)} jobs; rendering on GPUs {gpu_ids}", flush=True)

    # Phase 2: render each job pinned to a free GPU.
    gpu_q: queue.Queue = queue.Queue()
    for g in gpu_ids:
        gpu_q.put(g)

    render_ok = {}
    render_fail = {}
    compute_lines = []

    def _task(slug, job_dir):
        g = gpu_q.get()
        try:
            return slug, job_dir, _render_job(args.blender, job_dir, g, slug)
        finally:
            gpu_q.put(g)

    with ThreadPoolExecutor(max_workers=len(gpu_ids)) as ex:
        futs = [ex.submit(_task, s, jd) for s, jd in built]
        for fut in as_completed(futs):
            slug, job_dir, (ok, msg, compute_line) = fut.result()
            print("  " + msg.splitlines()[0], flush=True)
            if compute_line:
                compute_lines.append((slug, compute_line))
            if not ok:
                render_fail[slug] = msg
                continue
            # copy frames -> <slug>__rest.png / <slug>__mid.png
            rest_src = job_dir / "frames" / "frame_0000.png"
            mid_src = job_dir / "frames" / "frame_0001.png"
            if rest_src.exists() and mid_src.exists():
                shutil.copy(rest_src, args.out / f"{slug}__rest.png")
                shutil.copy(mid_src, args.out / f"{slug}__mid.png")
                render_ok[slug] = True
            else:
                render_fail[slug] = "frames missing"

    # index.html contact sheet
    _write_index(args.out, slugs, render_ok, build_fail, render_fail)

    # summary json
    summary = {
        "total": len(slugs),
        "rendered": sorted(render_ok),
        "build_fail": build_fail,
        "render_fail": {k: v.splitlines()[0] for k, v in render_fail.items()},
        "gpu_compute": compute_lines,
    }
    (args.out / "_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"rendered": len(render_ok), "build_fail": list(build_fail),
                      "render_fail": list(render_fail),
                      "gpu_sample": compute_lines[:3]}, indent=2))
    return 0


def _write_index(out: Path, slugs, render_ok, build_fail, render_fail):
    rows = []
    for slug in slugs:
        if slug in render_ok:
            cells = (
                f'<td><img src="{slug}__rest.png" loading="lazy"><div class="cap">rest</div></td>'
                f'<td><img src="{slug}__mid.png" loading="lazy"><div class="cap">mid</div></td>'
            )
            status = '<span class="ok">rendered</span>'
        else:
            reason = build_fail.get(slug) or render_fail.get(slug, "?")
            cells = f'<td colspan="2" class="fail">FAILED: {reason}</td>'
            status = '<span class="bad">failed</span>'
        rows.append(f'<tr><th>{slug}<br>{status}</th>{cells}</tr>')
    html = (
        "<!doctype html><meta charset=utf-8><title>Repaired template previews</title>"
        "<style>body{font-family:system-ui,sans-serif;background:#1b1e24;color:#e7e9ee;margin:16px}"
        "table{border-collapse:collapse}td,th{border:1px solid #333;padding:4px;vertical-align:top;text-align:center}"
        "th{width:180px;font-size:13px}img{width:320px;height:320px;object-fit:contain;background:#e8edf5}"
        ".cap{font-size:11px;color:#9aa}.ok{color:#4ade80}.bad{color:#f87171}"
        ".fail{color:#f87171;font-family:monospace;font-size:12px}h1{font-size:18px}</style>"
        f"<h1>Repaired template previews — {len(render_ok)}/{len(slugs)} rendered (seed 1, rest | mid)</h1>"
        "<table>" + "".join(rows) + "</table>"
    )
    (out / "index.html").write_text(html)


if __name__ == "__main__":
    sys.exit(main())
