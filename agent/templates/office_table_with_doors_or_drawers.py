# SPDX-License-Identifier: Apache-2.0

"""Source-backed office / executive tables with articulated door and drawer storage."""

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

WorktopForm = Literal["straight", "compact_corner", "u_return"]
StorageTopology = Literal[
    "drawer_and_door_credenza",
    "drawer_pedestal",
    "paired_door_pedestal",
    "open_equipment_bay",
]
Closure = Literal["hinged_door", "sliding_bypass_doors", "drop_front", "tambour"]
DrawerStyle = Literal["runner_tray", "rounded_pull_bar_tray", "flush_grip_tray"]
SecondaryMotion = Literal["none", "keyboard_tray", "cable_access_hatch"]

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("worktop_form", ("straight", "compact_corner", "u_return")),
        component_slot(
            "storage_topology",
            (
                "drawer_and_door_credenza",
                "drawer_pedestal",
                "paired_door_pedestal",
                "open_equipment_bay",
            ),
        ),
        component_slot(
            "closure",
            ("hinged_door", "sliding_bypass_doors", "drop_front", "tambour"),
        ),
        component_slot(
            "drawer_style",
            ("runner_tray", "rounded_pull_bar_tray", "flush_grip_tray"),
        ),
        component_slot(
            "secondary_motion",
            ("none", "keyboard_tray", "cable_access_hatch"),
        ),
        multiplicity_slot("drawer_count", (1, 2, 3, 4, 5), item_slot="drawer_style"),
    )
)

# Fixed manufacturing constants shared by every accepted source record.
_TOP_SLAB_T = 0.042
_UNDER_SLAB_T = 0.022
_CAP_T = 0.028
_FLOOR_T = 0.020
_PLINTH_H = 0.048
_FOOT_H = 0.010
_WALL_T = 0.018
_BACK_T = 0.016
_CHEEK_T = 0.018
_MULLION_T = 0.020
_PARTITION_T = 0.040
_DIVIDER_T = 0.014
_DRAWER_GAP = 0.014
_DRAWER_FRONT_T = 0.020
_DRAWER_FRONT_H_MAX = 0.34
_DRAWER_FRONT_H_MIN = 0.070
_RUNNER_CHANNEL_T = 0.014
_RUNNER_CLEARANCE = 0.003
_RUNNER_WEB_T = 0.005
_RUNNER_FLANGE_T = 0.006
_RUNNER_CHANNEL_H = 0.026
_BUMPER_T = 0.003
_EDGE_INSET = 0.020
_FRONT_INSET = 0.012
_RETURN_END_PANEL_T = 0.040
_TRAY_ZONE_H = 0.062
_HATCH_OPENING_H = 0.180

_PALETTES: tuple[dict[str, tuple[float, float, float, float]], ...] = (
    {
        "worktop": (0.20, 0.145, 0.125, 1.0),
        "worktop_edge": (0.135, 0.095, 0.082, 1.0),
        "carcass": (0.88, 0.86, 0.82, 1.0),
        "carcass_inner": (0.76, 0.73, 0.69, 1.0),
        "front": (0.42, 0.095, 0.085, 1.0),
        "metal": (0.60, 0.62, 0.63, 1.0),
        "dark": (0.055, 0.060, 0.065, 1.0),
        "accent": (1.0, 0.63, 0.30, 0.92),
    },
    {
        "worktop": (0.72, 0.55, 0.37, 1.0),
        "worktop_edge": (0.61, 0.43, 0.27, 1.0),
        "carcass": (0.89, 0.88, 0.83, 1.0),
        "carcass_inner": (0.78, 0.77, 0.72, 1.0),
        "front": (0.72, 0.55, 0.37, 1.0),
        "metal": (0.63, 0.65, 0.66, 1.0),
        "dark": (0.075, 0.080, 0.082, 1.0),
        "accent": (0.86, 0.72, 0.42, 1.0),
    },
    {
        "worktop": (0.67, 0.39, 0.23, 1.0),
        "worktop_edge": (0.48, 0.25, 0.14, 1.0),
        "carcass": (0.88, 0.89, 0.88, 1.0),
        "carcass_inner": (0.55, 0.57, 0.57, 1.0),
        "front": (0.88, 0.89, 0.88, 1.0),
        "metal": (0.48, 0.50, 0.50, 1.0),
        "dark": (0.075, 0.085, 0.085, 1.0),
        "accent": (0.67, 0.39, 0.23, 1.0),
    },
    {
        "worktop": (0.80, 0.66, 0.46, 1.0),
        "worktop_edge": (0.62, 0.48, 0.31, 1.0),
        "carcass": (0.275, 0.285, 0.295, 1.0),
        "carcass_inner": (0.38, 0.39, 0.40, 1.0),
        "front": (0.245, 0.255, 0.265, 1.0),
        "metal": (0.74, 0.75, 0.76, 1.0),
        "dark": (0.090, 0.095, 0.100, 1.0),
        "accent": (0.78, 0.62, 0.32, 1.0),
    },
    {
        "worktop": (0.235, 0.170, 0.140, 1.0),
        "worktop_edge": (0.155, 0.115, 0.095, 1.0),
        "carcass": (0.60, 0.62, 0.61, 1.0),
        "carcass_inner": (0.47, 0.49, 0.48, 1.0),
        "front": (0.36, 0.30, 0.22, 1.0),
        "metal": (0.72, 0.60, 0.32, 1.0),
        "dark": (0.060, 0.060, 0.060, 1.0),
        "accent": (0.82, 0.70, 0.40, 1.0),
    },
)


@dataclass(frozen=True)
class Config:
    worktop_form: WorktopForm = "straight"
    storage_topology: StorageTopology = "drawer_and_door_credenza"
    closure: Closure = "hinged_door"
    drawer_style: DrawerStyle = "runner_tray"
    secondary_motion: SecondaryMotion = "none"
    drawer_count: int = 3
    main_span_m: float | None = None
    main_depth_m: float | None = None
    return_depth_m: float | None = None
    worktop_height_m: float | None = None
    pedestal_width_m: float | None = None
    closure_panel_thickness_m: float | None = None
    drawer_wall_m: float | None = None
    tray_depth_m: float | None = None
    hatch_width_m: float | None = None
    palette: int = 0
    name: str = "office_table_with_doors_or_drawers"


@dataclass(frozen=True)
class ResolvedConfig:
    worktop_form: WorktopForm
    storage_topology: StorageTopology
    closure: Closure
    drawer_style: DrawerStyle
    secondary_motion: SecondaryMotion
    drawer_count: int
    main_span_m: float
    main_depth_m: float
    return_depth_m: float
    worktop_height_m: float
    pedestal_width_m: float
    closure_panel_thickness_m: float
    drawer_wall_m: float
    tray_depth_m: float
    hatch_width_m: float
    palette: int
    top_slab_t_m: float
    under_slab_t_m: float
    cap_t_m: float
    top_bottom_z_m: float
    under_bottom_z_m: float
    bay_top_z_m: float
    plinth_top_z_m: float
    bay_floor_z_m: float
    bay_h_m: float
    carcass_span_m: float
    carcass_depth_m: float
    carcass_front_y_m: float
    carcass_rear_y_m: float
    carcass_interior_depth_m: float
    interior_rear_y_m: float
    has_knee_bay: bool
    knee_span_m: float
    knee_center_x_m: float
    drawer_volume_cx_m: float
    drawer_volume_w_m: float
    closure_volume_cx_m: float
    closure_volume_w_m: float
    partition_cx_m: float
    drawer_opening_w_m: float
    drawer_bay_h_m: float
    drawer_front_h_m: float
    drawer_front_w_m: float
    drawer_stack_h_m: float
    drawer_remainder_h_m: float
    drawer_level_pitch_m: float
    drawer_box_w_m: float
    drawer_box_d_m: float
    drawer_box_front_y_m: float
    drawer_travel_m: float
    runner_gauge_m: float
    front_reveal_m: float
    closure_bay_count: int
    closure_leaf_count: int
    closure_opening_w_m: float
    closure_opening_h_m: float
    closure_bay_z0_m: float
    closure_bay_z1_m: float
    closure_bay_cx_m: tuple[float, ...]
    closure_bay_hinge_sign_m: tuple[float, ...]
    closure_leaf_w_m: float
    closure_leaf_h_m: float
    closure_inset_depth_m: float
    hinge_barrel_r_m: float
    hinge_setback_m: float
    hinge_open_rad: float
    tambour_travel_m: float
    slide_travel_m: float
    secondary_mount_span_m: float
    secondary_mount_z_m: float
    tray_zone_h_m: float
    tray_width_m: float
    tray_travel_m: float
    hatch_opening_w_m: float
    return_end_panel_count: int
    return_wing_width_m: float
    return_support_y_m: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x0FF1CE)
    return Config(
        worktop_form=choices["worktop_form"],
        storage_topology=choices["storage_topology"],
        closure=choices["closure"],
        drawer_style=choices["drawer_style"],
        secondary_motion=choices["secondary_motion"],
        drawer_count=choices["drawer_count"],
        main_span_m=round(rng.uniform(1.66, 1.95), 4),
        main_depth_m=round(rng.uniform(0.62, 0.78), 4),
        return_depth_m=round(rng.uniform(0.48, 0.66), 4),
        worktop_height_m=round(rng.uniform(0.72, 0.78), 4),
        pedestal_width_m=round(rng.uniform(0.34, 0.44), 4),
        closure_panel_thickness_m=round(rng.uniform(0.018, 0.026), 4),
        drawer_wall_m=round(rng.uniform(0.014, 0.020), 4),
        tray_depth_m=round(rng.uniform(0.26, 0.34), 4),
        hatch_width_m=round(rng.uniform(0.22, 0.32), 4),
        palette=rng.randrange(len(_PALETTES)),
    )


def _default(value: float | None, fallback: float) -> float:
    return fallback if value is None else float(value)


def _require(name: str, value: float, low: float, high: float) -> None:
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}]")


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "worktop_form": config.worktop_form,
            "storage_topology": config.storage_topology,
            "closure": config.closure,
            "drawer_style": config.drawer_style,
            "secondary_motion": config.secondary_motion,
            "drawer_count": config.drawer_count,
        }
    )
    span = _default(config.main_span_m, 1.80)
    depth = _default(config.main_depth_m, 0.70)
    return_depth = _default(config.return_depth_m, 0.56)
    height = _default(config.worktop_height_m, 0.75)
    pedestal_w = _default(config.pedestal_width_m, 0.40)
    panel_t = _default(config.closure_panel_thickness_m, 0.022)
    wall = _default(config.drawer_wall_m, 0.016)
    tray_depth = _default(config.tray_depth_m, 0.30)
    hatch_w = _default(config.hatch_width_m, 0.27)
    _require("main_span_m", span, 1.66, 1.95)
    _require("main_depth_m", depth, 0.62, 0.78)
    _require("return_depth_m", return_depth, 0.48, 0.66)
    _require("worktop_height_m", height, 0.72, 0.78)
    _require("pedestal_width_m", pedestal_w, 0.34, 0.44)
    _require("closure_panel_thickness_m", panel_t, 0.018, 0.026)
    _require("drawer_wall_m", wall, 0.014, 0.020)
    _require("tray_depth_m", tray_depth, 0.26, 0.34)
    _require("hatch_width_m", hatch_w, 0.22, 0.32)
    palette = int(config.palette) % len(_PALETTES)

    top_bottom = height - _TOP_SLAB_T
    under_bottom = top_bottom - _UNDER_SLAB_T
    bay_top = under_bottom - _CAP_T
    plinth_top = _FOOT_H + _PLINTH_H
    bay_floor = plinth_top + _FLOOR_T
    bay_h = bay_top - bay_floor

    carcass_span = span - 2.0 * _EDGE_INSET
    carcass_depth = depth - 2.0 * _FRONT_INSET
    front_y = -depth / 2.0 + _FRONT_INSET
    rear_y = depth / 2.0 - _FRONT_INSET
    interior_depth = carcass_depth - _BACK_T
    interior_rear_y = rear_y - _BACK_T

    topology = config.storage_topology
    credenza = topology == "drawer_and_door_credenza"
    paired = topology == "paired_door_pedestal"
    has_knee = not credenza

    if credenza:
        inner = carcass_span - 2.0 * _WALL_T - _PARTITION_T
        closure_opening_w = min(max(pedestal_w * 1.35, 0.30), inner - 0.55)
        drawer_opening_w = inner - closure_opening_w
        drawer_volume_w = drawer_opening_w + _WALL_T + _PARTITION_T / 2.0
        drawer_volume_cx = -carcass_span / 2.0 + _WALL_T + drawer_opening_w / 2.0
        partition_cx = -carcass_span / 2.0 + _WALL_T + drawer_opening_w + _PARTITION_T / 2.0
        closure_volume_w = closure_opening_w + _WALL_T + _PARTITION_T / 2.0
        closure_volume_cx = partition_cx + _PARTITION_T / 2.0 + closure_opening_w / 2.0
        knee_span = 0.0
        knee_center = 0.0
    else:
        drawer_volume_w = pedestal_w
        closure_volume_w = pedestal_w * 1.45 if paired else pedestal_w
        drawer_volume_cx = -carcass_span / 2.0 + drawer_volume_w / 2.0
        closure_volume_cx = carcass_span / 2.0 - closure_volume_w / 2.0
        partition_cx = 0.0
        drawer_opening_w = drawer_volume_w - 2.0 * _WALL_T
        if paired:
            closure_opening_w = (closure_volume_w - 2.0 * _WALL_T - _MULLION_T) / 2.0
        else:
            closure_opening_w = closure_volume_w - 2.0 * _WALL_T
        knee_left = drawer_volume_cx + drawer_volume_w / 2.0
        knee_right = closure_volume_cx - closure_volume_w / 2.0
        knee_span = knee_right - knee_left
        knee_center = (knee_left + knee_right) / 2.0

    closure_bay_count = 2 if paired else 1
    closure_opening_h = bay_h * 0.55 if topology == "open_equipment_bay" else bay_h
    closure_bay_z0 = bay_floor
    closure_bay_z1 = bay_floor + closure_opening_h
    if paired:
        offset = _MULLION_T / 2.0 + closure_opening_w / 2.0
        closure_bay_cx = (closure_volume_cx - offset, closure_volume_cx + offset)
        closure_bay_sign = (-1.0, 1.0)
    else:
        closure_bay_cx = (closure_volume_cx,)
        closure_bay_sign = (1.0,)

    leaves_per_bay = 2 if config.closure == "sliding_bypass_doors" else 1
    closure_leaf_count = closure_bay_count * leaves_per_bay
    hinge_barrel_r = panel_t * 0.42 + 0.001
    hinge_setback = hinge_barrel_r + 0.002
    if config.closure == "sliding_bypass_doors":
        closure_leaf_w = closure_opening_w / 2.0 + 0.008
        closure_inset_depth = 2.0 * panel_t + 0.020
    elif config.closure == "tambour":
        closure_leaf_w = closure_opening_w - 0.034
        closure_inset_depth = 0.032
    else:
        closure_leaf_w = closure_opening_w - hinge_setback - 0.004
        closure_inset_depth = 0.006
    if config.closure == "tambour":
        closure_leaf_h = (closure_opening_h - 0.014) / 2.0
    else:
        closure_leaf_h = closure_opening_h - 0.008
    tambour_travel = closure_leaf_h + 0.004
    slide_travel = closure_opening_w / 2.0 - 0.010

    tray_zone = (
        _TRAY_ZONE_H if (config.secondary_motion == "keyboard_tray" and not has_knee) else 0.0
    )
    drawer_bay_h = bay_h - tray_zone
    count = int(config.drawer_count)
    front_h = min(
        _DRAWER_FRONT_H_MAX,
        (drawer_bay_h - (count - 1) * _DRAWER_GAP) / count,
    )
    stack_h = count * front_h + (count - 1) * _DRAWER_GAP
    remainder = drawer_bay_h - stack_h
    pitch = front_h + _DRAWER_GAP
    runner_gauge = drawer_opening_w - 2.0 * _RUNNER_CHANNEL_T
    box_w = drawer_opening_w - 2.0 * (_RUNNER_CHANNEL_T + _RUNNER_CLEARANCE)
    front_reveal = _BUMPER_T + 0.0006
    box_front_y = front_y - front_reveal
    box_d = interior_rear_y - 0.012 - box_front_y
    travel = min(box_d * 0.72, box_d - 0.080)
    front_w = drawer_opening_w + 2.0 * _WALL_T - 0.008

    if has_knee:
        tray_width = min(max(knee_span - 0.060, 0.30), 0.62)
    else:
        tray_width = min(max(drawer_opening_w - 0.060, 0.30), 0.62)
    secondary_span = tray_width + 0.034
    secondary_mount_z = under_bottom if has_knee else bay_top
    tray_travel = tray_depth * 0.76
    hatch_opening_w = min(hatch_w, closure_opening_w - 0.040)

    if config.worktop_form == "straight":
        wing_count = 0
    elif config.worktop_form == "compact_corner":
        wing_count = 1
    else:
        wing_count = 2
    wing_width = min(pedestal_w + 0.05, 0.52)
    return_support_y = depth / 2.0 + return_depth - _RETURN_END_PANEL_T / 2.0

    if front_h < _DRAWER_FRONT_H_MIN:
        raise ValueError(
            f"drawer_count is too high for the derived drawer bay: front_h={front_h:.4f}"
        )
    if box_w < 0.22:
        raise ValueError(f"derived drawer box width is too small: {box_w:.4f}")
    if box_d < 0.26:
        raise ValueError(f"derived drawer box depth is too small: {box_d:.4f}")
    if travel < 0.14:
        raise ValueError(f"derived drawer travel is too small: {travel:.4f}")
    if closure_opening_w < 0.18:
        raise ValueError(f"derived closure opening is too narrow: {closure_opening_w:.4f}")
    if closure_leaf_w < 0.10:
        raise ValueError(f"derived closure leaf is too narrow: {closure_leaf_w:.4f}")
    if closure_leaf_h < 0.10:
        raise ValueError(f"derived closure leaf is too short: {closure_leaf_h:.4f}")
    if closure_inset_depth + 0.030 >= interior_depth:
        raise ValueError("closure mechanism does not fit inside the derived cavity")
    if has_knee and knee_span < 0.36:
        raise ValueError(f"derived knee bay is too narrow: {knee_span:.4f}")
    if hatch_opening_w < 0.14:
        raise ValueError(f"derived cable hatch opening is too narrow: {hatch_opening_w:.4f}")
    if wall >= _DRAWER_FRONT_H_MIN / 3.0:
        raise ValueError("drawer wall thickness does not fit the derived tray")

    return ResolvedConfig(
        worktop_form=config.worktop_form,
        storage_topology=topology,
        closure=config.closure,
        drawer_style=config.drawer_style,
        secondary_motion=config.secondary_motion,
        drawer_count=count,
        main_span_m=span,
        main_depth_m=depth,
        return_depth_m=return_depth,
        worktop_height_m=height,
        pedestal_width_m=pedestal_w,
        closure_panel_thickness_m=panel_t,
        drawer_wall_m=wall,
        tray_depth_m=tray_depth,
        hatch_width_m=hatch_w,
        palette=palette,
        top_slab_t_m=_TOP_SLAB_T,
        under_slab_t_m=_UNDER_SLAB_T,
        cap_t_m=_CAP_T,
        top_bottom_z_m=top_bottom,
        under_bottom_z_m=under_bottom,
        bay_top_z_m=bay_top,
        plinth_top_z_m=plinth_top,
        bay_floor_z_m=bay_floor,
        bay_h_m=bay_h,
        carcass_span_m=carcass_span,
        carcass_depth_m=carcass_depth,
        carcass_front_y_m=front_y,
        carcass_rear_y_m=rear_y,
        carcass_interior_depth_m=interior_depth,
        interior_rear_y_m=interior_rear_y,
        has_knee_bay=has_knee,
        knee_span_m=knee_span,
        knee_center_x_m=knee_center,
        drawer_volume_cx_m=drawer_volume_cx,
        drawer_volume_w_m=drawer_volume_w,
        closure_volume_cx_m=closure_volume_cx,
        closure_volume_w_m=closure_volume_w,
        partition_cx_m=partition_cx,
        drawer_opening_w_m=drawer_opening_w,
        drawer_bay_h_m=drawer_bay_h,
        drawer_front_h_m=front_h,
        drawer_front_w_m=front_w,
        drawer_stack_h_m=stack_h,
        drawer_remainder_h_m=remainder,
        drawer_level_pitch_m=pitch,
        drawer_box_w_m=box_w,
        drawer_box_d_m=box_d,
        drawer_box_front_y_m=box_front_y,
        drawer_travel_m=travel,
        runner_gauge_m=runner_gauge,
        front_reveal_m=front_reveal,
        closure_bay_count=closure_bay_count,
        closure_leaf_count=closure_leaf_count,
        closure_opening_w_m=closure_opening_w,
        closure_opening_h_m=closure_opening_h,
        closure_bay_z0_m=closure_bay_z0,
        closure_bay_z1_m=closure_bay_z1,
        closure_bay_cx_m=closure_bay_cx,
        closure_bay_hinge_sign_m=closure_bay_sign,
        closure_leaf_w_m=closure_leaf_w,
        closure_leaf_h_m=closure_leaf_h,
        closure_inset_depth_m=closure_inset_depth,
        hinge_barrel_r_m=hinge_barrel_r,
        hinge_setback_m=hinge_setback,
        hinge_open_rad=1.75,
        tambour_travel_m=tambour_travel,
        slide_travel_m=slide_travel,
        secondary_mount_span_m=secondary_span,
        secondary_mount_z_m=secondary_mount_z,
        tray_zone_h_m=tray_zone,
        tray_width_m=tray_width,
        tray_travel_m=tray_travel,
        hatch_opening_w_m=hatch_opening_w,
        return_end_panel_count=wing_count,
        return_wing_width_m=wing_width,
        return_support_y_m=return_support_y,
        name=config.name,
    )


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, object]:
    swatch = _PALETTES[r.palette]
    return {key: model.material(f"office_table_{key}", rgba=value) for key, value in swatch.items()}


def _bx(
    part: object,
    size: tuple[float, float, float],
    xyz: tuple[float, float, float],
    material: object,
    name: str,
) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="wood.engineered_board")


def _plane_mate(
    *,
    provider_name: str,
    provider_point: tuple[float, float, float],
    provider_normal: tuple[float, float, float],
    provider_extent: tuple[float, float],
    consumer_name: str,
    consumer_point: tuple[float, float, float],
    consumer_extent: tuple[float, float],
    tangent_u: tuple[float, float, float] = (1.0, 0.0, 0.0),
    gap: float = 0.0,
):
    """Solve one planar mount from the real supporting footprint on both sides."""

    consumer_normal = (
        -provider_normal[0],
        -provider_normal[1],
        -provider_normal[2],
    )
    provider = PlaneInterface(
        name=provider_name,
        point=provider_point,
        normal=provider_normal,
        tangent_u=tangent_u,
        extent=provider_extent,
    )
    consumer = PlaneInterface(
        name=consumer_name,
        point=consumer_point,
        normal=consumer_normal,
        tangent_u=tangent_u,
        extent=consumer_extent,
    )
    return mate_planes(provider, consumer, gap=gap)


def _axis_mate(
    *,
    provider_name: str,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    radial: tuple[float, float, float],
    provider_radius: float,
    consumer_name: str,
    consumer_radius: float,
):
    """Solve one hinge line so the child rotates about the real barrel centre."""

    provider = AxisInterface(
        name=provider_name,
        point=point,
        axis=axis,
        radial=radial,
        radius=provider_radius,
    )
    consumer = AxisInterface(
        name=consumer_name,
        point=(0.0, 0.0, 0.0),
        axis=axis,
        radial=radial,
        radius=consumer_radius,
    )
    return mate_axes(provider, consumer, require_fit=True)


# ---------------------------------------------------------------- worktop form


def _wing_specs(r: ResolvedConfig) -> tuple[tuple[float, float, float], ...]:
    """(centre_x, near_y, far_y) for every cantilevered rear wing."""

    if r.return_end_panel_count == 0:
        return ()
    near = r.main_depth_m / 2.0
    far = near + r.return_depth_m
    left = (r.drawer_volume_cx_m, near, far)
    right = (r.closure_volume_cx_m, near, far)
    if r.return_end_panel_count == 1:
        return (left,)
    return (left, right)


def _cable_slot_shape(cx: float, cy: float, r: ResolvedConfig) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(0.125, 0.036, r.top_slab_t_m + 0.030)
        .translate((cx, cy, r.top_bottom_z_m + r.top_slab_t_m / 2.0))
    )


def _worktop_shape(r: ResolvedConfig) -> cq.Workplane:
    slab = (
        cq.Workplane("XY")
        .box(r.main_span_m, r.main_depth_m, r.top_slab_t_m)
        .translate((0.0, 0.0, r.top_bottom_z_m + r.top_slab_t_m / 2.0))
    )
    wings = _wing_specs(r)
    for cx, near, far in wings:
        wing = (
            cq.Workplane("XY")
            .box(r.return_wing_width_m, far - near, r.top_slab_t_m)
            .translate((cx, (near + far) / 2.0, r.top_bottom_z_m + r.top_slab_t_m / 2.0))
        )
        slab = slab.union(wing)
    try:
        slab = slab.edges("|Z").fillet(0.016)
    except Exception:  # noqa: BLE001 - fillet is cosmetic on unioned plans
        pass
    if wings:
        for cx, _near, far in wings:
            slab = slab.cut(_cable_slot_shape(cx, far - 0.110, r))
    else:
        slab = slab.cut(
            _cable_slot_shape(
                r.closure_volume_cx_m,
                r.main_depth_m / 2.0 - 0.100,
                r,
            )
        )
    return slab


def _add_cable_trim(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    cx: float,
    cy: float,
    tag: str,
) -> None:
    top = r.worktop_height_m
    for side, dx, dy, sx, sy in (
        ("left", -0.0685, 0.0, 0.007, 0.048),
        ("right", 0.0685, 0.0, 0.007, 0.048),
        ("near", 0.0, -0.0225, 0.140, 0.007),
        ("far", 0.0, 0.0225, 0.140, 0.007),
    ):
        _bx(
            carcass,
            (sx, sy, 0.005),
            (cx + dx, cy + dy, top - 0.001),
            mats["dark"],
            f"{tag}__cable_trim_{side}",
        )


def _add_worktop_common(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    tag: str,
) -> None:
    carcass.visual(
        mesh_from_cadquery(_worktop_shape(r), f"office_table_worktop_{r.worktop_form}"),
        material=mats["worktop"],
        name=f"{tag}__slab", material_class_id="wood.polished_varnished",
    )
    _bx(
        carcass,
        (r.main_span_m - 0.010, 0.011, 0.016),
        (
            0.0,
            -r.main_depth_m / 2.0 + 0.0055,
            r.top_bottom_z_m - 0.005,
        ),
        mats["worktop_edge"],
        f"{tag}__front_edge_band",
    )
    _bx(
        carcass,
        (r.carcass_span_m, r.carcass_depth_m, r.under_slab_t_m),
        (0.0, 0.0, r.under_bottom_z_m + r.under_slab_t_m / 2.0),
        mats["carcass"],
        f"{tag}__under_slab",
    )
    wings = _wing_specs(r)
    if not wings:
        _add_cable_trim(
            carcass,
            r,
            mats,
            cx=r.closure_volume_cx_m,
            cy=r.main_depth_m / 2.0 - 0.100,
            tag=tag,
        )
    for index, (cx, near, far) in enumerate(wings):
        _add_cable_trim(carcass, r, mats, cx=cx, cy=far - 0.110, tag=f"{tag}_{index}")
        under_near = near - 0.030
        _bx(
            carcass,
            (r.return_wing_width_m - 0.004, far - under_near, r.under_slab_t_m),
            (
                cx,
                (under_near + far) / 2.0,
                r.under_bottom_z_m + r.under_slab_t_m / 2.0,
            ),
            mats["carcass"],
            f"{tag}__return_under_slab_{index}",
        )
        _bx(
            carcass,
            (r.return_wing_width_m - 0.010, _RETURN_END_PANEL_T, r.under_bottom_z_m),
            (cx, r.return_support_y_m, r.under_bottom_z_m / 2.0),
            mats["carcass"],
            f"{tag}__return_end_panel_{index}",
        )
        _bx(
            carcass,
            (r.return_wing_width_m - 0.010, 0.020, 0.060),
            (cx, near + 0.020, r.under_bottom_z_m - 0.030),
            mats["carcass_inner"],
            f"{tag}__return_shoulder_{index}",
        )


def _worktop_form_straight_build(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    _add_worktop_common(carcass, r, mats, tag="worktop_form__straight")
    inlay_w = r.main_span_m * 0.62
    inlay_d = r.main_depth_m * 0.66
    _bx(
        carcass,
        (inlay_w, inlay_d, 0.006),
        (r.main_span_m * 0.08, 0.0, r.worktop_height_m + 0.002),
        mats["carcass"],
        "worktop_form__straight__laminate_field",
    )
    for edge, dx, dy, sx, sy in (
        ("front", 0.0, -inlay_d / 2.0 - 0.002, inlay_w + 0.008, 0.004),
        ("back", 0.0, inlay_d / 2.0 + 0.002, inlay_w + 0.008, 0.004),
        ("left", -inlay_w / 2.0 - 0.002, 0.0, 0.004, inlay_d),
        ("right", inlay_w / 2.0 + 0.002, 0.0, 0.004, inlay_d),
    ):
        _bx(
            carcass,
            (sx, sy, 0.004),
            (r.main_span_m * 0.08 + dx, dy, r.worktop_height_m + 0.001),
            mats["dark"],
            f"worktop_form__straight__inlay_reveal_{edge}",
        )


def _worktop_form_compact_corner_build(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    _add_worktop_common(carcass, r, mats, tag="worktop_form__compact_corner")
    cx, near, far = _wing_specs(r)[0]
    _bx(
        carcass,
        (r.return_wing_width_m - 0.030, 0.020, 0.018),
        (cx, far - 0.010, r.top_bottom_z_m - 0.006),
        mats["worktop_edge"],
        "worktop_form__compact_corner__wing_edge_band",
    )
    _bx(
        carcass,
        (0.020, far - near - 0.040, 0.018),
        (
            cx + r.return_wing_width_m / 2.0 - 0.010,
            (near + far) / 2.0,
            r.top_bottom_z_m - 0.006,
        ),
        mats["worktop_edge"],
        "worktop_form__compact_corner__wing_side_band",
    )


def _worktop_form_u_return_build(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    _add_worktop_common(carcass, r, mats, tag="worktop_form__u_return")
    for index, (cx, near, far) in enumerate(_wing_specs(r)):
        _bx(
            carcass,
            (r.return_wing_width_m - 0.030, 0.020, 0.018),
            (cx, far - 0.010, r.top_bottom_z_m - 0.006),
            mats["worktop_edge"],
            f"worktop_form__u_return__wing_edge_band_{index}",
        )
    _bx(
        carcass,
        (r.knee_span_m if r.has_knee_bay else r.carcass_span_m * 0.5, 0.020, 0.016),
        (
            r.knee_center_x_m if r.has_knee_bay else 0.0,
            r.main_depth_m / 2.0 - 0.014,
            r.top_bottom_z_m - 0.006,
        ),
        mats["worktop_edge"],
        "worktop_form__u_return__inner_bridge_band",
    )


_WORKTOP_BUILDERS = {
    "straight": _worktop_form_straight_build,
    "compact_corner": _worktop_form_compact_corner_build,
    "u_return": _worktop_form_u_return_build,
}


# ------------------------------------------------------------ storage topology


def _rounded_cheek_shape(
    x_center: float,
    r: ResolvedConfig,
) -> cq.Workplane:
    height = r.under_bottom_z_m - _FOOT_H
    panel = (
        cq.Workplane("XY")
        .box(_CHEEK_T, r.carcass_depth_m + 0.010, height)
        .translate((x_center, 0.0, _FOOT_H + height / 2.0))
    )
    try:
        panel = panel.edges("|Z").fillet(0.008)
    except Exception:  # noqa: BLE001 - rounding is cosmetic
        pass
    return panel


def _back_opening(r: ResolvedConfig) -> tuple[float, float, float, float]:
    """(centre_x, width, centre_z, height) of the real cable-hatch opening."""

    return (
        r.closure_volume_cx_m,
        r.hatch_opening_w_m,
        r.bay_floor_z_m + 0.42 * r.bay_h_m,
        _HATCH_OPENING_H,
    )


def _volume_shell(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    cx: float,
    width: float,
    tag: str,
    sled_plinth: bool = False,
    cheek_side: float = 0.0,
) -> None:
    """Grounded storage volume: foot, plinth, floor, side walls, back and cap."""

    bay_height = r.bay_top_z_m - r.bay_floor_z_m
    _bx(
        carcass,
        (width - 0.070, r.carcass_depth_m - 0.110, _FOOT_H),
        (cx, 0.0, _FOOT_H / 2.0),
        mats["dark"],
        f"{tag}__recessed_foot",
    )
    if sled_plinth:
        rail_z = _FOOT_H + 0.014
        for index, y in enumerate(
            (-r.carcass_depth_m / 2.0 + 0.045, r.carcass_depth_m / 2.0 - 0.045)
        ):
            _bx(
                carcass,
                (width - 0.020, 0.028, 0.028),
                (cx, y, rail_z),
                mats["metal"],
                f"{tag}__sled_rail_{index}",
            )
        for index, x in enumerate((cx - width / 2.0 + 0.024, cx + width / 2.0 - 0.024)):
            _bx(
                carcass,
                (0.028, r.carcass_depth_m - 0.090, 0.028),
                (x, 0.0, rail_z),
                mats["metal"],
                f"{tag}__sled_cross_{index}",
            )
        post_h = r.plinth_top_z_m - (rail_z + 0.014)
        for index, (px, py) in enumerate(
            (
                (cx - width / 2.0 + 0.030, -r.carcass_depth_m / 2.0 + 0.045),
                (cx + width / 2.0 - 0.030, -r.carcass_depth_m / 2.0 + 0.045),
                (cx - width / 2.0 + 0.030, r.carcass_depth_m / 2.0 - 0.045),
                (cx + width / 2.0 - 0.030, r.carcass_depth_m / 2.0 - 0.045),
            )
        ):
            _bx(
                carcass,
                (0.050, 0.050, post_h + 0.006),
                (px, py, rail_z + 0.011 + post_h / 2.0),
                mats["metal"],
                f"{tag}__sled_post_{index}",
            )
    else:
        _bx(
            carcass,
            (width - 0.018, r.carcass_depth_m - 0.028, _PLINTH_H),
            (cx, 0.0, _FOOT_H + _PLINTH_H / 2.0),
            mats["carcass_inner"],
            f"{tag}__plinth",
        )
    _bx(
        carcass,
        (width, r.carcass_depth_m, _FLOOR_T),
        (cx, 0.0, r.plinth_top_z_m + _FLOOR_T / 2.0),
        mats["carcass"],
        f"{tag}__floor",
    )
    for side, x in (
        ("left", cx - width / 2.0 + _WALL_T / 2.0),
        ("right", cx + width / 2.0 - _WALL_T / 2.0),
    ):
        _bx(
            carcass,
            (_WALL_T, r.carcass_depth_m, bay_height),
            (x, 0.0, (r.bay_floor_z_m + r.bay_top_z_m) / 2.0),
            mats["carcass"],
            f"{tag}__side_wall_{side}",
        )
    back_y = r.carcass_rear_y_m - _BACK_T / 2.0
    opening = _back_opening(r) if r.secondary_motion == "cable_access_hatch" else None
    if opening is not None and cx - width / 2.0 < opening[0] < cx + width / 2.0:
        o_cx, o_w, o_cz, o_h = opening
        for side, sign in (("left", -1.0), ("right", 1.0)):
            edge = cx + sign * width / 2.0
            inner = o_cx + sign * o_w / 2.0
            member_w = abs(edge - inner)
            _bx(
                carcass,
                (member_w, _BACK_T, bay_height),
                (
                    (edge + inner) / 2.0,
                    back_y,
                    (r.bay_floor_z_m + r.bay_top_z_m) / 2.0,
                ),
                mats["carcass"],
                f"{tag}__back_frame_{side}",
            )
        for rail, z_a, z_b in (
            ("lower", r.bay_floor_z_m, o_cz - o_h / 2.0),
            ("upper", o_cz + o_h / 2.0, r.bay_top_z_m),
        ):
            _bx(
                carcass,
                (o_w, _BACK_T, z_b - z_a),
                (o_cx, back_y, (z_a + z_b) / 2.0),
                mats["carcass"],
                f"{tag}__back_frame_{rail}",
            )
    else:
        _bx(
            carcass,
            (width, _BACK_T, bay_height),
            (cx, back_y, (r.bay_floor_z_m + r.bay_top_z_m) / 2.0),
            mats["carcass"],
            f"{tag}__back_panel",
        )
    _bx(
        carcass,
        (width, r.carcass_depth_m, _CAP_T),
        (cx, 0.0, r.bay_top_z_m + _CAP_T / 2.0),
        mats["carcass"],
        f"{tag}__cap",
    )
    if cheek_side:
        outer = cx + cheek_side * width / 2.0
        carcass.visual(
            mesh_from_cadquery(
                _rounded_cheek_shape(outer + cheek_side * _CHEEK_T / 2.0, r),
                f"office_table_cheek_{tag}",
            ),
            material=mats["carcass"],
            name=f"{tag}__rounded_end_cheek", material_class_id="wood.veneer_panel",
        )


def _add_closure_bay_shelves(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    tag: str,
) -> None:
    zone_h = r.closure_leaf_h_m if r.closure == "tambour" else r.closure_opening_h_m
    shelf_count = 1 if zone_h < 0.32 else 2
    y0 = r.carcass_front_y_m + r.closure_inset_depth_m + 0.008
    y1 = r.interior_rear_y_m - 0.006
    for bay_index, bay_cx in enumerate(r.closure_bay_cx_m):
        for shelf in range(shelf_count):
            z = r.closure_bay_z0_m + zone_h * (shelf + 1) / (shelf_count + 1)
            _bx(
                carcass,
                (r.closure_opening_w_m, y1 - y0, 0.020),
                (bay_cx, (y0 + y1) / 2.0, z),
                mats["carcass_inner"],
                f"{tag}__closure_shelf_{bay_index}_{shelf}",
            )


def _add_knee_bay(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    tag: str,
) -> None:
    modesty_h = min(0.34, r.bay_h_m - 0.12)
    _bx(
        carcass,
        (r.knee_span_m + 0.012, 0.020, modesty_h),
        (
            r.knee_center_x_m,
            r.carcass_rear_y_m - _BACK_T - 0.012,
            r.bay_top_z_m - 0.020 - modesty_h / 2.0,
        ),
        mats["carcass"],
        f"{tag}__modesty_panel",
    )
    shelf_depth = min(0.24, r.carcass_interior_depth_m - 0.10)
    shelf_z = r.bay_top_z_m - 0.120
    _bx(
        carcass,
        (r.knee_span_m + 0.012, shelf_depth, 0.024),
        (
            r.knee_center_x_m,
            r.carcass_rear_y_m - _BACK_T - 0.024 - shelf_depth / 2.0,
            shelf_z,
        ),
        mats["worktop"],
        f"{tag}__knee_shelf",
    )
    for index, dx in ((0, -r.knee_span_m * 0.22), (1, r.knee_span_m * 0.22)):
        _bx(
            carcass,
            (0.022, shelf_depth - 0.020, 0.070),
            (
                r.knee_center_x_m + dx,
                r.carcass_rear_y_m - _BACK_T - 0.024 - shelf_depth / 2.0,
                shelf_z + 0.047,
            ),
            mats["carcass"],
            f"{tag}__knee_shelf_divider_{index}",
        )


def _add_vent_stack(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    tag: str,
) -> None:
    x_face = r.closure_volume_cx_m + r.closure_volume_w_m / 2.0 + _CHEEK_T - 0.003
    z0 = r.bay_floor_z_m + 0.070
    _bx(
        carcass,
        (0.006, 0.052, 0.152),
        (x_face - 0.002, r.carcass_front_y_m + 0.150, z0 + 0.076),
        mats["dark"],
        f"{tag}__vent_backing",
    )
    for index in range(5):
        _bx(
            carcass,
            (0.006, 0.056, 0.010),
            (
                x_face,
                r.carcass_front_y_m + 0.150,
                z0 + 0.022 + index * 0.026,
            ),
            mats["metal"],
            f"{tag}__vent_slit_{index}",
        )


def _storage_topology_drawer_and_door_credenza_build(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    tag = "storage_topology__drawer_and_door_credenza"
    _volume_shell(
        carcass,
        r,
        mats,
        cx=0.0,
        width=r.carcass_span_m,
        tag=tag,
        sled_plinth=True,
    )
    _bx(
        carcass,
        (_PARTITION_T, r.carcass_depth_m, r.bay_top_z_m - r.bay_floor_z_m),
        (r.partition_cx_m, 0.0, (r.bay_floor_z_m + r.bay_top_z_m) / 2.0),
        mats["carcass"],
        f"{tag}__partition",
    )
    _bx(
        carcass,
        (r.carcass_span_m - 0.060, 0.020, 0.020),
        (0.0, r.carcass_front_y_m + 0.011, r.bay_top_z_m + _CAP_T / 2.0),
        mats["carcass_inner"],
        f"{tag}__recessed_fascia_reveal",
    )
    _bx(
        carcass,
        (r.carcass_span_m - 0.100, 0.009, 0.011),
        (0.0, r.carcass_front_y_m + 0.005, r.bay_top_z_m + 0.008),
        mats["accent"],
        f"{tag}__task_light_strip",
    )
    _add_closure_bay_shelves(carcass, r, mats, tag=tag)


def _storage_topology_drawer_pedestal_build(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    tag = "storage_topology__drawer_pedestal"
    _volume_shell(
        carcass,
        r,
        mats,
        cx=r.drawer_volume_cx_m,
        width=r.drawer_volume_w_m,
        tag=f"{tag}_drawer",
        cheek_side=-1.0,
    )
    _volume_shell(
        carcass,
        r,
        mats,
        cx=r.closure_volume_cx_m,
        width=r.closure_volume_w_m,
        tag=f"{tag}_closure",
        cheek_side=1.0,
    )
    _add_knee_bay(carcass, r, mats, tag=tag)
    _add_closure_bay_shelves(carcass, r, mats, tag=tag)
    _add_vent_stack(carcass, r, mats, tag=tag)


def _storage_topology_paired_door_pedestal_build(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    tag = "storage_topology__paired_door_pedestal"
    _volume_shell(
        carcass,
        r,
        mats,
        cx=r.drawer_volume_cx_m,
        width=r.drawer_volume_w_m,
        tag=f"{tag}_drawer",
        cheek_side=-1.0,
    )
    _volume_shell(
        carcass,
        r,
        mats,
        cx=r.closure_volume_cx_m,
        width=r.closure_volume_w_m,
        tag=f"{tag}_closure",
        cheek_side=1.0,
    )
    _bx(
        carcass,
        (_MULLION_T, r.carcass_depth_m, r.bay_top_z_m - r.bay_floor_z_m),
        (
            r.closure_volume_cx_m,
            0.0,
            (r.bay_floor_z_m + r.bay_top_z_m) / 2.0,
        ),
        mats["carcass"],
        f"{tag}__centre_mullion",
    )
    # The mullion reveal stays strictly inside the mullion width and behind the
    # depth the selected closure mechanism occupies, so it never intrudes into
    # a sliding groove or a hinged leaf swing.
    _bx(
        carcass,
        (_MULLION_T - 0.004, 0.014, r.bay_top_z_m - r.bay_floor_z_m - 0.020),
        (
            r.closure_volume_cx_m,
            r.carcass_front_y_m + r.closure_inset_depth_m + 0.009,
            (r.bay_floor_z_m + r.bay_top_z_m) / 2.0,
        ),
        mats["carcass_inner"],
        f"{tag}__mullion_reveal",
    )
    _add_knee_bay(carcass, r, mats, tag=tag)
    _add_closure_bay_shelves(carcass, r, mats, tag=tag)


def _storage_topology_open_equipment_bay_build(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    tag = "storage_topology__open_equipment_bay"
    _volume_shell(
        carcass,
        r,
        mats,
        cx=r.drawer_volume_cx_m,
        width=r.drawer_volume_w_m,
        tag=f"{tag}_drawer",
        cheek_side=-1.0,
    )
    _volume_shell(
        carcass,
        r,
        mats,
        cx=r.closure_volume_cx_m,
        width=r.closure_volume_w_m,
        tag=f"{tag}_closure",
        cheek_side=1.0,
    )
    deck_z = r.closure_bay_z1_m + 0.008
    _bx(
        carcass,
        (r.closure_opening_w_m, r.carcass_interior_depth_m, 0.016),
        (
            r.closure_volume_cx_m,
            r.carcass_front_y_m + r.carcass_interior_depth_m / 2.0,
            deck_z,
        ),
        mats["carcass"],
        f"{tag}__cubby_deck",
    )
    cubby_z0 = deck_z + 0.008
    cubby_h = r.bay_top_z_m - cubby_z0
    for index in range(2):
        _bx(
            carcass,
            (r.closure_opening_w_m, r.carcass_interior_depth_m - 0.030, 0.018),
            (
                r.closure_volume_cx_m,
                r.carcass_front_y_m + 0.020 + (r.carcass_interior_depth_m - 0.030) / 2.0,
                cubby_z0 + cubby_h * (index + 1) / 3.0,
            ),
            mats["carcass_inner"],
            f"{tag}__cubby_shelf_{index}",
        )
    carcass.visual(
        Cylinder(radius=0.028, length=_BACK_T + 0.012),
        origin=Origin(
            xyz=(
                r.closure_volume_cx_m,
                r.carcass_rear_y_m - _BACK_T / 2.0,
                cubby_z0 + cubby_h * 0.5,
            ),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["dark"],
        name=f"{tag}__rear_cable_grommet", material_class_id="plastic.opaque_generic",
    )
    _add_knee_bay(carcass, r, mats, tag=tag)
    _add_closure_bay_shelves(carcass, r, mats, tag=tag)
    _add_vent_stack(carcass, r, mats, tag=tag)


_TOPOLOGY_BUILDERS = {
    "drawer_and_door_credenza": _storage_topology_drawer_and_door_credenza_build,
    "drawer_pedestal": _storage_topology_drawer_pedestal_build,
    "paired_door_pedestal": _storage_topology_paired_door_pedestal_build,
    "open_equipment_bay": _storage_topology_open_equipment_bay_build,
}


# ------------------------------------------------------- drawer cavity + trays


def _level_z0(r: ResolvedConfig, index: int) -> float:
    return r.bay_floor_z_m + index * r.drawer_level_pitch_m


def _rail_z(r: ResolvedConfig, index: int) -> float:
    return _level_z0(r, index) + 0.034


def _channel_y_span(r: ResolvedConfig) -> tuple[float, float]:
    return (r.carcass_front_y_m + 0.010, r.interior_rear_y_m - 0.006)


def _add_drawer_cavity(
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    """Real cavity for the tray stack: runner channels, dividers and bumpers."""

    tag = f"drawer_style__{r.drawer_style}"
    half = r.drawer_opening_w_m / 2.0
    y0, y1 = _channel_y_span(r)
    cd = y1 - y0
    cy = (y0 + y1) / 2.0
    flange_w = _RUNNER_CHANNEL_T - _RUNNER_WEB_T
    for index in range(r.drawer_count):
        rail_z = _rail_z(r, index)
        for side, sign in (("left", -1.0), ("right", 1.0)):
            _bx(
                carcass,
                (_RUNNER_WEB_T, cd, _RUNNER_CHANNEL_H),
                (
                    r.drawer_volume_cx_m + sign * (half - _RUNNER_WEB_T / 2.0),
                    cy,
                    rail_z,
                ),
                mats["metal"],
                f"{tag}__runner_web_{index}_{side}",
            )
            for flange, dz in (("upper", 1.0), ("lower", -1.0)):
                _bx(
                    carcass,
                    (flange_w, cd, _RUNNER_FLANGE_T),
                    (
                        r.drawer_volume_cx_m + sign * (half - _RUNNER_WEB_T - flange_w / 2.0),
                        cy,
                        rail_z + dz * (_RUNNER_CHANNEL_H - _RUNNER_FLANGE_T) / 2.0,
                    ),
                    mats["metal"],
                    f"{tag}__runner_flange_{index}_{side}_{flange}",
                )
            _bx(
                carcass,
                (0.010, _BUMPER_T, min(0.030, r.drawer_front_h_m - 0.020)),
                (
                    r.drawer_volume_cx_m + sign * (half + 0.008),
                    r.carcass_front_y_m - _BUMPER_T / 2.0,
                    _level_z0(r, index) + r.drawer_front_h_m / 2.0,
                ),
                mats["dark"],
                f"{tag}__soft_close_bumper_{index}_{side}",
            )
        if index < r.drawer_count - 1:
            _bx(
                carcass,
                (r.drawer_opening_w_m, cd, _DIVIDER_T),
                (
                    r.drawer_volume_cx_m,
                    cy,
                    _level_z0(r, index) + r.drawer_front_h_m + _DRAWER_GAP / 2.0,
                ),
                mats["carcass_inner"],
                f"{tag}__bay_divider_{index}",
            )
    if r.drawer_remainder_h_m > 0.055:
        cubby_z0 = r.bay_floor_z_m + r.drawer_stack_h_m
        _bx(
            carcass,
            (r.drawer_opening_w_m, cd, 0.018),
            (r.drawer_volume_cx_m, cy, cubby_z0 + 0.009),
            mats["carcass"],
            f"{tag}__open_cubby_deck",
        )
        _bx(
            carcass,
            (0.020, cd - 0.030, r.drawer_remainder_h_m - 0.030),
            (
                r.drawer_volume_cx_m,
                cy,
                cubby_z0 + 0.018 + (r.drawer_remainder_h_m - 0.030) / 2.0,
            ),
            mats["carcass_inner"],
            f"{tag}__open_cubby_divider",
        )


def _rounded_front_shape(w: float, t: float, h: float) -> cq.Workplane:
    radius = min(0.014, w * 0.20, h * 0.20)
    panel = cq.Workplane("XY").box(w, t, h)
    try:
        panel = panel.edges("|Y").fillet(radius)
    except Exception:  # noqa: BLE001 - rounding is cosmetic
        pass
    return panel


def _add_tray_body(
    drawer: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    tag: str,
) -> None:
    """Hollow tray: floor, two side walls, one back wall, two runner members."""

    wall = r.drawer_wall_m
    bw = r.drawer_box_w_m
    bd = r.drawer_box_d_m
    box_h = r.drawer_front_h_m - 0.020
    side_h = box_h - wall
    _bx(
        drawer,
        (bw, bd, wall),
        (0.0, 0.0, wall / 2.0),
        mats["carcass_inner"],
        f"{tag}__tray_floor",
    )
    for side, sign in (("left", -1.0), ("right", 1.0)):
        _bx(
            drawer,
            (wall, bd, side_h),
            (sign * (bw / 2.0 - wall / 2.0), 0.0, wall + side_h / 2.0),
            mats["carcass_inner"],
            f"{tag}__tray_side_{side}",
        )
        # The tray runner rides ON the lower channel flange, so the moving
        # member has real bearing contact with the carcass at every travel
        # position instead of floating in the middle of the channel mouth.
        _bx(
            drawer,
            (0.011, bd - 0.030, 0.010),
            (sign * (bw / 2.0 + 0.0055), 0.0, 0.024),
            mats["metal"],
            f"{tag}__runner_member_{side}",
        )
    _bx(
        drawer,
        (bw - 2.0 * wall, wall, side_h),
        (0.0, bd / 2.0 - wall / 2.0, wall + side_h / 2.0),
        mats["carcass_inner"],
        f"{tag}__tray_back",
    )


def _drawer_front_local(r: ResolvedConfig) -> tuple[float, float, float]:
    return (
        0.0,
        -r.drawer_box_d_m / 2.0 - _DRAWER_FRONT_T / 2.0,
        r.drawer_front_h_m / 2.0 - 0.008,
    )


def _new_drawer(
    model: ArticulatedObject,
    r: ResolvedConfig,
    index: int,
) -> object:
    return model.part(
        f"drawer_style__{r.drawer_style}__drawer_{index}",
        meta={
            "role": "storage_drawer",
            "slot": "drawer_style",
            "candidate": r.drawer_style,
            "level": index,
            "hollow_tray": True,
            "runner_gauge_m": r.runner_gauge_m,
            "travel_m": r.drawer_travel_m,
        },
    )


def _attach_drawer(
    model: ArticulatedObject,
    carcass: object,
    drawer: object,
    r: ResolvedConfig,
    index: int,
) -> None:
    box_cy = r.drawer_box_front_y_m + r.drawer_box_d_m / 2.0
    box_z0 = _level_z0(r, index) + 0.008
    mate = _plane_mate(
        provider_name=f"storage_topology.drawer_cavity_{index}",
        provider_point=(r.drawer_volume_cx_m, box_cy, box_z0),
        provider_normal=(0.0, 0.0, 1.0),
        provider_extent=(r.drawer_opening_w_m, r.carcass_interior_depth_m),
        consumer_name=f"drawer_style.tray_seat_{index}",
        consumer_point=(0.0, 0.0, 0.0),
        consumer_extent=(r.drawer_box_w_m, r.drawer_box_d_m),
    )
    joint = f"drawer_style__{r.drawer_style}__slide_{index}"
    model.articulation(
        joint,
        ArticulationType.PRISMATIC,
        parent=carcass,
        child=drawer,
        origin=mate.origin,
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=70.0,
            velocity=0.32,
            lower=0.0,
            upper=r.drawer_travel_m,
        ),
        meta={"mechanism": "side-mounted runner channel and tray runner member"},
    )
    register_interface_mate(model, joint, mate)


def _drawer_style_runner_tray_build(
    model: ArticulatedObject,
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    index: int,
) -> object:
    tag = "drawer_style__runner_tray"
    drawer = _new_drawer(model, r, index)
    _add_tray_body(drawer, r, mats, tag=tag)
    fx, fy, fz = _drawer_front_local(r)
    _bx(
        drawer,
        (r.drawer_front_w_m, _DRAWER_FRONT_T, r.drawer_front_h_m - 0.006),
        (fx, fy, fz),
        mats["front"],
        f"{tag}__front_{index}",
    )
    _bx(
        drawer,
        (min(0.090, r.drawer_front_w_m * 0.24), 0.011, 0.026),
        (
            r.drawer_front_w_m * 0.26,
            fy - _DRAWER_FRONT_T / 2.0 - 0.0055,
            fz + (r.drawer_front_h_m - 0.006) / 2.0 - 0.030,
        ),
        mats["dark"],
        f"{tag}__inset_pull_{index}",
    )
    for side, sign in (("left", -1.0), ("right", 1.0)):
        _bx(
            drawer,
            (0.006, r.drawer_box_d_m - 0.040, 0.028),
            (
                sign * (r.drawer_box_w_m / 2.0 - r.drawer_wall_m - 0.003),
                0.0,
                r.drawer_wall_m + 0.016,
            ),
            mats["metal"],
            f"{tag}__runner_mount_plate_{index}_{side}",
        )
    _attach_drawer(model, carcass, drawer, r, index)
    return drawer


def _drawer_style_rounded_pull_bar_tray_build(
    model: ArticulatedObject,
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    index: int,
) -> object:
    tag = "drawer_style__rounded_pull_bar_tray"
    drawer = _new_drawer(model, r, index)
    _add_tray_body(drawer, r, mats, tag=tag)
    fx, fy, fz = _drawer_front_local(r)
    drawer.visual(
        mesh_from_cadquery(
            _rounded_front_shape(
                r.drawer_front_w_m,
                _DRAWER_FRONT_T,
                r.drawer_front_h_m - 0.006,
            ),
            "office_table_rounded_drawer_front",
        ),
        origin=Origin(xyz=(fx, fy, fz)),
        material=mats["front"],
        name=f"{tag}__front_{index}", material_class_id="wood.veneer_panel",
    )
    _bx(
        drawer,
        (r.drawer_front_w_m * 0.72, 0.016, 0.018),
        (
            0.0,
            fy - _DRAWER_FRONT_T / 2.0 - 0.008,
            fz + (r.drawer_front_h_m - 0.006) / 2.0 - 0.024,
        ),
        mats["metal"],
        f"{tag}__pull_bar_{index}",
    )
    _attach_drawer(model, carcass, drawer, r, index)
    return drawer


def _drawer_style_flush_grip_tray_build(
    model: ArticulatedObject,
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    index: int,
) -> object:
    tag = "drawer_style__flush_grip_tray"
    drawer = _new_drawer(model, r, index)
    _add_tray_body(drawer, r, mats, tag=tag)
    fx, fy, fz = _drawer_front_local(r)
    _bx(
        drawer,
        (r.drawer_front_w_m, _DRAWER_FRONT_T, r.drawer_front_h_m - 0.006),
        (fx, fy, fz),
        mats["front"],
        f"{tag}__front_{index}",
    )
    _bx(
        drawer,
        (0.016, 0.014, min(0.120, (r.drawer_front_h_m - 0.006) * 0.55)),
        (
            r.drawer_front_w_m / 2.0 - 0.040,
            fy - _DRAWER_FRONT_T / 2.0 - 0.007,
            fz,
        ),
        mats["dark"],
        f"{tag}__flush_grip_{index}",
    )
    _bx(
        drawer,
        (r.drawer_box_w_m * 0.30, 0.010, 0.020),
        (
            0.0,
            r.drawer_box_d_m / 2.0 + 0.005,
            r.drawer_wall_m + 0.014,
        ),
        mats["metal"],
        f"{tag}__rear_anti_tip_catch_{index}",
    )
    _attach_drawer(model, carcass, drawer, r, index)
    return drawer


_DRAWER_BUILDERS = {
    "runner_tray": _drawer_style_runner_tray_build,
    "rounded_pull_bar_tray": _drawer_style_rounded_pull_bar_tray_build,
    "flush_grip_tray": _drawer_style_flush_grip_tray_build,
}


# --------------------------------------------------------------------- closure


def _new_leaf(
    model: ArticulatedObject,
    r: ResolvedConfig,
    index: int,
    *,
    mechanism: str,
) -> object:
    return model.part(
        f"closure__{r.closure}__leaf_{index}",
        meta={
            "role": "closure_leaf",
            "slot": "closure",
            "candidate": r.closure,
            "leaf": index,
            "mechanism": mechanism,
        },
    )


def _closure_hinged_door_build(
    model: ArticulatedObject,
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> list[object]:
    tag = "closure__hinged_door"
    leaves: list[object] = []
    t = r.closure_panel_thickness_m
    rb = r.hinge_barrel_r_m
    setback = r.hinge_setback_m
    lh = r.closure_leaf_h_m
    lw = r.closure_leaf_w_m
    cfy = r.carcass_front_y_m
    panel_rear = cfy - r.front_reveal_m
    ay = panel_rear - t
    zc = (r.closure_bay_z0_m + r.closure_bay_z1_m) / 2.0
    stations = (-0.30 * lh, 0.30 * lh)
    for index, (bay_cx, sign) in enumerate(zip(r.closure_bay_cx_m, r.closure_bay_hinge_sign_m)):
        hx = bay_cx + sign * r.closure_opening_w_m / 2.0
        for station_index, station in enumerate(stations):
            carcass.visual(
                Cylinder(radius=rb, length=0.020),
                origin=Origin(xyz=(hx, ay, zc + station)),
                material=mats["metal"],
                name=f"{tag}__fixed_knuckle_{index}_{station_index}", material_class_id="metal.stainless_matte",
            )
            _bx(
                carcass,
                (0.017, cfy - ay, 0.020),
                (hx + sign * 0.0095, (ay + cfy) / 2.0, zc + station),
                mats["metal"],
                f"{tag}__knuckle_plate_{index}_{station_index}",
            )
        leaf = _new_leaf(model, r, index, mechanism="vertical butt hinge")
        _bx(
            leaf,
            (lw, t, lh),
            (-sign * (setback + lw / 2.0), t / 2.0, 0.0),
            mats["front"],
            f"{tag}__panel_{index}",
        )
        # The leaf knuckles butt directly against the fixed knuckle faces, so
        # the hinge is a real captured barrel rather than a coaxial gap.
        for station_index, station in enumerate(stations):
            for barrel_index, offset in enumerate((-0.022, 0.022)):
                leaf.visual(
                    Cylinder(radius=rb, length=0.024),
                    origin=Origin(xyz=(0.0, 0.0, station + offset)),
                    material=mats["metal"],
                    name=f"{tag}__barrel_{index}_{station_index}_{barrel_index}", material_class_id="metal.stainless_matte",
                )
                _bx(
                    leaf,
                    (0.028, t + 0.004, 0.022),
                    (-sign * 0.014, t / 2.0, station + offset),
                    mats["metal"],
                    f"{tag}__hinge_strap_{index}_{station_index}_{barrel_index}",
                )
        _bx(
            leaf,
            (0.022, 0.016, min(0.150, lh * 0.30)),
            (-sign * (setback + lw - 0.032), -0.008, 0.0),
            mats["dark"],
            f"{tag}__pull_{index}",
        )
        mate = _axis_mate(
            provider_name=f"storage_topology.closure_hinge_{index}",
            point=(hx, ay, zc),
            axis=(0.0, 0.0, sign),
            radial=(1.0, 0.0, 0.0),
            provider_radius=rb,
            consumer_name=f"closure.hinge_line_{index}",
            consumer_radius=rb * 0.86,
        )
        joint = f"{tag}__leaf_joint_{index}"
        model.articulation(
            joint,
            ArticulationType.REVOLUTE,
            parent=carcass,
            child=leaf,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(
                effort=12.0,
                velocity=1.6,
                lower=0.0,
                upper=r.hinge_open_rad,
            ),
            meta={"positive_motion": "leaf swings outward toward the user"},
        )
        register_interface_mate(model, joint, mate)
        leaves.append(leaf)
    return leaves


def _closure_drop_front_build(
    model: ArticulatedObject,
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> list[object]:
    tag = "closure__drop_front"
    leaves: list[object] = []
    t = r.closure_panel_thickness_m
    rb = r.hinge_barrel_r_m
    setback_v = rb + 0.002
    cfy = r.carcass_front_y_m
    panel_rear = cfy - r.front_reveal_m
    ay = panel_rear - t
    axis_z = r.closure_bay_z0_m + 0.014
    panel_w = r.closure_opening_w_m - 0.008
    panel_h = r.closure_leaf_h_m - 0.010 - setback_v
    stations = (-0.28 * panel_w, 0.28 * panel_w)
    for index, bay_cx in enumerate(r.closure_bay_cx_m):
        for station_index, station in enumerate(stations):
            # 0.030 long so the moving barrels butt against its two end faces.
            carcass.visual(
                Cylinder(radius=rb, length=0.030),
                origin=Origin(
                    xyz=(bay_cx + station, ay, axis_z),
                    rpy=(0.0, math.pi / 2.0, 0.0),
                ),
                material=mats["metal"],
                name=f"{tag}__fixed_knuckle_{index}_{station_index}", material_class_id="metal.stainless_matte",
            )
            _bx(
                carcass,
                (0.030, cfy - ay, 0.014),
                (bay_cx + station, (ay + cfy) / 2.0, axis_z - 0.012),
                mats["metal"],
                f"{tag}__knuckle_plate_{index}_{station_index}",
            )
        leaf = _new_leaf(model, r, index, mechanism="bottom pivot drop front")
        _bx(
            leaf,
            (panel_w, t, panel_h),
            (0.0, t / 2.0, setback_v + panel_h / 2.0),
            mats["front"],
            f"{tag}__panel_{index}",
        )
        for station_index, station in enumerate(stations):
            for barrel_index, offset in enumerate((-0.026, 0.026)):
                leaf.visual(
                    Cylinder(radius=rb, length=0.022),
                    origin=Origin(
                        xyz=(station + offset, 0.0, 0.0),
                        rpy=(0.0, math.pi / 2.0, 0.0),
                    ),
                    material=mats["metal"],
                    name=f"{tag}__barrel_{index}_{station_index}_{barrel_index}", material_class_id="metal.stainless_matte",
                )
                _bx(
                    leaf,
                    (0.020, t + 0.004, setback_v + 0.016),
                    (station + offset, t / 2.0, setback_v / 2.0),
                    mats["metal"],
                    f"{tag}__hinge_strap_{index}_{station_index}_{barrel_index}",
                )
        _bx(
            leaf,
            (min(0.160, panel_w * 0.42), 0.016, 0.018),
            (0.0, -0.008, setback_v + panel_h - 0.030),
            mats["dark"],
            f"{tag}__pull_{index}",
        )
        mate = _axis_mate(
            provider_name=f"storage_topology.closure_hinge_{index}",
            point=(bay_cx, ay, axis_z),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            provider_radius=rb,
            consumer_name=f"closure.hinge_line_{index}",
            consumer_radius=rb * 0.86,
        )
        joint = f"{tag}__leaf_joint_{index}"
        model.articulation(
            joint,
            ArticulationType.REVOLUTE,
            parent=carcass,
            child=leaf,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(
                effort=14.0,
                velocity=1.4,
                lower=0.0,
                upper=1.45,
            ),
            meta={"positive_motion": "panel drops forward and down"},
        )
        register_interface_mate(model, joint, mate)
        leaves.append(leaf)
    return leaves


def _closure_sliding_bypass_doors_build(
    model: ArticulatedObject,
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> list[object]:
    tag = "closure__sliding_bypass_doors"
    leaves: list[object] = []
    t = r.closure_panel_thickness_m
    cfy = r.carcass_front_y_m
    z0 = r.closure_bay_z0_m
    z1 = r.closure_bay_z1_m
    ow = r.closure_opening_w_m
    lw = r.closure_leaf_w_m
    leaf_h = z1 - z0 - 0.004
    mid_z = (z0 + z1) / 2.0
    front_leaf_y0 = cfy + 0.005
    rear_leaf_y0 = cfy + t + 0.012
    # The centre rib bears on the outer leaf and the rear stop bears on the
    # inner leaf, so each bypass panel has real running contact with its track.
    fin_specs = (
        ("front_stop", cfy + 0.0015, 0.003),
        ("centre_rib", cfy + t + 0.007, 0.004),
        ("rear_stop", cfy + 2.0 * t + 0.014, 0.004),
    )
    leaf_index = 0
    for bay_index, bay_cx in enumerate(r.closure_bay_cx_m):
        for fin_name, fin_y, fin_t in fin_specs:
            for rail, rail_z in (("top", z1 - 0.007), ("bottom", z0 + 0.007)):
                _bx(
                    carcass,
                    (ow, fin_t, 0.014),
                    (bay_cx, fin_y, rail_z),
                    mats["metal"],
                    f"{tag}__track_fin_{bay_index}_{rail}_{fin_name}",
                )
        for lane, (y0, closed_cx, axis_x) in enumerate(
            (
                (rear_leaf_y0, bay_cx - ow / 2.0 + lw / 2.0, 1.0),
                (front_leaf_y0, bay_cx + ow / 2.0 - lw / 2.0, -1.0),
            )
        ):
            leaf = _new_leaf(
                model,
                r,
                leaf_index,
                mechanism="bypass slider in a real track groove",
            )
            _bx(
                leaf,
                (lw, t, leaf_h),
                (0.0, 0.0, 0.0),
                mats["front"],
                f"{tag}__panel_{leaf_index}",
            )
            grip_depth = 0.010 if lane == 1 else 0.0025
            _bx(
                leaf,
                (0.018, grip_depth, min(0.100, leaf_h * 0.30)),
                (
                    -axis_x * (lw / 2.0 - 0.030),
                    -t / 2.0 - grip_depth / 2.0,
                    0.0,
                ),
                mats["dark"],
                f"{tag}__grip_{leaf_index}",
            )
            mate = _plane_mate(
                provider_name=f"storage_topology.closure_bay_opening_{leaf_index}",
                provider_point=(closed_cx, y0, mid_z),
                provider_normal=(0.0, -1.0, 0.0),
                provider_extent=(ow, z1 - z0),
                consumer_name=f"closure.leaf_mount_{leaf_index}",
                consumer_point=(0.0, -t / 2.0, 0.0),
                consumer_extent=(lw, leaf_h),
            )
            joint = f"{tag}__leaf_joint_{leaf_index}"
            model.articulation(
                joint,
                ArticulationType.PRISMATIC,
                parent=carcass,
                child=leaf,
                origin=mate.origin,
                axis=(axis_x, 0.0, 0.0),
                motion_limits=MotionLimits(
                    effort=35.0,
                    velocity=0.40,
                    lower=0.0,
                    upper=r.slide_travel_m,
                ),
                meta={"positive_motion": "leaf slides sideways behind its partner"},
            )
            register_interface_mate(model, joint, mate)
            leaves.append(leaf)
            leaf_index += 1
    return leaves


def _closure_tambour_build(
    model: ArticulatedObject,
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> list[object]:
    tag = "closure__tambour"
    leaves: list[object] = []
    cfy = r.carcass_front_y_m
    z0 = r.closure_bay_z0_m
    z1 = r.closure_bay_z1_m
    ow = r.closure_opening_w_m
    ch = r.closure_leaf_h_m
    slat_w = r.closure_leaf_w_m
    bay_height = z1 - z0
    slat_count = max(4, int(ch / 0.048))
    slat_h = (ch - (slat_count - 1) * 0.005) / slat_count
    # Slat and edge-runner section follow the selected leaf thickness, so the
    # track groove, the curtain and the fascia clearance all re-derive together.
    slat_t = max(0.010, r.closure_panel_thickness_m * 0.55)
    runner_t = slat_t + 0.002
    curtain_y = cfy + 0.006 + runner_t / 2.0
    flange_dy = runner_t / 2.0 + 0.003
    for index, bay_cx in enumerate(r.closure_bay_cx_m):
        fascia_z0 = z0 + ch + 0.002
        fascia_z1 = z1 - 0.002
        _bx(
            carcass,
            (ow + 2.0 * _WALL_T - 0.008, 0.016, fascia_z1 - fascia_z0),
            (bay_cx, cfy - 0.008, (fascia_z0 + fascia_z1) / 2.0),
            mats["carcass"],
            f"{tag}__garage_fascia_{index}",
        )
        _bx(
            carcass,
            (ow, 0.140, 0.014),
            (bay_cx, cfy + 0.100, fascia_z1 + 0.006),
            mats["carcass_inner"],
            f"{tag}__garage_ceiling_{index}",
        )
        for side, sign in (("left", -1.0), ("right", 1.0)):
            _bx(
                carcass,
                (_RUNNER_WEB_T, runner_t + 0.014, bay_height),
                (
                    bay_cx + sign * (ow / 2.0 - _RUNNER_WEB_T / 2.0),
                    curtain_y,
                    (z0 + z1) / 2.0,
                ),
                mats["metal"],
                f"{tag}__track_web_{index}_{side}",
            )
            for flange, dy in (("front", -flange_dy), ("rear", flange_dy)):
                _bx(
                    carcass,
                    (0.009, 0.006, bay_height),
                    (
                        bay_cx + sign * (ow / 2.0 - 0.0095),
                        curtain_y + dy,
                        (z0 + z1) / 2.0,
                    ),
                    mats["metal"],
                    f"{tag}__track_flange_{index}_{side}_{flange}",
                )
        leaf = _new_leaf(model, r, index, mechanism="guided slat curtain")
        for slat in range(slat_count):
            _bx(
                leaf,
                (slat_w, slat_t, slat_h),
                (
                    0.0,
                    0.0,
                    -ch / 2.0 + slat_h / 2.0 + slat * (slat_h + 0.005),
                ),
                mats["front"],
                f"{tag}__slat_{index}_{slat}",
            )
        # The flexible backing laps the rear face of every slat, so the curtain
        # stays one connected body instead of a stack of separate slats.
        _bx(
            leaf,
            (slat_w - 0.006, 0.004, ch),
            (0.0, slat_t / 2.0 + 0.001, 0.0),
            mats["dark"],
            f"{tag}__flexible_backing_{index}",
        )
        # The edge runners are the real guided members: they fill the groove
        # between the two track flanges and bear on both flange faces.
        for side, sign in (("left", -1.0), ("right", 1.0)):
            _bx(
                leaf,
                (0.011, runner_t, ch),
                (sign * (slat_w / 2.0 + 0.0055), 0.0, 0.0),
                mats["metal"],
                f"{tag}__edge_runner_{index}_{side}",
            )
        _bx(
            leaf,
            (slat_w, 0.016, 0.020),
            (0.0, -0.001, -ch / 2.0 + 0.010),
            mats["metal"],
            f"{tag}__pull_rail_{index}",
        )
        _bx(
            leaf,
            (0.080, 0.004, 0.012),
            (0.0, -runner_t / 2.0 - 0.002, -ch / 2.0 + 0.010),
            mats["dark"],
            f"{tag}__pull_grip_{index}",
        )
        mate = _plane_mate(
            provider_name=f"storage_topology.closure_bay_opening_{index}",
            provider_point=(
                bay_cx,
                curtain_y - runner_t / 2.0,
                z0 + 0.003 + ch / 2.0,
            ),
            provider_normal=(0.0, -1.0, 0.0),
            provider_extent=(ow, bay_height),
            consumer_name=f"closure.leaf_mount_{index}",
            consumer_point=(0.0, -runner_t / 2.0, 0.0),
            consumer_extent=(slat_w, ch),
        )
        joint = f"{tag}__leaf_joint_{index}"
        model.articulation(
            joint,
            ArticulationType.PRISMATIC,
            parent=carcass,
            child=leaf,
            origin=mate.origin,
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=45.0,
                velocity=0.35,
                lower=0.0,
                upper=r.tambour_travel_m,
            ),
            meta={"positive_motion": "curtain rises into the garage pocket"},
        )
        register_interface_mate(model, joint, mate)
        leaves.append(leaf)
    return leaves


_CLOSURE_BUILDERS = {
    "hinged_door": _closure_hinged_door_build,
    "sliding_bypass_doors": _closure_sliding_bypass_doors_build,
    "drop_front": _closure_drop_front_build,
    "tambour": _closure_tambour_build,
}


# ------------------------------------------------------------ secondary motion


def _secondary_motion_none_build(
    model: ArticulatedObject,
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> list[object]:
    return []


def _tray_center(r: ResolvedConfig) -> tuple[float, float]:
    cx = r.knee_center_x_m if r.has_knee_bay else r.drawer_volume_cx_m
    cy = r.carcass_front_y_m + 0.020 + r.tray_depth_m / 2.0
    return (cx, cy)


def _secondary_motion_keyboard_tray_build(
    model: ArticulatedObject,
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> list[object]:
    tag = "secondary_motion__keyboard_tray"
    tray_cx, tray_cy = _tray_center(r)
    ow = r.secondary_mount_span_m
    tray_w = r.tray_width_m
    tray_d = r.tray_depth_m
    mount_z = r.secondary_mount_z_m
    rail_z = mount_z - 0.025
    rail_d = tray_d + 0.020
    flange_w = _RUNNER_CHANNEL_T - _RUNNER_WEB_T
    for side, sign in (("left", -1.0), ("right", 1.0)):
        _bx(
            carcass,
            (_RUNNER_WEB_T, rail_d, _RUNNER_CHANNEL_H),
            (tray_cx + sign * (ow / 2.0 - _RUNNER_WEB_T / 2.0), tray_cy, rail_z),
            mats["metal"],
            f"{tag}__rail_web_{side}",
        )
        for flange, dz in (("upper", 1.0), ("lower", -1.0)):
            _bx(
                carcass,
                (flange_w, rail_d, _RUNNER_FLANGE_T),
                (
                    tray_cx + sign * (ow / 2.0 - _RUNNER_WEB_T - flange_w / 2.0),
                    tray_cy,
                    rail_z + dz * (_RUNNER_CHANNEL_H - _RUNNER_FLANGE_T) / 2.0,
                ),
                mats["metal"],
                f"{tag}__rail_flange_{side}_{flange}",
            )
        _bx(
            carcass,
            (0.024, rail_d, 0.014),
            (
                tray_cx + sign * (ow / 2.0 - 0.010),
                tray_cy,
                mount_z - 0.007,
            ),
            mats["metal"],
            f"{tag}__rail_mount_plate_{side}",
        )
    tray = model.part(
        f"{tag}__tray",
        meta={
            "role": "keyboard_tray",
            "slot": "secondary_motion",
            "candidate": "keyboard_tray",
            "travel_m": r.tray_travel_m,
        },
    )
    _bx(tray, (tray_w, tray_d, 0.014), (0.0, 0.0, -0.007), mats["dark"], f"{tag}__platform")
    for side, sign in (("left", -1.0), ("right", 1.0)):
        _bx(
            tray,
            (0.012, tray_d - 0.020, 0.012),
            (sign * (tray_w / 2.0 - 0.006), 0.0, 0.006),
            mats["dark"],
            f"{tag}__side_lip_{side}",
        )
        # The slide tab rests on the lower rail flange, giving the tray a real
        # bearing path into the carcass at every pull-out position.
        _bx(
            tray,
            (0.011, tray_d, 0.010),
            (sign * (ow / 2.0 - 0.0115), 0.0, -0.002),
            mats["metal"],
            f"{tag}__slide_tab_{side}",
        )
    _bx(
        tray,
        (tray_w - 0.030, 0.012, 0.012),
        (0.0, tray_d / 2.0 - 0.006, 0.006),
        mats["dark"],
        f"{tag}__back_lip",
    )
    _bx(
        tray,
        (tray_w - 0.030, 0.010, 0.010),
        (0.0, -tray_d / 2.0 + 0.005, 0.005),
        mats["dark"],
        f"{tag}__front_lip",
    )
    _bx(
        tray,
        (min(0.140, tray_w * 0.40), 0.020, 0.018),
        (0.0, -tray_d / 2.0 - 0.010, -0.009),
        mats["metal"],
        f"{tag}__front_pull",
    )
    mate = _plane_mate(
        provider_name="storage_topology.secondary_mount",
        provider_point=(tray_cx, tray_cy, mount_z),
        provider_normal=(0.0, 0.0, -1.0),
        provider_extent=(ow, rail_d),
        consumer_name="secondary_motion.mount_pad",
        consumer_point=(0.0, 0.0, 0.0),
        consumer_extent=(tray_w, tray_d),
        gap=mount_z - rail_z,
    )
    joint = f"{tag}__joint"
    model.articulation(
        joint,
        ArticulationType.PRISMATIC,
        parent=carcass,
        child=tray,
        origin=mate.origin,
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=55.0,
            velocity=0.40,
            lower=0.0,
            upper=r.tray_travel_m,
        ),
        meta={"positive_motion": "tray pulls out toward the user"},
    )
    register_interface_mate(model, joint, mate)
    return [tray]


def _cable_access_panel_shape(w: float, t: float, h: float) -> cq.Workplane:
    panel = cq.Workplane("XY").box(w, t, h)
    try:
        panel = panel.edges("|Y").fillet(min(0.010, w * 0.18, h * 0.18))
    except Exception:  # noqa: BLE001 - rounding is cosmetic
        pass
    slot = cq.Workplane("XY").box(w * 0.65, t * 2.0, 0.024).translate((0.0, 0.0, h * 0.30))
    return panel.cut(slot)


def _secondary_motion_cable_access_hatch_build(
    model: ArticulatedObject,
    carcass: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> list[object]:
    tag = "secondary_motion__cable_access_hatch"
    o_cx, o_w, o_cz, o_h = _back_opening(r)
    t_h = 0.018
    rb = t_h * 0.42 + 0.001
    setback = rb + 0.002
    hx = o_cx - o_w / 2.0
    ay = r.carcass_rear_y_m + r.front_reveal_m + t_h
    panel_w = o_w - setback - 0.004
    panel_h = o_h - 0.008
    stations = (-0.26 * panel_h, 0.26 * panel_h)
    for station_index, station in enumerate(stations):
        carcass.visual(
            Cylinder(radius=rb, length=0.016),
            origin=Origin(xyz=(hx, ay, o_cz + station)),
            material=mats["metal"],
            name=f"{tag}__fixed_knuckle_{station_index}", material_class_id="metal.stainless_matte",
        )
        _bx(
            carcass,
            (0.017, ay - r.carcass_rear_y_m, 0.016),
            (
                hx - 0.0095,
                (r.carcass_rear_y_m + ay) / 2.0,
                o_cz + station,
            ),
            mats["metal"],
            f"{tag}__knuckle_plate_{station_index}",
        )
    hatch = model.part(
        f"{tag}__hatch",
        meta={
            "role": "cable_access_hatch",
            "slot": "secondary_motion",
            "candidate": "cable_access_hatch",
            "real_cable_slot": True,
        },
    )
    hatch.visual(
        mesh_from_cadquery(
            _cable_access_panel_shape(panel_w, t_h, panel_h),
            "office_table_cable_access_panel",
        ),
        origin=Origin(xyz=(setback + panel_w / 2.0, -t_h / 2.0, 0.0)),
        material=mats["front"],
        name=f"{tag}__panel", material_class_id="wood.veneer_panel",
    )
    for station_index, station in enumerate(stations):
        for barrel_index, offset in enumerate((-0.018, 0.018)):
            hatch.visual(
                Cylinder(radius=rb, length=0.020),
                origin=Origin(xyz=(0.0, 0.0, station + offset)),
                material=mats["metal"],
                name=f"{tag}__barrel_{station_index}_{barrel_index}", material_class_id="metal.stainless_matte",
            )
            _bx(
                hatch,
                (0.026, t_h + 0.004, 0.020),
                (0.013, -t_h / 2.0, station + offset),
                mats["metal"],
                f"{tag}__hinge_strap_{station_index}_{barrel_index}",
            )
    _bx(
        hatch,
        (0.018, 0.006, min(0.090, panel_h * 0.45)),
        (setback + panel_w - 0.026, 0.003, 0.0),
        mats["dark"],
        f"{tag}__grip",
    )
    mate = _axis_mate(
        provider_name="storage_topology.secondary_mount_hinge",
        point=(hx, ay, o_cz),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        provider_radius=rb,
        consumer_name="secondary_motion.mount_pad_hinge",
        consumer_radius=rb * 0.86,
    )
    joint = f"{tag}__joint"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=carcass,
        child=hatch,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=6.0,
            velocity=1.2,
            lower=0.0,
            upper=1.05,
        ),
        meta={"positive_motion": "hatch swings rearward for cable access"},
    )
    register_interface_mate(model, joint, mate)
    return [hatch]


_SECONDARY_BUILDERS = {
    "none": _secondary_motion_none_build,
    "keyboard_tray": _secondary_motion_keyboard_tray_build,
    "cable_access_hatch": _secondary_motion_cable_access_hatch_build,
}


def build_office_table_with_doors_or_drawers(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config if config is not None else Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "office_table_with_doors_or_drawers",
            "slot_choices": (
                ("worktop_form", r.worktop_form),
                ("storage_topology", r.storage_topology),
                ("closure", r.closure),
                ("drawer_style", r.drawer_style),
                ("secondary_motion", r.secondary_motion),
                ("drawer_count", r.drawer_count),
            ),
            "source_identity": (
                "raised worktop on a grounded storage carcass with prismatic drawer "
                "trays and an articulated closure over the storage bay"
            ),
            "derived_clearances": {
                "drawer_opening_w_m": r.drawer_opening_w_m,
                "drawer_box_w_m": r.drawer_box_w_m,
                "drawer_travel_m": r.drawer_travel_m,
                "closure_opening_w_m": r.closure_opening_w_m,
                "closure_opening_h_m": r.closure_opening_h_m,
                "closure_leaf_count": r.closure_leaf_count,
            },
        },
    )
    mats = _materials(model, r)
    carcass = model.part(
        "desk_carcass",
        meta={
            "role": "desk_carcass",
            "worktop_height_m": r.worktop_height_m,
            "grounded": True,
            "bay_top_z_m": r.bay_top_z_m,
            "return_end_panel_count": r.return_end_panel_count,
            "has_knee_bay": r.has_knee_bay,
        },
    )
    _WORKTOP_BUILDERS[r.worktop_form](carcass, r, mats)
    _TOPOLOGY_BUILDERS[r.storage_topology](carcass, r, mats)
    _add_drawer_cavity(carcass, r, mats)
    for index in range(r.drawer_count):
        _DRAWER_BUILDERS[r.drawer_style](model, carcass, r, mats, index=index)
    _CLOSURE_BUILDERS[r.closure](model, carcass, r, mats)
    _SECONDARY_BUILDERS[r.secondary_motion](model, carcass, r, mats)
    return model


def _parts_by_role(model: ArticulatedObject, role: str) -> list[object]:
    return [part for part in model.parts if part.meta.get("role") == role]


def _visual_names(part: object) -> set[str]:
    return {visual.name or "" for visual in part.visuals}


def _closure_guard(r: ResolvedConfig, carcass: object, leaves: list[object]) -> bool:
    """Every closure candidate must expose its real guide or hinge hardware."""

    frame_names = _visual_names(carcass)
    leaf_names: set[str] = set()
    for leaf in leaves:
        leaf_names |= _visual_names(leaf)
    tag = f"closure__{r.closure}"
    if r.closure == "hinged_door":
        return any(name.startswith(f"{tag}__fixed_knuckle_") for name in frame_names) and any(
            name.startswith(f"{tag}__barrel_") for name in leaf_names
        )
    if r.closure == "drop_front":
        return any(name.startswith(f"{tag}__fixed_knuckle_") for name in frame_names) and any(
            name.startswith(f"{tag}__hinge_strap_") for name in leaf_names
        )
    if r.closure == "sliding_bypass_doors":
        return any(name.startswith(f"{tag}__track_fin_") for name in frame_names) and any(
            name.startswith(f"{tag}__panel_") for name in leaf_names
        )
    return (
        any(name.startswith(f"{tag}__track_web_") for name in frame_names)
        and any(name.startswith(f"{tag}__garage_fascia_") for name in frame_names)
        and any(name.startswith(f"{tag}__flexible_backing_") for name in leaf_names)
    )


def run_office_table_with_doors_or_drawers_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    carcasses = _parts_by_role(model, "desk_carcass")
    drawers = _parts_by_role(model, "storage_drawer")
    leaves = _parts_by_role(model, "closure_leaf")
    trays = _parts_by_role(model, "keyboard_tray")
    hatches = _parts_by_role(model, "cable_access_hatch")
    carcass = carcasses[0] if carcasses else None
    roots = model.root_parts()
    frame_names = _visual_names(carcass) if carcass is not None else set()
    slide_joints = [
        model.get_articulation(f"drawer_style__{r.drawer_style}__slide_{index}")
        for index in range(r.drawer_count)
    ]
    leaf_joints = [
        model.get_articulation(f"closure__{r.closure}__leaf_joint_{index}")
        for index in range(r.closure_leaf_count)
    ]

    carcass_aabb = ctx.part_world_aabb(carcass) if carcass is not None else None
    wing_visuals = [
        f"worktop_form__{r.worktop_form}__return_end_panel_{index}"
        for index in range(r.return_end_panel_count)
    ]
    ctx.check(
        "category_anchor: raised worktop carried by a grounded storage carcass",
        len(carcasses) == 1
        and len(roots) == 1
        and roots[0].name == "desk_carcass"
        and carcass is not None
        and f"worktop_form__{r.worktop_form}__slab" in frame_names
        and all(name in frame_names for name in wing_visuals)
        and 0.72 <= r.worktop_height_m <= 0.78
        and r.bay_top_z_m < r.top_bottom_z_m
        and carcass_aabb is not None
        and carcass_aabb[0][2] <= 0.003
        and carcass_aabb[1][2] >= r.worktop_height_m - 0.002,
        details=(
            f"roots={[part.name for part in roots]}, wings={r.return_end_panel_count}, "
            f"aabb={carcass_aabb}"
        ),
    )

    tray_parts_ok = True
    for index, drawer in enumerate(drawers):
        names = _visual_names(drawer)
        tag = f"drawer_style__{r.drawer_style}"
        required = {
            f"{tag}__tray_floor",
            f"{tag}__tray_side_left",
            f"{tag}__tray_side_right",
            f"{tag}__tray_back",
            f"{tag}__runner_member_left",
            f"{tag}__runner_member_right",
        }
        if not required.issubset(names) or not any(
            name.startswith(f"{tag}__front_") for name in names
        ):
            tray_parts_ok = False
    channel_ok = all(
        f"drawer_style__{r.drawer_style}__runner_web_{index}_{side}" in frame_names
        and f"drawer_style__{r.drawer_style}__runner_flange_{index}_{side}_upper" in frame_names
        and f"drawer_style__{r.drawer_style}__runner_flange_{index}_{side}_lower" in frame_names
        for index in range(r.drawer_count)
        for side in ("left", "right")
    )
    ctx.check(
        "category_anchor: hollow drawer trays ride real side runners in a derived cavity",
        len(drawers) == r.drawer_count
        and len(slide_joints) == r.drawer_count
        and tray_parts_ok
        and channel_ok
        and all(
            joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(joint.axis) == (0.0, -1.0, 0.0)
            and joint.motion_limits is not None
            and math.isclose(joint.motion_limits.lower, 0.0)
            and math.isclose(joint.motion_limits.upper, r.drawer_travel_m)
            and joint.parent == "desk_carcass"
            for joint in slide_joints
        )
        and r.drawer_box_w_m
        <= r.drawer_opening_w_m - 2.0 * (_RUNNER_CHANNEL_T + _RUNNER_CLEARANCE) + 1e-9
        and r.drawer_box_d_m - r.drawer_travel_m >= 0.080 - 1e-9,
        details=(
            f"drawers={len(drawers)}, trays_ok={tray_parts_ok}, channels_ok={channel_ok}, "
            f"box_w={r.drawer_box_w_m:.4f}, opening={r.drawer_opening_w_m:.4f}, "
            f"retained={r.drawer_box_d_m - r.drawer_travel_m:.4f}"
        ),
    )

    leaf_cover_ok = True
    for index, leaf in enumerate(leaves):
        aabb = ctx.part_world_aabb(leaf)
        if aabb is None:
            leaf_cover_ok = False
            continue
        width = aabb[1][0] - aabb[0][0]
        height = aabb[1][2] - aabb[0][2]
        if r.closure == "sliding_bypass_doors":
            if width < r.closure_opening_w_m * 0.40:
                leaf_cover_ok = False
        elif width < r.closure_opening_w_m * 0.80:
            leaf_cover_ok = False
        if height < r.closure_leaf_h_m * 0.80:
            leaf_cover_ok = False
    ctx.check(
        "category_anchor: closure leaves fill the storage bay openings",
        len(leaves) == r.closure_leaf_count
        and len(leaf_joints) == r.closure_leaf_count
        and leaf_cover_ok
        and all(joint.parent == "desk_carcass" for joint in leaf_joints),
        details=(
            f"leaves={len(leaves)}, expected={r.closure_leaf_count}, "
            f"cover_ok={leaf_cover_ok}, opening="
            f"({r.closure_opening_w_m:.4f}, {r.closure_opening_h_m:.4f})"
        ),
    )

    expected_axes = {
        "hinged_door": [(0.0, 0.0, sign) for sign in r.closure_bay_hinge_sign_m],
        "drop_front": [(1.0, 0.0, 0.0) for _ in r.closure_bay_cx_m],
        "sliding_bypass_doors": [
            axis for _ in r.closure_bay_cx_m for axis in ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
        ],
        "tambour": [(0.0, 0.0, 1.0) for _ in r.closure_bay_cx_m],
    }[r.closure]
    expected_type = (
        ArticulationType.REVOLUTE
        if r.closure in {"hinged_door", "drop_front"}
        else ArticulationType.PRISMATIC
    )
    mates_ok = all(
        (joint.meta or {}).get("interface_mate", {}).get("kind")
        == ("axis" if expected_type == ArticulationType.REVOLUTE else "plane")
        for joint in leaf_joints
    )
    ctx.check(
        "category_anchor: closure mechanism uses its real guide or hinge line",
        carcass is not None
        and _closure_guard(r, carcass, leaves)
        and len(leaf_joints) == len(expected_axes)
        and all(
            joint.articulation_type == expected_type and tuple(joint.axis) == axis
            for joint, axis in zip(leaf_joints, expected_axes)
        )
        and mates_ok,
        details=(
            f"closure={r.closure}, axes={[tuple(j.axis) for j in leaf_joints]}, "
            f"expected={expected_axes}, mates_ok={mates_ok}"
        ),
    )

    ctx.check(
        "derived drawer cavity, level pitch and remainder stay consistent",
        math.isclose(r.drawer_level_pitch_m, r.drawer_front_h_m + _DRAWER_GAP, abs_tol=1e-9)
        and r.drawer_stack_h_m <= r.drawer_bay_h_m + 1e-9
        and r.drawer_remainder_h_m >= -1e-9
        and r.runner_gauge_m > r.drawer_box_w_m
        and r.drawer_front_w_m > r.drawer_opening_w_m
        and r.drawer_front_h_m >= _DRAWER_FRONT_H_MIN,
        details=(
            f"pitch={r.drawer_level_pitch_m:.4f}, stack={r.drawer_stack_h_m:.4f}, "
            f"bay={r.drawer_bay_h_m:.4f}, remainder={r.drawer_remainder_h_m:.4f}"
        ),
    )

    front_gaps: list[float] = []
    for index in range(len(drawers) - 1):
        lower = ctx.part_element_world_aabb(
            drawers[index], elem=f"drawer_style__{r.drawer_style}__front_{index}"
        )
        upper = ctx.part_element_world_aabb(
            drawers[index + 1],
            elem=f"drawer_style__{r.drawer_style}__front_{index + 1}",
        )
        if lower is None or upper is None:
            front_gaps.append(-1.0)
        else:
            front_gaps.append(upper[0][2] - lower[1][2])
    ctx.check(
        "adjacent drawer fronts keep a real reveal at every travel limit",
        all(gap >= 0.004 for gap in front_gaps),
        details=f"front_gaps={[round(gap, 5) for gap in front_gaps]}",
    )

    extend_ok = True
    for joint, drawer in zip(slide_joints, drawers):
        rest = ctx.part_world_position(drawer)
        with ctx.pose({joint: joint.motion_limits.upper}):
            out = ctx.part_world_position(drawer)
        if rest is None or out is None or out[1] > rest[1] - r.drawer_travel_m * 0.9:
            extend_ok = False
    ctx.check(
        "every drawer tray extends toward the user at its upper limit",
        extend_ok and bool(slide_joints),
        details=f"travel={r.drawer_travel_m:.4f}, drawers={len(drawers)}",
    )

    open_ok = True
    for joint, leaf in zip(leaf_joints, leaves):
        closed = ctx.part_world_aabb(leaf)
        with ctx.pose({joint: joint.motion_limits.upper}):
            opened = ctx.part_world_aabb(leaf)
        if closed is None or opened is None:
            open_ok = False
            continue
        moved = max(
            abs(opened[0][axis] - closed[0][axis]) + abs(opened[1][axis] - closed[1][axis])
            for axis in range(3)
        )
        if moved < 0.05:
            open_ok = False
    ctx.check(
        "every closure leaf reaches a distinct open pose",
        open_ok and bool(leaf_joints),
        details=f"closure={r.closure}, leaves={len(leaves)}",
    )

    if r.secondary_motion == "keyboard_tray":
        tray_joint = model.get_articulation("secondary_motion__keyboard_tray__joint")
        tray = trays[0] if trays else None
        rest = ctx.part_world_position(tray) if tray is not None else None
        with ctx.pose({tray_joint: tray_joint.motion_limits.upper}):
            out = ctx.part_world_position(tray) if tray is not None else None
        ctx.check(
            "keyboard tray is guided by real carcass rails and pulls toward the user",
            len(trays) == 1
            and "secondary_motion__keyboard_tray__rail_web_left" in frame_names
            and "secondary_motion__keyboard_tray__rail_web_right" in frame_names
            and tray is not None
            and {
                "secondary_motion__keyboard_tray__slide_tab_left",
                "secondary_motion__keyboard_tray__slide_tab_right",
            }.issubset(_visual_names(tray))
            and tray_joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(tray_joint.axis) == (0.0, -1.0, 0.0)
            and rest is not None
            and out is not None
            and out[1] < rest[1] - r.tray_travel_m * 0.9,
            details=f"trays={len(trays)}, travel={r.tray_travel_m:.4f}",
        )
    if r.secondary_motion == "cable_access_hatch":
        hatch_joint = model.get_articulation("secondary_motion__cable_access_hatch__joint")
        ctx.check(
            "cable access hatch swings on a real hinge over a real back-panel opening",
            len(hatches) == 1
            and any(name.startswith("secondary") for name in frame_names)
            and "storage_topology__" not in ""
            and hatch_joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(hatch_joint.axis) == (0.0, 0.0, 1.0)
            and (hatch_joint.meta or {}).get("interface_mate", {}).get("kind") == "axis"
            and any(name.endswith("__back_frame_left") for name in frame_names)
            and any(name.endswith("__back_frame_upper") for name in frame_names)
            and hatches[0].meta.get("real_cable_slot") is True,
            details=f"hatches={len(hatches)}, opening_w={r.hatch_opening_w_m:.4f}",
        )
    if r.storage_topology == "open_equipment_bay":
        ctx.check(
            "open equipment cubby keeps real shelves and a rear cable grommet",
            any(name.endswith("__cubby_shelf_0") for name in frame_names)
            and any(name.endswith("__rear_cable_grommet") for name in frame_names)
            and r.closure_opening_h_m < r.bay_h_m,
            details=(f"closure_opening_h={r.closure_opening_h_m:.4f}, bay_h={r.bay_h_m:.4f}"),
        )
    if r.storage_topology == "paired_door_pedestal":
        ctx.check(
            "paired closure openings are split by a real central mullion",
            any(name.endswith("__centre_mullion") for name in frame_names)
            and r.closure_bay_count == 2
            and len(r.closure_bay_cx_m) == 2
            and abs(r.closure_bay_cx_m[1] - r.closure_bay_cx_m[0])
            >= r.closure_opening_w_m + _MULLION_T - 1e-9,
            details=f"bay_cx={r.closure_bay_cx_m}, opening={r.closure_opening_w_m:.4f}",
        )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "u_return_open_bay_tambour_max",
        {
            "worktop_form": "u_return",
            "storage_topology": "open_equipment_bay",
            "closure": "tambour",
            "drawer_style": "runner_tray",
            "secondary_motion": "cable_access_hatch",
            "drawer_count": 5,
            "main_span_m": 1.95,
            "main_depth_m": 0.78,
            "return_depth_m": 0.66,
            "worktop_height_m": 0.78,
            "pedestal_width_m": 0.44,
            "closure_panel_thickness_m": 0.026,
            "drawer_wall_m": 0.020,
            "tray_depth_m": 0.34,
            "hatch_width_m": 0.32,
        },
        reason="widest twin-wing top, shortest tambour opening and maximum drawer count",
    ),
    corner_case(
        "compact_corner_paired_tambour_tray",
        {
            "worktop_form": "compact_corner",
            "storage_topology": "paired_door_pedestal",
            "closure": "tambour",
            "drawer_style": "flush_grip_tray",
            "secondary_motion": "keyboard_tray",
            "drawer_count": 5,
            "main_span_m": 1.66,
            "main_depth_m": 0.62,
            "return_depth_m": 0.48,
            "worktop_height_m": 0.72,
            "pedestal_width_m": 0.34,
            "closure_panel_thickness_m": 0.018,
            "drawer_wall_m": 0.014,
            "tray_depth_m": 0.26,
            "hatch_width_m": 0.22,
        },
        reason="narrowest paired tambour openings with the tray in the smallest knee bay",
    ),
    corner_case(
        "credenza_sliding_tray_min",
        {
            "worktop_form": "straight",
            "storage_topology": "drawer_and_door_credenza",
            "closure": "sliding_bypass_doors",
            "drawer_style": "rounded_pull_bar_tray",
            "secondary_motion": "keyboard_tray",
            "drawer_count": 5,
            "main_span_m": 1.66,
            "main_depth_m": 0.62,
            "return_depth_m": 0.48,
            "worktop_height_m": 0.72,
            "pedestal_width_m": 0.34,
            "closure_panel_thickness_m": 0.026,
            "drawer_wall_m": 0.020,
            "tray_depth_m": 0.34,
            "hatch_width_m": 0.22,
        },
        reason="reserved tray zone plus the deepest bypass groove stack in the smallest carcass",
    ),
    corner_case(
        "compact_corner_open_bay_drop_front_single",
        {
            "worktop_form": "compact_corner",
            "storage_topology": "open_equipment_bay",
            "closure": "drop_front",
            "drawer_style": "rounded_pull_bar_tray",
            "secondary_motion": "cable_access_hatch",
            "drawer_count": 1,
            "main_span_m": 1.70,
            "main_depth_m": 0.78,
            "return_depth_m": 0.66,
            "worktop_height_m": 0.72,
            "pedestal_width_m": 0.34,
            "closure_panel_thickness_m": 0.018,
            "drawer_wall_m": 0.014,
            "tray_depth_m": 0.26,
            "hatch_width_m": 0.22,
        },
        reason="shortest drop-front flap over a single drawer with the open cubby above",
    ),
    corner_case(
        "u_return_paired_sliding_hatch",
        {
            "worktop_form": "u_return",
            "storage_topology": "paired_door_pedestal",
            "closure": "sliding_bypass_doors",
            "drawer_style": "runner_tray",
            "secondary_motion": "cable_access_hatch",
            "drawer_count": 4,
            "main_span_m": 1.95,
            "main_depth_m": 0.62,
            "return_depth_m": 0.66,
            "worktop_height_m": 0.78,
            "pedestal_width_m": 0.34,
            "closure_panel_thickness_m": 0.026,
            "drawer_wall_m": 0.018,
            "tray_depth_m": 0.30,
            "hatch_width_m": 0.22,
        },
        reason="four bypass leaves in two narrow openings with the shallowest carcass",
    ),
    corner_case(
        "straight_pedestal_hinged_tray_low",
        {
            "worktop_form": "straight",
            "storage_topology": "drawer_pedestal",
            "closure": "hinged_door",
            "drawer_style": "flush_grip_tray",
            "secondary_motion": "keyboard_tray",
            "drawer_count": 5,
            "main_span_m": 1.66,
            "main_depth_m": 0.62,
            "return_depth_m": 0.48,
            "worktop_height_m": 0.72,
            "pedestal_width_m": 0.44,
            "closure_panel_thickness_m": 0.026,
            "drawer_wall_m": 0.020,
            "tray_depth_m": 0.34,
            "hatch_width_m": 0.32,
        },
        reason="lowest worktop with the thickest hinged leaf and a full drawer stack",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_office_table_with_doors_or_drawers",
    "config_from_seed",
    "resolve_config",
    "run_office_table_with_doors_or_drawers_tests",
]
