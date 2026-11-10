# SPDX-License-Identifier: Apache-2.0

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
    Cylinder,
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

SupportLayout = Literal[
    "upright_spindle", "underslung", "saddle_body", "tower_post", "drum_indexer"
]
StageBodyStyle = Literal["solid_disk", "annular_ring", "spoked_ring", "stepped_drum", "fixture_cup"]
StageRadiusProfile = Literal["descending", "nested_equal_outer", "underslung_descending"]
RotationRangeMode = Literal["limited", "continuous", "full_turn_revolute"]
IndexMarkerStyle = Literal["none", "pointer_tabs", "tick_marks", "drive_lugs", "bolt_circle"]
BearingStyle = Literal["collar_stack", "thrust_washer", "bearing_land", "hanger_collar"]
MaterialStyle = Literal["instrument_colors", "machined_steel", "dark_indexer"]

PALETTES: dict[
    MaterialStyle,
    dict[str, tuple[float, float, float, float] | tuple[tuple[float, float, float, float], ...]],
] = {
    "instrument_colors": {
        "base": (0.16, 0.18, 0.20, 1.0),
        "shaft": (0.62, 0.64, 0.66, 1.0),
        "bearing": (0.70, 0.52, 0.28, 1.0),
        "accent": (0.92, 0.88, 0.76, 1.0),
        "stages": (
            (0.62, 0.18, 0.14, 1.0),
            (0.78, 0.42, 0.12, 1.0),
            (0.10, 0.52, 0.55, 1.0),
            (0.42, 0.34, 0.64, 1.0),
        ),
    },
    "machined_steel": {
        "base": (0.38, 0.40, 0.42, 1.0),
        "shaft": (0.74, 0.76, 0.76, 1.0),
        "bearing": (0.58, 0.59, 0.58, 1.0),
        "accent": (0.12, 0.13, 0.14, 1.0),
        "stages": (
            (0.64, 0.66, 0.67, 1.0),
            (0.52, 0.55, 0.56, 1.0),
            (0.46, 0.49, 0.50, 1.0),
            (0.36, 0.39, 0.40, 1.0),
        ),
    },
    "dark_indexer": {
        "base": (0.055, 0.060, 0.065, 1.0),
        "shaft": (0.46, 0.48, 0.50, 1.0),
        "bearing": (0.86, 0.60, 0.18, 1.0),
        "accent": (0.95, 0.72, 0.12, 1.0),
        "stages": (
            (0.14, 0.17, 0.20, 1.0),
            (0.20, 0.24, 0.28, 1.0),
            (0.24, 0.17, 0.20, 1.0),
            (0.12, 0.22, 0.22, 1.0),
        ),
    },
}


@dataclass(frozen=True)
class CoaxialRotaryStackConfig:
    stage_count: int = 3
    support_layout: SupportLayout = "upright_spindle"
    stage_body_style: StageBodyStyle = "annular_ring"
    stage_radius_profile: StageRadiusProfile = "descending"
    base_radius: float = 0.22
    shaft_radius: float = 0.027
    stage_gap: float = 0.018
    rotation_range_mode: RotationRangeMode = "limited"
    index_marker_style: IndexMarkerStyle = "pointer_tabs"
    bearing_style: BearingStyle = "collar_stack"
    material_style: MaterialStyle = "instrument_colors"
    name: str = "reference_coaxial_rotary_stack"


@dataclass(frozen=True)
class ResolvedCoaxialRotaryStackConfig:
    stage_count: int
    support_layout: SupportLayout
    stage_body_style: StageBodyStyle
    stage_radius_profile: StageRadiusProfile
    base_radius: float
    shaft_radius: float
    stage_gap: float
    rotation_range_mode: RotationRangeMode
    index_marker_style: IndexMarkerStyle
    bearing_style: BearingStyle
    material_style: MaterialStyle
    stage_radii: tuple[float, ...]
    stage_heights: tuple[float, ...]
    # z-offset of each stage joint origin relative to base origin
    stage_joint_z: tuple[float, ...]
    # absolute z of each stage base face in world frame (used for gap checks)
    stage_base_z: tuple[float, ...]
    shaft_height: float
    name: str


def config_from_seed(seed: int) -> CoaxialRotaryStackConfig:
    rng = random.Random(seed)
    return CoaxialRotaryStackConfig(
        stage_count=rng.randint(2, 4),
        support_layout=rng.choice(("upright_spindle", "saddle_body", "tower_post")),
        stage_body_style=rng.choice(("solid_disk", "annular_ring", "spoked_ring")),
        stage_radius_profile=rng.choice(("descending", "nested_equal_outer")),
        base_radius=round(rng.uniform(0.18, 0.40), 3),
        shaft_radius=round(rng.uniform(0.018, 0.050), 3),
        stage_gap=round(rng.uniform(0.006, 0.035), 3),
        rotation_range_mode=rng.choice(("limited", "continuous", "full_turn_revolute")),
        index_marker_style=rng.choice(("none", "pointer_tabs", "tick_marks", "bolt_circle")),
        bearing_style=rng.choice(("collar_stack", "thrust_washer", "bearing_land")),
        material_style=rng.choice(tuple(PALETTES)),
        name=f"seeded_coaxial_rotary_stack_{seed}",
    )


def resolve_config(config: CoaxialRotaryStackConfig) -> ResolvedCoaxialRotaryStackConfig:
    if config.stage_count not in {2, 3, 4}:
        raise ValueError("stage_count must be in {2,3,4}")
    if config.support_layout not in {
        "upright_spindle",
        "underslung",
        "saddle_body",
        "tower_post",
        "drum_indexer",
    }:
        raise ValueError(f"Unsupported support_layout: {config.support_layout}")
    if config.stage_body_style not in {
        "solid_disk",
        "annular_ring",
        "spoked_ring",
        "stepped_drum",
        "fixture_cup",
    }:
        raise ValueError(f"Unsupported stage_body_style: {config.stage_body_style}")
    if config.stage_radius_profile not in {
        "descending",
        "nested_equal_outer",
        "underslung_descending",
    }:
        raise ValueError(f"Unsupported stage_radius_profile: {config.stage_radius_profile}")
    if config.rotation_range_mode not in {"limited", "continuous", "full_turn_revolute"}:
        raise ValueError(f"Unsupported rotation_range_mode: {config.rotation_range_mode}")
    if config.index_marker_style not in {
        "none",
        "pointer_tabs",
        "tick_marks",
        "drive_lugs",
        "bolt_circle",
    }:
        raise ValueError(f"Unsupported index_marker_style: {config.index_marker_style}")
    if config.bearing_style not in {
        "collar_stack",
        "thrust_washer",
        "bearing_land",
        "hanger_collar",
    }:
        raise ValueError(f"Unsupported bearing_style: {config.bearing_style}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if not 0.14 <= config.base_radius <= 0.50:
        raise ValueError("base_radius must be in [0.14, 0.50]")
    if not 0.010 <= config.shaft_radius <= 0.070:
        raise ValueError("shaft_radius must be in [0.010, 0.070]")
    if not 0.004 <= config.stage_gap <= 0.055:
        raise ValueError("stage_gap must be in [0.004, 0.055]")

    config = replace(
        config,
        support_layout="upright_spindle"
        if config.support_layout in {"underslung", "drum_indexer"}
        else config.support_layout,
        stage_body_style="annular_ring"
        if config.stage_body_style in {"stepped_drum", "fixture_cup"}
        else config.stage_body_style,
        stage_radius_profile="descending"
        if config.stage_radius_profile == "underslung_descending"
        else config.stage_radius_profile,
        index_marker_style="pointer_tabs"
        if config.index_marker_style == "drive_lugs"
        else config.index_marker_style,
        bearing_style="collar_stack"
        if config.bearing_style == "hanger_collar"
        else config.bearing_style,
    )

    if config.stage_radius_profile == "nested_equal_outer":
        stage_radii = tuple(
            config.base_radius * (0.72 - 0.03 * i) for i in range(config.stage_count)
        )
    else:
        stage_radii = tuple(
            config.base_radius * (0.86 - 0.16 * i) for i in range(config.stage_count)
        )
    min_radius = config.shaft_radius * 2.4
    stage_radii = tuple(max(min_radius, r) for r in stage_radii)
    # Stage heights taper slightly from bottom to top for visual realism.
    stage_heights = tuple(
        0.040 + 0.010 * (config.stage_count - i) for i in range(config.stage_count)
    )
    # Support-collar thickness sits between each stage and the one below.
    collar_thickness = min(0.010, max(0.004, config.stage_gap - 0.002))

    # Build up cumulative z positions.
    # Base top-of-housing establishes z=0 for the joint chain.
    base_housing_top = 0.095  # foot + housing
    joint_z: list[float] = []
    base_z: list[float] = []
    cursor = base_housing_top
    for i, height in enumerate(stage_heights):
        joint_z.append(cursor)
        base_z.append(cursor)
        cursor += height + collar_thickness + config.stage_gap

    shaft_height = cursor + 0.060

    return ResolvedCoaxialRotaryStackConfig(
        stage_count=config.stage_count,
        support_layout=config.support_layout,
        stage_body_style=config.stage_body_style,
        stage_radius_profile=config.stage_radius_profile,
        base_radius=config.base_radius,
        shaft_radius=config.shaft_radius,
        stage_gap=config.stage_gap,
        rotation_range_mode=config.rotation_range_mode,
        index_marker_style=config.index_marker_style,
        bearing_style=config.bearing_style,
        material_style=config.material_style,
        stage_radii=stage_radii,
        stage_heights=stage_heights,
        stage_joint_z=tuple(joint_z),
        stage_base_z=tuple(base_z),
        shaft_height=shaft_height,
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------


def _annular_plate_cq(outer_radius: float, inner_radius: float, thickness: float) -> cq.Workplane:
    """CadQuery annular disk with a concentric through-bore."""
    return cq.Workplane("XY").circle(outer_radius).circle(inner_radius).extrude(thickness)


def _spoked_ring_cq(
    outer_radius: float,
    inner_radius: float,
    thickness: float,
    spoke_count: int = 3,
) -> cq.Workplane:
    """Outer annular ring connected to inner hub by evenly-spaced rectangular spokes."""
    hub_outer = inner_radius * 1.45
    spoke_width = min(0.020, outer_radius * 0.10)
    spoke_span = outer_radius - hub_outer - 0.005

    body = _annular_plate_cq(
        outer_radius, outer_radius - max(0.010, outer_radius * 0.12), thickness
    )
    body = body.union(_annular_plate_cq(hub_outer, inner_radius, thickness))

    for k in range(spoke_count):
        angle_deg = 360.0 * k / spoke_count
        spoke = (
            cq.Workplane("XY")
            .box(spoke_span, spoke_width, thickness)
            .translate((hub_outer + spoke_span * 0.5, 0.0, thickness * 0.5))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle_deg)
        )
        body = body.union(spoke)
    return body


def _chamfered_drum_lathe(
    outer_radius: float, inner_radius: float, height: float, chamfered: bool = True
) -> LatheGeometry:
    """Return a LatheGeometry profile for an annular drum, optionally with edge chamfers
    and a shallow circumferential grip groove."""
    chamfer = min(0.008, height * 0.16) if chamfered else 0.0
    groove = min(0.006, (outer_radius - inner_radius) * 0.05) if chamfered else 0.0
    z0 = -height * 0.5
    z1 = z0 + chamfer
    z2 = height * 0.5 - chamfer
    z3 = height * 0.5
    profile = [
        (inner_radius, z0),
        (outer_radius - groove, z0),
        (outer_radius, z1),
        (outer_radius, z1 + height * 0.18),
        (outer_radius - groove * 1.5, z1 + height * 0.24),
        (outer_radius - groove * 1.5, z2 - height * 0.24),
        (outer_radius, z2 - height * 0.18),
        (outer_radius, z2),
        (outer_radius - groove, z3),
        (inner_radius, z3),
        (inner_radius, z0),
    ]
    return LatheGeometry(profile, segments=96)


def _joint_meta(
    joint_type: str,
    axis: tuple[float, float, float],
    origin: tuple[float, float, float],
    joint_range: object,
) -> dict[str, object]:
    return {"type": joint_type, "axis": axis, "origin": origin, "range": joint_range}


def _stage_direction(resolved: ResolvedCoaxialRotaryStackConfig) -> float:
    if (
        resolved.support_layout == "underslung"
        or resolved.stage_radius_profile == "underslung_descending"
    ):
        return -1.0
    return 1.0


# ---------------------------------------------------------------------------
# Part builders
# ---------------------------------------------------------------------------


def _build_base(
    base,
    resolved: ResolvedCoaxialRotaryStackConfig,
    *,
    base_mat,
    shaft_mat,
    bearing_mat,
) -> None:
    foot_height = 0.030
    housing_height = 0.045
    housing_radius = resolved.base_radius * 0.78
    collar_height = 0.008
    collar_radius = resolved.base_radius * 0.50

    if resolved.support_layout == "underslung":
        base.visual(
            Box((resolved.base_radius * 1.7, resolved.base_radius * 0.45, 0.045)),
            origin=Origin(xyz=(0.0, 0.0, 0.040)),
            material=base_mat,
            name="top_support", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )
    elif resolved.support_layout == "drum_indexer":
        base.visual(
            Cylinder(radius=resolved.base_radius, length=0.080),
            origin=Origin(xyz=(0.0, 0.0, 0.040)),
            material=base_mat,
            name="drum_mount_body", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )
    elif resolved.support_layout == "saddle_body":
        base.visual(
            Box((resolved.base_radius * 1.8, resolved.base_radius * 1.2, 0.060)),
            origin=Origin(xyz=(0.0, 0.0, 0.030)),
            material=base_mat,
            name="saddle_mount_plate", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )
    elif resolved.support_layout == "tower_post":
        base.visual(
            Box((resolved.base_radius * 1.3, resolved.base_radius * 1.3, 0.055)),
            origin=Origin(xyz=(0.0, 0.0, 0.028)),
            material=base_mat,
            name="tower_base_plate", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )
        base.visual(
            Cylinder(radius=resolved.base_radius * 0.16, length=resolved.shaft_height * 0.62),
            origin=Origin(xyz=(0.0, 0.0, resolved.shaft_height * 0.31)),
            material=base_mat,
            name="tower_post", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )
    else:
        # upright_spindle — most common layout: flat foot + central housing.
        base.visual(
            Cylinder(radius=resolved.base_radius, length=foot_height),
            origin=Origin(xyz=(0.0, 0.0, foot_height * 0.5)),
            material=base_mat,
            name="base_foot", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )
        base.visual(
            Cylinder(radius=housing_radius, length=housing_height),
            origin=Origin(xyz=(0.0, 0.0, foot_height + housing_height * 0.5)),
            material=base_mat,
            name="base_housing", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )
        base.visual(
            Cylinder(radius=collar_radius, length=collar_height),
            origin=Origin(xyz=(0.0, 0.0, foot_height + housing_height + collar_height * 0.5)),
            material=bearing_mat,
            name="base_support_collar", material_class_id=("metal.brass_polished" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.bronze_cast"),
        )

    # Central spindle shared by all layouts.
    base.visual(
        Cylinder(radius=resolved.shaft_radius, length=resolved.shaft_height),
        origin=Origin(xyz=(0.0, 0.0, resolved.shaft_height * 0.5)),
        material=shaft_mat,
        name="common_shaft", material_class_id="metal.stainless_matte",
    )
    # Retainer cap at spindle top.
    retainer_z = resolved.shaft_height - 0.005
    base.visual(
        Cylinder(radius=resolved.shaft_radius * 1.75, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, retainer_z)),
        material=bearing_mat,
        name="shaft_retainer", material_class_id=("metal.brass_polished" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.bronze_cast"),
    )

    # Support collars between consecutive stages on the shaft.
    support_thickness = min(0.010, max(0.004, resolved.stage_gap - 0.002))
    for i, z in enumerate(resolved.stage_joint_z):
        inner_r = max(resolved.shaft_radius * 1.6, resolved.stage_radii[i] * 0.28)
        collar_name = {
            "collar_stack": "support_collar",
            "thrust_washer": "support_washer",
            "bearing_land": "bearing_land",
            "hanger_collar": "hanger_collar",
        }[resolved.bearing_style]
        base.visual(
            Cylinder(radius=inner_r, length=support_thickness),
            origin=Origin(xyz=(0.0, 0.0, z - support_thickness * 0.5)),
            material=bearing_mat,
            name=f"{collar_name}_{i}", material_class_id=("metal.brass_polished" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.bronze_cast"),
        )
        # Spacer bushing above each stage.
        spacer_h = min(0.018, max(0.008, resolved.stage_heights[i] * 0.22))
        spacer_z = z + resolved.stage_heights[i] + spacer_h * 0.5
        base.visual(
            Cylinder(
                radius=max(resolved.shaft_radius * 1.35, inner_r * 0.58),
                length=spacer_h,
            ),
            origin=Origin(xyz=(0.0, 0.0, spacer_z)),
            material=shaft_mat,
            name=f"shaft_spacer_{i}", material_class_id="metal.stainless_matte",
        )

    base.inertial = Inertial.from_geometry(
        Cylinder(radius=resolved.base_radius, length=resolved.shaft_height),
        mass=max(2.0, resolved.base_radius * 250.0),
        origin=Origin(xyz=(0.0, 0.0, resolved.shaft_height * 0.5)),
    )


def _build_stage(
    stage,
    resolved: ResolvedCoaxialRotaryStackConfig,
    index: int,
    *,
    assets: AssetContext,
    stage_mat,
    accent_mat,
) -> None:
    radius = resolved.stage_radii[index]
    height = resolved.stage_heights[index]
    inner = max(resolved.shaft_radius * 1.6, radius * 0.28)
    direction = _stage_direction(resolved)
    center_z = direction * height * 0.5

    if resolved.stage_body_style == "solid_disk":
        # Use LatheGeometry (annular disk) so there is no overlap with the central shaft.
        stage.visual(
            mesh_from_geometry(
                _chamfered_drum_lathe(radius, inner, height, chamfered=False),
                assets.mesh_path(f"stage_{index}_solid_disk.obj"),
            ),
            origin=Origin(xyz=(0.0, 0.0, center_z)),
            material=stage_mat,
            name="stage_body", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )
        # Bore collar accent ring.
        stage.visual(
            mesh_from_geometry(
                _chamfered_drum_lathe(
                    inner + min(0.012, radius * 0.08), inner, 0.006, chamfered=False
                ),
                assets.mesh_path(f"stage_{index}_bore_accent.obj"),
            ),
            origin=Origin(xyz=(0.0, 0.0, center_z)),
            material=accent_mat,
            name="center_bore_marker", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"instrument_colors", "machined_steel"} else "metal.brass_polished"),
        )

    elif resolved.stage_body_style == "annular_ring":
        stage.visual(
            mesh_from_geometry(
                _chamfered_drum_lathe(radius, inner, height, chamfered=True),
                assets.mesh_path(f"stage_{index}_annular_outer.obj"),
            ),
            origin=Origin(xyz=(0.0, 0.0, center_z)),
            material=stage_mat,
            name="annular_outer_body", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )
        stage.visual(
            mesh_from_geometry(
                _chamfered_drum_lathe(
                    inner + min(0.014, radius * 0.08), inner, 0.006, chamfered=False
                ),
                assets.mesh_path(f"stage_{index}_bore_ring.obj"),
            ),
            origin=Origin(xyz=(0.0, 0.0, center_z)),
            material=accent_mat,
            name="visible_center_bore", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"instrument_colors", "machined_steel"} else "metal.brass_polished"),
        )

    elif resolved.stage_body_style == "spoked_ring":
        spoke_count = 3 if index % 2 == 0 else 4
        # Clamp the hub so the smallest stage still fits spokes
        # (unclamped inner*1.45 can push spoke_span <= 0 on the last stage).
        hub_outer = min(inner * 1.45, radius - 0.011)
        spoke_width = min(0.020, radius * 0.10)
        spoke_span = radius - hub_outer - 0.005
        spoke_center_r = hub_outer + spoke_span * 0.5
        # Outer annular rim ring (LatheGeometry avoids overlap with shaft).
        stage.visual(
            mesh_from_geometry(
                _chamfered_drum_lathe(
                    radius, radius - max(0.010, radius * 0.12), height, chamfered=False
                ),
                assets.mesh_path(f"stage_{index}_rim_ring.obj"),
            ),
            origin=Origin(xyz=(0.0, 0.0, center_z)),
            material=stage_mat,
            name="rim_ring", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )
        # Inner hub annular ring (LatheGeometry avoids overlap with shaft).
        stage.visual(
            mesh_from_geometry(
                _chamfered_drum_lathe(hub_outer, inner, height, chamfered=False),
                assets.mesh_path(f"stage_{index}_hub_ring.obj"),
            ),
            origin=Origin(xyz=(0.0, 0.0, center_z)),
            material=stage_mat,
            name="hub_ring", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )
        # Individual spokes — named spoke_0, spoke_1, … so tests can find them.
        for k in range(spoke_count):
            angle = math.tau * k / spoke_count
            stage.visual(
                Box((spoke_span, spoke_width, height)),
                origin=Origin(
                    xyz=(
                        spoke_center_r * math.cos(angle),
                        spoke_center_r * math.sin(angle),
                        center_z,
                    ),
                    rpy=(0.0, 0.0, angle),
                ),
                material=stage_mat,
                name=f"spoke_{k}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
            )

    elif resolved.stage_body_style == "stepped_drum":
        # Lower thick drum step.
        stage.visual(
            mesh_from_geometry(
                _chamfered_drum_lathe(radius, inner, height * 0.55, chamfered=True),
                assets.mesh_path(f"stage_{index}_lower_step.obj"),
            ),
            origin=Origin(xyz=(0.0, 0.0, direction * height * 0.275)),
            material=stage_mat,
            name="lower_drum_step", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )
        # Upper narrower step.
        stage.visual(
            mesh_from_geometry(
                _chamfered_drum_lathe(
                    max(inner + 0.012, radius * 0.78), inner, height * 0.65, chamfered=True
                ),
                assets.mesh_path(f"stage_{index}_upper_step.obj"),
            ),
            origin=Origin(xyz=(0.0, 0.0, direction * height * 0.600)),
            material=stage_mat,
            name="upper_drum_step", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )

    else:
        # fixture_cup: outer rim + inner hub, like a shallow cup.
        cup_rim_inner = min(radius - 0.010, max(inner * 1.45, radius - max(0.028, radius * 0.14)))
        stage.visual(
            mesh_from_geometry(
                _chamfered_drum_lathe(radius, cup_rim_inner, height * 0.30, chamfered=True),
                assets.mesh_path(f"stage_{index}_cup_rim.obj"),
            ),
            origin=Origin(xyz=(0.0, 0.0, direction * height * 0.150)),
            material=stage_mat,
            name="fixture_cup_rim", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )
        stage.visual(
            mesh_from_geometry(
                _chamfered_drum_lathe(inner * 1.35, inner, height, chamfered=True),
                assets.mesh_path(f"stage_{index}_cup_hub.obj"),
            ),
            origin=Origin(xyz=(0.0, 0.0, center_z)),
            material=stage_mat,
            name="fixture_cup_hub", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"machined_steel", "dark_indexer"} else "metal.paint_coated"),
        )

    # Top bearing race (accent ring visible above the stage body).
    race_radius = min(radius - 0.006, inner + max(0.014, radius * 0.09))
    stage.visual(
        mesh_from_geometry(
            _chamfered_drum_lathe(race_radius, inner, 0.006, chamfered=False),
            assets.mesh_path(f"stage_{index}_top_race.obj"),
        ),
        origin=Origin(xyz=(0.0, 0.0, direction * (height + 0.006) * 0.5)),
        material=accent_mat,
        name="top_bearing_race", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"instrument_colors", "machined_steel"} else "metal.brass_polished"),
    )

    # Index markers — angular offset varies by stage so they are visually distinct.
    marker_yaw = math.tau * index / max(3, resolved.stage_count) + (
        0.35 if direction < 0.0 else 0.0
    )

    if resolved.index_marker_style == "pointer_tabs":
        stage.visual(
            Box((radius * 0.35, 0.024, 0.010)),
            origin=Origin(
                xyz=(
                    radius * 0.82 * math.cos(marker_yaw),
                    radius * 0.82 * math.sin(marker_yaw),
                    direction * height * 0.97,
                ),
                rpy=(0.0, 0.0, marker_yaw),
            ),
            material=accent_mat,
            name="pointer_tab", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"instrument_colors", "machined_steel"} else "metal.brass_polished"),
        )
    elif resolved.index_marker_style == "tick_marks":
        for k in range(8):
            yaw = math.tau * k / 8
            stage.visual(
                Box((0.035, 0.006, 0.006)),
                origin=Origin(
                    xyz=(radius * 0.82, 0.0, direction * height * 0.97),
                    rpy=(0.0, 0.0, yaw),
                ),
                material=accent_mat,
                name=f"tick_mark_{k}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"instrument_colors", "machined_steel"} else "metal.brass_polished"),
            )
    elif resolved.index_marker_style == "drive_lugs":
        stage.visual(
            Box((0.050, 0.043, height * 0.55)),
            origin=Origin(
                xyz=(
                    (radius + 0.014) * math.cos(marker_yaw),
                    (radius + 0.014) * math.sin(marker_yaw),
                    center_z,
                ),
                rpy=(0.0, 0.0, marker_yaw),
            ),
            material=accent_mat,
            name="rim_drive_lug", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"instrument_colors", "machined_steel"} else "metal.brass_polished"),
        )
    elif resolved.index_marker_style == "bolt_circle":
        # Spoked stages have a void between hub and rim; put the bolt circle on
        # the rim ring instead of the 0.70*radius spoke-gap band.
        if resolved.stage_body_style == "spoked_ring":
            bolt_r = radius - max(0.010, radius * 0.12) * 0.5
        else:
            bolt_r = radius * 0.70
        for k in range(6):
            yaw = math.tau * k / 6
            stage.visual(
                Cylinder(radius=0.008, length=0.006),
                origin=Origin(
                    xyz=(
                        bolt_r * math.cos(yaw),
                        bolt_r * math.sin(yaw),
                        direction * height * 0.97,
                    )
                ),
                material=accent_mat,
                name=f"bolt_{k}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"instrument_colors", "machined_steel"} else "metal.brass_polished"),
            )

    # Clamp ears for drum_indexer or stepped_drum styles.
    if resolved.support_layout == "drum_indexer" or resolved.stage_body_style == "stepped_drum":
        ear_z = direction * height * 0.50
        for y_off, suffix in ((-0.048, "left"), (0.048, "right")):
            stage.visual(
                Box((0.060, 0.026, height * 0.72)),
                origin=Origin(xyz=(radius + 0.018, y_off, ear_z)),
                material=accent_mat,
                name=f"clamp_ear_{suffix}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"instrument_colors", "machined_steel"} else "metal.brass_polished"),
            )
        stage.visual(
            Cylinder(radius=0.006, length=0.110),
            origin=Origin(
                xyz=(radius + 0.030, 0.0, ear_z),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=accent_mat,
            name="clamp_screw", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"instrument_colors", "machined_steel"} else "metal.brass_polished"),
        )

    stage.inertial = Inertial.from_geometry(
        Cylinder(radius=radius, length=height),
        mass=max(0.5, radius * radius * height * 2700.0),
        origin=Origin(xyz=(0.0, 0.0, center_z)),
    )


# ---------------------------------------------------------------------------
# Public build entry points
# ---------------------------------------------------------------------------


def build_coaxial_rotary_stack(
    config: CoaxialRotaryStackConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or CoaxialRotaryStackConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-coaxial-stack-assets-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)
    palette = PALETTES[resolved.material_style]
    base_mat = model.material("stack_base", rgba=palette["base"])
    shaft_mat = model.material("stack_shaft", rgba=palette["shaft"])
    bearing_mat = model.material("stack_bearing", rgba=palette["bearing"])
    accent_mat = model.material("stack_index_marks", rgba=palette["accent"])
    stage_rgba = palette["stages"]
    stage_mats = [
        model.material(f"stage_{i}_finish", rgba=stage_rgba[i % len(stage_rgba)])
        for i in range(resolved.stage_count)
    ]

    base = model.part("base")
    _build_base(base, resolved, base_mat=base_mat, shaft_mat=shaft_mat, bearing_mat=bearing_mat)

    for i in range(resolved.stage_count):
        stage = model.part(f"stage_{i}")
        _build_stage(
            stage,
            resolved,
            i,
            assets=assets,
            stage_mat=stage_mats[i],
            accent_mat=accent_mat,
        )
        origin_xyz = (0.0, 0.0, resolved.stage_joint_z[i])
        if resolved.rotation_range_mode == "continuous":
            model.articulation(
                f"stage_{i}_rotate",
                ArticulationType.CONTINUOUS,
                parent=base,
                child=stage,
                origin=Origin(xyz=origin_xyz),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=20.0, velocity=2.5),
                meta=_joint_meta("continuous", (0.0, 0.0, 1.0), origin_xyz, "unbounded"),
            )
        else:
            upper = math.tau if resolved.rotation_range_mode == "full_turn_revolute" else math.pi
            lower = 0.0 if resolved.rotation_range_mode == "full_turn_revolute" else -math.pi
            model.articulation(
                f"stage_{i}_rotate",
                ArticulationType.REVOLUTE,
                parent=base,
                child=stage,
                origin=Origin(xyz=origin_xyz),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=40.0, velocity=2.0, lower=lower, upper=upper),
                meta=_joint_meta("revolute", (0.0, 0.0, 1.0), origin_xyz, (lower, upper)),
            )

    return model


def build_seeded_coaxial_rotary_stack(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_coaxial_rotary_stack(config_from_seed(seed), assets=assets)


def with_overrides(config: CoaxialRotaryStackConfig, **kwargs: object) -> CoaxialRotaryStackConfig:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def run_coaxial_rotary_stack_tests(
    object_model: ArticulatedObject, config: CoaxialRotaryStackConfig
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)

    stage_parts = [p for p in object_model.parts if p.name.startswith("stage_")]
    rotate_joints = [j for j in object_model.articulations if j.name.endswith("_rotate")]

    ctx.check(
        "stage_count matches config",
        len(stage_parts) == resolved.stage_count,
        details=f"parts={len(stage_parts)} expected={resolved.stage_count}",
    )
    ctx.check(
        "joint_count matches stage_count",
        len(rotate_joints) == resolved.stage_count,
        details=f"joints={len(rotate_joints)} expected={resolved.stage_count}",
    )

    for joint in rotate_joints:
        ctx.check(
            f"{joint.name} axis is vertical (0,0,1)",
            tuple(joint.axis) == (0.0, 0.0, 1.0),
            details=str(joint.axis),
        )
        ctx.check(
            f"{joint.name} origin is coaxial (xy≈0)",
            abs(joint.origin.xyz[0]) <= 0.001 and abs(joint.origin.xyz[1]) <= 0.001,
            details=str(joint.origin.xyz),
        )
        ctx.check(
            f"{joint.name} has required metadata keys",
            {"type", "axis", "origin", "range"}.issubset(joint.meta),
            details=str(joint.meta),
        )

    base_visuals = {v.name for v in object_model.get_part("base").visuals}
    ctx.check(
        "base has support contact visuals",
        any(
            token in str(name)
            for name in base_visuals
            for token in ("collar", "washer", "bearing", "land")
        ),
        details=str(base_visuals),
    )
    ctx.check("base has common_shaft", "common_shaft" in base_visuals, details=str(base_visuals))

    # Check that every stage seats at or very close to the bearing collar below it.
    # Skip for underslung layouts where stages hang below their joint origin.
    direction = _stage_direction(resolved)
    base_part = object_model.get_part("base")
    all_joint_poses = {j: 0.0 for j in rotate_joints}
    with ctx.pose(all_joint_poses):
        for i in range(resolved.stage_count):
            stage_part = object_model.get_part(f"stage_{i}")
            if resolved.stage_body_style == "annular_ring":
                stage_body_elem = "annular_outer_body"
            elif resolved.stage_body_style == "spoked_ring":
                stage_body_elem = "rim_ring"
            elif resolved.stage_body_style == "stepped_drum":
                stage_body_elem = "lower_drum_step"
            elif resolved.stage_body_style == "fixture_cup":
                stage_body_elem = "fixture_cup_rim"
            else:
                stage_body_elem = "stage_body"
            collar_suffix = i
            collar_candidates = [
                n
                for n in base_visuals
                if str(collar_suffix) in str(n)
                and ("collar" in str(n) or "washer" in str(n) or "bearing" in str(n))
            ]
            # The gap check is only valid when stages extend above their joint origin
            # (direction > 0).  For underslung layouts the stages hang below and the
            # z-ordering of stage vs. collar is inverted, so skip the check.
            if collar_candidates and direction > 0:
                ctx.expect_gap(
                    stage_part,
                    base_part,
                    axis="z",
                    positive_elem=stage_body_elem,
                    negative_elem=collar_candidates[0],
                    max_gap=0.003,
                    max_penetration=1e-4,
                    name=f"stage_{i} seats on collar_{i}",
                )

    # Rotation independence: rotating stage_0 should not move stage_1's world origin.
    if resolved.stage_count >= 2:
        s1 = object_model.get_part("stage_1")
        rest_pos_s1 = ctx.part_world_position(s1)
        with ctx.pose({rotate_joints[0]: 0.8}):
            moved_pos_s1 = ctx.part_world_position(s1)
        # The z coordinate of stage_1 should be unchanged; xy drift should be zero.
        ctx.check(
            "stage_1 xy stays fixed when only stage_0 rotates",
            rest_pos_s1 is not None
            and moved_pos_s1 is not None
            and abs(rest_pos_s1[0] - moved_pos_s1[0]) < 0.002
            and abs(rest_pos_s1[1] - moved_pos_s1[1]) < 0.002,
            details=f"rest={rest_pos_s1}, after_stage0_rotate={moved_pos_s1}",
        )

    return ctx.report()
