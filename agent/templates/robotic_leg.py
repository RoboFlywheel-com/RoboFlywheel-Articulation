# SPDX-License-Identifier: Apache-2.0

"""Robotic leg — modular procedural template.

Slot graph from the approved spec:

    kinematic_topology controls whether the leg is the default sagittal
    hip->thigh->shank->foot chain or the gated 5-DOF spatial branch.

    hip_mount -> thigh -> shank -> foot

The structural slots are sampled once per leg and then applied consistently:
``segment_construction`` styles both the thigh and shank, ``joint_interface``
styles the hip/knee/ankle captured pivots, and ``foot_module`` terminates the
chain. The pivots are mechanical barrel/shaft-in-yoke contacts, so they are
grandfathered in the author tests with explicit overlap allowances rather than
MatingContract face joints.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    LoftGeometry,
    MatingContract,
    MotionLimits,
    MotionProperties,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    superellipse_profile,
)

__modular__ = True


KinematicTopology = Literal["sagittal_3dof", "spatial_5dof"]
HipMountModule = Literal[
    "service_block_lug",
    "box_cheek_boss",
    "cast_yoke_flange",
    "sealed_drip_hood",
]
SegmentConstructionModule = Literal[
    "loft_superellipse_shell",
    "primitive_spine_web",
    "beam_collar_drive",
    "cadquery_armor",
]
JointInterfaceModule = Literal[
    "lug_axiscap_saddle",
    "barrel_lug_yoke",
    "rotor_barrel_clamp",
    "motor_bore_shaft",
]
FootModule = Literal[
    "loft_foot_sole_toe_heel",
    "plate_sole_toe_lip",
    "wear_plate_foot",
    "foot_plus_fixed_sole_part",
]
JointLimitProfile = Literal["walking_safe", "wide_range", "service_locked"]
BoltDetailLevel = Literal["none", "light", "heavy"]
PaletteTheme = Literal["utility_graphite", "sealed_silver", "hazard_yellow", "humanoid_white"]


KINEMATIC_TOPOLOGIES: tuple[KinematicTopology, ...] = ("sagittal_3dof", "spatial_5dof")
HIP_MOUNT_MODULES: tuple[HipMountModule, ...] = (
    "service_block_lug",
    "box_cheek_boss",
    "cast_yoke_flange",
    "sealed_drip_hood",
)
SEGMENT_MODULES: tuple[SegmentConstructionModule, ...] = (
    "loft_superellipse_shell",
    "primitive_spine_web",
    "beam_collar_drive",
    "cadquery_armor",
)
JOINT_INTERFACE_MODULES: tuple[JointInterfaceModule, ...] = (
    "lug_axiscap_saddle",
    "barrel_lug_yoke",
    "rotor_barrel_clamp",
    "motor_bore_shaft",
)
FOOT_MODULES: tuple[FootModule, ...] = (
    "loft_foot_sole_toe_heel",
    "plate_sole_toe_lip",
    "wear_plate_foot",
    "foot_plus_fixed_sole_part",
)


ROBOTIC_LEG_PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "utility_graphite": {
        "armor": (0.28, 0.31, 0.34, 1.0),
        "dark": (0.08, 0.09, 0.10, 1.0),
        "metal": (0.64, 0.66, 0.68, 1.0),
        "rubber": (0.035, 0.036, 0.038, 1.0),
        "accent": (0.13, 0.36, 0.58, 1.0),
        "seal": (0.02, 0.025, 0.030, 1.0),
    },
    "sealed_silver": {
        "armor": (0.62, 0.65, 0.66, 1.0),
        "dark": (0.18, 0.20, 0.22, 1.0),
        "metal": (0.82, 0.84, 0.86, 1.0),
        "rubber": (0.045, 0.048, 0.052, 1.0),
        "accent": (0.22, 0.42, 0.48, 1.0),
        "seal": (0.10, 0.11, 0.12, 1.0),
    },
    "hazard_yellow": {
        "armor": (0.90, 0.70, 0.16, 1.0),
        "dark": (0.09, 0.09, 0.08, 1.0),
        "metal": (0.68, 0.68, 0.65, 1.0),
        "rubber": (0.035, 0.035, 0.032, 1.0),
        "accent": (0.82, 0.20, 0.10, 1.0),
        "seal": (0.05, 0.05, 0.045, 1.0),
    },
    "humanoid_white": {
        "armor": (0.86, 0.87, 0.86, 1.0),
        "dark": (0.18, 0.20, 0.22, 1.0),
        "metal": (0.74, 0.77, 0.80, 1.0),
        "rubber": (0.08, 0.085, 0.09, 1.0),
        "accent": (0.10, 0.46, 0.72, 1.0),
        "seal": (0.16, 0.17, 0.18, 1.0),
    },
}


@dataclass(frozen=True)
class RoboticLegConfig:
    kinematic_topology: KinematicTopology | None = None
    hip_mount_module: HipMountModule | None = None
    segment_construction_module: SegmentConstructionModule | None = None
    joint_interface_module: JointInterfaceModule | None = None
    foot_module: FootModule | None = None

    palette_theme: PaletteTheme = "utility_graphite"
    total_leg_length: float = 0.66
    thigh_shank_ratio: float = 0.54
    mount_z: float = 0.14
    joint_limit_profile: JointLimitProfile = "walking_safe"
    bolt_detail_level: BoltDetailLevel = "light"

    palette: dict[str, tuple[float, float, float, float]] = field(default_factory=dict)


@dataclass(frozen=True)
class ResolvedRoboticLegConfig:
    kinematic_topology: KinematicTopology
    hip_mount_module: HipMountModule
    segment_construction_module: SegmentConstructionModule
    joint_interface_module: JointInterfaceModule
    foot_module: FootModule
    palette_theme: PaletteTheme
    total_leg_length: float
    thigh_shank_ratio: float
    mount_z: float
    thigh_len: float
    shank_len: float
    segment_width: float
    segment_depth: float
    joint_radius: float
    joint_span: float
    foot_length: float
    foot_width: float
    foot_drop: float
    joint_limit_profile: JointLimitProfile
    bolt_detail_level: BoltDetailLevel
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(float(value), hi))


def _weighted_choice(
    rng: random.Random,
    choices: tuple[tuple[KinematicTopology, float], ...],
) -> KinematicTopology:
    total = sum(weight for _, weight in choices)
    pick = rng.random() * total
    cursor = 0.0
    for value, weight in choices:
        cursor += weight
        if pick <= cursor:
            return value
    return choices[-1][0]


def config_from_seed(seed: int) -> RoboticLegConfig:
    if seed == 0:
        return RoboticLegConfig(
            kinematic_topology="sagittal_3dof",
            hip_mount_module="service_block_lug",
            segment_construction_module="loft_superellipse_shell",
            joint_interface_module="lug_axiscap_saddle",
            foot_module="loft_foot_sole_toe_heel",
            palette_theme="utility_graphite",
            total_leg_length=0.66,
            thigh_shank_ratio=0.54,
            mount_z=0.14,
            joint_limit_profile="walking_safe",
            bolt_detail_level="light",
        )

    rng = random.Random(seed)
    topology = _weighted_choice(rng, (("sagittal_3dof", 0.88), ("spatial_5dof", 0.12)))
    return RoboticLegConfig(
        kinematic_topology=topology,
        hip_mount_module=rng.choice(HIP_MOUNT_MODULES),
        segment_construction_module=rng.choice(SEGMENT_MODULES),
        joint_interface_module=rng.choice(JOINT_INTERFACE_MODULES),
        foot_module=rng.choice(FOOT_MODULES),
        palette_theme=rng.choice(tuple(ROBOTIC_LEG_PALETTES.keys())),  # type: ignore[arg-type]
        total_leg_length=round(rng.uniform(0.55, 1.10), 4),
        thigh_shank_ratio=round(rng.uniform(0.50, 0.58), 4),
        mount_z=round(rng.uniform(0.10, 0.31), 4),
        joint_limit_profile=rng.choice(("walking_safe", "wide_range", "service_locked")),
        bolt_detail_level=rng.choice(("none", "light", "heavy")),
    )


def resolve_config(config: RoboticLegConfig) -> ResolvedRoboticLegConfig:
    topology = config.kinematic_topology or "sagittal_3dof"
    hip_mount = config.hip_mount_module or "service_block_lug"
    segment = config.segment_construction_module or "loft_superellipse_shell"
    joint = config.joint_interface_module or "lug_axiscap_saddle"
    foot = config.foot_module or "loft_foot_sole_toe_heel"

    if topology not in KINEMATIC_TOPOLOGIES:
        raise ValueError(f"Unsupported kinematic_topology: {topology}")
    if hip_mount not in HIP_MOUNT_MODULES:
        raise ValueError(f"Unsupported hip_mount_module: {hip_mount}")
    if segment not in SEGMENT_MODULES:
        raise ValueError(f"Unsupported segment_construction_module: {segment}")
    if joint not in JOINT_INTERFACE_MODULES:
        raise ValueError(f"Unsupported joint_interface_module: {joint}")
    if foot not in FOOT_MODULES:
        raise ValueError(f"Unsupported foot_module: {foot}")
    if config.palette_theme not in ROBOTIC_LEG_PALETTES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")
    if config.joint_limit_profile not in ("walking_safe", "wide_range", "service_locked"):
        raise ValueError(f"Unsupported joint_limit_profile: {config.joint_limit_profile}")
    if config.bolt_detail_level not in ("none", "light", "heavy"):
        raise ValueError(f"Unsupported bolt_detail_level: {config.bolt_detail_level}")

    total = _clamp(config.total_leg_length, 0.55, 1.10)
    ratio = _clamp(config.thigh_shank_ratio, 0.50, 0.58)
    foot_drop = _clamp(total * 0.155, 0.095, 0.165)
    link_total = max(0.42, total - foot_drop)
    thigh_len = max(0.18, link_total * ratio)
    shank_len = max(0.16, link_total - thigh_len)
    scale = _clamp(total / 0.72, 0.80, 1.35)

    palette = dict(config.palette)
    if not palette:
        palette = dict(ROBOTIC_LEG_PALETTES[config.palette_theme])
    else:
        merged = dict(ROBOTIC_LEG_PALETTES[config.palette_theme])
        merged.update(palette)
        palette = merged

    return ResolvedRoboticLegConfig(
        kinematic_topology=topology,
        hip_mount_module=hip_mount,
        segment_construction_module=segment,
        joint_interface_module=joint,
        foot_module=foot,
        palette_theme=config.palette_theme,
        total_leg_length=total,
        thigh_shank_ratio=ratio,
        mount_z=_clamp(config.mount_z, 0.10, 0.31),
        thigh_len=thigh_len,
        shank_len=shank_len,
        segment_width=0.078 * scale,
        segment_depth=0.070 * scale,
        joint_radius=0.026 * scale,
        joint_span=0.104 * scale,
        foot_length=0.24 * scale,
        foot_width=0.115 * scale,
        foot_drop=foot_drop,
        joint_limit_profile=config.joint_limit_profile,
        bolt_detail_level=config.bolt_detail_level,
        palette=palette,
    )


def _axis_rpy(axis: str) -> tuple[float, float, float]:
    if axis == "x":
        return (0.0, math.pi / 2.0, 0.0)
    if axis == "y":
        return (-math.pi / 2.0, 0.0, 0.0)
    return (0.0, 0.0, 0.0)


def _xy_section(
    width: float,
    depth: float,
    z: float,
    *,
    x_shift: float = 0.0,
    exponent: float = 2.7,
    segments: int = 28,
) -> list[tuple[float, float, float]]:
    return [
        (x + x_shift, y, z)
        for x, y in superellipse_profile(width, depth, exponent=exponent, segments=segments)
    ]


def _loft_mesh(name: str, sections: list[list[tuple[float, float, float]]]):
    return mesh_from_geometry(LoftGeometry(sections, cap=True, closed=True), name)


def _bolt_count(level: BoltDetailLevel) -> int:
    return {"none": 0, "light": 1, "heavy": 2}[level]


def _add_y_cylinder(part, radius: float, length: float, xyz, *, material: str, name: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=_axis_rpy("y")),
        material=material,
        name=name, material_class_id="metal.stainless_matte",
    )


def _add_x_cylinder(part, radius: float, length: float, xyz, *, material: str, name: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=_axis_rpy("x")),
        material=material,
        name=name, material_class_id="metal.stainless_matte",
    )


def _add_side_fasteners(
    part,
    *,
    prefix: str,
    face_y: float,
    z_values: tuple[float, ...],
    x_values: tuple[float, ...],
    r: ResolvedRoboticLegConfig,
) -> None:
    count = _bolt_count(r.bolt_detail_level)
    if count == 0:
        return
    selected_z = z_values[: max(1, min(len(z_values), count))]
    for zi, z in enumerate(selected_z):
        for xi, x in enumerate(x_values):
            pad_y = face_y * 0.92
            part.visual(
                Box((0.018, 0.024, 0.012)),
                origin=Origin(xyz=(x, pad_y, z)),
                material="armor",
                name=f"{prefix}_washer_pad_{zi}_{xi}", material_class_id="metal.paint_coated",
            )
            _add_y_cylinder(
                part,
                0.0046,
                0.014,
                (x, face_y * 1.02, z),
                material="metal",
                name=f"{prefix}_{zi}_{xi}",
            )


def _hip_downstream_radius(r: ResolvedRoboticLegConfig) -> float:
    return r.joint_radius * 1.08


def _build_hip_mount(model: ArticulatedObject, r: ResolvedRoboticLegConfig) -> None:
    part = model.part("hip_mount")
    if r.hip_mount_module == "service_block_lug":
        part.visual(
            Box((0.150, 0.122, r.mount_z * 0.62)),
            origin=Origin(xyz=(0.0, 0.0, r.mount_z * 0.56)),
            material="armor",
            name="hip_service_block", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((0.070, 0.050, 0.026)),
            origin=Origin(xyz=(0.040, 0.0, 0.030)),
            material="armor",
            name="hip_front_gusset", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((0.074, 0.052, 0.030)),
            origin=Origin(xyz=(-0.030, 0.0, 0.026)),
            material="armor",
            name="hip_rear_gusset", material_class_id="metal.paint_coated",
        )
        for side, y in (("right", r.joint_span * 0.50), ("left", -r.joint_span * 0.50)):
            part.visual(
                Box((0.048, 0.020, 0.105)),
                origin=Origin(xyz=(0.0, y, 0.0)),
                material="armor",
                name=f"hip_lug_{side}", material_class_id="metal.paint_coated",
            )
            _add_y_cylinder(
                part,
                r.joint_radius * 0.78,
                0.012,
                (0.0, y + (0.010 if y > 0 else -0.010), 0.0),
                material="metal",
                name=f"hip_axis_cap_{side}",
            )
        for index, (x, y) in enumerate(
            ((0.050, 0.036), (0.050, -0.036), (-0.050, 0.036), (-0.050, -0.036))
        ):
            part.visual(
                Cylinder(radius=0.0052, length=0.006),
                origin=Origin(xyz=(x, y, r.mount_z * 0.64)),
                material="metal",
                name=f"hip_top_fastener_{index}", material_class_id="metal.stainless_matte",
            )
    elif r.hip_mount_module == "box_cheek_boss":
        part.visual(
            Box((0.19, 0.18, 0.070)),
            origin=Origin(xyz=(0.0, 0.0, r.mount_z * 0.70)),
            material="armor",
            name="mount_block", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((0.105, 0.160, 0.090)),
            origin=Origin(xyz=(-0.048, 0.0, r.mount_z * 0.55)),
            material="dark",
            name="actuator_pack", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Box((0.070, 0.160, 0.070)),
            origin=Origin(xyz=(0.058, 0.0, r.mount_z * 0.48)),
            material="dark",
            name="front_gusset", material_class_id="metal.blackened_gunmetal",
        )
        for side, y in (("left", 0.069), ("right", -0.069)):
            part.visual(
                Box((0.105, 0.026, 0.156)),
                origin=Origin(xyz=(0.0, y, 0.0)),
                material="armor",
                name=f"{side}_hip_cheek", material_class_id="metal.paint_coated",
            )
            _add_y_cylinder(
                part,
                r.joint_radius * 1.08,
                0.026,
                (0.0, y, 0.0),
                material="metal",
                name=f"{side}_hip_boss",
            )
        part.visual(
            Box((0.155, 0.120, 0.032)),
            origin=Origin(xyz=(0.0, 0.0, -0.020)),
            material="armor",
            name="lower_tie_bridge", material_class_id="metal.paint_coated",
        )
    elif r.hip_mount_module == "cast_yoke_flange":
        part.visual(
            Box((0.36, 0.26, 0.032)),
            origin=Origin(xyz=(0.0, 0.0, r.mount_z)),
            material="armor",
            name="fixed_mount_flange", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((0.23, 0.14, 0.112)),
            origin=Origin(xyz=(-0.015, 0.0, r.mount_z * 0.66)),
            material="armor",
            name="upper_actuator_spine", material_class_id="metal.paint_coated",
        )
        for idx, y in enumerate((0.106, -0.106)):
            part.visual(
                Box((0.210, 0.042, 0.194)),
                origin=Origin(xyz=(0.0, y, 0.0)),
                material="armor",
                name=f"hip_yoke_cheek_{idx}", material_class_id="metal.paint_coated",
            )
        part.visual(
            Box((0.210, 0.232, 0.042)),
            origin=Origin(xyz=(0.0, 0.0, 0.112)),
            material="armor",
            name="hip_top_bridge", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((0.044, 0.232, 0.116)),
            origin=Origin(xyz=(-0.100, 0.0, 0.020)),
            material="armor",
            name="hip_rear_bridge", material_class_id="metal.paint_coated",
        )
    else:
        gap = r.joint_span
        cheek_t = 0.026
        cheek_y = gap * 0.5 + cheek_t * 0.5
        part.visual(
            Box((0.36, 0.24, 0.046)),
            origin=Origin(xyz=(0.0, 0.0, r.mount_z)),
            material="armor",
            name="hip_base_plate", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((0.23, 0.20, 0.066)),
            origin=Origin(xyz=(0.0, 0.0, r.mount_z - 0.050)),
            material="armor",
            name="hip_top_bridge", material_class_id="metal.paint_coated",
        )
        for side, y in (("outer", cheek_y), ("inner", -cheek_y)):
            part.visual(
                Box((0.188, cheek_t, 0.260)),
                origin=Origin(xyz=(0.0, y, 0.0)),
                material="armor",
                name=f"hip_cheek_{side}", material_class_id="metal.paint_coated",
            )
            _add_y_cylinder(
                part,
                r.joint_radius * 1.42,
                0.012,
                (0.0, y + (0.018 if y > 0 else -0.018), 0.0),
                material="seal",
                name=f"hip_seal_{side}",
            )
        part.visual(
            Box((0.43, 0.30, 0.026)),
            origin=Origin(xyz=(0.0, 0.0, r.mount_z + 0.030)),
            material="dark",
            name="hip_drip_hood", material_class_id="metal.blackened_gunmetal",
        )

    part.visual(
        Box((0.060, 0.240, r.mount_z + 0.005)),
        origin=Origin(xyz=(0.0, 0.0, r.mount_z * 0.50 - 0.0025)),
        material="armor",
        name="hip_core_bridge", material_class_id="metal.paint_coated",
    )
    part.visual(
        Box((0.072, 0.300, 0.034)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="armor",
        name="hip_pivot_crossmember", material_class_id="metal.paint_coated",
    )
    _add_y_cylinder(
        part,
        r.joint_radius * 0.72,
        r.joint_span * 1.08,
        (0.0, 0.0, 0.0),
        material="metal",
        name="hip_pivot_bushing",
    )

    part.inertial = Inertial.from_geometry(
        Box((0.38, 0.30, r.mount_z + 0.16)),
        mass=5.5,
        origin=Origin(xyz=(0.0, 0.0, r.mount_z * 0.45)),
    )


def _emit_joint_hardware(
    part, *, prefix: str, z: float, role: str, r: ResolvedRoboticLegConfig
) -> None:
    jr = r.joint_radius
    span = r.joint_span
    if r.joint_interface_module == "lug_axiscap_saddle":
        _add_y_cylinder(
            part, jr * 0.88, span * 0.78, (0.0, 0.0, z), material="metal", name=f"{prefix}_hub"
        )
        part.visual(
            Box((jr * 1.75, span * 0.70, jr * 1.08)),
            origin=Origin(xyz=(0.0, 0.0, z - jr * 0.28)),
            material="armor",
            name=f"{prefix}_saddle", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((jr * 0.70, span * 0.78, jr * 2.00)),
            origin=Origin(xyz=(0.0, 0.0, z - jr * 0.75)),
            material="armor",
            name=f"{prefix}_web", material_class_id="metal.paint_coated",
        )
        for side, y in (("right", span * 0.45), ("left", -span * 0.45)):
            _add_y_cylinder(
                part,
                jr * 0.70,
                0.020,
                (0.0, span * (0.39 if y > 0 else -0.39), z),
                material="metal",
                name=f"{prefix}_axis_cap_{side}",
            )
    elif r.joint_interface_module == "barrel_lug_yoke":
        _add_y_cylinder(
            part,
            jr * 1.18,
            span * 1.22,
            (0.0, 0.0, z),
            material="metal",
            name=f"{prefix}_barrel" if role == "distal" else f"{prefix}_lug_barrel",
        )
        for side, y in (("outer", span * 0.58), ("inner", -span * 0.58)):
            part.visual(
                Box((jr * 1.95, 0.030, jr * 4.15)),
                origin=Origin(xyz=(0.012, y, z - jr * 1.38)),
                material="armor",
                name=f"{prefix}_cheek_{side}", material_class_id="metal.paint_coated",
            )
        part.visual(
            Box((jr * 2.10, span * 1.25, jr * 0.82)),
            origin=Origin(xyz=(0.0, 0.0, z - jr * 2.55)),
            material="armor",
            name=f"{prefix}_yoke_bridge", material_class_id="metal.paint_coated",
        )
    elif r.joint_interface_module == "rotor_barrel_clamp":
        _add_y_cylinder(
            part,
            jr * 1.10,
            span * 1.05,
            (0.0, 0.0, z),
            material="metal",
            name=f"{prefix}_rotor_barrel",
        )
        _add_y_cylinder(
            part,
            jr * 0.76,
            span * 0.86,
            (0.0, 0.0, z),
            material="dark",
            name=f"{prefix}_clamp_band",
        )
        part.visual(
            Box((jr * 1.30, span * 0.72, jr * 2.60)),
            origin=Origin(xyz=(0.0, 0.0, z - jr * 1.15)),
            material="dark",
            name=f"{prefix}_neck_block", material_class_id="metal.blackened_gunmetal",
        )
    else:
        if role == "distal":
            _add_y_cylinder(
                part, jr * 1.24, span * 1.25, (0.0, 0.0, z), material="dark", name=f"{prefix}_motor"
            )
        else:
            _add_y_cylinder(
                part,
                jr * 0.72,
                span * 1.35,
                (0.0, 0.0, z),
                material="metal",
                name=f"{prefix}_shaft",
            )
            part.visual(
                Box((jr * 2.60, span * 0.78, jr * 0.92)),
                origin=Origin(xyz=(0.0, 0.0, z - jr * 0.92)),
                material="dark",
                name=f"{prefix}_collar", material_class_id="metal.blackened_gunmetal",
            )
        part.visual(
            Box((jr * 0.86, span * 0.50, jr * 2.20)),
            origin=Origin(xyz=(0.0, 0.0, z - jr * 0.92)),
            material="dark",
            name=f"{prefix}_drive_web", material_class_id="metal.blackened_gunmetal",
        )


def _segment_loft_mesh(name: str, length: float, r: ResolvedRoboticLegConfig):
    w = r.segment_width
    d = r.segment_depth
    return _loft_mesh(
        name,
        [
            _xy_section(w * 1.18, d * 1.18, -0.010, exponent=2.9),
            _xy_section(w * 0.90, d * 0.92, -length * 0.38, x_shift=-0.006, exponent=2.6),
            _xy_section(w * 0.96, d * 0.96, -length * 0.72, x_shift=0.006, exponent=2.6),
            _xy_section(w * 1.05, d * 1.05, -length + 0.045, x_shift=0.010, exponent=2.8),
        ],
    )


def _armor_mesh(name: str, length: float, r: ResolvedRoboticLegConfig):
    w = r.segment_width * 1.18
    d = r.segment_depth * 1.28
    return _loft_mesh(
        name,
        [
            _xy_section(w * 0.88, d * 0.95, -0.070, exponent=4.0),
            _xy_section(w * 1.10, d * 1.05, -length * 0.36, exponent=4.5),
            _xy_section(w * 0.96, d * 1.20, -length * 0.68, x_shift=-0.006, exponent=4.0),
            _xy_section(w * 0.72, d * 0.92, -length + 0.080, exponent=3.8),
        ],
    )


def _build_segment(
    model: ArticulatedObject,
    *,
    part_name: str,
    length: float,
    r: ResolvedRoboticLegConfig,
) -> None:
    part = model.part(part_name)
    w = r.segment_width
    d = r.segment_depth
    jr = r.joint_radius

    _emit_joint_hardware(part, prefix=f"{part_name}_prox", z=0.0, role="proximal", r=r)
    _emit_joint_hardware(part, prefix=f"{part_name}_dist", z=-length, role="distal", r=r)

    if r.segment_construction_module == "loft_superellipse_shell":
        part.visual(
            _segment_loft_mesh(f"{part_name}_superellipse_shell", length, r),
            material="armor",
            name=f"{part_name}_shell", material_class_id="tech.scifi_panel",
        )
        part.visual(
            Box((w * 0.38, d * 0.74, length * 0.46)),
            origin=Origin(xyz=(w * 0.48, 0.0, -length * 0.48)),
            material="dark",
            name=f"{part_name}_actuator_bay", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            Box((w * 1.00, d * 0.20, length * 0.74)),
            origin=Origin(xyz=(-w * 0.30, 0.0, -length * 0.50)),
            material="accent",
            name=f"{part_name}_front_rib", material_class_id="plastic.opaque_glossy_molded",
        )
    elif r.segment_construction_module == "primitive_spine_web":
        part.visual(
            Box((w * 0.96, d * 0.88, length * 0.82)),
            origin=Origin(xyz=(0.0, 0.0, -length * 0.50)),
            material="dark",
            name=f"{part_name}_spine", material_class_id="metal.blackened_gunmetal",
        )
        for side, y in (("outer", d * 0.48), ("inner", -d * 0.48)):
            part.visual(
                Box((w * 1.28, d * 0.34, length * 0.66)),
                origin=Origin(xyz=(w * 0.28, y, -length * 0.52)),
                material="armor",
                name=f"{part_name}_side_web_{side}", material_class_id="metal.paint_coated",
            )
        part.visual(
            Box((w * 1.10, d * 1.40, jr * 1.05)),
            origin=Origin(xyz=(0.0, 0.0, -length + jr * 0.30)),
            material="armor",
            name=f"{part_name}_spine_yoke_bridge", material_class_id="metal.paint_coated",
        )
    elif r.segment_construction_module == "beam_collar_drive":
        part.visual(
            Box((w * 1.35, d * 1.02, length * 0.72)),
            origin=Origin(xyz=(0.0, 0.0, -length * 0.50)),
            material="dark",
            name=f"{part_name}_beam", material_class_id="metal.blackened_gunmetal",
        )
        for label, z in (("prox", -0.120), ("dist", -length + 0.120)):
            part.visual(
                Box((w * 1.80, d * 1.24, jr * 1.25)),
                origin=Origin(xyz=(0.0, 0.0, z)),
                material="metal",
                name=f"{part_name}_{label}_beam_collar", material_class_id="metal.stainless_matte",
            )
            part.visual(
                Box((w * 0.70, d * 0.58, jr * 2.80)),
                origin=Origin(xyz=(0.0, 0.0, z - jr * 0.75)),
                material="dark",
                name=f"{part_name}_{label}_beam_drive_web", material_class_id="metal.blackened_gunmetal",
            )
    else:
        part.visual(
            Box((w * 0.58, d * 0.62, length * 0.92)),
            origin=Origin(xyz=(0.0, 0.0, -length * 0.50)),
            material="dark",
            name=f"{part_name}_core", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            _armor_mesh(f"{part_name}_cadquery_style_armor", length, r),
            material="armor",
            name=f"{part_name}_armor", material_class_id="tech.scifi_panel",
        )
        part.visual(
            Box((w * 0.42, d * 0.20, length * 0.46)),
            origin=Origin(xyz=(0.0, d * 0.68, -length * 0.48)),
            material="accent",
            name=f"{part_name}_shin_rail", material_class_id="plastic.opaque_glossy_molded",
        )

    part.visual(
        Box((w * 0.78, d * 0.68, jr * 2.4)),
        origin=Origin(xyz=(0.0, 0.0, -jr * 1.00)),
        material="armor",
        name=f"{part_name}_prox_shell_neck", material_class_id="tech.scifi_panel",
    )
    part.visual(
        Box((w * 0.78, d * 0.68, jr * 2.4)),
        origin=Origin(xyz=(0.0, 0.0, -length + jr * 1.00)),
        material="armor",
        name=f"{part_name}_dist_shell_neck", material_class_id="tech.scifi_panel",
    )
    _add_side_fasteners(
        part,
        prefix=f"{part_name}_side_fastener",
        face_y=d * 0.58,
        z_values=(-length * 0.25, -length * 0.50, -length * 0.75, -length + 0.060),
        x_values=(-w * 0.28, w * 0.28),
        r=r,
    )
    _add_side_fasteners(
        part,
        prefix=f"{part_name}_side_fastener_inner",
        face_y=-d * 0.58,
        z_values=(-length * 0.25, -length * 0.50, -length * 0.75, -length + 0.060),
        x_values=(-w * 0.28, w * 0.28),
        r=r,
    )
    part.inertial = Inertial.from_geometry(
        Box((w * 1.8, d * 1.8, length + 0.10)),
        mass=3.0 + length * 6.0,
        origin=Origin(xyz=(0.0, 0.0, -length * 0.50)),
    )


def _foot_shell_mesh(r: ResolvedRoboticLegConfig):
    return _loft_mesh(
        "foot_superellipse_shell",
        [
            _xy_section(r.foot_width * 0.42, r.foot_width * 0.58, -0.035, x_shift=0.035),
            _xy_section(r.foot_width * 0.62, r.foot_width * 0.82, -0.080, x_shift=0.060),
            _xy_section(r.foot_width * 0.52, r.foot_width * 0.78, -0.130, x_shift=0.105),
            _xy_section(r.foot_width * 0.30, r.foot_width * 0.58, -0.155, x_shift=0.150),
        ],
    )


def _build_foot(model: ArticulatedObject, r: ResolvedRoboticLegConfig) -> None:
    foot = model.part("foot")
    _emit_joint_hardware(foot, prefix="foot_ankle", z=0.0, role="proximal", r=r)
    fl = r.foot_length
    fw = r.foot_width
    drop = r.foot_drop
    jr = r.joint_radius

    if r.foot_module == "loft_foot_sole_toe_heel":
        foot.visual(_foot_shell_mesh(r), material="armor", name="foot_shell", material_class_id="tech.scifi_panel")
        foot.visual(
            Box((fw * 0.56, fw * 0.50, jr * 1.00)),
            origin=Origin(xyz=(0.0, 0.0, -jr * 0.65)),
            material="armor",
            name="foot_ankle_bridge", material_class_id="metal.paint_coated",
        )
        foot.visual(
            Box((fl * 0.38, fw * 0.54, drop * 0.36)),
            origin=Origin(xyz=(fl * 0.05, 0.0, -drop * 0.48)),
            material="armor",
            name="foot_dorsal_housing", material_class_id="tech.scifi_panel",
        )
        foot.visual(
            Box((fl * 0.80, fw * 0.82, 0.018)),
            origin=Origin(xyz=(fl * 0.15, 0.0, -drop)),
            material="rubber",
            name="foot_sole", material_class_id="rubber.smooth_plain",
        )
        foot.visual(
            Box((fl * 0.14, fw * 0.72, 0.034)),
            origin=Origin(xyz=(fl * 0.48, 0.0, -drop + 0.016)),
            material="rubber",
            name="toe_bumper", material_class_id="rubber.smooth_plain",
        )
        foot.visual(
            Box((fl * 0.12, fw * 0.62, 0.030)),
            origin=Origin(xyz=(-fl * 0.25, 0.0, -drop + 0.014)),
            material="rubber",
            name="heel_pad", material_class_id="rubber.smooth_plain",
        )
    elif r.foot_module == "plate_sole_toe_lip":
        foot.visual(
            Box((fw * 0.78, fw * 0.70, drop * 0.52)),
            origin=Origin(xyz=(0.0, 0.0, -drop * 0.40)),
            material="armor",
            name="ankle_block", material_class_id="metal.paint_coated",
        )
        foot.visual(
            Box((fl * 1.10, fw * 1.25, 0.050)),
            origin=Origin(xyz=(fl * 0.22, 0.0, -drop)),
            material="rubber",
            name="sole_pad", material_class_id="rubber.smooth_plain",
        )
        foot.visual(
            Box((fl * 0.50, fw * 1.05, 0.036)),
            origin=Origin(xyz=(fl * 0.48, 0.0, -drop + 0.034)),
            material="rubber",
            name="toe_lip", material_class_id="rubber.smooth_plain",
        )
        foot.visual(
            Box((fw * 0.45, fw * 0.38, drop * 0.74)),
            origin=Origin(xyz=(0.0, 0.0, -drop * 0.45)),
            material="dark",
            name="ankle_drive_web", material_class_id="metal.blackened_gunmetal",
        )
    elif r.foot_module == "wear_plate_foot":
        foot.visual(
            Box((fw * 0.52, fw * 0.52, drop * 0.40)),
            origin=Origin(xyz=(0.0, 0.0, -drop * 0.35)),
            material="armor",
            name="ankle_neck_block", material_class_id="metal.paint_coated",
        )
        foot.visual(
            Box((fl * 0.42, fw * 0.78, drop * 0.42)),
            origin=Origin(xyz=(fl * 0.10, 0.0, -drop * 0.58)),
            material="armor",
            name="compact_ankle_carrier", material_class_id="metal.paint_coated",
        )
        foot.visual(
            Box((fl * 0.96, fw * 1.05, 0.036)),
            origin=Origin(xyz=(fl * 0.16, 0.0, -drop)),
            material="rubber",
            name="rubber_foot_pad", material_class_id="rubber.smooth_plain",
        )
        foot.visual(
            Box((fl * 0.32, fw * 0.88, 0.018)),
            origin=Origin(xyz=(fl * 0.43, 0.0, -drop + 0.022)),
            material="metal",
            name="toe_wear_plate", material_class_id="metal.steel_bare",
        )
        foot.visual(
            Box((fl * 0.25, fw * 0.82, 0.018)),
            origin=Origin(xyz=(-fl * 0.22, 0.0, -drop + 0.022)),
            material="metal",
            name="heel_wear_plate", material_class_id="metal.steel_bare",
        )
    else:
        foot.visual(
            Box((fw * 0.68, fw * 0.66, drop * 0.62)),
            origin=Origin(xyz=(0.0, 0.0, -drop * 0.40)),
            material="armor",
            name="ankle_knuckle", material_class_id="metal.paint_coated",
        )
        foot.visual(
            Box((fl * 0.72, fw * 0.90, drop * 0.42)),
            origin=Origin(xyz=(fl * 0.16, 0.0, -drop * 0.70)),
            material="dark",
            name="foot_deck", material_class_id="metal.blackened_gunmetal",
        )
        foot.visual(
            Box((fl * 0.24, fw * 1.08, 0.036)),
            origin=Origin(xyz=(fl * 0.50, 0.0, -drop * 0.58)),
            material="armor",
            name="toe_guard", material_class_id="tech.scifi_panel",
        )
        foot.visual(
            Box((fl * 0.20, fw * 0.82, 0.052)),
            origin=Origin(xyz=(-fl * 0.26, 0.0, -drop * 0.72)),
            material="armor",
            name="heel_block", material_class_id="metal.paint_coated",
        )
        foot.visual(
            Box((fl * 1.05, fw * 1.10, 0.012)),
            origin=Origin(xyz=(fl * 0.10, 0.0, -drop - 0.006)),
            material="armor",
            name="sole_socket", material_class_id="metal.paint_coated",
        )

    foot.visual(
        Box((fl * 0.76, fw * 0.46, drop + 0.018)),
        origin=Origin(xyz=(fl * 0.12, 0.0, -drop * 0.50 + 0.002)),
        material="armor",
        name="foot_underbridge", material_class_id="metal.paint_coated",
    )

    foot.inertial = Inertial.from_geometry(
        Box((fl * 1.25, fw * 1.25, drop + 0.060)),
        mass=2.4,
        origin=Origin(xyz=(fl * 0.12, 0.0, -drop * 0.65)),
    )

    if r.foot_module == "foot_plus_fixed_sole_part":
        sole = model.part("sole_pad")
        sole.visual(
            Box((fl * 1.12, fw * 1.16, 0.020)),
            origin=Origin(xyz=(0.0, 0.0, -0.010)),
            material="rubber",
            name="sole_block", material_class_id="rubber.smooth_plain",
        )
        sole.inertial = Inertial.from_geometry(
            Box((fl * 1.12, fw * 1.16, 0.020)),
            mass=0.8,
            origin=Origin(xyz=(0.0, 0.0, -0.010)),
        )
        model.articulation(
            "foot_to_sole",
            ArticulationType.FIXED,
            parent=foot,
            child=sole,
            origin=Origin(xyz=(fl * 0.10, 0.0, -drop - 0.012)),
            mating=MatingContract(
                parent_face_geometry="sole_socket",
                parent_face_side="negative_z",
                child_face_geometry="sole_block",
                child_face_side="positive_z",
                contact_tol=0.0030,
            ),
        )


def _build_spatial_roll_link(model: ArticulatedObject, r: ResolvedRoboticLegConfig) -> None:
    link = model.part("hip_roll_link")
    _add_x_cylinder(
        link,
        r.joint_radius * 1.08,
        r.joint_span * 0.95,
        (0.0, 0.0, 0.0),
        material="metal",
        name="hip_roll_barrel",
    )
    link.visual(
        Box((r.segment_width * 0.80, r.segment_depth * 0.82, 0.095)),
        origin=Origin(xyz=(0.0, 0.0, -0.050)),
        material="dark",
        name="roll_to_pitch_drop", material_class_id="metal.blackened_gunmetal",
    )
    _add_y_cylinder(
        link,
        r.joint_radius * 0.92,
        r.joint_span * 0.78,
        (0.0, 0.0, -0.085),
        material="metal",
        name="hip_pitch_barrel",
    )
    link.inertial = Inertial.from_geometry(
        Box((r.segment_width, r.joint_span, 0.13)),
        mass=1.2,
        origin=Origin(xyz=(0.0, 0.0, -0.045)),
    )


def _build_spatial_ankle_link(model: ArticulatedObject, r: ResolvedRoboticLegConfig) -> None:
    link = model.part("ankle_pitch_link")
    _add_y_cylinder(
        link,
        r.joint_radius * 0.92,
        r.joint_span * 0.78,
        (0.0, 0.0, 0.0),
        material="metal",
        name="ankle_pitch_barrel",
    )
    link.visual(
        Box((r.segment_width * 0.72, r.segment_depth * 0.72, 0.130)),
        origin=Origin(xyz=(0.0, 0.0, -0.060)),
        material="dark",
        name="pitch_to_roll_drop", material_class_id="metal.blackened_gunmetal",
    )
    _add_x_cylinder(
        link,
        r.joint_radius * 0.82,
        r.joint_span * 0.68,
        (0.0, 0.0, -0.115),
        material="metal",
        name="ankle_roll_barrel",
    )
    link.inertial = Inertial.from_geometry(
        Box((r.segment_width, r.joint_span, 0.16)),
        mass=0.9,
        origin=Origin(xyz=(0.0, 0.0, -0.060)),
    )


def _limits(profile: JointLimitProfile, joint_name: str) -> MotionLimits:
    if profile == "service_locked":
        ranges = {
            "hip_pitch": (-0.20, 0.28),
            "knee_pitch": (0.0, 0.42),
            "ankle_pitch": (-0.18, 0.18),
            "hip_roll": (-0.16, 0.16),
            "ankle_roll": (-0.14, 0.14),
        }
    elif profile == "wide_range":
        ranges = {
            "hip_pitch": (-0.90, 1.05),
            "knee_pitch": (0.0, 1.95),
            "ankle_pitch": (-0.75, 0.70),
            "hip_roll": (-0.55, 0.55),
            "ankle_roll": (-0.52, 0.52),
        }
    else:
        ranges = {
            "hip_pitch": (-0.62, 0.88),
            "knee_pitch": (0.0, 1.45),
            "ankle_pitch": (-0.48, 0.42),
            "hip_roll": (-0.38, 0.38),
            "ankle_roll": (-0.35, 0.35),
        }
    lower, upper = ranges[joint_name]
    effort = 320.0 if "hip" in joint_name else 260.0 if "knee" in joint_name else 160.0
    return MotionLimits(lower=lower, upper=upper, effort=effort, velocity=2.0)


def _wire_joints(model: ArticulatedObject, r: ResolvedRoboticLegConfig) -> None:
    damping = MotionProperties(damping=0.28, friction=0.10)
    if r.kinematic_topology == "spatial_5dof":
        model.articulation(
            "hip_roll",
            ArticulationType.REVOLUTE,
            parent="hip_mount",
            child="hip_roll_link",
            origin=Origin(),
            axis=(1.0, 0.0, 0.0),
            motion_limits=_limits(r.joint_limit_profile, "hip_roll"),
            motion_properties=damping,
        )
        model.articulation(
            "hip_pitch",
            ArticulationType.REVOLUTE,
            parent="hip_roll_link",
            child="thigh",
            origin=Origin(xyz=(0.0, 0.0, -0.085)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=_limits(r.joint_limit_profile, "hip_pitch"),
            motion_properties=damping,
        )
    else:
        model.articulation(
            "hip_pitch",
            ArticulationType.REVOLUTE,
            parent="hip_mount",
            child="thigh",
            origin=Origin(),
            axis=(0.0, 1.0, 0.0),
            motion_limits=_limits(r.joint_limit_profile, "hip_pitch"),
            motion_properties=damping,
        )
    model.articulation(
        "knee_pitch",
        ArticulationType.REVOLUTE,
        parent="thigh",
        child="shank",
        origin=Origin(xyz=(0.0, 0.0, -r.thigh_len)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=_limits(r.joint_limit_profile, "knee_pitch"),
        motion_properties=damping,
    )
    if r.kinematic_topology == "spatial_5dof":
        model.articulation(
            "ankle_pitch",
            ArticulationType.REVOLUTE,
            parent="shank",
            child="ankle_pitch_link",
            origin=Origin(xyz=(0.0, 0.0, -r.shank_len)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=_limits(r.joint_limit_profile, "ankle_pitch"),
            motion_properties=damping,
        )
        model.articulation(
            "ankle_roll",
            ArticulationType.REVOLUTE,
            parent="ankle_pitch_link",
            child="foot",
            origin=Origin(xyz=(0.0, 0.0, -0.115)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=_limits(r.joint_limit_profile, "ankle_roll"),
            motion_properties=damping,
        )
    else:
        model.articulation(
            "ankle_pitch",
            ArticulationType.REVOLUTE,
            parent="shank",
            child="foot",
            origin=Origin(xyz=(0.0, 0.0, -r.shank_len)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=_limits(r.joint_limit_profile, "ankle_pitch"),
            motion_properties=damping,
        )


def build_robotic_leg(
    config: RoboticLegConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or RoboticLegConfig())
    model = ArticulatedObject(name="robotic_leg", assets=assets)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    _build_hip_mount(model, r)
    if r.kinematic_topology == "spatial_5dof":
        _build_spatial_roll_link(model, r)
    _build_segment(model, part_name="thigh", length=r.thigh_len, r=r)
    _build_segment(model, part_name="shank", length=r.shank_len, r=r)
    if r.kinematic_topology == "spatial_5dof":
        _build_spatial_ankle_link(model, r)
    _build_foot(model, r)
    _wire_joints(model, r)
    return model


def build_seeded_robotic_leg(seed: int) -> ArticulatedObject:
    return build_robotic_leg(config_from_seed(seed))


def slot_choices_for_config(r: ResolvedRoboticLegConfig) -> list[tuple[str, str]]:
    return [
        ("kinematic_topology", r.kinematic_topology),
        ("hip_mount", r.hip_mount_module),
        ("segment_construction", r.segment_construction_module),
        ("joint_interface", r.joint_interface_module),
        ("foot_module", r.foot_module),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def _allow_pivot_overlaps(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedRoboticLegConfig
) -> None:
    pairs = [("hip_mount", "thigh"), ("thigh", "shank"), ("shank", "foot")]
    if r.kinematic_topology == "spatial_5dof":
        pairs = [
            ("hip_mount", "thigh"),
            ("hip_mount", "hip_roll_link"),
            ("hip_roll_link", "thigh"),
            ("thigh", "shank"),
            ("shank", "ankle_pitch_link"),
            ("ankle_pitch_link", "foot"),
        ]
    part_names = {part.name for part in model.parts}
    for parent, child in pairs:
        if parent in part_names and child in part_names:
            ctx.allow_overlap(
                model.get_part(parent),
                model.get_part(child),
                reason="captured robotic-leg pivot hardware intentionally nests shaft/barrel inside yoke or motor bore",
            )


def run_robotic_leg_tests(
    model: ArticulatedObject,
    config: RoboticLegConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    _allow_pivot_overlaps(ctx, model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    joint_names = {joint.name for joint in model.articulations}
    for required in ("hip_pitch", "knee_pitch", "ankle_pitch"):
        ctx.check(f"{required}_exists", required in joint_names, f"Missing {required}")
    if r.kinematic_topology == "spatial_5dof":
        ctx.check(
            "hip_roll_exists", "hip_roll" in joint_names, "spatial topology requires hip_roll"
        )
        ctx.check(
            "ankle_roll_exists", "ankle_roll" in joint_names, "spatial topology requires ankle_roll"
        )
    else:
        ctx.check("sagittal_joint_count", len([j for j in joint_names if j.endswith("pitch")]) == 3)

    knee = model.get_articulation("knee_pitch")
    limits = knee.motion_limits
    ctx.check(
        "knee_is_one_way",
        bool(limits and limits.lower >= -1e-6 and limits.upper > 0.4),
        f"knee limits should be one-way flexion, got {limits!r}",
    )
    ctx.check(
        "foot_is_terminal_part",
        any(part.name == "foot" for part in model.parts),
        "robotic_leg must terminate in a foot part",
    )

    return ctx.report()


__all__ = [
    "RoboticLegConfig",
    "ResolvedRoboticLegConfig",
    "config_from_seed",
    "slot_choices_for_seed",
    "build_robotic_leg",
    "build_seeded_robotic_leg",
    "resolve_config",
    "run_robotic_leg_tests",
]
