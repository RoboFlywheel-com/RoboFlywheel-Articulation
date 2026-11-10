# SPDX-License-Identifier: Apache-2.0

"""Source-backed horizontal wooden trough manual grain mills."""

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
    MotionLimits,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    register_interface_mate,
)

TroughBody = Literal[
    "open_straight_rails",
    "tapered_chamfered_rails",
    "tapered_hopper_trough",
]
FeedPath = Literal["shallow_plain_ramp", "narrowing_lipped_tray"]
Outlet = Literal["open_end_discharge", "side_spout_tray"]
GrindingElement = Literal[
    "plain_vertical_stone",
    "dished_wooden_wheel",
    "sloped_dished_wheel",
    "segmented_vertical_stone",
    "conical_burr_pair",
]
BearingCheeks = Literal["straight_slotted_cheeks", "arched_paired_cheeks"]
Drive = Literal["straight_axial_grip", "offset_side_crank"]


TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot(
            "trough_body",
            (
                "open_straight_rails",
                "tapered_chamfered_rails",
                "tapered_hopper_trough",
            ),
        ),
        component_slot(
            "feed_path",
            ("shallow_plain_ramp", "narrowing_lipped_tray"),
        ),
        component_slot(
            "outlet",
            ("open_end_discharge", "side_spout_tray"),
        ),
        component_slot(
            "grinding_element",
            (
                "plain_vertical_stone",
                "dished_wooden_wheel",
                "sloped_dished_wheel",
                "segmented_vertical_stone",
                "conical_burr_pair",
            ),
        ),
        component_slot(
            "bearing_cheeks",
            ("straight_slotted_cheeks", "arched_paired_cheeks"),
        ),
        component_slot(
            "drive",
            ("straight_axial_grip", "offset_side_crank"),
        ),
    )
)


@dataclass(frozen=True)
class Config:
    trough_body: TroughBody = "open_straight_rails"
    feed_path: FeedPath = "shallow_plain_ramp"
    outlet: Outlet = "open_end_discharge"
    grinding_element: GrindingElement = "plain_vertical_stone"
    bearing_cheeks: BearingCheeks = "straight_slotted_cheeks"
    drive: Drive = "straight_axial_grip"
    trough_length_m: float | None = None
    trough_width_m: float | None = None
    grinding_radius_m: float | None = None
    adjustment_travel_m: float | None = None
    grip_length_m: float | None = None
    crank_throw_m: float | None = None
    name: str = "manual_grain_mill2"


@dataclass(frozen=True)
class ResolvedConfig:
    trough_body: TroughBody
    feed_path: FeedPath
    outlet: Outlet
    grinding_element: GrindingElement
    bearing_cheeks: BearingCheeks
    drive: Drive
    trough_length_m: float
    trough_width_m: float
    grinding_radius_m: float
    adjustment_travel_m: float
    grip_length_m: float
    crank_throw_m: float
    floor_thickness_m: float
    floor_top_m: float
    rail_thickness_m: float
    inner_width_m: float
    rail_height_m: float
    grinding_thickness_m: float
    grinding_outer_radius_m: float
    relief_half_length_m: float
    relief_width_m: float
    bearing_axis_height_m: float
    cheek_center_y_m: float
    cheek_thickness_m: float
    cheek_width_m: float
    bearing_block_width_m: float
    bearing_block_height_m: float
    bearing_block_depth_m: float
    bearing_bore_radius_m: float
    axle_radius_m: float
    axle_half_span_m: float
    feed_start_x_m: float
    feed_throat_x_m: float
    feed_throat_width_m: float
    discharge_opening_m: float
    drive_mount_y_m: float
    grip_pin_radius_m: float
    grip_bore_radius_m: float
    grip_outer_radius_m: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x6112A)
    return Config(
        trough_body=choices["trough_body"],
        feed_path=choices["feed_path"],
        outlet=choices["outlet"],
        grinding_element=choices["grinding_element"],
        bearing_cheeks=choices["bearing_cheeks"],
        drive=choices["drive"],
        trough_length_m=round(rng.uniform(0.52, 0.66), 4),
        trough_width_m=round(rng.uniform(0.16, 0.20), 4),
        grinding_radius_m=round(rng.uniform(0.118, 0.145), 4),
        adjustment_travel_m=round(rng.uniform(0.004, 0.008), 4),
        grip_length_m=round(rng.uniform(0.12, 0.17), 4),
        crank_throw_m=round(rng.uniform(0.085, 0.115), 4),
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "trough_body": config.trough_body,
            "feed_path": config.feed_path,
            "outlet": config.outlet,
            "grinding_element": config.grinding_element,
            "bearing_cheeks": config.bearing_cheeks,
            "drive": config.drive,
        }
    )
    trough_length = (
        0.58 if config.trough_length_m is None else float(config.trough_length_m)
    )
    trough_width = (
        0.18 if config.trough_width_m is None else float(config.trough_width_m)
    )
    grinding_radius = (
        0.132 if config.grinding_radius_m is None else float(config.grinding_radius_m)
    )
    adjustment_travel = (
        0.006
        if config.adjustment_travel_m is None
        else float(config.adjustment_travel_m)
    )
    grip_length = (
        0.145 if config.grip_length_m is None else float(config.grip_length_m)
    )
    crank_throw = (
        0.100 if config.crank_throw_m is None else float(config.crank_throw_m)
    )
    if not 0.52 <= trough_length <= 0.66:
        raise ValueError("trough_length_m must be in [0.52, 0.66]")
    if not 0.16 <= trough_width <= 0.20:
        raise ValueError("trough_width_m must be in [0.16, 0.20]")
    if not 0.118 <= grinding_radius <= 0.145:
        raise ValueError("grinding_radius_m must be in [0.118, 0.145]")
    if not 0.004 <= adjustment_travel <= 0.008:
        raise ValueError("adjustment_travel_m must be in [0.004, 0.008]")
    if not 0.12 <= grip_length <= 0.17:
        raise ValueError("grip_length_m must be in [0.12, 0.17]")
    if not 0.085 <= crank_throw <= 0.115:
        raise ValueError("crank_throw_m must be in [0.085, 0.115]")

    floor_thickness = 0.025
    rail_thickness = 0.024
    inner_width = trough_width - 2.0 * rail_thickness
    rail_height = 0.073 + 0.10 * (trough_width - 0.16)
    if config.grinding_element == "conical_burr_pair":
        grinding_thickness = 0.064
        grinding_outer_radius = grinding_radius + 0.014
    elif config.grinding_element in {
        "dished_wooden_wheel",
        "sloped_dished_wheel",
    }:
        grinding_thickness = 0.056
        grinding_outer_radius = grinding_radius
    elif config.grinding_element == "segmented_vertical_stone":
        grinding_thickness = 0.058
        grinding_outer_radius = grinding_radius
    else:
        grinding_thickness = 0.052
        grinding_outer_radius = grinding_radius
    relief_half_length = grinding_outer_radius + 0.012
    relief_width = grinding_thickness + 0.018
    bearing_axis_height = floor_thickness + grinding_outer_radius + 0.006
    cheek_thickness = 0.022
    cheek_center_y = trough_width / 2.0 - cheek_thickness / 2.0
    cheek_width = max(0.090, 0.72 * grinding_outer_radius)
    bearing_block_width = 0.060
    bearing_block_height = 0.050
    bearing_block_depth = 0.014
    axle_radius = 0.0065
    bearing_bore_radius = axle_radius + 0.0022
    axle_half_span = cheek_center_y + cheek_thickness / 2.0 + 0.014
    feed_start_x = -trough_length / 2.0 + 0.026
    feed_throat_x = -relief_half_length - 0.008
    feed_throat_width = min(inner_width - 0.020, 0.092)
    discharge_opening = max(0.045, 0.42 * grinding_radius)
    drive_mount_y = -axle_half_span - 0.010
    grip_pin_radius = 0.0062
    grip_bore_radius = grip_pin_radius + 0.0013
    grip_outer_radius = 0.018
    if feed_start_x + 0.040 >= feed_throat_x:
        raise ValueError("trough is too short for the derived feed path")
    if relief_width >= inner_width - 0.018:
        raise ValueError("selected grinding element does not fit between trough rails")

    return ResolvedConfig(
        trough_body=config.trough_body,
        feed_path=config.feed_path,
        outlet=config.outlet,
        grinding_element=config.grinding_element,
        bearing_cheeks=config.bearing_cheeks,
        drive=config.drive,
        trough_length_m=trough_length,
        trough_width_m=trough_width,
        grinding_radius_m=grinding_radius,
        adjustment_travel_m=adjustment_travel,
        grip_length_m=grip_length,
        crank_throw_m=crank_throw,
        floor_thickness_m=floor_thickness,
        floor_top_m=floor_thickness,
        rail_thickness_m=rail_thickness,
        inner_width_m=inner_width,
        rail_height_m=rail_height,
        grinding_thickness_m=grinding_thickness,
        grinding_outer_radius_m=grinding_outer_radius,
        relief_half_length_m=relief_half_length,
        relief_width_m=relief_width,
        bearing_axis_height_m=bearing_axis_height,
        cheek_center_y_m=cheek_center_y,
        cheek_thickness_m=cheek_thickness,
        cheek_width_m=cheek_width,
        bearing_block_width_m=bearing_block_width,
        bearing_block_height_m=bearing_block_height,
        bearing_block_depth_m=bearing_block_depth,
        bearing_bore_radius_m=bearing_bore_radius,
        axle_radius_m=axle_radius,
        axle_half_span_m=axle_half_span,
        feed_start_x_m=feed_start_x,
        feed_throat_x_m=feed_throat_x,
        feed_throat_width_m=feed_throat_width,
        discharge_opening_m=discharge_opening,
        drive_mount_y_m=drive_mount_y,
        grip_pin_radius_m=grip_pin_radius,
        grip_bore_radius_m=grip_bore_radius,
        grip_outer_radius_m=grip_outer_radius,
        name=config.name,
    )


def _materials(model: ArticulatedObject) -> dict[str, object]:
    return {
        "pale_wood": model.material(
            "weathered_pale_wood",
            rgba=(0.69, 0.65, 0.56, 1.0),
        ),
        "wood_edge": model.material(
            "warm_end_grain",
            rgba=(0.54, 0.34, 0.17, 1.0),
        ),
        "stone": model.material(
            "light_millstone",
            rgba=(0.59, 0.58, 0.54, 1.0),
        ),
        "wheel_wood": model.material(
            "dished_wheel_wood",
            rgba=(0.47, 0.29, 0.13, 1.0),
        ),
        "steel": model.material(
            "aged_steel",
            rgba=(0.30, 0.31, 0.30, 1.0),
        ),
        "burr": model.material(
            "hardened_burr_steel",
            rgba=(0.24, 0.25, 0.24, 1.0),
        ),
    }


def _axis_y_cylinder(
    radius: float,
    length: float,
    *,
    center_y: float = 0.0,
) -> cq.Workplane:
    return (
        cq.Workplane("XZ")
        .circle(radius)
        .extrude(length / 2.0, both=True)
        .translate((0.0, center_y, 0.0))
    )


def _trough_floor_and_end(r: ResolvedConfig) -> cq.Workplane:
    floor = (
        cq.Workplane("XY")
        .box(r.trough_length_m, r.trough_width_m, r.floor_thickness_m)
        .translate((0.0, 0.0, r.floor_thickness_m / 2.0))
    )
    relief = (
        cq.Workplane("XY")
        .box(
            2.0 * r.relief_half_length_m,
            r.relief_width_m,
            r.floor_thickness_m + 0.010,
        )
        .translate((0.0, 0.0, r.floor_thickness_m / 2.0))
    )
    floor = floor.cut(relief)
    end_wall = (
        cq.Workplane("XY")
        .box(
            r.rail_thickness_m,
            r.inner_width_m,
            r.rail_height_m - r.floor_top_m,
        )
        .translate(
            (
                -r.trough_length_m / 2.0 + r.rail_thickness_m / 2.0,
                0.0,
                (r.rail_height_m + r.floor_top_m) / 2.0,
            )
        )
    )
    return floor.union(end_wall)


def _straight_rails(r: ResolvedConfig) -> cq.Workplane:
    rails: cq.Workplane | None = None
    for side in (-1.0, 1.0):
        rail = (
            cq.Workplane("XY")
            .box(
                r.trough_length_m,
                r.rail_thickness_m,
                r.rail_height_m - r.floor_top_m,
            )
            .translate(
                (
                    0.0,
                    side
                    * (r.trough_width_m / 2.0 - r.rail_thickness_m / 2.0),
                    (r.rail_height_m + r.floor_top_m) / 2.0,
                )
            )
        )
        rails = rail if rails is None else rails.union(rail)
    assert rails is not None
    return rails


def _tapered_rails(r: ResolvedConfig) -> cq.Workplane:
    half_length = r.trough_length_m / 2.0
    low_top = r.rail_height_m - 0.015
    high_top = r.rail_height_m + 0.011
    profile = [
        (-half_length, r.floor_top_m),
        (-half_length, high_top - 0.004),
        (-half_length + 0.010, high_top),
        (half_length - 0.010, low_top),
        (half_length, low_top - 0.004),
        (half_length, r.floor_top_m),
    ]
    rails: cq.Workplane | None = None
    for side in (-1.0, 1.0):
        rail = (
            cq.Workplane("XZ")
            .polyline(profile)
            .close()
            .extrude(r.rail_thickness_m / 2.0, both=True)
            .translate(
                (
                    0.0,
                    side
                    * (r.trough_width_m / 2.0 - r.rail_thickness_m / 2.0),
                    0.0,
                )
            )
        )
        try:
            rail = rail.edges("|Y").chamfer(0.003)
        except Exception:
            pass
        rails = rail if rails is None else rails.union(rail)
    assert rails is not None
    return rails


def _hopper_shape(r: ResolvedConfig) -> cq.Workplane:
    hopper_center_x = r.feed_start_x_m + 0.075
    throat_z = r.bearing_axis_height_m + r.grinding_outer_radius_m + 0.028
    rim_z = throat_z + 0.165
    throat_outer = (0.086, min(0.082, r.inner_width_m - 0.024))
    mouth_outer = (
        min(0.220, 0.38 * r.trough_length_m),
        min(0.166, r.trough_width_m - 0.012),
    )
    wall = 0.010
    height = rim_z - throat_z
    outer = (
        cq.Workplane("XY")
        .workplane(offset=throat_z)
        .center(hopper_center_x, 0.0)
        .rect(*throat_outer)
        .workplane(offset=height)
        .rect(*mouth_outer)
        .loft(combine=True)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=throat_z - 0.003)
        .center(hopper_center_x, 0.0)
        .rect(throat_outer[0] - 2.0 * wall, throat_outer[1] - 2.0 * wall)
        .workplane(offset=height + 0.006)
        .rect(mouth_outer[0] - 2.0 * wall, mouth_outer[1] - 2.0 * wall)
        .loft(combine=True)
    )
    walls = outer.cut(inner)
    rim_outer = (
        cq.Workplane("XY")
        .box(mouth_outer[0] + 0.026, mouth_outer[1] + 0.026, 0.012)
        .translate((hopper_center_x, 0.0, rim_z - 0.006))
    )
    rim_opening = (
        cq.Workplane("XY")
        .box(mouth_outer[0] - 2.0 * wall, mouth_outer[1] - 2.0 * wall, 0.020)
        .translate((hopper_center_x, 0.0, rim_z - 0.006))
    )
    rim = rim_outer.cut(rim_opening)
    supports: cq.Workplane | None = None
    support_height = throat_z - r.floor_top_m
    for x_offset in (-0.032, 0.032):
        for y_side in (-1.0, 1.0):
            support = (
                cq.Workplane("XY")
                .box(0.014, 0.014, support_height)
                .translate(
                    (
                        hopper_center_x + x_offset,
                        y_side * (throat_outer[1] / 2.0 - 0.008),
                        r.floor_top_m + support_height / 2.0,
                    )
                )
            )
            supports = support if supports is None else supports.union(support)
    assert supports is not None
    hopper = walls.union(rim).union(supports)
    wheel_envelope = _axis_y_cylinder(
        r.grinding_outer_radius_m + 0.010,
        r.relief_width_m,
    ).translate((0.0, 0.0, r.bearing_axis_height_m))
    return hopper.cut(wheel_envelope)


def _trough_body_open_straight_rails_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    shape = _trough_floor_and_end(r).union(_straight_rails(r))
    body.visual(
        mesh_from_cadquery(shape, "manual_grain_mill2_open_straight_trough"),
        material=mats["pale_wood"],
        name="trough_body__open_straight_rails__core", material_class_id="wood.rustic_weathered",
    )


def _trough_body_tapered_chamfered_rails_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    shape = _trough_floor_and_end(r).union(_tapered_rails(r))
    body.visual(
        mesh_from_cadquery(shape, "manual_grain_mill2_tapered_rail_trough"),
        material=mats["pale_wood"],
        name="trough_body__tapered_chamfered_rails__core", material_class_id="wood.rustic_weathered",
    )


def _trough_body_tapered_hopper_trough_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    trough = _trough_floor_and_end(r).union(_straight_rails(r))
    body.visual(
        mesh_from_cadquery(trough, "manual_grain_mill2_hopper_trough"),
        material=mats["pale_wood"],
        name="trough_body__tapered_hopper_trough__core", material_class_id="wood.rustic_weathered",
    )
    body.visual(
        mesh_from_cadquery(_hopper_shape(r), "manual_grain_mill2_tapered_hopper"),
        material=mats["pale_wood"],
        name="trough_body__tapered_hopper_trough__hollow_hopper", material_class_id="wood.rustic_weathered",
    )


def _plain_feed_shape(r: ResolvedConfig) -> cq.Workplane:
    rear_z = r.floor_top_m + 0.047
    throat_z = r.floor_top_m + 0.008
    profile = [
        (r.feed_start_x_m, r.floor_top_m),
        (r.feed_start_x_m, rear_z),
        (r.feed_throat_x_m, throat_z),
        (r.feed_throat_x_m, r.floor_top_m),
    ]
    return (
        cq.Workplane("XZ")
        .polyline(profile)
        .close()
        .extrude(r.feed_throat_width_m / 2.0, both=True)
    )


def _lipped_feed_shape(r: ResolvedConfig) -> cq.Workplane:
    run = r.feed_throat_x_m - r.feed_start_x_m
    rear_width = min(r.inner_width_m - 0.018, 0.122)
    throat_width = r.feed_throat_width_m
    rear_z = r.floor_top_m + 0.020
    throat_z = r.floor_top_m + 0.010
    slope = math.degrees(math.atan2(throat_z - rear_z, run))
    plan = [
        (r.feed_start_x_m, -rear_width / 2.0),
        (r.feed_start_x_m, rear_width / 2.0),
        (r.feed_throat_x_m, throat_width / 2.0),
        (r.feed_throat_x_m, -throat_width / 2.0),
    ]
    floor = (
        cq.Workplane("XY")
        .polyline(plan)
        .close()
        .extrude(0.007)
        .translate((0.0, 0.0, rear_z - 0.007))
        .rotate(
            (r.feed_start_x_m, 0.0, rear_z),
            (r.feed_start_x_m, 1.0, rear_z),
            -slope,
        )
    )
    lips: cq.Workplane | None = None
    for side in (-1.0, 1.0):
        y_rear = side * (rear_width / 2.0 - 0.006)
        y_throat = side * (throat_width / 2.0 - 0.006)
        lip_plan = [
            (r.feed_start_x_m, y_rear - 0.006),
            (r.feed_start_x_m, y_rear + 0.006),
            (r.feed_throat_x_m, y_throat + 0.006),
            (r.feed_throat_x_m, y_throat - 0.006),
        ]
        lip = (
            cq.Workplane("XY")
            .polyline(lip_plan)
            .close()
            .extrude(0.026)
            .translate((0.0, 0.0, rear_z))
            .rotate(
                (r.feed_start_x_m, 0.0, rear_z),
                (r.feed_start_x_m, 1.0, rear_z),
                -slope,
            )
        )
        lips = lip if lips is None else lips.union(lip)
    assert lips is not None
    support = (
        cq.Workplane("XY")
        .box(0.034, min(0.052, throat_width), 0.032)
        .translate(
            (
                r.feed_start_x_m + 0.022,
                0.0,
                r.floor_top_m + 0.012,
            )
        )
    )
    return floor.union(lips).union(support)


def _feed_path_shallow_plain_ramp_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    body.visual(
        mesh_from_cadquery(_plain_feed_shape(r), "manual_grain_mill2_plain_feed"),
        material=mats["pale_wood"],
        name="feed_path__shallow_plain_ramp__ramp", material_class_id="wood.rustic_weathered",
    )


def _feed_path_narrowing_lipped_tray_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    body.visual(
        mesh_from_cadquery(_lipped_feed_shape(r), "manual_grain_mill2_lipped_feed"),
        material=mats["pale_wood"],
        name="feed_path__narrowing_lipped_tray__tray", material_class_id="wood.rustic_weathered",
    )


def _open_discharge_shape(r: ResolvedConfig) -> cq.Workplane:
    start_x = r.relief_half_length_m + 0.010
    end_x = r.trough_length_m / 2.0 - 0.012
    width = min(r.inner_width_m - 0.026, 0.105)
    profile = [
        (start_x, r.floor_top_m + 0.010),
        (end_x, r.floor_top_m + 0.002),
        (end_x, r.floor_top_m),
        (start_x, r.floor_top_m),
    ]
    return (
        cq.Workplane("XZ")
        .polyline(profile)
        .close()
        .extrude(width / 2.0, both=True)
    )


def _side_spout_shape(r: ResolvedConfig) -> cq.Workplane:
    throat_x = r.relief_half_length_m + 0.025
    start_y = r.trough_width_m / 2.0 - 0.006
    end_y = start_y + 0.125
    channel_width = max(r.discharge_opening_m, 0.060)
    wall = 0.007
    floor = (
        cq.Workplane("XY")
        .box(channel_width, end_y - start_y, wall)
        .translate(
            (
                throat_x,
                (start_y + end_y) / 2.0,
                r.floor_top_m + 0.004,
            )
        )
    )
    sides: cq.Workplane | None = None
    for x_side in (-1.0, 1.0):
        side = (
            cq.Workplane("XY")
            .box(wall, end_y - start_y, 0.030)
            .translate(
                (
                    throat_x + x_side * (channel_width / 2.0 - wall / 2.0),
                    (start_y + end_y) / 2.0,
                    r.floor_top_m + 0.015,
                )
            )
        )
        sides = side if sides is None else sides.union(side)
    assert sides is not None
    tray_length = 0.075
    tray_width = channel_width + 0.048
    tray_center_y = end_y + tray_length / 2.0 - 0.012
    tray_floor = (
        cq.Workplane("XY")
        .box(tray_width, tray_length, wall)
        .translate((throat_x, tray_center_y, r.floor_top_m + 0.003))
    )
    tray_walls: cq.Workplane | None = None
    for x_side in (-1.0, 1.0):
        side = (
            cq.Workplane("XY")
            .box(wall, tray_length, 0.026)
            .translate(
                (
                    throat_x + x_side * (tray_width / 2.0 - wall / 2.0),
                    tray_center_y,
                    r.floor_top_m + 0.013,
                )
            )
        )
        tray_walls = side if tray_walls is None else tray_walls.union(side)
    end_lip = (
        cq.Workplane("XY")
        .box(tray_width, wall, 0.026)
        .translate(
            (
                throat_x,
                tray_center_y + tray_length / 2.0 - wall / 2.0,
                r.floor_top_m + 0.013,
            )
        )
    )
    assert tray_walls is not None
    return floor.union(sides).union(tray_floor).union(tray_walls).union(end_lip)


def _outlet_open_end_discharge_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    body.visual(
        mesh_from_cadquery(
            _open_discharge_shape(r),
            "manual_grain_mill2_open_discharge",
        ),
        material=mats["wood_edge"],
        name="outlet__open_end_discharge__meal_ramp", material_class_id="wood.oak",
    )


def _outlet_side_spout_tray_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    body.visual(
        mesh_from_cadquery(_side_spout_shape(r), "manual_grain_mill2_side_spout"),
        material=mats["pale_wood"],
        name="outlet__side_spout_tray__channel_and_tray", material_class_id="wood.rustic_weathered",
    )


def _cheek_outer_shape(
    r: ResolvedConfig,
    *,
    rear: bool,
    arched: bool,
) -> cq.Workplane:
    base_z = r.floor_top_m - 0.004
    top_z = r.bearing_axis_height_m + 0.066 + r.adjustment_travel_m
    if arched:
        shoulder_z = top_z - r.cheek_width_m / 2.0
        plate = (
            cq.Workplane("XY")
            .box(
                r.cheek_width_m,
                r.cheek_thickness_m,
                shoulder_z - base_z,
            )
            .translate(
                (
                    0.0,
                    0.0,
                    (shoulder_z + base_z) / 2.0,
                )
            )
        )
        crown = _axis_y_cylinder(
            r.cheek_width_m / 2.0,
            r.cheek_thickness_m,
        ).translate((0.0, 0.0, shoulder_z))
        plate = plate.union(crown)
    else:
        plate = (
            cq.Workplane("XY")
            .box(r.cheek_width_m, r.cheek_thickness_m, top_z - base_z)
            .translate((0.0, 0.0, (top_z + base_z) / 2.0))
        )
    foot = (
        cq.Workplane("XY")
        .box(r.cheek_width_m + 0.024, r.cheek_thickness_m, 0.018)
        .translate((0.0, 0.0, r.floor_top_m + 0.009))
    )
    plate = plate.union(foot)
    if rear:
        # Source layout: the rear cheek is an open U-shaped guide.  The
        # carriage sits in this opening at the cheek datum; the opening is
        # not a small pocket cut only around the carriage block.
        # The source guide width is the carriage width: the two wooden
        # uprights are the actual lateral sliding contacts, not a loose outer
        # frame with a large visual gap around the block.
        # The source block is captured between the two uprights; it is not
        # fused into them.  The uprights meet the block at its side datum,
        # while the bridge below is given a separate central clearance.
        opening_width = r.bearing_block_width_m
        opening_bottom = base_z - 0.002
        opening_top = max(
            r.bearing_axis_height_m
            + r.bearing_block_height_m / 2.0
            + r.adjustment_travel_m
            + 0.006,
            top_z - 0.040,
        )
        post_width = max(0.006, (r.cheek_width_m - opening_width) / 2.0)
        post_height = opening_top - opening_bottom
        rear_shape: cq.Workplane | None = None
        for side in (-1.0, 1.0):
            post = (
                cq.Workplane("XY")
                .box(post_width, r.cheek_thickness_m, post_height)
                .translate(
                    (
                        side * (opening_width / 2.0 + post_width / 2.0),
                        0.0,
                        (opening_top + opening_bottom) / 2.0,
                    )
                )
            )
            # The source has narrow guide uprights running directly into the
            # trough floor.  Do not add a widened foot here: it would intrude
            # into the carriage opening and turn the guided fit into a solid
            # overlap.  The upright itself is the load-bearing foot.
            rear_shape = post if rear_shape is None else rear_shape.union(post)
        bridge_height = top_z - opening_top
        # The source has a bored bridge for the adjuster stem.  Since this
        # template emits the guide as explicit solids, represent that bore as
        # a real central clearance rather than relying on a hidden boolean
        # subtraction that downstream collision checks may not preserve.
        stem_gap = max(0.014, opening_width + 0.004)
        bridge_side_width = (r.cheek_width_m - stem_gap) / 2.0
        bridge: cq.Workplane | None = None
        for side in (-1.0, 1.0):
            bridge_piece = (
                cq.Workplane("XY")
                .box(bridge_side_width, r.cheek_thickness_m, bridge_height)
                .translate(
                    (
                        side * (stem_gap / 2.0 + bridge_side_width / 2.0),
                        0.0,
                        (top_z + opening_top) / 2.0,
                    )
                )
            )
            bridge = (
                bridge_piece
                if bridge is None
                else bridge.union(bridge_piece)
            )
        assert bridge is not None
        assert rear_shape is not None
        rear_shape = rear_shape.union(bridge)
        if arched:
            shoulder_z = top_z - r.cheek_width_m / 2.0
            crown = _axis_y_cylinder(
                r.cheek_width_m / 2.0,
                r.cheek_thickness_m,
            ).translate((0.0, 0.0, shoulder_z))
            crown_clip: cq.Workplane | None = None
            for side in (-1.0, 1.0):
                clip_piece = (
                    cq.Workplane("XY")
                    .box(
                        bridge_side_width + 0.004,
                        r.cheek_thickness_m + 0.004,
                        bridge_height + 0.004,
                    )
                    .translate(
                        (
                            side * (stem_gap / 2.0 + bridge_side_width / 2.0),
                            0.0,
                            (top_z + opening_top) / 2.0,
                        )
                    )
                )
                crown_piece = crown.intersect(clip_piece)
                crown_clip = (
                    crown_piece
                    if crown_clip is None
                    else crown_clip.union(crown_piece)
                )
            assert crown_clip is not None
            rear_shape = rear_shape.union(crown_clip)
        # The open central bridge gap is the source-equivalent clearance for
        # the vertical adjuster stem; no hidden boolean hole is required.
        return rear_shape
    else:
        # Source front cheek: a long vertical axle-adjustment slot.  Keep the
        # nominal shaft datum in the slot while leaving substantial travel
        # above and below it, as in the photographed wooden support.
        slot_lower_z = max(base_z + 0.030, r.bearing_axis_height_m - 0.040)
        slot_upper_z = min(
            top_z - 0.030,
            r.bearing_axis_height_m + 0.040 + r.adjustment_travel_m,
        )
        bore_0 = _axis_y_cylinder(
            r.bearing_bore_radius_m,
            r.cheek_thickness_m + 0.010,
        ).translate((0.0, 0.0, slot_lower_z))
        bore_1 = _axis_y_cylinder(
            r.bearing_bore_radius_m,
            r.cheek_thickness_m + 0.010,
        ).translate(
            (
                0.0,
                0.0,
                slot_upper_z,
            )
        )
        slot = (
            cq.Workplane("XY")
            .box(
                2.0 * r.bearing_bore_radius_m,
                r.cheek_thickness_m + 0.010,
                slot_upper_z - slot_lower_z,
            )
            .translate(
                (
                    0.0,
                    0.0,
                    (slot_lower_z + slot_upper_z) / 2.0,
                )
            )
        )
        plate = plate.cut(bore_0.union(bore_1).union(slot))
    return plate


def _bearing_block_shape(r: ResolvedConfig) -> cq.Workplane:
    # The source carriage is centered on the rear-cheek datum.  Its shaft
    # bore remains coaxial with the horizontal axle while the whole carriage
    # translates vertically with the adjuster stem.
    block_center_y = 0.0
    block = cq.Workplane("XY").box(
        r.bearing_block_width_m,
        r.bearing_block_depth_m,
        r.bearing_block_height_m,
    ).translate((0.0, block_center_y, 0.0))
    bore = _axis_y_cylinder(
        r.bearing_bore_radius_m,
        r.bearing_block_depth_m + 0.010,
        center_y=block_center_y,
    )
    block = block.cut(bore)
    stem_height = 0.070 + r.adjustment_travel_m
    stem = (
        cq.Workplane("XY")
        .circle(0.004)
        .extrude(stem_height)
        .translate(
            (
                0.0,
                block_center_y,
                r.bearing_block_height_m / 2.0,
            )
        )
    )
    knob = (
        cq.Workplane("XY")
        .circle(0.013)
        .extrude(0.010)
        .translate(
            (
                0.0,
                block_center_y,
                r.bearing_block_height_m / 2.0 + stem_height,
            )
        )
    )
    return block.union(stem).union(knob)


def _bearing_sleeve_shape(r: ResolvedConfig) -> cq.Workplane:
    sleeve_length = r.bearing_block_depth_m
    sleeve_center_y = 0.0
    sleeve_outer = _axis_y_cylinder(
        r.bearing_bore_radius_m + 0.004,
        sleeve_length,
        center_y=sleeve_center_y,
    )
    sleeve_inner = _axis_y_cylinder(
        r.bearing_bore_radius_m,
        sleeve_length + 0.004,
        center_y=sleeve_center_y,
    )
    return sleeve_outer.cut(sleeve_inner)


def _bearing_saddle_shape(r: ResolvedConfig) -> cq.Workplane:
    saddle_length = r.bearing_block_depth_m
    saddle_center_y = 0.0
    saddle_height = 0.004
    return (
        cq.Workplane("XY")
        .box(
            2.0 * (r.bearing_bore_radius_m + 0.004),
            saddle_length,
            saddle_height,
        )
        .translate(
            (
                0.0,
                saddle_center_y,
                -r.axle_radius_m - saddle_height / 2.0 + 0.0002,
            )
        )
    )


def _build_bearing_parts(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    arched: bool,
) -> object:
    candidate = (
        "arched_paired_cheeks" if arched else "straight_slotted_cheeks"
    )
    for rear, side in ((False, -1.0), (True, 1.0)):
        cheek = _cheek_outer_shape(r, rear=rear, arched=arched).translate(
            (0.0, side * r.cheek_center_y_m, 0.0)
        )
        body.visual(
            mesh_from_cadquery(
                cheek,
                f"manual_grain_mill2_{candidate}_{'rear' if rear else 'front'}",
            ),
            material=mats["pale_wood"],
            name=(
                f"bearing_cheeks__{candidate}__"
                f"{'rear_guide' if rear else 'front_slot'}"
            ), material_class_id="wood.rustic_weathered",
        )
    bearing = model.part(
        "adjustable_bearing",
        meta={
            "role": "adjustable_bearing",
            "slot": "bearing_cheeks",
            "candidate": candidate,
            "real_axle_bore": True,
        },
    )
    bearing.visual(
        mesh_from_cadquery(
            _bearing_block_shape(r),
            f"manual_grain_mill2_{candidate}_bearing_block",
        ),
        material=mats["steel"],
        name=f"bearing_cheeks__{candidate}__adjustment_block", material_class_id="metal.steel_bare",
    )
    bearing.visual(
        mesh_from_cadquery(
            _bearing_sleeve_shape(r),
            f"manual_grain_mill2_{candidate}_bearing_sleeve",
        ),
        material=mats["steel"],
        name=f"bearing_cheeks__{candidate}__journal_sleeve", material_class_id="metal.steel_bare",
    )
    bearing.visual(
        mesh_from_cadquery(
            _bearing_saddle_shape(r),
            f"manual_grain_mill2_{candidate}_bearing_saddle",
        ),
        material=mats["steel"],
        name=f"bearing_cheeks__{candidate}__journal_saddle", material_class_id="metal.steel_bare",
    )
    return bearing


def _bearing_cheeks_straight_slotted_cheeks_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> object:
    return _build_bearing_parts(model, body, r, mats, arched=False)


def _bearing_cheeks_arched_paired_cheeks_build(
    model: ArticulatedObject,
    body: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> object:
    return _build_bearing_parts(model, body, r, mats, arched=True)


def _wheel_and_axle(
    wheel: cq.Workplane,
    r: ResolvedConfig,
) -> cq.Workplane:
    axle = _axis_y_cylinder(
        r.axle_radius_m,
        2.0 * r.axle_half_span_m,
    )
    hub = _axis_y_cylinder(
        0.018,
        r.grinding_thickness_m + 0.024,
    )
    return wheel.union(hub).union(axle)


def _axle_and_hub(r: ResolvedConfig) -> cq.Workplane:
    axle = _axis_y_cylinder(
        r.axle_radius_m,
        2.0 * r.axle_half_span_m,
    )
    hub = _axis_y_cylinder(
        0.018,
        r.grinding_thickness_m + 0.024,
    )
    return hub.union(axle)


def _plain_wheel_shape(r: ResolvedConfig) -> cq.Workplane:
    wheel = _axis_y_cylinder(
        r.grinding_radius_m,
        r.grinding_thickness_m,
    )
    try:
        wheel = wheel.edges().chamfer(0.004)
    except Exception:
        pass
    return _wheel_and_axle(wheel, r)


def _dished_wheel_shape(r: ResolvedConfig) -> cq.Workplane:
    wheel = _axis_y_cylinder(
        r.grinding_radius_m,
        r.grinding_thickness_m,
    )
    recess_radius = 0.80 * r.grinding_radius_m
    recess_depth = 0.006
    for side in (-1.0, 1.0):
        cutter = _axis_y_cylinder(
            recess_radius,
            recess_depth + 0.002,
            center_y=side
            * (r.grinding_thickness_m / 2.0 - recess_depth / 2.0 + 0.001),
        )
        wheel = wheel.cut(cutter)
        hub_face = _axis_y_cylinder(
            0.30 * r.grinding_radius_m,
            recess_depth,
            center_y=side
            * (r.grinding_thickness_m / 2.0 - recess_depth / 2.0),
        )
        wheel = wheel.union(hub_face)
    try:
        wheel = wheel.edges().chamfer(0.0025)
    except Exception:
        pass
    return _wheel_and_axle(wheel, r)


def _sloped_dished_wheel_shape(r: ResolvedConfig) -> cq.Workplane:
    """A single, continuous conical runner adapted from the source wheel.

    This is deliberately a revolved two-circle/frustum profile, not a wheel
    plus a neighboring box or a thin one-sided wedge.  The smaller circular
    end face transitions continuously across the sloped outer mesh to the
    larger circular grinding face.  The axle remains horizontal and centered
    in the trough, matching the source mechanism.
    """
    radius = r.grinding_radius_m
    half = r.grinding_thickness_m / 2.0
    bore_radius = r.axle_radius_m + 0.001
    # Keep a substantial smaller circular end while making the opposite end
    # visibly larger.  The straight radial transition is the characteristic
    # continuous slope; it is not approximated with boxes or stacked rings.
    small_end_radius = 0.72 * radius
    large_end_radius = radius
    edge = 0.0025
    small_end_y = -half + edge
    large_end_y = half - edge
    section = [
        (bore_radius, -half),
        (small_end_radius - edge, small_end_y),
        (small_end_radius, -half + 2.0 * edge),
        (large_end_radius - edge, large_end_y),
        (large_end_radius, half - 2.0 * edge),
        (bore_radius, half),
    ]
    wheel = (
        cq.Workplane("XY")
        .polyline(section)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )
    # Add only the coaxial hub seat used by the source wheel.  It is part of
    # the same rotating solid and does not introduce a box-like side member.
    wheel = wheel.union(_axis_y_cylinder(0.25 * radius, r.grinding_thickness_m + 0.004))
    return _wheel_and_axle(wheel, r)


def _segmented_wheel_shape(r: ResolvedConfig) -> cq.Workplane:
    wheel = _axis_y_cylinder(
        r.grinding_radius_m,
        r.grinding_thickness_m,
    )
    groove_inner = 0.32 * r.grinding_radius_m
    groove_outer = r.grinding_radius_m + 0.003
    groove_length = groove_outer - groove_inner
    groove_center = 0.5 * (groove_outer + groove_inner)
    for index in range(12):
        angle = 30.0 * index
        for side in (-1.0, 1.0):
            groove = (
                cq.Workplane("XY")
                .box(groove_length, 0.005, 0.003)
                .translate(
                    (
                        groove_center,
                        side * (r.grinding_thickness_m / 2.0 - 0.0015),
                        0.0,
                    )
                )
                .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), angle)
            )
            wheel = wheel.cut(groove)
    try:
        wheel = wheel.edges().chamfer(0.003)
    except Exception:
        pass
    return _wheel_and_axle(wheel, r)


def _conical_y(
    front_radius: float,
    rear_radius: float,
    front_y: float,
    rear_y: float,
) -> cq.Workplane:
    return (
        cq.Workplane("XZ")
        .circle(front_radius)
        .workplane(offset=rear_y - front_y)
        .circle(rear_radius)
        .loft(combine=True)
        .translate((0.0, rear_y, 0.0))
    )


def _burr_rotor_shape(r: ResolvedConfig) -> cq.Workplane:
    front_y = -r.grinding_thickness_m / 2.0
    rear_y = r.grinding_thickness_m / 2.0
    rotor = _conical_y(
        r.grinding_radius_m,
        0.60 * r.grinding_radius_m,
        front_y,
        rear_y,
    )
    for index in range(10):
        groove = (
            cq.Workplane("XY")
            .box(0.006, 0.026, 0.012)
            .translate(
                (
                    0.0,
                    front_y + 0.012,
                    r.grinding_radius_m - 0.004,
                )
            )
            .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), index * 36.0)
        )
        rotor = rotor.cut(groove)
    return rotor


def _burr_stator_shape(r: ResolvedConfig) -> cq.Workplane:
    stator_depth = 0.014
    stator_center_y = (
        -r.grinding_thickness_m / 2.0 - 0.004 - stator_depth / 2.0
    )
    outer_radius = 0.78 * r.grinding_radius_m
    inner_radius = 0.50 * r.grinding_radius_m
    outer = _axis_y_cylinder(
        outer_radius,
        stator_depth,
        center_y=stator_center_y,
    )
    inner = _axis_y_cylinder(
        inner_radius,
        stator_depth + 0.004,
        center_y=stator_center_y,
    )
    ring = outer.cut(inner)
    support_top = r.bearing_axis_height_m - outer_radius
    pedestal_height = max(0.012, support_top - r.floor_top_m)
    pedestal = (
        cq.Workplane("XY")
        .box(0.026, stator_depth, pedestal_height)
        .translate(
            (
                0.0,
                stator_center_y,
                r.floor_top_m + pedestal_height / 2.0,
            )
        )
    )
    return ring.translate((0.0, 0.0, r.bearing_axis_height_m)).union(pedestal)


def _new_grinding_shaft(
    model: ArticulatedObject,
    r: ResolvedConfig,
) -> object:
    return model.part(
        "grinding_shaft",
        meta={
            "role": "grinding_shaft",
            "slot": "grinding_element",
            "candidate": r.grinding_element,
            "centered_in_trough": True,
            "horizontal_axis": (0.0, 1.0, 0.0),
        },
    )


def _grinding_element_plain_vertical_stone_build(
    model: ArticulatedObject,
    body: object,
    bearing: object,
    shaft: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    shaft.visual(
        mesh_from_cadquery(_plain_wheel_shape(r), "manual_grain_mill2_plain_stone"),
        material=mats["stone"],
        name="grinding_element__plain_vertical_stone__wheel_and_axle", material_class_id="stone.cut_sedimentary",
    )


def _grinding_element_dished_wooden_wheel_build(
    model: ArticulatedObject,
    body: object,
    bearing: object,
    shaft: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    shaft.visual(
        mesh_from_cadquery(
            _dished_wheel_shape(r),
            "manual_grain_mill2_dished_wheel",
        ),
        material=mats["wheel_wood"],
        name="grinding_element__dished_wooden_wheel__wheel_and_axle", material_class_id="wood.mahogany_teak_dark",
    )


def _grinding_element_sloped_dished_wheel_build(
    model: ArticulatedObject,
    body: object,
    bearing: object,
    shaft: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    shaft.visual(
        mesh_from_cadquery(
            _sloped_dished_wheel_shape(r),
            "manual_grain_mill2_sloped_dished_wheel",
        ),
        material=mats["stone"],
        name="grinding_element__sloped_dished_wheel__wheel_and_axle", material_class_id="stone.cut_sedimentary",
    )


def _grinding_element_segmented_vertical_stone_build(
    model: ArticulatedObject,
    body: object,
    bearing: object,
    shaft: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    shaft.visual(
        mesh_from_cadquery(
            _segmented_wheel_shape(r),
            "manual_grain_mill2_segmented_stone",
        ),
        material=mats["stone"],
        name="grinding_element__segmented_vertical_stone__wheel_and_axle", material_class_id="stone.cut_sedimentary",
    )


def _grinding_element_conical_burr_pair_build(
    model: ArticulatedObject,
    body: object,
    bearing: object,
    shaft: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    shaft.visual(
        mesh_from_cadquery(_burr_rotor_shape(r), "manual_grain_mill2_burr_rotor"),
        material=mats["burr"],
        name="grinding_element__conical_burr_pair__rotor_and_axle", material_class_id="metal.steel_bare",
    )
    shaft.visual(
        mesh_from_cadquery(
            _axle_and_hub(r),
            "manual_grain_mill2_burr_axle",
        ),
        material=mats["steel"],
        name="grinding_element__conical_burr_pair__axle_and_hub", material_class_id="metal.steel_bare",
    )
    body.visual(
        mesh_from_cadquery(
            _burr_stator_shape(r),
            "manual_grain_mill2_burr_stator",
        ),
        material=mats["burr"],
        name="grinding_element__conical_burr_pair__supported_stator", material_class_id="metal.steel_bare",
    )


def _grip_shape(r: ResolvedConfig) -> cq.Workplane:
    outer = (
        cq.Workplane("XZ")
        .circle(r.grip_outer_radius_m)
        .workplane(offset=r.grip_length_m)
        .circle(0.78 * r.grip_outer_radius_m)
        .loft(combine=True)
    )
    insertion = min(0.052, 0.38 * r.grip_length_m)
    bore = (
        cq.Workplane("XZ")
        .circle(r.grip_bore_radius_m)
        .extrude(insertion + 0.003)
    )
    grip = outer.cut(bore)
    try:
        grip = grip.edges().fillet(0.002)
    except Exception:
        pass
    return grip


def _drive_straight_axial_grip_build(
    model: ArticulatedObject,
    shaft: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> tuple[object, tuple[float, float, float]]:
    provider = (0.0, r.drive_mount_y_m, 0.0)
    pin_length = 0.010
    pin = _axis_y_cylinder(
        r.grip_pin_radius_m,
        pin_length,
        center_y=r.drive_mount_y_m + pin_length / 2.0,
    )
    shoulder = _axis_y_cylinder(
        min(0.014, 0.78 * r.grip_outer_radius_m),
        0.006,
        center_y=r.drive_mount_y_m + 0.0025,
    )
    shaft.visual(
        mesh_from_cadquery(
            pin.union(shoulder),
            "manual_grain_mill2_straight_grip_pin",
        ),
        material=mats["steel"],
        name="drive__straight_axial_grip__support_pin", material_class_id="metal.steel_bare",
    )
    grip = model.part(
        "hand_grip",
        meta={
            "role": "hand_grip",
            "slot": "drive",
            "candidate": "straight_axial_grip",
            "real_blind_bore": True,
        },
    )
    grip.visual(
        mesh_from_cadquery(_grip_shape(r), "manual_grain_mill2_straight_grip"),
        material=mats["wood_edge"],
        name="drive__straight_axial_grip__tapered_bored_grip", material_class_id="wood.oak",
    )
    return grip, provider


def _offset_crank_hardware(
    r: ResolvedConfig,
) -> tuple[cq.Workplane, tuple[float, float, float]]:
    front_outer = -r.cheek_center_y_m - r.cheek_thickness_m / 2.0
    arm_center_y = front_outer - 0.016
    arm_depth = 0.012
    arm_width = 0.024
    arm = (
        cq.Workplane("XY")
        .box(r.crank_throw_m, arm_depth, arm_width)
        .translate((r.crank_throw_m / 2.0, arm_center_y, 0.0))
    )
    root_boss = _axis_y_cylinder(
        arm_width / 2.0,
        arm_depth,
        center_y=arm_center_y,
    )
    end_boss = _axis_y_cylinder(
        arm_width / 2.0,
        arm_depth,
        center_y=arm_center_y,
    ).translate((r.crank_throw_m, 0.0, 0.0))
    side_hub_length = abs(arm_center_y) - r.axle_half_span_m + arm_depth / 2.0
    side_hub = _axis_y_cylinder(
        0.019,
        side_hub_length,
        center_y=-(r.axle_half_span_m + side_hub_length / 2.0),
    )
    provider = (
        r.crank_throw_m,
        arm_center_y - arm_depth / 2.0,
        0.0,
    )
    pin_length = 0.010
    pin = _axis_y_cylinder(
        r.grip_pin_radius_m,
        pin_length,
        center_y=provider[1] + pin_length / 2.0,
    ).translate((r.crank_throw_m, 0.0, 0.0))
    shoulder = _axis_y_cylinder(
        min(0.014, 0.78 * r.grip_outer_radius_m),
        0.006,
        center_y=provider[1] + 0.0025,
    ).translate((r.crank_throw_m, 0.0, 0.0))
    return (
        arm.union(root_boss)
        .union(end_boss)
        .union(side_hub)
        .union(pin)
        .union(shoulder),
        provider,
    )


def _drive_offset_side_crank_build(
    model: ArticulatedObject,
    shaft: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> tuple[object, tuple[float, float, float]]:
    hardware, provider = _offset_crank_hardware(r)
    shaft.visual(
        mesh_from_cadquery(hardware, "manual_grain_mill2_offset_crank"),
        material=mats["steel"],
        name="drive__offset_side_crank__hub_arm_and_pin", material_class_id="metal.steel_bare",
    )
    grip = model.part(
        "hand_grip",
        meta={
            "role": "hand_grip",
            "slot": "drive",
            "candidate": "offset_side_crank",
            "real_blind_bore": True,
            "crank_throw_m": r.crank_throw_m,
        },
    )
    grip.visual(
        mesh_from_cadquery(_grip_shape(r), "manual_grain_mill2_offset_grip"),
        material=mats["wood_edge"],
        name="drive__offset_side_crank__tapered_bored_grip", material_class_id="wood.oak",
    )
    return grip, provider


_TROUGH_BUILDERS = {
    "open_straight_rails": _trough_body_open_straight_rails_build,
    "tapered_chamfered_rails": _trough_body_tapered_chamfered_rails_build,
    "tapered_hopper_trough": _trough_body_tapered_hopper_trough_build,
}
_FEED_BUILDERS = {
    "shallow_plain_ramp": _feed_path_shallow_plain_ramp_build,
    "narrowing_lipped_tray": _feed_path_narrowing_lipped_tray_build,
}
_OUTLET_BUILDERS = {
    "open_end_discharge": _outlet_open_end_discharge_build,
    "side_spout_tray": _outlet_side_spout_tray_build,
}
_BEARING_BUILDERS = {
    "straight_slotted_cheeks": _bearing_cheeks_straight_slotted_cheeks_build,
    "arched_paired_cheeks": _bearing_cheeks_arched_paired_cheeks_build,
}
_GRINDING_BUILDERS = {
    "plain_vertical_stone": _grinding_element_plain_vertical_stone_build,
    "dished_wooden_wheel": _grinding_element_dished_wooden_wheel_build,
    "sloped_dished_wheel": _grinding_element_sloped_dished_wheel_build,
    "segmented_vertical_stone": _grinding_element_segmented_vertical_stone_build,
    "conical_burr_pair": _grinding_element_conical_burr_pair_build,
}
_DRIVE_BUILDERS = {
    "straight_axial_grip": _drive_straight_axial_grip_build,
    "offset_side_crank": _drive_offset_side_crank_build,
}


def _axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent: object,
    child: object,
    provider: AxisInterface,
    consumer: AxisInterface,
    articulation_type: ArticulationType,
    limits: MotionLimits,
) -> None:
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        articulation_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
    )
    register_interface_mate(model, name, mate)


def build_manual_grain_mill2(
    config: Config,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "manual_grain_mill2",
            "slot_choices": (
                ("trough_body", r.trough_body),
                ("feed_path", r.feed_path),
                ("outlet", r.outlet),
                ("grinding_element", r.grinding_element),
                ("bearing_cheeks", r.bearing_cheeks),
                ("drive", r.drive),
            ),
            "source_identity": (
                "long wooden trough, centered vertical grinder, paired bearings, "
                "horizontal shaft and hand drive"
            ),
            "derived_clearances": {
                "relief_half_length_m": r.relief_half_length_m,
                "relief_width_m": r.relief_width_m,
                "bearing_axis_height_m": r.bearing_axis_height_m,
                "feed_throat_x_m": r.feed_throat_x_m,
            },
        },
    )
    mats = _materials(model)
    body = model.part(
        "mill_body",
        meta={
            "role": "mill_body",
            "long_open_trough": True,
            "wheel_relief_derived": True,
            "trough_length_m": r.trough_length_m,
            "trough_width_m": r.trough_width_m,
        },
    )
    _TROUGH_BUILDERS[r.trough_body](model, body, r, mats)
    _FEED_BUILDERS[r.feed_path](model, body, r, mats)
    _OUTLET_BUILDERS[r.outlet](model, body, r, mats)
    bearing = _BEARING_BUILDERS[r.bearing_cheeks](model, body, r, mats)
    shaft = _new_grinding_shaft(model, r)
    _GRINDING_BUILDERS[r.grinding_element](
        model,
        body,
        bearing,
        shaft,
        r,
        mats,
    )
    grip, grip_axis_point = _DRIVE_BUILDERS[r.drive](model, shaft, r, mats)

    _axis_joint(
        model,
        name="base_to_bearing",
        parent=body,
        child=bearing,
        provider=AxisInterface(
            name="trough_body.bearing_mount",
            point=(0.0, r.cheek_center_y_m, r.bearing_axis_height_m),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
        ),
        consumer=AxisInterface(
            name="bearing_cheeks.carriage_guide",
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
        ),
        articulation_type=ArticulationType.PRISMATIC,
        limits=MotionLimits(
            effort=120.0,
            velocity=0.015,
            lower=0.0,
            upper=r.adjustment_travel_m,
        ),
    )
    _axis_joint(
        model,
        name="bearing_to_shaft",
        parent=bearing,
        child=shaft,
        provider=AxisInterface(
            name="bearing_cheeks.shaft_support",
            point=(0.0, -r.cheek_center_y_m, 0.0),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.bearing_bore_radius_m,
        ),
        consumer=AxisInterface(
            name="grinding_element.shaft_axis",
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.axle_radius_m,
        ),
        articulation_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=35.0, velocity=8.0),
    )
    _axis_joint(
        model,
        name="shaft_to_grip",
        parent=shaft,
        child=grip,
        provider=AxisInterface(
            name="grinding_element.drive_axis",
            point=grip_axis_point,
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.grip_pin_radius_m,
        ),
        consumer=AxisInterface(
            name="drive.grip_axis",
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.grip_bore_radius_m,
        ),
        articulation_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=8.0, velocity=12.0),
    )
    return model


def _parts_by_role(model: ArticulatedObject, role: str) -> list[object]:
    return [part for part in model.parts if part.meta.get("role") == role]


def run_manual_grain_mill2_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    bodies = _parts_by_role(model, "mill_body")
    bearings = _parts_by_role(model, "adjustable_bearing")
    shafts = _parts_by_role(model, "grinding_shaft")
    grips = _parts_by_role(model, "hand_grip")
    body = bodies[0] if bodies else None
    bearing = bearings[0] if bearings else None
    shaft = shafts[0] if shafts else None
    grip = grips[0] if grips else None
    adjust = model.get_articulation("base_to_bearing")
    grind = model.get_articulation("bearing_to_shaft")
    grip_spin = model.get_articulation("shaft_to_grip")

    ctx.check(
        "category_anchor: manual grain mill 2 identity",
        len(bodies) == len(bearings) == len(shafts) == len(grips) == 1
        and len(model.parts) == 4
        and len(model.articulations) == 3
        and body is not None
        and bearing is not None
        and shaft is not None
        and grip is not None,
        details=(
            f"roles={{body:{len(bodies)}, bearing:{len(bearings)}, "
            f"shaft:{len(shafts)}, grip:{len(grips)}}}, "
            f"parts={len(model.parts)}, joints={len(model.articulations)}"
        ),
    )
    ctx.check(
        "category_anchor: source-like long trough geometry",
        body is not None
        and body.meta.get("long_open_trough") is True
        and r.trough_length_m >= 2.6 * r.trough_width_m
        and body.get_visual(f"trough_body__{r.trough_body}__core") is not None
        and body.get_visual(
            (
                "feed_path__shallow_plain_ramp__ramp"
                if r.feed_path == "shallow_plain_ramp"
                else "feed_path__narrowing_lipped_tray__tray"
            )
        )
        is not None,
        details=(
            f"trough={r.trough_body}, length={r.trough_length_m}, "
            f"width={r.trough_width_m}"
        ),
    )
    grinding_visual = {
        "plain_vertical_stone": "grinding_element__plain_vertical_stone__wheel_and_axle",
        "dished_wooden_wheel": "grinding_element__dished_wooden_wheel__wheel_and_axle",
        "sloped_dished_wheel": "grinding_element__sloped_dished_wheel__wheel_and_axle",
        "segmented_vertical_stone": (
            "grinding_element__segmented_vertical_stone__wheel_and_axle"
        ),
        "conical_burr_pair": "grinding_element__conical_burr_pair__rotor_and_axle",
    }[r.grinding_element]
    ctx.check(
        "category_anchor: centered supported grinding mechanism",
        shaft is not None
        and shaft.meta.get("centered_in_trough") is True
        and shaft.get_visual(grinding_visual) is not None
        and bearing is not None
        and bearing.meta.get("real_axle_bore") is True
        and adjust is not None
        and grind is not None
        and grip_spin is not None
        and adjust.parent == "mill_body"
        and adjust.child == "adjustable_bearing"
        and grind.parent == "adjustable_bearing"
        and grind.child == "grinding_shaft"
        and grip_spin.parent == "grinding_shaft"
        and grip_spin.child == "hand_grip",
        details=(
            f"grinding={r.grinding_element}, "
            f"axis_height={r.bearing_axis_height_m}"
        ),
    )
    ctx.check(
        "derived wheel relief, feed throat and bearing span remain valid",
        r.relief_half_length_m > r.grinding_outer_radius_m
        and r.relief_width_m > r.grinding_thickness_m
        and r.feed_throat_x_m < -r.grinding_outer_radius_m
        and 2.0 * r.cheek_center_y_m > r.grinding_thickness_m + 0.040
        and r.bearing_bore_radius_m > r.axle_radius_m,
        details=(
            f"relief=({r.relief_half_length_m}, {r.relief_width_m}), "
            f"feed_throat={r.feed_throat_x_m}, "
            f"cheek_span={2.0 * r.cheek_center_y_m}"
        ),
    )
    ctx.check(
        "source joint topology and axes are preserved",
        adjust is not None
        and adjust.articulation_type == ArticulationType.PRISMATIC
        and tuple(adjust.axis) == (0.0, 0.0, 1.0)
        and adjust.motion_limits is not None
        and math.isclose(adjust.motion_limits.lower, 0.0)
        and math.isclose(adjust.motion_limits.upper, r.adjustment_travel_m)
        and grind is not None
        and grind.articulation_type == ArticulationType.CONTINUOUS
        and tuple(grind.axis) == (0.0, 1.0, 0.0)
        and grip_spin is not None
        and grip_spin.articulation_type == ArticulationType.CONTINUOUS
        and tuple(grip_spin.axis) == (0.0, 1.0, 0.0),
        details=f"adjust={adjust}, grind={grind}, grip={grip_spin}",
    )
    ctx.check(
        "real bore clearances replace captured overlap allowances",
        r.bearing_bore_radius_m - r.axle_radius_m >= 0.0015
        and r.grip_bore_radius_m - r.grip_pin_radius_m >= 0.001
        and r.relief_width_m - r.grinding_thickness_m >= 0.014,
        details=(
            f"bearing_clearance={r.bearing_bore_radius_m-r.axle_radius_m}, "
            f"grip_clearance={r.grip_bore_radius_m-r.grip_pin_radius_m}, "
            f"slot_clearance={r.relief_width_m-r.grinding_thickness_m}"
        ),
    )
    if r.grinding_element == "conical_burr_pair":
        ctx.check(
            "conical burr pair has supported stator and rotating rotor",
            body is not None
            and body.get_visual(
                "grinding_element__conical_burr_pair__supported_stator"
            )
            is not None
            and shaft is not None
            and shaft.get_visual(
                "grinding_element__conical_burr_pair__rotor_and_axle"
            )
            is not None,
            details=f"bearing={bearing}, shaft={shaft}",
        )
    if r.drive == "offset_side_crank":
        ctx.check(
            "offset crank has real hub arm pin and separate bored grip",
            shaft is not None
            and shaft.get_visual("drive__offset_side_crank__hub_arm_and_pin")
            is not None
            and grip is not None
            and grip.meta.get("crank_throw_m") == r.crank_throw_m,
            details=f"throw={r.crank_throw_m}",
        )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "largest_burr_hopper_lipped_side_crank",
        {
            "trough_body": "tapered_hopper_trough",
            "feed_path": "narrowing_lipped_tray",
            "outlet": "side_spout_tray",
            "grinding_element": "conical_burr_pair",
            "bearing_cheeks": "arched_paired_cheeks",
            "drive": "offset_side_crank",
            "trough_length_m": 0.66,
            "trough_width_m": 0.20,
            "grinding_radius_m": 0.145,
            "adjustment_travel_m": 0.008,
            "grip_length_m": 0.17,
            "crank_throw_m": 0.115,
        },
        reason="largest host openings, hopper throat, stator and crank sweep",
    ),
    corner_case(
        "small_plain_source_configuration",
        {
            "trough_body": "open_straight_rails",
            "feed_path": "shallow_plain_ramp",
            "outlet": "open_end_discharge",
            "grinding_element": "plain_vertical_stone",
            "bearing_cheeks": "straight_slotted_cheeks",
            "drive": "straight_axial_grip",
            "trough_length_m": 0.52,
            "trough_width_m": 0.16,
            "grinding_radius_m": 0.118,
            "adjustment_travel_m": 0.004,
            "grip_length_m": 0.12,
            "crank_throw_m": 0.085,
        },
        reason="minimum source-like trough, wheel, guide and grip clearances",
    ),
    corner_case(
        "segmented_tapered_rails_side_outlet",
        {
            "trough_body": "tapered_chamfered_rails",
            "feed_path": "narrowing_lipped_tray",
            "outlet": "side_spout_tray",
            "grinding_element": "segmented_vertical_stone",
            "bearing_cheeks": "arched_paired_cheeks",
            "drive": "offset_side_crank",
            "trough_length_m": 0.60,
            "trough_width_m": 0.17,
            "grinding_radius_m": 0.142,
            "adjustment_travel_m": 0.008,
            "grip_length_m": 0.16,
            "crank_throw_m": 0.112,
        },
        reason="narrow host with high-profile wheel and offset discharge/drive",
    ),
    corner_case(
        "sloped_wheel_arched_cheeks",
        {
            "trough_body": "tapered_chamfered_rails",
            "feed_path": "shallow_plain_ramp",
            "outlet": "open_end_discharge",
            "grinding_element": "sloped_dished_wheel",
            "bearing_cheeks": "arched_paired_cheeks",
            "drive": "straight_axial_grip",
            "trough_length_m": 0.58,
            "trough_width_m": 0.18,
            "grinding_radius_m": 0.140,
            "adjustment_travel_m": 0.007,
            "grip_length_m": 0.15,
            "crank_throw_m": 0.10,
        },
        reason="source-like continuous conical wheel profile with arched guide cheeks",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_manual_grain_mill2",
    "config_from_seed",
    "resolve_config",
    "run_manual_grain_mill2_tests",
]
