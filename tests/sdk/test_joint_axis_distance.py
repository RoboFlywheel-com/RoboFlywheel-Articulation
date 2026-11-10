# SPDX-License-Identifier: Apache-2.0

"""Tests for the SHADOW joint-axis-distance metric (report-only, not a gate).

Covers the semantic contract of ``find_joint_axis_distance_findings`` /
``measure_joint_axis_distances``:

- a mid-air phantom pivot (axis passes through neither part) still FAILS;
- a prismatic origin displaced ALONG the slide axis PASSES (the intended win
  over the point metric);
- a continuous/revolute axle whose axis line passes through the wheel PASSES;
- FIXED joints keep the legacy origin-point semantics.
"""

from __future__ import annotations

from sdk import ArticulatedObject, ArticulationType, Box, Cylinder, Origin
from sdk._core.v0.geometry_qc import (
    find_joint_axis_distance_findings,
    find_joint_origin_distance_findings,
    measure_joint_axis_distances,
)


def _measurement(model: ArticulatedObject, joint_name: str):
    measurements = measure_joint_axis_distances(model, validate_model=False)
    by_name = {m.joint: m for m in measurements}
    assert joint_name in by_name, f"no measurement for joint {joint_name!r}: {sorted(by_name)}"
    return by_name[joint_name]


def _build_phantom_pivot_model() -> ArticulatedObject:
    """Revolute joint whose origin floats in mid-air AND whose axis line passes
    through neither the parent nor the child geometry."""
    model = ArticulatedObject(name="phantom_pivot")
    base = model.part("base")
    base.visual(Box((0.1, 0.1, 0.1)), origin=Origin(xyz=(0.0, 0.0, 0.0)), name="base_box")
    flap = model.part("flap")
    # Child geometry offset in the child frame so the (vertical) axis through
    # the child origin misses it too.
    flap.visual(Box((0.1, 0.1, 0.1)), origin=Origin(xyz=(0.2, 0.0, 0.0)), name="flap_box")
    model.articulation(
        "phantom_hinge",
        ArticulationType.REVOLUTE,
        parent=base,
        child=flap,
        origin=Origin(xyz=(0.3, 0.3, 0.3)),
        axis=(0.0, 0.0, 1.0),
    )
    return model


def test_phantom_midair_pivot_fails_axis_metric() -> None:
    model = _build_phantom_pivot_model()
    m = _measurement(model, "phantom_hinge")
    assert m.axis_based
    assert m.parent_axis_distance > 0.020
    assert m.child_axis_distance > 0.020

    findings = find_joint_axis_distance_findings(model, tol=0.015, validate_model=False)
    assert [f.joint for f in findings] == ["phantom_hinge"]
    finding = findings[0]
    assert finding.axis_based
    assert finding.parent_distance > 0.015
    assert finding.child_distance > 0.015


def _build_axial_offset_prismatic_model() -> ArticulatedObject:
    """Prismatic joint whose origin is displaced along the slide axis: the old
    point metric reads the child as far, but the axis line passes through both
    the rail and the slider."""
    model = ArticulatedObject(name="axial_offset_slide")
    rail = model.part("rail")
    rail.visual(Box((1.0, 0.06, 0.06)), origin=Origin(xyz=(0.0, 0.0, 0.0)), name="rail_bar")
    slider = model.part("slider")
    # Slider geometry sits 0.3 m down the slide axis from the child origin.
    slider.visual(Box((0.1, 0.05, 0.05)), origin=Origin(xyz=(0.3, 0.0, 0.0)), name="slider_block")
    model.articulation(
        "slide",
        ArticulationType.PRISMATIC,
        parent=rail,
        child=slider,
        origin=Origin(xyz=(0.4, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
    )
    return model


def test_axial_offset_prismatic_passes_axis_metric() -> None:
    model = _build_axial_offset_prismatic_model()
    m = _measurement(model, "slide")
    assert m.axis_based
    # The point metric sees the child geometry as far from the origin...
    assert m.child_point_distance > m.point_tol
    # ...but prismatic origin position is pure gauge freedom, so the live gate
    # applies NO positional check to prismatic joints at all (clean semantics).
    assert find_joint_origin_distance_findings(model, validate_model=False) == []
    # The axis line passes through both parts.
    assert m.parent_axis_distance <= 0.001
    assert m.child_axis_distance <= 0.001
    assert find_joint_axis_distance_findings(model, tol=0.010, validate_model=False) == []


def _build_axle_through_wheel_model() -> ArticulatedObject:
    """Continuous axle: the joint origin sits outside the wheel, but the axis
    line passes straight through the hub."""
    model = ArticulatedObject(name="axle_wheel")
    fork = model.part("fork")
    fork.visual(Box((0.04, 0.04, 0.3)), origin=Origin(xyz=(0.0, 0.0, 0.15)), name="fork_leg")
    wheel = model.part("wheel")
    # Wheel disc 0.1 m along the axle (+z in the child frame, cylinder axis =
    # z), so the child ORIGIN POINT is 0.075 m clear of the disc face.
    wheel.visual(Cylinder(radius=0.2, length=0.05), origin=Origin(xyz=(0.0, 0.0, 0.1)), name="disc")
    model.articulation(
        "axle_spin",
        ArticulationType.CONTINUOUS,
        parent=fork,
        child=wheel,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
    )
    return model


def test_revolute_axle_through_wheel_passes_axis_metric() -> None:
    model = _build_axle_through_wheel_model()
    m = _measurement(model, "axle_spin")
    assert m.axis_based
    # Point metric: the child origin point is 0.075 m from the wheel disc,
    # beyond the old effective tol.
    assert m.child_point_distance > m.point_tol
    # Axis metric: the axle line passes through the disc.
    assert m.child_axis_distance <= 0.001
    assert m.parent_axis_distance <= 0.001
    assert find_joint_axis_distance_findings(model, tol=0.010, validate_model=False) == []


def _build_fixed_models() -> tuple[ArticulatedObject, ArticulatedObject]:
    def build(child_offset: tuple[float, float, float], name: str) -> ArticulatedObject:
        model = ArticulatedObject(name=name)
        base = model.part("base")
        base.visual(Box((0.2, 0.2, 0.02)), origin=Origin(xyz=(0.0, 0.0, 0.0)), name="base_plate")
        tab = model.part("tab")
        tab.visual(Box((0.05, 0.05, 0.05)), origin=Origin(xyz=child_offset), name="tab_box")
        model.articulation(
            "mount",
            ArticulationType.FIXED,
            parent=base,
            child=tab,
            origin=Origin(xyz=(0.0, 0.0, 0.01)),
            # A vertical axis WOULD pass through the offset tab geometry only
            # if axis semantics were (wrongly) applied to FIXED joints.
            axis=(1.0, 0.0, 0.0),
        )
        return model

    touching = build((0.0, 0.0, 0.025), "fixed_touching")
    floating = build((0.0, 0.0, 0.3), "fixed_floating")
    return touching, floating


def test_fixed_joint_falls_back_to_point_distance() -> None:
    touching, floating = _build_fixed_models()

    m_ok = _measurement(touching, "mount")
    assert not m_ok.axis_based
    assert m_ok.axis_half_length == 0.0
    assert m_ok.parent_axis_distance == m_ok.parent_point_distance
    assert m_ok.child_axis_distance == m_ok.child_point_distance
    assert find_joint_axis_distance_findings(touching, tol=0.015, validate_model=False) == []

    m_bad = _measurement(floating, "mount")
    assert not m_bad.axis_based
    # The x-axis through the child origin would graze nothing either way, but
    # the point distance is what must be reported for FIXED joints.
    assert m_bad.child_axis_distance == m_bad.child_point_distance
    assert m_bad.child_point_distance > 0.2
    findings = find_joint_axis_distance_findings(floating, tol=0.015, validate_model=False)
    assert [f.joint for f in findings] == ["mount"]
    assert not findings[0].axis_based
