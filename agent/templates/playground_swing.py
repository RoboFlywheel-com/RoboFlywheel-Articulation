# SPDX-License-Identifier: Apache-2.0

"""Playground swing modular template.

Reviewed spec:
``articraft_template_authoring/specs_modular_v1/playground_swing.md``.

The category-level multiplicity is a wide playground frame carrying
``station_count`` independent swing stations. Each station samples a recipe
derived from the 5-star sample families: belt/plank, toddler bucket, tire,
lap-bar seat, platform, bench rocker, face-to-face glider, disc footrest, or
nest basket. Recipes may repeat or mix under one frame.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    Mimic,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireGroove,
    TireShoulder,
    TireSidewall,
    TireTread,
    TorusGeometry,
    mesh_from_geometry,
)

__modular__ = True


SupportFrameModule = Literal[
    "compact_a_frame_crossbeam",
    "tube_a_frame_with_clevises",
    "long_gantry_tire_frame",
    "multi_station_wide_frame",
    "minimal_top_beam_mount",
]
StationRecipe = Literal[
    "simple_belt_station",
    "bucket_station",
    "tire_station",
    "lap_bar_station",
    "platform_station",
    "bench_station",
    "glider_station",
    "swivel_disc_station",
    "nest_station",
]
PaletteTheme = Literal["park_green", "safety_red", "galvanized_blue", "mixed_bright"]


STATION_RECIPES: tuple[StationRecipe, ...] = (
    "simple_belt_station",
    "bucket_station",
    "tire_station",
    "lap_bar_station",
    "platform_station",
    "bench_station",
    "glider_station",
    "swivel_disc_station",
    "nest_station",
)

SUPPORT_FRAME_MODULES: tuple[SupportFrameModule, ...] = (
    "compact_a_frame_crossbeam",
    "tube_a_frame_with_clevises",
    "long_gantry_tire_frame",
    "multi_station_wide_frame",
    "minimal_top_beam_mount",
)

MINIMAL_MOUNT_RECIPES: tuple[StationRecipe, ...] = (
    "simple_belt_station",
    "swivel_disc_station",
)

COMPACT_FRAME_RECIPES: tuple[StationRecipe, ...] = (
    "simple_belt_station",
    "bucket_station",
    "lap_bar_station",
    "swivel_disc_station",
)

PALETTES: dict[PaletteTheme, dict[str, tuple[float, float, float, float]]] = {
    "park_green": {
        "frame": (0.20, 0.36, 0.23, 1.0),
        "frame_dark": (0.10, 0.16, 0.12, 1.0),
        "steel": (0.62, 0.65, 0.66, 1.0),
        "dark": (0.08, 0.085, 0.09, 1.0),
        "rubber": (0.035, 0.035, 0.035, 1.0),
        "seat": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.85, 0.10, 0.07, 1.0),
        "wood": (0.58, 0.39, 0.20, 1.0),
        "rope": (0.78, 0.62, 0.38, 1.0),
        "blue": (0.05, 0.25, 0.74, 1.0),
    },
    "safety_red": {
        "frame": (0.76, 0.08, 0.04, 1.0),
        "frame_dark": (0.32, 0.05, 0.03, 1.0),
        "steel": (0.70, 0.72, 0.73, 1.0),
        "dark": (0.09, 0.09, 0.10, 1.0),
        "rubber": (0.025, 0.025, 0.025, 1.0),
        "seat": (0.04, 0.18, 0.60, 1.0),
        "accent": (0.96, 0.70, 0.06, 1.0),
        "wood": (0.62, 0.42, 0.22, 1.0),
        "rope": (0.82, 0.66, 0.42, 1.0),
        "blue": (0.08, 0.30, 0.82, 1.0),
    },
    "galvanized_blue": {
        "frame": (0.08, 0.28, 0.68, 1.0),
        "frame_dark": (0.03, 0.08, 0.18, 1.0),
        "steel": (0.64, 0.67, 0.68, 1.0),
        "dark": (0.10, 0.11, 0.12, 1.0),
        "rubber": (0.030, 0.030, 0.030, 1.0),
        "seat": (0.11, 0.11, 0.12, 1.0),
        "accent": (0.96, 0.68, 0.08, 1.0),
        "wood": (0.55, 0.38, 0.20, 1.0),
        "rope": (0.76, 0.61, 0.39, 1.0),
        "blue": (0.03, 0.22, 0.78, 1.0),
    },
    "mixed_bright": {
        "frame": (0.92, 0.55, 0.08, 1.0),
        "frame_dark": (0.34, 0.22, 0.04, 1.0),
        "steel": (0.63, 0.65, 0.66, 1.0),
        "dark": (0.09, 0.09, 0.10, 1.0),
        "rubber": (0.030, 0.030, 0.030, 1.0),
        "seat": (0.04, 0.38, 0.44, 1.0),
        "accent": (0.82, 0.08, 0.04, 1.0),
        "wood": (0.60, 0.40, 0.18, 1.0),
        "rope": (0.82, 0.66, 0.42, 1.0),
        "blue": (0.05, 0.24, 0.78, 1.0),
    },
}

RECIPE_FOOTPRINTS: dict[StationRecipe, float] = {
    "simple_belt_station": 0.62,
    "bucket_station": 0.68,
    "tire_station": 0.92,
    "lap_bar_station": 0.72,
    "platform_station": 1.00,
    "bench_station": 1.38,
    "glider_station": 1.46,
    "swivel_disc_station": 0.58,
    "nest_station": 1.24,
}


@dataclass(frozen=True)
class StationParams:
    recipe: StationRecipe
    footprint: float
    scale: float
    drop: float
    width: float
    depth: float
    radius: float
    hanger_half_width: float
    hub_length: float


@dataclass(frozen=True)
class PlaygroundSwingConfig:
    support_frame_module: SupportFrameModule = "compact_a_frame_crossbeam"
    station_count: int = 1
    station_recipes: tuple[StationRecipe, ...] | None = None
    palette_theme: PaletteTheme = "park_green"
    top_z: float = 2.20
    station_spacing: float = 0.18
    end_clearance: float = 0.32
    swing_limit: float = 0.62
    station_size_scale: float = 1.0
    station_drop_scale: float = 1.0
    geometry_seed: int = 0
    name: str = "playground_swing"
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["park_green"])
    )


@dataclass(frozen=True)
class ResolvedPlaygroundSwingConfig:
    support_frame_module: SupportFrameModule
    station_count: int
    station_recipes: tuple[StationRecipe, ...]
    palette_theme: PaletteTheme
    top_z: float
    beam_length: float
    station_centers: tuple[float, ...]
    station_params: tuple[StationParams, ...]
    swing_limit: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _validate_recipe(name: str) -> StationRecipe:
    if name not in STATION_RECIPES:
        raise ValueError(f"Unknown playground swing station recipe: {name!r}")
    return name  # type: ignore[return-value]


def _frame_capacity(frame: SupportFrameModule) -> int:
    if frame in ("compact_a_frame_crossbeam", "minimal_top_beam_mount"):
        return 1
    if frame == "tube_a_frame_with_clevises":
        return 2
    return 5


def _allowed_recipes_for_frame(frame: SupportFrameModule) -> tuple[StationRecipe, ...]:
    if frame == "minimal_top_beam_mount":
        return MINIMAL_MOUNT_RECIPES
    if frame == "compact_a_frame_crossbeam":
        return COMPACT_FRAME_RECIPES
    return STATION_RECIPES


def _recipe_sequence_for_seed(
    seed: int,
    *,
    frame: SupportFrameModule = "multi_station_wide_frame",
) -> tuple[StationRecipe, ...]:
    if seed == 0:
        return ("simple_belt_station",)
    rng = random.Random(seed)
    station_count = rng.randint(1, _frame_capacity(frame))
    allowed_recipes = _allowed_recipes_for_frame(frame)
    recipes: list[StationRecipe] = []
    for index in range(station_count):
        if index == 0 and station_count >= 4:
            # Force at least one compact bay when the beam is very crowded.
            pool = tuple(
                recipe
                for recipe in ("simple_belt_station", "bucket_station", "swivel_disc_station")
                if recipe in allowed_recipes
            )
        else:
            pool = allowed_recipes
        recipes.append(rng.choice(pool))
    return tuple(recipes)


def config_from_seed(seed: int) -> PlaygroundSwingConfig:
    if seed == 0:
        return PlaygroundSwingConfig(
            support_frame_module="compact_a_frame_crossbeam",
            station_count=1,
            station_recipes=("simple_belt_station",),
            palette_theme="park_green",
            name="playground_swing_anchor_seed_0",
        )
    rng = random.Random(seed * 7919 + 17)
    support_frame_module = rng.choice(SUPPORT_FRAME_MODULES)
    recipes = _recipe_sequence_for_seed(seed, frame=support_frame_module)
    palette_theme = rng.choice(tuple(PALETTES.keys()))
    return PlaygroundSwingConfig(
        support_frame_module=support_frame_module,
        station_count=len(recipes),
        station_recipes=recipes,
        palette_theme=palette_theme,
        swing_limit=rng.uniform(0.48, 0.72),
        station_size_scale=round(rng.uniform(0.88, 1.16), 4),
        station_drop_scale=round(rng.uniform(0.92, 1.10), 4),
        geometry_seed=seed,
        name=f"seeded_playground_swing_{seed}",
    )


def _resolve_station_params(
    recipe: StationRecipe,
    *,
    rng: random.Random,
    top_z: float,
    size_scale: float = 1.0,
    drop_scale: float = 1.0,
) -> StationParams:
    scale = rng.uniform(0.88, 1.16) * size_scale
    width_jitter = rng.uniform(0.94, 1.12) * size_scale
    depth_jitter = rng.uniform(0.92, 1.10) * size_scale
    drop_jitter = rng.uniform(0.94, 1.08) * drop_scale

    base = RECIPE_FOOTPRINTS[recipe]
    width = base * width_jitter
    depth = 0.36 * depth_jitter
    radius = 0.20 * scale
    hanger_half_width = 0.22 * scale
    hub_length = 0.42 * scale
    drop = 1.20 * drop_jitter

    if recipe == "simple_belt_station":
        width = 0.54 * width_jitter
        depth = 0.24 * depth_jitter
        hanger_half_width = _clamp(width * 0.38, 0.18, 0.26)
        hub_length = _clamp(width * 0.82, 0.36, 0.52)
        drop = 1.42 * drop_jitter
        footprint = max(0.58, width + 0.16)
    elif recipe == "bucket_station":
        width = 0.54 * width_jitter
        depth = 0.44 * depth_jitter
        hanger_half_width = _clamp(width * 0.42, 0.20, 0.29)
        hub_length = _clamp(width * 0.82, 0.38, 0.54)
        drop = 1.28 * drop_jitter
        footprint = max(0.64, width + 0.20)
    elif recipe == "tire_station":
        radius = 0.36 * scale
        depth = 0.14 * depth_jitter
        width = radius * 2.0
        hanger_half_width = _clamp(radius * 0.72, 0.22, 0.32)
        hub_length = _clamp(radius * 1.56, 0.50, 0.68)
        drop = 1.14 * drop_jitter
        footprint = max(0.84, radius * 2.0 + 0.22)
    elif recipe == "lap_bar_station":
        width = 0.56 * width_jitter
        depth = 0.35 * depth_jitter
        hanger_half_width = _clamp(width * 0.43, 0.22, 0.30)
        hub_length = _clamp(width * 0.80, 0.38, 0.56)
        drop = 1.06 * drop_jitter
        footprint = max(0.68, width + 0.20)
    elif recipe == "platform_station":
        width = 0.82 * width_jitter
        depth = 0.70 * depth_jitter
        hanger_half_width = _clamp(width * 0.39, 0.28, 0.42)
        hub_length = _clamp(width * 0.86, 0.64, 0.88)
        drop = 1.18 * drop_jitter
        footprint = max(0.92, width + 0.22)
    elif recipe == "bench_station":
        width = 1.06 * width_jitter
        depth = 0.48 * depth_jitter
        hanger_half_width = _clamp(width * 0.40, 0.38, 0.52)
        hub_length = _clamp(width * 0.74, 0.72, 0.96)
        drop = 1.14 * drop_jitter
        footprint = max(1.22, width + 0.30)
    elif recipe == "glider_station":
        width = 1.02 * width_jitter
        depth = 0.86 * depth_jitter
        hanger_half_width = _clamp(width * 0.45, 0.42, 0.58)
        hub_length = _clamp(width * 0.88, 0.88, 1.12)
        drop = 1.14 * drop_jitter
        footprint = max(1.34, width + 0.40)
    elif recipe == "swivel_disc_station":
        radius = 0.20 * scale
        width = radius * 2.0
        depth = radius * 2.0
        hanger_half_width = 0.0
        hub_length = _clamp(radius * 1.2, 0.22, 0.30)
        drop = 0.58 * drop_jitter
        footprint = max(0.52, radius * 2.0 + 0.16)
    elif recipe == "nest_station":
        radius = 0.48 * scale
        width = radius * 2.0
        depth = radius * 2.0
        hanger_half_width = _clamp(radius * 0.72, 0.32, 0.43)
        hub_length = _clamp(radius * 1.72, 0.78, 1.00)
        drop = 1.18 * drop_jitter
        footprint = max(1.10, radius * 2.0 + 0.26)
    else:  # pragma: no cover - validated earlier.
        footprint = base

    max_drop = max(0.55, top_z - 0.58)
    drop = _clamp(drop, 0.52, max_drop)
    footprint = max(footprint, hub_length + 0.16)
    return StationParams(
        recipe=recipe,
        footprint=footprint,
        scale=scale,
        drop=drop,
        width=width,
        depth=depth,
        radius=radius,
        hanger_half_width=hanger_half_width,
        hub_length=hub_length,
    )


def resolve_config(config: PlaygroundSwingConfig) -> ResolvedPlaygroundSwingConfig:
    station_count = max(1, min(5, int(config.station_count)))
    if config.station_recipes:
        recipes = tuple(_validate_recipe(str(recipe)) for recipe in config.station_recipes)
        if len(recipes) != station_count:
            station_count = len(recipes)
    else:
        recipes = ("simple_belt_station",) * station_count

    if config.support_frame_module not in SUPPORT_FRAME_MODULES:
        support_frame_module: SupportFrameModule = "multi_station_wide_frame"
    else:
        support_frame_module = config.support_frame_module
    station_count = min(station_count, _frame_capacity(support_frame_module))
    allowed_recipes = _allowed_recipes_for_frame(support_frame_module)
    recipes = tuple(
        recipe if recipe in allowed_recipes else allowed_recipes[0] for recipe in recipes
    )
    recipes = recipes[:station_count] or (allowed_recipes[0],)
    station_count = len(recipes)

    top_z = _clamp(config.top_z, 1.85, 2.45)
    spacing = _clamp(config.station_spacing, 0.12, 0.32)
    end_clearance = _clamp(config.end_clearance, 0.22, 0.55)
    size_scale = _clamp(config.station_size_scale, 0.85, 1.25)
    drop_scale = _clamp(config.station_drop_scale, 0.90, 1.15)
    param_rng = random.Random(int(config.geometry_seed) * 104729 + 3011)
    station_params = tuple(
        _resolve_station_params(
            recipe, rng=param_rng, top_z=top_z, size_scale=size_scale, drop_scale=drop_scale
        )
        for recipe in recipes
    )
    footprints = [params.footprint for params in station_params]
    beam_length = max(
        1.40, sum(footprints) + spacing * max(0, station_count - 1) + end_clearance * 2.0
    )

    centers: list[float] = []
    cursor = -beam_length / 2.0 + end_clearance
    for footprint in footprints:
        center = cursor + footprint / 2.0
        centers.append(center)
        cursor += footprint + spacing

    palette_theme = config.palette_theme if config.palette_theme in PALETTES else "park_green"
    palette = dict(PALETTES[palette_theme])
    palette.update(config.palette or {})

    return ResolvedPlaygroundSwingConfig(
        support_frame_module=support_frame_module,
        station_count=station_count,
        station_recipes=recipes,
        palette_theme=palette_theme,
        top_z=top_z,
        beam_length=beam_length,
        station_centers=tuple(centers),
        station_params=station_params,
        swing_limit=_clamp(config.swing_limit, 0.35, 0.85),
        name=config.name,
        palette=palette,
    )


def _segment_pose(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
) -> tuple[Origin, float]:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 1e-9:
        return Origin(xyz=start), 0.0
    yaw = math.atan2(dy, dx)
    pitch = math.acos(max(-1.0, min(1.0, dz / length)))
    return (
        Origin(
            xyz=((start[0] + end[0]) * 0.5, (start[1] + end[1]) * 0.5, (start[2] + end[2]) * 0.5),
            rpy=(0.0, pitch, yaw),
        ),
        length,
    )


def _add_tube(part, name: str, start, end, radius: float, material) -> None:
    origin, length = _segment_pose(start, end)
    part.visual(Cylinder(radius=radius, length=length), origin=origin, material=material, name=name, material_class_id="metal.paint_coated")


def _mat(model: ArticulatedObject, key: str, rgba: tuple[float, float, float, float]):
    return model.material(key, rgba=rgba)


def _build_frame(model: ArticulatedObject, r: ResolvedPlaygroundSwingConfig) -> None:
    frame_mat = _mat(model, "frame_powder_coat", r.palette["frame"])
    frame_dark = _mat(model, "frame_dark_brace", r.palette["frame_dark"])
    steel = _mat(model, "galvanized_pivot_steel", r.palette["steel"])

    frame = model.part("frame")
    frame.inertial = Inertial.from_geometry(
        Box((r.beam_length, 1.65, r.top_z + 0.12)),
        mass=75.0 + 18.0 * r.station_count,
        origin=Origin(xyz=(0.0, 0.0, (r.top_z + 0.12) * 0.5)),
    )

    if r.support_frame_module == "minimal_top_beam_mount":
        frame.visual(
            Box((r.beam_length + 0.46, 0.24, 0.16)),
            origin=Origin(xyz=(0.0, 0.0, r.top_z + 0.03)),
            material=frame_mat,
            name="timber_overhead_beam", material_class_id="wood.painted_clean",
        )
        frame.visual(
            Box((r.beam_length + 0.30, 0.30, 0.035)),
            origin=Origin(xyz=(0.0, 0.0, r.top_z + 0.125)),
            material=frame_dark,
            name="ceiling_mount_plate", material_class_id="metal.paint_coated",
        )
        for bx in (-r.beam_length * 0.38, r.beam_length * 0.38):
            frame.visual(
                Cylinder(radius=0.018, length=0.18),
                origin=Origin(xyz=(bx, -0.08, r.top_z + 0.15)),
                material=steel,
                name=f"mount_bolt_front_{bx:+.2f}", material_class_id="metal.steel_galvanized",
            )
            frame.visual(
                Cylinder(radius=0.018, length=0.18),
                origin=Origin(xyz=(bx, 0.08, r.top_z + 0.15)),
                material=steel,
                name=f"mount_bolt_rear_{bx:+.2f}", material_class_id="metal.steel_galvanized",
            )
    elif r.support_frame_module == "tube_a_frame_with_clevises":
        _add_tube(
            frame,
            "round_tube_top_beam",
            (-r.beam_length / 2.0, 0.0, r.top_z),
            (r.beam_length / 2.0, 0.0, r.top_z),
            0.050,
            frame_mat,
        )
        frame.visual(
            Box((r.beam_length + 0.10, 0.040, 0.050)),
            origin=Origin(xyz=(0.0, -0.07, r.top_z - 0.18)),
            material=frame_dark,
            name="front_tube_spreader", material_class_id="metal.paint_coated",
        )
        frame.visual(
            Box((r.beam_length + 0.10, 0.040, 0.050)),
            origin=Origin(xyz=(0.0, 0.07, r.top_z - 0.18)),
            material=frame_dark,
            name="rear_tube_spreader", material_class_id="metal.paint_coated",
        )
    elif r.support_frame_module == "long_gantry_tire_frame":
        _add_tube(
            frame,
            "heavy_gantry_top_beam",
            (-r.beam_length / 2.0, 0.0, r.top_z),
            (r.beam_length / 2.0, 0.0, r.top_z),
            0.065,
            frame_mat,
        )
        frame.visual(
            Box((r.beam_length + 0.28, 0.070, 0.045)),
            origin=Origin(xyz=(0.0, -0.82, 0.055)),
            material=frame_dark,
            name="front_ground_skid", material_class_id="metal.paint_coated",
        )
        frame.visual(
            Box((r.beam_length + 0.28, 0.070, 0.045)),
            origin=Origin(xyz=(0.0, 0.82, 0.055)),
            material=frame_dark,
            name="rear_ground_skid", material_class_id="metal.paint_coated",
        )
        frame.visual(
            Box((r.beam_length + 0.18, 0.050, 0.050)),
            origin=Origin(xyz=(0.0, -0.82, r.top_z - 0.30)),
            material=frame_dark,
            name="front_upper_side_rail", material_class_id="metal.paint_coated",
        )
        frame.visual(
            Box((r.beam_length + 0.18, 0.050, 0.050)),
            origin=Origin(xyz=(0.0, 0.82, r.top_z - 0.30)),
            material=frame_dark,
            name="rear_upper_side_rail", material_class_id="metal.paint_coated",
        )
    else:
        _add_tube(
            frame,
            "top_beam",
            (-r.beam_length / 2.0, 0.0, r.top_z),
            (r.beam_length / 2.0, 0.0, r.top_z),
            0.055,
            frame_mat,
        )

    support_xs: list[float] = []
    if r.support_frame_module != "minimal_top_beam_mount":
        support_xs = [-r.beam_length / 2.0 + 0.18, r.beam_length / 2.0 - 0.18]
    if r.station_count >= 4 and r.support_frame_module in (
        "long_gantry_tire_frame",
        "multi_station_wide_frame",
    ):
        gap_index = max(1, r.station_count // 2)
        center_support_x = (r.station_centers[gap_index - 1] + r.station_centers[gap_index]) * 0.5
        support_xs.insert(1, center_support_x)
    elif r.station_count == 3 and r.support_frame_module == "multi_station_wide_frame":
        frame.visual(
            Box((r.beam_length - 0.40, 0.050, 0.045)),
            origin=Origin(xyz=(0.0, -0.07, r.top_z - 0.20)),
            material=frame_dark,
            name="long_front_upper_brace", material_class_id="metal.paint_coated",
        )
        frame.visual(
            Box((r.beam_length - 0.40, 0.050, 0.045)),
            origin=Origin(xyz=(0.0, 0.07, r.top_z - 0.20)),
            material=frame_dark,
            name="long_rear_upper_brace", material_class_id="metal.paint_coated",
        )

    for idx, x in enumerate(support_xs):
        foot_y = 0.86 if r.support_frame_module == "long_gantry_tire_frame" else 0.76
        leg_radius = 0.045 if r.support_frame_module == "long_gantry_tire_frame" else 0.040
        if r.support_frame_module == "long_gantry_tire_frame":
            front_base = (x, -foot_y, 0.06)
            rear_base = (x, foot_y, 0.06)
            front_top = (x, -foot_y, r.top_z - 0.01)
            rear_top = (x, foot_y, r.top_z - 0.01)
            _add_tube(
                frame, f"portal_{idx}_front_upright", front_base, front_top, leg_radius, frame_mat
            )
            _add_tube(
                frame, f"portal_{idx}_rear_upright", rear_base, rear_top, leg_radius, frame_mat
            )
            _add_tube(frame, f"portal_{idx}_top_crossmember", front_top, rear_top, 0.038, frame_mat)
            _add_tube(
                frame,
                f"portal_{idx}_mid_crossmember",
                (x, -foot_y, 1.05),
                (x, foot_y, 1.05),
                0.026,
                frame_dark,
            )
            _add_tube(
                frame,
                f"portal_{idx}_front_knee_brace",
                (x, -foot_y, r.top_z - 0.34),
                (x, -foot_y * 0.45, r.top_z - 0.01),
                0.024,
                frame_dark,
            )
            _add_tube(
                frame,
                f"portal_{idx}_rear_knee_brace",
                (x, foot_y, r.top_z - 0.34),
                (x, foot_y * 0.45, r.top_z - 0.01),
                0.024,
                frame_dark,
            )
            continue

        top = (x, 0.0, r.top_z - 0.01)
        front_foot = (x, foot_y, 0.06)
        rear_foot = (x, -foot_y, 0.06)
        _add_tube(frame, f"support_{idx}_front_leg", top, front_foot, leg_radius, frame_mat)
        _add_tube(frame, f"support_{idx}_rear_leg", top, rear_foot, leg_radius, frame_mat)
        _add_tube(
            frame,
            f"support_{idx}_foot_bar",
            (x, -foot_y - 0.08, 0.055),
            (x, foot_y + 0.08, 0.055),
            0.030,
            frame_dark,
        )
        _add_tube(
            frame,
            f"support_{idx}_mid_brace",
            (x, -foot_y * 0.70, 1.12),
            (x, foot_y * 0.70, 1.12),
            0.024,
            frame_dark,
        )
        if r.support_frame_module == "tube_a_frame_with_clevises":
            _add_tube(
                frame,
                f"support_{idx}_upper_cross_tie",
                (x, -foot_y * 0.42, r.top_z - 0.32),
                (x, foot_y * 0.42, r.top_z - 0.32),
                0.022,
                steel,
            )
        elif r.support_frame_module == "long_gantry_tire_frame":
            _add_tube(
                frame,
                f"support_{idx}_diagonal_front_brace",
                (x, -foot_y, 0.10),
                (x, 0.0, r.top_z - 0.32),
                0.024,
                frame_dark,
            )
            _add_tube(
                frame,
                f"support_{idx}_diagonal_rear_brace",
                (x, foot_y, 0.10),
                (x, 0.0, r.top_z - 0.32),
                0.024,
                frame_dark,
            )

    for index, x in enumerate(r.station_centers):
        # Visible bay hardware adapted from the dual-bay 5-star frame: two
        # cheek plates and a pin below the top beam for every station.
        frame.visual(
            Box((0.090, 0.036, 0.135)),
            origin=Origin(xyz=(x, -0.075, r.top_z - 0.105)),
            material=frame_mat,
            name=f"station_{index}_front_clevis_cheek", material_class_id="metal.paint_coated",
        )
        frame.visual(
            Box((0.090, 0.036, 0.135)),
            origin=Origin(xyz=(x, 0.075, r.top_z - 0.105)),
            material=frame_mat,
            name=f"station_{index}_rear_clevis_cheek", material_class_id="metal.paint_coated",
        )
        _add_tube(
            frame,
            f"station_{index}_pivot_pin",
            (x - 0.18, 0.0, r.top_z - 0.125),
            (x + 0.18, 0.0, r.top_z - 0.125),
            0.018,
            steel,
        )
        frame.visual(
            Box((0.12, 0.16, 0.040)),
            origin=Origin(xyz=(x, 0.0, r.top_z - 0.055)),
            material=frame_dark,
            name=f"station_{index}_hanger_block", material_class_id="metal.paint_coated",
        )
        frame.visual(
            Box((0.13, 0.12, 0.075)),
            origin=Origin(xyz=(x, 0.0, r.top_z - 0.118)),
            material=frame_dark,
            name=f"station_{index}_pivot_saddle", material_class_id="metal.paint_coated",
        )


def _motion(r: ResolvedPlaygroundSwingConfig, effort: float = 90.0) -> MotionLimits:
    return MotionLimits(effort=effort, velocity=1.8, lower=-r.swing_limit, upper=r.swing_limit)


def _add_top_hub(part, prefix: str, material, *, length: float = 0.42) -> None:
    part.visual(
        Cylinder(radius=0.030, length=length),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=f"{prefix}_upper_hub", material_class_id="metal.steel_galvanized",
    )
    part.visual(
        Box((length + 0.10, 0.070, 0.055)),
        origin=Origin(xyz=(0.0, 0.0, -0.034)),
        material=material,
        name=f"{prefix}_upper_yoke_web", material_class_id="metal.steel_galvanized",
    )


def _add_belt_station(
    model: ArticulatedObject,
    r: ResolvedPlaygroundSwingConfig,
    index: int,
    x: float,
    p: StationParams,
) -> None:
    steel = _mat(model, f"station_{index}_steel", r.palette["steel"])
    dark = _mat(model, f"station_{index}_dark", r.palette["dark"])
    seat_mat = _mat(model, f"station_{index}_seat", r.palette["seat"])
    swing = model.part(f"station_{index}_swing")
    _add_top_hub(swing, f"station_{index}", steel, length=p.hub_length)
    drop = p.drop
    for side, sx in (("left", -p.hanger_half_width), ("right", p.hanger_half_width)):
        _add_tube(
            swing,
            f"{side}_front_chain",
            (sx, 0.025, -0.030),
            (sx * 0.72, p.depth * 0.42, -drop + 0.03),
            0.009,
            steel,
        )
        _add_tube(
            swing,
            f"{side}_rear_chain",
            (sx, -0.025, -0.030),
            (sx * 0.72, -p.depth * 0.42, -drop + 0.03),
            0.009,
            steel,
        )
        swing.visual(
            Box((0.060, p.depth * 0.92, 0.070)),
            origin=Origin(xyz=(sx * 0.72, 0.0, -drop)),
            material=dark,
            name=f"{side}_seat_bracket", material_class_id="metal.paint_coated",
        )
    swing.visual(
        Box((p.width, p.depth, 0.040)),
        origin=Origin(xyz=(0.0, 0.0, -drop - 0.03)),
        material=seat_mat,
        name="belt_seat", material_class_id="rubber.smooth_plain",
    )
    swing.visual(
        Box((p.width * 0.85, p.depth * 0.82, 0.015)),
        origin=Origin(xyz=(0.0, 0.0, -drop - 0.005)),
        material=dark,
        name="seat_pad", material_class_id="rubber.sponge_foam",
    )
    model.articulation(
        f"station_{index}_frame_to_swing",
        ArticulationType.REVOLUTE,
        parent="frame",
        child=swing,
        origin=Origin(xyz=(x, 0.0, r.top_z - 0.125)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=_motion(r),
    )


def _add_bucket_station(
    model: ArticulatedObject,
    r: ResolvedPlaygroundSwingConfig,
    index: int,
    x: float,
    p: StationParams,
) -> None:
    steel = _mat(model, f"station_{index}_steel", r.palette["steel"])
    shell_mat = _mat(model, f"station_{index}_bucket_shell", r.palette["accent"])
    strap_mat = _mat(model, f"station_{index}_strap", r.palette["dark"])
    dark = _mat(model, f"station_{index}_bucket_shadow", r.palette["dark"])
    swing = model.part(f"station_{index}_bucket")
    _add_top_hub(swing, f"station_{index}", steel, length=p.hub_length)
    drop = p.drop
    for sx in (-p.hanger_half_width, p.hanger_half_width):
        _add_tube(
            swing,
            f"side_strap_{sx:+.1f}",
            (sx, 0.0, -0.02),
            (sx * 0.88, 0.0, -drop + p.depth * 0.41),
            0.015,
            strap_mat,
        )
        swing.visual(
            Sphere(radius=0.038),
            origin=Origin(xyz=(sx * 0.88, 0.0, -drop + p.depth * 0.36)),
            material=steel,
            name=f"side_bolt_{sx:+.1f}", material_class_id="metal.steel_galvanized",
        )
    swing.visual(
        Box((p.width, p.depth, 0.34 * p.scale)),
        origin=Origin(xyz=(0.0, 0.0, -drop)),
        material=shell_mat,
        name="bucket_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    swing.visual(
        Box((p.width * 0.40, 0.05, 0.13 * p.scale)),
        origin=Origin(xyz=(-p.width * 0.22, p.depth * 0.545, -drop - 0.02)),
        material=dark,
        name="left_leg_opening_shadow", material_class_id="plastic.opaque_glossy_molded",
    )
    swing.visual(
        Box((p.width * 0.40, 0.05, 0.13 * p.scale)),
        origin=Origin(xyz=(p.width * 0.22, p.depth * 0.545, -drop - 0.02)),
        material=dark,
        name="right_leg_opening_shadow", material_class_id="plastic.opaque_glossy_molded",
    )
    swing.visual(
        Box((p.width + 0.04, 0.055, 0.060)),
        origin=Origin(xyz=(0.0, p.depth * 0.50, -drop + 0.10)),
        material=steel,
        name="front_rim", material_class_id="metal.steel_galvanized",
    )
    swing.visual(
        Box((p.width + 0.04, 0.055, 0.060)),
        origin=Origin(xyz=(0.0, -p.depth * 0.50, -drop + 0.10)),
        material=steel,
        name="rear_rim", material_class_id="metal.steel_galvanized",
    )
    model.articulation(
        f"station_{index}_frame_to_bucket",
        ArticulationType.REVOLUTE,
        parent="frame",
        child=swing,
        origin=Origin(xyz=(x, 0.0, r.top_z - 0.125)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=_motion(r, effort=110.0),
    )


def _add_tire_station(
    model: ArticulatedObject,
    r: ResolvedPlaygroundSwingConfig,
    index: int,
    x: float,
    p: StationParams,
) -> None:
    steel = _mat(model, f"station_{index}_steel", r.palette["steel"])
    rubber = _mat(model, f"station_{index}_rubber", r.palette["rubber"])
    accent = _mat(model, f"station_{index}_accent", r.palette["accent"])
    swing = model.part(f"station_{index}_tire")
    _add_top_hub(swing, f"station_{index}", steel, length=p.hub_length)
    tire_z = -(p.drop + p.radius * 0.22)
    tire = TireGeometry(
        p.radius,
        p.depth,
        inner_radius=p.radius * 0.56,
        carcass=TireCarcass(belt_width_ratio=0.72, sidewall_bulge=0.08),
        tread=TireTread(style="block", depth=0.010, count=24, land_ratio=0.55),
        grooves=(TireGroove(center_offset=0.0, width=0.018, depth=0.004),),
        sidewall=TireSidewall(style="rounded", bulge=0.06),
        shoulder=TireShoulder(width=0.016, radius=0.005),
    )
    swing.visual(
        mesh_from_geometry(tire, f"station_{index}_tire_mesh"),
        origin=Origin(xyz=(0.0, 0.0, tire_z), rpy=(0.0, -math.pi / 2.0, 0.0)),
        material=rubber,
        name="tire_shell", material_class_id="rubber.directional_grooved",
    )
    swing.visual(
        Box((p.radius * 1.78, p.radius * 1.78, 0.070)),
        origin=Origin(xyz=(0.0, 0.0, -p.drop)),
        material=steel,
        name="tire_anchor_spider_plate", material_class_id="metal.steel_galvanized",
    )
    for name, top, bottom in (
        (
            "left",
            (-p.hanger_half_width, 0.0, -0.055),
            (-p.radius * 0.67, -p.radius * 0.47, -p.drop),
        ),
        ("center", (0.0, 0.0, -0.055), (0.0, p.radius * 0.81, -p.drop)),
        ("right", (p.hanger_half_width, 0.0, -0.055), (p.radius * 0.67, -p.radius * 0.47, -p.drop)),
    ):
        _add_tube(swing, f"{name}_hanger", top, bottom, 0.016, steel)
        swing.visual(
            Sphere(radius=0.040),
            origin=Origin(xyz=bottom),
            material=accent,
            name=f"{name}_tire_clamp", material_class_id="metal.paint_coated",
        )
        _add_tube(
            swing,
            f"{name}_tire_anchor_pin",
            bottom,
            (bottom[0], bottom[1], tire_z - p.radius * 0.07),
            0.020,
            steel,
        )
    model.articulation(
        f"station_{index}_frame_to_tire",
        ArticulationType.REVOLUTE,
        parent="frame",
        child=swing,
        origin=Origin(xyz=(x, 0.0, r.top_z - 0.125)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=_motion(r, effort=130.0),
    )


def _add_lap_bar_station(
    model: ArticulatedObject,
    r: ResolvedPlaygroundSwingConfig,
    index: int,
    x: float,
    p: StationParams,
) -> None:
    steel = _mat(model, f"station_{index}_steel", r.palette["steel"])
    wood = _mat(model, f"station_{index}_wood", r.palette["wood"])
    red = _mat(model, f"station_{index}_red", r.palette["accent"])
    seat = model.part(f"station_{index}_slatted_seat")
    _add_top_hub(seat, f"station_{index}", steel, length=p.hub_length)
    drop = p.drop
    for sx in (-p.hanger_half_width, p.hanger_half_width):
        _add_tube(
            seat, f"hanger_{sx:+.1f}", (sx, 0.0, -0.02), (sx, 0.0, -drop + 0.01), 0.014, steel
        )
    seat.visual(
        Box((p.width, p.depth, 0.065)),
        origin=Origin(xyz=(0.0, 0.0, -drop)),
        material=steel,
        name="seat_frame", material_class_id="metal.steel_galvanized",
    )
    slat_ys = (-p.depth * 0.37, -p.depth * 0.12, p.depth * 0.14, p.depth * 0.40)
    for j, yy in enumerate(slat_ys):
        seat.visual(
            Box((p.width * 0.89, p.depth * 0.16, 0.030)),
            origin=Origin(xyz=(0.0, yy, -drop + 0.035)),
            material=wood,
            name=f"seat_slat_{j}", material_class_id="wood.natural_generic",
        )
    seat.visual(
        Box((p.width * 0.86, p.depth * 0.23, 0.130)),
        origin=Origin(xyz=(0.0, p.depth * 0.51, -drop + 0.035)),
        material=steel,
        name="lap_hinge_socket", material_class_id="metal.steel_galvanized",
    )
    model.articulation(
        f"station_{index}_frame_to_slatted_seat",
        ArticulationType.REVOLUTE,
        parent="frame",
        child=seat,
        origin=Origin(xyz=(x, 0.0, r.top_z - 0.125)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=_motion(r),
    )
    lap = model.part(f"station_{index}_lap_bar")
    lap_width = p.width * 0.90
    lap_y = p.depth * 0.51
    lap.visual(
        Cylinder(radius=0.018, length=lap_width),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=red,
        name="lap_bar_hinge", material_class_id="metal.paint_coated",
    )
    _add_tube(
        lap,
        "left_bar_arm",
        (-lap_width * 0.40, 0.0, 0.0),
        (-lap_width * 0.40, lap_y, 0.14),
        0.012,
        red,
    )
    _add_tube(
        lap,
        "right_bar_arm",
        (lap_width * 0.40, 0.0, 0.0),
        (lap_width * 0.40, lap_y, 0.14),
        0.012,
        red,
    )
    lap.visual(
        Cylinder(radius=0.014, length=lap_width * 0.88),
        origin=Origin(xyz=(0.0, lap_y, 0.14), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=red,
        name="front_guard", material_class_id="metal.paint_coated",
    )
    model.articulation(
        f"station_{index}_seat_to_lap_bar",
        ArticulationType.REVOLUTE,
        parent=seat,
        child=lap,
        origin=Origin(xyz=(0.0, p.depth * 0.57, -drop + 0.11)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=1.5, lower=0.0, upper=1.15),
    )


def _add_platform_station(
    model: ArticulatedObject,
    r: ResolvedPlaygroundSwingConfig,
    index: int,
    x: float,
    p: StationParams,
) -> None:
    steel = _mat(model, f"station_{index}_steel", r.palette["steel"])
    dark = _mat(model, f"station_{index}_dark", r.palette["dark"])
    red = _mat(model, f"station_{index}_red", r.palette["accent"])
    links = model.part(f"station_{index}_platform_links")
    _add_top_hub(links, f"station_{index}", steel, length=p.hub_length)
    drop = p.drop
    for sx in (-p.hanger_half_width, p.hanger_half_width):
        _add_tube(links, f"side_link_{sx:+.1f}", (sx, 0.0, -0.02), (sx, 0.0, -drop), 0.018, steel)
        links.visual(
            Cylinder(radius=0.040, length=0.075),
            origin=Origin(xyz=(sx, 0.0, -drop), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=steel,
            name=f"lower_eye_{sx:+.1f}", material_class_id="metal.steel_galvanized",
        )
    links.visual(
        Cylinder(radius=0.020, length=p.hanger_half_width * 2.24),
        origin=Origin(xyz=(0.0, 0.0, -drop), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=steel,
        name="lower_pivot_crossbar", material_class_id="metal.steel_galvanized",
    )
    model.articulation(
        f"station_{index}_frame_to_platform_links",
        ArticulationType.REVOLUTE,
        parent="frame",
        child=links,
        origin=Origin(xyz=(x, 0.0, r.top_z - 0.125)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=180.0, velocity=1.2, lower=-0.45, upper=0.45),
    )
    platform = model.part(f"station_{index}_platform")
    platform.visual(
        Cylinder(radius=0.026, length=p.hanger_half_width * 2.24),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=red,
        name="platform_pivot_bar", material_class_id="metal.paint_coated",
    )
    platform.visual(
        Box((p.hanger_half_width * 2.16, 0.11, 0.080)),
        origin=Origin(xyz=(0.0, 0.0, -0.035)),
        material=red,
        name="pivot_to_deck_web", material_class_id="metal.paint_coated",
    )
    platform.visual(
        Box((p.width, p.depth, 0.040)),
        origin=Origin(xyz=(0.0, 0.0, -0.08)),
        material=dark,
        name="tread_deck", material_class_id="rubber.directional_grooved",
    )
    platform.visual(
        Box((p.width + 0.04, 0.055, 0.070)),
        origin=Origin(xyz=(0.0, -p.depth * 0.515, -0.06)),
        material=red,
        name="side_rail_front", material_class_id="metal.paint_coated",
    )
    platform.visual(
        Box((p.width + 0.04, 0.055, 0.070)),
        origin=Origin(xyz=(0.0, p.depth * 0.515, -0.06)),
        material=red,
        name="side_rail_rear", material_class_id="metal.paint_coated",
    )
    hand_x = p.width * 0.36
    hand_y = p.depth * 0.34
    _add_tube(
        platform, "hand_post_front", (hand_x, -hand_y, -0.06), (hand_x, -hand_y, 0.26), 0.018, red
    )
    _add_tube(
        platform, "hand_post_rear", (hand_x, hand_y, -0.06), (hand_x, hand_y, 0.26), 0.018, red
    )
    platform.visual(
        Cylinder(radius=0.020, length=hand_y * 2.16),
        origin=Origin(xyz=(hand_x, 0.0, 0.26), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=red,
        name="hand_bar", material_class_id="metal.paint_coated",
    )
    model.articulation(
        f"station_{index}_links_to_platform",
        ArticulationType.REVOLUTE,
        parent=links,
        child=platform,
        origin=Origin(xyz=(0.0, 0.0, -drop)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=110.0, velocity=1.2, lower=-0.45, upper=0.45),
        mimic=Mimic(joint=f"station_{index}_frame_to_platform_links", multiplier=-1.0),
    )


def _add_bench_station(
    model: ArticulatedObject,
    r: ResolvedPlaygroundSwingConfig,
    index: int,
    x: float,
    p: StationParams,
    *,
    glider: bool = False,
) -> None:
    steel = _mat(model, f"station_{index}_steel", r.palette["steel"])
    frame_mat = _mat(model, f"station_{index}_bench_frame", r.palette["frame_dark"])
    wood = _mat(model, f"station_{index}_wood", r.palette["wood"])
    dark = _mat(model, f"station_{index}_bench_dark", r.palette["dark"])
    yoke = model.part(f"station_{index}_glider_links" if glider else f"station_{index}_bench_yoke")
    _add_top_hub(yoke, f"station_{index}", steel, length=p.hub_length)
    drop = p.drop
    for sx in (-p.hanger_half_width, p.hanger_half_width):
        _add_tube(yoke, f"side_arm_{sx:+.1f}", (sx, 0.0, -0.02), (sx, -0.05, -drop), 0.019, steel)
        yoke.visual(
            Cylinder(radius=0.032, length=0.09),
            origin=Origin(xyz=(sx, -0.05, -drop), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=steel,
            name=f"lower_bushing_{sx:+.1f}", material_class_id="metal.steel_galvanized",
        )
    yoke.visual(
        Cylinder(radius=0.020, length=p.hanger_half_width * 2.10),
        origin=Origin(xyz=(0.0, -0.05, -drop), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=steel,
        name="lower_pivot_crossbar", material_class_id="metal.steel_galvanized",
    )
    joint_name = (
        f"station_{index}_frame_to_glider_links"
        if glider
        else f"station_{index}_frame_to_bench_yoke"
    )
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent="frame",
        child=yoke,
        origin=Origin(xyz=(x, 0.0, r.top_z - 0.125)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=150.0, velocity=1.2, lower=-0.46, upper=0.46),
    )
    bench = model.part(
        f"station_{index}_face_to_face_bench" if glider else f"station_{index}_bench"
    )
    bench.visual(
        Cylinder(radius=0.025, length=p.hanger_half_width * 2.14),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=frame_mat,
        name="bench_pivot_bar", material_class_id="metal.paint_coated",
    )
    bench.visual(
        Box((p.hanger_half_width * 2.06, 0.12, 0.140)),
        origin=Origin(xyz=(0.0, 0.0, -0.055)),
        material=frame_mat,
        name="pivot_to_bench_frame_web", material_class_id="metal.paint_coated",
    )
    bench.visual(
        Box((p.width, p.depth if not glider else p.depth * 0.56, 0.055)),
        origin=Origin(xyz=(0.0, 0.0, -0.12)),
        material=frame_mat,
        name="bench_frame", material_class_id="metal.paint_coated",
    )
    if glider:
        bench.visual(
            Box((p.width, p.depth * 0.28, 0.050)),
            origin=Origin(xyz=(0.0, -p.depth * 0.27, -0.08)),
            material=wood,
            name="seat_pan_front", material_class_id="wood.natural_generic",
        )
        bench.visual(
            Box((p.width, p.depth * 0.28, 0.050)),
            origin=Origin(xyz=(0.0, p.depth * 0.27, -0.08)),
            material=wood,
            name="seat_pan_rear", material_class_id="wood.natural_generic",
        )
        bench.visual(
            Box((p.width * 0.98, p.depth * 0.26, 0.140)),
            origin=Origin(xyz=(0.0, -p.depth * 0.40, -0.04)),
            material=frame_mat,
            name="front_seat_to_back_web", material_class_id="metal.paint_coated",
        )
        bench.visual(
            Box((p.width * 0.98, p.depth * 0.26, 0.140)),
            origin=Origin(xyz=(0.0, p.depth * 0.40, -0.04)),
            material=frame_mat,
            name="rear_seat_to_back_web", material_class_id="metal.paint_coated",
        )
        bench.visual(
            Box((p.width, 0.055, 0.30 * p.scale)),
            origin=Origin(xyz=(0.0, -p.depth * 0.50, 0.12)),
            material=wood,
            name="back_panel_front", material_class_id="wood.natural_generic",
        )
        bench.visual(
            Box((p.width, 0.055, 0.30 * p.scale)),
            origin=Origin(xyz=(0.0, p.depth * 0.50, 0.12)),
            material=wood,
            name="back_panel_rear", material_class_id="wood.natural_generic",
        )
        bench.visual(
            Box((p.width * 0.84, p.depth * 0.21, 0.050)),
            origin=Origin(xyz=(0.0, 0.0, -0.16)),
            material=dark,
            name="center_footwell", material_class_id="rubber.smooth_plain",
        )
    else:
        for j, yy in enumerate((-p.depth * 0.35, -p.depth * 0.12, p.depth * 0.10, p.depth * 0.33)):
            bench.visual(
                Box((p.width * 0.98, p.depth * 0.17, 0.025)),
                origin=Origin(xyz=(0.0, yy, -0.10)),
                material=wood,
                name=f"seat_slat_{j}", material_class_id="wood.natural_generic",
            )
        for sx in (-p.width * 0.42, p.width * 0.42):
            bench.visual(
                Box((0.060, p.depth * 0.19, 0.420 * p.scale)),
                origin=Origin(xyz=(sx, -p.depth * 0.52, 0.05)),
                material=frame_mat,
                name=f"back_post_{sx:+.1f}", material_class_id="metal.paint_coated",
            )
        for j, zz in enumerate((0.02, 0.12, 0.22)):
            bench.visual(
                Box((p.width * 0.98, 0.035, 0.075)),
                origin=Origin(xyz=(0.0, -p.depth * 0.58, zz)),
                material=wood,
                name=f"back_slat_{j}", material_class_id="wood.natural_generic",
            )
    model.articulation(
        f"station_{index}_links_to_bench",
        ArticulationType.REVOLUTE,
        parent=yoke,
        child=bench,
        origin=Origin(xyz=(0.0, -0.05, -drop)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=80.0, velocity=1.2, lower=-0.30, upper=0.30),
        mimic=Mimic(joint=joint_name, multiplier=-1.0 if glider else 0.35),
    )


def _add_disc_station(
    model: ArticulatedObject,
    r: ResolvedPlaygroundSwingConfig,
    index: int,
    x: float,
    p: StationParams,
) -> None:
    steel = _mat(model, f"station_{index}_steel", r.palette["steel"])
    dark = _mat(model, f"station_{index}_dark", r.palette["dark"])
    seat = model.part(f"station_{index}_disc_seat")
    _add_top_hub(seat, f"station_{index}", steel, length=p.hub_length)
    seat_z = -(p.drop + 0.04)
    _add_tube(seat, "single_strap", (0.0, 0.0, -0.02), (0.0, 0.0, seat_z + 0.07), 0.018, dark)
    seat.visual(
        Cylinder(radius=p.radius, length=0.040),
        origin=Origin(xyz=(0.0, 0.0, seat_z)),
        material=dark,
        name="seat_disk", material_class_id="plastic.opaque_glossy_molded",
    )
    seat.visual(
        Sphere(radius=0.055),
        origin=Origin(xyz=(0.0, 0.0, seat_z + 0.05)),
        material=steel,
        name="seat_hub", material_class_id="metal.steel_galvanized",
    )
    model.articulation(
        f"station_{index}_frame_to_disc",
        ArticulationType.REVOLUTE,
        parent="frame",
        child=seat,
        origin=Origin(xyz=(x, 0.0, r.top_z - 0.125)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=35.0, velocity=1.7, lower=-0.65, upper=0.65),
    )
    foot = model.part(f"station_{index}_footrest_ring")
    foot.visual(
        mesh_from_geometry(
            TorusGeometry(
                radius=p.radius * 0.75, tube=0.010, radial_segments=16, tubular_segments=48
            ),
            f"station_{index}_footrest_ring_mesh",
        ),
        origin=Origin(xyz=(-p.radius * 0.55, 0.0, -0.10)),
        material=steel,
        name="footrest_loop", material_class_id="metal.steel_galvanized",
    )
    foot.visual(Box((0.04, 0.03, 0.035)), origin=Origin(), material=steel, name="footrest_hinge", material_class_id="metal.steel_galvanized")
    _add_tube(
        foot, "footrest_hinge_strut", (0.0, 0.0, 0.0), (p.radius * 0.20, 0.0, -0.10), 0.012, steel
    )
    model.articulation(
        f"station_{index}_disc_to_footrest",
        ArticulationType.REVOLUTE,
        parent=seat,
        child=foot,
        origin=Origin(xyz=(p.radius * 0.45, 0.0, seat_z - 0.02)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=1.5, lower=0.0, upper=0.60),
    )


def _add_nest_station(
    model: ArticulatedObject,
    r: ResolvedPlaygroundSwingConfig,
    index: int,
    x: float,
    p: StationParams,
) -> None:
    steel = _mat(model, f"station_{index}_steel", r.palette["steel"])
    rope = _mat(model, f"station_{index}_rope", r.palette["rope"])
    blue = _mat(model, f"station_{index}_blue", r.palette["blue"])
    hanger = model.part(f"station_{index}_nest_hanger")
    _add_top_hub(hanger, f"station_{index}", steel, length=p.hub_length)
    drop = p.drop
    link_y = p.radius * 0.75
    lower_x = p.hanger_half_width * 0.72
    for sx in (-p.hanger_half_width, p.hanger_half_width):
        _add_tube(
            hanger,
            f"paired_link_{sx:+.1f}_a",
            (sx, -0.02, -0.02),
            (sx * 0.72, -link_y, -drop),
            0.016,
            steel,
        )
        _add_tube(
            hanger,
            f"paired_link_{sx:+.1f}_b",
            (sx, 0.02, -0.02),
            (sx * 0.72, link_y, -drop),
            0.016,
            steel,
        )
    hanger.visual(
        Cylinder(radius=0.022, length=p.hub_length * 0.95),
        origin=Origin(xyz=(0.0, 0.0, -drop), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=steel,
        name="lower_basket_pivot_bar", material_class_id="metal.steel_galvanized",
    )
    _add_tube(
        hanger,
        "lower_front_spreader",
        (-lower_x, -link_y, -drop),
        (lower_x, -link_y, -drop),
        0.014,
        steel,
    )
    _add_tube(
        hanger,
        "lower_rear_spreader",
        (-lower_x, link_y, -drop),
        (lower_x, link_y, -drop),
        0.014,
        steel,
    )
    _add_tube(
        hanger, "lower_center_web_front", (0.0, 0.0, -drop), (0.0, -link_y, -drop), 0.012, steel
    )
    _add_tube(
        hanger, "lower_center_web_rear", (0.0, 0.0, -drop), (0.0, link_y, -drop), 0.012, steel
    )
    model.articulation(
        f"station_{index}_frame_to_nest_hanger",
        ArticulationType.REVOLUTE,
        parent="frame",
        child=hanger,
        origin=Origin(xyz=(x, 0.0, r.top_z - 0.125)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=100.0, velocity=1.5, lower=-0.55, upper=0.55),
    )
    basket = model.part(f"station_{index}_nest_basket")
    basket.visual(
        Cylinder(radius=0.026, length=p.hub_length * 0.92),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=blue,
        name="basket_pivot_bar", material_class_id="metal.paint_coated",
    )
    basket.visual(
        mesh_from_geometry(
            TorusGeometry(
                radius=p.radius, tube=0.045 * p.scale, radial_segments=24, tubular_segments=72
            ),
            f"station_{index}_nest_ring_mesh",
        ),
        material=blue,
        name="padded_ring", material_class_id="rubber.sponge_foam",
    )
    basket.visual(
        mesh_from_geometry(
            TorusGeometry(
                radius=p.radius * 0.56, tube=0.010, radial_segments=12, tubular_segments=48
            ),
            f"station_{index}_inner_rope_ring_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, -0.025)),
        material=rope,
        name="inner_rope_ring", material_class_id="organic.woven_plant_fiber",
    )
    weave_offsets = tuple(p.radius * t for t in (-0.62, -0.31, 0.0, 0.31, 0.62))
    for j, yy in enumerate(weave_offsets):
        half = math.sqrt(max(0.0, (p.radius * 0.94) ** 2 - yy * yy))
        _add_tube(basket, f"weave_x_{j}", (-half, yy, -0.035), (half, yy, -0.035), 0.006, rope)
    for j, xx in enumerate(weave_offsets):
        half = math.sqrt(max(0.0, (p.radius * 0.94) ** 2 - xx * xx))
        _add_tube(basket, f"weave_y_{j}", (xx, -half, -0.043), (xx, half, -0.043), 0.006, rope)
    model.articulation(
        f"station_{index}_hanger_to_nest",
        ArticulationType.REVOLUTE,
        parent=hanger,
        child=basket,
        origin=Origin(xyz=(0.0, 0.0, -drop)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=22.0, velocity=1.0, lower=-0.18, upper=0.18),
    )


def _build_station(
    model: ArticulatedObject,
    r: ResolvedPlaygroundSwingConfig,
    index: int,
    recipe: StationRecipe,
    x: float,
    p: StationParams,
) -> None:
    if recipe == "simple_belt_station":
        _add_belt_station(model, r, index, x, p)
    elif recipe == "bucket_station":
        _add_bucket_station(model, r, index, x, p)
    elif recipe == "tire_station":
        _add_tire_station(model, r, index, x, p)
    elif recipe == "lap_bar_station":
        _add_lap_bar_station(model, r, index, x, p)
    elif recipe == "platform_station":
        _add_platform_station(model, r, index, x, p)
    elif recipe == "bench_station":
        _add_bench_station(model, r, index, x, p, glider=False)
    elif recipe == "glider_station":
        _add_bench_station(model, r, index, x, p, glider=True)
    elif recipe == "swivel_disc_station":
        _add_disc_station(model, r, index, x, p)
    elif recipe == "nest_station":
        _add_nest_station(model, r, index, x, p)
    else:  # pragma: no cover - resolve_config validates.
        raise ValueError(f"Unhandled station recipe {recipe!r}")


def build_playground_swing(
    config: PlaygroundSwingConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or PlaygroundSwingConfig())
    model = ArticulatedObject(name=r.name, assets=assets)
    _build_frame(model, r)
    for index, (recipe, x, params) in enumerate(
        zip(r.station_recipes, r.station_centers, r.station_params)
    ):
        _build_station(model, r, index, recipe, x, params)
    model.meta["template_slug"] = "playground_swing"
    model.meta["station_recipes"] = list(r.station_recipes)
    return model


def build_seeded_playground_swing(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_playground_swing(config_from_seed(seed), assets=assets)


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    config = resolve_config(config_from_seed(seed))
    choices: list[tuple[str, str]] = [("support_frame", config.support_frame_module)]
    choices.append(("station_count", f"{config.station_count}_stations"))
    for index, recipe in enumerate(config.station_recipes):
        choices.append((f"station_{index}", recipe))
    return choices


def _main_station_part_name(recipe: StationRecipe, index: int) -> str:
    return {
        "simple_belt_station": f"station_{index}_swing",
        "bucket_station": f"station_{index}_bucket",
        "tire_station": f"station_{index}_tire",
        "lap_bar_station": f"station_{index}_slatted_seat",
        "platform_station": f"station_{index}_platform_links",
        "bench_station": f"station_{index}_bench_yoke",
        "glider_station": f"station_{index}_glider_links",
        "swivel_disc_station": f"station_{index}_disc_seat",
        "nest_station": f"station_{index}_nest_hanger",
    }[recipe]


def run_playground_swing_tests(
    object_model: ArticulatedObject,
    config: PlaygroundSwingConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    part_by_name = {part.name: part for part in object_model.parts}

    for index, recipe in enumerate(r.station_recipes):
        main_name = _main_station_part_name(recipe, index)
        main = part_by_name.get(main_name)
        if main is not None:
            ctx.allow_overlap(
                frame,
                main,
                reason="The station top hub is captured inside the frame clevis/saddle around the shared pivot axis.",
            )
            ctx.allow_overlap(
                frame,
                main,
                elem_a=f"station_{index}_pivot_pin",
                elem_b=f"station_{index}_upper_hub",
                reason="The swing station upper hub is intentionally captured on the frame pivot pin.",
            )
            ctx.allow_overlap(
                frame,
                main,
                elem_a=f"station_{index}_pivot_saddle",
                elem_b=f"station_{index}_upper_hub",
                reason="The saddle visibly supports the captured hub around the same top pivot.",
            )
        for child_name in (
            f"station_{index}_lap_bar",
            f"station_{index}_platform",
            f"station_{index}_bench",
            f"station_{index}_face_to_face_bench",
            f"station_{index}_footrest_ring",
            f"station_{index}_nest_basket",
        ):
            child = part_by_name.get(child_name)
            if child is not None and main is not None:
                ctx.allow_overlap(
                    main,
                    child,
                    reason="Station-local hinge hardware intentionally captures the child part at its pivot.",
                )

    ctx.check_model_valid()
    parts = {part.name for part in object_model.parts}
    joints = {joint.name: joint for joint in object_model.articulations}
    ctx.check("frame_present", "frame" in parts)
    ctx.check("station_count_matches_config", len(r.station_recipes) == r.station_count)
    for index, recipe in enumerate(r.station_recipes):
        main_name = _main_station_part_name(recipe, index)
        ctx.check(f"station_{index}_main_part_present", main_name in parts, details=recipe)
        station_joints = [name for name in joints if name.startswith(f"station_{index}_")]
        ctx.check(
            f"station_{index}_has_articulation", bool(station_joints), details=str(station_joints)
        )
    return ctx.report()


__all__ = [
    "PlaygroundSwingConfig",
    "ResolvedPlaygroundSwingConfig",
    "StationParams",
    "build_playground_swing",
    "build_seeded_playground_swing",
    "config_from_seed",
    "resolve_config",
    "run_playground_swing_tests",
    "slot_choices_for_seed",
    "__modular__",
]
