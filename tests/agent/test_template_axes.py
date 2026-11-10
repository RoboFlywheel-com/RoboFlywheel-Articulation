# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.template_axes import (
    build_axis_realization,
    flatten_config,
    select_corner_seeds_from_fns,
)
from agent.template_sweep import SeedOutcome

# --- flatten_config --------------------------------------------------------


def test_flatten_config_dots_nested_and_len_encodes_sequences():
    flat = flatten_config(
        {
            "style": "round",
            "scale": 1.2,
            "nested": {"h": 0.5, "w": 0.3},
            "blades": [1, 2, 3],
            "seed": 7,
        }
    )
    assert flat["style"] == "round"
    assert flat["scale"] == 1.2
    assert flat["nested.h"] == 0.5
    assert flat["nested.w"] == 0.3
    assert flat["blades#len"] == 3
    assert flat["seed"] == 7


# --- corner-seed selection -------------------------------------------------


def _slotless_config(seed: int) -> dict:
    # A numeric axis whose extremes live at seeds the base sweep never touches.
    return {"scale": round(0.5 + (seed % 100) / 100.0, 4), "family": "a" if seed % 2 else "b"}


def test_corner_selection_targets_numeric_extremes_outside_base():
    plan = select_corner_seeds_from_fns(
        _slotless_config,
        None,
        base_seeds=range(50),
        probe_seeds=200,
        max_corner_seeds=8,
    )
    assert plan.status == "ok"
    assert plan.seeds  # picked at least one corner seed
    assert all(seed >= 50 for seed in plan.seeds)  # never re-selects a base seed
    # scale peaks at seed%100==99 (value 1.49); base 0-49 never reaches it.
    tokens = {tok for detail in plan.selection for tok in detail["tokens"]}
    assert "scale@max" in tokens


def test_corner_selection_uses_slot_combos_when_available():
    def config_fn(seed: int) -> dict:
        return {"scale": round(0.5 + (seed % 7) / 10.0, 4)}

    def slot_fn(seed: int):
        # A combo only reachable at seed%3==2, which base range 0-3 misses.
        return [("closure", ["drawer", "flip", "book"][seed % 3])]

    plan = select_corner_seeds_from_fns(
        config_fn,
        slot_fn,
        base_seeds=[0, 1, 3],  # closure hits drawer/flip only
        probe_seeds=60,
        max_corner_seeds=8,
    )
    assert plan.status == "ok"
    combo_tokens = {
        tok
        for detail in plan.selection
        for tok in detail["tokens"]
        if tok.startswith("combo:")
    }
    assert any("closure=book" in tok for tok in combo_tokens)
    assert plan.combo_summary["unrealized_by_base"] >= 1


def test_corner_selection_empty_when_base_covers_everything():
    def config_fn(seed: int) -> dict:
        return {"family": "a" if seed % 2 else "b"}  # only 2 reachable values

    plan = select_corner_seeds_from_fns(
        config_fn,
        None,
        base_seeds=range(50),
        probe_seeds=100,
        max_corner_seeds=8,
    )
    assert plan.status == "ok"
    assert plan.seeds == []
    assert "already cover" in plan.reason


def test_corner_selection_reports_error_when_config_fn_always_raises():
    def boom(seed: int) -> dict:
        raise ValueError("nope")

    plan = select_corner_seeds_from_fns(
        boom, None, base_seeds=range(4), probe_seeds=8, max_corner_seeds=4
    )
    assert plan.status == "error"
    assert plan.seeds == []


# --- axis realization report -----------------------------------------------


def _outcome(seed: int, config: dict, *, verdict: str = "pass") -> SeedOutcome:
    return SeedOutcome(
        seed=seed,
        verdict=verdict,
        config=config,
        failure_type=None,
        failure_type_normalized=None,
        failure_details=None,
        elapsed_s=0.01,
    )


def test_axis_realization_summarizes_numeric_and_skips_seed_name():
    outcomes = [
        _outcome(i, {"scale": 0.5 + i / 100.0, "seed": i, "name": f"x{i}"})
        for i in range(10)
    ]
    report = build_axis_realization("does_not_exist_slug", outcomes)
    assert report["seed_count"] == 10
    assert "scale" in report["numeric_fields"]
    assert "seed" not in report["numeric_fields"]
    entry = report["numeric_fields"]["scale"]
    assert entry["min"] == 0.5
    assert entry["max"] == 0.59
    assert "histogram" in entry
    assert sum(entry["histogram"]["bins"]) == 10
    # slot section is best-effort; unknown slug yields no slot counts, no crash.
    assert report["slot_value_counts"] == {}
