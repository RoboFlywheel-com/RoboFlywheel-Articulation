# SPDX-License-Identifier: Apache-2.0

"""pictureX/0611 Cabinet_with_drawers — Design-backed single-file template.

A chest of drawers: one load-bearing carcass (rectilinear, bombe, oval-ended, bow-front or
tapered case) whose only articulation is a set of pull-out drawers. Every drawer is a real
hollow tray riding on its own pair of side runners.

The host publishes a plan profile and a clear opening, so every drawer front is struck from
the host's own front curve over its own x-range: a bombe, bow or oval case gets curved
fronts, a rectilinear or tapered case gets flat ones. Level pitch, graduated front heights,
tray width, box depth and travel all derive from the cavity and from N, so every declared
slot combination builds and no overlap allowance is emitted.

Coordinate convention: X = width, Y = depth with the FRONT at -Y, Z = height, drawers pull
out along -Y.
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
    Box,
    Cylinder,
    ExtrudeGeometry,
    LoftGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    PlaneInterface,
    Sphere,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_planes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

BodyForm = Literal["rect_case", "bombe_serpentine", "oval_rounded", "bow_front", "tapered_case"]
DrawerLayout = Literal["full_width_stack", "paired_grid", "pair_over_full_width"]
DrawerFront = Literal["flat_panel", "framed_cane", "gothic_arch", "applique_moulded"]
SupportBase = Literal[
    "cabriole_apron",
    "fine_metal_legs",
    "plinth_block_feet",
    "splayed_tapered_legs",
    "tapered_legs_apron",
    "toe_kick_plinth",
]

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot(
            "body_form",
            ("rect_case", "bombe_serpentine", "oval_rounded", "bow_front", "tapered_case"),
        ),
        component_slot(
            "drawer_layout", ("full_width_stack", "paired_grid", "pair_over_full_width")
        ),
        component_slot(
            "drawer_front", ("flat_panel", "framed_cane", "gothic_arch", "applique_moulded")
        ),
        component_slot(
            "support_base",
            (
                "cabriole_apron",
                "fine_metal_legs",
                "plinth_block_feet",
                "splayed_tapered_legs",
                "tapered_legs_apron",
                "toe_kick_plinth",
            ),
        ),
        multiplicity_slot("drawer_count", (2, 3, 4, 5, 6), item_slot="drawer_front"),
    )
)

# manufacturing constants (metres)
_TOP_T = 0.028
_BASE_T = 0.024
_WALL_T = 0.020
_RAIL_W = 0.014
_RAIL_EMBED = 0.006
_RAIL_H = 0.012
_RUNNER_W = 0.009
_RUNNER_ENGAGE = 0.003
_TRAY_WALL_T = 0.011
_TRAY_FLOOR_T = 0.011
_SIDE_CLEAR = 0.003
_LEVEL_REVEAL = 0.008
_FRONT_GAP = 0.001
# Minimum front reach for a straight case.  Curved cases derive a larger reach
# per cell so the tray floor and side walls actually meet the back of the face.
_TRAY_FRONT_REACH = 0.017
_REAR_CLEAR = 0.016
_RAIL_FRONT_RECESS = 0.050
_RUNNER_FRONT_CLEAR = 0.004
_MIN_FRONT_H = 0.070
_MIN_DRAWER_W = 0.110
_PLAN_SEGMENTS = 26
_TRAY_PROFILE_SAMPLES = 12

RGBA = tuple[float, float, float, float]
_PALETTES: tuple[dict[str, RGBA], ...] = (
    {  # mahogany with gilt brass, origin 001
        "wood": (0.36, 0.17, 0.10, 1.0), "dark": (0.16, 0.08, 0.05, 1.0),
        "panel": (0.45, 0.23, 0.13, 1.0), "metal": (0.78, 0.63, 0.29, 1.0),
        "accent": (0.85, 0.72, 0.38, 1.0),
    },
    {  # walnut with fine brass, origin 002
        "wood": (0.33, 0.21, 0.13, 1.0), "dark": (0.14, 0.09, 0.06, 1.0),
        "panel": (0.42, 0.28, 0.17, 1.0), "metal": (0.74, 0.62, 0.34, 1.0),
        "accent": (0.62, 0.48, 0.24, 1.0),
    },
    {  # pale oak with bronze, origin 004
        "wood": (0.72, 0.56, 0.34, 1.0), "dark": (0.42, 0.30, 0.17, 1.0),
        "panel": (0.80, 0.66, 0.44, 1.0), "metal": (0.55, 0.42, 0.24, 1.0),
        "accent": (0.86, 0.74, 0.52, 1.0),
    },
    {  # painted ivory with wood tops, origin 003
        "wood": (0.88, 0.85, 0.78, 1.0), "dark": (0.40, 0.36, 0.30, 1.0),
        "panel": (0.92, 0.90, 0.84, 1.0), "metal": (0.66, 0.58, 0.36, 1.0),
        "accent": (0.52, 0.40, 0.26, 1.0),
    },
    {  # smoked grey with steel, var_toekick
        "wood": (0.40, 0.41, 0.43, 1.0), "dark": (0.17, 0.18, 0.19, 1.0),
        "panel": (0.50, 0.51, 0.53, 1.0), "metal": (0.76, 0.78, 0.80, 1.0),
        "accent": (0.86, 0.60, 0.22, 1.0),
    },
)

_SUPPORT_HEIGHT_FIELD: dict[str, str] = {
    "cabriole_apron": "cabriole_h_m",
    "fine_metal_legs": "metal_leg_h_m",
    "plinth_block_feet": "plinth_h_m",
    "splayed_tapered_legs": "splayed_leg_h_m",
    "tapered_legs_apron": "apron_leg_h_m",
    "toe_kick_plinth": "toe_kick_h_m",
}
_SUPPORT_BOUNDS: dict[str, tuple[float, float]] = {
    "cabriole_apron": (0.110, 0.260),
    "fine_metal_legs": (0.120, 0.320),
    "plinth_block_feet": (0.070, 0.190),
    "splayed_tapered_legs": (0.140, 0.320),
    "tapered_legs_apron": (0.140, 0.330),
    "toe_kick_plinth": (0.050, 0.130),
}
_BODY_BOUNDS: dict[str, dict[str, tuple[float, float]]] = {
    "rect_case": {"w": (0.70, 1.42), "d": (0.36, 0.54), "h": (0.72, 1.34)},
    "bombe_serpentine": {"w": (0.68, 1.10), "d": (0.38, 0.52), "h": (0.76, 1.16)},
    "oval_rounded": {"w": (0.66, 1.06), "d": (0.36, 0.50), "h": (0.74, 1.20)},
    "bow_front": {"w": (0.70, 1.30), "d": (0.36, 0.52), "h": (0.74, 1.26)},
    "tapered_case": {"w": (0.70, 1.30), "d": (0.36, 0.52), "h": (0.74, 1.30)},
}


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    body_form: BodyForm = "rect_case"
    drawer_layout: DrawerLayout = "full_width_stack"
    drawer_front: DrawerFront = "flat_panel"
    support_base: SupportBase = "plinth_block_feet"
    drawer_count: int = 3
    carcass_width_m: float | None = None
    carcass_depth_m: float | None = None
    carcass_height_m: float | None = None
    rect_wall_t_m: float | None = None
    bombe_bulge_m: float | None = None
    oval_end_ratio: float | None = None
    bow_depth_m: float | None = None
    case_taper_ratio: float | None = None
    graduation_ratio: float | None = None
    divider_t_m: float | None = None
    base_level_ratio: float | None = None
    drawer_travel_ratio: float | None = None
    front_t_m: float | None = None
    cane_frame_w_m: float | None = None
    arch_rise_ratio: float | None = None
    applique_relief_m: float | None = None
    cabriole_h_m: float | None = None
    metal_leg_h_m: float | None = None
    plinth_h_m: float | None = None
    splayed_leg_h_m: float | None = None
    apron_leg_h_m: float | None = None
    toe_kick_h_m: float | None = None
    palette: int = 0
    name: str = "drawer_cabinet_with_sliding_drawers"


@dataclass(frozen=True)
class ResolvedConfig:
    body_form: BodyForm
    drawer_layout: DrawerLayout
    drawer_front: DrawerFront
    support_base: SupportBase
    drawer_count: int
    palette: int
    name: str
    carcass_width_m: float
    carcass_depth_m: float
    carcass_height_m: float
    rect_wall_t_m: float
    bombe_bulge_m: float
    oval_end_ratio: float
    bow_depth_m: float
    case_taper_ratio: float
    graduation_ratio: float
    divider_t_m: float
    base_level_ratio: float
    drawer_travel_ratio: float
    front_t_m: float
    cane_frame_w_m: float
    arch_rise_ratio: float
    applique_relief_m: float
    cabriole_h_m: float
    metal_leg_h_m: float
    plinth_h_m: float
    splayed_leg_h_m: float
    apron_leg_h_m: float
    toe_kick_h_m: float
    wall_t_m: float
    body_bottom_z_m: float
    body_top_z_m: float
    cavity_lo_z_m: float
    cavity_hi_z_m: float
    inner_half_w_m: float
    cavity_front_y_m: float
    cavity_back_y_m: float
    box_depth_m: float
    travel_m: float
    level_columns: tuple[int, ...]
    level_bounds: tuple[tuple[float, float], ...]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value: float | None, default: float) -> float:
    return default if value is None else float(value)


def _level_columns(layout: str, n: int) -> tuple[int, ...]:
    """Column count per level, bottom to top; the total is always N."""

    if layout == "full_width_stack":
        return tuple([1] * n)
    if layout == "paired_grid":
        # pairs from the bottom up, a single narrow drawer on top when N is odd
        return tuple([2] * (n // 2) + ([1] if n % 2 else []))
    remaining = n - 1
    return tuple([1] + [2] * (remaining // 2) + ([1] if remaining % 2 else []))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(seed)
    body_form: BodyForm = rng.choice(
        ("rect_case", "bombe_serpentine", "oval_rounded", "bow_front", "tapered_case")
    )
    bounds = _BODY_BOUNDS[body_form]
    return Config(
        body_form=body_form,
        drawer_layout=rng.choice(("full_width_stack", "paired_grid", "pair_over_full_width")),
        drawer_front=rng.choice(("flat_panel", "framed_cane", "gothic_arch", "applique_moulded")),
        support_base=rng.choice(tuple(_SUPPORT_HEIGHT_FIELD)),
        drawer_count=rng.choice((2, 3, 4, 5, 6)),
        carcass_width_m=round(rng.uniform(*bounds["w"]), 3),
        carcass_depth_m=round(rng.uniform(*bounds["d"]), 3),
        carcass_height_m=round(rng.uniform(*bounds["h"]), 3),
        rect_wall_t_m=round(rng.uniform(0.016, 0.030), 4),
        bombe_bulge_m=round(rng.uniform(0.018, 0.055), 4),
        oval_end_ratio=round(rng.uniform(0.30, 0.95), 3),
        bow_depth_m=round(rng.uniform(0.012, 0.048), 4),
        case_taper_ratio=round(rng.uniform(0.72, 0.96), 3),
        graduation_ratio=round(rng.uniform(1.00, 1.85), 3),
        divider_t_m=round(rng.uniform(0.014, 0.036), 4),
        base_level_ratio=round(rng.uniform(1.15, 2.10), 3),
        drawer_travel_ratio=round(rng.uniform(0.36, 0.62), 3),
        front_t_m=round(rng.uniform(0.016, 0.032), 4),
        cane_frame_w_m=round(rng.uniform(0.030, 0.062), 4),
        arch_rise_ratio=round(rng.uniform(0.24, 0.72), 3),
        applique_relief_m=round(rng.uniform(0.004, 0.014), 4),
        cabriole_h_m=round(rng.uniform(0.110, 0.260), 3),
        metal_leg_h_m=round(rng.uniform(0.120, 0.320), 3),
        plinth_h_m=round(rng.uniform(0.070, 0.190), 3),
        splayed_leg_h_m=round(rng.uniform(0.140, 0.320), 3),
        apron_leg_h_m=round(rng.uniform(0.140, 0.330), 3),
        toe_kick_h_m=round(rng.uniform(0.050, 0.130), 3),
        palette=rng.randrange(len(_PALETTES)),
        name=f"drawer_cabinet_with_sliding_drawers_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    body_form = config.body_form
    layout = config.drawer_layout
    front_kind = config.drawer_front
    support = config.support_base
    n = int(_clamp(int(config.drawer_count), 2, 6))

    bounds = _BODY_BOUNDS[body_form]
    width = _clamp(_pick(config.carcass_width_m, sum(bounds["w"]) / 2), *bounds["w"])
    depth = _clamp(_pick(config.carcass_depth_m, sum(bounds["d"]) / 2), *bounds["d"])
    height = _clamp(_pick(config.carcass_height_m, sum(bounds["h"]) / 2), *bounds["h"])

    rect_wall = _clamp(_pick(config.rect_wall_t_m, 0.020), 0.016, 0.030)
    wall_t = rect_wall if body_form == "rect_case" else _WALL_T

    support_bounds = _SUPPORT_BOUNDS[support]
    body_bottom = _clamp(
        _pick(getattr(config, _SUPPORT_HEIGHT_FIELD[support]), sum(support_bounds) / 2),
        *support_bounds,
    )
    body_top = body_bottom + height

    cavity_lo = body_bottom + _BASE_T
    cavity_hi = body_top - _TOP_T
    inner_half_w = max(width / 2.0 - wall_t, 0.12)
    cavity_front_y = -depth / 2.0
    cavity_back_y = depth / 2.0 - wall_t
    box_depth = max(cavity_back_y - cavity_front_y - _REAR_CLEAR, 0.14)
    travel_ratio = _clamp(_pick(config.drawer_travel_ratio, 0.48), 0.36, 0.62)
    travel = box_depth * travel_ratio

    # --- level ladder -------------------------------------------------------
    columns = _level_columns(layout, n)
    graduation = _clamp(_pick(config.graduation_ratio, 1.35), 1.00, 1.85)
    base_ratio = _clamp(_pick(config.base_level_ratio, 1.55), 1.15, 2.10)
    level_count = len(columns)
    if layout == "full_width_stack":
        weights = [
            1.0 + (graduation - 1.0) * (1.0 - (i / max(level_count - 1, 1)))
            for i in range(level_count)
        ]
    elif layout == "pair_over_full_width":
        weights = [base_ratio] + [1.0] * (level_count - 1)
    else:
        weights = [1.0 + 0.18 * (level_count - 1 - i) for i in range(level_count)]
    total_weight = sum(weights)
    usable = max(cavity_hi - cavity_lo - level_count * _LEVEL_REVEAL, level_count * _MIN_FRONT_H)
    bounds_list: list[tuple[float, float]] = []
    z = cavity_lo
    for weight in weights:
        band = max(usable * weight / total_weight, _MIN_FRONT_H)
        bounds_list.append((z, z + band))
        z += band + _LEVEL_REVEAL

    return ResolvedConfig(
        body_form=body_form,
        drawer_layout=layout,
        drawer_front=front_kind,
        support_base=support,
        drawer_count=n,
        palette=int(config.palette) % len(_PALETTES),
        name=config.name,
        carcass_width_m=width,
        carcass_depth_m=depth,
        carcass_height_m=height,
        rect_wall_t_m=rect_wall,
        bombe_bulge_m=_clamp(_pick(config.bombe_bulge_m, 0.032), 0.018, 0.055),
        oval_end_ratio=_clamp(_pick(config.oval_end_ratio, 0.62), 0.30, 0.95),
        bow_depth_m=_clamp(_pick(config.bow_depth_m, 0.028), 0.012, 0.048),
        case_taper_ratio=_clamp(_pick(config.case_taper_ratio, 0.86), 0.72, 0.96),
        graduation_ratio=graduation,
        divider_t_m=_clamp(_pick(config.divider_t_m, 0.024), 0.014, 0.036),
        base_level_ratio=base_ratio,
        drawer_travel_ratio=travel_ratio,
        front_t_m=_clamp(_pick(config.front_t_m, 0.022), 0.016, 0.032),
        cane_frame_w_m=_clamp(_pick(config.cane_frame_w_m, 0.044), 0.030, 0.062),
        arch_rise_ratio=_clamp(_pick(config.arch_rise_ratio, 0.46), 0.24, 0.72),
        applique_relief_m=_clamp(_pick(config.applique_relief_m, 0.009), 0.004, 0.014),
        cabriole_h_m=_clamp(_pick(config.cabriole_h_m, 0.180), 0.110, 0.260),
        metal_leg_h_m=_clamp(_pick(config.metal_leg_h_m, 0.220), 0.120, 0.320),
        plinth_h_m=_clamp(_pick(config.plinth_h_m, 0.130), 0.070, 0.190),
        splayed_leg_h_m=_clamp(_pick(config.splayed_leg_h_m, 0.230), 0.140, 0.320),
        apron_leg_h_m=_clamp(_pick(config.apron_leg_h_m, 0.235), 0.140, 0.330),
        toe_kick_h_m=_clamp(_pick(config.toe_kick_h_m, 0.090), 0.050, 0.130),
        wall_t_m=wall_t,
        body_bottom_z_m=body_bottom,
        body_top_z_m=body_top,
        cavity_lo_z_m=cavity_lo,
        cavity_hi_z_m=cavity_hi,
        inner_half_w_m=inner_half_w,
        cavity_front_y_m=cavity_front_y,
        cavity_back_y_m=cavity_back_y,
        box_depth_m=box_depth,
        travel_m=travel,
        level_columns=columns,
        level_bounds=tuple(bounds_list),
    )


# ---------------------------------------------------------------------------
# plan profile — the single source of the host's outline and front curve
# ---------------------------------------------------------------------------
def _taper_scale(r: ResolvedConfig, z: float) -> float:
    if r.body_form != "tapered_case":
        return 1.0
    span = max(r.carcass_height_m, 1e-6)
    t = _clamp((z - r.body_bottom_z_m) / span, 0.0, 1.0)
    return 1.0 - t * (1.0 - r.case_taper_ratio)


def _bombe_scale(r: ResolvedConfig, z: float) -> float:
    """Bombe swell peaks near mid height and returns at top and bottom."""

    if r.body_form != "bombe_serpentine":
        return 0.0
    span = max(r.carcass_height_m, 1e-6)
    t = _clamp((z - r.body_bottom_z_m) / span, 0.0, 1.0)
    return math.sin(math.pi * _clamp(t * 0.85 + 0.10, 0.0, 1.0))


def _front_y(r: ResolvedConfig, x: float, z: float) -> float:
    """Front face y at plan coordinate x and height z (negative is forward)."""

    scale = _taper_scale(r, z)
    half_w = max(r.carcass_width_m / 2.0 * scale, 1e-4)
    u = _clamp(x / half_w, -1.0, 1.0)
    base = -r.carcass_depth_m / 2.0
    if r.body_form == "bow_front":
        return base - r.bow_depth_m * (1.0 - u * u)
    if r.body_form == "bombe_serpentine":
        return base - r.bombe_bulge_m * _bombe_scale(r, z) * (1.0 - u * u)
    if r.body_form == "oval_rounded":
        end = _clamp(r.oval_end_ratio, 0.05, 1.0)
        return base * (math.sqrt(max(1.0 - u * u, 0.0)) * end + (1.0 - end))
    return base


def _side_x(r: ResolvedConfig, v: float, z: float) -> float:
    """Half width at normalised depth v in [-1, 1] (front = -1)."""

    half_w = r.carcass_width_m / 2.0 * _taper_scale(r, z)
    if r.body_form == "bombe_serpentine":
        return half_w + r.bombe_bulge_m * _bombe_scale(r, z) * (1.0 - v * v) * 0.55
    if r.body_form == "oval_rounded":
        end = _clamp(r.oval_end_ratio, 0.05, 1.0)
        return half_w * (math.sqrt(max(1.0 - v * v, 0.0)) * end + (1.0 - end))
    return half_w


def _back_y(r: ResolvedConfig, x: float, z: float) -> float:
    """Rear face y at plan coordinate x and height z."""

    scale = _taper_scale(r, z)
    half_w = max(r.carcass_width_m / 2.0 * scale, 1e-4)
    u = _clamp(x / half_w, -1.0, 1.0)
    base = r.carcass_depth_m / 2.0
    if r.body_form == "oval_rounded":
        end = _clamp(r.oval_end_ratio, 0.05, 1.0)
        return base * (math.sqrt(max(1.0 - u * u, 0.0)) * end + (1.0 - end))
    return base


def _clear_depth(r: ResolvedConfig, x: float, z: float) -> float:
    """Usable cavity depth at plan coordinate x."""

    return (_back_y(r, x, z) - r.wall_t_m) - (_front_y(r, x, z) + 0.012)


def _level_window(r: ResolvedConfig, z: float) -> tuple[float, float, float]:
    """(half width, front y, rear y) of the largest tray envelope the host allows.

    Width and depth constrain each other on a curved case — the walls pinch near
    the front and back, and the front curve recedes toward the ends — so the
    envelope is solved by a short fixed-point iteration on the plan profile.
    """

    back_half = max(r.carcass_depth_m / 2.0, 1e-4)
    half_w = max(_side_x(r, 0.0, z) - r.wall_t_m, 0.060)
    y_front = -back_half
    y_back = back_half
    for _ in range(4):
        xs = [-half_w + 2.0 * half_w * i / 8.0 for i in range(9)]
        y_front = max(_front_y(r, x, z) for x in xs) + 0.012
        y_back = min(_back_y(r, x, z) for x in xs) - r.wall_t_m
        if y_back - y_front < 0.150:
            y_back = y_front + 0.150
        # sample from the shell opening edge, not just the tray window, because
        # the tray reaches forward to meet its front panel
        y_lo = y_front - _TRAY_FRONT_REACH - 0.006
        vs = [_clamp((y_lo + (y_back - y_lo) * i / 10.0) / back_half, -1.0, 1.0) for i in range(11)]
        pinched = min(_side_x(r, v, z) for v in vs) - r.wall_t_m
        half_w = max(min(half_w, pinched), 0.060)
    return half_w, y_front, y_back


def _usable_half_w(r: ResolvedConfig, z: float) -> float:
    return _level_window(r, z)[0]


def _adapt_edge_x(r: ResolvedConfig, x: float, z: float, reference_z: float) -> float:
    """Adapt a cell edge from its reference level to the actual section height."""

    reference_w = max(_usable_half_w(r, reference_z), 0.060)
    target_w = max(_usable_half_w(r, z), 0.060)
    return x * target_w / reference_w


def _front_open_y(r: ResolvedConfig) -> float:
    """Y where the drawer opening starts; the shell stops in front of it."""

    return min(_level_window(r, z1)[1] for _z0, z1 in r.level_bounds) - 0.012


def _plan_outline(
    r: ResolvedConfig, z: float, y_open: float | None = None
) -> list[tuple[float, float]]:
    """Outline from the opening edge around the back to the other opening edge."""

    back_y = r.carcass_depth_m / 2.0
    v_start = -1.0
    if y_open is not None:
        v_start = _clamp(y_open / back_y, -1.0, 0.85)
    points: list[tuple[float, float]] = []
    steps = _PLAN_SEGMENTS
    for i in range(steps + 1):
        v = v_start + (1.0 - v_start) * i / steps
        points.append((-_side_x(r, v, z), back_y * v))
    for i in range(steps + 1):
        v = 1.0 - (1.0 - v_start) * i / steps
        points.append((_side_x(r, v, z), back_y * v))
    return points


def _shell_profile(r: ResolvedConfig, z: float, y_open: float) -> list[tuple[float, float]]:
    """Annular band between the outline and a radially inset copy of it."""

    outer = _plan_outline(r, z, y_open)
    inner: list[tuple[float, float]] = []
    for x, y in reversed(outer):
        length = math.hypot(x, y)
        if length <= 1e-6:
            inner.append((x, y))
            continue
        shrink = max(1.0 - r.wall_t_m / length, 0.05)
        inner.append((x * shrink, y * shrink))
    return outer + inner


def _solid_slab_profile(r: ResolvedConfig, z: float, grow: float) -> list[tuple[float, float]]:
    points = _plan_outline(r, z)
    grown: list[tuple[float, float]] = []
    for x, y in points:
        length = math.hypot(x, y)
        scale = 1.0 + grow / length if length > 1e-6 else 1.0
        grown.append((x * scale, y * scale))
    # close across the front with the real front curve
    front: list[tuple[float, float]] = []
    steps = _PLAN_SEGMENTS
    half_w = r.carcass_width_m / 2.0 * _taper_scale(r, z)
    for i in range(steps + 1):
        x = half_w - 2.0 * half_w * i / steps
        front.append((x, _front_y(r, x, z) - grow))
    return grown + front


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def _wood_box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Box(size=(float(size[0]), float(size[1]), float(size[2]))),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name, material_class_id="wood.polished_varnished",
    )


def _tray_box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Box(size=(float(size[0]), float(size[1]), float(size[2]))),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name, material_class_id="wood.plywood",
    )


def _metal_box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Box(size=(float(size[0]), float(size[1]), float(size[2]))),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name, material_class_id="metal.brass_polished",
    )


def _cane_box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Box(size=(float(size[0]), float(size[1]), float(size[2]))),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name, material_class_id="wood.woven_plant_fiber",
    )


def _cy(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=float(radius), length=float(length)),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name, material_class_id="metal.brass_polished",
    )


def _materials(model: ArticulatedObject, palette: int) -> dict[str, object]:
    table = _PALETTES[palette % len(_PALETTES)]
    materials = {k: model.material(f"chest_{palette}_{k}", rgba=v) for k, v in table.items()}
    materials["tray"] = model.material(f"chest_{palette}_tray", rgba=table["wood"])
    return materials


def _slide_mate(*, provider_name, provider_point, provider_extent, consumer_name, consumer_extent):
    provider = PlaneInterface(
        name=provider_name,
        point=(float(provider_point[0]), float(provider_point[1]), float(provider_point[2])),
        normal=(0.0, -1.0, 0.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=provider_extent,
    )
    consumer = PlaneInterface(
        name=consumer_name,
        point=(0.0, 0.0, 0.0),
        normal=(0.0, 1.0, 0.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=consumer_extent,
    )
    return mate_planes(provider, consumer)


# ---------------------------------------------------------------------------
# body_form candidates
# ---------------------------------------------------------------------------
def _build_case_shell(carcass, r: ResolvedConfig, mats, tag: str) -> None:
    z0, z1 = r.body_bottom_z_m, r.body_top_z_m
    shell_z0, shell_z1 = z0 + _BASE_T, z1 - _TOP_T
    levels = (shell_z0, (shell_z0 + shell_z1) / 2.0, shell_z1)
    y_open = _front_open_y(r)
    profiles = []
    for z in levels:
        profiles.append([(x, y, z) for x, y in _shell_profile(r, z, y_open)])
    shell = mesh_from_geometry(LoftGeometry(profiles), f"{tag}__shell_mesh")
    carcass.visual(shell, material=mats["wood"], name=f"{tag}__case_shell", material_class_id="wood.polished_varnished")
    top = mesh_from_geometry(
        ExtrudeGeometry(_solid_slab_profile(r, z1, 0.014), _TOP_T, center=False),
        f"{tag}__top_mesh",
    )
    carcass.visual(
        top,
        origin=Origin(xyz=(0.0, 0.0, z1 - _TOP_T)),
        material=mats["wood"],
        name=f"{tag}__top_slab", material_class_id="wood.polished_varnished",
    )
    base = mesh_from_geometry(
        ExtrudeGeometry(_solid_slab_profile(r, z0, 0.0), _BASE_T, center=False),
        f"{tag}__base_mesh",
    )
    carcass.visual(
        base,
        origin=Origin(xyz=(0.0, 0.0, z0)),
        material=mats["wood"],
        name=f"{tag}__base_panel", material_class_id="wood.polished_varnished",
    )


def _body_form_rect_case_build(carcass, r: ResolvedConfig, mats) -> None:
    _build_case_shell(carcass, r, mats, "body_form__rect_case")


def _body_form_bombe_serpentine_build(carcass, r: ResolvedConfig, mats) -> None:
    _build_case_shell(carcass, r, mats, "body_form__bombe_serpentine")


def _body_form_oval_rounded_build(carcass, r: ResolvedConfig, mats) -> None:
    _build_case_shell(carcass, r, mats, "body_form__oval_rounded")


def _body_form_bow_front_build(carcass, r: ResolvedConfig, mats) -> None:
    _build_case_shell(carcass, r, mats, "body_form__bow_front")


def _body_form_tapered_case_build(carcass, r: ResolvedConfig, mats) -> None:
    _build_case_shell(carcass, r, mats, "body_form__tapered_case")


_BODY_BUILDERS = {
    "rect_case": _body_form_rect_case_build,
    "bombe_serpentine": _body_form_bombe_serpentine_build,
    "oval_rounded": _body_form_oval_rounded_build,
    "bow_front": _body_form_bow_front_build,
    "tapered_case": _body_form_tapered_case_build,
}


# ---------------------------------------------------------------------------
# support_base candidates
# ---------------------------------------------------------------------------
def _corner_positions(r: ResolvedConfig, inset: float) -> list[tuple[float, float]]:
    lx = max(r.carcass_width_m / 2 - inset, 0.05)
    ly = max(r.carcass_depth_m / 2 - inset, 0.05)
    return [(-lx, -ly), (lx, -ly), (-lx, ly), (lx, ly)]


def _rect_ring(cx: float, cy: float, z: float, sx: float, sy: float) -> list[tuple[float, float, float]]:
    """A clipped-corner rectangular section for a furniture leg loft."""

    hx, hy = sx / 2.0, sy / 2.0
    clip = min(hx, hy) * 0.18
    return [
        (cx - hx + clip, cy - hy, z),
        (cx + hx - clip, cy - hy, z),
        (cx + hx, cy - hy + clip, z),
        (cx + hx, cy + hy - clip, z),
        (cx + hx - clip, cy + hy, z),
        (cx - hx + clip, cy + hy, z),
        (cx - hx, cy + hy - clip, z),
        (cx - hx, cy - hy + clip, z),
    ]


def _round_ring(cx: float, cy: float, z: float, radius: float, segments: int = 12) -> list[tuple[float, float, float]]:
    return [
        (
            cx + radius * math.cos(2.0 * math.pi * i / segments),
            cy + radius * math.sin(2.0 * math.pi * i / segments),
            z,
        )
        for i in range(segments)
    ]


def _loft_support_leg(
    carcass,
    *,
    x: float,
    y: float,
    h: float,
    sx: float,
    sy: float,
    tag: str,
    material,
    style: str,
    bottom_z: float = 0.0,
) -> None:
    """Build one continuous shaped leg instead of a stack of cuboids."""

    sign_x = -1.0 if x < 0.0 else 1.0
    sign_y = -1.0 if y < 0.0 else 1.0
    if style == "cabriole":
        stations = (
            (0.000, x + sign_x * 0.040, y + sign_y * 0.022, sx * 0.92, sy * 0.92),
            (0.085, x + sign_x * 0.045, y + sign_y * 0.024, sx * 1.08, sy * 1.02),
            (0.340, x + sign_x * 0.018, y + sign_y * 0.010, sx * 0.62, sy * 0.64),
            (0.620, x - sign_x * 0.012, y - sign_y * 0.004, sx * 0.72, sy * 0.70),
            (0.860, x - sign_x * 0.004, y, sx * 0.88, sy * 0.84),
            (1.000, x, y, sx, sy),
        )
    else:
        stations = (
            (0.000, x + sign_x * 0.038, y + sign_y * 0.028, sx * 0.72, sy * 0.72),
            (0.100, x + sign_x * 0.040, y + sign_y * 0.029, sx * 0.86, sy * 0.84),
            (0.700, x + sign_x * 0.012, y + sign_y * 0.009, sx * 0.62, sy * 0.64),
            (1.000, x, y, sx, sy),
        )
    rings = [
        _rect_ring(cx, cy, bottom_z + h * fraction, wx, wy)
        for fraction, cx, cy, wx, wy in stations
    ]
    leg = mesh_from_geometry(LoftGeometry(rings, cap=True, closed=True), f"{tag}__shaped_leg")
    carcass.visual(leg, material=material, name=f"{tag}__shaped_leg", material_class_id="wood.polished_varnished")


def _loft_turned_leg(carcass, *, x: float, y: float, h: float, tag: str, material) -> None:
    """Turned metal support with a foot, collar and tapered shaft."""

    stations = (
        (0.000, 0.020),
        (0.045, 0.022),
        (0.100, 0.016),
        (0.720, 0.011),
        (0.900, 0.016),
        (1.000, 0.020),
    )
    rings = [_round_ring(x, y, h * fraction, radius) for fraction, radius in stations]
    leg = mesh_from_geometry(LoftGeometry(rings, cap=True, closed=True), f"{tag}__turned_leg")
    carcass.visual(leg, material=material, name=f"{tag}__turned_leg", material_class_id="metal.brass_polished")
    _cy(carcass, 0.024, 0.012, (x, y, 0.006), material, f"{tag}__foot")


def _apron_band(carcass, r: ResolvedConfig, mats, tag: str, height: float) -> None:
    """Shaped skirt under the case, following the host front curve."""

    z = r.body_bottom_z_m
    steps = 8
    half_w = r.carcass_width_m / 2.0 * 0.86
    for i in range(steps):
        x0 = -half_w + 2 * half_w * i / steps
        x1 = -half_w + 2 * half_w * (i + 1) / steps
        cx = (x0 + x1) / 2.0
        scallop = height * (0.55 + 0.45 * abs(math.sin(math.pi * (i + 0.5) / steps)))
        _wood_box(
            carcass,
            (x1 - x0 + 0.004, 0.020, scallop),
            (cx, _front_y(r, cx, z) + 0.012, z - scallop / 2 + 0.006),
            mats["wood"],
            f"{tag}__apron_{i}",
        )


def _support_base_cabriole_apron_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "support_base__cabriole_apron"
    h = r.body_bottom_z_m
    for i, (x, y) in enumerate(_corner_positions(r, 0.055)):
        _loft_support_leg(
            carcass,
            x=x,
            y=y,
            h=h + 0.006,
            sx=0.052,
            sy=0.050,
            tag=f"{tag}__cabriole_{i}",
            material=mats["wood"],
            style="cabriole",
        )
    _apron_band(carcass, r, mats, tag, h * 0.42)


def _support_base_fine_metal_legs_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "support_base__fine_metal_legs"
    h = r.body_bottom_z_m
    for i, (x, y) in enumerate(_corner_positions(r, 0.075)):
        _loft_turned_leg(carcass, x=x, y=y, h=h + 0.010, tag=f"{tag}__leg_{i}", material=mats["metal"])
        _cy(carcass, 0.022, 0.010, (x, y, 0.005), mats["metal"], f"{tag}__metal_sole_{i}")


def _support_base_plinth_block_feet_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "support_base__plinth_block_feet"
    h = r.body_bottom_z_m
    for i, (x, y) in enumerate(_corner_positions(r, 0.050)):
        rings = [
            _rect_ring(x, y, 0.0, 0.102, 0.098),
            _rect_ring(x, y, h * 0.18, 0.094, 0.091),
            _rect_ring(x, y, h * 0.62, 0.075, 0.074),
        ]
        foot = mesh_from_geometry(
            LoftGeometry(rings, cap=True, closed=True), f"{tag}__block_foot_{i}"
        )
        carcass.visual(foot, material=mats["wood"], name=f"{tag}__block_foot_{i}", material_class_id="wood.polished_varnished")
        _wood_box(carcass, (0.092, 0.090, 0.018), (x, y, h * 0.64), mats["wood"], f"{tag}__foot_cap_{i}")
    _wood_box(
        carcass,
        (r.carcass_width_m * 0.94, r.carcass_depth_m * 0.94, h * 0.46),
        (0.0, 0.0, h - h * 0.23),
        mats["wood"],
        f"{tag}__base_plinth",
    )


def _support_base_splayed_tapered_legs_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "support_base__splayed_tapered_legs"
    h = r.body_bottom_z_m
    for i, (x, y) in enumerate(_corner_positions(r, 0.070)):
        _loft_support_leg(
            carcass,
            x=x,
            y=y,
            h=h - 0.014,
            sx=0.054,
            sy=0.052,
            tag=f"{tag}__splayed_leg_{i}",
            material=mats["wood"],
            style="splayed",
            bottom_z=0.020,
        )
        _metal_box(carcass, (0.046, 0.046, 0.020), (x, y, 0.010), mats["metal"], f"{tag}__leg_shoe_{i}")


def _support_base_tapered_legs_apron_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "support_base__tapered_legs_apron"
    h = r.body_bottom_z_m
    for i, (x, y) in enumerate(_corner_positions(r, 0.060)):
        _loft_support_leg(
            carcass,
            x=x,
            y=y,
            h=h + 0.006,
            sx=0.050,
            sy=0.048,
            tag=f"{tag}__tapered_leg_{i}",
            material=mats["wood"],
            style="tapered",
        )
    _apron_band(carcass, r, mats, tag, h * 0.34)


def _support_base_toe_kick_plinth_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "support_base__toe_kick_plinth"
    h = r.body_bottom_z_m
    _wood_box(
        carcass,
        (r.carcass_width_m - 0.070, r.carcass_depth_m - 0.060, h + 0.008),
        (0.0, 0.020, (h + 0.008) / 2.0),
        mats["wood"],
        f"{tag}__toe_kick_box",
    )


_SUPPORT_BUILDERS = {
    "cabriole_apron": _support_base_cabriole_apron_build,
    "fine_metal_legs": _support_base_fine_metal_legs_build,
    "plinth_block_feet": _support_base_plinth_block_feet_build,
    "splayed_tapered_legs": _support_base_splayed_tapered_legs_build,
    "tapered_legs_apron": _support_base_tapered_legs_apron_build,
    "toe_kick_plinth": _support_base_toe_kick_plinth_build,
}


# ---------------------------------------------------------------------------
# drawer_layout candidates — runner rails, divider and the cell table
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Cell:
    index: int
    x0: float
    x1: float
    z0: float
    z1: float
    y_front: float
    y_back: float


def _cells(r: ResolvedConfig) -> list[_Cell]:
    """Drawer cells bottom to top, left to right, adapted to the host profile."""

    out: list[_Cell] = []
    index = 0
    for level, columns in enumerate(r.level_columns):
        z0, z1 = r.level_bounds[level]
        # the narrowest point of the level is at its top on a tapered case
        inner, y0, y1 = _level_window(r, z1)
        if columns == 1:
            out.append(_Cell(index, -inner, inner, z0, z1, y0, y1))
            index += 1
            continue
        half_div = min(r.divider_t_m / 2.0, max(inner - _MIN_DRAWER_W - 0.02, 0.006))
        for side in (0, 1):
            cx0 = -inner if side == 0 else half_div
            cx1 = -half_div if side == 0 else inner
            out.append(_Cell(index, cx0, cx1, z0, z1, y0, y1))
            index += 1
    return out


def _build_rails(carcass, r: ResolvedConfig, mats, tag: str) -> None:
    for cell in _cells(r):
        # Keep the fixed runner behind the face/stile line.  The moving
        # runner still spans the full tray depth, so this recess only hides
        # the exposed hardware nose at the front of an open drawer.
        y0 = cell.y_front + _RAIL_FRONT_RECESS
        y1 = cell.y_back + 0.004
        # the rail is let into the level rail (or the base panel) below it
        rail_z = cell.z0 + _RAIL_H / 2.0 - 0.002
        for side, raw_x in ((0, cell.x0), (1, cell.x1)):
            edge_x = _adapt_edge_x(r, raw_x, cell.z0, cell.z1)
            back_half = max(r.carcass_depth_m / 2.0, 1e-4)
            outer: list[tuple[float, float]] = []
            inner: list[tuple[float, float]] = []
            for i in range(_TRAY_PROFILE_SAMPLES + 1):
                y = y0 + (y1 - y0) * i / _TRAY_PROFILE_SAMPLES
                v = _clamp(y / back_half, -1.0, 1.0)
                wall_edge = _side_x(r, v, cell.z1) - r.wall_t_m + _RAIL_EMBED
                if side == 0:
                    outer_x = min(-wall_edge, edge_x - _RAIL_EMBED)
                    inner_x = edge_x + _RAIL_W
                else:
                    outer_x = max(wall_edge, edge_x + _RAIL_EMBED)
                    inner_x = edge_x - _RAIL_W
                outer.append((outer_x, y))
                inner.append((inner_x, y))
            profile = outer + list(reversed(inner))
            rail = mesh_from_geometry(
                ExtrudeGeometry(profile, _RAIL_H, center=False),
                f"{tag}__runner_rail_mesh_{cell.index}_{side}",
            )
            carcass.visual(
                rail,
                origin=Origin(xyz=(0.0, 0.0, rail_z - _RAIL_H / 2.0)),
                material=mats["wood"],
                name=f"{tag}__runner_rail_{cell.index}_{side}", material_class_id="wood.polished_varnished",
            )


def _build_divider(carcass, r: ResolvedConfig, mats, tag: str) -> None:
    by_level: dict[int, list[_Cell]] = {}
    index = 0
    for level, columns in enumerate(r.level_columns):
        by_level[level] = []
        index += columns
    cells = _cells(r)
    cursor = 0
    for level, columns in enumerate(r.level_columns):
        group = cells[cursor : cursor + columns]
        cursor += columns
        if columns < 2:
            continue
        z0, z1 = r.level_bounds[level]
        y0 = min(c.y_front for c in group) - 0.004
        y1 = max(c.y_back for c in group)
        _wood_box(
            carcass,
            (r.divider_t_m, max(y1 - y0, 0.10), z1 - z0 + 0.010),
            (0.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0),
            mats["wood"],
            f"{tag}__centre_divider_{level}",
        )


def _build_level_rails(carcass, r: ResolvedConfig, mats, tag: str) -> None:
    """Horizontal dust rail between levels, tying the side rails together."""

    cells = _cells(r)
    cursor = 0
    for level, columns in enumerate(r.level_columns):
        group = cells[cursor : cursor + columns]
        cursor += columns
        if level == 0:
            continue
        z0, _z1 = r.level_bounds[level]
        y0 = min(c.y_front for c in group) + _RAIL_FRONT_RECESS
        y1 = max(c.y_back for c in group)
        back_half = max(r.carcass_depth_m / 2.0, 1e-4)
        left: list[tuple[float, float]] = []
        right: list[tuple[float, float]] = []
        for i in range(_TRAY_PROFILE_SAMPLES + 1):
            y = y0 + (y1 - y0) * i / _TRAY_PROFILE_SAMPLES
            v = _clamp(y / back_half, -1.0, 1.0)
            half = _side_x(r, v, z0) - r.wall_t_m + _RAIL_EMBED
            left.append((-half, y))
            right.append((half, y))
        rail = mesh_from_geometry(
            ExtrudeGeometry(left + list(reversed(right)), 0.010, center=False),
            f"{tag}__level_rail_mesh_{level}",
        )
        carcass.visual(
            rail,
            origin=Origin(xyz=(0.0, 0.0, z0 - _LEVEL_REVEAL / 2.0 - 0.005)),
            material=mats["wood"],
            name=f"{tag}__level_rail_{level}", material_class_id="wood.polished_varnished",
        )


def _drawer_layout_full_width_stack_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "drawer_layout__full_width_stack"
    _build_level_rails(carcass, r, mats, tag)
    _build_rails(carcass, r, mats, tag)


def _drawer_layout_paired_grid_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "drawer_layout__paired_grid"
    _build_level_rails(carcass, r, mats, tag)
    _build_divider(carcass, r, mats, tag)
    _build_rails(carcass, r, mats, tag)


def _drawer_layout_pair_over_full_width_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "drawer_layout__pair_over_full_width"
    _build_level_rails(carcass, r, mats, tag)
    _build_divider(carcass, r, mats, tag)
    _build_rails(carcass, r, mats, tag)


_LAYOUT_BUILDERS = {
    "full_width_stack": _drawer_layout_full_width_stack_build,
    "paired_grid": _drawer_layout_paired_grid_build,
    "pair_over_full_width": _drawer_layout_pair_over_full_width_build,
}


# ---------------------------------------------------------------------------
# drawer_front candidates — authored in drawer-local coordinates
#
# Drawer-local frame: origin at (cell centre x, cell front y, cell floor z);
# +Y is into the cavity, so all front geometry sits at local y <= 0.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Frame:
    cx: float
    y_ref: float
    z_ref: float
    edge_ref_z: float


def _front_panel_section(
    r: ResolvedConfig, x0: float, x1: float, z: float, f: _Frame
) -> list[tuple[float, float, float]]:
    """One horizontal section of a front panel, following the slot outline."""

    outer: list[tuple[float, float, float]] = []
    inner: list[tuple[float, float, float]] = []
    for x, y in _panel_back_section(r, x0, x1, z, f):
        outer.append((x - f.cx, y - r.front_t_m - f.y_ref, z - f.z_ref))
        inner.append((x - f.cx, y - f.y_ref, z - f.z_ref))
    return outer + list(reversed(inner))


def _panel_back_section(
    r: ResolvedConfig, x0: float, x1: float, z: float, f: _Frame
) -> list[tuple[float, float]]:
    """The exact sampled back edge consumed by the panel loft and drawer tray."""

    points: list[tuple[float, float]] = []
    for i in range(_TRAY_PROFILE_SAMPLES + 1):
        nominal_x = x0 + (x1 - x0) * i / _TRAY_PROFILE_SAMPLES
        x = _adapt_edge_x(r, nominal_x, z, f.edge_ref_z)
        points.append((x, _front_y(r, x, z) - _FRONT_GAP))
    return points


def _front_face_y(r: ResolvedConfig, x: float, z: float, f: _Frame) -> float:
    """Local y of the outer front surface at plan coordinate x."""

    return _front_y(r, x, z) - _FRONT_GAP - r.front_t_m - f.y_ref


def _panel_face_y(
    r: ResolvedConfig, nominal_x: float, cz: float, height: float, z: float, f: _Frame
) -> float:
    """Outer face of the actual two-section loft, not the analytic host curve."""

    low, high = cz - height / 2.0, cz + height / 2.0
    t = _clamp((z - low) / max(height, 1e-6), 0.0, 1.0)
    ys = []
    for section_z in (low, high):
        x = _adapt_edge_x(r, nominal_x, section_z, f.edge_ref_z)
        ys.append(_front_y(r, x, section_z) - _FRONT_GAP - r.front_t_m - f.y_ref)
    return ys[0] * (1.0 - t) + ys[1] * t


def _panel_back_y_at_actual_x(
    r: ResolvedConfig,
    actual_x: float,
    panel_x0: float,
    panel_x1: float,
    cz: float,
    height: float,
    z: float,
    f: _Frame,
) -> float:
    """Interpolate the exact triangles used by the panel loft's back surface."""

    low_z, high_z = cz - height / 2.0, cz + height / 2.0
    query_z = _clamp(z, low_z, high_z)
    low = _panel_back_section(r, panel_x0, panel_x1, low_z, f)
    high = _panel_back_section(r, panel_x0, panel_x1, high_z, f)

    def interpolate(triangle):
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = triangle
        denominator = (z1 - z2) * (x0 - x2) + (x2 - x1) * (z0 - z2)
        if abs(denominator) <= 1e-12:
            return None
        a = ((z1 - z2) * (actual_x - x2) + (x2 - x1) * (query_z - z2)) / denominator
        b = ((z2 - z0) * (actual_x - x2) + (x0 - x2) * (query_z - z2)) / denominator
        c = 1.0 - a - b
        if min(a, b, c) < -1e-8:
            return None
        return a * y0 + b * y1 + c * y2

    for i in range(_TRAY_PROFILE_SAMPLES):
        low_left = (*low[i], low_z)
        low_right = (*low[i + 1], low_z)
        high_left = (*high[i], high_z)
        high_right = (*high[i + 1], high_z)
        for triangle in (
            (low_right, low_left, high_left),
            (low_right, high_left, high_right),
        ):
            value = interpolate(triangle)
            if value is not None:
                return value
    raise ValueError("tray front point lies outside the shared panel back mesh")


def _hardware_seat_y(
    r: ResolvedConfig,
    x: float,
    cz: float,
    height: float,
    z: float,
    f: _Frame,
    radius: float,
) -> float:
    """Seat a circular fitting against the outermost loft point under its footprint."""

    samples = (
        _panel_face_y(r, x + radius * i / 4.0, cz, height, z, f)
        for i in range(-4, 5)
    )
    return min(samples)


def _fitted_pull_stem(drawer, r, mats, f: _Frame, cz: float, height: float, tag: str) -> None:
    """A brass neck whose inner end follows the curved front exactly."""

    radius = 0.003
    segments = 16
    inner: list[tuple[float, float, float]] = []
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        x = radius * math.cos(angle)
        z_local = cz - f.z_ref + radius * math.sin(angle)
        y = _panel_face_y(r, f.cx + x, cz, height, f.z_ref + z_local, f)
        inner.append((x, y, z_local))
    outer_y = min(point[1] for point in inner) - 0.018
    vertices = inner + [(x, outer_y, z) for x, _y, z in inner]
    faces: list[tuple[int, int, int]] = []
    for i in range(segments):
        j = (i + 1) % segments
        faces.extend(((i, j, segments + j), (i, segments + j, segments + i)))
    for i in range(1, segments - 1):
        faces.append((0, i + 1, i))
        faces.append((segments, segments + i, segments + i + 1))
    stem = mesh_from_geometry(MeshGeometry(vertices=vertices, faces=faces), f"{tag}__pull_stem_mesh")
    drawer.visual(
        stem,
        material=mats["metal"],
        name=f"{tag}__pull_stem", material_class_id="metal.brass_polished",
    )


def _drawer_front_reach(r: ResolvedConfig, x0: float, x1: float, z: float, y_ref: float) -> float:
    """Return the tray reach needed to touch the whole front-panel back edge."""

    samples = 12
    panel_back = [
        _front_y(r, x0 + (x1 - x0) * i / samples, z) - _FRONT_GAP
        for i in range(samples + 1)
    ]
    return max(_TRAY_FRONT_REACH, y_ref - min(panel_back) + 0.003)


def _drawer_pull(drawer, r, mats, f: _Frame, cz, width, height, tag, style: str) -> None:
    zc = cz - f.z_ref
    if style == "handleless":
        return
    if style == "knob":
        offsets = (-1.0, 1.0) if width > 0.34 else (0.0,)
        for i, sign in enumerate(offsets):
            x = f.cx + sign * width * 0.24
            y = _hardware_seat_y(r, x, cz, height, cz, f, 0.005)
            _cy(drawer, 0.014, 0.008, (x - f.cx, y - 0.004, zc), mats["metal"],
                f"{tag}__pull_rosette_{i}", rpy=(math.pi / 2, 0, 0))
            _cy(drawer, 0.005, 0.018, (x - f.cx, y - 0.013, zc), mats["metal"],
                f"{tag}__pull_stem_{i}", rpy=(math.pi / 2, 0, 0))
            drawer.visual(
                Sphere(radius=0.013),
                origin=Origin(xyz=(x - f.cx, y - 0.026, zc)),
                material=mats["metal"],
                name=f"{tag}__pull_knob_{i}", material_class_id="metal.brass_polished",
            )
        return
    if style == "bail":
        y = _hardware_seat_y(r, f.cx, cz, height, cz, f, 0.070)
        _metal_box(drawer, (min(0.140, width * 0.5), 0.008, min(0.048, height * 0.5)),
            (0.0, y - 0.004, zc), mats["metal"], f"{tag}__pull_backplate")
        _cy(drawer, 0.005, min(0.120, width * 0.42), (0.0, y - 0.004, zc - 0.012),
            mats["metal"], f"{tag}__pull_bail", rpy=(0.0, math.pi / 2, 0.0))
        for i, sign in enumerate((-1.0, 1.0)):
            _cy(drawer, 0.004, 0.016, (sign * min(0.060, width * 0.21), y - 0.012, zc),
                mats["metal"], f"{tag}__pull_boss_{i}", rpy=(math.pi / 2, 0, 0))
        return
    y = _panel_face_y(r, f.cx, cz, height, cz, f)
    _fitted_pull_stem(drawer, r, mats, f, cz, height, tag)
    _cy(drawer, 0.013, 0.010, (0.0, y - 0.018, zc), mats["metal"], f"{tag}__pull",
        rpy=(math.pi / 2, 0, 0))


def _front_slab(drawer, r, mats, x0, x1, cz, height, f: _Frame, tag, material_key: str) -> None:
    panel = mesh_from_geometry(
        LoftGeometry(
            [
                _front_panel_section(r, x0, x1, cz - height / 2.0, f),
                _front_panel_section(r, x0, x1, cz + height / 2.0, f),
            ],
            cap=True,
            closed=True,
        ),
        f"{tag}__front_mesh",
    )
    drawer.visual(
        panel,
        material=mats[material_key],
        name=f"{tag}__drawer_front", material_class_id="wood.veneer_panel",
    )


def _drawer_front_flat_panel_build(drawer, r, mats, x0, x1, cz, height, f, tag) -> None:
    _front_slab(drawer, r, mats, x0, x1, cz, height, f, tag, "panel")
    _drawer_pull(drawer, r, mats, f, cz, x1 - x0, height, tag, "round")


def _drawer_front_framed_cane_build(drawer, r, mats, x0, x1, cz, height, f, tag) -> None:
    width = x1 - x0
    _front_slab(drawer, r, mats, x0, x1, cz, height, f, tag, "wood")
    zc = cz - f.z_ref
    frame_w = min(r.cane_frame_w_m, width * 0.24, height * 0.30)
    field_w = max(width - 2 * frame_w, width * 0.20)
    field_h = max(height - 2 * frame_w, height * 0.20)
    y_mid = _panel_face_y(r, f.cx, cz, height, cz, f)
    _cane_box(drawer, (field_w, 0.007, field_h), (0.0, y_mid - 0.0035, zc), mats["accent"],
        f"{tag}__cane_panel")
    for j in range(3):
        x = f.cx + (j - 1) * field_w / 3.0
        _wood_box(drawer, (0.005, 0.007, field_h), (x - f.cx, y_mid - 0.0105, zc),
            mats["dark"], f"{tag}__cane_reed_v{j}")
    for j in range(3):
        _wood_box(drawer, (field_w, 0.007, 0.005), (0.0, y_mid - 0.0105, zc + (j - 1) * field_h / 3.0),
            mats["dark"], f"{tag}__cane_reed_h{j}")
    _drawer_pull(drawer, r, mats, f, cz, width, height, tag, "round")


def _drawer_front_gothic_arch_build(drawer, r, mats, x0, x1, cz, height, f, tag) -> None:
    width = x1 - x0
    _front_slab(drawer, r, mats, x0, x1, cz, height, f, tag, "panel")
    zc = cz - f.z_ref
    rise = _clamp(r.arch_rise_ratio, 0.20, 0.80) * height * 0.6
    steps = 5
    for j in range(steps):
        t0, t1 = j / steps, (j + 1) / steps
        for side, sign in enumerate((-1.0, 1.0)):
            xa = f.cx + sign * (width * 0.38) * (1.0 - t0)
            xb = f.cx + sign * (width * 0.38) * (1.0 - t1)
            za = zc - height * 0.28 + rise * t0
            zb = zc - height * 0.28 + rise * t1
            xm = (xa + xb) / 2.0
            _wood_box(
                drawer,
                (abs(xa - xb) + 0.012, 0.008, abs(zb - za) + 0.012),
                (xm - f.cx, _panel_face_y(r, xm, cz, height, cz, f) - 0.004, (za + zb) / 2.0),
                mats["dark"],
                f"{tag}__gothic_slope_{side}_{j}",
            )
    _wood_box(drawer, (width * 0.80, 0.008, 0.010),
        (0.0, _panel_face_y(r, f.cx, cz, height, cz, f) - 0.004, zc - height * 0.30),
        mats["dark"], f"{tag}__gothic_sill")
    _drawer_pull(drawer, r, mats, f, cz, width, height, tag, "knob")


def _drawer_front_applique_moulded_build(drawer, r, mats, x0, x1, cz, height, f, tag) -> None:
    width = x1 - x0
    _front_slab(drawer, r, mats, x0, x1, cz, height, f, tag, "panel")
    zc = cz - f.z_ref
    relief = r.applique_relief_m
    y_mid = _panel_face_y(r, f.cx, cz, height, cz, f)
    _metal_box(drawer, (min(0.150, width * 0.34), relief, min(0.060, height * 0.42)),
        (0.0, y_mid - relief / 2, zc), mats["metal"], f"{tag}__centre_crest")
    for i, (sx, sz) in enumerate(((-1.0, 1.0), (1.0, 1.0), (-1.0, -1.0), (1.0, -1.0))):
        nominal_x = f.cx + sx * width * 0.36
        # The front slab follows the case profile at every height.  Apply the
        # same width adaptation to the relief so corner details cannot float
        # off the upper/lower edge of a curved or tapered panel.
        corner_z = cz + sz * height * 0.26
        x = _adapt_edge_x(r, nominal_x, corner_z, f.edge_ref_z)
        _metal_box(
            drawer,
            (min(0.070, width * 0.16), relief, min(0.030, height * 0.24)),
            (
                x - f.cx,
                _panel_face_y(r, nominal_x, cz, height, corner_z, f) - relief / 2,
                corner_z - f.z_ref,
            ),
            mats["metal"],
            f"{tag}__corner_scroll_{i}",
        )
    _drawer_pull(drawer, r, mats, f, cz, width, height, tag, "bail")


_FRONT_BUILDERS = {
    "flat_panel": _drawer_front_flat_panel_build,
    "framed_cane": _drawer_front_framed_cane_build,
    "gothic_arch": _drawer_front_gothic_arch_build,
    "applique_moulded": _drawer_front_applique_moulded_build,
}


# ---------------------------------------------------------------------------
# drawer assembly
# ---------------------------------------------------------------------------
def _tray_edges(
    r: ResolvedConfig, x0: float, x1: float, z: float, reference_z: float
) -> tuple[float, float]:
    opening_x0 = _adapt_edge_x(r, x0, z, reference_z)
    opening_x1 = _adapt_edge_x(r, x1, z, reference_z)
    return (
        opening_x0 + _RAIL_W + _SIDE_CLEAR,
        opening_x1 - _RAIL_W - _SIDE_CLEAR,
    )


def _tray_floor_profile(
    r: ResolvedConfig,
    *,
    x0: float,
    x1: float,
    z: float,
    reference_z: float,
    y_ref: float,
    rear_y: float,
    cx: float,
    panel_cz: float,
    panel_height: float,
    frame: _Frame,
) -> list[tuple[float, float]]:
    tray_x0, tray_x1 = _tray_edges(r, x0, x1, z, reference_z)
    front: list[tuple[float, float]] = []
    rear: list[tuple[float, float]] = []
    for i in range(_TRAY_PROFILE_SAMPLES + 1):
        x = tray_x0 + (tray_x1 - tray_x0) * i / _TRAY_PROFILE_SAMPLES
        front_y = max(
            _panel_back_y_at_actual_x(
                r, x, x0, x1, panel_cz, panel_height, z, frame
            ),
            _panel_back_y_at_actual_x(
                r,
                x,
                x0,
                x1,
                panel_cz,
                panel_height,
                z + _TRAY_FLOOR_T,
                frame,
            ),
        )
        front.append((x - cx, front_y - y_ref))
        rear.append((x - cx, rear_y - _TRAY_WALL_T - y_ref))
    return front + list(reversed(rear))


def _tray_side_section(
    r: ResolvedConfig,
    *,
    x0: float,
    x1: float,
    z: float,
    reference_z: float,
    y_ref: float,
    rear_y: float,
    cx: float,
    side: int,
    z_local: float,
    panel_cz: float,
    panel_height: float,
    frame: _Frame,
) -> list[tuple[float, float, float]]:
    tray_x0, tray_x1 = _tray_edges(r, x0, x1, z, reference_z)
    if side == 0:
        x_outer, x_inner = tray_x0, tray_x0 + _TRAY_WALL_T
    else:
        x_inner, x_outer = tray_x1 - _TRAY_WALL_T, tray_x1
    front_outer = (
        _panel_back_y_at_actual_x(
            r, x_outer, x0, x1, panel_cz, panel_height, z, frame
        )
    )
    front_inner = (
        _panel_back_y_at_actual_x(
            r, x_inner, x0, x1, panel_cz, panel_height, z, frame
        )
    )
    if side == 0:
        # The panel's sampled back face is triangulated from right to left.
        # Match that order so the shared non-planar quad has the same diagonal.
        return [
            (x_inner - cx, front_inner - y_ref, z_local),
            (x_outer - cx, front_outer - y_ref, z_local),
            (x_outer - cx, rear_y - y_ref, z_local),
            (x_inner - cx, rear_y - y_ref, z_local),
        ]
    return [
        (x_outer - cx, front_outer - y_ref, z_local),
        (x_inner - cx, front_inner - y_ref, z_local),
        (x_inner - cx, rear_y - y_ref, z_local),
        (x_outer - cx, rear_y - y_ref, z_local),
    ]


def _tray_rear_section(
    r: ResolvedConfig,
    *,
    x0: float,
    x1: float,
    z: float,
    reference_z: float,
    y_ref: float,
    rear_y: float,
    cx: float,
    z_local: float,
) -> list[tuple[float, float, float]]:
    tray_x0, tray_x1 = _tray_edges(r, x0, x1, z, reference_z)
    return [
        (tray_x0 + _TRAY_WALL_T - cx, rear_y - _TRAY_WALL_T - y_ref, z_local),
        (tray_x1 - _TRAY_WALL_T - cx, rear_y - _TRAY_WALL_T - y_ref, z_local),
        (tray_x1 - _TRAY_WALL_T - cx, rear_y - y_ref, z_local),
        (tray_x0 + _TRAY_WALL_T - cx, rear_y - y_ref, z_local),
    ]


def _build_drawers(model, carcass, r: ResolvedConfig, mats) -> list[object]:
    tag = f"drawer_front__{r.drawer_front}"
    drawers: list[object] = []
    for cell in _cells(r):
        cell_w = cell.x1 - cell.x0
        cx = (cell.x0 + cell.x1) / 2.0
        cz = (cell.z0 + cell.z1) / 2.0
        front_h = max(cell.z1 - cell.z0, _MIN_FRONT_H)
        front_reach = _drawer_front_reach(r, cell.x0, cell.x1, cz, cell.y_front)
        box_depth = max(cell.y_back - cell.y_front, 0.150) + front_reach
        travel = min(r.travel_m, box_depth * 0.60)
        box_h = max(front_h - 0.022, 0.045)
        floor_z = cell.z0 + 0.014
        rear_y = cell.y_front + box_depth - front_reach
        tray_x0, tray_x1 = _tray_edges(r, cell.x0, cell.x1, floor_z, cell.z1)
        tray_w = max(tray_x1 - tray_x0, _MIN_DRAWER_W)
        # The physical tray may widen slightly toward the lower part of a
        # tapered opening, but its registered seat must stay within the
        # nominal opening footprint exposed by the carcass.
        interface_tray_w = min(
            tray_w,
            max(cell_w - 2.0 * (_RAIL_W + _SIDE_CLEAR), _MIN_DRAWER_W),
        )
        frame = _Frame(cx=cx, y_ref=cell.y_front, z_ref=floor_z, edge_ref_z=cell.z1)
        panel_h = max(front_h - _LEVEL_REVEAL * 0.45, _MIN_FRONT_H)

        drawer = model.part(
            f"drawer_front__{r.drawer_front}__drawer_{cell.index}",
            meta={
                "role": "drawer",
                "slot": "drawer_front",
                "candidate": r.drawer_front,
                "level_index": cell.index,
                "hollow_tray": True,
                "travel_m": travel,
            },
        )
        # hollow tray: floor, two sides, rear wall — never a solid block.
        # The floor and side walls now extend to the actual curved face-back,
        # so the applied front is keyed into the tray rather than floating
        # ahead of a fixed-depth box.
        floor_mesh = mesh_from_geometry(
            ExtrudeGeometry(
                _tray_floor_profile(
                    r,
                    x0=cell.x0,
                    x1=cell.x1,
                    z=floor_z,
                    reference_z=cell.z1,
                    y_ref=cell.y_front,
                    rear_y=rear_y,
                    cx=cx,
                    panel_cz=cz,
                    panel_height=panel_h,
                    frame=frame,
                ),
                _TRAY_FLOOR_T,
                center=False,
            ),
            f"{tag}__tray_floor_mesh_{cell.index}",
        )
        drawer.visual(floor_mesh, material=mats["tray"], name=f"{tag}__tray_floor_{cell.index}", material_class_id="wood.plywood")
        top_z = floor_z + box_h
        for side, sign in enumerate((-1.0, 1.0)):
            side_mesh = mesh_from_geometry(
                LoftGeometry(
                    [
                        _tray_side_section(
                            r,
                            x0=cell.x0,
                            x1=cell.x1,
                            z=floor_z,
                            reference_z=cell.z1,
                            y_ref=cell.y_front,
                            rear_y=rear_y,
                            cx=cx,
                            side=side,
                            z_local=_TRAY_FLOOR_T,
                            panel_cz=cz,
                            panel_height=panel_h,
                            frame=frame,
                        ),
                        _tray_side_section(
                            r,
                            x0=cell.x0,
                            x1=cell.x1,
                            z=top_z,
                            reference_z=cell.z1,
                            y_ref=cell.y_front,
                            rear_y=rear_y,
                            cx=cx,
                            side=side,
                            z_local=box_h,
                            panel_cz=cz,
                            panel_height=panel_h,
                            frame=frame,
                        ),
                    ],
                    cap=True,
                    closed=True,
                ),
                f"{tag}__tray_side_mesh_{cell.index}_{side}",
            )
            drawer.visual(side_mesh, material=mats["tray"], name=f"{tag}__tray_side_{cell.index}_{side}", material_class_id="wood.plywood")
            # Stop the moving runner behind the applied front.  Its rear end
            # stays at the old datum, preserving contact with the fixed rail
            # through the full stroke without letting hardware cross the face.
            edge_x = tray_x0 if side == 0 else tray_x1
            runner_front = _RUNNER_FRONT_CLEAR
            runner_rear = box_depth - front_reach
            runner_depth = max(runner_rear - runner_front, 0.120)
            _wood_box(
                drawer,
                (_RUNNER_W, runner_depth, _RAIL_H),
                (
                    edge_x - cx + sign * (_RUNNER_W / 2.0),
                    (runner_front + runner_rear) / 2.0,
                    -0.001,
                ),
                mats["dark"],
                f"{tag}__tray_runner_{cell.index}_{side}",
            )
        rear_mesh = mesh_from_geometry(
            LoftGeometry(
                [
                    _tray_rear_section(
                        r,
                        x0=cell.x0,
                        x1=cell.x1,
                        z=floor_z,
                        reference_z=cell.z1,
                        y_ref=cell.y_front,
                        rear_y=rear_y,
                        cx=cx,
                        z_local=_TRAY_FLOOR_T,
                    ),
                    _tray_rear_section(
                        r,
                        x0=cell.x0,
                        x1=cell.x1,
                        z=top_z,
                        reference_z=cell.z1,
                        y_ref=cell.y_front,
                        rear_y=rear_y,
                        cx=cx,
                        z_local=box_h,
                    ),
                ],
                cap=True,
                closed=True,
            ),
            f"{tag}__tray_rear_mesh_{cell.index}",
        )
        drawer.visual(rear_mesh, material=mats["tray"], name=f"{tag}__tray_rear_{cell.index}", material_class_id="wood.plywood")

        # Keep the applied front inside its actual slot.  The old positive
        # reveal allowance made the lowest, oversized level cross the base
        # line and read as a dropped/oversized front when pulled out.
        _FRONT_BUILDERS[r.drawer_front](
            drawer, r, mats, cell.x0, cell.x1, cz, panel_h, frame, tag
        )

        mate = _slide_mate(
            provider_name=f"body_form.drawer_opening.cell_{cell.index}",
            provider_point=(cx, cell.y_front, floor_z),
            provider_extent=(cell_w, cell.z1 - cell.z0),
            consumer_name=f"drawer_front.tray_seat_{cell.index}",
            consumer_extent=(interface_tray_w, box_h),
        )
        joint = f"drawer_layout__{r.drawer_layout}__slide_{cell.index}"
        model.articulation(
            joint,
            ArticulationType.PRISMATIC,
            parent=carcass,
            child=drawer,
            origin=mate.origin,
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=60.0, velocity=0.30, lower=0.0, upper=travel),
            meta={"mechanism": "side runner pair riding on the carcass rails"},
        )
        register_interface_mate(model, joint, mate)
        drawers.append(drawer)
    return drawers


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
def build_drawer_cabinet_with_sliding_drawers(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r.palette)
    carcass = model.part(
        "carcass", meta={"role": "carcass", "slot": "body_form", "candidate": r.body_form}
    )
    _SUPPORT_BUILDERS[r.support_base](carcass, r, mats)
    _BODY_BUILDERS[r.body_form](carcass, r, mats)
    _LAYOUT_BUILDERS[r.drawer_layout](carcass, r, mats)
    _build_drawers(model, carcass, r, mats)
    carcass.inertial = None
    model.meta["slot_choices"] = (
        ("body_form", r.body_form),
        ("drawer_layout", r.drawer_layout),
        ("drawer_front", r.drawer_front),
        ("support_base", r.support_base),
        ("drawer_count", str(r.drawer_count)),
    )
    return model


def build_seeded_drawer_cabinet_with_sliding_drawers(seed: int) -> ArticulatedObject:
    return build_drawer_cabinet_with_sliding_drawers(config_from_seed(seed))


# ---------------------------------------------------------------------------
# author tests
# ---------------------------------------------------------------------------
def run_drawer_cabinet_with_sliding_drawers_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    parts = {p.name: p for p in object_model.parts}
    roles: dict[str, list[str]] = {}
    for part in object_model.parts:
        role = str(getattr(part, "meta", {}).get("role") or "")
        if role:
            roles.setdefault(role, []).append(part.name)

    ctx.check(
        "category_anchor: one load-bearing carcass",
        len(roles.get("carcass", [])) == 1,
        details=str(roles.get("carcass")),
    )

    drawer_names = roles.get("drawer", [])
    moving = {
        j.child: j
        for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
    }
    ctx.check(
        "category_anchor: every drawer is a moving child of the carcass",
        len(drawer_names) == r.drawer_count
        and all(
            name in moving
            and moving[name].parent == "carcass"
            and moving[name].articulation_type == ArticulationType.PRISMATIC
            for name in drawer_names
        ),
        details=f"drawers={drawer_names} expected={r.drawer_count}",
    )

    hollow = True
    details: list[str] = []
    for name in drawer_names:
        visuals = [str(v.name) for v in parts[name].visuals]
        has_floor = any("__tray_floor_" in v for v in visuals)
        has_sides = sum(1 for v in visuals if "__tray_side_" in v) == 2
        has_rear = any("__tray_rear_" in v for v in visuals)
        has_front = any("__drawer_front" in v for v in visuals)
        if not (has_floor and has_sides and has_rear and has_front):
            hollow = False
            details.append(f"{name}:{visuals}")
    ctx.check(
        "category_anchor: drawer trays are hollow boxes",
        hollow,
        details="; ".join(details)[:400] or "floor + two sides + rear + front on every tray",
    )

    name = drawer_names[0]
    joint = moving[name]
    rest = ctx.part_world_aabb(parts[name])
    with ctx.pose({joint: r.travel_m}):
        opened = ctx.part_world_aabb(parts[name])
    advanced = rest is not None and opened is not None and opened[0][1] < rest[0][1] - 0.02
    ctx.check(
        "category_anchor: drawer pulls out along -Y",
        advanced,
        details=f"rest_min_y={None if rest is None else round(rest[0][1], 4)} "
        f"open_min_y={None if opened is None else round(opened[0][1], 4)}",
    )

    ctx.check(
        "runner travel keeps the tray engaged with its rail",
        r.travel_m < r.box_depth_m * 0.66,
        details=f"travel={r.travel_m:.4f} box_depth={r.box_depth_m:.4f}",
    )

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    return ctx.report()


run_drawer_cabinet_with_sliding_drawers_tests.__test__ = False


TEMPLATE_CORNERS = (
    corner_case(
        "widest_bombe_six_paired_drawers",
        {
            "body_form": "bombe_serpentine",
            "drawer_layout": "paired_grid",
            "drawer_front": "applique_moulded",
            "support_base": "cabriole_apron",
            "drawer_count": 6,
            "carcass_width_m": 1.10,
            "carcass_depth_m": 0.52,
            "carcass_height_m": 1.16,
            "bombe_bulge_m": 0.055,
            "divider_t_m": 0.036,
            "drawer_travel_ratio": 0.62,
            "applique_relief_m": 0.014,
            "cabriole_h_m": 0.260,
        },
        reason="deepest swell with the most cells, widest divider and the longest stroke",
    ),
    corner_case(
        "narrow_oval_two_drawers_minimum",
        {
            "body_form": "oval_rounded",
            "drawer_layout": "pair_over_full_width",
            "drawer_front": "gothic_arch",
            "support_base": "fine_metal_legs",
            "drawer_count": 2,
            "carcass_width_m": 0.66,
            "carcass_depth_m": 0.36,
            "carcass_height_m": 0.74,
            "oval_end_ratio": 0.95,
            "arch_rise_ratio": 0.72,
            "drawer_travel_ratio": 0.36,
            "metal_leg_h_m": 0.320,
        },
        reason="strongest oval curvature on the smallest case with the tallest arch",
    ),
    corner_case(
        "tall_tapered_six_stack",
        {
            "body_form": "tapered_case",
            "drawer_layout": "full_width_stack",
            "drawer_front": "framed_cane",
            "support_base": "toe_kick_plinth",
            "drawer_count": 6,
            "carcass_width_m": 0.70,
            "carcass_depth_m": 0.52,
            "carcass_height_m": 1.30,
            "case_taper_ratio": 0.72,
            "graduation_ratio": 1.85,
            "cane_frame_w_m": 0.062,
            "toe_kick_h_m": 0.050,
        },
        reason="strongest taper with the most graduated stack and the widest cane frame",
    ),
    corner_case(
        "wide_bow_five_mixed",
        {
            "body_form": "bow_front",
            "drawer_layout": "pair_over_full_width",
            "drawer_front": "flat_panel",
            "support_base": "splayed_tapered_legs",
            "drawer_count": 5,
            "carcass_width_m": 1.30,
            "carcass_depth_m": 0.36,
            "carcass_height_m": 0.74,
            "bow_depth_m": 0.048,
            "base_level_ratio": 2.10,
            "front_t_m": 0.032,
            "splayed_leg_h_m": 0.320,
        },
        reason="deepest bow on the shallowest case with the most graduated base level",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_drawer_cabinet_with_sliding_drawers",
    "build_seeded_drawer_cabinet_with_sliding_drawers",
    "config_from_seed",
    "resolve_config",
    "run_drawer_cabinet_with_sliding_drawers_tests",
]
