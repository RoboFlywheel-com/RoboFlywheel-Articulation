# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.vane_array_with_independent_pivots import (
    build_vane_array_with_independent_pivots,
    config_from_seed,
    run_vane_array_with_independent_pivots_tests,
    slot_choices_for_seed,
)


def test_seed_zero_has_modular_choices() -> None:
    choices = slot_choices_for_seed(0)
    assert any(slot == "frame" for slot, _module in choices)
    assert any(slot == "vane_multiplicity" for slot, _module in choices)
    assert any(slot == "axis_family" for slot, _module in choices)


def test_seeded_vane_array_templates_pass_author_checks() -> None:
    for seed in range(10):
        config = config_from_seed(seed)
        model = build_vane_array_with_independent_pivots(config)
        report = run_vane_array_with_independent_pivots_tests(model, config)
        assert report.passed, (seed, report.failures)
