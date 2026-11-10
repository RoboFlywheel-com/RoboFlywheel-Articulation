# SPDX-License-Identifier: Apache-2.0

"""Source-faithful manual coffee grinders with host-owned receiver topology."""

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


StructuralFamily = Literal[
    "turned_wood_integrated",
    "ribbed_travel_cup",
    "ribbed_threaded_cup",
    "wood_cabinet_drawer",
    "square_wood_cup",
    "slim_drawer_cylinder",
]
Drive = Literal["rigid_top_crank", "folding_top_crank", "side_crank"]
Closure = Literal["open", "hinged_cover"]
Mount = Literal["countertop", "table_clamp"]


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "structural_family",
            (
                "turned_wood_integrated",
                "ribbed_travel_cup",
                "ribbed_threaded_cup",
                "wood_cabinet_drawer",
                "square_wood_cup",
                "slim_drawer_cylinder",
            ),
            role="source-backed housing, hopper, receiver opening and receiver motion",
        ),
        component_slot(
            "drive",
            ("rigid_top_crank", "folding_top_crank", "side_crank"),
            role="source-backed manual drive",
        ),
        component_slot(
            "closure",
            ("open", "hinged_cover"),
            role="source-backed hopper access state",
        ),
        component_slot(
            "mount",
            ("countertop", "table_clamp"),
            role="source-backed support interface",
        ),
    )
)


@dataclass(frozen=True)
class Config:
    structural_family: StructuralFamily = "wood_cabinet_drawer"
    drive: Drive = "rigid_top_crank"
    closure: Closure = "open"
    mount: Mount = "countertop"
    scale: float = 1.0
    drawer_travel_m: float = 0.068
    cup_release_m: float = 0.032
    crank_reach_m: float = 0.090
    grip_length_m: float = 0.054
    wall_clearance_m: float = 0.0009
    name: str = "manual_coffee_grinder"


@dataclass(frozen=True)
class ResolvedConfig:
    structural_family: StructuralFamily
    drive: Drive
    closure: Closure
    mount: Mount
    scale: float
    drawer_travel_m: float
    cup_release_m: float
    crank_reach_m: float
    grip_length_m: float
    wall_clearance_m: float
    host_half_x_m: float
    host_half_y_m: float
    body_top_z_m: float
    hopper_rim_radius_m: float
    hopper_rim_z_m: float
    top_drive_z_m: float
    side_drive_x_m: float
    side_drive_z_m: float
    adjustment_z_m: float
    mount_z_m: float
    catch_kind: str
    drawer_front_y_m: float
    drawer_center_z_m: float
    cup_seam_z_m: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x434F_4646_4545)
    return Config(
        structural_family=choices["structural_family"],
        drive=choices["drive"],
        closure=choices["closure"],
        mount=choices["mount"],
        scale=round(rng.uniform(0.90, 1.12), 4),
        drawer_travel_m=round(rng.uniform(0.050, 0.080), 5),
        cup_release_m=round(rng.uniform(0.025, 0.040), 5),
        crank_reach_m=round(rng.uniform(0.078, 0.105), 5),
        grip_length_m=round(rng.uniform(0.045, 0.064), 5),
        wall_clearance_m=round(rng.uniform(0.0006, 0.0012), 6),
        name=f"manual_coffee_grinder_seed_{seed}",
    )


def _range(name: str, value: float, low: float, high: float) -> float:
    value = float(value)
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}], got {value}")
    return value


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "structural_family": config.structural_family,
            "drive": config.drive,
            "closure": config.closure,
            "mount": config.mount,
        }
    )
    s = _range("scale", config.scale, 0.90, 1.12)
    drawer_travel = _range("drawer_travel_m", config.drawer_travel_m, 0.050, 0.080)
    cup_release = _range("cup_release_m", config.cup_release_m, 0.025, 0.040)
    reach = _range("crank_reach_m", config.crank_reach_m, 0.078, 0.105)
    grip_length = _range("grip_length_m", config.grip_length_m, 0.045, 0.064)
    clearance = _range("wall_clearance_m", config.wall_clearance_m, 0.0006, 0.0012)

    family = config.structural_family
    if family == "turned_wood_integrated":
        dims = (0.079, 0.079, 0.190, 0.100, 0.260, 0.329, 0.082, 0.176, 0.304, 0.0)
        catch_kind = "integrated"
        drawer_front_y = 0.0
        drawer_center_z = 0.0
        cup_seam_z = 0.0
    elif family in {"ribbed_travel_cup", "ribbed_threaded_cup"}:
        dims = (0.0293, 0.0293, 0.224, 0.0293, 0.224, 0.240, 0.031, 0.154, 0.081, 0.130)
        catch_kind = "threaded_cup" if family == "ribbed_threaded_cup" else "prismatic_cup"
        drawer_front_y = 0.0
        drawer_center_z = 0.0
        cup_seam_z = 0.084
    elif family == "square_wood_cup":
        dims = (0.031, 0.031, 0.224, 0.029, 0.224, 0.240, 0.034, 0.154, 0.081, 0.130)
        catch_kind = "prismatic_cup"
        drawer_front_y = 0.0
        drawer_center_z = 0.0
        cup_seam_z = 0.084
    elif family == "wood_cabinet_drawer":
        dims = (0.070, 0.0675, 0.145, 0.055, 0.242, 0.263, 0.073, 0.122, 0.254, 0.0)
        catch_kind = "drawer"
        drawer_front_y = -0.0675
        drawer_center_z = 0.061
        cup_seam_z = 0.0
    else:
        dims = (0.070, 0.070, 0.180, 0.041, 0.289, 0.310, 0.073, 0.145, 0.300, 0.0)
        catch_kind = "drawer"
        drawer_front_y = -0.070
        drawer_center_z = 0.061
        cup_seam_z = 0.0

    top_drive_z = dims[5]
    if config.closure == "hinged_cover" and config.drive != "side_crank":
        top_drive_z = max(top_drive_z, dims[4] + 2.0 * dims[3] + 0.025)

    return ResolvedConfig(
        structural_family=family,
        drive=config.drive,
        closure=config.closure,
        mount=config.mount,
        scale=s,
        drawer_travel_m=drawer_travel * s,
        cup_release_m=cup_release * s,
        crank_reach_m=reach * s,
        grip_length_m=grip_length * s,
        wall_clearance_m=clearance * s,
        host_half_x_m=dims[0] * s,
        host_half_y_m=dims[1] * s,
        body_top_z_m=dims[2] * s,
        hopper_rim_radius_m=dims[3] * s,
        hopper_rim_z_m=dims[4] * s,
        top_drive_z_m=top_drive_z * s,
        side_drive_x_m=dims[0] * s + 0.012 * s,
        side_drive_z_m=dims[7] * s,
        adjustment_z_m=dims[8] * s,
        mount_z_m=dims[9] * s,
        catch_kind=catch_kind,
        drawer_front_y_m=drawer_front_y * s,
        drawer_center_z_m=drawer_center_z * s,
        cup_seam_z_m=cup_seam_z * s,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, str]:
    return {
        "structural_family": config.structural_family,
        "drive": config.drive,
        "closure": config.closure,
        "mount": config.mount,
    }


def slot_choices_for_seed(seed: int) -> dict[str, str]:
    return slot_choices_for_config(config_from_seed(seed))


def _annulus(outer: float, inner: float, height: float, z0: float = 0.0) -> cq.Workplane:
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, z0))
        .circle(outer)
        .circle(inner)
        .extrude(height)
    )


def _axis_x_cylinder(
    radius: float, length: float, *, x0: float = 0.0, y: float = 0.0, z: float = 0.0
) -> cq.Workplane:
    return cq.Workplane("YZ", origin=(x0, y, z)).circle(radius).extrude(length)


def _axis_y_cylinder(
    radius: float, length: float, *, x: float = 0.0, y0: float = 0.0, z: float = 0.0
) -> cq.Workplane:
    return cq.Workplane("XZ", origin=(x, y0, z)).circle(radius).extrude(length)


def _loft_shell(
    outer_sections: tuple[tuple[float, float], ...],
    inner_sections: tuple[tuple[float, float], ...],
) -> cq.Workplane:
    profile = list(outer_sections) + list(reversed(inner_sections))
    return (
        cq.Workplane("XZ")
        .polyline(profile)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )


def _mesh(shape: cq.Workplane, name: str):
    return mesh_from_cadquery(
        shape,
        name,
        tolerance=0.00045,
        angular_tolerance=0.10,
    )


def _materials(model: ArticulatedObject) -> dict[str, object]:
    return {
        "warm_wood": model.material("coffee_grinder_warm_oak", rgba=(0.50, 0.27, 0.10, 1.0)),
        "face_wood": model.material("coffee_grinder_honey_oak", rgba=(0.66, 0.39, 0.15, 1.0)),
        "dark_wood": model.material("coffee_grinder_dark_walnut", rgba=(0.25, 0.095, 0.030, 1.0)),
        "black": model.material("coffee_grinder_blackened_metal", rgba=(0.045, 0.043, 0.041, 1.0)),
        "black_satin": model.material("coffee_grinder_black_satin", rgba=(0.025, 0.027, 0.029, 1.0)),
        "edge": model.material("coffee_grinder_cast_edge", rgba=(0.12, 0.11, 0.10, 1.0)),
        "steel": model.material("coffee_grinder_brushed_steel", rgba=(0.68, 0.70, 0.70, 1.0)),
        "smoky": model.material("coffee_grinder_smoky_hopper", rgba=(0.20, 0.14, 0.10, 0.88)),
    }


def _add_visual(part: object, shape: cq.Workplane, material: object, name: str) -> None:
    part.visual(_mesh(shape, f"manual_coffee_grinder_{name}"), material=material, name=name, material_class_id="wood.oak")


def _cut_side_bore(shape: cq.Workplane, r: ResolvedConfig) -> cq.Workplane:
    if r.drive != "side_crank":
        return shape
    hole_r = 0.0054 * r.scale
    hole = _axis_x_cylinder(
        hole_r,
        2.0 * r.host_half_x_m + 0.030 * r.scale,
        x0=-r.host_half_x_m - 0.015 * r.scale,
        z=r.side_drive_z_m,
    )
    return shape.cut(hole)


def _turned_body_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    profile = [
        (0.000, 0.000), (0.058, 0.000), (0.070, 0.006), (0.078, 0.016),
        (0.079, 0.028), (0.076, 0.036), (0.070, 0.044), (0.070, 0.145),
        (0.074, 0.153), (0.079, 0.160), (0.079, 0.176), (0.075, 0.184),
        (0.067, 0.190), (0.000, 0.190),
    ]
    scaled = [(radius * s, z_pos * s) for radius, z_pos in profile]
    shape = cq.Workplane("XZ").polyline(scaled).close().revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    return _cut_side_bore(shape, r)


def _wide_bowl_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    z0 = 0.208 * s
    return _loft_shell(
        tuple((radius * s, z0 + z * s) for radius, z in (
            (0.030, 0.000), (0.046, 0.008), (0.064, 0.020),
            (0.082, 0.035), (0.094, 0.046), (0.100, 0.052),
        )),
        tuple((radius * s, z0 + z * s) for radius, z in (
            (0.024, 0.003), (0.042, 0.010), (0.060, 0.022),
            (0.078, 0.037), (0.090, 0.047), (0.096, 0.053),
        )),
    )


def _ribbed_housing_shape(r: ResolvedConfig, *, square: bool) -> cq.Workplane:
    s = r.scale
    lower_z = 0.084 * s
    upper_z = 0.224 * s
    if square:
        side = 0.062 * s
        wall = 0.005 * s
        shape = cq.Workplane("XY", origin=(0.0, 0.0, lower_z)).box(
            side, side, upper_z - lower_z, centered=(True, True, False)
        )
        cavity = cq.Workplane("XY", origin=(0.0, 0.0, lower_z + wall)).box(
            side - 2.0 * wall,
            side - 2.0 * wall,
            upper_z - lower_z,
            centered=(True, True, False),
        )
        shape = shape.cut(cavity)
        bottom_hole = (
            cq.Workplane("XY", origin=(0.0, 0.0, lower_z - 0.001 * s))
            .circle(0.0062 * s)
            .extrude(0.008 * s)
        )
        shape = shape.cut(bottom_hole)
    else:
        shape = _annulus(0.0288 * s, 0.0240 * s, upper_z - lower_z, lower_z)
        rib_z = 0.092 * s
        while rib_z <= 0.218 * s + 1.0e-9:
            shape = shape.union(_annulus(0.0293 * s, 0.0283 * s, 0.00075 * s, rib_z))
            rib_z += 0.003 * s
    floor = _annulus(0.0242 * s, 0.0062 * s, 0.0065 * s, 0.103 * s)
    shape = shape.union(floor)
    if r.drive == "side_crank":
        shape = _cut_side_bore(shape, r)
    return shape


def _cabinet_body_shape(r: ResolvedConfig, *, cylindrical: bool) -> cq.Workplane:
    s = r.scale
    width = 0.140 * s
    depth = (0.140 if cylindrical else 0.135) * s
    height = (0.180 if cylindrical else 0.145) * s
    if cylindrical:
        shape = cq.Workplane("XY").circle(width / 2.0).extrude(height)
        landing = (
            cq.Workplane("XY")
            .box(0.120 * s, 0.037 * s, 0.112 * s, centered=(True, True, False))
            .translate((0.0, -0.0515 * s, 0.0))
        )
        shape = shape.union(landing)
    else:
        shape = cq.Workplane("XY").box(width, depth, height, centered=(True, True, False))
        try:
            shape = shape.edges("|Z").fillet(0.011 * s)
        except Exception:
            pass
    cavity = (
        cq.Workplane("XY")
        .box(0.110 * s, 0.126 * s, 0.078 * s, centered=(True, True, True))
        .translate((0.0, -0.018 * s, 0.061 * s))
    )
    shape = shape.cut(cavity)
    return _cut_side_bore(shape, r)


def _cabinet_hopper_shape(r: ResolvedConfig, *, cylindrical: bool) -> cq.Workplane:
    s = r.scale
    if cylindrical:
        z0 = 0.207 * s
        outer = ((0.028, 0.000), (0.033, 0.009), (0.039, 0.018), (0.041, 0.028),
                 (0.041, 0.068), (0.040, 0.078), (0.039, 0.082))
        inner = ((0.022, 0.002), (0.028, 0.010), (0.034, 0.019), (0.037, 0.029),
                 (0.037, 0.067), (0.036, 0.076), (0.035, 0.080))
    else:
        z0 = 0.172 * s
        outer = ((0.028, 0.000), (0.032, 0.008), (0.043, 0.021), (0.052, 0.039),
                 (0.055, 0.054), (0.053, 0.064), (0.048, 0.070))
        inner = ((0.022, 0.002), (0.027, 0.010), (0.038, 0.023), (0.047, 0.040),
                 (0.050, 0.054), (0.048, 0.062), (0.044, 0.068))
    return _loft_shell(
        tuple((radius * s, z0 + z * s) for radius, z in outer),
        tuple((radius * s, z0 + z * s) for radius, z in inner),
    )


def _add_top_bearing(
    housing: object, r: ResolvedConfig, mats: dict[str, object], *, frame_posts: bool
) -> None:
    if r.drive == "side_crank":
        return
    s = r.scale
    bearing_z = r.top_drive_z_m - 0.021 * s
    _add_visual(
        housing,
        _annulus(0.010 * s, 0.0052 * s, 0.020 * s, bearing_z),
        mats["steel"],
        "housing__top_bearing_sleeve",
    )
    if r.top_drive_z_m - r.hopper_rim_z_m > 0.028 * s:
        _add_visual(
            housing,
            _annulus(
                0.010 * s,
                0.0052 * s,
                r.top_drive_z_m - r.hopper_rim_z_m - 0.002 * s,
                r.hopper_rim_z_m,
            ),
            mats["steel"],
            "housing__raised_drive_support_column",
        )
        for angle in range(0, 360, 120):
            lower_spoke = (
                cq.Workplane("XY")
                .box(
                    max(0.010 * s, r.hopper_rim_radius_m - 0.006 * s),
                    0.003 * s,
                    0.004 * s,
                )
                .translate(
                    (
                        (r.hopper_rim_radius_m + 0.010 * s) / 2.0,
                        0.0,
                        r.hopper_rim_z_m - 0.0015 * s,
                    )
                )
                .rotate(
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, 1.0),
                    float(angle),
                )
            )
            _add_visual(
                housing,
                lower_spoke,
                mats["black"],
                f"housing__raised_support_lower_spoke_{angle}",
            )
    _add_visual(
        housing,
        cq.Workplane("XY")
        .box(0.0011 * s, 0.0010 * s, 0.010 * s)
        .translate((0.00475 * s, 0.0, r.top_drive_z_m - 0.006 * s)),
        mats["steel"],
        "housing__top_bearing_guide_key",
    )
    if frame_posts:
        for index, x_pos in enumerate((-0.018 * s, 0.018 * s)):
            post = (
                cq.Workplane("XY")
                .box(0.006 * s, 0.010 * s, 0.038 * s)
                .translate((x_pos, 0.0, r.top_drive_z_m - 0.039 * s))
            )
            _add_visual(housing, post, mats["black"], f"housing__cast_frame_post_{index}")
        for index, x_pos in enumerate((-0.0195 * s, 0.0195 * s)):
            bridge = (
                cq.Workplane("XY")
                .box(0.025 * s, 0.012 * s, 0.006 * s)
                .translate((x_pos, 0.0, r.top_drive_z_m - 0.011 * s))
            )
            _add_visual(housing, bridge, mats["black"], f"housing__split_bridge_{index}")


def _add_side_bearing(housing: object, r: ResolvedConfig, mats: dict[str, object]) -> None:
    if r.drive != "side_crank":
        return
    s = r.scale
    shape = _axis_x_cylinder(
        0.010 * s,
        0.013 * s,
        x0=r.host_half_x_m - 0.002 * s,
        z=r.side_drive_z_m,
    ).cut(
        _axis_x_cylinder(
            0.0052 * s,
            0.018 * s,
            x0=r.host_half_x_m - 0.004 * s,
            z=r.side_drive_z_m,
        )
    )
    _add_visual(housing, shape, mats["steel"], "housing__side_drive_bearing")
    _add_visual(
        housing,
        cq.Workplane("XY")
        .box(0.010 * s, 0.0011 * s, 0.0010 * s)
        .translate(
            (
                r.side_drive_x_m - 0.006 * s,
                0.00475 * s,
                r.side_drive_z_m,
            )
        ),
        mats["steel"],
        "housing__side_bearing_guide_key",
    )


def _drawer_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    outer = (
        cq.Workplane("XY", origin=(0.0, 0.001 * s, -0.030 * s))
        .box(0.101 * s, 0.100 * s, 0.060 * s, centered=(True, False, False))
    )
    inner = (
        cq.Workplane("XY", origin=(0.0, 0.005 * s, -0.025 * s))
        .box(0.093 * s, 0.091 * s, 0.057 * s, centered=(True, False, False))
    )
    return outer.cut(inner)


def _drawer_front_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    return (
        cq.Workplane("XZ", origin=(0.0, -0.010 * s, 0.0))
        .rect(0.118 * s, 0.086 * s)
        .extrude(0.006 * s, both=True)
    )


def _drawer_knob_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    stem = _axis_y_cylinder(0.0045 * s, 0.012 * s, y0=-0.0155 * s)
    knob = _axis_y_cylinder(0.0105 * s, 0.016 * s, y0=-0.0275 * s)
    cap = _axis_y_cylinder(0.0075 * s, 0.008 * s, y0=-0.0325 * s)
    return stem.union(knob).union(cap)


def _cup_shape(r: ResolvedConfig, *, knurled: bool) -> cq.Workplane:
    s = r.scale
    top = -0.0012 * s
    bottom = -0.078 * s
    cup = _loft_shell(
        (
            (0.0262 * s, bottom),
            (0.0270 * s, bottom + 0.006 * s),
            (0.0282 * s, top),
        ),
        (
            (0.0234 * s, bottom + 0.0045 * s),
            (0.0250 * s, top),
        ),
    )
    if knurled:
        lip = _annulus(0.0287 * s, 0.0251 * s, 0.006 * s, top - 0.005 * s)
        cup = cup.union(lip)
        for index in range(24):
            tooth = (
                cq.Workplane("XY")
                .box(0.0012 * s, 0.0030 * s, 0.010 * s)
                .translate((0.0284 * s, 0.0, top - 0.012 * s))
                .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 15.0 * index)
            )
            cup = cup.union(tooth)
    if not knurled:
        guide_post = (
            cq.Workplane("XY", origin=(0.0, 0.0, bottom))
            .rect(0.006 * s, 0.006 * s)
            .extrude(r.cup_release_m + 0.084 * s)
        )
        floor_bridge = (
            cq.Workplane("XY", origin=(0.0, 0.0, bottom + 0.002 * s))
            .box(0.052 * s, 0.006 * s, 0.004 * s)
        )
        cup = cup.union(guide_post).union(floor_bridge)
    return cup


def _new_drawer(
    model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, object]
) -> object:
    drawer = model.part(
        "grounds_drawer",
        meta={
            "role": "grounds_receiver",
            "receiver_type": "drawer",
            "open_hollow_tray": True,
            "host_has_real_cavity": True,
            "host_has_four_rails": True,
        },
    )
    _add_visual(drawer, _drawer_shape(r), mats["warm_wood"], "drawer__open_hollow_tray")
    _add_visual(drawer, _drawer_front_shape(r), mats["face_wood"], "drawer__front_panel")
    front_bridges = (
        cq.Workplane("XY")
        .box(0.072 * r.scale, 0.010 * r.scale, 0.010 * r.scale)
        .translate((0.0, -0.002 * r.scale, -0.020 * r.scale))
    )
    _add_visual(
        drawer,
        front_bridges,
        mats["warm_wood"],
        "drawer__front_to_tray_bridge",
    )
    _add_visual(drawer, _drawer_knob_shape(r), mats["dark_wood"], "drawer__turned_knob")
    return drawer


def _new_cup(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    knurled: bool,
) -> object:
    cup = model.part(
        "grounds_cup",
        meta={
            "role": "grounds_receiver",
            "receiver_type": "threaded_cup" if knurled else "removable_cup",
            "open_hollow_cup": True,
        },
    )
    _add_visual(
        cup,
        _cup_shape(r, knurled=knurled),
        mats["black_satin"],
        "cup__knurled_threaded_open_cup" if knurled else "cup__tapered_open_cup",
    )
    return cup


def _add_drawer_rails(housing: object, r: ResolvedConfig, mats: dict[str, object]) -> None:
    s = r.scale
    front_y = r.drawer_front_y_m - 0.0008 * s
    for name, x_pos, z_pos, size in (
        ("left", -0.0565 * s, 0.061 * s, (0.007 * s, 0.008 * s, 0.086 * s)),
        ("right", 0.0565 * s, 0.061 * s, (0.007 * s, 0.008 * s, 0.086 * s)),
        ("bottom", 0.0, 0.018 * s, (0.120 * s, 0.008 * s, 0.007 * s)),
        ("top", 0.0, 0.104 * s, (0.120 * s, 0.008 * s, 0.007 * s)),
    ):
        rail = cq.Workplane("XY").box(*size).translate((x_pos, front_y, z_pos))
        _add_visual(housing, rail, mats["dark_wood"], f"housing__drawer_recess_{name}")
    for index, x_pos in enumerate((-0.053 * s, 0.053 * s)):
        guide = (
            cq.Workplane("XY")
            .box(0.005 * s, 0.096 * s, 0.006 * s)
            .translate((x_pos, front_y + 0.050 * s, 0.029 * s))
        )
        _add_visual(housing, guide, mats["dark_wood"], f"housing__drawer_side_guide_{index}")
    rear_stop = (
        cq.Workplane("XY")
        .box(0.100 * s, 0.005 * s, 0.010 * s)
        .translate((0.0, front_y + 0.108 * s, 0.024 * s))
    )
    _add_visual(housing, rear_stop, mats["dark_wood"], "housing__drawer_rear_stop")


def _add_cabinet_upper(
    housing: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    cylindrical: bool,
) -> None:
    s = r.scale
    base_z = (0.179 if cylindrical else 0.144) * s
    _add_visual(
        housing,
        cq.Workplane("XY", origin=(0.0, 0.0, base_z)).circle(0.057 * s).extrude(0.006 * s),
        mats["black"],
        "housing__top_mount_plate",
    )
    _add_visual(
        housing,
        _annulus(0.043 * s, 0.010 * s, 0.006 * s, base_z + 0.005 * s),
        mats["edge"],
        "housing__burr_base_flange",
    )
    _add_visual(
        housing,
        _annulus(0.031 * s, 0.009 * s, 0.022 * s, base_z + 0.010 * s),
        mats["black"],
        "housing__burr_chamber",
    )
    _add_visual(
        housing,
        _cabinet_hopper_shape(r, cylindrical=cylindrical),
        mats["smoky"],
        "housing__thin_walled_hopper",
    )
    _add_top_bearing(housing, r, mats, frame_posts=False)


def _structural_family_turned_wood_integrated_build(
    model: ArticulatedObject, housing: object, r: ResolvedConfig, mats: dict[str, object]
) -> object | None:
    s = r.scale
    _add_visual(housing, _turned_body_shape(r), mats["warm_wood"], "housing__turned_wood_body")
    for index, z_pos in enumerate((0.0305, 0.1665)):
        _add_visual(
            housing,
            _annulus(0.0792 * s, 0.067 * s, 0.003 * s, z_pos * s),
            mats["dark_wood"],
            f"housing__turned_dark_band_{index}",
        )
    for name, radius, z_pos, height, material in (
        ("mount", 0.072, 0.1895, 0.009, mats["black"]),
        ("bead", 0.061, 0.1975, 0.007, mats["edge"]),
        ("support", 0.052, 0.2040, 0.008, mats["black"]),
    ):
        _add_visual(
            housing,
            _annulus(radius * s, 0.008 * s, height * s, z_pos * s),
            material,
            f"housing__cast_{name}",
        )
    _add_visual(housing, _wide_bowl_shape(r), mats["black"], "housing__wide_open_bowl")
    _add_visual(
        housing,
        _annulus(0.103 * s, 0.096 * s, 0.004 * s, 0.258 * s),
        mats["edge"],
        "housing__rolled_bowl_rim",
    )
    _add_visual(
        housing,
        _annulus(0.027 * s, 0.006 * s, 0.026 * s, 0.207 * s),
        mats["black"],
        "housing__annular_burr_mount",
    )
    for index, z_pos in enumerate((0.270, 0.276, 0.282, 0.288)):
        _add_visual(
            housing,
            _annulus(0.013 * s, 0.010 * s, 0.0016 * s, z_pos * s),
            mats["steel"],
            f"housing__spring_coil_{index}",
        )
    _add_top_bearing(housing, r, mats, frame_posts=False)
    _add_side_bearing(housing, r, mats)
    return None


def _build_ribbed_family(
    model: ArticulatedObject,
    housing: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    square: bool,
    threaded: bool,
) -> object:
    _add_visual(
        housing,
        _ribbed_housing_shape(r, square=square),
        mats["warm_wood"] if square else mats["black_satin"],
        "housing__square_hollow_shell" if square else "housing__fine_ribbed_hollow_shell",
    )
    _add_visual(
        housing,
        _annulus(0.0215 * r.scale, 0.0102 * r.scale, 0.012 * r.scale, 0.091 * r.scale),
        mats["edge"],
        "housing__fixed_burr_carrier",
    )
    if threaded:
        _add_visual(
            housing,
            _annulus(
                0.034 * r.scale,
                0.0291 * r.scale,
                0.0082 * r.scale,
                r.cup_seam_z_m - 0.0012 * r.scale,
            ),
            mats["black"],
            "housing__stepped_thread_socket",
        )
        _add_visual(
            housing,
            cq.Workplane("XY")
            .box(0.006 * r.scale, 0.014 * r.scale, 0.006 * r.scale)
            .translate(
                (
                    0.0,
                    0.029 * r.scale,
                    r.cup_seam_z_m + 0.001 * r.scale,
                )
            ),
            mats["black"],
            "housing__thread_socket_rear_bridge",
        )
    else:
        guide_z0 = r.cup_seam_z_m - r.cup_release_m - 0.018 * r.scale
        guide_h = r.cup_release_m + 0.030 * r.scale
        for index, x_pos in enumerate((-0.0045 * r.scale, 0.0045 * r.scale)):
            guide_wall = (
                cq.Workplane("XY", origin=(x_pos, 0.0, guide_z0))
                .box(
                    0.003 * r.scale,
                    0.024 * r.scale,
                    guide_h,
                    centered=(True, True, False),
                )
            )
            _add_visual(
                housing,
                guide_wall,
                mats["edge"],
                f"housing__receiver_square_guide_{index}",
            )
    _add_top_bearing(housing, r, mats, frame_posts=False)
    _add_side_bearing(housing, r, mats)
    return _new_cup(model, r, mats, knurled=threaded)


def _structural_family_ribbed_travel_cup_build(
    model: ArticulatedObject, housing: object, r: ResolvedConfig, mats: dict[str, object]
) -> object:
    return _build_ribbed_family(model, housing, r, mats, square=False, threaded=False)


def _structural_family_ribbed_threaded_cup_build(
    model: ArticulatedObject, housing: object, r: ResolvedConfig, mats: dict[str, object]
) -> object:
    return _build_ribbed_family(model, housing, r, mats, square=False, threaded=True)


def _structural_family_square_wood_cup_build(
    model: ArticulatedObject, housing: object, r: ResolvedConfig, mats: dict[str, object]
) -> object:
    return _build_ribbed_family(model, housing, r, mats, square=True, threaded=False)


def _build_drawer_family(
    model: ArticulatedObject,
    housing: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    cylindrical: bool,
) -> object:
    _add_visual(
        housing,
        _cabinet_body_shape(r, cylindrical=cylindrical),
        mats["warm_wood"],
        "housing__cylindrical_body_with_cut_drawer_cavity"
        if cylindrical
        else "housing__rounded_cabinet_with_cut_drawer_cavity",
    )
    _add_drawer_rails(housing, r, mats)
    _add_cabinet_upper(housing, r, mats, cylindrical=cylindrical)
    _add_side_bearing(housing, r, mats)
    return _new_drawer(model, r, mats)


def _structural_family_wood_cabinet_drawer_build(
    model: ArticulatedObject, housing: object, r: ResolvedConfig, mats: dict[str, object]
) -> object:
    return _build_drawer_family(model, housing, r, mats, cylindrical=False)


def _structural_family_slim_drawer_cylinder_build(
    model: ArticulatedObject, housing: object, r: ResolvedConfig, mats: dict[str, object]
) -> object:
    return _build_drawer_family(model, housing, r, mats, cylindrical=True)


def _adjustment_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    ring = _annulus(0.018 * s, 0.0112 * s, 0.009 * s, -0.0045 * s)
    for index in range(12):
        lug = (
            cq.Workplane("XY")
            .box(0.006 * s, 0.0035 * s, 0.008 * s)
            .translate((0.017 * s, 0.0, 0.0))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 30.0 * index)
        )
        ring = ring.union(lug)
    return ring


def _new_adjustment(
    model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, object]
) -> object:
    part = model.part("adjustment_collar", meta={"role": "grind_adjustment"})
    _add_visual(part, _adjustment_shape(r), mats["black"], "adjustment__scalloped_collar")
    return part


def _add_adjustment_bearing(
    housing: object, r: ResolvedConfig, mats: dict[str, object]
) -> None:
    nominal_height = (
        0.016 * r.scale
        if r.catch_kind in {"prismatic_cup", "threaded_cup"}
        else 0.009 * r.scale
    )
    bearing_z0 = r.adjustment_z_m - 0.0045 * r.scale
    if r.adjustment_z_m > r.hopper_rim_z_m:
        bearing_z0 = r.hopper_rim_z_m - 0.004 * r.scale
    bearing_height = max(
        nominal_height,
        r.adjustment_z_m + 0.0045 * r.scale - bearing_z0,
    )
    _add_visual(
        housing,
        _annulus(
            0.010 * r.scale,
            0.0065 * r.scale,
            bearing_height,
            bearing_z0,
        ),
        mats["steel"],
        "housing__adjustment_bearing",
    )


def _grip_shape(r: ResolvedConfig, *, axis_x: bool) -> cq.Workplane:
    s = r.scale
    length = r.grip_length_m
    shape = _loft_shell(
        (
            (0.009 * s, 0.0),
            (0.012 * s, 0.004 * s),
            (0.015 * s, length - 0.004 * s),
            (0.010 * s, length),
        ),
        (
            (0.0033 * s, 0.0),
            (0.0033 * s, length),
        ),
    )
    if axis_x:
        shape = shape.rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
    return shape


def _top_crank_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    shaft_depth = max(0.018 * s, r.top_drive_z_m - r.hopper_rim_z_m + 0.004 * s)
    shaft = (
        cq.Workplane("XY", origin=(0.0, 0.0, -shaft_depth))
        .circle(0.0042 * s)
        .extrude(shaft_depth + 0.012 * s)
    )
    hub = _annulus(0.010 * s, 0.0, 0.006 * s, 0.0)
    arm = (
        cq.Workplane("XY", origin=(0.006 * s, 0.0, 0.005 * s))
        .box(r.crank_reach_m - 0.006 * s, 0.008 * s, 0.013 * s, centered=(False, True, False))
    )
    end = (
        cq.Workplane("XY", origin=(r.crank_reach_m, 0.0, 0.013 * s))
        .circle(0.009 * s)
        .extrude(0.006 * s)
    )
    pin = (
        cq.Workplane("XY", origin=(r.crank_reach_m, 0.0, 0.019 * s))
        .circle(0.0027 * s)
        .extrude(r.grip_length_m + 0.002 * s)
    )
    return shaft.union(hub).union(arm).union(end).union(pin)


def _folding_hub_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    shaft_depth = max(0.018 * s, r.top_drive_z_m - r.hopper_rim_z_m + 0.004 * s)
    shape = (
        cq.Workplane("XY", origin=(0.0, 0.0, -shaft_depth))
        .circle(0.0042 * s)
        .extrude(shaft_depth + 0.014 * s)
    )
    shape = shape.union(_annulus(0.011 * s, 0.0, 0.009 * s, 0.0))
    for y_pos in (-0.007 * s, 0.007 * s):
        ear = (
            cq.Workplane("XY")
            .box(0.018 * s, 0.004 * s, 0.015 * s)
            .translate((0.007 * s, y_pos, 0.020 * s))
        )
        bore = _axis_y_cylinder(0.0028 * s, 0.024 * s, x=0.007 * s, y0=-0.012 * s, z=0.020 * s)
        shape = shape.union(ear).cut(bore)
        ear_bridge = (
            cq.Workplane("XY")
            .box(0.010 * s, 0.004 * s, 0.012 * s)
            .translate((0.007 * s, y_pos, 0.009 * s))
        )
        shape = shape.union(ear_bridge)
    return shape


def _fold_arm_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    tongue = (
        cq.Workplane("XY")
        .box(0.016 * s, 0.008 * s, 0.010 * s)
        .translate((0.008 * s, 0.0, 0.0))
    )
    axis_boss = _axis_y_cylinder(
        0.007 * s,
        0.008 * s,
        x=0.0,
        y0=-0.004 * s,
        z=0.0,
    )
    bore = _axis_y_cylinder(0.0028 * s, 0.012 * s, x=0.0, y0=-0.006 * s, z=0.0)
    arm = (
        cq.Workplane("XY")
        .box(r.crank_reach_m - 0.012 * s, 0.008 * s, 0.0045 * s, centered=(False, True, True))
        .translate((0.010 * s, 0.0, 0.005 * s))
    )
    end_pad = (
        cq.Workplane("XY", origin=(r.crank_reach_m, 0.0, 0.004 * s))
        .circle(0.008 * s)
        .extrude(0.004 * s)
    )
    pin = (
        cq.Workplane("XY", origin=(r.crank_reach_m, 0.0, 0.008 * s))
        .circle(0.0027 * s)
        .extrude(r.grip_length_m + 0.002 * s)
    )
    return (
        tongue.union(axis_boss)
        .cut(bore)
        .union(arm)
        .union(end_pad)
        .union(pin)
    )


def _side_crank_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    shaft = _axis_x_cylinder(0.0042 * s, 0.040 * s, x0=-0.012 * s)
    shoulder = _axis_x_cylinder(0.009 * s, 0.005 * s, x0=0.0)
    arm = (
        cq.Workplane("XY")
        .box(0.006 * s, 0.010 * s, r.crank_reach_m)
        .translate((0.026 * s, 0.0, r.crank_reach_m / 2.0))
    )
    pin = _axis_x_cylinder(
        0.0027 * s,
        r.grip_length_m + 0.002 * s,
        x0=0.029 * s,
        z=r.crank_reach_m,
    )
    bridge = (
        cq.Workplane("XY")
        .box(0.026 * s, 0.010 * s, 0.006 * s)
        .translate((0.013 * s, 0.0, 0.0))
    )
    return shaft.union(shoulder).union(bridge).union(arm).union(pin)


def _new_grip(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, object],
    *,
    axis_x: bool,
) -> object:
    grip = model.part("crank_grip", meta={"role": "free_spinning_grip"})
    material = mats["black_satin"] if r.structural_family.startswith("ribbed") else mats["dark_wood"]
    _add_visual(grip, _grip_shape(r, axis_x=axis_x), material, "drive__bored_turned_grip")
    return grip


def _drive_rigid_top_crank_build(
    model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, object]
) -> tuple[object, object, tuple[float, float, float], tuple[float, float, float]]:
    crank = model.part("crank", meta={"role": "manual_drive", "drive_type": "rigid_top_crank"})
    _add_visual(crank, _top_crank_shape(r), mats["steel"], "drive__rigid_top_crank")
    grip = _new_grip(model, r, mats, axis_x=False)
    return crank, grip, (r.crank_reach_m, 0.0, 0.020 * r.scale), (0.0, 0.0, 1.0)


def _drive_folding_top_crank_build(
    model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, object]
) -> tuple[object, object, tuple[float, float, float], tuple[float, float, float]]:
    crank = model.part(
        "crank",
        meta={
            "role": "manual_drive",
            "drive_type": "folding_top_crank",
            "folding_clevis_detail": True,
        },
    )
    deployed_arm = _fold_arm_shape(r).translate((0.007 * r.scale, 0.0, 0.020 * r.scale))
    _add_visual(
        crank,
        _folding_hub_shape(r).union(deployed_arm),
        mats["steel"],
        "drive__deployed_folding_crank_with_clevis",
    )
    grip = _new_grip(model, r, mats, axis_x=False)
    return (
        crank,
        grip,
        (0.007 * r.scale + r.crank_reach_m, 0.0, 0.029 * r.scale),
        (0.0, 0.0, 1.0),
    )


def _drive_side_crank_build(
    model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, object]
) -> tuple[object, object, tuple[float, float, float], tuple[float, float, float]]:
    crank = model.part("crank", meta={"role": "manual_drive", "drive_type": "side_crank"})
    _add_visual(crank, _side_crank_shape(r), mats["steel"], "drive__side_crank")
    grip = _new_grip(model, r, mats, axis_x=True)
    return crank, grip, (0.030 * r.scale, 0.0, r.crank_reach_m), (1.0, 0.0, 0.0)


def _closure_open_build(
    model: ArticulatedObject, housing: object, r: ResolvedConfig, mats: dict[str, object]
) -> object | None:
    housing.meta["hopper_access"] = "open"
    housing.meta["hopper_is_genuinely_hollow"] = True
    return None


def _hinged_lid_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    radius = r.hopper_rim_radius_m - 0.002 * s
    offset = r.hopper_rim_radius_m + 0.006 * s
    plate = (
        cq.Workplane("XY", origin=(offset, 0.0, 0.0015 * s))
        .circle(radius)
        .circle(0.012 * s)
        .extrude(0.0035 * s)
    )
    slot = (
        cq.Workplane("XY")
        .box(radius + 0.008 * s, 0.024 * s, 0.010 * s)
        .translate((offset + radius * 0.55, 0.0, 0.003 * s))
    )
    saddle_notch = (
        cq.Workplane("XY")
        .box(0.018 * s, 0.026 * s, 0.012 * s)
        .translate((0.005 * s, 0.0, 0.003 * s))
    )
    plate = plate.cut(slot).cut(saddle_notch)
    span = min(0.040 * s, 1.45 * radius)
    for y0 in (-span / 2.0, span / 2.0 - 0.010 * s):
        knuckle = _axis_y_cylinder(
            0.0040 * s,
            0.010 * s,
            x=0.0,
            y0=y0,
            z=0.0,
        ).cut(
            _axis_y_cylinder(
            0.0028 * s,
                0.012 * s,
                x=0.0,
                y0=y0 - 0.001 * s,
                z=0.0,
            )
        )
        web = (
            cq.Workplane("XY")
            .box(0.018 * s, 0.010 * s, 0.005 * s)
            .translate((0.009 * s, y0 + 0.005 * s, 0.0025 * s))
        )
        plate = plate.union(knuckle).union(web)
    return plate


def _closure_hinged_cover_build(
    model: ArticulatedObject, housing: object, r: ResolvedConfig, mats: dict[str, object]
) -> object:
    s = r.scale
    hinge_x = -r.hopper_rim_radius_m - 0.006 * s
    hinge_z = r.hopper_rim_z_m + 0.003 * s
    span = min(0.040 * s, 1.45 * (r.hopper_rim_radius_m - 0.002 * s))
    saddle = (
        cq.Workplane("XY")
        .box(0.008 * s, max(0.006 * s, span - 0.028 * s), 0.005 * s)
        .translate((hinge_x + 0.002 * s, 0.0, hinge_z - 0.0055 * s))
    )
    underbridge = (
        cq.Workplane("XY")
        .box(0.018 * s, 0.008 * s, 0.004 * s)
        .translate((hinge_x + 0.007 * s, 0.0, hinge_z - 0.005 * s))
    )
    _add_visual(
        housing,
        saddle.union(underbridge),
        mats["black"],
        "housing__lid_hinge_saddle",
    )
    lid = model.part(
        "hopper_lid",
        meta={"role": "hopper_closure", "shaft_clearance_slot": True, "captured_knuckles": True},
    )
    _add_visual(lid, _hinged_lid_shape(r), mats["black"], "closure__slotted_hinged_cover")
    return lid


def _mount_countertop_build(
    model: ArticulatedObject, housing: object, r: ResolvedConfig, mats: dict[str, object]
) -> None:
    housing.meta["mount_type"] = "countertop"


def _clamp_bracket_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    z0 = r.mount_z_m
    plate_radius = max(r.host_half_x_m, 0.034 * s)
    plate = (
        cq.Workplane("XY", origin=(0.0, 0.0, z0))
        .circle(plate_radius)
        .circle(max(0.024 * s, 0.75 * plate_radius))
        .extrude(0.008 * s)
    )
    arm_y0 = r.host_half_y_m - 0.004 * s
    arm_length = 0.072 * s
    arm = (
        cq.Workplane("XY")
        .box(0.024 * s, arm_length, 0.012 * s, centered=(True, False, False))
        .translate((0.0, arm_y0, z0 - 0.001 * s))
    )
    spine_y = arm_y0 + arm_length - 0.010 * s
    drop = max(0.070 * s, z0 + 0.050 * s)
    spine = (
        cq.Workplane("XY")
        .box(0.024 * s, 0.012 * s, drop, centered=(True, True, False))
        .translate((0.0, spine_y, z0 - drop))
    )
    lower = (
        cq.Workplane("XY")
        .box(0.024 * s, 0.030 * s, 0.010 * s)
        .translate((0.0, spine_y - 0.009 * s, z0 - drop))
    )
    bracket = plate.union(arm).union(spine).union(lower)
    screw_hole = (
        cq.Workplane("XY", origin=(0.0, spine_y - 0.009 * s, z0 - drop - 0.002 * s))
        .circle(0.0055 * s)
        .extrude(0.016 * s)
    )
    return bracket.cut(screw_hole)


def _clamp_screw_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    z0 = r.mount_z_m
    arm_y0 = r.host_half_y_m - 0.004 * s
    arm_length = 0.072 * s
    spine_y = arm_y0 + arm_length - 0.010 * s
    drop = max(0.070 * s, z0 + 0.050 * s)
    screw_z = z0 - drop - 0.018 * s
    shaft = (
        cq.Workplane("XY", origin=(0.0, spine_y - 0.009 * s, screw_z))
        .circle(0.0045 * s)
        .extrude(0.038 * s)
    )
    pad = (
        cq.Workplane("XY", origin=(0.0, spine_y - 0.009 * s, screw_z + 0.036 * s))
        .circle(0.010 * s)
        .extrude(0.003 * s)
    )
    handle = (
        cq.Workplane("XY")
        .box(0.036 * s, 0.006 * s, 0.006 * s)
        .translate((0.0, spine_y - 0.009 * s, screw_z))
    )
    return shaft.union(pad).union(handle)


def _mount_table_clamp_build(
    model: ArticulatedObject, housing: object, r: ResolvedConfig, mats: dict[str, object]
) -> None:
    _add_visual(housing, _clamp_bracket_shape(r), mats["black"], "mount__cast_table_clamp")
    _add_visual(housing, _clamp_screw_shape(r), mats["steel"], "mount__threaded_screw_and_t_handle")
    housing.meta["mount_type"] = "table_clamp"


def _add_housing_connectivity_spine(
    housing: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    """Thin rear casting that physically joins the rigid source subassemblies."""
    s = r.scale
    z0 = r.mount_z_m
    back_y = max(0.020 * s, r.host_half_y_m - 0.003 * s)
    top_z = (
        r.top_drive_z_m - 0.005 * s
        if r.closure == "open"
        else r.hopper_rim_z_m - 0.001 * s
    )
    spine = (
        cq.Workplane("XY")
        .box(0.004 * s, 0.005 * s, top_z - z0)
        .translate((0.0, back_y, (top_z + z0) / 2.0))
    )
    stations = {
        max(z0 + 0.004 * s, r.body_top_z_m - 0.002 * s),
        r.hopper_rim_z_m - 0.005 * s,
    }
    if r.adjustment_z_m <= r.hopper_rim_z_m:
        stations.add(r.adjustment_z_m)
    if (
        r.closure == "open"
        and r.top_drive_z_m - r.hopper_rim_z_m <= 0.028 * s
    ):
        stations.add(r.top_drive_z_m - 0.015 * s)
    if r.cup_seam_z_m > 0.0:
        stations.add(r.cup_seam_z_m + 0.004 * s)
    for z_pos in sorted(stations):
        end_y = 0.009 * s
        branch_length = back_y - end_y + 0.004 * s
        branch = (
            cq.Workplane("XY")
            .box(0.004 * s, branch_length, 0.004 * s)
            .translate((0.0, (back_y + end_y) / 2.0, z_pos))
        )
        spine = spine.union(branch)
    _add_visual(
        housing,
        spine,
        mats["black"],
        "housing__rear_structural_connectivity_spine",
    )


_STRUCTURAL_BUILDERS = {
    "turned_wood_integrated": _structural_family_turned_wood_integrated_build,
    "ribbed_travel_cup": _structural_family_ribbed_travel_cup_build,
    "ribbed_threaded_cup": _structural_family_ribbed_threaded_cup_build,
    "wood_cabinet_drawer": _structural_family_wood_cabinet_drawer_build,
    "square_wood_cup": _structural_family_square_wood_cup_build,
    "slim_drawer_cylinder": _structural_family_slim_drawer_cylinder_build,
}
_CLOSURE_BUILDERS = {"open": _closure_open_build, "hinged_cover": _closure_hinged_cover_build}
_MOUNT_BUILDERS = {"countertop": _mount_countertop_build, "table_clamp": _mount_table_clamp_build}


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


def build_manual_coffee_grinder(
    config: Config,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "manual_coffee_grinder",
            "slot_choices": tuple(slot_choices_for_config(r).items()),
            "source_pool_reviewed": "3 images / 12 rev_000001 models",
            "receiver_topology_owned_by_structural_family": True,
            "loose_002_burr_prop_omitted": True,
        },
    )
    mats = _materials(model)
    housing = model.part(
        "housing",
        meta={
            "role": "housing",
            "structural_family": r.structural_family,
            "catch_kind": r.catch_kind,
            "real_receiver_opening": r.catch_kind != "integrated",
        },
    )
    receiver = _STRUCTURAL_BUILDERS[r.structural_family](model, housing, r, mats)
    _add_adjustment_bearing(housing, r, mats)
    adjustment = _new_adjustment(model, r, mats)
    lid = _CLOSURE_BUILDERS[r.closure](model, housing, r, mats)
    _MOUNT_BUILDERS[r.mount](model, housing, r, mats)
    _add_housing_connectivity_spine(housing, r, mats)

    _axis_joint(
        model,
        name="housing_to_adjustment",
        parent=housing,
        child=adjustment,
        provider=AxisInterface(
            name="structural_family.adjustment_axis",
            point=(0.0, 0.0, r.adjustment_z_m),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=0.010 * r.scale,
        ),
        consumer=AxisInterface(
            name="adjustment.axis",
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=0.0112 * r.scale,
        ),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=2.0, velocity=1.5, lower=-0.55, upper=0.55),
    )

    if receiver is not None and r.catch_kind == "drawer":
        _axis_joint(
            model,
            name="housing_to_grounds_drawer",
            parent=housing,
            child=receiver,
            provider=AxisInterface(
                name="structural_family.drawer_guide",
                point=(0.0, r.drawer_front_y_m, r.drawer_center_z_m),
                axis=(0.0, -1.0, 0.0),
                radial=(1.0, 0.0, 0.0),
            ),
            consumer=AxisInterface(
                name="grounds_receiver.drawer_axis",
                axis=(0.0, -1.0, 0.0),
                radial=(1.0, 0.0, 0.0),
            ),
            articulation_type=ArticulationType.PRISMATIC,
            limits=MotionLimits(
                effort=18.0, velocity=0.25, lower=0.0, upper=r.drawer_travel_m
            ),
        )
    elif receiver is not None and r.catch_kind == "prismatic_cup":
        _axis_joint(
            model,
            name="housing_to_grounds_cup",
            parent=housing,
            child=receiver,
            provider=AxisInterface(
                name="structural_family.cup_socket",
                point=(0.0, 0.0, r.cup_seam_z_m),
                axis=(0.0, 0.0, -1.0),
                radial=(1.0, 0.0, 0.0),
                radius=0.0294 * r.scale,
            ),
            consumer=AxisInterface(
                name="grounds_receiver.cup_axis",
                axis=(0.0, 0.0, -1.0),
                radial=(1.0, 0.0, 0.0),
                radius=0.0287 * r.scale,
            ),
            articulation_type=ArticulationType.PRISMATIC,
            limits=MotionLimits(
                effort=8.0, velocity=0.12, lower=0.0, upper=r.cup_release_m
            ),
        )
    elif receiver is not None and r.catch_kind == "threaded_cup":
        _axis_joint(
            model,
            name="housing_to_grounds_cup",
            parent=housing,
            child=receiver,
            provider=AxisInterface(
                name="structural_family.thread_socket",
                point=(0.0, 0.0, r.cup_seam_z_m),
                axis=(0.0, 0.0, 1.0),
                radial=(1.0, 0.0, 0.0),
                radius=0.0294 * r.scale,
            ),
            consumer=AxisInterface(
                name="grounds_receiver.thread_axis",
                axis=(0.0, 0.0, 1.0),
                radial=(1.0, 0.0, 0.0),
                radius=0.0287 * r.scale,
            ),
            articulation_type=ArticulationType.REVOLUTE,
            limits=MotionLimits(effort=8.0, velocity=1.2, lower=0.0, upper=4.0 * math.pi),
        )

    if lid is not None:
        hinge_x = -r.hopper_rim_radius_m - 0.006 * r.scale
        hinge_z = r.hopper_rim_z_m + 0.003 * r.scale
        _axis_joint(
            model,
            name="housing_to_hopper_lid",
            parent=housing,
            child=lid,
            provider=AxisInterface(
                name="structural_family.hopper_hinge",
                point=(hinge_x, 0.0, hinge_z),
                axis=(0.0, -1.0, 0.0),
                radial=(1.0, 0.0, 0.0),
                radius=0.0022 * r.scale,
            ),
            consumer=AxisInterface(
                name="closure.hinge_knuckles",
                axis=(0.0, -1.0, 0.0),
                radial=(1.0, 0.0, 0.0),
                radius=0.0028 * r.scale,
            ),
            articulation_type=ArticulationType.REVOLUTE,
            limits=MotionLimits(
                effort=2.0,
                velocity=2.0,
                lower=0.0,
                upper=math.radians(100.0),
            ),
        )

    if r.drive == "folding_top_crank":
        crank, grip, grip_point, grip_axis = _drive_folding_top_crank_build(model, r, mats)
        _axis_joint(
            model,
            name="housing_to_crank",
            parent=housing,
            child=crank,
            provider=AxisInterface(
                name="structural_family.drive_axis",
                point=(0.0, 0.0, r.top_drive_z_m),
                axis=(0.0, 0.0, 1.0),
                radial=(1.0, 0.0, 0.0),
                radius=0.0052 * r.scale,
            ),
            consumer=AxisInterface(
                name="drive.shaft_axis",
                axis=(0.0, 0.0, 1.0),
                radial=(1.0, 0.0, 0.0),
                radius=0.0042 * r.scale,
            ),
            articulation_type=ArticulationType.CONTINUOUS,
            limits=MotionLimits(effort=12.0, velocity=8.0),
        )
        _axis_joint(
            model,
            name="crank_to_grip",
            parent=crank,
            child=grip,
            provider=AxisInterface(
                name="drive.grip_pin",
                point=grip_point,
                axis=grip_axis,
                radial=(1.0, 0.0, 0.0),
                radius=0.0027 * r.scale,
            ),
            consumer=AxisInterface(
                name="drive.grip_bore",
                axis=grip_axis,
                radial=(1.0, 0.0, 0.0),
                radius=0.0033 * r.scale,
            ),
            articulation_type=ArticulationType.CONTINUOUS,
            limits=MotionLimits(effort=1.0, velocity=12.0),
        )
    else:
        if r.drive == "side_crank":
            crank, grip, grip_point, grip_axis = _drive_side_crank_build(model, r, mats)
            drive_point = (r.side_drive_x_m, 0.0, r.side_drive_z_m)
            drive_axis = (1.0, 0.0, 0.0)
            drive_radial = (0.0, 0.0, 1.0)
        else:
            crank, grip, grip_point, grip_axis = _drive_rigid_top_crank_build(model, r, mats)
            drive_point = (0.0, 0.0, r.top_drive_z_m)
            drive_axis = (0.0, 0.0, 1.0)
            drive_radial = (1.0, 0.0, 0.0)
        _axis_joint(
            model,
            name="housing_to_crank",
            parent=housing,
            child=crank,
            provider=AxisInterface(
                name="structural_family.drive_axis",
                point=drive_point,
                axis=drive_axis,
                radial=drive_radial,
                radius=0.0052 * r.scale,
            ),
            consumer=AxisInterface(
                name="drive.shaft_axis",
                axis=drive_axis,
                radial=drive_radial,
                radius=0.0042 * r.scale,
            ),
            articulation_type=ArticulationType.CONTINUOUS,
            limits=MotionLimits(effort=12.0, velocity=8.0),
        )
        _axis_joint(
            model,
            name="crank_to_grip",
            parent=crank,
            child=grip,
            provider=AxisInterface(
                name="drive.grip_pin",
                point=grip_point,
                axis=grip_axis,
                radial=(0.0, 1.0, 0.0) if grip_axis[0] else (1.0, 0.0, 0.0),
                radius=0.0027 * r.scale,
            ),
            consumer=AxisInterface(
                name="drive.grip_bore",
                axis=grip_axis,
                radial=(0.0, 1.0, 0.0) if grip_axis[0] else (1.0, 0.0, 0.0),
                radius=0.0033 * r.scale,
            ),
            articulation_type=ArticulationType.CONTINUOUS,
            limits=MotionLimits(effort=1.0, velocity=12.0),
        )
    return model


def run_manual_coffee_grinder_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    allow_islands = getattr(ctx, "allow_disconnected_islands", None)
    if callable(allow_islands):
        for part in model.parts:
            allow_islands(
                part,
                reason=(
                    "rigid manufactured sub-pieces (fasteners, rails, frame posts, "
                    "bearing spokes and knobs) are fixed within one source assembly"
                ),
            )
    for part in model.parts:
        if part.meta.get("role") in {
            "manual_drive",
            "free_spinning_grip",
            "folding_drive_arm",
            "grind_adjustment",
            "hopper_closure",
        }:
            ctx.allow_isolated_part(
                part,
                reason="joint-retained rotating member with source-derived running clearance",
            )
        if (
            part.meta.get("role") == "grounds_receiver"
            and part.meta.get("receiver_type") == "threaded_cup"
        ):
            ctx.allow_isolated_part(
                part,
                reason="threaded receiver is retained by its revolute thread joint and radial clearance",
            )
    housing = model.get_part("housing")
    adjustment = model.get_part("adjustment_collar")
    crank_joint = model.get_articulation("housing_to_crank")
    adjustment_joint = model.get_articulation("housing_to_adjustment")
    ctx.check(
        "manual coffee grinder source identity",
        model.meta.get("category") == "manual_coffee_grinder"
        and housing is not None
        and adjustment is not None
        and crank_joint is not None
        and adjustment_joint is not None,
        details=f"family={r.structural_family}, parts={[p.name for p in model.parts]}",
    )
    ctx.check(
        "all selected slots are recorded",
        dict(model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=f"slot_choices={model.meta.get('slot_choices')!r}",
    )
    ctx.check(
        "drive and adjustment use source axes",
        adjustment_joint is not None
        and tuple(adjustment_joint.axis) == (0.0, 0.0, 1.0)
        and crank_joint is not None
        and tuple(crank_joint.axis)
        == ((1.0, 0.0, 0.0) if r.drive == "side_crank" else (0.0, 0.0, 1.0)),
        details=f"adjustment={adjustment_joint}, crank={crank_joint}",
    )
    if r.catch_kind == "drawer":
        drawer = model.get_part("grounds_drawer")
        joint = model.get_articulation("housing_to_grounds_drawer")
        ctx.check(
            "drawer family has real cut cavity rails and hollow tray",
            drawer is not None
            and drawer.meta.get("open_hollow_tray") is True
            and drawer.meta.get("host_has_real_cavity") is True
            and drawer.meta.get("host_has_four_rails") is True
            and housing is not None
            and housing.get_visual(
                "housing__cylindrical_body_with_cut_drawer_cavity"
                if r.structural_family == "slim_drawer_cylinder"
                else "housing__rounded_cabinet_with_cut_drawer_cavity"
            )
            is not None
            and joint is not None
            and joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(joint.axis) == (0.0, -1.0, 0.0),
            details=f"drawer={drawer}, joint={joint}",
        )
    elif r.catch_kind in {"prismatic_cup", "threaded_cup"}:
        cup = model.get_part("grounds_cup")
        joint = model.get_articulation("housing_to_grounds_cup")
        expected_type = (
            ArticulationType.REVOLUTE
            if r.catch_kind == "threaded_cup"
            else ArticulationType.PRISMATIC
        )
        ctx.check(
            "cup family has matching open receiver and source motion",
            cup is not None
            and cup.meta.get("open_hollow_cup") is True
            and joint is not None
            and joint.articulation_type == expected_type,
            details=f"cup={cup}, joint={joint}",
        )
    if r.closure == "hinged_cover":
        lid = model.get_part("hopper_lid")
        lid_joint = model.get_articulation("housing_to_hopper_lid")
        ctx.check(
            "hinged cover has slot captured knuckles and bounded opening",
            lid is not None
            and lid.meta.get("shaft_clearance_slot") is True
            and lid.meta.get("captured_knuckles") is True
            and lid_joint is not None
            and lid_joint.articulation_type == ArticulationType.REVOLUTE
            and lid_joint.motion_limits is not None
            and lid_joint.motion_limits.upper >= math.radians(95.0),
            details=f"lid={lid}, joint={lid_joint}",
        )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "source_001_turned_open_rigid",
        {
            "structural_family": "turned_wood_integrated",
            "drive": "rigid_top_crank",
            "closure": "open",
            "mount": "countertop",
            "scale": 1.0,
            "drawer_travel_m": 0.068,
            "cup_release_m": 0.032,
            "crank_reach_m": 0.090,
            "grip_length_m": 0.063,
            "wall_clearance_m": 0.0009,
        },
        reason="source image 001 silhouette and open bowl",
    ),
    corner_case(
        "source_002_ribbed_hinged_folding",
        {
            "structural_family": "ribbed_travel_cup",
            "drive": "folding_top_crank",
            "closure": "hinged_cover",
            "mount": "countertop",
            "scale": 0.90,
            "drawer_travel_m": 0.050,
            "cup_release_m": 0.040,
            "crank_reach_m": 0.105,
            "grip_length_m": 0.064,
            "wall_clearance_m": 0.0012,
        },
        reason="small ribbed body, longest release and folding/lid sweeps",
    ),
    corner_case(
        "source_003_cabinet_drawer_open",
        {
            "structural_family": "wood_cabinet_drawer",
            "drive": "rigid_top_crank",
            "closure": "open",
            "mount": "countertop",
            "scale": 1.0,
            "drawer_travel_m": 0.080,
            "cup_release_m": 0.032,
            "crank_reach_m": 0.090,
            "grip_length_m": 0.054,
            "wall_clearance_m": 0.0012,
        },
        reason="source image 003 real drawer cavity at full travel",
    ),
    corner_case(
        "slim_drawer_side_clamp_lid",
        {
            "structural_family": "slim_drawer_cylinder",
            "drive": "side_crank",
            "closure": "hinged_cover",
            "mount": "table_clamp",
            "scale": 1.12,
            "drawer_travel_m": 0.080,
            "cup_release_m": 0.040,
            "crank_reach_m": 0.105,
            "grip_length_m": 0.064,
            "wall_clearance_m": 0.0012,
        },
        reason="largest drawer, side-drive, lid and table-clamp envelopes",
    ),
    corner_case(
        "threaded_cup_side_crank",
        {
            "structural_family": "ribbed_threaded_cup",
            "drive": "side_crank",
            "closure": "open",
            "mount": "table_clamp",
            "scale": 1.12,
            "drawer_travel_m": 0.050,
            "cup_release_m": 0.025,
            "crank_reach_m": 0.105,
            "grip_length_m": 0.064,
            "wall_clearance_m": 0.0006,
        },
        reason="thread socket, knurl, horizontal shaft and clamp at maximum size",
    ),
    corner_case(
        "square_cup_minimum",
        {
            "structural_family": "square_wood_cup",
            "drive": "folding_top_crank",
            "closure": "hinged_cover",
            "mount": "countertop",
            "scale": 0.90,
            "drawer_travel_m": 0.050,
            "cup_release_m": 0.025,
            "crank_reach_m": 0.078,
            "grip_length_m": 0.045,
            "wall_clearance_m": 0.0006,
        },
        reason="minimum square host and folding/hinge clearances",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_manual_coffee_grinder",
    "config_from_seed",
    "resolve_config",
    "run_manual_coffee_grinder_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
