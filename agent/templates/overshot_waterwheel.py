# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for `overshot_waterwheel`.

Slot graph:
    support_and_feed -> bucket_wheel
    support_and_feed -> water_control_or_service
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

SupportAndFeedModule = Literal[
    "simple_frame_chute",
    "timber_mill_frame",
    "masonry_flume_support",
    "suspended_inlet_box",
    "detached_launder_frame",
    "detached_inlet_box_frame",
    "long_launder_trestle",
]
BucketWheelModule = Literal[
    "spoked_shallow_bucket_wheel",
    "deep_timber_bucket_wheel",
    "drive_pinion_rotor",
    "cast_iron_bucket_wheel",
    "open_spoke_paddle_wheel",
]
WaterControlModule = Literal[
    "fixed_chute_only",
    "sliding_sluice_gate",
    "pivoting_shutoff_flap",
    "brake_arm",
    "hinged_guard_panel",
]
PaletteName = Literal["wet_timber", "masonry_iron", "museum_demo", "algae_weathered"]

SUPPORT_MODULES: tuple[SupportAndFeedModule, ...] = (
    "simple_frame_chute",
    "timber_mill_frame",
    "masonry_flume_support",
    "suspended_inlet_box",
    "detached_launder_frame",
    "detached_inlet_box_frame",
    "long_launder_trestle",
)
WHEEL_MODULES: tuple[BucketWheelModule, ...] = (
    "spoked_shallow_bucket_wheel",
    "deep_timber_bucket_wheel",
    "drive_pinion_rotor",
    "cast_iron_bucket_wheel",
    "open_spoke_paddle_wheel",
)
CONTROL_MODULES: tuple[WaterControlModule, ...] = (
    "fixed_chute_only",
    "sliding_sluice_gate",
    "pivoting_shutoff_flap",
    "brake_arm",
    "hinged_guard_panel",
)

PALETTES: dict[PaletteName, dict[str, tuple[float, float, float, float]]] = {
    "wet_timber": {
        "timber": (0.36, 0.23, 0.12, 1.0),
        "wet_timber": (0.24, 0.16, 0.09, 1.0),
        "stone": (0.46, 0.44, 0.39, 1.0),
        "iron": (0.18, 0.19, 0.19, 1.0),
        "water": (0.30, 0.55, 0.64, 0.62),
        "shadow": (0.045, 0.040, 0.035, 1.0),
    },
    "masonry_iron": {
        "timber": (0.30, 0.22, 0.16, 1.0),
        "wet_timber": (0.20, 0.15, 0.10, 1.0),
        "stone": (0.58, 0.56, 0.52, 1.0),
        "iron": (0.12, 0.13, 0.14, 1.0),
        "water": (0.22, 0.48, 0.58, 0.60),
        "shadow": (0.035, 0.035, 0.035, 1.0),
    },
    "museum_demo": {
        "timber": (0.60, 0.43, 0.24, 1.0),
        "wet_timber": (0.44, 0.30, 0.16, 1.0),
        "stone": (0.70, 0.66, 0.58, 1.0),
        "iron": (0.24, 0.25, 0.27, 1.0),
        "water": (0.34, 0.62, 0.72, 0.55),
        "shadow": (0.06, 0.05, 0.04, 1.0),
    },
    "algae_weathered": {
        "timber": (0.26, 0.30, 0.20, 1.0),
        "wet_timber": (0.18, 0.22, 0.14, 1.0),
        "stone": (0.42, 0.48, 0.40, 1.0),
        "iron": (0.20, 0.22, 0.20, 1.0),
        "water": (0.20, 0.44, 0.48, 0.62),
        "shadow": (0.035, 0.045, 0.035, 1.0),
    },
}


@dataclass(frozen=True)
class OvershotWaterwheelConfig:
    support_and_feed_module: SupportAndFeedModule | None = None
    bucket_wheel_module: BucketWheelModule | None = None
    water_control_module: WaterControlModule | None = None
    bucket_count: int = 18
    wheel_radius: float = 0.50
    wheel_width: float = 0.50
    axle_height: float = 0.70
    frame_span: float = 0.78
    chute_height: float = 1.26
    palette_name: PaletteName = "wet_timber"
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["wet_timber"])
    )


@dataclass(frozen=True)
class ResolvedOvershotWaterwheelConfig:
    support_and_feed_module: SupportAndFeedModule
    bucket_wheel_module: BucketWheelModule
    water_control_module: WaterControlModule
    bucket_count: int
    wheel_radius: float
    wheel_width: float
    axle_height: float
    frame_span: float
    chute_height: float
    palette_name: PaletteName
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _cyl_x() -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0, 0.0)


def _cyl_y() -> tuple[float, float, float]:
    return (math.pi / 2.0, 0.0, 0.0)


def _wheel_point(theta: float, radius: float) -> tuple[float, float]:
    return math.cos(theta) * radius, math.sin(theta) * radius


def _support_half_span(r: ResolvedOvershotWaterwheelConfig) -> float:
    return max(r.frame_span * 0.5, r.wheel_width * 0.62 + 0.013)


def _wheel_axle_length(r: ResolvedOvershotWaterwheelConfig) -> float:
    return max(0.24, 2.0 * (_support_half_span(r) - 0.013))


def _wheel_outer_extent(r: ResolvedOvershotWaterwheelConfig) -> float:
    """Outer radius of the spinning wheel including bucket plates poking past the rim."""
    radius = r.wheel_radius
    if r.bucket_wheel_module == "open_spoke_paddle_wheel":
        # Bucket floor band: radial centre 0.98R, radial half-extent 0.035, corner margin.
        return radius * 0.98 + 0.041
    depth = 0.086 if r.bucket_wheel_module == "deep_timber_bucket_wheel" else 0.060
    if r.bucket_wheel_module == "cast_iron_bucket_wheel":
        depth = 0.048
    return max(radius, radius * 0.92 + depth * 0.5 + 0.010, radius * 0.98 + 0.012)


def _midpoint(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    return ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5, (a[2] + b[2]) * 0.5)


def _distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2 + (b[2] - a[2]) ** 2)


def _rpy_for_segment(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    length_xy = math.hypot(dx, dy)
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(length_xy, dz)
    return (0.0, pitch, yaw)


def _add_round_member(
    part,
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    *,
    radius: float,
    mat: str,
    name: str,
) -> None:
    part.visual(
        Cylinder(radius=radius, length=_distance(a, b)),
        origin=Origin(xyz=_midpoint(a, b), rpy=_rpy_for_segment(a, b)),
        material=mat,
        name=name, material_class_id="wood.natural_generic",
    )


def config_from_seed(seed: int) -> OvershotWaterwheelConfig:
    if seed == 0:
        return OvershotWaterwheelConfig(
            support_and_feed_module="simple_frame_chute",
            bucket_wheel_module="spoked_shallow_bucket_wheel",
            water_control_module="fixed_chute_only",
            bucket_count=18,
            wheel_radius=0.50,
            wheel_width=0.50,
            axle_height=0.70,
            frame_span=0.78,
            chute_height=1.26,
            palette_name="wet_timber",
        )
    rng = random.Random(seed)
    radius = rng.uniform(0.42, 0.68)
    return OvershotWaterwheelConfig(
        support_and_feed_module=rng.choice(SUPPORT_MODULES),
        bucket_wheel_module=rng.choice(WHEEL_MODULES),
        water_control_module=rng.choice(CONTROL_MODULES),
        bucket_count=rng.randint(12, 32),
        wheel_radius=radius,
        wheel_width=rng.uniform(0.38, 0.62),
        axle_height=rng.uniform(radius + 0.12, radius + 0.34),
        frame_span=rng.uniform(0.70, 0.96),
        chute_height=rng.uniform(radius * 2.15, radius * 2.65),
        palette_name=rng.choice(tuple(PALETTES)),
    )


def resolve_config(config: OvershotWaterwheelConfig) -> ResolvedOvershotWaterwheelConfig:
    support = config.support_and_feed_module or "simple_frame_chute"
    wheel = config.bucket_wheel_module or "spoked_shallow_bucket_wheel"
    control = config.water_control_module or "fixed_chute_only"
    if support not in SUPPORT_MODULES:
        raise ValueError(f"Unsupported support_and_feed_module: {support!r}")
    if wheel not in WHEEL_MODULES:
        raise ValueError(f"Unsupported bucket_wheel_module: {wheel!r}")
    if control not in CONTROL_MODULES:
        raise ValueError(f"Unsupported water_control_module: {control!r}")
    if support == "detached_inlet_box_frame" and control == "pivoting_shutoff_flap":
        control = "sliding_sluice_gate"
    if config.palette_name not in PALETTES:
        raise ValueError(f"Unsupported palette_name: {config.palette_name!r}")
    radius = _clamp(config.wheel_radius, 0.36, 0.72)
    axle_height = _clamp(config.axle_height, radius + 0.08, radius + 0.42)
    return ResolvedOvershotWaterwheelConfig(
        support_and_feed_module=support,
        bucket_wheel_module=wheel,
        water_control_module=control,
        bucket_count=max(12, min(32, int(config.bucket_count))),
        wheel_radius=radius,
        wheel_width=_clamp(config.wheel_width, 0.32, 0.68),
        axle_height=axle_height,
        frame_span=_clamp(config.frame_span, radius * 1.36, 1.08),
        chute_height=_clamp(
            config.chute_height, axle_height + radius + 0.10, axle_height + radius + 0.38
        ),
        palette_name=config.palette_name,
        palette=dict(PALETTES[config.palette_name]),
    )


def _add_frame_post(
    frame, *, name: str, x: float, y: float, z0: float, z1: float, mat: str
) -> None:
    frame.visual(
        Box((0.060, 0.060, z1 - z0)),
        origin=Origin(xyz=(x, y, (z0 + z1) * 0.5)),
        material=mat,
        name=name, material_class_id="wood.natural_generic",
    )


def _add_chute_gantry(
    frame, r: ResolvedOvershotWaterwheelConfig, *, y: float, z_top: float, name: str
) -> None:
    """Side gantry carrying an overhead feed structure down to the frame.

    The posts stand at the frame half-span, which is always wider than the wheel
    (``_support_half_span`` >= wheel_width*0.62), so they sit clear of the wheel
    instead of routing a stay through the rotating disc. A cross tie runs over the
    top, above the wheel, to meet the feed and tie the two posts together.
    """
    half_span = _support_half_span(r)
    skid_z = 0.035
    for side_name, x in (("left", -half_span), ("right", half_span)):
        frame.visual(
            Box((0.044, 0.044, z_top - skid_z)),
            origin=Origin(xyz=(x, y, (z_top + skid_z) * 0.5)),
            material="timber",
            name=f"{name}_{side_name}_gantry_post", material_class_id="wood.natural_generic",
        )
    frame.visual(
        Box((half_span * 2.0 + 0.060, 0.050, 0.050)),
        origin=Origin(xyz=(0.0, y, z_top - 0.025)),
        material="timber",
        name=f"{name}_gantry_tie", material_class_id="wood.natural_generic",
    )


def _add_overhead_chute(
    frame, r: ResolvedOvershotWaterwheelConfig, *, wide: bool, boxed: bool
) -> None:
    chute_w = r.wheel_width * (0.58 if wide else 0.42)
    chute_d = r.wheel_radius * 0.50
    y = -r.wheel_radius * 0.36
    z = r.chute_height
    frame.visual(
        Box((chute_w * 1.10, 0.040, 0.038)),
        origin=Origin(xyz=(0.0, y - chute_d * 0.10, z - 0.038)),
        material="timber",
        name="overhead_chute_bearer", material_class_id="wood.natural_generic",
    )
    # Carry the chute down to the frame via side posts that clear the wheel. No
    # center drop-posts/braces here: at chute width they sit inside the rotating
    # disc and clip through it. The gantry tie over the top holds the chute
    # bearer/floor, so the chute is fully supported without piercing the wheel.
    _add_chute_gantry(frame, r, y=y, z_top=z, name="chute")
    frame.visual(
        Box((chute_w, chute_d, 0.034)),
        origin=Origin(xyz=(0.0, y, z)),
        material="wet_timber",
        name="overhead_chute_floor", material_class_id="wood.rustic_weathered",
    )
    frame.visual(
        Box((0.030, chute_d, 0.11)),
        origin=Origin(xyz=(-chute_w * 0.5, y, z + 0.046)),
        material="wet_timber",
        name="chute_left_wall", material_class_id="wood.rustic_weathered",
    )
    frame.visual(
        Box((0.030, chute_d, 0.11)),
        origin=Origin(xyz=(chute_w * 0.5, y, z + 0.046)),
        material="wet_timber",
        name="chute_right_wall", material_class_id="wood.rustic_weathered",
    )
    frame.visual(
        Box((chute_w * 0.82, 0.026, 0.09)),
        origin=Origin(xyz=(0.0, y + chute_d * 0.48, z + 0.038)),
        material="wet_timber",
        name="chute_lip", material_class_id="wood.rustic_weathered",
    )
    # Water emerging from the chute outlet; tall enough to meet the chute lip so it
    # reads as connected to the chute rather than a free-floating sheet.
    frame.visual(
        Box((chute_w * 0.68, chute_d * 0.24, 0.110)),
        origin=Origin(xyz=(0.0, y + chute_d * 0.52, z - 0.012)),
        material="water",
        name="visible_overshot_water_sheet", material_class_id="liquid.water_wave_foam",
    )
    if boxed:
        # z + 0.085 (not higher): the box bottom must reach below the chute floor
        # top (z + 0.017) so the stone inlet box is welded to the floor plank
        # instead of hovering 3mm above it as a disconnected island.
        frame.visual(
            Box((chute_w * 0.78, chute_d * 0.72, 0.16)),
            origin=Origin(xyz=(0.0, y - chute_d * 0.52, z + 0.085)),
            material="stone",
            name="inlet_box", material_class_id="stone.masonry_wall",
        )


def _add_detached_feed_part(
    model: ArticulatedObject,
    r: ResolvedOvershotWaterwheelConfig,
    *,
    name: str,
    boxed: bool,
) -> None:
    frame = model.get_part("frame")
    chute_w = r.wheel_width * (0.54 if boxed else 0.48)
    chute_d = r.wheel_radius * (0.42 if boxed else 0.50)
    origin_y = -r.wheel_radius * 0.36
    origin_z = r.chute_height
    frame.visual(
        Box((chute_w * 0.70, 0.050, 0.060)),
        origin=Origin(xyz=(0.0, origin_y, origin_z)),
        material="timber",
        name=f"{name}_fixed_mount_socket", material_class_id="wood.natural_generic",
    )
    # Carry the suspended feed down to the frame via side posts that clear the
    # wheel. No center hanger posts: at feed width they pierce the rotating disc.
    # The gantry tie meets the fixed mount socket above the wheel.
    _add_chute_gantry(frame, r, y=origin_y, z_top=origin_z, name=name)
    feed = model.part(name)
    feed.visual(
        Box((chute_w * 0.72, 0.052, 0.038)),
        origin=Origin(xyz=(0.0, 0.0, -0.030)),
        material="timber",
        name="feed_mount_cleat", material_class_id="wood.natural_generic",
    )
    feed.visual(
        Box((chute_w, chute_d, 0.034)),
        origin=Origin(),
        material="wet_timber",
        name="feed_floor", material_class_id="wood.rustic_weathered",
    )
    feed.visual(
        Box((0.028, chute_d, 0.11)),
        origin=Origin(xyz=(-chute_w * 0.5, 0.0, 0.046)),
        material="wet_timber",
        name="left_feed_wall", material_class_id="wood.rustic_weathered",
    )
    feed.visual(
        Box((0.028, chute_d, 0.11)),
        origin=Origin(xyz=(chute_w * 0.5, 0.0, 0.046)),
        material="wet_timber",
        name="right_feed_wall", material_class_id="wood.rustic_weathered",
    )
    feed.visual(
        Box((chute_w * 0.82, 0.026, 0.09)),
        origin=Origin(xyz=(0.0, chute_d * 0.48, 0.038)),
        material="wet_timber",
        name="downstream_lip", material_class_id="wood.rustic_weathered",
    )
    feed.visual(
        Box((chute_w * 0.68, chute_d * 0.24, 0.110)),
        origin=Origin(xyz=(0.0, chute_d * 0.52, -0.012)),
        material="water",
        name="overshot_water_sheet", material_class_id="liquid.water_wave_foam",
    )
    if boxed:
        feed.visual(
            Box((chute_w * 0.84, chute_d * 0.82, 0.17)),
            origin=Origin(xyz=(0.0, -chute_d * 0.50, 0.095)),
            material="stone",
            name="suspended_inlet_box_shell", material_class_id="stone.masonry_wall",
        )
        feed.visual(
            Box((chute_w * 0.34, 0.018, 0.13)),
            origin=Origin(xyz=(0.0, chute_d * 0.08, 0.062)),
            material="iron",
            name="regulator_guide_slot", material_class_id="metal.cast_iron_bare",
        )
    else:
        feed.visual(
            Cylinder(radius=0.012, length=chute_w * 0.95),
            origin=Origin(xyz=(0.0, chute_d * 0.45, 0.068), rpy=_cyl_x()),
            material="iron",
            name=f"{name}_flap_hinge_socket", material_class_id="metal.cast_iron_bare",
        )
    model.articulation(
        f"frame_to_{name}",
        ArticulationType.FIXED,
        parent=frame,
        child=feed,
        origin=Origin(xyz=(0.0, origin_y, origin_z)),
    )


def _add_long_launder_trestle(frame, r: ResolvedOvershotWaterwheelConfig) -> None:
    half_span = _support_half_span(r)
    chute_w = r.wheel_width * 0.50
    upstream_y = -r.wheel_radius * 1.52
    outlet_y = -r.wheel_radius * 0.30
    center_y = (upstream_y + outlet_y) * 0.5
    launder_d = outlet_y - upstream_y
    floor_z = r.chute_height + 0.030
    post_z0 = 0.070

    for side_name, x in (("left", -half_span), ("right", half_span)):
        for station_name, y in (("upstream", upstream_y), ("outlet", outlet_y)):
            frame.visual(
                Box((0.052, 0.052, floor_z - post_z0)),
                origin=Origin(xyz=(x, y, (floor_z + post_z0) * 0.5)),
                material="timber",
                name=f"{side_name}_{station_name}_launder_post", material_class_id="wood.natural_generic",
            )
        frame.visual(
            Box((0.052, launder_d + 0.10, 0.060)),
            origin=Origin(xyz=(x, center_y, floor_z + 0.020)),
            material="timber",
            name=f"{side_name}_launder_head_beam", material_class_id="wood.natural_generic",
        )
        _add_round_member(
            frame,
            (x, upstream_y, post_z0 + 0.05),
            (x, outlet_y, floor_z - 0.05),
            radius=0.014,
            mat="timber",
            name=f"{side_name}_launder_diagonal_brace_a",
        )
        _add_round_member(
            frame,
            (x, outlet_y, post_z0 + 0.05),
            (x, upstream_y, floor_z - 0.05),
            radius=0.014,
            mat="timber",
            name=f"{side_name}_launder_diagonal_brace_b",
        )

    frame.visual(
        Box((half_span * 2.0 + 0.12, 0.060, 0.060)),
        origin=Origin(xyz=(0.0, upstream_y, floor_z + 0.020)),
        material="timber",
        name="upstream_launder_crosshead", material_class_id="wood.natural_generic",
    )
    frame.visual(
        Box((half_span * 2.0 + 0.12, 0.060, 0.060)),
        origin=Origin(xyz=(0.0, outlet_y, floor_z + 0.020)),
        material="timber",
        name="outlet_launder_crosshead", material_class_id="wood.natural_generic",
    )
    frame.visual(
        Box((chute_w, launder_d + 0.12, 0.034)),
        origin=Origin(xyz=(0.0, center_y, floor_z)),
        material="wet_timber",
        name="long_launder_floor", material_class_id="wood.rustic_weathered",
    )
    for side_name, x in (("left", -chute_w * 0.5), ("right", chute_w * 0.5)):
        frame.visual(
            Box((0.030, launder_d + 0.12, 0.115)),
            origin=Origin(xyz=(x, center_y, floor_z + 0.052)),
            material="wet_timber",
            name=f"{side_name}_long_launder_wall", material_class_id="wood.rustic_weathered",
        )
    frame.visual(
        Box((chute_w * 0.88, 0.028, 0.090)),
        origin=Origin(xyz=(0.0, outlet_y + 0.055, floor_z + 0.038)),
        material="wet_timber",
        name="long_launder_outlet_lip", material_class_id="wood.rustic_weathered",
    )
    frame.visual(
        Box((chute_w * 0.70, 0.070, 0.145)),
        origin=Origin(xyz=(0.0, outlet_y + 0.095, floor_z - 0.030)),
        material="water",
        name="long_launder_water_sheet", material_class_id="liquid.water_wave_foam",
    )


def _build_support_and_feed(model: ArticulatedObject, r: ResolvedOvershotWaterwheelConfig) -> None:
    frame = model.part("frame")
    half_span = _support_half_span(r)
    frame_width = half_span * 2.0
    side_y = r.wheel_radius * 0.58
    skid_z = 0.035
    if r.support_and_feed_module == "masonry_flume_support":
        frame.visual(
            Box((0.12, r.wheel_radius * 1.48, r.axle_height + 0.20)),
            origin=Origin(xyz=(-half_span, 0.0, (r.axle_height + 0.20) * 0.5)),
            material="stone",
            name="left_masonry_pier", material_class_id="stone.masonry_wall",
        )
        frame.visual(
            Box((0.12, r.wheel_radius * 1.48, r.axle_height + 0.20)),
            origin=Origin(xyz=(half_span, 0.0, (r.axle_height + 0.20) * 0.5)),
            material="stone",
            name="right_masonry_pier", material_class_id="stone.masonry_wall",
        )
        frame.visual(
            Box((frame_width + 0.12, 0.11, 0.08)),
            origin=Origin(xyz=(0.0, -side_y, r.axle_height + 0.16)),
            material="stone",
            name="masonry_flume_bridge", material_class_id="stone.masonry_wall",
        )
        frame.visual(
            Box((frame_width + 0.10, 0.075, 0.075)),
            origin=Origin(xyz=(0.0, 0.0, r.axle_height)),
            material="iron",
            name="axle_crossbar", material_class_id="metal.cast_iron_bare",
        )
        for side_name, x in (("left", -half_span), ("right", half_span)):
            frame.visual(
                Box((0.16, 0.20, 0.10)),
                origin=Origin(xyz=(x, 0.0, r.axle_height - 0.055)),
                material="stone",
                name=f"{side_name}_stone_bearing_bed", material_class_id="stone.masonry_wall",
            )
            frame.visual(
                Box((0.09, 0.16, 0.035)),
                origin=Origin(xyz=(x, 0.0, r.axle_height + 0.070)),
                material="iron",
                name=f"{side_name}_bearing_cap", material_class_id="metal.cast_iron_bare",
            )
        _add_overhead_chute(frame, r, wide=True, boxed=False)
    else:
        frame.visual(
            Box((0.08, r.wheel_radius * 1.38, 0.070)),
            origin=Origin(xyz=(-half_span, 0.0, skid_z)),
            material="timber",
            name="left_skid", material_class_id="wood.natural_generic",
        )
        frame.visual(
            Box((0.08, r.wheel_radius * 1.38, 0.070)),
            origin=Origin(xyz=(half_span, 0.0, skid_z)),
            material="timber",
            name="right_skid", material_class_id="wood.natural_generic",
        )
        frame.visual(
            Box((frame_width + 0.12, 0.060, 0.065)),
            origin=Origin(xyz=(0.0, -side_y, skid_z + 0.018)),
            material="timber",
            name="front_tie_beam", material_class_id="wood.natural_generic",
        )
        frame.visual(
            Box((frame_width + 0.12, 0.060, 0.065)),
            origin=Origin(xyz=(0.0, side_y, skid_z + 0.018)),
            material="timber",
            name="rear_tie_beam", material_class_id="wood.natural_generic",
        )
        for i, x in enumerate((-half_span, half_span)):
            _add_frame_post(
                frame,
                name=f"front_axle_post_{i}",
                x=x,
                y=-side_y * 0.52,
                z0=0.06,
                z1=r.axle_height + 0.14,
                mat="timber",
            )
            _add_frame_post(
                frame,
                name=f"rear_axle_post_{i}",
                x=x,
                y=side_y * 0.52,
                z0=0.06,
                z1=r.axle_height + 0.14,
                mat="timber",
            )
            # Bolster beam spanning between the front and rear axle posts (post
            # centres sit at y = +-0.52*side_y = +-0.3016R). At a fixed 0.19
            # depth the bed only reached the posts for R <= ~0.41 and otherwise
            # relied on the diagonal braces happening to cross its y-band, which
            # fails at large axle_height - R: the whole bearing cluster floated.
            frame.visual(
                Box((0.095, side_y * 1.04 + 0.060, 0.060)),
                origin=Origin(xyz=(x, 0.0, r.axle_height - 0.052)),
                material="timber",
                name=f"{'left' if x < 0 else 'right'}_axle_bed", material_class_id="wood.natural_generic",
            )
            frame.visual(
                Box((0.062, 0.15, 0.035)),
                origin=Origin(xyz=(x, 0.0, r.axle_height + 0.064)),
                material="iron",
                name=f"{'left' if x < 0 else 'right'}_bearing_cap", material_class_id="metal.cast_iron_bare",
            )
            _add_round_member(
                frame,
                (x, -side_y * 0.66, skid_z + 0.040),
                (x, side_y * 0.52, r.axle_height + 0.12),
                radius=0.016,
                mat="timber",
                name=f"side_x_brace_a_{i}",
            )
            _add_round_member(
                frame,
                (x, side_y * 0.66, skid_z + 0.040),
                (x, -side_y * 0.52, r.axle_height + 0.12),
                radius=0.016,
                mat="timber",
                name=f"side_x_brace_b_{i}",
            )
        frame.visual(
            Box((frame_width + 0.06, 0.070, 0.070)),
            origin=Origin(xyz=(0.0, 0.0, r.axle_height)),
            material="timber",
            name="axle_crossbar", material_class_id="wood.natural_generic",
        )
        if r.support_and_feed_module == "timber_mill_frame":
            frame.visual(
                Box((frame_width + 0.16, 0.070, 0.065)),
                origin=Origin(xyz=(0.0, 0.0, r.axle_height + 0.18)),
                material="timber",
                name="upper_timber_tie", material_class_id="wood.natural_generic",
            )
            # Stanchions carrying the upper tie down onto the bearing caps. The
            # tie runs along y=0 while the axle posts stand at y = +-0.30R and
            # top out at axle_height + 0.14 (below the tie underside at +0.1475),
            # so without these the tie is a floating island in the frame part.
            for side_name, x in (("left", -half_span), ("right", half_span)):
                frame.visual(
                    Box((0.055, 0.055, 0.150)),
                    origin=Origin(xyz=(x, 0.0, r.axle_height + 0.115)),
                    material="timber",
                    name=f"{side_name}_upper_tie_stanchion", material_class_id="wood.natural_generic",
                )
            _add_overhead_chute(frame, r, wide=True, boxed=False)
        elif r.support_and_feed_module == "suspended_inlet_box":
            frame.visual(
                Box((r.wheel_width * 0.80, 0.055, 0.070)),
                origin=Origin(xyz=(0.0, -r.wheel_radius * 0.36, r.chute_height + 0.072)),
                material="timber",
                name="inlet_suspension_beam", material_class_id="wood.natural_generic",
            )
            _add_overhead_chute(frame, r, wide=False, boxed=True)
        elif r.support_and_feed_module == "detached_launder_frame":
            frame.visual(
                Box((frame_width * 0.74, 0.050, 0.060)),
                origin=Origin(xyz=(0.0, -r.wheel_radius * 0.36, r.chute_height + 0.038)),
                material="timber",
                name="launder_support_beam", material_class_id="wood.natural_generic",
            )
            _add_detached_feed_part(model, r, name="launder", boxed=False)
        elif r.support_and_feed_module == "detached_inlet_box_frame":
            frame.visual(
                Box((r.wheel_width * 0.82, 0.050, 0.065)),
                origin=Origin(xyz=(0.0, -r.wheel_radius * 0.36, r.chute_height + 0.040)),
                material="timber",
                name="inlet_box_hanger_beam", material_class_id="wood.natural_generic",
            )
            _add_detached_feed_part(model, r, name="inlet_box", boxed=True)
        elif r.support_and_feed_module == "long_launder_trestle":
            _add_long_launder_trestle(frame, r)
        else:
            _add_overhead_chute(frame, r, wide=False, boxed=False)

    frame.visual(
        Box((0.026, 0.12, 0.10)),
        origin=Origin(xyz=(-half_span, 0.0, r.axle_height)),
        material="iron",
        name="left_bearing_face", material_class_id="metal.cast_iron_bare",
    )
    frame.visual(
        Box((0.026, 0.12, 0.10)),
        origin=Origin(xyz=(half_span, 0.0, r.axle_height)),
        material="iron",
        name="right_bearing_face", material_class_id="metal.cast_iron_bare",
    )
    for side, x in (("left", -half_span), ("right", half_span)):
        for y in (-0.038, 0.038):
            frame.visual(
                Cylinder(radius=0.010, length=0.012),
                origin=Origin(xyz=(x, y, r.axle_height + 0.032), rpy=_cyl_x()),
                material="iron",
                name=f"{side}_bearing_cap_bolt_{'front' if y < 0 else 'rear'}", material_class_id="metal.cast_iron_bare",
            )
    # Splash basin resting across the frame skids at the front, low enough to
    # clear the wheel (the wheel bottom nearly meets the base, so there is no
    # room directly beneath it; spanning the skids keeps it carried and clear).
    frame.visual(
        Box((half_span * 2.0, 0.090, 0.040)),
        origin=Origin(xyz=(0.0, -r.wheel_radius * 0.42, skid_z + 0.035)),
        material="stone",
        name="splash_catch_trough", material_class_id="stone.masonry_wall",
    )


def _bucket_origin(theta: float, radius: float, *, x: float) -> Origin:
    """Origin at wheel angle theta with the box y-dim radial and z-dim tangential.

    The roll must be +theta (the position angle is measured from +y toward +z,
    and Rx(+theta) maps local +y onto that radial direction). With -theta every
    element is mirror-tilted by 2*theta: correct only at cardinal angles, so
    ring/bucket contacts silently vanished at intermediate angles.
    """
    y, z = _wheel_point(theta, radius)
    return Origin(xyz=(x, y, z), rpy=(theta, 0.0, 0.0))


def _build_bucket_wheel(model: ArticulatedObject, r: ResolvedOvershotWaterwheelConfig) -> None:
    wheel = model.part("wheel")
    radius = r.wheel_radius
    width = r.wheel_width
    wheel.visual(
        Cylinder(radius=0.026, length=_wheel_axle_length(r)),
        origin=Origin(rpy=_cyl_x()),
        material="iron",
        name="axle", material_class_id="metal.cast_iron_bare",
    )
    wheel.visual(
        Cylinder(radius=radius * 0.18, length=width * 0.34),
        origin=Origin(rpy=_cyl_x()),
        material="timber" if r.bucket_wheel_module != "cast_iron_bucket_wheel" else "iron",
        name="hub_barrel", material_class_id=("wood.natural_generic" if r.bucket_wheel_module in {"spoked_shallow_bucket_wheel", "deep_timber_bucket_wheel", "drive_pinion_rotor", "open_spoke_paddle_wheel"} else "metal.cast_iron_bare"),
    )
    for side, x in (("left", -width * 0.22), ("right", width * 0.22)):
        wheel.visual(
            Cylinder(radius=radius * 0.20, length=0.018),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=_cyl_x()),
            material="iron",
            name=f"{side}_hub_retaining_collar", material_class_id="metal.cast_iron_bare",
        )
    if r.bucket_wheel_module == "open_spoke_paddle_wheel":
        rim_mat = "wet_timber"
        rim_count = max(18, min(32, r.bucket_count))
        rim_radius = radius * 0.90
        # 1.32x pitch: neighbouring rim segments overlap ~25% of the pitch so the
        # segmented ring is one solid loop instead of tangency-dependent blobs.
        rim_tangent = (math.tau * rim_radius / rim_count) * 1.32
        for side_name, x in (("left", -width * 0.42), ("right", width * 0.42)):
            for i in range(rim_count):
                theta = math.tau * i / rim_count
                # _bucket_origin maps the box y-dim to the radial direction and
                # z-dim to the tangential direction, so the long rim_tangent dim
                # must be the z-dim: (0.030, rim_tangent, 0.060) produced radial
                # slats with tangential gaps and the "ring" fell apart into
                # disconnected islands.
                wheel.visual(
                    Box((0.030, 0.060, rim_tangent)),
                    origin=_bucket_origin(theta, rim_radius, x=x),
                    material=rim_mat,
                    name=f"{side_name}_segmented_rim_{i:02d}", material_class_id="wood.rustic_weathered",
                )
        for i in range(12):
            theta = math.tau * i / 12
            y, z = _wheel_point(theta, radius * 0.48)
            # Spokes reach 0.48R + 0.43R = 0.91R (into the rim band [0.87R,
            # 0.93R]) and span 0.88*width so they overlap the rim segment blocks
            # at |x| ~ 0.42w; at 0.78R length the spoke tip was exactly tangent
            # to the rim inner face and the ring drifted off as its own island.
            wheel.visual(
                Box((width * 0.88, radius * 0.86, 0.024)),
                origin=Origin(xyz=(0.0, y, z), rpy=(math.pi / 2.0 + theta, 0.0, 0.0)),
                material="timber",
                name=f"open_spoke_{i:02d}", material_class_id="wood.natural_generic",
            )
        # The open_spoke plates above are chord plates (rpy = pi/2 - theta puts
        # their long dim tangential): they close into a 12-gon drum at ~0.48R
        # that never reaches the hub (0.18R), leaving the axle/hub cluster as a
        # floating island. Radial arms span hub -> drum -> segmented rim band
        # ([0.87R, 0.93R]) so the wheel is one connected body.
        for i in range(6):
            theta = math.tau * i / 6
            wheel.visual(
                Box((width * 0.88, radius * 0.80, 0.028)),
                origin=_bucket_origin(theta, radius * 0.54, x=0.0),
                material="timber",
                name=f"radial_spoke_arm_{i:02d}", material_class_id="wood.natural_generic",
            )
        for i in range(r.bucket_count):
            theta = math.tau * i / r.bucket_count
            wheel.visual(
                Box((width * 0.86, 0.070, 0.030)),
                origin=_bucket_origin(theta, radius * 0.98, x=0.0),
                material="wet_timber",
                name=f"bucket_floor_{i:02d}", material_class_id="wood.rustic_weathered",
            )
            # 0.88*width so the back plate reaches the segmented rim blocks at
            # |x| ~ 0.42w regardless of spoke/bucket angle alignment.
            wheel.visual(
                Box((width * 0.88, 0.024, 0.105)),
                origin=_bucket_origin(theta, radius * 0.87, x=0.0),
                material="wet_timber",
                name=f"bucket_back_{i:02d}", material_class_id="wood.rustic_weathered",
            )
            for side_name, x in (("left", -width * 0.43), ("right", width * 0.43)):
                wheel.visual(
                    Box((0.022, 0.082, 0.090)),
                    origin=_bucket_origin(theta, radius * 0.93, x=x),
                    material="wet_timber",
                    name=f"open_bucket_{side_name}_cheek_{i:02d}", material_class_id="wood.rustic_weathered",
                )
        return
    rim_mat = (
        "iron"
        if r.bucket_wheel_module in {"cast_iron_bucket_wheel", "drive_pinion_rotor"}
        else "wet_timber"
    )
    rim_thick = 0.020 if r.bucket_wheel_module != "deep_timber_bucket_wheel" else 0.034
    for side, x in (("left", -width * 0.43), ("right", width * 0.43)):
        wheel.visual(
            Cylinder(radius=radius, length=rim_thick),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=_cyl_x()),
            material=rim_mat,
            name=f"outer_rim_{side}", material_class_id=("wood.rustic_weathered" if r.bucket_wheel_module in {"spoked_shallow_bucket_wheel", "deep_timber_bucket_wheel", "open_spoke_paddle_wheel"} else "metal.cast_iron_bare"),
        )
        wheel.visual(
            Cylinder(radius=radius * 0.78, length=rim_thick * 0.75),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=_cyl_x()),
            material="shadow",
            name=f"inner_shadow_rim_{side}", material_class_id=("wood.rustic_weathered" if r.bucket_wheel_module in {"spoked_shallow_bucket_wheel", "deep_timber_bucket_wheel", "open_spoke_paddle_wheel"} else "metal.cast_iron_bare"),
        )

    spoke_count = {
        "spoked_shallow_bucket_wheel": 12,
        "deep_timber_bucket_wheel": 10,
        "drive_pinion_rotor": 14,
        "cast_iron_bucket_wheel": 16,
    }[r.bucket_wheel_module]
    spoke_mat = "iron" if r.bucket_wheel_module == "cast_iron_bucket_wheel" else "timber"
    for i in range(spoke_count):
        theta = math.tau * i / spoke_count
        y, z = _wheel_point(theta, radius * 0.45)
        # 0.88*width: the chord plates close into a drum at ~0.45R that touches
        # neither the hub (0.18R) nor, at 0.82*width, the rim discs whose inner
        # faces sit at |x| = 0.42w — embedding them into both solid discs keeps
        # the drum welded to the wheel at every angle.
        wheel.visual(
            Box((width * 0.88, radius * 0.82, 0.018)),
            origin=Origin(xyz=(0.0, y, z), rpy=(math.pi / 2.0 + theta, 0.0, 0.0)),
            material=spoke_mat,
            name=f"spoke_{i:02d}", material_class_id=("wood.natural_generic" if r.bucket_wheel_module in {"spoked_shallow_bucket_wheel", "deep_timber_bucket_wheel", "drive_pinion_rotor", "open_spoke_paddle_wheel"} else "metal.cast_iron_bare"),
        )

    bucket_depth = 0.086 if r.bucket_wheel_module == "deep_timber_bucket_wheel" else 0.060
    if r.bucket_wheel_module == "cast_iron_bucket_wheel":
        bucket_depth = 0.048
    for i in range(r.bucket_count):
        theta = math.tau * i / r.bucket_count
        bucket_mat = "wet_timber" if r.bucket_wheel_module != "cast_iron_bucket_wheel" else "iron"
        # Bucket plates span 0.88*width so they embed into both solid rim discs
        # (disc faces occupy |x| in [0.43w - t/2, 0.43w + t/2]); at 0.82*width the
        # plates stop short of the discs and whole buckets float unless a bucket
        # happens to line up with a spoke angle.
        wheel.visual(
            Box((width * 0.88, bucket_depth, 0.018)),
            origin=_bucket_origin(theta, radius * 0.92, x=0.0),
            material=bucket_mat,
            name=f"bucket_floor_{i:02d}", material_class_id=("wood.rustic_weathered" if r.bucket_wheel_module in {"spoked_shallow_bucket_wheel", "deep_timber_bucket_wheel", "drive_pinion_rotor", "open_spoke_paddle_wheel"} else "metal.cast_iron_bare"),
        )
        wheel.visual(
            Box((width * 0.88, 0.016, bucket_depth * 0.88)),
            origin=_bucket_origin(theta, radius * 0.86, x=0.0),
            material=bucket_mat,
            name=f"bucket_back_{i:02d}", material_class_id=("wood.rustic_weathered" if r.bucket_wheel_module in {"spoked_shallow_bucket_wheel", "deep_timber_bucket_wheel", "drive_pinion_rotor", "open_spoke_paddle_wheel"} else "metal.cast_iron_bare"),
        )
        wheel.visual(
            Box((width * 0.88, 0.014, bucket_depth * 0.48)),
            origin=_bucket_origin(theta, radius * 0.98, x=0.0),
            material=bucket_mat,
            name=f"bucket_lip_{i:02d}", material_class_id=("wood.rustic_weathered" if r.bucket_wheel_module in {"spoked_shallow_bucket_wheel", "deep_timber_bucket_wheel", "drive_pinion_rotor", "open_spoke_paddle_wheel"} else "metal.cast_iron_bare"),
        )
        for side_name, x in (("left", -width * 0.43), ("right", width * 0.43)):
            wheel.visual(
                Box((0.016, bucket_depth * 0.88, bucket_depth * 0.68)),
                origin=_bucket_origin(theta, radius * 0.90, x=x),
                material=bucket_mat,
                name=f"bucket_{side_name}_cheek_{i:02d}", material_class_id=("wood.rustic_weathered" if r.bucket_wheel_module in {"spoked_shallow_bucket_wheel", "deep_timber_bucket_wheel", "drive_pinion_rotor", "open_spoke_paddle_wheel"} else "metal.cast_iron_bare"),
            )
        if i % 2 == 0:
            wheel.visual(
                Box((0.018, bucket_depth * 0.72, bucket_depth * 0.20)),
                origin=_bucket_origin(theta, radius * 0.90, x=-width * 0.42),
                material="iron",
                name=f"bucket_left_strap_{i:02d}", material_class_id="metal.cast_iron_bare",
            )
        if i % max(3, r.bucket_count // 8) == 0:
            wheel.visual(
                Box((width * 0.86, 0.022, 0.024)),
                origin=_bucket_origin(theta, radius * 0.76, x=0.0),
                material=rim_mat,
                name=f"rim_spacer_tie_{i:02d}", material_class_id=("wood.rustic_weathered" if r.bucket_wheel_module in {"spoked_shallow_bucket_wheel", "deep_timber_bucket_wheel", "open_spoke_paddle_wheel"} else "metal.cast_iron_bare"),
            )

    if r.bucket_wheel_module == "drive_pinion_rotor":
        pinion_x = width * 0.58
        wheel.visual(
            Cylinder(radius=radius * 0.23, length=0.045),
            origin=Origin(xyz=(pinion_x, 0.0, 0.0), rpy=_cyl_x()),
            material="iron",
            name="outboard_drive_pinion", material_class_id="metal.cast_iron_bare",
        )
        for i in range(12):
            theta = math.tau * i / 12
            y, z = _wheel_point(theta, radius * 0.25)
            wheel.visual(
                Box((0.050, 0.038, 0.018)),
                origin=Origin(xyz=(pinion_x, y, z), rpy=(theta, 0.0, 0.0)),
                material="iron",
                name=f"pinion_tooth_{i:02d}", material_class_id="metal.cast_iron_bare",
            )
    elif r.bucket_wheel_module == "deep_timber_bucket_wheel":
        wheel.visual(
            Cylinder(radius=radius * 0.64, length=width * 0.88),
            origin=Origin(rpy=_cyl_x()),
            material="wet_timber",
            name="inner_drum_shadow", material_class_id="wood.rustic_weathered",
        )


def _build_control(model: ArticulatedObject, r: ResolvedOvershotWaterwheelConfig) -> None:
    frame = model.get_part("frame")
    feed_parent_name = "frame"
    if r.support_and_feed_module == "detached_launder_frame":
        feed_parent_name = "launder"
    elif r.support_and_feed_module == "detached_inlet_box_frame":
        feed_parent_name = "inlet_box"
    feed_parent = model.get_part(feed_parent_name)
    if r.water_control_module == "fixed_chute_only":
        return
    if r.water_control_module == "sliding_sluice_gate":
        parent = feed_parent if feed_parent_name == "inlet_box" else frame
        gate_x = r.wheel_width * 0.46
        # Keep the whole gate travel envelope (board half-height 0.09 plus 0.08
        # downward travel) clear of the spinning wheel's outer envelope, else
        # motion QC finds the gate board / runners inside rotating bucket plates.
        min_gate_center_z = r.axle_height + _wheel_outer_extent(r) + 0.09 + 0.08 + 0.006
        if parent is frame:
            guide_z = max(r.chute_height - 0.02, min_gate_center_z)
            guide_y = r.wheel_radius * 0.01
        else:
            # Feed part origin sits at (0, -0.36R, chute_height) on the frame.
            guide_z = max(0.03, min_gate_center_z - r.chute_height)
            guide_y = 0.0
        guide_height = 0.24
        parent.visual(
            Box((r.wheel_width * 0.52, 0.032, 0.14)),
            origin=Origin(
                xyz=(
                    0.0,
                    guide_y,
                    guide_z,
                )
            ),
            material="iron",
            name="sluice_gate_guides", material_class_id="metal.cast_iron_bare",
        )
        parent.visual(
            Box((r.wheel_width * 0.54, 0.034, 0.026)),
            origin=Origin(xyz=(0.0, guide_y, guide_z - 0.105)),
            material="wet_timber",
            name="sluice_gate_sill", material_class_id="wood.rustic_weathered",
        )
        parent.visual(
            Box((r.wheel_width * 0.54, 0.034, 0.026)),
            origin=Origin(xyz=(0.0, guide_y, guide_z + 0.135)),
            material="wet_timber",
            name="sluice_gate_lintel", material_class_id="wood.rustic_weathered",
        )
        for side_name, x in (("left", -gate_x * 0.55), ("right", gate_x * 0.55)):
            parent.visual(
                Box((0.022, 0.052, guide_height)),
                origin=Origin(xyz=(x, guide_y, guide_z + 0.020)),
                material="iron",
                name=f"{side_name}_sluice_side_guide", material_class_id="metal.cast_iron_bare",
            )
        if parent is frame:
            # Carry the sluice guide frame down to the frame via side posts that
            # clear the wheel, instead of a stay routed through the wheel centre.
            _add_chute_gantry(frame, r, y=guide_y, z_top=guide_z + 0.020, name="sluice")
        gate = model.part("sluice_gate")
        gate.visual(
            Box((gate_x, 0.026, 0.18)),
            origin=Origin(),
            material="wet_timber",
            name="sliding_gate_board", material_class_id="wood.rustic_weathered",
        )
        # Runners are centred on the board edges (+-0.5*gate_x) so they always
        # overlap the board by half their width; at 0.52*gate_x they detach from
        # the 0.5*gate_x-wide board once wheel_width > ~0.54.
        for side_name, x in (("left", -gate_x * 0.50), ("right", gate_x * 0.50)):
            gate.visual(
                Box((0.010, 0.030, 0.17)),
                origin=Origin(xyz=(x, 0.0, 0.0)),
                material="iron",
                name=f"{side_name}_gate_runner", material_class_id="metal.cast_iron_bare",
            )
        gate.visual(
            Box((r.wheel_width * 0.18, 0.034, 0.035)),
            origin=Origin(xyz=(0.0, -0.004, 0.095)),
            material="iron",
            name="gate_pull_handle", material_class_id="metal.cast_iron_bare",
        )
        model.articulation(
            "frame_to_sluice_gate",
            ArticulationType.PRISMATIC,
            parent=parent,
            child=gate,
            origin=Origin(
                xyz=(
                    0.0,
                    guide_y,
                    guide_z,
                )
            ),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=12.0, velocity=0.12, lower=-0.08, upper=0.10),
        )
    elif r.water_control_module == "pivoting_shutoff_flap":
        parent = feed_parent if feed_parent_name == "launder" else frame
        flap_y = -r.wheel_radius * 0.28 if parent is frame else r.wheel_radius * 0.08
        flap_z = r.chute_height - 0.04 if parent is frame else -0.04
        parent.visual(
            Cylinder(radius=0.018, length=r.wheel_width * 0.54),
            origin=Origin(xyz=(0.0, flap_y, flap_z), rpy=_cyl_x()),
            material="iron",
            name="flap_hinge_socket", material_class_id="metal.cast_iron_bare",
        )
        if parent is frame:
            # Hanger straps tying the hinge socket up into the feed floor above
            # it. The socket hangs below the floor (flap_z = chute_height - 0.04
            # while the floor underside is at floor_z - 0.017), so without these
            # the socket is a floating island in the frame part. The straps wrap
            # the socket (their z-range covers the full pin diameter) and embed
            # ~0.03 into the floor plank; the pin still spins freely because the
            # straps are axisymmetric-agnostic hinge knuckles around the x-axis
            # joint at (0, flap_y, flap_z).
            floor_z = r.chute_height + (
                0.030 if r.support_and_feed_module == "long_launder_trestle" else 0.0
            )
            hanger_top = floor_z + 0.012
            hanger_bottom = flap_z - 0.025
            for side_name, x in (
                ("left", -r.wheel_width * 0.15),
                ("right", r.wheel_width * 0.15),
            ):
                frame.visual(
                    Box((0.032, 0.050, hanger_top - hanger_bottom)),
                    origin=Origin(xyz=(x, flap_y, (hanger_top + hanger_bottom) * 0.5)),
                    material="iron",
                    name=f"{side_name}_flap_hinge_hanger", material_class_id="metal.cast_iron_bare",
                )
        flap = model.part("shutoff_flap")
        flap.visual(
            Cylinder(radius=0.016, length=r.wheel_width * 0.50),
            origin=Origin(rpy=_cyl_x()),
            material="iron",
            name="flap_hinge_barrel", material_class_id="metal.cast_iron_bare",
        )
        # Arm rigidly tying the gate board back to the hinge barrel (the pivot),
        # so the board is carried by the hinge instead of floating off it.
        flap.visual(
            Box((r.wheel_width * 0.46, 0.10, 0.024)),
            origin=Origin(xyz=(0.0, -0.055, 0.020)),
            material="wet_timber",
            name="flap_arm", material_class_id="wood.rustic_weathered",
        )
        flap.visual(
            Box((r.wheel_width * 0.50, 0.026, 0.18)),
            origin=Origin(xyz=(0.0, -0.110, 0.080)),
            material="wet_timber",
            name="flap_board", material_class_id="wood.rustic_weathered",
        )
        # Link from the board up to the pull bar so the handle is attached.
        flap.visual(
            Box((0.026, 0.13, 0.026)),
            origin=Origin(xyz=(0.0, -0.165, 0.150)),
            material="iron",
            name="flap_pull_link", material_class_id="metal.cast_iron_bare",
        )
        flap.visual(
            Box((0.026, r.wheel_width * 0.20, 0.026)),
            origin=Origin(xyz=(0.0, -0.225, 0.150)),
            material="iron",
            name="flap_pull_bar", material_class_id="metal.cast_iron_bare",
        )
        model.articulation(
            "frame_to_shutoff_flap",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=flap,
            origin=Origin(xyz=(0.0, flap_y, flap_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=7.0, velocity=0.50, lower=-1.05, upper=0.20),
        )
    elif r.water_control_module == "brake_arm":
        pivot_x = _support_half_span(r) + 0.035
        pivot_z = r.axle_height + r.wheel_radius * 0.36
        frame.visual(
            Box((0.050, 0.060, 0.060)),
            origin=Origin(xyz=(pivot_x, r.wheel_radius * 0.12, pivot_z)),
            material="iron",
            name="brake_pivot_block", material_class_id="metal.cast_iron_bare",
        )
        # Pivot post carrying the brake pivot block down to the frame. The block
        # sits above the timber post tops (ah + 0.14) and outboard of them in y,
        # so on its own it floats. Anchor it to the right bearing face
        # (Box(0.026, 0.12, 0.10) at (half_span, 0, axle_height)), which exists
        # for every support module: the post overlaps the bearing face in
        # x [hs - 0.013, hs + 0.013], y [-0.010, 0.060], z [ah - 0.020, ah + 0.050]
        # and the block in x [hs + 0.010, hs + 0.036], y (0.05 band), z (0.025).
        half_span = pivot_x - 0.035
        post_y0, post_y1 = -0.010, r.wheel_radius * 0.12 + 0.020
        post_z0, post_z1 = r.axle_height - 0.020, pivot_z - 0.005
        frame.visual(
            Box((0.052, post_y1 - post_y0, post_z1 - post_z0)),
            origin=Origin(
                xyz=(half_span + 0.010, (post_y0 + post_y1) * 0.5, (post_z0 + post_z1) * 0.5)
            ),
            material="iron",
            name="brake_pivot_post", material_class_id="metal.cast_iron_bare",
        )
        brake = model.part("brake_arm")
        brake.visual(
            Cylinder(radius=0.016, length=0.052),
            origin=Origin(rpy=_cyl_y()),
            material="iron",
            name="brake_pivot_pin", material_class_id="metal.cast_iron_bare",
        )
        brake.visual(
            Box((0.040, r.wheel_radius * 0.54, 0.032)),
            origin=Origin(xyz=(0.0, -r.wheel_radius * 0.25, 0.0)),
            material="timber",
            name="brake_handle_arm", material_class_id="wood.natural_generic",
        )
        brake.visual(
            Box((0.030, r.wheel_radius * 0.24, 0.026)),
            origin=Origin(xyz=(0.0, r.wheel_radius * 0.13, 0.0)),
            material="iron",
            name="brake_counterweight_link", material_class_id="metal.cast_iron_bare",
        )
        # Drop link from the handle arm down to the brake shoe so the shoe is
        # carried by the arm rather than floating off its end.
        brake.visual(
            Box((0.034, 0.052, r.wheel_radius * 0.16)),
            origin=Origin(xyz=(-0.006, -r.wheel_radius * 0.52, -r.wheel_radius * 0.05)),
            material="iron",
            name="brake_shoe_link", material_class_id="metal.cast_iron_bare",
        )
        brake.visual(
            Box((0.052, 0.065, 0.040)),
            origin=Origin(xyz=(-0.012, -r.wheel_radius * 0.54, -r.wheel_radius * 0.10)),
            material="wet_timber",
            name="rim_brake_shoe", material_class_id="wood.rustic_weathered",
        )
        model.articulation(
            "frame_to_brake_arm",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=brake,
            origin=Origin(xyz=(pivot_x, r.wheel_radius * 0.12, pivot_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=20.0, velocity=0.45, lower=-0.70, upper=0.45),
        )
    else:
        hinge_x = -_support_half_span(r) - 0.040
        hinge_z = r.axle_height + r.wheel_radius * 0.24
        frame.visual(
            Cylinder(radius=0.017, length=r.wheel_radius * 0.72),
            origin=Origin(xyz=(hinge_x, -r.wheel_radius * 0.24, hinge_z)),
            material="iron",
            name="guard_hinge_socket", material_class_id="metal.cast_iron_bare",
        )
        guard = model.part("guard_panel")
        guard.visual(
            Cylinder(radius=0.014, length=r.wheel_radius * 0.70),
            origin=Origin(),
            material="iron",
            name="guard_hinge_barrel", material_class_id="metal.cast_iron_bare",
        )
        guard.visual(
            Box((0.028, r.wheel_radius * 0.74, r.wheel_radius * 0.72)),
            origin=Origin(xyz=(0.0, r.wheel_radius * 0.34, -r.wheel_radius * 0.10)),
            material="timber",
            name="hinged_guard_panel", material_class_id="wood.natural_generic",
        )
        model.articulation(
            "frame_to_guard_panel",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=guard,
            origin=Origin(xyz=(hinge_x, -r.wheel_radius * 0.24, hinge_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=5.0, velocity=0.55, lower=0.0, upper=1.35),
        )


def build_overshot_waterwheel(
    config: OvershotWaterwheelConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="overshot_waterwheel", assets=assets)
    for name, rgba in r.palette.items():
        model.material(name, rgba=rgba)
    _build_support_and_feed(model, r)
    _build_bucket_wheel(model, r)
    frame = model.get_part("frame")
    wheel = model.get_part("wheel")
    model.articulation(
        "wheel_spin",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=wheel,
        origin=Origin(xyz=(0.0, 0.0, r.axle_height)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=4.0),
        mating=MatingContract(
            "left_bearing_face", "positive_x", "axle", "negative_x", contact_tol=0.002
        ),
    )
    _build_control(model, r)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_overshot_waterwheel(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_overshot_waterwheel(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedOvershotWaterwheelConfig) -> list[tuple[str, str]]:
    return [
        ("support_and_feed", r.support_and_feed_module),
        ("bucket_wheel", r.bucket_wheel_module),
        ("water_control_or_service", r.water_control_module),
        ("bucket_multiplicity", f"{r.bucket_count}_buckets"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def run_overshot_waterwheel_tests(
    object_model: ArticulatedObject, config: OvershotWaterwheelConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    names = {p.name for p in object_model.parts}
    joints = {j.name: j for j in object_model.articulations}
    ctx.check("frame_present", "frame" in names)
    ctx.check("wheel_present", "wheel" in names)
    ctx.check("wheel_spin_present", "wheel_spin" in joints)
    ctx.check("wheel_axis_horizontal", joints["wheel_spin"].axis == (1.0, 0.0, 0.0))
    ctx.check(
        "wheel_spin_continuous",
        joints["wheel_spin"].articulation_type == ArticulationType.CONTINUOUS,
    )
    feed_visual_names = set(
        frame_visuals := {v.name for v in object_model.get_part("frame").visuals}
    )
    for feed_name in ("launder", "inlet_box"):
        if feed_name in names:
            feed_visual_names.update(v.name for v in object_model.get_part(feed_name).visuals)
    ctx.check(
        "overhead_chute_present",
        "overhead_chute_floor" in frame_visuals
        or "long_launder_floor" in frame_visuals
        or "feed_floor" in feed_visual_names,
    )
    ctx.check(
        "overshot_water_sheet_present",
        "visible_overshot_water_sheet" in frame_visuals
        or "long_launder_water_sheet" in frame_visuals
        or "overshot_water_sheet" in feed_visual_names,
    )
    bucket_visuals = [
        v.name for v in object_model.get_part("wheel").visuals if v.name.startswith("bucket_floor_")
    ]
    ctx.check("bucket_count_matches_config", len(bucket_visuals) == r.bucket_count)
    control_part_by_module = {
        "sliding_sluice_gate": "sluice_gate",
        "pivoting_shutoff_flap": "shutoff_flap",
        "brake_arm": "brake_arm",
        "hinged_guard_panel": "guard_panel",
    }
    if r.water_control_module in control_part_by_module:
        ctx.check("control_part_present", control_part_by_module[r.water_control_module] in names)

    for a, b in (
        ("frame", "wheel"),
        ("frame", "launder"),
        ("frame", "inlet_box"),
        ("frame", "sluice_gate"),
        ("inlet_box", "sluice_gate"),
        ("frame", "shutoff_flap"),
        ("launder", "shutoff_flap"),
        ("frame", "brake_arm"),
        ("wheel", "brake_arm"),
        ("frame", "guard_panel"),
    ):
        if a in names and b in names:
            ctx.allow_overlap(
                object_model.get_part(a),
                object_model.get_part(b),
                reason="Captured axle, gate guide, hinge barrel, brake shoe, or guard hardware intentionally overlaps at its interface.",
            )
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry()
    ctx.fail_if_joint_mating_has_gap()
    return ctx.report()


__all__ = [
    "__modular__",
    "OvershotWaterwheelConfig",
    "ResolvedOvershotWaterwheelConfig",
    "config_from_seed",
    "resolve_config",
    "build_overshot_waterwheel",
    "build_seeded_overshot_waterwheel",
    "slot_choices_for_seed",
    "run_overshot_waterwheel_tests",
]
