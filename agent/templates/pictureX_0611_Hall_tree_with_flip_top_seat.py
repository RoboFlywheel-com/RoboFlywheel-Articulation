# SPDX-License-Identifier: Apache-2.0

"""Self-contained entryway hall tree with a flip-top bench seat.

One rigid ``carcass`` root carries the base, both side cheeks, the
cabinet bottom, the rear seat ledgers and the tall tower back that rises
between the cheeks.  The bench slab is a separate ``flip_seat`` part hinged
REVOLUTE about +x on two strap/knuckle pairs at its rear edge, so the flip is
the fixed category motion.

``lower_build`` fills the carcass under the seat (a bank of prismatic drawers,
one hinged door over a fixed shelf, or a walled storage well) and
``upper_build`` treats the tower above it (open cubbies, a mirror panel, a hook
rail or an applied board frame).  ``case_dress`` is how the same case meets the
floor and the ceiling (stepped plinth under a two-piece crown, recessed toe kick
under one thin crown rail, or a flush base under a broad crown).  ``bay_count``
divides the face frame and the tower on the same pitch, so the two line up.

No source-replay import, no motion clamping, no whole-part overlap allowance.
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
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    multiplicity_slot,
    register_interface_mate,
)

LowerBuild = Literal["drawer_bank", "door_cabinet", "seat_bin"]
UpperBuild = Literal["open_cubbies", "mirror_panel", "hook_rail", "framed_board"]
CaseDress = Literal["stepped_plinth_crown", "toe_kick_rail", "flush_base_crown"]
PaletteStyle = Literal["white_oak", "dove_grey", "sage_green", "charcoal_walnut"]

LOWER_BUILDS: tuple[LowerBuild, ...] = ("drawer_bank", "door_cabinet", "seat_bin")
UPPER_BUILDS: tuple[UpperBuild, ...] = (
    "open_cubbies",
    "mirror_panel",
    "hook_rail",
    "framed_board",
)
CASE_DRESSES: tuple[CaseDress, ...] = (
    "stepped_plinth_crown",
    "toe_kick_rail",
    "flush_base_crown",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "white_oak",
    "dove_grey",
    "sage_green",
    "charcoal_walnut",
)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("lower_build", LOWER_BUILDS),
        component_slot("upper_build", UPPER_BUILDS),
        component_slot("case_dress", CASE_DRESSES),
        multiplicity_slot("bay_count", (2, 3, 4, 6), item_slot="lower_build"),
    )
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "white_oak": {
        "case": (0.93, 0.92, 0.89, 1.0),
        "trim": (0.86, 0.84, 0.80, 1.0),
        "seat": (0.62, 0.46, 0.30, 1.0),
        "metal": (0.18, 0.18, 0.19, 1.0),
        "glass": (0.78, 0.82, 0.84, 0.55),
        "shadow": (0.20, 0.22, 0.25, 1.0),
    },
    "dove_grey": {
        "case": (0.72, 0.74, 0.75, 1.0),
        "trim": (0.62, 0.64, 0.66, 1.0),
        "seat": (0.30, 0.26, 0.24, 1.0),
        "metal": (0.22, 0.23, 0.24, 1.0),
        "glass": (0.74, 0.80, 0.84, 0.55),
        "shadow": (0.16, 0.18, 0.21, 1.0),
    },
    "sage_green": {
        "case": (0.62, 0.68, 0.58, 1.0),
        "trim": (0.52, 0.58, 0.49, 1.0),
        "seat": (0.55, 0.40, 0.26, 1.0),
        "metal": (0.24, 0.25, 0.24, 1.0),
        "glass": (0.76, 0.81, 0.82, 0.55),
        "shadow": (0.18, 0.22, 0.18, 1.0),
    },
    "charcoal_walnut": {
        "case": (0.26, 0.27, 0.28, 1.0),
        "trim": (0.20, 0.21, 0.22, 1.0),
        "seat": (0.36, 0.24, 0.16, 1.0),
        "metal": (0.66, 0.67, 0.68, 1.0),
        "glass": (0.70, 0.76, 0.80, 0.55),
        "shadow": (0.12, 0.13, 0.14, 1.0),
    },
}

SIDE_T = 0.020  # side cheek thickness
BACK_T = 0.016  # back panel thickness
BOTTOM_T = 0.018  # cabinet bottom thickness
PLINTH_H = 0.070  # stepped plinth height
SEAT_T = 0.040  # bench slab thickness
LEDGER_D = 0.070  # rear seat ledger depth
FLIP = 1.30  # bench flip range
DOOR_SWING = 1.90  # cabinet door swing range
TOWER_FREE = 0.440  # tower stays clear of the flipped seat below this height
MOUNT = 0.0008  # intra-part embedment so one part stays one island


@dataclass(frozen=True)
class Config:
    lower_build: LowerBuild = "drawer_bank"
    upper_build: UpperBuild = "open_cubbies"
    case_dress: CaseDress = "stepped_plinth_crown"
    bay_count: int = 4
    carcass_width_m: float | None = None
    carcass_depth_m: float | None = None
    seat_height_m: float | None = None
    tower_height_m: float | None = None
    palette_style: PaletteStyle = "white_oak"
    name: str = "pictureX_0611_Hall_tree_with_flip_top_seat"


@dataclass(frozen=True)
class ResolvedConfig:
    lower_build: LowerBuild
    upper_build: UpperBuild
    case_dress: CaseDress
    bay_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    carcass_width_m: float
    carcass_depth_m: float
    seat_height_m: float
    tower_height_m: float
    inner_width_m: float
    bay_pitch_m: float
    opening_bottom_m: float
    opening_top_m: float
    hinge_axis_y_m: float
    hinge_axis_z_m: float
    tower_base_m: float
    crown_z_m: float
    drawer_count: int
    door_count: int
    drawer_travel_m: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x4A1B_C3D5)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        lower_build=choices["lower_build"],
        upper_build=choices["upper_build"],
        case_dress=choices["case_dress"],
        bay_count=choices["bay_count"],
        carcass_width_m=round(rng.uniform(0.62, 1.30), 4),
        carcass_depth_m=round(rng.uniform(0.32, 0.44), 4),
        seat_height_m=round(rng.uniform(0.42, 0.52), 4),
        tower_height_m=round(rng.uniform(0.90, 1.30), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"hall_tree_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "lower_build": config.lower_build,
            "upper_build": config.upper_build,
            "case_dress": config.case_dress,
            "bay_count": config.bay_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.carcass_width_m is not None and not 0.62 <= float(config.carcass_width_m) <= 1.30:
        raise ValueError("carcass_width_m must be in [0.62, 1.30]")
    if config.carcass_depth_m is not None and not 0.32 <= float(config.carcass_depth_m) <= 0.44:
        raise ValueError("carcass_depth_m must be in [0.32, 0.44]")
    if config.seat_height_m is not None and not 0.42 <= float(config.seat_height_m) <= 0.52:
        raise ValueError("seat_height_m must be in [0.42, 0.52]")
    if config.tower_height_m is not None and not 0.90 <= float(config.tower_height_m) <= 1.30:
        raise ValueError("tower_height_m must be in [0.90, 1.30]")

    width = (
        _clamp(config.carcass_width_m, 0.62, 1.30) if config.carcass_width_m is not None else 1.10
    )
    depth = (
        _clamp(config.carcass_depth_m, 0.32, 0.44) if config.carcass_depth_m is not None else 0.38
    )
    seat_h = _clamp(config.seat_height_m, 0.42, 0.52) if config.seat_height_m is not None else 0.46
    tower_h = (
        _clamp(config.tower_height_m, 0.90, 1.30) if config.tower_height_m is not None else 1.10
    )

    bays = int(config.bay_count)
    inner_w = width - 2.0 * SIDE_T
    pitch = inner_w / bays
    opening_bottom = PLINTH_H + BOTTOM_T
    opening_top = seat_h - SEAT_T - 0.006
    # The hinge sits above and behind the slab so the slab swings up and away
    # from the tower back instead of sweeping into it.
    hinge_y = depth * 0.5 - BACK_T - 0.012
    hinge_z = seat_h + 0.012
    drawers = bays if config.lower_build == "drawer_bank" else 0
    doors = 1 if config.lower_build == "door_cabinet" else 0
    travel = (depth - 0.070) * 0.62

    return ResolvedConfig(
        lower_build=config.lower_build,
        upper_build=config.upper_build,
        case_dress=config.case_dress,
        bay_count=bays,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        carcass_width_m=width,
        carcass_depth_m=depth,
        seat_height_m=seat_h,
        tower_height_m=tower_h,
        inner_width_m=inner_w,
        bay_pitch_m=pitch,
        opening_bottom_m=opening_bottom,
        opening_top_m=opening_top,
        hinge_axis_y_m=hinge_y,
        hinge_axis_z_m=hinge_z,
        tower_base_m=seat_h,
        crown_z_m=seat_h + tower_h,
        drawer_count=drawers,
        door_count=doors,
        drawer_travel_m=travel,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("lower_build", config.lower_build),
        ("upper_build", config.upper_build),
        ("case_dress", config.case_dress),
        ("bay_count", config.bay_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --- helpers ----------------------------------------------------------------
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"ht_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"ht_{r.palette_style}_{key}"
    return mats


def _joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    point,
    axis,
    radial,
    child_axis=(0.0, 1.0, 0.0),
    child_radial=(1.0, 0.0, 0.0),
    lower: float,
    upper: float,
    effort: float,
    velocity: float,
    kind: ArticulationType = ArticulationType.REVOLUTE,
    meta: dict | None = None,
) -> None:
    provider = AxisInterface(name=f"{name}__provider", point=point, axis=axis, radial=radial)
    consumer = AxisInterface(name=f"{name}__consumer", axis=child_axis, radial=child_radial)
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        kind,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(lower=lower, upper=upper, effort=effort, velocity=velocity),
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)


def _bay_center(r: ResolvedConfig, index: int) -> float:
    return -r.inner_width_m * 0.5 + (index + 0.5) * r.bay_pitch_m


# --- carcass ----------------------------------------------------------------
def _build_carcass(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    car = model.part("carcass", meta={"role": "carcass"})
    w = r.carcass_width_m
    d = r.carcass_depth_m
    inner = r.inner_width_m
    rear = d * 0.5 - BACK_T

    cheek_h = r.crown_z_m - PLINTH_H + 0.010
    for side, sx in enumerate((-1.0, 1.0)):
        car.visual(
            Box((SIDE_T, d, cheek_h)),
            origin=Origin(
                xyz=(
                    sx * (w - SIDE_T) * 0.5,
                    0.0,
                    PLINTH_H - 0.010 + cheek_h * 0.5,
                )
            ),
            material=mats["case"],
            name=f"side_cheek_{side}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    car.visual(
        Box((inner + 0.004, d - 0.016, BOTTOM_T)),
        origin=Origin(xyz=(0.0, 0.0, PLINTH_H + BOTTOM_T * 0.5 - 0.002)),
        material=mats["case"],
        name="cabinet_bottom", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    car.visual(
        Box((inner + 0.004, BACK_T, r.seat_height_m - PLINTH_H + 0.010)),
        origin=Origin(xyz=(0.0, rear + BACK_T * 0.5, (r.seat_height_m + PLINTH_H - 0.010) * 0.5)),
        material=mats["case"],
        name="lower_back", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    car.visual(
        Box((inner + 0.004, BACK_T, r.tower_height_m)),
        origin=Origin(xyz=(0.0, rear + BACK_T * 0.5, r.seat_height_m + r.tower_height_m * 0.5)),
        material=mats["case"],
        name="tower_back", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    car.visual(
        Box((inner + 0.004, LEDGER_D, 0.024)),
        origin=Origin(xyz=(0.0, rear + 0.004 - LEDGER_D * 0.5, r.seat_height_m - SEAT_T - 0.013)),
        material=mats["trim"],
        name="rear_seat_ledger", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    return car


def _hinge_stations(r: ResolvedConfig) -> tuple[float, float]:
    off = min(r.inner_width_m * 0.30, 0.22)
    return (-off, off)


def _build_seat(model: ArticulatedObject, car, r: ResolvedConfig, mats: dict[str, str]):
    d = r.carcass_depth_m
    hy = r.hinge_axis_y_m
    hz = r.hinge_axis_z_m
    seat = model.part("flip_seat", meta={"role": "flip_seat"})

    rear_edge = hy - 0.020
    front_edge = -d * 0.5 - 0.020
    slab_depth = rear_edge - front_edge
    seat.visual(
        Box((r.inner_width_m - 0.006, slab_depth, SEAT_T)),
        origin=Origin(
            xyz=(
                0.0,
                (rear_edge + front_edge) * 0.5 - hy,
                r.seat_height_m - SEAT_T * 0.5 - hz,
            )
        ),
        material=mats["seat"],
        name="bench_slab", material_class_id=("wood.oak" if r.palette_style in {"white_oak", "sage_green"} else "wood.walnut_dark"),
    )
    seat.visual(
        Box((r.inner_width_m - 0.030, slab_depth - 0.110, 0.012)),
        origin=Origin(
            xyz=(
                0.0,
                (rear_edge + front_edge) * 0.5 - 0.035 - hy,
                r.seat_height_m - SEAT_T - 0.004 - hz,
            )
        ),
        material=mats["trim"],
        name="seat_underframe", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    for station, hx in enumerate(_hinge_stations(r)):
        car.visual(
            Box((0.030, 0.030, 0.030)),
            origin=Origin(xyz=(hx, hy, hz)),
            material=mats["metal"],
            name=f"seat_hinge_knuckle_{station}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_oak", "dove_grey", "sage_green"} else "metal.stainless_matte"),
        )
        for strap, sx in enumerate((-1.0, 1.0)):
            seat.visual(
                Box((0.014, 0.028, 0.044)),
                origin=Origin(xyz=(hx + sx * 0.0225, -0.008, -0.014)),
                material=mats["metal"],
                name=f"seat_hinge_strap_{station}_{strap}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_oak", "dove_grey", "sage_green"} else "metal.stainless_matte"),
            )
    _joint(
        model,
        name="carcass_to_flip_seat",
        parent=car,
        child=seat,
        point=(0.0, hy, hz),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 1.0, 0.0),
        child_axis=(1.0, 0.0, 0.0),
        child_radial=(0.0, 1.0, 0.0),
        lower=-FLIP,
        upper=0.0,
        effort=30.0,
        velocity=1.5,
        meta={"positive_motion": "lowers the flipped bench top back onto its ledger"},
    )
    return seat


# --- case dress candidates --------------------------------------------------
def _case_dress_stepped_plinth_crown_build(car, r: ResolvedConfig, mats):
    """Broad plinth stepping out on all four sides under a two-piece crown."""
    w = r.carcass_width_m
    d = r.carcass_depth_m
    car.visual(
        Box((w, d - 0.020, PLINTH_H - 0.020)),
        origin=Origin(xyz=(0.0, 0.0, (PLINTH_H - 0.020) * 0.5)),
        material=mats["trim"],
        name="stepped_plinth_crown__plinth_base", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    car.visual(
        Box((w + 0.016, d - 0.004, 0.020)),
        origin=Origin(xyz=(0.0, 0.0, PLINTH_H - 0.010)),
        material=mats["trim"],
        name="stepped_plinth_crown__plinth_cap", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    car.visual(
        Box((w + 0.020, d * 0.45, 0.026)),
        origin=Origin(xyz=(0.0, d * 0.5 - d * 0.225, r.crown_z_m - 0.013)),
        material=mats["trim"],
        name="stepped_plinth_crown__crown_board", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    car.visual(
        Box((w + 0.044, d * 0.45 + 0.020, 0.014)),
        origin=Origin(xyz=(0.0, d * 0.5 - d * 0.225, r.crown_z_m + 0.003)),
        material=mats["trim"],
        name="stepped_plinth_crown__crown_top", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )


def _case_dress_toe_kick_rail_build(car, r: ResolvedConfig, mats):
    """Front kick board recessed under the case, one thin flush crown rail."""
    w = r.carcass_width_m
    d = r.carcass_depth_m
    car.visual(
        Box((w - 0.040, 0.035, PLINTH_H)),
        origin=Origin(xyz=(0.0, -d * 0.5 + 0.048, PLINTH_H * 0.5)),
        material=mats["shadow"],
        name="toe_kick_rail__toe_kick", material_class_id="wood.painted_clean",
    )
    for side, sx in enumerate((-1.0, 1.0)):
        car.visual(
            Box((0.030, d - 0.070, PLINTH_H)),
            origin=Origin(xyz=(sx * (w * 0.5 - 0.015), -0.010, PLINTH_H * 0.5)),
            material=mats["trim"],
            name=f"toe_kick_rail__base_rail_{side}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
        car.visual(
            Box((0.030, 0.026, r.seat_height_m - PLINTH_H - 0.060)),
            origin=Origin(
                xyz=(
                    sx * (w * 0.5 + 0.012),
                    -d * 0.5 + 0.005,
                    (r.seat_height_m + PLINTH_H) * 0.5 - 0.020,
                )
            ),
            material=mats["trim"],
            name=f"toe_kick_rail__front_stile_{side}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    car.visual(
        Box((w, d * 0.30, 0.040)),
        origin=Origin(xyz=(0.0, d * 0.5 - d * 0.150, r.crown_z_m - 0.014)),
        material=mats["trim"],
        name="toe_kick_rail__crown_top", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )


def _case_dress_flush_base_crown_build(car, r: ResolvedConfig, mats):
    """Base flush with the case face under a single broad deep crown."""
    w = r.carcass_width_m
    d = r.carcass_depth_m
    car.visual(
        Box((w, d, PLINTH_H)),
        origin=Origin(xyz=(0.0, 0.0, PLINTH_H * 0.5)),
        material=mats["case"],
        name="flush_base_crown__base_block", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    car.visual(
        Box((w + 0.030, d * 0.62, 0.038)),
        origin=Origin(xyz=(0.0, d * 0.5 - d * 0.310, r.crown_z_m - 0.011)),
        material=mats["trim"],
        name="flush_base_crown__crown_top", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    for side, sx in enumerate((-1.0, 1.0)):
        car.visual(
            Box((0.030, 0.020, r.tower_height_m - 0.090)),
            origin=Origin(
                xyz=(
                    sx * (w * 0.5 - 0.015),
                    -d * 0.5 - 0.008,
                    r.seat_height_m + r.tower_height_m * 0.5 - 0.030,
                )
            ),
            material=mats["trim"],
            name=f"flush_base_crown__side_stile_{side}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )


def _build_case_dress(car, r: ResolvedConfig, mats: dict[str, str]):
    return {
        "stepped_plinth_crown": _case_dress_stepped_plinth_crown_build,
        "toe_kick_rail": _case_dress_toe_kick_rail_build,
        "flush_base_crown": _case_dress_flush_base_crown_build,
    }[r.case_dress](car, r, mats)


# --- lower build candidates -------------------------------------------------
def _lower_build_drawer_bank_build(model: ArticulatedObject, car, r: ResolvedConfig, mats):
    """Face frame divided into bays, one prismatic drawer per bay."""
    d = r.carcass_depth_m
    inner = r.inner_width_m
    front = -d * 0.5
    op_lo = r.opening_bottom_m
    op_hi = r.opening_top_m
    op_h = op_hi - op_lo
    for rail, rz in ((0, op_lo + 0.010), (1, op_hi - 0.010)):
        car.visual(
            Box((inner + 0.004, 0.040, 0.020)),
            origin=Origin(xyz=(0.0, front + 0.020, rz)),
            material=mats["case"],
            name=f"drawer_bank__face_rail_{rail}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    for i in range(r.bay_count - 1):
        car.visual(
            Box((0.014, 0.040, op_h)),
            origin=Origin(
                xyz=(
                    -inner * 0.5 + (i + 1) * r.bay_pitch_m,
                    front + 0.020,
                    (op_lo + op_hi) * 0.5,
                )
            ),
            material=mats["case"],
            name=f"drawer_bank__face_stile_{i}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    runner_y0 = front + 0.030
    runner_y1 = d * 0.5 - 0.040
    for i in range(r.bay_count):
        car.visual(
            Box((r.bay_pitch_m - 0.030, runner_y1 - runner_y0, 0.023)),
            origin=Origin(
                xyz=(
                    _bay_center(r, i),
                    (runner_y0 + runner_y1) * 0.5,
                    op_lo + 0.011,
                )
            ),
            material=mats["trim"],
            name=f"drawer_bank__runner_{i}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    drawers = []
    tray_rear = d * 0.5 - 0.045
    tray_front = front - 0.004
    tray_depth = tray_rear - tray_front
    box_h = min(op_h - 0.055, 0.170)
    for i in range(r.bay_count):
        cx = _bay_center(r, i)
        drawer = model.part(
            f"lower_build__drawer_bank__drawer_{i}",
            meta={"role": "storage_drawer", "index": i},
        )
        drawer.visual(
            Box((r.bay_pitch_m - 0.006, 0.018, op_h - 0.006)),
            origin=Origin(xyz=(0.0, -0.022, 0.0)),
            material=mats["case"],
            name=f"lower_build__drawer_bank__drawer_front_{i}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
        drawer.visual(
            Box((r.bay_pitch_m * 0.42, 0.020, 0.016)),
            origin=Origin(xyz=(0.0, -0.039, 0.0)),
            material=mats["metal"],
            name=f"lower_build__drawer_bank__drawer_pull_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_oak", "dove_grey", "sage_green"} else "metal.stainless_matte"),
        )
        drawer.visual(
            Box((r.bay_pitch_m - 0.030, tray_depth, 0.012)),
            origin=Origin(
                xyz=(
                    0.0,
                    (tray_front + tray_rear) * 0.5 - front - 0.011,
                    -op_h * 0.5 + 0.029,
                )
            ),
            material=mats["trim"],
            name=f"lower_build__drawer_bank__tray_bottom_{i}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
        for wall, wx in enumerate((-1.0, 1.0)):
            drawer.visual(
                Box((0.010, tray_depth, box_h)),
                origin=Origin(
                    xyz=(
                        wx * (r.bay_pitch_m * 0.5 - 0.020),
                        (tray_front + tray_rear) * 0.5 - front - 0.011,
                        -op_h * 0.5 + 0.030 + box_h * 0.5,
                    )
                ),
                material=mats["trim"],
                name=f"lower_build__drawer_bank__tray_wall_{i}_{wall}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
            )
        drawer.visual(
            Box((r.bay_pitch_m - 0.030, 0.010, box_h)),
            origin=Origin(
                xyz=(
                    0.0,
                    tray_rear - 0.005 - front - 0.011,
                    -op_h * 0.5 + 0.030 + box_h * 0.5,
                )
            ),
            material=mats["trim"],
            name=f"lower_build__drawer_bank__tray_back_{i}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
        _joint(
            model,
            name=f"carcass_to_storage_drawer_{i}",
            parent=car,
            child=drawer,
            point=(cx, front + 0.011, (op_lo + op_hi) * 0.5),
            axis=(0.0, -1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            child_axis=(0.0, -1.0, 0.0),
            child_radial=(1.0, 0.0, 0.0),
            lower=0.0,
            upper=r.drawer_travel_m,
            effort=40.0,
            velocity=0.5,
            kind=ArticulationType.PRISMATIC,
            meta={"positive_motion": "pulls the drawer out of its bay"},
        )
        drawers.append(drawer)
    return drawers


def _lower_build_door_cabinet_build(model: ArticulatedObject, car, r: ResolvedConfig, mats):
    """One overlay door on a vertical axis over a fixed interior shelf."""
    d = r.carcass_depth_m
    inner = r.inner_width_m
    front = -d * 0.5
    op_lo = r.opening_bottom_m
    op_hi = r.opening_top_m
    op_h = op_hi - op_lo
    car.visual(
        Box((inner + 0.004, d - 0.070, 0.016)),
        origin=Origin(xyz=(0.0, front + 0.040 + (d - 0.070) * 0.5, (op_lo + op_hi) * 0.5)),
        material=mats["case"],
        name="door_cabinet__interior_shelf", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    for rail, rz in ((0, op_lo + 0.010), (1, op_hi - 0.010)):
        car.visual(
            Box((inner + 0.004, 0.034, 0.020)),
            origin=Origin(xyz=(0.0, front + 0.017, rz)),
            material=mats["case"],
            name=f"door_cabinet__case_rail_{rail}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    axis_x = -inner * 0.5 - 0.002
    axis_y = front - 0.012
    knuckle_z = (op_lo + 0.050, op_hi - 0.050)
    for i, kz in enumerate(knuckle_z):
        car.visual(
            Box((0.030, 0.024, 0.030)),
            origin=Origin(xyz=(axis_x, axis_y + 0.012, kz)),
            material=mats["metal"],
            name=f"door_cabinet__door_knuckle_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_oak", "dove_grey", "sage_green"} else "metal.stainless_matte"),
        )
    door = model.part("lower_build__door_cabinet__door", meta={"role": "cabinet_door", "index": 0})
    panel_w = inner + 0.004
    door.visual(
        Box((panel_w, 0.018, op_h - 0.004)),
        origin=Origin(xyz=(panel_w * 0.5, -0.011, 0.0)),
        material=mats["case"],
        name="lower_build__door_cabinet__door_panel", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    door.visual(
        Box((panel_w - 0.070, 0.008, op_h - 0.070)),
        origin=Origin(xyz=(panel_w * 0.5, -0.024, 0.0)),
        material=mats["trim"],
        name="lower_build__door_cabinet__door_relief", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    door.visual(
        Cylinder(radius=0.010, length=0.070),
        origin=Origin(xyz=(panel_w - 0.045, -0.026, 0.0)),
        material=mats["metal"],
        name="lower_build__door_cabinet__door_pull", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_oak", "dove_grey", "sage_green"} else "metal.stainless_matte"),
    )
    for i, kz in enumerate(knuckle_z):
        for strap, sz in enumerate((-1.0, 1.0)):
            door.visual(
                Box((0.020, 0.014, 0.024)),
                origin=Origin(xyz=(0.0, -0.004, kz - (op_lo + op_hi) * 0.5 + sz * 0.0270)),
                material=mats["metal"],
                name=f"lower_build__door_cabinet__door_strap_{i}_{strap}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_oak", "dove_grey", "sage_green"} else "metal.stainless_matte"),
            )
    _joint(
        model,
        name="carcass_to_cabinet_door",
        parent=car,
        child=door,
        point=(axis_x, axis_y, (op_lo + op_hi) * 0.5),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        child_axis=(0.0, 0.0, 1.0),
        child_radial=(1.0, 0.0, 0.0),
        lower=-DOOR_SWING,
        upper=0.0,
        effort=25.0,
        velocity=1.5,
        meta={"positive_motion": "swings the cabinet door shut"},
    )
    return [door]


def _lower_build_seat_bin_build(model: ArticulatedObject, car, r: ResolvedConfig, mats):
    """A walled storage well reached only by flipping the seat."""
    d = r.carcass_depth_m
    inner = r.inner_width_m
    front = -d * 0.5
    op_lo = r.opening_bottom_m
    op_hi = r.opening_top_m
    op_h = op_hi - op_lo
    floor_z = op_hi - 0.185
    car.visual(
        Box((inner + 0.004, d - 0.060, 0.014)),
        origin=Origin(xyz=(0.0, 0.0, floor_z)),
        material=mats["case"],
        name="seat_bin__well_floor", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    car.visual(
        Box((inner + 0.004, 0.020, op_h)),
        origin=Origin(xyz=(0.0, front + 0.010, (op_lo + op_hi) * 0.5)),
        material=mats["case"],
        name="seat_bin__front_panel", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    for wall, wx in enumerate((-1.0, 1.0)):
        car.visual(
            Box((0.014, d - 0.060, op_hi - floor_z)),
            origin=Origin(
                xyz=(
                    wx * (inner * 0.5 - 0.005),
                    0.0,
                    (floor_z + op_hi) * 0.5,
                )
            ),
            material=mats["trim"],
            name=f"seat_bin__well_wall_{wall}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    car.visual(
        Box((inner + 0.004, 0.014, op_hi - floor_z)),
        origin=Origin(xyz=(0.0, front + 0.032, (floor_z + op_hi) * 0.5)),
        material=mats["trim"],
        name="seat_bin__well_front", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    return []


def _build_lower(model: ArticulatedObject, car, r: ResolvedConfig, mats: dict[str, str]):
    return {
        "drawer_bank": _lower_build_drawer_bank_build,
        "door_cabinet": _lower_build_door_cabinet_build,
        "seat_bin": _lower_build_seat_bin_build,
    }[r.lower_build](model, car, r, mats)


# --- upper build candidates -------------------------------------------------
def _upper_build_open_cubbies_build(model: ArticulatedObject, car, r: ResolvedConfig, mats):
    """Cubby floor and top closed by dividers on the bay pitch."""
    d = r.carcass_depth_m
    inner = r.inner_width_m
    rear = d * 0.5 - BACK_T
    base = r.seat_height_m + TOWER_FREE
    head = r.crown_z_m - 0.040
    field = head - base
    depth = d * 0.60
    cy = rear - depth * 0.5 + 0.004
    cubby_h = min(field - 0.030, 0.320)
    for board, bz in ((0, base + 0.009), (1, base + 0.009 + cubby_h)):
        car.visual(
            Box((inner + 0.004, depth, 0.018)),
            origin=Origin(xyz=(0.0, cy, bz)),
            material=mats["case"],
            name=f"open_cubbies__cubby_board_{board}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    for i in range(r.bay_count - 1):
        car.visual(
            Box((0.014, depth, cubby_h)),
            origin=Origin(
                xyz=(
                    -inner * 0.5 + (i + 1) * r.bay_pitch_m,
                    cy,
                    base + 0.009 + cubby_h * 0.5,
                )
            ),
            material=mats["case"],
            name=f"open_cubbies__cubby_divider_{i}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    car.visual(
        Box((inner + 0.004, 0.020, 0.030)),
        origin=Origin(xyz=(0.0, cy - depth * 0.5 + 0.010, base + 0.009 - 0.020)),
        material=mats["trim"],
        name="open_cubbies__cubby_apron", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    return


def _upper_build_mirror_panel_build(model: ArticulatedObject, car, r: ResolvedConfig, mats):
    """Glass panel in an applied surround, divided by muntins."""
    d = r.carcass_depth_m
    inner = r.inner_width_m
    rear = d * 0.5 - BACK_T
    base = r.seat_height_m + TOWER_FREE
    head = r.crown_z_m - 0.040
    field = head - base
    mirror_h = min(field - 0.020, 0.620)
    mid = base + 0.010 + mirror_h * 0.5
    car.visual(
        Box((inner - 0.076, 0.006, mirror_h - 0.076)),
        origin=Origin(xyz=(0.0, rear - 0.003, mid)),
        material=mats["glass"],
        name="mirror_panel__mirror_glass", material_class_id="glass.mirror",
    )
    for stile, sx in enumerate((-1.0, 1.0)):
        car.visual(
            Box((0.040, 0.020, mirror_h)),
            origin=Origin(xyz=(sx * (inner * 0.5 - 0.020), rear - 0.008, mid)),
            material=mats["trim"],
            name=f"mirror_panel__surround_stile_{stile}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    for rail, rz in ((0, mid - mirror_h * 0.5 + 0.020), (1, mid + mirror_h * 0.5 - 0.020)):
        car.visual(
            Box((inner + 0.004, 0.020, 0.040)),
            origin=Origin(xyz=(0.0, rear - 0.008, rz)),
            material=mats["trim"],
            name=f"mirror_panel__surround_rail_{rail}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    for i in range(r.bay_count - 1):
        car.visual(
            Box((0.016, 0.014, mirror_h - 0.076)),
            origin=Origin(
                xyz=(
                    -inner * 0.5 + (i + 1) * r.bay_pitch_m,
                    rear - 0.005,
                    mid,
                )
            ),
            material=mats["trim"],
            name=f"mirror_panel__muntin_{i}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    return


def _upper_build_hook_rail_build(model: ArticulatedObject, car, r: ResolvedConfig, mats):
    """A hook rail across the open tower with one upward-facing hook per bay."""
    d = r.carcass_depth_m
    inner = r.inner_width_m
    rear = d * 0.5 - BACK_T
    base = r.seat_height_m + TOWER_FREE
    head = r.crown_z_m - 0.040
    field = head - base
    rail_z = base + min(field * 0.45, 0.160)
    car.visual(
        Box((inner + 0.004, 0.026, 0.080)),
        origin=Origin(xyz=(0.0, rear - 0.013, rail_z)),
        material=mats["case"],
        name="hook_rail__hook_rail", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    car.visual(
        Box((inner + 0.004, d * 0.34, 0.018)),
        origin=Origin(xyz=(0.0, rear - d * 0.17 + 0.004, head - 0.009)),
        material=mats["case"],
        name="hook_rail__parcel_shelf", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
    )
    for i in range(r.bay_count):
        hx = _bay_center(r, i)
        car.visual(
            Box((0.026, 0.012, 0.052)),
            origin=Origin(xyz=(hx, rear - 0.032, rail_z)),
            material=mats["metal"],
            name=f"hook_rail__hook_plate_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_oak", "dove_grey", "sage_green"} else "metal.stainless_matte"),
        )
        car.visual(
            Box((0.014, 0.048, 0.014)),
            origin=Origin(xyz=(hx, rear - 0.058, rail_z - 0.019)),
            material=mats["metal"],
            name=f"hook_rail__hook_arm_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_oak", "dove_grey", "sage_green"} else "metal.stainless_matte"),
        )
        car.visual(
            Box((0.014, 0.014, 0.030)),
            origin=Origin(xyz=(hx, rear - 0.076, rail_z - 0.009)),
            material=mats["metal"],
            name=f"hook_rail__hook_prong_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"white_oak", "dove_grey", "sage_green"} else "metal.stainless_matte"),
        )
    return


def _upper_build_framed_board_build(model: ArticulatedObject, car, r: ResolvedConfig, mats):
    """Applied stile-and-rail frame with one recessed field per bay."""
    d = r.carcass_depth_m
    inner = r.inner_width_m
    rear = d * 0.5 - BACK_T
    base = r.seat_height_m + TOWER_FREE
    head = r.crown_z_m - 0.040
    field = head - base
    for rail, rz in ((0, base + 0.026), (1, head - 0.026)):
        car.visual(
            Box((inner + 0.004, 0.018, 0.052)),
            origin=Origin(xyz=(0.0, rear - 0.009, rz)),
            material=mats["trim"],
            name=f"framed_board__frame_rail_{rail}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    for i in range(r.bay_count + 1):
        car.visual(
            Box((0.034, 0.018, field)),
            origin=Origin(
                xyz=(
                    -inner * 0.5 + i * r.bay_pitch_m,
                    rear - 0.009,
                    base + field * 0.5,
                )
            ),
            material=mats["trim"],
            name=f"framed_board__frame_stile_{i}", material_class_id=("wood.painted_clean" if r.palette_style in {"dove_grey", "sage_green", "charcoal_walnut"} else "wood.oak"),
        )
    for i in range(r.bay_count):
        car.visual(
            Box((r.bay_pitch_m - 0.044, 0.008, field - 0.072)),
            origin=Origin(xyz=(_bay_center(r, i), rear - 0.004, base + field * 0.5)),
            material=mats["shadow"],
            name=f"framed_board__recessed_field_{i}", material_class_id="wood.painted_clean",
        )


def _build_upper(model: ArticulatedObject, car, r: ResolvedConfig, mats: dict[str, str]):
    return {
        "open_cubbies": _upper_build_open_cubbies_build,
        "mirror_panel": _upper_build_mirror_panel_build,
        "hook_rail": _upper_build_hook_rail_build,
        "framed_board": _upper_build_framed_board_build,
    }[r.upper_build](model, car, r, mats)


# --- assembly ---------------------------------------------------------------
def build_picturex_0611_hall_tree_with_flip_top_seat(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Hall_tree_with_flip_top_seat",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "flip-top bench under a tall hall-tree tower",
        },
    )
    mats = _materials(model, r)
    car = _build_carcass(model, r, mats)
    _build_case_dress(car, r, mats)
    _build_seat(model, car, r, mats)
    _build_lower(model, car, r, mats)
    _build_upper(model, car, r, mats)

    poses: list[dict[str, float]] = [{"carcass_to_flip_seat": 0.0}, {"carcass_to_flip_seat": -FLIP}]
    if r.drawer_count:
        poses.append(
            {f"carcass_to_storage_drawer_{i}": r.drawer_travel_m for i in range(r.drawer_count)}
        )
    if r.door_count:
        poses.append({"carcass_to_cabinet_door": -DOOR_SWING})
    model.meta["risk_poses"] = tuple(poses)
    return model


def build_seeded_picturex_0611_hall_tree_with_flip_top_seat(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_hall_tree_with_flip_top_seat(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_hall_tree_with_flip_top_seat_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    carcasses = _parts_by_role(model, "carcass")
    seats = _parts_by_role(model, "flip_seat")
    drawers = _parts_by_role(model, "storage_drawer")
    doors = _parts_by_role(model, "cabinet_door")
    joints = {j.name: j for j in model.articulations}
    flip = joints.get("carcass_to_flip_seat")

    ctx.check(
        "category_anchor: the bench top flips on its rear edge",
        len(carcasses) == 1
        and len(seats) == 1
        and flip is not None
        and flip.articulation_type == ArticulationType.REVOLUTE
        and abs(abs(flip.axis[0]) - 1.0) < 1e-6
        and flip.motion_limits.lower < -1.0
        and abs(flip.motion_limits.upper) < 1e-9,
        details=(
            f"carcass={len(carcasses)} seat={len(seats)} "
            f"flip={None if flip is None else (flip.axis, flip.motion_limits.lower)}"
        ),
    )

    visual_names = [v.name for p in model.parts for v in p.visuals]
    car = carcasses[0]
    ledger = ctx.part_element_world_aabb(car, elem="rear_seat_ledger")
    slab = ctx.part_element_world_aabb(seats[0], elem="bench_slab")
    crown = ctx.part_element_world_aabb(car, elem=f"{r.case_dress}__crown_top")
    ctx.check(
        "category_anchor: the tower stands on the carcass above the seat",
        ledger is not None
        and slab is not None
        and crown is not None
        and ledger[1][2] <= slab[0][2] + 1e-6
        and crown[0][2] > slab[1][2] + 0.60
        and "tower_back" in visual_names,
        details=(
            f"ledger_top={None if ledger is None else round(ledger[1][2], 4)} "
            f"slab_bottom={None if slab is None else round(slab[0][2], 4)} "
            f"crown={None if crown is None else round(crown[0][2], 4)}"
        ),
    )

    lower_marker = {
        "drawer_bank": "drawer_bank__face_rail_0",
        "door_cabinet": "door_cabinet__interior_shelf",
        "seat_bin": "seat_bin__well_floor",
    }[r.lower_build]
    ctx.check(
        "category_anchor: lower_build identity",
        lower_marker in visual_names
        and len(drawers) == r.drawer_count
        and len(doors) == r.door_count,
        details=(f"lower_build={r.lower_build} drawers={len(drawers)} doors={len(doors)}"),
    )

    case_marker = {
        "stepped_plinth_crown": "stepped_plinth_crown__plinth_cap",
        "toe_kick_rail": "toe_kick_rail__toe_kick",
        "flush_base_crown": "flush_base_crown__base_block",
    }[r.case_dress]
    ctx.check(
        "category_anchor: case_dress identity",
        case_marker in visual_names and f"{r.case_dress}__crown_top" in visual_names,
        details=f"case_dress={r.case_dress}",
    )

    upper_marker = {
        "open_cubbies": "open_cubbies__cubby_board_0",
        "mirror_panel": "mirror_panel__mirror_glass",
        "hook_rail": "hook_rail__hook_rail",
        "framed_board": "framed_board__frame_rail_0",
    }[r.upper_build]
    ctx.check(
        "category_anchor: upper_build identity",
        upper_marker in visual_names,
        details=f"upper_build={r.upper_build}",
    )

    if r.lower_build == "drawer_bank":
        slides = [joints.get(f"carcass_to_storage_drawer_{i}") for i in range(r.bay_count)]
        ctx.check(
            "every bay carries one prismatic drawer that clears the face frame",
            all(s is not None and s.articulation_type == ArticulationType.PRISMATIC for s in slides)
            and r.drawer_travel_m > 0.14
            and r.bay_pitch_m > 0.090,
            details=(
                f"bays={r.bay_count} pitch={round(r.bay_pitch_m, 4)} "
                f"travel={round(r.drawer_travel_m, 4)}"
            ),
        )
        stiles = [
            ctx.part_element_world_aabb(car, elem=f"drawer_bank__face_stile_{i}")
            for i in range(r.bay_count - 1)
        ]
        fronts = [
            ctx.part_element_world_aabb(d, elem=f"lower_build__drawer_bank__drawer_front_{i}")
            for i, d in enumerate(drawers)
        ]
        ctx.check(
            "the drawer fronts sit proud of the face frame in every bay",
            all(s is not None for s in stiles)
            and all(f is not None for f in fronts)
            and all(f[1][1] < min(s[0][1] for s in stiles) for f in fronts)
            if stiles
            else all(f is not None for f in fronts),
            details=f"stiles={len(stiles)} fronts={len(fronts)}",
        )
    elif r.lower_build == "door_cabinet":
        door_joint = joints.get("carcass_to_cabinet_door")
        ctx.check(
            "the cabinet door swings on a vertical axis at one side",
            door_joint is not None
            and door_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(abs(door_joint.axis[2]) - 1.0) < 1e-6
            and door_joint.motion_limits.lower < -1.5,
            details=f"door={None if door_joint is None else door_joint.axis}",
        )
    else:
        floor = ctx.part_element_world_aabb(car, elem="seat_bin__well_floor")
        ctx.check(
            "the storage well sits under the seat with walls on both sides",
            floor is not None
            and slab is not None
            and floor[1][2] < slab[0][2] - 0.050
            and "seat_bin__well_wall_0" in visual_names
            and "seat_bin__well_wall_1" in visual_names,
            details=f"floor_top={None if floor is None else round(floor[1][2], 4)}",
        )

    ctx.check(
        "the flipped seat clears every tower feature",
        r.seat_height_m
        + 0.012
        + (r.hinge_axis_y_m - 0.020 + r.carcass_depth_m * 0.5 + 0.020) * math.sin(FLIP)
        < r.seat_height_m + TOWER_FREE,
        details=(
            f"reach={round((r.hinge_axis_y_m - 0.020 + r.carcass_depth_m * 0.5 + 0.020) * math.sin(FLIP), 4)} "
            f"free={TOWER_FREE}"
        ),
    )
    ctx.check(
        "the tower has room for its treatment above the free zone",
        r.crown_z_m - 0.040 - (r.seat_height_m + TOWER_FREE) > 0.400,
        details=f"field={round(r.crown_z_m - 0.040 - r.seat_height_m - TOWER_FREE, 4)}",
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "narrowest_two_bay_door_mirror",
        {
            "lower_build": "door_cabinet",
            "upper_build": "mirror_panel",
            "case_dress": "toe_kick_rail",
            "bay_count": 2,
            "carcass_width_m": 0.62,
            "carcass_depth_m": 0.32,
            "seat_height_m": 0.42,
            "tower_height_m": 0.90,
        },
        reason="narrowest shallowest case with the lowest seat and shortest tower",
    ),
    corner_case(
        "widest_six_bay_drawers_cubbies",
        {
            "lower_build": "drawer_bank",
            "upper_build": "open_cubbies",
            "case_dress": "stepped_plinth_crown",
            "bay_count": 6,
            "carcass_width_m": 1.30,
            "carcass_depth_m": 0.44,
            "seat_height_m": 0.52,
            "tower_height_m": 1.30,
        },
        reason="widest deepest case with six drawer bays and six cubbies",
    ),
    corner_case(
        "narrow_six_bay_hooks",
        {
            "lower_build": "seat_bin",
            "upper_build": "hook_rail",
            "case_dress": "flush_base_crown",
            "bay_count": 6,
            "carcass_width_m": 0.62,
            "carcass_depth_m": 0.44,
            "seat_height_m": 0.52,
            "tower_height_m": 0.90,
        },
        reason="tightest bay pitch: six hooks across the narrowest tower",
    ),
    corner_case(
        "wide_two_bay_framed_board",
        {
            "lower_build": "drawer_bank",
            "upper_build": "framed_board",
            "case_dress": "toe_kick_rail",
            "bay_count": 2,
            "carcass_width_m": 1.30,
            "carcass_depth_m": 0.32,
            "seat_height_m": 0.42,
            "tower_height_m": 1.30,
        },
        reason="widest bays on the shallowest carcass under the tallest tower",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_picturex_0611_hall_tree_with_flip_top_seat",
    "build_seeded_picturex_0611_hall_tree_with_flip_top_seat",
    "run_picturex_0611_hall_tree_with_flip_top_seat_tests",
]
