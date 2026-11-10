# SPDX-License-Identifier: Apache-2.0

"""Tests for the clearance-driven joint-limit solver (sdk.motion_solve)."""

from __future__ import annotations

import pytest

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    ClearanceProbe,
    MotionLimits,
    Origin,
    clamp_joint_limits,
    max_joint_value,
    min_clearance_at_pose,
)

# A door leaf hinged at the origin swinging about +z toward a wall slab
# parallel to the x-axis at y=0.28: the leaf (spanning x 0.05..0.39 at rest,
# clear of the hinge post) reaches the wall near asin(0.27/0.39) ~ 0.76 rad.
# The wall lives in its own FIXED part so keepout=["frame"] can exclude it.


def _door_and_wall() -> ArticulatedObject:
    model = ArticulatedObject(name="door_rig")
    frame = model.part("frame")
    frame.visual(Box((0.05, 0.05, 0.6)), origin=Origin(xyz=(0.0, 0.0, 0.3)), name="post")
    wall = model.part("wall")
    wall.visual(
        Box((0.7, 0.04, 0.6)),
        origin=Origin(xyz=(0.2, 0.30, 0.3)),
        name="wall_slab",
    )
    model.articulation(
        "frame_to_wall",
        ArticulationType.FIXED,
        parent=frame,
        child=wall,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    leaf = model.part("leaf")
    leaf.visual(Box((0.34, 0.02, 0.5)), origin=Origin(xyz=(0.22, 0.0, 0.25)), name="panel")
    model.articulation(
        "hinge",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=leaf,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=10.0, velocity=1.0, lower=-1.2, upper=1.2),
    )
    return model


def test_min_clearance_at_pose_decreases_toward_wall() -> None:
    model = _door_and_wall()
    at_rest = min_clearance_at_pose(model, joint="hinge", joint_positions={"hinge": 0.0})
    near_wall = min_clearance_at_pose(model, joint="hinge", joint_positions={"hinge": 0.6})
    assert at_rest > near_wall > 0.0


def test_clearance_probe_reuses_compiled_model_across_poses() -> None:
    model = _door_and_wall()
    probe = ClearanceProbe(model, joint_name="hinge")
    at_rest = probe.min_clearance({"hinge": 0.0})
    near_wall = probe.min_clearance({"hinge": 0.6})
    assert at_rest > near_wall > 0.0


def test_max_joint_value_stops_short_of_wall() -> None:
    model = _door_and_wall()
    solved = max_joint_value(model, joint="hinge", limit=1.2, margin=0.008)
    # Must stop short of wall contact (~0.76 rad) but well past halfway.
    assert 0.4 < solved < 0.80
    clearance = min_clearance_at_pose(model, joint="hinge", joint_positions={"hinge": solved})
    assert clearance >= 0.008 - 1e-6


def test_max_joint_value_full_range_when_clear() -> None:
    model = _door_and_wall()
    # Swinging AWAY from the wall is clear across the whole range.
    solved = max_joint_value(model, joint="hinge", limit=-1.2, margin=0.008)
    assert solved == -1.2


def test_max_joint_value_returns_start_when_rest_violates() -> None:
    model = _door_and_wall()
    # A tiny margin larger than the rest clearance makes the start unsafe.
    rest = min_clearance_at_pose(model, joint="hinge", joint_positions={"hinge": 0.0})
    solved = max_joint_value(model, joint="hinge", limit=1.2, margin=rest + 0.05)
    assert solved == 0.0


def test_clamp_joint_limits_writes_solved_range() -> None:
    model = _door_and_wall()
    limits = clamp_joint_limits(model, "hinge", margin=0.008)
    joint = next(j for j in model.articulations if j.name == "hinge")
    assert joint.motion_limits is limits
    assert limits.lower == -1.2  # away from the wall: untouched
    assert 0.4 < limits.upper < 0.80  # toward the wall: clamped
    assert limits.effort == 10.0 and limits.velocity == 1.0


def test_keepout_restriction_ignores_other_parts() -> None:
    model = _door_and_wall()
    # Only the frame (post) is keep-out -> the wall no longer constrains the swing.
    solved = max_joint_value(model, joint="hinge", limit=1.2, margin=0.008, keepout=["frame"])
    assert solved == pytest.approx(1.2)
