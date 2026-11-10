# SPDX-License-Identifier: Apache-2.0

"""Procedural template for the ``simple_aframe_step_ladder`` category.

World convention used throughout this template:

* Ladder width direction is the world Y axis (left/right rails sit at +/-Y).
* Front/back depth is the world X axis (front frame tilts toward +X feet,
  rear frame tilts toward -X feet).
* Vertical is the world Z axis; the ground plane is ``z = 0``.

The fold joint is therefore a revolute joint with ``axis = (0, 1, 0)`` (Y).
This is non-negotiable: the spec rejects fold axes along the world X axis.

Spine: ``ladder_height_class`` (Literal low / medium / tall) plus a per-class
continuous ``top_rail_z`` range.  ``step_count`` is derived from the class in
``resolve_config`` (NOT a Config field).
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
    TestContext,
    TestReport,
)

# ---------------------------------------------------------------------------
# Discrete parameter literals
# ---------------------------------------------------------------------------

LadderHeightClass = Literal["low", "medium", "tall"]
StepStyle = Literal["flat", "narrow_rung", "anti_slip"]
RailCrossSection = Literal["rectangular", "round"]
RearSupportStyle = Literal["simple"]
TopCapStyle = Literal["narrow_cap", "tool_tray", "flat"]
SpreaderType = Literal["none", "side_bar", "folding_link"]
FootStyle = Literal["rubber_pads", "wide_pads"]
MaterialStyle = Literal["aluminum", "fiberglass", "steel"]

# ---------------------------------------------------------------------------
# Bucket-class continuous ranges for the spine ``top_rail_z``.
# ---------------------------------------------------------------------------

TOP_RAIL_Z_RANGES: dict[LadderHeightClass, tuple[float, float]] = {
    "low": (0.55, 0.95),
    "medium": (0.95, 1.45),
    "tall": (1.45, 2.10),
}

# Per-class allowed step counts.  ``step_count`` is derived from the class.
STEP_COUNT_CHOICES: dict[LadderHeightClass, tuple[int, ...]] = {
    "low": (2, 3),
    "medium": (3, 4, 5),
    "tall": (5, 6, 7),
}

# Material colour palette for the structural rails.
MATERIAL_RGBA: dict[MaterialStyle, tuple[float, float, float, float]] = {
    "aluminum": (0.82, 0.83, 0.85, 1.0),
    "fiberglass": (0.86, 0.40, 0.16, 1.0),
    "steel": (0.62, 0.65, 0.69, 1.0),
}

# Minimum half-spread between the front and rear feet (along X).  The actual
# foot offset is derived from ``top_rail_z`` * tan(frame_angle).
FRAME_ANGLE_MIN_DEG = 15.0
FRAME_ANGLE_MAX_DEG = 35.0

# Hinge axis must be world Y per spec.
FOLD_AXIS: tuple[float, float, float] = (0.0, 1.0, 0.0)


# ---------------------------------------------------------------------------
# Config + ResolvedConfig (ferris_wheel pattern).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SimpleAframeStepLadderConfig:
    ladder_height_class: LadderHeightClass = "medium"
    top_rail_z: float | None = None  # spine; per-class continuous range
    frame_angle_deg: float = 22.0
    step_style: StepStyle = "flat"
    rail_cross_section: RailCrossSection = "rectangular"
    rear_support_style: RearSupportStyle = "simple"
    top_cap_style: TopCapStyle = "narrow_cap"
    spreader_type: SpreaderType = "side_bar"
    foot_style: FootStyle = "rubber_pads"
    material_style: MaterialStyle = "aluminum"
    name: str = "reference_simple_aframe_step_ladder"


@dataclass(frozen=True)
class ResolvedSimpleAframeStepLadderConfig:
    ladder_height_class: LadderHeightClass
    top_rail_z: float
    step_count: int  # derived from ladder_height_class
    frame_angle_rad: float
    step_style: StepStyle
    rail_cross_section: RailCrossSection
    rear_support_style: RearSupportStyle
    top_cap_style: TopCapStyle
    spreader_type: SpreaderType
    foot_style: FootStyle
    material_style: MaterialStyle
    rail_half_spacing_y: float  # half of inner ladder width
    rail_cross_size: float  # rail cross-section nominal half-extent
    foot_half_size_y: float
    foot_half_size_x: float
    foot_thickness_z: float
    front_foot_x: float
    rear_foot_x: float
    name: str


def _sample_step_count(rng: random.Random, ladder_class: LadderHeightClass) -> int:
    return int(rng.choice(STEP_COUNT_CHOICES[ladder_class]))


def config_from_seed(seed: int) -> SimpleAframeStepLadderConfig:
    rng = random.Random(seed)
    ladder_class: LadderHeightClass = rng.choice(("low", "medium", "tall"))
    z_min, z_max = TOP_RAIL_Z_RANGES[ladder_class]
    top_rail_z = round(rng.uniform(z_min, z_max), 3)
    frame_angle = round(rng.uniform(FRAME_ANGLE_MIN_DEG, FRAME_ANGLE_MAX_DEG), 2)
    step_style: StepStyle = rng.choice(("flat", "narrow_rung", "anti_slip"))
    rail_cross_section: RailCrossSection = rng.choice(("rectangular", "round"))
    rear_support_style: RearSupportStyle = "simple"
    top_cap_style: TopCapStyle = rng.choice(("narrow_cap", "tool_tray", "flat"))
    spreader_type: SpreaderType = rng.choice(("none", "side_bar", "folding_link"))
    foot_style: FootStyle = rng.choice(("rubber_pads", "wide_pads"))
    material_style: MaterialStyle = rng.choice(("aluminum", "fiberglass", "steel"))
    return SimpleAframeStepLadderConfig(
        ladder_height_class=ladder_class,
        top_rail_z=top_rail_z,
        frame_angle_deg=frame_angle,
        step_style=step_style,
        rail_cross_section=rail_cross_section,
        rear_support_style=rear_support_style,
        top_cap_style=top_cap_style,
        spreader_type=spreader_type,
        foot_style=foot_style,
        material_style=material_style,
        name=f"seeded_simple_aframe_step_ladder_{seed}",
    )


def resolve_config(
    config: SimpleAframeStepLadderConfig,
) -> ResolvedSimpleAframeStepLadderConfig:
    if config.ladder_height_class not in TOP_RAIL_Z_RANGES:
        raise ValueError(f"Unsupported ladder_height_class: {config.ladder_height_class}")
    if config.step_style not in {"flat", "narrow_rung", "anti_slip"}:
        raise ValueError(f"Unsupported step_style: {config.step_style}")
    if config.rail_cross_section not in {"rectangular", "round"}:
        raise ValueError(f"Unsupported rail_cross_section: {config.rail_cross_section}")
    if config.rear_support_style not in {"simple"}:
        raise ValueError(f"Unsupported rear_support_style: {config.rear_support_style}")
    if config.top_cap_style not in {"narrow_cap", "tool_tray", "flat"}:
        raise ValueError(f"Unsupported top_cap_style: {config.top_cap_style}")
    if config.spreader_type not in {"none", "side_bar", "folding_link"}:
        raise ValueError(f"Unsupported spreader_type: {config.spreader_type}")
    if config.foot_style not in {"rubber_pads", "wide_pads"}:
        raise ValueError(f"Unsupported foot_style: {config.foot_style}")
    if config.material_style not in MATERIAL_RGBA:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if not (FRAME_ANGLE_MIN_DEG - 0.001 <= config.frame_angle_deg <= FRAME_ANGLE_MAX_DEG + 0.001):
        raise ValueError(
            f"frame_angle_deg must be in [{FRAME_ANGLE_MIN_DEG}, {FRAME_ANGLE_MAX_DEG}], "
            f"got {config.frame_angle_deg}"
        )
    z_min, z_max = TOP_RAIL_Z_RANGES[config.ladder_height_class]
    if config.top_rail_z is None:
        top_rail_z = 0.5 * (z_min + z_max)
    else:
        # Clamp to the configured bucket so config diversity never silently
        # drifts out of the spec's class range.
        top_rail_z = max(z_min, min(z_max, float(config.top_rail_z)))

    # Derive step_count deterministically from the spine seed.  We thread
    # the class name + height into a small RNG so the resolved step count is
    # stable for a given Config but still varies across height bucket samples.
    step_rng = random.Random(hash(("step_count", config.ladder_height_class, round(top_rail_z, 4))))
    step_count = _sample_step_count(step_rng, config.ladder_height_class)

    frame_angle_rad = math.radians(config.frame_angle_deg)

    # Foot footprint derives from spine + frame_angle.
    front_foot_x = top_rail_z * math.tan(frame_angle_rad)
    rear_foot_x = -top_rail_z * math.tan(frame_angle_rad)

    # Rail half-spacing across Y scales modestly with height class.
    if config.ladder_height_class == "low":
        rail_half_spacing_y = 0.18
    elif config.ladder_height_class == "medium":
        rail_half_spacing_y = 0.20
    else:
        rail_half_spacing_y = 0.22

    # Rail cross-section nominal size: rectangular = side length, round = radius.
    if config.rail_cross_section == "rectangular":
        rail_cross_size = 0.028
    else:
        rail_cross_size = 0.018

    # Foot dimensions depend on foot_style.
    if config.foot_style == "wide_pads":
        foot_half_size_y = 0.055
        foot_half_size_x = 0.060
    else:
        foot_half_size_y = 0.035
        foot_half_size_x = 0.040
    foot_thickness_z = 0.022

    return ResolvedSimpleAframeStepLadderConfig(
        ladder_height_class=config.ladder_height_class,
        top_rail_z=top_rail_z,
        step_count=step_count,
        frame_angle_rad=frame_angle_rad,
        step_style=config.step_style,
        rail_cross_section=config.rail_cross_section,
        rear_support_style=config.rear_support_style,
        top_cap_style=config.top_cap_style,
        spreader_type=config.spreader_type,
        foot_style=config.foot_style,
        material_style=config.material_style,
        rail_half_spacing_y=rail_half_spacing_y,
        rail_cross_size=rail_cross_size,
        foot_half_size_y=foot_half_size_y,
        foot_half_size_x=foot_half_size_x,
        foot_thickness_z=foot_thickness_z,
        front_foot_x=front_foot_x,
        rear_foot_x=rear_foot_x,
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Geometry helpers.
# ---------------------------------------------------------------------------


def _add_rail(
    part,
    *,
    top_xyz: tuple[float, float, float],
    bottom_xyz: tuple[float, float, float],
    cross_section: RailCrossSection,
    cross_size: float,
    material,
    name: str,
) -> None:
    """Add a single rail as a tilted box or cylinder going from top to bottom.

    The rail is built so its long axis points from ``top_xyz`` to ``bottom_xyz``.
    The tilt is achieved with an RPY rotation about Y (pitch); the in-Y-Z plane
    is not used because rails tilt in the X-Z plane (width = Y is preserved).
    """
    dx = bottom_xyz[0] - top_xyz[0]
    dz = bottom_xyz[2] - top_xyz[2]
    length = math.hypot(dx, dz)
    # Pitch about Y: angle between rail and world -Z (downward).  We want the
    # rail's local +Z to point from top to bottom (i.e. world (dx, 0, dz)).
    # For a cylinder, length is along local Z, so we need to rotate local +Z
    # to that world direction.  Rotation about Y by angle ``pitch`` (URDF Ry)
    # sends local +Z to (sin(pitch), 0, cos(pitch)).  We need this to align
    # with the *downward* direction (dx, 0, dz) / length where dz is negative.
    # Solve: sin(pitch) = dx / length, cos(pitch) = dz / length.
    pitch = math.atan2(dx, dz)
    center = (
        0.5 * (top_xyz[0] + bottom_xyz[0]),
        0.5 * (top_xyz[1] + bottom_xyz[1]),
        0.5 * (top_xyz[2] + bottom_xyz[2]),
    )
    if cross_section == "rectangular":
        part.visual(
            Box((cross_size, cross_size, length)),
            origin=Origin(xyz=center, rpy=(0.0, pitch, 0.0)),
            material=material,
            name=name, material_class_id="metal.aluminum_bare",
        )
    else:
        part.visual(
            Cylinder(radius=cross_size, length=length),
            origin=Origin(xyz=center, rpy=(0.0, pitch, 0.0)),
            material=material,
            name=name, material_class_id="metal.aluminum_bare",
        )


def _interp_along_rail(
    top_xyz: tuple[float, float, float],
    bottom_xyz: tuple[float, float, float],
    t: float,
) -> tuple[float, float, float]:
    return (
        top_xyz[0] + (bottom_xyz[0] - top_xyz[0]) * t,
        top_xyz[1] + (bottom_xyz[1] - top_xyz[1]) * t,
        top_xyz[2] + (bottom_xyz[2] - top_xyz[2]) * t,
    )


def _add_step(
    part,
    *,
    center_xyz: tuple[float, float, float],
    rail_half_spacing_y: float,
    step_style: StepStyle,
    tread_material,
    grip_material,
    index: int,
) -> None:
    """Add one step (tread + style-specific grip) spanning left/right rails.

    The tread spans the full ladder inner width along Y so it physically
    connects both front rails.  Per the spec, anti-slip steps must carry grip
    geometry as parent.visual children of the step's part.
    """
    width_y = 2.0 * rail_half_spacing_y + 0.02  # slight overhang
    if step_style == "narrow_rung":
        tread_depth_x = 0.04  # narrow rung
        tread_height_z = 0.022
    else:
        tread_depth_x = 0.105
        tread_height_z = 0.024
    part.visual(
        Box((tread_depth_x, width_y, tread_height_z)),
        origin=Origin(xyz=center_xyz),
        material=tread_material,
        name=f"step_{index}", material_class_id="metal.paint_coated",
    )
    if step_style == "anti_slip":
        # Grip ridges along the tread (parent.visual children of the step's
        # parent part, exactly as spec mandates).
        for ridge_idx, ridge_y_frac in enumerate((-0.35, 0.0, 0.35)):
            ridge_y = center_xyz[1] + ridge_y_frac * width_y
            part.visual(
                Box((tread_depth_x * 0.85, 0.008, 0.005)),
                origin=Origin(
                    xyz=(center_xyz[0], ridge_y, center_xyz[2] + tread_height_z * 0.5 + 0.002)
                ),
                material=grip_material,
                name=f"step_{index}_grip_ridge_{ridge_idx}", material_class_id="rubber.smooth_plain",
            )


def _add_foot_pad(
    part,
    *,
    foot_x: float,
    foot_y: float,
    foot_half_size_x: float,
    foot_half_size_y: float,
    foot_thickness_z: float,
    rubber_material,
    name: str,
) -> None:
    """Place a foot pad with its bottom face exactly on the ground (z=0)."""
    pad_size_x = 2.0 * foot_half_size_x
    pad_size_y = 2.0 * foot_half_size_y
    part.visual(
        Box((pad_size_x, pad_size_y, foot_thickness_z)),
        origin=Origin(xyz=(foot_x, foot_y, 0.5 * foot_thickness_z)),
        material=rubber_material,
        name=name, material_class_id="rubber.smooth_plain",
    )


def _add_top_cap_visuals(
    part,
    *,
    top_cap_style: TopCapStyle,
    top_rail_z: float,
    rail_half_spacing_y: float,
    cap_material,
    accent_material,
) -> None:
    """Top cap geometry mounted as parent.visual children of front_frame."""
    cap_y = 2.0 * rail_half_spacing_y + 0.05
    if top_cap_style == "narrow_cap":
        cap_size = (0.10, cap_y, 0.022)
        part.visual(
            Box(cap_size),
            origin=Origin(xyz=(0.0, 0.0, top_rail_z + 0.011)),
            material=cap_material,
            name="top_cap", material_class_id="plastic.opaque_glossy_molded",
        )
    elif top_cap_style == "tool_tray":
        # Flat tray plate.
        part.visual(
            Box((0.18, cap_y, 0.014)),
            origin=Origin(xyz=(0.0, 0.0, top_rail_z + 0.007)),
            material=cap_material,
            name="top_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        # Tool-tray side cheeks as anti-roll rims (parent.visual on front_frame).
        for side, sign in (("left", 1.0), ("right", -1.0)):
            part.visual(
                Box((0.18, 0.012, 0.018)),
                origin=Origin(xyz=(0.0, sign * (cap_y * 0.5 - 0.006), top_rail_z + 0.018)),
                material=accent_material,
                name=f"top_cap_tray_rim_{side}", material_class_id="plastic.opaque_glossy_molded",
            )
        # A small front lip.
        part.visual(
            Box((0.012, cap_y, 0.018)),
            origin=Origin(xyz=(0.084, 0.0, top_rail_z + 0.018)),
            material=accent_material,
            name="top_cap_tray_lip_front", material_class_id="plastic.opaque_glossy_molded",
        )
    else:
        # "flat" cap.
        part.visual(
            Box((0.14, cap_y, 0.012)),
            origin=Origin(xyz=(0.0, 0.0, top_rail_z + 0.006)),
            material=cap_material,
            name="top_cap", material_class_id="plastic.opaque_glossy_molded",
        )


def _build_front_frame(
    front_frame,
    resolved: ResolvedSimpleAframeStepLadderConfig,
    *,
    rail_material,
    tread_material,
    grip_material,
    rubber_material,
    cap_material,
    accent_material,
) -> dict[str, tuple[float, float, float]]:
    """Build the front (ladder) frame.  Returns key anchor points used later."""
    top_z = resolved.top_rail_z
    rail_top_left = (0.0, +resolved.rail_half_spacing_y, top_z)
    rail_top_right = (0.0, -resolved.rail_half_spacing_y, top_z)
    foot_top_z = resolved.foot_thickness_z
    rail_bottom_left = (resolved.front_foot_x, +resolved.rail_half_spacing_y, foot_top_z)
    rail_bottom_right = (resolved.front_foot_x, -resolved.rail_half_spacing_y, foot_top_z)

    _add_rail(
        front_frame,
        top_xyz=rail_top_left,
        bottom_xyz=rail_bottom_left,
        cross_section=resolved.rail_cross_section,
        cross_size=resolved.rail_cross_size,
        material=rail_material,
        name="front_left_rail",
    )
    _add_rail(
        front_frame,
        top_xyz=rail_top_right,
        bottom_xyz=rail_bottom_right,
        cross_section=resolved.rail_cross_section,
        cross_size=resolved.rail_cross_size,
        material=rail_material,
        name="front_right_rail",
    )

    # Steps: distribute step_count steps along the rail, leaving a margin near
    # the top.  ``t`` runs from a small offset down to near-bottom.
    n = resolved.step_count
    t_top = 0.18
    t_bottom = 0.92
    for i in range(n):
        if n == 1:
            t = 0.5
        else:
            t = t_top + (t_bottom - t_top) * (i / (n - 1))
        center_left = _interp_along_rail(rail_top_left, rail_bottom_left, t)
        center_right = _interp_along_rail(rail_top_right, rail_bottom_right, t)
        center = (
            0.5 * (center_left[0] + center_right[0]),
            0.5 * (center_left[1] + center_right[1]),
            0.5 * (center_left[2] + center_right[2]),
        )
        # Number steps from bottom (1) upward (N) to read naturally.
        step_index = n - i
        _add_step(
            front_frame,
            center_xyz=center,
            rail_half_spacing_y=resolved.rail_half_spacing_y,
            step_style=resolved.step_style,
            tread_material=tread_material,
            grip_material=grip_material,
            index=step_index,
        )

    # Feet (parent.visual on front_frame) - front-left and front-right.
    _add_foot_pad(
        front_frame,
        foot_x=resolved.front_foot_x,
        foot_y=+resolved.rail_half_spacing_y,
        foot_half_size_x=resolved.foot_half_size_x,
        foot_half_size_y=resolved.foot_half_size_y,
        foot_thickness_z=resolved.foot_thickness_z,
        rubber_material=rubber_material,
        name="front_left_foot",
    )
    _add_foot_pad(
        front_frame,
        foot_x=resolved.front_foot_x,
        foot_y=-resolved.rail_half_spacing_y,
        foot_half_size_x=resolved.foot_half_size_x,
        foot_half_size_y=resolved.foot_half_size_y,
        foot_thickness_z=resolved.foot_thickness_z,
        rubber_material=rubber_material,
        name="front_right_foot",
    )

    # Top cap visuals attached as parent.visual children (no extra parts).
    _add_top_cap_visuals(
        front_frame,
        top_cap_style=resolved.top_cap_style,
        top_rail_z=top_z,
        rail_half_spacing_y=resolved.rail_half_spacing_y,
        cap_material=cap_material,
        accent_material=accent_material,
    )

    return {
        "top_left": rail_top_left,
        "top_right": rail_top_right,
        "bottom_left": rail_bottom_left,
        "bottom_right": rail_bottom_right,
    }


def _build_rear_support_frame(
    rear_frame,
    resolved: ResolvedSimpleAframeStepLadderConfig,
    *,
    rail_material,
    accent_material,
    rubber_material,
) -> dict[str, tuple[float, float, float]]:
    """Build the rear support frame in its rest-pose (open) world coordinates.

    The fold joint origin is the world-space top hinge (0, 0, top_rail_z) in
    the parent (front_frame) frame; the rear part's local frame is coincident
    with that joint frame at q=0.  We therefore author all rear visuals in a
    local frame centred on the top hinge, with rear feet pointing toward -X.
    """
    top_z = resolved.top_rail_z
    foot_top_z = resolved.foot_thickness_z
    # Rear feet land at world X = resolved.rear_foot_x, Z = foot_top_z.  In the
    # rear part's local frame (origin at top hinge, no rotation), feet are at:
    foot_dx = resolved.rear_foot_x  # negative
    foot_dz_from_top = foot_top_z - top_z  # negative

    rail_top_left = (0.0, +resolved.rail_half_spacing_y, 0.0)
    rail_top_right = (0.0, -resolved.rail_half_spacing_y, 0.0)
    rail_bottom_left = (foot_dx, +resolved.rail_half_spacing_y, foot_dz_from_top)
    rail_bottom_right = (foot_dx, -resolved.rail_half_spacing_y, foot_dz_from_top)

    _add_rail(
        rear_frame,
        top_xyz=rail_top_left,
        bottom_xyz=rail_bottom_left,
        cross_section=resolved.rail_cross_section,
        cross_size=resolved.rail_cross_size,
        material=rail_material,
        name="rear_left_rail",
    )
    _add_rail(
        rear_frame,
        top_xyz=rail_top_right,
        bottom_xyz=rail_bottom_right,
        cross_section=resolved.rail_cross_section,
        cross_size=resolved.rail_cross_size,
        material=rail_material,
        name="rear_right_rail",
    )

    # Crossbars (parent.visual on rear_frame): 2 horizontal bars.
    bar_y = 2.0 * resolved.rail_half_spacing_y - 0.02
    for i, t in enumerate((0.45, 0.80)):
        center_left = _interp_along_rail(rail_top_left, rail_bottom_left, t)
        center_right = _interp_along_rail(rail_top_right, rail_bottom_right, t)
        center = (
            0.5 * (center_left[0] + center_right[0]),
            0.5 * (center_left[1] + center_right[1]),
            0.5 * (center_left[2] + center_right[2]),
        )
        rear_frame.visual(
            Box((0.035, bar_y, 0.020)),
            origin=Origin(xyz=center),
            material=accent_material,
            name=f"rear_crossbar_{i}", material_class_id="metal.paint_coated",
        )

    # Rear feet pads.
    _add_foot_pad(
        rear_frame,
        foot_x=foot_dx,
        foot_y=+resolved.rail_half_spacing_y,
        foot_half_size_x=resolved.foot_half_size_x,
        foot_half_size_y=resolved.foot_half_size_y,
        foot_thickness_z=resolved.foot_thickness_z,
        rubber_material=rubber_material,
        name="rear_left_foot",
    )
    _add_foot_pad(
        rear_frame,
        foot_x=foot_dx,
        foot_y=-resolved.rail_half_spacing_y,
        foot_half_size_x=resolved.foot_half_size_x,
        foot_half_size_y=resolved.foot_half_size_y,
        foot_thickness_z=resolved.foot_thickness_z,
        rubber_material=rubber_material,
        name="rear_right_foot",
    )
    # The rear part's local origin sits at world z = top_rail_z, so a foot
    # whose bottom face should land on world z = 0 needs its local centre at
    # z = 0.5 * foot_thickness_z - top_rail_z.  Override the two foot
    # visuals (added with the front-frame helper that doesn't know about the
    # rear local offset).
    local_foot_z = 0.5 * resolved.foot_thickness_z - top_z
    for foot_name, sign_y in (("rear_left_foot", +1.0), ("rear_right_foot", -1.0)):
        foot_visual = rear_frame.get_visual(foot_name)
        foot_visual.origin = Origin(
            xyz=(foot_dx, sign_y * resolved.rail_half_spacing_y, local_foot_z)
        )

    return {
        "top_left": rail_top_left,
        "top_right": rail_top_right,
        "bottom_left": rail_bottom_left,
        "bottom_right": rail_bottom_right,
    }


# ---------------------------------------------------------------------------
# Spreaders.
# ---------------------------------------------------------------------------


SPREADER_COUNT: dict[SpreaderType, int] = {
    "none": 0,
    "side_bar": 2,
    "folding_link": 4,
}


def _spreader_names(spreader_type: SpreaderType) -> tuple[str, ...]:
    if spreader_type == "none":
        return ()
    if spreader_type == "side_bar":
        return ("left_side_bar_spreader", "right_side_bar_spreader")
    return (
        "left_front_folding_link",
        "left_rear_folding_link",
        "right_front_folding_link",
        "right_rear_folding_link",
    )


def _add_spreader_geometry(
    part,
    *,
    length: float,
    material,
    fastener_material,
    visual_prefix: str,
) -> None:
    part.visual(
        Box((length, 0.018, 0.010)),
        origin=Origin(xyz=(0.5 * length, 0.0, 0.0)),
        material=material,
        name=f"{visual_prefix}_bar", material_class_id="metal.paint_coated",
    )
    # Pivot lug on the mounted end and an inner lug at the free end so the
    # validator can locate the spreader's mounting and tip without ambiguity.
    part.visual(
        Box((0.022, 0.020, 0.020)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=fastener_material,
        name=f"{visual_prefix}_pivot_lug", material_class_id="metal.steel_galvanized",
    )
    part.visual(
        Box((0.022, 0.018, 0.018)),
        origin=Origin(xyz=(length, 0.0, 0.0)),
        material=fastener_material,
        name=f"{visual_prefix}_inner_lug", material_class_id="metal.steel_galvanized",
    )


# ---------------------------------------------------------------------------
# Build entry point.
# ---------------------------------------------------------------------------


def build_simple_aframe_step_ladder(
    config: SimpleAframeStepLadderConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or SimpleAframeStepLadderConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-simple-aframe-ladder-")))

    model = ArticulatedObject(name=resolved.name, assets=assets)

    rail_rgba = MATERIAL_RGBA[resolved.material_style]
    rail_material = model.material("ladder_rail", rgba=rail_rgba)
    tread_material = model.material("ladder_tread", rgba=(0.30, 0.32, 0.34, 1.0))
    grip_material = model.material("ladder_grip", rgba=(0.12, 0.13, 0.14, 1.0))
    rubber_material = model.material("ladder_rubber_foot", rgba=(0.08, 0.08, 0.09, 1.0))
    cap_material = model.material("ladder_top_cap", rgba=(0.20, 0.22, 0.24, 1.0))
    accent_material = model.material("ladder_accent", rgba=(0.45, 0.47, 0.50, 1.0))
    fastener_material = model.material("ladder_fastener", rgba=(0.66, 0.68, 0.72, 1.0))

    front_frame = model.part("front_frame")
    front_anchors = _build_front_frame(
        front_frame,
        resolved,
        rail_material=rail_material,
        tread_material=tread_material,
        grip_material=grip_material,
        rubber_material=rubber_material,
        cap_material=cap_material,
        accent_material=accent_material,
    )

    rear_frame = model.part("rear_support_frame")
    rear_anchors = _build_rear_support_frame(
        rear_frame,
        resolved,
        rail_material=rail_material,
        accent_material=accent_material,
        rubber_material=rubber_material,
    )

    # ------------------------------------------------------------------
    # Fold joint.  parent = front_frame, child = rear_support_frame.
    # Origin sits at the world-space top hinge (which is also the local top
    # of the front_frame).  Axis = (0, 1, 0) by spec.  Lower bound allows
    # the rear frame to be folded back toward the front frame; upper bound
    # is 0 (rest, fully open A-shape).
    # ------------------------------------------------------------------
    fold_origin = Origin(xyz=(0.0, 0.0, resolved.top_rail_z))
    fold_upper = 0.0
    # Allow folding rear toward front by up to 2 * frame_angle (parallel).
    fold_lower = -2.0 * resolved.frame_angle_rad - 0.05
    model.articulation(
        "frame_fold_joint",
        ArticulationType.REVOLUTE,
        parent=front_frame,
        child=rear_frame,
        origin=fold_origin,
        axis=FOLD_AXIS,
        motion_limits=MotionLimits(
            effort=24.0,
            velocity=1.6,
            lower=fold_lower,
            upper=fold_upper,
        ),
    )

    # ------------------------------------------------------------------
    # Spreaders.
    # ------------------------------------------------------------------
    spreader_names = _spreader_names(resolved.spreader_type)
    # Spreader bar length spans roughly half the open footprint along X.
    spreader_length = max(0.12, 0.45 * (resolved.front_foot_x - resolved.rear_foot_x) * 0.5)

    if resolved.spreader_type == "side_bar":
        # One bar per side, hinged to the front frame near mid-rail, reaching
        # toward the rear frame.  Free end is decorative; spec accepts joint
        # type revolute OR fixed for spreaders.
        for name in spreader_names:
            spreader_part = model.part(name)
            _add_spreader_geometry(
                spreader_part,
                length=spreader_length,
                material=accent_material,
                fastener_material=fastener_material,
                visual_prefix=name,
            )
        # Mount points on the front rails, partway down (t=0.50).
        for side_sign, name in (
            (+1.0, "left_side_bar_spreader"),
            (-1.0, "right_side_bar_spreader"),
        ):
            mount = _interp_along_rail(
                front_anchors["top_left" if side_sign > 0 else "top_right"],
                front_anchors["bottom_left" if side_sign > 0 else "bottom_right"],
                0.55,
            )
            model.articulation(
                f"spreader_joint_{name}",
                ArticulationType.REVOLUTE,
                parent=front_frame,
                child=name,
                origin=Origin(xyz=mount),
                axis=FOLD_AXIS,
                motion_limits=MotionLimits(
                    effort=6.0,
                    velocity=2.0,
                    lower=-1.0,
                    upper=0.05,
                ),
            )
    elif resolved.spreader_type == "folding_link":
        # 4 half-spreaders.  Each one hinges to either front or rear frame.
        for name in spreader_names:
            spreader_part = model.part(name)
            _add_spreader_geometry(
                spreader_part,
                length=spreader_length * 0.55,
                material=accent_material,
                fastener_material=fastener_material,
                visual_prefix=name,
            )
        link_mount_t = 0.55
        # Front-side links hinge to the front frame.
        for side_sign, name in (
            (+1.0, "left_front_folding_link"),
            (-1.0, "right_front_folding_link"),
        ):
            mount = _interp_along_rail(
                front_anchors["top_left" if side_sign > 0 else "top_right"],
                front_anchors["bottom_left" if side_sign > 0 else "bottom_right"],
                link_mount_t,
            )
            model.articulation(
                f"spreader_joint_{name}",
                ArticulationType.REVOLUTE,
                parent=front_frame,
                child=name,
                origin=Origin(xyz=mount),
                axis=FOLD_AXIS,
                motion_limits=MotionLimits(
                    effort=4.0,
                    velocity=2.0,
                    lower=-1.0,
                    upper=0.05,
                ),
            )
        # Rear-side links hinge to the rear frame (local coords).
        for side_sign, name in (
            (+1.0, "left_rear_folding_link"),
            (-1.0, "right_rear_folding_link"),
        ):
            mount = _interp_along_rail(
                rear_anchors["top_left" if side_sign > 0 else "top_right"],
                rear_anchors["bottom_left" if side_sign > 0 else "bottom_right"],
                link_mount_t,
            )
            model.articulation(
                f"spreader_joint_{name}",
                ArticulationType.REVOLUTE,
                parent=rear_frame,
                child=name,
                origin=Origin(xyz=mount),
                axis=FOLD_AXIS,
                motion_limits=MotionLimits(
                    effort=4.0,
                    velocity=2.0,
                    lower=-0.05,
                    upper=1.0,
                ),
            )

    return model


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------


def run_simple_aframe_step_ladder_tests(
    object_model: ArticulatedObject, config: SimpleAframeStepLadderConfig
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)

    front_frame = object_model.get_part("front_frame")
    rear_frame = object_model.get_part("rear_support_frame")
    fold_joint = object_model.get_articulation("frame_fold_joint")

    # The front and rear frames hinge together at the apex and the side-bar
    # spreaders pin the two frames apart; those captured hinge/pivot interfaces
    # intentionally overlap.
    ctx.allow_overlap(
        front_frame, rear_frame,
        reason="Front and rear frames share the apex fold hinge.",
    )
    _part_names = {p.name for p in object_model.parts}
    for _sp in _part_names:
        if "spreader" in _sp or "folding_link" in _sp:
            ctx.allow_overlap(
                front_frame, object_model.get_part(_sp),
                reason="Spreader / folding link is pinned to the front frame rails.",
            )
            ctx.allow_overlap(
                rear_frame, object_model.get_part(_sp),
                reason="Spreader / folding link is pinned to the rear frame rails.",
            )
    # Front/rear folding links cross each other as the frame folds.
    _links = [n for n in _part_names if "folding_link" in n]
    for _i in range(len(_links)):
        for _j in range(_i + 1, len(_links)):
            ctx.allow_overlap(
                object_model.get_part(_links[_i]),
                object_model.get_part(_links[_j]),
                reason="Folding links cross each other while the A-frame folds.",
            )

    # --- 1.  Model integrity.
    ctx.check_model_valid()
    ctx.check_mesh_files_exist()
    ctx.fail_if_isolated_parts()

    # --- 2.  Step count matches the resolved spine derivation.
    step_visual_names = [
        v.name
        for v in front_frame.visuals
        if v.name and v.name.startswith("step_") and "grip" not in v.name
    ]
    ctx.check(
        "step_count_matches_resolved_class",
        len(step_visual_names) == resolved.step_count,
        details=f"found {len(step_visual_names)} step visuals, expected {resolved.step_count}",
    )

    # --- 3.  Fold joint axis must be world Y.  Spec rejects axis along X.
    axis = tuple(fold_joint.axis)
    ctx.check(
        "fold_joint_axis_is_world_y",
        abs(axis[0]) < 1e-6 and abs(axis[1] - 1.0) < 1e-6 and abs(axis[2]) < 1e-6,
        details=f"axis={axis}",
    )
    ctx.check(
        "fold_joint_origin_rpy_zero",
        all(abs(v) < 1e-6 for v in fold_joint.origin.rpy),
        details=f"rpy={fold_joint.origin.rpy}",
    )

    # --- 4.  Top hinge is at top_rail_z.
    ctx.check(
        "fold_joint_origin_at_top",
        abs(fold_joint.origin.xyz[2] - resolved.top_rail_z) < 1e-4,
        details=(
            f"fold_joint origin z={fold_joint.origin.xyz[2]:.4f}, "
            f"expected ~{resolved.top_rail_z:.4f}"
        ),
    )

    # --- 5.  All four feet touch the ground plane in the open pose.
    foot_tol_z = 1e-3
    for part, foot_name in (
        (front_frame, "front_left_foot"),
        (front_frame, "front_right_foot"),
        (rear_frame, "rear_left_foot"),
        (rear_frame, "rear_right_foot"),
    ):
        aabb = ctx.part_element_world_aabb(part, elem=foot_name)
        bottom_z = aabb[0][2] if aabb is not None else None
        ctx.check(
            f"{foot_name}_bottom_at_ground",
            aabb is not None and abs(bottom_z) <= foot_tol_z,
            details=(f"foot bottom z={bottom_z}, expected within +/-{foot_tol_z} of ground"),
        )

    # --- 6.  Open A-shape: rear feet sit at -X and front feet sit at +X.  We
    # use AABB centres to make this robust against pad thickness.
    front_foot_aabb = ctx.part_element_world_aabb(front_frame, elem="front_left_foot")
    rear_foot_aabb = ctx.part_element_world_aabb(rear_frame, elem="rear_left_foot")
    if front_foot_aabb is not None and rear_foot_aabb is not None:
        front_x = 0.5 * (front_foot_aabb[0][0] + front_foot_aabb[1][0])
        rear_x = 0.5 * (rear_foot_aabb[0][0] + rear_foot_aabb[1][0])
        ctx.check(
            "a_shape_open_stance",
            (front_x - rear_x) > 0.10,
            details=(
                f"open A-shape requires front_foot_x > rear_foot_x by at least 0.10; "
                f"got front_x={front_x:.3f}, rear_x={rear_x:.3f}"
            ),
        )

    # --- 7.  Steps attach to both front rails.  We check the leftmost step
    # spans across rail_half_spacing_y on both sides (within margin).
    if step_visual_names:
        any_step_name = step_visual_names[len(step_visual_names) // 2]
        step_aabb = ctx.part_element_world_aabb(front_frame, elem=any_step_name)
        if step_aabb is not None:
            min_y, max_y = step_aabb[0][1], step_aabb[1][1]
            ctx.check(
                "step_spans_left_and_right_rails",
                min_y <= -resolved.rail_half_spacing_y + 0.005
                and max_y >= +resolved.rail_half_spacing_y - 0.005,
                details=(
                    f"step y-extent [{min_y:.3f}, {max_y:.3f}] must cover "
                    f"+/-{resolved.rail_half_spacing_y:.3f}"
                ),
            )

    # --- 8.  Spreader consistency: part count == expected for spreader_type.
    expected_spreader_count = SPREADER_COUNT[resolved.spreader_type]
    spreader_parts = [
        p for p in object_model.parts if "spreader" in p.name or "folding_link" in p.name
    ]
    ctx.check(
        "spreader_part_count_matches_type",
        len(spreader_parts) == expected_spreader_count,
        details=(
            f"spreader_type={resolved.spreader_type} expects "
            f"{expected_spreader_count} spreader parts; found {len(spreader_parts)}"
        ),
    )

    # --- 9.  Anti-slip evidence: when step_style is anti_slip, every step has
    # at least one grip ridge visual on the front_frame part.
    if resolved.step_style == "anti_slip":
        grip_visuals = [v for v in front_frame.visuals if v.name and "grip_ridge" in v.name]
        ctx.check(
            "anti_slip_grip_geometry_present",
            len(grip_visuals) >= resolved.step_count,
            details=(
                f"anti_slip step_style requires >= {resolved.step_count} grip visuals; "
                f"found {len(grip_visuals)}"
            ),
        )

    # --- 10. Hinge actually folds the rear frame.  Compare rear foot world X
    # at rest (open) vs. at the fold-joint lower bound (folded).
    limits = fold_joint.motion_limits
    rest_aabb = ctx.part_element_world_aabb(rear_frame, elem="rear_left_foot")
    rest_x = 0.5 * (rest_aabb[0][0] + rest_aabb[1][0]) if rest_aabb is not None else None
    if limits is not None and limits.lower is not None and rest_x is not None:
        with ctx.pose({fold_joint: limits.lower}):
            folded_aabb = ctx.part_element_world_aabb(rear_frame, elem="rear_left_foot")
            folded_x = (
                0.5 * (folded_aabb[0][0] + folded_aabb[1][0]) if folded_aabb is not None else None
            )
            ctx.check(
                "fold_joint_moves_rear_frame_toward_front",
                folded_x is not None and folded_x > rest_x + 0.05,
                details=(
                    f"folding should pull rear foot toward +X; rest_x={rest_x}, folded_x={folded_x}"
                ),
            )

    return ctx.report()


# ---------------------------------------------------------------------------
# Convenience entry points.
# ---------------------------------------------------------------------------


def build_seeded_simple_aframe_step_ladder(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_simple_aframe_step_ladder(config_from_seed(seed), assets=assets)


def with_overrides(
    config: SimpleAframeStepLadderConfig, **kwargs: object
) -> SimpleAframeStepLadderConfig:
    return replace(config, **kwargs)
