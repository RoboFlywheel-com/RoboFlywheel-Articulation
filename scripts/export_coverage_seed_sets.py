# SPDX-License-Identifier: Apache-2.0

"""Drive `template gen-seeds` for a list of slugs with coverage-picked seeds.

For each slug: pick `--count` seeds that cover every reachable slot candidate
(see `pick_coverage_seeds.py`), then run gen-seeds. gen-seeds is all-or-nothing —
one QC-rejected seed leaves the whole category unwritten — so a rejected seed is
added to a blocklist and the pick is redone without it, up to `--attempts` times.

Usage:
    python scripts/export_coverage_seed_sets.py --out <dir> --slugs-file <file>
        [--count 15] [--attempts 4] [--max-workers 8]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.pick_coverage_seeds import pick, probe  # noqa: E402


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


def run_slug(
    slug: str,
    *,
    out_root: Path,
    count: int,
    pool: int,
    attempts: int,
    max_workers: int,
    rng_seed: int,
) -> dict:
    blocked: set[int] = set()
    rejected_line = 0
    path = out_root / "_rejected" / f"{slug}.jsonl"
    if path.exists():
        rejected_line = len(path.read_text(encoding="utf-8").splitlines())

    history: list[dict] = []
    for attempt in range(1, attempts + 1):
        choices_by_seed = probe(slug, pool, blocked)
        if not choices_by_seed:
            return {"slug": slug, "ok": False, "error": "no usable seeds", "history": history}
        # Vary the tie-break per slug (so categories do not share a seed list) and
        # per attempt (so a retry is not the same pick minus one seed, which would
        # keep re-compiling the same near-miss neighbourhood).
        slug_salt = int(hashlib.sha256(slug.encode("utf-8")).hexdigest()[:8], 16)
        seeds, universe, uncovered = pick(choices_by_seed, count, rng_seed + slug_salt + attempt)
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
            str(max_workers),
        ]
        proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        newly_rejected, rejected_line = _rejected_seeds(out_root, slug, rejected_line)
        history.append(
            {
                "attempt": attempt,
                "seeds": seeds,
                "returncode": proc.returncode,
                "rejected": newly_rejected,
            }
        )
        if proc.returncode == 0:
            return {
                "slug": slug,
                "ok": True,
                "seeds": seeds,
                "candidates_total": len(universe),
                "candidates_covered": len(universe) - len(uncovered),
                "uncovered": sorted(uncovered),
                "slots": {
                    slot: sorted({v for s, v in universe if s == slot})
                    for slot in sorted({s for s, _ in universe})
                },
                "attempts_used": attempt,
                "blocked_seeds": sorted(blocked),
                "history": history,
            }
        if not newly_rejected:
            # Failed for a reason other than seed QC (import error, disk, ...);
            # retrying the same pick would just repeat it.
            return {
                "slug": slug,
                "ok": False,
                "error": (proc.stderr or proc.stdout)[-2000:],
                "history": history,
            }
        blocked.update(newly_rejected)

    return {
        "slug": slug,
        "ok": False,
        "error": f"exhausted {attempts} attempts",
        "blocked_seeds": sorted(blocked),
        "history": history,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--slugs-file", type=Path, required=True)
    parser.add_argument("--count", type=int, default=15)
    parser.add_argument("--pool", type=int, default=3000)
    parser.add_argument("--attempts", type=int, default=4)
    parser.add_argument("--max-workers", type=int, default=8)
    parser.add_argument("--rng-seed", type=int, default=20260729)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    slugs = [
        line.strip()
        for line in args.slugs_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    results = []
    for index, slug in enumerate(slugs, start=1):
        print(f"[{index}/{len(slugs)}] {slug}", flush=True)
        result = run_slug(
            slug,
            out_root=args.out,
            count=args.count,
            pool=args.pool,
            attempts=args.attempts,
            max_workers=args.max_workers,
            rng_seed=args.rng_seed,
        )
        status = "OK" if result["ok"] else "FAIL"
        print(f"    {status} {slug}: {result.get('error', '')}", flush=True)
        results.append(result)
        if args.report:
            args.report.write_text(json.dumps(results, indent=2), encoding="utf-8")

    failed = [r["slug"] for r in results if not r["ok"]]
    print(f"\ndone: {len(results) - len(failed)}/{len(results)} categories exported")
    if failed:
        print("failed: " + ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
