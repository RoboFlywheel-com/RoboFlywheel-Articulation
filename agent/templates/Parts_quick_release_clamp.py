# SPDX-License-Identifier: Apache-2.0

"""Bicycle / seatpost-style quick-release clamp modular template.

Identity: a rigid split ``collar`` (open Omega throat or pinch-slit, or a
two-arc watchband hinge) wraps a seatpost bore. A ``cross_bolt`` runs along Y
through the two clamping feet; its +Y (cap-side) end carries a **quick-release
actuation** mechanism and its -Y (nut-side) end carries a spinnable **adjuster
nut**. The kinematics are exactly one REVOLUTE (the cam-over-center / folding /
hex-key actuation) + one CONTINUOUS (the adjuster nut about the bolt axis);
the ``hinged_collar`` collar style adds a second REVOLUTE ``barrel_hinge``.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Parts_quick_release_Handtools_Clamp.md`` and the
``picture/Parts/quick release clamp`` 5-star pool (1 baseline parent + 6 slot
forks), read directly from ``articraft_data/data/records/``.

Pattern = ``parallel_children`` (3 fixed named slots, NO multiplicity axis):

  * ``collar_style`` (3): omega_split_ring / pinch_collar / hinged_collar.
    omega/pinch are a single rigid ``collar`` root; hinged_collar re-parents the
    structure into ``cam_arc`` (root) + ``nut_arc`` joined by a visible
    ``barrel_hinge`` REVOLUTE z, and the nut joint re-parents to ``nut_arc``
    with a ``-HINGE_X`` X offset (S3 structural side effect).
  * ``actuation_style`` (3): cam_over_center_lever (REVOLUTE z) /
    fold_flat_lever (REVOLUTE x) / recessed_hex_bolt (REVOLUTE -x). Each emits
    its own fixed cap-side support hardware (cam barrel / bolt-head clevis /
    socket head) onto the collar root and sets the cross-bolt +Y span.
  * ``nut_style`` (3): knurled_barrel_nut / winged_thumb_nut / domed_acorn_nut.
    All reuse the ``adjuster_nut_spin`` CONTINUOUS y joint, seated against the
    nut-side thrust washer.

3 collar x 3 actuation x 3 nut = 27 distinct topologies (>= 10 gate).

Rule notes:
  * Lips / grooves / washers / barrels / bolt heads / fork cheeks are
    ``parent.visual(...)`` decorations on the collar root, never FIXED joints.
  * cam lever + adjuster nut joints declare MatingContracts to real visuals
    (cam barrel / thrust washer). The captured-pin joints (fold-lever eye on
    pin, hex-key knuckle in socket, barrel hinge pin) are grandfathered and
    guarded by element-scoped ``allow_overlap``, mirroring each source record.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from math import cos, pi, radians, sin
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    KnobBore,
    KnobGeometry,
    KnobGrip,
    MatingContract,
    MotionLimits,
    MotionProperties,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

CollarStyle = Literal["omega_split_ring", "pinch_collar", "hinged_collar"]
ActuationStyle = Literal["cam_over_center_lever", "fold_flat_lever", "recessed_hex_bolt"]
NutStyle = Literal["knurled_barrel_nut", "winged_thumb_nut", "domed_acorn_nut"]
PaletteStyle = Literal[
    "brushed_aluminum",
    "black_anodized",
    "red_anodized",
    "blue_anodized",
    "polished_chrome",
    "gunmetal",
]

COLLAR_STYLES: tuple[CollarStyle, ...] = (
    "omega_split_ring",
    "pinch_collar",
    "hinged_collar",
)
ACTUATION_STYLES: tuple[ActuationStyle, ...] = (
    "cam_over_center_lever",
    "fold_flat_lever",
    "recessed_hex_bolt",
)
NUT_STYLES: tuple[NutStyle, ...] = (
    "knurled_barrel_nut",
    "winged_thumb_nut",
    "domed_acorn_nut",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brushed_aluminum",
    "black_anodized",
    "red_anodized",
    "blue_anodized",
    "polished_chrome",
    "gunmetal",
)

# Realistic clamp colorways. Keys: body / lever / nut / steel / dark / light.
# brushed_aluminum is the verbatim 5-star source palette; the rest are common
# anodized / plated finishes for aluminum seat clamps.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "brushed_aluminum": {
        "body": (0.66, 0.67, 0.69, 1.0),
        "lever": (0.72, 0.73, 0.75, 1.0),
        "nut": (0.69, 0.70, 0.72, 1.0),
        "steel": (0.55, 0.56, 0.58, 1.0),
        "dark": (0.42, 0.43, 0.45, 1.0),
        "light": (0.82, 0.83, 0.84, 1.0),
    },
    "black_anodized": {
        "body": (0.07, 0.07, 0.08, 1.0),
        "lever": (0.11, 0.11, 0.12, 1.0),
        "nut": (0.09, 0.09, 0.10, 1.0),
        "steel": (0.55, 0.56, 0.58, 1.0),
        "dark": (0.03, 0.03, 0.03, 1.0),
        "light": (0.34, 0.34, 0.36, 1.0),
    },
    "red_anodized": {
        "body": (0.55, 0.06, 0.06, 1.0),
        "lever": (0.70, 0.10, 0.10, 1.0),
        "nut": (0.60, 0.07, 0.07, 1.0),
        "steel": (0.55, 0.56, 0.58, 1.0),
        "dark": (0.28, 0.02, 0.02, 1.0),
        "light": (0.86, 0.40, 0.40, 1.0),
    },
    "blue_anodized": {
        "body": (0.10, 0.21, 0.46, 1.0),
        "lever": (0.14, 0.30, 0.62, 1.0),
        "nut": (0.12, 0.24, 0.52, 1.0),
        "steel": (0.55, 0.56, 0.58, 1.0),
        "dark": (0.05, 0.10, 0.24, 1.0),
        "light": (0.50, 0.64, 0.86, 1.0),
    },
    "polished_chrome": {
        "body": (0.80, 0.81, 0.83, 1.0),
        "lever": (0.86, 0.87, 0.89, 1.0),
        "nut": (0.83, 0.84, 0.86, 1.0),
        "steel": (0.62, 0.63, 0.65, 1.0),
        "dark": (0.50, 0.51, 0.53, 1.0),
        "light": (0.93, 0.94, 0.95, 1.0),
    },
    "gunmetal": {
        "body": (0.29, 0.31, 0.34, 1.0),
        "lever": (0.36, 0.38, 0.41, 1.0),
        "nut": (0.32, 0.34, 0.37, 1.0),
        "steel": (0.52, 0.53, 0.55, 1.0),
        "dark": (0.16, 0.17, 0.19, 1.0),
        "light": (0.58, 0.60, 0.63, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Nominal layout constants (meters). World frame: +Z is the collar bore axis,
# the throat/slit faces -X, the cross bolt runs along Y. All values verbatim
# from the 5-star sources unless noted (S1..S7 in the spec).
# ---------------------------------------------------------------------------
BORE_R0 = 0.016
WALL = 0.005
BAND_H0 = 0.015

# Omega throat (S1).
THROAT_OPEN_OUT = 0.0098
THROAT_APEX_X = 0.0015

# Pinch slit (S2).
PINCH_SLIT_HALF_W = 0.0006

# Lugs / pivot / bolt / washers (fixed hardware, do not scale with bore).
LUG_X_MIN, LUG_X_MAX = -0.038, -0.016
LUG_Y_IN, LUG_Y_OUT = 0.0050, 0.0100
LUG_LEN = LUG_X_MAX - LUG_X_MIN
LUG_XC = 0.5 * (LUG_X_MIN + LUG_X_MAX)
LUG_T = LUG_Y_OUT - LUG_Y_IN
LUG_YC = 0.5 * (LUG_Y_IN + LUG_Y_OUT)

PIVOT_X = -0.0305
BOLT_R = 0.0025
BOLT_Y_MIN = -0.0225

WASHER_R = 0.0064
WASHER_LEN = 0.0016

# cam_over_center_lever hardware (S1).
BARREL_R = 0.0057
BARREL_LEN = 0.0110
VISIBLE_BARREL_LEN = 0.0010
LEVER_YC = LUG_Y_OUT + WASHER_LEN + 0.0004 + 0.5 * BARREL_LEN
HANDLE_Z_HALF = 0.0030
CAM_BOLT_Y_MAX = 0.0250
CAM_OPEN = radians(170.0)

# fold_flat_lever hardware (S4).
HEAD_R = 0.0059
HEAD_LEN = 0.0046
HEAD_YC = LUG_Y_OUT + WASHER_LEN + 0.0003 + 0.5 * HEAD_LEN
HINGE_Y = 0.0224
PIN_R = 0.00255
PIN_LEN = 0.0185
LEVER_EYE_R = 0.0054
LEVER_PIN_CLEAR_R = 0.00255
LEVER_EYE_HALF_X = 0.0050
FORK_CHEEK_T = 0.0022
FORK_CHEEK_LEN = 0.0082
FORK_CHEEK_H = 0.0115
FORK_CHEEK_X = 0.0068
LEVER_Z_HALF = 0.00155
FOLD_LEVER_LEN = 0.060
FOLD_BOLT_Y_MAX = 0.0162
FOLD_OPEN = radians(95.0)

# recessed_hex_bolt hardware (S5).
SOCKET_HEAD_R = 0.0072
SOCKET_HEAD_LEN = 0.0085
SOCKET_HEAD_YC = LUG_Y_OUT + 0.5 * WASHER_LEN + SOCKET_HEAD_LEN
SOCKET_FACE_Y = SOCKET_HEAD_YC + SOCKET_HEAD_LEN
SOCKET_RECESS_DEPTH = 0.0044
SOCKET_RECESS_D = 0.0065
HEX_KEY_D = 0.0030
HEX_KEY_ARM_LEN = 0.038
HEX_KEY_ARM_Y = 0.00145
HEX_KEY_HINGE_R = 0.00165
HEX_KEY_HINGE_LEN = 0.0050
HEX_BOLT_Y_MAX = 0.0225
HEX_OPEN = radians(92.0)

# hinged_collar hardware (S3).
HINGE_R = 0.0030
HINGE_PIN_R = 0.00105
HINGE_SPLIT_ANGLE = radians(13.0)
CLAMP_END_ANGLE = radians(151.5)
HINGE_OPEN = radians(62.0)

# Nut nominal sizes per style.
KNURLED_NUT_D = 0.022
WING_NUT_D = 0.014
ACORN_NUT_D = 0.022
NUT_LEN0 = 0.020
WING_RADIAL_LEN = 0.0130
WING_AXIAL_LEN = 0.0070
WING_THICKNESS = 0.0045
WING_OUTBOARD_Z = 0.0035

_BOLT_Y_MAX = {
    "cam_over_center_lever": CAM_BOLT_Y_MAX,
    "fold_flat_lever": FOLD_BOLT_Y_MAX,
    "recessed_hex_bolt": HEX_BOLT_Y_MAX,
}
_NUT_D = {
    "knurled_barrel_nut": KNURLED_NUT_D,
    "winged_thumb_nut": WING_NUT_D,
    "domed_acorn_nut": ACORN_NUT_D,
}
_ACT_OPEN = {
    "cam_over_center_lever": CAM_OPEN,
    "fold_flat_lever": FOLD_OPEN,
    "recessed_hex_bolt": HEX_OPEN,
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class QuickReleaseClampConfig:
    collar_style: CollarStyle | None = None
    actuation_style: ActuationStyle | None = None
    nut_style: NutStyle | None = None
    palette_style: PaletteStyle = "brushed_aluminum"
    bore_radius_scale: float = 1.0
    band_height_scale: float = 1.0
    lever_reach_scale: float = 1.0
    nut_len_scale: float = 1.0
    name: str = "quick_release_clamp"


@dataclass(frozen=True)
class ResolvedQuickReleaseClampConfig:
    collar_style: CollarStyle
    actuation_style: ActuationStyle
    nut_style: NutStyle
    palette_style: PaletteStyle
    bore_r: float
    outer_r: float
    band_h: float
    pivot_z: float
    bolt_y_max: float
    nut_d: float
    nut_len: float
    nut_yc: float
    hinge_x: float
    lever_scale: float
    act_open: float
    name: str

    @property
    def is_hinged(self) -> bool:
        return self.collar_style == "hinged_collar"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> QuickReleaseClampConfig:
    rng = random.Random(seed)
    return QuickReleaseClampConfig(
        collar_style=rng.choice(COLLAR_STYLES),
        actuation_style=rng.choice(ACTUATION_STYLES),
        nut_style=rng.choice(NUT_STYLES),
        palette_style=rng.choice(PALETTE_STYLES),
        bore_radius_scale=round(rng.uniform(0.85, 1.20), 4),
        band_height_scale=round(rng.uniform(0.85, 1.25), 4),
        lever_reach_scale=round(rng.uniform(0.85, 1.25), 4),
        nut_len_scale=round(rng.uniform(0.85, 1.20), 4),
        name=f"seeded_quick_release_clamp_{seed}",
    )


def resolve_config(
    config: QuickReleaseClampConfig | None = None,
) -> ResolvedQuickReleaseClampConfig:
    cfg = config or QuickReleaseClampConfig()
    collar_style = _pick(cfg.collar_style, COLLAR_STYLES)
    actuation_style = _pick(cfg.actuation_style, ACTUATION_STYLES)
    nut_style = _pick(cfg.nut_style, NUT_STYLES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    bore_scale = _clamp(cfg.bore_radius_scale, 0.85, 1.20)
    height_scale = _clamp(cfg.band_height_scale, 0.85, 1.25)
    lever_scale = _clamp(cfg.lever_reach_scale, 0.85, 1.25)
    nut_scale = _clamp(cfg.nut_len_scale, 0.85, 1.20)

    bore_r = BORE_R0 * bore_scale
    outer_r = bore_r + WALL
    band_h = BAND_H0 * height_scale
    pivot_z = 0.5 * band_h

    bolt_y_max = _BOLT_Y_MAX[actuation_style]
    nut_d = _NUT_D[nut_style]
    nut_len = NUT_LEN0 * nut_scale
    # Equation (spec): keep the nut +Y face seated against the thrust washer.
    nut_yc = -LUG_Y_OUT - WASHER_LEN - 0.0004 - 0.5 * nut_len
    hinge_x = outer_r + 0.0040

    return ResolvedQuickReleaseClampConfig(
        collar_style=collar_style,
        actuation_style=actuation_style,
        nut_style=nut_style,
        palette_style=palette_style,
        bore_r=bore_r,
        outer_r=outer_r,
        band_h=band_h,
        pivot_z=pivot_z,
        bolt_y_max=bolt_y_max,
        nut_d=nut_d,
        nut_len=nut_len,
        nut_yc=nut_yc,
        hinge_x=hinge_x,
        lever_scale=lever_scale,
        act_open=_ACT_OPEN[actuation_style],
        name=cfg.name or "quick_release_clamp",
    )


def slot_choices_for_config(
    config: QuickReleaseClampConfig | ResolvedQuickReleaseClampConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedQuickReleaseClampConfig) else resolve_config(config)
    return (
        ("collar", r.collar_style),
        ("actuation", r.actuation_style),
        ("nut", r.nut_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared collar geometry helpers (adapted from S1 / S2 / S3).
# ---------------------------------------------------------------------------
def _throat_notch_solid(outer_r: float, band_h: float) -> cq.Workplane:
    """Wedge sector removed from the -X side to open the ring into an Omega (S1)."""
    return (
        cq.Workplane("XY")
        .polyline(
            [
                (THROAT_APEX_X, 0.0),
                (-(outer_r + 0.005), THROAT_OPEN_OUT),
                (-(outer_r + 0.005), -THROAT_OPEN_OUT),
            ]
        )
        .close()
        .extrude(band_h + 0.012)
        .translate((0.0, 0.0, -0.006))
    )


def _pinch_slit_solid(bore_r: float, outer_r: float, band_h: float) -> cq.Workplane:
    """Thin radial saw-cut through the -X wall of the pinch collar (S2)."""
    x_in = -bore_r - 0.00025
    x_out = -outer_r - 0.0020
    return (
        cq.Workplane("XY")
        .rect(abs(x_out - x_in), 2.0 * PINCH_SLIT_HALF_W)
        .extrude(band_h + 0.012)
        .translate((0.5 * (x_in + x_out), 0.0, -0.006))
    )


def _collar_band_solid(
    bore_r: float, outer_r: float, band_h: float, *, opening: cq.Workplane
) -> cq.Workplane:
    band = cq.Workplane("XY").circle(outer_r).circle(bore_r).extrude(band_h)
    cb_r = outer_r - 0.0035
    counterbore = cq.Workplane("XY", origin=(0.0, 0.0, band_h - 0.005)).circle(cb_r).extrude(0.007)
    band = band.cut(counterbore)
    return band.cut(opening)


def _annular_ring_solid(
    inner_r: float, outer_r: float, height: float, *, opening: cq.Workplane | None
) -> cq.Workplane:
    ring = cq.Workplane("XY").circle(outer_r).circle(inner_r).extrude(height)
    if opening is not None:
        ring = ring.cut(opening)
    return ring


def _lug_solid(yc: float, band_h: float) -> cq.Workplane:
    lug = (
        cq.Workplane("XY")
        .box(LUG_LEN, LUG_T, band_h, centered=(True, True, True))
        .edges("|Z")
        .fillet(0.0010)
        .edges(">Z or <Z")
        .fillet(0.00045)
    )
    return lug.translate((LUG_XC, yc, 0.5 * band_h))


def _annular_washer_solid(inner_r: float, outer_r: float, height: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(outer_r).circle(inner_r).extrude(height)


def _washer_solid() -> cq.Workplane:
    return _annular_washer_solid(BOLT_R * 0.8, WASHER_R, WASHER_LEN)


# --- hinged arc helpers (S3) -----------------------------------------------
def _arc_profile_points(
    side: int, inner_r: float, outer_r: float, *, samples: int = 54
) -> list[tuple[float, float]]:
    if side > 0:
        start, end = HINGE_SPLIT_ANGLE, CLAMP_END_ANGLE
    else:
        start, end = -CLAMP_END_ANGLE, -HINGE_SPLIT_ANGLE
    outer = [
        (
            outer_r * cos(start + (end - start) * i / samples),
            outer_r * sin(start + (end - start) * i / samples),
        )
        for i in range(samples + 1)
    ]
    inner = [
        (
            inner_r * cos(end + (start - end) * i / samples),
            inner_r * sin(end + (start - end) * i / samples),
        )
        for i in range(samples + 1)
    ]
    return outer + inner


def _arc_band_solid(side: int, inner_r: float, outer_r: float, height: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .polyline(_arc_profile_points(side, inner_r, outer_r))
        .close()
        .extrude(height)
    )


def _collar_arc_solid(side: int, bore_r: float, outer_r: float, band_h: float) -> cq.Workplane:
    arc = _arc_band_solid(side, bore_r, outer_r, band_h)
    cb_r = outer_r - 0.0035
    counterbore = _arc_band_solid(side, bore_r, cb_r, 0.007).translate((0.0, 0.0, band_h - 0.005))
    return arc.cut(counterbore)


def _arc_lug_solid(yc: float, band_h: float, pivot_z: float) -> cq.Workplane:
    bolt_hole = (
        cq.Workplane("XZ")
        .center(PIVOT_X, pivot_z)
        .circle(BOLT_R * 1.18)
        .extrude(LUG_T + 0.006, both=True)
        .translate((0.0, yc, 0.0))
    )
    lug = (
        cq.Workplane("XY")
        .box(LUG_LEN, LUG_T, band_h, centered=(True, True, True))
        .edges("|Z")
        .fillet(0.0010)
        .edges(">Z or <Z")
        .fillet(0.00045)
    )
    return lug.translate((LUG_XC, yc, 0.5 * band_h)).cut(bolt_hole)


def _hinge_leaf_solid(side: int, outer_r: float, hinge_x: float, band_h: float) -> cq.Workplane:
    y_inner = 0.0008 * side
    y_outer = 0.0060 * side
    leaf = (
        cq.Workplane("XY")
        .polyline(
            [
                (outer_r - 0.0010, y_inner),
                (hinge_x, y_inner),
                (hinge_x, y_outer),
                (outer_r - 0.0014, y_outer),
            ]
        )
        .close()
        .extrude(band_h)
    )
    return leaf.edges("|Z").fillet(0.00065)


def _vertical_tube_solid(inner_r: float, outer_r: float, height: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(outer_r).circle(inner_r).extrude(height)


def _hinge_pin_solid(hinge_x: float, band_h: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .circle(HINGE_PIN_R)
        .extrude(band_h + 0.0012)
        .translate((hinge_x, 0.0, -0.0006))
    )


# ---------------------------------------------------------------------------
# Actuation geometry helpers (cam / fold / hex).
# ---------------------------------------------------------------------------
def _scaled(points: list[tuple[float, float]], s: float) -> list[tuple[float, float]]:
    return [(x * s, y * s) for x, y in points]


def _lever_handle_solid(scale: float = 1.0) -> cq.Workplane:
    """One-piece solid cam-over-center handle (S1). Blade swept by ``scale``;
    the hub radius is fixed so the -Y mating face stays put."""
    blade = (
        cq.Workplane("XY")
        .moveTo(-0.0085 * scale, -0.0040 * scale)
        .spline(
            _scaled(
                [
                    (-0.0020, 0.0070),
                    (0.0110, 0.0185),
                    (0.0270, 0.0300),
                    (0.0450, 0.0360),
                    (0.0585, 0.0345),
                ],
                scale,
            ),
            includeCurrent=True,
        )
        .spline(
            _scaled(
                [
                    (0.0560, 0.0270),
                    (0.0400, 0.0200),
                    (0.0240, 0.0120),
                    (0.0100, 0.0050),
                    (0.0010, 0.0008),
                    (-0.0070, 0.0005),
                ],
                scale,
            ),
            includeCurrent=True,
        )
        .close()
        .extrude(HANDLE_Z_HALF, both=True)
    )
    hub = cq.Workplane("XY").circle(0.0072).extrude(HANDLE_Z_HALF + 0.0006, both=True)
    return hub.union(blade)


def _folding_lever_solid(scale: float = 1.0) -> cq.Workplane:
    """Flat folding lever with a bored hinge eye (S4). Blade length scaled."""
    tip = FOLD_LEVER_LEN * scale
    eye = (
        cq.Workplane("YZ")
        .circle(LEVER_EYE_R)
        .circle(LEVER_PIN_CLEAR_R)
        .extrude(LEVER_EYE_HALF_X, both=True)
    )
    blade = (
        cq.Workplane("XY")
        .moveTo(-0.0043, 0.0008)
        .spline(
            [(-0.0045, 0.018 * scale), (-0.0069, 0.039 * scale), (-0.0046, tip)],
            includeCurrent=True,
        )
        .radiusArc((0.0046, tip), 0.0046)
        .spline(
            [(0.0069, 0.039 * scale), (0.0045, 0.018 * scale), (0.0043, 0.0008)],
            includeCurrent=True,
        )
        .close()
        .extrude(LEVER_Z_HALF, both=True)
    )
    spine = (
        cq.Workplane("XY")
        .moveTo(-0.0022, 0.0070)
        .lineTo(-0.0016, 0.047 * scale)
        .radiusArc((0.0016, 0.047 * scale), 0.0016)
        .lineTo(0.0022, 0.0070)
        .close()
        .extrude(0.00045)
        .translate((0.0, 0.0, LEVER_Z_HALF - 0.00005))
    )
    solid = eye.union(blade).union(spine)
    pivot_bore = cq.Workplane("YZ").circle(LEVER_PIN_CLEAR_R).extrude(0.012, both=True)
    return solid.cut(pivot_bore)


def _fork_cheek_solid(xc: float, bolt_y_max: float, pivot_z: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(FORK_CHEEK_T, FORK_CHEEK_LEN, FORK_CHEEK_H, centered=(True, True, True))
        .edges("|Z")
        .fillet(0.00045)
        .edges(">Z or <Z")
        .fillet(0.00025)
        .translate((xc, 0.5 * (bolt_y_max + HINGE_Y), pivot_z))
    )


def _socket_head_solid() -> cq.Workplane:
    head = cq.Workplane("XZ").circle(SOCKET_HEAD_R).extrude(SOCKET_HEAD_LEN, both=True)
    recess = (
        cq.Workplane("XZ", origin=(0.0, 0.5 * SOCKET_HEAD_LEN + 0.0002, 0.0))
        .polygon(6, SOCKET_RECESS_D)
        .extrude(-(SOCKET_RECESS_DEPTH + 0.0004))
    )
    return head.cut(recess)


def _hex_socket_floor_solid() -> cq.Workplane:
    y_floor = 0.5 * SOCKET_HEAD_LEN - SOCKET_RECESS_DEPTH + 0.00008
    return (
        cq.Workplane("XZ", origin=(0.0, y_floor, 0.0))
        .polygon(6, SOCKET_RECESS_D * 1.25)
        .extrude(-0.00016)
    )


def _hex_drive_bit_solid() -> cq.Workplane:
    return cq.Workplane("XZ").polygon(6, HEX_KEY_D).extrude(SOCKET_RECESS_DEPTH - 0.00055)


def _hex_key_hinge_solid() -> cq.Workplane:
    return cq.Workplane("YZ").circle(HEX_KEY_HINGE_R).extrude(HEX_KEY_HINGE_LEN, both=True)


def _folding_hex_key_arm_solid(scale: float = 1.0) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .polygon(6, HEX_KEY_D)
        .extrude(HEX_KEY_ARM_LEN * scale)
        .translate((0.0, HEX_KEY_ARM_Y, 0.0))
    )


# ---------------------------------------------------------------------------
# Nut geometry helpers (S1 / S6 / S7).
# ---------------------------------------------------------------------------
def _knurled_nut_geometry(nut_d: float, nut_len: float) -> KnobGeometry:
    return KnobGeometry(
        nut_d,
        nut_len,
        body_style="cylindrical",
        edge_radius=0.0008,
        grip=KnobGrip(style="knurled", count=40, depth=0.0006, helix_angle_deg=0.0),
        bore=KnobBore(style="round", diameter=0.0046, through=False),
        center=True,
    )


def _thumb_nut_hub_solid(nut_d: float, nut_len: float) -> cq.Workplane:
    hub = (
        cq.Workplane("XY")
        .circle(0.5 * nut_d)
        .circle(BOLT_R * 0.8)
        .extrude(0.5 * nut_len, both=True)
    )
    end_rim = (
        cq.Workplane("XY", origin=(0.0, 0.0, -0.5 * nut_len - 0.00005))
        .circle(0.5 * nut_d + 0.00035)
        .circle(BOLT_R * 1.05)
        .extrude(0.00055)
    )
    shoulder_rim = (
        cq.Workplane("XY", origin=(0.0, 0.0, 0.5 * nut_len - 0.00050))
        .circle(0.5 * nut_d + 0.00020)
        .circle(BOLT_R * 0.8)
        .extrude(0.00050)
    )
    return hub.union(end_rim).union(shoulder_rim)


def _thumb_wing_solid(index: int, nut_d: float) -> cq.Workplane:
    sign = 1.0 if index == 0 else -1.0
    radial_center = sign * (0.5 * nut_d + 0.5 * WING_RADIAL_LEN - 0.0007)
    wing = (
        cq.Workplane("XY")
        .box(WING_RADIAL_LEN, WING_THICKNESS, WING_AXIAL_LEN, centered=(True, True, True))
        .edges("|Z")
        .fillet(0.0016)
        .edges(">Z or <Z")
        .fillet(0.00045)
    )
    return wing.translate((radial_center, 0.0, WING_OUTBOARD_Z))


def _acorn_cap_nut_solid(nut_d: float, nut_len: float) -> cq.Workplane:
    acorn_hex_r = 0.5 * nut_d
    acorn_z_min = -0.5 * nut_len
    acorn_hex_len = 0.0110
    acorn_hex_top = acorn_z_min + acorn_hex_len
    acorn_shoulder_h = 0.0011
    acorn_dome_base_z = acorn_hex_top + 0.0007
    acorn_dome_r = 0.5 * nut_len - acorn_dome_base_z
    acorn_bore_r = BOLT_R * 0.90
    acorn_bore_depth = acorn_hex_len + 0.0020

    hex_pts = [(acorn_hex_r * cos(i * pi / 3.0), acorn_hex_r * sin(i * pi / 3.0)) for i in range(6)]
    hex_base = (
        cq.Workplane("XY")
        .polyline(hex_pts)
        .close()
        .extrude(acorn_hex_len)
        .translate((0.0, 0.0, acorn_z_min))
        .edges("|Z")
        .chamfer(0.00045)
        .edges(">Z or <Z")
        .chamfer(0.00035)
    )
    shoulder = (
        cq.Workplane("XY")
        .circle(acorn_dome_r)
        .extrude(acorn_shoulder_h)
        .translate((0.0, 0.0, acorn_hex_top - 0.0002))
    )
    lower_half_cutter = (
        cq.Workplane("XY")
        .box(0.040, 0.040, 0.040, centered=(True, True, False))
        .translate((0.0, 0.0, acorn_dome_base_z - 0.040))
    )
    dome = (
        cq.Workplane("XY")
        .sphere(acorn_dome_r)
        .translate((0.0, 0.0, acorn_dome_base_z))
        .cut(lower_half_cutter)
    )
    thread_bore = (
        cq.Workplane("XY")
        .circle(acorn_bore_r)
        .extrude(acorn_bore_depth)
        .translate((0.0, 0.0, acorn_z_min - 0.0002))
    )
    return hex_base.union(shoulder).union(dome).cut(thread_bore)


# ---------------------------------------------------------------------------
# Collar builders (Slot A). Each returns (collar_root, nut_carrier, nut_x).
# ---------------------------------------------------------------------------
def _emit_machined_trim(part, r, mats, *, opening_factory, assets) -> None:
    """Lips + grooves (parent visuals, Rule 1) on a single-piece collar band."""
    for z, name in ((0.0004, "lower_machined_lip"), (r.band_h - 0.0008, "upper_machined_lip")):
        part.visual(
            mesh_from_cadquery(
                _annular_ring_solid(
                    r.bore_r + 0.0004, r.outer_r + 0.0003, 0.00045, opening=opening_factory()
                ),
                name,
                assets=assets,
            ),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=mats["light"],
            name=name, material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
        )
    for z, name in ((0.0043, "lower_brushed_groove"), (0.0107, "upper_brushed_groove")):
        part.visual(
            mesh_from_cadquery(
                _annular_ring_solid(
                    r.outer_r + 0.00005, r.outer_r + 0.00025, 0.00018, opening=opening_factory()
                ),
                name,
                assets=assets,
            ),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=mats["dark"],
            name=name, material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
        )


def _emit_cross_bolt_and_washers(part, r, mats, *, nut_carrier, nut_x, assets) -> None:
    """Cross bolt + cap-side washer on the root; nut-side washer on nut_carrier."""
    part.visual(
        Cylinder(radius=BOLT_R, length=r.bolt_y_max - BOLT_Y_MIN),
        origin=Origin(
            xyz=(PIVOT_X, 0.5 * (BOLT_Y_MIN + r.bolt_y_max), r.pivot_z),
            rpy=(pi / 2.0, 0.0, 0.0),
        ),
        material=mats["steel"],
        name="cross_bolt", material_class_id="metal.steel_bare",
    )
    part.visual(
        mesh_from_cadquery(_washer_solid(), "cap_side_thrust_washer", assets=assets),
        origin=Origin(
            xyz=(PIVOT_X, LUG_Y_OUT + 0.5 * WASHER_LEN, r.pivot_z), rpy=(pi / 2.0, 0.0, 0.0)
        ),
        material=mats["light"],
        name="cap_side_thrust_washer", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    # On a single-piece collar the nut washer grips the cross_bolt; on the hinged
    # nut_arc the bolt lives on cam_arc, so nudge the washer +Y into the nut lug
    # face so it stays connected to its own part (mirrors S3).
    nut_washer_nudge = 0.0013 if abs(nut_x) > 1e-9 else 0.0
    nut_carrier.visual(
        mesh_from_cadquery(_washer_solid(), "nut_side_thrust_washer", assets=assets),
        origin=Origin(
            xyz=(PIVOT_X + nut_x, -LUG_Y_OUT - 0.5 * WASHER_LEN + nut_washer_nudge, r.pivot_z),
            rpy=(pi / 2.0, 0.0, 0.0),
        ),
        material=mats["light"],
        name="nut_side_thrust_washer", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )


def _emit_single_piece_collar(model, r, mats, *, opening_factory, assets):
    collar = model.part("collar")
    collar.visual(
        mesh_from_cadquery(
            _collar_band_solid(r.bore_r, r.outer_r, r.band_h, opening=opening_factory()),
            "collar_band",
            assets=assets,
        ),
        material=mats["body"],
        name="collar_band", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    collar.visual(
        mesh_from_cadquery(_lug_solid(LUG_YC, r.band_h), "lug_cap_side", assets=assets),
        material=mats["body"],
        name="lug_cap_side", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    collar.visual(
        mesh_from_cadquery(_lug_solid(-LUG_YC, r.band_h), "lug_nut_side", assets=assets),
        material=mats["body"],
        name="lug_nut_side", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    _emit_machined_trim(collar, r, mats, opening_factory=opening_factory, assets=assets)
    _emit_cross_bolt_and_washers(collar, r, mats, nut_carrier=collar, nut_x=0.0, assets=assets)
    collar.inertial = Inertial.from_geometry(
        Box((0.055, 0.030, r.band_h)),
        mass=0.07,
        origin=Origin(xyz=(PIVOT_X * 0.4, 0.0, r.pivot_z)),
    )
    return collar, collar, 0.0


def _build_omega_collar(model, r, mats, *, assets):
    return _emit_single_piece_collar(
        model,
        r,
        mats,
        opening_factory=lambda: _throat_notch_solid(r.outer_r, r.band_h),
        assets=assets,
    )


def _build_pinch_collar(model, r, mats, *, assets):
    return _emit_single_piece_collar(
        model,
        r,
        mats,
        opening_factory=lambda: _pinch_slit_solid(r.bore_r, r.outer_r, r.band_h),
        assets=assets,
    )


def _build_hinged_collar(model, r, mats, *, assets):
    """Two half-arc watchband collar (S3): cam_arc root + nut_arc on barrel_hinge."""
    cam_arc = model.part("cam_arc")
    nut_arc = model.part("nut_arc")
    hinge_x = r.hinge_x

    def add_arc_visual(part, side, geometry, name, material):
        origin = Origin(xyz=(-hinge_x, 0.0, 0.0)) if side < 0 else Origin()
        part.visual(
            mesh_from_cadquery(geometry, name, assets=assets),
            origin=origin,
            material=material,
            name=name, material_class_id="metal.aluminum_bare",
        )

    for side, part, prefix, lug_y in (
        (1, cam_arc, "cam", LUG_YC),
        (-1, nut_arc, "nut", -LUG_YC),
    ):
        add_arc_visual(
            part,
            side,
            _collar_arc_solid(side, r.bore_r, r.outer_r, r.band_h),
            f"{prefix}_collar_arc",
            mats["body"],
        )
        add_arc_visual(
            part,
            side,
            _arc_lug_solid(lug_y, r.band_h, r.pivot_z),
            f"{prefix}_clamp_lug",
            mats["body"],
        )
        add_arc_visual(
            part,
            side,
            _hinge_leaf_solid(side, r.outer_r, hinge_x, r.band_h),
            f"{prefix}_hinge_leaf",
            mats["body"],
        )
        for i, z in enumerate((0.0004, r.band_h - 0.0008)):
            add_arc_visual(
                part,
                side,
                _arc_band_solid(side, r.bore_r + 0.0004, r.outer_r + 0.0003, 0.00045).translate(
                    (0.0, 0.0, z)
                ),
                f"{prefix}_machined_lip_{i}",
                mats["light"],
            )
        for i, z in enumerate((0.0043, 0.0107)):
            add_arc_visual(
                part,
                side,
                _arc_band_solid(side, r.outer_r + 0.00005, r.outer_r + 0.00025, 0.00018).translate(
                    (0.0, 0.0, z)
                ),
                f"{prefix}_brushed_groove_{i}",
                mats["dark"],
            )

    hinge_segment_h = 0.0046
    hinge_gap = 0.00035
    for i, z0 in enumerate((0.0, 2.0 * (hinge_segment_h + hinge_gap))):
        cam_arc.visual(
            mesh_from_cadquery(
                _vertical_tube_solid(HINGE_PIN_R, HINGE_R, hinge_segment_h).translate(
                    (hinge_x, 0.0, z0)
                ),
                f"cam_hinge_knuckle_{i}",
                assets=assets,
            ),
            material=mats["body"],
            name=f"cam_hinge_knuckle_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
        )
    nut_arc.visual(
        mesh_from_cadquery(
            _vertical_tube_solid(HINGE_PIN_R, HINGE_R, hinge_segment_h).translate(
                (hinge_x, 0.0, hinge_segment_h + hinge_gap)
            ),
            "nut_hinge_knuckle",
            assets=assets,
        ),
        origin=Origin(xyz=(-hinge_x, 0.0, 0.0)),
        material=mats["body"],
        name="nut_hinge_knuckle", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    cam_arc.visual(
        mesh_from_cadquery(_hinge_pin_solid(hinge_x, r.band_h), "barrel_hinge_pin", assets=assets),
        material=mats["steel"],
        name="barrel_hinge_pin", material_class_id="metal.steel_bare",
    )
    _emit_cross_bolt_and_washers(
        cam_arc, r, mats, nut_carrier=nut_arc, nut_x=-hinge_x, assets=assets
    )
    cam_arc.inertial = Inertial.from_geometry(
        Box((0.055, 0.020, r.band_h)),
        mass=0.05,
        origin=Origin(xyz=(PIVOT_X * 0.4, 0.006, r.pivot_z)),
    )
    nut_arc.inertial = Inertial.from_geometry(
        Box((0.040, 0.020, r.band_h)),
        mass=0.04,
        origin=Origin(xyz=(PIVOT_X * 0.4 - hinge_x, -0.006, r.pivot_z)),
    )

    model.articulation(
        "barrel_hinge",
        ArticulationType.REVOLUTE,
        parent=cam_arc,
        child=nut_arc,
        origin=Origin(xyz=(hinge_x, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=18.0, velocity=3.0, lower=0.0, upper=HINGE_OPEN),
        motion_properties=MotionProperties(damping=0.3, friction=0.08),
        # Grandfathered: the +X barrel hinge is a captured pin through interleaved
        # knuckles (barrel_hinge_pin <-> nut_hinge_knuckle), not an axis-aligned face pair.
    )
    return cam_arc, nut_arc, -hinge_x


_COLLAR_BUILDERS = {
    "omega_split_ring": _build_omega_collar,
    "pinch_collar": _build_pinch_collar,
    "hinged_collar": _build_hinged_collar,
}


# ---------------------------------------------------------------------------
# Actuation builders (Slot B). Each adds fixed cap-side hardware to collar_root,
# emits the moving child part, and the single REVOLUTE joint.
# ---------------------------------------------------------------------------
def _emit_cam_over_center(model, r, mats, *, collar_root, assets) -> list[str]:
    collar_root.visual(
        Cylinder(radius=BARREL_R, length=VISIBLE_BARREL_LEN),
        origin=Origin(
            xyz=(PIVOT_X, LUG_Y_OUT - 0.5 * VISIBLE_BARREL_LEN, r.pivot_z),
            rpy=(pi / 2.0, 0.0, 0.0),
        ),
        material=mats["lever"],
        name="fixed_cam_barrel", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    cam_lever = model.part("cam_lever")
    cam_lever.visual(
        mesh_from_cadquery(_lever_handle_solid(r.lever_scale), "lever_handle", assets=assets),
        material=mats["lever"],
        name="lever_handle", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    cam_lever.inertial = Inertial.from_geometry(
        Box((0.060 * r.lever_scale, 0.040 * r.lever_scale, 2.0 * HANDLE_Z_HALF)),
        mass=0.02,
        origin=Origin(xyz=(0.02 * r.lever_scale, 0.015 * r.lever_scale, 0.0)),
    )
    model.articulation(
        "lever_cam_pivot",
        ArticulationType.REVOLUTE,
        parent=collar_root,
        child=cam_lever,
        origin=Origin(xyz=(PIVOT_X, LEVER_YC, r.pivot_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=25.0, velocity=6.0, lower=0.0, upper=CAM_OPEN),
        motion_properties=MotionProperties(damping=0.2, friction=0.05),
        mating=MatingContract(
            parent_face_geometry="fixed_cam_barrel",
            parent_face_side="positive_y",
            child_face_geometry="lever_handle",
            child_face_side="negative_y",
            contact_tol=0.0015,
        ),
    )
    return ["cam_lever"]


def _emit_fold_flat_lever(model, r, mats, *, collar_root, assets) -> list[str]:
    collar_root.visual(
        Cylinder(radius=HEAD_R, length=HEAD_LEN),
        origin=Origin(xyz=(PIVOT_X, HEAD_YC, r.pivot_z), rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="bolt_head", material_class_id="metal.steel_bare",
    )
    for i, x in enumerate((PIVOT_X - FORK_CHEEK_X, PIVOT_X + FORK_CHEEK_X)):
        collar_root.visual(
            mesh_from_cadquery(
                _fork_cheek_solid(x, r.bolt_y_max, r.pivot_z), f"fork_cheek_{i}", assets=assets
            ),
            material=mats["steel"],
            name=f"fork_cheek_{i}", material_class_id="metal.steel_bare",
        )
    collar_root.visual(
        Cylinder(radius=PIN_R, length=PIN_LEN),
        origin=Origin(xyz=(PIVOT_X, HINGE_Y, r.pivot_z), rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["steel"],
        name="hinge_pin", material_class_id="metal.steel_bare",
    )
    for i, x in enumerate((PIVOT_X - 0.5 * PIN_LEN - 0.0006, PIVOT_X + 0.5 * PIN_LEN + 0.0006)):
        collar_root.visual(
            Cylinder(radius=PIN_R * 1.35, length=0.0012),
            origin=Origin(xyz=(x, HINGE_Y, r.pivot_z), rpy=(0.0, pi / 2.0, 0.0)),
            material=mats["light"],
            name=f"pin_head_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
        )
    folding_lever = model.part("folding_lever")
    folding_lever.visual(
        mesh_from_cadquery(_folding_lever_solid(r.lever_scale), "flat_lever", assets=assets),
        material=mats["lever"],
        name="flat_lever", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    folding_lever.inertial = Inertial.from_geometry(
        Box((0.012, FOLD_LEVER_LEN * r.lever_scale, 2.0 * LEVER_Z_HALF)),
        mass=0.015,
        origin=Origin(xyz=(0.0, 0.5 * FOLD_LEVER_LEN * r.lever_scale, 0.0)),
    )
    model.articulation(
        "lever_hinge",
        ArticulationType.REVOLUTE,
        parent=collar_root,
        child=folding_lever,
        origin=Origin(xyz=(PIVOT_X, HINGE_Y, r.pivot_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=25.0, velocity=6.0, lower=0.0, upper=FOLD_OPEN),
        motion_properties=MotionProperties(damping=0.2, friction=0.05),
        # Grandfathered: the flat lever eye is a zero-clearance captured pin around
        # hinge_pin (S4), guarded by element-scoped allow_overlap in run_tests.
    )
    return ["folding_lever"]


def _emit_recessed_hex(model, r, mats, *, collar_root, assets) -> list[str]:
    collar_root.visual(
        mesh_from_cadquery(_socket_head_solid(), "socket_head_bolt", assets=assets),
        origin=Origin(xyz=(PIVOT_X, SOCKET_HEAD_YC, r.pivot_z)),
        material=mats["steel"],
        name="socket_head_bolt", material_class_id="metal.steel_bare",
    )
    collar_root.visual(
        mesh_from_cadquery(_hex_socket_floor_solid(), "hex_socket_recess", assets=assets),
        origin=Origin(xyz=(PIVOT_X, SOCKET_FACE_Y - SOCKET_RECESS_DEPTH + 0.00035, r.pivot_z)),
        material=mats["dark"],
        name="hex_socket_recess", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    hex_key = model.part("hex_key")
    hex_key.visual(
        mesh_from_cadquery(_hex_drive_bit_solid(), "hex_drive_bit", assets=assets),
        material=mats["lever"],
        name="hex_drive_bit", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    hex_key.visual(
        mesh_from_cadquery(_hex_key_hinge_solid(), "hinge_knuckle", assets=assets),
        material=mats["light"],
        name="hinge_knuckle", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    hex_key.visual(
        mesh_from_cadquery(
            _folding_hex_key_arm_solid(r.lever_scale), "folding_hex_arm", assets=assets
        ),
        material=mats["lever"],
        name="folding_hex_arm", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    hex_key.inertial = Inertial.from_geometry(
        Box((0.006, 0.006, HEX_KEY_ARM_LEN * r.lever_scale)),
        mass=0.008,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * HEX_KEY_ARM_LEN * r.lever_scale)),
    )
    model.articulation(
        "hex_key_hinge",
        ArticulationType.REVOLUTE,
        parent=collar_root,
        child=hex_key,
        origin=Origin(xyz=(PIVOT_X, SOCKET_FACE_Y, r.pivot_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=5.0, lower=0.0, upper=HEX_OPEN),
        motion_properties=MotionProperties(damping=0.08, friction=0.03),
        # Grandfathered: the folding-key hinge knuckle is seated/captured in the
        # socket-head mouth (S5), guarded by element-scoped allow_overlap.
    )
    return ["hex_key"]


_ACTUATION_BUILDERS = {
    "cam_over_center_lever": _emit_cam_over_center,
    "fold_flat_lever": _emit_fold_flat_lever,
    "recessed_hex_bolt": _emit_recessed_hex,
}


# ---------------------------------------------------------------------------
# Nut builders (Slot C). All reuse adjuster_nut_spin CONTINUOUS y.
# ---------------------------------------------------------------------------
def _emit_nut_joint(model, r, *, nut_carrier, adjuster_nut, nut_x, nut_elem) -> None:
    model.articulation(
        "adjuster_nut_spin",
        ArticulationType.CONTINUOUS,
        parent=nut_carrier,
        child=adjuster_nut,
        origin=Origin(xyz=(PIVOT_X + nut_x, r.nut_yc, r.pivot_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=12.0),
        motion_properties=MotionProperties(damping=0.05, friction=0.02),
        mating=MatingContract(
            parent_face_geometry="nut_side_thrust_washer",
            parent_face_side="negative_y",
            child_face_geometry=nut_elem,
            child_face_side="positive_y",
            contact_tol=0.0015,
        ),
    )


def _nut_inertial(r) -> Inertial:
    return Inertial.from_geometry(
        Box((max(r.nut_d, 0.014), max(r.nut_d, 0.014), r.nut_len)),
        mass=0.012,
        origin=Origin(),
    )


def _emit_knurled_nut(model, r, mats, *, nut_carrier, nut_x, assets) -> list[str]:
    adjuster_nut = model.part("adjuster_nut")
    adjuster_nut.visual(
        mesh_from_geometry(_knurled_nut_geometry(r.nut_d, r.nut_len), "knurled_nut"),
        origin=Origin(rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["nut"],
        name="knurled_nut", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    adjuster_nut.inertial = _nut_inertial(r)
    _emit_nut_joint(
        model,
        r,
        nut_carrier=nut_carrier,
        adjuster_nut=adjuster_nut,
        nut_x=nut_x,
        nut_elem="knurled_nut",
    )
    return ["adjuster_nut"]


def _emit_winged_thumb_nut(model, r, mats, *, nut_carrier, nut_x, assets) -> list[str]:
    adjuster_nut = model.part("adjuster_nut")
    adjuster_nut.visual(
        mesh_from_cadquery(
            _thumb_nut_hub_solid(r.nut_d, r.nut_len), "thumb_nut_hub", assets=assets
        ),
        origin=Origin(rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["nut"],
        name="thumb_nut_hub", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    for i in range(2):
        adjuster_nut.visual(
            mesh_from_cadquery(_thumb_wing_solid(i, r.nut_d), f"wing_{i}", assets=assets),
            origin=Origin(rpy=(pi / 2.0, 0.0, 0.0)),
            material=mats["nut"],
            name=f"wing_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
        )
    adjuster_nut.inertial = _nut_inertial(r)
    _emit_nut_joint(
        model,
        r,
        nut_carrier=nut_carrier,
        adjuster_nut=adjuster_nut,
        nut_x=nut_x,
        nut_elem="thumb_nut_hub",
    )
    return ["adjuster_nut"]


def _emit_domed_acorn_nut(model, r, mats, *, nut_carrier, nut_x, assets) -> list[str]:
    adjuster_nut = model.part("adjuster_nut")
    adjuster_nut.visual(
        mesh_from_cadquery(
            _acorn_cap_nut_solid(r.nut_d, r.nut_len), "acorn_cap_nut", assets=assets
        ),
        origin=Origin(rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["nut"],
        name="acorn_cap_nut", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_aluminum", "black_anodized", "polished_chrome", "gunmetal"} else "metal.paint_coated"),
    )
    adjuster_nut.inertial = _nut_inertial(r)
    _emit_nut_joint(
        model,
        r,
        nut_carrier=nut_carrier,
        adjuster_nut=adjuster_nut,
        nut_x=nut_x,
        nut_elem="acorn_cap_nut",
    )
    return ["adjuster_nut"]


_NUT_BUILDERS = {
    "knurled_barrel_nut": _emit_knurled_nut,
    "winged_thumb_nut": _emit_winged_thumb_nut,
    "domed_acorn_nut": _emit_domed_acorn_nut,
}

_NUT_ELEM = {
    "knurled_barrel_nut": "knurled_nut",
    "winged_thumb_nut": "thumb_nut_hub",
    "domed_acorn_nut": "acorn_cap_nut",
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_quick_release_clamp(
    config: QuickReleaseClampConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"qrc_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    collar_root, nut_carrier, nut_x = _COLLAR_BUILDERS[r.collar_style](
        model, r, mats, assets=assets
    )
    _ACTUATION_BUILDERS[r.actuation_style](model, r, mats, collar_root=collar_root, assets=assets)
    _NUT_BUILDERS[r.nut_style](model, r, mats, nut_carrier=nut_carrier, nut_x=nut_x, assets=assets)

    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]
    return model


def build_seeded_quick_release_clamp(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_quick_release_clamp(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_quick_release_clamp_tests(
    object_model: ArticulatedObject,
    config: QuickReleaseClampConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    collar_root_name = "cam_arc" if r.is_hinged else "collar"
    nut_carrier_name = "nut_arc" if r.is_hinged else "collar"
    collar_root = object_model.get_part(collar_root_name)
    nut_carrier = object_model.get_part(nut_carrier_name)
    adjuster_nut = object_model.get_part("adjuster_nut")
    nut_elem = _NUT_ELEM[r.nut_style]

    # ---- Captured-pin / coaxial allowances (element-scoped). ----
    # cross_bolt lives on the collar root (collar / cam_arc), coaxial with the nut.
    ctx.allow_overlap(
        collar_root,
        adjuster_nut,
        elem_a="cross_bolt",
        elem_b=nut_elem,
        reason="The cross bolt threads into the adjuster nut bore (thread-engagement proxy).",
    )

    if r.actuation_style == "cam_over_center_lever":
        cam_lever = object_model.get_part("cam_lever")
        ctx.allow_overlap(
            collar_root,
            cam_lever,
            elem_a="cross_bolt",
            elem_b="lever_handle",
            reason="The cross bolt is the pivot axle through the lever hub.",
        )
        ctx.allow_overlap(
            collar_root,
            cam_lever,
            elem_a="cap_side_thrust_washer",
            elem_b="lever_handle",
            reason="The lever hub bears against the cap-side thrust washer at the pivot.",
        )
    elif r.actuation_style == "fold_flat_lever":
        folding_lever = object_model.get_part("folding_lever")
        ctx.allow_overlap(
            collar_root,
            folding_lever,
            elem_a="hinge_pin",
            elem_b="flat_lever",
            reason="The hinge pin is a captured pin through the folding-lever eye.",
        )
        ctx.allow_overlap(
            collar_root,
            folding_lever,
            elem_a="bolt_head",
            elem_b="flat_lever",
            reason="The folded lever eye sits just outboard of the bolt head.",
        )
    else:  # recessed_hex_bolt
        hex_key = object_model.get_part("hex_key")
        ctx.allow_overlap(
            collar_root,
            hex_key,
            elem_a="socket_head_bolt",
            elem_b="hex_drive_bit",
            reason="The stowed hex bit is inserted into the recessed socket drive.",
        )
        ctx.allow_overlap(
            collar_root,
            hex_key,
            elem_a="socket_head_bolt",
            elem_b="hinge_knuckle",
            reason="The folding-key hinge knuckle is seated in the socket-head mouth.",
        )
        ctx.allow_overlap(
            collar_root,
            hex_key,
            elem_a="hex_socket_recess",
            elem_b="hex_drive_bit",
            reason="The hex bit is coaxial inside the recessed socket.",
        )

    if r.is_hinged:
        ctx.allow_overlap(
            collar_root,
            nut_carrier,
            elem_a="barrel_hinge_pin",
            elem_b="nut_hinge_knuckle",
            reason="The barrel-hinge pin runs through the nut-side knuckle (captured pin).",
        )
        ctx.allow_overlap(
            collar_root,
            nut_carrier,
            elem_a="cam_clamp_lug",
            elem_b="nut_clamp_lug",
            reason="The opposed -X clamp lugs are drawn together by the lever bolt.",
        )

    # ---- Baseline gates. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "collar root part present",
        collar_root_name in part_names,
        details=str(sorted(part_names)),
    )

    # Exactly one actuation REVOLUTE with the expected axis.
    act_axis = {
        "cam_over_center_lever": (0.0, 0.0, 1.0),
        "fold_flat_lever": (1.0, 0.0, 0.0),
        "recessed_hex_bolt": (-1.0, 0.0, 0.0),
    }[r.actuation_style]
    act_joint_name = {
        "cam_over_center_lever": "lever_cam_pivot",
        "fold_flat_lever": "lever_hinge",
        "recessed_hex_bolt": "hex_key_hinge",
    }[r.actuation_style]
    aj = object_model.get_articulation(act_joint_name)
    ctx.check(
        "actuation is one REVOLUTE on the expected axis",
        aj.articulation_type == ArticulationType.REVOLUTE and tuple(aj.axis) == act_axis,
        details=f"name={act_joint_name} type={aj.articulation_type} axis={tuple(aj.axis)}",
    )

    spin = object_model.get_articulation("adjuster_nut_spin")
    ctx.check(
        "adjuster nut spins continuously about +Y (coaxial with cross bolt)",
        spin.articulation_type == ArticulationType.CONTINUOUS
        and tuple(spin.axis) == (0.0, 1.0, 0.0)
        and abs(spin.origin.xyz[2] - r.pivot_z) < 1e-9,
        details=f"type={spin.articulation_type} axis={tuple(spin.axis)} origin={spin.origin.xyz}",
    )

    if r.is_hinged:
        bh = object_model.get_articulation("barrel_hinge")
        ctx.check(
            "hinged collar adds a barrel_hinge REVOLUTE about +Z",
            bh.articulation_type == ArticulationType.REVOLUTE and tuple(bh.axis) == (0.0, 0.0, 1.0),
            details=f"type={bh.articulation_type} axis={tuple(bh.axis)}",
        )

    # Collar keeps an open throat / slit (single-piece styles) or two arcs.
    if not r.is_hinged:
        band_aabb = ctx.part_element_world_aabb(collar_root, elem="collar_band")
        if r.collar_style == "omega_split_ring":
            ctx.check(
                "omega collar band leaves an open -X throat",
                band_aabb is not None and band_aabb[0][0] <= -r.bore_r + 1e-4,
                details=f"collar_band aabb={band_aabb}",
            )
        else:
            ctx.check(
                "pinch collar band is a full-circle annulus",
                band_aabb is not None
                and band_aabb[0][0] <= -r.outer_r + 0.001
                and band_aabb[1][0] >= r.outer_r - 0.001,
                details=f"collar_band aabb={band_aabb}",
            )

    # Actuation joint opens (the moving child travels).
    child_name = {
        "cam_over_center_lever": "cam_lever",
        "fold_flat_lever": "folding_lever",
        "recessed_hex_bolt": "hex_key",
    }[r.actuation_style]
    child = object_model.get_part(child_name)
    closed = ctx.part_world_aabb(child)
    with ctx.pose({aj: r.act_open * 0.8}):
        opened = ctx.part_world_aabb(child)
    if closed is not None and opened is not None:
        moved = any(abs(opened[k][a] - closed[k][a]) > 0.010 for k in (0, 1) for a in (0, 1, 2))
        ctx.check(
            "actuation child moves when actuated",
            moved,
            details=f"closed={closed} opened={opened}",
        )

    # slot_choices recorded.
    ctx.check(
        "slot_choices recorded",
        tuple(tuple(t) for t in object_model.meta.get("slot_choices", ()))
        == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "QuickReleaseClampConfig",
    "ResolvedQuickReleaseClampConfig",
    "build_quick_release_clamp",
    "build_seeded_quick_release_clamp",
    "config_from_seed",
    "resolve_config",
    "run_quick_release_clamp_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
