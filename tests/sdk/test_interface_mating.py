# SPDX-License-Identifier: Apache-2.0

import math

import pytest

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AxisInterface,
    Origin,
    PlaneInterface,
    ValidationError,
    find_interface_mate_findings,
    mate_axes,
    mate_planes,
    register_interface_mate,
)
from sdk import (
    TestContext as SDKTestContext,
)


def test_mate_planes_places_consumer_at_declared_gap() -> None:
    tilt = math.radians(18.0)
    provider = PlaneInterface(
        name="body.front",
        point=(0.0, -0.03, 0.01),
        normal=(0.0, -math.cos(tilt), -math.sin(tilt)),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(0.12, 0.10),
    )
    consumer = PlaneInterface(
        name="dial.back",
        normal=(0.0, 1.0, 0.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(0.07, 0.07),
    )

    mate = mate_planes(provider, consumer, gap=0.0002)

    assert mate.origin.xyz == pytest.approx(
        (
            0.0,
            -0.03 - math.cos(tilt) * 0.0002,
            0.01 - math.sin(tilt) * 0.0002,
        )
    )
    assert mate.origin.rpy == pytest.approx((tilt, 0.0, 0.0))


def test_mate_planes_rejects_out_of_bounds_footprint() -> None:
    provider = PlaneInterface(name="host", extent=(0.10, 0.08))
    consumer = PlaneInterface(name="child", extent=(0.09, 0.07))

    with pytest.raises(ValidationError, match="does not fit"):
        mate_planes(provider, consumer, uv=(0.02, 0.0), margin=0.001)


def test_mate_axes_aligns_different_local_axis_frames() -> None:
    provider = AxisInterface(
        name="housing.axis",
        point=(0.01, 0.02, 0.03),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.01,
    )
    consumer = AxisInterface(
        name="shaft.axis",
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.004,
    )

    mate = mate_axes(
        provider,
        consumer,
        axial_offset=0.005,
        require_fit=True,
        radial_clearance=0.001,
    )

    assert mate.origin.xyz == pytest.approx((0.01, 0.015, 0.03))
    assert mate.origin.rpy == pytest.approx((math.pi / 2.0, 0.0, 0.0))
    assert mate.axis == pytest.approx((0.0, 0.0, 1.0))
    assert mate.axis_origin_offset == pytest.approx(0.0)


def test_registered_axis_mate_detects_wrong_motion_axis() -> None:
    model = ArticulatedObject(name="axis_mate_test")
    parent = model.part("fork")
    child = model.part("wheel")
    mate = mate_axes(
        AxisInterface(name="fork.axle", axis=(1.0, 0.0, 0.0)),
        AxisInterface(name="wheel.spin", axis=(0.0, 0.0, 1.0)),
    )
    joint = model.articulation(
        "wheel_spin",
        ArticulationType.CONTINUOUS,
        parent,
        child,
        origin=mate.origin,
        axis=mate.axis,
    )
    register_interface_mate(model, "wheel_spin", mate)
    assert find_interface_mate_findings(model) == ()

    joint.axis = (1.0, 0.0, 0.0)
    findings = find_interface_mate_findings(model)
    assert len(findings) == 1
    assert "axis_error" in findings[0].reason


def test_strict_rotational_contract_reports_missing_axis_mate() -> None:
    model = ArticulatedObject(name="missing_axis_mate")
    parent = model.part("fork")
    child = model.part("wheel")
    model.articulation(
        "wheel_spin",
        ArticulationType.CONTINUOUS,
        parent,
        child,
        axis=(1.0, 0.0, 0.0),
    )

    assert find_interface_mate_findings(model) == ()
    findings = find_interface_mate_findings(model, require_rotational_axis_mates=True)

    assert len(findings) == 1
    assert findings[0].joint == "wheel_spin"
    assert "no registered AxisInterface mate" in findings[0].reason


def test_strict_rotational_contract_passes_for_registered_axis_mate() -> None:
    model = ArticulatedObject(name="registered_axis_mate")
    parent = model.part("fork")
    child = model.part("wheel")
    mate = mate_axes(
        AxisInterface(name="fork.axle", axis=(1.0, 0.0, 0.0)),
        AxisInterface(
            name="wheel.spin",
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
        ),
    )
    model.articulation(
        "wheel_spin",
        ArticulationType.CONTINUOUS,
        parent,
        child,
        origin=mate.origin,
        axis=mate.axis,
    )
    register_interface_mate(model, "wheel_spin", mate)

    assert find_interface_mate_findings(model, require_rotational_axis_mates=True) == ()


def test_rotational_joint_rejects_plane_interface_registration() -> None:
    model = ArticulatedObject(name="wrong_interface_kind")
    parent = model.part("frame")
    child = model.part("wheel")
    mate = mate_planes(
        PlaneInterface(name="frame.face"),
        PlaneInterface(name="wheel.face", normal=(0.0, 0.0, -1.0)),
    )
    model.articulation(
        "wheel_spin",
        ArticulationType.REVOLUTE,
        parent,
        child,
        origin=mate.origin,
    )

    with pytest.raises(ValidationError, match="requires an axis interface mate"):
        register_interface_mate(model, "wheel_spin", mate)


def test_rotating_axis_interface_must_pass_through_child_origin() -> None:
    model = ArticulatedObject(name="offset_axis_test")
    parent = model.part("fork")
    child = model.part("wheel")
    mate = mate_axes(
        AxisInterface(name="fork.axle", axis=(1.0, 0.0, 0.0)),
        AxisInterface(
            name="wheel.bad_spin",
            point=(0.0, 0.02, 0.0),
            axis=(1.0, 0.0, 0.0),
        ),
    )
    model.articulation(
        "wheel_spin",
        ArticulationType.CONTINUOUS,
        parent,
        child,
        origin=mate.origin,
        axis=mate.axis,
    )

    with pytest.raises(ValidationError, match="center the moving component on that axis"):
        register_interface_mate(model, "wheel_spin", mate)


def test_registered_interface_mate_detects_joint_origin_drift() -> None:
    model = ArticulatedObject(name="interface_mate_test")
    parent = model.part("parent")
    child = model.part("child")
    mate = mate_planes(
        PlaneInterface(name="parent.face", normal=(0.0, -1.0, 0.0)),
        PlaneInterface(name="child.back", normal=(0.0, 1.0, 0.0)),
        gap=0.001,
    )
    joint = model.articulation(
        "mount",
        ArticulationType.FIXED,
        parent,
        child,
        origin=mate.origin,
    )
    register_interface_mate(model, "mount", mate)

    assert find_interface_mate_findings(model) == ()

    joint.origin = Origin(
        xyz=(joint.origin.xyz[0] + 0.002, *joint.origin.xyz[1:]),
        rpy=joint.origin.rpy,
    )
    findings = find_interface_mate_findings(model)
    assert len(findings) == 1
    assert findings[0].joint == "mount"
    assert "linear_error" in findings[0].reason

    ctx = SDKTestContext(model)
    assert not ctx.fail_if_interface_mate_mismatch()
    report = ctx.report()
    assert not report.passed
    assert "Interface mate mismatch detected" in report.failures[0].details
