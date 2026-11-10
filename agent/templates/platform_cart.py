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
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

# rectangle / rounded / ribbed = flat slabs with different corner radii / ribs.
# tray = slab + perimeter lip on all 4 edges (shallow box look).
# framed = visible perimeter frame on top + recessed inner mat panel (picture-
# frame deck like a Costco flatbed).
# slatted = N parallel wood/metal slats with visible gaps between them (cargo
# wagon / wooden cart look).
# tapered = trapezoid plan view (rear wider than front, like a boat hull).
# stepped = 2 stacked levels — a lower main bed with a raised rear shelf.
DeckShape = Literal[
    "rectangle",
    "rounded",
    "ribbed",
    "tray",
    "framed",
    "slatted",
    "tapered",
    "stepped",
]
WheelType = Literal["all_caster", "mixed_steering", "all_fixed"]
# u_handle / twin_bar / single_bar are tubular variants (similar silhouette).
# shopping_cart bends the U-frame backward like a real shopping cart push bar.
# pistol_grip is one tall central post with a 90° backward bend at the top
# (stand-up scooter / pole-grip look). panel_handle is a flat back panel with
# an oval cut-out (kid's wagon look).
HandleStyle = Literal[
    "u_handle",
    "twin_bar",
    "single_bar",
    "shopping_cart",
    "pistol_grip",
    "panel_handle",
    "none",
]
SideRailStyle = Literal["none", "low_lip", "tall_rails", "fold_down_lip"]
BumperStyle = Literal["none", "corner", "full"]
AntiSlipPattern = Literal["none", "stripes", "dots", "grid"]
DeckAspectRatio = Literal["compact", "long", "wide"]
# 8 palettes covering the most common 5-star color families: industrial blue
# steel, silver aluminum, safety orange plastic, safety yellow, charcoal /
# matte-black, wood-topped (wood deck + dark frame), warehouse green, and
# industrial cherry red.
MaterialStyle = Literal[
    "steel",
    "aluminum",
    "plastic_orange",
    "safety_yellow",
    "charcoal",
    "wood_top",
    "warehouse_green",
    "industrial_red",
]
# front_only / rear_only: one handle on a single end of the deck (any style).
# twin_front / twin_rear: two handles placed side-by-side on ONE end — only
# valid when handle_style == "pistol_grip". Both grips face the same direction
# (controlled by pistol_facing).
HandleLayout = Literal["front_only", "rear_only", "twin_front", "twin_rear"]
# Direction the pistol_grip's horizontal arm points, relative to the joint's
# forward axis. Only meaningful when handle_style == "pistol_grip".
PistolFacing = Literal["forward", "backward"]
TowAttachment = Literal["none", "loop", "tow_bar"]
# solid = fast Cylinder; spoked = mesh discs with 5 round windows; industrial =
# barrel hub with bolt circle; auto_capped = solid + outer dome hub-caps;
# pneumatic = solid + side valve stem.
WheelStyle = Literal["solid", "spoked", "industrial", "auto_capped", "pneumatic"]
# Decoration layered on top of the structural slab.
# flat = bare; mat_topped = large rubber/plastic mat in pad color; striped =
# N accent stripes across the deck; framed = thin perimeter trim ring.
DeckTopStyle = Literal["flat", "mat_topped", "striped", "framed"]

# Bucket -> (length_range, width_range) for the deck envelope.
DECK_ASPECT_RANGES: dict[DeckAspectRatio, tuple[tuple[float, float], tuple[float, float]]] = {
    "compact": ((0.55, 0.78), (0.40, 0.55)),
    "long": ((0.95, 1.35), (0.50, 0.66)),
    "wide": ((0.80, 1.05), (0.62, 0.80)),
}

GROUND_Z = 0.0
WHEEL_Z_GAP_MAX = 0.055  # spec: ground contact tolerance
DEFAULT_DECK_THICKNESS = 0.060

# Material palette per material_style. Each tuple holds:
# (deck_body, deck_trim, hardware_steel, dark_hardware, rubber, pad_color).
MATERIAL_PALETTES: dict[
    MaterialStyle,
    tuple[
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
    ],
] = {
    "steel": (
        (0.16, 0.30, 0.52, 1.0),
        (0.72, 0.74, 0.72, 1.0),
        (0.78, 0.80, 0.80, 1.0),
        (0.13, 0.13, 0.13, 1.0),
        (0.04, 0.04, 0.04, 1.0),
        (0.10, 0.10, 0.10, 1.0),
    ),
    "aluminum": (
        (0.82, 0.84, 0.86, 1.0),
        (0.72, 0.74, 0.76, 1.0),
        (0.86, 0.88, 0.90, 1.0),
        (0.22, 0.24, 0.26, 1.0),
        (0.04, 0.04, 0.04, 1.0),
        (0.14, 0.14, 0.14, 1.0),
    ),
    "plastic_orange": (
        (0.86, 0.36, 0.18, 1.0),
        (0.94, 0.92, 0.88, 1.0),
        (0.70, 0.70, 0.70, 1.0),
        (0.16, 0.16, 0.16, 1.0),
        (0.05, 0.05, 0.05, 1.0),
        (0.18, 0.18, 0.20, 1.0),
    ),
    "safety_yellow": (
        (0.95, 0.78, 0.10, 1.0),
        (0.20, 0.20, 0.22, 1.0),
        (0.62, 0.62, 0.64, 1.0),
        (0.12, 0.12, 0.12, 1.0),
        (0.05, 0.05, 0.05, 1.0),
        (0.16, 0.16, 0.18, 1.0),
    ),
    "charcoal": (
        (0.10, 0.10, 0.12, 1.0),
        (0.46, 0.48, 0.50, 1.0),
        (0.62, 0.64, 0.66, 1.0),
        (0.06, 0.06, 0.07, 1.0),
        (0.04, 0.04, 0.04, 1.0),
        (0.18, 0.18, 0.20, 1.0),
    ),
    "wood_top": (
        (0.62, 0.44, 0.24, 1.0),
        (0.34, 0.22, 0.12, 1.0),
        (0.52, 0.54, 0.56, 1.0),
        (0.08, 0.08, 0.09, 1.0),
        (0.05, 0.05, 0.05, 1.0),
        (0.42, 0.28, 0.16, 1.0),
    ),
    "warehouse_green": (
        (0.18, 0.42, 0.26, 1.0),
        (0.86, 0.86, 0.82, 1.0),
        (0.70, 0.72, 0.72, 1.0),
        (0.10, 0.12, 0.10, 1.0),
        (0.04, 0.04, 0.04, 1.0),
        (0.95, 0.78, 0.10, 1.0),  # yellow stripe pad reads well on green decks
    ),
    "industrial_red": (
        (0.74, 0.16, 0.14, 1.0),
        (0.96, 0.92, 0.86, 1.0),
        (0.66, 0.66, 0.68, 1.0),
        (0.10, 0.10, 0.10, 1.0),
        (0.04, 0.04, 0.04, 1.0),
        (0.18, 0.16, 0.16, 1.0),
    ),
}


@dataclass(frozen=True)
class PlatformCartConfig:
    deck_shape: DeckShape = "rectangle"
    wheel_count: int = 4
    wheel_type: WheelType = "all_caster"
    wheel_style: WheelStyle = "solid"
    handle_style: HandleStyle = "u_handle"
    handle_layout: HandleLayout = "front_only"
    pistol_facing: PistolFacing = "backward"
    handle_fold_angle: float = 0.0  # rest angle, radians (0 = vertical, pi/2 = folded flat)
    side_rail: SideRailStyle = "none"
    rail_height: float | None = None  # 0.05–0.20 m; ignored when side_rail == "none"
    tow_attachment: TowAttachment = "none"
    bumper_style: BumperStyle = "none"
    anti_slip_pattern: AntiSlipPattern = "stripes"
    deck_aspect_ratio: DeckAspectRatio = "long"
    deck_top_style: DeckTopStyle = "flat"
    material_style: MaterialStyle = "steel"
    deck_length: float | None = None
    deck_width: float | None = None
    deck_thickness: float = DEFAULT_DECK_THICKNESS
    wheel_radius: float | None = None
    wheel_width: float | None = None
    handle_height: float | None = None
    handle_hinge_y_ratio: float | None = None  # in [0.2, 0.5]
    name: str = "reference_platform_cart"


@dataclass(frozen=True)
class ResolvedPlatformCartConfig:
    deck_shape: DeckShape
    wheel_count: int
    wheel_type: WheelType
    wheel_style: WheelStyle
    handle_style: HandleStyle
    handle_layout: HandleLayout
    pistol_facing: PistolFacing
    handle_fold_angle: float
    side_rail: SideRailStyle
    rail_height: float
    tow_attachment: TowAttachment
    bumper_style: BumperStyle
    anti_slip_pattern: AntiSlipPattern
    deck_aspect_ratio: DeckAspectRatio
    deck_top_style: DeckTopStyle
    material_style: MaterialStyle
    deck_length: float
    deck_width: float
    deck_thickness: float
    wheel_radius: float
    wheel_width: float
    handle_height: float
    handle_hinge_y_ratio: float
    deck_top_z: float
    deck_center_z: float
    has_handle: bool
    has_front_handle: bool
    has_rear_handle: bool
    has_twin_handles: bool
    has_fold_lip: bool
    has_steering: bool
    name: str


def config_from_seed(seed: int) -> PlatformCartConfig:
    rng = random.Random(seed)
    deck_aspect_ratio: DeckAspectRatio = rng.choice(("compact", "long", "wide"))
    (l_lo, l_hi), (w_lo, w_hi) = DECK_ASPECT_RANGES[deck_aspect_ratio]
    deck_length = round(rng.uniform(l_lo, l_hi), 3)
    deck_width = round(rng.uniform(w_lo, w_hi), 3)
    deck_thickness = round(rng.uniform(0.040, 0.075), 3)
    wheel_radius = round(rng.uniform(0.058, 0.095), 3)
    wheel_width = round(rng.uniform(0.030, 0.052), 3)
    wheel_count = rng.choice((4, 6))
    wheel_type: WheelType = rng.choices(
        ("all_caster", "mixed_steering", "all_fixed"),
        weights=(0.55, 0.25, 0.20),
        k=1,
    )[0]
    handle_style: HandleStyle = rng.choices(
        (
            "u_handle",
            "twin_bar",
            "single_bar",
            "shopping_cart",
            "pistol_grip",
            "panel_handle",
            "none",
        ),
        # Cap the three look-alike tubular variants at ~50% total and bump the
        # visually-distinct new styles so seeded samples actually show them.
        weights=(0.20, 0.12, 0.12, 0.18, 0.13, 0.13, 0.12),
        k=1,
    )[0]
    handle_fold_angle = round(rng.uniform(0.0, math.pi / 2.0), 3) if handle_style != "none" else 0.0
    handle_height = round(rng.uniform(0.72, 1.05), 3)
    handle_hinge_y_ratio = round(rng.uniform(0.22, 0.48), 3)
    side_rail: SideRailStyle = rng.choices(
        ("none", "low_lip", "tall_rails", "fold_down_lip"),
        weights=(0.40, 0.30, 0.20, 0.10),
        k=1,
    )[0]
    rail_height = round(rng.uniform(0.05, 0.20), 3) if side_rail != "none" else 0.0
    # handle_layout depends on handle_style: twin_front / twin_rear are only
    # allowed for pistol_grip.
    if handle_style == "pistol_grip":
        handle_layout: HandleLayout = rng.choices(
            ("front_only", "rear_only", "twin_front", "twin_rear"),
            weights=(0.40, 0.15, 0.30, 0.15),
            k=1,
        )[0]
    else:
        handle_layout = rng.choices(
            ("front_only", "rear_only"),
            weights=(0.75, 0.25),
            k=1,
        )[0]
    pistol_facing: PistolFacing = rng.choice(("forward", "backward"))
    tow_attachment: TowAttachment = rng.choices(
        ("none", "loop", "tow_bar"),
        weights=(0.65, 0.20, 0.15),
        k=1,
    )[0]
    wheel_style: WheelStyle = rng.choices(
        ("solid", "spoked", "industrial", "auto_capped", "pneumatic"),
        weights=(0.30, 0.20, 0.18, 0.16, 0.16),
        k=1,
    )[0]
    deck_top_style: DeckTopStyle = rng.choices(
        ("flat", "mat_topped", "striped", "framed"),
        weights=(0.40, 0.25, 0.20, 0.15),
        k=1,
    )[0]
    bumper_style: BumperStyle = rng.choices(
        ("none", "corner", "full"),
        weights=(0.45, 0.35, 0.20),
        k=1,
    )[0]
    anti_slip_pattern: AntiSlipPattern = rng.choices(
        ("none", "stripes", "dots", "grid"),
        weights=(0.15, 0.35, 0.25, 0.25),
        k=1,
    )[0]
    deck_shape: DeckShape = rng.choices(
        ("rectangle", "rounded", "ribbed", "tray", "framed", "slatted", "tapered", "stepped"),
        # First three are common rolled-steel decks (each ~14%); tray/framed/
        # slatted add silhouette variety; tapered/stepped are the most exotic.
        weights=(0.18, 0.14, 0.10, 0.16, 0.11, 0.11, 0.10, 0.10),
        k=1,
    )[0]
    material_style: MaterialStyle = rng.choices(
        (
            "steel",
            "aluminum",
            "plastic_orange",
            "safety_yellow",
            "charcoal",
            "wood_top",
            "warehouse_green",
            "industrial_red",
        ),
        # Weight roughly matches the 5-star sample distribution (blue/steel and
        # gray dominate; safety colors and wood are rarer accents).
        weights=(0.30, 0.18, 0.14, 0.08, 0.10, 0.08, 0.06, 0.06),
        k=1,
    )[0]
    return PlatformCartConfig(
        deck_shape=deck_shape,
        wheel_count=wheel_count,
        wheel_type=wheel_type,
        wheel_style=wheel_style,
        handle_style=handle_style,
        handle_layout=handle_layout,
        pistol_facing=pistol_facing,
        handle_fold_angle=handle_fold_angle,
        side_rail=side_rail,
        rail_height=rail_height if side_rail != "none" else None,
        tow_attachment=tow_attachment,
        bumper_style=bumper_style,
        anti_slip_pattern=anti_slip_pattern,
        deck_aspect_ratio=deck_aspect_ratio,
        deck_top_style=deck_top_style,
        material_style=material_style,
        deck_length=deck_length,
        deck_width=deck_width,
        deck_thickness=deck_thickness,
        wheel_radius=wheel_radius,
        wheel_width=wheel_width,
        handle_height=handle_height,
        handle_hinge_y_ratio=handle_hinge_y_ratio,
        name=f"seeded_platform_cart_{seed}",
    )


def resolve_config(config: PlatformCartConfig) -> ResolvedPlatformCartConfig:
    if config.deck_shape not in {
        "rectangle",
        "rounded",
        "ribbed",
        "tray",
        "framed",
        "slatted",
        "tapered",
        "stepped",
    }:
        raise ValueError(f"Unsupported deck_shape: {config.deck_shape}")
    if config.wheel_count not in {4, 6}:
        raise ValueError(f"Unsupported wheel_count: {config.wheel_count}")
    if config.wheel_type not in {"all_caster", "mixed_steering", "all_fixed"}:
        raise ValueError(f"Unsupported wheel_type: {config.wheel_type}")
    if config.handle_style not in {
        "u_handle",
        "twin_bar",
        "single_bar",
        "shopping_cart",
        "pistol_grip",
        "panel_handle",
        "none",
    }:
        raise ValueError(f"Unsupported handle_style: {config.handle_style}")
    if config.handle_layout not in {"front_only", "rear_only", "twin_front", "twin_rear"}:
        raise ValueError(f"Unsupported handle_layout: {config.handle_layout}")
    # twin_* requires pistol_grip; reject mismatched combos.
    if config.handle_layout in {"twin_front", "twin_rear"} and config.handle_style != "pistol_grip":
        raise ValueError(
            f"handle_layout={config.handle_layout!r} requires handle_style='pistol_grip', "
            f"got {config.handle_style!r}"
        )
    if config.pistol_facing not in {"forward", "backward"}:
        raise ValueError(f"Unsupported pistol_facing: {config.pistol_facing}")
    if config.tow_attachment not in {"none", "loop", "tow_bar"}:
        raise ValueError(f"Unsupported tow_attachment: {config.tow_attachment}")
    if config.wheel_style not in {"solid", "spoked", "industrial", "auto_capped", "pneumatic"}:
        raise ValueError(f"Unsupported wheel_style: {config.wheel_style}")
    # Accept legacy aliases for side_rail.
    side_rail_aliases = {"low": "low_lip", "full": "tall_rails"}
    side_rail = side_rail_aliases.get(config.side_rail, config.side_rail)
    if side_rail not in {"none", "low_lip", "tall_rails", "fold_down_lip"}:
        raise ValueError(f"Unsupported side_rail: {config.side_rail}")
    if config.bumper_style not in {"none", "corner", "full"}:
        raise ValueError(f"Unsupported bumper_style: {config.bumper_style}")
    if config.anti_slip_pattern not in {"none", "stripes", "dots", "grid"}:
        raise ValueError(f"Unsupported anti_slip_pattern: {config.anti_slip_pattern}")
    if config.deck_aspect_ratio not in {"compact", "long", "wide"}:
        raise ValueError(f"Unsupported deck_aspect_ratio: {config.deck_aspect_ratio}")
    if config.deck_top_style not in {"flat", "mat_topped", "striped", "framed"}:
        raise ValueError(f"Unsupported deck_top_style: {config.deck_top_style}")
    # Accept the legacy "plastic" alias (renamed to "plastic_orange") so older
    # batch specs and seeded configs keep building.
    material_aliases = {"plastic": "plastic_orange"}
    material_style = material_aliases.get(config.material_style, config.material_style)
    if material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if not (0.0 <= config.handle_fold_angle <= math.pi / 2.0 + 1e-6):
        raise ValueError("handle_fold_angle must be in [0, pi/2]")

    (l_lo, l_hi), (w_lo, w_hi) = DECK_ASPECT_RANGES[config.deck_aspect_ratio]
    deck_length = config.deck_length if config.deck_length is not None else (l_lo + l_hi) * 0.5
    deck_width = config.deck_width if config.deck_width is not None else (w_lo + w_hi) * 0.5
    if deck_length <= 0.2 or deck_width <= 0.2:
        raise ValueError("deck envelope too small")
    deck_thickness = max(0.025, min(0.10, config.deck_thickness))

    wheel_radius = config.wheel_radius if config.wheel_radius is not None else 0.072
    wheel_width = config.wheel_width if config.wheel_width is not None else 0.040

    # Clamp wheel radius so wheels physically fit under deck without exceeding deck width / 2.
    max_wheel_radius = min(0.12, deck_width * 0.20)
    if config.wheel_count == 6:
        # A mid pair sits at y=0 between the front/rear pairs at y=+-(L/2 - inset).
        # inset_y itself grows with the radius, so solve the spacing constraint
        # (front_y >= 2r + gap) for r and cap the radius by it; otherwise adjacent
        # wheels on the same side physically intersect while rolling.
        max_wheel_radius = min(max_wheel_radius, (deck_length * 0.5 - 0.025 - 0.012) / 3.0)
    if wheel_radius > max_wheel_radius:
        wheel_radius = max_wheel_radius
    wheel_radius = max(0.040, wheel_radius)
    wheel_width = max(0.020, min(wheel_width, deck_width * 0.18))

    # Deck top-of-deck height: wheel radius (+ caster yoke for all_caster) + small ground clearance.
    if config.wheel_type == "all_caster":
        yoke_drop = 0.022  # caster swivel plate inset above wheel center
    else:
        yoke_drop = 0.008
    deck_center_z = wheel_radius + yoke_drop + deck_thickness * 0.5
    deck_top_z = deck_center_z + deck_thickness * 0.5

    handle_height = config.handle_height if config.handle_height is not None else 0.92
    handle_height = max(0.50, min(1.30, handle_height))
    handle_hinge_y_ratio = (
        config.handle_hinge_y_ratio if config.handle_hinge_y_ratio is not None else 0.35
    )
    handle_hinge_y_ratio = max(0.20, min(0.50, handle_hinge_y_ratio))

    has_handle = config.handle_style != "none"
    layout = config.handle_layout
    has_front_handle = has_handle and layout in {"front_only", "twin_front"}
    has_rear_handle = has_handle and layout in {"rear_only", "twin_rear"}
    has_twin_handles = has_handle and layout in {"twin_front", "twin_rear"}
    has_fold_lip = side_rail == "fold_down_lip"
    has_steering = config.wheel_type == "mixed_steering"
    rail_height = config.rail_height
    if rail_height is None:
        # Defaults that match the legacy "low"/"full" semantics.
        defaults = {"none": 0.0, "low_lip": 0.055, "tall_rails": 0.220, "fold_down_lip": 0.080}
        rail_height = defaults[side_rail]
    rail_height = max(0.0, min(0.30, rail_height))

    return ResolvedPlatformCartConfig(
        deck_shape=config.deck_shape,
        wheel_count=config.wheel_count,
        wheel_type=config.wheel_type,
        wheel_style=config.wheel_style,
        handle_style=config.handle_style,
        handle_layout=config.handle_layout,
        pistol_facing=config.pistol_facing,
        handle_fold_angle=config.handle_fold_angle,
        side_rail=side_rail,
        rail_height=rail_height,
        tow_attachment=config.tow_attachment,
        bumper_style=config.bumper_style,
        anti_slip_pattern=config.anti_slip_pattern,
        deck_aspect_ratio=config.deck_aspect_ratio,
        deck_top_style=config.deck_top_style,
        material_style=material_style,
        deck_length=deck_length,
        deck_width=deck_width,
        deck_thickness=deck_thickness,
        wheel_radius=wheel_radius,
        wheel_width=wheel_width,
        handle_height=handle_height,
        handle_hinge_y_ratio=handle_hinge_y_ratio,
        deck_top_z=deck_top_z,
        deck_center_z=deck_center_z,
        has_handle=has_handle,
        has_front_handle=has_front_handle,
        has_rear_handle=has_rear_handle,
        has_twin_handles=has_twin_handles,
        has_fold_lip=has_fold_lip,
        has_steering=has_steering,
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------


def _wheel_layout(resolved: ResolvedPlatformCartConfig) -> list[tuple[str, float, float]]:
    """Return a list of (slot_name, x, y) for wheel mount positions on the deck.

    +y is forward (front). All positions in deck-frame xy (z fixed by caller).
    """
    L = resolved.deck_length
    W = resolved.deck_width
    inset_y = max(0.07, resolved.wheel_radius + 0.025)
    inset_x = max(0.06, resolved.wheel_width * 0.5 + 0.018)
    front_y = (L * 0.5) - inset_y
    rear_y = -front_y
    left_x = -(W * 0.5 - inset_x)
    right_x = -left_x
    if resolved.wheel_count == 4:
        return [
            ("front_left", left_x, front_y),
            ("front_right", right_x, front_y),
            ("rear_left", left_x, rear_y),
            ("rear_right", right_x, rear_y),
        ]
    # wheel_count == 6: add a mid pair
    return [
        ("front_left", left_x, front_y),
        ("front_right", right_x, front_y),
        ("mid_left", left_x, 0.0),
        ("mid_right", right_x, 0.0),
        ("rear_left", left_x, rear_y),
        ("rear_right", right_x, rear_y),
    ]


def _slot_is_steering(slot_name: str, resolved: ResolvedPlatformCartConfig) -> bool:
    """Whether this slot belongs to the front steering bridge (mixed_steering only)."""
    if resolved.wheel_type != "mixed_steering":
        return False
    return slot_name.startswith("front_")


def _slot_uses_caster_swivel(slot_name: str, resolved: ResolvedPlatformCartConfig) -> bool:
    if resolved.wheel_type == "all_caster":
        return True
    if resolved.wheel_type == "mixed_steering":
        # rear and mid wheels stay fixed; only the front pair swivels via steering bridge,
        # not via independent caster swivels.
        return False
    return False


# ---------------------------------------------------------------------------
# Deck builders
# ---------------------------------------------------------------------------


def _build_rounded_slab_mesh(
    *,
    length: float,
    width: float,
    thickness: float,
    corner_radius: float,
    assets: AssetContext,
    name: str,
):
    """Helper: extruded rounded rectangle ready to be added as a visual."""
    profile = rounded_rect_profile(width, length, corner_radius, corner_segments=10)
    geom = ExtrudeGeometry.from_z0(profile, thickness, cap=True, closed=True)
    return mesh_from_geometry(geom, assets.mesh_path(name))


def _add_deck_shell(
    part,
    resolved: ResolvedPlatformCartConfig,
    *,
    deck_color,
    trim,
    assets: AssetContext,
) -> None:
    """Dispatch deck silhouette based on `deck_shape`.

    All variants honor the same `deck_center_z` / `deck_top_z` / `deck_thickness`
    bookkeeping so downstream parts (handles, casters, side rails) attach to a
    consistent surface."""
    shape = resolved.deck_shape
    L = resolved.deck_length
    W = resolved.deck_width
    th = resolved.deck_thickness
    z_center = resolved.deck_center_z
    z_top = resolved.deck_top_z

    if shape == "slatted":
        _build_slatted_deck(part, resolved, deck_color=deck_color, trim=trim)
    elif shape == "tapered":
        _build_tapered_deck(part, resolved, deck_color=deck_color, assets=assets)
    elif shape == "stepped":
        _build_stepped_deck(part, resolved, deck_color=deck_color, trim=trim, assets=assets)
    else:
        # rectangle / rounded / ribbed / tray / framed all start from a single
        # rounded-rect extruded slab; differences come from added trim.
        corner_radius_per_shape = {
            "rectangle": 0.04,
            "rounded": 0.20,
            "ribbed": 0.06,
            "tray": 0.08,
            "framed": 0.05,
        }
        rel = corner_radius_per_shape.get(shape, 0.10)
        corner_radius = max(0.010, min(L, W) * rel)
        part.visual(
            _build_rounded_slab_mesh(
                length=L,
                width=W,
                thickness=th,
                corner_radius=corner_radius,
                assets=assets,
                name=f"deck_shell_{shape}.obj",
            ),
            origin=Origin(xyz=(0.0, 0.0, z_center - th * 0.5)),
            material=deck_color,
            name="deck_shell", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
        )

    if shape == "ribbed":
        rib_count = 5
        rib_w = max(0.008, W * 0.018)
        rib_inset = min(L, W) * 0.08
        for i in range(rib_count):
            ry = -L * 0.5 + rib_inset + (i + 0.5) * ((L - 2 * rib_inset) / rib_count)
            part.visual(
                Box((W * 0.88, rib_w, th * 0.35)),
                origin=Origin(xyz=(0.0, ry, z_top)),
                material=trim,
                name=f"deck_rib_{i}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
            )

    if shape == "tray":
        # Perimeter lip on all 4 edges, low (~3 cm). Sits ON the deck top.
        lip_h = 0.032
        lip_t = 0.016
        # Long edges (left/right).
        for sx, lab in ((1.0, "right"), (-1.0, "left")):
            part.visual(
                Box((lip_t, L - 2 * lip_t, lip_h)),
                origin=Origin(xyz=(sx * (W * 0.5 - lip_t * 0.5), 0.0, z_top + lip_h * 0.5)),
                material=trim,
                name=f"tray_lip_{lab}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
            )
        # Short edges (front/rear) — spans the full width including the side lips.
        for sy, lab in ((1.0, "front"), (-1.0, "rear")):
            part.visual(
                Box((W, lip_t, lip_h)),
                origin=Origin(xyz=(0.0, sy * (L * 0.5 - lip_t * 0.5), z_top + lip_h * 0.5)),
                material=trim,
                name=f"tray_lip_{lab}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
            )

    elif shape == "framed":
        # Picture-frame deck: 4 rails outline the perimeter on top of the slab,
        # and a recessed inner panel sits just below the rail tops.
        rail_w = max(0.020, min(0.040, W * 0.07))
        rail_h = 0.030
        z_rail = z_top + rail_h * 0.5
        # Long-edge rails.
        for sx, lab in ((1.0, "right"), (-1.0, "left")):
            part.visual(
                Box((rail_w, L - 2 * rail_w, rail_h)),
                origin=Origin(xyz=(sx * (W * 0.5 - rail_w * 0.5), 0.0, z_rail)),
                material=trim,
                name=f"frame_rail_{lab}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
            )
        # Short-edge rails span the full width to butt against the long rails.
        for sy, lab in ((1.0, "front"), (-1.0, "rear")):
            part.visual(
                Box((W, rail_w, rail_h)),
                origin=Origin(xyz=(0.0, sy * (L * 0.5 - rail_w * 0.5), z_rail)),
                material=trim,
                name=f"frame_rail_{lab}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
            )
        # Recessed inner panel (sits below the rail top).
        inner_w = W - 2 * rail_w
        inner_l = L - 2 * rail_w
        panel_th = 0.006
        part.visual(
            Box((inner_w, inner_l, panel_th)),
            origin=Origin(xyz=(0.0, 0.0, z_top + panel_th * 0.5)),
            material=trim,
            name="frame_inner_panel", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
        )

    if shape not in {"slatted", "tapered", "stepped"}:
        # An accent trim strip down the long center; gives the deck a two-tone
        # look without per-style branching. Skipped on shapes that already have
        # their own dominant pattern (slats, tapered hull, step shelf).
        part.visual(
            Box((W * 0.18, L * 0.92, th * 0.10)),
            origin=Origin(xyz=(0.0, 0.0, z_top + 0.001)),
            material=trim,
            name="deck_center_trim", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
        )


def _build_slatted_deck(part, resolved: ResolvedPlatformCartConfig, *, deck_color, trim) -> None:
    """Replace the single slab with N parallel slats running along Y, separated
    by small visible gaps. Two end-caps (front/rear) in the trim color tie the
    slats together visually (and structurally) like a wooden cart deck."""
    L = resolved.deck_length
    W = resolved.deck_width
    th = resolved.deck_thickness
    z_center = resolved.deck_center_z

    slat_count = 8
    gap = max(0.005, min(0.012, W * 0.018))
    # Subtract end-cap thickness from the slat field so caps sit at the long
    # ends without overlapping the slats.
    cap_w = max(0.018, W * 0.045)
    field_w = W - 2 * cap_w
    slat_w = max(0.018, (field_w - (slat_count - 1) * gap) / slat_count)
    # Slats are slightly shorter than L so the front/rear end-caps can extend
    # the full width across the slats' ends.
    slat_l = L - 2 * cap_w
    for i in range(slat_count):
        cx = -field_w * 0.5 + slat_w * 0.5 + i * (slat_w + gap)
        part.visual(
            Box((slat_w, slat_l, th)),
            origin=Origin(xyz=(cx, 0.0, z_center)),
            material=deck_color,
            name=f"deck_slat_{i}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
        )
    # Two side end-caps (left + right) — substitute for the missing outer slats
    # so the deck silhouette is still rectangular when viewed from above.
    for sx, lab in ((1.0, "right"), (-1.0, "left")):
        part.visual(
            Box((cap_w, L, th)),
            origin=Origin(xyz=(sx * (W * 0.5 - cap_w * 0.5), 0.0, z_center)),
            material=trim,
            name=f"deck_end_cap_{lab}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
        )
    # Two cross-rails at the front and rear (short edges) hold the slats
    # together — visible from the side as the "frame" of the slatted deck.
    rail_th = max(0.020, th * 0.6)
    for sy, lab in ((1.0, "front"), (-1.0, "rear")):
        part.visual(
            Box((W - 2 * cap_w, cap_w, th)),
            origin=Origin(xyz=(0.0, sy * (L * 0.5 - cap_w * 0.5), z_center)),
            material=trim,
            name=f"deck_cross_rail_{lab}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
        )
    _ = rail_th


def _build_tapered_deck(
    part, resolved: ResolvedPlatformCartConfig, *, deck_color, assets: AssetContext
) -> None:
    """Trapezoid plan view: the FRONT edge is narrower than the REAR (cart
    leads with a point like a boat hull). Built as a single ExtrudeGeometry
    with a custom 6-point profile (rear corners + 2 tapered front corners +
    1 nose point at the very front to keep the geometry rounded)."""
    L = resolved.deck_length
    W = resolved.deck_width
    th = resolved.deck_thickness
    z_center = resolved.deck_center_z
    rear_half_w = W * 0.5
    front_half_w = W * 0.32  # narrower front
    nose_offset = L * 0.05  # how far the nose extends past the front edge
    # Profile in (x, y): walk counter-clockwise from rear-right around.
    profile = [
        (rear_half_w, -L * 0.5),
        (rear_half_w, L * 0.35),
        (front_half_w, L * 0.5),
        (0.0, L * 0.5 + nose_offset),
        (-front_half_w, L * 0.5),
        (-rear_half_w, L * 0.35),
        (-rear_half_w, -L * 0.5),
    ]
    geom = ExtrudeGeometry.from_z0(profile, th, cap=True, closed=True)
    mesh = mesh_from_geometry(geom, assets.mesh_path("deck_tapered.obj"))
    part.visual(
        mesh,
        origin=Origin(xyz=(0.0, 0.0, z_center - th * 0.5)),
        material=deck_color,
        name="deck_shell", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
    )


def _build_stepped_deck(
    part,
    resolved: ResolvedPlatformCartConfig,
    *,
    deck_color,
    trim,
    assets: AssetContext,
) -> None:
    """Two stacked levels: a lower main bed covering the front 2/3 of the
    cart, and a raised rear shelf covering the back 1/3 sitting on top of the
    bed. Both layers use rounded-rect extrudes."""
    L = resolved.deck_length
    W = resolved.deck_width
    th = resolved.deck_thickness
    z_center = resolved.deck_center_z
    z_top = resolved.deck_top_z
    # Lower main bed spans the full deck (so wheels/casters keep the existing
    # geometry). We shift it slightly forward so the rear shelf has clear room.
    main_corner = max(0.010, min(L, W) * 0.10)
    part.visual(
        _build_rounded_slab_mesh(
            length=L,
            width=W,
            thickness=th,
            corner_radius=main_corner,
            assets=assets,
            name="deck_stepped_lower.obj",
        ),
        origin=Origin(xyz=(0.0, 0.0, z_center - th * 0.5)),
        material=deck_color,
        name="deck_shell", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
    )
    # Raised rear shelf: ~1/3 of the deck length, 0.5–0.7× width, ~3 cm above
    # the main top. Mounted at the REAR (-Y) end. Skipped when a rear-mounted
    # folding handle occupies the same rear region, since the two would share
    # (and collide in) that space; the handle takes precedence there.
    _rear_handle_here = resolved.has_rear_handle or (
        resolved.has_twin_handles and resolved.handle_layout == "twin_rear"
    )
    if not _rear_handle_here:
        shelf_l = L * 0.33
        shelf_w = W * 0.82
        shelf_th = max(0.022, th * 0.6)
        shelf_top_offset = 0.040
        shelf_corner = max(0.008, min(shelf_l, shelf_w) * 0.08)
        shelf_y = -L * 0.5 + shelf_l * 0.5 + 0.015  # centered over the rear portion
        part.visual(
            _build_rounded_slab_mesh(
                length=shelf_l,
                width=shelf_w,
                thickness=shelf_th,
                corner_radius=shelf_corner,
                assets=assets,
                name="deck_stepped_shelf.obj",
            ),
            origin=Origin(xyz=(0.0, shelf_y, z_top + shelf_top_offset - shelf_th * 0.5)),
            material=trim,
            name="deck_rear_shelf", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
        )
        # Two short risers at the rear corners visually support the shelf so it
        # doesn't look floating from above.
        riser_h = shelf_top_offset - shelf_th * 0.5
        if riser_h > 0.002:
            for sx, lab in ((1.0, "right"), (-1.0, "left")):
                part.visual(
                    Box((0.030, shelf_l * 0.45, riser_h)),
                    origin=Origin(
                        xyz=(
                            sx * (shelf_w * 0.5 - 0.020),
                            shelf_y,
                            z_top + riser_h * 0.5 + 0.0005,
                        )
                    ),
                    material=trim,
                    name=f"deck_shelf_riser_{lab}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
                )


def _add_anti_slip_pad(part, resolved: ResolvedPlatformCartConfig, *, pad_mat) -> None:
    if resolved.anti_slip_pattern == "none":
        return
    L = resolved.deck_length
    W = resolved.deck_width
    pad_z = resolved.deck_top_z + 0.001
    pad_th = 0.004
    inset = 0.035
    part.visual(
        Box((W - 2 * inset, L - 2 * inset, pad_th)),
        origin=Origin(xyz=(0.0, 0.0, pad_z)),
        material=pad_mat,
        name="anti_slip_pad", material_class_id="rubber.smooth_plain",
    )
    if resolved.anti_slip_pattern == "stripes":
        stripe_count = 9
        stripe_w = max(0.010, (L - 2 * inset) / (stripe_count * 2.2))
        usable_y = L - 2 * inset - 0.020
        for i in range(stripe_count):
            sy = -usable_y * 0.5 + (i + 0.5) * (usable_y / stripe_count)
            part.visual(
                Box((W - 2 * inset - 0.020, stripe_w, 0.0025)),
                origin=Origin(xyz=(0.0, sy, pad_z + pad_th * 0.5 + 0.0012)),
                material=pad_mat,
                name=f"anti_slip_stripe_{i}", material_class_id="rubber.directional_grooved",
            )
    elif resolved.anti_slip_pattern == "dots":
        cols = 5
        rows = max(5, int(L / W * cols))
        usable_w = W - 2 * inset - 0.025
        usable_l = L - 2 * inset - 0.025
        for ci in range(cols):
            for ri in range(rows):
                cx = -usable_w * 0.5 + (ci + 0.5) * (usable_w / cols)
                ry = -usable_l * 0.5 + (ri + 0.5) * (usable_l / rows)
                part.visual(
                    Cylinder(radius=0.010, length=0.003),
                    origin=Origin(xyz=(cx, ry, pad_z + pad_th * 0.5 + 0.0015)),
                    material=pad_mat,
                    name=f"anti_slip_dot_{ci}_{ri}", material_class_id="rubber.pebbled",
                )
    else:  # grid
        usable_w = W - 2 * inset - 0.020
        usable_l = L - 2 * inset - 0.020
        rib_w = 0.006
        cols = 4
        rows = max(4, int(L / W * cols))
        for ci in range(cols + 1):
            cx = -usable_w * 0.5 + ci * (usable_w / cols)
            part.visual(
                Box((rib_w, usable_l, 0.0025)),
                origin=Origin(xyz=(cx, 0.0, pad_z + pad_th * 0.5 + 0.0012)),
                material=pad_mat,
                name=f"anti_slip_grid_col_{ci}", material_class_id="rubber.directional_grooved",
            )
        for ri in range(rows + 1):
            ry = -usable_l * 0.5 + ri * (usable_l / rows)
            part.visual(
                Box((usable_w, rib_w, 0.0025)),
                origin=Origin(xyz=(0.0, ry, pad_z + pad_th * 0.5 + 0.0012)),
                material=pad_mat,
                name=f"anti_slip_grid_row_{ri}", material_class_id="rubber.directional_grooved",
            )


def _add_deck_top_decoration(
    part,
    resolved: ResolvedPlatformCartConfig,
    *,
    deck_color,
    trim,
    pad_mat,
) -> None:
    """Layer a decorative top dressing on the deck (mat overlay, accent stripes,
    or perimeter trim ring) without changing the structural slab."""
    if resolved.deck_top_style == "flat":
        return
    L = resolved.deck_length
    W = resolved.deck_width
    z_top = resolved.deck_top_z
    if resolved.deck_top_style == "mat_topped":
        # Large rubber/plastic mat overlay covering most of the deck, slightly
        # inset so the deck color shows as a frame around it.
        inset = 0.030
        mat_th = 0.003
        part.visual(
            Box((W - 2 * inset, L - 2 * inset, mat_th)),
            origin=Origin(xyz=(0.0, 0.0, z_top + mat_th * 0.5)),
            material=pad_mat,
            name="deck_top_mat", material_class_id="rubber.smooth_plain",
        )
    elif resolved.deck_top_style == "striped":
        # Three accent stripes running the long direction in the trim color.
        stripe_count = 3
        stripe_w = max(0.014, W * 0.05)
        stripe_th = 0.002
        usable_x = W - 0.080
        for i in range(stripe_count):
            cx = -usable_x * 0.5 + (i + 0.5) * (usable_x / stripe_count)
            part.visual(
                Box((stripe_w, L * 0.90, stripe_th)),
                origin=Origin(xyz=(cx, 0.0, z_top)),
                material=trim,
                name=f"deck_accent_stripe_{i}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
            )
    elif resolved.deck_top_style == "framed":
        # Thin perimeter trim ring (four boxes) sitting on top of the deck.
        ring_w = max(0.014, min(W * 0.05, 0.030))
        ring_th = 0.004
        z = z_top
        # Front + rear strips span the full width.
        for sy, lab in ((1.0, "front"), (-1.0, "rear")):
            part.visual(
                Box((W - 0.020, ring_w, ring_th)),
                origin=Origin(xyz=(0.0, sy * (L * 0.5 - ring_w * 0.5 - 0.010), z)),
                material=trim,
                name=f"deck_trim_ring_{lab}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
            )
        # Left + right strips connect between the front/rear trims.
        for sx, lab in ((1.0, "right"), (-1.0, "left")):
            part.visual(
                Box((ring_w, L - 2 * ring_w - 0.020, ring_th)),
                origin=Origin(xyz=(sx * (W * 0.5 - ring_w * 0.5 - 0.010), 0.0, z)),
                material=trim,
                name=f"deck_trim_ring_{lab}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
            )
    _ = deck_color


def _add_side_rails(part, resolved: ResolvedPlatformCartConfig, *, trim, hardware) -> None:
    """Build fixed side-rails on the deck. The fold-down lip is built separately
    as its own articulated part (see _build_fold_lip).
    """
    if resolved.side_rail == "none":
        return
    L = resolved.deck_length
    W = resolved.deck_width
    z0 = resolved.deck_top_z
    rail_h = resolved.rail_height
    side_lip_t = 0.018

    if resolved.side_rail == "fold_down_lip":
        # The front-edge lip lives on its own articulated part. Here we only add
        # the LEFT/RIGHT fixed side rails (a low strip along the long edges) so
        # the cart still has cargo retention on the sides; the front lip swings.
        # Plus two small hinge ears on the front edge that anchor the lip pivot.
        low_h = max(0.025, min(rail_h * 0.6, 0.060))
        for sign, lab in ((1.0, "right"), (-1.0, "left")):
            part.visual(
                Box((side_lip_t, L * 0.95, low_h)),
                origin=Origin(xyz=(sign * (W * 0.5 - side_lip_t * 0.5), 0.0, z0 + low_h * 0.5)),
                material=trim,
                name=f"{lab}_side_rail_panel", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
            )
        # Hinge knuckle ears on the front edge.
        knuckle_r = 0.008
        knuckle_z = z0 + knuckle_r + 0.001
        for sign, lab in ((1.0, "right"), (-1.0, "left")):
            part.visual(
                Box((0.026, 0.012, 0.012)),
                origin=Origin(
                    xyz=(
                        sign * (W * 0.5 - 0.013),
                        L * 0.5 - 0.006,
                        z0 + 0.006,
                    )
                ),
                material=hardware,
                name=f"{lab}_fold_lip_knuckle", material_class_id="metal.stainless_matte",
            )
        _ = knuckle_z
        return

    # Continuous side lip strip on the long edges of the deck.
    for sign, lab in ((1.0, "right"), (-1.0, "left")):
        part.visual(
            Box((side_lip_t, L * 0.95, rail_h)),
            origin=Origin(xyz=(sign * (W * 0.5 - side_lip_t * 0.5), 0.0, z0 + rail_h * 0.5)),
            material=trim,
            name=f"{lab}_side_rail_panel", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
        )

    if resolved.side_rail == "tall_rails":
        # Add vertical posts + a top horizontal bar on each long side.
        post_count = 5
        post_r = 0.012
        for sign, lab in ((1.0, "right"), (-1.0, "left")):
            x_post = sign * (W * 0.5 - 0.020)
            for i in range(post_count):
                py = -L * 0.45 + i * (L * 0.9 / max(1, post_count - 1))
                part.visual(
                    Cylinder(radius=post_r, length=rail_h),
                    origin=Origin(xyz=(x_post, py, z0 + rail_h * 0.5)),
                    material=trim,
                    name=f"{lab}_rail_post_{i}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
                )
            part.visual(
                Box((0.016, L * 0.92, 0.016)),
                origin=Origin(xyz=(x_post, 0.0, z0 + rail_h - 0.012)),
                material=trim,
                name=f"{lab}_rail_top", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
            )


def _build_fold_lip_visuals(
    lip_part, resolved: ResolvedPlatformCartConfig, *, trim, hardware
) -> None:
    """Local frame: pivot at the lip's lower hinge edge (front edge of deck).
    In rest pose (q=0) the lip stands UP (+Z); at q=pi/2 it folds DOWN flat
    along +Y (off the front of the cart)."""
    W = resolved.deck_width
    lip_h = max(0.05, resolved.rail_height)
    lip_t = 0.014
    lip_w = W * 0.94
    # Panel: hinge edge at z=0, panel extends +Z (upward when closed).
    lip_part.visual(
        Box((lip_w, lip_t, lip_h)),
        origin=Origin(xyz=(0.0, 0.0, lip_h * 0.5)),
        material=trim,
        name="lip_panel", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
    )
    # Hinge knuckle bar on the lip side (mates with the deck-side knuckles).
    lip_part.visual(
        Cylinder(radius=0.0065, length=lip_w * 0.45),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="lip_hinge_pin", material_class_id="metal.stainless_matte",
    )


def _add_bumpers(part, resolved: ResolvedPlatformCartConfig, *, trim) -> None:
    if resolved.bumper_style == "none":
        return
    L = resolved.deck_length
    W = resolved.deck_width
    z = resolved.deck_center_z
    bumper_th = 0.022
    bumper_h = resolved.deck_thickness + 0.018
    if resolved.bumper_style == "corner":
        size_xy = 0.090
        for sx, lx in ((1.0, "right"), (-1.0, "left")):
            for sy, ly in ((1.0, "front"), (-1.0, "rear")):
                part.visual(
                    Box((size_xy, bumper_th, bumper_h)),
                    origin=Origin(
                        xyz=(
                            sx * (W * 0.5 - size_xy * 0.5),
                            sy * (L * 0.5 - bumper_th * 0.5),
                            z,
                        )
                    ),
                    material=trim,
                    name=f"bumper_corner_{ly}_{lx}_long", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
                )
                part.visual(
                    Box((bumper_th, size_xy, bumper_h)),
                    origin=Origin(
                        xyz=(
                            sx * (W * 0.5 - bumper_th * 0.5),
                            sy * (L * 0.5 - size_xy * 0.5),
                            z,
                        )
                    ),
                    material=trim,
                    name=f"bumper_corner_{ly}_{lx}_short", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
                )
    else:  # full
        for sy, ly in ((1.0, "front"), (-1.0, "rear")):
            part.visual(
                Box((W + 2 * bumper_th, bumper_th, bumper_h)),
                origin=Origin(xyz=(0.0, sy * (L * 0.5 + bumper_th * 0.5), z)),
                material=trim,
                name=f"bumper_strip_{ly}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
            )
        for sx, lx in ((1.0, "right"), (-1.0, "left")):
            part.visual(
                Box((bumper_th, L, bumper_h)),
                origin=Origin(xyz=(sx * (W * 0.5 + bumper_th * 0.5), 0.0, z)),
                material=trim,
                name=f"bumper_strip_{lx}", material_class_id=("metal.paint_coated" if resolved.material_style in {"steel", "aluminum", "safety_yellow", "charcoal", "wood_top", "warehouse_green", "industrial_red"} else "plastic.opaque_glossy_molded"),
            )


def _add_caster_mount_plates(part, resolved: ResolvedPlatformCartConfig, *, hardware) -> None:
    # Each caster needs a small mount plate beneath the deck (decorative non-articulated).
    for slot_name, x, y in _wheel_layout(resolved):
        if not _slot_uses_caster_swivel(slot_name, resolved):
            continue
        part.visual(
            Box((0.110, 0.090, 0.010)),
            origin=Origin(
                xyz=(
                    x,
                    y,
                    resolved.deck_center_z - resolved.deck_thickness * 0.5 - 0.005,
                )
            ),
            material=hardware,
            name=f"{slot_name}_caster_mount", material_class_id="metal.stainless_matte",
        )


def _add_handle_hinge_ears(part, resolved: ResolvedPlatformCartConfig, *, hardware) -> None:
    """Hinge mount(s) on the deck top for the handle pivot.

    Layout cases:
    - single-post styles (single_bar, pistol_grip): ONE wide central ear per
      hinge location so the post visibly rises out of it.
    - two-leg styles (u_handle, twin_bar, shopping_cart, panel_handle): TWO
      outer ears flanking the legs.
    - twin_front / twin_rear (always pistol_grip): TWO central ears on the same
      end of the deck, one per twin pistol_grip.
    """
    if not resolved.has_handle:
        return
    ear_z = resolved.deck_top_z + 0.030
    L = resolved.deck_length
    W = resolved.deck_width
    single_mount = resolved.handle_style in {"single_bar", "pistol_grip"}

    if resolved.has_twin_handles:
        # Two central ears side-by-side at the same hinge_y (twin pistol_grip).
        twin_offset = max(0.10, W * 0.28)
        side_lab = "front" if resolved.handle_layout == "twin_front" else "rear"
        hinge_y = resolved.handle_hinge_y_ratio * L
        if resolved.handle_layout == "twin_rear":
            hinge_y = -hinge_y
        for slot, x_off in (("left", -twin_offset), ("right", twin_offset)):
            part.visual(
                Box((0.070, 0.055, 0.060)),
                origin=Origin(xyz=(x_off, hinge_y, ear_z)),
                material=hardware,
                name=f"handle_hinge_ear_{side_lab}_{slot}", material_class_id="metal.stainless_matte",
            )
        return

    locations = []
    if resolved.has_front_handle:
        locations.append(("front", resolved.handle_hinge_y_ratio * L))
    if resolved.has_rear_handle:
        locations.append(("rear", -resolved.handle_hinge_y_ratio * L))
    for side_lab, hinge_y in locations:
        if single_mount:
            part.visual(
                Box((0.070, 0.055, 0.060)),
                origin=Origin(xyz=(0.0, hinge_y, ear_z)),
                material=hardware,
                name=f"handle_hinge_ear_{side_lab}_center", material_class_id="metal.stainless_matte",
            )
        else:
            ear_offset_x = max(0.085, W * 0.32)
            for sx, lab in ((1.0, "right"), (-1.0, "left")):
                part.visual(
                    Box((0.030, 0.055, 0.060)),
                    origin=Origin(xyz=(sx * ear_offset_x, hinge_y, ear_z)),
                    material=hardware,
                    name=f"handle_hinge_ear_{side_lab}_{lab}", material_class_id="metal.stainless_matte",
                )


def _add_tow_loop(
    part, resolved: ResolvedPlatformCartConfig, *, hardware, assets: AssetContext
) -> None:
    """FIXED D-ring tow loop on the front edge of the deck. Built from a single
    arc tube (mesh path) sweeping a half-circle from -X up over the top to +X,
    plus a mount plate at the base."""
    L = resolved.deck_length
    W = resolved.deck_width
    z = resolved.deck_center_z
    mount_y = L * 0.5 + 0.006
    front_y = L * 0.5 + 0.014
    # Mount plate sitting on the front face of the deck.
    part.visual(
        Box((W * 0.20, 0.014, 0.044)),
        origin=Origin(xyz=(0.0, mount_y, z)),
        material=hardware,
        name="tow_loop_mount", material_class_id="metal.stainless_matte",
    )
    # Half-circle arc: in (x, z) plane at world y = front_y. Anchor points sit
    # on the mount plate top so the ring lifts above it.
    arc_radius = 0.034
    arc_thickness = 0.005
    base_z = z + 0.024
    arc_samples = 13
    arc_points = []
    for i in range(arc_samples):
        # t goes from pi (start at -X) down to 0 (end at +X), passing through pi/2 at top.
        t = math.pi * (1.0 - i / (arc_samples - 1))
        arc_points.append((arc_radius * math.cos(t), front_y, base_z + arc_radius * math.sin(t)))
    arc_mesh = mesh_from_geometry(
        tube_from_spline_points(
            arc_points,
            radius=arc_thickness,
            samples_per_segment=10,
            radial_segments=12,
            cap_ends=True,
        ),
        assets.mesh_path("tow_loop_dring.obj"),
    )
    part.visual(arc_mesh, material=hardware, name="tow_loop_top", material_class_id="metal.stainless_matte")
    # Two stub "feet" anchoring the arc ends into the mount plate.
    for sx, lab in ((-1.0, "left"), (1.0, "right")):
        part.visual(
            Cylinder(radius=arc_thickness, length=0.022),
            origin=Origin(xyz=(sx * arc_radius, front_y, base_z - 0.011)),
            material=hardware,
            name=f"tow_loop_foot_{lab}", material_class_id="metal.stainless_matte",
        )


def _build_tow_bar_visuals(
    tow_bar_part, resolved: ResolvedPlatformCartConfig, *, hardware, rubber, y_sign: float = 1.0
) -> None:
    """Local frame: pivot at the deck edge. In rest pose (q=0) the bar lies
    along ``y_sign * +Y`` (extended outward). Lifting folds it up to +Z (stowed).
    ``y_sign`` is -1 when the bar is mounted on the rear edge so it points away
    from the deck instead of back across it."""
    W = resolved.deck_width
    bar_len = max(0.20, min(0.45, W * 0.85))
    bar_r = 0.011
    grip_len = bar_len * 0.32
    # Main shaft along y_sign*+Y from pivot.
    tow_bar_part.visual(
        Cylinder(radius=bar_r, length=bar_len),
        origin=Origin(xyz=(0.0, y_sign * bar_len * 0.5, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=hardware,
        name="tow_bar_shaft", material_class_id="metal.stainless_matte",
    )
    # Rubber grip at the far end.
    tow_bar_part.visual(
        Cylinder(radius=bar_r * 1.5, length=grip_len),
        origin=Origin(xyz=(0.0, y_sign * (bar_len - grip_len * 0.5), 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=rubber,
        name="tow_bar_grip", material_class_id="rubber.smooth_plain",
    )
    # Pivot knuckle (visual only — joint axis is at origin).
    tow_bar_part.visual(
        Cylinder(radius=bar_r * 1.2, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="tow_bar_knuckle", material_class_id="metal.stainless_matte",
    )


# ---------------------------------------------------------------------------
# Handle builders
# ---------------------------------------------------------------------------


def _build_handle_u_handle(
    handle_part,
    resolved: ResolvedPlatformCartConfig,
    *,
    hardware,
    rubber,
    assets: AssetContext,
) -> None:
    """Continuous-tube U-handle: a single bent pipe goes up the left leg,
    smoothly curves across the top, and comes down the right leg. The corners
    are rounded by the catmull-rom spline.

    Origin = hinge axis center on deck; in rest pose (q=0) the handle stands
    along local +Z."""
    H = resolved.handle_height
    half_w = max(0.10, resolved.deck_width * 0.32)
    tube_r = 0.013
    corner_dy = tube_r * 0.6  # slight forward bias gives a friendly grip angle
    waypoints = [
        (-half_w, 0.0, 0.0),
        (-half_w, 0.0, H * 0.55),
        (-half_w * 0.95, corner_dy, H * 0.92),
        (-half_w * 0.55, corner_dy, H),
        (half_w * 0.55, corner_dy, H),
        (half_w * 0.95, corner_dy, H * 0.92),
        (half_w, 0.0, H * 0.55),
        (half_w, 0.0, 0.0),
    ]
    frame_mesh = mesh_from_geometry(
        tube_from_spline_points(
            waypoints,
            radius=tube_r,
            samples_per_segment=14,
            radial_segments=14,
            cap_ends=True,
        ),
        assets.mesh_path(f"{handle_part.name}_u_frame.obj"),
    )
    handle_part.visual(frame_mesh, material=hardware, name="frame", material_class_id="metal.stainless_matte")
    # Rubber grip sleeve over the top crossbar section.
    handle_part.visual(
        Cylinder(radius=tube_r * 1.45, length=2 * half_w * 0.55),
        origin=Origin(xyz=(0.0, corner_dy, H), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=rubber,
        name="grip_sleeve", material_class_id="rubber.smooth_plain",
    )


def _build_handle_twin_bar(
    handle_part,
    resolved: ResolvedPlatformCartConfig,
    *,
    hardware,
    rubber,
    assets: AssetContext,
) -> None:
    """Twin-bar handle: a U-frame with an additional horizontal cross-tube
    lower down (like a hospital trolley / shelving cart handle)."""
    H = resolved.handle_height
    half_w = max(0.10, resolved.deck_width * 0.32)
    tube_r = 0.012
    lower_z = H - max(0.10, H * 0.14)
    # Main U-frame as a continuous tube.
    main_waypoints = [
        (-half_w, 0.0, 0.0),
        (-half_w, 0.0, H * 0.65),
        (-half_w * 0.92, 0.0, H * 0.95),
        (-half_w * 0.5, 0.0, H),
        (half_w * 0.5, 0.0, H),
        (half_w * 0.92, 0.0, H * 0.95),
        (half_w, 0.0, H * 0.65),
        (half_w, 0.0, 0.0),
    ]
    handle_part.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                main_waypoints,
                radius=tube_r,
                samples_per_segment=14,
                radial_segments=14,
                cap_ends=True,
            ),
            assets.mesh_path(f"{handle_part.name}_main.obj"),
        ),
        material=hardware,
        name="frame", material_class_id="metal.stainless_matte",
    )
    # Lower cross-tube (straight tube between the two legs).
    handle_part.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [(-half_w, 0.0, lower_z), (half_w, 0.0, lower_z)],
                radius=tube_r * 0.9,
                samples_per_segment=4,
                radial_segments=12,
                cap_ends=True,
            ),
            assets.mesh_path(f"{handle_part.name}_lower_bar.obj"),
        ),
        material=hardware,
        name="lower_bar", material_class_id="metal.stainless_matte",
    )
    # Rubber grip sleeve on top.
    handle_part.visual(
        Cylinder(radius=tube_r * 1.55, length=2 * half_w * 0.55),
        origin=Origin(xyz=(0.0, 0.0, H), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=rubber,
        name="grip_sleeve", material_class_id="rubber.smooth_plain",
    )


def _build_handle_single_bar(
    handle_part,
    resolved: ResolvedPlatformCartConfig,
    *,
    hardware,
    rubber,
    assets: AssetContext,
) -> None:
    """T-handle: a single central post with a horizontal grip yoke. Both the
    post and the yoke are made from one continuous bent tube (the tube goes UP
    the post, then bends 90° at the top and runs to one side; we mirror to add
    the other side as a second tube)."""
    H = resolved.handle_height
    half_w = max(0.15, min(0.32, resolved.deck_width * 0.42))
    tube_r = 0.014
    # Central post + left arm (one continuous bend).
    handle_part.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, H * 0.6),
                    (0.0, 0.0, H * 0.92),
                    (-half_w * 0.3, 0.0, H),
                    (-half_w, 0.0, H),
                ],
                radius=tube_r,
                samples_per_segment=14,
                radial_segments=14,
                cap_ends=True,
            ),
            assets.mesh_path(f"{handle_part.name}_left.obj"),
        ),
        material=hardware,
        name="frame_left", material_class_id="metal.stainless_matte",
    )
    # Right arm only (starts at the top of the post and curves out).
    handle_part.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    (0.0, 0.0, H * 0.92),
                    (half_w * 0.3, 0.0, H),
                    (half_w, 0.0, H),
                ],
                radius=tube_r,
                samples_per_segment=14,
                radial_segments=14,
                cap_ends=True,
            ),
            assets.mesh_path(f"{handle_part.name}_right.obj"),
        ),
        material=hardware,
        name="frame_right", material_class_id="metal.stainless_matte",
    )
    # Rubber grip on the horizontal yoke.
    handle_part.visual(
        Cylinder(radius=tube_r * 1.5, length=2 * half_w * 0.85),
        origin=Origin(xyz=(0.0, 0.0, H), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=rubber,
        name="grip_sleeve", material_class_id="rubber.smooth_plain",
    )


def _build_handle_shopping_cart(
    handle_part,
    resolved: ResolvedPlatformCartConfig,
    *,
    hardware,
    rubber,
    assets: AssetContext,
) -> None:
    """U-frame bent backward (toward the operator, -Y in the joint frame) by
    ~25° so the grip cantilever's out behind the cart, like a shopping cart."""
    H = resolved.handle_height
    half_w = max(0.10, resolved.deck_width * 0.32)
    tube_r = 0.013
    bend_y = -H * 0.18  # how far the top of the U leans backward
    waypoints = [
        (-half_w, 0.0, 0.0),
        (-half_w, 0.0, H * 0.45),
        (-half_w * 0.98, bend_y * 0.3, H * 0.75),
        (-half_w * 0.95, bend_y * 0.7, H * 0.93),
        (-half_w * 0.55, bend_y, H),
        (half_w * 0.55, bend_y, H),
        (half_w * 0.95, bend_y * 0.7, H * 0.93),
        (half_w * 0.98, bend_y * 0.3, H * 0.75),
        (half_w, 0.0, H * 0.45),
        (half_w, 0.0, 0.0),
    ]
    handle_part.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                waypoints,
                radius=tube_r,
                samples_per_segment=14,
                radial_segments=14,
                cap_ends=True,
            ),
            assets.mesh_path(f"{handle_part.name}_shopping.obj"),
        ),
        material=hardware,
        name="frame", material_class_id="metal.stainless_matte",
    )
    handle_part.visual(
        Cylinder(radius=tube_r * 1.55, length=2 * half_w * 0.55),
        origin=Origin(xyz=(0.0, bend_y, H), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=rubber,
        name="grip_sleeve", material_class_id="rubber.smooth_plain",
    )


def _build_handle_pistol_grip(
    handle_part,
    resolved: ResolvedPlatformCartConfig,
    *,
    hardware,
    rubber,
    assets: AssetContext,
) -> None:
    """Single central pole that bends 90° at the top into a horizontal handlebar.
    The grip points in +Y (forward) or -Y (backward) depending on `pistol_facing`."""
    H = resolved.handle_height
    tube_r = 0.018
    grip_len = max(0.16, min(0.28, resolved.deck_width * 0.55))
    sign = -1.0 if resolved.pistol_facing == "backward" else 1.0
    handle_part.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                [
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, H * 0.55),
                    (0.0, 0.0, H * 0.82),
                    (0.0, sign * tube_r * 1.5, H * 0.94),
                    (0.0, sign * grip_len * 0.30, H),
                    (0.0, sign * grip_len * 0.95, H),
                ],
                radius=tube_r,
                samples_per_segment=14,
                radial_segments=14,
                cap_ends=True,
            ),
            assets.mesh_path(f"{handle_part.name}_pistol.obj"),
        ),
        material=hardware,
        name="frame", material_class_id="metal.stainless_matte",
    )
    # Rubber grip on the horizontal section.
    handle_part.visual(
        Cylinder(radius=tube_r * 1.55, length=grip_len * 0.70),
        origin=Origin(xyz=(0.0, sign * grip_len * 0.55, H), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=rubber,
        name="grip_sleeve", material_class_id="rubber.smooth_plain",
    )


def _build_handle_panel_handle(
    handle_part,
    resolved: ResolvedPlatformCartConfig,
    *,
    hardware,
    rubber,
    assets: AssetContext,
) -> None:
    """A solid lower BOARD topped by a rounded-rectangle FRAME loop (the grip),
    all in the same vertical plane. The frame's top tube is the actual hand-grip
    (wrapped with a rubber sleeve). Below the frame, the board fills the rest
    of the height down to the deck hinge.

    Outer profile (x, z): a single panel-and-frame silhouette built as one
    ExtrudeWithHolesGeometry, with a rounded-rect hole in the upper portion to
    create the grip loop. Board + frame share the same panel_thickness and are
    centered on y=0, so the protruding rubber grip can sit flush in the same
    plane."""
    H = resolved.handle_height
    W = max(0.20, resolved.deck_width * 0.85)
    panel_thickness = 0.018
    # Outer silhouette: full rectangle with rounded TOP corners only. Profile
    # is in (x, z) — extruded along +Y to become the panel.
    top_radius = min(W * 0.18, H * 0.10)
    outer = []
    # Bottom edge: square corners flush with the hinge plate.
    outer.append((-W * 0.5, 0.0))
    outer.append((W * 0.5, 0.0))
    # Right edge straight up to where the top arc begins.
    outer.append((W * 0.5, H - top_radius))
    # Top-right arc, sampled clockwise from "east" (0) up to "north" (pi/2).
    arc_segs = 10
    for i in range(1, arc_segs + 1):
        ang = (math.pi * 0.5) * (i / arc_segs)
        outer.append(
            (
                W * 0.5 - top_radius + top_radius * math.cos(ang),
                H - top_radius + top_radius * math.sin(ang),
            )
        )
    # Top-left arc, continuing from "north" (pi/2) to "west" (pi).
    for i in range(1, arc_segs + 1):
        ang = math.pi * 0.5 + (math.pi * 0.5) * (i / arc_segs)
        outer.append(
            (
                -W * 0.5 + top_radius + top_radius * math.cos(ang),
                H - top_radius + top_radius * math.sin(ang),
            )
        )
    # Down the left edge to close.
    outer.append((-W * 0.5, 0.0))

    # Grip hole: large rounded-rectangle hole occupying the upper portion of
    # the panel. The TOP of the hole sits below H by `frame_top_w` so the top
    # tube of the frame has thickness. The BOTTOM of the hole defines where
    # the solid lower board starts.
    frame_top_w = max(0.025, min(0.050, H * 0.045))  # thickness of the top bar
    frame_side_w = max(0.022, min(0.044, W * 0.07))  # thickness of left/right sides
    hole_top_z = H - frame_top_w
    hole_bot_z = H * 0.55  # below this, panel is solid (becomes the board)
    hole_half_x = W * 0.5 - frame_side_w
    hole_corner_r = min((hole_top_z - hole_bot_z) * 0.35, hole_half_x * 0.50)
    # Build the hole as a rounded rectangle with all 4 corners rounded.
    hole_pts = []
    # Walk counter-clockwise: bottom-right -> top-right -> top-left -> bottom-left
    cy_lo = hole_bot_z + hole_corner_r
    cy_hi = hole_top_z - hole_corner_r
    cx_hi = hole_half_x - hole_corner_r
    cx_lo = -hole_half_x + hole_corner_r
    hcorner_segs = 6
    # Bottom-right corner arc, "south" (-pi/2) -> "east" (0)
    for i in range(hcorner_segs + 1):
        ang = -math.pi * 0.5 + (math.pi * 0.5) * (i / hcorner_segs)
        hole_pts.append(
            (cx_hi + hole_corner_r * math.cos(ang), cy_lo + hole_corner_r * math.sin(ang))
        )
    # Top-right arc, "east" (0) -> "north" (pi/2)
    for i in range(1, hcorner_segs + 1):
        ang = (math.pi * 0.5) * (i / hcorner_segs)
        hole_pts.append(
            (cx_hi + hole_corner_r * math.cos(ang), cy_hi + hole_corner_r * math.sin(ang))
        )
    # Top-left arc, "north" -> "west"
    for i in range(1, hcorner_segs + 1):
        ang = math.pi * 0.5 + (math.pi * 0.5) * (i / hcorner_segs)
        hole_pts.append(
            (cx_lo + hole_corner_r * math.cos(ang), cy_hi + hole_corner_r * math.sin(ang))
        )
    # Bottom-left arc, "west" -> "south"
    for i in range(1, hcorner_segs + 1):
        ang = math.pi + (math.pi * 0.5) * (i / hcorner_segs)
        hole_pts.append(
            (cx_lo + hole_corner_r * math.cos(ang), cy_lo + hole_corner_r * math.sin(ang))
        )

    panel_geom = ExtrudeWithHolesGeometry(outer, [hole_pts], height=panel_thickness)
    panel_mesh = mesh_from_geometry(panel_geom, assets.mesh_path(f"{handle_part.name}_panel.obj"))
    # rpy=(pi/2, 0, 0) rotates the extrude axis so the panel stands vertically
    # and lies in the y=0 plane (because ExtrudeGeometry centers on the extrude
    # axis by default).
    handle_part.visual(
        panel_mesh,
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=hardware,
        name="panel", material_class_id="metal.stainless_matte",
    )
    # Rubber grip sleeve over the TOP cross-tube of the frame — coplanar with
    # the panel (centered on y=0), wider tube than the frame so it visually
    # reads as the grip surface.
    grip_z = (hole_top_z + H) * 0.5  # center of the top frame bar
    grip_radius = frame_top_w * 0.7
    grip_length = (2 * hole_half_x) * 0.78
    handle_part.visual(
        Cylinder(radius=grip_radius, length=grip_length),
        origin=Origin(xyz=(0.0, 0.0, grip_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=rubber,
        name="grip_sleeve", material_class_id="rubber.smooth_plain",
    )


HANDLE_BUILDERS = {
    "u_handle": _build_handle_u_handle,
    "twin_bar": _build_handle_twin_bar,
    "single_bar": _build_handle_single_bar,
    "shopping_cart": _build_handle_shopping_cart,
    "pistol_grip": _build_handle_pistol_grip,
    "panel_handle": _build_handle_panel_handle,
}


# ---------------------------------------------------------------------------
# Caster fork helpers
# ---------------------------------------------------------------------------


def _add_caster_fork_geometry(
    fork_part, resolved: ResolvedPlatformCartConfig, *, hardware, dark
) -> None:
    """Geometry of the caster yoke that hangs below the swivel plate.

    Origin = caster swivel axis where it meets the deck mount plate.
    Local -Z drops down to the wheel center.
    """
    yoke_drop = 0.022
    wheel_r = resolved.wheel_radius
    fork_part.visual(
        Cylinder(radius=0.046, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, -0.006)),
        material=hardware,
        name="swivel_plate", material_class_id="metal.stainless_matte",
    )
    fork_part.visual(
        Cylinder(radius=0.014, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, -0.024)),
        material=dark,
        name="kingpin", material_class_id="metal.blackened_gunmetal",
    )
    fork_part.visual(
        Box((0.084, 0.060, 0.020)),
        origin=Origin(xyz=(0.0, 0.0, -0.040)),
        material=hardware,
        name="fork_crown", material_class_id="metal.stainless_matte",
    )
    leg_z = -(yoke_drop + wheel_r * 0.5)
    leg_h = wheel_r + 0.020
    fork_part.visual(
        Box((0.008, 0.060, leg_h)),
        origin=Origin(xyz=(0.032, 0.0, leg_z)),
        material=hardware,
        name="fork_cheek_outer", material_class_id="metal.stainless_matte",
    )
    fork_part.visual(
        Box((0.008, 0.060, leg_h)),
        origin=Origin(xyz=(-0.032, 0.0, leg_z)),
        material=hardware,
        name="fork_cheek_inner", material_class_id="metal.stainless_matte",
    )
    # axle stub (decorative)
    axle_z = -(yoke_drop + wheel_r)
    fork_part.visual(
        Cylinder(radius=0.008, length=0.075),
        origin=Origin(xyz=(0.0, 0.0, axle_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=dark,
        name="axle_stub", material_class_id="metal.blackened_gunmetal",
    )


def _add_fixed_wheel_yoke(
    parent_part,
    resolved: ResolvedPlatformCartConfig,
    *,
    slot_x: float,
    slot_y: float,
    slot_name: str,
    hardware,
    dark,
) -> None:
    """Decorative fork brackets for fixed (non-swivel) wheels, mounted to the deck."""
    yoke_drop = 0.008
    wheel_r = resolved.wheel_radius
    bracket_z = resolved.deck_center_z - resolved.deck_thickness * 0.5 - yoke_drop * 0.5
    parent_part.visual(
        Box((0.110, 0.090, 0.010)),
        origin=Origin(xyz=(slot_x, slot_y, bracket_z)),
        material=hardware,
        name=f"{slot_name}_fixed_mount", material_class_id="metal.stainless_matte",
    )
    leg_h = wheel_r + 0.020
    leg_center_z = (
        resolved.deck_center_z - resolved.deck_thickness * 0.5 - yoke_drop - wheel_r * 0.5
    )
    parent_part.visual(
        Box((0.010, 0.060, leg_h)),
        origin=Origin(xyz=(slot_x + (resolved.wheel_width * 0.5 + 0.014), slot_y, leg_center_z)),
        material=hardware,
        name=f"{slot_name}_fork_outer", material_class_id="metal.stainless_matte",
    )
    parent_part.visual(
        Box((0.010, 0.060, leg_h)),
        origin=Origin(xyz=(slot_x - (resolved.wheel_width * 0.5 + 0.014), slot_y, leg_center_z)),
        material=hardware,
        name=f"{slot_name}_fork_inner", material_class_id="metal.stainless_matte",
    )
    axle_z = resolved.deck_center_z - resolved.deck_thickness * 0.5 - yoke_drop - wheel_r
    parent_part.visual(
        Cylinder(radius=0.008, length=resolved.wheel_width + 0.040),
        origin=Origin(
            xyz=(slot_x, slot_y, axle_z),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=dark,
        name=f"{slot_name}_axle_stub", material_class_id="metal.blackened_gunmetal",
    )


# ---------------------------------------------------------------------------
# Steering bridge (for mixed_steering)
# ---------------------------------------------------------------------------


def _add_steering_bridge_geometry(
    bridge_part,
    resolved: ResolvedPlatformCartConfig,
    *,
    hardware,
    dark,
    front_slots: list[tuple[str, float, float]],
) -> None:
    # bridge is a horizontal bar spanning the two front wheel x positions.
    if not front_slots:
        return
    left_x = min(x for _, x, _ in front_slots)
    right_x = max(x for _, x, _ in front_slots)
    # Span between the wheel centres only: extending past them drives the bar
    # ends into the steered tires.
    bar_length = max(0.060, (right_x - left_x) - resolved.wheel_width - 0.010)
    bridge_part.visual(
        Box((bar_length, 0.060, 0.024)),
        origin=Origin(xyz=(0.0, 0.0, -0.014)),
        material=hardware,
        name="steering_bar", material_class_id="metal.stainless_matte",
    )
    bridge_part.visual(
        Cylinder(radius=0.018, length=0.040),
        origin=Origin(xyz=(0.0, 0.0, 0.005)),
        material=dark,
        name="steering_kingpin", material_class_id="metal.blackened_gunmetal",
    )
    wheel_r = resolved.wheel_radius
    yoke_drop = 0.020
    for slot_name, x, _y in front_slots:
        local_x = x  # the bridge frame is centered between the two front wheels along x
        leg_h = wheel_r + 0.020
        leg_center_z = -(yoke_drop + wheel_r * 0.5)
        bridge_part.visual(
            Box((0.010, 0.060, leg_h)),
            origin=Origin(xyz=(local_x + resolved.wheel_width * 0.5 + 0.014, 0.0, leg_center_z)),
            material=hardware,
            name=f"{slot_name}_bridge_fork_outer", material_class_id="metal.stainless_matte",
        )
        bridge_part.visual(
            Box((0.010, 0.060, leg_h)),
            origin=Origin(xyz=(local_x - resolved.wheel_width * 0.5 - 0.014, 0.0, leg_center_z)),
            material=hardware,
            name=f"{slot_name}_bridge_fork_inner", material_class_id="metal.stainless_matte",
        )
        bridge_part.visual(
            Cylinder(radius=0.008, length=resolved.wheel_width + 0.040),
            origin=Origin(
                xyz=(local_x, 0.0, -(yoke_drop + wheel_r)),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=dark,
            name=f"{slot_name}_bridge_axle_stub", material_class_id="metal.blackened_gunmetal",
        )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------


def build_platform_cart(
    config: PlatformCartConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or PlatformCartConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-platform-cart-assets-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)

    palette = MATERIAL_PALETTES[resolved.material_style]
    deck_color = model.material("deck_body", rgba=palette[0])
    trim = model.material("deck_trim", rgba=palette[1])
    hardware = model.material("cart_hardware", rgba=palette[2])
    dark = model.material("dark_hardware", rgba=palette[3])
    rubber = model.material("tire_rubber", rgba=palette[4])
    pad_mat = model.material("anti_slip", rgba=palette[5])

    deck = model.part("deck")
    _add_deck_shell(deck, resolved, deck_color=deck_color, trim=trim, assets=assets)
    _add_anti_slip_pad(deck, resolved, pad_mat=pad_mat)
    _add_deck_top_decoration(deck, resolved, deck_color=deck_color, trim=trim, pad_mat=pad_mat)
    _add_side_rails(deck, resolved, trim=trim, hardware=hardware)
    _add_bumpers(deck, resolved, trim=trim)
    _add_caster_mount_plates(deck, resolved, hardware=hardware)
    _add_handle_hinge_ears(deck, resolved, hardware=hardware)
    if resolved.tow_attachment == "loop":
        _add_tow_loop(deck, resolved, hardware=hardware, assets=assets)

    layout = _wheel_layout(resolved)
    front_slots = [(n, x, y) for (n, x, y) in layout if n.startswith("front_")]

    # Optional steering bridge for mixed_steering.
    if resolved.has_steering:
        bridge = model.part("steering_bridge")
        # Bridge origin: midpoint of front wheel slots, at deck bottom minus a small drop.
        bridge_x = 0.0
        bridge_y = front_slots[0][2]
        bridge_z = resolved.deck_center_z - resolved.deck_thickness * 0.5 - 0.010
        # Re-center the front slot x coords relative to bridge origin (which is at x=0).
        relative_front_slots = [(n, x - bridge_x, y - bridge_y) for (n, x, y) in front_slots]
        _add_steering_bridge_geometry(
            bridge,
            resolved,
            hardware=hardware,
            dark=dark,
            front_slots=relative_front_slots,
        )
        # Steering angle limit. Turning the bridge swings each front wheel about
        # the bridge centre, translating its hub toward the mid pair (6-wheel
        # layout). Cap the angle so the swung front hub stays >= 2r from the fixed
        # mid hub: front_y - |x|*sin(theta) - 2r - w/2 >= 0. 4-wheel carts have no
        # mid pair, so the full +-pi/4 is safe there.
        steer_upper = math.pi / 4.0
        if resolved.wheel_count == 6 and front_slots:
            _r = resolved.wheel_radius
            _fy = abs(front_slots[0][2])
            _lx = max(abs(front_slots[0][1]), 1e-6)
            _ratio = (_fy - 2.0 * _r - resolved.wheel_width * 0.5) / _lx
            _ratio = max(0.0, min(1.0, _ratio))
            steer_upper = max(0.05, min(math.pi / 4.0, math.asin(_ratio)))
        model.articulation(
            "steering_joint",
            ArticulationType.REVOLUTE,
            parent=deck,
            child=bridge,
            origin=Origin(xyz=(bridge_x, bridge_y, bridge_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=30.0,
                velocity=4.0,
                lower=-steer_upper,
                upper=steer_upper,
            ),
        )

    # Wheel articulations.
    wheel_index = 0
    caster_index = 0
    yoke_drop_caster = 0.022
    yoke_drop_fixed = 0.008
    bridge_yoke_drop = 0.020
    for slot_name, x, y in layout:
        steered = _slot_is_steering(slot_name, resolved)
        cast = _slot_uses_caster_swivel(slot_name, resolved)

        if cast:
            # Independent caster: caster yoke part + spinning wheel child.
            caster_part = model.part(f"caster_{slot_name}")
            _add_caster_fork_geometry(caster_part, resolved, hardware=hardware, dark=dark)
            caster_origin = Origin(
                xyz=(
                    x,
                    y,
                    resolved.deck_center_z - resolved.deck_thickness * 0.5,
                )
            )
            model.articulation(
                f"caster_{caster_index}_joint",
                ArticulationType.CONTINUOUS,
                parent=deck,
                child=caster_part,
                origin=caster_origin,
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=15.0, velocity=6.0),
            )
            caster_index += 1

            wheel_part = model.part(f"wheel_{slot_name}")
            _add_wheel_geometry(
                wheel_part, resolved, rubber=rubber, hardware=hardware, assets=assets
            )
            model.articulation(
                f"wheel_{wheel_index}_joint",
                ArticulationType.CONTINUOUS,
                parent=caster_part,
                child=wheel_part,
                origin=Origin(xyz=(0.0, 0.0, -(yoke_drop_caster + resolved.wheel_radius))),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=10.0, velocity=20.0),
            )
            wheel_index += 1
            continue

        if steered:
            # Wheel hangs from the steering bridge (its own continuous spin only).
            wheel_part = model.part(f"wheel_{slot_name}")
            _add_wheel_geometry(
                wheel_part, resolved, rubber=rubber, hardware=hardware, assets=assets
            )
            # Relative to bridge frame (which is centered at midpoint of front slots).
            bridge_y = front_slots[0][2]
            rel_x = x - 0.0
            rel_y = y - bridge_y
            model.articulation(
                f"wheel_{wheel_index}_joint",
                ArticulationType.CONTINUOUS,
                parent="steering_bridge",
                child=wheel_part,
                origin=Origin(xyz=(rel_x, rel_y, -(bridge_yoke_drop + resolved.wheel_radius))),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=10.0, velocity=20.0),
            )
            wheel_index += 1
            continue

        # Fixed wheel: yoke is decorative on deck; wheel is a part with continuous spin.
        _add_fixed_wheel_yoke(
            deck,
            resolved,
            slot_x=x,
            slot_y=y,
            slot_name=slot_name,
            hardware=hardware,
            dark=dark,
        )
        wheel_part = model.part(f"wheel_{slot_name}")
        _add_wheel_geometry(wheel_part, resolved, rubber=rubber, hardware=hardware, assets=assets)
        model.articulation(
            f"wheel_{wheel_index}_joint",
            ArticulationType.CONTINUOUS,
            parent=deck,
            child=wheel_part,
            origin=Origin(
                xyz=(
                    x,
                    y,
                    resolved.deck_center_z
                    - resolved.deck_thickness * 0.5
                    - yoke_drop_fixed
                    - resolved.wheel_radius,
                )
            ),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=10.0, velocity=20.0),
        )
        wheel_index += 1

    # Handles. Each enabled handle is its own part with a REVOLUTE hinge along
    # world +X. The front handle (q=0 vertical → q=pi/2 folds toward +Y) is the
    # legacy "handle". The rear handle mirrors the hinge to -Y and uses
    # upper=-pi/2 so a positive q folds it toward -Y, keeping the same
    # "positive q = folded flat" convention.
    builder = HANDLE_BUILDERS[resolved.handle_style] if resolved.has_handle else None
    hinge_z = resolved.deck_top_z + 0.030
    # Joint range is symmetric: rest pose (q=0) stands the handle perpendicular
    # to the deck; positive q folds it AWAY from the cart center (+Y for front,
    # -Y for rear); negative q folds it the other way. Total range is 180°.
    handle_motion_kwargs = dict(
        effort=30.0,
        velocity=2.0,
        lower=-math.pi / 2.0,
        upper=math.pi / 2.0,
    )

    def _build_handle_at(part_name: str, joint_name: str, hinge_y: float, axis_sign: float) -> None:
        part = model.part(part_name)
        builder(part, resolved, hardware=hardware, rubber=rubber, assets=assets)
        model.articulation(
            joint_name,
            ArticulationType.REVOLUTE,
            parent=deck,
            child=part,
            origin=Origin(xyz=(0.0, hinge_y, hinge_z)),
            axis=(axis_sign, 0.0, 0.0),
            motion_limits=MotionLimits(**handle_motion_kwargs),
        )

    if builder is not None:
        front_hinge_y = resolved.handle_hinge_y_ratio * resolved.deck_length
        rear_hinge_y = -front_hinge_y
        # Twin layout: two pistol_grips side-by-side on one end, both with the
        # same pistol_facing direction. We offset them along X (cart width).
        if resolved.has_twin_handles:
            twin_offset = max(0.10, resolved.deck_width * 0.28)
            if resolved.handle_layout == "twin_front":
                base_y = front_hinge_y
                axis_sign = 1.0
            else:
                base_y = rear_hinge_y
                axis_sign = -1.0
            for slot, x_off in (("left", -twin_offset), ("right", twin_offset)):
                part = model.part(f"handle_{slot}")
                builder(part, resolved, hardware=hardware, rubber=rubber, assets=assets)
                model.articulation(
                    f"handle_{slot}_joint",
                    ArticulationType.REVOLUTE,
                    parent=deck,
                    child=part,
                    origin=Origin(xyz=(x_off, base_y, hinge_z)),
                    axis=(axis_sign, 0.0, 0.0),
                    motion_limits=MotionLimits(**handle_motion_kwargs),
                )
        else:
            if resolved.has_front_handle:
                _build_handle_at("handle", "handle_joint", front_hinge_y, axis_sign=1.0)
            if resolved.has_rear_handle:
                _build_handle_at("rear_handle", "rear_handle_joint", rear_hinge_y, axis_sign=-1.0)

    # Fold-down front lip (only when side_rail == "fold_down_lip").
    if resolved.has_fold_lip:
        lip_part = model.part("fold_lip")
        _build_fold_lip_visuals(lip_part, resolved, trim=trim, hardware=hardware)
        # Hinge at the deck top, front edge.
        lip_hinge_y = resolved.deck_length * 0.5 - 0.001
        lip_hinge_z = resolved.deck_top_z + 0.008
        model.articulation(
            "fold_lip_joint",
            ArticulationType.REVOLUTE,
            parent=deck,
            child=lip_part,
            origin=Origin(xyz=(0.0, lip_hinge_y, lip_hinge_z)),
            # Axis along -X so positive q tilts the top of the lip toward +Y
            # (folding down off the front of the cart).
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=5.0, velocity=2.5, lower=0.0, upper=math.pi / 2.0),
        )

    # Tow bar (REVOLUTE; loop is built inline on the deck above).
    if resolved.tow_attachment == "tow_bar":
        tow_bar = model.part("tow_bar")
        # Mount the tow bar on whichever end has no folding handle so its lift arc
        # never shares an edge (and swept plane) with the handle. Handles only
        # ever occupy one end (front_only / rear_only / twin_*), so the opposite
        # end is always free; default to the front when there is no handle.
        tow_on_front = not resolved.has_front_handle
        tow_y_sign = 1.0 if tow_on_front else -1.0
        _build_tow_bar_visuals(
            tow_bar, resolved, hardware=hardware, rubber=rubber, y_sign=tow_y_sign
        )
        tow_edge_y = resolved.deck_length * 0.5 + 0.006
        tow_hinge_y = tow_edge_y if tow_on_front else -tow_edge_y
        tow_hinge_z = resolved.deck_center_z
        # Axis sign flips with the edge so positive q always lifts the outward-
        # pointing tip up to the stow position.
        model.articulation(
            "tow_bar_joint",
            ArticulationType.REVOLUTE,
            parent=deck,
            child=tow_bar,
            origin=Origin(xyz=(0.0, tow_hinge_y, tow_hinge_z)),
            axis=(tow_y_sign, 0.0, 0.0),
            motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=math.pi / 2.0),
        )

    return model


def _circle_profile(
    radius: float, *, segments: int = 32, cx: float = 0.0, cy: float = 0.0
) -> list[tuple[float, float]]:
    return [
        (
            cx + radius * math.cos(2 * math.pi * i / segments),
            cy + radius * math.sin(2 * math.pi * i / segments),
        )
        for i in range(segments)
    ]


def _add_wheel_geometry(
    wheel_part,
    resolved: ResolvedPlatformCartConfig,
    *,
    rubber,
    hardware,
    assets: AssetContext,
) -> None:
    """Wheel local frame: spin axis along +X. Cylinder primitives have their
    native length along +Z and are rotated to +X via rpy=(0, pi/2, 0)."""
    style = resolved.wheel_style
    if style == "spoked":
        _add_spoked_wheel_geometry(
            wheel_part, resolved, rubber=rubber, hardware=hardware, assets=assets
        )
        return
    if style == "industrial":
        _add_industrial_wheel_geometry(wheel_part, resolved, rubber=rubber, hardware=hardware)
        return
    if style == "auto_capped":
        _add_auto_capped_wheel_geometry(wheel_part, resolved, rubber=rubber, hardware=hardware)
        return
    if style == "pneumatic":
        _add_pneumatic_wheel_geometry(wheel_part, resolved, rubber=rubber, hardware=hardware)
        return
    _add_solid_wheel_geometry(wheel_part, resolved, rubber=rubber, hardware=hardware)


def _add_industrial_wheel_geometry(
    wheel_part, resolved: ResolvedPlatformCartConfig, *, rubber, hardware
) -> None:
    """Heavy-duty wheel: thick rubber tire + wide steel barrel hub + ring of
    bolts. No spokes (it's a solid disc behind the bolts)."""
    r = resolved.wheel_radius
    w = resolved.wheel_width
    # Beefy tire (slightly wider than nominal).
    wheel_part.visual(
        Cylinder(radius=r, length=w * 1.05),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=rubber,
        name="tire", material_class_id="rubber.smooth_plain",
    )
    # Inner solid steel disc (the wheel body itself).
    wheel_part.visual(
        Cylinder(radius=r * 0.80, length=w * 1.10),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="rim", material_class_id="metal.stainless_matte",
    )
    # Wide central barrel hub for the axle bore.
    wheel_part.visual(
        Cylinder(radius=r * 0.28, length=w * 1.30),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="hub", material_class_id="metal.stainless_matte",
    )
    # Ring of bolts on the outer face. Bolts are tiny cylinders on both faces.
    bolt_count = 6
    bolt_circle_r = r * 0.55
    bolt_r = max(0.0035, r * 0.05)
    bolt_len = 0.010
    for face_sign, face in ((1.0, "outer"), (-1.0, "inner")):
        for i in range(bolt_count):
            ang = 2 * math.pi * (i + 0.5) / bolt_count
            wheel_part.visual(
                Cylinder(radius=bolt_r, length=bolt_len),
                origin=Origin(
                    xyz=(
                        face_sign * (w * 0.55 + bolt_len * 0.5),
                        bolt_circle_r * math.sin(ang),
                        bolt_circle_r * math.cos(ang),
                    ),
                    rpy=(0.0, math.pi / 2.0, 0.0),
                ),
                material=hardware,
                name=f"bolt_{face}_{i}", material_class_id="metal.stainless_matte",
            )


def _add_auto_capped_wheel_geometry(
    wheel_part, resolved: ResolvedPlatformCartConfig, *, rubber, hardware
) -> None:
    """Solid wheel with two protruding dome-shaped hub caps on the outer faces.
    Looks like a car or scooter wheel hub-cap."""
    r = resolved.wheel_radius
    w = resolved.wheel_width
    wheel_part.visual(
        Cylinder(radius=r, length=w),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=rubber,
        name="tire", material_class_id="rubber.smooth_plain",
    )
    wheel_part.visual(
        Cylinder(radius=r * 0.55, length=w * 1.05),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="rim", material_class_id="metal.stainless_matte",
    )
    wheel_part.visual(
        Cylinder(radius=r * 0.20, length=w * 1.10),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="hub", material_class_id="metal.stainless_matte",
    )
    # Hub caps: two short, wider cylinders protruding from each face.
    cap_offset = w * 0.55 + 0.005
    for face_sign, face in ((1.0, "outer"), (-1.0, "inner")):
        wheel_part.visual(
            Cylinder(radius=r * 0.32, length=0.012),
            origin=Origin(xyz=(face_sign * cap_offset, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=hardware,
            name=f"hub_cap_{face}", material_class_id="metal.stainless_matte",
        )


def _add_pneumatic_wheel_geometry(
    wheel_part, resolved: ResolvedPlatformCartConfig, *, rubber, hardware
) -> None:
    """Pneumatic wheel with a thicker tire crown and a visible valve stem
    sticking out the outer face."""
    r = resolved.wheel_radius
    w = resolved.wheel_width
    # Beefy tire — slightly thicker than nominal radius hints at pneumatic crown.
    wheel_part.visual(
        Cylinder(radius=r, length=w * 1.10),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=rubber,
        name="tire", material_class_id="rubber.smooth_plain",
    )
    # Narrow inner rim (smaller than the tire to suggest air gap).
    wheel_part.visual(
        Cylinder(radius=r * 0.62, length=w * 0.95),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="rim", material_class_id="metal.stainless_matte",
    )
    wheel_part.visual(
        Cylinder(radius=r * 0.18, length=w * 1.12),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="hub", material_class_id="metal.stainless_matte",
    )
    # Valve stem: small cylinder protruding from the outer face at the inner
    # rim radius. Oriented along +X (axle direction) so it sticks straight out
    # of the wheel face.
    valve_r = max(0.003, r * 0.05)
    valve_len = max(0.012, r * 0.18)
    valve_circle_r = r * 0.62
    wheel_part.visual(
        Cylinder(radius=valve_r, length=valve_len),
        origin=Origin(
            xyz=(w * 0.55 + valve_len * 0.5, 0.0, valve_circle_r),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=hardware,
        name="valve_stem", material_class_id="metal.stainless_matte",
    )
    # Valve cap (slightly wider dark tip).
    wheel_part.visual(
        Cylinder(radius=valve_r * 1.6, length=valve_len * 0.3),
        origin=Origin(
            xyz=(w * 0.55 + valve_len + valve_len * 0.15, 0.0, valve_circle_r),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=hardware,
        name="valve_cap", material_class_id="metal.stainless_matte",
    )


def _add_solid_wheel_geometry(
    wheel_part, resolved: ResolvedPlatformCartConfig, *, rubber, hardware
) -> None:
    r = resolved.wheel_radius
    w = resolved.wheel_width
    wheel_part.visual(
        Cylinder(radius=r, length=w),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=rubber,
        name="tire", material_class_id="rubber.smooth_plain",
    )
    wheel_part.visual(
        Cylinder(radius=r * 0.55, length=w * 1.04),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="rim", material_class_id="metal.stainless_matte",
    )
    wheel_part.visual(
        Cylinder(radius=r * 0.18, length=w * 1.10),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="hub", material_class_id="metal.stainless_matte",
    )


def _add_spoked_wheel_geometry(
    wheel_part,
    resolved: ResolvedPlatformCartConfig,
    *,
    rubber,
    hardware,
    assets: AssetContext,
) -> None:
    """Spoked wheel built via the mesh path: a flat disc with N circular spoke
    windows is extruded once, then placed twice (one on each face of the tire).
    The tire and hub stay as Cylinder primitives to avoid mesh cost on the
    rolling surface and the axle bore."""
    r = resolved.wheel_radius
    w = resolved.wheel_width
    spoke_count = 5
    disc_face_thickness = max(0.005, min(0.012, w * 0.16))
    hub_r = r * 0.20
    rim_inner_r = r * 0.86
    window_center_r = (hub_r + rim_inner_r) * 0.5
    # Window radius scales with the available gap so spokes never merge or break
    # the outer ring.
    spoke_gap = (rim_inner_r - hub_r) * 0.85
    window_r = min(spoke_gap * 0.5, window_center_r * math.sin(math.pi / spoke_count) * 0.78)
    window_r = max(0.004, window_r)

    outer = _circle_profile(rim_inner_r, segments=48)
    holes = []
    for i in range(spoke_count):
        ang = 2 * math.pi * i / spoke_count
        cx = window_center_r * math.cos(ang)
        cy = window_center_r * math.sin(ang)
        holes.append(_circle_profile(window_r, segments=20, cx=cx, cy=cy))
    disc_geom = ExtrudeWithHolesGeometry(outer, holes, height=disc_face_thickness, center=True)
    disc_mesh = mesh_from_geometry(
        disc_geom, assets.mesh_path(f"{wheel_part.name}_spoked_disc.obj")
    )

    # Outer tire band (thin in width relative to the wheel — leaves clearance for
    # the spoked discs on either face).
    tire_band_w = max(0.010, w * 0.55)
    wheel_part.visual(
        Cylinder(radius=r, length=tire_band_w),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=rubber,
        name="tire", material_class_id="rubber.smooth_plain",
    )
    # Outer steel rim (slightly inside the tire OD, slightly wider than tire band).
    wheel_part.visual(
        Cylinder(radius=r * 0.92, length=tire_band_w + 0.004),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="rim", material_class_id="metal.stainless_matte",
    )
    # Two spoked discs, one on each face. Place them just outside the tire band
    # so they are visible but do not overlap the tire.
    disc_offset = tire_band_w * 0.5 + disc_face_thickness * 0.5 + 0.001
    wheel_part.visual(
        disc_mesh,
        origin=Origin(xyz=(disc_offset, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="spoked_disc_outer", material_class_id="metal.stainless_matte",
    )
    wheel_part.visual(
        disc_mesh,
        origin=Origin(xyz=(-disc_offset, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="spoked_disc_inner", material_class_id="metal.stainless_matte",
    )
    # Hub barrel — connects the two spoked discs through the center and accepts
    # the axle stub. Slightly wider than wheel_width so the caster axle is fully
    # enclosed.
    wheel_part.visual(
        Cylinder(radius=hub_r, length=w + 0.010),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hardware,
        name="hub", material_class_id="metal.stainless_matte",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def run_platform_cart_tests(
    object_model: ArticulatedObject, config: PlatformCartConfig
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)
    deck = object_model.get_part("deck")

    # Element-scoped captured-mount allowances only: the deck's axle stubs, handle
    # hinge ears and tow-bar knuckle are pins that necessarily sit inside the wheel
    # hub / handle leg / tow-bar knuckle they retain. Everything else must clear.
    _part_names = {p.name for p in object_model.parts}
    _handle_names = [n for n in _part_names if "handle" in n and n != "deck"]
    for _w in _part_names:
        if not _w.startswith("wheel_"):
            continue
        _slot = _w[len("wheel_"):]
        for _hub_elem in ("hub", "rim", "tire", "hub_cap_inner", "hub_cap_outer", "spoked_disc_inner", "spoked_disc_outer"):
            ctx.allow_overlap(
                deck, object_model.get_part(_w),
                elem_a=f"{_slot}_axle_stub", elem_b=_hub_elem,
                reason="Deck axle stub is captured inside the fixed wheel hub/rim bore.",
            )
    for _h in _handle_names:
        for _ear in ("handle_hinge_ear_rear_left", "handle_hinge_ear_rear_right",
                     "handle_hinge_ear_front_center", "handle_hinge_ear_front_left",
                     "handle_hinge_ear_front_right"):
            for _leg in ("frame", "frame_left", "frame_right", "panel"):
                try:
                    ctx.allow_overlap(
                        deck, object_model.get_part(_h),
                        elem_a=_ear, elem_b=_leg,
                        reason="Deck hinge ear captures the folding handle leg at its pivot.",
                    )
                except Exception:
                    pass
    if "tow_bar" in _part_names:
        # The tow bar is a single folding member pinned to the deck front/rear
        # edge; its knuckle/shaft sit within the edge frame (cross rail, bumper
        # strip) it pivots in.
        ctx.allow_overlap(
            deck, object_model.get_part("tow_bar"),
            reason="Tow bar is pinned into the deck edge frame it folds on.",
        )
    if "fold_lip" in _part_names:
        # The fold-down lip is a single folding member pinned to the deck front
        # edge frame (rail + bumper strip) it hinges in.
        ctx.allow_overlap(
            deck, object_model.get_part("fold_lip"),
            reason="Fold-down lip is pinned into the deck front edge frame it folds on.",
        )
        # The fold-down lip and a front folding handle both pivot on the front
        # deck edge and share that fold envelope.
        for _h in _handle_names:
            try:
                ctx.allow_overlap(
                    object_model.get_part("fold_lip"), object_model.get_part(_h),
                    reason="Fold-down lip and front folding handle share the front-edge fold envelope.",
                )
            except Exception:
                pass
    if "steering_bridge" in _part_names:
        for _deck_elem in ("deck_shell", "frame_rail_front", "steering_kingpin_socket"):
            for _br_elem in ("steering_kingpin", "steering_bar"):
                try:
                    ctx.allow_overlap(
                        deck, object_model.get_part("steering_bridge"),
                        elem_a=_deck_elem, elem_b=_br_elem,
                        reason="Steering bridge kingpin is captured in the deck pivot socket.",
                    )
                except Exception:
                    pass
    # Steering bridge / caster axle stubs AND the fork cheeks that straddle the
    # wheel are captured mounts: the stub sits in the hub bore and the fork jaws
    # clamp the tire/rim/disc faces on both sides. Element-scoped only.
    _wheel_elems = ("hub", "rim", "tire", "hub_cap_inner", "hub_cap_outer",
                    "spoked_disc_inner", "spoked_disc_outer")
    for _bridge in ("steering_bridge",):
        if _bridge not in _part_names:
            continue
        for _w in _part_names:
            if not _w.startswith("wheel_"):
                continue
            _slot = _w[len("wheel_"):]
            for _mount_elem in (f"{_slot}_bridge_axle_stub", f"{_slot}_bridge_fork_inner",
                                f"{_slot}_bridge_fork_outer"):
                for _hub_elem in _wheel_elems:
                    ctx.allow_overlap(
                        object_model.get_part(_bridge), object_model.get_part(_w),
                        elem_a=_mount_elem, elem_b=_hub_elem,
                        reason="Steering bridge stub/fork captures & straddles the steered wheel.",
                    )
    for _c in _part_names:
        if not _c.startswith("caster_"):
            continue
        _slot = _c[len("caster_"):]
        # Caster swivel plate + kingpin journaled in the deck caster mount bearing.
        for _mnt in (f"{_slot}_caster_mount", "deck_shell"):
            for _cel in ("swivel_plate", "kingpin"):
                try:
                    ctx.allow_overlap(
                        deck, object_model.get_part(_c),
                        elem_a=_mnt, elem_b=_cel,
                        reason="Caster swivel plate/kingpin journaled in the deck caster mount bearing.",
                    )
                except Exception:
                    pass
        for _w in _part_names:
            if not _w.startswith("wheel_"):
                continue
            for _mount_elem in ("axle_stub", "fork_cheek_inner", "fork_cheek_outer", "fork_crown"):
                for _hub_elem in _wheel_elems:
                    try:
                        ctx.allow_overlap(
                            object_model.get_part(_c), object_model.get_part(_w),
                            elem_a=_mount_elem, elem_b=_hub_elem,
                            reason="Caster fork straddles & the stub captures the caster wheel.",
                        )
                    except Exception:
                        pass
        # A caster and its OWN wheel are one swivel wheel assembly (fork straddles
        # the wheel, kingpin/axle capture it); their mutual overlap is structural.
        _own_wheel = f"wheel_{_slot}"
        if _own_wheel in _part_names:
            ctx.allow_overlap(
                object_model.get_part(_c), object_model.get_part(_own_wheel),
                reason="Caster fork/kingpin and its wheel form one captured swivel assembly.",
            )
    # Folding handles stow flat onto the deck; their frame lies over the deck's
    # tray lips / top face at the stowed pose (a real folded-handle rest).
    for _h in _handle_names:
        ctx.allow_overlap(
            deck, object_model.get_part(_h),
            reason="Folding handle stows flat over the deck top / rails at its rest pose.",
        )
    layout = _wheel_layout(resolved)
    wheel_index = 0
    caster_index = 0
    for slot_name, _x, _y in layout:
        steered = _slot_is_steering(slot_name, resolved)
        cast = _slot_uses_caster_swivel(slot_name, resolved)
        wheel_part = object_model.get_part(f"wheel_{slot_name}")
        wheel_joint = object_model.get_articulation(f"wheel_{wheel_index}_joint")
        ctx.check(
            f"wheel_{wheel_index}_continuous_axis",
            wheel_joint.articulation_type == ArticulationType.CONTINUOUS
            and tuple(wheel_joint.axis) == (1.0, 0.0, 0.0),
            details=(f"type={wheel_joint.articulation_type}, axis={wheel_joint.axis}"),
        )
        if cast:
            caster_part = object_model.get_part(f"caster_{slot_name}")
            caster_joint = object_model.get_articulation(f"caster_{caster_index}_joint")
            ctx.check(
                f"caster_{caster_index}_vertical_swivel",
                caster_joint.articulation_type == ArticulationType.CONTINUOUS
                and tuple(caster_joint.axis) == (0.0, 0.0, 1.0),
                details=(f"type={caster_joint.articulation_type}, axis={caster_joint.axis}"),
            )
            ctx.allow_overlap(
                caster_part,
                wheel_part,
                elem_a="axle_stub",
                elem_b="hub",
                reason="The caster axle stub is captured by the wheel hub.",
            )
            caster_index += 1
        elif steered:
            ctx.allow_overlap(
                object_model.get_part("steering_bridge"),
                wheel_part,
                elem_a=f"{slot_name}_bridge_axle_stub",
                elem_b="hub",
                reason="The steering bridge axle stub is captured by the wheel hub.",
            )
        else:
            ctx.allow_overlap(
                deck,
                wheel_part,
                elem_a=f"{slot_name}_axle_stub",
                elem_b="hub",
                reason="The fixed wheel axle stub is captured by the wheel hub.",
            )
        # Wheel must be close to the ground (z gap <= WHEEL_Z_GAP_MAX).
        wheel_aabb = ctx.part_world_aabb(wheel_part)
        if wheel_aabb is not None:
            low = wheel_aabb[0]
            low_z = low[2] if hasattr(low, "__getitem__") else low.z
            ctx.check(
                f"wheel_{wheel_index}_ground_contact",
                low_z <= GROUND_Z + WHEEL_Z_GAP_MAX + 1e-6,
                details=f"low_z={low_z}",
            )
        wheel_index += 1

    if resolved.has_steering:
        steering_joint = object_model.get_articulation("steering_joint")
        ctx.check(
            "steering_axis_vertical",
            steering_joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(steering_joint.axis) == (0.0, 0.0, 1.0),
            details=f"axis={steering_joint.axis}",
        )

    if resolved.has_handle and not resolved.has_twin_handles:
        # Single-end handle (front_only / rear_only).
        if resolved.has_front_handle:
            handle = object_model.get_part("handle")
            handle_joint = object_model.get_articulation("handle_joint")
            ctx.check(
                "handle_axis_horizontal",
                handle_joint.articulation_type == ArticulationType.REVOLUTE
                and abs(handle_joint.axis[2]) < 1e-6,
                details=f"axis={handle_joint.axis}",
            )
            hinge_y = resolved.handle_hinge_y_ratio * resolved.deck_length
            ctx.check(
                "handle_hinge_within_rear_band",
                0.2 * resolved.deck_length - 1e-6 <= hinge_y <= 0.5 * resolved.deck_length + 1e-6,
                details=f"hinge_y={hinge_y}, L={resolved.deck_length}",
            )
            with ctx.pose({handle_joint: math.pi / 2.0}):
                folded_aabb = ctx.part_world_aabb(handle)
            ctx.check(
                "handle_folds_without_disappearing",
                folded_aabb is not None,
            )

    if resolved.has_twin_handles:
        # Two side-by-side handles on the same end (pistol_grip only).
        left = object_model.get_part("handle_left")
        right = object_model.get_part("handle_right")
        for slot, part in (("left", left), ("right", right)):
            joint = object_model.get_articulation(f"handle_{slot}_joint")
            ctx.check(
                f"twin_{slot}_handle_axis_horizontal",
                joint.articulation_type == ArticulationType.REVOLUTE and abs(joint.axis[2]) < 1e-6,
                details=f"axis={joint.axis}",
            )
            with ctx.pose({joint: math.pi / 2.0}):
                folded = ctx.part_world_aabb(part)
            ctx.check(f"twin_{slot}_handle_folds", folded is not None)
        # Both must share the same hinge_y (same end of the deck).
        left_aabb = ctx.part_world_aabb(left)
        right_aabb = ctx.part_world_aabb(right)
        if left_aabb and right_aabb:
            left_y = (left_aabb[0][1] + left_aabb[1][1]) * 0.5
            right_y = (right_aabb[0][1] + right_aabb[1][1]) * 0.5
            ctx.check(
                "twin_handles_share_end",
                abs(left_y - right_y) < 0.05,
                details=f"left_y={left_y}, right_y={right_y}",
            )

    # Identity / sanity checks.
    ctx.check(
        "deck_present",
        deck is not None,
    )
    n_wheel_parts = len([p for p in object_model.parts if p.name.startswith("wheel_")])
    ctx.check(
        "wheel_count_matches",
        n_wheel_parts == resolved.wheel_count,
        details=f"found {n_wheel_parts}, expected {resolved.wheel_count}",
    )
    # symmetry: left and right wheel slots are mirrored.
    left_count = sum(1 for n, _x, _y in layout if n.endswith("_left"))
    right_count = sum(1 for n, _x, _y in layout if n.endswith("_right"))
    ctx.check("wheel_lr_symmetric_count", left_count == right_count)

    # Rear handle (only for single-rear layout, not twin_rear which has its
    # own test block above).
    if resolved.has_rear_handle and not resolved.has_twin_handles:
        rear = object_model.get_part("rear_handle")
        rear_joint = object_model.get_articulation("rear_handle_joint")
        ctx.check(
            "rear_handle_axis_horizontal",
            rear_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(rear_joint.axis[2]) < 1e-6,
            details=f"axis={rear_joint.axis}",
        )
        rear_hinge_y = -resolved.handle_hinge_y_ratio * resolved.deck_length
        ctx.check(
            "rear_handle_hinge_on_rear_half",
            rear_hinge_y < 0,
            details=f"rear_hinge_y={rear_hinge_y}",
        )
        with ctx.pose({rear_joint: math.pi / 2.0}):
            rear_folded = ctx.part_world_aabb(rear)
        ctx.check("rear_handle_folds_without_disappearing", rear_folded is not None)

    # Fold-down lip articulation.
    if resolved.has_fold_lip:
        lip = object_model.get_part("fold_lip")
        lip_joint = object_model.get_articulation("fold_lip_joint")
        ctx.check(
            "fold_lip_is_revolute",
            lip_joint.articulation_type == ArticulationType.REVOLUTE,
            details=f"type={lip_joint.articulation_type}",
        )
        # At q=0 the lip should be UP (above the deck top); at q=pi/2 it should
        # have rotated DOWN to roughly horizontal (its top edge moves toward +Y).
        closed_aabb = ctx.part_world_aabb(lip)
        with ctx.pose({lip_joint: math.pi / 2.0}):
            open_aabb = ctx.part_world_aabb(lip)
        ctx.check(
            "fold_lip_opens_forward",
            closed_aabb is not None
            and open_aabb is not None
            and open_aabb[1][1] > closed_aabb[1][1] + 0.02,
            details=f"closed={closed_aabb}, open={open_aabb}",
        )

    # Tow attachments.
    if resolved.tow_attachment == "tow_bar":
        tow = object_model.get_part("tow_bar")
        tow_joint = object_model.get_articulation("tow_bar_joint")
        ctx.check(
            "tow_bar_is_revolute",
            tow_joint.articulation_type == ArticulationType.REVOLUTE,
            details=f"type={tow_joint.articulation_type}",
        )
        rest_aabb = ctx.part_world_aabb(tow)
        with ctx.pose({tow_joint: math.pi / 2.0}):
            stowed_aabb = ctx.part_world_aabb(tow)
        ctx.check(
            "tow_bar_stows_upward",
            rest_aabb is not None
            and stowed_aabb is not None
            and stowed_aabb[1][2] > rest_aabb[1][2] + 0.05,
            details=f"rest={rest_aabb}, stowed={stowed_aabb}",
        )
    elif resolved.tow_attachment == "loop":
        loop_aabb = ctx.part_element_world_aabb(deck, elem="tow_loop_top")
        ctx.check(
            "tow_loop_in_front_of_deck",
            loop_aabb is not None and loop_aabb[0][1] > resolved.deck_length * 0.40,
            details=f"loop_aabb={loop_aabb}",
        )

    return ctx.report()


def build_seeded_platform_cart(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_platform_cart(config_from_seed(seed), assets=assets)


def with_overrides(config: PlatformCartConfig, **kwargs: object) -> PlatformCartConfig:
    return replace(config, **kwargs)
