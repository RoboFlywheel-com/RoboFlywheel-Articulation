# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.wheelbarrow import (
    build_seeded_wheelbarrow,
    config_from_seed,
    run_wheelbarrow_tests,
)
from sdk import TestContext as ArticraftTestContext


def test_seeded_rotary_axes_follow_visible_axles() -> None:
    for seed in range(8):
        model = build_seeded_wheelbarrow(seed)
        joints = {joint.name: joint for joint in model.articulations}

        assert joints["wheel_spin"].axis == (0.0, 1.0, 0.0)
        if "frame_to_rear_stand" in joints:
            assert joints["frame_to_rear_stand"].axis == (0.0, 1.0, 0.0)


def test_wheel_disk_plane_matches_wheelbarrow_side_view() -> None:
    for seed in range(20):
        model = build_seeded_wheelbarrow(seed)
        aabb = ArticraftTestContext(model).part_world_aabb(model.get_part("front_wheel"))
        extents = tuple(aabb[1][i] - aabb[0][i] for i in range(3))

        assert extents[0] > extents[1] * 2.5
        assert extents[2] > extents[1] * 2.5


def test_template_qc_rejects_rear_stand_axis_not_on_hinge_cylinder() -> None:
    model = build_seeded_wheelbarrow(2)
    model.get_articulation("frame_to_rear_stand").axis = (1.0, 0.0, 0.0)

    report = run_wheelbarrow_tests(model, config_from_seed(2))

    assert not report.passed
    assert any(
        failure.name == "frame_to_rear_stand_axis_matches_visible_cylinder"
        for failure in report.failures
    )
