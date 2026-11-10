# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from sdk import ArticulatedObject, Mimic, MotionLimits, ValidationError
from sdk._core.v0._urdf_export import _articulation_element


def test_unknown_articulation_type() -> None:
    model = ArticulatedObject(name="planar_not_supported")
    base = model.part("base")
    slider = model.part("slider")

    with pytest.raises(ValidationError, match="Unknown articulation type"):
        model.articulation("base_to_slider", "planar", parent=base, child=slider)


def test_continuous_requires_motion_limits() -> None:
    model = ArticulatedObject(name="continuous_requires_limits")
    base = model.part("base")
    mast = model.part("mast")
    model.articulation("mast_slew", "continuous", parent=base, child=mast)

    with pytest.raises(
        ValidationError,
        match="must set motion_limits=MotionLimits\\(effort=..., velocity=...\\)",
    ):
        model.validate(strict=True)


def test_continuous_forbids_lower_upper_limits() -> None:
    model = ArticulatedObject(name="continuous_forbids_bounds")
    base = model.part("base")
    mast = model.part("mast")
    model.articulation(
        "mast_slew",
        "continuous",
        parent=base,
        child=mast,
        motion_limits=MotionLimits(
            effort=12.0,
            velocity=1.5,
            lower=0.0,
            upper=1.0,
        ),
    )

    with pytest.raises(ValidationError, match="cannot include lower/upper limits"):
        model.validate(strict=True)


def test_continuous_accepts_effort_velocity_only() -> None:
    model = ArticulatedObject(name="continuous_valid")
    base = model.part("base")
    mast = model.part("mast")
    model.articulation(
        "mast_slew",
        "continuous",
        parent=base,
        child=mast,
        motion_limits=MotionLimits(effort=12.0, velocity=1.5),
    )
    model.validate(strict=True)


def test_floating_forbids_motion_limits() -> None:
    model = ArticulatedObject(name="floating_forbids_limits")
    base = model.part("base")
    payload = model.part("payload")
    model.articulation(
        "base_to_payload",
        "floating",
        parent=base,
        child=payload,
        motion_limits=MotionLimits(effort=1.0, velocity=1.0),
    )

    with pytest.raises(ValidationError, match="does not support motion limits"):
        model.validate(strict=True)


def test_mimic_requires_existing_source() -> None:
    model = ArticulatedObject(name="mimic_missing_source")
    base = model.part("base")
    finger = model.part("finger")
    model.articulation(
        "base_to_finger",
        "revolute",
        parent=base,
        child=finger,
        motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=0.0, upper=1.0),
        mimic=Mimic(joint="missing_joint"),
    )

    with pytest.raises(ValidationError, match="mimic references missing articulation"):
        model.validate(strict=True)


def test_mimic_rejects_incompatible_motion_domain() -> None:
    model = ArticulatedObject(name="mimic_incompatible_domain")
    base = model.part("base")
    slider = model.part("slider")
    arm = model.part("arm")
    model.articulation(
        "base_to_slider",
        "prismatic",
        parent=base,
        child=slider,
        motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=0.0, upper=0.2),
    )
    model.articulation(
        "slider_to_arm",
        "revolute",
        parent=slider,
        child=arm,
        motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=-0.5, upper=0.5),
        mimic=Mimic(joint="base_to_slider"),
    )

    with pytest.raises(ValidationError, match="compatible motion domain"):
        model.validate(strict=True)


def test_mimic_rejects_cycles() -> None:
    model = ArticulatedObject(name="mimic_cycle")
    base = model.part("base")
    left = model.part("left")
    right = model.part("right")
    model.articulation(
        "base_to_left",
        "revolute",
        parent=base,
        child=left,
        motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=-1.0, upper=1.0),
        mimic=Mimic(joint="left_to_right"),
    )
    model.articulation(
        "left_to_right",
        "revolute",
        parent=left,
        child=right,
        motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=-1.0, upper=1.0),
        mimic=Mimic(joint="base_to_left"),
    )

    with pytest.raises(ValidationError, match="Mimic cycle detected"):
        model.validate(strict=True)


def test_strict_validation_rejects_multiple_root_parts() -> None:
    model = ArticulatedObject(name="multiple_roots")
    model.part("base")
    model.part("rogue")

    with pytest.raises(ValidationError, match="exactly one root part"):
        model.validate(strict=True)


def test_urdf_export_normalizes_motion_axis() -> None:
    model = ArticulatedObject(name="normalized_axis_export")
    base = model.part("base")
    arm = model.part("arm")
    joint = model.articulation(
        "base_to_arm",
        "revolute",
        parent=base,
        child=arm,
        axis=(0.0, 0.0, 10.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=-1.0, upper=1.0),
    )

    elem = _articulation_element(joint)
    axis_elem = elem.find("axis")
    assert axis_elem is not None
    assert axis_elem.attrib["xyz"] == "0 0 1"


def test_urdf_export_emits_mimic_element() -> None:
    model = ArticulatedObject(name="mimic_export")
    base = model.part("base")
    left = model.part("left")
    right = model.part("right")
    model.articulation(
        "base_to_left",
        "revolute",
        parent=base,
        child=left,
        motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=0.0, upper=0.6),
    )
    joint = model.articulation(
        "base_to_right",
        "revolute",
        parent=base,
        child=right,
        motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=-0.6, upper=0.0),
        mimic=Mimic(joint="base_to_left", multiplier=-1.0, offset=0.05),
    )

    elem = _articulation_element(joint)
    mimic_elem = elem.find("mimic")
    assert mimic_elem is not None
    assert mimic_elem.attrib == {
        "joint": "base_to_left",
        "multiplier": "-1",
        "offset": "0.05",
    }
