# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for `branching_tree_with_two_independent_rotary_branches`.

Implements
`articraft_template_authoring/specs_modular_v1/branching_tree_with_two_independent_rotary_branches.md`.

The category identity is exactly two independent rotary branch leaves carried by one
grounded support.  Procedural-first sampling applies to every seed including 0.
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
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True

SupportCarrier = Literal[
    "vertical_spine",
    "vertical_mast",
    "tower_stand",
    "ladder_frame",
    "trunk_y_tree",
    "pedestal_or_wall",
]
MountLayout = Literal[
    "staggered_vertical_opposed",
    "bilateral_same_height",
    "diagonal_quadrants",
    "forward_plus_side",
    "orthogonal_fork_plate",
]
JointAxisPolicy = Literal[
    "parallel_Y_pitch",
    "parallel_Z_yaw",
    "mirror_Y",
    "orthogonal_per_branch",
    "two_link_chain_axes",
]
BranchTopology = Literal[
    "single_rigid_branch",
    "two_link_chain",
    "hub_spoke",
    "cheek_arm",
    "bracket_carrier",
]
JointLimitStyle = Literal["compact", "medium", "wide"]
MaterialStyle = Literal["shop_steel", "dark_fixture", "blue_tooling", "warm_machined"]
FaceSide = Literal[
    "positive_x",
    "negative_x",
    "positive_y",
    "negative_y",
    "positive_z",
    "negative_z",
]

SUPPORT_CARRIERS: tuple[SupportCarrier, ...] = (
    "vertical_spine",
    "vertical_mast",
    "tower_stand",
    "ladder_frame",
    "trunk_y_tree",
    "pedestal_or_wall",
)
MOUNT_LAYOUTS: tuple[MountLayout, ...] = (
    "staggered_vertical_opposed",
    "bilateral_same_height",
    "diagonal_quadrants",
    "forward_plus_side",
    "orthogonal_fork_plate",
)
JOINT_AXIS_POLICIES: tuple[JointAxisPolicy, ...] = (
    "parallel_Y_pitch",
    "parallel_Z_yaw",
    "mirror_Y",
    "orthogonal_per_branch",
    "two_link_chain_axes",
)
BRANCH_TOPOLOGIES: tuple[BranchTopology, ...] = (
    "single_rigid_branch",
    "two_link_chain",
    "hub_spoke",
    "cheek_arm",
    "bracket_carrier",
)
JOINT_LIMIT_STYLES: tuple[JointLimitStyle, ...] = ("compact", "medium", "wide")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "shop_steel",
    "dark_fixture",
    "blue_tooling",
    "warm_machined",
)

LEGAL_MOUNTS: dict[SupportCarrier, tuple[MountLayout, ...]] = {
    "vertical_spine": (
        "staggered_vertical_opposed",
        "bilateral_same_height",
        "diagonal_quadrants",
    ),
    "vertical_mast": ("staggered_vertical_opposed", "forward_plus_side"),
    "tower_stand": ("staggered_vertical_opposed", "bilateral_same_height"),
    "ladder_frame": ("staggered_vertical_opposed",),
    "trunk_y_tree": ("bilateral_same_height",),
    "pedestal_or_wall": ("bilateral_same_height", "staggered_vertical_opposed"),
}

LEGAL_BRANCHES: dict[tuple[SupportCarrier, MountLayout], tuple[BranchTopology, ...]] = {
    ("vertical_spine", "staggered_vertical_opposed"): (
        "single_rigid_branch",
        "bracket_carrier",
        "two_link_chain",
    ),
    ("vertical_spine", "bilateral_same_height"): (
        "single_rigid_branch",
        "bracket_carrier",
        "two_link_chain",
    ),
    ("vertical_spine", "diagonal_quadrants"): ("single_rigid_branch", "bracket_carrier"),
    ("vertical_mast", "staggered_vertical_opposed"): ("single_rigid_branch", "hub_spoke"),
    ("vertical_mast", "forward_plus_side"): ("single_rigid_branch", "hub_spoke"),
    ("tower_stand", "staggered_vertical_opposed"): ("single_rigid_branch",),
    ("tower_stand", "bilateral_same_height"): ("single_rigid_branch",),
    ("ladder_frame", "staggered_vertical_opposed"): ("single_rigid_branch", "cheek_arm"),
    ("trunk_y_tree", "bilateral_same_height"): ("single_rigid_branch", "two_link_chain"),
    ("pedestal_or_wall", "bilateral_same_height"): ("single_rigid_branch",),
    ("pedestal_or_wall", "staggered_vertical_opposed"): ("single_rigid_branch",),
}

LEGAL_AXES: dict[BranchTopology, tuple[JointAxisPolicy, ...]] = {
    "single_rigid_branch": (
        "parallel_Y_pitch",
        "parallel_Z_yaw",
        "mirror_Y",
        "orthogonal_per_branch",
    ),
    "two_link_chain": ("two_link_chain_axes",),
    "hub_spoke": ("mirror_Y", "parallel_Y_pitch"),
    "cheek_arm": ("mirror_Y",),
    "bracket_carrier": ("parallel_Y_pitch", "mirror_Y"),
}

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "shop_steel": {
        "support": (0.22, 0.24, 0.27, 1.0),
        "support_dark": (0.14, 0.15, 0.17, 1.0),
        "bearing": (0.66, 0.70, 0.73, 1.0),
        "branch": (0.34, 0.38, 0.42, 1.0),
        "branch_alt": (0.24, 0.30, 0.36, 1.0),
        "terminal": (0.76, 0.78, 0.78, 1.0),
        "accent": (0.90, 0.58, 0.14, 1.0),
    },
    "dark_fixture": {
        "support": (0.16, 0.17, 0.18, 1.0),
        "support_dark": (0.055, 0.058, 0.062, 1.0),
        "bearing": (0.42, 0.44, 0.46, 1.0),
        "branch": (0.62, 0.64, 0.65, 1.0),
        "branch_alt": (0.44, 0.48, 0.50, 1.0),
        "terminal": (0.78, 0.80, 0.80, 1.0),
        "accent": (0.86, 0.68, 0.16, 1.0),
    },
    "blue_tooling": {
        "support": (0.16, 0.23, 0.32, 1.0),
        "support_dark": (0.06, 0.10, 0.16, 1.0),
        "bearing": (0.60, 0.62, 0.64, 1.0),
        "branch": (0.08, 0.30, 0.56, 1.0),
        "branch_alt": (0.52, 0.56, 0.58, 1.0),
        "terminal": (0.82, 0.84, 0.82, 1.0),
        "accent": (0.93, 0.45, 0.12, 1.0),
    },
    "warm_machined": {
        "support": (0.43, 0.35, 0.22, 1.0),
        "support_dark": (0.18, 0.14, 0.09, 1.0),
        "bearing": (0.74, 0.62, 0.36, 1.0),
        "branch": (0.42, 0.39, 0.32, 1.0),
        "branch_alt": (0.58, 0.50, 0.34, 1.0),
        "terminal": (0.82, 0.76, 0.62, 1.0),
        "accent": (0.25, 0.36, 0.48, 1.0),
    },
}


@dataclass(frozen=True)
class BranchingTreeWithTwoIndependentRotaryBranchesConfig:
    support_carrier: SupportCarrier | None = None
    mount_layout: MountLayout | None = None
    joint_axis_policy: JointAxisPolicy | None = None
    branch_topology: BranchTopology | None = None
    station_spacing_scale: float = 1.0
    arm_reach_scale: float = 1.0
    joint_limit_style: JointLimitStyle = "medium"
    material_style: MaterialStyle = "shop_steel"
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["shop_steel"])
    )


@dataclass(frozen=True)
class ResolvedBranchingTreeWithTwoIndependentRotaryBranchesConfig:
    support_carrier: SupportCarrier
    mount_layout: MountLayout
    joint_axis_policy: JointAxisPolicy
    branch_topology: BranchTopology
    station_spacing_scale: float
    arm_reach_scale: float
    joint_limit_style: JointLimitStyle
    material_style: MaterialStyle
    palette: dict[str, tuple[float, float, float, float]]
    branch_count: int = 2


@dataclass
class _Station:
    name: str
    origin: tuple[float, float, float]
    axis: tuple[float, float, float]
    parent_part: str
    parent_visual: str
    parent_face_side: FaceSide
    child_face_side: FaceSide
    child_hub_visual: str
    arm_sign: int
    role: str
    parent_mate_depth: float = 0.018


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _axis_rpy(axis: str) -> tuple[float, float, float]:
    if axis == "x":
        return (0.0, math.pi / 2.0, 0.0)
    if axis == "y":
        return (math.pi / 2.0, 0.0, 0.0)
    return (0.0, 0.0, 0.0)


def _normal(face_side: FaceSide) -> tuple[float, float, float]:
    axis = face_side[-1]
    sign = 1.0 if face_side.startswith("positive") else -1.0
    if axis == "x":
        return (sign, 0.0, 0.0)
    if axis == "y":
        return (0.0, sign, 0.0)
    return (0.0, 0.0, sign)


def _add_vec(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _mul_vec(v: tuple[float, float, float], scalar: float) -> tuple[float, float, float]:
    return (v[0] * scalar, v[1] * scalar, v[2] * scalar)


def _box_visual(
    part,
    size: tuple[float, float, float],
    center: tuple[float, float, float],
    *,
    material: str,
    name: str,
    rpy: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    part.visual(Box(size), origin=Origin(xyz=center, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cylinder_axis(
    part,
    *,
    axis: str,
    radius: float,
    length: float,
    center: tuple[float, float, float],
    material: str,
    name: str,
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=center, rpy=_axis_rpy(axis)),
        material=material,
        name=name, material_class_id="metal.stainless_matte",
    )


def _socket_box_center(
    origin: tuple[float, float, float], face_side: FaceSide, thickness: float
) -> tuple[float, float, float]:
    return _add_vec(origin, _mul_vec(_normal(face_side), -0.5 * thickness))


def _add_socket(
    support,
    *,
    station: str,
    origin: tuple[float, float, float],
    face_side: FaceSide,
    size: tuple[float, float, float],
    material: str,
) -> str:
    visual_name = f"{station}_socket"
    axis = face_side[-1]
    thickness = {"x": size[0], "y": size[1], "z": size[2]}[axis]
    _box_visual(
        support,
        size,
        _socket_box_center(origin, face_side, thickness),
        material=material,
        name=visual_name,
    )
    return visual_name


def _add_y_hinge_socket(
    support,
    *,
    station: str,
    origin: tuple[float, float, float],
    material: str,
) -> str:
    visual_name = f"{station}_socket"
    size = (0.040, 0.030, 0.040)
    center = (origin[0], origin[1] - size[1] * 0.5, origin[2])
    _box_visual(support, size, center, material=material, name=visual_name)
    return visual_name


def _add_z_hinge_socket(
    support,
    *,
    station: str,
    origin: tuple[float, float, float],
    material: str,
) -> str:
    visual_name = f"{station}_socket"
    size = (0.040, 0.040, 0.030)
    center = (origin[0], origin[1], origin[2] - size[2] * 0.5)
    _box_visual(support, size, center, material=material, name=visual_name)
    return visual_name


def _motion_limits(style: JointLimitStyle, index: int) -> MotionLimits:
    ranges = {
        "compact": (-0.45, 0.55, 1.0),
        "medium": (-0.75, 0.85, 1.4),
        "wide": (-1.05, 1.10, 1.8),
    }
    lower, upper, velocity = ranges[style]
    offset = index * 0.05
    return MotionLimits(
        lower=lower - offset,
        upper=upper + offset,
        effort=10.0 + 3.0 * index,
        velocity=velocity,
    )


def _legal_axes_for_branches(
    branches: tuple[BranchTopology, ...],
) -> tuple[JointAxisPolicy, ...]:
    seen: list[JointAxisPolicy] = []
    for branch in branches:
        for axis in LEGAL_AXES[branch]:
            if axis not in seen:
                seen.append(axis)
    return tuple(seen)


def config_from_seed(seed: int) -> BranchingTreeWithTwoIndependentRotaryBranchesConfig:
    rng = random.Random(seed)
    support = rng.choice(SUPPORT_CARRIERS)
    mount = rng.choice(LEGAL_MOUNTS[support])
    branches = LEGAL_BRANCHES[(support, mount)]
    legal_axes = _legal_axes_for_branches(branches)
    axis = rng.choice(legal_axes)
    compatible = tuple(b for b in branches if axis in LEGAL_AXES[b])
    branch = rng.choice(compatible)
    return BranchingTreeWithTwoIndependentRotaryBranchesConfig(
        support_carrier=support,
        mount_layout=mount,
        joint_axis_policy=axis,
        branch_topology=branch,
        station_spacing_scale=rng.uniform(0.85, 1.20),
        arm_reach_scale=rng.uniform(0.80, 1.25),
        joint_limit_style=rng.choice(JOINT_LIMIT_STYLES),
        material_style=rng.choice(MATERIAL_STYLES),
    )


def resolve_config(
    config: BranchingTreeWithTwoIndependentRotaryBranchesConfig,
) -> ResolvedBranchingTreeWithTwoIndependentRotaryBranchesConfig:
    support = config.support_carrier or SUPPORT_CARRIERS[0]
    if support not in SUPPORT_CARRIERS:
        raise ValueError(f"Unsupported support_carrier: {support!r}")

    legal_mounts = LEGAL_MOUNTS[support]
    mount = config.mount_layout or legal_mounts[0]
    if mount not in legal_mounts:
        mount = legal_mounts[0]

    legal_branches = LEGAL_BRANCHES[(support, mount)]
    branch = config.branch_topology or legal_branches[0]
    if branch not in legal_branches:
        branch = legal_branches[0]

    legal_axes = [a for a in LEGAL_AXES[branch] if a in _legal_axes_for_branches(legal_branches)]
    axis = config.joint_axis_policy or (legal_axes[0] if legal_axes else LEGAL_AXES[branch][0])
    if axis not in legal_axes:
        axis = legal_axes[0] if legal_axes else LEGAL_AXES[branch][0]

    limit_style = config.joint_limit_style
    if limit_style not in JOINT_LIMIT_STYLES:
        raise ValueError(f"Unsupported joint_limit_style: {limit_style!r}")
    material_style = config.material_style
    if material_style not in MATERIAL_STYLES:
        raise ValueError(f"Unsupported material_style: {material_style!r}")

    return ResolvedBranchingTreeWithTwoIndependentRotaryBranchesConfig(
        support_carrier=support,
        mount_layout=mount,
        joint_axis_policy=axis,
        branch_topology=branch,
        station_spacing_scale=_clamp(config.station_spacing_scale, 0.85, 1.20),
        arm_reach_scale=_clamp(config.arm_reach_scale, 0.80, 1.25),
        joint_limit_style=limit_style,
        material_style=material_style,
        palette=dict(config.palette or PALETTES[material_style]),
    )


def _register_materials(
    model: ArticulatedObject,
    r: ResolvedBranchingTreeWithTwoIndependentRotaryBranchesConfig,
) -> None:
    palette = dict(PALETTES[r.material_style])
    palette.update(r.palette)
    for name, rgba in palette.items():
        model.material(name, rgba=rgba)


def _station_axes(policy: JointAxisPolicy, index: int) -> tuple[float, float, float]:
    if policy == "parallel_Y_pitch":
        return (0.0, 1.0, 0.0)
    if policy == "parallel_Z_yaw":
        return (0.0, 0.0, 1.0)
    if policy == "mirror_Y":
        return (0.0, -1.0 if index == 0 else 1.0, 0.0)
    if policy == "orthogonal_per_branch":
        return (0.0, 1.0, 0.0) if index == 0 else (1.0, 0.0, 0.0)
    return (0.0, 1.0, 0.0)


def _resolve_two_stations(
    r: ResolvedBranchingTreeWithTwoIndependentRotaryBranchesConfig,
) -> list[_Station]:
    spacing = r.station_spacing_scale
    hub_x = 0.100 * spacing
    hub_z_hi = 0.31 * spacing
    hub_z_lo = 0.16 * spacing
    hub_z_mid = 0.235 * spacing
    lateral = 0.110 * spacing

    mount = r.mount_layout
    if mount == "staggered_vertical_opposed":
        specs = (
            ("upper_branch", (hub_x, 0.0, hub_z_hi), 1, "upper"),
            ("lower_branch", (-hub_x, 0.0, hub_z_lo), -1, "lower"),
        )
    elif mount == "bilateral_same_height":
        specs = (
            ("left_branch", (-hub_x, 0.0, hub_z_mid), -1, "left"),
            ("right_branch", (hub_x, 0.0, hub_z_mid), 1, "right"),
        )
    elif mount == "diagonal_quadrants":
        specs = (
            ("upper_left_branch", (-lateral, lateral, hub_z_hi), -1, "upper_left"),
            ("lower_right_branch", (lateral, -lateral, hub_z_lo), 1, "lower_right"),
        )
    elif mount == "forward_plus_side":
        specs = (
            ("forward_branch", (0.0, lateral, hub_z_mid), 1, "forward"),
            ("side_branch", (hub_x, 0.0, hub_z_lo), 1, "side"),
        )
    else:
        specs = (
            ("fork_branch", (0.0, lateral, hub_z_hi), 1, "fork"),
            ("plate_branch", (0.0, -lateral * 0.6, hub_z_lo), -1, "plate"),
        )

    stations: list[_Station] = []
    for index, (name, origin, arm_sign, role) in enumerate(specs):
        axis = _station_axes(r.joint_axis_policy, index)
        if r.joint_axis_policy == "two_link_chain_axes":
            axis = (0.0, 1.0, 0.0)
        if axis[1] > 0.0:
            parent_face: FaceSide = "positive_y"
            child_face: FaceSide = "negative_y"
        elif axis[1] < 0.0:
            parent_face = "negative_y"
            child_face = "positive_y"
        elif axis[2] != 0.0:
            parent_face = "positive_z"
            child_face = "negative_z"
        else:
            parent_face = "positive_x" if arm_sign > 0 else "negative_x"
            child_face = "negative_x" if arm_sign > 0 else "positive_x"
        stations.append(
            _Station(
                name=name,
                origin=origin,
                axis=axis,
                parent_part="support",
                parent_visual=f"{role}_station_socket",
                parent_face_side=parent_face,
                child_face_side=child_face,
                child_hub_visual=f"{name}_hub",
                arm_sign=arm_sign,
                role=role,
            )
        )
    return stations


def _build_vertical_spine(support, r, stations: list[_Station]) -> None:
    base_size = (0.18, 0.12, 0.02)
    spine_size = (0.05, 0.08, 0.40)
    root_size = (0.046, 0.036, 0.042)

    _box_visual(
        support,
        base_size,
        (0.0, 0.0, base_size[2] / 2.0),
        material="support",
        name="base_plate",
    )
    _box_visual(
        support,
        spine_size,
        (0.0, 0.0, base_size[2] + spine_size[2] / 2.0),
        material="support",
        name="spine_column",
    )
    for station in stations:
        ox, oy, oz = station.origin
        x_sign = 1.0 if ox >= 0.0 else -1.0
        _box_visual(
            support,
            root_size,
            (0.025 * x_sign, oy * 0.15, oz),
            material="support_dark",
            name=f"{station.role}_root",
        )
        if station.axis[2] != 0.0:
            _box_visual(
                support,
                (max(abs(ox), 0.040) + 0.050, max(abs(oy), 0.040) + 0.050, 0.032),
                (ox * 0.45, oy * 0.45, oz - 0.018),
                material="support_dark",
                name=f"{station.role}_hinge_bridge",
            )
            station_socket = _add_z_hinge_socket(
                support,
                station=station.role,
                origin=station.origin,
                material="bearing",
            )
            station.parent_visual = station_socket
            station.parent_face_side = "positive_z"
            station.child_face_side = "negative_z"
            station.parent_mate_depth = 0.0
            continue
        _box_visual(
            support,
            (max(abs(ox), 0.040) + 0.050, max(abs(oy), 0.040) + 0.050, 0.030),
            (ox * 0.45, oy * 0.45, oz - 0.010),
            material="support_dark",
            name=f"{station.role}_hinge_bridge",
        )
        station_socket = _add_y_hinge_socket(
            support,
            station=station.role,
            origin=station.origin,
            material="bearing",
        )
        station.parent_visual = station_socket
        station.parent_face_side = "positive_y"
        station.child_face_side = "negative_y"
        station.parent_mate_depth = 0.0


def _build_vertical_mast(support, r, stations: list[_Station]) -> None:
    _cylinder_axis(
        support,
        axis="z",
        radius=0.150,
        length=0.030,
        center=(0.0, 0.0, 0.015),
        material="support_dark",
        name="base_disc",
    )
    _cylinder_axis(
        support,
        axis="z",
        radius=0.055,
        length=0.520,
        center=(0.0, 0.0, 0.290),
        material="support",
        name="mast_shaft",
    )
    for station in stations:
        ox, oy, oz = station.origin
        _box_visual(
            support,
            (0.080, 0.050, 0.040),
            (ox * 0.45 if abs(ox) > 0.01 else 0.0, oy * 0.45 if abs(oy) > 0.01 else 0.0, oz),
            material="support_dark",
            name=f"{station.role}_mast_collar",
        )
        if r.branch_topology == "hub_spoke":
            reach = max(abs(ox), abs(oy), 0.06)
            if abs(oy) > abs(ox):
                ped_size = (0.060, reach * 0.96, 0.040)
                ped_center = (0.0, math.copysign(reach * 0.48, oy), oz)
            else:
                ped_size = (reach * 0.96, 0.060, 0.040)
                ped_center = (math.copysign(reach * 0.48, ox), 0.0, oz)
            _box_visual(
                support,
                ped_size,
                ped_center,
                material="support_dark",
                name=f"{station.role}_hub_pedestal",
            )
            station.parent_mate_depth = 0.0
            continue
        if station.axis[2] != 0.0:
            _box_visual(
                support,
                (max(abs(ox), 0.050) + 0.060, max(abs(oy), 0.050) + 0.060, 0.038),
                (ox * 0.5, oy * 0.5, oz - 0.022),
                material="support_dark",
                name=f"{station.role}_mast_bridge",
            )
            station_socket = _add_z_hinge_socket(
                support,
                station=station.role,
                origin=station.origin,
                material="bearing",
            )
            station.parent_visual = station_socket
            station.parent_face_side = "positive_z"
            station.child_face_side = "negative_z"
            station.parent_mate_depth = 0.0
            continue
        if abs(oy) > abs(ox):
            _box_visual(
                support,
                (0.060, abs(oy) + 0.050, 0.040),
                (0.0, oy * 0.5, oz),
                material="support_dark",
                name=f"{station.role}_mast_bridge",
            )
        else:
            _box_visual(
                support,
                (abs(ox) + 0.050, 0.060, 0.040),
                (ox * 0.5, 0.0, oz),
                material="support_dark",
                name=f"{station.role}_mast_bridge",
            )
        station_socket = _add_y_hinge_socket(
            support,
            station=station.role,
            origin=station.origin,
            material="bearing",
        )
        station.parent_visual = station_socket
        station.parent_face_side = "positive_y"
        station.child_face_side = "negative_y"
        station.parent_mate_depth = 0.0


def _build_tower_stand(support, r, stations: list[_Station]) -> None:
    _box_visual(
        support,
        (0.280, 0.220, 0.040),
        (0.0, 0.0, 0.020),
        material="support_dark",
        name="heavy_base",
    )
    _cylinder_axis(
        support,
        axis="z",
        radius=0.060,
        length=0.360,
        center=(0.0, 0.0, 0.220),
        material="support",
        name="tower_collar",
    )
    for station in stations:
        oz = station.origin[2]
        _box_visual(
            support,
            (abs(station.origin[0]) + 0.060, 0.055, 0.040),
            (station.origin[0] * 0.5, 0.0, oz - 0.022),
            material="support_dark",
            name=f"{station.role}_tower_bridge",
        )
        station_socket = _add_z_hinge_socket(
            support,
            station=station.role,
            origin=station.origin,
            material="bearing",
        )
        station.parent_visual = station_socket
        station.parent_face_side = "positive_z"
        station.child_face_side = "negative_z"
        station.parent_mate_depth = 0.0


def _build_ladder_frame(support, r, stations: list[_Station]) -> None:
    _box_visual(
        support,
        (0.360, 0.040, 0.030),
        (0.0, 0.0, 0.015),
        material="support_dark",
        name="foot_rail",
    )
    for x in (-0.150, 0.150):
        _box_visual(
            support,
            (0.030, 0.030, 0.520),
            (x, 0.0, 0.275),
            material="support",
            name=f"upright_{'left' if x < 0 else 'right'}",
        )
    for z in (0.120, 0.240, 0.360, 0.480):
        _box_visual(
            support,
            (0.300, 0.022, 0.018),
            (0.0, 0.0, z),
            material="support_dark",
            name=f"rung_{int(z * 100)}",
        )
    for station in stations:
        upright_x = -0.150 if station.origin[0] <= 0.0 else 0.150
        cheek_half = 0.020
        if station.origin[0] <= 0.0:
            cheek_center_x = upright_x - 0.020
            joint_x = cheek_center_x - cheek_half
        else:
            cheek_center_x = upright_x + 0.020
            joint_x = cheek_center_x + cheek_half
        z = station.origin[2]
        station.origin = (joint_x, 0.0, z)
        _box_visual(
            support,
            (0.040, 0.070, 0.050),
            (cheek_center_x, -0.035, z),
            material="bearing",
            name=f"{station.role}_cheek_mount",
        )
        station.parent_visual = f"{station.role}_cheek_mount"
        station.parent_face_side = "positive_y"
        station.child_face_side = "negative_y"
        station.parent_mate_depth = 0.0


def _build_trunk_y_tree(support, r, stations: list[_Station]) -> None:
    _box_visual(
        support,
        (0.200, 0.120, 0.030),
        (0.0, 0.0, 0.015),
        material="support_dark",
        name="trunk_base",
    )
    _box_visual(
        support,
        (0.060, 0.060, 0.220),
        (0.0, 0.0, 0.140),
        material="support",
        name="trunk_stem",
    )
    for station in stations:
        ox, _, oz = station.origin
        reach = abs(ox) + 0.030
        cx = ox * 0.5
        cz = oz - 0.012
        _box_visual(
            support,
            (reach, 0.040, 0.030),
            (cx, 0.0, cz),
            material="support_dark",
            name=f"{station.role}_y_bar",
        )
        station_socket = _add_z_hinge_socket(
            support,
            station=station.role,
            origin=station.origin,
            material="bearing",
        )
        station.parent_visual = station_socket
        station.parent_face_side = "positive_z"
        station.child_face_side = "negative_z"
        station.parent_mate_depth = 0.0


def _build_pedestal_or_wall(support, r, stations: list[_Station]) -> None:
    if r.mount_layout == "bilateral_same_height":
        _box_visual(
            support,
            (0.160, 0.160, 0.050),
            (0.0, 0.0, 0.025),
            material="support_dark",
            name="pedestal_foot",
        )
        _box_visual(
            support,
            (0.080, 0.080, 0.280),
            (0.0, 0.0, 0.190),
            material="support",
            name="pedestal_column",
        )
    else:
        _box_visual(
            support,
            (0.040, 0.420, 0.560),
            (0.0, 0.0, 0.280),
            material="support",
            name="wall_backplate",
        )
        _box_visual(
            support,
            (0.055, 0.070, 0.500),
            (0.048, 0.0, 0.300),
            material="support_dark",
            name="wall_mount_spine",
        )
    for station in stations:
        ox, oy, oz = station.origin
        if r.mount_layout == "bilateral_same_height":
            pod_center = (ox, oy, oz)
            bridge_center = (ox * 0.5, oy * 0.5, oz - 0.030)
            bridge_size = (0.060, 0.070, 0.040)
        else:
            pod_center = (0.078, oy * 0.15, oz)
            bridge_center = ((0.078 + ox) * 0.5, oy * 0.15, oz - 0.018)
            bridge_size = (max(abs(ox), 0.050) + 0.050, 0.055, 0.032)
        _box_visual(
            support,
            (0.070, 0.090, 0.045),
            pod_center,
            material="support_dark",
            name=f"{station.role}_clamp_pod",
        )
        _box_visual(
            support,
            bridge_size,
            bridge_center,
            material="support_dark",
            name=f"{station.role}_clamp_bridge",
        )
        station_socket = _add_z_hinge_socket(
            support,
            station=station.role,
            origin=station.origin,
            material="bearing",
        )
        station.parent_visual = station_socket
        station.parent_face_side = "positive_z"
        station.child_face_side = "negative_z"
        station.parent_mate_depth = 0.0


def _build_support_carrier(
    model: ArticulatedObject,
    r: ResolvedBranchingTreeWithTwoIndependentRotaryBranchesConfig,
    stations: list[_Station],
) -> None:
    support = model.part("support")
    builders = {
        "vertical_spine": _build_vertical_spine,
        "vertical_mast": _build_vertical_mast,
        "tower_stand": _build_tower_stand,
        "ladder_frame": _build_ladder_frame,
        "trunk_y_tree": _build_trunk_y_tree,
        "pedestal_or_wall": _build_pedestal_or_wall,
    }
    builders[r.support_carrier](support, r, stations)


def _hub_center_for_mating(station: _Station, hub_length: float) -> tuple[float, float, float]:
    half = 0.5 * hub_length
    depth = station.parent_mate_depth if station.parent_part == "support" else 0.0
    if station.child_face_side == "negative_y":
        return (0.0, depth + half, 0.0)
    if station.child_face_side == "positive_y":
        return (0.0, -(depth + half), 0.0)
    if station.child_face_side == "negative_z":
        return (0.0, 0.0, depth + half)
    if station.child_face_side == "negative_x":
        return (depth + half, 0.0, 0.0)
    if station.child_face_side == "positive_x":
        return (-(depth + half), 0.0, 0.0)
    return (0.0, 0.0, 0.0)


def _joint_origin_for_parent(station: _Station) -> tuple[float, float, float]:
    if station.parent_part == "support":
        return station.origin
    if station.parent_face_side == "positive_x":
        return (station.parent_mate_depth, 0.0, 0.0)
    if station.parent_face_side == "negative_x":
        return (-station.parent_mate_depth, 0.0, 0.0)
    if station.parent_face_side == "positive_y":
        return (0.0, station.parent_mate_depth, 0.0)
    if station.parent_face_side == "negative_y":
        return (0.0, -station.parent_mate_depth, 0.0)
    if station.parent_face_side == "positive_z":
        return (0.0, 0.0, station.parent_mate_depth)
    return (0.0, 0.0, 0.0)


def _hub_axis_from_station(station: _Station) -> str:
    if "x" in station.child_face_side:
        return "x"
    if "z" in station.child_face_side:
        return "z"
    return "y"


def _add_single_branch_visuals(part, station: _Station, reach: float) -> None:
    hub_r = 0.018
    hub_l = 0.024
    hub_axis = _hub_axis_from_station(station)
    hub_center = _hub_center_for_mating(station, hub_l)
    _cylinder_axis(
        part,
        axis=hub_axis,
        radius=hub_r,
        length=hub_l,
        center=hub_center,
        material="bearing",
        name=station.child_hub_visual,
    )
    if hub_center != (0.0, 0.0, 0.0):
        neck_size = (0.022, 0.022, 0.022) if hub_axis == "y" else (0.022, 0.022, 0.022)
        _box_visual(
            part,
            neck_size,
            (hub_center[0] * 0.5, hub_center[1] * 0.5, hub_center[2] * 0.5),
            material="branch",
            name=f"{station.name}_root_neck",
        )
    beam_len = reach * 0.90
    if hub_axis == "x":
        beam_x = hub_center[0] + hub_r + beam_len * 0.5 - 0.008
    else:
        beam_x = hub_center[0] + station.arm_sign * (hub_r + beam_len * 0.5 - 0.008)
    beam_y = hub_center[1]
    beam_z = hub_center[2]
    _box_visual(
        part,
        (beam_len, 0.020, 0.024),
        (beam_x, beam_y, beam_z),
        material="branch",
        name=f"{station.name}_beam",
    )
    pad_x = beam_x + station.arm_sign * (beam_len * 0.5 + 0.016)
    _box_visual(
        part,
        (0.036, 0.060, 0.012),
        (pad_x, beam_y, beam_z),
        material="terminal",
        name=f"{station.name}_pad",
    )


def _add_bracket_fixed(
    model: ArticulatedObject,
    station: _Station,
) -> str:
    bracket_name = f"{station.role}_bracket"
    bracket = model.part(bracket_name)
    sign = float(station.arm_sign)
    _box_visual(
        bracket,
        (0.050, 0.034, 0.032),
        (sign * 0.030, 0.0, 0.0),
        material="support_dark",
        name=f"{station.role}_bracket_body",
    )
    _box_visual(
        bracket,
        (0.030, 0.006, 0.052),
        (sign * 0.060, 0.0, 0.0),
        material="bearing",
        name=f"{station.role}_bracket_plate",
    )
    support = model.get_part("support")
    model.articulation(
        f"support_to_{bracket_name}",
        ArticulationType.FIXED,
        parent=support,
        child=bracket,
        origin=Origin(xyz=station.origin),
    )
    station.parent_part = bracket_name
    station.parent_visual = f"{station.role}_bracket_plate"
    station.parent_face_side = "positive_x" if sign > 0.0 else "negative_x"
    station.child_face_side = "negative_x" if sign > 0.0 else "positive_x"
    station.parent_mate_depth = 0.075
    return bracket_name


def _add_hub_fixed(model: ArticulatedObject, station: _Station) -> str:
    hub_name = f"{station.role}_hub_carrier"
    hub = model.part(hub_name)
    _box_visual(
        hub,
        (0.060, 0.050, 0.040),
        (0.0, 0.0, 0.0),
        material="support_dark",
        name=f"{station.role}_hub_back",
    )
    _cylinder_axis(
        hub,
        axis="z",
        radius=0.030,
        length=0.026,
        center=(0.0, 0.0, 0.028),
        material="bearing",
        name=f"{station.role}_hub_barrel",
    )
    support = model.get_part("support")
    pedestal_name = f"{station.role}_hub_pedestal"
    try:
        support.get_visual(pedestal_name)
    except Exception:
        _box_visual(
            support,
            (0.070, 0.050, 0.040),
            station.origin,
            material="support_dark",
            name=pedestal_name,
        )
    model.articulation(
        f"support_to_{hub_name}",
        ArticulationType.FIXED,
        parent=support,
        child=hub,
        origin=Origin(xyz=station.origin),
    )
    station.parent_part = hub_name
    station.parent_visual = f"{station.role}_hub_barrel"
    station.parent_face_side = "positive_z"
    station.child_face_side = "negative_z"
    station.child_hub_visual = f"{station.name}_spoke_hub"
    station.parent_mate_depth = 0.041
    return hub_name


def _add_cheek_fixed(model: ArticulatedObject, station: _Station) -> str:
    cheek_name = f"{station.role}_cheek"
    cheek = model.part(cheek_name)
    _box_visual(
        cheek,
        (0.030, 0.070, 0.050),
        (0.0, -0.035, 0.0),
        material="bearing",
        name=f"{station.role}_cheek_plate",
    )
    support = model.get_part("support")
    model.articulation(
        f"support_to_{cheek_name}",
        ArticulationType.FIXED,
        parent=support,
        child=cheek,
        origin=Origin(xyz=station.origin),
    )
    station.parent_part = cheek_name
    station.parent_visual = f"{station.role}_cheek_plate"
    station.parent_face_side = "positive_y"
    station.child_face_side = "negative_y"
    station.child_hub_visual = f"{station.name}_arm_barrel"
    station.parent_mate_depth = 0.0
    return cheek_name


def _build_branch_topology(
    model: ArticulatedObject,
    r: ResolvedBranchingTreeWithTwoIndependentRotaryBranchesConfig,
    station: _Station,
    index: int,
) -> list[str]:
    reach = (0.090 + 0.010 * index) * r.arm_reach_scale
    leaf_parts: list[str] = []

    if r.branch_topology == "bracket_carrier":
        _add_bracket_fixed(model, station)
    elif r.branch_topology == "hub_spoke":
        _add_hub_fixed(model, station)
    elif r.branch_topology == "cheek_arm":
        _add_cheek_fixed(model, station)

    if r.branch_topology == "two_link_chain":
        upper_name = f"{station.name}_upper"
        forearm_name = f"{station.name}_forearm"
        upper = model.part(upper_name)
        forearm = model.part(forearm_name)
        shoulder_hub_len = 0.052
        shoulder_hub_r = 0.026
        shoulder_center = _hub_center_for_mating(station, shoulder_hub_len)
        _cylinder_axis(
            upper,
            axis="y",
            radius=shoulder_hub_r,
            length=shoulder_hub_len,
            center=shoulder_center,
            material="bearing",
            name=f"{station.name}_shoulder_hub",
        )
        upper_beam_len = 0.082
        upper_beam_x = shoulder_center[0] + station.arm_sign * (
            shoulder_hub_r + upper_beam_len * 0.5
        )
        _box_visual(
            upper,
            (upper_beam_len, 0.034, 0.046),
            (upper_beam_x, shoulder_center[1], shoulder_center[2]),
            material="branch",
            name=f"{station.name}_upper_beam",
        )
        elbow_boss_x = shoulder_center[0] + station.arm_sign * (
            shoulder_hub_r + upper_beam_len + 0.010
        )
        _box_visual(
            upper,
            (0.020, 0.030, 0.042),
            (elbow_boss_x, shoulder_center[1], shoulder_center[2]),
            material="branch",
            name=f"{station.name}_elbow_boss",
        )
        elbow_hub_r = 0.020
        elbow_hub_len = 0.040
        elbow_origin = (
            station.arm_sign * (shoulder_hub_r + upper_beam_len + elbow_hub_r),
            0.0,
            0.0,
        )
        _cylinder_axis(
            forearm,
            axis="y",
            radius=elbow_hub_r,
            length=elbow_hub_len,
            center=(0.0, 0.0, 0.0),
            material="bearing",
            name=f"{station.name}_elbow_hub",
        )
        forearm_beam_len = 0.108
        _box_visual(
            forearm,
            (forearm_beam_len, 0.032, 0.040),
            (station.arm_sign * (elbow_hub_r + forearm_beam_len * 0.5), 0.0, 0.0),
            material="branch_alt",
            name=f"{station.name}_forearm_beam",
        )
        parent = model.get_part(station.parent_part)
        shoulder_origin = _joint_origin_for_parent(station)
        model.articulation(
            f"{station.parent_part}_to_{upper_name}",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=upper,
            origin=Origin(xyz=shoulder_origin),
            axis=station.axis,
            motion_limits=_motion_limits(r.joint_limit_style, index),
            mating=MatingContract(
                station.parent_visual,
                station.parent_face_side,
                f"{station.name}_shoulder_hub",
                station.child_face_side,
                contact_tol=0.002,
            ),
        )
        model.articulation(
            f"{upper_name}_to_{forearm_name}",
            ArticulationType.REVOLUTE,
            parent=upper,
            child=forearm,
            origin=Origin(xyz=elbow_origin),
            axis=(0.0, 0.0, 1.0),
            motion_limits=_motion_limits(r.joint_limit_style, index + 2),
        )
        leaf_parts.append(forearm_name)
        return leaf_parts

    if r.branch_topology == "hub_spoke":
        part = model.part(station.name)
        spoke_hub_len = 0.022
        _cylinder_axis(
            part,
            axis="z",
            radius=0.018,
            length=spoke_hub_len,
            center=(0.0, 0.0, spoke_hub_len * 0.5),
            material="bearing",
            name=station.child_hub_visual,
        )
        spoke_z = spoke_hub_len * 0.5
        _box_visual(
            part,
            (reach, 0.028, 0.022),
            (station.arm_sign * (reach / 2.0 + 0.020), 0.0, spoke_z + 0.006),
            material="branch",
            name=f"{station.name}_spoke",
        )
        _box_visual(
            part,
            (0.024, 0.020, 0.018),
            (station.arm_sign * 0.012, 0.0, spoke_z * 0.5),
            material="branch",
            name=f"{station.name}_spoke_root",
        )
    elif r.branch_topology == "cheek_arm":
        part = model.part(station.name)
        arm_hub_len = 0.040
        arm_center = _hub_center_for_mating(station, arm_hub_len)
        _cylinder_axis(
            part,
            axis="y",
            radius=0.020,
            length=arm_hub_len,
            center=arm_center,
            material="bearing",
            name=station.child_hub_visual,
        )
        _box_visual(
            part,
            (reach, 0.030, 0.034),
            (
                station.arm_sign * (reach / 2.0 + 0.022) + arm_center[0],
                arm_center[1],
                arm_center[2],
            ),
            material="branch",
            name=f"{station.name}_arm_beam",
        )
    else:
        part = model.part(station.name)
        _add_single_branch_visuals(part, station, reach)

    parent = model.get_part(station.parent_part)
    joint_origin = _joint_origin_for_parent(station)
    if r.branch_topology == "hub_spoke":
        joint_origin = (0.0, 0.0, station.parent_mate_depth)
    model.articulation(
        f"{station.parent_part}_to_{station.name}",
        ArticulationType.REVOLUTE,
        parent=parent,
        child=part,
        origin=Origin(xyz=joint_origin),
        axis=station.axis,
        motion_limits=_motion_limits(r.joint_limit_style, index),
        mating=MatingContract(
            station.parent_visual,
            station.parent_face_side,
            station.child_hub_visual,
            station.child_face_side,
            contact_tol=0.002,
        ),
    )
    leaf_parts.append(station.name)
    return leaf_parts


def build_branching_tree_with_two_independent_rotary_branches(
    config: BranchingTreeWithTwoIndependentRotaryBranchesConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name="branching_tree_with_two_independent_rotary_branches",
        assets=assets,
    )
    _register_materials(model, r)

    stations = _resolve_two_stations(r)
    _build_support_carrier(model, r, stations)

    branch_leaves: list[str] = []
    for index, station in enumerate(stations):
        branch_leaves.extend(_build_branch_topology(model, r, station, index))

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["branch_leaf_parts"] = branch_leaves
    return model


def build_seeded_branching_tree_with_two_independent_rotary_branches(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_branching_tree_with_two_independent_rotary_branches(
        config_from_seed(seed),
        assets=assets,
    )


def slot_choices_for_config(
    r: ResolvedBranchingTreeWithTwoIndependentRotaryBranchesConfig,
) -> list[tuple[str, str]]:
    return [
        ("support_carrier", r.support_carrier),
        ("mount_layout", r.mount_layout),
        ("joint_axis_policy", r.joint_axis_policy),
        ("branch_topology", r.branch_topology),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def run_branching_tree_with_two_independent_rotary_branches_tests(
    object_model: ArticulatedObject,
    config: BranchingTreeWithTwoIndependentRotaryBranchesConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    names = {p.name for p in object_model.parts}
    joints = {j.name: j for j in object_model.articulations}
    revolute_joints = [
        j for j in joints.values() if j.articulation_type == ArticulationType.REVOLUTE
    ]
    branch_leaves = list(object_model.meta.get("branch_leaf_parts") or [])
    branch_joints = [j for j in revolute_joints if "_forearm" not in j.name]
    ctx.check("modular_two_branch_count", len(branch_leaves) == 2)
    ctx.check("exactly_two_revolute_joints", len(branch_joints) == 2)
    ctx.check("support_present", "support" in names)
    ctx.check(
        "slot_choices_match_config",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    for leaf in branch_leaves:
        ctx.check(f"{leaf}_present", leaf in names)

    support_part = object_model.get_part("support")
    for part_name in names:
        part = object_model.get_part(part_name)
        if part_name.endswith("_bracket"):
            ctx.allow_overlap(
                part,
                support_part,
                reason="bracket_root_overlaps_support_socket",
            )
            for leaf in branch_leaves:
                if leaf.startswith(part_name.replace("_bracket", "")):
                    ctx.allow_overlap(
                        part,
                        object_model.get_part(leaf),
                        reason="branch_hub_seated_on_bracket_plate",
                    )
        if part_name.endswith("_hub_carrier"):
            ctx.allow_overlap(
                part,
                support_part,
                reason="hub_carrier_seated_on_support_pedestal",
            )
            branch_name = part_name.replace("_hub_carrier", "_branch")
            if branch_name in names:
                ctx.allow_overlap(
                    part,
                    object_model.get_part(branch_name),
                    reason="spoke_hub_seated_in_carrier_barrel",
                )
    for leaf in branch_leaves:
        ctx.allow_overlap(
            object_model.get_part(leaf),
            support_part,
            reason="branch_hub_near_support_bearing",
        )
        if leaf.endswith("_forearm"):
            upper_name = leaf.replace("_forearm", "_upper")
            if upper_name in names:
                ctx.allow_overlap(
                    object_model.get_part(upper_name),
                    object_model.get_part(leaf),
                    reason="two_link_chain_elbow_hub_seated_on_upper_boss",
                )

    for joint in revolute_joints:
        ctx.check(
            f"{joint.name}_has_mating_or_internal",
            joint.mating is not None or joint.parent != "support",
        )

    ctx.fail_if_isolated_parts()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()
    return ctx.report()
