# SPDX-License-Identifier: Apache-2.0

"""Procedural Articraft template for ``revolving_door``.

Spec source: ``0_revised.md`` section 8 ("Revolving Door | 旋转门").

Identity: a single ``central_post`` carrying 3 or 4 radial wings (equal-angle)
that rotate together as one rigid unit around a vertical axis. The whole rotor
lives inside a static ``outer_drum`` that may be a full cylinder, a partial
cylinder, an open frame, or a square enclosure.

Key invariants (enforced by ``resolve_config`` + ``run_revolving_door_tests``):

* Exactly one CONTINUOUS joint about ``(0, 0, 1)``.
* Exactly one rotor (one central_post + one wing group) per record.
* Wings are placed at angles ``2*pi*i/N`` (within 1 deg) and stay inside the
  drum's inscribed circle.
* All decoration (canopy soffit / crown / skirt / tier_2, top_cap, finial,
  motor_housing, threshold, bearings, header_band, kick_panel, bottom_ring,
  walls, push_bars) is attached as ``parent.visual(...)`` on outer_drum or
  central_post - not as independent parts.
* The static drum hosts both bearings; the rotor's hubs sit exactly above the
  bottom bearing and below the top bearing so nothing inter-penetrates.
* For square drums, ``drum_inner_radius`` is reinterpreted as the inscribed
  circle radius (= half side length); wings still fit cleanly.
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
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
)

# ---------------------------------------------------------------------------
# Discrete parameter literals
# ---------------------------------------------------------------------------

DrumType = Literal["full_cylinder", "partial", "open_frame", "square"]
DoorRadiusClass = Literal["small", "medium", "large"]
DoorHeightClass = Literal["low", "standard", "tall"]
WingMaterial = Literal["glass", "metal_frame", "wood_panel"]
PushBarStyle = Literal["straight", "curved", "d_handle", "none"]
TopCapStyle = Literal["flat", "thick", "decorative"]
BottomRingStyle = Literal["none", "low", "full"]
SensorModuleStyle = Literal["none", "small_blocks"]
MaterialStyle = Literal["glass", "dark_metal", "aluminum", "brass", "bronze", "white_powder"]
CanopyStyle = Literal["single_disc", "soffit_crown", "tiered"]
PanelDensity = Literal["low", "med", "high"]
CanopySkirt = Literal["none", "low", "tall"]
HeaderBand = Literal["none", "narrow", "bold"]
KickPanel = Literal["none", "low", "tall"]
MotorHousing = Literal["none", "top_box"]

# ---------------------------------------------------------------------------
# Bucket continuous ranges
# ---------------------------------------------------------------------------

DOOR_RADIUS_RANGES: dict[DoorRadiusClass, tuple[float, float]] = {
    # Inner radius of the drum (= half side length for square). Wings reach
    # approximately this far minus a small clearance.
    "small": (0.85, 1.05),
    "medium": (1.05, 1.30),
    "large": (1.30, 1.70),
}
DOOR_HEIGHT_RANGES: dict[DoorHeightClass, tuple[float, float]] = {
    # Drum inner height in meters (floor of drum to bottom of canopy soffit).
    "low": (2.00, 2.40),
    "standard": (2.40, 2.90),
    "tall": (2.90, 3.50),
}

# ---------------------------------------------------------------------------
# Geometry constants
# ---------------------------------------------------------------------------

FLOOR_THICKNESS = 0.040
THRESHOLD_THICKNESS = 0.025
BOTTOM_BEARING_THICKNESS = 0.025
TOP_BEARING_THICKNESS = 0.030

# Total canopy depth (soffit + crown + optional tier_2). Top_cap is the thin
# finishing rim above the canopy stack.
CANOPY_TOTAL_THICKNESS_BY_STYLE: dict[TopCapStyle, float] = {
    "flat": 0.110,
    "thick": 0.180,
    "decorative": 0.240,
}
SOFFIT_THICKNESS = 0.040  # thin underside disc when canopy_style != single_disc
TIER_2_THICKNESS = 0.060  # extra small disc on top of crown for ``tiered``
TIER_2_RADIAL_INSET = 0.20  # tier_2 radius shrinks by this much vs crown

TOP_CAP_THICKNESS_BY_STYLE: dict[TopCapStyle, float] = {
    "flat": 0.030,
    "thick": 0.045,
    "decorative": 0.050,
}

PANEL_COUNT_BY_DENSITY: dict[PanelDensity, int] = {
    "low": 6,
    "med": 8,
    "high": 12,
}

CANOPY_SKIRT_HEIGHT: dict[CanopySkirt, float] = {
    "none": 0.0,
    "low": 0.090,
    "tall": 0.180,
}
HEADER_BAND_HEIGHT: dict[HeaderBand, float] = {
    "none": 0.0,
    "narrow": 0.055,
    "bold": 0.120,
}
KICK_PANEL_HEIGHT: dict[KickPanel, float] = {
    "none": 0.0,
    "low": 0.090,
    "tall": 0.180,
}

WING_RADIAL_CLEARANCE = 0.020
WING_PANEL_THICKNESS = 0.035
WING_TOP_BOTTOM_CLEARANCE = 0.030
WING_ROOT_STILE_WIDTH = 0.040
WING_ROOT_STILE_DEPTH = 0.080
CENTRAL_POST_RADIUS_RATIO = 0.050
DRUM_WALL_THICKNESS = 0.040
PUSH_BAR_OFFSET = 0.55
BOTTOM_RING_HEIGHT_LOW = 0.080
BOTTOM_RING_HEIGHT_FULL = 0.200

# Square drum specifics
SQUARE_CORNER_POST_WIDTH = 0.090

# Motor housing dimensions (top_box variant)
MOTOR_HOUSING_RADIUS_RATIO = 0.40  # fraction of canopy outer radius
MOTOR_HOUSING_HEIGHT = 0.160
MOTOR_CAP_HEIGHT = 0.060
MOTOR_CAP_RADIUS_RATIO = 0.55  # fraction of motor_housing radius

# Push bar (d_handle / curved) settings
D_HANDLE_OFFSET = 0.090  # standoff distance from wing face
D_HANDLE_BAR_RADIUS = 0.026
D_HANDLE_BRACKET_RADIUS = 0.013
CURVED_BAR_RADIUS = 0.022
CURVED_BOW_HEIGHT = 0.045  # max outward bow from wing face
CURVED_SEGMENT_COUNT = 5
STRAIGHT_BAR_RADIUS = 0.022
PUSH_BAR_BASE_OFFSET = 0.030  # straight / curved offset from wing face (bar radius bites the panel)

MATERIAL_PALETTES: dict[
    MaterialStyle,
    tuple[
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
    ],
] = {
    "glass": (
        (0.78, 0.80, 0.82, 1.0),
        (0.38, 0.40, 0.44, 1.0),
        (0.55, 0.72, 0.85, 0.30),
    ),
    "dark_metal": (
        (0.20, 0.20, 0.22, 1.0),
        (0.10, 0.10, 0.11, 1.0),
        (0.42, 0.58, 0.72, 0.40),
    ),
    "aluminum": (
        (0.84, 0.85, 0.87, 1.0),
        (0.46, 0.48, 0.50, 1.0),
        (0.62, 0.76, 0.88, 0.30),
    ),
    "brass": (
        (0.78, 0.62, 0.28, 1.0),  # warm polished brass
        (0.52, 0.40, 0.16, 1.0),  # deep brass shadow
        (0.82, 0.84, 0.74, 0.30),
    ),
    "bronze": (
        (0.55, 0.40, 0.22, 1.0),  # mid bronze
        (0.34, 0.24, 0.12, 1.0),  # dark patina bronze
        (0.68, 0.74, 0.78, 0.32),
    ),
    "white_powder": (
        (0.93, 0.93, 0.92, 1.0),  # off-white powder coat
        (0.62, 0.62, 0.60, 1.0),  # light warm gray accent
        (0.66, 0.80, 0.90, 0.28),
    ),
}

WING_BODY_PALETTES: dict[
    WingMaterial, tuple[tuple[float, float, float, float], tuple[float, float, float, float]]
] = {
    "glass": ((0.62, 0.78, 0.88, 0.30), (0.40, 0.42, 0.46, 1.0)),
    "metal_frame": ((0.72, 0.74, 0.76, 1.0), (0.30, 0.32, 0.36, 1.0)),
    "wood_panel": ((0.55, 0.36, 0.20, 1.0), (0.30, 0.20, 0.10, 1.0)),
}


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RevolvingDoorConfig:
    wing_count: int = 3
    drum_type: DrumType = "full_cylinder"
    door_radius: DoorRadiusClass = "medium"
    door_height: DoorHeightClass = "standard"
    wing_material: WingMaterial = "glass"
    push_bar_style: PushBarStyle = "straight"
    top_cap_style: TopCapStyle = "flat"
    bottom_ring: BottomRingStyle = "low"
    sensor_module: SensorModuleStyle = "small_blocks"
    material_style: MaterialStyle = "aluminum"
    canopy_style: CanopyStyle = "soffit_crown"
    panel_density: PanelDensity = "med"
    canopy_skirt: CanopySkirt = "none"
    header_band: HeaderBand = "none"
    kick_panel: KickPanel = "none"
    motor_housing: MotorHousing = "none"
    drum_inner_radius: float | None = None
    drum_inner_height: float | None = None
    name: str = "reference_revolving_door"


@dataclass(frozen=True)
class ResolvedRevolvingDoorConfig:
    wing_count: int
    drum_type: DrumType
    door_radius: DoorRadiusClass
    door_height: DoorHeightClass
    wing_material: WingMaterial
    push_bar_style: PushBarStyle
    top_cap_style: TopCapStyle
    bottom_ring: BottomRingStyle
    sensor_module: SensorModuleStyle
    material_style: MaterialStyle
    canopy_style: CanopyStyle
    panel_density: PanelDensity
    canopy_skirt: CanopySkirt
    header_band: HeaderBand
    kick_panel: KickPanel
    motor_housing: MotorHousing
    # Sizes
    drum_inner_radius: float
    drum_inner_height: float
    central_post_radius: float
    wing_radial_extent: float
    wing_panel_height: float
    # Derived counts / heights
    panel_count: int  # walls / mullions count (0 for open_frame/square w/ different scheme)
    soffit_thickness: float  # 0 if canopy_style == single_disc
    crown_thickness: float
    tier_2_thickness: float  # 0 unless tiered
    top_cap_thickness: float
    bottom_ring_thickness: float
    header_band_height: float
    kick_panel_height: float
    canopy_skirt_height: float
    # Z stack pre-computed (drum-local / world coordinates)
    drum_floor_z: float  # top of floor_disc
    threshold_top_z: float  # top of threshold
    bottom_bearing_top_z: float  # top of bottom_bearing
    wall_outer_bottom_z: float  # bottom of mullions/posts (sits on bottom_ring or floor)
    wall_glass_bottom_z: float  # where glass panels start (above kick_panel)
    wall_glass_top_z: float  # where glass panels end (below header_band)
    soffit_bottom_z: float  # = drum_inner_height (above floor)
    soffit_top_z: float
    crown_bottom_z: float
    crown_top_z: float
    tier_2_bottom_z: float
    tier_2_top_z: float  # == crown_top_z when no tier_2
    top_cap_bottom_z: float
    top_cap_top_z: float
    # Rotor-local offsets
    rotor_floor_offset: float  # rotor link z where bottom_hub bottom sits
    rotor_ceiling_offset: float  # distance from drum_inner_height down to top_hub top
    name: str


# ---------------------------------------------------------------------------
# Seed sampling
# ---------------------------------------------------------------------------


def config_from_seed(seed: int) -> RevolvingDoorConfig:
    """Sample a RevolvingDoorConfig from ``seed``."""

    rng = random.Random(seed)

    wing_count = rng.choices((3, 4), weights=(0.55, 0.45), k=1)[0]

    drum_type: DrumType = rng.choices(
        ("full_cylinder", "partial", "open_frame", "square"),
        weights=(0.40, 0.20, 0.18, 0.22),
        k=1,
    )[0]

    door_radius: DoorRadiusClass = rng.choices(
        ("small", "medium", "large"),
        weights=(0.30, 0.50, 0.20),
        k=1,
    )[0]
    door_height: DoorHeightClass = rng.choices(
        ("low", "standard", "tall"),
        weights=(0.25, 0.55, 0.20),
        k=1,
    )[0]

    wing_material: WingMaterial = rng.choices(
        ("glass", "metal_frame", "wood_panel"),
        weights=(0.55, 0.30, 0.15),
        k=1,
    )[0]
    push_bar_style: PushBarStyle = rng.choices(
        ("straight", "curved", "d_handle", "none"),
        weights=(0.25, 0.20, 0.25, 0.30),
        k=1,
    )[0]
    top_cap_style: TopCapStyle = rng.choices(
        ("flat", "thick", "decorative"),
        weights=(0.40, 0.35, 0.25),
        k=1,
    )[0]
    bottom_ring: BottomRingStyle = rng.choices(
        ("none", "low", "full"),
        weights=(0.30, 0.45, 0.25),
        k=1,
    )[0]
    sensor_module: SensorModuleStyle = rng.choices(
        ("none", "small_blocks"),
        weights=(0.50, 0.50),
        k=1,
    )[0]
    material_style: MaterialStyle = rng.choices(
        ("glass", "dark_metal", "aluminum", "brass", "bronze", "white_powder"),
        weights=(0.20, 0.18, 0.22, 0.12, 0.10, 0.18),
        k=1,
    )[0]
    canopy_style: CanopyStyle = rng.choices(
        ("single_disc", "soffit_crown", "tiered"),
        weights=(0.20, 0.55, 0.25),
        k=1,
    )[0]
    panel_density: PanelDensity = rng.choices(
        ("low", "med", "high"),
        weights=(0.25, 0.45, 0.30),
        k=1,
    )[0]
    canopy_skirt: CanopySkirt = rng.choices(
        ("none", "low", "tall"),
        weights=(0.55, 0.30, 0.15),
        k=1,
    )[0]
    header_band: HeaderBand = rng.choices(
        ("none", "narrow", "bold"),
        weights=(0.45, 0.40, 0.15),
        k=1,
    )[0]
    kick_panel: KickPanel = rng.choices(
        ("none", "low", "tall"),
        weights=(0.50, 0.35, 0.15),
        k=1,
    )[0]
    motor_housing: MotorHousing = rng.choices(
        ("none", "top_box"),
        weights=(0.75, 0.25),
        k=1,
    )[0]

    rmin, rmax = DOOR_RADIUS_RANGES[door_radius]
    drum_inner_radius = round(rng.uniform(rmin, rmax), 4)
    hmin, hmax = DOOR_HEIGHT_RANGES[door_height]
    drum_inner_height = round(rng.uniform(hmin, hmax), 4)

    return RevolvingDoorConfig(
        wing_count=wing_count,
        drum_type=drum_type,
        door_radius=door_radius,
        door_height=door_height,
        wing_material=wing_material,
        push_bar_style=push_bar_style,
        top_cap_style=top_cap_style,
        bottom_ring=bottom_ring,
        sensor_module=sensor_module,
        material_style=material_style,
        canopy_style=canopy_style,
        panel_density=panel_density,
        canopy_skirt=canopy_skirt,
        header_band=header_band,
        kick_panel=kick_panel,
        motor_housing=motor_housing,
        drum_inner_radius=drum_inner_radius,
        drum_inner_height=drum_inner_height,
        name=f"seeded_revolving_door_{seed}",
    )


# ---------------------------------------------------------------------------
# Config resolution (every wing/decoration dimension derives from here)
# ---------------------------------------------------------------------------


def resolve_config(config: RevolvingDoorConfig) -> ResolvedRevolvingDoorConfig:
    if config.wing_count not in (3, 4):
        raise ValueError(f"wing_count must be 3 or 4 (got {config.wing_count})")
    if config.drum_type not in {"full_cylinder", "partial", "open_frame", "square"}:
        raise ValueError(f"Unsupported drum_type: {config.drum_type}")
    if config.door_radius not in DOOR_RADIUS_RANGES:
        raise ValueError(f"Unsupported door_radius bucket: {config.door_radius}")
    if config.door_height not in DOOR_HEIGHT_RANGES:
        raise ValueError(f"Unsupported door_height bucket: {config.door_height}")
    if config.wing_material not in WING_BODY_PALETTES:
        raise ValueError(f"Unsupported wing_material: {config.wing_material}")
    if config.push_bar_style not in {"straight", "curved", "d_handle", "none"}:
        raise ValueError(f"Unsupported push_bar_style: {config.push_bar_style}")
    if config.top_cap_style not in CANOPY_TOTAL_THICKNESS_BY_STYLE:
        raise ValueError(f"Unsupported top_cap_style: {config.top_cap_style}")
    if config.bottom_ring not in {"none", "low", "full"}:
        raise ValueError(f"Unsupported bottom_ring: {config.bottom_ring}")
    if config.sensor_module not in {"none", "small_blocks"}:
        raise ValueError(f"Unsupported sensor_module: {config.sensor_module}")
    if config.material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if config.canopy_style not in {"single_disc", "soffit_crown", "tiered"}:
        raise ValueError(f"Unsupported canopy_style: {config.canopy_style}")
    if config.panel_density not in PANEL_COUNT_BY_DENSITY:
        raise ValueError(f"Unsupported panel_density: {config.panel_density}")
    if config.canopy_skirt not in CANOPY_SKIRT_HEIGHT:
        raise ValueError(f"Unsupported canopy_skirt: {config.canopy_skirt}")
    if config.header_band not in HEADER_BAND_HEIGHT:
        raise ValueError(f"Unsupported header_band: {config.header_band}")
    if config.kick_panel not in KICK_PANEL_HEIGHT:
        raise ValueError(f"Unsupported kick_panel: {config.kick_panel}")
    if config.motor_housing not in {"none", "top_box"}:
        raise ValueError(f"Unsupported motor_housing: {config.motor_housing}")

    drum_type = config.drum_type
    canopy_style = config.canopy_style
    motor_housing = config.motor_housing
    canopy_skirt = config.canopy_skirt
    header_band = config.header_band
    kick_panel = config.kick_panel
    panel_density = config.panel_density
    top_cap_style = config.top_cap_style

    # Normalization rules
    # - open_frame is a bare skeleton: no wall-attached decorations. Also
    # strip bottom_ring so the posts sit directly on the floor disc (an
    # outer ring without a wall above it would just look like a floating
    # raised hoop).
    bottom_ring_field = config.bottom_ring
    if drum_type == "open_frame":
        canopy_skirt = "none"
        header_band = "none"
        kick_panel = "none"
        bottom_ring_field = "none"
    # - partial drum looks empty with only 6 panels (loses 1/3 to the opening);
    # require at least medium density.
    if drum_type == "partial" and panel_density == "low":
        panel_density = "med"
    # - motor_housing replaces finial decoration; if the user picked both
    # ``decorative`` top_cap and motor_housing, downgrade the cap to ``thick``
    # so the finial stack is suppressed but the canopy stays substantial.
    if motor_housing == "top_box" and top_cap_style == "decorative":
        top_cap_style = "thick"

    if config.drum_inner_radius is None:
        rmin, rmax = DOOR_RADIUS_RANGES[config.door_radius]
        drum_inner_radius = 0.5 * (rmin + rmax)
    else:
        drum_inner_radius = float(config.drum_inner_radius)
    if drum_inner_radius < 0.40:
        raise ValueError(f"drum_inner_radius too small: {drum_inner_radius}")

    if config.drum_inner_height is None:
        hmin, hmax = DOOR_HEIGHT_RANGES[config.door_height]
        drum_inner_height = 0.5 * (hmin + hmax)
    else:
        drum_inner_height = float(config.drum_inner_height)
    if drum_inner_height < 1.5:
        raise ValueError(f"drum_inner_height too small: {drum_inner_height}")

    canopy_total = CANOPY_TOTAL_THICKNESS_BY_STYLE[top_cap_style]
    top_cap_thickness = TOP_CAP_THICKNESS_BY_STYLE[top_cap_style]

    if canopy_style == "single_disc":
        soffit_thickness = 0.0
        tier_2_thickness = 0.0
        crown_thickness = canopy_total
    elif canopy_style == "soffit_crown":
        soffit_thickness = SOFFIT_THICKNESS
        tier_2_thickness = 0.0
        crown_thickness = max(0.040, canopy_total - soffit_thickness)
    else:  # tiered
        soffit_thickness = SOFFIT_THICKNESS
        tier_2_thickness = TIER_2_THICKNESS
        crown_thickness = max(0.040, canopy_total - soffit_thickness - tier_2_thickness)

    if bottom_ring_field == "none":
        bottom_ring_thickness = 0.0
    elif bottom_ring_field == "low":
        bottom_ring_thickness = BOTTOM_RING_HEIGHT_LOW
    else:
        bottom_ring_thickness = BOTTOM_RING_HEIGHT_FULL

    header_band_height = HEADER_BAND_HEIGHT[header_band]
    kick_panel_height = KICK_PANEL_HEIGHT[kick_panel]
    canopy_skirt_height = CANOPY_SKIRT_HEIGHT[canopy_skirt]

    panel_count = PANEL_COUNT_BY_DENSITY[panel_density]
    # Open-frame and square use their own fixed counts; record them anyway for
    # the validator to introspect.
    if drum_type == "open_frame":
        panel_count = 6
    elif drum_type == "square":
        panel_count = 4

    drum_floor_z = FLOOR_THICKNESS
    threshold_top_z = drum_floor_z + THRESHOLD_THICKNESS
    bottom_bearing_top_z = threshold_top_z + BOTTOM_BEARING_THICKNESS

    central_post_radius = max(0.035, min(0.12, drum_inner_radius * CENTRAL_POST_RADIUS_RATIO))
    wing_radial_extent = drum_inner_radius - WING_RADIAL_CLEARANCE

    rotor_floor_offset = THRESHOLD_THICKNESS + BOTTOM_BEARING_THICKNESS
    rotor_ceiling_offset = TOP_BEARING_THICKNESS

    # Wall vertical layout. Mullions / posts / corner-posts rest on the
    # floor_disc when there is no bottom_ring; with a bottom_ring they rest
    # on top of it. The threshold and the bottom bearing both live at much
    # smaller radii than the wall so they do NOT push the wall up.
    # Glass section is bounded by kick_panel below and header_band above;
    # both shorten the glass area without affecting wings, which live well
    # inside the drum's vertical span.
    wall_outer_bottom_z = drum_floor_z + bottom_ring_thickness
    wall_glass_bottom_z = wall_outer_bottom_z + kick_panel_height
    wall_glass_top_z = drum_floor_z + drum_inner_height - header_band_height
    if wall_glass_top_z - wall_glass_bottom_z < 0.4:
        raise ValueError(
            "Wall glass section is too short; check kick_panel/header_band/drum height combo: "
            f"glass_bottom={wall_glass_bottom_z}, glass_top={wall_glass_top_z}"
        )

    # Canopy stack (above the wall area)
    soffit_bottom_z = drum_floor_z + drum_inner_height
    soffit_top_z = soffit_bottom_z + soffit_thickness
    crown_bottom_z = soffit_top_z
    crown_top_z = crown_bottom_z + crown_thickness
    tier_2_bottom_z = crown_top_z
    tier_2_top_z = tier_2_bottom_z + tier_2_thickness
    top_cap_bottom_z = tier_2_top_z if tier_2_thickness > 0 else crown_top_z
    top_cap_top_z = top_cap_bottom_z + top_cap_thickness

    # Wing panel height: covers the full inner drum span minus floor/ceiling
    # offsets and breathing room. Kick_panel and header_band are radially
    # outside the wing's reach, so they don't reduce wing height.
    floor_obstacle = max(rotor_floor_offset, bottom_ring_thickness)
    panel_bottom_local = floor_obstacle + WING_TOP_BOTTOM_CLEARANCE
    panel_top_local = drum_inner_height - rotor_ceiling_offset - WING_TOP_BOTTOM_CLEARANCE
    wing_panel_height = max(0.8, panel_top_local - panel_bottom_local)

    return ResolvedRevolvingDoorConfig(
        wing_count=config.wing_count,
        drum_type=drum_type,
        door_radius=config.door_radius,
        door_height=config.door_height,
        wing_material=config.wing_material,
        push_bar_style=config.push_bar_style,
        top_cap_style=top_cap_style,
        bottom_ring=config.bottom_ring,
        sensor_module=config.sensor_module,
        material_style=config.material_style,
        canopy_style=canopy_style,
        panel_density=panel_density,
        canopy_skirt=canopy_skirt,
        header_band=header_band,
        kick_panel=kick_panel,
        motor_housing=motor_housing,
        drum_inner_radius=drum_inner_radius,
        drum_inner_height=drum_inner_height,
        central_post_radius=central_post_radius,
        wing_radial_extent=wing_radial_extent,
        wing_panel_height=wing_panel_height,
        panel_count=panel_count,
        soffit_thickness=soffit_thickness,
        crown_thickness=crown_thickness,
        tier_2_thickness=tier_2_thickness,
        top_cap_thickness=top_cap_thickness,
        bottom_ring_thickness=bottom_ring_thickness,
        header_band_height=header_band_height,
        kick_panel_height=kick_panel_height,
        canopy_skirt_height=canopy_skirt_height,
        drum_floor_z=drum_floor_z,
        threshold_top_z=threshold_top_z,
        bottom_bearing_top_z=bottom_bearing_top_z,
        wall_outer_bottom_z=wall_outer_bottom_z,
        wall_glass_bottom_z=wall_glass_bottom_z,
        wall_glass_top_z=wall_glass_top_z,
        soffit_bottom_z=soffit_bottom_z,
        soffit_top_z=soffit_top_z,
        crown_bottom_z=crown_bottom_z,
        crown_top_z=crown_top_z,
        tier_2_bottom_z=tier_2_bottom_z,
        tier_2_top_z=tier_2_top_z,
        top_cap_bottom_z=top_cap_bottom_z,
        top_cap_top_z=top_cap_top_z,
        rotor_floor_offset=rotor_floor_offset,
        rotor_ceiling_offset=rotor_ceiling_offset,
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Outline-aware helpers (cylinder vs square)
# ---------------------------------------------------------------------------


def _drum_disc_geometry(
    drum_type: DrumType, *, base_size: float, thickness: float, margin: float = 0.0
):
    """Return a Box or Cylinder matching the drum outline.

    ``base_size`` = drum_inner_radius for cylinder / partial / open_frame, and
    half the side length for square (== drum_inner_radius too, since we treat
    drum_inner_radius as the inscribed circle radius for square drums).
    ``margin`` extends the outline outward by that many meters.
    """

    if drum_type == "square":
        side = 2.0 * (base_size + margin)
        return Box((side, side, thickness))
    return Cylinder(radius=base_size + margin, length=thickness)


def _add_outline_disc(
    drum,
    *,
    drum_type: DrumType,
    base_size: float,
    z_center: float,
    thickness: float,
    margin: float,
    material,
    name: str,
) -> None:
    geom = _drum_disc_geometry(drum_type, base_size=base_size, thickness=thickness, margin=margin)
    drum.visual(
        geom,
        origin=Origin(xyz=(0.0, 0.0, z_center)),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


# ---------------------------------------------------------------------------
# Drum walls
# ---------------------------------------------------------------------------


def _add_cylinder_wall(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    frame_material,
    glass_material,
) -> None:
    """Tangent glass panels + mullions for full_cylinder / partial drums."""

    panel_count = resolved.panel_count
    radius = resolved.drum_inner_radius + 0.5 * DRUM_WALL_THICKNESS
    panel_arc = 2.0 * math.pi / panel_count
    panel_width = 2.0 * radius * math.sin(0.5 * panel_arc) * 0.94
    # Glass panel spans only the glass section (above kick_panel, below
    # header_band). Mullion runs the full wall height so it touches the
    # bottom_ring (or floor) and the bottom of the header_band.
    glass_height = resolved.wall_glass_top_z - resolved.wall_glass_bottom_z
    glass_center_z = 0.5 * (resolved.wall_glass_bottom_z + resolved.wall_glass_top_z)
    mullion_height = resolved.wall_glass_top_z - resolved.wall_outer_bottom_z
    mullion_center_z = 0.5 * (resolved.wall_outer_bottom_z + resolved.wall_glass_top_z)

    if resolved.drum_type == "full_cylinder":
        keep_indices = set(range(panel_count))
    else:
        opening = max(2, panel_count // 3)
        center_idx = panel_count // 4
        skip_indices = {
            (center_idx + d) % panel_count for d in range(-opening // 2, opening // 2 + 1)
        }
        keep_indices = set(range(panel_count)) - skip_indices
        if len(keep_indices) < 4:
            keep_indices = set(range(0, panel_count, max(1, panel_count // 4)))

    for i in range(panel_count):
        if i not in keep_indices:
            continue
        angle = (2.0 * math.pi * i) / panel_count
        cx = radius * math.cos(angle)
        cy = radius * math.sin(angle)
        yaw = angle + 0.5 * math.pi  # panel face points outward radially
        drum.visual(
            Box((panel_width, DRUM_WALL_THICKNESS, glass_height)),
            origin=Origin(xyz=(cx, cy, glass_center_z), rpy=(0.0, 0.0, yaw)),
            material=glass_material,
            name=f"side_glass_panel_{i}", material_class_id="glass.clear_transparent",
        )
        mullion_radius = 0.030
        post_x = (radius + 0.5 * DRUM_WALL_THICKNESS) * math.cos(angle)
        post_y = (radius + 0.5 * DRUM_WALL_THICKNESS) * math.sin(angle)
        drum.visual(
            Cylinder(radius=mullion_radius, length=mullion_height),
            origin=Origin(xyz=(post_x, post_y, mullion_center_z)),
            material=frame_material,
            name=f"drum_mullion_{i}", material_class_id=("metal.aluminum_bare" if resolved.material_style in {"glass", "aluminum", "brass", "bronze", "white_powder"} else "metal.blackened_gunmetal"),
        )


def _add_open_frame(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    frame_material,
) -> None:
    post_count = 6
    radius = resolved.drum_inner_radius + 0.5 * DRUM_WALL_THICKNESS
    # Posts run from floor (wall_outer_bottom_z == drum_floor_z for open_frame
    # since resolve_config strips bottom_ring) up to the top of the wall zone.
    wall_height = resolved.wall_glass_top_z - resolved.wall_outer_bottom_z
    post_z = 0.5 * (resolved.wall_outer_bottom_z + resolved.wall_glass_top_z)
    for i in range(post_count):
        angle = (2.0 * math.pi * i) / post_count
        drum.visual(
            Cylinder(radius=0.025, length=wall_height),
            origin=Origin(
                xyz=(radius * math.cos(angle), radius * math.sin(angle), post_z),
            ),
            material=frame_material,
            name=f"open_frame_post_{i}", material_class_id=("metal.aluminum_bare" if resolved.material_style in {"glass", "aluminum", "brass", "bronze", "white_powder"} else "metal.blackened_gunmetal"),
        )


def _add_square_wall(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    frame_material,
    glass_material,
) -> None:
    """Four flat glass walls + four corner posts for a square drum.

    Half-side length = drum_inner_radius (inscribed circle radius == half side).
    """

    half = resolved.drum_inner_radius
    # Glass panel spans only the glass section (above kick_panel, below
    # header_band). Corner posts and the side panels run the full wall
    # height so they touch bottom_ring/floor and reach the header_band.
    glass_height = resolved.wall_glass_top_z - resolved.wall_glass_bottom_z
    glass_z = 0.5 * (resolved.wall_glass_bottom_z + resolved.wall_glass_top_z)
    full_height = resolved.wall_glass_top_z - resolved.wall_outer_bottom_z
    full_z = 0.5 * (resolved.wall_outer_bottom_z + resolved.wall_glass_top_z)
    # Side wall width spans corner-to-corner minus corner post bite-in.
    side_width = 2.0 * half - 2.0 * SQUARE_CORNER_POST_WIDTH
    # Wall sits at the four cardinal directions; outer face at radius=half+wall_thickness/2.
    wall_outer = half + 0.5 * DRUM_WALL_THICKNESS
    for i, (cx, cy, yaw) in enumerate(
        (
            (0.0, wall_outer, 0.0),  # +Y wall
            (wall_outer, 0.0, 0.5 * math.pi),  # +X wall
            (0.0, -wall_outer, 0.0),  # -Y wall
            (-wall_outer, 0.0, 0.5 * math.pi),  # -X wall
        )
    ):
        drum.visual(
            Box((side_width, DRUM_WALL_THICKNESS, glass_height)),
            origin=Origin(xyz=(cx, cy, glass_z), rpy=(0.0, 0.0, yaw)),
            material=glass_material,
            name=f"side_glass_panel_{i}", material_class_id="glass.clear_transparent",
        )

    # Corner posts run the full wall height (touch floor / bottom_ring).
    corner_dist = half + 0.5 * DRUM_WALL_THICKNESS
    for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        drum.visual(
            Box((SQUARE_CORNER_POST_WIDTH, SQUARE_CORNER_POST_WIDTH, full_height)),
            origin=Origin(
                xyz=(sx * corner_dist, sy * corner_dist, full_z),
            ),
            material=frame_material,
            name=f"corner_post_{i}", material_class_id=("metal.aluminum_bare" if resolved.material_style in {"glass", "aluminum", "brass", "bronze", "white_powder"} else "metal.blackened_gunmetal"),
        )


# ---------------------------------------------------------------------------
# Floor / threshold / bearings / bottom_ring / kick_panel
# ---------------------------------------------------------------------------


def _build_floor_stack(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    frame_material,
    accent_material,
) -> None:
    """floor_disc → threshold → bottom_bearing column."""

    floor_margin = DRUM_WALL_THICKNESS + 0.060
    _add_outline_disc(
        drum,
        drum_type=resolved.drum_type,
        base_size=resolved.drum_inner_radius,
        z_center=0.5 * FLOOR_THICKNESS,
        thickness=FLOOR_THICKNESS,
        margin=floor_margin,
        material=accent_material,
        name="floor_disc",
    )

    # Threshold (always round; sits inside the drum)
    threshold_radius = max(0.40, resolved.drum_inner_radius - 0.020)
    drum.visual(
        Cylinder(radius=threshold_radius, length=THRESHOLD_THICKNESS),
        origin=Origin(xyz=(0.0, 0.0, resolved.drum_floor_z + 0.5 * THRESHOLD_THICKNESS)),
        material=accent_material,
        name="threshold", material_class_id=("metal.aluminum_bare" if resolved.material_style in {"aluminum", "brass", "bronze", "white_powder"} else "metal.blackened_gunmetal"),
    )

    # Bottom bearing (smaller than the rotor hub so the hub rests flush on it)
    bearing_radius = resolved.central_post_radius * 1.8
    drum.visual(
        Cylinder(radius=bearing_radius, length=BOTTOM_BEARING_THICKNESS),
        origin=Origin(
            xyz=(
                0.0,
                0.0,
                resolved.threshold_top_z + 0.5 * BOTTOM_BEARING_THICKNESS,
            )
        ),
        material=frame_material,
        name="bottom_bearing", material_class_id=("metal.aluminum_bare" if resolved.material_style in {"glass", "aluminum", "brass", "bronze", "white_powder"} else "metal.blackened_gunmetal"),
    )


def _add_bottom_ring(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    accent_material,
) -> None:
    if resolved.bottom_ring == "none" or resolved.drum_type == "open_frame":
        return
    ring_margin = DRUM_WALL_THICKNESS + 0.020
    _add_outline_disc(
        drum,
        drum_type=resolved.drum_type,
        base_size=resolved.drum_inner_radius,
        z_center=resolved.drum_floor_z + 0.5 * resolved.bottom_ring_thickness,
        thickness=resolved.bottom_ring_thickness,
        margin=ring_margin,
        material=accent_material,
        name="bottom_ring",
    )


def _add_kick_panel(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    accent_material,
) -> None:
    if resolved.kick_panel_height <= 0.0:
        return
    # Kick panel sits at the bottom of the wall zone, just inside the wall
    # outer face. Its bottom == wall_outer_bottom_z so it rests on whatever
    # is below (floor or bottom_ring).
    _add_outline_disc(
        drum,
        drum_type=resolved.drum_type,
        base_size=resolved.drum_inner_radius,
        z_center=resolved.wall_outer_bottom_z + 0.5 * resolved.kick_panel_height,
        thickness=resolved.kick_panel_height,
        margin=0.5 * DRUM_WALL_THICKNESS - 0.005,
        material=accent_material,
        name="kick_panel",
    )


def _add_header_band(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    accent_material,
) -> None:
    if resolved.header_band_height <= 0.0:
        return
    band_top_z = resolved.drum_floor_z + resolved.drum_inner_height
    band_center_z = band_top_z - 0.5 * resolved.header_band_height
    _add_outline_disc(
        drum,
        drum_type=resolved.drum_type,
        base_size=resolved.drum_inner_radius,
        z_center=band_center_z,
        thickness=resolved.header_band_height,
        margin=0.5 * DRUM_WALL_THICKNESS - 0.005,
        material=accent_material,
        name="header_band",
    )


# ---------------------------------------------------------------------------
# Top bearing + canopy stack + skirt + cap + finial + motor housing
# ---------------------------------------------------------------------------


def _add_top_bearing(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    frame_material,
) -> None:
    bearing_radius = resolved.central_post_radius * 1.8
    bearing_center_z = resolved.soffit_bottom_z - 0.5 * TOP_BEARING_THICKNESS
    drum.visual(
        Cylinder(radius=bearing_radius, length=TOP_BEARING_THICKNESS),
        origin=Origin(xyz=(0.0, 0.0, bearing_center_z)),
        material=frame_material,
        name="top_bearing", material_class_id=("metal.aluminum_bare" if resolved.material_style in {"glass", "aluminum", "brass", "bronze", "white_powder"} else "metal.blackened_gunmetal"),
    )


def _add_canopy_skirt(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    accent_material,
) -> None:
    if resolved.canopy_skirt_height <= 0.0:
        return
    # Sits just outside the wall, hanging down from the soffit's underside.
    skirt_top_z = resolved.soffit_bottom_z
    skirt_bottom_z = skirt_top_z - resolved.canopy_skirt_height
    skirt_center_z = 0.5 * (skirt_top_z + skirt_bottom_z)
    _add_outline_disc(
        drum,
        drum_type=resolved.drum_type,
        base_size=resolved.drum_inner_radius,
        z_center=skirt_center_z,
        thickness=resolved.canopy_skirt_height,
        margin=DRUM_WALL_THICKNESS + 0.025,
        material=accent_material,
        name="canopy_skirt",
    )


def _add_canopy_stack(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    frame_material,
    accent_material,
) -> None:
    canopy_margin = DRUM_WALL_THICKNESS + 0.060

    # Soffit (only when canopy_style is not single_disc)
    if resolved.soffit_thickness > 0.0:
        _add_outline_disc(
            drum,
            drum_type=resolved.drum_type,
            base_size=resolved.drum_inner_radius,
            z_center=0.5 * (resolved.soffit_bottom_z + resolved.soffit_top_z),
            thickness=resolved.soffit_thickness,
            margin=canopy_margin - 0.015,
            material=accent_material,
            name="canopy_soffit",
        )

    # Crown (the thick canopy slab; always present)
    _add_outline_disc(
        drum,
        drum_type=resolved.drum_type,
        base_size=resolved.drum_inner_radius,
        z_center=0.5 * (resolved.crown_bottom_z + resolved.crown_top_z),
        thickness=resolved.crown_thickness,
        margin=canopy_margin,
        material=frame_material,
        name="canopy_crown",
    )

    # Tier 2 (extra small slab on top of crown when canopy_style == tiered)
    if resolved.tier_2_thickness > 0.0:
        _add_outline_disc(
            drum,
            drum_type=resolved.drum_type,
            base_size=resolved.drum_inner_radius,
            z_center=0.5 * (resolved.tier_2_bottom_z + resolved.tier_2_top_z),
            thickness=resolved.tier_2_thickness,
            margin=canopy_margin - TIER_2_RADIAL_INSET,
            material=accent_material,
            name="canopy_tier_2",
        )


def _add_top_cap(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    accent_material,
) -> None:
    # Finishing rim slightly wider than the topmost canopy element.
    rim_margin = DRUM_WALL_THICKNESS + 0.090
    if resolved.tier_2_thickness > 0.0:
        rim_margin = DRUM_WALL_THICKNESS + 0.090 - TIER_2_RADIAL_INSET
    _add_outline_disc(
        drum,
        drum_type=resolved.drum_type,
        base_size=resolved.drum_inner_radius,
        z_center=0.5 * (resolved.top_cap_bottom_z + resolved.top_cap_top_z),
        thickness=resolved.top_cap_thickness,
        margin=rim_margin,
        material=accent_material,
        name="top_cap",
    )


def _add_finial_stack(
    drum,
    *,
    base_z: float,
    accent_material,
) -> None:
    """Decorative multi-stage finial (only when top_cap_style == decorative).

    Five stacked elements (base / stem / ball / spire / tip). Each stage sits
    exactly on the one beneath it.
    """

    base_thickness = 0.060
    base_radius = 0.115
    drum.visual(
        Cylinder(radius=base_radius, length=base_thickness),
        origin=Origin(xyz=(0.0, 0.0, base_z + 0.5 * base_thickness)),
        material=accent_material,
        name="finial_base", material_class_id="metal.bronze_cast",
    )

    stem_thickness = 0.160
    stem_bottom = base_z + base_thickness
    drum.visual(
        Cylinder(radius=0.048, length=stem_thickness),
        origin=Origin(xyz=(0.0, 0.0, stem_bottom + 0.5 * stem_thickness)),
        material=accent_material,
        name="finial_stem", material_class_id="metal.bronze_cast",
    )

    ball_radius = 0.055
    ball_center = stem_bottom + stem_thickness + ball_radius
    drum.visual(
        Sphere(radius=ball_radius),
        origin=Origin(xyz=(0.0, 0.0, ball_center)),
        material=accent_material,
        name="finial_ball", material_class_id="metal.bronze_cast",
    )

    spire_thickness = 0.130
    spire_bottom = ball_center + ball_radius
    drum.visual(
        Cylinder(radius=0.018, length=spire_thickness),
        origin=Origin(xyz=(0.0, 0.0, spire_bottom + 0.5 * spire_thickness)),
        material=accent_material,
        name="finial_spire", material_class_id="metal.bronze_cast",
    )

    tip_radius = 0.024
    tip_center = spire_bottom + spire_thickness + tip_radius
    drum.visual(
        Sphere(radius=tip_radius),
        origin=Origin(xyz=(0.0, 0.0, tip_center)),
        material=accent_material,
        name="finial_tip", material_class_id="metal.bronze_cast",
    )


def _add_motor_housing(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    frame_material,
    accent_material,
) -> None:
    if resolved.motor_housing == "none":
        return
    # Sits centred on top of the top_cap.
    canopy_radius = resolved.drum_inner_radius + DRUM_WALL_THICKNESS + 0.060
    housing_radius = max(0.18, canopy_radius * MOTOR_HOUSING_RADIUS_RATIO)
    housing_bottom_z = resolved.top_cap_top_z
    drum.visual(
        Cylinder(radius=housing_radius, length=MOTOR_HOUSING_HEIGHT),
        origin=Origin(xyz=(0.0, 0.0, housing_bottom_z + 0.5 * MOTOR_HOUSING_HEIGHT)),
        material=frame_material,
        name="motor_housing", material_class_id=("metal.aluminum_bare" if resolved.material_style in {"glass", "aluminum", "brass", "bronze", "white_powder"} else "metal.blackened_gunmetal"),
    )
    cap_radius = housing_radius * MOTOR_CAP_RADIUS_RATIO
    cap_bottom_z = housing_bottom_z + MOTOR_HOUSING_HEIGHT
    drum.visual(
        Cylinder(radius=cap_radius, length=MOTOR_CAP_HEIGHT),
        origin=Origin(xyz=(0.0, 0.0, cap_bottom_z + 0.5 * MOTOR_CAP_HEIGHT)),
        material=accent_material,
        name="motor_cap", material_class_id=("metal.aluminum_bare" if resolved.material_style in {"aluminum", "brass", "bronze", "white_powder"} else "metal.blackened_gunmetal"),
    )


def _add_sensor_module(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    accent_material,
) -> None:
    if resolved.sensor_module == "none":
        return
    block_size = (0.110, 0.080, 0.045)
    # Anchor on the inside lip just below the canopy soffit; for square drums
    # we keep the same angular convention (mid-edge of two opposite walls).
    sensor_radius = resolved.drum_inner_radius - 0.080
    for i, angle in enumerate((math.pi / 2.0, -math.pi / 2.0)):
        bx = sensor_radius * math.cos(angle)
        by = sensor_radius * math.sin(angle)
        drum.visual(
            Box(block_size),
            origin=Origin(
                xyz=(bx, by, resolved.soffit_bottom_z - 0.5 * block_size[2]),
                rpy=(0.0, 0.0, angle),
            ),
            material=accent_material,
            name=f"sensor_block_{i}", material_class_id="tech.control_interface",
        )


def _build_drum(
    drum,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    frame_material,
    accent_material,
    glass_material,
) -> None:
    _build_floor_stack(
        drum,
        resolved,
        frame_material=frame_material,
        accent_material=accent_material,
    )
    _add_bottom_ring(drum, resolved, accent_material=accent_material)
    _add_kick_panel(drum, resolved, accent_material=accent_material)

    if resolved.drum_type in ("full_cylinder", "partial"):
        _add_cylinder_wall(
            drum,
            resolved,
            frame_material=frame_material,
            glass_material=glass_material,
        )
    elif resolved.drum_type == "square":
        _add_square_wall(
            drum,
            resolved,
            frame_material=frame_material,
            glass_material=glass_material,
        )
    else:  # open_frame
        _add_open_frame(drum, resolved, frame_material=frame_material)

    _add_header_band(drum, resolved, accent_material=accent_material)
    _add_top_bearing(drum, resolved, frame_material=frame_material)
    _add_canopy_skirt(drum, resolved, accent_material=accent_material)
    _add_canopy_stack(
        drum,
        resolved,
        frame_material=frame_material,
        accent_material=accent_material,
    )
    _add_top_cap(drum, resolved, accent_material=accent_material)

    # Decorative finial OR motor housing, never both. resolve_config makes
    # them mutually exclusive by suppressing decorative top_cap when motor is
    # on.
    if resolved.motor_housing == "top_box":
        _add_motor_housing(
            drum,
            resolved,
            frame_material=frame_material,
            accent_material=accent_material,
        )
    elif resolved.top_cap_style == "decorative":
        _add_finial_stack(drum, base_z=resolved.top_cap_top_z, accent_material=accent_material)

    _add_sensor_module(drum, resolved, accent_material=accent_material)


# ---------------------------------------------------------------------------
# Central post + wings
# ---------------------------------------------------------------------------


def _build_central_post(
    post,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    frame_material,
    accent_material,
) -> None:
    """Hubs + shaft, all in rotor-local Z (joint origin at floor top)."""

    hub_height = 0.120
    hub_radius = resolved.central_post_radius * 2.4
    bottom_hub_center = resolved.rotor_floor_offset + 0.5 * hub_height
    post.visual(
        Cylinder(radius=hub_radius, length=hub_height),
        origin=Origin(xyz=(0.0, 0.0, bottom_hub_center)),
        material=accent_material,
        name="bottom_hub", material_class_id=("metal.aluminum_bare" if resolved.material_style in {"aluminum", "brass", "bronze", "white_powder"} else "metal.blackened_gunmetal"),
    )
    top_hub_top = resolved.drum_inner_height - resolved.rotor_ceiling_offset
    top_hub_center = top_hub_top - 0.5 * hub_height
    post.visual(
        Cylinder(radius=hub_radius, length=hub_height),
        origin=Origin(xyz=(0.0, 0.0, top_hub_center)),
        material=accent_material,
        name="top_hub", material_class_id=("metal.aluminum_bare" if resolved.material_style in {"aluminum", "brass", "bronze", "white_powder"} else "metal.blackened_gunmetal"),
    )
    shaft_bottom = bottom_hub_center + 0.5 * hub_height
    shaft_top = top_hub_center - 0.5 * hub_height
    shaft_length = max(0.1, shaft_top - shaft_bottom)
    post.visual(
        Cylinder(radius=resolved.central_post_radius, length=shaft_length),
        origin=Origin(xyz=(0.0, 0.0, shaft_bottom + 0.5 * shaft_length)),
        material=frame_material,
        name="central_shaft", material_class_id=("metal.aluminum_bare" if resolved.material_style in {"glass", "aluminum", "brass", "bronze", "white_powder"} else "metal.blackened_gunmetal"),
    )


def _add_push_bar_straight(
    post,
    *,
    index: int,
    angle: float,
    radial_inner: float,
    radial_length: float,
    panel_center_z: float,
    frame_material,
) -> None:
    bar_length = 0.50 * radial_length
    bar_center_x_local = radial_inner + 0.50 * radial_length
    offset = PUSH_BAR_BASE_OFFSET
    c, s = math.cos(angle), math.sin(angle)
    tx, ty = -s, c
    bar_x = c * bar_center_x_local + tx * offset
    bar_y = s * bar_center_x_local + ty * offset
    post.visual(
        Cylinder(radius=STRAIGHT_BAR_RADIUS, length=bar_length),
        origin=Origin(
            xyz=(bar_x, bar_y, panel_center_z),
            rpy=(0.0, math.pi / 2.0, angle),
        ),
        material=frame_material,
        name=f"wing_{index}_push_bar", material_class_id="metal.aluminum_bare",
    )


def _add_push_bar_curved(
    post,
    *,
    index: int,
    angle: float,
    radial_inner: float,
    radial_length: float,
    panel_center_z: float,
    frame_material,
) -> None:
    """Multi-segment arc bowing outward from the wing face."""

    bar_length = 0.55 * radial_length
    bar_center_x_local = radial_inner + 0.50 * radial_length
    offset_base = PUSH_BAR_BASE_OFFSET
    bow = CURVED_BOW_HEIGHT
    n = CURVED_SEGMENT_COUNT
    c, s = math.cos(angle), math.sin(angle)
    tx, ty = -s, c

    points = []
    for k in range(n + 1):
        u = (k / n) - 0.5
        x_local = bar_center_x_local + u * bar_length
        y_local = offset_base + bow * (1.0 - 4.0 * u * u)  # parabolic bow
        points.append((x_local, y_local))

    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        cx_local = 0.5 * (x0 + x1)
        cy_local = 0.5 * (y0 + y1)
        seg_length = math.hypot(x1 - x0, y1 - y0)
        seg_angle = math.atan2(y1 - y0, x1 - x0)
        world_x = c * cx_local + tx * cy_local
        world_y = s * cx_local + ty * cy_local
        final_yaw = angle + seg_angle
        post.visual(
            Cylinder(radius=CURVED_BAR_RADIUS, length=seg_length),
            origin=Origin(
                xyz=(world_x, world_y, panel_center_z),
                rpy=(0.0, math.pi / 2.0, final_yaw),
            ),
            material=frame_material,
            name=f"wing_{index}_push_bar_seg_{i}", material_class_id="metal.aluminum_bare",
        )


def _add_push_bar_d_handle(
    post,
    *,
    index: int,
    angle: float,
    radial_inner: float,
    radial_length: float,
    panel_center_z: float,
    frame_material,
    stile_material,
) -> None:
    """Thick straight bar standing well off the wing face on two brackets."""

    bar_length = 0.55 * radial_length
    bar_center_x_local = radial_inner + 0.50 * radial_length
    offset = D_HANDLE_OFFSET
    c, s = math.cos(angle), math.sin(angle)
    tx, ty = -s, c

    bar_x = c * bar_center_x_local + tx * offset
    bar_y = s * bar_center_x_local + ty * offset
    post.visual(
        Cylinder(radius=D_HANDLE_BAR_RADIUS, length=bar_length),
        origin=Origin(
            xyz=(bar_x, bar_y, panel_center_z),
            rpy=(0.0, math.pi / 2.0, angle),
        ),
        material=frame_material,
        name=f"wing_{index}_push_bar", material_class_id="metal.aluminum_bare",
    )

    # Two cylindrical stand-off brackets perpendicular to the wing face,
    # connecting wing (at offset 0 in tangent dir) to bar (at offset).
    for side_sign, label in ((-1.0, "left"), (1.0, "right")):
        end_x_local = bar_center_x_local + side_sign * 0.5 * bar_length
        # Bracket centre sits halfway between wing face and bar in tangent dir.
        bx = c * end_x_local + tx * (0.5 * offset)
        by = s * end_x_local + ty * (0.5 * offset)
        # Bracket cylinder oriented along tangent direction (perpendicular to wing).
        # Its length axis +Z (local) should map to tangent (tx, ty, 0):
        # pitch=pi/2, yaw=angle+pi/2.
        post.visual(
            Cylinder(radius=D_HANDLE_BRACKET_RADIUS, length=offset),
            origin=Origin(
                xyz=(bx, by, panel_center_z),
                rpy=(0.0, math.pi / 2.0, angle + 0.5 * math.pi),
            ),
            material=stile_material,
            name=f"wing_{index}_push_bar_bracket_{label}", material_class_id="metal.blackened_gunmetal",
        )


def _add_wing(
    post,
    *,
    index: int,
    angle: float,
    resolved: ResolvedRevolvingDoorConfig,
    panel_material,
    stile_material,
    frame_material,
) -> None:
    """Visual wing on the rotor link. Rotor-local frame."""

    inner_edge = resolved.central_post_radius + WING_ROOT_STILE_WIDTH
    outer_edge = resolved.wing_radial_extent
    radial_length = max(0.10, outer_edge - inner_edge)
    radial_center = inner_edge + 0.5 * radial_length
    panel_height = resolved.wing_panel_height

    floor_obstacle = max(resolved.bottom_ring_thickness, resolved.rotor_floor_offset)
    panel_bottom_local = floor_obstacle + WING_TOP_BOTTOM_CLEARANCE
    panel_center_z = panel_bottom_local + 0.5 * panel_height

    c = math.cos(angle)
    s = math.sin(angle)

    # Wing panel (main face)
    post.visual(
        Box((radial_length, WING_PANEL_THICKNESS, panel_height)),
        origin=Origin(
            xyz=(c * radial_center, s * radial_center, panel_center_z),
            rpy=(0.0, 0.0, angle),
        ),
        material=panel_material,
        name=f"wing_{index}_panel", material_class_id=("glass.clear_transparent" if resolved.wing_material in {"glass", "wood_panel"} else "metal.aluminum_bare"),
    )

    # Inner / root stile flush against the central post
    root_stile_center = resolved.central_post_radius + 0.5 * WING_ROOT_STILE_WIDTH
    post.visual(
        Box((WING_ROOT_STILE_WIDTH, WING_ROOT_STILE_DEPTH, panel_height)),
        origin=Origin(
            xyz=(c * root_stile_center, s * root_stile_center, panel_center_z),
            rpy=(0.0, 0.0, angle),
        ),
        material=stile_material,
        name=f"wing_{index}_root_stile", material_class_id=("metal.blackened_gunmetal" if resolved.wing_material in {"glass", "metal_frame"} else "wood.walnut_dark"),
    )

    # Bottom and top rails (reinforcement strips on the panel)
    rail_h = 0.060
    for z_offset, label in (
        (-0.5 * panel_height + 0.5 * rail_h, "bottom"),
        (0.5 * panel_height - 0.5 * rail_h, "top"),
    ):
        post.visual(
            Box((radial_length, WING_PANEL_THICKNESS + 0.015, rail_h)),
            origin=Origin(
                xyz=(c * radial_center, s * radial_center, panel_center_z + z_offset),
                rpy=(0.0, 0.0, angle),
            ),
            material=stile_material,
            name=f"wing_{index}_{label}_rail", material_class_id=("metal.blackened_gunmetal" if resolved.wing_material in {"glass", "metal_frame"} else "wood.walnut_dark"),
        )

    # Outer stile (vertical post at the wing tip)
    stile_w = 0.060
    stile_thickness = 0.080
    outer_r = outer_edge - 0.5 * stile_w
    post.visual(
        Box((stile_w, stile_thickness, panel_height)),
        origin=Origin(
            xyz=(c * outer_r, s * outer_r, panel_center_z),
            rpy=(0.0, 0.0, angle),
        ),
        material=stile_material,
        name=f"wing_{index}_outer_stile", material_class_id=("metal.blackened_gunmetal" if resolved.wing_material in {"glass", "metal_frame"} else "wood.walnut_dark"),
    )

    # Push bar variant
    style = resolved.push_bar_style
    if style == "straight":
        _add_push_bar_straight(
            post,
            index=index,
            angle=angle,
            radial_inner=inner_edge,
            radial_length=radial_length,
            panel_center_z=panel_center_z,
            frame_material=frame_material,
        )
    elif style == "curved":
        _add_push_bar_curved(
            post,
            index=index,
            angle=angle,
            radial_inner=inner_edge,
            radial_length=radial_length,
            panel_center_z=panel_center_z,
            frame_material=frame_material,
        )
    elif style == "d_handle":
        _add_push_bar_d_handle(
            post,
            index=index,
            angle=angle,
            radial_inner=inner_edge,
            radial_length=radial_length,
            panel_center_z=panel_center_z,
            frame_material=frame_material,
            stile_material=stile_material,
        )
    # style == "none" -> add nothing


def _add_wings(
    post,
    resolved: ResolvedRevolvingDoorConfig,
    *,
    panel_material,
    stile_material,
    frame_material,
) -> None:
    for i in range(resolved.wing_count):
        angle = (2.0 * math.pi * i) / resolved.wing_count
        _add_wing(
            post,
            index=i,
            angle=angle,
            resolved=resolved,
            panel_material=panel_material,
            stile_material=stile_material,
            frame_material=frame_material,
        )


# ---------------------------------------------------------------------------
# Top-level builder
# ---------------------------------------------------------------------------


def build_revolving_door(
    config: RevolvingDoorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or RevolvingDoorConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-revolving-door-assets-")))

    model = ArticulatedObject(name=resolved.name, assets=assets)

    frame_rgba, accent_rgba, glass_rgba = MATERIAL_PALETTES[resolved.material_style]
    frame_material = model.material("door_frame", rgba=frame_rgba)
    accent_material = model.material("door_accent", rgba=accent_rgba)
    glass_material = model.material("door_glass", rgba=glass_rgba)
    panel_rgba, stile_rgba = WING_BODY_PALETTES[resolved.wing_material]
    panel_material = model.material("wing_panel", rgba=panel_rgba)
    stile_material = model.material("wing_stile", rgba=stile_rgba)

    drum = model.part("outer_drum")
    _build_drum(
        drum,
        resolved,
        frame_material=frame_material,
        accent_material=accent_material,
        glass_material=glass_material,
    )

    post = model.part("central_post")
    _build_central_post(
        post,
        resolved,
        frame_material=frame_material,
        accent_material=accent_material,
    )
    _add_wings(
        post,
        resolved,
        panel_material=panel_material,
        stile_material=stile_material,
        frame_material=frame_material,
    )

    model.articulation(
        "central_rotation_joint",
        ArticulationType.CONTINUOUS,
        parent=drum,
        child=post,
        origin=Origin(xyz=(0.0, 0.0, resolved.drum_floor_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=120.0, velocity=1.4),
    )

    return model


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


def run_revolving_door_tests(
    object_model: ArticulatedObject, config: RevolvingDoorConfig
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)

    drum = object_model.get_part("outer_drum")
    post = object_model.get_part("central_post")
    rotation_joint = object_model.get_articulation("central_rotation_joint")

    # The central post (shaft + hubs + wings) spins inside the drum; its hubs are
    # journaled in the drum's floor bearing / bottom ring and canopy skirt. That
    # bearing engagement is an intentional, pose-invariant overlap.
    ctx.allow_overlap(
        post,
        drum,
        reason="Central post rotor is journaled inside the drum (hubs in the bottom ring / canopy skirt bearings).",
    )

    continuous_joints = [
        j for j in object_model.articulations if j.articulation_type == ArticulationType.CONTINUOUS
    ]
    ctx.check(
        "single_continuous_rotation_joint",
        len(continuous_joints) == 1,
        details=f"continuous_joints={[j.name for j in continuous_joints]}",
    )
    central_post_parts = [p for p in object_model.parts if p.name == "central_post"]
    ctx.check(
        "single_central_post_per_record",
        len(central_post_parts) == 1,
        details=f"central_post_parts={[p.name for p in central_post_parts]}",
    )
    ctx.check(
        "no_extra_articulations",
        len(object_model.articulations) == 1,
        details=f"articulations={[j.name for j in object_model.articulations]}",
    )

    ax = rotation_joint.axis
    ctx.check(
        "central_rotation_axis_vertical",
        abs(ax[0]) < 1e-6 and abs(ax[1]) < 1e-6 and abs(abs(ax[2]) - 1.0) < 1e-6,
        details=f"axis={ax}",
    )

    ctx.check(
        "rotation_parent_is_outer_drum",
        rotation_joint.parent == "outer_drum" and rotation_joint.child == "central_post",
        details=f"parent={rotation_joint.parent}, child={rotation_joint.child}",
    )

    # Wings: count + equal-angle distribution
    wing_panel_visuals = [
        v
        for v in post.visuals
        if v.name is not None and v.name.startswith("wing_") and v.name.endswith("_panel")
    ]
    ctx.check(
        "wing_panel_count_matches",
        len(wing_panel_visuals) == resolved.wing_count,
        details=(f"wing_panel_count={len(wing_panel_visuals)}, expected={resolved.wing_count}"),
    )
    expected_angles = sorted(
        ((2.0 * math.pi * i) / resolved.wing_count) % (2.0 * math.pi)
        for i in range(resolved.wing_count)
    )
    observed_angles = []
    for v in wing_panel_visuals:
        x, y, _z = v.origin.xyz
        observed_angles.append(math.atan2(y, x) % (2.0 * math.pi))
    observed_angles.sort()
    tol_rad = math.radians(1.0)
    ang_ok = len(observed_angles) == len(expected_angles) and all(
        min(abs(o - e), 2.0 * math.pi - abs(o - e)) < tol_rad
        for o, e in zip(observed_angles, expected_angles)
    )
    ctx.check(
        "wings_equal_angle_distribution",
        ang_ok,
        details=f"observed={observed_angles}, expected={expected_angles}",
    )

    # Wing tip within drum inscribed radius (the inscribed circle is the same
    # for cylinder, partial, open_frame, and square -- in all cases the wing
    # must fit inside a circle of radius drum_inner_radius).
    max_tip_radius = 0.0
    for i in range(resolved.wing_count):
        outer_stile = next((v for v in post.visuals if v.name == f"wing_{i}_outer_stile"), None)
        if outer_stile is None:
            continue
        x, y, _z = outer_stile.origin.xyz
        max_tip_radius = max(max_tip_radius, math.hypot(x, y))
    ctx.check(
        "wings_within_drum_radius",
        max_tip_radius <= resolved.drum_inner_radius + 1e-3,
        details=(
            f"max_tip_radius={max_tip_radius:.3f}, "
            f"drum_inner_radius={resolved.drum_inner_radius:.3f}"
        ),
    )

    # Half-turn rotation moves the wing tip to the opposite side
    stile_rest = ctx.part_element_world_aabb(post, elem="wing_0_outer_stile")
    with ctx.pose({rotation_joint: math.pi}):
        stile_half = ctx.part_element_world_aabb(post, elem="wing_0_outer_stile")
    if stile_rest is not None and stile_half is not None:
        rest_cx = 0.5 * (stile_rest[0][0] + stile_rest[1][0])
        rest_cy = 0.5 * (stile_rest[0][1] + stile_rest[1][1])
        half_cx = 0.5 * (stile_half[0][0] + stile_half[1][0])
        half_cy = 0.5 * (stile_half[0][1] + stile_half[1][1])
        moved = math.hypot(half_cx - rest_cx, half_cy - rest_cy)
        ctx.check(
            "wings_rotate_with_post",
            moved > 0.5 * resolved.wing_radial_extent,
            details=f"moved={moved:.3f}",
        )
    else:
        ctx.check(
            "wings_rotate_with_post",
            False,
            details="missing wing_0_outer_stile element AABB",
        )

    # central_shaft on drum axis
    shaft = next((v for v in post.visuals if v.name == "central_shaft"), None)
    if shaft is not None:
        sx, sy, _sz = shaft.origin.xyz
        ctx.check(
            "central_shaft_on_drum_axis",
            abs(sx) < 1e-3 and abs(sy) < 1e-3,
            details=f"shaft xyz={shaft.origin.xyz}",
        )

    drum_visual_names = {v.name for v in drum.visuals if v.name is not None}

    # Mandatory drum elements
    for required_name in (
        "floor_disc",
        "threshold",
        "bottom_bearing",
        "top_bearing",
        "canopy_crown",
        "top_cap",
    ):
        ctx.check(
            f"drum_has_{required_name}",
            required_name in drum_visual_names,
            details=f"drum_visuals={sorted(drum_visual_names)}",
        )

    # Canopy style → soffit / tier_2 presence
    if resolved.soffit_thickness > 0.0:
        ctx.check(
            "canopy_soffit_present",
            "canopy_soffit" in drum_visual_names,
            details=f"canopy_style={resolved.canopy_style}",
        )
    else:
        ctx.check(
            "no_canopy_soffit_for_single_disc",
            "canopy_soffit" not in drum_visual_names,
            details=f"canopy_style={resolved.canopy_style}",
        )
    if resolved.tier_2_thickness > 0.0:
        ctx.check(
            "canopy_tier_2_present_for_tiered",
            "canopy_tier_2" in drum_visual_names,
            details=f"canopy_style={resolved.canopy_style}",
        )
    else:
        ctx.check(
            "no_canopy_tier_2_unless_tiered",
            "canopy_tier_2" not in drum_visual_names,
            details=f"canopy_style={resolved.canopy_style}",
        )

    # canopy_skirt / header_band / kick_panel present-iff configured
    for opt_name, opt_height in (
        ("canopy_skirt", resolved.canopy_skirt_height),
        ("header_band", resolved.header_band_height),
        ("kick_panel", resolved.kick_panel_height),
    ):
        if opt_height > 0.0:
            ctx.check(
                f"{opt_name}_present_when_configured",
                opt_name in drum_visual_names,
                details=f"drum_visuals={sorted(drum_visual_names)}",
            )
        else:
            ctx.check(
                f"no_{opt_name}_when_disabled",
                opt_name not in drum_visual_names,
                details=f"drum_visuals={sorted(drum_visual_names)}",
            )

    # Motor housing vs finial mutex
    finial_names = {"finial_base", "finial_stem", "finial_ball", "finial_spire", "finial_tip"}
    finial_present = finial_names & drum_visual_names
    motor_present = "motor_housing" in drum_visual_names
    if resolved.motor_housing == "top_box":
        ctx.check(
            "motor_housing_visuals_present",
            motor_present and "motor_cap" in drum_visual_names,
            details=f"motor_housing={resolved.motor_housing}",
        )
        ctx.check(
            "no_finial_when_motorized",
            len(finial_present) == 0,
            details=f"finial_visuals={sorted(finial_present)}",
        )
    else:
        ctx.check(
            "no_motor_housing_when_disabled",
            not motor_present,
            details=f"motor_housing={resolved.motor_housing}",
        )
        if resolved.top_cap_style == "decorative":
            ctx.check(
                "finial_stack_present_for_decorative",
                finial_present == finial_names,
                details=f"finial_visuals={sorted(finial_present)}",
            )
        else:
            ctx.check(
                "no_finial_stack_for_non_decorative",
                len(finial_present) == 0,
                details=f"finial_visuals={sorted(finial_present)}",
            )

    # Drum-type-specific wall checks
    if resolved.drum_type in ("full_cylinder", "partial"):
        mullion_count = sum(1 for n in drum_visual_names if n.startswith("drum_mullion_"))
        glass_panel_count = sum(1 for n in drum_visual_names if n.startswith("side_glass_panel_"))
        if resolved.drum_type == "full_cylinder":
            ctx.check(
                "cylinder_panel_count_matches_density",
                glass_panel_count == resolved.panel_count and mullion_count == resolved.panel_count,
                details=(
                    f"panels={glass_panel_count}, mullions={mullion_count}, "
                    f"expected={resolved.panel_count}"
                ),
            )
        else:  # partial -- some panels are skipped
            ctx.check(
                "partial_panel_count_positive_and_below_density",
                0 < glass_panel_count < resolved.panel_count and mullion_count == glass_panel_count,
                details=(
                    f"panels={glass_panel_count}, mullions={mullion_count}, "
                    f"density={resolved.panel_count}"
                ),
            )
    elif resolved.drum_type == "square":
        wall_count = sum(1 for n in drum_visual_names if n.startswith("side_glass_panel_"))
        corner_post_count = sum(1 for n in drum_visual_names if n.startswith("corner_post_"))
        ctx.check(
            "square_has_4_walls",
            wall_count == 4,
            details=f"wall_count={wall_count}",
        )
        ctx.check(
            "square_has_4_corner_posts",
            corner_post_count == 4,
            details=f"corner_post_count={corner_post_count}",
        )
    else:  # open_frame
        post_count = sum(1 for n in drum_visual_names if n.startswith("open_frame_post_"))
        ctx.check(
            "open_frame_post_count",
            post_count == 6,
            details=f"post_count={post_count}",
        )

    # Each wing has an inner root_stile
    post_visual_names = {v.name for v in post.visuals if v.name is not None}
    for i in range(resolved.wing_count):
        ctx.check(
            f"wing_{i}_has_root_stile",
            f"wing_{i}_root_stile" in post_visual_names,
            details=f"post_visuals={sorted(post_visual_names)}",
        )

    # Push-bar style → expected visuals
    style = resolved.push_bar_style
    push_bar_main = sum(1 for n in post_visual_names if n is not None and n.endswith("_push_bar"))
    push_bar_segs = sum(1 for n in post_visual_names if n is not None and "_push_bar_seg_" in n)
    push_bar_brackets = sum(
        1 for n in post_visual_names if n is not None and "_push_bar_bracket_" in n
    )
    if style == "none":
        ctx.check(
            "no_push_bar_when_disabled",
            push_bar_main == 0 and push_bar_segs == 0 and push_bar_brackets == 0,
            details=(f"main={push_bar_main}, segs={push_bar_segs}, brackets={push_bar_brackets}"),
        )
    elif style == "straight":
        ctx.check(
            "straight_push_bar_one_per_wing",
            push_bar_main == resolved.wing_count and push_bar_segs == 0 and push_bar_brackets == 0,
            details=(f"main={push_bar_main}, segs={push_bar_segs}, brackets={push_bar_brackets}"),
        )
    elif style == "curved":
        ctx.check(
            "curved_push_bar_segments_per_wing",
            push_bar_segs == resolved.wing_count * CURVED_SEGMENT_COUNT
            and push_bar_main == 0
            and push_bar_brackets == 0,
            details=(
                f"segs={push_bar_segs}, expected="
                f"{resolved.wing_count * CURVED_SEGMENT_COUNT}, "
                f"main={push_bar_main}, brackets={push_bar_brackets}"
            ),
        )
    elif style == "d_handle":
        ctx.check(
            "d_handle_push_bar_per_wing",
            push_bar_main == resolved.wing_count
            and push_bar_brackets == 2 * resolved.wing_count
            and push_bar_segs == 0,
            details=(
                f"main={push_bar_main}, brackets={push_bar_brackets}, "
                f"expected_main={resolved.wing_count}, "
                f"expected_brackets={2 * resolved.wing_count}"
            ),
        )

    # Identity: outer_drum + central_post, no bypass parts
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "has_outer_drum_and_central_post",
        "outer_drum" in part_names and "central_post" in part_names,
        details=f"parts={sorted(part_names)}",
    )
    ctx.check(
        "no_bypass_parts",
        not any("bypass" in p for p in part_names),
        details=f"parts={sorted(part_names)}",
    )

    # No clipping rotor hubs vs static bearings
    bottom_hub_aabb = ctx.part_element_world_aabb(post, elem="bottom_hub")
    bottom_bearing_aabb = ctx.part_element_world_aabb(drum, elem="bottom_bearing")
    if bottom_hub_aabb is not None and bottom_bearing_aabb is not None:
        hub_min_z = bottom_hub_aabb[0][2]
        bearing_max_z = bottom_bearing_aabb[1][2]
        ctx.check(
            "bottom_hub_above_bottom_bearing",
            hub_min_z >= bearing_max_z - 1e-3,
            details=f"hub_min_z={hub_min_z:.4f}, bearing_max_z={bearing_max_z:.4f}",
        )
    top_hub_aabb = ctx.part_element_world_aabb(post, elem="top_hub")
    top_bearing_aabb = ctx.part_element_world_aabb(drum, elem="top_bearing")
    if top_hub_aabb is not None and top_bearing_aabb is not None:
        hub_max_z = top_hub_aabb[1][2]
        bearing_min_z = top_bearing_aabb[0][2]
        ctx.check(
            "top_hub_below_top_bearing",
            hub_max_z <= bearing_min_z + 1e-3,
            details=f"hub_max_z={hub_max_z:.4f}, bearing_min_z={bearing_min_z:.4f}",
        )

    # Wing panel must stay between floor and canopy
    wing_aabb = ctx.part_element_world_aabb(post, elem="wing_0_panel")
    soffit_or_crown_aabb = ctx.part_element_world_aabb(
        drum,
        elem="canopy_soffit" if resolved.soffit_thickness > 0.0 else "canopy_crown",
    )
    threshold_aabb = ctx.part_element_world_aabb(drum, elem="threshold")
    if wing_aabb is not None and soffit_or_crown_aabb is not None:
        wing_max_z = wing_aabb[1][2]
        canopy_min_z = soffit_or_crown_aabb[0][2]
        ctx.check(
            "wing_below_canopy",
            wing_max_z <= canopy_min_z + 1e-3,
            details=f"wing_max_z={wing_max_z:.4f}, canopy_min_z={canopy_min_z:.4f}",
        )
    if wing_aabb is not None and threshold_aabb is not None:
        wing_min_z = wing_aabb[0][2]
        threshold_max_z = threshold_aabb[1][2]
        ctx.check(
            "wing_above_threshold",
            wing_min_z >= threshold_max_z - 1e-3,
            details=f"wing_min_z={wing_min_z:.4f}, threshold_max_z={threshold_max_z:.4f}",
        )

    # No floating wall structure: every mullion / open_frame_post /
    # corner_post must have its bottom AABB-z within a tight tolerance of
    # wall_outer_bottom_z, i.e. sitting on top of the floor_disc (or on top
    # of the bottom_ring when one is present).
    floating_tol = 1.5e-3
    expected_bottom_z = resolved.wall_outer_bottom_z
    floating_offenders: list[tuple[str, float]] = []
    for v_name in sorted(drum_visual_names):
        if not (
            v_name.startswith("drum_mullion_")
            or v_name.startswith("open_frame_post_")
            or v_name.startswith("corner_post_")
        ):
            continue
        aabb = ctx.part_element_world_aabb(drum, elem=v_name)
        if aabb is None:
            continue
        min_z = aabb[0][2]
        if abs(min_z - expected_bottom_z) > floating_tol:
            floating_offenders.append((v_name, min_z))
    ctx.check(
        "wall_posts_touch_floor_or_bottom_ring",
        len(floating_offenders) == 0,
        details=(f"expected_bottom_z={expected_bottom_z:.4f}, offenders={floating_offenders[:6]}"),
    )

    # Motor housing sits ABOVE top_cap (no penetration)
    if resolved.motor_housing == "top_box":
        motor_aabb = ctx.part_element_world_aabb(drum, elem="motor_housing")
        top_cap_aabb = ctx.part_element_world_aabb(drum, elem="top_cap")
        if motor_aabb is not None and top_cap_aabb is not None:
            ctx.check(
                "motor_housing_above_top_cap",
                motor_aabb[0][2] >= top_cap_aabb[1][2] - 1e-3,
                details=(
                    f"motor_min_z={motor_aabb[0][2]:.4f}, top_cap_max_z={top_cap_aabb[1][2]:.4f}"
                ),
            )

    return ctx.report()


# ---------------------------------------------------------------------------
# Convenience wrappers
# ---------------------------------------------------------------------------


def build_seeded_revolving_door(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_revolving_door(config_from_seed(seed), assets=assets)


def with_overrides(config: RevolvingDoorConfig, **kwargs: object) -> RevolvingDoorConfig:
    return replace(config, **kwargs)
