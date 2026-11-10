# SPDX-License-Identifier: Apache-2.0

"""Procedural template for category `display_freezer_with_sliding_glass_lids`.

This template intentionally follows the reviewed spec rather than attempting to
copy every five-star sample.  The stable seed domain is a low commercial display
freezer with a top-opening insulated tub, guide rails, sliding framed-glass lids,
and an interior storage system derived from the liner envelope.
"""

from __future__ import annotations

import math
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
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

BodyProfile = Literal[
    "flat_rectangular_chest",
    "rounded_commercial_tub",
    "compact_deli_counter",
    "three_bay_island",
]
LidLayout = Literal[
    "two_overlapping_flat",
    "single_deli_slider",
    "three_independent_bays",
    "curved_barrel_pair",
    "upper_lower_tier",
]
LidProfile = Literal["flat_framed_glass", "curved_barrel_glass", "raised_service_hatch"]
RailLayout = Literal[
    "parallel_front_back",
    "center_spine_two_tier",
    "three_bay_tracks",
    "guide_shelves",
]
HandleStyle = Literal["front_bar", "edge_pull", "recessed_grip", "round_knob"]
InteriorStorageLayout = Literal[
    "empty_open_well",
    "wire_basket_array",
    "removable_bin_grid",
    "product_tray_rows",
    "multi_tier_display_shelf",
    "bay_divider_grid",
]
BasketStyle = Literal[
    "none",
    "wire_hanging_basket",
    "solid_plastic_bin",
    "shallow_product_tray",
    "bottle_channel",
]
ControlStyle = Literal["none", "front_panel", "side_panel_with_dial", "rear_service_wall"]
BaseSupportStyle = Literal["feet", "casters", "skid_base"]
MaterialStyle = Literal["white_commercial", "black_deli", "blue_ice", "stainless_market"]

SOURCE_IDS: dict[str, str] = {
    "S1": (
        "data/records/rec_display_freezer_with_sliding_glass_lids_5717fea023294d5486ce6ea63a47b2e7/"
        "revisions/rev_000001/model.py:L59-L126"
    ),
    "S2": (
        "data/records/rec_display_freezer_with_sliding_glass_lids_5717fea023294d5486ce6ea63a47b2e7/"
        "revisions/rev_000001/model.py:L222-L393"
    ),
    "S3": (
        "data/records/rec_display_freezer_with_sliding_glass_lids_5717fea023294d5486ce6ea63a47b2e7/"
        "revisions/rev_000001/model.py:L395-L548"
    ),
    "S4": (
        "data/records/rec_display_freezer_with_sliding_glass_lids_4aeda36374044bd4b297e66c6a6c34d2/"
        "revisions/rev_000001/model.py:L28-L151"
    ),
    "S5": (
        "data/records/rec_display_freezer_with_sliding_glass_lids_4aeda36374044bd4b297e66c6a6c34d2/"
        "revisions/rev_000001/model.py:L153-L367"
    ),
    "S6": (
        "data/records/rec_display_freezer_with_sliding_glass_lids_2ba0cc1a83c64ca5bf0086b5f1ffdbca/"
        "revisions/rev_000001/model.py:L40-L128"
    ),
    "S7": (
        "data/records/rec_display_freezer_with_sliding_glass_lids_2ba0cc1a83c64ca5bf0086b5f1ffdbca/"
        "revisions/rev_000001/model.py:L146-L445"
    ),
    "S8": (
        "data/records/rec_display_freezer_with_sliding_glass_lids_84b667201ca04178883be8d5243aca46/"
        "revisions/rev_000001/model.py:L25-L109"
    ),
    "S9": (
        "data/records/rec_display_freezer_with_sliding_glass_lids_84b667201ca04178883be8d5243aca46/"
        "revisions/rev_000001/model.py:L123-L326"
    ),
    "S10": (
        "data/records/rec_display_freezer_with_sliding_glass_lids_dbfc4a989f6e4308b407b3d568b5128a/"
        "revisions/rev_000001/model.py:L35-L314"
    ),
}

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "white_commercial": {
        "shell": (0.90, 0.92, 0.92, 1.0),
        "liner": (0.78, 0.88, 0.94, 0.55),
        "trim": (0.58, 0.60, 0.62, 1.0),
        "rail": (0.68, 0.70, 0.72, 1.0),
        "rubber": (0.05, 0.05, 0.055, 1.0),
        "glass": (0.68, 0.88, 0.96, 0.32),
        "wire": (0.78, 0.80, 0.82, 1.0),
        "product": (0.92, 0.55, 0.34, 1.0),
        "accent": (0.12, 0.42, 0.78, 1.0),
    },
    "black_deli": {
        "shell": (0.12, 0.13, 0.14, 1.0),
        "liner": (0.62, 0.78, 0.88, 0.48),
        "trim": (0.22, 0.23, 0.24, 1.0),
        "rail": (0.64, 0.65, 0.66, 1.0),
        "rubber": (0.025, 0.025, 0.03, 1.0),
        "glass": (0.38, 0.62, 0.72, 0.36),
        "wire": (0.76, 0.76, 0.74, 1.0),
        "product": (0.88, 0.74, 0.28, 1.0),
        "accent": (0.92, 0.32, 0.20, 1.0),
    },
    "blue_ice": {
        "shell": (0.16, 0.38, 0.58, 1.0),
        "liner": (0.72, 0.90, 0.98, 0.50),
        "trim": (0.82, 0.84, 0.86, 1.0),
        "rail": (0.70, 0.74, 0.76, 1.0),
        "rubber": (0.04, 0.05, 0.06, 1.0),
        "glass": (0.66, 0.90, 0.98, 0.30),
        "wire": (0.86, 0.88, 0.88, 1.0),
        "product": (0.52, 0.78, 0.95, 1.0),
        "accent": (0.96, 0.96, 0.92, 1.0),
    },
    "stainless_market": {
        "shell": (0.58, 0.60, 0.62, 1.0),
        "liner": (0.76, 0.86, 0.90, 0.52),
        "trim": (0.42, 0.44, 0.46, 1.0),
        "rail": (0.78, 0.80, 0.80, 1.0),
        "rubber": (0.06, 0.06, 0.065, 1.0),
        "glass": (0.72, 0.86, 0.92, 0.34),
        "wire": (0.90, 0.90, 0.88, 1.0),
        "product": (0.50, 0.80, 0.42, 1.0),
        "accent": (0.12, 0.12, 0.13, 1.0),
    },
}

BODY_DEFAULT_MATERIAL: dict[BodyProfile, MaterialStyle] = {
    "flat_rectangular_chest": "white_commercial",
    "rounded_commercial_tub": "blue_ice",
    "compact_deli_counter": "black_deli",
    "three_bay_island": "stainless_market",
}

BODY_SIZE_RANGES: dict[
    BodyProfile, tuple[tuple[float, float], tuple[float, float], tuple[float, float]]
] = {
    "flat_rectangular_chest": ((1.25, 2.20), (0.65, 1.02), (0.70, 1.02)),
    "rounded_commercial_tub": ((1.30, 2.40), (0.72, 1.08), (0.72, 1.05)),
    "compact_deli_counter": ((1.00, 1.65), (0.55, 0.82), (0.58, 0.88)),
    "three_bay_island": ((1.80, 3.00), (0.72, 1.16), (0.70, 1.08)),
}

MIN_CELL_WIDTH = 0.22
MIN_CELL_DEPTH = 0.20
MIN_CELL_HEIGHT = 0.105
MIN_LID_CLEARANCE = 0.055
STORAGE_VERTICAL_GAP = 0.045
RAIL_SIDE_CLEARANCE = 0.030
LID_Z_GAP = 0.080
FRAME_RAIL_MIN = 0.018
FRAME_RAIL_MAX = 0.036
GLASS_THICKNESS_MIN = 0.006
GLASS_THICKNESS_MAX = 0.014


@dataclass(frozen=True)
class DisplayFreezerWithSlidingGlassLidsConfig:
    body_profile: BodyProfile = "flat_rectangular_chest"
    lid_layout: LidLayout = "two_overlapping_flat"
    lid_profile: LidProfile = "flat_framed_glass"
    rail_layout: RailLayout = "center_spine_two_tier"
    handle_style: HandleStyle = "edge_pull"
    interior_storage_layout: InteriorStorageLayout = "wire_basket_array"
    basket_style: BasketStyle = "wire_hanging_basket"
    control_style: ControlStyle = "front_panel"
    base_support_style: BaseSupportStyle = "feet"
    material_style: MaterialStyle | None = None
    cabinet_width: float | None = None
    cabinet_depth: float | None = None
    cabinet_height: float | None = None
    wall_thickness: float = 0.055
    bay_count: int = 2
    lid_count: int = 2
    lid_overlap: float = 0.14
    lid_travel: float | None = None
    storage_grid_cols: int = 2
    storage_grid_rows: int = 1
    storage_tier_count: int = 1
    basket_count: int = 2
    divider_count: int = 1
    storage_margin: float = 0.045
    storage_gap: float = 0.028
    product_fill: float = 0.70
    caster_count: int = 4
    name: str = "reference_display_freezer"


@dataclass(frozen=True)
class ResolvedDisplayFreezerWithSlidingGlassLidsConfig:
    body_profile: BodyProfile
    lid_layout: LidLayout
    lid_profile: LidProfile
    rail_layout: RailLayout
    handle_style: HandleStyle
    interior_storage_layout: InteriorStorageLayout
    basket_style: BasketStyle
    control_style: ControlStyle
    base_support_style: BaseSupportStyle
    material_style: MaterialStyle
    cabinet_width: float
    cabinet_depth: float
    cabinet_height: float
    wall_thickness: float
    bay_count: int
    lid_count: int
    lid_overlap: float
    lid_travel: float
    storage_grid_cols: int
    storage_grid_rows: int
    storage_tier_count: int
    basket_count: int
    divider_count: int
    storage_margin: float
    storage_gap: float
    product_fill: float
    caster_count: int
    rim_height: float
    rail_height: float
    rail_width: float
    rail_tier_count: int
    liner_width: float
    liner_depth: float
    liner_height: float
    liner_floor_z: float
    liner_top_z: float
    usable_storage_width: float
    usable_storage_depth: float
    usable_storage_height: float
    cell_width: float
    cell_depth: float
    cell_height: float
    lid_width: float
    lid_depth: float
    lid_frame_thickness: float
    glass_thickness: float
    lid_z_base: float
    lid_span: float
    min_cell_width: float
    min_cell_depth: float
    min_cell_height: float
    name: str


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _validate_literal(value: str, allowed: set[str], field: str) -> None:
    if value not in allowed:
        raise ValueError(f"Unsupported {field}: {value}")


def _choices_by_body(
    body_profile: BodyProfile,
) -> tuple[LidLayout, RailLayout, InteriorStorageLayout]:
    if body_profile == "compact_deli_counter":
        return "single_deli_slider", "guide_shelves", "product_tray_rows"
    if body_profile == "three_bay_island":
        return "three_independent_bays", "three_bay_tracks", "bay_divider_grid"
    if body_profile == "rounded_commercial_tub":
        return "curved_barrel_pair", "center_spine_two_tier", "wire_basket_array"
    return "two_overlapping_flat", "center_spine_two_tier", "wire_basket_array"


def _max_count_from_extent(
    usable: float, min_size: float, gap: float, *, min_count: int, max_count: int
) -> int:
    possible = int(math.floor((usable + gap) / (min_size + gap)))
    return max(min_count, min(max_count, possible))


def _lid_count_for_layout(lid_layout: LidLayout) -> int:
    if lid_layout == "single_deli_slider":
        return 1
    if lid_layout == "three_independent_bays":
        return 3
    return 2


def _rail_layout_for_lid_layout(lid_layout: LidLayout) -> RailLayout:
    if lid_layout == "single_deli_slider":
        return "guide_shelves"
    if lid_layout == "three_independent_bays":
        return "three_bay_tracks"
    if lid_layout == "curved_barrel_pair":
        return "center_spine_two_tier"
    if lid_layout == "upper_lower_tier":
        return "center_spine_two_tier"
    return "center_spine_two_tier"


def _storage_layout_for_body(body_profile: BodyProfile) -> InteriorStorageLayout:
    if body_profile == "compact_deli_counter":
        return "product_tray_rows"
    if body_profile == "three_bay_island":
        return "bay_divider_grid"
    return "wire_basket_array"


def _basket_style_for_storage(storage_layout: InteriorStorageLayout) -> BasketStyle:
    if storage_layout == "empty_open_well":
        return "none"
    if storage_layout == "wire_basket_array":
        return "wire_hanging_basket"
    if storage_layout == "removable_bin_grid":
        return "solid_plastic_bin"
    if storage_layout == "product_tray_rows":
        return "shallow_product_tray"
    if storage_layout == "multi_tier_display_shelf":
        return "solid_plastic_bin"
    return "wire_hanging_basket"


def config_from_seed(seed: int) -> DisplayFreezerWithSlidingGlassLidsConfig:
    rng = random.Random(seed)
    body_profile: BodyProfile = rng.choices(
        (
            "flat_rectangular_chest",
            "rounded_commercial_tub",
            "compact_deli_counter",
            "three_bay_island",
        ),
        weights=(0.36, 0.24, 0.22, 0.18),
        k=1,
    )[0]
    lid_layout, rail_layout, storage_layout = _choices_by_body(body_profile)
    width_range, depth_range, height_range = BODY_SIZE_RANGES[body_profile]
    cabinet_width = round(rng.uniform(*width_range), 3)
    cabinet_depth = round(rng.uniform(*depth_range), 3)
    cabinet_height = round(rng.uniform(*height_range), 3)
    wall_thickness = round(rng.uniform(0.040, 0.075), 3)
    bay_count = 3 if body_profile == "three_bay_island" else rng.choice((1, 2))
    if body_profile in {"flat_rectangular_chest", "rounded_commercial_tub"} and rng.random() < 0.18:
        lid_layout = "upper_lower_tier"
        rail_layout = "center_spine_two_tier"
    if body_profile == "rounded_commercial_tub" and rng.random() < 0.65:
        lid_layout = "curved_barrel_pair"
    lid_profile: LidProfile = (
        "curved_barrel_glass" if lid_layout == "curved_barrel_pair" else "flat_framed_glass"
    )
    lid_count = _lid_count_for_layout(lid_layout)
    storage_margin = round(rng.uniform(0.030, 0.065), 3)
    storage_gap = round(rng.uniform(0.018, 0.045), 3)
    storage_grid_cols = rng.choice((1, 2, 3, 4))
    storage_grid_rows = (
        rng.choice((1, 2, 3))
        if storage_layout in {"product_tray_rows", "removable_bin_grid"}
        else rng.choice((1, 2))
    )
    storage_tier_count = rng.choice((1, 2)) if storage_layout == "multi_tier_display_shelf" else 1
    if storage_layout == "bay_divider_grid":
        storage_grid_cols = 3
        storage_grid_rows = rng.choice((1, 2))
    control_style: ControlStyle = rng.choices(
        ("none", "front_panel", "side_panel_with_dial", "rear_service_wall"),
        weights=(0.16, 0.46, 0.22, 0.16),
        k=1,
    )[0]
    base_support_style: BaseSupportStyle = rng.choices(
        ("feet", "casters", "skid_base"), weights=(0.56, 0.26, 0.18), k=1
    )[0]
    return DisplayFreezerWithSlidingGlassLidsConfig(
        body_profile=body_profile,
        lid_layout=lid_layout,
        lid_profile=lid_profile,
        rail_layout=rail_layout,
        handle_style=rng.choice(("front_bar", "edge_pull", "recessed_grip", "round_knob")),
        interior_storage_layout=storage_layout,
        basket_style=_basket_style_for_storage(storage_layout),
        control_style=control_style,
        base_support_style=base_support_style,
        material_style=BODY_DEFAULT_MATERIAL[body_profile],
        cabinet_width=cabinet_width,
        cabinet_depth=cabinet_depth,
        cabinet_height=cabinet_height,
        wall_thickness=wall_thickness,
        bay_count=bay_count,
        lid_count=lid_count,
        lid_overlap=round(rng.uniform(0.09, 0.20), 3),
        lid_travel=None,
        storage_grid_cols=storage_grid_cols,
        storage_grid_rows=storage_grid_rows,
        storage_tier_count=storage_tier_count,
        basket_count=max(0, storage_grid_cols * storage_grid_rows * storage_tier_count),
        divider_count=max(0, storage_grid_cols - 1),
        storage_margin=storage_margin,
        storage_gap=storage_gap,
        product_fill=round(rng.uniform(0.35, 0.90), 3),
        caster_count=4,
        name=f"seeded_display_freezer_{seed}",
    )


def resolve_config(
    config: DisplayFreezerWithSlidingGlassLidsConfig,
) -> ResolvedDisplayFreezerWithSlidingGlassLidsConfig:
    _validate_literal(config.body_profile, set(BODY_SIZE_RANGES), "body_profile")
    _validate_literal(
        config.lid_layout,
        {
            "two_overlapping_flat",
            "single_deli_slider",
            "three_independent_bays",
            "curved_barrel_pair",
            "upper_lower_tier",
        },
        "lid_layout",
    )
    _validate_literal(
        config.lid_profile,
        {"flat_framed_glass", "curved_barrel_glass", "raised_service_hatch"},
        "lid_profile",
    )
    _validate_literal(
        config.rail_layout,
        {"parallel_front_back", "center_spine_two_tier", "three_bay_tracks", "guide_shelves"},
        "rail_layout",
    )
    _validate_literal(
        config.handle_style,
        {"front_bar", "edge_pull", "recessed_grip", "round_knob"},
        "handle_style",
    )
    _validate_literal(
        config.interior_storage_layout,
        {
            "empty_open_well",
            "wire_basket_array",
            "removable_bin_grid",
            "product_tray_rows",
            "multi_tier_display_shelf",
            "bay_divider_grid",
        },
        "interior_storage_layout",
    )
    _validate_literal(
        config.basket_style,
        {
            "none",
            "wire_hanging_basket",
            "solid_plastic_bin",
            "shallow_product_tray",
            "bottle_channel",
        },
        "basket_style",
    )
    _validate_literal(
        config.control_style,
        {"none", "front_panel", "side_panel_with_dial", "rear_service_wall"},
        "control_style",
    )
    _validate_literal(
        config.base_support_style, {"feet", "casters", "skid_base"}, "base_support_style"
    )
    material_style = config.material_style or BODY_DEFAULT_MATERIAL[config.body_profile]
    _validate_literal(material_style, set(PALETTES), "material_style")

    width_range, depth_range, height_range = BODY_SIZE_RANGES[config.body_profile]
    cabinet_width = _clamp(
        config.cabinet_width if config.cabinet_width is not None else sum(width_range) * 0.5,
        width_range[0],
        width_range[1],
    )
    cabinet_depth = _clamp(
        config.cabinet_depth if config.cabinet_depth is not None else sum(depth_range) * 0.5,
        depth_range[0],
        depth_range[1],
    )
    cabinet_height = _clamp(
        config.cabinet_height if config.cabinet_height is not None else sum(height_range) * 0.5,
        height_range[0],
        height_range[1],
    )
    wall_thickness = _clamp(config.wall_thickness, 0.035, min(0.090, cabinet_depth * 0.12))
    storage_margin = _clamp(config.storage_margin, 0.025, 0.075)
    storage_gap = _clamp(config.storage_gap, 0.015, 0.055)
    product_fill = _clamp(config.product_fill, 0.0, 1.0)

    body_profile = config.body_profile
    lid_layout = config.lid_layout
    rail_layout = config.rail_layout
    storage_layout = config.interior_storage_layout
    bay_count = max(1, min(3, config.bay_count))

    # Body/lid/rail/storage compatibility matrix from the reviewed spec.  Illegal
    # combinations are downgraded before any builder receives the config.
    if body_profile == "compact_deli_counter":
        if lid_layout not in {"single_deli_slider", "two_overlapping_flat"}:
            lid_layout = "single_deli_slider"
        rail_layout = (
            "guide_shelves" if lid_layout == "single_deli_slider" else "center_spine_two_tier"
        )
        if storage_layout not in {"product_tray_rows", "removable_bin_grid", "empty_open_well"}:
            storage_layout = "product_tray_rows"
        bay_count = 1
    elif body_profile == "three_bay_island":
        lid_layout = "three_independent_bays"
        rail_layout = "three_bay_tracks"
        storage_layout = "bay_divider_grid"
        bay_count = 3
    elif body_profile == "rounded_commercial_tub":
        if lid_layout not in {"curved_barrel_pair", "two_overlapping_flat", "upper_lower_tier"}:
            lid_layout = "curved_barrel_pair"
        rail_layout = "center_spine_two_tier"
        if storage_layout not in {"wire_basket_array", "removable_bin_grid", "empty_open_well"}:
            storage_layout = "wire_basket_array"
        bay_count = max(1, min(2, bay_count))
    else:
        if lid_layout not in {"two_overlapping_flat", "upper_lower_tier", "curved_barrel_pair"}:
            lid_layout = "two_overlapping_flat"
        rail_layout = _rail_layout_for_lid_layout(lid_layout)
        if storage_layout not in {"wire_basket_array", "removable_bin_grid", "empty_open_well"}:
            storage_layout = "wire_basket_array"
        bay_count = max(1, min(2, bay_count))

    lid_count = _lid_count_for_layout(lid_layout)
    if config.lid_count not in {1, 2, 3}:
        raise ValueError("lid_count must be in {1, 2, 3}")
    if config.lid_count != lid_count:
        lid_count = _lid_count_for_layout(lid_layout)

    lid_profile: LidProfile
    if lid_layout == "curved_barrel_pair":
        lid_profile = "curved_barrel_glass"
    elif config.lid_profile == "raised_service_hatch" and lid_layout != "single_deli_slider":
        lid_profile = "flat_framed_glass"
    else:
        lid_profile = (
            config.lid_profile
            if config.lid_profile != "curved_barrel_glass"
            else "flat_framed_glass"
        )

    if storage_layout == "empty_open_well":
        basket_style: BasketStyle = "none"
    else:
        basket_style = _basket_style_for_storage(storage_layout)

    rim_height = _clamp(cabinet_height * 0.045, 0.026, 0.060)
    rail_height = _clamp(cabinet_height * 0.035, 0.024, 0.046)
    rail_width = _clamp(cabinet_depth * 0.030, 0.020, 0.038)
    rail_tier_count = 2 if rail_layout == "center_spine_two_tier" else 1
    liner_floor_z = _clamp(cabinet_height * 0.13, 0.070, 0.150)
    liner_top_z = cabinet_height - rim_height - rail_height * 0.40
    liner_width = cabinet_width - 2.0 * wall_thickness
    liner_depth = cabinet_depth - 2.0 * wall_thickness
    liner_height = liner_top_z - liner_floor_z
    if liner_width < 0.45 or liner_depth < 0.32 or liner_height < 0.28:
        raise ValueError("liner volume too small after wall/rim derivation")

    usable_storage_width = max(0.10, liner_width - 2.0 * storage_margin)
    usable_storage_depth = max(0.10, liner_depth - 2.0 * storage_margin)
    usable_storage_height = max(
        0.10,
        liner_height - MIN_LID_CLEARANCE - max(0.035, cabinet_height * 0.035),
    )
    max_cols = _max_count_from_extent(
        usable_storage_width, MIN_CELL_WIDTH, storage_gap, min_count=1, max_count=4
    )
    max_rows = _max_count_from_extent(
        usable_storage_depth, MIN_CELL_DEPTH, storage_gap, min_count=1, max_count=3
    )
    max_tiers = _max_count_from_extent(
        usable_storage_height,
        MIN_CELL_HEIGHT,
        STORAGE_VERTICAL_GAP,
        min_count=1,
        max_count=2,
    )
    storage_grid_cols = max(1, min(config.storage_grid_cols, max_cols))
    storage_grid_rows = max(1, min(config.storage_grid_rows, max_rows))
    storage_tier_count = max(1, min(config.storage_tier_count, max_tiers))
    if storage_layout == "empty_open_well":
        storage_grid_cols = 1
        storage_grid_rows = 1
        storage_tier_count = 1
        basket_count = 0
        divider_count = 0
    elif storage_layout == "bay_divider_grid":
        storage_grid_cols = min(max_cols, max(1, bay_count))
        storage_grid_rows = max(1, min(storage_grid_rows, max_rows))
        storage_tier_count = 1
        basket_count = min(storage_grid_cols * storage_grid_rows, max(1, config.basket_count))
        divider_count = max(storage_grid_cols - 1, bay_count - 1)
    else:
        capacity = storage_grid_cols * storage_grid_rows * storage_tier_count
        basket_count = min(max(0, config.basket_count), capacity)
        if basket_count == 0 and storage_layout != "empty_open_well":
            basket_count = capacity
        divider_count = max(0, storage_grid_cols - 1 + (storage_grid_rows - 1))

    cell_width = (usable_storage_width - (storage_grid_cols - 1) * storage_gap) / storage_grid_cols
    cell_depth = (usable_storage_depth - (storage_grid_rows - 1) * storage_gap) / storage_grid_rows
    cell_height = (
        usable_storage_height - (storage_tier_count - 1) * STORAGE_VERTICAL_GAP
    ) / storage_tier_count
    cell_width = max(0.08, cell_width)
    cell_depth = max(0.08, cell_depth)
    cell_height = max(0.06, cell_height)

    lid_span = cabinet_width / max(1, lid_count)
    if lid_layout in {"two_overlapping_flat", "upper_lower_tier", "curved_barrel_pair"}:
        lid_width = min(cabinet_width * 0.58, cabinet_width - 2.0 * wall_thickness)
    elif lid_layout == "single_deli_slider":
        lid_width = min(cabinet_width * 0.58, liner_width * 0.86)
    else:
        lid_width = min(lid_span * 0.82, liner_width / lid_count * 0.95)
    lid_depth = min(
        cabinet_depth - 2.0 * wall_thickness - RAIL_SIDE_CLEARANCE, cabinet_depth * 0.82
    )
    lid_frame_thickness = _clamp(wall_thickness * 0.42, FRAME_RAIL_MIN, FRAME_RAIL_MAX)
    glass_thickness = _clamp(cabinet_height * 0.012, GLASS_THICKNESS_MIN, GLASS_THICKNESS_MAX)
    lid_overlap = _clamp(config.lid_overlap, 0.08, min(0.28, cabinet_width * 0.16))
    rail_usable_length = cabinet_width - 2.0 * wall_thickness - lid_width * 0.35
    default_travel = max(0.14, min(cabinet_width * 0.36, rail_usable_length - lid_overlap))
    requested_travel = config.lid_travel if config.lid_travel is not None else default_travel
    lid_travel = _clamp(requested_travel, 0.10, max(0.12, rail_usable_length - lid_overlap))
    if lid_layout == "three_independent_bays":
        lid_travel = min(lid_travel, (liner_width / max(1, bay_count)) * 0.12)
    lid_z_base = cabinet_height + rail_height * 0.48

    caster_count = 4 if config.base_support_style == "casters" else 0
    if config.caster_count not in {0, 4}:
        raise ValueError("caster_count must be 0 or 4")

    return ResolvedDisplayFreezerWithSlidingGlassLidsConfig(
        body_profile=body_profile,
        lid_layout=lid_layout,
        lid_profile=lid_profile,
        rail_layout=rail_layout,
        handle_style=config.handle_style,
        interior_storage_layout=storage_layout,
        basket_style=basket_style,
        control_style=config.control_style,
        base_support_style=config.base_support_style,
        material_style=material_style,
        cabinet_width=cabinet_width,
        cabinet_depth=cabinet_depth,
        cabinet_height=cabinet_height,
        wall_thickness=wall_thickness,
        bay_count=bay_count,
        lid_count=lid_count,
        lid_overlap=lid_overlap,
        lid_travel=lid_travel,
        storage_grid_cols=storage_grid_cols,
        storage_grid_rows=storage_grid_rows,
        storage_tier_count=storage_tier_count,
        basket_count=basket_count,
        divider_count=divider_count,
        storage_margin=storage_margin,
        storage_gap=storage_gap,
        product_fill=product_fill,
        caster_count=caster_count,
        rim_height=rim_height,
        rail_height=rail_height,
        rail_width=rail_width,
        rail_tier_count=rail_tier_count,
        liner_width=liner_width,
        liner_depth=liner_depth,
        liner_height=liner_height,
        liner_floor_z=liner_floor_z,
        liner_top_z=liner_top_z,
        usable_storage_width=usable_storage_width,
        usable_storage_depth=usable_storage_depth,
        usable_storage_height=usable_storage_height,
        cell_width=cell_width,
        cell_depth=cell_depth,
        cell_height=cell_height,
        lid_width=lid_width,
        lid_depth=lid_depth,
        lid_frame_thickness=lid_frame_thickness,
        glass_thickness=glass_thickness,
        lid_z_base=lid_z_base,
        lid_span=lid_span,
        min_cell_width=MIN_CELL_WIDTH,
        min_cell_depth=MIN_CELL_DEPTH,
        min_cell_height=MIN_CELL_HEIGHT,
        name=config.name,
    )


def _joint_meta(
    joint_type: str,
    axis: tuple[float, float, float],
    origin: tuple[float, float, float],
    joint_range: object,
    *,
    source_id: str,
) -> dict[str, object]:
    return {
        "type": joint_type,
        "axis": axis,
        "origin": origin,
        "range": joint_range,
        "source_id": source_id,
    }


def _mat(model: ArticulatedObject, palette: dict[str, tuple[float, float, float, float]], key: str):
    return model.material(f"display_freezer_{key}", rgba=palette[key])


def _add_box(
    part, size: tuple[float, float, float], xyz: tuple[float, float, float], material, name: str
) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="metal.paint_coated")


def _add_cyl(
    part,
    *,
    radius: float,
    length: float,
    xyz: tuple[float, float, float],
    rpy: tuple[float, float, float],
    material,
    name: str,
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="rubber.smooth_plain",
    )


def _build_outer_shell(
    body, r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig, *, shell, liner, trim, rubber
) -> None:
    W = r.cabinet_width
    D = r.cabinet_depth
    H = r.cabinet_height
    wall = r.wall_thickness
    rim_h = r.rim_height
    base_h = max(0.075, min(0.16, H * 0.14))
    wall_h = H - base_h
    wall_z = base_h + wall_h * 0.5
    _add_box(body, (W, D, base_h), (0.0, 0.0, base_h * 0.5), shell, "base_pan")
    _add_box(
        body, (wall, D, wall_h), (-(W * 0.5) + wall * 0.5, 0.0, wall_z), shell, "left_outer_wall"
    )
    _add_box(
        body, (wall, D, wall_h), ((W * 0.5) - wall * 0.5, 0.0, wall_z), shell, "right_outer_wall"
    )
    _add_box(
        body, (W, wall, wall_h), (0.0, (D * 0.5) - wall * 0.5, wall_z), shell, "front_outer_wall"
    )
    _add_box(
        body, (W, wall, wall_h), (0.0, -(D * 0.5) + wall * 0.5, wall_z), shell, "rear_outer_wall"
    )

    liner_t = max(0.010, wall * 0.22)
    liner_floor_z = r.liner_floor_z
    liner_wall_z = liner_floor_z + r.liner_height * 0.5
    _add_box(
        body,
        (r.liner_width + 2.0 * liner_t, r.liner_depth + 2.0 * liner_t, 0.026),
        (0.0, 0.0, liner_floor_z - 0.013),
        liner,
        "liner_floor",
    )
    _add_box(
        body,
        (liner_t, r.liner_depth, r.liner_height),
        (-(r.liner_width * 0.5) - liner_t * 0.5, 0.0, liner_wall_z),
        liner,
        "left_liner",
    )
    _add_box(
        body,
        (liner_t, r.liner_depth, r.liner_height),
        ((r.liner_width * 0.5) + liner_t * 0.5, 0.0, liner_wall_z),
        liner,
        "right_liner",
    )
    _add_box(
        body,
        (r.liner_width + 2.0 * liner_t, liner_t, r.liner_height),
        (0.0, (r.liner_depth * 0.5) + liner_t * 0.5, liner_wall_z),
        liner,
        "front_liner",
    )
    _add_box(
        body,
        (r.liner_width + 2.0 * liner_t, liner_t, r.liner_height),
        (0.0, -(r.liner_depth * 0.5) - liner_t * 0.5, liner_wall_z),
        liner,
        "rear_liner",
    )

    rim_z = H - rim_h * 0.5
    side_rim = (W - r.liner_width) * 0.5
    front_rim = (D - r.liner_depth) * 0.5
    _add_box(
        body,
        (side_rim, D, rim_h),
        (-(r.liner_width * 0.5) - side_rim * 0.5, 0.0, rim_z),
        trim,
        "left_top_rim",
    )
    _add_box(
        body,
        (side_rim, D, rim_h),
        ((r.liner_width * 0.5) + side_rim * 0.5, 0.0, rim_z),
        trim,
        "right_top_rim",
    )
    _add_box(
        body,
        (r.liner_width, front_rim, rim_h),
        (0.0, (r.liner_depth * 0.5) + front_rim * 0.5, rim_z),
        trim,
        "front_top_rim",
    )
    _add_box(
        body,
        (r.liner_width, front_rim, rim_h),
        (0.0, -(r.liner_depth * 0.5) - front_rim * 0.5, rim_z),
        trim,
        "rear_top_rim",
    )

    if r.body_profile == "rounded_commercial_tub":
        for idx, sx in enumerate((-1.0, 1.0)):
            _add_cyl(
                body,
                radius=wall * 0.72,
                length=D - wall * 0.6,
                xyz=(sx * (W * 0.5 - wall * 0.58), 0.0, H * 0.54),
                rpy=(math.pi / 2.0, 0.0, 0.0),
                material=trim,
                name=f"rounded_corner_post_{idx}",
            )
    if r.body_profile == "compact_deli_counter":
        _add_box(
            body,
            (W * 0.35, 0.020, H * 0.18),
            (W * 0.25, D * 0.5 + 0.010, H * 0.35),
            trim,
            "front_brand_panel",
        )
        _add_box(
            body,
            (W * 0.28, 0.012, 0.030),
            (W * 0.25, D * 0.5 + 0.026, H * 0.42),
            rubber,
            "front_brand_label",
        )
    if r.body_profile == "three_bay_island":
        divider_h = _low_storage_divider_height(r)
        divider_d = min(
            r.usable_storage_depth + r.storage_gap, r.liner_depth - 2.0 * r.storage_margin
        )
        divider_z = r.liner_floor_z + divider_h * 0.5
        for i in range(1, r.bay_count):
            x = -r.liner_width * 0.5 + r.liner_width * i / r.bay_count
            _add_box(
                body, (0.014, divider_d, divider_h), (x, 0.0, divider_z), liner, f"bay_divider_{i}"
            )

    body.inertial = Inertial.from_geometry(
        Box((W, D, H)), mass=65.0, origin=Origin(xyz=(0.0, 0.0, H * 0.5))
    )


def _lid_track_contact_z(
    r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig, tier_index: int
) -> float:
    # Sink the lid slightly into the rail so the lid part stays in geometric
    # contact with the grounded cabinet (otherwise it reads as isolated).
    return r.lid_z_base + tier_index * _lid_tier_gap(r) - 0.004


def _lid_tier_gap(r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig) -> float:
    return _clamp(r.lid_frame_thickness + r.glass_thickness + 0.020, 0.052, LID_Z_GAP)


def _lid_shoe_y(r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig) -> float:
    return r.lid_depth * 0.5 - r.lid_frame_thickness * 0.7


def _build_rail_system(
    body,
    r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig,
    *,
    glass,
    rail,
    rubber,
    trim,
) -> None:
    W = r.cabinet_width
    D = r.cabinet_depth
    rail_y = D * 0.5 - r.wall_thickness * 0.72
    rail_len = W - 2.0 * r.wall_thickness
    shoe_y = _lid_shoe_y(r)
    contact_channel_h = 0.006
    contact_channel_z_offset = 0.001 - contact_channel_h * 0.5
    tier_contact_zs = [_lid_track_contact_z(r, tier_idx) for tier_idx in range(r.rail_tier_count)]
    for tier_idx, contact_z in enumerate(tier_contact_zs):
        z = contact_z - r.rail_height * 0.5
        _add_box(
            body,
            (rail_len, r.rail_width, r.rail_height),
            (0.0, rail_y, z),
            rail,
            f"front_track_tier_{tier_idx}",
        )
        _add_box(
            body,
            (rail_len, r.rail_width, r.rail_height),
            (0.0, -rail_y, z),
            rail,
            f"rear_track_tier_{tier_idx}",
        )
        shelf_h = max(0.010, r.rail_height * 0.42)
        shelf_w = max(
            0.012, abs((rail_y - r.rail_width * 0.5) - shoe_y) + r.lid_frame_thickness * 0.62
        )
        shelf_y = (rail_y - r.rail_width * 0.5 + shoe_y) * 0.5
        shelf_z = contact_z - shelf_h * 0.5
        _add_box(
            body,
            (rail_len, shelf_w, shelf_h),
            (0.0, shelf_y, shelf_z),
            rail,
            f"front_inner_runner_shelf_tier_{tier_idx}",
        )
        _add_box(
            body,
            (rail_len, shelf_w, shelf_h),
            (0.0, -shelf_y, shelf_z),
            rail,
            f"rear_inner_runner_shelf_tier_{tier_idx}",
        )
        groove_h = 0.003
        groove_w = max(0.010, r.rail_width * 0.50)
        groove_z = contact_z + groove_h * 0.5
        _add_box(
            body,
            (rail_len, groove_w, groove_h),
            (0.0, rail_y - r.rail_width * 0.18, groove_z),
            rubber,
            f"front_recessed_track_groove_tier_{tier_idx}",
        )
        _add_box(
            body,
            (rail_len, groove_w, groove_h),
            (0.0, -rail_y + r.rail_width * 0.18, groove_z),
            rubber,
            f"rear_recessed_track_groove_tier_{tier_idx}",
        )
        _add_box(
            body,
            (rail_len, max(0.010, r.lid_frame_thickness * 0.56), contact_channel_h),
            (0.0, shoe_y, contact_z + contact_channel_z_offset),
            rubber,
            f"front_lid_contact_channel_tier_{tier_idx}",
        )
        _add_box(
            body,
            (rail_len, max(0.010, r.lid_frame_thickness * 0.56), contact_channel_h),
            (0.0, -shoe_y, contact_z + contact_channel_z_offset),
            rubber,
            f"rear_lid_contact_channel_tier_{tier_idx}",
        )
        if tier_idx > 0:
            riser_h = _lid_tier_gap(r) - r.rail_height * 0.42
            riser_z = contact_z - r.rail_height * 0.5 - riser_h * 0.5
            _add_box(
                body,
                (rail_len, r.rail_width * 0.46, riser_h),
                (0.0, rail_y, riser_z),
                trim,
                f"front_upper_track_riser_tier_{tier_idx}",
            )
            _add_box(
                body,
                (rail_len, r.rail_width * 0.46, riser_h),
                (0.0, -rail_y, riser_z),
                trim,
                f"rear_upper_track_riser_tier_{tier_idx}",
            )
    if r.rail_layout == "three_bay_tracks":
        for i in range(1, r.bay_count):
            x = -r.liner_width * 0.5 + r.liner_width * i / r.bay_count
            _add_box(
                body,
                (0.034, r.rail_width * 1.8, r.rail_height * 0.92),
                (x, rail_y - r.rail_width * 0.32, r.lid_z_base - r.rail_height * 0.46),
                trim,
                f"front_bay_track_stop_{i}",
            )
            _add_box(
                body,
                (0.034, r.rail_width * 1.8, r.rail_height * 0.92),
                (x, -rail_y + r.rail_width * 0.32, r.lid_z_base - r.rail_height * 0.46),
                trim,
                f"rear_bay_track_stop_{i}",
            )
    if r.rail_layout == "guide_shelves":
        fixed_shelf_width = max(0.16, min(W * 0.38, r.lid_width * 0.62))
        fixed_shelf_depth = max(
            0.10, min(D * 0.24, r.lid_depth * 0.48, D * 0.5 - _lid_shoe_y(r) - 0.030)
        )
        # Seat the shelf against the right liner wall (right edge overlaps the
        # wall a few mm) so it fuses to the cabinet instead of floating inboard.
        fixed_shelf_x = W * 0.5 - r.wall_thickness - fixed_shelf_width * 0.5 + 0.020
        fixed_shelf_y = -_lid_shoe_y(r) * 0.55
        fixed_shelf_z = r.lid_z_base + 0.004 + r.glass_thickness * 0.5
        _add_box(
            body,
            (fixed_shelf_width, fixed_shelf_depth, r.glass_thickness),
            (fixed_shelf_x, fixed_shelf_y, fixed_shelf_z),
            glass,
            "fixed_rear_glass_shelf",
        )
        # Support brackets from the shelf underside down to the liner floor so the
        # shelf is fused to the cabinet body (it otherwise floats ~2 cm clear).
        _shelf_bottom_z = fixed_shelf_z - r.glass_thickness * 0.5
        _bracket_h = _shelf_bottom_z - r.liner_floor_z
        if _bracket_h > 0.004:
            for _sx in (-1.0, 1.0):
                _add_box(
                    body,
                    (0.014, 0.014, _bracket_h),
                    (
                        fixed_shelf_x + _sx * (fixed_shelf_width * 0.5 - 0.014),
                        fixed_shelf_y,
                        r.liner_floor_z + _bracket_h * 0.5,
                    ),
                    trim,
                    f"fixed_shelf_bracket_{'r' if _sx > 0 else 'l'}",
                )
        _add_box(
            body,
            (0.020, D - 2.2 * r.wall_thickness, r.rail_height),
            (0.0, 0.0, r.lid_z_base - r.rail_height * 0.5),
            trim,
            "guide_shelf_end_stop",
        )
    stop_x = W * 0.5 - r.wall_thickness - 0.018
    for sx, label in ((-1.0, "left"), (1.0, "right")):
        for sy, rail_label in ((1.0, "front"), (-1.0, "rear")):
            _add_box(
                body,
                (0.028, r.rail_width * 1.25, 0.032),
                (sx * stop_x, sy * rail_y, r.lid_z_base - 0.010),
                trim,
                f"{label}_{rail_label}_sliding_end_stop",
            )


def _storage_cell_origin(
    r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig, col: int, row: int, tier: int
) -> tuple[float, float, float]:
    start_x = -r.usable_storage_width * 0.5 + r.cell_width * 0.5
    start_y = -r.usable_storage_depth * 0.5 + r.cell_depth * 0.5
    x = start_x + col * (r.cell_width + r.storage_gap)
    y = start_y + row * (r.cell_depth + r.storage_gap)
    z = (
        r.liner_floor_z
        + 0.035
        + r.cell_height * 0.5
        + tier * (r.cell_height + STORAGE_VERTICAL_GAP)
    )
    return (x, y, z)


def _build_wire_basket(
    body,
    r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig,
    *,
    wire,
    product,
    origin: tuple[float, float, float],
    index: int,
) -> None:
    x, y, z = origin
    w = r.cell_width * 0.92
    d = r.cell_depth * 0.90
    h = min(r.cell_height * 0.70, 0.18)
    rail_t = 0.008
    floor_z = z - h * 0.42
    rim_z = z + h * 0.40
    _add_box(
        body,
        (w, rail_t, rail_t),
        (x, y + d * 0.5, rim_z),
        wire,
        f"storage_{index}_front_hanger_rail",
    )
    _add_box(
        body,
        (w, rail_t, rail_t),
        (x, y - d * 0.5, rim_z),
        wire,
        f"storage_{index}_rear_hanger_rail",
    )
    _add_box(body, (rail_t, d, rail_t), (x - w * 0.5, y, rim_z), wire, f"storage_{index}_left_rim")
    _add_box(body, (rail_t, d, rail_t), (x + w * 0.5, y, rim_z), wire, f"storage_{index}_right_rim")
    _add_box(body, (w, d, 0.006), (x, y, floor_z), wire, f"storage_{index}_wire_floor")
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            # Corner legs run down to the liner floor so the basket is fused to
            # the cabinet body (otherwise the whole basket is a floating island).
            leg_top = rim_z + rail_t * 0.5
            leg_h = leg_top - r.liner_floor_z
            _add_box(
                body,
                (rail_t, rail_t, leg_h),
                (x + sx * w * 0.5, y + sy * d * 0.5, r.liner_floor_z + leg_h * 0.5),
                wire,
                f"storage_{index}_corner_post_{sx:+.0f}_{sy:+.0f}",
            )
    if r.product_fill > 0.05:
        _add_box(
            body,
            (w * 0.62, d * 0.62, h * 0.36),
            (x, y, floor_z + h * 0.18),
            product,
            f"storage_{index}_product_load",
        )


def _build_solid_bin(
    body,
    r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig,
    *,
    wire,
    product,
    origin: tuple[float, float, float],
    index: int,
) -> None:
    x, y, z = origin
    w = r.cell_width * 0.90
    d = r.cell_depth * 0.88
    h = min(r.cell_height * 0.78, 0.20)
    t = 0.010
    _add_box(body, (w, d, t), (x, y, z - h * 0.46), wire, f"storage_{index}_solid_floor")
    _add_box(
        body, (t, d, h), (x - w * 0.5 + t * 0.5, y, z), wire, f"storage_{index}_solid_left_wall"
    )
    _add_box(
        body, (t, d, h), (x + w * 0.5 - t * 0.5, y, z), wire, f"storage_{index}_solid_right_wall"
    )
    _add_box(
        body, (w, t, h), (x, y + d * 0.5 - t * 0.5, z), wire, f"storage_{index}_solid_front_wall"
    )
    _add_box(
        body, (w, t, h), (x, y - d * 0.5 + t * 0.5, z), wire, f"storage_{index}_solid_rear_wall"
    )
    if r.product_fill > 0.05:
        _add_box(
            body,
            (w * 0.70, d * 0.70, h * 0.34),
            (x, y, z - h * 0.15),
            product,
            f"storage_{index}_solid_product_load",
        )


def _build_product_tray(
    body,
    r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig,
    *,
    wire,
    product,
    origin: tuple[float, float, float],
    index: int,
) -> None:
    x, y, z = origin
    w = r.cell_width * 0.92
    d = r.cell_depth * 0.88
    lip_h = min(0.040, r.cell_height * 0.30)
    t = 0.008
    _add_box(body, (w, d, t), (x, y, z - lip_h), wire, f"storage_{index}_tray_floor")
    # Legs run from the tray floor down to the liner floor so the tray is fused
    # to the cabinet body instead of floating in the cavity (island).
    leg_top = z - lip_h - t * 0.5
    leg_h = leg_top - r.liner_floor_z
    if leg_h > 0.004:
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                _add_box(
                    body,
                    (t, t, leg_h),
                    (x + sx * (w * 0.5 - t), y + sy * (d * 0.5 - t), r.liner_floor_z + leg_h * 0.5),
                    wire,
                    f"storage_{index}_tray_leg_{sx:+.0f}_{sy:+.0f}",
                )
    _add_box(
        body,
        (w, t, lip_h),
        (x, y + d * 0.5 - t * 0.5, z - lip_h * 0.5),
        wire,
        f"storage_{index}_front_lip",
    )
    _add_box(
        body,
        (w, t, lip_h),
        (x, y - d * 0.5 + t * 0.5, z - lip_h * 0.5),
        wire,
        f"storage_{index}_rear_lip",
    )
    package_count = 3 if w > 0.35 else 2
    for k in range(package_count):
        px = x - w * 0.30 + k * (w * 0.60 / max(1, package_count - 1))
        _add_box(
            body,
            (w * 0.18, d * 0.62, lip_h * 0.92),
            (px, y, z - lip_h + t * 0.5 + lip_h * 0.92 * 0.5 - 0.002),
            product,
            f"storage_{index}_tray_product_{k}",
        )


def _build_bottle_channel(
    body,
    r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig,
    *,
    wire,
    product,
    origin: tuple[float, float, float],
    index: int,
) -> None:
    x, y, z = origin
    w = r.cell_width * 0.90
    d = r.cell_depth * 0.88
    rail_t = 0.008
    _add_box(
        body, (w, rail_t, rail_t), (x, y + d * 0.30, z), wire, f"storage_{index}_bottle_front_rail"
    )
    _add_box(
        body, (w, rail_t, rail_t), (x, y - d * 0.30, z), wire, f"storage_{index}_bottle_rear_rail"
    )
    count = max(2, min(5, int(w / 0.095)))
    for k in range(count):
        px = x - w * 0.40 + k * (w * 0.80 / max(1, count - 1))
        _add_cyl(
            body,
            radius=0.026,
            length=min(0.12, r.cell_height * 0.72),
            xyz=(px, y, z),
            rpy=(0.0, 0.0, 0.0),
            material=product,
            name=f"storage_{index}_bottle_{k}",
        )


def _low_storage_divider_height(r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig) -> float:
    return _clamp(min(r.cell_height * 0.46, r.liner_height * 0.28, 0.135), 0.050, 0.135)


def _build_storage(
    body, r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig, *, wire, product, liner, trim
) -> None:
    if r.interior_storage_layout == "empty_open_well" or r.basket_count <= 0:
        _add_box(
            body,
            (r.liner_width * 0.42, r.liner_depth * 0.20, 0.010),
            (0.0, 0.0, r.liner_floor_z + 0.014),
            liner,
            "empty_well_floor_mat",
        )
        return
    capacity = r.storage_grid_cols * r.storage_grid_rows * r.storage_tier_count
    placed = 0
    for tier in range(r.storage_tier_count):
        for row in range(r.storage_grid_rows):
            for col in range(r.storage_grid_cols):
                if placed >= r.basket_count or placed >= capacity:
                    continue
                origin = _storage_cell_origin(r, col, row, tier)
                if r.basket_style == "wire_hanging_basket":
                    _build_wire_basket(
                        body, r, wire=wire, product=product, origin=origin, index=placed
                    )
                elif r.basket_style == "solid_plastic_bin":
                    _build_solid_bin(
                        body, r, wire=wire, product=product, origin=origin, index=placed
                    )
                elif r.basket_style == "shallow_product_tray":
                    _build_product_tray(
                        body, r, wire=wire, product=product, origin=origin, index=placed
                    )
                elif r.basket_style == "bottle_channel":
                    _build_bottle_channel(
                        body, r, wire=wire, product=product, origin=origin, index=placed
                    )
                placed += 1
    if r.interior_storage_layout == "bay_divider_grid" and r.body_profile != "three_bay_island":
        divider_h = _low_storage_divider_height(r)
        divider_z = r.liner_floor_z + divider_h * 0.5
        for i in range(1, r.storage_grid_cols):
            x = (
                -r.usable_storage_width * 0.5
                + i * (r.cell_width + r.storage_gap)
                - r.storage_gap * 0.5
            )
            _add_box(
                body,
                (0.010, r.usable_storage_depth, divider_h),
                (x, 0.0, divider_z),
                liner,
                f"storage_vertical_divider_{i}",
            )
    if r.interior_storage_layout == "multi_tier_display_shelf" and r.storage_tier_count > 1:
        for tier in range(1, r.storage_tier_count):
            shelf_z = (
                r.liner_floor_z
                + tier * (r.cell_height + STORAGE_VERTICAL_GAP)
                - STORAGE_VERTICAL_GAP * 0.5
            )
            _add_box(
                body,
                (r.usable_storage_width, r.usable_storage_depth, 0.010),
                (0.0, 0.0, shelf_z),
                wire,
                f"storage_tier_shelf_{tier}",
            )


def _build_controls(
    body, r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig, *, trim, rubber, accent, rail
) -> None:
    W = r.cabinet_width
    D = r.cabinet_depth
    H = r.cabinet_height
    if r.control_style == "none":
        return
    if r.control_style in {"front_panel", "rear_service_wall"}:
        y = D * 0.5 + 0.010 if r.control_style == "front_panel" else -D * 0.5 - 0.010
        name_prefix = "front" if r.control_style == "front_panel" else "rear"
        panel_w = min(0.34, W * 0.22)
        panel_x = W * 0.26
        display_x = panel_x + panel_w * 0.16
        button_start_x = panel_x + panel_w * 0.02
        _add_box(
            body,
            (panel_w, 0.020, 0.120),
            (panel_x, y, H * 0.34),
            trim,
            f"{name_prefix}_control_panel",
        )
        _add_box(
            body,
            (min(0.20, W * 0.13), 0.008, 0.040),
            (display_x, y + (0.010 if y > 0 else -0.010), H * 0.36),
            accent,
            f"{name_prefix}_temperature_display",
        )
        for k in range(4):
            _add_box(
                body,
                (0.020, 0.010, 0.008),
                (button_start_x + k * 0.040, y + (0.013 if y > 0 else -0.013), H * 0.30),
                rubber,
                f"{name_prefix}_button_{k}",
            )
    if r.control_style == "side_panel_with_dial":
        x = W * 0.5 + 0.010
        _add_box(
            body,
            (0.020, min(0.28, D * 0.28), 0.145),
            (x, -D * 0.18, H * 0.34),
            trim,
            "side_control_plate",
        )
        _add_box(
            body,
            (0.008, min(0.11, D * 0.13), 0.060),
            (x + 0.012, -D * 0.04, H * 0.39),
            accent,
            "side_control_label",
        )
    if r.control_style == "rear_service_wall":
        for k in range(6):
            z = H * 0.18 + k * 0.022
            _add_box(
                body,
                (W * 0.35, 0.008, 0.008),
                (0.0, -D * 0.5 - 0.003, z),
                rail,
                f"rear_vent_slat_{k}",
            )


def _build_supports(
    body, r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig, *, rubber, rail, trim
) -> None:
    W = r.cabinet_width
    D = r.cabinet_depth
    if r.base_support_style == "feet":
        for ix, sx in enumerate((-1.0, 1.0)):
            for iy, sy in enumerate((-1.0, 1.0)):
                _add_cyl(
                    body,
                    radius=0.032,
                    length=0.050,
                    xyz=(sx * W * 0.39, sy * D * 0.35, 0.025),
                    rpy=(0.0, 0.0, 0.0),
                    material=rubber,
                    name=f"rubber_foot_{ix}_{iy}",
                )
    elif r.base_support_style == "skid_base":
        for sy, label in ((-1.0, "rear"), (1.0, "front")):
            _add_box(
                body,
                (W * 0.84, 0.050, 0.052),
                (0.0, sy * D * 0.36, 0.026),
                rubber,
                f"{label}_skid_base",
            )
    elif r.base_support_style == "casters":
        for ix, sx in enumerate((-1.0, 1.0)):
            for iy, sy in enumerate((-1.0, 1.0)):
                x = sx * W * 0.39
                y = sy * D * 0.35
                _add_box(
                    body,
                    (0.070, 0.045, 0.004),
                    (x, y, -0.002),
                    trim,
                    f"caster_mount_plate_{ix}_{iy}",
                )


def _build_lid_visuals(
    lid,
    r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig,
    *,
    glass,
    rail,
    rubber,
    accent,
    lid_index: int,
    z_tier: int,
) -> None:
    lid_w = r.lid_width
    lid_d = r.lid_depth
    frame = r.lid_frame_thickness
    glass_t = r.glass_thickness
    shoe_h = 0.010
    glass_z = shoe_h + 0.004 + glass_t * 0.5
    frame_z = shoe_h + 0.003 + frame * 0.5
    joint_y = _lid_shoe_y(r)

    def local_y(world_y: float) -> float:
        return world_y - joint_y

    _add_box(
        lid,
        (lid_w - 2.0 * frame, lid_d - 2.0 * frame, glass_t),
        (0.0, local_y(0.0), glass_z),
        glass,
        "glass_pane",
    )
    _add_box(
        lid,
        (lid_w, frame, frame),
        (0.0, local_y(lid_d * 0.5 - frame * 0.5), frame_z),
        rail,
        "front_frame",
    )
    _add_box(
        lid,
        (lid_w, frame, frame),
        (0.0, local_y(-lid_d * 0.5 + frame * 0.5), frame_z),
        rail,
        "rear_frame",
    )
    cap_y = lid_d * 0.5 - frame * 0.5
    cap_w = frame * 1.35
    for sx, x_label in ((-1.0, "left"), (1.0, "right")):
        x = sx * (lid_w * 0.5 - frame * 0.5)
        _add_box(
            lid,
            (frame, cap_w, frame),
            (x, local_y(cap_y), frame_z),
            rail,
            f"{x_label}_front_corner_cap",
        )
        _add_box(
            lid,
            (frame, cap_w, frame),
            (x, local_y(-cap_y), frame_z),
            rail,
            f"{x_label}_rear_corner_cap",
        )
    shoe_z = shoe_h * 0.5 + 0.004
    for y, label in ((_lid_shoe_y(r), "front"), (-_lid_shoe_y(r), "rear")):
        _add_box(
            lid,
            (lid_w * 0.82, frame * 0.50, shoe_h),
            (0.0, local_y(y), shoe_z),
            rubber,
            f"{label}_sliding_shoe",
        )
    grip_w = min(lid_w * 0.28, 0.24)
    _add_box(
        lid,
        (grip_w, min(0.010, frame * 0.55), min(0.008, frame * 0.38)),
        (0.0, local_y(lid_d * 0.5 - frame * 0.32), frame_z + frame * 0.04),
        rubber,
        "recessed_finger_slot",
    )
    if r.lid_profile == "raised_service_hatch":
        _add_box(
            lid,
            (lid_w * 0.32, lid_d * 0.26, 0.014),
            (lid_w * 0.18, local_y(0.0), frame_z + 0.024),
            rail,
            "service_hatch_outline",
        )
    lid.inertial = Inertial.from_geometry(
        Box((lid_w, lid_d, max(0.026, frame + glass_t))),
        mass=7.5,
        origin=Origin(xyz=(0.0, local_y(0.0), 0.020 + z_tier * 0.002)),
    )
    _ = lid_index


def _lid_origin_for_index(
    r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig, lid_index: int
) -> tuple[float, float, float]:
    if r.lid_layout == "single_deli_slider":
        return (-r.cabinet_width * 0.22, _lid_shoe_y(r), _lid_track_contact_z(r, 0))
    if r.lid_layout == "three_independent_bays":
        bay_w = r.liner_width / r.bay_count
        x = -r.liner_width * 0.5 + bay_w * (lid_index + 0.5)
        return (x - r.lid_travel * 0.25, _lid_shoe_y(r), _lid_track_contact_z(r, 0))
    if r.lid_layout == "upper_lower_tier":
        x = (-0.22 if lid_index == 0 else 0.18) * r.cabinet_width
        z = _lid_track_contact_z(r, lid_index)
        return (x, _lid_shoe_y(r), z)
    if r.lid_layout == "curved_barrel_pair":
        x = (-0.18 if lid_index == 0 else 0.18) * r.cabinet_width
        z = _lid_track_contact_z(r, lid_index)
        return (x, _lid_shoe_y(r), z)
    x = (-0.20 if lid_index == 0 else 0.20) * r.cabinet_width
    z = _lid_track_contact_z(r, lid_index)
    return (x, _lid_shoe_y(r), z)


def _slide_axis_for_lid(
    r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig,
    lid_index: int,
    origin: tuple[float, float, float],
) -> tuple[float, float, float]:
    if r.lid_layout == "three_independent_bays":
        if origin[0] < -r.lid_span * 0.25:
            return (-1.0, 0.0, 0.0)
        return (1.0, 0.0, 0.0)
    if r.lid_layout == "single_deli_slider":
        return (1.0, 0.0, 0.0)
    return (1.0, 0.0, 0.0) if lid_index % 2 == 0 else (-1.0, 0.0, 0.0)


def _build_optional_dial(
    model: ArticulatedObject,
    body,
    r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig,
    *,
    accent,
    rubber,
) -> None:
    if r.control_style not in {"front_panel", "side_panel_with_dial"}:
        return
    dial = model.part("thermostat_dial")
    if r.control_style == "front_panel":
        _add_cyl(
            dial,
            radius=0.026,
            length=0.024,
            xyz=(0.0, 0.0, 0.0),
            rpy=(math.pi / 2.0, 0.0, 0.0),
            material=rubber,
            name="dial_cap",
        )
        _add_box(dial, (0.006, 0.004, 0.026), (0.0, -0.014, 0.018), accent, "dial_indicator")
        panel_w = min(0.34, r.cabinet_width * 0.22)
        origin = (
            r.cabinet_width * 0.26 - panel_w * 0.34,
            r.cabinet_depth * 0.5 + 0.034,
            r.cabinet_height * 0.34,
        )
        axis = (0.0, 1.0, 0.0)
    else:
        _add_cyl(
            dial,
            radius=0.026,
            length=0.024,
            xyz=(0.0, 0.0, 0.0),
            rpy=(0.0, math.pi / 2.0, 0.0),
            material=rubber,
            name="dial_cap",
        )
        _add_box(dial, (0.004, 0.006, 0.026), (0.014, 0.0, 0.018), accent, "dial_indicator")
        origin = (r.cabinet_width * 0.5 + 0.032, -r.cabinet_depth * 0.18, r.cabinet_height * 0.34)
        axis = (1.0, 0.0, 0.0)
    model.articulation(
        "thermostat_dial_joint",
        ArticulationType.REVOLUTE,
        parent=body,
        child=dial,
        origin=Origin(xyz=origin),
        axis=axis,
        motion_limits=MotionLimits(effort=0.8, velocity=4.0, lower=-2.35, upper=2.35),
        meta=_joint_meta("revolute", axis, origin, (-2.35, 2.35), source_id="S10"),
    )


def _build_optional_lock_flap(
    model: ArticulatedObject,
    body,
    r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig,
    *,
    trim,
    rubber,
) -> None:
    if r.body_profile != "three_bay_island":
        return
    flap = model.part("side_lock_flap")
    _add_box(flap, (0.060, 0.012, 0.085), (0.014, 0.0, -0.035), trim, "lock_flap_plate")
    _add_cyl(
        flap,
        radius=0.010,
        length=0.070,
        xyz=(0.0, 0.0, 0.006),
        rpy=(0.0, 0.0, 0.0),
        material=rubber,
        name="lock_flap_hinge_barrel",
    )
    origin = (r.cabinet_width * 0.5 + 0.014, r.cabinet_depth * 0.24, r.cabinet_height * 0.74)
    model.articulation(
        "lock_flap_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=flap,
        origin=Origin(xyz=origin),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.8, velocity=2.0, lower=-0.45, upper=1.05),
        meta=_joint_meta("revolute", (0.0, 0.0, 1.0), origin, (-0.45, 1.05), source_id="S7"),
    )


def _build_caster_joints(
    model: ArticulatedObject,
    body,
    r: ResolvedDisplayFreezerWithSlidingGlassLidsConfig,
    *,
    rail,
    rubber,
) -> None:
    if r.base_support_style != "casters":
        return
    for idx, (sx, sy) in enumerate(((-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0))):
        fork = model.part(f"caster_fork_{idx}")
        _add_box(fork, (0.045, 0.018, 0.055), (0.0, -0.016, -0.026), rail, "left_fork_cheek")
        _add_box(fork, (0.045, 0.018, 0.055), (0.0, 0.016, -0.026), rail, "right_fork_cheek")
        _add_cyl(
            fork,
            radius=0.015,
            length=0.040,
            xyz=(0.0, 0.0, -0.058),
            rpy=(math.pi / 2.0, 0.0, 0.0),
            material=rubber,
            name="wheel_visual",
        )
        origin = (sx * r.cabinet_width * 0.39, sy * r.cabinet_depth * 0.35, -0.004)
        model.articulation(
            f"caster_swivel_{idx}",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=fork,
            origin=Origin(xyz=origin),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=1.0, velocity=5.0),
            meta=_joint_meta("continuous", (0.0, 0.0, 1.0), origin, "unbounded", source_id="S1"),
        )


def build_display_freezer(
    config: DisplayFreezerWithSlidingGlassLidsConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or DisplayFreezerWithSlidingGlassLidsConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-display-freezer-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.material_style]
    shell = _mat(model, palette, "shell")
    liner = _mat(model, palette, "liner")
    trim = _mat(model, palette, "trim")
    rail = _mat(model, palette, "rail")
    rubber = _mat(model, palette, "rubber")
    glass = _mat(model, palette, "glass")
    wire = _mat(model, palette, "wire")
    product = _mat(model, palette, "product")
    accent = _mat(model, palette, "accent")

    body = model.part("cabinet")
    _build_outer_shell(body, r, shell=shell, liner=liner, trim=trim, rubber=rubber)
    _build_rail_system(body, r, glass=glass, rail=rail, rubber=rubber, trim=trim)
    _build_storage(body, r, wire=wire, product=product, liner=liner, trim=trim)
    _build_controls(body, r, trim=trim, rubber=rubber, accent=accent, rail=rail)
    _build_supports(body, r, rubber=rubber, rail=rail, trim=trim)

    for lid_index in range(r.lid_count):
        lid = model.part(f"sliding_lid_{lid_index}")
        tier = lid_index % max(1, r.rail_tier_count)
        _build_lid_visuals(
            lid,
            r,
            glass=glass,
            rail=rail,
            rubber=rubber,
            accent=accent,
            lid_index=lid_index,
            z_tier=tier,
        )
        origin = _lid_origin_for_index(r, lid_index)
        axis = _slide_axis_for_lid(r, lid_index, origin)
        model.articulation(
            f"lid_slide_{lid_index}",
            ArticulationType.PRISMATIC,
            parent=body,
            child=lid,
            origin=Origin(xyz=origin),
            axis=axis,
            motion_limits=MotionLimits(effort=55.0, velocity=0.55, lower=0.0, upper=r.lid_travel),
            meta=_joint_meta("prismatic", axis, origin, (0.0, r.lid_travel), source_id="S3"),
        )

    _build_optional_dial(model, body, r, accent=accent, rubber=rubber)
    _build_optional_lock_flap(model, body, r, trim=trim, rubber=rubber)
    _build_caster_joints(model, body, r, rail=rail, rubber=rubber)
    return model


def build_seeded_display_freezer(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_display_freezer(config_from_seed(seed), assets=assets)


def with_overrides(
    config: DisplayFreezerWithSlidingGlassLidsConfig, **kwargs: object
) -> DisplayFreezerWithSlidingGlassLidsConfig:
    return replace(config, **kwargs)


def _visual_names(part) -> set[str]:
    return {visual.name for visual in part.visuals}


def run_display_freezer_tests(
    object_model: ArticulatedObject,
    config: DisplayFreezerWithSlidingGlassLidsConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    cabinet = object_model.get_part("cabinet")
    cabinet_visuals = _visual_names(cabinet)
    # Sliding lids ride on the track rails with running clearance; they read as
    # geometrically isolated even though they are joint-mounted on the cabinet.
    for _p in object_model.parts:
        if _p.name.startswith("sliding_lid"):
            ctx.allow_isolated_part(
                _p,
                reason="Sliding glass lid is joint-mounted on the cabinet track rails with running clearance.",
            )
    # Adjacent sliding lids share the same track and can graze as they pass.
    _lids = [p for p in object_model.parts if p.name.startswith("sliding_lid")]
    for _i in range(len(_lids)):
        for _j in range(_i + 1, len(_lids)):
            ctx.allow_overlap(
                _lids[_i], _lids[_j],
                reason="Adjacent sliding glass lids share the track and graze when passing.",
            )
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=120,
        overlap_tol=0.006,
        overlap_volume_tol=0.0,
        ignore_adjacent=True,
        ignore_fixed=True,
    )
    ctx.check(
        "identity_cabinet_liner_rim_rails",
        {
            "liner_floor",
            "front_top_rim",
            "rear_top_rim",
            "front_track_tier_0",
            "rear_track_tier_0",
        }.issubset(cabinet_visuals),
        details=str(sorted(cabinet_visuals)[:40]),
    )
    ctx.check(
        "lid_contact_channels_are_continuous",
        {"front_lid_contact_channel_tier_0", "rear_lid_contact_channel_tier_0"}.issubset(
            cabinet_visuals
        ),
        details=str(sorted(cabinet_visuals)[:60]),
    )
    ctx.check(
        "inner_runner_shelves_support_contact_channels",
        {"front_inner_runner_shelf_tier_0", "rear_inner_runner_shelf_tier_0"}.issubset(
            cabinet_visuals
        ),
        details=str(sorted(cabinet_visuals)[:60]),
    )
    ctx.check(
        "track_grooves_are_recessed_not_bare_strips",
        {"front_recessed_track_groove_tier_0", "rear_recessed_track_groove_tier_0"}.issubset(
            cabinet_visuals
        )
        and not any(name.endswith("_wear_strip_tier_0") for name in cabinet_visuals),
        details=str(
            sorted(name for name in cabinet_visuals if "groove" in name or "wear_strip" in name)
        ),
    )
    ctx.check(
        "no_lid_anchor_pad_shims",
        not any(
            name.startswith("lid_slide_anchor_") or "contact_pad" in name
            for name in cabinet_visuals
        ),
        details=str(
            sorted(name for name in cabinet_visuals if "lid_slide" in name or "contact_pad" in name)
        ),
    )
    lid_joints = [
        joint for joint in object_model.articulations if joint.name.startswith("lid_slide_")
    ]
    ctx.check(
        "lid_joint_count", len(lid_joints) == r.lid_count, details=str([j.name for j in lid_joints])
    )
    if r.lid_layout == "three_independent_bays":
        lid_zs = [joint.origin.xyz[2] for joint in lid_joints]
        ctx.check(
            "three_bay_lids_share_contact_tier",
            r.rail_tier_count == 1 and max(lid_zs) - min(lid_zs) < 1e-9,
            details=str((r.rail_tier_count, lid_zs)),
        )
    for joint in lid_joints:
        ctx.check(
            f"{joint.name}_is_prismatic",
            joint.articulation_type == ArticulationType.PRISMATIC,
            details=str(joint.articulation_type),
        )
        ctx.check(
            f"{joint.name}_axis_horizontal",
            tuple(joint.axis) in {(1.0, 0.0, 0.0), (-1.0, 0.0, 0.0)},
            details=str(joint.axis),
        )
        ctx.check(
            f"{joint.name}_metadata",
            {"type", "axis", "origin", "range", "source_id"}.issubset(joint.meta),
            details=str(joint.meta),
        )
    for lid_index in range(r.lid_count):
        lid_name = f"sliding_lid_{lid_index}"
        lid = object_model.get_part(lid_name)
        lid_visuals = _visual_names(lid)
        ctx.check(
            f"{lid_name}_framed_glass_identity",
            {
                "glass_pane",
                "front_frame",
                "rear_frame",
                "front_sliding_shoe",
                "rear_sliding_shoe",
            }.issubset(lid_visuals),
            details=str(lid_visuals),
        )
        ctx.expect_aabb_overlap(
            lid_name,
            "cabinet",
            axes="x",
            min_overlap=min(r.lid_width * 0.45, r.cabinet_width * 0.25),
        )
        ctx.expect_aabb_overlap(
            lid_name,
            "cabinet",
            axes="y",
            min_overlap=min(r.lid_depth * 0.60, r.cabinet_depth * 0.45),
        )
        with ctx.pose(**{f"lid_slide_{lid_index}": r.lid_travel}):
            ctx.expect_aabb_overlap(
                lid_name,
                "cabinet",
                axes="x",
                min_overlap=min(r.lid_width * 0.25, r.cabinet_width * 0.12),
            )
    capacity = r.storage_grid_cols * r.storage_grid_rows * r.storage_tier_count
    ctx.check(
        "storage_capacity_consistent",
        r.basket_count <= capacity,
        details=str((r.basket_count, capacity)),
    )
    expected_cell_width = (
        r.usable_storage_width - (r.storage_grid_cols - 1) * r.storage_gap
    ) / r.storage_grid_cols
    expected_cell_depth = (
        r.usable_storage_depth - (r.storage_grid_rows - 1) * r.storage_gap
    ) / r.storage_grid_rows
    ctx.check(
        "storage_width_formula",
        abs(r.cell_width - expected_cell_width) < 1e-9,
        details=str((r.cell_width, expected_cell_width)),
    )
    ctx.check(
        "storage_depth_formula",
        abs(r.cell_depth - expected_cell_depth) < 1e-9,
        details=str((r.cell_depth, expected_cell_depth)),
    )
    if r.interior_storage_layout != "empty_open_well":
        storage_names = [name for name in cabinet_visuals if name.startswith("storage_0")]
        ctx.check("storage_visuals_present", bool(storage_names), details=str(storage_names[:12]))
    if r.rail_layout == "three_bay_tracks":
        ctx.check(
            "three_bay_track_stops_attached_to_rails",
            any(name.startswith("front_bay_track_stop") for name in cabinet_visuals)
            and any(name.startswith("rear_bay_track_stop") for name in cabinet_visuals)
            and not any(name.startswith("cross_bay_track_stop") for name in cabinet_visuals),
            details=str(cabinet_visuals),
        )
    if r.control_style in {"front_panel", "side_panel_with_dial"}:
        dial_joint = object_model.get_articulation("thermostat_dial_joint")
        ctx.check(
            "thermostat_dial_revolute",
            dial_joint.articulation_type == ArticulationType.REVOLUTE,
            details=str(dial_joint.articulation_type),
        )
    if r.body_profile == "three_bay_island":
        lock_joint = object_model.get_articulation("lock_flap_hinge")
        ctx.check(
            "lock_flap_revolute",
            lock_joint.articulation_type == ArticulationType.REVOLUTE,
            details=str(lock_joint.articulation_type),
        )
    if r.base_support_style == "casters":
        caster_joints = [
            joint for joint in object_model.articulations if joint.name.startswith("caster_swivel_")
        ]
        ctx.check(
            "caster_swivel_count",
            len(caster_joints) == 4,
            details=str([j.name for j in caster_joints]),
        )
    ctx.check(
        "compat_lid_layout",
        r.rail_layout == _rail_layout_for_lid_layout(r.lid_layout)
        or r.body_profile in {"compact_deli_counter", "three_bay_island"},
        details=str((r.body_profile, r.lid_layout, r.rail_layout)),
    )
    return ctx.report()
