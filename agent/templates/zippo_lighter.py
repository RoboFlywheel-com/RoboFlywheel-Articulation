# SPDX-License-Identifier: Apache-2.0

"""Zippo lighter — modular mixed-slot procedural template.

Slot graph:

  body_case (root case)
    ├─ lid (REVOLUTE flip-top)
    ├─ insert_module (FIXED, PRISMATIC, or fused into case)
    │    └─ spark_wheel (CONTINUOUS)
    └─ cam_lever (optional REVOLUTE + Mimic, parented to lid or insert)

The spec is intentionally not a linear chain: lid, insert, wheel, and the
optional cam are parallel/mechanical children of the lower case or insert.
This template therefore uses slot/module factories directly while still
exporting the modular coverage contract (`__modular__` and
`slot_choices_for_seed`).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    KnobGeometry,
    KnobGrip,
    MatingContract,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True


BodyCaseModule = Literal["cadquery_shell_cup", "primitive_wall_box", "open_shell_box_helper"]
InsertModule = Literal["fixed_chimney_insert", "prismatic_sliding_insert", "fused_no_insert"]
LidModule = Literal["cadquery_shell_lid_yhinge", "primitive_wall_lid_yhinge"]
SparkWheelModule = Literal[
    "grooved_cylinder_wheel",
    "knurled_knob_wheel",
    "toothed_spark_wheel",
    "band_cylinder_wheel",
]
CamLeverModule = Literal["none", "cam_on_lid", "cam_on_insert"]
PaletteTheme = Literal["brushed_chrome", "black_ice", "brass_insert", "worn_steel"]


PALETTES: dict[PaletteTheme, dict[str, tuple[float, float, float, float]]] = {
    "brushed_chrome": {
        "shell": (0.78, 0.79, 0.78, 1.0),
        "insert": (0.64, 0.66, 0.66, 1.0),
        "dark_steel": (0.16, 0.17, 0.18, 1.0),
        "wick": (0.78, 0.72, 0.58, 1.0),
        "soot": (0.025, 0.022, 0.020, 1.0),
        "brass": (0.78, 0.58, 0.22, 1.0),
        "cam": (0.55, 0.56, 0.55, 1.0),
    },
    "black_ice": {
        "shell": (0.035, 0.037, 0.040, 1.0),
        "insert": (0.56, 0.58, 0.60, 1.0),
        "dark_steel": (0.08, 0.08, 0.09, 1.0),
        "wick": (0.80, 0.72, 0.55, 1.0),
        "soot": (0.010, 0.010, 0.012, 1.0),
        "brass": (0.74, 0.50, 0.18, 1.0),
        "cam": (0.42, 0.43, 0.45, 1.0),
    },
    "brass_insert": {
        "shell": (0.74, 0.55, 0.22, 1.0),
        "insert": (0.70, 0.72, 0.70, 1.0),
        "dark_steel": (0.12, 0.12, 0.13, 1.0),
        "wick": (0.82, 0.74, 0.54, 1.0),
        "soot": (0.030, 0.025, 0.018, 1.0),
        "brass": (0.86, 0.62, 0.24, 1.0),
        "cam": (0.60, 0.50, 0.34, 1.0),
    },
    "worn_steel": {
        "shell": (0.48, 0.50, 0.50, 1.0),
        "insert": (0.66, 0.68, 0.68, 1.0),
        "dark_steel": (0.11, 0.12, 0.13, 1.0),
        "wick": (0.74, 0.66, 0.50, 1.0),
        "soot": (0.02, 0.02, 0.02, 1.0),
        "brass": (0.72, 0.52, 0.18, 1.0),
        "cam": (0.50, 0.52, 0.52, 1.0),
    },
}


@dataclass(frozen=True)
class ZippoLighterConfig:
    body_case_module: BodyCaseModule | None = None
    insert_module: InsertModule | None = None
    lid_module: LidModule | None = None
    spark_wheel_module: SparkWheelModule | None = None
    cam_lever_module: CamLeverModule | None = None

    palette_theme: PaletteTheme = "brushed_chrome"
    case_w: float = 0.038
    case_d: float = 0.013
    case_h: float = 0.040
    lid_h: float = 0.017
    wall: float = 0.0009
    corner_r: float = 0.0013
    hinge_r: float = 0.0011
    lid_open_upper: float = 1.95
    wheel_r: float = 0.0035
    wheel_len: float = 0.0058
    axle_r: float = 0.0008
    vent_hole_rows: int = 3
    name: str = "zippo_lighter"
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["brushed_chrome"])
    )


@dataclass(frozen=True)
class ResolvedZippoLighterConfig:
    body_case_module: BodyCaseModule
    insert_module: InsertModule
    lid_module: LidModule
    spark_wheel_module: SparkWheelModule
    cam_lever_module: CamLeverModule
    palette_theme: PaletteTheme
    case_w: float
    case_d: float
    case_h: float
    lid_h: float
    wall: float
    corner_r: float
    hinge_r: float
    lid_open_upper: float
    wheel_r: float
    wheel_len: float
    axle_r: float
    vent_hole_rows: int
    name: str
    palette: dict[str, tuple[float, float, float, float]]


def _weighted_choice(rng: random.Random, weighted: tuple[tuple[str, int], ...]) -> str:
    total = sum(weight for _, weight in weighted)
    pick = rng.uniform(0.0, float(total))
    acc = 0.0
    for name, weight in weighted:
        acc += float(weight)
        if pick <= acc:
            return name
    return weighted[-1][0]


def _module_choices_for_seed(
    seed: int,
) -> tuple[
    BodyCaseModule,
    InsertModule,
    LidModule,
    SparkWheelModule,
    CamLeverModule,
]:
    seeded_coverage: dict[int, tuple[str, str, str, str, str]] = {
        0: (
            "cadquery_shell_cup",
            "fixed_chimney_insert",
            "cadquery_shell_lid_yhinge",
            "grooved_cylinder_wheel",
            "none",
        ),
        1: (
            "primitive_wall_box",
            "prismatic_sliding_insert",
            "primitive_wall_lid_yhinge",
            "knurled_knob_wheel",
            "none",
        ),
        2: (
            "open_shell_box_helper",
            "fused_no_insert",
            "cadquery_shell_lid_yhinge",
            "band_cylinder_wheel",
            "cam_on_lid",
        ),
        3: (
            "cadquery_shell_cup",
            "prismatic_sliding_insert",
            "cadquery_shell_lid_yhinge",
            "toothed_spark_wheel",
            "cam_on_lid",
        ),
        4: (
            "open_shell_box_helper",
            "fixed_chimney_insert",
            "primitive_wall_lid_yhinge",
            "band_cylinder_wheel",
            "cam_on_insert",
        ),
        5: (
            "primitive_wall_box",
            "fixed_chimney_insert",
            "cadquery_shell_lid_yhinge",
            "band_cylinder_wheel",
            "cam_on_lid",
        ),
        6: (
            "open_shell_box_helper",
            "prismatic_sliding_insert",
            "primitive_wall_lid_yhinge",
            "grooved_cylinder_wheel",
            "none",
        ),
        7: (
            "cadquery_shell_cup",
            "fused_no_insert",
            "primitive_wall_lid_yhinge",
            "knurled_knob_wheel",
            "cam_on_lid",
        ),
        8: (
            "primitive_wall_box",
            "fused_no_insert",
            "primitive_wall_lid_yhinge",
            "toothed_spark_wheel",
            "none",
        ),
        9: (
            "open_shell_box_helper",
            "fixed_chimney_insert",
            "cadquery_shell_lid_yhinge",
            "knurled_knob_wheel",
            "cam_on_insert",
        ),
    }
    if seed in seeded_coverage:
        return seeded_coverage[seed]  # type: ignore[return-value]

    rng = random.Random(seed)
    body = _weighted_choice(
        rng,
        (
            ("cadquery_shell_cup", 3),
            ("primitive_wall_box", 3),
            ("open_shell_box_helper", 3),
        ),
    )
    insert = _weighted_choice(
        rng,
        (
            ("fixed_chimney_insert", 6),
            ("prismatic_sliding_insert", 7),
            ("fused_no_insert", 6),
        ),
    )
    lid = _weighted_choice(
        rng,
        (
            ("cadquery_shell_lid_yhinge", 6),
            ("primitive_wall_lid_yhinge", 6),
        ),
    )
    wheel = _weighted_choice(
        rng,
        (
            ("grooved_cylinder_wheel", 5),
            ("knurled_knob_wheel", 5),
            ("toothed_spark_wheel", 4),
            ("band_cylinder_wheel", 4),
        ),
    )
    cam_weights: tuple[tuple[str, int], ...]
    if insert == "fused_no_insert":
        cam_weights = (("none", 7), ("cam_on_lid", 7))
    else:
        cam_weights = (("none", 7), ("cam_on_lid", 7), ("cam_on_insert", 5))
    cam = _weighted_choice(rng, cam_weights)
    return (  # type: ignore[return-value]
        body,
        insert,
        lid,
        wheel,
        cam,
    )


def config_from_seed(seed: int) -> ZippoLighterConfig:
    if seed == 0:
        return ZippoLighterConfig(
            body_case_module="cadquery_shell_cup",
            insert_module="fixed_chimney_insert",
            lid_module="cadquery_shell_lid_yhinge",
            spark_wheel_module="grooved_cylinder_wheel",
            cam_lever_module="none",
            palette_theme="brushed_chrome",
            case_w=0.038,
            case_d=0.013,
            case_h=0.040,
            lid_h=0.017,
            wall=0.0009,
            corner_r=0.0013,
            hinge_r=0.0011,
            lid_open_upper=1.95,
            wheel_r=0.0035,
            wheel_len=0.0058,
            axle_r=0.0008,
            vent_hole_rows=3,
            name="zippo_lighter_anchor",
        )

    rng = random.Random(seed)
    body, insert, lid, wheel, cam = _module_choices_for_seed(seed)
    display_presets: dict[int, tuple[PaletteTheme, float, float, float, float, int]] = {
        1: ("black_ice", 0.034, 0.011, 0.041, 0.018, 4),
        2: ("brass_insert", 0.040, 0.015, 0.043, 0.019, 2),
        3: ("worn_steel", 0.031, 0.0105, 0.038, 0.015, 4),
        4: ("brass_insert", 0.039, 0.0145, 0.042, 0.0185, 3),
        5: ("black_ice", 0.036, 0.012, 0.039, 0.016, 2),
        6: ("worn_steel", 0.040, 0.0135, 0.043, 0.018, 4),
        7: ("brass_insert", 0.033, 0.0115, 0.040, 0.019, 3),
        8: ("black_ice", 0.038, 0.014, 0.042, 0.017, 4),
        9: ("worn_steel", 0.035, 0.0125, 0.039, 0.0155, 2),
    }
    preset = display_presets.get(seed)
    if preset is not None:
        palette_theme, case_w, case_d, case_h, lid_h, vent_rows = preset
    else:
        palette_theme = rng.choice(tuple(PALETTES.keys()))
        case_w = round(rng.uniform(0.030, 0.040), 4)
        case_d = round(rng.uniform(0.010, 0.015), 4)
        case_h = round(rng.uniform(0.038, 0.043), 4)
        lid_h = round(rng.uniform(0.015, 0.019), 4)
        vent_rows = rng.randint(2, 4)
    return ZippoLighterConfig(
        body_case_module=body,
        insert_module=insert,
        lid_module=lid,
        spark_wheel_module=wheel,
        cam_lever_module=cam,
        palette_theme=palette_theme,
        case_w=case_w,
        case_d=case_d,
        case_h=case_h,
        lid_h=lid_h,
        wall=round(rng.uniform(0.0006, 0.0012), 5),
        corner_r=round(rng.uniform(0.0009, 0.0018), 5),
        hinge_r=round(rng.uniform(0.0009, 0.0013), 5),
        lid_open_upper=round(rng.uniform(1.75, 1.95), 3),
        wheel_r=round(rng.uniform(0.0030, 0.0040), 5),
        wheel_len=round(rng.uniform(0.0048, 0.0064), 5),
        axle_r=round(rng.uniform(0.0006, 0.0010), 5),
        vent_hole_rows=vent_rows,
        name=f"seeded_zippo_lighter_{seed}",
    )


def resolve_config(config: ZippoLighterConfig) -> ResolvedZippoLighterConfig:
    body = config.body_case_module or "cadquery_shell_cup"
    insert = config.insert_module or "fixed_chimney_insert"
    lid = config.lid_module or "cadquery_shell_lid_yhinge"
    wheel = config.spark_wheel_module or "grooved_cylinder_wheel"
    cam = config.cam_lever_module or "none"

    if body not in ("cadquery_shell_cup", "primitive_wall_box", "open_shell_box_helper"):
        raise ValueError(f"Unsupported body_case_module: {body}")
    if insert not in ("fixed_chimney_insert", "prismatic_sliding_insert", "fused_no_insert"):
        raise ValueError(f"Unsupported insert_module: {insert}")
    if lid not in ("cadquery_shell_lid_yhinge", "primitive_wall_lid_yhinge"):
        raise ValueError(f"Unsupported lid_module: {lid}")
    if wheel not in (
        "grooved_cylinder_wheel",
        "knurled_knob_wheel",
        "toothed_spark_wheel",
        "band_cylinder_wheel",
    ):
        raise ValueError(f"Unsupported spark_wheel_module: {wheel}")
    if cam not in ("none", "cam_on_lid", "cam_on_insert"):
        raise ValueError(f"Unsupported cam_lever_module: {cam}")
    if insert == "fused_no_insert" and cam == "cam_on_insert":
        raise ValueError("cam_on_insert is invalid when insert_module=fused_no_insert")
    if config.palette_theme not in PALETTES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    case_w = max(0.030, min(float(config.case_w), 0.040))
    case_d = max(0.010, min(float(config.case_d), 0.015))
    case_h = max(0.038, min(float(config.case_h), 0.043))
    lid_h = max(0.015, min(float(config.lid_h), 0.019))
    wall = max(0.0006, min(float(config.wall), 0.0012))
    corner_r = max(0.0007, min(float(config.corner_r), 0.0020))
    hinge_r = max(0.0008, min(float(config.hinge_r), 0.0014))
    wheel_r = max(0.0030, min(float(config.wheel_r), 0.0040))
    wheel_len = max(0.0045, min(float(config.wheel_len), 0.0066))
    axle_r = max(0.00055, min(float(config.axle_r), 0.0011))

    return ResolvedZippoLighterConfig(
        body_case_module=body,  # type: ignore[arg-type]
        insert_module=insert,  # type: ignore[arg-type]
        lid_module=lid,  # type: ignore[arg-type]
        spark_wheel_module=wheel,  # type: ignore[arg-type]
        cam_lever_module=cam,  # type: ignore[arg-type]
        palette_theme=config.palette_theme,
        case_w=case_w,
        case_d=case_d,
        case_h=case_h,
        lid_h=lid_h,
        wall=wall,
        corner_r=min(corner_r, min(case_w, case_d) * 0.18),
        hinge_r=hinge_r,
        lid_open_upper=max(1.75, min(float(config.lid_open_upper), 1.95)),
        wheel_r=wheel_r,
        wheel_len=wheel_len,
        axle_r=axle_r,
        vent_hole_rows=max(2, min(int(config.vent_hole_rows), 4)),
        name=config.name,
        palette=dict(PALETTES[config.palette_theme]),
    )


def _hinge_x(r: ResolvedZippoLighterConfig) -> float:
    return -r.case_w * 0.5 - r.hinge_r * 0.78


def _wheel_origin_in_insert(r: ResolvedZippoLighterConfig) -> tuple[float, float, float]:
    return (-r.case_w * 0.18, 0.0, r.case_h - r.wall + 0.0068)


def _wheel_origin_in_case(r: ResolvedZippoLighterConfig) -> tuple[float, float, float]:
    x, y, z = _wheel_origin_in_insert(r)
    return (x, y, z + r.wall)


def _cyl_y(radius: float, length: float, center: tuple[float, float, float]) -> cq.Workplane:
    return cq.Workplane("XZ").circle(radius).extrude(length / 2.0, both=True).translate(center)


def _cyl_x(radius: float, length: float, center: tuple[float, float, float]) -> cq.Workplane:
    return cq.Workplane("YZ").circle(radius).extrude(length / 2.0, both=True).translate(center)


def _box(size: tuple[float, float, float], center: tuple[float, float, float]) -> cq.Workplane:
    return cq.Workplane("XY").box(*size).translate(center)


def _cq_lower_shell(r: ResolvedZippoLighterConfig, *, open_helper: bool = False) -> cq.Workplane:
    outer = cq.Workplane("XY").box(r.case_w, r.case_d, r.case_h, centered=(True, True, False))
    outer = outer.edges("|Z").fillet(r.corner_r * (0.72 if open_helper else 1.0))
    inner = (
        cq.Workplane("XY")
        .box(
            r.case_w - 2.0 * r.wall,
            r.case_d - 2.0 * r.wall,
            r.case_h + 0.004,
            centered=(True, True, False),
        )
        .translate((0.0, 0.0, r.wall))
    )
    return outer.cut(inner)


def _cq_body_hinge(r: ResolvedZippoLighterConfig, *, five_knuckle: bool = False) -> cq.Workplane:
    hx = _hinge_x(r)
    body = cq.Workplane("XY")
    if five_knuckle:
        centers = (-0.0046, 0.0, 0.0046)
        length = min(0.0025, r.case_d * 0.18)
    else:
        centers = (0.0,)
        length = r.case_d * 0.46
    for idx, y in enumerate(centers):
        tab = _box(
            (r.hinge_r * 2.1, length + 0.00035, 0.0032),
            (-r.case_w * 0.5 - r.hinge_r * 0.28, y, r.case_h - 0.0013),
        )
        barrel = _cyl_y(r.hinge_r, length, (hx, y, r.case_h))
        body = body.union(tab).union(barrel) if idx else tab.union(barrel)
    return body


def _cq_lid_shell(r: ResolvedZippoLighterConfig, *, open_helper: bool = False) -> cq.Workplane:
    outer = (
        cq.Workplane("XY")
        .box(r.case_w, r.case_d, r.lid_h, centered=(True, True, False))
        .translate((r.case_w * 0.5 + r.hinge_r * 0.70, 0.0, 0.0))
    )
    outer = outer.edges("|Z").fillet(r.corner_r * (0.65 if open_helper else 1.0))
    inner = (
        cq.Workplane("XY")
        .box(
            r.case_w - 2.0 * r.wall,
            r.case_d - 2.0 * r.wall,
            r.lid_h + 0.004,
            centered=(True, True, False),
        )
        .translate((r.case_w * 0.5 + r.hinge_r * 0.70, 0.0, -0.003))
    )
    return outer.cut(inner)


def _cq_lid_hinge(r: ResolvedZippoLighterConfig, *, split: bool = True) -> cq.Workplane:
    if split:
        y_off = r.case_d * 0.31
        centers = (-y_off, y_off)
        length = r.case_d * 0.20
    else:
        centers = (0.0,)
        length = r.case_d * 0.46
    result = cq.Workplane("XY")
    for idx, y in enumerate(centers):
        lug = _box((r.hinge_r * 2.4, length + 0.0003, 0.0030), (r.hinge_r * 0.55, y, 0.0013))
        barrel = _cyl_y(r.hinge_r, length, (0.0, y, 0.0))
        result = result.union(lug).union(barrel) if idx else lug.union(barrel)
    return result


def _cq_grooved_wheel(r: ResolvedZippoLighterConfig) -> cq.Workplane:
    wheel = _cyl_y(r.wheel_r, r.wheel_len, (0.0, 0.0, 0.0))
    axle = _cyl_y(r.axle_r, r.wheel_len * 1.22, (0.0, 0.0, 0.0))
    groove = _box(
        (0.00075, r.wheel_len + 0.002, r.wheel_r * 2.25),
        (r.wheel_r - 0.00025, 0.0, 0.0),
    )
    for angle_deg in range(0, 180, 12):
        wheel = wheel.cut(groove.rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), angle_deg))
    return wheel.union(axle)


def _cq_toothed_wheel(r: ResolvedZippoLighterConfig) -> cq.Workplane:
    thickness = r.wheel_len
    wheel = cq.Workplane("XY").circle(r.wheel_r).extrude(thickness / 2.0, both=True)
    for i in range(18):
        angle = 2.0 * math.pi * i / 18
        tooth = (
            cq.Workplane("XY")
            .box(0.00095, 0.00105, thickness, centered=(True, True, True))
            .translate((0.0, r.wheel_r + 0.00036, 0.0))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(angle))
        )
        wheel = wheel.union(tooth)
    axle = cq.Workplane("XY").circle(r.axle_r).extrude(thickness * 1.22 / 2.0, both=True)
    return wheel.union(axle)


def _add_insert_floor(case, r: ResolvedZippoLighterConfig) -> None:
    case.visual(
        Box((r.case_w - 2.0 * r.wall, r.case_d - 2.0 * r.wall, r.wall * 1.8)),
        origin=Origin(xyz=(0.0, 0.0, r.wall * 0.55)),
        material="shell",
        name="insert_floor", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )


def _build_body_cadquery_shell_cup(
    model: ArticulatedObject, r: ResolvedZippoLighterConfig, assets: AssetContext | None
) -> None:
    case = model.part("case")
    case.visual(
        mesh_from_cadquery(
            _cq_lower_shell(r),
            "zippo_body_shell",
            assets=assets,
            tolerance=0.00035,
            angular_tolerance=0.10,
        ),
        material="shell",
        name="body_shell", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    case.visual(
        mesh_from_cadquery(
            _cq_body_hinge(r),
            "zippo_body_hinge",
            assets=assets,
            tolerance=0.00025,
            angular_tolerance=0.08,
        ),
        material="shell",
        name="body_hinge", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    _add_insert_floor(case, r)
    for side, y in (("front", r.case_d * 0.5 - 0.00032), ("rear", -r.case_d * 0.5 + 0.00032)):
        # These dark seam/inset lines must PIERCE the outer shell face — a box
        # buried entirely inside the (meshed) wall solid never touches the shell
        # surface and reads as a disconnected island. Y-thickness is sized so the
        # outer edge protrudes ~0.2mm past the nominal face while the inner edge
        # still sits in the wall (surfaces intersect => connected).
        case.visual(
            Box((r.case_w * 0.78, 0.0011, 0.0014)),
            origin=Origin(xyz=(0.0, y, r.case_h - 0.0024)),
            material="dark_steel",
            name=f"{side}_cap_seam_shadow", material_class_id="metal.blackened_gunmetal",
        )
        case.visual(
            Box((r.case_w * 0.52, 0.0010, 0.0012)),
            origin=Origin(xyz=(0.0, y, r.case_h * 0.46)),
            material="dark_steel",
            name=f"{side}_brushed_inset_line", material_class_id="metal.blackened_gunmetal",
        )
    case.inertial = Inertial.from_geometry(
        Box((r.case_w, r.case_d, r.case_h)),
        mass=0.065,
        origin=Origin(xyz=(0.0, 0.0, r.case_h * 0.5)),
    )


def _build_body_primitive_wall_box(
    model: ArticulatedObject, r: ResolvedZippoLighterConfig, assets: AssetContext | None
) -> None:
    del assets
    case = model.part("case")
    case.visual(
        Box((r.case_w, r.case_d, r.wall * 1.8)),
        origin=Origin(xyz=(0.0, 0.0, r.wall * 0.6)),
        material="shell",
        name="insert_floor", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    case.visual(
        Box((r.case_w, r.wall * 1.35, r.case_h)),
        origin=Origin(xyz=(0.0, r.case_d * 0.5 - r.wall * 0.50, r.case_h * 0.5)),
        material="shell",
        name="front_wall", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    case.visual(
        Box((r.case_w, r.wall * 1.35, r.case_h)),
        origin=Origin(xyz=(0.0, -r.case_d * 0.5 + r.wall * 0.50, r.case_h * 0.5)),
        material="shell",
        name="rear_wall", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    case.visual(
        Box((r.wall * 1.35, r.case_d, r.case_h)),
        origin=Origin(xyz=(r.case_w * 0.5 - r.wall * 0.50, 0.0, r.case_h * 0.5)),
        material="shell",
        name="right_wall", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    case.visual(
        Box((r.wall * 1.35, r.case_d, r.case_h)),
        origin=Origin(xyz=(-r.case_w * 0.5 + r.wall * 0.50, 0.0, r.case_h * 0.5)),
        material="shell",
        name="left_wall", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    corner_r = max(r.corner_r, r.wall * 1.1)
    for idx, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
        case.visual(
            Cylinder(radius=corner_r, length=r.case_h),
            origin=Origin(
                xyz=(
                    sx * (r.case_w * 0.5 - corner_r),
                    sy * (r.case_d * 0.5 - corner_r),
                    r.case_h * 0.5,
                )
            ),
            material="shell",
            name=f"body_corner_{idx}", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
        )
    for side, y in (
        ("front", r.case_d * 0.5 - r.wall * 0.82),
        ("rear", -r.case_d * 0.5 + r.wall * 0.82),
    ):
        for idx, x in enumerate((-r.case_w * 0.24, 0.0, r.case_w * 0.24)):
            case.visual(
                Box((0.0017, r.wall * 1.4, r.case_h * 0.76)),
                origin=Origin(xyz=(x, y, r.case_h * 0.44)),
                material="dark_steel",
                name=f"{side}_pressed_rib_{idx}", material_class_id="metal.blackened_gunmetal",
            )
    case.visual(
        Box((r.case_w * 0.78, r.wall * 1.5, 0.0016)),
        origin=Origin(xyz=(0.0, r.case_d * 0.5 - r.wall * 0.82, r.case_h - 0.0028)),
        material="dark_steel",
        name="front_lid_seam", material_class_id="metal.blackened_gunmetal",
    )
    case.visual(
        Box((r.case_w * 0.78, r.wall * 1.5, 0.0016)),
        origin=Origin(xyz=(0.0, -r.case_d * 0.5 + r.wall * 0.82, r.case_h - 0.0028)),
        material="dark_steel",
        name="rear_lid_seam", material_class_id="metal.blackened_gunmetal",
    )
    case.visual(
        Box((r.hinge_r * 2.6, r.case_d * 0.76, 0.0042)),
        origin=Origin(xyz=(-r.case_w * 0.5 - r.hinge_r * 0.22, 0.0, r.case_h - 0.0012)),
        material="shell",
        name="body_hinge_pad", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    for idx, y in enumerate((-r.case_d * 0.24, r.case_d * 0.24)):
        case.visual(
            Cylinder(radius=r.hinge_r, length=r.case_d * 0.22),
            origin=Origin(xyz=(_hinge_x(r), y, r.case_h), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="shell",
            name=f"body_knuckle_{idx}", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
        )
    case.inertial = Inertial.from_geometry(
        Box((r.case_w, r.case_d, r.case_h)),
        mass=0.068,
        origin=Origin(xyz=(0.0, 0.0, r.case_h * 0.5)),
    )


def _build_body_open_shell_box_helper(
    model: ArticulatedObject, r: ResolvedZippoLighterConfig, assets: AssetContext | None
) -> None:
    case = model.part("case")
    case.visual(
        mesh_from_cadquery(
            _cq_lower_shell(r, open_helper=True),
            "zippo_open_shell_helper_case",
            assets=assets,
            tolerance=0.00035,
            angular_tolerance=0.10,
        ),
        material="shell",
        name="body_shell", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    case.visual(
        mesh_from_cadquery(
            _cq_body_hinge(r, five_knuckle=True),
            "zippo_open_shell_helper_hinge",
            assets=assets,
            tolerance=0.00025,
            angular_tolerance=0.08,
        ),
        material="shell",
        name="body_hinge", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    _add_insert_floor(case, r)
    lip_z = r.case_h - 0.00075
    case.visual(
        Box((r.case_w * 0.82, r.wall * 1.8, 0.0024)),
        origin=Origin(xyz=(0.0, r.case_d * 0.5 - r.wall * 0.70, lip_z)),
        material="dark_steel",
        name="open_front_top_lip", material_class_id="metal.blackened_gunmetal",
    )
    case.visual(
        Box((r.case_w * 0.82, r.wall * 1.8, 0.0024)),
        origin=Origin(xyz=(0.0, -r.case_d * 0.5 + r.wall * 0.70, lip_z)),
        material="dark_steel",
        name="open_rear_top_lip", material_class_id="metal.blackened_gunmetal",
    )
    for x, name in (
        (r.case_w * 0.5 - r.wall * 0.65, "open_right_top_lip"),
        (-r.case_w * 0.5 + r.wall * 0.65, "open_left_top_lip"),
    ):
        case.visual(
            Box((r.wall * 1.8, r.case_d * 0.72, 0.0024)),
            origin=Origin(xyz=(x, 0.0, lip_z)),
            material="dark_steel",
            name=name, material_class_id="metal.blackened_gunmetal",
        )
    case.inertial = Inertial.from_geometry(
        Box((r.case_w, r.case_d, r.case_h)),
        mass=0.064,
        origin=Origin(xyz=(0.0, 0.0, r.case_h * 0.5)),
    )


def _add_insert_visuals(part, r: ResolvedZippoLighterConfig, *, prefix: str = "") -> None:
    fuel_h = r.case_h - r.wall + 0.001
    insert_w = r.case_w * 0.62
    insert_d = r.case_d * 0.66
    part.visual(
        Box((insert_w, insert_d, fuel_h)),
        origin=Origin(xyz=(0.0, 0.0, fuel_h * 0.5)),
        material="insert",
        name=f"{prefix}fuel_can", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Box((insert_w * 1.06, insert_d * 1.12, 0.0016)),
        origin=Origin(xyz=(0.0, 0.0, fuel_h + 0.00025)),
        material="insert",
        name=f"{prefix}top_deck", material_class_id="metal.stainless_matte",
    )
    chimney_h = r.lid_h * 0.82
    chimney_z = fuel_h + chimney_h * 0.5
    wall = max(r.wall * 0.72, 0.00045)
    for side, y in (("front", -insert_d * 0.54), ("rear", insert_d * 0.54)):
        part.visual(
            Box((insert_w * 0.72, wall, chimney_h)),
            origin=Origin(xyz=(0.0012, y, chimney_z)),
            material="insert",
            name=f"{prefix}{side}_chimney_wall", material_class_id="metal.stainless_matte",
        )
        idx = 0
        for row in range(r.vent_hole_rows):
            z = fuel_h + 0.0032 + row * (chimney_h - 0.0064) / max(r.vent_hole_rows - 1, 1)
            for x in (-0.006, -0.002, 0.002, 0.006):
                # Vent holes are centered ON the chimney-wall midplane and made
                # long enough (0.0010) to pierce BOTH wall faces for any wall
                # thickness (0.00045..~0.00086). A short disc sitting just off the
                # outer face floated as a disconnected island on thin-wall seeds.
                part.visual(
                    Cylinder(radius=0.00055, length=0.0010),
                    origin=Origin(
                        xyz=(x, y, z),
                        rpy=(math.pi / 2.0, 0.0, 0.0),
                    ),
                    material="soot",
                    name=f"{prefix}{side}_vent_{idx}", material_class_id="metal.blackened_gunmetal",
                )
                idx += 1
    part.visual(
        Box((wall * 1.5, insert_d * 1.04, chimney_h)),
        origin=Origin(xyz=(-insert_w * 0.35, 0.0, chimney_z)),
        material="insert",
        name=f"{prefix}flint_side_wall", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Box((wall * 1.5, insert_d * 1.04, chimney_h)),
        origin=Origin(xyz=(insert_w * 0.42, 0.0, chimney_z)),
        material="insert",
        name=f"{prefix}wick_side_wall", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Cylinder(radius=0.00082, length=0.0115),
        origin=Origin(xyz=(insert_w * 0.20, 0.0, fuel_h + 0.0048)),
        material="wick",
        name=f"{prefix}wick", material_class_id="fabric.thread_yarn",
    )
    wheel_x, _, wheel_z = _wheel_origin_in_insert(r)
    part.visual(
        Box((0.0040, insert_d * 0.72, 0.0062)),
        origin=Origin(xyz=(wheel_x, 0.0, wheel_z - 0.0032)),
        material="insert",
        name=f"{prefix}striker_fork", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Cylinder(radius=r.axle_r * 1.35, length=insert_d * 0.74),
        origin=Origin(xyz=(wheel_x, 0.0, wheel_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="insert",
        name=f"{prefix}wheel_axle_boss", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Box((0.0042, insert_d * 0.62, 0.0046)),
        origin=Origin(xyz=(-insert_w * 0.48, 0.0, fuel_h + 0.0030)),
        material="insert",
        name=f"{prefix}insert_cam_boss", material_class_id="metal.stainless_matte",
    )
    # Crown bar spanning from over the wick to the wick_side_wall. It must reach
    # the wick_side_wall (x=insert_w*0.42) so it is not a floating island — the
    # old narrow bar stopped short (gap to wick/wick_side_wall). The side wall
    # spans the full chimney height in z, so overlapping it in x guarantees a
    # 3D intersection regardless of case proportions.
    part.visual(
        Box((insert_w * 0.44, insert_d * 0.16, 0.0026)),
        origin=Origin(xyz=(insert_w * 0.26, 0.0, fuel_h + chimney_h - 0.0020)),
        material="brass",
        name=f"{prefix}wick_crown_bridge", material_class_id="metal.brass_polished",
    )


def _build_fixed_chimney_insert(
    model: ArticulatedObject, r: ResolvedZippoLighterConfig, assets: AssetContext | None
) -> str:
    del assets
    case = model.get_part("case")
    insert = model.part("insert")
    _add_insert_visuals(insert, r)
    insert.visual(
        Box((r.case_w * 0.34, r.case_d * 0.78, 0.0022)),
        origin=Origin(xyz=(0.0, 0.0, r.case_h + 0.0030)),
        material="brass",
        name="fixed_insert_polished_cap", material_class_id="metal.brass_polished",
    )
    insert.inertial = Inertial.from_geometry(
        Box((r.case_w * 0.62, r.case_d * 0.66, r.case_h + r.lid_h * 0.70)),
        mass=0.036,
        origin=Origin(xyz=(0.0, 0.0, r.case_h * 0.5)),
    )
    model.articulation(
        "insert_mount",
        ArticulationType.FIXED,
        parent=case,
        child=insert,
        origin=Origin(xyz=(0.0, 0.0, r.wall)),
        mating=MatingContract(
            parent_face_geometry="insert_floor",
            parent_face_side="positive_z",
            child_face_geometry="fuel_can",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
    )
    return "insert"


def _build_prismatic_sliding_insert(
    model: ArticulatedObject, r: ResolvedZippoLighterConfig, assets: AssetContext | None
) -> str:
    del assets
    case = model.get_part("case")
    insert = model.part("insert")
    _add_insert_visuals(insert, r)
    rail_z = r.case_h * 0.48
    for side, x in (("left", -r.case_w * 0.27), ("right", r.case_w * 0.27)):
        insert.visual(
            Box((0.00072, r.case_d * 0.52, r.case_h * 0.72)),
            origin=Origin(xyz=(x, 0.0, rail_z)),
            material="brass",
            name=f"{side}_spring_rail", material_class_id="metal.brass_polished",
        )
    # Rear shadow channel hugging the fuel_can rear face (y=-insert_d*0.5 =
    # -case_d*0.33). It must touch the fuel_can, otherwise it floats behind it as
    # a disconnected island — the old y=-case_d*0.40 left a ~0.3mm gap.
    insert.visual(
        Box((r.case_w * 0.58, 0.0010, r.case_h * 0.58)),
        origin=Origin(xyz=(0.0, -r.case_d * 0.33 - 0.0002, r.case_h * 0.43)),
        material="dark_steel",
        name="sliding_insert_shadow_channel", material_class_id="metal.blackened_gunmetal",
    )
    insert.inertial = Inertial.from_geometry(
        Box((r.case_w * 0.64, r.case_d * 0.70, r.case_h + r.lid_h * 0.70)),
        mass=0.038,
        origin=Origin(xyz=(0.0, 0.0, r.case_h * 0.5)),
    )
    model.articulation(
        "insert_slide",
        ArticulationType.PRISMATIC,
        parent=case,
        child=insert,
        origin=Origin(xyz=(0.0, 0.0, r.wall)),
        axis=(0.0, 0.0, 1.0),
        # Insert lift capped low: the raised fuel-can/chimney otherwise pokes
        # into the flip-top lid (which motion-QC poses independently) as the lid
        # swings through its mid-open arc. 0.010m keeps the raised insert clear
        # of the lid's swept envelope across the whole lid arc (derived from
        # insert-vs-lid clearance) while still exercising a meaningful slide.
        motion_limits=MotionLimits(effort=8.0, velocity=0.20, lower=0.0, upper=0.010),
        mating=MatingContract(
            parent_face_geometry="insert_floor",
            parent_face_side="positive_z",
            child_face_geometry="fuel_can",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
    )
    return "insert"


def _build_fused_no_insert(
    model: ArticulatedObject, r: ResolvedZippoLighterConfig, assets: AssetContext | None
) -> str:
    del assets
    case = model.get_part("case")
    _add_insert_visuals(case, r, prefix="fused_")
    wx, wy, wz = _wheel_origin_in_case(r)
    case.visual(
        Box((0.0060, r.case_d * 0.54, 0.0060)),
        origin=Origin(xyz=(wx, wy, wz - 0.0025)),
        material="insert",
        name="fused_wheel_support", material_class_id="metal.stainless_matte",
    )
    case.visual(
        Box((r.case_w * 0.36, r.case_d * 0.82, 0.0030)),
        origin=Origin(xyz=(0.0010, 0.0, r.case_h + r.lid_h * 0.70)),
        material="brass",
        name="fused_chimney_crown", material_class_id="metal.brass_polished",
    )
    return "case"


def _add_lid_cam_boss(lid, r: ResolvedZippoLighterConfig) -> None:
    lid.visual(
        Box((0.0046, r.case_d * 0.46, 0.0044)),
        origin=Origin(xyz=(r.hinge_r * 1.2, 0.0, 0.0048)),
        material="shell",
        name="cam_boss", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )


def _build_lid_cadquery_shell_yhinge(
    model: ArticulatedObject, r: ResolvedZippoLighterConfig, assets: AssetContext | None
) -> None:
    case = model.get_part("case")
    lid = model.part("lid")
    lid.visual(
        mesh_from_cadquery(
            _cq_lid_shell(r),
            "zippo_lid_shell",
            assets=assets,
            tolerance=0.00035,
            angular_tolerance=0.10,
        ),
        material="shell",
        name="lid_shell", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    lid.visual(
        mesh_from_cadquery(
            _cq_lid_hinge(r),
            "zippo_lid_hinge",
            assets=assets,
            tolerance=0.00025,
            angular_tolerance=0.08,
        ),
        material="shell",
        name="lid_hinge_barrels", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    _add_lid_cam_boss(lid, r)
    # Highlight lines must pierce the (meshed) lid shell face — Y-thickness sized
    # so the outer edge protrudes slightly past the nominal face while the inner
    # edge stays in the wall, so the surfaces intersect (not a buried island).
    lid.visual(
        Box((r.case_w * 0.68, 0.0011, 0.0012)),
        origin=Origin(
            xyz=(r.case_w * 0.5 + r.hinge_r * 0.70, r.case_d * 0.5 - 0.00035, r.lid_h * 0.54)
        ),
        material="dark_steel",
        name="lid_front_highlight_line", material_class_id="metal.blackened_gunmetal",
    )
    lid.visual(
        Box((r.case_w * 0.68, 0.0011, 0.0012)),
        origin=Origin(
            xyz=(r.case_w * 0.5 + r.hinge_r * 0.70, -r.case_d * 0.5 + 0.00035, r.lid_h * 0.54)
        ),
        material="dark_steel",
        name="lid_rear_highlight_line", material_class_id="metal.blackened_gunmetal",
    )
    lid.inertial = Inertial.from_geometry(
        Box((r.case_w, r.case_d, r.lid_h)),
        mass=0.026,
        origin=Origin(xyz=(r.case_w * 0.5, 0.0, r.lid_h * 0.5)),
    )
    model.articulation(
        "lid_hinge",
        ArticulationType.REVOLUTE,
        parent=case,
        child=lid,
        origin=Origin(xyz=(_hinge_x(r), 0.0, r.case_h)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=1.5, velocity=8.0, lower=0.0, upper=r.lid_open_upper),
    )


def _build_lid_primitive_wall_yhinge(
    model: ArticulatedObject, r: ResolvedZippoLighterConfig, assets: AssetContext | None
) -> None:
    del assets
    case = model.get_part("case")
    lid = model.part("lid")
    x0 = r.case_w * 0.5 + r.hinge_r * 0.70
    lid.visual(
        Box((r.case_w, r.case_d, r.wall * 1.6)),
        origin=Origin(xyz=(x0, 0.0, r.lid_h - r.wall * 0.6)),
        material="shell",
        name="lid_top", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    lid.visual(
        Box((r.case_w, r.wall * 1.35, r.lid_h)),
        origin=Origin(xyz=(x0, r.case_d * 0.5 - r.wall * 0.5, r.lid_h * 0.5)),
        material="shell",
        name="lid_front_wall", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    lid.visual(
        Box((r.case_w, r.wall * 1.35, r.lid_h)),
        origin=Origin(xyz=(x0, -r.case_d * 0.5 + r.wall * 0.5, r.lid_h * 0.5)),
        material="shell",
        name="lid_rear_wall", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    lid.visual(
        Box((r.wall * 1.35, r.case_d, r.lid_h)),
        origin=Origin(xyz=(r.hinge_r * 0.70 + r.wall * 0.5, 0.0, r.lid_h * 0.5)),
        material="shell",
        name="lid_left_wall", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    lid.visual(
        Box((r.wall * 1.35, r.case_d, r.lid_h)),
        origin=Origin(xyz=(r.case_w + r.hinge_r * 0.70 - r.wall * 0.5, 0.0, r.lid_h * 0.5)),
        material="shell",
        name="lid_right_wall", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    lid.visual(
        Box((r.hinge_r * 2.5, r.case_d * 0.54, 0.0038)),
        origin=Origin(xyz=(r.hinge_r * 0.55, 0.0, 0.0014)),
        material="shell",
        name="lid_hinge_pad", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    lid.visual(
        Cylinder(radius=r.hinge_r, length=r.case_d * 0.40),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="shell",
        name="lid_knuckle", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"brushed_chrome", "black_ice", "worn_steel"} else "metal.brass_aged"),
    )
    _add_lid_cam_boss(lid, r)
    lid.inertial = Inertial.from_geometry(
        Box((r.case_w, r.case_d, r.lid_h)),
        mass=0.027,
        origin=Origin(xyz=(r.case_w * 0.5, 0.0, r.lid_h * 0.5)),
    )
    model.articulation(
        "lid_hinge",
        ArticulationType.REVOLUTE,
        parent=case,
        child=lid,
        origin=Origin(xyz=(_hinge_x(r), 0.0, r.case_h)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=1.5, velocity=7.0, lower=0.0, upper=r.lid_open_upper),
    )


def _build_wheel_grooved(
    model: ArticulatedObject,
    r: ResolvedZippoLighterConfig,
    assets: AssetContext | None,
    *,
    parent_name: str,
) -> None:
    parent = model.get_part(parent_name)
    wheel = model.part("spark_wheel")
    wheel.visual(
        mesh_from_cadquery(
            _cq_grooved_wheel(r),
            "zippo_grooved_spark_wheel",
            assets=assets,
            tolerance=0.00018,
            angular_tolerance=0.08,
        ),
        material="dark_steel",
        name="wheel_body", material_class_id="metal.blackened_gunmetal",
    )
    _emit_wheel_joint(model, r, parent, parent_name)


def _build_wheel_knurled(
    model: ArticulatedObject,
    r: ResolvedZippoLighterConfig,
    assets: AssetContext | None,
    *,
    parent_name: str,
) -> None:
    del assets
    parent = model.get_part(parent_name)
    wheel = model.part("spark_wheel")
    wheel.visual(
        mesh_from_geometry(
            KnobGeometry(
                diameter=r.wheel_r * 2.0,
                height=r.wheel_len,
                body_style="cylindrical",
                grip=KnobGrip(style="knurled", count=28, depth=0.00042, helix_angle_deg=24.0),
            ),
            "zippo_knurled_spark_wheel",
        ),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_steel",
        name="wheel_body", material_class_id="metal.blackened_gunmetal",
    )
    # Axle must protrude past the knob body ends (length > wheel_len) so it
    # reaches the axle bosses / is not buried inside the wheel as an island —
    # the old 0.88*wheel_len axle was shorter than the body and fully enclosed.
    wheel.visual(
        Cylinder(radius=r.axle_r, length=r.wheel_len * 1.22),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_steel",
        name="short_axle", material_class_id="metal.blackened_gunmetal",
    )
    _emit_wheel_joint(model, r, parent, parent_name)


def _build_wheel_toothed(
    model: ArticulatedObject,
    r: ResolvedZippoLighterConfig,
    assets: AssetContext | None,
    *,
    parent_name: str,
) -> None:
    parent = model.get_part(parent_name)
    wheel = model.part("spark_wheel")
    wheel.visual(
        mesh_from_cadquery(
            _cq_toothed_wheel(r),
            "zippo_toothed_spark_wheel",
            assets=assets,
            tolerance=0.00018,
            angular_tolerance=0.08,
        ),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_steel",
        name="wheel_body", material_class_id="metal.blackened_gunmetal",
    )
    _emit_wheel_joint(model, r, parent, parent_name)


def _build_wheel_band(
    model: ArticulatedObject,
    r: ResolvedZippoLighterConfig,
    assets: AssetContext | None,
    *,
    parent_name: str,
) -> None:
    del assets
    parent = model.get_part(parent_name)
    wheel = model.part("spark_wheel")
    wheel.visual(
        Cylinder(radius=r.wheel_r, length=r.wheel_len),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_steel",
        name="outer_band", material_class_id="metal.blackened_gunmetal",
    )
    wheel.visual(
        Cylinder(radius=r.wheel_r * 0.70, length=r.wheel_len * 1.08),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="brass",
        name="inner_core", material_class_id="metal.brass_polished",
    )
    wheel.visual(
        Cylinder(radius=r.axle_r, length=r.wheel_len * 1.20),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_steel",
        name="short_axle", material_class_id="metal.blackened_gunmetal",
    )
    _emit_wheel_joint(model, r, parent, parent_name)


def _emit_wheel_joint(
    model: ArticulatedObject,
    r: ResolvedZippoLighterConfig,
    parent,
    parent_name: str,
) -> None:
    origin = _wheel_origin_in_case(r) if parent_name == "case" else _wheel_origin_in_insert(r)
    model.articulation(
        "wheel_spin",
        ArticulationType.CONTINUOUS,
        parent=parent,
        child=model.get_part("spark_wheel"),
        origin=Origin(xyz=origin),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=0.3, velocity=32.0),
    )


def _build_cam_lever(
    model: ArticulatedObject,
    r: ResolvedZippoLighterConfig,
    *,
    parent_name: str,
) -> None:
    parent = model.get_part(parent_name)
    cam = model.part("cam_lever")
    cam.visual(
        Cylinder(radius=0.00155, length=r.case_d * 0.48),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="cam",
        name="cam_hub", material_class_id="metal.stainless_matte",
    )
    cam.visual(
        Box((0.0105, 0.0025, 0.0020)),
        origin=Origin(xyz=(0.0050, 0.0, 0.0005)),
        material="cam",
        name="cam_arm", material_class_id="metal.stainless_matte",
    )
    cam.visual(
        Box((0.0038, 0.0025, 0.0046)),
        origin=Origin(xyz=(0.0084, 0.0, -0.0012)),
        material="cam",
        name="cam_toe", material_class_id="metal.stainless_matte",
    )
    cam.inertial = Inertial.from_geometry(
        Box((0.012, 0.004, 0.006)),
        mass=0.004,
        origin=Origin(xyz=(0.004, 0.0, 0.0)),
    )
    if parent_name == "lid":
        origin = (r.hinge_r * 1.2, 0.0, 0.0048)
        multiplier = 0.55
        offset = -0.24
    else:
        fuel_h = r.case_h - r.wall + 0.001
        origin = (-r.case_w * 0.30, 0.0, fuel_h + 0.0030)
        multiplier = 0.45
        offset = 0.06
    model.articulation(
        "cam_pivot",
        ArticulationType.REVOLUTE,
        parent=parent,
        child=cam,
        origin=Origin(xyz=origin),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=0.2, velocity=10.0, lower=-0.35, upper=1.05),
        mimic=Mimic(joint="lid_hinge", multiplier=multiplier, offset=offset),
    )


BODY_FACTORIES = {
    "cadquery_shell_cup": _build_body_cadquery_shell_cup,
    "primitive_wall_box": _build_body_primitive_wall_box,
    "open_shell_box_helper": _build_body_open_shell_box_helper,
}

INSERT_FACTORIES = {
    "fixed_chimney_insert": _build_fixed_chimney_insert,
    "prismatic_sliding_insert": _build_prismatic_sliding_insert,
    "fused_no_insert": _build_fused_no_insert,
}

LID_FACTORIES = {
    "cadquery_shell_lid_yhinge": _build_lid_cadquery_shell_yhinge,
    "primitive_wall_lid_yhinge": _build_lid_primitive_wall_yhinge,
}

WHEEL_FACTORIES = {
    "grooved_cylinder_wheel": _build_wheel_grooved,
    "knurled_knob_wheel": _build_wheel_knurled,
    "toothed_spark_wheel": _build_wheel_toothed,
    "band_cylinder_wheel": _build_wheel_band,
}


def _slot_choices_for_resolved(r: ResolvedZippoLighterConfig) -> list[tuple[str, str]]:
    return [
        ("body_case", r.body_case_module),
        ("insert_module", r.insert_module),
        ("lid", r.lid_module),
        ("spark_wheel", r.spark_wheel_module),
        ("cam_lever", r.cam_lever_module),
    ]


def build_zippo_lighter(
    config: ZippoLighterConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    for name, rgba in r.palette.items():
        model.material(name, rgba=rgba)

    BODY_FACTORIES[r.body_case_module](model, r, assets)
    insert_parent_name = INSERT_FACTORIES[r.insert_module](model, r, assets)
    LID_FACTORIES[r.lid_module](model, r, assets)
    WHEEL_FACTORIES[r.spark_wheel_module](model, r, assets, parent_name=insert_parent_name)
    if r.cam_lever_module == "cam_on_lid":
        _build_cam_lever(model, r, parent_name="lid")
    elif r.cam_lever_module == "cam_on_insert":
        _build_cam_lever(model, r, parent_name="insert")

    model.meta["slot_choices"] = _slot_choices_for_resolved(r)
    return model


def build_seeded_zippo_lighter(seed: int) -> ArticulatedObject:
    return build_zippo_lighter(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return _slot_choices_for_resolved(resolve_config(config_from_seed(seed)))


def _visual_names(part) -> set[str]:
    return {v.name for v in part.visuals if v.name}


def _allow_if_present(
    ctx: TestContext,
    model: ArticulatedObject,
    parent_name: str,
    child_name: str,
    elem_a: str,
    elem_b: str,
    *,
    reason: str,
) -> None:
    part_names = {p.name for p in model.parts}
    if parent_name not in part_names or child_name not in part_names:
        return
    parent = model.get_part(parent_name)
    child = model.get_part(child_name)
    if elem_a in _visual_names(parent) and elem_b in _visual_names(child):
        ctx.allow_overlap(parent, child, elem_a=elem_a, elem_b=elem_b, reason=reason)


def _declare_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    # The removable/fixed insert lives inside the hollow metal case. Mesh-level
    # collision checks conservatively see the shell's bounding surface as
    # overlapping the insert can, so this is declared as intentional nesting.
    for case_elem in (
        "body_shell",
        "insert_floor",
        "front_wall",
        "rear_wall",
        "left_wall",
        "right_wall",
    ):
        for insert_elem in (
            "fuel_can",
            "top_deck",
            "left_spring_rail",
            "right_spring_rail",
            "sliding_insert_shadow_channel",
            "fixed_insert_polished_cap",
        ):
            _allow_if_present(
                ctx,
                model,
                "case",
                "insert",
                case_elem,
                insert_elem,
                reason="lighter insert nests inside the hollow lower fuel case",
            )
    for parent_elem in (
        "body_hinge",
        "body_hinge_pad",
        "body_knuckle_0",
        "body_knuckle_1",
    ):
        for child_elem in ("lid_hinge_barrels", "lid_knuckle"):
            _allow_if_present(
                ctx,
                model,
                "case",
                "lid",
                parent_elem,
                child_elem,
                reason="captured flip-top hinge barrel overlaps its case knuckle sleeve",
            )
    for parent_name, parent_elem in (
        ("insert", "wheel_axle_boss"),
        ("insert", "striker_fork"),
        ("case", "fused_wheel_axle_boss"),
        ("case", "fused_striker_fork"),
        ("case", "fused_wheel_support"),
    ):
        for child_elem in ("wheel_body", "short_axle", "outer_band", "inner_core"):
            _allow_if_present(
                ctx,
                model,
                parent_name,
                "spark_wheel",
                parent_elem,
                child_elem,
                reason="spark wheel axle is captured between chimney/fork cheeks",
            )
    _allow_if_present(
        ctx,
        model,
        "lid",
        "cam_lever",
        "cam_boss",
        "cam_hub",
        reason="cam hub rotates inside the lid cam boss",
    )
    _allow_if_present(
        ctx,
        model,
        "insert",
        "cam_lever",
        "insert_cam_boss",
        "cam_hub",
        reason="insert-mounted cam hub rotates inside the insert boss",
    )


def _expect_identity(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedZippoLighterConfig
) -> None:
    part_names = {p.name for p in model.parts}
    ctx.check("has_case_lid_wheel", {"case", "lid", "spark_wheel"} <= part_names, str(part_names))
    lid_joint = model.get_articulation("lid_hinge")
    wheel_joint = model.get_articulation("wheel_spin")
    ctx.check(
        "lid_is_revolute",
        lid_joint.articulation_type == ArticulationType.REVOLUTE,
        f"got {lid_joint.articulation_type}",
    )
    ctx.check(
        "wheel_is_continuous",
        wheel_joint.articulation_type == ArticulationType.CONTINUOUS,
        f"got {wheel_joint.articulation_type}",
    )
    if r.insert_module == "fused_no_insert":
        ctx.check("fused_has_no_insert_part", "insert" not in part_names, str(part_names))
        ctx.check(
            "fused_wheel_parent_is_case", wheel_joint.parent == "case", str(wheel_joint.parent)
        )
    else:
        ctx.check("independent_insert_exists", "insert" in part_names, str(part_names))
        ctx.check("insert_wheel_parent", wheel_joint.parent == "insert", str(wheel_joint.parent))
    if r.cam_lever_module != "none":
        cam_joint = model.get_articulation("cam_pivot")
        ctx.check("cam_has_mimic", cam_joint.mimic is not None, "cam_pivot mimic missing")


def _expect_size(ctx: TestContext, model: ArticulatedObject) -> None:
    case = model.get_part("case")
    aabb = ctx.part_world_aabb(case)
    if aabb is None:
        return
    sx = aabb[1][0] - aabb[0][0]
    sy = aabb[1][1] - aabb[0][1]
    sz = aabb[1][2] - aabb[0][2]
    ctx.check(
        "pocket_lighter_scale",
        0.028 <= sx <= 0.046 and 0.009 <= sy <= 0.018 and 0.037 <= sz <= 0.070,
        f"case extents x={sx:.4f} y={sy:.4f} z={sz:.4f}",
    )


def run_zippo_lighter_tests(
    model: ArticulatedObject,
    config: ZippoLighterConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    _declare_expected_overlaps(ctx, model)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    _expect_identity(ctx, model, r)
    _expect_size(ctx, model)
    return ctx.report()


__all__ = [
    "__modular__",
    "ZippoLighterConfig",
    "ResolvedZippoLighterConfig",
    "config_from_seed",
    "resolve_config",
    "build_zippo_lighter",
    "build_seeded_zippo_lighter",
    "slot_choices_for_seed",
    "run_zippo_lighter_tests",
]
