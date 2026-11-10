# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.desktop_pc_tower import (
    DesktopPcTowerConfig,
    build_desktop_pc_tower,
    config_from_seed,
    resolve_config,
    run_desktop_pc_tower_tests,
)
from sdk import TestContext as ArticraftTestContext


def _assert_strict_qc_passes(model) -> None:
    ctx = ArticraftTestContext(model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_part_contains_disconnected_geometry_islands(tol=0.002)
    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
    report = ctx.report()
    assert report.passed, report.failures


def _center(aabb):
    mins, maxs = aabb
    return tuple((lo + hi) * 0.5 for lo, hi in zip(mins, maxs))


def test_resolve_rejects_invalid_drawer_count() -> None:
    with pytest.raises(ValueError, match="drive_tray_count"):
        resolve_config(DesktopPcTowerConfig(drive_tray_count=9))


def test_resolve_scales_height_to_drawer_count() -> None:
    config = DesktopPcTowerConfig(case_height=0.30, drive_tray_count=7, drawer_height=0.070)
    resolved = resolve_config(config)

    assert resolved.drive_tray_count == 7
    assert resolved.case_height > config.case_height
    assert resolved.drawer_pitch > resolved.drawer_height


def test_builds_sealed_drawer_tower() -> None:
    config = DesktopPcTowerConfig(drive_tray_count=5, case_width=0.34, case_depth=0.56)
    model = build_desktop_pc_tower(config)
    chassis_visuals = {visual.name for visual in model.get_part("chassis").visuals}

    assert {"left_wall", "right_wall", "rear_wall", "top_wall", "bottom_wall"} <= chassis_visuals
    assert {"front_left_post", "front_right_post", "front_header", "front_sill"} <= chassis_visuals
    assert "side_panel" not in {part.name for part in model.parts}
    assert "top_panel" not in {part.name for part in model.parts}


def test_clear_gray_lab_palette_keeps_translucent_case_type() -> None:
    model = build_desktop_pc_tower(DesktopPcTowerConfig(material_style="clear_gray_lab"))
    case_material = next(material for material in model.materials if material.name == "pc_case")

    assert case_material.rgba[3] < 1.0


def test_drawer_count_and_motion_are_constrained() -> None:
    config = DesktopPcTowerConfig(drive_tray_count=4, tray_travel=0.16)
    resolved = resolve_config(config)
    model = build_desktop_pc_tower(config)
    ctx = ArticraftTestContext(model)

    tray_joints = [
        joint for joint in model.articulations if joint.name.startswith("drive_tray_slide_")
    ]
    assert len(tray_joints) == resolved.drive_tray_count
    assert all(joint.axis == (0.0, 1.0, 0.0) for joint in tray_joints)

    first_joint = model.get_articulation("drive_tray_slide_0")
    first_tray = model.get_part("drive_tray_0")
    fascia = next(visual for visual in first_tray.visuals if visual.name == "fascia")
    rest_center = _center(ctx.part_element_world_aabb(first_tray, elem=fascia))
    with ctx.pose({first_joint: resolved.tray_travel * 0.85}):
        open_center = _center(ctx.part_element_world_aabb(first_tray, elem=fascia))

    assert open_center[1] > rest_center[1] + resolved.tray_travel * 0.50
    assert first_joint.motion_limits.upper <= resolved.case_depth * 0.45


def test_seed_config_is_reproducible() -> None:
    assert config_from_seed(21) == config_from_seed(21)
    assert config_from_seed(21) != config_from_seed(22)


def test_run_desktop_pc_tower_tests_passes() -> None:
    config = DesktopPcTowerConfig(drive_tray_count=5, drawer_height=0.058)
    report = run_desktop_pc_tower_tests(build_desktop_pc_tower(config), config)

    assert report.passed, report.failures


def test_seed_zero_to_ten_pass_strict_qc() -> None:
    for seed in range(11):
        _assert_strict_qc_passes(build_desktop_pc_tower(config_from_seed(seed)))


def test_known_review_seeds_pass_strict_qc() -> None:
    for seed in (80, 81, 82, 83, 84, 85):
        _assert_strict_qc_passes(build_desktop_pc_tower(config_from_seed(seed)))
