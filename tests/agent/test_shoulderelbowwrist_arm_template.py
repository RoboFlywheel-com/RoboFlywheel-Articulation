# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.shoulderelbowwrist_arm import (
    build_shoulderelbowwrist_arm,
    config_from_seed,
    run_shoulderelbowwrist_arm_tests,
    slot_choices_for_seed,
)


def test_seed_zero_has_modular_choices() -> None:
    choices = slot_choices_for_seed(0)
    assert any(slot == "kinematic_layout" for slot, _module in choices)
    assert any(slot == "joint_multiplicity" for slot, _module in choices)
    assert any(slot == "wrist_module" for slot, _module in choices)


def test_seeded_shoulderelbowwrist_arm_templates_pass_author_checks() -> None:
    for seed in range(10):
        config = config_from_seed(seed)
        model = build_shoulderelbowwrist_arm(config)
        report = run_shoulderelbowwrist_arm_tests(model, config)
        assert report.passed, (seed, report.failures)
