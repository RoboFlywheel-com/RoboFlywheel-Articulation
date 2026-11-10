# SPDX-License-Identifier: Apache-2.0

"""Clock tower with rotating hour and minute hands — modular procedural template.

Follows ``articraft_template_authoring/specs_modular_v1/clock_tower_with_rotating_hour_and_minute_hands.md``.

A vertical clock tower (campanile / glazed shaft / tiered stack) carries at least
one clock dial with independent hour and minute hands, each on a coaxial
CONTINUOUS joint about the dial face normal.

PRIMARY_ANCHOR: ``rec_clock_tower_with_rotating_hour_and_minute_hands_004c708c80f84d9290185a2bd93e2c5c``.
``config_from_seed(0)`` reproduces the anchor: glazed 4-face tower, integrated
dial visuals, ``hour_hand_i`` / ``minute_hand_i`` parts, 8 CONTINUOUS hand joints.

Adopted source modules (see specs/clock_tower_with_rotating_hour_and_minute_hands.md):
S1 004c708c (4-face glazed tower + indexed hands),
S2 08ab090 (campanile round shaft + mesh hands),
S3 496b656 (tiered base/shaft/lantern/clock_face chain),
S4 89a4bced (column + dual-face housing hands),
S5 f551a304 (belfry column stack + clock_face hands).
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    ConeGeometry,
    Cylinder,
    CylinderGeometry,
    LatheGeometry,
    MotionLimits,
    MotionProperties,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    section_loft,
)

__modular__ = True

TowerStyle = Literal["glazed_multiface", "campanile_round", "tiered_stack", "belfry_column"]
DialStyle = Literal["integrated", "single_face", "separate_part", "dual_housing"]
HandStyle = Literal["indexed_multiface", "mesh_blade", "stacked_simple", "front_rear"]
PaletteTheme = Literal["steel_glass", "limestone_campanile", "lighthouse_stone", "heritage_iron"]

TOWER_STYLES: tuple[TowerStyle, ...] = (
    "glazed_multiface",
    "campanile_round",
    "tiered_stack",
    "belfry_column",
)
DIAL_STYLES: tuple[DialStyle, ...] = (
    "integrated",
    "single_face",
    "separate_part",
    "dual_housing",
)
HAND_STYLES: tuple[HandStyle, ...] = (
    "indexed_multiface",
    "mesh_blade",
    "stacked_simple",
    "front_rear",
)

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "steel_glass": {
        "steel": (0.56, 0.59, 0.60, 1.0),
        "dark_steel": (0.05, 0.06, 0.07, 1.0),
        "glass": (0.55, 0.82, 0.95, 0.36),
        "frosted_glass": (0.86, 0.94, 0.98, 0.70),
        "concrete": (0.22, 0.23, 0.24, 1.0),
        "warm_led": (0.92, 0.82, 0.56, 1.0),
        "hand": (0.05, 0.06, 0.07, 1.0),
    },
    "limestone_campanile": {
        "steel": (0.56, 0.59, 0.60, 1.0),
        "dark_steel": (0.05, 0.05, 0.045, 1.0),
        "glass": (0.55, 0.82, 0.95, 0.36),
        "frosted_glass": (0.86, 0.94, 0.98, 0.70),
        "concrete": (0.70, 0.64, 0.52, 1.0),
        "warm_led": (0.86, 0.62, 0.23, 1.0),
        "hand": (0.02, 0.018, 0.015, 1.0),
    },
    "lighthouse_stone": {
        "steel": (0.24, 0.27, 0.30, 1.0),
        "dark_steel": (0.10, 0.10, 0.11, 1.0),
        "glass": (0.80, 0.92, 0.97, 0.42),
        "frosted_glass": (0.94, 0.92, 0.86, 1.0),
        "concrete": (0.79, 0.76, 0.69, 1.0),
        "warm_led": (0.18, 0.17, 0.16, 1.0),
        "hand": (0.10, 0.10, 0.11, 1.0),
    },
    "heritage_iron": {
        "steel": (0.61, 0.54, 0.34, 1.0),
        "dark_steel": (0.14, 0.17, 0.16, 1.0),
        "glass": (0.55, 0.82, 0.95, 0.36),
        "frosted_glass": (0.94, 0.93, 0.88, 1.0),
        "concrete": (0.14, 0.17, 0.16, 1.0),
        "warm_led": (0.07, 0.07, 0.06, 1.0),
        "hand": (0.07, 0.07, 0.06, 1.0),
    },
}


@dataclass(frozen=True)
class ClockTowerConfig:
    """User-facing configuration.

    Defaults reproduce the PRIMARY_ANCHOR (004c708c): glazed 4-face tower with
    integrated dial visuals and indexed multiface hands.
    """

    tower_style: TowerStyle = "glazed_multiface"
    dial_style: DialStyle = "integrated"
    hand_style: HandStyle = "indexed_multiface"
    palette_theme: PaletteTheme = "steel_glass"
    face_count: int = 4
    tower_height: float = 10.18
    shaft_width: float = 1.18
    dial_radius: float = 0.590
    hour_hand_length: float = 0.40
    minute_hand_length: float = 0.615
    has_lantern: bool = True
    has_antenna: bool = True
    has_bell: bool = False
    band_count: int = 7
    name: str = "reference_clock_tower"


@dataclass(frozen=True)
class ResolvedClockTowerConfig:
    tower_style: TowerStyle
    dial_style: DialStyle
    hand_style: HandStyle
    palette_theme: PaletteTheme
    face_count: int
    tower_height: float
    shaft_width: float
    dial_radius: float
    hour_hand_length: float
    minute_hand_length: float
    has_lantern: bool
    has_antenna: bool
    has_bell: bool
    band_count: int
    # Derived layout (S1 anchor proportions).
    base_size: float
    shaft_height: float
    head_size: float
    head_height: float
    head_center_z: float
    face_center_z: float
    hour_z_offset: float
    minute_z_offset: float
    hand_parent: str
    name: str


@dataclass(frozen=True)
class FaceSpec:
    name: str
    center: tuple[float, float, float]
    rpy: tuple[float, float, float]
    normal_axis: str
    normal_sign: float
    joint_axis: tuple[float, float, float]


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _minimum_clock_room_span(dial_radius: float, scale: float) -> float:
    bezel_diameter = 2.0 * 1.15 * dial_radius
    border = max(0.18 * scale, 0.30 * bezel_diameter)
    return bezel_diameter + border


def config_from_seed(seed: int) -> ClockTowerConfig:
    """Sample a reproducible clock-tower configuration.

    seed=0 returns defaults matching the PRIMARY_ANCHOR. Other seeds explore
    the tower_style × dial_style × hand_style × face_count subdomain.
    """
    if seed == 0:
        return ClockTowerConfig()

    rng = random.Random(seed)
    combos: list[tuple[TowerStyle, DialStyle, HandStyle, int]] = [
        ("glazed_multiface", "integrated", "indexed_multiface", 4),
        ("glazed_multiface", "integrated", "indexed_multiface", 2),
        ("glazed_multiface", "integrated", "indexed_multiface", 1),
        ("glazed_multiface", "single_face", "mesh_blade", 1),
        ("campanile_round", "single_face", "stacked_simple", 1),
        ("campanile_round", "integrated", "mesh_blade", 2),
        ("campanile_round", "separate_part", "indexed_multiface", 1),
        ("campanile_round", "integrated", "indexed_multiface", 4),
        ("glazed_multiface", "dual_housing", "front_rear", 2),
        ("campanile_round", "single_face", "mesh_blade", 1),
        ("campanile_round", "integrated", "mesh_blade", 4),
        ("glazed_multiface", "integrated", "mesh_blade", 1),
    ]
    tower_style, dial_style, hand_style, face_count = rng.choice(combos)

    tower_height = round(rng.uniform(5.0, 16.0), 4)
    shaft_width = round(rng.uniform(0.9, 2.2), 4)
    dial_radius = round(rng.uniform(0.45, 0.80), 4)
    hour_len = round(rng.uniform(0.28, min(0.55, dial_radius * 0.85)), 4)
    minute_len = round(rng.uniform(max(hour_len + 0.08, 0.38), min(0.72, dial_radius * 1.15)), 4)

    return ClockTowerConfig(
        tower_style=tower_style,
        dial_style=dial_style,
        hand_style=hand_style,
        palette_theme=rng.choice(tuple(PALETTES)),
        face_count=face_count,
        tower_height=tower_height,
        shaft_width=shaft_width,
        dial_radius=dial_radius,
        hour_hand_length=hour_len,
        minute_hand_length=minute_len,
        has_lantern=rng.random() < 0.75,
        has_antenna=rng.random() < 0.55,
        has_bell=tower_style in ("campanile_round", "belfry_column") and rng.random() < 0.8,
        band_count=rng.choice((4, 5, 6, 7, 8)),
        name=f"seeded_clock_tower_{seed}",
    )


def resolve_config(config: ClockTowerConfig) -> ResolvedClockTowerConfig:
    if config.tower_style not in TOWER_STYLES:
        raise ValueError(f"Unsupported tower_style: {config.tower_style}")
    if config.dial_style not in DIAL_STYLES:
        raise ValueError(f"Unsupported dial_style: {config.dial_style}")
    if config.hand_style not in HAND_STYLES:
        raise ValueError(f"Unsupported hand_style: {config.hand_style}")
    if config.palette_theme not in PALETTES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    tower_style: TowerStyle = config.tower_style
    dial_style: DialStyle = config.dial_style
    face_count = int(_clamp(config.face_count, 1, 4))
    if config.hand_style == "front_rear":
        face_count = 2
        dial_style = "dual_housing"
        if tower_style in ("tiered_stack", "belfry_column"):
            # S4's standalone column+housing clock is its own root object;
            # stacking it on a multi-part tower would create two root parts.
            tower_style = "glazed_multiface"
    if dial_style == "dual_housing":
        # The S4 housing carries exactly a front and a rear dial.
        face_count = 2
    if tower_style in ("tiered_stack", "belfry_column") and dial_style == "separate_part":
        face_count = 1

    tower_height = _clamp(config.tower_height, 4.0, 18.0)
    shaft_width = _clamp(config.shaft_width, 0.8, 2.8)
    dial_radius = _clamp(config.dial_radius, 0.45, 0.85)
    hour_hand_length = _clamp(config.hour_hand_length, 0.28, dial_radius * 0.85)
    minute_hand_length = _clamp(
        config.minute_hand_length,
        max(hour_hand_length + 0.04, 0.38),
        dial_radius * 1.15,
    )
    band_count = int(_clamp(config.band_count, 3, 10))

    # S1 anchor proportions (parameterized but seed=0 literals preserved).
    scale = tower_height / 10.18
    base_size = 2.45 * scale
    shaft_height = 7.45 * scale
    head_size = max(shaft_width * 1.58, 1.50 * scale)
    head_height = 1.82 * scale
    if tower_style == "glazed_multiface" and dial_style != "dual_housing":
        minimum_clock_room_span = _minimum_clock_room_span(dial_radius, scale)
        head_size = max(head_size, minimum_clock_room_span)
        head_height = max(head_height, minimum_clock_room_span)
    plinth_h = 0.36 * scale
    head_center_z = plinth_h + shaft_height + head_height / 2.0 - 0.05 * scale
    face_center_z = head_center_z

    hand_parent = "tower"
    if config.tower_style == "tiered_stack" and config.dial_style == "separate_part":
        hand_parent = "clock_face"
    elif config.tower_style == "belfry_column" and config.dial_style == "separate_part":
        hand_parent = "clock_face"
    elif config.hand_style == "front_rear":
        hand_parent = "housing"

    return ResolvedClockTowerConfig(
        tower_style=tower_style,
        dial_style=dial_style,
        hand_style=config.hand_style,
        palette_theme=config.palette_theme,
        face_count=face_count,
        tower_height=tower_height,
        shaft_width=shaft_width,
        dial_radius=dial_radius,
        hour_hand_length=hour_hand_length,
        minute_hand_length=minute_hand_length,
        has_lantern=bool(config.has_lantern),
        has_antenna=bool(config.has_antenna),
        has_bell=bool(config.has_bell),
        band_count=band_count,
        base_size=base_size,
        shaft_height=shaft_height,
        head_size=head_size,
        head_height=head_height,
        head_center_z=head_center_z,
        face_center_z=face_center_z,
        hour_z_offset=0.030,
        minute_z_offset=0.066,
        hand_parent=hand_parent,
        name=config.name,
    )


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #


def _cq_mesh(model: ArticulatedObject, shape: cq.Workplane, name: str, *, tolerance: float = 0.001):
    return mesh_from_cadquery(shape, name, assets=model.assets, tolerance=tolerance)


# adopted: S1 004c708c — annulus washer + connected hour tick ring
def _annulus(outer_radius: float, inner_radius: float, thickness: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(thickness)
        .translate((0.0, 0.0, -thickness / 2.0))
    )


def _marker_ring(radius: float, thickness: float) -> cq.Workplane:
    track = _annulus(radius + 0.012, radius - 0.012, thickness)
    result = track
    for index in range(12):
        angle = index * 30.0
        is_quarter = index % 3 == 0
        tangential = 0.035 if is_quarter else 0.020
        radial = 0.145 if is_quarter else 0.100
        tick_center = radius - radial * 0.28
        tick = (
            cq.Workplane("XY")
            .box(tangential, radial, thickness)
            .translate((0.0, tick_center, 0.0))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)
        )
        result = result.union(tick)
    return result


# adopted: S2 08ab090 — mesh clock hand profile
def _hand_shape(
    *,
    tip_length: float,
    tail_length: float,
    root_half_width: float,
    tip_half_width: float,
    thickness: float,
) -> cq.Workplane:
    return (
        cq.Workplane("XZ")
        .polyline(
            [
                (-root_half_width * 0.75, -tail_length),
                (root_half_width * 0.75, -tail_length),
                (root_half_width, 0.055),
                (tip_half_width, tip_length - 0.070),
                (0.0, tip_length),
                (-tip_half_width, tip_length - 0.070),
                (-root_half_width, 0.055),
            ]
        )
        .close()
        .extrude(thickness)
    )


def _offset_along_normal(
    center: tuple[float, float, float],
    axis: str,
    sign: float,
    distance: float,
) -> tuple[float, float, float]:
    cx, cy, cz = center
    if axis == "x":
        return (cx + sign * distance, cy, cz)
    return (cx, cy + sign * distance, cz)


def face_specs_for_count(
    resolved: ResolvedClockTowerConfig,
) -> list[FaceSpec]:
    """Radial face placement; S1 uses four cardinal faces at seed=0."""
    hs = resolved.head_size
    cz = resolved.face_center_z
    if resolved.hand_style == "front_rear":
        return [
            FaceSpec(
                "face_front", (0.0, 0.108, cz), (math.pi / 2.0, 0.0, 0.0), "y", 1.0, (0.0, 1.0, 0.0)
            ),
            FaceSpec(
                "face_rear",
                (0.0, -0.108, cz),
                (math.pi / 2.0, 0.0, math.pi),
                "y",
                -1.0,
                (0.0, -1.0, 0.0),
            ),
        ]
    specs: list[FaceSpec] = []
    if resolved.face_count == 1:
        specs.append(
            FaceSpec(
                "face_0",
                (0.0, -hs / 2.0 - 0.020, cz),
                (math.pi / 2.0, 0.0, 0.0),
                "y",
                -1.0,
                (0.0, 0.0, 1.0),
            )
        )
    elif resolved.face_count == 2:
        specs.extend(
            [
                FaceSpec(
                    "face_0",
                    (0.0, -hs / 2.0 - 0.020, cz),
                    (math.pi / 2.0, 0.0, 0.0),
                    "y",
                    -1.0,
                    (0.0, 0.0, 1.0),
                ),
                FaceSpec(
                    "face_1",
                    (0.0, hs / 2.0 + 0.020, cz),
                    (math.pi / 2.0, 0.0, math.pi),
                    "y",
                    1.0,
                    (0.0, 0.0, 1.0),
                ),
            ]
        )
    elif resolved.face_count == 3:
        for i, ang in enumerate((0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)):
            x = (hs / 2.0 + 0.020) * math.sin(ang)
            y = -(hs / 2.0 + 0.020) * math.cos(ang)
            specs.append(
                FaceSpec(
                    f"face_{i}",
                    (x, y, cz),
                    (math.pi / 2.0, 0.0, ang),
                    "y",
                    -1.0,
                    (0.0, 0.0, 1.0),
                )
            )
    else:
        specs.extend(
            [
                FaceSpec(
                    "face_0",
                    (0.0, -hs / 2.0 - 0.020, cz),
                    (math.pi / 2.0, 0.0, 0.0),
                    "y",
                    -1.0,
                    (0.0, 0.0, 1.0),
                ),
                FaceSpec(
                    "face_1",
                    (0.0, hs / 2.0 + 0.020, cz),
                    (math.pi / 2.0, 0.0, math.pi),
                    "y",
                    1.0,
                    (0.0, 0.0, 1.0),
                ),
                FaceSpec(
                    "face_2",
                    (hs / 2.0 + 0.020, 0.0, cz),
                    (math.pi / 2.0, 0.0, math.pi / 2.0),
                    "x",
                    1.0,
                    (0.0, 0.0, 1.0),
                ),
                FaceSpec(
                    "face_3",
                    (-hs / 2.0 - 0.020, 0.0, cz),
                    (math.pi / 2.0, 0.0, -math.pi / 2.0),
                    "x",
                    -1.0,
                    (0.0, 0.0, 1.0),
                ),
            ]
        )
    return specs[: resolved.face_count]


def campanile_face_specs(resolved: ResolvedClockTowerConfig) -> list[FaceSpec]:
    scale = resolved.tower_height / 13.0
    clock_z = 9.70 * scale
    shaft_r = 0.995 * scale
    angles = [0.0]
    if resolved.face_count >= 2:
        angles = [0.0, math.pi]
    if resolved.face_count >= 3:
        angles = [i * 2.0 * math.pi / 3.0 for i in range(3)]
    if resolved.face_count >= 4:
        angles = [0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0]
    angles = angles[: resolved.face_count]
    specs: list[FaceSpec] = []
    for i, ang in enumerate(angles):
        x = shaft_r * math.sin(ang)
        y = -shaft_r * math.cos(ang)
        specs.append(
            FaceSpec(
                f"face_{i}",
                (x, y, clock_z),
                (math.pi / 2.0, 0.0, ang),
                "y",
                -1.0,
                (0.0, 0.0, 1.0),
            )
        )
    return specs


def _radial_face_specs(
    face_count: int,
    *,
    radius: float,
    dial_z: float,
    yaws: tuple[float, ...],
) -> list[FaceSpec]:
    """FaceSpecs on a vertical cylinder/panel wall; yaw 0 faces -Y (dial up vector +Z)."""
    specs: list[FaceSpec] = []
    for i, yaw in enumerate(yaws[:face_count]):
        nx, ny = math.sin(yaw), -math.cos(yaw)
        if abs(nx) >= abs(ny):
            axis, sign = "x", 1.0 if nx >= 0.0 else -1.0
        else:
            axis, sign = "y", 1.0 if ny >= 0.0 else -1.0
        specs.append(
            FaceSpec(
                f"face_{i}",
                (nx * radius, ny * radius, dial_z),
                (math.pi / 2.0, 0.0, yaw),
                axis,
                sign,
                (0.0, 0.0, 1.0),
            )
        )
    return specs


def belfry_face_specs(resolved: ResolvedClockTowerConfig) -> list[FaceSpec]:
    """Dial placement on the belfry clock panel(s), in belfry_frame-local coords."""
    scale = resolved.tower_height / 18.0
    if resolved.face_count <= 1:
        yaws = (math.pi,)
    elif resolved.face_count == 2:
        yaws = (math.pi, 0.0)
    elif resolved.face_count == 3:
        yaws = (math.pi, math.pi + 2.0 * math.pi / 3.0, math.pi + 4.0 * math.pi / 3.0)
    else:
        yaws = (math.pi, 0.0, math.pi / 2.0, -math.pi / 2.0)
    return _radial_face_specs(
        resolved.face_count, radius=2.22 * scale, dial_z=2.35 * scale, yaws=yaws
    )


def tiered_face_specs(resolved: ResolvedClockTowerConfig) -> list[FaceSpec]:
    """Dial placement on the tiered shaft clock band, in shaft-local coords."""
    band_r = resolved.shaft_width * 0.85 * 1.15
    dial_z = resolved.face_center_z * 0.55
    if resolved.face_count <= 1:
        yaws = (0.0,)
    elif resolved.face_count == 2:
        yaws = (0.0, math.pi)
    elif resolved.face_count == 3:
        yaws = (0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)
    else:
        yaws = (0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)
    return _radial_face_specs(resolved.face_count, radius=band_r, dial_z=dial_z, yaws=yaws)


# --------------------------------------------------------------------------- #
# Slot A: tower_spine modules
# --------------------------------------------------------------------------- #


def _build_glazed_multiface_tower(
    model: ArticulatedObject,
    tower,
    resolved: ResolvedClockTowerConfig,
    mats: dict,
) -> None:
    """adopted: S1 004c708c — square glazed shaft + clock head + lantern."""
    steel = mats["steel"]
    glass = mats["glass"]
    concrete = mats["concrete"]

    scale = resolved.tower_height / 10.18
    base_size = resolved.base_size
    shaft_size = resolved.shaft_width
    shaft_height = resolved.shaft_height
    head_size = resolved.head_size
    head_height = resolved.head_height
    plinth_h = 0.36 * scale
    sill_h = 0.12 * scale
    sill_z = plinth_h + sill_h / 2.0
    shaft_bottom = plinth_h + sill_h
    shaft_top = shaft_bottom + shaft_height
    shaft_center_z = shaft_bottom + shaft_height / 2.0
    head_center_z = resolved.head_center_z

    tower.visual(
        Box((base_size, base_size, plinth_h)),
        origin=Origin(xyz=(0.0, 0.0, plinth_h / 2.0)),
        material=concrete,
        name="granite_plinth", material_class_id="stone.polished_granite",
    )
    tower.visual(
        Box((1.95 * scale, 1.95 * scale, sill_h)),
        origin=Origin(xyz=(0.0, 0.0, sill_z)),
        material=steel,
        name="steel_sill", material_class_id="metal.steel_bare",
    )
    tower.visual(
        Box((shaft_size, shaft_size, shaft_height)),
        origin=Origin(xyz=(0.0, 0.0, shaft_center_z)),
        material=glass,
        name="square_glass_shaft", material_class_id="glass.clear_transparent",
    )

    post_w = 0.105 * scale
    post_extend = 0.18 * scale
    for ix, x in enumerate((-shaft_size / 2.0 - post_w / 2.8, shaft_size / 2.0 + post_w / 2.8)):
        for iy, y in enumerate((-shaft_size / 2.0 - post_w / 2.8, shaft_size / 2.0 + post_w / 2.8)):
            tower.visual(
                Box((post_w, post_w, shaft_height + post_extend)),
                origin=Origin(xyz=(x, y, shaft_center_z)),
                material=steel,
                name=f"corner_post_{ix}_{iy}", material_class_id="metal.steel_bare",
            )

    band_zs_base = [1.25, 2.35, 3.45, 4.55, 5.65, 6.75, 7.65]
    band_depth = 0.075 * scale
    band_thickness = 0.075 * scale
    band_inset = band_depth * 0.35
    for i, z_base in enumerate(band_zs_base[: resolved.band_count]):
        z = z_base * scale
        if z < shaft_bottom + 0.04 * scale or z > shaft_top - 0.04 * scale:
            continue
        tower.visual(
            Box((shaft_size + 0.28 * scale, band_depth + band_inset, band_thickness)),
            origin=Origin(
                xyz=(
                    0.0,
                    -shaft_size / 2.0 - (band_depth + band_inset) / 2.0 + band_inset * 0.25,
                    z,
                )
            ),
            material=steel,
            name=f"front_band_{i}", material_class_id="metal.steel_bare",
        )
        tower.visual(
            Box((shaft_size + 0.28 * scale, band_depth + band_inset, band_thickness)),
            origin=Origin(
                xyz=(0.0, shaft_size / 2.0 + (band_depth + band_inset) / 2.0 - band_inset * 0.25, z)
            ),
            material=steel,
            name=f"rear_band_{i}", material_class_id="metal.steel_bare",
        )
        tower.visual(
            Box((band_depth + band_inset, shaft_size + 0.28 * scale, band_thickness)),
            origin=Origin(
                xyz=(
                    -shaft_size / 2.0 - (band_depth + band_inset) / 2.0 + band_inset * 0.25,
                    0.0,
                    z,
                )
            ),
            material=steel,
            name=f"side_band_{i}_0", material_class_id="metal.steel_bare",
        )
        tower.visual(
            Box((band_depth + band_inset, shaft_size + 0.28 * scale, band_thickness)),
            origin=Origin(
                xyz=(shaft_size / 2.0 + (band_depth + band_inset) / 2.0 - band_inset * 0.25, 0.0, z)
            ),
            material=steel,
            name=f"side_band_{i}_1", material_class_id="metal.steel_bare",
        )

    tower.visual(
        Box((head_size, head_size, head_height)),
        origin=Origin(xyz=(0.0, 0.0, head_center_z)),
        material=glass,
        name="glass_clock_room", material_class_id="glass.clear_transparent",
    )
    tower.visual(
        Box((head_size + 0.30 * scale, head_size + 0.30 * scale, 0.15 * scale)),
        origin=Origin(xyz=(0.0, 0.0, head_center_z - head_height / 2.0 - 0.02 * scale)),
        material=steel,
        name="lower_head_belt", material_class_id="metal.steel_bare",
    )
    tower.visual(
        Box((head_size + 0.36 * scale, head_size + 0.36 * scale, 0.18 * scale)),
        origin=Origin(xyz=(0.0, 0.0, head_center_z + head_height / 2.0 + 0.02 * scale)),
        material=steel,
        name="upper_head_belt", material_class_id="metal.steel_bare",
    )
    if resolved.has_lantern:
        tower.visual(
            Box((1.42 * scale, 1.42 * scale, 0.18 * scale)),
            origin=Origin(xyz=(0.0, 0.0, head_center_z + head_height / 2.0 + 0.20 * scale)),
            material=glass,
            name="glass_lantern", material_class_id="glass.clear_transparent",
        )
        tower.visual(
            Box((1.66 * scale, 1.66 * scale, 0.16 * scale)),
            origin=Origin(xyz=(0.0, 0.0, head_center_z + head_height / 2.0 + 0.36 * scale)),
            material=steel,
            name="flat_roof_cap", material_class_id="metal.steel_bare",
        )
    if resolved.has_antenna:
        if resolved.has_lantern:
            antenna_center_z = head_center_z + head_height / 2.0 + 0.96 * scale
        else:
            antenna_center_z = (
                head_center_z + head_height / 2.0 + 0.06 * scale + (1.15 * scale) / 2.0
            )
        antenna_len = 1.15 * scale
        tower.visual(
            Cylinder(radius=0.025 * scale, length=antenna_len),
            origin=Origin(xyz=(0.0, 0.0, antenna_center_z)),
            material=steel,
            name="antenna_mast", material_class_id="metal.steel_bare",
        )


def _build_campanile_round_tower(
    model: ArticulatedObject,
    tower,
    resolved: ResolvedClockTowerConfig,
    mats: dict,
) -> None:
    """adopted: S2 08ab090 — round limestone shaft + belfry roof."""
    stone = mats["concrete"]
    pale = mats["frosted_glass"]
    shadow = mats["steel"]
    slate = mats["dark_steel"]
    bronze = mats["warm_led"]
    dark = mats["hand"]

    scale = resolved.tower_height / 13.0
    shaft_h = 12.55 * scale
    lower_h = 0.28 * scale
    upper_h = 0.24 * scale
    plinth_overlap = 0.06 * scale
    lower_z = lower_h * 0.5
    upper_z = lower_h - plinth_overlap + upper_h * 0.5
    plinth_top = lower_h + upper_h - plinth_overlap
    tower.visual(
        Cylinder(radius=1.55 * scale, length=lower_h),
        origin=Origin(xyz=(0.0, 0.0, lower_z)),
        material=shadow,
        name="lower_plinth", material_class_id="stone.cut_sedimentary",
    )
    tower.visual(
        Cylinder(radius=1.34 * scale, length=upper_h),
        origin=Origin(xyz=(0.0, 0.0, upper_z)),
        material=pale,
        name="upper_plinth", material_class_id="stone.cut_sedimentary",
    )
    shaft_len = shaft_h + 0.04 * scale
    tower.visual(
        Cylinder(radius=1.00 * scale, length=shaft_len),
        origin=Origin(xyz=(0.0, 0.0, plinth_top - plinth_overlap + shaft_len * 0.5)),
        material=stone,
        name="round_shaft", material_class_id="stone.cut_sedimentary",
    )

    for z in (0.70, 2.95, 5.20, 7.45, 9.70, 11.95):
        if z * scale > shaft_h:
            continue
        tower.visual(
            Cylinder(radius=1.035 * scale, length=0.105 * scale),
            origin=Origin(xyz=(0.0, 0.0, z * scale)),
            material=pale,
            name=f"stone_band_{int(z * 100)}", material_class_id="stone.cut_sedimentary",
        )

    if resolved.has_bell:
        shaft_top = plinth_top - plinth_overlap + shaft_len
        tower.visual(
            Cylinder(radius=1.10 * scale, length=0.20 * scale),
            origin=Origin(xyz=(0.0, 0.0, shaft_top + 0.08 * scale)),
            material=pale,
            name="belfry_collar", material_class_id="stone.cut_sedimentary",
        )
        belfry_z = shaft_top + 0.16 * scale
        tower.visual(
            Cylinder(radius=1.18 * scale, length=0.34 * scale),
            origin=Origin(xyz=(0.0, 0.0, belfry_z + 0.17 * scale)),
            material=pale,
            name="belfry_drum", material_class_id="stone.cut_sedimentary",
        )
        tower.visual(
            Cylinder(radius=1.02 * scale, length=0.08 * scale),
            origin=Origin(xyz=(0.0, 0.0, belfry_z + 0.04 * scale)),
            material=pale,
            name="belfry_floor_ring", material_class_id="stone.cut_sedimentary",
        )
        for i in range(8):
            ang = i * math.tau / 8.0
            col_r = 0.96 * scale
            tower.visual(
                Cylinder(radius=0.085 * scale, length=2.20 * scale),
                origin=Origin(
                    xyz=(col_r * math.cos(ang), col_r * math.sin(ang), belfry_z + 1.27 * scale)
                ),
                material=pale,
                name=f"belfry_column_{i}", material_class_id="stone.cut_sedimentary",
            )
        tower.visual(
            Cylinder(radius=1.05 * scale, length=0.12 * scale),
            origin=Origin(xyz=(0.0, 0.0, belfry_z + 2.32 * scale)),
            material=slate,
            name="belfry_lintel", material_class_id="stone.slate",
        )
        hanger_len = max(0.85 * scale, belfry_z + 2.26 * scale - (belfry_z + 0.34 * scale))
        hanger_cz = (belfry_z + 0.34 * scale) + hanger_len * 0.5
        tower.visual(
            Cylinder(radius=0.08 * scale, length=hanger_len),
            origin=Origin(xyz=(0.0, 0.0, hanger_cz)),
            material=slate,
            name="bell_hanger", material_class_id="metal.blackened_gunmetal",
        )
        tower.visual(
            Cylinder(radius=0.20 * scale, length=0.50 * scale),
            origin=Origin(xyz=(0.0, 0.0, belfry_z + 1.55 * scale)),
            material=bronze,
            name="bell", material_class_id="metal.bronze_cast",
        )
        tower.visual(
            Cylinder(radius=0.04 * scale, length=0.24 * scale),
            origin=Origin(xyz=(0.0, 0.0, belfry_z + 1.42 * scale)),
            material=dark,
            name="bell_clapper", material_class_id="metal.blackened_gunmetal",
        )
        tower.visual(
            mesh_from_geometry(
                ConeGeometry(
                    radius=1.0 * scale, height=1.2 * scale, radial_segments=24, closed=True
                ),
                "belfry_roof",
            ),
            origin=Origin(xyz=(0.0, 0.0, belfry_z + 2.90 * scale)),
            material=slate,
            name="belfry_roof", material_class_id="stone.slate",
        )


def _octagon_mesh(model: ArticulatedObject, radius: float, height: float, name: str):
    return mesh_from_geometry(
        CylinderGeometry(radius, height, radial_segments=8, closed=True), name
    )


def _build_tiered_stack_tower(
    model: ArticulatedObject,
    resolved: ResolvedClockTowerConfig,
    mats: dict,
) -> tuple[ArticulatedObject, ArticulatedObject, ArticulatedObject]:
    """adopted: S3 496b656 — base/shaft/lantern FIXED chain; returns (base, shaft, lantern)."""
    stone = mats["concrete"]
    trim = mats["steel"]
    metal = mats["dark_steel"]
    glass = mats["glass"]
    roof = mats["hand"]

    base_h = 2.8
    shaft_h = resolved.tower_height * 0.75
    shaft_r = resolved.shaft_width * 0.85

    base = model.part("base")
    base.visual(
        _octagon_mesh(model, 3.15, 1.55, "base_lower"),
        origin=Origin(xyz=(0.0, 0.0, 0.775)),
        material=stone,
        name="lower_plinth", material_class_id="stone.masonry_wall",
    )
    base.visual(
        _octagon_mesh(model, 2.62, 1.25, "base_upper"),
        origin=Origin(xyz=(0.0, 0.0, 2.175)),
        material=stone,
        name="upper_plinth", material_class_id="stone.masonry_wall",
    )
    base.visual(
        _octagon_mesh(model, 2.25, 0.18, "base_cap"),
        origin=Origin(xyz=(0.0, 0.0, 2.71)),
        material=trim,
        name="cap_course", material_class_id="metal.steel_bare",
    )

    shaft = model.part("shaft")
    shaft.visual(
        Cylinder(radius=shaft_r, length=shaft_h),
        origin=Origin(xyz=(0.0, 0.0, shaft_h / 2.0)),
        material=stone,
        name="main_shaft", material_class_id="stone.cut_sedimentary",
    )
    shaft.visual(
        Cylinder(radius=shaft_r * 1.14, length=0.46),
        origin=Origin(xyz=(0.0, 0.0, 0.23)),
        material=trim,
        name="shaft_foot_course", material_class_id="metal.steel_bare",
    )
    shaft.visual(
        Cylinder(radius=shaft_r * 1.15, length=0.72),
        origin=Origin(xyz=(0.0, 0.0, resolved.face_center_z * 0.55)),
        material=trim,
        name="clock_band", material_class_id="metal.steel_bare",
    )
    shaft.visual(
        Cylinder(radius=shaft_r * 1.28, length=0.40),
        origin=Origin(xyz=(0.0, 0.0, shaft_h + 0.20)),
        material=trim,
        name="gallery_support", material_class_id="metal.steel_bare",
    )

    model.articulation(
        "base_to_shaft",
        ArticulationType.FIXED,
        parent=base,
        child=shaft,
        origin=Origin(xyz=(0.0, 0.0, base_h)),
    )

    lantern = model.part("lantern_room")
    lantern.visual(
        _octagon_mesh(model, 2.35, 0.26, "lantern_deck"),
        origin=Origin(xyz=(0.0, 0.0, 0.13)),
        material=trim,
        name="gallery_deck", material_class_id="metal.steel_bare",
    )
    lantern.visual(
        _octagon_mesh(model, 1.52, 0.24, "lantern_sill"),
        origin=Origin(xyz=(0.0, 0.0, 0.38)),
        material=metal,
        name="lower_sill", material_class_id="metal.blackened_gunmetal",
    )
    lantern.visual(
        _octagon_mesh(model, 1.52, 0.24, "lantern_ring"),
        origin=Origin(xyz=(0.0, 0.0, 2.33)),
        material=metal,
        name="upper_ring", material_class_id="metal.blackened_gunmetal",
    )
    lantern.visual(
        mesh_from_geometry(
            ConeGeometry(radius=1.70, height=1.55, radial_segments=8, closed=True), "lantern_roof"
        ),
        origin=Origin(xyz=(0.0, 0.0, 3.22)),
        material=roof,
        name="roof", material_class_id="metal.blackened_gunmetal",
    )
    for index in range(8):
        corner_angle = index * (math.pi / 4.0) + (math.pi / 8.0)
        face_angle = index * (math.pi / 4.0)
        lantern.visual(
            Box((0.15, 0.15, 2.18)),
            origin=Origin(
                xyz=(1.62 * math.cos(corner_angle), 1.62 * math.sin(corner_angle), 1.29),
                rpy=(0.0, 0.0, corner_angle),
            ),
            material=metal,
            name=f"post_{index}", material_class_id="metal.blackened_gunmetal",
        )
        lantern.visual(
            Box((1.00, 0.10, 1.82)),
            origin=Origin(
                xyz=(1.40 * math.cos(face_angle), 1.40 * math.sin(face_angle), 1.37),
                rpy=(0.0, 0.0, face_angle + math.pi / 2.0),
            ),
            material=glass,
            name=f"glass_{index}", material_class_id="glass.clear_transparent",
        )

    model.articulation(
        "shaft_to_lantern_room",
        ArticulationType.FIXED,
        parent=shaft,
        child=lantern,
        origin=Origin(xyz=(0.0, 0.0, shaft_h + 0.40)),
    )
    return base, shaft, lantern


def _build_belfry_column_stack(
    model: ArticulatedObject,
    resolved: ResolvedClockTowerConfig,
    mats: dict,
) -> tuple[ArticulatedObject, ArticulatedObject, ArticulatedObject]:
    """adopted: S5 f551a304 — base/shaft/belfry/roof/bell stack."""
    stone = mats["concrete"]
    trim = mats["steel"]
    roof_m = mats["dark_steel"]
    bronze = mats["warm_led"]

    scale = resolved.tower_height / 18.0
    base = model.part("base")
    base.visual(
        Cylinder(radius=3.40 * scale, length=0.80 * scale),
        origin=Origin(xyz=(0.0, 0.0, 0.40 * scale)),
        material=stone,
        name="lower_plinth", material_class_id="stone.masonry_wall",
    )
    base.visual(
        Cylinder(radius=2.80 * scale, length=1.20 * scale),
        origin=Origin(xyz=(0.0, 0.0, 1.40 * scale)),
        material=stone,
        name="upper_plinth", material_class_id="stone.masonry_wall",
    )

    shaft = model.part("shaft")
    shaft_h = 16.0 * scale
    shaft.visual(
        Cylinder(radius=2.10 * scale, length=shaft_h),
        origin=Origin(xyz=(0.0, 0.0, shaft_h / 2.0)),
        material=stone,
        name="tower_shaft", material_class_id="stone.cut_sedimentary",
    )
    shaft.visual(
        Cylinder(radius=2.35 * scale, length=0.45 * scale),
        origin=Origin(xyz=(0.0, 0.0, 0.225 * scale)),
        material=trim,
        name="shaft_collar", material_class_id="metal.steel_bare",
    )

    model.articulation(
        "base_to_shaft",
        ArticulationType.FIXED,
        parent=base,
        child=shaft,
        origin=Origin(xyz=(0.0, 0.0, 2.00 * scale)),
    )

    belfry = model.part("belfry_frame")
    belfry.visual(
        Cylinder(radius=2.55 * scale, length=0.90 * scale),
        origin=Origin(xyz=(0.0, 0.0, 0.45 * scale)),
        material=trim,
        name="lower_belfry_ring", material_class_id="metal.steel_bare",
    )
    belfry.visual(
        Cylinder(radius=2.75 * scale, length=0.90 * scale),
        origin=Origin(xyz=(0.0, 0.0, 4.15 * scale)),
        material=trim,
        name="upper_belfry_ring", material_class_id="metal.steel_bare",
    )
    for index in range(8):
        ang = (index + 0.5) * (math.tau / 8.0)
        belfry.visual(
            Cylinder(radius=0.22 * scale, length=3.30 * scale),
            origin=Origin(
                xyz=(2.15 * scale * math.cos(ang), 2.15 * scale * math.sin(ang), 2.35 * scale)
            ),
            material=stone,
            name=f"belfry_column_{index + 1}", material_class_id="stone.cut_sedimentary",
        )
    belfry.visual(
        Box((1.95 * scale, 0.18 * scale, 2.70 * scale)),
        origin=Origin(xyz=(0.0, 2.13 * scale, 2.35 * scale)),
        material=trim,
        name="clock_panel", material_class_id="metal.steel_bare",
    )
    for panel_spec in belfry_face_specs(resolved)[1:]:
        panel_ratio = 2.13 / 2.22
        belfry.visual(
            Box((1.95 * scale, 0.18 * scale, 2.70 * scale)),
            origin=Origin(
                xyz=(
                    panel_spec.center[0] * panel_ratio,
                    panel_spec.center[1] * panel_ratio,
                    panel_spec.center[2],
                ),
                rpy=(0.0, 0.0, panel_spec.rpy[2]),
            ),
            material=trim,
            name=f"clock_panel_{panel_spec.name}", material_class_id="metal.steel_bare",
        )

    roof = model.part("roof")
    roof.visual(
        Cylinder(radius=2.45 * scale, length=0.25 * scale),
        origin=Origin(xyz=(0.0, 0.0, 0.125 * scale)),
        material=roof_m,
        name="roof_drum", material_class_id="metal.blackened_gunmetal",
    )
    roof.visual(
        mesh_from_geometry(
            ConeGeometry(radius=2.35 * scale, height=2.80 * scale, radial_segments=48, closed=True),
            "campanile_roof",
        ),
        origin=Origin(xyz=(0.0, 0.0, 1.65 * scale)),
        material=roof_m,
        name="roof_cone", material_class_id="metal.blackened_gunmetal",
    )

    model.articulation(
        "shaft_to_belfry",
        ArticulationType.FIXED,
        parent=shaft,
        child=belfry,
        origin=Origin(xyz=(0.0, 0.0, shaft_h)),
    )
    model.articulation(
        "belfry_to_roof",
        ArticulationType.FIXED,
        parent=belfry,
        child=roof,
        origin=Origin(xyz=(0.0, 0.0, 4.60 * scale)),
    )

    if resolved.has_bell:
        bell_asm = model.part("bell_assembly")
        bell_asm.visual(
            Box((1.60 * scale, 0.24 * scale, 0.20 * scale)),
            origin=Origin(),
            material=trim,
            name="bell_beam", material_class_id="metal.steel_bare",
        )
        bell_asm.visual(
            Cylinder(radius=0.08 * scale, length=1.10 * scale),
            origin=Origin(xyz=(0.0, 0.0, -0.55 * scale)),
            material=roof_m,
            name="bell_hanger", material_class_id="metal.blackened_gunmetal",
        )
        bell_shell = ConeGeometry(
            radius=0.70 * scale, height=1.20 * scale, radial_segments=40, closed=True
        )
        bell_shell.rotate_x(math.pi)
        bell_asm.visual(
            mesh_from_geometry(bell_shell, "bell_shell"),
            origin=Origin(xyz=(0.0, 0.0, -1.13 * scale)),
            material=bronze,
            name="bell_shell", material_class_id="metal.bronze_cast",
        )
        # The beam seats into the underside of the upper belfry ring, so the
        # FIXED joint origin lands inside both parent ring and child beam.
        model.articulation(
            "belfry_to_bell",
            ArticulationType.FIXED,
            parent=belfry,
            child=bell_asm,
            origin=Origin(xyz=(0.0, 0.0, 3.75 * scale)),
        )

    return base, shaft, belfry


# --------------------------------------------------------------------------- #
# Slot B: clock_dial modules
# --------------------------------------------------------------------------- #


def _build_integrated_dials(
    model: ArticulatedObject,
    tower,
    resolved: ResolvedClockTowerConfig,
    mats: dict,
    *,
    dial_ring_mesh,
    marker_mesh,
    face_specs: list[FaceSpec] | None = None,
) -> None:
    """adopted: S1 004c708c — dial glass/rim/marks baked on tower per face."""
    steel = mats["steel"]
    frosted = mats["frosted_glass"]
    warm = mats["warm_led"]
    dr = resolved.dial_radius

    specs = face_specs if face_specs is not None else face_specs_for_count(resolved)
    for spec_index, spec in enumerate(specs):
        rpy = spec.rpy
        axis = spec.normal_axis
        sign = spec.normal_sign

        tower.visual(
            Cylinder(radius=dr, length=0.040),
            origin=Origin(xyz=_offset_along_normal(spec.center, axis, sign, 0.000), rpy=rpy),
            material=frosted,
            name=f"dial_glass_{spec_index}", material_class_id="glass.frosted_smooth",
        )
        tower.visual(
            dial_ring_mesh,
            origin=Origin(xyz=_offset_along_normal(spec.center, axis, sign, 0.001), rpy=rpy),
            material=steel,
            name=f"steel_rim_{spec_index}", material_class_id="metal.steel_bare",
        )
        tower.visual(
            marker_mesh,
            origin=Origin(xyz=_offset_along_normal(spec.center, axis, sign, 0.001), rpy=rpy),
            material=warm,
            name=f"hour_marks_{spec_index}", material_class_id="tech.emissive_surface",
        )


def _build_campanile_radial_dials(
    model: ArticulatedObject,
    tower,
    resolved: ResolvedClockTowerConfig,
    mats: dict,
    *,
    dial_ring_mesh,
    marker_mesh,
) -> None:
    """Integrated dials on a round campanile shaft (cylindrical face placement)."""
    steel = mats["steel"]
    frosted = mats["frosted_glass"]
    warm = mats["warm_led"]
    scale = resolved.tower_height / 13.0
    clock_z = 9.70 * scale
    shaft_r = 0.995 * scale
    dr = resolved.dial_radius

    angles = [0.0]
    if resolved.face_count >= 2:
        angles = [0.0, math.pi]
    if resolved.face_count >= 3:
        angles = [i * 2.0 * math.pi / 3.0 for i in range(3)]
    if resolved.face_count >= 4:
        angles = [0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0]
    angles = angles[: resolved.face_count]

    for spec_index, ang in enumerate(angles):
        x = shaft_r * math.sin(ang)
        y = -shaft_r * math.cos(ang)
        rpy = (math.pi / 2.0, 0.0, ang)
        tower.visual(
            Cylinder(radius=dr, length=0.040),
            origin=Origin(xyz=(x, y, clock_z), rpy=rpy),
            material=frosted,
            name=f"dial_glass_{spec_index}", material_class_id="glass.frosted_smooth",
        )
        tower.visual(
            dial_ring_mesh,
            origin=Origin(
                xyz=(x + 0.001 * math.sin(ang), y - 0.001 * math.cos(ang), clock_z), rpy=rpy
            ),
            material=steel,
            name=f"steel_rim_{spec_index}", material_class_id="metal.steel_bare",
        )
        tower.visual(
            marker_mesh,
            origin=Origin(
                xyz=(x + 0.001 * math.sin(ang), y - 0.001 * math.cos(ang), clock_z), rpy=rpy
            ),
            material=warm,
            name=f"hour_marks_{spec_index}", material_class_id="tech.emissive_surface",
        )


def _build_single_face_dial(
    tower,
    resolved: ResolvedClockTowerConfig,
    mats: dict,
    *,
    tower_style: TowerStyle = "campanile_round",
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """adopted: S2 08ab090 — single front face rim + markers."""
    clock_white = mats["frosted_glass"]
    clock_black = mats["hand"]
    gold = mats["warm_led"]
    dr = resolved.dial_radius

    if tower_style == "glazed_multiface":
        spec = face_specs_for_count(resolved)[0]
        rpy = spec.rpy
        axis = spec.normal_axis
        sign = spec.normal_sign
        center = spec.center
        face_offset = 0.001

        tower.visual(
            Cylinder(radius=dr * 1.15, length=0.105),
            origin=Origin(
                xyz=_offset_along_normal(center, axis, sign, face_offset - 0.010), rpy=rpy
            ),
            material=clock_black,
            name="clock_rim", material_class_id="metal.blackened_gunmetal",
        )
        tower.visual(
            Cylinder(radius=dr, length=0.040),
            origin=Origin(xyz=_offset_along_normal(center, axis, sign, face_offset), rpy=rpy),
            material=clock_white,
            name="clock_face", material_class_id="glass.frosted_smooth",
        )
        for i in range(12):
            angle = i * math.tau / 12.0
            marker_radius = dr * 0.90
            marker_long = 0.125 if i % 3 == 0 else 0.085
            marker_wide = 0.035 if i % 3 == 0 else 0.024
            local_x = marker_radius * math.sin(angle)
            local_z = marker_radius * math.cos(angle)
            if axis == "y":
                marker_xyz = (
                    local_x,
                    center[1] + sign * (0.018 + face_offset),
                    center[2] + local_z,
                )
                marker_rpy = (0.0, angle, 0.0)
            else:
                marker_xyz = (
                    center[0] + local_x,
                    center[1] + sign * (0.018 + face_offset),
                    center[2] + local_z,
                )
                marker_rpy = (0.0, angle, 0.0)
            tower.visual(
                Box((marker_wide, 0.018, marker_long)),
                origin=Origin(xyz=marker_xyz, rpy=marker_rpy),
                material=clock_black,
                name=f"hour_marker_{i}", material_class_id="metal.blackened_gunmetal",
            )
        tower.visual(
            Cylinder(radius=0.082, length=0.018),
            origin=Origin(
                xyz=_offset_along_normal(center, axis, sign, face_offset + 0.008), rpy=rpy
            ),
            material=gold,
            name="center_bearing", material_class_id="metal.precious_gold",
        )
        hand_center = _offset_along_normal(center, axis, sign, 0.020)
        if axis == "y":
            hand_axis = (0.0, float(sign), 0.0)
        else:
            hand_axis = (float(sign), 0.0, 0.0)
        return hand_center, hand_axis

    scale = resolved.tower_height / 13.0
    clock_z = 9.70 * scale
    shaft_r = 1.00 * scale
    face_y = -shaft_r
    tower.visual(
        Cylinder(radius=dr * 1.15, length=0.105),
        origin=Origin(xyz=(0.0, face_y + 0.045 * scale, clock_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=clock_black,
        name="clock_rim", material_class_id="metal.blackened_gunmetal",
    )
    tower.visual(
        Cylinder(radius=dr, length=0.040),
        origin=Origin(xyz=(0.0, face_y, clock_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=clock_white,
        name="clock_face", material_class_id="glass.frosted_smooth",
    )
    for i in range(12):
        angle = i * math.tau / 12.0
        marker_radius = dr * 0.90
        marker_long = 0.125 if i % 3 == 0 else 0.085
        marker_wide = 0.035 if i % 3 == 0 else 0.024
        tower.visual(
            Box((marker_wide, 0.030, marker_long)),
            origin=Origin(
                xyz=(
                    marker_radius * math.sin(angle),
                    face_y - 0.015 * scale,
                    clock_z + marker_radius * math.cos(angle),
                ),
                rpy=(0.0, angle, 0.0),
            ),
            material=clock_black,
            name=f"hour_marker_{i}", material_class_id="metal.blackened_gunmetal",
        )
    tower.visual(
        Cylinder(radius=0.082, length=0.018),
        origin=Origin(xyz=(0.0, face_y - 0.009 * scale, clock_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=gold,
        name="center_bearing", material_class_id="metal.precious_gold",
    )
    return (0.0, face_y - 0.020 * scale, clock_z), (0.0, -1.0, 0.0)


def _build_separate_clock_face_part(
    model: ArticulatedObject,
    parent_part,
    resolved: ResolvedClockTowerConfig,
    mats: dict,
    *,
    mount_origin: Origin,
) -> ArticulatedObject:
    """adopted: S3 496b656 — independent clock_face part + markers."""
    dial_white = mats["frosted_glass"]
    marker_dark = mats["warm_led"]
    metal = mats["steel"]
    dr = resolved.dial_radius

    clock_face = model.part("clock_face")
    clock_face.visual(
        Cylinder(radius=dr, length=0.024),
        origin=Origin(xyz=(0.0, 0.0, 0.012)),
        material=dial_white,
        name="dial_disk", material_class_id="glass.frosted_smooth",
    )
    clock_face.visual(
        mesh_from_geometry(
            LatheGeometry.from_shell_profiles(
                [(dr * 1.14, 0.0), (dr * 1.14, 0.064)],
                [(dr, 0.0), (dr, 0.064)],
                segments=48,
                start_cap="flat",
                end_cap="flat",
            ),
            "clock_bezel_ring",
        ),
        material=metal,
        name="bezel", material_class_id="metal.steel_bare",
    )
    clock_face.visual(
        Cylinder(radius=dr * 0.12, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, 0.027)),
        material=marker_dark,
        name="center_boss", material_class_id="metal.blackened_gunmetal",
    )
    for index in range(12):
        marker_angle = index * (math.pi / 6.0)
        marker_x = -dr * 0.84 * math.cos(marker_angle)
        marker_y = dr * 0.84 * math.sin(marker_angle)
        marker_long = 0.22 if index % 3 == 0 else 0.14
        marker_wide = 0.07 if index % 3 == 0 else 0.05
        clock_face.visual(
            Box((marker_long, marker_wide, 0.010)),
            origin=Origin(xyz=(marker_x, marker_y, 0.026), rpy=(0.0, 0.0, -marker_angle)),
            material=marker_dark,
            name=f"marker_{index}", material_class_id="metal.blackened_gunmetal",
        )

    model.articulation(
        "parent_to_clock_face",
        ArticulationType.FIXED,
        parent=parent_part,
        child=clock_face,
        origin=mount_origin,
    )
    return clock_face


def _fluted_section(
    z: float, *, radius: float, groove_depth: float, flute_count: int = 16, samples: int = 96
):
    points = []
    for idx in range(samples):
        angle = 2.0 * math.pi * idx / samples
        groove = 0.5 + 0.5 * math.cos(flute_count * angle)
        local_radius = radius - groove_depth * groove * groove
        points.append((local_radius * math.cos(angle), local_radius * math.sin(angle), z))
    return points


def _build_dual_housing_dial(
    model: ArticulatedObject,
    resolved: ResolvedClockTowerConfig,
    mats: dict,
) -> tuple[ArticulatedObject, ArticulatedObject]:
    """adopted: S4 89a4bced — column + housing with front/rear dial features."""
    cast_iron = mats["concrete"]
    brass = mats["steel"]
    dial_enamel = mats["frosted_glass"]
    hand_black = mats["warm_led"]

    column = model.part("column")
    column.visual(
        Cylinder(radius=0.22, length=0.05),
        origin=Origin(xyz=(0.0, 0.0, 0.025)),
        material=cast_iron,
        name="base_foot", material_class_id="metal.cast_iron_bare",
    )
    column.visual(
        Cylinder(radius=0.16, length=0.10),
        origin=Origin(xyz=(0.0, 0.0, 0.10)),
        material=cast_iron,
        name="base_plinth", material_class_id="metal.cast_iron_bare",
    )
    column.visual(
        Cylinder(radius=0.14, length=0.08),
        origin=Origin(xyz=(0.0, 0.0, 0.19)),
        material=cast_iron,
        name="shaft_base_collar", material_class_id="metal.cast_iron_bare",
    )
    shaft_mesh = section_loft(
        [
            _fluted_section(0.12, radius=0.074, groove_depth=0.008),
            _fluted_section(2.56, radius=0.062, groove_depth=0.007),
        ]
    )
    column.visual(
        mesh_from_geometry(shaft_mesh, "fluted_column_shaft"),
        material=cast_iron,
        name="fluted_shaft", material_class_id="metal.cast_iron_bare",
    )
    column.visual(
        Cylinder(radius=0.10, length=0.22),
        origin=Origin(xyz=(0.0, 0.0, 2.67)),
        material=cast_iron,
        name="shaft_top_collar", material_class_id="metal.cast_iron_bare",
    )
    column.visual(
        Cylinder(radius=0.13, length=0.08),
        origin=Origin(xyz=(0.0, 0.0, 2.78)),
        material=brass,
        name="capital_plate", material_class_id="metal.brass_aged",
    )

    housing = model.part("housing")
    face_z = resolved.face_center_z if resolved.face_center_z < 2.0 else 0.56
    housing.visual(
        Cylinder(radius=0.055, length=0.13),
        origin=Origin(xyz=(0.0, 0.0, 0.065)),
        material=cast_iron,
        name="support_stem", material_class_id="metal.cast_iron_bare",
    )
    housing.visual(
        Cylinder(radius=0.22, length=0.34),
        origin=Origin(xyz=(0.0, 0.0, 0.30)),
        material=cast_iron,
        name="stem_shell_bridge", material_class_id="metal.cast_iron_bare",
    )
    shell = LatheGeometry.from_shell_profiles(
        [
            (0.330, -0.090),
            (0.388, -0.122),
            (0.405, -0.130),
            (0.405, 0.130),
            (0.388, 0.122),
            (0.330, 0.090),
        ],
        [
            (0.288, -0.088),
            (0.340, -0.118),
            (0.352, -0.124),
            (0.352, 0.124),
            (0.340, 0.118),
            (0.288, 0.088),
        ],
        segments=72,
        start_cap="flat",
        end_cap="flat",
    )
    shell.rotate_x(-math.pi * 0.5).translate(0.0, 0.0, face_z)
    housing.visual(
        mesh_from_geometry(shell, "clock_housing_shell"), material=cast_iron, name="clock_shell", material_class_id="metal.cast_iron_bare"
    )
    dr = resolved.dial_radius * 0.62
    housing.visual(
        Cylinder(radius=dr, length=0.010),
        origin=Origin(xyz=(0.0, 0.108, face_z), rpy=(math.pi * 0.5, 0.0, 0.0)),
        material=dial_enamel,
        name="front_dial", material_class_id="glass.frosted_smooth",
    )
    housing.visual(
        Cylinder(radius=dr, length=0.010),
        origin=Origin(xyz=(0.0, -0.108, face_z), rpy=(math.pi * 0.5, 0.0, 0.0)),
        material=dial_enamel,
        name="rear_dial", material_class_id="glass.frosted_smooth",
    )
    for side_sign, prefix, face_y in ((1.0, "front", 0.112), (-1.0, "rear", -0.112)):
        for idx in range(12):
            angle = idx * math.pi / 6.0
            mark_radius = dr * 0.84
            x = mark_radius * math.sin(angle)
            z = face_z + mark_radius * math.cos(angle)
            is_quarter = idx % 3 == 0
            housing.visual(
                Box((0.016 if is_quarter else 0.010, 0.004, 0.042 if is_quarter else 0.028)),
                origin=Origin(xyz=(x, face_y, z), rpy=(0.0, angle, 0.0)),
                material=hand_black,
                name=f"{prefix}_marker_{idx}", material_class_id="metal.blackened_gunmetal",
            )
    housing.visual(
        Cylinder(radius=0.14, length=0.28),
        origin=Origin(xyz=(0.0, 0.0, face_z + 0.20)),
        material=brass,
        name="finial_spire", material_class_id="metal.brass_aged",
    )

    model.articulation(
        "column_to_housing",
        ArticulationType.FIXED,
        parent=column,
        child=housing,
        origin=Origin(xyz=(0.0, 0.0, 2.785)),
    )
    return column, housing


# --------------------------------------------------------------------------- #
# Slot C: hand_mechanism modules
# --------------------------------------------------------------------------- #


def _add_hand_geometry_s4(
    hand,
    *,
    side_sign: float,
    blade_length: float,
    blade_width: float,
    blade_thickness: float,
    hub_radius: float,
    hub_length: float,
    tip_length: float,
    tail_length: float,
    material,
) -> None:
    """adopted: S4 89a4bced — ornate spade hand geometry."""
    y_center = side_sign * hub_length * 0.58
    hand.visual(
        Cylinder(radius=hub_radius, length=hub_length),
        origin=Origin(xyz=(0.0, side_sign * hub_length * 0.5, 0.0), rpy=(math.pi * 0.5, 0.0, 0.0)),
        material=material,
        name="hub", material_class_id="metal.blackened_gunmetal",
    )
    hand.visual(
        Box((blade_width, blade_thickness, blade_length)),
        origin=Origin(xyz=(0.0, y_center, blade_length * 0.5)),
        material=material,
        name="blade", material_class_id="metal.blackened_gunmetal",
    )
    hand.visual(
        Box((blade_width * 1.85, blade_thickness, tip_length)),
        origin=Origin(xyz=(0.0, y_center, blade_length * 0.70)),
        material=material,
        name="spade_body", material_class_id="metal.blackened_gunmetal",
    )
    hand.visual(
        Box((blade_width * 0.55, blade_thickness, tail_length)),
        origin=Origin(xyz=(0.0, y_center, -tail_length * 0.5)),
        material=material,
        name="counter_tail", material_class_id="metal.blackened_gunmetal",
    )


def _build_indexed_multiface_hands(
    model: ArticulatedObject,
    parent_part,
    resolved: ResolvedClockTowerConfig,
    mats: dict,
    *,
    hour_hub_mesh,
    face_specs: list[FaceSpec] | None = None,
) -> list[str]:
    """adopted: S1 004c708c — hour_hand_i/minute_hand_i + per-face CONTINUOUS joints."""
    dark = mats["hand"]
    joint_names: list[str] = []

    specs = face_specs if face_specs is not None else face_specs_for_count(resolved)
    for spec_index, spec in enumerate(specs):
        hour = model.part(f"hour_hand_{spec_index}")
        hour.visual(
            Box((0.080, 0.400, 0.012)),
            origin=Origin(xyz=(0.0, 0.260, 0.015)),
            material=dark,
            name="hour_blade", material_class_id="metal.blackened_gunmetal",
        )
        hour.visual(
            Cylinder(radius=0.030, length=resolved.hour_z_offset),
            origin=Origin(xyz=(0.0, 0.0, resolved.hour_z_offset * 0.5)),
            material=dark,
            name="hour_spindle", material_class_id="metal.blackened_gunmetal",
        )
        hour.visual(
            hour_hub_mesh, origin=Origin(xyz=(0.0, 0.0, 0.0)), material=dark, name="hour_hub", material_class_id="metal.blackened_gunmetal"
        )
        hour.visual(
            Box((0.038, 0.110, 0.010)),
            origin=Origin(xyz=(0.0, -0.100, 0.015)),
            material=dark,
            name="hour_tail", material_class_id="metal.blackened_gunmetal",
        )

        minute = model.part(f"minute_hand_{spec_index}")
        minute.visual(
            Cylinder(radius=0.020, length=0.075),
            origin=Origin(xyz=(0.0, 0.0, 0.0375)),
            material=dark,
            name="minute_spindle", material_class_id="metal.blackened_gunmetal",
        )
        minute.visual(
            Box((0.044, 0.615, 0.006)),
            origin=Origin(xyz=(0.0, 0.285, resolved.minute_z_offset)),
            material=dark,
            name="minute_blade", material_class_id="metal.blackened_gunmetal",
        )
        minute.visual(
            Cylinder(radius=0.052, length=0.012),
            origin=Origin(xyz=(0.0, 0.0, resolved.minute_z_offset)),
            material=dark,
            name="minute_hub", material_class_id="metal.blackened_gunmetal",
        )
        minute.visual(
            Box((0.026, 0.185, 0.005)),
            origin=Origin(xyz=(0.0, -0.072, resolved.minute_z_offset)),
            material=dark,
            name="minute_tail", material_class_id="metal.blackened_gunmetal",
        )

        joint_xyz = (0.0, 0.0, 0.020)
        rpy = (0.0, 0.0, 0.0)
        hub_offset = 0.020
        if parent_part.name != "clock_face":
            if face_specs is not None:
                hub_offset = 0.006
            joint_xyz = _offset_along_normal(
                spec.center, spec.normal_axis, spec.normal_sign, hub_offset
            )
            rpy = spec.rpy
            if face_specs is not None and parent_part.name in (
                "tower",
                "shaft",
                "belfry_frame",
                "housing",
            ):
                parent_part.visual(
                    Cylinder(radius=0.055, length=0.040),
                    origin=Origin(xyz=joint_xyz, rpy=rpy),
                    material=mats["warm_led"],
                    name=f"dial_hub_{spec_index}", material_class_id="tech.emissive_surface",
                )
        jh = f"face_{spec_index}_hour"
        jm = f"face_{spec_index}_minute"
        model.articulation(
            jh,
            ArticulationType.CONTINUOUS,
            parent=parent_part,
            child=hour,
            origin=Origin(xyz=joint_xyz, rpy=rpy),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=0.35),
            motion_properties=MotionProperties(damping=0.01, friction=0.002),
        )
        model.articulation(
            jm,
            ArticulationType.CONTINUOUS,
            parent=parent_part,
            child=minute,
            origin=Origin(xyz=joint_xyz, rpy=rpy),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=1.5, velocity=6.4),
            motion_properties=MotionProperties(damping=0.005, friction=0.001),
        )
        joint_names.extend([jh, jm])
    return joint_names


def _build_mesh_blade_hands(
    model: ArticulatedObject,
    parent_part,
    resolved: ResolvedClockTowerConfig,
    mats: dict,
    *,
    hand_origin: Origin,
    hand_axis: tuple[float, float, float],
    blade_length_cap: float | None = None,
) -> None:
    """adopted: S2 08ab090 — mesh _hand_shape hour/minute parts."""
    dark = mats["hand"]
    gold = mats["warm_led"]
    hour_tip_length = resolved.hour_hand_length
    minute_tip_length = resolved.minute_hand_length
    if blade_length_cap is not None:
        hour_tip_length = min(hour_tip_length, blade_length_cap)
        minute_tip_length = min(minute_tip_length, blade_length_cap)
    hour_mesh = _cq_mesh(
        model,
        _hand_shape(
            tip_length=hour_tip_length,
            tail_length=0.10,
            root_half_width=0.055,
            tip_half_width=0.018,
            thickness=0.018,
        ),
        "hour_hand_blade",
    )
    minute_mesh = _cq_mesh(
        model,
        _hand_shape(
            tip_length=minute_tip_length,
            tail_length=0.13,
            root_half_width=0.038,
            tip_half_width=0.010,
            thickness=0.014,
        ),
        "minute_hand_blade",
    )

    hour = model.part("hour_hand")
    hour.visual(
        Cylinder(radius=0.075, length=0.040),
        origin=Origin(xyz=(0.0, 0.0, 0.020)),
        material=dark,
        name="hour_axle", material_class_id="metal.blackened_gunmetal",
    )
    hour.visual(
        hour_mesh, origin=Origin(xyz=(0.0, -0.001, -0.009)), material=dark, name="hour_blade", material_class_id="metal.blackened_gunmetal"
    )
    hour.visual(
        Cylinder(radius=0.075, length=0.018),
        origin=Origin(xyz=(0.0, -0.006, 0.010), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=dark,
        name="hour_hub", material_class_id="metal.blackened_gunmetal",
    )

    minute = model.part("minute_hand")
    minute.visual(
        Cylinder(radius=0.030, length=0.050),
        origin=Origin(xyz=(0.0, 0.0, 0.025)),
        material=dark,
        name="minute_axle", material_class_id="metal.blackened_gunmetal",
    )
    minute.visual(
        Box((0.040, 0.040, 0.012)),
        origin=Origin(xyz=(0.0, -0.012, 0.028)),
        material=dark,
        name="minute_blade_root", material_class_id="metal.blackened_gunmetal",
    )
    minute.visual(
        minute_mesh, origin=Origin(xyz=(0.0, -0.012, 0.028)), material=dark, name="minute_blade", material_class_id="metal.blackened_gunmetal"
    )
    minute.visual(
        Cylinder(radius=0.095, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, 0.038), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=gold,
        name="minute_cap", material_class_id="metal.precious_gold",
    )

    model.articulation(
        "hour_hand_rotation",
        ArticulationType.CONTINUOUS,
        parent=parent_part,
        child=hour,
        origin=hand_origin,
        axis=hand_axis,
        motion_limits=MotionLimits(effort=0.05, velocity=0.15),
    )
    model.articulation(
        "minute_hand_rotation",
        ArticulationType.CONTINUOUS,
        parent=parent_part,
        child=minute,
        origin=hand_origin,
        axis=hand_axis,
        motion_limits=MotionLimits(effort=0.04, velocity=1.0),
    )


def _build_stacked_simple_hands(
    model: ArticulatedObject,
    parent_part,
    resolved: ResolvedClockTowerConfig,
    mats: dict,
    *,
    hand_origin: Origin | None = None,
    fit_radius: float | None = None,
) -> None:
    """adopted: S3 496b656 — hour/minute on clock_face with stacked Z offset."""
    dark = mats["hand"]
    hl = resolved.hour_hand_length
    ml = resolved.minute_hand_length
    hour_scale = 1.0
    minute_scale = 1.0
    if fit_radius is not None:
        # Scale each hand down uniformly so its sweep stays on a small dial.
        hour_scale = min(1.0, fit_radius / max(2.0 * hl, 1.8 * hl + 0.12))
        minute_scale = min(1.0, fit_radius / max(2.0 * ml, 1.8 * ml + 0.10))
    origin = hand_origin if hand_origin is not None else Origin()

    hs = hour_scale
    hour = model.part("hour_hand")
    hour.visual(
        Cylinder(radius=0.13 * hs, length=0.024 * hs),
        origin=Origin(xyz=(0.0, 0.0, 0.012 * hs)),
        material=dark,
        name="hour_hub", material_class_id="metal.blackened_gunmetal",
    )
    hour.visual(
        Box((hl * 2.0 * hs, 0.16 * hs, 0.012 * hs)),
        origin=Origin(xyz=(-hl * hs, 0.0, 0.012 * hs)),
        material=dark,
        name="hour_blade", material_class_id="metal.blackened_gunmetal",
    )
    hour.visual(
        Box((0.24 * hs, 0.08 * hs, 0.012 * hs)),
        origin=Origin(xyz=(-hl * 1.8 * hs, 0.0, 0.012 * hs)),
        material=dark,
        name="hour_tip", material_class_id="metal.blackened_gunmetal",
    )

    ms = minute_scale
    minute = model.part("minute_hand")
    minute.visual(
        Cylinder(radius=0.09 * ms, length=0.020 * ms),
        origin=Origin(xyz=(0.0, 0.0, 0.020 * ms)),
        material=dark,
        name="minute_hub", material_class_id="metal.blackened_gunmetal",
    )
    minute.visual(
        Box((ml * 2.0 * ms, 0.12 * ms, 0.010 * ms)),
        origin=Origin(xyz=(-ml * ms, 0.0, 0.020 * ms)),
        material=dark,
        name="minute_blade", material_class_id="metal.blackened_gunmetal",
    )
    minute.visual(
        Box((0.20 * ms, 0.07 * ms, 0.010 * ms)),
        origin=Origin(xyz=(-ml * 1.8 * ms, 0.0, 0.020 * ms)),
        material=dark,
        name="minute_tip", material_class_id="metal.blackened_gunmetal",
    )

    model.articulation(
        "clock_face_to_hour_hand",
        ArticulationType.CONTINUOUS,
        parent=parent_part,
        child=hour,
        origin=origin,
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=6.0),
    )
    model.articulation(
        "clock_face_to_minute_hand",
        ArticulationType.CONTINUOUS,
        parent=parent_part,
        child=minute,
        origin=origin,
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=12.0),
    )


def _build_front_rear_hands(
    model: ArticulatedObject,
    housing,
    resolved: ResolvedClockTowerConfig,
    mats: dict,
) -> None:
    """adopted: S4 89a4bced — front/rear hour/minute named hands."""
    dark = mats["hand"]
    face_z = resolved.face_center_z if resolved.face_center_z < 2.0 else 0.56
    front_y = 0.110
    rear_y = -0.110

    front_hour = model.part("front_hour_hand")
    _add_hand_geometry_s4(
        front_hour,
        side_sign=1.0,
        blade_length=resolved.hour_hand_length * 0.46,
        blade_width=0.030,
        blade_thickness=0.005,
        hub_radius=0.023,
        hub_length=0.012,
        tip_length=0.055,
        tail_length=0.060,
        material=dark,
    )
    front_minute = model.part("front_minute_hand")
    _add_hand_geometry_s4(
        front_minute,
        side_sign=1.0,
        blade_length=resolved.minute_hand_length * 0.44,
        blade_width=0.022,
        blade_thickness=0.004,
        hub_radius=0.016,
        hub_length=0.010,
        tip_length=0.060,
        tail_length=0.080,
        material=dark,
    )
    rear_hour = model.part("rear_hour_hand")
    _add_hand_geometry_s4(
        rear_hour,
        side_sign=-1.0,
        blade_length=resolved.hour_hand_length * 0.46,
        blade_width=0.030,
        blade_thickness=0.005,
        hub_radius=0.023,
        hub_length=0.012,
        tip_length=0.055,
        tail_length=0.060,
        material=dark,
    )
    rear_minute = model.part("rear_minute_hand")
    _add_hand_geometry_s4(
        rear_minute,
        side_sign=-1.0,
        blade_length=resolved.minute_hand_length * 0.44,
        blade_width=0.022,
        blade_thickness=0.004,
        hub_radius=0.016,
        hub_length=0.010,
        tip_length=0.060,
        tail_length=0.080,
        material=dark,
    )

    model.articulation(
        "housing_to_front_hour",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=front_hour,
        origin=Origin(xyz=(0.0, front_y, face_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=2.0),
    )
    model.articulation(
        "housing_to_front_minute",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=front_minute,
        origin=Origin(xyz=(0.0, front_y + 0.010, face_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=2.5),
    )
    model.articulation(
        "housing_to_rear_hour",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=rear_hour,
        origin=Origin(xyz=(0.0, rear_y, face_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=2.0),
    )
    model.articulation(
        "housing_to_rear_minute",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=rear_minute,
        origin=Origin(xyz=(0.0, rear_y - 0.010, face_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=2.5),
    )


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #


def slot_choices_for_config(r: ResolvedClockTowerConfig) -> list[tuple[str, str]]:
    return [
        ("tower_spine", r.tower_style),
        ("clock_dial", r.dial_style),
        ("hand_mechanism", r.hand_style),
        ("face_count", str(r.face_count)),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def build_clock_tower_with_rotating_hour_and_minute_hands(
    config: ClockTowerConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or ClockTowerConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-clock-tower-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)
    model.meta["adopted_source_ids"] = ("S1", "S2", "S3", "S4", "S5")
    model.meta["slot_choices"] = slot_choices_for_config(resolved)

    palette = PALETTES[resolved.palette_theme]
    mats = {
        "steel": model.material("steel", rgba=palette["steel"]),
        "dark_steel": model.material("dark_steel", rgba=palette["dark_steel"]),
        "glass": model.material("glass", rgba=palette["glass"]),
        "frosted_glass": model.material("frosted_glass", rgba=palette["frosted_glass"]),
        "concrete": model.material("concrete", rgba=palette["concrete"]),
        "warm_led": model.material("warm_led", rgba=palette["warm_led"]),
        "hand": model.material("hand_metal", rgba=palette["hand"]),
    }

    # Shared meshes for S1 anchor path.
    dial_ring_mesh = _cq_mesh(model, _annulus(0.675, 0.605, 0.055), "beveled_clock_rim")
    marker_mesh = _cq_mesh(model, _marker_ring(0.490, 0.014), "connected_hour_marks")
    hour_hub_mesh = _cq_mesh(model, _annulus(0.075, 0.030, 0.030), "hollow_hour_hub")

    hand_parent = None
    camp_specs: list[FaceSpec] | None = None
    panel_specs: list[FaceSpec] | None = None

    if resolved.tower_style == "tiered_stack":
        base, shaft, _lantern = _build_tiered_stack_tower(model, resolved, mats)
        if resolved.dial_style == "separate_part":
            clock_face = _build_separate_clock_face_part(
                model,
                shaft,
                resolved,
                mats,
                mount_origin=Origin(
                    xyz=(resolved.shaft_width * 0.85 * 1.15, 0.0, resolved.face_center_z * 0.55),
                    rpy=(0.0, math.pi / 2.0, 0.0),
                ),
            )
            hand_parent = clock_face
        else:
            tower = shaft
            panel_specs = tiered_face_specs(resolved)
            _build_integrated_dials(
                model,
                tower,
                resolved,
                mats,
                dial_ring_mesh=dial_ring_mesh,
                marker_mesh=marker_mesh,
                face_specs=panel_specs,
            )
            hand_parent = tower
    elif resolved.tower_style == "belfry_column":
        base, shaft, belfry = _build_belfry_column_stack(model, resolved, mats)
        if resolved.dial_style == "separate_part":
            clock_face = _build_separate_clock_face_part(
                model,
                belfry,
                resolved,
                mats,
                mount_origin=Origin(
                    xyz=(
                        0.0,
                        2.216 * (resolved.tower_height / 18.0),
                        2.45 * (resolved.tower_height / 18.0),
                    ),
                    rpy=(-math.pi / 2.0, 0.0, 0.0),
                ),
            )
            hand_parent = clock_face
        else:
            panel_specs = belfry_face_specs(resolved)
            _build_integrated_dials(
                model,
                belfry,
                resolved,
                mats,
                dial_ring_mesh=dial_ring_mesh,
                marker_mesh=marker_mesh,
                face_specs=panel_specs,
            )
            hand_parent = belfry
    elif resolved.dial_style == "dual_housing":
        column, housing = _build_dual_housing_dial(model, resolved, mats)
        hand_parent = housing
        housing_face_z = resolved.face_center_z if resolved.face_center_z < 2.0 else 0.56
        panel_specs = [
            FaceSpec(
                "face_front",
                (0.0, 0.108, housing_face_z),
                (math.pi / 2.0, 0.0, math.pi),
                "y",
                1.0,
                (0.0, 0.0, 1.0),
            ),
            FaceSpec(
                "face_rear",
                (0.0, -0.108, housing_face_z),
                (math.pi / 2.0, 0.0, 0.0),
                "y",
                -1.0,
                (0.0, 0.0, 1.0),
            ),
        ]
    else:
        tower = model.part("tower")
        if resolved.tower_style == "glazed_multiface":
            _build_glazed_multiface_tower(model, tower, resolved, mats)
        else:
            _build_campanile_round_tower(model, tower, resolved, mats)

        use_integrated = resolved.dial_style == "integrated" or (
            resolved.dial_style == "separate_part"
            and resolved.hand_style == "indexed_multiface"
            and resolved.face_count > 1
        )
        if use_integrated:
            if resolved.tower_style == "campanile_round":
                _build_campanile_radial_dials(
                    model,
                    tower,
                    resolved,
                    mats,
                    dial_ring_mesh=dial_ring_mesh,
                    marker_mesh=marker_mesh,
                )
                camp_specs = campanile_face_specs(resolved)
                panel_specs = camp_specs
            else:
                _build_integrated_dials(
                    model,
                    tower,
                    resolved,
                    mats,
                    dial_ring_mesh=dial_ring_mesh,
                    marker_mesh=marker_mesh,
                )
            hand_parent = tower
        elif resolved.dial_style == "single_face":
            _build_single_face_dial(tower, resolved, mats, tower_style=resolved.tower_style)
            hand_parent = tower
        elif resolved.dial_style == "separate_part":
            scale = (
                resolved.tower_height / 13.0 if resolved.tower_style == "campanile_round" else 1.0
            )
            if resolved.tower_style == "campanile_round":
                mount_z = 9.70 * scale
                mount_y = 1.00 * scale
                mount_rpy = (math.pi / 2.0, 0.0, 0.0)
                dr = resolved.dial_radius
                tower.visual(
                    Cylinder(radius=dr * 1.15, length=0.14),
                    origin=Origin(xyz=(0.0, -mount_y + 0.05 * scale, mount_z), rpy=mount_rpy),
                    material=mats["hand"],
                    name="clock_face_lug", material_class_id="metal.blackened_gunmetal",
                )
                tower.visual(
                    Box((dr * 2.2, 0.24 * scale, dr * 2.2)),
                    origin=Origin(xyz=(0.0, -mount_y + 0.14 * scale, mount_z)),
                    material=mats["steel"],
                    name="clock_face_lug_pad", material_class_id="metal.steel_bare",
                )
            else:
                # Glazed head: bridge the glass clock-room wall with a lug and
                # seat the separate dial on it (mirrors the campanile lug).
                mount_z = resolved.face_center_z
                head_surface_y = resolved.head_size / 2.0
                mount_y = head_surface_y + 0.09
                mount_rpy = (math.pi / 2.0, 0.0, 0.0)
                tower.visual(
                    Cylinder(radius=resolved.dial_radius * 0.55, length=0.14),
                    origin=Origin(
                        xyz=(0.0, -head_surface_y - 0.04, mount_z), rpy=mount_rpy
                    ),
                    material=mats["hand"],
                    name="clock_face_lug", material_class_id="metal.blackened_gunmetal",
                )
            clock_face = _build_separate_clock_face_part(
                model,
                tower,
                resolved,
                mats,
                mount_origin=Origin(
                    xyz=(0.0, -mount_y, mount_z),
                    rpy=mount_rpy,
                ),
            )
            hand_parent = clock_face
        else:
            hand_parent = tower

    if resolved.hand_style == "indexed_multiface" and hand_parent is not None:
        _build_indexed_multiface_hands(
            model,
            hand_parent,
            resolved,
            mats,
            hour_hub_mesh=hour_hub_mesh,
            face_specs=panel_specs,
        )
    elif resolved.hand_style == "mesh_blade" and hand_parent is not None:
        blade_length_cap: float | None = None
        if hand_parent.name == "clock_face":
            origin = Origin()
            axis = (0.0, 0.0, -1.0)
        elif hand_parent.name == "housing":
            housing_face_z = resolved.face_center_z if resolved.face_center_z < 2.0 else 0.56
            origin = Origin(xyz=(0.0, 0.116, housing_face_z))
            axis = (0.0, 1.0, 0.0)
            # Keep the sweep on the small housing dial and above the capital.
            blade_length_cap = resolved.dial_radius * 0.62 * 0.85
        elif panel_specs is not None:
            spec = panel_specs[0]
            origin = Origin(
                xyz=_offset_along_normal(spec.center, spec.normal_axis, spec.normal_sign, 0.006),
                rpy=spec.rpy,
            )
            axis = (0.0, 0.0, 1.0)
            if hand_parent.name in ("tower", "shaft", "belfry_frame"):
                hand_parent.visual(
                    Cylinder(radius=0.055, length=0.040),
                    origin=origin,
                    material=mats["warm_led"],
                    name="hand_joint_hub", material_class_id="tech.emissive_surface",
                )
        elif resolved.tower_style == "campanile_round":
            scale = resolved.tower_height / 13.0
            origin = Origin(xyz=(0.0, -(1.00 + 0.02) * scale, 9.70 * scale))
            axis = (0.0, -1.0, 0.0)
        else:
            specs = face_specs_for_count(resolved)
            spec = specs[0]
            hub_offset = 0.006 if resolved.tower_style == "glazed_multiface" else 0.020
            origin = Origin(
                xyz=_offset_along_normal(
                    spec.center, spec.normal_axis, spec.normal_sign, hub_offset
                ),
                rpy=spec.rpy,
            )
            axis = (0.0, 0.0, 1.0)
            if hand_parent.name == "tower":
                hand_parent.visual(
                    Cylinder(radius=0.055, length=0.040),
                    origin=origin,
                    material=mats["warm_led"],
                    name="hand_joint_hub", material_class_id="tech.emissive_surface",
                )
        _build_mesh_blade_hands(
            model,
            hand_parent,
            resolved,
            mats,
            hand_origin=origin,
            hand_axis=axis,
            blade_length_cap=blade_length_cap,
        )
    elif resolved.hand_style == "stacked_simple" and hand_parent is not None:
        hand_origin: Origin | None = None
        fit_radius: float | None = None
        if hand_parent.name == "housing":
            housing_face_z = resolved.face_center_z if resolved.face_center_z < 2.0 else 0.56
            hand_origin = Origin(xyz=(0.0, 0.115, housing_face_z), rpy=(-math.pi / 2.0, 0.0, 0.0))
            fit_radius = resolved.dial_radius * 0.62 * 0.85
        elif panel_specs is not None and hand_parent.name in ("shaft", "belfry_frame"):
            spec = panel_specs[0]
            hand_origin = Origin(
                xyz=_offset_along_normal(spec.center, spec.normal_axis, spec.normal_sign, 0.006),
                rpy=spec.rpy,
            )
            if hand_parent.name == "belfry_frame":
                # Keep the sweep between the belfry rings and the roof drum.
                fit_radius = max(0.15, 1.45 * (resolved.tower_height / 18.0) - 0.06)
        _build_stacked_simple_hands(
            model, hand_parent, resolved, mats, hand_origin=hand_origin, fit_radius=fit_radius
        )
    elif resolved.hand_style == "front_rear":
        if "housing" not in {p.name for p in model.parts}:
            _build_dual_housing_dial(model, resolved, mats)
        housing = model.get_part("housing")
        _build_front_rear_hands(model, housing, resolved, mats)

    return model


def build_seeded_clock_tower_with_rotating_hour_and_minute_hands(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_clock_tower_with_rotating_hour_and_minute_hands(
        config_from_seed(seed), assets=assets
    )


def with_overrides(config: ClockTowerConfig, **kwargs: object) -> ClockTowerConfig:
    return replace(config, **kwargs)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _declare_captured_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    part_names = {p.name for p in model.parts}
    for tower_name in ("tower", "shaft", "belfry_frame", "housing", "clock_face"):
        if tower_name not in part_names:
            continue
        tower = model.get_part(tower_name)
        if "clock_face" in part_names and tower_name == "tower":
            ctx.allow_overlap(
                tower,
                model.get_part("clock_face"),
                elem_a="clock_face_lug",
                elem_b="bezel",
                reason="separate clock face bezel seats on the tower dial lug",
            )
            ctx.allow_overlap(
                tower,
                model.get_part("clock_face"),
                elem_a="clock_face_lug",
                elem_b="dial_disk",
                reason="separate clock face disk registers on the tower lug",
            )
        for hand_prefix in (
            "hour_hand",
            "minute_hand",
            "front_hour_hand",
            "front_minute_hand",
            "rear_hour_hand",
            "rear_minute_hand",
        ):
            if hand_prefix in part_names:
                ctx.allow_overlap(
                    tower,
                    model.get_part(hand_prefix),
                    reason="clock hand hub seats on dial center boss",
                )
                ctx.allow_isolated_part(
                    hand_prefix, reason="clock hands rotate on dial center axis"
                )
        for i in range(8):
            for prefix in ("hour_hand", "minute_hand"):
                name = f"{prefix}_{i}"
                if name in part_names:
                    ctx.allow_overlap(
                        tower,
                        model.get_part(name),
                        reason="indexed hand hub overlaps dial glass near center",
                    )
                    ctx.allow_isolated_part(
                        name, reason="indexed clock hands rotate on dial center axis"
                    )
            hour_name = f"hour_hand_{i}"
            minute_name = f"minute_hand_{i}"
            if hour_name in part_names and minute_name in part_names:
                ctx.allow_overlap(
                    model.get_part(hour_name),
                    model.get_part(minute_name),
                    elem_a="hour_spindle",
                    elem_b="minute_spindle",
                    reason="coaxial hour/minute hands share the dial axle (stacked movement)",
                )
                ctx.allow_overlap(
                    model.get_part(hour_name),
                    model.get_part(minute_name),
                    elem_a="hour_hub",
                    elem_b="minute_hub",
                    reason="stacked hand hubs nest at the dial center",
                )
    if "clock_face" in part_names:
        clock_face = model.get_part("clock_face")
        if "tower" in part_names:
            ctx.allow_overlap(
                clock_face,
                model.get_part("tower"),
                reason="clock_face FIXED mount overlaps tower lug",
            )
        for hand_name in part_names:
            if (
                hand_name in ("hour_hand", "minute_hand")
                or hand_name.startswith("hour_hand_")
                or hand_name.startswith("minute_hand_")
            ):
                ctx.allow_overlap(
                    clock_face,
                    model.get_part(hand_name),
                    reason="clock hands seat in the dial face bore",
                )
                ctx.allow_isolated_part(
                    hand_name, reason="clock hands rotate on dial face center axis"
                )
    if "hour_hand" in part_names and "minute_hand" in part_names:
        ctx.allow_overlap(
            model.get_part("hour_hand"),
            model.get_part("minute_hand"),
            reason="stacked coaxial hour/minute hands share the dial axle",
        )
    for hand_name in ("hour_hand", "minute_hand"):
        if hand_name in part_names:
            ctx.allow_isolated_part(hand_name, reason="clock hands rotate on dial center axis")
    if "housing" in part_names and "column" in part_names:
        ctx.allow_overlap(
            model.get_part("column"),
            model.get_part("housing"),
            elem_a="capital_plate",
            elem_b="support_stem",
            reason="housing stem registers on the column capital plate",
        )
    for fixed_child in (
        "shaft",
        "lantern_room",
        "belfry_frame",
        "roof",
        "bell_assembly",
        "clock_face",
        "housing",
    ):
        if fixed_child in part_names:
            for parent in ("base", "shaft", "belfry_frame"):
                if parent in part_names and parent != fixed_child:
                    ctx.allow_overlap(
                        model.get_part(parent),
                        model.get_part(fixed_child),
                        reason="FIXED stacked tower chain contact overlap",
                    )


def run_clock_tower_with_rotating_hour_and_minute_hands_tests(
    object_model: ArticulatedObject,
    config: ClockTowerConfig,
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_captured_overlaps(ctx, object_model)

    continuous = [
        j for j in object_model.articulations if j.articulation_type == ArticulationType.CONTINUOUS
    ]
    expected_joints = 2 * resolved.face_count
    if resolved.hand_style == "front_rear":
        expected_joints = 4
    elif resolved.hand_style in ("mesh_blade", "stacked_simple"):
        expected_joints = 2

    ctx.check(
        "continuous_hand_joint_count",
        len(continuous) == expected_joints,
        details=f"expected {expected_joints} CONTINUOUS hand joints, got {len(continuous)}",
    )

    roots = object_model.root_parts()
    ctx.check("single_root_exists", len(roots) == 1, details=str([p.name for p in roots]))

    if (
        resolved.tower_style == "glazed_multiface"
        and resolved.face_count == 4
        and resolved.hand_style == "indexed_multiface"
    ):
        normal_checks = [
            ("y", "hour_hand_0", "minute_hand_0"),
            ("y", "minute_hand_1", "hour_hand_1"),
            ("x", "minute_hand_2", "hour_hand_2"),
            ("x", "hour_hand_3", "minute_hand_3"),
        ]
        for face_index in range(4):
            hour = object_model.get_part(f"hour_hand_{face_index}")
            minute = object_model.get_part(f"minute_hand_{face_index}")
            ctx.expect_origin_distance(
                hour,
                minute,
                axes="xyz",
                max_dist=0.001,
                name=f"face {face_index} hands share center axis",
            )
            axis, positive_name, negative_name = normal_checks[face_index]
            ctx.expect_gap(
                object_model.get_part(positive_name),
                object_model.get_part(negative_name),
                axis=axis,
                positive_elem="hour_blade" if "hour" in positive_name else "minute_blade",
                negative_elem="hour_blade" if "hour" in negative_name else "minute_blade",
                min_gap=0.004,
                name=f"face {face_index} stacked hands are separated",
            )
        minute_0 = object_model.get_part("minute_hand_0")
        minute_joint_0 = object_model.get_articulation("face_0_minute")
        rest_aabb = ctx.part_element_world_aabb(minute_0, elem="minute_blade")
        with ctx.pose({minute_joint_0: math.pi / 2.0}):
            turned_aabb = ctx.part_element_world_aabb(minute_0, elem="minute_blade")
        if rest_aabb is None or turned_aabb is None:
            ctx.fail("minute hand produces measurable rotating blade", "missing minute blade AABB")
        else:
            rest_width = rest_aabb[1][0] - rest_aabb[0][0]
            turned_width = turned_aabb[1][0] - turned_aabb[0][0]
            ctx.check(
                "minute hand visibly rotates in the clock plane",
                turned_width > rest_width + 0.35,
                details=f"rest_width={rest_width:.3f}, turned_width={turned_width:.3f}",
            )

    if resolved.tower_style == "glazed_multiface" and resolved.dial_style != "dual_housing":
        scale = resolved.tower_height / 10.18
        minimum_span = _minimum_clock_room_span(resolved.dial_radius, scale)
        ctx.check(
            "clock room contains the full dial and bezel",
            resolved.head_height >= minimum_span and resolved.head_size >= minimum_span,
            details=(
                f"head_size={resolved.head_size:.3f}, head_height={resolved.head_height:.3f}, "
                f"required_span={minimum_span:.3f}"
            ),
        )

    root_name = roots[0].name if roots else "tower"
    skip_aspect = resolved.dial_style == "dual_housing" or resolved.tower_style in (
        "tiered_stack",
        "belfry_column",
    )
    if not skip_aspect:
        try:
            bbox = ctx.part_world_aabb(object_model.get_part(root_name))
        except Exception:
            bbox = None
        if bbox is not None:
            xs = bbox[1][0] - bbox[0][0]
            ys = bbox[1][1] - bbox[0][1]
            zs = bbox[1][2] - bbox[0][2]
            footprint = max(xs, ys)
            aspect = zs / max(footprint, 1e-6)
            ctx.check(
                "tower_height_to_footprint_ratio", aspect > 1.2, details=f"aspect={aspect:.3f}"
            )

    return ctx.report()


__all__ = [
    "ClockTowerConfig",
    "DialStyle",
    "HandStyle",
    "PaletteTheme",
    "ResolvedClockTowerConfig",
    "TowerStyle",
    "__modular__",
    "build_clock_tower_with_rotating_hour_and_minute_hands",
    "build_seeded_clock_tower_with_rotating_hour_and_minute_hands",
    "config_from_seed",
    "resolve_config",
    "run_clock_tower_with_rotating_hour_and_minute_hands_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
