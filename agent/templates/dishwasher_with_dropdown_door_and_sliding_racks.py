# SPDX-License-Identifier: Apache-2.0

"""Source-backed dishwasher generator with a dropdown door and sliding racks.

The template is the only runtime truth.  It samples compatible component families,
derives every interface from the selected tub, and builds ordinary category-specific
geometry without source-runtime or component-module imports.
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
    PlaneInterface,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mate_planes,
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

FrontFamily = Literal[
    "integrated_hidden",
    "pro_fascia",
    "black_glass",
    "commercial_pod",
    "retro_rounded",
]
RackGeometry = Literal["round_wire", "formed_square_wire", "glass_basket"]
RackAccessory = Literal["none", "sliding_caddy", "folding_mug_shelves"]
WashArmStyle = Literal["offset_paddle", "cross_jet"]
PaletteStyle = Literal["stainless", "graphite", "panel_white", "warm_retro"]


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "front_family",
            (
                "integrated_hidden",
                "pro_fascia",
                "black_glass",
                "commercial_pod",
                "retro_rounded",
            ),
        ),
        component_slot("rack_geometry", ("round_wire", "formed_square_wire", "glass_basket")),
        component_slot("rack_accessory", ("none", "sliding_caddy", "folding_mug_shelves")),
        component_slot("wash_arm", ("offset_paddle", "cross_jet")),
        multiplicity_slot(
            "rack_count",
            (2, 3),
            item_slot="rack_geometry",
        ),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "stainless": {
        "shell": (0.66, 0.69, 0.70, 1.0),
        "liner": (0.73, 0.76, 0.77, 1.0),
        "rack": (0.82, 0.84, 0.84, 1.0),
        "trim": (0.30, 0.32, 0.33, 1.0),
        "dark": (0.035, 0.040, 0.045, 1.0),
        "accent": (0.12, 0.32, 0.52, 1.0),
    },
    "graphite": {
        "shell": (0.14, 0.15, 0.16, 1.0),
        "liner": (0.56, 0.59, 0.60, 1.0),
        "rack": (0.72, 0.74, 0.75, 1.0),
        "trim": (0.22, 0.23, 0.24, 1.0),
        "dark": (0.012, 0.014, 0.017, 1.0),
        "accent": (0.78, 0.16, 0.08, 1.0),
    },
    "panel_white": {
        "shell": (0.88, 0.89, 0.87, 1.0),
        "liner": (0.70, 0.73, 0.74, 1.0),
        "rack": (0.36, 0.38, 0.39, 1.0),
        "trim": (0.56, 0.58, 0.59, 1.0),
        "dark": (0.055, 0.058, 0.060, 1.0),
        "accent": (0.08, 0.46, 0.28, 1.0),
    },
    "warm_retro": {
        "shell": (0.78, 0.70, 0.58, 1.0),
        "liner": (0.75, 0.73, 0.68, 1.0),
        "rack": (0.85, 0.83, 0.76, 1.0),
        "trim": (0.48, 0.50, 0.49, 1.0),
        "dark": (0.09, 0.075, 0.055, 1.0),
        "accent": (0.62, 0.12, 0.07, 1.0),
    },
}


@dataclass(frozen=True)
class Config:
    front_family: FrontFamily = "integrated_hidden"
    rack_geometry: RackGeometry = "round_wire"
    rack_accessory: RackAccessory = "none"
    wash_arm: WashArmStyle = "offset_paddle"
    rack_count: int = 2
    scale: float = 1.0
    width_bias: float = 1.0
    depth_bias: float = 1.0
    wire_scale: float = 1.0
    palette_style: PaletteStyle = "stainless"
    name: str = "dishwasher_with_dropdown_door_and_sliding_racks"


@dataclass(frozen=True)
class ResolvedConfig:
    front_family: FrontFamily
    rack_geometry: RackGeometry
    rack_accessory: RackAccessory
    wash_arm: WashArmStyle
    rack_count: int
    scale: float
    width_bias: float
    depth_bias: float
    wire_scale: float
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    body_width: float
    body_depth: float
    body_height: float
    wall: float
    front_y: float
    sill_z: float
    cavity_bottom: float
    cavity_top: float
    tub_width: float
    tub_depth: float
    rack_width: float
    rack_depth: float
    rack_heights: tuple[float, ...]
    rack_levels: tuple[float, ...]
    rack_travel: tuple[float, ...]
    rack_origin_y: float
    rail_x: float
    door_width: float
    door_height: float
    door_thickness: float
    lower_arm_z: float
    lower_arm_span: float
    upper_arm_span: float
    accessory_span: float
    name: str


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x4449_5348_5741_5348)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        front_family=choices["front_family"],
        rack_geometry=choices["rack_geometry"],
        rack_accessory=choices["rack_accessory"],
        wash_arm=choices["wash_arm"],
        rack_count=choices["rack_count"],
        scale=round(rng.uniform(0.94, 1.06), 4),
        width_bias=round(rng.uniform(0.96, 1.04), 4),
        depth_bias=round(rng.uniform(0.96, 1.04), 4),
        wire_scale=round(rng.uniform(0.90, 1.10), 4),
        palette_style=rng.choice(tuple(PALETTES)),
        name=f"dishwasher_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "front_family": config.front_family,
            "rack_geometry": config.rack_geometry,
            "rack_accessory": config.rack_accessory,
            "wash_arm": config.wash_arm,
            "rack_count": config.rack_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")

    scale = _clamp(config.scale, 0.94, 1.06)
    width_bias = _clamp(config.width_bias, 0.96, 1.04)
    depth_bias = _clamp(config.depth_bias, 0.96, 1.04)
    wire_scale = _clamp(config.wire_scale, 0.90, 1.10)
    nominal = {
        "integrated_hidden": (0.598, 0.595, 0.820),
        "pro_fascia": (0.600, 0.630, 0.860),
        "black_glass": (0.610, 0.620, 0.840),
        "commercial_pod": (0.620, 0.630, 0.820),
        "retro_rounded": (0.620, 0.620, 0.840),
    }[config.front_family]
    body_width = nominal[0] * scale * width_bias
    body_depth = nominal[1] * scale * depth_bias
    body_height = nominal[2] * scale
    wall = 0.012 * scale
    front_y = body_depth * 0.5
    sill_z = (0.105 if config.front_family == "commercial_pod" else 0.088) * scale
    cavity_bottom = sill_z + 0.036 * scale
    cavity_top = body_height - 0.038 * scale
    tub_width = body_width - 0.052 * scale
    tub_depth = body_depth - 0.058 * scale
    rack_width = tub_width - 0.050 * scale
    rack_depth = tub_depth - 0.075 * scale
    rack_origin_y = front_y - 0.050 * scale
    rail_x = rack_width * 0.5 + 0.015 * scale

    usable_height = cavity_top - cavity_bottom
    if config.rack_count == 2:
        fractions = (0.20, 0.62)
        height_factors = (0.135, 0.112)
        travel_factors = (0.78, 0.70)
    else:
        fractions = (0.16, 0.52, 0.84)
        height_factors = (0.128, 0.106, 0.050)
        travel_factors = (0.76, 0.68, 0.58)
    rack_levels = tuple(cavity_bottom + fraction * usable_height for fraction in fractions)
    rack_heights = tuple(value * scale for value in height_factors)
    base_travel = min(rack_depth * 0.80, body_depth - 0.115 * scale)
    rack_travel = tuple(base_travel * factor for factor in travel_factors)

    door_thickness = (0.050 if config.front_family == "commercial_pod" else 0.044) * scale
    door_width = body_width - 0.008 * scale
    door_top_clearance = 0.085 * scale if config.front_family == "commercial_pod" else 0.012 * scale
    door_height = body_height - sill_z - door_top_clearance
    lower_arm_z = cavity_bottom + 0.042 * scale
    lower_arm_span = min(tub_width * 0.70, tub_depth * 0.72)
    upper_arm_span = lower_arm_span * 0.82
    accessory_span = rack_width * 0.40

    return ResolvedConfig(
        front_family=config.front_family,
        rack_geometry=config.rack_geometry,
        rack_accessory=config.rack_accessory,
        wash_arm=config.wash_arm,
        rack_count=config.rack_count,
        scale=scale,
        width_bias=width_bias,
        depth_bias=depth_bias,
        wire_scale=wire_scale,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        body_width=body_width,
        body_depth=body_depth,
        body_height=body_height,
        wall=wall,
        front_y=front_y,
        sill_z=sill_z,
        cavity_bottom=cavity_bottom,
        cavity_top=cavity_top,
        tub_width=tub_width,
        tub_depth=tub_depth,
        rack_width=rack_width,
        rack_depth=rack_depth,
        rack_heights=rack_heights,
        rack_levels=rack_levels,
        rack_travel=rack_travel,
        rack_origin_y=rack_origin_y,
        rail_x=rail_x,
        door_width=door_width,
        door_height=door_height,
        door_thickness=door_thickness,
        lower_arm_z=lower_arm_z,
        lower_arm_span=lower_arm_span,
        upper_arm_span=upper_arm_span,
        accessory_span=accessory_span,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, object]:
    return {
        "front_family": config.front_family,
        "rack_geometry": config.rack_geometry,
        "rack_accessory": config.rack_accessory,
        "wash_arm": config.wash_arm,
        "rack_count": config.rack_count,
    }


def slot_choices_for_seed(seed: int) -> dict[str, object]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig):
    return {
        key: model.material(f"dishwasher_{r.palette_style}_{key}", rgba=rgba)
        for key, rgba in r.palette.items()
    }


def _rod_origin(center: tuple[float, float, float], axis: str) -> Origin:
    if axis == "x":
        return Origin(xyz=center, rpy=(0.0, math.pi / 2.0, 0.0))
    if axis == "y":
        return Origin(xyz=center, rpy=(math.pi / 2.0, 0.0, 0.0))
    return Origin(xyz=center)


def _rod(part, name: str, center, length: float, radius: float, axis: str, material) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=_rod_origin(center, axis),
        material=material,
        name=name, material_class_id="metal.stainless_matte",
    )


def _rounded_door_shape(
    width: float,
    depth: float,
    height: float,
    radius: float,
    *,
    bottom_clearance: float,
):
    panel_height = height - bottom_clearance
    return (
        cq.Workplane("XZ")
        .rect(width, panel_height)
        .extrude(depth * 0.5, both=True)
        .edges("|Y")
        .fillet(radius)
        .translate((0.0, 0.0, bottom_clearance + panel_height * 0.5))
    )


def _add_axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    articulation_type: ArticulationType,
    parent,
    child,
    provider: AxisInterface,
    consumer: AxisInterface,
    motion_limits: MotionLimits,
):
    mate = mate_axes(provider, consumer)
    joint = model.articulation(
        name,
        articulation_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=motion_limits,
    )
    register_interface_mate(model, name, mate)
    return joint


def _add_common_body(body, r: ResolvedConfig, mats) -> None:
    w, d, h, wall = r.body_width, r.body_depth, r.body_height, r.wall
    liner_wall = wall * 0.82
    shell_side = (w - r.tub_width) * 0.5
    rear_shell = 0.018 * r.scale
    top_shell = h - (r.cavity_top + liner_wall)
    body.visual(
        Box((shell_side, d, h)),
        origin=Origin(xyz=(-w * 0.5 + shell_side * 0.5, 0.0, h * 0.5)),
        material=mats["shell"],
        name=f"front_family__{r.front_family}__left_outer_panel", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless", "panel_white", "warm_retro"} else "metal.blackened_gunmetal"),
    )
    body.visual(
        Box((shell_side, d, h)),
        origin=Origin(xyz=(w * 0.5 - shell_side * 0.5, 0.0, h * 0.5)),
        material=mats["shell"],
        name=f"front_family__{r.front_family}__right_outer_panel", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless", "panel_white", "warm_retro"} else "metal.blackened_gunmetal"),
    )
    body.visual(
        Box((w - 2.0 * shell_side, rear_shell, h)),
        origin=Origin(xyz=(0.0, -d * 0.5 + rear_shell * 0.5, h * 0.5)),
        material=mats["shell"],
        name=f"front_family__{r.front_family}__rear_panel", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless", "panel_white", "warm_retro"} else "metal.blackened_gunmetal"),
    )
    body.visual(
        Box((w - 2.0 * shell_side, d - rear_shell, top_shell)),
        origin=Origin(xyz=(0.0, -rear_shell * 0.5, h - top_shell * 0.5)),
        material=mats["shell"],
        name=f"front_family__{r.front_family}__top_panel", material_class_id=("metal.stainless_matte" if r.palette_style in {"stainless", "panel_white", "warm_retro"} else "metal.blackened_gunmetal"),
    )

    liner_depth = r.tub_depth
    liner_center_y = r.rack_origin_y - liner_depth * 0.5 + 0.010 * r.scale
    for sign, label in ((-1.0, "left"), (1.0, "right")):
        body.visual(
            Box((liner_wall, liner_depth, r.cavity_top - r.cavity_bottom)),
            origin=Origin(
                xyz=(
                    sign * (r.tub_width * 0.5 - liner_wall * 0.5),
                    liner_center_y,
                    (r.cavity_top + r.cavity_bottom) * 0.5,
                )
            ),
            material=mats["liner"],
            name=f"front_family__{r.front_family}__tub_{label}_wall", material_class_id="metal.stainless_matte",
        )
    body.visual(
        Box((r.tub_width, liner_wall, r.cavity_top - r.cavity_bottom)),
        origin=Origin(
            xyz=(
                0.0,
                liner_center_y - liner_depth * 0.5 + liner_wall * 0.5,
                (r.cavity_top + r.cavity_bottom) * 0.5,
            )
        ),
        material=mats["liner"],
        name=f"front_family__{r.front_family}__tub_back_wall", material_class_id="metal.stainless_matte",
    )
    body.visual(
        Box((r.tub_width, liner_depth, liner_wall)),
        origin=Origin(xyz=(0.0, liner_center_y, r.cavity_bottom - liner_wall * 0.5)),
        material=mats["liner"],
        name=f"front_family__{r.front_family}__tub_floor", material_class_id="metal.stainless_matte",
    )
    body.visual(
        Box((r.tub_width, liner_depth, liner_wall)),
        origin=Origin(xyz=(0.0, liner_center_y, r.cavity_top + liner_wall * 0.5)),
        material=mats["liner"],
        name=f"front_family__{r.front_family}__tub_ceiling", material_class_id="metal.stainless_matte",
    )

    stile_w = 0.030 * r.scale
    opening_h = r.cavity_top - r.sill_z
    for sign, label in ((-1.0, "left"), (1.0, "right")):
        body.visual(
            Box((stile_w, 0.050 * r.scale, opening_h)),
            origin=Origin(
                xyz=(
                    sign * (w * 0.5 - stile_w * 0.5),
                    r.front_y - 0.025 * r.scale,
                    r.sill_z + opening_h * 0.5,
                )
            ),
            material=mats["trim"],
            name=f"front_family__{r.front_family}__front_{label}_stile", material_class_id="metal.brushed_silver",
        )
    body.visual(
        Box((w, 0.050 * r.scale, 0.045 * r.scale)),
        origin=Origin(xyz=(0.0, r.front_y - 0.025 * r.scale, h - 0.0225 * r.scale)),
        material=mats["trim"],
        name=f"front_family__{r.front_family}__front_header", material_class_id="metal.brushed_silver",
    )
    body.visual(
        Box((w, 0.050 * r.scale, r.cavity_bottom)),
        origin=Origin(xyz=(0.0, r.front_y - 0.025 * r.scale, r.cavity_bottom * 0.5)),
        material=mats["dark"],
        name=f"front_family__{r.front_family}__toe_kick", material_class_id="metal.paint_coated",
    )

    gasket_t = 0.008 * r.scale
    gasket_y = r.front_y - 0.009 * r.scale
    body.visual(
        Box((r.tub_width, gasket_t, gasket_t)),
        origin=Origin(xyz=(0.0, gasket_y, r.cavity_top)),
        material=mats["dark"],
        name=f"front_family__{r.front_family}__gasket_top", material_class_id="rubber.smooth_plain",
    )
    for sign, label in ((-1.0, "left"), (1.0, "right")):
        body.visual(
            Box((gasket_t, gasket_t, r.cavity_top - r.sill_z)),
            origin=Origin(
                xyz=(
                    sign * r.tub_width * 0.5,
                    gasket_y,
                    (r.cavity_top + r.sill_z) * 0.5,
                )
            ),
            material=mats["dark"],
            name=f"front_family__{r.front_family}__gasket_{label}", material_class_id="rubber.smooth_plain",
        )

    rail_len = r.rack_depth + 0.010 * r.scale
    rail_center_y = r.rack_origin_y - r.rack_depth * 0.5
    for level_index, level_z in enumerate(r.rack_levels):
        for sign, label in ((-1.0, "left"), (1.0, "right")):
            body.visual(
                Box((0.006 * r.scale, rail_len, 0.006 * r.scale)),
                origin=Origin(
                    xyz=(
                        sign * r.rail_x,
                        rail_center_y,
                        level_z - 0.008 * r.scale,
                    )
                ),
                material=mats["trim"],
                name=f"front_family__{r.front_family}__rail_{level_index}_{label}", material_class_id="metal.brushed_silver",
            )
            for roller_index, roller_y in enumerate(
                (r.rack_origin_y - 0.08 * r.scale, r.rack_origin_y - r.rack_depth + 0.08 * r.scale)
            ):
                body.visual(
                    Cylinder(radius=0.010 * r.scale, length=0.005 * r.scale),
                    origin=Origin(
                        xyz=(sign * r.rail_x, roller_y, level_z - 0.002 * r.scale),
                        rpy=(0.0, math.pi * 0.5, 0.0),
                    ),
                    material=mats["dark"],
                    name=(
                        f"front_family__{r.front_family}__rail_{level_index}_{label}_"
                        f"roller_{roller_index}"
                    ), material_class_id="plastic.opaque_glossy_molded",
                )

    body.visual(
        Cylinder(radius=0.065 * r.scale, length=0.014 * r.scale),
        origin=Origin(xyz=(0.0, liner_center_y, r.cavity_bottom + 0.004 * r.scale)),
        material=mats["trim"],
        name=f"front_family__{r.front_family}__sump_ring", material_class_id="metal.stainless_matte",
    )
    body.visual(
        Cylinder(radius=0.028 * r.scale, length=0.026 * r.scale),
        origin=Origin(xyz=(0.0, liner_center_y, r.lower_arm_z - 0.018 * r.scale)),
        material=mats["liner"],
        name=f"front_family__{r.front_family}__lower_spray_post", material_class_id="metal.stainless_matte",
    )
    body.visual(
        Box((0.044 * r.scale, r.tub_depth * 0.40, 0.026 * r.scale)),
        origin=Origin(
            xyz=(0.0, liner_center_y - r.tub_depth * 0.29, r.rack_levels[1] - 0.055 * r.scale)
        ),
        material=mats["liner"],
        name=f"front_family__{r.front_family}__upper_feed_duct", material_class_id="metal.stainless_matte",
    )

    hinge_y = r.front_y + r.door_thickness * 0.5
    socket_len = 0.055 * r.scale
    for sign, label in ((-1.0, "left"), (1.0, "right")):
        body.visual(
            Cylinder(radius=0.018 * r.scale, length=socket_len),
            origin=Origin(
                xyz=(sign * (r.door_width * 0.5 - socket_len * 0.5), hinge_y, r.sill_z),
                rpy=(0.0, math.pi * 0.5, 0.0),
            ),
            material=mats["trim"],
            name=f"front_family__{r.front_family}__hinge_socket_{label}", material_class_id="metal.brushed_silver",
        )
        body.visual(
            Box((socket_len, 0.010 * r.scale, 0.035 * r.scale)),
            origin=Origin(
                xyz=(
                    sign * (r.door_width * 0.5 - socket_len * 0.5),
                    r.front_y + 0.003 * r.scale,
                    r.sill_z,
                )
            ),
            material=mats["trim"],
            name=f"front_family__{r.front_family}__hinge_bracket_{label}", material_class_id="metal.brushed_silver",
        )


def _add_door_liner(door, r: ResolvedConfig, mats) -> None:
    inset_w = r.door_width - 0.074 * r.scale
    inset_h = r.door_height - 0.105 * r.scale
    inner_y = -r.door_thickness * 0.5 - 0.005 * r.scale
    door.visual(
        Box((inset_w, 0.008 * r.scale, inset_h)),
        origin=Origin(xyz=(0.0, inner_y, r.door_height * 0.49)),
        material=mats["liner"],
        name=f"front_family__{r.front_family}__door_inner_pan", material_class_id="metal.stainless_matte",
    )
    lip = 0.018 * r.scale
    for sign, label in ((-1.0, "left"), (1.0, "right")):
        door.visual(
            Box((lip, 0.018 * r.scale, inset_h)),
            origin=Origin(
                xyz=(
                    sign * (inset_w * 0.5 - lip * 0.5),
                    inner_y - 0.004 * r.scale,
                    r.door_height * 0.49,
                )
            ),
            material=mats["liner"],
            name=f"front_family__{r.front_family}__door_liner_{label}_lip", material_class_id="metal.stainless_matte",
        )
    door.visual(
        Box((inset_w, 0.018 * r.scale, lip)),
        origin=Origin(xyz=(0.0, inner_y - 0.004 * r.scale, r.door_height - 0.060 * r.scale)),
        material=mats["liner"],
        name=f"front_family__{r.front_family}__door_liner_top_lip", material_class_id="metal.stainless_matte",
    )
    door.visual(
        Box((0.165 * r.scale, 0.022 * r.scale, 0.105 * r.scale)),
        origin=Origin(xyz=(0.090 * r.scale, inner_y - 0.012 * r.scale, r.door_height * 0.43)),
        material=mats["trim"],
        name=f"front_family__{r.front_family}__detergent_dispenser", material_class_id="plastic.opaque_glossy_molded",
    )
    door.visual(
        Box((0.135 * r.scale, 0.005 * r.scale, 0.075 * r.scale)),
        origin=Origin(xyz=(0.090 * r.scale, inner_y - 0.025 * r.scale, r.door_height * 0.43)),
        material=mats["liner"],
        name=f"front_family__{r.front_family}__detergent_cover", material_class_id="plastic.opaque_glossy_molded",
    )
    door.visual(
        Cylinder(radius=0.030 * r.scale, length=0.012 * r.scale),
        origin=Origin(
            xyz=(-0.130 * r.scale, inner_y - 0.010 * r.scale, r.door_height * 0.32),
            rpy=(math.pi * 0.5, 0.0, 0.0),
        ),
        material=mats["accent"],
        name=f"front_family__{r.front_family}__rinse_aid_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    _rod(
        door,
        f"front_family__{r.front_family}__door_hinge_barrel",
        (0.0, 0.0, 0.0),
        r.door_width - 0.110 * r.scale,
        0.015 * r.scale,
        "x",
        mats["trim"],
    )
    for sign, label in ((-1.0, "left"), (1.0, "right")):
        door.visual(
            Box((0.050 * r.scale, 0.020 * r.scale, 0.060 * r.scale)),
            origin=Origin(
                xyz=(sign * (r.door_width * 0.5 - 0.080 * r.scale), 0.0, 0.030 * r.scale)
            ),
            material=mats["trim"],
            name=f"front_family__{r.front_family}__door_hinge_strap_{label}", material_class_id="metal.brushed_silver",
        )


def _add_fixed_dial(
    part,
    r: ResolvedConfig,
    mats,
    *,
    x: float,
    y: float,
    z: float,
    radius: float,
    prefix: str,
    support_y: float | None = None,
) -> None:
    if support_y is not None and y > support_y:
        _rod(
            part,
            f"{prefix}_mounting_shaft",
            (x, (support_y + y) * 0.5, z),
            y - support_y,
            radius * 0.28,
            "y",
            mats["trim"],
        )
    part.visual(
        Cylinder(radius=radius, length=0.018 * r.scale),
        origin=Origin(xyz=(x, y, z), rpy=(math.pi * 0.5, 0.0, 0.0)),
        material=mats["trim"],
        name=f"{prefix}_dial", material_class_id="metal.brushed_silver",
    )
    part.visual(
        Box((radius * 0.12, 0.008 * r.scale, radius * 0.72)),
        origin=Origin(xyz=(x, y + 0.010 * r.scale, z + radius * 0.22)),
        material=mats["dark"],
        name=f"{prefix}_dial_indicator", material_class_id="plastic.opaque_glossy_molded",
    )


def _add_fixed_buttons(
    part,
    r: ResolvedConfig,
    mats,
    *,
    positions,
    y: float,
    z: float,
    prefix: str,
    support_y: float | None = None,
) -> None:
    for index, x in enumerate(positions):
        if support_y is not None and y > support_y:
            part.visual(
                Box((0.012 * r.scale, y - support_y, 0.012 * r.scale)),
                origin=Origin(xyz=(x, (support_y + y) * 0.5, z)),
                material=mats["trim"],
                name=f"{prefix}_button_{index}_mount", material_class_id="metal.brushed_silver",
            )
        part.visual(
            Box((0.026 * r.scale, 0.012 * r.scale, 0.018 * r.scale)),
            origin=Origin(xyz=(x, y, z)),
            material=mats["accent"] if index == 0 else mats["dark"],
            name=f"{prefix}_button_{index}", material_class_id="plastic.opaque_glossy_molded",
        )


def _add_handle_standoffs(
    part,
    r: ResolvedConfig,
    mats,
    *,
    span: float,
    support_y: float,
    handle_y: float,
    z: float,
    radius: float,
    prefix: str,
) -> None:
    for index, sign in enumerate((-1.0, 1.0)):
        _rod(
            part,
            f"{prefix}_standoff_{index}",
            (sign * span * 0.42, (support_y + handle_y) * 0.5, z),
            handle_y - support_y,
            radius * 0.62,
            "y",
            mats["trim"],
        )


def _build_front_family(model, r: ResolvedConfig, mats, assets: AssetContext | None):
    body = model.part(f"front_family__{r.front_family}__body")
    _add_common_body(body, r, mats)
    door = model.part(f"front_family__{r.front_family}__door")
    radius = (0.040 if r.front_family == "retro_rounded" else 0.012) * r.scale
    panel_material = mats["dark"] if r.front_family == "black_glass" else mats["shell"]
    door.visual(
        mesh_from_cadquery(
            _rounded_door_shape(
                r.door_width,
                r.door_thickness,
                r.door_height,
                radius,
                bottom_clearance=0.042 * r.scale,
            ),
            f"dishwasher_{r.front_family}_door",
            assets=assets,
            tolerance=0.001,
        ),
        material=panel_material,
        name=f"front_family__{r.front_family}__outer_door_panel", material_class_id=("glass.smoked_tinted" if r.front_family == "black_glass" else "metal.stainless_matte"),
    )
    _add_door_liner(door, r, mats)
    outer_y = r.door_thickness * 0.5 + 0.008 * r.scale

    if r.front_family == "integrated_hidden":
        door.visual(
            Box((r.door_width - 0.055 * r.scale, 0.018 * r.scale, 0.060 * r.scale)),
            origin=Origin(xyz=(0.0, outer_y, r.door_height - 0.038 * r.scale)),
            material=mats["dark"],
            name="front_family__integrated_hidden__concealed_control_strip", material_class_id="tech.control_interface",
        )
        _add_fixed_buttons(
            door,
            r,
            mats,
            positions=(-0.090 * r.scale, -0.050 * r.scale, -0.010 * r.scale, 0.030 * r.scale),
            y=outer_y + 0.012 * r.scale,
            z=r.door_height - 0.038 * r.scale,
            prefix="front_family__integrated_hidden__controls",
            support_y=outer_y + 0.009 * r.scale,
        )
        door.visual(
            Box((0.340 * r.scale, 0.020 * r.scale, 0.026 * r.scale)),
            origin=Origin(
                xyz=(
                    0.0,
                    r.door_thickness * 0.5 + 0.010 * r.scale,
                    r.door_height - 0.105 * r.scale,
                )
            ),
            material=mats["trim"],
            name="front_family__integrated_hidden__recessed_handle", material_class_id="metal.brushed_silver",
        )
    elif r.front_family == "pro_fascia":
        fascia_z = r.door_height - 0.075 * r.scale
        door.visual(
            Box((r.door_width - 0.030 * r.scale, 0.024 * r.scale, 0.135 * r.scale)),
            origin=Origin(xyz=(0.0, outer_y, fascia_z)),
            material=mats["dark"],
            name="front_family__pro_fascia__control_fascia", material_class_id="tech.control_interface",
        )
        _add_fixed_dial(
            door,
            r,
            mats,
            x=-0.155 * r.scale,
            y=outer_y + 0.018 * r.scale,
            z=fascia_z,
            radius=0.043 * r.scale,
            prefix="front_family__pro_fascia__cycle",
            support_y=outer_y + 0.012 * r.scale,
        )
        _add_fixed_buttons(
            door,
            r,
            mats,
            positions=(0.050 * r.scale, 0.105 * r.scale),
            y=outer_y + 0.020 * r.scale,
            z=fascia_z,
            prefix="front_family__pro_fascia__controls",
            support_y=outer_y + 0.012 * r.scale,
        )
        handle_span = r.door_width * 0.72
        handle_y = outer_y + 0.020 * r.scale
        handle_z = r.door_height - 0.180 * r.scale
        _rod(
            door,
            "front_family__pro_fascia__bar_handle",
            (0.0, handle_y, handle_z),
            handle_span,
            0.012 * r.scale,
            "x",
            mats["trim"],
        )
        _add_handle_standoffs(
            door,
            r,
            mats,
            span=handle_span,
            support_y=r.door_thickness * 0.5,
            handle_y=handle_y,
            z=handle_z,
            radius=0.012 * r.scale,
            prefix="front_family__pro_fascia__bar_handle",
        )
    elif r.front_family == "black_glass":
        glass_surface_y = r.door_thickness * 0.5 + 0.008 * r.scale
        glass_height = r.door_height - 0.075 * r.scale
        door.visual(
            Box((r.door_width - 0.028 * r.scale, 0.008 * r.scale, glass_height)),
            origin=Origin(
                xyz=(
                    0.0,
                    r.door_thickness * 0.5 + 0.004 * r.scale,
                    0.042 * r.scale + glass_height * 0.5,
                )
            ),
            material=mats["dark"],
            name="front_family__black_glass__glass_skin", material_class_id="glass.smoked_tinted",
        )
        _add_fixed_dial(
            door,
            r,
            mats,
            x=-0.150 * r.scale,
            y=outer_y + 0.020 * r.scale,
            z=r.door_height - 0.075 * r.scale,
            radius=0.040 * r.scale,
            prefix="front_family__black_glass__cycle",
            support_y=glass_surface_y,
        )
        _add_fixed_buttons(
            door,
            r,
            mats,
            positions=(0.020 * r.scale, 0.070 * r.scale, 0.120 * r.scale),
            y=outer_y + 0.020 * r.scale,
            z=r.door_height - 0.075 * r.scale,
            prefix="front_family__black_glass__program",
            support_y=glass_surface_y,
        )
        handle_span = r.door_width * 0.78
        handle_y = outer_y + 0.025 * r.scale
        handle_z = r.door_height - 0.160 * r.scale
        _rod(
            door,
            "front_family__black_glass__full_width_handle",
            (0.0, handle_y, handle_z),
            handle_span,
            0.011 * r.scale,
            "x",
            mats["trim"],
        )
        _add_handle_standoffs(
            door,
            r,
            mats,
            span=handle_span,
            support_y=glass_surface_y,
            handle_y=handle_y,
            z=handle_z,
            radius=0.011 * r.scale,
            prefix="front_family__black_glass__full_width_handle",
        )
    elif r.front_family == "commercial_pod":
        pod_z = r.body_height - 0.040 * r.scale
        body.visual(
            Box((0.380 * r.scale, 0.078 * r.scale, 0.072 * r.scale)),
            origin=Origin(xyz=(0.0, r.front_y + 0.035 * r.scale, pod_z)),
            material=mats["dark"],
            name="front_family__commercial_pod__control_pod", material_class_id="tech.control_interface",
        )
        _add_fixed_dial(
            body,
            r,
            mats,
            x=0.110 * r.scale,
            y=r.front_y + 0.075 * r.scale,
            z=pod_z,
            radius=0.026 * r.scale,
            prefix="front_family__commercial_pod__timer",
            support_y=r.front_y + 0.074 * r.scale,
        )
        for index, x in enumerate((-0.105 * r.scale, -0.045 * r.scale)):
            body.visual(
                Box((0.030 * r.scale, 0.018 * r.scale, 0.030 * r.scale)),
                origin=Origin(xyz=(x, r.front_y + 0.075 * r.scale, pod_z)),
                material=mats["accent"],
                name=f"front_family__commercial_pod__rocker_{index}", material_class_id="plastic.opaque_glossy_molded",
            )
        handle_span = r.door_width * 0.70
        handle_y = outer_y + 0.020 * r.scale
        handle_z = r.door_height - 0.090 * r.scale
        _rod(
            door,
            "front_family__commercial_pod__heavy_handle",
            (0.0, handle_y, handle_z),
            handle_span,
            0.014 * r.scale,
            "x",
            mats["trim"],
        )
        _add_handle_standoffs(
            door,
            r,
            mats,
            span=handle_span,
            support_y=r.door_thickness * 0.5,
            handle_y=handle_y,
            z=handle_z,
            radius=0.014 * r.scale,
            prefix="front_family__commercial_pod__heavy_handle",
        )
    else:
        door.visual(
            Box((r.door_width - 0.045 * r.scale, 0.022 * r.scale, 0.125 * r.scale)),
            origin=Origin(xyz=(0.0, outer_y, r.door_height - 0.075 * r.scale)),
            material=mats["trim"],
            name="front_family__retro_rounded__rounded_fascia", material_class_id="metal.brushed_silver",
        )
        for index, x in enumerate((0.105 * r.scale, 0.175 * r.scale)):
            _add_fixed_dial(
                door,
                r,
                mats,
                x=x,
                y=outer_y + 0.018 * r.scale,
                z=r.door_height - 0.075 * r.scale,
                radius=(0.030 - index * 0.003) * r.scale,
                prefix=f"front_family__retro_rounded__dial_{index}",
                support_y=outer_y + 0.011 * r.scale,
            )
        _add_fixed_buttons(
            door,
            r,
            mats,
            positions=(-0.155 * r.scale, -0.105 * r.scale),
            y=outer_y + 0.018 * r.scale,
            z=r.door_height - 0.075 * r.scale,
            prefix="front_family__retro_rounded__controls",
            support_y=outer_y + 0.011 * r.scale,
        )
        handle_span = r.door_width * 0.66
        handle_y = outer_y + 0.022 * r.scale
        handle_z = r.door_height - 0.170 * r.scale
        _rod(
            door,
            "front_family__retro_rounded__chrome_handle",
            (0.0, handle_y, handle_z),
            handle_span,
            0.012 * r.scale,
            "x",
            mats["trim"],
        )
        _add_handle_standoffs(
            door,
            r,
            mats,
            span=handle_span,
            support_y=r.door_thickness * 0.5,
            handle_y=handle_y,
            z=handle_z,
            radius=0.012 * r.scale,
            prefix="front_family__retro_rounded__chrome_handle",
        )

    hinge_name = f"front_family__{r.front_family}__door_hinge"
    _add_axis_joint(
        model,
        name=hinge_name,
        articulation_type=ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        provider=AxisInterface(
            name=f"front_family.{r.front_family}.door_hinge_axis",
            point=(0.0, r.front_y + r.door_thickness * 0.5, r.sill_z),
            axis=(-1.0, 0.0, 0.0),
            radial=(0.0, 1.0, 0.0),
            radius=0.018 * r.scale,
        ),
        consumer=AxisInterface(
            name="door.bottom_hinge_axis",
            axis=(-1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=0.015 * r.scale,
        ),
        motion_limits=MotionLimits(
            effort=80.0,
            velocity=0.8,
            lower=-math.radians(87.0),
            upper=0.0,
        ),
    )
    return body, door


def _front_family_integrated_hidden_build(model, r, mats, assets):
    return _build_front_family(model, r, mats, assets)


def _front_family_pro_fascia_build(model, r, mats, assets):
    return _build_front_family(model, r, mats, assets)


def _front_family_black_glass_build(model, r, mats, assets):
    return _build_front_family(model, r, mats, assets)


def _front_family_commercial_pod_build(model, r, mats, assets):
    return _build_front_family(model, r, mats, assets)


def _front_family_retro_rounded_build(model, r, mats, assets):
    return _build_front_family(model, r, mats, assets)


_FRONT_BUILDERS = {
    "integrated_hidden": _front_family_integrated_hidden_build,
    "pro_fascia": _front_family_pro_fascia_build,
    "black_glass": _front_family_black_glass_build,
    "commercial_pod": _front_family_commercial_pod_build,
    "retro_rounded": _front_family_retro_rounded_build,
}


def _add_round_wire_rack(part, r: ResolvedConfig, mats, *, index: int, shallow: bool) -> None:
    width, depth, height = r.rack_width, r.rack_depth, r.rack_heights[index]
    radius = (0.0028 if shallow else 0.0034) * r.scale * r.wire_scale
    prefix = f"rack_geometry__round_wire__rack_{index}"
    for y, label in ((0.0, "front"), (-depth, "rear")):
        _rod(part, f"{prefix}__bottom_{label}", (0.0, y, radius), width, radius, "x", mats["rack"])
        _rod(part, f"{prefix}__top_{label}", (0.0, y, height), width, radius, "x", mats["rack"])
    for x, label in ((-width * 0.5, "left"), (width * 0.5, "right")):
        _rod(
            part,
            f"{prefix}__bottom_{label}",
            (x, -depth * 0.5, radius),
            depth,
            radius,
            "y",
            mats["rack"],
        )
        _rod(
            part,
            f"{prefix}__top_{label}",
            (x, -depth * 0.5, height),
            depth,
            radius,
            "y",
            mats["rack"],
        )
        for y_index, y in enumerate((0.0, -depth)):
            _rod(
                part,
                f"{prefix}__post_{label}_{y_index}",
                (x, y, height * 0.5),
                height,
                radius,
                "z",
                mats["rack"],
            )
    for grid_index, y in enumerate(
        (-depth * 0.18, -depth * 0.36, -depth * 0.54, -depth * 0.72, -depth * 0.90)
    ):
        _rod(
            part,
            f"{prefix}__cross_{grid_index}",
            (0.0, y, radius),
            width,
            radius * 0.62,
            "x",
            mats["rack"],
        )
    for grid_index, x in enumerate((-width * 0.36, -width * 0.18, 0.0, width * 0.18, width * 0.36)):
        _rod(
            part,
            f"{prefix}__foreaft_{grid_index}",
            (x, -depth * 0.5, radius),
            depth,
            radius * 0.62,
            "y",
            mats["rack"],
        )
    if not shallow:
        tine_h = height * 0.55
        for row, y in enumerate((-depth * 0.36, -depth * 0.72)):
            for col, x in enumerate(
                (-width * 0.36, -width * 0.18, 0.0, width * 0.18, width * 0.36)
            ):
                _rod(
                    part,
                    f"{prefix}__tine_{row}_{col}",
                    (x, y, tine_h * 0.5),
                    tine_h,
                    radius * 0.58,
                    "z",
                    mats["rack"],
                )


def _add_square_wire_rack(
    part, r: ResolvedConfig, mats, *, index: int, shallow: bool, glass: bool
) -> None:
    width, depth, height = r.rack_width, r.rack_depth, r.rack_heights[index]
    wire = (0.0055 if glass else 0.0048) * r.scale * r.wire_scale
    style = "glass_basket" if glass else "formed_square_wire"
    prefix = f"rack_geometry__{style}__rack_{index}"
    for y, label in ((0.0, "front"), (-depth, "rear")):
        part.visual(
            Box((width, wire, wire)),
            origin=Origin(xyz=(0.0, y, wire * 0.5)),
            material=mats["rack"],
            name=f"{prefix}__bottom_{label}", material_class_id="metal.stainless_matte",
        )
        part.visual(
            Box((width, wire, wire)),
            origin=Origin(xyz=(0.0, y, height)),
            material=mats["rack"],
            name=f"{prefix}__top_{label}", material_class_id="metal.stainless_matte",
        )
    for x, label in ((-width * 0.5, "left"), (width * 0.5, "right")):
        part.visual(
            Box((wire, depth, wire)),
            origin=Origin(xyz=(x, -depth * 0.5, wire * 0.5)),
            material=mats["rack"],
            name=f"{prefix}__bottom_{label}", material_class_id="metal.stainless_matte",
        )
        part.visual(
            Box((wire, depth, wire)),
            origin=Origin(xyz=(x, -depth * 0.5, height)),
            material=mats["rack"],
            name=f"{prefix}__top_{label}", material_class_id="metal.stainless_matte",
        )
        for end, y in enumerate((0.0, -depth)):
            part.visual(
                Box((wire, wire, height)),
                origin=Origin(xyz=(x, y, height * 0.5)),
                material=mats["rack"],
                name=f"{prefix}__post_{label}_{end}", material_class_id="metal.stainless_matte",
            )
    grid_count = 7 if glass else 5
    for grid_index in range(grid_count):
        y = -depth * (grid_index + 1) / (grid_count + 1)
        part.visual(
            Box((width, wire * 0.70, wire)),
            origin=Origin(xyz=(0.0, y, wire * 0.5)),
            material=mats["rack"],
            name=f"{prefix}__cross_{grid_index}", material_class_id="metal.stainless_matte",
        )
    for grid_index in range(grid_count):
        x = -width * 0.40 + width * 0.80 * grid_index / max(1, grid_count - 1)
        part.visual(
            Box((wire * 0.70, depth, wire)),
            origin=Origin(xyz=(x, -depth * 0.5, wire * 0.5)),
            material=mats["rack"],
            name=f"{prefix}__foreaft_{grid_index}", material_class_id="metal.stainless_matte",
        )
    if not shallow and not glass:
        for row, y in enumerate((-depth / 3.0, -depth * 2.0 / 3.0)):
            for col, x in enumerate(
                (-width * 0.40, -width * 0.20, 0.0, width * 0.20, width * 0.40)
            ):
                part.visual(
                    Box((wire * 0.70, wire * 0.70, height * 0.54)),
                    origin=Origin(xyz=(x, y, height * 0.27)),
                    material=mats["rack"],
                    name=f"{prefix}__tine_{row}_{col}", material_class_id="metal.stainless_matte",
                )


def _build_rack_part(model, body, r: ResolvedConfig, mats, *, index: int):
    shallow = index == 2
    part = model.part(f"rack_geometry__{r.rack_geometry}__rack_{index}")
    if r.rack_geometry == "round_wire":
        _add_round_wire_rack(part, r, mats, index=index, shallow=shallow)
    else:
        _add_square_wire_rack(
            part,
            r,
            mats,
            index=index,
            shallow=shallow,
            glass=r.rack_geometry == "glass_basket",
        )
    # Each runner spans from the basket side frame to the fixed guide.  Both
    # contacts are exact, so it is a real load path rather than floating trim.
    if r.rack_geometry == "round_wire":
        frame_outer = (0.0028 if shallow else 0.0034) * r.scale * r.wire_scale
    elif r.rack_geometry == "glass_basket":
        frame_outer = 0.00275 * r.scale * r.wire_scale
    else:
        frame_outer = 0.0024 * r.scale * r.wire_scale
    runner_width = 0.012 * r.scale - frame_outer
    runner_x = r.rack_width * 0.5 + frame_outer + runner_width * 0.5
    for sign, label in ((-1.0, "left"), (1.0, "right")):
        part.visual(
            Box((runner_width, r.rack_depth * 0.88, 0.010 * r.scale)),
            origin=Origin(xyz=(sign * runner_x, -r.rack_depth * 0.52, 0.0)),
            material=mats["trim"],
            name=f"rack_geometry__{r.rack_geometry}__rack_{index}__runner_{label}", material_class_id="metal.brushed_silver",
        )
    if not shallow:
        pull_span = r.rack_width * 0.52
        pull_y = 0.010 * r.scale
        pull_z = r.rack_heights[index] + 0.018 * r.scale
        _rod(
            part,
            f"rack_geometry__{r.rack_geometry}__rack_{index}__front_pull",
            (0.0, pull_y, pull_z),
            pull_span,
            0.0045 * r.scale,
            "x",
            mats["trim"],
        )
        for support_index, sign in enumerate((-1.0, 1.0)):
            part.visual(
                Box((0.008 * r.scale, 0.014 * r.scale, 0.022 * r.scale)),
                origin=Origin(
                    xyz=(
                        sign * pull_span * 0.42,
                        pull_y * 0.5,
                        r.rack_heights[index] + 0.009 * r.scale,
                    )
                ),
                material=mats["trim"],
                name=(
                    f"rack_geometry__{r.rack_geometry}__rack_{index}__"
                    f"front_pull_support_{support_index}"
                ), material_class_id="metal.brushed_silver",
            )
    if index == 1:
        # The upper spray hub hangs below the basket.  This short supply post
        # makes the mechanical connection explicit while leaving the arm free
        # to rotate around its own axis.
        part.visual(
            Cylinder(radius=0.020 * r.scale, length=0.031 * r.scale),
            origin=Origin(xyz=(0.0, -r.rack_depth * 0.50, -0.0135 * r.scale)),
            material=mats["trim"],
            name=f"rack_geometry__{r.rack_geometry}__rack_1__upper_spray_supply_post", material_class_id="metal.stainless_matte",
        )

    support = PlaneInterface(
        name=f"front_family.{r.front_family}.rack_support_{index}",
        point=(0.0, r.rack_origin_y, r.rack_levels[index]),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.tub_width - 0.018 * r.scale, r.tub_depth - 0.018 * r.scale),
    )
    footprint = PlaneInterface(
        name=f"rack_geometry.{r.rack_geometry}.bottom_{index}",
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.rack_width + 0.020 * r.scale, r.rack_depth),
    )
    placement = mate_planes(support, footprint, margin=0.002 * r.scale)
    model.articulation(
        f"rack_geometry__{r.rack_geometry}__rack_{index}_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=part,
        origin=placement.origin,
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=45.0 if index < 2 else 24.0,
            velocity=0.38,
            lower=0.0,
            upper=r.rack_travel[index],
        ),
    )
    return part


def _rack_geometry_round_wire_build(model, body, r, mats):
    return tuple(_build_rack_part(model, body, r, mats, index=i) for i in range(r.rack_count))


def _rack_geometry_formed_square_wire_build(model, body, r, mats):
    return tuple(_build_rack_part(model, body, r, mats, index=i) for i in range(r.rack_count))


def _rack_geometry_glass_basket_build(model, body, r, mats):
    return tuple(_build_rack_part(model, body, r, mats, index=i) for i in range(r.rack_count))


_RACK_BUILDERS = {
    "round_wire": _rack_geometry_round_wire_build,
    "formed_square_wire": _rack_geometry_formed_square_wire_build,
    "glass_basket": _rack_geometry_glass_basket_build,
}


def _rack_accessory_none_build(model, racks, r, mats):
    return ()


def _rack_accessory_sliding_caddy_build(model, racks, r: ResolvedConfig, mats):
    lower = racks[0]
    caddy = model.part("rack_accessory__sliding_caddy__caddy")
    width = r.accessory_span
    depth = min(0.135 * r.scale, r.rack_depth * 0.32)
    height = min(0.095 * r.scale, r.rack_heights[0] * 0.72)
    wire = 0.004 * r.scale
    for y, label in ((0.0, "front"), (-depth, "rear")):
        caddy.visual(
            Box((width, wire, wire)),
            origin=Origin(xyz=(0.0, y, wire * 0.5)),
            material=mats["accent"],
            name=f"rack_accessory__sliding_caddy__bottom_{label}", material_class_id="metal.paint_coated",
        )
        caddy.visual(
            Box((width, wire, wire)),
            origin=Origin(xyz=(0.0, y, height)),
            material=mats["accent"],
            name=f"rack_accessory__sliding_caddy__top_{label}", material_class_id="metal.paint_coated",
        )
    for x, label in ((-width * 0.5, "left"), (width * 0.5, "right")):
        caddy.visual(
            Box((wire, depth, wire)),
            origin=Origin(xyz=(x, -depth * 0.5, wire * 0.5)),
            material=mats["accent"],
            name=f"rack_accessory__sliding_caddy__bottom_{label}", material_class_id="metal.paint_coated",
        )
        caddy.visual(
            Box((wire, depth, wire)),
            origin=Origin(xyz=(x, -depth * 0.5, height)),
            material=mats["accent"],
            name=f"rack_accessory__sliding_caddy__top_{label}", material_class_id="metal.paint_coated",
        )
        for y_index, y in enumerate((0.0, -depth)):
            caddy.visual(
                Box((wire, wire, height)),
                origin=Origin(xyz=(x, y, height * 0.5)),
                material=mats["accent"],
                name=f"rack_accessory__sliding_caddy__post_{label}_{y_index}", material_class_id="metal.paint_coated",
            )
    for divider_index, x in enumerate((-width * 0.25, 0.0, width * 0.25)):
        caddy.visual(
            Box((wire, depth, height * 0.82)),
            origin=Origin(xyz=(x, -depth * 0.5, height * 0.41)),
            material=mats["accent"],
            name=f"rack_accessory__sliding_caddy__divider_{divider_index}", material_class_id="metal.paint_coated",
        )
    start_x = -r.rack_width * 0.5 + width * 0.5 + 0.045 * r.scale
    travel = r.rack_width - width - 0.090 * r.scale
    if r.rack_geometry == "round_wire":
        rack_floor_top = 0.005508 * r.scale * r.wire_scale
    elif r.rack_geometry == "glass_basket":
        rack_floor_top = 0.0055 * r.scale * r.wire_scale
    else:
        rack_floor_top = 0.0048 * r.scale * r.wire_scale
    model.articulation(
        "rack_accessory__sliding_caddy__lateral_slide",
        ArticulationType.PRISMATIC,
        parent=lower,
        child=caddy,
        origin=Origin(xyz=(start_x, -0.055 * r.scale, rack_floor_top)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.25, lower=0.0, upper=travel),
    )
    return (caddy,)


def _rack_accessory_folding_mug_shelves_build(model, racks, r: ResolvedConfig, mats):
    upper = racks[1]
    shelf_span = min(r.accessory_span * 0.70, r.rack_width * 0.23)
    shelf_depth = r.rack_depth * 0.42
    shelf_z = r.rack_heights[1] + 0.006 * r.scale
    shelves = []
    for side, sign in (("left", 1.0), ("right", -1.0)):
        shelf = model.part(f"rack_accessory__folding_mug_shelves__{side}_shelf")
        _rod(
            shelf,
            f"rack_accessory__folding_mug_shelves__{side}_hinge_spine",
            (0.0, -shelf_depth * 0.5, 0.0),
            shelf_depth,
            0.004 * r.scale,
            "y",
            mats["rack"],
        )
        for rail_index, y in enumerate(
            (-shelf_depth * 0.18, -shelf_depth * 0.50, -shelf_depth * 0.82)
        ):
            shelf.visual(
                Box((shelf_span, 0.005 * r.scale, 0.005 * r.scale)),
                origin=Origin(xyz=(sign * shelf_span * 0.5, y, 0.0)),
                material=mats["rack"],
                name=f"rack_accessory__folding_mug_shelves__{side}_rail_{rail_index}", material_class_id="metal.stainless_matte",
            )
        shelf.visual(
            Box((0.005 * r.scale, shelf_depth, 0.005 * r.scale)),
            origin=Origin(xyz=(sign * shelf_span, -shelf_depth * 0.5, 0.0)),
            material=mats["rack"],
            name=f"rack_accessory__folding_mug_shelves__{side}_outer_edge", material_class_id="metal.stainless_matte",
        )
        provider_axis = (0.0, sign, 0.0)
        radial = (sign, 0.0, 0.0)
        joint_name = f"rack_accessory__folding_mug_shelves__{side}_hinge"
        _add_axis_joint(
            model,
            name=joint_name,
            articulation_type=ArticulationType.REVOLUTE,
            parent=upper,
            child=shelf,
            provider=AxisInterface(
                name=f"rack_geometry.{r.rack_geometry}.{side}_shelf_axis",
                point=(-sign * r.rack_width * 0.5, -r.rack_depth * 0.52, shelf_z),
                axis=provider_axis,
                radial=radial,
                radius=0.004 * r.scale,
            ),
            consumer=AxisInterface(
                name=f"rack_accessory.folding_mug_shelves.{side}_axis",
                axis=provider_axis,
                radial=radial,
                radius=0.0032 * r.scale,
            ),
            motion_limits=MotionLimits(
                effort=1.5,
                velocity=1.2,
                lower=-math.radians(68.0),
                upper=0.0,
            ),
        )
        shelves.append(shelf)
    return tuple(shelves)


_ACCESSORY_BUILDERS = {
    "none": _rack_accessory_none_build,
    "sliding_caddy": _rack_accessory_sliding_caddy_build,
    "folding_mug_shelves": _rack_accessory_folding_mug_shelves_build,
}


def _add_wash_arm_visuals(part, r: ResolvedConfig, mats, *, span: float, prefix: str) -> None:
    part.visual(
        Cylinder(radius=0.027 * r.scale, length=0.018 * r.scale),
        origin=Origin(),
        material=mats["trim"],
        name=f"{prefix}__hub", material_class_id="metal.stainless_matte",
    )
    if r.wash_arm == "offset_paddle":
        part.visual(
            Box((span, 0.027 * r.scale, 0.012 * r.scale)),
            origin=Origin(),
            material=mats["accent"],
            name=f"{prefix}__main_paddle", material_class_id="plastic.opaque_glossy_molded",
        )
        for sign, label in ((-1.0, "left"), (1.0, "right")):
            part.visual(
                Box((span * 0.25, 0.050 * r.scale, 0.012 * r.scale)),
                origin=Origin(
                    xyz=(sign * span * 0.28, sign * 0.010 * r.scale, 0.0),
                    rpy=(0.0, 0.0, sign * 0.16),
                ),
                material=mats["accent"],
                name=f"{prefix}__offset_{label}", material_class_id="plastic.opaque_glossy_molded",
            )
            part.visual(
                Cylinder(radius=0.004 * r.scale, length=0.006 * r.scale),
                origin=Origin(xyz=(sign * span * 0.43, sign * 0.010 * r.scale, 0.009 * r.scale)),
                material=mats["dark"],
                name=f"{prefix}__jet_{label}", material_class_id="plastic.opaque_glossy_molded",
            )
    else:
        part.visual(
            Box((span, 0.024 * r.scale, 0.012 * r.scale)),
            origin=Origin(),
            material=mats["accent"],
            name=f"{prefix}__bar_x", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            Box((span * 0.62, 0.024 * r.scale, 0.012 * r.scale)),
            origin=Origin(rpy=(0.0, 0.0, math.pi * 0.5)),
            material=mats["accent"],
            name=f"{prefix}__bar_y", material_class_id="plastic.opaque_glossy_molded",
        )
        for jet_index, (x, y) in enumerate(
            ((span * 0.42, 0.0), (-span * 0.42, 0.0), (0.0, span * 0.25), (0.0, -span * 0.25))
        ):
            part.visual(
                Cylinder(radius=0.0035 * r.scale, length=0.006 * r.scale),
                origin=Origin(xyz=(x, y, 0.009 * r.scale)),
                material=mats["dark"],
                name=f"{prefix}__jet_{jet_index}", material_class_id="plastic.opaque_glossy_molded",
            )


def _build_wash_arms(model, body, racks, r: ResolvedConfig, mats):
    lower = model.part(f"wash_arm__{r.wash_arm}__lower")
    _add_wash_arm_visuals(
        lower, r, mats, span=r.lower_arm_span, prefix=f"wash_arm__{r.wash_arm}__lower"
    )
    _add_axis_joint(
        model,
        name=f"wash_arm__{r.wash_arm}__lower_spin",
        articulation_type=ArticulationType.CONTINUOUS,
        parent=body,
        child=lower,
        provider=AxisInterface(
            name=f"front_family.{r.front_family}.lower_spray_axis",
            point=(0.0, r.rack_origin_y - r.rack_depth * 0.48, r.lower_arm_z),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=0.030 * r.scale,
        ),
        consumer=AxisInterface(
            name=f"wash_arm.{r.wash_arm}.lower_axis",
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=0.027 * r.scale,
        ),
        motion_limits=MotionLimits(effort=2.0, velocity=12.0),
    )
    upper_parent = racks[1]
    upper = model.part(f"wash_arm__{r.wash_arm}__upper")
    _add_wash_arm_visuals(
        upper, r, mats, span=r.upper_arm_span, prefix=f"wash_arm__{r.wash_arm}__upper"
    )
    _add_axis_joint(
        model,
        name=f"wash_arm__{r.wash_arm}__upper_spin",
        articulation_type=ArticulationType.CONTINUOUS,
        parent=upper_parent,
        child=upper,
        provider=AxisInterface(
            name=f"rack_geometry.{r.rack_geometry}.upper_spray_axis",
            point=(0.0, -r.rack_depth * 0.50, -0.038 * r.scale),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=0.026 * r.scale,
        ),
        consumer=AxisInterface(
            name=f"wash_arm.{r.wash_arm}.upper_axis",
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=0.023 * r.scale,
        ),
        motion_limits=MotionLimits(effort=1.5, velocity=12.0),
    )
    return lower, upper


def _wash_arm_offset_paddle_build(model, body, racks, r, mats):
    return _build_wash_arms(model, body, racks, r, mats)


def _wash_arm_cross_jet_build(model, body, racks, r, mats):
    return _build_wash_arms(model, body, racks, r, mats)


_WASH_ARM_BUILDERS = {
    "offset_paddle": _wash_arm_offset_paddle_build,
    "cross_jet": _wash_arm_cross_jet_build,
}


def build_dishwasher_with_dropdown_door_and_sliding_racks(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r)
    body, _door = _FRONT_BUILDERS[r.front_family](model, r, mats, assets)
    racks = _RACK_BUILDERS[r.rack_geometry](model, body, r, mats)
    _ACCESSORY_BUILDERS[r.rack_accessory](model, racks, r, mats)
    _WASH_ARM_BUILDERS[r.wash_arm](model, body, racks, r, mats)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["source_family"] = (
        "articraft_10000plus/dishwasher_with_dropdown_door_and_sliding_racks"
    )
    model.meta["rack_levels"] = list(r.rack_levels)
    model.meta["rack_travel"] = list(r.rack_travel)
    model.meta["motion_interlocks"] = [
        {
            "controller_joint": f"front_family__{r.front_family}__door_hinge",
            "controller_required_position": 0.0,
            "dependent_joints": [
                f"rack_geometry__{r.rack_geometry}__rack_{index}_slide"
                for index in range(r.rack_count)
            ],
        }
    ]
    return model


def build_seeded_dishwasher_with_dropdown_door_and_sliding_racks(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_dishwasher_with_dropdown_door_and_sliding_racks(
        config_from_seed(seed), assets=assets
    )


def run_dishwasher_with_dropdown_door_and_sliding_racks_tests(
    object_model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()

    parts = {part.name: part for part in object_model.parts}
    joints = {joint.name: joint for joint in object_model.articulations}
    body_name = f"front_family__{r.front_family}__body"
    door_name = f"front_family__{r.front_family}__door"
    rack_names = [f"rack_geometry__{r.rack_geometry}__rack_{i}" for i in range(r.rack_count)]
    ctx.check("selected body family exists", body_name in parts)
    ctx.check("layered dropdown door exists", door_name in parts)
    ctx.check(
        "rack multiplicity matches Config",
        all(name in parts for name in rack_names) and len(rack_names) == r.rack_count,
    )

    door_joint = joints.get(f"front_family__{r.front_family}__door_hinge")
    ctx.check(
        "door has one bottom-front revolute hinge",
        door_joint is not None
        and door_joint.articulation_type == ArticulationType.REVOLUTE
        and door_joint.axis == (-1.0, 0.0, 0.0)
        and door_joint.motion_limits is not None
        and door_joint.motion_limits.lower < -1.4
        and door_joint.motion_limits.upper == 0.0,
    )

    rack_joints = [
        joints.get(f"rack_geometry__{r.rack_geometry}__rack_{i}_slide") for i in range(r.rack_count)
    ]
    ctx.check(
        "every rack has an outward prismatic slide",
        all(
            joint is not None
            and joint.articulation_type == ArticulationType.PRISMATIC
            and joint.axis == (0.0, 1.0, 0.0)
            and joint.motion_limits is not None
            and joint.motion_limits.upper > r.rack_depth * 0.35
            for joint in rack_joints
        ),
    )
    ctx.check(
        "rack levels are strictly ordered inside the tub",
        all(a < b for a, b in zip(r.rack_levels, r.rack_levels[1:]))
        and r.rack_levels[0] > r.cavity_bottom
        and r.rack_levels[-1] + r.rack_heights[-1] < r.cavity_top,
    )
    for name in rack_names:
        ctx.expect_within(
            parts[name],
            parts[body_name],
            axes="xz",
            margin=0.002 * r.scale,
            name=f"{name} fits the hollow tub cross-section",
        )

    spray_joints = [
        joints.get(f"wash_arm__{r.wash_arm}__lower_spin"),
        joints.get(f"wash_arm__{r.wash_arm}__upper_spin"),
    ]
    ctx.check(
        "two coaxial continuous wash arms exist",
        all(
            joint is not None
            and joint.articulation_type == ArticulationType.CONTINUOUS
            and joint.axis == (0.0, 0.0, 1.0)
            for joint in spray_joints
        ),
    )

    if r.rack_accessory == "sliding_caddy":
        accessory_joint = joints.get("rack_accessory__sliding_caddy__lateral_slide")
        ctx.check(
            "caddy stays a rack-local prismatic mechanism",
            accessory_joint is not None
            and accessory_joint.articulation_type == ArticulationType.PRISMATIC
            and accessory_joint.axis == (1.0, 0.0, 0.0),
        )
    elif r.rack_accessory == "folding_mug_shelves":
        shelf_joints = [
            joints.get("rack_accessory__folding_mug_shelves__left_hinge"),
            joints.get("rack_accessory__folding_mug_shelves__right_hinge"),
        ]
        ctx.check(
            "mug shelves have paired supported hinges",
            all(
                joint is not None and joint.articulation_type == ArticulationType.REVOLUTE
                for joint in shelf_joints
            ),
        )
    else:
        ctx.check(
            "none accessory emits no hidden mechanism",
            not any(name.startswith("rack_accessory__") for name in parts),
        )

    ctx.check(
        "domain choices are recorded on the model",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "compact_geometry_limits",
        {"scale": 0.94, "width_bias": 0.96, "depth_bias": 0.96, "wire_scale": 1.10},
        reason="smallest host with the heaviest rack wire",
    ),
    corner_case(
        "large_geometry_limits",
        {"scale": 1.06, "width_bias": 1.04, "depth_bias": 1.04, "wire_scale": 0.90},
        reason="largest host with the finest rack wire",
    ),
    corner_case(
        "commercial_three_level_glass",
        {
            "front_family": "commercial_pod",
            "rack_geometry": "glass_basket",
            "rack_accessory": "sliding_caddy",
            "wash_arm": "cross_jet",
            "rack_count": 3,
        },
        reason="highest-capacity commercial cross-slot assembly",
    ),
    corner_case(
        "hidden_three_level_mug_shelves",
        {
            "front_family": "integrated_hidden",
            "rack_geometry": "formed_square_wire",
            "rack_accessory": "folding_mug_shelves",
            "wash_arm": "offset_paddle",
            "rack_count": 3,
        },
        reason="dense domestic upper-rack mechanism and third tray",
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
    "build_dishwasher_with_dropdown_door_and_sliding_racks",
    "build_seeded_dishwasher_with_dropdown_door_and_sliding_racks",
    "run_dishwasher_with_dropdown_door_and_sliding_racks_tests",
]
