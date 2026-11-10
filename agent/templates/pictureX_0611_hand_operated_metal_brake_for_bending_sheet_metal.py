# SPDX-License-Identifier: Apache-2.0

"""Self-contained hand-operated sheet-metal bending brake template.

The grounded ``frame`` part is the bed: a plate with a bending edge rail along
+x at y=0, forked hinge ears for both moving members, a rear apron and the
adjuster posts behind it.  The ``clamp_beam`` part hinges REVOLUTE about +x at
the back of the bed and lifts its nose off the bed; the ``bending_leaf`` part
hinges REVOLUTE about +x one clearance in front of the bending edge and folds up
through a travel that stops just short of the bend line, so it never reaches
back under the clamp nose.  Each clamp station carries a ``handle_{i}`` lever on
the clamp beam and an ``adjuster_{i}`` screw on a PRISMATIC slide behind the bed.

Four slots vary without touching that chain: ``frame_form`` (bare bed, bench-top
pad, floor stand), ``clamp_form`` (plain bar, bolted segments, removable
fingers, screw-down clamps), ``leaf_form`` (plain leaf, segmented leaf) and
``accessory`` (PRISMATIC bend-stop fence, centre lever).
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
    MotionProperties,
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

FrameForm = Literal["plain_bed", "bench_top", "floor_stand"]
ClampForm = Literal[
    "plain_clamp_bar", "segmented_clamp", "finger_clamp", "screw_down_clamp"
]
LeafForm = Literal["plain_leaf", "segmented_leaf"]
Accessory = Literal["bend_stop_fence", "center_lever"]
PaletteStyle = Literal["works_red", "machine_grey", "safety_yellow", "cast_green"]

FRAME_FORMS: tuple[FrameForm, ...] = ("plain_bed", "bench_top", "floor_stand")
CLAMP_FORMS: tuple[ClampForm, ...] = (
    "plain_clamp_bar",
    "segmented_clamp",
    "finger_clamp",
    "screw_down_clamp",
)
LEAF_FORMS: tuple[LeafForm, ...] = ("plain_leaf", "segmented_leaf")
ACCESSORIES: tuple[Accessory, ...] = ("bend_stop_fence", "center_lever")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "works_red",
    "machine_grey",
    "safety_yellow",
    "cast_green",
)


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("frame_form", FRAME_FORMS),
        component_slot("clamp_form", CLAMP_FORMS),
        component_slot("leaf_form", LEAF_FORMS),
        component_slot("accessory", ACCESSORIES),
        multiplicity_slot("clamp_station_count", (2, 3, 4), item_slot="clamp_form"),
        multiplicity_slot("leaf_rib_count", (3, 5, 7), item_slot="leaf_form"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "works_red": {
        "frame": (0.58, 0.16, 0.14, 1.0),
        "steel": (0.74, 0.76, 0.78, 1.0),
        "dark": (0.16, 0.17, 0.18, 1.0),
        "accent": (0.88, 0.80, 0.30, 1.0),
    },
    "machine_grey": {
        "frame": (0.44, 0.46, 0.48, 1.0),
        "steel": (0.80, 0.81, 0.82, 1.0),
        "dark": (0.18, 0.19, 0.20, 1.0),
        "accent": (0.26, 0.52, 0.78, 1.0),
    },
    "safety_yellow": {
        "frame": (0.78, 0.66, 0.16, 1.0),
        "steel": (0.76, 0.78, 0.80, 1.0),
        "dark": (0.14, 0.14, 0.15, 1.0),
        "accent": (0.20, 0.20, 0.22, 1.0),
    },
    "cast_green": {
        "frame": (0.20, 0.38, 0.28, 1.0),
        "steel": (0.72, 0.74, 0.76, 1.0),
        "dark": (0.12, 0.16, 0.14, 1.0),
        "accent": (0.86, 0.84, 0.78, 1.0),
    },
}


# Fixed manufacturing cross-sections (surface detail, not core/raw).
BED_T = 0.012
EDGE_RAIL_D = 0.020
CLAMP_BEAM_H = 0.024
CLAMP_LIFT_Z = 0.030
CLAMP_NOSE_D = 0.030
LEAF_T = 0.010
LEAF_HINGE_Y = 0.006
FOLD_TRAVEL = 1.45
CLAMP_TRAVEL = 0.45
EAR_T = 0.008
FIT_GAP = 0.001
ADJUSTER_Y = 0.060
ADJUSTER_TRAVEL = 0.020

BED_HEIGHT: dict[FrameForm, float] = {
    "plain_bed": 0.055,
    "bench_top": 0.075,
    "floor_stand": 0.300,
}


@dataclass(frozen=True)
class Config:
    frame_form: FrameForm = "plain_bed"
    clamp_form: ClampForm = "plain_clamp_bar"
    leaf_form: LeafForm = "plain_leaf"
    accessory: Accessory = "bend_stop_fence"
    clamp_station_count: int = 2
    leaf_rib_count: int = 3
    brake_width_m: float | None = None
    bed_depth_m: float | None = None
    leaf_length_m: float | None = None
    palette_style: PaletteStyle = "works_red"
    name: str = "pictureX_0611_hand_operated_metal_brake_for_bending_sheet_metal"


@dataclass(frozen=True)
class ResolvedConfig:
    frame_form: FrameForm
    clamp_form: ClampForm
    leaf_form: LeafForm
    accessory: Accessory
    clamp_station_count: int
    leaf_rib_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    brake_width_m: float
    bed_depth_m: float
    leaf_length_m: float
    bed_height_m: float
    clamp_hinge_y_m: float
    clamp_hinge_z_m: float
    clamp_reach_m: float
    station_pitch_m: float
    station_span_m: float
    rib_pitch_m: float
    rib_span_m: float
    fold_travel_rad: float
    accessory_station_y_m: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x4A_31_C8_6F)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        frame_form=choices["frame_form"],
        clamp_form=choices["clamp_form"],
        leaf_form=choices["leaf_form"],
        accessory=choices["accessory"],
        clamp_station_count=choices["clamp_station_count"],
        leaf_rib_count=choices["leaf_rib_count"],
        brake_width_m=round(rng.uniform(0.30, 0.70), 4),
        bed_depth_m=round(rng.uniform(0.100, 0.200), 4),
        leaf_length_m=round(rng.uniform(0.060, 0.140), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"metal_brake_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "frame_form": config.frame_form,
            "clamp_form": config.clamp_form,
            "leaf_form": config.leaf_form,
            "accessory": config.accessory,
            "clamp_station_count": config.clamp_station_count,
            "leaf_rib_count": config.leaf_rib_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.brake_width_m is not None and not 0.30 <= float(config.brake_width_m) <= 0.70:
        raise ValueError("brake_width_m must be in [0.30, 0.70]")
    if config.bed_depth_m is not None and not 0.100 <= float(config.bed_depth_m) <= 0.200:
        raise ValueError("bed_depth_m must be in [0.100, 0.200]")
    if config.leaf_length_m is not None and not 0.060 <= float(config.leaf_length_m) <= 0.140:
        raise ValueError("leaf_length_m must be in [0.060, 0.140]")

    width = (
        _clamp(config.brake_width_m, 0.30, 0.70) if config.brake_width_m is not None else 0.50
    )
    depth = (
        _clamp(config.bed_depth_m, 0.100, 0.200) if config.bed_depth_m is not None else 0.150
    )
    leaf = (
        _clamp(config.leaf_length_m, 0.060, 0.140)
        if config.leaf_length_m is not None
        else 0.100
    )
    bed_z = BED_HEIGHT[config.frame_form]
    stations = int(config.clamp_station_count)
    ribs = int(config.leaf_rib_count)
    station_span = width - 0.080
    rib_span = width - 0.060
    return ResolvedConfig(
        frame_form=config.frame_form,
        clamp_form=config.clamp_form,
        leaf_form=config.leaf_form,
        accessory=config.accessory,
        clamp_station_count=stations,
        leaf_rib_count=ribs,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        brake_width_m=width,
        bed_depth_m=depth,
        leaf_length_m=leaf,
        bed_height_m=bed_z,
        clamp_hinge_y_m=-(depth - 0.015),
        clamp_hinge_z_m=bed_z + CLAMP_LIFT_Z + 0.5 * CLAMP_BEAM_H,
        clamp_reach_m=depth - 0.035,
        station_pitch_m=station_span / max(1, stations - 1),
        station_span_m=station_span,
        rib_pitch_m=rib_span / max(1, ribs - 1),
        rib_span_m=rib_span,
        fold_travel_rad=FOLD_TRAVEL,
        accessory_station_y_m=-(depth + ADJUSTER_Y),
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("frame_form", config.frame_form),
        ("clamp_form", config.clamp_form),
        ("leaf_form", config.leaf_form),
        ("accessory", config.accessory),
        ("clamp_station_count", config.clamp_station_count),
        ("leaf_rib_count", config.leaf_rib_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        name = f"mb_{r.palette_style}_{key}"
        model.material(name, rgba=rgba)
        mats[key] = name
    return mats


def _local_origin(origin: Origin | None, offset: tuple[float, float, float]) -> Origin:
    base = origin or Origin()
    return Origin(
        xyz=tuple(value - shift for value, shift in zip(base.xyz, offset)),
        rpy=base.rpy,
    )


_ZERO_OFFSET = (0.0, 0.0, 0.0)


def _station_x(r: ResolvedConfig, index: int) -> float:
    return -0.5 * r.station_span_m + index * r.station_pitch_m


def _frame_common(part, offset, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Bed plate, bending edge rail, both hinge forks, rear apron and adjuster posts."""
    w, d, z = r.brake_width_m, r.bed_depth_m, r.bed_height_m
    part.visual(
        Box((w, d, BED_T)),
        origin=_local_origin(Origin(xyz=(0.0, -0.5 * d, z - 0.5 * BED_T)), offset),
        material=mats["frame"],
        name="frame__bed_plate", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((w, EDGE_RAIL_D, 0.016)),
        origin=_local_origin(Origin(xyz=(0.0, -0.010, z - 0.008)), offset),
        material=mats["steel"],
        name="frame__bending_edge_rail", material_class_id="metal.steel_bare",
    )
    for apron_index, sx in enumerate((-1.0, 1.0)):
        part.visual(
            Box((0.030, 0.010, CLAMP_LIFT_Z + CLAMP_BEAM_H + 0.030)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        sx * (0.5 * w - 0.015),
                        -d + 0.005,
                        z + 0.5 * (CLAMP_LIFT_Z + CLAMP_BEAM_H + 0.030),
                    )
                ),
                offset,
            ),
            material=mats["frame"],
            name=f"frame__rear_apron_{apron_index}", material_class_id="metal.paint_coated",
        )
    for ear_index, sx in enumerate((-1.0, 1.0)):
        part.visual(
            Box((EAR_T, 0.030, 0.030)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        sx * (0.5 * w - 0.5 * EAR_T),
                        r.clamp_hinge_y_m,
                        r.clamp_hinge_z_m,
                    )
                ),
                offset,
            ),
            material=mats["frame"],
            name=f"frame__clamp_hinge_ear_{ear_index}", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((EAR_T, 0.026, 0.022)),
            origin=_local_origin(
                Origin(
                    xyz=(sx * (0.5 * w - 0.5 * EAR_T), LEAF_HINGE_Y, z - 0.006)
                ),
                offset,
            ),
            material=mats["frame"],
            name=f"frame__leaf_hinge_ear_{ear_index}", material_class_id="metal.paint_coated",
        )
    part.visual(
        Box((w, ADJUSTER_Y + 0.030, 0.012)),
        origin=_local_origin(
            Origin(xyz=(0.0, -d - 0.5 * ADJUSTER_Y, z - 0.006)), offset
        ),
        material=mats["frame"],
        name="frame__rear_shelf", material_class_id="metal.paint_coated",
    )
    for i in range(r.clamp_station_count):
        x = _station_x(r, i)
        part.visual(
            Box((0.016, 0.016, 0.070)),
            origin=_local_origin(
                Origin(xyz=(x, r.accessory_station_y_m, z + 0.029)), offset
            ),
            material=mats["frame"],
            name=f"frame__adjuster_post_{i}", material_class_id="metal.paint_coated",
        )


def _frame_form_plain_bed_build(part, offset, r: ResolvedConfig, mats) -> None:
    w, d, z = r.brake_width_m, r.bed_depth_m, r.bed_height_m
    for foot_index, sx in enumerate((-1.0, 1.0)):
        part.visual(
            Box((0.040, d + ADJUSTER_Y, z - BED_T)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        sx * (0.5 * w - 0.020),
                        -0.5 * (d + ADJUSTER_Y),
                        0.5 * (z - BED_T),
                    )
                ),
                offset,
            ),
            material=mats["frame"],
            name=f"frame_form__plain_bed__side_web_{foot_index}", material_class_id="metal.paint_coated",
        )


def _frame_form_bench_top_build(part, offset, r: ResolvedConfig, mats) -> None:
    w, d, z = r.brake_width_m, r.bed_depth_m, r.bed_height_m
    part.visual(
        Box((w + 0.040, d + ADJUSTER_Y + 0.040, 0.014)),
        origin=_local_origin(
            Origin(xyz=(0.0, -0.5 * (d + ADJUSTER_Y), 0.007)), offset
        ),
        material=mats["frame"],
        name="frame_form__bench_top__bench_pad", material_class_id="metal.paint_coated",
    )
    for lug_index, (sx, sy) in enumerate(((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0))):
        part.visual(
            Cylinder(radius=0.010, length=0.010),
            origin=_local_origin(
                Origin(
                    xyz=(
                        sx * (0.5 * w + 0.012),
                        -0.5 * (d + ADJUSTER_Y)
                        + sy * 0.5 * (d + ADJUSTER_Y + 0.012),
                        0.018,
                    )
                ),
                offset,
            ),
            material=mats["dark"],
            name=f"frame_form__bench_top__bolt_lug_{lug_index}", material_class_id="metal.blackened_gunmetal",
        )
    for post_index, sx in enumerate((-1.0, 1.0)):
        part.visual(
            Box((0.036, d + ADJUSTER_Y, z - BED_T - 0.014)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        sx * (0.5 * w - 0.018),
                        -0.5 * (d + ADJUSTER_Y),
                        0.014 + 0.5 * (z - BED_T - 0.014),
                    )
                ),
                offset,
            ),
            material=mats["frame"],
            name=f"frame_form__bench_top__riser_{post_index}", material_class_id="metal.paint_coated",
        )


def _frame_form_floor_stand_build(part, offset, r: ResolvedConfig, mats) -> None:
    w, d, z = r.brake_width_m, r.bed_depth_m, r.bed_height_m
    for leg_index, (sx, sy) in enumerate(((-1.0, 0.0), (1.0, 0.0), (-1.0, 1.0), (1.0, 1.0))):
        top = (
            sx * (0.5 * w - 0.024),
            -0.020 - sy * (d - 0.040),
            z - BED_T,
        )
        foot = (
            sx * (0.5 * w + 0.030),
            -0.020 - sy * (d + 0.030),
            0.012,
        )
        _strut(
            part,
            offset,
            top,
            foot,
            0.010,
            mats["frame"],
            f"frame_form__floor_stand__leg_{leg_index}",
        )
    for rail_index, sy in enumerate((0.0, 1.0)):
        part.visual(
            Box((w + 0.040, 0.016, 0.016)),
            origin=_local_origin(
                Origin(xyz=(0.0, -0.020 - sy * (d + 0.010), 0.5 * z)), offset
            ),
            material=mats["frame"],
            name=f"frame_form__floor_stand__tie_rail_{rail_index}", material_class_id="metal.paint_coated",
        )
    part.visual(
        Box((0.020, d + 0.060, 0.016)),
        origin=_local_origin(
            Origin(xyz=(0.0, -0.020 - 0.5 * (d + 0.010), 0.5 * z)), offset
        ),
        material=mats["frame"],
        name="frame_form__floor_stand__spine_rail", material_class_id="metal.paint_coated",
    )


def _strut(part, offset, start, end, radius, material, name) -> None:
    dx, dy, dz = (end[i] - start[i] for i in range(3))
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 1e-6:
        return
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=_local_origin(
            Origin(
                xyz=(
                    start[0] + 0.5 * dx,
                    start[1] + 0.5 * dy,
                    start[2] + 0.5 * dz,
                ),
                rpy=(
                    0.0,
                    math.acos(_clamp(dz / length, -1.0, 1.0)),
                    math.atan2(dy, dx),
                ),
            ),
            offset,
        ),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


_FRAME_FORM_BUILDERS = {
    "plain_bed": _frame_form_plain_bed_build,
    "bench_top": _frame_form_bench_top_build,
    "floor_stand": _frame_form_floor_stand_build,
}


# --- clamp candidates -----------------------------------------------------------
def _clamp_common(part, offset, r: ResolvedConfig, mats) -> None:
    w = r.brake_width_m - 0.010
    y0 = r.clamp_hinge_y_m
    y1 = -0.020
    part.visual(
        Box((w, y1 - y0, CLAMP_BEAM_H)),
        origin=_local_origin(
            Origin(xyz=(0.0, 0.5 * (y0 + y1), r.clamp_hinge_z_m)), offset
        ),
        material=mats["frame"],
        name="clamp__beam", material_class_id="metal.paint_coated",
    )


def _clamp_form_plain_clamp_bar_build(part, offset, r: ResolvedConfig, mats) -> None:
    w = r.brake_width_m - 0.010
    part.visual(
        Box((w, CLAMP_NOSE_D, CLAMP_LIFT_Z + 0.001)),
        origin=_local_origin(
            Origin(
                xyz=(
                    0.0,
                    -0.020 - 0.5 * CLAMP_NOSE_D + 0.006,
                    r.bed_height_m + 0.5 * (CLAMP_LIFT_Z + 0.001),
                )
            ),
            offset,
        ),
        material=mats["steel"],
        name="clamp_form__plain_clamp_bar__nose", material_class_id="metal.steel_bare",
    )


def _clamp_form_segmented_clamp_build(part, offset, r: ResolvedConfig, mats) -> None:
    n = r.clamp_station_count
    seg_w = (r.brake_width_m - 0.010) / n - 0.004
    for i in range(n):
        x = -0.5 * (r.brake_width_m - 0.010) + (i + 0.5) * (r.brake_width_m - 0.010) / n
        part.visual(
            Box((seg_w, CLAMP_NOSE_D, CLAMP_LIFT_Z + 0.001)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        x,
                        -0.020 - 0.5 * CLAMP_NOSE_D + 0.006,
                        r.bed_height_m + 0.5 * (CLAMP_LIFT_Z + 0.001),
                    )
                ),
                offset,
            ),
            material=mats["steel"],
            name=f"clamp_form__segmented_clamp__segment_{i}", material_class_id="metal.steel_bare",
        )


def _clamp_form_finger_clamp_build(part, offset, r: ResolvedConfig, mats) -> None:
    n = r.clamp_station_count
    finger_w = min(0.060, 0.55 * r.station_pitch_m)
    for i in range(n):
        x = _station_x(r, i)
        part.visual(
            Box((finger_w, CLAMP_NOSE_D, CLAMP_LIFT_Z + 0.001)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        x,
                        -0.020 - 0.5 * CLAMP_NOSE_D + 0.006,
                        r.bed_height_m + 0.5 * (CLAMP_LIFT_Z + 0.001),
                    )
                ),
                offset,
            ),
            material=mats["steel"],
            name=f"clamp_form__finger_clamp__finger_{i}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Cylinder(radius=0.005, length=0.012),
            origin=_local_origin(
                Origin(
                    xyz=(
                        x,
                        -0.024,
                        r.clamp_hinge_z_m + 0.5 * CLAMP_BEAM_H + 0.004,
                    )
                ),
                offset,
            ),
            material=mats["dark"],
            name=f"clamp_form__finger_clamp__finger_bolt_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _clamp_form_screw_down_clamp_build(part, offset, r: ResolvedConfig, mats) -> None:
    w = r.brake_width_m - 0.010
    part.visual(
        Box((w, CLAMP_NOSE_D, CLAMP_LIFT_Z + 0.001)),
        origin=_local_origin(
            Origin(
                xyz=(
                    0.0,
                    -0.020 - 0.5 * CLAMP_NOSE_D + 0.006,
                    r.bed_height_m + 0.5 * (CLAMP_LIFT_Z + 0.001),
                )
            ),
            offset,
        ),
        material=mats["steel"],
        name="clamp_form__screw_down_clamp__nose", material_class_id="metal.steel_bare",
    )
    for i in range(r.clamp_station_count):
        x = _station_x(r, i)
        part.visual(
            Cylinder(radius=0.008, length=0.044),
            origin=_local_origin(
                Origin(
                    xyz=(
                        x,
                        -0.024,
                        r.clamp_hinge_z_m + 0.5 * CLAMP_BEAM_H + 0.018,
                    )
                ),
                offset,
            ),
            material=mats["steel"],
            name=f"clamp_form__screw_down_clamp__screw_{i}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Cylinder(radius=0.018, length=0.008),
            origin=_local_origin(
                Origin(
                    xyz=(
                        x,
                        -0.024,
                        r.clamp_hinge_z_m + 0.5 * CLAMP_BEAM_H + 0.044,
                    )
                ),
                offset,
            ),
            material=mats["accent"],
            name=f"clamp_form__screw_down_clamp__screw_knob_{i}", material_class_id="plastic.opaque_glossy_molded",
        )


_CLAMP_FORM_BUILDERS = {
    "plain_clamp_bar": _clamp_form_plain_clamp_bar_build,
    "segmented_clamp": _clamp_form_segmented_clamp_build,
    "finger_clamp": _clamp_form_finger_clamp_build,
    "screw_down_clamp": _clamp_form_screw_down_clamp_build,
}


# --- leaf candidates ------------------------------------------------------------
def _leaf_form_plain_leaf_build(part, offset, r: ResolvedConfig, mats) -> None:
    w = r.brake_width_m - 0.010
    z = r.bed_height_m - 0.006
    part.visual(
        Box((w, r.leaf_length_m, LEAF_T)),
        origin=_local_origin(
            Origin(xyz=(0.0, LEAF_HINGE_Y + 0.5 * r.leaf_length_m, z)), offset
        ),
        material=mats["steel"],
        name="leaf_form__plain_leaf__plate", material_class_id="metal.steel_bare",
    )
    for i in range(r.leaf_rib_count):
        x = -0.5 * r.rib_span_m + i * r.rib_pitch_m
        part.visual(
            Box((min(0.020, 0.4 * r.rib_pitch_m), r.leaf_length_m * 0.5, 0.008)),
            origin=_local_origin(
                Origin(xyz=(x, LEAF_HINGE_Y + 0.30 * r.leaf_length_m, z - 0.008)),
                offset,
            ),
            material=mats["steel"],
            name=f"leaf_form__leaf_rib_{i}", material_class_id="metal.steel_bare",
        )
    part.visual(
        Cylinder(radius=0.010, length=w * 0.4),
        origin=_local_origin(
            Origin(
                xyz=(0.0, LEAF_HINGE_Y + r.leaf_length_m - 0.010, z + 0.012),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            offset,
        ),
        material=mats["accent"],
        name="leaf_form__plain_leaf__lift_bar", material_class_id="metal.paint_coated",
    )


def _leaf_form_segmented_leaf_build(part, offset, r: ResolvedConfig, mats) -> None:
    w = r.brake_width_m - 0.010
    z = r.bed_height_m - 0.006
    n = r.leaf_rib_count
    seg_w = w / n - 0.004
    for i in range(n):
        x = -0.5 * w + (i + 0.5) * w / n
        part.visual(
            Box((seg_w, r.leaf_length_m, LEAF_T)),
            origin=_local_origin(
                Origin(xyz=(x, LEAF_HINGE_Y + 0.5 * r.leaf_length_m, z)), offset
            ),
            material=mats["steel"],
            name=f"leaf_form__segmented_leaf__segment_{i}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box((min(0.020, 0.4 * r.rib_pitch_m), r.leaf_length_m * 0.5, 0.010)),
            origin=_local_origin(
                Origin(xyz=(x, LEAF_HINGE_Y + 0.30 * r.leaf_length_m, z - 0.009)),
                offset,
            ),
            material=mats["steel"],
            name=f"leaf_form__leaf_rib_{i}", material_class_id="metal.steel_bare",
        )
    part.visual(
        Box((w, 0.016, LEAF_T)),
        origin=_local_origin(Origin(xyz=(0.0, LEAF_HINGE_Y + 0.008, z)), offset),
        material=mats["steel"],
        name="leaf_form__segmented_leaf__hinge_spine", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=0.010, length=w * 0.4),
        origin=_local_origin(
            Origin(
                xyz=(0.0, LEAF_HINGE_Y + r.leaf_length_m - 0.010, z + 0.012),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            offset,
        ),
        material=mats["accent"],
        name="leaf_form__segmented_leaf__lift_bar", material_class_id="metal.paint_coated",
    )


_LEAF_FORM_BUILDERS = {
    "plain_leaf": _leaf_form_plain_leaf_build,
    "segmented_leaf": _leaf_form_segmented_leaf_build,
}


# --- moving assemblies ----------------------------------------------------------
def _build_clamp(model, frame, r: ResolvedConfig, mats):
    hinge = (0.0, r.clamp_hinge_y_m, r.clamp_hinge_z_m)
    clamp = model.part("clamp_beam", meta={"role": "clamp"})
    _clamp_common(clamp, hinge, r, mats)
    _CLAMP_FORM_BUILDERS[r.clamp_form](clamp, hinge, r, mats)
    provider = AxisInterface(
        name="clamp_hinge_axis", point=hinge, axis=(1.0, 0.0, 0.0), radial=(0.0, 1.0, 0.0)
    )
    consumer = AxisInterface(
        name="clamp_pivot_axis", axis=(1.0, 0.0, 0.0), radial=(0.0, 1.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "frame_to_clamp",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=clamp,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=200.0, velocity=1.0, lower=0.0, upper=CLAMP_TRAVEL),
        motion_properties=MotionProperties(damping=1.0, friction=0.5),
        meta={"positive_motion": "lifts the clamp nose off the bed to load a sheet"},
    )
    register_interface_mate(model, "frame_to_clamp", mate)
    return clamp, hinge


def _build_leaf(model, frame, r: ResolvedConfig, mats):
    hinge = (0.0, LEAF_HINGE_Y, r.bed_height_m - 0.006)
    leaf = model.part("bending_leaf", meta={"role": "leaf"})
    _LEAF_FORM_BUILDERS[r.leaf_form](leaf, hinge, r, mats)
    provider = AxisInterface(
        name="leaf_hinge_axis", point=hinge, axis=(1.0, 0.0, 0.0), radial=(0.0, 1.0, 0.0)
    )
    consumer = AxisInterface(
        name="leaf_pivot_axis", axis=(1.0, 0.0, 0.0), radial=(0.0, 1.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "frame_to_leaf",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=leaf,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=260.0, velocity=1.0, lower=0.0, upper=r.fold_travel_rad
        ),
        motion_properties=MotionProperties(damping=1.2, friction=0.6),
        meta={"positive_motion": "folds the bending leaf up over the bending edge"},
    )
    register_interface_mate(model, "frame_to_leaf", mate)
    return leaf


def _lever_pivot_z(r: ResolvedConfig) -> float:
    return r.clamp_hinge_z_m + 0.5 * CLAMP_BEAM_H + 0.016


def _build_stations(model, frame, clamp, clamp_offset, r: ResolvedConfig, mats):
    handles, adjusters = [], []
    for i in range(r.clamp_station_count):
        x = _station_x(r, i)
        pivot = (x, r.clamp_hinge_y_m + 0.014, _lever_pivot_z(r))
        clamp.visual(
            Box((0.030, 0.024, 0.030)),
            origin=_local_origin(
                Origin(
                    xyz=(x, r.clamp_hinge_y_m + 0.014, r.clamp_hinge_z_m + 0.009)
                ),
                clamp_offset,
            ),
            material=mats["frame"],
            name=f"clamp__handle_boss_{i}", material_class_id="metal.paint_coated",
        )
        handle = model.part(f"handle_{i}", meta={"role": "handle"})
        tip = (x, r.clamp_hinge_y_m + 0.110, _lever_pivot_z(r) + 0.100)
        _strut(
            handle, pivot, pivot, tip, 0.008, mats["steel"], f"handle__lever_{i}"
        )
        handle.visual(
            Cylinder(radius=0.012, length=0.040),
            origin=_local_origin(
                Origin(xyz=tip, rpy=(0.0, math.pi / 2.0, 0.0)), pivot
            ),
            material=mats["accent"],
            name=f"handle__grip_{i}", material_class_id="rubber.smooth_plain",
        )
        provider = AxisInterface(
            name=f"handle_mount_axis_{i}",
            point=tuple(
                pivot[k] - (0.0, r.clamp_hinge_y_m, r.clamp_hinge_z_m)[k] for k in range(3)
            ),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 1.0, 0.0),
        )
        consumer = AxisInterface(
            name=f"handle_pivot_axis_{i}", axis=(1.0, 0.0, 0.0), radial=(0.0, 1.0, 0.0)
        )
        mate = mate_axes(provider, consumer)
        model.articulation(
            f"clamp_to_handle_{i}",
            ArticulationType.REVOLUTE,
            parent=clamp,
            child=handle,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(effort=60.0, velocity=2.0, lower=0.0, upper=1.20),
            meta={"positive_motion": "throws the cam handle back to release the clamp"},
        )
        register_interface_mate(model, f"clamp_to_handle_{i}", mate)
        handles.append(handle)

        base = (x, r.accessory_station_y_m - 0.0145, r.bed_height_m + 0.064)
        adjuster = model.part(f"adjuster_{i}", meta={"role": "adjuster"})
        adjuster.visual(
            Cylinder(radius=0.007, length=0.050),
            origin=_local_origin(Origin(xyz=base), base),
            material=mats["steel"],
            name=f"adjuster__screw_{i}", material_class_id="metal.steel_bare",
        )
        adjuster.visual(
            Cylinder(radius=0.016, length=0.008),
            origin=_local_origin(
                Origin(xyz=(base[0], base[1], base[2] + 0.028)), base
            ),
            material=mats["accent"],
            name=f"adjuster__knob_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            f"frame_to_adjuster_{i}",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=adjuster,
            origin=Origin(xyz=base),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=80.0, velocity=0.1, lower=-ADJUSTER_TRAVEL, upper=0.0
            ),
            meta={"positive_motion": "winds the stop screw back up out of the bed"},
        )
        adjusters.append(adjuster)
    return handles, adjusters


# --- accessory candidates -------------------------------------------------------
def _accessory_bend_stop_fence_build(model, frame, clamp, clamp_offset,
                                    r: ResolvedConfig, mats):
    w = r.brake_width_m
    rail_z = r.bed_height_m + 0.014
    for rail_index, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.010, 0.070, 0.008)),
            origin=Origin(
                xyz=(sx * (0.5 * w - 0.030), -r.bed_depth_m - 0.030, rail_z)
            ),
            material=mats["frame"],
            name=f"accessory__bend_stop_fence__slide_rail_{rail_index}", material_class_id="metal.paint_coated",
        )
        frame.visual(
            Box((0.010, 0.012, 0.030)),
            origin=Origin(
                xyz=(sx * (0.5 * w - 0.030), -r.bed_depth_m - 0.010, rail_z - 0.012)
            ),
            material=mats["frame"],
            name=f"accessory__bend_stop_fence__rail_post_{rail_index}", material_class_id="metal.paint_coated",
        )
    base = (0.0, -r.bed_depth_m - 0.030, rail_z)
    fence = model.part("accessory__bend_stop_fence__fence", meta={"role": "accessory"})
    fence.visual(
        Box((w - 0.050, 0.014, 0.010)),
        origin=_local_origin(Origin(xyz=(0.0, base[1], base[2] + 0.008)), base),
        material=mats["steel"],
        name="accessory__bend_stop_fence__fence_bar", material_class_id="metal.steel_bare",
    )
    fence.visual(
        Box((w - 0.050, 0.010, 0.026)),
        origin=_local_origin(
            Origin(xyz=(0.0, base[1] + 0.010, base[2] + 0.024)), base
        ),
        material=mats["steel"],
        name="accessory__bend_stop_fence__fence_blade", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "frame_to_accessory",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=fence,
        origin=Origin(xyz=base),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=40.0, velocity=0.2, lower=-0.020, upper=0.020),
        meta={"positive_motion": "slides the bend stop fence toward the bending edge"},
    )
    return (fence,)


def _accessory_center_lever_build(model, frame, clamp, clamp_offset,
                                  r: ResolvedConfig, mats):
    lever_x = _station_x(r, 0) + 0.5 * r.station_pitch_m
    pivot = (lever_x, r.clamp_hinge_y_m + 0.014, _lever_pivot_z(r) + 0.045)
    boss_top = pivot[2] - 0.004
    clamp.visual(
        Box((0.040, 0.024, boss_top - (r.clamp_hinge_z_m - 0.006))),
        origin=_local_origin(
            Origin(
                xyz=(
                    lever_x,
                    r.clamp_hinge_y_m + 0.014,
                    0.5 * (boss_top + r.clamp_hinge_z_m - 0.006),
                )
            ),
            clamp_offset,
        ),
        material=mats["frame"],
        name="accessory__center_lever__lever_boss", material_class_id="metal.paint_coated",
    )
    lever = model.part("accessory__center_lever__lever", meta={"role": "accessory"})
    tip = (lever_x, r.clamp_hinge_y_m + 0.164, pivot[2] + 0.150)
    lever.visual(
        Cylinder(radius=0.007, length=0.028),
        origin=_local_origin(
            Origin(xyz=pivot, rpy=(0.0, math.pi / 2.0, 0.0)), pivot
        ),
        material=mats["dark"],
        name="accessory__center_lever__knuckle", material_class_id="metal.blackened_gunmetal",
    )
    _strut(
        lever,
        pivot,
        pivot,
        tip,
        0.009,
        mats["steel"],
        "accessory__center_lever__lever_arm",
    )
    lever.visual(
        Cylinder(radius=0.014, length=0.060),
        origin=_local_origin(
            Origin(xyz=tip, rpy=(0.0, math.pi / 2.0, 0.0)), pivot
        ),
        material=mats["accent"],
        name="accessory__center_lever__grip", material_class_id="rubber.smooth_plain",
    )
    provider = AxisInterface(
        name="accessory_mount_axis",
        point=(lever_x, 0.014, _lever_pivot_z(r) + 0.045 - r.clamp_hinge_z_m),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 1.0, 0.0),
    )
    consumer = AxisInterface(
        name="accessory_pivot_axis", axis=(1.0, 0.0, 0.0), radial=(0.0, 1.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "frame_to_accessory",
        ArticulationType.REVOLUTE,
        parent=clamp,
        child=lever,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=90.0, velocity=2.0, lower=0.0, upper=1.20),
        meta={"positive_motion": "throws the centre lever back to release the clamp"},
    )
    register_interface_mate(model, "frame_to_accessory", mate)
    return (lever,)


_ACCESSORY_BUILDERS = {
    "bend_stop_fence": _accessory_bend_stop_fence_build,
    "center_lever": _accessory_center_lever_build,
}


def build_pictureX_0611_hand_operated_metal_brake_for_bending_sheet_metal(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_hand_operated_metal_brake_for_bending_sheet_metal",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "clamp beam and bending leaf hinged on one bed",
        },
    )
    mats = _materials(model, r)
    frame = model.part("frame", meta={"role": "frame"})
    _frame_common(frame, _ZERO_OFFSET, r, mats)
    _FRAME_FORM_BUILDERS[r.frame_form](frame, _ZERO_OFFSET, r, mats)
    clamp, clamp_offset = _build_clamp(model, frame, r, mats)
    _build_leaf(model, frame, r, mats)
    _build_stations(model, frame, clamp, clamp_offset, r, mats)
    _ACCESSORY_BUILDERS[r.accessory](
        model, frame, clamp, clamp_offset, r, mats
    )

    risk: list[dict[str, float]] = [
        {"frame_to_clamp": 0.0, "frame_to_leaf": 0.0},
        {"frame_to_clamp": CLAMP_TRAVEL, "frame_to_leaf": 0.0},
        {"frame_to_clamp": 0.0, "frame_to_leaf": r.fold_travel_rad},
        {"frame_to_clamp": CLAMP_TRAVEL, "frame_to_leaf": r.fold_travel_rad},
    ]
    model.meta["risk_poses"] = tuple(risk)
    return model


def build_seeded_pictureX_0611_hand_operated_metal_brake_for_bending_sheet_metal(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_pictureX_0611_hand_operated_metal_brake_for_bending_sheet_metal(
        config_from_seed(seed), assets=assets
    )


# --- authored tests --------------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_pictureX_0611_hand_operated_metal_brake_for_bending_sheet_metal_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    frames = _parts_by_role(model, "frame")
    clamps = _parts_by_role(model, "clamp")
    leaves = _parts_by_role(model, "leaf")
    handles = _parts_by_role(model, "handle")
    adjusters = _parts_by_role(model, "adjuster")
    joints = {j.name: j for j in model.articulations}
    clamp_joint = joints.get("frame_to_clamp")
    leaf_joint = joints.get("frame_to_leaf")

    ctx.check(
        "category_anchor: a clamp beam and a bending leaf hinge on the same grounded bed",
        len(frames) == 1
        and len(clamps) == 1
        and len(leaves) == 1
        and len(handles) == r.clamp_station_count
        and len(adjusters) == r.clamp_station_count
        and bool(model.root_parts())
        and model.root_parts()[0].name == "frame"
        and clamp_joint is not None
        and leaf_joint is not None
        and clamp_joint.articulation_type == ArticulationType.REVOLUTE
        and leaf_joint.articulation_type == ArticulationType.REVOLUTE
        and clamp_joint.parent == "frame"
        and leaf_joint.parent == "frame"
        and tuple(round(abs(v), 6) for v in leaf_joint.axis) == (1.0, 0.0, 0.0)
        and tuple(round(abs(v), 6) for v in clamp_joint.axis) == (1.0, 0.0, 0.0),
        details=(
            f"frames={len(frames)} clamps={len(clamps)} leaves={len(leaves)} "
            f"handles={len(handles)} adjusters={len(adjusters)} joints={sorted(joints)}"
        ),
    )

    fold_reach = r.leaf_length_m * math.cos(r.fold_travel_rad)
    ctx.check(
        "category_anchor: the leaf folds up without ever reaching back under the clamp nose",
        abs(leaf_joint.motion_limits.upper - r.fold_travel_rad) < 1e-9
        and abs(leaf_joint.motion_limits.lower) < 1e-9
        and fold_reach + LEAF_HINGE_Y > -0.019
        and abs(r.clamp_reach_m - (r.bed_depth_m - 0.035)) < 1e-9
        and abs(r.clamp_hinge_y_m + (r.bed_depth_m - 0.015)) < 1e-9
        and r.station_pitch_m > 0.060
        and r.rib_pitch_m > 0.035
        and abs(r.bed_height_m - BED_HEIGHT[r.frame_form]) < 1e-9,
        details=(
            f"fold={r.fold_travel_rad} reach={fold_reach} clamp_reach={r.clamp_reach_m} "
            f"station_pitch={r.station_pitch_m} rib_pitch={r.rib_pitch_m}"
        ),
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}

    def count(fragment: str) -> int:
        return sum(1 for n in visual_names if fragment in n)

    frame_ok = {
        "plain_bed": count("plain_bed__side_web_") == 2,
        "bench_top": count("bench_top__bolt_lug_") == 4
        and any("bench_top__bench_pad" in n for n in visual_names),
        "floor_stand": count("floor_stand__leg_") == 4
        and count("floor_stand__tie_rail_") == 2,
    }[r.frame_form]
    ctx.check(
        "category_anchor: frame_form identity",
        frame_ok
        and any("frame__bending_edge_rail" in n for n in visual_names)
        and count("frame__clamp_hinge_ear_") == 2
        and count("frame__rear_apron_") == 2
        and count("frame__leaf_hinge_ear_") == 2
        and count("frame__adjuster_post_") == r.clamp_station_count,
        details=f"frame_form={r.frame_form} bed_z={r.bed_height_m}",
    )

    n = r.clamp_station_count
    clamp_ok = {
        "plain_clamp_bar": any("plain_clamp_bar__nose" in x for x in visual_names),
        "segmented_clamp": count("segmented_clamp__segment_") == n,
        "finger_clamp": count("finger_clamp__finger_") == 2 * n,
        "screw_down_clamp": count("screw_down_clamp__screw_") == 2 * n,
    }[r.clamp_form]
    ctx.check(
        "category_anchor: clamp_form identity",
        clamp_ok
        and any("clamp__beam" in x for x in visual_names)
        and count("handle__lever_") == n
        and count("adjuster__screw_") == n,
        details=f"clamp_form={r.clamp_form} stations={n}",
    )

    leaf_ok = {
        "plain_leaf": any("plain_leaf__plate" in x for x in visual_names)
        and any("plain_leaf__lift_bar" in x for x in visual_names),
        "segmented_leaf": count("segmented_leaf__segment_") == r.leaf_rib_count
        and any("segmented_leaf__hinge_spine" in x for x in visual_names),
    }[r.leaf_form]
    ctx.check(
        "category_anchor: leaf_form identity",
        leaf_ok and count("leaf_form__leaf_rib_") == r.leaf_rib_count,
        details=f"leaf_form={r.leaf_form} ribs={r.leaf_rib_count}",
    )

    accessory_joint = joints.get("frame_to_accessory")
    accessory_ok = {
        "bend_stop_fence": accessory_joint is not None
        and accessory_joint.articulation_type == ArticulationType.PRISMATIC
        and any("bend_stop_fence__fence_blade" in x for x in visual_names),
        "center_lever": accessory_joint is not None
        and accessory_joint.articulation_type == ArticulationType.REVOLUTE
        and accessory_joint.parent == "clamp_beam"
        and any("center_lever__lever_arm" in x for x in visual_names),
    }[r.accessory]
    ctx.check(
        "category_anchor: accessory identity",
        accessory_ok,
        details=f"accessory={r.accessory}",
    )

    # Motion evidence: the fold really swings the leaf up off the bed.
    rest = ctx.part_world_aabb(leaves[0])
    with ctx.pose({leaf_joint: r.fold_travel_rad}):
        folded = ctx.part_world_aabb(leaves[0])
    ctx.check(
        "the fold swings the bending leaf up off the bed",
        rest is not None
        and folded is not None
        and folded[1][2] > rest[1][2] + 0.5 * r.leaf_length_m,
        details=f"rest={rest} folded={folded}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "widest_floor_stand_four_stations",
        {
            "frame_form": "floor_stand",
            "clamp_form": "finger_clamp",
            "leaf_form": "segmented_leaf",
            "accessory": "bend_stop_fence",
            "clamp_station_count": 4,
            "leaf_rib_count": 7,
            "brake_width_m": 0.70,
            "bed_depth_m": 0.200,
            "leaf_length_m": 0.140,
        },
        reason="the widest brake on the tallest stand with the most fingers, ribs and the "
        "longest leaf",
    ),
    corner_case(
        "narrowest_plain_two_stations",
        {
            "frame_form": "plain_bed",
            "clamp_form": "plain_clamp_bar",
            "leaf_form": "plain_leaf",
            "accessory": "center_lever",
            "clamp_station_count": 2,
            "leaf_rib_count": 3,
            "brake_width_m": 0.30,
            "bed_depth_m": 0.100,
            "leaf_length_m": 0.060,
        },
        reason="the smallest brake with the shallowest bed and shortest leaf",
    ),
    corner_case(
        "narrow_bench_four_stations",
        {
            "frame_form": "bench_top",
            "clamp_form": "screw_down_clamp",
            "leaf_form": "segmented_leaf",
            "accessory": "center_lever",
            "clamp_station_count": 4,
            "leaf_rib_count": 7,
            "brake_width_m": 0.30,
            "bed_depth_m": 0.100,
            "leaf_length_m": 0.140,
        },
        reason="the tightest station and rib pitch — four screws and seven ribs on the "
        "narrowest bench brake",
    ),
    corner_case(
        "wide_bench_deep_bed_stop",
        {
            "frame_form": "bench_top",
            "clamp_form": "segmented_clamp",
            "leaf_form": "plain_leaf",
            "accessory": "bend_stop_fence",
            "clamp_station_count": 2,
            "leaf_rib_count": 3,
            "brake_width_m": 0.70,
            "bed_depth_m": 0.200,
            "leaf_length_m": 0.060,
        },
        reason="the deepest bed with the shortest leaf and the longest stop fence",
    ),
    corner_case(
        "floor_stand_shallow_bed_center_lever",
        {
            "frame_form": "floor_stand",
            "clamp_form": "plain_clamp_bar",
            "leaf_form": "plain_leaf",
            "accessory": "center_lever",
            "clamp_station_count": 3,
            "leaf_rib_count": 5,
            "brake_width_m": 0.50,
            "bed_depth_m": 0.100,
            "leaf_length_m": 0.140,
        },
        reason="the shallowest bed at full standing height with the longest leaf and the "
        "centre lever",
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
    "build_pictureX_0611_hand_operated_metal_brake_for_bending_sheet_metal",
    "build_seeded_pictureX_0611_hand_operated_metal_brake_for_bending_sheet_metal",
    "run_pictureX_0611_hand_operated_metal_brake_for_bending_sheet_metal_tests",
]
