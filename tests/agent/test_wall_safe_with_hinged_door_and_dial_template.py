# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.wall_safe_with_hinged_door_and_dial import (
    build_wall_safe_with_hinged_door_and_dial,
    config_from_seed,
    run_wall_safe_with_hinged_door_and_dial_tests,
    slot_choices_for_seed,
)


def test_seed_zero_anchor_combination() -> None:
    assert slot_choices_for_seed(0) == [
        ("body_style", "recessed_rect"),
        ("door_style", "right_hinged_thick"),
        ("lock_style", "three_spoke_center"),
        ("aux_style", "none"),
        ("material_style", "gunmetal"),
        ("hinge_barrel_multiplicity", "3_barrels"),
        ("handle_spoke_multiplicity", "3_spokes"),
        ("vault_rib_multiplicity", "0_ribs"),
        ("lock_bolt_multiplicity", "2_bolts"),
    ]


def test_seeded_wall_safe_with_hinged_door_and_dial_templates_pass_author_checks() -> None:
    for seed in range(10):
        config = config_from_seed(seed)
        model = build_wall_safe_with_hinged_door_and_dial(config)
        report = run_wall_safe_with_hinged_door_and_dial_tests(model, config)
        assert report.passed, (seed, report.failures)
