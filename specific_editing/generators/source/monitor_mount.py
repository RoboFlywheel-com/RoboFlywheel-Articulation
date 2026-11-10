# SPDX-License-Identifier: Apache-2.0

"""Publication-facing monitor-mount snapshot with a repeatable arm chain.

The production template in ``agent/templates/monitor_mount.py`` faithfully
reproduces a two-link source asset. This task-local snapshot keeps its wall
mount, articulated VESA head, and material vocabulary, but exposes the arm as
an indexed serial module so paper figures can compare 2, 5, and 20 links.

This module is visualization-only. It intentionally omits the production
template's expensive motion-envelope solver and physics-oriented QC.
"""

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
    MotionLimits,
    MotionProperties,
    Origin,
)

__modular__ = True

ArmStyle = Literal["counterbalance_spring", "gas_strut", "simple_link"]
HeadStyle = Literal["vesa_yoke", "single_pivot", "compact_plate"]
WallStyle = Literal["wall_plate_lugs", "wall_plate_compact", "wall_plate_long"]
MountPaletteTheme = Literal["anodized_aluminum", "office_white", "matte_bronze"]

BASE_ARM_SEGMENT_COUNT = 5
ARM_SEGMENT_COUNTS = (2, BASE_ARM_SEGMENT_COUNT, 20)
ARM_STYLES: tuple[ArmStyle, ...] = (
    "counterbalance_spring",
    "gas_strut",
    "simple_link",
)
HEAD_STYLES: tuple[HeadStyle, ...] = (
    "vesa_yoke",
    "single_pivot",
    "compact_plate",
)
WALL_STYLES: tuple[WallStyle, ...] = (
    "wall_plate_lugs",
    "wall_plate_compact",
    "wall_plate_long",
)
PALETTE_THEMES: tuple[MountPaletteTheme, ...] = (
    "anodized_aluminum",
    "office_white",
    "matte_bronze",
)

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "anodized_aluminum": {
        "base": (0.075, 0.080, 0.090, 1.0),
        "link": (0.56, 0.59, 0.62, 1.0),
        "joint": (0.10, 0.11, 0.12, 1.0),
        "accent": (0.76, 0.55, 0.22, 1.0),
        "cover": (0.82, 0.83, 0.82, 1.0),
        "bezel": (0.025, 0.028, 0.032, 1.0),
        "screen": (0.055, 0.085, 0.115, 1.0),
    },
    "office_white": {
        "base": (0.22, 0.23, 0.24, 1.0),
        "link": (0.88, 0.88, 0.85, 1.0),
        "joint": (0.26, 0.27, 0.28, 1.0),
        "accent": (0.63, 0.65, 0.67, 1.0),
        "cover": (0.95, 0.95, 0.92, 1.0),
        "bezel": (0.035, 0.038, 0.042, 1.0),
        "screen": (0.060, 0.090, 0.120, 1.0),
    },
    "matte_bronze": {
        "base": (0.13, 0.10, 0.08, 1.0),
        "link": (0.43, 0.31, 0.20, 1.0),
        "joint": (0.10, 0.075, 0.055, 1.0),
        "accent": (0.72, 0.52, 0.25, 1.0),
        "cover": (0.25, 0.18, 0.13, 1.0),
        "bezel": (0.030, 0.025, 0.022, 1.0),
        "screen": (0.055, 0.080, 0.100, 1.0),
    },
}


@dataclass(frozen=True)
class MonitorMountConfig:
    arm_style: ArmStyle = "counterbalance_spring"
    head_style: HeadStyle = "vesa_yoke"
    wall_style: WallStyle = "wall_plate_lugs"
    palette_theme: MountPaletteTheme = "anodized_aluminum"
    arm_segment_count: int = 5
    arm_span: float = 1.10
    link_width: float = 0.064
    wall_plate_height: float = 0.52
    wall_plate_width: float = 0.36
    display_width: float = 0.42
    display_height: float = 0.27
    name: str = "monitor_mount"


@dataclass(frozen=True)
class ResolvedMonitorMountConfig:
    arm_style: ArmStyle
    head_style: HeadStyle
    wall_style: WallStyle
    palette_theme: MountPaletteTheme
    arm_segment_count: int
    arm_span: float
    segment_length: float
    link_width: float
    link_height: float
    wall_plate_height: float
    wall_plate_width: float
    shoulder_height: float
    display_width: float
    display_height: float
    bend_angle: float
    palette: dict[str, tuple[float, float, float, float]]
    name: str


def _choice(value, choices, label: str):
    if value not in choices:
        raise ValueError(f"{label} must be one of {choices}, got {value!r}")
    return value


def config_from_seed(seed: int) -> MonitorMountConfig:
    rng = random.Random(seed)
    return MonitorMountConfig(
        arm_style=rng.choice(ARM_STYLES),
        head_style=rng.choice(HEAD_STYLES),
        wall_style=rng.choice(WALL_STYLES),
        palette_theme=rng.choice(PALETTE_THEMES),
        arm_segment_count=rng.choice(ARM_SEGMENT_COUNTS),
        arm_span=round(rng.uniform(0.88, 1.34), 3),
        link_width=round(rng.uniform(0.052, 0.074), 3),
        display_width=round(rng.uniform(0.36, 0.48), 3),
        display_height=round(rng.uniform(0.23, 0.31), 3),
        name=f"seeded_monitor_mount_{seed}",
    )


def resolve_config(
    config: MonitorMountConfig | None = None,
) -> ResolvedMonitorMountConfig:
    cfg = config or MonitorMountConfig()
    arm_style = _choice(cfg.arm_style, ARM_STYLES, "arm_style")
    head_style = _choice(cfg.head_style, HEAD_STYLES, "head_style")
    wall_style = _choice(cfg.wall_style, WALL_STYLES, "wall_style")
    palette_theme = _choice(cfg.palette_theme, PALETTE_THEMES, "palette_theme")
    count = int(cfg.arm_segment_count)
    if count not in ARM_SEGMENT_COUNTS:
        raise ValueError(
            f"arm_segment_count must be one of {ARM_SEGMENT_COUNTS}, got {count}"
        )

    arm_span = max(0.78, min(float(cfg.arm_span), 1.42))
    link_width = max(0.048, min(float(cfg.link_width), 0.080))
    wall_h = max(0.38, min(float(cfg.wall_plate_height), 0.68))
    wall_w = max(0.28, min(float(cfg.wall_plate_width), 0.46))
    display_w = max(0.32, min(float(cfg.display_width), 0.52))
    display_h = max(0.20, min(float(cfg.display_height), 0.34))

    # ``arm_span`` is the authored span of the five-link Base. Count edits add
    # or remove complete modules without rescaling an individual arm segment.
    segment_length = arm_span / BASE_ARM_SEGMENT_COUNT
    return ResolvedMonitorMountConfig(
        arm_style=arm_style,
        head_style=head_style,
        wall_style=wall_style,
        palette_theme=palette_theme,
        arm_segment_count=count,
        arm_span=arm_span,
        segment_length=segment_length,
        link_width=link_width,
        link_height=link_width * 0.74,
        wall_plate_height=wall_h,
        wall_plate_width=wall_w,
        shoulder_height=wall_h * 0.58,
        display_width=display_w,
        display_height=display_h,
        bend_angle=math.radians(12.0),
        palette=dict(PALETTES[palette_theme]),
        name=cfg.name or "monitor_mount",
    )


def with_overrides(config: MonitorMountConfig, **kwargs: object) -> MonitorMountConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: MonitorMountConfig | ResolvedMonitorMountConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedMonitorMountConfig) else resolve_config(config)
    return (
        ("wall_style", str(r.wall_style)),
        ("arm_style", str(r.arm_style)),
        ("arm_segment_count", f"{r.arm_segment_count}_segments"),
        ("head_style", str(r.head_style)),
        ("palette_theme", str(r.palette_theme)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materialize(model: ArticulatedObject, r: ResolvedMonitorMountConfig) -> None:
    names = {
        "base": "monitor_mount_base",
        "link": "monitor_mount_link",
        "joint": "monitor_mount_joint",
        "accent": "monitor_mount_accent",
        "cover": "monitor_mount_cover",
        "bezel": "monitor_mount_bezel",
        "screen": "monitor_mount_screen",
    }
    for slot, name in names.items():
        model.material(name, rgba=r.palette[slot])


def _box(
    part,
    size,
    xyz,
    material,
    name,
    *,
    rpy=(0.0, 0.0, 0.0),
    class_id="metal.paint_coated",
) -> None:
    part.visual(
        Box(size),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name,
        material_class_id=class_id,
    )


def _cylinder(
    part,
    radius,
    length,
    xyz,
    material,
    name,
    *,
    rpy=(0.0, 0.0, 0.0),
    class_id="metal.stainless_matte",
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name,
        material_class_id=class_id,
    )


def _build_wall_bracket(part, r: ResolvedMonitorMountConfig) -> None:
    height = r.wall_plate_height
    width = r.wall_plate_width
    if r.wall_style == "wall_plate_compact":
        height *= 0.78
        width *= 0.82
    elif r.wall_style == "wall_plate_long":
        height *= 1.20
        width *= 0.90

    _box(
        part,
        (0.040, width, height),
        (-0.020, 0.0, height * 0.5),
        "monitor_mount_base",
        "wall_plate",
    )
    fasteners = (
        (-width * 0.34, height * 0.20),
        (width * 0.34, height * 0.20),
        (-width * 0.34, height * 0.80),
        (width * 0.34, height * 0.80),
    )
    for index, (y, z) in enumerate(fasteners):
        _cylinder(
            part,
            0.012,
            0.012,
            (0.006, y, z),
            "monitor_mount_accent",
            f"wall_fastener_{index:02d}",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )

    if r.wall_style == "wall_plate_lugs":
        for side, y in enumerate((-width * 0.54, width * 0.54)):
            _box(
                part,
                (0.075, 0.040, height * 0.22),
                (0.018, y, r.shoulder_height),
                "monitor_mount_base",
                f"side_mount_lug_{side}",
            )
    elif r.wall_style == "wall_plate_long":
        _box(
            part,
            (0.072, width * 0.58, 0.055),
            (0.018, 0.0, height * 0.12),
            "monitor_mount_cover",
            "lower_cable_housing",
        )

    _cylinder(
        part,
        0.060,
        0.095,
        (0.030, 0.0, r.shoulder_height),
        "monitor_mount_joint",
        "wall_pan_bearing",
    )


def _build_pan_carriage(part, r: ResolvedMonitorMountConfig) -> None:
    _cylinder(
        part,
        0.048,
        0.16,
        (0.0, 0.0, 0.0),
        "monitor_mount_joint",
        "pan_spindle",
    )
    _box(
        part,
        (0.14, r.link_width * 1.72, 0.062),
        (0.072, 0.0, 0.0),
        "monitor_mount_base",
        "shoulder_yoke",
    )
    _cylinder(
        part,
        r.link_width * 0.46,
        r.link_width * 1.90,
        (0.125, 0.0, 0.0),
        "monitor_mount_accent",
        "shoulder_pin",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )


def _build_arm_segment(part, r: ResolvedMonitorMountConfig, index: int) -> None:
    length = r.segment_length
    width = r.link_width * (0.992**index)
    height = r.link_height * (0.996**index)
    hub_radius = max(0.020, height * 0.66)
    hub_span = width * 1.24

    _cylinder(
        part,
        hub_radius,
        hub_span,
        (0.0, 0.0, 0.0),
        "monitor_mount_joint",
        "proximal_hinge_hub",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    _cylinder(
        part,
        hub_radius,
        hub_span,
        (length, 0.0, 0.0),
        "monitor_mount_joint",
        "distal_hinge_hub",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    _cylinder(
        part,
        hub_radius * 0.38,
        hub_span * 1.18,
        (length, 0.0, 0.0),
        "monitor_mount_accent",
        "distal_hinge_pin",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )

    body_length = max(0.035, length - 2.0 * hub_radius * 0.52)
    body_x = length * 0.5
    if r.arm_style == "counterbalance_spring":
        for side, y in enumerate((-width * 0.34, width * 0.34)):
            _box(
                part,
                (body_length, width * 0.22, height),
                (body_x, y, 0.0),
                "monitor_mount_link",
                f"link_side_rail_{side}",
            )
        _cylinder(
            part,
            height * 0.24,
            body_length * 0.82,
            (body_x, 0.0, height * 0.72),
            "monitor_mount_cover",
            "counterbalance_spring_case",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )
    elif r.arm_style == "gas_strut":
        _box(
            part,
            (body_length, width * 0.76, height * 0.82),
            (body_x, 0.0, 0.0),
            "monitor_mount_link",
            "link_box_beam",
        )
        _cylinder(
            part,
            height * 0.20,
            body_length * 0.72,
            (body_x, 0.0, height * 0.74),
            "monitor_mount_cover",
            "gas_strut_case",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )
    else:
        _box(
            part,
            (body_length, width * 0.70, height * 0.70),
            (body_x, 0.0, 0.0),
            "monitor_mount_link",
            "simple_link_beam",
        )

    _box(
        part,
        (body_length * 0.60, width * 0.44, max(0.007, height * 0.15)),
        (body_x, 0.0, -height * 0.50),
        "monitor_mount_cover",
        "cable_management_cover",
        class_id="plastic.opaque_generic",
    )


def _build_head_knuckle(part, r: ResolvedMonitorMountConfig) -> None:
    _cylinder(
        part,
        0.034,
        0.11,
        (0.0, 0.0, 0.0),
        "monitor_mount_joint",
        "head_pan_bearing",
    )
    if r.head_style == "single_pivot":
        _cylinder(
            part,
            0.050,
            0.034,
            (0.068, 0.0, 0.0),
            "monitor_mount_base",
            "single_pivot_head",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )
    else:
        yoke_width = 0.12 if r.head_style == "vesa_yoke" else 0.095
        _box(
            part,
            (0.12, yoke_width, 0.050),
            (0.060, 0.0, 0.0),
            "monitor_mount_base",
            "tilt_yoke_bridge",
        )
        for side, y in enumerate((-yoke_width * 0.46, yoke_width * 0.46)):
            _box(
                part,
                (0.058, 0.015, 0.105),
                (0.112, y, 0.0),
                "monitor_mount_base",
                f"tilt_yoke_cheek_{side}",
            )
    _cylinder(
        part,
        0.022,
        0.145,
        (0.112, 0.0, 0.0),
        "monitor_mount_accent",
        "tilt_cross_pin",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )


def _build_display_head(part, r: ResolvedMonitorMountConfig) -> None:
    width = r.display_width * (0.84 if r.head_style == "compact_plate" else 1.0)
    height = r.display_height * (0.86 if r.head_style == "compact_plate" else 1.0)
    _cylinder(
        part,
        0.026,
        0.080,
        (0.0, 0.0, 0.0),
        "monitor_mount_joint",
        "tilt_trunnion",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    _box(
        part,
        (0.055, 0.085, 0.070),
        (0.054, 0.0, 0.0),
        "monitor_mount_joint",
        "head_adapter_block",
    )
    _box(
        part,
        (0.026, width, height),
        (0.105, 0.0, 0.0),
        "monitor_mount_bezel",
        "monitor_body",
        class_id="plastic.opaque_glossy_molded",
    )
    _box(
        part,
        (0.004, width * 0.90, height * 0.84),
        (0.120, 0.0, 0.006),
        "monitor_mount_screen",
        "screen_surface",
        class_id="glass.smoked_tinted",
    )
    _box(
        part,
        (0.018, width * 0.44, height * 0.46),
        (0.079, 0.0, 0.0),
        "monitor_mount_cover",
        "vesa_mounting_plate",
    )
    fasteners = ((-0.05, -0.05), (-0.05, 0.05), (0.05, -0.05), (0.05, 0.05))
    for index, (y, z) in enumerate(fasteners):
        _cylinder(
            part,
            0.006,
            0.012,
            (0.067, y, z),
            "monitor_mount_accent",
            f"vesa_fastener_{index}",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )


def _absolute_segment_angle(index: int, bend_angle: float) -> float:
    if index == 0:
        return 0.0
    return bend_angle if index % 2 else -bend_angle


def _relative_segment_turn(index: int, bend_angle: float) -> float:
    return _absolute_segment_angle(index, bend_angle) - _absolute_segment_angle(
        index - 1, bend_angle
    )


def build_monitor_mount(
    config: MonitorMountConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    _materialize(model, r)

    wall = model.part("wall_bracket")
    _build_wall_bracket(wall, r)
    carriage = model.part("pan_carriage")
    _build_pan_carriage(carriage, r)
    segments = []
    for index in range(r.arm_segment_count):
        segment = model.part(f"arm_segment_{index + 1:02d}")
        _build_arm_segment(segment, r, index)
        segments.append(segment)
    head = model.part("head_knuckle")
    _build_head_knuckle(head, r)
    display = model.part("tilt_head")
    _build_display_head(display, r)

    model.articulation(
        "wall_pan",
        ArticulationType.REVOLUTE,
        parent=wall,
        child=carriage,
        origin=Origin(xyz=(0.030, 0.0, r.shoulder_height)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=-0.65, upper=0.65, effort=30.0, velocity=1.0),
        motion_properties=MotionProperties(damping=0.18, friction=0.12),
    )
    model.articulation(
        "shoulder_lift",
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=segments[0],
        origin=Origin(xyz=(0.125, 0.0, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=-0.42, upper=0.72, effort=48.0, velocity=0.9),
        motion_properties=MotionProperties(damping=0.30, friction=0.14),
    )
    for index in range(1, r.arm_segment_count):
        model.articulation(
            f"segment_joint_{index:02d}",
            ArticulationType.REVOLUTE,
            parent=segments[index - 1],
            child=segments[index],
            origin=Origin(
                xyz=(r.segment_length, 0.0, 0.0),
                rpy=(0.0, _relative_segment_turn(index, r.bend_angle), 0.0),
            ),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(lower=-0.34, upper=0.34, effort=24.0, velocity=1.2),
            motion_properties=MotionProperties(damping=0.16, friction=0.10),
        )

    terminal_angle = _absolute_segment_angle(r.arm_segment_count - 1, r.bend_angle)
    model.articulation(
        "head_pan",
        ArticulationType.REVOLUTE,
        parent=segments[-1],
        child=head,
        origin=Origin(
            xyz=(r.segment_length, 0.0, 0.0),
            rpy=(terminal_angle, 0.0, -math.pi / 2.0),
        ),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=-1.2, upper=1.2, effort=14.0, velocity=1.2),
    )
    model.articulation(
        "head_tilt",
        ArticulationType.REVOLUTE,
        parent=head,
        child=display,
        origin=Origin(xyz=(0.112, 0.0, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=-0.55, upper=0.55, effort=12.0, velocity=1.0),
    )

    model.meta["template_slug"] = "monitor_mount"
    model.meta["slot_choices"] = [list(item) for item in slot_choices_for_config(r)]
    model.meta["arm_segment_count"] = r.arm_segment_count
    model.meta["arm_segment_length"] = r.segment_length
    model.meta["visualization_only_topology_extension"] = True
    return model


def build_seeded_monitor_mount(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_monitor_mount(config_from_seed(seed), assets=assets)


__all__ = [
    "ArmStyle",
    "HeadStyle",
    "MonitorMountConfig",
    "ResolvedMonitorMountConfig",
    "WallStyle",
    "build_monitor_mount",
    "build_seeded_monitor_mount",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
