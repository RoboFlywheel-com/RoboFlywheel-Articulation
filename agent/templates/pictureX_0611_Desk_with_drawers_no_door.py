# SPDX-License-Identifier: Apache-2.0

"""pictureX/0611 Desk_with_drawers (no door) — Design-backed single-file template.

A writing desk whose only articulation is a set of pull-out hollow drawers under a worktop:
one pedestal beside a knee hole, mirrored twin pedestals, a shallow apron band, or an L-shaped
run with a return wing. There is no door of any kind and no revolute joint anywhere.

The desk form publishes its drawer zones and its top footprint, so tray width, front height,
box depth, travel and the leg stations all derive from the real host and from N. Every declared
slot combination builds and no overlap allowance is emitted.

Coordinate convention: X = width, Y = depth with the FRONT at -Y, Z = height; drawers pull out
along -Y.
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
    LatheGeometry,
    MotionLimits,
    Origin,
    PlaneInterface,
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

DeskForm = Literal["single_pedestal", "twin_pedestal", "apron_rail_desk", "l_shaped_return"]
LegForm = Literal["turned_legs", "tapered_legs", "hairpin_frame", "panel_end"]
DrawerFront = Literal["bail_pull_front", "flush_front", "lipped_front"]
TopForm = Literal["rect_top", "leather_inset_top", "bullnose_top"]

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot(
            "desk_form",
            ("single_pedestal", "twin_pedestal", "apron_rail_desk", "l_shaped_return"),
        ),
        component_slot("leg_form", ("turned_legs", "tapered_legs", "hairpin_frame", "panel_end")),
        component_slot("drawer_front", ("bail_pull_front", "flush_front", "lipped_front")),
        component_slot("top_form", ("rect_top", "leather_inset_top", "bullnose_top")),
        multiplicity_slot("drawer_count", (1, 2, 3, 4, 5, 6), item_slot="drawer_front"),
    )
)

_WALL_T = 0.018
_BACK_T = 0.012
_FRONT_T = 0.019
_FRONT_GAP = 0.002
_RAIL_W = 0.014
_RAIL_EMBED = 0.010
_RAIL_H = 0.012
_RUNNER_W = 0.009
_RUNNER_ENGAGE = 0.003
_TRAY_WALL_T = 0.010
_TRAY_FLOOR_T = 0.010
_TRAY_FRONT_REACH = 0.016
_SIDE_CLEAR = 0.003
_LEVEL_REVEAL = 0.006
_MIN_FRONT_H = 0.050
_MIN_TRAY_W = 0.090

RGBA = tuple[float, float, float, float]
_PALETTES: tuple[dict[str, RGBA], ...] = (
    {"wood": (0.42, 0.26, 0.15, 1.0), "dark": (0.18, 0.11, 0.07, 1.0),
     "panel": (0.50, 0.33, 0.19, 1.0), "metal": (0.76, 0.64, 0.34, 1.0),
     "leather": (0.22, 0.32, 0.26, 1.0)},
    {"wood": (0.72, 0.56, 0.34, 1.0), "dark": (0.36, 0.26, 0.15, 1.0),
     "panel": (0.80, 0.66, 0.44, 1.0), "metal": (0.62, 0.63, 0.65, 1.0),
     "leather": (0.44, 0.20, 0.16, 1.0)},
    {"wood": (0.30, 0.31, 0.33, 1.0), "dark": (0.14, 0.15, 0.16, 1.0),
     "panel": (0.40, 0.41, 0.43, 1.0), "metal": (0.80, 0.82, 0.84, 1.0),
     "leather": (0.20, 0.21, 0.23, 1.0)},
    {"wood": (0.86, 0.83, 0.76, 1.0), "dark": (0.40, 0.37, 0.31, 1.0),
     "panel": (0.92, 0.90, 0.85, 1.0), "metal": (0.70, 0.71, 0.72, 1.0),
     "leather": (0.32, 0.36, 0.44, 1.0)},
)

_FORM_BOUNDS = {
    "single_pedestal": {"w": (0.90, 1.70), "d": (0.52, 0.80), "h": (0.70, 0.80)},
    "twin_pedestal": {"w": (1.10, 1.90), "d": (0.56, 0.84), "h": (0.70, 0.80)},
    "apron_rail_desk": {"w": (0.90, 1.60), "d": (0.50, 0.72), "h": (0.70, 0.80)},
    "l_shaped_return": {"w": (1.10, 1.80), "d": (0.56, 0.80), "h": (0.70, 0.80)},
}


@dataclass(frozen=True)
class Config:
    desk_form: DeskForm = "single_pedestal"
    leg_form: LegForm = "tapered_legs"
    drawer_front: DrawerFront = "lipped_front"
    top_form: TopForm = "rect_top"
    drawer_count: int = 3
    desk_width_m: float | None = None
    desk_depth_m: float | None = None
    desk_height_m: float | None = None
    pedestal_width_m: float | None = None
    apron_depth_m: float | None = None
    return_depth_m: float | None = None
    drawer_travel_ratio: float | None = None
    turned_leg_d_m: float | None = None
    tapered_leg_top_m: float | None = None
    hairpin_rod_r_m: float | None = None
    end_panel_t_m: float | None = None
    bail_drop_m: float | None = None
    grip_depth_m: float | None = None
    lip_proud_m: float | None = None
    rect_top_t_m: float | None = None
    inset_border_m: float | None = None
    bullnose_top_t_m: float | None = None
    palette: int = 0
    name: str = "pictureX_0611_Desk_with_drawers_no_door"


@dataclass(frozen=True)
class ResolvedConfig:
    desk_form: DeskForm
    leg_form: LegForm
    drawer_front: DrawerFront
    top_form: TopForm
    drawer_count: int
    palette: int
    name: str
    desk_width_m: float
    desk_depth_m: float
    desk_height_m: float
    pedestal_width_m: float
    apron_depth_m: float
    return_depth_m: float
    drawer_travel_ratio: float
    turned_leg_d_m: float
    tapered_leg_top_m: float
    hairpin_rod_r_m: float
    end_panel_t_m: float
    bail_drop_m: float
    grip_depth_m: float
    lip_proud_m: float
    rect_top_t_m: float
    inset_border_m: float
    bullnose_top_t_m: float
    top_t_m: float
    top_z_m: float
    front_y_m: float
    back_y_m: float
    front_t_m: float


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _pick(v, d):
    return d if v is None else float(v)


def config_from_seed(seed: int) -> Config:
    rng = random.Random(seed)
    form: DeskForm = rng.choice(
        ("single_pedestal", "twin_pedestal", "apron_rail_desk", "l_shaped_return")
    )
    b = _FORM_BOUNDS[form]
    return Config(
        desk_form=form,
        leg_form=rng.choice(("turned_legs", "tapered_legs", "hairpin_frame", "panel_end")),
        drawer_front=rng.choice(("bail_pull_front", "flush_front", "lipped_front")),
        top_form=rng.choice(("rect_top", "leather_inset_top", "bullnose_top")),
        drawer_count=rng.choice((1, 2, 3, 4, 5, 6)),
        desk_width_m=round(rng.uniform(*b["w"]), 3),
        desk_depth_m=round(rng.uniform(*b["d"]), 3),
        desk_height_m=round(rng.uniform(*b["h"]), 3),
        pedestal_width_m=round(rng.uniform(0.26, 0.48), 3),
        apron_depth_m=round(rng.uniform(0.090, 0.190), 3),
        return_depth_m=round(rng.uniform(0.36, 0.72), 3),
        drawer_travel_ratio=round(rng.uniform(0.34, 0.62), 3),
        turned_leg_d_m=round(rng.uniform(0.040, 0.080), 4),
        tapered_leg_top_m=round(rng.uniform(0.038, 0.072), 4),
        hairpin_rod_r_m=round(rng.uniform(0.006, 0.014), 4),
        end_panel_t_m=round(rng.uniform(0.018, 0.042), 4),
        bail_drop_m=round(rng.uniform(0.020, 0.055), 4),
        grip_depth_m=round(rng.uniform(0.008, 0.022), 4),
        lip_proud_m=round(rng.uniform(0.005, 0.018), 4),
        rect_top_t_m=round(rng.uniform(0.022, 0.044), 4),
        inset_border_m=round(rng.uniform(0.045, 0.120), 4),
        bullnose_top_t_m=round(rng.uniform(0.030, 0.060), 4),
        palette=rng.randrange(len(_PALETTES)),
        name=f"pictureX_0611_Desk_with_drawers_no_door_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    form = config.desk_form
    b = _FORM_BOUNDS[form]
    width = _clamp(_pick(config.desk_width_m, sum(b["w"]) / 2), *b["w"])
    depth = _clamp(_pick(config.desk_depth_m, sum(b["d"]) / 2), *b["d"])
    height = _clamp(_pick(config.desk_height_m, sum(b["h"]) / 2), *b["h"])
    top_form = config.top_form
    if top_form == "rect_top":
        top_t = _clamp(_pick(config.rect_top_t_m, 0.032), 0.022, 0.044)
    elif top_form == "bullnose_top":
        top_t = _clamp(_pick(config.bullnose_top_t_m, 0.044), 0.030, 0.060)
    else:
        top_t = 0.038
    return ResolvedConfig(
        desk_form=form,
        leg_form=config.leg_form,
        drawer_front=config.drawer_front,
        top_form=top_form,
        drawer_count=int(_clamp(int(config.drawer_count), 1, 6)),
        palette=int(config.palette) % len(_PALETTES),
        name=config.name,
        desk_width_m=width,
        desk_depth_m=depth,
        desk_height_m=height,
        pedestal_width_m=_clamp(_pick(config.pedestal_width_m, 0.360), 0.26, 0.48),
        apron_depth_m=_clamp(_pick(config.apron_depth_m, 0.140), 0.090, 0.190),
        return_depth_m=_clamp(_pick(config.return_depth_m, 0.540), 0.36, 0.72),
        drawer_travel_ratio=_clamp(_pick(config.drawer_travel_ratio, 0.48), 0.34, 0.62),
        turned_leg_d_m=_clamp(_pick(config.turned_leg_d_m, 0.058), 0.040, 0.080),
        tapered_leg_top_m=_clamp(_pick(config.tapered_leg_top_m, 0.054), 0.038, 0.072),
        hairpin_rod_r_m=_clamp(_pick(config.hairpin_rod_r_m, 0.010), 0.006, 0.014),
        end_panel_t_m=_clamp(_pick(config.end_panel_t_m, 0.028), 0.018, 0.042),
        bail_drop_m=_clamp(_pick(config.bail_drop_m, 0.036), 0.020, 0.055),
        grip_depth_m=_clamp(_pick(config.grip_depth_m, 0.014), 0.008, 0.022),
        lip_proud_m=_clamp(_pick(config.lip_proud_m, 0.010), 0.005, 0.018),
        rect_top_t_m=_clamp(_pick(config.rect_top_t_m, 0.032), 0.022, 0.044),
        inset_border_m=_clamp(_pick(config.inset_border_m, 0.080), 0.045, 0.120),
        bullnose_top_t_m=_clamp(_pick(config.bullnose_top_t_m, 0.044), 0.030, 0.060),
        top_t_m=top_t,
        top_z_m=height,
        front_y_m=-depth / 2.0,
        back_y_m=depth / 2.0 - _BACK_T,
        front_t_m=_FRONT_T,
    )


def _bx(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size=(float(size[0]), float(size[1]), float(size[2]))),
                origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
                material=material, name=name, material_class_id="wood.veneer_panel")


def _cy(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Cylinder(radius=float(radius), length=float(length)),
                origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
                material=material, name=name, material_class_id="metal.brushed_silver")


def _materials(model, palette):
    table = _PALETTES[palette % len(_PALETTES)]
    return {k: model.material(f"desk_{palette}_{k}", rgba=v) for k, v in table.items()}


def _plane_mate(*, provider_name, provider_point, provider_extent, consumer_name, consumer_extent):
    provider = PlaneInterface(name=provider_name, point=tuple(float(v) for v in provider_point),
                              normal=(0.0, -1.0, 0.0), tangent_u=(1.0, 0.0, 0.0), extent=provider_extent)
    consumer = PlaneInterface(name=consumer_name, point=(0.0, 0.0, 0.0), normal=(0.0, 1.0, 0.0),
                              tangent_u=(1.0, 0.0, 0.0), extent=consumer_extent)
    return mate_planes(provider, consumer)


# --------------------------------------------------------------------------- zones
@dataclass(frozen=True)
class _Zone:
    x0: float
    x1: float
    z0: float
    z1: float
    y_front: float
    y_back: float


def _zones(r: ResolvedConfig) -> list[_Zone]:
    """Drawer zones published by the desk form, left to right."""

    half_w = r.desk_width_m / 2.0
    top_lo = r.top_z_m - r.top_t_m
    y_front = r.front_y_m + 0.010
    y_back = r.back_y_m
    if r.desk_form == "apron_rail_desk":
        z1 = top_lo - 0.012
        z0 = z1 - r.apron_depth_m
        return [_Zone(-half_w + 0.060, half_w - 0.060, z0, z1, y_front, y_back)]
    # the pedestal keeps its declared width on a wide desk and shrinks with the host
    pw = r.pedestal_width_m * min(1.0, half_w / 0.62)
    z1 = top_lo - 0.034
    z0 = 0.070
    if r.desk_form == "twin_pedestal":
        return [
            _Zone(-half_w + 0.010, -half_w + pw, z0, z1, y_front, y_back),
            _Zone(half_w - pw, half_w - 0.010, z0, z1, y_front, y_back),
        ]
    return [_Zone(half_w - pw, half_w - 0.010, z0, z1, y_front, y_back)]


def _zone_inner(zone: _Zone) -> tuple[float, float]:
    """Clear span inside the zone's own side walls."""

    return zone.x0 + _WALL_T, zone.x1 - _WALL_T


@dataclass(frozen=True)
class _Cell:
    index: int
    zone: _Zone
    z0: float
    z1: float


def _cells(r: ResolvedConfig) -> list[_Cell]:
    zones = _zones(r)
    n = r.drawer_count
    per_zone = [n // len(zones)] * len(zones)
    for i in range(n - sum(per_zone)):
        per_zone[i] += 1
    cells: list[_Cell] = []
    index = 0
    for zone, count in zip(zones, per_zone):
        if count <= 0:
            continue
        gap = _LEVEL_REVEAL
        band = (zone.z1 - zone.z0 - (count - 1) * gap) / count
        if band < _MIN_FRONT_H:
            gap = 0.002
            band = max((zone.z1 - zone.z0 - (count - 1) * gap) / count, 0.024)
        z = zone.z0
        for _k in range(count):
            cells.append(_Cell(index, zone, z, z + band))
            index += 1
            z += band + gap
    return cells


# --------------------------------------------------------------------------- desk_form
def _pedestal_box(desk, r, mats, zone: _Zone, tag: str, index: int) -> None:
    w = zone.x1 - zone.x0
    cx = (zone.x0 + zone.x1) / 2.0
    h = zone.z1 - zone.z0
    d = zone.y_back - zone.y_front + 0.020
    cy = (zone.y_front + zone.y_back) / 2.0 - 0.010
    # the side panels run from below the cavity floor up into the worktop
    top_lo = r.top_z_m - r.top_t_m + 0.002
    side_lo = zone.z0 - 0.022
    for i, sx in enumerate((-1.0, 1.0)):
        _bx(desk, (_WALL_T, d, top_lo - side_lo), (cx + sx * (w / 2 - _WALL_T / 2), cy,
                                                   (side_lo + top_lo) / 2.0),
            mats["wood"], f"{tag}__pedestal_side_{index}_{i}")
    _bx(desk, (w, d, _WALL_T), (cx, cy, zone.z0 - _WALL_T / 2 - 0.001), mats["wood"],
        f"{tag}__pedestal_floor_{index}")
    _bx(desk, (w - 2 * _WALL_T + 0.004, _BACK_T, h - 0.006), (cx, zone.y_back + _BACK_T / 2, (zone.z0 + zone.z1) / 2.0),
        mats["dark"], f"{tag}__pedestal_back_{index}")
    _bx(desk, (w, d, 0.018), (cx, cy, top_lo - 0.009), mats["wood"], f"{tag}__pedestal_cap_{index}")


def _runner_rails(desk, r, mats, tag: str) -> None:
    cells = _cells(r)
    previous: dict[int, float] = {}
    for i, cell in enumerate(cells):
        if i > 0 and cells[i - 1].zone is cell.zone:
            previous[cell.index] = cells[i - 1].z1
    for cell in cells:
        zone = cell.zone
        y0 = zone.y_front + 0.002
        y1 = zone.y_back + 0.004
        ix0, ix1 = _zone_inner(zone)
        for side, x in ((0, ix0), (1, ix1)):
            direction = 1.0 if side == 0 else -1.0
            _bx(desk, (_RAIL_W + _RAIL_EMBED, max(y1 - y0, 0.10), _RAIL_H),
                (x + direction * (_RAIL_W - _RAIL_EMBED) / 2.0, (y0 + y1) / 2.0,
                 cell.z0 + _RAIL_H / 2 - 0.002), mats["dark"],
                f"{tag}__runner_rail_{cell.index}_{side}")
        prev_top = previous.get(cell.index)
        if prev_top is not None:
            gap = cell.z0 - prev_top
            if gap >= 0.005:
                _bx(desk, (ix1 - ix0 + 0.030, max(y1 - y0, 0.10), min(0.010, gap * 0.7)),
                    ((ix0 + ix1) / 2.0, (y0 + y1) / 2.0, (prev_top + cell.z0) / 2.0),
                    mats["dark"], f"{tag}__level_rail_{cell.index}")


def _desk_form_single_pedestal_build(desk, r, mats) -> None:
    tag = "desk_form__single_pedestal"
    for i, zone in enumerate(_zones(r)):
        _pedestal_box(desk, r, mats, zone, tag, i)
    _runner_rails(desk, r, mats, tag)


def _desk_form_twin_pedestal_build(desk, r, mats) -> None:
    tag = "desk_form__twin_pedestal"
    for i, zone in enumerate(_zones(r)):
        _pedestal_box(desk, r, mats, zone, tag, i)
    _runner_rails(desk, r, mats, tag)


def _desk_form_apron_rail_desk_build(desk, r, mats) -> None:
    tag = "desk_form__apron_rail_desk"
    zone = _zones(r)[0]
    w = r.desk_width_m
    d = zone.y_back - zone.y_front + 0.020
    cy = (zone.y_front + zone.y_back) / 2.0 - 0.010
    zc = (zone.z0 + zone.z1) / 2.0
    lo = zone.z0 - 0.024
    hi = r.top_z_m - r.top_t_m + 0.002
    for i, sx in enumerate((-1.0, 1.0)):
        _bx(desk, (_WALL_T, d, hi - lo), (sx * (w / 2 - 0.030), cy, (lo + hi) / 2.0), mats["wood"],
            f"{tag}__apron_end_{i}")
    _bx(desk, (w - 0.040, 0.016, hi - lo), (0.0, zone.y_back + 0.008, (lo + hi) / 2.0), mats["wood"],
        f"{tag}__apron_back_rail")
    _bx(desk, (w - 0.040, d, 0.020), (0.0, cy, zone.z0 - 0.012), mats["wood"],
        f"{tag}__apron_bottom_rail")
    del zc
    _runner_rails(desk, r, mats, tag)


def _desk_form_l_shaped_return_build(desk, r, mats) -> None:
    tag = "desk_form__l_shaped_return"
    for i, zone in enumerate(_zones(r)):
        _pedestal_box(desk, r, mats, zone, tag, i)
    _runner_rails(desk, r, mats, tag)
    # the return wing and its own end support
    ret_d = r.return_depth_m
    ret_w = r.desk_width_m * 0.42
    y0 = r.desk_depth_m / 2.0
    cx = -r.desk_width_m / 2.0 + ret_w / 2.0
    _bx(desk, (ret_w, ret_d + 0.030, r.top_t_m), (cx, y0 + ret_d / 2 - 0.018, r.top_z_m - r.top_t_m / 2),
        mats["wood"], f"{tag}__return_top")
    _bx(desk, (0.030, 0.030, r.top_z_m - r.top_t_m + 0.006),
        (cx - ret_w / 2 + 0.030, y0 + ret_d - 0.040, (r.top_z_m - r.top_t_m + 0.006) / 2.0), mats["wood"],
        f"{tag}__return_leg_0")
    _bx(desk, (0.030, 0.030, r.top_z_m - r.top_t_m + 0.006),
        (cx + ret_w / 2 - 0.030, y0 + ret_d - 0.040, (r.top_z_m - r.top_t_m + 0.006) / 2.0), mats["wood"],
        f"{tag}__return_leg_1")


_FORM_BUILDERS = {
    "single_pedestal": _desk_form_single_pedestal_build,
    "twin_pedestal": _desk_form_twin_pedestal_build,
    "apron_rail_desk": _desk_form_apron_rail_desk_build,
    "l_shaped_return": _desk_form_l_shaped_return_build,
}


# --------------------------------------------------------------------------- leg_form
def _leg_stations(r: ResolvedConfig) -> list[tuple[float, float]]:
    """Corner stations of the top that are not already carried by a pedestal."""

    half_w = r.desk_width_m / 2.0
    ly = r.desk_depth_m / 2.0 - 0.060
    zones = _zones(r)
    stations: list[tuple[float, float]] = []
    for sx in (-1.0, 1.0):
        x = sx * (half_w - 0.055)
        covered = any(z.x0 - 0.020 <= x <= z.x1 + 0.020 and z.z0 < 0.20 for z in zones)
        if covered:
            continue
        stations.append((x, -ly))
        stations.append((x, ly))
    if not stations:
        stations = [(0.0, -ly), (0.0, ly)]
    return stations


def _leg_form_turned_legs_build(desk, r, mats) -> None:
    tag = "leg_form__turned_legs"
    h = r.top_z_m - r.top_t_m + 0.005
    rad = r.turned_leg_d_m / 2.0
    profile = [(0.0, 0.0), (rad * 0.86, 0.0), (rad * 0.70, h * 0.20), (rad, h * 0.42),
               (rad * 0.64, h * 0.70), (rad * 0.88, h * 0.92), (rad * 0.70, h), (0.0, h)]
    leg = mesh_from_geometry(LatheGeometry(profile, segments=20), f"{tag}__turned_leg_mesh")
    for i, (x, y) in enumerate(_leg_stations(r)):
        desk.visual(leg, origin=Origin(xyz=(x, y, 0.0)), material=mats["wood"], name=f"{tag}__leg_{i}", material_class_id="wood.polished_varnished")


def _leg_form_tapered_legs_build(desk, r, mats) -> None:
    tag = "leg_form__tapered_legs"
    h = r.top_z_m - r.top_t_m + 0.005
    top = r.tapered_leg_top_m
    for i, (x, y) in enumerate(_leg_stations(r)):
        for j in range(4):
            t0, t1 = j / 4.0, (j + 1) / 4.0
            z0, z1 = h * t0, h * t1
            side = top * (1.0 - 0.45 * (t0 + t1) / 2.0)
            _bx(desk, (side, side, z1 - z0 + 0.006), (x, y, (z0 + z1) / 2.0), mats["wood"],
                f"{tag}__leg_{i}_{j}")


def _leg_form_hairpin_frame_build(desk, r, mats) -> None:
    tag = "leg_form__hairpin_frame"
    h = r.top_z_m - r.top_t_m + 0.005
    rod = r.hairpin_rod_r_m
    for i, (x, y) in enumerate(_leg_stations(r)):
        _cy(desk, rod, h, (x, y, h / 2.0), mats["metal"], f"{tag}__rod_{i}")
        _cy(desk, rod * 0.9, 0.090, (x, y + math.copysign(0.045, -y), h - 0.030), mats["metal"],
            f"{tag}__brace_{i}", rpy=(math.pi / 2, 0.0, 0.0))
        _cy(desk, rod * 1.8, 0.010, (x, y, 0.005), mats["dark"], f"{tag}__foot_{i}")


def _leg_form_panel_end_build(desk, r, mats) -> None:
    tag = "leg_form__panel_end"
    h = r.top_z_m - r.top_t_m + 0.005
    t = r.end_panel_t_m
    seen_x: list[float] = []
    for i, (x, y) in enumerate(_leg_stations(r)):
        if any(abs(x - sx) < 1e-6 for sx in seen_x):
            continue
        seen_x.append(x)
        _bx(desk, (t, r.desk_depth_m - 0.060, h), (x, 0.0, h / 2.0), mats["wood"], f"{tag}__end_panel_{i}")
        _bx(desk, (t + 0.020, r.desk_depth_m - 0.040, 0.018), (x, 0.0, 0.009), mats["dark"],
            f"{tag}__end_plinth_{i}")


_LEG_BUILDERS = {
    "turned_legs": _leg_form_turned_legs_build,
    "tapered_legs": _leg_form_tapered_legs_build,
    "hairpin_frame": _leg_form_hairpin_frame_build,
    "panel_end": _leg_form_panel_end_build,
}


# --------------------------------------------------------------------------- top_form
def _top_form_rect_top_build(desk, r, mats) -> None:
    tag = "top_form__rect_top"
    _bx(desk, (r.desk_width_m, r.desk_depth_m, r.top_t_m), (0.0, 0.0, r.top_z_m - r.top_t_m / 2),
        mats["wood"], f"{tag}__worktop")
    _bx(desk, (r.desk_width_m, 0.012, r.top_t_m * 0.6),
        (0.0, -r.desk_depth_m / 2 + 0.004, r.top_z_m - r.top_t_m / 2), mats["dark"],
        f"{tag}__front_edge_band")


def _top_form_leather_inset_top_build(desk, r, mats) -> None:
    tag = "top_form__leather_inset_top"
    _bx(desk, (r.desk_width_m, r.desk_depth_m, r.top_t_m), (0.0, 0.0, r.top_z_m - r.top_t_m / 2),
        mats["wood"], f"{tag}__worktop")
    border = min(r.inset_border_m, r.desk_width_m * 0.22, r.desk_depth_m * 0.22)
    fw = max(r.desk_width_m - 2 * border, r.desk_width_m * 0.25)
    fd = max(r.desk_depth_m - 2 * border, r.desk_depth_m * 0.25)
    _bx(desk, (fw, fd, 0.006), (0.0, 0.0, r.top_z_m - 0.002), mats["leather"], f"{tag}__writing_field")
    for i, (sx, sy, sw, sd) in enumerate((
        (0.0, (fd + 0.010) / 2, fw + 0.020, 0.010),
        (0.0, -(fd + 0.010) / 2, fw + 0.020, 0.010),
        ((fw + 0.010) / 2, 0.0, 0.010, fd + 0.020),
        (-(fw + 0.010) / 2, 0.0, 0.010, fd + 0.020),
    )):
        _bx(desk, (sw, sd, 0.008), (sx, sy, r.top_z_m - 0.003), mats["metal"], f"{tag}__field_bead_{i}")


def _top_form_bullnose_top_build(desk, r, mats) -> None:
    tag = "top_form__bullnose_top"
    _bx(desk, (r.desk_width_m, r.desk_depth_m, r.top_t_m), (0.0, 0.0, r.top_z_m - r.top_t_m / 2),
        mats["wood"], f"{tag}__worktop")
    _cy(desk, r.top_t_m * 0.48, r.desk_width_m,
        (0.0, -r.desk_depth_m / 2 + 0.004, r.top_z_m - r.top_t_m / 2), mats["wood"],
        f"{tag}__bullnose_edge", rpy=(0.0, math.pi / 2, 0.0))


_TOP_BUILDERS = {
    "rect_top": _top_form_rect_top_build,
    "leather_inset_top": _top_form_leather_inset_top_build,
    "bullnose_top": _top_form_bullnose_top_build,
}


# --------------------------------------------------------------------------- drawer_front
def _drawer_front_bail_pull_front_build(drawer, r, mats, w, h, y0, tag) -> None:
    t = r.front_t_m
    _bx(drawer, (w, t, h), (0.0, y0 + t / 2, 0.0), mats["panel"], f"{tag}__front_slab")
    fw = max(w - 0.070, w * 0.35)
    fh = max(h - 0.030, h * 0.35)
    for label, (dx, dz, sx, sz) in {
        "moulding_top": (0.0, fh / 2, fw, 0.010),
        "moulding_bottom": (0.0, -fh / 2, fw, 0.010),
        "moulding_left": (-fw / 2, 0.0, 0.010, fh),
        "moulding_right": (fw / 2, 0.0, 0.010, fh),
    }.items():
        _bx(drawer, (sx, 0.008, sz), (dx, y0 - 0.002, dz), mats["wood"], f"{tag}__{label}")
    drop = min(r.bail_drop_m, h * 0.42)
    _bx(drawer, (min(0.130, w * 0.42), 0.006, min(0.040, h * 0.4)), (0.0, y0 - 0.002, 0.0),
        mats["metal"], f"{tag}__bail_backplate")
    _cy(drawer, 0.005, min(0.110, w * 0.34), (0.0, y0 - 0.008, -drop / 2), mats["metal"],
        f"{tag}__bail_bar", rpy=(0.0, math.pi / 2, 0.0))
    for i, sx in enumerate((-1.0, 1.0)):
        _cy(drawer, 0.004, drop, (sx * min(0.055, w * 0.17), y0 - 0.006, -drop / 2), mats["metal"],
            f"{tag}__bail_arm_{i}")


def _drawer_front_flush_front_build(drawer, r, mats, w, h, y0, tag) -> None:
    t = r.front_t_m
    depth = r.grip_depth_m * 0.60
    _bx(drawer, (w, t, h), (0.0, y0 + t / 2, 0.0), mats["panel"], f"{tag}__front_slab")
    _bx(drawer, (max(w - 0.060, w * 0.4), depth, min(0.026, h * 0.30)),
        (0.0, y0 + depth / 2 + 0.001, h * 0.30), mats["dark"], f"{tag}__finger_grip")


def _drawer_front_lipped_front_build(drawer, r, mats, w, h, y0, tag) -> None:
    t = r.front_t_m
    proud = r.lip_proud_m
    _bx(drawer, (w, t, h), (0.0, y0 + t / 2, 0.0), mats["panel"], f"{tag}__front_slab")
    for i, dz in enumerate((h / 2 - 0.008, -h / 2 + 0.008)):
        _bx(drawer, (w + 0.006, proud + 0.006, 0.016), (0.0, y0 - proud / 2 + 0.002, dz),
            mats["wood"], f"{tag}__lip_band_{i}")
    _cy(drawer, 0.011, 0.014, (0.0, y0 - 0.005, 0.0), mats["metal"], f"{tag}__knob",
        rpy=(math.pi / 2, 0.0, 0.0))


_FRONT_BUILDERS = {
    "bail_pull_front": _drawer_front_bail_pull_front_build,
    "flush_front": _drawer_front_flush_front_build,
    "lipped_front": _drawer_front_lipped_front_build,
}


def _build_drawers(model, desk, r: ResolvedConfig, mats) -> list[object]:
    tag = f"drawer_front__{r.drawer_front}"
    drawers: list[object] = []
    for cell in _cells(r):
        zone = cell.zone
        ix0, ix1 = _zone_inner(zone)
        cell_w = ix1 - ix0
        cx = (ix0 + ix1) / 2.0
        band = cell.z1 - cell.z0
        tray_half = max(cell_w / 2.0 - _RAIL_W - _SIDE_CLEAR, _MIN_TRAY_W / 2.0)
        tray_w = 2 * tray_half
        box_depth = max(zone.y_back - zone.y_front, 0.140) + _TRAY_FRONT_REACH
        travel = min(box_depth * r.drawer_travel_ratio, box_depth * 0.60)
        floor_z = cell.z0 + 0.012
        box_h = max(min(band - 0.020, cell.z1 - floor_z - 0.010), 0.016)
        box_cy = box_depth / 2.0 - _TRAY_FRONT_REACH
        drawer = model.part(
            f"drawer_front__{r.drawer_front}__drawer_{cell.index}",
            meta={"role": "drawer", "slot": "drawer_front", "candidate": r.drawer_front,
                  "index": cell.index, "hollow_tray": True, "travel_m": travel},
        )
        _bx(drawer, (tray_w, box_depth, _TRAY_FLOOR_T), (0.0, box_cy, _TRAY_FLOOR_T / 2), mats["wood"],
            f"{tag}__tray_floor_{cell.index}")
        for side, sign in enumerate((-1.0, 1.0)):
            _bx(drawer, (_TRAY_WALL_T, box_depth, box_h),
                (sign * (tray_half - _TRAY_WALL_T / 2), box_cy, box_h / 2), mats["wood"],
                f"{tag}__tray_side_{cell.index}_{side}")
            _bx(drawer, (_RUNNER_W, box_depth, _RAIL_H),
                (sign * (tray_half + _RUNNER_W / 2 - _RUNNER_ENGAGE), box_cy, -0.001), mats["dark"],
                f"{tag}__tray_runner_{cell.index}_{side}")
        _bx(drawer, (tray_w, _TRAY_WALL_T, box_h),
            (0.0, box_depth - _TRAY_FRONT_REACH - _TRAY_WALL_T / 2, box_h / 2), mats["wood"],
            f"{tag}__tray_rear_{cell.index}")
        face_y0 = r.front_y_m - _FRONT_GAP - r.front_t_m - zone.y_front
        # the face is authored about its own centre, then lifted onto the level
        before = len(list(drawer.visuals))
        _FRONT_BUILDERS[r.drawer_front](drawer, r, mats, cell_w - 0.004, band - 0.004, face_y0, tag)
        lift = (cell.z0 + cell.z1) / 2.0 - floor_z
        for v in list(drawer.visuals)[before:]:
            x, y, z = v.origin.xyz
            v.origin = Origin(xyz=(x, y, z + lift), rpy=v.origin.rpy)
        mate = _plane_mate(provider_name=f"desk_form.drawer_zone.cell_{cell.index}",
                           provider_point=(cx, zone.y_front, floor_z),
                           provider_extent=(cell_w, band),
                           consumer_name=f"drawer_front.tray_seat_{cell.index}",
                           consumer_extent=(tray_w, box_h))
        joint = f"{tag}__slide_{cell.index}"
        model.articulation(joint, ArticulationType.PRISMATIC, parent=desk, child=drawer,
                           origin=mate.origin, axis=(0.0, -1.0, 0.0),
                           motion_limits=MotionLimits(effort=55.0, velocity=0.30, lower=0.0, upper=travel),
                           meta={"mechanism": "side runner pair riding on the pedestal rails"})
        register_interface_mate(model, joint, mate)
        drawers.append(drawer)
    return drawers


# --------------------------------------------------------------------------- build
def build_pictureX_0611_Desk_with_drawers_no_door(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r.palette)
    desk = model.part("desk", meta={"role": "desk", "slot": "desk_form", "candidate": r.desk_form})
    _LEG_BUILDERS[r.leg_form](desk, r, mats)
    _FORM_BUILDERS[r.desk_form](desk, r, mats)
    _TOP_BUILDERS[r.top_form](desk, r, mats)
    _build_drawers(model, desk, r, mats)
    desk.inertial = None
    model.meta["slot_choices"] = (
        ("desk_form", r.desk_form),
        ("leg_form", r.leg_form),
        ("drawer_front", r.drawer_front),
        ("top_form", r.top_form),
        ("drawer_count", str(r.drawer_count)),
    )
    return model


def build_seeded_pictureX_0611_Desk_with_drawers_no_door(seed: int) -> ArticulatedObject:
    return build_pictureX_0611_Desk_with_drawers_no_door(config_from_seed(seed))


def run_pictureX_0611_Desk_with_drawers_no_door_tests(
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

    ctx.check("category_anchor: one desk carcass", len(roles.get("desk", [])) == 1,
              details=str(roles.get("desk")))

    drawer_names = roles.get("drawer", [])
    moving = {j.child: j for j in object_model.articulations
              if j.articulation_type != ArticulationType.FIXED}
    ctx.check(
        "category_anchor: every drawer is a moving child of the desk",
        len(drawer_names) == r.drawer_count
        and all(name in moving and moving[name].parent == "desk"
                and moving[name].articulation_type == ArticulationType.PRISMATIC
                for name in drawer_names),
        details=f"drawers={drawer_names} expected={r.drawer_count}",
    )

    hollow = all(
        any("__tray_floor_" in str(v.name) for v in parts[n].visuals)
        and sum(1 for v in parts[n].visuals if "__tray_side_" in str(v.name)) == 2
        and any("__tray_rear_" in str(v.name) for v in parts[n].visuals)
        for n in drawer_names
    )
    ctx.check("category_anchor: drawer trays are hollow boxes", hollow,
              details="floor + two sides + rear on every tray")

    ctx.check(
        "category_anchor: the desk has no door leaf",
        all(j.articulation_type != ArticulationType.REVOLUTE for j in object_model.articulations)
        and not any("door" in n for n in parts),
        details=str([j.articulation_type.name for j in object_model.articulations][:8]),
    )

    name = drawer_names[0]
    joint = moving[name]
    rest = ctx.part_world_aabb(parts[name])
    with ctx.pose({joint: joint.motion_limits.upper or 0.0}):
        opened = ctx.part_world_aabb(parts[name])
    ctx.check(
        "drawer pulls out along -Y",
        rest is not None and opened is not None and opened[0][1] < rest[0][1] - 0.02,
        details=f"rest={None if rest is None else round(rest[0][1], 4)} open={None if opened is None else round(opened[0][1], 4)}",
    )

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    return ctx.report()


run_pictureX_0611_Desk_with_drawers_no_door_tests.__test__ = False


TEMPLATE_CORNERS = (
    corner_case(
        "widest_twin_pedestal_six_drawers",
        {"desk_form": "twin_pedestal", "leg_form": "panel_end", "drawer_front": "bail_pull_front",
         "top_form": "leather_inset_top", "drawer_count": 6, "desk_width_m": 1.90,
         "desk_depth_m": 0.84, "desk_height_m": 0.80, "pedestal_width_m": 0.44,
         "drawer_travel_ratio": 0.62, "inset_border_m": 0.120, "end_panel_t_m": 0.042},
        reason="largest desk with both pedestals full and the longest stroke",
    ),
    corner_case(
        "shallow_apron_single_drawer",
        {"desk_form": "apron_rail_desk", "leg_form": "turned_legs", "drawer_front": "flush_front",
         "top_form": "bullnose_top", "drawer_count": 1, "desk_width_m": 0.90,
         "desk_depth_m": 0.50, "desk_height_m": 0.70, "apron_depth_m": 0.090,
         "drawer_travel_ratio": 0.34, "grip_depth_m": 0.022, "bullnose_top_t_m": 0.060},
        reason="shallowest apron band carrying one drawer under the thickest bullnose top",
    ),
    corner_case(
        "l_shaped_six_drawers_hairpin",
        {"desk_form": "l_shaped_return", "leg_form": "hairpin_frame", "drawer_front": "lipped_front",
         "top_form": "rect_top", "drawer_count": 6, "desk_width_m": 1.10, "desk_depth_m": 0.56,
         "desk_height_m": 0.70, "return_depth_m": 0.72, "pedestal_width_m": 0.26,
         "lip_proud_m": 0.018, "hairpin_rod_r_m": 0.006},
        reason="narrowest pedestal stacked six deep beside the longest return on the thinnest rods",
    ),
    corner_case(
        "single_pedestal_five_tapered",
        {"desk_form": "single_pedestal", "leg_form": "tapered_legs", "drawer_front": "bail_pull_front",
         "top_form": "leather_inset_top", "drawer_count": 5, "desk_width_m": 0.90,
         "desk_depth_m": 0.80, "desk_height_m": 0.70, "pedestal_width_m": 0.48,
         "bail_drop_m": 0.055, "inset_border_m": 0.045, "tapered_leg_top_m": 0.072},
        reason="shortest desk with the widest pedestal, five levels and the deepest bail drop",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_pictureX_0611_Desk_with_drawers_no_door",
    "build_seeded_pictureX_0611_Desk_with_drawers_no_door",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_Desk_with_drawers_no_door_tests",
]
