# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for a shoulder-elbow-wrist robotic arm."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
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

KinematicLayout = Literal["yaw_pitch_pitch", "all_pitch", "planar_scara"]
BaseStyle = Literal["pedestal_column", "wall_bracket", "floor_track", "controller_box"]
LinkProfile = Literal["box_beam", "round_tube", "twin_sideplates", "truss_braced"]
WristModule = Literal[
    "tool_flange",
    "parallel_gripper",
    "camera_pod",
    "welding_nozzle",
    "magnetic_pad",
]
MaterialStyle = Literal["industrial_gray", "safety_orange", "lab_white", "dark_anodized"]

KINEMATIC_LAYOUTS: tuple[KinematicLayout, ...] = (
    "yaw_pitch_pitch",
    "all_pitch",
    "planar_scara",
)
BASE_STYLES: tuple[BaseStyle, ...] = (
    "pedestal_column",
    "wall_bracket",
    "floor_track",
    "controller_box",
)
LINK_PROFILES: tuple[LinkProfile, ...] = (
    "box_beam",
    "round_tube",
    "twin_sideplates",
    "truss_braced",
)
WRIST_MODULES: tuple[WristModule, ...] = (
    "tool_flange",
    "parallel_gripper",
    "camera_pod",
    "welding_nozzle",
    "magnetic_pad",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "industrial_gray",
    "safety_orange",
    "lab_white",
    "dark_anodized",
)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "industrial_gray": {
        "base": (0.42, 0.44, 0.45, 1.0),
        "link": (0.58, 0.60, 0.60, 1.0),
        "joint": (0.12, 0.13, 0.14, 1.0),
        "accent": (0.86, 0.63, 0.20, 1.0),
        "tool": (0.20, 0.21, 0.22, 1.0),
        "pad": (0.025, 0.025, 0.026, 1.0),
    },
    "safety_orange": {
        "base": (0.20, 0.22, 0.23, 1.0),
        "link": (0.92, 0.40, 0.12, 1.0),
        "joint": (0.08, 0.08, 0.08, 1.0),
        "accent": (0.98, 0.88, 0.20, 1.0),
        "tool": (0.16, 0.17, 0.18, 1.0),
        "pad": (0.02, 0.02, 0.02, 1.0),
    },
    "lab_white": {
        "base": (0.78, 0.79, 0.76, 1.0),
        "link": (0.88, 0.87, 0.82, 1.0),
        "joint": (0.22, 0.23, 0.24, 1.0),
        "accent": (0.10, 0.36, 0.58, 1.0),
        "tool": (0.54, 0.56, 0.55, 1.0),
        "pad": (0.04, 0.045, 0.05, 1.0),
    },
    "dark_anodized": {
        "base": (0.055, 0.060, 0.066, 1.0),
        "link": (0.13, 0.14, 0.15, 1.0),
        "joint": (0.58, 0.54, 0.44, 1.0),
        "accent": (0.56, 0.18, 0.12, 1.0),
        "tool": (0.07, 0.075, 0.08, 1.0),
        "pad": (0.008, 0.008, 0.010, 1.0),
    },
}


@dataclass(frozen=True)
class ShoulderElbowWristArmConfig:
    kinematic_layout: KinematicLayout | None = None
    base_style: BaseStyle | None = None
    link_profile: LinkProfile | None = None
    wrist_module: WristModule | None = None
    material_style: MaterialStyle = "industrial_gray"
    reach: float = 0.72
    upper_ratio: float = 0.52
    shoulder_z: float = 0.24
    link_width: float = 0.060
    joint_limit_scale: float = 1.0
    name: str = "shoulderelbowwrist_arm"


@dataclass(frozen=True)
class ResolvedShoulderElbowWristArmConfig:
    kinematic_layout: KinematicLayout
    base_style: BaseStyle
    link_profile: LinkProfile
    wrist_module: WristModule
    material_style: MaterialStyle
    upper_len: float
    forearm_len: float
    wrist_len: float
    shoulder_z: float
    link_width: float
    link_height: float
    shoulder_origin: tuple[float, float, float]
    shoulder_axis: tuple[float, float, float]
    elbow_axis: tuple[float, float, float]
    wrist_axis: tuple[float, float, float]
    shoulder_limit: tuple[float, float]
    elbow_limit: tuple[float, float]
    wrist_limit: tuple[float, float]
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> ShoulderElbowWristArmConfig:
    rng = random.Random(seed)
    return ShoulderElbowWristArmConfig(
        kinematic_layout=rng.choice(KINEMATIC_LAYOUTS),
        base_style=rng.choice(BASE_STYLES),
        link_profile=rng.choice(LINK_PROFILES),
        wrist_module=rng.choice(WRIST_MODULES),
        material_style=rng.choice(MATERIAL_STYLES),
        reach=rng.uniform(0.52, 1.12),
        upper_ratio=rng.uniform(0.47, 0.60),
        shoulder_z=rng.uniform(0.16, 0.36),
        link_width=rng.uniform(0.044, 0.078),
        joint_limit_scale=rng.uniform(0.82, 1.18),
        name=f"seeded_shoulderelbowwrist_arm_{seed}",
    )


def resolve_config(
    config: ShoulderElbowWristArmConfig | None = None,
) -> ResolvedShoulderElbowWristArmConfig:
    cfg = config or ShoulderElbowWristArmConfig()
    kinematic_layout = _pick(cfg.kinematic_layout, KINEMATIC_LAYOUTS)
    base_style = _pick(cfg.base_style, BASE_STYLES)
    link_profile = _pick(cfg.link_profile, LINK_PROFILES)
    wrist_module = _pick(cfg.wrist_module, WRIST_MODULES)
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)

    reach = _clamp(cfg.reach, 0.46, 1.24)
    upper_ratio = _clamp(cfg.upper_ratio, 0.44, 0.62)
    wrist_len = max(0.060, reach * 0.13)
    upper_len = max(0.20, (reach - wrist_len) * upper_ratio)
    forearm_len = max(0.18, reach - wrist_len - upper_len)
    link_width = _clamp(cfg.link_width, 0.038, 0.088)
    link_height = max(0.036, link_width * 0.78)
    shoulder_z = _clamp(cfg.shoulder_z, 0.12, 0.42)
    scale = _clamp(cfg.joint_limit_scale, 0.70, 1.30)

    if kinematic_layout == "all_pitch":
        shoulder_axis = (0.0, 1.0, 0.0)
        elbow_axis = (0.0, 1.0, 0.0)
        wrist_axis = (0.0, 1.0, 0.0)
    elif kinematic_layout == "planar_scara":
        shoulder_axis = (0.0, 0.0, 1.0)
        elbow_axis = (0.0, 0.0, 1.0)
        wrist_axis = (0.0, 0.0, 1.0)
    else:
        shoulder_axis = (0.0, 0.0, 1.0)
        elbow_axis = (0.0, 1.0, 0.0)
        wrist_axis = (0.0, 1.0, 0.0)

    return ResolvedShoulderElbowWristArmConfig(
        kinematic_layout=kinematic_layout,
        base_style=base_style,
        link_profile=link_profile,
        wrist_module=wrist_module,
        material_style=material_style,
        upper_len=upper_len,
        forearm_len=forearm_len,
        wrist_len=wrist_len,
        shoulder_z=shoulder_z,
        link_width=link_width,
        link_height=link_height,
        shoulder_origin=(0.0, 0.0, shoulder_z),
        shoulder_axis=shoulder_axis,
        elbow_axis=elbow_axis,
        wrist_axis=wrist_axis,
        shoulder_limit=(-1.30 * scale, 1.35 * scale),
        elbow_limit=(-1.65 * scale, 1.20 * scale),
        wrist_limit=(-1.05 * scale, 1.05 * scale),
        name=cfg.name or "shoulderelbowwrist_arm",
    )


def with_overrides(
    config: ShoulderElbowWristArmConfig, **kwargs: object
) -> ShoulderElbowWristArmConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ShoulderElbowWristArmConfig | ResolvedShoulderElbowWristArmConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedShoulderElbowWristArmConfig)
        else resolve_config(config)
    )
    return (
        ("kinematic_layout", r.kinematic_layout),
        ("joint_multiplicity", "3_named_joints"),
        ("base", r.base_style),
        ("link_profile", r.link_profile),
        ("wrist_module", r.wrist_module),
        ("material_palette", r.material_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _mat(model: ArticulatedObject, r: ResolvedShoulderElbowWristArmConfig, key: str):
    return model.material(f"shoulder_arm_{key}", rgba=PALETTES[r.material_style][key])


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _build_base(model: ArticulatedObject, r: ResolvedShoulderElbowWristArmConfig, mats):
    base = model.part("base")
    w = r.link_width
    h = r.link_height
    socket_depth = max(0.026, w * 0.58)
    sx, sy, sz = r.shoulder_origin

    _box(
        base,
        (socket_depth, w * 1.45, h * 1.35),
        (sx - socket_depth * 0.5, sy, sz),
        mats["joint"],
        "shoulder_socket",
    )
    _cyl(
        base,
        h * 0.46,
        w * 1.52,
        (sx - socket_depth * 0.5, sy, sz),
        mats["joint"],
        "shoulder_axis_cap",
        (math.pi / 2.0, 0.0, 0.0),
    )
    _box(
        base,
        (socket_depth * 1.15, w * 1.05, max(0.040, sz)),
        (sx - socket_depth * 0.78, sy, sz * 0.5),
        mats["base"],
        "shoulder_support_web",
    )

    if r.base_style == "pedestal_column":
        _cyl(
            base,
            w * 0.76,
            sz,
            (sx - socket_depth * 0.85, sy, sz * 0.5),
            mats["base"],
            "pedestal_column",
        )
        _box(
            base,
            (w * 3.8, w * 2.8, 0.035),
            (sx - socket_depth * 0.85, sy, 0.0175),
            mats["base"],
            "floor_plate",
        )
    elif r.base_style == "wall_bracket":
        _box(
            base,
            (0.050, w * 3.4, max(0.18, sz * 1.35)),
            (sx - socket_depth * 1.85, sy, sz * 0.55),
            mats["base"],
            "wall_plate",
        )
        for z in (sz * 0.22, sz * 0.82):
            _cyl(
                base,
                0.0045,
                0.010,
                (sx - socket_depth * 2.42, sy - w, z),
                mats["accent"],
                f"wall_bolt_low_{z:.2f}",
                (0.0, math.pi / 2.0, 0.0),
            )
            _cyl(
                base,
                0.0045,
                0.010,
                (sx - socket_depth * 2.42, sy + w, z),
                mats["accent"],
                f"wall_bolt_high_{z:.2f}",
                (0.0, math.pi / 2.0, 0.0),
            )
    elif r.base_style == "floor_track":
        _box(
            base,
            (w * 5.2, w * 1.25, 0.030),
            (sx - socket_depth * 0.25, sy, 0.015),
            mats["base"],
            "floor_track_rail",
        )
        _box(
            base,
            (w * 1.7, w * 2.4, 0.045),
            (sx - socket_depth * 0.90, sy, 0.052),
            mats["base"],
            "sliding_carriage",
        )
        _box(
            base,
            (w * 0.34, w * 2.5, 0.035),
            (sx - w * 1.70, sy, 0.045),
            mats["accent"],
            "left_track_stop",
        )
        _box(
            base,
            (w * 0.34, w * 2.5, 0.035),
            (sx + w * 1.70, sy, 0.045),
            mats["accent"],
            "right_track_stop",
        )
    else:
        _box(
            base,
            (w * 2.8, w * 2.2, max(0.10, sz * 0.55)),
            (sx - socket_depth * 0.95, sy, max(0.055, sz * 0.25)),
            mats["base"],
            "controller_box",
        )
        _box(
            base,
            (w * 1.2, 0.006, 0.028),
            (sx - socket_depth * 0.95, sy - w * 1.12, max(0.090, sz * 0.46)),
            mats["accent"],
            "status_panel",
        )
    return base


def _build_link(
    model: ArticulatedObject,
    r: ResolvedShoulderElbowWristArmConfig,
    mats,
    *,
    part_name: str,
    length: float,
    width: float,
    height: float,
    distal_socket_name: str,
):
    part = model.part(part_name)
    hub_depth = max(0.028, width * 0.54)
    distal_depth = max(0.024, width * 0.48)
    body_len = max(0.040, length - hub_depth - distal_depth)

    _box(
        part,
        (hub_depth, width * 1.12, height * 1.15),
        (hub_depth * 0.5, 0.0, 0.0),
        mats["joint"],
        "proximal_hub",
    )
    _cyl(
        part,
        height * 0.39,
        width * 1.20,
        (hub_depth * 0.5, 0.0, 0.0),
        mats["joint"],
        "proximal_barrel",
        (math.pi / 2.0, 0.0, 0.0),
    )
    _box(
        part,
        (distal_depth, width * 1.04, height * 1.04),
        (length - distal_depth * 0.5, 0.0, 0.0),
        mats["joint"],
        distal_socket_name,
    )

    body_x = hub_depth + body_len * 0.5
    if r.link_profile == "box_beam":
        _box(
            part,
            (body_len, width * 0.78, height * 0.76),
            (body_x, 0.0, 0.0),
            mats["link"],
            "box_beam_body",
        )
    elif r.link_profile == "round_tube":
        _cyl(
            part,
            height * 0.36,
            body_len,
            (body_x, 0.0, 0.0),
            mats["link"],
            "round_tube_body",
            (0.0, math.pi / 2.0, 0.0),
        )
        _box(
            part,
            (body_len * 0.96, width * 0.22, height * 0.26),
            (body_x, 0.0, -height * 0.05),
            mats["accent"],
            "tube_flat_web",
        )
    elif r.link_profile == "twin_sideplates":
        plate_t = max(0.006, width * 0.16)
        _box(
            part,
            (body_len, plate_t, height * 0.86),
            (body_x, -width * 0.34, 0.0),
            mats["link"],
            "left_sideplate",
        )
        _box(
            part,
            (body_len, plate_t, height * 0.86),
            (body_x, width * 0.34, 0.0),
            mats["link"],
            "right_sideplate",
        )
        for frac in (0.24, 0.70):
            _box(
                part,
                (body_len * 0.12, width * 0.70, height * 0.22),
                (hub_depth + body_len * frac, 0.0, 0.0),
                mats["accent"],
                f"cross_tie_{frac:.2f}",
            )
    else:
        _box(
            part,
            (body_len, width * 0.34, height * 0.34),
            (body_x, 0.0, 0.0),
            mats["link"],
            "center_spine",
        )
        for frac in (0.22, 0.50, 0.78):
            _box(
                part,
                (body_len * 0.14, width * 0.76, height * 0.18),
                (hub_depth + body_len * frac, 0.0, height * 0.22),
                mats["accent"],
                f"upper_truss_node_{frac:.2f}",
            )
            _box(
                part,
                (body_len * 0.14, width * 0.76, height * 0.18),
                (hub_depth + body_len * frac, 0.0, -height * 0.22),
                mats["accent"],
                f"lower_truss_node_{frac:.2f}",
            )

    return part


def _build_wrist_tool(model: ArticulatedObject, r: ResolvedShoulderElbowWristArmConfig, mats):
    part = model.part("wrist_tool")
    w = r.link_width * 0.78
    h = r.link_height * 0.88
    hub_depth = max(0.024, w * 0.54)
    tool_len = r.wrist_len
    _box(
        part,
        (hub_depth, w * 1.06, h * 1.06),
        (hub_depth * 0.5, 0.0, 0.0),
        mats["joint"],
        "wrist_hub",
    )
    _cyl(
        part,
        h * 0.38,
        w * 1.15,
        (hub_depth * 0.5, 0.0, 0.0),
        mats["joint"],
        "wrist_barrel",
        (math.pi / 2.0, 0.0, 0.0),
    )
    _box(
        part,
        (tool_len * 0.58, w * 0.58, h * 0.58),
        (hub_depth + tool_len * 0.29, 0.0, 0.0),
        mats["tool"],
        "wrist_neck",
    )

    tool_x = hub_depth + tool_len * 0.54
    if r.wrist_module == "tool_flange":
        _box(
            part,
            (tool_len * 0.26, w * 1.05, h * 1.05),
            (tool_x, 0.0, 0.0),
            mats["tool"],
            "tool_flange_plate",
        )
        for y in (-w * 0.32, w * 0.32):
            _cyl(
                part,
                0.0035,
                tool_len * 0.10,
                (tool_x + tool_len * 0.10, y, h * 0.24),
                mats["accent"],
                f"flange_bolt_{y:.2f}",
                (0.0, math.pi / 2.0, 0.0),
            )
    elif r.wrist_module == "parallel_gripper":
        _box(
            part,
            (tool_len * 0.22, w * 1.22, h * 0.70),
            (tool_x, 0.0, 0.0),
            mats["tool"],
            "gripper_palm",
        )
        _box(
            part,
            (tool_len * 0.48, w * 0.20, h * 0.32),
            (tool_x + tool_len * 0.32, -w * 0.42, 0.0),
            mats["pad"],
            "left_gripper_finger",
        )
        _box(
            part,
            (tool_len * 0.48, w * 0.20, h * 0.32),
            (tool_x + tool_len * 0.32, w * 0.42, 0.0),
            mats["pad"],
            "right_gripper_finger",
        )
    elif r.wrist_module == "camera_pod":
        _box(
            part,
            (tool_len * 0.48, w * 0.94, h * 0.86),
            (tool_x + tool_len * 0.12, 0.0, 0.0),
            mats["tool"],
            "camera_body",
        )
        _cyl(
            part,
            h * 0.24,
            tool_len * 0.08,
            (tool_x + tool_len * 0.40, 0.0, 0.0),
            mats["pad"],
            "lens",
            (0.0, math.pi / 2.0, 0.0),
        )
    elif r.wrist_module == "welding_nozzle":
        _cyl(
            part,
            h * 0.25,
            tool_len * 0.62,
            (tool_x + tool_len * 0.15, 0.0, 0.0),
            mats["tool"],
            "nozzle_body",
            (0.0, math.pi / 2.0, 0.0),
        )
        _cyl(
            part,
            h * 0.14,
            tool_len * 0.20,
            (tool_x + tool_len * 0.55, 0.0, 0.0),
            mats["accent"],
            "nozzle_tip",
            (0.0, math.pi / 2.0, 0.0),
        )
    else:
        _box(
            part,
            (tool_len * 0.28, w * 1.08, h * 0.84),
            (tool_x, 0.0, 0.0),
            mats["tool"],
            "magnet_carrier",
        )
        _box(
            part,
            (tool_len * 0.12, w * 1.18, h * 0.96),
            (tool_x + tool_len * 0.20, 0.0, 0.0),
            mats["pad"],
            "magnetic_pad",
        )
    return part


def build_shoulderelbowwrist_arm(
    config: ShoulderElbowWristArmConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {key: _mat(model, r, key) for key in ("base", "link", "joint", "accent", "tool", "pad")}

    base = _build_base(model, r, mats)
    upper_arm = _build_link(
        model,
        r,
        mats,
        part_name="upper_arm",
        length=r.upper_len,
        width=r.link_width,
        height=r.link_height,
        distal_socket_name="elbow_socket",
    )
    forearm = _build_link(
        model,
        r,
        mats,
        part_name="forearm",
        length=r.forearm_len,
        width=r.link_width * 0.86,
        height=r.link_height * 0.88,
        distal_socket_name="wrist_socket",
    )
    wrist_tool = _build_wrist_tool(model, r, mats)

    model.articulation(
        "shoulder_joint",
        ArticulationType.REVOLUTE,
        parent=base,
        child=upper_arm,
        origin=Origin(xyz=r.shoulder_origin),
        axis=r.shoulder_axis,
        motion_limits=MotionLimits(
            lower=r.shoulder_limit[0], upper=r.shoulder_limit[1], effort=8.0, velocity=1.8
        ),
        mating=MatingContract(
            "shoulder_socket", "positive_x", "proximal_hub", "negative_x", contact_tol=0.002
        ),
    )
    model.articulation(
        "elbow_joint",
        ArticulationType.REVOLUTE,
        parent=upper_arm,
        child=forearm,
        origin=Origin(xyz=(r.upper_len, 0.0, 0.0)),
        axis=r.elbow_axis,
        motion_limits=MotionLimits(
            lower=r.elbow_limit[0], upper=r.elbow_limit[1], effort=6.0, velocity=2.1
        ),
        mating=MatingContract(
            "elbow_socket", "positive_x", "proximal_hub", "negative_x", contact_tol=0.002
        ),
    )
    model.articulation(
        "wrist_joint",
        ArticulationType.REVOLUTE,
        parent=forearm,
        child=wrist_tool,
        origin=Origin(xyz=(r.forearm_len, 0.0, 0.0)),
        axis=r.wrist_axis,
        motion_limits=MotionLimits(
            lower=r.wrist_limit[0], upper=r.wrist_limit[1], effort=2.5, velocity=2.8
        ),
        mating=MatingContract(
            "wrist_socket", "positive_x", "wrist_hub", "negative_x", contact_tol=0.002
        ),
    )
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_shoulderelbowwrist_arm(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_shoulderelbowwrist_arm(config_from_seed(seed), assets=assets)


def _aabb_center(aabb) -> tuple[float, float, float]:
    return (
        (aabb[0][0] + aabb[1][0]) * 0.5,
        (aabb[0][1] + aabb[1][1]) * 0.5,
        (aabb[0][2] + aabb[1][2]) * 0.5,
    )


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    ctx.allow_overlap(
        model.get_part("base"),
        model.get_part("upper_arm"),
        reason="shoulder shaft and upper-arm bearing are intentionally coaxial",
    )
    ctx.allow_overlap(
        model.get_part("upper_arm"),
        model.get_part("forearm"),
        reason="elbow shaft and forearm bearing are intentionally coaxial",
    )
    ctx.allow_overlap(
        model.get_part("forearm"),
        model.get_part("wrist_tool"),
        reason="wrist shaft and wrist-tool bearing are intentionally coaxial",
    )


def run_shoulderelbowwrist_arm_tests(
    object_model: ArticulatedObject,
    config: ShoulderElbowWristArmConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.018)
    ctx.fail_if_joint_mating_has_gap()

    part_names = {part.name for part in object_model.parts}
    expected_parts = {"base", "upper_arm", "forearm", "wrist_tool"}
    ctx.check(
        "identity_parts_present",
        expected_parts.issubset(part_names),
        details=str(sorted(part_names)),
    )
    ctx.check(
        "joint_multiplicity",
        len(object_model.joints) == 3,
        details=f"got {len(object_model.joints)}",
    )

    expected_axes = {
        "shoulder_joint": r.shoulder_axis,
        "elbow_joint": r.elbow_axis,
        "wrist_joint": r.wrist_axis,
    }
    expected_parents = {
        "shoulder_joint": ("base", "upper_arm"),
        "elbow_joint": ("upper_arm", "forearm"),
        "wrist_joint": ("forearm", "wrist_tool"),
    }
    for joint_name, axis in expected_axes.items():
        joint = object_model.get_articulation(joint_name)
        ctx.check(
            f"{joint_name}_revolute",
            joint.articulation_type == ArticulationType.REVOLUTE,
            details=str(joint.articulation_type),
        )
        ctx.check(f"{joint_name}_axis", tuple(joint.axis) == axis, details=str(joint.axis))
        parent, child = expected_parents[joint_name]
        ctx.check(
            f"{joint_name}_parent_child",
            joint.parent == parent and joint.child == child,
            details=f"{joint.parent}->{joint.child}",
        )
        ctx.check(
            f"{joint_name}_mating",
            joint.mating is not None,
            details="named joint should mate adjacent hardware",
        )

    slot_choices = dict(slot_choices_for_config(r))
    ctx.check(
        "joint_multiplicity_slot",
        slot_choices.get("joint_multiplicity") == "3_named_joints",
        details=str(slot_choices),
    )
    ctx.check(
        "slot_choices_recorded",
        dict(object_model.meta.get("slot_choices", ())) == slot_choices,
        details=str(object_model.meta.get("slot_choices")),
    )

    wrist = object_model.get_part("wrist_tool")
    rest_aabb = ctx.part_world_aabb(wrist)
    shoulder = object_model.get_articulation("shoulder_joint")
    elbow = object_model.get_articulation("elbow_joint")
    wrist_joint = object_model.get_articulation("wrist_joint")
    pose = {
        shoulder: shoulder.motion_limits.upper * 0.35,
        elbow: elbow.motion_limits.upper * 0.45,
        wrist_joint: wrist_joint.motion_limits.upper * 0.40,
    }
    with ctx.pose(pose):
        posed_aabb = ctx.part_world_aabb(wrist)
    if rest_aabb and posed_aabb:
        rest_center = _aabb_center(rest_aabb)
        posed_center = _aabb_center(posed_aabb)
        delta = math.sqrt(sum((posed_center[i] - rest_center[i]) ** 2 for i in range(3)))
        ctx.check("posed_wrist_moves", delta > 0.015, details=f"delta={delta:.4f}")

    return ctx.report()


__all__ = (
    "ShoulderElbowWristArmConfig",
    "ResolvedShoulderElbowWristArmConfig",
    "build_shoulderelbowwrist_arm",
    "build_seeded_shoulderelbowwrist_arm",
    "config_from_seed",
    "resolve_config",
    "run_shoulderelbowwrist_arm_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
