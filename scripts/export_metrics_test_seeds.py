# SPDX-License-Identifier: Apache-2.0

"""Export 1-2 QC-passing, mutually different seeds for every registered template.

This is the fleet-wide variant of `export_coverage_seed_sets.py`: instead of a
15-seed coverage set for a handful of slugs, it walks the whole
`TEMPLATE_REGISTRY` and asks for a *small* set (default 2) chosen to show both
ends of what the template can do.

Seed picking has two jobs, and they pull in opposite directions:

- **Tail.** Templates that expose a structural multiplicity slot (a fence's
  `panel_count`, a rack's `bar_count`) can build anything from 2 to ~100
  articulated parts. Sampling those uniformly buries the high-joint end, so the
  first seed is drawn from the 70-90th percentile *of the template's own count
  distribution*. Using the template's own distribution rather than an absolute
  joint target is deliberate: it widens the fleet-wide joint histogram without
  flattening it into a spike at every template's maximum, and a template whose
  counts top out at 3 simply contributes a small tail seed.
- **Diversity.** The second seed is chosen to differ from the first in as many
  *categorical* slots as possible while staying at or below the median count, so
  the pair is a genuine variant pair rather than the same build twice.

Templates with no `slot_choices_for_seed` (35 frozen legacy modules plus ~80
that never implemented it) cannot be steered either way and fall back to plain
random seeds.

`gen-seeds` is all-or-nothing -- one QC-rejected seed leaves the whole category
unwritten -- so a rejected seed goes on a blocklist and the pick is redone
without it. When no pair survives `--attempts` tries, the slug falls back to a
single seed (the "1" in "1-2 seeds per template") before being called failed.

Slugs are fanned out across `--jobs` threads, each of which only spawns and
waits on child processes -- the probe and the compile both run out-of-process.
Each `gen-seeds` call compiles its own seeds with `--seed-workers` workers, so
peak compile concurrency is `jobs * seed_workers`.

Usage:
    python scripts/export_metrics_test_seeds.py --out <dir> [--jobs 36]
        [--count 2] [--pool 400] [--attempts 3] [--resume]
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from agent.template_registry import TEMPLATE_REGISTRY  # noqa: E402

# Each per-seed compile is its own subprocess and NumPy/OpenBLAS otherwise grabs
# a thread per core inside every one of them. The compile budget is raised well
# above the 300 s default because the whole point of the tail seed is geometry
# that takes longer than a median build.
CHILD_ENV = {
    **os.environ,
    "OPENBLAS_NUM_THREADS": "2",
    "OMP_NUM_THREADS": "2",
    "URDF_COMPILE_TIMEOUT_SECONDS": "900",
}

_INT = re.compile(r"\d+")

# Spawning a child can fail with EAGAIN for reasons that have nothing to do with
# the template: this host is shared, and its process/thread headroom fluctuates
# with other tenants' load (a run holding only ~500 threads of a ~12.5k system
# total still saw bursts of these). Such a failure must not consume a pick
# attempt or blocklist a seed -- it says nothing about the seed. Back off and
# retry the same command instead.
_SPAWN_EAGAIN = (
    "Resource temporarily unavailable",
    "can't start new thread",
    "BlockingIOError",
    "pthread_create",
)
_SPAWN_RETRIES = 6
_SPAWN_BACKOFF_S = 20.0


def _looks_like_spawn_exhaustion(text: str) -> bool:
    return any(marker in text for marker in _SPAWN_EAGAIN)


def _run_child(cmd: list[str], *, timeout: float):
    """subprocess.run, retrying transient host process-table exhaustion.

    Returns the completed process, or None when the command timed out. Raises
    only if every retry hit spawn exhaustion, so callers can tell "the host was
    full" apart from "this seed failed QC".
    """
    last: Exception | None = None
    for attempt in range(_SPAWN_RETRIES):
        try:
            proc = subprocess.run(
                cmd, cwd=REPO, capture_output=True, text=True, env=CHILD_ENV, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            return None
        except OSError as exc:  # EAGAIN from fork/posix_spawn
            last = exc
            if not _looks_like_spawn_exhaustion(f"{type(exc).__name__}: {exc}"):
                raise
            time.sleep(_SPAWN_BACKOFF_S * (attempt + 1))
            continue
        if proc.returncode != 0 and _looks_like_spawn_exhaustion(proc.stderr or ""):
            last = RuntimeError((proc.stderr or "")[-400:])
            time.sleep(_SPAWN_BACKOFF_S * (attempt + 1))
            continue
        return proc
    raise RuntimeError(f"host process table exhausted after {_SPAWN_RETRIES} retries: {last}")


def _probe(slug: str, pool: int, blocked: set[int]) -> dict[int, tuple[tuple[str, str], ...]]:
    """Slot choices per seed, tolerating non-string slot values.

    `pick_coverage_seeds.probe` goes through the coverage gate's strict
    normalizer, which requires both halves of every pair to be `str`. 54 of the
    531 templates report counts as plain ints (`("bar_count", 8)`) and are
    dropped whole by that rule -- and they are exactly the count-steerable ones
    this exporter wants most. Coercing here keeps the shared gate's semantics
    untouched while still letting the pick see their multiplicity slots.
    """
    from agent.template_sweep_coverage import _slot_choices_for_seed

    choices_by_seed: dict[int, tuple[tuple[str, str], ...]] = {}
    for seed in range(pool):
        if seed in blocked:
            continue
        try:
            raw = _slot_choices_for_seed(slug, seed)
            items = list(raw.items()) if hasattr(raw, "items") else list(raw)
            pairs = tuple((str(slot), str(value)) for slot, value in items)
        except Exception:  # noqa: BLE001 - a seed the sampler rejects is not a candidate
            continue
        if pairs:
            choices_by_seed[seed] = pairs
    return choices_by_seed


def _multiplicity_score(choices, mult_slots: set[str]) -> int:
    """Total structural multiplicity a seed asks for; the joint-count proxy.

    Multiplicity values arrive as bare counts ("n12", "b4", "r2c3"), so the
    score is just the numbers in them. It is a proxy, not a joint count -- some
    counts drive visual-only repeats -- but it is the only signal available
    without compiling, and it tracked joint count exactly on the template it was
    calibrated against (a fence's `panel_count` is joints + 1).
    """
    total = 0
    for slot, value in choices:
        if slot in mult_slots:
            found = _INT.findall(value)
            if found:
                total += max(int(n) for n in found)
    return total


def _measure_joints(slug: str, seeds: list[int], budget_s: float) -> dict[int, int]:
    """Actual joint count per seed, by building the model with no asset context.

    Building without an `AssetContext` skips tessellation and export, so this
    costs 0.01-5 s per seed instead of a full compile. It replaces the
    multiplicity-slot proxy because the proxy is only sometimes a joint count:
    it tracked `panel_count` exactly on a cascade fence, but on an antenna dish
    the same kind of slot drives visual repeats (score 0 vs 14, both 2 joints),
    and the two templates with the widest measured joint spread -- a ferris
    wheel at 7 vs 18 and a keyboard at 77 vs 79 -- expose no count slot at all,
    so the proxy could not see them.

    Stops early once `budget_s` is spent; callers fall back to the proxy when
    this returns nothing.
    """
    import importlib

    try:
        module = importlib.import_module(f"agent.templates.{slug}")
        build = getattr(module, f"build_{TEMPLATE_REGISTRY[slug]}")
        config_from_seed = module.config_from_seed
    except Exception:  # noqa: BLE001 - unbuildable here is not fatal to the pick
        return {}

    counts: dict[int, int] = {}
    deadline = time.time() + budget_s
    for seed in seeds:
        if time.time() > deadline:
            break
        try:
            counts[seed] = len(build(config_from_seed(seed)).joints)
        except Exception:  # noqa: BLE001 - a seed the sampler rejects is not a candidate
            continue
    return counts


def _run_probe(
    slug: str, pool: int, blocked: set[int], probe_seeds: int, budget_s: float, rng_seed: int
) -> dict:
    """Body of the probe child process: slot choices plus measured joint counts."""
    choices = _probe(slug, pool, blocked)
    universe = sorted(choices) or [s for s in range(pool) if s not in blocked]
    sample = list(universe)
    random.Random(rng_seed).shuffle(sample)
    measured = _measure_joints(slug, sample[:probe_seeds], budget_s)
    return {
        "choices": {str(seed): list(pairs) for seed, pairs in choices.items()},
        "measured": {str(seed): count for seed, count in measured.items()},
    }


def _probe_subprocess(
    slug: str,
    *,
    pool: int,
    blocked: set[int],
    probe_seeds: int,
    budget_s: float,
    rng_seed: int,
) -> dict:
    """Run `_run_probe` in a child so no CAD library is ever loaded in-process."""
    cmd = [
        sys.executable,
        __file__,
        "--probe-slug",
        slug,
        "--pool",
        str(pool),
        "--probe-seeds",
        str(probe_seeds),
        "--probe-budget",
        str(budget_s),
        "--rng-seed",
        str(rng_seed),
        "--out",
        os.devnull,
    ]
    if blocked:
        cmd += ["--probe-blocked", ",".join(str(s) for s in sorted(blocked))]
    try:
        proc = _run_child(cmd, timeout=max(120.0, budget_s * 2))
        return json.loads(proc.stdout) if proc is not None else {}
    except Exception:  # noqa: BLE001 - an unprobeable template falls back to random
        return {}


def pick_seeds(
    slug: str,
    *,
    pool: int,
    blocked: set[int],
    want: int,
    rng_seed: int,
    probe_seeds: int = 12,
    probe_budget_s: float = 90.0,
) -> tuple[list[int], dict]:
    """Pick `want` seeds: one from the joint-count tail, the rest categorically distinct.

    Probing and joint measurement both import the template, and importing a
    template loads CadQuery/OCCT. That has to happen in a child process, never
    here: this function's caller goes on to spawn `uv run articraft` for the
    compile, and forking a subprocess out of an interpreter that already has
    OCCT loaded aborts it ("terminate called after throwing an instance of
    std::runtime_error"), which then takes the whole worker pool down with it.
    Keeping every heavyweight import behind `_probe_subprocess` leaves this
    process a pure orchestrator.
    """
    from scripts.pick_coverage_seeds import is_multiplicity_slot

    rng = random.Random(rng_seed)
    payload = _probe_subprocess(
        slug,
        pool=pool,
        blocked=blocked,
        probe_seeds=probe_seeds,
        budget_s=probe_budget_s,
        rng_seed=rng_seed,
    )
    choices_by_seed = {
        int(seed): tuple((slot, value) for slot, value in pairs)
        for seed, pairs in payload.get("choices", {}).items()
    }
    measured = {int(seed): int(count) for seed, count in payload.get("measured", {}).items()}

    if not choices_by_seed and not measured:
        candidates = [s for s in range(pool) if s not in blocked]
        rng.shuffle(candidates)
        return candidates[:want], {"mode": "unsteerable_random"}

    per_slot: dict[str, set[str]] = {}
    for choices in choices_by_seed.values():
        for slot, value in choices:
            per_slot.setdefault(slot, set()).add(value)
    mult_slots = {s for s, v in per_slot.items() if is_multiplicity_slot(s, v)}

    if measured:
        mode = "measured_joints"
        scores = dict(measured)
        scored = sorted(scores, key=lambda s: (scores[s], s))
    else:
        mode = "multiplicity_proxy"
        scores = {s: _multiplicity_score(choices_by_seed[s], mult_slots) for s in choices_by_seed}
        scored = sorted(scores, key=lambda s: (scores[s], s))

    # Tail seed: the 70-90th percentile band of this template's own counts.
    lo = int(len(scored) * 0.70)
    hi = max(lo + 1, int(len(scored) * 0.90))
    band = scored[lo:hi] or scored[-1:]
    tail = rng.choice(band)
    chosen = [tail]

    # Remaining seeds: maximise categorical difference from what is already
    # chosen, tie-broken toward the lower half of the count distribution so the
    # pair spans the range instead of clustering in the tail.
    median_score = scores[scored[len(scored) // 2]]
    # `.get` because a template can be measurable but not steerable: it has real
    # joint counts and no slot_choices_for_seed at all, in which case there are
    # no categorical pairs to diff and the count tie-break decides alone.
    categorical_seen = {p for p in choices_by_seed.get(tail, ()) if p[0] not in mult_slots}
    while len(chosen) < want:
        best, best_key = None, None
        for seed in scored:
            if seed in chosen:
                continue
            new = {
                p
                for p in choices_by_seed.get(seed, ())
                if p[0] not in mult_slots and p not in categorical_seen
            }
            key = (len(new), scores[seed] <= median_score, -scores[seed])
            if best_key is None or key > best_key:
                best, best_key = seed, key
        if best is None:
            break
        chosen.append(best)
        categorical_seen.update(p for p in choices_by_seed.get(best, ()) if p[0] not in mult_slots)

    return sorted(chosen), {
        "mode": mode,
        "multiplicity_slots": sorted(mult_slots),
        "scores": {str(s): scores[s] for s in chosen},
        "score_band": [scores[band[0]], scores[band[-1]]],
        "score_max": scores[scored[-1]],
        "probed": len(scored),
    }


def _rejected_seeds(out_root: Path, slug: str, since_line: int) -> tuple[list[int], int]:
    """Seeds gen-seeds logged as rejected after `since_line` lines of the log."""
    path = out_root / "_rejected" / f"{slug}.jsonl"
    if not path.exists():
        return [], since_line
    lines = path.read_text(encoding="utf-8").splitlines()
    seeds: list[int] = []
    for line in lines[since_line:]:
        try:
            seeds.append(int(json.loads(line)["seed"]))
        except Exception:  # noqa: BLE001 - a malformed log line is not fatal here
            continue
    return seeds, len(lines)


def _gen_seeds(
    slug: str,
    seeds: list[int],
    out_root: Path,
    seed_workers: int,
    timeout: int,
    motion_qc: bool = False,
):
    cmd = [
        "uv",
        "run",
        "articraft",
        "template",
        "gen-seeds",
        slug,
        "--seeds",
        ",".join(str(s) for s in seeds),
        "--out",
        str(out_root),
        "--max-workers",
        str(seed_workers),
    ]
    if not motion_qc:
        cmd.append("--no-motion-qc")
    return _run_child(cmd, timeout=timeout)


def run_slug(
    slug: str,
    *,
    out_root: Path,
    count: int,
    pool: int,
    attempts: int,
    seed_workers: int,
    rng_seed: int,
    timeout: int,
    probe_seeds: int = 12,
    probe_budget_s: float = 90.0,
    motion_qc: bool = False,
) -> dict:
    started = time.time()
    blocked: set[int] = set()
    rejected_line = 0
    path = out_root / "_rejected" / f"{slug}.jsonl"
    if path.exists():
        rejected_line = len(path.read_text(encoding="utf-8").splitlines())

    history: list[dict] = []
    # Vary the tie-break per slug so categories do not all share one seed list,
    # and per attempt so a retry is not the same pick minus one seed.
    salt = int(hashlib.sha256(slug.encode("utf-8")).hexdigest()[:8], 16)

    # Phase 1 asks for the full `count`; phase 2 falls back to a single seed so a
    # template with one flaky variant still lands in the export.
    plan = [count] * attempts + [1] * attempts if count > 1 else [1] * attempts
    for attempt, want in enumerate(plan, start=1):
        seeds, pick_info = pick_seeds(
            slug,
            pool=pool,
            blocked=blocked,
            want=want,
            rng_seed=rng_seed + salt + attempt,
            probe_seeds=probe_seeds,
            probe_budget_s=probe_budget_s,
        )
        if not seeds:
            return {
                "slug": slug,
                "ok": False,
                "error": "no usable seeds left in pool",
                "blocked_seeds": sorted(blocked),
                "history": history,
                "seconds": round(time.time() - started, 1),
            }
        try:
            proc = _gen_seeds(
                slug, seeds, out_root, min(seed_workers, len(seeds)), timeout, motion_qc
            )
        except RuntimeError as exc:
            # Host exhaustion, not a template or seed verdict. Report it under
            # its own key so a --resume pass can tell it apart from QC rejection.
            return {
                "slug": slug,
                "ok": False,
                "error": f"host_exhaustion: {exc}",
                "retryable": True,
                "history": history,
                "seconds": round(time.time() - started, 1),
            }
        newly_rejected, rejected_line = _rejected_seeds(out_root, slug, rejected_line)
        history.append(
            {
                "attempt": attempt,
                "seeds": seeds,
                "pick": pick_info,
                "returncode": None if proc is None else proc.returncode,
                "rejected": newly_rejected,
            }
        )
        if proc is not None and proc.returncode == 0:
            return {
                "slug": slug,
                "ok": True,
                "seeds": seeds,
                "seed_count": len(seeds),
                "pick": pick_info,
                "attempts_used": attempt,
                "blocked_seeds": sorted(blocked),
                "history": history,
                "seconds": round(time.time() - started, 1),
            }
        if proc is None:
            # A wedged compile burns the whole slug budget if retried blindly;
            # block the picks so the next attempt walks down the count band.
            blocked.update(seeds)
            continue
        if not newly_rejected:
            # Failed for a reason other than seed QC (import error, disk, ...);
            # retrying the same pick would just repeat it.
            return {
                "slug": slug,
                "ok": False,
                "error": (proc.stderr or proc.stdout)[-2000:],
                "history": history,
                "seconds": round(time.time() - started, 1),
            }
        blocked.update(newly_rejected)

    return {
        "slug": slug,
        "ok": False,
        "error": f"exhausted {len(plan)} attempts",
        "blocked_seeds": sorted(blocked),
        "history": history,
        "seconds": round(time.time() - started, 1),
    }


def _already_done(out_root: Path, slug: str) -> bool:
    category = out_root / slug
    return category.is_dir() and any(category.glob("seed_*/model.urdf"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--slugs-file",
        type=Path,
        default=None,
        help="Optional slug list; defaults to every slug in TEMPLATE_REGISTRY.",
    )
    parser.add_argument("--count", type=int, default=2, help="Seeds per template (upper bound).")
    parser.add_argument("--pool", type=int, default=400, help="Seed pool probed for the pick.")
    parser.add_argument(
        "--attempts",
        type=int,
        default=3,
        help="Re-picks per phase; phase 1 asks for --count seeds, phase 2 for 1.",
    )
    parser.add_argument("--jobs", type=int, default=36, help="Templates compiled in parallel.")
    parser.add_argument(
        "--seed-workers", type=int, default=2, help="Compile threads inside one gen-seeds call."
    )
    parser.add_argument(
        "--timeout", type=int, default=1800, help="Per-gen-seeds-call wall clock cap, seconds."
    )
    parser.add_argument("--rng-seed", type=int, default=20260805)
    parser.add_argument("--probe-seeds", type=int, default=12)
    parser.add_argument("--probe-budget", type=float, default=90.0)
    parser.add_argument(
        "--probe-slug",
        default=None,
        help="Internal: run the probe for one slug and print JSON. Not for direct use.",
    )
    parser.add_argument("--probe-blocked", default="")
    parser.add_argument(
        "--motion-qc",
        action="store_true",
        help=(
            "Keep the sampled-pose collision gate. Off by default: this exporter "
            "asks only that a seed be articulated and clean in its rest pose."
        ),
    )
    parser.add_argument(
        "--resume", action="store_true", help="Skip slugs that already have an exported seed."
    )
    parser.add_argument("--report", type=Path, default=None, help="JSONL result log (appended).")
    args = parser.parse_args()

    if args.probe_slug:
        blocked = {int(tok) for tok in args.probe_blocked.split(",") if tok.strip()}
        print(
            json.dumps(
                _run_probe(
                    args.probe_slug,
                    args.pool,
                    blocked,
                    args.probe_seeds,
                    args.probe_budget,
                    args.rng_seed,
                )
            )
        )
        return 0

    if args.slugs_file:
        slugs = [
            line.strip()
            for line in args.slugs_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        unknown = [s for s in slugs if s not in TEMPLATE_REGISTRY]
        if unknown:
            print(f"unknown slugs: {', '.join(unknown[:10])}", file=sys.stderr)
            return 2
    else:
        slugs = sorted(TEMPLATE_REGISTRY)

    args.out.mkdir(parents=True, exist_ok=True)
    skipped = 0
    if args.resume:
        pending = [s for s in slugs if not _already_done(args.out, s)]
        skipped = len(slugs) - len(pending)
        slugs = pending

    report = args.report
    if report:
        report.parent.mkdir(parents=True, exist_ok=True)

    total = len(slugs)
    print(
        f"metrics_test export: {total} template(s) "
        f"({skipped} already done, skipped) -> {args.out}\n"
        f"  {args.jobs} templates in parallel x {args.seed_workers} compile workers, "
        f"asking for {args.count} seed(s) each",
        flush=True,
    )
    started = time.time()
    results: list[dict] = []
    done = 0
    # Threads, not processes: every worker now only spawns and waits on child
    # processes, so there is no CPU work to parallelise here -- and a thread pool
    # cannot be poisoned the way a forked worker can, where one aborted child
    # raised BrokenProcessPool and instantly marked the other 520 templates
    # failed without running them.
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {
            executor.submit(
                run_slug,
                slug,
                out_root=args.out,
                count=args.count,
                pool=args.pool,
                attempts=args.attempts,
                seed_workers=args.seed_workers,
                rng_seed=args.rng_seed,
                timeout=args.timeout,
                probe_seeds=args.probe_seeds,
                probe_budget_s=args.probe_budget,
                motion_qc=args.motion_qc,
            ): slug
            for slug in slugs
        }
        for future in concurrent.futures.as_completed(futures):
            slug = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001 - one slug must not kill the fleet
                result = {"slug": slug, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
            results.append(result)
            done += 1
            if result["ok"]:
                scores = (result.get("pick") or {}).get("scores", {})
                status = f"OK   {result['seed_count']} seed(s) {result['seeds']} mult={scores}"
            else:
                status = f"FAIL {str(result.get('error', '')).splitlines()[-1][:120]}"
            elapsed = time.time() - started
            print(
                f"[{done}/{total}] {slug}: {status} "
                f"({result.get('seconds', 0)}s, elapsed {elapsed / 60:.1f}m)",
                flush=True,
            )
            if report:
                with report.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(result) + "\n")

    ok = [r for r in results if r["ok"]]
    pairs = [r for r in ok if r.get("seed_count", 0) >= args.count]
    failed = [r["slug"] for r in results if not r["ok"]]
    print(
        f"\ndone in {(time.time() - started) / 60:.1f}m: "
        f"{len(ok)}/{total} templates exported "
        f"({len(pairs)} with {args.count} seeds, {len(ok) - len(pairs)} with fewer)",
        flush=True,
    )
    if failed:
        print(f"failed ({len(failed)}): " + ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
