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
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
)

FixtureLayout = Literal["track_spot", "branching_arm", "pull_down_pendant"]
MountStyle = Literal["round_canopy", "rectangular_track", "compact_ceiling_plate", "canopy_cup"]
ShadeStyle = Literal["bowl", "drum", "cylindrical_spot", "flat_diffuser"]
HeadProfile = Literal["short_barrel", "deep_barrel", "wide_bezel"]
ArmLayout = Literal["bilateral", "radial"]
ServiceLatchStyle = Literal["none", "spring_tab", "side_button"]
MaterialStyle = Literal["warm_brass", "matte_black", "brushed_nickel", "white_track"]

MATERIAL_PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "warm_brass": {
        "body": (0.86, 0.62, 0.28, 1.0),
        "hardware": (0.18, 0.15, 0.11, 1.0),
        "glass": (0.95, 0.88, 0.70, 0.38),
    },
    "matte_black": {
        "body": (0.015, 0.014, 0.013, 1.0),
        "hardware": (0.18, 0.18, 0.17, 1.0),
        "glass": (0.82, 0.90, 0.95, 0.35),
    },
    "brushed_nickel": {
        "body": (0.62, 0.64, 0.64, 1.0),
        "hardware": (0.34, 0.35, 0.36, 1.0),
        "glass": (0.90, 0.95, 1.0, 0.36),
    },
    "white_track": {
        "body": (0.88, 0.88, 0.84, 1.0),
        "hardware": (0.44, 0.45, 0.46, 1.0),
        "glass": (0.94, 0.96, 0.92, 0.40),
    },
}

_TRACK_SWIVEL_LIMIT = 0.20
_TRACK_CLEARANCE = 0.005
_TRACK_MIN_SLIDE = 0.020
_TRACK_YOKE_CROSS_RADIUS = 0.078


@dataclass(frozen=True)
class CeilingLightFixtureConfig:
    fixture_layout: FixtureLayout = "track_spot"
    mount_style: MountStyle = "rectangular_track"
    shade_style: ShadeStyle = "cylindrical_spot"
    head_profile: HeadProfile = "short_barrel"
    arm_layout: ArmLayout = "bilateral"
    head_count: int = 3
    arm_count: int = 3
    track_length: float = 1.2
    drop_length: float = 0.35
    diffuser_open_angle: float = 1.35
    tilt_range: tuple[float, float] = (-0.35, 0.95)
    service_latch_style: ServiceLatchStyle = "spring_tab"
    material_style: MaterialStyle = "matte_black"
    trim_density: int = 4
    name: str = "reference_ceiling_light_fixture_adjustable"


@dataclass(frozen=True)
class ResolvedCeilingLightFixtureConfig:
    fixture_layout: FixtureLayout
    mount_style: MountStyle
    shade_style: ShadeStyle
    head_profile: HeadProfile
    arm_layout: ArmLayout
    head_count: int
    arm_count: int
    track_length: float
    drop_length: float
    diffuser_open_angle: float
    tilt_range: tuple[float, float]
    service_latch_style: ServiceLatchStyle
    material_style: MaterialStyle
    trim_density: int
    slide_travel: float
    canopy_radius: float
    name: str


def _spot_head_longitudinal_radius(head_profile: HeadProfile) -> float:
    barrel_len = {"short_barrel": 0.135, "deep_barrel": 0.205, "wide_bezel": 0.155}[
        head_profile
    ]
    radius = 0.045 if head_profile != "wide_bezel" else 0.062
    return math.hypot(0.036 + barrel_len + 0.022, radius * 1.10) + 0.020


def _track_slot_half_extent(head_profile: HeadProfile) -> float:
    longitudinal = _spot_head_longitudinal_radius(head_profile)
    return (
        _TRACK_YOKE_CROSS_RADIUS * math.cos(_TRACK_SWIVEL_LIMIT)
        + longitudinal * math.sin(_TRACK_SWIVEL_LIMIT)
    )


def config_from_seed(seed: int) -> CeilingLightFixtureConfig:
    rng = random.Random(seed)
    layout: FixtureLayout = ("branching_arm", "pull_down_pendant", "branching_arm", "track_spot")[
        seed % 4
    ]
    mount_by_layout: dict[FixtureLayout, MountStyle] = {
        "track_spot": "rectangular_track",
        "branching_arm": "round_canopy",
        "pull_down_pendant": "canopy_cup",
    }
    shade_by_layout: dict[FixtureLayout, ShadeStyle] = {
        "track_spot": "cylindrical_spot",
        "branching_arm": "bowl",
        "pull_down_pendant": "drum",
    }
    return CeilingLightFixtureConfig(
        fixture_layout=layout,
        mount_style=mount_by_layout[layout],
        shade_style=shade_by_layout[layout],
        head_profile=rng.choice(("short_barrel", "deep_barrel", "wide_bezel")),
        arm_layout="radial" if layout == "branching_arm" else rng.choice(("bilateral", "radial")),
        head_count=rng.randint(1, 5),
        arm_count=rng.randint(2, 5),
        track_length=round(rng.uniform(0.70, 1.80), 3),
        drop_length=round(rng.uniform(0.10, 0.85), 3),
        diffuser_open_angle=round(rng.uniform(0.8, 1.6), 3),
        tilt_range=(round(rng.uniform(-0.60, -0.20), 3), round(rng.uniform(0.50, 1.10), 3)),
        service_latch_style=rng.choice(("none", "spring_tab", "side_button")),
        material_style=rng.choice(tuple(MATERIAL_PALETTES)),
        trim_density=rng.choice((0, 4, 6, 8)),
        name=f"seeded_ceiling_light_fixture_adjustable_{seed}",
    )


def resolve_config(config: CeilingLightFixtureConfig) -> ResolvedCeilingLightFixtureConfig:
    if config.fixture_layout not in {"track_spot", "branching_arm", "pull_down_pendant"}:
        raise ValueError(f"Unsupported fixture_layout: {config.fixture_layout}")
    if config.mount_style not in {
        "round_canopy",
        "rectangular_track",
        "compact_ceiling_plate",
        "canopy_cup",
    }:
        raise ValueError(f"Unsupported mount_style: {config.mount_style}")
    if config.shade_style not in {"bowl", "drum", "cylindrical_spot", "flat_diffuser"}:
        raise ValueError(f"Unsupported shade_style: {config.shade_style}")
    if config.head_profile not in {"short_barrel", "deep_barrel", "wide_bezel"}:
        raise ValueError(f"Unsupported head_profile: {config.head_profile}")
    if config.arm_layout not in {"bilateral", "radial"}:
        raise ValueError(f"Unsupported arm_layout: {config.arm_layout}")
    if config.service_latch_style not in {"none", "spring_tab", "side_button"}:
        raise ValueError(f"Unsupported service_latch_style: {config.service_latch_style}")
    if config.material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if not 1 <= config.head_count <= 6:
        raise ValueError("head_count must be in [1, 6]")
    if not 2 <= config.arm_count <= 6:
        raise ValueError("arm_count must be in [2, 6]")
    if not 0.7 <= config.track_length <= 2.4:
        raise ValueError("track_length must be in [0.7, 2.4]")
    if not 0.10 <= config.drop_length <= 0.85:
        raise ValueError("drop_length must be in [0.10, 0.85]")
    if not 0.8 <= config.diffuser_open_angle <= 1.6:
        raise ValueError("diffuser_open_angle must be in [0.8, 1.6]")
    if config.tilt_range[0] >= config.tilt_range[1]:
        raise ValueError("tilt_range lower must be less than upper")
    if not 0 <= config.trim_density <= 12:
        raise ValueError("trim_density must be in [0, 12]")

    if config.fixture_layout == "track_spot":
        occupied_half_width = _track_slot_half_extent(config.head_profile)
        minimum_head_spacing = 2.0 * (
            occupied_half_width + _TRACK_CLEARANCE + _TRACK_MIN_SLIDE
        )
        head_count = min(
            config.head_count, max(1, math.floor(config.track_length / minimum_head_spacing))
        )
    else:
        head_count = 1
    if config.fixture_layout == "branching_arm":
        arm_count = (
            min(config.arm_count, 2) if config.arm_layout == "bilateral" else config.arm_count
        )
    else:
        arm_count = 0
    mount_style = config.mount_style
    if config.fixture_layout == "track_spot" and mount_style != "rectangular_track":
        raise ValueError("track_spot requires mount_style='rectangular_track'")
    if config.fixture_layout == "pull_down_pendant" and mount_style == "rectangular_track":
        raise ValueError("pull_down_pendant cannot use rectangular_track")
    if config.fixture_layout == "track_spot":
        cell_half_width = config.track_length / (2.0 * head_count)
        slide_travel = min(
            config.track_length * 0.40,
            cell_half_width
            - _track_slot_half_extent(config.head_profile)
            - _TRACK_CLEARANCE,
        )
    else:
        slide_travel = min(config.track_length * 0.40, max(0.18, config.track_length - 0.28))
    canopy_radius = 0.18 if mount_style != "compact_ceiling_plate" else 0.13
    return ResolvedCeilingLightFixtureConfig(
        fixture_layout=config.fixture_layout,
        mount_style=mount_style,
        shade_style=config.shade_style,
        head_profile=config.head_profile,
        arm_layout=config.arm_layout,
        head_count=head_count,
        arm_count=arm_count,
        track_length=config.track_length,
        drop_length=config.drop_length,
        diffuser_open_angle=config.diffuser_open_angle,
        tilt_range=config.tilt_range,
        service_latch_style=config.service_latch_style,
        material_style=config.material_style,
        trim_density=config.trim_density,
        slide_travel=slide_travel,
        canopy_radius=canopy_radius,
        name=config.name,
    )


def _joint_meta(
    joint_type: str,
    axis: tuple[float, float, float],
    origin: tuple[float, float, float],
    joint_range: object,
) -> dict[str, object]:
    return {"type": joint_type, "axis": axis, "origin": origin, "range": joint_range}


def _branching_swing_limit(arm_count: int) -> float:
    shade_clearance_angle = 2.0 * math.asin((0.078 + 0.005) / 0.322)
    available_half_sector = (math.tau / arm_count - shade_clearance_angle) * 0.5
    return min(1.25, available_half_sector)


def _build_mount(
    part, resolved: ResolvedCeilingLightFixtureConfig, *, body_mat, accent_mat
) -> None:
    if resolved.mount_style == "rectangular_track":
        tl = resolved.track_length
        part.visual(
            Box((tl, 0.090, 0.035)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=body_mat,
            name="rail_body", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"matte_black", "brushed_nickel", "white_track"} else "metal.brass_polished"),
        )
        part.visual(
            Box((tl * 1.018, 0.122, 0.008)),
            origin=Origin(xyz=(0.0, 0.0, 0.0215)),
            material=accent_mat,
            name="ceiling_flange", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        part.visual(
            Box((0.022, 0.096, 0.040)),
            origin=Origin(xyz=(-tl * 0.5 - 0.011, 0.0, 0.0)),
            material=accent_mat,
            name="end_cap_0", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        part.visual(
            Box((0.022, 0.096, 0.040)),
            origin=Origin(xyz=(tl * 0.5 + 0.011, 0.0, 0.0)),
            material=accent_mat,
            name="end_cap_1", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        part.visual(
            Box((tl * 0.94, 0.012, 0.002)),
            origin=Origin(xyz=(0.0, 0.0, -0.0165)),
            material=accent_mat,
            name="center_recess", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        for side, y in enumerate((-0.026, 0.026)):
            part.visual(
                Box((tl * 0.90, 0.006, 0.002)),
                origin=Origin(xyz=(0.0, y, -0.0165)),
                material=body_mat,
                name=f"contact_strip_{side}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"matte_black", "brushed_nickel", "white_track"} else "metal.brass_polished"),
            )
        part.visual(
            Cylinder(radius=0.118, length=0.022),
            origin=Origin(xyz=(0.0, 0.0, 0.026)),
            material=body_mat,
            name="round_junction_canopy", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"matte_black", "brushed_nickel", "white_track"} else "metal.brass_polished"),
        )
        for i, x in enumerate((-tl * 0.43, tl * 0.43)):
            part.visual(
                Cylinder(radius=0.009, length=0.006),
                origin=Origin(xyz=(x * 0.84, 0.0, 0.0285)),
                material=accent_mat,
                name=f"track_mounting_screw_{i}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
            )
        return

    radius = resolved.canopy_radius
    part.visual(
        Cylinder(radius=radius, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, -0.009)),
        material=body_mat,
        name="ceiling_plate", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"matte_black", "brushed_nickel", "white_track"} else "metal.brass_polished"),
    )
    part.visual(
        Cylinder(radius=radius * 1.08, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, -0.001)),
        material=accent_mat,
        name="canopy_trim_ring", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )
    for i, angle in enumerate((math.pi / 4.0, math.pi * 5.0 / 4.0)):
        part.visual(
            Cylinder(radius=0.009, length=0.006),
            origin=Origin(
                xyz=(radius * 0.62 * math.cos(angle), radius * 0.62 * math.sin(angle), 0.007)
            ),
            material=accent_mat,
            name=f"canopy_mounting_screw_{i}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
    part.visual(
        Cylinder(radius=radius * 0.72, length=0.046),
        origin=Origin(xyz=(0.0, 0.0, -0.037)),
        material=accent_mat,
        name=resolved.mount_style, material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )


def _build_spot_head(
    part, resolved: ResolvedCeilingLightFixtureConfig, *, body_mat, accent_mat, glass_mat
) -> None:
    barrel_len = {"short_barrel": 0.135, "deep_barrel": 0.205, "wide_bezel": 0.155}[
        resolved.head_profile
    ]
    radius = 0.045 if resolved.head_profile != "wide_bezel" else 0.062
    head_clearance = 0.036

    part.visual(
        Cylinder(radius=radius * 0.72, length=0.030),
        origin=Origin(xyz=(0.024, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=accent_mat,
        name="rear_knuckle_socket", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )
    part.visual(
        Cylinder(radius=radius, length=barrel_len),
        origin=Origin(
            xyz=(head_clearance + barrel_len * 0.5, 0.0, 0.0),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=body_mat,
        name="spot_body", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"matte_black", "brushed_nickel", "white_track"} else "metal.brass_polished"),
    )
    for i, frac in enumerate((0.28, 0.50, 0.72)):
        part.visual(
            Cylinder(radius=radius * 1.04, length=0.006),
            origin=Origin(
                xyz=(head_clearance + barrel_len * frac, 0.0, 0.0),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=accent_mat,
            name=f"cooling_fin_{i}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
    part.visual(
        Cylinder(radius=radius * 1.10, length=0.020),
        origin=Origin(
            xyz=(head_clearance + barrel_len + 0.010, 0.0, 0.0),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=accent_mat,
        name="front_bezel", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )
    part.visual(
        Cylinder(radius=radius * 0.74, length=0.005),
        origin=Origin(
            xyz=(head_clearance + barrel_len + 0.022, 0.0, 0.0),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=glass_mat,
        name="warm_lens", material_class_id="glass.frosted_smooth",
    )
    part.visual(
        Box((0.026, 0.010, 0.016)),
        origin=Origin(xyz=(head_clearance + barrel_len * 0.35, -radius - 0.006, radius * 0.35)),
        material=accent_mat,
        name="rear_toggle_switch", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )


def _build_track_spot(
    model: ArticulatedObject,
    mount,
    resolved: ResolvedCeilingLightFixtureConfig,
    *,
    body_mat,
    accent_mat,
    glass_mat,
) -> None:
    spacing = resolved.track_length / max(1, resolved.head_count)
    rail_bottom_z = -0.0305
    for i in range(resolved.head_count):
        x0 = -resolved.track_length * 0.5 + spacing * (i + 0.5)

        carriage = model.part(f"carriage_{i}")
        carriage.visual(
            Box((0.10, 0.048, 0.026)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=accent_mat,
            name="runner_block", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        carriage.visual(
            Box((0.074, 0.090, 0.010)),
            origin=Origin(xyz=(0.0, 0.0, 0.006)),
            material=accent_mat,
            name="rail_capture_plate", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        for side, y in enumerate((-0.051, 0.051)):
            carriage.visual(
                Box((0.100, 0.012, 0.032)),
                origin=Origin(xyz=(0.0, y, 0.014)),
                material=accent_mat,
                name=f"rail_lip_{side}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
            )
        carriage.visual(
            Cylinder(radius=0.034, length=0.018),
            origin=Origin(xyz=(0.0, 0.0, -0.020)),
            material=accent_mat,
            name="swivel_socket", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        carriage.visual(
            Cylinder(radius=0.009, length=0.005),
            origin=Origin(xyz=(0.028, 0.0, 0.012)),
            material=accent_mat,
            name="carriage_lock_screw", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )

        model.articulation(
            f"rail_slide_{i}",
            ArticulationType.PRISMATIC,
            parent=mount,
            child=carriage,
            origin=Origin(xyz=(x0, 0.0, rail_bottom_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=20.0,
                velocity=0.35,
                lower=-resolved.slide_travel,
                upper=resolved.slide_travel,
            ),
            meta=_joint_meta(
                "prismatic",
                (1.0, 0.0, 0.0),
                (x0, 0.0, rail_bottom_z),
                (-resolved.slide_travel, resolved.slide_travel),
            ),
        )

        swivel_yoke = model.part(f"swivel_yoke_{i}")
        swivel_yoke.visual(
            Cylinder(radius=0.026, length=0.008),
            origin=Origin(xyz=(0.0, 0.0, -0.004)),
            material=accent_mat,
            name="turntable_disc", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        swivel_yoke.visual(
            Cylinder(radius=0.012, length=0.159),
            origin=Origin(xyz=(0.0, 0.0, -0.0875)),
            material=accent_mat,
            name="drop_stem", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        swivel_yoke.visual(
            Box((0.036, 0.150, 0.014)),
            origin=Origin(xyz=(0.0, 0.0, -0.145)),
            material=accent_mat,
            name="yoke_bridge", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        for side, y in enumerate((-0.072, 0.072)):
            swivel_yoke.visual(
                Box((0.026, 0.012, 0.156)),
                origin=Origin(xyz=(0.0, y, -0.230)),
                material=accent_mat,
                name=f"yoke_arm_{side}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
            )
        swivel_yoke.visual(
            Cylinder(radius=0.011, length=0.130),
            origin=Origin(xyz=(0.0, 0.0, -0.230), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=accent_mat,
            name="tilt_trunnion", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        for side, y in (("left", -0.066), ("right", 0.066)):
            swivel_yoke.visual(
                Cylinder(radius=0.012, length=0.008),
                origin=Origin(xyz=(0.0, y, -0.230), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=accent_mat,
                name=f"{side}_pivot_screw", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
            )

        model.articulation(
            f"carriage_swivel_{i}",
            ArticulationType.REVOLUTE,
            parent=carriage,
            child=swivel_yoke,
            origin=Origin(xyz=(0.0, 0.0, -0.029), rpy=(0.0, 0.0, math.pi / 2.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=6.0,
                velocity=2.4,
                lower=-_TRACK_SWIVEL_LIMIT,
                upper=_TRACK_SWIVEL_LIMIT,
            ),
            meta=_joint_meta(
                "revolute",
                (0.0, 0.0, 1.0),
                (0.0, 0.0, -0.029),
                (-_TRACK_SWIVEL_LIMIT, _TRACK_SWIVEL_LIMIT),
            ),
        )

        lamp_head = model.part(f"lamp_head_{i}")
        _build_spot_head(
            lamp_head, resolved, body_mat=body_mat, accent_mat=accent_mat, glass_mat=glass_mat
        )

        model.articulation(
            f"head_tilt_{i}",
            ArticulationType.REVOLUTE,
            parent=swivel_yoke,
            child=lamp_head,
            origin=Origin(xyz=(0.0, 0.0, -0.230)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(
                effort=3.0,
                velocity=1.5,
                lower=resolved.tilt_range[0],
                upper=resolved.tilt_range[1],
            ),
            meta=_joint_meta("revolute", (0.0, 1.0, 0.0), (0.0, 0.0, -0.230), resolved.tilt_range),
        )


def _build_branching_arm(
    model: ArticulatedObject,
    mount,
    resolved: ResolvedCeilingLightFixtureConfig,
    *,
    body_mat,
    accent_mat,
    glass_mat,
) -> None:
    arm_count = resolved.arm_count
    swing_limit = _branching_swing_limit(arm_count)
    mount.visual(
        Cylinder(radius=0.052, length=0.104),
        origin=Origin(xyz=(0.0, 0.0, -0.110)),
        material=accent_mat,
        name="central_hub", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )
    mount.visual(
        Cylinder(radius=0.060, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, -0.070)),
        material=accent_mat,
        name="hub_upper_trim", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )
    for i in range(arm_count):
        if resolved.arm_layout == "bilateral":
            angle = 0.0 if i % 2 == 0 else math.pi
        else:
            angle = math.tau * i / arm_count
        pivot = (0.056 * math.cos(angle), 0.056 * math.sin(angle), -0.112)
        mount.visual(
            Cylinder(radius=0.014, length=0.018),
            origin=Origin(xyz=pivot),
            material=accent_mat,
            name=f"arm_pivot_socket_{i}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        mount.visual(
            Box((0.015, 0.006, 0.002)),
            origin=Origin(
                xyz=(
                    pivot[0] + math.cos(angle) * 0.008,
                    pivot[1] + math.sin(angle) * 0.008,
                    pivot[2],
                ),
                rpy=(0.0, 0.0, angle),
            ),
            material=accent_mat,
            name=f"arm_pivot_key_{i}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        arm = model.part(f"arm_{i}")
        arm.visual(
            Cylinder(radius=0.012, length=0.314),
            origin=Origin(xyz=(0.168, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=accent_mat,
            name="arm_bar", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        arm.visual(
            Cylinder(radius=0.012, length=0.072),
            origin=Origin(xyz=(0.322, 0.0, -0.046)),
            material=accent_mat,
            name="drop_post", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        arm.visual(
            Box((0.034, 0.170, 0.018)),
            origin=Origin(xyz=(0.322, 0.0, -0.058)),
            material=accent_mat,
            name="tip_yoke_bridge", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        arm.visual(
            Box((0.018, 0.010, 0.100)),
            origin=Origin(xyz=(0.322, -0.080, -0.116)),
            material=accent_mat,
            name="tip_yoke_left_cheek", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        arm.visual(
            Box((0.018, 0.010, 0.100)),
            origin=Origin(xyz=(0.322, 0.080, -0.116)),
            material=accent_mat,
            name="tip_yoke_right_cheek", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        shade = model.part(f"shade_{i}")
        shade.visual(
            Cylinder(radius=0.014, length=0.062),
            origin=Origin(xyz=(0.0, 0.0, -0.010), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=accent_mat,
            name="tilt_socket", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        shade.visual(
            Cylinder(radius=0.056, length=0.054),
            origin=Origin(xyz=(0.0, 0.0, -0.038)),
            material=body_mat,
            name="spot_socket_collar", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"matte_black", "brushed_nickel", "white_track"} else "metal.brass_polished"),
        )
        shade.visual(
            Cylinder(radius=0.072, length=0.078),
            origin=Origin(xyz=(0.0, 0.0, -0.062)),
            material=glass_mat,
            name="bowl_shade", material_class_id="glass.frosted_smooth",
        )
        shade.visual(
            Cylinder(radius=0.078, length=0.012),
            origin=Origin(xyz=(0.0, 0.0, -0.104)),
            material=accent_mat,
            name="shade_bezel_ring", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        shade.visual(
            Sphere(radius=0.030),
            origin=Origin(xyz=(0.0, 0.0, -0.112)),
            material=glass_mat,
            name="globe_bulb", material_class_id="glass.frosted_smooth",
        )

        model.articulation(
            f"arm_swing_{i}",
            ArticulationType.REVOLUTE,
            parent=mount,
            child=arm,
            origin=Origin(xyz=pivot, rpy=(0.0, 0.0, angle)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=12.0,
                velocity=1.3,
                lower=-swing_limit,
                upper=swing_limit,
            ),
            meta=_joint_meta(
                "revolute", (0.0, 0.0, 1.0), pivot, (-swing_limit, swing_limit)
            ),
        )
        model.articulation(
            f"shade_tilt_{i}",
            ArticulationType.REVOLUTE,
            parent=arm,
            child=shade,
            origin=Origin(xyz=(0.322, 0.0, -0.084)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(
                effort=8.0,
                velocity=1.4,
                lower=resolved.tilt_range[0],
                upper=resolved.tilt_range[1],
            ),
            meta=_joint_meta(
                "revolute", (0.0, 1.0, 0.0), (0.322, 0.0, -0.084), resolved.tilt_range
            ),
        )


def _build_pull_down_pendant(
    model: ArticulatedObject,
    mount,
    resolved: ResolvedCeilingLightFixtureConfig,
    *,
    body_mat,
    accent_mat,
    glass_mat,
) -> None:
    cord_joint_z = -0.080
    mount.visual(
        Cylinder(radius=0.030, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, -0.070)),
        material=accent_mat,
        name="cord_outlet", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )
    mount.visual(
        Box((0.028, 0.050, 0.026)),
        origin=Origin(xyz=(0.044, 0.0, -0.086)),
        material=accent_mat,
        name="knurled_cord_grip", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )
    mount.visual(
        Box((0.006, 0.026, 0.070)),
        origin=Origin(xyz=(0.016, 0.0, cord_joint_z + 0.012)),
        material=accent_mat,
        name="fixed_cord_guide_sleeve", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )
    if resolved.service_latch_style == "side_button":
        button_origin = (resolved.canopy_radius * 0.82, 0.0, -0.040)
        guide_start_x = resolved.canopy_radius * 0.72 - 0.004
        guide_end_x = button_origin[0] + 0.040
        mount.visual(
            Box((guide_end_x - guide_start_x, 0.006, 0.028)),
            origin=Origin(
                xyz=((guide_start_x + guide_end_x) * 0.5, 0.017, button_origin[2])
            ),
            material=accent_mat,
            name="lock_pocket", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        lock = model.part("lock_button")
        lock.visual(
            Cylinder(radius=0.014, length=0.040),
            origin=Origin(xyz=(0.020, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=accent_mat,
            name="button_plunger", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
        )
        model.articulation(
            "lock_button_slide",
            ArticulationType.PRISMATIC,
            parent=mount,
            child=lock,
            origin=Origin(xyz=button_origin),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=0.05, lower=0.0, upper=0.012),
            meta=_joint_meta("prismatic", (-1.0, 0.0, 0.0), button_origin, (0.0, 0.012)),
        )

    cord_len = resolved.drop_length + 0.23
    mount.visual(
        Cylinder(radius=0.006, length=cord_len),
        origin=Origin(xyz=(0.0, 0.0, cord_joint_z - cord_len * 0.5)),
        material=accent_mat,
        name="fixed_hanging_cord", material_class_id="tech.cable_pipe_bundle",
    )
    mount.visual(
        Cylinder(radius=0.018, length=0.022),
        origin=Origin(xyz=(0.0, 0.0, cord_joint_z - (resolved.drop_length + 0.23))),
        material=accent_mat,
        name="swivel_cap", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )

    shade = model.part("shade")
    shade.visual(
        Cylinder(radius=0.022, length=0.056),
        origin=Origin(xyz=(0.0, 0.0, -0.028)),
        material=accent_mat,
        name="swivel_cup", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )
    shade.visual(
        Cylinder(radius=0.18, length=0.16),
        origin=Origin(xyz=(0.0, 0.0, -0.12)),
        material=body_mat,
        name="drum_shell", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"matte_black", "brushed_nickel", "white_track"} else "metal.brass_polished"),
    )
    shade.visual(
        Cylinder(radius=0.190, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, -0.046)),
        material=accent_mat,
        name="upper_shade_retainer", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )
    shade.visual(
        Cylinder(radius=0.190, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, -0.198)),
        material=accent_mat,
        name="lower_shade_bezel", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )
    shade.visual(
        Box((0.0278, 0.030, 0.032)),
        origin=Origin(xyz=(0.1939, 0.0, -0.112)),
        material=accent_mat,
        name="pull_chain_switch_boss", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )
    shade.visual(
        Sphere(radius=0.054),
        origin=Origin(xyz=(0.0, 0.0, -0.182)),
        material=glass_mat,
        name="globe_bulb", material_class_id="glass.frosted_smooth",
    )

    pull_chain = model.part("pull_chain")
    pull_chain.visual(
        Cylinder(radius=0.0022, length=0.142),
        origin=Origin(xyz=(0.0, 0.0, -0.071)),
        material=accent_mat,
        name="bead_chain", material_class_id="metal.mesh_chainmail",
    )
    pull_chain.visual(
        Sphere(radius=0.011),
        origin=Origin(xyz=(0.0, 0.0, -0.153)),
        material=accent_mat,
        name="teardrop_pull", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"warm_brass", "matte_black"} else "metal.brushed_silver"),
    )

    model.articulation(
        "shade_spin",
        ArticulationType.CONTINUOUS,
        parent=mount,
        child=shade,
        origin=Origin(xyz=(0.0, 0.0, cord_joint_z - (resolved.drop_length + 0.24))),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=5.0),
        meta=_joint_meta(
            "continuous",
            (0.0, 0.0, 1.0),
            (0.0, 0.0, cord_joint_z - (resolved.drop_length + 0.24)),
            "unbounded",
        ),
    )
    model.articulation(
        "pull_chain_swing",
        ArticulationType.CONTINUOUS,
        parent=shade,
        child=pull_chain,
        origin=Origin(xyz=(0.210, 0.0, -0.112)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.3, velocity=3.0),
        meta=_joint_meta("continuous", (1.0, 0.0, 0.0), (0.210, 0.0, -0.112), "unbounded"),
    )


def build_ceiling_light(
    config: CeilingLightFixtureConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or CeilingLightFixtureConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-ceiling-light-assets-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)
    palette = MATERIAL_PALETTES[resolved.material_style]
    body_mat = model.material("ceiling_light_body", rgba=palette["body"])
    accent_mat = model.material("ceiling_light_hardware", rgba=palette["hardware"])
    glass_mat = model.material("ceiling_light_glass", rgba=palette["glass"])
    mount = model.part("mount")
    _build_mount(mount, resolved, body_mat=body_mat, accent_mat=accent_mat)
    if resolved.fixture_layout == "track_spot":
        _build_track_spot(
            model, mount, resolved, body_mat=body_mat, accent_mat=accent_mat, glass_mat=glass_mat
        )
    elif resolved.fixture_layout == "branching_arm":
        _build_branching_arm(
            model, mount, resolved, body_mat=body_mat, accent_mat=accent_mat, glass_mat=glass_mat
        )
    else:
        _build_pull_down_pendant(
            model, mount, resolved, body_mat=body_mat, accent_mat=accent_mat, glass_mat=glass_mat
        )
    return model


def build_seeded_ceiling_light(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_ceiling_light(config_from_seed(seed), assets=assets)


def with_overrides(
    config: CeilingLightFixtureConfig, **kwargs: object
) -> CeilingLightFixtureConfig:
    return replace(config, **kwargs)


def run_ceiling_light_tests(
    object_model: ArticulatedObject, config: CeilingLightFixtureConfig
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {part.name for part in object_model.parts}
    ctx.check("identity_has_mount", "mount" in part_names, details=str(sorted(part_names)))
    ctx.check(
        "identity_has_light_output",
        any(
            any(
                v.name in {"diffuser", "warm_lens", "front_glass", "bowl_shade", "globe_bulb"}
                for v in p.visuals
            )
            for p in object_model.parts
        ),
        details="missing lens/diffuser/bulb",
    )
    for joint in object_model.articulations:
        ctx.check(
            f"{joint.name}_has_joint_metadata",
            {"type", "axis", "origin", "range"}.issubset(joint.meta),
            details=str(joint.meta),
        )
    if resolved.fixture_layout == "track_spot":
        rail_slides = [j for j in object_model.articulations if j.name.startswith("rail_slide_")]
        carriage_swivels = [
            j for j in object_model.articulations if j.name.startswith("carriage_swivel_")
        ]
        head_tilts = [j for j in object_model.articulations if j.name.startswith("head_tilt_")]
        ctx.check(
            "track_joint_count",
            len(rail_slides) == resolved.head_count
            and len(carriage_swivels) == resolved.head_count
            and len(head_tilts) == resolved.head_count,
            details=f"slides={len(rail_slides)}, swivels={len(carriage_swivels)}, tilts={len(head_tilts)}",
        )
        ctx.check(
            "track_slide_axis",
            all(tuple(j.axis) == (1.0, 0.0, 0.0) for j in rail_slides),
            details=str([j.axis for j in rail_slides]),
        )
        ctx.check(
            "swivel_axis_vertical",
            all(tuple(j.axis) == (0.0, 0.0, 1.0) for j in carriage_swivels),
            details=str([j.axis for j in carriage_swivels]),
        )
        ctx.check(
            "swivel_has_symmetric_stops",
            all(
                j.articulation_type == ArticulationType.REVOLUTE
                and j.motion_limits is not None
                and j.motion_limits.lower == -_TRACK_SWIVEL_LIMIT
                and j.motion_limits.upper == _TRACK_SWIVEL_LIMIT
                for j in carriage_swivels
            ),
            details=str(
                [(j.articulation_type, j.motion_limits) for j in carriage_swivels]
            ),
        )
        for i in range(resolved.head_count):
            slide = object_model.get_articulation(f"rail_slide_{i}")
            ctx.check(
                f"carriage_{i}_slides_along_rail",
                slide.articulation_type == ArticulationType.PRISMATIC
                and tuple(slide.axis) == (1.0, 0.0, 0.0),
                details=str(slide.axis),
            )
            tilt = object_model.get_articulation(f"head_tilt_{i}")
            ctx.check(
                f"head_{i}_tilt_revolute",
                tilt.articulation_type == ArticulationType.REVOLUTE,
                details=str(tilt.articulation_type),
            )
    elif resolved.fixture_layout == "branching_arm":
        ctx.check(
            "branch_arm_count",
            len([p for p in object_model.parts if p.name.startswith("arm_")]) == resolved.arm_count,
            details=str(part_names),
        )
        ctx.check(
            "branch_shade_count",
            len([j for j in object_model.articulations if j.name.startswith("shade_tilt_")])
            == resolved.arm_count,
            details=str([j.name for j in object_model.articulations]),
        )
    else:
        ctx.check(
            "cord_slide_removed",
            all(j.name != "cord_slide" for j in object_model.articulations),
            details=str([j.name for j in object_model.articulations]),
        )
        ctx.check(
            "shade_spin_exists",
            object_model.get_articulation("shade_spin").articulation_type
            == ArticulationType.CONTINUOUS,
            details="",
        )
    return ctx.report()
