# SPDX-License-Identifier: Apache-2.0

"""Source-backed horizontal stone rotary querns on exposed timber supports.

The template composes local source variants as independent components. SourceMap
and TemplateDesign are authoring evidence only; seeded builds depend on this file
and the public SDK.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

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
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

SupportFrame = Literal[
    "straight_four_leg",
    "braced_four_leg",
    "splayed_trestle",
    "low_skid_cradle",
]
DischargeSystem = Literal["open_sloped_board", "bridge_supported_chute"]
RimProfile = Literal["rough_segmented_blocks", "fitted_stepped_voussoirs"]
RunnerProfile = Literal[
    "shallow_circular_funnel",
    "terraced_circular_feed",
    "faceted_polygonal_feed",
]
Drive = Literal["straight_socket_crank", "offset_counterweighted_crank"]
PaletteStyle = Literal["weathered_grey", "warm_granite", "cool_limestone"]


TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot(
            "support_frame",
            (
                "straight_four_leg",
                "braced_four_leg",
                "splayed_trestle",
                "low_skid_cradle",
            ),
        ),
        component_slot(
            "discharge_system",
            ("open_sloped_board", "bridge_supported_chute"),
        ),
        component_slot(
            "rim_profile",
            ("rough_segmented_blocks", "fitted_stepped_voussoirs"),
        ),
        component_slot(
            "runner_profile",
            (
                "shallow_circular_funnel",
                "terraced_circular_feed",
                "faceted_polygonal_feed",
            ),
        ),
        component_slot(
            "drive",
            ("straight_socket_crank", "offset_counterweighted_crank"),
        ),
        multiplicity_slot(
            "rim_segment_count",
            (10, 14, 18),
            item_slot="rim_profile",
        ),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "weathered_grey": {
        "lower_stone": (0.49, 0.52, 0.50, 1.0),
        "runner_stone": (0.66, 0.68, 0.65, 1.0),
        "wood": (0.55, 0.35, 0.19, 1.0),
        "endgrain": (0.70, 0.49, 0.27, 1.0),
        "metal": (0.16, 0.17, 0.15, 1.0),
    },
    "warm_granite": {
        "lower_stone": (0.50, 0.45, 0.39, 1.0),
        "runner_stone": (0.67, 0.60, 0.51, 1.0),
        "wood": (0.48, 0.27, 0.13, 1.0),
        "endgrain": (0.67, 0.43, 0.21, 1.0),
        "metal": (0.18, 0.15, 0.12, 1.0),
    },
    "cool_limestone": {
        "lower_stone": (0.48, 0.51, 0.53, 1.0),
        "runner_stone": (0.71, 0.72, 0.69, 1.0),
        "wood": (0.58, 0.39, 0.23, 1.0),
        "endgrain": (0.73, 0.53, 0.31, 1.0),
        "metal": (0.13, 0.15, 0.16, 1.0),
    },
}


@dataclass(frozen=True)
class Config:
    support_frame: SupportFrame = "straight_four_leg"
    discharge_system: DischargeSystem = "open_sloped_board"
    rim_profile: RimProfile = "rough_segmented_blocks"
    runner_profile: RunnerProfile = "shallow_circular_funnel"
    drive: Drive = "straight_socket_crank"
    rim_segment_count: int = 14
    quern_radius_m: float = 0.31
    support_height_scale: float = 1.0
    discharge_width_ratio: float = 0.56
    rim_height_ratio: float = 0.20
    runner_radius_ratio: float = 0.66
    feed_opening_ratio: float = 0.59
    crank_reach_ratio: float = 1.66
    palette_style: PaletteStyle = "weathered_grey"
    name: str = "manual_grain_mill1"


@dataclass(frozen=True)
class ResolvedConfig:
    support_frame: SupportFrame
    discharge_system: DischargeSystem
    rim_profile: RimProfile
    runner_profile: RunnerProfile
    drive: Drive
    rim_segment_count: int
    quern_radius_m: float
    support_height_scale: float
    discharge_width_ratio: float
    rim_height_ratio: float
    runner_radius_ratio: float
    feed_opening_ratio: float
    crank_reach_ratio: float
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    support_nominal_height: float
    grinding_surface_z: float
    lower_stone_bottom: float
    lower_body_height: float
    grinding_bed_height: float
    grinding_bed_radius: float
    runner_radius: float
    runner_thickness: float
    runner_eye_radius: float
    feed_mouth_radius: float
    pivot_bore_radius: float
    pivot_axle_radius: float
    bearing_outer_radius: float
    rim_inner_radius: float
    rim_outer_radius: float
    rim_height: float
    rim_base_z: float
    rim_angles: tuple[float, ...]
    rim_tangential_width: float
    outlet_width: float
    chute_width: float
    crank_reach: float
    crank_y_offset: float
    crank_arm_z: float
    crank_pin_z: float
    crank_arm_width: float
    grip_pin_radius: float
    grip_bore_radius: float
    grip_length: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x5145_524E)
    return Config(
        support_frame=choices["support_frame"],
        discharge_system=choices["discharge_system"],
        rim_profile=choices["rim_profile"],
        runner_profile=choices["runner_profile"],
        drive=choices["drive"],
        rim_segment_count=choices["rim_segment_count"],
        quern_radius_m=round(rng.uniform(0.28, 0.34), 4),
        support_height_scale=round(rng.uniform(0.90, 1.10), 4),
        discharge_width_ratio=round(rng.uniform(0.48, 0.66), 4),
        rim_height_ratio=round(rng.uniform(0.16, 0.24), 4),
        runner_radius_ratio=round(rng.uniform(0.62, 0.70), 4),
        feed_opening_ratio=round(rng.uniform(0.48, 0.70), 4),
        crank_reach_ratio=round(rng.uniform(1.55, 1.85), 4),
        palette_style=rng.choice(tuple(PALETTES)),
        name=f"manual_grain_mill1_seed_{int(seed)}",
    )


def _bounded(name: str, value: float, lower: float, upper: float) -> float:
    result = float(value)
    if not lower <= result <= upper:
        raise ValueError(f"{name} must be in [{lower}, {upper}], got {result}")
    return result


def _rim_segment_layout(
    count: int,
    mean_radius: float,
) -> tuple[tuple[float, ...], float]:
    if count not in (10, 14, 18):
        raise ValueError("rim_segment_count must be one of (10, 14, 18)")
    opening_half_angle = math.acos(0.90)
    usable_sweep = 2.0 * math.pi - 2.0 * opening_half_angle
    step = usable_sweep / count
    first = -math.pi / 2.0 + opening_half_angle + 0.5 * step
    angles = tuple(first + index * step for index in range(count))
    tangential_width = mean_radius * step * 0.78
    return angles, tangential_width


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "support_frame": config.support_frame,
            "discharge_system": config.discharge_system,
            "rim_profile": config.rim_profile,
            "runner_profile": config.runner_profile,
            "drive": config.drive,
            "rim_segment_count": config.rim_segment_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")

    quern_radius = _bounded("quern_radius_m", config.quern_radius_m, 0.28, 0.34)
    support_scale = _bounded("support_height_scale", config.support_height_scale, 0.90, 1.10)
    discharge_ratio = _bounded("discharge_width_ratio", config.discharge_width_ratio, 0.48, 0.66)
    rim_height_ratio = _bounded("rim_height_ratio", config.rim_height_ratio, 0.16, 0.24)
    runner_ratio = _bounded("runner_radius_ratio", config.runner_radius_ratio, 0.62, 0.70)
    feed_ratio = _bounded("feed_opening_ratio", config.feed_opening_ratio, 0.48, 0.70)
    crank_ratio = _bounded("crank_reach_ratio", config.crank_reach_ratio, 1.55, 1.85)

    support_nominal_height = 0.235 if config.support_frame == "low_skid_cradle" else 0.585
    grinding_surface_z = support_nominal_height * support_scale
    lower_body_height = 0.29 * quern_radius
    grinding_bed_height = 0.081 * quern_radius
    lower_stone_bottom = grinding_surface_z - lower_body_height - grinding_bed_height
    if lower_stone_bottom <= 0.075:
        raise ValueError("derived lower stone leaves no room for its timber support")

    runner_radius = quern_radius * runner_ratio
    runner_thickness = 0.58 * quern_radius
    runner_eye_radius = 0.087 * quern_radius
    feed_mouth_radius = runner_radius * feed_ratio
    grinding_bed_radius = runner_radius + 0.095 * quern_radius
    if grinding_bed_radius >= quern_radius - 0.012:
        raise ValueError("derived grinding bed exceeds the lower quern")

    pivot_bore_radius = 0.047 * quern_radius
    pivot_axle_radius = pivot_bore_radius - 0.0022
    bearing_outer_radius = runner_eye_radius - 0.0020
    if not pivot_axle_radius < pivot_bore_radius < bearing_outer_radius < runner_eye_radius:
        raise ValueError("central bore, bearing and runner eye derivation is invalid")

    rim_inner_radius = runner_radius + max(0.024, 0.08 * quern_radius)
    rim_outer_radius = quern_radius - 0.004
    if rim_inner_radius >= rim_outer_radius - 0.035:
        raise ValueError("rim has insufficient radial stone depth")
    rim_height = quern_radius * rim_height_ratio
    rim_base_z = grinding_surface_z - grinding_bed_height
    rim_angles, rim_tangential_width = _rim_segment_layout(
        config.rim_segment_count,
        0.5 * (rim_inner_radius + rim_outer_radius),
    )

    outlet_width = 0.34 * quern_radius
    chute_width = runner_radius * discharge_ratio
    crank_reach = runner_radius * crank_ratio
    crank_y_offset = -0.16 * quern_radius if config.drive == "offset_counterweighted_crank" else 0.0
    crank_arm_z = 0.60 * runner_thickness
    crank_pin_z = 0.76 * runner_thickness
    crank_arm_width = 0.17 * quern_radius
    grip_pin_radius = 0.0225 * quern_radius
    grip_bore_radius = grip_pin_radius + 0.0015
    grip_length = 0.68 * quern_radius
    if crank_arm_z - 0.07 * quern_radius <= rim_height:
        raise ValueError("derived crank arm does not clear the rim")

    return ResolvedConfig(
        support_frame=config.support_frame,
        discharge_system=config.discharge_system,
        rim_profile=config.rim_profile,
        runner_profile=config.runner_profile,
        drive=config.drive,
        rim_segment_count=config.rim_segment_count,
        quern_radius_m=quern_radius,
        support_height_scale=support_scale,
        discharge_width_ratio=discharge_ratio,
        rim_height_ratio=rim_height_ratio,
        runner_radius_ratio=runner_ratio,
        feed_opening_ratio=feed_ratio,
        crank_reach_ratio=crank_ratio,
        palette_style=config.palette_style,
        palette=PALETTES[config.palette_style],
        support_nominal_height=support_nominal_height,
        grinding_surface_z=grinding_surface_z,
        lower_stone_bottom=lower_stone_bottom,
        lower_body_height=lower_body_height,
        grinding_bed_height=grinding_bed_height,
        grinding_bed_radius=grinding_bed_radius,
        runner_radius=runner_radius,
        runner_thickness=runner_thickness,
        runner_eye_radius=runner_eye_radius,
        feed_mouth_radius=feed_mouth_radius,
        pivot_bore_radius=pivot_bore_radius,
        pivot_axle_radius=pivot_axle_radius,
        bearing_outer_radius=bearing_outer_radius,
        rim_inner_radius=rim_inner_radius,
        rim_outer_radius=rim_outer_radius,
        rim_height=rim_height,
        rim_base_z=rim_base_z,
        rim_angles=rim_angles,
        rim_tangential_width=rim_tangential_width,
        outlet_width=outlet_width,
        chute_width=chute_width,
        crank_reach=crank_reach,
        crank_y_offset=crank_y_offset,
        crank_arm_z=crank_arm_z,
        crank_pin_z=crank_pin_z,
        crank_arm_width=crank_arm_width,
        grip_pin_radius=grip_pin_radius,
        grip_bore_radius=grip_bore_radius,
        grip_length=grip_length,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("support_frame", config.support_frame),
        ("discharge_system", config.discharge_system),
        ("rim_profile", config.rim_profile),
        ("runner_profile", config.runner_profile),
        ("drive", config.drive),
        ("rim_segment_count", config.rim_segment_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, object]:
    return {
        key: model.material(f"{r.palette_style}_{key}", rgba=rgba)
        for key, rgba in r.palette.items()
    }


def _axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent: object,
    child: object,
    point: tuple[float, float, float],
    axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    radial: tuple[float, float, float] = (1.0, 0.0, 0.0),
    limits: MotionLimits,
) -> None:
    mate = mate_axes(
        AxisInterface(
            name=f"{name}_provider",
            point=point,
            axis=axis,
            radial=radial,
        ),
        AxisInterface(
            name=f"{name}_consumer",
            axis=axis,
            radial=radial,
        ),
    )
    model.articulation(
        name,
        ArticulationType.CONTINUOUS,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
    )
    register_interface_mate(model, name, mate)


def _ring_z(outer_radius: float, inner_radius: float, height: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(outer_radius).circle(inner_radius).extrude(height).clean()


def _ring_x(outer_radius: float, inner_radius: float, length: float) -> cq.Workplane:
    return (
        cq.Workplane("YZ")
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(0.5 * length, both=True)
        .clean()
    )


def _lower_quern_shape(r: ResolvedConfig) -> cq.Workplane:
    body = (
        cq.Workplane("XY")
        .circle(r.quern_radius_m)
        .extrude(r.lower_body_height)
        .translate((0.0, 0.0, r.lower_stone_bottom))
    )
    bed = (
        cq.Workplane("XY")
        .circle(r.grinding_bed_radius)
        .extrude(r.grinding_bed_height)
        .translate(
            (
                0.0,
                0.0,
                r.grinding_surface_z - r.grinding_bed_height,
            )
        )
    )
    spout = (
        cq.Workplane("XY")
        .polyline(
            [
                (-0.50 * r.outlet_width, -0.76 * r.quern_radius_m),
                (0.50 * r.outlet_width, -0.76 * r.quern_radius_m),
                (0.34 * r.outlet_width, -1.40 * r.quern_radius_m),
                (-0.34 * r.outlet_width, -1.40 * r.quern_radius_m),
            ]
        )
        .close()
        .extrude(0.50 * r.lower_body_height)
        .translate((0.0, 0.0, r.lower_stone_bottom + 0.38 * r.lower_body_height))
    )
    rear_notch = (
        cq.Workplane("XY")
        .box(
            0.72 * r.outlet_width,
            0.48 * r.quern_radius_m,
            r.lower_body_height + r.grinding_bed_height,
        )
        .translate(
            (
                0.0,
                -r.quern_radius_m,
                r.lower_stone_bottom + 0.70 * r.lower_body_height,
            )
        )
    )
    central_bore = (
        cq.Workplane("XY")
        .circle(r.pivot_bore_radius)
        .extrude(r.lower_body_height + r.grinding_bed_height + 0.02)
        .translate((0.0, 0.0, r.lower_stone_bottom - 0.01))
    )
    return body.union(bed).union(spout).cut(rear_notch).cut(central_bore).clean()


def _wood_grip_shape(r: ResolvedConfig) -> cq.Workplane:
    outer = (
        cq.Workplane("XY")
        .ellipse(0.078 * r.quern_radius_m, 0.068 * r.quern_radius_m)
        .workplane(offset=0.13 * r.grip_length)
        .ellipse(0.082 * r.quern_radius_m, 0.072 * r.quern_radius_m)
        .workplane(offset=0.67 * r.grip_length)
        .ellipse(0.061 * r.quern_radius_m, 0.055 * r.quern_radius_m)
        .workplane(offset=0.20 * r.grip_length)
        .ellipse(0.065 * r.quern_radius_m, 0.058 * r.quern_radius_m)
        .loft(ruled=True, combine=True)
    )
    pin_bore = cq.Workplane("XY").circle(r.grip_bore_radius).extrude(0.42 * r.grip_length)
    return outer.cut(pin_bore).clean()


def _timber_between(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    thickness: float,
) -> tuple[Box, Origin]:
    dx, dy, dz = (end[index] - start[index] for index in range(3))
    horizontal = math.hypot(dx, dy)
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    yaw = math.atan2(dy, dx)
    pitch = -math.atan2(dz, horizontal)
    midpoint = tuple((start[index] + end[index]) * 0.5 for index in range(3))
    return (
        Box((length, thickness, thickness)),
        Origin(xyz=midpoint, rpy=(0.0, pitch, yaw)),
    )


def _add_lower_quern_and_bearing(
    stand: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    stand.visual(
        mesh_from_cadquery(_lower_quern_shape(r), "lower_quern_with_real_bore"),
        material=mats["lower_stone"],
        name="support_frame__shared__lower_quern", material_class_id="stone.cut_sedimentary",
    )
    axle_length = r.lower_body_height + r.grinding_bed_height + 0.055
    stand.visual(
        Cylinder(radius=r.pivot_axle_radius, length=axle_length),
        origin=Origin(
            xyz=(
                0.0,
                0.0,
                r.grinding_surface_z - 0.5 * r.grinding_bed_height,
            )
        ),
        material=mats["metal"],
        name="support_frame__shared__pivot_axle", material_class_id="metal.steel_bare",
    )
    flange_height = 0.070 * r.quern_radius_m
    stand.visual(
        Cylinder(
            radius=r.pivot_bore_radius + 0.008,
            length=flange_height,
        ),
        origin=Origin(
            xyz=(
                0.0,
                0.0,
                r.lower_stone_bottom + 0.040 * r.quern_radius_m,
            )
        ),
        material=mats["metal"],
        name="support_frame__shared__pivot_base_flange", material_class_id="metal.cast_iron_bare",
    )
    bearing_height = 0.030 * r.quern_radius_m
    stand.visual(
        mesh_from_cadquery(
            _ring_z(r.bearing_outer_radius, r.pivot_bore_radius, bearing_height),
            "annular_pivot_bearing",
        ),
        origin=Origin(xyz=(0.0, 0.0, r.grinding_surface_z - 0.5 * bearing_height)),
        material=mats["metal"],
        name="support_frame__shared__pivot_bearing", material_class_id="metal.bronze_cast",
    )
    for index, angle in enumerate((45.0, 135.0, 225.0, 315.0)):
        theta = math.radians(angle)
        stand.visual(
            Cylinder(
                radius=0.022 * r.quern_radius_m,
                length=0.035 * r.quern_radius_m,
            ),
            origin=Origin(
                xyz=(
                    0.88 * r.quern_radius_m * math.cos(theta),
                    0.88 * r.quern_radius_m * math.sin(theta),
                    r.rim_base_z - 0.010 * r.quern_radius_m,
                )
            ),
            material=mats["metal"],
            name=f"support_frame__shared__rim_bolt_{index}", material_class_id="metal.steel_bare",
        )


def _support_frame_straight_four_leg_build(
    stand: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    _add_lower_quern_and_bearing(stand, r, mats)
    timber = 0.19 * r.quern_radius_m
    leg_x = 0.72 * r.quern_radius_m
    leg_y = 0.56 * r.quern_radius_m
    for index, (x, y) in enumerate(
        ((-leg_x, -leg_y), (leg_x, -leg_y), (-leg_x, leg_y), (leg_x, leg_y))
    ):
        stand.visual(
            Box((timber, timber, r.lower_stone_bottom)),
            origin=Origin(xyz=(x, y, 0.5 * r.lower_stone_bottom)),
            material=mats["wood"],
            name=f"support_frame__straight_four_leg__leg_{index}", material_class_id="wood.rustic_weathered",
        )
        stand.visual(
            Box((0.78 * timber, 0.78 * timber, 0.010 * r.quern_radius_m)),
            origin=Origin(xyz=(x, y, 0.005 * r.quern_radius_m)),
            material=mats["endgrain"],
            name=f"support_frame__straight_four_leg__foot_endgrain_{index}", material_class_id="wood.natural_generic",
        )
    rail_height = 0.145 * r.quern_radius_m
    for index, y in enumerate((-leg_y, leg_y)):
        stand.visual(
            Box((1.65 * r.quern_radius_m, timber, rail_height)),
            origin=Origin(xyz=(0.0, y, r.lower_stone_bottom - 0.5 * rail_height)),
            material=mats["wood"],
            name=f"support_frame__straight_four_leg__support_rail_{index}", material_class_id="wood.rustic_weathered",
        )


def _support_frame_braced_four_leg_build(
    stand: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    _support_frame_straight_four_leg_build(stand, r, mats)
    timber = 0.19 * r.quern_radius_m
    brace_thickness = 0.68 * timber
    leg_x = 0.72 * r.quern_radius_m
    leg_y = 0.56 * r.quern_radius_m
    for index, (x, y) in enumerate(
        ((-leg_x, -leg_y), (leg_x, -leg_y), (-leg_x, leg_y), (leg_x, leg_y))
    ):
        inward_x = math.copysign(0.33 * r.quern_radius_m, x)
        geometry, origin = _timber_between(
            (x, y, 0.62 * r.lower_stone_bottom),
            (inward_x, y, r.lower_stone_bottom - 0.11 * r.quern_radius_m),
            brace_thickness,
        )
        stand.visual(
            geometry,
            origin=origin,
            material=mats["wood"],
            name=f"support_frame__braced_four_leg__knee_brace_{index}", material_class_id="wood.rustic_weathered",
        )
        stand.visual(
            Cylinder(
                radius=0.026 * r.quern_radius_m,
                length=timber + 0.008,
            ),
            origin=Origin(
                xyz=(
                    0.5 * (x + inward_x),
                    y,
                    0.78 * r.lower_stone_bottom,
                ),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["endgrain"],
            name=f"support_frame__braced_four_leg__brace_peg_{index}", material_class_id="wood.natural_generic",
        )
    stand.visual(
        Box((timber, 1.30 * r.quern_radius_m, timber)),
        origin=Origin(
            xyz=(
                leg_x,
                0.0,
                max(0.13, 0.36 * r.lower_stone_bottom),
            )
        ),
        material=mats["wood"],
        name="support_frame__braced_four_leg__lower_stretcher", material_class_id="wood.rustic_weathered",
    )


def _splayed_leg_shape(
    x: float,
    side: float,
    top_y: float,
    bottom_y: float,
    top_z: float,
    thickness: float,
) -> cq.Workplane:
    half = 0.5 * thickness
    return (
        cq.Workplane("YZ")
        .polyline(
            [
                (side * bottom_y - half, 0.0),
                (side * bottom_y + half, 0.0),
                (side * top_y + half, top_z),
                (side * top_y - half, top_z),
            ]
        )
        .close()
        .extrude(0.5 * thickness, both=True)
        .translate((x, 0.0, 0.0))
        .clean()
    )


def _support_frame_splayed_trestle_build(
    stand: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    _add_lower_quern_and_bearing(stand, r, mats)
    timber = 0.19 * r.quern_radius_m
    leg_x = 0.72 * r.quern_radius_m
    top_y = 0.50 * r.quern_radius_m
    bottom_y = 0.88 * r.quern_radius_m
    for index, (x, side) in enumerate(((-leg_x, -1.0), (leg_x, -1.0), (-leg_x, 1.0), (leg_x, 1.0))):
        stand.visual(
            mesh_from_cadquery(
                _splayed_leg_shape(
                    x,
                    side,
                    top_y,
                    bottom_y,
                    r.lower_stone_bottom,
                    timber,
                ),
                f"splayed_trestle_leg_{index}",
            ),
            material=mats["wood"],
            name=f"support_frame__splayed_trestle__leg_{index}", material_class_id="wood.rustic_weathered",
        )
    head_height = 0.14 * r.quern_radius_m
    for index, x in enumerate((-leg_x, leg_x)):
        stand.visual(
            Box((1.15 * timber, 1.48 * r.quern_radius_m, head_height)),
            origin=Origin(xyz=(x, 0.0, r.lower_stone_bottom - 0.5 * head_height)),
            material=mats["endgrain"],
            name=f"support_frame__splayed_trestle__head_{index}", material_class_id="wood.natural_generic",
        )
        tie_z = 0.46 * r.lower_stone_bottom
        stand.visual(
            Box((timber, 1.45 * r.quern_radius_m, timber)),
            origin=Origin(xyz=(x, 0.0, tie_z)),
            material=mats["wood"],
            name=f"support_frame__splayed_trestle__tie_{index}", material_class_id="wood.rustic_weathered",
        )
    stand.visual(
        Box((1.46 * r.quern_radius_m, timber, timber)),
        origin=Origin(xyz=(0.0, 0.0, 0.46 * r.lower_stone_bottom)),
        material=mats["wood"],
        name="support_frame__splayed_trestle__central_stretcher", material_class_id="wood.rustic_weathered",
    )


def _support_frame_low_skid_cradle_build(
    stand: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    _add_lower_quern_and_bearing(stand, r, mats)
    skid_width = 0.20 * r.quern_radius_m
    skid_height = min(0.055, 0.46 * r.lower_stone_bottom)
    skid_x = 0.68 * r.quern_radius_m
    frame_depth = 2.45 * r.quern_radius_m
    frame_center_y = -0.35 * r.quern_radius_m
    for index, x in enumerate((-skid_x, skid_x)):
        stand.visual(
            Box((skid_width, frame_depth, skid_height)),
            origin=Origin(xyz=(x, frame_center_y, 0.5 * skid_height)),
            material=mats["wood"],
            name=f"support_frame__low_skid_cradle__skid_{index}", material_class_id="wood.rustic_weathered",
        )
    bearer_height = r.lower_stone_bottom - skid_height
    for index, y in enumerate((-0.52 * r.quern_radius_m, 0.52 * r.quern_radius_m)):
        stand.visual(
            Box((1.70 * r.quern_radius_m, 0.24 * r.quern_radius_m, bearer_height)),
            origin=Origin(xyz=(0.0, y, skid_height + 0.5 * bearer_height)),
            material=mats["wood"],
            name=f"support_frame__low_skid_cradle__stone_bearer_{index}", material_class_id="wood.rustic_weathered",
        )
        stand.visual(
            Box(
                (
                    1.74 * r.quern_radius_m,
                    0.27 * r.quern_radius_m,
                    0.018 * r.quern_radius_m,
                )
            ),
            origin=Origin(
                xyz=(
                    0.0,
                    y,
                    r.lower_stone_bottom - 0.009 * r.quern_radius_m,
                )
            ),
            material=mats["endgrain"],
            name=f"support_frame__low_skid_cradle__bearing_pad_{index}", material_class_id="wood.natural_generic",
        )


_SUPPORT_BUILDERS = {
    "straight_four_leg": _support_frame_straight_four_leg_build,
    "braced_four_leg": _support_frame_braced_four_leg_build,
    "splayed_trestle": _support_frame_splayed_trestle_build,
    "low_skid_cradle": _support_frame_low_skid_cradle_build,
}


def _chute_pose(
    r: ResolvedConfig,
    *,
    length_ratio: float,
) -> tuple[float, float, float, float, float]:
    length = length_ratio * r.quern_radius_m
    upper_y = -0.10 * r.quern_radius_m
    drop = min(
        0.50 * r.quern_radius_m,
        max(0.045, r.lower_stone_bottom - 0.035),
    )
    pitch = math.asin(min(0.75, drop / length))
    center_y = upper_y - 0.5 * length * math.cos(pitch)
    center_z = r.lower_stone_bottom - 0.5 * length * math.sin(pitch)
    lower_y = upper_y - length * math.cos(pitch)
    lower_z = r.lower_stone_bottom - length * math.sin(pitch)
    return length, pitch, center_y, center_z, 0.5 * (lower_y + upper_y) + 0.5 * lower_z


def _discharge_system_open_sloped_board_build(
    stand: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    length, pitch, center_y, center_z, _ = _chute_pose(r, length_ratio=1.28)
    stand.visual(
        Box((r.chute_width, length, 0.060 * r.quern_radius_m)),
        origin=Origin(xyz=(0.0, center_y, center_z), rpy=(pitch, 0.0, 0.0)),
        material=mats["wood"],
        name="discharge_system__open_sloped_board__board", material_class_id="wood.rustic_weathered",
    )
    stand.visual(
        Box(
            (
                0.82 * r.chute_width,
                0.075 * r.quern_radius_m,
                0.075 * r.quern_radius_m,
            )
        ),
        origin=Origin(
            xyz=(
                0.0,
                center_y - 0.49 * length * math.cos(pitch),
                center_z - 0.49 * length * math.sin(pitch),
            ),
            rpy=(pitch, 0.0, 0.0),
        ),
        material=mats["endgrain"],
        name="discharge_system__open_sloped_board__dressed_nose", material_class_id="wood.natural_generic",
    )


def _discharge_system_bridge_supported_chute_build(
    stand: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    length, pitch, center_y, center_z, _ = _chute_pose(r, length_ratio=1.18)
    board_thickness = 0.052 * r.quern_radius_m
    stand.visual(
        Box((r.chute_width, length, board_thickness)),
        origin=Origin(xyz=(0.0, center_y, center_z), rpy=(pitch, 0.0, 0.0)),
        material=mats["wood"],
        name="discharge_system__bridge_supported_chute__board", material_class_id="wood.rustic_weathered",
    )
    lip_thickness = 0.035 * r.quern_radius_m
    lip_height = 0.090 * r.quern_radius_m
    for index, x in enumerate(
        (-0.5 * r.chute_width + 0.5 * lip_thickness, 0.5 * r.chute_width - 0.5 * lip_thickness)
    ):
        stand.visual(
            Box((lip_thickness, length, lip_height)),
            origin=Origin(
                xyz=(x, center_y, center_z + 0.5 * lip_height),
                rpy=(pitch, 0.0, 0.0),
            ),
            material=mats["endgrain"],
            name=f"discharge_system__bridge_supported_chute__side_lip_{index}", material_class_id="wood.natural_generic",
        )
    bridge_y = center_y - 0.36 * length * math.cos(pitch)
    bridge_z = center_z - 0.36 * length * math.sin(pitch) - 0.035 * r.quern_radius_m
    stand.visual(
        Box(
            (
                max(1.42 * r.quern_radius_m, 1.25 * r.chute_width),
                0.16 * r.quern_radius_m,
                0.14 * r.quern_radius_m,
            )
        ),
        origin=Origin(xyz=(0.0, bridge_y, bridge_z)),
        material=mats["wood"],
        name="discharge_system__bridge_supported_chute__support_bridge", material_class_id="wood.rustic_weathered",
    )
    for index, x in enumerate((-0.58 * r.quern_radius_m, 0.58 * r.quern_radius_m)):
        stand.visual(
            Cylinder(
                radius=0.020 * r.quern_radius_m,
                length=0.17 * r.quern_radius_m,
            ),
            origin=Origin(
                xyz=(x, bridge_y, bridge_z),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["metal"],
            name=f"discharge_system__bridge_supported_chute__bridge_peg_{index}", material_class_id="metal.steel_bare",
        )


_DISCHARGE_BUILDERS = {
    "open_sloped_board": _discharge_system_open_sloped_board_build,
    "bridge_supported_chute": _discharge_system_bridge_supported_chute_build,
}


def _fitted_rim_segment_shape(
    radial_depth: float,
    tangential_width: float,
    height: float,
) -> cq.Workplane:
    half_depth = 0.5 * radial_depth
    half_bottom = 0.5 * tangential_width
    half_top = 0.42 * tangential_width
    return (
        cq.Workplane("XY")
        .polyline(
            [
                (-half_depth, -half_bottom),
                (half_depth, -0.95 * half_bottom),
                (half_depth, half_bottom),
                (-half_depth, 0.96 * half_bottom),
            ]
        )
        .close()
        .workplane(offset=0.72 * height)
        .polyline(
            [
                (-half_depth + 0.10 * radial_depth, -half_top),
                (half_depth - 0.07 * radial_depth, -0.94 * half_top),
                (half_depth - 0.08 * radial_depth, half_top),
                (-half_depth + 0.08 * radial_depth, 0.95 * half_top),
            ]
        )
        .close()
        .workplane(offset=0.28 * height)
        .polyline(
            [
                (-half_depth + 0.14 * radial_depth, -0.90 * half_top),
                (half_depth - 0.11 * radial_depth, -0.86 * half_top),
                (half_depth - 0.12 * radial_depth, 0.90 * half_top),
                (-half_depth + 0.12 * radial_depth, 0.88 * half_top),
            ]
        )
        .close()
        .loft(ruled=True, combine=True)
        .clean()
    )


def _rim_profile_rough_segmented_blocks_build(
    stand: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    mean_radius = 0.5 * (r.rim_inner_radius + r.rim_outer_radius)
    radial_depth = r.rim_outer_radius - r.rim_inner_radius
    for index, theta in enumerate(r.rim_angles):
        stand.visual(
            Box(
                (
                    r.rim_tangential_width,
                    0.92 * radial_depth,
                    r.rim_height,
                )
            ),
            origin=Origin(
                xyz=(
                    mean_radius * math.cos(theta),
                    mean_radius * math.sin(theta),
                    r.rim_base_z + 0.5 * r.rim_height,
                ),
                rpy=(0.0, 0.0, theta + math.pi / 2.0),
            ),
            material=mats["lower_stone"],
            name=f"rim_profile__rough_segmented_blocks__segment_{index}", material_class_id="stone.masonry_wall",
        )


def _rim_profile_fitted_stepped_voussoirs_build(
    stand: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    mean_radius = 0.5 * (r.rim_inner_radius + r.rim_outer_radius)
    radial_depth = r.rim_outer_radius - r.rim_inner_radius
    segment_mesh = mesh_from_cadquery(
        _fitted_rim_segment_shape(
            radial_depth,
            r.rim_tangential_width,
            0.78 * r.rim_height,
        ),
        "fitted_stepped_rim_voussoir",
    )
    for index, theta in enumerate(r.rim_angles):
        stand.visual(
            segment_mesh,
            origin=Origin(
                xyz=(
                    mean_radius * math.cos(theta),
                    mean_radius * math.sin(theta),
                    r.rim_base_z,
                ),
                rpy=(0.0, 0.0, theta),
            ),
            material=mats["lower_stone"],
            name=f"rim_profile__fitted_stepped_voussoirs__segment_{index}", material_class_id="stone.cut_sedimentary",
        )


_RIM_BUILDERS = {
    "rough_segmented_blocks": _rim_profile_rough_segmented_blocks_build,
    "fitted_stepped_voussoirs": _rim_profile_fitted_stepped_voussoirs_build,
}


def _runner_shape_shallow(r: ResolvedConfig) -> cq.Workplane:
    body = cq.Workplane("XY").circle(r.runner_radius).extrude(r.runner_thickness)
    throat = cq.Workplane("XY").circle(r.runner_eye_radius).extrude(r.runner_thickness + 0.01)
    funnel = (
        cq.Workplane("XY")
        .workplane(offset=0.46 * r.runner_thickness)
        .circle(1.06 * r.runner_eye_radius)
        .workplane(offset=0.54 * r.runner_thickness)
        .circle(r.feed_mouth_radius)
        .loft(ruled=True, combine=True)
    )
    return body.cut(throat).cut(funnel).clean()


def _runner_shape_terraced(r: ResolvedConfig) -> cq.Workplane:
    body = (
        cq.Workplane("XY")
        .circle(r.runner_radius)
        .workplane(offset=0.76 * r.runner_thickness)
        .circle(r.runner_radius)
        .workplane(offset=0.24 * r.runner_thickness)
        .circle(0.95 * r.runner_radius)
        .loft(combine=True)
    )
    sections = (
        (1.05 * r.runner_eye_radius, 0.42),
        (0.36 * r.feed_mouth_radius, 0.58),
        (0.36 * r.feed_mouth_radius, 0.64),
        (0.70 * r.feed_mouth_radius, 0.75),
        (0.70 * r.feed_mouth_radius, 0.81),
        (r.feed_mouth_radius, 1.02),
    )
    funnel = (
        cq.Workplane("XY")
        .workplane(offset=sections[0][1] * r.runner_thickness)
        .circle(sections[0][0])
    )
    previous = sections[0][1]
    for radius, height_ratio in sections[1:]:
        funnel = funnel.workplane(offset=(height_ratio - previous) * r.runner_thickness).circle(
            radius
        )
        previous = height_ratio
    shaped = body.cut(funnel.loft(ruled=True, combine=True))
    throat = cq.Workplane("XY").circle(r.runner_eye_radius).extrude(r.runner_thickness + 0.01)
    return shaped.cut(throat).clean()


def _runner_shape_faceted(r: ResolvedConfig) -> cq.Workplane:
    body = (
        cq.Workplane("XY")
        .polygon(14, 2.0 * r.runner_radius)
        .workplane(offset=0.25 * r.runner_thickness)
        .polygon(14, 2.03 * r.runner_radius)
        .workplane(offset=0.50 * r.runner_thickness)
        .polygon(14, 1.96 * r.runner_radius)
        .workplane(offset=0.25 * r.runner_thickness)
        .polygon(14, 1.82 * r.runner_radius)
        .loft(ruled=True, combine=True)
    )
    throat = cq.Workplane("XY").circle(r.runner_eye_radius).extrude(r.runner_thickness + 0.01)
    funnel = (
        cq.Workplane("XY")
        .workplane(offset=0.43 * r.runner_thickness)
        .polygon(14, 2.1 * r.runner_eye_radius)
        .workplane(offset=0.30 * r.runner_thickness)
        .polygon(14, 1.05 * r.feed_mouth_radius)
        .workplane(offset=0.29 * r.runner_thickness)
        .polygon(14, 2.0 * r.feed_mouth_radius)
        .loft(ruled=True, combine=True)
    )
    return body.cut(throat).cut(funnel).clean()


def _runner_profile_shallow_circular_funnel_build(
    runner: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    runner.visual(
        mesh_from_cadquery(_runner_shape_shallow(r), "shallow_circular_runner"),
        material=mats["runner_stone"],
        name="runner_profile__shallow_circular_funnel__stone", material_class_id="stone.cut_sedimentary",
    )


def _runner_profile_terraced_circular_feed_build(
    runner: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    runner.visual(
        mesh_from_cadquery(_runner_shape_terraced(r), "terraced_circular_runner"),
        material=mats["runner_stone"],
        name="runner_profile__terraced_circular_feed__stone", material_class_id="stone.cut_sedimentary",
    )


def _runner_profile_faceted_polygonal_feed_build(
    runner: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    runner.visual(
        mesh_from_cadquery(_runner_shape_faceted(r), "faceted_polygonal_runner"),
        material=mats["runner_stone"],
        name="runner_profile__faceted_polygonal_feed__stone", material_class_id="stone.cut_sedimentary",
    )


_RUNNER_BUILDERS = {
    "shallow_circular_funnel": _runner_profile_shallow_circular_funnel_build,
    "terraced_circular_feed": _runner_profile_terraced_circular_feed_build,
    "faceted_polygonal_feed": _runner_profile_faceted_polygonal_feed_build,
}


def _crank_arm_shape(
    length: float,
    width: float,
    height: float,
) -> cq.Workplane:
    half_length = 0.5 * length
    half_width = 0.5 * width
    bevel = min(0.18 * width, 0.12 * length)
    return (
        cq.Workplane("XY")
        .polyline(
            [
                (-half_length + bevel, -half_width),
                (half_length - bevel, -half_width),
                (half_length, -half_width + bevel),
                (half_length, half_width - bevel),
                (half_length - bevel, half_width),
                (-half_length + bevel, half_width),
                (-half_length, half_width - bevel),
                (-half_length, -half_width + bevel),
            ]
        )
        .close()
        .extrude(0.5 * height, both=True)
        .clean()
    )


def _counterweight_shape(r: ResolvedConfig) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .ellipse(0.15 * r.quern_radius_m, 0.11 * r.quern_radius_m)
        .workplane(offset=0.03 * r.quern_radius_m)
        .ellipse(0.16 * r.quern_radius_m, 0.12 * r.quern_radius_m)
        .workplane(offset=0.12 * r.quern_radius_m)
        .ellipse(0.16 * r.quern_radius_m, 0.12 * r.quern_radius_m)
        .workplane(offset=0.03 * r.quern_radius_m)
        .ellipse(0.14 * r.quern_radius_m, 0.10 * r.quern_radius_m)
        .loft(ruled=True, combine=True)
        .clean()
    )


def _add_detailed_crank_stack(
    runner: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    candidate: Drive,
) -> None:
    inner_x = -r.runner_radius + 0.020 * r.quern_radius_m
    outer_x = -r.crank_reach
    arm_length = abs(outer_x - inner_x)
    arm_center_x = 0.5 * (inner_x + outer_x)
    arm_height = 0.145 * r.quern_radius_m
    runner.visual(
        mesh_from_cadquery(
            _crank_arm_shape(arm_length, r.crank_arm_width, arm_height),
            f"{candidate}_dressed_crank_arm",
        ),
        origin=Origin(xyz=(arm_center_x, r.crank_y_offset, r.crank_arm_z)),
        material=mats["endgrain"],
        name=f"drive__{candidate}__crank_arm", material_class_id="wood.natural_generic",
    )
    socket_outer = 0.103 * r.quern_radius_m
    socket_inner = 0.052 * r.quern_radius_m
    runner.visual(
        mesh_from_cadquery(
            _ring_x(socket_outer, socket_inner, 0.16 * r.quern_radius_m),
            f"{candidate}_bored_crank_socket",
        ),
        origin=Origin(xyz=(inner_x, r.crank_y_offset, r.crank_arm_z)),
        material=mats["endgrain"],
        name=f"drive__{candidate}__bored_socket", material_class_id="wood.natural_generic",
    )
    washer_height = 0.022 * r.quern_radius_m
    runner.visual(
        mesh_from_cadquery(
            _ring_z(
                0.050 * r.quern_radius_m,
                r.grip_bore_radius,
                washer_height,
            ),
            f"{candidate}_grip_washer",
        ),
        origin=Origin(
            xyz=(
                outer_x,
                r.crank_y_offset,
                r.crank_pin_z - washer_height,
            )
        ),
        material=mats["metal"],
        name=f"drive__{candidate}__grip_washer", material_class_id="metal.steel_bare",
    )
    runner.visual(
        Cylinder(
            radius=r.grip_pin_radius,
            length=0.23 * r.quern_radius_m,
        ),
        origin=Origin(
            xyz=(
                outer_x,
                r.crank_y_offset,
                r.crank_pin_z + 0.055 * r.quern_radius_m,
            )
        ),
        material=mats["metal"],
        name=f"drive__{candidate}__grip_pin", material_class_id="metal.steel_bare",
    )
def _drive_straight_socket_crank_build(
    model: ArticulatedObject,
    runner: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> object:
    _add_detailed_crank_stack(
        runner,
        r,
        mats,
        candidate="straight_socket_crank",
    )
    grip = model.part("crank_grip", meta={"role": "crank_grip"})
    grip.visual(
        mesh_from_cadquery(_wood_grip_shape(r), "tapered_bored_crank_grip"),
        material=mats["wood"],
        name="drive__straight_socket_crank__wood_grip", material_class_id="wood.natural_generic",
    )
    _axis_joint(
        model,
        name="crank_spin",
        parent=runner,
        child=grip,
        point=(-r.crank_reach, r.crank_y_offset, r.crank_pin_z),
        limits=MotionLimits(effort=1.2, velocity=8.0),
    )
    return grip


def _drive_offset_counterweighted_crank_build(
    model: ArticulatedObject,
    runner: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> object:
    _add_detailed_crank_stack(
        runner,
        r,
        mats,
        candidate="offset_counterweighted_crank",
    )
    counter_x = 0.90 * r.crank_reach
    counter_y = -0.72 * r.crank_y_offset
    counter_length = math.hypot(counter_x - 0.35 * r.runner_radius, counter_y)
    runner.visual(
        Box(
            (
                counter_length,
                0.09 * r.quern_radius_m,
                0.07 * r.quern_radius_m,
            )
        ),
        origin=Origin(
            xyz=(
                0.5 * (counter_x + 0.35 * r.runner_radius),
                0.5 * counter_y,
                r.crank_arm_z,
            ),
            rpy=(0.0, 0.0, math.atan2(counter_y, counter_x)),
        ),
        material=mats["metal"],
        name="drive__offset_counterweighted_crank__counterweight_arm", material_class_id="metal.cast_iron_bare",
    )
    runner.visual(
        mesh_from_cadquery(
            _counterweight_shape(r),
            "forged_oval_counterweight",
        ),
        origin=Origin(
            xyz=(
                counter_x,
                counter_y,
                r.crank_arm_z - 0.09 * r.quern_radius_m,
            )
        ),
        material=mats["metal"],
        name="drive__offset_counterweighted_crank__counterweight", material_class_id="metal.cast_iron_bare",
    )
    grip = model.part("crank_grip", meta={"role": "crank_grip"})
    grip.visual(
        mesh_from_cadquery(_wood_grip_shape(r), "offset_tapered_bored_grip"),
        material=mats["wood"],
        name="drive__offset_counterweighted_crank__wood_grip", material_class_id="wood.natural_generic",
    )
    _axis_joint(
        model,
        name="crank_spin",
        parent=runner,
        child=grip,
        point=(-r.crank_reach, r.crank_y_offset, r.crank_pin_z),
        limits=MotionLimits(effort=1.2, velocity=8.0),
    )
    return grip


_DRIVE_BUILDERS = {
    "straight_socket_crank": _drive_straight_socket_crank_build,
    "offset_counterweighted_crank": _drive_offset_counterweighted_crank_build,
}


def build_manual_grain_mill1(
    config: Config,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "manual_grain_mill1",
            "slot_choices": slot_choices_for_config(r),
            "source_identity": (
                "horizontal stone rotary quern, exposed timber support, rear meal "
                "outlet, vertical runner axis and detailed side crank"
            ),
        },
    )
    mats = _materials(model, r)
    stand = model.part("stand", meta={"role": "support_frame"})
    _SUPPORT_BUILDERS[r.support_frame](stand, r, mats)
    _DISCHARGE_BUILDERS[r.discharge_system](stand, r, mats)
    _RIM_BUILDERS[r.rim_profile](stand, r, mats)

    runner = model.part("runner", meta={"role": "runner_stone"})
    _RUNNER_BUILDERS[r.runner_profile](runner, r, mats)
    sleeve_height = 0.08 * r.quern_radius_m
    runner.visual(
        mesh_from_cadquery(
            _ring_z(
                r.runner_eye_radius + 0.001,
                r.pivot_axle_radius + 0.0008,
                sleeve_height,
            ),
            "runner_pivot_sleeve",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * sleeve_height)),
        material=mats["metal"],
        name="runner_profile__shared__pivot_sleeve", material_class_id="metal.bronze_cast",
    )
    _axis_joint(
        model,
        name="grinding_shaft",
        parent=stand,
        child=runner,
        point=(0.0, 0.0, r.grinding_surface_z),
        limits=MotionLimits(effort=70.0, velocity=2.5),
    )
    _DRIVE_BUILDERS[r.drive](model, runner, r, mats)
    return model


def build_seeded_manual_grain_mill1(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_manual_grain_mill1(config_from_seed(seed), assets=assets)


def _parts_by_role(model: ArticulatedObject, role: str) -> list[object]:
    return [part for part in model.parts if part.meta.get("role") == role]


def _selected_visual_name(r: ResolvedConfig, slot: str, local: str) -> str:
    candidate = getattr(r, slot)
    return f"{slot}__{candidate}__{local}"


def run_manual_grain_mill1_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    supports = _parts_by_role(model, "support_frame")
    runners = _parts_by_role(model, "runner_stone")
    grips = _parts_by_role(model, "crank_grip")
    stand = supports[0] if supports else None
    runner = runners[0] if runners else None
    grip = grips[0] if grips else None
    grinding = model.get_articulation("grinding_shaft")
    crank_spin = model.get_articulation("crank_spin")

    ctx.check(
        "category_anchor: rotary stone quern identity",
        len(supports) == len(runners) == len(grips) == 1
        and stand is not None
        and runner is not None
        and grip is not None
        and grinding is not None
        and crank_spin is not None
        and grinding.parent == stand.name
        and grinding.child == runner.name
        and crank_spin.parent == runner.name
        and crank_spin.child == grip.name,
        details=(f"roles={{support:{len(supports)}, runner:{len(runners)}, grip:{len(grips)}}}"),
    )
    ctx.check(
        "category_anchor: supported coaxial grinding shaft",
        grinding is not None
        and grinding.articulation_type == ArticulationType.CONTINUOUS
        and tuple(grinding.axis) == (0.0, 0.0, 1.0)
        and stand is not None
        and stand.get_visual("support_frame__shared__lower_quern") is not None
        and stand.get_visual("support_frame__shared__pivot_axle") is not None
        and stand.get_visual("support_frame__shared__pivot_bearing") is not None
        and r.pivot_axle_radius < r.pivot_bore_radius
        and r.bearing_outer_radius < r.runner_eye_radius,
        details=(
            f"axle={r.pivot_axle_radius}, bore={r.pivot_bore_radius}, "
            f"bearing={r.bearing_outer_radius}, eye={r.runner_eye_radius}"
        ),
    )
    drive_prefix = f"drive__{r.drive}__"
    ctx.check(
        "category_anchor: source-detailed crank assembly",
        runner is not None
        and grip is not None
        and all(
            runner.get_visual(f"{drive_prefix}{name}") is not None
            for name in (
                "crank_arm",
                "bored_socket",
                "grip_washer",
                "grip_pin",
            )
        )
        and grip.get_visual(f"{drive_prefix}wood_grip") is not None
        and crank_spin is not None
        and tuple(crank_spin.axis) == (0.0, 0.0, 1.0)
        and r.grip_bore_radius > r.grip_pin_radius,
        details=f"drive={r.drive}",
    )

    support_requirements = {
        "straight_four_leg": ("leg_0", "support_rail_0"),
        "braced_four_leg": ("knee_brace_0", "brace_peg_0", "lower_stretcher"),
        "splayed_trestle": ("leg_0", "head_0", "tie_0", "central_stretcher"),
        "low_skid_cradle": ("skid_0", "stone_bearer_0", "bearing_pad_0"),
    }[r.support_frame]
    ctx.check(
        f"category_anchor: {r.support_frame} identity",
        stand is not None
        and all(
            stand.get_visual(f"support_frame__{r.support_frame}__{name}") is not None
            for name in support_requirements
        ),
        details=f"required={support_requirements}",
    )

    runner_visual = (
        None if runner is None else runner.get_visual(f"runner_profile__{r.runner_profile}__stone")
    )
    ctx.check(
        "category_anchor: real runner eye and feed profile",
        runner_visual is not None
        and r.runner_eye_radius < r.feed_mouth_radius < 0.80 * r.runner_radius
        and r.runner_radius + 0.020 < r.rim_inner_radius,
        details=(
            f"runner={r.runner_radius}, eye={r.runner_eye_radius}, "
            f"mouth={r.feed_mouth_radius}, rim_inner={r.rim_inner_radius}"
        ),
    )
    ctx.check(
        f"category_anchor: {r.runner_profile} identity",
        runner_visual is not None,
        details=f"runner_profile={r.runner_profile}",
    )
    ctx.check(
        f"category_anchor: {r.drive} identity",
        runner is not None
        and grip is not None
        and (
            "drive__offset_counterweighted_crank__counterweight"
            in {visual.name for visual in runner.visuals}
            if r.drive == "offset_counterweighted_crank"
            else "drive__offset_counterweighted_crank__counterweight"
            not in {visual.name for visual in runner.visuals}
        ),
        details=f"drive={r.drive}",
    )

    rim_prefix = f"rim_profile__{r.rim_profile}__segment_"
    rim_visuals = (
        []
        if stand is None
        else [
            visual
            for visual in stand.visuals
            if visual.name is not None and visual.name.startswith(rim_prefix)
        ]
    )
    ctx.check(
        "multiplicity emits exact rear-open rim segment count",
        len(rim_visuals) == r.rim_segment_count
        and {visual.name for visual in rim_visuals}
        == {f"{rim_prefix}{index}" for index in range(r.rim_segment_count)}
        and all(math.sin(theta) >= -0.90 - 1.0e-9 for theta in r.rim_angles),
        details=f"count={len(rim_visuals)}, angles={r.rim_angles}",
    )
    ctx.check(
        "lower quern outlet and selected discharge remain connected",
        stand is not None
        and stand.get_visual(f"discharge_system__{r.discharge_system}__board") is not None
        and (
            r.discharge_system == "open_sloped_board"
            or all(
                stand.get_visual(f"discharge_system__bridge_supported_chute__{name}") is not None
                for name in ("side_lip_0", "side_lip_1", "support_bridge")
            )
        ),
        details=f"discharge={r.discharge_system}",
    )
    ctx.check(
        "domain choices are recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )

    ctx.check(
        "runner seating and radial containment are derived from one quern interface",
        grinding is not None
        and tuple(grinding.origin.xyz) == (0.0, 0.0, r.grinding_surface_z)
        and r.runner_radius < r.grinding_bed_radius < r.quern_radius_m
        and r.runner_radius + 0.020 < r.rim_inner_radius,
        details=(
            f"joint_origin={None if grinding is None else grinding.origin.xyz}, "
            f"surface_z={r.grinding_surface_z}, runner={r.runner_radius}, "
            f"bed={r.grinding_bed_radius}, rim_inner={r.rim_inner_radius}"
        ),
    )
    ctx.check(
        "crank and bored grip clear the rim without an overlap allowance",
        crank_spin is not None
        and tuple(crank_spin.origin.xyz)
        == (-r.crank_reach, r.crank_y_offset, r.crank_pin_z)
        and r.grip_bore_radius > r.grip_pin_radius
        and r.crank_arm_z - 0.07 * r.quern_radius_m > r.rim_height,
        details=(
            f"grip_axis={None if crank_spin is None else crank_spin.origin.xyz}, "
            f"pin={r.grip_pin_radius}, bore={r.grip_bore_radius}, "
            f"arm_z={r.crank_arm_z}, rim_height={r.rim_height}"
        ),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "compact_low_faceted_fitted_counterweighted",
        {
            "support_frame": "low_skid_cradle",
            "discharge_system": "bridge_supported_chute",
            "rim_profile": "fitted_stepped_voussoirs",
            "runner_profile": "faceted_polygonal_feed",
            "drive": "offset_counterweighted_crank",
            "rim_segment_count": 18,
            "quern_radius_m": 0.28,
            "support_height_scale": 0.90,
            "discharge_width_ratio": 0.66,
            "rim_height_ratio": 0.24,
            "runner_radius_ratio": 0.70,
            "feed_opening_ratio": 0.70,
            "crank_reach_ratio": 1.55,
        },
        reason="compact low support, maximum rim density and largest rotating envelope",
    ),
    corner_case(
        "large_braced_rough_terraced_long_crank",
        {
            "support_frame": "braced_four_leg",
            "discharge_system": "open_sloped_board",
            "rim_profile": "rough_segmented_blocks",
            "runner_profile": "terraced_circular_feed",
            "drive": "straight_socket_crank",
            "rim_segment_count": 10,
            "quern_radius_m": 0.34,
            "support_height_scale": 1.10,
            "discharge_width_ratio": 0.48,
            "rim_height_ratio": 0.16,
            "runner_radius_ratio": 0.62,
            "feed_opening_ratio": 0.48,
            "crank_reach_ratio": 1.85,
        },
        reason="largest timber frame and longest crank with sparse source-like rim",
    ),
    corner_case(
        "splayed_max_runner_high_rim",
        {
            "support_frame": "splayed_trestle",
            "discharge_system": "bridge_supported_chute",
            "rim_profile": "fitted_stepped_voussoirs",
            "runner_profile": "shallow_circular_funnel",
            "drive": "offset_counterweighted_crank",
            "rim_segment_count": 14,
            "quern_radius_m": 0.31,
            "support_height_scale": 1.0,
            "discharge_width_ratio": 0.57,
            "rim_height_ratio": 0.24,
            "runner_radius_ratio": 0.70,
            "feed_opening_ratio": 0.60,
            "crank_reach_ratio": 1.70,
        },
        reason="splayed load path with the tightest runner-to-rim radial envelope",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_manual_grain_mill1",
    "build_seeded_manual_grain_mill1",
    "run_manual_grain_mill1_tests",
]
