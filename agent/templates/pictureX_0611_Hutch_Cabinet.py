# SPDX-License-Identifier: Apache-2.0

"""pictureX/0611 Hutch_Cabinet — Design-backed single-file template.

A two-tier dresser: a deeper base cabinet carries a shallower upper case under a crown.
Both tiers are real storage — the base always holds articulated units (hinged leaves, a drawer
bank or pull-out bottle cradles) and the upper case carries its own front (hinged or bypass
glazing, a tambour curtain, a fall front, a lift-up flap) or an open shelf bay.

Each tier publishes its own clear opening, so leaf and tray sizes, hinge lines, track runs,
cradle pitch and travel all derive from the tier they belong to and from N. Every declared
slot combination builds and no overlap allowance is emitted.

Coordinate convention: X = width, Y = depth with the FRONT at -Y, Z = height.
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
    multiplicity_slot,
    register_interface_mate,
)

UpperFront = Literal[
    "glass_hinged_doors",
    "open_shelves",
    "sliding_glass_doors",
    "tambour_roll",
    "drop_front_desk",
    "lift_up_flap",
]
LowerFront = Literal["double_doors", "drawer_bank", "wine_cubby_grid"]
CrownForm = Literal["moulded_cornice", "arched_pediment"]
BackTreatment = Literal["plain_back", "plate_rack"]

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot(
            "upper_front",
            (
                "glass_hinged_doors",
                "open_shelves",
                "sliding_glass_doors",
                "tambour_roll",
                "drop_front_desk",
                "lift_up_flap",
            ),
        ),
        component_slot("lower_front", ("double_doors", "drawer_bank", "wine_cubby_grid")),
        component_slot("crown_form", ("moulded_cornice", "arched_pediment")),
        component_slot("back_treatment", ("plain_back", "plate_rack")),
        multiplicity_slot("lower_unit_count", (1, 2, 3, 4), item_slot="lower_front"),
        multiplicity_slot("upper_shelf_count", (1, 2, 3), item_slot="back_treatment"),
    )
)

_WALL_T = 0.020
_DECK_T = 0.030
_TOP_T = 0.024
_PLINTH_H = 0.090
_LEAF_T = 0.020
_LEAF_GAP = 0.002
_BARREL_R = 0.008
_LEAF_SETBACK = 0.012
_REVEAL = 0.008
_OUTER_REVEAL = 0.024
_TRAY_WALL_T = 0.011
_TRAY_FLOOR_T = 0.011
_RAIL_W = 0.014
_RAIL_EMBED = 0.012
_RAIL_H = 0.012
_RUNNER_W = 0.009
_RUNNER_ENGAGE = 0.003
_TRAY_FRONT_REACH = 0.016
_SIDE_CLEAR = 0.003
_LEVEL_REVEAL = 0.008
_UPPER_DEPTH_RATIO = 0.62
_MIN_LEAF_W = 0.060
_MIN_FRONT_H = 0.055
_MIN_SHELF_GAP = 0.110
_SHELF_T = 0.018

RGBA = tuple[float, float, float, float]
_PALETTES: tuple[dict[str, RGBA], ...] = (
    {"wood": (0.42, 0.26, 0.15, 1.0), "dark": (0.18, 0.11, 0.06, 1.0),
     "panel": (0.52, 0.34, 0.20, 1.0), "metal": (0.76, 0.64, 0.34, 1.0),
     "glass": (0.58, 0.68, 0.72, 0.32), "accent": (0.70, 0.52, 0.28, 1.0)},
    {"wood": (0.86, 0.84, 0.78, 1.0), "dark": (0.38, 0.36, 0.31, 1.0),
     "panel": (0.92, 0.90, 0.85, 1.0), "metal": (0.68, 0.60, 0.36, 1.0),
     "glass": (0.62, 0.72, 0.76, 0.30), "accent": (0.56, 0.46, 0.30, 1.0)},
    {"wood": (0.25, 0.34, 0.30, 1.0), "dark": (0.12, 0.18, 0.16, 1.0),
     "panel": (0.33, 0.43, 0.38, 1.0), "metal": (0.78, 0.68, 0.38, 1.0),
     "glass": (0.60, 0.70, 0.72, 0.30), "accent": (0.84, 0.78, 0.58, 1.0)},
    {"wood": (0.55, 0.55, 0.57, 1.0), "dark": (0.24, 0.25, 0.26, 1.0),
     "panel": (0.66, 0.66, 0.68, 1.0), "metal": (0.80, 0.82, 0.84, 1.0),
     "glass": (0.60, 0.70, 0.78, 0.30), "accent": (0.40, 0.42, 0.44, 1.0)},
)

_CROWN_BOUNDS = {
    "moulded_cornice": {"w": (0.80, 1.50), "d": (0.40, 0.60), "bh": (0.72, 1.00), "uh": (0.60, 1.15)},
    "arched_pediment": {"w": (0.80, 1.40), "d": (0.40, 0.58), "bh": (0.72, 0.98), "uh": (0.60, 1.10)},
}


@dataclass(frozen=True)
class Config:
    upper_front: UpperFront = "glass_hinged_doors"
    lower_front: LowerFront = "double_doors"
    crown_form: CrownForm = "moulded_cornice"
    back_treatment: BackTreatment = "plain_back"
    lower_unit_count: int = 2
    upper_shelf_count: int = 2
    carcass_width_m: float | None = None
    base_depth_m: float | None = None
    base_height_m: float | None = None
    upper_height_m: float | None = None
    cornice_step_m: float | None = None
    pediment_rise_m: float | None = None
    upper_swing_rad: float | None = None
    open_bay_reveal_m: float | None = None
    upper_slide_travel_m: float | None = None
    tambour_travel_m: float | None = None
    drop_front_rad: float | None = None
    lift_flap_rad: float | None = None
    lower_swing_rad: float | None = None
    lower_travel_ratio: float | None = None
    cubby_rib_t_m: float | None = None
    back_board_t_m: float | None = None
    plate_rail_t_m: float | None = None
    palette: int = 0
    name: str = "pictureX_0611_Hutch_Cabinet"


@dataclass(frozen=True)
class ResolvedConfig:
    upper_front: UpperFront
    lower_front: LowerFront
    crown_form: CrownForm
    back_treatment: BackTreatment
    lower_unit_count: int
    upper_shelf_count: int
    palette: int
    name: str
    carcass_width_m: float
    base_depth_m: float
    base_height_m: float
    upper_height_m: float
    cornice_step_m: float
    pediment_rise_m: float
    upper_swing_rad: float
    open_bay_reveal_m: float
    upper_slide_travel_m: float
    tambour_travel_m: float
    drop_front_rad: float
    lift_flap_rad: float
    lower_swing_rad: float
    lower_travel_ratio: float
    cubby_rib_t_m: float
    back_board_t_m: float
    plate_rail_t_m: float
    upper_width_m: float
    upper_depth_m: float
    base_lo_z_m: float
    base_hi_z_m: float
    deck_z_m: float
    upper_lo_z_m: float
    upper_hi_z_m: float
    base_front_y_m: float
    upper_front_y_m: float
    base_half_w_m: float
    upper_half_w_m: float
    upper_open_hi_z_m: float
    upper_unit_count: int


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v: float | None, d: float) -> float:
    return d if v is None else float(v)


def _upper_unit_count_for(front: str) -> int:
    if front == "open_shelves":
        return 0
    if front in ("glass_hinged_doors", "sliding_glass_doors"):
        return 2
    return 1


def config_from_seed(seed: int) -> Config:
    rng = random.Random(seed)
    crown: CrownForm = rng.choice(("moulded_cornice", "arched_pediment"))
    b = _CROWN_BOUNDS[crown]
    return Config(
        upper_front=rng.choice(
            ("glass_hinged_doors", "open_shelves", "sliding_glass_doors", "tambour_roll",
             "drop_front_desk", "lift_up_flap")
        ),
        lower_front=rng.choice(("double_doors", "drawer_bank", "wine_cubby_grid")),
        crown_form=crown,
        back_treatment=rng.choice(("plain_back", "plate_rack")),
        lower_unit_count=rng.choice((1, 2, 3, 4)),
        upper_shelf_count=rng.choice((1, 2, 3)),
        carcass_width_m=round(rng.uniform(*b["w"]), 3),
        base_depth_m=round(rng.uniform(*b["d"]), 3),
        base_height_m=round(rng.uniform(*b["bh"]), 3),
        upper_height_m=round(rng.uniform(*b["uh"]), 3),
        cornice_step_m=round(rng.uniform(0.020, 0.070), 4),
        pediment_rise_m=round(rng.uniform(0.050, 0.180), 3),
        upper_swing_rad=round(rng.uniform(1.30, 1.85), 3),
        open_bay_reveal_m=round(rng.uniform(0.010, 0.040), 4),
        upper_slide_travel_m=round(rng.uniform(0.14, 0.42), 3),
        tambour_travel_m=round(rng.uniform(0.16, 0.48), 3),
        drop_front_rad=round(rng.uniform(1.30, 1.60), 3),
        lift_flap_rad=round(rng.uniform(1.00, 1.60), 3),
        lower_swing_rad=round(rng.uniform(1.30, 1.90), 3),
        lower_travel_ratio=round(rng.uniform(0.34, 0.60), 3),
        cubby_rib_t_m=round(rng.uniform(0.010, 0.026), 4),
        back_board_t_m=round(rng.uniform(0.010, 0.024), 4),
        plate_rail_t_m=round(rng.uniform(0.010, 0.026), 4),
        palette=rng.randrange(len(_PALETTES)),
        name=f"pictureX_0611_Hutch_Cabinet_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    crown = config.crown_form
    b = _CROWN_BOUNDS[crown]
    width = _clamp(_pick(config.carcass_width_m, sum(b["w"]) / 2), *b["w"])
    base_d = _clamp(_pick(config.base_depth_m, sum(b["d"]) / 2), *b["d"])
    base_h = _clamp(_pick(config.base_height_m, sum(b["bh"]) / 2), *b["bh"])
    upper_h = _clamp(_pick(config.upper_height_m, sum(b["uh"]) / 2), *b["uh"])
    upper_w = width * 0.97
    upper_d = base_d * _UPPER_DEPTH_RATIO

    base_lo = _PLINTH_H
    base_hi = base_lo + base_h
    deck_z = base_hi
    upper_lo = deck_z + _DECK_T
    upper_hi = upper_lo + upper_h

    tambour_travel = _clamp(_pick(config.tambour_travel_m, 0.30), 0.16, 0.48)
    upper_clear = upper_hi - _TOP_T - upper_lo
    if config.upper_front == "tambour_roll":
        pocket = _clamp(tambour_travel + 0.010, 0.06, max(upper_clear - 0.18, 0.06))
    else:
        pocket = 0.0

    return ResolvedConfig(
        upper_front=config.upper_front,
        lower_front=config.lower_front,
        crown_form=crown,
        back_treatment=config.back_treatment,
        lower_unit_count=int(_clamp(int(config.lower_unit_count), 1, 4)),
        upper_shelf_count=int(_clamp(int(config.upper_shelf_count), 1, 3)),
        palette=int(config.palette) % len(_PALETTES),
        name=config.name,
        carcass_width_m=width,
        base_depth_m=base_d,
        base_height_m=base_h,
        upper_height_m=upper_h,
        cornice_step_m=_clamp(_pick(config.cornice_step_m, 0.040), 0.020, 0.070),
        pediment_rise_m=_clamp(_pick(config.pediment_rise_m, 0.110), 0.050, 0.180),
        upper_swing_rad=_clamp(_pick(config.upper_swing_rad, 1.60), 1.30, 1.85),
        open_bay_reveal_m=_clamp(_pick(config.open_bay_reveal_m, 0.022), 0.010, 0.040),
        upper_slide_travel_m=_clamp(_pick(config.upper_slide_travel_m, 0.26), 0.14, 0.42),
        tambour_travel_m=tambour_travel,
        drop_front_rad=_clamp(_pick(config.drop_front_rad, 1.45), 1.30, 1.60),
        lift_flap_rad=_clamp(_pick(config.lift_flap_rad, 1.30), 1.00, 1.60),
        lower_swing_rad=_clamp(_pick(config.lower_swing_rad, 1.62), 1.30, 1.90),
        lower_travel_ratio=_clamp(_pick(config.lower_travel_ratio, 0.46), 0.34, 0.60),
        cubby_rib_t_m=_clamp(_pick(config.cubby_rib_t_m, 0.016), 0.010, 0.026),
        back_board_t_m=_clamp(_pick(config.back_board_t_m, 0.016), 0.010, 0.024),
        plate_rail_t_m=_clamp(_pick(config.plate_rail_t_m, 0.016), 0.010, 0.026),
        upper_width_m=upper_w,
        upper_depth_m=upper_d,
        base_lo_z_m=base_lo,
        base_hi_z_m=base_hi,
        deck_z_m=deck_z,
        upper_lo_z_m=upper_lo,
        upper_hi_z_m=upper_hi,
        base_front_y_m=-base_d / 2.0,
        upper_front_y_m=-upper_d / 2.0,
        base_half_w_m=width / 2.0 - _WALL_T,
        upper_half_w_m=upper_w / 2.0 - _WALL_T,
        upper_open_hi_z_m=upper_hi - _TOP_T - pocket,
        upper_unit_count=_upper_unit_count_for(config.upper_front),
    )


# --------------------------------------------------------------------------- helpers
def _bx(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Box(size=(float(size[0]), float(size[1]), float(size[2]))),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material, name=name, material_class_id="wood.polished_varnished",
    )


def _cy(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=float(radius), length=float(length)),
        origin=Origin(xyz=(float(xyz[0]), float(xyz[1]), float(xyz[2])), rpy=rpy),
        material=material, name=name, material_class_id="metal.brass_polished",
    )


def _materials(model: ArticulatedObject, palette: int) -> dict[str, object]:
    table = _PALETTES[palette % len(_PALETTES)]
    return {k: model.material(f"hutch_{palette}_{k}", rgba=v) for k, v in table.items()}


def _axis_mate(*, provider_name, point, axis, radial, consumer_name, consumer_radius):
    provider = AxisInterface(name=provider_name, point=tuple(float(v) for v in point),
                             axis=axis, radial=radial, radius=_BARREL_R)
    consumer = AxisInterface(name=consumer_name, point=(0.0, 0.0, 0.0), axis=axis,
                             radial=radial, radius=consumer_radius)
    return mate_axes(provider, consumer, require_fit=True)


def _plane_mate(*, provider_name, provider_point, provider_extent, consumer_name, consumer_extent,
                normal=(0.0, -1.0, 0.0), tangent=(1.0, 0.0, 0.0)):
    provider = PlaneInterface(name=provider_name, point=tuple(float(v) for v in provider_point),
                              normal=normal, tangent_u=tangent, extent=provider_extent)
    consumer = PlaneInterface(name=consumer_name, point=(0.0, 0.0, 0.0),
                              normal=tuple(-v for v in normal), tangent_u=tangent,
                              extent=consumer_extent)
    return mate_planes(provider, consumer)


# --------------------------------------------------------------------------- crown_form
def _build_two_tier_case(carcass, r: ResolvedConfig, mats, tag: str) -> None:
    w, d = r.carcass_width_m, r.base_depth_m
    # plinth
    _bx(carcass, (w - 0.050, d - 0.040, _PLINTH_H + 0.006), (0.0, 0.018, (_PLINTH_H + 0.006) / 2),
        mats["dark"], f"{tag}__plinth")
    # base cabinet
    zc = (r.base_lo_z_m + r.base_hi_z_m) / 2.0
    base_h = r.base_hi_z_m - r.base_lo_z_m
    for i, sx in enumerate((-1.0, 1.0)):
        _bx(carcass, (_WALL_T, d, base_h), (sx * (w / 2 - _WALL_T / 2), 0.0, zc), mats["wood"],
            f"{tag}__base_side_{i}")
    _bx(carcass, (w, d, 0.020), (0.0, 0.0, r.base_lo_z_m + 0.010), mats["wood"], f"{tag}__base_floor")
    _bx(carcass, (w - 2 * _WALL_T + 0.006, _WALL_T, base_h), (0.0, d / 2 - _WALL_T / 2, zc),
        mats["dark"], f"{tag}__base_back")
    # deck between the tiers
    _bx(carcass, (w + 0.026, d + 0.016, _DECK_T), (0.0, 0.0, r.deck_z_m + _DECK_T / 2), mats["wood"],
        f"{tag}__deck")
    # upper case
    uw, ud = r.upper_width_m, r.upper_depth_m
    uzc = (r.upper_lo_z_m + r.upper_hi_z_m) / 2.0
    uh = r.upper_hi_z_m - r.upper_lo_z_m
    for i, sx in enumerate((-1.0, 1.0)):
        _bx(carcass, (_WALL_T, ud, uh), (sx * (uw / 2 - _WALL_T / 2), (d - ud) / 2, uzc),
            mats["wood"], f"{tag}__upper_side_{i}")
    _bx(carcass, (uw, ud, _TOP_T), (0.0, (d - ud) / 2, r.upper_hi_z_m - _TOP_T / 2), mats["wood"],
        f"{tag}__upper_top")


def _crown_form_moulded_cornice_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "crown_form__moulded_cornice"
    _build_two_tier_case(carcass, r, mats, tag)
    step = r.cornice_step_m
    uw, ud = r.upper_width_m, r.upper_depth_m
    cy = (r.base_depth_m - ud) / 2.0
    for i in range(3):
        grow = step * (i + 1) / 3.0
        _bx(carcass, (uw + 2 * grow, ud + 2 * grow, 0.018),
            (0.0, cy - grow / 2, r.upper_hi_z_m - 0.006 + i * 0.016), mats["wood"],
            f"{tag}__cornice_step_{i}")


def _crown_form_arched_pediment_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "crown_form__arched_pediment"
    _build_two_tier_case(carcass, r, mats, tag)
    rise = r.pediment_rise_m
    uw, ud = r.upper_width_m, r.upper_depth_m
    cy = (r.base_depth_m - ud) / 2.0
    _bx(carcass, (uw + 0.030, ud + 0.020, 0.020), (0.0, cy, r.upper_hi_z_m - 0.004), mats["wood"],
        f"{tag}__pediment_base")
    steps = 7
    for i in range(steps):
        t0 = (i + 0.5) / steps
        x = (-0.5 + t0) * uw * 0.92
        h = rise * math.sin(math.pi * t0)
        if h < 0.006:
            continue
        _bx(carcass, (uw * 0.92 / steps + 0.006, ud * 0.55, h + 0.010),
            (x, cy - ud * 0.20, r.upper_hi_z_m + 0.006 + h / 2 - 0.005), mats["wood"],
            f"{tag}__pediment_arc_{i}")


_CROWN_BUILDERS = {
    "moulded_cornice": _crown_form_moulded_cornice_build,
    "arched_pediment": _crown_form_arched_pediment_build,
}


# --------------------------------------------------------------------------- back_treatment
def _upper_shelf_levels(r: ResolvedConfig) -> list[float]:
    lo = r.upper_lo_z_m + _MIN_SHELF_GAP * 0.35
    hi = r.upper_open_hi_z_m - _MIN_SHELF_GAP * 0.35
    if hi <= lo:
        lo, hi = r.upper_lo_z_m, r.upper_open_hi_z_m
    return [lo + (i + 1) * (hi - lo) / (r.upper_shelf_count + 1) for i in range(r.upper_shelf_count)]


def _upper_shelves(carcass, r: ResolvedConfig, mats, tag: str) -> None:
    span = 2 * r.upper_half_w_m + 0.008
    y0 = r.upper_front_y_m + (r.base_depth_m - r.upper_depth_m) / 2.0 + 0.020
    y1 = (r.base_depth_m - r.upper_depth_m) / 2.0 + r.upper_depth_m / 2.0 - 0.004
    for i, z in enumerate(_upper_shelf_levels(r)):
        _bx(carcass, (span, max(y1 - y0, 0.06), _SHELF_T), (0.0, (y0 + y1) / 2.0, z), mats["wood"],
            f"{tag}__upper_shelf_{i}")


def _back_treatment_plain_back_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "back_treatment__plain_back"
    t = r.back_board_t_m
    cy = (r.base_depth_m - r.upper_depth_m) / 2.0 + r.upper_depth_m / 2.0 - t / 2.0
    _bx(carcass, (2 * r.upper_half_w_m + 0.010, t, r.upper_hi_z_m - r.upper_lo_z_m),
        (0.0, cy, (r.upper_lo_z_m + r.upper_hi_z_m) / 2.0), mats["dark"], f"{tag}__back_board")
    _upper_shelves(carcass, r, mats, tag)


def _back_treatment_plate_rack_build(carcass, r: ResolvedConfig, mats) -> None:
    tag = "back_treatment__plate_rack"
    t = r.plate_rail_t_m
    cy = (r.base_depth_m - r.upper_depth_m) / 2.0 + r.upper_depth_m / 2.0 - t / 2.0
    _bx(carcass, (2 * r.upper_half_w_m + 0.010, t, r.upper_hi_z_m - r.upper_lo_z_m),
        (0.0, cy, (r.upper_lo_z_m + r.upper_hi_z_m) / 2.0), mats["dark"], f"{tag}__back_board")
    _upper_shelves(carcass, r, mats, tag)
    span = 2 * r.upper_half_w_m
    for i, z in enumerate(_upper_shelf_levels(r)):
        _bx(carcass, (span, t + 0.006, 0.030), (0.0, cy - t / 2 - 0.004, z + 0.055), mats["wood"],
            f"{tag}__plate_rail_{i}")
        count = max(3, int(span / 0.14))
        for j in range(count):
            x = -span / 2 + span * (j + 0.5) / count
            _cy(carcass, t * 0.4, 0.070, (x, cy - t / 2 - 0.004, z + 0.055), mats["wood"],
                f"{tag}__plate_spindle_{i}_{j}")


_BACK_BUILDERS = {
    "plain_back": _back_treatment_plain_back_build,
    "plate_rack": _back_treatment_plate_rack_build,
}


# --------------------------------------------------------------------------- shared leaf parts
def _new_unit(model, r: ResolvedConfig, role: str, slot: str, candidate: str, index: int, mech: str):
    return model.part(
        f"{slot}__{candidate}__{role}_{index}",
        meta={"role": role, "slot": slot, "candidate": candidate, "index": index, "mechanism": mech},
    )


def _vertical_hinge(carcass, leaf, r, mats, hinge_x, hinge_y, zc, leaf_h, tag, index) -> None:
    for si, station in enumerate((-leaf_h * 0.34, leaf_h * 0.34)):
        _cy(carcass, _BARREL_R, 0.030, (hinge_x, hinge_y, zc + station), mats["metal"],
            f"{tag}__fixed_knuckle_{index}_{si}")
        _bx(carcass, (0.018, 0.030, 0.020), (hinge_x, hinge_y + 0.016, zc + station), mats["metal"],
            f"{tag}__knuckle_plate_{index}_{si}")
        for bi, off in enumerate((-0.022, 0.022)):
            _cy(leaf, _BARREL_R * 0.86, 0.022, (0.0, 0.0, station + off), mats["metal"],
                f"{tag}__barrel_{index}_{si}_{bi}")


def _hinge_strap(leaf, r, mats, sign, station_z, name) -> None:
    reach = _LEAF_SETBACK + 0.008
    _bx(leaf, (reach, min(_LEAF_T, 0.014), 0.016), (sign * reach / 2.0, 0.0, station_z),
        mats["metal"], name)


def _glazed_leaf(leaf, r, mats, sign, leaf_w, leaf_h, tag) -> None:
    s = _LEAF_SETBACK
    cx = sign * (s + leaf_w / 2.0)
    frame = min(0.040, leaf_w * 0.24, leaf_h * 0.24)
    _bx(leaf, (frame, _LEAF_T, leaf_h), (sign * (s + frame / 2), 0.0, 0.0), mats["wood"], f"{tag}__stile_outer")
    _bx(leaf, (frame, _LEAF_T, leaf_h), (sign * (s + leaf_w - frame / 2), 0.0, 0.0), mats["wood"], f"{tag}__stile_inner")
    fw = max(leaf_w - 2 * frame, leaf_w * 0.2)
    fh = max(leaf_h - 2 * frame, leaf_h * 0.2)
    _bx(leaf, (fw, _LEAF_T, frame), (cx, 0.0, leaf_h / 2 - frame / 2), mats["wood"], f"{tag}__rail_top")
    _bx(leaf, (fw, _LEAF_T, frame), (cx, 0.0, -leaf_h / 2 + frame / 2), mats["wood"], f"{tag}__rail_bottom")
    _bx(leaf, (fw + 0.006, 0.006, fh + 0.006), (cx, 0.0, 0.0), mats["glass"], f"{tag}__glass")
    for j in range(2):
        _bx(leaf, (0.010, 0.008, fh), (cx + (j - 0.5) * fw / 2.4, -_LEAF_T / 2 + 0.004, 0.0),
            mats["wood"], f"{tag}__muntin_v{j}")
    _bx(leaf, (fw, 0.008, 0.010), (cx, -_LEAF_T / 2 + 0.004, 0.0), mats["wood"], f"{tag}__muntin_h")


def _panelled_leaf(leaf, r, mats, sign, leaf_w, leaf_h, tag) -> None:
    s = _LEAF_SETBACK
    cx = sign * (s + leaf_w / 2.0)
    _bx(leaf, (leaf_w, _LEAF_T, leaf_h), (cx, 0.0, 0.0), mats["panel"], f"{tag}__leaf_panel")
    fw = max(leaf_w - 0.080, leaf_w * 0.35)
    fh = max(leaf_h - 0.090, leaf_h * 0.35)
    for label, (dx, dz, sx, sz) in {
        "moulding_top": (0.0, fh / 2, fw, 0.016),
        "moulding_bottom": (0.0, -fh / 2, fw, 0.016),
        "moulding_left": (-fw / 2, 0.0, 0.016, fh),
        "moulding_right": (fw / 2, 0.0, 0.016, fh),
    }.items():
        _bx(leaf, (sx, 0.010, sz), (cx + dx, -_LEAF_T / 2 - 0.003, dz), mats["wood"], f"{tag}__{label}")
    _cy(leaf, 0.013, 0.012, (sign * (s + leaf_w - 0.034), -_LEAF_T / 2 - 0.010, 0.0), mats["metal"],
        f"{tag}__knob", rpy=(math.pi / 2, 0, 0))


# --------------------------------------------------------------------------- upper_front
def _upper_leaf_zone(r: ResolvedConfig) -> tuple[float, float, float, float]:
    """(x0, x1, z0, z1) clear opening of the upper case."""

    return (-r.upper_half_w_m, r.upper_half_w_m, r.upper_lo_z_m + 0.010, r.upper_open_hi_z_m)


def _upper_front_glass_hinged_doors_build(model, carcass, r, mats) -> list[object]:
    tag = "upper_front__glass_hinged_doors"
    x0, x1, z0, z1 = _upper_leaf_zone(r)
    zc = (z0 + z1) / 2.0
    leaf_h = max(z1 - z0 - 0.010, 0.100)
    cell_w = (x1 - x0) / 2.0
    leaves = []
    for k in range(2):
        cell_x0 = x0 + k * cell_w
        hinge_left = k == 0
        sign = 1.0 if hinge_left else -1.0
        hinge_x = cell_x0 + _OUTER_REVEAL if hinge_left else cell_x0 + cell_w - _OUTER_REVEAL
        leaf_w = max(cell_w - _OUTER_REVEAL - _LEAF_SETBACK - _REVEAL, _MIN_LEAF_W)
        hinge_y = r.upper_front_y_m + (r.base_depth_m - r.upper_depth_m) / 2.0 - _LEAF_GAP - _LEAF_T / 2
        leaf = _new_unit(model, r, "upper_unit", "upper_front", "glass_hinged_doors", k, "vertical hinge")
        _glazed_leaf(leaf, r, mats, sign, leaf_w, leaf_h, tag)
        _vertical_hinge(carcass, leaf, r, mats, hinge_x, hinge_y, zc, leaf_h, tag, k)
        for si, station in enumerate((-leaf_h * 0.34, leaf_h * 0.34)):
            for bi, off in enumerate((-0.022, 0.022)):
                _hinge_strap(leaf, r, mats, sign, station + off, f"{tag}__strap_{k}_{si}_{bi}")
        _bx(carcass, (0.040, 0.020, z1 - z0 + 0.014),
            (hinge_x, hinge_y + 0.020, zc), mats["wood"], f"{tag}__hinge_mullion_{k}")
        mate = _axis_mate(provider_name=f"crown_form.upper_opening.hinge_{k}",
                          point=(hinge_x, hinge_y, zc), axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0),
                          consumer_name=f"upper_front.upper_mount_{k}", consumer_radius=_BARREL_R * 0.86)
        joint = f"{tag}__leaf_joint_{k}"
        lower, upper = (-r.upper_swing_rad, 0.0) if sign > 0 else (0.0, r.upper_swing_rad)
        model.articulation(joint, ArticulationType.REVOLUTE, parent=carcass, child=leaf,
                           origin=mate.origin, axis=mate.axis,
                           motion_limits=MotionLimits(effort=10.0, velocity=1.4, lower=lower, upper=upper),
                           meta={"positive_motion": "glazed leaf swings outward"})
        register_interface_mate(model, joint, mate)
        leaves.append(leaf)
    return leaves


def _upper_front_open_shelves_build(model, carcass, r, mats) -> list[object]:
    tag = "upper_front__open_shelves"
    x0, x1, z0, z1 = _upper_leaf_zone(r)
    reveal = r.open_bay_reveal_m
    cy = r.upper_front_y_m + (r.base_depth_m - r.upper_depth_m) / 2.0 + reveal / 2 + 0.004
    for i, sx in enumerate((-1.0, 1.0)):
        _bx(carcass, (0.026, reveal + 0.008, z1 - z0 + 0.020),
            (sx * (r.upper_half_w_m - 0.010), cy, (z0 + z1) / 2.0), mats["wood"],
            f"{tag}__bay_stile_{i}")
    _bx(carcass, (2 * r.upper_half_w_m + 0.010, reveal + 0.008, 0.030),
        (0.0, cy, z1 - 0.010), mats["wood"], f"{tag}__bay_head_rail")
    del x0, x1
    return []


def _upper_front_sliding_glass_doors_build(model, carcass, r, mats) -> list[object]:
    tag = "upper_front__sliding_glass_doors"
    x0, x1, z0, z1 = _upper_leaf_zone(r)
    zone_w = x1 - x0
    zc = (z0 + z1) / 2.0
    leaf_h = max(z1 - z0 - 0.034, 0.100)
    leaf_w = max(zone_w * 0.56 - r.upper_slide_travel_m * 0.22, 0.060)
    travel = max(min(r.upper_slide_travel_m, zone_w - leaf_w - 0.010), 0.012)
    base_y = r.upper_front_y_m + (r.base_depth_m - r.upper_depth_m) / 2.0
    leaves = []
    for k in range(2):
        rest_x0 = x0 if k == 0 else x1 - leaf_w
        slide_sign = 1.0 if k == 0 else -1.0
        cx = rest_x0 + leaf_w / 2.0
        plane_y = base_y - _LEAF_GAP - k * (_LEAF_T + 0.030)
        leaf = _new_unit(model, r, "upper_unit", "upper_front", "sliding_glass_doors", k, "bypass track")
        _glazed_leaf(leaf, r, mats, 1.0, leaf_w, leaf_h, tag)
        for j, dz in enumerate((leaf_h / 2 - 0.001, -leaf_h / 2 + 0.001)):
            _bx(leaf, (0.046, 0.016, 0.014), (_LEAF_SETBACK + leaf_w / 2, _LEAF_T / 2 + 0.002, dz),
                mats["metal"], f"{tag}__roller_{k}_{j}")
        track_back = base_y + 0.014
        track_front = plane_y - _LEAF_T - 0.006
        for side, z in ((0, z1 - 0.006), (1, z0 + 0.006)):
            _bx(carcass, (2 * r.upper_half_w_m + 0.026, max(track_back - track_front, 0.014), 0.016),
                (0.0, (track_back + track_front) / 2.0, z), mats["dark"], f"{tag}__track_{k}_{side}")
        mate = _plane_mate(provider_name=f"crown_form.upper_opening.track_{k}",
                           provider_point=(cx - _LEAF_SETBACK - leaf_w / 2, plane_y - _LEAF_T / 2, zc),
                           provider_extent=(zone_w, z1 - z0),
                           consumer_name=f"upper_front.upper_mount_{k}",
                           consumer_extent=(leaf_w, leaf_h))
        joint = f"{tag}__leaf_joint_{k}"
        lower, upper = (0.0, travel) if slide_sign > 0 else (-travel, 0.0)
        model.articulation(joint, ArticulationType.PRISMATIC, parent=carcass, child=leaf,
                           origin=mate.origin, axis=(1.0, 0.0, 0.0),
                           motion_limits=MotionLimits(effort=20.0, velocity=0.32, lower=lower, upper=upper),
                           meta={"positive_motion": "glazed leaf slides across the upper opening"})
        register_interface_mate(model, joint, mate)
        leaves.append(leaf)
    return leaves


def _upper_front_tambour_roll_build(model, carcass, r, mats) -> list[object]:
    tag = "upper_front__tambour_roll"
    x0, x1, z0, z1 = _upper_leaf_zone(r)
    zone_w = x1 - x0
    curtain_h = max(z1 - z0 - 0.010, 0.090)
    zc = (z0 + z1) / 2.0
    base_y = r.upper_front_y_m + (r.base_depth_m - r.upper_depth_m) / 2.0
    plane_y = base_y - _LEAF_GAP
    travel = r.tambour_travel_m
    curtain = _new_unit(model, r, "upper_unit", "upper_front", "tambour_roll", 0, "roll-up slat curtain")
    slats = max(6, int(curtain_h / 0.045))
    slat_h = curtain_h / slats
    for i in range(slats):
        _bx(curtain, (zone_w - 0.014, 0.014, slat_h * 0.86),
            (0.0, 0.0, -curtain_h / 2 + (i + 0.5) * slat_h), mats["wood"], f"{tag}__slat_{i}")
    for i, sx in enumerate((-1.0, 1.0)):
        _bx(curtain, (0.010, 0.018, curtain_h), (sx * (zone_w / 2 - 0.010), 0.0, 0.0), mats["dark"],
            f"{tag}__curtain_edge_{i}")
        ch_lo = z0 - 0.010
        ch_hi = r.upper_hi_z_m - _TOP_T
        _bx(carcass, (0.016, 0.026, max(ch_hi - ch_lo, 0.08)),
            (sx * (r.upper_half_w_m - 0.006), plane_y + 0.014, (ch_lo + ch_hi) / 2.0), mats["dark"],
            f"{tag}__guide_channel_{i}")
    mate = _plane_mate(provider_name="crown_form.upper_opening.tambour",
                       provider_point=(0.0, plane_y - 0.009, zc),
                       provider_extent=(zone_w, z1 - z0),
                       consumer_name="upper_front.upper_mount_0",
                       consumer_extent=(zone_w, curtain_h))
    joint = f"{tag}__curtain_joint"
    model.articulation(joint, ArticulationType.PRISMATIC, parent=carcass, child=curtain,
                       origin=mate.origin, axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=18.0, velocity=0.30, lower=0.0, upper=travel),
                       meta={"positive_motion": "slat curtain rolls up into the head pocket"})
    register_interface_mate(model, joint, mate)
    return [curtain]


def _flap_leaf(flap, r, mats, width, height, sign, tag) -> None:
    """Flap authored away from its pivot, set back so it clears the knuckles."""

    base = sign * (_LEAF_SETBACK + height / 2.0)
    _bx(flap, (width, _LEAF_T, height), (0.0, 0.0, base), mats["panel"], f"{tag}__flap_panel")
    fw = max(width - 0.090, width * 0.35)
    fh = max(height - 0.080, height * 0.35)
    for label, dz in (("band_top", fh / 2), ("band_bottom", -fh / 2)):
        _bx(flap, (fw, 0.010, 0.014), (0.0, -_LEAF_T / 2 - 0.003, base + dz), mats["wood"],
            f"{tag}__{label}")
    _cy(flap, 0.012, 0.014, (0.0, -_LEAF_T / 2 - 0.004, base + sign * height * 0.32), mats["metal"],
        f"{tag}__flap_knob", rpy=(math.pi / 2, 0, 0))


def _horizontal_flap(model, carcass, r, mats, tag, candidate, pivot_at_bottom: bool, angle: float):
    x0, x1, z0, z1 = _upper_leaf_zone(r)
    width = max((x1 - x0) - 0.016, 0.100)
    height = max(z1 - z0 - 0.016, 0.090)
    base_y = r.upper_front_y_m + (r.base_depth_m - r.upper_depth_m) / 2.0
    pivot_y = base_y - _LEAF_GAP - _LEAF_T / 2
    pivot_z = z0 + 0.010 if pivot_at_bottom else z1 - 0.010
    flap = _new_unit(model, r, "upper_unit", "upper_front", candidate, 0,
                     "bottom pivot fall front" if pivot_at_bottom else "top hinged lift flap")
    sign = 1.0 if pivot_at_bottom else -1.0
    _flap_leaf(flap, r, mats, width, height, sign, tag)
    stations = (-width * 0.34, width * 0.34)
    for si, station in enumerate(stations):
        _cy(carcass, _BARREL_R, 0.030, (station, pivot_y, pivot_z), mats["metal"],
            f"{tag}__fixed_knuckle_{si}", rpy=(0.0, math.pi / 2, 0.0))
        # the bracket sits on the far side of the pivot from the flap, so the
        # leaf never sweeps through it
        _bx(carcass, (0.020, 0.030, 0.018), (station, pivot_y + 0.016, pivot_z - sign * 0.013),
            mats["metal"], f"{tag}__knuckle_plate_{si}")
        for bi, off in enumerate((-0.022, 0.022)):
            _cy(flap, _BARREL_R * 0.86, 0.022, (station + off, 0.0, 0.0), mats["metal"],
                f"{tag}__barrel_{si}_{bi}", rpy=(0.0, math.pi / 2, 0.0))
            _bx(flap, (0.016, min(_LEAF_T, 0.014), _LEAF_SETBACK + 0.008),
                (station + off, 0.0, sign * (_LEAF_SETBACK + 0.008) / 2.0), mats["metal"],
                f"{tag}__strap_{si}_{bi}")
    # a real stay whose length follows the opening angle
    stay_len = max(height * math.sin(angle) * 0.55, 0.020)
    for si, station in enumerate(stations):
        # the stay is let into the knuckle bracket so it is carried by structure
        _bx(carcass, (0.012, 0.012, stay_len + 0.018),
            (station * 0.9, pivot_y + 0.026, pivot_z + sign * (stay_len - 0.018) / 2),
            mats["metal"], f"{tag}__stay_{si}")
    mate = _axis_mate(provider_name="crown_form.upper_opening.flap_axis",
                      point=(0.0, pivot_y, pivot_z), axis=(1.0, 0.0, 0.0), radial=(0.0, 0.0, 1.0),
                      consumer_name="upper_front.upper_mount_0", consumer_radius=_BARREL_R * 0.86)
    joint = f"{tag}__flap_joint"
    lower, upper = (0.0, angle) if pivot_at_bottom else (-angle, 0.0)
    model.articulation(joint, ArticulationType.REVOLUTE, parent=carcass, child=flap,
                       origin=mate.origin, axis=mate.axis,
                       motion_limits=MotionLimits(effort=14.0, velocity=1.2, lower=lower, upper=upper),
                       meta={"positive_motion": "flap rotates about the horizontal pivot"})
    register_interface_mate(model, joint, mate)
    return [flap]


def _upper_front_drop_front_desk_build(model, carcass, r, mats) -> list[object]:
    return _horizontal_flap(model, carcass, r, mats, "upper_front__drop_front_desk",
                            "drop_front_desk", True, r.drop_front_rad)


def _upper_front_lift_up_flap_build(model, carcass, r, mats) -> list[object]:
    return _horizontal_flap(model, carcass, r, mats, "upper_front__lift_up_flap",
                            "lift_up_flap", False, r.lift_flap_rad)


_UPPER_BUILDERS = {
    "glass_hinged_doors": _upper_front_glass_hinged_doors_build,
    "open_shelves": _upper_front_open_shelves_build,
    "sliding_glass_doors": _upper_front_sliding_glass_doors_build,
    "tambour_roll": _upper_front_tambour_roll_build,
    "drop_front_desk": _upper_front_drop_front_desk_build,
    "lift_up_flap": _upper_front_lift_up_flap_build,
}


# --------------------------------------------------------------------------- lower_front
def _base_zone(r: ResolvedConfig) -> tuple[float, float, float, float]:
    return (-r.base_half_w_m, r.base_half_w_m, r.base_lo_z_m + 0.024, r.base_hi_z_m - 0.010)


def _base_window(r: ResolvedConfig) -> tuple[float, float]:
    y_front = r.base_front_y_m + 0.012
    y_back = r.base_depth_m / 2.0 - _WALL_T
    return y_front, y_back


def _lower_front_double_doors_build(model, carcass, r, mats) -> list[object]:
    tag = "lower_front__double_doors"
    x0, x1, z0, z1 = _base_zone(r)
    n = r.lower_unit_count
    zc = (z0 + z1) / 2.0
    leaf_h = max(z1 - z0 - 0.010, 0.090)
    cell_w = (x1 - x0) / n
    hinge_y = r.base_front_y_m - _LEAF_GAP - _LEAF_T / 2
    leaves = []
    for k in range(n):
        cell_x0 = x0 + k * cell_w
        hinge_left = k < n / 2.0 or n == 1
        sign = 1.0 if hinge_left else -1.0
        hinge_x = cell_x0 + _OUTER_REVEAL if hinge_left else cell_x0 + cell_w - _OUTER_REVEAL
        leaf_w = max(cell_w - _OUTER_REVEAL - _LEAF_SETBACK - _REVEAL, _MIN_LEAF_W)
        has_neighbour = (k > 0) if hinge_left else (k < n - 1)
        limit = min(r.lower_swing_rad, math.pi / 2 - 0.03) if has_neighbour else r.lower_swing_rad
        leaf = _new_unit(model, r, "lower_unit", "lower_front", "double_doors", k, "vertical hinge")
        _panelled_leaf(leaf, r, mats, sign, leaf_w, leaf_h, tag)
        _vertical_hinge(carcass, leaf, r, mats, hinge_x, hinge_y, zc, leaf_h, tag, k)
        for si, station in enumerate((-leaf_h * 0.34, leaf_h * 0.34)):
            for bi, off in enumerate((-0.022, 0.022)):
                _hinge_strap(leaf, r, mats, sign, station + off, f"{tag}__strap_{k}_{si}_{bi}")
        _bx(carcass, (0.040, 0.020, z1 - z0 + 0.016), (hinge_x, hinge_y + 0.020, zc), mats["wood"],
            f"{tag}__hinge_mullion_{k}")
        mate = _axis_mate(provider_name=f"crown_form.base_opening.hinge_{k}",
                          point=(hinge_x, hinge_y, zc), axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0),
                          consumer_name=f"lower_front.lower_mount_{k}", consumer_radius=_BARREL_R * 0.86)
        joint = f"{tag}__leaf_joint_{k}"
        lower, upper = (-limit, 0.0) if sign > 0 else (0.0, limit)
        model.articulation(joint, ArticulationType.REVOLUTE, parent=carcass, child=leaf,
                           origin=mate.origin, axis=mate.axis,
                           motion_limits=MotionLimits(effort=12.0, velocity=1.4, lower=lower, upper=upper),
                           meta={"positive_motion": "base leaf swings outward"})
        register_interface_mate(model, joint, mate)
        leaves.append(leaf)
    return leaves


def _tray_unit(model, carcass, r, mats, tag, candidate, index, x0, x1, z0, z1, ribs: bool):
    y_front, y_back = _base_window(r)
    cell_w = x1 - x0
    cx = (x0 + x1) / 2.0
    front_h = max(z1 - z0, 0.030)
    tray_half = max(cell_w / 2.0 - _RAIL_W - _SIDE_CLEAR, 0.045)
    tray_w = 2 * tray_half
    box_depth = max(y_back - y_front, 0.140) + _TRAY_FRONT_REACH
    travel = min(box_depth * r.lower_travel_ratio, box_depth * 0.60)
    floor_z = z0 + 0.012
    box_h = max(min(front_h - 0.020, z1 - floor_z - 0.006), 0.022)
    box_cy = box_depth / 2.0 - _TRAY_FRONT_REACH

    unit = _new_unit(model, r, "lower_unit", "lower_front", candidate, index, "side runner slide")
    _bx(unit, (tray_w, box_depth, _TRAY_FLOOR_T), (0.0, box_cy, _TRAY_FLOOR_T / 2), mats["wood"],
        f"{tag}__tray_floor_{index}")
    for side, sign in enumerate((-1.0, 1.0)):
        _bx(unit, (_TRAY_WALL_T, box_depth, box_h), (sign * (tray_half - _TRAY_WALL_T / 2), box_cy, box_h / 2),
            mats["wood"], f"{tag}__tray_side_{index}_{side}")
        _bx(unit, (_RUNNER_W, box_depth, _RAIL_H),
            (sign * (tray_half + _RUNNER_W / 2 - _RUNNER_ENGAGE), box_cy, -0.001), mats["dark"],
            f"{tag}__tray_runner_{index}_{side}")
    _bx(unit, (tray_w, _TRAY_WALL_T, box_h), (0.0, box_depth - _TRAY_FRONT_REACH - _TRAY_WALL_T / 2, box_h / 2),
        mats["wood"], f"{tag}__tray_rear_{index}")
    if ribs:
        count = max(2, int(tray_w / 0.10))
        for j in range(count):
            x = -tray_half + tray_w * (j + 0.5) / count
            _bx(unit, (r.cubby_rib_t_m, box_depth * 0.86, box_h * 0.72),
                (x, box_cy, box_h * 0.36 + _TRAY_FLOOR_T), mats["wood"], f"{tag}__cradle_rib_{index}_{j}")
    front_y_local = r.base_front_y_m - _LEAF_GAP - _LEAF_T - (y_front)
    _bx(unit, (cell_w - 0.006, _LEAF_T, front_h - 0.004),
        (0.0, front_y_local + _LEAF_T / 2, (z0 + z1) / 2.0 - floor_z), mats["panel"],
        f"{tag}__unit_front_{index}")
    _cy(unit, 0.006, min(0.130, (cell_w - 0.006) * 0.36),
        (0.0, front_y_local - 0.004, (z0 + z1) / 2.0 - floor_z), mats["metal"],
        f"{tag}__pull_{index}", rpy=(0.0, math.pi / 2, 0.0))

    # runner rails on the carcass
    rail_y0 = y_front + 0.002
    rail_y1 = y_back + 0.004
    for side, x in ((0, x0), (1, x1)):
        direction = 1.0 if side == 0 else -1.0
        outer = max(r.base_half_w_m - abs(x), 0.0) + _RAIL_EMBED
        _bx(carcass, (_RAIL_W + outer, max(rail_y1 - rail_y0, 0.10), _RAIL_H),
            (x + direction * (_RAIL_W - outer) / 2.0, (rail_y0 + rail_y1) / 2.0,
             z0 + _RAIL_H / 2 - 0.002), mats["dark"], f"{tag}__runner_rail_{index}_{side}")
    mate = _plane_mate(provider_name=f"crown_form.base_opening.cell_{index}",
                       provider_point=(cx, y_front, floor_z),
                       provider_extent=(cell_w, z1 - z0),
                       consumer_name=f"lower_front.lower_mount_{index}",
                       consumer_extent=(tray_w, box_h))
    joint = f"{tag}__slide_{index}"
    model.articulation(joint, ArticulationType.PRISMATIC, parent=carcass, child=unit,
                       origin=mate.origin, axis=(0.0, -1.0, 0.0),
                       motion_limits=MotionLimits(effort=55.0, velocity=0.30, lower=0.0, upper=travel),
                       meta={"mechanism": "side runner pair riding on the carcass rails"})
    register_interface_mate(model, joint, mate)
    return unit


def _lower_front_drawer_bank_build(model, carcass, r, mats) -> list[object]:
    tag = "lower_front__drawer_bank"
    x0, x1, z0, z1 = _base_zone(r)
    n = r.lower_unit_count
    gap = _LEVEL_REVEAL
    band = (z1 - z0 - (n - 1) * gap) / n
    if band < _MIN_FRONT_H:
        gap = 0.002
        band = max((z1 - z0 - (n - 1) * gap) / n, 0.024)
    units = []
    z = z0
    for k in range(n):
        units.append(_tray_unit(model, carcass, r, mats, tag, "drawer_bank", k, x0, x1, z, z + band, False))
        if k > 0:
            _bx(carcass, (2 * r.base_half_w_m + 0.024, 0.10, 0.010), (0.0, 0.0, z - gap / 2),
                mats["dark"], f"{tag}__level_rail_{k}")
        z += band + gap
    return units


def _lower_front_wine_cubby_grid_build(model, carcass, r, mats) -> list[object]:
    tag = "lower_front__wine_cubby_grid"
    x0, x1, z0, z1 = _base_zone(r)
    n = r.lower_unit_count
    cell_w = (x1 - x0) / n
    units = []
    for k in range(n):
        cx0 = x0 + k * cell_w
        units.append(_tray_unit(model, carcass, r, mats, tag, "wine_cubby_grid", k,
                                cx0 + 0.004, cx0 + cell_w - 0.004, z0, z1, True))
        if k > 0:
            _bx(carcass, (r.cubby_rib_t_m + 0.008, 0.10, z1 - z0 + 0.012), (cx0, 0.0, (z0 + z1) / 2.0),
                mats["wood"], f"{tag}__cubby_divider_{k}")
    return units


_LOWER_BUILDERS = {
    "double_doors": _lower_front_double_doors_build,
    "drawer_bank": _lower_front_drawer_bank_build,
    "wine_cubby_grid": _lower_front_wine_cubby_grid_build,
}


# --------------------------------------------------------------------------- build
def build_pictureX_0611_Hutch_Cabinet(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r.palette)
    carcass = model.part("carcass", meta={"role": "carcass", "slot": "crown_form", "candidate": r.crown_form})
    _CROWN_BUILDERS[r.crown_form](carcass, r, mats)
    _BACK_BUILDERS[r.back_treatment](carcass, r, mats)
    _UPPER_BUILDERS[r.upper_front](model, carcass, r, mats)
    _LOWER_BUILDERS[r.lower_front](model, carcass, r, mats)
    carcass.inertial = None
    model.meta["slot_choices"] = (
        ("upper_front", r.upper_front),
        ("lower_front", r.lower_front),
        ("crown_form", r.crown_form),
        ("back_treatment", r.back_treatment),
        ("lower_unit_count", str(r.lower_unit_count)),
        ("upper_shelf_count", str(r.upper_shelf_count)),
    )
    return model


def build_seeded_pictureX_0611_Hutch_Cabinet(seed: int) -> ArticulatedObject:
    return build_pictureX_0611_Hutch_Cabinet(config_from_seed(seed))


def run_pictureX_0611_Hutch_Cabinet_tests(
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

    carcass = parts.get("carcass")
    visuals = [str(v.name) for v in carcass.visuals] if carcass is not None else []
    ctx.check(
        "category_anchor: one two-tier carcass",
        len(roles.get("carcass", [])) == 1
        and any("__base_side_" in v for v in visuals)
        and any("__upper_side_" in v for v in visuals)
        and any("__deck" in v for v in visuals),
        details=f"carcass={roles.get('carcass')} tiers={[v for v in visuals if 'side_' in v or 'deck' in v][:6]}",
    )

    moving = {
        j.child: j for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
    }
    lower = roles.get("lower_unit", [])
    ctx.check(
        "category_anchor: the hutch has a lower storage unit",
        len(lower) == r.lower_unit_count
        and all(name in moving and moving[name].parent == "carcass" for name in lower),
        details=f"lower={lower} expected={r.lower_unit_count}",
    )

    upper = roles.get("upper_unit", [])
    shelves = [v for v in visuals if "__upper_shelf_" in v]
    ctx.check(
        "category_anchor: the upper case has its own front or shelves",
        len(upper) == r.upper_unit_count and len(shelves) == r.upper_shelf_count,
        details=f"upper={upper} expected={r.upper_unit_count} shelves={len(shelves)}",
    )

    name = lower[0]
    joint = moving[name]
    rest = ctx.part_world_aabb(parts[name])
    limit = joint.motion_limits.upper or joint.motion_limits.lower or 0.0
    with ctx.pose({joint: limit * 0.8}):
        opened = ctx.part_world_aabb(parts[name])
    ctx.check(
        "lower unit opens forward",
        rest is not None and opened is not None and opened[0][1] < rest[0][1] - 0.015,
        details=f"rest={None if rest is None else round(rest[0][1], 4)} "
        f"open={None if opened is None else round(opened[0][1], 4)}",
    )

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    return ctx.report()


run_pictureX_0611_Hutch_Cabinet_tests.__test__ = False


TEMPLATE_CORNERS = (
    corner_case(
        "widest_cornice_tambour_over_four_cradles",
        {"upper_front": "tambour_roll", "lower_front": "wine_cubby_grid",
         "crown_form": "moulded_cornice", "back_treatment": "plate_rack",
         "lower_unit_count": 4, "upper_shelf_count": 3, "carcass_width_m": 1.50,
         "base_depth_m": 0.60, "base_height_m": 1.00, "upper_height_m": 1.15,
         "cornice_step_m": 0.070, "tambour_travel_m": 0.48, "cubby_rib_t_m": 0.026},
        reason="largest case with the deepest cornice, longest tambour stroke and most cradles",
    ),
    corner_case(
        "narrow_pediment_drop_front_single_door",
        {"upper_front": "drop_front_desk", "lower_front": "double_doors",
         "crown_form": "arched_pediment", "back_treatment": "plain_back",
         "lower_unit_count": 1, "upper_shelf_count": 1, "carcass_width_m": 0.80,
         "base_depth_m": 0.40, "base_height_m": 0.72, "upper_height_m": 0.60,
         "pediment_rise_m": 0.180, "drop_front_rad": 1.60, "lower_swing_rad": 1.90},
        reason="smallest case with the tallest pediment and a full fall front over one wide leaf",
    ),
    corner_case(
        "sliding_uppers_over_four_drawers",
        {"upper_front": "sliding_glass_doors", "lower_front": "drawer_bank",
         "crown_form": "moulded_cornice", "back_treatment": "plate_rack",
         "lower_unit_count": 4, "upper_shelf_count": 3, "carcass_width_m": 0.80,
         "base_depth_m": 0.40, "base_height_m": 0.72, "upper_height_m": 1.15,
         "upper_slide_travel_m": 0.42, "lower_travel_ratio": 0.60, "plate_rail_t_m": 0.026},
        reason="narrowest case with the longest bypass stroke over the deepest drawer stack",
    ),
    corner_case(
        "lift_flap_over_four_leaves",
        {"upper_front": "lift_up_flap", "lower_front": "double_doors",
         "crown_form": "arched_pediment", "back_treatment": "plain_back",
         "lower_unit_count": 4, "upper_shelf_count": 1, "carcass_width_m": 1.40,
         "base_depth_m": 0.58, "base_height_m": 0.98, "upper_height_m": 0.60,
         "lift_flap_rad": 1.60, "lower_swing_rad": 1.90, "back_board_t_m": 0.024},
        reason="shortest upper case at full lift over four interior-limited base leaves",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_pictureX_0611_Hutch_Cabinet",
    "build_seeded_pictureX_0611_Hutch_Cabinet",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_Hutch_Cabinet_tests",
]
