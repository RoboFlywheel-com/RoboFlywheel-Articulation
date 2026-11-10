# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.windshield_wiper_assembly import (
    build_windshield_wiper_assembly,
    config_from_seed,
    run_windshield_wiper_assembly_tests,
    slot_choices_for_seed,
)


def test_seed_zero_has_modular_choices() -> None:
    choices = slot_choices_for_seed(0)
    assert any(slot == "base" for slot, _module in choices)
    assert any(slot == "wiper_multiplicity" for slot, _module in choices)
    assert any(slot == "blade_profile" for slot, _module in choices)


def test_seeded_windshield_wiper_templates_pass_author_checks() -> None:
    for seed in range(10):
        config = config_from_seed(seed)
        model = build_windshield_wiper_assembly(config)
        report = run_windshield_wiper_assembly_tests(model, config)
        assert report.passed, (seed, report.failures)
