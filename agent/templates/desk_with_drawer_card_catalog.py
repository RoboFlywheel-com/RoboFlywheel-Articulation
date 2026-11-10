# SPDX-License-Identifier: Apache-2.0

"""Design-backed card-catalog desk with a regular grid of guided drawers.

The runtime truth is this single file. X is width, the reader sits at -Y, and
Z is height. Every small drawer is an open-topped tray (or a boxed full-front
drawer) on its own -Y prismatic slide; the desk frame contains the worktop,
its support structure, the grid bank and the fixed rails.

Source-backed axes (upstream rec_0611 table/drawer families):

    desk_frame     : single_bank_open_knee / four_leg_apron_bank / trestle_open_bay
    drawer_module  : open_tray_guided / boxed_full_front
    pull_style     : bar_pull / knob_pair / finger_slot / recessed_oval
    drawer_columns : 2..6, drawer_rows : 2..6
    palette        : oak_brass / walnut_nickel / painted_steel / sage_enamel /
                     blackened_iron
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
    Inertial,
    MotionLimits,
    MotionProperties,
    Origin,
    PlaneInterface,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_planes,
    multiplicity_slot,
)

DeskFrame = Literal["single_bank_open_knee", "four_leg_apron_bank", "trestle_open_bay"]
DrawerModule = Literal["open_tray_guided", "boxed_full_front"]
PullStyle = Literal["bar_pull", "knob_pair", "finger_slot", "recessed_oval"]
Palette = Literal["oak_brass", "walnut_nickel", "painted_steel", "sage_enamel", "blackened_iron"]

DESK_FRAMES: tuple[DeskFrame, ...] = (
    "single_bank_open_knee",
    "four_leg_apron_bank",
    "trestle_open_bay",
)
DRAWER_MODULES: tuple[DrawerModule, ...] = ("open_tray_guided", "boxed_full_front")
PULL_STYLES: tuple[PullStyle, ...] = ("bar_pull", "knob_pair", "finger_slot", "recessed_oval")
GRID_VALUES: tuple[int, ...] = (2, 3, 4, 5, 6)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("desk_frame", DESK_FRAMES),
        component_slot("drawer_module", DRAWER_MODULES),
        component_slot("pull_style", PULL_STYLES),
        multiplicity_slot("drawer_columns", GRID_VALUES, item_slot="drawer_module"),
        multiplicity_slot("drawer_rows", GRID_VALUES, item_slot="drawer_module"),
    )
)

# "recess" doubles as the dark inset tone for finger-slot pulls.
_PALETTES: dict[Palette, dict[str, tuple[float, float, float, float]]] = {
    "oak_brass": {
        "top": (0.50, 0.30, 0.13, 1.0),
        "case": (0.40, 0.23, 0.10, 1.0),
        "edge": (0.22, 0.11, 0.045, 1.0),
        "inside": (0.60, 0.42, 0.23, 1.0),
        "metal": (0.66, 0.51, 0.22, 1.0),
        "paper": (0.90, 0.86, 0.71, 1.0),
        "recess": (0.16, 0.09, 0.04, 1.0),
    },
    "walnut_nickel": {
        "top": (0.31, 0.16, 0.075, 1.0),
        "case": (0.25, 0.12, 0.052, 1.0),
        "edge": (0.11, 0.055, 0.025, 1.0),
        "inside": (0.43, 0.26, 0.13, 1.0),
        "metal": (0.58, 0.61, 0.60, 1.0),
        "paper": (0.91, 0.88, 0.78, 1.0),
        "recess": (0.08, 0.045, 0.02, 1.0),
    },
    "painted_steel": {
        "top": (0.70, 0.69, 0.63, 1.0),
        "case": (0.27, 0.34, 0.33, 1.0),
        "edge": (0.10, 0.13, 0.13, 1.0),
        "inside": (0.46, 0.50, 0.47, 1.0),
        "metal": (0.72, 0.73, 0.69, 1.0),
        "paper": (0.94, 0.90, 0.74, 1.0),
        "recess": (0.07, 0.09, 0.09, 1.0),
    },
    "sage_enamel": {
        "top": (0.62, 0.60, 0.52, 1.0),
        "case": (0.42, 0.50, 0.42, 1.0),
        "edge": (0.24, 0.30, 0.24, 1.0),
        "inside": (0.56, 0.62, 0.54, 1.0),
        "metal": (0.62, 0.55, 0.35, 1.0),
        "paper": (0.92, 0.89, 0.80, 1.0),
        "recess": (0.12, 0.15, 0.12, 1.0),
    },
    "blackened_iron": {
        "top": (0.24, 0.23, 0.22, 1.0),
        "case": (0.16, 0.15, 0.145, 1.0),
        "edge": (0.09, 0.085, 0.08, 1.0),
        "inside": (0.33, 0.32, 0.30, 1.0),
        "metal": (0.44, 0.45, 0.46, 1.0),
        "paper": (0.88, 0.85, 0.76, 1.0),
        "recess": (0.05, 0.05, 0.05, 1.0),
    },
}


@dataclass(frozen=True)
class Config:
    desk_layout: str = "card_catalog"
    desk_frame: DeskFrame = "single_bank_open_knee"
    drawer_module: DrawerModule = "open_tray_guided"
    pull_style: PullStyle = "bar_pull"
    drawer_columns: int = 4
    drawer_rows: int = 3
    scale: float = 1.0
    drawer_travel_ratio: float = 0.50
    palette: Palette = "oak_brass"
    name: str = "desk_with_drawer_card_catalog"


@dataclass(frozen=True)
class ResolvedConfig:
    desk_frame: DeskFrame
    drawer_module: DrawerModule
    pull_style: PullStyle
    drawer_columns: int
    drawer_rows: int
    drawer_count: int
    scale: float
    drawer_travel_ratio: float
    palette: Palette
    rgba: dict[str, tuple[float, float, float, float]]
    desk_width: float
    desk_depth: float
    desk_height: float
    top_t: float
    bank_width: float
    bank_depth: float
    bank_bottom: float
    bank_top: float
    wall_t: float
    divider_t: float
    opening_width: float
    opening_height: float
    face_width: float
    face_height: float
    face_t: float
    tray_width: float
    tray_height: float
    tray_depth: float
    tray_wall_t: float
    tray_bottom_t: float
    rail_w: float
    rail_h: float
    rail_depth: float
    drawer_travel: float
    bank_center_x: float
    front_y: float
    column_centers: tuple[float, ...]
    row_centers: tuple[float, ...]
    name: str


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x4341_5244_4445_534B)
    selected = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        desk_frame=selected["desk_frame"],
        drawer_module=selected["drawer_module"],
        pull_style=selected["pull_style"],
        drawer_columns=selected["drawer_columns"],
        drawer_rows=selected["drawer_rows"],
        scale=round(rng.uniform(0.92, 1.08), 4),
        drawer_travel_ratio=round(rng.uniform(0.38, 0.62), 4),
        palette=rng.choice(tuple(_PALETTES)),
        name=f"desk_with_drawer_card_catalog_seed_{int(seed)}",
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    config = config_from_seed(seed)
    return (
        ("desk_frame", config.desk_frame),
        ("drawer_module", config.drawer_module),
        ("pull_style", config.pull_style),
        ("drawer_columns", str(config.drawer_columns)),
        ("drawer_rows", str(config.drawer_rows)),
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "desk_frame": config.desk_frame,
            "drawer_module": config.drawer_module,
            "pull_style": config.pull_style,
            "drawer_columns": config.drawer_columns,
            "drawer_rows": config.drawer_rows,
        }
    )
    if not 0.92 <= float(config.scale) <= 1.08:
        raise ValueError("scale must be in [0.92, 1.08]")
    if not 0.38 <= float(config.drawer_travel_ratio) <= 0.62:
        raise ValueError("drawer_travel_ratio must be in [0.38, 0.62]")
    if config.palette not in _PALETTES:
        raise ValueError(f"unsupported palette: {config.palette}")

    s = float(config.scale)
    desk_width = 1.60 * s
    desk_depth = 0.70 * s
    desk_height = 0.81 * s
    top_t = 0.048 * s
    if config.desk_frame == "four_leg_apron_bank":
        bank_width = desk_width - 0.12 * s  # full-width apron bank, inset at legs
        bank_center_x = 0.0
    elif config.desk_frame == "trestle_open_bay":
        bank_width = 0.84 * s  # centered bank between the trestle ends
        bank_center_x = 0.0
    else:  # single_bank_open_knee: right-side bank leaves a left knee bay
        bank_width = 0.84 * s
        bank_center_x = desk_width / 2.0 - 0.10 * s - bank_width / 2.0
    bank_depth = 0.60 * s
    bank_bottom = 0.075 * s
    bank_top = desk_height - top_t
    wall_t = 0.024 * s
    divider_t = 0.016 * s
    inner_w = bank_width - 2.0 * wall_t
    inner_h = bank_top - bank_bottom - 2.0 * wall_t
    opening_width = (
        inner_w - (int(config.drawer_columns) - 1) * divider_t
    ) / int(config.drawer_columns)
    opening_height = (
        inner_h - (int(config.drawer_rows) - 1) * divider_t
    ) / int(config.drawer_rows)
    if opening_width < 0.115 * s or opening_height < 0.090 * s:
        raise ValueError("resolved catalog grid openings are below the capacity contract")

    face_width = opening_width - 0.007 * s
    face_height = opening_height - 0.007 * s
    face_t = 0.018 * s
    tray_width = face_width - 0.016 * s
    tray_height = face_height - 0.024 * s
    tray_depth = bank_depth - wall_t - 0.040 * s
    tray_wall_t = 0.009 * s
    tray_bottom_t = 0.009 * s
    rail_w = 0.003 * s
    rail_h = 0.014 * s
    rail_depth = tray_depth - 0.030 * s
    drawer_travel = tray_depth * float(config.drawer_travel_ratio)
    front_y = -bank_depth / 2.0
    inner_left = bank_center_x - bank_width / 2.0 + wall_t
    inner_bottom = bank_bottom + wall_t
    column_centers = tuple(
        inner_left + opening_width / 2.0 + c * (opening_width + divider_t)
        for c in range(int(config.drawer_columns))
    )
    row_centers = tuple(
        inner_bottom + opening_height / 2.0 + r * (opening_height + divider_t)
        for r in range(int(config.drawer_rows))
    )
    return ResolvedConfig(
        desk_frame=config.desk_frame,
        drawer_module=config.drawer_module,
        pull_style=config.pull_style,
        drawer_columns=int(config.drawer_columns),
        drawer_rows=int(config.drawer_rows),
        drawer_count=int(config.drawer_columns) * int(config.drawer_rows),
        scale=s,
        drawer_travel_ratio=float(config.drawer_travel_ratio),
        palette=config.palette,
        rgba=_PALETTES[config.palette],
        desk_width=desk_width,
        desk_depth=desk_depth,
        desk_height=desk_height,
        top_t=top_t,
        bank_width=bank_width,
        bank_depth=bank_depth,
        bank_bottom=bank_bottom,
        bank_top=bank_top,
        wall_t=wall_t,
        divider_t=divider_t,
        opening_width=opening_width,
        opening_height=opening_height,
        face_width=face_width,
        face_height=face_height,
        face_t=face_t,
        tray_width=tray_width,
        tray_height=tray_height,
        tray_depth=tray_depth,
        tray_wall_t=tray_wall_t,
        tray_bottom_t=tray_bottom_t,
        rail_w=rail_w,
        rail_h=rail_h,
        rail_depth=rail_depth,
        drawer_travel=drawer_travel,
        bank_center_x=bank_center_x,
        front_y=front_y,
        column_centers=column_centers,
        row_centers=row_centers,
        name=config.name,
    )


def _wood_box(part, name: str, size, xyz, material, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.engineered_board")


def _metal_box(part, name: str, size, xyz, material, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.steel_bare")


def _paper_box(part, name: str, size, xyz, material) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="paper.plain_sheet")


def _worktop_build(frame, r: ResolvedConfig, wood) -> None:
    _wood_box(frame, f"desk_frame__{r.desk_frame}__work_surface", (r.desk_width, r.desk_depth, r.top_t), (0.0, 0.0, r.desk_height - r.top_t / 2.0), wood)
    _wood_box(frame, f"desk_frame__{r.desk_frame}__front_edge_band", (r.desk_width, 0.012 * r.scale, r.top_t + 0.002 * r.scale), (0.0, -r.desk_depth / 2.0 + 0.006 * r.scale, r.desk_height - r.top_t / 2.0), wood)


def _bank_carcass_build(model: ArticulatedObject, frame, r: ResolvedConfig, wood, metal) -> None:
    """Shared grid-bank carcass: walls, plinth, dividers, shelves, fixed rails."""
    s = r.scale
    prefix = f"desk_frame__{r.desk_frame}"
    side_x = r.bank_width / 2.0 - r.wall_t / 2.0
    bank_mid_z = (r.bank_bottom + r.bank_top) / 2.0
    bank_h = r.bank_top - r.bank_bottom
    for side, x in enumerate((r.bank_center_x - side_x, r.bank_center_x + side_x)):
        _wood_box(frame, f"{prefix}__bank_side_{side}", (r.wall_t, r.bank_depth, bank_h), (x, 0.0, bank_mid_z), wood)
    _wood_box(frame, f"{prefix}__bank_back", (r.bank_width - 2.0 * r.wall_t, r.wall_t, bank_h), (r.bank_center_x, r.bank_depth / 2.0 - r.wall_t / 2.0, bank_mid_z), wood)
    _wood_box(frame, f"{prefix}__bank_bottom", (r.bank_width, r.bank_depth, r.wall_t), (r.bank_center_x, 0.0, r.bank_bottom + r.wall_t / 2.0), wood)
    _wood_box(frame, f"{prefix}__bank_top", (r.bank_width, r.bank_depth, r.wall_t), (r.bank_center_x, 0.0, r.bank_top - r.wall_t / 2.0), wood)
    _wood_box(frame, f"{prefix}__bank_plinth", (r.bank_width * 0.92, r.bank_depth * 0.90, r.bank_bottom), (r.bank_center_x, 0.018 * s, r.bank_bottom / 2.0), wood)

    inner_left = r.bank_center_x - r.bank_width / 2.0 + r.wall_t
    inner_bottom = r.bank_bottom + r.wall_t
    inner_h = r.bank_top - r.bank_bottom - 2.0 * r.wall_t
    inner_w = r.bank_width - 2.0 * r.wall_t
    for col in range(1, r.drawer_columns):
        x = inner_left + col * r.opening_width + (col - 0.5) * r.divider_t
        _wood_box(frame, f"{prefix}__column_divider_{col}", (r.divider_t, r.bank_depth - r.wall_t, inner_h), (x, -r.wall_t / 2.0, inner_bottom + inner_h / 2.0), wood)
    for row in range(1, r.drawer_rows):
        z = inner_bottom + row * r.opening_height + (row - 0.5) * r.divider_t
        _wood_box(frame, f"{prefix}__row_shelf_{row}", (inner_w, r.bank_depth - r.wall_t, r.divider_t), (r.bank_center_x, -r.wall_t / 2.0, z), wood)

    rail_y = r.front_y + 0.022 * s + r.rail_depth / 2.0
    for row, zc in enumerate(r.row_centers):
        rail_bottom = zc - r.face_height / 2.0 + r.tray_bottom_t
        rail_z = rail_bottom + r.rail_h / 2.0
        for col, xc in enumerate(r.column_centers):
            rail_dx = r.tray_width / 2.0 + 1.5 * r.rail_w
            for side, x in enumerate((xc - rail_dx, xc + rail_dx)):
                rail_name = f"{prefix}__fixed_rail_{row}_{col}_{side}"
                rail = model.part(rail_name, meta={"role": "drawer_guide"})
                _metal_box(rail, rail_name, (r.rail_w, r.rail_depth, r.rail_h), (0.0, 0.0, 0.0), metal)
                rail.inertial = Inertial.from_geometry(
                    Box((r.rail_w, r.rail_depth, r.rail_h)),
                    mass=0.10 * r.scale**3,
                )
                model.articulation(
                    f"desk_frame_to_fixed_rail_{row}_{col}_{side}",
                    ArticulationType.FIXED,
                    parent=frame,
                    child=rail,
                    origin=Origin(xyz=(x, rail_y, rail_z)),
                )


def _desk_frame_single_bank_open_knee_build(model: ArticulatedObject, r: ResolvedConfig):
    frame = model.part(
        "desk_frame__single_bank_open_knee__frame",
        meta={"role": "desk_frame"},
    )
    wood = model.material("frame_wood_preview", rgba=r.rgba["case"])
    metal = model.material("rail_preview", rgba=r.rgba["metal"])
    s = r.scale

    _worktop_build(frame, r, wood)

    left_x = -r.desk_width / 2.0 + 0.10 * s + r.wall_t / 2.0
    _wood_box(frame, "desk_frame__single_bank_open_knee__left_support_panel", (r.wall_t, r.bank_depth, r.bank_top - r.bank_bottom), (left_x, 0.0, (r.bank_top + r.bank_bottom) / 2.0), wood)
    _wood_box(frame, "desk_frame__single_bank_open_knee__left_foot", (0.060 * s, r.bank_depth * 0.92, r.bank_bottom), (left_x, 0.0, r.bank_bottom / 2.0), wood)

    knee_left = left_x + r.wall_t / 2.0
    knee_right = r.bank_center_x - r.bank_width / 2.0
    knee_width = knee_right - knee_left
    _wood_box(frame, "desk_frame__single_bank_open_knee__modesty_panel", (knee_width, 0.016 * s, 0.20 * s), ((knee_left + knee_right) / 2.0, r.bank_depth / 2.0 - 0.018 * s, r.bank_top - 0.12 * s), wood)
    _wood_box(frame, "desk_frame__single_bank_open_knee__knee_rail", (knee_width, 0.026 * s, 0.032 * s), ((knee_left + knee_right) / 2.0, 0.0, r.bank_top - 0.028 * s), wood)

    _bank_carcass_build(model, frame, r, wood, metal)

    frame.inertial = Inertial.from_geometry(
        Box((r.desk_width, r.desk_depth, r.desk_height)),
        mass=52.0 * r.scale**3,
        origin=Origin(xyz=(0.0, 0.0, r.desk_height / 2.0)),
    )
    return frame


def _desk_frame_four_leg_apron_bank_build(model: ArticulatedObject, r: ResolvedConfig):
    frame = model.part(
        "desk_frame__four_leg_apron_bank__frame",
        meta={"role": "desk_frame"},
    )
    wood = model.material("frame_wood_preview", rgba=r.rgba["case"])
    metal = model.material("rail_preview", rgba=r.rgba["metal"])
    s = r.scale

    _worktop_build(frame, r, wood)

    leg_size = (0.055 * s, 0.055 * s, r.bank_bottom)
    leg_x = r.desk_width / 2.0 - 0.06 * s
    leg_y = r.desk_depth / 2.0 - 0.06 * s
    for idx, (x, y) in enumerate(
        ((-leg_x, -leg_y), (leg_x, -leg_y), (-leg_x, leg_y), (leg_x, leg_y))
    ):
        _wood_box(frame, f"desk_frame__four_leg_apron_bank__leg_{idx}", leg_size, (x, y, r.bank_bottom / 2.0), wood)

    _bank_carcass_build(model, frame, r, wood, metal)

    frame.inertial = Inertial.from_geometry(
        Box((r.desk_width, r.desk_depth, r.desk_height)),
        mass=54.0 * r.scale**3,
        origin=Origin(xyz=(0.0, 0.0, r.desk_height / 2.0)),
    )
    return frame


def _desk_frame_trestle_open_bay_build(model: ArticulatedObject, r: ResolvedConfig):
    frame = model.part(
        "desk_frame__trestle_open_bay__frame",
        meta={"role": "desk_frame"},
    )
    wood = model.material("frame_wood_preview", rgba=r.rgba["case"])
    metal = model.material("rail_preview", rgba=r.rgba["metal"])
    s = r.scale

    _worktop_build(frame, r, wood)

    # Two end trestles: foot pad + post + top cleat, joined by a low stretcher.
    post_h = r.desk_height - r.top_t
    trestle_x = r.desk_width / 2.0 - 0.09 * s
    for side, x in enumerate((-trestle_x, trestle_x)):
        _wood_box(frame, f"desk_frame__trestle_open_bay__foot_{side}", (0.10 * s, r.bank_depth * 0.92, 0.030 * s), (x, 0.0, 0.015 * s), wood)
        _wood_box(frame, f"desk_frame__trestle_open_bay__post_{side}", (0.045 * s, 0.060 * s, post_h - 0.030 * s), (x, 0.0, 0.030 * s + (post_h - 0.030 * s) / 2.0), wood)
        _wood_box(frame, f"desk_frame__trestle_open_bay__cleat_{side}", (0.14 * s, 0.045 * s, 0.030 * s), (x, 0.0, post_h - 0.015 * s), wood)
    _wood_box(frame, "desk_frame__trestle_open_bay__stretcher", (2.0 * trestle_x - 0.045 * s, 0.040 * s, 0.035 * s), (0.0, 0.0, r.bank_bottom / 2.0), wood)

    _bank_carcass_build(model, frame, r, wood, metal)

    frame.inertial = Inertial.from_geometry(
        Box((r.desk_width, r.desk_depth, r.desk_height)),
        mass=48.0 * r.scale**3,
        origin=Origin(xyz=(0.0, 0.0, r.desk_height / 2.0)),
    )
    return frame


_FRAME_BUILDERS = {
    "single_bank_open_knee": _desk_frame_single_bank_open_knee_build,
    "four_leg_apron_bank": _desk_frame_four_leg_apron_bank_build,
    "trestle_open_bay": _desk_frame_trestle_open_bay_build,
}


def _pull_build(drawer, r: ResolvedConfig, metal, dark, prefix: str) -> None:
    """One of four source-backed pull treatments on the drawer front (-Y face)."""
    s = r.scale
    face_width, face_height, face_t = r.face_width, r.face_height, r.face_t
    if r.pull_style == "knob_pair":
        knob_dx = min(face_width * 0.25, 0.035 * s)
        for side, x in enumerate((-knob_dx, knob_dx)):
            drawer.visual(Cylinder(radius=0.011 * s, length=0.004 * s), origin=Origin(xyz=(x, -face_t - 0.002 * s, -face_height * 0.20), rpy=(math.pi / 2.0, 0.0, 0.0)), material=metal, name=f"{prefix}__pull_knob_base_{side}", material_class_id="metal.steel_bare")
            drawer.visual(Cylinder(radius=0.008 * s, length=0.018 * s), origin=Origin(xyz=(x, -face_t - 0.011 * s, -face_height * 0.20), rpy=(math.pi / 2.0, 0.0, 0.0)), material=metal, name=f"{prefix}__pull_knob_{side}", material_class_id="metal.steel_bare")
    elif r.pull_style == "finger_slot":
        slot_w = min(face_width * 0.60, 0.100 * s)
        _wood_box(drawer, f"{prefix}__pull_finger_slot", (slot_w, 0.006 * s, 0.018 * s), (0.0, -face_t - 0.002 * s, -face_height * 0.15), dark)
    elif r.pull_style == "recessed_oval":
        oval_r = min(face_width * 0.28, 0.030 * s)
        drawer.visual(Cylinder(radius=oval_r, length=0.008 * s), origin=Origin(xyz=(0.0, -face_t - 0.003 * s, -face_height * 0.18), rpy=(math.pi / 2.0, 0.0, 0.0)), material=metal, name=f"{prefix}__pull_recessed_oval", material_class_id="metal.steel_bare")
        drawer.visual(Cylinder(radius=oval_r * 0.72, length=0.004 * s), origin=Origin(xyz=(0.0, -face_t - 0.006 * s, -face_height * 0.18), rpy=(math.pi / 2.0, 0.0, 0.0)), material=dark, name=f"{prefix}__pull_recessed_oval_inset", material_class_id="metal.steel_bare")
    else:  # bar_pull: twin posts + horizontal bar
        pull_w = min(face_width * 0.55, 0.095 * s)
        for side, x in enumerate((-pull_w / 2.0, pull_w / 2.0)):
            drawer.visual(Cylinder(radius=0.0045 * s, length=0.022 * s), origin=Origin(xyz=(x, -face_t - 0.011 * s, -face_height * 0.23), rpy=(math.pi / 2.0, 0.0, 0.0)), material=metal, name=f"{prefix}__pull_post_{side}", material_class_id="metal.steel_bare")
        drawer.visual(Cylinder(radius=0.005 * s, length=pull_w), origin=Origin(xyz=(0.0, -face_t - 0.023 * s, -face_height * 0.23), rpy=(0.0, math.pi / 2.0, 0.0)), material=metal, name=f"{prefix}__pull_bar", material_class_id="metal.steel_bare")


def _label_build(drawer, r: ResolvedConfig, metal, paper, prefix: str, label_z: float) -> None:
    s = r.scale
    label_w = min(r.face_width * 0.58, 0.105 * s)
    label_h = min(r.face_height * 0.24, 0.035 * s)
    bar_t = 0.004 * s
    label_y = -r.face_t - bar_t / 2.0
    _paper_box(drawer, f"{prefix}__label_card", (label_w, 0.0015 * s, label_h), (0.0, -r.face_t - 0.00075 * s, label_z), paper)
    for tag, size, xyz in (
        ("label_frame_top", (label_w + 0.010 * s, bar_t, bar_t), (0.0, label_y, label_z + label_h / 2.0 + bar_t / 2.0)),
        ("label_frame_bottom", (label_w + 0.010 * s, bar_t, bar_t), (0.0, label_y, label_z - label_h / 2.0 - bar_t / 2.0)),
        ("label_frame_left", (bar_t, bar_t, label_h + 0.012 * s), (-label_w / 2.0 - bar_t / 2.0, label_y, label_z)),
        ("label_frame_right", (bar_t, bar_t, label_h + 0.012 * s), (label_w / 2.0 + bar_t / 2.0, label_y, label_z)),
    ):
        _metal_box(drawer, f"{prefix}__{tag}", size, xyz, metal)


def _drawer_joint_build(model: ArticulatedObject, frame, drawer, r: ResolvedConfig, row: int, col: int):
    provider = PlaneInterface(point=(r.column_centers[col], r.front_y, r.row_centers[row]), normal=(0.0, -1.0, 0.0), tangent_u=(1.0, 0.0, 0.0), extent=(r.opening_width, r.opening_height), name=f"drawer_grid_{row}_{col}")
    consumer = PlaneInterface(point=(0.0, 0.0, 0.0), normal=(0.0, 1.0, 0.0), tangent_u=(1.0, 0.0, 0.0), extent=(r.face_width, r.face_height), name=f"tray_mount_{row}_{col}")
    mate = mate_planes(provider, consumer, margin=0.002 * r.scale)
    joint = model.articulation(
        f"desk_frame_to_catalog_drawer_{row}_{col}",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=drawer,
        origin=mate.origin,
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=45.0, velocity=0.30, lower=0.0, upper=r.drawer_travel),
        motion_properties=MotionProperties(damping=5.0, friction=2.5),
        meta={"motion_qc_repeat_group": "catalog_drawer_slides"},
    )
    drawer.inertial = Inertial.from_geometry(
        Box((r.face_width, r.tray_depth + r.face_t, r.face_height)),
        mass=1.1 * r.scale**3,
        origin=Origin(xyz=(0.0, r.tray_depth / 2.0, 0.0)),
    )
    return joint


def _drawer_module_open_tray_guided_build(model: ArticulatedObject, r: ResolvedConfig, frame, row: int, col: int):
    prefix = "drawer_module__open_tray_guided"
    drawer = model.part(f"{prefix}__drawer_{row}_{col}", meta={"role": "catalog_drawer"})
    suffix = f"{row}_{col}"
    wood = model.material(f"drawer_wood_preview_{suffix}", rgba=r.rgba["case"])
    metal = model.material(f"drawer_metal_preview_{suffix}", rgba=r.rgba["metal"])
    paper = model.material(f"label_preview_{suffix}", rgba=r.rgba["paper"])
    dark = model.material(f"drawer_recess_preview_{suffix}", rgba=r.rgba["recess"])
    s = r.scale

    _wood_box(drawer, f"{prefix}__front", (r.face_width, r.face_t, r.face_height), (0.0, -r.face_t / 2.0, 0.0), wood)
    bottom_z = -r.face_height / 2.0 + r.tray_bottom_t / 2.0
    _wood_box(drawer, f"{prefix}__tray_bottom", (r.tray_width, r.tray_depth, r.tray_bottom_t), (0.0, r.tray_depth / 2.0, bottom_z), wood)
    wall_z = -r.face_height / 2.0 + r.tray_height / 2.0
    side_x = r.tray_width / 2.0 - r.tray_wall_t / 2.0
    for side, x in enumerate((-side_x, side_x)):
        _wood_box(drawer, f"{prefix}__tray_side_{side}", (r.tray_wall_t, r.tray_depth, r.tray_height), (x, r.tray_depth / 2.0, wall_z), wood)
        runner_x = x + (-1.0 if x < 0.0 else 1.0) * (r.tray_wall_t / 2.0 + r.rail_w / 2.0)
        _metal_box(drawer, f"{prefix}__moving_runner_{side}", (r.rail_w, r.rail_depth, r.rail_h), (runner_x, 0.022 * s + r.rail_depth / 2.0, -r.face_height / 2.0 + r.tray_bottom_t - r.rail_h / 2.0), metal)
    _wood_box(drawer, f"{prefix}__tray_rear", (r.tray_width, r.tray_wall_t, r.tray_height), (0.0, r.tray_depth - r.tray_wall_t / 2.0, wall_z), wood)

    _label_build(drawer, r, metal, paper, prefix, label_z=r.face_height * 0.18)
    _pull_build(drawer, r, metal, dark, prefix)
    _drawer_joint_build(model, frame, drawer, r, row, col)
    return drawer


def _drawer_module_boxed_full_front_build(model: ArticulatedObject, r: ResolvedConfig, frame, row: int, col: int):
    prefix = "drawer_module__boxed_full_front"
    drawer = model.part(f"{prefix}__drawer_{row}_{col}", meta={"role": "catalog_drawer"})
    suffix = f"{row}_{col}"
    wood = model.material(f"drawer_wood_preview_{suffix}", rgba=r.rgba["case"])
    metal = model.material(f"drawer_metal_preview_{suffix}", rgba=r.rgba["metal"])
    paper = model.material(f"label_preview_{suffix}", rgba=r.rgba["paper"])
    dark = model.material(f"drawer_recess_preview_{suffix}", rgba=r.rgba["recess"])
    s = r.scale

    # Tall overlay front: the lip overlaps the grid dividers like upstream
    # lip-front drawer banks.
    lip_h = r.face_height + 0.010 * s
    _wood_box(drawer, f"{prefix}__front", (r.face_width, r.face_t, lip_h), (0.0, -r.face_t / 2.0, 0.0), wood)
    bottom_z = -r.face_height / 2.0 + r.tray_bottom_t / 2.0
    _wood_box(drawer, f"{prefix}__tray_bottom", (r.tray_width, r.tray_depth, r.tray_bottom_t), (0.0, r.tray_depth / 2.0, bottom_z), wood)
    wall_z = -r.face_height / 2.0 + r.tray_height / 2.0
    side_x = r.tray_width / 2.0 - r.tray_wall_t / 2.0
    for side, x in enumerate((-side_x, side_x)):
        _wood_box(drawer, f"{prefix}__tray_side_{side}", (r.tray_wall_t, r.tray_depth, r.tray_height), (x, r.tray_depth / 2.0, wall_z), wood)
        runner_x = x + (-1.0 if x < 0.0 else 1.0) * (r.tray_wall_t / 2.0 + r.rail_w / 2.0)
        _metal_box(drawer, f"{prefix}__moving_runner_{side}", (r.rail_w, r.rail_depth, r.rail_h), (runner_x, 0.022 * s + r.rail_depth / 2.0, -r.face_height / 2.0 + r.tray_bottom_t - r.rail_h / 2.0), metal)
    _wood_box(drawer, f"{prefix}__tray_rear", (r.tray_width, r.tray_wall_t, r.tray_height), (0.0, r.tray_depth - r.tray_wall_t / 2.0, wall_z), wood)

    _label_build(drawer, r, metal, paper, prefix, label_z=r.face_height * 0.22)
    _pull_build(drawer, r, metal, dark, prefix)
    _drawer_joint_build(model, frame, drawer, r, row, col)
    return drawer


_DRAWER_BUILDERS = {
    "open_tray_guided": _drawer_module_open_tray_guided_build,
    "boxed_full_front": _drawer_module_boxed_full_front_build,
}


def build_desk_with_drawer(config: Config | None = None, *, assets: AssetContext | None = None) -> ArticulatedObject:
    config = config or Config()
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    frame = _FRAME_BUILDERS[r.desk_frame](model, r)
    drawer_build = _DRAWER_BUILDERS[r.drawer_module]
    for row in range(r.drawer_rows):
        for col in range(r.drawer_columns):
            drawer_build(model, r, frame, row, col)
    model.meta["template_choices"] = (
        ("desk_frame", r.desk_frame),
        ("drawer_module", r.drawer_module),
        ("pull_style", r.pull_style),
        ("drawer_columns", str(r.drawer_columns)),
        ("drawer_rows", str(r.drawer_rows)),
    )
    return model


def build_seeded_desk_with_drawer_card_catalog(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_desk_with_drawer(config_from_seed(seed), assets=assets)


def run_desk_with_drawer_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    roles: dict[str, list[str]] = {}
    parts = {part.name: part for part in object_model.parts}
    for part in object_model.parts:
        role = str(part.meta.get("role") or "")
        if role:
            roles.setdefault(role, []).append(part.name)
    ctx.check("category_anchor: one load-bearing desk frame", len(roles.get("desk_frame", [])) == 1, details=str(roles))
    drawer_names = roles.get("catalog_drawer", [])
    ctx.check("category_anchor: catalog drawer grid count matches rows times columns", len(drawer_names) == r.drawer_count, details=f"actual={len(drawer_names)} expected={r.drawer_rows}x{r.drawer_columns}={r.drawer_count}")
    moving = {joint.child: joint for joint in object_model.articulations if joint.articulation_type != ArticulationType.FIXED}
    frame_name = roles.get("desk_frame", [""])[0]
    ctx.check("category_anchor: every catalog drawer is a moving child of desk frame", len(drawer_names) == r.drawer_count and all(name in moving and moving[name].parent == frame_name and moving[name].articulation_type == ArticulationType.PRISMATIC for name in drawer_names), details=f"drawers={drawer_names}")

    module_prefix = f"drawer_module__{r.drawer_module}"
    required_visuals = (
        f"{module_prefix}__tray_bottom",
        f"{module_prefix}__tray_side_0",
        f"{module_prefix}__tray_side_1",
        f"{module_prefix}__tray_rear",
        f"{module_prefix}__front",
    )
    hollow = True
    pulls_ok = True
    for name in drawer_names:
        visual_names = {str(visual.name) for visual in parts[name].visuals}
        hollow = hollow and all(required in visual_names for required in required_visuals)
        pulls_ok = pulls_ok and any("__pull_" in visual_name for visual_name in visual_names)
    ctx.check("category_anchor: catalog drawers are hollow guided trays", hollow, details="front + floor + two sides + rear required on every drawer")
    ctx.check("every catalog drawer carries its configured pull", pulls_ok, details=f"pull_style={r.pull_style}")

    axes_ok = all(tuple(round(float(v), 6) for v in moving[name].axis) == (0.0, -1.0, 0.0) for name in drawer_names)
    first = drawer_names[0]
    rest = ctx.part_world_position(parts[first])
    with ctx.pose({moving[first]: r.drawer_travel}):
        opened = ctx.part_world_position(parts[first])
    ctx.check("category_anchor: drawers pull out along -Y", axes_ok and rest is not None and opened is not None and opened[1] < rest[1] - 0.9 * r.drawer_travel, details=f"rest={rest} opened={opened}")
    ctx.check("catalog drawer runner engagement remains positive", r.drawer_travel <= r.tray_depth * 0.62 and r.rail_depth - r.drawer_travel >= 0.12 * r.scale, details=f"travel={r.drawer_travel:.4f} rail_depth={r.rail_depth:.4f}")
    return ctx.report()


run_desk_with_drawer_tests.__test__ = False


TEMPLATE_CORNERS = (
    corner_case("minimum_grid_open_knee_short_travel", {"desk_frame": "single_bank_open_knee", "drawer_module": "open_tray_guided", "pull_style": "bar_pull", "drawer_columns": 2, "drawer_rows": 2, "scale": 0.92, "drawer_travel_ratio": 0.38}, reason="sparsest grid, smallest host, shortest stroke"),
    corner_case("maximum_grid_open_knee_long_travel", {"desk_frame": "single_bank_open_knee", "drawer_module": "open_tray_guided", "pull_style": "bar_pull", "drawer_columns": 6, "drawer_rows": 6, "scale": 1.08, "drawer_travel_ratio": 0.62}, reason="densest grid, largest host, longest permitted stroke"),
    corner_case("apron_bank_knob_pair_wide_cells", {"desk_frame": "four_leg_apron_bank", "drawer_module": "boxed_full_front", "pull_style": "knob_pair", "drawer_columns": 2, "drawer_rows": 6, "scale": 1.08, "drawer_travel_ratio": 0.50}, reason="widest openings on the full-width apron bank"),
    corner_case("apron_bank_recessed_oval_dense", {"desk_frame": "four_leg_apron_bank", "drawer_module": "open_tray_guided", "pull_style": "recessed_oval", "drawer_columns": 6, "drawer_rows": 5, "scale": 0.92, "drawer_travel_ratio": 0.62}, reason="dense apron grid at minimum scale and longest stroke"),
    corner_case("trestle_finger_slot_minimum", {"desk_frame": "trestle_open_bay", "drawer_module": "open_tray_guided", "pull_style": "finger_slot", "drawer_columns": 5, "drawer_rows": 6, "scale": 0.92, "drawer_travel_ratio": 0.38}, reason="tightest centered bank openings near the capacity contract"),
    corner_case("trestle_boxed_knob_maximum", {"desk_frame": "trestle_open_bay", "drawer_module": "boxed_full_front", "pull_style": "knob_pair", "drawer_columns": 3, "drawer_rows": 3, "scale": 1.08, "drawer_travel_ratio": 0.62}, reason="boxed overlay fronts on the trestle host at maximum scale"),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_desk_with_drawer",
    "build_seeded_desk_with_drawer_card_catalog",
    "config_from_seed",
    "resolve_config",
    "run_desk_with_drawer_tests",
    "slot_choices_for_seed",
]
