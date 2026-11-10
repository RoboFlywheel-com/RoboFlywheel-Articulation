# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import random
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

# ---------------------------------------------------------------------------
# Type aliases for the discrete style knobs in spec section 7.
# ---------------------------------------------------------------------------

SizeClass = Literal["mini", "standard", "tall"]
DoorLayout = Literal[
    "single",
    "top_freezer",
    "bottom_freezer",
    "side_by_side",
    "t_type_1up_2down",
    "three_door_stacked",
    "french_3door",
    "french_4door",
    "four_door_stacked",
]
HandleStyle = Literal["vertical", "horizontal", "recessed"]
DispenserKind = Literal["none", "water", "ice"]
GasketStyle = Literal["thin", "thick", "dark"]
MaterialStyle = Literal["white", "stainless", "black", "retro"]


# Coordinate convention:
#   Body origin sits at the floor center (z = 0 at ground beneath the unit).
#   +X = right, -X = left.
#   +Y = back of the refrigerator, -Y = front (door face).
#   +Z = up.
# Door coordinate convention:
#   Each door's joint origin is placed at the hinge vertical line on the front
#   face of the body. The door part's local frame has +X pointing away from the
#   hinge along the door width, +Z up. The door panel is centered at
#   (door_width/2, 0, door_height/2) in the door's local frame.


# ---------------------------------------------------------------------------
# Per-size-class envelope ranges. Size class is the discrete bucket and the
# continuous (W, H, D) values are sampled per-class to satisfy the
# 「离散桶 + 连续范围」 requirement in section 0 of 0_revised.md.
# ---------------------------------------------------------------------------

SIZE_WIDTH_RANGES: dict[SizeClass, tuple[float, float]] = {
    "mini": (0.45, 0.58),
    "standard": (0.60, 0.82),
    "tall": (0.72, 0.95),
}
SIZE_HEIGHT_RANGES: dict[SizeClass, tuple[float, float]] = {
    "mini": (0.85, 1.10),
    "standard": (1.55, 1.80),
    "tall": (1.80, 2.05),
}
SIZE_DEPTH_RANGES: dict[SizeClass, tuple[float, float]] = {
    "mini": (0.50, 0.60),
    "standard": (0.58, 0.72),
    "tall": (0.62, 0.78),
}


DOOR_COUNT_BY_LAYOUT: dict[DoorLayout, int] = {
    "single": 1,
    "top_freezer": 2,
    "bottom_freezer": 2,
    "side_by_side": 2,
    "t_type_1up_2down": 3,
    "three_door_stacked": 3,
    "french_3door": 3,
    "french_4door": 4,
    "four_door_stacked": 4,
}


# Geometric constants (proportions, not absolute dimensions).
WALL_THICKNESS = 0.030
INTERIOR_LINER_OFFSET = 0.002
DOOR_THICKNESS = 0.055
DOOR_FRONT_GAP = 0.004  # clearance at the top and bottom of the door opening
DOOR_HINGE_FRONT_OFFSET = 0.014  # clears the 55 mm panel corner through 1.8 rad
HINGE_EDGE_INSET = 0.012  # how far from the body side wall the hinge axis sits
KICK_PLATE_HEIGHT = 0.060
TOP_VENT_HEIGHT = 0.018
HANDLE_PROTRUSION = 0.040
SHELF_THICKNESS = 0.010
DRAWER_FRONT_THICKNESS = 0.022
DRAWER_SIDE_THICKNESS = 0.008
DOOR_SHELF_RAIL_HEIGHT = 0.046
DOOR_SHELF_RAIL_THICKNESS = 0.010

# Material palettes per material_style.
# Keys: body, door, gasket, hardware, handle, kick, interior, accent
MATERIAL_PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "white": {
        "body": (0.94, 0.94, 0.92, 1.0),
        "door": (0.96, 0.96, 0.94, 1.0),
        "gasket_default": (0.18, 0.18, 0.19, 1.0),
        "hardware": (0.55, 0.56, 0.58, 1.0),
        "handle": (0.32, 0.33, 0.34, 1.0),
        "kick": (0.78, 0.78, 0.76, 1.0),
        "interior": (0.86, 0.88, 0.86, 1.0),
        "accent": (0.20, 0.40, 0.85, 1.0),
    },
    "stainless": {
        "body": (0.74, 0.75, 0.76, 1.0),
        "door": (0.80, 0.81, 0.82, 1.0),
        "gasket_default": (0.10, 0.10, 0.11, 1.0),
        "hardware": (0.40, 0.41, 0.43, 1.0),
        "handle": (0.45, 0.46, 0.48, 1.0),
        "kick": (0.55, 0.56, 0.58, 1.0),
        "interior": (0.86, 0.86, 0.84, 1.0),
        "accent": (0.10, 0.55, 0.95, 1.0),
    },
    "black": {
        "body": (0.12, 0.13, 0.14, 1.0),
        "door": (0.10, 0.10, 0.12, 1.0),
        "gasket_default": (0.04, 0.04, 0.05, 1.0),
        "hardware": (0.60, 0.61, 0.63, 1.0),
        "handle": (0.70, 0.72, 0.74, 1.0),
        "kick": (0.06, 0.07, 0.08, 1.0),
        "interior": (0.55, 0.56, 0.58, 1.0),
        "accent": (0.95, 0.75, 0.20, 1.0),
    },
    "retro": {
        "body": (0.78, 0.32, 0.28, 1.0),
        "door": (0.84, 0.36, 0.30, 1.0),
        "gasket_default": (0.18, 0.16, 0.16, 1.0),
        "hardware": (0.85, 0.82, 0.70, 1.0),
        "handle": (0.92, 0.88, 0.74, 1.0),
        "kick": (0.62, 0.24, 0.20, 1.0),
        "interior": (0.95, 0.94, 0.86, 1.0),
        "accent": (0.96, 0.92, 0.80, 1.0),
    },
}

GASKET_COLOR_OVERRIDE: dict[GasketStyle, tuple[float, float, float, float] | None] = {
    "thin": None,
    "thick": None,
    "dark": (0.04, 0.04, 0.05, 1.0),
}
GASKET_THICKNESS_BY_STYLE: dict[GasketStyle, float] = {
    "thin": 0.009,
    "thick": 0.012,
    "dark": 0.010,
}


@dataclass(frozen=True)
class RefrigeratorConfig:
    size_class: SizeClass = "standard"
    door_layout: DoorLayout = "top_freezer"
    freezer_ratio: float = 0.32
    handle_style: HandleStyle = "vertical"
    shelf_count: int = 3
    drawer_count: int = 1
    door_shelf_count: int = 2
    dispenser: DispenserKind = "none"
    gasket_style: GasketStyle = "thin"
    material_style: MaterialStyle = "white"
    body_width: float | None = None
    body_height: float | None = None
    body_depth: float | None = None
    name: str = "reference_refrigerator"


@dataclass(frozen=True)
class ResolvedRefrigeratorConfig:
    size_class: SizeClass
    door_layout: DoorLayout
    door_count: int
    freezer_ratio: float
    handle_style: HandleStyle
    shelf_count: int
    drawer_count: int
    door_shelf_count: int
    dispenser: DispenserKind
    gasket_style: GasketStyle
    material_style: MaterialStyle
    body_width: float
    body_height: float
    body_depth: float
    name: str


def config_from_seed(seed: int) -> RefrigeratorConfig:
    rng = random.Random(seed)
    size_class = rng.choices(
        ("mini", "standard", "tall"),
        weights=(0.20, 0.55, 0.25),
        k=1,
    )[0]
    body_width = round(rng.uniform(*SIZE_WIDTH_RANGES[size_class]), 3)
    body_height = round(rng.uniform(*SIZE_HEIGHT_RANGES[size_class]), 3)
    body_depth = round(rng.uniform(*SIZE_DEPTH_RANGES[size_class]), 3)

    # Mini fridges are dominated by single + top_freezer; larger units use full layout pool.
    if size_class == "mini":
        door_layout = rng.choices(
            ("single", "top_freezer", "bottom_freezer"),
            weights=(0.55, 0.30, 0.15),
            k=1,
        )[0]
    else:
        door_layout = rng.choice(
            (
                "single",
                "top_freezer",
                "bottom_freezer",
                "side_by_side",
                "t_type_1up_2down",
                "three_door_stacked",
                "french_3door",
                "french_4door",
                "four_door_stacked",
            )
        )

    freezer_ratio = round(rng.uniform(0.25, 0.50), 3)
    handle_style = rng.choices(
        ("vertical", "horizontal", "recessed"),
        weights=(0.55, 0.30, 0.15),
        k=1,
    )[0]
    shelf_count = rng.randint(2, 6)
    drawer_count = rng.choices((0, 1, 2, 3), weights=(0.30, 0.40, 0.20, 0.10), k=1)[0]
    door_shelf_count = rng.choices((0, 1, 2, 3, 4), weights=(0.20, 0.20, 0.30, 0.20, 0.10), k=1)[0]
    dispenser = rng.choices(
        ("none", "water", "ice"),
        weights=(0.60, 0.25, 0.15),
        k=1,
    )[0]
    gasket_style = rng.choice(("thin", "thick", "dark"))
    material_style = rng.choices(
        ("white", "stainless", "black", "retro"),
        weights=(0.30, 0.35, 0.20, 0.15),
        k=1,
    )[0]
    return RefrigeratorConfig(
        size_class=size_class,
        door_layout=door_layout,
        freezer_ratio=freezer_ratio,
        handle_style=handle_style,
        shelf_count=shelf_count,
        drawer_count=drawer_count,
        door_shelf_count=door_shelf_count,
        dispenser=dispenser,
        gasket_style=gasket_style,
        material_style=material_style,
        body_width=body_width,
        body_height=body_height,
        body_depth=body_depth,
        name=f"seeded_refrigerator_{seed}",
    )


def resolve_config(config: RefrigeratorConfig) -> ResolvedRefrigeratorConfig:
    if config.size_class not in SIZE_WIDTH_RANGES:
        raise ValueError(f"Unsupported size_class: {config.size_class}")
    if config.door_layout not in DOOR_COUNT_BY_LAYOUT:
        raise ValueError(f"Unsupported door_layout: {config.door_layout}")
    if not 0.20 <= config.freezer_ratio <= 0.55:
        raise ValueError("freezer_ratio must be in [0.20, 0.55]")
    if config.handle_style not in ("vertical", "horizontal", "recessed"):
        raise ValueError(f"Unsupported handle_style: {config.handle_style}")
    if not 2 <= config.shelf_count <= 6:
        raise ValueError("shelf_count must be in [2, 6]")
    if not 0 <= config.drawer_count <= 3:
        raise ValueError("drawer_count must be in [0, 3]")
    if not 0 <= config.door_shelf_count <= 4:
        raise ValueError("door_shelf_count must be in [0, 4]")
    if config.dispenser not in ("none", "water", "ice"):
        raise ValueError(f"Unsupported dispenser: {config.dispenser}")
    if config.gasket_style not in ("thin", "thick", "dark"):
        raise ValueError(f"Unsupported gasket_style: {config.gasket_style}")
    if config.material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    body_width = (
        config.body_width
        if config.body_width is not None
        else sum(SIZE_WIDTH_RANGES[config.size_class]) / 2.0
    )
    body_height = (
        config.body_height
        if config.body_height is not None
        else sum(SIZE_HEIGHT_RANGES[config.size_class]) / 2.0
    )
    body_depth = (
        config.body_depth
        if config.body_depth is not None
        else sum(SIZE_DEPTH_RANGES[config.size_class]) / 2.0
    )

    return ResolvedRefrigeratorConfig(
        size_class=config.size_class,
        door_layout=config.door_layout,
        door_count=DOOR_COUNT_BY_LAYOUT[config.door_layout],
        freezer_ratio=config.freezer_ratio,
        handle_style=config.handle_style,
        shelf_count=config.shelf_count,
        drawer_count=config.drawer_count,
        door_shelf_count=config.door_shelf_count,
        dispenser=config.dispenser,
        gasket_style=config.gasket_style,
        material_style=config.material_style,
        body_width=body_width,
        body_height=body_height,
        body_depth=body_depth,
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Door layout planning.
#
# Each "door slot" is a dict-like description of one door, expressed in body
# coordinates and including the geometry needed to derive its joint origin,
# door width/height/thickness and hinge side. All later door construction
# reads from this plan; nothing in `_build_door_*` does its own randomization.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DoorSlot:
    name: str  # e.g. "door_0"
    width: float  # door width along its local +X (extent away from hinge)
    height: float  # door height
    hinge_side: Literal["left", "right"]  # which side of its slot the hinge sits on
    # body-space coordinates of the hinge axis (front face plane)
    hinge_x: float
    hinge_y: float
    hinge_z_bottom: float  # bottom of the door (and door joint origin Z)
    role: Literal["fridge", "freezer"]
    # Slot center in body space (useful for sanity / dispenser placement).
    slot_center_x: float
    slot_center_z: float
    slot_width: float
    slot_height: float


def plan_doors(resolved: ResolvedRefrigeratorConfig) -> list[DoorSlot]:
    W = resolved.body_width
    H = resolved.body_height
    layout = resolved.door_layout
    front_y = -resolved.body_depth / 2.0

    # Total stack height available for doors equals body height minus kick plate.
    # Keep the articulated leaves inside the structural opening.  The previous
    # band ran through the cavity floor and top panel, so the perimeter gaskets
    # penetrated both panels in the closed pose.
    door_band_bottom = KICK_PLATE_HEIGHT + WALL_THICKNESS + DOOR_FRONT_GAP
    door_band_top = H - WALL_THICKNESS - DOOR_FRONT_GAP
    band_height = door_band_top - door_band_bottom

    slots: list[DoorSlot] = []

    def _slot(
        *,
        idx: int,
        slot_x_min: float,
        slot_x_max: float,
        slot_z_min: float,
        slot_z_max: float,
        hinge_side: Literal["left", "right"],
        role: Literal["fridge", "freezer"],
    ) -> DoorSlot:
        slot_w = slot_x_max - slot_x_min
        slot_h = slot_z_max - slot_z_min
        # Hinge x: on the requested side of the slot, inset slightly from the body edge if it
        # coincides with the body side wall; otherwise sits on the slot boundary.
        if hinge_side == "left":
            hinge_x = (
                slot_x_min + HINGE_EDGE_INSET if abs(slot_x_min + W / 2.0) < 1e-6 else slot_x_min
            )
        else:
            hinge_x = (
                slot_x_max - HINGE_EDGE_INSET if abs(slot_x_max - W / 2.0) < 1e-6 else slot_x_max
            )
        # Outer hinges are inset from the cabinet edge.  Subtract that inset
        # from the leaf width as well as the two seams; otherwise paired french
        # doors cross the centreline by 4 mm each.
        outer_hinge_inset = (
            HINGE_EDGE_INSET
            if (
                hinge_side == "left" and abs(slot_x_min + W / 2.0) < 1e-6
            )
            or (
                hinge_side == "right" and abs(slot_x_max - W / 2.0) < 1e-6
            )
            else 0.0
        )
        door_w = slot_w - outer_hinge_inset - 2.0 * 0.004
        door_h = slot_h - 2.0 * 0.004
        return DoorSlot(
            name=f"door_{idx}",
            width=door_w,
            height=door_h,
            hinge_side=hinge_side,
            hinge_x=hinge_x,
            hinge_y=front_y,
            hinge_z_bottom=slot_z_min + 0.004,
            role=role,
            slot_center_x=(slot_x_min + slot_x_max) / 2.0,
            slot_center_z=(slot_z_min + slot_z_max) / 2.0,
            slot_width=slot_w,
            slot_height=slot_h,
        )

    freezer_h = max(0.18, band_height * resolved.freezer_ratio)
    freezer_h = min(freezer_h, band_height - 0.22)  # keep fridge zone reasonable

    if layout == "single":
        slots.append(
            _slot(
                idx=0,
                slot_x_min=-W / 2.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_bottom,
                slot_z_max=door_band_top,
                hinge_side="right",
                role="fridge",
            )
        )
    elif layout == "top_freezer":
        # Freezer on top, fridge below; both full-width single doors.
        slots.append(
            _slot(
                idx=0,
                slot_x_min=-W / 2.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_top - freezer_h,
                slot_z_max=door_band_top,
                hinge_side="right",
                role="freezer",
            )
        )
        slots.append(
            _slot(
                idx=1,
                slot_x_min=-W / 2.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_bottom,
                slot_z_max=door_band_top - freezer_h,
                hinge_side="right",
                role="fridge",
            )
        )
    elif layout == "bottom_freezer":
        slots.append(
            _slot(
                idx=0,
                slot_x_min=-W / 2.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_bottom + freezer_h,
                slot_z_max=door_band_top,
                hinge_side="right",
                role="fridge",
            )
        )
        slots.append(
            _slot(
                idx=1,
                slot_x_min=-W / 2.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_bottom,
                slot_z_max=door_band_bottom + freezer_h,
                hinge_side="right",
                role="freezer",
            )
        )
    elif layout == "side_by_side":
        # Freezer on left, fridge on right. Both full-height.
        slots.append(
            _slot(
                idx=0,
                slot_x_min=-W / 2.0,
                slot_x_max=0.0,
                slot_z_min=door_band_bottom,
                slot_z_max=door_band_top,
                hinge_side="left",
                role="freezer",
            )
        )
        slots.append(
            _slot(
                idx=1,
                slot_x_min=0.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_bottom,
                slot_z_max=door_band_top,
                hinge_side="right",
                role="fridge",
            )
        )
    elif layout == "t_type_1up_2down":
        # Top: 1 full-width fridge door. Bottom: 2 half-width freezer doors.
        slots.append(
            _slot(
                idx=0,
                slot_x_min=-W / 2.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_bottom + freezer_h,
                slot_z_max=door_band_top,
                hinge_side="right",
                role="fridge",
            )
        )
        slots.append(
            _slot(
                idx=1,
                slot_x_min=-W / 2.0,
                slot_x_max=0.0,
                slot_z_min=door_band_bottom,
                slot_z_max=door_band_bottom + freezer_h,
                hinge_side="left",
                role="freezer",
            )
        )
        slots.append(
            _slot(
                idx=2,
                slot_x_min=0.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_bottom,
                slot_z_max=door_band_bottom + freezer_h,
                hinge_side="right",
                role="freezer",
            )
        )
    elif layout == "three_door_stacked":
        # 3 full-width doors stacked. Top = freezer band, middle = small fresh zone,
        # bottom = main fridge. We derive heights from freezer_ratio.
        top_h = freezer_h
        mid_h = max(0.18, band_height * 0.18)
        bot_h = band_height - top_h - mid_h
        if bot_h < 0.20:
            mid_h = max(0.14, band_height - top_h - 0.22)
            bot_h = band_height - top_h - mid_h
        slots.append(
            _slot(
                idx=0,
                slot_x_min=-W / 2.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_top - top_h,
                slot_z_max=door_band_top,
                hinge_side="right",
                role="freezer",
            )
        )
        slots.append(
            _slot(
                idx=1,
                slot_x_min=-W / 2.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_top - top_h - mid_h,
                slot_z_max=door_band_top - top_h,
                hinge_side="right",
                role="fridge",
            )
        )
        slots.append(
            _slot(
                idx=2,
                slot_x_min=-W / 2.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_bottom,
                slot_z_max=door_band_bottom + bot_h,
                hinge_side="right",
                role="fridge",
            )
        )
    elif layout == "french_3door":
        # Top: 2 half-width french fridge doors (hinges on outer edges).
        # Bottom: 1 full-width freezer drawer-style hinge door.
        slots.append(
            _slot(
                idx=0,
                slot_x_min=-W / 2.0,
                slot_x_max=0.0,
                slot_z_min=door_band_bottom + freezer_h,
                slot_z_max=door_band_top,
                hinge_side="left",
                role="fridge",
            )
        )
        slots.append(
            _slot(
                idx=1,
                slot_x_min=0.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_bottom + freezer_h,
                slot_z_max=door_band_top,
                hinge_side="right",
                role="fridge",
            )
        )
        slots.append(
            _slot(
                idx=2,
                slot_x_min=-W / 2.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_bottom,
                slot_z_max=door_band_bottom + freezer_h,
                hinge_side="right",
                role="freezer",
            )
        )
    elif layout == "french_4door":
        # Top: 2 half-width french fridge doors.
        # Bottom: 2 half-width freezer compartments.
        slots.append(
            _slot(
                idx=0,
                slot_x_min=-W / 2.0,
                slot_x_max=0.0,
                slot_z_min=door_band_bottom + freezer_h,
                slot_z_max=door_band_top,
                hinge_side="left",
                role="fridge",
            )
        )
        slots.append(
            _slot(
                idx=1,
                slot_x_min=0.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_bottom + freezer_h,
                slot_z_max=door_band_top,
                hinge_side="right",
                role="fridge",
            )
        )
        slots.append(
            _slot(
                idx=2,
                slot_x_min=-W / 2.0,
                slot_x_max=0.0,
                slot_z_min=door_band_bottom,
                slot_z_max=door_band_bottom + freezer_h,
                hinge_side="left",
                role="freezer",
            )
        )
        slots.append(
            _slot(
                idx=3,
                slot_x_min=0.0,
                slot_x_max=W / 2.0,
                slot_z_min=door_band_bottom,
                slot_z_max=door_band_bottom + freezer_h,
                hinge_side="right",
                role="freezer",
            )
        )
    elif layout == "four_door_stacked":
        # 4 full-width stacked doors. Top + bottom are freezer; middle two fridge.
        unit = band_height / 4.0
        boundaries = [door_band_bottom + i * unit for i in range(5)]
        roles: list[Literal["fridge", "freezer"]] = ["freezer", "fridge", "fridge", "freezer"]
        for idx in range(4):
            z_min = boundaries[3 - idx]
            z_max = boundaries[3 - idx + 1]
            slots.append(
                _slot(
                    idx=idx,
                    slot_x_min=-W / 2.0,
                    slot_x_max=W / 2.0,
                    slot_z_min=z_min,
                    slot_z_max=z_max,
                    hinge_side="right",
                    role=roles[idx],
                )
            )
    else:
        raise ValueError(f"Unhandled door_layout: {layout}")

    return slots


# ---------------------------------------------------------------------------
# Body construction.
# ---------------------------------------------------------------------------


def _build_body_shell(
    body, resolved: ResolvedRefrigeratorConfig, *, body_mat, interior_mat, kick_mat
) -> None:
    W = resolved.body_width
    D = resolved.body_depth
    H = resolved.body_height

    # Back wall.
    body.visual(
        Box((W, WALL_THICKNESS, H - KICK_PLATE_HEIGHT)),
        origin=Origin(
            xyz=(
                0.0,
                D / 2.0 - WALL_THICKNESS / 2.0,
                KICK_PLATE_HEIGHT + (H - KICK_PLATE_HEIGHT) / 2.0,
            )
        ),
        material=body_mat,
        name="back_wall", material_class_id=("metal.paint_coated" if resolved.material_style in {"white", "black", "retro"} else "metal.stainless_matte"),
    )
    # Left & right side walls.
    body.visual(
        Box((WALL_THICKNESS, D, H - KICK_PLATE_HEIGHT)),
        origin=Origin(
            xyz=(
                -W / 2.0 + WALL_THICKNESS / 2.0,
                0.0,
                KICK_PLATE_HEIGHT + (H - KICK_PLATE_HEIGHT) / 2.0,
            )
        ),
        material=body_mat,
        name="left_side_wall", material_class_id=("metal.paint_coated" if resolved.material_style in {"white", "black", "retro"} else "metal.stainless_matte"),
    )
    body.visual(
        Box((WALL_THICKNESS, D, H - KICK_PLATE_HEIGHT)),
        origin=Origin(
            xyz=(
                W / 2.0 - WALL_THICKNESS / 2.0,
                0.0,
                KICK_PLATE_HEIGHT + (H - KICK_PLATE_HEIGHT) / 2.0,
            )
        ),
        material=body_mat,
        name="right_side_wall", material_class_id=("metal.paint_coated" if resolved.material_style in {"white", "black", "retro"} else "metal.stainless_matte"),
    )
    # Top panel.
    body.visual(
        Box((W, D, WALL_THICKNESS)),
        origin=Origin(xyz=(0.0, 0.0, H - WALL_THICKNESS / 2.0)),
        material=body_mat,
        name="top_panel", material_class_id=("metal.paint_coated" if resolved.material_style in {"white", "black", "retro"} else "metal.stainless_matte"),
    )
    # Floor / bottom panel of cavity.
    body.visual(
        Box((W, D, WALL_THICKNESS)),
        origin=Origin(xyz=(0.0, 0.0, KICK_PLATE_HEIGHT + WALL_THICKNESS / 2.0)),
        material=body_mat,
        name="cavity_floor", material_class_id=("metal.paint_coated" if resolved.material_style in {"white", "black", "retro"} else "metal.stainless_matte"),
    )
    # Kick plate (visual non-structural decoration) at the bottom.
    body.visual(
        Box((W, D, KICK_PLATE_HEIGHT)),
        origin=Origin(xyz=(0.0, 0.0, KICK_PLATE_HEIGHT / 2.0)),
        material=kick_mat,
        name="kick_plate", material_class_id=("metal.paint_coated" if resolved.material_style in {"white", "black", "retro"} else "metal.stainless_matte"),
    )
    # Top vent strip (visual decoration).
    body.visual(
        Box((W * 0.85, 0.018, TOP_VENT_HEIGHT * 0.6)),
        origin=Origin(xyz=(0.0, -D / 2.0 + 0.020, H - TOP_VENT_HEIGHT / 2.0)),
        material=kick_mat,
        name="top_vent_grille", material_class_id="plastic.opaque_generic",
    )
    # Interior liner: a thin inset panel along the cavity back; pure visual.
    body.visual(
        Box(
            (
                W - 2.0 * WALL_THICKNESS - INTERIOR_LINER_OFFSET,
                INTERIOR_LINER_OFFSET + 0.004,
                H - KICK_PLATE_HEIGHT - 2.0 * WALL_THICKNESS,
            )
        ),
        origin=Origin(
            xyz=(
                0.0,
                D / 2.0 - WALL_THICKNESS - INTERIOR_LINER_OFFSET / 2.0 - 0.002,
                KICK_PLATE_HEIGHT
                + WALL_THICKNESS
                + (H - KICK_PLATE_HEIGHT - 2.0 * WALL_THICKNESS) / 2.0,
            )
        ),
        material=interior_mat,
        name="interior_liner_back", material_class_id="plastic.opaque_glossy_molded",
    )


def _interior_xy_bounds(
    resolved: ResolvedRefrigeratorConfig,
) -> tuple[float, float, float, float, float, float]:
    """Returns (x_min, x_max, y_min, y_max, z_min, z_max) of the interior cavity."""
    W = resolved.body_width
    D = resolved.body_depth
    H = resolved.body_height
    x_min = -W / 2.0 + WALL_THICKNESS
    x_max = W / 2.0 - WALL_THICKNESS
    y_min = -D / 2.0 + 0.004  # near the front
    y_max = D / 2.0 - WALL_THICKNESS
    z_min = KICK_PLATE_HEIGHT + WALL_THICKNESS
    z_max = H - WALL_THICKNESS
    return x_min, x_max, y_min, y_max, z_min, z_max


def _band_z_intervals(
    resolved: ResolvedRefrigeratorConfig, slots: list[DoorSlot]
) -> list[tuple[float, float, str]]:
    """Return interior z intervals that correspond to fridge zones (where shelves live).

    Each element is (z_low, z_high, role). We aggregate adjacent fridge regions and
    keep freezer ranges separate (freezer zones get the drawers instead).
    """
    # Find vertical fridge "stripes" by looking at slot Z ranges grouped by role.
    z_min = KICK_PLATE_HEIGHT + WALL_THICKNESS
    z_max = resolved.body_height - WALL_THICKNESS
    # Build a sorted set of horizontal slices spanning the doorband.
    cut_points = {z_min, z_max}
    for s in slots:
        cut_points.add(max(s.hinge_z_bottom, z_min))
        cut_points.add(min(s.hinge_z_bottom + s.slot_height, z_max))
    sorted_cuts = sorted(cut_points)
    intervals: list[tuple[float, float, str]] = []
    for lo, hi in zip(sorted_cuts, sorted_cuts[1:], strict=False):
        if hi - lo < 0.05:
            continue
        mid_z = (lo + hi) / 2.0
        # Find slot whose vertical span covers mid_z and whose horizontal extent reaches mid_x=0.
        role = "fridge"
        for s in slots:
            s_lo = s.hinge_z_bottom
            s_hi = s.hinge_z_bottom + s.slot_height
            if (
                s_lo - 0.005 <= mid_z <= s_hi + 0.005
                and abs(s.slot_center_x) < resolved.body_width / 2.0
            ):
                if s.role == "freezer":
                    role = "freezer"
                else:
                    role = "fridge"
                break
        intervals.append((lo, hi, role))
    return intervals


def _build_interior_shelves(
    body, resolved: ResolvedRefrigeratorConfig, slots: list[DoorSlot], *, shelf_mat
) -> int:
    """Distribute shelves evenly inside fridge zones. Returns number of shelves added."""
    x_min, x_max, y_min, y_max, _, _ = _interior_xy_bounds(resolved)
    # Shelves are carried by both liner side walls; span the full clear width
    # so they form one connected cabinet body instead of floating 3 mm short.
    shelf_w = x_max - x_min
    # Leave room for the closed door bins instead of letting cabinet shelves
    # occupy the same front slice of the cavity.
    shelf_d = (y_max - y_min) - 0.070
    intervals = _band_z_intervals(resolved, slots)
    fridge_intervals = [(lo, hi) for (lo, hi, role) in intervals if role == "fridge"]

    # When there is no freezer zone the drawers occupy the lower interior band;
    # keep cabinet shelves out of it so they cannot intersect a drawer.
    _has_freezer = (
        resolved.door_layout != "side_by_side"
        and any(role == "freezer" for (_l, _h, role) in intervals)
    )
    _dz_min = KICK_PLATE_HEIGHT + WALL_THICKNESS
    _dz_max = resolved.body_height - WALL_THICKNESS
    _drawer_top = _dz_min + 0.020 + (_dz_max - _dz_min) * 0.35 + 0.060
    if not _has_freezer:
        fridge_intervals = [
            (max(lo, _drawer_top), hi) for (lo, hi) in fridge_intervals if hi > _drawer_top
        ]

    if not fridge_intervals:
        # Fall back to the interior (e.g. layout="single"), skipping the drawer
        # band when drawers may occupy it.
        _fb_lo = KICK_PLATE_HEIGHT + WALL_THICKNESS + 0.040
        if not _has_freezer:
            _fb_lo = max(_fb_lo, _drawer_top)
        fridge_intervals = [
            (
                _fb_lo,
                resolved.body_height - WALL_THICKNESS - 0.040,
            )
        ]

    # Total available height in fridge zones.
    total_h = sum(hi - lo for (lo, hi) in fridge_intervals)
    # Distribute shelf_count shelves proportionally across intervals.
    target = resolved.shelf_count
    added = 0
    shelf_idx = 0
    for lo, hi in fridge_intervals:
        if total_h <= 0:
            break
        share = (hi - lo) / total_h
        n_here = max(1, round(target * share))
        # Spacing: equal divisions inside the band; do not cap to ratio computation, instead
        # by enforced minimum spacing to avoid stacking shelves on top of each other.
        min_spacing = 0.13
        n_max = max(1, int((hi - lo - 0.04) / min_spacing))
        n = min(n_here, n_max)
        for i in range(n):
            frac = (i + 1) / (n + 1)
            z = lo + frac * (hi - lo)
            body.visual(
                Box((shelf_w, shelf_d, SHELF_THICKNESS)),
                origin=Origin(xyz=(0.0, (y_min + y_max) / 2.0 + 0.008, z)),
                material=shelf_mat,
                name=f"shelf_{shelf_idx}", material_class_id="plastic.opaque_glossy_molded",
            )
            shelf_idx += 1
            added += 1
    return added


# ---------------------------------------------------------------------------
# Drawers as separate prismatic parts.
# ---------------------------------------------------------------------------


def _drawer_zones(
    resolved: ResolvedRefrigeratorConfig, slots: list[DoorSlot]
) -> list[tuple[float, float]]:
    """Return interior z intervals where drawers may live (freezer compartments preferred)."""
    intervals = _band_z_intervals(resolved, slots)
    freezer_intervals = [(lo, hi) for (lo, hi, role) in intervals if role == "freezer"]
    # This template has full-width drawers and shelves, without a vertical
    # divider. Side-by-side doors therefore share a lower drawer band rather
    # than assigning the entire cabinet height to the freezer drawer zone.
    if freezer_intervals and resolved.door_layout != "side_by_side":
        return freezer_intervals
    # No freezer zone (e.g. layout="single") -> place drawers in lower interior.
    z_min = KICK_PLATE_HEIGHT + WALL_THICKNESS
    z_max = resolved.body_height - WALL_THICKNESS
    band = (z_max - z_min) * 0.35
    return [(z_min + 0.020, z_min + 0.020 + band)]


def _build_drawers(
    model: ArticulatedObject,
    body,
    resolved: ResolvedRefrigeratorConfig,
    slots: list[DoorSlot],
    *,
    interior_mat,
    hardware_mat,
) -> int:
    if resolved.drawer_count == 0:
        return 0
    x_min, x_max, y_min, y_max, _, _ = _interior_xy_bounds(resolved)
    # One millimetre of side clearance keeps the moving drawer supported by
    # the liner while avoiding a true side-wall penetration.
    drawer_w = (x_max - x_min) - 0.002
    # Depth leaves enough rear clearance that the closed-pose recess does not
    # drive the drawer back through the cabinet back wall / liner.
    drawer_d = (y_max - y_min) - 0.090
    zones = _drawer_zones(resolved, slots)
    # Pick the tallest zone for stacking drawers vertically.
    zones.sort(key=lambda z: z[1] - z[0], reverse=True)
    if not zones:
        return 0
    lo, hi = zones[0]
    available = hi - lo - 0.04
    if available < 0.10:
        return 0
    n = resolved.drawer_count
    max_n = max(1, int(available / 0.10))
    n = min(n, max_n)
    drawer_h = available / n
    drawer_height_geom = min(drawer_h - 0.012, 0.22)
    if drawer_height_geom < 0.06:
        drawer_height_geom = 0.06
    for i in range(n):
        z_bottom = lo + 0.020 + i * drawer_h
        z_center = z_bottom + drawer_height_geom / 2.0
        drawer = model.part(f"drawer_{i}")
        # Drawer shell: floor + back + sides + front face.
        drawer.visual(
            Box((drawer_w, drawer_d, 0.006)),
            origin=Origin(xyz=(0.0, 0.0, -drawer_height_geom / 2.0 + 0.003)),
            material=interior_mat,
            name="drawer_floor", material_class_id="plastic.opaque_glossy_molded",
        )
        drawer.visual(
            Box((drawer_w, 0.008, drawer_height_geom)),
            origin=Origin(xyz=(0.0, drawer_d / 2.0 - 0.004, 0.0)),
            material=interior_mat,
            name="drawer_back", material_class_id="plastic.opaque_glossy_molded",
        )
        drawer.visual(
            Box((DRAWER_SIDE_THICKNESS, drawer_d, drawer_height_geom)),
            origin=Origin(xyz=(-drawer_w / 2.0 + DRAWER_SIDE_THICKNESS / 2.0, 0.0, 0.0)),
            material=interior_mat,
            name="drawer_left_side", material_class_id="plastic.opaque_glossy_molded",
        )
        drawer.visual(
            Box((DRAWER_SIDE_THICKNESS, drawer_d, drawer_height_geom)),
            origin=Origin(xyz=(drawer_w / 2.0 - DRAWER_SIDE_THICKNESS / 2.0, 0.0, 0.0)),
            material=interior_mat,
            name="drawer_right_side", material_class_id="plastic.opaque_glossy_molded",
        )
        # Drawer front: thicker plate that sticks out the front face. We center the part
        # at the closed pose so the front plate sits just at the body front interior face.
        drawer.visual(
            Box((drawer_w, DRAWER_FRONT_THICKNESS, drawer_height_geom + 0.010)),
            origin=Origin(xyz=(0.0, -drawer_d / 2.0 - DRAWER_FRONT_THICKNESS / 2.0 + 0.002, 0.0)),
            material=hardware_mat,
            name="drawer_front", material_class_id=("metal.brushed_silver" if resolved.material_style in {"white", "stainless", "black"} else "metal.brass_polished"),
        )
        # Drawer pull (visual on drawer front).
        drawer.visual(
            Box((drawer_w * 0.40, 0.018, 0.012)),
            origin=Origin(xyz=(0.0, -drawer_d / 2.0 - DRAWER_FRONT_THICKNESS - 0.006, 0.0)),
            material=hardware_mat,
            name="drawer_pull", material_class_id=("metal.brushed_silver" if resolved.material_style in {"white", "stainless", "black"} else "metal.brass_polished"),
        )

        # Drawer slides along Y. Closed pose has its center at body y = front + drawer_d/2.
        # Joint origin is in body space; the drawer is parented to the body.
        # Recess the complete drawer front and pull behind the door's inner
        # face so the door bins clear the pull in the closed pose.
        drawer_y_center_closed = y_min + drawer_d / 2.0 + 0.070
        joint_origin_xyz = (0.0, drawer_y_center_closed, z_center)
        # Allow useful extension once the doors are open. Closed-door clearance
        # must not permanently restrict the drawer's mechanical travel.
        travel = max(0.02, drawer_d * 0.6)
        model.articulation(
            f"drawer_{i}_joint",
            ArticulationType.PRISMATIC,
            parent=body,
            child=drawer,
            origin=Origin(xyz=joint_origin_xyz),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=40.0, velocity=0.25, lower=0.0, upper=travel),
        )
    return n


# ---------------------------------------------------------------------------
# Door construction.
# ---------------------------------------------------------------------------


def _build_door_visuals(
    door,
    slot: DoorSlot,
    resolved: ResolvedRefrigeratorConfig,
    *,
    door_mat,
    gasket_mat,
    handle_mat,
    interior_mat,
    accent_mat,
    dispenser_on_this_door: bool,
) -> None:
    """Populate one door part. Door local frame, by convention:

    - hinge axis is the local Z axis, located at local (x=0, y=0).
    - panel extends from local x=0 (hinge edge) to local x=sign*dw, where sign=+1 for
      left-hinge doors and sign=-1 for right-hinge doors.
    - panel front face (visible outside) is at local y=-dt; inner face (toward body
      cavity when closed) is at local y=0.
    - panel rises from local z=0 (bottom) to local z=+dh (top).

    Joint origin in body space is placed at (slot.hinge_x, front_y, slot.hinge_z_bottom)
    with rpy=0 always; the joint axis sign is set in the caller to make positive q open
    the door outward (free edge swings toward body -Y, i.e. forward, away from the body).
    """
    dw = slot.width
    dh = slot.height
    dt = DOOR_THICKNESS
    sign = 1.0 if slot.hinge_side == "left" else -1.0

    # Panel.
    panel_x = sign * dw / 2.0
    panel_y = -dt / 2.0
    panel_z = dh / 2.0
    door.visual(
        Box((dw, dt, dh)),
        origin=Origin(xyz=(panel_x, panel_y, panel_z)),
        material=door_mat,
        name="door_panel", material_class_id=("metal.paint_coated" if resolved.material_style in {"white", "black", "retro"} else "metal.stainless_matte"),
    )

    # Gasket strip around the inner perimeter. Gaskets sit on the inner face of the
    # door (local +Y side) so they press against the body face when closed.
    gw = GASKET_THICKNESS_BY_STYLE[resolved.gasket_style]
    # Seat most of the compliant gasket in the door skin and leave a 4 mm
    # compression lip.  Modelling the whole 9--12 mm section beyond the inner
    # face created a rigid penetration rather than a seal contact.
    gasket_y = -gw / 2.0 + 0.004
    # Top and bottom horizontal strips.
    door.visual(
        Box((dw - 0.020, gw, gw)),
        origin=Origin(xyz=(panel_x, gasket_y, dh - gw / 2.0 - 0.002)),
        material=gasket_mat,
        name="gasket_strip_top", material_class_id="rubber.smooth_plain",
    )
    door.visual(
        Box((dw - 0.020, gw, gw)),
        origin=Origin(xyz=(panel_x, gasket_y, gw / 2.0 + 0.002)),
        material=gasket_mat,
        name="gasket_strip_bottom", material_class_id="rubber.smooth_plain",
    )
    # Hinge-side vertical strip (near x=0) and latch-side vertical strip (near x=sign*dw).
    door.visual(
        Box((gw, gw, dh - 0.020)),
        origin=Origin(xyz=(sign * (0.010 + gw / 2.0), gasket_y, dh / 2.0)),
        material=gasket_mat,
        name="gasket_strip_hinge", material_class_id="rubber.smooth_plain",
    )
    door.visual(
        Box((gw, gw, dh - 0.020)),
        origin=Origin(xyz=(sign * (dw - 0.010 - gw / 2.0), gasket_y, dh / 2.0)),
        material=gasket_mat,
        name="gasket_strip_latch", material_class_id="rubber.smooth_plain",
    )

    # Handle: visual on the door. Position depends on handle_style.
    style = resolved.handle_style
    # Let the handle standoffs enter the outer door skin while keeping the grip
    # proud of the face.  The old datum left the complete handle 3--10 mm away.
    handle_y_outer = -dt + 0.008
    if style == "vertical":
        bar_h = max(0.14, dh * 0.45)
        # Vertical bar near the latch (non-hinge) side of the door.
        bar_x = sign * (dw - 0.060)
        door.visual(
            Box((0.025, 0.024, bar_h)),
            origin=Origin(xyz=(bar_x, handle_y_outer - HANDLE_PROTRUSION / 2.0, dh * 0.55)),
            material=handle_mat,
            name="handle_bar", material_class_id=("metal.brass_polished" if resolved.material_style in {"white", "stainless", "retro"} else "metal.brushed_silver"),
        )
        for idx, z_off in enumerate((-bar_h * 0.35, bar_h * 0.35)):
            door.visual(
                Box((0.014, 0.018, 0.012)),
                origin=Origin(xyz=(bar_x, handle_y_outer - 0.010, dh * 0.55 + z_off)),
                material=handle_mat,
                name=f"handle_standoff_{idx}", material_class_id=("metal.brass_polished" if resolved.material_style in {"white", "stainless", "retro"} else "metal.brushed_silver"),
            )
    elif style == "horizontal":
        bar_w = max(0.16, dw * 0.55)
        bar_x = sign * (dw - bar_w / 2.0 - 0.040)
        door.visual(
            Box((bar_w, 0.024, 0.025)),
            origin=Origin(xyz=(bar_x, handle_y_outer - HANDLE_PROTRUSION / 2.0, dh * 0.82)),
            material=handle_mat,
            name="handle_bar", material_class_id=("metal.brass_polished" if resolved.material_style in {"white", "stainless", "retro"} else "metal.brushed_silver"),
        )
        for idx, x_off in enumerate((-bar_w * 0.35, bar_w * 0.35)):
            door.visual(
                Box((0.014, 0.018, 0.012)),
                origin=Origin(xyz=(bar_x + x_off, handle_y_outer - 0.010, dh * 0.82)),
                material=handle_mat,
                name=f"handle_standoff_{idx}", material_class_id=("metal.brass_polished" if resolved.material_style in {"white", "stainless", "retro"} else "metal.brushed_silver"),
            )
    else:  # recessed
        plate_x = sign * (dw - 0.030)
        door.visual(
            Box((0.040, 0.014, max(0.10, dh * 0.30))),
            origin=Origin(xyz=(plate_x, -dt + 0.007, dh * 0.55)),
            material=handle_mat,
            name="handle_recess_plate", material_class_id=("metal.brass_polished" if resolved.material_style in {"white", "stainless", "retro"} else "metal.brushed_silver"),
        )
        door.visual(
            Box((0.030, 0.020, 0.024)),
            origin=Origin(xyz=(plate_x, -dt + 0.012, dh * 0.55 + max(0.05, dh * 0.14))),
            material=handle_mat,
            name="handle_recess_grip", material_class_id=("metal.brass_polished" if resolved.material_style in {"white", "stainless", "retro"} else "metal.brushed_silver"),
        )

    # Optional door-mounted shelves (small rails on the inner face).
    door_bin_depth = 0.008
    for i in range(min(resolved.door_shelf_count, max(0, int(dh / 0.18)))):
        z = dh * (0.20 + 0.18 * i)
        if z > dh - 0.10:
            break
        door.visual(
            Box((dw - 0.070, door_bin_depth, DOOR_SHELF_RAIL_THICKNESS)),
            origin=Origin(xyz=(sign * dw / 2.0, -0.002 + door_bin_depth / 2.0, z)),
            material=interior_mat,
            name=f"door_shelf_floor_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        door.visual(
            Box((dw - 0.070, 0.008, DOOR_SHELF_RAIL_HEIGHT)),
            origin=Origin(
                xyz=(
                    sign * dw / 2.0,
                    -0.002 + door_bin_depth - 0.004,
                    z + DOOR_SHELF_RAIL_HEIGHT / 2.0 - 0.002,
                )
            ),
            material=interior_mat,
            name=f"door_shelf_rail_{i}", material_class_id="plastic.opaque_glossy_molded",
        )

    # Dispenser bay (visual only) on the door front face.
    if dispenser_on_this_door:
        bay_w = min(0.16, dw * 0.40)
        bay_h = min(0.20, dh * 0.30)
        bay_z = dh * 0.65
        bay_x = sign * (dw * 0.35)
        door.visual(
            Box((bay_w, 0.008, bay_h)),
            origin=Origin(xyz=(bay_x, -dt - 0.004, bay_z)),
            material=handle_mat,
            name="dispenser_bay", material_class_id="plastic.opaque_glossy_molded",
        )
        door.visual(
            Box((bay_w * 0.6, 0.008, 0.030)),
            origin=Origin(xyz=(bay_x, -dt - 0.006, bay_z + bay_h * 0.30)),
            material=accent_mat,
            name="dispenser_panel", material_class_id="tech.control_interface",
        )


# ---------------------------------------------------------------------------
# Top-level build function.
# ---------------------------------------------------------------------------


def build_refrigerator(
    config: RefrigeratorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or RefrigeratorConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-refrigerator-assets-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)

    palette = MATERIAL_PALETTES[resolved.material_style]
    body_mat = model.material("fridge_body", rgba=palette["body"])
    door_mat = model.material("fridge_door", rgba=palette["door"])
    gasket_color = GASKET_COLOR_OVERRIDE[resolved.gasket_style] or palette["gasket_default"]
    gasket_mat = model.material("fridge_gasket", rgba=gasket_color)
    hardware_mat = model.material("fridge_hardware", rgba=palette["hardware"])
    handle_mat = model.material("fridge_handle", rgba=palette["handle"])
    kick_mat = model.material("fridge_kick", rgba=palette["kick"])
    interior_mat = model.material("fridge_interior", rgba=palette["interior"])
    accent_mat = model.material("fridge_accent", rgba=palette["accent"])

    body = model.part("fridge_body")
    _build_body_shell(
        body, resolved, body_mat=body_mat, interior_mat=interior_mat, kick_mat=kick_mat
    )

    slots = plan_doors(resolved)
    _build_interior_shelves(body, resolved, slots, shelf_mat=interior_mat)
    _build_drawers(
        model, body, resolved, slots, interior_mat=interior_mat, hardware_mat=hardware_mat
    )

    # Decide which door gets the dispenser (if any).
    dispenser_door_idx: int | None = None
    if resolved.dispenser != "none":
        # Pick the door with the largest front panel area, preferring a fridge door.
        candidates = [(i, s) for i, s in enumerate(slots)]
        candidates.sort(
            key=lambda kv: (
                0 if kv[1].role == "fridge" else 1,
                -(kv[1].width * kv[1].height),
            )
        )
        if candidates:
            dispenser_door_idx = candidates[0][0]

    # Build doors and their hinge joints.
    for i, slot in enumerate(slots):
        door = model.part(slot.name)
        _build_door_visuals(
            door,
            slot,
            resolved,
            door_mat=door_mat,
            gasket_mat=gasket_mat,
            handle_mat=handle_mat,
            interior_mat=interior_mat,
            accent_mat=accent_mat,
            dispenser_on_this_door=(dispenser_door_idx == i),
        )
        # Joint origin in body coords. Joint frame is placed at the hinge axis on the
        # body's front face (slightly in front of the body so the door panel sits clear
        # of the body's front face when closed). rpy=0; the door's local +Y points
        # toward the body interior, so the panel extends from local y=-dt (front) to
        # local y=0 (inner).
        front_y = -resolved.body_depth / 2.0
        # The inner panel corner swings slightly behind the hinge beyond 90°.
        # Offset the hinge forward so that corner and the gasket clear the body.
        joint_y = front_y - DOOR_HINGE_FRONT_OFFSET
        # Axis sign: positive q must swing the free edge outward (toward body -Y).
        #   - left-hinge: panel extends toward local +X, free edge at body x=hinge_x+dw.
        #     Rotating about local -Z by +q rotates +X toward -Y => axis=(0,0,-1).
        #   - right-hinge: panel extends toward local -X, free edge at body x=hinge_x-dw.
        #     Rotating about local +Z by +q rotates -X toward -Y => axis=(0,0,+1).
        axis = (0.0, 0.0, -1.0) if slot.hinge_side == "left" else (0.0, 0.0, 1.0)
        model.articulation(
            f"{slot.name}_joint",
            ArticulationType.REVOLUTE,
            parent=body,
            child=door,
            origin=Origin(xyz=(slot.hinge_x, joint_y, slot.hinge_z_bottom)),
            axis=axis,
            motion_limits=MotionLimits(effort=18.0, velocity=1.5, lower=0.0, upper=1.80),
        )

    return model


def build_seeded_refrigerator(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_refrigerator(config_from_seed(seed), assets=assets)


def with_overrides(config: RefrigeratorConfig, **kwargs: object) -> RefrigeratorConfig:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def run_refrigerator_tests(
    object_model: ArticulatedObject, config: RefrigeratorConfig
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("fridge_body")
    slots = plan_doors(resolved)

    # 1. Every door has a revolute joint with vertical axis and open range 60-120°.
    for slot in slots:
        joint = object_model.get_articulation(f"{slot.name}_joint")
        ctx.check(
            f"{slot.name}_is_revolute",
            joint.articulation_type == ArticulationType.REVOLUTE,
            details=f"type={joint.articulation_type}",
        )
        ax = joint.axis
        ctx.check(
            f"{slot.name}_axis_is_vertical",
            ax is not None
            and abs(ax[0]) < 1e-6
            and abs(ax[1]) < 1e-6
            and abs(abs(ax[2]) - 1.0) < 1e-6,
            details=f"axis={ax}",
        )
        limits = joint.motion_limits
        ctx.check(
            f"{slot.name}_open_range_60_to_120_deg",
            limits is not None
            and limits.lower is not None
            and limits.upper is not None
            and abs(limits.lower) < 1e-6
            and 1.0 <= limits.upper <= 2.20,
            details=f"limits={limits}",
        )
        # Hinge must sit on the door side edge (not in the middle of the door).
        # The joint origin x should match slot.hinge_x within a small tolerance.
        ctx.check(
            f"{slot.name}_hinge_on_side_edge",
            abs(joint.origin.xyz[0] - slot.hinge_x) < 1e-3,
            details=f"hinge_x={joint.origin.xyz[0]}, expected≈{slot.hinge_x}",
        )

    # 2. Door panels exist and are positioned in front of the body when closed.
    front_y = -resolved.body_depth / 2.0
    for slot in slots:
        door = object_model.get_part(slot.name)
        panel_aabb = ctx.part_element_world_aabb(door, elem="door_panel")
        ctx.check(
            f"{slot.name}_panel_exists_in_front",
            panel_aabb is not None and panel_aabb[1][1] <= front_y + 0.010,
            details=f"panel_aabb={panel_aabb}, body_front={front_y}",
        )

    # 3. Each door has gasket strips (4 visuals).
    for slot in slots:
        door = object_model.get_part(slot.name)
        names = {v.name for v in door.visuals}
        required_gaskets = {
            "gasket_strip_top",
            "gasket_strip_bottom",
            "gasket_strip_hinge",
            "gasket_strip_latch",
        }
        missing = required_gaskets - names
        ctx.check(
            f"{slot.name}_has_full_gasket_perimeter",
            not missing,
            details=f"missing={sorted(missing)}",
        )

    # 4. Each door has a handle visual (handle_bar OR handle_recess_grip).
    for slot in slots:
        door = object_model.get_part(slot.name)
        names = {v.name for v in door.visuals}
        has_handle = "handle_bar" in names or "handle_recess_grip" in names
        ctx.check(
            f"{slot.name}_has_handle_visual",
            has_handle,
            details=f"visuals={sorted(names)}",
        )

    # 5. Interior shelves exist as visible geometry.
    body_visuals = {v.name for v in body.visuals}
    shelf_names = [n for n in body_visuals if n.startswith("shelf_")]
    ctx.check(
        "shelves_have_visible_geometry",
        len(shelf_names) >= 1,
        details=f"shelf_visuals={shelf_names}",
    )

    # 6. Drawer count matches and each drawer slides front-back.
    drawer_parts = [p for p in object_model.parts if p.name.startswith("drawer_")]
    for p in drawer_parts:
        joint = object_model.get_articulation(f"{p.name}_joint")
        ctx.check(
            f"{p.name}_is_prismatic",
            joint.articulation_type == ArticulationType.PRISMATIC,
            details=f"type={joint.articulation_type}",
        )
        ax = joint.axis
        ctx.check(
            f"{p.name}_axis_is_front_back",
            ax is not None
            and abs(ax[0]) < 1e-6
            and abs(abs(ax[1]) - 1.0) < 1e-6
            and abs(ax[2]) < 1e-6,
            details=f"axis={ax}",
        )
        limits = joint.motion_limits
        drawer_depth = resolved.body_depth - 0.034 - 0.090
        ctx.check(
            f"{p.name}_has_useful_extension",
            limits is not None
            and limits.lower == 0.0
            and limits.upper is not None
            and drawer_depth * 0.5 <= limits.upper <= drawer_depth * 0.8,
            details=f"limits={limits}, drawer_depth={drawer_depth}",
        )

    # 7. Door opens outward: panel front edge moves toward -Y when joint at midpoint.
    if slots:
        slot = slots[0]
        joint = object_model.get_articulation(f"{slot.name}_joint")
        door = object_model.get_part(slot.name)
        rest_aabb = ctx.part_element_world_aabb(door, elem="door_panel")
        with ctx.pose({joint: 1.40}):
            open_aabb = ctx.part_element_world_aabb(door, elem="door_panel")
        ctx.check(
            f"{slot.name}_panel_swings_outward",
            rest_aabb is not None
            and open_aabb is not None
            and open_aabb[0][1] < rest_aabb[0][1] - 0.06,
            details=f"rest_y_min={rest_aabb[0][1] if rest_aabb else None}, "
            f"open_y_min={open_aabb[0][1] if open_aabb else None}",
        )

    # 8. Identity: there should be exactly one body part and ≥1 door, ≥1 shelf.
    door_parts = [p for p in object_model.parts if p.name.startswith("door_")]
    ctx.check(
        "has_at_least_one_door",
        len(door_parts) >= 1,
        details=f"doors={[p.name for p in door_parts]}",
    )
    ctx.check(
        "door_count_matches_layout",
        len(door_parts) == resolved.door_count,
        details=f"got={len(door_parts)}, expected={resolved.door_count}",
    )

    return ctx.report()
