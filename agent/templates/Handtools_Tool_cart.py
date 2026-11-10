# SPDX-License-Identifier: Apache-2.0

"""Rolling tool cart / mobile tool chest modular template.

NOTE on the slug: ``tool_cart`` here = a **wheeled rolling tool cart / mobile
tool chest** (a fused steel ``cabinet_frame`` carcass standing on four casters,
a fixed rear push handle, a stack of pull-out drawers, a side pegboard, and a
top tool tray), NOT a fixed shelf / shelving unit (no casters, no push handle),
NOT a desk / workbench (the body is a storage cabinet, not a work surface on
legs), NOT a flatbed / platform cart (it has cabinet storage, not a bare deck),
and NOT a rolling toolbox with a telescoping handle (4-caster pushed, not a
2-wheel drag box). Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Handtools_Tool_cart.md`` and the
``picture/Handtools/Tool cart`` 5-star pool (1 parent + 8 slot/multiplicity fork
variants), all synced under ``data/records/``.

Structure (pattern = ``multiplicity``; the drawer stack is the dominant
multiplicity axis): a single root ``cabinet_frame`` part holds the carcass
shell + side pegboard + top-deck geometry; everything else parents directly to
it as parallel children:

  * ``push_handle`` (FIXED — the inverted-U tubular handle + red grip sleeve at
    the top rear; always rigid).
  * N ``drawer_{i}`` parts (PRISMATIC +Y — each pulls straight out; this is the
    **multiplicity main axis**, N in [2, 9]).
  * Four casters under the floor (Slot B): all_swivel / mixed_swivel_fixed /
    brake_caster, each declaring its own swivel (CONTINUOUS +Z) + roll
    (CONTINUOUS +X) topology, with brake_caster adding a REVOLUTE +X foot brake
    per caster.

Slot A (``storage_module``) chooses the front storage face + top deck:
``drawer_stack`` (full N stack + recessed tool tray, the multiplicity carrier),
``cabinet_door`` (lower bay gets a left-hinged REVOLUTE +Z door; the stack caps
to 3 shallow drawers), ``open_shelf`` (lower bay gets a fixed divider + 2 fixed
inline shelf boards, Rule 1; stack caps to 3 shallow drawers), ``worktop`` (top
deck becomes a flat slab + lip, full N stack), ``rail_shelf`` (top deck gets a
fixed inline tubular guard rail, Rule 1; full N stack + steel rail material).

Compatibility (spec §9): ``cabinet_door`` / ``open_shelf`` consume the lower bay
so they always resolve the drawer stack to N=3 shallow drawers; ``drawer_stack``
/ ``worktop`` / ``rail_shelf`` keep the full sampled N. ``storage_module`` x
``caster`` are orthogonal. ``CAB_H`` grows with the stack so tall stacks (N=7..9)
never top out (n7 source raised CAB_H to 0.820; this template derives it).

All drawer-slide / caster-bearing / wheel-roll / door-hinge / brake-pivot /
handle-mount fits are captured geometry, so those joints omit ``MatingContract``
(grandfathered) and are guarded by the flat 0.015 m articulation-origin baseline
plus element-scoped ``allow_overlap`` / ``allow_isolated_part`` (mirroring each
source's run_tests block).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
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
    TireCarcass,
    TireGeometry,
    TireShoulder,
    TireSidewall,
    TireTread,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

StorageModule = Literal[
    "drawer_stack",
    "cabinet_door",
    "open_shelf",
    "worktop",
    "rail_shelf",
]
Caster = Literal["all_swivel", "mixed_swivel_fixed", "brake_caster"]
PaletteStyle = Literal[
    "red_black_steel",
    "blue_steel",
    "safety_yellow",
    "graphite_chrome",
    "hi_vis_orange",
]

STORAGE_MODULES: tuple[StorageModule, ...] = (
    "drawer_stack",
    "cabinet_door",
    "open_shelf",
    "worktop",
    "rail_shelf",
)
CASTERS: tuple[Caster, ...] = ("all_swivel", "mixed_swivel_fixed", "brake_caster")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "red_black_steel",
    "blue_steel",
    "safety_yellow",
    "graphite_chrome",
    "hi_vis_orange",
)

# Storage modules whose stack collapses onto the upper 3 shallow drawers because
# the lower bay is consumed by the door / shelves (spec §9 compatibility #1).
_LOWER_BAY_MODULES: tuple[StorageModule, ...] = ("cabinet_door", "open_shelf")
# Fixed shallow stack used by the lower-bay modules.
_BAY_DRAWER_COUNT = 3
_BAY_SHALLOW_H = 0.072

# drawer_count multiplicity domain (spec §8). Weighted small: N=3/4/5 high,
# 6/7 common, 8/9 long tail, 2 lower bound.
N_DRAWER_MIN, N_DRAWER_MAX = 2, 9
_DRAWER_COUNT_CHOICES = (2, 3, 4, 5, 6, 7, 8, 9)
_DRAWER_COUNT_WEIGHTS = (0.08, 0.20, 0.20, 0.18, 0.13, 0.10, 0.06, 0.05)

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). From the parent (1e586d5a) carcass.
# ---------------------------------------------------------------------------
_CAB_W = 0.560  # cabinet width (X)
_CAB_D = 0.420  # cabinet depth (Y)
WALL = 0.012  # carcass wall thickness
BASE_BAND = 0.055  # solid toe-kick band at the bottom, below the drawers
TOP_MARGIN = 0.006  # solid band under the top trim, above the top drawer

TOP_TRIM_H = 0.022  # black top trim band above the drawer stack
TRAY_LIP = 0.020  # raised lip around the top tray / worktop
TRAY_WALL = 0.010

DRAWER_FACE_T = 0.018  # red drawer-front panel thickness (Y)
DRAWER_GAP = 0.006  # reveal gap between adjacent drawer faces
SIDE_REVEAL = 0.014  # gap from carcass side wall to drawer face edge
_BASE_DRAWER_TRAVEL = 0.300  # pull-out travel along +Y
DRAWER_CLEAR = 0.004  # sliding clearance per side inside the opening

# Pegboard (left wall, -X face)
PEG_W = 0.300
PEG_H = 0.340
PEG_T = 0.006
PEG_HOLE_D = 0.012
PEG_PITCH = 0.030

# Push handle
HANDLE_TUBE_R = 0.013
HANDLE_RISE = 0.150
HANDLE_REACH = 0.110
GRIP_R = 0.017
GRIP_LEN = 0.230

# Casters (simple — all_swivel / mixed)
SIMPLE_WHEEL_R = 0.052
SIMPLE_WHEEL_W = 0.034
SIMPLE_FORK_DROP = 0.030
_BASE_CASTER_GAP = 0.150
CASTER_INSET_X = 0.070
CASTER_INSET_Y = 0.060

# Brake caster (larger pneumatic tires)
BRAKE_WHEEL_R = 0.076
BRAKE_WHEEL_W = 0.050
BRAKE_RIM_R = 0.050
BRAKE_HUB_R = 0.020
BRAKE_FORK_DROP = 0.036
BRAKE_INSET_X = 0.080
BRAKE_INSET_Y = 0.070
_BRAKE_CASTER_GAP = 0.190
BRAKE_LEVER_LEN = 0.065
BRAKE_LEVER_W = 0.020
BRAKE_LEVER_T = 0.006
BRAKE_PIVOT_R = 0.006
_BASE_BRAKE_ANGLE = 0.55

# Open-shelf bay
SHELF_T = 0.015
SHELF_COUNT = 2
SHELF_FRONT_LIP = 0.008
BAY_DIVIDER_T = 0.012

# Rail shelf guard rail
RAIL_SHELF_T = 0.006
GUARD_RAIL_R = 0.006
GUARD_RAIL_H = 0.055
GUARD_RAIL_INSET = 0.022
GUARD_POST_EXTRA = 0.008

# Cabinet door
_BASE_DOOR_OPEN_ANGLE = 1.50

# ---------------------------------------------------------------------------
# Palettes (5 colorways from the 9 source records, spec §7).
# Keys: drawer, shell, accent (handle/fork), wheel, grip, deck (worktop/rail).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "red_black_steel": {
        "drawer": (0.74, 0.07, 0.07, 1.0),
        "shell": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.16, 0.16, 0.18, 1.0),
        "wheel": (0.09, 0.09, 0.10, 1.0),
        "grip": (0.70, 0.10, 0.10, 1.0),
        "deck": (0.55, 0.56, 0.58, 1.0),
    },
    "blue_steel": {
        "drawer": (0.13, 0.24, 0.42, 1.0),
        "shell": (0.18, 0.19, 0.22, 1.0),
        "accent": (0.72, 0.74, 0.78, 1.0),
        "wheel": (0.08, 0.08, 0.09, 1.0),
        "grip": (0.16, 0.17, 0.20, 1.0),
        "deck": (0.66, 0.68, 0.72, 1.0),
    },
    "safety_yellow": {
        "drawer": (0.86, 0.72, 0.10, 1.0),
        "shell": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.72, 0.74, 0.78, 1.0),
        "wheel": (0.08, 0.08, 0.09, 1.0),
        "grip": (0.12, 0.12, 0.13, 1.0),
        "deck": (0.58, 0.59, 0.62, 1.0),
    },
    "graphite_chrome": {
        "drawer": (0.22, 0.23, 0.25, 1.0),
        "shell": (0.15, 0.15, 0.17, 1.0),
        "accent": (0.72, 0.74, 0.78, 1.0),
        "wheel": (0.08, 0.08, 0.09, 1.0),
        "grip": (0.55, 0.12, 0.12, 1.0),
        "deck": (0.70, 0.72, 0.76, 1.0),
    },
    "hi_vis_orange": {
        "drawer": (0.88, 0.36, 0.06, 1.0),
        "shell": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.30, 0.31, 0.34, 1.0),
        "wheel": (0.09, 0.09, 0.10, 1.0),
        "grip": (0.12, 0.12, 0.13, 1.0),
        "deck": (0.62, 0.63, 0.66, 1.0),
    },
}


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class ToolCartConfig:
    storage_module: StorageModule | None = None
    caster: Caster | None = None
    drawer_count: int | None = None
    palette_style: PaletteStyle = "red_black_steel"
    cab_width_scale: float = 1.0
    cab_depth_scale: float = 1.0
    drawer_height_scale: float = 1.0
    drawer_travel_scale: float = 1.0
    door_open_angle_scale: float = 1.0
    brake_angle_scale: float = 1.0
    caster_gap_scale: float = 1.0
    name: str = "tool_cart"


@dataclass(frozen=True)
class ResolvedToolCartConfig:
    storage_module: StorageModule
    caster: Caster
    drawer_count: int  # resolved (capped to 3 for lower-bay modules)
    palette_style: PaletteStyle
    # Derived / scaled geometry.
    cab_w: float
    cab_d: float
    cab_h: float
    drawer_heights: tuple[float, ...]
    drawer_travel: float
    door_open_angle: float  # meaningful only for cabinet_door
    brake_angle: float  # meaningful only for brake_caster
    caster_gap: float
    name: str

    @property
    def floor_z(self) -> float:
        return self.caster_gap


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> ToolCartConfig:
    rng = random.Random(seed)
    storage = rng.choice(STORAGE_MODULES)
    caster = rng.choice(CASTERS)
    if storage in _LOWER_BAY_MODULES:
        drawer_count = _BAY_DRAWER_COUNT
    else:
        drawer_count = rng.choices(
            _DRAWER_COUNT_CHOICES, weights=_DRAWER_COUNT_WEIGHTS, k=1
        )[0]
    return ToolCartConfig(
        storage_module=storage,
        caster=caster,
        drawer_count=drawer_count,
        palette_style=rng.choice(PALETTE_STYLES),
        cab_width_scale=round(rng.uniform(0.90, 1.12), 4),
        cab_depth_scale=round(rng.uniform(0.90, 1.12), 4),
        drawer_height_scale=round(rng.uniform(0.85, 1.15), 4),
        drawer_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        door_open_angle_scale=round(rng.uniform(0.85, 1.10), 4),
        brake_angle_scale=round(rng.uniform(0.85, 1.10), 4),
        caster_gap_scale=round(rng.uniform(0.92, 1.10), 4),
        name=f"seeded_tool_cart_{seed}",
    )


def _drawer_heights_for(
    storage: StorageModule, drawer_count: int, height_scale: float
) -> tuple[float, ...]:
    """Per-drawer FACE heights, top -> bottom.

    drawer_stack / worktop / rail_shelf keep the full N stack: the parent
    baseline (N=5) reads as three shallow + two deep; other N use a uniform
    height that fills the available band (n3 uniform 0.150, n7 uniform 0.098).
    cabinet_door / open_shelf use 3 shallow drawers (the lower bay is consumed).
    """
    if storage in _LOWER_BAY_MODULES:
        return tuple([_BAY_SHALLOW_H * height_scale] * _BAY_DRAWER_COUNT)
    if drawer_count == 5:
        # Parent baseline: three shallow + two deep.
        base = (0.072, 0.072, 0.072, 0.150, 0.150)
        return tuple(h * height_scale for h in base)
    # Uniform stack scaled to fit the band; reference points: n3->0.150,
    # n7->0.098. Linearly interpolate a sensible uniform face height by N.
    uniform = 0.450 / drawer_count  # ~0.150 @ N=3, ~0.064 @ N=7
    uniform = _clamp(uniform, 0.060, 0.165)
    return tuple([uniform * height_scale] * drawer_count)


def resolve_config(config: ToolCartConfig | None = None) -> ResolvedToolCartConfig:
    cfg = config or ToolCartConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    storage = _pick(cfg.storage_module, STORAGE_MODULES)
    caster = _pick(cfg.caster, CASTERS)

    # --- drawer_count: clamp + compatibility (lower-bay -> 3). ---
    drawer_count = (
        int(cfg.drawer_count) if cfg.drawer_count is not None else 5
    )
    drawer_count = int(_clamp(drawer_count, N_DRAWER_MIN, N_DRAWER_MAX))
    if storage in _LOWER_BAY_MODULES:
        drawer_count = _BAY_DRAWER_COUNT

    # --- continuous scales (clamped to declared ranges). ---
    width_scale = _clamp(cfg.cab_width_scale, 0.90, 1.12)
    depth_scale = _clamp(cfg.cab_depth_scale, 0.90, 1.12)
    height_scale = _clamp(cfg.drawer_height_scale, 0.85, 1.15)
    travel_scale = _clamp(cfg.drawer_travel_scale, 0.85, 1.10)
    door_angle_scale = _clamp(cfg.door_open_angle_scale, 0.85, 1.10)
    brake_angle_scale = _clamp(cfg.brake_angle_scale, 0.85, 1.10)
    gap_scale = _clamp(cfg.caster_gap_scale, 0.92, 1.10)

    cab_w = _CAB_W * width_scale
    cab_d = _CAB_D * depth_scale

    drawer_heights = _drawer_heights_for(storage, drawer_count, height_scale)

    # --- CAB_H derived from the stack so it never tops out (n7 raised it). ---
    # Available band must hold sum(heights) + (N) gaps + a divider/bay below for
    # the lower-bay modules. Band = CAB_H - WALL - TOP_MARGIN - BASE_BAND.
    n = len(drawer_heights)
    stack_h = sum(drawer_heights) + (n + 1) * DRAWER_GAP
    if storage == "cabinet_door":
        # Door covers two deep-drawer heights below the 3 shallow drawers.
        stack_h += 2 * 0.150 + 2 * DRAWER_GAP
    elif storage == "open_shelf":
        # Open bay below the 3 shallow drawers.
        stack_h += 0.220 + BAY_DIVIDER_T
    needed_h = stack_h + WALL + TOP_MARGIN + BASE_BAND
    cab_h = max(0.640, needed_h)

    # --- drawer travel: clamp below box depth so the box never exits the bore. ---
    box_depth = cab_d - WALL - 0.030
    drawer_travel = _BASE_DRAWER_TRAVEL * travel_scale
    drawer_travel = min(drawer_travel, 0.95 * box_depth)

    door_open_angle = min(_BASE_DOOR_OPEN_ANGLE * door_angle_scale, 0.95 * math.pi / 2 * 1.15)
    brake_angle = _BASE_BRAKE_ANGLE * brake_angle_scale

    base_gap = _BRAKE_CASTER_GAP if caster == "brake_caster" else _BASE_CASTER_GAP
    caster_gap = base_gap * gap_scale

    return ResolvedToolCartConfig(
        storage_module=storage,
        caster=caster,
        drawer_count=drawer_count,
        palette_style=palette_style,
        cab_w=cab_w,
        cab_d=cab_d,
        cab_h=cab_h,
        drawer_heights=drawer_heights,
        drawer_travel=drawer_travel,
        door_open_angle=door_open_angle,
        brake_angle=brake_angle,
        caster_gap=caster_gap,
        name=cfg.name or "tool_cart",
    )


def with_overrides(config: ToolCartConfig, **kwargs: object) -> ToolCartConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ToolCartConfig | ResolvedToolCartConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedToolCartConfig) else resolve_config(config)
    return (
        ("storage_module", r.storage_module),
        ("caster", r.caster),
        ("drawer_count", f"n{r.drawer_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Derived layout helpers (depend on resolved config r)
# ===========================================================================
def _drawer_band_top(r: ResolvedToolCartConfig) -> float:
    """Z of the top edge of the drawer stack."""
    return r.floor_z + r.cab_h - WALL - TOP_MARGIN


def _drawer_face_centers(r: ResolvedToolCartConfig) -> list[float]:
    """World Z center of each drawer face, top -> bottom."""
    top = _drawer_band_top(r)
    centers: list[float] = []
    z = top
    for h in r.drawer_heights:
        z -= DRAWER_GAP
        centers.append(z - h / 2.0)
        z -= h
    return centers


def _door_opening(r: ResolvedToolCartConfig) -> dict[str, float]:
    """Lower-bay door opening bounds for cabinet_door."""
    centers = _drawer_face_centers(r)
    last_h = r.drawer_heights[-1]
    last_bottom = centers[-1] - last_h / 2.0
    door_top = last_bottom - DRAWER_GAP
    door_bottom = r.floor_z + BASE_BAND + DRAWER_GAP
    door_cz = (door_top + door_bottom) / 2.0
    return {
        "top": door_top,
        "bottom": door_bottom,
        "center_z": door_cz,
        "height": door_top - door_bottom,
    }


def _bay_top_z(r: ResolvedToolCartConfig) -> float:
    centers = _drawer_face_centers(r)
    return centers[-1] - r.drawer_heights[-1] / 2.0 - DRAWER_GAP


def _bay_bot_z(r: ResolvedToolCartConfig) -> float:
    return r.floor_z + BASE_BAND


def _shelf_z_positions(r: ResolvedToolCartConfig) -> list[float]:
    z_top = _bay_top_z(r) - BAY_DIVIDER_T
    z_bot = _bay_bot_z(r)
    span = z_top - z_bot
    positions: list[float] = []
    for i in range(SHELF_COUNT):
        frac = (i + 1.0) / (SHELF_COUNT + 1.0)
        positions.append(z_bot + frac * span)
    return positions


def _axle_z(r: ResolvedToolCartConfig) -> float:
    """Axle height in the fork-local frame so the wheel lands on z=0."""
    wheel_r = BRAKE_WHEEL_R if r.caster == "brake_caster" else SIMPLE_WHEEL_R
    return -r.caster_gap + wheel_r


def _caster_positions(r: ResolvedToolCartConfig) -> list[tuple[float, float]]:
    inset_x = BRAKE_INSET_X if r.caster == "brake_caster" else CASTER_INSET_X
    inset_y = BRAKE_INSET_Y if r.caster == "brake_caster" else CASTER_INSET_Y
    return [
        (sx * (r.cab_w / 2.0 - inset_x), sy * (r.cab_d / 2.0 - inset_y))
        for sx in (-1.0, 1.0)
        for sy in (-1.0, 1.0)
    ]


# Handle geometry helpers (carcass frame).
def _handle_consts(r: ResolvedToolCartConfig) -> dict[str, float]:
    trim_top = r.floor_z + r.cab_h + TOP_TRIM_H
    z_base = trim_top + TRAY_LIP + 0.004
    return {
        "z_base": z_base,
        "y_back": -r.cab_d / 2.0 + 0.020,
        # Inverted-U push handle centered on the cabinet width (0.170 span).
        "x_off": 0.170 / 2.0,
        "x_in": -0.170 / 2.0,
        "z_top": z_base + HANDLE_RISE,
        "y_grip": -r.cab_d / 2.0 - HANDLE_REACH,
    }


# ===========================================================================
# Carcass + pegboard + top deck geometry
# ===========================================================================
def _carcass_base(r: ResolvedToolCartConfig):
    """Hollow black carcass box open at the front (+Y) + top trim band, as one
    fused solid. Returns the cadquery workplane (top deck added separately)."""
    z0 = r.floor_z
    z1 = r.floor_z + r.cab_h

    body = cq.Workplane("XY", origin=(0, 0, (z0 + z1) / 2.0)).box(r.cab_w, r.cab_d, r.cab_h)
    try:
        body = body.edges("|Z").fillet(0.010)
    except Exception:
        pass

    cav_z0 = z0 + BASE_BAND
    cav_z1 = z1 - WALL
    cavity = cq.Workplane(
        "XY", origin=(0, WALL, (cav_z0 + cav_z1) / 2.0)
    ).box(r.cab_w - 2 * WALL, r.cab_d, cav_z1 - cav_z0)
    body = body.cut(cavity)

    trim_overlap = 0.020
    trim_h = TOP_TRIM_H + trim_overlap
    trim_z = z1 + TOP_TRIM_H / 2.0 - trim_overlap / 2.0
    trim = cq.Workplane("XY", origin=(0, 0, trim_z)).box(
        r.cab_w + 0.012, r.cab_d + 0.012, trim_h
    )
    try:
        trim = trim.edges("|Z").fillet(0.012)
    except Exception:
        pass
    return body.union(trim)


def _top_tray(r: ResolvedToolCartConfig, body):
    """Recessed molded tool tray (drawer_stack / cabinet_door / open_shelf)."""
    z1 = r.floor_z + r.cab_h
    tray_top = z1 + TOP_TRIM_H
    tray_overlap = 0.012
    tray_h = TRAY_LIP + tray_overlap
    tray_outer = cq.Workplane(
        "XY", origin=(0, 0, tray_top + TRAY_LIP / 2.0 - tray_overlap / 2.0)
    ).box(r.cab_w + 0.010, r.cab_d + 0.010, tray_h)
    try:
        tray_outer = tray_outer.edges("|Z").fillet(0.012)
    except Exception:
        pass
    basin = cq.Workplane("XY", origin=(0, 0, tray_top + TRAY_LIP)).box(
        r.cab_w - 0.040, r.cab_d - 0.040, 2 * (TRAY_LIP - TRAY_WALL)
    )
    tray_outer = tray_outer.cut(basin)
    for sx in (-0.14, 0.0, 0.14):
        pocket = (
            cq.Workplane("XY", origin=(sx, 0.04, tray_top + TRAY_WALL))
            .circle(0.016)
            .extrude(2 * TRAY_LIP)
        )
        tray_outer = tray_outer.cut(pocket)
    return body.union(tray_outer)


def _top_worktop(r: ResolvedToolCartConfig, body):
    """Flat solid worktop slab + thin perimeter lip (worktop module)."""
    z1 = r.floor_z + r.cab_h
    worktop_top = z1 + TOP_TRIM_H
    slab_t = TRAY_WALL
    lip_h = TRAY_LIP
    lip_w = 0.008
    slab_overlap = 0.012
    slab = cq.Workplane(
        "XY", origin=(0, 0, worktop_top - slab_t / 2.0 + slab_overlap / 2.0)
    ).box(r.cab_w + 0.010, r.cab_d + 0.010, slab_t + slab_overlap)
    try:
        slab = slab.edges("|Z").fillet(0.012)
    except Exception:
        pass
    lip_outer = cq.Workplane("XY", origin=(0, 0, worktop_top + lip_h / 2.0)).box(
        r.cab_w + 0.010, r.cab_d + 0.010, lip_h
    )
    try:
        lip_outer = lip_outer.edges("|Z").fillet(0.012)
    except Exception:
        pass
    lip_inner = cq.Workplane("XY", origin=(0, 0, worktop_top + lip_h / 2.0 + 0.001)).box(
        r.cab_w + 0.010 - 2 * lip_w, r.cab_d + 0.010 - 2 * lip_w, lip_h + 0.002
    )
    lip = lip_outer.cut(lip_inner)
    return body.union(slab.union(lip))


def _top_rail_deck(r: ResolvedToolCartConfig, body):
    """Flat utility shelf slab on top (rail_shelf; guard rail is a separate
    inline visual)."""
    z1 = r.floor_z + r.cab_h
    deck_top = z1 + TOP_TRIM_H
    slab_t = RAIL_SHELF_T
    slab_overlap = 0.012
    slab = cq.Workplane(
        "XY", origin=(0, 0, deck_top + slab_t / 2.0 - slab_overlap / 2.0)
    ).box(r.cab_w + 0.010, r.cab_d + 0.010, slab_t + slab_overlap)
    try:
        slab = slab.edges("|Z").fillet(0.012)
    except Exception:
        pass
    return body.union(slab)


def _carcass_mesh(r: ResolvedToolCartConfig, assets):
    body = _carcass_base(r)
    if r.storage_module == "worktop":
        body = _top_worktop(r, body)
    elif r.storage_module == "rail_shelf":
        body = _top_rail_deck(r, body)
    else:
        body = _top_tray(r, body)
    return mesh_from_cadquery(body, "carcass", assets=assets)


def _pegboard_mesh(r: ResolvedToolCartConfig, assets):
    x_face = -r.cab_w / 2.0 - PEG_T / 2.0 + 0.004
    z_c = r.floor_z + r.cab_h * 0.55
    peg_w = min(PEG_W, r.cab_d - 0.060)
    peg_h = min(PEG_H, r.cab_h - 0.160)
    plate = cq.Workplane("YZ", origin=(x_face, 0.0, z_c)).box(peg_w, peg_h, PEG_T)
    nyy = max(2, int(peg_w // PEG_PITCH))
    nzz = max(2, int(peg_h // PEG_PITCH))
    y0 = -((nyy - 1) * PEG_PITCH) / 2.0
    zz0 = -((nzz - 1) * PEG_PITCH) / 2.0
    for iy in range(nyy):
        for iz in range(nzz):
            yy = y0 + iy * PEG_PITCH
            zz = zz0 + iz * PEG_PITCH
            hole = (
                cq.Workplane("YZ", origin=(x_face, yy, z_c + zz))
                .circle(PEG_HOLE_D / 2.0)
                .extrude(2 * PEG_T, both=True)
            )
            plate = plate.cut(hole)
    return mesh_from_cadquery(plate, "pegboard", assets=assets)


def _drawer_mesh(r: ResolvedToolCartConfig, index: int, assets):
    """One drawer: red front face + finger pull + black hollow box. Authored so
    the drawer-local origin (0,0,0) sits on a real captured side-mount point:
    the front-face outer plane, slightly inboard from the left face edge, where
    the prismatic joint is anchored onto the carcass side rim. The box extends
    back in -Y. This keeps (0,0,0) inside the drawer geometry so the
    articulation-origin baseline passes."""
    h = r.drawer_heights[index]
    face_w = r.cab_w - 2 * SIDE_REVEAL
    box_w = face_w - 2 * DRAWER_CLEAR
    box_h = h - 2 * DRAWER_CLEAR
    box_depth = r.cab_d - WALL - 0.030
    guide_offset_x = SIDE_REVEAL - WALL / 2.0

    # Front face: outer surface at y=0, body extends to y=-DRAWER_FACE_T.
    face_x_c = face_w / 2.0 + guide_offset_x
    face_y = -DRAWER_FACE_T / 2.0
    face = cq.Workplane("XY", origin=(face_x_c, face_y, 0)).box(
        face_w, DRAWER_FACE_T, h
    )
    try:
        face = face.edges("|Y").fillet(0.006)
    except Exception:
        pass
    pull = cq.Workplane(
        "XY", origin=(face_x_c, face_y + 0.002, h / 2.0 - 0.012)
    ).box(
        face_w * 0.62, DRAWER_FACE_T, 0.016
    )
    face = face.cut(pull)

    # Box extends back into the cabinet (-Y) from behind the face.
    box_x_c = face_w / 2.0 + guide_offset_x
    box_y_c = -DRAWER_FACE_T - box_depth / 2.0
    box_outer = cq.Workplane("XY", origin=(box_x_c, box_y_c, 0)).box(
        box_w, box_depth, box_h
    )
    box = box_outer.faces(">Z").shell(-0.005)

    # Hidden left slide-guide lug captured behind the carcass side rim. This
    # replaces the visible front cross-bar while keeping a real anchor volume
    # at the prismatic joint origin. The lug reaches into the face (2mm) so the
    # drawer mesh stays one connected body.
    guide_h = min(max(h * 0.42, 0.032), h - 0.010)
    guide_w = max(0.012, 2 * guide_offset_x + 0.004)
    guide = cq.Workplane("XY", origin=(0.0, -DRAWER_FACE_T / 2.0, 0.0)).box(
        guide_w, DRAWER_FACE_T, guide_h
    )
    return mesh_from_cadquery(face.union(box).union(guide), f"drawer_{index}", assets=assets)


def _cabinet_door_mesh(r: ResolvedToolCartConfig, assets):
    """Cabinet door panel authored in a hinge-line local frame (part frame at
    the left edge, vertical center; panel extends +X, front face +Y)."""
    info = _door_opening(r)
    face_w = r.cab_w - 2 * SIDE_REVEAL
    face_h = info["height"]

    face = cq.Workplane("XY", origin=(face_w / 2.0, 0.0, 0.0)).box(
        face_w, DRAWER_FACE_T, face_h
    )
    try:
        face = face.edges("|Y").fillet(0.006)
    except Exception:
        pass
    pull = cq.Workplane(
        "XY", origin=(face_w * 0.65, 0.002, face_h / 2.0 - 0.020)
    ).box(0.080, DRAWER_FACE_T, 0.018)
    face = face.cut(pull)

    handle_x = face_w - 0.040
    handle_bracket = cq.Workplane(
        "XY", origin=(handle_x, DRAWER_FACE_T / 2.0 + 0.006, 0.0)
    ).box(0.020, 0.012, min(0.070, face_h * 0.6))
    try:
        handle_bracket = handle_bracket.edges("|Y").fillet(0.004)
    except Exception:
        pass
    face = face.union(handle_bracket)

    barrel_r = 0.008
    barrel_h = 0.030
    for frac in (0.30, 0.70):
        bz = -face_h / 2.0 + frac * face_h
        barrel = cq.Workplane("XY", origin=(0.0, 0.0, bz - barrel_h / 2.0)).circle(
            barrel_r
        ).extrude(barrel_h)
        face = face.union(barrel)
    return mesh_from_cadquery(face, "cabinet_door", assets=assets)


def _shelf_mesh(r: ResolvedToolCartConfig, index: int, assets):
    """One fixed shelf board for the open bay (inline visual, Rule 1)."""
    wall_mount = 0.006
    board_w = r.cab_w - 2 * WALL + 2 * wall_mount
    board_d = r.cab_d - WALL - 0.004
    board_y_c = -WALL / 2.0 + 0.002
    board = cq.Workplane("XY", origin=(0, board_y_c, 0)).box(board_w, board_d, SHELF_T)
    lip_w = r.cab_w - 2 * WALL - 0.010
    lip = cq.Workplane(
        "XY",
        origin=(
            0,
            board_y_c + board_d / 2.0 - SHELF_FRONT_LIP / 2.0,
            SHELF_T / 2.0 + SHELF_FRONT_LIP / 2.0,
        ),
    ).box(lip_w, SHELF_FRONT_LIP, SHELF_FRONT_LIP)
    return mesh_from_cadquery(board.union(lip), f"shelf_{index}", assets=assets)


def _bay_divider_mesh(r: ResolvedToolCartConfig, assets):
    """Horizontal divider rail between the drawer stack and the open bay."""
    inner_w = r.cab_w - 2 * WALL
    depth = 0.030
    z_mid = _bay_top_z(r) - BAY_DIVIDER_T / 2.0
    y_mid = r.cab_d / 2.0 - depth / 2.0
    rail = cq.Workplane("XY", origin=(0, y_mid, z_mid)).box(inner_w, depth, BAY_DIVIDER_T)
    return mesh_from_cadquery(rail, "bay_divider", assets=assets)


def _guard_rail_mesh(r: ResolvedToolCartConfig, assets):
    """Tubular perimeter guard rail on the rail_shelf deck (inline, Rule 1)."""
    rail_r = GUARD_RAIL_R
    rail_h = GUARD_RAIL_H
    inset = GUARD_RAIL_INSET
    shelf_top = r.floor_z + r.cab_h + TOP_TRIM_H + RAIL_SHELF_T

    hw = (r.cab_w + 0.010) / 2.0 - inset
    hd = (r.cab_d + 0.010) / 2.0 - inset

    z_post_top = shelf_top + rail_h
    z_post_bot = shelf_top - GUARD_POST_EXTRA
    z_mid = shelf_top + rail_h * 0.45

    corners = [(-hw, -hd), (-hw, hd), (hw, hd), (hw, -hd)]
    result = None
    for cx, cy in corners:
        post = (
            cq.Workplane("XY", origin=(cx, cy, (z_post_bot + z_post_top) / 2.0))
            .circle(rail_r)
            .extrude((z_post_top - z_post_bot) / 2.0, both=True)
        )
        foot = (
            cq.Workplane("XY", origin=(cx, cy, shelf_top - 0.001))
            .circle(rail_r + 0.004)
            .extrude(0.004)
        )
        post = post.union(foot)
        result = post if result is None else result.union(post)

    for z_bar in (z_post_top, z_mid):
        for i in range(4):
            c0 = corners[i]
            c1 = corners[(i + 1) % 4]
            dx = c1[0] - c0[0]
            dy = c1[1] - c0[1]
            length = math.sqrt(dx * dx + dy * dy)
            mx = (c0[0] + c1[0]) / 2.0
            my = (c0[1] + c1[1]) / 2.0
            if abs(dx) > abs(dy):
                bar = (
                    cq.Workplane("YZ", origin=(mx, my, z_bar))
                    .circle(rail_r)
                    .extrude(length / 2.0, both=True)
                )
            else:
                bar = (
                    cq.Workplane("XZ", origin=(mx, my, z_bar))
                    .circle(rail_r)
                    .extrude(length / 2.0, both=True)
                )
            result = result.union(bar)

    for cx, cy in corners:
        cap = cq.Workplane("XY", origin=(cx, cy, z_post_top)).sphere(rail_r + 0.001)
        result = result.union(cap)
    return mesh_from_cadquery(result, "guard_rail", assets=assets)


def _handle_mount(r: ResolvedToolCartConfig) -> tuple[float, float, float]:
    """Real FIXED-joint mount point: the right upright boss seated in the top
    trim band. The handle geometry is authored relative to this point so the
    handle-local origin (0,0,0) sits inside the mounting boss."""
    c = _handle_consts(r)
    return (c["x_off"], c["y_back"], c["z_base"])


def _handle_mesh(r: ResolvedToolCartConfig, assets):
    """Dark tubular push handle (inverted-U) + red grip sleeve, authored in the
    carcass frame then shifted so the handle-local origin coincides with the
    right upright boss mount. Returns (frame_mesh, grip_mesh)."""
    c = _handle_consts(r)
    z_base, y_back = c["z_base"], c["y_back"]
    x_off, x_in = c["x_off"], c["x_in"]
    z_top, y_grip = c["z_top"], c["y_grip"]
    mx, my, mz = _handle_mount(r)

    pts = [
        (x_off, y_back, z_base),
        (x_off, y_back, z_base + 0.050),
        (x_off, (y_back + y_grip) / 2.0, z_top - 0.012),
        (x_off, y_grip, z_top),
        (x_in, y_grip, z_top),
        (x_in, (y_back + y_grip) / 2.0, z_top - 0.012),
        (x_in, y_back, z_base + 0.050),
        (x_in, y_back, z_base),
    ]
    wire_pts = [cq.Vector(*p) for p in pts]
    spline_edge = cq.Edge.makeSpline(wire_pts)
    wire = cq.Wire.assembleEdges([spline_edge])
    start = wire_pts[0]
    tan = spline_edge.tangentAt(0.0)
    tube = (
        cq.Workplane(cq.Plane(origin=start.toTuple(), normal=tan.toTuple()))
        .circle(HANDLE_TUBE_R)
        .sweep(cq.Workplane(obj=wire), transition="round")
    )
    for sx in (x_off, x_in):
        boss = (
            cq.Workplane("XY", origin=(sx, y_back, z_base - 0.014))
            .circle(HANDLE_TUBE_R + 0.004)
            .extrude(0.028)
        )
        tube = tube.union(boss)
    # Shift into the handle-local frame so (0,0,0) sits inside the right boss.
    tube = tube.translate((-mx, -my, -mz))
    frame_mesh = mesh_from_cadquery(tube, "handle_frame", assets=assets)

    grip = (
        cq.Workplane("YZ", origin=((x_in + x_off) / 2.0, y_grip, z_top))
        .circle(GRIP_R)
        .extrude(GRIP_LEN / 2.0, both=True)
    ).translate((-mx, -my, -mz))
    grip_mesh = mesh_from_cadquery(grip, "handle_grip", assets=assets)
    return frame_mesh, grip_mesh


# ===========================================================================
# Caster geometry
# ===========================================================================
def _simple_fork_mesh(r: ResolvedToolCartConfig, assets):
    """Swivel-caster yoke (all_swivel / mixed front)."""
    axle_z = _axle_z(r)
    leg_y = -SIMPLE_FORK_DROP
    wheel_half_w = SIMPLE_WHEEL_W / 2.0
    leg_x = wheel_half_w + 0.010
    plate = cq.Workplane("XY", origin=(0, 0, -0.007)).box(0.060, 0.060, 0.014)
    post = cq.Workplane("XY", origin=(0, 0, 0.0)).circle(0.013).extrude(0.030)
    post = post.union(cq.Workplane("XY", origin=(0, 0, -0.018)).circle(0.013).extrude(0.018))
    fork = plate.union(post)
    riser_top = 0.0
    # Stop the center spine above the wheel and carry the axle on a separate
    # shaft so the yoke does not cut through the tire volume.
    riser_bot = axle_z + SIMPLE_WHEEL_R + 0.008
    fork = fork.union(
        cq.Workplane(
            "XY", origin=(0.0, leg_y * 0.25, (riser_top + riser_bot) / 2.0)
        ).box(0.090, 0.032, abs(riser_top - riser_bot))
    )
    axle_shaft = (
        cq.Workplane("YZ", origin=(0.0, leg_y, axle_z))
        .circle(0.0045)
        .extrude(wheel_half_w + 0.010, both=True)
    )
    fork = fork.union(axle_shaft)
    leg_top = max(axle_z + SIMPLE_WHEEL_R * 0.55, riser_bot + 0.003)
    leg_bot = axle_z - 0.014
    for sx in (-1.0, 1.0):
        fork = fork.union(
            cq.Workplane(
                "XY",
                origin=(sx * leg_x, leg_y, (leg_top + leg_bot) / 2.0),
            ).box(0.014, 0.032, abs(leg_top - leg_bot))
        )
    return mesh_from_cadquery(fork, "caster_fork", assets=assets)


def _simple_wheel_mesh(r: ResolvedToolCartConfig, assets):
    """Plain rubber tire wheel centered on its own axle (all_swivel / mixed)."""
    wheel = (
        cq.Workplane("YZ", origin=(0, 0, 0))
        .circle(SIMPLE_WHEEL_R)
        .extrude(SIMPLE_WHEEL_W / 2.0, both=True)
    )
    hub_cut = (
        cq.Workplane("YZ", origin=(0, 0, 0))
        .circle(SIMPLE_WHEEL_R - 0.012)
        .extrude(SIMPLE_WHEEL_W / 2.0 + 0.002, both=True)
    )
    rim = wheel.cut(hub_cut)
    hub = cq.Workplane("YZ", origin=(0, 0, 0)).circle(0.015).extrude(SIMPLE_WHEEL_W / 2.0, both=True)
    disc = (
        cq.Workplane("YZ", origin=(0, 0, 0))
        .circle(SIMPLE_WHEEL_R - 0.012)
        .extrude(0.004, both=True)
    )
    solid = rim.union(hub).union(disc)
    # Axle bore through the hub so a mesh surface sits within 15 mm of the wheel
    # center (the prismatic/roll joint origin), satisfying the origin baseline.
    bore = (
        cq.Workplane("YZ", origin=(0, 0, 0))
        .circle(0.006)
        .extrude(SIMPLE_WHEEL_W / 2.0 + 0.010, both=True)
    )
    return mesh_from_cadquery(solid.cut(bore), "caster_wheel", assets=assets)


def _fixed_bracket_mesh(r: ResolvedToolCartConfig, assets):
    """Rigid (non-swivel) caster bracket (mixed rear). Axle directly below."""
    axle_z = _axle_z(r)
    wheel_half_w = SIMPLE_WHEEL_W / 2.0
    leg_x = wheel_half_w + 0.010
    plate = cq.Workplane("XY", origin=(0, 0, -0.007)).box(0.060, 0.050, 0.014)
    # Keep the center web above the wheel cavity and support the wheel on a
    # narrow axle shaft so the bracket no longer intersects the tire.
    riser_top = 0.0
    riser_bot = axle_z + SIMPLE_WHEEL_R + 0.008
    riser = cq.Workplane("XY", origin=(0, 0, (riser_top + riser_bot) / 2.0)).box(
        0.090, 0.036, abs(riser_top - riser_bot)
    )
    bracket = plate.union(riser)
    axle_shaft = (
        cq.Workplane("YZ", origin=(0.0, 0.0, axle_z))
        .circle(0.0045)
        .extrude(wheel_half_w + 0.010, both=True)
    )
    bracket = bracket.union(axle_shaft)
    leg_top = max(axle_z + SIMPLE_WHEEL_R * 0.55, riser_bot + 0.003)
    leg_bot = axle_z - 0.014
    for sx in (-1.0, 1.0):
        leg = cq.Workplane(
            "XY", origin=(sx * leg_x, 0.0, (leg_top + leg_bot) / 2.0)
        ).box(0.014, 0.032, abs(leg_top - leg_bot))
        bracket = bracket.union(leg)
    return mesh_from_cadquery(bracket, "fixed_bracket", assets=assets)


def _brake_fork_mesh(r: ResolvedToolCartConfig, assets):
    """Heavy-duty pneumatic swivel fork with a brake-lever pivot boss."""
    axle_z = _axle_z(r)
    leg_y = -BRAKE_FORK_DROP
    wheel_half_w = BRAKE_WHEEL_W / 2.0
    half_w = wheel_half_w + 0.016
    plate = cq.Workplane("XY", origin=(0, 0, -0.008)).box(0.072, 0.072, 0.016)
    post = cq.Workplane("XY", origin=(0, 0, 0.0)).circle(0.015).extrude(0.030)
    post = post.union(cq.Workplane("XY", origin=(0, 0, -0.020)).circle(0.015).extrude(0.020))
    fork = plate.union(post)
    riser_top = 0.0
    riser_bot = axle_z + BRAKE_WHEEL_R + 0.010
    fork = fork.union(
        cq.Workplane(
            "XY", origin=(0.0, leg_y * 0.25, (riser_top + riser_bot) / 2.0)
        ).box(0.100, 0.036, abs(riser_top - riser_bot))
    )
    axle_shaft = (
        cq.Workplane("YZ", origin=(0.0, leg_y, axle_z))
        .circle(0.0055)
        .extrude(wheel_half_w + 0.016, both=True)
    )
    fork = fork.union(axle_shaft)
    leg_top = max(axle_z + BRAKE_WHEEL_R * 0.55, riser_bot + 0.003)
    leg_bot = axle_z - 0.016
    for sx in (-1.0, 1.0):
        fork = fork.union(
            cq.Workplane("XY", origin=(sx * half_w, leg_y, (leg_top + leg_bot) / 2.0)).box(
                0.016, 0.040, abs(leg_top - leg_bot)
            )
        )
    boss_z = axle_z + BRAKE_WHEEL_R * 0.40
    boss = cq.Workplane("YZ", origin=(half_w + 0.008, leg_y, boss_z)).circle(BRAKE_PIVOT_R).extrude(0.012)
    fork = fork.union(boss)
    return mesh_from_cadquery(fork, "caster_fork", assets=assets)


def _brake_wheel_meshes(r: ResolvedToolCartConfig, assets):
    """Pneumatic wheel: metal rim (hub + web + spoked ring) + rubber tire.
    Returns (rim_mesh, tire_mesh)."""
    half_w = BRAKE_WHEEL_W * 0.44
    hub = cq.Workplane("YZ", origin=(0, 0, 0)).circle(BRAKE_HUB_R + 0.004).extrude(half_w, both=True)
    web = cq.Workplane("YZ", origin=(0, 0, 0)).circle(BRAKE_RIM_R - 0.004).extrude(half_w * 0.6, both=True)
    rim_outer = cq.Workplane("YZ", origin=(0, 0, 0)).circle(BRAKE_RIM_R).extrude(half_w, both=True)
    rim_inner = cq.Workplane("YZ", origin=(0, 0, 0)).circle(BRAKE_RIM_R - 0.006).extrude(half_w + 0.002, both=True)
    rim_solid = hub.union(web).union(rim_outer.cut(rim_inner))

    n_spokes = 5
    spoke_gap_r = 0.012
    spoke_outer_r = BRAKE_RIM_R - 0.008
    for k in range(n_spokes):
        angle = 2 * math.pi * k / n_spokes
        mid_r = 0.5 * (spoke_gap_r + spoke_outer_r)
        slot_len = spoke_outer_r - spoke_gap_r
        slot = (
            cq.Workplane("XY", origin=(0, 0, 0))
            .transformed(rotate=(0, 0, math.degrees(angle)))
            .transformed(offset=(0, mid_r, 0))
            .box(half_w * 1.2, slot_len, slot_len * 0.35)
        )
        rim_solid = rim_solid.cut(slot)
    bore = cq.Workplane("YZ", origin=(0, 0, 0)).circle(0.006).extrude(half_w + 0.010, both=True)
    rim_solid = rim_solid.cut(bore)
    rim_mesh = mesh_from_cadquery(rim_solid, "caster_rim", assets=assets)

    tire = TireGeometry(
        BRAKE_WHEEL_R,
        BRAKE_WHEEL_W,
        inner_radius=BRAKE_RIM_R - 0.004,
        carcass=TireCarcass(belt_width_ratio=0.70, sidewall_bulge=0.06),
        tread=TireTread(style="block", depth=0.008, count=22, land_ratio=0.55),
        sidewall=TireSidewall(style="rounded", bulge=0.05),
        shoulder=TireShoulder(width=0.006, radius=0.004),
    )
    tire_mesh = mesh_from_geometry(tire, "caster_tire")
    return rim_mesh, tire_mesh


def _brake_lever_mesh(r: ResolvedToolCartConfig, assets):
    """Side brake lever: a stamped tab pivoting on the fork boss about local X."""
    boss = (
        cq.Workplane("YZ", origin=(0, 0, 0))
        .circle(BRAKE_PIVOT_R - 0.001)
        .extrude(BRAKE_LEVER_W / 2.0, both=True)
    )
    arm = cq.Workplane(
        "XY", origin=(0, 0.008, -BRAKE_LEVER_LEN / 2.0 + BRAKE_PIVOT_R)
    ).box(BRAKE_LEVER_W, BRAKE_LEVER_T, BRAKE_LEVER_LEN)
    lever = boss.union(arm)
    toe = cq.Workplane(
        "XY", origin=(0, 0.008, -BRAKE_LEVER_LEN + BRAKE_PIVOT_R)
    ).box(BRAKE_LEVER_W, BRAKE_LEVER_T + 0.004, 0.012)
    lever = lever.union(toe)
    return mesh_from_cadquery(lever, "brake_lever", assets=assets)


# ===========================================================================
# Build
# ===========================================================================
def _build_drawers(model, r, mats, carcass, *, assets) -> None:
    face_centers = _drawer_face_centers(r)
    anchor_x = -(r.cab_w / 2.0 - WALL / 2.0)
    guide_offset_x = SIDE_REVEAL - WALL / 2.0
    drawer_origin_x = (
        (r.cab_w - 2 * SIDE_REVEAL) / 2.0 + guide_offset_x
    )
    drawer_origin_y = -(DRAWER_FACE_T + (r.cab_d - WALL - 0.030)) / 2.0
    for i, zc in enumerate(face_centers):
        drawer = model.part(f"drawer_{i}")
        drawer.visual(_drawer_mesh(r, i, assets), material=mats["drawer"], name=f"drawer_face_{i}", material_class_id="metal.paint_coated")
        drawer.inertial = Inertial.from_geometry(
            Box((r.cab_w - 2 * SIDE_REVEAL, r.cab_d - 0.05, r.drawer_heights[i])),
            mass=2.0 + 2.5 * (r.drawer_heights[i] > 0.10),
            origin=Origin(xyz=(drawer_origin_x, drawer_origin_y, 0.0)),
        )
        model.articulation(
            f"frame_to_drawer_{i}",
            ArticulationType.PRISMATIC,
            parent=carcass,
            child=drawer,
            # Anchor the joint on the carcass front-left side rim so the origin
            # sits on real cabinet steel without requiring a visible cross-bar.
            origin=Origin(xyz=(anchor_x, r.cab_d / 2.0, zc)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(
                effort=60.0, velocity=0.30, lower=0.0, upper=r.drawer_travel
            ),
        )


def _build_cabinet_door(model, r, mats, carcass, *, assets) -> None:
    info = _door_opening(r)
    hinge_x = -(r.cab_w / 2.0 - SIDE_REVEAL)
    hinge_y = r.cab_d / 2.0
    door = model.part("cabinet_door")
    door.visual(_cabinet_door_mesh(r, assets), material=mats["drawer"], name="door_panel", material_class_id="metal.paint_coated")
    door.inertial = Inertial.from_geometry(
        Box((r.cab_w - 2 * SIDE_REVEAL, DRAWER_FACE_T, info["height"])),
        mass=3.5,
        origin=Origin(xyz=((r.cab_w - 2 * SIDE_REVEAL) / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "frame_to_door",
        ArticulationType.REVOLUTE,
        parent=carcass,
        child=door,
        origin=Origin(xyz=(hinge_x, hinge_y, info["center_z"])),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=12.0, velocity=2.0, lower=0.0, upper=r.door_open_angle
        ),
    )


def _build_open_shelf_inlays(model, r, mats, carcass, *, assets) -> None:
    """Inline FIXED visuals (Rule 1): bay divider + 2 fixed shelf boards."""
    carcass.visual(_bay_divider_mesh(r, assets), material=mats["accent"], name="bay_divider", material_class_id="metal.paint_coated")
    shelf_zs = _shelf_z_positions(r)
    for i in range(SHELF_COUNT):
        carcass.visual(
            _shelf_mesh(r, i, assets),
            material=mats["accent"],
            name=f"shelf_{i}", material_class_id="metal.paint_coated",
            origin=Origin(xyz=(0.0, 0.0, shelf_zs[i])),
        )


def _build_all_swivel(model, r, mats, carcass, *, assets) -> None:
    fork_mesh = _simple_fork_mesh(r, assets)
    wheel_mesh = _simple_wheel_mesh(r, assets)
    axle_z = _axle_z(r)
    for i, (cx, cy) in enumerate(_caster_positions(r)):
        fork = model.part(f"caster_fork_{i}")
        fork.visual(fork_mesh, material=mats["accent"], name=f"fork_{i}", material_class_id="metal.paint_coated")
        fork.inertial = Inertial.from_geometry(
            Box((0.06, 0.06, r.caster_gap)),
            mass=0.4,
            origin=Origin(xyz=(0.0, -SIMPLE_FORK_DROP / 2.0, -r.caster_gap / 2.0)),
        )
        wheel = model.part(f"caster_wheel_{i}")
        wheel.visual(wheel_mesh, material=mats["wheel"], name=f"wheel_{i}", material_class_id="rubber.smooth_plain")
        wheel.inertial = Inertial.from_geometry(
            Box((SIMPLE_WHEEL_W, 2 * SIMPLE_WHEEL_R, 2 * SIMPLE_WHEEL_R)),
            mass=0.5,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        model.articulation(
            f"frame_to_caster_{i}",
            ArticulationType.CONTINUOUS,
            parent=carcass,
            child=fork,
            origin=Origin(xyz=(cx, cy, r.floor_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=8.0, velocity=6.0),
        )
        model.articulation(
            f"caster_to_wheel_{i}",
            ArticulationType.CONTINUOUS,
            parent=fork,
            child=wheel,
            origin=Origin(xyz=(0.0, -SIMPLE_FORK_DROP, axle_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=20.0),
        )


def _build_mixed_swivel_fixed(model, r, mats, carcass, *, assets) -> None:
    fork_mesh = _simple_fork_mesh(r, assets)
    wheel_mesh = _simple_wheel_mesh(r, assets)
    bracket_mesh = _fixed_bracket_mesh(r, assets)
    axle_z = _axle_z(r)
    front_xs = [sx * (r.cab_w / 2.0 - CASTER_INSET_X) for sx in (-1.0, 1.0)]
    front_cy = r.cab_d / 2.0 - CASTER_INSET_Y
    rear_cy = -(r.cab_d / 2.0 - CASTER_INSET_Y)

    # Front 2 swivel casters.
    for i in range(2):
        cx = front_xs[i]
        fork = model.part(f"swivel_fork_{i}")
        fork.visual(fork_mesh, material=mats["accent"], name=f"fork_{i}", material_class_id="metal.paint_coated")
        fork.inertial = Inertial.from_geometry(
            Box((0.06, 0.06, r.caster_gap)),
            mass=0.4,
            origin=Origin(xyz=(0.0, -SIMPLE_FORK_DROP / 2.0, -r.caster_gap / 2.0)),
        )
        wheel = model.part(f"swivel_wheel_{i}")
        wheel.visual(wheel_mesh, material=mats["wheel"], name=f"wheel_{i}", material_class_id="rubber.smooth_plain")
        wheel.inertial = Inertial.from_geometry(
            Box((SIMPLE_WHEEL_W, 2 * SIMPLE_WHEEL_R, 2 * SIMPLE_WHEEL_R)),
            mass=0.5,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        model.articulation(
            f"frame_to_swivel_{i}",
            ArticulationType.CONTINUOUS,
            parent=carcass,
            child=fork,
            origin=Origin(xyz=(cx, front_cy, r.floor_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=8.0, velocity=6.0),
        )
        model.articulation(
            f"swivel_to_wheel_{i}",
            ArticulationType.CONTINUOUS,
            parent=fork,
            child=wheel,
            origin=Origin(xyz=(0.0, -SIMPLE_FORK_DROP, axle_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=20.0),
        )

    # Rear 2 fixed casters (FIXED bracket, wheel rolls only).
    for i in range(2):
        cx = front_xs[i]
        bracket = model.part(f"fixed_bracket_{i}")
        bracket.visual(bracket_mesh, material=mats["accent"], name=f"bracket_{i}", material_class_id="metal.paint_coated")
        bracket.inertial = Inertial.from_geometry(
            Box((0.06, 0.05, r.caster_gap)),
            mass=0.3,
            origin=Origin(xyz=(0.0, 0.0, -r.caster_gap / 2.0)),
        )
        wheel = model.part(f"fixed_wheel_{i}")
        wheel.visual(wheel_mesh, material=mats["wheel"], name=f"wheel_{i}", material_class_id="rubber.smooth_plain")
        wheel.inertial = Inertial.from_geometry(
            Box((SIMPLE_WHEEL_W, 2 * SIMPLE_WHEEL_R, 2 * SIMPLE_WHEEL_R)),
            mass=0.5,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        model.articulation(
            f"frame_to_bracket_{i}",
            ArticulationType.FIXED,
            parent=carcass,
            child=bracket,
            origin=Origin(xyz=(cx, rear_cy, r.floor_z)),
        )
        model.articulation(
            f"bracket_to_wheel_{i}",
            ArticulationType.CONTINUOUS,
            parent=bracket,
            child=wheel,
            origin=Origin(xyz=(0.0, 0.0, axle_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=20.0),
        )


def _build_brake_caster(model, r, mats, carcass, *, assets) -> None:
    fork_mesh = _brake_fork_mesh(r, assets)
    rim_mesh, tire_mesh = _brake_wheel_meshes(r, assets)
    lever_mesh = _brake_lever_mesh(r, assets)
    axle_z = _axle_z(r)
    half_w = BRAKE_WHEEL_W / 2.0 + 0.016
    boss_z = axle_z + BRAKE_WHEEL_R * 0.40
    for i, (cx, cy) in enumerate(_caster_positions(r)):
        fork = model.part(f"caster_fork_{i}")
        fork.visual(fork_mesh, material=mats["accent"], name=f"fork_{i}", material_class_id="metal.paint_coated")
        fork.inertial = Inertial.from_geometry(
            Box((0.08, 0.08, r.caster_gap)),
            mass=0.6,
            origin=Origin(xyz=(0.0, -BRAKE_FORK_DROP / 2.0, -r.caster_gap / 2.0)),
        )
        wheel = model.part(f"caster_wheel_{i}")
        wheel.visual(rim_mesh, material=mats["accent"], name=f"rim_{i}", material_class_id="metal.paint_coated")
        wheel.visual(tire_mesh, material=mats["wheel"], name=f"tire_{i}", material_class_id="rubber.directional_grooved")
        wheel.inertial = Inertial.from_geometry(
            Box((BRAKE_WHEEL_W, 2 * BRAKE_WHEEL_R, 2 * BRAKE_WHEEL_R)),
            mass=0.8,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        lever = model.part(f"brake_lever_{i}")
        lever.visual(lever_mesh, material=mats["accent"], name=f"lever_{i}", material_class_id="metal.paint_coated")
        lever.inertial = Inertial.from_geometry(
            Box((BRAKE_LEVER_W, BRAKE_LEVER_T, BRAKE_LEVER_LEN)),
            mass=0.05,
            origin=Origin(xyz=(0.0, 0.0, -BRAKE_LEVER_LEN / 2.0)),
        )
        model.articulation(
            f"frame_to_caster_{i}",
            ArticulationType.CONTINUOUS,
            parent=carcass,
            child=fork,
            origin=Origin(xyz=(cx, cy, r.floor_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=8.0, velocity=6.0),
        )
        model.articulation(
            f"caster_to_wheel_{i}",
            ArticulationType.CONTINUOUS,
            parent=fork,
            child=wheel,
            origin=Origin(xyz=(0.0, -BRAKE_FORK_DROP, axle_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=20.0),
        )
        model.articulation(
            f"fork_to_brake_{i}",
            ArticulationType.REVOLUTE,
            parent=fork,
            child=lever,
            origin=Origin(xyz=(half_w + 0.008, -BRAKE_FORK_DROP, boss_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=20.0, velocity=2.0, lower=0.0, upper=r.brake_angle
            ),
        )


_CASTER_BUILDERS = {
    "all_swivel": _build_all_swivel,
    "mixed_swivel_fixed": _build_mixed_swivel_fixed,
    "brake_caster": _build_brake_caster,
}


def build_tool_cart(
    config: ToolCartConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"tool_cart_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in pal.items()
    }

    # --- Carcass (root) ---
    carcass = model.part("cabinet_frame")
    carcass.visual(_carcass_mesh(r, assets), material=mats["shell"], name="carcass_shell", material_class_id="metal.paint_coated")
    carcass.visual(_pegboard_mesh(r, assets), material=mats["drawer"], name="side_pegboard", material_class_id="metal.patterned_sheet_panel")
    if r.storage_module == "rail_shelf":
        carcass.visual(_guard_rail_mesh(r, assets), material=mats["deck"], name="guard_rail", material_class_id="metal.steel_galvanized")
    if r.storage_module == "open_shelf":
        _build_open_shelf_inlays(model, r, mats, carcass, assets=assets)
    carcass.inertial = Inertial.from_geometry(
        Box((r.cab_w, r.cab_d, r.cab_h)),
        mass=22.0,
        origin=Origin(xyz=(0.0, 0.0, r.floor_z + r.cab_h / 2.0)),
    )

    # --- Push handle (FIXED) ---
    handle = model.part("push_handle")
    frame_mesh, grip_mesh = _handle_mesh(r, assets)
    handle.visual(frame_mesh, material=mats["accent"], name="handle_frame", material_class_id="metal.paint_coated")
    handle.visual(grip_mesh, material=mats["grip"], name="handle_grip", material_class_id="rubber.smooth_plain")
    mx, my, mz = _handle_mount(r)
    handle.inertial = Inertial.from_geometry(
        Box((0.20, HANDLE_REACH + 0.10, HANDLE_RISE)),
        mass=1.2,
        # Handle geometry is in the handle-local frame (mount at 0,0,0).
        origin=Origin(xyz=(-0.06, -HANDLE_REACH / 2.0, HANDLE_RISE / 2.0)),
    )
    model.articulation(
        "frame_to_handle",
        ArticulationType.FIXED,
        parent=carcass,
        child=handle,
        # The right upright boss seats into the carcass top trim band (real
        # mount hardware); handle-local (0,0,0) coincides with this point.
        origin=Origin(xyz=(mx, my, mz)),
    )

    # --- Drawers (multiplicity axis: N PRISMATIC slide-out joints) ---
    _build_drawers(model, r, mats, carcass, assets=assets)

    # --- Cabinet door (REVOLUTE) for the cabinet_door module ---
    if r.storage_module == "cabinet_door":
        _build_cabinet_door(model, r, mats, carcass, assets=assets)

    # --- Casters (Slot B) ---
    _CASTER_BUILDERS[r.caster](model, r, mats, carcass, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_tool_cart(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_tool_cart(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_tool_cart_tests(
    object_model: ArticulatedObject,
    config: ToolCartConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    carcass = object_model.get_part("cabinet_frame")
    handle = object_model.get_part("push_handle")
    n = len(r.drawer_heights)
    drawers = [object_model.get_part(f"drawer_{i}") for i in range(n)]
    drawer_joints = [object_model.get_articulation(f"frame_to_drawer_{i}") for i in range(n)]

    # --- Allowances before the baseline gates. ---
    # Wheels spin as free rotary parts carried by their caster forks.
    for part in object_model.parts:
        if part.name.startswith(
            ("caster_wheel_", "swivel_wheel_", "fixed_wheel_", "brake_wheel_")
        ):
            ctx.allow_isolated_part(
                part,
                reason="caster wheel is a free spinning rotary part carried by its fork",
            )
    # Drawers pull out along their slides and ride close against the frame.
    for drw in drawers:
        ctx.allow_isolated_part(
            drw,
            reason="extended drawer slides out of the carcass bay and loses contact",
        )
        ctx.allow_overlap(
            carcass, drw,
            reason="drawer slides along the carcass bay in close sliding contact",
        )

    # --- Carcass present, cabinet-sized, rests above the caster gap. ---
    cab_aabb = ctx.part_world_aabb(carcass)
    ctx.check("carcass present with world AABB", cab_aabb is not None, details=f"cab_aabb={cab_aabb}")
    if cab_aabb is not None:
        (cmn, cmx) = cab_aabb
        ext_x = cmx[0] - cmn[0]
        ctx.check(
            "cabinet body is roughly cabinet-sized (X)",
            0.45 < ext_x < 0.70,
            details=f"ext_x={ext_x:.3f}",
        )
        ctx.check(
            "cabinet floor stands above the caster gap",
            cmn[2] > r.caster_gap - 0.03,
            details=f"carcass_z_min={cmn[2]:.4f}, caster_gap={r.caster_gap:.3f}",
        )

    # --- Drawers exist, stacked top -> bottom, prismatic +Y. ---
    ctx.check("at least two drawers authored", n >= 2, details=f"n_drawers={n}")
    centers = _drawer_face_centers(r)
    ctx.check(
        "drawers stacked top -> bottom (descending z)",
        all(centers[i] > centers[i + 1] for i in range(n - 1)),
        details=f"centers={['%.3f' % c for c in centers]}",
    )
    for i, dj in enumerate(drawer_joints):
        ctx.check(
            f"drawer {i} joint is prismatic",
            str(dj.articulation_type).upper().endswith("PRISMATIC"),
            details=f"type={dj.articulation_type}",
        )
        ax = dj.axis
        ctx.check(
            f"drawer {i} slides along +Y",
            abs(ax[1]) > 0.99 and abs(ax[0]) < 0.01 and abs(ax[2]) < 0.01,
            details=f"axis={ax}",
        )
        lim = dj.motion_limits
        ctx.check(
            f"drawer {i} has positive pull-out travel",
            lim is not None
            and lim.lower is not None
            and lim.upper is not None
            and lim.lower == 0.0
            and lim.upper > 0.10,
            details=f"lower={None if lim is None else lim.lower}, upper={None if lim is None else lim.upper}",
        )

    # --- Drawer opens out past the cabinet front. ---
    if cab_aabb is not None and n > 0:
        cab_front_y = cab_aabb[1][1]
        test_i = min(1, n - 1)
        dj = drawer_joints[test_i]
        with ctx.pose({dj: 0.0}):
            rest = ctx.part_world_aabb(drawers[test_i])
        with ctx.pose({dj: r.drawer_travel}):
            ext = ctx.part_world_aabb(drawers[test_i])
        if rest is not None and ext is not None:
            rest_cy = 0.5 * (rest[0][1] + rest[1][1])
            ext_cy = 0.5 * (ext[0][1] + ext[1][1])
            ctx.check(
                "opening the drawer moves it out in +Y",
                ext_cy > rest_cy + 0.10,
                details=f"rest_cy={rest_cy:.3f}, ext_cy={ext_cy:.3f}",
            )
            ctx.check(
                "closed drawer face is flush with the cabinet front",
                abs(rest[1][1] - cab_front_y) < 0.025,
                details=f"drawer_front={rest[1][1]:.3f}, cab_front={cab_front_y:.3f}",
            )

    for i, drawer in enumerate(drawers):
        ctx.allow_isolated_part(
            drawer,
            reason=(
                "Drawer slides on its prismatic joint inside the carcass opening; a "
                "small sliding clearance keeps the closed drawer from contacting the "
                "surrounding steel, but the joint provides the connection."
            ),
        )
        ctx.allow_overlap(
            carcass,
            drawer,
            elem_b=f"drawer_face_{i}",
            reason=(
                "Each drawer carries a hidden side slide-guide lug captured just "
                "behind the carcass side rim, replacing the previously visible "
                "front cross-rail."
            ),
        )

    # --- Push handle present, fixed, rises above and reaches back. ---
    h_aabb = ctx.part_world_aabb(handle)
    ctx.check("push handle present", h_aabb is not None, details=f"handle_aabb={h_aabb}")
    if h_aabb is not None and cab_aabb is not None:
        ctx.check(
            "handle rises above the cabinet top",
            h_aabb[1][2] > cab_aabb[1][2] + 0.05,
            details=f"handle_top={h_aabb[1][2]:.3f}, cab_top={cab_aabb[1][2]:.3f}",
        )
        ctx.check(
            "handle grip reaches back past the cabinet rear",
            h_aabb[0][1] < cab_aabb[0][1] - 0.05,
            details=f"handle_back_y={h_aabb[0][1]:.3f}, cab_back_y={cab_aabb[0][1]:.3f}",
        )
    handle_joint = object_model.get_articulation("frame_to_handle")
    ctx.check(
        "handle is rigidly fixed to the cabinet",
        str(handle_joint.articulation_type).upper().endswith("FIXED"),
        details=f"type={handle_joint.articulation_type}",
    )
    ctx.allow_overlap(
        carcass,
        handle,
        reason=(
            "The push-handle upright mounting bosses are intentionally seated into "
            "the cabinet top trim band; the small local overlap represents the bolted "
            "handle mount."
        ),
    )

    # --- Cabinet door (cabinet_door module). ---
    if r.storage_module == "cabinet_door":
        door = object_model.get_part("cabinet_door")
        door_joint = object_model.get_articulation("frame_to_door")
        ctx.check(
            "door joint is revolute",
            str(door_joint.articulation_type).upper().endswith("REVOLUTE"),
            details=f"type={door_joint.articulation_type}",
        )
        dax = door_joint.axis
        ctx.check(
            "door hinge axis is vertical Z",
            abs(dax[2]) > 0.99 and abs(dax[0]) < 0.01 and abs(dax[1]) < 0.01,
            details=f"axis={dax}",
        )
        dlim = door_joint.motion_limits
        ctx.check(
            "door has realistic open limits",
            dlim is not None
            and dlim.lower == 0.0
            and dlim.upper is not None
            and 0.8 < dlim.upper < 2.5,
            details=f"upper={None if dlim is None else dlim.upper}",
        )
        ctx.allow_overlap(
            carcass,
            door,
            reason=(
                "The cabinet door hinge barrel stubs are intentionally seated at the "
                "carcass front-left edge; the small local overlap represents the "
                "captured hinge pin that mounts the door to the cabinet."
            ),
        )

    # --- rail_shelf guard rail visual present. ---
    if r.storage_module == "rail_shelf":
        ctx.check(
            "guard rail visual present on cabinet_frame",
            carcass.get_visual("guard_rail") is not None,
            details="guard_rail visual not found",
        )

    # --- Casters: per-caster topology checks + ground contact. ---
    if r.caster == "mixed_swivel_fixed":
        swivel_forks = [object_model.get_part(f"swivel_fork_{i}") for i in range(2)]
        swivel_wheels = [object_model.get_part(f"swivel_wheel_{i}") for i in range(2)]
        fixed_brackets = [object_model.get_part(f"fixed_bracket_{i}") for i in range(2)]
        fixed_wheels = [object_model.get_part(f"fixed_wheel_{i}") for i in range(2)]
        swivel_joints = [object_model.get_articulation(f"frame_to_swivel_{i}") for i in range(2)]
        fixed_joints = [object_model.get_articulation(f"frame_to_bracket_{i}") for i in range(2)]
        roll_joints = [object_model.get_articulation(f"swivel_to_wheel_{i}") for i in range(2)]
        roll_joints += [object_model.get_articulation(f"bracket_to_wheel_{i}") for i in range(2)]
        all_wheels = swivel_wheels + fixed_wheels
        ctx.check(
            "two front swivel + two rear fixed casters",
            len(swivel_forks) == 2 and len(fixed_brackets) == 2,
            details=f"swivel={len(swivel_forks)}, fixed={len(fixed_brackets)}",
        )
        for sj in swivel_joints:
            ctx.check(
                "front caster swivels about vertical Z (continuous)",
                abs(sj.axis[2]) > 0.99 and str(sj.articulation_type).upper().endswith("CONTINUOUS"),
                details=f"axis={sj.axis}, type={sj.articulation_type}",
            )
        for fj in fixed_joints:
            ctx.check(
                "rear caster bracket is FIXED",
                str(fj.articulation_type).upper().endswith("FIXED"),
                details=f"type={fj.articulation_type}",
            )
        for i in range(2):
            ctx.allow_overlap(
                swivel_forks[i], swivel_wheels[i],
                reason="The swivel caster wheel is captured in the trailing yoke at the axle.",
            )
            ctx.allow_overlap(
                carcass, swivel_forks[i],
                reason="The swivel post bites up into the cabinet floor (captured swivel bearing).",
            )
            ctx.allow_overlap(
                fixed_brackets[i], fixed_wheels[i],
                reason="The fixed caster wheel is captured in the bracket yoke at the axle.",
            )
            ctx.allow_overlap(
                carcass, fixed_brackets[i],
                reason="The fixed bracket plate is bolted flat up against the cabinet floor.",
            )
    else:
        forks = [object_model.get_part(f"caster_fork_{i}") for i in range(4)]
        wheels = [object_model.get_part(f"caster_wheel_{i}") for i in range(4)]
        swivel_joints = [object_model.get_articulation(f"frame_to_caster_{i}") for i in range(4)]
        roll_joints = [object_model.get_articulation(f"caster_to_wheel_{i}") for i in range(4)]
        all_wheels = wheels
        ctx.check(
            "four casters authored",
            len(forks) == 4 and len(wheels) == 4,
            details=f"forks={len(forks)}, wheels={len(wheels)}",
        )
        for sj in swivel_joints:
            ctx.check(
                "caster swivels about vertical Z (continuous)",
                abs(sj.axis[2]) > 0.99 and str(sj.articulation_type).upper().endswith("CONTINUOUS"),
                details=f"axis={sj.axis}, type={sj.articulation_type}",
            )
        for rj in roll_joints:
            ctx.check(
                "caster wheel rolls about its X axle (continuous)",
                abs(rj.axis[0]) > 0.99 and str(rj.articulation_type).upper().endswith("CONTINUOUS"),
                details=f"axis={rj.axis}, type={rj.articulation_type}",
            )
        # Swiveling relocates the trailing wheel.
        with ctx.pose({swivel_joints[0]: 0.0}):
            w0 = ctx.part_world_position(wheels[0])
        with ctx.pose({swivel_joints[0]: math.pi}):
            w0b = ctx.part_world_position(wheels[0])
        ctx.check(
            "swiveling a caster relocates its trailing wheel",
            w0 is not None and w0b is not None
            and math.hypot(w0b[0] - w0[0], w0b[1] - w0[1]) > 0.02,
            details=f"wheel0={w0}, wheel0_180={w0b}",
        )
        for i in range(4):
            ctx.allow_overlap(
                forks[i], wheels[i],
                reason="The caster wheel is captured in the trailing yoke of the fork at the axle.",
            )
            ctx.allow_overlap(
                carcass, forks[i],
                reason="The caster swivel post is intentionally seated up into the cabinet floor.",
            )

    # All wheels reach the ground plane (z ~= 0).
    for i, wheel in enumerate(all_wheels):
        w_aabb = ctx.part_world_aabb(wheel)
        ctx.check(
            f"caster wheel {i} reaches the ground plane",
            w_aabb is not None and abs(w_aabb[0][2]) < 0.03,
            details=f"wheel_z_min={None if w_aabb is None else w_aabb[0][2]}",
        )

    # --- brake_caster brake lever checks. ---
    if r.caster == "brake_caster":
        levers = [object_model.get_part(f"brake_lever_{i}") for i in range(4)]
        brake_joints = [object_model.get_articulation(f"fork_to_brake_{i}") for i in range(4)]
        forks = [object_model.get_part(f"caster_fork_{i}") for i in range(4)]
        ctx.check("four brake levers authored", len(levers) == 4, details=f"levers={len(levers)}")
        for bj in brake_joints:
            ctx.check(
                "brake lever pivots about X (revolute)",
                abs(bj.axis[0]) > 0.99 and str(bj.articulation_type).upper().endswith("REVOLUTE"),
                details=f"axis={bj.axis}, type={bj.articulation_type}",
            )
        # Engaging the brake moves the lever.
        bj0 = brake_joints[0]
        with ctx.pose({bj0: 0.0}):
            l_rest = ctx.part_world_aabb(levers[0])
        with ctx.pose({bj0: r.brake_angle}):
            l_eng = ctx.part_world_aabb(levers[0])
        if l_rest is not None and l_eng is not None:
            moved = abs(l_eng[0][1] - l_rest[0][1]) + abs(l_eng[0][2] - l_rest[0][2])
            ctx.check(
                "engaging the brake swings the lever",
                moved > 0.005,
                details=f"moved={moved:.4f}",
            )
        for i in range(4):
            ctx.allow_overlap(
                forks[i], levers[i],
                reason="The brake lever pivots on the fork leg boss (captured pin-on-boss).",
            )

    return ctx.report()
