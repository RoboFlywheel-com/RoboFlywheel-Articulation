# SPDX-License-Identifier: Apache-2.0

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
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
)

__modular__ = True

GondolaStyle = Literal[
    "box_cabin",
    "open_basket",
    "glass_capsule",
    "bucket_seat",
    "rounded_pod",
]
SupportStyle = Literal["a_frame", "truss_tower", "inclined_legs"]
RimStyle = Literal["double_torus", "single_torus", "twin_rings", "concentric_double"]
ScaleMode = Literal["compact", "normal", "landmark"]
BaseStyle = Literal["platform"]
HangerStyle = Literal["pivot_bar", "yoke_fork", "between_rims", "leveling_arm"]
GondolaMotionMode = Literal["free_swing", "counter_rotate_mimic"]

LEVELING_ARM_LENGTH = 0.060
LOADING_PLINTH_HEIGHT = 0.045
PLATFORM_TOP_Z = 0.085

GONDOLA_WIDTH_Y = 0.132
GONDOLA_LOWEST_POINT_BELOW_PIVOT = 0.249
SUPPORT_RAIL_TOP_Z = 0.205
GROUND_CLEARANCE = 0.025
DEFAULT_RIM_RADIUS = 0.78
DEFAULT_WHEEL_HALF_WIDTH = 0.105
DEFAULT_AXLE_Z = (
    DEFAULT_RIM_RADIUS + GONDOLA_LOWEST_POINT_BELOW_PIVOT + SUPPORT_RAIL_TOP_Z + GROUND_CLEARANCE
)
SEED_RIM_RADIUS_MIN = DEFAULT_RIM_RADIUS
SEED_RIM_RADIUS_MAX = 1.10
SEED_COMPACT_RIM_RADIUS_MIN = 0.66
SEED_COMPACT_RIM_RADIUS_MAX = 0.90
SEED_LANDMARK_RIM_RADIUS_MIN = 1.10
SEED_LANDMARK_RIM_RADIUS_MAX = 1.65
SCALE_MODE_SEED_RANGES: dict[ScaleMode, tuple[float, float]] = {
    "compact": (SEED_COMPACT_RIM_RADIUS_MIN, SEED_COMPACT_RIM_RADIUS_MAX),
    "normal": (SEED_RIM_RADIUS_MIN, SEED_RIM_RADIUS_MAX),
    "landmark": (SEED_LANDMARK_RIM_RADIUS_MIN, SEED_LANDMARK_RIM_RADIUS_MAX),
}
SCALE_MODE_BASE_RIM_RADIUS: dict[ScaleMode, float] = {
    "compact": 0.66,
    "normal": DEFAULT_RIM_RADIUS,
    "landmark": 1.10,
}
SCALE_MODE_WHEEL_HALF_WIDTH_RANGES: dict[ScaleMode, tuple[float, float]] = {
    "compact": (0.090, 0.112),
    "normal": (0.095, 0.125),
    "landmark": (0.118, 0.155),
}


FramePaletteName = Literal[
    "painted_white",
    "industrial_galvanized",
    "candy_red",
    "midnight_navy",
    "deep_teal",
    "sunset_orange",
]
CabinPaletteName = Literal[
    "cream_and_white",
    "red_and_cream",
    "navy_and_cream",
    "forest_and_cream",
    "bronze_and_black",
    "lavender_and_cream",
    "mint_and_cream",
    "retro_yellow_and_white",
]
GlassTintName = Literal["smoky_blue", "clear", "rose", "amber", "green_tinted"]
GondolaPaletteName = Literal[
    "none",
    "rainbow_six",
    "warm_four",
    "cool_four",
    "pastel_six",
    "primary_three",
]


@dataclass(frozen=True)
class FramePalette:
    """Colors for the structural metalwork shared across leg/hub/rim and platform."""

    frame: tuple[float, float, float, float]
    accent: tuple[float, float, float, float]
    platform: tuple[float, float, float, float]


FRAME_PALETTES: dict[FramePaletteName, FramePalette] = {
    "painted_white": FramePalette(
        frame=(0.90, 0.90, 0.86, 1.0),
        accent=(0.32, 0.33, 0.34, 1.0),
        platform=(0.76, 0.75, 0.70, 1.0),
    ),
    "industrial_galvanized": FramePalette(
        frame=(0.72, 0.74, 0.76, 1.0),
        accent=(0.28, 0.30, 0.33, 1.0),
        platform=(0.55, 0.55, 0.57, 1.0),
    ),
    "candy_red": FramePalette(
        frame=(0.82, 0.16, 0.18, 1.0),
        accent=(0.25, 0.10, 0.12, 1.0),
        platform=(0.78, 0.74, 0.68, 1.0),
    ),
    "midnight_navy": FramePalette(
        frame=(0.14, 0.20, 0.40, 1.0),
        accent=(0.85, 0.83, 0.78, 1.0),
        platform=(0.68, 0.66, 0.62, 1.0),
    ),
    "deep_teal": FramePalette(
        frame=(0.08, 0.42, 0.46, 1.0),
        accent=(0.92, 0.90, 0.84, 1.0),
        platform=(0.70, 0.68, 0.64, 1.0),
    ),
    "sunset_orange": FramePalette(
        frame=(0.90, 0.48, 0.18, 1.0),
        accent=(0.22, 0.20, 0.22, 1.0),
        platform=(0.80, 0.75, 0.66, 1.0),
    ),
}


@dataclass(frozen=True)
class CabinPalette:
    body: tuple[float, float, float, float]
    trim: tuple[float, float, float, float]


CABIN_PALETTES: dict[CabinPaletteName, CabinPalette] = {
    "cream_and_white": CabinPalette(body=(0.92, 0.88, 0.78, 1.0), trim=(0.96, 0.96, 0.92, 1.0)),
    "red_and_cream": CabinPalette(body=(0.78, 0.20, 0.22, 1.0), trim=(0.96, 0.94, 0.88, 1.0)),
    "navy_and_cream": CabinPalette(body=(0.18, 0.26, 0.48, 1.0), trim=(0.95, 0.93, 0.86, 1.0)),
    "forest_and_cream": CabinPalette(body=(0.16, 0.42, 0.26, 1.0), trim=(0.94, 0.92, 0.84, 1.0)),
    "bronze_and_black": CabinPalette(body=(0.62, 0.42, 0.22, 1.0), trim=(0.18, 0.16, 0.16, 1.0)),
    "lavender_and_cream": CabinPalette(body=(0.62, 0.55, 0.78, 1.0), trim=(0.96, 0.94, 0.90, 1.0)),
    "mint_and_cream": CabinPalette(body=(0.50, 0.78, 0.66, 1.0), trim=(0.96, 0.94, 0.88, 1.0)),
    "retro_yellow_and_white": CabinPalette(
        body=(0.94, 0.78, 0.22, 1.0), trim=(0.97, 0.96, 0.92, 1.0)
    ),
}


GLASS_TINTS: dict[GlassTintName, tuple[float, float, float, float]] = {
    "smoky_blue": (0.55, 0.68, 0.72, 0.40),
    "clear": (0.85, 0.90, 0.94, 0.35),
    "rose": (0.78, 0.55, 0.62, 0.42),
    "amber": (0.82, 0.66, 0.34, 0.45),
    "green_tinted": (0.50, 0.72, 0.58, 0.40),
}


# Per-gondola color rotations. The cycle is applied modulo len(palette), so each
# gondola around the wheel gets its own RGB while sharing the chosen trim color.
GONDOLA_PALETTES: dict[GondolaPaletteName, tuple[tuple[float, float, float, float], ...]] = {
    "none": (),
    "rainbow_six": (
        (0.85, 0.22, 0.22, 1.0),  # red
        (0.94, 0.62, 0.18, 1.0),  # orange
        (0.94, 0.86, 0.30, 1.0),  # yellow
        (0.30, 0.70, 0.36, 1.0),  # green
        (0.22, 0.46, 0.82, 1.0),  # blue
        (0.58, 0.34, 0.78, 1.0),  # violet
    ),
    "warm_four": (
        (0.82, 0.22, 0.22, 1.0),
        (0.92, 0.58, 0.20, 1.0),
        (0.95, 0.82, 0.30, 1.0),
        (0.74, 0.34, 0.18, 1.0),
    ),
    "cool_four": (
        (0.22, 0.46, 0.78, 1.0),
        (0.32, 0.70, 0.78, 1.0),
        (0.30, 0.55, 0.42, 1.0),
        (0.46, 0.34, 0.74, 1.0),
    ),
    "pastel_six": (
        (0.96, 0.74, 0.74, 1.0),
        (0.96, 0.86, 0.68, 1.0),
        (0.94, 0.94, 0.74, 1.0),
        (0.76, 0.92, 0.78, 1.0),
        (0.72, 0.84, 0.94, 1.0),
        (0.86, 0.78, 0.94, 1.0),
    ),
    "primary_three": (
        (0.85, 0.18, 0.18, 1.0),
        (0.94, 0.82, 0.24, 1.0),
        (0.18, 0.40, 0.82, 1.0),
    ),
}


@dataclass(frozen=True)
class GondolaCollisionProfile:
    width_y: float
    lowest_point_below_pivot: float


GONDOLA_COLLISION_PROFILES: dict[GondolaStyle, GondolaCollisionProfile] = {
    "box_cabin": GondolaCollisionProfile(width_y=0.132, lowest_point_below_pivot=0.249),
    "open_basket": GondolaCollisionProfile(width_y=0.140, lowest_point_below_pivot=0.235),
    "glass_capsule": GondolaCollisionProfile(width_y=0.138, lowest_point_below_pivot=0.228),
    "bucket_seat": GondolaCollisionProfile(width_y=0.152, lowest_point_below_pivot=0.265),
    "rounded_pod": GondolaCollisionProfile(width_y=0.140, lowest_point_below_pivot=0.236),
}

# Largest half-extent (|x|) of any single gondola visual, measured in the gondola
# local frame. Swing rotates the cabin about the wheel's X axis, which leaves the
# X coordinate invariant, so a cabin whose whole X footprint stays inboard of the
# rim-tube band (|x| < wheel_half_width - RIM_TUBE_RADIUS) can never touch the rim
# at any swing pose. Only the wide bucket_seat back/lip reach far enough out in X
# to matter; the rest are comfortably inboard for every seeded wheel_half_width.
RIM_TUBE_RADIUS = 0.018
GONDOLA_MAX_HALF_X: dict[GondolaStyle, float] = {
    "box_cabin": 0.065,
    "open_basket": 0.069,
    "glass_capsule": 0.069,
    "bucket_seat": 0.095,
    "rounded_pod": 0.061,
}

# Target minimum clearance between two adjacent cabins at their worst-case
# opposing swings (comfortably above the 0.005 motion-QC overlap tolerance and
# the 0.008 clearance floor the playbook asks for).
GONDOLA_SWING_CLEARANCE = 0.014
# A gondola is a gravity-levelled cradle: it never flips. Cap the derived swing
# amplitude so even a very sparse wheel keeps a physically plausible range.
GONDOLA_SWING_MAX = 1.30


@dataclass(frozen=True)
class FerrisWheelConfig:
    num_gondolas: int = 16
    spoke_count: int = 32
    gondola_style: GondolaStyle = "box_cabin"
    support_style: SupportStyle = "a_frame"
    rim_style: RimStyle = "double_torus"
    scale_mode: ScaleMode = "normal"
    base_style: BaseStyle = "platform"
    hanger_style: HangerStyle = "pivot_bar"
    gondola_motion_mode: GondolaMotionMode = "free_swing"
    railing_enabled: bool = True
    rim_radius: float | None = None
    inner_rim_radius: float | None = None
    wheel_half_width: float = DEFAULT_WHEEL_HALF_WIDTH
    axle_z: float | None = None
    boarding_bridge_enabled: bool = False
    loading_plinth_enabled: bool = False
    operator_booth_enabled: bool = False
    drive_house_enabled: bool = False
    service_deck_enabled: bool = False
    frame_palette: FramePaletteName = "painted_white"
    cabin_palette: CabinPaletteName = "cream_and_white"
    glass_tint: GlassTintName = "smoky_blue"
    gondola_palette: GondolaPaletteName = "none"
    name: str = "reference_ferris_wheel"


@dataclass(frozen=True)
class ResolvedFerrisWheelConfig:
    num_gondolas: int
    spoke_count: int
    gondola_style: GondolaStyle
    support_style: SupportStyle
    rim_style: RimStyle
    scale_mode: ScaleMode
    base_style: BaseStyle
    hanger_style: HangerStyle
    gondola_motion_mode: GondolaMotionMode
    railing_enabled: bool
    rim_radius: float
    inner_rim_radius: float
    wheel_half_width: float
    axle_z: float
    support_scale: float
    boarding_bridge_enabled: bool
    loading_plinth_enabled: bool
    operator_booth_enabled: bool
    drive_house_enabled: bool
    service_deck_enabled: bool
    frame_palette: FramePaletteName
    cabin_palette: CabinPaletteName
    glass_tint: GlassTintName
    gondola_palette: GondolaPaletteName
    name: str


def config_from_seed(seed: int) -> FerrisWheelConfig:
    rng = random.Random(seed)
    num_gondolas = rng.choice(tuple(range(4, 21)))
    spoke_multiplier = rng.choice((2, 3))
    spoke_count = num_gondolas * spoke_multiplier
    if spoke_count % 2 != 0:
        spoke_count += 1
    scale_mode = rng.choices(
        ("compact", "normal", "landmark"),
        weights=(0.25, 0.55, 0.20),
        k=1,
    )[0]
    rim_min, rim_max = SCALE_MODE_SEED_RANGES[scale_mode]
    width_min, width_max = SCALE_MODE_WHEEL_HALF_WIDTH_RANGES[scale_mode]
    rim_style = rng.choices(
        ("double_torus", "single_torus", "twin_rings", "concentric_double"),
        weights=(0.34, 0.22, 0.22, 0.22),
        k=1,
    )[0]
    if rim_style == "twin_rings":
        hanger_style: HangerStyle = rng.choice(("pivot_bar", "yoke_fork", "between_rims"))
    else:
        # leveling_arm is valid for non-twin rims (it hangs off the outer rim only)
        hanger_style = rng.choice(("pivot_bar", "yoke_fork", "leveling_arm"))
    base_style: BaseStyle = "platform"
    # Platform extras: cluster of independent booleans, slightly biased toward off
    # to keep most seeded wheels uncluttered.
    boarding_bridge = rng.random() < 0.20
    loading_plinth = rng.random() < 0.20
    operator_booth = rng.random() < 0.20
    drive_house = rng.random() < 0.20
    service_deck = rng.random() < 0.15
    # Palette diversity: weight defaults a bit higher but cycle the others in too.
    frame_palette: FramePaletteName = rng.choices(
        (
            "painted_white",
            "industrial_galvanized",
            "candy_red",
            "midnight_navy",
            "deep_teal",
            "sunset_orange",
        ),
        weights=(0.34, 0.18, 0.14, 0.12, 0.12, 0.10),
        k=1,
    )[0]
    cabin_palette: CabinPaletteName = rng.choices(
        (
            "cream_and_white",
            "red_and_cream",
            "navy_and_cream",
            "forest_and_cream",
            "bronze_and_black",
            "lavender_and_cream",
            "mint_and_cream",
            "retro_yellow_and_white",
        ),
        weights=(0.26, 0.14, 0.12, 0.10, 0.10, 0.10, 0.10, 0.08),
        k=1,
    )[0]
    glass_tint: GlassTintName = rng.choices(
        ("smoky_blue", "clear", "rose", "amber", "green_tinted"),
        weights=(0.40, 0.22, 0.13, 0.13, 0.12),
        k=1,
    )[0]
    gondola_palette: GondolaPaletteName = rng.choices(
        ("none", "rainbow_six", "warm_four", "cool_four", "pastel_six", "primary_three"),
        weights=(0.40, 0.15, 0.12, 0.12, 0.12, 0.09),
        k=1,
    )[0]
    return FerrisWheelConfig(
        num_gondolas=num_gondolas,
        spoke_count=spoke_count,
        gondola_style=rng.choice(
            ("box_cabin", "open_basket", "glass_capsule", "bucket_seat", "rounded_pod")
        ),
        support_style=rng.choice(("a_frame", "truss_tower", "inclined_legs")),
        rim_style=rim_style,
        scale_mode=scale_mode,
        base_style=base_style,
        hanger_style=hanger_style,
        gondola_motion_mode=rng.choices(
            ("free_swing", "counter_rotate_mimic"), weights=(0.70, 0.30), k=1
        )[0],
        railing_enabled=(rng.random() > 0.20),
        rim_radius=round(rng.uniform(rim_min, rim_max), 3),
        wheel_half_width=round(rng.uniform(width_min, width_max), 3),
        boarding_bridge_enabled=boarding_bridge,
        loading_plinth_enabled=loading_plinth,
        operator_booth_enabled=operator_booth,
        drive_house_enabled=drive_house,
        service_deck_enabled=service_deck,
        frame_palette=frame_palette,
        cabin_palette=cabin_palette,
        glass_tint=glass_tint,
        gondola_palette=gondola_palette,
        name=f"seeded_ferris_wheel_{seed}",
    )


def gondola_collision_profile(style: GondolaStyle) -> GondolaCollisionProfile:
    return GONDOLA_COLLISION_PROFILES[style]


def support_scale_for_radius(rim_radius: float) -> float:
    return max(1.0, rim_radius / DEFAULT_RIM_RADIUS)


def hub_geometry(wheel_half_width: float) -> tuple[float, float, float, float]:
    width_ratio = wheel_half_width / DEFAULT_WHEEL_HALF_WIDTH
    return (
        2.0 * wheel_half_width * 0.96,
        wheel_half_width * 0.92,
        0.074 * width_ratio,
        0.055 * width_ratio,
    )


def resolve_config(config: FerrisWheelConfig) -> ResolvedFerrisWheelConfig:
    if config.num_gondolas < 4:
        raise ValueError("num_gondolas must be at least 4")
    if config.spoke_count < config.num_gondolas:
        raise ValueError("spoke_count should be >= num_gondolas")
    if config.gondola_style not in GONDOLA_COLLISION_PROFILES:
        raise ValueError(f"Unsupported gondola_style: {config.gondola_style}")
    if config.support_style not in {"a_frame", "truss_tower", "inclined_legs"}:
        raise ValueError(f"Unsupported support_style: {config.support_style}")
    if config.rim_style not in {"double_torus", "single_torus", "twin_rings", "concentric_double"}:
        raise ValueError(f"Unsupported rim_style: {config.rim_style}")
    if config.scale_mode not in {"compact", "normal", "landmark"}:
        raise ValueError(f"Unsupported scale_mode: {config.scale_mode}")
    if config.base_style not in {"platform"}:
        raise ValueError(f"Unsupported base_style: {config.base_style}")
    if config.hanger_style not in {"pivot_bar", "yoke_fork", "between_rims", "leveling_arm"}:
        raise ValueError(f"Unsupported hanger_style: {config.hanger_style}")
    if config.gondola_motion_mode not in {"free_swing", "counter_rotate_mimic"}:
        raise ValueError(f"Unsupported gondola_motion_mode: {config.gondola_motion_mode}")
    if not isinstance(config.railing_enabled, bool):
        raise ValueError("railing_enabled must be a bool")
    for flag_name in (
        "boarding_bridge_enabled",
        "loading_plinth_enabled",
        "operator_booth_enabled",
        "drive_house_enabled",
        "service_deck_enabled",
    ):
        if not isinstance(getattr(config, flag_name), bool):
            raise ValueError(f"{flag_name} must be a bool")
    if config.hanger_style == "between_rims" and config.rim_style != "twin_rings":
        raise ValueError("between_rims hanger_style requires rim_style='twin_rings'")
    if config.rim_style == "concentric_double" and config.hanger_style == "between_rims":
        raise ValueError(
            "concentric_double rim_style is incompatible with between_rims hanger_style"
        )
    if config.frame_palette not in FRAME_PALETTES:
        raise ValueError(f"Unsupported frame_palette: {config.frame_palette}")
    if config.cabin_palette not in CABIN_PALETTES:
        raise ValueError(f"Unsupported cabin_palette: {config.cabin_palette}")
    if config.glass_tint not in GLASS_TINTS:
        raise ValueError(f"Unsupported glass_tint: {config.glass_tint}")
    if config.gondola_palette not in GONDOLA_PALETTES:
        raise ValueError(f"Unsupported gondola_palette: {config.gondola_palette}")

    # A twin-ring rim carries cross bridges (rim_bridge_i) sitting on the outer ring.
    # counter_rotate_mimic keeps each cabin upright while the wheel spins, so the
    # cabin/hanger dwells at the outer-ring radius on the sides and the bridges sweep
    # straight through it. A smooth (torus) rim has no such spokes-across-the-width to
    # collide with, so mimic is only coherent there. Coerce the incompatible combo to
    # free_swing rather than emit a wheel that spears itself.
    gondola_motion_mode = config.gondola_motion_mode
    if config.rim_style == "twin_rings" and gondola_motion_mode == "counter_rotate_mimic":
        gondola_motion_mode = "free_swing"

    profile = gondola_collision_profile(config.gondola_style)
    effective_drop = profile.lowest_point_below_pivot
    if config.hanger_style == "leveling_arm":
        effective_drop += LEVELING_ARM_LENGTH
    min_spacing = max(profile.width_y + 0.018, effective_drop + 0.050)
    required_radius = min_spacing / (2.0 * math.sin(math.pi / config.num_gondolas))
    if config.rim_radius is None:
        rim_radius = max(SCALE_MODE_BASE_RIM_RADIUS[config.scale_mode], required_radius)
    else:
        rim_radius = max(config.rim_radius, required_radius)
    inner_rim_radius = (
        rim_radius * 0.74
        if config.inner_rim_radius is None
        else min(config.inner_rim_radius, rim_radius - 0.10)
    )
    # The rim is a tube living at x = +/- wheel_half_width. A cabin whose X
    # footprint reaches into that band (|x| >= wheel_half_width - RIM_TUBE_RADIUS)
    # can graze the outer rim -- and swing (rotation about X) cannot move it out,
    # since it preserves X. Widen the wheel just enough that the widest cabin
    # visual stays inboard of the rim tube for this gondola style.
    min_half_width = GONDOLA_MAX_HALF_X[config.gondola_style] + RIM_TUBE_RADIUS + 0.005
    wheel_half_width = max(config.wheel_half_width, min_half_width)
    scale = support_scale_for_radius(rim_radius)
    support_rail_top_z = SUPPORT_RAIL_TOP_Z * scale
    plinth_clearance = 0.0
    if config.loading_plinth_enabled:
        # Plinth top sits at LOADING_PLINTH_TOP_Z above platform top; reserve room so the
        # lowest gondola sweep stays above the plinth top.
        plinth_clearance = LOADING_PLINTH_HEIGHT + 0.020
    required_axle_z = (
        rim_radius + effective_drop + support_rail_top_z + GROUND_CLEARANCE + plinth_clearance
    )
    axle_z = required_axle_z if config.axle_z is None else max(config.axle_z, required_axle_z)
    return ResolvedFerrisWheelConfig(
        num_gondolas=config.num_gondolas,
        spoke_count=config.spoke_count,
        gondola_style=config.gondola_style,
        support_style=config.support_style,
        rim_style=config.rim_style,
        scale_mode=config.scale_mode,
        base_style=config.base_style,
        hanger_style=config.hanger_style,
        gondola_motion_mode=gondola_motion_mode,
        railing_enabled=config.railing_enabled,
        rim_radius=rim_radius,
        inner_rim_radius=inner_rim_radius,
        wheel_half_width=wheel_half_width,
        axle_z=axle_z,
        support_scale=scale,
        boarding_bridge_enabled=config.boarding_bridge_enabled,
        loading_plinth_enabled=config.loading_plinth_enabled,
        operator_booth_enabled=config.operator_booth_enabled,
        drive_house_enabled=config.drive_house_enabled,
        service_deck_enabled=config.service_deck_enabled,
        frame_palette=config.frame_palette,
        cabin_palette=config.cabin_palette,
        glass_tint=config.glass_tint,
        gondola_palette=config.gondola_palette,
        name=config.name,
    )


def _mesh(assets: AssetContext, name: str, geometry):
    return mesh_from_geometry(geometry, assets.mesh_path(name))


def _midpoint(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    return ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5, (a[2] + b[2]) * 0.5)


def _distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2 + (b[2] - a[2]) ** 2)


def _rpy_for_cylinder(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(math.hypot(dx, dy), dz)
    return (0.0, pitch, yaw)


def _member(
    part,
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    *,
    radius: float,
    material,
    name: str,
) -> None:
    part.visual(
        Cylinder(radius=radius, length=_distance(a, b)),
        origin=Origin(xyz=_midpoint(a, b), rpy=_rpy_for_cylinder(a, b)),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _wheel_point(radius: float, angle: float, x: float = 0.0) -> tuple[float, float, float]:
    return (x, radius * math.cos(angle), radius * math.sin(angle))


# The platform slab top is a fixed height (independent of wheel scale) so that the
# leg feet (planted at PLATFORM_TOP_Z) and every deck fixture share one datum. The
# slab is a touch taller than PLATFORM_TOP_Z so the feet and fixtures embed into it
# rather than resting exactly on the surface (which floats under FP rounding).
PLATFORM_SLAB_TOP_Z = 0.090


def _add_platform_railings(base, *, material, scale: float, enabled: bool) -> None:
    if not enabled:
        return
    post_positions: list[tuple[float, float]] = []
    for x in (-0.42, -0.24, 0.0, 0.24, 0.42):
        post_positions.append((x * scale, -0.34 * scale))
        post_positions.append((x * scale, 0.34 * scale))
    for y in (-0.18, 0.0, 0.18):
        post_positions.append((-0.52 * scale, y * scale))
        post_positions.append((0.52 * scale, y * scale))
    # Posts are anchored to the slab top: their base is pushed 0.015 into the slab so
    # the connection is robust at every scale, and the rails cross the posts within
    # their z-span so the whole railing is one connected shell tied to the slab.
    post_len = 0.115
    post_bottom = PLATFORM_SLAB_TOP_Z - 0.015
    post_center_z = post_bottom + post_len / 2.0
    lower_rail_z = post_bottom + post_len * 0.34
    upper_rail_z = post_bottom + post_len * 0.90
    for idx, (x, y) in enumerate(post_positions):
        base.visual(
            Cylinder(radius=0.008 * scale, length=post_len),
            origin=Origin(xyz=(x, y, post_center_z)),
            material=material,
            name=f"rail_post_{idx}", material_class_id="metal.paint_coated",
        )
    for y, label in ((-0.34, "rear"), (0.34, "front")):
        for z, level in ((lower_rail_z, "lower"), (upper_rail_z, "upper")):
            base.visual(
                Box((1.08 * scale, 0.010, 0.010)),
                origin=Origin(xyz=(0.0, y * scale, z)),
                material=material,
                name=f"{label}_{level}_rail", material_class_id="metal.paint_coated",
            )
    for x, label in ((-0.52, "left"), (0.52, "right")):
        for z, level in ((lower_rail_z, "lower"), (upper_rail_z, "upper")):
            base.visual(
                Box((0.010, 0.68 * scale, 0.010)),
                origin=Origin(xyz=(x * scale, 0.0, z)),
                material=material,
                name=f"{label}_{level}_rail", material_class_id="metal.paint_coated",
            )


def _add_platform_base(support, *, material, scale: float, railing_enabled: bool) -> None:
    slab_h = PLATFORM_SLAB_TOP_Z
    support.visual(
        Box((1.18 * scale, 0.82 * scale, slab_h)),
        origin=Origin(xyz=(0.0, 0.0, slab_h / 2.0)),
        material=material,
        name="platform_slab", material_class_id="metal.patterned_sheet_panel",
    )
    # Curbstones ride the front/rear slab edges. Their inner face is pulled well
    # inside the slab footprint (0.40 vs the 0.41 half-depth) so they overlap the
    # slab with healthy margin at any scale, and they straddle the slab top.
    for y_sign, label in ((1.0, "front"), (-1.0, "rear")):
        support.visual(
            Box((1.22 * scale, 0.060, 0.085)),
            origin=Origin(xyz=(0.0, y_sign * 0.40 * scale, PLATFORM_SLAB_TOP_Z)),
            material=material,
            name=f"{label}_curbstone", material_class_id="metal.paint_coated",
        )
    _add_platform_railings(support, material=material, scale=scale, enabled=railing_enabled)


def _add_optional_platform_extras(
    support, resolved: ResolvedFerrisWheelConfig, *, material, dark, white
) -> None:
    """Drive house / operator booth / boarding bridge / loading plinth / service deck.
    All extras anchor to surfaces that already exist on the support frame so nothing
    is left floating, and footprints are placed clear of the leg feet."""
    scale = resolved.support_scale
    deck_top_z = PLATFORM_TOP_Z
    # Drive house: a sealed motor cabinet sitting on the deck off to one side, beyond
    # the leg foot footprint (legs span y in [-foot_y, +foot_y] with foot_y >= 0.31*scale).
    if resolved.drive_house_enabled:
        dh_w = 0.22 * scale
        dh_d = 0.22 * scale
        dh_h = 0.20 * scale
        support.visual(
            Box((dh_w, dh_d, dh_h)),
            origin=Origin(xyz=(0.40 * scale, -0.20 * scale, deck_top_z + dh_h / 2.0)),
            material=dark,
            name="drive_house", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
        )
        support.visual(
            Box((dh_w * 0.85, dh_d * 0.85, 0.014)),
            origin=Origin(xyz=(0.40 * scale, -0.20 * scale, deck_top_z + dh_h + 0.007)),
            material=white,
            name="drive_house_roof", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
        )
    # Operator booth: a taller ticket cabin opposite the drive house.
    if resolved.operator_booth_enabled:
        ob_w = 0.20 * scale
        ob_d = 0.20 * scale
        ob_h = 0.28 * scale
        support.visual(
            Box((ob_w, ob_d, ob_h)),
            origin=Origin(xyz=(-0.40 * scale, 0.22 * scale, deck_top_z + ob_h / 2.0)),
            material=white,
            name="operator_booth", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
        )
        support.visual(
            Box((ob_w * 0.95, ob_d * 0.95, 0.018)),
            origin=Origin(xyz=(-0.40 * scale, 0.22 * scale, deck_top_z + ob_h + 0.009)),
            material=dark,
            name="booth_roof", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
        )
    # Boarding bridge: a short ramped deck that hangs off the front (+Y) edge of the
    # platform. Its near-edge overlaps the platform slab so it isn't floating, and
    # the far edge is supported by a stub leg that reaches the ground.
    if resolved.boarding_bridge_enabled:
        bridge_top_z = deck_top_z
        bridge_length_y = 0.40 * scale
        bridge_width_x = 0.60 * scale
        bridge_center_y = (0.82 * scale) / 2.0 + bridge_length_y / 2.0 - 0.02
        support.visual(
            Box((bridge_width_x, bridge_length_y, 0.030)),
            origin=Origin(xyz=(0.0, bridge_center_y, bridge_top_z - 0.015)),
            material=material,
            name="boarding_bridge", material_class_id="metal.patterned_sheet_panel",
        )
        # Two corner posts down to the ground prevent the bridge from cantilevering.
        post_height = bridge_top_z - 0.030
        for x_sign, side in ((-1.0, "left"), (1.0, "right")):
            support.visual(
                Cylinder(radius=0.014, length=post_height),
                origin=Origin(
                    xyz=(
                        x_sign * (bridge_width_x / 2.0 - 0.030),
                        bridge_center_y + bridge_length_y / 2.0 - 0.030,
                        post_height / 2.0,
                    )
                ),
                material=dark,
                name=f"boarding_bridge_{side}_post", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
            )
    # Loading plinth: a raised platform directly under the bottom-most gondola.
    # We size its height conservatively (LOADING_PLINTH_HEIGHT) so the lowest gondola
    # pose still clears it by GROUND_CLEARANCE -- the axle_z floor already reserved
    # this height during resolve_config.
    if resolved.loading_plinth_enabled:
        plinth_w = 0.40 * scale
        plinth_d = 0.26 * scale
        plinth_h = LOADING_PLINTH_HEIGHT
        support.visual(
            Box((plinth_w, plinth_d, plinth_h)),
            origin=Origin(xyz=(0.0, 0.0, deck_top_z + plinth_h / 2.0)),
            material=material,
            name="loading_plinth", material_class_id="metal.patterned_sheet_panel",
        )
    # Service deck: a narrow walkway hung underneath the axle for inspection.
    # It sits above the platform but must stay clear of the LOWEST wheel hardware
    # that sweeps through the center-bottom. That reach is the gondola pivot bar
    # radius (which, for leveling_arm hangers, is LEVELING_ARM_LENGTH beyond the
    # rim) plus the hanger boss -- NOT merely rim_radius, which is why the deck used
    # to spear the leveling-arm beams.
    if resolved.service_deck_enabled:
        sd_w = 0.32 * scale
        sd_d = 0.14 * scale
        sd_h = 0.012
        sweep_radius = max(resolved.rim_radius, _gondola_pivot_radius(resolved)) + 0.028
        sweep_ceiling = resolved.axle_z - sweep_radius
        sd_z = deck_top_z + 0.40 * scale
        if sd_z + sd_h / 2.0 < sweep_ceiling - 0.020:
            support.visual(
                Box((sd_w, sd_d, sd_h)),
                origin=Origin(xyz=(0.0, 0.0, sd_z + sd_h / 2.0)),
                material=dark,
                name="service_deck", material_class_id="metal.patterned_sheet_panel",
            )


def _add_support_base(
    support,
    resolved: ResolvedFerrisWheelConfig,
    *,
    material,
    dark,
    white,
) -> None:
    _add_platform_base(
        support,
        material=material,
        scale=resolved.support_scale,
        railing_enabled=resolved.railing_enabled,
    )
    _add_optional_platform_extras(
        support,
        resolved,
        material=material,
        dark=dark,
        white=white,
    )


def _build_support_a_frame(
    support,
    resolved: ResolvedFerrisWheelConfig,
    *,
    white,
    dark,
) -> tuple[tuple[float, float, float], float]:
    scale = resolved.support_scale
    bearing_x = 0.155 * scale
    for x, label in ((-bearing_x, "left"), (bearing_x, "right")):
        support.visual(
            Box((0.038 * scale, 0.060 * scale, resolved.axle_z + 0.040 * scale)),
            origin=Origin(xyz=(x, 0.0, resolved.axle_z / 2.0 + 0.020 * scale)),
            material=white,
            name=f"{label}_hidden_core", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
        )
        support.visual(
            Box((0.060 * scale, 0.070 * scale, 0.030 * scale)),
            origin=Origin(xyz=(x, 0.0, resolved.axle_z - 0.055 * scale)),
            material=white,
            name=f"{label}_bearing_web", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
        )

    axle = (0.0, 0.0, resolved.axle_z)
    foot_y = 0.310 * scale
    platform_top_z = 0.085
    brace_z = 0.50 + (resolved.axle_z - DEFAULT_AXLE_Z) * 0.35
    for x, side in ((-bearing_x, "left"), (bearing_x, "right")):
        front_foot = (x, foot_y, platform_top_z)
        rear_foot = (x, -foot_y, platform_top_z)
        top = (x, 0.0, resolved.axle_z)
        _member(
            support,
            front_foot,
            top,
            radius=0.018 * scale,
            material=white,
            name=f"{side}_front_a_leg",
        )
        _member(
            support, rear_foot, top, radius=0.018 * scale, material=white, name=f"{side}_rear_a_leg"
        )
        _member(
            support,
            front_foot,
            (x, 0.0, brace_z),
            radius=0.011 * scale,
            material=white,
            name=f"{side}_front_cross",
        )
        _member(
            support,
            rear_foot,
            (x, 0.0, brace_z),
            radius=0.011 * scale,
            material=white,
            name=f"{side}_rear_cross",
        )
        _member(
            support,
            (x, foot_y * 0.55, brace_z - 0.12 * scale),
            (x, -foot_y * 0.55, brace_z - 0.12 * scale),
            radius=0.010 * scale,
            material=white,
            name=f"{side}_mid_spreader",
        )
        support.visual(
            Box((0.078 * scale, 0.096 * scale, 0.092 * scale)),
            origin=Origin(xyz=(x, 0.0, resolved.axle_z)),
            material=dark,
            name=f"{side}_bearing_block", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
        )
    _member(
        support,
        (-bearing_x, 0.0, resolved.axle_z),
        (bearing_x, 0.0, resolved.axle_z),
        radius=0.020 * scale,
        material=dark,
        name="fixed_axle",
    )
    return axle, bearing_x


def _build_support_truss_tower(
    support,
    resolved: ResolvedFerrisWheelConfig,
    *,
    white,
    dark,
) -> tuple[tuple[float, float, float], float]:
    scale = resolved.support_scale
    bearing_x = 0.155 * scale
    platform_top_z = 0.085
    tower_inset_y = 0.260 * scale
    crown_z = resolved.axle_z - 0.030 * scale
    mid_z = platform_top_z + (crown_z - platform_top_z) * 0.52

    for x, side in ((-bearing_x, "left"), (bearing_x, "right")):
        support.visual(
            Box((0.038 * scale, 0.060 * scale, resolved.axle_z + 0.040 * scale)),
            origin=Origin(xyz=(x, 0.0, resolved.axle_z / 2.0 + 0.020 * scale)),
            material=white,
            name=f"{side}_hidden_core", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
        )
        support.visual(
            Box((0.060 * scale, 0.070 * scale, 0.030 * scale)),
            origin=Origin(xyz=(x, 0.0, resolved.axle_z - 0.055 * scale)),
            material=white,
            name=f"{side}_bearing_web", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
        )
        _member(
            support,
            (x, 0.0, platform_top_z),
            (x, 0.0, resolved.axle_z),
            radius=0.020 * scale,
            material=white,
            name=f"{side}_center_tower_post",
        )
        for y, label in ((tower_inset_y, "front"), (-tower_inset_y, "rear")):
            _member(
                support,
                (x, y, platform_top_z),
                (x, y, crown_z),
                radius=0.014 * scale,
                material=white,
                name=f"{side}_{label}_tower_post",
            )
            _member(
                support,
                (x, y, mid_z),
                (x, 0.0, mid_z),
                radius=0.010 * scale,
                material=white,
                name=f"{side}_{label}_diagonal_brace",
            )
        _member(
            support,
            (x, tower_inset_y, crown_z),
            (x, -tower_inset_y, crown_z),
            radius=0.012 * scale,
            material=white,
            name=f"{side}_tower_spreader",
        )
        _member(
            support,
            (x, tower_inset_y, platform_top_z + 0.10 * scale),
            (x, -tower_inset_y, platform_top_z + 0.10 * scale),
            radius=0.010 * scale,
            material=white,
            name=f"{side}_base_spreader",
        )
        _member(
            support,
            (x, 0.0, crown_z),
            (x, 0.0, resolved.axle_z),
            radius=0.014 * scale,
            material=white,
            name=f"{side}_center_crown_strut",
        )
        support.visual(
            Box((0.078 * scale, 0.120 * scale, 0.092 * scale)),
            origin=Origin(xyz=(x, 0.0, resolved.axle_z)),
            material=dark,
            name=f"{side}_bearing_block", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
        )
    _member(
        support,
        (-bearing_x, 0.0, resolved.axle_z),
        (bearing_x, 0.0, resolved.axle_z),
        radius=0.020 * scale,
        material=dark,
        name="fixed_axle",
    )
    return (0.0, 0.0, resolved.axle_z), bearing_x


def _build_support_inclined_legs(
    support,
    resolved: ResolvedFerrisWheelConfig,
    *,
    white,
    dark,
) -> tuple[tuple[float, float, float], float]:
    scale = resolved.support_scale
    bearing_x = 0.155 * scale
    platform_top_z = 0.085
    foot_y = 0.335 * scale
    axle = (0.0, 0.0, resolved.axle_z)
    shoulder_z = resolved.axle_z * 0.76

    for x, side in ((-bearing_x, "left"), (bearing_x, "right")):
        support.visual(
            Box((0.038 * scale, 0.060 * scale, resolved.axle_z + 0.040 * scale)),
            origin=Origin(xyz=(x, 0.0, resolved.axle_z / 2.0 + 0.020 * scale)),
            material=white,
            name=f"{side}_hidden_core", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
        )
        support.visual(
            Box((0.060 * scale, 0.070 * scale, 0.030 * scale)),
            origin=Origin(xyz=(x, 0.0, resolved.axle_z - 0.055 * scale)),
            material=white,
            name=f"{side}_bearing_web", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
        )
        front_foot = (x, foot_y, platform_top_z)
        rear_foot = (x, -foot_y, platform_top_z)
        top = (x, 0.0, resolved.axle_z)
        shoulder_front = (x, foot_y * 0.36, shoulder_z)
        shoulder_rear = (x, -foot_y * 0.36, shoulder_z)
        _member(
            support,
            front_foot,
            top,
            radius=0.018 * scale,
            material=white,
            name=f"{side}_front_inclined_leg",
        )
        _member(
            support,
            rear_foot,
            top,
            radius=0.018 * scale,
            material=white,
            name=f"{side}_rear_inclined_leg",
        )
        _member(
            support,
            front_foot,
            shoulder_rear,
            radius=0.010 * scale,
            material=white,
            name=f"{side}_cross_diagonal_a",
        )
        _member(
            support,
            rear_foot,
            shoulder_front,
            radius=0.010 * scale,
            material=white,
            name=f"{side}_cross_diagonal_b",
        )
        _member(
            support,
            shoulder_front,
            shoulder_rear,
            radius=0.011 * scale,
            material=white,
            name=f"{side}_shoulder_spreader",
        )
        support.visual(
            Box((0.082 * scale, 0.110 * scale, 0.092 * scale)),
            origin=Origin(xyz=(x, 0.0, resolved.axle_z)),
            material=dark,
            name=f"{side}_bearing_block", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
        )
    _member(
        support,
        (-bearing_x, 0.0, resolved.axle_z),
        (bearing_x, 0.0, resolved.axle_z),
        radius=0.020 * scale,
        material=dark,
        name="fixed_axle",
    )
    return axle, bearing_x


SUPPORT_STYLE_BUILDERS = {
    "a_frame": _build_support_a_frame,
    "truss_tower": _build_support_truss_tower,
    "inclined_legs": _build_support_inclined_legs,
}


def add_gondola_box_cabin(gondola, *, body_mat, trim_mat, glass_mat, index: int) -> None:
    """Default enclosed cabin style. Origin is the hanger pivot."""
    gondola.visual(
        Cylinder(radius=0.010, length=0.145),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=trim_mat,
        name="hanger_pin", material_class_id="metal.paint_coated",
    )
    for x, label in ((-0.052, "rear"), (0.052, "front")):
        gondola.visual(
            Box((0.010, 0.012, 0.155)),
            origin=Origin(xyz=(x, 0.0, -0.077)),
            material=trim_mat,
            name=f"hanger_{label}", material_class_id="metal.paint_coated",
        )
    gondola.visual(
        Box((0.112, 0.118, 0.100)),
        origin=Origin(xyz=(0.0, 0.0, -0.177)),
        material=body_mat,
        name="cabin_body", material_class_id="plastic.opaque_glossy_molded",
    )
    gondola.visual(
        Box((0.126, 0.128, 0.026)),
        origin=Origin(xyz=(0.0, 0.0, -0.107)),
        material=trim_mat,
        name="cabin_roof", material_class_id="metal.paint_coated",
    )
    gondola.visual(
        Box((0.130, 0.132, 0.022)),
        origin=Origin(xyz=(0.0, 0.0, -0.238)),
        material=trim_mat,
        name="cabin_floor", material_class_id="metal.paint_coated",
    )
    for y, label in ((-0.062, "rear"), (0.062, "front")):
        gondola.visual(
            Box((0.038, 0.006, 0.052)),
            origin=Origin(xyz=(-0.028, y, -0.158)),
            material=glass_mat,
            name=f"{label}_window_left", material_class_id="glass.smoked_tinted",
        )
        gondola.visual(
            Box((0.038, 0.006, 0.052)),
            origin=Origin(xyz=(0.028, y, -0.158)),
            material=glass_mat,
            name=f"{label}_window_right", material_class_id="glass.smoked_tinted",
        )
        gondola.visual(
            Box((0.006, 0.008, 0.068)),
            origin=Origin(xyz=(0.0, y, -0.158)),
            material=trim_mat,
            name=f"{label}_center_mullion", material_class_id="metal.paint_coated",
        )
    gondola.visual(
        Box((0.130, 0.012, 0.016)),
        origin=Origin(xyz=(0.0, 0.059, -0.214)),
        material=trim_mat,
        name="front_guard_bar", material_class_id="metal.paint_coated",
    )
    gondola.visual(
        Box((0.130, 0.012, 0.016)),
        origin=Origin(xyz=(0.0, -0.059, -0.214)),
        material=trim_mat,
        name="rear_guard_bar", material_class_id="metal.paint_coated",
    )


def add_gondola_open_basket(gondola, *, body_mat, trim_mat, glass_mat, index: int) -> None:
    """Open basket style: low floor, railings, and benches instead of a closed cabin."""
    gondola.visual(
        Cylinder(radius=0.010, length=0.145),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=trim_mat,
        name="hanger_pin", material_class_id="metal.paint_coated",
    )
    for x, label in ((-0.052, "rear"), (0.052, "front")):
        gondola.visual(
            Box((0.010, 0.012, 0.198)),
            origin=Origin(xyz=(x, 0.0, -0.099)),
            material=trim_mat,
            name=f"hanger_{label}", material_class_id="metal.paint_coated",
        )
    for x, side in ((-0.052, "rear"), (0.052, "front")):
        for y, face in ((0.034, "front"), (-0.034, "rear")):
            gondola.visual(
                Box((0.008, 0.070, 0.012)),
                origin=Origin(xyz=(x, y, -0.150)),
                material=trim_mat,
                name=f"{side}_{face}_top_spreader", material_class_id="metal.paint_coated",
            )
    gondola.visual(
        Box((0.140, 0.136, 0.022)),
        origin=Origin(xyz=(0.0, 0.0, -0.230)),
        material=body_mat,
        name="basket_floor", material_class_id="plastic.opaque_glossy_molded",
    )
    for y, label in ((0.064, "front"), (-0.064, "rear")):
        gondola.visual(
            Box((0.138, 0.010, 0.016)),
            origin=Origin(xyz=(0.0, y, -0.176)),
            material=trim_mat,
            name=f"{label}_top_rail", material_class_id="metal.paint_coated",
        )
        gondola.visual(
            Box((0.138, 0.010, 0.014)),
            origin=Origin(xyz=(0.0, y, -0.208)),
            material=trim_mat,
            name=f"{label}_lower_rail", material_class_id="metal.paint_coated",
        )
    for x, label in ((-0.064, "rear"), (0.064, "front")):
        gondola.visual(
            Box((0.010, 0.126, 0.016)),
            origin=Origin(xyz=(x, 0.0, -0.176)),
            material=trim_mat,
            name=f"{label}_side_rail", material_class_id="metal.paint_coated",
        )
    for x, side in ((-0.052, "rear"), (0.052, "front")):
        for y, face in ((0.058, "front"), (-0.058, "rear")):
            gondola.visual(
                Box((0.008, 0.008, 0.088)),
                origin=Origin(xyz=(x, y, -0.186)),
                material=trim_mat,
                name=f"{side}_{face}_hanger_leg", material_class_id="metal.paint_coated",
            )
    for x in (-0.046, 0.046):
        for y, label in ((0.064, "front"), (-0.064, "rear")):
            gondola.visual(
                Box((0.008, 0.010, 0.065)),
                origin=Origin(xyz=(x, y, -0.204)),
                material=trim_mat,
                name=f"{label}_stanchion_{'left' if x < 0 else 'right'}", material_class_id="metal.paint_coated",
            )
    for y, label in ((0.030, "front"), (-0.030, "rear")):
        gondola.visual(
            Box((0.104, 0.020, 0.018)),
            origin=Origin(xyz=(0.0, y, -0.196)),
            material=body_mat,
            name=f"{label}_bench", material_class_id="plastic.opaque_glossy_molded",
        )
        for x, side in ((-0.040, "left"), (0.040, "right")):
            gondola.visual(
                Box((0.010, 0.010, 0.046)),
                origin=Origin(xyz=(x, y, -0.220)),
                material=trim_mat,
                name=f"{label}_{side}_bench_leg", material_class_id="metal.paint_coated",
            )


def add_gondola_glass_capsule(gondola, *, body_mat, trim_mat, glass_mat, index: int) -> None:
    """Transparent capsule style with a larger panoramic shell and rounded end caps."""
    gondola.visual(
        Cylinder(radius=0.010, length=0.145),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=trim_mat,
        name="hanger_pin", material_class_id="metal.paint_coated",
    )
    for x, label in ((-0.052, "rear"), (0.052, "front")):
        gondola.visual(
            Box((0.010, 0.012, 0.132)),
            origin=Origin(xyz=(x, 0.0, -0.066)),
            material=trim_mat,
            name=f"hanger_{label}", material_class_id="metal.paint_coated",
        )
    gondola.visual(
        Box((0.120, 0.104, 0.058)),
        origin=Origin(xyz=(0.0, 0.0, -0.168)),
        material=glass_mat,
        name="panoramic_glass_shell", material_class_id="glass.smoked_tinted",
    )
    gondola.visual(
        Cylinder(radius=0.052, length=0.010),
        origin=Origin(xyz=(-0.064, 0.0, -0.168), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=glass_mat,
        name="rear_round_end", material_class_id="glass.smoked_tinted",
    )
    gondola.visual(
        Cylinder(radius=0.052, length=0.010),
        origin=Origin(xyz=(0.064, 0.0, -0.168), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=glass_mat,
        name="front_round_end", material_class_id="glass.smoked_tinted",
    )
    gondola.visual(
        Box((0.138, 0.126, 0.018)),
        origin=Origin(xyz=(0.0, 0.0, -0.226)),
        material=trim_mat,
        name="capsule_floor_ring", material_class_id="metal.paint_coated",
    )
    gondola.visual(
        Box((0.132, 0.118, 0.014)),
        origin=Origin(xyz=(0.0, 0.0, -0.118)),
        material=trim_mat,
        name="capsule_roof_frame", material_class_id="metal.paint_coated",
    )
    for x, label in ((-0.064, "rear"), (0.064, "front")):
        gondola.visual(
            Cylinder(radius=0.056, length=0.006),
            origin=Origin(xyz=(x, 0.0, -0.168), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=trim_mat,
            name=f"{label}_end_frame", material_class_id="metal.paint_coated",
        )
    for y, label in ((0.056, "front"), (-0.056, "rear")):
        gondola.visual(
            Box((0.126, 0.008, 0.012)),
            origin=Origin(xyz=(0.0, y, -0.126)),
            material=trim_mat,
            name=f"{label}_upper_window_frame", material_class_id="metal.paint_coated",
        )
        gondola.visual(
            Box((0.126, 0.008, 0.012)),
            origin=Origin(xyz=(0.0, y, -0.212)),
            material=trim_mat,
            name=f"{label}_lower_window_frame", material_class_id="metal.paint_coated",
        )
        for x, side in ((-0.040, "left"), (0.040, "right")):
            gondola.visual(
                Box((0.006, 0.008, 0.088)),
                origin=Origin(xyz=(x, y, -0.168)),
                material=trim_mat,
                name=f"{label}_{side}_mullion", material_class_id="metal.paint_coated",
            )
    for x, side in ((-0.050, "rear"), (0.050, "front")):
        gondola.visual(
            Box((0.010, 0.112, 0.010)),
            origin=Origin(xyz=(x, 0.0, -0.112)),
            material=trim_mat,
            name=f"{side}_yoke_crossbar", material_class_id="metal.paint_coated",
        )
        for y, face in ((0.052, "front"), (-0.052, "rear")):
            gondola.visual(
                Box((0.010, 0.010, 0.090)),
                origin=Origin(xyz=(x, y, -0.154)),
                material=trim_mat,
                name=f"{side}_{face}_yoke_leg", material_class_id="metal.paint_coated",
            )
    gondola.visual(
        Box((0.092, 0.024, 0.018)),
        origin=Origin(xyz=(0.0, 0.0, -0.200)),
        material=body_mat,
        name="center_bench", material_class_id="plastic.opaque_glossy_molded",
    )
    for x, side in ((-0.032, "left"), (0.032, "right")):
        gondola.visual(
            Box((0.008, 0.010, 0.044)),
            origin=Origin(xyz=(x, 0.0, -0.222)),
            material=trim_mat,
            name=f"{side}_bench_leg", material_class_id="metal.paint_coated",
        )


def add_gondola_bucket_seat(gondola, *, body_mat, trim_mat, glass_mat, index: int) -> None:
    """Open bucket seat adapted from high-quality fairground wheel samples."""
    gondola.visual(
        Cylinder(radius=0.010, length=0.145),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=trim_mat,
        name="hanger_pin", material_class_id="metal.paint_coated",
    )
    for x, label in ((-0.056, "rear"), (0.056, "front")):
        gondola.visual(
            Box((0.010, 0.012, 0.178)),
            origin=Origin(xyz=(x, 0.0, -0.088)),
            material=trim_mat,
            name=f"hanger_{label}", material_class_id="metal.paint_coated",
        )
    gondola.visual(
        Box((0.156, 0.146, 0.024)),
        origin=Origin(xyz=(0.0, 0.0, -0.250)),
        material=body_mat,
        name="bucket_floor", material_class_id="plastic.opaque_glossy_molded",
    )
    gondola.visual(
        Box((0.042, 0.140, 0.088)),
        origin=Origin(xyz=(-0.074, 0.0, -0.206)),
        material=body_mat,
        name="bucket_back", material_class_id="plastic.opaque_glossy_molded",
    )
    gondola.visual(
        Box((0.038, 0.140, 0.070)),
        origin=Origin(xyz=(0.074, 0.0, -0.214)),
        material=body_mat,
        name="bucket_front_lip", material_class_id="plastic.opaque_glossy_molded",
    )
    for y, label in ((-0.068, "rear"), (0.068, "front")):
        gondola.visual(
            Box((0.136, 0.010, 0.062)),
            origin=Origin(xyz=(0.0, y, -0.212)),
            material=trim_mat,
            name=f"{label}_bucket_side", material_class_id="metal.paint_coated",
        )
    gondola.visual(
        Box((0.122, 0.010, 0.014)),
        origin=Origin(xyz=(0.0, 0.0, -0.168)),
        material=trim_mat,
        name="safety_bar", material_class_id="metal.paint_coated",
    )
    for x, side in ((-0.030, "left"), (0.030, "right")):
        gondola.visual(
            Box((0.008, 0.012, 0.044)),
            origin=Origin(xyz=(x, 0.0, -0.188)),
            material=trim_mat,
            name=f"{side}_safety_bar_stanchion", material_class_id="metal.paint_coated",
        )


def add_gondola_rounded_pod(gondola, *, body_mat, trim_mat, glass_mat, index: int) -> None:
    """Rounded pod inspired by robust capsule/pod wheel records."""
    gondola.visual(
        Cylinder(radius=0.010, length=0.145),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=trim_mat,
        name="hanger_pin", material_class_id="metal.paint_coated",
    )
    for x, label in ((-0.052, "rear"), (0.052, "front")):
        gondola.visual(
            Box((0.010, 0.012, 0.142)),
            origin=Origin(xyz=(x, 0.0, -0.071)),
            material=trim_mat,
            name=f"hanger_{label}", material_class_id="metal.paint_coated",
        )
    gondola.visual(
        Cylinder(radius=0.060, length=0.114),
        origin=Origin(xyz=(0.0, 0.0, -0.165), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=body_mat,
        name="pod_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    gondola.visual(
        Cylinder(radius=0.060, length=0.008),
        origin=Origin(xyz=(-0.061, 0.0, -0.165), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=trim_mat,
        name="rear_pod_endcap", material_class_id="metal.paint_coated",
    )
    gondola.visual(
        Cylinder(radius=0.060, length=0.008),
        origin=Origin(xyz=(0.061, 0.0, -0.165), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=trim_mat,
        name="front_pod_endcap", material_class_id="metal.paint_coated",
    )
    gondola.visual(
        Box((0.130, 0.116, 0.020)),
        origin=Origin(xyz=(0.0, 0.0, -0.230)),
        material=trim_mat,
        name="pod_floor_ring", material_class_id="metal.paint_coated",
    )
    for y, label in ((0.056, "front"), (-0.056, "rear")):
        gondola.visual(
            Box((0.120, 0.006, 0.060)),
            origin=Origin(xyz=(0.0, y, -0.168)),
            material=glass_mat,
            name=f"{label}_pod_glass", material_class_id="glass.smoked_tinted",
        )
    gondola.visual(
        Box((0.084, 0.020, 0.018)),
        origin=Origin(xyz=(0.0, 0.0, -0.206)),
        material=body_mat,
        name="pod_bench", material_class_id="plastic.opaque_glossy_molded",
    )


GONDOLA_STYLE_BUILDERS = {
    "box_cabin": add_gondola_box_cabin,
    "open_basket": add_gondola_open_basket,
    "glass_capsule": add_gondola_glass_capsule,
    "bucket_seat": add_gondola_bucket_seat,
    "rounded_pod": add_gondola_rounded_pod,
}


def _gondola_angle(index0: int, num_gondolas: int) -> float:
    """Wheel-frame angle of gondola i (0-based). Gondolas start at the bottom."""
    return (2.0 * math.pi * index0) / num_gondolas - math.pi / 2.0


def _add_twin_ring_rim(wheel, resolved: ResolvedFerrisWheelConfig, *, white) -> None:
    segs = max(20, resolved.spoke_count)
    inner_radius = max(resolved.rim_radius * 0.86, resolved.rim_radius - 0.12)
    for i in range(segs):
        a0 = 2.0 * math.pi * i / segs
        a1 = 2.0 * math.pi * ((i + 1) % segs) / segs
        for x, side in ((-resolved.wheel_half_width, "left"), (resolved.wheel_half_width, "right")):
            _member(
                wheel,
                _wheel_point(resolved.rim_radius, a0, x),
                _wheel_point(resolved.rim_radius, a1, x),
                radius=0.012,
                material=white,
                name=f"{side}_outer_rim_segment_{i}",
            )
            _member(
                wheel,
                _wheel_point(inner_radius, a0, x),
                _wheel_point(inner_radius, a1, x),
                radius=0.0085,
                material=white,
                name=f"{side}_inner_rim_segment_{i}",
            )
    # No explicit outer cross bridges: the left and right outer rings are already tied
    # across the width by the hub (via the crossing spokes) and by every gondola's
    # pivot-bar/hanger struts, and the inner ring is tied in by the spokes that cross
    # it. Adding a full-width bar at each gondola angle only created a bar sitting in
    # the cabin's swing corridor (rim_bridge vs cabin floor/hanger overlaps).


def _gondola_pivot_radius(resolved: ResolvedFerrisWheelConfig) -> float:
    if resolved.hanger_style == "between_rims":
        return max(resolved.rim_radius * 0.86, resolved.rim_radius - 0.12)
    if resolved.hanger_style == "yoke_fork":
        return resolved.rim_radius - 0.018
    if resolved.hanger_style == "leveling_arm":
        # The actual swing pivot sits LEVELING_ARM_LENGTH outside the rim, dangled from a
        # mount_pad on the outer rim. axle_z resolved with this drop reserved.
        return resolved.rim_radius + LEVELING_ARM_LENGTH
    return resolved.rim_radius


def _cabin_rect_corners(
    pivot_yz: tuple[float, float], theta: float, hw: float, drop: float
) -> tuple[tuple[float, float], ...]:
    """The cabin's bounding rectangle in the swing (Y-Z) plane after swinging by
    ``theta`` about the pivot. The real cabin (windows, tapered hanger) fits inside
    this box, so clearances computed against it are a lower bound on the truth."""
    c = math.cos(theta)
    s = math.sin(theta)
    px, pz = pivot_yz
    corners = ((-hw, 0.0), (hw, 0.0), (hw, -drop), (-hw, -drop))
    return tuple((px + y * c - z * s, pz + y * s + z * c) for y, z in corners)


def _pt_seg_dist(p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length2 = dx * dx + dy * dy
    if length2 <= 1e-18:
        return math.hypot(p[0] - ax, p[1] - ay)
    t = ((p[0] - ax) * dx + (p[1] - ay) * dy) / length2
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def _orient(a, b, c) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _seg_seg_dist(p1, p2, p3, p4) -> float:
    # Proper crossing => zero distance.
    d1 = _orient(p3, p4, p1)
    d2 = _orient(p3, p4, p2)
    d3 = _orient(p1, p2, p3)
    d4 = _orient(p1, p2, p4)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    return min(
        _pt_seg_dist(p1, p3, p4),
        _pt_seg_dist(p2, p3, p4),
        _pt_seg_dist(p3, p1, p2),
        _pt_seg_dist(p4, p1, p2),
    )


def _rect_rect_dist(ra: tuple, rb: tuple) -> float:
    best = float("inf")
    for i in range(4):
        a1, a2 = ra[i], ra[(i + 1) % 4]
        for j in range(4):
            b1, b2 = rb[j], rb[(j + 1) % 4]
            d = _seg_seg_dist(a1, a2, b1, b2)
            if d < best:
                best = d
                if best == 0.0:
                    return 0.0
    return best


def gondola_swing_limit(resolved: ResolvedFerrisWheelConfig) -> float:
    """Largest symmetric free-swing amplitude (rad) that keeps two ADJACENT cabins
    at their worst-case opposing swings >= GONDOLA_SWING_CLEARANCE apart.

    Derived from the spoke pitch (2*pi/num_gondolas), the pivot radius, and the
    cabin bounding box, so a denser wheel (or a bigger cabin) is allowed less
    swing. counter_rotate_mimic wheels keep the full range: every gondola turns by
    the same -wheel_rotation, so they never approach one another."""
    if resolved.gondola_motion_mode == "counter_rotate_mimic":
        return 3.14
    n = resolved.num_gondolas
    pivot_radius = _gondola_pivot_radius(resolved)
    prof = GONDOLA_COLLISION_PROFILES[resolved.gondola_style]
    hw = prof.width_y / 2.0
    drop = prof.lowest_point_below_pivot
    # Every cabin hangs toward the wheel's -Z (a FIXED direction), so the pair
    # geometry is NOT rotation-invariant: a pair straddling the top closes up as it
    # swings, a pair at the side stacks vertically. Enumerate the real gondola
    # angles (2*pi*i/n - pi/2) and take the worst adjacent pair.
    angles = [_gondola_angle(i, n) for i in range(n)]
    pivots = [(pivot_radius * math.cos(a), pivot_radius * math.sin(a)) for a in angles]

    def slack(amp: float) -> float:
        if amp <= 0.0:
            thetas = (0.0,)
        else:
            thetas = tuple(-amp + 2.0 * amp * k / 12.0 for k in range(13))
        rects = [[_cabin_rect_corners(p, t, hw, drop) for t in thetas] for p in pivots]
        result = float("inf")
        for i in range(n):
            nxt = (i + 1) % n
            for ra in rects[i]:
                for rb in rects[nxt]:
                    d = _rect_rect_dist(ra, rb) - GONDOLA_SWING_CLEARANCE
                    if d < result:
                        result = d
        return result

    best = 0.0
    amp = 0.0
    step = 0.05
    while amp <= GONDOLA_SWING_MAX + 1e-9:
        if slack(amp) >= 0.0:
            best = amp
        else:
            break
        amp += step
    return round(best, 3)


def _add_gondola_mounting(
    wheel,
    resolved: ResolvedFerrisWheelConfig,
    *,
    angle: float,
    index: int,
    white,
    dark,
) -> tuple[float, float, float]:
    pivot_radius = _gondola_pivot_radius(resolved)
    p0 = _wheel_point(pivot_radius, angle, -resolved.wheel_half_width)
    p1 = _wheel_point(pivot_radius, angle, resolved.wheel_half_width)
    anchor_name = f"gondola_pivot_bar_{index}"

    if resolved.hanger_style == "pivot_bar":
        _member(wheel, p0, p1, radius=0.008, material=white, name=anchor_name)
    elif resolved.hanger_style == "yoke_fork":
        _member(wheel, p0, p1, radius=0.0072, material=white, name=anchor_name)
        for point, side in ((p0, "rear"), (p1, "front")):
            wheel.visual(
                Box((0.028, 0.014, 0.060)),
                origin=Origin(
                    xyz=(point[0], point[1] * 0.996, point[2] * 0.996),
                    rpy=(0.0, 0.0, math.atan2(point[2], point[1])),
                ),
                material=dark,
                name=f"{side}_fork_cheek_{index}", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
            )
    elif resolved.hanger_style == "leveling_arm":
        # Arm reaches from the outer rim outward to the pivot bar; the swing pivot
        # therefore sits LEVELING_ARM_LENGTH past the rim. mount_pad anchors the arm
        # to the rim so nothing hangs in mid-air.
        rim0 = _wheel_point(resolved.rim_radius, angle, -resolved.wheel_half_width)
        rim1 = _wheel_point(resolved.rim_radius, angle, resolved.wheel_half_width)
        _member(wheel, p0, p1, radius=0.0078, material=white, name=anchor_name)
        _member(wheel, rim0, p0, radius=0.0072, material=white, name=f"rear_arm_beam_{index}")
        _member(wheel, rim1, p1, radius=0.0072, material=white, name=f"front_arm_beam_{index}")
        for point, side in ((rim0, "rear"), (rim1, "front")):
            wheel.visual(
                Box((0.034, 0.014, 0.034)),
                origin=Origin(
                    xyz=(point[0], point[1] * 0.985, point[2] * 0.985),
                    rpy=(0.0, 0.0, math.atan2(point[2], point[1])),
                ),
                material=dark,
                name=f"{side}_mount_pad_{index}", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
            )
    else:
        outer0 = _wheel_point(resolved.rim_radius, angle, -resolved.wheel_half_width)
        outer1 = _wheel_point(resolved.rim_radius, angle, resolved.wheel_half_width)
        _member(wheel, p0, p1, radius=0.0070, material=white, name=anchor_name)
        # Two radial struts (one per rim face) tie the inboard pivot bar back to the
        # outer rim -- this is the whole between-rims connection. We deliberately do
        # NOT bridge outer0->outer1 across the full width: at the wheel's bottom that
        # bridge lies directly under the pivot, in the gondola's straight-down hang
        # corridor, so the cabin hanger would spear it. The struts sit outboard in X
        # (at +/- wheel_half_width) clear of the thin central hanger.
        _member(wheel, outer0, p0, radius=0.0060, material=white, name=f"rear_hanger_strut_{index}")
        _member(
            wheel,
            outer1,
            p1,
            radius=0.0060,
            material=white,
            name=f"front_hanger_strut_{index}",
        )

    wheel.visual(
        Cylinder(radius=0.020, length=0.018),
        origin=Origin(xyz=p0, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=dark,
        name=f"rear_hanger_boss_{index}", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
    )
    wheel.visual(
        Cylinder(radius=0.020, length=0.018),
        origin=Origin(xyz=p1, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=dark,
        name=f"front_hanger_boss_{index}", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
    )
    return _wheel_point(pivot_radius, angle, 0.0)


def build_ferris_wheel(
    config: FerrisWheelConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or FerrisWheelConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-ferris-assets-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)

    frame_pal = FRAME_PALETTES[resolved.frame_palette]
    cabin_pal = CABIN_PALETTES[resolved.cabin_palette]
    glass_rgba = GLASS_TINTS[resolved.glass_tint]
    white = model.material(f"frame_main_{resolved.frame_palette}", rgba=frame_pal.frame)
    dark = model.material(f"frame_accent_{resolved.frame_palette}", rgba=frame_pal.accent)
    platform_mat = model.material(
        f"platform_panels_{resolved.frame_palette}", rgba=frame_pal.platform
    )
    cabin_mat = model.material(f"cabin_body_{resolved.cabin_palette}", rgba=cabin_pal.body)
    trim_mat = model.material(f"cabin_trim_{resolved.cabin_palette}", rgba=cabin_pal.trim)
    glass = model.material(f"glass_{resolved.glass_tint}", rgba=glass_rgba)
    gondola_palette_rgba = GONDOLA_PALETTES[resolved.gondola_palette]
    gondola_palette_mats: list = []
    for idx, rgba in enumerate(gondola_palette_rgba):
        gondola_palette_mats.append(
            model.material(f"gondola_palette_{resolved.gondola_palette}_{idx}", rgba=rgba)
        )

    rim_mesh = None
    inner_rim_mesh = None
    if resolved.rim_style in {"single_torus", "double_torus", "concentric_double"}:
        rim_mesh = _mesh(
            assets,
            "large_outer_rim.obj",
            TorusGeometry(
                radius=resolved.rim_radius,
                tube=0.018,
                radial_segments=18,
                tubular_segments=144,
            ).rotate_y(math.pi / 2.0),
        )
    if resolved.rim_style in {"double_torus", "concentric_double"}:
        inner_rim_mesh = _mesh(
            assets,
            "inner_stiffening_rim.obj",
            TorusGeometry(
                radius=resolved.inner_rim_radius,
                tube=0.010,
                radial_segments=14,
                tubular_segments=128,
            ).rotate_y(math.pi / 2.0),
        )

    support = model.part("support_frame")
    _add_support_base(
        support,
        resolved,
        material=platform_mat,
        dark=dark,
        white=white,
    )
    support_builder = SUPPORT_STYLE_BUILDERS[resolved.support_style]
    axle, _bearing_x = support_builder(support, resolved, white=white, dark=dark)

    hub_length, hub_cap_x, hub_cap_radius, central_hub_radius = hub_geometry(
        resolved.wheel_half_width
    )
    hub_cap_length = 0.026 * (resolved.wheel_half_width / DEFAULT_WHEEL_HALF_WIDTH)

    wheel = model.part("wheel")
    if resolved.rim_style == "twin_rings":
        _add_twin_ring_rim(wheel, resolved, white=white)
    else:
        for x, label in (
            (-resolved.wheel_half_width, "left"),
            (resolved.wheel_half_width, "right"),
        ):
            wheel.visual(
                rim_mesh,
                origin=Origin(xyz=(x, 0.0, 0.0)),
                material=white,
                name=f"{label}_outer_rim", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
            )
            if resolved.rim_style in {"double_torus", "concentric_double"}:
                wheel.visual(
                    inner_rim_mesh,
                    origin=Origin(xyz=(x, 0.0, 0.0)),
                    material=white,
                    name=f"{label}_inner_rim", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
                )
        if resolved.rim_style == "concentric_double":
            # Radial struts so the inner ring isn't floating relative to the outer rim.
            strut_count = max(8, resolved.num_gondolas)
            for i in range(strut_count):
                a = 2.0 * math.pi * i / strut_count
                for x, side in (
                    (-resolved.wheel_half_width, "rear"),
                    (resolved.wheel_half_width, "front"),
                ):
                    _member(
                        wheel,
                        _wheel_point(resolved.inner_rim_radius, a, x),
                        _wheel_point(resolved.rim_radius, a, x),
                        radius=0.0058,
                        material=white,
                        name=f"{side}_concentric_strut_{i}",
                    )
    wheel.visual(
        Cylinder(radius=central_hub_radius, length=hub_length),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=dark,
        name="central_hub", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
    )
    wheel.visual(
        Cylinder(radius=hub_cap_radius, length=hub_cap_length),
        origin=Origin(xyz=(hub_cap_x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=white,
        name="front_hub_cap", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
    )
    wheel.visual(
        Cylinder(radius=hub_cap_radius, length=hub_cap_length),
        origin=Origin(xyz=(-hub_cap_x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=white,
        name="rear_hub_cap", material_class_id=("metal.steel_galvanized" if resolved.frame_palette == "industrial_galvanized" else "metal.paint_coated"),
    )

    for i in range(resolved.spoke_count):
        angle = (2.0 * math.pi * i) / resolved.spoke_count
        for x, side in ((-resolved.wheel_half_width, "rear"), (resolved.wheel_half_width, "front")):
            # Run the spoke tip INTO the rim tube (rim - 0.006), not just short of it.
            # A spoke points radially, so its cross-section radius spreads sideways,
            # not outward -- ending at rim - 0.020 leaves the flat tip ~2 mm shy of
            # the tube surface, and mesh tessellation makes that a hit-or-miss island.
            _member(
                wheel,
                (x, 0.0, 0.0),
                _wheel_point(resolved.rim_radius - 0.006, angle, x),
                radius=0.0065 if i % 2 else 0.008,
                material=white,
                name=f"{side}_spoke_{i}",
            )
    gondola_pivots: dict[int, tuple[float, float, float]] = {}
    for i in range(resolved.num_gondolas):
        angle = _gondola_angle(i, resolved.num_gondolas)
        gondola_pivots[i + 1] = _add_gondola_mounting(
            wheel,
            resolved,
            angle=angle,
            index=i + 1,
            white=white,
            dark=dark,
        )

    model.articulation(
        "wheel_rotation",
        ArticulationType.REVOLUTE,
        parent=support,
        child=wheel,
        origin=Origin(xyz=axle),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=250.0, velocity=0.35, lower=0.0, upper=6.28),
    )

    gondola_builder = GONDOLA_STYLE_BUILDERS[resolved.gondola_style]
    gondola_swing = gondola_swing_limit(resolved)
    for i in range(1, resolved.num_gondolas + 1):
        gondola = model.part(f"gondola_{i}")
        if gondola_palette_mats:
            this_body_mat = gondola_palette_mats[(i - 1) % len(gondola_palette_mats)]
        else:
            this_body_mat = cabin_mat
        gondola_builder(
            gondola, body_mat=this_body_mat, trim_mat=trim_mat, glass_mat=glass, index=i
        )
        pivot = gondola_pivots[i]
        model.articulation(
            f"gondola_pivot_{i}",
            ArticulationType.REVOLUTE,
            parent=wheel,
            child=gondola,
            origin=Origin(xyz=pivot),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=24.0, velocity=1.0, lower=-gondola_swing, upper=gondola_swing
            ),
            mimic=(
                Mimic(joint="wheel_rotation", multiplier=-1.0, offset=0.0)
                if resolved.gondola_motion_mode == "counter_rotate_mimic"
                else None
            ),
        )
    return model


def run_ferris_wheel_tests(
    object_model: ArticulatedObject, config: FerrisWheelConfig
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)
    support = object_model.get_part("support_frame")
    wheel = object_model.get_part("wheel")
    wheel_joint = object_model.get_articulation("wheel_rotation")
    # Single source of truth for the swing range: build and tests both read it from
    # gondola_swing_limit, so the derived per-config clearance limit and the asserted
    # limit can never drift apart.
    expected_swing = gondola_swing_limit(resolved)

    for elem in ("central_hub", "front_hub_cap", "rear_hub_cap"):
        ctx.allow_overlap(
            wheel,
            support,
            elem_a=elem,
            elem_b="fixed_axle",
            reason="The rotating hub is carried on the fixed axle.",
        )
    for elem, bearing in (
        ("rear_hub_cap", "left_bearing_block"),
        ("central_hub", "left_bearing_block"),
        ("central_hub", "right_bearing_block"),
        ("front_hub_cap", "right_bearing_block"),
    ):
        ctx.allow_overlap(
            wheel,
            support,
            elem_a=elem,
            elem_b=bearing,
            reason="The hub assembly is captured by the bearing support.",
        )
    for elem, bearing in (
        ("rear_hub_cap", "left_bearing_web"),
        ("front_hub_cap", "right_bearing_web"),
        ("rear_hub_cap", "left_hidden_core"),
        ("front_hub_cap", "right_hidden_core"),
    ):
        ctx.allow_overlap(
            wheel,
            support,
            elem_a=elem,
            elem_b=bearing,
            reason="The hub assembly is captured by the bearing support.",
        )
    if resolved.support_style == "truss_tower":
        for elem in ("central_hub", "front_hub_cap", "rear_hub_cap"):
            for support_elem in (
                "left_center_tower_post",
                "right_center_tower_post",
                "left_center_crown_strut",
                "right_center_crown_strut",
            ):
                ctx.allow_overlap(
                    wheel,
                    support,
                    elem_a=elem,
                    elem_b=support_elem,
                    reason="The truss crown and center posts capture the rotating hub assembly.",
                )
    for spoke_index in range(resolved.spoke_count):
        ctx.allow_overlap(
            wheel,
            support,
            elem_a=f"rear_spoke_{spoke_index}",
            elem_b="fixed_axle",
            reason="Rear spoke root passes through the central axle/hub region.",
        )
        ctx.allow_overlap(
            wheel,
            support,
            elem_a=f"front_spoke_{spoke_index}",
            elem_b="fixed_axle",
            reason="Front spoke root passes through the central axle/hub region.",
        )
        # Each spoke roots at the hub end (x = +/- wheel_half_width), which sits
        # inside the bearing block that carries the rotating hub -- the same capture
        # the hub caps and central hub are already allowed to make. When the sampled
        # wheel_half_width lands within the bearing-block footprint, the rear/front
        # spoke roots engage the near-side block; that is the bearing seat, not 穿模.
        ctx.allow_overlap(
            wheel,
            support,
            elem_a=f"rear_spoke_{spoke_index}",
            elem_b="left_bearing_block",
            reason="Rear spoke roots seat into the hub bearing block that carries them.",
        )
        ctx.allow_overlap(
            wheel,
            support,
            elem_a=f"front_spoke_{spoke_index}",
            elem_b="right_bearing_block",
            reason="Front spoke roots seat into the hub bearing block that carries them.",
        )
    for i in range(1, resolved.num_gondolas + 1):
        gondola = object_model.get_part(f"gondola_{i}")
        joint = object_model.get_articulation(f"gondola_pivot_{i}")
        for elem in ("hanger_pin", "hanger_rear", "hanger_front"):
            ctx.allow_overlap(
                gondola,
                wheel,
                elem_a=elem,
                elem_b=f"gondola_pivot_bar_{i}",
                reason="The gondola hanger is captured on the pivot bar.",
            )
        ctx.check(
            f"gondola_{i}_range",
            joint.motion_limits is not None
            and abs(joint.motion_limits.lower + expected_swing) < 1e-6
            and abs(joint.motion_limits.upper - expected_swing) < 1e-6,
        )
        if resolved.gondola_motion_mode == "counter_rotate_mimic":
            ctx.check(
                f"gondola_{i}_mimic",
                joint.mimic is not None
                and joint.mimic.joint == "wheel_rotation"
                and abs((joint.mimic.multiplier or 0.0) + 1.0) < 1e-6,
            )
        else:
            ctx.check(f"gondola_{i}_no_mimic", joint.mimic is None)

    ctx.check(
        "wheel_rotation_range",
        wheel_joint.motion_limits is not None
        and abs(wheel_joint.motion_limits.lower - 0.0) < 1e-6
        and abs(wheel_joint.motion_limits.upper - 6.28) < 1e-6,
    )
    ctx.check(
        "configured_gondola_count",
        len([p for p in object_model.parts if p.name.startswith("gondola_")])
        == resolved.num_gondolas,
    )
    ctx.expect_gap(
        wheel,
        support,
        axis="z",
        min_gap=0.18,
        positive_elem="central_hub",
        negative_elem="platform_slab",
        name="hub_high_above_platform",
    )
    ctx.expect_overlap(
        wheel,
        support,
        axes="yz",
        min_overlap=0.030,
        elem_a="central_hub",
        elem_b="fixed_axle",
        name="hub_centered_on_axle",
    )
    with ctx.pose({wheel_joint: 3.14}):
        ctx.check("wheel_can_rotate_half_turn", ctx.part_world_position(wheel) is not None)
    if resolved.gondola_motion_mode == "free_swing":
        swing_test_angle = min(1.2, expected_swing)
        with ctx.pose({"gondola_pivot_1": swing_test_angle}):
            ctx.check(
                "gondola_1_can_swing",
                ctx.part_world_position(object_model.get_part("gondola_1")) is not None,
            )
    else:
        with ctx.pose({"wheel_rotation": math.pi / 2.0}):
            ctx.check(
                "gondola_1_can_counter_rotate",
                ctx.part_world_position(object_model.get_part("gondola_1")) is not None,
            )
    return ctx.report()


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Per-axis module choices for the coverage gate. Reports the RESOLVED config so
    the reported motion mode matches what is actually built (twin_rings coerces
    counter_rotate_mimic -> free_swing). Structural multiplicity (num_gondolas /
    spoke_count) is intentionally omitted -- it is covered by construction, not an
    appearance slot."""
    r = resolve_config(config_from_seed(seed))
    return [
        ("gondola_style", r.gondola_style),
        ("support_style", r.support_style),
        ("rim_style", r.rim_style),
        ("hanger_style", r.hanger_style),
        ("scale_mode", r.scale_mode),
        ("gondola_motion_mode", r.gondola_motion_mode),
        ("railing", "on" if r.railing_enabled else "off"),
        ("frame_palette", r.frame_palette),
        ("cabin_palette", r.cabin_palette),
        ("glass_tint", r.glass_tint),
        ("gondola_palette", r.gondola_palette),
    ]


def build_seeded_ferris_wheel(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_ferris_wheel(config_from_seed(seed), assets=assets)


def with_overrides(config: FerrisWheelConfig, **kwargs: object) -> FerrisWheelConfig:
    return replace(config, **kwargs)
