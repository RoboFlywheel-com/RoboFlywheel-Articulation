# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.parabolic_dish_on_azimuth_elevation_mount import (
    build_parabolic_dish,
    config_from_seed,
    run_parabolic_dish_tests,
    slot_choices_for_seed,
)


def test_seed_zero_anchor_combination() -> None:
    assert slot_choices_for_seed(0) == [
        ("root_support", "pedestal"),
        ("azimuth_stage", "dual_yoke"),
        ("dish_reflector_assembly", "lathe_feed"),
        ("auxiliary_mechanism", "none"),
        ("feed_style", "single_boom"),
        ("back_frame_style", "simple_spine"),
        ("azimuth_joint_type", "continuous"),
    ]


def test_seeded_parabolic_dish_templates_pass_author_checks() -> None:
    for seed in range(10):
        config = config_from_seed(seed)
        model = build_parabolic_dish(config)
        report = run_parabolic_dish_tests(model, config)
        assert report.passed, (seed, report.failures)
