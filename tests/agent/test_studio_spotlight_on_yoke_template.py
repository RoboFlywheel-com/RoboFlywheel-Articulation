# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.studio_spotlight_on_yoke import (
    build_studio_spotlight_on_yoke,
    config_from_seed,
    run_studio_spotlight_on_yoke_tests,
    slot_choices_for_seed,
)


def test_seed_zero_anchor_combination() -> None:
    assert slot_choices_for_seed(0) == [
        ("stand_style", "round_floor"),
        ("yoke_style", "flat_side_plates"),
        ("can_style", "fresnel_short_can"),
        ("accessory_style", "barn_doors"),
        ("material_style", "matte_black_stage"),
    ]


def test_seeded_studio_spotlight_on_yoke_templates_pass_author_checks() -> None:
    for seed in range(10):
        config = config_from_seed(seed)
        model = build_studio_spotlight_on_yoke(config)
        report = run_studio_spotlight_on_yoke_tests(model, config)
        assert report.passed, (seed, report.failures)
