#!/usr/bin/env python
# SPDX-License-Identifier: Apache-2.0

"""SHADOW-RUN scan: joint origin-POINT gate vs proposed axis-LINE metric.

For every (template, seed) this builds the model DIRECTLY (import the template
module, ``build_<stem>(config_from_seed(seed))`` — no sweep, no sweep state,
no template edits) and records, per joint:

- joint type, the legacy point distances (parent/child), the legacy effective
  tol (0.015 floor, 0.05×bbox-diag relative term) and the legacy verdict;
- the shadow axis-segment distances (parent/child; FIXED/FLOATING fall back to
  point distances) and shadow verdicts at candidate FLAT thresholds
  {10, 15, 20} mm (no relative term).

Report-only: the live gate (``find_joint_origin_distance_findings``) is not
touched and nothing here is wired into any gate.

Results stream to JSONL (one line per template) so a long run can be
interrupted and resumed with ``--resume``. Templates run in a small process
pool; each seed inside a worker is guarded by a SIGALRM soft timeout (a seed
stuck in a C-level call can escape it — resume and skip in that case).

Usage (thread-capped, repo root, inside the venv):

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
        .venv/bin/python scripts/origin_axis_shadow_scan.py --seeds 6 --max-workers 6 \
        --out .articraft/origin_axis_shadow_scan.jsonl
"""

from __future__ import annotations

import argparse
import importlib
import json
import signal
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from multiprocessing import get_context
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Candidate flat thresholds for the shadow axis metric (meters).
THRESHOLDS: tuple[float, ...] = (0.010, 0.015, 0.020)


class _SeedTimeout(Exception):
    pass


def _alarm_handler(signum: int, frame: Any) -> None:  # noqa: ARG001
    raise _SeedTimeout()


def _joint_row(m: Any) -> dict[str, Any]:
    old_fail = m.parent_point_distance > m.point_tol or m.child_point_distance > m.point_tol
    row: dict[str, Any] = {
        "joint": m.joint,
        "type": m.joint_type,
        "parent": m.parent,
        "child": m.child,
        "point_parent": round(m.parent_point_distance, 6),
        "point_child": round(m.child_point_distance, 6),
        "old_tol": round(m.point_tol, 6),
        "old_fail": old_fail,
        "axis_parent": round(m.parent_axis_distance, 6),
        "axis_child": round(m.child_axis_distance, 6),
        "axis_based": m.axis_based,
        "half_len": round(m.axis_half_length, 6),
    }
    for tol in THRESHOLDS:
        key = f"new_fail_{int(round(tol * 1000))}"
        row[key] = m.parent_axis_distance > tol or m.child_axis_distance > tol
    return row


def _scan_slug(slug: str, stem: str, seeds: list[int], seed_timeout_s: float) -> dict[str, Any]:
    """Build every seed of one template and measure all joints (worker-side)."""
    from sdk._core.v0.geometry_qc import measure_joint_axis_distances

    started = time.monotonic()
    seed_rows: list[dict[str, Any]] = []
    try:
        module = importlib.import_module(f"agent.templates.{slug}")
        config_from_seed = getattr(module, "config_from_seed")
        build = getattr(module, f"build_{stem}")
    except Exception as exc:  # noqa: BLE001 - a broken template must not abort the scan
        return {
            "slug": slug,
            "stem": stem,
            "status": "error",
            "reason": f"{type(exc).__name__}: {exc}",
            "elapsed_s": round(time.monotonic() - started, 2),
        }

    previous_handler = signal.signal(signal.SIGALRM, _alarm_handler)
    try:
        for seed in seeds:
            seed_started = time.monotonic()
            signal.setitimer(signal.ITIMER_REAL, max(1.0, float(seed_timeout_s)))
            try:
                # Templates that register meshes via mesh_from_geometry() write
                # OBJs into the ACTIVE asset session, while exact-collision
                # compilation resolves through the model's AssetContext. A bare
                # build has no session -> ephemeral dir mismatch -> "Mesh file
                # not found" (the 25 unmeasured slugs of the first full scan).
                # Activate a session rooted where the AssetContext will look.
                import tempfile

                from sdk._core.v0.assets import (
                    AssetContext,
                    AssetSession,
                    activate_asset_session,
                )

                with tempfile.TemporaryDirectory(prefix="axis_scan_assets_") as tmp:
                    ctx = AssetContext(Path(tmp))
                    with activate_asset_session(AssetSession(Path(tmp))):
                        try:
                            model = build(config_from_seed(seed), assets=ctx)
                        except TypeError:
                            model = build(config_from_seed(seed))
                        measurements = measure_joint_axis_distances(model)
                seed_rows.append(
                    {
                        "seed": seed,
                        "status": "ok",
                        "joints": [_joint_row(m) for m in measurements],
                        "elapsed_s": round(time.monotonic() - seed_started, 2),
                    }
                )
            except _SeedTimeout:
                seed_rows.append(
                    {
                        "seed": seed,
                        "status": "timeout",
                        "reason": f"seed exceeded {seed_timeout_s:.0f}s",
                        "elapsed_s": round(time.monotonic() - seed_started, 2),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                seed_rows.append(
                    {
                        "seed": seed,
                        "status": "error",
                        "reason": f"{type(exc).__name__}: {str(exc)[:300]}",
                        "elapsed_s": round(time.monotonic() - seed_started, 2),
                    }
                )
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0.0)
    finally:
        signal.signal(signal.SIGALRM, previous_handler)

    return {
        "slug": slug,
        "stem": stem,
        "status": "ok",
        "seeds": seed_rows,
        "elapsed_s": round(time.monotonic() - started, 2),
    }


def _load_done(out_path: Path) -> set[str]:
    done: set[str] = set()
    if not out_path.exists():
        return done
    for line in out_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            done.add(json.loads(line)["slug"])
        except (json.JSONDecodeError, KeyError):
            continue
    return done


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Shadow scan: origin-point gate vs axis-line metric (report-only)."
    )
    parser.add_argument("--seeds", type=int, default=6, help="Seeds 0..N-1 per template.")
    parser.add_argument("--max-workers", type=int, default=6, help="Process pool size.")
    parser.add_argument(
        "--seed-timeout", type=float, default=180.0, help="Per-seed soft timeout (s)."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / ".articraft" / "origin_axis_shadow_scan.jsonl",
        help="JSONL output path (streamed per template).",
    )
    parser.add_argument(
        "--slugs",
        nargs="*",
        default=None,
        help="Restrict to these slugs (default: the whole TEMPLATE_REGISTRY).",
    )
    parser.add_argument("--resume", action="store_true", help="Skip slugs already in the JSONL.")
    args = parser.parse_args(argv)

    from agent.template_registry import TEMPLATE_REGISTRY

    seeds = list(range(max(1, int(args.seeds))))
    if args.slugs:
        unknown = sorted(set(args.slugs) - set(TEMPLATE_REGISTRY))
        if unknown:
            print(f"unknown slugs (skipped): {unknown}", file=sys.stderr)
        slugs = sorted(s for s in set(args.slugs) if s in TEMPLATE_REGISTRY)
    else:
        slugs = sorted(TEMPLATE_REGISTRY.keys())

    out_path: Path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = _load_done(out_path) if args.resume else set()
    if not args.resume and out_path.exists():
        out_path.unlink()

    pending = [s for s in slugs if s not in done]
    total = len(pending)
    print(
        f"axis shadow scan: {total} templates (skipping {len(done)} done), "
        f"seeds=0..{len(seeds) - 1}, workers={args.max_workers}, "
        f"seed_timeout={args.seed_timeout:.0f}s -> {out_path}",
        file=sys.stderr,
        flush=True,
    )
    if not pending:
        return 0

    scan_started = time.monotonic()
    finished = 0
    # A fresh spawn-context pool per batch bounds worker memory across many
    # template imports. (ProcessPoolExecutor's max_tasks_per_child can deadlock
    # once every worker retires simultaneously, so batching is done here.)
    ctx = get_context("spawn")
    batch_size = max(1, int(args.max_workers)) * 8
    with out_path.open("a", encoding="utf-8") as fh:
        for batch_start in range(0, len(pending), batch_size):
            batch = pending[batch_start : batch_start + batch_size]
            with ProcessPoolExecutor(max_workers=int(args.max_workers), mp_context=ctx) as pool:
                future_slug = {
                    pool.submit(
                        _scan_slug, slug, TEMPLATE_REGISTRY[slug], seeds, float(args.seed_timeout)
                    ): slug
                    for slug in batch
                }
                remaining = set(future_slug)
                while remaining:
                    ready, remaining = wait(remaining, return_when=FIRST_COMPLETED)
                    for future in ready:
                        slug = future_slug[future]
                        try:
                            summary = future.result()
                        except Exception as exc:  # noqa: BLE001 - keep scanning past crashes
                            summary = {
                                "slug": slug,
                                "stem": TEMPLATE_REGISTRY[slug],
                                "status": "error",
                                "reason": f"worker crashed: {type(exc).__name__}: {exc}",
                            }
                        fh.write(json.dumps(summary) + "\n")
                        fh.flush()
                        finished += 1
                        n_joints = sum(
                            len(s.get("joints", []))
                            for s in summary.get("seeds", [])
                            if isinstance(s, dict)
                        )
                        print(
                            f"[{finished}/{total}] {slug} {summary.get('status')} "
                            f"joints={n_joints} ({summary.get('elapsed_s', '?')}s)",
                            file=sys.stderr,
                            flush=True,
                        )

    print(
        f"done: {finished} templates in {time.monotonic() - scan_started:.0f}s -> {out_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
