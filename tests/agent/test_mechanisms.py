# SPDX-License-Identifier: Apache-2.0

"""Tests for SDK mechanisms and legacy agent mechanism compatibility."""

from __future__ import annotations

import math

import pytest

from agent.templates._mechanisms import sliding_member
from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    MotionLimits,
    Origin,
    coupled_chain,
    hinged_panel,
)


def _cabinet(model: ArticulatedObject):
    """Cabinet body with a wall behind (+y) — a door must open toward -y."""
    body = model.part("body")
    body.visual(Box((0.6, 0.4, 0.8)), origin=Origin(xyz=(0.0, 0.25, 0.4)), name="carcass")
    door = model.part("door")
    door.visual(Box((0.55, 0.02, 0.75)), origin=Origin(xyz=(0.275, 0.0, 0.375)), name="leaf")
    return body, door


def test_hinged_panel_accepts_correct_swing_and_solves_limit() -> None:
    model = ArticulatedObject(name="cabinet")
    body, door = _cabinet(model)
    limits = hinged_panel(
        model,
        joint_name="door_hinge",
        parent=body,
        panel=door,
        hinge_origin=(-0.3, 0.0, 0.0),
        axis=(0.0, 0.0, -1.0),  # opens toward -y (out the front)
        open_toward=(0.0, -1.0, 0.0),
        max_open=math.radians(170.0),
    )
    joint = next(j for j in model.articulations if j.name == "door_hinge")
    assert joint.motion_limits is limits
    # The full 170° would fold the door back along the body flank; some open
    # range must survive and the solver may keep all of it or trim it.
    assert limits.upper > math.radians(60.0)


def test_hinged_panel_rejects_reversed_swing() -> None:
    model = ArticulatedObject(name="cabinet_bad")
    body, door = _cabinet(model)
    with pytest.raises(ValueError, match="reversed-swing"):
        hinged_panel(
            model,
            joint_name="door_hinge",
            parent=body,
            panel=door,
            hinge_origin=(-0.3, 0.0, 0.0),
            axis=(0.0, 0.0, 1.0),  # swings INTO the carcass (+y)
            open_toward=(0.0, -1.0, 0.0),
        )


def test_sliding_member_travel_stops_below_ceiling() -> None:
    model = ArticulatedObject(name="box_rig")
    body = model.part("body")
    body.visual(Box((0.5, 0.4, 0.02)), origin=Origin(xyz=(0.0, 0.0, 0.01)), name="floor")
    body.visual(Box((0.5, 0.4, 0.02)), origin=Origin(xyz=(0.0, 0.0, 0.31)), name="ceiling")
    tray = model.part("tray")
    tray.visual(Box((0.4, 0.3, 0.04)), origin=Origin(xyz=(0.0, 0.0, 0.05)), name="pan")
    limits = sliding_member(
        model,
        joint_name="tray_lift",
        parent=body,
        slider=tray,
        origin=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        max_travel=0.5,
        margin=0.008,
    )
    # Tray top at rest = 0.07; ceiling underside = 0.30 -> travel <= ~0.222.
    assert 0.15 < limits.upper < 0.2301
    assert limits.upper < 0.5


def test_coupled_chain_wires_mimics_and_caps_budget() -> None:
    model = ArticulatedObject(name="chain_rig")
    base = model.part("base")
    base.visual(Box((0.1, 0.1, 0.05)), origin=Origin(xyz=(0.0, 0.0, 0.025)), name="pad")
    prev = base
    joint_names = []
    for i in range(3):
        link = model.part(f"link_{i}")
        link.visual(Box((0.3, 0.02, 0.05)), origin=Origin(xyz=(0.15, 0.0, 0.09)), name="bar")
        name = f"j{i}"
        model.articulation(
            name,
            ArticulationType.REVOLUTE,
            parent=prev,
            child=link,
            origin=Origin(xyz=(0.3 if i else 0.0, 0.0, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=5.0, velocity=1.0, lower=-2.5, upper=2.5),
        )
        joint_names.append(name)
        prev = link
    limits = coupled_chain(
        model,
        driver="j0",
        followers=["j1", "j2"],
        multipliers=[1.0, 1.0],
        fold_budget=2.4,
    )
    joints = {j.name: j for j in model.articulations}
    assert joints["j1"].mimic is not None and joints["j1"].mimic.joint == "j0"
    assert joints["j2"].mimic is not None
    # Budget 2.4 over gain 3 -> driver capped at +-0.8 before solving.
    assert limits.upper <= 0.8 + 1e-9
    assert limits.lower >= -0.8 - 1e-9


def _chain_rig(with_wall: bool) -> ArticulatedObject:
    model = ArticulatedObject(name="chain_rig2")
    base = model.part("base")
    base.visual(Box((0.1, 0.1, 0.05)), origin=Origin(xyz=(0.0, 0.0, 0.025)), name="pad")
    if with_wall:
        wall = model.part("wall")
        # Wall at +y: the chain folds toward it under positive joint values.
        wall.visual(Box((0.9, 0.03, 0.3)), origin=Origin(xyz=(0.3, 0.22, 0.1)), name="slab")
        model.articulation(
            "base_to_wall",
            ArticulationType.FIXED,
            parent=base,
            child=wall,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
    prev = base
    for i in range(3):
        link = model.part(f"link_{i}")
        link.visual(Box((0.3, 0.02, 0.05)), origin=Origin(xyz=(0.15, 0.0, 0.09)), name="bar")
        model.articulation(
            f"j{i}",
            ArticulationType.REVOLUTE,
            parent=prev,
            child=link,
            origin=Origin(xyz=(0.3 if i else 0.0, 0.0, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=5.0, velocity=1.0, lower=-2.5, upper=2.5),
        )
        prev = link
    return model


def test_coupled_chain_solves_on_the_coupled_trajectory() -> None:
    """The clearance solve must reflect the MIMIC-coupled sweep: with a wall
    in the fold path the driver's limit lands strictly below the budget cap;
    without the wall it reaches the cap (tested above)."""
    model = _chain_rig(with_wall=True)
    limits = coupled_chain(
        model,
        driver="j0",
        followers=["j1", "j2"],
        multipliers=[1.0, 1.0],
        fold_budget=2.4,
    )
    assert limits.upper < 0.8 - 1e-6  # wall trims the +fold side below the cap
    assert limits.lower == pytest.approx(-0.8)  # away side keeps the budget cap


def test_coupled_chain_rejects_follower_outside_driver_subtree() -> None:
    model = ArticulatedObject(name="siblings")
    base = model.part("base")
    base.visual(Box((0.2, 0.2, 0.02)), origin=Origin(xyz=(0.0, 0.0, 0.01)), name="top")
    for i in range(2):
        leg = model.part(f"leg_{i}")
        leg.visual(Box((0.02, 0.02, 0.3)), origin=Origin(xyz=(0.0, 0.0, -0.15)), name="post")
        model.articulation(
            f"leg_fold_{i}",
            ArticulationType.REVOLUTE,
            parent=base,
            child=leg,
            origin=Origin(xyz=(0.08 if i else -0.08, 0.0, 0.0)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=5.0, velocity=1.0, lower=0.0, upper=1.5),
        )
    with pytest.raises(ValueError, match="OUTSIDE the driver's"):
        coupled_chain(model, driver="leg_fold_0", followers=["leg_fold_1"])


def test_sliding_member_raises_on_collapsed_travel() -> None:
    model = ArticulatedObject(name="flipped_drawer")
    body = model.part("body")
    body.visual(Box((0.4, 0.4, 0.4)), origin=Origin(xyz=(0.0, 0.25, 0.2)), name="carcass")
    drawer = model.part("drawer")
    drawer.visual(Box((0.3, 0.2, 0.1)), origin=Origin(xyz=(0.0, -0.11, 0.05)), name="tray")
    with pytest.raises(ValueError, match="cannot move"):
        sliding_member(
            model,
            joint_name="slide",
            parent=body,
            slider=drawer,
            origin=(0.0, 0.0, 0.0),
            axis=(0.0, 1.0, 0.0),  # flipped: slides INTO the carcass
            max_travel=1.5,
        )
    assert all(j.name != "slide" for j in model.articulations)  # rolled back


def test_hinged_panel_rejects_centroid_on_axis() -> None:
    model = ArticulatedObject(name="axis_centroid")
    frame = model.part("frame")
    frame.visual(Box((0.05, 0.05, 0.5)), origin=Origin(xyz=(0.0, 0.0, 0.25)), name="post")
    disc = model.part("disc")
    # Single visual centered exactly on the hinge axis (z through origin).
    disc.visual(Box((0.2, 0.2, 0.01)), origin=Origin(xyz=(0.0, 0.0, 0.0)), name="plate")
    with pytest.raises(ValueError, match="centroid sits on the hinge axis"):
        hinged_panel(
            model,
            joint_name="spin",
            parent=frame,
            panel=disc,
            hinge_origin=(0.0, 0.0, 0.0),
            axis=(0.0, 0.0, 1.0),
            open_toward=(0.0, -1.0, 0.0),
        )
    assert all(j.name != "spin" for j in model.articulations)
