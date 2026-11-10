# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.miter_saw_arm_assembly import (
    build_miter_saw_arm_assembly,
    config_from_seed,
    run_miter_saw_arm_assembly_tests,
    slot_choices_for_seed,
)


def test_seed_zero_anchor_combination() -> None:
    assert slot_choices_for_seed(0) == [
        ("base_style", "compact_bench"),
        ("arm_style", "single_beam"),
        ("head_style", "yellow_guard"),
        ("aux_style", "none"),
        ("blade_style", "toothed_disc"),
        ("material_style", "shop_yellow"),
    ]


def test_seeded_miter_saw_arm_assembly_templates_pass_author_checks() -> None:
    for seed in range(10):
        config = config_from_seed(seed)
        model = build_miter_saw_arm_assembly(config)
        report = run_miter_saw_arm_assembly_tests(model, config)
        assert report.passed, (seed, report.failures)
