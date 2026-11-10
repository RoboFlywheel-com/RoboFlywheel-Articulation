# SPDX-License-Identifier: Apache-2.0

"""Robotic arms — modular procedural template.

Slot graph:
    base_yaw_root -> shoulder_elbow_link -> wrist_module -> end_effector

The main arm is a serial chain with a mandatory base yaw, shoulder pitch, and
elbow pitch. The end-effector slot may branch into parallel children for a
two/three-finger gripper or a five-finger dexterous hand.
"""

from __future__ import annotations

import itertools
import logging
import math
import random
from dataclasses import dataclass, field
from typing import Literal

logger = logging.getLogger(__name__)

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    ClearanceProbe,
    Cylinder,
    CylinderGeometry,
    Mimic,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    section_loft,
)

__modular__ = True


BaseYawRootModule = Literal["combined_shoulder_base", "yaw_turret", "yaw_carriage"]
ShoulderElbowLinkModule = Literal["box_beam_link", "ribbed_cast_link", "forked_yoke_link"]
WristModule = Literal[
    "wrist_1dof_roll",
    "wrist_2dof_pitch_roll",
    "wrist_2dof_roll_pitch",
    "wrist_3dof_spherical",
]
EndEffectorModule = Literal[
    "fixed_flange",
    "roll_flange",
    "parallel_gripper",
    "dexterous_hand",
]
GripperModule = Literal[
    "parallel_slide",
    "angular_2jaw",
    "concentric_3jaw_chuck",
    "adaptive_2finger",
]
JointLimitProfile = Literal["industrial_safe", "wide_range", "compact_service"]
DetailLevel = Literal["clean", "bolts", "industrial"]
PaletteTheme = Literal["cast_white", "retrofit_olive", "metrology_silver", "safety_yellow"]


BASE_MODULES: tuple[BaseYawRootModule, ...] = (
    "combined_shoulder_base",
    "yaw_turret",
    "yaw_carriage",
)
LINK_MODULES: tuple[ShoulderElbowLinkModule, ...] = (
    "box_beam_link",
    "ribbed_cast_link",
    "forked_yoke_link",
)
WRIST_MODULES: tuple[WristModule, ...] = (
    "wrist_1dof_roll",
    "wrist_2dof_pitch_roll",
    "wrist_2dof_roll_pitch",
    "wrist_3dof_spherical",
)
EFFECTOR_MODULES: tuple[EndEffectorModule, ...] = (
    "fixed_flange",
    "roll_flange",
    "parallel_gripper",
    "dexterous_hand",
)
GRIPPER_MODULES: tuple[GripperModule, ...] = (
    "parallel_slide",
    "angular_2jaw",
    "concentric_3jaw_chuck",
    "adaptive_2finger",
)

ANCHOR_BASE: BaseYawRootModule = "combined_shoulder_base"
ANCHOR_LINK: ShoulderElbowLinkModule = "box_beam_link"
ANCHOR_WRIST: WristModule = "wrist_1dof_roll"
ANCHOR_EFFECTOR: EndEffectorModule = "fixed_flange"
ANCHOR_GRIPPER: GripperModule = "parallel_slide"


ROBOT_ARM_PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "cast_white": {
        "cast": (0.86, 0.88, 0.86, 1.0),
        "dark": (0.10, 0.11, 0.12, 1.0),
        "steel": (0.66, 0.68, 0.70, 1.0),
        "accent": (0.06, 0.25, 0.56, 1.0),
        "rubber": (0.025, 0.025, 0.030, 1.0),
        "warning": (0.92, 0.64, 0.12, 1.0),
    },
    "retrofit_olive": {
        "cast": (0.30, 0.35, 0.31, 1.0),
        "dark": (0.055, 0.060, 0.060, 1.0),
        "steel": (0.62, 0.60, 0.55, 1.0),
        "accent": (0.16, 0.22, 0.23, 1.0),
        "rubber": (0.015, 0.015, 0.014, 1.0),
        "warning": (0.72, 0.54, 0.23, 1.0),
    },
    "metrology_silver": {
        "cast": (0.68, 0.70, 0.73, 1.0),
        "dark": (0.06, 0.07, 0.08, 1.0),
        "steel": (0.82, 0.84, 0.86, 1.0),
        "accent": (0.10, 0.45, 0.40, 1.0),
        "rubber": (0.025, 0.030, 0.030, 1.0),
        "warning": (0.18, 0.42, 0.78, 1.0),
    },
    "safety_yellow": {
        "cast": (0.88, 0.68, 0.12, 1.0),
        "dark": (0.06, 0.06, 0.065, 1.0),
        "steel": (0.58, 0.60, 0.62, 1.0),
        "accent": (0.16, 0.17, 0.18, 1.0),
        "rubber": (0.025, 0.025, 0.022, 1.0),
        "warning": (0.92, 0.90, 0.16, 1.0),
    },
}


@dataclass(frozen=True)
class RoboticArmsConfig:
    base_yaw_root_module: BaseYawRootModule | None = None
    shoulder_elbow_link_module: ShoulderElbowLinkModule | None = None
    wrist_module: WristModule | None = None
    end_effector_module: EndEffectorModule | None = None
    gripper_module: GripperModule | None = None
    finger_count: int | None = None

    palette_theme: PaletteTheme = "cast_white"
    total_reach: float = 1.05
    link_ratio: float = 0.54
    base_z: float = 0.36
    wrist_scale: float = 1.0
    finger_travel: float = 0.024
    joint_limit_profile: JointLimitProfile = "industrial_safe"
    detail_level: DetailLevel = "clean"
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(ROBOT_ARM_PALETTE_PRESETS["cast_white"])
    )


@dataclass(frozen=True)
class ResolvedRoboticArmsConfig:
    base_yaw_root_module: BaseYawRootModule
    shoulder_elbow_link_module: ShoulderElbowLinkModule
    wrist_module: WristModule
    end_effector_module: EndEffectorModule
    gripper_module: GripperModule
    finger_count: int
    palette_theme: PaletteTheme
    total_reach: float
    link_ratio: float
    upper_len: float
    forearm_len: float
    base_z: float
    wrist_len: float
    wrist_scale: float
    finger_travel: float
    joint_limit_profile: JointLimitProfile
    detail_level: DetailLevel
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _cyl_x() -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0, 0.0)


def _cyl_y() -> tuple[float, float, float]:
    return (-math.pi / 2.0, 0.0, 0.0)


def _weighted_finger_count(rng: random.Random) -> int:
    return rng.choices((2, 3), weights=(0.75, 0.25), k=1)[0]


def _finger_count_for_gripper(
    gripper_module: GripperModule, configured_finger_count: int | None = None
) -> int:
    if gripper_module in {"angular_2jaw", "adaptive_2finger"}:
        return 2
    if gripper_module == "concentric_3jaw_chuck":
        return 3
    finger_count = int(configured_finger_count or 2)
    if finger_count not in {2, 3}:
        raise ValueError("parallel_slide finger_count must be 2 or 3")
    return finger_count


def config_from_seed(seed: int) -> RoboticArmsConfig:
    if seed == 0:
        return RoboticArmsConfig(
            base_yaw_root_module=ANCHOR_BASE,
            shoulder_elbow_link_module=ANCHOR_LINK,
            wrist_module=ANCHOR_WRIST,
            end_effector_module=ANCHOR_EFFECTOR,
            gripper_module=ANCHOR_GRIPPER,
            finger_count=2,
            palette_theme="cast_white",
            total_reach=1.05,
            link_ratio=0.54,
            base_z=0.36,
            wrist_scale=1.0,
            finger_travel=0.024,
            joint_limit_profile="industrial_safe",
            detail_level="clean",
        )

    rng = random.Random(seed)
    end_effector: EndEffectorModule = rng.choice(EFFECTOR_MODULES)  # type: ignore[assignment]
    gripper_module: GripperModule = ANCHOR_GRIPPER
    finger_count = 5 if end_effector == "dexterous_hand" else 2
    if end_effector == "parallel_gripper":
        gripper_module = rng.choice(GRIPPER_MODULES)  # type: ignore[assignment]
        finger_count = (
            _weighted_finger_count(rng)
            if gripper_module == "parallel_slide"
            else _finger_count_for_gripper(gripper_module)
        )
    return RoboticArmsConfig(
        base_yaw_root_module=rng.choice(BASE_MODULES),  # type: ignore[arg-type]
        shoulder_elbow_link_module=rng.choice(LINK_MODULES),  # type: ignore[arg-type]
        wrist_module=rng.choice(WRIST_MODULES),  # type: ignore[arg-type]
        end_effector_module=end_effector,
        gripper_module=gripper_module,
        finger_count=finger_count,
        palette_theme=rng.choice(tuple(ROBOT_ARM_PALETTE_PRESETS.keys())),  # type: ignore[arg-type]
        total_reach=rng.uniform(0.70, 1.42),
        link_ratio=rng.uniform(0.48, 0.58),
        base_z=rng.uniform(0.18, 0.55),
        wrist_scale=rng.uniform(0.82, 1.20),
        finger_travel=rng.uniform(0.012, 0.035),
        joint_limit_profile=rng.choice(("industrial_safe", "wide_range", "compact_service")),  # type: ignore[arg-type]
        detail_level=rng.choice(("clean", "bolts", "industrial")),  # type: ignore[arg-type]
    )


def resolve_config(config: RoboticArmsConfig) -> ResolvedRoboticArmsConfig:
    base = config.base_yaw_root_module or ANCHOR_BASE
    link = config.shoulder_elbow_link_module or ANCHOR_LINK
    wrist = config.wrist_module or ANCHOR_WRIST
    effector = config.end_effector_module or ANCHOR_EFFECTOR
    gripper = config.gripper_module or ANCHOR_GRIPPER
    if base not in BASE_MODULES:
        raise ValueError(f"Unsupported base_yaw_root_module: {base!r}")
    if link not in LINK_MODULES:
        raise ValueError(f"Unsupported shoulder_elbow_link_module: {link!r}")
    if wrist not in WRIST_MODULES:
        raise ValueError(f"Unsupported wrist_module: {wrist!r}")
    if effector not in EFFECTOR_MODULES:
        raise ValueError(f"Unsupported end_effector_module: {effector!r}")
    if gripper not in GRIPPER_MODULES:
        raise ValueError(f"Unsupported gripper_module: {gripper!r}")
    if config.palette_theme not in ROBOT_ARM_PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme!r}")
    if config.joint_limit_profile not in {"industrial_safe", "wide_range", "compact_service"}:
        raise ValueError(f"Unsupported joint_limit_profile: {config.joint_limit_profile!r}")
    if config.detail_level not in {"clean", "bolts", "industrial"}:
        raise ValueError(f"Unsupported detail_level: {config.detail_level!r}")

    total_reach = _clamp(config.total_reach, 0.45, 1.50)
    link_ratio = _clamp(config.link_ratio, 0.48, 0.58)
    wrist_scale = _clamp(config.wrist_scale, 0.75, 1.25)
    wrist_len = 0.11 * wrist_scale
    available = max(0.38, total_reach - wrist_len - 0.11)
    upper_len = max(0.20, available * link_ratio)
    forearm_len = max(0.18, available - upper_len)

    if effector == "parallel_gripper":
        finger_count = _finger_count_for_gripper(gripper, config.finger_count)
    elif effector == "dexterous_hand":
        finger_count = 5
    else:
        finger_count = int(config.finger_count or 2)

    return ResolvedRoboticArmsConfig(
        base_yaw_root_module=base,
        shoulder_elbow_link_module=link,
        wrist_module=wrist,
        end_effector_module=effector,
        gripper_module=gripper,
        finger_count=finger_count,
        palette_theme=config.palette_theme,
        total_reach=total_reach,
        link_ratio=link_ratio,
        upper_len=upper_len,
        forearm_len=forearm_len,
        base_z=_clamp(config.base_z, 0.10, 0.60),
        wrist_len=wrist_len,
        wrist_scale=wrist_scale,
        finger_travel=_clamp(config.finger_travel, 0.010, 0.036),
        joint_limit_profile=config.joint_limit_profile,
        detail_level=config.detail_level,
        palette=dict(ROBOT_ARM_PALETTE_PRESETS[config.palette_theme]),
    )


def _limits(
    r: ResolvedRoboticArmsConfig, name: str, *, effort: float, velocity: float
) -> MotionLimits:
    if name == "base_yaw":
        if r.joint_limit_profile == "compact_service":
            return MotionLimits(effort=effort, velocity=velocity, lower=-1.70, upper=1.70)
        return MotionLimits(effort=effort, velocity=velocity, lower=-math.pi, upper=math.pi)
    if name == "shoulder":
        upper = 1.75 if r.joint_limit_profile == "wide_range" else 1.45
        # Lower bound kept at/above horizontal: a deeper back-tilt swings the
        # whole (folded/fisted) arm back over its own base plate and turret.
        return MotionLimits(effort=effort, velocity=velocity, lower=0.0, upper=upper)
    if name == "elbow":
        span = 2.65 if r.joint_limit_profile == "wide_range" else 2.15
        return MotionLimits(effort=effort, velocity=velocity, lower=-1.20, upper=span)
    if name == "finger_slide":
        return MotionLimits(effort=12.0, velocity=0.08, lower=0.0, upper=r.finger_travel)
    return MotionLimits(effort=effort, velocity=velocity, lower=-math.pi, upper=math.pi)


def _add_bolt_circle(
    part,
    *,
    prefix: str,
    radius: float,
    z: float,
    count: int,
    material: str = "steel",
) -> None:
    for i in range(count):
        angle = 2.0 * math.pi * i / count
        part.visual(
            Cylinder(radius=0.010, length=0.010),
            origin=Origin(xyz=(radius * math.cos(angle), radius * math.sin(angle), z)),
            material=material,
            name=f"{prefix}_bolt_{i}", material_class_id="metal.steel_bare",
        )


def _add_subtle_base_bolt_ring(part, *, prefix: str, radius: float, z: float, count: int) -> None:
    for i in range(count):
        angle = 2.0 * math.pi * i / count
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        part.visual(
            Cylinder(radius=0.010, length=0.006),
            origin=Origin(xyz=(x, y, z), rpy=(0.0, 0.0, angle)),
            material="dark",
            name=f"{prefix}_counterbore_{i}", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Cylinder(radius=0.0048, length=0.006),
            origin=Origin(xyz=(x, y, z + 0.003)),
            material="steel",
            name=f"{prefix}_cap_screw_{i}", material_class_id="metal.steel_bare",
        )


def _mesh_from_geometry_for_model(model: ArticulatedObject, geometry, name: str):
    if model.assets is not None:
        return mesh_from_geometry(geometry, model.assets.mesh_path(f"{name}.obj"))
    return mesh_from_geometry(geometry, name)


def _smooth_cylinder_mesh(
    model: ArticulatedObject,
    *,
    radius: float,
    length: float,
    name: str,
    radial_segments: int = 72,
):
    return _mesh_from_geometry_for_model(
        model,
        CylinderGeometry(radius=radius, height=length, radial_segments=radial_segments),
        name,
    )


def _yz_rounded_section(
    x: float,
    width_y: float,
    height_z: float,
    radius: float,
    *,
    z_shift: float = 0.0,
) -> list[tuple[float, float, float]]:
    return [
        (x, y, z + z_shift)
        for y, z in rounded_rect_profile(width_y, height_z, radius, corner_segments=10)
    ]


def _xy_rounded_section(
    z: float,
    length_x: float,
    width_y: float,
    radius: float,
    *,
    x_shift: float = 0.0,
) -> list[tuple[float, float, float]]:
    return [
        (x + x_shift, y, z)
        for x, y in rounded_rect_profile(length_x, width_y, radius, corner_segments=10)
    ]


def _dexterous_palm_shell_mesh(model: ArticulatedObject):
    sections = [
        _yz_rounded_section(0.004, 0.120, 0.090, 0.030, z_shift=-0.006),
        _yz_rounded_section(0.040, 0.190, 0.126, 0.038, z_shift=0.000),
        _yz_rounded_section(0.088, 0.215, 0.138, 0.032, z_shift=0.004),
        _yz_rounded_section(0.132, 0.188, 0.110, 0.026, z_shift=0.018),
    ]
    return _mesh_from_geometry_for_model(
        model,
        section_loft(sections),
        "dexterous_hand_tapered_palm_shell",
    )


def _dexterous_dorsal_cover_mesh(model: ArticulatedObject):
    sections = [
        _xy_rounded_section(-0.004, 0.088, 0.152, 0.018, x_shift=0.000),
        _xy_rounded_section(0.004, 0.078, 0.136, 0.016, x_shift=0.004),
    ]
    return _mesh_from_geometry_for_model(
        model,
        section_loft(sections),
        "dexterous_hand_dorsal_access_cover",
    )


def _dexterous_wrist_cover_mesh(model: ArticulatedObject):
    sections = [
        _yz_rounded_section(-0.006, 0.156, 0.056, 0.016),
        _yz_rounded_section(0.006, 0.140, 0.048, 0.014),
    ]
    return _mesh_from_geometry_for_model(
        model,
        section_loft(sections),
        "dexterous_hand_wrist_access_cover",
    )


def _adaptive_drive_shell_mesh(model: ArticulatedObject):
    sections = [
        _yz_rounded_section(0.000, 0.106, 0.082, 0.030, z_shift=0.000),
        _yz_rounded_section(0.028, 0.136, 0.114, 0.040, z_shift=0.014),
        _yz_rounded_section(0.078, 0.152, 0.128, 0.044, z_shift=0.020),
        _yz_rounded_section(0.124, 0.130, 0.104, 0.034, z_shift=0.004),
    ]
    return _mesh_from_geometry_for_model(
        model,
        section_loft(sections),
        "adaptive_2finger_rounded_drive_shell",
    )


def _adaptive_front_mask_mesh(model: ArticulatedObject):
    sections = [
        _yz_rounded_section(-0.006, 0.136, 0.092, 0.020, z_shift=-0.002),
        _yz_rounded_section(0.008, 0.148, 0.106, 0.024, z_shift=0.000),
    ]
    return _mesh_from_geometry_for_model(
        model,
        section_loft(sections),
        "adaptive_2finger_front_mask",
    )


def _adaptive_link_mesh(
    model: ArticulatedObject,
    *,
    length: float,
    width_y: float,
    height_z: float,
    radius: float,
    name: str,
    z_tip_shift: float = 0.0,
):
    radius = min(radius, width_y * 0.42, height_z * 0.42)
    sections = [
        _yz_rounded_section(0.000, width_y * 0.96, height_z * 0.96, radius),
        _yz_rounded_section(
            length * 0.45, width_y, height_z * 1.05, radius, z_shift=z_tip_shift * 0.35
        ),
        _yz_rounded_section(length, width_y * 0.90, height_z * 0.94, radius, z_shift=z_tip_shift),
    ]
    return _mesh_from_geometry_for_model(model, section_loft(sections), name)


def _adaptive_jaw_mesh(model: ArticulatedObject):
    sections = [
        _yz_rounded_section(0.000, 0.036, 0.052, 0.012, z_shift=0.000),
        _yz_rounded_section(0.038, 0.034, 0.060, 0.013, z_shift=-0.004),
        _yz_rounded_section(0.084, 0.029, 0.052, 0.011, z_shift=-0.012),
        _yz_rounded_section(0.116, 0.030, 0.040, 0.010, z_shift=-0.020),
    ]
    return _mesh_from_geometry_for_model(
        model,
        section_loft(sections),
        "adaptive_2finger_milled_lower_jaw",
    )


def _adaptive_grip_pad_mesh(model: ArticulatedObject, name: str):
    sections = [
        _yz_rounded_section(0.000, 0.018, 0.018, 0.006),
        _yz_rounded_section(0.038, 0.020, 0.020, 0.007),
        _yz_rounded_section(0.080, 0.018, 0.018, 0.006),
    ]
    return _mesh_from_geometry_for_model(model, section_loft(sections), name)


def _angular_curved_grip_pad_mesh(model: ArticulatedObject, name: str):
    sections = [
        _yz_rounded_section(0.000, 0.014, 0.023, 0.0050, z_shift=0.000),
        _yz_rounded_section(0.028, 0.015, 0.024, 0.0052, z_shift=-0.004),
        _yz_rounded_section(0.058, 0.014, 0.023, 0.0050, z_shift=-0.011),
        _yz_rounded_section(0.078, 0.013, 0.021, 0.0046, z_shift=-0.017),
    ]
    return _mesh_from_geometry_for_model(model, section_loft(sections), name)


def _parallel_slide_housing_mesh(model: ArticulatedObject):
    sections = [
        _yz_rounded_section(0.000, 0.102, 0.074, 0.020),
        _yz_rounded_section(0.044, 0.132, 0.092, 0.024),
        _yz_rounded_section(0.092, 0.138, 0.090, 0.020),
    ]
    return _mesh_from_geometry_for_model(
        model,
        section_loft(sections),
        "parallel_slide_rounded_actuator_housing",
    )


def _parallel_slide_jaw_mesh(model: ArticulatedObject, name: str):
    sections = [
        _yz_rounded_section(0.000, 0.024, 0.034, 0.008),
        _yz_rounded_section(0.060, 0.026, 0.050, 0.010, z_shift=-0.002),
        _yz_rounded_section(0.120, 0.024, 0.044, 0.009, z_shift=-0.010),
    ]
    return _mesh_from_geometry_for_model(model, section_loft(sections), name)


def _angular_drive_body_mesh(model: ArticulatedObject):
    sections = [
        _yz_rounded_section(0.000, 0.088, 0.080, 0.018),
        _yz_rounded_section(0.044, 0.110, 0.098, 0.020),
        _yz_rounded_section(0.092, 0.124, 0.102, 0.018),
    ]
    return _mesh_from_geometry_for_model(model, section_loft(sections), "angular_2jaw_drive_body")


def _angular_jaw_mesh(model: ArticulatedObject, name: str):
    sections = [
        _yz_rounded_section(0.000, 0.024, 0.040, 0.009),
        _yz_rounded_section(0.050, 0.026, 0.052, 0.010, z_shift=-0.004),
        _yz_rounded_section(0.110, 0.026, 0.050, 0.010, z_shift=-0.018),
        _yz_rounded_section(0.142, 0.026, 0.036, 0.009, z_shift=-0.030),
    ]
    return _mesh_from_geometry_for_model(model, section_loft(sections), name)


def _angular_pad_retainer_rail_mesh(model: ArticulatedObject, name: str):
    sections = [
        _yz_rounded_section(0.000, 0.006, 0.005, 0.0022, z_shift=0.000),
        _yz_rounded_section(0.026, 0.006, 0.005, 0.0022, z_shift=-0.003),
        _yz_rounded_section(0.052, 0.0055, 0.0048, 0.0020, z_shift=-0.009),
        _yz_rounded_section(0.066, 0.005, 0.0045, 0.0019, z_shift=-0.013),
    ]
    return _mesh_from_geometry_for_model(model, section_loft(sections), name)


def _chuck_jaw_mesh(model: ArticulatedObject, name: str):
    sections = [
        _yz_rounded_section(0.000, 0.028, 0.028, 0.008),
        _yz_rounded_section(0.052, 0.028, 0.044, 0.010, z_shift=-0.003),
        _yz_rounded_section(0.096, 0.026, 0.050, 0.010, z_shift=-0.010),
    ]
    return _mesh_from_geometry_for_model(model, section_loft(sections), name)


def _chuck_grip_insert_mesh(model: ArticulatedObject, name: str):
    sections = [
        _yz_rounded_section(0.000, 0.016, 0.012, 0.004),
        _yz_rounded_section(0.032, 0.018, 0.014, 0.005, z_shift=-0.002),
        _yz_rounded_section(0.060, 0.016, 0.012, 0.004, z_shift=-0.006),
    ]
    return _mesh_from_geometry_for_model(model, section_loft(sections), name)


def _chuck_insert_retainer_rail_mesh(model: ArticulatedObject, name: str):
    sections = [
        _yz_rounded_section(0.000, 0.0048, 0.0048, 0.0018, z_shift=0.000),
        _yz_rounded_section(0.026, 0.0048, 0.0046, 0.0018, z_shift=-0.0018),
        _yz_rounded_section(0.052, 0.0042, 0.0042, 0.0016, z_shift=-0.0050),
    ]
    return _mesh_from_geometry_for_model(model, section_loft(sections), name)


def _arc_section(
    *,
    center_angle: float,
    radius: float,
    z: float,
    width_radial: float,
    height_z: float,
    corner_radius: float,
) -> list[tuple[float, float, float]]:
    radial = (math.cos(center_angle), math.sin(center_angle), 0.0)
    return [
        (
            (radius + radial_offset) * radial[0],
            (radius + radial_offset) * radial[1],
            z + z_offset,
        )
        for radial_offset, z_offset in rounded_rect_profile(
            width_radial,
            height_z,
            corner_radius,
            corner_segments=8,
        )
    ]


def _datum_curved_carriage_rail_mesh(
    model: ArticulatedObject,
    name: str,
    *,
    center_angle: float,
    z: float,
    radius: float = 0.155,
    span: float = 1.62,
    width_radial: float = 0.052,
    height_z: float = 0.018,
):
    sections = [
        _arc_section(
            center_angle=center_angle + offset,
            radius=radius,
            z=z,
            width_radial=width_radial,
            height_z=height_z,
            corner_radius=min(0.007, width_radial * 0.22, height_z * 0.42),
        )
        for offset in (-span * 0.50, -span * 0.25, 0.0, span * 0.25, span * 0.50)
    ]
    return _mesh_from_geometry_for_model(model, section_loft(sections), name)


def _datum_carriage_rail_mesh(model: ArticulatedObject, name: str):
    sections = [
        _yz_rounded_section(0.000, 0.044, 0.018, 0.007),
        _yz_rounded_section(0.200, 0.048, 0.020, 0.0075),
        _yz_rounded_section(0.400, 0.044, 0.018, 0.007),
    ]
    return _mesh_from_geometry_for_model(model, section_loft(sections), name)


def _build_base(model: ArticulatedObject, r: ResolvedRoboticArmsConfig) -> tuple[str, float]:
    base = model.part("base")
    base.visual(
        _smooth_cylinder_mesh(model, radius=0.20, length=0.070, name="base_floor_plate_round_72"),
        origin=Origin(xyz=(0.0, 0.0, 0.035)),
        material="dark",
        name="floor_plate", material_class_id="metal.blackened_gunmetal",
    )
    if r.base_yaw_root_module == "yaw_carriage":
        base.visual(
            Box((0.62, 0.46, 0.058)),
            origin=Origin(xyz=(0.0, 0.0, 0.060)),
            material="cast",
            name="datum_floor_plate", material_class_id="metal.paint_coated",
        )
        base.visual(
            Cylinder(radius=0.14, length=max(0.080, r.base_z - 0.08)),
            origin=Origin(xyz=(0.0, 0.0, r.base_z * 0.50)),
            material="steel",
            name="metrology_pedestal", material_class_id="metal.steel_bare",
        )
        for center_angle, suffix in ((-math.pi / 2.0, "rear"), (math.pi / 2.0, "front")):
            rail_z = r.base_z - 0.018
            base.visual(
                _datum_curved_carriage_rail_mesh(
                    model,
                    f"datum_curved_carriage_rail_{suffix}_mesh",
                    center_angle=center_angle,
                    z=rail_z,
                ),
                origin=Origin(),
                material="steel",
                name=f"curved_datum_rail_{suffix}", material_class_id="metal.steel_bare",
            )
            base.visual(
                _datum_curved_carriage_rail_mesh(
                    model,
                    f"datum_curved_reference_groove_{suffix}_mesh",
                    center_angle=center_angle,
                    z=rail_z + 0.010,
                    radius=0.155,
                    span=1.46,
                    width_radial=0.006,
                    height_z=0.004,
                ),
                origin=Origin(),
                material="dark",
                name=f"curved_rail_reference_groove_{suffix}", material_class_id="metal.blackened_gunmetal",
            )
            for angle_offset, end_name in ((-0.82, "left"), (0.82, "right")):
                end_angle = center_angle + angle_offset
                base.visual(
                    Box((0.018, 0.048, 0.018)),
                    origin=Origin(
                        xyz=(
                            0.155 * math.cos(end_angle),
                            0.155 * math.sin(end_angle),
                            rail_z + 0.001,
                        ),
                        rpy=(0.0, 0.0, end_angle + math.pi / 2.0),
                    ),
                    material="steel",
                    name=f"rail_stop_block_{suffix}_{end_name}", material_class_id="metal.steel_bare",
                )
            for angle_offset, screw_name in ((-0.46, "left"), (0.46, "right")):
                screw_angle = center_angle + angle_offset
                base.visual(
                    Cylinder(radius=0.007, length=0.006),
                    origin=Origin(
                        xyz=(
                            0.155 * math.cos(screw_angle),
                            0.155 * math.sin(screw_angle),
                            rail_z + 0.011,
                        )
                    ),
                    material="steel",
                    name=f"rail_counterbore_{suffix}_{screw_name}", material_class_id="metal.steel_bare",
                )
                base.visual(
                    Cylinder(radius=0.0028, length=0.007),
                    origin=Origin(
                        xyz=(
                            0.155 * math.cos(screw_angle),
                            0.155 * math.sin(screw_angle),
                            rail_z + 0.013,
                        )
                    ),
                    material="dark",
                    name=f"rail_hex_socket_{suffix}_{screw_name}", material_class_id="metal.blackened_gunmetal",
                )
    elif r.base_yaw_root_module == "yaw_turret":
        base.visual(
            Cylinder(radius=0.13, length=max(0.080, r.base_z - 0.08)),
            origin=Origin(xyz=(0.0, 0.0, r.base_z * 0.50)),
            material="cast",
            name="pedestal_column", material_class_id="metal.paint_coated",
        )
        base.visual(
            _smooth_cylinder_mesh(model, radius=0.24, length=0.075, name="yaw_socket_round_72"),
            origin=Origin(xyz=(0.0, 0.0, r.base_z - 0.030)),
            material="dark",
            name="yaw_socket", material_class_id="metal.blackened_gunmetal",
        )
    else:
        base.visual(
            Cylinder(radius=0.095, length=max(0.070, r.base_z - 0.07)),
            origin=Origin(xyz=(0.0, 0.0, r.base_z * 0.50)),
            material="cast",
            name="pedestal_column", material_class_id="metal.paint_coated",
        )
        base.visual(
            _smooth_cylinder_mesh(model, radius=0.15, length=0.058, name="top_turntable_round_72"),
            origin=Origin(xyz=(0.0, 0.0, r.base_z - 0.026)),
            material="steel",
            name="top_turntable", material_class_id="metal.steel_bare",
        )
    base.visual(
        _smooth_cylinder_mesh(model, radius=0.135, length=0.080, name="yaw_bearing_cap_round_72"),
        origin=Origin(xyz=(0.0, 0.0, r.base_z - 0.020)),
        material="steel",
        name="yaw_bearing_cap", material_class_id="metal.steel_bare",
    )
    if r.detail_level != "clean":
        _add_subtle_base_bolt_ring(base, prefix="base_anchor", radius=0.165, z=0.070, count=8)

    shoulder = model.part("shoulder_root")
    shoulder.visual(
        Cylinder(radius=0.105, length=0.080),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="steel",
        name="yaw_spindle", material_class_id="metal.steel_bare",
    )
    if r.base_yaw_root_module == "yaw_turret":
        shoulder_height = 0.24
        shoulder.visual(
            Cylinder(radius=0.19, length=0.070),
            origin=Origin(xyz=(0.0, 0.0, 0.060)),
            material="cast",
            name="turret_deck", material_class_id="metal.paint_coated",
        )
        shoulder.visual(
            Box((0.22, 0.24, 0.090)),
            origin=Origin(xyz=(0.10, 0.0, 0.115)),
            material="cast",
            name="shoulder_adapter", material_class_id="metal.paint_coated",
        )
        for y, suffix in ((0.13, "front"), (-0.13, "rear")):
            shoulder.visual(
                Box((0.13, 0.050, 0.22)),
                origin=Origin(xyz=(0.15, y, shoulder_height)),
                material="cast",
                name=f"shoulder_yoke_{suffix}", material_class_id="metal.paint_coated",
            )
        shoulder.visual(
            Cylinder(radius=0.085, length=0.24),
            origin=Origin(xyz=(0.070, 0.0, shoulder_height), rpy=_cyl_y()),
            material="cast",
            name="shoulder_cross_boss", material_class_id="metal.paint_coated",
        )
    elif r.base_yaw_root_module == "yaw_carriage":
        shoulder_height = 0.27
        shoulder.visual(
            Cylinder(radius=0.16, length=0.060),
            origin=Origin(xyz=(0.0, 0.0, 0.045)),
            material="steel",
            name="yaw_cartridge", material_class_id="metal.steel_bare",
        )
        shoulder.visual(
            Box((0.15, 0.19, 0.22)),
            origin=Origin(xyz=(0.0, 0.0, 0.155)),
            material="cast",
            name="riser_block", material_class_id="metal.paint_coated",
        )
        for y, suffix in ((0.12, "front"), (-0.12, "rear")):
            shoulder.visual(
                Box((0.14, 0.055, 0.19)),
                origin=Origin(xyz=(0.0, y, shoulder_height)),
                material="cast",
                name=f"pitch_cheek_{suffix}", material_class_id="metal.paint_coated",
            )
    else:
        shoulder_height = 0.18
        shoulder.visual(
            Cylinder(radius=0.056, length=shoulder_height - 0.020),
            origin=Origin(xyz=(0.0, 0.0, shoulder_height * 0.50), rpy=(0.0, 0.0, 0.0)),
            material="cast",
            name="shoulder_neck", material_class_id="metal.paint_coated",
        )
        shoulder.visual(
            Sphere(radius=0.105),
            origin=Origin(xyz=(0.0, 0.0, shoulder_height)),
            material="cast",
            name="shoulder_cap", material_class_id="metal.paint_coated",
        )
        shoulder.visual(
            Cylinder(radius=0.105, length=0.18),
            origin=Origin(xyz=(0.0, 0.0, shoulder_height), rpy=_cyl_y()),
            material="cast",
            name="shoulder_motor", material_class_id="metal.paint_coated",
        )
    shoulder.visual(
        Cylinder(radius=0.055, length=0.24),
        origin=Origin(xyz=(0.0, 0.0, shoulder_height), rpy=_cyl_y()),
        material="steel",
        name="shoulder_axis_core", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "base_yaw",
        ArticulationType.REVOLUTE,
        parent=base,
        child=shoulder,
        origin=Origin(xyz=(0.0, 0.0, r.base_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=_limits(r, "base_yaw", effort=180.0, velocity=1.2),
    )
    return "shoulder_root", shoulder_height


def _build_upper_arm(part, r: ResolvedRoboticArmsConfig) -> None:
    L = r.upper_len
    if r.shoulder_elbow_link_module == "ribbed_cast_link":
        part.visual(
            Cylinder(radius=0.090, length=0.26),
            origin=Origin(rpy=_cyl_y()),
            material="cast",
            name="shoulder_hub", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((L * 0.94, 0.11, 0.090)),
            origin=Origin(xyz=(L * 0.485, 0.0, 0.0)),
            material="cast",
            name="upper_cast_beam", material_class_id="metal.paint_coated",
        )
        for z, name in ((0.054, "top_rib"), (-0.054, "lower_rib")):
            part.visual(
                Box((L * 0.62, 0.035, 0.020)),
                origin=Origin(xyz=(L * 0.43, 0.0, z)),
                material="accent",
                name=f"upper_{name}", material_class_id="metal.paint_coated",
            )
        part.visual(
            Box((0.10, 0.25, 0.11)),
            origin=Origin(xyz=(L, 0.0, 0.0)),
            material="cast",
            name="elbow_cartridge", material_class_id="metal.paint_coated",
        )
        part.visual(
            Cylinder(radius=0.075, length=0.20),
            origin=Origin(xyz=(L, 0.0, 0.0), rpy=_cyl_y()),
            material="steel",
            name="elbow_bearing", material_class_id="metal.steel_bare",
        )
    elif r.shoulder_elbow_link_module == "forked_yoke_link":
        part.visual(
            Cylinder(radius=0.080, length=0.30),
            origin=Origin(rpy=_cyl_y()),
            material="steel",
            name="shoulder_axle", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box((L * 0.94, 0.080, 0.090)),
            origin=Origin(xyz=(L * 0.48, 0.0, 0.0)),
            material="cast",
            name="metrology_beam", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((L * 0.70, 0.022, 0.014)),
            origin=Origin(xyz=(L * 0.45, 0.0, 0.051)),
            material="steel",
            name="top_datum_rail", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box((0.12, 0.30, 0.080)),
            origin=Origin(xyz=(L - 0.04, 0.0, 0.0)),
            material="cast",
            name="elbow_bridge", material_class_id="metal.paint_coated",
        )
        for y, suffix in ((0.125, "front"), (-0.125, "rear")):
            part.visual(
                Box((0.14, 0.055, 0.13)),
                origin=Origin(xyz=(L, y, 0.0)),
                material="cast",
                name=f"elbow_fork_{suffix}", material_class_id="metal.paint_coated",
            )
    else:
        part.visual(
            Cylinder(radius=0.085, length=0.20),
            origin=Origin(rpy=_cyl_y()),
            material="cast",
            name="shoulder_hub", material_class_id="metal.paint_coated",
        )
        for y, suffix in ((0.050, "front"), (-0.050, "rear")):
            part.visual(
                Box((L * 0.92, 0.040, 0.060)),
                origin=Origin(xyz=(L * 0.49, y, 0.0)),
                material="cast",
                name=f"upper_rail_{suffix}", material_class_id="metal.paint_coated",
            )
        part.visual(
            Box((L * 0.58, 0.12, 0.020)),
            origin=Origin(xyz=(L * 0.48, 0.0, 0.040)),
            material="accent",
            name="upper_service_cover", material_class_id="plastic.opaque_glossy_molded",
        )
        for y, suffix in ((0.078, "front"), (-0.078, "rear")):
            part.visual(
                Cylinder(radius=0.062, length=0.038),
                origin=Origin(xyz=(L, y, 0.0), rpy=_cyl_y()),
                material="cast",
                name=f"elbow_fork_{suffix}", material_class_id="metal.paint_coated",
            )
        part.visual(
            Cylinder(radius=0.018, length=0.18),
            origin=Origin(xyz=(L, 0.0, 0.0), rpy=_cyl_y()),
            material="steel",
            name="elbow_pin", material_class_id="metal.steel_bare",
        )


def _build_forearm(part, r: ResolvedRoboticArmsConfig) -> None:
    L = r.forearm_len
    style = r.shoulder_elbow_link_module
    if style == "ribbed_cast_link":
        part.visual(
            Cylinder(radius=0.070, length=0.18),
            origin=Origin(rpy=_cyl_y()),
            material="steel",
            name="elbow_hub", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box((L * 0.96, 0.095, 0.080)),
            origin=Origin(xyz=(L * 0.50, 0.0, 0.0)),
            material="cast",
            name="forearm_cast_beam", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((L * 0.55, 0.030, 0.018)),
            origin=Origin(xyz=(L * 0.43, 0.0, 0.047)),
            material="accent",
            name="forearm_top_rib", material_class_id="metal.paint_coated",
        )
        part.visual(
            Cylinder(radius=0.065, length=0.080),
            origin=Origin(xyz=(L, 0.0, 0.0), rpy=_cyl_x()),
            material="cast",
            name="wrist_bearing", material_class_id="metal.paint_coated",
        )
    elif style == "forked_yoke_link":
        part.visual(
            Cylinder(radius=0.066, length=0.16),
            origin=Origin(rpy=_cyl_y()),
            material="steel",
            name="elbow_axle", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box((L * 0.94, 0.084, 0.082)),
            origin=Origin(xyz=(L * 0.49, 0.0, 0.0)),
            material="cast",
            name="forearm_beam", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((L * 0.62, 0.020, 0.012)),
            origin=Origin(xyz=(L * 0.43, 0.0, 0.047)),
            material="steel",
            name="forearm_datum", material_class_id="metal.steel_bare",
        )
        for y, suffix in ((0.060, "front"), (-0.060, "rear")):
            part.visual(
                Box((0.11, 0.030, 0.085)),
                origin=Origin(xyz=(L, y, 0.0)),
                material="cast",
                name=f"wrist_fork_{suffix}", material_class_id="metal.paint_coated",
            )
        part.visual(
            Cylinder(radius=0.060, length=0.12),
            origin=Origin(xyz=(L, 0.0, 0.0), rpy=_cyl_x()),
            material="steel",
            name="wrist_axis", material_class_id="metal.steel_bare",
        )
    else:
        part.visual(
            Cylinder(radius=0.060, length=0.10),
            origin=Origin(rpy=_cyl_y()),
            material="cast",
            name="elbow_lug", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((L * 0.94, 0.070, 0.064)),
            origin=Origin(xyz=(L * 0.50, 0.0, 0.0)),
            material="cast",
            name="forearm_beam", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((L * 0.58, 0.028, 0.020)),
            origin=Origin(xyz=(L * 0.52, 0.0, 0.042)),
            material="accent",
            name="cable_cover", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            Cylinder(radius=0.060, length=0.052),
            origin=Origin(xyz=(L, 0.0, 0.0), rpy=_cyl_x()),
            material="cast",
            name="wrist_bearing", material_class_id="metal.paint_coated",
        )


def _build_main_links(
    model: ArticulatedObject,
    r: ResolvedRoboticArmsConfig,
    shoulder_parent_name: str,
    shoulder_origin_z: float,
) -> tuple[str, tuple[float, float, float]]:
    shoulder_parent = model.get_part(shoulder_parent_name)
    upper = model.part("upper_arm")
    _build_upper_arm(upper, r)
    forearm = model.part("forearm")
    _build_forearm(forearm, r)
    model.articulation(
        "shoulder_pitch",
        ArticulationType.REVOLUTE,
        parent=shoulder_parent,
        child=upper,
        origin=Origin(xyz=(0.0, 0.0, shoulder_origin_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=_limits(r, "shoulder", effort=160.0, velocity=1.0),
    )
    model.articulation(
        "elbow_pitch",
        ArticulationType.REVOLUTE,
        parent=upper,
        child=forearm,
        origin=Origin(xyz=(r.upper_len, 0.0, 0.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=_limits(r, "elbow", effort=120.0, velocity=1.1),
    )
    return "forearm", (r.forearm_len, 0.0, 0.0)


def _make_wrist_part(model: ArticulatedObject, name: str, *, length: float, radius: float) -> None:
    part = model.part(name)
    part.visual(
        Cylinder(radius=radius, length=0.070),
        origin=Origin(rpy=_cyl_x()),
        material="steel",
        name=f"{name}_input_hub", material_class_id="metal.steel_bare",
    )
    part.visual(
        Box((length, radius * 1.55, radius * 1.55)),
        origin=Origin(xyz=(length * 0.50, 0.0, 0.0)),
        material="cast",
        name=f"{name}_body", material_class_id="metal.paint_coated",
    )
    part.visual(
        Cylinder(radius=radius * 0.82, length=0.045),
        origin=Origin(xyz=(length, 0.0, 0.0), rpy=_cyl_x()),
        material="steel",
        name=f"{name}_output_hub", material_class_id="metal.steel_bare",
    )


def _build_wrist(
    model: ArticulatedObject,
    r: ResolvedRoboticArmsConfig,
    parent_name: str,
    parent_tip: tuple[float, float, float],
) -> tuple[str, tuple[float, float, float]]:
    current_parent = parent_name
    current_tip = parent_tip
    scale = r.wrist_scale
    radius = 0.050 * scale

    def add_segment(
        name: str, axis: tuple[float, float, float], length: float, limits_name: str
    ) -> None:
        nonlocal current_parent, current_tip
        _make_wrist_part(model, name, length=length, radius=radius)
        model.articulation(
            name,
            ArticulationType.REVOLUTE,
            parent=model.get_part(current_parent),
            child=model.get_part(name),
            origin=Origin(xyz=current_tip),
            axis=axis,
            motion_limits=_limits(r, limits_name, effort=42.0, velocity=2.4),
        )
        current_parent = name
        current_tip = (length, 0.0, 0.0)

    if r.wrist_module == "wrist_1dof_roll":
        add_segment("wrist_roll", (1.0, 0.0, 0.0), r.wrist_len, "wrist")
    elif r.wrist_module == "wrist_2dof_pitch_roll":
        add_segment("wrist_pitch", (0.0, -1.0, 0.0), r.wrist_len * 0.72, "wrist")
        add_segment("wrist_roll", (1.0, 0.0, 0.0), r.wrist_len * 0.72, "wrist")
    elif r.wrist_module == "wrist_2dof_roll_pitch":
        add_segment("wrist_roll", (1.0, 0.0, 0.0), r.wrist_len * 0.72, "wrist")
        add_segment("wrist_pitch", (0.0, -1.0, 0.0), r.wrist_len * 0.72, "wrist")
    else:
        add_segment("wrist_yaw", (0.0, 0.0, 1.0), r.wrist_len * 0.62, "wrist")
        add_segment("wrist_pitch", (0.0, 1.0, 0.0), r.wrist_len * 0.62, "wrist")
        add_segment("tool_roll", (1.0, 0.0, 0.0), r.wrist_len * 0.62, "wrist")
    return current_parent, current_tip


def _build_flange_part(model: ArticulatedObject, name: str, r: ResolvedRoboticArmsConfig) -> None:
    part = model.part(name)
    part.visual(
        Cylinder(radius=0.043, length=0.042),
        origin=Origin(rpy=_cyl_x()),
        material="steel",
        name="flange_shaft", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=0.066, length=0.026),
        origin=Origin(xyz=(0.033, 0.0, 0.0), rpy=_cyl_x()),
        material="cast",
        name="tool_flange", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((0.018, 0.110, 0.110)),
        origin=Origin(xyz=(0.0545, 0.0, 0.0)),
        material="dark",
        name="mounting_face", material_class_id="metal.blackened_gunmetal",
    )
    if r.detail_level != "clean":
        for i, (y, z) in enumerate(
            ((-0.030, -0.030), (-0.030, 0.030), (0.030, -0.030), (0.030, 0.030))
        ):
            part.visual(
                Cylinder(radius=0.006, length=0.008),
                origin=Origin(xyz=(0.066, y, z), rpy=_cyl_x()),
                material="steel",
                name=f"face_bolt_{i}", material_class_id="metal.steel_bare",
            )


def _attach_fixed_flange(
    model: ArticulatedObject,
    r: ResolvedRoboticArmsConfig,
    parent_name: str,
    parent_tip: tuple[float, float, float],
) -> None:
    _build_flange_part(model, "tool_flange", r)
    model.articulation(
        "tool_fixed",
        ArticulationType.FIXED,
        parent=model.get_part(parent_name),
        child=model.get_part("tool_flange"),
        origin=Origin(xyz=parent_tip),
    )


def _attach_roll_flange(
    model: ArticulatedObject,
    r: ResolvedRoboticArmsConfig,
    parent_name: str,
    parent_tip: tuple[float, float, float],
) -> None:
    _build_flange_part(model, "roll_flange", r)
    model.articulation(
        "end_effector_roll",
        ArticulationType.CONTINUOUS,
        parent=model.get_part(parent_name),
        child=model.get_part("roll_flange"),
        origin=Origin(xyz=parent_tip),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=28.0, velocity=4.0),
    )


def _attach_parallel_slide_gripper(
    model: ArticulatedObject,
    r: ResolvedRoboticArmsConfig,
    parent_name: str,
    parent_tip: tuple[float, float, float],
) -> None:
    palm = model.part("gripper_base")
    palm.visual(
        Cylinder(radius=0.058, length=0.040),
        origin=Origin(rpy=_cyl_x()),
        material="steel",
        name="wrist_coupler", material_class_id="metal.steel_bare",
    )
    palm.visual(
        _parallel_slide_housing_mesh(model),
        origin=Origin(xyz=(0.004, 0.0, 0.0)),
        material="cast",
        name="linear_actuator_housing", material_class_id="metal.paint_coated",
    )
    palm.visual(
        Box((0.014, 0.136, 0.086)),
        origin=Origin(xyz=(0.098, 0.0, 0.0)),
        material="dark",
        name="recessed_front_slide_face", material_class_id="metal.blackened_gunmetal",
    )
    for z, suffix in ((0.040, "top"), (-0.040, "bottom")):
        palm.visual(
            Box((0.080, 0.122, 0.008)),
            origin=Origin(xyz=(0.070, 0.0, z)),
            material="steel",
            name=f"precision_guide_rail_{suffix}", material_class_id="metal.steel_bare",
        )
    for y, suffix in ((-0.032, "a"), (0.032, "b")):
        palm.visual(
            Box((0.008, 0.008, 0.070)),
            origin=Origin(xyz=(0.106, y, 0.0)),
            material="steel",
            name=f"vertical_slide_keyway_{suffix}", material_class_id="metal.steel_bare",
        )
    for y, z, suffix in (
        (-0.050, 0.030, "upper_left"),
        (0.050, 0.030, "upper_right"),
        (-0.050, -0.030, "lower_left"),
        (0.050, -0.030, "lower_right"),
    ):
        palm.visual(
            Cylinder(radius=0.0065, length=0.008),
            origin=Origin(xyz=(0.105, y, z), rpy=_cyl_x()),
            material="steel",
            name=f"counterbore_screw_{suffix}", material_class_id="metal.steel_bare",
        )
        palm.visual(
            Cylinder(radius=0.0025, length=0.010),
            origin=Origin(xyz=(0.106, y, z), rpy=_cyl_x()),
            material="dark",
            name=f"hex_socket_{suffix}", material_class_id="metal.blackened_gunmetal",
        )
    palm.visual(
        Box((0.052, 0.080, 0.006)),
        origin=Origin(xyz=(0.052, 0.0, 0.047)),
        material="accent",
        name="linear_scale_cover", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "gripper_mount",
        ArticulationType.FIXED,
        parent=model.get_part(parent_name),
        child=palm,
        origin=Origin(xyz=parent_tip),
    )
    radius = 0.045 if r.finger_count == 3 else 0.052
    for i in range(r.finger_count):
        angle = 2.0 * math.pi * i / r.finger_count + (math.pi / 2.0 if r.finger_count == 2 else 0.0)
        y = radius * math.cos(angle)
        z = radius * math.sin(angle)
        finger = model.part(f"finger_{i}")
        finger.visual(
            Box((0.070, 0.026, 0.030)),
            origin=Origin(xyz=(0.036, 0.0, 0.0)),
            material="steel",
            name="cross_roller_carriage", material_class_id="metal.steel_bare",
        )
        finger.visual(
            _parallel_slide_jaw_mesh(model, f"parallel_slide_finger_{i}_milled_jaw_mesh"),
            origin=Origin(xyz=(0.042, 0.0, -0.002)),
            material="cast",
            name="milled_step_jaw_body", material_class_id="metal.paint_coated",
        )
        finger.visual(
            Box((0.070, 0.006, 0.026)),
            origin=Origin(xyz=(0.104, 0.0, -0.004)),
            material="dark",
            name="inset_grip_pad_pocket", material_class_id="metal.blackened_gunmetal",
        )
        finger.visual(
            Box((0.050, 0.010, 0.020)),
            origin=Origin(xyz=(0.112, 0.0, -0.004)),
            material="rubber",
            name="flat_replaceable_grip_pad", material_class_id="rubber.smooth_plain",
        )
        for x, suffix in ((0.070, "rear"), (0.128, "front")):
            finger.visual(
                Cylinder(radius=0.0055, length=0.024),
                origin=Origin(xyz=(x, 0.0, 0.016), rpy=_cyl_y()),
                material="steel",
                name=f"jaw_insert_screw_{suffix}", material_class_id="metal.steel_bare",
            )
            finger.visual(
                Cylinder(radius=0.0022, length=0.026),
                origin=Origin(xyz=(x, 0.0, 0.016), rpy=_cyl_y()),
                material="dark",
                name=f"jaw_insert_hex_{suffix}", material_class_id="metal.blackened_gunmetal",
            )
        finger.visual(
            Box((0.036, 0.018, 0.006)),
            origin=Origin(xyz=(0.052, 0.0, 0.019)),
            material="steel",
            name="carriage_clamp_plate", material_class_id="metal.steel_bare",
        )
        finger.visual(
            Cylinder(radius=0.008, length=0.028),
            origin=Origin(xyz=(0.042, 0.0, -0.017), rpy=_cyl_y()),
            material="steel",
            name="carriage_dowel_pin", material_class_id="metal.steel_bare",
        )
        axis = (0.0, -math.cos(angle), -math.sin(angle))
        model.articulation(
            f"finger_slide_{i}",
            ArticulationType.PRISMATIC,
            parent=palm,
            child=finger,
            origin=Origin(xyz=(0.100, y, z), rpy=(angle, 0.0, 0.0)),
            axis=axis,
            motion_limits=_limits(r, "finger_slide", effort=12.0, velocity=0.08),
            mimic=None if i == 0 else Mimic(joint="finger_slide_0", multiplier=1.0, offset=0.0),
        )


def _attach_angular_2jaw_gripper(
    model: ArticulatedObject,
    r: ResolvedRoboticArmsConfig,
    parent_name: str,
    parent_tip: tuple[float, float, float],
) -> None:
    palm = model.part("gripper_base")
    palm.visual(
        Cylinder(radius=0.060, length=0.040),
        origin=Origin(rpy=_cyl_x()),
        material="steel",
        name="wrist_coupler", material_class_id="metal.steel_bare",
    )
    palm.visual(
        _angular_drive_body_mesh(model),
        origin=Origin(xyz=(0.004, 0.0, 0.0)),
        material="cast",
        name="pneumatic_drive_body", material_class_id="metal.paint_coated",
    )
    palm.visual(
        Box((0.014, 0.120, 0.090)),
        origin=Origin(xyz=(0.100, 0.0, -0.002)),
        material="dark",
        name="recessed_front_pivot_plate", material_class_id="metal.blackened_gunmetal",
    )
    for y, suffix in ((-0.054, "left"), (0.054, "right")):
        palm.visual(
            _adaptive_link_mesh(
                model,
                length=0.050,
                width_y=0.018,
                height_z=0.080,
                radius=0.008,
                name=f"angular_root_cheek_mesh_{suffix}",
                z_tip_shift=-0.004,
            ),
            origin=Origin(xyz=(0.080, y, 0.000)),
            material="steel",
            name=f"contoured_pivot_cheek_{suffix}", material_class_id="metal.steel_bare",
        )
        palm.visual(
            Cylinder(radius=0.019, length=0.024),
            origin=Origin(xyz=(0.108, y, 0.0), rpy=_cyl_y()),
            material="steel",
            name=f"jaw_pivot_boss_{suffix}", material_class_id="metal.steel_bare",
        )
        palm.visual(
            Cylinder(radius=0.0075, length=0.027),
            origin=Origin(xyz=(0.108, y, 0.0), rpy=_cyl_y()),
            material="dark",
            name=f"jaw_pivot_socket_{suffix}", material_class_id="metal.blackened_gunmetal",
        )
    palm.visual(
        Box((0.056, 0.074, 0.006)),
        origin=Origin(xyz=(0.052, 0.0, 0.049)),
        material="accent",
        name="recessed_sensor_cover", material_class_id="plastic.opaque_glossy_molded",
    )
    for y, suffix in ((-0.030, "left"), (0.030, "right")):
        palm.visual(
            Cylinder(radius=0.006, length=0.006),
            origin=Origin(xyz=(0.052, y, 0.053), rpy=_cyl_x()),
            material="steel",
            name=f"sensor_cover_screw_{suffix}", material_class_id="metal.steel_bare",
        )
    model.articulation(
        "gripper_mount",
        ArticulationType.FIXED,
        parent=model.get_part(parent_name),
        child=palm,
        origin=Origin(xyz=parent_tip),
    )
    for i, side in enumerate((-1.0, 1.0)):
        jaw = model.part(f"angular_jaw_{i}")
        jaw.visual(
            Cylinder(radius=0.020, length=0.034),
            origin=Origin(rpy=_cyl_y()),
            material="steel",
            name="pivot_barrel", material_class_id="metal.steel_bare",
        )
        jaw.visual(
            _adaptive_link_mesh(
                model,
                length=0.058,
                width_y=0.020,
                height_z=0.044,
                radius=0.009,
                name=f"angular_jaw_{i}_root_link_mesh",
                z_tip_shift=-0.006,
            ),
            origin=Origin(xyz=(0.010, side * 0.004, 0.0)),
            material="cast",
            name="rounded_root_link", material_class_id="metal.paint_coated",
        )
        jaw.visual(
            _angular_jaw_mesh(model, f"angular_jaw_{i}_white_finger_mesh"),
            origin=Origin(xyz=(0.048, side * 0.014, -0.004)),
            material="steel",
            name="milled_angular_finger", material_class_id="metal.steel_bare",
        )
        jaw.visual(
            _adaptive_link_mesh(
                model,
                length=0.078,
                width_y=0.010,
                height_z=0.030,
                radius=0.0045,
                name=f"angular_jaw_{i}_pad_pocket_mesh",
                z_tip_shift=-0.012,
            ),
            origin=Origin(xyz=(0.070, side * 0.022, -0.008), rpy=(0.0, 0.0, side * -0.03)),
            material="dark",
            name="milled_inner_pad_pocket", material_class_id="metal.blackened_gunmetal",
        )
        jaw.visual(
            _angular_curved_grip_pad_mesh(model, f"angular_jaw_{i}_curved_rubber_insert_mesh"),
            origin=Origin(xyz=(0.071, side * 0.027, -0.007), rpy=(0.0, 0.0, side * -0.03)),
            material="rubber",
            name="curved_flush_rubber_grip_insert", material_class_id="rubber.smooth_plain",
        )
        for z, suffix in ((0.006, "upper"), (-0.027, "lower")):
            jaw.visual(
                _angular_pad_retainer_rail_mesh(
                    model,
                    f"angular_jaw_{i}_curved_retainer_rail_{suffix}_mesh",
                ),
                origin=Origin(xyz=(0.078, side * 0.025, z), rpy=(0.0, 0.0, side * -0.03)),
                material="steel",
                name=f"curved_pad_retainer_rail_{suffix}", material_class_id="metal.steel_bare",
            )
        for x, z, suffix in ((0.078, -0.008, "rear"), (0.146, -0.024, "front")):
            jaw.visual(
                Cylinder(radius=0.0048, length=0.014),
                origin=Origin(xyz=(x, side * 0.030, z), rpy=_cyl_y()),
                material="steel",
                name=f"countersunk_pad_screw_{suffix}", material_class_id="metal.steel_bare",
            )
            jaw.visual(
                Cylinder(radius=0.0019, length=0.016),
                origin=Origin(xyz=(x, side * 0.031, z), rpy=_cyl_y()),
                material="dark",
                name=f"pad_screw_hex_socket_{suffix}", material_class_id="metal.blackened_gunmetal",
            )
        model.articulation(
            f"angular_jaw_{i}_swing",
            ArticulationType.REVOLUTE,
            parent=palm,
            child=jaw,
            origin=Origin(xyz=(0.108, side * 0.050, 0.0), rpy=(0.0, 0.0, side * 0.18)),
            axis=(0.0, 0.0, side),
            motion_limits=MotionLimits(effort=18.0, velocity=1.8, lower=0.0, upper=0.72),
            mimic=None
            if i == 0
            else Mimic(joint="angular_jaw_0_swing", multiplier=1.0, offset=0.0),
        )


def _attach_concentric_3jaw_chuck(
    model: ArticulatedObject,
    r: ResolvedRoboticArmsConfig,
    parent_name: str,
    parent_tip: tuple[float, float, float],
) -> None:
    palm = model.part("gripper_base")
    palm.visual(
        Cylinder(radius=0.057, length=0.038),
        origin=Origin(rpy=_cyl_x()),
        material="steel",
        name="wrist_coupler", material_class_id="metal.steel_bare",
    )
    palm.visual(
        _smooth_cylinder_mesh(
            model, radius=0.073, length=0.074, name="threejaw_chuck_body_round_72"
        ),
        origin=Origin(xyz=(0.054, 0.0, 0.0), rpy=_cyl_x()),
        material="cast",
        name="round_chuck_body", material_class_id="metal.paint_coated",
    )
    palm.visual(
        _smooth_cylinder_mesh(
            model, radius=0.083, length=0.018, name="threejaw_front_scroll_round_72"
        ),
        origin=Origin(xyz=(0.097, 0.0, 0.0), rpy=_cyl_x()),
        material="dark",
        name="front_scroll_plate", material_class_id="metal.blackened_gunmetal",
    )
    palm.visual(
        Cylinder(radius=0.026, length=0.020),
        origin=Origin(xyz=(0.107, 0.0, 0.0), rpy=_cyl_x()),
        material="steel",
        name="central_drive_cap", material_class_id="metal.steel_bare",
    )
    guide_mid_radius = 0.040
    jaw_mount_radius = 0.064
    guide_end_radius = 0.080
    for i in range(3):
        angle = 2.0 * math.pi * i / 3.0
        radial_y = math.cos(angle)
        radial_z = math.sin(angle)
        palm.visual(
            Box((0.020, 0.088, 0.014)),
            origin=Origin(
                xyz=(0.108, guide_mid_radius * radial_y, guide_mid_radius * radial_z),
                rpy=(angle, 0.0, 0.0),
            ),
            material="dark",
            name=f"recessed_radial_slot_{i}", material_class_id="metal.blackened_gunmetal",
        )
        palm.visual(
            Box((0.014, 0.076, 0.006)),
            origin=Origin(
                xyz=(0.116, guide_mid_radius * radial_y, guide_mid_radius * radial_z),
                rpy=(angle, 0.0, 0.0),
            ),
            material="steel",
            name=f"raised_slot_land_{i}", material_class_id="metal.steel_bare",
        )
        palm.visual(
            Cylinder(radius=0.0055, length=0.008),
            origin=Origin(
                xyz=(0.116, guide_end_radius * radial_y, guide_end_radius * radial_z),
                rpy=_cyl_x(),
            ),
            material="steel",
            name=f"slot_end_screw_{i}", material_class_id="metal.steel_bare",
        )
    model.articulation(
        "gripper_mount",
        ArticulationType.FIXED,
        parent=model.get_part(parent_name),
        child=palm,
        origin=Origin(xyz=parent_tip),
    )
    for i in range(3):
        angle = 2.0 * math.pi * i / 3.0
        radial_y = math.cos(angle)
        radial_z = math.sin(angle)
        jaw_y = jaw_mount_radius * radial_y
        jaw_z = jaw_mount_radius * radial_z
        jaw = model.part(f"chuck_jaw_{i}")
        jaw.visual(
            Box((0.052, 0.028, 0.024)),
            origin=Origin(xyz=(0.026, 0.0, 0.0)),
            material="steel",
            name="radial_slide_shoe", material_class_id="metal.steel_bare",
        )
        jaw.visual(
            _chuck_jaw_mesh(model, f"chuck_jaw_{i}_stepped_mesh"),
            origin=Origin(xyz=(0.044, 0.0, -0.004)),
            material="cast",
            name="milled_stepped_hard_jaw", material_class_id="metal.paint_coated",
        )
        jaw.visual(
            _adaptive_link_mesh(
                model,
                length=0.066,
                width_y=0.020,
                height_z=0.014,
                radius=0.005,
                name=f"chuck_jaw_{i}_pad_pocket_mesh",
                z_tip_shift=-0.004,
            ),
            origin=Origin(xyz=(0.072, 0.0, 0.014)),
            material="dark",
            name="milled_grip_insert_pocket", material_class_id="metal.blackened_gunmetal",
        )
        jaw.visual(
            _chuck_grip_insert_mesh(model, f"chuck_jaw_{i}_rubber_insert_mesh"),
            origin=Origin(xyz=(0.076, 0.0, 0.018)),
            material="rubber",
            name="flush_grip_insert", material_class_id="rubber.smooth_plain",
        )
        for rail_y, suffix in ((-0.010, "left"), (0.010, "right")):
            jaw.visual(
                _chuck_insert_retainer_rail_mesh(
                    model,
                    f"chuck_jaw_{i}_curved_insert_retainer_rail_{suffix}_mesh",
                ),
                origin=Origin(xyz=(0.080, rail_y, 0.023)),
                material="steel",
                name=f"curved_insert_retainer_rail_{suffix}", material_class_id="metal.steel_bare",
            )
        for x, screw_z, suffix in ((0.082, 0.023, "rear"), (0.116, 0.020, "front")):
            jaw.visual(
                Cylinder(radius=0.0048, length=0.018),
                origin=Origin(xyz=(x, 0.0, screw_z), rpy=_cyl_y()),
                material="steel",
                name=f"insert_countersunk_screw_{suffix}", material_class_id="metal.steel_bare",
            )
            jaw.visual(
                Cylinder(radius=0.0019, length=0.020),
                origin=Origin(xyz=(x, 0.0, screw_z + 0.001), rpy=_cyl_y()),
                material="dark",
                name=f"insert_hex_socket_{suffix}", material_class_id="metal.blackened_gunmetal",
            )
        model.articulation(
            f"chuck_jaw_{i}_slide",
            ArticulationType.PRISMATIC,
            parent=palm,
            child=jaw,
            origin=Origin(xyz=(0.111, jaw_y, jaw_z), rpy=(angle, 0.0, 0.0)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=_limits(r, "finger_slide", effort=16.0, velocity=0.08),
        )


def _attach_adaptive_2finger_gripper(
    model: ArticulatedObject,
    r: ResolvedRoboticArmsConfig,
    parent_name: str,
    parent_tip: tuple[float, float, float],
) -> None:
    palm = model.part("gripper_base")
    palm.visual(
        Cylinder(radius=0.060, length=0.040),
        origin=Origin(rpy=_cyl_x()),
        material="steel",
        name="wrist_coupler", material_class_id="metal.steel_bare",
    )
    palm.visual(
        _adaptive_drive_shell_mesh(model),
        origin=Origin(),
        material="dark",
        name="rounded_motor_housing", material_class_id="metal.blackened_gunmetal",
    )
    palm.visual(
        Cylinder(radius=0.048, length=0.072),
        origin=Origin(xyz=(0.045, 0.0, 0.050), rpy=_cyl_x()),
        material="dark",
        name="compact_top_drive_cap", material_class_id="metal.blackened_gunmetal",
    )
    palm.visual(
        Box((0.020, 0.126, 0.078)),
        origin=Origin(xyz=(0.120, 0.0, -0.010)),
        material="dark",
        name="front_clevis_backplate", material_class_id="metal.blackened_gunmetal",
    )
    palm.visual(
        Box((0.060, 0.080, 0.012)),
        origin=Origin(xyz=(0.078, 0.0, -0.055)),
        material="steel",
        name="lower_drive_cover", material_class_id="metal.steel_bare",
    )
    palm.visual(
        Box((0.050, 0.068, 0.006)),
        origin=Origin(xyz=(0.072, 0.0, 0.020)),
        material="steel",
        name="recessed_brand_plate", material_class_id="metal.steel_bare",
    )
    palm.visual(
        Box((0.030, 0.038, 0.003)),
        origin=Origin(xyz=(0.073, -0.014, 0.024)),
        material="dark",
        name="brand_dark_mark", material_class_id="metal.blackened_gunmetal",
    )
    palm.visual(
        Box((0.030, 0.014, 0.003)),
        origin=Origin(xyz=(0.073, 0.022, 0.024)),
        material="accent",
        name="badge_signal_mark", material_class_id="plastic.opaque_glossy_molded",
    )
    for x, y, suffix in (
        (0.044, -0.038, "left_upper"),
        (0.044, 0.038, "right_upper"),
        (0.100, -0.030, "left_lower"),
        (0.100, 0.030, "right_lower"),
    ):
        palm.visual(
            Cylinder(radius=0.0065, length=0.006),
            origin=Origin(xyz=(x, y, 0.024), rpy=_cyl_x()),
            material="steel",
            name=f"face_screw_{suffix}", material_class_id="metal.steel_bare",
        )
    for y, suffix in ((-0.055, "left"), (0.055, "right")):
        palm.visual(
            _adaptive_link_mesh(
                model,
                length=0.056,
                width_y=0.026,
                height_z=0.072,
                radius=0.010,
                name=f"adaptive_root_dark_side_cover_{suffix}",
                z_tip_shift=-0.004,
            ),
            origin=Origin(xyz=(0.084, y, -0.012), rpy=(0.0, 0.0, 0.0)),
            material="dark",
            name=f"rounded_outer_root_cover_{suffix}", material_class_id="metal.blackened_gunmetal",
        )
        palm.visual(
            _adaptive_link_mesh(
                model,
                length=0.070,
                width_y=0.018,
                height_z=0.056,
                radius=0.009,
                name=f"adaptive_root_steel_yoke_plate_{suffix}",
                z_tip_shift=-0.008,
            ),
            origin=Origin(xyz=(0.076, y, -0.022), rpy=(0.0, 0.0, 0.0)),
            material="steel",
            name=f"contoured_root_yoke_plate_{suffix}", material_class_id="metal.steel_bare",
        )
        palm.visual(
            Cylinder(radius=0.019, length=0.032),
            origin=Origin(xyz=(0.124, y, 0.006), rpy=_cyl_y()),
            material="steel",
            name=f"main_root_pivot_boss_{suffix}", material_class_id="metal.steel_bare",
        )
        palm.visual(
            Cylinder(radius=0.008, length=0.036),
            origin=Origin(xyz=(0.124, y, 0.006), rpy=_cyl_y()),
            material="dark",
            name=f"main_root_pivot_socket_{suffix}", material_class_id="metal.blackened_gunmetal",
        )
        palm.visual(
            Cylinder(radius=0.014, length=0.028),
            origin=Origin(xyz=(0.078, y * 0.90, -0.036), rpy=_cyl_y()),
            material="steel",
            name=f"rear_fourbar_pivot_{suffix}", material_class_id="metal.steel_bare",
        )
        palm.visual(
            Cylinder(radius=0.0065, length=0.032),
            origin=Origin(xyz=(0.078, y * 0.90, -0.036), rpy=_cyl_y()),
            material="dark",
            name=f"rear_fourbar_socket_{suffix}", material_class_id="metal.blackened_gunmetal",
        )
        palm.visual(
            Box((0.040, 0.014, 0.016)),
            origin=Origin(xyz=(0.112, y, -0.050)),
            material="steel",
            name=f"silver_lower_clevis_bridge_{suffix}", material_class_id="metal.steel_bare",
        )
    model.articulation(
        "gripper_mount",
        ArticulationType.FIXED,
        parent=model.get_part(parent_name),
        child=palm,
        origin=Origin(xyz=parent_tip),
    )
    for i, side in enumerate((-1.0, 1.0)):
        proximal_name = f"adaptive_finger_{i}_proximal"
        distal_name = f"adaptive_finger_{i}_distal"
        proximal = model.part(proximal_name)
        proximal.visual(
            Cylinder(radius=0.021, length=0.034),
            origin=Origin(rpy=_cyl_y()),
            material="steel",
            name="root_knuckle_barrel", material_class_id="metal.steel_bare",
        )
        proximal.visual(
            _adaptive_link_mesh(
                model,
                length=0.104,
                width_y=0.018,
                height_z=0.030,
                radius=0.008,
                name=f"adaptive_finger_{i}_upper_parallel_link_mesh",
                z_tip_shift=-0.006,
            ),
            origin=Origin(xyz=(0.010, side * 0.009, 0.014), rpy=(0.0, 0.0, side * -0.05)),
            material="dark",
            name="upper_rounded_parallel_link", material_class_id="metal.blackened_gunmetal",
        )
        proximal.visual(
            _adaptive_link_mesh(
                model,
                length=0.100,
                width_y=0.016,
                height_z=0.026,
                radius=0.007,
                name=f"adaptive_finger_{i}_lower_parallel_link_mesh",
                z_tip_shift=0.004,
            ),
            origin=Origin(xyz=(0.014, side * -0.010, -0.020), rpy=(0.0, 0.0, side * -0.02)),
            material="dark",
            name="lower_rounded_parallel_link", material_class_id="metal.blackened_gunmetal",
        )
        proximal.visual(
            Cylinder(radius=0.016, length=0.030),
            origin=Origin(xyz=(0.104, side * 0.000, -0.004), rpy=_cyl_y()),
            material="steel",
            name="distal_knuckle_socket", material_class_id="metal.steel_bare",
        )
        proximal.visual(
            Cylinder(radius=0.010, length=0.026),
            origin=Origin(xyz=(0.018, side * 0.009, 0.014), rpy=_cyl_y()),
            material="steel",
            name="root_link_washer", material_class_id="metal.steel_bare",
        )
        proximal.visual(
            Cylinder(radius=0.007, length=0.024),
            origin=Origin(xyz=(0.104, side * 0.000, -0.004), rpy=_cyl_y()),
            material="steel",
            name="distal_link_pin", material_class_id="metal.steel_bare",
        )
        model.articulation(
            f"adaptive_finger_{i}_root",
            ArticulationType.REVOLUTE,
            parent=palm,
            child=proximal,
            origin=Origin(xyz=(0.124, side * 0.055, 0.006), rpy=(0.0, 0.0, side * 0.10)),
            axis=(0.0, 0.0, side),
            motion_limits=MotionLimits(effort=10.0, velocity=1.4, lower=0.0, upper=0.95),
            mimic=None
            if i == 0
            else Mimic(joint="adaptive_finger_0_root", multiplier=1.0, offset=0.0),
        )

        distal = model.part(distal_name)
        distal.visual(
            Cylinder(radius=0.016, length=0.032),
            origin=Origin(rpy=_cyl_y()),
            material="steel",
            name="distal_hinge_barrel", material_class_id="metal.steel_bare",
        )
        distal.visual(
            _adaptive_jaw_mesh(model),
            origin=Origin(xyz=(0.010, 0.0, -0.032), rpy=(0.0, 0.0, 0.0)),
            material="steel",
            name="milled_silver_lower_jaw", material_class_id="metal.steel_bare",
        )
        distal.visual(
            Box((0.086, 0.006, 0.032)),
            origin=Origin(xyz=(0.070, -side * 0.018, -0.035)),
            material="dark",
            name="machined_pad_pocket", material_class_id="metal.blackened_gunmetal",
        )
        distal.visual(
            _adaptive_grip_pad_mesh(model, f"adaptive_finger_{i}_rubber_pad_mesh"),
            origin=Origin(xyz=(0.030, -side * 0.021, -0.035)),
            material="rubber",
            name="inner_soft_grip_pad", material_class_id="rubber.smooth_plain",
        )
        for dz, suffix in ((0.016, "upper"), (-0.016, "lower")):
            distal.visual(
                Box((0.074, 0.008, 0.006)),
                origin=Origin(xyz=(0.074, -side * 0.023, -0.035 + dz)),
                material="steel",
                name=f"pad_retainer_rail_{suffix}", material_class_id="metal.steel_bare",
            )
        distal.visual(
            Cylinder(radius=0.009, length=0.026),
            origin=Origin(xyz=(0.020, 0.0, -0.010), rpy=_cyl_y()),
            material="steel",
            name="jaw_root_washer", material_class_id="metal.steel_bare",
        )
        for x, z, suffix in ((0.045, -0.019, "rear"), (0.103, -0.051, "front")):
            distal.visual(
                Cylinder(radius=0.0068, length=0.018),
                origin=Origin(xyz=(x, -side * 0.024, z), rpy=_cyl_y()),
                material="steel",
                name=f"countersunk_pad_screw_{suffix}", material_class_id="metal.steel_bare",
            )
            distal.visual(
                Cylinder(radius=0.0028, length=0.020),
                origin=Origin(xyz=(x, -side * 0.025, z), rpy=_cyl_y()),
                material="dark",
                name=f"hex_socket_{suffix}", material_class_id="metal.blackened_gunmetal",
            )
        model.articulation(
            f"adaptive_finger_{i}_distal_curl",
            ArticulationType.REVOLUTE,
            parent=proximal,
            child=distal,
            origin=Origin(xyz=(0.104, 0.0, -0.004), rpy=(0.0, 0.0, side * 0.05)),
            axis=(0.0, 0.0, side),
            motion_limits=MotionLimits(effort=5.0, velocity=1.6, lower=0.0, upper=1.05),
            mimic=Mimic(joint=f"adaptive_finger_{i}_root", multiplier=0.72, offset=0.0),
        )


def _attach_parallel_gripper(
    model: ArticulatedObject,
    r: ResolvedRoboticArmsConfig,
    parent_name: str,
    parent_tip: tuple[float, float, float],
) -> None:
    if r.gripper_module == "angular_2jaw":
        _attach_angular_2jaw_gripper(model, r, parent_name, parent_tip)
    elif r.gripper_module == "concentric_3jaw_chuck":
        _attach_concentric_3jaw_chuck(model, r, parent_name, parent_tip)
    elif r.gripper_module == "adaptive_2finger":
        _attach_adaptive_2finger_gripper(model, r, parent_name, parent_tip)
    else:
        _attach_parallel_slide_gripper(model, r, parent_name, parent_tip)


def _attach_dexterous_hand(
    model: ArticulatedObject,
    r: ResolvedRoboticArmsConfig,
    parent_name: str,
    parent_tip: tuple[float, float, float],
) -> None:
    palm = model.part("palm")
    palm.visual(
        Cylinder(radius=0.058, length=0.045),
        origin=Origin(rpy=_cyl_x()),
        material="steel",
        name="wrist_socket", material_class_id="metal.steel_bare",
    )
    palm.visual(
        _dexterous_palm_shell_mesh(model),
        origin=Origin(),
        material="cast",
        name="palm_shell", material_class_id="metal.paint_coated",
    )
    palm.visual(
        _dexterous_wrist_cover_mesh(model),
        origin=Origin(xyz=(0.020, 0.0, -0.046)),
        material="dark",
        name="wrist_access_cover", material_class_id="metal.blackened_gunmetal",
    )
    palm.visual(
        _dexterous_dorsal_cover_mesh(model),
        origin=Origin(xyz=(0.072, 0.0, 0.072)),
        material="dark",
        name="dorsal_service_cover", material_class_id="metal.blackened_gunmetal",
    )
    palm.visual(
        Box((0.060, 0.012, 0.004)),
        origin=Origin(xyz=(0.077, 0.0, 0.077)),
        material="steel",
        name="dorsal_cover_center_rib", material_class_id="metal.steel_bare",
    )
    for x, y, suffix in (
        (0.040, -0.055, "rear_neg"),
        (0.040, 0.055, "rear_pos"),
        (0.105, -0.050, "front_neg"),
        (0.105, 0.050, "front_pos"),
    ):
        palm.visual(
            Cylinder(radius=0.0045, length=0.006),
            origin=Origin(xyz=(x, y, 0.077)),
            material="steel",
            name=f"dorsal_cover_screw_{suffix}", material_class_id="metal.steel_bare",
        )
    for y, z, suffix in (
        (-0.055, -0.058, "lower_neg"),
        (0.055, -0.058, "lower_pos"),
        (-0.055, -0.034, "upper_neg"),
        (0.055, -0.034, "upper_pos"),
    ):
        palm.visual(
            Cylinder(radius=0.004, length=0.004),
            origin=Origin(xyz=(0.028, y, z), rpy=_cyl_x()),
            material="steel",
            name=f"wrist_cover_screw_{suffix}", material_class_id="metal.steel_bare",
        )
    palm.visual(
        Box((0.022, 0.190, 0.056)),
        origin=Origin(xyz=(0.125, 0.0, 0.033)),
        material="accent",
        name="knuckle_bar", material_class_id="metal.paint_coated",
    )
    for y, suffix in (
        (-0.078, "outer"),
        (-0.026, "inner_a"),
        (0.026, "inner_b"),
        (0.078, "outer_b"),
    ):
        palm.visual(
            Cylinder(radius=0.014, length=0.018),
            origin=Origin(xyz=(0.131, y, 0.062), rpy=_cyl_x()),
            material="steel",
            name=f"knuckle_cap_{suffix}", material_class_id="metal.steel_bare",
        )
    palm.visual(
        Box((0.055, 0.050, 0.046)),
        origin=Origin(xyz=(0.095, -0.106, 0.000), rpy=(0.0, 0.0, -0.42)),
        material="steel",
        name="thumb_saddle", material_class_id="metal.steel_bare",
    )
    palm.visual(
        Cylinder(radius=0.022, length=0.038),
        origin=Origin(xyz=(0.098, -0.100, 0.002), rpy=(0.0, math.pi / 2.0, -0.42)),
        material="dark",
        name="thumb_opposition_motor", material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        "hand_mount",
        ArticulationType.FIXED,
        parent=model.get_part(parent_name),
        child=palm,
        origin=Origin(xyz=parent_tip),
    )
    finger_specs = [
        ((0.135, -0.070, 0.041), (0.0, 0.0, 0.0), False, 0.94),
        ((0.136, -0.024, 0.052), (0.0, 0.0, 0.0), False, 1.06),
        ((0.136, 0.024, 0.052), (0.0, 0.0, 0.0), False, 1.04),
        ((0.135, 0.070, 0.041), (0.0, 0.0, 0.0), False, 0.90),
        ((0.098, -0.115, 0.004), (0.0, 0.0, -0.82), True, 0.82),
    ]
    for i, (root_xyz, _root_rpy, is_thumb, scale) in enumerate(finger_specs):
        # Tuck the thumb carpal block inboard (toward the palm centre) so it
        # sits behind the thumb pivot instead of under the swing path of the
        # proximal/middle knuckle.
        block_xyz = (
            (root_xyz[0] - 0.012, root_xyz[1] + 0.010, root_xyz[2]) if is_thumb else root_xyz
        )
        palm.visual(
            Box((0.040, 0.042, 0.040) if is_thumb else (0.038, 0.040, 0.038)),
            origin=Origin(
                xyz=block_xyz,
                rpy=(0.0, 0.0, -0.44) if is_thumb else (0.0, 0.0, 0.0),
            ),
            material="steel",
            name="thumb_carpal_block" if is_thumb else f"finger_socket_{i}", material_class_id="metal.steel_bare",
        )
    for i, (root_xyz, root_rpy, is_thumb, scale) in enumerate(finger_specs):
        parent = "palm"
        origin = root_xyz
        segment_specs = (
            (
                ("proximal", 0.058 * scale, 0.019),
                ("middle", 0.040 * scale, 0.016),
                ("distal", 0.034 * scale, 0.014),
            )
            if is_thumb
            else (
                ("proximal", 0.062 * scale, 0.020),
                ("middle", 0.048 * scale, 0.017),
                ("distal", 0.038 * scale, 0.014),
            )
        )
        for seg, length, height in segment_specs:
            name = f"finger_{i}_{seg}"
            part = model.part(name)
            width = (0.025 if is_thumb else 0.022) * (0.92 if seg == "distal" else 1.0)
            part.visual(
                Cylinder(radius=height * 0.72, length=width + 0.006),
                origin=Origin(rpy=_cyl_y()),
                material="steel",
                name=f"{seg}_hinge_barrel", material_class_id="metal.steel_bare",
            )
            part.visual(
                Box((length * 0.86, width, height * 0.88)),
                origin=Origin(xyz=(length * 0.46, 0.0, 0.0)),
                material="steel",
                name=f"{seg}_center_bone", material_class_id="metal.steel_bare",
            )
            part.visual(
                Box((length * 0.74, 0.0045, height * 1.40)),
                origin=Origin(xyz=(length * 0.44, width * 0.43, 0.0)),
                material="cast",
                name=f"{seg}_side_plate_pos", material_class_id="metal.paint_coated",
            )
            part.visual(
                Box((length * 0.74, 0.0045, height * 1.40)),
                origin=Origin(xyz=(length * 0.44, -width * 0.43, 0.0)),
                material="cast",
                name=f"{seg}_side_plate_neg", material_class_id="metal.paint_coated",
            )
            part.visual(
                Cylinder(radius=height * 0.55, length=width * 0.86),
                origin=Origin(xyz=(length, 0.0, 0.0), rpy=_cyl_y()),
                material="steel",
                name=f"{seg}_distal_pin", material_class_id="metal.steel_bare",
            )
            if seg == "distal":
                part.visual(
                    Box((length * 0.30, width * 1.10, height * 1.18)),
                    origin=Origin(xyz=(length * 0.86, 0.0, -height * 0.08)),
                    material="rubber",
                    name=f"{seg}_replaceable_pad", material_class_id="rubber.smooth_plain",
                )
            else:
                part.visual(
                    Box((length * 0.34, width * 0.62, height * 0.38)),
                    origin=Origin(xyz=(length * 0.62, 0.0, height * 0.58)),
                    material="accent",
                    name=f"{seg}_tendon_cover", material_class_id="plastic.opaque_glossy_molded",
                )
            model.articulation(
                f"finger_{i}_{seg}_curl",
                ArticulationType.REVOLUTE,
                parent=model.get_part(parent),
                child=part,
                origin=Origin(
                    xyz=origin,
                    rpy=root_rpy if parent == "palm" else (0.0, 0.0, 0.0),
                ),
                axis=(0.0, 0.0, 1.0) if is_thumb and parent == "palm" else (0.0, -1.0, 0.0),
                motion_limits=MotionLimits(effort=2.0, velocity=2.2, lower=0.0, upper=1.25),
            )
            parent = name
            origin = (length, 0.0, 0.0)


def _build_end_effector(
    model: ArticulatedObject,
    r: ResolvedRoboticArmsConfig,
    parent_name: str,
    parent_tip: tuple[float, float, float],
) -> None:
    if r.end_effector_module == "fixed_flange":
        _attach_fixed_flange(model, r, parent_name, parent_tip)
    elif r.end_effector_module == "roll_flange":
        _attach_roll_flange(model, r, parent_name, parent_tip)
    elif r.end_effector_module == "parallel_gripper":
        _attach_parallel_gripper(model, r, parent_name, parent_tip)
    else:
        _attach_dexterous_hand(model, r, parent_name, parent_tip)


_WRIST_SEGMENT_PARTS = ("wrist_yaw", "wrist_pitch", "wrist_roll", "tool_roll")
_TOOL_ROOT_PARTS = ("tool_flange", "roll_flange", "gripper_base", "palm")
_ARM_CHAIN_CAPTURES = (
    ("base", "shoulder_root"),
    ("shoulder_root", "upper_arm"),
    ("upper_arm", "forearm"),
    ("forearm", "wrist_yaw"),
    ("forearm", "wrist_pitch"),
    ("forearm", "wrist_roll"),
)


def _captured_interface_pairs(model: ArticulatedObject) -> list[tuple[str, str]]:
    """Mechanically captured/nested interfaces whose overlap is legitimate.

    Single source (Contract 3c) for BOTH the rest-pose test ``allow_overlap``
    set and the clearance-solver clamp. The wrist segments and the tool mount
    form one compact telescoping stack (each output hub seats into the next
    input hub) so they may self-overlap; but NONE of them is paired with the
    forearm or upper arm, so folding the tool/flange back onto the arm proper
    stays a genuine collision the solver clamps against.
    """
    names = {part.name for part in model.parts}
    pairs: list[tuple[str, str]] = []
    for a, b in _ARM_CHAIN_CAPTURES:
        if a in names and b in names:
            pairs.append((a, b))
    cluster = [p for p in (*_WRIST_SEGMENT_PARTS, *_TOOL_ROOT_PARTS) if p in names]
    pairs.extend(itertools.combinations(cluster, 2))
    return pairs


_CLAMP_MARGIN = 0.010
_THUMB_CLAMP_MARGIN = 0.004
# These local folds (thumb-into-palm, wrist-into-forearm, hand-into-base) are
# monotonic in the swept joint, so a coarse scan + short bisection brackets the
# boundary cheaply — important because the FCL query runs over a many-mesh
# dexterous hand and the whole build must clear the 60 s medium-stage budget.
_DEFAULT_CLAMP_SCAN = 6
_DEFAULT_CLAMP_BISECT = 6


def _scan_safe_limit(
    probe: ClearanceProbe,
    joint: str,
    base_pose: dict[str, float],
    limit: float,
    margin: float,
    scan_steps: int,
    bisect_iters: int,
) -> float:
    """Furthest value in ``[0, limit]`` keeping the probe's clearance >= margin.

    Mirrors ``sdk.max_joint_value`` (coarse scan to bracket the first violation,
    then bisection) but against an ALREADY-COMPILED probe, so no per-call model
    recompile. These folds all move monotonically toward the obstacle, so an
    endpoint pre-check short-circuits the (common) corner poses that stay clear
    across the whole travel — 2 queries instead of a full scan.
    """
    pose = dict(base_pose)

    def safe(value: float) -> bool:
        pose[joint] = value
        return probe.min_clearance(pose) >= margin

    if limit == 0.0 or not safe(0.0):
        return 0.0
    if safe(limit):
        return limit
    last_safe = 0.0
    first_bad: float | None = None
    for step in range(1, scan_steps + 1):
        value = limit * step / scan_steps
        if safe(value):
            last_safe = value
        else:
            first_bad = value
            break
    if first_bad is None:
        return limit
    lo, hi = last_safe, first_bad
    for _ in range(bisect_iters):
        mid = (lo + hi) / 2.0
        if safe(mid):
            lo = mid
        else:
            hi = mid
    return lo


def _corner_base_poses(model: ArticulatedObject, other_joints: list[str]) -> list[dict[str, float]]:
    """Rest pose plus every sign-combination of the other joints' extremes."""
    extremes: list[list[tuple[str, float]]] = []
    for other in other_joints:
        limits = model.get_articulation(other).motion_limits
        extremes.append([(other, float(limits.lower)), (other, float(limits.upper))])
    poses: list[dict[str, float]] = [{}]
    for combo in itertools.product(*extremes):
        poses.append({name: value for name, value in combo})
    return poses


def _corner_clamp(
    model: ArticulatedObject,
    joint: str,
    other_joints: list[str],
    allowed: list[tuple[str, str]],
    *,
    margin: float = _CLAMP_MARGIN,
    park: dict[str, float] | None = None,
    keepout: list[str] | None = None,
    scan_steps: int = _DEFAULT_CLAMP_SCAN,
    bisect_iters: int = _DEFAULT_CLAMP_BISECT,
) -> None:
    """Tighten ``joint`` so it stays clear across the worst-case corner of the
    other fold joints (each held at its already-realized extremes). When
    ``park`` is given, every corner is also tested with that fixed pose merged
    in (e.g. a fisted hand). ``keepout`` restricts the collision set to a few
    named parts so the query stays cheap (the fold is local — a thumb only meets
    the palm, a wrist only its own forearm)."""
    limits = model.get_articulation(joint).motion_limits
    lower = float(limits.lower)
    upper = float(limits.upper)
    probe = ClearanceProbe(model, joint_name=joint, keepout=keepout, allowed_pairs=allowed)
    park_variants: list[dict[str, float]] = [{}] if not park else [{}, park]
    for base_pose in _corner_base_poses(model, other_joints):
        for variant in park_variants:
            pose = {**base_pose, **variant}
            lower = max(
                lower,
                _scan_safe_limit(
                    probe, joint, pose, float(limits.lower), margin, scan_steps, bisect_iters
                ),
            )
            upper = min(
                upper,
                _scan_safe_limit(
                    probe, joint, pose, float(limits.upper), margin, scan_steps, bisect_iters
                ),
            )
    model.get_articulation(joint).motion_limits = MotionLimits(
        effort=limits.effort,
        velocity=limits.velocity,
        lower=lower,
        upper=upper,
    )


# --- Closed-form distal-fold budget (Contract 3c single-source) ----------------
#
# A serial arm curls its (fisted) end effector back through its own upper arm /
# shoulder / base as the same-direction pitch fold accumulates. The motion-QC
# sampler drives every joint INDEPENDENTLY, so the worst cumulative in-plane fold
# it can command is elbow.|limit| + wrist_pitch.|limit| (both held at the same-
# sign extreme); an intermediate value only folds LESS. Capping that sum below
# the fold at which the fisted hand re-enters the arm therefore covers every pose
# combination in a single cheap geometric bound — no per-pose FCL sweep (which is
# both leaky, because the worst collision sits at an intermediate value of the
# OTHER joints rather than their sampled corner extremes, and far too slow: the
# corner solver blew the compile budget on 20-joint dexterous hands).
#
# The budget below is calibrated from the FCL clearance break (>=8 mm) over every
# module combination: the bulkiest dexterous hands re-enter the upper arm at a
# cumulative fold of ~3.3 rad, and every end effector — the bulky hands AND the
# short coaxial flange plates, which the wrist can still swing back onto the beam
# — folds onto its OWN forearm (elbow straight) at |wrist_pitch| ~1.15 rad when
# the pitch pivot sits at the wrist output (roll_pitch / spherical) or ~2.3 rad
# when it sits at the wrist input (pitch_roll). Each cap sits a safe angular
# margin below its measured break, so the realized poses stay well clear of the
# 5 mm motion-QC penetration tolerance.


def _distal_fold_budget(r: ResolvedRoboticArmsConfig) -> float:
    """Max same-direction (elbow + wrist_pitch) fold before the end effector
    curls back into the upper arm / shoulder / base envelope."""
    return 2.85


def _wrist_bend_forearm_cap(r: ResolvedRoboticArmsConfig) -> float:
    """Max |wrist bend| before the end effector folds onto its OWN forearm with
    the elbow straight (independent of the cumulative budget). A short flange
    reaches the forearm later than a bulky hand, so the hand-calibrated caps are
    conservative for it."""
    if r.wrist_module == "wrist_3dof_spherical":
        # Pitch AND yaw both bend the same distal tool segment back onto the
        # forearm, so they COMPOUND; each must stay small enough that the pair
        # combined clears (measured self-fold break ~0.65 rad on the bulkiest
        # combos).
        return 0.60
    if r.wrist_module == "wrist_2dof_roll_pitch":
        return 0.95  # pitch pivot at the wrist output -> folds in early (~1.15)
    return 2.00  # pitch_roll: pivot at the wrist input -> longer lever (~2.3)


def _set_joint_limits(
    model: ArticulatedObject,
    joint: str,
    *,
    lower: float | None = None,
    upper: float | None = None,
) -> None:
    lim = model.get_articulation(joint).motion_limits
    model.get_articulation(joint).motion_limits = MotionLimits(
        effort=lim.effort,
        velocity=lim.velocity,
        lower=lim.lower if lower is None else lower,
        upper=lim.upper if upper is None else upper,
    )


def _apply_distal_fold_budget(model: ArticulatedObject, r: ResolvedRoboticArmsConfig) -> None:
    joint_names = {joint.name for joint in model.articulations}
    if "elbow_pitch" not in joint_names:
        return
    budget = _distal_fold_budget(r)
    forearm_cap = _wrist_bend_forearm_cap(r)
    elbow = model.get_articulation("elbow_pitch").motion_limits
    # Elbow keeps the lion's share of the budget (primary reach DOF); the wrist
    # bends take the remainder, further clipped so they cannot fold onto the
    # forearm on their own.
    elbow_up = min(float(elbow.upper), budget * 0.65)
    elbow_lo = max(float(elbow.lower), -budget * 0.65)
    _set_joint_limits(model, "elbow_pitch", lower=elbow_lo, upper=elbow_up)

    if "wrist_pitch" in joint_names:
        wp = model.get_articulation("wrist_pitch").motion_limits
        _set_joint_limits(
            model,
            "wrist_pitch",
            lower=max(float(wp.lower), -(budget + elbow_lo), -forearm_cap),
            upper=min(float(wp.upper), budget - elbow_up, forearm_cap),
        )
    if "wrist_yaw" in joint_names:
        # Out-of-plane bend: it does not add to the in-plane reach-back budget,
        # but combined with roll it can still fold the fist onto the forearm, so
        # it takes the same forearm cap.
        wy = model.get_articulation("wrist_yaw").motion_limits
        _set_joint_limits(
            model,
            "wrist_yaw",
            lower=max(float(wy.lower), -forearm_cap),
            upper=min(float(wy.upper), forearm_cap),
        )


# The base's floor plate / pedestal / turret — the only geometry the arm can fold
# DOWN onto. Kept to this tiny set so each backstop distance query is an order of
# magnitude cheaper than a whole-arm sweep.
_BASE_KEEPOUT = ("base", "shoulder_root")
# The motion-QC gate flags penetration deeper than 5 mm, so a 4 mm keep-clear is
# ample; the arm-fold margin (10 mm) would needlessly amputate downward reach.
_BASE_CLAMP_MARGIN = 0.004


def _finger_pose(model: ArticulatedObject, fraction: float) -> dict[str, float]:
    """Every finger/jaw actuator at ``fraction`` of its closure travel.

    Sweeping the fraction over the values the pose sampler visits (0, mid, full)
    matters because the fingertip that dips LOWEST toward the base is often a
    partly-curled finger, not a full fist; a base contact is one finger vs the
    base, so an all-fingers-at-``fraction`` pose covers every single-finger case
    at that curl.
    """
    pose: dict[str, float] = {}
    for articulation in model.articulations:
        if getattr(articulation, "mimic", None) is not None:
            continue
        if articulation.name.endswith(("_curl", "_swing", "_slide", "_root")):
            limits = getattr(articulation, "motion_limits", None)
            if limits is not None:
                pose[articulation.name] = fraction * float(limits.upper)
    return pose


def _clamp_fold_into_base(model: ArticulatedObject) -> None:
    """Cap the DOWNWARD elbow fold so the fisted hand cannot descend onto the base
    pedestal/floor. This is the one fold the closed-form distal budget cannot
    reason about (it curls toward the ground, not back along the arm's own tube),
    and it depends on the fixed base geometry and the base-yaw sector.

    The shoulder cannot pitch below horizontal (its lower bound is 0), so the arm
    is lowest at shoulder=0 and the hand only reaches the base by folding the
    elbow negative; folding further only descends further, so the worst case is
    bracketed by a small product of corner poses (fist closed, wrist bends/rolls
    at their limits, base yaw at each sampled sector) rather than a leaky
    intermediate sweep. Keep-out is just the base parts, so the whole clamp costs
    a handful of cheap queries.
    """
    joint_names = {joint.name for joint in model.articulations}
    if "elbow_pitch" not in joint_names:
        return
    part_names = {part.name for part in model.parts}
    keepout = [name for name in _BASE_KEEPOUT if name in part_names]
    if not keepout:
        return
    allowed = _captured_interface_pairs(model)
    # The in-plane wrist pitch and the hand orientation (roll) fold the hand
    # toward the base; the out-of-plane yaw does not, so hold it at 0. Base yaw is
    # swept over the values the pose sampler actually visits (0 and +/-pi), and
    # the finger closure over {open, mid, full}.
    axes: list[list[tuple[str, float]]] = []
    if "wrist_pitch" in joint_names:
        wp = model.get_articulation("wrist_pitch").motion_limits
        axes.append([("wrist_pitch", float(wp.lower)), ("wrist_pitch", float(wp.upper))])
    for rj in ("wrist_roll", "tool_roll"):
        if rj in joint_names:
            axes.append([(rj, 0.0), (rj, math.pi)])
    # Only the carriage base's rectangular datum plate is non-axisymmetric, so it
    # is the only one whose base-yaw sector changes the clearance; round pedestals
    # need no yaw sweep.
    if "base_yaw" in joint_names and "datum_floor_plate" in part_names:
        axes.append([("base_yaw", 0.0), ("base_yaw", math.pi)])

    # A dexterous finger CURLS, so a mid-curled tip can dip toward the base at a
    # pose neither closure extreme covers — it needs the mid fraction. Gripper
    # jaws only slide/swing, so their two extremes bracket the reach.
    fractions = (0.0, 0.5, 1.0) if "palm" in part_names else (0.0, 1.0)
    finger_poses = [_finger_pose(model, frac) for frac in fractions]
    elbow_limits = model.get_articulation("elbow_pitch").motion_limits
    probe = ClearanceProbe(
        model,
        joint_name="elbow_pitch",
        keepout=keepout,
        allowed_pairs=allowed,
    )
    lower = float(elbow_limits.lower)
    for fingers in finger_poses:
        for combo in itertools.product(*axes) if axes else [()]:
            pose = dict(fingers)
            pose["shoulder_pitch"] = 0.0  # arm horizontal: lowest, worst vs base
            if "wrist_yaw" in joint_names:
                pose["wrist_yaw"] = 0.0
            for name, value in combo:
                pose[name] = value
            lower = max(
                lower,
                _scan_safe_limit(
                    probe,
                    "elbow_pitch",
                    pose,
                    float(elbow_limits.lower),
                    _BASE_CLAMP_MARGIN,
                    _DEFAULT_CLAMP_SCAN,
                    _DEFAULT_CLAMP_BISECT,
                ),
            )
    _set_joint_limits(model, "elbow_pitch", lower=lower)


def _clamp_wrist_into_forearm(model: ArticulatedObject) -> None:
    """Precise cheap backstop for the wrist bends doubling the end effector back
    onto its OWN forearm. The closed-form forearm cap is calibrated on a plain
    beam; a forked_yoke forearm's prongs reach toward the wrist and are met at a
    smaller bend, and a spherical wrist's pitch+yaw COMPOUND. Keep-out is just the
    forearm/upper-arm (one or two parts) so the query is cheap, and the fold is
    monotonic so the coarse corner clamp brackets it.
    """
    joint_names = {joint.name for joint in model.articulations}
    bends = [b for b in ("wrist_pitch", "wrist_yaw") if b in joint_names]
    if not bends:
        return
    part_names = {part.name for part in model.parts}
    keepout = [name for name in ("forearm", "upper_arm") if name in part_names]
    if not keepout:
        return
    allowed = _captured_interface_pairs(model)
    fist = _finger_pose(model, 1.0)
    # Two relaxation passes so the pair co-tighten against each other's realized
    # extreme when both bends compound (spherical wrist).
    for _ in range(2 if len(bends) > 1 else 1):
        for joint in bends:
            _corner_clamp(
                model,
                joint,
                [b for b in bends if b != joint],
                allowed,
                margin=0.006,
                park=fist,
                keepout=keepout,
            )


def _solve_joint_limits(model: ArticulatedObject, r: ResolvedRoboticArmsConfig) -> None:
    """Bound the joints whose safe travel is limited by fold-into-arm clearance.

    The dominant fold family is cumulative: shoulder/elbow/wrist pitch folding in
    the same direction curls the (fisted) end effector back through the upper
    arm and shoulder. Rather than sweep every pose combination with FCL (leaky —
    the worst pose is at an INTERMEDIATE value of the other joints, not their
    sampled corner extremes — and far too slow on a 20-joint dexterous hand), the
    same-direction elbow+wrist_pitch fold BUDGET is capped in closed form
    (`_apply_distal_fold_budget`); an intermediate joint value only folds less, so
    the single geometric bound covers the whole independent-joint sample space,
    and the shoulder keeps its full profile lift range (its lower bound is already
    0, so it cannot back-tilt the folded arm over the base).

    The wrist bends' own fold onto the forearm (including a spherical wrist's
    compounding pitch+yaw) starts from the closed-form `_wrist_bend_forearm_cap`
    and is then refined by `_clamp_wrist_into_forearm`, a cheap forearm-only FCL
    backstop that catches forked-yoke prongs the plain-beam calibration misses.
    The one remaining fold is the hand folding straight DOWN onto the base, which
    depends on the fixed base geometry; it is caught by `_clamp_fold_into_base`, a
    cheap base-only FCL backstop on the elbow.

    The opposed dexterous thumb is the one genuinely local fold the budget does
    not cover (it curls toward the palm centre, not back along the arm), so it
    keeps its cheap palm-local FCL clamp.

    Every FCL backstop uses a tiny keep-out set and a coarse monotonic scan, so
    the whole solve stays well under the 60 s medium-stage compile budget even on
    a 20-joint dexterous hand.
    """
    _apply_distal_fold_budget(model, r)
    _clamp_wrist_into_forearm(model)
    _clamp_fold_into_base(model)

    allowed = _captured_interface_pairs(model)
    joint_names = {joint.name for joint in model.articulations}

    # Dexterous thumb: it is opposed (curls toward the palm centre, not away
    # like the fingers), so its proximal/middle curl can drive the knuckle into
    # the palm shell. Solve the safe curl range against the hand (the thumb
    # segments are one captured chain seated on the palm).
    thumb_curls = [
        j for j in ("finger_4_proximal_curl", "finger_4_middle_curl") if j in joint_names
    ]
    if thumb_curls:
        thumb_allowed = allowed + [
            pair
            for pair in (
                ("palm", "finger_4_proximal"),
                ("finger_4_proximal", "finger_4_middle"),
                ("finger_4_middle", "finger_4_distal"),
            )
            if pair[0] in {p.name for p in model.parts} and pair[1] in {p.name for p in model.parts}
        ]
        # The opposed thumb naturally rests close to the palm, so use a tight
        # margin (just clear of the QC penetration tolerance) rather than the
        # arm fold margin, otherwise the rest pose itself reads as blocked.
        # The thumb only meets the palm, so keep-out to that one part keeps the
        # query cheap.
        thumb_keepout = ["palm"] if "palm" in {p.name for p in model.parts} else None
        if len(thumb_curls) == 1:
            _corner_clamp(
                model,
                thumb_curls[0],
                [],
                thumb_allowed,
                margin=_THUMB_CLAMP_MARGIN,
                keepout=thumb_keepout,
            )
        else:
            for _ in range(2):
                for joint in thumb_curls:
                    _corner_clamp(
                        model,
                        joint,
                        [b for b in thumb_curls if b != joint],
                        thumb_allowed,
                        margin=_THUMB_CLAMP_MARGIN,
                        keepout=thumb_keepout,
                    )


def build_robotic_arms(
    config: RoboticArmsConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="robotic_arms", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    shoulder_parent, shoulder_z = _build_base(model, r)
    forearm_parent, wrist_origin = _build_main_links(model, r, shoulder_parent, shoulder_z)
    wrist_parent, wrist_tip = _build_wrist(model, r, forearm_parent, wrist_origin)
    _build_end_effector(model, r, wrist_parent, wrist_tip)

    _solve_joint_limits(model, r)

    # Catch-all: no clamp pass may leave a revolute/prismatic joint at a
    # zero-width limit (degenerate declaration); floor and surface it.
    for articulation in model.articulations:
        limits = getattr(articulation, "motion_limits", None)
        if limits is None or limits.lower is None or limits.upper is None:
            continue
        if float(limits.lower) == 0.0 and float(limits.upper) == 0.0:
            logger.warning(
                "joint %r collapsed to a zero-width limit; flooring to ±0.01",
                articulation.name,
            )
            articulation.motion_limits = MotionLimits(
                effort=limits.effort,
                velocity=limits.velocity,
                lower=-0.01,
                upper=0.01,
            )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_robotic_arms(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_robotic_arms(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedRoboticArmsConfig) -> list[tuple[str, str]]:
    choices = [
        ("base_yaw_root", r.base_yaw_root_module),
        ("shoulder_elbow_link", r.shoulder_elbow_link_module),
        ("wrist_module", r.wrist_module),
        ("end_effector", r.end_effector_module),
    ]
    if r.end_effector_module == "parallel_gripper":
        choices.append(("gripper_module", r.gripper_module))
        choices.append(("gripper_finger_multiplicity", f"{r.finger_count}_finger"))
    elif r.end_effector_module == "dexterous_hand":
        choices.append(("dexterous_hand_multiplicity", "5_finger"))
    return choices


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def _allow_pair(ctx: TestContext, model: ArticulatedObject, a: str, b: str, reason: str) -> None:
    names = {part.name for part in model.parts}
    if a in names and b in names:
        ctx.allow_overlap(model.get_part(a), model.get_part(b), reason=reason)


def run_robotic_arms_tests(
    object_model: ArticulatedObject, config: RoboticArmsConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    joint_names = {joint.name for joint in object_model.articulations}
    part_names = {part.name for part in object_model.parts}

    for required in ("base_yaw", "shoulder_pitch", "elbow_pitch"):
        ctx.check(f"{required}_present", required in joint_names)
    ctx.check(
        "base_yaw_axis_vertical",
        object_model.get_articulation("base_yaw").axis == (0.0, 0.0, 1.0),
    )
    ctx.check(
        "shoulder_elbow_parallel",
        object_model.get_articulation("shoulder_pitch").axis
        == object_model.get_articulation("elbow_pitch").axis,
    )

    # Lock the distal-fold budget invariant (single source: _distal_fold_budget /
    # _wrist_bend_forearm_cap): the worst same-direction elbow+wrist_pitch fold
    # the motion sampler can command must stay under the budget at which the
    # fisted end effector curls back into the upper arm / shoulder, and each wrist
    # bend must stay under the cap at which it folds onto its own forearm.
    if "elbow_pitch" in joint_names:
        budget = _distal_fold_budget(r)
        forearm_cap = _wrist_bend_forearm_cap(r)
        elbow_limits = object_model.get_articulation("elbow_pitch").motion_limits
        wrist_up = wrist_lo = 0.0
        bend_ok = True
        if "wrist_pitch" in joint_names:
            wp = object_model.get_articulation("wrist_pitch").motion_limits
            wrist_up, wrist_lo = float(wp.upper), abs(float(wp.lower))
            bend_ok = wrist_up <= forearm_cap + 1e-6 and wrist_lo <= forearm_cap + 1e-6
        for bend in ("wrist_pitch", "wrist_yaw"):
            if bend in joint_names:
                bl = object_model.get_articulation(bend).motion_limits
                bend_ok = (
                    bend_ok and max(abs(float(bl.lower)), float(bl.upper)) <= forearm_cap + 1e-6
                )
        fold_up = float(elbow_limits.upper) + wrist_up
        fold_lo = abs(float(elbow_limits.lower)) + wrist_lo
        ctx.check(
            "distal_fold_budget_respected",
            fold_up <= budget + 1e-6 and fold_lo <= budget + 1e-6 and bend_ok,
            details=(
                f"budget={budget:.3f} fold_up={fold_up:.3f} fold_lo={fold_lo:.3f} "
                f"forearm_cap={forearm_cap:.3f}"
            ),
        )
    if r.end_effector_module == "parallel_gripper":
        ctx.check("parallel_gripper_has_base", "gripper_base" in part_names)
        if r.gripper_module == "parallel_slide":
            finger_parts = [name for name in part_names if name.startswith("finger_")]
            ctx.check(
                "parallel_slide_finger_count",
                len(finger_parts) == r.finger_count,
                details=f"expected {r.finger_count}, got {sorted(finger_parts)}",
            )
        elif r.gripper_module == "angular_2jaw":
            ctx.check(
                "angular_2jaw_has_two_jaws",
                {"angular_jaw_0", "angular_jaw_1"}.issubset(part_names),
            )
        elif r.gripper_module == "concentric_3jaw_chuck":
            ctx.check(
                "concentric_chuck_has_three_jaws",
                {"chuck_jaw_0", "chuck_jaw_1", "chuck_jaw_2"}.issubset(part_names),
            )
        elif r.gripper_module == "adaptive_2finger":
            expected = {
                "adaptive_finger_0_proximal",
                "adaptive_finger_0_distal",
                "adaptive_finger_1_proximal",
                "adaptive_finger_1_distal",
            }
            ctx.check("adaptive_2finger_has_four_links", expected.issubset(part_names))
    if r.end_effector_module == "dexterous_hand":
        proximal = [name for name in part_names if name.endswith("_proximal")]
        ctx.check("dexterous_hand_has_five_digits", len(proximal) == 5)

    for a, b in _captured_interface_pairs(object_model):
        _allow_pair(
            ctx,
            object_model,
            a,
            b,
            "Captured/nested hub geometry overlaps at the telescoping wrist/arm interface.",
        )

    for i in range(max(5, r.finger_count)):
        _allow_pair(
            ctx,
            object_model,
            "gripper_base",
            f"finger_{i}",
            "Sliding jaw carriage sits in the gripper palm slot.",
        )
        _allow_pair(
            ctx,
            object_model,
            "gripper_base",
            f"angular_jaw_{i}",
            "Angular jaw pivot is captured by the gripper cheek plates.",
        )
        _allow_pair(
            ctx,
            object_model,
            "gripper_base",
            f"chuck_jaw_{i}",
            "Chuck jaw shoe runs inside the radial guide slot.",
        )
        _allow_pair(
            ctx,
            object_model,
            "gripper_base",
            f"adaptive_finger_{i}_proximal",
            "Adaptive finger root pivots are captured by the front clevis.",
        )
        _allow_pair(
            ctx,
            object_model,
            f"adaptive_finger_{i}_proximal",
            f"adaptive_finger_{i}_distal",
            "Adaptive finger knuckles interleave.",
        )
        _allow_pair(
            ctx,
            object_model,
            "palm",
            f"finger_{i}_proximal",
            "Finger knuckle is captured by the palm knuckle bar.",
        )
        _allow_pair(
            ctx,
            object_model,
            f"finger_{i}_proximal",
            f"finger_{i}_middle",
            "Finger phalanx knuckles interleave.",
        )
        _allow_pair(
            ctx,
            object_model,
            f"finger_{i}_middle",
            f"finger_{i}_distal",
            "Finger phalanx knuckles interleave.",
        )
    return ctx.report()


__all__ = [
    "GRIPPER_MODULES",
    "RoboticArmsConfig",
    "ResolvedRoboticArmsConfig",
    "config_from_seed",
    "resolve_config",
    "build_robotic_arms",
    "build_seeded_robotic_arms",
    "slot_choices_for_seed",
    "run_robotic_arms_tests",
]
