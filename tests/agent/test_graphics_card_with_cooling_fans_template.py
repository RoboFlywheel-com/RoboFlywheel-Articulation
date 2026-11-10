# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import pytest

from agent.templates.graphics_card_with_cooling_fans import (
    GraphicsCardConfig,
    build_graphics_card,
    build_seeded_graphics_card,
    config_from_seed,
    resolve_config,
    run_graphics_card_tests,
)
from sdk import ArticulationType
from sdk._core.v0.testing import TestContext as SDKTestContext


def _assert_template_qc_passes(config: GraphicsCardConfig) -> None:
    model = build_graphics_card(config)
    report = run_graphics_card_tests(model, config)
    assert report.passed, report.failures


def test_template_line_floor() -> None:
    template_path = Path("agent/templates/graphics_card_with_cooling_fans.py")
    assert len(template_path.read_text().splitlines()) >= 1000


def test_seed_reproducibility() -> None:
    assert config_from_seed(7) == config_from_seed(7)
    assert config_from_seed(7) != config_from_seed(8)
    assert build_seeded_graphics_card(7).name == "seeded_graphics_card_with_cooling_fans_7"


def test_long_triple_fan_layout_has_three_axial_rotors() -> None:
    config = GraphicsCardConfig(cooler_family="long_triple_fan")
    resolved = resolve_config(config)
    model = build_graphics_card(config)
    fan_joints = [joint for joint in model.articulations if joint.name.startswith("fan_spin_")]

    assert resolved.fan_count == 3
    assert len(fan_joints) == 3
    assert all(joint.articulation_type == ArticulationType.CONTINUOUS for joint in fan_joints)
    assert all(tuple(joint.axis) == (0.0, 0.0, 1.0) for joint in fan_joints)


def test_short_card_cannot_keep_three_large_fans() -> None:
    resolved = resolve_config(
        GraphicsCardConfig(
            cooler_family="single_short_card",
            fan_count=3,
            fan_layout="triple_equal",
        )
    )
    assert resolved.fan_count == 1
    assert resolved.fan_layout == "single_center"


def test_interfaces_are_derived_from_card_edges() -> None:
    config = GraphicsCardConfig(cooler_family="compact_dual_fan")
    resolved = resolve_config(config)
    model = build_graphics_card(config)
    card = model.get_part("card_body")
    names = {visual.name for visual in card.visuals}

    assert "io_bracket" in names
    assert "pcie_contact_bar" in names
    assert (
        sum(1 for name in names if name.startswith("pcie_finger_")) == resolved.pcie_contact_count
    )


def test_asymmetric_tail_fan_gets_smaller_radius() -> None:
    resolved = resolve_config(GraphicsCardConfig(cooler_family="dual_large_tail_small"))
    radii = [fan.radius for fan in resolved.fan_specs]

    assert resolved.fan_count == 3
    assert radii[2] < radii[0]
    assert radii[2] < radii[1]


def test_support_brace_uses_side_hinge_axis() -> None:
    config = GraphicsCardConfig(cooler_family="compact_dual_fan", support_brace_enabled=True)
    model = build_graphics_card(config)
    hinge = model.get_articulation("support_brace_hinge")

    assert hinge.articulation_type == ArticulationType.REVOLUTE
    assert tuple(hinge.axis) == (0.0, 1.0, 0.0)


@pytest.mark.parametrize("seed", range(12))
def test_seeded_configs_pass_template_qc(seed: int) -> None:
    _assert_template_qc_passes(config_from_seed(seed))


def test_strict_current_pose_overlap_seed_zero() -> None:
    model = build_graphics_card(config_from_seed(0))
    ctx = SDKTestContext(model)
    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
    assert ctx.report().passed
