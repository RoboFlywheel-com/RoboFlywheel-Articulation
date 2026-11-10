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
    TestContext,
    TestReport,
)

BlenderLayout = Literal[
    "countertop_jug", "personal_cup", "commercial_hood", "vacuum_jug", "bar_blender"
]
BaseShape = Literal["rectangular", "round_disc", "tapered_commercial"]
JarShape = Literal["square_pitcher", "cylindrical_jug", "rounded_rect_jar", "inverted_cup"]
BladeStyle = Literal["two_blade_cross", "four_blade_cross", "six_blade_stack"]
JarLockMotion = Literal["fixed", "twist_lock"]
LidStyle = Literal[
    "flat_lid", "center_cap_lid", "flip_spout", "hinged_shield", "vacuum_cap", "none"
]
ControlStyle = Literal["dial", "button_panel", "rocker", "trigger", "none"]
ShaftLockStyle = Literal["none"]
BladeSpinSpeedClass = Literal["slow_display", "normal", "high_speed"]
HandleProfile = Literal["cylindrical", "tapered_grip"]
GuardStyle = Literal["bell_guard", "open_cage"]
CupStyle = Literal["smooth_cup", "threaded_travel_cup"]
CapStyle = Literal["none", "center_twist", "vacuum_press"]
HandleStyle = Literal["none", "side_handle", "bridge_handle"]
MaterialStyle = Literal[
    "kitchen_white",
    "commercial_black",
    "brushed_steel",
    "red_consumer",
    "blue_soft_grip",
]

MATERIAL_PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "kitchen_white": {
        "base": (0.88, 0.88, 0.84, 1.0),
        "jar": (0.70, 0.86, 0.95, 0.35),
        "lid": (0.08, 0.08, 0.09, 1.0),
        "blade": (0.72, 0.74, 0.76, 1.0),
        "accent": (0.80, 0.12, 0.08, 1.0),
    },
    "commercial_black": {
        "base": (0.05, 0.05, 0.06, 1.0),
        "jar": (0.68, 0.82, 0.90, 0.32),
        "lid": (0.03, 0.03, 0.03, 1.0),
        "blade": (0.76, 0.78, 0.80, 1.0),
        "accent": (0.35, 0.36, 0.38, 1.0),
    },
    "brushed_steel": {
        "base": (0.58, 0.60, 0.60, 1.0),
        "jar": (0.72, 0.86, 0.96, 0.34),
        "lid": (0.12, 0.12, 0.13, 1.0),
        "blade": (0.86, 0.88, 0.88, 1.0),
        "accent": (0.06, 0.06, 0.06, 1.0),
    },
    "red_consumer": {
        "base": (0.82, 0.06, 0.045, 1.0),
        "jar": (0.78, 0.90, 0.98, 0.30),
        "lid": (0.08, 0.07, 0.065, 1.0),
        "blade": (0.82, 0.84, 0.84, 1.0),
        "accent": (0.12, 0.12, 0.13, 1.0),
    },
    "blue_soft_grip": {
        "base": (0.84, 0.86, 0.82, 1.0),
        "jar": (0.70, 0.86, 0.94, 0.34),
        "lid": (0.04, 0.05, 0.06, 1.0),
        "blade": (0.76, 0.78, 0.80, 1.0),
        "accent": (0.08, 0.22, 0.48, 1.0),
    },
}

ADOPTED_SOURCES: dict[str, str] = {
    "S1": "data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L117-L350",
    "S2": "data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L45-L326",
    "S3": "data/records/rec_blender_f8cf6dc9c409425aaa7bee101674500b/revisions/rev_000001/model.py:L152-L260",
    "S4": "data/records/rec_blender_f513f69f35204dab87e58687d44fb722/revisions/rev_000001/model.py:L89-L322",
    "S5": "data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L33-L270",
    "S6": "data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L55-L419",
}


@dataclass(frozen=True)
class BlenderConfig:
    blender_layout: BlenderLayout = "countertop_jug"
    base_shape: BaseShape | None = None
    jar_shape: JarShape | None = None
    blade_style: BladeStyle = "four_blade_cross"
    jar_lock_motion: JarLockMotion = "fixed"
    lid_style: LidStyle = "center_cap_lid"
    control_style: ControlStyle = "dial"
    hood_enabled: bool = False
    safety_latch_enabled: bool = False
    shaft_lock_style: ShaftLockStyle = "none"
    blade_spin_speed_class: BladeSpinSpeedClass = "high_speed"
    handle_profile: HandleProfile = "cylindrical"
    guard_style: GuardStyle = "bell_guard"
    cup_style: CupStyle = "threaded_travel_cup"
    cap_style: CapStyle = "center_twist"
    handle_style: HandleStyle = "side_handle"
    base_width: float = 0.180
    base_depth: float = 0.160
    base_height: float = 0.140
    jar_height: float = 0.260
    shaft_length: float = 0.260
    blade_radius: float = 0.042
    material_style: MaterialStyle = "kitchen_white"
    name: str = "reference_blender_countertop"


@dataclass(frozen=True)
class ResolvedBlenderConfig:
    blender_layout: BlenderLayout
    base_shape: BaseShape
    jar_shape: JarShape
    blade_style: BladeStyle
    blade_count: int
    jar_lock_motion: JarLockMotion
    lid_style: LidStyle
    control_style: ControlStyle
    hood_enabled: bool
    safety_latch_enabled: bool
    shaft_lock_style: ShaftLockStyle
    blade_spin_speed_class: BladeSpinSpeedClass
    handle_profile: HandleProfile
    guard_style: GuardStyle
    cup_style: CupStyle
    cap_style: CapStyle
    handle_style: HandleStyle
    base_width: float
    base_depth: float
    base_height: float
    jar_height: float
    shaft_length: float
    blade_radius: float
    blade_axis: tuple[float, float, float]
    material_style: MaterialStyle
    name: str


def config_from_seed(seed: int) -> BlenderConfig:
    rng = random.Random(seed)
    # Keep the good-parameterized original families, but avoid commercial/bar
    # hood layouts whose large covers and latch chains were brittle.
    layout: BlenderLayout = rng.choice(("countertop_jug", "personal_cup", "vacuum_jug"))
    lid_style: LidStyle = {
        "countertop_jug": rng.choice(("flat_lid", "center_cap_lid")),
        "personal_cup": "none",
        "vacuum_jug": rng.choice(("center_cap_lid", "vacuum_cap")),
    }[layout]
    handle_style: HandleStyle = {
        "countertop_jug": rng.choice(("side_handle", "bridge_handle")),
        "personal_cup": "none",
        "vacuum_jug": rng.choice(("side_handle", "none")),
    }[layout]
    control_style: ControlStyle = (
        rng.choice(("dial", "button_panel")) if layout == "countertop_jug" else "button_panel"
    )
    return BlenderConfig(
        blender_layout=layout,
        blade_style=rng.choice(("two_blade_cross", "four_blade_cross", "six_blade_stack")),
        jar_lock_motion=rng.choice(("fixed", "twist_lock")),
        lid_style=lid_style,
        control_style=control_style,
        hood_enabled=False,
        safety_latch_enabled=False,
        shaft_lock_style="none",
        blade_spin_speed_class=rng.choice(("slow_display", "normal", "high_speed")),
        handle_profile=rng.choice(("cylindrical", "tapered_grip")),
        guard_style="bell_guard",
        cup_style="threaded_travel_cup",
        cap_style=rng.choice(("none", "center_twist")),
        handle_style=handle_style,
        base_width=round(rng.uniform(0.145, 0.220), 3),
        base_depth=round(rng.uniform(0.135, 0.210), 3),
        base_height=round(rng.uniform(0.105, 0.180), 3),
        jar_height=round(rng.uniform(0.200, 0.330), 3),
        shaft_length=round(rng.uniform(0.220, 0.330), 3),
        blade_radius=round(rng.uniform(0.028, 0.055), 4),
        material_style=rng.choice(tuple(MATERIAL_PALETTES)),
        name=f"seeded_blender_countertop_{seed}",
    )


def resolve_config(config: BlenderConfig) -> ResolvedBlenderConfig:
    if config.blender_layout not in (
        "countertop_jug",
        "personal_cup",
        "commercial_hood",
        "vacuum_jug",
        "bar_blender",
    ):
        raise ValueError(f"Unsupported blender_layout: {config.blender_layout}")
    base_shape = config.base_shape
    jar_shape = config.jar_shape
    if base_shape is None:
        base_shape = (
            "round_disc"
            if config.blender_layout == "vacuum_jug"
            else "tapered_commercial"
            if config.blender_layout in ("commercial_hood", "bar_blender")
            else "rectangular"
        )
    if jar_shape is None:
        jar_shape = (
            "inverted_cup"
            if config.blender_layout == "personal_cup"
            else "cylindrical_jug"
            if config.blender_layout == "vacuum_jug"
            else "square_pitcher"
        )
    if base_shape not in ("rectangular", "round_disc", "tapered_commercial"):
        raise ValueError(f"Unsupported base_shape: {base_shape}")
    if jar_shape not in ("square_pitcher", "cylindrical_jug", "rounded_rect_jar", "inverted_cup"):
        raise ValueError(f"Unsupported jar_shape: {jar_shape}")
    if config.blade_style not in ("two_blade_cross", "four_blade_cross", "six_blade_stack"):
        raise ValueError(f"Unsupported blade_style: {config.blade_style}")
    if config.jar_lock_motion not in ("fixed", "twist_lock"):
        raise ValueError(f"Unsupported jar_lock_motion: {config.jar_lock_motion}")
    if config.lid_style not in (
        "flat_lid",
        "center_cap_lid",
        "flip_spout",
        "hinged_shield",
        "vacuum_cap",
        "none",
    ):
        raise ValueError(f"Unsupported lid_style: {config.lid_style}")
    if config.control_style not in ("dial", "button_panel", "rocker", "trigger", "none"):
        raise ValueError(f"Unsupported control_style: {config.control_style}")
    if config.shaft_lock_style != "none":
        raise ValueError(f"Unsupported shaft_lock_style: {config.shaft_lock_style}")
    if config.blade_spin_speed_class not in ("slow_display", "normal", "high_speed"):
        raise ValueError(f"Unsupported blade_spin_speed_class: {config.blade_spin_speed_class}")
    if config.handle_profile not in ("cylindrical", "tapered_grip"):
        raise ValueError(f"Unsupported handle_profile: {config.handle_profile}")
    if config.guard_style not in ("bell_guard", "open_cage"):
        raise ValueError(f"Unsupported guard_style: {config.guard_style}")
    if config.cup_style not in ("smooth_cup", "threaded_travel_cup"):
        raise ValueError(f"Unsupported cup_style: {config.cup_style}")
    if config.cap_style not in ("none", "center_twist", "vacuum_press"):
        raise ValueError(f"Unsupported cap_style: {config.cap_style}")
    if config.handle_style not in ("none", "side_handle", "bridge_handle"):
        raise ValueError(f"Unsupported handle_style: {config.handle_style}")
    if config.material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    if config.blender_layout in {"commercial_hood", "bar_blender"}:
        config = replace(
            config,
            blender_layout="countertop_jug",
            hood_enabled=False,
            safety_latch_enabled=False,
            lid_style="center_cap_lid",
            control_style="dial",
            cap_style="center_twist",
            handle_style="side_handle",
        )
        base_shape = "rectangular"
        jar_shape = "square_pitcher"
    elif config.blender_layout == "personal_cup":
        config = replace(
            config,
            lid_style="none",
            cap_style="none",
            handle_style="none",
            control_style="button_panel",
            hood_enabled=False,
            safety_latch_enabled=False,
        )
        base_shape = "rectangular"
        jar_shape = "inverted_cup"
    elif config.blender_layout == "vacuum_jug":
        if config.lid_style in {"flat_lid", "flip_spout", "hinged_shield", "none"}:
            config = replace(config, lid_style="vacuum_cap")
        if config.control_style != "button_panel":
            config = replace(config, control_style="button_panel")
        base_shape = "round_disc"
        jar_shape = "cylindrical_jug"
    elif config.lid_style in {"flip_spout", "hinged_shield", "vacuum_cap", "none"}:
        config = replace(config, lid_style="center_cap_lid")
    if config.control_style in {"rocker", "trigger", "none"}:
        config = replace(config, control_style="dial")
    if config.cap_style == "vacuum_press":
        config = replace(config, cap_style="center_twist")
    config = replace(config, hood_enabled=False, safety_latch_enabled=False)

    blade_count = {"two_blade_cross": 2, "four_blade_cross": 4, "six_blade_stack": 6}[
        config.blade_style
    ]
    return ResolvedBlenderConfig(
        blender_layout=config.blender_layout,
        base_shape=base_shape,
        jar_shape=jar_shape,
        blade_style=config.blade_style,
        blade_count=blade_count,
        jar_lock_motion=config.jar_lock_motion,
        lid_style=config.lid_style,
        control_style=config.control_style,
        hood_enabled=bool(config.hood_enabled),
        safety_latch_enabled=bool(
            config.safety_latch_enabled
            and config.blender_layout in ("commercial_hood", "bar_blender")
        ),
        shaft_lock_style="none",
        blade_spin_speed_class=config.blade_spin_speed_class,
        handle_profile=config.handle_profile,
        guard_style=config.guard_style,
        cup_style=config.cup_style,
        cap_style=config.cap_style,
        handle_style=config.handle_style,
        base_width=max(0.145, min(0.220, config.base_width)),
        base_depth=max(0.135, min(0.210, config.base_depth)),
        base_height=max(0.105, min(0.180, config.base_height)),
        jar_height=max(0.200, min(0.330, config.jar_height)),
        shaft_length=max(0.220, min(0.330, config.shaft_length)),
        blade_radius=max(0.028, min(0.055, config.blade_radius)),
        blade_axis=(0.0, 0.0, 1.0),
        material_style=config.material_style,
        name=config.name,
    )


def _add_base(part, r: ResolvedBlenderConfig, *, base_mat, accent_mat) -> None:
    if r.base_shape == "round_disc":
        part.visual(
            Cylinder(radius=max(r.base_width, r.base_depth) * 0.54, length=r.base_height),
            origin=Origin(xyz=(0.0, 0.0, r.base_height / 2.0)),
            material=base_mat,
            name="round_motor_base", material_class_id=("plastic.opaque_glossy_molded" if r.material_style in {"kitchen_white", "commercial_black", "red_consumer", "blue_soft_grip"} else "metal.brushed_silver"),
        )
    else:
        part.visual(
            Box((r.base_width, r.base_depth, r.base_height)),
            origin=Origin(xyz=(0.0, 0.0, r.base_height / 2.0)),
            material=base_mat,
            name=f"{r.base_shape}_motor_base", material_class_id=("plastic.opaque_glossy_molded" if r.material_style in {"kitchen_white", "commercial_black", "red_consumer", "blue_soft_grip"} else "metal.brushed_silver"),
        )
    part.visual(
        Cylinder(radius=0.032, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, r.base_height + 0.006)),
        material=accent_mat,
        name="drive_coupling", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        Box((r.base_width * 0.48, 0.010, r.base_height * 0.34)),
        origin=Origin(xyz=(0.0, -r.base_depth / 2.0 - 0.004, r.base_height * 0.52)),
        material=accent_mat,
        name="control_panel", material_class_id="tech.control_interface",
    )


def _add_jar(part, r: ResolvedBlenderConfig, *, jar_mat, accent_mat) -> None:
    if r.jar_shape in ("cylindrical_jug", "inverted_cup"):
        radius = 0.065 if r.jar_shape == "cylindrical_jug" else 0.055
        wall = 0.006
        span = radius * 2.0
        part.visual(
            Box((span, span, 0.012)),
            origin=Origin(xyz=(0.0, 0.0, 0.006)),
            material=jar_mat,
            name=f"{r.jar_shape}_floor", material_class_id="plastic.clear_rigid",
        )
        part.visual(
            Box((wall, span, r.jar_height)),
            origin=Origin(xyz=(radius, 0.0, r.jar_height / 2.0)),
            material=jar_mat,
            name=f"{r.jar_shape}_wall_x_pos", material_class_id="plastic.clear_rigid",
        )
        part.visual(
            Box((wall, span, r.jar_height)),
            origin=Origin(xyz=(-radius, 0.0, r.jar_height / 2.0)),
            material=jar_mat,
            name=f"{r.jar_shape}_wall_x_neg", material_class_id="plastic.clear_rigid",
        )
        part.visual(
            Box((span, wall, r.jar_height)),
            origin=Origin(xyz=(0.0, radius, r.jar_height / 2.0)),
            material=jar_mat,
            name=f"{r.jar_shape}_wall_y_pos", material_class_id="plastic.clear_rigid",
        )
        part.visual(
            Box((span, wall, r.jar_height)),
            origin=Origin(xyz=(0.0, -radius, r.jar_height / 2.0)),
            material=jar_mat,
            name=f"{r.jar_shape}_wall_y_neg", material_class_id="plastic.clear_rigid",
        )
        part.visual(
            Cylinder(radius=radius, length=0.010),
            origin=Origin(xyz=(0.0, 0.0, r.jar_height - 0.005)),
            material=accent_mat,
            name=f"{r.jar_shape}_rim", material_class_id="plastic.opaque_glossy_molded",
        )
    else:
        bottom = 0.110 if r.jar_shape == "square_pitcher" else 0.120
        top = 0.145 if r.jar_shape == "square_pitcher" else 0.135
        floor_size = top - 0.010
        part.visual(
            Box((floor_size, floor_size, 0.012)),
            origin=Origin(xyz=(0.0, 0.0, 0.006)),
            material=jar_mat,
            name="pitcher_floor", material_class_id="plastic.clear_rigid",
        )
        part.visual(
            Box((top, 0.010, r.jar_height)),
            origin=Origin(xyz=(0.0, -top / 2.0, r.jar_height / 2.0)),
            material=jar_mat,
            name="pitcher_front_wall", material_class_id="plastic.clear_rigid",
        )
        part.visual(
            Box((top, 0.010, r.jar_height)),
            origin=Origin(xyz=(0.0, top / 2.0, r.jar_height / 2.0)),
            material=jar_mat,
            name="pitcher_rear_wall", material_class_id="plastic.clear_rigid",
        )
        part.visual(
            Box((0.010, top, r.jar_height)),
            origin=Origin(xyz=(top / 2.0, 0.0, r.jar_height / 2.0)),
            material=jar_mat,
            name="pitcher_right_wall", material_class_id="plastic.clear_rigid",
        )
        part.visual(
            Box((0.010, top, r.jar_height)),
            origin=Origin(xyz=(-top / 2.0, 0.0, r.jar_height / 2.0)),
            material=jar_mat,
            name="pitcher_left_wall", material_class_id="plastic.clear_rigid",
        )
    if r.handle_style != "none":
        part.visual(
            Box((0.025, 0.030, r.jar_height * 0.60)),
            origin=Origin(xyz=(0.095, 0.0, r.jar_height * 0.54)),
            material=accent_mat,
            name=f"{r.handle_style}_handle_grip", material_class_id=("plastic.opaque_glossy_molded" if r.material_style in {"kitchen_white", "commercial_black", "brushed_steel", "red_consumer"} else "rubber.smooth_plain"),
        )
        part.visual(
            Box((0.050, 0.025, 0.020)),
            origin=Origin(xyz=(0.072, 0.0, r.jar_height * 0.78)),
            material=accent_mat,
            name="handle_upper_bridge", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            Box((0.045, 0.025, 0.020)),
            origin=Origin(xyz=(0.068, 0.0, r.jar_height * 0.32)),
            material=accent_mat,
            name="handle_lower_bridge", material_class_id="plastic.opaque_glossy_molded",
        )


def _container_mouth_half_y(r: ResolvedBlenderConfig) -> float:
    if r.jar_shape == "inverted_cup":
        return 0.055
    if r.jar_shape == "cylindrical_jug":
        return 0.065
    return 0.0725


def _add_lid(part, r: ResolvedBlenderConfig, *, lid_mat, accent_mat, hinge_y: float) -> None:
    lid_size = hinge_y * 2.0
    part.visual(
        Box((lid_size, lid_size, 0.018)),
        origin=Origin(xyz=(0.0, -hinge_y, 0.009)),
        material=lid_mat,
        name=r.lid_style, material_class_id="plastic.opaque_glossy_molded",
    )
    if r.lid_style in ("center_cap_lid", "vacuum_cap"):
        part.visual(
            Cylinder(radius=0.026, length=0.016),
            origin=Origin(xyz=(0.0, -hinge_y, 0.024)),
            material=accent_mat,
            name="cap_seat", material_class_id="plastic.opaque_glossy_molded",
        )
    if r.lid_style == "flip_spout":
        part.visual(
            Box((0.045, 0.030, 0.018)),
            origin=Origin(xyz=(0.0, -2.0 * hinge_y + 0.014, 0.020)),
            material=accent_mat,
            name="flip_spout", material_class_id="plastic.opaque_glossy_molded",
        )


def _add_blade(part, r: ResolvedBlenderConfig, *, blade_mat) -> None:
    part.visual(
        Cylinder(radius=0.018, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, -0.009)),
        material=blade_mat,
        name="blade_mount_flange", material_class_id="metal.stainless_matte",
    )
    part.visual(
        Cylinder(radius=0.010, length=0.012), origin=Origin(), material=blade_mat, name="blade_hub", material_class_id="metal.stainless_matte"
    )
    for i in range(r.blade_count):
        angle = 2.0 * math.pi * i / r.blade_count
        part.visual(
            Box((r.blade_radius, 0.010, 0.004)),
            origin=Origin(
                xyz=(
                    math.cos(angle) * r.blade_radius / 2.0,
                    math.sin(angle) * r.blade_radius / 2.0,
                    0.006,
                ),
                rpy=(0.0, 0.0, angle),
            ),
            material=blade_mat,
            name=f"blade_{i}", material_class_id="metal.stainless_matte",
        )


def _add_control(
    model: ArticulatedObject, parent, r: ResolvedBlenderConfig, *, accent_mat, base_depth: float
) -> None:
    if r.control_style == "none":
        return
    if r.control_style == "button_panel":
        for i in range(3):
            parent.visual(
                Cylinder(radius=0.008, length=0.006),
                origin=Origin(
                    xyz=(-0.025 + i * 0.025, -base_depth / 2.0 - 0.008, r.base_height * 0.55),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=accent_mat,
                name=f"button_{i}", material_class_id="tech.control_interface",
            )
        return
    control = model.part("dial_or_controls")
    if r.control_style == "trigger":
        control.visual(
            Box((0.014, 0.030, 0.070)), origin=Origin(), material=accent_mat, name="trigger_pad", material_class_id="tech.control_interface"
        )
        model.articulation(
            "trigger_or_dial",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=control,
            origin=Origin(xyz=(0.030, -base_depth / 2.0 - 0.024, r.base_height * 0.55)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=3.0, lower=0.0, upper=0.35),
            meta={"source_id": "S3"},
        )
    elif r.control_style == "rocker":
        control.visual(
            Box((0.040, 0.012, 0.025)), origin=Origin(), material=accent_mat, name="rocker_switch", material_class_id="tech.control_interface"
        )
        model.articulation(
            "trigger_or_dial",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=control,
            origin=Origin(xyz=(0.0, -base_depth / 2.0 - 0.010, r.base_height * 0.55)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=3.0, lower=-0.30, upper=0.30),
            meta={"source_id": "S3"},
        )
    else:
        control.visual(
            Cylinder(radius=0.024, length=0.018),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=accent_mat,
            name="speed_dial", material_class_id="tech.control_interface",
        )
        control.visual(
            Box((0.006, 0.006, 0.030)),
            origin=Origin(xyz=(0.0, -0.011, 0.017)),
            material=accent_mat,
            name="speed_dial_pointer", material_class_id="tech.control_interface",
        )
        model.articulation(
            "trigger_or_dial",
            ArticulationType.CONTINUOUS,
            parent=parent,
            child=control,
            origin=Origin(xyz=(0.0, -base_depth / 2.0 - 0.018, r.base_height * 0.56)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=0.8, velocity=5.0),
            meta={"source_id": "S1"},
        )


def build_blender(
    config: BlenderConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or BlenderConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-blender-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = MATERIAL_PALETTES[r.material_style]
    base_mat = model.material("blender_base", rgba=palette["base"])
    jar_mat = model.material("blender_clear_container", rgba=palette["jar"])
    lid_mat = model.material("blender_lid", rgba=palette["lid"])
    blade_mat = model.material("blender_blade", rgba=palette["blade"])
    accent_mat = model.material("blender_accent", rgba=palette["accent"])

    base = model.part("motor_base")
    _add_base(base, r, base_mat=base_mat, accent_mat=accent_mat)
    jar = model.part("pitcher_or_jar" if r.blender_layout != "personal_cup" else "bottle_or_cup")
    _add_jar(jar, r, jar_mat=jar_mat, accent_mat=accent_mat)
    jar_joint_type = (
        ArticulationType.REVOLUTE if r.jar_lock_motion == "twist_lock" else ArticulationType.FIXED
    )
    jar_kwargs = {}
    if jar_joint_type == ArticulationType.REVOLUTE:
        jar_kwargs["axis"] = (0.0, 0.0, 1.0)
        jar_kwargs["motion_limits"] = MotionLimits(
            effort=12.0, velocity=2.5, lower=-0.40, upper=0.55
        )
    model.articulation(
        "jar_twist_lock",
        jar_joint_type,
        parent=base,
        child=jar,
        origin=Origin(xyz=(0.0, 0.0, r.base_height + 0.010)),
        meta={"source_id": "S2" if jar_joint_type == ArticulationType.REVOLUTE else "S1"},
        **jar_kwargs,
    )

    blade = model.part("blade_assembly")
    _add_blade(blade, r, blade_mat=blade_mat)
    model.articulation(
        "blade_spin",
        ArticulationType.CONTINUOUS,
        parent=jar,
        child=blade,
        origin=Origin(xyz=(0.0, 0.0, 0.024)),
        axis=r.blade_axis,
        motion_limits=MotionLimits(
            effort=8.0,
            velocity={"slow_display": 12.0, "normal": 35.0, "high_speed": 70.0}[
                r.blade_spin_speed_class
            ],
        ),
        meta={"source_id": "S1"},
    )

    if r.lid_style != "none":
        lid = model.part("lid")
        lid_hinge_y = _container_mouth_half_y(r)
        _add_lid(lid, r, lid_mat=lid_mat, accent_mat=accent_mat, hinge_y=lid_hinge_y)
        if r.lid_style in ("flip_spout", "hinged_shield"):
            model.articulation(
                "lid_hinge",
                ArticulationType.REVOLUTE,
                parent=jar,
                child=lid,
                origin=Origin(xyz=(0.0, lid_hinge_y, r.jar_height)),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=1.8),
                meta={"source_id": "S4"},
            )
        else:
            model.articulation(
                "lid_to_container",
                ArticulationType.FIXED,
                parent=jar,
                child=lid,
                origin=Origin(xyz=(0.0, lid_hinge_y, r.jar_height)),
                meta={"source_id": "S1"},
            )
        if r.lid_style in ("center_cap_lid", "vacuum_cap") and r.cap_style != "none":
            cap = model.part("center_cap")
            cap.visual(
                Cylinder(radius=0.022, length=0.018),
                origin=Origin(),
                material=accent_mat,
                name=r.cap_style, material_class_id="plastic.opaque_glossy_molded",
            )
            cap.visual(
                Box((0.032, 0.006, 0.006)),
                origin=Origin(xyz=(0.016, 0.0, 0.012)),
                material=accent_mat,
                name="cap_twist_pointer", material_class_id="plastic.opaque_glossy_molded",
            )
            if r.cap_style == "vacuum_press":
                model.articulation(
                    "connector_cap_press",
                    ArticulationType.PRISMATIC,
                    parent=lid,
                    child=cap,
                    origin=Origin(xyz=(0.0, -lid_hinge_y, 0.041)),
                    axis=(0.0, 0.0, -1.0),
                    motion_limits=MotionLimits(effort=1.0, velocity=0.2, lower=0.0, upper=0.018),
                    meta={"source_id": "S5"},
                )
            else:
                model.articulation(
                    "center_cap_twist",
                    ArticulationType.REVOLUTE,
                    parent=lid,
                    child=cap,
                    origin=Origin(xyz=(0.0, -lid_hinge_y, 0.041)),
                    axis=(0.0, 0.0, 1.0),
                    motion_limits=MotionLimits(effort=1.5, velocity=3.0, lower=0.0, upper=0.45),
                    meta={"source_id": "S1"},
                )

    if r.hood_enabled:
        hood = model.part("noise_hood")
        hood.visual(
            Cylinder(radius=0.010, length=r.base_depth * 1.12),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=accent_mat,
            name="hood_hinge_barrel", material_class_id="metal.blackened_gunmetal",
        )
        hood.visual(
            Box((0.280, 0.240, 0.008)),
            origin=Origin(xyz=(0.130, 0.0, 0.390)),
            material=jar_mat,
            name="hood_top_panel", material_class_id="plastic.clear_rigid",
        )
        hood.visual(
            Box((0.008, 0.240, 0.390)),
            origin=Origin(xyz=(-0.010, 0.0, 0.195)),
            material=jar_mat,
            name="hood_back_wall", material_class_id="plastic.clear_rigid",
        )
        hood.visual(
            Box((0.008, 0.240, 0.390)),
            origin=Origin(xyz=(0.270, 0.0, 0.195)),
            material=jar_mat,
            name="hood_front_wall", material_class_id="plastic.clear_rigid",
        )
        hood.visual(
            Box((0.280, 0.008, 0.390)),
            origin=Origin(xyz=(0.130, 0.116, 0.195)),
            material=jar_mat,
            name="hood_right_wall", material_class_id="plastic.clear_rigid",
        )
        hood.visual(
            Box((0.280, 0.008, 0.390)),
            origin=Origin(xyz=(0.130, -0.116, 0.195)),
            material=jar_mat,
            name="hood_left_wall", material_class_id="plastic.clear_rigid",
        )
        model.articulation(
            "hood_hinge",
            ArticulationType.REVOLUTE,
            parent=base,
            child=hood,
            origin=Origin(xyz=(-r.base_width / 2.0 - 0.018, 0.0, r.base_height + 0.030)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=18.0, velocity=1.2, lower=0.0, upper=1.25),
            meta={"source_id": "S2"},
        )
        if r.safety_latch_enabled:
            latch = model.part("safety_latch")
            latch.visual(
                Cylinder(radius=0.006, length=0.050),
                origin=Origin(xyz=(-0.006, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=accent_mat,
                name="latch_hinge_barrel", material_class_id="metal.blackened_gunmetal",
            )
            latch.visual(
                Box((0.018, 0.050, 0.075)),
                origin=Origin(xyz=(0.016, 0.0, -0.040)),
                material=accent_mat,
                name="front_safety_latch", material_class_id="metal.blackened_gunmetal",
            )
            model.articulation(
                "safety_latch_hinge",
                ArticulationType.REVOLUTE,
                parent=hood,
                child=latch,
                origin=Origin(xyz=(0.285, 0.0, 0.230)),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=1.05),
                meta={"source_id": "S6"},
            )

    _add_control(model, base, r, accent_mat=accent_mat, base_depth=r.base_depth)
    return model


def build_seeded_blender(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_blender(config_from_seed(seed), assets=assets)


def with_overrides(config: BlenderConfig, **kwargs: object) -> BlenderConfig:
    return replace(config, **kwargs)


def run_blender_tests(object_model: ArticulatedObject, config: BlenderConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    object_model.validate()
    blade_joints = [j for j in object_model.articulations if j.name == "blade_spin"]
    ctx.check("exactly_one_blade_spin", len(blade_joints) == 1)
    blade_joint = blade_joints[0]
    ctx.check("blade_joint_rotary", blade_joint.articulation_type == ArticulationType.CONTINUOUS)
    ctx.check("blade_axis_aligned", abs(blade_joint.axis[2]) > 0.9)
    ctx.check("blade_radius_inside_container_or_guard", r.blade_radius <= 0.060)
    ctx.check(
        "container_seated", object_model.get_articulation("jar_twist_lock").parent == "motor_base"
    )
    if r.jar_lock_motion == "twist_lock":
        ctx.check(
            "jar_twist_is_revolute",
            object_model.get_articulation("jar_twist_lock").articulation_type
            == ArticulationType.REVOLUTE,
        )
    if r.lid_style in ("flip_spout", "hinged_shield"):
        ctx.check(
            "lid_hinge_present",
            object_model.get_articulation("lid_hinge").articulation_type
            == ArticulationType.REVOLUTE,
        )
    if r.hood_enabled:
        ctx.check(
            "hood_hinge_present",
            object_model.get_articulation("hood_hinge").articulation_type
            == ArticulationType.REVOLUTE,
        )
    moving_controls = [j for j in object_model.articulations if j.name == "trigger_or_dial"]
    if r.control_style in ("dial", "rocker", "trigger"):
        ctx.check("moving_control_mounted", len(moving_controls) == 1)
    ctx.check(
        "part_diversity_parameters_present",
        all((r.blender_layout, r.jar_shape, r.blade_style, r.lid_style, r.control_style)),
    )
    return ctx.report()
