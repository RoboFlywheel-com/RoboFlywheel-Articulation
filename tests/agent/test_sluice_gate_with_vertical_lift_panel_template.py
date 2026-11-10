# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.sluice_gate_with_vertical_lift_panel import (
    build_sluice_gate_with_vertical_lift_panel,
    config_from_seed,
    run_sluice_gate_with_vertical_lift_panel_tests,
    slot_choices_for_seed,
)
from sdk import ArticulationType


def test_seed_zero_has_modular_choices() -> None:
    choices = slot_choices_for_seed(0)
    assert any(slot == "foundation" for slot, _module in choices)
    assert any(slot == "frame" for slot, _module in choices)
    assert any(slot == "lift_panel" for slot, _module in choices)
    assert any(slot == "lift_drive" for slot, _module in choices)


def test_seeded_sluice_gate_templates_pass_author_checks() -> None:
    for seed in range(10):
        config = config_from_seed(seed)
        model = build_sluice_gate_with_vertical_lift_panel(config)
        report = run_sluice_gate_with_vertical_lift_panel_tests(model, config)
        assert report.passed, (seed, report.failures)


def test_vertical_lift_panel_joint_contract() -> None:
    model = build_sluice_gate_with_vertical_lift_panel(config_from_seed(3))
    joint = model.get_articulation("panel_vertical_lift")
    assert joint.articulation_type == ArticulationType.PRISMATIC
    assert joint.axis == (0.0, 0.0, 1.0)
    assert joint.motion_limits.lower == 0.0
    assert joint.motion_limits.upper > 0.45
