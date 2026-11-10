# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.casino_machine import (
    build_casino_machine,
    config_from_seed,
    run_casino_machine_tests,
    slot_choices_for_seed,
)


def test_seed_zero_anchor_combination() -> None:
    assert slot_choices_for_seed(0) == [
        ("cabinet_body", "upright_reel"),
        ("game_display_or_reels", "five_reel_window"),
        ("controls_and_openings", "spin_button_service"),
        ("reel_count", "5"),
        ("button_count", "1"),
    ]


def test_seeded_casino_machine_templates_pass_author_checks() -> None:
    for seed in range(10):
        config = config_from_seed(seed)
        model = build_casino_machine(config)
        report = run_casino_machine_tests(model, config)
        assert report.passed, (seed, report.failures)
