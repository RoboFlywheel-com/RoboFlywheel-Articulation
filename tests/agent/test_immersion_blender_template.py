# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.immersion_blender import (
    BlenderConfig,
    build_blender,
    build_seeded_blender,
    config_from_seed,
    run_blender_tests,
)
from sdk import TestContext as ArticraftTestContext


@pytest.mark.parametrize("seed", range(13))
def test_seeded_immersion_blenders_have_connected_non_overlapping_parts(seed: int) -> None:
    model = build_seeded_blender(seed)
    ctx = ArticraftTestContext(model)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)

    report = ctx.report()
    assert report.passed, report.failures


def test_tapered_handle_keeps_soft_grip_buttons_and_attached_cup() -> None:
    config = config_from_seed(5)
    assert config.handle_profile == "tapered_grip"

    model = build_blender(config)
    handle = model.get_part("motor_handle")
    cup = model.get_part("measuring_cup")

    handle_visuals = {visual.name for visual in handle.visuals}
    cup_visuals = {visual.name for visual in cup.visuals}

    assert {"soft_upper_grip_band", "narrow_lower_grip_band"} <= handle_visuals
    assert {"flush_speed_button", "pulse_button"} <= handle_visuals
    assert "cup_handle_bridge" in cup_visuals


@pytest.mark.parametrize(
    ("blade_style", "visual_name"),
    [
        ("whisk", "whisk_assembly"),
        ("flat_beater", "flat_beater_blade_main"),
        ("dough_hook", "dough_hook_upper_shaft"),
    ],
)
def test_stand_mixer_attachment_styles_and_splash_guard_remain_supported(
    blade_style: str,
    visual_name: str,
) -> None:
    config = BlenderConfig(blade_style=blade_style, guard_style="perforated_bell")
    model = build_blender(config)
    report = run_blender_tests(model, config)

    assert report.passed, report.failures
    assert model.get_part("blade_assembly").get_visual(visual_name) is not None
    assert model.get_part("shaft_assembly").get_visual("guard_perforation_bridge_0") is not None
