# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.candy_vending_machine import (
    build_candy_vending_machine,
    config_from_seed,
    run_candy_vending_machine_tests,
    slot_choices_for_seed,
)


def test_seed_zero_has_modular_choices() -> None:
    choices = slot_choices_for_seed(0)
    assert ("chassis", "stacked_canister_cabinet") in choices
    assert any(slot == "selector_multiplicity" for slot, _module in choices)


def test_seeded_candy_vending_machine_templates_pass_author_checks() -> None:
    for seed in range(10):
        config = config_from_seed(seed)
        model = build_candy_vending_machine(config)
        report = run_candy_vending_machine_tests(model, config)
        assert report.passed, (seed, report.failures)
