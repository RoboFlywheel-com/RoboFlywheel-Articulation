# SPDX-License-Identifier: Apache-2.0

"""Manual barrel hand-pump procedural template (modular, parallel-children).

A cast-metal vertical barrel pump: a machined barrel is carried by a cast
base fitting + yoke clamp; a piston rod telescopes up out of the knurled top
cap and is topped by a hand grip; pushing the grip down drives the piston into
the barrel (PRIMARY = ``barrel_to_piston`` PRISMATIC, the hero air-stroke). A
foot/wing lever pinned to the yoke clevis rocks about that pin (SECONDARY =
``yoke_to_lever`` REVOLUTE). The base fitting carries a -Y side outlet stub on
which the discharge fitting (hose / gooseneck / barb / quarter-turn tap) is
seated.

Three structural slots all parent to the single root body ``pump_body`` (or its
``piston`` child); there is NO parent-level ×N multiplicity axis:

  handle  -> piston grip on the rod (drives barrel_to_piston PRISMATIC)
              {ball_knob_plunger, handle_tbar, handle_dloop, handle_palmdisc}
  base    -> grounding/wall support on pump_body (FIXED root visuals)
              {cast_hex_foot, base_flange, base_tripod, base_wallbracket}
  outlet  -> discharge fitting on the -Y outlet stub (FIXED root visuals,
              except outlet_tapvalve which adds a tap_handle part +
              tap_to_handle REVOLUTE)
              {loose_rubber_hose, outlet_gooseneck, outlet_barb, outlet_tapvalve}

5-star sources (workbench-only Equipment/Pump2 fork batch in articraft_data):
  parent  rec_..._621823e2          -> core body + ball_knob + cast_hex_foot + hose
  handle  rec_pump_var_handle_tbar / _dloop / _palmdisc
  base    rec_pump_var_base_flange / _tripod / _wallbracket
  outlet  rec_pump_var_outlet_gooseneck / _barb / _tapvalve

Per AUTHORING.md §A Rule 3 the CadQuery / lathe / spline mesh
primitives are preserved verbatim (never downgraded to Box/Cylinder); only
literal dimensions, the knurl flute count, and the local copy-counts
(``leg_count`` / ``bolt_count``) are parameterised.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from math import cos, pi, sin
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Cylinder,
    LatheGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot enums
# --------------------------------------------------------------------------- #
HandleStyle = Literal[
    "ball_knob_plunger", "handle_tbar", "handle_dloop", "handle_palmdisc"
]
BaseStyle = Literal[
    "cast_hex_foot", "base_flange", "base_tripod", "base_wallbracket"
]
OutletStyle = Literal[
    "loose_rubber_hose", "outlet_gooseneck", "outlet_barb", "outlet_tapvalve"
]
PaletteStyle = Literal[
    "cast_iron", "galvanized", "red_oxide", "forest_green", "brass_bronze", "industrial_blue"
]

HANDLE_STYLES: tuple[HandleStyle, ...] = (
    "ball_knob_plunger",
    "handle_tbar",
    "handle_dloop",
    "handle_palmdisc",
)
BASE_STYLES: tuple[BaseStyle, ...] = (
    "cast_hex_foot",
    "base_flange",
    "base_tripod",
    "base_wallbracket",
)
OUTLET_STYLES: tuple[OutletStyle, ...] = (
    "loose_rubber_hose",
    "outlet_gooseneck",
    "outlet_barb",
    "outlet_tapvalve",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "cast_iron",
    "galvanized",
    "red_oxide",
    "forest_green",
    "brass_bronze",
    "industrial_blue",
)

# Material roles used by every visual; each palette style provides all keys.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "cast_iron": {
        "barrel": (0.46, 0.49, 0.54, 1.0),
        "cap": (0.34, 0.36, 0.40, 1.0),
        "cast": (0.58, 0.59, 0.60, 1.0),
        "black": (0.08, 0.08, 0.09, 1.0),
        "rod": (0.40, 0.42, 0.46, 1.0),
        "white": (0.90, 0.91, 0.92, 1.0),
        "hose": (0.06, 0.06, 0.07, 1.0),
        "spout": (0.55, 0.56, 0.58, 1.0),
        "brass": (0.74, 0.56, 0.30, 1.0),
        "fastener": (0.03, 0.03, 0.035, 1.0),
    },
    "galvanized": {
        "barrel": (0.72, 0.74, 0.77, 1.0),
        "cap": (0.62, 0.64, 0.67, 1.0),
        "cast": (0.66, 0.68, 0.70, 1.0),
        "black": (0.10, 0.10, 0.11, 1.0),
        "rod": (0.78, 0.80, 0.83, 1.0),
        "white": (0.92, 0.93, 0.94, 1.0),
        "hose": (0.10, 0.10, 0.11, 1.0),
        "spout": (0.68, 0.70, 0.72, 1.0),
        "brass": (0.80, 0.62, 0.34, 1.0),
        "fastener": (0.20, 0.21, 0.22, 1.0),
    },
    "red_oxide": {
        "barrel": (0.62, 0.12, 0.10, 1.0),
        "cap": (0.36, 0.10, 0.09, 1.0),
        "cast": (0.55, 0.13, 0.11, 1.0),
        "black": (0.07, 0.07, 0.08, 1.0),
        "rod": (0.45, 0.46, 0.50, 1.0),
        "white": (0.92, 0.90, 0.88, 1.0),
        "hose": (0.06, 0.06, 0.07, 1.0),
        "spout": (0.50, 0.13, 0.11, 1.0),
        "brass": (0.76, 0.58, 0.32, 1.0),
        "fastener": (0.10, 0.04, 0.04, 1.0),
    },
    "forest_green": {
        "barrel": (0.12, 0.34, 0.22, 1.0),
        "cap": (0.10, 0.26, 0.18, 1.0),
        "cast": (0.13, 0.32, 0.21, 1.0),
        "black": (0.06, 0.08, 0.07, 1.0),
        "rod": (0.55, 0.58, 0.56, 1.0),
        "white": (0.90, 0.92, 0.90, 1.0),
        "hose": (0.05, 0.06, 0.05, 1.0),
        "spout": (0.11, 0.28, 0.19, 1.0),
        "brass": (0.74, 0.57, 0.31, 1.0),
        "fastener": (0.05, 0.10, 0.07, 1.0),
    },
    "brass_bronze": {
        "barrel": (0.72, 0.55, 0.27, 1.0),
        "cap": (0.60, 0.45, 0.22, 1.0),
        "cast": (0.66, 0.50, 0.25, 1.0),
        "black": (0.10, 0.09, 0.07, 1.0),
        "rod": (0.78, 0.62, 0.34, 1.0),
        "white": (0.90, 0.88, 0.82, 1.0),
        "hose": (0.10, 0.08, 0.06, 1.0),
        "spout": (0.74, 0.57, 0.30, 1.0),
        "brass": (0.82, 0.66, 0.36, 1.0),
        "fastener": (0.30, 0.22, 0.10, 1.0),
    },
    "industrial_blue": {
        "barrel": (0.16, 0.30, 0.50, 1.0),
        "cap": (0.13, 0.24, 0.40, 1.0),
        "cast": (0.17, 0.31, 0.48, 1.0),
        "black": (0.06, 0.07, 0.09, 1.0),
        "rod": (0.55, 0.58, 0.62, 1.0),
        "white": (0.90, 0.92, 0.94, 1.0),
        "hose": (0.05, 0.05, 0.07, 1.0),
        "spout": (0.15, 0.28, 0.45, 1.0),
        "brass": (0.76, 0.58, 0.32, 1.0),
        "fastener": (0.08, 0.12, 0.20, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Base dimensions (meters) — from parent model.py:L36-L52. The base fitting,
# yoke, lever and outlet stub are independent of the barrel-height / stroke
# scales; only the barrel, cap and piston follow them.
# --------------------------------------------------------------------------- #
TOL = 0.0006
ATOL = 0.2

BARREL_R = 0.042
BARREL_BORE_R = 0.0345
BARREL_BOTTOM_Z = 0.072
_BASE_BARREL_LEN = 0.190  # parent BARREL_TOP_Z - BARREL_BOTTOM_Z (0.262 - 0.072)
_CAP_RISE = 0.017  # parent CAP_TOP_Z - BARREL_TOP_Z (0.279 - 0.262)

ROD_R = 0.0085
KNOB_R = 0.030
CUP_LEN = 0.018
_CUP_BELOW_TOP = 0.032  # cup center sits this far below the barrel top
_BASE_STROKE = 0.065
_HANDLE_GAP = 0.014  # grip-bottom clearance above the cap at full stroke

YOKE_BASE_Z = 0.022
YOKE_PIN_Z = 0.044
CLEVIS_X = -0.052

# Outlet stub center (parent base fitting), -Y side.
OUTLET_Y = -0.038
OUTLET_Z = 0.030

# Handle grip dimensions.
T_BAR_R = 0.012
T_BAR_LEN = 0.118
LOOP_TUBE_R = 0.0065
LOOP_WIDTH = 0.078
_LOOP_ARCH = 0.060  # parent LOOP_TOP_Z - LOOP_BOTTOM_Z
DISC_R = 0.044
_DISC_H = 0.030  # parent DISC_TOP_Z - DISC_BOTTOM_Z

# Base copy-loop ranges.
FLANGE_R = 0.070
FLANGE_THICKNESS = 0.014
FLANGE_BOLT_CIRCLE_R = 0.052
FLANGE_BOLT_HEAD_R = 0.0065

# Wallbracket dimensions.
BACKPLATE_W = 0.135
BACKPLATE_T = 0.012
BACKPLATE_H = 0.305
BACKPLATE_Y = 0.060
BACKPLATE_FRONT_Y = BACKPLATE_Y - BACKPLATE_T / 2.0
CLAMP_Z = 0.152
CLAMP_H = 0.030
CLAMP_OUTER_R = BARREL_R + 0.009
CLAMP_INNER_R = BARREL_R + 0.0005

# Tap / quarter-turn valve.
TAP_Y = -0.086
TAP_AXIS_Z = 0.030
TAP_BOSS_TOP_Z = 0.062

LEG_COUNT_RANGE = (3, 6)
BOLT_COUNT_RANGE = (3, 8)


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class HandPumpConfig:
    handle_style: HandleStyle | None = None
    base_style: BaseStyle | None = None
    outlet_style: OutletStyle | None = None
    palette_style: PaletteStyle | None = None
    stroke_scale: float = 1.0
    barrel_height_scale: float = 1.0
    leg_count: int | None = None
    bolt_count: int | None = None
    n_flutes: int = 18
    name: str = "hand_pump"


@dataclass(frozen=True)
class ResolvedHandPumpConfig:
    handle_style: HandleStyle
    base_style: BaseStyle
    outlet_style: OutletStyle
    palette_style: PaletteStyle
    leg_count: int
    bolt_count: int
    n_flutes: int
    # Derived absolute heights.
    barrel_bottom_z: float
    barrel_top_z: float
    cap_top_z: float
    stroke: float
    cup_center_z: float
    handle_low_z: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> HandPumpConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    return HandPumpConfig(
        handle_style=rng.choice(HANDLE_STYLES),
        base_style=rng.choice(BASE_STYLES),
        outlet_style=rng.choice(OUTLET_STYLES),
        palette_style=rng.choice(PALETTE_STYLES),
        stroke_scale=round(rng.uniform(0.85, 1.15), 4),
        barrel_height_scale=round(rng.uniform(0.92, 1.12), 4),
        leg_count=rng.randint(*LEG_COUNT_RANGE),
        bolt_count=rng.randint(*BOLT_COUNT_RANGE),
        name=f"seeded_hand_pump_{seed}",
    )


def resolve_config(config: HandPumpConfig | None = None) -> ResolvedHandPumpConfig:
    cfg = config or HandPumpConfig()

    handle_style = _pick(cfg.handle_style, HANDLE_STYLES)
    base_style = _pick(cfg.base_style, BASE_STYLES)
    outlet_style = _pick(cfg.outlet_style, OUTLET_STYLES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # --- Compatibility matrix (spec §9). The loose floor-resting hose conflicts
    # with the wall-mounted bracket pose (the "free end on the floor" wraps
    # behind the back-plate); degrade to a rigid barbed nipple. The tap valve's
    # trailing hose is suppressed for the same pose (handled in the emitter).
    if base_style == "base_wallbracket" and outlet_style == "loose_rubber_hose":
        outlet_style = "outlet_barb"

    leg_count = int(cfg.leg_count) if cfg.leg_count is not None else LEG_COUNT_RANGE[0]
    leg_count = int(_clamp(leg_count, *LEG_COUNT_RANGE))
    bolt_count = int(cfg.bolt_count) if cfg.bolt_count is not None else 4
    bolt_count = int(_clamp(bolt_count, *BOLT_COUNT_RANGE))

    n_flutes = int(_clamp(int(cfg.n_flutes), 8, 40))

    bh = _clamp(float(cfg.barrel_height_scale), 0.92, 1.12)
    barrel_top_z = BARREL_BOTTOM_Z + _BASE_BARREL_LEN * bh
    cap_top_z = barrel_top_z + _CAP_RISE
    barrel_len = barrel_top_z - BARREL_BOTTOM_Z

    stroke = _BASE_STROKE * _clamp(float(cfg.stroke_scale), 0.85, 1.15)
    # Retained-insertion inequality: the piston cup must not exit the bore at
    # full stroke (cup body length + slack stays inside the barrel).
    stroke = _clamp(stroke, 0.040, barrel_len - CUP_LEN - 0.03)

    cup_center_z = barrel_top_z - _CUP_BELOW_TOP
    # Knob-clearance inequality: grip bottom clears the cap by _HANDLE_GAP at
    # full stroke (rest clearance = stroke + _HANDLE_GAP).
    handle_low_z = cap_top_z + stroke + _HANDLE_GAP

    return ResolvedHandPumpConfig(
        handle_style=handle_style,
        base_style=base_style,
        outlet_style=outlet_style,
        palette_style=palette_style,
        leg_count=leg_count,
        bolt_count=bolt_count,
        n_flutes=n_flutes,
        barrel_bottom_z=BARREL_BOTTOM_Z,
        barrel_top_z=barrel_top_z,
        cap_top_z=cap_top_z,
        stroke=stroke,
        cup_center_z=cup_center_z,
        handle_low_z=handle_low_z,
        name=cfg.name or "hand_pump",
    )


def slot_choices_for_config(
    config: HandPumpConfig | ResolvedHandPumpConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedHandPumpConfig) else resolve_config(config)
    return (
        ("handle", r.handle_style),
        ("base", r.base_style),
        ("outlet", r.outlet_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Shared core CadQuery shapes (preserve source Mesh primitives — Rule 3).
# --------------------------------------------------------------------------- #
def _barrel_shape(r: ResolvedHandPumpConfig) -> cq.Workplane:
    """Hollow machined barrel: bored open-top tube with a rolled lower rim."""
    h = r.barrel_top_z - r.barrel_bottom_z
    barrel = (
        cq.Workplane("XY")
        .circle(BARREL_R)
        .workplane(offset=h)
        .circle(BARREL_R)
        .loft(combine=True)
        .translate((0.0, 0.0, r.barrel_bottom_z))
    )
    bore = (
        cq.Workplane("XY")
        .circle(BARREL_BORE_R)
        .extrude(h + 0.020)
        .translate((0.0, 0.0, r.barrel_bottom_z + 0.010))
    )
    barrel = barrel.cut(bore)
    rim = (
        cq.Workplane("XY")
        .circle(BARREL_R + 0.0035)
        .extrude(0.012)
        .translate((0.0, 0.0, r.barrel_bottom_z))
    )
    return barrel.union(rim)


def _cap_shape(r: ResolvedHandPumpConfig) -> cq.Workplane:
    """Knurled top cap ring with a rod gland boss."""
    top = r.barrel_top_z
    cap_top = r.cap_top_z
    cap = (
        cq.Workplane("XY")
        .circle(BARREL_R + 0.004)
        .extrude(cap_top - top)
        .translate((0.0, 0.0, top))
    )
    cap = cap.edges(">Z").chamfer(0.0015)
    flute_h = cap_top - top
    for i in range(r.n_flutes):
        a = 2.0 * pi * i / r.n_flutes
        groove = (
            cq.Workplane("XY")
            .circle(0.0012)
            .extrude(flute_h + 0.002)
            .translate((BARREL_R + 0.0045, 0.0, top - 0.001))
            .rotate((0, 0, 0), (0, 0, 1), a * 180.0 / pi)
        )
        cap = cap.cut(groove)
    boss = (
        cq.Workplane("XY")
        .circle(0.018)
        .extrude(0.010)
        .translate((0.0, 0.0, cap_top))
    )
    gland_bore = (
        cq.Workplane("XY")
        .circle(ROD_R - 0.0006)
        .extrude(0.040)
        .translate((0.0, 0.0, top - 0.001))
    )
    return cap.union(boss).cut(gland_bore)


def _guide_collar_shape() -> cq.Workplane:
    """Lower split guide ring clamped around the barrel, just above the yoke."""
    collar = (
        cq.Workplane("XY")
        .circle(BARREL_R + 0.006)
        .circle(BARREL_R + 0.0005)
        .extrude(0.014)
        .translate((0.0, 0.0, BARREL_BOTTOM_Z - 0.004))
    )
    for sx in (1.0, -1.0):
        ear = (
            cq.Workplane("XY")
            .box(0.010, 0.016, 0.014, centered=(True, True, False))
            .translate((sx * (BARREL_R + 0.008), 0.0, BARREL_BOTTOM_Z - 0.004))
        )
        collar = collar.union(ear)
    return collar


def _yoke_shape() -> cq.Workplane:
    """Clamp collar around the base neck plus a clevis carrying the lever pin."""
    # Collar inner radius is slightly under the base neck (0.026) so it grips
    # the casting with a real overlap rather than floating around it.
    collar = (
        cq.Workplane("XY")
        .circle(0.036)
        .circle(0.0255)
        .extrude(0.040)
        .translate((0.0, 0.0, YOKE_BASE_Z))
    )
    yoke = collar
    cheek_bot = YOKE_PIN_Z - 0.018
    for sy in (1.0, -1.0):
        cheek = (
            cq.Workplane("XY")
            .box(0.024, 0.011, 0.030, centered=(True, True, False))
            .translate((CLEVIS_X, sy * 0.024, cheek_bot))
        )
        cheek = cheek.edges("|X").fillet(0.005)
        yoke = yoke.union(cheek)
    # Spine web tying the clevis cheeks back to the collar. Authored tall enough
    # to overlap the cheeks volumetrically (not just a coplanar face) so the
    # boolean union fuses into a single connected solid.
    web = (
        cq.Workplane("XY")
        .box(abs(CLEVIS_X) + 0.030, 0.044, 0.018, centered=(True, True, False))
        .translate((CLEVIS_X / 2.0, 0.0, YOKE_PIN_Z - 0.030))
    )
    yoke = yoke.union(web)
    pin = (
        cq.Workplane("XY")
        .circle(0.005)
        .extrude(0.034, both=True)
        .rotate((0, 0, 0), (1, 0, 0), 90.0)
        .translate((CLEVIS_X, 0.0, YOKE_PIN_Z))
    )
    return yoke.union(pin)


def _lever_shape() -> cq.Workplane:
    """Foot/wing lever: grip bar with a hub that wraps the yoke pin (axis Y)."""
    hub = (
        cq.Workplane("XY")
        .circle(0.012)
        .extrude(0.013, both=True)
        .rotate((0, 0, 0), (1, 0, 0), 90.0)
    )
    arm = (
        cq.Workplane("XY")
        .circle(0.012)
        .extrude(0.130)
        .rotate((0, 0, 0), (0, 1, 0), -90.0)
    )
    lever = hub.union(arm)
    pin_bore = (
        cq.Workplane("XY")
        .circle(0.0044)
        .extrude(0.040, both=True)
        .rotate((0, 0, 0), (1, 0, 0), 90.0)
    )
    return lever.cut(pin_bore)


def _lever_endcap_shape() -> cq.Workplane:
    """White plastic end cap on the free end of the lever grip."""
    cap = (
        cq.Workplane("XY")
        .circle(0.0135)
        .extrude(0.014)
        .edges(">Z")
        .fillet(0.003)
    )
    return cap.rotate((0, 0, 0), (0, 1, 0), -90.0).translate((-0.122, 0.0, 0.0))


def _piston_head_shape() -> cq.Workplane:
    """Piston cup at the bottom of the rod, hidden inside the barrel bore."""
    head = (
        cq.Workplane("XY")
        .circle(BARREL_BORE_R - 0.0015)
        .extrude(CUP_LEN)
    )
    return head.edges(">Z").fillet(0.002)


# --------------------------------------------------------------------------- #
# Base-fitting CadQuery shapes (one per base module).
# --------------------------------------------------------------------------- #
def _neck_and_outlet(body: cq.Workplane) -> cq.Workplane:
    neck = (
        cq.Workplane("XY")
        .circle(0.026)
        .extrude(BARREL_BOTTOM_Z + 0.012 - YOKE_BASE_Z)
        .translate((0.0, 0.0, YOKE_BASE_Z))
    )
    body = body.union(neck)
    outlet = (
        cq.Workplane("XY")
        .circle(0.0085)
        .extrude(0.030, both=True)
        .rotate((0, 0, 0), (1, 0, 0), 90.0)
        .translate((0.0, OUTLET_Y, OUTLET_Z))
    )
    return body.union(outlet)


def _base_fitting_hex() -> cq.Workplane:
    """Parent cast fitting: tapered body + hex foot flange + neck + outlet."""
    body = (
        cq.Workplane("XY")
        .circle(0.030)
        .workplane(offset=YOKE_BASE_Z)
        .circle(0.034)
        .loft(combine=True)
    )
    foot = cq.Workplane("XY").polygon(6, 0.082).extrude(0.012)
    foot = foot.edges("|Z").fillet(0.003)
    body = body.union(foot)
    return _neck_and_outlet(body)


def _base_fitting_flange() -> cq.Workplane:
    """Round bolt-flange pedestal + raised plinth + neck + outlet."""
    body = (
        cq.Workplane("XY")
        .circle(0.030)
        .workplane(offset=YOKE_BASE_Z - FLANGE_THICKNESS)
        .circle(0.034)
        .loft(combine=True)
        .translate((0.0, 0.0, FLANGE_THICKNESS))
    )
    flange = cq.Workplane("XY").circle(FLANGE_R).extrude(FLANGE_THICKNESS)
    for i in range(4):
        a = 2.0 * pi * i / 4
        hole = (
            cq.Workplane("XY")
            .circle(0.0038)
            .extrude(FLANGE_THICKNESS + 0.006)
            .translate((FLANGE_BOLT_CIRCLE_R * cos(a), FLANGE_BOLT_CIRCLE_R * sin(a), -0.003))
        )
        flange = flange.cut(hole)
    plinth = (
        cq.Workplane("XY")
        .circle(0.039)
        .extrude(0.010)
        .translate((0.0, 0.0, FLANGE_THICKNESS - 0.0005))
    )
    body = body.union(flange).union(plinth)
    return _neck_and_outlet(body)


def _base_fitting_plain() -> cq.Workplane:
    """Cast fitting with no foot flange (tripod / wallbracket)."""
    body = (
        cq.Workplane("XY")
        .circle(0.030)
        .workplane(offset=YOKE_BASE_Z)
        .circle(0.034)
        .loft(combine=True)
    )
    return _neck_and_outlet(body)


def _flange_bolt_shape() -> cq.Workplane:
    """Low hex bolt head seated on the round pedestal flange."""
    return cq.Workplane("XY").polygon(6, FLANGE_BOLT_HEAD_R * 2.0).extrude(0.0042)


def _tripod_leg_shape(angle: float) -> cq.Workplane:
    """One splayed cast leg, authored along +X then rotated about the pump."""
    strut = (
        cq.Workplane("XY")
        .circle(0.010)
        .workplane(offset=0.092)
        .circle(0.014)
        .loft(combine=True)
        .rotate((0, 0, 0), (0, 1, 0), 94.5)
        .translate((0.024, 0.0, 0.021))
    )
    root_boss = (
        cq.Workplane("XY")
        .circle(0.020)
        .extrude(0.014)
        .translate((0.026, 0.0, 0.004))
    )
    root_boss = root_boss.edges(">Z").fillet(0.002)
    foot_pad = (
        cq.Workplane("XY")
        .circle(0.023)
        .extrude(0.008)
        .translate((0.118, 0.0, 0.0))
    )
    foot_pad = foot_pad.edges(">Z").fillet(0.0025)
    leg = root_boss.union(strut).union(foot_pad)
    return leg.rotate((0, 0, 0), (0, 0, 1), angle * 180.0 / pi)


def _y_axis_cylinder(radius: float, length: float, center: tuple[float, float, float]) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .circle(radius)
        .extrude(length, both=True)
        .rotate((0, 0, 0), (1, 0, 0), 90.0)
        .translate(center)
    )


def _back_plate_shape() -> cq.Workplane:
    """Flat wall/bench back-plate replacing the broad lower foot flange."""
    plate = (
        cq.Workplane("XY")
        .box(BACKPLATE_W, BACKPLATE_T, BACKPLATE_H, centered=(True, True, False))
        .translate((0.0, BACKPLATE_Y, 0.0))
    )
    plate = plate.edges("|Y").chamfer(0.003)
    for sx in (-1.0, 1.0):
        for z in (0.036, 0.270):
            plate = plate.cut(
                _y_axis_cylinder(0.0048, BACKPLATE_T + 0.006, (sx * 0.045, BACKPLATE_Y, z))
            )
    return plate


def _saddle_clamp_band_shape() -> cq.Workplane:
    """Raised saddle clamp band around the barrel, bridged into the back-plate."""
    z0 = CLAMP_Z - CLAMP_H / 2.0
    band = (
        cq.Workplane("XY")
        .circle(CLAMP_OUTER_R)
        .circle(CLAMP_INNER_R)
        .extrude(CLAMP_H)
        .translate((0.0, 0.0, z0))
    )
    band = band.edges(">Z").chamfer(0.0015).edges("<Z").chamfer(0.0015)
    rear_web = (
        cq.Workplane("XY")
        .box(0.086, 0.017, CLAMP_H, centered=(True, True, False))
        .translate((0.0, BACKPLATE_FRONT_Y - 0.004, z0))
    )
    band = band.union(rear_web)
    for sx in (-1.0, 1.0):
        ear = (
            cq.Workplane("XY")
            .box(0.020, 0.014, CLAMP_H, centered=(True, True, False))
            .translate((sx * 0.014, -CLAMP_OUTER_R - 0.003, z0))
        )
        ear = ear.edges("|Z").fillet(0.002)
        band = band.union(ear)
    return band


def _fastener_head_shape(radius: float = 0.006, thickness: float = 0.003) -> cq.Workplane:
    """Low domed screw/bolt head with its shank axis along Y."""
    head = cq.Workplane("XY").circle(radius).extrude(thickness, both=True)
    head = head.edges(">Z").fillet(min(0.0012, thickness * 0.40))
    return head.rotate((0, 0, 0), (1, 0, 0), 90.0)


# --------------------------------------------------------------------------- #
# Handle CadQuery / lathe shapes (one per handle module).
# --------------------------------------------------------------------------- #
def _t_bar_grip_shape(center_z: float) -> cq.Workplane:
    """Horizontal T-bar crossgrip with a downward socket on the piston rod."""
    crossbar = (
        cq.Workplane("XY")
        .circle(T_BAR_R)
        .extrude(T_BAR_LEN, both=True)
        .rotate((0, 0, 0), (0, 1, 0), 90.0)
        .translate((0.0, 0.0, center_z))
    )
    for sx in (-1.0, 1.0):
        end_collar = (
            cq.Workplane("XY")
            .circle(T_BAR_R * 1.08)
            .extrude(0.010, both=True)
            .rotate((0, 0, 0), (0, 1, 0), 90.0)
            .translate((sx * T_BAR_LEN / 2.0, 0.0, center_z))
        )
        crossbar = crossbar.union(end_collar)
    socket_bottom = center_z - T_BAR_R - 0.018
    socket = (
        cq.Workplane("XY")
        .circle(ROD_R + 0.004)
        .extrude(center_z - socket_bottom)
        .translate((0.0, 0.0, socket_bottom))
    )
    socket = socket.edges(">Z").fillet(0.0015)
    return crossbar.union(socket)


def _pull_loop_geometry(loop_bottom_z: float):
    """Closed D-shaped pull loop from one continuous bent round tube (XZ plane)."""
    loop_top_z = loop_bottom_z + _LOOP_ARCH
    half_center_width = LOOP_WIDTH * 0.5 - LOOP_TUBE_R
    arch_h = loop_top_z - loop_bottom_z
    pts: list[tuple[float, float, float]] = []
    for x in (
        half_center_width,
        half_center_width * 0.45,
        0.0,
        -half_center_width * 0.45,
        -half_center_width,
    ):
        pts.append((x, 0.0, loop_bottom_z))
    for t in (0.18, 0.42, 0.68):
        pts.append((-half_center_width, 0.0, loop_bottom_z + arch_h * t))
    for i in range(1, 8):
        theta = pi - (pi * i / 8.0)
        x = half_center_width * cos(theta)
        z = loop_bottom_z + arch_h * (0.66 + 0.34 * sin(theta))
        pts.append((x, 0.0, z))
    for t in (0.68, 0.42, 0.18):
        pts.append((half_center_width, 0.0, loop_bottom_z + arch_h * t))
    return tube_from_spline_points(
        pts,
        radius=LOOP_TUBE_R,
        samples_per_segment=14,
        closed_spline=True,
        radial_segments=22,
        cap_ends=False,
        up_hint=(0.0, 1.0, 0.0),
    )


def _push_disc_geometry(disc_bottom_z: float) -> LatheGeometry:
    """Lathe-turned mushroom / palm push-disc for the top of the plunger rod."""
    disc_top_z = disc_bottom_z + _DISC_H
    mid_z = (disc_bottom_z + disc_top_z) / 2.0
    profile = [
        (0.0, disc_bottom_z),
        (0.0135, disc_bottom_z),
        (0.0180, disc_bottom_z + 0.004),
        (0.0390, disc_bottom_z + 0.007),
        (DISC_R, mid_z - 0.001),
        (0.0415, disc_top_z - 0.006),
        (0.0300, disc_top_z),
        (0.0240, disc_top_z - 0.0012),
        (0.0060, disc_top_z - 0.0028),
        (0.0, disc_top_z - 0.0024),
    ]
    return LatheGeometry(profile, segments=72, closed=True)


def _tap_body_shape() -> cq.Workplane:
    """Small inline quarter-turn valve body added to the base outlet."""
    inline = _y_axis_cylinder(0.0105, 0.055, (0.0, TAP_Y, TAP_AXIS_Z))
    inlet_collar = _y_axis_cylinder(0.013, 0.014, (0.0, TAP_Y + 0.021, TAP_AXIS_Z))
    outlet_nipple = _y_axis_cylinder(0.008, 0.020, (0.0, TAP_Y - 0.035, TAP_AXIS_Z))
    chest = (
        cq.Workplane("XY")
        .circle(0.014)
        .extrude(0.025)
        .translate((0.0, TAP_Y, TAP_AXIS_Z - 0.004))
    )
    packing_nut = (
        cq.Workplane("XY")
        .polygon(6, 0.0155)
        .extrude(0.009)
        .translate((0.0, TAP_Y, TAP_BOSS_TOP_Z - 0.017))
    )
    spindle_boss = (
        cq.Workplane("XY")
        .circle(0.007)
        .extrude(0.008)
        .translate((0.0, TAP_Y, TAP_BOSS_TOP_Z - 0.008))
    )
    return inline.union(inlet_collar).union(outlet_nipple).union(chest).union(packing_nut).union(spindle_boss)


def _tap_handle_shape() -> cq.Workplane:
    """Quarter-turn T handle authored around the valve spindle axis (origin at
    the joint center on the boss top; stem descends into the boss)."""
    stem = cq.Workplane("XY").circle(0.0042).extrude(0.020).translate((0.0, 0.0, -0.010))
    cap = cq.Workplane("XY").circle(0.011).extrude(0.005).translate((0.0, 0.0, 0.000))
    crossbar = (
        cq.Workplane("XY")
        .circle(0.0045)
        .extrude(0.050, both=True)
        .rotate((0, 0, 0), (0, 1, 0), 90.0)
        .translate((0.0, 0.0, 0.014))
    )
    for sx in (-1.0, 1.0):
        end_knob = cq.Workplane("XY").sphere(0.006).translate((sx * 0.025, 0.0, 0.014))
        crossbar = crossbar.union(end_knob)
    return stem.union(cap).union(crossbar)


def _spout_socket_shape() -> cq.Workplane:
    """Short cast socket slipped over the existing base outlet stub."""
    return (
        cq.Workplane("XY")
        .circle(0.0115)
        .circle(0.0062)
        .extrude(0.028, both=True)
        .rotate((0, 0, 0), (1, 0, 0), 90.0)
        .translate((0.0, -0.061, OUTLET_Z))
    )


def _downturned_nozzle_shape() -> cq.Workplane:
    """Open hollow vertical nozzle and small cast lips at the spout outlet."""
    nozzle_x, nozzle_y = 0.096, 0.016
    nozzle_bottom_z, nozzle_top_z = 0.022, 0.066
    h = nozzle_top_z - nozzle_bottom_z
    body = (
        cq.Workplane("XY")
        .circle(0.0090)
        .extrude(h)
        .translate((nozzle_x, nozzle_y, nozzle_bottom_z))
    )
    lower_lip = (
        cq.Workplane("XY")
        .circle(0.0115)
        .extrude(0.006)
        .translate((nozzle_x, nozzle_y, nozzle_bottom_z))
    )
    upper_collar = (
        cq.Workplane("XY")
        .circle(0.0105)
        .extrude(0.008)
        .translate((nozzle_x, nozzle_y, nozzle_top_z - 0.008))
    )
    bore = (
        cq.Workplane("XY")
        .circle(0.0052)
        .extrude(h + 0.012)
        .translate((nozzle_x, nozzle_y, nozzle_bottom_z - 0.006))
    )
    return body.union(lower_lip).union(upper_collar).cut(bore)


def _barbed_nipple_shape() -> cq.Workplane:
    """Short hollow barbed hose nipple seated on the -Y outlet stub."""

    def cyl_y(radius: float, length: float, start_y: float) -> cq.Workplane:
        return (
            cq.Workplane("XY")
            .circle(radius)
            .extrude(length)
            .rotate((0, 0, 0), (1, 0, 0), 90.0)
            .translate((0.0, start_y, OUTLET_Z))
        )

    def cone_y(r0: float, r1: float, length: float, start_y: float) -> cq.Workplane:
        return (
            cq.Workplane("XY")
            .circle(r0)
            .workplane(offset=length)
            .circle(r1)
            .loft(combine=True)
            .rotate((0, 0, 0), (1, 0, 0), 90.0)
            .translate((0.0, start_y, OUTLET_Z))
        )

    nipple = cyl_y(0.0108, 0.010, -0.052)
    nipple = nipple.union(cyl_y(0.0062, 0.044, -0.058))
    for i in range(3):
        start_y = -0.060 - i * 0.012
        nipple = nipple.union(cyl_y(0.0092, 0.0025, start_y))
        nipple = nipple.union(cone_y(0.0092, 0.0064, 0.0075, start_y - 0.0025))
    nipple = nipple.union(cone_y(0.0068, 0.0054, 0.006, -0.096))
    bore = cyl_y(0.0034, 0.060, -0.049)
    return nipple.cut(bore)


# --------------------------------------------------------------------------- #
# Core body + module emitters
# --------------------------------------------------------------------------- #
def _mesh_cq(shape: cq.Workplane, name: str, assets):
    return mesh_from_cadquery(
        shape, name, assets=assets, tolerance=TOL, angular_tolerance=ATOL
    )


def _emit_core_body(body, r: ResolvedHandPumpConfig, mats, assets) -> None:
    """Always-present barrel + guide collar + cap + yoke on the root part."""
    body.visual(_mesh_cq(_yoke_shape(), "yoke", assets), material=mats["cast"], name="yoke", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"))
    body.visual(_mesh_cq(_barrel_shape(r), "barrel", assets), material=mats["barrel"], name="barrel", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"))
    body.visual(
        _mesh_cq(_guide_collar_shape(), "guide_collar", assets),
        material=mats["cap"],
        name="guide_collar", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"),
    )
    body.visual(_mesh_cq(_cap_shape(r), "cap", assets), material=mats["cap"], name="cap", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"))


# ---- base slot ----
def _emit_base_hex(model, body, r, mats, assets) -> None:
    body.visual(
        _mesh_cq(_base_fitting_hex(), "base_fitting", assets),
        material=mats["cast"],
        name="base_fitting", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"),
    )


def _emit_base_flange(model, body, r, mats, assets) -> None:
    body.visual(
        _mesh_cq(_base_fitting_flange(), "base_fitting", assets),
        material=mats["cast"],
        name="base_fitting", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"),
    )
    bolt_mesh = _mesh_cq(_flange_bolt_shape(), "flange_bolt", assets)
    for i in range(r.bolt_count):
        a = 2.0 * pi * i / r.bolt_count
        body.visual(
            bolt_mesh,
            origin=Origin(
                xyz=(
                    FLANGE_BOLT_CIRCLE_R * cos(a),
                    FLANGE_BOLT_CIRCLE_R * sin(a),
                    FLANGE_THICKNESS - 0.0007,
                ),
                rpy=(0.0, 0.0, a),
            ),
            material=mats["cap"],
            name=f"flange_bolt_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"),
        )


def _emit_base_tripod(model, body, r, mats, assets) -> None:
    body.visual(
        _mesh_cq(_base_fitting_plain(), "base_fitting", assets),
        material=mats["cast"],
        name="base_fitting", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"),
    )
    for i in range(r.leg_count):
        angle = 2.0 * pi * i / r.leg_count
        body.visual(
            _mesh_cq(_tripod_leg_shape(angle), f"leg_{i}", assets),
            material=mats["cast"],
            name=f"leg_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"),
        )


def _emit_base_wallbracket(model, body, r, mats, assets) -> None:
    body.visual(
        _mesh_cq(_base_fitting_plain(), "base_fitting", assets),
        material=mats["cast"],
        name="base_fitting", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"),
    )
    body.visual(
        _mesh_cq(_back_plate_shape(), "back_plate", assets),
        material=mats["cast"],
        name="back_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"),
    )
    body.visual(
        _mesh_cq(_saddle_clamp_band_shape(), "saddle_clamp_band", assets),
        material=mats["cap"],
        name="saddle_clamp_band", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"),
    )
    fastener_positions = [
        (-0.045, BACKPLATE_FRONT_Y - 0.0013, 0.036),
        (0.045, BACKPLATE_FRONT_Y - 0.0013, 0.036),
        (-0.045, BACKPLATE_FRONT_Y - 0.0013, 0.270),
        (0.045, BACKPLATE_FRONT_Y - 0.0013, 0.270),
        (-0.014, -CLAMP_OUTER_R - 0.0113, CLAMP_Z),
        (0.014, -CLAMP_OUTER_R - 0.0113, CLAMP_Z),
    ]
    screw_mesh = _mesh_cq(_fastener_head_shape(), "fastener_head", assets)
    for i, pos in enumerate(fastener_positions):
        body.visual(
            screw_mesh, origin=Origin(xyz=pos), material=mats["fastener"], name=f"fastener_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal")
        )


_BASE_EMITTERS = {
    "cast_hex_foot": _emit_base_hex,
    "base_flange": _emit_base_flange,
    "base_tripod": _emit_base_tripod,
    "base_wallbracket": _emit_base_wallbracket,
}


# ---- handle slot (owns the piston part + barrel_to_piston PRISMATIC) ----
def _piston_pivot(r: ResolvedHandPumpConfig) -> tuple[float, float, float]:
    """World point used as the barrel_to_piston joint origin AND the piston link
    frame origin. fail_if_articulation_origin_far_from_geometry probes the SAME
    world point against both the parent (barrel) and child (cup) solid meshes,
    so it must sit within 0.015 m of both. On-axis the bored barrel is hollow,
    so the point is placed in the thin cup-wall ↔ bore-wall sealing gap (radius
    ~BARREL_BORE_R, mid-cup height). All piston visuals are authored in world
    coordinates and shifted by -pivot so the assembly stays on-axis."""
    return (0.0, BARREL_BORE_R - 0.0007, r.cup_center_z + CUP_LEN / 2.0)


def _emit_piston_rod_cup(piston, r: ResolvedHandPumpConfig, mats, assets, rod_top: float):
    px, py, pz = _piston_pivot(r)
    cup_top = r.cup_center_z + CUP_LEN
    piston.visual(
        _mesh_cq(_piston_head_shape(), "piston_head", assets),
        origin=Origin(xyz=(0.0 - px, 0.0 - py, r.cup_center_z - pz)),
        material=mats["black"],
        name="piston_head", material_class_id="rubber.smooth_plain",
    )
    rod_bottom = cup_top - 0.003
    rod_len = rod_top - rod_bottom
    piston.visual(
        Cylinder(radius=ROD_R, length=rod_len),
        origin=Origin(xyz=(0.0 - px, 0.0 - py, rod_bottom + rod_len / 2.0 - pz)),
        material=mats["rod"],
        name="rod", material_class_id=("metal.stainless_matte" if r.palette_style in {"cast_iron", "galvanized", "red_oxide", "forest_green", "industrial_blue"} else "metal.brass_polished"),
    )


def _emit_barrel_to_piston(model, body, piston, r: ResolvedHandPumpConfig) -> None:
    # Hero air-stroke. PRISMATIC, axis -Z (positive q drives the plunger DOWN).
    # The piston cup is a retained insertion inside the barrel bore (hidden,
    # overlapping); MatingContract does not model a telescoping insertion, so
    # the joint is grandfathered (no mating) and the overlap is allowed in
    # run_hand_pump_tests (see AUTHORING.md §B grandfathering).
    model.articulation(
        "barrel_to_piston",
        ArticulationType.PRISMATIC,
        parent=body,
        child=piston,
        origin=Origin(xyz=_piston_pivot(r)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.40, lower=0.0, upper=r.stroke),
    )


def _emit_handle_ball(model, body, r, mats, assets) -> None:
    piston = model.part("piston")
    px, py, pz = _piston_pivot(r)
    _emit_piston_rod_cup(piston, r, mats, assets, rod_top=r.handle_low_z + 0.006)
    piston.visual(
        Sphere(radius=KNOB_R),
        origin=Origin(xyz=(0.0 - px, 0.0 - py, r.handle_low_z + KNOB_R - pz)),
        material=mats["black"],
        name="ball_knob", material_class_id="plastic.opaque_glossy_molded",
    )
    _emit_barrel_to_piston(model, body, piston, r)


def _emit_handle_tbar(model, body, r, mats, assets) -> None:
    piston = model.part("piston")
    px, py, pz = _piston_pivot(r)
    center_z = r.handle_low_z + T_BAR_R + 0.018
    _emit_piston_rod_cup(piston, r, mats, assets, rod_top=r.handle_low_z + 0.018)
    piston.visual(
        _mesh_cq(_t_bar_grip_shape(center_z), "t_bar_grip", assets),
        origin=Origin(xyz=(-px, -py, -pz)),
        material=mats["black"],
        name="t_bar_grip", material_class_id="metal.blackened_gunmetal",
    )
    _emit_barrel_to_piston(model, body, piston, r)


def _emit_handle_dloop(model, body, r, mats, assets) -> None:
    piston = model.part("piston")
    px, py, pz = _piston_pivot(r)
    loop_bottom = r.handle_low_z + 0.009
    _emit_piston_rod_cup(piston, r, mats, assets, rod_top=loop_bottom + 0.008)
    piston.visual(
        mesh_from_geometry(_pull_loop_geometry(loop_bottom), "pull_loop"),
        origin=Origin(xyz=(-px, -py, -pz)),
        material=mats["black"],
        name="pull_loop", material_class_id="metal.blackened_gunmetal",
    )
    piston.visual(
        Cylinder(radius=0.013, length=0.018),
        origin=Origin(xyz=(0.0 - px, 0.0 - py, loop_bottom - pz)),
        material=mats["black"],
        name="loop_socket", material_class_id="metal.blackened_gunmetal",
    )
    _emit_barrel_to_piston(model, body, piston, r)


def _emit_handle_palmdisc(model, body, r, mats, assets) -> None:
    piston = model.part("piston")
    px, py, pz = _piston_pivot(r)
    disc_bottom = r.handle_low_z
    _emit_piston_rod_cup(piston, r, mats, assets, rod_top=disc_bottom + 0.008)
    piston.visual(
        mesh_from_geometry(_push_disc_geometry(disc_bottom), "push_disc"),
        origin=Origin(xyz=(-px, -py, -pz)),
        material=mats["black"],
        name="push_disc", material_class_id="plastic.opaque_glossy_molded",
    )
    _emit_barrel_to_piston(model, body, piston, r)


_HANDLE_EMITTERS = {
    "ball_knob_plunger": _emit_handle_ball,
    "handle_tbar": _emit_handle_tbar,
    "handle_dloop": _emit_handle_dloop,
    "handle_palmdisc": _emit_handle_palmdisc,
}


# ---- outlet slot ----
def _emit_floor_hose(body, r, mats, assets) -> None:
    hose_pts = [
        (0.0, -0.060, 0.030),
        (0.02, -0.110, 0.014),
        (0.075, -0.115, 0.012),
        (0.105, -0.050, 0.014),
        (0.105, 0.030, 0.016),
        (0.070, 0.072, 0.013),
        (0.020, 0.088, 0.0085),
        (-0.032, 0.070, 0.0075),
        (-0.072, 0.040, 0.0075),
    ]
    hose_geom = tube_from_spline_points(
        hose_pts, radius=0.0075, samples_per_segment=16, radial_segments=18, cap_ends=True
    )
    body.visual(mesh_from_geometry(hose_geom, "hose"), material=mats["hose"], name="hose", material_class_id="rubber.smooth_plain")


def _emit_outlet_hose(model, body, r, mats, assets) -> None:
    _emit_floor_hose(body, r, mats, assets)


def _emit_outlet_gooseneck(model, body, r, mats, assets) -> None:
    nozzle_x, nozzle_y, nozzle_top_z = 0.096, 0.016, 0.066
    spout_pts = [
        (0.0, -0.060, 0.030),
        (0.030, -0.087, 0.052),
        (0.070, -0.076, 0.083),
        (0.105, -0.038, 0.091),
        (0.112, 0.004, 0.079),
        (nozzle_x, nozzle_y, nozzle_top_z - 0.002),
    ]
    spout_geom = tube_from_spline_points(
        spout_pts, radius=0.0078, samples_per_segment=18, radial_segments=24, cap_ends=True
    )
    body.visual(
        _mesh_cq(_spout_socket_shape(), "spout_socket", assets),
        material=mats["spout"],
        name="spout_socket", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"),
    )
    body.visual(
        mesh_from_geometry(spout_geom, "gooseneck_spout"),
        material=mats["spout"],
        name="gooseneck_spout", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"),
    )
    body.visual(
        _mesh_cq(_downturned_nozzle_shape(), "downturned_nozzle", assets),
        material=mats["spout"],
        name="downturned_nozzle", material_class_id=("metal.paint_coated" if r.palette_style in {"cast_iron", "galvanized", "forest_green", "brass_bronze", "industrial_blue"} else "rust.oxidized_metal"),
    )


def _emit_outlet_barb(model, body, r, mats, assets) -> None:
    body.visual(
        _mesh_cq(_barbed_nipple_shape(), "barbed_nipple", assets),
        material=mats["black"],
        name="barbed_nipple", material_class_id="metal.blackened_gunmetal",
    )


def _emit_outlet_tapvalve(model, body, r, mats, assets) -> None:
    body.visual(
        _mesh_cq(_tap_body_shape(), "tap_body", assets),
        material=mats["brass"],
        name="tap_body", material_class_id="metal.brass_polished",
    )
    # The trailing floor hose is suppressed for the wall-mounted pose.
    if r.base_style != "base_wallbracket":
        _emit_floor_hose(body, r, mats, assets)
    # Quarter-turn tap handle: a separate moving child (REVOLUTE about +Z). The
    # stem is a captured insertion into the boss, so the joint is grandfathered.
    tap_handle = model.part("tap_handle")
    tap_handle.visual(
        _mesh_cq(_tap_handle_shape(), "tap_handle", assets),
        material=mats["brass"],
        name="tap_handle", material_class_id="metal.brass_polished",
    )
    model.articulation(
        "tap_to_handle",
        ArticulationType.REVOLUTE,
        parent=body,
        child=tap_handle,
        origin=Origin(xyz=(0.0, TAP_Y, TAP_BOSS_TOP_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=0.0, upper=pi / 2.0),
    )


_OUTLET_EMITTERS = {
    "loose_rubber_hose": _emit_outlet_hose,
    "outlet_gooseneck": _emit_outlet_gooseneck,
    "outlet_barb": _emit_outlet_barb,
    "outlet_tapvalve": _emit_outlet_tapvalve,
}


# ---- lever slot (always present, yoke_to_lever REVOLUTE) ----
def _emit_lever(model, body, r, mats, assets) -> None:
    lever = model.part("lever")
    lever.visual(_mesh_cq(_lever_shape(), "lever", assets), material=mats["black"], name="lever_arm", material_class_id="metal.blackened_gunmetal")
    lever.visual(
        _mesh_cq(_lever_endcap_shape(), "lever_endcap", assets),
        material=mats["white"],
        name="lever_endcap", material_class_id="plastic.opaque_glossy_molded",
    )
    # Captured-pin pivot (lever hub bore wraps the yoke pin) — grandfathered.
    model.articulation(
        "yoke_to_lever",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lever,
        origin=Origin(xyz=(CLEVIS_X, 0.0, YOKE_PIN_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=2.0, lower=-0.5, upper=0.5),
    )


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build_hand_pump(
    config: HandPumpConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"hp_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = model.part("pump_body")
    _emit_core_body(body, r, mats, assets)
    _BASE_EMITTERS[r.base_style](model, body, r, mats, assets)
    _HANDLE_EMITTERS[r.handle_style](model, body, r, mats, assets)
    _OUTLET_EMITTERS[r.outlet_style](model, body, r, mats, assets)
    _emit_lever(model, body, r, mats, assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_hand_pump(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_hand_pump(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Author tests
# --------------------------------------------------------------------------- #
def _expect_plunger_strokes(ctx, model, r) -> None:
    piston = model.get_part("piston")
    plunger = model.get_articulation("barrel_to_piston")
    rest = ctx.part_world_aabb(piston)
    with ctx.pose({plunger: plunger.motion_limits.upper}):
        pushed = ctx.part_world_aabb(piston)
    if rest is None or pushed is None:
        return
    ctx.check(
        "pumping lowers the piston handle",
        pushed[1][2] < rest[1][2] - r.stroke * 0.8,
        f"rest={rest}, pushed={pushed}",
    )


def _expect_lever_rocks(ctx, model) -> None:
    lever = model.get_part("lever")
    rocker = model.get_articulation("yoke_to_lever")
    rest = ctx.part_element_world_aabb(lever, elem="lever_endcap")
    with ctx.pose({rocker: 0.45}):
        up = ctx.part_element_world_aabb(lever, elem="lever_endcap")
    if rest is None or up is None:
        return
    ctx.check(
        "rocking the lever moves its end cap vertically",
        abs(up[0][2] - rest[0][2]) > 0.03,
        f"rest={rest}, posed={up}",
    )


def _expect_body_envelope(ctx, model) -> None:
    body = model.get_part("pump_body")
    aabb = ctx.part_world_aabb(body)
    if aabb is None:
        return
    z = aabb[1][2] - aabb[0][2]
    ctx.check(
        "barrel height realistic",
        0.18 <= z <= 0.40,
        f"unexpected pump_body z extent: {z:.4f}",
    )


def run_hand_pump_tests(
    object_model: ArticulatedObject,
    config: HandPumpConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("pump_body")
    piston = object_model.get_part("piston")
    lever = object_model.get_part("lever")

    # ---- Captured-pivot / retained-insertion allowances (element-scoped). ----
    ctx.allow_overlap(
        piston, body, elem_a="piston_head", elem_b="barrel",
        reason="The piston cup slides inside the hollow barrel bore (retained insertion).",
    )
    ctx.allow_overlap(
        piston, body, elem_a="rod", elem_b="cap",
        reason="The piston rod passes through the cap gland bore.",
    )
    ctx.allow_overlap(
        lever, body, elem_a="lever_arm", elem_b="yoke",
        reason="The lever hub bore captures the yoke pivot pin it rotates about.",
    )
    if r.outlet_style == "outlet_tapvalve":
        tap_handle = object_model.get_part("tap_handle")
        ctx.allow_overlap(
            tap_handle, body, elem_a="tap_handle", elem_b="tap_body",
            reason="The tap handle stem descends into the captured valve spindle boss.",
        )
        # The quarter-turn handle sweeps close across the pump body outlet boss.
        ctx.allow_overlap(
            tap_handle, body,
            reason="tap handle rotates adjacent to the pump outlet boss while turning",
        )

    # ---- Standard compiler-aligned QC stack. ----
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # ---- Hero joint topology claims. ----
    plunger = object_model.get_articulation("barrel_to_piston")
    rocker = object_model.get_articulation("yoke_to_lever")
    ctx.check(
        "barrel_to_piston is a vertical prismatic stroke",
        plunger.joint_type == ArticulationType.PRISMATIC
        and abs(plunger.axis[2]) > 0.99,
        f"type={plunger.joint_type} axis={plunger.axis}",
    )
    ctx.check(
        "yoke_to_lever is a Y-axis revolute",
        rocker.joint_type == ArticulationType.REVOLUTE
        and abs(rocker.axis[1]) > 0.99,
        f"type={rocker.joint_type} axis={rocker.axis}",
    )
    if r.outlet_style == "outlet_tapvalve":
        tap = object_model.get_articulation("tap_to_handle")
        ctx.check(
            "tap_to_handle is a Z-axis revolute",
            tap.joint_type == ArticulationType.REVOLUTE and abs(tap.axis[2]) > 0.99,
            f"type={tap.joint_type} axis={tap.axis}",
        )

    _expect_plunger_strokes(ctx, object_model, r)
    _expect_lever_rocks(ctx, object_model)
    _expect_body_envelope(ctx, object_model)

    return ctx.report()


__all__ = [
    "HandleStyle",
    "BaseStyle",
    "OutletStyle",
    "PaletteStyle",
    "HandPumpConfig",
    "ResolvedHandPumpConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_hand_pump",
    "build_seeded_hand_pump",
    "run_hand_pump_tests",
]
