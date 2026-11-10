# SPDX-License-Identifier: Apache-2.0

"""Pick a small seed set that is random yet covers every reachable slot candidate.

`articraft template gen-seeds` takes an explicit seed list, so the "15 random
seeds that cover all candidates" request reduces to a set-cover problem over the
modular slot space: probe `slot_choices_for_seed(seed)` (pure, no compile) across
a dense seed pool, collect the reachable (slot, value) universe, then greedily
pick seeds until every pair is hit, filling the remainder of the budget with
random seeds so the export is not just the cover skeleton.

Usage:
    python scripts/pick_coverage_seeds.py <slug> [--count 15] [--pool 3000]
        [--exclude 1,2,3] [--rng-seed 20260729] [--json]
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from agent.template_sweep_coverage import (  # noqa: E402
    _normalize_slot_choices,
    _slot_choices_for_seed,
)


def probe(slug: str, pool: int, exclude: set[int]) -> dict[int, tuple[tuple[str, str], ...]]:
    """Map every usable seed in the pool to its normalized slot choices."""
    choices_by_seed: dict[int, tuple[tuple[str, str], ...]] = {}
    for seed in range(pool):
        if seed in exclude:
            continue
        try:
            choices_by_seed[seed] = _normalize_slot_choices(_slot_choices_for_seed(slug, seed))
        except Exception:  # noqa: BLE001 - a seed the sampler rejects is simply not a candidate
            continue
    return choices_by_seed


# Structural-multiplicity values are reported as bare counts ("n12", "b4", "s28",
# "r2c3", "g3") rather than module names. A slot like Door_Double_Door's
# `infill_count` has 45 of them — more than any 15-seed budget can realize — and
# VISUAL_DIVERSITY_MODEL treats structural N as covered, never counted. So the
# cover chases every categorical (module-valued) candidate FIRST and only then
# spends leftover budget widening the count slots.
_MULTIPLICITY_VALUE = re.compile(r"^[a-z]{0,2}\d+(c\d+)?$")


def is_multiplicity_slot(slot: str, values: set[str]) -> bool:
    return slot.endswith("_count") or all(_MULTIPLICITY_VALUE.match(v) for v in values)


def _greedy(
    order: list[int],
    choices_by_seed: dict[int, tuple[tuple[str, str], ...]],
    remaining: set[tuple[str, str]],
    chosen: list[int],
    count: int,
) -> None:
    """Extend `chosen` in place with max-gain seeds until `remaining` is empty."""
    picked = set(chosen)
    while remaining and len(chosen) < count:
        best_seed = None
        best_gain = 0
        for seed in order:
            if seed in picked:
                continue
            gain = len(remaining.intersection(choices_by_seed[seed]))
            if gain > best_gain:
                best_gain = gain
                best_seed = seed
        if best_seed is None:
            break
        chosen.append(best_seed)
        picked.add(best_seed)
        remaining -= set(choices_by_seed[best_seed])


def pick(
    choices_by_seed: dict[int, tuple[tuple[str, str], ...]],
    count: int,
    rng_seed: int,
) -> tuple[list[int], set[tuple[str, str]], set[tuple[str, str]]]:
    """Two-phase greedy cover, random among ties, padded to `count` seeds."""
    rng = random.Random(rng_seed)
    universe: set[tuple[str, str]] = set()
    for choices in choices_by_seed.values():
        universe.update(choices)

    per_key: dict[str, set[str]] = {}
    for slot, value in universe:
        per_key.setdefault(slot, set()).add(value)
    multiplicity = {slot for slot, values in per_key.items() if is_multiplicity_slot(slot, values)}

    # Shuffling once makes the greedy tie-break random but reproducible, so two
    # templates with identical slot spaces do not get the identical seed list.
    order = list(choices_by_seed)
    rng.shuffle(order)

    chosen: list[int] = []
    categorical = {pair for pair in universe if pair[0] not in multiplicity}
    _greedy(order, choices_by_seed, set(categorical), chosen, count)
    remaining = set(universe)
    for seed in chosen:
        remaining -= set(choices_by_seed[seed])
    _greedy(order, choices_by_seed, remaining, chosen, count)

    # Budget left over after the cover: spend it on plain random seeds so the
    # export is a random sample, not only the minimal cover skeleton.
    leftovers = [seed for seed in order if seed not in chosen]
    while len(chosen) < count and leftovers:
        chosen.append(leftovers.pop())

    covered: set[tuple[str, str]] = set()
    for seed in chosen:
        covered.update(choices_by_seed[seed])
    return sorted(chosen), universe, universe - covered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug")
    parser.add_argument("--count", type=int, default=15)
    parser.add_argument("--pool", type=int, default=3000)
    parser.add_argument("--rng-seed", type=int, default=20260729)
    parser.add_argument("--exclude", default="", help="Comma-separated seeds to skip.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    exclude = {int(tok) for tok in args.exclude.split(",") if tok.strip()}
    choices_by_seed = probe(args.slug, args.pool, exclude)
    if not choices_by_seed:
        print(f"{args.slug}: no usable seeds in pool", file=sys.stderr)
        return 1

    chosen, universe, uncovered = pick(choices_by_seed, args.count, args.rng_seed)
    per_key: dict[str, set[str]] = {}
    for slot, value in universe:
        per_key.setdefault(slot, set()).add(value)

    multiplicity = {slot for slot, values in per_key.items() if is_multiplicity_slot(slot, values)}
    categorical = {pair for pair in universe if pair[0] not in multiplicity}
    payload = {
        "slug": args.slug,
        "seeds": chosen,
        "seed_arg": ",".join(str(s) for s in chosen),
        "candidates_total": len(universe),
        "candidates_covered": len(universe) - len(uncovered),
        "categorical_total": len(categorical),
        "categorical_uncovered": sorted(p for p in uncovered if p in categorical),
        "multiplicity_slots": sorted(multiplicity),
        "uncovered": sorted(uncovered),
        "slots": {slot: sorted(values) for slot, values in sorted(per_key.items())},
        "pool_usable": len(choices_by_seed),
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
