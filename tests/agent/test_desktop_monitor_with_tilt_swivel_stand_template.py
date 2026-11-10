# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.desktop_monitor_with_tilt_swivel_stand import (
    DesktopMonitorWithTiltSwivelStandConfig,
    build_desktop_monitor,
    config_from_seed,
    resolve_config,
    run_desktop_monitor_tests,
)
from sdk import ArticulationType
from sdk import TestContext as ArticraftTestContext


def _assert_strict_qc_passes(model) -> None:
    ctx = ArticraftTestContext(model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
    report = ctx.report()
    assert report.passed, report.failures


def test_resolve_rejects_invalid_screen_width() -> None:
    with pytest.raises(ValueError, match="screen_width"):
        resolve_config(DesktopMonitorWithTiltSwivelStandConfig(screen_width=0.20))


def test_telescoping_stand_derives_height_joint() -> None:
    config = DesktopMonitorWithTiltSwivelStandConfig(
        stand_layout="telescoping_column",
        height_travel=0.0,
    )
    resolved = resolve_config(config)
    model = build_desktop_monitor(config)

    assert resolved.height_travel == pytest.approx(0.08)
    assert model.get_articulation("height_adjust_joint").axis == (0.0, 0.0, 1.0)


def test_swivel_continuous_joint_has_unbounded_motion_limits() -> None:
    model = build_desktop_monitor(DesktopMonitorWithTiltSwivelStandConfig())
    swivel = model.get_articulation("base_to_stand_swivel")

    assert swivel.articulation_type == ArticulationType.CONTINUOUS
    assert swivel.motion_limits is not None
    assert swivel.motion_limits.effort == pytest.approx(16.0)
    assert swivel.motion_limits.velocity == pytest.approx(3.0)
    assert swivel.motion_limits.lower is None
    assert swivel.motion_limits.upper is None
    assert swivel.meta["range"] == "continuous"


def test_diversity_branches_change_screen_base_and_controls() -> None:
    config = DesktopMonitorWithTiltSwivelStandConfig(
        screen_profile="curved_wide",
        base_style="tripod",
        stand_layout="split_yoke",
        controls_style="joystick",
    )
    model = build_desktop_monitor(config)

    assert "curved_screen_panel" in {visual.name for visual in model.get_part("display").visuals}
    assert any(visual.name.startswith("tripod_leg_") for visual in model.get_part("base").visuals)
    assert not any(joint.name.startswith("menu_button_joint_") for joint in model.articulations)


def test_portrait_pivot_request_is_normalized_to_single_tilt_axis() -> None:
    config = DesktopMonitorWithTiltSwivelStandConfig(has_portrait_pivot=True)
    model = build_desktop_monitor(config)

    assert model.get_articulation("tilt_joint").axis == (1.0, 0.0, 0.0)
    assert "portrait_pivot_joint" not in {joint.name for joint in model.articulations}


def test_seed_config_is_reproducible() -> None:
    assert config_from_seed(14) == config_from_seed(14)
    assert config_from_seed(14) != config_from_seed(15)


def test_run_desktop_monitor_tests_passes() -> None:
    config = DesktopMonitorWithTiltSwivelStandConfig(cable_cover_style="hinged_rear_door")
    report = run_desktop_monitor_tests(build_desktop_monitor(config), config)

    assert report.passed, report.failures


def test_seed_zero_to_thirty_one_pass_strict_qc() -> None:
    for seed in range(32):
        _assert_strict_qc_passes(build_desktop_monitor(config_from_seed(seed)))
