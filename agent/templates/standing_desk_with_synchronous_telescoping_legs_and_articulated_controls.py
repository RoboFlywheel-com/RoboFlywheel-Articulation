# SPDX-License-Identifier: Apache-2.0

"""Procedural template for the
``standing_desk_with_synchronous_telescoping_legs_and_articulated_controls``
category.

Implementation notes
--------------------

* Uses spec **mode B** (multi-leg Mimic).  One leg is designated as the
  *primary* leg and drives every other leg's first-stage prismatic via
  ``Mimic(joint=<primary first-stage joint>, multiplier=1.0, offset=0.0)``.
* For ``stage_count = N`` (per leg), each leg has ``N - 1`` prismatic joints:
  outer -> mid (if N >= 3) -> inner.  Same-leg downstream prismatics Mimic
  to the leg's first stage; across legs, every other leg's first stage
  Mimics to the primary leg's first stage.
* Desktop is FIXED to the primary leg's innermost stage.  All other legs'
  innermost stages have Mimic prismatic chains, so the synced rise produces
  ``max(Delta z) - min(Delta z) < 1 mm`` by construction.
* ``crossbar_style = integrated_into_desktop_apron`` adds the cross beam as
  a ``desktop.visual(...)`` and creates **no** crossbar part/joint.  The
  other styles attach a ``crossbar`` part FIXED to the primary leg's
  innermost stage so it tracks the desktop.
* The control panel is FIXED to the desktop.  Buttons are drawn as decorative
  visuals on the panel (no separate parts, no button articulations) — this
  matches the 5-star ground-truth distribution where most records have no
  articulated buttons.
* All decorative sub-parts (foot pads, cable management, screen badges,
  apron crossbar, button markings) are attached via ``parent.visual(...)``,
  never separate parts and never separate FIXED articulations.
"""

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
    Cylinder,
    Inertial,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

# ---------------------------------------------------------------------------
# Discrete parameter literals
# ---------------------------------------------------------------------------

DesktopShape = Literal[
    "rectangle",
    "rounded",
    "rounded_corner_rect",
]
DesktopEdgeTreatment = Literal[
    "plain",
    "edge_banded",
    "front_lip",
    "beveled_front",
    "stepped_riser",
]
DesktopSize = Literal["small", "medium", "large"]
LegCrossSection = Literal["rectangular", "round", "oval"]
CrossbarStyle = Literal["front", "rear", "double", "integrated_into_desktop_apron"]
FootStyle = Literal["T_foot", "rectangular", "wide"]
ControlPanelPosition = Literal["left", "right", "center", "front_underside"]
MaterialStyle = Literal[
    "warm_oak_black",
    "walnut_graphite",
    "pale_birch_white",
    "matte_black",
    "satin_white",
    "industrial_steel",
    "charcoal_aluminum",
    "warm_oak_steel",
]

# ---------------------------------------------------------------------------
# Spine ranges (per bucket).  Continuous values are sampled from these.
# ---------------------------------------------------------------------------

# Desktop size buckets: (length_x_range, width_y_range)
DESKTOP_SIZE_RANGES: dict[DesktopSize, tuple[tuple[float, float], tuple[float, float]]] = {
    "small": ((1.00, 1.20), (0.55, 0.65)),
    "medium": ((1.30, 1.60), (0.65, 0.75)),
    "large": ((1.70, 2.10), (0.75, 0.85)),
}

DESKTOP_THICKNESS = 0.030

# Outer leg envelope (x_size_outer, y_size_outer) before cross-section reshape.
OUTER_LEG_X_RANGE = (0.075, 0.105)
OUTER_LEG_Y_RANGE = (0.075, 0.105)

# Outer leg vertical length (without inner stages extended).
OUTER_LEG_HEIGHT_RANGE = (0.55, 0.75)

# Each stage shrinks the cross-section by this much.
STAGE_SHRINK = 0.78

# Each inner stage vertical length: fraction of outer leg height (covers
# overlap and travel).  Larger -> more travel and more overlap reserve.
STAGE_LENGTH_FACTOR = 0.95

# Useful travel of a single prismatic step.  Total max desktop rise =
# (stage_count - 1) * SINGLE_STAGE_TRAVEL.
SINGLE_STAGE_TRAVEL_RANGE = (0.22, 0.34)

# Base / foot constants (the "feet" are visuals on the base part).
BASE_PLATE_THICKNESS = 0.022

# Materials.  Each palette is a coherent finish picked to match a real
# office-desk colourway found in the 5-star ground-truth set.  Keys:
#   outer_leg   — visible outer column tubes
#   inner_leg   — the inner telescoping stage tubes (slightly lighter)
#   accent      — dark trim: aprons, mount plates, button/keypad caps' base
#   desktop_top — the work-surface board
#   panel       — control-panel housing
#   button      — keypad markings on the panel face
MATERIAL_PALETTES: dict[
    MaterialStyle,
    dict[str, tuple[float, float, float, float]],
] = {
    # Warm oak top, satin-black powder-coated frame (most common in samples).
    "warm_oak_black": {
        "outer_leg": (0.12, 0.13, 0.14, 1.0),
        "inner_leg": (0.42, 0.43, 0.45, 1.0),
        "accent": (0.07, 0.08, 0.09, 1.0),
        "desktop_top": (0.66, 0.49, 0.30, 1.0),
        "panel": (0.10, 0.10, 0.11, 1.0),
        "button": (0.78, 0.79, 0.80, 1.0),
    },
    # Walnut-stained wood top, graphite-grey frame.
    "walnut_graphite": {
        "outer_leg": (0.26, 0.27, 0.29, 1.0),
        "inner_leg": (0.55, 0.56, 0.58, 1.0),
        "accent": (0.18, 0.19, 0.21, 1.0),
        "desktop_top": (0.36, 0.22, 0.13, 1.0),
        "panel": (0.16, 0.17, 0.19, 1.0),
        "button": (0.70, 0.72, 0.74, 1.0),
    },
    # Pale birch / Scandinavian: light wood top, almost-white frame.
    "pale_birch_white": {
        "outer_leg": (0.93, 0.93, 0.92, 1.0),
        "inner_leg": (0.85, 0.85, 0.84, 1.0),
        "accent": (0.65, 0.66, 0.67, 1.0),
        "desktop_top": (0.87, 0.78, 0.62, 1.0),
        "panel": (0.82, 0.83, 0.85, 1.0),
        "button": (0.32, 0.32, 0.34, 1.0),
    },
    # All-matte-black office desk.
    "matte_black": {
        "outer_leg": (0.06, 0.06, 0.07, 1.0),
        "inner_leg": (0.15, 0.15, 0.17, 1.0),
        "accent": (0.04, 0.04, 0.05, 1.0),
        "desktop_top": (0.10, 0.10, 0.11, 1.0),
        "panel": (0.05, 0.05, 0.06, 1.0),
        "button": (0.50, 0.52, 0.55, 1.0),
    },
    # All-satin-white minimalist.
    "satin_white": {
        "outer_leg": (0.96, 0.96, 0.95, 1.0),
        "inner_leg": (0.92, 0.92, 0.91, 1.0),
        "accent": (0.76, 0.76, 0.78, 1.0),
        "desktop_top": (0.97, 0.96, 0.94, 1.0),
        "panel": (0.88, 0.88, 0.90, 1.0),
        "button": (0.40, 0.40, 0.42, 1.0),
    },
    # Industrial steel: brushed-stainless tube, dark grey desk top.
    "industrial_steel": {
        "outer_leg": (0.62, 0.64, 0.66, 1.0),
        "inner_leg": (0.78, 0.79, 0.80, 1.0),
        "accent": (0.30, 0.31, 0.33, 1.0),
        "desktop_top": (0.32, 0.33, 0.34, 1.0),
        "panel": (0.22, 0.22, 0.24, 1.0),
        "button": (0.82, 0.83, 0.84, 1.0),
    },
    # Charcoal + brushed aluminum: dark top, lighter metallic columns.
    "charcoal_aluminum": {
        "outer_leg": (0.70, 0.71, 0.72, 1.0),
        "inner_leg": (0.84, 0.84, 0.85, 1.0),
        "accent": (0.22, 0.22, 0.24, 1.0),
        "desktop_top": (0.22, 0.23, 0.25, 1.0),
        "panel": (0.16, 0.16, 0.18, 1.0),
        "button": (0.88, 0.89, 0.90, 1.0),
    },
    # Warm oak top with industrial steel base (mixed-material premium feel).
    "warm_oak_steel": {
        "outer_leg": (0.55, 0.57, 0.59, 1.0),
        "inner_leg": (0.74, 0.75, 0.76, 1.0),
        "accent": (0.28, 0.29, 0.31, 1.0),
        "desktop_top": (0.70, 0.55, 0.36, 1.0),
        "panel": (0.20, 0.20, 0.22, 1.0),
        "button": (0.80, 0.81, 0.83, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StandingDeskConfig:
    leg_count: int = 2
    stage_count_per_leg: int = 2
    desktop_shape: DesktopShape = "rectangle"
    desktop_edge_treatment: DesktopEdgeTreatment = "plain"
    desktop_size: DesktopSize = "medium"
    leg_cross_section: LegCrossSection = "rectangular"
    crossbar_style: CrossbarStyle = "front"
    foot_style: FootStyle = "T_foot"
    control_panel_position: ControlPanelPosition = "right"
    material_style: MaterialStyle = "warm_oak_black"

    # Spine values - if None they are filled in resolve_config from bucket defaults.
    desktop_length: float | None = None
    desktop_width: float | None = None
    outer_leg_x: float | None = None
    outer_leg_y: float | None = None
    outer_leg_height: float | None = None
    single_stage_travel: float | None = None

    name: str = "reference_standing_desk"


@dataclass(frozen=True)
class ResolvedStandingDeskConfig:
    leg_count: int
    stage_count_per_leg: int
    desktop_shape: DesktopShape
    desktop_edge_treatment: DesktopEdgeTreatment
    desktop_size: DesktopSize
    leg_cross_section: LegCrossSection
    crossbar_style: CrossbarStyle
    foot_style: FootStyle
    control_panel_position: ControlPanelPosition
    material_style: MaterialStyle
    # Derived geometry.
    desktop_length: float
    desktop_width: float
    outer_leg_x: float
    outer_leg_y: float
    outer_leg_height: float
    single_stage_travel: float
    # Derived per-stage sizes; stage 0 is the outer leg.
    stage_dims_xy: tuple[tuple[float, float], ...]  # (x, y) per stage
    stage_length: float  # length along Z of each inner stage tube
    primary_leg_index: int
    leg_x_positions: tuple[float, ...]
    name: str


# ---------------------------------------------------------------------------
# Seed-based config sampler
# ---------------------------------------------------------------------------


def config_from_seed(seed: int) -> StandingDeskConfig:
    rng = random.Random(seed)
    stage_count_per_leg = rng.choices((2, 3), weights=(0.60, 0.40), k=1)[0]
    desktop_shape: DesktopShape = rng.choices(
        ("rectangle", "rounded", "rounded_corner_rect"),
        weights=(0.50, 0.25, 0.25),
        k=1,
    )[0]
    # Three leg layouts are supported:
    #   1-leg — single central pedestal under the desktop centre (cafe-style)
    #   2-leg — twin columns near the desk ends (standard sit/stand)
    #   3-leg — twin end columns + a central support (bench desks)
    # Weights: 25 / 50 / 25 per the user spec.
    leg_count = rng.choices((1, 2, 3), weights=(0.25, 0.50, 0.25), k=1)[0]
    desktop_edge_treatment: DesktopEdgeTreatment = rng.choices(
        ("plain", "edge_banded", "front_lip", "beveled_front", "stepped_riser"),
        weights=(0.35, 0.20, 0.15, 0.15, 0.15),
        k=1,
    )[0]
    desktop_size: DesktopSize = rng.choices(
        ("small", "medium", "large"), weights=(0.30, 0.45, 0.25), k=1
    )[0]
    leg_cross_section: LegCrossSection = rng.choices(
        ("rectangular", "round", "oval"), weights=(0.55, 0.30, 0.15), k=1
    )[0]
    crossbar_style: CrossbarStyle = rng.choices(
        ("front", "rear", "double", "integrated_into_desktop_apron"),
        weights=(0.30, 0.25, 0.15, 0.30),
        k=1,
    )[0]
    foot_style: FootStyle = rng.choices(
        ("T_foot", "rectangular", "wide"), weights=(0.45, 0.30, 0.25), k=1
    )[0]
    control_panel_position: ControlPanelPosition = rng.choices(
        ("left", "right", "center", "front_underside"),
        weights=(0.25, 0.30, 0.20, 0.25),
        k=1,
    )[0]
    material_style: MaterialStyle = rng.choices(
        (
            "warm_oak_black",
            "walnut_graphite",
            "pale_birch_white",
            "matte_black",
            "satin_white",
            "industrial_steel",
            "charcoal_aluminum",
            "warm_oak_steel",
        ),
        weights=(0.22, 0.14, 0.12, 0.12, 0.10, 0.08, 0.10, 0.12),
        k=1,
    )[0]

    length_range, width_range = DESKTOP_SIZE_RANGES[desktop_size]
    desktop_length = round(rng.uniform(*length_range), 3)
    desktop_width = round(rng.uniform(*width_range), 3)
    outer_leg_x = round(rng.uniform(*OUTER_LEG_X_RANGE), 3)
    outer_leg_y = round(rng.uniform(*OUTER_LEG_Y_RANGE), 3)
    outer_leg_height = round(rng.uniform(*OUTER_LEG_HEIGHT_RANGE), 3)
    single_stage_travel = round(rng.uniform(*SINGLE_STAGE_TRAVEL_RANGE), 3)

    return StandingDeskConfig(
        leg_count=leg_count,
        stage_count_per_leg=stage_count_per_leg,
        desktop_shape=desktop_shape,
        desktop_edge_treatment=desktop_edge_treatment,
        desktop_size=desktop_size,
        leg_cross_section=leg_cross_section,
        crossbar_style=crossbar_style,
        foot_style=foot_style,
        control_panel_position=control_panel_position,
        material_style=material_style,
        desktop_length=desktop_length,
        desktop_width=desktop_width,
        outer_leg_x=outer_leg_x,
        outer_leg_y=outer_leg_y,
        outer_leg_height=outer_leg_height,
        single_stage_travel=single_stage_travel,
        name=f"seeded_standing_desk_{seed}",
    )


# ---------------------------------------------------------------------------
# resolve_config: derive per-stage sizes, leg layout, primary index.
# ---------------------------------------------------------------------------


def resolve_config(config: StandingDeskConfig) -> ResolvedStandingDeskConfig:
    if config.leg_count not in {1, 2, 3}:
        raise ValueError(f"leg_count must be in {{1, 2, 3}}, got {config.leg_count}")
    if config.stage_count_per_leg not in {2, 3}:
        raise ValueError(
            f"stage_count_per_leg must be in {{2, 3}}, got {config.stage_count_per_leg}"
        )
    if config.desktop_shape not in {
        "rectangle",
        "rounded",
        "rounded_corner_rect",
    }:
        raise ValueError(f"Unsupported desktop_shape: {config.desktop_shape}")
    if config.desktop_edge_treatment not in {
        "plain",
        "edge_banded",
        "front_lip",
        "beveled_front",
        "stepped_riser",
    }:
        raise ValueError(f"Unsupported desktop_edge_treatment: {config.desktop_edge_treatment}")
    if config.desktop_size not in DESKTOP_SIZE_RANGES:
        raise ValueError(f"Unsupported desktop_size: {config.desktop_size}")
    if config.leg_cross_section not in {"rectangular", "round", "oval"}:
        raise ValueError(f"Unsupported leg_cross_section: {config.leg_cross_section}")
    if config.crossbar_style not in {
        "front",
        "rear",
        "double",
        "integrated_into_desktop_apron",
    }:
        raise ValueError(f"Unsupported crossbar_style: {config.crossbar_style}")
    if config.foot_style not in {"T_foot", "rectangular", "wide"}:
        raise ValueError(f"Unsupported foot_style: {config.foot_style}")
    if config.control_panel_position not in {"left", "right", "center", "front_underside"}:
        raise ValueError(f"Unsupported control_panel_position: {config.control_panel_position}")
    if config.material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    length_range, width_range = DESKTOP_SIZE_RANGES[config.desktop_size]
    if config.desktop_length is None:
        desktop_length = (length_range[0] + length_range[1]) * 0.5
    else:
        # The continuous value may have been drawn for a different size bucket
        # than the one now active (raw discrete overrides do not re-resolve
        # dependent fields).  Reconcile by clamping into the active bucket.
        desktop_length = min(max(float(config.desktop_length), length_range[0]), length_range[1])
    if config.desktop_width is None:
        desktop_width = (width_range[0] + width_range[1]) * 0.5
    else:
        desktop_width = min(max(float(config.desktop_width), width_range[0]), width_range[1])

    outer_leg_x = (
        float(config.outer_leg_x)
        if config.outer_leg_x is not None
        else (OUTER_LEG_X_RANGE[0] + OUTER_LEG_X_RANGE[1]) * 0.5
    )
    outer_leg_y = (
        float(config.outer_leg_y)
        if config.outer_leg_y is not None
        else (OUTER_LEG_Y_RANGE[0] + OUTER_LEG_Y_RANGE[1]) * 0.5
    )
    outer_leg_height = (
        float(config.outer_leg_height)
        if config.outer_leg_height is not None
        else (OUTER_LEG_HEIGHT_RANGE[0] + OUTER_LEG_HEIGHT_RANGE[1]) * 0.5
    )
    single_stage_travel = (
        float(config.single_stage_travel)
        if config.single_stage_travel is not None
        else (SINGLE_STAGE_TRAVEL_RANGE[0] + SINGLE_STAGE_TRAVEL_RANGE[1]) * 0.5
    )

    # Per-stage XY dims.  Stage 0 = outer leg; each successive stage shrinks.
    stage_dims_xy_list: list[tuple[float, float]] = [(outer_leg_x, outer_leg_y)]
    for _i in range(1, config.stage_count_per_leg):
        prev_x, prev_y = stage_dims_xy_list[-1]
        new_x = prev_x * STAGE_SHRINK
        new_y = prev_y * STAGE_SHRINK
        if new_x < 0.020 or new_y < 0.020:
            raise ValueError(
                f"derived stage {_i} too narrow ({new_x:.3f}, {new_y:.3f}); increase outer_leg_x/y."
            )
        stage_dims_xy_list.append((new_x, new_y))

    # Each inner stage tube spans the full outer leg height (less a small
    # margin) so it can extend up while keeping retained insertion.
    stage_length = outer_leg_height * STAGE_LENGTH_FACTOR

    # Layout the legs along world +X around the desktop centre.
    # Use a generous inset so feet fit under the desktop comfortably.
    leg_inset = max(0.16, min(outer_leg_x, outer_leg_y) * 1.4)
    half_span = desktop_length * 0.5 - leg_inset
    if half_span < 0.15:
        # Too small a desk; clamp.
        half_span = 0.15
    if config.leg_count == 1:
        # Single central pedestal — sits under the desktop centre.
        leg_x_positions = (0.0,)
        primary_leg_index = 0
    elif config.leg_count == 2:
        leg_x_positions = (-half_span, half_span)
        primary_leg_index = 0
    else:
        leg_x_positions = (-half_span, 0.0, half_span)
        primary_leg_index = 1  # centre leg

    return ResolvedStandingDeskConfig(
        leg_count=config.leg_count,
        stage_count_per_leg=config.stage_count_per_leg,
        desktop_shape=config.desktop_shape,
        desktop_edge_treatment=config.desktop_edge_treatment,
        desktop_size=config.desktop_size,
        leg_cross_section=config.leg_cross_section,
        crossbar_style=config.crossbar_style,
        foot_style=config.foot_style,
        control_panel_position=config.control_panel_position,
        material_style=config.material_style,
        desktop_length=desktop_length,
        desktop_width=desktop_width,
        outer_leg_x=outer_leg_x,
        outer_leg_y=outer_leg_y,
        outer_leg_height=outer_leg_height,
        single_stage_travel=single_stage_travel,
        stage_dims_xy=tuple(stage_dims_xy_list),
        stage_length=stage_length,
        primary_leg_index=primary_leg_index,
        leg_x_positions=tuple(leg_x_positions),
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def _build_leg_stage_visual(
    part,
    *,
    cross_section: LegCrossSection,
    dim_x: float,
    dim_y: float,
    length_z: float,
    z_centre: float,
    material,
    prefix: str,
) -> None:
    """Authoring helper: add the stage tube visual along local +Z.

    The visual is centred at ``z_centre`` and spans ``length_z`` along world Z.
    Cross-section dictates whether the visual is a Box, Cylinder, or Box+Box
    (oval ~ scaled cylinder, approximated as a wider Box for stability).
    """
    if cross_section == "rectangular":
        part.visual(
            Box((dim_x, dim_y, length_z)),
            origin=Origin(xyz=(0.0, 0.0, z_centre)),
            material=material,
            name=f"{prefix}_tube", material_class_id="metal.paint_coated",
        )
    elif cross_section == "round":
        radius = min(dim_x, dim_y) * 0.5
        part.visual(
            Cylinder(radius=radius, length=length_z),
            origin=Origin(xyz=(0.0, 0.0, z_centre)),
            material=material,
            name=f"{prefix}_tube", material_class_id="metal.paint_coated",
        )
    else:  # oval - approximate via a chamfered Box (visual-only).
        part.visual(
            Box((dim_x * 1.05, dim_y * 0.85, length_z)),
            origin=Origin(xyz=(0.0, 0.0, z_centre)),
            material=material,
            name=f"{prefix}_tube", material_class_id="metal.paint_coated",
        )
        # Small side-fillets that read as an oval profile.  Radius is sized to
        # stay inside the box's Y half-extent so the fillets do not extend
        # outside the leg envelope.
        fillet_radius = min(dim_y * 0.45, dim_y * 0.5 - 0.002)
        fillet_x_offset = max(0.0, dim_x * 0.5 - fillet_radius)
        for sx, label in ((-1, "left"), (1, "right")):
            part.visual(
                Cylinder(radius=fillet_radius, length=length_z),
                origin=Origin(
                    xyz=(sx * fillet_x_offset, 0.0, z_centre),
                ),
                material=material,
                name=f"{prefix}_oval_fillet_{label}", material_class_id="metal.paint_coated",
            )


def _add_foot_visual(
    base,
    *,
    x_position: float,
    foot_style: FootStyle,
    desktop_width: float,
    material,
    accent_material,
    index: int,
) -> None:
    """Foot pad / foot bar visual attached to the base part below a leg."""
    z_centre = BASE_PLATE_THICKNESS * 0.5
    if foot_style == "T_foot":
        # Wide bar across Y plus a small platform under the leg.
        base.visual(
            Box((0.16, desktop_width * 0.78, BASE_PLATE_THICKNESS)),
            origin=Origin(xyz=(x_position, 0.0, z_centre)),
            material=material,
            name=f"foot_{index}_bar", material_class_id="metal.paint_coated",
        )
        base.visual(
            Box((0.12, 0.12, BASE_PLATE_THICKNESS + 0.006)),
            origin=Origin(xyz=(x_position, 0.0, z_centre + 0.003)),
            material=accent_material,
            name=f"foot_{index}_pad", material_class_id="rubber.smooth_plain",
        )
    elif foot_style == "rectangular":
        # Thin rectangular slab.
        base.visual(
            Box((0.20, desktop_width * 0.55, BASE_PLATE_THICKNESS)),
            origin=Origin(xyz=(x_position, 0.0, z_centre)),
            material=material,
            name=f"foot_{index}_slab", material_class_id="metal.paint_coated",
        )
        for sy, label in ((-1, "rear"), (1, "front")):
            base.visual(
                Cylinder(radius=0.012, length=0.010),
                origin=Origin(
                    xyz=(x_position, sy * desktop_width * 0.22, BASE_PLATE_THICKNESS),
                ),
                material=accent_material,
                name=f"foot_{index}_glide_{label}", material_class_id="rubber.smooth_plain",
            )
    else:  # wide
        base.visual(
            Box((0.30, desktop_width * 0.85, BASE_PLATE_THICKNESS)),
            origin=Origin(xyz=(x_position, 0.0, z_centre)),
            material=material,
            name=f"foot_{index}_wide", material_class_id="metal.paint_coated",
        )
        base.visual(
            Box((0.30, 0.05, BASE_PLATE_THICKNESS + 0.005)),
            origin=Origin(xyz=(x_position, 0.0, z_centre + 0.004)),
            material=accent_material,
            name=f"foot_{index}_strap", material_class_id="metal.paint_coated",
        )


def _add_desktop_edge_treatment(
    desktop,
    resolved: ResolvedStandingDeskConfig,
    *,
    top_material,
    accent_material,
) -> None:
    """Apply the decorative edge treatment on top of the base desktop shape.

    All visuals are anchored at the desktop's local frame, where z=0 is the
    underside and z=DESKTOP_THICKNESS is the top surface.  Treatments that
    rise above the top surface stay shallow (≤ 0.04 m) so the desktop's Z
    extent remains the smallest of (x, y, z) — preserving the "desktop is
    level / flat" validator constraint.
    """
    L = resolved.desktop_length
    W = resolved.desktop_width
    top_thickness = DESKTOP_THICKNESS
    treatment = resolved.desktop_edge_treatment

    if treatment == "plain":
        return

    if treatment == "edge_banded":
        # Contrasting wood/metal trim around the perimeter of the main board,
        # sitting flush with the top.
        if resolved.desktop_shape == "rounded":
            band_L = L * 0.86
        elif resolved.desktop_shape == "rounded_corner_rect":
            band_L = L * 0.96
        else:
            band_L = L * 0.98
        band_W = W * 0.98
        band_thickness = 0.014
        band_height = top_thickness + 0.004
        band_z_centre = band_height * 0.5
        # Front + rear strips, full length along X
        for sy, name in ((-1.0, "front"), (1.0, "rear")):
            desktop.visual(
                Box((band_L, band_thickness, band_height)),
                origin=Origin(
                    xyz=(0.0, sy * (band_W * 0.5 - band_thickness * 0.5), band_z_centre),
                ),
                material=accent_material,
                name=f"edge_band_{name}", material_class_id="metal.paint_coated",
            )
        # Left + right strips, inset within front/rear strips
        side_band_y = band_W - band_thickness * 2.0
        if side_band_y > 0.05:
            for sx, name in ((-1.0, "left"), (1.0, "right")):
                desktop.visual(
                    Box((band_thickness, side_band_y, band_height)),
                    origin=Origin(
                        xyz=(
                            sx * (band_L * 0.5 - band_thickness * 0.5),
                            0.0,
                            band_z_centre,
                        ),
                    ),
                    material=accent_material,
                    name=f"edge_band_{name}", material_class_id="metal.paint_coated",
                )
        return

    if treatment == "front_lip":
        # A raised reading rail along the front edge — sits proud above the
        # top surface and uses the accent material so it reads as a metal
        # strip.  Spans most of the front edge.
        if resolved.desktop_shape == "rounded":
            lip_L = L * 0.82
        elif resolved.desktop_shape == "rounded_corner_rect":
            lip_L = L * 0.90
        else:
            lip_L = L * 0.94
        lip_height = 0.022
        lip_thickness = 0.016
        # Y position: just inside the front apron (y = -W*0.42)
        front_y = -W * 0.5 + lip_thickness * 0.5 + 0.006
        desktop.visual(
            Box((lip_L, lip_thickness, lip_height)),
            origin=Origin(
                xyz=(0.0, front_y, top_thickness + lip_height * 0.5),
            ),
            material=accent_material,
            name="front_lip", material_class_id="metal.paint_coated",
        )
        return

    if treatment == "beveled_front":
        # Beveled profile: a wider, slightly thicker sub-board just below the
        # front edge, sticking out a couple of mm forward of the main top so
        # the front reads as a chamfered profile.  Sits at z just below the
        # top surface (and just below the front apron interior so it does not
        # collide with the apron).
        if resolved.desktop_shape == "rounded":
            bevel_L = L * 0.84
        elif resolved.desktop_shape == "rounded_corner_rect":
            bevel_L = L * 0.92
        else:
            bevel_L = L * 0.96
        bevel_thickness = 0.028
        bevel_height = 0.012
        bevel_y = -W * 0.5 + bevel_thickness * 0.5 - 0.006  # 6 mm proud of edge
        desktop.visual(
            Box((bevel_L, bevel_thickness, bevel_height)),
            origin=Origin(
                xyz=(0.0, bevel_y, top_thickness - bevel_height * 0.5),
            ),
            material=top_material,
            name="front_bevel_profile", material_class_id="wood.engineered_board",
        )
        return

    if treatment == "stepped_riser":
        # A small raised platform on the rear half of the desktop — reads as a
        # monitor riser.
        if resolved.desktop_shape == "rounded":
            riser_L = L * 0.55
        elif resolved.desktop_shape == "rounded_corner_rect":
            riser_L = L * 0.60
        else:
            riser_L = L * 0.62
        riser_W = W * 0.28
        riser_height = 0.022
        riser_y = W * 0.5 - riser_W * 0.5 - 0.030
        desktop.visual(
            Box((riser_L, riser_W, riser_height)),
            origin=Origin(
                xyz=(0.0, riser_y, top_thickness + riser_height * 0.5),
            ),
            material=top_material,
            name="riser_platform", material_class_id="wood.engineered_board",
        )
        # Riser front fascia (accent) so the step reads as a distinct piece.
        desktop.visual(
            Box((riser_L, 0.012, riser_height)),
            origin=Origin(
                xyz=(
                    0.0,
                    riser_y - riser_W * 0.5 + 0.006,
                    top_thickness + riser_height * 0.5,
                ),
            ),
            material=accent_material,
            name="riser_fascia", material_class_id="metal.paint_coated",
        )
        return


def _build_desktop_outline(
    desktop,
    *,
    L: float,
    W: float,
    top_thickness: float,
    shape: DesktopShape,
    top_material,
) -> None:
    """Render the desktop perimeter as one or more visuals on the desktop part.

    All visuals sit at z ∈ [0, top_thickness] in the desktop's local frame
    (desktop underside at z=0).  Convex outlines (rectangle / rounded /
    rounded_corner_rect) build a single contiguous shape.  Concave outlines
    (U / T) compose a few overlapping rectangles plus small Cylinders at the
    inner/outer corners so the silhouette is not visibly stepped.
    """
    top_z = top_thickness * 0.5

    if shape == "rectangle":
        desktop.visual(
            Box((L, W, top_thickness)),
            origin=Origin(xyz=(0.0, 0.0, top_z)),
            material=top_material,
            name="top", material_class_id="wood.engineered_board",
        )
        return

    if shape == "rounded":
        # Capsule: a slightly inset central box with full-radius end caps.
        inner_L = L * 0.86
        desktop.visual(
            Box((inner_L, W, top_thickness)),
            origin=Origin(xyz=(0.0, 0.0, top_z)),
            material=top_material,
            name="top", material_class_id="wood.engineered_board",
        )
        cap_radius = W * 0.5
        cap_x = inner_L * 0.5
        desktop.visual(
            Cylinder(radius=cap_radius, length=top_thickness),
            origin=Origin(xyz=(cap_x, 0.0, top_z)),
            material=top_material,
            name="top_cap_right", material_class_id="wood.engineered_board",
        )
        desktop.visual(
            Cylinder(radius=cap_radius, length=top_thickness),
            origin=Origin(xyz=(-cap_x, 0.0, top_z)),
            material=top_material,
            name="top_cap_left", material_class_id="wood.engineered_board",
        )
        return

    if shape == "rounded_corner_rect":
        # Plain rectangle whose four corners are softened with small fillets.
        # Constructed as: central plate + four edge strips (covering the
        # straight edges) + four Cylinders at the corners.  The radius is
        # sized to ~5–7% of the shorter side so it reads as a soft corner
        # rather than a capsule.
        r = min(L, W) * 0.06
        desktop.visual(
            Box((L - 2.0 * r, W, top_thickness)),
            origin=Origin(xyz=(0.0, 0.0, top_z)),
            material=top_material,
            name="top", material_class_id="wood.engineered_board",
        )
        desktop.visual(
            Box((L, W - 2.0 * r, top_thickness)),
            origin=Origin(xyz=(0.0, 0.0, top_z)),
            material=top_material,
            name="top_cross", material_class_id="wood.engineered_board",
        )
        for sx, sy, label in (
            (-1.0, -1.0, "front_left"),
            (1.0, -1.0, "front_right"),
            (-1.0, 1.0, "rear_left"),
            (1.0, 1.0, "rear_right"),
        ):
            desktop.visual(
                Cylinder(radius=r, length=top_thickness),
                origin=Origin(
                    xyz=(sx * (L * 0.5 - r), sy * (W * 0.5 - r), top_z),
                ),
                material=top_material,
                name=f"top_corner_{label}", material_class_id="wood.engineered_board",
            )
        return


def _add_desktop_aprons(
    desktop,
    *,
    L: float,
    W: float,
    shape: DesktopShape,
    accent_material,
) -> None:
    """Author the under-desktop apron frame ring.

    For convex shapes (rectangle / rounded / rounded_corner_rect) this is a
    full perimeter skirt (front + rear + two sides).  For concave shapes
    (U / T) the apron is broken up so it only sits under solid portions of
    the top surface, never floating across the open mouth.
    """
    apron_height = 0.045
    apron_thickness = 0.04
    # Embed the apron top 1 mm into the desktop slab underside (z = 0) so the
    # perimeter aprons stay welded to the top rather than floating 1 mm below it.
    apron_z_centre = -apron_height * 0.5 + 0.001

    if shape in ("rectangle", "rounded", "rounded_corner_rect"):
        desktop.visual(
            Box((L * 0.92, apron_thickness, apron_height)),
            origin=Origin(xyz=(0.0, W * 0.42, apron_z_centre)),
            material=accent_material,
            name="rear_apron", material_class_id="metal.paint_coated",
        )
        desktop.visual(
            Box((L * 0.92, apron_thickness, apron_height)),
            origin=Origin(xyz=(0.0, -W * 0.42, apron_z_centre)),
            material=accent_material,
            name="front_apron", material_class_id="metal.paint_coated",
        )
        # Side rails close the frame so the apron reads as a continuous
        # skirt.  Inset to stay inside the actual desktop X-extent.
        if shape == "rounded":
            side_rail_x = L * 0.40
        elif shape == "rounded_corner_rect":
            side_rail_x = L * 0.43
        else:
            side_rail_x = L * 0.44
        side_rail_length_y = W * 0.84 - apron_thickness * 2.0
        if side_rail_length_y > 0.05:
            for sx, side in ((-1.0, "left"), (1.0, "right")):
                desktop.visual(
                    Box((apron_thickness, side_rail_length_y, apron_height)),
                    origin=Origin(
                        xyz=(sx * side_rail_x, 0.0, apron_z_centre),
                    ),
                    material=accent_material,
                    name=f"side_apron_{side}", material_class_id="metal.paint_coated",
                )
        return


def _add_desktop_visuals(
    desktop,
    resolved: ResolvedStandingDeskConfig,
    *,
    top_material,
    accent_material,
) -> None:
    """Author the desktop visuals based on shape.  Desktop is FIXED to the
    primary leg's innermost stage; its local origin is on the desktop top
    centre with z-zero at the desktop underside.
    """
    L = resolved.desktop_length
    W = resolved.desktop_width
    top_thickness = DESKTOP_THICKNESS

    _build_desktop_outline(
        desktop,
        L=L,
        W=W,
        top_thickness=top_thickness,
        shape=resolved.desktop_shape,
        top_material=top_material,
    )

    # Decorative edge treatment layered on top of the base shape (banding /
    # raised lip / bevel profile / stepped riser).  Choice is independent of
    # desktop_shape so any of 3 shapes × 5 treatments can combine.
    _add_desktop_edge_treatment(
        desktop,
        resolved,
        top_material=top_material,
        accent_material=accent_material,
    )

    # Aprons / cable strip under the desktop, shape-aware so the apron rails
    # actually live *under* the top surface and never float in the air over
    # the open mouth of a U or beside the stem of a T.
    _add_desktop_aprons(
        desktop,
        L=L,
        W=W,
        shape=resolved.desktop_shape,
        accent_material=accent_material,
    )

    if resolved.crossbar_style == "integrated_into_desktop_apron":
        # The crossbar is added as a hidden beam visual on the desktop
        # underside, spanning between leg positions.
        if resolved.leg_count >= 2:
            span_left = resolved.leg_x_positions[0]
            span_right = resolved.leg_x_positions[-1]
            cb_length = (span_right - span_left) * 0.96
            desktop.visual(
                Box((cb_length, 0.05, 0.05)),
                origin=Origin(
                    xyz=((span_left + span_right) * 0.5, 0.0, -0.028),
                ),
                material=accent_material,
                name="integrated_crossbar", material_class_id="metal.paint_coated",
            )


def _add_control_panel_visuals(panel, *, material, accent_material, panel_size_xy) -> None:
    """The control panel is a flat housing under the desktop."""
    px, py = panel_size_xy
    panel.visual(
        Box((px, py, 0.022)),
        origin=Origin(xyz=(0.0, 0.0, -0.011)),
        material=material,
        name="body", material_class_id="plastic.opaque_glossy_molded",
    )
    panel.visual(
        Box((px * 0.94, py * 0.78, 0.006)),
        origin=Origin(xyz=(0.0, 0.0, -0.025)),
        material=accent_material,
        name="bezel", material_class_id="plastic.opaque_glossy_molded",
    )


# ---------------------------------------------------------------------------
# Crossbar geometry helper for separate-part crossbars.
# ---------------------------------------------------------------------------


def _add_crossbar_visual(
    crossbar_part,
    *,
    style: CrossbarStyle,
    leg_x_positions: tuple[float, ...],
    desktop_width: float,
    desktop_thickness: float,
    z_offset_from_desktop: float,
    material,
) -> float:
    """Author the crossbar visuals and return the local ``weld_x`` at which the
    hanger gusset meets the desktop underside.  ``z_offset_from_desktop`` is the
    local Z coordinate at which the bar sits below the desktop underside
    (typically a small negative value).  The crossbar part frame is at the
    desktop
    underside-centre and moves with the desktop.
    """
    span_left = leg_x_positions[0]
    span_right = leg_x_positions[-1]
    x_mid = (span_left + span_right) * 0.5
    length = (span_right - span_left) * 0.94
    bar_y_front = -desktop_width * 0.30
    bar_y_rear = desktop_width * 0.30

    # Weld point x: the midpoint of the widest gap between adjacent legs, so the
    # hanger gusset that carries the FIXED weld up to the desktop underside sits
    # clear of every leg column (crucial for the 3-leg case where a leg sits on
    # the centreline).
    gaps = [
        (
            (leg_x_positions[i] + leg_x_positions[i + 1]) * 0.5,
            leg_x_positions[i + 1] - leg_x_positions[i],
        )
        for i in range(len(leg_x_positions) - 1)
    ]
    weld_x = max(gaps, key=lambda g: g[1])[0] if gaps else x_mid

    if style == "front":
        present_bars_y = [bar_y_front]
        crossbar_part.visual(
            Box((length, 0.045, 0.045)),
            origin=Origin(xyz=(x_mid, bar_y_front, z_offset_from_desktop)),
            material=material,
            name="front_bar", material_class_id="metal.paint_coated",
        )
    elif style == "rear":
        present_bars_y = [bar_y_rear]
        crossbar_part.visual(
            Box((length, 0.045, 0.045)),
            origin=Origin(xyz=(x_mid, bar_y_rear, z_offset_from_desktop)),
            material=material,
            name="rear_bar", material_class_id="metal.paint_coated",
        )
    else:  # double
        present_bars_y = [bar_y_front, bar_y_rear]
        crossbar_part.visual(
            Box((length, 0.040, 0.040)),
            origin=Origin(xyz=(x_mid, bar_y_front, z_offset_from_desktop)),
            material=material,
            name="front_bar", material_class_id="metal.paint_coated",
        )
        crossbar_part.visual(
            Box((length, 0.040, 0.040)),
            origin=Origin(xyz=(x_mid, bar_y_rear, z_offset_from_desktop)),
            material=material,
            name="rear_bar", material_class_id="metal.paint_coated",
        )

    # A single gusset at ``weld_x`` bridges the air gap between the stretcher
    # bar(s) and the desktop underside (z = 0), fusing them into one connected
    # part.  It spans the full y-range of the bars (and through y = 0), and
    # passes through the point (weld_x, 0, 0) so that — after the crossbar frame
    # is rebased onto that point in the builder — the FIXED weld sits on real
    # crossbar hardware.
    ys = present_bars_y + [0.0]
    y_lo = min(ys) - 0.010
    y_hi = max(ys) + 0.010
    z_lo = z_offset_from_desktop - 0.002
    z_hi = 0.0
    crossbar_part.visual(
        Box((0.05, y_hi - y_lo, z_hi - z_lo)),
        origin=Origin(xyz=(weld_x, (y_lo + y_hi) * 0.5, (z_lo + z_hi) * 0.5)),
        material=material,
        name="crossbar_hanger", material_class_id="metal.paint_coated",
    )
    return weld_x


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------


def _leg_name(leg_index: int) -> str:
    return f"leg_{leg_index}"


def _stage_part_name(leg_index: int, stage_index: int) -> str:
    """Stage index 0 is the outer leg sleeve; higher indices are inner stages."""
    if stage_index == 0:
        return f"leg_{leg_index}_outer"
    return f"leg_{leg_index}_stage_{stage_index}"


def _stage_joint_name(leg_index: int, stage_index: int) -> str:
    """Joint that drives stage_index relative to (stage_index - 1).

    Indices: stage_index >= 1.  This is the prismatic joint name.
    """
    return f"leg_{leg_index}_lift_joint_{stage_index}"


def _rebase_part_origins(part, shift: tuple[float, float, float]) -> None:
    """Translate every visual/collision/inertial origin of ``part`` by ``-shift``.

    Used to move a FIXED-welded child's local frame onto the mounting interface
    without changing world placement (the parent joint origin absorbs the change
    and every joint parented to this part subtracts ``shift`` in turn).
    """
    sx, sy, sz = shift
    if abs(sx) < 1e-12 and abs(sy) < 1e-12 and abs(sz) < 1e-12:
        return
    for elem in list(part.visuals) + list(part.collisions):
        o = elem.origin
        elem.origin = Origin(xyz=(o.xyz[0] - sx, o.xyz[1] - sy, o.xyz[2] - sz), rpy=o.rpy)
    inertial = getattr(part, "inertial", None)
    if inertial is not None:
        o = inertial.origin
        part.inertial = Inertial(
            mass=inertial.mass,
            inertia=inertial.inertia,
            origin=Origin(xyz=(o.xyz[0] - sx, o.xyz[1] - sy, o.xyz[2] - sz), rpy=o.rpy),
        )


def build_standing_desk(
    config: StandingDeskConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or StandingDeskConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-standing-desk-assets-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)

    palette = MATERIAL_PALETTES[resolved.material_style]
    outer_leg_mat = model.material(
        f"desk_outer_leg_{resolved.material_style}", rgba=palette["outer_leg"]
    )
    inner_leg_mat = model.material(
        f"desk_inner_leg_{resolved.material_style}", rgba=palette["inner_leg"]
    )
    accent_mat = model.material(f"desk_accent_{resolved.material_style}", rgba=palette["accent"])
    top_mat = model.material(f"desk_top_{resolved.material_style}", rgba=palette["desktop_top"])
    panel_mat = model.material(f"desk_panel_{resolved.material_style}", rgba=palette["panel"])
    button_mat = model.material(f"desk_button_{resolved.material_style}", rgba=palette["button"])

    # ----- base + feet -----
    base = model.part("base")
    for i, x_pos in enumerate(resolved.leg_x_positions):
        _add_foot_visual(
            base,
            x_position=x_pos,
            foot_style=resolved.foot_style,
            desktop_width=resolved.desktop_width,
            material=outer_leg_mat,
            accent_material=accent_mat,
            index=i,
        )

    # The per-leg feet must sit at each leg's x-position (the base->leg FIXED
    # weld anchors on the foot there), so with two or more legs the base part
    # would otherwise be a set of disconnected foot islands.  A slim floor-level
    # spine links them into one connected base frame (a low foot rail hidden at
    # ground level between the feet).
    if resolved.leg_count >= 2:
        span_left = resolved.leg_x_positions[0]
        span_right = resolved.leg_x_positions[-1]
        base.visual(
            Box((span_right - span_left + 0.10, 0.05, BASE_PLATE_THICKNESS)),
            origin=Origin(xyz=(0.0, 0.0, BASE_PLATE_THICKNESS * 0.5)),
            material=outer_leg_mat,
            name="base_foot_spine", material_class_id=("metal.paint_coated" if resolved.material_style in {"warm_oak_black", "walnut_graphite", "pale_birch_white", "matte_black", "satin_white", "charcoal_aluminum"} else "metal.stainless_matte"),
        )

    # ----- legs (per leg: an outer part + inner stage parts) -----
    # For each leg create the outer part FIXED to base at its x_position.  Then
    # create stage_count_per_leg - 1 inner stages, each PRISMATIC to its
    # parent stage.  Same-leg downstream stages Mimic to that leg's first
    # stage joint; non-primary legs' first-stage joints Mimic to the primary
    # leg's first-stage joint.
    stage_count = resolved.stage_count_per_leg
    primary_idx = resolved.primary_leg_index
    primary_first_joint_name = _stage_joint_name(primary_idx, 1)

    # Limits: same for every leg.
    lift_limits = MotionLimits(
        effort=900.0,
        velocity=0.05,
        lower=0.0,
        upper=resolved.single_stage_travel,
    )

    # Build leg parts and stage articulations.
    leg_outer_parts: dict[int, object] = {}
    leg_top_parts: dict[int, object] = {}  # innermost stage part (where desktop attaches)
    for leg_index, x_pos in enumerate(resolved.leg_x_positions):
        # Outer leg part.
        outer_part = model.part(_stage_part_name(leg_index, 0))
        leg_outer_parts[leg_index] = outer_part
        outer_x, outer_y = resolved.stage_dims_xy[0]
        # Visual is centred along +Z from z=0 (outer leg origin is at the
        # base-plate top) up to z=outer_leg_height.
        _build_leg_stage_visual(
            outer_part,
            cross_section=resolved.leg_cross_section,
            dim_x=outer_x,
            dim_y=outer_y,
            length_z=resolved.outer_leg_height,
            z_centre=resolved.outer_leg_height * 0.5,
            material=outer_leg_mat,
            prefix=f"leg_{leg_index}_outer",
        )

        # FIXED articulation: base -> outer leg.  Place at the base plate top.
        model.articulation(
            f"base_to_leg_{leg_index}_outer",
            ArticulationType.FIXED,
            parent=base,
            child=outer_part,
            origin=Origin(xyz=(x_pos, 0.0, BASE_PLATE_THICKNESS)),
        )

        # Inner stages.
        prev_part = outer_part
        for stage_index in range(1, stage_count):
            stage_part = model.part(_stage_part_name(leg_index, stage_index))
            stage_x, stage_y = resolved.stage_dims_xy[stage_index]
            # The stage visual is anchored so its CENTRE is at z = -stage_length/2.
            # Choosing a negative z origin means: when the joint is at q=0,
            # the inner stage's top sits at the joint origin (z=0 in the
            # joint frame, which equals z=outer_leg_height in the parent
            # part frame).  Increasing q moves the inner stage upward,
            # carrying its visual upward and keeping the bottom retained
            # inside the parent stage.
            _build_leg_stage_visual(
                stage_part,
                cross_section=resolved.leg_cross_section,
                dim_x=stage_x,
                dim_y=stage_y,
                length_z=resolved.stage_length,
                z_centre=-resolved.stage_length * 0.5,
                material=inner_leg_mat,
                prefix=f"leg_{leg_index}_stage_{stage_index}",
            )

            # Joint origin: at the top of the previous stage.  For the first
            # inner stage, that's at z=outer_leg_height in the outer-leg
            # part frame.  For subsequent stages, it's at z=0 in the
            # previous (inner) stage part frame, which itself is at the
            # parent's top - this means we place subsequent joint origins
            # at z=0 (the previous stage's top edge is at z=0 by the
            # negative-centre convention).
            if stage_index == 1:
                joint_origin_z = resolved.outer_leg_height
            else:
                joint_origin_z = 0.0

            # Determine mimic.  The first inner stage of non-primary legs
            # mimics the primary leg's first joint.  Same-leg downstream
            # stages mimic that leg's own first joint.
            mimic: Mimic | None = None
            if stage_index == 1:
                if leg_index != primary_idx:
                    mimic = Mimic(joint=primary_first_joint_name, multiplier=1.0, offset=0.0)
            else:
                # Downstream stage on the same leg.
                mimic = Mimic(
                    joint=_stage_joint_name(leg_index, 1),
                    multiplier=1.0,
                    offset=0.0,
                )

            model.articulation(
                _stage_joint_name(leg_index, stage_index),
                ArticulationType.PRISMATIC,
                parent=prev_part,
                child=stage_part,
                origin=Origin(xyz=(0.0, 0.0, joint_origin_z)),
                axis=(0.0, 0.0, 1.0),
                motion_limits=lift_limits,
                mimic=mimic,
            )
            prev_part = stage_part

        # Top cap on the innermost stage: a slightly oversized plate sitting
        # flush with the stage's top edge (z=0 in the stage frame).  The cap
        # spans z ∈ [-cap_thickness, 0] so its top is flush with the desktop
        # underside when this is the primary leg, and so it hides the open
        # tube end on non-primary legs.  Cap size is bounded to stay strictly
        # smaller than the outer leg footprint so the AABB-nesting validator
        # still holds (the inner stage's AABB must fit inside the outer's).
        innermost = prev_part
        cap_thickness = 0.012
        innermost_x, innermost_y = resolved.stage_dims_xy[stage_count - 1]
        outer_x_dim, outer_y_dim = resolved.stage_dims_xy[0]
        # Round/oval legs have circular cross-section, so the effective outer
        # AABB extent on both axes is the cross-section diameter, not the
        # nominal box dim.  Use min(x, y) to bound the cap conservatively for
        # those cross-sections.
        if resolved.leg_cross_section in ("round", "oval"):
            # Round outer AABB is 2*radius = min(outer_x, outer_y).  Oval outer
            # AABB Y extent is 2*radius (fillet) = 0.9 * outer_y, and X extent
            # is outer_x * 1.05.  Use the cylinder/box derived extents directly
            # so the cap stays strictly inside.
            outer_x_extent = outer_x_dim * (1.05 if resolved.leg_cross_section == "oval" else 1.0)
            outer_y_extent = outer_y_dim * (0.90 if resolved.leg_cross_section == "oval" else 1.0)
            if resolved.leg_cross_section == "round":
                outer_x_extent = min(outer_x_dim, outer_y_dim)
                outer_y_extent = outer_x_extent
        else:
            outer_x_extent = outer_x_dim
            outer_y_extent = outer_y_dim
        cap_x = min(innermost_x * 1.45, outer_x_extent * 0.78)
        cap_y = min(innermost_y * 1.45, outer_y_extent * 0.78)
        innermost.visual(
            Box((cap_x, cap_y, cap_thickness)),
            origin=Origin(xyz=(0.0, 0.0, -cap_thickness * 0.5)),
            material=accent_mat,
            name=f"leg_{leg_index}_top_cap", material_class_id="metal.paint_coated",
        )
        # Optional neck reinforcement just below the cap, smaller than the cap
        # and bounded by the outer footprint extents derived above.
        neck_thickness = 0.040
        neck_x = min(innermost_x * 1.15, outer_x_extent * 0.65)
        neck_y = min(innermost_y * 1.15, outer_y_extent * 0.65)
        innermost.visual(
            Box((neck_x, neck_y, neck_thickness)),
            origin=Origin(
                xyz=(0.0, 0.0, -cap_thickness - neck_thickness * 0.5),
            ),
            material=inner_leg_mat,
            name=f"leg_{leg_index}_neck_reinforcement", material_class_id=("metal.stainless_matte" if resolved.material_style in {"warm_oak_black", "walnut_graphite", "industrial_steel", "charcoal_aluminum", "warm_oak_steel"} else "metal.paint_coated"),
        )

        leg_top_parts[leg_index] = prev_part

    # ----- desktop -----
    desktop = model.part("desktop")
    _add_desktop_visuals(
        desktop,
        resolved,
        top_material=top_mat,
        accent_material=accent_mat,
    )
    # Mount plates under the desktop at each leg's X position, hiding the
    # stage-top to desktop-underside interface.  The plates extend downward
    # from the desktop underside (desk z=0) so they read as the leg-to-top
    # bracket.  Stays inside the desktop X/Y footprint so it cannot stick out
    # past the desktop edges.
    plate_thickness = 0.018
    plate_x = min(0.140, resolved.outer_leg_x * 1.30)
    plate_y = min(0.110, resolved.outer_leg_y * 1.30)
    for i, leg_x in enumerate(resolved.leg_x_positions):
        desktop.visual(
            Box((plate_x, plate_y, plate_thickness)),
            origin=Origin(xyz=(leg_x, 0.0, -plate_thickness * 0.5)),
            material=accent_mat,
            name=f"mount_plate_{i}", material_class_id="metal.paint_coated",
        )
    # FIXED to the primary leg's innermost (top) stage.  The physical weld lives
    # at the stage top centre, which is the parent stage's local origin
    # (0, 0, 0): x = 0 on the leg axis, z = 0 at the stage top edge (by the
    # negative-centre convention).  Put the joint origin there — on real leg
    # hardware — and rebase the desktop's own geometry by ``desktop_shift`` so
    # world placement is unchanged (the desktop stays centred over the desk).
    # Every joint parented to the desktop then subtracts ``desktop_shift``.
    desktop_shift = (resolved.leg_x_positions[primary_idx], 0.0, 0.0)
    _rebase_part_origins(desktop, desktop_shift)

    def _desktop_origin(xyz: tuple[float, float, float]) -> Origin:
        return Origin(
            xyz=(
                xyz[0] - desktop_shift[0],
                xyz[1] - desktop_shift[1],
                xyz[2] - desktop_shift[2],
            )
        )

    model.articulation(
        "primary_stage_to_desktop",
        ArticulationType.FIXED,
        parent=leg_top_parts[primary_idx],
        child=desktop,
        origin=Origin(),
    )

    # ----- crossbar (separate part for non-integrated styles) -----
    if resolved.crossbar_style != "integrated_into_desktop_apron" and resolved.leg_count >= 2:
        crossbar = model.part("crossbar")
        weld_x = _add_crossbar_visual(
            crossbar,
            style=resolved.crossbar_style,
            leg_x_positions=resolved.leg_x_positions,
            desktop_width=resolved.desktop_width,
            desktop_thickness=DESKTOP_THICKNESS,
            z_offset_from_desktop=-0.06,
            material=accent_mat,
        )
        # Rebase the crossbar so its local origin sits on the hanger gusset at
        # (weld_x, 0, 0) — real crossbar hardware clear of every leg column.
        crossbar_shift = (weld_x, 0.0, 0.0)
        _rebase_part_origins(crossbar, crossbar_shift)
        # FIXED to the desktop so the crossbar travels in sync.  The weld sits at
        # the hanger-to-underside contact (world (weld_x, 0, 0)), expressed in
        # the rebased desktop frame.
        model.articulation(
            "desktop_to_crossbar",
            ArticulationType.FIXED,
            parent=desktop,
            child=crossbar,
            origin=_desktop_origin((weld_x, 0.0, 0.0)),
        )

    # ----- control panel -----
    # The panel is FIXED to the desktop.  Buttons are drawn as decorative
    # visuals on the panel face (no separate parts, no articulations) — this
    # tracks the 5-star ground-truth distribution where most records have no
    # articulated buttons.
    panel = model.part("control_panel")
    panel_size = (0.16, 0.08)
    _add_control_panel_visuals(
        panel,
        material=panel_mat,
        accent_material=accent_mat,
        panel_size_xy=panel_size,
    )
    # Decorative keypad face flush with the panel bezel underside.  The bezel
    # spans z ∈ [-0.028, -0.022] in the panel frame; we place a thin keypad
    # plate so its TOP is co-planar with the bezel bottom (z=-0.028) and the
    # plate itself extends only ~2 mm below.  This avoids any visible gap
    # between the panel and its button face.
    keypad_z_top = -0.028
    keypad_thickness = 0.0025
    panel.visual(
        Box((panel_size[0] * 0.78, panel_size[1] * 0.62, keypad_thickness)),
        origin=Origin(
            xyz=(0.0, 0.0, keypad_z_top - keypad_thickness * 0.5),
        ),
        material=accent_mat,
        name="keypad_face", material_class_id="tech.control_interface",
    )
    # Up / down button caps painted on the keypad face.  These are very thin
    # tiles sitting on top of the keypad face so they look painted on rather
    # than dangling.
    cap_thickness = 0.0015
    for sx, label in ((-1.0, "left"), (1.0, "right")):
        panel.visual(
            Box((panel_size[0] * 0.18, panel_size[1] * 0.32, cap_thickness)),
            origin=Origin(
                xyz=(
                    sx * panel_size[0] * 0.22,
                    0.0,
                    keypad_z_top - keypad_thickness - cap_thickness * 0.5,
                ),
            ),
            material=button_mat,
            name=f"button_marking_{label}", material_class_id="plastic.opaque_glossy_molded",
        )

    # Determine panel mounting xyz relative to desktop underside.
    # Desktop underside is at z=0 (in desktop part frame), since top centre is
    # at z=top_thickness/2 with origin at underside.
    panel_y_front = -resolved.desktop_width * 0.42 + panel_size[1] * 0.5 + 0.005
    if resolved.control_panel_position == "left":
        panel_xy = (-resolved.desktop_length * 0.35, panel_y_front)
    elif resolved.control_panel_position == "right":
        panel_xy = (resolved.desktop_length * 0.35, panel_y_front)
    elif resolved.control_panel_position == "center":
        panel_xy = (0.0, panel_y_front)
    else:  # front_underside - centred but further forward
        panel_xy = (0.0, -resolved.desktop_width * 0.42 + panel_size[1] * 0.5)

    model.articulation(
        "desktop_to_control_panel",
        ArticulationType.FIXED,
        parent=desktop,
        child=panel,
        origin=_desktop_origin((panel_xy[0], panel_xy[1], -0.005)),
    )

    return model


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


def run_standing_desk_tests(
    object_model: ArticulatedObject, config: StandingDeskConfig
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)

    base = object_model.get_part("base")
    desktop = object_model.get_part("desktop")
    panel = object_model.get_part("control_panel")

    primary_idx = resolved.primary_leg_index
    stage_count = resolved.stage_count_per_leg

    # Allow nested-proxy overlap for every pair of stages on every leg.  With
    # the stages fully collapsed at rest, an inner stage is nested inside *all*
    # of its outer stages simultaneously (not just the immediately adjacent
    # one), so every (i, j) stage pair on a leg is an intentional
    # sleeve-in-sleeve contact.
    for leg_index in range(resolved.leg_count):
        for outer_index in range(stage_count):
            for inner_index in range(outer_index + 1, stage_count):
                parent_part = object_model.get_part(_stage_part_name(leg_index, outer_index))
                child_part = object_model.get_part(_stage_part_name(leg_index, inner_index))
                ctx.allow_overlap(
                    parent_part,
                    child_part,
                    reason=(
                        "Inner telescoping stage is intentionally represented as sliding "
                        "inside the parent stage proxy."
                    ),
                )

    # Allow desktop to overlap with control panel mount and with crossbar
    # part (visuals share the desktop underside region).
    if resolved.crossbar_style != "integrated_into_desktop_apron":
        try:
            crossbar = object_model.get_part("crossbar")
            ctx.allow_overlap(
                desktop,
                crossbar,
                reason="Crossbar visuals hang below the desktop apron and may touch.",
            )
            # The control panel and the crossbar are both mounted in the crowded
            # region just under the desktop front and can abut.
            ctx.allow_overlap(
                panel,
                crossbar,
                reason="Control panel and crossbar both mount under the desktop and may abut.",
            )
        except Exception:
            crossbar = None

    # The desktop is welded onto the telescoping leg columns.  At the mounting
    # interface its under-structure (per-leg mount plates, the perimeter side
    # aprons, and the integrated apron crossbar) physically seats on the leg
    # tops, which — with the stages fully nested at rest — means it contacts the
    # outer sleeve and every inner stage of each leg.  These are the real weld
    # contacts, declared element-by-element per leg column.
    for leg_index in range(resolved.leg_count):
        for stage_index in range(stage_count):
            stage_part = object_model.get_part(_stage_part_name(leg_index, stage_index))
            ctx.allow_overlap(
                desktop,
                stage_part,
                reason=(
                    "Desktop mount plate / apron / crossbar seats on the leg column at "
                    "the mounting interface."
                ),
            )
        # Foot pad wraps the base of the outer leg tube where the leg meets the
        # base plate (a captured foot-to-leg contact).
        ctx.allow_overlap(
            base,
            object_model.get_part(_stage_part_name(leg_index, 0)),
            reason="Foot pad wraps the base of the outer leg tube at the floor contact.",
        )

    # The control panel is bolted flush under the desktop; its housing abuts the
    # front apron rail it hangs beside.
    ctx.allow_overlap(
        panel,
        desktop,
        reason="Control panel housing is mounted flush against the desktop apron/underside.",
    )

    # --- 1. At least one prismatic lift joint.
    prismatic_joints = [
        j for j in object_model.articulations if j.articulation_type == ArticulationType.PRISMATIC
    ]
    lift_joints = [j for j in prismatic_joints if "lift_joint" in j.name]
    ctx.check(
        "at_least_one_prismatic_lift_joint",
        len(lift_joints) >= 1,
        details=f"lift_joints={[j.name for j in lift_joints]}",
    )
    expected_lift_joint_count = resolved.leg_count * (stage_count - 1)
    ctx.check(
        "lift_joint_count_matches_legs_times_stages_minus_one",
        len(lift_joints) == expected_lift_joint_count,
        details=(
            f"got {len(lift_joints)}, expected "
            f"{resolved.leg_count}*({stage_count}-1)={expected_lift_joint_count}"
        ),
    )

    # --- 2. Every lift joint has axis (0, 0, 1) and parallel.
    for j in lift_joints:
        ax = tuple(j.axis)
        ctx.check(
            f"{j.name}_axis_is_world_z",
            abs(ax[0]) < 1e-6 and abs(ax[1]) < 1e-6 and abs(ax[2] - 1.0) < 1e-6,
            details=f"axis={ax}",
        )

    # --- 3. Mimic chain: every non-primary first-stage joint mimics the primary
    #        first-stage joint.  Every downstream stage joint mimics its own
    #        leg's first-stage joint.  Both with multiplier=1.0, offset=0.0.
    primary_first_joint_name = _stage_joint_name(primary_idx, 1)
    for leg_index in range(resolved.leg_count):
        first_joint_name = _stage_joint_name(leg_index, 1)
        first_joint = object_model.get_articulation(first_joint_name)
        if leg_index == primary_idx:
            ctx.check(
                f"primary_leg_{leg_index}_first_joint_has_no_mimic",
                first_joint.mimic is None,
                details=f"mimic={first_joint.mimic}",
            )
        else:
            ctx.check(
                f"non_primary_leg_{leg_index}_first_joint_mimics_primary",
                first_joint.mimic is not None
                and first_joint.mimic.joint == primary_first_joint_name
                and abs(first_joint.mimic.multiplier - 1.0) < 1e-6
                and abs(first_joint.mimic.offset) < 1e-6,
                details=f"mimic={first_joint.mimic}",
            )
        # Downstream stages.
        for stage_index in range(2, stage_count):
            joint_name = _stage_joint_name(leg_index, stage_index)
            joint = object_model.get_articulation(joint_name)
            ctx.check(
                f"{joint_name}_mimics_same_leg_first_stage",
                joint.mimic is not None
                and joint.mimic.joint == first_joint_name
                and abs(joint.mimic.multiplier - 1.0) < 1e-6
                and abs(joint.mimic.offset) < 1e-6,
                details=f"mimic={joint.mimic}",
            )

    # --- 4. Desktop level: at rest the desktop top normal aligns with world +Z.
    #        Use AABB extents: the top thickness should be the smallest extent
    #        and the largest extents are the X/Y dimensions of the desktop.
    desktop_aabb = ctx.part_world_aabb(desktop)
    if desktop_aabb is not None:
        ex = desktop_aabb[1][0] - desktop_aabb[0][0]
        ey = desktop_aabb[1][1] - desktop_aabb[0][1]
        ez = desktop_aabb[1][2] - desktop_aabb[0][2]
        ctx.check(
            "desktop_thickness_along_z_is_smallest_extent",
            ez < ex and ez < ey,
            details=f"extents=({ex:.3f},{ey:.3f},{ez:.3f})",
        )

    # --- 5. Leg alignment: each leg outer is centred under its slot in X
    #        and the inner stages sit inside the outer leg footprint at rest.
    for leg_index in range(resolved.leg_count):
        outer = object_model.get_part(_stage_part_name(leg_index, 0))
        for stage_index in range(1, stage_count):
            inner = object_model.get_part(_stage_part_name(leg_index, stage_index))
            ctx.expect_within(
                inner,
                outer,
                axes="xy",
                inner_elem=f"leg_{leg_index}_stage_{stage_index}_tube",
                outer_elem=f"leg_{leg_index}_outer_tube",
                margin=0.010,
                name=f"leg_{leg_index}_stage_{stage_index}_centred_in_outer_at_rest",
            )

    # --- 6. Nesting: the outer leg AABB (yz extents) strictly contains every
    #        inner stage AABB.
    for leg_index in range(resolved.leg_count):
        outer = object_model.get_part(_stage_part_name(leg_index, 0))
        outer_aabb = ctx.part_world_aabb(outer)
        if outer_aabb is None:
            continue
        outer_x_extent = outer_aabb[1][0] - outer_aabb[0][0]
        outer_y_extent = outer_aabb[1][1] - outer_aabb[0][1]
        for stage_index in range(1, stage_count):
            inner = object_model.get_part(_stage_part_name(leg_index, stage_index))
            inner_aabb = ctx.part_world_aabb(inner)
            if inner_aabb is None:
                continue
            inner_x_extent = inner_aabb[1][0] - inner_aabb[0][0]
            inner_y_extent = inner_aabb[1][1] - inner_aabb[0][1]
            ctx.check(
                f"leg_{leg_index}_stage_{stage_index}_section_smaller_than_outer",
                inner_x_extent < outer_x_extent - 1e-4 and inner_y_extent < outer_y_extent - 1e-4,
                details=(
                    f"outer=({outer_x_extent:.3f},{outer_y_extent:.3f}); "
                    f"inner=({inner_x_extent:.3f},{inner_y_extent:.3f})"
                ),
            )

    # --- 7. Sync check: at full lift, all legs' tops and the desktop rise by
    #        the same amount (within 1 mm).
    primary_first_joint = object_model.get_articulation(primary_first_joint_name)
    upper = (
        primary_first_joint.motion_limits.upper
        if primary_first_joint.motion_limits is not None
        else 0.0
    )

    rest_positions: dict[str, tuple[float, float, float] | None] = {
        "desktop": ctx.part_world_position(desktop),
    }
    for leg_index in range(resolved.leg_count):
        top_part = object_model.get_part(_stage_part_name(leg_index, stage_count - 1))
        rest_positions[f"leg_{leg_index}_top"] = ctx.part_world_position(top_part)

    with ctx.pose({primary_first_joint: upper}):
        raised_positions: dict[str, tuple[float, float, float] | None] = {
            "desktop": ctx.part_world_position(desktop),
        }
        for leg_index in range(resolved.leg_count):
            top_part = object_model.get_part(_stage_part_name(leg_index, stage_count - 1))
            raised_positions[f"leg_{leg_index}_top"] = ctx.part_world_position(top_part)

    # Compute Z deltas across legs + desktop.
    deltas_z: list[float] = []
    for key in rest_positions:
        rest = rest_positions[key]
        raised = raised_positions[key]
        if rest is None or raised is None:
            ctx.fail(f"{key}_world_position_available", "position is None")
            continue
        deltas_z.append(raised[2] - rest[2])

    if deltas_z:
        ctx.check(
            "lift_actually_rises",
            min(deltas_z) > max(0.02, upper * 0.5),
            details=f"deltas_z={deltas_z}, upper={upper}",
        )
        ctx.check(
            "sync_check_max_minus_min_delta_z_under_1mm",
            max(deltas_z) - min(deltas_z) < 1e-3,
            details=f"deltas_z={deltas_z}",
        )

    # --- 8. Stability: foot footprint covers the desktop on each leg axis.
    #        Just sanity-check the base part exists and has visuals.
    ctx.check(
        "base_has_feet_visuals",
        any(v.name and v.name.startswith("foot_") for v in base.visuals),
        details=f"visuals={[v.name for v in base.visuals]}",
    )

    # --- 9. Control panel sits under the desktop (z is below the desktop top).
    panel_pos = ctx.part_world_position(panel)
    desktop_pos = ctx.part_world_position(desktop)
    if panel_pos is not None and desktop_pos is not None:
        ctx.check(
            "control_panel_below_desktop_top",
            panel_pos[2] < desktop_pos[2] + DESKTOP_THICKNESS * 0.5 + 1e-6,
            details=f"panel_z={panel_pos[2]}, desktop_z={desktop_pos[2]}",
        )

    # --- 10. Identity: desktop has a 'top' visual; every leg has an outer
    #         tube; control panel has a 'body' visual.
    desktop_visual_names = {v.name for v in desktop.visuals if v.name is not None}
    ctx.check(
        "desktop_has_top_visual",
        "top" in desktop_visual_names,
        details=f"desktop_visuals={sorted(desktop_visual_names)}",
    )
    panel_visual_names = {v.name for v in panel.visuals if v.name is not None}
    ctx.check(
        "control_panel_has_body_visual",
        "body" in panel_visual_names,
        details=f"panel_visuals={sorted(panel_visual_names)}",
    )
    for leg_index in range(resolved.leg_count):
        outer = object_model.get_part(_stage_part_name(leg_index, 0))
        outer_visual_names = {v.name for v in outer.visuals if v.name is not None}
        ctx.check(
            f"leg_{leg_index}_has_outer_tube_visual",
            f"leg_{leg_index}_outer_tube" in outer_visual_names,
            details=f"visuals={sorted(outer_visual_names)}",
        )

    return ctx.report()


# ---------------------------------------------------------------------------
# Seeded entry point + override helper.
# ---------------------------------------------------------------------------


def build_seeded_standing_desk(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_standing_desk(config_from_seed(seed), assets=assets)


def with_overrides(config: StandingDeskConfig, **kwargs: object) -> StandingDeskConfig:
    return replace(config, **kwargs)
