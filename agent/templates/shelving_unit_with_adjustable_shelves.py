# SPDX-License-Identifier: Apache-2.0

"""Source-backed multi-bay shelving with independently adjustable shelves."""

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

AssemblyFamily = Literal[
    "stepped_grid_open_bins",
    "stepped_grid_lidded_drawers",
    "stepped_grid_wire_baskets",
    "open_ladder_solid_shelves",
    "uniform_grid_slotted_shelves",
    "wall_rail_wire_shelves",
]

FAMILIES: tuple[AssemblyFamily, ...] = (
    "stepped_grid_open_bins",
    "stepped_grid_lidded_drawers",
    "stepped_grid_wire_baskets",
    "open_ladder_solid_shelves",
    "uniform_grid_slotted_shelves",
    "wall_rail_wire_shelves",
)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("assembly_family", FAMILIES),
        multiplicity_slot(
            "bay_count",
            (4, 5, 6, 7, 8, 9),
            item_slot="assembly_family",
        ),
        multiplicity_slot(
            "level_count",
            (4, 5, 6, 7, 8),
            item_slot="assembly_family",
        ),
        multiplicity_slot(
            "shelf_count",
            (3, 5, 7),
            item_slot="assembly_family",
        ),
    )
)


@dataclass(frozen=True)
class Config:
    assembly_family: AssemblyFamily = "stepped_grid_open_bins"
    bay_count: int = 6
    level_count: int = 6
    shelf_count: int = 5
    bay_width_m: float | None = None
    level_pitch_m: float | None = None
    shelf_depth_m: float | None = None
    name: str = "shelving_unit_with_adjustable_shelves"


@dataclass(frozen=True)
class ResolvedConfig:
    assembly_family: AssemblyFamily
    bay_count: int
    level_count: int
    tall_bay_count: int
    low_bay_count: int
    low_level_count: int
    shelf_count: int
    bay_width_m: float
    level_pitch_m: float
    shelf_depth_m: float
    frame_depth_m: float
    frame_width_m: float
    tall_height_m: float
    low_height_m: float
    tube_m: float
    insert_width_m: float
    shelf_thickness_m: float
    shelf_travel_m: float
    storage_height_m: float
    storage_travel_m: float
    bay_centers_m: tuple[float, ...]
    cubby_count: int
    storage_count: int
    cubby_layout: tuple[tuple[int, int], ...]
    shelf_placements: tuple[tuple[int, int], ...]
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x5E1F_2026)
    return Config(
        assembly_family=choices["assembly_family"],
        bay_count=choices["bay_count"],
        level_count=choices["level_count"],
        shelf_count=choices["shelf_count"],
        bay_width_m=round(rng.uniform(0.34, 0.42), 4),
        level_pitch_m=round(rng.uniform(0.34, 0.40), 4),
        shelf_depth_m=round(rng.uniform(0.33, 0.43), 4),
    )


_SHELF_PLACEMENTS: dict[int, tuple[tuple[int, int], ...]] = {
    3: ((0, 5), (1, 1), (3, 1)),
    5: ((0, 5), (2, 4), (2, 3), (0, 1), (3, 1)),
    7: ((0, 2), (0, 4), (1, 1), (1, 3), (1, 5), (2, 2), (3, 2)),
}


def _grid_partition(bay_count: int, level_count: int) -> tuple[int, int, int]:
    tall_bays = (bay_count + 1) // 2
    low_bays = bay_count // 2
    low_levels = max(2, (level_count + 1) // 2)
    return tall_bays, low_bays, low_levels


def _ordered_cells(bays: range, levels: int) -> list[tuple[int, int]]:
    cells: list[tuple[int, int]] = []
    bay_values = tuple(bays)
    for row, level in enumerate(range(levels - 1, -1, -1)):
        ordered_bays = bay_values if row % 2 == 0 else tuple(reversed(bay_values))
        cells.extend((bay, level) for bay in ordered_bays)
    return cells


def _derive_cubby_layout(
    bay_count: int,
    level_count: int,
    shelf_count: int,
    *,
    cubby_count: int,
) -> tuple[tuple[int, int], ...]:
    if bay_count == 6 and level_count == 6 and cubby_count == 7:
        return (
            (2, 5),
            (1, 4),
            (0, 3),
            (1, 2),
            (2, 1),
            (4, 2),
            (5, 1),
        )
    tall_bays, low_bays, low_levels = _grid_partition(bay_count, level_count)
    tall_cells = [cell for cell in _ordered_cells(range(tall_bays), level_count) if cell[1] > 0]
    low_cells = [
        cell for cell in _ordered_cells(range(tall_bays, bay_count), low_levels) if cell[1] > 0
    ]
    tall_target = min(
        len(tall_cells),
        max(1, int(round(cubby_count * 5.0 / 7.0))),
    )
    selected = tall_cells[:tall_target]
    selected += low_cells[: max(0, cubby_count - len(selected))]
    if len(selected) != cubby_count:
        raise ValueError(
            "grid cannot place the requested source-like cubby count "
            f"for bay_count={bay_count}, level_count={level_count}, "
            f"shelf_count={shelf_count}"
        )
    return tuple(selected)


def _derive_shelf_layout(
    bay_count: int,
    level_count: int,
    shelf_count: int,
    cubby_layout: tuple[tuple[int, int], ...],
) -> tuple[tuple[int, int], ...]:
    if bay_count == 6 and level_count == 6 and shelf_count in _SHELF_PLACEMENTS:
        return _SHELF_PLACEMENTS[shelf_count]
    tall_bays, _low_bays, low_levels = _grid_partition(bay_count, level_count)
    occupied = set(cubby_layout)
    cells = [cell for cell in _ordered_cells(range(tall_bays), level_count) if cell[1] > 0]
    cells += [
        cell for cell in _ordered_cells(range(tall_bays, bay_count), low_levels) if cell[1] > 0
    ]
    selected = [cell for cell in cells if cell not in occupied][:shelf_count]
    if len(selected) != shelf_count:
        raise ValueError(
            "grid cannot place the requested adjustable shelf count "
            f"for bay_count={bay_count}, level_count={level_count}"
        )
    return tuple(selected)


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "assembly_family": config.assembly_family,
            "bay_count": config.bay_count,
            "level_count": config.level_count,
            "shelf_count": config.shelf_count,
        }
    )
    bay_width = 0.37 if config.bay_width_m is None else float(config.bay_width_m)
    level_pitch = 0.37 if config.level_pitch_m is None else float(config.level_pitch_m)
    shelf_depth = 0.38 if config.shelf_depth_m is None else float(config.shelf_depth_m)
    if not 0.34 <= bay_width <= 0.42:
        raise ValueError("bay_width_m must be in [0.34, 0.42]")
    if not 0.34 <= level_pitch <= 0.40:
        raise ValueError("level_pitch_m must be in [0.34, 0.40]")
    if not 0.33 <= shelf_depth <= 0.43:
        raise ValueError("shelf_depth_m must be in [0.33, 0.43]")

    tall_bays, low_bays, low_levels = _grid_partition(
        config.bay_count,
        config.level_count,
    )
    cell_capacity = tall_bays * (config.level_count - 1) + low_bays * (low_levels - 1)
    cubby_count = min(7, max(1, cell_capacity - config.shelf_count))
    cubby_layout = _derive_cubby_layout(
        config.bay_count,
        config.level_count,
        config.shelf_count,
        cubby_count=cubby_count,
    )
    shelf_placements = _derive_shelf_layout(
        config.bay_count,
        config.level_count,
        config.shelf_count,
        cubby_layout,
    )
    tube = min(0.030, bay_width * 0.075)
    centers = tuple(
        (index - (config.bay_count - 1) * 0.5) * bay_width for index in range(config.bay_count)
    )
    return ResolvedConfig(
        assembly_family=config.assembly_family,
        bay_count=config.bay_count,
        level_count=config.level_count,
        tall_bay_count=tall_bays,
        low_bay_count=low_bays,
        low_level_count=low_levels,
        shelf_count=config.shelf_count,
        bay_width_m=bay_width,
        level_pitch_m=level_pitch,
        shelf_depth_m=shelf_depth,
        frame_depth_m=shelf_depth + 0.075,
        frame_width_m=config.bay_count * bay_width + tube,
        tall_height_m=config.level_count * level_pitch,
        low_height_m=low_levels * level_pitch,
        tube_m=tube,
        insert_width_m=bay_width - tube - 0.030,
        shelf_thickness_m=0.026,
        shelf_travel_m=min(0.055, level_pitch * 0.15),
        storage_height_m=min(0.115, level_pitch * 0.30),
        storage_travel_m=min(0.20, shelf_depth * 0.52),
        bay_centers_m=centers,
        cubby_count=cubby_count,
        storage_count=config.bay_count,
        cubby_layout=cubby_layout,
        shelf_placements=shelf_placements,
        name=config.name,
    )


def _materials(model: ArticulatedObject) -> dict[str, str]:
    model.material("charcoal_steel", rgba=(0.055, 0.060, 0.058, 1.0))
    model.material("rail_slot", rgba=(0.64, 0.67, 0.65, 1.0))
    model.material("walnut", rgba=(0.47, 0.27, 0.13, 1.0))
    model.material("walnut_shadow", rgba=(0.24, 0.105, 0.045, 1.0))
    model.material("light_oak", rgba=(0.79, 0.63, 0.44, 1.0))
    model.material("oak_edge", rgba=(0.64, 0.44, 0.26, 1.0))
    model.material("wire_steel", rgba=(0.16, 0.18, 0.18, 1.0))
    model.material("wall_panel", rgba=(0.11, 0.12, 0.12, 1.0))
    model.material("rubber", rgba=(0.025, 0.027, 0.026, 1.0))
    return {
        "frame": "charcoal_steel",
        "slot": "rail_slot",
        "cubby": "walnut",
        "cubby_shadow": "walnut_shadow",
        "shelf": "light_oak",
        "edge": "oak_edge",
        "wire": "wire_steel",
        "wall": "wall_panel",
        "rubber": "rubber",
    }


def _frame_box(frame, size, xyz, material: str, name: str) -> None:
    frame.visual(
        Box(size),
        origin=Origin(xyz=xyz),
        material=material,
        name=name,
        material_class_id="metal.blackened_gunmetal",
    )


def _build_frame(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
):
    family = r.assembly_family
    frame = model.part(
        f"assembly_family__{family}__frame",
        meta={
            "role": "load_bearing_frame",
            "family": family,
            "bay_count": r.bay_count,
            "tall_levels": r.level_count,
            "low_levels": r.low_level_count,
            "stepped": family != "uniform_grid_slotted_shelves",
        },
    )
    tube = r.tube_m
    depth = r.frame_depth_m
    front_y = -depth * 0.5
    rear_y = depth * 0.5
    posts = tuple((index - r.bay_count * 0.5) * r.bay_width_m for index in range(r.bay_count + 1))
    tall_levels = tuple(index * r.level_pitch_m for index in range(r.level_count + 1))
    low_levels = tuple(index * r.level_pitch_m for index in range(r.low_level_count + 1))

    if family == "wall_rail_wire_shelves":
        tall_width = r.tall_bay_count * r.bay_width_m + tube
        low_width = r.low_bay_count * r.bay_width_m + tube
        tall_center = (r.bay_centers_m[0] + r.bay_centers_m[r.tall_bay_count - 1]) * 0.5
        low_center = (r.bay_centers_m[r.tall_bay_count] + r.bay_centers_m[-1]) * 0.5
        _frame_box(
            frame,
            (tall_width, 0.018, r.tall_height_m + tube),
            (tall_center, rear_y + 0.034, r.tall_height_m * 0.5),
            mats["wall"],
            "tall_wall_backplate",
        )
        _frame_box(
            frame,
            (low_width, 0.018, r.low_height_m + tube),
            (low_center, rear_y + 0.034, r.low_height_m * 0.5),
            mats["wall"],
            "low_wall_backplate",
        )
        for post_index, x in enumerate(posts):
            height = r.tall_height_m if post_index <= r.tall_bay_count else r.low_height_m
            _frame_box(
                frame,
                (tube, 0.032, height),
                (x, rear_y + 0.010, height * 0.5),
                mats["frame"],
                f"wall_standard_{post_index}",
            )
            level_count = r.level_count if post_index <= r.tall_bay_count else r.low_level_count
            for level in range(1, level_count + 1):
                _frame_box(
                    frame,
                    (0.007, 0.004, 0.050),
                    (x, rear_y - 0.008, level * r.level_pitch_m - 0.06),
                    mats["slot"],
                    f"wall_standard_slot_{post_index}_{level}",
                )
        for bay_index, center_x in enumerate(r.bay_centers_m):
            levels = tall_levels if bay_index < r.tall_bay_count else low_levels
            for level_index, z in enumerate(levels):
                support_z = max(tube * 0.5, z)
                for side, x in (
                    ("left", center_x - r.bay_width_m * 0.5),
                    ("right", center_x + r.bay_width_m * 0.5),
                ):
                    _frame_box(
                        frame,
                        (tube, depth, tube),
                        (x, 0.0, support_z),
                        mats["frame"],
                        f"cantilever_{bay_index}_{level_index}_{side}",
                    )
                _frame_box(
                    frame,
                    (r.bay_width_m + tube, tube, tube),
                    (center_x, front_y, support_z),
                    mats["frame"],
                    f"cantilever_front_bearing_{bay_index}_{level_index}",
                )
            _frame_box(
                frame,
                (tube, depth, tube),
                (center_x, 0.0, tube * 0.5),
                mats["frame"],
                f"wall_storage_runner_{bay_index}",
            )
        return frame

    uniform = family == "uniform_grid_slotted_shelves"
    open_ladder = family == "open_ladder_solid_shelves"
    for post_index, x in enumerate(posts):
        height = r.tall_height_m if uniform or post_index <= r.tall_bay_count else r.low_height_m
        for side, y in (("front", front_y), ("rear", rear_y)):
            _frame_box(
                frame,
                (tube, tube, height),
                (x, y, height * 0.5),
                mats["frame"],
                (
                    f"uniform_post_{post_index}_{side}"
                    if uniform
                    else f"ladder_upright_{post_index}_{side}"
                    if open_ladder
                    else f"{'tall' if post_index <= r.tall_bay_count else 'low'}_post_{post_index}_{side}"
                ),
            )
        if uniform:
            for level in range(1, r.level_count + 1):
                _frame_box(
                    frame,
                    (0.007, 0.004, 0.050),
                    (x, front_y - tube * 0.55, level * r.level_pitch_m - 0.055),
                    mats["slot"],
                    f"slot_tab_{post_index}_{level}",
                )

    level_sets = (
        (0, r.tall_bay_count, tall_levels),
        (
            r.tall_bay_count,
            r.bay_count,
            tall_levels if uniform else low_levels,
        ),
    )
    for first_bay, last_bay, levels in level_sets:
        x0 = posts[first_bay]
        x1 = posts[last_bay]
        for level_index, z in enumerate(levels):
            support_z = max(tube * 0.5, z)
            for side, y in (("front", front_y), ("rear", rear_y)):
                _frame_box(
                    frame,
                    (x1 - x0 + tube, tube, tube),
                    ((x0 + x1) * 0.5, y, support_z),
                    mats["frame"],
                    (
                        f"ladder_rung_{first_bay}_{level_index}_{side}"
                        if open_ladder
                        else f"cross_rail_{first_bay}_{level_index}_{side}"
                    ),
                )
            if not open_ladder or level_index in {0, len(levels) - 1}:
                for post_index in range(first_bay, last_bay + 1):
                    _frame_box(
                        frame,
                        (tube, depth + tube, tube),
                        (posts[post_index], 0.0, support_z),
                        mats["frame"],
                        f"depth_tie_{first_bay}_{post_index}_{level_index}",
                    )

    for bay_index, center_x in enumerate(r.bay_centers_m):
        _frame_box(
            frame,
            (tube, depth, tube),
            (center_x, 0.0, tube * 0.5),
            mats["frame"],
            f"storage_runner_{bay_index}",
        )
    for post_index, x in enumerate(posts):
        for side, y in (("front", front_y), ("rear", rear_y)):
            _frame_box(
                frame,
                (tube * 1.55, tube * 1.55, 0.009),
                (x, y, 0.0045),
                mats["rubber"],
                f"foot_{post_index}_{side}",
            )
    return frame


def _add_cubby(
    model: ArticulatedObject,
    frame,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    index: int,
    bay: int,
    level: int,
) -> None:
    family = r.assembly_family
    width = r.insert_width_m - 0.010
    depth = r.shelf_depth_m + 0.035
    height = r.level_pitch_m * 0.78
    wall = 0.014
    cubby = model.part(
        f"assembly_family__{family}__cubby_{index}",
        meta={"role": "open_cubby", "bay": bay, "level": level},
    )
    cubby.visual(
        Box((width, depth, wall)),
        origin=Origin(xyz=(0.0, 0.0, wall * 0.5)),
        material=mats["cubby"],
        name="bottom_panel",
        material_class_id="wood.walnut_dark",
    )
    cubby.visual(
        Box((width, depth, wall)),
        origin=Origin(xyz=(0.0, 0.0, height - wall * 0.5)),
        material=mats["cubby"],
        name="top_panel",
        material_class_id="wood.walnut_dark",
    )
    for side, x in (
        ("left_panel", -width * 0.5 + wall * 0.5),
        ("right_panel", width * 0.5 - wall * 0.5),
    ):
        cubby.visual(
            Box((wall, depth, height - 2.0 * wall)),
            origin=Origin(xyz=(x, 0.0, height * 0.5)),
            material=mats["cubby"],
            name=side,
            material_class_id="wood.walnut_dark",
        )
    cubby.visual(
        Box((width - 2.0 * wall, wall, height - 2.0 * wall)),
        origin=Origin(xyz=(0.0, depth * 0.5 - wall * 0.5, height * 0.5)),
        material=mats["cubby"],
        name="back_panel",
        material_class_id="wood.walnut_dark",
    )
    cubby.visual(
        Box((width - 0.050, 0.003, height - 0.050)),
        origin=Origin(xyz=(0.0, depth * 0.5 - wall - 0.0015, height * 0.5)),
        material=mats["cubby_shadow"],
        name="recessed_inner_back",
        material_class_id="wood.walnut_dark",
    )
    support_z = level * r.level_pitch_m + r.tube_m * 0.5
    frame.visual(
        Box((r.bay_width_m, r.frame_depth_m, r.tube_m)),
        origin=Origin(
            xyz=(
                r.bay_centers_m[bay],
                0.0,
                support_z,
            )
        ),
        material=mats["frame"],
        name=f"cubby_bearing_runner_{index}",
        material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        f"assembly_family__{family}__frame_to_cubby_{index}",
        ArticulationType.FIXED,
        parent=frame,
        child=cubby,
        origin=Origin(
            xyz=(
                r.bay_centers_m[bay],
                0.0,
                support_z + r.tube_m * 0.5,
            )
        ),
    )


def _rod(
    part,
    *,
    length: float,
    radius: float,
    axis: str,
    xyz: tuple[float, float, float],
    material: str,
    name: str,
) -> None:
    rotations = {
        "x": (0.0, math.pi * 0.5, 0.0),
        "y": (math.pi * 0.5, 0.0, 0.0),
        "z": (0.0, 0.0, 0.0),
    }
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rotations[axis]),
        material=material,
        name=name,
        material_class_id="metal.steel_bare",
    )


def _add_shelf(
    model: ArticulatedObject,
    frame,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    index: int,
    bay: int,
    level: int,
) -> None:
    family = r.assembly_family
    wire = family in {"stepped_grid_wire_baskets", "wall_rail_wire_shelves"}
    shelf = model.part(
        f"assembly_family__{family}__shelf_{index}",
        meta={
            "role": "adjustable_shelf",
            "bay": bay,
            "level": level,
            "support_count": 4,
            "deck": "wire" if wire else "solid",
        },
    )
    width = r.insert_width_m
    depth = r.shelf_depth_m
    thickness = r.shelf_thickness_m
    if wire:
        rod_r = 0.0042
        for rod_index in range(8):
            x = -width * 0.42 + width * 0.84 * rod_index / 7.0
            _rod(
                shelf,
                length=depth,
                radius=rod_r,
                axis="y",
                xyz=(x, 0.0, 0.0),
                material=mats["wire"],
                name=f"deck_depth_rod_{rod_index}",
            )
        for rod_index, y in enumerate((-depth * 0.44, 0.0, depth * 0.44)):
            _rod(
                shelf,
                length=width,
                radius=rod_r * 1.12,
                axis="x",
                xyz=(0.0, y, 0.0),
                material=mats["wire"],
                name=f"deck_cross_rod_{rod_index}",
            )
    else:
        shelf.visual(
            Box((width, depth, thickness)),
            material=mats["shelf"],
            name="shelf_slab",
            material_class_id="wood.oak",
        )
        shelf.visual(
            Box((width, 0.007, thickness + 0.003)),
            origin=Origin(xyz=(0.0, -depth * 0.5 + 0.0035, 0.0)),
            material=mats["edge"],
            name="front_edge",
            material_class_id="wood.oak",
        )
    # The clip brackets must straddle the support rail across the whole
    # adjustment travel (so the shelf stays within the 1 mm supported band
    # even at the upper travel pose) yet stay short enough to clear any
    # cubby top panel in the cell below at the lower pose: at q=0 the clip
    # bottom sits travel + 1 mm below the rail top, and cubby tops stay at
    # least ~10 mm lower; at q=upper the clip bottom sits 1 mm below the
    # rail top with the 0.5 mm side gap preserved.
    hook_length = r.shelf_travel_m + 0.015
    support_z = -(thickness * 0.5 + hook_length * 0.5) + 0.002
    clip_depth = 0.012
    # Real clearance: the clip faces run parallel to the support rail inner
    # face with a positive gap (no intersection) that stays inside the 1 mm
    # band baseline QC counts as supported contact.
    clip_rail_gap = 0.0005
    support_y = r.frame_depth_m * 0.5 - r.tube_m * 0.5 - clip_rail_gap - clip_depth * 0.5
    for support_index, (x, y) in enumerate(
        (
            (-width * 0.42, -support_y),
            (width * 0.42, -support_y),
            (-width * 0.42, support_y),
            (width * 0.42, support_y),
        )
    ):
        shelf.visual(
            Box((0.030, clip_depth, hook_length)),
            origin=Origin(xyz=(x, y, support_z)),
            material=mats["frame"],
            name=f"support_clip_{support_index}",
            material_class_id="metal.blackened_gunmetal",
        )
        shelf_edge_y = math.copysign(depth * 0.5 - 0.004, y)
        clip_inner_y = y - math.copysign(clip_depth * 0.5, y)
        arm_length = abs(clip_inner_y - shelf_edge_y) + 0.010
        shelf.visual(
            Box((0.030, arm_length, 0.018)),
            origin=Origin(
                xyz=(
                    x,
                    (shelf_edge_y + clip_inner_y) * 0.5,
                    -0.006,
                )
            ),
            material=mats["frame"],
            name=f"support_arm_{support_index}",
            material_class_id="metal.blackened_gunmetal",
        )
    if family == "uniform_grid_slotted_shelves":
        for hook_index, x in enumerate((-width * 0.42, width * 0.42)):
            shelf.visual(
                Box((0.018, 0.022, 0.050)),
                origin=Origin(xyz=(x, depth * 0.5 - 0.010, -0.012)),
                material=mats["frame"],
                name=f"slotted_rear_hook_{hook_index}",
                material_class_id="metal.blackened_gunmetal",
            )

    model.articulation(
        f"assembly_family__{family}__adjust_shelf_{index}",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=shelf,
        origin=Origin(
            xyz=(
                r.bay_centers_m[bay],
                0.0,
                level * r.level_pitch_m + r.tube_m * 0.5 + thickness * 0.5 + 0.012,
            )
        ),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=120.0,
            velocity=0.08,
            lower=0.0,
            upper=r.shelf_travel_m,
        ),
        meta={"mechanism": "indexed vertical shelf repositioning"},
    )


def _add_open_bin_geometry(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    width = r.insert_width_m - 0.012
    depth = r.shelf_depth_m * 0.82
    height = r.storage_height_m
    wall = 0.012
    part.visual(
        Box((width, depth, wall)),
        origin=Origin(xyz=(0.0, 0.0, wall * 0.5)),
        material=mats["shelf"],
        name="bin_bottom",
        material_class_id="wood.oak",
    )
    for side, x in (
        ("bin_side_left", -width * 0.5 + wall * 0.5),
        ("bin_side_right", width * 0.5 - wall * 0.5),
    ):
        part.visual(
            Box((wall, depth, height - wall)),
            origin=Origin(xyz=(x, 0.0, (height + wall) * 0.5)),
            material=mats["shelf"],
            name=side,
            material_class_id="wood.oak",
        )
    for edge, y in (
        ("bin_front", -depth * 0.5 + wall * 0.5),
        ("bin_rear", depth * 0.5 - wall * 0.5),
    ):
        part.visual(
            Box((width - 2.0 * wall, wall, height - wall)),
            origin=Origin(xyz=(0.0, y, (height + wall) * 0.5)),
            material=mats["shelf"],
            name=edge,
            material_class_id="wood.oak",
        )
    part.visual(
        Box((width * 0.55, 0.009, 0.025)),
        origin=Origin(xyz=(0.0, -depth * 0.5 - 0.004, height * 0.62)),
        material=mats["edge"],
        name="front_pull_lip",
        material_class_id="wood.oak",
    )


def _add_wire_basket_geometry(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    width = r.insert_width_m - 0.012
    depth = r.shelf_depth_m * 0.82
    height = r.storage_height_m
    radius = 0.0038
    for index in range(6):
        x = -width * 0.42 + width * 0.84 * index / 5.0
        _rod(
            part,
            length=depth,
            radius=radius,
            axis="y",
            xyz=(x, 0.0, radius),
            material=mats["wire"],
            name=f"basket_floor_rod_{index}",
        )
    for index, y in enumerate((-depth * 0.44, 0.0, depth * 0.44)):
        _rod(
            part,
            length=width,
            radius=radius,
            axis="x",
            xyz=(0.0, y, radius),
            material=mats["wire"],
            name=f"basket_floor_cross_{index}",
        )
    for corner_index, (x, y) in enumerate(
        (
            (-width * 0.46, -depth * 0.46),
            (width * 0.46, -depth * 0.46),
            (-width * 0.46, depth * 0.46),
            (width * 0.46, depth * 0.46),
        )
    ):
        _rod(
            part,
            length=height,
            radius=radius * 1.2,
            axis="z",
            xyz=(x, y, height * 0.5),
            material=mats["wire"],
            name=f"basket_corner_post_{corner_index}",
        )
    for level_index, z in enumerate((height * 0.48, height)):
        for side_index, y in enumerate((-depth * 0.46, depth * 0.46)):
            _rod(
                part,
                length=width * 0.92,
                radius=radius * 1.15,
                axis="x",
                xyz=(0.0, y, z),
                material=mats["wire"],
                name=f"basket_side_rail_{level_index}_{side_index}",
            )
        for side_index, x in enumerate((-width * 0.46, width * 0.46)):
            _rod(
                part,
                length=depth * 0.92,
                radius=radius * 1.15,
                axis="y",
                xyz=(x, 0.0, z),
                material=mats["wire"],
                name=f"basket_end_rail_{level_index}_{side_index}",
            )


def _add_lid_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    depth: float,
    height: float,
) -> None:
    provider = AxisInterface(
        name=f"{name}_provider",
        point=(0.0, depth * 0.5, height),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
    )
    consumer = AxisInterface(
        name=f"{name}_consumer",
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=8.0,
            velocity=1.0,
            lower=-math.radians(30.0),
            upper=0.0,
        ),
    )
    register_interface_mate(model, name, mate)


def _add_storage(
    model: ArticulatedObject,
    frame,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    index: int,
) -> None:
    family = r.assembly_family
    style = (
        "lidded_drawer"
        if family in {"stepped_grid_lidded_drawers", "uniform_grid_slotted_shelves"}
        else "wire_basket"
        if family in {"stepped_grid_wire_baskets", "wall_rail_wire_shelves"}
        else "open_bin"
    )
    storage = model.part(
        f"assembly_family__{family}__storage_{index}",
        meta={"role": "storage_module", "style": style, "bay": index},
    )
    if style == "wire_basket":
        _add_wire_basket_geometry(storage, r, mats)
    else:
        _add_open_bin_geometry(storage, r, mats)
    model.articulation(
        f"assembly_family__{family}__pull_storage_{index}",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=storage,
        origin=Origin(
            xyz=(
                r.bay_centers_m[index],
                0.0,
                r.tube_m,
            )
        ),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=45.0,
            velocity=0.20,
            lower=0.0,
            upper=r.storage_travel_m,
        ),
        meta={"mechanism": "frame-guided lower storage pull-out"},
    )
    if style != "lidded_drawer":
        return
    depth = r.shelf_depth_m * 0.82
    width = r.insert_width_m - 0.012
    lid = model.part(
        f"assembly_family__{family}__storage_lid_{index}",
        meta={"role": "storage_lid", "bay": index},
    )
    lid.visual(
        Box((width, depth, 0.012)),
        # Rest 0.5 mm above the bin wall tops: a real clearance gap that
        # still sits inside the 1 mm supported-gap band, so the closed lid
        # neither intersects the drawer body nor floats unsupported.
        origin=Origin(xyz=(0.0, -depth * 0.5, 0.0065)),
        material=mats["shelf"],
        name="hinged_lid_panel",
        material_class_id="wood.oak",
    )
    _add_lid_joint(
        model,
        name=f"assembly_family__{family}__hinge_lid_{index}",
        parent=storage,
        child=lid,
        depth=depth,
        height=r.storage_height_m,
    )


def _populate_family(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
) -> ArticulatedObject:
    frame = _build_frame(model, r, mats)
    for index, (bay, level) in enumerate(r.cubby_layout):
        _add_cubby(
            model,
            frame,
            r,
            mats,
            index=index,
            bay=bay,
            level=level,
        )
    for index, (bay, level) in enumerate(r.shelf_placements):
        _add_shelf(
            model,
            frame,
            r,
            mats,
            index=index,
            bay=bay,
            level=level,
        )
    for index in range(r.storage_count):
        _add_storage(model, frame, r, mats, index=index)
    return model


def _assembly_family_stepped_grid_open_bins_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
) -> ArticulatedObject:
    return _populate_family(model, r, mats)


def _assembly_family_stepped_grid_lidded_drawers_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
) -> ArticulatedObject:
    return _populate_family(model, r, mats)


def _assembly_family_stepped_grid_wire_baskets_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
) -> ArticulatedObject:
    return _populate_family(model, r, mats)


def _assembly_family_open_ladder_solid_shelves_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
) -> ArticulatedObject:
    return _populate_family(model, r, mats)


def _assembly_family_uniform_grid_slotted_shelves_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
) -> ArticulatedObject:
    return _populate_family(model, r, mats)


def _assembly_family_wall_rail_wire_shelves_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
) -> ArticulatedObject:
    return _populate_family(model, r, mats)


_FAMILY_BUILDERS = {
    "stepped_grid_open_bins": _assembly_family_stepped_grid_open_bins_build,
    "stepped_grid_lidded_drawers": _assembly_family_stepped_grid_lidded_drawers_build,
    "stepped_grid_wire_baskets": _assembly_family_stepped_grid_wire_baskets_build,
    "open_ladder_solid_shelves": _assembly_family_open_ladder_solid_shelves_build,
    "uniform_grid_slotted_shelves": _assembly_family_uniform_grid_slotted_shelves_build,
    "wall_rail_wire_shelves": _assembly_family_wall_rail_wire_shelves_build,
}


def build_shelving_unit_with_adjustable_shelves(
    config: Config,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "shelving_unit_with_adjustable_shelves",
            "slot_choices": (
                ("assembly_family", r.assembly_family),
                ("bay_count", r.bay_count),
                ("level_count", r.level_count),
                ("shelf_count", r.shelf_count),
            ),
            "source_layout": "variable-bay high-left/low-right adjustable shelving",
        },
    )
    mats = _materials(model)
    return _FAMILY_BUILDERS[r.assembly_family](model, r, mats)


def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def run_shelving_unit_with_adjustable_shelves_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    frames = _parts_by_role(model, "load_bearing_frame")
    shelves = _parts_by_role(model, "adjustable_shelf")
    cubbies = _parts_by_role(model, "open_cubby")
    storage = _parts_by_role(model, "storage_module")
    lids = _parts_by_role(model, "storage_lid")
    frame = frames[0] if frames else None

    ctx.check(
        "category_anchor: source-like multi-bay shelving",
        len(frames) == 1
        and len(cubbies) == r.cubby_count
        and len(storage) == r.storage_count
        and frame is not None
        and frame.meta.get("bay_count") == r.bay_count,
        details=(
            f"frames={len(frames)}, cubbies={len(cubbies)}, "
            f"storage={len(storage)}, frame_meta={getattr(frame, 'meta', None)}"
        ),
    )
    shelf_joints = [
        joint for joint in model.articulations if joint.child in {part.name for part in shelves}
    ]
    ctx.check(
        "category_anchor: supported adjustable shelves",
        len(shelves) == r.shelf_count
        and len(shelf_joints) == r.shelf_count
        and all(part.meta.get("support_count") == 4 for part in shelves)
        and all(
            joint.parent == getattr(frame, "name", None)
            and joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(joint.axis) == (0.0, 0.0, 1.0)
            for joint in shelf_joints
        ),
        details=f"shelves={len(shelves)}, joints={[joint.name for joint in shelf_joints]}",
    )

    family_visuals = {visual.name or "" for part in model.parts for visual in part.visuals}
    identity = {
        "stepped_grid_open_bins": (
            any("tall_post" in name for name in family_visuals)
            and all(part.meta.get("style") == "open_bin" for part in storage)
        ),
        "stepped_grid_lidded_drawers": (
            len(lids) == r.storage_count
            and all(part.meta.get("style") == "lidded_drawer" for part in storage)
        ),
        "stepped_grid_wire_baskets": (
            any("basket_floor_rod" in name for name in family_visuals)
            and all(part.meta.get("style") == "wire_basket" for part in storage)
        ),
        "open_ladder_solid_shelves": (
            any("ladder_upright" in name for name in family_visuals)
            and any("ladder_rung" in name for name in family_visuals)
            and all(part.meta.get("deck") == "solid" for part in shelves)
        ),
        "uniform_grid_slotted_shelves": (
            any("uniform_post" in name for name in family_visuals)
            and any("slot_tab" in name for name in family_visuals)
            and any("slotted_rear_hook" in name for name in family_visuals)
        ),
        "wall_rail_wire_shelves": (
            any("wall_backplate" in name for name in family_visuals)
            and any("cantilever" in name for name in family_visuals)
            and all(part.meta.get("deck") == "wire" for part in shelves)
        ),
    }[r.assembly_family]
    ctx.check(
        f"category_anchor: {r.assembly_family} identity",
        identity,
        details=f"visual_count={len(family_visuals)}",
    )

    storage_joints = [
        joint for joint in model.articulations if joint.child in {part.name for part in storage}
    ]
    ctx.check(
        "six frame-guided lower storage modules",
        len(storage_joints) == r.storage_count
        and all(
            joint.parent == getattr(frame, "name", None)
            and joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(joint.axis) == (0.0, -1.0, 0.0)
            for joint in storage_joints
        ),
        details=(
            f"storage_count={r.storage_count}, "
            f"storage_joints={[joint.name for joint in storage_joints]}"
        ),
    )
    ctx.check(
        "grid multiplicity is applied to frame envelope",
        frame is not None
        and math.isclose(
            float(frame.meta.get("tall_levels", 0)),
            float(r.level_count),
            abs_tol=0.0,
        )
        and math.isclose(
            float(frame.meta.get("low_levels", 0)),
            float(r.low_level_count),
            abs_tol=0.0,
        ),
        details=f"frame_meta={getattr(frame, 'meta', None)}",
    )

    # Design-backed overlap policy forbids allow_overlap: cubby bottoms bear
    # flush on their welded bearing runners, shelf clips run beside the
    # support rails with a real 0.5 mm clearance gap, lids rest 0.5 mm above
    # the drawer wall tops, and storage modules ride on their bottom
    # runners, so no part pair needs an overlap allowance.
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "three_shelves_narrow_stepped_open_bins",
        {
            "assembly_family": "stepped_grid_open_bins",
            "shelf_count": 3,
            "bay_width_m": 0.34,
            "level_pitch_m": 0.34,
            "shelf_depth_m": 0.43,
        },
        reason="minimum N and bay dimensions with deepest solid inserts",
    ),
    corner_case(
        "seven_shelves_wall_rail_wire",
        {
            "assembly_family": "wall_rail_wire_shelves",
            "shelf_count": 7,
            "bay_width_m": 0.42,
            "level_pitch_m": 0.40,
            "shelf_depth_m": 0.43,
        },
        reason="maximum N and envelope on the cantilever wall family",
    ),
    corner_case(
        "seven_shelves_lidded_drawers",
        {
            "assembly_family": "stepped_grid_lidded_drawers",
            "shelf_count": 7,
            "bay_width_m": 0.34,
            "level_pitch_m": 0.40,
            "shelf_depth_m": 0.33,
        },
        reason="maximum shelf and hinge motion in the narrowest frame",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_shelving_unit_with_adjustable_shelves",
    "config_from_seed",
    "resolve_config",
    "run_shelving_unit_with_adjustable_shelves_tests",
]
