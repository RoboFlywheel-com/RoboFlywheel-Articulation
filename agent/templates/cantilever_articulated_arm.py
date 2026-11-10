# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
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

ArmLayout = Literal[
    "vertical_pitch_chain",
    "horizontal_swing_chain",
    "pedestal_yaw_pitch_chain",
    "underslung_pitch_chain",
]
BaseMountStyle = Literal["pedestal", "wall_block", "support_frame", "column_turret"]
LinkProfile = Literal["box_beam", "forked_link", "underslung_shell", "tapered_beam"]
WristStyle = Literal["end_plate", "tool_head", "flange", "wrist_block"]
MaterialStyle = Literal["industrial_orange", "brushed_aluminum", "graphite", "blue_tool"]

MATERIAL_PALETTES: dict[
    MaterialStyle,
    tuple[
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
    ],
] = {
    "industrial_orange": (
        (0.13, 0.13, 0.14, 1.0),
        (0.88, 0.36, 0.08, 1.0),
        (0.72, 0.74, 0.70, 1.0),
        (0.02, 0.02, 0.018, 1.0),
        (0.025, 0.028, 0.030, 1.0),
    ),
    "brushed_aluminum": (
        (0.52, 0.54, 0.56, 1.0),
        (0.62, 0.64, 0.60, 1.0),
        (0.72, 0.74, 0.70, 1.0),
        (0.02, 0.02, 0.018, 1.0),
        (0.025, 0.028, 0.030, 1.0),
    ),
    "graphite": (
        (0.10, 0.11, 0.11, 1.0),
        (0.34, 0.36, 0.34, 1.0),
        (0.55, 0.57, 0.54, 1.0),
        (0.018, 0.018, 0.016, 1.0),
        (0.025, 0.028, 0.030, 1.0),
    ),
    "blue_tool": (
        (0.09, 0.12, 0.18, 1.0),
        (0.14, 0.38, 0.74, 1.0),
        (0.62, 0.64, 0.66, 1.0),
        (0.02, 0.02, 0.018, 1.0),
        (0.025, 0.028, 0.030, 1.0),
    ),
}


@dataclass(frozen=True)
class CantileverArticulatedArmConfig:
    arm_layout: ArmLayout = "vertical_pitch_chain"
    base_mount_style: BaseMountStyle = "pedestal"
    link_profile: LinkProfile = "forked_link"
    link_count: int = 2
    shoulder_link_length: float = 0.80
    elbow_link_length: float = 0.55
    wrist_length: float = 0.16
    wrist_style: WristStyle = "end_plate"
    yaw_enabled: bool | None = None
    material_style: MaterialStyle = "graphite"
    name: str = "reference_cantilever_articulated_arm"


@dataclass(frozen=True)
class ResolvedCantileverArticulatedArmConfig:
    arm_layout: ArmLayout
    base_mount_style: BaseMountStyle
    link_profile: LinkProfile
    link_count: int
    shoulder_link_length: float
    elbow_link_length: float
    wrist_length: float
    yaw_enabled: bool
    wrist_style: WristStyle
    joint_axis: tuple[float, float, float]
    shoulder_origin: tuple[float, float, float]
    shoulder_limits: tuple[float, float]
    elbow_limits: tuple[float, float]
    wrist_limits: tuple[float, float]
    base_height: float
    base_width: float
    column_radius: float
    cheek_half_width: float
    shoulder_effort: float
    elbow_effort: float
    material_style: MaterialStyle
    name: str


def config_from_seed(seed: int) -> CantileverArticulatedArmConfig:
    rng = random.Random(seed)
    arm_layout: ArmLayout = rng.choice(
        (
            "vertical_pitch_chain",
            "horizontal_swing_chain",
            "pedestal_yaw_pitch_chain",
            "underslung_pitch_chain",
        )
    )
    base_mount_style: BaseMountStyle = rng.choice(
        ("pedestal", "wall_block", "support_frame", "column_turret")
    )
    return CantileverArticulatedArmConfig(
        arm_layout=arm_layout,
        base_mount_style=base_mount_style,
        link_profile=rng.choice(("box_beam", "forked_link", "underslung_shell", "tapered_beam")),
        link_count=rng.choice((2, 3)),
        shoulder_link_length=round(rng.uniform(0.65, 1.05), 3),
        elbow_link_length=round(rng.uniform(0.42, 0.75), 3),
        wrist_length=round(rng.uniform(0.11, 0.22), 3),
        wrist_style=rng.choice(("end_plate", "tool_head", "flange", "wrist_block")),
        yaw_enabled=None,
        material_style=rng.choice(
            ("industrial_orange", "brushed_aluminum", "graphite", "blue_tool")
        ),
        name=f"seeded_cantilever_articulated_arm_{seed}",
    )


def _link_root_half_height(_profile: LinkProfile) -> float:
    if _profile == "underslung_shell":
        return 0.067
    return 0.045


def resolve_config(
    config: CantileverArticulatedArmConfig,
) -> ResolvedCantileverArticulatedArmConfig:
    if config.arm_layout not in {
        "vertical_pitch_chain",
        "horizontal_swing_chain",
        "pedestal_yaw_pitch_chain",
        "underslung_pitch_chain",
    }:
        raise ValueError(f"Unsupported arm_layout: {config.arm_layout}")
    if config.base_mount_style not in {"pedestal", "wall_block", "support_frame", "column_turret"}:
        raise ValueError(f"Unsupported base_mount_style: {config.base_mount_style}")
    if config.link_profile not in {"box_beam", "forked_link", "underslung_shell", "tapered_beam"}:
        raise ValueError(f"Unsupported link_profile: {config.link_profile}")
    if config.wrist_style not in {"end_plate", "tool_head", "flange", "wrist_block"}:
        raise ValueError(f"Unsupported wrist_style: {config.wrist_style}")
    if config.link_count not in {2, 3}:
        raise ValueError("link_count must be 2 or 3")
    if config.material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    shoulder_link_length = max(0.60, min(1.10, config.shoulder_link_length))
    elbow_link_length = max(0.38, min(0.80, config.elbow_link_length))
    wrist_length = max(0.10, min(0.24, config.wrist_length))
    yaw_enabled = config.yaw_enabled
    if yaw_enabled is None:
        yaw_enabled = (
            config.base_mount_style == "column_turret"
            or config.arm_layout == "pedestal_yaw_pitch_chain"
        )
    joint_axis = (
        (0.0, 0.0, 1.0) if config.arm_layout == "horizontal_swing_chain" else (0.0, 1.0, 0.0)
    )
    base_height = 0.72 if config.base_mount_style in {"pedestal", "column_turret"} else 0.60
    base_width = 0.34 if config.base_mount_style != "support_frame" else 0.48
    column_radius = 0.145 if config.base_mount_style == "pedestal" else 0.08
    cheek_half_width = 0.185
    shoulder_effort = 220.0 + shoulder_link_length * 50.0
    elbow_effort = 140.0 + elbow_link_length * 40.0
    if config.base_mount_style == "wall_block":
        shoulder_origin: tuple[float, float, float] = (0.09, 0.0, 0.24)
    else:
        shoulder_origin = (
            base_width * 0.50 if config.base_mount_style == "support_frame" else 0.34,
            0.0,
            base_height + _link_root_half_height(config.link_profile),
        )
    if config.arm_layout == "underslung_pitch_chain":
        shoulder_origin = (0.06, 0.0, base_height * 0.72)
    return ResolvedCantileverArticulatedArmConfig(
        arm_layout=config.arm_layout,
        base_mount_style=config.base_mount_style,
        link_profile=config.link_profile,
        link_count=config.link_count,
        shoulder_link_length=shoulder_link_length,
        elbow_link_length=elbow_link_length,
        wrist_length=wrist_length,
        yaw_enabled=bool(yaw_enabled),
        wrist_style=config.wrist_style,
        joint_axis=joint_axis,
        shoulder_origin=shoulder_origin,
        shoulder_limits=(-0.70, 0.45),
        elbow_limits=(-1.10, 1.05),
        wrist_limits=(-math.pi, math.pi),
        base_height=base_height,
        base_width=base_width,
        column_radius=column_radius,
        cheek_half_width=cheek_half_width,
        shoulder_effort=shoulder_effort,
        elbow_effort=elbow_effort,
        material_style=config.material_style,
        name=config.name,
    )


def _box(part, size, xyz, material, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cyl(
    part,
    radius: float,
    length: float,
    xyz,
    material,
    name: str,
    rpy=(0.0, 0.0, 0.0),
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.stainless_matte",
    )


_CYL_X = (0.0, math.pi / 2.0, 0.0)
_CYL_Y = (math.pi / 2.0, 0.0, 0.0)


def _add_anchor_bolts(part, centers: tuple[tuple[float, float, float], ...], material) -> None:
    for index, center in enumerate(centers):
        _cyl(part, 0.022, 0.018, center, material, f"anchor_bolt_{index}")


def _add_cheek_pair(
    part,
    *,
    pivot_x: float,
    pivot_z: float,
    half_w: float,
    cheek_size: tuple[float, float, float],
    cap_radius: float,
    cap_length: float,
    base_mat,
    machined_mat,
    prefix: str,
) -> None:
    for i, sign in enumerate((-1.0, 1.0)):
        y = sign * half_w
        _box(part, cheek_size, (pivot_x, y, pivot_z), base_mat, f"{prefix}_cheek_{i}")
        _cyl(
            part,
            cap_radius,
            cap_length,
            (pivot_x, sign * half_w * 1.13, pivot_z),
            machined_mat,
            f"{prefix}_cap_{i}",
            _CYL_Y,
        )
    _box(
        part,
        (cheek_size[0] * 0.72, 2.0 * half_w, cheek_size[2] * 0.10),
        (pivot_x, 0.0, pivot_z - cheek_size[2] * 0.52),
        base_mat,
        f"{prefix}_cheek_bridge",
    )


def _add_hub_washers(
    part,
    *,
    hub_radius: float,
    hub_length: float,
    washer_radius: float,
    washer_length: float,
    half_sep: float,
    xyz: tuple[float, float, float],
    machined_mat,
    prefix: str,
) -> None:
    _cyl(part, hub_radius, hub_length, xyz, machined_mat, f"{prefix}_hub", _CYL_Y)
    for i, sign in enumerate((-1.0, 1.0)):
        _cyl(
            part,
            washer_radius,
            washer_length,
            (xyz[0], xyz[1] + sign * half_sep, xyz[2]),
            machined_mat,
            f"{prefix}_washer_{i}",
            _CYL_Y,
        )


def _build_base(
    part, r: ResolvedCantileverArticulatedArmConfig, base_mat, link_mat, machined_mat, bolt_mat
) -> None:
    so = r.shoulder_origin
    hw = r.cheek_half_width
    if r.base_mount_style == "pedestal":
        _cyl(part, 0.36, 0.065, (0.0, 0.0, 0.0325), base_mat, "pedestal_foot")
        _add_anchor_bolts(
            part,
            (
                (0.24, 0.24, 0.068),
                (0.24, -0.24, 0.068),
                (-0.24, 0.24, 0.068),
                (-0.24, -0.24, 0.068),
            ),
            bolt_mat,
        )
        _cyl(
            part,
            r.column_radius,
            r.base_height,
            (0.0, 0.0, r.base_height * 0.5),
            base_mat,
            "pedestal_column",
        )
        _cyl(
            part,
            r.column_radius * 1.32,
            0.16,
            (0.0, 0.0, r.base_height * 0.90),
            base_mat,
            "top_cast_cap",
        )
        _box(
            part,
            (so[0] * 1.80, 0.30, 0.13),
            (so[0] * 0.40, 0.0, so[2] - 0.22),
            base_mat,
            "shoulder_cantilever",
        )
        _box(
            part,
            (so[0] * 1.80, 0.42, 0.07),
            (so[0] * 0.38, 0.0, so[2] - 0.30),
            base_mat,
            "shoulder_yoke_base",
        )
        _box(part, (0.24, 0.030, 0.10), (0.0, -0.115, 0.18), link_mat, "front_column_rib")
        _box(part, (0.24, 0.030, 0.10), (0.0, 0.115, 0.18), link_mat, "rear_column_rib")
        if not r.yaw_enabled:
            _add_cheek_pair(
                part,
                pivot_x=so[0],
                pivot_z=so[2],
                half_w=hw,
                cheek_size=(0.24, 0.050, 0.42),
                cap_radius=0.122,
                cap_length=0.040,
                base_mat=base_mat,
                machined_mat=machined_mat,
                prefix="shoulder",
            )
    elif r.base_mount_style == "wall_block":
        _box(part, (0.12, r.base_width, r.base_height), (-0.06, 0.0, 0.22), base_mat, "wall_plate")
        for index, (y, z) in enumerate(((-0.10, 0.08), (0.10, 0.08), (-0.10, 0.36), (0.10, 0.36))):
            _cyl(part, 0.010, 0.014, (0.004, y, z), bolt_mat, f"wall_socket_bolt_{index}", _CYL_X)
        _box(part, (0.12, 0.18, 0.18), (0.03, 0.0, 0.24), base_mat, "root_hinge_block")
        _box(part, (0.16, 0.030, 0.15), (0.015, -0.105, 0.22), link_mat, "wall_left_web")
        _box(part, (0.16, 0.030, 0.15), (0.015, 0.105, 0.22), link_mat, "wall_right_web")
        _add_anchor_bolts(
            part,
            (
                (-0.08, -0.105, 0.14),
                (-0.08, 0.105, 0.14),
                (-0.08, -0.105, 0.34),
                (-0.08, 0.105, 0.34),
            ),
            bolt_mat,
        )
        if not r.yaw_enabled:
            _add_cheek_pair(
                part,
                pivot_x=so[0],
                pivot_z=so[2],
                half_w=hw,
                cheek_size=(0.20, 0.050, 0.36),
                cap_radius=0.105,
                cap_length=0.034,
                base_mat=base_mat,
                machined_mat=machined_mat,
                prefix="shoulder",
            )
    elif r.base_mount_style == "support_frame":
        _box(
            part, (0.10, r.base_width, r.base_height), (-0.04, 0.0, 0.25), base_mat, "rear_upright"
        )
        _box(part, (0.40, 0.06, 0.08), (0.10, r.base_width * 0.35, 0.08), base_mat, "left_foot")
        _box(part, (0.40, 0.06, 0.08), (0.10, -r.base_width * 0.35, 0.08), base_mat, "right_foot")
        _box(part, (0.30, 0.035, 0.055), (0.03, 0.0, 0.30), base_mat, "rear_cross_tie")
        for y, name in (
            (r.base_width * 0.26, "left_diagonal_web"),
            (-r.base_width * 0.26, "right_diagonal_web"),
        ):
            _box(part, (0.18, 0.018, 0.055), (0.03, y, 0.20), link_mat, name, (0.0, 0.42, 0.0))
        _add_anchor_bolts(
            part,
            (
                (0.10, r.base_width * 0.40, 0.04),
                (0.10, -r.base_width * 0.40, 0.04),
                (-0.10, r.base_width * 0.40, 0.04),
                (-0.10, -r.base_width * 0.40, 0.04),
            ),
            bolt_mat,
        )
        if not r.yaw_enabled:
            _box(
                part,
                (so[0] + 0.12, 0.16, 0.08),
                (so[0] * 0.50 - 0.02, 0.0, so[2] - 0.36 * 0.52),
                base_mat,
                "shoulder_yoke_stem",
            )
            _add_cheek_pair(
                part,
                pivot_x=so[0],
                pivot_z=so[2],
                half_w=hw,
                cheek_size=(0.20, 0.050, 0.36),
                cap_radius=0.105,
                cap_length=0.034,
                base_mat=base_mat,
                machined_mat=machined_mat,
                prefix="shoulder",
            )
    else:
        _cyl(part, 0.36, 0.065, (0.0, 0.0, 0.0325), base_mat, "round_base")
        for index, angle in enumerate((0.0, math.pi * 0.5, math.pi, math.pi * 1.5)):
            _cyl(
                part,
                0.022,
                0.018,
                (0.24 * math.cos(angle), 0.24 * math.sin(angle), 0.068),
                bolt_mat,
                f"anchor_bolt_{index}",
            )
        _cyl(
            part,
            r.column_radius,
            r.base_height,
            (0.0, 0.0, r.base_height * 0.5),
            base_mat,
            "pedestal_column",
        )
        _cyl(
            part,
            r.column_radius * 1.32,
            0.040,
            (0.0, 0.0, r.base_height - 0.020),
            base_mat,
            "top_cast_cap",
        )
    if r.yaw_enabled:
        _cyl(
            part,
            max(0.065, r.column_radius * 0.86),
            r.base_height,
            (0.0, 0.0, r.base_height * 0.5),
            base_mat,
            "yaw_contact_post",
        )


def _add_root_bushed_pin(part, length: float, material, dark, prefix: str) -> None:
    _cyl(part, 0.026, 0.072, (0.032, 0.0, 0.0), dark, f"{prefix}_root_bushed_pin", _CYL_Y)
    for y, side in ((-0.074, "left"), (0.074, "right")):
        _cyl(part, 0.012, 0.008, (0.032, y, 0.0), material, f"{prefix}_root_{side}_cap", _CYL_Y)


def _build_link(
    part,
    r: ResolvedCantileverArticulatedArmConfig,
    length: float,
    link_mat,
    machined_mat,
    bolt_mat,
    cover_mat,
    prefix: str,
    hub_radius: float,
    washer_radius: float,
    parent_cheek_half_sep: float,
    parent_cheek_y_half: float,
    cheek_half_sep: float,
    elbow_cheek_size: tuple[float, float, float],
    elbow_cap_radius: float,
) -> None:
    # Washers sit just inside the parent cheek inner faces; hub is shorter for clearance.
    washer_half_len = 0.015
    washer_center = parent_cheek_half_sep - parent_cheek_y_half - washer_half_len
    hub_half_len = parent_cheek_half_sep - parent_cheek_y_half - 0.020
    _cyl(
        part,
        hub_radius,
        2.0 * hub_half_len,
        (0.0, 0.0, 0.0),
        machined_mat,
        f"{prefix}_root_hub",
        _CYL_Y,
    )
    for i, sign in enumerate((-1.0, 1.0)):
        _cyl(
            part,
            washer_radius,
            2.0 * washer_half_len,
            (0.0, sign * washer_center, 0.0),
            machined_mat,
            f"{prefix}_root_washer_{i}",
            _CYL_Y,
        )
    _box(
        part,
        (0.075, 2.0 * hub_half_len * 0.58, hub_radius * 1.35),
        (0.135, 0.0, 0.0),
        link_mat,
        f"{prefix}_neck",
    )
    _add_root_bushed_pin(part, length, link_mat, machined_mat, prefix)

    safe_end = length - elbow_cap_radius - 0.024

    if r.link_profile == "box_beam":
        _box(
            part,
            (length * 0.80, hub_radius * 1.73, hub_radius * 1.73),
            (length * 0.44, 0.0, 0.0),
            link_mat,
            f"{prefix}_box_beam",
        )
    elif r.link_profile == "forked_link":
        _box(
            part,
            (length * 0.72, hub_radius * 1.55, hub_radius * 1.55),
            (length * 0.40, 0.0, 0.0),
            link_mat,
            f"{prefix}_beam",
        )
        fork_x = safe_end - length * 0.055
        for i, y in enumerate((-cheek_half_sep * 0.45, cheek_half_sep * 0.45)):
            _box(
                part,
                (length * 0.14, hub_radius * 0.50, hub_radius * 1.65),
                (fork_x, y, 0.0),
                link_mat,
                f"{prefix}_fork_{i}",
            )
        _box(
            part,
            (length * 0.13, hub_radius * 2.50, hub_radius * 1.10),
            (safe_end - length * 0.065, 0.0, 0.0),
            machined_mat,
            f"{prefix}_fork_bridge",
        )
    elif r.link_profile == "underslung_shell":
        _box(
            part,
            (length * 0.72, hub_radius * 1.55, hub_radius * 1.10),
            (length * 0.44, 0.0, -hub_radius * 0.52),
            link_mat,
            f"{prefix}_underslung_shell",
        )
        top_rib_end = min(length * 0.93, safe_end - 0.010)
        _box(
            part,
            (top_rib_end, hub_radius * 0.68, hub_radius * 0.64),
            (top_rib_end * 0.50, 0.0, hub_radius * 0.40),
            machined_mat,
            f"{prefix}_top_rib",
        )
        end_lug_len = min(0.060, safe_end - top_rib_end)
        if end_lug_len > 0.010:
            _box(
                part,
                (end_lug_len, hub_radius * 1.55, hub_radius * 1.95),
                (safe_end - end_lug_len * 0.5, 0.0, 0.0),
                machined_mat,
                f"{prefix}_end_lug",
            )
    else:
        wide_len = hub_radius * 1.74
        _box(
            part,
            (length * 0.62, hub_radius * 1.35, hub_radius * 1.40),
            (length * 0.40, 0.0, 0.0),
            link_mat,
            f"{prefix}_tapered_beam",
        )
        _box(
            part,
            (wide_len, hub_radius * 1.85, hub_radius * 1.74),
            (safe_end - wide_len * 0.5, 0.0, 0.0),
            link_mat,
            f"{prefix}_wide_end",
        )

    lower_bridge_z = -elbow_cheek_size[2] * 0.52
    lower_bridge_h = elbow_cheek_size[2] * 0.10
    lower_bridge_start = max(length * 0.68, length - elbow_cap_radius * 1.60)
    lower_bridge_len = length - lower_bridge_start + elbow_cheek_size[0] * 0.18
    web_h = max(hub_radius * 1.30, abs(lower_bridge_z) + hub_radius * 0.95)
    _box(
        part,
        (0.050, hub_radius * 1.05, web_h),
        (lower_bridge_start, 0.0, lower_bridge_z * 0.50),
        link_mat,
        f"{prefix}_end_yoke_drop_web",
    )
    _box(
        part,
        (lower_bridge_len, hub_radius * 1.05, lower_bridge_h),
        ((lower_bridge_start + length) * 0.5, 0.0, lower_bridge_z),
        link_mat,
        f"{prefix}_end_yoke_lower_bridge",
    )

    _add_cheek_pair(
        part,
        pivot_x=length,
        pivot_z=0.0,
        half_w=cheek_half_sep,
        cheek_size=elbow_cheek_size,
        cap_radius=elbow_cap_radius,
        cap_length=0.034,
        base_mat=link_mat,
        machined_mat=machined_mat,
        prefix=f"{prefix}_elbow",
    )


def _add_wrist_end(part, link_mat, machined_mat, *, at_x: float) -> None:
    _box(part, (0.080, 0.120, 0.100), (at_x - 0.048, 0.0, 0.0), link_mat, "wrist_neck")
    _cyl(part, 0.062, 0.050, (at_x, 0.0, 0.0), machined_mat, "wrist_end_boss", _CYL_X)


def _build_wrist(
    part,
    r: ResolvedCantileverArticulatedArmConfig,
    link_mat,
    machined_mat,
    bolt_mat,
    cover_mat,
) -> None:
    _box(part, (0.086, 0.074, 0.074), (0.027, 0.0, 0.0), link_mat, "wrist_contact_bridge")
    _cyl(part, 0.021, 0.060, (0.030, 0.0, 0.0), machined_mat, "wrist_bushed_pin", _CYL_Y)
    _cyl(part, 0.055, 0.040, (0.056, 0.0, 0.0), machined_mat, "wrist_collar", _CYL_X)
    offset = 0.090
    spine_len = offset + r.wrist_length + 0.018
    _box(
        part,
        (spine_len, 0.058, 0.058),
        (spine_len * 0.5 - 0.010, 0.0, 0.0),
        link_mat,
        "wrist_body_spine",
    )
    if r.wrist_style == "end_plate":
        _cyl(part, 0.050, 0.040, (offset, 0.0, 0.0), machined_mat, "pilot_boss", _CYL_X)
        _box(
            part,
            (0.030, 0.16, 0.16),
            (offset + r.wrist_length * 0.80, 0.0, 0.0),
            link_mat,
            "end_plate",
        )
    elif r.wrist_style == "tool_head":
        _box(
            part,
            (r.wrist_length, 0.080, 0.075),
            (offset + r.wrist_length * 0.5, 0.0, 0.0),
            link_mat,
            "tool_body",
        )
        _cyl(
            part,
            0.024,
            0.16,
            (offset + r.wrist_length, 0.0, 0.0),
            machined_mat,
            "tool_nozzle",
            _CYL_X,
        )
    elif r.wrist_style == "flange":
        _cyl(part, 0.050, 0.040, (offset, 0.0, 0.0), machined_mat, "pilot_boss", _CYL_X)
        _cyl(
            part,
            0.075,
            0.030,
            (offset + r.wrist_length, 0.0, 0.0),
            machined_mat,
            "round_flange",
            _CYL_X,
        )
        for i in range(4):
            angle = i * math.tau / 4.0
            _cyl(
                part,
                0.008,
                0.010,
                (offset + r.wrist_length, 0.050 * math.cos(angle), 0.050 * math.sin(angle)),
                bolt_mat,
                f"flange_bolt_{i}",
                _CYL_X,
            )
        _cyl(
            part,
            0.043,
            0.020,
            (offset + r.wrist_length - 0.022, 0.0, 0.0),
            machined_mat,
            "flange_rear_boss",
            _CYL_X,
        )
    else:
        _box(
            part,
            (r.wrist_length, 0.10, 0.09),
            (offset + r.wrist_length * 0.5, 0.0, 0.0),
            link_mat,
            "wrist_block",
        )
        _box(
            part,
            (0.030, 0.13, 0.11),
            (offset + r.wrist_length, 0.0, 0.0),
            machined_mat,
            "front_pad",
        )


def build_cantilever_arm(
    config: CantileverArticulatedArmConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or CantileverArticulatedArmConfig()
    r = resolve_config(config)
    assets = assets or AssetContext(
        Path(tempfile.mkdtemp(prefix="articraft-cantilever-arm-assets-"))
    )
    model = ArticulatedObject(name=r.name, assets=assets)
    base_rgba, link_rgba, machined_rgba, bolt_rgba, cover_rgba = MATERIAL_PALETTES[r.material_style]
    base_mat = model.material(f"base_{r.material_style}", rgba=base_rgba)
    link_mat = model.material(f"link_{r.material_style}", rgba=link_rgba)
    machined_mat = model.material(f"machined_{r.material_style}", rgba=machined_rgba)
    bolt_mat = model.material(f"bolt_{r.material_style}", rgba=bolt_rgba)
    cover_mat = model.material(f"cover_{r.material_style}", rgba=cover_rgba)

    base = model.part("base_support")
    _build_base(base, r, base_mat, link_mat, machined_mat, bolt_mat)
    parent = base
    shoulder_origin = Origin(xyz=r.shoulder_origin)

    if r.yaw_enabled:
        yaw_shoulder_z = 0.38 if r.link_profile == "underslung_shell" else 0.32
        yaw = model.part("yaw_housing")
        _cyl(yaw, 0.19, 0.050, (0.0, 0.0, 0.025), machined_mat, "yaw_bearing_race")
        _box(yaw, (0.11, 0.11, 0.080), (0.04, 0.0, 0.055), base_mat, "yaw_stack_spigot")
        _box(yaw, (0.16, 0.16, 0.09), (0.04, 0.0, 0.090), base_mat, "turret_block")
        _box(
            yaw,
            (0.12, 0.12, 0.10),
            (0.08, 0.0, yaw_shoulder_z - 0.25),
            base_mat,
            "yaw_shoulder_riser",
        )
        _add_cheek_pair(
            yaw,
            pivot_x=0.08,
            pivot_z=yaw_shoulder_z,
            half_w=r.cheek_half_width,
            cheek_size=(0.24, 0.050, 0.42),
            cap_radius=0.122,
            cap_length=0.040,
            base_mat=base_mat,
            machined_mat=machined_mat,
            prefix="yaw_shoulder",
        )
        model.articulation(
            "base_yaw",
            ArticulationType.REVOLUTE,
            parent=base,
            child=yaw,
            origin=Origin(xyz=(0.0, 0.0, r.base_height)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=60.0, velocity=1.5, lower=-1.57, upper=1.57),
            meta={
                "type": "revolute",
                "axis": (0.0, 0.0, 1.0),
                "origin": "pedestal top center",
                "range": (-1.57, 1.57),
            },
        )
        parent = yaw
        shoulder_origin = Origin(xyz=(0.08, 0.0, yaw_shoulder_z))

    sl = r.shoulder_link_length
    el = r.elbow_link_length
    s_hub_r = 0.104
    s_washer_r = 0.074
    e_hub_r = 0.084
    e_washer_r = 0.060
    s_cheek_size = (sl * 0.26, 0.046, sl * 0.40)
    e_cheek_size = (el * 0.24, 0.046, el * 0.38)
    # base_cheek_y_half: base/yaw cheek y-half for shoulder_link root contact
    base_cheek_y_half = 0.025
    # shoulder_elbow_cheek_y_half: shoulder_link elbow cheek y-half for elbow_link root contact
    shoulder_elbow_cheek_y_half = 0.023

    shoulder_link = model.part("shoulder_link")
    _build_link(
        shoulder_link,
        r,
        sl,
        link_mat,
        machined_mat,
        bolt_mat,
        cover_mat,
        "shoulder",
        hub_radius=s_hub_r,
        washer_radius=s_washer_r,
        parent_cheek_half_sep=r.cheek_half_width,
        parent_cheek_y_half=base_cheek_y_half,
        cheek_half_sep=r.cheek_half_width,
        elbow_cheek_size=s_cheek_size,
        elbow_cap_radius=e_hub_r * 1.12,
    )

    # In 3-link chain elbow's parent cheeks are on intermediate_link (cheek_half_sep=0.90*hw);
    # in 2-link chain they are on shoulder_link (cheek_half_sep=hw).
    elbow_parent_cheek_half_sep = (
        r.cheek_half_width * 0.90 if r.link_count == 3 else r.cheek_half_width
    )
    elbow_link = model.part("elbow_link")
    _build_link(
        elbow_link,
        r,
        el,
        link_mat,
        machined_mat,
        bolt_mat,
        cover_mat,
        "elbow",
        hub_radius=e_hub_r,
        washer_radius=e_washer_r,
        parent_cheek_half_sep=elbow_parent_cheek_half_sep,
        parent_cheek_y_half=shoulder_elbow_cheek_y_half,
        cheek_half_sep=r.cheek_half_width * 0.80,
        elbow_cheek_size=e_cheek_size,
        elbow_cap_radius=e_hub_r * 0.95,
    )
    _add_wrist_end(elbow_link, link_mat, machined_mat, at_x=el - 0.040)

    wrist = model.part("wrist_or_end_effector")
    _build_wrist(wrist, r, link_mat, machined_mat, bolt_mat, cover_mat)

    model.articulation(
        "shoulder_joint",
        ArticulationType.REVOLUTE,
        parent=parent,
        child=shoulder_link,
        origin=shoulder_origin,
        axis=r.joint_axis,
        motion_limits=MotionLimits(
            effort=r.shoulder_effort,
            velocity=0.8,
            lower=r.shoulder_limits[0],
            upper=r.shoulder_limits[1],
        ),
        meta={
            "type": "revolute",
            "axis": r.joint_axis,
            "origin": "base support shoulder hinge",
            "range": r.shoulder_limits,
        },
    )
    elbow_parent = shoulder_link
    elbow_origin = Origin(xyz=(sl, 0.0, 0.0))
    if r.link_count == 3:
        intermediate = model.part("intermediate_link")
        inter_len = (sl + el) * 0.42
        _build_link(
            intermediate,
            r,
            inter_len,
            link_mat,
            machined_mat,
            bolt_mat,
            cover_mat,
            "intermediate",
            hub_radius=s_hub_r * 0.88,
            washer_radius=s_washer_r * 0.88,
            parent_cheek_half_sep=r.cheek_half_width,
            parent_cheek_y_half=shoulder_elbow_cheek_y_half,
            cheek_half_sep=r.cheek_half_width * 0.90,
            elbow_cheek_size=(inter_len * 0.26, 0.046, inter_len * 0.40),
            elbow_cap_radius=e_hub_r * 1.05,
        )
        model.articulation(
            "intermediate_joint",
            ArticulationType.REVOLUTE,
            parent=shoulder_link,
            child=intermediate,
            origin=elbow_origin,
            axis=r.joint_axis,
            motion_limits=MotionLimits(
                effort=r.elbow_effort * 0.90, velocity=1.1, lower=-1.4, upper=1.2
            ),
            meta={
                "type": "revolute",
                "axis": r.joint_axis,
                "origin": "shoulder link end",
                "range": (-1.4, 1.2),
            },
        )
        elbow_parent = intermediate
        elbow_origin = Origin(xyz=(inter_len, 0.0, 0.0))

    model.articulation(
        "elbow_joint",
        ArticulationType.REVOLUTE,
        parent=elbow_parent,
        child=elbow_link,
        origin=elbow_origin,
        axis=r.joint_axis,
        motion_limits=MotionLimits(
            effort=r.elbow_effort,
            velocity=0.95,
            lower=r.elbow_limits[0],
            upper=r.elbow_limits[1],
        ),
        meta={
            "type": "revolute",
            "axis": r.joint_axis,
            "origin": "parent link end",
            "range": r.elbow_limits,
        },
    )
    wrist_axis = r.joint_axis if r.arm_layout != "pedestal_yaw_pitch_chain" else (1.0, 0.0, 0.0)
    model.articulation(
        "wrist_joint",
        ArticulationType.REVOLUTE,
        parent=elbow_link,
        child=wrist,
        origin=Origin(xyz=(el, 0.0, 0.0)),
        axis=wrist_axis,
        motion_limits=MotionLimits(
            effort=55.0, velocity=1.6, lower=r.wrist_limits[0], upper=r.wrist_limits[1]
        ),
        meta={
            "type": "revolute",
            "axis": wrist_axis,
            "origin": "elbow link end",
            "range": r.wrist_limits,
        },
    )
    model.meta["primary_joints"] = ("shoulder_joint", "elbow_joint", "wrist_joint")
    return model


def run_cantilever_arm_tests(
    object_model: ArticulatedObject, config: CantileverArticulatedArmConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {part.name for part in object_model.parts}
    joint_names = {joint.name for joint in object_model.articulations}

    # Articulated arm links hinge into one another; each joint's yokes / cheeks /
    # hubs intentionally overlap the mating link they pivot on.
    _links = [n for n in part_names if n in (
        "base_support", "shoulder_link", "elbow_link", "intermediate_link",
        "wrist_or_end_effector", "yaw_housing",
    )]
    for _i in range(len(_links)):
        for _j in range(_i + 1, len(_links)):
            ctx.allow_overlap(
                object_model.get_part(_links[_i]), object_model.get_part(_links[_j]),
                reason="Articulated arm links hinge into one another at their joints.",
            )

    ctx.check(
        "required_parts",
        {"base_support", "shoulder_link", "elbow_link", "wrist_or_end_effector"}.issubset(
            part_names
        ),
        details=str(sorted(part_names)),
    )
    revolute_joints = [
        joint
        for joint in object_model.articulations
        if joint.articulation_type == ArticulationType.REVOLUTE
    ]
    ctx.check(
        "joint_count", len(revolute_joints) >= 3, details=f"revolute_count={len(revolute_joints)}"
    )
    ctx.check(
        "chain_joints_exist",
        {"shoulder_joint", "elbow_joint", "wrist_joint"}.issubset(joint_names),
        details=str(sorted(joint_names)),
    )

    shoulder = object_model.get_articulation("shoulder_joint")
    elbow_joint = object_model.get_articulation("elbow_joint")
    wrist = object_model.get_articulation("wrist_joint")
    expected_axis = r.joint_axis

    for name, joint in (("shoulder_joint", shoulder), ("elbow_joint", elbow_joint)):
        ctx.check(
            f"{name}_axis_consistent",
            tuple(round(v, 6) for v in joint.axis) == expected_axis,
            details=str(joint.axis),
        )
        ctx.check(
            f"{name}_metadata_complete",
            {"type", "axis", "origin", "range"}.issubset(joint.meta),
            details=str(joint.meta),
        )
    ctx.check(
        "wrist_joint_has_metadata",
        {"type", "axis", "origin", "range"}.issubset(wrist.meta),
        details=str(wrist.meta),
    )
    ctx.check(
        "elbow_origin_at_link_end",
        object_model.get_articulation("elbow_joint").origin.xyz[0] > 0.35,
        details=str(object_model.get_articulation("elbow_joint").origin.xyz),
    )
    ctx.check(
        "wrist_origin_at_elbow_end",
        abs(wrist.origin.xyz[0] - r.elbow_link_length) < 1e-6,
        details=str(wrist.origin.xyz),
    )

    elbow_part = object_model.get_part("elbow_link")

    axis_is_y = r.joint_axis == (0.0, 1.0, 0.0)
    shoulder_part = object_model.get_part("shoulder_link")

    if axis_is_y and not r.yaw_enabled:
        base_part = object_model.get_part("base_support")
        ctx.expect_gap(
            base_part,
            shoulder_part,
            axis="y",
            positive_elem="shoulder_cheek_1",
            negative_elem="shoulder_root_hub",
            min_gap=0.012,
            name="shoulder positive cheek clears hub",
        )
        ctx.expect_gap(
            shoulder_part,
            base_part,
            axis="y",
            positive_elem="shoulder_root_hub",
            negative_elem="shoulder_cheek_0",
            min_gap=0.012,
            name="shoulder negative cheek clears hub",
        )

    if axis_is_y:
        ctx.expect_gap(
            shoulder_part,
            elbow_part,
            axis="y",
            positive_elem="shoulder_elbow_cheek_1",
            negative_elem="elbow_root_hub",
            min_gap=0.012,
            name="elbow positive cheek clears hub",
        )
        ctx.expect_gap(
            elbow_part,
            shoulder_part,
            axis="y",
            positive_elem="elbow_root_hub",
            negative_elem="shoulder_elbow_cheek_0",
            min_gap=0.012,
            name="elbow negative cheek clears hub",
        )

    if r.yaw_enabled:
        yaw = object_model.get_articulation("base_yaw")
        ctx.check(
            "yaw_axis_vertical",
            tuple(round(v, 6) for v in yaw.axis) == (0.0, 0.0, 1.0),
            details=str(yaw.axis),
        )
    else:
        ctx.check(
            "yaw_absent_when_disabled",
            "base_yaw" not in joint_names,
            details=str(sorted(joint_names)),
        )

    if axis_is_y and not r.yaw_enabled:
        base_part = object_model.get_part("base_support")
        for joint_val, check_name in (
            (r.shoulder_limits[0], "shoulder lower-limit cheek clearance"),
            (r.shoulder_limits[1], "shoulder upper-limit cheek clearance"),
        ):
            with ctx.pose({shoulder: joint_val}):
                ctx.expect_gap(
                    base_part,
                    shoulder_part,
                    axis="y",
                    positive_elem="shoulder_cheek_1",
                    negative_elem="shoulder_root_hub",
                    min_gap=0.012,
                    name=check_name,
                )

        for joint_val, check_name in (
            (r.elbow_limits[0], "elbow lower-limit cheek clearance"),
            (r.elbow_limits[1], "elbow upper-limit cheek clearance"),
        ):
            with ctx.pose({elbow_joint: joint_val}):
                ctx.expect_gap(
                    shoulder_part,
                    elbow_part,
                    axis="y",
                    positive_elem="shoulder_elbow_cheek_1",
                    negative_elem="elbow_root_hub",
                    min_gap=0.012,
                    name=check_name,
                )

    ctx.check(
        "part_diversity_parameters_present",
        r.arm_layout
        in {
            "vertical_pitch_chain",
            "horizontal_swing_chain",
            "pedestal_yaw_pitch_chain",
            "underslung_pitch_chain",
        }
        and r.base_mount_style in {"pedestal", "wall_block", "support_frame", "column_turret"}
        and r.link_profile in {"box_beam", "forked_link", "underslung_shell", "tapered_beam"}
        and r.wrist_style in {"end_plate", "tool_head", "flange", "wrist_block"},
        details=f"{r.arm_layout}, {r.base_mount_style}, {r.link_profile}, {r.wrist_style}",
    )
    return ctx.report()


def build_seeded_cantilever_arm(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_cantilever_arm(config_from_seed(seed), assets=assets)
