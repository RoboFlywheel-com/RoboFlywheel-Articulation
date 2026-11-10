#!/usr/bin/env python
# SPDX-License-Identifier: Apache-2.0

"""Whole-library motion-QC census (report-only).

Runs the harness-owned sampled-pose overlap gate (``harness_motion_qc``) across
every registered template for a small seed set and reports which templates have
motion-driven 穿模 defects — parts that pass the static single-pose overlap check
but collide once their joints are driven to sampled poses.

This is *calibration/report only*:

- It never writes sweep streak state (uses ``run_seed_outcomes`` directly, which
  has no ``state_dir`` side effect) and never edits any template.
- Each seed compiles in a fresh timeout-guarded subprocess (same path the sweep
  uses), so a hanging seed is SIGKILL'd rather than stalling the census.
- Results stream to a JSONL file as each template finishes, so a long run can be
  interrupted and resumed (``--resume`` skips slugs already in the JSONL).

The existing 289 templates are NOT a retrofit target; this surfaces where the
motion gate would newly bite so real defects can be triaged deliberately.

Usage (thread-capped, from the repo root, inside the venv):

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
        python scripts/motion_census.py --seeds 6 --max-workers 6 --compile-timeout 120 \
        --out .articraft/motion_census.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent.template_registry import TEMPLATE_REGISTRY  # noqa: E402
from agent.template_sweep import SeedOutcome, run_seed_outcomes  # noqa: E402

_MOTION_QC_MARKER = "harness_motion_qc"


def _is_motion_qc_failure(outcome: SeedOutcome) -> bool:
    for field in (outcome.failure_type, outcome.failure_type_normalized, outcome.failure_details):
        if field and _MOTION_QC_MARKER in str(field):
            return True
    return False


def _classify(outcomes: list[SeedOutcome]) -> dict[str, Any]:
    motion_fail: list[dict[str, Any]] = []
    other_fail: list[dict[str, Any]] = []
    passed: list[int] = []
    for outcome in outcomes:
        if outcome.verdict == "pass":
            passed.append(outcome.seed)
            continue
        record = {
            "seed": outcome.seed,
            "failure_type": outcome.failure_type,
            "detail": (outcome.failure_details or "")[:400],
        }
        (motion_fail if _is_motion_qc_failure(outcome) else other_fail).append(record)
    return {
        "passed_seeds": passed,
        "motion_qc_failures": motion_fail,
        "other_failures": other_fail,
        "motion_qc_fail_count": len(motion_fail),
        "other_fail_count": len(other_fail),
        "pass_count": len(passed),
    }


def _census_one(
    slug: str,
    stem: str,
    seeds: list[int],
    *,
    max_workers: int,
    compile_timeout_s: float,
) -> dict[str, Any]:
    started = time.monotonic()
    try:
        outcomes = run_seed_outcomes(
            slug=slug,
            stem=stem,
            seeds=seeds,
            max_workers=max_workers,
            repo_root=REPO_ROOT,
            compile_timeout_s=compile_timeout_s,
            motion_qc=True,
        )
    except Exception as exc:  # noqa: BLE001 - a broken template must not abort the census
        return {
            "slug": slug,
            "stem": stem,
            "status": "error",
            "reason": f"{type(exc).__name__}: {exc}",
            "elapsed_s": round(time.monotonic() - started, 2),
        }
    summary = _classify(outcomes)
    summary.update(
        {
            "slug": slug,
            "stem": stem,
            "status": "ok",
            "seeds": list(seeds),
            "elapsed_s": round(time.monotonic() - started, 2),
        }
    )
    return summary


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
    parser = argparse.ArgumentParser(description="Report-only whole-library motion-QC census.")
    parser.add_argument("--seeds", type=int, default=6, help="Seeds 0..N-1 per template (default 6).")
    parser.add_argument("--max-workers", type=int, default=6, help="Per-template seed workers.")
    parser.add_argument("--compile-timeout", type=float, default=120.0, help="Per-seed timeout (s).")
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / ".articraft" / "motion_census.jsonl",
        help="JSONL output path (streamed per template).",
    )
    parser.add_argument(
        "--slugs",
        nargs="*",
        default=None,
        help="Restrict to these slugs (default: the whole registry).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip slugs already present in the JSONL output.",
    )
    args = parser.parse_args(argv)

    seeds = list(range(max(1, int(args.seeds))))
    slugs = sorted(args.slugs) if args.slugs else sorted(TEMPLATE_REGISTRY.keys())
    out_path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    done = _load_done(out_path) if args.resume else set()
    if not args.resume and out_path.exists():
        out_path.unlink()

    pending = [s for s in slugs if s not in done]
    total = len(pending)
    print(
        f"motion census: {total} templates (skipping {len(done)} done), "
        f"seeds=0..{len(seeds) - 1}, workers={args.max_workers}, timeout={args.compile_timeout:.0f}s",
        file=sys.stderr,
        flush=True,
    )

    results: list[dict[str, Any]] = []
    census_started = time.monotonic()
    with out_path.open("a", encoding="utf-8") as fh:
        for index, slug in enumerate(pending, start=1):
            stem = TEMPLATE_REGISTRY[slug]
            summary = _census_one(
                slug,
                stem,
                seeds,
                max_workers=int(args.max_workers),
                compile_timeout_s=float(args.compile_timeout),
            )
            fh.write(json.dumps(summary) + "\n")
            fh.flush()
            results.append(summary)
            tag = summary.get("status")
            mqc = summary.get("motion_qc_fail_count", "?")
            other = summary.get("other_fail_count", "?")
            print(
                f"[{index}/{total}] {slug} {tag} motion_qc_fail={mqc} other_fail={other} "
                f"({summary.get('elapsed_s', 0)}s)",
                file=sys.stderr,
                flush=True,
            )

    _print_ranked_report(out_path, elapsed=time.monotonic() - census_started)
    return 0


def _print_ranked_report(out_path: Path, *, elapsed: float) -> None:
    rows: list[dict[str, Any]] = []
    for line in out_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    motion_offenders = sorted(
        (r for r in rows if r.get("motion_qc_fail_count", 0) > 0),
        key=lambda r: (-r["motion_qc_fail_count"], r["slug"]),
    )
    errored = [r for r in rows if r.get("status") == "error"]
    other_only = [
        r
        for r in rows
        if r.get("status") == "ok"
        and r.get("motion_qc_fail_count", 0) == 0
        and r.get("other_fail_count", 0) > 0
    ]

    print("\n" + "=" * 72, file=sys.stderr)
    print(
        f"MOTION-QC CENSUS: {len(rows)} templates in {elapsed:.0f}s | "
        f"{len(motion_offenders)} with motion_qc defects | "
        f"{len(other_only)} with only non-motion failures | {len(errored)} errored",
        file=sys.stderr,
    )
    print("=" * 72, file=sys.stderr)
    if motion_offenders:
        print("\nTemplates with motion-QC 穿模 defects (ranked):", file=sys.stderr)
        for r in motion_offenders:
            seeds_hit = [f["seed"] for f in r["motion_qc_failures"]]
            print(
                f"  {r['motion_qc_fail_count']:>2}x  {r['slug']}  seeds={seeds_hit}",
                file=sys.stderr,
            )
        first = motion_offenders[0]
        example = first["motion_qc_failures"][0]
        print(
            f"\n  example — {first['slug']} seed {example['seed']}:\n    {example['detail']}",
            file=sys.stderr,
        )
    else:
        print("\nNo motion-QC defects found in the sampled seeds.", file=sys.stderr)
    print(f"\nFull JSONL: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
