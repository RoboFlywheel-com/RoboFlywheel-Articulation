# SPDX-License-Identifier: Apache-2.0

"""Astronomy / Space shuttle — modular procedural template.

A winged reusable spaceplane orbiter (Space Shuttle / Buran class) in landing
configuration: a blended-lifting-body or near-circular ``fuselage`` (black-TPS
underside, white upper skin) with a low delta wing carrying hinged elevons, a
vertical tail carrying a rudder / speed-brake, a body flap and closed payload-bay
doors on the spine, an aft cluster of 2-4 SSME bells flanked by 2 OMS pods, and a
deployed tricycle landing gear (steerable nose gear + 2 main gear on revolute or
prismatic struts, spinning wheels, hinged gear doors).

Slot graph (pattern = mixed: root airframe + 3 parallel-children slots + 3
multiplicity axes engine_count / elevon segments / main_wheel_count):

    airframe (root; fuselage: hull{blended|cylindrical} + wing{double|pure delta}
              + payload-bay layout{standard|satellite|laboratory} + N engine bells)
        ├─ control_surfaces (bay doors x2 + body flap + elevons x[2|4])
        ├─ tail             (fin fused visual + rudder x2)
        └─ landing_gear     (nose+2 main gear + 4 doors; revolute|prismatic)

Adapted per AUTHORING.md §A/§B from the confirmed 5-star Space shuttle pool
(spec: specs_modular_v1/Astronomy_Space_shuttle.md). All geometry helpers and
constant tables are ported from the origin 母本 model.py; ③/② axes swap the
station tables / joint types per the forked variants (see spec Module Source
Index). ``fuse_scale`` scales input coordinates uniformly; ``wing_span_scale``
scales spanwise |y|.

Coordinate frame: +X = nose/forward, +Y = left/port, +Z = up, ground at z=0.
All mirrored pieces straddle y=0.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from agent.templates._modular import (
    InterfaceSpec,
    ModuleBuild,
    ModuleBuildContext,
    SlotSpec,
    assemble,
)
from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    BoltPattern,
    Box,
    ConeGeometry,
    Cylinder,
    CylinderGeometry,
    LatheGeometry,
    LoftGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireSidewall,
    TireTread,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    mesh_from_cadquery,
    mesh_from_geometry,
    superellipse_side_loft,
)

__modular__ = True

SIDES = (("left", 1.0), ("right", -1.0))

HullForm = Literal["blended", "cylindrical"]
WingForm = Literal["double_delta", "pure_delta"]
ControlModule = Literal["single_elevon", "split_elevon"]
TailModule = Literal["swept_fin", "straight_fin", "twin_tail"]
GearModule = Literal["revolute_gear", "prismatic_gear"]
PayloadBayLayout = Literal["standard_bay", "satellite_deployer", "laboratory_module"]
ShuttlePalette = Literal["nasa_endeavour", "buran_white", "midnight_black", "bare_aluminum"]


# --------------------------------------------------------------------------- #
# Canonical constants (origin 母本 ...4400ecc9)
# --------------------------------------------------------------------------- #

# Payload bay / doors
BAY_X_FWD = 8.6
BAY_X_AFT = -7.4
BAY_LEN = BAY_X_FWD - BAY_X_AFT
BAY_X_MID = 0.5 * (BAY_X_FWD + BAY_X_AFT)
SILL_Y = 2.35
SILL_Z = 5.90
DOOR_CROWN_Z = 6.70
_h = DOOR_CROWN_Z - SILL_Z
DOOR_ARC_R = (SILL_Y * SILL_Y + _h * _h) / (2.0 * _h)
DOOR_ARC_ZC = DOOR_CROWN_Z - DOOR_ARC_R
DOOR_THICK = 0.10
DOOR_PHI_HINGE = math.atan2(SILL_Y, SILL_Z - DOOR_ARC_ZC)
DOOR_PHI_SEAM = math.asin(0.02 / DOOR_ARC_R)
DOOR_PHI_TUCK = 0.04

BAY_CUT_X_FWD = BAY_X_FWD - 0.2
BAY_CUT_X_AFT = BAY_X_AFT + 0.2
BAY_CUT_HALF_W = 2.12
BAY_FLOOR_Z = 4.15

# Wing planforms per side: (|y|, x_leading, x_trailing, z_bottom, thickness)
WING_STATIONS_DOUBLE = (
    (2.2, 11.5, -10.7, 3.02, 1.35),
    (3.0, 8.5, -10.7, 3.05, 0.95),
    (4.3, 3.6, -10.7, 3.10, 0.70),
    (7.5, -0.5, -10.7, 3.18, 0.45),
    (10.0, -3.6, -10.7, 3.25, 0.32),
    (11.6, -5.6, -10.7, 3.30, 0.22),
)
WING_STATIONS_PURE = (
    (2.2, 11.50, -10.7, 3.02, 1.35),
    (3.0, 10.05, -10.7, 3.05, 0.95),
    (4.3, 7.68, -10.7, 3.10, 0.70),
    (7.5, 1.86, -10.7, 3.18, 0.45),
    (10.0, -2.69, -10.7, 3.25, 0.32),
    (11.6, -5.60, -10.7, 3.30, 0.22),
)

# Elevons
ELEVON_HINGE_X = -10.55
ELEVON_TE_X = -12.75
ELEVON_Y_IN = 2.6
ELEVON_Y_OUT = 11.3
ELEVON_Z = 3.30

# Single swept fin: (z, x_leading, thickness)
FIN_STATIONS_SWEPT = (
    (6.75, -10.2, 0.72),
    (9.5, -11.9, 0.55),
    (13.0, -13.9, 0.40),
    (16.4, -15.9, 0.26),
)
# Straight-tapered fin (unswept LE)
FIN_STATIONS_STRAIGHT = (
    (6.75, -10.5, 0.72),
    (9.5, -10.5, 0.58),
    (13.0, -10.5, 0.44),
    (16.4, -10.5, 0.30),
)
RUDDER_ROOT_Z = 7.2
RUDDER_TIP_Z = 16.2
RUDDER_TE_ROOT_X = -17.0
RUDDER_TE_TIP_X = -17.85
RUDDER_PANEL_T = 0.17
# Split speed-brake: each half sits wholly on its own side of the centreline (its
# leading edge lies ON the hinge line, nothing forward of it) and only ever opens
# OUTBOARD, so the two halves never cross into each other -> no rudder-vs-rudder
# overlap and no allow_overlap mask.
RUDDER_OPEN = 0.62
# The single fin's trailing edge runs slightly AFT of the hinge line so it buries
# the rudder leading edge (cove contact -> rudder not isolated).
FIN_TE_AFT_OF_HINGE = 0.16

# Twin fins (fin-local frame: dz, x_le, x_te, thickness)
TWIN_FIN_Y_OFFSET = 1.75
TWIN_FIN_ROOT_Z = 8.15
TWIN_FIN_STATIONS = (
    (0.0, -11.0, -14.5, 0.50),
    (1.5, -11.8, -14.7, 0.40),
    (3.0, -12.8, -14.9, 0.30),
    (4.5, -13.6, -15.1, 0.20),
)
TWIN_FIN_TIP_DZ = TWIN_FIN_STATIONS[-1][0]
TWIN_RUDDER_HINGE_X = (-14.2, -14.8)
TWIN_RUDDER_TE_X = (-16.0, -16.5)
TWIN_RUDDER_PANEL_T = 0.14

# Body flap
FLAP_HINGE = (-16.75, 0.0, 3.45)
FLAP_CHORD = 2.35
FLAP_WIDTH = 5.7
FLAP_THICK = 0.34

# Landing gear
NOSE_GEAR_X = 13.3
NOSE_GEAR_TOP_Z = 3.30
NOSE_WHEEL_R = 0.41
NOSE_WHEEL_W = 0.22
NOSE_FORK_DROP = 1.55
NOSE_AXLE_DROP = NOSE_GEAR_TOP_Z - NOSE_FORK_DROP - NOSE_WHEEL_R

MAIN_GEAR_X = -2.6
MAIN_GEAR_Y = 3.45
MAIN_GEAR_TOP_Z = 3.35
MAIN_WHEEL_R = 0.56
MAIN_WHEEL_W = 0.40
MAIN_AXLE_DROP = MAIN_GEAR_TOP_Z - MAIN_WHEEL_R

# Gear-DOWN at q=0 for BOTH joint types so the rest pose is a clean landed
# stance, and positive travel always retracts.
#
# revolute_gear: the whole leg pivots on its trunnion, so the retract range is
# capped where the swung wheel still clears the wing underside.
GEAR_REVOLUTE_UPPER = 0.7

# prismatic_gear: a telescoping leg's moving element is the inner PISTON, not
# the whole leg. The outer trunnion cylinder and its braces are fixed structure
# fused into the fuselage; only the piston slides inside that bore. Modelling it
# this way is what keeps the moving part from ever rising above the housing and
# punching out through the wing/hull skin.
#   *_HOUSING_*: fixed outer bore, in strut-local z (0 = trunnion).
#   *_PISTON_*:  moving inner rod, fully deployed (q=0).
# The bore is kept SHORT and high so the retracting wheels pass under it; the
# piston is correspondingly long and carries the whole visible leg.
NOSE_HOUSING_TOP_Z = 0.55
NOSE_HOUSING_BOT_Z = -0.45
NOSE_PISTON_TOP_Z = -0.25
NOSE_PISTON_BOT_Z = -NOSE_FORK_DROP - 0.20

MAIN_HOUSING_TOP_Z = 0.40
MAIN_HOUSING_BOT_Z = -0.60
MAIN_PISTON_TOP_Z = -0.40

# Retract stroke window, in nominal (pre-fuse_scale) metres. Four independent
# ceilings, all satisfied with margin at 0.70:
#   piston crown stays inside its bore    -> <= 0.80 main, 0.80 nose
#   retracted wheels stay under the bore  -> <= 0.88 main, 1.03 nose
#   retracted nose fork clears the bore   -> <= 0.80
#   retracted nose fork clears drag brace -> <= 1.12
# Sizing the stroke from the structure (rather than picking a travel and then
# masking whatever it hits) is what keeps every retracted pose clip-free.
GEAR_PRISMATIC_STROKE_MIN = 0.45
GEAR_PRISMATIC_STROKE_MAX = 0.70

# Aft engine mount tables by count: (ey, ez, pitch_deg). Bells sit high on the
# base shield so the body flap's up-deflection clears them.
ENGINE_MOUNTS = {
    2: ((1.30, 5.7, 10.0), (-1.30, 5.7, 10.0)),
    3: ((0.0, 6.35, 12.0), (1.30, 5.30, 8.0), (-1.30, 5.30, 8.0)),
    4: ((1.20, 6.15, 10.0), (-1.20, 6.15, 10.0), (1.20, 5.25, 10.0), (-1.20, 5.25, 10.0)),
}
BELL_PROFILE = ((0.44, 0.0), (0.56, 0.35), (0.78, 1.0), (1.02, 1.85), (1.15, 2.55))

OMS_SECTIONS = (
    (-11.8, 6.25, 6.75, 0.85),
    (-12.8, 6.15, 7.90, 2.00),
    (-14.5, 6.15, 8.15, 2.30),
    (-16.3, 6.20, 8.00, 2.10),
    (-17.3, 6.35, 7.50, 1.40),
)

HULL_SECTIONS_BLENDED = (
    (17.8, 4.32, 4.55, 0.36),
    (16.9, 3.95, 5.05, 1.70),
    (15.3, 3.55, 5.75, 3.15),
    (13.4, 3.30, 6.28, 4.35),
    (10.6, 3.10, 6.55, 4.90),
    (9.4, 3.05, 6.30, 5.10),
    (8.6, 3.05, 5.98, 5.20),
    (-7.4, 3.05, 5.98, 5.20),
    (-8.6, 3.10, 6.45, 5.30),
    (-10.5, 3.18, 6.90, 5.50),
    (-14.5, 3.35, 6.90, 5.20),
    (-16.9, 3.60, 6.75, 4.50),
)
HULL_EXPO_BLENDED = (2.0, 2.0, 2.2, 2.5, 2.7, 3.0, 3.4, 3.4, 3.0, 2.8, 2.7, 2.5)
HULL_SECTIONS_CYL = (
    (17.8, 4.32, 4.55, 0.36),
    (16.9, 3.55, 5.50, 2.00),
    (15.3, 3.05, 6.25, 3.55),
    (13.4, 2.88, 6.68, 4.50),
    (10.6, 2.85, 6.88, 4.78),
    (9.4, 2.85, 6.88, 4.85),
    (8.6, 2.85, 6.88, 4.85),
    (-7.4, 2.85, 6.88, 4.85),
    (-8.6, 2.85, 6.92, 4.92),
    (-10.5, 2.88, 7.02, 5.00),
    (-14.5, 2.98, 6.98, 5.00),
    (-16.9, 3.25, 6.78, 4.55),
)
HULL_EXPO_CYL = tuple([2.0] * 12)

BELLY_SECTIONS = (
    (17.82, 4.28, 4.60, 0.44),
    (16.9, 3.90, 4.95, 1.80),
    (15.3, 3.50, 4.70, 3.26),
    (13.4, 3.25, 4.18, 4.46),
    (10.6, 3.05, 3.88, 5.00),
    (8.6, 3.00, 3.74, 5.30),
    (-7.4, 3.00, 3.74, 5.30),
    (-10.5, 3.13, 3.92, 5.60),
    (-14.5, 3.30, 4.06, 5.30),
    (-16.9, 3.55, 4.42, 4.60),
)
BELLY_EXPO = (2.0, 2.0, 2.2, 2.4, 2.6, 2.8, 2.8, 2.6, 2.5, 2.4)
NOSE_SECTIONS = ((17.86, 4.26, 4.62, 0.50), (17.2, 3.90, 5.12, 1.80), (16.3, 3.75, 5.15, 2.40))
CHINE_SECTIONS = (
    (16.9, 4.05, 4.50, 1.86),
    (15.3, 3.95, 4.45, 3.24),
    (13.4, 3.85, 4.35, 4.44),
    (11.3, 3.80, 4.28, 4.86),
)


# --------------------------------------------------------------------------- #
# Palettes (>=4 colorways; every token resolves so any .visual works)
# --------------------------------------------------------------------------- #

def _pal(white, black, charcoal, glass, silver, steel, throat, tire, red, blue):
    return {
        "tps_white": white,
        "tps_black": black,
        "tps_charcoal": charcoal,
        "window_glass": glass,
        "gear_silver": silver,
        "nozzle_steel": steel,
        "nozzle_throat": throat,
        "tire_rubber": tire,
        "flag_red": red,
        "flag_blue": blue,
    }


PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "nasa_endeavour": _pal(
        (0.92, 0.92, 0.94, 1.0), (0.10, 0.10, 0.12, 1.0), (0.17, 0.17, 0.19, 1.0),
        (0.04, 0.04, 0.07, 1.0), (0.72, 0.73, 0.75, 1.0), (0.42, 0.42, 0.45, 1.0),
        (0.14, 0.14, 0.15, 1.0), (0.07, 0.07, 0.08, 1.0), (0.70, 0.12, 0.15, 1.0),
        (0.10, 0.16, 0.42, 1.0),
    ),
    "buran_white": _pal(
        (0.95, 0.96, 0.98, 1.0), (0.16, 0.18, 0.22, 1.0), (0.34, 0.36, 0.40, 1.0),
        (0.05, 0.07, 0.12, 1.0), (0.70, 0.72, 0.76, 1.0), (0.48, 0.50, 0.54, 1.0),
        (0.16, 0.17, 0.19, 1.0), (0.08, 0.08, 0.09, 1.0), (0.66, 0.16, 0.18, 1.0),
        (0.12, 0.20, 0.48, 1.0),
    ),
    "midnight_black": _pal(
        (0.20, 0.21, 0.24, 1.0), (0.06, 0.06, 0.08, 1.0), (0.11, 0.11, 0.13, 1.0),
        (0.03, 0.04, 0.07, 1.0), (0.52, 0.54, 0.58, 1.0), (0.36, 0.37, 0.40, 1.0),
        (0.08, 0.08, 0.09, 1.0), (0.05, 0.05, 0.06, 1.0), (0.55, 0.12, 0.14, 1.0),
        (0.10, 0.13, 0.30, 1.0),
    ),
    "bare_aluminum": _pal(
        (0.78, 0.80, 0.83, 1.0), (0.22, 0.23, 0.26, 1.0), (0.40, 0.42, 0.45, 1.0),
        (0.06, 0.08, 0.12, 1.0), (0.84, 0.86, 0.89, 1.0), (0.60, 0.62, 0.66, 1.0),
        (0.18, 0.19, 0.21, 1.0), (0.09, 0.09, 0.10, 1.0), (0.62, 0.16, 0.18, 1.0),
        (0.14, 0.20, 0.44, 1.0),
    ),
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class AstronomySpaceShuttleConfig:
    hull_form: HullForm = "blended"
    wing_form: WingForm = "double_delta"
    payload_bay_layout: PayloadBayLayout = "standard_bay"
    control_module: ControlModule = "single_elevon"
    tail_module: TailModule = "swept_fin"
    gear_module: GearModule = "revolute_gear"
    palette_style: ShuttlePalette = "nasa_endeavour"

    engine_count: int = 3
    main_wheel_count: int = 2

    fuse_scale: float = 1.0
    wing_span_scale: float = 1.0
    elevon_up: float = 0.40
    gear_deploy: float = 0.65


@dataclass(frozen=True)
class ResolvedAstronomySpaceShuttleConfig:
    hull_form: HullForm
    wing_form: WingForm
    payload_bay_layout: PayloadBayLayout
    control_module: ControlModule
    tail_module: TailModule
    gear_module: GearModule
    palette_style: str

    engine_count: int
    main_wheel_count: int

    fuse_scale: float
    wing_span_scale: float
    elevon_up: float
    gear_deploy: float

    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> AstronomySpaceShuttleConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin 母本 combination (blended double-delta,
    single elevon, swept fin, revolute gear, 3 engines, dual main wheels,
    nasa_endeavour) as a documented regression anchor; every other seed is
    fully procedural.
    """
    if seed == 0:
        return AstronomySpaceShuttleConfig()

    rng = random.Random(seed)
    return AstronomySpaceShuttleConfig(
        hull_form=rng.choice(("blended", "cylindrical")),
        wing_form=rng.choice(("double_delta", "pure_delta")),
        payload_bay_layout=rng.choice(("standard_bay", "satellite_deployer", "laboratory_module")),
        control_module=rng.choice(("single_elevon", "split_elevon")),
        tail_module=rng.choice(("swept_fin", "straight_fin", "twin_tail")),
        gear_module=rng.choice(("revolute_gear", "prismatic_gear")),
        palette_style=rng.choice(PALETTE_NAMES),
        engine_count=rng.choices((2, 3, 4), weights=(0.25, 0.5, 0.25))[0],
        main_wheel_count=rng.choices((1, 2), weights=(0.3, 0.7))[0],
        fuse_scale=round(rng.uniform(0.90, 1.12), 4),
        wing_span_scale=round(rng.uniform(0.92, 1.10), 4),
        elevon_up=round(rng.uniform(0.30, 0.45), 4),
        gear_deploy=round(
            rng.uniform(GEAR_PRISMATIC_STROKE_MIN, GEAR_PRISMATIC_STROKE_MAX), 4
        ),
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(
    config: AstronomySpaceShuttleConfig,
) -> ResolvedAstronomySpaceShuttleConfig:
    if str(config.hull_form) not in {"blended", "cylindrical"}:
        raise ValueError(f"Unsupported hull_form: {config.hull_form}")
    if str(config.wing_form) not in {"double_delta", "pure_delta"}:
        raise ValueError(f"Unsupported wing_form: {config.wing_form}")
    if str(config.payload_bay_layout) not in {
        "standard_bay", "satellite_deployer", "laboratory_module"
    }:
        raise ValueError(f"Unsupported payload_bay_layout: {config.payload_bay_layout}")
    if str(config.control_module) not in {"single_elevon", "split_elevon"}:
        raise ValueError(f"Unsupported control_module: {config.control_module}")
    if str(config.tail_module) not in {"swept_fin", "straight_fin", "twin_tail"}:
        raise ValueError(f"Unsupported tail_module: {config.tail_module}")
    if str(config.gear_module) not in {"revolute_gear", "prismatic_gear"}:
        raise ValueError(f"Unsupported gear_module: {config.gear_module}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    return ResolvedAstronomySpaceShuttleConfig(
        hull_form=config.hull_form,
        wing_form=config.wing_form,
        payload_bay_layout=config.payload_bay_layout,
        control_module=config.control_module,
        tail_module=config.tail_module,
        gear_module=config.gear_module,
        palette_style=config.palette_style,
        engine_count=int(_clamp(config.engine_count, 2, 4)),
        main_wheel_count=int(_clamp(config.main_wheel_count, 1, 2)),
        fuse_scale=_clamp(config.fuse_scale, 0.90, 1.12),
        wing_span_scale=_clamp(config.wing_span_scale, 0.92, 1.10),
        elevon_up=_clamp(config.elevon_up, 0.30, 0.45),
        gear_deploy=_clamp(
            config.gear_deploy, GEAR_PRISMATIC_STROKE_MIN, GEAR_PRISMATIC_STROKE_MAX
        ),
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# Geometry helpers (ported verbatim from origin 母本; input-scaled by fuse_scale)
# --------------------------------------------------------------------------- #


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _scl(loop, s: float):
    """Uniformly scale a list of (x,y,z) points by ``s`` (fuse_scale)."""
    return [(s * a, s * b, s * c) for (a, b, c) in loop]


def _o(s: float, x: float, y: float, z: float, rpy=(0.0, 0.0, 0.0)) -> Origin:
    return Origin(xyz=(s * x, s * y, s * z), rpy=rpy)


def _box(s: float, a: float, b: float, c: float) -> Box:
    return Box((s * a, s * b, s * c))


def _cyl(s: float, radius: float, length: float) -> Cylinder:
    return Cylinder(radius=s * radius, length=s * length)


def _airfoil_loop(x_le, x_te, y, z_b, thick, samples=9):
    """Chordwise wing station loop authored as (x, -z, y); rotate_x(-pi/2)
    maps to world (x, y, z). Flat bottom, rounded top (origin L142-159)."""
    pts = []
    for i in range(samples):
        s = i / (samples - 1)
        x = _lerp(x_le, x_te, s)
        bump = (4.0 * s * (1.0 - s)) ** 0.7
        pts.append((x, -(z_b + max(0.02, thick * bump)), y))
    for i in range(samples):
        s = 1.0 - i / (samples - 1)
        x = _lerp(x_le, x_te, s)
        pts.append((x, -z_b, y))
    return pts


def _fin_loop(z, x_le, x_te, thick, samples=7):
    """Vertical-fin lens loop in the XY plane at height z (origin L162-172)."""
    top, bot = [], []
    for i in range(samples):
        s = i / (samples - 1)
        x = _lerp(x_le, x_te, s)
        w = max(0.015, 0.5 * thick * (4.0 * s * (1.0 - s)) ** 0.6)
        top.append((x, w, z))
        bot.append((x, -w, z))
    return top + bot[::-1]


def _door_arc_loop(x_local, side, r_out, r_in, phi_lo, phi_hi, n=14):
    """Bay-door annular arc cross-section in door-local frame (origin L175-193)."""
    outer, inner = [], []
    for i in range(n):
        phi = _lerp(phi_lo, phi_hi, i / (n - 1))
        s, c = math.sin(phi), math.cos(phi)
        outer.append((-(DOOR_ARC_ZC + r_out * c - SILL_Z), side * r_out * s - side * SILL_Y, x_local))
        inner.append((-(DOOR_ARC_ZC + r_in * c - SILL_Z), side * r_in * s - side * SILL_Y, x_local))
    loop = outer + inner[::-1]
    if side < 0:
        loop = loop[::-1]
    return loop


def _superellipse_wire(x, z0, z1, w, e, n=40):
    """Closed smooth superellipse cross-section wire in the YZ plane (origin L196-209)."""
    zc = 0.5 * (z0 + z1)
    hh = 0.5 * (z1 - z0)
    hw = 0.5 * w
    pts = []
    for i in range(n):
        t = 2.0 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        y = hw * math.copysign(abs(c) ** (2.0 / e), c)
        z = zc + hh * math.copysign(abs(s) ** (2.0 / e), s)
        pts.append(cq.Vector(x, y, z))
    return cq.Wire.assembleEdges([cq.Edge.makeSpline(pts, periodic=True)])


def _tube(s, radius, p0, p1, segments=16):
    """Cylinder mesh from p0 to p1 (part-local points); all inputs scaled by s."""
    p0 = (s * p0[0], s * p0[1], s * p0[2])
    p1 = (s * p1[0], s * p1[1], s * p1[2])
    radius = s * radius
    dx, dy, dz = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    geom = CylinderGeometry(radius, length, radial_segments=segments)
    yaw = math.atan2(dy, dx)
    pitch = math.acos(max(-1.0, min(1.0, dz / length)))
    geom.rotate_y(pitch)
    geom.rotate_z(yaw)
    geom.translate(0.5 * (p0[0] + p1[0]), 0.5 * (p0[1] + p1[1]), 0.5 * (p0[2] + p1[2]))
    return geom


def _wheel_geoms(s, tire_r, tire_w, rim_r):
    """Build ONE (rim, tire) MeshGeometry pair (shared across wheel parts)."""
    tire_r, tire_w, rim_r = s * tire_r, s * tire_w, s * rim_r
    wheel = WheelGeometry(
        rim_r, tire_w * 0.72,
        rim=WheelRim(inner_radius=rim_r * 0.62, flange_height=0.02 * s,
                     flange_thickness=0.012 * s, bead_seat_depth=0.008 * s),
        hub=WheelHub(radius=rim_r * 0.38, width=tire_w * 0.5, cap_style="domed",
                     bolt_pattern=BoltPattern(count=6, circle_diameter=rim_r * 0.55,
                                              hole_diameter=0.022 * s)),
        face=WheelFace(dish_depth=0.005 * s, front_inset=0.003 * s, rear_inset=0.003 * s),
    )
    tire = TireGeometry(
        tire_r, tire_w, inner_radius=rim_r,
        carcass=TireCarcass(belt_width_ratio=0.62, sidewall_bulge=0.07),
        tread=TireTread(style="ribbed", depth=0.012 * s, count=4, land_ratio=0.6),
        sidewall=TireSidewall(style="rounded", bulge=0.05),
    )
    return (mesh_from_geometry(wheel, "wheel_rim"), mesh_from_geometry(tire, "wheel_tire"))


def _rudder_hinge_x_swept(z):
    return -15.7 - 1.0 * (z - 7.2) / (16.2 - 7.2)


def _rudder_hinge_x_straight(z):
    return -15.8 - 0.3 * (z - 7.2) / (16.2 - 7.2)


# --------------------------------------------------------------------------- #
# Downstream interface (parallel-children: re-export fuselage; no chain joint)
# --------------------------------------------------------------------------- #


def _fuselage_downstream(r: ResolvedAstronomySpaceShuttleConfig) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="fuselage",
        visual_name="hull",
        face_side="positive_z",
        anchor_local=(r.fuse_scale * BAY_X_MID, 0.0, r.fuse_scale * SILL_Z),
        contact_tol=0.01,
    )


# --------------------------------------------------------------------------- #
# Slot A — airframe (root; ③ hull + wing + engine count)
# --------------------------------------------------------------------------- #


def _build_airframe(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedAstronomySpaceShuttleConfig = ctx.config  # type: ignore[assignment]
    s = r.fuse_scale
    fus = model.part("fuselage")

    # --- main hull: superellipse loft with a real payload-bay cavity cut ---
    if r.hull_form == "cylindrical":
        sections, expo = HULL_SECTIONS_CYL, HULL_EXPO_CYL
    else:
        sections, expo = HULL_SECTIONS_BLENDED, HULL_EXPO_BLENDED
    hull_solid = cq.Solid.makeLoft(
        [_superellipse_wire(s * x, s * z0, s * z1, s * w, e)
         for (x, z0, z1, w), e in zip(sections, expo)],
        ruled=True,
    )
    bay_len = (BAY_CUT_X_FWD - BAY_CUT_X_AFT) * s
    bay_cut = cq.Solid.makeBox(bay_len, 2.0 * BAY_CUT_HALF_W * s, 3.5 * s).translate(
        (BAY_CUT_X_AFT * s, -BAY_CUT_HALF_W * s, BAY_FLOOR_Z * s)
    )
    hull_solid = hull_solid.cut(bay_cut)
    fus.visual(mesh_from_cadquery(cq.Workplane("XY").add(hull_solid), "hull"),
               material="tps_white", name="hull", material_class_id="metal.paint_coated")

    # --- black TPS belly / nose / chine skins ---
    belly = superellipse_side_loft(
        [(s * x, s * z0, s * z1, s * w) for (x, z0, z1, w) in BELLY_SECTIONS],
        exponents=BELLY_EXPO, segments=44,
    ).rotate_z(-math.pi / 2.0)
    fus.visual(mesh_from_geometry(belly, "belly_tiles"), material="tps_black", name="belly_tiles", material_class_id="ceramic.architectural_tile")
    nose = superellipse_side_loft(
        [(s * x, s * z0, s * z1, s * w) for (x, z0, z1, w) in NOSE_SECTIONS],
        exponents=2.0, segments=36,
    ).rotate_z(-math.pi / 2.0)
    fus.visual(mesh_from_geometry(nose, "nose_cap"), material="tps_black", name="nose_cap", material_class_id="fabric.carbon_weave")
    chine = superellipse_side_loft(
        [(s * x, s * z0, s * z1, s * w) for (x, z0, z1, w) in CHINE_SECTIONS],
        exponents=2.2, segments=36,
    ).rotate_z(-math.pi / 2.0)
    fus.visual(mesh_from_geometry(chine, "chine_band"), material="tps_black", name="chine_band", material_class_id="ceramic.architectural_tile")

    # --- forward RCS panel + thruster ports ---
    fus.visual(_box(s, 1.5, 1.9, 0.06), origin=_o(s, 15.7, 0.0, 5.42, rpy=(0.0, -0.30, 0.0)),
               material="tps_charcoal", name="forward_rcs_panel", material_class_id="metal.paint_coated")
    for name, side in SIDES:
        for i in range(3):
            fus.visual(_box(s, 0.26, 0.05, 0.20),
                       origin=_o(s, 16.5 - 0.45 * i, side * (1.05 + 0.10 * i), 4.55),
                       material="tps_charcoal", name=f"{name}_rcs_port_{i}", material_class_id="metal.paint_coated")

    # --- cockpit windows + crew hatch ---
    # Panes are seated deep (thickened in y and z) so they stay embedded in the
    # cockpit skin across both hull envelopes (the cylindrical crown sits inboard
    # of the blended one).
    for i in range(6):
        t = (i - 2.5) / 2.5
        fus.visual(_box(s, 0.60, 0.80, 0.78),
                   origin=_o(s, 14.95 - 0.55 * abs(t), 1.10 * t, 5.78, rpy=(0.0, -0.70, 0.55 * t)),
                   material="window_glass", name=f"window_pane_{i}", material_class_id="glass.clear_transparent")
    fus.visual(_cyl(s, 0.46, 0.06), origin=_o(s, 12.4, 2.24, 4.85, rpy=(math.pi / 2.0, 0.0, 0.0)),
               material="tps_charcoal", name="crew_hatch_ring", material_class_id="metal.paint_coated")

    # --- payload bay interior + sills (doors hinge onto the sills) ---
    bay_len_i = BAY_CUT_X_FWD - BAY_CUT_X_AFT
    fus.visual(_box(s, bay_len_i - 0.1, 2.0 * BAY_CUT_HALF_W - 0.1, 0.08),
               origin=_o(s, BAY_X_MID, 0.0, BAY_FLOOR_Z + 0.02),
               material="tps_charcoal", name="payload_bay_floor", material_class_id="ceramic.architectural_tile")
    for name, side in SIDES:
        fus.visual(_box(s, bay_len_i - 0.3, 0.14, 0.12),
                   origin=_o(s, BAY_X_MID, side * 1.55, BAY_FLOOR_Z + 0.12),
                   material="gear_silver", name=f"{name}_payload_rail", material_class_id="metal.aluminum_bare")
        fus.visual(_box(s, BAY_LEN, 0.34, 0.36),
                   origin=_o(s, BAY_X_MID, side * SILL_Y, SILL_Z - 0.14),
                   material="tps_white", name=f"{name}_bay_sill", material_class_id="metal.paint_coated")

    # Payload-bay layout is a structural/function axis, not a loose payload
    # prop.  All variants stay inside the existing bay envelope and are fused
    # into the fuselage part, while changing the support/interface architecture.
    if r.payload_bay_layout == "standard_bay":
        fus.visual(
            _box(s, bay_len_i - 0.8, 0.22, 0.20),
            origin=_o(s, BAY_X_MID, 0.0, BAY_FLOOR_Z + 0.15),
            material="gear_silver",
            name="payload_standard_keel", material_class_id="metal.aluminum_bare",
        )
    elif r.payload_bay_layout == "satellite_deployer":
        fus.visual(
            _box(s, bay_len_i - 1.2, 1.20, 0.30),
            origin=_o(s, BAY_X_MID, 0.0, BAY_FLOOR_Z + 0.20),
            material="gear_silver",
            name="payload_satellite_truss", material_class_id="metal.aluminum_bare",
        )
        for x, label in ((BAY_X_AFT + 2.0, "aft"), (BAY_X_FWD - 2.0, "forward")):
            fus.visual(
                _box(s, 0.42, 2.75, 0.36),
                origin=_o(s, x, 0.0, BAY_FLOOR_Z + 0.48),
                material="gear_silver",
                name=f"payload_satellite_{label}_adapter", material_class_id="metal.aluminum_bare",
            )
            fus.visual(
                _box(s, 0.34, 0.22, 0.55),
                origin=_o(s, x, 0.0, BAY_FLOOR_Z + 0.55),
                material="nozzle_steel",
                name=f"payload_satellite_{label}_pedestal", material_class_id="metal.steel_bare",
            )
    else:
        fus.visual(
            mesh_from_geometry(
                _tube(
                    s,
                    1.16,
                    (BAY_X_AFT + 2.1, 0.0, BAY_FLOOR_Z + 1.18),
                    (BAY_X_FWD - 2.1, 0.0, BAY_FLOOR_Z + 1.18),
                    segments=32,
                ),
                "payload_laboratory_module",
            ),
            material="tps_white",
            name="payload_laboratory_module", material_class_id="metal.paint_coated",
        )
        for side, label in ((1.0, "port"), (-1.0, "starboard")):
            fus.visual(
                _box(s, bay_len_i - 2.0, 0.24, 0.68),
                origin=_o(s, BAY_X_MID, side * 1.70, BAY_FLOOR_Z + 0.40),
                material="gear_silver",
                name=f"payload_laboratory_{label}_rack", material_class_id="metal.aluminum_bare",
            )
        fus.visual(
            _box(s, 1.10, 0.20, 0.76),
            origin=_o(s, BAY_X_FWD - 1.2, -1.78, BAY_FLOOR_Z + 0.40),
            material="tps_charcoal",
            name="payload_laboratory_umbilical_panel", material_class_id="metal.paint_coated",
        )

    # --- livery: flag + insignia + name strip ---
    # Side decals are thickened inboard (visible outer face kept at |y|~2.58) so
    # they stay embedded in either hull envelope (cylindrical side skin sits a few
    # cm inboard of the blended one at this station).
    fus.visual(_box(s, 0.80, 0.18, 0.34), origin=_o(s, 2.2, 2.49, 4.95),
               material="tps_white", name="flag_field", appearance_only=AppearanceOnlySpec(kind="decal"))
    for i in range(3):
        fus.visual(_box(s, 0.80, 0.18, 0.045), origin=_o(s, 2.2, 2.49, 4.82 + 0.12 * i),
                   material="flag_red", name=f"flag_stripe_{i}", appearance_only=AppearanceOnlySpec(kind="decal"))
    fus.visual(_box(s, 0.36, 0.18, 0.18), origin=_o(s, 2.42, 2.49, 5.02),
               material="flag_blue", name="flag_canton", appearance_only=AppearanceOnlySpec(kind="decal"))
    fus.visual(_cyl(s, 0.30, 0.20), origin=_o(s, -3.4, 2.48, 4.95, rpy=(math.pi / 2.0, 0.0, 0.0)),
               material="flag_blue", name="insignia_roundel", appearance_only=AppearanceOnlySpec(kind="decal"))
    fus.visual(_box(s, 3.4, 0.18, 0.30), origin=_o(s, 0.4, -2.49, 4.95),
               material="tps_charcoal", name="name_strip", appearance_only=AppearanceOnlySpec(kind="overlay"))

    # --- wings: delta lofts + black leading edge + black underside ---
    stations = WING_STATIONS_PURE if r.wing_form == "pure_delta" else WING_STATIONS_DOUBLE
    w_span = r.wing_span_scale
    for name, side in SIDES:
        loops, le_loops, under_loops = [], [], []
        for (ay, x_le, x_te, z_b, th) in stations:
            y = side * ay * w_span
            loops.append(_airfoil_loop(x_le, x_te, y, z_b, th))
            le_loops.append(_airfoil_loop(x_le - 0.08, x_le + 1.2, y, z_b - 0.05, th * 0.85 + 0.06))
            under_loops.append(_airfoil_loop(x_le + 0.3, x_te, y, z_b - 0.035, 0.05))
        if side < 0:
            loops = [lp[::-1] for lp in loops]
            le_loops = [lp[::-1] for lp in le_loops]
            under_loops = [lp[::-1] for lp in under_loops]
        rot = -math.pi / 2.0
        fus.visual(mesh_from_geometry(LoftGeometry([_scl(lp, s) for lp in loops]).rotate_x(rot),
                                      f"{name}_wing"), material="tps_white", name=f"{name}_wing", material_class_id="metal.paint_coated")
        fus.visual(mesh_from_geometry(LoftGeometry([_scl(lp, s) for lp in le_loops]).rotate_x(rot),
                                      f"{name}_wing_le"), material="tps_black",
                   name=f"{name}_wing_leading_edge", material_class_id="fabric.carbon_weave")
        fus.visual(mesh_from_geometry(LoftGeometry([_scl(lp, s) for lp in under_loops]).rotate_x(rot),
                                      f"{name}_wing_under"), material="tps_black",
                   name=f"{name}_wing_underside", material_class_id="ceramic.architectural_tile")

    # --- OMS pods flanking the tail on the aft deck ---
    for name, side in SIDES:
        pod = superellipse_side_loft(
            [(s * x, s * z0, s * z1, s * w) for (x, z0, z1, w) in OMS_SECTIONS],
            exponents=2.2, segments=32,
        ).rotate_z(-math.pi / 2.0).translate(0.0, s * side * 1.75, 0.0)
        fus.visual(mesh_from_geometry(pod, f"{name}_oms_pod"), material="tps_white",
                   name=f"{name}_oms_pod", material_class_id="metal.paint_coated")
        oms_bell = ConeGeometry(0.42 * s, 1.05 * s, radial_segments=24)
        oms_bell.rotate_y(math.radians(105.0))
        oms_bell.translate(s * -17.35, s * side * 1.75, s * 7.35)
        fus.visual(mesh_from_geometry(oms_bell, f"{name}_oms_nozzle"), material="nozzle_steel",
                   name=f"{name}_oms_nozzle", material_class_id="metal.stainless_matte")

    # --- aft base heat shield + N SSME bells (multiplicity engine_count) ---
    fus.visual(_box(s, 0.5, 4.4, 3.1), origin=_o(s, -17.0, 0.0, 5.0),
               material="nozzle_steel", name="base_heat_shield", material_class_id="metal.blackened_gunmetal")
    mounts = ENGINE_MOUNTS[r.engine_count]
    for i, (ey, ez, pitch_deg) in enumerate(mounts):
        bell = LatheGeometry([(s * rr, s * zz) for (rr, zz) in BELL_PROFILE], segments=32)
        bell.rotate_y(math.radians(-(90.0 - pitch_deg)))
        bell.translate(s * -16.95, s * ey, s * ez)
        fus.visual(mesh_from_geometry(bell, f"main_engine_nozzle_{i}"), material="nozzle_steel",
                   name=f"main_engine_nozzle_{i}", material_class_id="metal.stainless_matte")
        throat = CylinderGeometry(1.12 * s, 0.25 * s, radial_segments=24)
        throat.rotate_y(math.radians(-(90.0 - pitch_deg)))
        dx = -2.30 * math.cos(math.radians(pitch_deg))
        dz = 2.30 * math.sin(math.radians(pitch_deg))
        throat.translate(s * (-16.95 + dx), s * ey, s * (ez + dz))
        fus.visual(mesh_from_geometry(throat, f"main_engine_throat_{i}"),
                   material="nozzle_throat", name=f"main_engine_throat_{i}", material_class_id="metal.blackened_gunmetal")

    return ModuleBuild(
        module_name=r.hull_form,
        parts_emitted=["fuselage"],
        interfaces={"downstream": _fuselage_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot B — control_surfaces (bay doors + body flap + elevons)
# --------------------------------------------------------------------------- #


def _emit_bay_doors(model, fus, s: float) -> list[str]:
    parts = []
    for name, side in SIDES:
        door = model.part(f"{name}_payload_bay_door")
        # Arc starts exactly on the hinge line (phi=DOOR_PHI_HINGE) so the door
        # near edge contains the joint origin (origin honesty, tol 0.015).
        loop_f = _door_arc_loop(BAY_LEN / 2.0, side, DOOR_ARC_R + DOOR_THICK / 2.0,
                                DOOR_ARC_R - DOOR_THICK / 2.0,
                                DOOR_PHI_HINGE, DOOR_PHI_SEAM)
        loop_a = _door_arc_loop(-BAY_LEN / 2.0, side, DOOR_ARC_R + DOOR_THICK / 2.0,
                                DOOR_ARC_R - DOOR_THICK / 2.0,
                                DOOR_PHI_HINGE, DOOR_PHI_SEAM)
        door.visual(mesh_from_geometry(
            LoftGeometry([_scl(loop_f, s), _scl(loop_a, s)]).rotate_y(math.pi / 2.0),
            f"{name}_bay_door"), material="tps_white", name=f"{name}_door_shell", material_class_id="metal.paint_coated")
        model.articulation(
            f"fuselage_to_{name}_payload_bay_door", ArticulationType.REVOLUTE,
            parent=fus, child=door, origin=_o(s, BAY_X_MID, side * SILL_Y, SILL_Z),
            axis=(-side, 0.0, 0.0),
            motion_limits=MotionLimits(effort=400.0, velocity=0.3, lower=0.0, upper=2.0),
        )
        parts.append(door.name)
    return parts


def _emit_body_flap(model, fus, s: float) -> str:
    flap = model.part("body_flap")
    # Panel runs aft from the hinge line (leading edge on the hinge -> origin
    # honesty); up-travel is capped so the panel clears the engine bells above.
    flap.visual(_box(s, FLAP_CHORD, FLAP_WIDTH, FLAP_THICK),
                origin=_o(s, -FLAP_CHORD / 2.0, 0.0, 0.0),
                material="tps_black", name="body_flap_panel", material_class_id="ceramic.architectural_tile")
    model.articulation(
        "fuselage_to_body_flap", ArticulationType.REVOLUTE, parent=fus, child=flap,
        origin=_o(s, *FLAP_HINGE), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=300.0, velocity=0.4, lower=-0.30, upper=0.20),
    )
    return flap.name


def _emit_elevon(model, fus, s: float, r, name: str, side: float, seg: str,
                 y_in: float, y_out: float) -> str:
    """One elevon slab hinged on the wing TE (origin L553-581)."""
    suffix = f"{name}_{seg}" if seg else name
    elevon = model.part(f"{suffix}_elevon")
    mid_y = 0.5 * (y_in + y_out)
    loops = []
    for ay, root_t in ((y_in, 0.30), (y_out, 0.16)):
        y = side * ay - side * mid_y
        x0 = 0.14
        x1 = ELEVON_TE_X - ELEVON_HINGE_X
        loop = [(x0, -root_t / 2.0, y), (x1, -0.03, y), (x1, 0.03, y), (x0, root_t / 2.0, y)]
        loops.append(loop)
    if side < 0:
        loops = [lp[::-1] for lp in loops]
    elevon.visual(mesh_from_geometry(
        LoftGeometry([_scl(lp, s) for lp in loops]).rotate_x(-math.pi / 2.0),
        f"{suffix}_elevon"), material="tps_white", name=f"{suffix}_elevon_panel", material_class_id="metal.paint_coated")
    model.articulation(
        f"wing_to_{suffix}_elevon", ArticulationType.REVOLUTE, parent=fus, child=elevon,
        origin=_o(s, ELEVON_HINGE_X, side * mid_y, ELEVON_Z), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=300.0, velocity=0.7, lower=-0.6, upper=r.elevon_up),
    )
    return elevon.name


def _build_control_surfaces(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedAstronomySpaceShuttleConfig = ctx.config  # type: ignore[assignment]
    s = r.fuse_scale
    fus = model.get_part("fuselage")
    w = r.wing_span_scale

    parts = list(_emit_bay_doors(model, fus, s))
    parts.append(_emit_body_flap(model, fus, s))

    y_in, y_out = ELEVON_Y_IN * w, ELEVON_Y_OUT * w
    for name, side in SIDES:
        if r.control_module == "split_elevon":
            mid = 0.5 * (y_in + y_out)
            parts.append(_emit_elevon(model, fus, s, r, name, side, "inboard", y_in, mid))
            parts.append(_emit_elevon(model, fus, s, r, name, side, "outboard", mid, y_out))
        else:
            parts.append(_emit_elevon(model, fus, s, r, name, side, "", y_in, y_out))

    return ModuleBuild(
        module_name=r.control_module,
        parts_emitted=parts,
        interfaces={"downstream": _fuselage_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot C — tail (fin fused as fuselage visual; rudder panels articulate)
# --------------------------------------------------------------------------- #


def _emit_single_fin(model, fus, s: float, hinge_fn, stations) -> list[str]:
    fin_loops, fin_le_loops = [], []
    for (z, x_le, th) in stations:
        x_te = hinge_fn(z) - FIN_TE_AFT_OF_HINGE
        fin_loops.append(_fin_loop(z, x_le, x_te, th))
        fin_le_loops.append(_fin_loop(z, x_le - 0.04, x_le + 0.75, th * 0.82))
    fus.visual(mesh_from_geometry(LoftGeometry([_scl(lp, s) for lp in fin_loops]),
                                  "vertical_stabilizer"), material="tps_white",
               name="vertical_stabilizer", material_class_id="metal.paint_coated")
    fus.visual(mesh_from_geometry(LoftGeometry([_scl(lp, s) for lp in fin_le_loops]),
                                  "fin_leading_edge"), material="tps_charcoal",
               name="fin_leading_edge", material_class_id="fabric.carbon_weave")

    hinge_root = (hinge_fn(RUDDER_ROOT_Z), 0.0, RUDDER_ROOT_Z)
    hinge_tip = (hinge_fn(RUDDER_TIP_Z), 0.0, RUDDER_TIP_Z)
    h_len = math.hypot(hinge_tip[0] - hinge_root[0], hinge_tip[2] - hinge_root[2])
    hdir = ((hinge_tip[0] - hinge_root[0]) / h_len, 0.0, (hinge_tip[2] - hinge_root[2]) / h_len)
    parts = []
    for name, side in SIDES:
        panel = model.part(f"{name}_rudder_panel")
        loops = []
        for (z, te_x) in ((RUDDER_ROOT_Z, RUDDER_TE_ROOT_X), (RUDDER_TIP_Z, RUDDER_TE_TIP_X)):
            hx = hinge_fn(z)
            zl = z - RUDDER_ROOT_Z
            # Leading edge lies ON the hinge line (x0 = hinge x): the axis touches
            # the panel LE (origin honesty) and the fin TE runs aft of the hinge to
            # bury this LE (cove contact). Nothing sits forward of the hinge, so
            # opening outboard keeps the whole half on its own side of y=0.
            x0 = hx - hinge_root[0]
            x1 = te_x - hinge_root[0]
            loop = [(x0, 0.0, zl), (x0, side * RUDDER_PANEL_T, zl),
                    (x1, side * 0.35 * RUDDER_PANEL_T, zl), (x1, 0.0, zl)]
            if side < 0:
                loop = loop[::-1]
            loops.append(loop)
        panel.visual(mesh_from_geometry(LoftGeometry([_scl(lp, s) for lp in loops]),
                                        f"{name}_rudder_panel"), material="tps_white",
                     name=f"{name}_rudder_slab", material_class_id="metal.paint_coated")
        # Hinge about the (near-vertical) fin trailing edge. Use a pure vertical
        # axis so a tall panel does not tilt-couple across the seam; sign mirrored
        # by side so positive travel flares each half OUTBOARD. Range is
        # outboard-only (a real split-brake half opens from the closed seam).
        model.articulation(
            f"fin_to_{name}_rudder_panel", ArticulationType.REVOLUTE, parent=fus, child=panel,
            origin=_o(s, *hinge_root),
            axis=(0.0, 0.0, -side),
            motion_limits=MotionLimits(effort=200.0, velocity=0.8, lower=0.0, upper=RUDDER_OPEN),
        )
        parts.append(panel.name)
    return parts


def _build_swept_fin(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config
    fus = model.get_part("fuselage")
    parts = _emit_single_fin(model, fus, r.fuse_scale, _rudder_hinge_x_swept, FIN_STATIONS_SWEPT)
    return ModuleBuild(module_name="swept_fin", parts_emitted=parts,
                       interfaces={"downstream": _fuselage_downstream(r)})


def _build_straight_fin(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config
    fus = model.get_part("fuselage")
    parts = _emit_single_fin(model, fus, r.fuse_scale, _rudder_hinge_x_straight,
                             FIN_STATIONS_STRAIGHT)
    return ModuleBuild(module_name="straight_fin", parts_emitted=parts,
                       interfaces={"downstream": _fuselage_downstream(r)})


def _build_twin_tail(ctx: ModuleBuildContext) -> ModuleBuild:
    """Two smaller swept fins on the aft deck (fused visuals at +-Y), each with a
    rudder REVOLUTE hinged to the fuselage (fin is non-moving -> Rule 1)."""
    model = ctx.model
    r: ResolvedAstronomySpaceShuttleConfig = ctx.config  # type: ignore[assignment]
    s = r.fuse_scale
    fus = model.get_part("fuselage")
    parts = []
    for i in range(2):
        side = 1.0 if i == 0 else -1.0
        yoff = side * TWIN_FIN_Y_OFFSET
        fin_loops, fin_le_loops = [], []
        for (dz, x_le, x_te, th) in TWIN_FIN_STATIONS:
            z = TWIN_FIN_ROOT_Z + dz
            fin_loops.append([(x, yoff + wy, z) for (x, wy, _z) in _fin_loop(0.0, x_le, x_te, th)])
            fin_le_loops.append([(x, yoff + wy, z)
                                 for (x, wy, _z) in _fin_loop(0.0, x_le - 0.04, x_le + 0.65, th * 0.82)])
        fus.visual(mesh_from_geometry(LoftGeometry([_scl(lp, s) for lp in fin_loops]),
                                      f"tail_fin_{i}_body"), material="tps_white",
                   name=f"tail_fin_{i}_body", material_class_id="metal.paint_coated")
        fus.visual(mesh_from_geometry(LoftGeometry([_scl(lp, s) for lp in fin_le_loops]),
                                      f"tail_fin_{i}_le"), material="tps_charcoal",
                   name=f"tail_fin_{i}_leading_edge", material_class_id="fabric.carbon_weave")

        rudder = model.part(f"tail_fin_{i}_rudder")
        hx_root, hx_tip = TWIN_RUDDER_HINGE_X
        te_root, te_tip = TWIN_RUDDER_TE_X
        rudder_loops = []
        for dz, hx, tex in ((0.0, hx_root, te_root), (TWIN_FIN_TIP_DZ, hx_tip, te_tip)):
            lx_hx = hx - hx_root  # leading edge on the hinge line -> origin honesty
            lx_te = tex - hx_root
            ht = TWIN_RUDDER_PANEL_T / 2.0
            loop = [(lx_hx, -ht, dz), (lx_hx, ht, dz),
                    (lx_te, ht * 0.55, dz), (lx_te, -ht * 0.55, dz)]
            rudder_loops.append(loop)
        rudder.visual(mesh_from_geometry(LoftGeometry([_scl(lp, s) for lp in rudder_loops]),
                                         f"tail_fin_{i}_rudder_slab"), material="tps_white",
                      name=f"tail_fin_{i}_rudder_slab", material_class_id="metal.paint_coated")
        hdx = hx_tip - hx_root
        h_len = math.hypot(hdx, TWIN_FIN_TIP_DZ)
        model.articulation(
            f"tail_fin_{i}_to_rudder", ArticulationType.REVOLUTE, parent=fus, child=rudder,
            origin=_o(s, hx_root, side * TWIN_FIN_Y_OFFSET, TWIN_FIN_ROOT_Z),
            axis=(hdx / h_len, 0.0, TWIN_FIN_TIP_DZ / h_len),
            motion_limits=MotionLimits(effort=200.0, velocity=0.8, lower=-0.55, upper=0.55),
        )
        parts.append(rudder.name)
    return ModuleBuild(module_name="twin_tail", parts_emitted=parts,
                       interfaces={"downstream": _fuselage_downstream(r)})


# --------------------------------------------------------------------------- #
# Slot D — landing_gear (nose + main gear + doors; revolute | prismatic)
# --------------------------------------------------------------------------- #


def _build_gear(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedAstronomySpaceShuttleConfig = ctx.config  # type: ignore[assignment]
    s = r.fuse_scale
    fus = model.get_part("fuselage")
    prismatic = r.gear_module == "prismatic_gear"

    # shared wheel meshes (built once, reused across all wheels of a size)
    nose_rim, nose_tire = _wheel_geoms(s, NOSE_WHEEL_R, NOSE_WHEEL_W, 0.24)
    main_rim, main_tire = _wheel_geoms(s, MAIN_WHEEL_R, MAIN_WHEEL_W, 0.33)

    parts, joints = [], []

    def _attach_wheel(part, rim, tire):
        part.visual(rim, material="gear_silver", name="wheel_rim", material_class_id="metal.aluminum_bare")
        part.visual(tire, material="tire_rubber", name="wheel_tire", material_class_id="rubber.directional_grooved")

    def _strut_joint(name, child, x, y, top_z, axis_rev):
        if prismatic:
            # +Z travel retracts the piston up into its fixed bore, so q=0 is the
            # deployed stance for both joint types. (Pushing the leg further DOWN
            # from a wheels-on-ground rest pose would drive it under the runway.)
            # The stroke is a LENGTH, so it scales with fuse_scale exactly like
            # the geometry it slides through. Leaving it unscaled makes the
            # relative travel grow on small airframes and the retracted leg then
            # runs into structure that the nominal-scale clearances cleared.
            model.articulation(
                name, ArticulationType.PRISMATIC, parent=fus, child=child,
                origin=_o(s, x, y, top_z), axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=1500.0, velocity=0.4,
                                           lower=0.0, upper=s * r.gear_deploy),
            )
        else:
            model.articulation(
                name, ArticulationType.REVOLUTE, parent=fus, child=child,
                origin=_o(s, x, y, top_z), axis=axis_rev,
                motion_limits=MotionLimits(effort=1500.0, velocity=0.4, lower=0.0, upper=GEAR_REVOLUTE_UPPER),
            )

    # ---- nose gear: strut + steerable fork + wheels ----
    nose_strut = model.part("nose_gear_strut")
    if prismatic:
        # Telescoping leg: outer bore + drag brace are fixed structure on the
        # fuselage; the moving part is only the inner piston sliding in the bore.
        fus.visual(
            mesh_from_geometry(
                _tube(s, 0.14,
                      (NOSE_GEAR_X, 0.0, NOSE_GEAR_TOP_Z + NOSE_HOUSING_TOP_Z),
                      (NOSE_GEAR_X, 0.0, NOSE_GEAR_TOP_Z + NOSE_HOUSING_BOT_Z)),
                "nose_gear_housing"),
            material="gear_silver", name="nose_gear_housing", material_class_id="metal.brushed_silver")
        fus.visual(
            mesh_from_geometry(
                _tube(s, 0.07,
                      (NOSE_GEAR_X, 0.0, NOSE_GEAR_TOP_Z),
                      (NOSE_GEAR_X + 0.95, 0.0, NOSE_GEAR_TOP_Z + 0.30)),
                "nose_gear_drag_brace"),
            material="gear_silver", name="nose_gear_drag_brace", material_class_id="metal.brushed_silver")
        nose_strut.visual(
            mesh_from_geometry(
                _tube(s, 0.10, (0.0, 0.0, NOSE_PISTON_TOP_Z), (0.0, 0.0, NOSE_PISTON_BOT_Z)),
                "nose_strut_piston"),
            material="gear_silver", name="nose_strut_piston", material_class_id="metal.brushed_silver")
    else:
        # Retracting leg: the whole assembly swings up on its trunnion.
        nose_strut.visual(mesh_from_geometry(_tube(s, 0.14, (0.0, 0.0, 0.40), (0.0, 0.0, -1.10)),
                                             "nose_strut_tube"), material="gear_silver",
                          name="nose_strut_tube", material_class_id="metal.brushed_silver")
        nose_strut.visual(mesh_from_geometry(_tube(s, 0.10, (0.0, 0.0, -1.05), (0.0, 0.0, -NOSE_FORK_DROP - 0.15)),
                                             "nose_strut_piston"), material="gear_silver",
                          name="nose_strut_piston", material_class_id="metal.brushed_silver")
        nose_strut.visual(mesh_from_geometry(_tube(s, 0.07, (0.0, 0.0, -0.85), (0.95, 0.0, 0.30)),
                                             "nose_drag_brace"), material="gear_silver",
                          name="nose_drag_brace", material_class_id="metal.brushed_silver")
    _strut_joint("fuselage_to_nose_gear_strut", nose_strut, NOSE_GEAR_X, 0.0, NOSE_GEAR_TOP_Z,
                 (0.0, -1.0, 0.0))
    parts.append(nose_strut.name)
    joints.append("fuselage_to_nose_gear_strut")

    nose_fork = model.part("nose_gear_fork")
    nose_fork.visual(mesh_from_geometry(_tube(s, 0.115, (0.0, 0.0, 0.30), (0.0, 0.0, -NOSE_AXLE_DROP)),
                                        "nose_fork_tube"), material="gear_silver",
                     name="nose_fork_tube", material_class_id="metal.brushed_silver")
    nose_fork.visual(mesh_from_geometry(_tube(s, 0.075, (0.0, -0.42, -NOSE_AXLE_DROP), (0.0, 0.42, -NOSE_AXLE_DROP)),
                                        "nose_axle"), material="nozzle_steel", name="nose_axle", material_class_id="metal.steel_bare")
    model.articulation(
        "nose_gear_strut_to_fork", ArticulationType.REVOLUTE, parent=nose_strut, child=nose_fork,
        origin=_o(s, 0.0, 0.0, -NOSE_FORK_DROP), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=150.0, velocity=1.0, lower=-0.35, upper=0.35),
    )
    parts.append(nose_fork.name)
    joints.append("nose_gear_strut_to_fork")

    for name, side in SIDES:
        wp = model.part(f"{name}_nose_wheel")
        _attach_wheel(wp, nose_rim, nose_tire)
        model.articulation(
            f"nose_axle_to_{name}_wheel", ArticulationType.CONTINUOUS, parent=nose_fork, child=wp,
            origin=_o(s, 0.0, side * 0.27, -NOSE_AXLE_DROP, rpy=(0.0, 0.0, math.pi / 2.0)),
            axis=(1.0, 0.0, 0.0), motion_limits=MotionLimits(effort=50.0, velocity=60.0),
        )
        parts.append(wp.name)
        joints.append(f"nose_axle_to_{name}_wheel")

    # ---- main gear pair ----
    for name, side in SIDES:
        strut = model.part(f"{name}_main_gear_strut")
        gy = side * MAIN_GEAR_Y
        if prismatic:
            # Telescoping leg: outer bore + both braces are fixed structure in
            # the wing-root well; only the inner piston (and the axle it carries)
            # slides. The piston crown stays inside the bore at full retract, so
            # nothing can travel up through the wing skin.
            fus.visual(
                mesh_from_geometry(
                    _tube(s, 0.17,
                          (MAIN_GEAR_X, gy, MAIN_GEAR_TOP_Z + MAIN_HOUSING_TOP_Z),
                          (MAIN_GEAR_X, gy, MAIN_GEAR_TOP_Z + MAIN_HOUSING_BOT_Z)),
                    f"{name}_main_gear_housing"),
                material="gear_silver", name=f"{name}_main_gear_housing", material_class_id="metal.brushed_silver")
            fus.visual(
                mesh_from_geometry(
                    _tube(s, 0.08,
                          (MAIN_GEAR_X, gy, MAIN_GEAR_TOP_Z + MAIN_HOUSING_BOT_Z),
                          (MAIN_GEAR_X + 0.95, gy, MAIN_GEAR_TOP_Z + 0.30)),
                    f"{name}_main_gear_drag_brace"),
                material="gear_silver", name=f"{name}_main_gear_drag_brace", material_class_id="metal.brushed_silver")
            fus.visual(
                mesh_from_geometry(
                    _tube(s, 0.08,
                          (MAIN_GEAR_X, gy, MAIN_GEAR_TOP_Z + MAIN_HOUSING_BOT_Z),
                          (MAIN_GEAR_X, gy - side * 0.95, MAIN_GEAR_TOP_Z + 0.30)),
                    f"{name}_main_gear_side_brace"),
                material="gear_silver", name=f"{name}_main_gear_side_brace", material_class_id="metal.brushed_silver")
            strut.visual(
                mesh_from_geometry(
                    _tube(s, 0.12, (0.0, 0.0, MAIN_PISTON_TOP_Z),
                          (0.0, 0.0, -MAIN_AXLE_DROP - 0.05)),
                    f"{name}_main_strut_piston"),
                material="gear_silver", name=f"{name}_main_strut_piston", material_class_id="metal.brushed_silver")
        else:
            # Retracting leg: the whole assembly swings up on its trunnion.
            strut.visual(mesh_from_geometry(_tube(s, 0.17, (0.0, 0.0, 0.40), (0.0, 0.0, -1.85)),
                                            f"{name}_main_strut_tube"), material="gear_silver",
                         name=f"{name}_main_strut_tube", material_class_id="metal.brushed_silver")
            strut.visual(mesh_from_geometry(_tube(s, 0.12, (0.0, 0.0, -1.80), (0.0, 0.0, -MAIN_AXLE_DROP - 0.05)),
                                            f"{name}_main_strut_piston"), material="gear_silver",
                         name=f"{name}_main_strut_piston", material_class_id="metal.brushed_silver")
            strut.visual(mesh_from_geometry(_tube(s, 0.08, (0.0, 0.0, -1.15), (0.95, 0.0, 0.30)),
                                            f"{name}_main_drag_brace"), material="gear_silver",
                         name=f"{name}_main_drag_brace", material_class_id="metal.brushed_silver")
            strut.visual(mesh_from_geometry(_tube(s, 0.08, (0.0, 0.0, -1.15), (0.0, -side * 0.95, 0.30)),
                                            f"{name}_main_side_brace"), material="gear_silver",
                         name=f"{name}_main_side_brace", material_class_id="metal.brushed_silver")
        strut.visual(mesh_from_geometry(_tube(s, 0.095, (0.0, -0.50, -MAIN_AXLE_DROP), (0.0, 0.50, -MAIN_AXLE_DROP)),
                                        f"{name}_main_axle"), material="nozzle_steel",
                     name=f"{name}_main_axle", material_class_id="metal.steel_bare")
        _strut_joint(f"fuselage_to_{name}_main_gear_strut", strut, MAIN_GEAR_X, gy,
                     MAIN_GEAR_TOP_Z, (0.0, -1.0, 0.0))
        parts.append(strut.name)
        joints.append(f"fuselage_to_{name}_main_gear_strut")

        if r.main_wheel_count == 1:
            wheels = (("", 0.0),)
        else:
            wheels = (("outboard", side * 0.33), ("inboard", -side * 0.33))
        for wname, woff in wheels:
            wpname = f"{name}_main_wheel" if not wname else f"{name}_{wname}_main_wheel"
            wp = model.part(wpname)
            _attach_wheel(wp, main_rim, main_tire)
            jn = f"{name}_main_axle_to_wheel" if not wname else f"{name}_main_axle_to_{wname}_wheel"
            model.articulation(
                jn, ArticulationType.CONTINUOUS, parent=strut, child=wp,
                origin=_o(s, 0.0, woff, -MAIN_AXLE_DROP, rpy=(0.0, 0.0, math.pi / 2.0)),
                axis=(1.0, 0.0, 0.0), motion_limits=MotionLimits(effort=200.0, velocity=60.0),
            )
            parts.append(wp.name)
            joints.append(jn)

    # ---- nose gear doors: open at rest (q=0), closable ----
    # (main gear doors were dropped: hanging fully open at q=0 they read as a
    # loose flat panel beside the strut rather than a door, and the source
    # pool's main-gear-well doors are not load-bearing to any other geometry.)
    for name, side in SIDES:
        door = model.part(f"{name}_nose_gear_door")
        # Sized so each half, swung flat, reaches only to the centreline (hinge at
        # |y|=0.62): the two nose doors meet at the seam instead of overshooting it.
        door.visual(_box(s, 1.9, 0.07, 0.70), origin=_o(s, 0.0, 0.0, -0.26),
                    material="tps_black", name=f"{name}_nose_door_panel", material_class_id="ceramic.architectural_tile")
        model.articulation(
            f"fuselage_to_{name}_nose_gear_door", ArticulationType.REVOLUTE, parent=fus, child=door,
            origin=_o(s, NOSE_GEAR_X, side * 0.62, 3.42), axis=(-side, 0.0, 0.0),
            motion_limits=MotionLimits(effort=80.0, velocity=0.8, lower=0.0, upper=1.5),
        )
        parts.append(door.name)
        joints.append(f"fuselage_to_{name}_nose_gear_door")

    return ModuleBuild(module_name=r.gear_module, parts_emitted=parts,
                       internal_articulations=joints,
                       interfaces={"downstream": _fuselage_downstream(r)})


# --------------------------------------------------------------------------- #
# Registries + assembly
# --------------------------------------------------------------------------- #

CONTROL_FACTORIES = {
    "single_elevon": _build_control_surfaces,
    "split_elevon": _build_control_surfaces,
}
TAIL_FACTORIES = {
    "swept_fin": _build_swept_fin,
    "straight_fin": _build_straight_fin,
    "twin_tail": _build_twin_tail,
}
GEAR_FACTORIES = {
    "revolute_gear": _build_gear,
    "prismatic_gear": _build_gear,
}


def _slots_for_config(r: ResolvedAstronomySpaceShuttleConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="airframe", candidates={r.hull_form: _build_airframe},
                 anchor_choice=r.hull_form),
        SlotSpec(slot_name="control_surfaces",
                 candidates={r.control_module: CONTROL_FACTORIES[r.control_module]},
                 anchor_choice=r.control_module),
        SlotSpec(slot_name="tail", candidates={r.tail_module: TAIL_FACTORIES[r.tail_module]},
                 anchor_choice=r.tail_module),
        SlotSpec(slot_name="landing_gear",
                 candidates={r.gear_module: GEAR_FACTORIES[r.gear_module]},
                 anchor_choice=r.gear_module),
    ]


def build_astronomy_space_shuttle(
    config: AstronomySpaceShuttleConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="astronomy_space_shuttle", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    assemble(
        model,
        slots=_slots_for_config(r),
        rng=random.Random(0),
        palette=r.palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    return model


def build_seeded_astronomy_space_shuttle(seed: int) -> ArticulatedObject:
    return build_astronomy_space_shuttle(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("hull_form", r.hull_form),
        ("wing_form", r.wing_form),
        ("payload_bay_layout", r.payload_bay_layout),
        ("control_surfaces", r.control_module),
        ("tail", r.tail_module),
        ("landing_gear", r.gear_module),
        ("engine_count", f"engines_{r.engine_count}"),
        ("main_wheel_count", f"mainwheels_{r.main_wheel_count}"),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject,
                      r: ResolvedAstronomySpaceShuttleConfig) -> None:
    parts = {p.name for p in model.parts}

    def _ov(parent, child, *, reason, elem_a=None, elem_b=None):
        if child in parts and parent in parts:
            if elem_a is not None:
                ctx.allow_overlap(parent, child, elem_a=elem_a, elem_b=elem_b, reason=reason)
            else:
                ctx.allow_overlap(parent, child, reason=reason)

    hull_skins = ("hull", "belly_tiles", "nose_cap", "chine_band")

    for name, _side in SIDES:
        # bay door hinge lip tucks into the sill / hull
        for elem in (f"{name}_bay_sill", "hull"):
            _ov("fuselage", f"{name}_payload_bay_door", elem_a=elem, elem_b=f"{name}_door_shell",
                reason="Closed bay door tucks its hinge lip into the sill rail.")
        # single-fin split rudder seated in the fin cove
        _ov("fuselage", f"{name}_rudder_panel", elem_a="vertical_stabilizer",
            elem_b=f"{name}_rudder_slab",
            reason="Rudder/speed-brake panel leading edge seated inside the fin trailing-edge cove.")
        # elevons seated in the wing cove (single or split)
        for seg in ("", "inboard", "outboard"):
            suffix = f"{name}_{seg}" if seg else name
            for elem in (f"{name}_wing", f"{name}_wing_underside", "belly_tiles", "hull"):
                _ov("fuselage", f"{suffix}_elevon", elem_a=elem, elem_b=f"{suffix}_elevon_panel",
                    reason="Elevon root seated inside the wing/hull-blend trailing-edge cove.")
        # gear struts + doors + captured wheel axles (mesh component names unstable
        # after auto-split, so part-scoped, proven by stance/retraction pose checks)
        _ov("fuselage", f"{name}_main_gear_strut",
            reason="Main gear strut assembly anchors up inside the wing-root gear well.")
        nose_door_elems = ["hull", "belly_tiles"]
        if r.gear_module == "prismatic_gear":
            # The telescoping bore and its brace are fixed fuselage structure
            # standing in the well mouth, so the door sweeps across them for the
            # same coupled-mechanism reason it sweeps across the stowed leg.
            nose_door_elems += ["nose_gear_housing", "nose_gear_drag_brace"]
        for elem in nose_door_elems:
            _ov("fuselage", f"{name}_nose_gear_door", elem_a=elem, elem_b=f"{name}_nose_door_panel",
                reason="Open nose gear door keeps its hinge edge embedded in the well sill; "
                       "closing it over the well is only physical once the leg is stowed.")
        # Nose gear door and its strut/fork share one wheel well: the door only
        # closes once the strut is stowed (coupled mechanism), so an
        # independently-sampled "door closed while gear down" pose
        # interpenetrates them non-physically.
        _ov(f"{name}_nose_gear_door", "nose_gear_strut",
            reason="Nose gear door closes over the well only when the strut is stowed (coupled mechanism).")
        _ov(f"{name}_nose_gear_door", "nose_gear_fork",
            reason="Nose gear door closes over the well only when the fork is stowed (coupled mechanism).")
        _ov("nose_gear_fork", f"{name}_nose_wheel",
            reason="Nose wheel hub captures the through-axle (captured-pin fit).")
        for wname in ("", "outboard", "inboard"):
            wp = f"{name}_main_wheel" if not wname else f"{name}_{wname}_main_wheel"
            _ov(f"{name}_main_gear_strut", wp,
                reason="Main wheel hub captures the through-axle (captured-pin fit).")
        for nwname, _ns in SIDES:
            _ov(f"{name}_nose_gear_door", f"{nwname}_nose_wheel",
                reason="Nose gear door closes over the well only when the wheels are stowed (coupled mechanism).")

    # twin-tail rudders seated in their fin cove
    for i in range(2):
        _ov("fuselage", f"tail_fin_{i}_rudder", elem_a=f"tail_fin_{i}_body",
            elem_b=f"tail_fin_{i}_rudder_slab",
            reason="Twin-fin rudder leading edge seated inside its fin trailing-edge cove.")

    # body flap seated in the aft fuselage cove
    for elem in ("hull", "belly_tiles", "base_heat_shield"):
        _ov("fuselage", "body_flap", elem_a=elem, elem_b="body_flap_panel",
            reason="Body flap forward edge seated inside the aft fuselage hinge cove.")
    _ov("fuselage", "nose_gear_strut",
        reason="Nose gear strut and drag brace anchor up inside the nose wheel well.")
    _ov("nose_gear_strut", "nose_gear_fork",
        reason="Steering fork collar captures the oleo piston (captured-pin fit).")
    if "left_rudder_panel" in parts and "right_rudder_panel" in parts:
        ctx.allow_coplanar_surfaces("left_rudder_panel", "right_rudder_panel",
                                    reason="The two speed-brake halves lie face to face when closed.")


def _aabb_span(a, i):
    return None if a is None else a[1][i] - a[0][i]


def _center(a):
    return None if a is None else [(a[0][k] + a[1][k]) / 2.0 for k in range(3)]


def _run_targeted(ctx: TestContext, model: ArticulatedObject,
                  r: ResolvedAstronomySpaceShuttleConfig) -> None:
    def g(n):
        return model.get_articulation(n)

    def p(n):
        return model.get_part(n)

    # bay door swings up + outboard
    ld = p("left_payload_bay_door")
    rest = ctx.part_world_aabb(ld)
    with ctx.pose({g("fuselage_to_left_payload_bay_door"): 1.2}):
        opened = ctx.part_world_aabb(ld)
    ctx.check("bay door swings up and outboard",
              rest is not None and opened is not None
              and opened[1][2] > rest[1][2] + 0.5 and opened[1][1] > rest[1][1] + 0.3,
              details=f"rest={rest}, open={opened}")

    # body flap trails up
    flap = p("body_flap")
    rest = ctx.part_world_aabb(flap)
    with ctx.pose({g("fuselage_to_body_flap"): 0.20}):
        up = ctx.part_world_aabb(flap)
    ctx.check("body flap trails up", rest is not None and up is not None
              and up[1][2] > rest[1][2] + 0.1, details=f"rest={rest}, up={up}")

    # an elevon deflects up
    ename = "left_elevon" if r.control_module == "single_elevon" else "left_inboard_elevon"
    jname = "wing_to_left_elevon" if r.control_module == "single_elevon" else "wing_to_left_inboard_elevon"
    el = p(ename)
    rest = ctx.part_world_aabb(el)
    with ctx.pose({g(jname): r.elevon_up}):
        upe = ctx.part_world_aabb(el)
    ctx.check("elevon trailing edge deflects up", rest is not None and upe is not None
              and upe[1][2] > rest[1][2] + 0.15, details=f"rest={rest}, up={upe}")

    # rudder deflects
    if r.tail_module == "twin_tail":
        rud, rj = "tail_fin_0_rudder", "tail_fin_0_to_rudder"
    else:
        rud, rj = "left_rudder_panel", "fin_to_left_rudder_panel"
    rud_q = 0.5 if r.tail_module == "twin_tail" else RUDDER_OPEN
    rr = p(rud)
    c0 = _center(ctx.part_world_aabb(rr))
    with ctx.pose({g(rj): rud_q}):
        c1 = _center(ctx.part_world_aabb(rr))
    ctx.check("rudder panel deflects", c0 is not None and c1 is not None
              and math.dist(c0, c1) > 0.05, details=f"{c0}->{c1}")

    # main gear strut moves the wheel: both types are gear-DOWN at q=0 and
    # retract on positive travel — revolute swings the whole leg up on its
    # trunnion, prismatic telescopes the piston up into its fixed bore.
    strut_j = g("fuselage_to_left_main_gear_strut")
    wp = "left_main_wheel" if r.main_wheel_count == 1 else "left_outboard_main_wheel"
    lw = p(wp)
    rest = ctx.part_world_aabb(lw)
    if r.gear_module == "prismatic_gear":
        full_retract = r.fuse_scale * r.gear_deploy
        with ctx.pose({strut_j: full_retract}):
            moved = ctx.part_world_aabb(lw)
        ctx.check("main gear telescopes the wheel up into the bore",
                  rest is not None and moved is not None and moved[0][2] > rest[0][2] + 0.3,
                  details=f"rest={rest}, retracted={moved}")
        # The retracted piston must stay swallowed by its fixed housing, and the
        # wheel must stop short of the wing underside: this is the check that
        # would have caught the old upper-slide rod spearing through the skin.
        strut_rest = ctx.part_world_aabb(p("left_main_gear_strut"))
        with ctx.pose({strut_j: full_retract}):
            strut_up = ctx.part_world_aabb(p("left_main_gear_strut"))
        bore_top = r.fuse_scale * (MAIN_GEAR_TOP_Z + MAIN_HOUSING_TOP_Z)
        ctx.check("retracted telescoping leg stays inside its bore",
                  strut_rest is not None and strut_up is not None
                  and strut_up[1][2] <= bore_top + 1e-6,
                  details=f"strut_top={strut_up[1][2] if strut_up else None}, bore_top={bore_top}")
        ctx.check("retracted main wheel stays below the wing underside",
                  moved is not None and moved[1][2] < 3.0 * r.fuse_scale,
                  details=f"retracted={moved}")
    else:
        with ctx.pose({strut_j: GEAR_REVOLUTE_UPPER}):
            moved = ctx.part_world_aabb(lw)
        ctx.check("main gear retracts the wheel upward",
                  rest is not None and moved is not None and moved[0][2] > rest[0][2] + 0.3,
                  details=f"rest={rest}, retracted={moved}")

    # nose wheels steer about the strut axis
    lnw, rnw = p("left_nose_wheel"), p("right_nose_wheel")
    l0 = ctx.part_world_position(lnw)
    r0 = ctx.part_world_position(rnw)
    with ctx.pose({g("nose_gear_strut_to_fork"): 0.3}):
        l1 = ctx.part_world_position(lnw)
        r1 = ctx.part_world_position(rnw)
    ctx.check("nose wheels steer about the strut axis",
              None not in (l0, r0, l1, r1)
              and (l1[0] - l0[0]) < -0.02 and (r1[0] - r0[0]) > 0.02,
              details=f"left {l0}->{l1}, right {r0}->{r1}")


def run_astronomy_space_shuttle_tests(
    model: ArticulatedObject,
    config: AstronomySpaceShuttleConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    _declare_overlaps(ctx, model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    # identity + proportions
    fus = model.get_part("fuselage")
    aabb = ctx.part_world_aabb(fus)
    sc = r.fuse_scale
    ctx.check("orbiter is real scale", _aabb_span(aabb, 0) is not None
              and _aabb_span(aabb, 0) > 30.0 * sc, details=f"aabb={aabb}")
    ctx.check("delta wing span", _aabb_span(aabb, 1) is not None
              and _aabb_span(aabb, 1) > 20.0 * sc, details=f"aabb={aabb}")
    # twin-tail fins top out ~12.5 m (single centreline fin ~16 m); 11.5*sc admits
    # both families as legitimate tall vertical tails.
    ctx.check("tail reaches height", aabb is not None and aabb[1][2] > 11.5 * sc,
              details=f"aabb={aabb}")
    belly = ctx.part_element_world_aabb(fus, elem="belly_tiles")
    ctx.check("black TPS wraps the underside", belly is not None and belly[0][2] < 3.4 * sc,
              details=f"belly={belly}")
    payload_elements = {
        "standard_bay": ("payload_standard_keel",),
        "satellite_deployer": (
            "payload_satellite_truss",
            "payload_satellite_forward_adapter",
            "payload_satellite_aft_adapter",
        ),
        "laboratory_module": (
            "payload_laboratory_module",
            "payload_laboratory_port_rack",
            "payload_laboratory_starboard_rack",
        ),
    }[r.payload_bay_layout]
    payload_aabbs = [
        ctx.part_element_world_aabb(fus, elem=name) for name in payload_elements
    ]
    ctx.check(
        "payload bay layout emits its structural interface",
        all(aabb is not None for aabb in payload_aabbs),
        details=f"layout={r.payload_bay_layout}, elements={payload_elements}, aabbs={payload_aabbs}",
    )
    bells = [p for p in [ctx.part_element_world_aabb(fus, elem=f"main_engine_nozzle_{i}")
                         for i in range(r.engine_count)] if p is not None]
    ctx.check("engine bells protrude aft", len(bells) == r.engine_count
              and all(b[0][0] < -17.5 * sc for b in bells), details=f"n_bells={len(bells)}")

    _run_targeted(ctx, model, r)

    # Rule 5: dynamic collision across sampled joint poses (6+ joints -> cap 32).
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "AstronomySpaceShuttleConfig",
    "ResolvedAstronomySpaceShuttleConfig",
    "HullForm",
    "WingForm",
    "PayloadBayLayout",
    "ControlModule",
    "TailModule",
    "GearModule",
    "ShuttlePalette",
    "build_astronomy_space_shuttle",
    "build_seeded_astronomy_space_shuttle",
    "config_from_seed",
    "resolve_config",
    "run_astronomy_space_shuttle_tests",
    "slot_choices_for_seed",
]
