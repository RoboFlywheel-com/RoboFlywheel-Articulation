# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for public drinking fountains / refill stations.

Derived from 7 five-star sources (1 parent + 6 converged variants):
  - parent  rec_build-...-dric_..._b6678542   : pedestal_body + rect basin + gooseneck + single push button
  - wall_mounted_body                         : mounting_plate root + compact body shell
  - round_basin                               : round bowl (cylinder shell + rim ring)
  - bubbler_spout                             : up-spraying bubbler (variable-radius tapered tube)
  - bottle_filler                             : extra tall bottle-filler gooseneck arch part
  - foot_pedal                                : REVOLUTE chrome treadle hinged on a pylon boss
  - dual_push_buttons                         : N side-by-side push buttons, independent PRISMATIC
  - rotary_knob                               : N turnable control knobs, independent REVOLUTE (about +Y)

Slot graph (parallel children — basin/faceplate/actuator all parent to the body):
  [A body]  pedestal_body (pylon root)  |  wall_mounted_body (plate root -> body shell)
  [B basin] parent_basin_spout | round_basin | bubbler_spout | bottle_filler
  [C actuator] single_push_button | dual_push_buttons | rotary_knob (control_count mult.) | foot_pedal

EVERY actuated/operable part carries a REAL joint (spec: no operable control is FIXED):
  - push button(s)     : PRISMATIC plunger, axis (0,-1,0), short BTN_TRAVEL inward (-Y).
  - rotary knob(s)     : REVOLUTE control, axis (0,1,0), turned RKNOB_SPIN about its own axis.
  - foot pedal         : REVOLUTE treadle, axis (-1,0,0), pressed down by PEDAL_PRESS.
  - water_spout        : REVOLUTE swivel of the gooseneck/bubbler/filler pipe about the
                         vertical riser (axis (0,0,1)) so the outlet swings side-to-side.
  - valve_fitting      : REVOLUTE secondary flow knob (axis (0,1,0)) — present on every unit,
                         never decorative/FIXED; carries an off-axis pointer so the turn shows.

Compatibility gate (spec §9):
  - foot_pedal => pedestal_body  (the pedal pivot boss only exists on the pylon front;
    the wall body has no ground-level pivot, so foot_pedal forces a pedestal body).

Coordinate convention (inherited from all 7 sources): +Z up, user faces +Y (front),
fountain stands on the ground at z=0 (pedestal) or hangs on a wall at y=0 (wall).

Geometry primitives are preserved from the sources (CadQuery lofts/solids for the
curved pylon/basins, mesh tube sweeps for the goosenecks/bubblers) — NOT downgraded
to Box/Cylinder placeholders (AUTHORING.md §A Rule 3).
"""

from __future__ import annotations

import copy
import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MatingContract,
    MeshGeometry,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot enums + palette
# --------------------------------------------------------------------------- #
BodyModule = Literal["pedestal_body", "wall_mounted_body"]
BasinModule = Literal["parent_basin_spout", "round_basin", "bubbler_spout", "bottle_filler"]
ActuatorModule = Literal[
    "single_push_button",
    "dual_push_buttons",
    "rotary_knob",
    "foot_pedal",
]
LayoutModule = Literal["single_unit", "linear_bank", "radial_ring"]
# Radial-ring centerpiece options (the "hero" in the middle of the ring).
CenterModule = Literal["tiered_column", "sun_umbrella"]
PaletteStyle = Literal[
    "teal_steel",
    "stainless_minimal",
    "slate_grey",
    "bronze_park",
    "hospital_white",
]

BODY_MODULES: tuple[BodyModule, ...] = ("pedestal_body", "wall_mounted_body")
BASIN_MODULES: tuple[BasinModule, ...] = (
    "parent_basin_spout",
    "round_basin",
    "bubbler_spout",
    "bottle_filler",
)
ACTUATOR_MODULES: tuple[ActuatorModule, ...] = (
    "single_push_button",
    "dual_push_buttons",
    "rotary_knob",
    "foot_pedal",
)
LAYOUT_MODULES: tuple[LayoutModule, ...] = ("single_unit", "linear_bank", "radial_ring")
CENTER_MODULES: tuple[CenterModule, ...] = ("tiered_column", "sun_umbrella")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "teal_steel",
    "stainless_minimal",
    "slate_grey",
    "bronze_park",
    "hospital_white",
)

BTN_COUNT_MIN = 1
BTN_COUNT_MAX = 2
BTN_COUNT_WEIGHTS = (0.6, 0.4)  # N=1 high freq, N=2 common (spec §8 test domain)

UNIT_COUNT_MIN_LINEAR = 2
UNIT_COUNT_MAX_LINEAR = 6
UNIT_COUNT_MIN_RADIAL = 3
UNIT_COUNT_MAX_RADIAL = 8
UNIT_SPACING_MIN = 0.38
UNIT_SPACING_MAX = 0.62
RADIAL_RADIUS_MIN = 0.42
RADIAL_RADIUS_MAX = 0.85

# Radial-ring centerpiece (two module types): a tiered bubbling-fountain column
# or a shade umbrella, both topped with a kinetic spinning finial.
COL_R = 0.055  # column shaft radius
COL_POST_H = 0.030  # short mounting post on top the finial spins on
# Tiered fountain dish radii (fraction of height) — larger/grander than before.
COL_TIERS = ((0.20, 0.300), (0.42, 0.235), (0.62, 0.175), (0.80, 0.120))
FINIAL_REACH = 0.105  # spinner blade tip radius
FINIAL_SPIN = math.pi  # finial spins freely (+/- pi)

# Sun-umbrella centerpiece: a tall mast + wide canopy that shades the ring.
UMBRELLA_MAST_R = 0.050
UMBRELLA_RIB_COUNT = 10
UMBRELLA_OVERHANG = 0.34  # canopy radius = ring_radius + this (covers the stations)
UMBRELLA_CLEARANCE = 0.34  # canopy rim sits this far above the tallest station part
UMBRELLA_RISE = 0.30  # dome rise from rim to apex
UMBRELLA_VALANCE = 0.055  # hanging skirt depth at the rim

# Material token names used by every .visual(material=...) call. Resolved to rgba
# per palette_style so the sweep pool is colorfully diverse (required by rules).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "teal_steel": {
        "body": (0.06, 0.45, 0.62, 1.0),
        "basin": (0.74, 0.76, 0.78, 1.0),
        "chrome": (0.86, 0.88, 0.90, 1.0),
        "engraving": (0.20, 0.22, 0.24, 1.0),
    },
    "stainless_minimal": {
        "body": (0.74, 0.76, 0.78, 1.0),
        "basin": (0.70, 0.72, 0.74, 1.0),
        "chrome": (0.86, 0.88, 0.90, 1.0),
        "engraving": (0.20, 0.22, 0.24, 1.0),
    },
    "slate_grey": {
        "body": (0.32, 0.34, 0.36, 1.0),
        "basin": (0.74, 0.76, 0.78, 1.0),
        "chrome": (0.86, 0.88, 0.90, 1.0),
        "engraving": (0.20, 0.22, 0.24, 1.0),
    },
    "bronze_park": {
        "body": (0.36, 0.26, 0.16, 1.0),
        "basin": (0.74, 0.76, 0.78, 1.0),
        "chrome": (0.45, 0.34, 0.22, 1.0),
        "engraving": (0.20, 0.16, 0.12, 1.0),
    },
    "hospital_white": {
        "body": (0.90, 0.91, 0.92, 1.0),
        "basin": (0.74, 0.76, 0.78, 1.0),
        "chrome": (0.86, 0.88, 0.90, 1.0),
        "engraving": (0.45, 0.47, 0.50, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Master dimensions (meters) — inherited from the sources; scaled at resolve.
# --------------------------------------------------------------------------- #
# Pedestal pylon (curved teal standard).
PYLON_H = 1.020
PYLON_X = 0.150
WALL_T = 0.006
BASE_FRONT_Y = 0.060
BASE_BACK_Y = -0.030
TOP_FRONT_Y = 0.085
TOP_BACK_Y = -0.005

# Wall mounting plate + compact body shell.
PLATE_X = 0.360
PLATE_H = 0.440
PLATE_T = 0.006
PLATE_Z_CENTER = 0.900
PLATE_HOLE_R = 0.005
PLATE_HOLE_DX = 0.150
PLATE_HOLE_DZ = 0.190
BODY_X = 0.280
BODY_Y = 0.170
BODY_H = 0.320
BODY_FILLET = 0.012
BODY_BOT_Z = PLATE_Z_CENTER - PLATE_H / 2.0 + 0.050

# Rectangular catch basin.
BASIN_X = 0.180
BASIN_Y = 0.150
BASIN_H = 0.075
BASIN_WALL = 0.006
BASIN_CY = 0.085  # forward overhang of basin center on the pedestal

# Round basin bowl.
ROUND_BASIN_R = 0.090
ROUND_BASIN_H = 0.075
ROUND_BASIN_RIM_R = 0.096

# Gooseneck drinking spout.
SPOUT_R = 0.008
SPOUT_RISE = 0.085

# Bottle-filler arch.
FILLER_R = 0.010
FILLER_RISE = 0.260
FILLER_REACH = 0.70

# Faceplate (brushed-steel strip with engraved bottle pictogram).
FACE_X = 0.120
FACE_H = 0.430
FACE_T = 0.010

# Push button.
BTN_R = 0.013
BTN_LEN = 0.022
BTN_BOSS_R = 0.018
BTN_BOSS_LEN = 0.014
BTN_TRAVEL = 0.008
BTN_SPACING = 0.052  # >= 2*BTN_BOSS_R + clearance so adjacent bosses never merge

# Rotary control knob (primary "rotary_knob" actuator). REVOLUTE about +Y; an
# off-axis pointer rib breaks axisymmetry so the turn is visible to the AABB
# spin check (memory: axisymmetric knobs are spin-invariant).
RKNOB_R = 0.017
RKNOB_LEN = 0.018
RKNOB_BOSS_R = 0.021
RKNOB_BOSS_LEN = 0.010
RKNOB_POINTER_W = 0.005
RKNOB_SPACING = 0.058  # >= 2*RKNOB_BOSS_R + clearance
RKNOB_SPIN = 1.20  # +/- turn range (rad), ~70 deg each way

# Secondary valve fitting (chrome control knob next to the primary actuator).
# Now a REAL REVOLUTE flow knob (never FIXED), with a pointer so the turn shows.
KNOB_R = 0.011
KNOB_LEN = 0.020
KNOB_DX = 0.040
KNOB_SPIN = 1.20  # +/- turn range (rad)
KNOB_Z_DROP = 0.075  # how far below the primary row the fitting sits (clear of it)

# Water-spout swivel (gooseneck / bubbler / filler all swivel about the riser).
SPOUT_SWIVEL = 1.20  # +/- swivel range (rad)
SPOUT_HUB_EXTRA = 0.006  # mounting-hub radius added around the riser tube

# Bottle-rest grille shelf (perforated D-tray).
GRILLE_R = 0.060
GRILLE_T = 0.010
GRILLE_HOLE_R = 0.006
GRILLE_PITCH = 0.018

# Foot pedal.
PEDAL_X = 0.100
PEDAL_Y = 0.075
PEDAL_T = 0.008
PEDAL_PIVOT_R = 0.007
PEDAL_PIVOT_Z = 0.042
PEDAL_PRESS = 0.30


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class DrinkingFountainConfig:
    layout_mode: LayoutModule = "single_unit"
    unit_count: int = 1
    body_module: BodyModule = "pedestal_body"
    basin_module: BasinModule = "parent_basin_spout"
    actuator_module: ActuatorModule = "single_push_button"
    button_count: int = 1
    center_feature: CenterModule = "tiered_column"
    palette_style: PaletteStyle = "teal_steel"

    unit_spacing: float = 0.48
    ring_radius: float = 0.58
    pylon_height_scale: float = 1.0
    body_width_scale: float = 1.0
    basin_size_scale: float = 1.0
    btn_spacing_scale: float = 1.0
    btn_travel: float = BTN_TRAVEL
    pedal_press: float = PEDAL_PRESS
    name: str = "drinking_fountain"


@dataclass(frozen=True)
class ResolvedDrinkingFountainConfig:
    layout_mode: LayoutModule
    unit_count: int
    body_module: BodyModule
    basin_module: BasinModule
    actuator_module: ActuatorModule
    button_count: int
    center_feature: CenterModule
    palette_style: PaletteStyle
    mats: dict[str, tuple[float, float, float, float]]

    pylon_h: float
    unit_spacing: float
    ring_radius: float
    body_width_scale: float
    basin_scale: float
    btn_spacing: float
    knob_spacing: float
    btn_travel: float
    pedal_press: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


# --------------------------------------------------------------------------- #
# Seed sampling + resolution
# --------------------------------------------------------------------------- #
def config_from_seed(seed: int) -> DrinkingFountainConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)

    layout: LayoutModule = rng.choices(
        LAYOUT_MODULES,
        weights=(0.55, 0.30, 0.15),
        k=1,
    )[0]
    actuator: ActuatorModule = rng.choice(ACTUATOR_MODULES)
    # foot_pedal pivots on a pylon-front boss the wall body lacks -> pedestal.
    # The radial station domain keeps outward clearance simple by using buttons.
    if layout == "radial_ring":
        body: BodyModule = "pedestal_body"
        if actuator == "foot_pedal":
            actuator = rng.choice(("single_push_button", "dual_push_buttons", "rotary_knob"))
    elif actuator == "foot_pedal":
        body: BodyModule = "pedestal_body"
    else:
        body = rng.choice(BODY_MODULES)

    basin: BasinModule = rng.choice(BASIN_MODULES)

    if actuator == "single_push_button":
        button_count = 1
    elif actuator == "dual_push_buttons":
        button_count = 2
    elif actuator == "rotary_knob":
        button_count = rng.choices((1, 2), weights=(0.55, 0.45), k=1)[0]
    else:  # foot_pedal exposes no button count
        button_count = rng.choices(
            (1, 2), weights=BTN_COUNT_WEIGHTS, k=1
        )[0]

    if layout == "single_unit":
        unit_count = 1
    elif layout == "linear_bank":
        unit_count = rng.choices((2, 3, 4, 5, 6), weights=(0.35, 0.28, 0.20, 0.10, 0.07), k=1)[0]
    else:
        unit_count = rng.choices((3, 4, 5, 6, 7, 8), weights=(0.30, 0.26, 0.10, 0.22, 0.05, 0.07), k=1)[0]

    center_feature: CenterModule = rng.choices(
        CENTER_MODULES, weights=(0.55, 0.45), k=1
    )[0]

    return DrinkingFountainConfig(
        layout_mode=layout,
        unit_count=unit_count,
        body_module=body,
        basin_module=basin,
        actuator_module=actuator,
        button_count=button_count,
        center_feature=center_feature,
        palette_style=rng.choice(PALETTE_STYLES),
        unit_spacing=round(rng.uniform(UNIT_SPACING_MIN, UNIT_SPACING_MAX), 4),
        ring_radius=round(rng.uniform(RADIAL_RADIUS_MIN, RADIAL_RADIUS_MAX), 4),
        pylon_height_scale=round(rng.uniform(0.95, 1.06), 4),
        body_width_scale=round(rng.uniform(0.92, 1.10), 4),
        basin_size_scale=round(rng.uniform(0.90, 1.12), 4),
        btn_spacing_scale=round(rng.uniform(0.90, 1.10), 4),
        btn_travel=round(rng.uniform(0.006, 0.010), 4),
        pedal_press=round(rng.uniform(0.22, 0.34), 4),
        name=f"drinking_fountain_{seed}",
    )


def _resolve_choices(
    cfg: DrinkingFountainConfig,
) -> tuple[LayoutModule, int, BodyModule, BasinModule, ActuatorModule, int]:
    layout = cfg.layout_mode if cfg.layout_mode in LAYOUT_MODULES else "single_unit"
    body = cfg.body_module if cfg.body_module in BODY_MODULES else "pedestal_body"
    basin = cfg.basin_module if cfg.basin_module in BASIN_MODULES else "parent_basin_spout"
    actuator = (
        cfg.actuator_module
        if cfg.actuator_module in ACTUATOR_MODULES
        else "single_push_button"
    )
    if layout == "single_unit":
        unit_count = 1
    elif layout == "linear_bank":
        unit_count = max(UNIT_COUNT_MIN_LINEAR, min(int(cfg.unit_count), UNIT_COUNT_MAX_LINEAR))
    else:
        unit_count = max(UNIT_COUNT_MIN_RADIAL, min(int(cfg.unit_count), UNIT_COUNT_MAX_RADIAL))

    # Compatibility gates: foot_pedal forces pedestal; radial stations are
    # pedestal-only and use push buttons for clear outward approach space.
    if layout == "radial_ring":
        body = "pedestal_body"
        if actuator == "foot_pedal":
            actuator = "single_push_button"
    elif actuator == "foot_pedal":
        body = "pedestal_body"

    if actuator == "single_push_button":
        button_count = 1
    elif actuator == "dual_push_buttons":
        button_count = max(2, min(int(cfg.button_count), BTN_COUNT_MAX))
    else:  # rotary_knob / foot_pedal
        button_count = int(_clamp(cfg.button_count, BTN_COUNT_MIN, BTN_COUNT_MAX))
    return layout, unit_count, body, basin, actuator, button_count


def resolve_config(
    config: DrinkingFountainConfig | None = None,
) -> ResolvedDrinkingFountainConfig:
    cfg = config or DrinkingFountainConfig()
    layout, unit_count, body, basin, actuator, button_count = _resolve_choices(cfg)

    palette_style = (
        cfg.palette_style if cfg.palette_style in PALETTES else "teal_steel"
    )
    mats = dict(PALETTES[palette_style])
    center_feature = (
        cfg.center_feature if cfg.center_feature in CENTER_MODULES else "tiered_column"
    )

    # Pylon height clamp keeps the test-domain proportion (~1 m, 0.95<h<1.10).
    h_scale = _clamp(cfg.pylon_height_scale, 0.95, 1.06)
    pylon_h = _clamp(PYLON_H * h_scale, 0.96, 1.08)

    body_width_scale = _clamp(cfg.body_width_scale, 0.92, 1.10)
    basin_scale = _clamp(cfg.basin_size_scale, 0.90, 1.12)

    btn_travel = _clamp(cfg.btn_travel, 0.006, 0.010)
    pedal_press = _clamp(cfg.pedal_press, 0.22, 0.34)
    unit_spacing = _clamp(cfg.unit_spacing, UNIT_SPACING_MIN, UNIT_SPACING_MAX)
    min_radial = max(
        RADIAL_RADIUS_MIN,
        unit_count * (BASIN_X * basin_scale + 0.12) / (2.0 * math.pi),
    )
    ring_radius = _clamp(cfg.ring_radius, min_radial, RADIAL_RADIUS_MAX)

    # Multi-control spacing must (a) keep adjacent mounting bosses from merging
    # into one blob, and (b) keep the whole row inside the faceplate width.
    spacing_scale = _clamp(cfg.btn_spacing_scale, 0.90, 1.10)
    # Push-button row: floor is 2*boss_r + clearance so the two raised bosses
    # never touch (this is the dual-button "merged blob" overlap fix).
    btn_floor = 2.0 * BTN_BOSS_R + 0.012
    btn_spacing = _clamp(BTN_SPACING * spacing_scale, btn_floor, 0.060)
    # Rotary-knob row: larger collars need a wider floor.
    knob_floor = 2.0 * RKNOB_BOSS_R + 0.012
    knob_spacing = _clamp(RKNOB_SPACING * spacing_scale, knob_floor, 0.066)
    if button_count >= 2:
        max_btn_row = FACE_X - 2.0 * BTN_BOSS_R
        if (button_count - 1) * btn_spacing > max_btn_row:
            btn_spacing = max(btn_floor, max_btn_row / (button_count - 1))
        max_knob_row = FACE_X - 2.0 * RKNOB_BOSS_R
        if (button_count - 1) * knob_spacing > max_knob_row:
            knob_spacing = max(knob_floor, max_knob_row / (button_count - 1))

    return ResolvedDrinkingFountainConfig(
        layout_mode=layout,
        unit_count=unit_count,
        body_module=body,
        basin_module=basin,
        actuator_module=actuator,
        button_count=button_count,
        center_feature=center_feature,
        palette_style=palette_style,
        mats=mats,
        pylon_h=pylon_h,
        unit_spacing=unit_spacing,
        ring_radius=ring_radius,
        body_width_scale=body_width_scale,
        basin_scale=basin_scale,
        btn_spacing=btn_spacing,
        knob_spacing=knob_spacing,
        btn_travel=btn_travel,
        pedal_press=pedal_press,
        name=cfg.name,
    )


def slot_choices_for_config(
    cfg: DrinkingFountainConfig,
) -> tuple[tuple[str, str], ...]:
    layout, unit_count, body, basin, actuator, button_count = _resolve_choices(cfg)
    # Encode button_count into the actuator slot tuple so the diversity gate
    # counts single vs dual vs pedal as distinct topologies.
    if actuator == "foot_pedal":
        act_name = "foot_pedal"
    else:
        act_name = f"{actuator}_n{button_count}"
    layout_name = "single_unit" if layout == "single_unit" else f"{layout}_n{unit_count}"
    slots = [
        ("layout", layout_name),
        ("body", body),
        ("basin", basin),
        ("actuator", act_name),
    ]
    # The radial centerpiece is a real topology axis (column vs umbrella).
    if layout == "radial_ring":
        center = cfg.center_feature if cfg.center_feature in CENTER_MODULES else "tiered_column"
        slots.append(("center", center))
    return tuple(slots)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Geometry helpers (mesh tube sweeps for goosenecks/bubblers) — from sources.
# --------------------------------------------------------------------------- #
def _unit(v):
    length = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if length < 1e-9:
        return (0.0, 0.0, 1.0)
    return (v[0] / length, v[1] / length, v[2] / length)


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _combine_mesh_geometries(*geometries):
    vertices: list = []
    faces: list = []
    for geom in geometries:
        offset = len(vertices)
        vertices.extend(geom.vertices)
        faces.extend((a + offset, b + offset, c + offset) for a, b, c in geom.faces)
    return MeshGeometry(vertices=vertices, faces=faces)


def _translate_mesh(geom, dx: float, dy: float, dz: float):
    """Return a copy of geom with every vertex shifted by (dx, dy, dz)."""
    return MeshGeometry(
        vertices=[(x + dx, y + dy, z + dz) for (x, y, z) in geom.vertices],
        faces=list(geom.faces),
    )


def _hollow_tube_mesh_from_path(points, outer_radius, inner_radius=None, segments=24):
    """Thin-wall open tube mesh following a 3D path, with visible hollow ends."""
    inner_radius = inner_radius or outer_radius * 0.55
    vertices: list = []
    faces: list = []
    rings = []
    n = len(points)
    for i, p in enumerate(points):
        if i == 0:
            tangent = (points[1][0] - p[0], points[1][1] - p[1], points[1][2] - p[2])
        elif i == n - 1:
            tangent = (p[0] - points[i - 1][0], p[1] - points[i - 1][1], p[2] - points[i - 1][2])
        else:
            tangent = (
                points[i + 1][0] - points[i - 1][0],
                points[i + 1][1] - points[i - 1][1],
                points[i + 1][2] - points[i - 1][2],
            )
        tangent = _unit(tangent)
        u = (1.0, 0.0, 0.0)
        if abs(tangent[0]) > 0.92:
            u = (0.0, 1.0, 0.0)
        v = _unit(_cross(tangent, u))
        u = _unit(_cross(v, tangent))
        outer = []
        inner = []
        for k in range(segments):
            a = 2.0 * math.pi * k / segments
            ca = math.cos(a)
            sa = math.sin(a)
            outer.append(len(vertices))
            vertices.append((
                p[0] + outer_radius * (u[0] * ca + v[0] * sa),
                p[1] + outer_radius * (u[1] * ca + v[1] * sa),
                p[2] + outer_radius * (u[2] * ca + v[2] * sa),
            ))
            inner.append(len(vertices))
            vertices.append((
                p[0] + inner_radius * (u[0] * ca + v[0] * sa),
                p[1] + inner_radius * (u[1] * ca + v[1] * sa),
                p[2] + inner_radius * (u[2] * ca + v[2] * sa),
            ))
        rings.append((outer, inner))
    for i in range(n - 1):
        outer0, inner0 = rings[i]
        outer1, inner1 = rings[i + 1]
        for k in range(segments):
            j = (k + 1) % segments
            faces.append((outer0[k], outer1[k], outer1[j]))
            faces.append((outer0[k], outer1[j], outer0[j]))
            faces.append((inner0[k], inner1[j], inner1[k]))
            faces.append((inner0[k], inner0[j], inner1[j]))
    for ring_index in (0, n - 1):
        outer, inner = rings[ring_index]
        for k in range(segments):
            j = (k + 1) % segments
            if ring_index == 0:
                faces.append((outer[k], inner[j], inner[k]))
                faces.append((outer[k], outer[j], inner[j]))
            else:
                faces.append((outer[k], inner[k], inner[j]))
                faces.append((outer[k], inner[j], outer[j]))
    return MeshGeometry(vertices=vertices, faces=faces)


def _hollow_variable_tube_mesh_from_path(points, outer_radii, inner_radii, segments=24):
    """Thin-wall tube mesh that can taper smoothly along a 3D path (bubbler)."""
    vertices: list = []
    faces: list = []
    rings = []
    n = len(points)
    if len(outer_radii) != n or len(inner_radii) != n:
        raise ValueError("tube radii must match point count")
    for i, p in enumerate(points):
        if i == 0:
            tangent = (points[1][0] - p[0], points[1][1] - p[1], points[1][2] - p[2])
        elif i == n - 1:
            tangent = (p[0] - points[i - 1][0], p[1] - points[i - 1][1], p[2] - points[i - 1][2])
        else:
            tangent = (
                points[i + 1][0] - points[i - 1][0],
                points[i + 1][1] - points[i - 1][1],
                points[i + 1][2] - points[i - 1][2],
            )
        tangent = _unit(tangent)
        u = (1.0, 0.0, 0.0)
        if abs(tangent[0]) > 0.92:
            u = (0.0, 1.0, 0.0)
        v = _unit(_cross(tangent, u))
        u = _unit(_cross(v, tangent))
        outer = []
        inner = []
        for k in range(segments):
            a = 2.0 * math.pi * k / segments
            ca = math.cos(a)
            sa = math.sin(a)
            outer_radius = outer_radii[i]
            inner_radius = inner_radii[i]
            outer.append(len(vertices))
            vertices.append((
                p[0] + outer_radius * (u[0] * ca + v[0] * sa),
                p[1] + outer_radius * (u[1] * ca + v[1] * sa),
                p[2] + outer_radius * (u[2] * ca + v[2] * sa),
            ))
            inner.append(len(vertices))
            vertices.append((
                p[0] + inner_radius * (u[0] * ca + v[0] * sa),
                p[1] + inner_radius * (u[1] * ca + v[1] * sa),
                p[2] + inner_radius * (u[2] * ca + v[2] * sa),
            ))
        rings.append((outer, inner))
    for i in range(n - 1):
        outer0, inner0 = rings[i]
        outer1, inner1 = rings[i + 1]
        for k in range(segments):
            j = (k + 1) % segments
            faces.append((outer0[k], outer1[k], outer1[j]))
            faces.append((outer0[k], outer1[j], outer0[j]))
            faces.append((inner0[k], inner1[j], inner1[k]))
            faces.append((inner0[k], inner0[j], inner1[j]))
    for ring_index in (0, n - 1):
        outer, inner = rings[ring_index]
        for k in range(segments):
            j = (k + 1) % segments
            if ring_index == 0:
                faces.append((outer[k], inner[j], inner[k]))
                faces.append((outer[k], outer[j], inner[j]))
            else:
                faces.append((outer[k], inner[k], inner[j]))
                faces.append((outer[k], inner[j], outer[j]))
    return MeshGeometry(vertices=vertices, faces=faces)


def _box_mesh(cx, cy, cz, sx, sy, sz):
    """Axis-aligned box mesh centered at (cx,cy,cz) with full sizes sx,sy,sz."""
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    v = [
        (cx - hx, cy - hy, cz - hz),
        (cx + hx, cy - hy, cz - hz),
        (cx + hx, cy + hy, cz - hz),
        (cx - hx, cy + hy, cz - hz),
        (cx - hx, cy - hy, cz + hz),
        (cx + hx, cy - hy, cz + hz),
        (cx + hx, cy + hy, cz + hz),
        (cx - hx, cy + hy, cz + hz),
    ]
    f = [
        (0, 2, 1), (0, 3, 2),  # bottom
        (4, 5, 6), (4, 6, 7),  # top
        (0, 1, 5), (0, 5, 4),  # -y
        (2, 3, 7), (2, 7, 6),  # +y
        (1, 2, 6), (1, 6, 5),  # +x
        (0, 4, 7), (0, 7, 3),  # -x
    ]
    return MeshGeometry(vertices=v, faces=f)


def _annular_cylinder_mesh(center, outer_radius, inner_radius, height, segments=32):
    cx, cy, z0 = center
    z1 = z0 + height
    vertices = []
    for z in (z0, z1):
        for r in (outer_radius, inner_radius):
            for k in range(segments):
                a = 2.0 * math.pi * k / segments
                vertices.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    faces = []
    bo = 0
    bi = segments
    to = 2 * segments
    ti = 3 * segments
    for k in range(segments):
        j = (k + 1) % segments
        faces.append((bo + k, bo + j, to + j))
        faces.append((bo + k, to + j, to + k))
        faces.append((bi + k, ti + j, bi + j))
        faces.append((bi + k, ti + k, ti + j))
        faces.append((to + k, to + j, ti + j))
        faces.append((to + k, ti + j, ti + k))
        faces.append((bo + k, bi + j, bo + j))
        faces.append((bo + k, bi + k, bi + j))
    return MeshGeometry(vertices=vertices, faces=faces)


def _loft_levels(levels, width):
    """Loft rectangular sections (centered at per-level Y) up the height."""
    z0 = levels[0][0]
    wp = cq.Workplane("XY").workplane(offset=z0)
    first = True
    prev_cy = 0.0
    for z, by, fy in levels:
        cy = 0.5 * (by + fy)
        depth = max(fy - by, 0.004)
        if first:
            wp = wp.center(0.0, cy).rect(width, depth)
            prev_cy = cy
            first = False
        else:
            wp = wp.workplane(offset=(z - z0)).center(0.0, cy - prev_cy).rect(width, depth)
            prev_cy = cy
        z0 = z
    return wp.loft(combine=True)


def _side_profile(front_pts, back_pts):
    """Curved hollow side-profile of the pylon as a lofted sheet-steel shell."""
    levels = []
    for (fy, fz), (by, _bz) in zip(front_pts, back_pts):
        levels.append((fz, by, fy))
    solid = _loft_levels(levels, PYLON_X)
    inner_levels = []
    for z, by, fy in levels:
        cy = 0.5 * (by + fy)
        depth = max(fy - by - 2.0 * WALL_T, 0.004)
        inner_levels.append((z, cy - depth / 2.0, cy + depth / 2.0))
    inner_solid = _loft_levels(inner_levels, PYLON_X - 2.0 * WALL_T)
    return solid.cut(inner_solid)


# --------------------------------------------------------------------------- #
# Slot A: body modules
# --------------------------------------------------------------------------- #
def _build_pylon(pylon_h: float, *, with_pedal_boss: bool):
    """Curved teal pylon (hollow sheet-steel standard) rising to pylon_h."""
    n = 11
    front_pts = []
    back_pts = []
    for i in range(n):
        t = i / (n - 1)
        z = t * pylon_h
        e = 0.5 - 0.5 * math.cos(math.pi * t)
        fy = BASE_FRONT_Y + (TOP_FRONT_Y - BASE_FRONT_Y) * e
        by = BASE_BACK_Y + (TOP_BACK_Y - BASE_BACK_Y) * t
        front_pts.append((fy, z))
        back_pts.append((by, z))
    body = _side_profile(front_pts, back_pts)
    foot = (
        cq.Workplane("XY")
        .workplane(offset=0.0)
        .center(0.0, 0.5 * (BASE_BACK_Y + BASE_FRONT_Y))
        .rect(PYLON_X, BASE_FRONT_Y - BASE_BACK_Y)
        .extrude(0.018)
    )
    body = body.union(foot)
    if with_pedal_boss:
        boss = (
            cq.Workplane("XZ")
            .workplane(offset=-BASE_FRONT_Y)
            .center(0.0, PEDAL_PIVOT_Z)
            .circle(PEDAL_PIVOT_R + 0.005)
            .extrude(-0.010)  # protrude toward +Y
        )
        body = body.union(boss)
    return body


def _build_mounting_plate():
    """Flat stainless wall plate with four corner screw holes (back face y=0)."""
    plate = cq.Workplane("XY").box(PLATE_X, PLATE_T, PLATE_H, centered=(True, False, True))
    plate = plate.translate((0.0, 0.0, PLATE_Z_CENTER))
    for sx in (-1, 1):
        for sz in (-1, 1):
            hx = sx * PLATE_HOLE_DX
            hz = PLATE_Z_CENTER + sz * PLATE_HOLE_DZ
            hole = (
                cq.Workplane("XY")
                .workplane(offset=-0.005)
                .center(hx, hz)
                .circle(PLATE_HOLE_R)
                .extrude(PLATE_T + 0.01)
            )
            plate = plate.cut(hole)
    return plate


def _build_wall_body(body_w: float):
    """Compact hollow painted-steel shell (back face y=0, bottom at z=0)."""
    bx = BODY_X * body_w
    outer = (
        cq.Workplane("XY")
        .box(bx, BODY_Y, BODY_H, centered=(True, False, False))
        .edges("|Z")
        .fillet(BODY_FILLET)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=WALL_T)
        .box(bx - 2.0 * WALL_T, BODY_Y - 2.0 * WALL_T, BODY_H + 0.01, centered=(True, True, False))
    )
    return outer.cut(inner)


# --------------------------------------------------------------------------- #
# Slot B: basin modules (basin authored centered in XY, floor at z=0)
# --------------------------------------------------------------------------- #
def _build_rect_basin(scale: float):
    bx, by, bh = BASIN_X * scale, BASIN_Y * scale, BASIN_H
    outer = (
        cq.Workplane("XY")
        .box(bx, by, bh, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.010)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=BASIN_WALL)
        .box(bx - 2.0 * BASIN_WALL, by - 2.0 * BASIN_WALL, bh, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.006)
    )
    basin = outer.cut(inner)
    drain = cq.Workplane("XY").workplane(offset=-0.005).circle(0.012).extrude(BASIN_WALL + 0.01)
    return basin.cut(drain)


def _build_round_basin(scale: float):
    r = ROUND_BASIN_R * scale
    rim_r = ROUND_BASIN_RIM_R * scale
    bh = ROUND_BASIN_H
    outer = cq.Workplane("XY").circle(r).extrude(bh)
    outer = outer.edges("<Z").fillet(0.008)
    inner_r = r - BASIN_WALL
    inner = cq.Workplane("XY").workplane(offset=BASIN_WALL).circle(inner_r).extrude(bh)
    inner = inner.edges("<Z").fillet(inner_r * 0.35)
    basin = outer.cut(inner)
    rim = (
        cq.Workplane("XY")
        .workplane(offset=bh - 0.008)
        .circle(rim_r)
        .circle(r - 0.001)
        .extrude(0.008)
    )
    basin = basin.union(rim)
    drain = cq.Workplane("XY").workplane(offset=-0.005).circle(0.012).extrude(BASIN_WALL + 0.01)
    return basin.cut(drain)


def _gooseneck_spout(back_y: float, forward_span: float):
    """Short drinking gooseneck: riser up the back wall arching forward/down."""
    riser_base_z = BASIN_WALL
    riser_top_z = BASIN_H
    pts = []
    n_riser = 6
    for i in range(n_riser + 1):
        t = i / n_riser
        pts.append((0.0, back_y, riser_base_z + (riser_top_z - riser_base_z) * t))
    n = 22
    for i in range(1, n + 1):
        t = i / n
        z = riser_top_z + SPOUT_RISE * math.sin(math.pi * 0.5 * min(t * 1.25, 1.0))
        y = back_y + forward_span * (0.5 - 0.5 * math.cos(math.pi * t))
        pts.append((0.0, y, z))
    return _combine_mesh_geometries(
        _hollow_tube_mesh_from_path(pts, SPOUT_R),
        _annular_cylinder_mesh(
            (0.0, back_y, BASIN_WALL - 0.002),
            SPOUT_R + 0.006,
            max(SPOUT_R * 0.55, 0.0025),
            0.014,
        ),
    )


def _bubbler_spout(back_y: float, forward_span: float):
    """Classic up-spraying bubbler: tapered hollow tube arching up to a nozzle."""
    riser_base_z = BASIN_WALL
    riser_top_z = BASIN_H
    pts = []
    n_riser = 6
    for i in range(n_riser + 1):
        t = i / n_riser
        pts.append((0.0, back_y, riser_base_z + (riser_top_z - riser_base_z) * t))
    n_arch = 20
    for i in range(1, n_arch + 1):
        t = i / n_arch
        z = riser_top_z + SPOUT_RISE * math.sin(math.pi * 0.5 * t)
        y = back_y + forward_span * (0.5 - 0.5 * math.cos(math.pi * t))
        pts.append((0.0, y, z))
    bend_base = pts[-1]
    nozzle_r = SPOUT_R * 0.55
    nozzle_h = 0.020
    outlet_pts = pts + [
        (bend_base[0], bend_base[1] + 0.0025, bend_base[2] + 0.004),
        (bend_base[0], bend_base[1] + 0.0035, bend_base[2] + 0.010),
        (bend_base[0], bend_base[1] + 0.0025, bend_base[2] + 0.016),
        (bend_base[0], bend_base[1] + 0.0005, bend_base[2] + nozzle_h),
    ]
    outer_radii = [SPOUT_R] * len(pts) + [
        SPOUT_R * 0.92,
        SPOUT_R * 0.76,
        SPOUT_R * 0.64,
        nozzle_r,
    ]
    inner_radii = [max(r * 0.55, 0.0015) for r in outer_radii]
    tip_pt = outlet_pts[-1]
    return _combine_mesh_geometries(
        _hollow_variable_tube_mesh_from_path(outlet_pts, outer_radii, inner_radii, segments=28),
        _annular_cylinder_mesh(
            (tip_pt[0], tip_pt[1], tip_pt[2] - 0.002),
            nozzle_r + 0.003,
            inner_radii[-1],
            0.004,
            segments=24,
        ),
        _annular_cylinder_mesh(
            (0.0, back_y, BASIN_WALL - 0.002),
            SPOUT_R + 0.006,
            max(SPOUT_R * 0.55, 0.0025),
            0.014,
        ),
    )


def _build_bottle_filler_arch(back_y: float, basin_y: float):
    """Tall bottle-filler gooseneck rising well above the basin rim."""
    riser_base_z = BASIN_WALL
    riser_top_z = BASIN_H + 0.040
    pts = []
    n_riser = 8
    for i in range(n_riser + 1):
        t = i / n_riser
        pts.append((0.0, back_y, riser_base_z + (riser_top_z - riser_base_z) * t))
    n_arch = 28
    for i in range(1, n_arch + 1):
        t = i / n_arch
        rise = FILLER_RISE * math.sin(math.pi * 0.5 * min(t * 1.15, 1.0))
        tip_drop = 0.025 * max(t - 0.85, 0.0) / 0.15 if t > 0.85 else 0.0
        z = riser_top_z + rise - tip_drop
        y = back_y + (FILLER_REACH * basin_y) * (0.5 - 0.5 * math.cos(math.pi * t))
        pts.append((0.0, y, z))
    tip_pt = pts[-1]
    nozzle_len = 0.018
    # The riser flange seats the arch on the basin mounting hub. The arch swivels
    # about the vertical riser, so it carries NO long forward base block (which
    # would sweep out of the basin when turned); the flange + basin hub seat it.
    return _combine_mesh_geometries(
        _hollow_tube_mesh_from_path(pts, FILLER_R),
        _hollow_tube_mesh_from_path(
            [tip_pt, (tip_pt[0], tip_pt[1], tip_pt[2] - nozzle_len)],
            FILLER_R - 0.002,
            max((FILLER_R - 0.002) * 0.55, 0.0025),
            segments=24,
        ),
        _annular_cylinder_mesh(
            (0.0, back_y, BASIN_WALL - 0.002),
            FILLER_R + 0.008,
            max(FILLER_R * 0.55, 0.003),
            0.016,
        ),
    )


# --------------------------------------------------------------------------- #
# Faceplate + decorations (front panel hangs on the body front)
# --------------------------------------------------------------------------- #
def _build_faceplate(
    face_center_z: float,
    bosses: tuple[tuple[float, float, float, float], ...],
):
    """Brushed-steel front strip with mounting bosses + engraved bottle pictogram.

    Plate spans local y in [0, FACE_T]; centered in X and Z. Each entry in
    `bosses` is (cx, cz_body_local, radius, length): a cylinder protruding +Y
    (front) at the given body-local z, which a button/knob/fitting mounts onto.
    """
    plate = (
        cq.Workplane("XY")
        .box(FACE_X, FACE_T, FACE_H, centered=(True, False, True))
        .edges("|Y")
        .fillet(0.006)
    )

    def _front_cyl(cx, cz, r, length, start=FACE_T):
        return (
            cq.Workplane("XZ")
            .workplane(offset=-start)
            .center(cx, cz)
            .circle(r)
            .extrude(-length)
        )

    for cx, cz_body, r, length in bosses:
        plate = plate.union(_front_cyl(cx, cz_body - face_center_z, r, length))

    bz = -0.5 * FACE_H + 0.130
    recess = 0.0025
    body_w, body_h = 0.034, 0.060

    def _picto_part(cz, w, h):
        return (
            cq.Workplane("XZ")
            .workplane(offset=-(FACE_T - recess))
            .center(0.0, cz)
            .rect(w, h)
            .extrude(-(recess + 0.0005))
        )

    bottle = _picto_part(bz, body_w, body_h)
    neck = _picto_part(bz + body_h / 2.0 + 0.010, 0.014, 0.022)
    cap = _picto_part(bz + body_h / 2.0 + 0.026, 0.018, 0.008)
    picto = bottle.union(neck).union(cap)
    plate = plate.cut(picto)
    return plate, picto


def _build_knob():
    """Secondary valve fitting: a turnable chrome flow knob (base y=0, +Y front).

    Carries an off-axis pointer rib on the cap so its REVOLUTE turn is visible
    to the AABB spin check (an axisymmetric cylinder would be spin-invariant)."""
    fitting = cq.Workplane("XZ").circle(KNOB_R).extrude(-KNOB_LEN)
    cap = (
        cq.Workplane("XZ")
        .workplane(offset=-KNOB_LEN)
        .circle(KNOB_R + 0.003)
        .extrude(-0.006)
    )
    knob = fitting.union(cap)
    # short shaft into the boss (captured) so connectivity is robust
    shaft = (
        cq.Workplane("XZ")
        .workplane(offset=-0.002)
        .circle(KNOB_R * 0.4)
        .extrude(0.014)
    )
    knob = knob.union(shaft)
    # Needle pointer that extends PAST the cap rim so the turn shifts the AABB
    # (a pointer inside the rim would leave the spin AABB-invariant).
    pointer = (
        cq.Workplane("XZ")
        .workplane(offset=-(KNOB_LEN + 0.006))
        .center(0.0, KNOB_R + 0.003)
        .rect(0.004, 0.016)
        .extrude(-0.003)
    )
    return knob.union(pointer)


def _build_rotary_knob():
    """Primary rotary control knob: knurled chrome cylinder protruding +Y, a
    grip skirt, a short captured shaft, and an off-axis pointer rib so its
    REVOLUTE turn registers on the AABB spin check (base near y=0, +Y front)."""
    body = (
        cq.Workplane("XZ")
        .circle(RKNOB_R)
        .extrude(-RKNOB_LEN)
        .edges(">Y")
        .fillet(0.003)
    )
    skirt = cq.Workplane("XZ").circle(RKNOB_R + 0.002).extrude(-0.004)
    knob = body.union(skirt)
    shaft = (
        cq.Workplane("XZ")
        .workplane(offset=-0.002)
        .circle(RKNOB_R * 0.35)
        .extrude(RKNOB_BOSS_LEN + 0.008)
    )
    knob = knob.union(shaft)
    # Needle pointer extending PAST the knob rim so the turn shifts the AABB.
    pointer = (
        cq.Workplane("XZ")
        .workplane(offset=-RKNOB_LEN)
        .center(0.0, RKNOB_R + 0.001)
        .rect(RKNOB_POINTER_W, 0.018)
        .extrude(-0.004)
    )
    return knob.union(pointer)


def _build_grille():
    """Perforated D-shaped bottle-rest shelf (centered XY, bottom z=0)."""
    shelf = (
        cq.Workplane("XY")
        .moveTo(-GRILLE_R, 0.0)
        .threePointArc((0.0, GRILLE_R), (GRILLE_R, 0.0))
        .lineTo(-GRILLE_R, 0.0)
        .close()
        .extrude(GRILLE_T)
    )
    lip = (
        cq.Workplane("XY")
        .moveTo(-GRILLE_R, 0.0)
        .threePointArc((0.0, GRILLE_R), (GRILLE_R, 0.0))
        .lineTo(-GRILLE_R, 0.0)
        .close()
        .extrude(GRILLE_T + 0.010)
    )
    lip_inner = (
        cq.Workplane("XY")
        .moveTo(-(GRILLE_R - 0.006), 0.0)
        .threePointArc((0.0, GRILLE_R - 0.006), (GRILLE_R - 0.006, 0.0))
        .lineTo(-(GRILLE_R - 0.006), 0.0)
        .close()
        .extrude(GRILLE_T + 0.012)
    )
    lip = lip.cut(lip_inner)
    shelf = shelf.union(lip)
    holes = None
    steps = int((2 * GRILLE_R) / GRILLE_PITCH) + 1
    start = -GRILLE_R + 0.012
    for ix in range(steps):
        x = start + ix * GRILLE_PITCH
        for iy in range(steps):
            y = 0.012 + iy * GRILLE_PITCH
            if x * x + y * y < (GRILLE_R - 0.010) ** 2 and y < GRILLE_R - 0.006:
                hole = (
                    cq.Workplane("XY")
                    .workplane(offset=-0.005)
                    .center(x, y)
                    .circle(GRILLE_HOLE_R)
                    .extrude(GRILLE_T + 0.01)
                )
                holes = hole if holes is None else holes.union(hole)
    if holes is not None:
        shelf = shelf.cut(holes)
    bracket = (
        cq.Workplane("XY")
        .center(0.0, -0.012)
        .box(0.060, 0.024, GRILLE_T, centered=(True, True, False))
    )
    return shelf.union(bracket)


# --------------------------------------------------------------------------- #
# Slot C: actuator geometry
# --------------------------------------------------------------------------- #
def _build_button(btn_travel: float):
    """Chrome push-button plunger: cap (+Y) with captured stem (-Y, into boss)."""
    cap = (
        cq.Workplane("XZ")
        .circle(BTN_R)
        .extrude(-BTN_LEN)
        .edges(">Y")
        .fillet(0.003)
    )
    stem_len = BTN_BOSS_LEN + btn_travel + 0.010
    stem = (
        cq.Workplane("XZ")
        .workplane(offset=-0.004)
        .circle(BTN_R - 0.005)
        .extrude(stem_len)
    )
    return cap.union(stem)


def _build_foot_pedal():
    """Chrome foot-pedal treadle with pivot barrel at the rear edge (origin at
    pivot axis center). Plate extends +Y; top surface near z=0."""
    barrel = (
        cq.Workplane("YZ")
        .workplane(offset=-PEDAL_X / 2.0)
        .circle(PEDAL_PIVOT_R)
        .extrude(PEDAL_X)
    )
    for sign in (-1, 1):
        cap = (
            cq.Workplane("YZ")
            .workplane(offset=sign * PEDAL_X / 2.0 - 0.001 * sign)
            .circle(PEDAL_PIVOT_R + 0.003)
            .extrude(0.002 * sign)
        )
        barrel = barrel.union(cap)
    plate_start_y = PEDAL_PIVOT_R * 0.5
    plate_depth = PEDAL_Y - plate_start_y
    plate_cy = plate_start_y + plate_depth / 2.0
    plate = (
        cq.Workplane("XY")
        .workplane(offset=-PEDAL_T)
        .center(0.0, plate_cy)
        .box(PEDAL_X - 0.006, plate_depth, PEDAL_T, centered=(True, True, False))
    )
    gussets = None
    for sign in (-1, 1):
        gx = sign * (PEDAL_X / 2.0 - 0.018)
        gusset = (
            cq.Workplane("XY")
            .workplane(offset=-PEDAL_T)
            .center(gx, PEDAL_PIVOT_R + 0.010)
            .box(0.008, 0.025, PEDAL_T, centered=(True, True, False))
        )
        gussets = gusset if gussets is None else gussets.union(gusset)
    pedal = barrel.union(plate)
    if gussets is not None:
        pedal = pedal.union(gussets)
    n_ribs = 4
    rib_spacing = (PEDAL_Y - 0.020) / max(n_ribs - 1, 1)
    for i in range(n_ribs):
        ry = PEDAL_PIVOT_R + 0.012 + i * rib_spacing
        rib = (
            cq.Workplane("XY")
            .workplane(offset=0.0)
            .center(0.0, ry)
            .box(PEDAL_X - 0.016, 0.004, 0.002, centered=(True, True, False))
        )
        pedal = pedal.union(rib)
    front_lip = (
        cq.Workplane("XY")
        .workplane(offset=0.0)
        .center(0.0, PEDAL_Y - 0.003)
        .box(PEDAL_X - 0.010, 0.006, 0.005, centered=(True, True, False))
    )
    return pedal.union(front_lip)


# --------------------------------------------------------------------------- #
# Geometry context — resolves the body-frame mounting points the upper slots
# attach to (so basin/faceplate/actuator can be wired the same way for both
# pedestal and wall bodies).
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _BodyFrame:
    """Mounting points the upper slots attach to, expressed in the BODY part's
    own local frame (the part that basin/faceplate parent to). For the pedestal
    the body part is the pylon, whose local frame == world. For the wall body
    the body part is the shell, whose local origin sits at world
    (0, PLATE_T, BODY_BOT_Z); so its local coords differ from world."""

    body_part_name: str  # part that basin/faceplate parent to
    body_visual_name: str  # the body's main visual (mating face geometry)
    top_z_local: float  # body-local z of the body top (basin floor seat)
    top_z_world: float  # world z of the body top (for faceplate world placement)
    front_y_local: float  # body-local y of the body front face
    basin_cy_local: float  # basin center y (forward overhang) in body-local
    face_y_local: float  # faceplate back-face y in body-local frame
    pylon_part_name: str  # pylon/base part (for pedal pivot); "" if none


def _basin_y(r: ResolvedDrinkingFountainConfig) -> float:
    return (ROUND_BASIN_R * 2.0 if r.basin_module == "round_basin" else BASIN_Y) * r.basin_scale


def _basin_back_y(r: ResolvedDrinkingFountainConfig) -> float:
    if r.basin_module == "round_basin":
        return -ROUND_BASIN_R * r.basin_scale + BASIN_WALL + 0.006
    return -(BASIN_Y * r.basin_scale) / 2.0 + BASIN_WALL + 0.006


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def _build_single_drinking_fountain(
    config: DrinkingFountainConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    mats = r.mats
    model = ArticulatedObject(name="drinking_fountain", assets=assets)
    body_mat = model.material("body", rgba=mats["body"])
    basin_mat = model.material("basin", rgba=mats["basin"])
    chrome_mat = model.material("chrome", rgba=mats["chrome"])
    dark_mat = model.material("engraving", rgba=mats["engraving"])

    # ----- Slot A: body / mount -------------------------------------------- #
    if r.body_module == "pedestal_body":
        pylon = model.part("pylon_body")
        with_pedal = r.actuator_module == "foot_pedal"
        pylon.visual(
            mesh_from_cadquery(
                _build_pylon(r.pylon_h, with_pedal_boss=with_pedal), "pylon_body"
            ),
            material=body_mat,
            name="pylon_body", material_class_id=("metal.paint_coated" if r.palette_style in {"teal_steel", "stainless_minimal", "slate_grey", "hospital_white"} else "metal.bronze_cast"),
        )
        pylon.inertial = Inertial.from_geometry(
            Box((PYLON_X, 0.15, r.pylon_h)),
            mass=22.0,
            origin=Origin(xyz=(0.0, 0.03, r.pylon_h / 2.0)),
        )
        bf = _BodyFrame(
            body_part_name="pylon_body",
            body_visual_name="pylon_body",
            top_z_local=r.pylon_h,
            top_z_world=r.pylon_h,
            front_y_local=TOP_FRONT_Y,
            basin_cy_local=BASIN_CY,
            # Seat the plate back 2mm into the pylon front so the mating face
            # touches (the swoosh front at the faceplate band sits near TOP_FRONT_Y).
            face_y_local=TOP_FRONT_Y - 0.002,
            pylon_part_name="pylon_body",
        )
    else:  # wall_mounted_body
        plate = model.part("mounting_plate")
        plate.visual(
            mesh_from_cadquery(_build_mounting_plate(), "mounting_plate"),
            material=basin_mat,
            name="mounting_plate", material_class_id="metal.stainless_matte",
        )
        plate.inertial = Inertial.from_geometry(
            Box((PLATE_X, PLATE_T, PLATE_H)),
            mass=3.0,
            origin=Origin(xyz=(0.0, PLATE_T / 2.0, PLATE_Z_CENTER)),
        )
        body = model.part("body")
        body.visual(
            mesh_from_cadquery(_build_wall_body(r.body_width_scale), "body"),
            material=body_mat,
            name="body_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"teal_steel", "stainless_minimal", "slate_grey", "hospital_white"} else "metal.bronze_cast"),
        )
        body.inertial = Inertial.from_geometry(
            Box((BODY_X * r.body_width_scale, BODY_Y, BODY_H)),
            mass=8.0,
            origin=Origin(xyz=(0.0, BODY_Y / 2.0, BODY_H / 2.0)),
        )
        # Body back face seats on the plate front (y=PLATE_T), bottom at BODY_BOT_Z.
        model.articulation(
            "plate_to_body",
            ArticulationType.FIXED,
            parent=plate,
            child=body,
            origin=Origin(xyz=(0.0, PLATE_T, BODY_BOT_Z)),
            mating=MatingContract(
                parent_face_geometry="mounting_plate",
                parent_face_side="positive_y",
                child_face_geometry="body_shell",
                child_face_side="negative_y",
                contact_tol=0.002,
            ),
        )
        # Body shell authored with bottom at z=0, back face at y=0 -> in its
        # OWN local frame the top is at BODY_H and the front face at BODY_Y.
        bf = _BodyFrame(
            body_part_name="body",
            body_visual_name="body_shell",
            top_z_local=BODY_H,
            top_z_world=BODY_BOT_Z + BODY_H,
            front_y_local=BODY_Y,
            basin_cy_local=BODY_Y * 0.55,
            # Seat the plate back 4mm into the body front for a flush mount.
            face_y_local=BODY_Y - 0.004,
            pylon_part_name="",
        )

    body_part = model.get_part(bf.body_part_name)

    # ----- Slot B: basin + swiveling water spout --------------------------- #
    back_y = _basin_back_y(r)
    basin_y = _basin_y(r)
    spout_base_r = FILLER_R if r.basin_module == "bottle_filler" else SPOUT_R
    basin_visual_name = "basin_bowl" if r.basin_module == "round_basin" else "basin_tray"

    basin = model.part("catch_basin")
    if r.basin_module == "round_basin":
        basin_solid = _build_round_basin(r.basin_scale)
        basin.inertial = Inertial.from_geometry(
            Cylinder(radius=ROUND_BASIN_R * r.basin_scale, length=ROUND_BASIN_H),
            mass=2.5,
            origin=Origin(xyz=(0.0, 0.0, ROUND_BASIN_H / 2.0)),
        )
    else:
        basin_solid = _build_rect_basin(r.basin_scale)
        basin.inertial = Inertial.from_geometry(
            Box((BASIN_X * r.basin_scale, BASIN_Y * r.basin_scale, BASIN_H)),
            mass=2.5,
            origin=Origin(xyz=(0.0, 0.0, BASIN_H / 2.0)),
        )
    # Valve mounting hub at the riser: gives the spout a base to seat on AND
    # places solid basin geometry exactly under the swivel-joint origin (so it
    # passes the origin-on-geometry gate).
    spout_hub = (
        cq.Workplane("XY")
        .center(0.0, back_y)
        .circle(spout_base_r + SPOUT_HUB_EXTRA)
        .extrude(BASIN_WALL + 0.006)
    )
    basin_solid = basin_solid.union(spout_hub)
    basin.visual(
        mesh_from_cadquery(basin_solid, "catch_basin"),
        material=basin_mat,
        name=basin_visual_name, material_class_id="metal.stainless_matte",
    )

    # Basin floor center seats on the body top, overhanging forward. Keep the
    # basin's back edge from reaching back into the wall plate / pylon seam:
    # for the wall body the body back face is at local y=0, so the basin center
    # must sit at least half its depth (plus margin) forward.
    basin_half_depth = basin_y / 2.0
    if r.body_module == "wall_mounted_body":
        # Body back face at local y=0; keep the basin back >=10mm forward of it.
        basin_cy_local = max(bf.basin_cy_local, basin_half_depth + 0.010)
    else:
        basin_cy_local = bf.basin_cy_local
    body_top_visual = bf.body_visual_name
    model.articulation(
        f"{bf.body_part_name}_to_basin",
        ArticulationType.FIXED,
        parent=body_part,
        child=basin,
        origin=Origin(xyz=(0.0, basin_cy_local, bf.top_z_local)),
        mating=MatingContract(
            parent_face_geometry=body_top_visual,
            parent_face_side="positive_z",
            child_face_geometry=basin_visual_name,
            child_face_side="negative_z",
            contact_tol=0.004,
        ),
    )

    # Water spout (gooseneck / bubbler / tall filler) — its own part on a
    # REVOLUTE swivel about the vertical riser (axis +Z), so the outlet can
    # swing side-to-side. Authored in basin coords (riser at (0, back_y,
    # BASIN_WALL)) then shifted into a riser-local frame so the swivel axis
    # passes through the part origin.
    if r.basin_module == "bubbler_spout":
        spout_geom_world = _bubbler_spout(back_y, 0.30 * basin_y)
        spout_len = SPOUT_RISE + BASIN_H
    elif r.basin_module == "bottle_filler":
        spout_geom_world = _build_bottle_filler_arch(back_y, basin_y)
        spout_len = FILLER_RISE + BASIN_H
    else:
        spout_geom_world = _gooseneck_spout(back_y, 0.55 * basin_y)
        spout_len = SPOUT_RISE + BASIN_H
    spout_geom = _translate_mesh(spout_geom_world, 0.0, -back_y, -BASIN_WALL)
    spout = model.part("water_spout")
    spout.visual(
        mesh_from_geometry(spout_geom, "water_spout"),
        material=basin_mat,
        name="water_spout", material_class_id="metal.stainless_matte",
    )
    spout.inertial = Inertial.from_geometry(
        Cylinder(radius=max(spout_base_r, 0.006), length=spout_len),
        mass=0.6,
        origin=Origin(xyz=(0.0, 0.0, spout_len / 2.0)),
    )
    model.articulation(
        "basin_to_spout",
        ArticulationType.REVOLUTE,
        parent=basin,
        child=spout,
        origin=Origin(xyz=(0.0, back_y, BASIN_WALL)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=5.0, velocity=1.0, lower=-SPOUT_SWIVEL, upper=SPOUT_SWIVEL
        ),
    )

    # ----- Faceplate (front panel) + decorations -------------------------- #
    # All face_*_z are in the BODY part's LOCAL frame (top at top_z_local).
    face_top_z = bf.top_z_local - 0.010 - (0.010 if r.body_module == "wall_mounted_body" else 0.0)
    face_bot_z = face_top_z - FACE_H
    face_center_z = 0.5 * (face_top_z + face_bot_z)
    btn_z = face_top_z - 0.060
    grille_z = face_bot_z + 0.090

    # Primary actuator row (push buttons OR rotary knobs) at btn_z; the bosses
    # they mount on are unioned into the faceplate.
    if r.actuator_module == "foot_pedal":
        primary_xs: list[float] = []
        primary_boss_r, primary_boss_len = BTN_BOSS_R, BTN_BOSS_LEN
    elif r.actuator_module == "rotary_knob":
        n = r.button_count
        primary_xs = [(i - 0.5 * (n - 1)) * r.knob_spacing for i in range(n)]
        primary_boss_r, primary_boss_len = RKNOB_BOSS_R, RKNOB_BOSS_LEN
    else:
        n = r.button_count
        primary_xs = [(i - 0.5 * (n - 1)) * r.btn_spacing for i in range(n)]
        primary_boss_r, primary_boss_len = BTN_BOSS_R, BTN_BOSS_LEN

    # Secondary valve fitting: offset to the side and (when a primary row is
    # present) dropped well below it so the two never crowd / overlap.
    outer_ctrl_x = max((abs(x) for x in primary_xs), default=0.0)
    if r.actuator_module == "foot_pedal":
        fit_dx = KNOB_DX
        fit_z = btn_z
    else:
        fit_dx = _clamp(
            outer_ctrl_x + primary_boss_r + KNOB_R + 0.006,
            KNOB_DX,
            FACE_X / 2.0 - (KNOB_R + 0.004) - 0.004,
        )
        fit_z = btn_z - KNOB_Z_DROP

    primary_bosses = [(x, btn_z, primary_boss_r, primary_boss_len) for x in primary_xs]
    fitting_boss = (fit_dx, fit_z, KNOB_R + 0.004, 0.008)

    # The faceplate geometry helper places features relative to its own panel
    # center; pass body-local z (it converts using face_center_z).
    plate_geom, picto_geom = _build_faceplate(
        face_center_z, tuple(primary_bosses) + (fitting_boss,)
    )
    faceplate = model.part("front_faceplate")
    faceplate.visual(
        mesh_from_cadquery(plate_geom, "front_faceplate"),
        material=basin_mat,
        name="plate_face", material_class_id="metal.brushed_silver",
    )
    faceplate.visual(
        mesh_from_cadquery(picto_geom, "bottle_pictogram"),
        material=dark_mat,
        name="bottle_pictogram", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    faceplate.inertial = Inertial.from_geometry(
        Box((FACE_X, FACE_T, FACE_H)),
        mass=2.0,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    model.articulation(
        f"{bf.body_part_name}_to_faceplate",
        ArticulationType.FIXED,
        parent=body_part,
        child=faceplate,
        origin=Origin(xyz=(0.0, bf.face_y_local, face_center_z)),
        mating=MatingContract(
            parent_face_geometry=body_top_visual,
            parent_face_side="positive_y",
            child_face_geometry="plate_face",
            child_face_side="negative_y",
            contact_tol=0.008,
        ),
    )

    # Secondary valve fitting: a REAL turnable flow knob (REVOLUTE about +Y),
    # never FIXED. Its captured shaft seats into the faceplate fitting boss.
    fitting = model.part("valve_fitting")
    fitting.visual(mesh_from_cadquery(_build_knob(), "valve_fitting"), material=chrome_mat, name="fitting", material_class_id=("metal.chrome_polished" if r.palette_style in {"teal_steel", "stainless_minimal", "slate_grey", "hospital_white"} else "metal.brass_aged"))
    fitting.inertial = Inertial.from_geometry(
        Cylinder(radius=KNOB_R, length=KNOB_LEN),
        mass=0.05,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    model.articulation(
        "faceplate_to_fitting",
        ArticulationType.REVOLUTE,
        parent=faceplate,
        child=fitting,
        origin=Origin(xyz=(fit_dx, FACE_T, fit_z - face_center_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=4.0, velocity=1.0, lower=-KNOB_SPIN, upper=KNOB_SPIN
        ),
    )

    # Bottle-rest grille shelf cantilevered from the lower front.
    grille = model.part("bottle_grille")
    grille.visual(mesh_from_cadquery(_build_grille(), "bottle_grille"), material=basin_mat, name="grille", material_class_id="metal.patterned_sheet_panel")
    grille.inertial = Inertial.from_geometry(
        Box((2 * GRILLE_R, GRILLE_R, GRILLE_T)),
        mass=0.4,
        origin=Origin(xyz=(0.0, GRILLE_R / 2.0, 0.0)),
    )
    model.articulation(
        "faceplate_to_grille",
        ArticulationType.FIXED,
        parent=faceplate,
        child=grille,
        origin=Origin(xyz=(0.0, FACE_T - 0.004, grille_z - face_center_z)),
    )

    # ----- Slot C: actuator (core motion) --------------------------------- #
    if r.actuator_module == "foot_pedal":
        pedal = model.part("foot_pedal")
        pedal.visual(
            mesh_from_cadquery(_build_foot_pedal(), "foot_pedal"),
            material=chrome_mat,
            name="pedal", material_class_id=("metal.chrome_polished" if r.palette_style in {"teal_steel", "stainless_minimal", "slate_grey", "hospital_white"} else "metal.brass_aged"),
        )
        pedal.inertial = Inertial.from_geometry(
            Box((PEDAL_X, PEDAL_Y, PEDAL_T)),
            mass=0.25,
            origin=Origin(xyz=(0.0, PEDAL_Y / 2.0, 0.0)),
        )
        pivot = model.get_part(bf.pylon_part_name)
        pedal_pivot_y = BASE_FRONT_Y + 0.010
        model.articulation(
            "pylon_to_pedal",
            ArticulationType.REVOLUTE,
            parent=pivot,
            child=pedal,
            origin=Origin(xyz=(0.0, pedal_pivot_y, PEDAL_PIVOT_Z)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=30.0, velocity=1.5, lower=0.0, upper=r.pedal_press
            ),
        )
    elif r.actuator_module == "rotary_knob":
        n = r.button_count
        knob_geom = _build_rotary_knob()
        for i in range(n):
            kx = primary_xs[i]
            name = "control_knob" if n == 1 else f"knob_{i}"
            knob_part = model.part(name)
            knob_part.visual(
                mesh_from_cadquery(knob_geom, name), material=chrome_mat, name=name, material_class_id=("metal.chrome_polished" if r.palette_style in {"teal_steel", "stainless_minimal", "slate_grey", "hospital_white"} else "metal.brass_aged")
            )
            knob_part.inertial = Inertial.from_geometry(
                Cylinder(radius=RKNOB_R, length=RKNOB_LEN),
                mass=0.04,
                origin=Origin(xyz=(0.0, 0.0, 0.0)),
            )
            joint_name = "faceplate_to_knob" if n == 1 else f"faceplate_to_knob_{i}"
            model.articulation(
                joint_name,
                ArticulationType.REVOLUTE,
                parent=faceplate,
                child=knob_part,
                origin=Origin(xyz=(kx, FACE_T + RKNOB_BOSS_LEN, btn_z - face_center_z)),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(
                    effort=4.0, velocity=1.0, lower=-RKNOB_SPIN, upper=RKNOB_SPIN
                ),
            )
    else:
        n = r.button_count
        btn_geom = _build_button(r.btn_travel)
        for i in range(n):
            bx = primary_xs[i]
            name = "push_button" if n == 1 else f"button_{i}"
            btn_part = model.part(name)
            btn_part.visual(
                mesh_from_cadquery(btn_geom, name), material=chrome_mat, name=name, material_class_id=("metal.chrome_polished" if r.palette_style in {"teal_steel", "stainless_minimal", "slate_grey", "hospital_white"} else "metal.brass_aged")
            )
            btn_part.inertial = Inertial.from_geometry(
                Cylinder(radius=BTN_R, length=BTN_LEN),
                mass=0.03,
                origin=Origin(xyz=(0.0, 0.0, 0.0)),
            )
            joint_name = "faceplate_to_button" if n == 1 else f"faceplate_to_button_{i}"
            model.articulation(
                joint_name,
                ArticulationType.PRISMATIC,
                parent=faceplate,
                child=btn_part,
                origin=Origin(xyz=(bx, FACE_T + BTN_BOSS_LEN, btn_z - face_center_z)),
                axis=(0.0, -1.0, 0.0),
                motion_limits=MotionLimits(
                    effort=20.0, velocity=0.1, lower=0.0, upper=r.btn_travel
                ),
            )

    return model


def _single_unit_config_from_resolved(r: ResolvedDrinkingFountainConfig) -> DrinkingFountainConfig:
    return DrinkingFountainConfig(
        layout_mode="single_unit",
        unit_count=1,
        body_module=r.body_module,
        basin_module=r.basin_module,
        actuator_module=r.actuator_module,
        button_count=r.button_count,
        palette_style=r.palette_style,
        pylon_height_scale=r.pylon_h / PYLON_H,
        body_width_scale=r.body_width_scale,
        basin_size_scale=r.basin_scale,
        btn_spacing_scale=r.btn_spacing / BTN_SPACING,
        btn_travel=r.btn_travel,
        pedal_press=r.pedal_press,
        name=r.name,
    )


def _prefixed(prefix: str, name: str) -> str:
    return f"{prefix}{name}" if prefix else name


def _copy_mating_with_parent_visual(mating: MatingContract | None, parent_visual: str) -> MatingContract | None:
    if mating is None:
        return None
    return MatingContract(
        parent_face_geometry=parent_visual,
        parent_face_side=mating.parent_face_side,
        child_face_geometry=mating.child_face_geometry,
        child_face_side=mating.child_face_side,
        contact_tol=mating.contact_tol,
    )


def _append_prefixed_unit(
    target: ArticulatedObject,
    unit: ArticulatedObject,
    *,
    prefix: str,
    skip_parts: set[str] | None = None,
    parent_rewrites: dict[str, str] | None = None,
    origin_offsets: dict[str, tuple[float, float, float]] | None = None,
    mating_parent_visuals: dict[str, str] | None = None,
) -> list[str]:
    skip_parts = skip_parts or set()
    parent_rewrites = parent_rewrites or {}
    origin_offsets = origin_offsets or {}
    mating_parent_visuals = mating_parent_visuals or {}

    child_names = {joint.child for joint in unit.articulations}
    roots = [part.name for part in unit.parts if part.name not in child_names and part.name not in skip_parts]

    for source_part in unit.parts:
        if source_part.name in skip_parts:
            continue
        part = copy.deepcopy(source_part)
        part.name = _prefixed(prefix, part.name)
        target.parts.append(part)
        target._part_index[part.name] = part

    for source_joint in unit.articulations:
        if source_joint.parent in skip_parts or source_joint.child in skip_parts:
            if source_joint.parent not in parent_rewrites:
                continue
        joint = copy.deepcopy(source_joint)
        joint.name = _prefixed(prefix, joint.name)
        joint.parent = parent_rewrites.get(source_joint.parent, _prefixed(prefix, source_joint.parent))
        joint.child = parent_rewrites.get(source_joint.child, _prefixed(prefix, source_joint.child))
        if source_joint.name in origin_offsets:
            dx, dy, dz = origin_offsets[source_joint.name]
            ox, oy, oz = joint.origin.xyz
            joint.origin = Origin(xyz=(ox + dx, oy + dy, oz + dz), rpy=joint.origin.rpy)
        if joint.mimic is not None:
            joint.mimic = Mimic(
                joint=_prefixed(prefix, joint.mimic.joint),
                multiplier=joint.mimic.multiplier,
                offset=joint.mimic.offset,
            )
        if source_joint.name in mating_parent_visuals:
            joint.mating = _copy_mating_with_parent_visual(
                joint.mating,
                mating_parent_visuals[source_joint.name],
            )
        target.articulations.append(joint)
        target._articulation_index[joint.name] = joint

    return [_prefixed(prefix, root) for root in roots]


def _make_linear_base(
    model: ArticulatedObject,
    r: ResolvedDrinkingFountainConfig,
    material,
):
    span = (r.unit_count - 1) * r.unit_spacing
    if r.body_module == "wall_mounted_body":
        root = model.part("bank_backplate")
        root.visual(
            Box((span + PLATE_X + 0.10, PLATE_T, PLATE_H + 0.08)),
            origin=Origin(xyz=(0.0, PLATE_T / 2.0, PLATE_Z_CENTER)),
            material=material,
            name="bank_backplate", material_class_id="metal.stainless_matte",
        )
        root.inertial = Inertial.from_geometry(
            Box((span + PLATE_X + 0.10, PLATE_T, PLATE_H + 0.08)),
            mass=4.0 + 2.0 * r.unit_count,
            origin=Origin(xyz=(0.0, PLATE_T / 2.0, PLATE_Z_CENTER)),
        )
    else:
        root = model.part("bank_base")
        root.visual(
            Box((span + PYLON_X + 0.18, 0.18, 0.035)),
            origin=Origin(xyz=(0.0, 0.035, -0.0175)),
            material=material,
            name="bank_base", material_class_id=("metal.paint_coated" if r.palette_style in {"teal_steel", "stainless_minimal", "slate_grey", "hospital_white"} else "metal.bronze_cast"),
        )
        root.inertial = Inertial.from_geometry(
            Box((span + PYLON_X + 0.18, 0.18, 0.035)),
            mass=8.0 + 3.0 * r.unit_count,
            origin=Origin(xyz=(0.0, 0.035, -0.0175)),
        )
    return root


def _build_tiered_column(col_h: float):
    """Grand tiered bubbling-fountain column: a profiled shaft (base plinth +
    torus moldings), four large flared dish tiers (cone support + dish + a
    beaded double rim + a drip lip), and a top post for the finial. Authored on
    the +Z axis with its base at z=0."""
    # base plinth: a stepped wide molding so the column reads as a real fountain.
    obj = cq.Workplane("XY").circle(COL_R * 2.1).extrude(0.030)
    obj = obj.union(cq.Workplane("XY").workplane(offset=0.030).circle(COL_R * 1.5).extrude(0.022))
    obj = obj.union(cq.Workplane("XY").circle(COL_R).extrude(col_h))
    for zf, rr in COL_TIERS:
        z = col_h * zf
        # flared conical support up to the dish
        cone = (
            cq.Workplane("XY")
            .workplane(offset=z - 0.060)
            .circle(COL_R)
            .workplane(offset=0.060)
            .circle(rr)
            .loft(combine=True)
        )
        dish = cq.Workplane("XY").workplane(offset=z).circle(rr).extrude(0.012)
        # drip lip: a thin wider flange under the dish edge
        lip = (
            cq.Workplane("XY")
            .workplane(offset=z - 0.006)
            .circle(rr + 0.010)
            .circle(rr - 0.004)
            .extrude(0.006)
        )
        # beaded double rim (two stacked annular rings — cheap, no revolve)
        rim = (
            cq.Workplane("XY")
            .workplane(offset=z + 0.012)
            .circle(rr)
            .circle(rr - 0.010)
            .extrude(0.016)
        )
        bead = (
            cq.Workplane("XY")
            .workplane(offset=z + 0.024)
            .circle(rr + 0.004)
            .circle(rr - 0.006)
            .extrude(0.006)
        )
        obj = obj.union(cone).union(lip).union(dish).union(rim).union(bead)
    # collar molding + top post
    obj = obj.union(
        cq.Workplane("XY").workplane(offset=col_h - 0.030).circle(COL_R * 1.25).extrude(0.018)
    )
    obj = obj.union(cq.Workplane("XY").workplane(offset=col_h).circle(0.014).extrude(COL_POST_H))
    return obj


def _build_sun_umbrella(canopy_r: float, rim_z: float):
    """Refined shade umbrella: a full-height central mast, a domed canopy
    (revolved profile + hanging valance) wide enough to shade the ring, and
    radial under-ribs. EVERY piece embeds into the mast/canopy so the union is
    one connected solid (no disconnected islands). Base at z=0; apex = rim_z+RISE.
    """
    apex_z = rim_z + UMBRELLA_RISE
    # Mast runs the FULL height so the canopy hole and rib bases embed into it.
    obj = cq.Workplane("XY").circle(UMBRELLA_MAST_R).extrude(apex_z)
    obj = obj.union(cq.Workplane("XY").circle(UMBRELLA_MAST_R * 1.8).extrude(0.028))  # base foot

    # Canopy: revolve a drooping umbrella profile (x=radius, z=height) about Z.
    # Inner hole radius < mast radius so the mast fills it and they fuse.
    r_apex = UMBRELLA_MAST_R - 0.012
    t = 0.012  # fabric thickness
    profile = [
        (r_apex, apex_z),
        (canopy_r * 0.55, rim_z + UMBRELLA_RISE * 0.45),
        (canopy_r, rim_z),
        (canopy_r, rim_z - UMBRELLA_VALANCE),  # valance bottom
        (canopy_r - 0.018, rim_z - UMBRELLA_VALANCE + 0.010),
        (canopy_r * 0.55, rim_z + UMBRELLA_RISE * 0.45 - t),
        (r_apex, apex_z - t),
    ]
    # NB: revolve axis is in workplane-LOCAL coords; for the XZ workplane the
    # local Y axis is world +Z, so (0,1,0) revolves about the vertical axis.
    obj = obj.union(
        cq.Workplane("XZ").polyline(profile).close().revolve(360.0, (0, 0, 0), (0, 1, 0))
    )

    # Radial under-ribs: flat sloped fins from the mast axis to under the rim,
    # following the canopy underside (base embeds in the mast, top grazes the
    # canopy, so each fin is fused to the connected body).
    rib_top = [
        (0.0, apex_z - t),
        (canopy_r - 0.03, rim_z + 0.002),
        (canopy_r - 0.03, rim_z + 0.002 - 0.018),
        (0.0, apex_z - t - 0.018),
    ]
    for k in range(UMBRELLA_RIB_COUNT):
        a = 2.0 * math.pi * k / UMBRELLA_RIB_COUNT
        fin = (
            cq.Workplane("XZ")
            .polyline(rib_top)
            .close()
            .extrude(0.006, both=True)
        )
        fin = fin.rotate((0, 0, 0), (0, 0, 1), math.degrees(a))
        obj = obj.union(fin)
    # solid finial post poking above the apex (so the finial seats with a
    # generous overlap regardless of canopy-apex tessellation). Radius < the
    # 0.015 joint-origin tol so the on-axis finial origin stays within tol.
    obj = obj.union(
        cq.Workplane("XY").workplane(offset=apex_z - 0.010).circle(0.013).extrude(0.040)
    )
    return obj, apex_z


def _build_center_finial():
    """Kinetic spinner ornament for the centerpiece top: a hub, pitched turbine
    blades (off-axis so the spin registers), and a finial ball. Authored about
    the +Z axis with the hub straddling z=0 (seats on the post/apex)."""
    obj = cq.Workplane("XY").workplane(offset=-0.006).circle(0.020).extrude(0.022)
    n = 5
    for k in range(n):
        a = 2.0 * math.pi * k / n
        blade = (
            cq.Workplane("XY")
            .box(FINIAL_REACH, 0.016, 0.004, centered=(False, True, True))
            .translate((0.018, 0.0, 0.014))
        )
        blade = blade.rotate((0.018, 0.0, 0.014), (1.0, 0.0, 0.0), 30.0)
        blade = blade.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(a))
        obj = obj.union(blade)
    obj = obj.union(cq.Workplane("XY").workplane(offset=0.022).sphere(0.018))
    obj = obj.union(cq.Workplane("XY").workplane(offset=0.040).circle(0.004).extrude(0.020))  # spike
    return obj


def _make_radial_core(
    model: ArticulatedObject,
    r: ResolvedDrinkingFountainConfig,
    base_material,
    structure_material,
    accent_material,
):
    root = model.part("drinking_station_core")
    root.visual(
        Cylinder(radius=r.ring_radius + 0.10, length=0.035),
        origin=Origin(xyz=(0.0, 0.0, -0.0175)),
        material=base_material,
        name="circular_base", material_class_id=("metal.paint_coated" if r.palette_style in {"teal_steel", "stainless_minimal", "slate_grey", "hospital_white"} else "metal.bronze_cast"),
    )
    root.inertial = Inertial.from_geometry(
        Cylinder(radius=r.ring_radius + 0.10, length=0.035),
        mass=10.0 + 2.5 * r.unit_count,
        origin=Origin(xyz=(0.0, 0.0, -0.0175)),
    )

    if r.center_feature == "sun_umbrella":
        # Canopy must overhang past the stations (radius) and clear the tallest
        # station part (the bottle-filler arch reaches ~pylon_h + 0.36).
        canopy_r = r.ring_radius + UMBRELLA_OVERHANG
        rim_z = r.pylon_h + 0.36 + UMBRELLA_CLEARANCE
        umbrella, apex_z = _build_sun_umbrella(canopy_r, rim_z)
        root.visual(
            mesh_from_cadquery(umbrella, "shade_umbrella"),
            material=structure_material,
            name="shade_umbrella", material_class_id=("metal.paint_coated" if r.palette_style in {"teal_steel", "stainless_minimal", "slate_grey", "hospital_white"} else "metal.bronze_cast"),
        )
        # seat the finial on the apex post (origin inside the post, deep overlap)
        finial_z = apex_z + 0.010
    else:
        col_h = max(0.55, r.pylon_h * 1.10)
        root.visual(
            mesh_from_cadquery(_build_tiered_column(col_h), "tiered_fountain_column"),
            material=structure_material,
            name="tiered_fountain_column", material_class_id=("metal.paint_coated" if r.palette_style in {"teal_steel", "stainless_minimal", "slate_grey", "hospital_white"} else "metal.bronze_cast"),
        )
        finial_z = col_h + COL_POST_H

    # Kinetic spinning finial on the centerpiece top (REVOLUTE about +Z).
    finial = model.part("center_finial")
    finial.visual(
        mesh_from_cadquery(_build_center_finial(), "center_finial"),
        material=accent_material,
        name="center_finial", material_class_id=("metal.chrome_polished" if r.palette_style in {"teal_steel", "stainless_minimal", "slate_grey", "hospital_white"} else "metal.brass_aged"),
    )
    finial.inertial = Inertial.from_geometry(
        Cylinder(radius=FINIAL_REACH, length=0.04),
        mass=0.15,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    model.articulation(
        "core_to_finial",
        ArticulationType.REVOLUTE,
        parent=root,
        child=finial,
        origin=Origin(xyz=(0.0, 0.0, finial_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=2.0, lower=-FINIAL_SPIN, upper=FINIAL_SPIN
        ),
    )
    model.meta["radial_center_feature"] = r.center_feature
    model.meta["radial_center_top_z"] = finial_z
    return root


def build_drinking_fountain(
    config: DrinkingFountainConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    if r.layout_mode == "single_unit":
        return _build_single_drinking_fountain(config, assets=assets)

    unit_cfg = _single_unit_config_from_resolved(r)
    unit = _build_single_drinking_fountain(unit_cfg, assets=assets)
    model = ArticulatedObject(name="drinking_fountain", assets=assets)
    model.materials = copy.deepcopy(unit.materials)
    material_by_name = {material.name: material for material in model.materials}
    body_mat = material_by_name["body"]
    basin_mat = material_by_name["basin"]

    if r.layout_mode == "linear_bank":
        root = _make_linear_base(
            model,
            r,
            basin_mat if r.body_module == "wall_mounted_body" else body_mat,
        )
        for i in range(r.unit_count):
            x = (i - 0.5 * (r.unit_count - 1)) * r.unit_spacing
            prefix = f"unit_{i}_"
            if r.body_module == "wall_mounted_body":
                _append_prefixed_unit(
                    model,
                    unit,
                    prefix=prefix,
                    skip_parts={"mounting_plate"},
                    parent_rewrites={"mounting_plate": root.name},
                    origin_offsets={"plate_to_body": (x, 0.0, 0.0)},
                    mating_parent_visuals={"plate_to_body": "bank_backplate"},
                )
            else:
                roots = _append_prefixed_unit(model, unit, prefix=prefix)
                for root_name in roots:
                    model.articulation(
                        f"bank_base_to_{root_name}",
                        ArticulationType.FIXED,
                        parent=root,
                        child=model.get_part(root_name),
                        origin=Origin(xyz=(x, 0.0, 0.0)),
                    )
    else:
        root = _make_radial_core(
            model, r, body_mat, body_mat, material_by_name["chrome"]
        )
        for i in range(r.unit_count):
            theta = 2.0 * math.pi * i / r.unit_count
            x = r.ring_radius * math.cos(theta)
            y = r.ring_radius * math.sin(theta)
            yaw = theta - math.pi / 2.0
            roots = _append_prefixed_unit(model, unit, prefix=f"unit_{i}_")
            for root_name in roots:
                model.articulation(
                    f"station_core_to_{root_name}",
                    ArticulationType.FIXED,
                    parent=root,
                    child=model.get_part(root_name),
                    origin=Origin(xyz=(x, y, 0.0), rpy=(0.0, 0.0, yaw)),
                )

    model.meta["layout_mode"] = r.layout_mode
    model.meta["unit_count"] = r.unit_count
    return model


def build_seeded_drinking_fountain(seed: int) -> ArticulatedObject:
    return build_drinking_fountain(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Author tests / QC
# --------------------------------------------------------------------------- #
def run_drinking_fountain_tests(
    model: ArticulatedObject,
    config: DrinkingFountainConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    unit_count = r.unit_count if r.layout_mode != "single_unit" else 1
    prefixes = ["" if r.layout_mode == "single_unit" else f"unit_{i}_" for i in range(unit_count)]

    if r.layout_mode == "linear_bank":
        root_name = "bank_backplate" if r.body_module == "wall_mounted_body" else "bank_base"
        root = model.get_part(root_name)
        root_lo, root_hi = ctx.part_world_aabb(root)
        ctx.check(
            "linear bank emits one shared rail/backplate",
            root_hi[0] - root_lo[0] > (unit_count - 1) * r.unit_spacing,
            details=f"span={root_hi[0] - root_lo[0]:.3f} expected>{(unit_count - 1) * r.unit_spacing:.3f}",
        )
    elif r.layout_mode == "radial_ring":
        root = model.get_part("drinking_station_core")
        root_lo, root_hi = ctx.part_world_aabb(root)
        ctx.check(
            "radial ring emits shared core/base",
            root_hi[0] - root_lo[0] > 2.0 * r.ring_radius,
            details=f"base_d={root_hi[0] - root_lo[0]:.3f} ring_r={r.ring_radius:.3f}",
        )
        # Centerpiece rises as a tall hero (column or umbrella mast).
        ctx.check(
            "radial centerpiece is a tall hero",
            root_hi[2] > 0.45,
            details=f"core_top_z={root_hi[2]:.3f} feature={r.center_feature}",
        )
        # Kinetic finial spins (REVOLUTE about Z) on the centerpiece top.
        finial = model.get_part("center_finial")
        fin_joint = model.get_articulation("core_to_finial")
        ctx.check(
            "center finial joint is revolute about Z",
            str(fin_joint.joint_type).lower().endswith("revolute")
            and abs(fin_joint.axis[2]) > 0.99,
            details=f"type={fin_joint.joint_type} axis={fin_joint.axis}",
        )
        fr_lo, fr_hi = ctx.part_world_aabb(finial)
        # Pose an angle that is NOT a multiple of the blade symmetry (90 deg)
        # so the 4-fold spinner does not map onto itself (which would be
        # AABB-invariant).
        with ctx.pose({fin_joint: 0.7}):
            fp_lo, fp_hi = ctx.part_world_aabb(finial)
        ctx.check(
            "spinning the finial registers (blades sweep)",
            abs((fp_hi[0] - fp_lo[0]) - (fr_hi[0] - fr_lo[0])) > 0.01
            or abs((fp_hi[1] - fp_lo[1]) - (fr_hi[1] - fr_lo[1])) > 0.01,
            details=(
                f"rest_xy=({fr_hi[0]-fr_lo[0]:.3f},{fr_hi[1]-fr_lo[1]:.3f}) "
                f"turned_xy=({fp_hi[0]-fp_lo[0]:.3f},{fp_hi[1]-fp_lo[1]:.3f})"
            ),
        )
        ctx.check(
            "finial sits at the centerpiece top",
            fr_lo[2] > root_hi[2] - 0.30,
            details=f"finial_min_z={fr_lo[2]:.3f} core_top={root_hi[2]:.3f}",
        )
        ctx.allow_overlap(
            finial, root,
            reason="The finial hub is captured on the centerpiece-top mounting post.",
        )
        ctx.expect_contact(finial, root, name="finial seated on centerpiece top")

        # Sun-umbrella: the canopy must shade the ring (overhang the stations)
        # and sit ABOVE the tallest station part (so it never clips them).
        if r.center_feature == "sun_umbrella":
            # tallest station part across all units (basin + swiveling spout)
            station_top = 0.0
            for p in prefixes:
                for nm in ("catch_basin", "water_spout"):
                    part = model.get_part(_prefixed(p, nm))
                    if part is not None:
                        station_top = max(station_top, ctx.part_world_aabb(part)[1][2])
            core_span = root_hi[0] - root_lo[0]
            ctx.check(
                "umbrella canopy shades past the ring stations",
                core_span > 2.0 * (r.ring_radius + 0.12),
                details=f"canopy_span={core_span:.3f} need>{2.0*(r.ring_radius+0.12):.3f}",
            )
            ctx.check(
                "umbrella is taller than the fountains",
                root_hi[2] > station_top + 0.10,
                details=f"umbrella_top={root_hi[2]:.3f} station_top={station_top:.3f}",
            )

    ctx.check(
        "layout emits requested unit count",
        sum(1 for p in prefixes if model.get_part(_prefixed(p, "catch_basin")) is not None) == unit_count,
        details=f"unit_count={unit_count}",
    )

    body_centers: list[tuple[float, float]] = []
    for idx, prefix in enumerate(prefixes):
        basin = model.get_part(_prefixed(prefix, "catch_basin"))
        faceplate = model.get_part(_prefixed(prefix, "front_faceplate"))
        fitting = model.get_part(_prefixed(prefix, "valve_fitting"))
        grille = model.get_part(_prefixed(prefix, "bottle_grille"))

        # ----- Body identity ------------------------------------------------ #
        if r.body_module == "pedestal_body":
            pylon = model.get_part(_prefixed(prefix, "pylon_body"))
            p_lo, p_hi = ctx.part_world_aabb(pylon)
            p_h = p_hi[2] - p_lo[2]
            p_w = min(p_hi[0] - p_lo[0], p_hi[1] - p_lo[1])
            ctx.check(f"{prefix}pylon stands on ground z~0", abs(p_lo[2]) < 0.04, details=f"min_z={p_lo[2]:.4f}")
            ctx.check(f"{prefix}pylon is tall (~1 m)", 0.95 < p_h < 1.10, details=f"h={p_h:.3f}")
            ctx.check(f"{prefix}pylon is slim", p_h > 4.0 * p_w, details=f"h={p_h:.3f} w={p_w:.3f}")
            body_part = pylon
        else:
            body = model.get_part(_prefixed(prefix, "body"))
            if r.layout_mode == "single_unit":
                plate = model.get_part("mounting_plate")
                pl_lo, pl_hi = ctx.part_world_aabb(plate)
                ctx.check("mount plate hugs the wall (y~0)", pl_lo[1] < 0.02, details=f"plate_min_y={pl_lo[1]:.4f}")
                ctx.check(
                    "mount plate centered ~0.9 m up",
                    0.55 < 0.5 * (pl_lo[2] + pl_hi[2]) < 1.2,
                    details=f"plate_cz={0.5 * (pl_lo[2] + pl_hi[2]):.3f}",
                )
            b_lo, b_hi = ctx.part_world_aabb(body)
            bw = b_hi[0] - b_lo[0]
            bd = b_hi[1] - b_lo[1]
            ctx.check(f"{prefix}wall body wider than deep", bw > bd, details=f"w={bw:.3f} d={bd:.3f}")
            body_part = body

        bp_lo, bp_hi = ctx.part_world_aabb(body_part)
        body_centers.append((0.5 * (bp_lo[0] + bp_hi[0]), 0.5 * (bp_lo[1] + bp_hi[1])))

        # ----- Basin and outlet -------------------------------------------- #
        ba_lo, ba_hi = ctx.part_world_aabb(basin)
        ctx.check(
            f"{prefix}basin sits at the top of the body",
            ba_lo[2] > bp_hi[2] - 0.10,
            details=f"basin_min_z={ba_lo[2]:.3f} body_top={bp_hi[2]:.3f}",
        )
        ctx.check(f"{prefix}basin has real height", (ba_hi[2] - ba_lo[2]) > 0.05, details=f"h={ba_hi[2] - ba_lo[2]:.3f}")
        if r.layout_mode != "radial_ring":
            basin_cy = 0.5 * (ba_lo[1] + ba_hi[1])
            ctx.check(f"{prefix}basin overhangs forward (+Y)", basin_cy > 0.03, details=f"basin_cy={basin_cy:.3f}")
        if r.basin_module == "round_basin":
            bx = ba_hi[0] - ba_lo[0]
            by = ba_hi[1] - ba_lo[1]
            ctx.check(f"{prefix}round basin is near-circular", abs(bx - by) < 0.06, details=f"x={bx:.3f} y={by:.3f}")
            ctx.check(f"{prefix}round basin diameter in real range", 0.14 < max(bx, by) < 0.30, details=f"d={max(bx, by):.3f}")

        # ----- Water spout: a swiveling pipe (REVOLUTE about the riser) ----- #
        spout = model.get_part(_prefixed(prefix, "water_spout"))
        sp_lo, sp_hi = ctx.part_world_aabb(spout)
        ctx.check(
            f"{prefix}water spout rises above the basin",
            sp_hi[2] > ba_hi[2] + 0.02,
            details=f"spout_top={sp_hi[2]:.3f} basin_top={ba_hi[2]:.3f}",
        )
        if r.basin_module == "bottle_filler":
            ctx.check(
                f"{prefix}bottle-filler arch rises well above basin",
                sp_hi[2] > ba_hi[2] + 0.05,
                details=f"spout_top={sp_hi[2]:.3f} basin_top={ba_hi[2]:.3f}",
            )
        spout_joint = model.get_articulation(_prefixed(prefix, "basin_to_spout"))
        ctx.check(
            f"{prefix}spout joint is revolute (not fixed)",
            str(spout_joint.joint_type).lower().endswith("revolute"),
            details=f"type={spout_joint.joint_type}",
        )
        ctx.check(
            f"{prefix}spout swivel axis is vertical (Z)",
            abs(spout_joint.axis[2]) > 0.99 and abs(spout_joint.axis[0]) < 0.01,
            details=f"axis={spout_joint.axis}",
        )
        rest_c = (0.5 * (sp_lo[0] + sp_hi[0]), 0.5 * (sp_lo[1] + sp_hi[1]))
        with ctx.pose({spout_joint: SPOUT_SWIVEL}):
            sw_lo, sw_hi = ctx.part_world_aabb(spout)
        sw_c = (0.5 * (sw_lo[0] + sw_hi[0]), 0.5 * (sw_lo[1] + sw_hi[1]))
        ctx.check(
            f"{prefix}swiveling the spout swings the outlet aside",
            math.hypot(sw_c[0] - rest_c[0], sw_c[1] - rest_c[1]) > 0.012,
            details=f"rest_c={tuple(round(v,3) for v in rest_c)} swiveled_c={tuple(round(v,3) for v in sw_c)}",
        )
        ctx.allow_overlap(
            spout,
            basin,
            reason="The spout riser flange seats into the basin valve mounting hub.",
        )
        ctx.expect_contact(spout, basin, name=f"{prefix}spout seated on basin hub")

        # ----- Faceplate and shelf ----------------------------------------- #
        f_lo, f_hi = ctx.part_world_aabb(faceplate)
        ctx.check(f"{prefix}faceplate is a tall front strip", (f_hi[2] - f_lo[2]) > 0.20, details=f"h={f_hi[2] - f_lo[2]:.3f}")
        g_lo, g_hi = ctx.part_world_aabb(grille)
        ctx.check(
            f"{prefix}grille shelf low on front",
            0.5 * (g_lo[2] + g_hi[2]) < 0.5 * (f_lo[2] + f_hi[2]),
            details=f"grille_z={0.5 * (g_lo[2] + g_hi[2]):.3f}",
        )

        # ----- Actuator ----------------------------------------------------- #
        if r.actuator_module == "foot_pedal":
            pedal = model.get_part(_prefixed(prefix, "foot_pedal"))
            pedal_joint = model.get_articulation(_prefixed(prefix, "pylon_to_pedal"))
            ctx.check(f"{prefix}pedal joint is revolute", str(pedal_joint.joint_type).lower().endswith("revolute"), details=f"type={pedal_joint.joint_type}")
            ctx.check(f"{prefix}pedal axis along X", abs(pedal_joint.axis[0]) > 0.99 and abs(pedal_joint.axis[1]) < 0.01, details=f"axis={pedal_joint.axis}")
            rest = ctx.part_world_aabb(pedal)
            with ctx.pose({pedal_joint: r.pedal_press}):
                pressed = ctx.part_world_aabb(pedal)
            ctx.check(
                f"{prefix}pressing pedal lowers front edge",
                pressed[0][2] < rest[0][2] + 1e-6,
                details=f"rest_minz={rest[0][2]:.4f} pressed_minz={pressed[0][2]:.4f}",
            )
            ctx.allow_overlap(
                model.get_part(_prefixed(prefix, "pylon_body")),
                pedal,
                reason="The foot-pedal pivot barrel is captured against the pylon front pivot boss.",
            )
        elif r.actuator_module == "rotary_knob":
            n = r.button_count
            knob_names = [_prefixed(prefix, "control_knob")] if n == 1 else [_prefixed(prefix, f"knob_{i}") for i in range(n)]
            joint_names = [_prefixed(prefix, "faceplate_to_knob")] if n == 1 else [_prefixed(prefix, f"faceplate_to_knob_{i}") for i in range(n)]
            for jn in joint_names:
                j = model.get_articulation(jn)
                ctx.check(f"{jn} is revolute", str(j.joint_type).lower().endswith("revolute"), details=f"type={j.joint_type}")
                ctx.check(f"{jn} turn axis along Y", abs(j.axis[1]) > 0.99 and abs(j.axis[2]) < 0.01, details=f"axis={j.axis}")
            first_knob = model.get_part(knob_names[0])
            first_joint = model.get_articulation(joint_names[0])
            kr_lo, kr_hi = ctx.part_world_aabb(first_knob)
            with ctx.pose({first_joint: RKNOB_SPIN}):
                kp_lo, kp_hi = ctx.part_world_aabb(first_knob)
            # Orientation-robust AABB-center displacement (see valve-knob note).
            kr_c = tuple(0.5 * (kr_lo[i] + kr_hi[i]) for i in range(3))
            kp_c = tuple(0.5 * (kp_lo[i] + kp_hi[i]) for i in range(3))
            ctx.check(
                f"{prefix}turning a knob registers (pointer sweeps)",
                math.dist(kr_c, kp_c) > 0.003,
                details=f"center_disp={math.dist(kr_c, kp_c):.4f}",
            )
            lim = first_joint.motion_limits
            ctx.check(
                f"{prefix}knob turn range realistic",
                lim is not None and lim.upper is not None and 0.3 < lim.upper <= 3.2,
                details=f"upper={None if lim is None else lim.upper}",
            )
            if n >= 2:
                k1 = model.get_part(knob_names[1])
                k1_rest = ctx.part_world_aabb(k1)
                with ctx.pose({first_joint: RKNOB_SPIN}):
                    k1_while = ctx.part_world_aabb(k1)
                ctx.check(
                    f"{prefix}knobs are independent",
                    abs(k1_while[0][0] - k1_rest[0][0]) < 1e-4 and abs(k1_while[1][2] - k1_rest[1][2]) < 1e-4,
                    details="neighbor knob must not move when one turns",
                )
                row = (n - 1) * r.knob_spacing
                ctx.check(f"{prefix}knob row fits faceplate", row + 2.0 * RKNOB_BOSS_R < FACE_X, details=f"row={row:.3f}")
            for kn in knob_names:
                knob = model.get_part(kn)
                ctx.allow_overlap(faceplate, knob, reason="The rotary-knob shaft is captured inside the faceplate mounting boss.")
                ctx.expect_overlap(knob, faceplate, axes="xz", min_overlap=0.006, name=f"{kn} captured by faceplate boss")
                ctx.allow_overlap(knob, body_part, reason="The knob shaft runs back through the faceplate boss toward the body valve.")
        else:
            n = r.button_count
            button_names = [_prefixed(prefix, "push_button")] if n == 1 else [_prefixed(prefix, f"button_{i}") for i in range(n)]
            joint_names = [_prefixed(prefix, "faceplate_to_button")] if n == 1 else [_prefixed(prefix, f"faceplate_to_button_{i}") for i in range(n)]
            for jn in joint_names:
                j = model.get_articulation(jn)
                ctx.check(f"{jn} is prismatic", str(j.joint_type).lower().endswith("prismatic"), details=f"type={j.joint_type}")
                ctx.check(f"{jn} press axis along Y", abs(j.axis[1]) > 0.99 and abs(j.axis[0]) < 0.01, details=f"axis={j.axis}")
            first_btn = model.get_part(button_names[0])
            first_joint = model.get_articulation(joint_names[0])
            rest = ctx.part_world_position(first_btn)
            with ctx.pose({first_joint: r.btn_travel}):
                pressed = ctx.part_world_position(first_btn)
            moved = (
                rest is not None
                and pressed is not None
                and math.hypot(pressed[0] - rest[0], pressed[1] - rest[1]) > 0.003
            )
            if r.layout_mode != "radial_ring":
                moved = moved and pressed[1] < rest[1] - 0.003
            ctx.check(
                f"{prefix}pressing a button moves it inward",
                moved,
                details=f"rest_y={rest[1]:.4f} pressed_y={pressed[1]:.4f}",
            )
            lim = first_joint.motion_limits
            ctx.check(
                f"{prefix}button travel short and realistic",
                lim is not None and lim.lower == 0.0 and lim.upper is not None and 0.003 < lim.upper < 0.020,
                details=f"travel={None if lim is None else lim.upper}",
            )
            if n >= 2:
                b1 = model.get_part(button_names[1])
                b1_rest = ctx.part_world_position(b1)
                with ctx.pose({first_joint: r.btn_travel}):
                    b1_while = ctx.part_world_position(b1)
                ctx.check(
                    f"{prefix}buttons are independent",
                    b1_rest is not None and b1_while is not None and abs(b1_while[1] - b1_rest[1]) < 1e-4,
                    details=f"b1_rest_y={b1_rest[1]:.4f} b1_while_y={b1_while[1]:.4f}",
                )
                row = (n - 1) * r.btn_spacing
                ctx.check(f"{prefix}button row fits faceplate", row + 2.0 * BTN_R < FACE_X, details=f"row={row:.3f}")
            for bn in button_names:
                button = model.get_part(bn)
                ctx.allow_overlap(faceplate, button, reason="The push-button stem is intentionally captured inside the faceplate mounting boss.")
                ctx.expect_overlap(button, faceplate, axes="xz", min_overlap=0.008, name=f"{bn} captured by faceplate boss")
                ctx.allow_overlap(button, body_part, reason="The plunger stem runs back through the faceplate into the body valve.")

        # ----- Mounting seats ---------------------------------------------- #
        ctx.allow_overlap(faceplate, body_part, reason="The steel faceplate is flush-mounted onto the body front.")
        ctx.expect_contact(faceplate, body_part, name=f"{prefix}faceplate seated on body front")
        ctx.allow_overlap(grille, faceplate, reason="The grille shelf bracket is tabbed into the faceplate front.")
        ctx.allow_overlap(grille, body_part, reason="The grille shelf bracket seats into the body front.")
        ctx.expect_contact(grille, faceplate, name=f"{prefix}grille bracket seated on faceplate")
        ctx.allow_overlap(faceplate, fitting, reason="The secondary valve fitting base is seated into its faceplate boss.")
        ctx.allow_overlap(body_part, fitting, reason="The valve fitting base seats through the faceplate into the body.")
        ctx.expect_contact(fitting, faceplate, name=f"{prefix}valve fitting seated on faceplate")

        # The secondary valve fitting must be a REAL turnable knob, not FIXED.
        fitting_joint = model.get_articulation(_prefixed(prefix, "faceplate_to_fitting"))
        ctx.check(
            f"{prefix}valve fitting is articulated (revolute, not fixed)",
            str(fitting_joint.joint_type).lower().endswith("revolute"),
            details=f"type={fitting_joint.joint_type}",
        )
        vr_lo, vr_hi = ctx.part_world_aabb(fitting)
        with ctx.pose({fitting_joint: KNOB_SPIN}):
            vp_lo, vp_hi = ctx.part_world_aabb(fitting)
        # Orientation-robust: the off-axis pointer shifts the AABB center when
        # turned (works for yawed radial units where the motion is along world Y).
        vr_c = tuple(0.5 * (vr_lo[i] + vr_hi[i]) for i in range(3))
        vp_c = tuple(0.5 * (vp_lo[i] + vp_hi[i]) for i in range(3))
        ctx.check(
            f"{prefix}turning the valve knob registers (pointer sweeps)",
            math.dist(vr_c, vp_c) > 0.003,
            details=f"center_disp={math.dist(vr_c, vp_c):.4f}",
        )

    if r.layout_mode == "linear_bank" and unit_count >= 2:
        xs = sorted(c[0] for c in body_centers)
        gaps = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
        ctx.check(
            "linear bank units are evenly spaced along X",
            all(abs(gap - r.unit_spacing) < 0.05 for gap in gaps),
            details=f"gaps={[round(g, 3) for g in gaps]} target={r.unit_spacing:.3f}",
        )
    if r.layout_mode == "radial_ring":
        radii = [math.hypot(x, y) for x, y in body_centers]
        ctx.check(
            "radial ring units sit around shared core",
            all(abs(radius - r.ring_radius) < 0.08 for radius in radii),
            details=f"radii={[round(radius, 3) for radius in radii]} target={r.ring_radius:.3f}",
        )

    # ----- Baseline gating checks (run AFTER all allowances are declared so
    #       the intentional captured/flush-mount overlaps are consulted). ----- #
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    return ctx.report()


__all__ = [
    "DrinkingFountainConfig",
    "ResolvedDrinkingFountainConfig",
    "config_from_seed",
    "resolve_config",
    "build_drinking_fountain",
    "build_seeded_drinking_fountain",
    "slot_choices_for_seed",
    "run_drinking_fountain_tests",
    "__modular__",
]
