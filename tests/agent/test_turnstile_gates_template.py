# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.turnstile_gates import (
    build_turnstile_gates,
    config_from_seed,
    run_turnstile_gates_tests,
    slot_choices_for_seed,
)


def test_seed_zero_anchor_combination() -> None:
    assert slot_choices_for_seed(0) == [
        ("fixed_support_lane", "refined_frame"),
        ("barrier_mechanism", "three_arm_rotor"),
        ("service_and_locking", "none"),
        ("arm_count", "3"),
        ("rotor_joint_type", "continuous"),
    ]


def test_seeded_turnstile_gates_templates_pass_author_checks() -> None:
    for seed in range(10):
        config = config_from_seed(seed)
        model = build_turnstile_gates(config)
        report = run_turnstile_gates_tests(model, config)
        assert report.passed, (seed, report.failures)
