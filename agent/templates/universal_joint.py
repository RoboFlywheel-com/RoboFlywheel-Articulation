# SPDX-License-Identifier: Apache-2.0

"""Universal joint modular procedural template.

Two disjoint 5-star source families, selected by the ``joint_topology`` slot
(the ③ Primary Form Family slot):

- **single cross / cardan (Hooke)** — S2 ``universal_joint_002``
  (rec_picturex_0611__universal_joint__002…884db283) and its forks
  S3 pin_and_block, S4 forged-open yoke, S5 enclosed-block yoke, S6 splined shaft.
  Skeleton: ``spider`` root + ``shaft_yoke_a`` + ``shaft_yoke_b`` (parallel
  children), TWO orthogonal REVOLUTE journal joints.
- **double-cardan** — S1 ``compact_double_cardan``
  (rec_build-a-reference-accurate-compact-steel-double-…f7e21841) and its forks
  S7 enclosed-block end yoke, S8 flange end yoke, S9 centering ball, S10
  intermediate shaft. Skeleton: ``middle_section`` root + ``left/right_spider`` +
  ``left/right_section`` chain, FOUR REVOLUTE journal joints.

Compatibility gates (AUTHORING §A / spec §9): ``middle_member`` is sampled ONLY
for ``double_cardan``; ``shaft_connection`` ONLY for the single-cross family;
``yoke_form`` candidate sets are matched to the topology family — never
cross-composed.

Hard rules: decorations (retaining rings, cap dimples, bore liners, mouth edges,
centering ball/socket/stub) are ``parent.visual(...)`` on the moving part, not
FIXED joints (Rule 1). The spider↔yoke revolute journals are captured trunnions
(journal-in-cup, no axis-aligned face pair) → they omit ``MatingContract`` and are
grandfathered (Rule 2); capture is asserted with element-scoped ``allow_overlap``.
Cadquery fused/lathe forms from the sources are preserved, never downgraded to
plain Box/Cylinder (Rule 3). Journal/cup mating derives from shared quantities;
no sweep-tuned unsourced constants (Rule 4/geometry traceability).
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

JointTopology = Literal["single_cross", "pin_and_block", "double_cardan"]
PaletteStyle = Literal[
    "machined_bright", "satin_forged", "zinc_plated", "blackened_oxide", "raw_forged"
]

SINGLE_CROSS_FAMILY = ("single_cross", "pin_and_block")
# Single-cross yoke head is a MODULE-LOCAL FIXED structure (sc_sleeve_open only).
# Excluded (moved from the yoke_form slot to fixed): sc_enclosed_block and
# sc_forged_open both give bulky fork heads that interleave around the cross with
# ~zero articulation clearance under independent-revolute motion QC (they collide
# at any non-rest pose, even ±3°). Only the slim open box-arm fork (sc_sleeve_open)
# leaves room for the two orthogonal yokes to articulate without clashing. The
# forged-open and enclosed-block prototypes remain represented in the double-cardan
# family (dc_sleeve_open / dc_enclosed_block / dc_flange), whose end sections are
# far apart and never interleave. Single-cross discrete diversity is therefore
# carried by joint_topology (single_cross vs pin_and_block) × shaft_connection.
SC_YOKE_FORMS = ("sc_sleeve_open",)
DC_YOKE_FORMS = ("dc_sleeve_open", "dc_enclosed_block", "dc_flange")
# intermediate_shaft excluded: its two protruding forged end-yokes on the middle
# body sit close to the end sections and interfere with the swinging end section
# under motion QC by a roughly angle-independent ~19mm (a fixed geometric
# interference, not a widen-able travel graze). solid_hub and centering_ball both
# articulate cleanly, so middle_member keeps 2 source-backed candidates.
MIDDLE_MEMBERS = ("solid_hub", "centering_ball")
SHAFT_CONNECTIONS = ("plain_bore", "splined_shaft")

# Five realistic all-steel colorways drawn from the 5-star sources (S1/S2
# materials) plus safe companion finishes. Roles: body (shafts/forgings/blocks),
# bearing (spider/journals/cups), accent (polished edges/centering ball), dark
# (retaining rings/dimples/liners/stubs).
PALETTE_STYLES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "machined_bright": {
        "body": (0.72, 0.74, 0.77, 1.0),
        "bearing": (0.49, 0.51, 0.54, 1.0),
        "accent": (0.84, 0.85, 0.87, 1.0),
        "dark": (0.12, 0.13, 0.14, 1.0),
    },
    "satin_forged": {
        "body": (0.43, 0.45, 0.47, 1.0),
        "bearing": (0.30, 0.31, 0.33, 1.0),
        "accent": (0.62, 0.65, 0.68, 1.0),
        "dark": (0.16, 0.17, 0.18, 1.0),
    },
    "zinc_plated": {
        "body": (0.66, 0.69, 0.74, 1.0),
        "bearing": (0.55, 0.60, 0.66, 1.0),
        "accent": (0.82, 0.86, 0.91, 1.0),
        "dark": (0.28, 0.31, 0.36, 1.0),
    },
    "blackened_oxide": {
        "body": (0.17, 0.18, 0.20, 1.0),
        "bearing": (0.25, 0.26, 0.28, 1.0),
        "accent": (0.46, 0.48, 0.51, 1.0),
        "dark": (0.08, 0.08, 0.09, 1.0),
    },
    "raw_forged": {
        "body": (0.39, 0.38, 0.36, 1.0),
        "bearing": (0.48, 0.47, 0.45, 1.0),
        "accent": (0.61, 0.60, 0.58, 1.0),
        "dark": (0.14, 0.14, 0.13, 1.0),
    },
}

MAT_BODY = "uj_body"
MAT_BEARING = "uj_bearing"
MAT_ACCENT = "uj_accent"
MAT_DARK = "uj_dark"

# Cup/journal capture geometry (shared quantities, single-sourced). The needle
# cup seat sits at ±CUP_OFFSET on the bearing axis; the journal pin tip reaches
# JOURNAL_HALF·reach. Capture overlap = tip − CUP_OFFSET is held ≥6mm by the
# reach clamp in resolve_config.
SC_CUP_OFFSET = 0.0120
SC_JOURNAL_HALF = 0.021
# Extra room around the moving spider: keep the fork cheeks farther from the
# center while retaining overlap with the bearing bosses.
SC_FORK_CHEEK_INNER_BASE = 0.0155
SC_FORK_CHEEK_OUTER = 0.0215


# --------------------------------------------------------------------------- #
# Primitive helpers (verbatim from S1/S2 sources)
# --------------------------------------------------------------------------- #
def _cylinder(radius, length, start, direction):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*start), cq.Vector(*direction))


def _annulus(outer_radius, inner_radius, length, start, direction):
    return _cylinder(outer_radius, length, start, direction).cut(
        _cylinder(inner_radius, length, start, direction)
    )


def _centered_box(size, center):
    return cq.Workplane("XY").box(*size).translate(center).val()


def _fuse(*shapes):
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.fuse(shape)
    return result


def _safe_fillet(shape, selector, radius):
    try:
        return shape.edges(selector).fillet(radius)
    except Exception:
        return shape


def _bearing_cap(start, direction):
    """Closed-end needle-bearing cup with a proud machined flange (S2 L58-75)."""
    length = 0.0110
    wall = 0.0013
    flange_thickness = 0.0014
    outer = _cylinder(0.00745, length, start, direction)
    cavity = _cylinder(0.00525, length - wall, start, direction)
    flange_start = tuple(start[i] + direction[i] * (length - flange_thickness) for i in range(3))
    flange = _cylinder(0.00945, flange_thickness, flange_start, direction)
    return outer.fuse(flange).cut(cavity)


# --------------------------------------------------------------------------- #
# Single-cross family shapes (S2 + S3/S4/S5/S6)
# --------------------------------------------------------------------------- #
def _sc_hub_solid(topology: str):
    """Spider center: spherical forged hub (S2 L172) or chamfered pivot block
    (S3 L179-185). Both keep the same two orthogonal journals + interfaces."""
    if topology == "pin_and_block":
        return cq.Workplane("XY").box(0.0185, 0.0185, 0.0170).edges().chamfer(0.0018).val()
    return cq.Workplane("XY").sphere(0.0095).val()


def _sc_journal_x_solid(reach: float):
    return _fuse(
        _cylinder(0.00525, 0.042 * reach, (-SC_JOURNAL_HALF * reach, 0.0, 0.0), (1.0, 0.0, 0.0)),
        _cylinder(0.00655, 0.0200, (-0.010, 0.0, 0.0), (1.0, 0.0, 0.0)),
    )


def _sc_journal_y_solid(reach: float):
    return _fuse(
        _cylinder(0.00525, 0.042 * reach, (0.0, -SC_JOURNAL_HALF * reach, 0.0), (0.0, 1.0, 0.0)),
        _cylinder(0.00655, 0.0200, (0.0, -0.010, 0.0), (0.0, 1.0, 0.0)),
    )


# Canonical (yoke_a) → yoke_b axis map M(x,y,z) = (y, -z, -x): -X→+Z (shaft) and
# +Y→+X (bearing axis). Used only for the rotationally-symmetric decorations
# (cups/rings/dimples/liners), NOT the fork shells — the enclosed-block heads are
# authored natively per orientation (S5 deliberately shapes yoke_a and yoke_b
# blocks differently so they interleave around the cross without colliding).
def _orient(p, orient: str):
    if orient == "a":
        return p
    return (p[1], -p[2], -p[0])


def _sc_yoke_a_solid(yoke_form: str, shaft_form: str, motion_clearance: float):
    """Yoke A: shaft along -X, fork bearings on ±Y (S2/S4/S5/S6 yoke_a)."""
    transition = cq.Solid.makeCone(
        0.0200, 0.0160, 0.0170, cq.Vector(-0.045, 0.0, 0.0), cq.Vector(1.0, 0.0, 0.0)
    )
    collar = _cylinder(0.0215, 0.0070, (-0.034, 0.0, 0.0), (1.0, 0.0, 0.0))
    shaft_bore = None
    if shaft_form == "splined_shaft":
        root = _cylinder(0.0155, 0.0740, (-0.105, 0.0, 0.0), (1.0, 0.0, 0.0))
        teeth = [
            _centered_box((0.0570, 0.0042, 0.0062), (-0.0765, 0.0, 0.0167)).rotate(
                cq.Vector(-0.0765, 0.0, 0.0), cq.Vector(-0.0755, 0.0, 0.0), i * 30.0
            )
            for i in range(12)
        ]
        shaft = [_fuse(root, *teeth), _cylinder(0.0157, 0.0032, (-0.105, 0.0, 0.0), (1.0, 0.0, 0.0))]
    else:
        shaft = [
            _annulus(0.0200, 0.0130, 0.0740, (-0.105, 0.0, 0.0), (1.0, 0.0, 0.0)),
            _annulus(0.0215, 0.0128, 0.0032, (-0.105, 0.0, 0.0), (1.0, 0.0, 0.0)),
        ]
        shaft_bore = _cylinder(0.0130, 0.0940, (-0.106, 0.0, 0.0), (1.0, 0.0, 0.0))

    bosses = [
        _cylinder(0.0120, 0.0100, (0.0, 0.0125, 0.0), (0.0, 1.0, 0.0)),
        _cylinder(0.0120, 0.0100, (0.0, -0.0225, 0.0), (0.0, 1.0, 0.0)),
    ]
    fork_inner = SC_FORK_CHEEK_INNER_BASE + motion_clearance
    fork_center = 0.5 * (fork_inner + SC_FORK_CHEEK_OUTER)
    fork_width = SC_FORK_CHEEK_OUTER - fork_inner
    if yoke_form == "sc_forged_open":
        head = [
            cq.Workplane("YZ", origin=(-0.045, y, 0.0))
            .rect(0.0105, 0.0225).workplane(offset=0.028)
            .rect(0.0092, 0.0175).workplane(offset=0.017)
            .rect(0.0086, 0.0150).loft(combine=True).val()
            for y in (-0.0155, 0.0155)
        ] + bosses
    elif yoke_form == "sc_enclosed_block":
        block = _centered_box((0.049, 0.0450, 0.0220), (-0.0125, 0.0, 0.0))
        block = block.cut(_centered_box((0.039, 0.0290, 0.0280), (-0.0095, 0.0, 0.0)))
        block = block.cut(_cylinder(0.0082, 0.0550, (-0.040, 0.0, 0.0), (1.0, 0.0, 0.0)))
        head = [block] + bosses
    else:  # sc_sleeve_open
        head = [
            _centered_box((0.036, fork_width, 0.0180), (-0.017, y, 0.0))
            for y in (-fork_center, fork_center)
        ]
        head += bosses

    shape = _fuse(*shaft, transition, collar, *head)
    shape = shape.cut(_cylinder(0.00770, 0.0500, (0.0, -0.025, 0.0), (0.0, 1.0, 0.0)))
    if shaft_bore is not None:
        shape = shape.cut(shaft_bore)
    return shape


def _sc_yoke_b_solid(yoke_form: str, shaft_form: str, motion_clearance: float):
    """Yoke B: shaft along +Z, fork bearings on ±X (S2/S4/S5/S6 yoke_b).
    Authored natively (not a rotation of yoke A) so the enclosed-block head keeps
    the S5 interleave proportions."""
    transition = cq.Solid.makeCone(
        0.0160, 0.0200, 0.0180, cq.Vector(0.0, 0.0, 0.020), cq.Vector(0.0, 0.0, 1.0)
    )
    collar = _cylinder(0.0215, 0.0070, (0.0, 0.0, 0.018), (0.0, 0.0, 1.0))
    shaft_bore = None
    if shaft_form == "splined_shaft":
        root = _cylinder(0.0155, 0.0740, (0.0, 0.0, 0.031), (0.0, 0.0, 1.0))
        teeth = [
            _centered_box((0.0062, 0.0042, 0.0570), (0.0167, 0.0, 0.0765)).rotate(
                cq.Vector(0.0, 0.0, 0.0765), cq.Vector(0.0, 0.0, 0.0775), i * 30.0
            )
            for i in range(12)
        ]
        shaft = [_fuse(root, *teeth), _cylinder(0.0157, 0.0032, (0.0, 0.0, 0.1018), (0.0, 0.0, 1.0))]
    else:
        shaft = [
            _annulus(0.0200, 0.0130, 0.0740, (0.0, 0.0, 0.031), (0.0, 0.0, 1.0)),
            _annulus(0.0215, 0.0128, 0.0032, (0.0, 0.0, 0.1018), (0.0, 0.0, 1.0)),
        ]
        shaft_bore = _cylinder(0.0130, 0.0940, (0.0, 0.0, 0.015), (0.0, 0.0, 1.0))

    bosses = [
        _cylinder(0.0120, 0.0100, (0.0125, 0.0, 0.0), (1.0, 0.0, 0.0)),
        _cylinder(0.0120, 0.0100, (-0.0225, 0.0, 0.0), (1.0, 0.0, 0.0)),
    ]
    fork_inner = SC_FORK_CHEEK_INNER_BASE + motion_clearance
    fork_center = 0.5 * (fork_inner + SC_FORK_CHEEK_OUTER)
    fork_width = SC_FORK_CHEEK_OUTER - fork_inner
    if yoke_form == "sc_forged_open":
        head = [
            cq.Workplane("XY", origin=(x, 0.0, 0.0))
            .rect(0.0086, 0.0150).workplane(offset=0.017)
            .rect(0.0092, 0.0175).workplane(offset=0.028)
            .rect(0.0105, 0.0225).loft(combine=True).val()
            for x in (-0.0155, 0.0155)
        ] + bosses
    elif yoke_form == "sc_enclosed_block":
        block = _centered_box((0.0450, 0.0240, 0.0560), (0.0, 0.0, 0.0120))
        block = block.cut(_centered_box((0.0290, 0.0300, 0.0470), (0.0, 0.0, 0.0110)))
        head = [block] + bosses
    else:  # sc_sleeve_open
        head = [
            _centered_box((fork_width, 0.0180, 0.036), (x, 0.0, 0.017))
            for x in (-fork_center, fork_center)
        ]
        head += bosses

    shape = _fuse(*shaft, transition, collar, *head)
    shape = shape.cut(_cylinder(0.00770, 0.0500, (-0.025, 0.0, 0.0), (1.0, 0.0, 0.0)))
    if shaft_bore is not None:
        shape = shape.cut(shaft_bore)
    return shape


# --------------------------------------------------------------------------- #
# Double-cardan family shapes (S1 + S7/S8/S9/S10)
# --------------------------------------------------------------------------- #
def _dc_bearing_cup_solid():
    """Stepped hollow pressed cup, open toward the journal (S1 L31-54)."""
    barrel = cq.Workplane("XY", origin=(0.0, 0.0, 0.0100)).circle(0.00515).extrude(0.0092)
    flange = cq.Workplane("XY", origin=(0.0, 0.0, 0.0176)).circle(0.00625).extrude(0.0016)
    cup = barrel.union(flange)
    inner = cq.Workplane("XY", origin=(0.0, 0.0, 0.0098)).circle(0.00355).extrude(0.0083)
    dimple = cq.Workplane("XY", origin=(0.0, 0.0, 0.01875)).circle(0.00135).extrude(0.0007)
    return cup.cut(inner).cut(dimple)


def _dc_spider_core_solid():
    center = cq.Workplane("XY").sphere(0.0054)
    z_shoulder = cq.Workplane("XY").circle(0.00445).extrude(0.0096, both=True)
    y_shoulder = cq.Workplane("XZ").circle(0.00445).extrude(0.0096, both=True)
    return center.union(z_shoulder).union(y_shoulder)


def _dc_journal_solid():
    collar = cq.Workplane("XY", origin=(0.0, 0.0, 0.0078)).circle(0.00430).extrude(0.0016)
    pin = cq.Workplane("XY", origin=(0.0, 0.0, 0.0085)).circle(0.00355).extrude(0.0088)
    return collar.union(pin)


def _dc_cheeks_solid():
    """Common open forged cheek pair + journal pin bore (S1 L101-122)."""
    boss = cq.Workplane("XY").circle(0.0095).extrude(0.0040, both=True)
    arm_profile = (
        cq.Workplane("XY")
        .polyline(
            [
                (-0.0030, -0.0087),
                (0.0240, -0.0112),
                (0.0340, -0.0094),
                (0.0340, 0.0094),
                (0.0240, 0.0112),
                (-0.0030, 0.0087),
            ]
        )
        .close()
        .extrude(0.0040, both=True)
    )
    cheek = _safe_fillet(boss.union(arm_profile), "|Z", 0.0014)
    cheeks = cheek.translate((0.0, 0.0, 0.0140)).union(
        cheek.translate((0.0, 0.0, -0.0140))
    )
    pin_bore = cq.Workplane("XY").circle(0.00510).extrude(0.050, both=True)
    return cheeks.cut(pin_bore)


def _dc_end_section_solid(sign: int, yoke_form: str):
    """End coupling section = forged cheeks + a driveline backing that varies by
    yoke_form: hollow sleeve (S1), monobloc block (S7), or 4-bolt flange (S8)."""
    cheeks = _dc_cheeks_solid()

    if yoke_form == "dc_flange":
        neck = cq.Workplane("YZ", origin=(0.0250, 0.0, 0.0)).circle(0.0145).extrude(0.0180)
        flange = cq.Workplane("YZ", origin=(0.0400, 0.0, 0.0)).circle(0.0225).extrude(0.0080)
        flange = _safe_fillet(flange, "|X", 0.0012)
        for index in range(4):
            angle = math.radians(45.0 + 90.0 * index)
            y = 0.0158 * math.cos(angle)
            z = 0.0158 * math.sin(angle)
            hole = cq.Workplane("YZ", origin=(0.0385, y, z)).circle(0.00305).extrude(0.0110)
            flange = flange.cut(hole)
        yoke = neck.union(flange).union(cheeks)
        if sign < 0:
            yoke = yoke.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 180.0)
        return yoke

    outer = cq.Workplane("YZ", origin=(0.020, 0.0, 0.0)).circle(0.0190).extrude(0.0360)
    bore = cq.Workplane("YZ", origin=(0.0195, 0.0, 0.0)).circle(0.0118).extrude(0.0370)
    sleeve = outer.cut(bore)
    mouth_ring = (
        cq.Workplane("YZ", origin=(0.0520, 0.0, 0.0)).circle(0.0196).circle(0.0118).extrude(0.0040)
    )
    sleeve = sleeve.union(mouth_ring)

    if yoke_form == "dc_enclosed_block":
        block = cq.Workplane("XY").box(0.0440, 0.0300, 0.0400).translate((0.0160, 0.0, 0.0))
        spider_window = cq.Workplane("XY").box(0.0280, 0.0340, 0.0210).translate((0.0030, 0.0, 0.0))
        block = block.cut(spider_window)
        bearing_bore = cq.Workplane("XY").circle(0.00510).extrude(0.050, both=True)
        upper_cb = cq.Workplane("XY", origin=(0.0, 0.0, 0.0164)).circle(0.00615).extrude(0.0042)
        lower_cb = cq.Workplane("XY", origin=(0.0, 0.0, -0.0164)).circle(0.00615).extrude(-0.0042)
        block = block.cut(bearing_bore).cut(upper_cb).cut(lower_cb)
        block = _safe_fillet(block, "|Z", 0.0012)
        yoke = sleeve.union(block).cut(bore)
    else:  # dc_sleeve_open (S1 default)
        yoke = sleeve.union(cheeks)

    if sign < 0:
        yoke = yoke.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 180.0)
    return yoke


def _dc_middle_solid(middle_member: str, half_spacing: float):
    """Middle coupling body. solid_hub (S1), centering_ball saddles (S9), or
    turned intermediate shaft with two forked yokes (S10)."""
    left_boss = (
        cq.Workplane("XZ").center(-half_spacing, 0.0).circle(0.0098).extrude(0.0040, both=True)
    )
    right_boss = (
        cq.Workplane("XZ").center(half_spacing, 0.0).circle(0.0098).extrude(0.0040, both=True)
    )
    neck = cq.Workplane("XZ").rect(2.0 * half_spacing, 0.0088).extrude(0.0040, both=True)

    cheek = left_boss.union(right_boss).union(neck)
    cheek = _safe_fillet(cheek, "|Y", 0.0018)
    cheeks = cheek.translate((0.0, 0.0140, 0.0)).union(
        cheek.translate((0.0, -0.0140, 0.0))
    )

    if middle_member == "centering_ball":
        left_saddle = (
            cq.Workplane("XZ", origin=(-0.0160, 0.0, 0.0)).circle(0.0035).extrude(0.0115, both=True)
        )
        right_saddle = (
            cq.Workplane("XZ", origin=(0.0160, 0.0, 0.0)).circle(0.0034).extrude(0.0115, both=True)
        )
        forging = cheeks.union(left_saddle).union(right_saddle)
    else:  # solid_hub (S1 default)
        hub = cq.Workplane("XZ", origin=(0.0, 0.0, 0.0)).circle(0.0096).extrude(0.0150, both=True)
        hub = _safe_fillet(hub, "|Y", 0.0030)
        forging = _safe_fillet(cheeks.union(hub), "|Y", 0.0008)

    for x in (-half_spacing, half_spacing):
        journal_bore = (
            cq.Workplane("XZ", origin=(x, 0.0, 0.0)).circle(0.00510).extrude(0.060, both=True)
        )
        forging = forging.cut(journal_bore)
    return forging


def _dc_centering_socket_solid():
    outer = cq.Workplane("XY").sphere(0.0103)
    cavity = cq.Workplane("XY").sphere(0.0068)
    socket = outer.cut(cavity)
    front_relief = cq.Workplane("YZ", origin=(0.0020, 0.0, 0.0)).rect(0.030, 0.030).extrude(0.020)
    return socket.cut(front_relief)


def _dc_centering_ball_solid():
    return cq.Workplane("XY").sphere(0.0062)


def _dc_centering_ball_stub_solid():
    stud = cq.Workplane("YZ", origin=(0.0054, 0.0, 0.0)).circle(0.0032).extrude(0.0106)
    saddle = cq.Workplane("XZ", origin=(0.0160, 0.0, 0.0)).circle(0.0033).extrude(0.0115, both=True)
    return stud.union(saddle)


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class UniversalJointConfig:
    joint_topology: JointTopology = "single_cross"
    yoke_form: str = "sc_sleeve_open"
    middle_member: str = "n/a"
    shaft_connection: str = "plain_bore"
    palette_style: PaletteStyle = "machined_bright"
    sc_journal_reach_scale: float = 1.0
    sc_motion_clearance: float = 0.004
    sc_articulation_limit: float = 0.15
    dc_articulation_limit: float = 0.279
    dc_joint_half_spacing: float = 0.025


@dataclass(frozen=True)
class ResolvedUniversalJointConfig:
    joint_topology: str
    yoke_form: str
    middle_member: str
    shaft_connection: str
    palette_style: str
    palette: dict[str, tuple[float, float, float, float]]
    sc_journal_reach_scale: float
    sc_motion_clearance: float
    sc_articulation_limit: float
    dc_articulation_limit: float
    dc_joint_half_spacing: float


def config_from_seed(seed: int) -> UniversalJointConfig:
    rng = random.Random(seed)
    joint_topology = rng.choice(("single_cross", "pin_and_block", "double_cardan"))
    palette_style = rng.choice(tuple(PALETTE_STYLES.keys()))

    if joint_topology == "double_cardan":
        yoke_form = rng.choice(DC_YOKE_FORMS)
        middle_member = rng.choice(MIDDLE_MEMBERS)
        shaft_connection = "n/a"
    else:
        yoke_form = "sc_sleeve_open"  # module-local fixed (see SC_YOKE_FORMS note)
        middle_member = "n/a"
        shaft_connection = rng.choice(SHAFT_CONNECTIONS)

    return UniversalJointConfig(
        joint_topology=joint_topology,
        yoke_form=yoke_form,
        middle_member=middle_member,
        shaft_connection=shaft_connection,
        palette_style=palette_style,
        sc_journal_reach_scale=round(rng.uniform(0.92, 1.06), 4),
        sc_motion_clearance=round(rng.uniform(0.0015, 0.0025), 4),
        sc_articulation_limit=round(rng.uniform(0.12, 0.16), 4),
        dc_articulation_limit=round(rng.uniform(0.18, 0.30), 4),
        dc_joint_half_spacing=round(rng.uniform(0.025, 0.028), 5),
    )


def resolve_config(config: UniversalJointConfig) -> ResolvedUniversalJointConfig:
    topology = str(config.joint_topology)
    if topology not in ("single_cross", "pin_and_block", "double_cardan"):
        raise ValueError(f"Unsupported joint_topology: {topology}")
    if str(config.palette_style) not in PALETTE_STYLES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    # Compatibility gates (never sample an illegal combo).
    if topology == "double_cardan":
        yoke_form = config.yoke_form if config.yoke_form in DC_YOKE_FORMS else "dc_sleeve_open"
        middle_member = (
            config.middle_member if config.middle_member in MIDDLE_MEMBERS else "solid_hub"
        )
        shaft_connection = "n/a"
    else:
        yoke_form = config.yoke_form if config.yoke_form in SC_YOKE_FORMS else "sc_sleeve_open"
        middle_member = "n/a"
        shaft_connection = (
            config.shaft_connection if config.shaft_connection in SHAFT_CONNECTIONS else "plain_bore"
        )

    # Reach clamp keeps journal tip inside the cup seat with ≥6mm capture and
    # <SC_CUP_OFFSET+cup_depth escape margin (single-sourced from SC_* consts).
    reach = max(0.90, min(float(config.sc_journal_reach_scale), 1.08))
    motion_clearance = max(0.0, min(float(config.sc_motion_clearance), 0.003))
    sc_limit = max(0.12, min(float(config.sc_articulation_limit), 0.16))
    dc_limit = max(0.18, min(float(config.dc_articulation_limit), 0.30))
    half_spacing = max(0.025, min(float(config.dc_joint_half_spacing), 0.028))

    return ResolvedUniversalJointConfig(
        joint_topology=topology,
        yoke_form=yoke_form,
        middle_member=middle_member,
        shaft_connection=shaft_connection,
        palette_style=str(config.palette_style),
        palette=dict(PALETTE_STYLES[str(config.palette_style)]),
        sc_journal_reach_scale=reach,
        sc_motion_clearance=motion_clearance,
        sc_articulation_limit=sc_limit,
        dc_articulation_limit=dc_limit,
        dc_joint_half_spacing=half_spacing,
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("joint_topology", r.joint_topology),
        ("yoke_form", r.yoke_form),
        ("middle_member", r.middle_member),
        ("shaft_connection", r.shaft_connection),
        ("palette_style", r.palette_style),
    ]


# --------------------------------------------------------------------------- #
# Builders
# --------------------------------------------------------------------------- #
def _mesh(solid, name):
    return mesh_from_cadquery(solid, name, tolerance=0.00025, angular_tolerance=0.08)


def _build_single_cross(model: ArticulatedObject, r: ResolvedUniversalJointConfig) -> None:
    reach = r.sc_journal_reach_scale

    spider = model.part("spider")
    spider.visual(_mesh(_sc_hub_solid(r.joint_topology), "uj_sc_hub"), material=MAT_BEARING,
                  name="spider_center", material_class_id="metal.stainless_matte")
    spider.visual(_mesh(_sc_journal_x_solid(reach), "uj_sc_journal_x"), material=MAT_BEARING,
                  name="journal_x", material_class_id="metal.stainless_matte")
    spider.visual(_mesh(_sc_journal_y_solid(reach), "uj_sc_journal_y"), material=MAT_BEARING,
                  name="journal_y", material_class_id="metal.stainless_matte")

    for orient, part_name in (("a", "shaft_yoke_a"), ("b", "shaft_yoke_b")):
        part = model.part(part_name)
        if orient == "a":
            shell = _sc_yoke_a_solid(r.yoke_form, r.shaft_connection, r.sc_motion_clearance)
        else:
            shell = _sc_yoke_b_solid(r.yoke_form, r.shaft_connection, r.sc_motion_clearance)
        part.visual(_mesh(shell, f"uj_sc_shell_{orient}"), material=MAT_BODY, name="shaft_yoke", material_class_id="metal.steel_bare")

        for sense, off in (("pos", SC_CUP_OFFSET), ("neg", -SC_CUP_OFFSET)):
            d = (0.0, 1.0 if sense == "pos" else -1.0, 0.0)
            cap = _bearing_cap(_orient((0.0, off, 0.0), orient), _orient(d, orient))
            part.visual(_mesh(cap, f"uj_sc_cap_{orient}_{sense}"), material=MAT_BEARING,
                        name=f"cap_{sense}", material_class_id="metal.stainless_matte")
            ring = _annulus(0.0108, 0.0093, 0.0008,
                            _orient((0.0, off + 0.01035 * (1 if sense == "pos" else -1), 0.0),
                                    orient), _orient(d, orient))
            part.visual(_mesh(ring, f"uj_sc_ring_{orient}_{sense}"), material=MAT_DARK,
                        name=f"retaining_ring_{sense}", material_class_id="metal.blackened_gunmetal")
            dim = _cylinder(0.0023, 0.00045,
                            _orient((0.0, off + 0.01095 * (1 if sense == "pos" else -1), 0.0),
                                    orient), _orient(d, orient))
            part.visual(_mesh(dim, f"uj_sc_dimple_{orient}_{sense}"), material=MAT_DARK,
                        name=f"cap_dimple_{sense}", material_class_id="metal.blackened_gunmetal")

        if r.shaft_connection == "plain_bore":
            liner = _annulus(0.01305, 0.0117, 0.0040, _orient((-0.1045, 0.0, 0.0), orient),
                             _orient((1.0, 0.0, 0.0), orient))
            part.visual(_mesh(liner, f"uj_sc_liner_{orient}"), material=MAT_DARK, name="bore_liner", material_class_id="metal.blackened_gunmetal")
            mouth = _annulus(0.02165, 0.0199, 0.0007, _orient((-0.1052, 0.0, 0.0), orient),
                             _orient((1.0, 0.0, 0.0), orient))
            part.visual(_mesh(mouth, f"uj_sc_mouth_{orient}"), material=MAT_ACCENT,
                        name="mouth_edge", material_class_id="metal.chrome_polished")

    limits = MotionLimits(effort=120.0, velocity=5.0, lower=-r.sc_articulation_limit,
                          upper=r.sc_articulation_limit)
    model.articulation("spider_to_yoke_a", ArticulationType.REVOLUTE,
                       parent=model.get_part("spider"), child=model.get_part("shaft_yoke_a"),
                       origin=Origin(), axis=(0.0, 1.0, 0.0), motion_limits=limits)
    model.articulation("spider_to_yoke_b", ArticulationType.REVOLUTE,
                       parent=model.get_part("spider"), child=model.get_part("shaft_yoke_b"),
                       origin=Origin(), axis=(1.0, 0.0, 0.0), motion_limits=limits)


def _add_dc_spider_visuals(part, core_mesh, journal_mesh):
    part.visual(core_mesh, material=MAT_BEARING, name="spider_core", material_class_id="metal.stainless_matte")
    part.visual(journal_mesh, material=MAT_BEARING, name="journal_pos_z", material_class_id="metal.stainless_matte")
    part.visual(journal_mesh, origin=Origin(rpy=(math.pi, 0.0, 0.0)), material=MAT_BEARING,
                name="journal_neg_z", material_class_id="metal.stainless_matte")
    part.visual(journal_mesh, origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)), material=MAT_BEARING,
                name="journal_pos_y", material_class_id="metal.stainless_matte")
    part.visual(journal_mesh, origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)), material=MAT_BEARING,
                name="journal_neg_y", material_class_id="metal.stainless_matte")


def _build_double_cardan(model: ArticulatedObject, r: ResolvedUniversalJointConfig) -> None:
    hs = r.dc_joint_half_spacing
    rest_pitch = math.radians(8.0)
    rest_yaw = math.radians(10.0)

    cup_mesh = _mesh(_dc_bearing_cup_solid(), "uj_dc_cup")
    core_mesh = _mesh(_dc_spider_core_solid(), "uj_dc_spider_core")
    journal_mesh = _mesh(_dc_journal_solid(), "uj_dc_journal")

    middle = model.part("middle_section")
    middle.visual(_mesh(_dc_middle_solid(r.middle_member, hs), "uj_dc_middle"),
                  material=MAT_BODY, name="double_yoke_forging", material_class_id="metal.steel_bare")
    if r.middle_member == "centering_ball":
        middle.visual(_mesh(_dc_centering_socket_solid(), "uj_dc_socket"), material=MAT_BODY,
                      name="centering_socket", material_class_id="metal.steel_bare")
        middle.visual(_mesh(_dc_centering_ball_solid(), "uj_dc_ball"), material=MAT_ACCENT,
                      name="centering_ball", material_class_id="metal.chrome_polished")
        middle.visual(_mesh(_dc_centering_ball_stub_solid(), "uj_dc_stub"), material=MAT_DARK,
                      name="centering_ball_stub", material_class_id="metal.blackened_gunmetal")
    for side, x in (("left", -hs), ("right", hs)):
        middle.visual(cup_mesh, origin=Origin(xyz=(x, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
                      material=MAT_BEARING, name=f"{side}_cap_pos_y", material_class_id="metal.stainless_matte")
        middle.visual(cup_mesh, origin=Origin(xyz=(x, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                      material=MAT_BEARING, name=f"{side}_cap_neg_y", material_class_id="metal.stainless_matte")

    for side in ("left", "right"):
        spider = model.part(f"{side}_spider")
        _add_dc_spider_visuals(spider, core_mesh, journal_mesh)

    for side, sign in (("left", -1), ("right", 1)):
        section = model.part(f"{side}_section")
        section.visual(_mesh(_dc_end_section_solid(sign, r.yoke_form), f"uj_dc_end_{side}"),
                       material=MAT_BODY, name="sleeve_yoke_body", material_class_id="metal.steel_bare")
        section.visual(cup_mesh, material=MAT_BEARING, name=f"{side}_cap_pos_z", material_class_id="metal.stainless_matte")
        section.visual(cup_mesh, origin=Origin(rpy=(math.pi, 0.0, 0.0)), material=MAT_BEARING,
                       name=f"{side}_cap_neg_z", material_class_id="metal.stainless_matte")

    limits = MotionLimits(effort=12.0, velocity=2.2, lower=-r.dc_articulation_limit,
                          upper=r.dc_articulation_limit)
    for side, x in (("left", -hs), ("right", hs)):
        model.articulation(f"{side}_primary_axis", ArticulationType.REVOLUTE,
                           parent=model.get_part("middle_section"),
                           child=model.get_part(f"{side}_spider"),
                           origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, rest_pitch, 0.0)),
                           axis=(0.0, 1.0, 0.0), motion_limits=limits)
        model.articulation(f"{side}_secondary_axis", ArticulationType.REVOLUTE,
                           parent=model.get_part(f"{side}_spider"),
                           child=model.get_part(f"{side}_section"),
                           origin=Origin(rpy=(0.0, 0.0, rest_yaw)),
                           axis=(0.0, 0.0, 1.0), motion_limits=limits)


def build_universal_joint(
    config: UniversalJointConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    assets = assets or AssetContext(Path(tempfile.mkdtemp(prefix="articraft-universal-joint-")))
    model = ArticulatedObject(name="universal_joint", assets=assets)
    for role in (MAT_BODY, MAT_BEARING, MAT_ACCENT, MAT_DARK):
        model.material(role, rgba=r.palette[role.removeprefix("uj_")])

    if r.joint_topology == "double_cardan":
        _build_double_cardan(model, r)
    else:
        _build_single_cross(model, r)
    return model


def build_seeded_universal_joint(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_universal_joint(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def _allow_sc_capture(ctx, spider, yoke_a, yoke_b):
    for cap in ("cap_pos", "cap_neg"):
        ctx.allow_overlap(spider, yoke_a, elem_a="journal_y", elem_b=cap,
                          reason="Y journal captured in yoke A needle cup.")
        ctx.allow_overlap(spider, yoke_b, elem_a="journal_x", elem_b=cap,
                          reason="X journal captured in yoke B needle cup.")


def _allow_dc_capture(ctx, model):
    middle = model.get_part("middle_section")
    for side in ("left", "right"):
        spider = model.get_part(f"{side}_spider")
        end = model.get_part(f"{side}_section")
        for sense in ("pos", "neg"):
            ctx.allow_overlap(spider, middle, elem_a=f"journal_{sense}_y",
                              elem_b=f"{side}_cap_{sense}_y",
                              reason="Spider Y journal captured in middle bearing cup.")
            ctx.allow_overlap(spider, end, elem_a=f"journal_{sense}_z",
                              elem_b=f"{side}_cap_{sense}_z",
                              reason="Spider Z journal captured in end bearing cup.")


def run_universal_joint_tests(
    model: ArticulatedObject, config: UniversalJointConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    # Declare captured-trunnion allowances FIRST so every subsequent overlap
    # gate (closed pose + sampled poses + carried-over baseline) honors them.
    if r.joint_topology == "double_cardan":
        _allow_dc_capture(ctx, model)
    else:
        _allow_sc_capture(ctx, model.get_part("spider"),
                          model.get_part("shaft_yoke_a"), model.get_part("shaft_yoke_b"))

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    revolutes = [
        j for j in model.articulations if j.articulation_type == ArticulationType.REVOLUTE
    ]

    if r.joint_topology == "double_cardan":
        ctx.check("double_cardan has four revolute journal joints",
                  len(model.articulations) == 4 and len(revolutes) == 4,
                  details=f"joints={[j.name for j in model.articulations]}")
        primary = model.get_articulation("left_primary_axis")
        secondary = model.get_articulation("left_secondary_axis")
        ctx.check("left group axes orthogonal",
                  abs(sum(a * b for a, b in zip(primary.axis, secondary.axis))) < 1e-9,
                  details=f"{primary.axis},{secondary.axis}")
        end = model.get_part("left_section")
        rest = ctx.part_world_aabb(end)
        with ctx.pose({primary: r.dc_articulation_limit, secondary: -r.dc_articulation_limit}):
            moved = ctx.part_world_aabb(end)
        if rest is not None and moved is not None:
            rc = tuple((rest[0][i] + rest[1][i]) * 0.5 for i in range(3))
            mc = tuple((moved[0][i] + moved[1][i]) * 0.5 for i in range(3))
            ctx.check("compound cardan pose moves the left end section",
                      math.dist(rc, mc) > 0.004, details=f"rest={rc}, moved={mc}")
    else:
        spider = model.get_part("spider")
        yoke_a = model.get_part("shaft_yoke_a")
        yoke_b = model.get_part("shaft_yoke_b")
        joint_a = model.get_articulation("spider_to_yoke_a")
        joint_b = model.get_articulation("spider_to_yoke_b")
        ctx.check("single cross has two revolute journal joints",
                  len(model.articulations) == 2 and len(revolutes) == 2,
                  details=f"joints={[j.name for j in model.articulations]}")
        ctx.check("spider bearing axes orthogonal",
                  abs(sum(a * b for a, b in zip(joint_a.axis, joint_b.axis))) < 1e-9,
                  details=f"{joint_a.axis},{joint_b.axis}")
        rest = ctx.part_element_world_aabb(yoke_a, elem="shaft_yoke")
        with ctx.pose({joint_a: r.sc_articulation_limit}):
            moved = ctx.part_element_world_aabb(yoke_a, elem="shaft_yoke")
            ctx.expect_overlap(spider, yoke_a, axes="y", elem_a="journal_y", elem_b="cap_pos",
                               min_overlap=0.006, name="yoke A stays captured while articulated")
        if rest is not None and moved is not None:
            rz = (rest[0][2] + rest[1][2]) * 0.5
            mz = (moved[0][2] + moved[1][2]) * 0.5
            ctx.check("yoke A rotates about Y", abs(mz - rz) > 0.004,
                      details=f"rest_z={rz}, moved_z={mz}")

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=96, ignore_fixed=True)
    return ctx.report()


__all__ = [
    "UniversalJointConfig",
    "ResolvedUniversalJointConfig",
    "build_universal_joint",
    "build_seeded_universal_joint",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_universal_joint_tests",
]
