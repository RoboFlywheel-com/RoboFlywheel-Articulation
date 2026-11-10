# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.camera_flash import (
    CameraFlashConfig,
    build_camera_flash,
    build_seeded_camera_flash,
    config_from_seed,
    resolve_config,
    run_camera_flash_tests,
)
from sdk import ArticulationType
from sdk import TestContext as ArticraftTestContext


def _axis_gap(aabb_a, aabb_b, axis: int) -> float:
    return max(aabb_b[0][axis] - aabb_a[1][axis], aabb_a[0][axis] - aabb_b[1][axis], 0.0)


def test_resolve_rejects_invalid_neck_style() -> None:
    with pytest.raises(ValueError, match="neck_style"):
        resolve_config(CameraFlashConfig(neck_style="bad"))  # type: ignore[arg-type]


def test_resolve_rejects_non_bool_bounce_flag() -> None:
    with pytest.raises(ValueError, match="bounce_card_enabled"):
        resolve_config(CameraFlashConfig(bounce_card_enabled=1))  # type: ignore[arg-type]


def test_builds_identity_and_main_joints() -> None:
    config = CameraFlashConfig()
    model = build_camera_flash(config)
    report = run_camera_flash_tests(model, config)

    assert report.passed, report.failures
    assert model.get_articulation("body_to_neck_yaw").axis == (0.0, 0.0, 1.0)
    assert (
        model.get_articulation("neck_to_head_tilt").articulation_type == ArticulationType.REVOLUTE
    )


def test_side_yoke_uses_normalized_tilt_axis() -> None:
    model = build_camera_flash(CameraFlashConfig(neck_style="side_yoke_arms"))

    assert model.get_articulation("neck_to_head_tilt").axis == (1.0, 0.0, 0.0)


def test_head_tilt_barrel_is_seated_in_neck_yoke() -> None:
    model = build_camera_flash(CameraFlashConfig(neck_style="trunnion_yoke"))
    head_visuals = {visual.name for visual in model.get_part("head").visuals}

    assert {"tilt_barrel", "tilt_barrel_to_head_bridge", "front_diffuser"} <= head_visuals


def test_short_neck_axis_caps_touch_tilt_barrel() -> None:
    model = build_camera_flash(CameraFlashConfig(neck_style="short_neck"))
    ctx = ArticraftTestContext(model)
    head = model.get_part("head")
    barrel_aabb = ctx.part_element_world_aabb(head, elem="tilt_barrel")

    assert barrel_aabb is not None
    for cap_name in ("tilt_axis_cap_0", "tilt_axis_cap_1"):
        cap_aabb = ctx.part_element_world_aabb(head, elem=cap_name)
        assert cap_aabb is not None
        assert _axis_gap(barrel_aabb, cap_aabb, axis=0) == pytest.approx(0.0, abs=1e-6)


def test_side_yoke_pedestal_embeds_bridge_into_swivel_disk() -> None:
    model = build_camera_flash(CameraFlashConfig(neck_style="side_yoke_arms"))
    ctx = ArticraftTestContext(model)
    neck = model.get_part("neck")
    head = model.get_part("head")
    neck_visuals = {visual.name for visual in neck.visuals}
    disk_aabb = ctx.part_element_world_aabb(neck, elem="swivel_disk")
    pedestal_aabb = ctx.part_element_world_aabb(neck, elem="yoke_pedestal")
    bridge_aabb = ctx.part_element_world_aabb(neck, elem="rear_bridge")
    saddle_aabb = ctx.part_element_world_aabb(head, elem="tilt_saddle_contact")

    assert "yoke_pedestal" in neck_visuals
    assert disk_aabb is not None
    assert pedestal_aabb is not None
    assert bridge_aabb is not None
    assert saddle_aabb is not None
    assert disk_aabb[1][2] >= pedestal_aabb[0][2] - 1e-6
    assert pedestal_aabb[1][2] >= bridge_aabb[0][2] - 1e-6
    assert pedestal_aabb[1][2] <= saddle_aabb[0][2] + 1e-6


def test_bounce_card_and_battery_door_optional_joints() -> None:
    model = build_camera_flash(
        CameraFlashConfig(bounce_card_enabled=True, battery_door_enabled=True)
    )

    assert (
        model.get_articulation("bounce_card_slide").articulation_type == ArticulationType.PRISMATIC
    )
    assert model.get_articulation("bounce_card_slide").axis == (0.0, 0.0, 1.0)
    assert (
        model.get_articulation("battery_door_hinge").articulation_type == ArticulationType.REVOLUTE
    )


def test_control_layout_adds_dial_and_button_joints() -> None:
    model = build_camera_flash(CameraFlashConfig(control_layout="screen_dial_buttons"))

    assert model.get_articulation("rear_dial_turn").articulation_type == ArticulationType.REVOLUTE
    assert len([j for j in model.articulations if j.name.startswith("button_press_")]) == 3


def test_diversity_parameters_change_geometry() -> None:
    rails = build_camera_flash(CameraFlashConfig(mount_style="rails_shoe_block"))
    plate = build_camera_flash(CameraFlashConfig(mount_style="plate_only"))
    rail_visuals = {v.name for v in rails.get_part("body").visuals if v.name}
    plate_visuals = {v.name for v in plate.get_part("body").visuals if v.name}

    assert any(name.startswith("hotshoe_rail_") for name in rail_visuals)
    assert not any(name.startswith("hotshoe_rail_") for name in plate_visuals)


def test_joint_metadata_includes_spec_fields() -> None:
    model = build_camera_flash(
        CameraFlashConfig(
            bounce_card_enabled=True,
            battery_door_enabled=True,
            control_layout="screen_dial_buttons",
        )
    )

    for joint in model.articulations:
        if joint.articulation_type != ArticulationType.FIXED:
            assert {"type", "axis", "origin", "range"}.issubset(joint.meta)


def test_seed_config_reproducible_and_varied() -> None:
    assert config_from_seed(3) == config_from_seed(3)
    assert config_from_seed(3) != config_from_seed(4)
    configs = [config_from_seed(seed) for seed in range(40)]
    assert len({config.neck_style for config in configs}) >= 2
    assert len({config.head_shape for config in configs}) >= 2


def test_run_camera_flash_tests_passes_for_variants() -> None:
    for config in (
        CameraFlashConfig(),
        CameraFlashConfig(neck_style="side_yoke_arms", head_shape="wide_professional"),
        CameraFlashConfig(
            bounce_card_enabled=False, battery_door_enabled=True, control_layout="button_bank"
        ),
    ):
        report = run_camera_flash_tests(build_camera_flash(config), config)
        assert report.passed, report.failures


def test_seeded_models_pass_strict_geometry_qc() -> None:
    for seed in (0, 1, 2, 5, 6, 9, 10, 12, 13, 16, 17, 19, 20):
        ctx = ArticraftTestContext(build_seeded_camera_flash(seed))
        ctx.check_model_valid()
        ctx.fail_if_isolated_parts()
        ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
        report = ctx.report()
        assert report.passed, report.failures
