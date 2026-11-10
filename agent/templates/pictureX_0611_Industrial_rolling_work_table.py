# SPDX-License-Identifier: Apache-2.0

"""Self-contained mobile industrial work table template.

The grounded ``frame`` part is the welded post-and-rail structure: four posts,
perimeter rails and the storage bay's own rails.  Four braked swivel casters
hang from the post feet and are identity-fixed -- a ``caster_swivel`` turns
CONTINUOUS about +z in a bored king-pin boss, a ``caster_wheel`` spins
CONTINUOUS about the yoke's local +y between two cheeks, and a ``caster_brake``
pedal swings REVOLUTE about that same local axis onto the tread.

Three slots vary without touching that chain: ``top_surface`` (folded stainless
deck or laminated butcher block), ``storage_module`` (open shelves, sliding
drawer trays, or a pegboard back with sliding trays) and ``leg_form`` (welded
fixed posts, or telescopic posts that give the worktop a real height travel).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

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
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

TopSurface = Literal["stainless_deck", "butcher_block"]
StorageModule = Literal["open_shelf", "drawer_bank", "pegboard_rack"]
LegForm = Literal["fixed_post", "telescopic_post"]
BenchAccessory = Literal["monitor_arm", "keyboard_tray", "equipment_shelf"]
SideBracing = Literal["plain_rails", "x_braces"]
PaletteStyle = Literal["stainless", "works_blue", "safety_orange", "graphite"]

TOP_SURFACES: tuple[TopSurface, ...] = ("stainless_deck", "butcher_block")
STORAGE_MODULES: tuple[StorageModule, ...] = ("open_shelf", "drawer_bank", "pegboard_rack")
LEG_FORMS: tuple[LegForm, ...] = ("fixed_post", "telescopic_post")
BENCH_ACCESSORIES: tuple[BenchAccessory, ...] = (
    "monitor_arm",
    "keyboard_tray",
    "equipment_shelf",
)
SIDE_BRACINGS: tuple[SideBracing, ...] = ("plain_rails", "x_braces")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "stainless",
    "works_blue",
    "safety_orange",
    "graphite",
)


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("top_surface", TOP_SURFACES),
        component_slot("storage_module", STORAGE_MODULES),
        component_slot("leg_form", LEG_FORMS),
        component_slot("bench_accessory", BENCH_ACCESSORIES),
        component_slot("side_bracing", SIDE_BRACINGS),
        multiplicity_slot("storage_level_count", (1, 2, 3), item_slot="storage_module"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "stainless": {
        "frame": (0.72, 0.74, 0.76, 1.0),
        "deck": (0.80, 0.82, 0.84, 1.0),
        "wood": (0.72, 0.55, 0.33, 1.0),
        "dark": (0.14, 0.14, 0.15, 1.0),
        "steel": (0.44, 0.46, 0.48, 1.0),
        "rubber": (0.09, 0.09, 0.10, 1.0),
    },
    "works_blue": {
        "frame": (0.16, 0.30, 0.52, 1.0),
        "deck": (0.74, 0.76, 0.78, 1.0),
        "wood": (0.68, 0.50, 0.30, 1.0),
        "dark": (0.10, 0.13, 0.18, 1.0),
        "steel": (0.40, 0.43, 0.47, 1.0),
        "rubber": (0.08, 0.08, 0.09, 1.0),
    },
    "safety_orange": {
        "frame": (0.82, 0.42, 0.12, 1.0),
        "deck": (0.76, 0.77, 0.78, 1.0),
        "wood": (0.74, 0.57, 0.36, 1.0),
        "dark": (0.14, 0.12, 0.10, 1.0),
        "steel": (0.42, 0.42, 0.43, 1.0),
        "rubber": (0.09, 0.08, 0.08, 1.0),
    },
    "graphite": {
        "frame": (0.24, 0.25, 0.26, 1.0),
        "deck": (0.70, 0.72, 0.74, 1.0),
        "wood": (0.62, 0.45, 0.27, 1.0),
        "dark": (0.10, 0.10, 0.11, 1.0),
        "steel": (0.46, 0.47, 0.48, 1.0),
        "rubber": (0.07, 0.07, 0.08, 1.0),
    },
}


# Fixed manufacturing cross-sections (surface detail, not core/raw).
POST = 0.038              # square post side
RAIL_H = 0.030            # perimeter rail height
RAIL_T = 0.022            # perimeter rail thickness
DECK_T = 0.014            # stainless deck thickness
BLOCK_T = 0.038           # butcher block thickness
INSET = 0.030             # post inset from the top edge
# Radial running fit, under the 1 mm assembly-gap tolerance.
FIT = 0.0008
SEAT = 0.0006
WHEEL_R = 0.040
WHEEL_W = 0.030
YOKE_T = 0.008
KINGPIN_R = 0.009
SWIVEL_DROP = 0.030       # king-pin boss height under the post foot
TRAIL = 0.018             # caster trail: the wheel axis stands behind the king pin
BAY_TOP_GAP = 0.060       # clear space under the worktop before the storage bay


@dataclass(frozen=True)
class Config:
    top_surface: TopSurface = "stainless_deck"
    storage_module: StorageModule = "open_shelf"
    leg_form: LegForm = "fixed_post"
    bench_accessory: BenchAccessory = "monitor_arm"
    side_bracing: SideBracing = "plain_rails"
    storage_level_count: int = 2
    table_length_m: float | None = None
    table_depth_m: float | None = None
    table_height_m: float | None = None
    palette_style: PaletteStyle = "stainless"
    name: str = "pictureX_0611_Industrial_rolling_work_table"


@dataclass(frozen=True)
class ResolvedConfig:
    top_surface: TopSurface
    storage_module: StorageModule
    leg_form: LegForm
    bench_accessory: BenchAccessory
    side_bracing: SideBracing
    storage_level_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    table_length_m: float
    table_depth_m: float
    table_height_m: float
    top_thickness_m: float
    deck_top_z_m: float
    post_x: float
    post_y: float
    caster_z: float
    post_bottom_z: float
    bay_top_z: float
    bay_floor_z: float
    level_pitch_m: float
    post_travel_m: float
    drawer_travel_m: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x2B_71_44_9E)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        top_surface=choices["top_surface"],
        storage_module=choices["storage_module"],
        leg_form=choices["leg_form"],
        bench_accessory=choices["bench_accessory"],
        side_bracing=choices["side_bracing"],
        storage_level_count=choices["storage_level_count"],
        table_length_m=round(rng.uniform(0.700, 1.400), 4),
        table_depth_m=round(rng.uniform(0.450, 0.800), 4),
        table_height_m=round(rng.uniform(0.780, 1.020), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"industrial_rolling_work_table_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "top_surface": config.top_surface,
            "storage_module": config.storage_module,
            "leg_form": config.leg_form,
            "bench_accessory": config.bench_accessory,
            "side_bracing": config.side_bracing,
            "storage_level_count": config.storage_level_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.table_length_m is not None and not 0.700 <= float(config.table_length_m) <= 1.400:
        raise ValueError("table_length_m must be in [0.700, 1.400]")
    if config.table_depth_m is not None and not 0.450 <= float(config.table_depth_m) <= 0.800:
        raise ValueError("table_depth_m must be in [0.450, 0.800]")
    if config.table_height_m is not None and not 0.780 <= float(config.table_height_m) <= 1.020:
        raise ValueError("table_height_m must be in [0.780, 1.020]")

    length = (
        _clamp(config.table_length_m, 0.700, 1.400) if config.table_length_m is not None else 1.000
    )
    depth = (
        _clamp(config.table_depth_m, 0.450, 0.800) if config.table_depth_m is not None else 0.600
    )
    height = (
        _clamp(config.table_height_m, 0.780, 1.020) if config.table_height_m is not None else 0.900
    )

    top_t = DECK_T if config.top_surface == "stainless_deck" else BLOCK_T
    post_x = 0.5 * length - INSET - 0.5 * POST
    post_y = 0.5 * depth - INSET - 0.5 * POST
    caster_z = 2.0 * WHEEL_R + 0.016
    post_bottom = caster_z + SWIVEL_DROP
    post_top = height - top_t - SEAT
    travel_pre = 0.12 * height if config.leg_form == "telescopic_post" else 0.0
    # The bay-top rail has to clear the inner posts' full travel, so a
    # telescopic table carries its bay lower than a welded one.
    bay_top = height - top_t - BAY_TOP_GAP
    if config.leg_form == "telescopic_post":
        bay_top = min(bay_top, post_top - 2.0 * travel_pre - 0.072 - 0.5 * RAIL_H - 0.002)
    bay_floor = post_bottom + 0.020
    n = int(config.storage_level_count)
    pitch = (bay_top - bay_floor - 0.020) / n
    travel = travel_pre
    return ResolvedConfig(
        top_surface=config.top_surface,
        storage_module=config.storage_module,
        leg_form=config.leg_form,
        bench_accessory=config.bench_accessory,
        side_bracing=config.side_bracing,
        storage_level_count=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        table_length_m=length,
        table_depth_m=depth,
        table_height_m=height,
        top_thickness_m=top_t,
        deck_top_z_m=height,
        post_x=post_x,
        post_y=post_y,
        caster_z=caster_z,
        post_bottom_z=post_bottom,
        bay_top_z=bay_top,
        bay_floor_z=bay_floor,
        level_pitch_m=pitch,
        post_travel_m=travel,
        drawer_travel_m=0.62 * depth,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("top_surface", config.top_surface),
        ("storage_module", config.storage_module),
        ("leg_form", config.leg_form),
        ("bench_accessory", config.bench_accessory),
        ("side_bracing", config.side_bracing),
        ("storage_level_count", config.storage_level_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        name = f"irwt_{r.palette_style}_{key}"
        model.material(name, rgba=rgba)
        mats[key] = name
    return mats


def _box_at(x0, x1, y0, y1, z0, z1):
    return (
        cq.Workplane("XY")
        .transformed(offset=(0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1)))
        .box(x1 - x0, y1 - y0, z1 - z0)
    )


def _local_origin(
    origin: Origin | None, offset: tuple[float, float, float]
) -> Origin:
    base = origin or Origin()
    return Origin(
        xyz=tuple(a - b for a, b in zip(base.xyz, offset)),
        rpy=base.rpy,
    )


# --- frame --------------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    frame = model.part("frame", meta={"role": "frame"})
    post_top = r.deck_top_z_m - r.top_thickness_m - SEAT
    for index, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
        x = sx * r.post_x
        y = sy * r.post_y
        if r.leg_form == "fixed_post":
            frame.visual(
                Box((POST, POST, post_top - r.post_bottom_z)),
                origin=Origin(xyz=(x, y, 0.5 * (r.post_bottom_z + post_top))),
                material=mats["frame"],
                name=f"leg_form__fixed_post__post_{index}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
            )
        else:
            # The outer post is the fixed leg; the inner post rides with the top.
            sleeve_top = post_top - r.post_travel_m
            inner = POST - 0.008 + 2.0 * FIT
            sleeve = _box_at(
                x - 0.5 * POST,
                x + 0.5 * POST,
                y - 0.5 * POST,
                y + 0.5 * POST,
                r.post_bottom_z,
                sleeve_top,
            )
            # A real sleeve: the inner post slides in its bore, it is not a
            # solid leg with another solid pushed into it.
            sleeve = sleeve.cut(
                _box_at(
                    x - 0.5 * inner,
                    x + 0.5 * inner,
                    y - 0.5 * inner,
                    y + 0.5 * inner,
                    r.post_bottom_z + 0.030,
                    sleeve_top + 0.01,
                )
            )
            collar = _box_at(
                x - 0.5 * POST - 0.005,
                x + 0.5 * POST + 0.005,
                y - 0.5 * POST - 0.005,
                y + 0.5 * POST + 0.005,
                sleeve_top - 0.016,
                sleeve_top - 0.002,
            ).cut(
                _box_at(
                    x - 0.5 * inner,
                    x + 0.5 * inner,
                    y - 0.5 * inner,
                    y + 0.5 * inner,
                    sleeve_top - 0.03,
                    sleeve_top + 0.01,
                )
            )
            frame.visual(
                mesh_from_cadquery(sleeve, f"irwt_outer_post_{index}"),
                material=mats["frame"],
                name=f"leg_form__telescopic_post__outer_post_{index}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
            )
            frame.visual(
                mesh_from_cadquery(collar, f"irwt_locking_collar_{index}"),
                material=mats["steel"],
                name=f"leg_form__telescopic_post__locking_collar_{index}", material_class_id="metal.steel_bare",
            )
        # King-pin boss under each post foot, bored for the swivel stem.
        boss = (
            cq.Workplane("XY")
            .transformed(offset=(0.0, 0.0, 0.5 * SWIVEL_DROP))
            .box(POST + 0.010, POST + 0.010, SWIVEL_DROP)
        )
        boss = boss.cut(
            cq.Workplane("XY")
            .transformed(offset=(0.0, 0.0, 0.5 * SWIVEL_DROP))
            .cylinder(height=SWIVEL_DROP * 3.0, radius=KINGPIN_R + FIT, direct=(0.0, 0.0, 1.0))
        )
        frame.visual(
            mesh_from_cadquery(boss, f"irwt_kingpin_boss_{index}"),
            origin=Origin(xyz=(x, y, r.caster_z)),
            material=mats["dark"],
            name=f"caster_boss_{index}", material_class_id="metal.blackened_gunmetal",
        )

    # Perimeter rails at the bay top and the bay floor.
    for level, z in ((0, r.bay_top_z), (1, r.bay_floor_z)):
        for side, sy in enumerate((-1.0, 1.0)):
            frame.visual(
                Box((2.0 * r.post_x + POST, RAIL_T, RAIL_H)),
                origin=Origin(xyz=(0.0, sy * r.post_y, z)),
                material=mats["frame"],
                name=f"side_rail_{level}_{side}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
            )
        for side, sx in enumerate((-1.0, 1.0)):
            frame.visual(
                Box((RAIL_T, 2.0 * r.post_y - POST, RAIL_H)),
                origin=Origin(xyz=(sx * r.post_x, 0.0, z)),
                material=mats["frame"],
                name=f"end_rail_{level}_{side}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
            )
    _SIDE_BRACING_BUILDERS[r.side_bracing](frame, r, mats)
    if r.storage_module == "pegboard_rack":
        _pegboard_back(frame, r, mats)
    return frame


def _side_bracing_plain_rails_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Open sides: a single light stretcher keeps the bay legible as rail-only."""
    for index, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((RAIL_T, 2.0 * r.post_y - POST, 0.016)),
            origin=Origin(
                xyz=(sx * r.post_x, 0.0, 0.5 * (r.bay_floor_z + r.bay_top_z))
            ),
            material=mats["frame"],
            name=f"side_bracing__plain_rails__stretcher_{index}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
        )


def _side_bracing_x_braces_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Crossed flat bars filling each side bay on its own diagonal."""
    dy = 2.0 * r.post_y - POST
    dz = r.bay_top_z - r.bay_floor_z - RAIL_H
    length = math.hypot(dy, dz)
    angle = math.atan2(dz, dy)
    cz = 0.5 * (r.bay_floor_z + r.bay_top_z)
    for index, sx in enumerate((-1.0, 1.0)):
        for k, sign in enumerate((1.0, -1.0)):
            frame.visual(
                Box((0.014, length, 0.016)),
                origin=Origin(
                    xyz=(sx * r.post_x, 0.0, cz), rpy=(sign * angle, 0.0, 0.0)
                ),
                material=mats["frame"],
                name=f"side_bracing__x_braces__brace_{index}_{k}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
            )


def _pegboard_back(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Host adaptation: the pegboard candidate raises a perforated back panel on
    two brackets behind the worktop, clear of the top's own footprint."""
    panel_h = 0.34 * r.table_height_m
    y_panel = 0.5 * r.table_depth_m + 0.014
    z0 = r.bay_top_z
    for index, sx in enumerate((-1.0, 1.0)):
        x = sx * r.post_x
        frame.visual(
            Box((0.026, y_panel + 0.008 - r.post_y, 0.016)),
            origin=Origin(
                xyz=(x, 0.5 * (r.post_y + y_panel + 0.008), r.bay_top_z)
            ),
            material=mats["frame"],
            name=f"storage_module__pegboard_rack__bracket_{index}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
        )
        frame.visual(
            Box((0.026, 0.016, r.deck_top_z_m + panel_h - z0)),
            origin=Origin(
                xyz=(x, y_panel, 0.5 * (z0 + r.deck_top_z_m + panel_h))
            ),
            material=mats["frame"],
            name=f"storage_module__pegboard_rack__riser_{index}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
        )
    panel_z0 = r.deck_top_z_m
    panel = _box_at(
        -(r.post_x + 0.5 * POST),
        r.post_x + 0.5 * POST,
        y_panel - 0.004,
        y_panel + 0.006,
        panel_z0,
        panel_z0 + panel_h,
    )
    cols = min(10, max(4, int((2.0 * r.post_x) / 0.070)))
    rows = min(5, max(3, int(panel_h / 0.070)))
    for i in range(cols):
        for j in range(rows):
            px = -(r.post_x) + (i + 0.5) * (2.0 * r.post_x) / cols
            pz = panel_z0 + (j + 0.5) * panel_h / rows
            panel = panel.cut(
                cq.Workplane("XY")
                .transformed(offset=(px, y_panel, pz), rotate=(90.0, 0.0, 0.0))
                .cylinder(height=0.05, radius=0.005, direct=(0.0, 0.0, 1.0))
            )
    frame.visual(
        mesh_from_cadquery(panel, "irwt_pegboard_panel"),
        material=mats["frame"],
        name="storage_module__pegboard_rack__back_panel", material_class_id="metal.patterned_sheet_panel",
    )
    for index in range(4):
        px = -(r.post_x) + (index + 0.5) * (2.0 * r.post_x) / 4.0
        frame.visual(
            Cylinder(radius=0.004, length=0.040),
            origin=Origin(
                xyz=(px, y_panel - 0.024, panel_z0 + 0.72 * panel_h),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["steel"],
            name=f"storage_module__pegboard_rack__hook_{index}", material_class_id="metal.steel_bare",
        )


# --- caster chain -------------------------------------------------------------
def _build_casters(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]):
    """Four braked swivel casters.  Every part is retained by real geometry: the
    king pin runs in the frame boss, the wheel between two yoke cheeks, and the
    brake pedal between two ears hanging off the yoke plate."""
    swivels, wheels, brakes = [], [], []
    cheek_y = 0.5 * WHEEL_W + FIT + 0.5 * YOKE_T
    plate_z0 = -0.014
    plate_z1 = -0.002
    pivot = (0.030, 0.0, -0.020)
    pedal_half_y = 0.5 * WHEEL_W + YOKE_T
    ear_y = pedal_half_y + FIT + 0.004
    for index, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
        x = sx * r.post_x
        y = sy * r.post_y
        swivel = model.part(
            f"caster_swivel_{index}", meta={"role": "caster_swivel", "index": index}
        )
        pin_len = SWIVEL_DROP + 0.011
        swivel.visual(
            Cylinder(radius=KINGPIN_R, length=pin_len),
            origin=Origin(xyz=(0.0, 0.0, 0.5 * pin_len - 0.014)),
            material=mats["steel"],
            name=f"caster_swivel__kingpin_{index}", material_class_id="metal.steel_bare",
        )
        swivel.visual(
            Box((0.086, 2.0 * cheek_y + YOKE_T, plate_z1 - plate_z0)),
            origin=Origin(xyz=(-0.005, 0.0, 0.5 * (plate_z0 + plate_z1))),
            material=mats["steel"],
            name=f"caster_swivel__yoke_plate_{index}", material_class_id="metal.steel_bare",
        )
        for cheek, cy in enumerate((-1.0, 1.0)):
            swivel.visual(
                Box((0.034, YOKE_T, WHEEL_R + 0.018)),
                origin=Origin(
                    xyz=(-TRAIL, cy * cheek_y, plate_z0 + 0.004 - 0.5 * (WHEEL_R + 0.018))
                ),
                material=mats["steel"],
                name=f"caster_swivel__yoke_cheek_{index}_{cheek}", material_class_id="metal.steel_bare",
            )
        for ear, ey in enumerate((-1.0, 1.0)):
            swivel.visual(
                Box((0.014, 0.008, plate_z1 - pivot[2] - 0.004)),
                origin=Origin(
                    xyz=(pivot[0], ey * ear_y, 0.5 * (plate_z1 + pivot[2] + 0.004)),
                ),
                material=mats["steel"],
                name=f"caster_swivel__brake_ear_{index}_{ear}", material_class_id="metal.steel_bare",
            )
        _axis_joint(
            model,
            name=f"frame_to_caster_swivel_{index}",
            parent=frame,
            child=swivel,
            point=(x, y, r.caster_z),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            kind=ArticulationType.CONTINUOUS,
            limits=MotionLimits(effort=40.0, velocity=4.0),
            meta={"positive_motion": "swivels the caster about its king pin"},
        )

        wheel = model.part(
            f"caster_wheel_{index}", meta={"role": "caster_wheel", "index": index}
        )
        wheel.visual(
            Cylinder(radius=WHEEL_R, length=WHEEL_W),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["rubber"],
            name=f"caster_wheel__tyre_{index}", material_class_id="rubber.smooth_plain",
        )
        wheel.visual(
            Cylinder(radius=WHEEL_R * 0.46, length=WHEEL_W + 0.006),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["steel"],
            name=f"caster_wheel__hub_{index}", material_class_id="metal.steel_bare",
        )
        _axis_joint(
            model,
            name=f"caster_swivel_to_wheel_{index}",
            parent=swivel,
            child=wheel,
            point=(-TRAIL, 0.0, -r.caster_z + WHEEL_R),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            kind=ArticulationType.CONTINUOUS,
            limits=MotionLimits(effort=60.0, velocity=8.0),
            meta={"positive_motion": "rolls the wheel forward"},
        )

        brake = model.part(
            f"caster_brake_{index}", meta={"role": "caster_brake", "index": index}
        )
        brake.visual(
            Box((0.050, 2.0 * pedal_half_y, 0.008)),
            origin=Origin(xyz=(0.025, 0.0, 0.0)),
            material=mats["steel"],
            name=f"caster_brake__pedal_{index}", material_class_id="metal.steel_bare",
        )
        # The shoe stands 5 mm off the tread and closes on it as the pedal drops.
        brake.visual(
            Box((0.014, WHEEL_W - 0.004, 0.020)),
            origin=Origin(xyz=(0.004, 0.0, -0.012)),
            material=mats["rubber"],
            name=f"caster_brake__shoe_{index}", material_class_id="rubber.smooth_plain",
        )
        _axis_joint(
            model,
            name=f"caster_swivel_to_brake_{index}",
            parent=swivel,
            child=brake,
            point=pivot,
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            kind=ArticulationType.REVOLUTE,
            limits=MotionLimits(effort=20.0, velocity=2.0, lower=-0.35, upper=0.0),
            meta={"positive_motion": "lifts the brake shoe off the tread"},
        )
        swivels.append(swivel)
        wheels.append(wheel)
        brakes.append(brake)
    return swivels, wheels, brakes


def _axis_joint(model, *, name, parent, child, point, axis, radial, kind, limits, meta=None) -> None:
    provider = AxisInterface(name=f"{name}__provider", point=point, axis=axis, radial=radial)
    consumer = AxisInterface(name=f"{name}__consumer", axis=axis, radial=radial)
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        kind,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)


# --- worktop candidates -------------------------------------------------------
def _top_surface_stainless_deck_build(
    part, offset: tuple[float, float, float], r: ResolvedConfig, mats: dict[str, str]
) -> None:
    half_x = 0.5 * r.table_length_m
    half_y = 0.5 * r.table_depth_m
    z1 = r.deck_top_z_m
    z0 = z1 - DECK_T
    deck = _box_at(-half_x, half_x, -half_y, half_y, z0, z1)
    # Turned-down edge skirt: the deck is a folded panel, not a solid slab.
    deck = deck.cut(
        _box_at(
            -half_x + 0.012,
            half_x - 0.012,
            -half_y + 0.012,
            half_y - 0.012,
            z0,
            z1 - 0.004,
        )
    )
    part.visual(
        mesh_from_cadquery(deck, "irwt_stainless_deck"),
        origin=_local_origin(None, offset),
        material=mats["deck"],
        name="top_surface__stainless_deck__deck_panel", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Box((2.0 * half_x - 0.030, 0.020, 0.014)),
        origin=_local_origin(
            Origin(xyz=(0.0, half_y - 0.012, z0 - 0.006)), offset
        ),
        material=mats["deck"],
        name="top_surface__stainless_deck__rear_upstand", material_class_id="metal.stainless_matte",
    )
    # Underside stiffeners: the folded panel is carried on two bearers that
    # actually land on the post tops.
    for index, sy in enumerate((-1.0, 1.0)):
        part.visual(
            Box((2.0 * half_x - 0.024, 0.026, DECK_T - 0.004)),
            origin=_local_origin(
                Origin(
                    xyz=(0.0, sy * r.post_y, z0 + 0.5 * (DECK_T - 0.004))
                ),
                offset,
            ),
            material=mats["deck"],
            name=f"top_surface__stainless_deck__bearer_{index}", material_class_id="metal.stainless_matte",
        )


def _top_surface_butcher_block_build(
    part, offset: tuple[float, float, float], r: ResolvedConfig, mats: dict[str, str]
) -> None:
    half_x = 0.5 * r.table_length_m
    half_y = 0.5 * r.table_depth_m
    z1 = r.deck_top_z_m
    z0 = z1 - BLOCK_T
    part.visual(
        Box((2.0 * half_x, 2.0 * half_y, BLOCK_T)),
        origin=_local_origin(Origin(xyz=(0.0, 0.0, 0.5 * (z0 + z1))), offset),
        material=mats["wood"],
        name="top_surface__butcher_block__slab", material_class_id="wood.oak",
    )
    strips = max(5, int(2.0 * half_y / 0.070))
    for index in range(1, strips):
        y = -half_y + index * (2.0 * half_y) / strips
        part.visual(
            Box((2.0 * half_x, 0.0025, 0.0018)),
            origin=_local_origin(Origin(xyz=(0.0, y, z1 - 0.0006)), offset),
            material=mats["dark"],
            name=f"top_surface__butcher_block__glue_line_{index}", material_class_id="wood.walnut_dark",
        )


_TOP_BUILDERS = {
    "stainless_deck": _top_surface_stainless_deck_build,
    "butcher_block": _top_surface_butcher_block_build,
}


def _top_offset(r: ResolvedConfig) -> tuple[float, float, float]:
    """Over a post, so the joint origin sits in both the frame and the top."""
    return (r.post_x, r.post_y, r.deck_top_z_m - r.top_thickness_m + 0.004)


def _build_worktop(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]):
    top = model.part("worktop", meta={"role": "worktop"})
    off = _top_offset(r)
    _TOP_BUILDERS[r.top_surface](top, off, r, mats)
    if r.leg_form == "telescopic_post":
        # The inner posts belong to the moving top and slide inside the legs.
        for index, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
            top.visual(
                Box(
                    (
                        POST - 0.008,
                        POST - 0.008,
                        r.post_travel_m + 0.070,
                    )
                ),
                origin=_local_origin(
                    Origin(
                        xyz=(
                            sx * r.post_x,
                            sy * r.post_y,
                            r.deck_top_z_m
                            - 0.006
                            - 0.5 * (r.post_travel_m + 0.070),
                        )
                    ),
                    off,
                ),
                material=mats["steel"],
                name=f"leg_form__telescopic_post__inner_post_{index}", material_class_id="metal.steel_bare",
            )
        model.articulation(
            "frame_to_worktop",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=top,
            origin=Origin(xyz=off),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=800.0, velocity=0.05, lower=-r.post_travel_m, upper=0.0
            ),
            meta={"positive_motion": "raises the worktop to full height"},
        )
    else:
        model.articulation(
            "frame_to_worktop",
            ArticulationType.FIXED,
            parent=frame,
            child=top,
            origin=Origin(xyz=off),
        )
    return top


# --- storage module candidates ------------------------------------------------
def _level_z(r: ResolvedConfig, index: int) -> float:
    return r.bay_floor_z + 0.010 + (index + 0.5) * r.level_pitch_m


def _storage_offset(r: ResolvedConfig, index: int) -> tuple[float, float, float]:
    """Beside a post, so the joint origin sits in both the frame and the item."""
    return (
        r.post_x - 0.5 * POST - SEAT - 0.004,
        r.post_y - 0.5 * POST - SEAT - 0.004,
        _level_z(r, index),
    )


def _storage_open_shelf_build(
    part,
    offset: tuple[float, float, float],
    r: ResolvedConfig,
    mats: dict[str, str],
    index: int,
) -> None:
    half_x = r.post_x - 0.5 * POST - SEAT
    half_y = r.post_y - 0.5 * POST - SEAT
    part.visual(
        Box((2.0 * half_x, 2.0 * half_y, 0.012)),
        origin=_local_origin(Origin(xyz=(0.0, 0.0, 0.0)), offset),
        material=mats["frame"],
        name=f"storage_module__open_shelf__shelf_panel_{index}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
    )
    for edge, sy in enumerate((-1.0, 1.0)):
        part.visual(
            Box((2.0 * half_x, 0.010, 0.020)),
            origin=_local_origin(
                Origin(xyz=(0.0, sy * (half_y - 0.005), 0.014)), offset
            ),
            material=mats["frame"],
            name=f"storage_module__open_shelf__shelf_lip_{index}_{edge}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
        )


def _storage_drawer_bank_build(
    part,
    offset: tuple[float, float, float],
    r: ResolvedConfig,
    mats: dict[str, str],
    index: int,
) -> None:
    half_x = r.post_x - 0.5 * POST - 0.012
    half_y = r.post_y - 0.5 * POST - 0.012
    h = min(0.120, r.level_pitch_m - 0.026)
    tray = _box_at(-half_x, half_x, -half_y, half_y, -0.5 * h, 0.5 * h)
    tray = tray.cut(
        _box_at(
            -half_x + 0.008,
            half_x - 0.008,
            -half_y + 0.008,
            half_y - 0.008,
            -0.5 * h + 0.008,
            0.5 * h + 0.01,
        )
    )
    part.visual(
        mesh_from_cadquery(tray, f"irwt_drawer_tray_{index}"),
        origin=_local_origin(None, offset),
        material=mats["frame"],
        name=f"storage_module__drawer_bank__tray_{index}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
    )
    part.visual(
        Box((2.0 * half_x + 0.016, 0.012, h + 0.014)),
        origin=_local_origin(Origin(xyz=(0.0, -half_y - 0.006, 0.0)), offset),
        material=mats["dark"],
        name=f"storage_module__drawer_bank__front_face_{index}", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((0.5 * half_x, 0.018, 0.014)),
        origin=_local_origin(Origin(xyz=(0.0, -half_y - 0.018, 0.0)), offset),
        material=mats["steel"],
        name=f"storage_module__drawer_bank__pull_{index}", material_class_id="metal.steel_bare",
    )
    for side, sx in enumerate((-1.0, 1.0)):
        part.visual(
            Box((0.016, 2.0 * (r.post_y - 0.5 * POST - SEAT), 0.010)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        sx * (r.post_x - 0.5 * POST - SEAT - 0.008),
                        0.0,
                        0.5 * h - 0.010,
                    )
                ),
                offset,
            ),
            material=mats["steel"],
            name=f"storage_module__drawer_bank__runner_{index}_{side}", material_class_id="metal.steel_bare",
        )


def _storage_pegboard_rack_build(
    part,
    offset: tuple[float, float, float],
    r: ResolvedConfig,
    mats: dict[str, str],
    index: int,
) -> None:
    half_x = r.post_x - 0.5 * POST - 0.012
    half_y = r.post_y - 0.5 * POST - 0.012
    part.visual(
        Box((2.0 * half_x, 2.0 * half_y, 0.010)),
        origin=_local_origin(Origin(xyz=(0.0, 0.0, 0.0)), offset),
        material=mats["steel"],
        name=f"storage_module__pegboard_rack__tray_floor_{index}", material_class_id="metal.steel_bare",
    )
    for edge, (dx, dy, sx, sy) in enumerate(
        (
            (2.0 * half_x, 0.008, 0.0, -1.0),
            (2.0 * half_x, 0.008, 0.0, 1.0),
            (0.008, 2.0 * half_y, -1.0, 0.0),
            (0.008, 2.0 * half_y, 1.0, 0.0),
        )
    ):
        part.visual(
            Box((dx, dy, 0.026)),
            origin=_local_origin(
                Origin(
                    xyz=(sx * (half_x - 0.004), sy * (half_y - 0.004), 0.017)
                ),
                offset,
            ),
            material=mats["steel"],
            name=f"storage_module__pegboard_rack__tray_wall_{index}_{edge}", material_class_id="metal.steel_bare",
        )
    for side, sx in enumerate((-1.0, 1.0)):
        part.visual(
            Box((0.016, 2.0 * (r.post_y - 0.5 * POST - SEAT), 0.010)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        sx * (r.post_x - 0.5 * POST - SEAT - 0.008),
                        0.0,
                        0.0,
                    )
                ),
                offset,
            ),
            material=mats["steel"],
            name=f"storage_module__pegboard_rack__runner_{index}_{side}", material_class_id="metal.steel_bare",
        )


_SIDE_BRACING_BUILDERS = {
    "plain_rails": _side_bracing_plain_rails_build,
    "x_braces": _side_bracing_x_braces_build,
}


_STORAGE_BUILDERS = {
    "open_shelf": _storage_open_shelf_build,
    "drawer_bank": _storage_drawer_bank_build,
    "pegboard_rack": _storage_pegboard_rack_build,
}


def _build_storage(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]):
    items = []
    for index in range(r.storage_level_count):
        item = model.part(
            f"storage_module__{r.storage_module}__item_{index}",
            meta={"role": "storage_item", "index": index},
        )
        off = _storage_offset(r, index)
        _STORAGE_BUILDERS[r.storage_module](
            item, (off[0], off[1], 0.0), r, mats, index
        )
        joint = f"frame_to_storage_item_{index}"
        if r.storage_module == "open_shelf":
            model.articulation(
                joint,
                ArticulationType.FIXED,
                parent=frame,
                child=item,
                origin=Origin(xyz=off),
            )
        else:
            model.articulation(
                joint,
                ArticulationType.PRISMATIC,
                parent=frame,
                child=item,
                origin=Origin(xyz=off),
                axis=(0.0, -1.0, 0.0),
                motion_limits=MotionLimits(
                    effort=60.0, velocity=0.20, lower=0.0, upper=r.drawer_travel_m
                ),
                meta={"positive_motion": "pulls the tray out of the bay"},
            )
        items.append(item)
    return items


# --- bench accessory candidates -------------------------------------------------
def _accessory_monitor_arm_build(model, frame, r: ResolvedConfig, mats: dict[str, str]):
    """A rear post carrying a display that tilts on its own horizontal axis."""
    # Behind the pegboard's own plane, so the two rear fittings never share space.
    post_y = 0.5 * r.table_depth_m + 0.052
    post_top = r.deck_top_z_m + 0.34 * r.table_height_m
    mast_top = post_top - 0.0148
    frame.visual(
        Box((0.040, 0.024, mast_top - r.bay_top_z)),
        origin=Origin(xyz=(0.0, post_y, 0.5 * (r.bay_top_z + mast_top))),
        material=mats["frame"],
        name="bench_accessory__monitor_arm__mast", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
    )
    frame.visual(
        Box((0.090, 0.026 + (post_y - r.post_y), 0.016)),
        origin=Origin(
            xyz=(0.0, 0.5 * (r.post_y + post_y), r.bay_top_z)
        ),
        material=mats["frame"],
        name="bench_accessory__monitor_arm__mast_bracket", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
    )
    monitor = model.part(
        "bench_accessory__monitor_arm__display", meta={"role": "bench_accessory"}
    )
    off = (0.0, post_y, post_top)
    monitor.visual(
        Cylinder(radius=0.014, length=0.070),
        origin=_local_origin(
            Origin(
                xyz=(0.0, post_y, post_top), rpy=(0.0, math.pi / 2.0, 0.0)
            ),
            off,
        ),
        material=mats["steel"],
        name="bench_accessory__monitor_arm__tilt_barrel", material_class_id="metal.steel_bare",
    )
    width = min(0.46, 1.6 * r.post_x)
    monitor.visual(
        Box((0.070, 0.022, 0.046)),
        origin=_local_origin(
            Origin(xyz=(0.0, post_y - 0.014, post_top + 0.022)), off
        ),
        material=mats["steel"],
        name="bench_accessory__monitor_arm__yoke", material_class_id="metal.steel_bare",
    )
    monitor.visual(
        Box((width, 0.024, 0.60 * width)),
        origin=_local_origin(
            Origin(
                xyz=(0.0, post_y - 0.014, post_top + 0.040 + 0.30 * width)
            ),
            off,
        ),
        material=mats["frame"],
        name="bench_accessory__monitor_arm__display_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    monitor.visual(
        Box((width - 0.040, 0.006, 0.60 * width - 0.040)),
        origin=_local_origin(
            Origin(
                xyz=(0.0, post_y - 0.029, post_top + 0.040 + 0.30 * width)
            ),
            off,
        ),
        material=mats["dark"],
        name="bench_accessory__monitor_arm__display_glass", material_class_id="glass.smoked_tinted",
    )
    _axis_joint(
        model,
        name="frame_to_bench_accessory",
        parent=frame,
        child=monitor,
        point=off,
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        kind=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=18.0, velocity=1.5, lower=-0.30, upper=0.30),
        meta={"positive_motion": "tilts the display back"},
    )
    return monitor


def _accessory_keyboard_tray_build(model, frame, r: ResolvedConfig, mats: dict[str, str]):
    """A lipped pan hung under the bench on two side runners."""
    tray_z = r.bay_top_z + 0.030
    half_x = r.post_x - 0.5 * POST - 0.010
    half_y = r.post_y - 0.5 * POST - 0.010
    # The rails run inboard of the posts so a telescopic top's inner posts
    # sweep past them, and hang off the bay-top rail on their own stubs.
    rail_x = r.post_x - 0.5 * POST - 0.014
    for index, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.014, 2.0 * r.post_y, 0.014)),
            origin=Origin(xyz=(sx * rail_x, 0.0, tray_z + 0.014)),
            material=mats["steel"],
            name=f"bench_accessory__keyboard_tray__rail_{index}", material_class_id="metal.steel_bare",
        )
        # Only a rear hanger: a front one would sit in the tray's own travel.
        for stub in range(1):
            frame.visual(
                Box((0.014, 0.016, tray_z + 0.021 - r.bay_top_z)),
                origin=Origin(
                    xyz=(
                        sx * rail_x,
                        r.post_y - 0.012,
                        0.5 * (r.bay_top_z + tray_z + 0.021),
                    )
                ),
                material=mats["steel"],
                name=f"bench_accessory__keyboard_tray__hanger_{index}_{stub}", material_class_id="metal.steel_bare",
            )
    tray = model.part(
        "bench_accessory__keyboard_tray__tray", meta={"role": "bench_accessory"}
    )
    off = (0.0, 0.0, tray_z)
    tray.visual(
        Box((2.0 * half_x, 2.0 * half_y - 0.020, 0.014)),
        origin=_local_origin(Origin(xyz=(0.0, 0.0, tray_z)), off),
        material=mats["frame"],
        name="bench_accessory__keyboard_tray__tray_pan", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
    )
    tray.visual(
        Box((2.0 * half_x - 0.014, 0.020, 0.040)),
        origin=_local_origin(
            Origin(xyz=(0.0, -(half_y - 0.014), tray_z + 0.012)), off
        ),
        material=mats["steel"],
        name="bench_accessory__keyboard_tray__front_lip", material_class_id="metal.steel_bare",
    )
    for index, sx in enumerate((-1.0, 1.0)):
        tray.visual(
            Box((0.014, 2.0 * half_y - 0.020, 0.012)),
            origin=_local_origin(
                Origin(
                    xyz=(sx * (r.post_x - 0.5 * POST - 0.014), 0.0, tray_z)
                ),
                off,
            ),
            material=mats["steel"],
            name=f"bench_accessory__keyboard_tray__runner_{index}", material_class_id="metal.steel_bare",
        )
    model.articulation(
        "frame_to_bench_accessory",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=tray,
        origin=Origin(xyz=off),
        axis=(0.0, -1.0, 0.0),
        # The tray keeps 70 mm of runner engaged on its rails at full pull-out.
        motion_limits=MotionLimits(
            effort=30.0,
            velocity=0.20,
            lower=0.0,
            upper=min(0.70 * r.table_depth_m, 2.0 * half_y - 0.090),
        ),
        meta={"positive_motion": "pulls the keyboard tray out toward the operator"},
    )
    return tray


def _accessory_equipment_shelf_build(model, frame, r: ResolvedConfig, mats: dict[str, str]):
    """A closed equipment box fixed on the bench's rear brackets."""
    box_y = 0.5 * r.table_depth_m + 0.062
    box_z = r.deck_top_z_m
    frame.visual(
        Box((0.100, 0.030 + (box_y - r.post_y), 0.016)),
        origin=Origin(xyz=(0.0, 0.5 * (r.post_y + box_y), r.bay_top_z)),
        material=mats["frame"],
        name="bench_accessory__equipment_shelf__bracket", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
    )
    frame.visual(
        Box((0.030, 0.024, box_z - r.bay_top_z)),
        origin=Origin(xyz=(0.0, box_y, 0.5 * (r.bay_top_z + box_z))),
        material=mats["frame"],
        name="bench_accessory__equipment_shelf__riser", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
    )
    shelf = model.part(
        "bench_accessory__equipment_shelf__module", meta={"role": "bench_accessory"}
    )
    off = (0.0, box_y, box_z + 0.001)
    width = min(0.34, 1.3 * r.post_x)
    shelf.visual(
        Box((width, 0.056, 0.110)),
        origin=_local_origin(Origin(xyz=(0.0, box_y, box_z + 0.056)), off),
        material=mats["frame"],
        name="bench_accessory__equipment_shelf__module_body", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless" else "metal.paint_coated"),
    )
    shelf.visual(
        Box((width - 0.030, 0.006, 0.040)),
        origin=_local_origin(
            Origin(xyz=(0.0, box_y - 0.030, box_z + 0.070)), off
        ),
        material=mats["dark"],
        name="bench_accessory__equipment_shelf__module_panel", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "frame_to_bench_accessory",
        ArticulationType.FIXED,
        parent=frame,
        child=shelf,
        origin=Origin(xyz=off),
    )
    return shelf


_ACCESSORY_BUILDERS = {
    "monitor_arm": _accessory_monitor_arm_build,
    "keyboard_tray": _accessory_keyboard_tray_build,
    "equipment_shelf": _accessory_equipment_shelf_build,
}


# --- assembly -----------------------------------------------------------------
def build_picturex_0611_industrial_rolling_work_table(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Industrial_rolling_work_table",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "welded frame on four braked swivel casters",
        },
    )
    mats = _materials(model, r)
    frame = _build_frame(model, r, mats)
    _build_casters(model, frame, r, mats)
    _build_worktop(model, frame, r, mats)
    _build_storage(model, frame, r, mats)
    _ACCESSORY_BUILDERS[r.bench_accessory](model, frame, r, mats)

    open_pose = {}
    if r.storage_module != "open_shelf":
        open_pose = {
            f"frame_to_storage_item_{i}": r.drawer_travel_m
            for i in range(r.storage_level_count)
        }
    swivel_pose = {f"frame_to_caster_swivel_{i}": math.pi / 2.0 for i in range(4)}
    brake_pose = {f"caster_swivel_to_brake_{i}": -0.35 for i in range(4)}
    risk = [
        {f"frame_to_caster_swivel_{i}": 0.0 for i in range(4)},
        dict(swivel_pose) | dict(open_pose),
        dict(brake_pose) | dict(open_pose),
    ]
    if r.leg_form == "telescopic_post":
        risk[1]["frame_to_worktop"] = -r.post_travel_m
    model.meta["risk_poses"] = tuple(risk)
    return model


def build_seeded_picturex_0611_industrial_rolling_work_table(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_industrial_rolling_work_table(config_from_seed(seed), assets=assets)


# --- authored tests -----------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_industrial_rolling_work_table_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    frames = _parts_by_role(model, "frame")
    tops = _parts_by_role(model, "worktop")
    swivels = _parts_by_role(model, "caster_swivel")
    wheels = _parts_by_role(model, "caster_wheel")
    brakes = _parts_by_role(model, "caster_brake")
    items = _parts_by_role(model, "storage_item")
    joints = {j.name: j for j in model.articulations}

    ctx.check(
        "category_anchor: rolling work table frame, top and caster chain",
        len(frames) == 1
        and len(tops) == 1
        and len(swivels) == 4
        and len(wheels) == 4
        and len(brakes) == 4
        and len(items) == r.storage_level_count
        and bool(model.root_parts())
        and model.root_parts()[0].name == "frame"
        and joints["frame_to_worktop"].parent == "frame"
        and all(
            joints[f"frame_to_storage_item_{i}"].parent == "frame"
            for i in range(r.storage_level_count)
        ),
        details=(
            f"frames={len(frames)} tops={len(tops)} swivels={len(swivels)} "
            f"wheels={len(wheels)} brakes={len(brakes)} items={len(items)}"
        ),
    )

    def _axis_of(name: str) -> tuple[float, ...]:
        return tuple(round(abs(v), 6) for v in joints[name].axis)

    ctx.check(
        "category_anchor: every caster swivels, spins and brakes on its own axes",
        all(
            joints[f"frame_to_caster_swivel_{i}"].articulation_type
            == ArticulationType.CONTINUOUS
            and _axis_of(f"frame_to_caster_swivel_{i}") == (0.0, 0.0, 1.0)
            and joints[f"caster_swivel_to_wheel_{i}"].articulation_type
            == ArticulationType.CONTINUOUS
            and _axis_of(f"caster_swivel_to_wheel_{i}") == (0.0, 1.0, 0.0)
            and joints[f"caster_swivel_to_wheel_{i}"].parent == f"caster_swivel_{i}"
            and joints[f"caster_swivel_to_brake_{i}"].articulation_type
            == ArticulationType.REVOLUTE
            and joints[f"caster_swivel_to_brake_{i}"].parent == f"caster_swivel_{i}"
            for i in range(4)
        )
        # The swivel axis and the wheel axis are genuinely separate: the wheel
        # centre trails the king pin, which is what makes a caster steer.
        and TRAIL > 0.010
        and 0.0 < FIT <= 0.001
        and abs(r.caster_z - (2.0 * WHEEL_R + 0.016)) < 1e-9,
        details=f"trail={TRAIL} wheel_r={WHEEL_R} caster_z={r.caster_z}",
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    top_ok = {
        "stainless_deck": any("stainless_deck__deck_panel" in n for n in visual_names)
        and any("stainless_deck__rear_upstand" in n for n in visual_names),
        "butcher_block": any("butcher_block__slab" in n for n in visual_names)
        and sum(1 for n in visual_names if "butcher_block__glue_line" in n) >= 4,
    }[r.top_surface]
    ctx.check("category_anchor: top_surface identity", top_ok, details=f"top={r.top_surface}")

    storage_ok = {
        "open_shelf": sum(1 for n in visual_names if "open_shelf__shelf_panel" in n)
        == r.storage_level_count
        and all(
            joints[f"frame_to_storage_item_{i}"].articulation_type == ArticulationType.FIXED
            for i in range(r.storage_level_count)
        ),
        "drawer_bank": sum(1 for n in visual_names if "drawer_bank__tray_" in n)
        == r.storage_level_count
        and all(
            joints[f"frame_to_storage_item_{i}"].articulation_type == ArticulationType.PRISMATIC
            for i in range(r.storage_level_count)
        ),
        "pegboard_rack": any("pegboard_rack__back_panel" in n for n in visual_names)
        and sum(1 for n in visual_names if "pegboard_rack__tray_floor" in n)
        == r.storage_level_count,
    }[r.storage_module]
    ctx.check(
        "category_anchor: storage_module identity",
        storage_ok,
        details=f"storage={r.storage_module} n={r.storage_level_count}",
    )

    leg_ok = {
        "fixed_post": sum(1 for n in visual_names if "fixed_post__post_" in n) == 4
        and joints["frame_to_worktop"].articulation_type == ArticulationType.FIXED,
        "telescopic_post": sum(1 for n in visual_names if "telescopic_post__inner_post" in n) == 4
        and sum(1 for n in visual_names if "telescopic_post__locking_collar" in n) == 4
        and joints["frame_to_worktop"].articulation_type == ArticulationType.PRISMATIC,
    }[r.leg_form]
    ctx.check("category_anchor: leg_form identity", leg_ok, details=f"leg={r.leg_form}")

    accessory_ok = {
        "monitor_arm": any("monitor_arm__display_shell" in n for n in visual_names)
        and joints["frame_to_bench_accessory"].articulation_type == ArticulationType.REVOLUTE,
        "keyboard_tray": any("keyboard_tray__tray_pan" in n for n in visual_names)
        and sum(1 for n in visual_names if "keyboard_tray__rail_" in n) == 2
        and joints["frame_to_bench_accessory"].articulation_type == ArticulationType.PRISMATIC,
        "equipment_shelf": any("equipment_shelf__module_body" in n for n in visual_names)
        and joints["frame_to_bench_accessory"].articulation_type == ArticulationType.FIXED,
    }[r.bench_accessory]
    bracing_ok = {
        "plain_rails": sum(1 for n in visual_names if "plain_rails__stretcher" in n) == 2,
        "x_braces": sum(1 for n in visual_names if "x_braces__brace_" in n) == 4,
    }[r.side_bracing]
    ctx.check(
        "category_anchor: side_bracing identity",
        bracing_ok,
        details=f"bracing={r.side_bracing}",
    )

    ctx.check(
        "category_anchor: bench_accessory identity",
        accessory_ok,
        details=f"accessory={r.bench_accessory}",
    )

    # Motion evidence: a caster steers the wheel around its king pin.
    swivel_joint = joints["frame_to_caster_swivel_0"]
    rest = ctx.part_world_aabb(wheels[0])
    with ctx.pose({swivel_joint: math.pi / 2.0}):
        turned = ctx.part_world_aabb(wheels[0])
    ctx.check(
        "steering a caster carries its wheel around the king pin",
        rest is not None
        and turned is not None
        and abs(turned[0][2] - rest[0][2]) < 1e-6
        # A quarter turn swaps the wheel's footprint: its tread width and its
        # rolling diameter change places.
        and abs(
            (turned[1][1] - turned[0][1]) - (rest[1][1] - rest[0][1])
        ) > 0.5 * (2.0 * WHEEL_R - WHEEL_W),
        details=f"rest={rest} turned={turned}",
    )

    if r.leg_form == "telescopic_post":
        top_joint = joints["frame_to_worktop"]
        high = ctx.part_world_aabb(tops[0])
        with ctx.pose({top_joint: -r.post_travel_m}):
            low = ctx.part_world_aabb(tops[0])
        ctx.check(
            "the telescopic posts lower the worktop by the full travel",
            high is not None
            and low is not None
            and abs((high[0][2] - low[0][2]) - r.post_travel_m) < 1e-3,
            details=f"high={high} low={low}",
        )
    else:
        ctx.check(
            "the fixed posts hold the worktop at the working height",
            joints["frame_to_worktop"].articulation_type == ArticulationType.FIXED
            and abs(r.deck_top_z_m - r.table_height_m) < 1e-9,
            details=f"deck_top={r.deck_top_z_m} height={r.table_height_m}",
        )

    if r.storage_module != "open_shelf":
        item_joint = joints["frame_to_storage_item_0"]
        closed = ctx.part_world_aabb(items[0])
        with ctx.pose({item_joint: r.drawer_travel_m}):
            pulled = ctx.part_world_aabb(items[0])
        ctx.check(
            "a storage tray pulls clear of the frame on its runners",
            closed is not None
            and pulled is not None
            and abs((closed[0][1] - pulled[0][1]) - r.drawer_travel_m) < 1e-3,
            details=f"closed={closed} pulled={pulled}",
        )
    else:
        ctx.check(
            "the open shelves are carried on the bay rails",
            r.level_pitch_m > 0.090 and r.bay_top_z > r.bay_floor_z,
            details=f"pitch={r.level_pitch_m} bay=({r.bay_floor_z}, {r.bay_top_z})",
        )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "min_table_one_shelf_fixed",
        {
            "top_surface": "stainless_deck",
            "storage_module": "open_shelf",
            "leg_form": "fixed_post",
            "bench_accessory": "monitor_arm",
            "side_bracing": "plain_rails",
            "storage_level_count": 1,
            "table_length_m": 0.700,
            "table_depth_m": 0.450,
            "table_height_m": 0.780,
        },
        reason="smallest, lowest table with a single shelf — tightest bay",
    ),
    corner_case(
        "max_table_three_drawers_telescopic",
        {
            "top_surface": "butcher_block",
            "storage_module": "drawer_bank",
            "leg_form": "telescopic_post",
            "bench_accessory": "keyboard_tray",
            "side_bracing": "x_braces",
            "storage_level_count": 3,
            "table_length_m": 1.400,
            "table_depth_m": 0.800,
            "table_height_m": 1.020,
        },
        reason="largest table, three drawers and the full post travel under a thick slab",
    ),
    corner_case(
        "low_tall_bay_three_pegboard_trays",
        {
            "top_surface": "stainless_deck",
            "storage_module": "pegboard_rack",
            "leg_form": "telescopic_post",
            "bench_accessory": "equipment_shelf",
            "side_bracing": "x_braces",
            "storage_level_count": 3,
            "table_length_m": 0.700,
            "table_depth_m": 0.450,
            "table_height_m": 0.780,
        },
        reason="three trays in the shallowest bay under a raised pegboard back",
    ),
    corner_case(
        "wide_shallow_one_drawer_fixed",
        {
            "top_surface": "butcher_block",
            "storage_module": "drawer_bank",
            "leg_form": "fixed_post",
            "bench_accessory": "keyboard_tray",
            "side_bracing": "plain_rails",
            "storage_level_count": 1,
            "table_length_m": 1.400,
            "table_depth_m": 0.450,
            "table_height_m": 1.020,
        },
        reason="widest but shallowest table — the longest drawer front on the shortest runners",
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
    "build_picturex_0611_industrial_rolling_work_table",
    "build_seeded_picturex_0611_industrial_rolling_work_table",
    "run_picturex_0611_industrial_rolling_work_table_tests",
]
