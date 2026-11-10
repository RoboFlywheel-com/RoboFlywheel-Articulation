# SPDX-License-Identifier: Apache-2.0

"""Surgical / exam chair procedural template (modular).

Spec: articraft_template_authoring/specs_modular_v1/Science_Surgical_Chair_Chair.md

Seated surgical / gynecological exam stool: a round upholstered seat on a
pneumatic (gas-pillar) lift column, two wing armrests that swing out, a curved
backrest, and a support base. Identity = **gas-lift PRISMATIC + wing-armrest
REVOLUTE** spine.

Fixed motion spine (kept on every seed — so even the B=fixed_stalk backrest
combination still has >=1 non-FIXED joint):
  * seat_lift       PRISMATIC +Z  — the seat raises/lowers on the gas pillar
  * left_arm_swing  REVOLUTE  +Z  — left wing armrest swings out on its post
  * right_arm_swing REVOLUTE  +Z  — right wing armrest swings out on its post
Armrest count is FIXED at 2 (real exam chairs always have two wings); it is NOT
a multiplicity axis.

Two structural slots (pattern = mixed: 2 parallel structure slots + 1
conditional multiplicity axis):
  * Slot A `base`               : five_star_caster / cross_caster /
                                  fixed_pedestal / four_leg_frame
  * Slot B `backrest_mechanism` : fixed_stalk / reclining_backrest /
                                  split_headrest_tilt / footrest_legrest

Conditional multiplicity axis:
  * `caster_count` (N in {3,4,5}): the number of twin-wheel casters on the
    star base. Exposed ONLY on five_star_caster (cross_caster is fixed at 4;
    pedestal / four-leg bases have no casters). The casters are FIXED
    decorative wheels fused as `base.visual(...)` (Rule 1 — no FIXED joints),
    mirroring the 5-star source record. Encoded into the slot_choice tuple as
    ("caster_count", f"c{N}") on five_star_caster only.

Module sources (5-star surgical_chair records, adapted verbatim — every
cadquery `mesh_from_cadquery` profile is preserved, no Box/Cylinder downgrade):
  S1 parent  five_star_caster + fixed_stalk
  S2 var_pedestal    fixed_pedestal base
  S3 var_fourleg     four_leg_frame base
  S4 var_xcaster     cross_caster base
  S5 var_caster3     caster_count N=3
  S6 var_recline     reclining_backrest (seat_to_backrest REVOLUTE -Y)
  S7 var_headrest    split_headrest_tilt (headrest_tilt REVOLUTE +Y)
  S8 var_legrest     footrest_legrest (legrest_hinge REVOLUTE -Y)

Rules:
  Rule 1 — decorative bits (casters, pedals, hub cone, bellows, backrest stalk,
    bracket, lever/knob) are `parent.visual(...)`, never FIXED-jointed parts.
  Rule 2 — every separate moving child part has real captured contact, declared
    with element-scoped allow_overlap mirroring the source record run_tests.
  Rule 3 — structure derives from the declared per-module 5-star sources; the
    cadquery profiles are adapted, not downgraded.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

BaseSupport = Literal["five_star_caster", "cross_caster", "fixed_pedestal", "four_leg_frame"]
BackrestMechanism = Literal[
    "fixed_stalk", "reclining_backrest", "split_headrest_tilt", "footrest_legrest"
]
PaletteStyle = Literal[
    "blue_vinyl_chrome", "black_leather_chrome", "white_clinical", "teal_clinical"
]

BASE_SUPPORTS: tuple[BaseSupport, ...] = (
    "five_star_caster",
    "cross_caster",
    "fixed_pedestal",
    "four_leg_frame",
)
BACKREST_MECHANISMS: tuple[BackrestMechanism, ...] = (
    "fixed_stalk",
    "reclining_backrest",
    "split_headrest_tilt",
    "footrest_legrest",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "blue_vinyl_chrome",
    "black_leather_chrome",
    "white_clinical",
    "teal_clinical",
)

# Caster multiplicity (five_star_caster only). Parent record uses N=5.
N_MIN = 3
N_MAX = 5
CASTER_COUNTS: tuple[int, ...] = (3, 4, 5)
CASTER_COUNT_WEIGHTS = (0.20, 0.30, 0.50)  # 5 most common (parent), 3 the tail

# Bases that carry casters (expose the caster_count axis context). cross_caster
# is fixed at 4 wheels (its own arm count); only five_star exposes the axis.
CASTER_BASES: tuple[BaseSupport, ...] = ("five_star_caster", "cross_caster")


# ---------------------------------------------------------------------------
# Palette colorways. Every .visual(material=...) draws one of these keys.
# Palette never enters the slot_choice tuple (>=3 distinct colorways required).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "blue_vinyl_chrome": {
        "chrome": (0.66, 0.68, 0.72, 1.0),
        "upholstery": (0.30, 0.32, 0.50, 1.0),
        "hub": (0.92, 0.82, 0.34, 1.0),
        "rubber": (0.07, 0.07, 0.08, 1.0),
    },
    "black_leather_chrome": {
        "chrome": (0.70, 0.72, 0.75, 1.0),
        "upholstery": (0.09, 0.09, 0.10, 1.0),
        "hub": (0.85, 0.78, 0.36, 1.0),
        "rubber": (0.05, 0.05, 0.055, 1.0),
    },
    "white_clinical": {
        "chrome": (0.80, 0.81, 0.83, 1.0),
        "upholstery": (0.90, 0.91, 0.92, 1.0),
        "hub": (0.62, 0.64, 0.67, 1.0),
        "rubber": (0.16, 0.16, 0.17, 1.0),
    },
    "teal_clinical": {
        "chrome": (0.68, 0.70, 0.73, 1.0),
        "upholstery": (0.18, 0.46, 0.46, 1.0),
        "hub": (0.55, 0.62, 0.60, 1.0),
        "rubber": (0.10, 0.11, 0.11, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Real-world scale (meters) — shared across all bases / backrests (from S1).
# ---------------------------------------------------------------------------
SEAT_RADIUS = 0.205
SEAT_THICK = 0.085
SEAT_TOP_Z = 0.560  # seat top at the collapsed (lowest) pose

COLUMN_RADIUS = 0.040  # outer telescoping sleeve radius
HUB_TOP_Z = 0.250  # top of yellow conical hub

ARM_POST_HEIGHT = 0.135
ARM_PAD_LEN = 0.230
ARM_PAD_W = 0.062
ARM_PAD_H = 0.058

LIFT_TRAVEL = 0.080  # gas-pillar height range

# --- Base assembly z-budget (world meters, ground at z=0) ---
WHEEL_R = 0.030
WHEEL_W = 0.014
WHEEL_GAP = 0.009
CASTER_R = 0.240  # radial distance of each caster stem from the column axis
LEG_ROOT_X = 0.040
LEG_TIP_X = 0.250
LEG_ROOT_Z = (0.060, 0.125)
LEG_TIP_Z = (0.080, 0.112)
HUB_CYL_R = 0.062
HUB_CYL_Z = (0.060, 0.135)
CONE_Z = (0.120, HUB_TOP_Z)
CONE_R = (0.088, 0.052)
COLLAR_Z = (HUB_TOP_Z, HUB_TOP_Z + 0.022)
COLLAR_R = 0.064
BELLOWS_Z0 = 0.258
PEDAL_Z = 0.105

# Pedestal base (S2).
DISC_R = 0.220
DISC_H = 0.022
PEDESTAL_R = 0.048
PEDESTAL_Z = (DISC_H, 0.120)

# Four-leg frame (S3).
N_LEGS = 4
LEG_AZIMUTH_OFFSET = math.pi / 4.0
FOOT_R = 0.026
FOOT_H = 0.012
LEG_TUBE_R = 0.014
LEG_TUBE_WALL = 0.003
LEG_ROOT_R = 0.062
LEG_ROOT_Z_4 = 0.098
LEG_TIP_R = 0.240
LEG_TIP_Z_4 = FOOT_H

# Backrest hinge geometry (seat-local frame; S6).
HINGE_X = -SEAT_RADIUS + 0.020
HINGE_Z = SEAT_THICK

# Legrest extension (S8).
LEGREST_LEN = 0.320
LEGREST_W = 0.280
LEGREST_THICK = 0.055
BRACKET_CHEEK_H = 0.065
BRACKET_CHEEK_T = 0.006
BRACKET_SPACING = 0.110
LEGREST_HINGE_X = SEAT_RADIUS + LEGREST_THICK / 2.0 + 0.005
LEGREST_HINGE_Z = SEAT_THICK - LEGREST_THICK / 2.0

TOL = dict(tolerance=0.0009, angular_tolerance=0.09)


# ===========================================================================
# Shared geometry builders (CadQuery, authored directly in meters).
# Adapted verbatim from the 5-star surgical_chair records.
# ===========================================================================
def _hub_cone_mesh(model, name: str):
    """Yellow conical hub: sunk into the base hub cylinder, capped by a collar
    that the bellows boot overlaps (S1)."""
    cone = (
        cq.Workplane("XY", origin=(0.0, 0.0, CONE_Z[0]))
        .circle(CONE_R[0])
        .workplane(offset=CONE_Z[1] - CONE_Z[0])
        .circle(CONE_R[1])
        .loft(combine=True)
    )
    collar = (
        cq.Workplane("XY", origin=(0.0, 0.0, COLLAR_Z[0]))
        .circle(COLLAR_R)
        .extrude(COLLAR_Z[1] - COLLAR_Z[0])
    )
    return mesh_from_cadquery(cone.union(collar), name, **TOL)


def _bellows_mesh(model, name: str, *, height: float = 0.205):
    """Black ribbed accordion boot around the telescoping pillar (S1).

    Height tracks the scaled sleeve so the boot top stays below the cushion."""
    z0 = 0.0
    z1 = height
    ribs = 8
    outer = 0.080
    inner = 0.067
    bore = 0.060
    outer_wall: list[tuple[float, float]] = []
    n = ribs * 2
    for k in range(n + 1):
        z = z0 + (z1 - z0) * k / n
        r = outer if (k % 2 == 1) else inner
        outer_wall.append((r, z))
    inner_wall = [(bore, z1), (bore, z0)]
    poly = outer_wall + inner_wall
    boot = cq.Workplane("XZ").polyline(poly).close().revolve(360.0, (0, 0, 0), (0, 1, 0))
    return mesh_from_cadquery(boot, name, **TOL)


def _column_sleeve_mesh(model, name: str, *, length: float = 0.210):
    """Chrome telescoping sleeve riser that the seat collar slides on (S1).

    Length is parameterized by seat_h_scale so the seated height varies while
    the seat_lift joint origin stays anchored on the real sleeve-top geometry.
    A solid piston-top cap closes the bore so the seat_lift joint origin (on the
    column axis at the sleeve top) sits on real solid metal, not in the bore."""
    sleeve = (
        cq.Workplane("XY", origin=(0.0, 0.0, 0.0))
        .circle(COLUMN_RADIUS)
        .circle(COLUMN_RADIUS - 0.008)
        .extrude(length)
    )
    # Solid gas-piston top cap filling the bore at the sleeve mouth.
    cap = (
        cq.Workplane("XY", origin=(0.0, 0.0, length - 0.012))
        .circle(COLUMN_RADIUS - 0.004)
        .extrude(0.012)
    )
    return mesh_from_cadquery(sleeve.union(cap), name, **TOL)


def _caster_mesh(model, name: str):
    """One twin-wheel caster; wheel bottoms sit at z=0. +X radial outward, twin
    wheels spin about local +Y, stem rises along +Z into the spoke tip (S1)."""
    wheels = None
    for s in (-1.0, 1.0):
        w = (
            cq.Workplane("XZ", origin=(0.0, s * (WHEEL_GAP + WHEEL_W / 2.0), WHEEL_R))
            .circle(WHEEL_R)
            .extrude(WHEEL_W / 2.0, both=True)
        )
        wheels = w if wheels is None else wheels.union(w)
    axle = (
        cq.Workplane("XZ", origin=(0.0, 0.0, WHEEL_R))
        .circle(0.007)
        .extrude(WHEEL_GAP + WHEEL_W, both=True)
    )
    yoke = cq.Workplane("XY", origin=(0.0, 0.0, 0.052)).box(0.034, 2.0 * WHEEL_GAP, 0.045)
    stem = cq.Workplane("XY", origin=(0.0, 0.0, 0.070)).circle(0.009).extrude(0.040)
    cas = wheels.union(axle).union(yoke).union(stem)
    return mesh_from_cadquery(cas, name, **TOL)


def _pedal_mesh(model, name: str):
    """Black foot pedal: horizontal stem rooted in the hub carrying a tilted
    rounded paddle (S1). Local stem axis +X at z=0; placement at PEDAL_Z."""
    stem = cq.Workplane("YZ", origin=(0.030, 0.0, 0.0)).circle(0.008).extrude(0.175)
    paddle = cq.Workplane("XY").box(0.075, 0.085, 0.014).edges("|Z").fillet(0.010)
    paddle = paddle.rotate((0, 0, 0), (0, 1, 0), -12.0).translate((0.210, 0.0, 0.004))
    return mesh_from_cadquery(stem.union(paddle), name, **TOL)


def _star_arms_mesh(model, name: str, *, arms: int):
    """N-spoke chrome caster base with a central column socket (S1 / S4).

    Each spoke is a loft between a tall wide root sunk into the hub cylinder
    and a shorter narrower tip the caster stem plugs into from below."""
    root_hw, tip_hw = 0.038, 0.020
    root = [
        (-root_hw, LEG_ROOT_Z[0]),
        (root_hw, LEG_ROOT_Z[0]),
        (root_hw, LEG_ROOT_Z[1]),
        (-root_hw, LEG_ROOT_Z[1]),
    ]
    tip = [
        (-tip_hw, LEG_TIP_Z[0]),
        (tip_hw, LEG_TIP_Z[0]),
        (tip_hw, LEG_TIP_Z[1]),
        (-tip_hw, LEG_TIP_Z[1]),
    ]
    base = None
    for i in range(arms):
        ang = 2.0 * math.pi * i / arms + math.radians(90.0)
        leg = (
            cq.Workplane("YZ", origin=(LEG_ROOT_X, 0.0, 0.0))
            .polyline(root)
            .close()
            .workplane(offset=LEG_TIP_X - LEG_ROOT_X)
            .polyline(tip)
            .close()
            .loft(combine=True)
        )
        leg = leg.rotate((0, 0, 0), (0, 0, 1), math.degrees(ang))
        base = leg if base is None else base.union(leg)
    hub = (
        cq.Workplane("XY", origin=(0.0, 0.0, HUB_CYL_Z[0]))
        .circle(HUB_CYL_R)
        .extrude(HUB_CYL_Z[1] - HUB_CYL_Z[0])
    )
    base = base.union(hub)
    return mesh_from_cadquery(base, name, **TOL)


def _pedestal_base_mesh(model, name: str):
    """Fixed pedestal: flat weighted disc foot + central column to the cone (S2)."""
    disc = cq.Workplane("XY", origin=(0.0, 0.0, 0.0)).circle(DISC_R).extrude(DISC_H)
    disc = disc.edges(">Z").chamfer(0.004)
    col_height = PEDESTAL_Z[1] - PEDESTAL_Z[0]
    column = (
        cq.Workplane("XY", origin=(0.0, 0.0, PEDESTAL_Z[0])).circle(PEDESTAL_R).extrude(col_height)
    )
    boss = (
        cq.Workplane("XY", origin=(0.0, 0.0, PEDESTAL_Z[0]))
        .circle(PEDESTAL_R + 0.012)
        .workplane(offset=0.018)
        .circle(PEDESTAL_R + 0.002)
        .loft(combine=True)
    )
    return mesh_from_cadquery(disc.union(column).union(boss), name, **TOL)


def _four_leg_hub_mesh(model, name: str):
    """Central hub cylinder tying the four legs together (S3)."""
    hub = (
        cq.Workplane("XY", origin=(0.0, 0.0, HUB_CYL_Z[0]))
        .circle(HUB_CYL_R)
        .extrude(HUB_CYL_Z[1] - HUB_CYL_Z[0])
    )
    return mesh_from_cadquery(hub, name, **TOL)


def _leg_mesh(model, name: str):
    """One splayed hollow tubular leg from hub wall to floor-level foot (S3)."""
    dx = LEG_TIP_R - LEG_ROOT_R
    dz = LEG_TIP_Z_4 - LEG_ROOT_Z_4
    length = math.sqrt(dx * dx + dz * dz)
    pitch_deg = math.degrees(math.atan2(dz, dx))
    tube = cq.Workplane("YZ").circle(LEG_TUBE_R).circle(LEG_TUBE_R - LEG_TUBE_WALL).extrude(length)
    tube = tube.rotate((0, 0, 0), (0, 1, 0), -pitch_deg)
    tube = tube.translate((LEG_ROOT_R, 0.0, LEG_ROOT_Z_4))
    return mesh_from_cadquery(tube, name, **TOL)


def _foot_mesh(model, name: str):
    """Rubber foot cap under a leg tip (S3)."""
    foot = cq.Workplane("XY", origin=(0.0, 0.0, 0.0)).circle(FOOT_R).extrude(FOOT_H)
    foot = foot.edges(">Z").fillet(min(0.006, FOOT_H * 0.4))
    return mesh_from_cadquery(foot, name, **TOL)


def _seat_mesh(model, name: str):
    """Round upholstered seat cushion with a soft domed top and rounded rim (S1)."""
    base_disc = cq.Workplane("XY", origin=(0.0, 0.0, 0.0)).circle(SEAT_RADIUS).extrude(0.030)
    cushion = (
        cq.Workplane("XY", origin=(0.0, 0.0, 0.030))
        .circle(SEAT_RADIUS)
        .workplane(offset=SEAT_THICK - 0.030)
        .circle(SEAT_RADIUS - 0.045)
        .loft(combine=True)
    )
    seat = base_disc.union(cushion)
    seat = seat.edges(">Z").fillet(0.018)
    return mesh_from_cadquery(seat, name, **TOL)


def _seat_mount_mesh(model, name: str):
    """Hidden underside collar gripping the column sleeve (S1)."""
    tube = (
        cq.Workplane("XY", origin=(0.0, 0.0, -0.145))
        .circle(COLUMN_RADIUS + 0.014)
        .circle(COLUMN_RADIUS - 0.002)
        .extrude(0.148)
    )
    plate = (
        cq.Workplane("XY", origin=(0.0, 0.0, -0.004)).circle(COLUMN_RADIUS + 0.014).extrude(0.006)
    )
    return mesh_from_cadquery(tube.union(plate), name, **TOL)


def _backrest_pad_mesh(model, name: str):
    """Curved padded backrest behind the seat (S1)."""
    pad = (
        cq.Workplane("XZ", origin=(0.0, 0.0, 0.0))
        .moveTo(-0.150, 0.0)
        .threePointArc((0.0, 0.030), (0.150, 0.0))
        .lineTo(0.150, 0.140)
        .threePointArc((0.0, 0.175), (-0.150, 0.140))
        .close()
        .extrude(0.060, both=True)
    )
    pad = pad.edges("|Y").fillet(0.020)
    return mesh_from_cadquery(pad, name, **TOL)


def _backrest_arm_fixed_mesh(model, name: str):
    """Chrome stalk carrying the backrest up off the seat rim (fixed_stalk; S1).
    Long on purpose: bottom sinks into the cushion, top embeds in the pad."""
    stalk = cq.Workplane("XY", origin=(0.0, 0.0, -0.060)).circle(0.012).extrude(0.205)
    return mesh_from_cadquery(stalk, name, **TOL)


def _backrest_arm_hinged_mesh(model, name: str):
    """Chrome stalk for the reclining backrest, authored at z=0 = hinge pivot,
    extending up into the pad (S6)."""
    stalk = cq.Workplane("XY", origin=(0.0, 0.0, 0.0)).circle(0.012).extrude(0.200)
    return mesh_from_cadquery(stalk, name, **TOL)


def _backrest_bracket_mesh(model, name: str):
    """Chrome hinge bracket at the seat rear edge: base plate + two ears +
    a horizontal pivot crossbar along Y (S6)."""
    plate = cq.Workplane("XY").box(0.048, 0.076, 0.010)
    for s in (-1.0, 1.0):
        ear = (
            cq.Workplane("XY", origin=(0.0, s * 0.028, 0.025))
            .box(0.024, 0.012, 0.040)
            .edges(">Z")
            .fillet(0.005)
        )
        plate = plate.union(ear)
    bar = cq.Workplane("XZ", origin=(0.0, 0.0, 0.040)).circle(0.005).extrude(0.028, both=True)
    return mesh_from_cadquery(plate.union(bar), name, **TOL)


def _lower_back_mesh(model, name: str):
    """Fixed lower lumbar pad of the split backrest (S7)."""
    pad = (
        cq.Workplane("XZ", origin=(0.0, 0.0, 0.0))
        .moveTo(-0.150, 0.0)
        .threePointArc((0.0, 0.030), (0.150, 0.0))
        .lineTo(0.150, 0.100)
        .threePointArc((0.0, 0.115), (-0.150, 0.100))
        .close()
        .extrude(0.060, both=True)
    )
    pad = pad.edges("|Y").fillet(0.020)
    return mesh_from_cadquery(pad, name, **TOL)


def _headrest_stem_mesh(model, name: str):
    """Chrome stem rising from the lower pad top to carry the headrest (S7)."""
    stem = cq.Workplane("XY", origin=(0.0, 0.0, 0.0)).circle(0.010).extrude(0.055)
    flange = cq.Workplane("XY", origin=(0.0, 0.0, 0.050)).circle(0.018).extrude(0.008)
    return mesh_from_cadquery(stem.union(flange), name, **TOL)


def _headrest_pad_mesh(model, name: str):
    """Upper headrest pad that tilts on the chrome stem; flat bottom seats on
    the stem flange (S7)."""
    pad = (
        cq.Workplane("XZ", origin=(0.0, 0.0, 0.0))
        .moveTo(-0.120, 0.0)
        .lineTo(0.120, 0.0)
        .lineTo(0.120, 0.080)
        .threePointArc((0.0, 0.098), (-0.120, 0.080))
        .close()
        .extrude(0.050, both=True)
    )
    pad = pad.edges("|Y").fillet(0.016)
    return mesh_from_cadquery(pad, name, **TOL)


def _legrest_pad_mesh(model, name: str):
    """Padded legrest panel hanging downward from the hinge (S8). Hinge at
    origin (pin along Y); panel extends along -Z at rest."""
    panel = (
        cq.Workplane("XY", origin=(0.0, 0.0, -LEGREST_LEN / 2.0))
        .box(LEGREST_THICK, LEGREST_W, LEGREST_LEN)
        .edges("|Z")
        .fillet(0.018)
    )
    panel = panel.edges("<Z").fillet(0.014)
    knuckle_len = BRACKET_SPACING - 2.0 * BRACKET_CHEEK_T - 0.006
    knuckle = (
        cq.Workplane("XZ", origin=(0.0, 0.0, 0.0))
        .circle(0.013)
        .extrude(knuckle_len / 2.0, both=True)
    )
    gusset = cq.Workplane("XY", origin=(0.0, 0.0, -0.012)).box(LEGREST_THICK, knuckle_len, 0.028)
    return mesh_from_cadquery(panel.union(knuckle).union(gusset), name, **TOL)


def _legrest_bracket_mesh(model, name: str):
    """Chrome hinge bracket at the seat front edge: two cheeks + hinge pin +
    a mounting plate reaching back into the cushion body (S8)."""
    bracket = None
    cheek_x_extent = 0.034
    for s in (-1.0, 1.0):
        cheek = (
            cq.Workplane(
                "XY",
                origin=(
                    cheek_x_extent / 2.0 - 0.005,
                    s * BRACKET_SPACING / 2.0,
                    -BRACKET_CHEEK_H / 2.0,
                ),
            )
            .box(cheek_x_extent, BRACKET_CHEEK_T, BRACKET_CHEEK_H)
            .edges("|Y")
            .fillet(0.003)
        )
        bracket = cheek if bracket is None else bracket.union(cheek)
    pin_half = BRACKET_SPACING / 2.0 + BRACKET_CHEEK_T + 0.002
    pin = cq.Workplane("XZ", origin=(0.0, 0.0, 0.0)).circle(0.005).extrude(pin_half, both=True)
    bracket = bracket.union(pin)
    mount = (
        cq.Workplane("XY", origin=(-0.050, 0.0, 0.0))
        .box(0.090, BRACKET_SPACING, 0.040)
        .edges("|Z")
        .fillet(0.006)
    )
    bracket = bracket.union(mount)
    return mesh_from_cadquery(bracket, name, **TOL)


# Geometry constants shared by the arm frame and its pad (S1).
_ARM_STALK_LEN = ARM_PAD_LEN * 0.55
_ARM_PAD_CX = ARM_PAD_LEN * 0.45
_ARM_PAD_CZ = ARM_POST_HEIGHT + ARM_PAD_H / 2.0 - 0.020

# Swing-post standoff from the column axis (the joint origin |y|). Single-sourced
# so the arm builder and the inward-swing limit derive from one value.
POST_RADIUS_XY = SEAT_RADIUS - 0.028

# Inward-swing clearance: at full inward swing each armrest pad must stop this far
# short of the seat midline (y=0). The two wings are independent parts and must
# never occupy the same space (motion-QC 穿模), so this is a genuine geometric
# limit, not an allow_overlap. 0.008 m per side => a 2*0.008 = 16 mm gap between
# the mirrored pads (well clear of the 5 mm overlap tol).
ARM_MIDLINE_CLEARANCE = 0.008


def _arm_inward_swing_limit() -> float:
    """Magnitude (rad) of the max inward armrest swing at which the pad's
    forward, midline-side corner still clears the seat midline by
    ARM_MIDLINE_CLEARANCE (Contract 3c: single-sourced geometric limit).

    The +Y (left) post sits at |y| = POST_RADIUS_XY; the pad box extends along
    local +X. At inward (negative) theta the critical corner is (x_hi, -half_w).
    Solving
        POST_RADIUS_XY + x_hi*sin(theta) - half_w*cos(theta) = ARM_MIDLINE_CLEARANCE
    for the most-inward theta gives the limit; the right arm mirrors it. Because
    the wings are mirror-symmetric, each stopping ARM_MIDLINE_CLEARANCE short of
    y=0 leaves a 2*ARM_MIDLINE_CLEARANCE gap so they cannot interpenetrate."""
    x_hi = _ARM_PAD_CX + ARM_PAD_LEN / 2.0
    half_w = ARM_PAD_W / 2.0
    r = math.hypot(x_hi, half_w)
    phi = math.atan2(-half_w, x_hi)
    c = ARM_MIDLINE_CLEARANCE - POST_RADIUS_XY
    theta = math.asin(max(-1.0, min(1.0, c / r))) - phi
    return abs(theta)


# Max inward swing magnitude (rad) shared by both mirrored wings (~0.731 rad).
ARM_INWARD_SWING = _arm_inward_swing_limit()


def _arm_frame_mesh(model, name: str, *, sign: float):
    """Chrome frame of one armrest: vertical swing post + clamp collar +
    horizontal carrier stalk + small adjustment lever/knob (S1). Post axis is
    local +Z through (0,0,*); the pad extends along +X."""
    post = cq.Workplane("XY", origin=(0.0, 0.0, 0.0)).circle(0.013).extrude(ARM_POST_HEIGHT)
    collar = (
        cq.Workplane("XY", origin=(-0.016, 0.0, 0.010))
        .box(0.052, 0.030, 0.034)
        .edges("|Z")
        .fillet(0.008)
    )
    post = post.union(collar)
    stalk = (
        cq.Workplane("XY", origin=(0.0, 0.0, ARM_POST_HEIGHT - 0.020))
        .transformed(rotate=(0.0, 90.0, 0.0))
        .circle(0.010)
        .extrude(_ARM_STALK_LEN)
    )
    lever = cq.Workplane("XZ", origin=(0.0, 0.0, 0.040)).circle(0.006).extrude(-sign * 0.043)
    knob = cq.Workplane("XY", origin=(0.0, sign * 0.043, 0.040)).sphere(0.011)
    frame = post.union(stalk).union(lever).union(knob)
    return mesh_from_cadquery(frame, name, **TOL)


def _arm_pad_mesh(model, name: str):
    """Upholstered armrest cushion, long axis along X, resting on the stalk (S1)."""
    pad = (
        cq.Workplane("XY", origin=(_ARM_PAD_CX, 0.0, _ARM_PAD_CZ))
        .box(ARM_PAD_LEN, ARM_PAD_W, ARM_PAD_H)
        .edges("|Z")
        .fillet(0.020)
    )
    pad = pad.edges(">Z").fillet(0.014)
    return mesh_from_cadquery(pad, name, **TOL)


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class SurgicalChairConfig:
    base_support: BaseSupport | None = None
    backrest_mechanism: BackrestMechanism | None = None
    caster_count: int | None = None
    palette_style: PaletteStyle = "blue_vinyl_chrome"
    seat_h_scale: float = 1.0
    column_scale: float = 1.0
    name: str = "surgical_chair"


@dataclass(frozen=True)
class ResolvedSurgicalChairConfig:
    base_support: BaseSupport
    backrest_mechanism: BackrestMechanism
    caster_count: int  # number of casters; 0 when not a caster base
    palette_style: PaletteStyle
    sleeve_len: float  # chrome telescoping sleeve length (scaled by seat_h_scale)
    column_top_z: float  # world z of the sleeve top = seat_lift joint origin z
    seat_frame_z: float  # seat part-frame z at q=0 (== column_top_z)
    seat_top_z: float  # seat top height at the collapsed pose
    lift_travel: float
    column_scale: float
    name: str

    @property
    def is_star_caster(self) -> bool:
        return self.base_support == "five_star_caster"

    @property
    def is_caster_base(self) -> bool:
        return self.base_support in CASTER_BASES


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> SurgicalChairConfig:
    """Deterministic procedural sampling over the full slot domain (seed 0 is
    not special). Sample base + backrest uniformly; sample caster_count only
    when the base is the star caster (other bases ignore it)."""
    rng = random.Random(seed)
    return SurgicalChairConfig(
        base_support=rng.choice(BASE_SUPPORTS),
        backrest_mechanism=rng.choice(BACKREST_MECHANISMS),
        caster_count=rng.choices(CASTER_COUNTS, weights=CASTER_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        seat_h_scale=round(rng.uniform(0.90, 1.15), 4),
        column_scale=round(rng.uniform(0.90, 1.15), 4),
        name=f"seeded_surgical_chair_{seed}",
    )


def resolve_config(
    config: SurgicalChairConfig | None = None,
) -> ResolvedSurgicalChairConfig:
    cfg = config or SurgicalChairConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    base_support = _pick(cfg.base_support, BASE_SUPPORTS)
    backrest_mechanism = _pick(cfg.backrest_mechanism, BACKREST_MECHANISMS)

    # caster_count: only meaningful on the five_star_caster base (multiplicity
    # axis). cross_caster is structurally fixed at 4 wheels; non-caster bases
    # carry no casters.
    if base_support == "five_star_caster":
        n = int(cfg.caster_count) if cfg.caster_count is not None else 5
        caster_count = int(_clamp(n, N_MIN, N_MAX))
    elif base_support == "cross_caster":
        caster_count = 4
    else:
        caster_count = 0

    # Scales (independent clamp). seat_h_scale stretches the chrome sleeve so
    # the seated height varies while the seat_lift origin stays anchored on the
    # real sleeve-top geometry (avoids the joint-origin-far-from-geometry trap).
    seat_h_scale = _clamp(cfg.seat_h_scale, 0.90, 1.15)
    column_scale = _clamp(cfg.column_scale, 0.90, 1.15)

    # Base sleeve length 0.210 (S1); scale it for the seated-height variation.
    sleeve_len = 0.210 * seat_h_scale
    # Sleeve rises from HUB_TOP_Z; its top is real geometry the joint sits on.
    column_top_z = HUB_TOP_Z + sleeve_len
    seat_frame_z = column_top_z  # cushion bottom rests on the sleeve top
    seat_top_z = seat_frame_z + SEAT_THICK

    return ResolvedSurgicalChairConfig(
        base_support=base_support,
        backrest_mechanism=backrest_mechanism,
        caster_count=caster_count,
        palette_style=palette_style,
        sleeve_len=sleeve_len,
        column_top_z=column_top_z,
        seat_frame_z=seat_frame_z,
        seat_top_z=seat_top_z,
        lift_travel=LIFT_TRAVEL,
        column_scale=column_scale,
        name=cfg.name or "surgical_chair",
    )


def slot_choices_for_config(
    config: SurgicalChairConfig | ResolvedSurgicalChairConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedSurgicalChairConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("base", r.base_support),
        ("backrest_mechanism", r.backrest_mechanism),
    ]
    # Multiplicity axis only on the star caster base (conditional).
    if r.is_star_caster:
        choices.append(("caster_count", f"c{r.caster_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Base builders (Slot A). Each emits the `base` root part + decorative caster /
# pedal / hub-cone / sleeve / bellows visuals, plus the shared upper column.
# Casters and pedals are FIXED decorative visuals (Rule 1).
# ===========================================================================
def _emit_upper_column(base, r: ResolvedSurgicalChairConfig, mats):
    """Yellow cone + chrome sleeve + bellows boot rising from the hub (shared)."""
    base.visual(_hub_cone_mesh(base, "hub_cone"), material=mats["hub"], name="hub_cone", material_class_id="metal.paint_coated")
    base.visual(
        _column_sleeve_mesh(base, "column_sleeve", length=r.sleeve_len),
        origin=Origin(xyz=(0.0, 0.0, HUB_TOP_Z)),
        material=mats["chrome"],
        name="column_sleeve", material_class_id="metal.chrome_polished",
    )
    # Boot wraps the sleeve from just above the cone collar up to just under the
    # cushion bottom (column_top_z); height tracks the scaled sleeve.
    bellows_h = max(0.12, r.column_top_z - BELLOWS_Z0 - 0.010)
    base.visual(
        _bellows_mesh(base, "bellows_boot", height=bellows_h),
        origin=Origin(xyz=(0.0, 0.0, BELLOWS_Z0)),
        material=mats["rubber"],
        name="bellows_boot", material_class_id="rubber.directional_grooved",
    )


def _emit_pedals(base, mats, angles):
    for j, pang in enumerate(angles):
        base.visual(
            _pedal_mesh(base, f"pedal_{j}"),
            origin=Origin(xyz=(0.0, 0.0, PEDAL_Z), rpy=(0.0, 0.0, pang)),
            material=mats["rubber"],
            name=f"pedal_{j}", material_class_id="rubber.smooth_plain",
        )


def _emit_casters(base, mats, n: int):
    """N twin-wheel casters in an even ring, each FIXED decorative (Rule 1)."""
    for i in range(n):
        ang = 2.0 * math.pi * i / n + math.radians(90.0)
        cx = CASTER_R * math.cos(ang)
        cy = CASTER_R * math.sin(ang)
        base.visual(
            _caster_mesh(base, f"caster_{i}"),
            origin=Origin(xyz=(cx, cy, 0.0), rpy=(0.0, 0.0, ang)),
            material=mats["rubber"],
            name=f"caster_{i}", material_class_id="rubber.smooth_plain",
        )


def _build_five_star_caster(model, r: ResolvedSurgicalChairConfig, mats):
    base = model.part("base")
    # One spoke per caster so every caster stem plugs into a spoke tip (S1/S5);
    # spoke and caster share the same even-angle ring (θ = 2πi/N + 90°).
    base.visual(
        _star_arms_mesh(base, "star_base", arms=r.caster_count),
        material=mats["chrome"],
        name="star_base", material_class_id="metal.chrome_polished",
    )
    _emit_casters(base, mats, r.caster_count)
    _emit_pedals(base, mats, (math.radians(45.0), math.radians(-45.0)))
    _emit_upper_column(base, r, mats)
    return base


def _build_cross_caster(model, r: ResolvedSurgicalChairConfig, mats):
    base = model.part("base")
    base.visual(
        _star_arms_mesh(base, "cross_base", arms=4),
        material=mats["chrome"],
        name="cross_base", material_class_id="metal.chrome_polished",
    )
    _emit_casters(base, mats, 4)
    _emit_pedals(base, mats, (math.radians(45.0), math.radians(-45.0)))
    _emit_upper_column(base, r, mats)
    return base


def _build_fixed_pedestal(model, r: ResolvedSurgicalChairConfig, mats):
    base = model.part("base")
    base.visual(
        _pedestal_base_mesh(base, "pedestal_base"),
        material=mats["chrome"],
        name="pedestal_base", material_class_id="metal.chrome_polished",
    )
    # No casters / pedals on the fixed pedestal (matches S2).
    _emit_upper_column(base, r, mats)
    return base


def _build_four_leg_frame(model, r: ResolvedSurgicalChairConfig, mats):
    base = model.part("base")
    base.visual(_four_leg_hub_mesh(base, "hub"), material=mats["chrome"], name="hub", material_class_id="metal.chrome_polished")
    for i in range(N_LEGS):
        az = LEG_AZIMUTH_OFFSET + i * 2.0 * math.pi / N_LEGS
        base.visual(
            _leg_mesh(base, f"leg_{i}"),
            origin=Origin(rpy=(0.0, 0.0, az)),
            material=mats["chrome"],
            name=f"leg_{i}", material_class_id="metal.chrome_polished",
        )
    for i in range(N_LEGS):
        az = LEG_AZIMUTH_OFFSET + i * 2.0 * math.pi / N_LEGS
        fx = LEG_TIP_R * math.cos(az)
        fy = LEG_TIP_R * math.sin(az)
        base.visual(
            _foot_mesh(base, f"foot_{i}"),
            origin=Origin(xyz=(fx, fy, 0.0)),
            material=mats["rubber"],
            name=f"foot_{i}", material_class_id="rubber.smooth_plain",
        )
    _emit_pedals(base, mats, (0.0, math.pi))
    _emit_upper_column(base, r, mats)
    return base


_BASE_BUILDERS = {
    "five_star_caster": _build_five_star_caster,
    "cross_caster": _build_cross_caster,
    "fixed_pedestal": _build_fixed_pedestal,
    "four_leg_frame": _build_four_leg_frame,
}


# ===========================================================================
# Seat + arms (fixed spine — kept on every seed).
# ===========================================================================
def _build_seat(model, r: ResolvedSurgicalChairConfig, mats):
    seat = model.part("seat")
    seat.visual(_seat_mesh(seat, "seat_cushion"), material=mats["upholstery"], name="seat_cushion", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"blue_vinyl_chrome", "white_clinical", "teal_clinical"} else "leather.smooth_plain"))
    seat.visual(_seat_mount_mesh(seat, "seat_mount"), material=mats["chrome"], name="seat_mount", material_class_id="metal.chrome_polished")
    seat.inertial = Inertial.from_geometry(
        Box((2.0 * SEAT_RADIUS, 2.0 * SEAT_RADIUS, SEAT_THICK)),
        mass=6.0,
        origin=Origin(xyz=(0.0, 0.0, SEAT_THICK / 2.0)),
    )
    return seat


def _emit_seat_lift(model, base, seat, r: ResolvedSurgicalChairConfig):
    """Gas-pillar PRISMATIC lift: seat raises/lowers on the column (+Z)."""
    model.articulation(
        "seat_lift",
        ArticulationType.PRISMATIC,
        parent=base,
        child=seat,
        origin=Origin(xyz=(0.0, 0.0, r.seat_frame_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=600.0, velocity=0.10, lower=0.0, upper=r.lift_travel),
    )


def _build_armrests(model, seat, r: ResolvedSurgicalChairConfig, mats):
    """Two wing armrests that swing out on vertical posts (REVOLUTE +Z)."""
    post_z = SEAT_THICK - 0.030
    post_radius_xy = POST_RADIUS_XY

    left_arm = model.part("left_arm")
    left_arm.visual(
        _arm_frame_mesh(left_arm, "left_arm_frame", sign=1.0),
        material=mats["chrome"],
        name="left_arm_frame", material_class_id="metal.chrome_polished",
    )
    left_arm.visual(
        _arm_pad_mesh(left_arm, "left_arm_pad"),
        material=mats["upholstery"],
        name="left_arm_pad", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"blue_vinyl_chrome", "white_clinical", "teal_clinical"} else "leather.smooth_plain"),
    )
    left_arm.inertial = Inertial.from_geometry(
        Box((ARM_PAD_LEN, ARM_PAD_W, ARM_POST_HEIGHT)),
        mass=0.8,
        origin=Origin(xyz=(_ARM_PAD_CX * 0.5, 0.0, ARM_POST_HEIGHT / 2.0)),
    )

    right_arm = model.part("right_arm")
    right_arm.visual(
        _arm_frame_mesh(right_arm, "right_arm_frame", sign=-1.0),
        material=mats["chrome"],
        name="right_arm_frame", material_class_id="metal.chrome_polished",
    )
    right_arm.visual(
        _arm_pad_mesh(right_arm, "right_arm_pad"),
        material=mats["upholstery"],
        name="right_arm_pad", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"blue_vinyl_chrome", "white_clinical", "teal_clinical"} else "leather.smooth_plain"),
    )
    right_arm.inertial = Inertial.from_geometry(
        Box((ARM_PAD_LEN, ARM_PAD_W, ARM_POST_HEIGHT)),
        mass=0.8,
        origin=Origin(xyz=(_ARM_PAD_CX * 0.5, 0.0, ARM_POST_HEIGHT / 2.0)),
    )

    model.articulation(
        "left_arm_swing",
        ArticulationType.REVOLUTE,
        parent=seat,
        child=left_arm,
        origin=Origin(xyz=(0.060, post_radius_xy, post_z)),
        axis=(0.0, 0.0, 1.0),
        # Inward (negative) swing capped by geometry so the +Y pad cannot cross
        # the seat midline into the -Y arm; outward (+) range kept intact.
        motion_limits=MotionLimits(effort=20.0, velocity=2.0, lower=-ARM_INWARD_SWING, upper=0.2),
    )
    model.articulation(
        "right_arm_swing",
        ArticulationType.REVOLUTE,
        parent=seat,
        child=right_arm,
        origin=Origin(xyz=(0.060, -post_radius_xy, post_z)),
        axis=(0.0, 0.0, 1.0),
        # Mirror: inward (positive) swing capped; outward (-) range kept intact.
        motion_limits=MotionLimits(effort=20.0, velocity=2.0, lower=-0.2, upper=ARM_INWARD_SWING),
    )


# ===========================================================================
# Backrest mechanisms (Slot B).
# ===========================================================================
def _build_fixed_stalk(model, seat, r: ResolvedSurgicalChairConfig, mats):
    """Rigid backrest on a chrome stalk, fused to the seat (0 joint; S1)."""
    seat.visual(
        _backrest_arm_fixed_mesh(seat, "backrest_arm"),
        origin=Origin(xyz=(-SEAT_RADIUS + 0.020, 0.0, SEAT_THICK - 0.010)),
        material=mats["chrome"],
        name="backrest_arm", material_class_id="metal.chrome_polished",
    )
    seat.visual(
        _backrest_pad_mesh(seat, "backrest_pad"),
        origin=Origin(xyz=(-SEAT_RADIUS - 0.010, 0.0, SEAT_THICK + 0.090)),
        material=mats["upholstery"],
        name="backrest_pad", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"blue_vinyl_chrome", "white_clinical", "teal_clinical"} else "leather.smooth_plain"),
    )


def _build_reclining_backrest(model, seat, r: ResolvedSurgicalChairConfig, mats):
    """Backrest as a separate part hinged to the seat rear (REVOLUTE -Y; S6)."""
    # Visible hinge bracket on the seat rear edge (fixed to seat).
    seat.visual(
        _backrest_bracket_mesh(seat, "backrest_bracket"),
        origin=Origin(xyz=(HINGE_X, 0.0, HINGE_Z)),
        material=mats["chrome"],
        name="backrest_bracket", material_class_id="metal.chrome_polished",
    )
    backrest = model.part("backrest")
    backrest.visual(
        _backrest_arm_hinged_mesh(backrest, "backrest_arm"),
        material=mats["chrome"],
        name="backrest_arm", material_class_id="metal.chrome_polished",
    )
    backrest.visual(
        _backrest_pad_mesh(backrest, "backrest_pad"),
        origin=Origin(xyz=(-0.030, 0.0, 0.090)),
        material=mats["upholstery"],
        name="backrest_pad", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"blue_vinyl_chrome", "white_clinical", "teal_clinical"} else "leather.smooth_plain"),
    )
    backrest.inertial = Inertial.from_geometry(
        Box((0.10, 0.30, 0.20)),
        mass=1.5,
        origin=Origin(xyz=(-0.03, 0.0, 0.12)),
    )
    model.articulation(
        "seat_to_backrest",
        ArticulationType.REVOLUTE,
        parent=seat,
        child=backrest,
        origin=Origin(xyz=(HINGE_X, 0.0, HINGE_Z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=1.5, lower=-0.25, upper=0.55),
    )


def _build_split_headrest_tilt(model, seat, r: ResolvedSurgicalChairConfig, mats):
    """Fixed lower lumbar pad + separate upper headrest tilting on a stem
    (REVOLUTE +Y; S7)."""
    seat.visual(
        _backrest_arm_fixed_mesh(seat, "backrest_arm"),
        origin=Origin(xyz=(-SEAT_RADIUS + 0.020, 0.0, SEAT_THICK - 0.010)),
        material=mats["chrome"],
        name="backrest_arm", material_class_id="metal.chrome_polished",
    )
    lower_back_z = SEAT_THICK + 0.090
    seat.visual(
        _lower_back_mesh(seat, "lower_back_pad"),
        origin=Origin(xyz=(-SEAT_RADIUS - 0.010, 0.0, lower_back_z)),
        material=mats["upholstery"],
        name="lower_back_pad", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"blue_vinyl_chrome", "white_clinical", "teal_clinical"} else "leather.smooth_plain"),
    )
    lower_back_top = lower_back_z + 0.100
    seat.visual(
        _headrest_stem_mesh(seat, "headrest_stem"),
        origin=Origin(xyz=(-SEAT_RADIUS - 0.010, 0.0, lower_back_top)),
        material=mats["chrome"],
        name="headrest_stem", material_class_id="metal.chrome_polished",
    )
    headrest = model.part("headrest")
    headrest.visual(
        _headrest_pad_mesh(headrest, "headrest_pad"),
        material=mats["upholstery"],
        name="headrest_pad", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"blue_vinyl_chrome", "white_clinical", "teal_clinical"} else "leather.smooth_plain"),
    )
    headrest.inertial = Inertial.from_geometry(
        Box((0.06, 0.24, 0.10)),
        mass=0.6,
        origin=Origin(xyz=(0.0, 0.0, 0.05)),
    )
    headrest_joint_z = lower_back_top + 0.058
    model.articulation(
        "headrest_tilt",
        ArticulationType.REVOLUTE,
        parent=seat,
        child=headrest,
        origin=Origin(xyz=(-SEAT_RADIUS - 0.010, 0.0, headrest_joint_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.5, lower=-0.45, upper=0.25),
    )


def _build_footrest_legrest(model, seat, r: ResolvedSurgicalChairConfig, mats):
    """Fixed rear backrest + a front legrest panel swinging up (REVOLUTE -Y; S8)."""
    # Standard fixed backrest at the rear (S8 keeps a rigid backrest).
    seat.visual(
        _backrest_arm_fixed_mesh(seat, "backrest_arm"),
        origin=Origin(xyz=(-SEAT_RADIUS + 0.020, 0.0, SEAT_THICK - 0.010)),
        material=mats["chrome"],
        name="backrest_arm", material_class_id="metal.chrome_polished",
    )
    seat.visual(
        _backrest_pad_mesh(seat, "backrest_pad"),
        origin=Origin(xyz=(-SEAT_RADIUS - 0.010, 0.0, SEAT_THICK + 0.090)),
        material=mats["upholstery"],
        name="backrest_pad", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"blue_vinyl_chrome", "white_clinical", "teal_clinical"} else "leather.smooth_plain"),
    )
    # Front hinge bracket (fixed to seat).
    seat.visual(
        _legrest_bracket_mesh(seat, "legrest_bracket"),
        origin=Origin(xyz=(LEGREST_HINGE_X, 0.0, LEGREST_HINGE_Z)),
        material=mats["chrome"],
        name="legrest_bracket", material_class_id="metal.chrome_polished",
    )
    legrest = model.part("legrest")
    legrest.visual(
        _legrest_pad_mesh(legrest, "legrest_pad"),
        material=mats["upholstery"],
        name="legrest_pad", material_class_id=("fabric.upholstery_plain" if r.palette_style in {"blue_vinyl_chrome", "white_clinical", "teal_clinical"} else "leather.smooth_plain"),
    )
    legrest.inertial = Inertial.from_geometry(
        Box((LEGREST_THICK, LEGREST_W, LEGREST_LEN)),
        mass=1.2,
        origin=Origin(xyz=(0.0, 0.0, -LEGREST_LEN / 2.0)),
    )
    model.articulation(
        "legrest_hinge",
        ArticulationType.REVOLUTE,
        parent=seat,
        child=legrest,
        origin=Origin(xyz=(LEGREST_HINGE_X, 0.0, LEGREST_HINGE_Z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=1.5, lower=0.0, upper=1.45),
    )


_BACKREST_BUILDERS = {
    "fixed_stalk": _build_fixed_stalk,
    "reclining_backrest": _build_reclining_backrest,
    "split_headrest_tilt": _build_split_headrest_tilt,
    "footrest_legrest": _build_footrest_legrest,
}


# ===========================================================================
# Top-level build
# ===========================================================================
def build_surgical_chair(
    config: SurgicalChairConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"surgical_chair_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    base = _BASE_BUILDERS[r.base_support](model, r, mats)
    # base inertial proxy.
    base.inertial = Inertial.from_geometry(
        Box((2.0 * CASTER_R, 2.0 * CASTER_R, HUB_TOP_Z)),
        mass=4.0,
        origin=Origin(xyz=(0.0, 0.0, HUB_TOP_Z / 2.0)),
    )

    seat = _build_seat(model, r, mats)
    _emit_seat_lift(model, base, seat, r)

    # Backrest mechanism (parallel child of the seat, or fused into the seat).
    _BACKREST_BUILDERS[r.backrest_mechanism](model, seat, r, mats)

    # Wing armrests (fixed spine — always present, 2 of them).
    _build_armrests(model, seat, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_surgical_chair(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_surgical_chair(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_surgical_chair_tests(
    object_model: ArticulatedObject,
    config: SurgicalChairConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    base = object_model.get_part("base")
    seat = object_model.get_part("seat")
    left_arm = object_model.get_part("left_arm")
    right_arm = object_model.get_part("right_arm")

    # ---- Captured / nested fits (element-scoped allow_overlap). ----
    # Seat collar telescopes over the column sleeve (prismatic capture fit).
    ctx.allow_overlap(
        seat,
        base,
        elem_a="seat_mount",
        elem_b="column_sleeve",
        reason="Seat collar telescopes over the gas-pillar sleeve (prismatic capture).",
    )
    # Each armrest clamp collar embeds into the cushion rim (mounted, not floating).
    ctx.allow_overlap(
        left_arm,
        seat,
        elem_a="left_arm_frame",
        elem_b="seat_cushion",
        reason="Left armrest clamp collar seats into the cushion rim.",
    )
    ctx.allow_overlap(
        right_arm,
        seat,
        elem_a="right_arm_frame",
        elem_b="seat_cushion",
        reason="Right armrest clamp collar seats into the cushion rim.",
    )

    # Backrest-mechanism-specific captured pivots.
    if r.backrest_mechanism == "reclining_backrest":
        backrest = object_model.get_part("backrest")
        ctx.allow_overlap(
            seat,
            backrest,
            elem_a="backrest_bracket",
            elem_b="backrest_arm",
            reason="Backrest stalk passes through the bracket ears at the hinge pivot.",
        )
        ctx.allow_overlap(
            seat,
            backrest,
            elem_a="seat_cushion",
            elem_b="backrest_arm",
            reason="Backrest stalk root meets the seat rear at the recline seam.",
        )
    elif r.backrest_mechanism == "split_headrest_tilt":
        headrest = object_model.get_part("headrest")
        ctx.allow_overlap(
            seat,
            headrest,
            elem_a="headrest_stem",
            elem_b="headrest_pad",
            reason="Headrest pad seats on the stem flange (captured tilt mount).",
        )
    elif r.backrest_mechanism == "footrest_legrest":
        legrest = object_model.get_part("legrest")
        ctx.allow_overlap(
            seat,
            legrest,
            elem_a="legrest_bracket",
            elem_b="legrest_pad",
            reason="Legrest knuckle is captured between the bracket cheeks (hinge pin).",
        )
        ctx.allow_overlap(
            seat,
            legrest,
            elem_a="seat_cushion",
            elem_b="legrest_pad",
            reason="Legrest top meets the cushion front edge when extended.",
        )

    # ---- Spine joint identity (kept on every seed). ----
    seat_lift = object_model.get_articulation("seat_lift")
    left_swing = object_model.get_articulation("left_arm_swing")
    right_swing = object_model.get_articulation("right_arm_swing")
    ctx.check(
        "seat_lift is prismatic about +Z",
        seat_lift.articulation_type == ArticulationType.PRISMATIC
        and tuple(seat_lift.axis) == (0.0, 0.0, 1.0),
        details=f"type={seat_lift.articulation_type}, axis={seat_lift.axis}",
    )
    ctx.check(
        "left arm swings (revolute) about +Z",
        left_swing.articulation_type == ArticulationType.REVOLUTE
        and tuple(left_swing.axis) == (0.0, 0.0, 1.0),
        details=f"type={left_swing.articulation_type}, axis={left_swing.axis}",
    )
    ctx.check(
        "right arm swings (revolute) about +Z",
        right_swing.articulation_type == ArticulationType.REVOLUTE
        and tuple(right_swing.axis) == (0.0, 0.0, 1.0),
        details=f"type={right_swing.articulation_type}, axis={right_swing.axis}",
    )

    # ---- Hero geometry checks. ----
    seat_cushion = seat.get_visual("seat_cushion")
    sc_aabb = ctx.part_element_world_aabb(seat, elem=seat_cushion)
    ctx.check(
        "seat cushion sits well above the base",
        sc_aabb is not None and sc_aabb[0][2] > HUB_TOP_Z + 0.10,
        details=f"cushion_min_z={sc_aabb[0][2] if sc_aabb else None}",
    )
    if sc_aabb is not None:
        sx = sc_aabb[1][0] - sc_aabb[0][0]
        sy = sc_aabb[1][1] - sc_aabb[0][1]
        ctx.check(
            "seat reads as a wide round cushion",
            sx > 2.0 * SEAT_RADIUS - 0.02 and sy > 2.0 * SEAT_RADIUS - 0.02,
            details=f"seat extent x={sx:.3f}, y={sy:.3f}",
        )

    # Armrests on opposite Y sides, pads above the seat top.
    la_aabb = ctx.part_world_aabb(left_arm)
    ra_aabb = ctx.part_world_aabb(right_arm)
    ctx.check(
        "left armrest on +Y side, right on -Y side",
        la_aabb is not None and ra_aabb is not None and la_aabb[1][1] > 0.0 and ra_aabb[0][1] < 0.0,
        details=f"left_max_y={la_aabb[1][1] if la_aabb else None}, "
        f"right_min_y={ra_aabb[0][1] if ra_aabb else None}",
    )

    # ---- Prismatic lift actually raises the seat. ----
    rest_seat = ctx.part_world_position(seat)
    with ctx.pose({seat_lift: r.lift_travel}):
        lifted_seat = ctx.part_world_position(seat)
    ctx.check(
        "raising seat_lift moves the seat upward",
        rest_seat is not None
        and lifted_seat is not None
        and lifted_seat[2] > rest_seat[2] + r.lift_travel - 0.005,
        details=f"rest_z={rest_seat[2] if rest_seat else None}, "
        f"lifted_z={lifted_seat[2] if lifted_seat else None}",
    )

    # ---- Swinging an armrest moves its pad footprint. ----
    la_rest = ctx.part_world_aabb(left_arm)
    with ctx.pose({left_swing: left_swing.motion_limits.lower}):
        la_swung = ctx.part_world_aabb(left_arm)
    # Sum the XY drift of BOTH aabb corners: as the pad rotates inward its
    # axis-aligned max corner shrinks while the midline-side (min) corner dives,
    # so the footprint shift is captured by both corners, not the max alone.
    footprint_shift = (
        abs(la_swung[0][0] - la_rest[0][0])
        + abs(la_swung[0][1] - la_rest[0][1])
        + abs(la_swung[1][0] - la_rest[1][0])
        + abs(la_swung[1][1] - la_rest[1][1])
        if (la_rest is not None and la_swung is not None)
        else 0.0
    )
    ctx.check(
        "swinging left arm moves its pad footprint",
        la_rest is not None and la_swung is not None and footprint_shift > 0.08,
        details=f"rest={la_rest}, swung={la_swung}, shift={footprint_shift:.4f}",
    )

    # ---- Two independent wings must never cross the seat midline (motion-QC). ----
    # At the full inward swing of BOTH arms the pads must each stay on their own
    # side of y=0, so the mirrored envelopes cannot interpenetrate. This locks the
    # derived inward-swing limit: restoring the old +/-1.4 would fail here.
    with ctx.pose(
        {left_swing: left_swing.motion_limits.lower, right_swing: right_swing.motion_limits.upper}
    ):
        la_in = ctx.part_world_aabb(left_arm)
        ra_in = ctx.part_world_aabb(right_arm)
    ctx.check(
        "armrests stay clear of the seat midline at full inward swing",
        la_in is not None
        and ra_in is not None
        and la_in[0][1] > 0.0
        and ra_in[1][1] < 0.0
        and (la_in[0][1] - ra_in[1][1]) > 0.008,
        details=f"left_min_y={la_in[0][1] if la_in else None}, "
        f"right_max_y={ra_in[1][1] if ra_in else None}",
    )

    # ---- Backrest-mechanism joint identity. ----
    if r.backrest_mechanism == "reclining_backrest":
        hinge = object_model.get_articulation("seat_to_backrest")
        ctx.check(
            "backrest reclines (revolute -Y)",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and tuple(hinge.axis) == (0.0, -1.0, 0.0),
            details=f"type={hinge.articulation_type}, axis={hinge.axis}",
        )
    elif r.backrest_mechanism == "split_headrest_tilt":
        tilt = object_model.get_articulation("headrest_tilt")
        ctx.check(
            "headrest tilts (revolute +Y)",
            tilt.articulation_type == ArticulationType.REVOLUTE
            and tuple(tilt.axis) == (0.0, 1.0, 0.0),
            details=f"type={tilt.articulation_type}, axis={tilt.axis}",
        )
    elif r.backrest_mechanism == "footrest_legrest":
        hinge = object_model.get_articulation("legrest_hinge")
        ctx.check(
            "legrest swings up (revolute -Y)",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and tuple(hinge.axis) == (0.0, -1.0, 0.0),
            details=f"type={hinge.articulation_type}, axis={hinge.axis}",
        )

    # ---- Compiler-owned baseline (also enforced by the sweep). ----
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    return ctx.report()
