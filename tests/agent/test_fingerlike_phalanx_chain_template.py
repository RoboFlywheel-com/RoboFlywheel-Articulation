# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.fingerlike_phalanx_chain import (
    build_fingerlike_phalanx_chain,
    config_from_seed,
    run_fingerlike_phalanx_chain_tests,
    slot_choices_for_seed,
)


def test_seed_zero_has_modular_choices() -> None:
    choices = slot_choices_for_seed(0)
    assert any(slot == "base" for slot, _module in choices)
    assert any(slot == "chain_multiplicity" for slot, _module in choices)
    assert any(slot == "phalanx_multiplicity" for slot, _module in choices)
    assert any(slot == "phalanx_profile" for slot, _module in choices)


def test_seeded_fingerlike_phalanx_chain_templates_pass_author_checks() -> None:
    for seed in range(10):
        config = config_from_seed(seed)
        model = build_fingerlike_phalanx_chain(config)
        report = run_fingerlike_phalanx_chain_tests(model, config)
        assert report.passed, (seed, report.failures)
