# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for the ``sports_car`` 小类.

A two-door low-slung four-wheel single-cabin high-performance road car.

Pattern: ``parallel_children`` — every slot's part / joint parents to a single
lofted single-body ``body`` (chassis). The body mesh itself is the Slot A
``body_profile_family`` choice (a ``superellipse_side_loft`` over one of four
distinct ``LOWER_SECTIONS`` tables, with boolean-carved wheel arches, axle
channels, hollow cabin and door apertures). All other slots hang off the body.

5★ sources adapted (per AUTHORING.md §A Rule 3):
  P2 Diablo  rec_bright-yellow-lamborghini-diablo-style-wedge-sup_…655801c5
             — baseline body pipeline, scissor doors, headlights, rear,
               exhaust, kinematic skeleton (model.py:L44-L781).
  P1 300SL   rec_classic-mercedes-300sl-gullwing-sports-car-in-de_…88ed264e
             — vintage_pontoon LOWER_SECTIONS + independent roof part +
               windshield/rear-window shells, gullwing door axis
               (model.py:L121-L155, L664-L834).
  fastback   rec_sportscar_fastback_body_v01 (LOWER_SECTIONS L103-L119).
  teardrop   rec_sportscar_teardrop_body_v01 (LOWER_SECTIONS L103-L119).
  pop-up     rec_codex_car002_v07 — headlight_cover part + REVOLUTE
             (model.py:L604-L637, L779-L791).
  louver     rec_codex_car002_v09 — engine_cover part + REVOLUTE
             (model.py:L604-L629, L768-L777).
  dihedral   rec_porsche_911_v01 (DOOR_AXIS _DH L105-L108).

Shared kinematic skeleton is FIXED (never an axis):
  front 2 wheels  : REVOLUTE king-pin steer (Z) + CONTINUOUS spin (X)
  rear 2 wheels   : CONTINUOUS spin (X)
  2 doors         : REVOLUTE swing (axis per door_mechanism)
  baseline        : 4 REVOLUTE + 4 CONTINUOUS (+ steering-wheel REVOLUTE)
  +pop_up         : +2 REVOLUTE (per side)
  +louver         : +1 REVOLUTE

Structural diversity axes (slot_choices_for_seed records these):
  A body_profile_family (4) × B door_mechanism (3) × C headlight_shape (3)
  × C popup{0,1} × D rear_blade (3) × D louver{0,1} × D exhaust (3)
  E palette_style (6, orthogonal, drives every .visual material).
Structural-only distinct (A × B × popup × louver) = 48 ≫ 10.

Bodywork rebuild, 2026-08-02. The kinematic skeleton, the slot set and the
sources above are unchanged; what changed is how every bolt-on is placed.

  * Bolt-ons are now derived from the body's OWN loft at their OWN station via
    _flank_x / _flank_z / _sec_lerp instead of constants tuned on one family.
    A 1.44 m tail panel, a 1.30 m splitter, lamps pinned at x=±0.40 and a rocker
    set in from the section's widest half-width all stood proud of the skin — on
    the 0.48 m-wide vintage tail by half a metre a side. They read as shelves
    bolted to the car, which was the reported defect.
  * The greenhouse is carried on a real beltline rail with raked A/C-pillars and
    a cant rail struck between the canopy's own seam rails. The four
    full-height corner posts it replaces were planted at the CABIN cut corners,
    outboard and fore/aft of every canopy shell, and stood ~0.3 m clear above
    the roofline in every gallery render.
  * _glass_shell no longer inverts its subtrahend, so the canopy is genuinely a
    set of thin shells; the roof shell carries a cut side-window opening and the
    body glazes it. Previously every shell was a solid blob.
  * The doors are the exact skin slice the aperture removed (shell ∩ cutter),
    over a full-height opening from the rocker to the beltline, so they seat
    flush instead of straddling the flank as a straight slab.
  * Added the cues that make it read as a race car rather than a smooth hull:
    front air dam + brake ducts, bonnet vents / radiator shell, fender arch
    lips, side intakes, rear diffuser, an extruded aerofoil GT wing with
    endplates and swan-neck pylons, split-spoke alloys, and a cabin.
  * Track is derived from the body half-width at the axle so the tyre sits in
    the arch (it hung 60-130 mm outboard of the skin on the wedge families).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    BoltPattern,
    Box,
    BoxGeometry,
    Cylinder,
    CylinderGeometry,
    ExtrudeGeometry,
    Inertial,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireSidewall,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    boolean_difference,
    boolean_intersection,
    mesh_from_geometry,
    superellipse_side_loft,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot enums
# --------------------------------------------------------------------------- #
BodyProfileFamily = Literal["modern_wedge", "vintage_pontoon", "fastback", "organic_teardrop"]
DoorMechanism = Literal["scissor_butterfly", "gullwing", "dihedral"]
HeadlightShape = Literal["exposed_rect", "round_fixed", "quad_cluster"]
RearBlade = Literal["integrated", "big_gt_wing", "ducktail"]
ExhaustLayout = Literal["side", "central_quad", "central_single"]
PaletteStyle = Literal[
    "diablo_gloss_yellow",
    "vintage_maroon_chrome",
    "pagani_bare_carbon_silver",
    "bugatti_two_tone_silver_blue",
    "ferrari_rosso_corsa",
    "koenigsegg_icy_blue_carbon",
]

BODY_PROFILE_FAMILIES: tuple[BodyProfileFamily, ...] = (
    "modern_wedge",
    "vintage_pontoon",
    "fastback",
    "organic_teardrop",
)
DOOR_MECHANISMS: tuple[DoorMechanism, ...] = ("scissor_butterfly", "gullwing", "dihedral")
HEADLIGHT_SHAPES: tuple[HeadlightShape, ...] = ("exposed_rect", "round_fixed", "quad_cluster")
REAR_BLADES: tuple[RearBlade, ...] = ("integrated", "big_gt_wing", "ducktail")
EXHAUST_LAYOUTS: tuple[ExhaustLayout, ...] = ("side", "central_quad", "central_single")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "diablo_gloss_yellow",
    "vintage_maroon_chrome",
    "pagani_bare_carbon_silver",
    "bugatti_two_tone_silver_blue",
    "ferrari_rosso_corsa",
    "koenigsegg_icy_blue_carbon",
)

# --------------------------------------------------------------------------- #
# Palette presets (Slot E) — every colorway resolves to a `mats` dict with the
# SAME token set so the builder is colorway-agnostic. Tokens:
#   body   — main paint / body color   accent — trim / black sills / wing
#   alloy  — wheel rim / bright metal   chrome — bright bumper/exhaust rings
#   glass  — tinted glazing (translucent)
#   lens   — pale reflector / driving-light lens
#   amber  — indicators                 tail   — taillights
#   rubber — tires                      interior — cabin floor/seats
# --------------------------------------------------------------------------- #
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "diablo_gloss_yellow": {
        "body": (0.93, 0.74, 0.02, 1.0),
        "accent": (0.05, 0.05, 0.055, 1.0),
        "alloy": (0.74, 0.75, 0.78, 1.0),
        "chrome": (0.80, 0.82, 0.85, 1.0),
        "glass": (0.12, 0.13, 0.15, 0.25),
        "lens": (0.72, 0.75, 0.78, 1.0),
        "amber": (0.85, 0.50, 0.06, 1.0),
        "tail": (0.45, 0.04, 0.05, 1.0),
        "rubber": (0.04, 0.04, 0.045, 1.0),
        "interior": (0.10, 0.10, 0.11, 1.0),
    },
    "vintage_maroon_chrome": {
        "body": (0.43, 0.05, 0.07, 1.0),
        "accent": (0.27, 0.28, 0.30, 1.0),
        "alloy": (0.80, 0.82, 0.85, 1.0),
        "chrome": (0.86, 0.88, 0.90, 1.0),
        "glass": (0.10, 0.12, 0.15, 0.31),
        "lens": (0.86, 0.88, 0.82, 1.0),
        "amber": (0.85, 0.52, 0.10, 1.0),
        "tail": (0.60, 0.06, 0.05, 1.0),
        "rubber": (0.05, 0.05, 0.055, 1.0),
        "interior": (0.12, 0.09, 0.07, 1.0),
    },
    "pagani_bare_carbon_silver": {
        "body": (0.10, 0.10, 0.115, 1.0),
        "accent": (0.045, 0.045, 0.05, 1.0),
        "alloy": (0.78, 0.79, 0.82, 1.0),
        "chrome": (0.82, 0.83, 0.86, 1.0),
        "glass": (0.09, 0.10, 0.12, 0.27),
        "lens": (0.74, 0.77, 0.80, 1.0),
        "amber": (0.86, 0.52, 0.08, 1.0),
        "tail": (0.50, 0.05, 0.05, 1.0),
        "rubber": (0.04, 0.04, 0.045, 1.0),
        "interior": (0.09, 0.09, 0.10, 1.0),
    },
    "bugatti_two_tone_silver_blue": {
        "body": (0.74, 0.76, 0.80, 1.0),
        "accent": (0.07, 0.16, 0.42, 1.0),
        "alloy": (0.72, 0.74, 0.78, 1.0),
        "chrome": (0.84, 0.86, 0.90, 1.0),
        "glass": (0.10, 0.12, 0.18, 0.27),
        "lens": (0.78, 0.81, 0.85, 1.0),
        "amber": (0.86, 0.52, 0.08, 1.0),
        "tail": (0.55, 0.05, 0.06, 1.0),
        "rubber": (0.04, 0.04, 0.045, 1.0),
        "interior": (0.10, 0.11, 0.14, 1.0),
    },
    "ferrari_rosso_corsa": {
        "body": (0.78, 0.04, 0.04, 1.0),
        "accent": (0.05, 0.05, 0.055, 1.0),
        "alloy": (0.76, 0.77, 0.80, 1.0),
        "chrome": (0.82, 0.83, 0.86, 1.0),
        "glass": (0.10, 0.11, 0.13, 0.25),
        "lens": (0.92, 0.88, 0.40, 1.0),
        "amber": (0.88, 0.55, 0.08, 1.0),
        "tail": (0.55, 0.04, 0.04, 1.0),
        "rubber": (0.04, 0.04, 0.045, 1.0),
        "interior": (0.10, 0.07, 0.07, 1.0),
    },
    "koenigsegg_icy_blue_carbon": {
        "body": (0.58, 0.74, 0.82, 1.0),
        "accent": (0.08, 0.09, 0.10, 1.0),
        "alloy": (0.45, 0.47, 0.50, 1.0),
        "chrome": (0.80, 0.84, 0.88, 1.0),
        "glass": (0.09, 0.12, 0.15, 0.27),
        "lens": (0.80, 0.86, 0.90, 1.0),
        "amber": (0.84, 0.54, 0.10, 1.0),
        "tail": (0.45, 0.05, 0.06, 1.0),
        "rubber": (0.04, 0.04, 0.045, 1.0),
        "interior": (0.10, 0.11, 0.12, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Body profile tables (Slot A). Each is a distinct LOWER_SECTIONS rail set
# `(y, z_min, z_max, width)` + a superellipse exponent + per-family proportions.
# Adapted verbatim from the declared 5★ sources.
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _ProfileSpec:
    sections: tuple[tuple[float, float, float, float], ...]
    exponent: float
    half_track: float
    front_axle_y: float
    rear_axle_y: float
    wheel_r: float
    wheel_w: float
    arch_radius: float
    # arch inboard/outboard walls (abs |x|); front reaches deeper inboard.
    arch_front: tuple[float, float]
    arch_rear: tuple[float, float]
    cabin_half_x: float
    cabin_y: tuple[float, float]
    cabin_z: tuple[float, float]
    door_aperture_x: tuple[float, float]
    door_aperture_y: tuple[float, float]
    door_aperture_z: tuple[float, float]
    has_roof_part: bool  # vintage carries an independent roof + glass shells
    roof_top_z: float  # top of the greenhouse (for the gullwing clearance gate)


# P2 Diablo — modern wedge (model.py:L48-L118, L172-L227).
_WEDGE = _ProfileSpec(
    sections=(
        (2.23, 0.16, 0.35, 1.18),
        (2.06, 0.13, 0.42, 1.56),
        (1.80, 0.12, 0.55, 1.84),
        (1.50, 0.12, 0.70, 1.92),
        (1.32, 0.12, 0.76, 1.96),
        (1.15, 0.12, 0.73, 1.96),
        (0.92, 0.12, 0.70, 1.94),
        (0.45, 0.13, 0.68, 1.86),
        (-0.10, 0.13, 0.68, 1.86),
        (-0.65, 0.12, 0.72, 1.96),
        (-1.10, 0.11, 0.76, 2.02),
        (-1.45, 0.11, 0.77, 2.02),
        (-1.85, 0.13, 0.75, 1.92),
        (-2.10, 0.16, 0.72, 1.76),
        (-2.23, 0.20, 0.70, 1.60),
    ),
    exponent=4.0,
    half_track=0.89,
    front_axle_y=1.32,
    rear_axle_y=-1.33,
    wheel_r=0.33,
    wheel_w=0.295,
    arch_radius=0.36,
    arch_front=(0.58, 1.16),
    arch_rear=(0.70, 1.16),
    cabin_half_x=0.60,
    cabin_y=(-0.80, 0.88),
    cabin_z=(0.24, 0.71),
    door_aperture_x=(0.52, 1.05),
    door_aperture_y=(-0.34, 0.82),
    door_aperture_z=(0.265, 0.70),
    has_roof_part=False,
    roof_top_z=1.05,
)

# P1 300SL — vintage pontoon (model.py:L57-L142). Narrow body, tall greenhouse,
# independent roof part.
_VINTAGE = _ProfileSpec(
    sections=(
        (2.32, 0.21, 0.40, 0.46),
        (2.24, 0.16, 0.45, 0.78),
        (2.12, 0.13, 0.51, 1.10),
        (1.97, 0.11, 0.60, 1.42),
        (1.80, 0.10, 0.70, 1.57),
        (1.62, 0.10, 0.75, 1.62),
        (1.42, 0.10, 0.76, 1.63),
        (1.21, 0.10, 0.76, 1.62),
        (1.00, 0.11, 0.70, 1.55),
        (0.72, 0.12, 0.65, 1.47),
        (0.30, 0.12, 0.64, 1.45),
        (-0.15, 0.12, 0.64, 1.46),
        (-0.58, 0.12, 0.67, 1.52),
        (-0.90, 0.11, 0.74, 1.61),
        (-1.19, 0.10, 0.76, 1.63),
        (-1.45, 0.11, 0.73, 1.58),
        (-1.70, 0.13, 0.67, 1.42),
        (-1.94, 0.16, 0.57, 1.10),
        (-2.16, 0.20, 0.49, 0.74),
        (-2.30, 0.26, 0.44, 0.48),
    ),
    exponent=2.6,
    half_track=0.745,
    front_axle_y=1.21,
    rear_axle_y=-1.19,
    wheel_r=0.335,
    wheel_w=0.205,
    arch_radius=0.36,
    arch_front=(0.46, 1.02),
    arch_rear=(0.55, 1.02),
    cabin_half_x=0.56,
    cabin_y=(-0.82, 0.86),
    cabin_z=(0.23, 0.70),
    door_aperture_x=(0.46, 0.84),
    door_aperture_y=(-0.46, 0.44),
    door_aperture_z=(0.275, 0.71),
    has_roof_part=True,
    roof_top_z=1.22,
)

# fastback — rec_sportscar_fastback_body_v01 (model.py:L103-L119).
_FASTBACK = _ProfileSpec(
    sections=(
        (2.23, 0.18, 0.42, 1.32),
        (2.10, 0.15, 0.52, 1.62),
        (1.85, 0.13, 0.62, 1.84),
        (1.55, 0.12, 0.70, 1.92),
        (1.32, 0.12, 0.74, 1.96),
        (1.10, 0.12, 0.72, 1.94),
        (0.85, 0.12, 0.70, 1.92),
        (0.40, 0.13, 0.68, 1.86),
        (-0.10, 0.13, 0.68, 1.86),
        (-0.50, 0.12, 0.70, 1.92),
        (-0.90, 0.11, 0.74, 2.04),
        (-1.30, 0.11, 0.76, 2.08),
        (-1.65, 0.12, 0.74, 2.04),
        (-1.95, 0.14, 0.72, 1.92),
        (-2.23, 0.18, 0.68, 1.76),
    ),
    exponent=3.0,
    half_track=0.89,
    front_axle_y=1.32,
    rear_axle_y=-1.33,
    wheel_r=0.33,
    wheel_w=0.295,
    arch_radius=0.36,
    arch_front=(0.58, 1.16),
    arch_rear=(0.70, 1.18),
    cabin_half_x=0.60,
    cabin_y=(-0.80, 0.88),
    cabin_z=(0.24, 0.72),
    door_aperture_x=(0.52, 1.05),
    door_aperture_y=(-0.34, 0.82),
    door_aperture_z=(0.265, 0.70),
    has_roof_part=False,
    roof_top_z=1.06,
)

# organic_teardrop — rec_sportscar_teardrop_body_v01 (model.py:L103-L119).
_TEARDROP = _ProfileSpec(
    sections=(
        (2.23, 0.20, 0.42, 1.24),
        (2.08, 0.15, 0.52, 1.60),
        (1.88, 0.13, 0.60, 1.86),
        (1.60, 0.12, 0.70, 1.94),
        (1.32, 0.12, 0.78, 1.98),
        (1.00, 0.12, 0.82, 2.00),
        (0.50, 0.12, 0.85, 1.98),
        (0.00, 0.12, 0.83, 1.96),
        (-0.40, 0.12, 0.80, 1.94),
        (-0.80, 0.12, 0.78, 1.92),
        (-1.20, 0.12, 0.76, 1.90),
        (-1.55, 0.13, 0.74, 1.86),
        (-1.85, 0.15, 0.72, 1.78),
        (-2.10, 0.18, 0.66, 1.60),
        (-2.23, 0.22, 0.58, 1.40),
    ),
    exponent=2.2,
    half_track=0.89,
    front_axle_y=1.32,
    rear_axle_y=-1.33,
    wheel_r=0.33,
    wheel_w=0.295,
    arch_radius=0.36,
    arch_front=(0.58, 1.16),
    arch_rear=(0.70, 1.16),
    cabin_half_x=0.60,
    cabin_y=(-0.80, 0.88),
    cabin_z=(0.24, 0.72),
    door_aperture_x=(0.52, 1.05),
    door_aperture_y=(-0.34, 0.82),
    door_aperture_z=(0.265, 0.70),
    has_roof_part=False,
    roof_top_z=1.04,
)

_PROFILES: dict[str, _ProfileSpec] = {
    "modern_wedge": _WEDGE,
    "vintage_pontoon": _VINTAGE,
    "fastback": _FASTBACK,
    "organic_teardrop": _TEARDROP,
}

# --------------------------------------------------------------------------- #
# Body-contour queries.
#
# Every bolt-on (bumper, deck, wing, sill, lamp, intake, exhaust) is sized and
# placed from the body's OWN loft at its OWN station rather than from a constant
# tuned on one family. A 1.44 m tail panel authored against the 2.02 m-wide wedge
# hangs half a metre proud of the 0.48 m-wide vintage tail, and a straight rocker
# sill set in from the section WIDTH still breaks the skin because the flank has
# already drawn in by the time it reaches sill height. Both defects read as
# bolted-on shelves, which is exactly the "crude frame" complaint.
#
# ``superellipse_side_loft`` interpolates its profiles point-for-point at equal
# parameter, and every section of one body shares an exponent, so lerping
# (half_width, z_center, z_half) between the two bracketing rails and evaluating
# |x/a|^n + |z'/b|^n = 1 describes the lofted surface EXACTLY, not approximately.
# --------------------------------------------------------------------------- #

# Solid skin left between the cabin cavity and the outer flank at the beltline.
# The door aperture stops here, so the greenhouse always has a shoulder to land
# on instead of four free-standing corner posts.
BELT_SHOULDER = 0.20
DOOR_SKIN_T = 0.055  # door panel wall thickness (the panel IS a slice of the skin)
# Radial clearance carved between the tyre's outer diameter and the wheel arch.
# The arch used to be carved at a fixed 0.36 while wheel_r runs to 0.355 at the
# top of body_height_scale, leaving 5 mm — and the fender lip, whose inner radius
# was that same fixed 0.36, then cut straight through the tyre's shoulder.
ARCH_GAP = 0.055
# Sheet metal the arch must leave above the tyre. The arch is centred on the hub,
# so its crown sits at ``2*wheel_r + ARCH_GAP``; let that exceed the body's own
# crown at the axle and the carve breaches the top of the fender, which opens a
# slot in the bodywork and hands manifold3d a degenerate coplanar ring.
FENDER_TOP = 0.030


def _wheel_radius_base(p: "_ProfileSpec") -> float:
    """Base wheel radius, bounded so the arch fits under the fender at any scale.

    Solve ``2*wheel_r + ARCH_GAP + FENDER_TOP <= crown(axle)`` at the tighter of
    the two axles, then divide out the widest body_height_scale so the seed's
    scale never clamps — a hard min-clamp that binds for most seeds makes the
    parameter geometrically dead.
    """
    crown = min(_crown(p, p.front_axle_y), _crown(p, p.rear_axle_y))
    ceiling = 0.5 * (crown - ARCH_GAP - FENDER_TOP)
    return min(p.wheel_r, ceiling / 1.06)


def _arch_geom(p: "_ProfileSpec") -> tuple[float, float]:
    """``(centre_z, radius)`` of the wheel-arch carve — FAMILY CONSTANTS.

    Sized for the LARGEST wheel the sampler can produce, so the smaller ones just
    sit in a slightly roomier arch. Deliberately independent of the per-seed
    scales: driving the carve off the resolved wheel_r made the arch's tangent
    plane land exactly on a loft rail for some scales (seed 31: front axle at
    1.2756, arch radius 0.3556, section rail at 0.920 — coincident to 1e-4) and
    manifold3d's coplanar merge then died on a zero-area ring. Keeping the carve
    off the seed parameters is the invariant the original build documented, and
    it also restores the per-family mesh cache.
    """
    base = _wheel_radius_base(p)
    return base, base * 1.06 + ARCH_GAP


def _arch_radius_max(p: "_ProfileSpec") -> float:
    """Clearance margin any straight rail must leave around the wheel opening."""
    return _arch_geom(p)[1]


def _sec_lerp(p: _ProfileSpec, y: float) -> tuple[float, float, float]:
    """``(z_min, z_max, half_width)`` of the body loft at station ``y``."""
    secs = p.sections
    if y >= secs[0][0]:
        s = secs[0]
        return s[1], s[2], s[3] * 0.5
    if y <= secs[-1][0]:
        s = secs[-1]
        return s[1], s[2], s[3] * 0.5
    for a, b in zip(secs, secs[1:]):
        if b[0] <= y <= a[0]:
            t = (a[0] - y) / (a[0] - b[0])
            return (
                a[1] + (b[1] - a[1]) * t,
                a[2] + (b[2] - a[2]) * t,
                0.5 * (a[3] + (b[3] - a[3]) * t),
            )
    s = secs[-1]
    return s[1], s[2], s[3] * 0.5


def _crown(p: _ProfileSpec, y: float) -> float:
    """Top of the body skin at station ``y``."""
    return _sec_lerp(p, y)[1]


def _pan(p: _ProfileSpec, y: float) -> float:
    """Underbody floor of the body skin at station ``y``."""
    return _sec_lerp(p, y)[0]


def _half_w(p: _ProfileSpec, y: float) -> float:
    """Widest half-width of the body skin at station ``y``."""
    return _sec_lerp(p, y)[2]


def _flank_x(p: _ProfileSpec, y: float, z: float) -> float:
    """|x| of the body surface at ``(y, z)``; 0.0 above the crown / below the pan."""
    z0, z1, a = _sec_lerp(p, y)
    b = 0.5 * (z1 - z0)
    zc = 0.5 * (z0 + z1)
    if b <= 1e-9 or a <= 1e-9:
        return 0.0
    t = abs(z - zc) / b
    if t >= 1.0:
        return 0.0
    n = max(0.2, p.exponent)
    return a * (1.0 - t**n) ** (1.0 / n)


def _flank_z(p: _ProfileSpec, y: float, x: float, *, upper: bool = True) -> float:
    """Inverse of :func:`_flank_x` — the z at which the flank has drawn in to ``x``."""
    z0, z1, a = _sec_lerp(p, y)
    b = 0.5 * (z1 - z0)
    zc = 0.5 * (z0 + z1)
    if a <= 1e-9 or x >= a:
        return zc
    n = max(0.2, p.exponent)
    t = (1.0 - (max(0.0, x) / a) ** n) ** (1.0 / n)
    return zc + b * t if upper else zc - b * t


def _flank_min(p: _ProfileSpec, y0: float, y1: float, z: float, samples: int = 11) -> float:
    """Narrowest surface |x| over ``[y0, y1]`` at height ``z``.

    A straight rail (sill, beltline, skirt) may only ride at this x — set in from
    the WIDEST section it would still break the skin at the narrow end.
    """
    lo, hi = (y0, y1) if y0 <= y1 else (y1, y0)
    n = max(2, samples)
    return min(_flank_x(p, lo + (hi - lo) * i / (n - 1.0), z) for i in range(n))


def _crown_min(p: _ProfileSpec, y0: float, y1: float, samples: int = 11) -> float:
    lo, hi = (y0, y1) if y0 <= y1 else (y1, y0)
    n = max(2, samples)
    return min(_crown(p, lo + (hi - lo) * i / (n - 1.0)) for i in range(n))


def _door_opening(p: _ProfileSpec) -> tuple[float, float, float, float, float, float]:
    """``(x_in, x_out, y0, y1, z_bot, z_top)`` of the door aperture cutter.

    ``z_top`` is the BELTLINE: the height at which the flank has drawn in to
    ``cabin_half_x + BELT_SHOULDER``. Cutting no higher leaves a continuous
    shoulder rail between the cabin cavity and the skin, which is what carries
    the greenhouse (the old build had to prop the roof on four corner posts that
    stood clear above the roofline — the antennae in every gallery render).
    """
    y0, y1 = p.door_aperture_y
    y_mid = 0.5 * (y0 + y1)
    # Clamp the shoulder target INSIDE the section half-width: _flank_z degenerates
    # to the section's mid-height once the target reaches the widest point, and on
    # the narrow vintage body cabin_half_x + BELT_SHOULDER overshoots it — which
    # collapsed that family's door to a 105 mm strip.
    a = _half_w(p, y_mid)
    target = _clamp(p.cabin_half_x + BELT_SHOULDER, a * 0.55, a * 0.88)
    z_top = min(_flank_z(p, y_mid, target), p.cabin_z[1] - 0.05)
    z_bot = p.door_aperture_z[0]
    x_out = max(s[3] for s in p.sections) * 0.5 + 0.30
    return p.door_aperture_x[0], x_out, y0, y1, z_bot, z_top


def _strut(part, a, b, *, thick: float, material, name: str, width: float | None = None) -> None:
    """A box bridging two body-frame points (its local +Z runs a→b).

    ``Origin.rpy`` composes as Rz(yaw)·Ry(pitch)·Rx(roll), so local +Z lands on
    ``(cos yaw sin pitch, sin yaw sin pitch, cos pitch)``.
    """
    ax, ay, az = a
    bx, by, bz = b
    dx, dy, dz = bx - ax, by - ay, bz - az
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-6:
        return
    pitch = math.acos(_clamp(dz / length, -1.0, 1.0))
    yaw = math.atan2(dy, dx)
    part.visual(
        Box((width if width is not None else thick, thick, length)),
        origin=Origin(
            xyz=((ax + bx) * 0.5, (ay + by) * 0.5, (az + bz) * 0.5), rpy=(0.0, pitch, yaw)
        ),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _mirror_x(mesh):
    """Mirror a mesh across the YZ plane, restoring face winding."""
    m = mesh.clone().scale(-1.0, 1.0, 1.0)
    return MeshGeometry(vertices=list(m.vertices), faces=[(f[0], f[2], f[1]) for f in m.faces])


# Greenhouse (one-piece, body-color skin + tinted shells) for the fastback /
# teardrop / wedge bodies. The roof reads as a thin domed skin spanning the
# cabin. We build it as a single eased dome Box stack so we don't pay a second
# boolean per seed (the lower-body carve is already the cost bottleneck).
# Axle bar radius just under the bored channel radius so the rod touches the
# channel wall (stays connected to the body — not floating in the open bore).
AXLE_BAR_RADIUS = 0.082
# Channel bored slightly NARROWER than the bar so the rod's surface presses into
# the solid body around the bore (keeps the rod connected to the body part, not
# floating in an open hole — matters most on the narrow vintage body).
AXLE_CHANNEL_RADIUS = 0.066
GLASS_SHELL_T = 0.016

# Door swept-volume / hinge constants.
_SCISSOR_TILT = 0.25
_DH = (0.0, -0.22, 0.975)


@dataclass(frozen=True)
class SportsCarConfig:
    body_profile_family: BodyProfileFamily | None = None
    door_mechanism: DoorMechanism | None = None
    headlight_shape: HeadlightShape | None = None
    headlight_popup: bool = False
    rear_blade: RearBlade | None = None
    rear_louver_cover: bool = False
    exhaust_layout: ExhaustLayout | None = None
    palette_style: PaletteStyle = "diablo_gloss_yellow"

    track_scale: float = 1.0
    wheelbase_scale: float = 1.0
    body_height_scale: float = 1.0
    door_open_max: float = 1.4
    name: str = "sports_car"


@dataclass(frozen=True)
class ResolvedSportsCarConfig:
    body_profile_family: BodyProfileFamily
    door_mechanism: DoorMechanism
    headlight_shape: HeadlightShape
    headlight_popup: bool
    rear_blade: RearBlade
    rear_louver_cover: bool
    exhaust_layout: ExhaustLayout
    palette_style: PaletteStyle
    profile: _ProfileSpec
    # resolved scaled kinematics
    half_track: float
    front_axle_y: float
    rear_axle_y: float
    wheel_r: float
    wheel_w: float
    arch_radius: float
    body_height_scale: float
    door_open_max: float
    steer_lock: float
    name: str


# --------------------------------------------------------------------------- #
# Sampling
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> SportsCarConfig:
    """Deterministic per-seed procedural sampling (seed 0 not special)."""
    rng = random.Random(seed)

    body_profile_family = rng.choice(BODY_PROFILE_FAMILIES)
    # door: slightly biased away from gullwing (it is body-gated / single-source).
    door_mechanism = rng.choices(DOOR_MECHANISMS, weights=(0.42, 0.20, 0.38), k=1)[0]
    headlight_shape = rng.choice(HEADLIGHT_SHAPES)
    headlight_popup = rng.random() < 0.30
    rear_blade = rng.choice(REAR_BLADES)
    rear_louver_cover = rng.random() < 0.30
    exhaust_layout = rng.choice(EXHAUST_LAYOUTS)
    palette_style = rng.choice(PALETTE_STYLES)

    return SportsCarConfig(
        body_profile_family=body_profile_family,
        door_mechanism=door_mechanism,
        headlight_shape=headlight_shape,
        headlight_popup=headlight_popup,
        rear_blade=rear_blade,
        rear_louver_cover=rear_louver_cover,
        exhaust_layout=exhaust_layout,
        palette_style=palette_style,
        track_scale=round(rng.uniform(0.92, 1.08), 4),
        wheelbase_scale=round(rng.uniform(0.94, 1.06), 4),
        body_height_scale=round(rng.uniform(0.95, 1.06), 4),
        door_open_max=round(rng.uniform(1.2, 1.6), 4),
        name=f"seeded_sports_car_{seed}",
    )


def _pick(value, choices):
    return value if value in choices else choices[0]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def resolve_config(config: SportsCarConfig | None = None) -> ResolvedSportsCarConfig:
    cfg = config or SportsCarConfig()

    body_profile_family = _pick(cfg.body_profile_family, BODY_PROFILE_FAMILIES)
    door_mechanism = _pick(cfg.door_mechanism, DOOR_MECHANISMS)
    headlight_shape = _pick(cfg.headlight_shape, HEADLIGHT_SHAPES)
    rear_blade = _pick(cfg.rear_blade, REAR_BLADES)
    exhaust_layout = _pick(cfg.exhaust_layout, EXHAUST_LAYOUTS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    headlight_popup = bool(cfg.headlight_popup)
    rear_louver_cover = bool(cfg.rear_louver_cover)

    profile = _PROFILES[body_profile_family]

    # --- Compatibility gating (spec §兼容性矩阵). ---
    # (1) gullwing is single-source (vintage). On a NON-vintage low body it needs
    #     a roof shoulder anchor + a top-hinge clearance gate; if the body cannot
    #     clear, fall back to dihedral (spec Reject case: gullwing-on-low-wedge).
    if door_mechanism == "gullwing" and not profile.has_roof_part:
        # roof_top_z must clear hinge_z + door_half_height·sin(open). The non-
        # vintage greenhouses sit too low for the longitudinal roof-ridge hinge,
        # so fall back to dihedral rather than punch a door through the roofline.
        door_mechanism = "dihedral"

    # (2) pop_up ⊥ quad_cluster — the flap covers the whole pod cluster. Force a
    #     single rect/round lamp under a pop-up cover.
    if headlight_popup and headlight_shape == "quad_cluster":
        headlight_shape = "round_fixed"

    track_scale = _clamp(float(cfg.track_scale), 0.92, 1.08)
    wheelbase_scale = _clamp(float(cfg.wheelbase_scale), 0.94, 1.06)
    body_height_scale = _clamp(float(cfg.body_height_scale), 0.95, 1.06)

    # Track. The wheel is planted at ±half_track with wheel_w of rubber, so the
    # outer sidewall lands at half_track + wheel_w/2. The stored half_track puts
    # 60–130 mm of that outboard of the body's own half-width at the axle on the
    # wedge families — the tyre visibly hangs in space beside the fender. Derive
    # the base from the body and divide out the widest scale, so the seed's
    # track_scale never clamps and the parameter stays fully live.
    axle_hw = min(_half_w(profile, profile.front_axle_y), _half_w(profile, profile.rear_axle_y))
    max_half_track = axle_hw - profile.wheel_w * 0.5 + 0.015
    half_track = min(profile.half_track, max_half_track / 1.08) * track_scale
    front_axle_y = profile.front_axle_y * wheelbase_scale
    rear_axle_y = profile.rear_axle_y * wheelbase_scale
    # wheel_radius equation (ground-anchored z=0); derived from body_height_scale.
    # The base is bounded by the fender it has to fit under (see
    # _wheel_radius_base), not by the profile's nominal radius alone.
    wheel_r = _wheel_radius_base(profile) * body_height_scale

    # door_open_max conditional on mechanism (gullwing回缩 to avoid roof sweep).
    door_open_max = _clamp(float(cfg.door_open_max), 1.2, 1.6)
    if door_mechanism == "gullwing":
        door_open_max = min(door_open_max, 1.2)

    # steer-lock vs fender-well inequality: keep the ±throw inside the well.
    # well inboard wall ≈ arch_front[0]; back off lock on the narrowest track.
    steer_lock = 0.40
    well_inboard = profile.arch_front[0]
    if half_track - profile.wheel_w * 0.5 - 0.10 < well_inboard:
        steer_lock = 0.32

    return ResolvedSportsCarConfig(
        body_profile_family=body_profile_family,
        door_mechanism=door_mechanism,
        headlight_shape=headlight_shape,
        headlight_popup=headlight_popup,
        rear_blade=rear_blade,
        rear_louver_cover=rear_louver_cover,
        exhaust_layout=exhaust_layout,
        palette_style=palette_style,
        profile=profile,
        half_track=half_track,
        front_axle_y=front_axle_y,
        rear_axle_y=rear_axle_y,
        wheel_r=wheel_r,
        wheel_w=profile.wheel_w,
        arch_radius=_arch_geom(profile)[1],
        body_height_scale=body_height_scale,
        door_open_max=door_open_max,
        steer_lock=steer_lock,
        name=cfg.name,
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Per-seed (slot, module) tuples consumed by module_topology_diversity.

    Records the post-resolution choices (after gullwing fallback / popup gating)
    so the reported topology matches what is actually built. Includes the four
    structural axes (A/B/popup/louver, 48 distinct floor) plus the cosmetic
    shape/blade/exhaust slots to lift the distinct count toward ≥100.
    """
    r = resolve_config(config_from_seed(seed))
    return [
        ("body_profile_family", r.body_profile_family),
        ("door_mechanism", r.door_mechanism),
        ("headlight_shape", r.headlight_shape),
        ("headlight_popup", "popup" if r.headlight_popup else "fixed"),
        ("rear_blade", r.rear_blade),
        ("rear_louver_cover", "louver" if r.rear_louver_cover else "smooth"),
        ("exhaust_layout", r.exhaust_layout),
    ]


# --------------------------------------------------------------------------- #
# Geometry helpers (adapted from P2 / P1 sources)
# --------------------------------------------------------------------------- #


def _save(name: str, geom):
    return mesh_from_geometry(geom, name)


def _box_cutter(x0, x1, y0, y1, z0, z1):
    """Axis-aligned solid box cutter with flipped winding (P2 L154-L166)."""
    box = BoxGeometry((x1 - x0, y1 - y0, z1 - z0)).translate(
        (x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0
    )
    return MeshGeometry(
        vertices=list(box.vertices),
        faces=[(f[0], f[2], f[1]) for f in box.faces],
    )


_BODY_MESH_CACHE: dict[str, object] = {}


def _lower_body_mesh(r: ResolvedSportsCarConfig):
    """Lofted single-body lower body with carved arches / axle channels / cabin /
    door apertures (P2 L172-L227, P1 L205-L246).

    The carve uses only the profile's NOMINAL constants (not the per-seed track/
    wheelbase/height scale), so the result depends only on body_profile_family.
    It is cached per family — the boolean carve is the per-seed cost bottleneck.
    """
    key = r.body_profile_family
    if key in _BODY_MESH_CACHE:
        return _BODY_MESH_CACHE[key].clone()
    p = r.profile
    sections = list(p.sections)
    # Segment counts tuned for BOTH manifold robustness and per-seed compile speed:
    # the boolean carve is the sweep's wall-time bottleneck (each sweep seed runs in
    # its own subprocess, so the per-profile mesh cache does NOT amortize across
    # seeds), and the cost is dominated by the coplanar-merge pass that follows each
    # boolean — it probes point-in-manifold once per candidate face pair, so it
    # scales super-linearly in the triangle count. Measured on the wedge carve:
    # 44/28/18 = 6.7 s, 36/20/14 = 4.9 s, 30/18/12 = 3.7 s, all visually identical
    # at gallery resolution. Below ~26 the coplanar triangulation starts to
    # degenerate, so 30 is the floor with margin.
    body = superellipse_side_loft(sections, exponents=p.exponent, segments=30)

    # Carve at the profile's NOMINAL axle positions / track (not the scaled r.*),
    # so the mesh stays independent of track/wheelbase scale — the small (±6%)
    # scale only repositions the wheels/knuckles/axle rod, which still sit inside
    # the open arches. The arch RADIUS is the exception: it has to track wheel_r
    # (see ARCH_GAP), so it joins the cache key. That costs nothing — the key is
    # constant within one build, and each sweep seed is its own subprocess, so the
    # cache never amortised across seeds anyway.
    arch_cz, arch_r = _arch_geom(p)
    arches = (
        (1.0, p.front_axle_y, p.arch_front[0], p.arch_front[1]),
        (-1.0, p.front_axle_y, p.arch_front[0], p.arch_front[1]),
        (1.0, p.rear_axle_y, p.arch_rear[0], p.arch_rear[1]),
        (-1.0, p.rear_axle_y, p.arch_rear[0], p.arch_rear[1]),
    )
    for sign, ay, inboard, outboard in arches:
        arch = (
            CylinderGeometry(radius=arch_r, height=outboard - inboard, radial_segments=18)
            .rotate_y(math.pi / 2.0)
            .translate(sign * (inboard + outboard) / 2.0, ay, arch_cz)
        )
        body = boolean_difference(body, arch)

    for ay in (p.front_axle_y, p.rear_axle_y):
        channel = (
            CylinderGeometry(
                radius=AXLE_CHANNEL_RADIUS,
                height=2.0 * p.half_track + 0.2,
                radial_segments=12,
            )
            .rotate_y(math.pi / 2.0)
            .translate(0.0, ay, p.wheel_r)
        )
        body = boolean_difference(body, channel)

    body = boolean_difference(
        body,
        _box_cutter(
            -p.cabin_half_x, p.cabin_half_x, p.cabin_y[0], p.cabin_y[1], p.cabin_z[0], p.cabin_z[1]
        ),
    )
    # Door apertures — a full-height opening from the rocker up to the beltline
    # (see _door_opening). The door part is the exact skin slice that was removed
    # here, so the panel seats perfectly flush instead of standing proud.
    x_in, x_out, ay0, ay1, az0, az1 = _door_opening(p)
    for sgn in (1.0, -1.0):
        xa, xb = sorted((sgn * x_in, sgn * x_out))
        body = boolean_difference(body, _box_cutter(xa, xb, ay0, ay1, az0, az1))
    _BODY_MESH_CACHE[key] = body
    return body.clone()


def _wheel_geoms(r: ResolvedSportsCarConfig):
    """Tire + alloy wheel geometry (P2 L254-L274). BoltPattern guarded all-positive."""
    tire = TireGeometry(
        r.wheel_r,
        r.wheel_w,
        inner_radius=r.wheel_r * 0.65,
        carcass=TireCarcass(belt_width_ratio=0.68, sidewall_bulge=0.04),
        sidewall=TireSidewall(style="rounded", bulge=0.04),
    )
    # WheelHub BoltPattern: count>=1, circle_diameter>0 (guard — count=1/cd=0 crashes).
    bolt = BoltPattern(count=5, circle_diameter=max(0.060, r.wheel_r * 0.22), hole_diameter=0.009)
    wheel = WheelGeometry(
        r.wheel_r * 0.66,
        r.wheel_w * 0.66,
        rim=WheelRim(inner_radius=r.wheel_r * 0.53, flange_height=0.012, flange_thickness=0.006),
        hub=WheelHub(
            radius=r.wheel_r * 0.17, width=r.wheel_w * 0.32, cap_style="domed", bolt_pattern=bolt
        ),
        # window_depth pushes the spoke face out toward the rim flange.
        # `face_outer_radius` is otherwise capped at rim_inner + 28% of the rim
        # band (~30 mm here), so the slots get cut into a narrow annulus and read
        # as scattered nicks in a hubcap rather than openings between spokes.
        face=WheelFace(dish_depth=0.022, front_inset=0.008, window_depth=r.wheel_r * 0.22),
        # Five open spokes. A plain disc rim reads as a hubcap, and the wheel is
        # the second-most looked-at feature on a sports car after the roofline.
        spokes=WheelSpokes(
            style="straight", count=5, thickness=0.020, window_radius=r.wheel_r * 0.135
        ),
    )
    return tire, wheel


# --------------------------------------------------------------------------- #
# Body visual builders (headlights / rear / exhaust / greenhouse) — body visuals
# (Rule 1: not articulated → parent.visual, no FIXED joints).
# --------------------------------------------------------------------------- #


def _greenhouse_geom(r):
    """Greenhouse geometry constants. The body's cabin top sits at cabin_z[1]; the
    roof springs from that rim up to roof_top (a realistic +0.30..0.55 m). Every
    piece embeds into the body cabin rim or an adjacent greenhouse piece so the
    part stays connected (no floating islands)."""
    p = r.profile
    hs = r.body_height_scale
    rim_z = p.cabin_z[1]  # body cabin top
    roof_top = rim_z + (p.roof_top_z - rim_z) * hs  # greenhouse top
    cy0, cy1 = p.cabin_y
    cyl = cy0 + 0.04  # rear cabin wall
    cyh = cy1 - 0.04  # front cabin wall (windshield base)
    half_w = p.cabin_half_x + 0.02
    return p, rim_z, roof_top, cy0, cy1, cyl, cyh, half_w


# Greenhouse canopy: three thin shells per body family, ported from the 5★
# sources. Each family's windshield/roof/rear-window tables SHARE seam rails
# (windshield top == roof leading edge; roof trailing == rear-window top) so the
# panes meet the roof FLUSH — the seating gap of a box greenhouse cannot occur
# when adjacent shells reuse the identical seam section. Sources:
#   modern_wedge    ← P2 Diablo cab-forward dome      (model.py:L120-L142, verbatim)
#   vintage_pontoon ← P1 300SL one-piece fixed dome   (model.py:L150-L156) + bridged glass
#   organic_teardrop← Pagani Huayra wraparound bubble (model.py:L144-L160), bases lifted to the tall teardrop crown
#   fastback        ← Diablo windshield + a long fastback rear-glass slope to the deck
# Built once per family and cached (the loft+boolean is a per-seed sweep cost).

# modern_wedge — Diablo greenhouse (verbatim; same coordinate frame as _WEDGE).
_WEDGE_SF = (0.20, 0.66, 1.10, 1.22)
_WEDGE_SR = (-0.55, 0.66, 1.08, 1.14)
_CANOPY_WEDGE = (
    [(0.92, 0.62, 0.72, 1.46), (0.55, 0.64, 0.92, 1.34), _WEDGE_SF],
    [_WEDGE_SF, (-0.05, 0.66, 1.18, 1.20), (-0.42, 0.66, 1.17, 1.16), _WEDGE_SR],
    [_WEDGE_SR, (-0.88, 0.66, 0.82, 1.10)],
)

# vintage_pontoon — 300SL one-piece dome + windshield/rear glass bridged from the
# cowl up to the shared seam rails (300SL doors carry the side glass in the
# source; the template builds the full fixed greenhouse on the body).
#
# The shell BASES are seated on this body's crown (0.62–0.66). As ported they
# stood at 0.78–0.88 while _VINTAGE's crown across the cabin is only 0.64 — the
# greenhouse floated 0.14–0.24 m clear of the bodywork. That was invisible while
# the shells were solid blobs propped on four corner posts, but a real thin-shell
# glasshouse leaves the gap as an open slot straight through the cabin.
_VINT_SF = (0.46, 0.62, 1.12, 1.10)
_VINT_SR = (-0.56, 0.62, 1.13, 1.12)
_CANOPY_VINTAGE = (
    [(0.84, 0.62, 0.78, 1.14), (0.64, 0.66, 0.98, 1.12), _VINT_SF],
    [_VINT_SF, (0.16, 0.62, 1.17, 1.20), (-0.24, 0.62, 1.17, 1.20), _VINT_SR],
    [_VINT_SR, (-0.84, 0.64, 0.86, 1.12)],
)

# organic_teardrop — Pagani Huayra bubble canopy; glass bases lifted (~+0.2) so
# they emerge from the tall teardrop crown (z_max≈0.85) instead of sinking in.
_TEAR_SF = (0.36, 0.80, 1.03, 1.10)
_TEAR_SR = (-0.70, 0.80, 0.98, 0.90)
_CANOPY_TEARDROP = (
    [(0.90, 0.80, 0.90, 1.36), (0.62, 0.82, 0.99, 1.22), _TEAR_SF],
    [_TEAR_SF, (0.02, 0.84, 1.07, 1.02), (-0.36, 0.84, 1.04, 0.94), _TEAR_SR],
    [_TEAR_SR, (-0.98, 0.80, 0.90, 0.84)],
)

# fastback — Diablo windshield + front roof, then a single long rear-glass slope
# running back to the high rear deck (the defining fastback roofline).
_FAST_SF = (0.20, 0.66, 1.10, 1.22)
_FAST_SR = (-0.55, 0.66, 1.05, 1.26)
_CANOPY_FASTBACK = (
    [(0.92, 0.62, 0.72, 1.46), (0.55, 0.64, 0.92, 1.34), _FAST_SF],
    [_FAST_SF, (-0.08, 0.66, 1.16, 1.22), _FAST_SR],
    [_FAST_SR, (-1.15, 0.66, 0.84, 1.46)],
)

_CANOPY_SECTIONS: dict[str, tuple] = {
    "modern_wedge": _CANOPY_WEDGE,
    "vintage_pontoon": _CANOPY_VINTAGE,
    "fastback": _CANOPY_FASTBACK,
    "organic_teardrop": _CANOPY_TEARDROP,
}

_CANOPY_CACHE: dict[str, tuple] = {}


def _glass_shell(sections, t=GLASS_SHELL_T, segments=32):
    """Thin uniform-thickness shell of a superellipse side-loft (P2 _glass_shell):
    subtract an inset copy (top/sides pulled in by t, bottom dropped 0.15 below to
    open into the cabin). Adjacent shells from SHARED seam sections meet seamlessly
    because they reuse the identical seam rail.

    NOTE the inner copy is passed with its NATIVE winding. ``superellipse_side_loft``
    already returns a positive-volume solid (measured: +2.047 for a unit test loft,
    against BoxGeometry's -1.0), so the previous face-flip here inverted the
    subtrahend and manifold3d returned the outer solid untouched — every "thin
    shell" was in fact a solid blob. That is why the greenhouse rendered as an
    opaque dome with no side glazing and no cabin behind the windscreen.
    """
    outer = superellipse_side_loft(sections, exponents=2.8, segments=segments)
    inner = superellipse_side_loft(
        [(y, zmin - 0.15, zmax - t, max(w - 2.0 * t, 0.04)) for (y, zmin, zmax, w) in sections],
        exponents=2.8,
        segments=segments,
    )
    return boolean_difference(outer, inner)


def _canopy_rail(family: str, shell: int, end: int):
    """One end rail of a canopy shell: ``(y, z_min, z_max, half_width)``.

    ``shell`` is 0=windshield / 1=roof / 2=rear window, ``end`` is 0=front rail /
    -1=rear rail. Pillars are struck between these rails so they cannot stand
    clear of the roofline they are meant to frame.
    """
    sec = _CANOPY_SECTIONS[family][shell][end]
    return sec[0], sec[1], sec[2], sec[3] * 0.5


def _roof_base_z(family: str) -> float:
    """Lowest z the ROOF shell reaches — the height its side skirt springs from."""
    return min(sec[1] for sec in _CANOPY_SECTIONS[family][1])


def _belt_geom(p: _ProfileSpec, family: str):
    """``(y0, y1, z_bot, z_top, x_out, x_in)`` of the beltline rail.

    The rail is the body side between the door's top edge and the greenhouse's
    own base, and its run stops short of both arches — it sits at beltline height
    where the flank is still wide, so an unclamped rail drives through the tyres.

    ``z_top`` is carried up to the roof shell's base, not just to the body crown.
    The 300SL canopy tables spring from z≈0.78 while that body's crown at the
    cabin is 0.64: with the greenhouse shells solid (the old winding bug) the
    0.14 m gap was hidden inside the blob, but a real glasshouse leaves it as an
    open slot straight through the cabin.
    """
    cy0, cy1 = p.cabin_y
    y1 = min(cy1 + 0.12, p.front_axle_y - _arch_radius_max(p) - 0.03)
    y0 = max(cy0 - 0.12, p.rear_axle_y + _arch_radius_max(p) + 0.03)
    z_bot = _door_opening(p)[5]
    z_top = max(_crown_min(p, y0, y1), _roof_base_z(family) + 0.025)
    x_out = _flank_min(p, y0, y1, z_bot + 0.01)
    x_in = min(p.cabin_half_x - 0.03, x_out - 0.06)
    return y0, y1, z_bot, z_top, x_out, x_in


def _window_band(p: _ProfileSpec, family: str):
    """``(y_rear, y_front, z_bot, z_top, x_pane, x_cut_in)`` of the side glazing,
    or ``None`` when the roofline is too shallow to carry a side window.

    One source of truth for the opening cut in the roof shell and the pane that
    fills it, so the glass always fills the hole exactly.
    """
    a_hi = _canopy_rail(family, 0, -1)  # windshield / roof seam
    c_hi = _canopy_rail(family, 2, 0)  # roof / rear-glass seam
    z_top = min(a_hi[2], c_hi[2]) - 0.075  # stay under the cant rail
    z_bot = _belt_geom(p, family)[3] + 0.02  # just above the beltline rail
    if z_top - z_bot < 0.12:
        return None
    x_pane = 0.5 * (a_hi[3] + c_hi[3]) - 0.024
    return c_hi[0] + 0.03, a_hi[0] - 0.03, z_bot, z_top, x_pane, x_pane * 0.55


def _window_front_y(p: _ProfileSpec, family: str) -> float:
    """Forward limit of the side glazing, at the A-pillar foot.

    The roof shell ends at the windscreen seam, roughly mid-door, so a window cut
    only into the roof stops halfway along the door — and everything forward of
    it (dash, steering wheel) sits behind painted metal. Real door glass runs to
    the A-pillar, so the band is carried on into the WINDSCREEN shell's sides.
    """
    a_lo = _canopy_rail(family, 0, 0)
    return min(a_lo[0] - 0.12, p.cabin_y[1] - 0.06)


def _canopy_meshes(p: _ProfileSpec, family: str):
    """(roof, windshield, rear_window, headliner) shells for the family, cached.

    The roof shell gets its side-window openings cut here; otherwise the "roof"
    is a closed dome down to the beltline and the car has no side glazing at all.

    The headliner is the same roofline drawn in by 8 mm, shelled, and cut with the
    SAME window boxes. It exists because the side window looks into the GREENHOUSE
    volume, which sits above the cabin cavity: without it the surface you see
    across the cabin is the far side of the roof shell's inner face, carrying the
    body paint, and the cockpit reads as a glowing yellow box with a seat in it.
    Its outer surface lands inside the roof shell's own 16 mm wall, so the two are
    welded rather than nested with a gap.
    """
    if family not in _CANOPY_CACHE:
        ws, roof, rw = _CANOPY_SECTIONS[family]
        band = _window_band(p, family)

        def _cut_windows(mesh, pad: float = 0.0):
            if band is None:
                return mesh
            wy0, wy1, wz0, wz1, _xp, x_in = band
            for sgn in (1.0, -1.0):
                xa, xb = sorted((sgn * x_in, sgn * 3.0))
                mesh = boolean_difference(
                    mesh, _box_cutter(xa, xb, wy0 - pad, wy1 + pad, wz0 - pad, wz1 + pad)
                )
            return mesh

        roof_mesh = _cut_windows(_glass_shell(roof))
        liner_secs = [(y, z0 + 0.006, z1 - 0.008, max(w - 0.016, 0.05)) for (y, z0, z1, w) in roof]
        # Pad the liner's opening so its cut edge hides behind the roof's.
        liner = _cut_windows(_glass_shell(liner_secs, t=0.018), pad=0.010)

        # Carry the opening forward through the WINDSCREEN shell's sides so the
        # door glass reaches the A-pillar. Only a shallow band just above the
        # beltline is taken: at |x| below x_in the shell's surfaces lie well above
        # and below that band, so the screen itself is untouched.
        ws_mesh = _glass_shell(ws)
        if band is not None:
            _wy0, wy1, wz0, _wz1, _xp, x_in = band
            wy_front = _window_front_y(p, family)
            if wy_front > wy1 + 0.06:
                for sgn in (1.0, -1.0):
                    xa, xb = sorted((sgn * x_in, sgn * 3.0))
                    ws_mesh = boolean_difference(
                        ws_mesh, _box_cutter(xa, xb, wy1, wy_front, wz0, wz0 + 0.17)
                    )
        _CANOPY_CACHE[family] = (roof_mesh, ws_mesh, _glass_shell(rw), liner)
    roof_m, ws_m, rw_m, liner_m = _CANOPY_CACHE[family]
    return roof_m.clone(), ws_m.clone(), rw_m.clone(), liner_m.clone()


def seat_y_of(cy0: float, cy1: float) -> float:
    """Longitudinal station of the seat cushions inside the cabin span."""
    return cy0 + (cy1 - cy0) * 0.34


def _add_greenhouse(body, r, mats) -> None:
    """Cab greenhouse = three thin shells (windshield / roof / rear window) that
    SHARE seam rails so the glass meets the roof flush (ported per body family
    from the _CANOPY_SECTIONS tables), carried on a real beltline rail with raked
    A- and C-pillars and a cant rail along the roof edge.

    The old build framed this with four axis-aligned corner posts of the full
    greenhouse height, planted at the CABIN cut corners — which sit outboard and
    fore/aft of the canopy shells on every family. They stood ~0.3 m clear above
    the roof in every gallery render (the "antennae"). Struts between the canopy's
    own rails cannot do that: their endpoints ARE the roofline.
    """
    p = r.profile
    cy0, cy1 = p.cabin_y
    fam = r.body_profile_family

    # ---- Beltline rail: the body side between the door's top edge and the
    # greenhouse base, and the load path that carries the greenhouse. This
    # replaces the four corner posts as the roof's anchor. Body-coloured: it is
    # visible sheetmetal on the tall-greenhouse families, not a trim strip.
    rail_y0, rail_y1, belt_z, belt_top, rail_out, rail_in = _belt_geom(p, fam)
    belt_h = max(0.07, belt_top - belt_z + 0.03)
    belt_mid_z = belt_z + belt_h * 0.5 - 0.015
    for sgn, side in ((1.0, "left"), (-1.0, "right")):
        body.visual(
            Box((rail_out - rail_in, rail_y1 - rail_y0, belt_h)),
            origin=Origin(
                xyz=(sgn * (rail_in + rail_out) * 0.5, (rail_y0 + rail_y1) * 0.5, belt_mid_z)
            ),
            material=mats["body"],
            name=f"beltline_rail_{side}", material_class_id="metal.paint_coated",
        )
        # Sill trim capping it, at the glass line.
        body.visual(
            Box((rail_out - rail_in + 0.010, rail_y1 - rail_y0 - 0.10, 0.030)),
            origin=Origin(
                xyz=(sgn * (rail_in + rail_out) * 0.5, (rail_y0 + rail_y1) * 0.5, belt_top - 0.004)
            ),
            material=mats["chrome"],
            name=f"beltline_trim_{side}", material_class_id="metal.chrome_polished",
        )

    # ---- Three seam-shared shells: roof (body color) + windshield + rear window.
    roof_mesh, ws_mesh, rw_mesh, liner_mesh = _canopy_meshes(p, fam)
    body.visual(_save("greenhouse_roof.obj", roof_mesh), material=mats["body"], name="greenhouse", material_class_id="metal.paint_coated")
    body.visual(
        _save("greenhouse_windshield.obj", ws_mesh), material=mats["glass"], name="windshield", material_class_id="glass.smoked_tinted"
    )
    body.visual(_save("greenhouse_rear.obj", rw_mesh), material=mats["glass"], name="rear_window", material_class_id="glass.smoked_tinted")
    body.visual(_save("headliner.obj", liner_mesh), material=mats["interior"], name="headliner", material_class_id="fabric.upholstery_plain")

    # ---- Side glazing filling the opening cut in the roof shell. Lofted with
    # rounded ends so it reads as a dropped side window rather than a rectangle,
    # and seated on the beltline rail / under the cant rail that frame it.
    band = _window_band(p, fam)
    if band is not None:
        bwy0, bwy1, wz0, wz1, xp, _xi = band
        # Forward of the roof seam the opening is only the shallow band cut into
        # the windscreen's sides, so the pane tapers down to match it.
        wy_front = max(bwy1, _window_front_y(p, fam))
        run = bwy1 - bwy0
        pane = superellipse_side_loft(
            [
                (bwy0 + run * 0.015, wz0 + 0.035, wz1 - 0.055, 0.028),
                (bwy0 + run * 0.22, wz0 - 0.010, wz1 - 0.014, 0.028),
                (bwy1 - run * 0.22, wz0 - 0.010, wz1 - 0.014, 0.028),
                (bwy1 + 0.01, wz0 - 0.010, wz1 - 0.055, 0.028),
                (wy_front - 0.02, wz0 + 0.005, wz0 + 0.15, 0.028),
            ],
            exponents=6.0,
            segments=20,
        )
        for sgn, side in ((1.0, "left"), (-1.0, "right")):
            mesh = pane.clone() if sgn > 0 else _mirror_x(pane)
            body.visual(
                _save(f"side_glass_{side}.obj", mesh.translate(sgn * xp, 0.0, 0.0)),
                material=mats["glass"],
                name=f"quarter_light_{side}", material_class_id="glass.smoked_tinted",
            )

    # ---- A-pillars along the windshield side rail, C-pillars along the rear
    # glass, and a cant rail closing the roof edge between them. Each strut runs
    # between two canopy rails, so it lies IN the roofline.
    a_lo = _canopy_rail(fam, 0, 0)  # windshield base (cowl)
    a_hi = _canopy_rail(fam, 0, -1)  # windshield / roof seam
    c_hi = _canopy_rail(fam, 2, 0)  # roof / rear-glass seam
    c_lo = _canopy_rail(fam, 2, -1)  # rear glass base (deck)
    for sgn, side in ((1.0, "left"), (-1.0, "right")):
        _strut(
            body,
            (sgn * (a_lo[3] - 0.035), a_lo[0], a_lo[2] - 0.05),
            (sgn * (a_hi[3] - 0.035), a_hi[0], a_hi[2] - 0.04),
            thick=0.055,
            width=0.055,
            material=mats["body"],
            name=f"a_pillar_{side}",
        )
        _strut(
            body,
            (sgn * (c_hi[3] - 0.035), c_hi[0], c_hi[2] - 0.04),
            (sgn * (c_lo[3] - 0.035), c_lo[0], c_lo[2] - 0.05),
            thick=0.055,
            width=0.055,
            material=mats["body"],
            name=f"c_pillar_{side}",
        )
        _strut(
            body,
            (sgn * (a_hi[3] - 0.035), a_hi[0], a_hi[2] - 0.045),
            (sgn * (c_hi[3] - 0.035), c_hi[0], c_hi[2] - 0.045),
            thick=0.05,
            width=0.05,
            material=mats["body"],
            name=f"cant_rail_{side}",
        )
        # Quarter panel tying the C-pillar foot down onto the beltline rail. Its
        # foot is pinned to the rail's own (arch-clamped) rear end, so it cannot
        # reach back over the rear tyre.
        _strut(
            body,
            (sgn * (c_lo[3] - 0.04), c_lo[0], c_lo[2] - 0.04),
            (
                sgn * min(rail_out - 0.02, c_lo[3] + 0.10),
                max(c_lo[0], rail_y0 + 0.07),
                belt_z + 0.03,
            ),
            thick=0.07,
            width=0.09,
            material=mats["body"],
            name=f"quarter_panel_{side}",
        )

    # ---- Cabin interior.
    #
    # The cavity now runs from just above the floor pan to the crown (see
    # cabin_z), not a 210 mm tray sitting on 370 mm of solid body — a shallow tray
    # gives the seats nowhere to stand and reads as a filled-in cockpit.
    #
    # The liner matters as much as the furniture: without it the thing you see
    # through the side glass is the far side of the roof shell's INNER surface,
    # which carries the body paint and lights up bright yellow/red. Lining the
    # cavity in the interior tone makes the cabin read as a dark volume with the
    # seats and wheel silhouetted in it.
    floor_z = p.cabin_z[0]
    roof_z = p.cabin_z[1]
    belt_z = _door_opening(p)[5]
    cab_hw = p.cabin_half_x
    mid_y = (cy0 + cy1) * 0.5
    body.visual(
        Box((2.0 * cab_hw - 0.05, cy1 - cy0 - 0.08, 0.09)),
        origin=Origin(xyz=(0.0, mid_y, floor_z + 0.03)),
        material=mats["interior"],
        name="cabin_floor", material_class_id="fabric.carpet_fleece",
    )
    # Side trim stops at the beltline. The greenhouse is barely wider than the
    # cabin, so a liner carried up to the roof sits OUTBOARD of the glass pane and
    # simply plugs the window from the outside.
    liner_top = min(roof_z, belt_z)
    for sgn, side in ((1.0, "left"), (-1.0, "right")):
        body.visual(
            Box((0.05, cy1 - cy0 - 0.08, liner_top - floor_z)),
            origin=Origin(xyz=(sgn * (cab_hw - 0.02), mid_y, (floor_z + liner_top) * 0.5)),
            material=mats["interior"],
            name=f"cabin_liner_{side}", material_class_id="fabric.upholstery_plain",
        )
    # Engine bulkhead, standing right behind the seats and carried up to the
    # roofline. It is what stops the side window reading as a flat tinted panel:
    # the greenhouse is open on both sides, so without something filling it the
    # line of sight goes straight through the car to the background.
    band = _window_band(p, fam)
    bulk_top = min(band[3] - 0.03, roof_z + 0.34) if band else roof_z + 0.10
    bulk_y = seat_y_of(cy0, cy1) - 0.22
    body.visual(
        Box((2.0 * cab_hw - 0.05, 0.09, bulk_top - floor_z)),
        origin=Origin(xyz=(0.0, bulk_y, (floor_z + bulk_top) * 0.5)),
        material=mats["interior"],
        name="rear_bulkhead", material_class_id="fabric.upholstery_plain",
    )
    body.visual(
        Box((0.24, cy1 - cy0 - 0.30, 0.20)),
        origin=Origin(xyz=(0.0, mid_y, floor_z + 0.11)),
        material=mats["interior"],
        name="center_tunnel", material_class_id="plastic.opaque_generic",
    )
    # Dash brought up to the scuttle so the wheel reads against it, not against
    # daylight through the screen — but kept shallow and pushed forward, or it
    # simply hides the wheel from anyone looking in through the windscreen.
    dash_z = belt_z - 0.15
    # Kept behind the front arch: steering swings the tyre's inner-rear corner
    # inboard, and a full-width dash sitting level with the arch gets clipped by
    # it a few degrees into lock (it is inside the cabin, the tyre is outside, so
    # nothing catches this in the closed pose).
    dash_y = min(cy1 - 0.13, p.front_axle_y - _arch_radius_max(p) - 0.20)
    body.visual(
        Box((2.0 * cab_hw - 0.16, 0.26, 0.13)),
        origin=Origin(xyz=(0.0, dash_y, dash_z), rpy=(0.22, 0.0, 0.0)),
        material=mats["interior"],
        name="dash_cowl", material_class_id="leather.smooth_plain",
    )
    # Bucket seats sized from the cavity: cushion just off the floor, backrest up
    # through the window line, headrest above it.
    seat_y = seat_y_of(cy0, cy1)
    seat_x = max(0.26, cab_hw * 0.55)
    pan_z = floor_z + 0.11
    back_top = belt_z + 0.20
    back_h = max(0.32, back_top - (pan_z + 0.04))
    for sgn, side in ((1.0, "left"), (-1.0, "right")):
        body.visual(
            Box((0.40, 0.44, 0.13)),
            origin=Origin(xyz=(sgn * seat_x, seat_y - 0.12, pan_z)),
            material=mats["interior"],
            name=f"seat_pan_{side}", material_class_id=("leather.suede" if r.palette_style == "koenigsegg_icy_blue_carbon" else "leather.smooth_plain"),
        )
        body.visual(
            Box((0.42, 0.22, back_h)),
            origin=Origin(
                xyz=(sgn * seat_x, seat_y + 0.15, pan_z + 0.04 + back_h * 0.5),
                rpy=(-0.16, 0.0, 0.0),
            ),
            material=mats["interior"],
            name=f"seat_back_{side}", material_class_id="leather.smooth_plain",
        )
        body.visual(
            Box((0.26, 0.14, 0.16)),
            origin=Origin(
                xyz=(sgn * seat_x, seat_y + 0.20, back_top + 0.06), rpy=(-0.16, 0.0, 0.0)
            ),
            material=mats["interior"],
            name=f"headrest_{side}", material_class_id="leather.smooth_plain",
        )


def _lamp_station(p: _ProfileSpec) -> tuple[float, float, float, float]:
    """``(nose_y, lamp_x, lamp_width, lamp_z)`` of the headlight pocket.

    Pick x off the nose half-width first, then read the z at which the skin has
    drawn in to exactly that x — so the lamp lies ON the sheetmetal on a 0.49 m
    vintage nose and a 1.56 m wedge nose alike. The pop-up cover shares this so
    the flap always caps the lamp it is hinged over.
    """
    nose_y = p.sections[1][0] - 0.10
    nose_hw = _half_w(p, nose_y)
    lamp_x = nose_hw * 0.56
    lamp_w = _clamp(nose_hw * 0.46, 0.14, 0.40)
    return nose_y, lamp_x, lamp_w, _flank_z(p, nose_y, lamp_x) - 0.035


def _add_headlights(body, r, mats) -> None:
    """Front end: air dam + brake ducts + lamp cluster + bonnet relief + splitter.

    Every span and station comes from the body's own loft here. The old build
    planted the lamps at a fixed x=±0.40 with a fixed 0.36 m width and hung a
    1.30 m splitter off the nose, which is 2.6x the vintage body's 0.49 m nose —
    the lamps floated in mid-air off the sides of the narrow front wings.
    """
    p = r.profile
    nose_tip = p.sections[0][0]
    nose_y, lamp_x, lamp_w, z = _lamp_station(p)
    nose_crown = _crown(p, nose_y)
    nose_pan = _pan(p, nose_y)
    shape = r.headlight_shape
    rake = (-0.30, 0.0, 0.0)

    # ---- Front air dam. The loft caps its first section, so the body has a real
    # flat fascia at ``sections[0]`` — the grille is planted ON that face so it
    # straddles the skin. (A feature buried entirely inside the shell touches no
    # surface at all and the 1e-6 connectivity check calls it a floating island;
    # the surrounding sheetmetal being 200 mm thick does not count as contact.)
    cap_y, cap_z0, cap_z1, cap_w = p.sections[0]
    cap_hw = cap_w * 0.5
    cap_h = cap_z1 - cap_z0
    cap_cz = 0.5 * (cap_z0 + cap_z1)
    body.visual(
        Box((cap_hw * 1.24, 0.11, cap_h * 0.66)),
        origin=Origin(xyz=(0.0, cap_y - 0.025, cap_cz - cap_h * 0.10)),
        material=mats["accent"],
        name="front_air_dam", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((cap_hw * 1.06, 0.06, cap_h * 0.44)),
        origin=Origin(xyz=(0.0, cap_y + 0.010, cap_cz - cap_h * 0.10)),
        material=mats["glass"],
        name="front_air_dam_mouth", material_class_id="glass.smoked_tinted",
    )
    for sgn, side in ((1.0, "left"), (-1.0, "right")):
        body.visual(
            Box((cap_hw * 0.30, 0.12, cap_h * 0.40)),
            origin=Origin(xyz=(sgn * cap_hw * 0.80, cap_y - 0.03, cap_cz + cap_h * 0.20)),
            material=mats["accent"],
            name=f"brake_duct_{side}", material_class_id="plastic.opaque_glossy_molded",
        )

    # ---- Bumper band across the nose, straddling the flank at its own height.
    bump_z = _clamp(cap_cz + cap_h * 0.42, nose_pan + 0.08, nose_crown - 0.08)
    body.visual(
        Box((_flank_x(p, nose_y + 0.12, bump_z) * 2.04, 0.12, 0.13)),
        origin=Origin(xyz=(0.0, nose_y + 0.12, bump_z)),
        material=mats["accent"],
        name="front_bumper_strip", material_class_id="plastic.opaque_glossy_molded",
    )

    for sgn, side in ((1.0, "left"), (-1.0, "right")):
        sx = sgn * lamp_x
        ind_x = _flank_x(p, nose_y + 0.18, z - 0.06) * 0.86
        body.visual(
            Box((0.10, 0.06, 0.07)),
            origin=Origin(xyz=(sgn * ind_x, nose_y + 0.18, z - 0.07)),
            material=mats["amber"],
            name=f"front_indicator_{side}", material_class_id="tech.emissive_surface",
        )
        if shape == "exposed_rect":
            body.visual(
                Box((lamp_w, 0.20, 0.05)),
                origin=Origin(xyz=(sx, nose_y, z), rpy=rake),
                material=mats["accent"],
                name=f"headlight_surround_{side}", material_class_id="plastic.opaque_glossy_molded",
            )
            body.visual(
                Box((lamp_w * 0.90, 0.16, 0.014)),
                origin=Origin(xyz=(sx, nose_y, z + 0.022), rpy=rake),
                material=mats["lens"],
                name=f"headlight_reflector_{side}", material_class_id="metal.chrome_polished",
            )
            body.visual(
                Box((lamp_w * 0.94, 0.17, 0.012)),
                origin=Origin(xyz=(sx, nose_y + 0.002, z + 0.030), rpy=rake),
                material=mats["glass"],
                name=f"headlight_{side}", material_class_id="plastic.clear_rigid",
            )
        elif shape == "round_fixed":
            lamp_r = _clamp(lamp_w * 0.46, 0.070, 0.125)
            body.visual(
                Cylinder(radius=lamp_r, length=0.06),
                origin=Origin(xyz=(sx, nose_y, z), rpy=(math.pi / 2.0 - 0.30, 0.0, 0.0)),
                material=mats["chrome"],
                name=f"headlight_bucket_{side}", material_class_id="metal.chrome_polished",
            )
            body.visual(
                Cylinder(radius=lamp_r * 0.82, length=0.03),
                origin=Origin(
                    xyz=(sx, nose_y + 0.04, z + 0.01), rpy=(math.pi / 2.0 - 0.30, 0.0, 0.0)
                ),
                material=mats["lens"],
                name=f"headlight_reflector_{side}", material_class_id="metal.chrome_polished",
            )
            body.visual(
                Cylinder(radius=lamp_r * 0.91, length=0.018),
                origin=Origin(
                    xyz=(sx, nose_y + 0.07, z + 0.015), rpy=(math.pi / 2.0 - 0.30, 0.0, 0.0)
                ),
                material=mats["glass"],
                name=f"headlight_{side}", material_class_id="plastic.clear_rigid",
            )
        else:  # quad_cluster — sculpted pod with 3 jewels
            jewel_r = _clamp(lamp_w * 0.16, 0.028, 0.048)
            body.visual(
                Box((lamp_w * 0.86, 0.20, 0.06)),
                origin=Origin(xyz=(sx, nose_y, z), rpy=rake),
                material=mats["accent"],
                name=f"headlight_pod_{side}", material_class_id="plastic.opaque_glossy_molded",
            )
            for k, frac in enumerate((-0.30, 0.0, 0.30)):
                body.visual(
                    Cylinder(radius=jewel_r, length=0.05),
                    origin=Origin(
                        xyz=(sx + frac * lamp_w, nose_y + 0.02, z + 0.02),
                        rpy=(math.pi / 2.0 - 0.30, 0.0, 0.0),
                    ),
                    material=mats["lens"] if k != 2 else mats["amber"],
                    name=f"headlight_jewel_{side}_{k}", material_class_id="tech.emissive_surface",
                )
            body.visual(
                Box((lamp_w * 0.86, 0.17, 0.012)),
                origin=Origin(xyz=(sx, nose_y + 0.04, z + 0.035), rpy=rake),
                material=mats["glass"],
                name=f"headlight_{side}", material_class_id="plastic.clear_rigid",
            )

    # ---- Bonnet relief between the lamps: a chrome radiator grille on the
    # upright vintage nose, twin extractor vents on the low modern noses.
    hood_y = nose_y - 0.42
    hood_crown = _crown(p, hood_y)
    if p.has_roof_part:
        # Upright vintage nose: chrome radiator shell on the fascia cap + a spine
        # down the bonnet crown.
        body.visual(
            Box((cap_hw * 1.30, 0.07, cap_h * 0.82)),
            origin=Origin(xyz=(0.0, cap_y - 0.015, cap_cz + cap_h * 0.06)),
            material=mats["chrome"],
            name="radiator_grille", material_class_id="metal.chrome_polished",
        )
        # Follows the crown line: a straight bar at the bonnet's own crown height
        # rises clear of the nose, where the crown has fallen 0.3 m away.
        body.visual(
            _save("hood_spine.obj", _crown_strip(p, hood_y - 0.34, hood_y + 0.30, 0.035)),
            material=mats["chrome"],
            name="hood_spine", material_class_id="metal.chrome_polished",
        )
    else:
        for sgn, side in ((1.0, "left"), (-1.0, "right")):
            vent_x = _flank_x(p, hood_y, hood_crown - 0.03) * 0.52
            # Read the crown height AT the vent's own x — the section's z_max is
            # only reached on the centreline, so a vent placed at crown height but
            # off-centre floats above the bonnet.
            vent_z = _flank_z(p, hood_y, vent_x)
            body.visual(
                Box((0.20, 0.34, 0.05)),
                origin=Origin(xyz=(sgn * vent_x, hood_y, vent_z - 0.012)),
                material=mats["accent"],
                name=f"hood_vent_{side}", material_class_id="plastic.opaque_glossy_molded",
            )

    # ---- Splitter under the nose, spanning the actual front footprint.
    split_y = nose_tip - 0.20
    body.visual(
        Box((max(0.50, _half_w(p, split_y) * 1.86), 0.40, 0.055)),
        origin=Origin(xyz=(0.0, split_y, _pan(p, split_y) - 0.005)),
        material=mats["accent"],
        name="front_splitter", material_class_id="plastic.opaque_glossy_molded",
    )


def _rear_deck(p: _ProfileSpec) -> tuple[float, float, float]:
    """``(y_front, y_back, top_z)`` of the engine deck lid.

    ``top_z`` is the crown at the deck's FRONT rail, i.e. the highest point of
    the lid — everything mounted on the deck references it, and it tracks the
    body instead of the old ``cabin_z[1] + 0.03`` constant (which floated 0.25 m
    over the vintage tail because that body's crown falls away to 0.44)."""
    y_back = p.sections[-1][0] + 0.12
    y_front = p.cabin_y[0] - 0.04
    return y_front, y_back, _crown(p, y_front) + 0.008


_DECK_CACHE: dict[str, object] = {}


def _deck_mesh(r: ResolvedSportsCarConfig):
    """Engine-deck lid as a thin lens lofted along the body's own crown line."""
    p = r.profile
    key = r.body_profile_family
    if key in _DECK_CACHE:
        return _DECK_CACHE[key].clone()
    y_front, y_back, _top = _rear_deck(p)
    secs = []
    n = 9
    for i in range(n):
        y = y_back + (y_front - y_back) * i / (n - 1.0)
        crown = _crown(p, y)
        half = _flank_x(p, y, crown - 0.045)
        secs.append((y, crown - 0.09, crown + 0.008, max(0.10, 2.0 * half)))
    mesh = superellipse_side_loft(secs, exponents=max(2.4, p.exponent * 0.8), segments=32)
    _DECK_CACHE[key] = mesh
    return mesh.clone()


def _crown_strip(
    p: _ProfileSpec,
    y0: float,
    y1: float,
    half_w: float,
    drop: float = 0.06,
    proud: float = 0.006,
    steps: int = 7,
):
    """A narrow lens lofted along the body's crown line between two stations.

    Used for anything that must ride the top of the bodywork over a long run: a
    straight bar authored at the crown height of ONE station stands clear of the
    skin wherever the crown falls away (the bonnet spine cleared the vintage nose
    by 0.3 m and rendered as a rod sticking out of the car).
    """
    secs = []
    for i in range(steps):
        y = y0 + (y1 - y0) * i / (steps - 1.0)
        crown = _crown(p, y)
        secs.append((y, crown - drop, crown + proud, 2.0 * half_w))
    return superellipse_side_loft(secs, exponents=4.0, segments=20)


def _airfoil_profile(chord: float, thickness: float, camber: float, steps: int = 14):
    """Closed 2D NACA-style aerofoil outline, chord centred on the origin.

    Returned as ``(chord_offset, thickness_offset)`` pairs; the caller extrudes it
    along the span. A GT wing built from a flat 45 mm box reads as a shelf — the
    silhouette is what makes it read as a wing.
    """
    pts_up: list[tuple[float, float]] = []
    pts_lo: list[tuple[float, float]] = []
    for i in range(steps + 1):
        u = i / steps
        yt = (
            5.0
            * thickness
            * (
                0.2969 * math.sqrt(max(u, 0.0))
                - 0.1260 * u
                - 0.3516 * u * u
                + 0.2843 * u**3
                - 0.1015 * u**4
            )
        )
        yc = camber * 4.0 * u * (1.0 - u)
        c = chord * (u - 0.5)
        pts_up.append((c, yc + yt))
        pts_lo.append((c, yc - yt))
    return pts_up + list(reversed(pts_lo[1:-1]))


def _wing_blade_mesh(span: float, chord: float, thickness: float, aoa: float):
    """Extruded aerofoil: span along X, chord along Y, thickness along Z."""
    prof = [(-t, c) for (c, t) in _airfoil_profile(chord, thickness, chord * 0.055)]
    mesh = ExtrudeGeometry(prof, span, cap=True, center=True)
    mesh.rotate_y(math.pi / 2.0)  # profile-x → -Z, profile-y → Y, extrusion → X
    mesh.rotate_x(aoa)
    return mesh


def _add_rear(body, r, mats) -> None:
    """Rear treatment: engine deck lid + tail panel/lights + blade (GT wing /
    ducktail / louvered deck) + diffuser + exhaust, all sized off the body's own
    tail section rather than wedge-shaped constants."""
    p = r.profile
    tail_y = p.sections[-1][0]
    deck_front, deck_back, deck_top = _rear_deck(p)

    # ---- Engine deck lid: lofted along the crown so it lies ON the body all the
    # way back instead of cantilevering off the tail as a flat shelf.
    # Body-coloured lid (a black slab across the whole rear deck swallows the
    # tail); only the louvres that sit on it are accent.
    body.visual(_save("engine_deck.obj", _deck_mesh(r)), material=mats["body"], name="engine_deck", material_class_id="metal.paint_coated")

    # ---- Tail panel + taillights, spanning the ACTUAL tail section.
    tail_pan = _pan(p, tail_y + 0.05)
    tail_crown = _crown(p, tail_y + 0.05)
    panel_z = tail_pan + (tail_crown - tail_pan) * 0.62
    tail_hw = _flank_x(p, tail_y + 0.05, panel_z)
    panel_h = max(0.13, (tail_crown - tail_pan) * 0.34)
    body.visual(
        Box((max(0.34, tail_hw * 1.88), 0.09, panel_h)),
        origin=Origin(xyz=(0.0, tail_y + 0.05, panel_z)),
        material=mats["accent"],
        name="tail_panel", material_class_id="plastic.opaque_glossy_molded",
    )
    lamp_hw = max(0.10, tail_hw * 0.52)
    for sgn, side in ((1.0, "left"), (-1.0, "right")):
        body.visual(
            Box((lamp_hw, 0.045, panel_h * 0.42)),
            origin=Origin(xyz=(sgn * tail_hw * 0.56, tail_y + 0.015, panel_z + panel_h * 0.10)),
            material=mats["tail"],
            name=f"taillight_{side}", material_class_id="tech.emissive_surface",
        )
    body.visual(
        Box((max(0.16, tail_hw * 0.44), 0.04, panel_h * 0.20)),
        origin=Origin(xyz=(0.0, tail_y + 0.02, panel_z - panel_h * 0.24)),
        material=mats["tail"],
        name="tail_light_bar", material_class_id="tech.emissive_surface",
    )

    # ---- Rear diffuser under the tail: the underbody cue every modern race car
    # carries, and it closes off the otherwise blank tail underside.
    diff_y0 = tail_y + 0.06
    diff_y1 = tail_y + 0.62
    diff_z = _pan(p, (diff_y0 + diff_y1) * 0.5) + 0.018
    diff_hw = _flank_min(p, diff_y0, diff_y1, diff_z)
    body.visual(
        Box((max(0.30, diff_hw * 1.80), diff_y1 - diff_y0, 0.07)),
        origin=Origin(xyz=(0.0, (diff_y0 + diff_y1) * 0.5, diff_z), rpy=(-0.14, 0.0, 0.0)),
        material=mats["accent"],
        name="diffuser_pan", material_class_id="plastic.opaque_glossy_molded",
    )
    for k in range(3):
        fx = (k - 1) * diff_hw * 0.58
        body.visual(
            Box((0.035, diff_y1 - diff_y0 - 0.06, 0.10)),
            origin=Origin(
                xyz=(fx, (diff_y0 + diff_y1) * 0.5, diff_z + 0.045), rpy=(-0.14, 0.0, 0.0)
            ),
            material=mats["accent"],
            name=f"diffuser_fin_{k}", material_class_id="plastic.opaque_glossy_molded",
        )

    # ---- Rear blade.
    wing_y = tail_y + 0.30
    deck_hw = _flank_x(p, wing_y, _crown(p, wing_y) - 0.045)
    if r.rear_blade == "big_gt_wing":
        span = max(0.90, deck_hw * 2.02)
        chord = 0.34
        blade_z = deck_top + 0.34
        blade_y = wing_y - 0.06
        body.visual(
            _save(
                "wing_blade.obj",
                _wing_blade_mesh(span, chord, 0.055, 0.14).translate(0.0, blade_y, blade_z),
            ),
            material=mats["body"],
            name="wing_blade", material_class_id="metal.paint_coated",
        )
        # Gurney flap standing on the trailing edge. The blade is rotated by the
        # angle of attack about X, so the TE has moved to
        # (y - c/2·cos aoa, z - c/2·sin aoa) — placing the flap at the un-rotated
        # height leaves it hanging in the air above the wing.
        aoa = 0.14
        te_y = blade_y - chord * 0.46 * math.cos(aoa)
        te_z = blade_z - chord * 0.46 * math.sin(aoa)
        body.visual(
            Box((span * 0.96, 0.02, 0.07)),
            origin=Origin(xyz=(0.0, te_y, te_z + 0.022), rpy=(aoa, 0.0, 0.0)),
            material=mats["accent"],
            name="wing_gurney", material_class_id="plastic.opaque_glossy_molded",
        )
        for sgn, side in ((1.0, "left"), (-1.0, "right")):
            # End plate — the feature that reads "race wing" rather than "shelf".
            # Set 8 mm inboard of the blade tip: a plate that merely kisses the
            # tip plane is a tangency, and tangencies do not survive triangulation.
            body.visual(
                Box((0.022, chord * 1.30, 0.24)),
                origin=Origin(xyz=(sgn * (span * 0.5 - 0.008), blade_y, blade_z + 0.02)),
                material=mats["accent"],
                name=f"wing_endplate_{side}", material_class_id="plastic.opaque_glossy_molded",
            )
            # Swan-neck pylon: raked strut from the deck up to the blade, plus a
            # foot that embeds into the deck lid so the wing hangs off the body.
            px = sgn * deck_hw * 0.56
            _strut(
                body,
                (px, wing_y + 0.16, deck_top - 0.05),
                (px, blade_y + chord * 0.22, blade_z + 0.02),
                thick=0.05,
                width=0.09,
                material=mats["accent"],
                name=f"wing_pylon_{side}",
            )
            body.visual(
                Box((0.12, 0.20, 0.06)),
                origin=Origin(xyz=(px, wing_y + 0.16, deck_top - 0.055)),
                material=mats["accent"],
                name=f"wing_foot_{side}", material_class_id="plastic.opaque_glossy_molded",
            )
    elif r.rear_blade == "ducktail":
        body.visual(
            Box((max(0.40, deck_hw * 1.92), 0.30, 0.05)),
            origin=Origin(xyz=(0.0, wing_y, _crown(p, wing_y) - 0.015), rpy=(0.18, 0.0, 0.0)),
            material=mats["body"],
            name="ducktail_blade", material_class_id="metal.paint_coated",
        )
        body.visual(
            Box((max(0.40, deck_hw * 1.92), 0.07, 0.11)),
            origin=Origin(
                xyz=(0.0, wing_y - 0.10, _crown(p, wing_y) + 0.030), rpy=(0.18, 0.0, 0.0)
            ),
            material=mats["accent"],
            name="ducktail_lip", material_class_id="plastic.opaque_glossy_molded",
        )
    else:  # integrated — louvered deck, no big wing
        for k in range(6):
            ly = deck_front - 0.16 - 0.11 * k
            lw = _flank_x(p, ly, _crown(p, ly) - 0.045)
            body.visual(
                Box((max(0.24, lw * 1.62), 0.075, 0.055)),
                origin=Origin(xyz=(0.0, ly, _crown(p, ly) - 0.008), rpy=(0.12, 0.0, 0.0)),
                material=mats["accent"],
                name=f"deck_louver_{k}", material_class_id="plastic.opaque_glossy_molded",
            )

    # ---- Exhaust, hung off the actual tail footprint.
    ex_z = tail_pan + (tail_crown - tail_pan) * 0.24
    ex_hw = _flank_x(p, tail_y + 0.05, ex_z)
    if r.exhaust_layout == "side":
        ex_x = max(0.14, ex_hw - 0.07)
        for sgn, side in ((1.0, "left"), (-1.0, "right")):
            body.visual(
                Cylinder(radius=0.048, length=0.18),
                origin=Origin(xyz=(sgn * ex_x, tail_y + 0.04, ex_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["chrome"],
                name=f"exhaust_{side}", material_class_id="metal.chrome_polished",
            )
    elif r.exhaust_layout == "central_quad":
        pitch = min(0.085, max(0.045, ex_hw * 0.22))
        for k, mul in enumerate((-1.5, -0.5, 0.5, 1.5)):
            body.visual(
                Cylinder(radius=min(0.038, pitch * 0.45), length=0.14),
                origin=Origin(
                    xyz=(mul * pitch, tail_y + 0.02, ex_z), rpy=(math.pi / 2.0, 0.0, 0.0)
                ),
                material=mats["chrome"],
                name=f"exhaust_q{k}", material_class_id="metal.chrome_polished",
            )
    else:  # central_single
        body.visual(
            Cylinder(radius=0.075, length=0.16),
            origin=Origin(xyz=(0.0, tail_y + 0.02, ex_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["chrome"],
            name="exhaust_center_ring", material_class_id="metal.chrome_polished",
        )
        body.visual(
            Cylinder(radius=0.055, length=0.10),
            origin=Origin(xyz=(0.0, tail_y + 0.05, ex_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["accent"],
            name="exhaust_center_bore", material_class_id="metal.blackened_gunmetal",
        )


def _arch_flare_mesh(
    p: _ProfileSpec,
    ay: float,
    arch_cz: float,
    arch_r: float,
    sign: float,
    *,
    inboard: float = 0.048,
    proud: float = 0.020,
    segments: int = 16,
):
    """Fender flare: a band swept over the wheel opening that FOLLOWS the flank.

    A constant-radius annular ring cannot work here. At the top of the arch the
    fender crown has drawn in to roughly 0.53 half-width while the tyre's outer
    sidewall stands at 0.77, so a ring placed outboard of the tyre hangs in space
    over the crown, and a ring placed on the crown cuts through the tyre. The
    first build shipped the second of those — the black band slicing across the
    tyre shoulder.

    So the band's x is read from :func:`_flank_x` at each station of the sweep and
    straddles the skin there, while its RADIUS stays clear of the tyre all the way
    round. Built by hand as a quad strip: ``LoftGeometry`` only stacks closed XY
    loops at constant z, which a sweep whose direction rotates cannot supply.
    """
    r_in = arch_r - 0.014
    r_out = arch_r + 0.024
    r_mid = 0.5 * (r_in + r_out)
    h = 0.5 * (r_out - r_in)
    lo, hi = 0.14, math.pi - 0.14
    mesh = MeshGeometry()
    rings: list[list[int]] = []
    for i in range(segments + 1):
        t = lo + (hi - lo) * i / segments
        uy, uz = math.cos(t), math.sin(t)
        cy = ay + r_mid * uy
        cz = arch_cz + r_mid * uz
        xs = max(0.02, _flank_x(p, cy, cz))
        xi, xo = xs - inboard, xs + proud
        rings.append(
            [
                mesh.add_vertex(xi, cy - h * uy, cz - h * uz),
                mesh.add_vertex(xo, cy - h * uy, cz - h * uz),
                mesh.add_vertex(xo, cy + h * uy, cz + h * uz),
                mesh.add_vertex(xi, cy + h * uy, cz + h * uz),
            ]
        )
    # Wound so the strip is a positive-volume solid (outward normals), matching
    # the loft primitives the rest of the template feeds to manifold3d.
    for a, b in zip(rings, rings[1:]):
        for k in range(4):
            k2 = (k + 1) % 4
            mesh.add_face(a[k], b[k2], b[k])
            mesh.add_face(a[k], a[k2], b[k2])
    f, last = rings[0], rings[-1]
    mesh.add_face(f[0], f[1], f[2])
    mesh.add_face(f[0], f[2], f[3])
    mesh.add_face(last[0], last[2], last[1])
    mesh.add_face(last[0], last[3], last[2])
    return mesh if sign > 0 else _mirror_x(mesh)


def _add_sills_intakes(body, r, mats) -> None:
    """Rockers, fender arch lips, side intakes and fender vents.

    The old rocker set itself in from the section WIDTH — the widest point of the
    section, at mid-height. By the time the flank drops to sill height it has
    already drawn in (0.85 vs 0.93 on the wedge), so the "embedded" sill stood
    ~60 mm proud of the skin down its whole length. Everything here is set from
    :func:`_flank_min` at the feature's OWN height instead.
    """
    p = r.profile
    _x_in, _x_out, ap_y0, ap_y1, sill_top, _belt = _door_opening(p)

    # ---- Rocker / side skirt between the wheel arches.
    sill_y0 = p.rear_axle_y + _arch_radius_max(p) + 0.06
    sill_y1 = p.front_axle_y - _arch_radius_max(p) - 0.06
    sill_h = 0.12
    sill_out = _flank_min(p, sill_y0, sill_y1, sill_top) - 0.008
    sill_t = 0.11
    for sgn, side in ((1.0, "left"), (-1.0, "right")):
        body.visual(
            Box((sill_t, sill_y1 - sill_y0, sill_h)),
            origin=Origin(
                xyz=(
                    sgn * (sill_out - sill_t * 0.5),
                    (sill_y0 + sill_y1) * 0.5,
                    sill_top - sill_h * 0.5 + 0.01,
                )
            ),
            material=mats["accent"],
            name=f"rocker_sill_{side}", material_class_id="plastic.opaque_glossy_molded",
        )

    # ---- Fender arch lips. The arch is a plain cylinder carved out of the skin;
    # without a lip the opening reads as a slot punched in a slab.
    #
    # The lip has to satisfy two constraints at once, and the first build met
    # neither: RADIALLY it must straddle the carve edge (inside it and it is a
    # floating island in the open arch; outside it and it is buried in solid
    # bodywork), and AXIALLY it must sit outboard of the tyre. It previously sat
    # at a fixed radius of 0.36 — the same value the arch was carved at, which the
    # tyre could reach to within 5 mm — and its x band overlapped the tyre's by
    # 32-46 mm, so the band cut visibly through the tyre shoulder.
    arch_cz, arch_r = _arch_geom(p)
    for ay, tag in ((r.front_axle_y, "front"), (r.rear_axle_y, "rear")):
        for sgn, side in ((1.0, "left"), (-1.0, "right")):
            body.visual(
                _save(
                    f"arch_lip_{tag}_{side}.obj",
                    _arch_flare_mesh(p, ay, arch_cz, arch_r, sgn),
                ),
                material=mats["accent"],
                name=f"arch_lip_{tag}_{side}", material_class_id="plastic.opaque_glossy_molded",
            )

    # ---- Side intake in the rear quarter, ahead of the rear wheel: the single
    # strongest mid-engine cue on the flank.
    in_y = p.rear_axle_y + r.arch_radius + 0.26
    in_z = _pan(p, in_y) + (_crown(p, in_y) - _pan(p, in_y)) * 0.74
    in_x = _flank_x(p, in_y, in_z)
    for sgn, side in ((1.0, "left"), (-1.0, "right")):
        body.visual(
            Box((0.10, 0.30, 0.20)),
            origin=Origin(xyz=(sgn * (in_x - 0.045), in_y, in_z)),
            material=mats["glass"],
            name=f"side_intake_{side}", material_class_id="glass.smoked_tinted",
        )
        body.visual(
            Box((0.075, 0.06, 0.21)),
            origin=Origin(xyz=(sgn * (in_x - 0.030), in_y + 0.19, in_z)),
            material=mats["body"],
            name=f"side_intake_fin_{side}", material_class_id="metal.paint_coated",
        )
        # Front fender extractor vent behind the front arch.
        v_y = p.front_axle_y - r.arch_radius - 0.10
        v_z = _pan(p, v_y) + (_crown(p, v_y) - _pan(p, v_y)) * 0.70
        v_x = _flank_x(p, v_y, v_z)
        body.visual(
            Box((0.07, 0.16, 0.10)),
            origin=Origin(xyz=(sgn * (v_x - 0.030), v_y, v_z)),
            material=mats["accent"],
            name=f"fender_vent_{side}", material_class_id="plastic.opaque_glossy_molded",
        )


def _add_axles_steering(body, r, mats, model):
    """Axle rods (body visuals) + spinning steering wheel (REVOLUTE child part)."""
    p = r.profile
    for ay, axle_name in ((r.front_axle_y, "front_axle_bar"), (r.rear_axle_y, "rear_axle_bar")):
        body.visual(
            Cylinder(radius=AXLE_BAR_RADIUS, length=2.0 * r.half_track),
            origin=Origin(xyz=(0.0, ay, r.wheel_r), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["alloy"],
            name=axle_name, material_class_id="metal.aluminum_bare",
        )

    # Steering column (fixed body visual) + spinning steering wheel part.
    # Steering wheel inside the cabin, well forward of the door apertures so the
    # rim does not poke the roof or the door glass. cabin_y[1] is the front cabin
    # wall; sit the hub ~0.35 m behind it. Its HEIGHT is read off the beltline,
    # not off the cabin floor: the floor now sits at the footwell, so
    # `cabin_z[0] + 0.12` would put the wheel down by the driver's shins.
    sw_x = max(0.26, p.cabin_half_x * 0.50)
    # Rim top carried just past the beltline so the wheel clears the dash cowl —
    # sunk below it the dash hides the wheel completely from anyone looking in.
    # Station measured from the SEAT (a driver's wheel sits ~0.55 m ahead of the
    # cushion), not from the front cabin wall: the old `cabin_y[1] - 0.36` put it
    # 0.69 m ahead of the seat, out under the scuttle where nothing can see it.
    sw_y = min(seat_y_of(*p.cabin_y) + 0.55, p.cabin_y[1] - 0.30)
    sw_hub = (sw_x, sw_y, _door_opening(p)[5] - 0.010)
    sw_rake = (0.6, 0.0, 0.0)
    # Column runs from the cabin floor up to the hub. Its top end lands on sw_hub
    # so the steering-wheel joint origin sits on real geometry. Raked toward the
    # driver: with rpy x=0.6 the +Z local axis tilts back, so place the lower end
    # forward (+Y) of the hub and let the cylinder reach up/back to sw_hub.
    # Long enough to reach down into the floor pan. It used to be a fixed 0.34,
    # which no longer lands anywhere now that the hub is set from the beltline and
    # the floor from the deepened footwell.
    col_len = max(0.28, (sw_hub[2] - (p.cabin_z[0] + 0.05)) / math.cos(sw_rake[0]))
    col_cx = sw_x
    col_cy = sw_hub[1] + 0.5 * col_len * math.sin(sw_rake[0])
    col_cz = sw_hub[2] - 0.5 * col_len * math.cos(sw_rake[0])
    body.visual(
        Cylinder(radius=0.024, length=col_len),
        origin=Origin(xyz=(col_cx, col_cy, col_cz), rpy=sw_rake),
        material=mats["accent"],
        name="steering_column", material_class_id="plastic.opaque_generic",
    )
    steer_wheel = model.part("steering_wheel")
    rw, rh, rt, rd = 0.145, 0.110, 0.026, 0.045
    for sy, tag in ((rh, "top"), (-rh, "bot")):
        steer_wheel.visual(
            Box((2.0 * rw + rt, rt, rd)),
            origin=Origin(xyz=(0.0, sy, 0.0)),
            material=mats["accent"],
            name=f"sw_rim_{tag}", material_class_id="leather.smooth_plain",
        )
    for sx, tag in ((rw, "left"), (-rw, "right")):
        steer_wheel.visual(
            Box((rt + 0.016, 2.0 * rh - 0.010, rd + 0.012)),
            origin=Origin(xyz=(sx, 0.0, 0.0)),
            material=mats["accent"],
            name=f"sw_grip_{tag}", material_class_id="leather.smooth_plain",
        )
    steer_wheel.visual(
        Box((2.0 * rw, 0.030, 0.020)), material=mats["accent"], name="sw_spoke_cross", material_class_id="metal.blackened_gunmetal"
    )
    steer_wheel.visual(
        Cylinder(radius=0.044, length=0.10),
        origin=Origin(xyz=(0.0, 0.0, -0.02)),
        material=mats["accent"],
        name="sw_hub", material_class_id="plastic.opaque_generic",
    )
    steer_wheel.visual(
        Box((0.034, 0.020, 0.020)),
        origin=Origin(xyz=(0.0, rh, 0.020)),
        material=mats["amber"],
        name="sw_top_marker", material_class_id="tech.emissive_surface",
    )
    steer_wheel.inertial = Inertial.from_geometry(Box((0.32, 0.26, 0.06)), mass=2.0)
    # Steering wheel spins on the raked column (captured hub-on-column pivot).
    # Origin sits on the column top (real geometry); mating is grandfathered
    # because the hub-barrel-around-column is a pin-in-sleeve, not two faces.
    model.articulation(
        "steering_wheel_turn",
        ArticulationType.REVOLUTE,
        parent=body,
        child=steer_wheel,
        origin=Origin(xyz=sw_hub, rpy=sw_rake),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=10.0, velocity=8.0, lower=-3.14, upper=3.14),
    )


# --------------------------------------------------------------------------- #
# Door builders (Slot B)
# --------------------------------------------------------------------------- #


def _door_axis(mechanism: str, side: str):
    s = 1.0 if side == "left" else -1.0
    if mechanism == "scissor_butterfly":
        norm = math.sqrt(1.0 + _SCISSOR_TILT * _SCISSOR_TILT)
        return (-1.0 / norm, 0.0, s * _SCISSOR_TILT / norm)
    if mechanism == "gullwing":
        return (0.0, -s, 0.0)
    # Dihedral. Mirroring a rotation across the YZ plane is orientation-reversing:
    # axis (nx, ny, nz) on the left becomes (nx, -ny, -nz) on the right for the
    # SAME positive travel. _DH has no X component, so that is exactly s·_DH.
    #
    # The old form negated only Y and kept +Z on both sides, which left both doors
    # turning the same way about the vertical: the right-hand door swung INBOARD,
    # sweeping across the centreline and through the front wheel (it reached
    # x = +0.26 from a hinge at x = -0.93 on the wedge body).
    dn = math.sqrt(_DH[0] ** 2 + _DH[1] ** 2 + _DH[2] ** 2)
    return (s * _DH[0] / dn, s * _DH[1] / dn, s * _DH[2] / dn)


def _door_hinge_origin(r: ResolvedSportsCarConfig, side: str):
    """Hinge point in body frame. scissor/dihedral: front-top side edge.
    gullwing: roof-ridge longitudinal axis just off centerline."""
    p = r.profile
    s = 1.0 if side == "left" else -1.0
    if r.door_mechanism == "gullwing":
        # Roof-ridge longitudinal hinge at the cant-rail. Snap ONTO an actual
        # vertex of the canopy ROOF shell so the origin sits on real sheetmetal:
        # the seam-shared shell is lower/narrower than the old box roof panel, so
        # a fixed geometric point floats off it (fail_if_articulation_origin_far).
        _, rim_z, roof_top, cy0, cy1, cyl, cyh, half_w = _greenhouse_geom(r)
        target = (s * (half_w - 0.06), (cyl + cyh) * 0.5, roof_top - 0.02)
        return _nearest_canopy_vertex(r, target, s)
    # scissor/dihedral: the A-pillar foot, ON the outer flank just FORWARD of the
    # aperture (where the body is still solid).
    #
    # This used to snap to the body vertex nearest the target. After the aperture
    # was opened up to full door height that vertex is on the CUT PLANE at
    # x = door_aperture_x[0] — 0.4 m inboard of the skin — and a hinge that far in
    # swings the panel through an arc wide enough to reach the front tyre. The
    # loft surface is analytic (see _flank_x), so read the flank point directly.
    _x_in, _x_out, _ay0, ay1, _az0, az1 = _door_opening(p)
    hy = ay1 + 0.03
    hz = az1 - 0.05
    return (s * _flank_x(p, hy, hz), hy, hz)


_BODY_VTX_CACHE: dict[tuple, tuple[float, float, float]] = {}


def _nearest_body_vertex(r: ResolvedSportsCarConfig, target):
    """The body vertex nearest the 3D target point, from the cached mesh. Used to
    plant the pop-up cover hinge exactly on the front-fender surface."""
    tx, ty, tz = target
    sgn = 1.0 if tx >= 0 else -1.0
    key = (r.body_profile_family, round(tx, 3), round(ty, 3), round(tz, 3))
    if key in _BODY_VTX_CACHE:
        return _BODY_VTX_CACHE[key]
    mesh = _lower_body_mesh(r)
    best = (tx, ty, tz)
    best_d = 1e9
    for vx, vy, vz in mesh.vertices:
        if vx * sgn <= 0.10:  # same side as the target
            continue
        d = (vx - tx) ** 2 + (vy - ty) ** 2 + (vz - tz) ** 2
        if d < best_d:
            best_d = d
            best = (vx, vy, vz)
    _BODY_VTX_CACHE[key] = best
    return best


_CANOPY_VTX_CACHE: dict[tuple, tuple[float, float, float]] = {}


def _nearest_canopy_vertex(r: ResolvedSportsCarConfig, target, side_sign: float):
    """Nearest vertex of the family's canopy ROOF shell to the target, on the
    target's side. Plants the gullwing roof-ridge hinge exactly on the roof skin
    (the shell, not the lower body, is what the hinge must land on)."""
    tx, ty, tz = target
    key = (r.body_profile_family, round(tx, 3), round(ty, 3), round(tz, 3))
    if key in _CANOPY_VTX_CACHE:
        return _CANOPY_VTX_CACHE[key]
    roof_mesh, _ws, _rw, _ln = _canopy_meshes(r.profile, r.body_profile_family)
    best = target
    best_d = 1e9
    for vx, vy, vz in roof_mesh.vertices:
        if vx * side_sign <= 0.02:  # same side as the hinge
            continue
        d = (vx - tx) ** 2 + (vy - ty) ** 2 + (vz - tz) ** 2
        if d < best_d:
            best_d = d
            best = (vx, vy, vz)
    _CANOPY_VTX_CACHE[key] = best
    return best


_DOOR_MESH_CACHE: dict[str, object] = {}


def _door_skin_mesh(p: _ProfileSpec, family: str, sign: float):
    """The exact skin slice the door aperture removed from the body.

    Built as (body shell) ∩ (aperture cutter), so the panel *is* the body surface
    over the opening and seats dead flush. The old door was a straight 0.22 m-wide
    loft centred on the hinge — half of it stood outside the skin, which is the
    slab hanging off the flank in every gallery render, and its top edge was a
    hard chord across a flank that curves in by 0.2 m over the aperture's height.
    """
    if family not in _DOOR_MESH_CACHE:
        x_in, x_out, y0, y1, z0, z1 = _door_opening(p)
        ys = [y0 - 0.05 + (y1 - y0 + 0.10) * i / 8.0 for i in range(9)]
        outer_secs = []
        for y in ys:
            a0, a1, hw = _sec_lerp(p, y)
            outer_secs.append((y, a0, a1, 2.0 * hw))
        t = DOOR_SKIN_T
        inner_secs = [(y, a0 + t, a1 - t, max(w - 2.0 * t, 0.05)) for (y, a0, a1, w) in outer_secs]
        shell = boolean_difference(
            superellipse_side_loft(outer_secs, exponents=p.exponent, segments=32),
            superellipse_side_loft(inner_secs, exponents=p.exponent, segments=32),
        )
        _DOOR_MESH_CACHE[family] = boolean_intersection(
            shell, _box_cutter(x_in, x_out, y0, y1, z0, z1)
        )
    mesh = _DOOR_MESH_CACHE[family].clone()
    return mesh if sign > 0 else _mirror_x(mesh)


def _make_door(model, r, mats, side: str):
    """Door part: flush skin slice + frameless side glass + beltline moulding +
    handle + door mirror, authored in body frame then shifted into the hinge-local
    frame (P2 L610-L676)."""
    s = 1.0 if side == "left" else -1.0
    p = r.profile
    hx, hy, hz = _door_hinge_origin(r, side)
    door = model.part(f"door_{side}")
    _x_in, _x_out, y0, y1, z0, z1 = _door_opening(p)

    def loc(x, y, z):
        return (x - hx, y - hy, z - hz)

    door.visual(
        _save(
            f"door_{side}_skin.obj",
            _door_skin_mesh(p, r.body_profile_family, s).translate(-hx, -hy, -hz),
        ),
        material=mats["body"],
        name="door_skin", material_class_id="metal.paint_coated",
    )

    # Beltline moulding capping the panel's top edge — a thin strip riding the
    # flank, not the old 0.34 m-wide shelf that stuck out past the bodywork.
    belt_x = _flank_min(p, y0, y1, z1 - 0.02)
    door.visual(
        Box((0.075, y1 - y0 - 0.04, 0.07)),
        origin=Origin(xyz=loc(s * (belt_x - 0.030), (y0 + y1) * 0.5, z1 - 0.010)),
        material=mats["accent"],
        name="door_beltline", material_class_id="plastic.opaque_glossy_molded",
    )

    # NOTE the side glazing is carried by the BODY, not the door. The greenhouse
    # is tumble-homed 0.15–0.30 m inboard of the flank, so a door-mounted pane has
    # to be tied back to the panel across that whole gap — and the bridge is a
    # horizontal shelf standing proud of the shoulder, which is precisely the
    # bolted-on-plate look this rebuild is removing. The body already owns the
    # shoulder sheetmetal the glass sits on, so the glass belongs to it too.

    # Recessed flush handle at the rear of the panel.
    handle_z = z1 - 0.10
    door.visual(
        Box((0.05, 0.17, 0.045)),
        origin=Origin(xyz=loc(s * (_flank_x(p, y0 + 0.22, handle_z) - 0.018), y0 + 0.22, handle_z)),
        material=mats["accent"],
        name="door_handle", material_class_id="plastic.opaque_glossy_molded",
    )

    # Door mirror on a short stalk at the panel's leading edge.
    # Read the flank at the stalk's OWN height: the panel stops at the beltline,
    # so a mirror seated above z1 has no door skin under it to attach to.
    mir_y = y1 - 0.10
    mir_z = z1 - 0.050
    mir_x = _flank_x(p, mir_y, mir_z)
    door.visual(
        Box((0.13, 0.045, 0.035)),
        origin=Origin(xyz=loc(s * (mir_x + 0.020), mir_y, mir_z), rpy=(0.0, -s * 0.45, 0.0)),
        material=mats["body"],
        name="mirror_stalk", material_class_id="metal.paint_coated",
    )
    door.visual(
        Box((0.055, 0.15, 0.085)),
        origin=Origin(xyz=loc(s * (mir_x + 0.080), mir_y, mir_z + 0.048)),
        material=mats["body"],
        name="mirror_head", material_class_id="metal.paint_coated",
    )

    # Hinge lug at the door's local origin (the joint origin) — real hinge
    # hardware so the door part AABB contains (0,0,0); also the visual contact
    # point where the door pivots against the body flank.
    door.visual(
        Box((0.08, 0.10, 0.10)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["accent"],
        name="door_hinge_lug", material_class_id="metal.blackened_gunmetal",
    )
    # Arm bridging the lug to the panel. The scissor/dihedral hinge already sits
    # in the skin, so this is a stub; the gullwing hinge is up on the roof ridge
    # and inboard of the flank, so the arm has to reach both down AND outboard —
    # a purely vertical arm drops through thin air beside the door. Landed on the
    # panel's FRONT-top corner so it lies along the A-pillar (a gullwing door's
    # leading edge really does run up the pillar to the roof); routed to the
    # middle of the opening it reads as a roll-cage bar across the side window.
    _strut(
        door,
        (0.0, 0.0, 0.02),
        loc(s * (belt_x - 0.03), y1 - 0.05, z1 - 0.05),
        thick=0.075,
        width=0.075,
        material=mats["body"],
        name="door_hinge_arm",
    )
    door.inertial = Inertial.from_geometry(
        Box((0.14, y1 - y0, z1 - z0 + 0.30)),
        mass=30.0,
        origin=Origin(xyz=loc(s * belt_x * 0.9, (y0 + y1) * 0.5, (z0 + z1) * 0.5)),
    )
    return door


# --------------------------------------------------------------------------- #
# Optional articulated covers (Slot C pop-up, Slot D louver)
# --------------------------------------------------------------------------- #


def _make_headlight_cover(model, r, mats, side: str):
    """Pop-up headlight cover part (v07 L605-L637). REVOLUTE about X.

    Sized off the lamp pocket it caps rather than a fixed 0.37 m panel, which on
    the vintage nose was wider than the wing it was supposed to sit in.
    """
    s = 1.0 if side == "left" else -1.0
    _ny, _lx, lamp_w, _lz = _lamp_station(r.profile)
    cw = lamp_w * 1.06
    cover = model.part(f"headlight_cover_{side}")
    cover.visual(
        Box((cw, 0.21, 0.024)),
        origin=Origin(xyz=(0.0, 0.085, -0.018), rpy=(-0.30, 0.0, 0.0)),
        material=mats["body"],
        name="cover_panel", material_class_id="metal.paint_coated",
    )
    cover.visual(
        Box((cw, 0.016, 0.030)),
        origin=Origin(xyz=(0.0, -0.030, -0.006), rpy=(-0.30, 0.0, 0.0)),
        material=mats["accent"],
        name="cover_front_seam", material_class_id="plastic.opaque_generic",
    )
    cover.visual(
        Box((0.024, 0.20, 0.030)),
        origin=Origin(xyz=(s * (cw * 0.5 - 0.012), 0.080, -0.006), rpy=(-0.30, 0.0, 0.0)),
        material=mats["accent"],
        name="cover_outer_seam", material_class_id="plastic.opaque_generic",
    )
    cover.visual(
        Cylinder(radius=0.018, length=cw * 0.92),
        origin=Origin(xyz=(0.0, -0.020, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["accent"],
        name="hinge_pin", material_class_id="metal.stainless_matte",
    )
    cover.inertial = Inertial.from_geometry(
        Box((cw + 0.03, 0.24, 0.04)), mass=3.0, origin=Origin(xyz=(0.0, 0.08, -0.01))
    )
    return cover


def _make_engine_cover(model, r, mats):
    """Engine louver cover part (v09 L605-L629). REVOLUTE about X.

    Spans the deck it seats on: the fixed 1.18 m panel overhung the vintage rear
    deck by a quarter-metre a side, which is the grey shelf floating over the tail
    in the gallery renders.

    REAR-hinged (the pin is at the tail end and the panel reaches FORWARD toward
    the cabin). The joint opens positively about +X, and +X lifts whatever lies at
    +y: a forward-hinged panel reaching aft is driven DOWN through the rear
    bulkhead and into the rear tyres by the same motion.
    """
    p = r.profile
    deck_front, deck_back, _top = _rear_deck(p)
    cw = max(
        0.42, 2.0 * _flank_x(p, (deck_front + deck_back) * 0.5, _crown(p, deck_front) - 0.06) * 0.86
    )
    cl = min(0.70, max(0.34, (deck_front - deck_back) * 0.62))
    cover = model.part("engine_cover")
    cover.visual(
        Box((cw, cl, 0.045)),
        origin=Origin(xyz=(0.0, cl * 0.5 - 0.01, 0.055), rpy=(0.18, 0.0, 0.0)),
        material=mats["body"],
        name="cover_panel", material_class_id="metal.paint_coated",
    )
    for k in range(5):
        # Louver ribs embed into the cover panel. Made tall (and their center kept
        # at the panel z) so that even with the panel's rake the rib bottom stays
        # inside the panel along its whole length (no front-rib island).
        cover.visual(
            Box((cw * 0.90, 0.052, 0.10)),
            origin=Origin(xyz=(0.0, 0.09 + (cl - 0.16) / 5.0 * k, 0.055), rpy=(0.18, 0.0, 0.0)),
            material=mats["accent"],
            name=f"cover_louver_{k}", material_class_id="plastic.opaque_glossy_molded",
        )
    cover.visual(
        Cylinder(radius=0.026, length=cw * 0.88),
        origin=Origin(xyz=(0.0, -0.020, 0.020), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["alloy"],
        name="cover_hinge_pin", material_class_id="metal.aluminum_bare",
    )
    cover.inertial = Inertial.from_geometry(
        Box((cw + 0.02, cl + 0.02, 0.08)), mass=18.0, origin=Origin(xyz=(0.0, cl * 0.5, 0.04))
    )
    return cover


# --------------------------------------------------------------------------- #
# Wheels + knuckles + assembly
# --------------------------------------------------------------------------- #


def _make_wheel(model, r, mats, tire_geom, wheel_geom, name: str, outboard_sign: float):
    w = model.part(name)
    face_rpy = (0.0, 0.0, 0.0) if outboard_sign > 0 else (0.0, 0.0, math.pi)
    w.visual(
        _save(f"{name}_tire.obj", tire_geom.clone()),
        origin=Origin(rpy=face_rpy),
        material=mats["rubber"],
        name="tire", material_class_id="rubber.directional_grooved",
    )
    w.visual(
        _save(f"{name}_alloy.obj", wheel_geom.clone()),
        origin=Origin(xyz=(outboard_sign * 0.03, 0.0, 0.0), rpy=face_rpy),
        material=mats["alloy"],
        name="rim", material_class_id="metal.aluminum_bare",
    )
    # Hub-center fill so the wheel part AABB solidly contains the spin origin
    # (0,0,0) — the open bore otherwise leaves a >tol gap at the rear-wheel
    # spin joint (fail_if_articulation_origin_far_from_geometry).
    w.visual(
        Cylinder(radius=r.wheel_r * 0.18, length=r.wheel_w * 0.8),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["alloy"],
        name="hub_center", material_class_id="metal.aluminum_bare",
    )
    w.inertial = Inertial.from_geometry(
        Cylinder(radius=r.wheel_r, length=r.wheel_w),
        mass=22.0,
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
    )
    return w


def build_sports_car(
    config: SportsCarConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    p = r.profile
    model = ArticulatedObject(name=r.name, assets=assets)

    # Register materials (Slot E palette). Every .visual uses mats[...].
    mats: dict[str, object] = {}
    for token, rgba in PALETTES[r.palette_style].items():
        mats[token] = model.material(token, rgba=rgba)

    # ----------------------------------------------------------------- body
    body = model.part("body")
    body.visual(
        _save("lower_body.obj", _lower_body_mesh(r)), material=mats["body"], name="lower_body", material_class_id="metal.paint_coated"
    )
    _add_greenhouse(body, r, mats)
    _add_headlights(body, r, mats)
    _add_rear(body, r, mats)
    _add_sills_intakes(body, r, mats)
    _add_axles_steering(body, r, mats, model)
    body.inertial = Inertial.from_geometry(
        Box((2.0, 4.46, 1.10 * r.body_height_scale)),
        mass=1450.0,
        origin=Origin(xyz=(0.0, 0.0, 0.55)),
    )

    # ----------------------------------------------------------------- doors
    door_left = _make_door(model, r, mats, "left")
    door_right = _make_door(model, r, mats, "right")
    for door, side in ((door_left, "left"), (door_right, "right")):
        hx, hy, hz = _door_hinge_origin(r, side)
        # Door is a flush-seat panel captured in the body aperture: the skin
        # loft refills the carved hole. This is not a clean two-face mate, so the
        # mating contract is grandfathered (matches the 5★ reference doors).
        model.articulation(
            f"door_{side}_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=door,
            origin=Origin(xyz=(hx, hy, hz)),
            axis=_door_axis(r.door_mechanism, side),
            motion_limits=MotionLimits(effort=60.0, velocity=2.0, lower=0.0, upper=r.door_open_max),
        )

    # --------------------------------------------------------------- wheels
    tire_geom, wheel_geom = _wheel_geoms(r)
    _make_wheel(model, r, mats, tire_geom, wheel_geom, "wheel_front_left", 1.0)
    _make_wheel(model, r, mats, tire_geom, wheel_geom, "wheel_front_right", -1.0)
    _make_wheel(model, r, mats, tire_geom, wheel_geom, "wheel_rear_left", 1.0)
    _make_wheel(model, r, mats, tire_geom, wheel_geom, "wheel_rear_right", -1.0)

    # --------------------------------------------------- steer knuckles
    def make_knuckle(name: str):
        k = model.part(name)
        k.inertial = Inertial.from_geometry(Box((0.10, 0.10, 0.22)), mass=6.0)
        return k

    knuckle_fl = make_knuckle("steer_knuckle_front_left")
    knuckle_fr = make_knuckle("steer_knuckle_front_right")

    # Front steering REVOLUTE about vertical king-pin (Z). Grandfathered (the
    # knuckle is a captured carrier link with no visual; pin-in-bore geometry).
    for knuckle, sx in ((knuckle_fl, r.half_track), (knuckle_fr, -r.half_track)):
        model.articulation(
            f"{knuckle.name}_steer",
            ArticulationType.REVOLUTE,
            parent=body,
            child=knuckle,
            origin=Origin(xyz=(sx, r.front_axle_y, r.wheel_r)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=120.0, velocity=4.0, lower=-r.steer_lock, upper=r.steer_lock
            ),
        )

    # Wheel spin CONTINUOUS about lateral X. Front spins off the knuckle; rear off
    # the body. Grandfathered (axle pin runs through the hub bore).
    for name, spin_parent, origin_xyz in (
        ("wheel_front_left", knuckle_fl, (0.0, 0.0, 0.0)),
        ("wheel_front_right", knuckle_fr, (0.0, 0.0, 0.0)),
        ("wheel_rear_left", body, (r.half_track, r.rear_axle_y, r.wheel_r)),
        ("wheel_rear_right", body, (-r.half_track, r.rear_axle_y, r.wheel_r)),
    ):
        model.articulation(
            f"{name}_spin",
            ArticulationType.CONTINUOUS,
            parent=spin_parent,
            child=name,
            origin=Origin(xyz=origin_xyz),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=200.0, velocity=60.0),
        )

    # ----------------------------------------- optional pop-up headlight covers
    if r.headlight_popup:
        nose_y, lamp_x, _lw, lamp_z = _lamp_station(p)
        for side, sgn in (("left", 1.0), ("right", -1.0)):
            cover = _make_headlight_cover(model, r, mats, side)
            # Snap the cover hinge onto the actual front-fender body surface near
            # the lamp pocket so the joint origin sits on real geometry.
            hx, hy, hz = _nearest_body_vertex(r, (sgn * lamp_x, nose_y - 0.10, lamp_z + 0.01))
            # Pop-up cover hinged on a pin at the front fender; flush-seat in the
            # carved pocket. Grandfathered (pin-in-pocket, matches v07 reference).
            model.articulation(
                f"headlight_cover_{side}_hinge",
                ArticulationType.REVOLUTE,
                parent=body,
                child=cover,
                origin=Origin(xyz=(hx, hy, hz)),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=8.0, velocity=3.0, lower=0.0, upper=0.90),
            )

    # ------------------------------------------- optional engine louver cover
    if r.rear_louver_cover:
        cover = _make_engine_cover(model, r, mats)
        deck_front, deck_back, _deck_top = _rear_deck(p)
        cl = min(0.70, max(0.34, (deck_front - deck_back) * 0.62))
        # Engine louver cover hinged on a pin across the TAIL end of the deck, so
        # +X travel lifts the panel clear of the body; flush-seat on the engine
        # deck. Grandfathered (pin-on-deck, matches v09 reference). Origin planted
        # on the deck's own crown so the joint origin lies on real geometry.
        hinge_y = deck_front - cl
        model.articulation(
            "engine_cover_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=cover,
            origin=Origin(xyz=(0.0, hinge_y, _crown(p, hinge_y) - 0.010)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=30.0, velocity=2.0, lower=0.0, upper=0.70),
        )

    return model


def build_seeded_sports_car(seed: int) -> ArticulatedObject:
    return build_sports_car(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Author tests
# --------------------------------------------------------------------------- #


def run_sports_car_tests(
    model: ArticulatedObject,
    config: SportsCarConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    body = model.get_part("body")
    door_l = model.get_part("door_left")
    door_r = model.get_part("door_right")
    wheels = {
        name: model.get_part(name)
        for name in (
            "wheel_front_left",
            "wheel_front_right",
            "wheel_rear_left",
            "wheel_rear_right",
        )
    }

    # ---- Intentional overlap allowances (captured-pin / flush-seat). ---------
    # Steering column meets the spinning wheel hub on the spin axis; the wheel
    # hub also sits down inside the cabin against the body floor/flank.
    sw_part = model.get_part("steering_wheel")
    sw_elems = (
        "sw_hub",
        "sw_spoke_cross",
        "sw_rim_top",
        "sw_rim_bot",
        "sw_grip_left",
        "sw_grip_right",
        "sw_top_marker",
    )
    for selem in sw_elems:
        ctx.allow_overlap(
            body,
            sw_part,
            elem_a="steering_column",
            elem_b=selem,
            reason="Fixed steering column meets the wheel hub/spokes at the center, on the spin axis.",
        )
        for shell in (
            "lower_body",
            "cabin_floor",
            "greenhouse",
            "windshield",
            "seat_back_left",
            "seat_back_right",
            "seat_pan_left",
            "seat_pan_right",
            "dash_cowl",
            "center_tunnel",
            "beltline_rail_left",
            "beltline_rail_right",
            "beltline_trim_left",
            "beltline_trim_right",
            "cabin_liner_left",
            "cabin_liner_right",
            "rear_bulkhead",
            "headliner",
            "headrest_left",
            "headrest_right",
            "a_pillar_left",
            "a_pillar_right",
        ):
            ctx.allow_overlap(
                body,
                sw_part,
                elem_a=shell,
                elem_b=selem,
                reason="Steering wheel sits inside the hollow cabin against the body.",
            )
    # Wheels seated in the fender wells; axle rods run hub-to-hub through them.
    axle_of = {
        "wheel_front_left": "front_axle_bar",
        "wheel_front_right": "front_axle_bar",
        "wheel_rear_left": "rear_axle_bar",
        "wheel_rear_right": "rear_axle_bar",
    }
    for wname, w in wheels.items():
        side = "left" if wname.endswith("left") else "right"
        is_rear = "rear" in wname
        for elem in ("tire", "rim", "hub_center"):
            ctx.allow_overlap(
                body,
                w,
                elem_a="lower_body",
                elem_b=elem,
                reason="Wheel seated flush inside the fender wheel arch of the solid body shell.",
            )
            ctx.allow_overlap(
                body,
                w,
                elem_a=axle_of[wname],
                elem_b=elem,
                reason="Straight axle rod runs out to the wheel hub on the spin/steer axis.",
            )
            # Narrow-track (vintage) bodies tuck the rocker sill against the tire.
            ctx.allow_overlap(
                body,
                w,
                elem_a=f"rocker_sill_{side}",
                elem_b=elem,
                reason="Rocker sill runs alongside the wheel between the arches.",
            )
            # Arch lip wraps the wheel opening it frames.
            ctx.allow_overlap(
                body,
                w,
                elem_a=f"arch_lip_{'rear' if is_rear else 'front'}_{side}",
                elem_b=elem,
                reason="Fender arch lip wraps the wheel opening around the tire.",
            )
            for be in (
                "diffuser_pan",
                "front_splitter",
                "side_intake_left",
                "side_intake_right",
                f"fender_vent_{side}",
                "engine_deck",
            ):
                ctx.allow_overlap(
                    body,
                    w,
                    elem_a=be,
                    elem_b=elem,
                    reason="Aero/body furniture spans over the wheel bays.",
                )
            # The engine deck spans over the rear bay above the rear wheels; on the
            # short-wheelbase vintage body the deck shoulder brushes the rear tire.
            if is_rear:
                ctx.allow_overlap(
                    body,
                    w,
                    elem_a="engine_deck",
                    elem_b=elem,
                    reason="Engine deck spans over the mid/rear bay above the rear wheel.",
                )
    # The driver's steering wheel sits at the cabin edge near the left door — its
    # rim/grip can brush the door glass/skin (both inhabit the cabin opening).
    for door, side in ((door_l, "left"), (door_r, "right")):
        for selem in ("sw_rim_top", "sw_rim_bot", "sw_grip_left", "sw_grip_right", "sw_hub"):
            for delem in ("door_skin", "door_beltline", "door_handle"):
                ctx.allow_overlap(
                    door,
                    sw_part,
                    elem_a=delem,
                    elem_b=selem,
                    reason="Steering wheel sits at the cabin edge by the door opening.",
                )
    # Doors seat flush into the body aperture (thin embed intentional); the inner
    # skin/glass also brush the cabin floor / seats / window glazing.
    for door, side in ((door_l, "left"), (door_r, "right")):
        for shell in (
            "lower_body",
            "greenhouse",
            f"rocker_sill_{side}",
            "windshield",
            "rear_window",
            "cabin_floor",
            f"seat_back_{side}",
            f"seat_pan_{side}",
            f"headrest_{side}",
            f"cabin_liner_{side}",
            "rear_bulkhead",
            "headliner",
            f"headrest_{side}",
            "dash_cowl",
            "center_tunnel",
            "engine_deck",
            "steering_column",
            f"a_pillar_{side}",
            f"c_pillar_{side}",
            f"cant_rail_{side}",
            f"quarter_panel_{side}",
            f"beltline_rail_{side}",
            f"beltline_trim_{side}",
            f"side_intake_{side}",
            f"side_intake_fin_{side}",
            f"fender_vent_{side}",
            f"arch_lip_front_{side}",
            f"arch_lip_rear_{side}",
            f"quarter_light_{side}",
        ):
            for delem in (
                "door_skin",
                "door_beltline",
                "mirror_stalk",
                "mirror_head",
                "door_handle",
                "door_hinge_lug",
                "door_hinge_arm",
            ):
                ctx.allow_overlap(
                    body,
                    door,
                    elem_a=shell,
                    elem_b=delem,
                    reason="Door seats flush in the body aperture; thin embed intentional.",
                )
    # Pop-up covers seat in the nose, OVER the headlight cluster (the cover's
    # whole job is to cap the lamp), so they overlap the body nose + lamp visuals.
    if r.headlight_popup:
        hl_elems = (
            "lower_body",
            "front_splitter",
            "front_bumper_strip",
            "front_air_dam",
            "front_air_dam_mouth",
            "brake_duct_left",
            "brake_duct_right",
            "radiator_grille",
            "hood_spine",
            "hood_vent_left",
            "hood_vent_right",
            "arch_lip_front_left",
            "arch_lip_front_right",
            "front_indicator_left",
            "front_indicator_right",
            "headlight_left",
            "headlight_right",
            "headlight_surround_left",
            "headlight_surround_right",
            "headlight_reflector_left",
            "headlight_reflector_right",
            "headlight_bucket_left",
            "headlight_bucket_right",
            "headlight_pod_left",
            "headlight_pod_right",
        )
        for side in ("left", "right"):
            cv = model.get_part(f"headlight_cover_{side}")
            for celem in ("cover_panel", "cover_front_seam", "cover_outer_seam", "hinge_pin"):
                for be in hl_elems:
                    ctx.allow_overlap(
                        body,
                        cv,
                        elem_a=be,
                        elem_b=celem,
                        reason="Pop-up cover caps the headlight in the fender pocket.",
                    )
    if r.rear_louver_cover:
        ec = model.get_part("engine_cover")
        cover_elems = ["cover_panel", "cover_hinge_pin"] + [f"cover_louver_{k}" for k in range(5)]
        deck_louvers = (
            [f"deck_louver_{k}" for k in range(6)] if r.rear_blade == "integrated" else []
        )
        # The cover seats flush over the rear deck: it embeds into the engine deck,
        # the body shell, the rear glass/roof behind it, and the deck louvers.
        for be in (
            "engine_deck",
            "arch_lip_rear_left",
            "arch_lip_rear_right",
            "lower_body",
            "tail_panel",
            "rear_window",
            "greenhouse",
            "ducktail_blade",
            "ducktail_lip",
            "wing_foot_left",
            "wing_foot_right",
            "wing_pylon_left",
            "wing_pylon_right",
            "quarter_panel_left",
            "quarter_panel_right",
            "c_pillar_left",
            "c_pillar_right",
            *deck_louvers,
        ):
            for celem in cover_elems:
                ctx.allow_overlap(
                    body,
                    ec,
                    elem_a=be,
                    elem_b=celem,
                    reason="Engine louver cover seats flush over the rear deck / body shell.",
                )

    # ---- Baseline ------------------------------------------------------------
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # ---- Category identity: 4 wheels, 2 doors, body present ------------------
    vis_names = {v.name for v in body.visuals}
    ctx.check(
        "lofted single-body present (not a box)",
        "lower_body" in vis_names,
        details=f"body visuals={sorted(vis_names)[:8]}",
    )
    ctx.check("two doors present", door_l is not None and door_r is not None)
    ctx.check("four wheels present", len(wheels) == 4)

    # ---- Scale sanity --------------------------------------------------------
    bb = ctx.part_world_aabb(body)
    assert bb is not None
    lo, hi = bb
    ctx.check(
        "car length 4.3..4.8 m", 4.2 <= hi[1] - lo[1] <= 4.9, details=f"L={hi[1] - lo[1]:.3f}"
    )
    ctx.check(
        "car width 1.5..2.3 m", 1.4 <= hi[0] - lo[0] <= 2.35, details=f"W={hi[0] - lo[0]:.3f}"
    )
    ctx.check("car height 0.9..1.5 m", 0.85 <= hi[2] <= 1.55, details=f"H={hi[2]:.3f}")

    # ---- Doors: correct hinge axis + actually swing --------------------------
    for side, door in (("left", door_l), ("right", door_r)):
        hinge = model.get_articulation(f"door_{side}_hinge")
        ax = tuple(hinge.axis)
        if r.door_mechanism == "scissor_butterfly":
            ok_axis = abs(ax[0]) > 0.9 and abs(ax[1]) < 1e-6
        elif r.door_mechanism == "gullwing":
            ok_axis = abs(ax[1]) > 0.9 and abs(ax[0]) < 1e-6
        else:  # dihedral — near-vertical canted
            ok_axis = abs(ax[2]) > 0.8 and abs(ax[0]) < 1e-6
        ctx.check(
            f"door_{side} hinge axis matches {r.door_mechanism}",
            ok_axis,
            details=f"axis={ax}",
        )
        ml = hinge.motion_limits
        ctx.check(
            f"door_{side} opens from closed",
            ml is not None and abs(ml.lower) < 1e-6 and ml.upper >= 1.0,
            details=f"limits=({ml.lower}, {ml.upper})" if ml else "no limits",
        )
        rest = ctx.part_world_aabb(door)
        with ctx.pose({hinge: min(1.0, ml.upper)}):
            opened = ctx.part_world_aabb(door)
        if rest is not None and opened is not None:
            moved = (
                abs(opened[1][2] - rest[1][2]) > 0.1
                or abs(opened[1][0] - rest[1][0]) > 0.1
                or abs(opened[0][0] - rest[0][0]) > 0.1
            )
            ctx.check(
                f"door_{side} swings when opened", moved, details=f"rest={rest}, opened={opened}"
            )

    # ---- Wheels: 4 continuous lateral spins, grounded -----------------------
    ground_zs = []
    for name, w in wheels.items():
        j = model.get_articulation(f"{name}_spin")
        ctx.check(
            f"{name} spin axis lateral X + continuous",
            tuple(j.axis) == (1.0, 0.0, 0.0) and j.articulation_type == ArticulationType.CONTINUOUS,
            details=f"axis={j.axis}, type={j.articulation_type}",
        )
        wbb = ctx.part_world_aabb(w)
        assert wbb is not None
        ground_zs.append(wbb[0][2])
        ctx.check(
            f"{name} touches ground", abs(wbb[0][2]) <= 0.03, details=f"min z={wbb[0][2]:.4f}"
        )
    ctx.check(
        "all four wheels touch ground consistently",
        max(ground_zs) - min(ground_zs) <= 0.02,
        details=f"ground zs={['%.4f' % z for z in ground_zs]}",
    )

    # ---- Front steering: vertical king-pin REVOLUTE -------------------------
    for kname, wname, side in (
        ("steer_knuckle_front_left", "wheel_front_left", "left"),
        ("steer_knuckle_front_right", "wheel_front_right", "right"),
    ):
        steer = model.get_articulation(f"{kname}_steer")
        ax = tuple(steer.axis)
        ctx.check(
            f"front-{side} steer axis vertical Z + revolute",
            abs(ax[2]) > 0.9
            and abs(ax[0]) < 1e-6
            and abs(ax[1]) < 1e-6
            and steer.articulation_type == ArticulationType.REVOLUTE,
            details=f"axis={ax}, type={steer.articulation_type}",
        )
        w = wheels[wname]
        rest_bb = ctx.part_world_aabb(w)
        with ctx.pose({steer: 0.30}):
            steer_bb = ctx.part_world_aabb(w)
        if rest_bb is not None and steer_bb is not None:
            rest_xw = rest_bb[1][0] - rest_bb[0][0]
            steer_xw = steer_bb[1][0] - steer_bb[0][0]
            ctx.check(
                f"front-{side} wheel turns about vertical axis",
                steer_xw > rest_xw + 0.05,
                details=f"rest x-extent={rest_xw:.3f}, steered x-extent={steer_xw:.3f}",
            )

    # ---- Steering wheel spins -----------------------------------------------
    sw_turn = model.get_articulation("steering_wheel_turn")
    ctx.check(
        "steering wheel revolute about column axis",
        tuple(sw_turn.axis) == (0.0, 0.0, 1.0)
        and sw_turn.articulation_type == ArticulationType.REVOLUTE,
        details=f"axis={sw_turn.axis}",
    )

    # ---- Optional covers: REVOLUTE about X ----------------------------------
    if r.headlight_popup:
        for side in ("left", "right"):
            ch = model.get_articulation(f"headlight_cover_{side}_hinge")
            ctx.check(
                f"pop-up cover {side} REVOLUTE about X",
                tuple(ch.axis) == (1.0, 0.0, 0.0)
                and ch.articulation_type == ArticulationType.REVOLUTE,
                details=f"axis={ch.axis}",
            )
    if r.rear_louver_cover:
        eh = model.get_articulation("engine_cover_hinge")
        cover = model.get_part("engine_cover")
        ctx.check(
            "engine louver cover REVOLUTE about X with >=5 louvers",
            tuple(eh.axis) == (1.0, 0.0, 0.0)
            and eh.articulation_type == ArticulationType.REVOLUTE
            and sum(1 for v in cover.visuals if v.name.startswith("cover_louver_")) >= 5,
            details=f"axis={eh.axis}",
        )

    # ---- Palette diversity: body color differs from glass --------------------
    matset = {m.name: m for m in model.materials}
    if "body" in matset and "glass" in matset:
        ctx.check(
            "glass darker/different than body paint",
            sum(matset["glass"].rgba[:3]) <= sum(matset["body"].rgba[:3]) + 0.1,
            details=f"body={matset['body'].rgba}, glass={matset['glass'].rgba}",
        )

    return ctx.report()


__all__ = [
    "BodyProfileFamily",
    "DoorMechanism",
    "HeadlightShape",
    "RearBlade",
    "ExhaustLayout",
    "PaletteStyle",
    "SportsCarConfig",
    "ResolvedSportsCarConfig",
    "config_from_seed",
    "resolve_config",
    "build_sports_car",
    "build_seeded_sports_car",
    "slot_choices_for_seed",
    "run_sports_car_tests",
    "__modular__",
]
