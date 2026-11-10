# SPDX-License-Identifier: Apache-2.0

"""Self-contained four-wheel golf cart.

One rigid ``chassis`` root carries the body, floor, roof posts, canopy, battery
bay and both axles.  Each front wheel spins CONTINUOUS on its own
``steer_knuckle`` and each knuckle turns REVOLUTE (+z) on the chassis; the rear
wheels spin CONTINUOUS straight off the chassis, so the steered-front /
driven-rear layout is fixed.

``screen_build`` changes the folding windshield, ``seat_build`` the cushions
over the battery bay (repeated ``row_count`` times), ``steer_build`` the driver
control that turns both knuckles and ``bed_build`` the cargo deck, whose length
is derived from ``row_count`` so a second row always fits.  Every hinged
cushion faces forward; ``rear_facing`` adds a back-to-back bench behind the
last row instead of turning the driver around.

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

ScreenBuild = Literal["split_fold", "center_fold", "full_width"]
CanopyBuild = Literal["cowl_post_canopy", "a_post_canopy"]
SeatBuild = Literal["bench", "bucket_pair", "rear_facing", "rear_deck_row"]
SteerBuild = Literal["wheel_column", "tiller"]
BedBuild = Literal["tailgate", "flatbed"]
PaletteStyle = Literal["white_cart", "beige_cart", "green_cart", "charcoal_cart"]

SCREEN_BUILDS: tuple[ScreenBuild, ...] = ("split_fold", "center_fold", "full_width")
CANOPY_BUILDS: tuple[CanopyBuild, ...] = ("cowl_post_canopy", "a_post_canopy")
SEAT_BUILDS: tuple[SeatBuild, ...] = ("bench", "bucket_pair", "rear_facing", "rear_deck_row")
STEER_BUILDS: tuple[SteerBuild, ...] = ("wheel_column", "tiller")
BED_BUILDS: tuple[BedBuild, ...] = ("tailgate", "flatbed")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "white_cart",
    "beige_cart",
    "green_cart",
    "charcoal_cart",
)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("screen_build", SCREEN_BUILDS),
        component_slot("canopy_build", CANOPY_BUILDS),
        component_slot("seat_build", SEAT_BUILDS),
        component_slot("steer_build", STEER_BUILDS),
        component_slot("bed_build", BED_BUILDS),
        multiplicity_slot("row_count", (1, 2), item_slot="seat_build"),
    )
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "white_cart": {
        "body": (0.92, 0.92, 0.90, 1.0),
        "trim": (0.72, 0.73, 0.72, 1.0),
        "seat": (0.28, 0.30, 0.34, 1.0),
        "glass": (0.72, 0.80, 0.84, 0.55),
        "tyre": (0.09, 0.09, 0.10, 1.0),
        "rim": (0.78, 0.79, 0.80, 1.0),
        "metal": (0.42, 0.43, 0.45, 1.0),
    },
    "beige_cart": {
        "body": (0.86, 0.80, 0.66, 1.0),
        "trim": (0.64, 0.58, 0.46, 1.0),
        "seat": (0.42, 0.34, 0.24, 1.0),
        "glass": (0.74, 0.80, 0.82, 0.55),
        "tyre": (0.10, 0.10, 0.10, 1.0),
        "rim": (0.74, 0.72, 0.68, 1.0),
        "metal": (0.46, 0.45, 0.42, 1.0),
    },
    "green_cart": {
        "body": (0.20, 0.42, 0.28, 1.0),
        "trim": (0.14, 0.30, 0.20, 1.0),
        "seat": (0.80, 0.78, 0.72, 1.0),
        "glass": (0.70, 0.78, 0.80, 0.55),
        "tyre": (0.08, 0.08, 0.09, 1.0),
        "rim": (0.80, 0.80, 0.78, 1.0),
        "metal": (0.38, 0.40, 0.38, 1.0),
    },
    "charcoal_cart": {
        "body": (0.24, 0.25, 0.26, 1.0),
        "trim": (0.16, 0.17, 0.18, 1.0),
        "seat": (0.62, 0.14, 0.14, 1.0),
        "glass": (0.62, 0.68, 0.72, 0.55),
        "tyre": (0.07, 0.07, 0.08, 1.0),
        "rim": (0.60, 0.61, 0.62, 1.0),
        "metal": (0.52, 0.53, 0.55, 1.0),
    },
}

FLOOR_CLEARANCE = 0.055  # floor above the wheel centre height
TYRE_W = 0.110  # tyre width
KNUCKLE_ARM = 0.110  # knuckle offset from the steer axis to the hub
STEER_LIMIT = 0.35  # knuckle steer range each way
SEAT_LIFT = 0.95  # seat cushion hinge range
SCREEN_FOLD = 1.30  # windshield leaf fold range
GATE_DROP = 1.45  # tailgate drop range
MOUNT = 0.0008  # intra-part embedment so one part stays one island


@dataclass(frozen=True)
class Config:
    screen_build: ScreenBuild = "split_fold"
    canopy_build: CanopyBuild = "cowl_post_canopy"
    seat_build: SeatBuild = "bench"
    steer_build: SteerBuild = "wheel_column"
    bed_build: BedBuild = "tailgate"
    row_count: int = 1
    wheelbase_m: float | None = None
    track_width_m: float | None = None
    wheel_radius_m: float | None = None
    palette_style: PaletteStyle = "white_cart"
    name: str = "pictureX_0611_Golf_cart"


@dataclass(frozen=True)
class ResolvedConfig:
    screen_build: ScreenBuild
    canopy_build: CanopyBuild
    seat_build: SeatBuild
    steer_build: SteerBuild
    bed_build: BedBuild
    row_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    wheelbase_m: float
    track_width_m: float
    wheel_radius_m: float
    floor_height_m: float
    body_width_m: float
    seat_station_m: float
    seat_pitch_m: float
    bed_length_m: float
    bed_start_m: float
    roof_height_m: float
    cowl_x_m: float
    seat_total: int
    screen_leaf_count: int
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x0F77_5527)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        screen_build=choices["screen_build"],
        canopy_build=choices["canopy_build"],
        seat_build=choices["seat_build"],
        steer_build=choices["steer_build"],
        bed_build=choices["bed_build"],
        row_count=choices["row_count"],
        wheelbase_m=round(rng.uniform(1.60, 2.10), 4),
        track_width_m=round(rng.uniform(0.86, 1.16), 4),
        wheel_radius_m=round(rng.uniform(0.19, 0.27), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"golf_cart_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "screen_build": config.screen_build,
            "canopy_build": config.canopy_build,
            "seat_build": config.seat_build,
            "steer_build": config.steer_build,
            "bed_build": config.bed_build,
            "row_count": config.row_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.wheelbase_m is not None and not 1.60 <= float(config.wheelbase_m) <= 2.10:
        raise ValueError("wheelbase_m must be in [1.60, 2.10]")
    if config.track_width_m is not None and not 0.86 <= float(config.track_width_m) <= 1.16:
        raise ValueError("track_width_m must be in [0.86, 1.16]")
    if config.wheel_radius_m is not None and not 0.19 <= float(config.wheel_radius_m) <= 0.27:
        raise ValueError("wheel_radius_m must be in [0.19, 0.27]")

    wb = _clamp(config.wheelbase_m, 1.60, 2.10) if config.wheelbase_m is not None else 1.85
    track = _clamp(config.track_width_m, 0.86, 1.16) if config.track_width_m is not None else 1.00
    wr = _clamp(config.wheel_radius_m, 0.19, 0.27) if config.wheel_radius_m is not None else 0.225

    floor = wr + FLOOR_CLEARANCE
    hub_y_r = (track - TYRE_W) * 0.5
    body_w = 2.0 * min(
        track * 0.5 - TYRE_W - 0.015,
        hub_y_r - TYRE_W * 0.5 - wr * math.sin(STEER_LIMIT) - 0.020,
    )
    seat_station = wb * 0.22
    seat_pitch = wb * 0.30
    rows = int(config.row_count)
    bed_start = seat_station - seat_pitch * (rows - 1) - wb * 0.24
    # The deck never overhangs the rear axle by more than 0.18 m.
    bed_len = min(wb * (0.46 - 0.18 * (rows - 1)), bed_start + wb * 0.5 + 0.18)
    roof_h = floor + 1.05
    cowl_x = wb * 0.46
    leaves = {"split_fold": 2, "center_fold": 2, "full_width": 1}[config.screen_build]
    seats = (2 if config.seat_build == "bucket_pair" else 1) * rows

    return ResolvedConfig(
        screen_build=config.screen_build,
        canopy_build=config.canopy_build,
        seat_build=config.seat_build,
        steer_build=config.steer_build,
        bed_build=config.bed_build,
        row_count=rows,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        wheelbase_m=wb,
        track_width_m=track,
        wheel_radius_m=wr,
        floor_height_m=floor,
        body_width_m=body_w,
        seat_station_m=seat_station,
        seat_pitch_m=seat_pitch,
        bed_length_m=bed_len,
        bed_start_m=bed_start,
        roof_height_m=roof_h,
        cowl_x_m=cowl_x,
        seat_total=seats,
        screen_leaf_count=leaves,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("screen_build", config.screen_build),
        ("canopy_build", config.canopy_build),
        ("seat_build", config.seat_build),
        ("steer_build", config.steer_build),
        ("bed_build", config.bed_build),
        ("row_count", config.row_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --- helpers ----------------------------------------------------------------
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"gc_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"gc_{r.palette_style}_{key}"
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


# --- canopy candidates ------------------------------------------------------
def _canopy_build_cowl_post_canopy_build(ch, r: ResolvedConfig, mats) -> None:
    """Canopy front edge on vertical posts rising off the cowl."""
    bw = r.body_width_m
    floor = r.floor_height_m
    for side, sy in enumerate((-1.0, 1.0)):
        ch.visual(
            Box((0.050, 0.050, r.roof_height_m - floor + 0.010)),
            origin=Origin(
                xyz=(
                    r.cowl_x_m - 0.020,
                    sy * (bw * 0.5 - 0.040),
                    (r.roof_height_m + floor) * 0.5,
                )
            ),
            material=mats["metal"],
            name=f"canopy_build__cowl_post_canopy__front_post_{side}", material_class_id="metal.steel_bare",
        )


def _canopy_build_a_post_canopy_build(ch, r: ResolvedConfig, mats) -> None:
    """Canopy front edge on rearward-raked A-posts tied by a crossbar."""
    bw = r.body_width_m
    floor = r.floor_height_m
    height = r.roof_height_m - floor + 0.010
    for side, sy in enumerate((-1.0, 1.0)):
        ch.visual(
            Box((0.044, 0.044, height)),
            origin=Origin(
                xyz=(
                    r.cowl_x_m - 0.060,
                    sy * (bw * 0.5 - 0.040),
                    (r.roof_height_m + floor) * 0.5,
                ),
                rpy=(0.0, 0.10, 0.0),
            ),
            material=mats["metal"],
            name=f"canopy_build__a_post_canopy__a_post_{side}", material_class_id="metal.steel_bare",
        )
    ch.visual(
        Box((0.060, bw - 0.010, 0.036)),
        origin=Origin(
            xyz=(
                r.cowl_x_m - 0.060 - (r.roof_height_m - floor) * 0.5 * 0.100,
                0.0,
                r.roof_height_m - 0.040,
            )
        ),
        material=mats["metal"],
        name="canopy_build__a_post_canopy__a_post_crossbar", material_class_id="metal.steel_bare",
    )


_CANOPY_BUILDERS = {
    "cowl_post_canopy": _canopy_build_cowl_post_canopy_build,
    "a_post_canopy": _canopy_build_a_post_canopy_build,
}


# --- chassis ----------------------------------------------------------------
def _build_chassis(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    ch = model.part("chassis", meta={"role": "chassis"})
    front_x = r.wheelbase_m * 0.5
    rear_x = -r.wheelbase_m * 0.5
    floor = r.floor_height_m
    bw = r.body_width_m

    ch.visual(
        Box((r.wheelbase_m - 2.0 * (r.wheel_radius_m + 0.060), bw, 0.070)),
        origin=Origin(xyz=(0.0, 0.0, floor - 0.035)),
        material=mats["body"],
        name="floor_pan", material_class_id="metal.paint_coated",
    )
    for side, sy in enumerate((-1.0, 1.0)):
        ch.visual(
            Box((r.wheelbase_m - 2.0 * (r.wheel_radius_m + 0.060), 0.040, 0.120)),
            origin=Origin(xyz=(0.0, sy * (bw * 0.5 - 0.040), floor - 0.100)),
            material=mats["trim"],
            name=f"side_sill_{side}", material_class_id="plastic.opaque_glossy_molded",
        )
    # Cowl and dash ahead of the driver.
    ch.visual(
        Box((0.170, bw, 0.310)),
        origin=Origin(xyz=(r.cowl_x_m, 0.0, floor + 0.145)),
        material=mats["body"],
        name="front_cowl", material_class_id="metal.paint_coated",
    )
    ch.visual(
        Box((0.070, bw - 0.060, 0.090)),
        origin=Origin(xyz=(r.cowl_x_m - 0.070, 0.0, floor + 0.330)),
        material=mats["trim"],
        name="dash_panel", material_class_id="plastic.opaque_glossy_molded",
    )
    # Battery bay the seat hinges over, and its backrest.
    for row in range(r.row_count):
        x = r.seat_station_m - r.seat_pitch_m * row
        ch.visual(
            Box((0.300, bw - 0.020, 0.240)),
            origin=Origin(xyz=(x, 0.0, floor + 0.110)),
            material=mats["body"],
            name=f"battery_bay_{row}", material_class_id="metal.paint_coated",
        )

        ch.visual(
            Box((0.080, bw - 0.100, 0.420)),
            origin=Origin(xyz=(x - 0.235, 0.0, floor + 0.320)),
            material=mats["body"],
            name=f"seat_back_{row}", material_class_id="metal.paint_coated",
        )
        ch.visual(
            Box((0.100, bw - 0.140, 0.100)),
            origin=Origin(xyz=(x - 0.195, 0.0, floor + 0.140)),
            material=mats["body"],
            name=f"seat_back_foot_{row}", material_class_id="metal.paint_coated",
        )
    # Roof posts and canopy: the front support is the canopy_build candidate.
    _CANOPY_BUILDERS[r.canopy_build](ch, r, mats)
    for side, sy in enumerate((-1.0, 1.0)):
        ch.visual(
            Box((0.050, 0.050, r.roof_height_m - floor + 0.010)),
            origin=Origin(
                xyz=(
                    r.bed_start_m + 0.060,
                    sy * (bw * 0.5 - 0.040),
                    (r.roof_height_m + floor) * 0.5,
                )
            ),
            material=mats["metal"],
            name=f"roof_post_1_{side}", material_class_id="metal.steel_bare",
        )
    ch.visual(
        Box((r.cowl_x_m - r.bed_start_m + 0.260, bw + 0.060, 0.045)),
        origin=Origin(
            xyz=((r.cowl_x_m + r.bed_start_m) * 0.5, 0.0, r.roof_height_m),
        ),
        material=mats["body"],
        name="canopy", material_class_id="fabric.canvas",
    )
    # Axle beams the wheels and knuckles hang on.
    hub_y = (r.track_width_m - TYRE_W) * 0.5
    rail_lo = r.wheel_radius_m - 0.035
    rail_hi = floor - 0.040
    for side, sy in enumerate((-1.0, 1.0)):
        ch.visual(
            Box((r.wheelbase_m + 0.080, 0.060, rail_hi - rail_lo)),
            origin=Origin(
                xyz=(
                    0.0,
                    sy * (hub_y - KNUCKLE_ARM - 0.0655),
                    (rail_hi + rail_lo) * 0.5,
                )
            ),
            material=mats["metal"],
            name=f"frame_rail_{side}", material_class_id="metal.steel_bare",
        )
    for name, ax in (("front_axle", front_x), ("rear_axle", rear_x)):
        ch.visual(
            Box((0.080, 2.0 * (hub_y - KNUCKLE_ARM - 0.0255), 0.070)),
            origin=Origin(xyz=(ax, 0.0, r.wheel_radius_m)),
            material=mats["metal"],
            name=name, material_class_id="metal.steel_bare",
        )
        if name == "front_axle":
            for side, sy in enumerate((-1.0, 1.0)):
                king_y = sy * (hub_y - KNUCKLE_ARM)
                ch.visual(
                    Box((0.060, 0.080, 0.020)),
                    origin=Origin(xyz=(ax, king_y - sy * 0.020, r.wheel_radius_m + 0.040)),
                    material=mats["metal"],
                    name=f"steer_cap_{side}", material_class_id="metal.steel_bare",
                )
                ch.visual(
                    Cylinder(radius=0.0135, length=0.055),
                    origin=Origin(xyz=(ax, king_y, r.wheel_radius_m + 0.0175)),
                    material=mats["metal"],
                    name=f"king_pin_{side}", material_class_id="metal.steel_bare",
                )
    for side, sy in enumerate((-1.0, 1.0)):
        inner = hub_y - KNUCKLE_ARM - 0.030
        outer = hub_y - TYRE_W * 0.5 + 0.0005
        ch.visual(
            Cylinder(radius=0.026, length=outer - inner),
            origin=Origin(
                xyz=(rear_x, sy * (inner + outer) * 0.5, r.wheel_radius_m),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["metal"],
            name=f"rear_hub_stub_{side}", material_class_id="metal.steel_bare",
        )
    return ch


def _wheel(model: ArticulatedObject, r: ResolvedConfig, mats, tag: str, y_off: float = 0.0):
    wheel = model.part(f"road_wheel_{tag}", meta={"role": "road_wheel", "index": tag})
    wheel.visual(
        Cylinder(radius=r.wheel_radius_m, length=TYRE_W),
        origin=Origin(xyz=(0.0, y_off, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["tyre"],
        name=f"tyre_{tag}", material_class_id="rubber.directional_grooved",
    )
    wheel.visual(
        Cylinder(radius=r.wheel_radius_m * 0.62, length=TYRE_W + 0.006),
        origin=Origin(xyz=(0.0, y_off, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["rim"],
        name=f"rim_{tag}", material_class_id="metal.aluminum_bare",
    )
    for i in range(4):
        wheel.visual(
            Box((r.wheel_radius_m * 0.90, 0.030, 0.030)),
            origin=Origin(
                xyz=(0.0, y_off, 0.0),
                rpy=(0.0, 0.0, 0.0) if i % 2 == 0 else (0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["rim"],
            name=f"spoke_{tag}_{i}", material_class_id="metal.aluminum_bare",
        )
    return wheel


def _build_running_gear(model: ArticulatedObject, ch, r: ResolvedConfig, mats) -> tuple:
    front_x = r.wheelbase_m * 0.5
    rear_x = -r.wheelbase_m * 0.5
    hub_y = (r.track_width_m - TYRE_W) * 0.5
    wheels, knuckles = [], []
    for side, sy in enumerate((-1.0, 1.0)):
        knuckle = model.part(f"steer_knuckle_{side}", meta={"role": "steer_knuckle", "index": side})
        knuckle.visual(
            Box((0.060, 0.032, 0.110)),
            origin=Origin(xyz=(0.0, sy * 0.030, -0.025)),
            material=mats["metal"],
            name=f"knuckle_body_{side}", material_class_id="metal.steel_bare",
        )
        knuckle.visual(
            Box((0.050, 0.0405, 0.050)),
            origin=Origin(xyz=(0.0, sy * 0.03425, 0.020)),
            material=mats["metal"],
            name=f"knuckle_stub_{side}", material_class_id="metal.steel_bare",
        )
        _joint(
            model,
            name=f"chassis_to_steer_knuckle_{side}",
            parent=ch,
            child=knuckle,
            point=(front_x, sy * (hub_y - KNUCKLE_ARM), r.wheel_radius_m - 0.020),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            child_axis=(0.0, 0.0, 1.0),
            child_radial=(1.0, 0.0, 0.0),
            lower=-STEER_LIMIT,
            upper=STEER_LIMIT,
            effort=80.0,
            velocity=2.0,
            meta={"positive_motion": "steers the front wheel toward the left"},
        )
        wheel = _wheel(model, r, mats, f"front_{side}", y_off=sy * (TYRE_W * 0.5 + 0.0005))
        _joint(
            model,
            name=f"knuckle_{side}_to_wheel",
            parent=knuckle,
            child=wheel,
            point=(0.0, sy * (KNUCKLE_ARM - TYRE_W * 0.5 - 0.0005), 0.020),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            lower=-math.pi,
            upper=math.pi,
            effort=60.0,
            velocity=25.0,
            meta={"positive_motion": "rolls the front wheel forward"},
        )
        wheels.append(wheel)
        knuckles.append(knuckle)
    for side, sy in enumerate((-1.0, 1.0)):
        wheel = _wheel(model, r, mats, f"rear_{side}", y_off=sy * (TYRE_W * 0.5 + 0.0005))
        _joint(
            model,
            name=f"chassis_to_rear_wheel_{side}",
            parent=ch,
            child=wheel,
            point=(rear_x, sy * (hub_y - TYRE_W * 0.5 - 0.0005), r.wheel_radius_m),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            lower=-math.pi,
            upper=math.pi,
            effort=140.0,
            velocity=25.0,
            meta={"positive_motion": "drives the rear wheel forward"},
        )
        wheels.append(wheel)
    return wheels, knuckles


# --- windshield candidates --------------------------------------------------
def _build_screen(model: ArticulatedObject, ch, r: ResolvedConfig, mats) -> list:
    kind = r.screen_build
    bw = r.body_width_m
    base_z = r.floor_height_m + 0.300
    top_z = r.roof_height_m - 0.030
    height = top_z - base_z
    leaves = []
    lug_y = bw * 0.5 - 0.060
    if kind == "center_fold":
        ch.visual(
            Box((0.030, 0.029, 0.180)),
            origin=Origin(xyz=(r.cowl_x_m + 0.110, 0.0, base_z + 0.070)),
            material=mats["trim"],
            name="screen_build__center_fold__centre_post", material_class_id="plastic.opaque_glossy_molded",
        )
        ch.visual(
            Box((0.150, 0.030, 0.030)),
            origin=Origin(xyz=(r.cowl_x_m + 0.045, 0.0, base_z - 0.020)),
            material=mats["trim"],
            name="screen_build__center_fold__centre_post_arm", material_class_id="plastic.opaque_glossy_molded",
        )
        ch.visual(
            Box((0.030, 0.026, 0.040)),
            origin=Origin(xyz=(r.cowl_x_m + 0.110, 0.0, base_z - 0.015)),
            material=mats["trim"],
            name="screen_build__center_fold__centre_post_foot", material_class_id="plastic.opaque_glossy_molded",
        )
    for side, sy in enumerate((-1.0, 1.0)):
        if kind == "center_fold":
            break
        ch.visual(
            Box((0.030, 0.030, 0.045)),
            origin=Origin(xyz=(r.cowl_x_m + 0.110, sy * lug_y, base_z - 0.005)),
            material=mats["trim"],
            name=f"screen_build__{kind}__screen_lug_{side}", material_class_id="plastic.opaque_glossy_molded",
        )
        ch.visual(
            Box((0.150, 0.030, 0.030)),
            origin=Origin(xyz=(r.cowl_x_m + 0.045, sy * lug_y, base_z - 0.020)),
            material=mats["trim"],
            name=f"screen_build__{kind}__screen_lug_arm_{side}", material_class_id="plastic.opaque_glossy_molded",
        )
    leaf_specs = {
        "split_fold": (
            (height * 0.52, base_z + height * 0.26),
            (height * 0.46, base_z + height * 0.77),
        ),
        "center_fold": ((height, base_z + height * 0.5), (height, base_z + height * 0.5)),
        "full_width": ((height, base_z + height * 0.5),),
    }[kind]
    for index, (leaf_h, leaf_z) in enumerate(leaf_specs):
        leaf = model.part(
            f"screen_build__{kind}__windshield_leaf_{index}",
            meta={"role": "windshield_leaf", "index": index},
        )
        leaf_w = bw * 0.42 if kind == "center_fold" else bw - 0.160
        lug_y = bw * 0.5 - 0.060
        leaf_y = 0.0
        if kind == "center_fold":
            leaf_y = (-1.0 if index == 0 else 1.0) * (leaf_w * 0.5 + 0.014)
        leaf.visual(
            Box((0.014, leaf_w, leaf_h)),
            origin=Origin(xyz=(0.0, leaf_y, leaf_h * 0.5)),
            material=mats["glass"],
            name=f"screen_build__{kind}__glass_{index}", material_class_id="glass.clear_transparent",
        )
        if kind == "center_fold":
            leaf.visual(
                Cylinder(radius=0.014, length=0.070),
                origin=Origin(xyz=(0.0, 0.0, 0.070)),
                material=mats["trim"],
                name=f"screen_build__{kind}__hinge_knuckle_{index}", material_class_id="plastic.opaque_glossy_molded",
            )
        else:
            leaf.visual(
                Cylinder(radius=0.012, length=2.0 * (lug_y - 0.0155)),
                origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["trim"],
                name=f"screen_build__{kind}__hinge_knuckle_{index}", material_class_id="plastic.opaque_glossy_molded",
            )
        leaf.visual(
            Box((0.020, leaf_w, 0.026)),
            origin=Origin(xyz=(0.0, leaf_y, 0.013)),
            material=mats["trim"],
            name=f"screen_build__{kind}__leaf_rail_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        leaf.visual(
            Box((0.020, leaf_w, 0.026)),
            origin=Origin(xyz=(0.0, leaf_y, leaf_h - 0.013)),
            material=mats["trim"],
            name=f"screen_build__{kind}__leaf_cap_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        if kind == "center_fold":
            hinge_point = (
                r.cowl_x_m + 0.110,
                (-1.0 if index == 0 else 1.0) * 0.029,
                leaf_z - leaf_h * 0.5,
            )
            axis = (0.0, 0.0, 1.0)
            radial = (1.0, 0.0, 0.0)
            child_axis = (0.0, 0.0, 1.0)
            child_radial = (1.0, 0.0, 0.0)
            lower, upper = (0.0, SCREEN_FOLD) if index == 0 else (-SCREEN_FOLD, 0.0)
            # Each half hangs off the centre post, so it swings inboard.
            leaf.visual(
                Box((0.020, leaf_w, 0.020)),
                origin=Origin(xyz=(0.0, leaf_y, leaf_h * 0.5)),
                material=mats["trim"],
                name=f"screen_build__{kind}__centre_stile_{index}", material_class_id="plastic.opaque_glossy_molded",
            )
        else:
            hinge_point = (r.cowl_x_m + 0.110, 0.0, leaf_z - leaf_h * 0.5)
            axis = (0.0, 1.0, 0.0)
            radial = (1.0, 0.0, 0.0)
            child_axis = (0.0, 1.0, 0.0)
            child_radial = (1.0, 0.0, 0.0)
            lower, upper = 0.0, SCREEN_FOLD
        parent_part = leaves[0] if (kind == "split_fold" and index == 1) else ch
        if kind == "split_fold" and index == 1:
            hinge_point = (0.0, 0.0, leaf_specs[0][0] + 0.0125)
        _joint(
            model,
            name=f"chassis_to_windshield_leaf_{index}",
            parent=parent_part,
            child=leaf,
            point=hinge_point,
            axis=axis,
            radial=radial,
            child_axis=child_axis,
            child_radial=child_radial,
            lower=lower,
            upper=upper,
            effort=20.0,
            velocity=1.5,
            meta={"positive_motion": f"folds windshield leaf {index}"},
        )
        leaves.append(leaf)
    return leaves


# --- seat candidates --------------------------------------------------------
def _build_seats(model: ArticulatedObject, ch, r: ResolvedConfig, mats) -> list:
    kind = r.seat_build
    bw = r.body_width_m
    seats = []
    lift = 0.110 if kind == "rear_deck_row" else 0.0
    for row in range(r.row_count):
        x = r.seat_station_m - r.seat_pitch_m * row
        z = r.floor_height_m + 0.2700 + lift
        if kind == "rear_deck_row":
            ch.visual(
                Box((0.320, bw - 0.020, 0.110)),
                origin=Origin(xyz=(x, 0.0, r.floor_height_m + 0.230 + 0.055)),
                material=mats["body"],
                name=f"seat_build__rear_deck_row__deck_riser_{row}", material_class_id="metal.paint_coated",
            )
            ch.visual(
                Box((0.016, bw - 0.060, 0.070)),
                origin=Origin(xyz=(x + 0.156, 0.0, r.floor_height_m + 0.230 + 0.055)),
                material=mats["trim"],
                name=f"seat_build__rear_deck_row__deck_fascia_{row}", material_class_id="plastic.opaque_glossy_molded",
            )
        if kind == "bucket_pair":
            spots = ((-bw * 0.22, bw * 0.34), (bw * 0.22, bw * 0.34))
        else:
            spots = ((0.0, bw - 0.100),)
        for i, (sy, sw) in enumerate(spots):
            seat = model.part(
                f"seat_build__{kind}__seat_cushion_{row}_{i}",
                meta={"role": "seat_cushion", "row": row, "index": i},
            )
            seat.visual(
                Box((0.280, sw, 0.075)),
                origin=Origin(xyz=(0.155, 0.0, 0.0)),
                material=mats["seat"],
                name=f"seat_build__{kind}__cushion_{row}_{i}", material_class_id="fabric.upholstery_plain",
            )
            seat.visual(
                Box((0.290, sw + 0.010, 0.020)),
                origin=Origin(xyz=(0.155, 0.0, -0.0295)),
                material=mats["trim"],
                name=f"seat_build__{kind}__cushion_pan_{row}_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
            if kind == "bucket_pair":
                for b, by in enumerate((-1.0, 1.0)):
                    seat.visual(
                        Box((0.270, 0.030, 0.055)),
                        origin=Origin(xyz=(0.155, by * (sw * 0.5 - 0.014), 0.050)),
                        material=mats["seat"],
                        name=f"seat_build__bucket_pair__bolster_{row}_{i}_{b}", material_class_id="fabric.upholstery_plain",
                    )
            elif kind == "rear_deck_row":
                seat.visual(
                    Box((0.260, 0.034, 0.048)),
                    origin=Origin(xyz=(0.155, 0.0, 0.052)),
                    material=mats["seat"],
                    name=f"seat_build__rear_deck_row__deck_bolster_{row}_{i}", material_class_id="fabric.upholstery_plain",
                )
            else:
                seat.visual(
                    Box((0.040, sw * 0.86, 0.026)),
                    origin=Origin(xyz=(0.250, 0.0, 0.048)),
                    material=mats["trim"],
                    name=f"seat_build__{kind}__cushion_seam_{row}_{i}", material_class_id="plastic.opaque_glossy_molded",
                )
            for lug, ly in enumerate((-1.0, 1.0)):
                ch.visual(
                    Box((0.040, 0.030, 0.070)),
                    origin=Origin(
                        xyz=(
                            x - 0.145,
                            sy + ly * (sw * 0.5 + 0.0155),
                            r.floor_height_m + 0.250 + lift,
                        )
                    ),
                    material=mats["metal"],
                    name=f"seat_hinge_lug_{row}_{i}_{lug}", material_class_id="metal.steel_bare",
                )
            _joint(
                model,
                name=f"chassis_to_seat_cushion_{row}_{i}",
                parent=ch,
                child=seat,
                point=(x - 0.145, sy, z),
                axis=(0.0, 1.0, 0.0),
                radial=(1.0, 0.0, 0.0),
                child_axis=(0.0, 1.0, 0.0),
                child_radial=(1.0, 0.0, 0.0),
                lower=-SEAT_LIFT,
                upper=0.0,
                effort=30.0,
                velocity=1.5,
                meta={"positive_motion": "tips the cushion up off the battery bay"},
            )
            seats.append(seat)
    if kind == "rear_facing":
        _seat_build_rear_facing_build(ch, r, mats)
    return seats


def _seat_build_rear_facing_build(ch, r: ResolvedConfig, mats) -> None:
    """Rear-facing bench behind the last row, back to back over the cargo deck.

    Every hinged cushion still faces forward; the rear-facing seat is its own
    chassis-fixed module whose backrest is at its front edge, sharing the last
    row's seat back as the back-to-back divider.  It rides on skid rails that
    land on the bed deck, so the bed keeps its full length underneath.
    """
    bw = r.body_width_m
    sw = bw - 0.140
    floor = r.floor_height_m
    x_last = r.seat_station_m - r.seat_pitch_m * (r.row_count - 1)
    # Front face of the module: the rear face of the last row's seat back.
    divider = x_last - 0.235 - 0.040
    cushion_z = floor + 0.270
    deck_top = floor + 0.190 + 0.025

    back_x = divider - 0.030 + MOUNT
    ch.visual(
        Box((0.060, sw, 0.320)),
        origin=Origin(xyz=(back_x, 0.0, cushion_z + 0.1225)),
        material=mats["seat"],
        name="seat_build__rear_facing__rear_backrest_0", material_class_id="fabric.upholstery_plain",
    )
    cushion_x = back_x - 0.030 - 0.150 + MOUNT
    ch.visual(
        Box((0.300, sw, 0.075)),
        origin=Origin(xyz=(cushion_x, 0.0, cushion_z)),
        material=mats["seat"],
        name="seat_build__rear_facing__rear_cushion_0", material_class_id="fabric.upholstery_plain",
    )
    ch.visual(
        Box((0.310, sw + 0.010, 0.020)),
        origin=Origin(xyz=(cushion_x, 0.0, cushion_z - 0.0295)),
        material=mats["trim"],
        name="seat_build__rear_facing__rear_cushion_pan_0", material_class_id="plastic.opaque_glossy_molded",
    )
    # Skid rails bridging the pan down onto the bed deck it sits over.
    rail_rear = cushion_x - 0.150 + 0.020
    rail_front = r.bed_start_m - 0.020
    rail_lo = deck_top - MOUNT
    rail_hi = cushion_z - 0.0395 + MOUNT
    for side, sy in enumerate((-1.0, 1.0)):
        ch.visual(
            Box((rail_front - rail_rear, 0.040, rail_hi - rail_lo)),
            origin=Origin(
                xyz=(
                    (rail_front + rail_rear) * 0.5,
                    sy * (sw * 0.5 - 0.040),
                    (rail_hi + rail_lo) * 0.5,
                )
            ),
            material=mats["metal"],
            name=f"seat_build__rear_facing__bench_skid_{side}", material_class_id="metal.steel_bare",
        )


# --- steering candidates ----------------------------------------------------
def _build_steer(model: ArticulatedObject, ch, r: ResolvedConfig, mats):
    kind = r.steer_build
    control = model.part(f"steer_build__{kind}__driver_control", meta={"role": "driver_control"})
    base = (r.cowl_x_m - 0.180, -r.body_width_m * 0.22, r.floor_height_m + 0.330)
    reach = (r.cowl_x_m - 0.105) - base[0] + 0.0020
    for cheek, sc in enumerate((-1.0, 1.0)):
        if kind == "tiller":
            xyz = (base[0] + sc * 0.0205, base[1], base[2] + 0.150)
            size = (0.012, 0.060, 0.080)
        else:
            xyz = (r.cowl_x_m - 0.1325, base[1], base[2] + sc * 0.0205)
            size = (0.055, 0.060, 0.012)
        ch.visual(
            Box(size),
            origin=Origin(xyz=xyz),
            material=mats["trim"],
            name=f"steer_build__{kind}__control_yoke_{cheek}", material_class_id="plastic.opaque_glossy_molded",
        )
    if kind == "tiller":
        ch.visual(
            Box((0.053, 0.014, 0.080)),
            origin=Origin(xyz=(base[0], base[1] + 0.023, base[2] + 0.150)),
            material=mats["trim"],
            name="steer_build__tiller__yoke_bridge", material_class_id="plastic.opaque_glossy_molded",
        )
        ch.visual(
            Box((0.085, 0.024, 0.024)),
            origin=Origin(xyz=(base[0] + 0.0625, base[1], base[2] + 0.150)),
            material=mats["trim"],
            name="steer_build__tiller__yoke_arm", material_class_id="plastic.opaque_glossy_molded",
        )
        ch.visual(
            Box((0.030, 0.024, 0.190)),
            origin=Origin(xyz=(base[0] + 0.100, base[1], base[2] + 0.075)),
            material=mats["trim"],
            name="steer_build__tiller__control_tower", material_class_id="plastic.opaque_glossy_molded",
        )
    else:
        ch.visual(
            Box((0.029, 0.060, 0.047)),
            origin=Origin(xyz=(r.cowl_x_m - 0.1145, base[1], base[2])),
            material=mats["trim"],
            name="steer_build__wheel_column__control_tower", material_class_id="plastic.opaque_glossy_molded",
        )
    if kind == "wheel_column":
        control.visual(
            Cylinder(radius=0.135, length=0.022),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name="steer_build__wheel_column__wheel_rim", material_class_id="metal.steel_bare",
        )
        control.visual(
            Cylinder(radius=0.040, length=0.030),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["trim"],
            name="steer_build__wheel_column__wheel_hub", material_class_id="plastic.opaque_glossy_molded",
        )
        for i in range(3):
            a = 2.0 * math.pi * i / 3.0
            control.visual(
                Box((0.018, 0.030, 0.135)),
                origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(a, 0.0, 0.0)),
                material=mats["trim"],
                name=f"steer_build__wheel_column__wheel_spoke_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        control.visual(
            Cylinder(radius=0.014, length=reach - 0.032),
            origin=Origin(xyz=((reach - 0.032) * 0.5, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name="steer_build__wheel_column__column_shaft", material_class_id="metal.steel_bare",
        )
    else:
        control.visual(
            Cylinder(radius=0.014, length=0.360),
            origin=Origin(xyz=(0.0, 0.0, 0.170)),
            material=mats["metal"],
            name="steer_build__tiller__tiller_post", material_class_id="metal.steel_bare",
        )
        control.visual(
            Cylinder(radius=0.020, length=r.body_width_m * 0.42),
            origin=Origin(xyz=(0.0, 0.0, 0.340), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["trim"],
            name="steer_build__tiller__tiller_bar", material_class_id="plastic.opaque_glossy_molded",
        )
        control.visual(
            Box((reach, 0.040, 0.030)),
            origin=Origin(xyz=(reach * 0.5, 0.0, 0.010)),
            material=mats["metal"],
            name="steer_build__tiller__steering_link", material_class_id="metal.steel_bare",
        )
        control.visual(
            Cylinder(radius=0.014, length=0.040),
            origin=Origin(xyz=(reach - 0.020, 0.0, 0.010)),
            material=mats["metal"],
            name="steer_build__tiller__link_ball", material_class_id="metal.steel_bare",
        )
    _joint(
        model,
        name="chassis_to_driver_control",
        parent=ch,
        child=control,
        point=base,
        axis=(0.0, 0.0, 1.0) if kind == "tiller" else (1.0, 0.0, 0.0),
        radial=(1.0, 0.0, 0.0) if kind == "tiller" else (0.0, 0.0, 1.0),
        child_axis=(0.0, 0.0, 1.0) if kind == "tiller" else (1.0, 0.0, 0.0),
        child_radial=(1.0, 0.0, 0.0) if kind == "tiller" else (0.0, 0.0, 1.0),
        lower=-STEER_LIMIT * 2.0,
        upper=STEER_LIMIT * 2.0,
        effort=12.0,
        velocity=3.0,
        meta={"positive_motion": "turns the driver control toward the left"},
    )
    return control


# --- cargo bed candidates ---------------------------------------------------
def _build_bed(model: ArticulatedObject, ch, r: ResolvedConfig, mats):
    kind = r.bed_build
    bw = r.body_width_m
    deck_z = r.floor_height_m + 0.190
    rear_x = r.bed_start_m - r.bed_length_m
    ch.visual(
        Box((0.030, bw - 0.090, 0.030 if kind == "tailgate" else 0.040)),
        origin=Origin(
            xyz=(
                r.bed_start_m - r.bed_length_m + 0.0255,
                0.0,
                deck_z + (0.011 if kind == "tailgate" else 0.0405),
            )
        ),
        material=mats["metal"],
        name=f"bed_build__{kind}__closure_hinge_bar", material_class_id="metal.steel_bare",
    )
    ch.visual(
        Box((r.bed_length_m, bw, 0.050)),
        origin=Origin(xyz=(r.bed_start_m - r.bed_length_m * 0.5, 0.0, deck_z)),
        material=mats["body"],
        name=f"bed_build__{kind}__bed_deck", material_class_id="metal.paint_coated",
    )
    riser_lo = r.floor_height_m - 0.060
    riser_hi = deck_z - 0.015
    rail_y = (r.track_width_m - TYRE_W) * 0.5 - KNUCKLE_ARM - 0.0655
    for side, sy in enumerate((-1.0, 1.0)):
        for i in range(2):
            ch.visual(
                Box((0.070, 0.060, riser_hi - riser_lo)),
                origin=Origin(
                    xyz=(
                        r.bed_start_m - r.bed_length_m * (0.12 + 0.62 * i),
                        sy * rail_y,
                        (riser_hi + riser_lo) * 0.5,
                    )
                ),
                material=mats["metal"],
                name=f"bed_build__{kind}__bed_riser_{side}_{i}", material_class_id="metal.steel_bare",
            )
    if kind == "tailgate":
        for side, sy in enumerate((-1.0, 1.0)):
            ch.visual(
                Box((r.bed_length_m - 0.060, 0.040, 0.170)),
                origin=Origin(
                    xyz=(
                        r.bed_start_m - r.bed_length_m * 0.5 + 0.030,
                        sy * (bw * 0.5 - 0.020),
                        deck_z + 0.110,
                    )
                ),
                material=mats["body"],
                name=f"bed_build__tailgate__bed_side_{side}", material_class_id="metal.paint_coated",
            )
        gate = model.part("bed_build__tailgate__tailgate", meta={"role": "cargo_closure"})
        gate.visual(
            Box((0.020, bw - 0.020, 0.170)),
            origin=Origin(xyz=(0.0, 0.0, 0.085)),
            material=mats["body"],
            name="bed_build__tailgate__gate_panel", material_class_id="metal.paint_coated",
        )
        gate.visual(
            Box((0.034, bw - 0.010, 0.026)),
            origin=Origin(xyz=(0.0, 0.0, 0.160)),
            material=mats["trim"],
            name="bed_build__tailgate__gate_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        _joint(
            model,
            name="chassis_to_cargo_closure",
            parent=ch,
            child=gate,
            point=(rear_x, 0.0, deck_z + 0.026),
            axis=(0.0, 1.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            child_axis=(0.0, 1.0, 0.0),
            child_radial=(0.0, 0.0, 1.0),
            lower=-GATE_DROP,
            upper=0.0,
            effort=25.0,
            velocity=1.5,
            meta={"positive_motion": "lifts the dropped tailgate shut"},
        )
        return gate
    rail = model.part("bed_build__flatbed__side_rail", meta={"role": "cargo_closure"})
    rail_len = r.bed_length_m
    for side, sy in enumerate((-1.0, 1.0)):
        rail.visual(
            Box((rail_len * 0.15 + 0.030, 0.030, 0.030)),
            origin=Origin(xyz=(rail_len * 0.075 + 0.015, sy * (bw * 0.5 - 0.0295), 0.0)),
            material=mats["metal"],
            name=f"bed_build__flatbed__rail_lug_{side}", material_class_id="metal.steel_bare",
        )
        rail.visual(
            Cylinder(radius=0.018, length=rail_len),
            origin=Origin(
                xyz=(rail_len * 0.5, sy * (bw * 0.5 - 0.030), 0.150),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["metal"],
            name=f"bed_build__flatbed__rail_tube_{side}", material_class_id="metal.steel_bare",
        )
        for post in range(2):
            rail.visual(
                Box((0.034, 0.034, 0.150)),
                origin=Origin(
                    xyz=(
                        rail_len * (0.15 + 0.70 * post),
                        sy * (bw * 0.5 - 0.030),
                        0.0755,
                    )
                ),
                material=mats["metal"],
                name=f"bed_build__flatbed__rail_post_{side}_{post}", material_class_id="metal.steel_bare",
            )
    rail.visual(
        Cylinder(radius=0.018, length=bw - 0.060),
        origin=Origin(xyz=(rail_len - 0.018, 0.0, 0.150), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name="bed_build__flatbed__rail_end", material_class_id="metal.steel_bare",
    )
    _joint(
        model,
        name="chassis_to_cargo_closure",
        parent=ch,
        child=rail,
        point=(rear_x, 0.0, deck_z + 0.0405),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        child_axis=(0.0, 1.0, 0.0),
        child_radial=(1.0, 0.0, 0.0),
        lower=-1.20,
        upper=0.0,
        effort=25.0,
        velocity=1.5,
        meta={"positive_motion": "swings the folded side rails back upright"},
    )
    return rail


# --- assembly ---------------------------------------------------------------
def build_picturex_0611_golf_cart(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Golf_cart",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "steered-front, driven-rear four-wheel cart",
        },
    )
    mats = _materials(model, r)
    ch = _build_chassis(model, r, mats)
    _build_running_gear(model, ch, r, mats)
    _build_screen(model, ch, r, mats)
    _build_seats(model, ch, r, mats)
    _build_steer(model, ch, r, mats)
    _build_bed(model, ch, r, mats)

    steer_joints = [f"chassis_to_steer_knuckle_{s}" for s in range(2)]
    model.meta["risk_poses"] = (
        {name: 0.0 for name in steer_joints},
        {name: STEER_LIMIT for name in steer_joints},
        {name: -STEER_LIMIT for name in steer_joints},
    )
    model.meta["coupled_joint_pairs"] = ((steer_joints[0], steer_joints[1]),)
    return model


def build_seeded_picturex_0611_golf_cart(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_golf_cart(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_golf_cart_tests(model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    chassis = _parts_by_role(model, "chassis")
    wheels = _parts_by_role(model, "road_wheel")
    knuckles = _parts_by_role(model, "steer_knuckle")
    seats = _parts_by_role(model, "seat_cushion")
    leaves = _parts_by_role(model, "windshield_leaf")
    joints = {j.name: j for j in model.articulations}

    spin_joints = [joints.get(f"knuckle_{s}_to_wheel") for s in range(2)] + [
        joints.get(f"chassis_to_rear_wheel_{s}") for s in range(2)
    ]
    steer_joints = [joints.get(f"chassis_to_steer_knuckle_{s}") for s in range(2)]
    ctx.check(
        "category_anchor: four road wheels spin and the front pair steers",
        len(chassis) == 1
        and len(wheels) == 4
        and len(knuckles) == 2
        and bool(model.root_parts())
        and model.root_parts()[0].name == "chassis"
        and all(
            j is not None
            and tuple(round(abs(v), 6) for v in j.axis) == (0.0, 1.0, 0.0)
            and j.motion_limits is not None
            and j.motion_limits.upper - j.motion_limits.lower > 6.0
            for j in spin_joints
        )
        and all(
            j is not None
            and j.parent == "chassis"
            and tuple(round(abs(v), 6) for v in j.axis) == (0.0, 0.0, 1.0)
            and j.motion_limits is not None
            and abs(j.motion_limits.upper - STEER_LIMIT) < 1e-6
            for j in steer_joints
        ),
        details=f"wheels={len(wheels)} knuckles={len(knuckles)}",
    )

    # Decisive motion evidence: the seat really tips up and a screen leaf folds.
    seat_joint = joints.get("chassis_to_seat_cushion_0_0")
    seat_elem = f"seat_build__{r.seat_build}__cushion_0_0"
    rest = ctx.part_element_world_aabb(seats[0], elem=seat_elem)
    with ctx.pose({seat_joint: -SEAT_LIFT}):
        lifted = ctx.part_element_world_aabb(seats[0], elem=seat_elem)
    leaf_joint = joints.get("chassis_to_windshield_leaf_0")
    leaf_elem = f"screen_build__{r.screen_build}__glass_0"
    leaf_rest = ctx.part_element_world_aabb(leaves[0], elem=leaf_elem)
    with ctx.pose({leaf_joint: leaf_joint.motion_limits.upper}):
        leaf_folded = ctx.part_element_world_aabb(leaves[0], elem=leaf_elem)
    ctx.check(
        "category_anchor: the seat hinges over the bay and the screen folds",
        len(seats) == r.seat_total
        and len(leaves) == r.screen_leaf_count
        and rest is not None
        and lifted is not None
        and lifted[1][2] > rest[1][2] + 0.080
        and leaf_rest is not None
        and leaf_folded is not None
        and (
            abs(leaf_folded[1][0] - leaf_rest[1][0])
            + abs(leaf_folded[1][1] - leaf_rest[1][1])
            + abs(leaf_folded[1][2] - leaf_rest[1][2])
        )
        > 0.060,
        details=f"seats={len(seats)} leaves={len(leaves)} seat={rest}->{lifted}",
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    screen_marker = {
        "split_fold": "split_fold__glass_1",
        "center_fold": "center_fold__centre_stile_0",
        "full_width": "full_width__glass_0",
    }[r.screen_build]
    ctx.check(
        "category_anchor: screen_build identity",
        any(screen_marker in n for n in visual_names),
        details=f"screen_build={r.screen_build}",
    )

    seat_marker = {
        "bench": "bench__cushion_seam_",
        "bucket_pair": "bucket_pair__bolster_",
        "rear_facing": "rear_facing__rear_backrest_",
        "rear_deck_row": "rear_deck_row__deck_riser_",
    }[r.seat_build]
    canopy_marker = {
        "cowl_post_canopy": "cowl_post_canopy__front_post_0",
        "a_post_canopy": "a_post_canopy__a_post_crossbar",
    }[r.canopy_build]
    ctx.check(
        "category_anchor: canopy_build identity",
        any(canopy_marker in n for n in visual_names) and "canopy" in visual_names,
        details=f"canopy_build={r.canopy_build}",
    )

    ctx.check(
        "category_anchor: seat_build identity",
        any(seat_marker in n for n in visual_names) and len(seats) == r.seat_total,
        details=f"seat_build={r.seat_build} seats={len(seats)}",
    )

    steer_marker = {
        "wheel_column": "wheel_column__wheel_rim",
        "tiller": "tiller__steering_link",
    }[r.steer_build]
    ctx.check(
        "category_anchor: steer_build identity",
        any(steer_marker in n for n in visual_names),
        details=f"steer_build={r.steer_build}",
    )

    bed_marker = {
        "tailgate": "tailgate__gate_panel",
        "flatbed": "flatbed__rail_end",
    }[r.bed_build]
    ctx.check(
        "category_anchor: bed_build identity",
        any(bed_marker in n for n in visual_names),
        details=f"bed_build={r.bed_build}",
    )

    ctx.check(
        "the bed shortens so every seat row still fits",
        r.bed_length_m > 0.24
        and r.bed_start_m - r.bed_length_m > -r.wheelbase_m * 0.5 - 0.20
        and r.seat_station_m - r.seat_pitch_m * (r.row_count - 1) > r.bed_start_m,
        details=(
            f"rows={r.row_count} bed={r.bed_length_m} start={r.bed_start_m} seat={r.seat_station_m}"
        ),
    )

    # No occupant ever faces the tailgate: every hinged cushion sits ahead of
    # its row's seat back, and rear_facing puts its bench in its own module
    # behind the last row rather than turning the driver around.
    seat_back_0 = ctx.part_element_world_aabb(chassis[0], elem="seat_back_0")
    cushion_0 = ctx.part_element_world_aabb(seats[0], elem=seat_elem)
    faces_forward = (
        seat_back_0 is not None and cushion_0 is not None and cushion_0[0][0] > seat_back_0[1][0]
    )
    if r.seat_build == "rear_facing":
        back_last = ctx.part_element_world_aabb(chassis[0], elem=f"seat_back_{r.row_count - 1}")
        bench_back = ctx.part_element_world_aabb(
            chassis[0], elem="seat_build__rear_facing__rear_backrest_0"
        )
        bench_pad = ctx.part_element_world_aabb(
            chassis[0], elem="seat_build__rear_facing__rear_cushion_0"
        )
        faces_forward = (
            faces_forward
            and back_last is not None
            and bench_back is not None
            and bench_pad is not None
            and bench_back[1][0] <= back_last[0][0] + 2.0 * MOUNT
            and bench_pad[1][0] <= bench_back[0][0] + 2.0 * MOUNT
        )
    ctx.check(
        "hinged cushions face forward and rear_facing is a bench behind them",
        faces_forward,
        details=f"seat_build={r.seat_build} cushion={cushion_0} seat_back={seat_back_0}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "shortest_narrowest_two_rows",
        {
            "screen_build": "center_fold",
            "canopy_build": "a_post_canopy",
            "seat_build": "bucket_pair",
            "steer_build": "tiller",
            "bed_build": "flatbed",
            "row_count": 2,
            "wheelbase_m": 1.60,
            "track_width_m": 0.86,
            "wheel_radius_m": 0.19,
        },
        reason="shortest narrowest cart carrying two bucket rows and the shortest bed",
    ),
    corner_case(
        "longest_widest_single_row",
        {
            "screen_build": "split_fold",
            "canopy_build": "cowl_post_canopy",
            "seat_build": "bench",
            "steer_build": "wheel_column",
            "bed_build": "tailgate",
            "row_count": 1,
            "wheelbase_m": 2.10,
            "track_width_m": 1.16,
            "wheel_radius_m": 0.27,
        },
        reason="largest envelope on the tallest wheels with the longest bed",
    ),
    corner_case(
        "rear_facing_two_rows_tall_wheels",
        {
            "screen_build": "full_width",
            "canopy_build": "a_post_canopy",
            "seat_build": "rear_facing",
            "steer_build": "tiller",
            "bed_build": "tailgate",
            "row_count": 2,
            "wheelbase_m": 1.60,
            "track_width_m": 1.16,
            "wheel_radius_m": 0.27,
        },
        reason="rear-facing bench squeezed behind two rows on the shortest wheelbase",
    ),
    corner_case(
        "full_width_screen_flatbed",
        {
            "screen_build": "full_width",
            "canopy_build": "cowl_post_canopy",
            "seat_build": "bucket_pair",
            "steer_build": "wheel_column",
            "bed_build": "flatbed",
            "row_count": 1,
            "wheelbase_m": 2.10,
            "track_width_m": 0.86,
            "wheel_radius_m": 0.19,
        },
        reason="longest narrow cart with one screen leaf over an open flatbed",
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
    "build_picturex_0611_golf_cart",
    "build_seeded_picturex_0611_golf_cart",
    "run_picturex_0611_golf_cart_tests",
]
