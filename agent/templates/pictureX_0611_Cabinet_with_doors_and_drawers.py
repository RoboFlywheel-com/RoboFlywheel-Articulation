# SPDX-License-Identifier: Apache-2.0

"""pictureX/0611 Cabinet_with_doors_and_drawers — Design-backed single-file template.

A sideboard/cabinet that always carries BOTH mechanisms: at least one openable door
(vertical butt hinge or a sliding track leaf) and a bank of pull-out hollow drawers, on one
load-bearing carcass (straight, bow-front or tapered case).

The layout candidate splits the cavity into a door zone and a drawer zone — stacked either
way, side by side, or with doors flanking a central bank — and every leaf and drawer front is
struck from the host's own front curve, so a bow-front case gets arced fronts. Leaf size,
hinge line, track run, tray width, box depth and travel all derive from the zone split and
from N, so every declared slot combination builds and no overlap allowance is emitted.

Coordinate convention: X = width, Y = depth with the FRONT at -Y, Z = height. Doors swing
about +Z or slide along X; drawers pull out along -Y.
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
    AxisInterface,
    Box,
    Cylinder,
    ExtrudeGeometry,
    LoftGeometry,
    MotionLimits,
    Origin,
    PlaneInterface,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mate_planes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

BodyForm = Literal["rect_box", "bow_front", "tapered_box"]
StorageLayout = Literal[
    "doors_over_drawers", "drawers_over_doors", "door_beside_drawers", "doors_flanking_drawers"
]
DoorKind = Literal["slab_panel", "recessed_panel", "glazed_lattice"]
DoorMechanism = Literal["hinged_swing", "sliding_track"]
DrawerFront = Literal["plain_slab", "grained_slab"]
SupportBase = Literal["tapered_legs", "stone_plinth", "apron_feet_plinth", "metal_legs"]

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("body_form", ("rect_box", "bow_front", "tapered_box")),
        component_slot(
            "storage_layout",
            (
                "doors_over_drawers",
                "drawers_over_doors",
                "door_beside_drawers",
                "doors_flanking_drawers",
            ),
        ),
        component_slot("door_kind", ("slab_panel", "recessed_panel", "glazed_lattice")),
        component_slot("door_mechanism", ("hinged_swing", "sliding_track")),
        component_slot("drawer_front", ("plain_slab", "grained_slab")),
        component_slot(
            "support_base", ("tapered_legs", "stone_plinth", "apron_feet_plinth", "metal_legs")
        ),
        multiplicity_slot("drawer_count", (1, 2, 3, 4), item_slot="drawer_front"),
    )
)

# manufacturing constants (metres)
_TOP_T = 0.030
_BASE_T = 0.026
_WALL_T = 0.020
_RAIL_W = 0.014
_RAIL_EMBED = 0.016
_RAIL_H = 0.012
_RUNNER_W = 0.009
_RUNNER_ENGAGE = 0.003
_TRAY_WALL_T = 0.011
_TRAY_FLOOR_T = 0.011
_TRAY_FRONT_REACH = 0.017
_SIDE_CLEAR = 0.003
_LEVEL_REVEAL = 0.008
_ZONE_REVEAL = 0.034
_MID_RAIL_T = 0.034
_DIVIDER_T = 0.022
_FRONT_GAP = 0.0015
_BARREL_R = 0.008
_LEAF_SETBACK = 0.012
_LEAF_GAP = 0.002
_MIN_FRONT_H = 0.070
_MIN_LEAF_W = 0.080
_MIN_TRAY_W = 0.100
_PLAN_SEGMENTS = 24
_ZONE_MIN = 0.140

RGBA = tuple[float, float, float, float]
_PALETTES: tuple[dict[str, RGBA], ...] = (
    {  # walnut secretary, origin 001
        "wood": (0.34, 0.20, 0.12, 1.0), "dark": (0.14, 0.08, 0.05, 1.0),
        "panel": (0.44, 0.27, 0.16, 1.0), "metal": (0.74, 0.62, 0.34, 1.0),
        "glass": (0.56, 0.66, 0.70, 0.34), "accent": (0.66, 0.48, 0.26, 1.0),
    },
    {  # green jeweller cabinet, origin 002
        "wood": (0.16, 0.30, 0.24, 1.0), "dark": (0.08, 0.16, 0.13, 1.0),
        "panel": (0.22, 0.38, 0.31, 1.0), "metal": (0.80, 0.68, 0.36, 1.0),
        "glass": (0.60, 0.72, 0.74, 0.32), "accent": (0.86, 0.80, 0.60, 1.0),
    },
    {  # slate painted, origin 003
        "wood": (0.34, 0.36, 0.38, 1.0), "dark": (0.16, 0.17, 0.18, 1.0),
        "panel": (0.42, 0.44, 0.46, 1.0), "metal": (0.72, 0.73, 0.75, 1.0),
        "glass": (0.58, 0.68, 0.74, 0.33), "accent": (0.84, 0.82, 0.78, 1.0),
    },
    {  # gray oak sideboard, origin 004
        "wood": (0.62, 0.58, 0.52, 1.0), "dark": (0.32, 0.29, 0.25, 1.0),
        "panel": (0.70, 0.66, 0.59, 1.0), "metal": (0.60, 0.61, 0.62, 1.0),
        "glass": (0.62, 0.70, 0.74, 0.32), "accent": (0.48, 0.44, 0.38, 1.0),
    },
)

_SUPPORT_FIELD: dict[str, str] = {
    "tapered_legs": "tapered_leg_h_m",
    "stone_plinth": "stone_plinth_h_m",
    "apron_feet_plinth": "apron_plinth_h_m",
    "metal_legs": "metal_leg_h_m",
}
_SUPPORT_BOUNDS: dict[str, tuple[float, float]] = {
    "tapered_legs": (0.120, 0.320),
    "stone_plinth": (0.050, 0.170),
    "apron_feet_plinth": (0.080, 0.210),
    "metal_legs": (0.100, 0.300),
}
_BODY_BOUNDS: dict[str, dict[str, tuple[float, float]]] = {
    "rect_box": {"w": (0.72, 1.60), "d": (0.34, 0.52), "h": (0.80, 1.75)},
    "bow_front": {"w": (0.72, 1.44), "d": (0.34, 0.52), "h": (0.80, 1.60)},
    "tapered_box": {"w": (0.72, 1.44), "d": (0.34, 0.52), "h": (0.80, 1.68)},
}


@dataclass(frozen=True)
class Config:
    body_form: BodyForm = "rect_box"
    storage_layout: StorageLayout = "doors_over_drawers"
    door_kind: DoorKind = "slab_panel"
    door_mechanism: DoorMechanism = "hinged_swing"
    drawer_front: DrawerFront = "plain_slab"
    support_base: SupportBase = "tapered_legs"
    drawer_count: int = 2
    carcass_width_m: float | None = None
    carcass_depth_m: float | None = None
    carcass_height_m: float | None = None
    rect_wall_t_m: float | None = None
    bow_depth_m: float | None = None
    case_taper_ratio: float | None = None
    door_zone_ratio: float | None = None
    drawer_zone_ratio: float | None = None
    door_column_ratio: float | None = None
    flank_column_ratio: float | None = None
    slab_leaf_t_m: float | None = None
    recess_depth_m: float | None = None
    lattice_bar_w_m: float | None = None
    door_swing_rad: float | None = None
    slide_travel_m: float | None = None
    front_t_m: float | None = None
    grain_relief_m: float | None = None
    drawer_travel_ratio: float | None = None
    tapered_leg_h_m: float | None = None
    stone_plinth_h_m: float | None = None
    apron_plinth_h_m: float | None = None
    metal_leg_h_m: float | None = None
    palette: int = 0
    name: str = "pictureX_0611_Cabinet_with_doors_and_drawers"


@dataclass(frozen=True)
class ResolvedConfig:
    body_form: BodyForm
    storage_layout: StorageLayout
    door_kind: DoorKind
    door_mechanism: DoorMechanism
    drawer_front: DrawerFront
    support_base: SupportBase
    drawer_count: int
    door_leaf_count: int
    palette: int
    name: str
    carcass_width_m: float
    carcass_depth_m: float
    carcass_height_m: float
    rect_wall_t_m: float
    bow_depth_m: float
    case_taper_ratio: float
    door_zone_ratio: float
    drawer_zone_ratio: float
    door_column_ratio: float
    flank_column_ratio: float
    slab_leaf_t_m: float
    recess_depth_m: float
    lattice_bar_w_m: float
    door_swing_rad: float
    slide_travel_m: float
    front_t_m: float
    grain_relief_m: float
    drawer_travel_ratio: float
    tapered_leg_h_m: float
    stone_plinth_h_m: float
    apron_plinth_h_m: float
    metal_leg_h_m: float
    wall_t_m: float
    leaf_t_m: float
    body_bottom_z_m: float
    body_top_z_m: float
    cavity_lo_z_m: float
    cavity_hi_z_m: float


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value: float | None, default: float) -> float:
    return default if value is None else float(value)


def _leaf_count_for(layout: str) -> int:
    return 1 if layout == "door_beside_drawers" else 2


def config_from_seed(seed: int) -> Config:
    rng = random.Random(seed)
    body_form: BodyForm = rng.choice(("rect_box", "bow_front", "tapered_box"))
    bounds = _BODY_BOUNDS[body_form]
    return Config(
        body_form=body_form,
        storage_layout=rng.choice(
            (
                "doors_over_drawers",
                "drawers_over_doors",
                "door_beside_drawers",
                "doors_flanking_drawers",
            )
        ),
        door_kind=rng.choice(("slab_panel", "recessed_panel", "glazed_lattice")),
        door_mechanism=rng.choice(("hinged_swing", "sliding_track")),
        drawer_front=rng.choice(("plain_slab", "grained_slab")),
        support_base=rng.choice(tuple(_SUPPORT_FIELD)),
        drawer_count=rng.choice((1, 2, 3, 4)),
        carcass_width_m=round(rng.uniform(*bounds["w"]), 3),
        carcass_depth_m=round(rng.uniform(*bounds["d"]), 3),
        carcass_height_m=round(rng.uniform(*bounds["h"]), 3),
        rect_wall_t_m=round(rng.uniform(0.016, 0.030), 4),
        bow_depth_m=round(rng.uniform(0.014, 0.052), 4),
        case_taper_ratio=round(rng.uniform(0.72, 0.96), 3),
        door_zone_ratio=round(rng.uniform(0.36, 0.78), 3),
        drawer_zone_ratio=round(rng.uniform(0.28, 0.70), 3),
        door_column_ratio=round(rng.uniform(0.34, 0.72), 3),
        flank_column_ratio=round(rng.uniform(0.20, 0.42), 3),
        slab_leaf_t_m=round(rng.uniform(0.016, 0.032), 4),
        recess_depth_m=round(rng.uniform(0.006, 0.018), 4),
        lattice_bar_w_m=round(rng.uniform(0.008, 0.022), 4),
        door_swing_rad=round(rng.uniform(1.40, 1.92), 3),
        slide_travel_m=round(rng.uniform(0.20, 0.46), 3),
        front_t_m=round(rng.uniform(0.016, 0.030), 4),
        grain_relief_m=round(rng.uniform(0.003, 0.011), 4),
        drawer_travel_ratio=round(rng.uniform(0.36, 0.62), 3),
        tapered_leg_h_m=round(rng.uniform(0.120, 0.320), 3),
        stone_plinth_h_m=round(rng.uniform(0.050, 0.170), 3),
        apron_plinth_h_m=round(rng.uniform(0.080, 0.210), 3),
        metal_leg_h_m=round(rng.uniform(0.100, 0.300), 3),
        palette=rng.randrange(len(_PALETTES)),
        name=f"pictureX_0611_Cabinet_with_doors_and_drawers_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    body_form = config.body_form
    layout = config.storage_layout
    support = config.support_base
    bounds = _BODY_BOUNDS[body_form]
    width = _clamp(_pick(config.carcass_width_m, sum(bounds["w"]) / 2), *bounds["w"])
    depth = _clamp(_pick(config.carcass_depth_m, sum(bounds["d"]) / 2), *bounds["d"])
    height = _clamp(_pick(config.carcass_height_m, sum(bounds["h"]) / 2), *bounds["h"])
    rect_wall = _clamp(_pick(config.rect_wall_t_m, 0.020), 0.016, 0.030)
    wall_t = rect_wall if body_form == "rect_box" else _WALL_T
    support_bounds = _SUPPORT_BOUNDS[support]
    body_bottom = _clamp(
        _pick(getattr(config, _SUPPORT_FIELD[support]), sum(support_bounds) / 2), *support_bounds
    )
    body_top = body_bottom + height
    leaf_t = _clamp(_pick(config.slab_leaf_t_m, 0.022), 0.016, 0.032)
    if config.door_kind != "slab_panel":
        leaf_t = 0.022
    return ResolvedConfig(
        body_form=body_form,
        storage_layout=layout,
        door_kind=config.door_kind,
        door_mechanism=config.door_mechanism,
        drawer_front=config.drawer_front,
        support_base=support,
        drawer_count=int(_clamp(int(config.drawer_count), 1, 4)),
        door_leaf_count=_leaf_count_for(layout),
        palette=int(config.palette) % len(_PALETTES),
        name=config.name,
        carcass_width_m=width,
        carcass_depth_m=depth,
        carcass_height_m=height,
        rect_wall_t_m=rect_wall,
        bow_depth_m=_clamp(_pick(config.bow_depth_m, 0.030), 0.014, 0.052),
        case_taper_ratio=_clamp(_pick(config.case_taper_ratio, 0.86), 0.72, 0.96),
        door_zone_ratio=_clamp(_pick(config.door_zone_ratio, 0.56), 0.36, 0.78),
        drawer_zone_ratio=_clamp(_pick(config.drawer_zone_ratio, 0.46), 0.28, 0.70),
        door_column_ratio=_clamp(_pick(config.door_column_ratio, 0.50), 0.34, 0.72),
        flank_column_ratio=_clamp(_pick(config.flank_column_ratio, 0.30), 0.20, 0.42),
        slab_leaf_t_m=_clamp(_pick(config.slab_leaf_t_m, 0.022), 0.016, 0.032),
        recess_depth_m=_clamp(_pick(config.recess_depth_m, 0.011), 0.006, 0.018),
        lattice_bar_w_m=_clamp(_pick(config.lattice_bar_w_m, 0.014), 0.008, 0.022),
        door_swing_rad=_clamp(_pick(config.door_swing_rad, 1.68), 1.40, 1.92),
        slide_travel_m=_clamp(_pick(config.slide_travel_m, 0.32), 0.20, 0.46),
        front_t_m=_clamp(_pick(config.front_t_m, 0.022), 0.016, 0.030),
        grain_relief_m=_clamp(_pick(config.grain_relief_m, 0.006), 0.003, 0.011),
        drawer_travel_ratio=_clamp(_pick(config.drawer_travel_ratio, 0.48), 0.36, 0.62),
        tapered_leg_h_m=_clamp(_pick(config.tapered_leg_h_m, 0.220), 0.120, 0.320),
        stone_plinth_h_m=_clamp(_pick(config.stone_plinth_h_m, 0.110), 0.050, 0.170),
        apron_plinth_h_m=_clamp(_pick(config.apron_plinth_h_m, 0.140), 0.080, 0.210),
        metal_leg_h_m=_clamp(_pick(config.metal_leg_h_m, 0.200), 0.100, 0.300),
        wall_t_m=wall_t,
        leaf_t_m=leaf_t,
        body_bottom_z_m=body_bottom,
        body_top_z_m=body_top,
        cavity_lo_z_m=body_bottom + _BASE_T,
        cavity_hi_z_m=body_top - _TOP_T,
    )


# ---------------------------------------------------------------------------
# plan profile
# ---------------------------------------------------------------------------
def _taper_scale(r: ResolvedConfig, z: float) -> float:
    if r.body_form != "tapered_box":
        return 1.0
    span = max(r.carcass_height_m, 1e-6)
    t = _clamp((z - r.body_bottom_z_m) / span, 0.0, 1.0)
    return 1.0 - t * (1.0 - r.case_taper_ratio)


def _front_y(r: ResolvedConfig, x: float, z: float) -> float:
    half_w = max(r.carcass_width_m / 2.0 * _taper_scale(r, z), 1e-4)
    u = _clamp(x / half_w, -1.0, 1.0)
    base = -r.carcass_depth_m / 2.0
    if r.body_form == "bow_front":
        return base - r.bow_depth_m * (1.0 - u * u)
    return base


def _side_x(r: ResolvedConfig, v: float, z: float) -> float:
    del v
    return r.carcass_width_m / 2.0 * _taper_scale(r, z)


def _back_y(r: ResolvedConfig) -> float:
    return r.carcass_depth_m / 2.0


def _cavity_window(r: ResolvedConfig, z: float) -> tuple[float, float, float]:
    """(half width, tray front y, tray rear y) available at height z."""

    half_w = max(_side_x(r, 0.0, z) - r.wall_t_m, 0.060)
    xs = [-half_w + 2.0 * half_w * i / 8.0 for i in range(9)]
    y_front = max(_front_y(r, x, z) for x in xs) + 0.012
    y_back = _back_y(r) - r.wall_t_m
    if y_back - y_front < 0.150:
        y_back = y_front + 0.150
    return half_w, y_front, y_back


def _front_open_y(r: ResolvedConfig) -> float:
    return _cavity_window(r, r.cavity_hi_z_m)[1] - 0.014


def _plan_outline(r: ResolvedConfig, z: float, y_open: float | None = None):
    back_y = _back_y(r)
    v_start = -1.0 if y_open is None else _clamp(y_open / back_y, -1.0, 0.85)
    points = []
    steps = _PLAN_SEGMENTS
    for i in range(steps + 1):
        v = v_start + (1.0 - v_start) * i / steps
        points.append((-_side_x(r, v, z), back_y * v))
    for i in range(steps + 1):
        v = 1.0 - (1.0 - v_start) * i / steps
        points.append((_side_x(r, v, z), back_y * v))
    return points


def _shell_profile(r: ResolvedConfig, z: float, y_open: float):
    outer = _plan_outline(r, z, y_open)
    inner = []
    for x, y in reversed(outer):
        length = math.hypot(x, y)
        shrink = max(1.0 - r.wall_t_m / length, 0.05) if length > 1e-6 else 1.0
        inner.append((x * shrink, y * shrink))
    return outer + inner


def _slab_profile(r: ResolvedConfig, z: float, grow: float):
    grown = []
    for x, y in _plan_outline(r, z):
        length = math.hypot(x, y)
        scale = 1.0 + grow / length if length > 1e-6 else 1.0
        grown.append((x * scale, y * scale))
    front = []
    steps = _PLAN_SEGMENTS
    half_w = _side_x(r, 0.0, z)
    for i in range(steps + 1):
        x = half_w - 2.0 * half_w * i / steps
        front.append((x, _front_y(r, x, z) - grow))
    return grown + front


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _bx(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Box(size=(float(size[0]), float(size[1]), float(size[2]))),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material,
        name=name, material_class_id="wood.polished_varnished",
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
    return {k: model.material(f"sideboard_{palette}_{k}", rgba=v) for k, v in table.items()}


def _axis_mate(*, provider_name, point, consumer_name, consumer_radius):
    provider = AxisInterface(
        name=provider_name,
        point=(float(point[0]), float(point[1]), float(point[2])),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=_BARREL_R,
    )
    consumer = AxisInterface(
        name=consumer_name,
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=consumer_radius,
    )
    return mate_axes(provider, consumer, require_fit=True)


def _plane_mate(*, provider_name, provider_point, provider_extent, consumer_name, consumer_extent):
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
# zones
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Zone:
    x0: float
    x1: float
    z0: float
    z1: float


def _zones(r: ResolvedConfig) -> tuple[tuple[_Zone, ...], _Zone]:
    """(door zones, drawer zone) derived from the layout candidate."""

    half_w, _y0, _y1 = _cavity_window(r, r.cavity_hi_z_m)
    lo, hi = r.cavity_lo_z_m, r.cavity_hi_z_m
    total_h = hi - lo
    if r.storage_layout == "doors_over_drawers":
        door_h = _clamp(total_h * r.door_zone_ratio, _ZONE_MIN, total_h - _ZONE_MIN)
        split = hi - door_h
        doors = (_Zone(-half_w, half_w, split + _ZONE_REVEAL / 2, hi),)
        drawers = _Zone(-half_w, half_w, lo, split - _ZONE_REVEAL / 2)
        return doors, drawers
    if r.storage_layout == "drawers_over_doors":
        drawer_h = _clamp(total_h * r.drawer_zone_ratio, _ZONE_MIN, total_h - _ZONE_MIN)
        split = hi - drawer_h
        doors = (_Zone(-half_w, half_w, lo, split - _ZONE_REVEAL / 2),)
        drawers = _Zone(-half_w, half_w, split + _ZONE_REVEAL / 2, hi)
        return doors, drawers
    if r.storage_layout == "door_beside_drawers":
        door_w = _clamp(2 * half_w * r.door_column_ratio, _ZONE_MIN, 2 * half_w - _ZONE_MIN)
        split_x = -half_w + door_w
        doors = (_Zone(-half_w, split_x - _DIVIDER_T / 2, lo, hi),)
        drawers = _Zone(split_x + _DIVIDER_T / 2, half_w, lo, hi)
        return doors, drawers
    flank_w = _clamp(
        2 * half_w * r.flank_column_ratio, _ZONE_MIN * 0.7, max(half_w - _ZONE_MIN / 2, 0.08)
    )
    doors = (
        _Zone(-half_w, -half_w + flank_w - _DIVIDER_T / 2, lo, hi),
        _Zone(half_w - flank_w + _DIVIDER_T / 2, half_w, lo, hi),
    )
    drawers = _Zone(
        -half_w + flank_w + _DIVIDER_T / 2, half_w - flank_w - _DIVIDER_T / 2, lo, hi
    )
    return doors, drawers


@dataclass(frozen=True)
class _Cell:
    index: int
    x0: float
    x1: float
    z0: float
    z1: float
    y_front: float
    y_back: float


def _drawer_cells(r: ResolvedConfig) -> list[_Cell]:
    _doors, zone = _zones(r)
    n = r.drawer_count
    zone_h = max(zone.z1 - zone.z0, 0.060)
    gap = _LEVEL_REVEAL
    band = (zone_h - (n - 1) * gap) / n
    if band < _MIN_FRONT_H * 0.45:
        # a squeezed zone closes its reveals before it overflows into the rail
        gap = 0.002
        band = max((zone_h - (n - 1) * gap) / n, 0.020)
    cells: list[_Cell] = []
    z = zone.z0
    for index in range(n):
        z0, z1 = z, z + band
        _hw, y_front, y_back = _cavity_window(r, z1)
        cells.append(_Cell(index, zone.x0, zone.x1, z0, z1, y_front, y_back))
        z = z1 + gap
    return cells


# ---------------------------------------------------------------------------
# body_form candidates
# ---------------------------------------------------------------------------
def _build_case_shell(carcass, r: ResolvedConfig, mats, tag: str) -> None:
    z0, z1 = r.body_bottom_z_m, r.body_top_z_m
    y_open = _front_open_y(r)
    profiles = [
        [(x, y, z) for x, y in _shell_profile(r, z, y_open)]
        for z in (z0, (z0 + z1) / 2.0, z1)
    ]
    carcass.visual(
        mesh_from_geometry(LoftGeometry(profiles), f"{tag}__shell_mesh"),
        material=mats["wood"],
        name=f"{tag}__case_shell", material_class_id="wood.polished_varnished",
    )
    carcass.visual(
        mesh_from_geometry(
            ExtrudeGeometry(_slab_profile(r, z1, 0.014), _TOP_T, center=False), f"{tag}__top_mesh"
        ),
        origin=Origin(xyz=(0.0, 0.0, z1 - _TOP_T)),
        material=mats["wood"],
        name=f"{tag}__top_slab", material_class_id="wood.polished_varnished",
    )
    carcass.visual(
        mesh_from_geometry(
            ExtrudeGeometry(_slab_profile(r, z0, 0.0), _BASE_T, center=False), f"{tag}__base_mesh"
        ),
        origin=Origin(xyz=(0.0, 0.0, z0)),
        material=mats["dark"],
        name=f"{tag}__base_panel", material_class_id="wood.walnut_dark",
    )


def _body_form_rect_box_build(carcass, r, mats) -> None:
    _build_case_shell(carcass, r, mats, "body_form__rect_box")


def _body_form_bow_front_build(carcass, r, mats) -> None:
    _build_case_shell(carcass, r, mats, "body_form__bow_front")


def _body_form_tapered_box_build(carcass, r, mats) -> None:
    _build_case_shell(carcass, r, mats, "body_form__tapered_box")


_BODY_BUILDERS = {
    "rect_box": _body_form_rect_box_build,
    "bow_front": _body_form_bow_front_build,
    "tapered_box": _body_form_tapered_box_build,
}


# ---------------------------------------------------------------------------
# support_base candidates
# ---------------------------------------------------------------------------
def _corners(r: ResolvedConfig, inset: float):
    lx = max(r.carcass_width_m / 2 - inset, 0.05)
    ly = max(r.carcass_depth_m / 2 - inset, 0.05)
    return [(-lx, -ly), (lx, -ly), (-lx, ly), (lx, ly)]


def _support_base_tapered_legs_build(carcass, r, mats) -> None:
    tag = "support_base__tapered_legs"
    h = r.body_bottom_z_m
    for i, (x, y) in enumerate(_corners(r, 0.062)):
        for j in range(4):
            t0, t1 = j / 4.0, (j + 1) / 4.0
            z0, z1 = h * (1.0 - t1), h * (1.0 - t0)
            side = 0.018 + 0.026 * (1.0 - (t0 + t1) / 2.0)
            _bx(carcass, (side, side, z1 - z0 + 0.006), (x, y, (z0 + z1) / 2.0), mats["wood"],
                f"{tag}__tapered_leg_{i}_{j}")


def _support_base_stone_plinth_build(carcass, r, mats) -> None:
    tag = "support_base__stone_plinth"
    h = r.body_bottom_z_m
    _bx(carcass, (r.carcass_width_m * 0.99, r.carcass_depth_m * 0.99, h + 0.008),
        (0.0, 0.0, (h + 0.008) / 2.0), mats["dark"], f"{tag}__plinth_block")
    _bx(carcass, (r.carcass_width_m * 1.02, r.carcass_depth_m * 1.02, 0.016),
        (0.0, 0.0, h - 0.008), mats["panel"], f"{tag}__plinth_cap")


def _support_base_apron_feet_plinth_build(carcass, r, mats) -> None:
    tag = "support_base__apron_feet_plinth"
    h = r.body_bottom_z_m
    for i, (x, y) in enumerate(_corners(r, 0.048)):
        _bx(carcass, (0.070, 0.070, h + 0.006), (x, y, (h + 0.006) / 2.0), mats["dark"], f"{tag}__foot_{i}")
    half_w = r.carcass_width_m / 2.0 * 0.90
    steps = 7
    for i in range(steps):
        x0 = -half_w + 2 * half_w * i / steps
        x1 = -half_w + 2 * half_w * (i + 1) / steps
        cx = (x0 + x1) / 2.0
        cut = h * (0.34 + 0.30 * abs(math.sin(math.pi * (i + 0.5) / steps)))
        _bx(carcass, (x1 - x0 + 0.004, 0.022, cut), (cx, _front_y(r, cx, h) + 0.014, h - cut / 2 + 0.004),
            mats["wood"], f"{tag}__apron_{i}")


def _support_base_metal_legs_build(carcass, r, mats) -> None:
    tag = "support_base__metal_legs"
    h = r.body_bottom_z_m
    for i, (x, y) in enumerate(_corners(r, 0.070)):
        _cy(carcass, 0.013, h + 0.010, (x, y, (h + 0.010) / 2.0), mats["metal"], f"{tag}__leg_{i}")
        _cy(carcass, 0.020, 0.012, (x, y, 0.006), mats["dark"], f"{tag}__floor_pad_{i}")


_SUPPORT_BUILDERS = {
    "tapered_legs": _support_base_tapered_legs_build,
    "stone_plinth": _support_base_stone_plinth_build,
    "apron_feet_plinth": _support_base_apron_feet_plinth_build,
    "metal_legs": _support_base_metal_legs_build,
}


# ---------------------------------------------------------------------------
# storage_layout candidates — the zone split structure
# ---------------------------------------------------------------------------
def _mid_rail(carcass, r, mats, tag: str, z: float, x0: float, x1: float) -> None:
    del x0, x1
    _hw, y_front, y_back = _cavity_window(r, z)
    span = 2.0 * (_side_x(r, 0.0, z) - r.wall_t_m) + 0.030
    y_lo = y_front + 0.004
    _bx(
        carcass,
        (span, max(y_back - y_lo, 0.10), _MID_RAIL_T),
        (0.0, (y_lo + y_back) / 2.0, z),
        mats["wood"],
        f"{tag}__mid_rail",
    )


def _vertical_divider(carcass, r, mats, tag: str, x: float, index: int) -> None:
    lo, hi = r.cavity_lo_z_m, r.cavity_hi_z_m
    _hw, y_front, y_back = _cavity_window(r, hi)
    _bx(
        carcass,
        (_DIVIDER_T, max(y_back - y_front, 0.10) + 0.014, hi - lo + 0.014),
        (x, (y_front + y_back) / 2.0 - 0.007, (lo + hi) / 2.0),
        mats["wood"],
        f"{tag}__divider_{index}",
    )


def _drawer_rails(carcass, r, mats, tag: str) -> None:
    for cell in _drawer_cells(r):
        y0 = cell.y_front + 0.002
        y1 = cell.y_back + 0.004
        depth = max(y1 - y0, 0.10)
        cy = (y0 + y1) / 2.0
        rail_z = cell.z0 + _RAIL_H / 2.0 - 0.002
        for side, x in ((0, cell.x0), (1, cell.x1)):
            direction = 1.0 if side == 0 else -1.0
            wall = _side_x(r, 0.0, cell.z1) - r.wall_t_m
            outer = max(wall - abs(x), 0.0) + _RAIL_EMBED
            _bx(
                carcass,
                (_RAIL_W + outer, depth, _RAIL_H),
                (x + direction * (_RAIL_W - outer) / 2.0, cy, rail_z),
                mats["dark"],
                f"{tag}__runner_rail_{cell.index}_{side}",
            )
        if cell.index > 0:
            x_lo = cell.x0 - _edge_reach(r, cell.z0, cell.x0)
            x_hi = cell.x1 + _edge_reach(r, cell.z0, cell.x1)
            _bx(
                carcass,
                (x_hi - x_lo, depth, 0.010),
                ((x_lo + x_hi) / 2.0, cy, cell.z0 - _LEVEL_REVEAL / 2.0),
                mats["dark"],
                f"{tag}__level_rail_{cell.index}",
            )


def _storage_layout_doors_over_drawers_build(carcass, r, mats) -> None:
    tag = "storage_layout__doors_over_drawers"
    doors, drawers = _zones(r)
    _mid_rail(carcass, r, mats, tag, (drawers.z1 + doors[0].z0) / 2.0, drawers.x0, drawers.x1)
    _drawer_rails(carcass, r, mats, tag)


def _storage_layout_drawers_over_doors_build(carcass, r, mats) -> None:
    tag = "storage_layout__drawers_over_doors"
    doors, drawers = _zones(r)
    _mid_rail(carcass, r, mats, tag, (doors[0].z1 + drawers.z0) / 2.0, drawers.x0, drawers.x1)
    _drawer_rails(carcass, r, mats, tag)


def _storage_layout_door_beside_drawers_build(carcass, r, mats) -> None:
    tag = "storage_layout__door_beside_drawers"
    doors, drawers = _zones(r)
    _vertical_divider(carcass, r, mats, tag, (doors[0].x1 + drawers.x0) / 2.0, 0)
    _drawer_rails(carcass, r, mats, tag)


def _storage_layout_doors_flanking_drawers_build(carcass, r, mats) -> None:
    tag = "storage_layout__doors_flanking_drawers"
    doors, drawers = _zones(r)
    _vertical_divider(carcass, r, mats, tag, (doors[0].x1 + drawers.x0) / 2.0, 0)
    _vertical_divider(carcass, r, mats, tag, (drawers.x1 + doors[1].x0) / 2.0, 1)
    _drawer_rails(carcass, r, mats, tag)


_LAYOUT_BUILDERS = {
    "doors_over_drawers": _storage_layout_doors_over_drawers_build,
    "drawers_over_doors": _storage_layout_drawers_over_doors_build,
    "door_beside_drawers": _storage_layout_door_beside_drawers_build,
    "doors_flanking_drawers": _storage_layout_doors_flanking_drawers_build,
}


# ---------------------------------------------------------------------------
# door_kind candidates — leaf-local frame, hinge/track origin at the local origin
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _LeafFrame:
    x_ref: float
    y_ref: float
    z_ref: float
    sign: float
    y_shift: float = 0.0


def _leaf_profile(r: ResolvedConfig, x0: float, x1: float, z: float, f: _LeafFrame):
    steps = 8
    outer, inner = [], []
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        y = _front_y(r, x, z) - _LEAF_GAP - f.y_shift
        outer.append((x - f.x_ref, y - r.leaf_t_m - f.y_ref))
        inner.append((x - f.x_ref, y - f.y_ref))
    return outer + list(reversed(inner))


def _leaf_face_y(r: ResolvedConfig, x: float, z: float, f: _LeafFrame) -> float:
    return _front_y(r, x, z) - _LEAF_GAP - f.y_shift - r.leaf_t_m - f.y_ref


def _leaf_slab(leaf, r, mats, x0, x1, cz, height, f, tag, material_key) -> None:
    leaf.visual(
        mesh_from_geometry(
            ExtrudeGeometry(_leaf_profile(r, x0, x1, cz, f), height, center=True),
            f"{tag}__leaf_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, cz - f.z_ref)),
        material=mats[material_key],
        name=f"{tag}__leaf_panel", material_class_id=("wood.polished_varnished" if r.door_kind in {"recessed_panel", "glazed_lattice"} else "wood.veneer_panel"),
    )


def _leaf_pull(leaf, r, mats, x_pull, cz, height, f, tag) -> None:
    y = _leaf_face_y(r, x_pull, cz, f)
    zc = cz - f.z_ref
    if r.door_mechanism == "sliding_track":
        # bypass leaves pass each other, so the pull is recessed into the face
        depth = min(0.008, r.leaf_t_m * 0.4)
        _bx(
            leaf,
            (0.028, depth, min(0.150, height * 0.45)),
            (x_pull - f.x_ref, y + depth / 2, zc),
            mats["dark"],
            f"{tag}__flush_pull",
        )
        return
    _cy(leaf, 0.006, min(0.130, height * 0.34), (x_pull - f.x_ref, y - 0.010, zc),
        mats["metal"], f"{tag}__pull_grip")
    for i, dz in enumerate((0.040, -0.040)):
        _cy(leaf, 0.005, 0.022, (x_pull - f.x_ref, y - 0.002, zc + dz), mats["metal"],
            f"{tag}__pull_mount_{i}", rpy=(math.pi / 2, 0, 0))


def _door_kind_slab_panel_build(leaf, r, mats, x0, x1, cz, height, f, tag) -> None:
    _leaf_slab(leaf, r, mats, x0, x1, cz, height, f, tag, "panel")
    x_pull = x1 - 0.040 if f.sign > 0 else x0 + 0.040
    _leaf_pull(leaf, r, mats, x_pull, cz, height, f, tag)


def _door_kind_recessed_panel_build(leaf, r, mats, x0, x1, cz, height, f, tag) -> None:
    _leaf_slab(leaf, r, mats, x0, x1, cz, height, f, tag, "wood")
    width = x1 - x0
    zc = cz - f.z_ref
    depth = r.recess_depth_m
    field_w = max(width - 0.100, width * 0.34)
    field_h = max(height - 0.100, height * 0.34)
    cx = (x0 + x1) / 2.0
    for label, (dx, dz, sx, sz) in {
        "moulding_top": (0.0, field_h / 2, field_w, 0.016),
        "moulding_bottom": (0.0, -field_h / 2, field_w, 0.016),
        "moulding_left": (-field_w / 2, 0.0, 0.016, field_h),
        "moulding_right": (field_w / 2, 0.0, 0.016, field_h),
    }.items():
        x = cx + dx
        _bx(leaf, (sx, depth + 0.004, sz), (x - f.x_ref, _leaf_face_y(r, x, cz, f) + depth / 2 - 0.002, zc + dz),
            mats["dark"], f"{tag}__{label}")
    x_pull = x1 - 0.040 if f.sign > 0 else x0 + 0.040
    _leaf_pull(leaf, r, mats, x_pull, cz, height, f, tag)


def _door_kind_glazed_lattice_build(leaf, r, mats, x0, x1, cz, height, f, tag) -> None:
    _leaf_slab(leaf, r, mats, x0, x1, cz, height, f, tag, "wood")
    width = x1 - x0
    zc = cz - f.z_ref
    bar = r.lattice_bar_w_m
    cx = (x0 + x1) / 2.0
    field_w = max(width - 0.080, width * 0.34)
    field_h = max(height - 0.080, height * 0.34)
    _bx(leaf, (field_w, 0.006, field_h), (cx - f.x_ref, _leaf_face_y(r, cx, cz, f) + 0.004, zc),
        mats["glass"], f"{tag}__glass_panel")
    for j in range(3):
        x = cx + (j - 1) * field_w / 3.0
        _bx(leaf, (bar, 0.008, field_h), (x - f.x_ref, _leaf_face_y(r, x, cz, f) + 0.002, zc),
            mats["dark"], f"{tag}__lattice_v{j}")
    for j in range(3):
        _bx(leaf, (field_w, 0.008, bar), (cx - f.x_ref, _leaf_face_y(r, cx, cz, f) + 0.002, zc + (j - 1) * field_h / 3.0),
            mats["dark"], f"{tag}__lattice_h{j}")
    x_pull = x1 - 0.040 if f.sign > 0 else x0 + 0.040
    _leaf_pull(leaf, r, mats, x_pull, cz, height, f, tag)


_DOOR_BUILDERS = {
    "slab_panel": _door_kind_slab_panel_build,
    "recessed_panel": _door_kind_recessed_panel_build,
    "glazed_lattice": _door_kind_glazed_lattice_build,
}


# ---------------------------------------------------------------------------
# door_mechanism candidates
# ---------------------------------------------------------------------------
def _edge_reach(r: ResolvedConfig, z: float, x: float) -> float:
    """How far a zone-wide member must reach to bite into what bounds that edge."""

    outer_half = _cavity_window(r, r.cavity_hi_z_m)[0]
    wall = _side_x(r, 0.0, z) - r.wall_t_m
    if abs(abs(x) - outer_half) < 0.002:
        return max(wall - abs(x), 0.0) + 0.012
    return _DIVIDER_T / 2.0 + 0.004


def _hinge_mullion(carcass, r, mats, hinge_x, z0, z1, tag, index) -> None:
    _hw, y_front, _y_back = _cavity_window(r, z1)
    _bx(
        carcass,
        (0.044, 0.022, z1 - z0 + 0.012),
        (hinge_x, y_front - 0.004, (z0 + z1) / 2.0),
        mats["wood"],
        f"{tag}__hinge_mullion_{index}",
    )


def _hinge_hardware(carcass, leaf, r, mats, hinge_x, hinge_y, zc, leaf_h, sign, tag, index) -> None:
    stations = (-leaf_h * 0.34, leaf_h * 0.34)
    for si, station in enumerate(stations):
        _cy(carcass, _BARREL_R, 0.030, (hinge_x, hinge_y, zc + station), mats["metal"],
            f"{tag}__fixed_knuckle_{index}_{si}")
        _bx(carcass, (0.018, 0.026, 0.020), (hinge_x, hinge_y + 0.014, zc + station), mats["metal"],
            f"{tag}__knuckle_plate_{index}_{si}")
        for bi, offset in enumerate((-0.022, 0.022)):
            _cy(leaf, _BARREL_R * 0.86, 0.022, (0.0, 0.0, station + offset), mats["metal"],
                f"{tag}__barrel_{index}_{si}_{bi}")
            reach = _LEAF_SETBACK + 0.008
            _bx(leaf, (reach, 0.013, 0.016), (sign * reach / 2.0, 0.0, station + offset),
                mats["metal"], f"{tag}__hinge_strap_{index}_{si}_{bi}")


def _door_mechanism_hinged_swing_build(model, carcass, r, mats) -> list[object]:
    tag = "door_mechanism__hinged_swing"
    doors, _drawers = _zones(r)
    leaves: list[object] = []
    for index, zone in enumerate(doors):
        cz = (zone.z0 + zone.z1) / 2.0
        leaf_h = max(zone.z1 - zone.z0 - 0.014, 0.100)
        # single-zone layouts carry a mirrored pair; flank layouts carry one leaf each
        pairs = 2 if r.storage_layout in ("doors_over_drawers", "drawers_over_doors") else 1
        for k in range(pairs):
            cell_w = (zone.x1 - zone.x0) / pairs
            cell_x0 = zone.x0 + k * cell_w
            hinge_left = k == 0 if pairs == 2 else (index == 0)
            sign = 1.0 if hinge_left else -1.0
            hinge_x = cell_x0 + 0.020 if hinge_left else cell_x0 + cell_w - 0.020
            x0 = hinge_x + _LEAF_SETBACK if hinge_left else cell_x0 + 0.006
            x1 = cell_x0 + cell_w - 0.006 if hinge_left else hinge_x - _LEAF_SETBACK
            if x1 - x0 < _MIN_LEAF_W:
                x0, x1 = (hinge_x + _LEAF_SETBACK, hinge_x + _LEAF_SETBACK + _MIN_LEAF_W) if hinge_left else (hinge_x - _LEAF_SETBACK - _MIN_LEAF_W, hinge_x - _LEAF_SETBACK)
            hinge_y = _front_y(r, hinge_x, cz) - _LEAF_GAP - r.leaf_t_m / 2.0
            leaf_index = len(leaves)
            leaf = model.part(
                f"door_kind__{r.door_kind}__door_leaf_{leaf_index}",
                meta={"role": "door_leaf", "slot": "door_kind", "candidate": r.door_kind,
                      "index": leaf_index, "mechanism": "vertical butt hinge"},
            )
            frame = _LeafFrame(x_ref=hinge_x, y_ref=hinge_y, z_ref=cz, sign=sign)
            _DOOR_BUILDERS[r.door_kind](
                leaf, r, mats, x0, x1, cz, leaf_h, frame, f"door_kind__{r.door_kind}"
            )
            _hinge_mullion(carcass, r, mats, hinge_x, zone.z0, zone.z1, tag, leaf_index)
            _hinge_hardware(carcass, leaf, r, mats, hinge_x, hinge_y, cz, leaf_h, sign, tag, leaf_index)
            mate = _axis_mate(
                provider_name=f"storage_layout.zone_split.hinge_{leaf_index}",
                point=(hinge_x, hinge_y, cz),
                consumer_name=f"door_mechanism.leaf_mount_{leaf_index}",
                consumer_radius=_BARREL_R * 0.86,
            )
            joint = f"{tag}__leaf_joint_{leaf_index}"
            lower, upper = (-r.door_swing_rad, 0.0) if sign > 0 else (0.0, r.door_swing_rad)
            model.articulation(
                joint,
                ArticulationType.REVOLUTE,
                parent=carcass,
                child=leaf,
                origin=mate.origin,
                axis=mate.axis,
                motion_limits=MotionLimits(effort=12.0, velocity=1.4, lower=lower, upper=upper),
                meta={"positive_motion": "leaf swings outward toward -Y"},
            )
            register_interface_mate(model, joint, mate)
            leaves.append(leaf)
        if pairs == 2:
            break
    return leaves


def _door_mechanism_sliding_track_build(model, carcass, r, mats) -> list[object]:
    tag = "door_mechanism__sliding_track"
    doors, _drawers = _zones(r)
    leaves: list[object] = []
    # a stacked door zone carries a bypass pair; a flank or column zone one leaf
    per_zone = 2 if r.storage_layout in ("doors_over_drawers", "drawers_over_doors") else 1
    for zone in doors:
        cz = (zone.z0 + zone.z1) / 2.0
        zone_w = zone.x1 - zone.x0
        leaf_h = max(zone.z1 - zone.z0 - 0.034, 0.100)
        # a longer stroke is bought with a narrower leaf: the reveal a leaf can
        # open is exactly the part of the zone it does not cover
        leaf_w = max(
            zone_w * (0.56 if per_zone == 2 else 0.62) - r.slide_travel_m * 0.22, 0.060
        )
        for k in range(per_zone):
            index = len(leaves)
            rest_x0 = zone.x0 if k == 0 else zone.x1 - leaf_w
            slide_sign = 1.0 if k == 0 else -1.0
            room = (zone_w - leaf_w) if per_zone == 1 else (zone_w - leaf_w)
            travel = max(min(r.slide_travel_m, room - 0.010), 0.012)
            cx = rest_x0 + leaf_w / 2.0
            plane_y = _front_y(r, cx, cz) - _LEAF_GAP - k * (r.leaf_t_m + 0.034)
            leaf = model.part(
                f"door_kind__{r.door_kind}__door_leaf_{index}",
                meta={"role": "door_leaf", "slot": "door_kind", "candidate": r.door_kind,
                      "index": index, "mechanism": "sliding track"},
            )
            frame = _LeafFrame(
                x_ref=cx,
                y_ref=plane_y - r.leaf_t_m / 2.0,
                z_ref=cz,
                sign=1.0,
                y_shift=k * (r.leaf_t_m + 0.034),
            )
            _DOOR_BUILDERS[r.door_kind](
                leaf, r, mats, rest_x0 + 0.004, rest_x0 + leaf_w - 0.004, cz, leaf_h, frame,
                f"door_kind__{r.door_kind}",
            )
            # the rail always reaches back inside the case, even behind a bow
            track_back = _cavity_window(r, cz)[1] + 0.010
            track_front = plane_y - 0.004
            track_d = max(track_back - track_front, 0.014)
            track_cy = (track_back + track_front) / 2.0
            for side, z in ((0, zone.z1 - 0.006), (1, zone.z0 + 0.006)):
                # the rail runs its own zone and is let into whatever bounds it —
                # the side wall on an outer edge, the divider on an inner one
                x_lo = zone.x0 - _edge_reach(r, z, zone.x0)
                x_hi = zone.x1 + _edge_reach(r, z, zone.x1)
                _bx(
                    carcass,
                    (x_hi - x_lo, track_d, 0.016),
                    ((x_lo + x_hi) / 2.0, track_cy, z),
                    mats["dark"],
                    f"{tag}__track_{index}_{side}",
                )
            for j, dz in enumerate((leaf_h / 2 - 0.001, -leaf_h / 2 + 0.001)):
                _bx(leaf, (0.050, 0.016, 0.014), (0.0, r.leaf_t_m / 2 + 0.002, dz), mats["metal"],
                    f"{tag}__roller_{index}_{j}")
            mate = _plane_mate(
                provider_name=f"storage_layout.zone_split.track_{index}",
                provider_point=(cx, plane_y - r.leaf_t_m / 2.0, cz),
                provider_extent=(zone_w, zone.z1 - zone.z0),
                consumer_name=f"door_mechanism.leaf_mount_{index}",
                consumer_extent=(leaf_w, leaf_h),
            )
            joint = f"{tag}__leaf_joint_{index}"
            lower, upper = (0.0, travel) if slide_sign > 0 else (-travel, 0.0)
            model.articulation(
                joint,
                ArticulationType.PRISMATIC,
                parent=carcass,
                child=leaf,
                origin=mate.origin,
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=26.0, velocity=0.32, lower=lower, upper=upper),
                meta={"positive_motion": "leaf slides across its zone"},
            )
            register_interface_mate(model, joint, mate)
            leaves.append(leaf)
    return leaves


_MECHANISM_BUILDERS = {
    "hinged_swing": _door_mechanism_hinged_swing_build,
    "sliding_track": _door_mechanism_sliding_track_build,
}


# ---------------------------------------------------------------------------
# drawer_front candidates
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Frame:
    cx: float
    y_ref: float
    z_ref: float


def _front_panel_profile(r: ResolvedConfig, x0, x1, z, f: _Frame):
    steps = 8
    outer, inner = [], []
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        y = _front_y(r, x, z) - _FRONT_GAP
        outer.append((x - f.cx, y - r.front_t_m - f.y_ref))
        inner.append((x - f.cx, y - f.y_ref))
    return outer + list(reversed(inner))


def _front_face_y(r: ResolvedConfig, x, z, f: _Frame) -> float:
    return _front_y(r, x, z) - _FRONT_GAP - r.front_t_m - f.y_ref


def _drawer_slab(drawer, r, mats, x0, x1, cz, height, f, tag, key) -> None:
    drawer.visual(
        mesh_from_geometry(
            ExtrudeGeometry(_front_panel_profile(r, x0, x1, cz, f), height, center=True),
            f"{tag}__front_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, cz - f.z_ref)),
        material=mats[key],
        name=f"{tag}__drawer_front", material_class_id=("wood.polished_varnished" if r.drawer_front == "grained_slab" else "wood.veneer_panel"),
    )


def _drawer_pull(drawer, r, mats, f, cz, width, tag) -> None:
    y = _front_face_y(r, f.cx, cz, f)
    zc = cz - f.z_ref
    _cy(drawer, 0.006, min(0.140, width * 0.34), (0.0, y - 0.004, zc), mats["metal"],
        f"{tag}__pull_grip", rpy=(0.0, math.pi / 2, 0.0))
    for i, sign in enumerate((-1.0, 1.0)):
        _cy(drawer, 0.005, 0.020, (sign * min(0.060, width * 0.16), y - 0.001, zc), mats["metal"],
            f"{tag}__pull_mount_{i}", rpy=(math.pi / 2, 0, 0))


def _drawer_front_plain_slab_build(drawer, r, mats, x0, x1, cz, height, f, tag) -> None:
    _drawer_slab(drawer, r, mats, x0, x1, cz, height, f, tag, "panel")
    _drawer_pull(drawer, r, mats, f, cz, x1 - x0, tag)


def _drawer_front_grained_slab_build(drawer, r, mats, x0, x1, cz, height, f, tag) -> None:
    _drawer_slab(drawer, r, mats, x0, x1, cz, height, f, tag, "wood")
    width = x1 - x0
    zc = cz - f.z_ref
    relief = r.grain_relief_m
    for j in range(4):
        dz = (j - 1.5) * height / 5.0
        _bx(drawer, (width * 0.92, relief + 0.003, height / 12.0),
            (0.0, _front_face_y(r, f.cx, cz, f) + relief / 2 - 0.0015, zc + dz),
            mats["accent"], f"{tag}__grain_{j}")
    _drawer_pull(drawer, r, mats, f, cz, width, tag)


_FRONT_BUILDERS = {
    "plain_slab": _drawer_front_plain_slab_build,
    "grained_slab": _drawer_front_grained_slab_build,
}


def _build_drawers(model, carcass, r: ResolvedConfig, mats) -> list[object]:
    tag = f"drawer_front__{r.drawer_front}"
    drawers: list[object] = []
    for cell in _drawer_cells(r):
        cell_w = cell.x1 - cell.x0
        cx = (cell.x0 + cell.x1) / 2.0
        cz = (cell.z0 + cell.z1) / 2.0
        front_h = max(cell.z1 - cell.z0, 0.020)
        tray_half = max(cell_w / 2.0 - _RAIL_W - _SIDE_CLEAR, _MIN_TRAY_W / 2.0)
        tray_w = 2.0 * tray_half
        box_depth = max(cell.y_back - cell.y_front, 0.150) + _TRAY_FRONT_REACH
        travel = min(box_depth * r.drawer_travel_ratio, box_depth * 0.60)
        floor_z = cell.z0 + 0.014
        # the tray body always stays inside its own level band
        box_h = max(min(front_h - 0.022, cell.z1 - floor_z - 0.006), 0.024)
        frame = _Frame(cx=cx, y_ref=cell.y_front, z_ref=floor_z)
        box_cy = box_depth / 2.0 - _TRAY_FRONT_REACH

        drawer = model.part(
            f"drawer_front__{r.drawer_front}__drawer_{cell.index}",
            meta={"role": "drawer", "slot": "drawer_front", "candidate": r.drawer_front,
                  "level_index": cell.index, "hollow_tray": True, "travel_m": travel},
        )
        _bx(drawer, (tray_w, box_depth, _TRAY_FLOOR_T), (0.0, box_cy, _TRAY_FLOOR_T / 2),
            mats["wood"], f"{tag}__tray_floor_{cell.index}")
        for side, sign in enumerate((-1.0, 1.0)):
            _bx(drawer, (_TRAY_WALL_T, box_depth, box_h),
                (sign * (tray_half - _TRAY_WALL_T / 2), box_cy, box_h / 2), mats["wood"],
                f"{tag}__tray_side_{cell.index}_{side}")
            _bx(drawer, (_RUNNER_W, box_depth, _RAIL_H),
                (sign * (tray_half + _RUNNER_W / 2.0 - _RUNNER_ENGAGE), box_cy, -0.001),
                mats["dark"], f"{tag}__tray_runner_{cell.index}_{side}")
        _bx(drawer, (tray_w, _TRAY_WALL_T, box_h),
            (0.0, box_depth - _TRAY_FRONT_REACH - _TRAY_WALL_T / 2, box_h / 2), mats["wood"],
            f"{tag}__tray_rear_{cell.index}")
        for side, sign in enumerate((-1.0, 1.0)):
            x_cleat = cx + sign * max(tray_half - 0.024, 0.006)
            panel_back_local = _front_y(r, x_cleat, cz) - _FRONT_GAP - cell.y_front
            cleat_y0 = min(panel_back_local - 0.002, 0.002)
            _bx(drawer, (0.030, max(0.004, 0.004 - cleat_y0), _TRAY_FLOOR_T),
                (sign * max(tray_half - 0.024, 0.006), (cleat_y0 + 0.004) / 2.0, _TRAY_FLOOR_T / 2),
                mats["wood"], f"{tag}__front_cleat_{cell.index}_{side}")

        _FRONT_BUILDERS[r.drawer_front](
            drawer, r, mats, cell.x0, cell.x1, cz, front_h, frame, tag
        )

        mate = _plane_mate(
            provider_name=f"storage_layout.zone_split.cell_{cell.index}",
            provider_point=(cx, cell.y_front, floor_z),
            provider_extent=(cell_w, cell.z1 - cell.z0),
            consumer_name=f"drawer_front.tray_seat_{cell.index}",
            consumer_extent=(tray_w, box_h),
        )
        joint = f"drawer_front__{r.drawer_front}__slide_{cell.index}"
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
def build_pictureX_0611_Cabinet_with_doors_and_drawers(
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
    _LAYOUT_BUILDERS[r.storage_layout](carcass, r, mats)
    _MECHANISM_BUILDERS[r.door_mechanism](model, carcass, r, mats)
    _build_drawers(model, carcass, r, mats)
    carcass.inertial = None
    model.meta["slot_choices"] = (
        ("body_form", r.body_form),
        ("storage_layout", r.storage_layout),
        ("door_kind", r.door_kind),
        ("door_mechanism", r.door_mechanism),
        ("drawer_front", r.drawer_front),
        ("support_base", r.support_base),
        ("drawer_count", str(r.drawer_count)),
    )
    return model


def build_seeded_pictureX_0611_Cabinet_with_doors_and_drawers(seed: int) -> ArticulatedObject:
    return build_pictureX_0611_Cabinet_with_doors_and_drawers(config_from_seed(seed))


# ---------------------------------------------------------------------------
# author tests
# ---------------------------------------------------------------------------
def run_pictureX_0611_Cabinet_with_doors_and_drawers_tests(
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

    ctx.check("category_anchor: one load-bearing carcass",
              len(roles.get("carcass", [])) == 1, details=str(roles.get("carcass")))

    leaf_names = roles.get("door_leaf", [])
    drawer_names = roles.get("drawer", [])
    ctx.check(
        "category_anchor: the cabinet has both a door and a drawer",
        len(leaf_names) == r.door_leaf_count and len(drawer_names) == r.drawer_count
        and len(leaf_names) >= 1 and len(drawer_names) >= 1,
        details=f"leaves={leaf_names} drawers={drawer_names}",
    )

    moving = {
        j.child: j for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
    }
    ctx.check(
        "category_anchor: every drawer is a moving child of the carcass",
        all(
            name in moving and moving[name].parent == "carcass"
            and moving[name].articulation_type == ArticulationType.PRISMATIC
            for name in drawer_names
        ),
        details=str(drawer_names),
    )

    hollow = True
    for name in drawer_names:
        visuals = [str(v.name) for v in parts[name].visuals]
        if not (
            any("__tray_floor_" in v for v in visuals)
            and sum(1 for v in visuals if "__tray_side_" in v) == 2
            and any("__tray_rear_" in v for v in visuals)
            and any("__drawer_front" in v for v in visuals)
        ):
            hollow = False
    ctx.check("category_anchor: drawer trays are hollow boxes", hollow,
              details="floor + two sides + rear + front on every tray")

    leaf = leaf_names[0]
    joint = moving[leaf]
    rest = ctx.part_world_aabb(parts[leaf])
    limit = joint.motion_limits.upper or joint.motion_limits.lower or 0.0
    with ctx.pose({joint: limit * (0.6 if r.door_mechanism == "hinged_swing" else 1.0)}):
        opened = ctx.part_world_aabb(parts[leaf])
    if r.door_mechanism == "hinged_swing":
        ctx.check(
            "category_anchor: swing leaf opens outward from the front plane",
            rest is not None and opened is not None and opened[0][1] < rest[0][1] - 0.02,
            details=f"rest={None if rest is None else round(rest[0][1], 4)} "
            f"open={None if opened is None else round(opened[0][1], 4)}",
        )
    else:
        moved = (
            0.0 if rest is None or opened is None
            else abs((opened[0][0] + opened[1][0]) / 2 - (rest[0][0] + rest[1][0]) / 2)
        )
        ctx.check("category_anchor: sliding leaf translates across its zone", moved > 0.008,
                  details=f"dx={moved:.4f}")

    drawer = drawer_names[0]
    djoint = moving[drawer]
    d_rest = ctx.part_world_aabb(parts[drawer])
    with ctx.pose({djoint: djoint.motion_limits.upper or 0.0}):
        d_open = ctx.part_world_aabb(parts[drawer])
    ctx.check(
        "drawer pulls out along -Y",
        d_rest is not None and d_open is not None and d_open[0][1] < d_rest[0][1] - 0.02,
        details=f"rest={None if d_rest is None else round(d_rest[0][1], 4)} "
        f"open={None if d_open is None else round(d_open[0][1], 4)}",
    )

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    return ctx.report()


run_pictureX_0611_Cabinet_with_doors_and_drawers_tests.__test__ = False


TEMPLATE_CORNERS = (
    corner_case(
        "widest_bow_flanking_doors_four_drawers",
        {
            "body_form": "bow_front", "storage_layout": "doors_flanking_drawers",
            "door_kind": "glazed_lattice", "door_mechanism": "hinged_swing",
            "drawer_front": "grained_slab", "support_base": "tapered_legs",
            "drawer_count": 4, "carcass_width_m": 1.44, "carcass_depth_m": 0.52,
            "carcass_height_m": 1.60, "bow_depth_m": 0.052, "flank_column_ratio": 0.42,
            "door_swing_rad": 1.92, "drawer_travel_ratio": 0.62, "tapered_leg_h_m": 0.320,
        },
        reason="deepest bow with the widest flanks, full swing and the longest stroke",
    ),
    corner_case(
        "narrow_taper_sliding_door_beside_one_drawer",
        {
            "body_form": "tapered_box", "storage_layout": "door_beside_drawers",
            "door_kind": "recessed_panel", "door_mechanism": "sliding_track",
            "drawer_front": "plain_slab", "support_base": "stone_plinth",
            "drawer_count": 1, "carcass_width_m": 0.72, "carcass_depth_m": 0.34,
            "carcass_height_m": 1.68, "case_taper_ratio": 0.72, "door_column_ratio": 0.72,
            "slide_travel_m": 0.46, "stone_plinth_h_m": 0.050,
        },
        reason="strongest taper with the widest door column and the longest slide",
    ),
    corner_case(
        "tall_rect_drawers_over_sliding_doors",
        {
            "body_form": "rect_box", "storage_layout": "drawers_over_doors",
            "door_kind": "slab_panel", "door_mechanism": "sliding_track",
            "drawer_front": "grained_slab", "support_base": "apron_feet_plinth",
            "drawer_count": 4, "carcass_width_m": 1.60, "carcass_depth_m": 0.52,
            "carcass_height_m": 1.75, "drawer_zone_ratio": 0.70, "rect_wall_t_m": 0.030,
            "apron_plinth_h_m": 0.210, "slide_travel_m": 0.46,
        },
        reason="largest case with the deepest drawer zone over a sliding door zone",
    ),
    corner_case(
        "compact_doors_over_drawers_minimum",
        {
            "body_form": "rect_box", "storage_layout": "doors_over_drawers",
            "door_kind": "recessed_panel", "door_mechanism": "hinged_swing",
            "drawer_front": "plain_slab", "support_base": "metal_legs",
            "drawer_count": 1, "carcass_width_m": 0.72, "carcass_depth_m": 0.34,
            "carcass_height_m": 0.80, "door_zone_ratio": 0.78, "recess_depth_m": 0.018,
            "door_swing_rad": 1.92, "metal_leg_h_m": 0.300,
        },
        reason="smallest case with the tallest door zone squeezing the drawer bank",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_pictureX_0611_Cabinet_with_doors_and_drawers",
    "build_seeded_pictureX_0611_Cabinet_with_doors_and_drawers",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_Cabinet_with_doors_and_drawers_tests",
]
