# SPDX-License-Identifier: Apache-2.0

"""Clean per-type semantics of the LIVE origin gate
(``find_joint_origin_distance_findings``): rotational = axis-OR-centerline,
prismatic = exempt (gauge freedom), fixed = flat point tol, and NO
bbox-relative loosening anywhere.
"""

from __future__ import annotations

from sdk import ArticulatedObject, ArticulationType, Box, Cylinder, Origin
from sdk._core.v0.geometry_qc import find_joint_origin_distance_findings


def _gate(model):
    return find_joint_origin_distance_findings(model, validate_model=False)


def test_ring_bearing_passes_via_centerline_clause() -> None:
    """A lens-ring / dome-style annulus: geometry far from the axis on both
    sides, but the axis IS the symmetry centerline."""
    model = ArticulatedObject(name="ring_bearing")
    barrel = model.part("barrel")
    barrel.visual(
        Cylinder(radius=0.08, length=0.3), origin=Origin(xyz=(0.0, 0.0, 0.0)), name="tube"
    )
    ring = model.part("ring")
    # Annular ring approximated by 4 pads at radius 0.1 — nothing near the axis.
    for i, (x, y) in enumerate(((0.1, 0), (-0.1, 0), (0, 0.1), (0, -0.1))):
        ring.visual(Box((0.02, 0.02, 0.03)), origin=Origin(xyz=(x, y, 0.0)), name=f"pad_{i}")
    model.articulation(
        "ring_turn",
        ArticulationType.REVOLUTE,
        parent=barrel,
        child=ring,
        origin=Origin(xyz=(0.0, 0.0, 0.16)),
        axis=(0.0, 0.0, 1.0),
    )
    # Axis-to-geometry is ~0.08/0.09 on both sides (>> tol), yet the gate
    # accepts: the axis passes through both parts' AABB centers.
    assert _gate(model) == []


def test_phantom_pivot_fails_both_clauses() -> None:
    model = ArticulatedObject(name="phantom")
    base = model.part("base")
    base.visual(Box((0.1, 0.1, 0.1)), name="base_box")
    flap = model.part("flap")
    flap.visual(Box((0.1, 0.1, 0.1)), origin=Origin(xyz=(0.2, 0.0, 0.0)), name="flap_box")
    model.articulation(
        "phantom_hinge",
        ArticulationType.REVOLUTE,
        parent=base,
        child=flap,
        origin=Origin(xyz=(0.3, 0.3, 0.3)),
        axis=(0.0, 0.0, 1.0),
    )
    findings = _gate(model)
    assert [f.joint for f in findings] == ["phantom_hinge"]
    f = findings[0]
    assert f.metric == "axis"
    assert f.parent_distance > 0.015 and f.parent_center_distance > 0.015


def test_edge_hinged_door_passes_via_axis_clause() -> None:
    """Classic door: centroid is half a leaf from the axis (centerline clause
    fails) but the axis runs along the leaf edge (hardware clause passes)."""
    model = ArticulatedObject(name="door")
    frame = model.part("frame")
    frame.visual(Box((0.05, 0.05, 2.0)), origin=Origin(xyz=(0.0, 0.0, 1.0)), name="jamb")
    leaf = model.part("leaf")
    leaf.visual(Box((0.8, 0.04, 2.0)), origin=Origin(xyz=(0.4, 0.0, 1.0)), name="panel")
    model.articulation(
        "hinge",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=leaf,
        origin=Origin(xyz=(0.03, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
    )
    assert _gate(model) == []


def test_prismatic_is_exempt_even_when_far() -> None:
    model = ArticulatedObject(name="slide_far")
    rail = model.part("rail")
    rail.visual(Box((1.0, 0.06, 0.06)), name="rail_bar")
    slider = model.part("slider")
    slider.visual(Box((0.1, 0.05, 0.05)), origin=Origin(xyz=(0.3, 0.2, 0.2)), name="block")
    model.articulation(
        "slide",
        ArticulationType.PRISMATIC,
        parent=rail,
        child=slider,
        origin=Origin(xyz=(2.0, 2.0, 2.0)),
        axis=(1.0, 0.0, 0.0),
    )
    assert _gate(model) == []


def test_fixed_gets_no_relative_loosening_on_big_parts() -> None:
    """The retired bbox-relative tol used to forgive a weld 0.2 m off a 4 m
    part (effective tol would have been ~0.2+). Flat semantics fail it."""
    model = ArticulatedObject(name="big_weld")
    deck = model.part("deck")
    deck.visual(Box((4.0, 2.0, 0.05)), name="slab")
    leg = model.part("leg")
    leg.visual(Box((0.05, 0.05, 0.7)), origin=Origin(xyz=(0.0, 0.0, -0.35)), name="post")
    model.articulation(
        "weld",
        ArticulationType.FIXED,
        parent=deck,
        child=leg,
        origin=Origin(xyz=(0.0, 0.0, -0.2)),
        axis=(0.0, 0.0, 1.0),
    )
    findings = _gate(model)
    assert [f.joint for f in findings] == ["weld"]
    assert findings[0].metric == "point"
    # legacy bbox_relative argument is accepted but ignored
    assert [
        f.joint
        for f in find_joint_origin_distance_findings(
            model, bbox_relative=0.05, validate_model=False
        )
    ] == ["weld"]
