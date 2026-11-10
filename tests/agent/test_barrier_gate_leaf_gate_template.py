# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.barrier_gate_leaf_gate import (
    BarrierGateConfig,
    build_barrier_gate,
    build_seeded_barrier_gate,
    config_from_seed,
    resolve_config,
    run_barrier_gate_tests,
)
from sdk import ArticulationType
from sdk import TestContext as ArticraftTestContext


@pytest.mark.parametrize(
    "layout",
    [
        "sliding_panel",
        "swing_leaf",
        "bifold_leaf",
        "rising_wedge",
        "telescoping_bollard",
        "vertical_lift_panel",
    ],
)
def test_leaf_gate_layouts_match_template_validator(layout: str) -> None:
    config = BarrierGateConfig(barrier_layout=layout)  # type: ignore[arg-type]
    model = build_barrier_gate(config)
    report = run_barrier_gate_tests(model, config)

    assert report.passed, report.failures


def test_rejects_boom_layouts_and_mismatched_supports() -> None:
    with pytest.raises(ValueError, match="Unsupported barrier_layout"):
        resolve_config(BarrierGateConfig(barrier_layout="single_boom"))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="support_style must match"):
        resolve_config(BarrierGateConfig(barrier_layout="swing_leaf", support_style="rail_frame"))


def test_seed_layouts_cover_all_leaf_gate_variants() -> None:
    configs = [config_from_seed(seed) for seed in range(6)]

    assert {config.barrier_layout for config in configs} == {
        "sliding_panel",
        "swing_leaf",
        "bifold_leaf",
        "rising_wedge",
        "telescoping_bollard",
        "vertical_lift_panel",
    }


def test_layout_specific_joint_contracts() -> None:
    sliding = build_barrier_gate(BarrierGateConfig(barrier_layout="sliding_panel", panel_count=2))
    assert sliding.get_articulation("sliding_panel_left_joint").axis == (-1.0, 0.0, 0.0)
    assert sliding.get_articulation("sliding_panel_right_joint").axis == (1.0, 0.0, 0.0)

    bifold = build_barrier_gate(BarrierGateConfig(barrier_layout="bifold_leaf"))
    assert bifold.get_articulation("swing_leaf_hinge").axis == (0.0, 0.0, 1.0)
    assert bifold.get_articulation("bifold_inner_hinge").axis == (0.0, 0.0, 1.0)

    wedge = build_barrier_gate(BarrierGateConfig(barrier_layout="rising_wedge"))
    assert wedge.get_articulation("wedge_lift_hinge").articulation_type == ArticulationType.REVOLUTE

    bollard = build_barrier_gate(BarrierGateConfig(barrier_layout="telescoping_bollard"))
    assert (
        bollard.get_articulation("bollard_vertical_slide").articulation_type
        == ArticulationType.PRISMATIC
    )
    assert "bollard_hinged_cap" not in {part.name for part in bollard.parts}

    lift = build_barrier_gate(BarrierGateConfig(barrier_layout="vertical_lift_panel"))
    assert lift.get_articulation("panel_vertical_slide").axis == (0.0, 0.0, 1.0)
    assert lift.get_articulation("counterweight_vertical_slide").axis == (0.0, 0.0, -1.0)


def test_seed_0_to_5_pass_strict_contact_qc() -> None:
    for seed in range(6):
        config = config_from_seed(seed)
        model = build_seeded_barrier_gate(seed)
        report = run_barrier_gate_tests(model, config)
        assert report.passed, report.failures

        ctx = ArticraftTestContext(model)
        ctx.check_model_valid()
        ctx.fail_if_isolated_parts()
        ctx.fail_if_parts_overlap_in_current_pose(
            overlap_tol=0.003,
            overlap_volume_tol=1e-7,
        )
        qc_report = ctx.report()
        assert qc_report.passed, qc_report.failures
