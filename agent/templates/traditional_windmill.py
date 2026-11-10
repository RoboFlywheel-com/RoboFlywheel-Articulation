# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for `traditional_windmill`.

Slot graph:
    support_tower -> yaw_cap_head -> sail_rotor
    support_tower/yaw_cap_head -> service_accessory
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
    Sphere,
    TestContext,
    TestReport,
)

__modular__ = True

SupportTowerModule = Literal[
    "low_body_tower",
    "rugged_tower_with_door",
    "industrial_guarded_tower",
    "split_bearing_tower",
]
YawCapModule = Literal[
    "continuous_roof_cap",
    "bounded_service_cap",
    "split_head_frame",
    "weatherproof_shell_cap",
]
SailRotorModule = Literal[
    "classic_lattice_sails",
    "retrofit_dense_rotor",
    "compact_stow_rotor",
    "weatherproof_rotor",
    "articulated_stow_sails",
]
ServiceAccessoryModule = Literal[
    "access_door",
    "brake_lever",
    "access_door_and_brake_lever",
    "lockout_lever",
    "side_hatch",
    "none",
]
PaletteName = Literal["limewashed_oak", "brick_and_oak", "weathered_gray", "painted_field"]

SUPPORT_MODULES: tuple[SupportTowerModule, ...] = (
    "low_body_tower",
    "rugged_tower_with_door",
    "industrial_guarded_tower",
    "split_bearing_tower",
)
YAW_CAP_MODULES: tuple[YawCapModule, ...] = (
    "continuous_roof_cap",
    "bounded_service_cap",
    "split_head_frame",
    "weatherproof_shell_cap",
)
SAIL_ROTOR_MODULES: tuple[SailRotorModule, ...] = (
    "classic_lattice_sails",
    "retrofit_dense_rotor",
    "compact_stow_rotor",
    "weatherproof_rotor",
    "articulated_stow_sails",
)
SERVICE_MODULES: tuple[ServiceAccessoryModule, ...] = (
    "access_door",
    "brake_lever",
    "access_door_and_brake_lever",
    "lockout_lever",
    "side_hatch",
    "none",
)

PALETTES: dict[PaletteName, dict[str, tuple[float, float, float, float]]] = {
    "limewashed_oak": {
        "stone": (0.70, 0.68, 0.60, 1.0),
        "plaster": (0.86, 0.84, 0.75, 1.0),
        "wood": (0.43, 0.27, 0.13, 1.0),
        "roof": (0.30, 0.18, 0.13, 1.0),
        "metal": (0.31, 0.32, 0.31, 1.0),
        "shadow": (0.05, 0.045, 0.035, 1.0),
    },
    "brick_and_oak": {
        "stone": (0.52, 0.28, 0.20, 1.0),
        "plaster": (0.72, 0.50, 0.40, 1.0),
        "wood": (0.36, 0.22, 0.12, 1.0),
        "roof": (0.22, 0.17, 0.15, 1.0),
        "metal": (0.23, 0.24, 0.25, 1.0),
        "shadow": (0.055, 0.040, 0.035, 1.0),
    },
    "weathered_gray": {
        "stone": (0.48, 0.50, 0.48, 1.0),
        "plaster": (0.63, 0.66, 0.62, 1.0),
        "wood": (0.36, 0.34, 0.30, 1.0),
        "roof": (0.18, 0.20, 0.21, 1.0),
        "metal": (0.42, 0.43, 0.42, 1.0),
        "shadow": (0.04, 0.045, 0.05, 1.0),
    },
    "painted_field": {
        "stone": (0.58, 0.55, 0.50, 1.0),
        "plaster": (0.82, 0.72, 0.56, 1.0),
        "wood": (0.55, 0.20, 0.15, 1.0),
        "roof": (0.12, 0.22, 0.30, 1.0),
        "metal": (0.24, 0.26, 0.27, 1.0),
        "shadow": (0.05, 0.04, 0.035, 1.0),
    },
}


@dataclass(frozen=True)
class TraditionalWindmillConfig:
    support_tower_module: SupportTowerModule | None = None
    yaw_cap_head_module: YawCapModule | None = None
    sail_rotor_module: SailRotorModule | None = None
    service_accessory_module: ServiceAccessoryModule | None = None
    sail_count: int = 4
    tower_height: float = 0.72
    tower_radius: float = 0.28
    cap_length: float = 0.42
    cap_width: float = 0.28
    cap_height: float = 0.20
    sail_span: float = 0.54
    hub_radius: float = 0.075
    palette_name: PaletteName = "limewashed_oak"
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["limewashed_oak"])
    )


@dataclass(frozen=True)
class ResolvedTraditionalWindmillConfig:
    support_tower_module: SupportTowerModule
    yaw_cap_head_module: YawCapModule
    sail_rotor_module: SailRotorModule
    service_accessory_module: ServiceAccessoryModule
    sail_count: int
    tower_height: float
    tower_radius: float
    cap_length: float
    cap_width: float
    cap_height: float
    sail_span: float
    hub_radius: float
    palette_name: PaletteName
    palette: dict[str, tuple[float, float, float, float]]


@dataclass(frozen=True)
class _SupportInfo:
    yaw_parent: str
    yaw_origin: tuple[float, float, float]
    yaw_parent_visual: str


@dataclass(frozen=True)
class _CapInfo:
    rotor_parent: str
    rotor_origin: tuple[float, float, float]
    rotor_parent_visual: str
    yaw_joint_type: ArticulationType
    yaw_limits: MotionLimits | None


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _cyl_x() -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0, 0.0)


def _cyl_y() -> tuple[float, float, float]:
    return (math.pi / 2.0, 0.0, 0.0)


def _radial_origin(angle: float, radius: float, *, x: float = 0.0) -> Origin:
    return Origin(
        xyz=(x, math.cos(angle) * radius, math.sin(angle) * radius),
        rpy=(angle, 0.0, 0.0),
    )


def config_from_seed(seed: int) -> TraditionalWindmillConfig:
    if seed == 0:
        return TraditionalWindmillConfig(
            support_tower_module="low_body_tower",
            yaw_cap_head_module="continuous_roof_cap",
            sail_rotor_module="classic_lattice_sails",
            service_accessory_module="access_door",
            sail_count=4,
            tower_height=0.72,
            tower_radius=0.28,
            cap_length=0.42,
            cap_width=0.28,
            cap_height=0.20,
            sail_span=0.54,
            hub_radius=0.075,
            palette_name="limewashed_oak",
        )
    rng = random.Random(seed)
    return TraditionalWindmillConfig(
        support_tower_module=rng.choice(SUPPORT_MODULES),
        yaw_cap_head_module=rng.choice(YAW_CAP_MODULES),
        sail_rotor_module=rng.choice(SAIL_ROTOR_MODULES),
        service_accessory_module=rng.choice(SERVICE_MODULES),
        sail_count=rng.randint(4, 8),
        tower_height=rng.uniform(0.62, 1.05),
        tower_radius=rng.uniform(0.22, 0.34),
        cap_length=rng.uniform(0.36, 0.55),
        cap_width=rng.uniform(0.23, 0.34),
        cap_height=rng.uniform(0.17, 0.27),
        sail_span=rng.uniform(0.44, 0.72),
        hub_radius=rng.uniform(0.055, 0.095),
        palette_name=rng.choice(tuple(PALETTES)),
    )


def resolve_config(config: TraditionalWindmillConfig) -> ResolvedTraditionalWindmillConfig:
    support = config.support_tower_module or "low_body_tower"
    cap = config.yaw_cap_head_module or "continuous_roof_cap"
    rotor = config.sail_rotor_module or "classic_lattice_sails"
    service = config.service_accessory_module or "access_door"
    if support not in SUPPORT_MODULES:
        raise ValueError(f"Unsupported support_tower_module: {support!r}")
    if cap not in YAW_CAP_MODULES:
        raise ValueError(f"Unsupported yaw_cap_head_module: {cap!r}")
    if rotor not in SAIL_ROTOR_MODULES:
        raise ValueError(f"Unsupported sail_rotor_module: {rotor!r}")
    if service not in SERVICE_MODULES:
        raise ValueError(f"Unsupported service_accessory_module: {service!r}")
    if config.palette_name not in PALETTES:
        raise ValueError(f"Unsupported palette_name: {config.palette_name!r}")
    radius = _clamp(config.tower_radius, 0.18, 0.38)
    sail_count = max(4, min(8, int(config.sail_count)))
    if rotor == "articulated_stow_sails":
        sail_count = 4
    return ResolvedTraditionalWindmillConfig(
        support_tower_module=support,
        yaw_cap_head_module=cap,
        sail_rotor_module=rotor,
        service_accessory_module=service,
        sail_count=sail_count,
        tower_height=_clamp(config.tower_height, 0.55, 1.15),
        tower_radius=radius,
        cap_length=_clamp(config.cap_length, radius * 1.25, 0.62),
        cap_width=_clamp(config.cap_width, radius * 0.72, 0.38),
        cap_height=_clamp(config.cap_height, 0.15, 0.30),
        sail_span=_clamp(config.sail_span, 0.38, 0.78),
        hub_radius=_clamp(config.hub_radius, 0.045, 0.105),
        palette_name=config.palette_name,
        palette=dict(PALETTES[config.palette_name]),
    )


def _tower_window_face_radius(r: ResolvedTraditionalWindmillConfig) -> float:
    """Radial distance of the tower body surface along +/-x at the upper-window z."""
    return {
        "low_body_tower": r.tower_radius,
        "rugged_tower_with_door": r.tower_radius * 0.79,  # square body half-width
        "industrial_guarded_tower": r.tower_radius * 0.55,  # slim core
        "split_bearing_tower": r.tower_radius * 0.82,
    }[r.support_tower_module]


def _add_tower_bands(tower, r: ResolvedTraditionalWindmillConfig, *, count: int) -> None:
    for i in range(count):
        z = r.tower_height * (0.20 + 0.62 * i / max(1, count - 1))
        radius = r.tower_radius * (1.03 - 0.23 * z / r.tower_height)
        tower.visual(
            Cylinder(radius=radius, length=0.018),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material="stone",
            name=f"stone_band_{i}", material_class_id="stone.masonry_wall",
        )


def _build_support(model: ArticulatedObject, r: ResolvedTraditionalWindmillConfig) -> _SupportInfo:
    tower = model.part("tower")
    seat_h = 0.045
    if r.support_tower_module == "low_body_tower":
        tower.visual(
            Cylinder(radius=r.tower_radius * 1.38, length=0.10),
            origin=Origin(xyz=(0.0, 0.0, 0.05)),
            material="stone",
            name="broad_plinth", material_class_id="stone.masonry_wall",
        )
        tower.visual(
            Cylinder(radius=r.tower_radius, length=r.tower_height * 0.82),
            origin=Origin(xyz=(0.0, 0.0, r.tower_height * 0.43)),
            material="plaster",
            name="tower_body", material_class_id="plaster.stucco",
        )
        _add_tower_bands(tower, r, count=4)
        tower.visual(
            Box((0.026, r.tower_radius * 0.42, r.tower_height * 0.20)),
            origin=Origin(xyz=(r.tower_radius * 0.93, 0.0, r.tower_height * 0.35)),
            material="shadow",
            name="front_window", material_class_id="glass.smoked_tinted",
        )
    elif r.support_tower_module == "rugged_tower_with_door":
        tower.visual(
            Cylinder(radius=r.tower_radius * 1.30, length=0.12),
            origin=Origin(xyz=(0.0, 0.0, 0.06)),
            material="stone",
            name="foundation_plinth", material_class_id="stone.masonry_wall",
        )
        tower.visual(
            Box((r.tower_radius * 1.58, r.tower_radius * 1.58, r.tower_height * 0.84)),
            origin=Origin(xyz=(0.0, 0.0, r.tower_height * 0.44)),
            material="plaster",
            name="square_mill_body", material_class_id="plaster.stucco",
        )
        tower.visual(
            Box((r.tower_radius * 0.54, 0.030, r.tower_height * 0.34)),
            origin=Origin(xyz=(0.0, -r.tower_radius * 0.80, r.tower_height * 0.25)),
            material="wood",
            name="door_frame", material_class_id="wood.oak",
        )
        tower.visual(
            Cylinder(radius=0.018, length=r.tower_height * 0.32),
            origin=Origin(
                xyz=(-r.tower_radius * 0.30, -r.tower_radius * 0.84, r.tower_height * 0.25)
            ),
            material="metal",
            name="door_hinge_socket", material_class_id="metal.cast_iron_bare",
        )
        _add_tower_bands(tower, r, count=3)
    elif r.support_tower_module == "industrial_guarded_tower":
        tower.visual(
            Cylinder(radius=r.tower_radius * 1.15, length=0.10),
            origin=Origin(xyz=(0.0, 0.0, 0.05)),
            material="stone",
            name="round_base", material_class_id="stone.masonry_wall",
        )
        tower.visual(
            Cylinder(radius=r.tower_radius * 0.55, length=r.tower_height * 0.88),
            origin=Origin(xyz=(0.0, 0.0, r.tower_height * 0.45)),
            material="plaster",
            name="central_tower_core", material_class_id="plaster.stucco",
        )
        for i, angle in enumerate((0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)):
            tower.visual(
                Cylinder(radius=0.018, length=r.tower_height * 0.72),
                origin=Origin(
                    xyz=(
                        math.cos(angle) * r.tower_radius * 0.78,
                        math.sin(angle) * r.tower_radius * 0.78,
                        r.tower_height * 0.44,
                    )
                ),
                material="metal",
                name=f"guard_upright_{i}", material_class_id="metal.steel_galvanized",
            )
        for i, z in enumerate((r.tower_height * 0.32, r.tower_height * 0.58)):
            tower.visual(
                Cylinder(radius=r.tower_radius * 0.84, length=0.015),
                origin=Origin(xyz=(0.0, 0.0, z)),
                material="metal",
                name=f"guard_ring_{i}", material_class_id="metal.steel_galvanized",
            )
    else:
        tower.visual(
            Cylinder(radius=r.tower_radius * 1.18, length=0.10),
            origin=Origin(xyz=(0.0, 0.0, 0.05)),
            material="stone",
            name="split_base_plinth", material_class_id="stone.masonry_wall",
        )
        tower.visual(
            Cylinder(radius=r.tower_radius * 0.82, length=r.tower_height * 0.82),
            origin=Origin(xyz=(0.0, 0.0, r.tower_height * 0.42)),
            material="plaster",
            name="bearing_tower_body", material_class_id="plaster.stucco",
        )
        _add_tower_bands(tower, r, count=3)

    # Neck bridging the tower body up to the yaw seat — the body tops out around
    # 0.84*tower_height while the yaw seat sits just under the rim, so without this
    # the whole yaw-seat/curb/pintle assembly floats above the shaft.
    neck_bot = r.tower_height * 0.80
    neck_top = r.tower_height - seat_h * 0.5
    tower.visual(
        Cylinder(radius=r.tower_radius * 0.80, length=neck_top - neck_bot),
        origin=Origin(xyz=(0.0, 0.0, (neck_bot + neck_top) * 0.5)),
        material="plaster",
        name="tower_neck", material_class_id="plaster.stucco",
    )
    tower.visual(
        Cylinder(radius=r.tower_radius * 0.74, length=seat_h),
        origin=Origin(xyz=(0.0, 0.0, r.tower_height - seat_h * 0.5)),
        material="wood",
        name="yaw_seat", material_class_id="wood.oak",
    )
    tower.visual(
        Cylinder(radius=r.tower_radius * 0.88, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, r.tower_height + 0.010)),
        material="metal",
        name="tower_curb_ring", material_class_id="metal.cast_iron_bare",
    )
    tower.visual(
        Cylinder(radius=r.tower_radius * 0.16, length=0.080),
        origin=Origin(xyz=(0.0, 0.0, r.tower_height + 0.040)),
        material="metal",
        name="yaw_pintle", material_class_id="metal.steel_bare",
    )
    tower.visual(
        Box((r.tower_radius * 1.55, 0.030, 0.026)),
        origin=Origin(xyz=(0.0, 0.0, r.tower_height - 0.015)),
        material="metal",
        name="top_adapter_beam_x", material_class_id="metal.steel_bare",
    )
    tower.visual(
        Box((0.030, r.tower_radius * 1.55, 0.026)),
        origin=Origin(xyz=(0.0, 0.0, r.tower_height - 0.015)),
        material="metal",
        name="top_adapter_beam_y", material_class_id="metal.steel_bare",
    )
    # Louvered windows mount on the actual body surface of the chosen tower
    # module (slim industrial core, square rugged body, ...): the 0.020-thick
    # frame is embedded 5mm into that face and the slats 3mm into the frame,
    # instead of floating at a fixed 0.92*R that only the round low body reaches.
    window_face = _tower_window_face_radius(r)
    window_r = window_face + 0.005
    slat_r = window_face + 0.012
    for i, angle in enumerate((0.0, math.pi)):
        tower.visual(
            Box((0.020, r.tower_radius * 0.34, r.tower_height * 0.11)),
            origin=Origin(
                xyz=(
                    math.cos(angle) * window_r,
                    math.sin(angle) * window_r,
                    r.tower_height * 0.56,
                ),
                rpy=(0.0, 0.0, angle),
            ),
            material="wood",
            name=f"louvered_upper_window_{i}", material_class_id="wood.oak",
        )
        for slat in range(3):
            tower.visual(
                Box((0.022, r.tower_radius * 0.30, 0.010)),
                origin=Origin(
                    xyz=(
                        math.cos(angle) * slat_r,
                        math.sin(angle) * slat_r,
                        r.tower_height * (0.525 + 0.026 * slat),
                    ),
                    rpy=(0.0, 0.0, angle),
                ),
                material="shadow",
                name=f"upper_window_slat_{i}_{slat}", material_class_id="wood.oak",
            )

    if r.support_tower_module != "split_bearing_tower":
        return _SupportInfo("tower", (0.0, 0.0, r.tower_height), "yaw_seat")

    bearing = model.part("bearing_module")
    bearing_h = 0.085
    bearing.visual(
        Cylinder(radius=r.tower_radius * 0.62, length=bearing_h),
        origin=Origin(xyz=(0.0, 0.0, bearing_h * 0.5)),
        material="metal",
        name="bearing_drum", material_class_id="metal.cast_iron_bare",
    )
    bearing.visual(
        Cylinder(radius=r.tower_radius * 0.70, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, bearing_h - 0.009)),
        material="wood",
        name="upper_bearing_ring", material_class_id="wood.oak",
    )
    bearing.visual(
        Cylinder(radius=r.tower_radius * 0.66, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, 0.009)),
        material="metal",
        name="lower_bearing_retainer", material_class_id="metal.steel_bare",
    )
    for i, angle in enumerate((0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)):
        bearing.visual(
            Cylinder(radius=0.007, length=0.018),
            origin=Origin(
                xyz=(
                    math.cos(angle) * r.tower_radius * 0.44,
                    math.sin(angle) * r.tower_radius * 0.44,
                    bearing_h - 0.006,
                )
            ),
            material="metal",
            name=f"bearing_cap_bolt_{i}", material_class_id="metal.steel_bare",
        )
    model.articulation(
        "tower_to_bearing_module",
        ArticulationType.FIXED,
        parent=tower,
        child=bearing,
        origin=Origin(xyz=(0.0, 0.0, r.tower_height)),
        mating=MatingContract("yaw_seat", "positive_z", "bearing_drum", "negative_z"),
    )
    return _SupportInfo("bearing_module", (0.0, 0.0, bearing_h), "upper_bearing_ring")


def _rotor_axis_standoff(r: ResolvedTraditionalWindmillConfig) -> float:
    """Horizontal distance from the tower yaw axis to the rotor hub joint."""
    return max(r.cap_length * 0.54, r.tower_radius + r.hub_radius + 0.09)


_FOLD_LIMIT_MAX = 1.28
_FOLD_CLEARANCE = 0.010


def _safe_fold_upper(r: ResolvedTraditionalWindmillConfig) -> float:
    """Largest fold angle keeping a folded sail blade clear of the tower column.

    The fold joint spins the blade about its local +z (tangential) axis, so a
    blade point at local (px, py) sits at horizontal distance
    ``hinge_x + px*cos(t) - py*sin(t)`` from the yaw axis. Neither the hub spin
    (roll about the rotor axis) nor the cap yaw changes that distance, so one
    bound covers every rotor phase. The critical point is the outboard spar-tip
    corner (max py, min px); requiring it to stay ``_FOLD_CLEARANCE`` in front
    of the tower's worst-case horizontal keep-out radius gives
    ``py*sin(t) - px*cos(t) <= slack``, whose (monotone in ``t``) left side
    inverts to ``t <= atan2(px, py) + asin(slack / hypot(px, py))``.
    """
    span = r.sail_span * 0.78  # articulated blades reuse the compact sail span
    tip_y = span * 0.98  # spar box: center at 0.48*span + half length 0.50*span
    tip_x = r.hub_radius * 0.42 - 0.015  # inboard face of the spar box
    hinge_x = _rotor_axis_standoff(r) + r.hub_radius * 0.55

    body_extent = {
        "low_body_tower": r.tower_radius,
        # Square mill body: corner half-diagonal of the 1.58*R box.
        "rugged_tower_with_door": r.tower_radius * 0.79 * math.sqrt(2.0),
        "industrial_guarded_tower": r.tower_radius * 0.84,  # guard rings
        "split_bearing_tower": r.tower_radius * 0.82,
    }[r.support_tower_module]
    keepout = max(
        body_extent,
        _tower_window_face_radius(r) + 0.023,  # louvered upper-window slats
        r.tower_radius * 0.88,  # tower curb ring
        r.cap_width * 0.62,  # cap bed ring, centered on the yaw axis
    )
    plinth_extent, plinth_top = {
        "low_body_tower": (r.tower_radius * 1.38, 0.10),
        "rugged_tower_with_door": (r.tower_radius * 1.30, 0.12),
        "industrial_guarded_tower": (r.tower_radius * 1.15, 0.10),
        "split_bearing_tower": (r.tower_radius * 1.18, 0.10),
    }[r.support_tower_module]
    rotor_z = r.tower_height + 0.070 + r.cap_height * 0.24
    if rotor_z - (r.hub_radius * 1.10 + tip_y) < plinth_top + 0.02:
        keepout = max(keepout, plinth_extent)

    slack = hinge_x - keepout - _FOLD_CLEARANCE
    hyp = math.hypot(tip_x, tip_y)
    if slack >= hyp:
        return _FOLD_LIMIT_MAX
    phase = math.atan2(tip_x, tip_y)
    return _clamp(phase + math.asin(max(slack, 0.0) / hyp), 0.0, _FOLD_LIMIT_MAX)


def _build_cap(model: ArticulatedObject, r: ResolvedTraditionalWindmillConfig) -> _CapInfo:
    cap = model.part("cap")
    skirt_h = 0.070
    rotor_x = _rotor_axis_standoff(r)
    cap.visual(
        Cylinder(radius=r.cap_width * 0.52, length=skirt_h),
        origin=Origin(xyz=(0.0, 0.0, skirt_h * 0.5)),
        material="wood",
        name="cap_skirt", material_class_id="wood.oak",
    )
    cap.visual(
        Cylinder(radius=r.cap_width * 0.62, length=0.022),
        origin=Origin(xyz=(0.0, 0.0, 0.011)),
        material="metal",
        name="cap_bed_ring", material_class_id="metal.cast_iron_bare",
    )
    cap.visual(
        Cylinder(radius=r.tower_radius * 0.20, length=skirt_h * 0.82),
        origin=Origin(xyz=(0.0, 0.0, skirt_h * 0.50)),
        material="metal",
        name="yaw_collar_sleeve", material_class_id="metal.steel_bare",
    )
    cap.visual(
        Box((r.cap_length * 0.62, r.cap_width, r.cap_height * 0.48)),
        origin=Origin(xyz=(r.cap_length * 0.18, 0.0, skirt_h + r.cap_height * 0.24)),
        material="roof",
        name="roofed_cap_shell", material_class_id="stone.slate",
    )
    # Ridge beam sunk 0.02*cap_height (>=3mm) into the roof shell top face
    # (shell tops out at skirt_h + 0.48*cap_height); floating it above leaves a
    # disconnected island inside the cap part.
    cap.visual(
        Box((r.cap_length * 0.46, r.cap_width * 0.22, r.cap_height * 0.16)),
        origin=Origin(xyz=(r.cap_length * 0.02, 0.0, skirt_h + r.cap_height * 0.54)),
        material="wood",
        name="roof_ridge", material_class_id="wood.oak",
    )
    cap.visual(
        Box((r.cap_length * 0.84, 0.028, 0.030)),
        origin=Origin(xyz=(r.cap_length * 0.18, -r.cap_width * 0.42, skirt_h + 0.030)),
        material="wood",
        name="left_cap_sill", material_class_id="wood.oak",
    )
    cap.visual(
        Box((r.cap_length * 0.84, 0.028, 0.030)),
        origin=Origin(xyz=(r.cap_length * 0.18, r.cap_width * 0.42, skirt_h + 0.030)),
        material="wood",
        name="right_cap_sill", material_class_id="wood.oak",
    )
    cap.visual(
        Box((0.036, r.cap_width * 0.78, 0.036)),
        origin=Origin(xyz=(rotor_x - r.cap_length * 0.36, 0.0, skirt_h + 0.040)),
        material="metal",
        name="rear_cross_tie", material_class_id="metal.steel_bare",
    )

    rotor_parent = "cap"
    rotor_origin = (rotor_x, 0.0, skirt_h + r.cap_height * 0.24)
    rotor_parent_visual = "front_bearing_block"
    yaw_type = ArticulationType.CONTINUOUS
    yaw_limits = MotionLimits(effort=28.0, velocity=0.55)

    if r.yaw_cap_head_module == "bounded_service_cap":
        yaw_type = ArticulationType.REVOLUTE
        yaw_limits = MotionLimits(effort=36.0, velocity=0.35, lower=-0.85, upper=0.85)
        cap.visual(
            Box((r.cap_length * 0.38, r.cap_width * 1.08, r.cap_height * 0.30)),
            origin=Origin(xyz=(r.cap_length * 0.28, 0.0, skirt_h + r.cap_height * 0.20)),
            material="wood",
            name="service_cap_cheek", material_class_id="wood.oak",
        )
        cap.visual(
            Box((0.020, r.cap_width * 0.92, r.cap_height * 0.12)),
            origin=Origin(xyz=(-r.cap_length * 0.12, 0.0, skirt_h + r.cap_height * 0.20)),
            material="metal",
            name="yaw_stop_bar", material_class_id="metal.steel_bare",
        )
    elif r.yaw_cap_head_module == "weatherproof_shell_cap":
        cap.visual(
            Box((r.cap_length * 0.82, r.cap_width * 0.92, r.cap_height * 0.22)),
            origin=Origin(xyz=(r.cap_length * 0.12, 0.0, skirt_h + r.cap_height * 0.50)),
            material="roof",
            name="sealed_roof_overhang", material_class_id="stone.slate",
        )
        for i, y in enumerate((-0.36, -0.12, 0.12, 0.36)):
            cap.visual(
                Box((0.018, r.cap_width * 0.11, r.cap_height * 0.22)),
                origin=Origin(
                    xyz=(-r.cap_length * 0.06, y * r.cap_width, skirt_h + r.cap_height * 0.16)
                ),
                material="shadow",
                name=f"side_louver_{i}", material_class_id="metal.paint_coated",
            )
    elif r.yaw_cap_head_module == "split_head_frame":
        head = model.part("head_frame")
        head_len = r.cap_length * 0.30
        mount_w = 0.035
        mount_origin_x = rotor_x - head_len - mount_w * 0.5
        head.visual(
            Box((head_len, r.cap_width * 0.38, r.cap_height * 0.34)),
            origin=Origin(xyz=(head_len * 0.5, 0.0, 0.0)),
            material="wood",
            name="head_frame_block", material_class_id="wood.oak",
        )
        head.visual(
            Cylinder(radius=r.hub_radius * 0.58, length=head_len * 0.72),
            origin=Origin(xyz=(head_len * 0.60, 0.0, 0.0), rpy=_cyl_x()),
            material="metal",
            name="head_shaft_sleeve", material_class_id="metal.steel_bare",
        )
        # Bearing cheeks hug the head_frame_block flanks (block half-width is
        # 0.19*cap_width): centering the 0.026-thick cheek at 0.19*w + 0.008
        # embeds its inner face 5mm into the block for every cap_width, instead
        # of floating off at 0.24*w on wide caps (disconnected island).
        cheek_y = r.cap_width * 0.19 + 0.008
        head.visual(
            Box((head_len * 0.50, 0.026, r.cap_height * 0.46)),
            origin=Origin(xyz=(head_len * 0.62, -cheek_y, 0.0)),
            material="metal",
            name="left_head_bearing_cheek", material_class_id="metal.cast_iron_bare",
        )
        head.visual(
            Box((head_len * 0.50, 0.026, r.cap_height * 0.46)),
            origin=Origin(xyz=(head_len * 0.62, cheek_y, 0.0)),
            material="metal",
            name="right_head_bearing_cheek", material_class_id="metal.cast_iron_bare",
        )
        cap.visual(
            Box((mount_w, r.cap_width * 0.42, r.cap_height * 0.40)),
            origin=Origin(xyz=(mount_origin_x, 0.0, skirt_h + r.cap_height * 0.24)),
            material="wood",
            name="front_head_mount", material_class_id="wood.oak",
        )
        # Deck tying the roof shell forward to the head mount / rear tie so the
        # cap shell is one body (the head mount sits forward of the shell).
        deck_x0 = -r.cap_length * 0.10
        deck_x1 = mount_origin_x + mount_w * 0.5
        cap.visual(
            Box((deck_x1 - deck_x0, r.cap_width * 0.5, 0.045)),
            origin=Origin(xyz=((deck_x0 + deck_x1) * 0.5, 0.0, skirt_h + r.cap_height * 0.24)),
            material="wood",
            name="cap_deck_plate", material_class_id="wood.oak",
        )
        model.articulation(
            "cap_to_head_frame",
            ArticulationType.FIXED,
            parent=cap,
            child=head,
            origin=Origin(xyz=(rotor_x - head_len, 0.0, skirt_h + r.cap_height * 0.24)),
            mating=MatingContract(
                "front_head_mount", "positive_x", "head_frame_block", "negative_x"
            ),
        )
        rotor_parent = "head_frame"
        rotor_origin = (head_len, 0.0, 0.0)
        rotor_parent_visual = "head_frame_block"

    if r.yaw_cap_head_module != "split_head_frame":
        bearing_len = max(0.080, r.cap_length * 0.22)
        rear_bearing_x = max(r.cap_length * 0.05, rotor_x - r.cap_length * 0.36)
        rail_len = max(0.060, rotor_x - rear_bearing_x)
        rail_center_x = (rotor_x + rear_bearing_x) * 0.5
        cap.visual(
            Box((rail_len, 0.026, 0.030)),
            origin=Origin(xyz=(rail_center_x, -r.cap_width * 0.26, skirt_h + r.cap_height * 0.24)),
            material="wood",
            name="left_shaft_rail", material_class_id="wood.oak",
        )
        cap.visual(
            Box((rail_len, 0.026, 0.030)),
            origin=Origin(xyz=(rail_center_x, r.cap_width * 0.26, skirt_h + r.cap_height * 0.24)),
            material="wood",
            name="right_shaft_rail", material_class_id="wood.oak",
        )
        cap.visual(
            Box((bearing_len * 0.78, r.cap_width * 0.32, r.cap_height * 0.30)),
            origin=Origin(xyz=(rear_bearing_x, 0.0, skirt_h + r.cap_height * 0.24)),
            material="wood",
            name="rear_bearing_block", material_class_id="wood.oak",
        )
        cap.visual(
            Cylinder(radius=r.hub_radius * 0.48, length=r.cap_length * 0.14),
            origin=Origin(xyz=(rear_bearing_x, 0.0, skirt_h + r.cap_height * 0.24), rpy=_cyl_x()),
            material="metal",
            name="rear_shaft_bearing", material_class_id="metal.bronze_cast",
        )
        cap.visual(
            Box((bearing_len, r.cap_width * 0.44, r.cap_height * 0.42)),
            origin=Origin(xyz=(rotor_x - bearing_len * 0.5, 0.0, skirt_h + r.cap_height * 0.24)),
            material="wood",
            name="front_bearing_block", material_class_id="wood.oak",
        )
        cap.visual(
            Box((bearing_len * 0.72, 0.026, r.cap_height * 0.48)),
            origin=Origin(
                xyz=(
                    rotor_x - bearing_len * 0.48,
                    -r.cap_width * 0.24,
                    skirt_h + r.cap_height * 0.24,
                )
            ),
            material="metal",
            name="left_front_bearing_cheek", material_class_id="metal.cast_iron_bare",
        )
        cap.visual(
            Box((bearing_len * 0.72, 0.026, r.cap_height * 0.48)),
            origin=Origin(
                xyz=(
                    rotor_x - bearing_len * 0.48,
                    r.cap_width * 0.24,
                    skirt_h + r.cap_height * 0.24,
                )
            ),
            material="metal",
            name="right_front_bearing_cheek", material_class_id="metal.cast_iron_bare",
        )
        cap.visual(
            Cylinder(radius=r.hub_radius * 0.54, length=r.cap_length * 0.18),
            origin=Origin(xyz=(rotor_x, 0.0, skirt_h + r.cap_height * 0.24), rpy=_cyl_x()),
            material="metal",
            name="shaft_bearing", material_class_id="metal.bronze_cast",
        )
        # Deck plate spanning the cap from the shell back-region to the front
        # bearing. When rotor_x is driven by tower clearance the shaft rails sit
        # forward of the roof shell, leaving the shell/skirt floating off the
        # machinery; this ties them into one body across all seeds.
        deck_x0 = -r.cap_length * 0.10
        deck_x1 = rotor_x
        cap.visual(
            Box((deck_x1 - deck_x0, r.cap_width * 0.5, 0.045)),
            origin=Origin(xyz=((deck_x0 + deck_x1) * 0.5, 0.0, skirt_h + r.cap_height * 0.24)),
            material="wood",
            name="cap_deck_plate", material_class_id="wood.oak",
        )

    return _CapInfo(rotor_parent, rotor_origin, rotor_parent_visual, yaw_type, yaw_limits)


def _add_lattice_sail(
    rotor,
    r: ResolvedTraditionalWindmillConfig,
    *,
    angle: float,
    index: int,
    dense: bool,
    compact: bool,
    panel: bool,
) -> None:
    span = r.sail_span * (0.78 if compact else 1.0)
    spar_len = span
    rotor.visual(
        Box((0.030, spar_len, 0.026)),
        origin=_radial_origin(angle, spar_len * 0.48, x=r.hub_radius * 0.42),
        material="wood",
        name=f"sail_spar_{index}", material_class_id="wood.oak",
    )
    rotor.visual(
        Box((0.034, r.hub_radius * 0.78, 0.026)),
        origin=_radial_origin(angle, r.hub_radius * 1.12, x=r.hub_radius * 0.56),
        material="metal",
        name=f"sail_root_clamp_{index}", material_class_id="metal.steel_bare",
    )
    rail_offsets = (-0.055, 0.055) if not dense else (-0.080, 0.0, 0.080)
    for j, offset in enumerate(rail_offsets):
        rotor.visual(
            Box((0.022, span * 0.70, 0.016)),
            origin=Origin(
                xyz=(
                    r.hub_radius * 0.55,
                    math.cos(angle) * span * 0.57 + math.cos(angle + math.pi / 2.0) * offset,
                    math.sin(angle) * span * 0.57 + math.sin(angle + math.pi / 2.0) * offset,
                ),
                rpy=(angle, 0.0, 0.0),
            ),
            material="wood",
            name=f"sail_rail_{index}_{j}", material_class_id="wood.oak",
        )
    # Root batten spanning tangentially across the offset rails and the central
    # spar so the blade is one connected piece (the rails are otherwise offset
    # off the spar and float, especially on the small per-blade folding sails).
    batten_reach = (max(rail_offsets) - min(rail_offsets)) + 0.040
    rotor.visual(
        Box((0.024, 0.030, batten_reach)),
        origin=Origin(
            xyz=(
                r.hub_radius * 0.55,
                math.cos(angle) * span * 0.40,
                math.sin(angle) * span * 0.40,
            ),
            rpy=(angle, 0.0, 0.0),
        ),
        material="wood",
        name=f"sail_root_batten_{index}", material_class_id="wood.oak",
    )
    slat_count = 6 if dense else 4
    if compact:
        slat_count = 3
    for j in range(slat_count):
        radius = span * (0.25 + 0.55 * j / max(1, slat_count - 1))
        rotor.visual(
            Box((0.020, span * (0.18 if not panel else 0.26), 0.014)),
            origin=Origin(
                xyz=(
                    r.hub_radius * 0.62,
                    math.cos(angle) * radius,
                    math.sin(angle) * radius,
                ),
                rpy=(angle + math.pi / 2.0, 0.0, 0.0),
            ),
            material="wood" if not panel else "plaster",
            name=f"sail_cross_slat_{index}_{j}", material_class_id=("wood.oak" if r.sail_rotor_module in {"classic_lattice_sails", "retrofit_dense_rotor", "compact_stow_rotor", "articulated_stow_sails"} else "plaster.smooth"),
        )
    brace_radius = span * 0.52
    rotor.visual(
        Box((0.014, span * 0.58, 0.012)),
        origin=Origin(
            xyz=(
                r.hub_radius * 0.50,
                math.cos(angle) * brace_radius,
                math.sin(angle) * brace_radius,
            ),
            rpy=(angle + 0.20, 0.0, 0.0),
        ),
        material="metal" if dense else "wood",
        name=f"sail_diagonal_tie_{index}", material_class_id=("wood.oak" if r.sail_rotor_module in {"classic_lattice_sails", "compact_stow_rotor", "weatherproof_rotor", "articulated_stow_sails"} else "metal.steel_bare"),
    )
    if compact:
        rotor.visual(
            Cylinder(radius=r.hub_radius * 0.20, length=0.050),
            origin=_radial_origin(angle, r.hub_radius * 1.22, x=r.hub_radius * 0.58),
            material="metal",
            name=f"fold_knuckle_{index}", material_class_id="metal.steel_bare",
        )


def _build_rotor(model: ArticulatedObject, r: ResolvedTraditionalWindmillConfig) -> None:
    rotor = model.part("sail_hub")
    hub_len = r.hub_radius * 1.45
    rotor.visual(
        Cylinder(radius=r.hub_radius * 0.38, length=hub_len * 2.45),
        origin=Origin(xyz=(-hub_len * 0.46, 0.0, 0.0), rpy=_cyl_x()),
        material="metal",
        name="windshaft", material_class_id="metal.cast_iron_bare",
    )
    rotor.visual(
        Cylinder(radius=r.hub_radius * 0.54, length=0.030),
        origin=Origin(xyz=(-hub_len * 0.88, 0.0, 0.0), rpy=_cyl_x()),
        material="metal",
        name="rear_journal", material_class_id="metal.steel_bare",
    )
    rotor.visual(
        Cylinder(radius=r.hub_radius * 0.58, length=0.034),
        origin=Origin(xyz=(-hub_len * 0.12, 0.0, 0.0), rpy=_cyl_x()),
        material="metal",
        name="front_journal", material_class_id="metal.steel_bare",
    )
    rotor.visual(
        Cylinder(radius=r.hub_radius, length=hub_len),
        origin=Origin(xyz=(hub_len * 0.5, 0.0, 0.0), rpy=_cyl_x()),
        material="metal",
        name="hub_barrel", material_class_id="metal.cast_iron_bare",
    )
    rotor.visual(
        Cylinder(radius=r.hub_radius * 1.30, length=0.026),
        origin=Origin(xyz=(hub_len + 0.013, 0.0, 0.0), rpy=_cyl_x()),
        material="metal",
        name="hub_face", material_class_id="metal.cast_iron_bare",
    )
    rotor.visual(
        Sphere(radius=r.hub_radius * 0.52),
        origin=Origin(xyz=(hub_len + r.hub_radius * 0.42, 0.0, 0.0)),
        material="metal",
        name="nose_cap", material_class_id="metal.cast_iron_bare",
    )
    stock_len = r.hub_radius * 2.55
    rotor.visual(
        Box((0.030, stock_len, 0.030)),
        origin=Origin(xyz=(hub_len * 0.78, 0.0, 0.0)),
        material="wood",
        name="horizontal_stock", material_class_id="wood.oak",
    )
    rotor.visual(
        Box((0.030, 0.030, stock_len)),
        origin=Origin(xyz=(hub_len * 0.78, 0.0, 0.0)),
        material="wood",
        name="vertical_stock", material_class_id="wood.oak",
    )
    for i in range(r.sail_count):
        angle = math.tau * i / r.sail_count
        rotor.visual(
            Sphere(radius=r.hub_radius * 0.12),
            origin=Origin(
                xyz=(
                    hub_len + 0.018,
                    math.sin(angle) * r.hub_radius * 0.82,
                    math.cos(angle) * r.hub_radius * 0.82,
                )
            ),
            material="shadow",
            name=f"hub_face_bolt_{i}", material_class_id="metal.steel_bare",
        )
    dense = r.sail_rotor_module == "retrofit_dense_rotor"
    compact = r.sail_rotor_module in {"compact_stow_rotor", "articulated_stow_sails"}
    panel = r.sail_rotor_module == "weatherproof_rotor"
    if r.sail_rotor_module == "articulated_stow_sails":
        hinge_radius = r.hub_radius * 1.10
        fold_upper = _safe_fold_upper(r)
        for i in range(r.sail_count):
            angle = math.tau * i / r.sail_count
            hinge_xyz = (
                r.hub_radius * 0.55,
                math.cos(angle) * hinge_radius,
                math.sin(angle) * hinge_radius,
            )
            rotor.visual(
                Box((0.030, 0.045, 0.035)),
                origin=Origin(xyz=hinge_xyz, rpy=(angle, 0.0, 0.0)),
                material="metal",
                name=f"folding_sail_lug_{i}", material_class_id="metal.steel_bare",
            )
            sail = model.part(f"sail_blade_{i}")
            _add_lattice_sail(
                sail,
                r,
                angle=0.0,
                index=i,
                dense=False,
                compact=True,
                panel=False,
            )
            # Hinge knuckle: radius reaches 7mm past the spar's inboard face at
            # 0.42*hub_radius - 0.015 (a 0.16*hub_radius pin floats for
            # hub_radius > ~0.058, leaving a disconnected island).
            sail.visual(
                Cylinder(
                    radius=max(r.hub_radius * 0.16, r.hub_radius * 0.42 - 0.008),
                    length=0.040,
                ),
                origin=Origin(rpy=_cyl_y()),
                material="metal",
                name="root_hinge_pin", material_class_id="metal.steel_bare",
            )
            model.articulation(
                f"sail_blade_fold_{i}",
                ArticulationType.REVOLUTE,
                parent=rotor,
                child=sail,
                origin=Origin(xyz=hinge_xyz, rpy=(angle, 0.0, 0.0)),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=2.0, velocity=0.8, lower=-0.18, upper=fold_upper),
            )
        return
    for i in range(r.sail_count):
        _add_lattice_sail(
            rotor,
            r,
            angle=math.tau * i / r.sail_count,
            index=i,
            dense=dense,
            compact=compact,
            panel=panel,
        )
    if dense:
        # Retrofit braces run from inside the hub barrel (inner end at
        # 0.5*hub_radius, buried half a hub radius deep) out to 0.61*sail_span;
        # starting them at 0.19*sail_span only touched the barrel by luck on
        # small-span/large-hub seeds and floated otherwise.
        brace_inner = r.hub_radius * 0.50
        brace_outer = r.sail_span * 0.61
        for i in range(r.sail_count):
            rotor.visual(
                Box((0.018, brace_outer - brace_inner, 0.014)),
                origin=_radial_origin(
                    math.tau * (i + 0.5) / r.sail_count,
                    (brace_outer + brace_inner) * 0.5,
                    x=r.hub_radius * 0.46,
                ),
                material="metal",
                name=f"diagonal_retrofit_brace_{i}", material_class_id="metal.steel_bare",
            )
    if panel:
        rotor.visual(
            Cylinder(radius=r.hub_radius * 1.55, length=0.018),
            origin=Origin(xyz=(hub_len + 0.030, 0.0, 0.0), rpy=_cyl_x()),
            material="roof",
            name="weather_seal_ring", material_class_id="rubber.smooth_plain",
        )


def _build_service_accessory(
    model: ArticulatedObject,
    r: ResolvedTraditionalWindmillConfig,
    support: _SupportInfo,
    cap: _CapInfo,
) -> None:
    if r.service_accessory_module == "none":
        return
    if r.service_accessory_module in {"access_door", "access_door_and_brake_lever"}:
        tower = model.get_part("tower")
        socket_y = -r.tower_radius * 0.82
        socket_x = -r.tower_radius * 0.30
        socket_z = r.tower_height * 0.19
        tower.visual(
            Cylinder(radius=0.014, length=r.tower_height * 0.28),
            origin=Origin(xyz=(socket_x, socket_y, socket_z + r.tower_height * 0.14)),
            material="metal",
            name="access_door_socket", material_class_id="metal.cast_iron_bare",
        )
        door = model.part("access_door")
        door_h = r.tower_height * 0.30
        door.visual(
            Cylinder(radius=0.014, length=door_h),
            origin=Origin(xyz=(0.0, 0.0, door_h * 0.5)),
            material="metal",
            name="door_hinge_barrel", material_class_id="metal.steel_bare",
        )
        door.visual(
            Box((r.tower_radius * 0.42, 0.030, door_h * 0.94)),
            origin=Origin(xyz=(r.tower_radius * 0.21, 0.0, door_h * 0.50)),
            material="wood",
            name="door_leaf", material_class_id="wood.oak",
        )
        model.articulation(
            "tower_to_access_door",
            ArticulationType.REVOLUTE,
            parent=tower,
            child=door,
            origin=Origin(xyz=(socket_x, socket_y, socket_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=4.0, velocity=0.7, lower=0.0, upper=1.45),
        )
        if r.service_accessory_module == "access_door":
            return
    if r.service_accessory_module in {"brake_lever", "access_door_and_brake_lever"}:
        parent = model.get_part(cap.rotor_parent)
        parent.visual(
            Box((0.045, 0.030, 0.040)),
            origin=Origin(
                xyz=(cap.rotor_origin[0] * 0.78, -r.cap_width * 0.42, cap.rotor_origin[2])
            ),
            material="metal",
            name="brake_pivot_socket", material_class_id="metal.cast_iron_bare",
        )
        # Strut tying the pivot socket inboard to the parent body (the socket sits
        # out at the cap edge and floats off a narrow split-head frame).
        parent.visual(
            Box((0.024, r.cap_width * 0.42, 0.024)),
            origin=Origin(
                xyz=(cap.rotor_origin[0] * 0.78, -r.cap_width * 0.21, cap.rotor_origin[2])
            ),
            material="metal",
            name="brake_pivot_strut", material_class_id="metal.steel_bare",
        )
        lever = model.part("brake_lever")
        lever.visual(
            Cylinder(radius=0.014, length=0.045),
            origin=Origin(rpy=_cyl_y()),
            material="metal",
            name="brake_hinge_pin", material_class_id="metal.steel_bare",
        )
        lever.visual(
            Box((0.026, r.cap_width * 0.70, 0.026)),
            origin=Origin(xyz=(0.0, -r.cap_width * 0.34, 0.0)),
            material="wood",
            name="brake_handle", material_class_id="wood.oak",
        )
        model.articulation(
            "cap_to_brake_lever",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=lever,
            origin=Origin(
                xyz=(cap.rotor_origin[0] * 0.78, -r.cap_width * 0.42, cap.rotor_origin[2])
            ),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=3.5, velocity=0.55, lower=-0.65, upper=0.35),
        )
        return
    elif r.service_accessory_module == "lockout_lever":
        parent = model.get_part(cap.rotor_parent)
        parent.visual(
            Box((0.034, 0.050, 0.038)),
            origin=Origin(
                xyz=(cap.rotor_origin[0] * 0.68, r.cap_width * 0.42, cap.rotor_origin[2])
            ),
            material="metal",
            name="lockout_socket", material_class_id="metal.cast_iron_bare",
        )
        # Strut tying the lockout socket inboard to the parent body.
        parent.visual(
            Box((0.024, r.cap_width * 0.42, 0.024)),
            origin=Origin(
                xyz=(cap.rotor_origin[0] * 0.68, r.cap_width * 0.21, cap.rotor_origin[2])
            ),
            material="metal",
            name="lockout_strut", material_class_id="metal.steel_bare",
        )
        lock = model.part("lockout_lever")
        lock.visual(
            Cylinder(radius=0.013, length=0.050),
            origin=Origin(rpy=_cyl_y()),
            material="metal",
            name="lockout_pin", material_class_id="metal.steel_bare",
        )
        lock.visual(
            Box((0.024, 0.038, r.cap_height * 0.72)),
            origin=Origin(xyz=(0.0, 0.0, -r.cap_height * 0.32)),
            material="wood",
            name="lockout_drop_handle", material_class_id="wood.oak",
        )
        model.articulation(
            "cap_to_lockout_lever",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=lock,
            origin=Origin(
                xyz=(cap.rotor_origin[0] * 0.68, r.cap_width * 0.42, cap.rotor_origin[2])
            ),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=0.45, lower=-0.30, upper=0.95),
        )
    else:
        parent = model.get_part("cap")
        parent.visual(
            Box((0.030, 0.026, r.cap_height * 0.50)),
            origin=Origin(xyz=(r.cap_length * 0.10, -r.cap_width * 0.51, r.cap_height * 0.35)),
            material="metal",
            name="side_hatch_hinge_socket", material_class_id="metal.cast_iron_bare",
        )
        hatch = model.part("side_hatch")
        hatch.visual(
            Cylinder(radius=0.012, length=r.cap_height * 0.45),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material="metal",
            name="hatch_hinge_barrel", material_class_id="metal.steel_bare",
        )
        hatch.visual(
            Box((r.cap_length * 0.24, 0.026, r.cap_height * 0.42)),
            origin=Origin(xyz=(r.cap_length * 0.12, 0.0, 0.0)),
            material="wood",
            name="hatch_panel", material_class_id="wood.oak",
        )
        model.articulation(
            "cap_to_side_hatch",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=hatch,
            origin=Origin(xyz=(r.cap_length * 0.10, -r.cap_width * 0.51, r.cap_height * 0.35)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.5, velocity=0.6, lower=0.0, upper=1.25),
        )


def build_traditional_windmill(
    config: TraditionalWindmillConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="traditional_windmill", assets=assets)
    for name, rgba in r.palette.items():
        model.material(name, rgba=rgba)

    support = _build_support(model, r)
    cap_info = _build_cap(model, r)
    _build_rotor(model, r)

    yaw_parent = model.get_part(support.yaw_parent)
    cap = model.get_part("cap")
    model.articulation(
        "tower_to_cap",
        cap_info.yaw_joint_type,
        parent=yaw_parent,
        child=cap,
        origin=Origin(xyz=support.yaw_origin),
        axis=(0.0, 0.0, 1.0),
        motion_limits=cap_info.yaw_limits,
        mating=MatingContract(support.yaw_parent_visual, "positive_z", "cap_skirt", "negative_z"),
    )

    rotor_parent = model.get_part(cap_info.rotor_parent)
    rotor = model.get_part("sail_hub")
    model.articulation(
        "cap_to_sail_hub",
        ArticulationType.CONTINUOUS,
        parent=rotor_parent,
        child=rotor,
        origin=Origin(xyz=cap_info.rotor_origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=14.0, velocity=7.5),
        mating=MatingContract(
            cap_info.rotor_parent_visual, "positive_x", "hub_barrel", "negative_x"
        ),
    )
    _build_service_accessory(model, r, support, cap_info)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_traditional_windmill(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_traditional_windmill(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedTraditionalWindmillConfig) -> list[tuple[str, str]]:
    return [
        ("support_tower", r.support_tower_module),
        ("yaw_cap_head", r.yaw_cap_head_module),
        ("sail_rotor", r.sail_rotor_module),
        ("service_accessory", r.service_accessory_module),
        ("sail_multiplicity", f"{r.sail_count}_sails"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def run_traditional_windmill_tests(
    object_model: ArticulatedObject, config: TraditionalWindmillConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    names = {p.name for p in object_model.parts}
    joints = {j.name: j for j in object_model.articulations}
    ctx.check("tower_present", "tower" in names)
    ctx.check("cap_present", "cap" in names)
    ctx.check("sail_hub_present", "sail_hub" in names)
    ctx.check("yaw_joint_present", "tower_to_cap" in joints)
    ctx.check("rotor_joint_present", "cap_to_sail_hub" in joints)
    ctx.check("yaw_axis_vertical", joints["tower_to_cap"].axis == (0.0, 0.0, 1.0))
    ctx.check("rotor_axis_horizontal", joints["cap_to_sail_hub"].axis == (1.0, 0.0, 0.0))
    ctx.check(
        "rotor_continuous_spin",
        joints["cap_to_sail_hub"].articulation_type == ArticulationType.CONTINUOUS,
    )
    sail_visuals = [
        v.name
        for part in object_model.parts
        for v in part.visuals
        if v.name.startswith("sail_spar_")
    ]
    ctx.check("sail_count_matches_config", len(sail_visuals) == r.sail_count)
    if r.service_accessory_module != "none":
        expected_parts = {
            "access_door": {"access_door"},
            "brake_lever": {"brake_lever"},
            "access_door_and_brake_lever": {"access_door", "brake_lever"},
            "lockout_lever": {"lockout_lever"},
            "side_hatch": {"side_hatch"},
        }[r.service_accessory_module]
        ctx.check("service_part_present", expected_parts <= names)

    for a, b in (
        ("tower", "bearing_module"),
        ("tower", "cap"),
        ("bearing_module", "cap"),
        ("cap", "head_frame"),
        ("cap", "sail_hub"),
        ("head_frame", "sail_hub"),
        ("sail_hub", "sail_blade_0"),
        ("sail_hub", "sail_blade_1"),
        ("sail_hub", "sail_blade_2"),
        ("sail_hub", "sail_blade_3"),
        ("sail_hub", "sail_blade_4"),
        ("sail_hub", "sail_blade_5"),
        ("sail_hub", "sail_blade_6"),
        ("sail_hub", "sail_blade_7"),
        ("tower", "access_door"),
        ("tower", "brake_lever"),
        ("tower", "lockout_lever"),
        ("tower", "side_hatch"),
        ("cap", "brake_lever"),
        ("head_frame", "brake_lever"),
        ("cap", "lockout_lever"),
        ("head_frame", "lockout_lever"),
        ("cap", "side_hatch"),
    ):
        if a in names and b in names:
            ctx.allow_overlap(
                object_model.get_part(a),
                object_model.get_part(b),
                reason="Captured hinge, yaw bearing, or shaft hardware intentionally overlaps at the mechanical interface.",
            )
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry()
    ctx.fail_if_joint_mating_has_gap()
    return ctx.report()


__all__ = [
    "__modular__",
    "TraditionalWindmillConfig",
    "ResolvedTraditionalWindmillConfig",
    "config_from_seed",
    "resolve_config",
    "build_traditional_windmill",
    "build_seeded_traditional_windmill",
    "slot_choices_for_seed",
    "run_traditional_windmill_tests",
]
