# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for a multi-segment fold-out arm."""

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

SegmentCount = Literal[3, 4, 5]
BaseStyle = Literal["pedestal_clevis", "wall_hinge_plate", "bench_clamp", "floor_carriage"]
LinkProfile = Literal["boxed_clevis", "round_tube", "twin_sideplates", "ladder_truss"]
AxisFamily = Literal["pitch_stack", "yaw_stack", "alternating_pitch_yaw"]
EndModule = Literal["plain_cap", "load_hook", "sensor_pod", "flat_mount", "cable_eye"]
MaterialStyle = Literal["safety_orange", "shop_gray", "lab_white", "dark_steel"]

SEGMENT_COUNTS: tuple[SegmentCount, ...] = (3, 4, 5)
BASE_STYLES: tuple[BaseStyle, ...] = (
    "pedestal_clevis",
    "wall_hinge_plate",
    "bench_clamp",
    "floor_carriage",
)
LINK_PROFILES: tuple[LinkProfile, ...] = (
    "boxed_clevis",
    "round_tube",
    "twin_sideplates",
    "ladder_truss",
)
AXIS_FAMILIES: tuple[AxisFamily, ...] = (
    "pitch_stack",
    "yaw_stack",
    "alternating_pitch_yaw",
)
END_MODULES: tuple[EndModule, ...] = (
    "plain_cap",
    "load_hook",
    "sensor_pod",
    "flat_mount",
    "cable_eye",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "safety_orange",
    "shop_gray",
    "lab_white",
    "dark_steel",
)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "safety_orange": {
        "base": (0.22, 0.24, 0.27, 1.0),
        "link": (0.92, 0.48, 0.12, 1.0),
        "joint": (0.07, 0.075, 0.08, 1.0),
        "accent": (0.98, 0.86, 0.18, 1.0),
        "tool": (0.18, 0.19, 0.20, 1.0),
        "pad": (0.035, 0.035, 0.038, 1.0),
    },
    "shop_gray": {
        "base": (0.39, 0.41, 0.42, 1.0),
        "link": (0.62, 0.64, 0.63, 1.0),
        "joint": (0.13, 0.14, 0.15, 1.0),
        "accent": (0.18, 0.40, 0.58, 1.0),
        "tool": (0.24, 0.25, 0.26, 1.0),
        "pad": (0.05, 0.05, 0.052, 1.0),
    },
    "lab_white": {
        "base": (0.78, 0.78, 0.74, 1.0),
        "link": (0.88, 0.86, 0.80, 1.0),
        "joint": (0.20, 0.21, 0.22, 1.0),
        "accent": (0.10, 0.36, 0.62, 1.0),
        "tool": (0.56, 0.58, 0.58, 1.0),
        "pad": (0.035, 0.04, 0.045, 1.0),
    },
    "dark_steel": {
        "base": (0.055, 0.060, 0.066, 1.0),
        "link": (0.14, 0.145, 0.15, 1.0),
        "joint": (0.52, 0.50, 0.43, 1.0),
        "accent": (0.62, 0.18, 0.13, 1.0),
        "tool": (0.075, 0.080, 0.085, 1.0),
        "pad": (0.010, 0.010, 0.012, 1.0),
    },
}


@dataclass(frozen=True)
class MultisegmentFoldoutArmConfig:
    segment_count: SegmentCount | None = None
    base_style: BaseStyle | None = None
    link_profile: LinkProfile | None = None
    axis_family: AxisFamily | None = None
    end_module: EndModule | None = None
    material_style: MaterialStyle = "safety_orange"
    reach: float = 0.88
    first_segment_ratio: float = 1.08
    link_width: float = 0.052
    hinge_clearance: float = 0.006
    joint_limit_scale: float = 1.0
    name: str = "multisegment_foldout_arm"


@dataclass(frozen=True)
class ResolvedMultisegmentFoldoutArmConfig:
    segment_count: SegmentCount
    base_style: BaseStyle
    link_profile: LinkProfile
    axis_family: AxisFamily
    end_module: EndModule
    material_style: MaterialStyle
    lengths: tuple[float, ...]
    link_width: float
    link_height: float
    hinge_clearance: float
    root_origin: tuple[float, float, float]
    axes: tuple[tuple[float, float, float], ...]
    limits: tuple[tuple[float, float], ...]
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# Worst-case same-sign cumulative fold (radians) of the whole serial arm before a
# distal segment curls back through the base/proximal envelope. Every revolute joint
# folds toward the same (negative) side, so the largest |cumulative turn| the motion-QC
# sampler can command for the distal segment is ``segment_count * |lower|`` (the
# all-same-sign stack; any non-adjacent pair spans a sub-chain and folds strictly less).
# Keeping that under this budget guarantees no non-adjacent segment pair meets for ANY
# independent joint combo. ~239 deg leaves generous chord clearance vs the compact base
# even for the longest reach; validated by the extreme-fold overlap tests below.
_FOLD_TURN_BUDGET = 4.18


def _safe_fold_limit(base_lower_mag: float, segment_count: int, scale: float) -> float:
    """Single-source shared fold magnitude for every joint (Contract 3c).

    Caps the shared negative fold limit so ``segment_count * |lower| <= budget`` — the
    fully-folded stack cannot wrap back into the base or a proximal segment, independent
    of ``scale``. The small positive ``upper`` never wraps (its cumulative stays < pi).
    """
    cap = _FOLD_TURN_BUDGET / segment_count
    return min(base_lower_mag * scale, cap)


def config_from_seed(seed: int) -> MultisegmentFoldoutArmConfig:
    rng = random.Random(seed)
    return MultisegmentFoldoutArmConfig(
        segment_count=rng.choice(SEGMENT_COUNTS),
        base_style=rng.choice(BASE_STYLES),
        link_profile=rng.choice(LINK_PROFILES),
        axis_family=rng.choice(AXIS_FAMILIES),
        end_module=rng.choice(END_MODULES),
        material_style=rng.choice(MATERIAL_STYLES),
        reach=rng.uniform(0.64, 1.22),
        first_segment_ratio=rng.uniform(0.92, 1.18),
        link_width=rng.uniform(0.040, 0.070),
        hinge_clearance=rng.uniform(0.004, 0.010),
        joint_limit_scale=rng.uniform(0.86, 1.16),
        name=f"seeded_multisegment_foldout_arm_{seed}",
    )


def resolve_config(
    config: MultisegmentFoldoutArmConfig | None = None,
) -> ResolvedMultisegmentFoldoutArmConfig:
    cfg = config or MultisegmentFoldoutArmConfig()
    segment_count = _pick(cfg.segment_count, SEGMENT_COUNTS)
    base_style = _pick(cfg.base_style, BASE_STYLES)
    link_profile = _pick(cfg.link_profile, LINK_PROFILES)
    axis_family = _pick(cfg.axis_family, AXIS_FAMILIES)
    end_module = _pick(cfg.end_module, END_MODULES)
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)

    reach = _clamp(cfg.reach, 0.54, 1.34)
    link_width = _clamp(cfg.link_width, 0.036, 0.078)
    link_height = max(0.032, link_width * 0.82)
    hinge_clearance = _clamp(cfg.hinge_clearance, 0.0035, 0.012)
    first_segment_ratio = _clamp(cfg.first_segment_ratio, 0.82, 1.26)

    weights = [first_segment_ratio * (0.90**i) for i in range(segment_count)]
    weight_total = sum(weights)
    min_len = max(0.13, link_width * 3.0)
    lengths = tuple(max(min_len, reach * weight / weight_total) for weight in weights)
    actual_reach = sum(lengths)
    if actual_reach > reach * 1.10:
        scale = reach / actual_reach
        lengths = tuple(max(min_len * 0.92, length * scale) for length in lengths)

    if axis_family == "pitch_stack":
        axes = tuple((0.0, 1.0, 0.0) for _ in range(segment_count))
    elif axis_family == "yaw_stack":
        axes = tuple((0.0, 0.0, 1.0) for _ in range(segment_count))
    else:
        axes = tuple(
            (0.0, 1.0, 0.0) if i % 2 == 0 else (0.0, 0.0, 1.0) for i in range(segment_count)
        )

    scale = _clamp(cfg.joint_limit_scale, 0.72, 1.28)
    fold_lower = _safe_fold_limit(1.55, segment_count, scale)
    limits = tuple((-fold_lower, 0.22 * scale) for _ in range(segment_count))

    return ResolvedMultisegmentFoldoutArmConfig(
        segment_count=segment_count,
        base_style=base_style,
        link_profile=link_profile,
        axis_family=axis_family,
        end_module=end_module,
        material_style=material_style,
        lengths=lengths,
        link_width=link_width,
        link_height=link_height,
        hinge_clearance=hinge_clearance,
        root_origin=(0.0, 0.0, max(0.12, link_width * 2.8)),
        axes=axes,
        limits=limits,
        name=cfg.name or "multisegment_foldout_arm",
    )


def with_overrides(
    config: MultisegmentFoldoutArmConfig, **kwargs: object
) -> MultisegmentFoldoutArmConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: MultisegmentFoldoutArmConfig | ResolvedMultisegmentFoldoutArmConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedMultisegmentFoldoutArmConfig)
        else resolve_config(config)
    )
    return (
        ("joint_multiplicity", f"{r.segment_count}_foldout_segments"),
        ("base", r.base_style),
        ("link_profile", r.link_profile),
        ("hinge_axis_family", r.axis_family),
        ("end_module", r.end_module),
        ("material_palette", r.material_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _mat(model: ArticulatedObject, r: ResolvedMultisegmentFoldoutArmConfig, key: str):
    return model.material(f"foldout_arm_{key}", rgba=PALETTES[r.material_style][key])


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _build_base(model: ArticulatedObject, r: ResolvedMultisegmentFoldoutArmConfig, mats):
    base = model.part("base")
    w = r.link_width
    h = r.link_height
    socket_depth = max(0.030, w * 0.62)
    sx, sy, sz = r.root_origin

    _box(
        base,
        (socket_depth, w * 1.70, h * 1.42),
        (sx - socket_depth * 0.5, sy, sz),
        mats["joint"],
        "root_clevis_socket",
    )
    _cyl(
        base,
        h * 0.44,
        w * 1.78,
        (sx - socket_depth * 0.5, sy, sz),
        mats["joint"],
        "root_hinge_pin",
        (math.pi / 2.0, 0.0, 0.0),
    )
    _box(
        base,
        (socket_depth * 1.18, w * 1.08, sz),
        (sx - socket_depth * 0.72, sy, sz * 0.5),
        mats["base"],
        "root_support_web",
    )

    if r.base_style == "pedestal_clevis":
        _box(
            base, (w * 4.2, w * 3.0, 0.036), (sx - w * 0.42, sy, 0.018), mats["base"], "floor_plate"
        )
        _cyl(
            base,
            w * 0.72,
            sz,
            (sx - socket_depth * 0.72, sy, sz * 0.5),
            mats["base"],
            "pedestal_column",
        )
    elif r.base_style == "wall_hinge_plate":
        _box(
            base,
            (0.044, w * 3.8, max(0.22, sz * 1.65)),
            (sx - socket_depth * 1.62, sy, max(0.11, sz * 0.74)),
            mats["base"],
            "wall_mount_plate",
        )
        for y in (-w * 1.20, w * 1.20):
            for z in (sz * 0.35, sz * 1.10):
                _cyl(
                    base,
                    w * 0.090,
                    0.012,
                    (sx - socket_depth * 2.16, y, z),
                    mats["accent"],
                    f"wall_bolt_{y:.2f}_{z:.2f}",
                    (0.0, math.pi / 2.0, 0.0),
                )
    elif r.base_style == "bench_clamp":
        _box(
            base,
            (w * 4.0, w * 2.4, 0.032),
            (sx - w * 0.50, sy, 0.016),
            mats["base"],
            "bench_top_jaw",
        )
        _box(
            base,
            (w * 0.52, w * 2.2, sz * 0.72),
            (sx - w * 1.85, sy, sz * 0.40),
            mats["base"],
            "clamp_back",
        )
        _box(
            base,
            (w * 2.6, w * 2.0, 0.026),
            (sx - w * 0.85, sy, sz * 0.26),
            mats["base"],
            "lower_clamp_jaw",
        )
        _cyl(
            base,
            w * 0.13,
            sz * 0.50,
            (sx - w * 0.20, sy, sz * 0.37),
            mats["accent"],
            "clamp_screw",
        )
    else:
        _box(
            base,
            (w * 5.2, w * 1.35, 0.032),
            (sx - w * 0.10, sy, 0.016),
            mats["base"],
            "floor_track",
        )
        _box(
            base,
            (w * 1.9, w * 2.5, 0.050),
            (sx - socket_depth * 0.78, sy, 0.056),
            mats["base"],
            "rolling_carriage",
        )
        _box(
            base,
            (w * 0.30, w * 2.6, 0.038),
            (sx - w * 2.35, sy, 0.046),
            mats["accent"],
            "rear_track_stop",
        )
        _box(
            base,
            (w * 0.30, w * 2.6, 0.038),
            (sx + w * 1.85, sy, 0.046),
            mats["accent"],
            "front_track_stop",
        )

    return base


def _add_link_body(
    part, r: ResolvedMultisegmentFoldoutArmConfig, mats, *, length: float, index: int
) -> None:
    w = r.link_width * (0.94**index)
    h = r.link_height * (0.96**index)
    hub_depth = max(0.030, w * 0.62)
    distal_depth = max(0.026, w * 0.54)
    body_len = max(0.060, length - hub_depth - distal_depth)
    body_x = hub_depth + body_len * 0.5

    _box(
        part,
        (hub_depth, w * 1.20, h * 1.18),
        (hub_depth * 0.5, 0.0, 0.0),
        mats["joint"],
        "proximal_hub",
    )
    _cyl(
        part,
        h * 0.40,
        w * 1.34,
        (hub_depth * 0.5, 0.0, 0.0),
        mats["joint"],
        "proximal_barrel",
        (math.pi / 2.0, 0.0, 0.0),
    )
    _box(
        part,
        (distal_depth, w * 1.14, h * 1.10),
        (length - distal_depth * 0.5, 0.0, 0.0),
        mats["joint"],
        "distal_clevis_socket",
    )

    if r.link_profile == "boxed_clevis":
        _box(part, (body_len, w * 0.72, h * 0.72), (body_x, 0.0, 0.0), mats["link"], "boxed_beam")
        _box(
            part,
            (body_len * 0.92, w * 0.20, h * 0.88),
            (body_x, -w * 0.40, 0.0),
            mats["accent"],
            "left_edge_flange",
        )
        _box(
            part,
            (body_len * 0.92, w * 0.20, h * 0.88),
            (body_x, w * 0.40, 0.0),
            mats["accent"],
            "right_edge_flange",
        )
    elif r.link_profile == "round_tube":
        _cyl(
            part,
            h * 0.34,
            body_len,
            (body_x, 0.0, 0.0),
            mats["link"],
            "round_tube",
            (0.0, math.pi / 2.0, 0.0),
        )
        _box(
            part,
            (body_len * 0.94, w * 0.22, h * 0.22),
            (body_x, 0.0, -h * 0.22),
            mats["accent"],
            "tube_bottom_web",
        )
    elif r.link_profile == "twin_sideplates":
        plate_t = max(0.006, w * 0.16)
        _box(
            part,
            (body_len, plate_t, h * 0.90),
            (body_x, -w * 0.36, 0.0),
            mats["link"],
            "left_sideplate",
        )
        _box(
            part,
            (body_len, plate_t, h * 0.90),
            (body_x, w * 0.36, 0.0),
            mats["link"],
            "right_sideplate",
        )
        for frac in (0.25, 0.55, 0.82):
            _box(
                part,
                (body_len * 0.10, w * 0.74, h * 0.24),
                (hub_depth + body_len * frac, 0.0, 0.0),
                mats["accent"],
                f"cross_tie_{frac:.2f}",
            )
    else:
        _box(part, (body_len, w * 0.30, h * 0.30), (body_x, 0.0, 0.0), mats["link"], "center_spine")
        for frac in (0.20, 0.42, 0.64, 0.84):
            _box(
                part,
                (body_len * 0.11, w * 0.72, h * 0.24),
                (hub_depth + body_len * frac, 0.0, h * 0.20),
                mats["accent"],
                f"upper_ladder_rung_{frac:.2f}",
            )
            _box(
                part,
                (body_len * 0.11, w * 0.72, h * 0.24),
                (hub_depth + body_len * frac, 0.0, -h * 0.20),
                mats["accent"],
                f"lower_ladder_rung_{frac:.2f}",
            )


def _add_end_module(
    part, r: ResolvedMultisegmentFoldoutArmConfig, mats, *, length: float, index: int
) -> None:
    w = r.link_width * (0.94**index)
    h = r.link_height * (0.96**index)
    neck_len = max(0.032, w * 0.72)
    neck_x = length + neck_len * 0.5
    _box(part, (neck_len, w * 0.48, h * 0.48), (neck_x, 0.0, 0.0), mats["tool"], "terminal_neck")

    tip_x = length + neck_len
    if r.end_module == "plain_cap":
        _box(
            part,
            (w * 0.42, w * 1.02, h * 1.02),
            (tip_x + w * 0.21, 0.0, 0.0),
            mats["tool"],
            "plain_end_cap",
        )
    elif r.end_module == "load_hook":
        _box(
            part,
            (w * 0.34, w * 0.34, h * 1.20),
            (tip_x + w * 0.17, 0.0, -h * 0.28),
            mats["tool"],
            "hook_shank",
        )
        _box(
            part,
            (w * 0.84, w * 0.34, h * 0.32),
            (tip_x + w * 0.42, 0.0, -h * 0.96),
            mats["tool"],
            "hook_foot",
        )
        _box(
            part,
            (w * 0.22, w * 0.34, h * 0.42),
            (tip_x + w * 0.73, 0.0, -h * 0.78),
            mats["accent"],
            "hook_lip",
        )
    elif r.end_module == "sensor_pod":
        _box(
            part,
            (w * 0.92, w * 0.88, h * 0.78),
            (tip_x + w * 0.46, 0.0, 0.0),
            mats["tool"],
            "sensor_body",
        )
        _cyl(
            part,
            h * 0.22,
            w * 0.10,
            (tip_x + w * 0.94, 0.0, 0.0),
            mats["pad"],
            "sensor_lens",
            (0.0, math.pi / 2.0, 0.0),
        )
    elif r.end_module == "flat_mount":
        _box(
            part,
            (w * 0.24, w * 1.42, h * 1.18),
            (tip_x + w * 0.12, 0.0, 0.0),
            mats["tool"],
            "flat_mount_plate",
        )
        for y in (-w * 0.42, w * 0.42):
            _cyl(
                part,
                w * 0.055,
                w * 0.08,
                (tip_x + w * 0.25, y, h * 0.26),
                mats["accent"],
                f"mount_bolt_{y:.2f}",
                (0.0, math.pi / 2.0, 0.0),
            )
    else:
        _box(
            part,
            (w * 0.72, w * 0.32, h * 0.78),
            (tip_x + w * 0.36, -w * 0.28, 0.0),
            mats["tool"],
            "left_eye_cheek",
        )
        _box(
            part,
            (w * 0.72, w * 0.32, h * 0.78),
            (tip_x + w * 0.36, w * 0.28, 0.0),
            mats["tool"],
            "right_eye_cheek",
        )
        _cyl(
            part,
            h * 0.22,
            w * 0.88,
            (tip_x + w * 0.42, 0.0, 0.0),
            mats["accent"],
            "eye_cross_pin",
            (math.pi / 2.0, 0.0, 0.0),
        )


def _build_segment(
    model: ArticulatedObject,
    r: ResolvedMultisegmentFoldoutArmConfig,
    mats,
    *,
    index: int,
    length: float,
    is_terminal: bool,
):
    part = model.part(f"segment_{index + 1}")
    _add_link_body(part, r, mats, length=length, index=index)
    if is_terminal:
        _add_end_module(part, r, mats, length=length, index=index)
    return part


def build_multisegment_foldout_arm(
    config: MultisegmentFoldoutArmConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {key: _mat(model, r, key) for key in ("base", "link", "joint", "accent", "tool", "pad")}

    base = _build_base(model, r, mats)
    segments = [
        _build_segment(
            model,
            r,
            mats,
            index=i,
            length=length,
            is_terminal=(i == r.segment_count - 1),
        )
        for i, length in enumerate(r.lengths)
    ]

    parent = base
    parent_name = "base"
    for i, segment in enumerate(segments):
        joint_name = "base_to_segment_1" if i == 0 else f"segment_{i}_to_segment_{i + 1}"
        origin = r.root_origin if i == 0 else (r.lengths[i - 1], 0.0, 0.0)
        parent_face = "root_clevis_socket" if i == 0 else "distal_clevis_socket"
        lower, upper = r.limits[i]
        model.articulation(
            joint_name,
            ArticulationType.REVOLUTE,
            parent=parent,
            child=segment,
            origin=Origin(xyz=origin),
            axis=r.axes[i],
            motion_limits=MotionLimits(
                lower=lower, upper=upper, effort=14.0 - i * 1.8, velocity=1.2 + i * 0.16
            ),
            mating=MatingContract(
                parent_face,
                "positive_x",
                "proximal_hub",
                "negative_x",
                contact_tol=0.002,
            ),
        )
        parent = segment
        parent_name = segment.name

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["segment_count"] = r.segment_count
    model.meta["terminal_parent"] = parent_name
    return model


def build_seeded_multisegment_foldout_arm(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_multisegment_foldout_arm(config_from_seed(seed), assets=assets)


def _aabb_center(aabb) -> tuple[float, float, float]:
    return (
        (aabb[0][0] + aabb[1][0]) * 0.5,
        (aabb[0][1] + aabb[1][1]) * 0.5,
        (aabb[0][2] + aabb[1][2]) * 0.5,
    )


def _allow_expected_overlaps(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedMultisegmentFoldoutArmConfig
) -> None:
    ctx.allow_overlap(
        model.get_part("base"),
        model.get_part("segment_1"),
        reason="root clevis socket and first segment hub intentionally capture the hinge pin",
    )
    for i in range(1, r.segment_count):
        ctx.allow_overlap(
            model.get_part(f"segment_{i}"),
            model.get_part(f"segment_{i + 1}"),
            reason="adjacent fold-out link clevis and hub intentionally share a hinge bearing",
        )


def run_multisegment_foldout_arm_tests(
    object_model: ArticulatedObject,
    config: MultisegmentFoldoutArmConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model, r)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.018)
    ctx.fail_if_joint_mating_has_gap()

    expected_parts = {"base"} | {f"segment_{i}" for i in range(1, r.segment_count + 1)}
    part_names = {part.name for part in object_model.parts}
    ctx.check(
        "identity_parts_present",
        expected_parts.issubset(part_names),
        details=str(sorted(part_names)),
    )
    ctx.check(
        "joint_multiplicity",
        len(object_model.joints) == r.segment_count,
        details=f"got {len(object_model.joints)} expected {r.segment_count}",
    )

    for i in range(r.segment_count):
        joint_name = "base_to_segment_1" if i == 0 else f"segment_{i}_to_segment_{i + 1}"
        joint = object_model.get_articulation(joint_name)
        expected_parent = "base" if i == 0 else f"segment_{i}"
        expected_child = f"segment_{i + 1}"
        ctx.check(
            f"{joint_name}_revolute",
            joint.articulation_type == ArticulationType.REVOLUTE,
            details=str(joint.articulation_type),
        )
        ctx.check(f"{joint_name}_axis", tuple(joint.axis) == r.axes[i], details=str(joint.axis))
        ctx.check(
            f"{joint_name}_parent_child",
            joint.parent == expected_parent and joint.child == expected_child,
            details=f"{joint.parent}->{joint.child}",
        )
        ctx.check(
            f"{joint_name}_mating",
            joint.mating is not None,
            details="fold-out hinge should mate visible faces",
        )

    slot_choices = dict(slot_choices_for_config(r))
    ctx.check(
        "joint_multiplicity_slot",
        slot_choices.get("joint_multiplicity") == f"{r.segment_count}_foldout_segments",
        details=str(slot_choices),
    )
    ctx.check(
        "slot_choices_recorded",
        dict(object_model.meta.get("slot_choices", ())) == slot_choices,
        details=str(object_model.meta.get("slot_choices")),
    )

    terminal = object_model.get_part(f"segment_{r.segment_count}")
    rest_aabb = ctx.part_world_aabb(terminal)
    pose = {}
    for i in range(r.segment_count):
        joint_name = "base_to_segment_1" if i == 0 else f"segment_{i}_to_segment_{i + 1}"
        joint = object_model.get_articulation(joint_name)
        pose[joint] = joint.motion_limits.lower * (0.20 + i * 0.035)
    with ctx.pose(pose):
        posed_aabb = ctx.part_world_aabb(terminal)
    if rest_aabb and posed_aabb:
        rest_center = _aabb_center(rest_aabb)
        posed_center = _aabb_center(posed_aabb)
        delta = math.sqrt(sum((posed_center[i] - rest_center[i]) ** 2 for i in range(3)))
        ctx.check("posed_terminal_moves", delta > 0.015, details=f"delta={delta:.4f}")

    # Lock the fold-budget invariant: the worst-case same-sign fold (the largest
    # cumulative turn the motion-QC sampler can command) must stay under the wrap budget
    # so no distal segment curls back through the base or a proximal segment.
    lower_mag = abs(r.limits[0][0])
    cumulative_fold = lower_mag * r.segment_count
    ctx.check(
        "fold_budget_respected",
        cumulative_fold <= _FOLD_TURN_BUDGET + 1e-6,
        details=f"cumulative_fold={cumulative_fold:.4f} budget={_FOLD_TURN_BUDGET:.4f}",
    )

    # Directly verify the two worst folds (every joint at its lower, then its upper
    # limit) drive no non-adjacent segment pair into contact. The allow_overlaps above
    # still cover the intentionally-captured adjacent hinge pivots.
    for tag, pick in (("lower", 0), ("upper", 1)):
        extreme = {}
        for i in range(r.segment_count):
            joint_name = "base_to_segment_1" if i == 0 else f"segment_{i}_to_segment_{i + 1}"
            extreme[object_model.get_articulation(joint_name)] = r.limits[i][pick]
        with ctx.pose(extreme):
            ctx.fail_if_parts_overlap_in_current_pose(name=f"no_overlap_at_full_fold_{tag}")

    return ctx.report()


__all__ = (
    "MultisegmentFoldoutArmConfig",
    "ResolvedMultisegmentFoldoutArmConfig",
    "build_multisegment_foldout_arm",
    "build_seeded_multisegment_foldout_arm",
    "config_from_seed",
    "resolve_config",
    "run_multisegment_foldout_arm_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
