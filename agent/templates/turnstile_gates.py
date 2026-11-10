# SPDX-License-Identifier: Apache-2.0

"""Turnstile gates procedural template.

This module implements ``articraft_template_authoring/specs_modular_v1/turnstile_gates.md``.

Identity invariant
-------------------
Every seed is an access-control turnstile lane: a fixed ground-mounted
support (``frame``) carries a single central ``rotor`` that spins about the
vertical world axis ``(0, 0, 1)`` and bears ``arm_count`` evenly-spaced radial
barrier arms. The default/seed-0 object is the canonical three-arm tripod
turnstile with an unbounded CONTINUOUS rotor.

The spec lists a review-gated ``dual_cabinet_glass`` / ``dual_swing_glass``
alternate whose motion spine (two opposing REVOLUTE glass leaves, no central
rotor) is incompatible with the central radial turnstile. Per the spec's own
guidance ("the default template should likely seed central rotor; the dual
swing gate branch should be either split or heavily gated after review") and
the workflow rule that ``config_from_seed`` must only sample a stable
subdomain, this template intentionally implements **only the central-rotor
family**. The swing-glass lane belongs in a separate slug
(``turnstile_gates_swing_lane``) and is not sampled here.

Slot graph (spec ``pattern = mixed``)
-------------------------------------
* Slot A ``fixed_support_lane`` -> the static ``frame`` root (pedestal, central
  post, bearing stack, optional service cabinet / split-head modules). All
  non-articulating structure is fused as ``frame.visual(...)`` per Rule 1.
* Slot B ``barrier_mechanism`` -> the ``rotor`` part (central hub + radial arms)
  joined to the frame by ``rotor_spin`` (CONTINUOUS or limited REVOLUTE about
  ``(0, 0, 1)``).
* Slot C ``service_and_locking`` -> optional ``service_panel`` /
  ``inspection_hatch`` REVOLUTE leaves on a frame cabinet, or a
  ``lockout_pawl`` REVOLUTE safety pawl, or extra fixed bearing visuals.

Geometry policy
---------------
The rotor mounts on the frame bearing top with a shallow vertical embed (a few
millimetres) so the parts read as connected without tripping the rest-pose
overlap baseline. All radial arms sweep in free space above every frame
structure (frame structure stays below the arm plane or inside the hub
radius), so the rotor never collides with the support. Hinge barrels and the
pawl pivot are captured features with explicit ``allow_overlap`` allowances,
mirroring the 5-star samples.

Adopted source mapping
----------------------
S1 rec_turnstile_gates_0002: rugged base frame, rotor assembly, service-panel
   vertical hinge + inspection-hatch horizontal hinge.
S2 rec_turnstile_gates_0003: refined frame + central post + bearing pads +
   three-arm CONTINUOUS rotor (seed-0 reference topology).
S3 rec_turnstile_gates_263530aa5ac54fec861233a7d86aa8c4: service base,
   bearing_core, stacked wear rings, fixed bearing service stack.
S4 rec_turnstile_gates_76346937a9f345e2b518432844044a83: split bearing module
   + fixed frame + head modules + arm hub topology.
S5 rec_turnstile_gates_7b8754ba455e44da91b04ad418caad73: industrial safety
   frame, radial rotor, lockout pawl REVOLUTE with captured pivot.
S6 rec_turnstile_gates_e615c706540b431592c7295a69ffa83e: dual cabinet swing
   gate alternate (read, intentionally split out — not implemented here).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    Part,
    Sphere,
    TestContext,
    TestReport,
)

__modular__ = True


# --------------------------------------------------------------------------- #
# Enum domains (central-rotor subdomain only)
# --------------------------------------------------------------------------- #

LaneStyle = Literal[
    "refined_frame",
    "rugged_base",
    "service_bearing",
    "split_head",
]
BarrierStyle = Literal[
    "three_arm_rotor",
    "rugged_rotor",
    "bearing_hub",
    "modular_arm_hub",
]
ServiceModule = Literal[
    "none",
    "service_panel_and_hatch",
    "fixed_bearing_stack",
    "lockout_pawl",
]
ArmStyle = Literal[
    "round_tube",
    "flat_bar",
    "paddle",
    "capsule_rail",
]
RotorJointType = Literal[
    "continuous",
    "limited_revolute",
]
MaterialStyle = Literal[
    "satin_steel",
    "anthracite",
    "industrial_safety",
    "warm_brass",
    "midnight",
]


LANE_STYLES: tuple[LaneStyle, ...] = (
    "refined_frame",
    "rugged_base",
    "service_bearing",
    "split_head",
)
BARRIER_STYLES: tuple[BarrierStyle, ...] = (
    "three_arm_rotor",
    "rugged_rotor",
    "bearing_hub",
    "modular_arm_hub",
)
SERVICE_MODULES: tuple[ServiceModule, ...] = (
    "none",
    "service_panel_and_hatch",
    "fixed_bearing_stack",
    "lockout_pawl",
)
ARM_STYLES: tuple[ArmStyle, ...] = (
    "round_tube",
    "flat_bar",
    "paddle",
    "capsule_rail",
)
ROTOR_JOINT_TYPES: tuple[RotorJointType, ...] = (
    "continuous",
    "limited_revolute",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "satin_steel",
    "anthracite",
    "industrial_safety",
    "warm_brass",
    "midnight",
)


SOURCE_INDEX = {
    "S1": (
        "data/records/rec_turnstile_gates_0002/revisions/rev_000001/model.py:L92-L225,L293-L536"
    ),
    "S2": ("data/records/rec_turnstile_gates_0003/revisions/rev_000001/model.py:L54-L346"),
    "S3": (
        "data/records/rec_turnstile_gates_263530aa5ac54fec861233a7d86aa8c4/"
        "revisions/rev_000001/model.py:L47-L382"
    ),
    "S4": (
        "data/records/rec_turnstile_gates_76346937a9f345e2b518432844044a83/"
        "revisions/rev_000001/model.py:L30-L247"
    ),
    "S5": (
        "data/records/rec_turnstile_gates_7b8754ba455e44da91b04ad418caad73/"
        "revisions/rev_000001/model.py:L22-L57,L364-L409"
    ),
    "S6": (
        "data/records/rec_turnstile_gates_e615c706540b431592c7295a69ffa83e/"
        "revisions/rev_000001/model.py:L39-L211"
    ),
}


# --------------------------------------------------------------------------- #
# Palettes
# --------------------------------------------------------------------------- #

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "satin_steel": {
        "frame": (0.62, 0.64, 0.67, 1.0),
        "frame_dark": (0.34, 0.36, 0.39, 1.0),
        "column": (0.46, 0.48, 0.51, 1.0),
        "bearing": (0.40, 0.42, 0.45, 1.0),
        "bearing_bright": (0.80, 0.82, 0.85, 1.0),
        "hub": (0.50, 0.52, 0.55, 1.0),
        "arm": (0.78, 0.80, 0.83, 1.0),
        "arm_tip": (0.10, 0.10, 0.11, 1.0),
        "hardware": (0.30, 0.31, 0.33, 1.0),
        "accent": (0.18, 0.46, 0.74, 1.0),
        "ratchet": (0.28, 0.29, 0.31, 1.0),
    },
    "anthracite": {
        "frame": (0.18, 0.19, 0.21, 1.0),
        "frame_dark": (0.10, 0.10, 0.12, 1.0),
        "column": (0.22, 0.23, 0.25, 1.0),
        "bearing": (0.27, 0.28, 0.30, 1.0),
        "bearing_bright": (0.66, 0.68, 0.71, 1.0),
        "hub": (0.24, 0.25, 0.27, 1.0),
        "arm": (0.70, 0.72, 0.75, 1.0),
        "arm_tip": (0.06, 0.06, 0.07, 1.0),
        "hardware": (0.40, 0.41, 0.43, 1.0),
        "accent": (0.84, 0.62, 0.12, 1.0),
        "ratchet": (0.16, 0.16, 0.18, 1.0),
    },
    "industrial_safety": {
        "frame": (0.86, 0.62, 0.08, 1.0),
        "frame_dark": (0.32, 0.22, 0.03, 1.0),
        "column": (0.20, 0.21, 0.22, 1.0),
        "bearing": (0.30, 0.31, 0.33, 1.0),
        "bearing_bright": (0.78, 0.80, 0.82, 1.0),
        "hub": (0.24, 0.25, 0.26, 1.0),
        "arm": (0.90, 0.66, 0.10, 1.0),
        "arm_tip": (0.08, 0.08, 0.09, 1.0),
        "hardware": (0.18, 0.18, 0.19, 1.0),
        "accent": (0.86, 0.12, 0.10, 1.0),
        "ratchet": (0.14, 0.14, 0.15, 1.0),
    },
    "warm_brass": {
        "frame": (0.52, 0.40, 0.18, 1.0),
        "frame_dark": (0.24, 0.18, 0.07, 1.0),
        "column": (0.58, 0.45, 0.20, 1.0),
        "bearing": (0.46, 0.36, 0.16, 1.0),
        "bearing_bright": (0.86, 0.72, 0.36, 1.0),
        "hub": (0.62, 0.48, 0.22, 1.0),
        "arm": (0.80, 0.66, 0.30, 1.0),
        "arm_tip": (0.16, 0.12, 0.05, 1.0),
        "hardware": (0.36, 0.28, 0.12, 1.0),
        "accent": (0.20, 0.30, 0.42, 1.0),
        "ratchet": (0.30, 0.23, 0.10, 1.0),
    },
    "midnight": {
        "frame": (0.10, 0.12, 0.20, 1.0),
        "frame_dark": (0.05, 0.06, 0.11, 1.0),
        "column": (0.14, 0.16, 0.26, 1.0),
        "bearing": (0.18, 0.20, 0.30, 1.0),
        "bearing_bright": (0.58, 0.62, 0.78, 1.0),
        "hub": (0.16, 0.18, 0.28, 1.0),
        "arm": (0.62, 0.66, 0.82, 1.0),
        "arm_tip": (0.04, 0.05, 0.08, 1.0),
        "hardware": (0.34, 0.36, 0.46, 1.0),
        "accent": (0.32, 0.70, 0.86, 1.0),
        "ratchet": (0.12, 0.13, 0.20, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class TurnstileGatesConfig:
    lane_style: LaneStyle = "refined_frame"
    barrier_style: BarrierStyle = "three_arm_rotor"
    service_module: ServiceModule = "none"
    arm_style: ArmStyle = "round_tube"
    rotor_joint_type: RotorJointType = "continuous"
    material_style: MaterialStyle = "satin_steel"
    arm_count: int = 3
    rotor_height: float = 0.90
    lane_width: float = 1.05
    panel_open_angle: float = 1.30
    hatch_open_angle: float = 1.15
    pawl_engage_angle: float = 0.65
    name: str = "reference_turnstile_gates"
    palette: dict[str, tuple[float, float, float, float]] | None = None


@dataclass(frozen=True)
class ResolvedTurnstileGatesConfig:
    lane_style: LaneStyle
    barrier_style: BarrierStyle
    service_module: ServiceModule
    arm_style: ArmStyle
    rotor_joint_type: RotorJointType
    material_style: MaterialStyle
    arm_count: int
    rotor_height: float
    lane_width: float
    panel_open_angle: float
    hatch_open_angle: float
    pawl_engage_angle: float
    # derived geometry
    base_h: float
    base_radius: float
    post_radius: float
    hub_radius: float
    bearing_radius: float
    bearing_top_z: float
    arm_inner_r: float
    arm_tip_r: float
    arm_radius: float
    arm_z: float
    cab_w: float
    cab_d: float
    cab_h: float
    cab_cx: float
    head_h: float
    head_w: float
    head_offset: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _require(value: str, allowed: tuple[str, ...], *, field_name: str) -> str:
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of {allowed}, got {value!r}")
    return value


def _radial_xy(radius: float, angle: float) -> tuple[float, float]:
    return (math.cos(angle) * radius, math.sin(angle) * radius)


def _radial_cyl_rpy(angle: float) -> tuple[float, float, float]:
    """RPY that lays a +Z cylinder horizontal, pointing along ``angle`` in XY."""
    return (0.0, math.pi / 2.0, angle)


def _y_cyl_rpy() -> tuple[float, float, float]:
    return (math.pi / 2.0, 0.0, 0.0)


def _register_materials(
    model: ArticulatedObject,
    palette: dict[str, tuple[float, float, float, float]],
) -> dict[str, object]:
    return {name: model.material(f"turnstile_{name}", rgba=rgba) for name, rgba in palette.items()}


def _arm_angles(count: int) -> list[float]:
    return [2.0 * math.pi * i / count for i in range(count)]


# --------------------------------------------------------------------------- #
# config_from_seed
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> TurnstileGatesConfig:
    curated: dict[int, TurnstileGatesConfig] = {
        0: TurnstileGatesConfig(
            lane_style="refined_frame",
            barrier_style="three_arm_rotor",
            service_module="none",
            arm_style="round_tube",
            rotor_joint_type="continuous",
            material_style="satin_steel",
            arm_count=3,
            rotor_height=0.90,
            lane_width=1.05,
            name="seeded_turnstile_gates_0",
        ),
        1: TurnstileGatesConfig(
            lane_style="rugged_base",
            barrier_style="rugged_rotor",
            service_module="service_panel_and_hatch",
            arm_style="flat_bar",
            rotor_joint_type="continuous",
            material_style="anthracite",
            arm_count=4,
            rotor_height=0.98,
            lane_width=1.22,
            name="seeded_turnstile_gates_1",
        ),
        2: TurnstileGatesConfig(
            lane_style="service_bearing",
            barrier_style="bearing_hub",
            service_module="fixed_bearing_stack",
            arm_style="paddle",
            rotor_joint_type="continuous",
            material_style="industrial_safety",
            arm_count=3,
            rotor_height=0.86,
            lane_width=1.10,
            name="seeded_turnstile_gates_2",
        ),
        3: TurnstileGatesConfig(
            lane_style="split_head",
            barrier_style="modular_arm_hub",
            service_module="none",
            arm_style="capsule_rail",
            rotor_joint_type="continuous",
            material_style="warm_brass",
            arm_count=4,
            rotor_height=1.02,
            lane_width=1.34,
            name="seeded_turnstile_gates_3",
        ),
        4: TurnstileGatesConfig(
            lane_style="refined_frame",
            barrier_style="three_arm_rotor",
            service_module="lockout_pawl",
            arm_style="round_tube",
            rotor_joint_type="limited_revolute",
            material_style="midnight",
            arm_count=3,
            rotor_height=0.92,
            lane_width=1.00,
            name="seeded_turnstile_gates_4",
        ),
        5: TurnstileGatesConfig(
            lane_style="rugged_base",
            barrier_style="bearing_hub",
            service_module="service_panel_and_hatch",
            arm_style="paddle",
            rotor_joint_type="continuous",
            material_style="satin_steel",
            arm_count=4,
            rotor_height=0.88,
            lane_width=1.28,
            name="seeded_turnstile_gates_5",
        ),
        6: TurnstileGatesConfig(
            lane_style="service_bearing",
            barrier_style="rugged_rotor",
            service_module="lockout_pawl",
            arm_style="flat_bar",
            rotor_joint_type="limited_revolute",
            material_style="anthracite",
            arm_count=3,
            rotor_height=0.95,
            lane_width=1.16,
            name="seeded_turnstile_gates_6",
        ),
        7: TurnstileGatesConfig(
            lane_style="split_head",
            barrier_style="three_arm_rotor",
            service_module="fixed_bearing_stack",
            arm_style="round_tube",
            rotor_joint_type="continuous",
            material_style="industrial_safety",
            arm_count=4,
            rotor_height=1.05,
            lane_width=1.40,
            name="seeded_turnstile_gates_7",
        ),
        8: TurnstileGatesConfig(
            lane_style="refined_frame",
            barrier_style="modular_arm_hub",
            service_module="service_panel_and_hatch",
            arm_style="capsule_rail",
            rotor_joint_type="continuous",
            material_style="warm_brass",
            arm_count=3,
            rotor_height=0.84,
            lane_width=0.96,
            name="seeded_turnstile_gates_8",
        ),
        9: TurnstileGatesConfig(
            lane_style="rugged_base",
            barrier_style="bearing_hub",
            service_module="none",
            arm_style="flat_bar",
            rotor_joint_type="continuous",
            material_style="midnight",
            arm_count=4,
            rotor_height=1.00,
            lane_width=1.30,
            name="seeded_turnstile_gates_9",
        ),
    }
    if seed in curated:
        return curated[seed]

    rng = random.Random(seed)
    lane = rng.choice(LANE_STYLES)
    barrier = rng.choice(BARRIER_STYLES)
    service = rng.choice(SERVICE_MODULES)
    arm_style = rng.choice(ARM_STYLES)
    rotor_joint = rng.choice(ROTOR_JOINT_TYPES)
    material = rng.choice(MATERIAL_STYLES)
    arm_count = rng.choice((3, 4))

    return TurnstileGatesConfig(
        lane_style=lane,
        barrier_style=barrier,
        service_module=service,
        arm_style=arm_style,
        rotor_joint_type=rotor_joint,
        material_style=material,
        arm_count=arm_count,
        rotor_height=round(rng.uniform(0.62, 1.30), 3),
        lane_width=round(rng.uniform(0.80, 1.55), 3),
        panel_open_angle=round(rng.uniform(1.05, 1.40), 3),
        hatch_open_angle=round(rng.uniform(0.95, 1.20), 3),
        pawl_engage_angle=round(rng.uniform(0.45, 0.78), 3),
        name=f"seeded_turnstile_gates_{seed}",
    )


# --------------------------------------------------------------------------- #
# resolve_config
# --------------------------------------------------------------------------- #


def resolve_config(config: TurnstileGatesConfig) -> ResolvedTurnstileGatesConfig:
    lane = _require(config.lane_style, LANE_STYLES, field_name="lane_style")
    barrier = _require(config.barrier_style, BARRIER_STYLES, field_name="barrier_style")
    service = _require(config.service_module, SERVICE_MODULES, field_name="service_module")
    arm_style = _require(config.arm_style, ARM_STYLES, field_name="arm_style")
    rotor_joint = _require(
        config.rotor_joint_type, ROTOR_JOINT_TYPES, field_name="rotor_joint_type"
    )
    material = _require(config.material_style, MATERIAL_STYLES, field_name="material_style")

    arm_count = int(config.arm_count)
    if arm_count not in (3, 4):
        arm_count = 3

    W = _clamp(config.lane_width, 0.75, 1.60)
    H = _clamp(config.rotor_height, 0.55, 1.35)

    base_h = 0.13 if lane == "rugged_base" else 0.10
    base_radius = _clamp(0.15 + 0.045 * W, 0.16, 0.27)
    post_radius = _clamp(0.045 + 0.012 * W, 0.045, 0.072)
    hub_radius = _clamp(0.058 + 0.018 * W, 0.062, 0.098)
    if barrier == "rugged_rotor":
        hub_radius = _clamp(hub_radius * 1.18, 0.062, 0.115)
    bearing_radius = hub_radius * 1.28

    arm_inner_r = hub_radius + 0.014
    arm_tip_r = _clamp(0.30 + 0.16 * W, 0.34, 0.58)
    arm_tip_r = max(arm_tip_r, arm_inner_r + 0.13)

    arm_radius = _clamp(0.016 + 0.005 * W, 0.016, 0.026)
    if barrier == "rugged_rotor":
        arm_radius = _clamp(arm_radius * 1.4, 0.016, 0.038)
    arm_z = 0.040  # local on rotor, above the hub seat

    bearing_top_z = H

    cab_w = _clamp(0.22 + 0.05 * W, 0.22, 0.30)
    cab_d = _clamp(0.28 + 0.10 * W, 0.30, 0.44)
    cab_h = _clamp(0.42 * H, 0.24, 0.54)
    cab_cx = post_radius + 0.055 + cab_w * 0.5

    head_h = _clamp(0.46 * H, 0.26, 0.58)
    head_w = _clamp(0.14 + 0.04 * W, 0.15, 0.22)
    head_offset = base_radius + head_w * 0.5 - 0.03

    palette = dict(PALETTES[material])
    if config.palette:
        palette.update(config.palette)

    return ResolvedTurnstileGatesConfig(
        lane_style=lane,  # type: ignore[arg-type]
        barrier_style=barrier,  # type: ignore[arg-type]
        service_module=service,  # type: ignore[arg-type]
        arm_style=arm_style,  # type: ignore[arg-type]
        rotor_joint_type=rotor_joint,  # type: ignore[arg-type]
        material_style=material,  # type: ignore[arg-type]
        arm_count=arm_count,
        rotor_height=H,
        lane_width=W,
        panel_open_angle=_clamp(config.panel_open_angle, 0.80, 1.45),
        hatch_open_angle=_clamp(config.hatch_open_angle, 0.70, 1.25),
        pawl_engage_angle=_clamp(config.pawl_engage_angle, 0.30, 0.80),
        base_h=base_h,
        base_radius=base_radius,
        post_radius=post_radius,
        hub_radius=hub_radius,
        bearing_radius=bearing_radius,
        bearing_top_z=bearing_top_z,
        arm_inner_r=arm_inner_r,
        arm_tip_r=arm_tip_r,
        arm_radius=arm_radius,
        arm_z=arm_z,
        cab_w=cab_w,
        cab_d=cab_d,
        cab_h=cab_h,
        cab_cx=cab_cx,
        head_h=head_h,
        head_w=head_w,
        head_offset=head_offset,
        name=config.name,
        palette=palette,
    )


# --------------------------------------------------------------------------- #
# Frame builders (Slot A) — all fused as visuals on the single `frame` part.
# --------------------------------------------------------------------------- #


# adopted: S2
def _build_frame_core(frame: Part, r: ResolvedTurnstileGatesConfig, m: dict) -> None:
    """Central pedestal + post + bearing stack shared by every lane style.

    Adapted from S2 (rec_turnstile_gates_0003) ``central_post`` /
    ``lower_bearing`` / ``upper_bearing`` stack: a vertical column rising from a
    ground pedestal to a bearing seat at ``bearing_top_z`` where the rotor sits.
    """
    base_top = r.base_h
    # Ground pedestal foot.
    frame.visual(
        Cylinder(radius=r.base_radius, length=r.base_h),
        origin=Origin(xyz=(0.0, 0.0, r.base_h * 0.5)),
        material=m["frame"],
        name="base_plinth", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "warm_brass"} else "metal.paint_coated"),
    )
    frame.visual(
        Cylinder(radius=r.base_radius * 0.86, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, r.base_h + 0.006)),
        material=m["frame_dark"],
        name="base_collar", material_class_id=("metal.paint_coated" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
    )
    # Central vertical post up to the bearing seat.
    post_len = r.bearing_top_z - base_top - 0.02
    frame.visual(
        Cylinder(radius=r.post_radius, length=post_len),
        origin=Origin(xyz=(0.0, 0.0, base_top + post_len * 0.5)),
        material=m["column"],
        name="central_post", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "warm_brass"} else "metal.paint_coated"),
    )
    # Bearing housing: a stacked thrust collar just below the rotor seat.
    frame.visual(
        Cylinder(radius=r.bearing_radius, length=0.05),
        origin=Origin(xyz=(0.0, 0.0, r.bearing_top_z - 0.034)),
        material=m["bearing"],
        name="lower_bearing_body", material_class_id=("metal.steel_bare" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
    )
    # Thrust pad whose top sits ~2 mm below the rotor seat; the rotor's lower
    # thrust face embeds ~3 mm into it (depth < 5 mm overlap tol -> connected,
    # not flagged).
    frame.visual(
        Cylinder(radius=r.bearing_radius * 0.55, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, r.bearing_top_z - 0.008)),
        material=m["bearing_bright"],
        name="bearing_pad", material_class_id=("metal.chrome_polished" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_polished"),
    )
    frame.visual(
        Cylinder(radius=r.post_radius * 0.7, length=0.03),
        origin=Origin(xyz=(0.0, 0.0, r.bearing_top_z - 0.052)),
        material=m["hardware"],
        name="bearing_shaft", material_class_id="metal.steel_bare",
    )


# adopted: S2
def _decorate_refined_frame(frame: Part, r: ResolvedTurnstileGatesConfig, m: dict) -> None:
    """Slim reader head + a low service fascia on the pedestal (S2 fascia)."""
    head_z = r.base_h + r.cab_h * 0.5
    frame.visual(
        Box((r.cab_w * 0.9, r.cab_d * 0.7, r.cab_h)),
        origin=Origin(xyz=(r.cab_cx, 0.0, r.base_h + r.cab_h * 0.5)),
        material=m["frame"],
        name="reader_head", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "warm_brass"} else "metal.paint_coated"),
    )
    frame.visual(
        Box((0.012, r.cab_d * 0.42, r.cab_h * 0.5)),
        origin=Origin(xyz=(r.cab_cx - r.cab_w * 0.45 - 0.006, 0.0, head_z)),
        material=m["accent"],
        name="reader_strip", material_class_id="plastic.opaque_glossy_molded",
    )
    frame.visual(
        Box((r.cab_w * 0.5, 0.01, 0.05)),
        origin=Origin(xyz=(r.cab_cx, -r.cab_d * 0.35 - 0.005, head_z + r.cab_h * 0.18)),
        material=m["bearing_bright"],
        name="reader_indicator", material_class_id="tech.emissive_surface",
    )


# adopted: S1
def _decorate_rugged_base(frame: Part, r: ResolvedTurnstileGatesConfig, m: dict) -> None:
    """Heavy boxed base with corner bolts (S1 rugged base frame)."""
    box_w = r.base_radius * 2.0
    frame.visual(
        Box((box_w, box_w, r.base_h * 0.9)),
        origin=Origin(xyz=(0.0, 0.0, r.base_h * 0.45)),
        material=m["frame_dark"],
        name="rugged_skirt", material_class_id=("metal.paint_coated" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
    )
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            frame.visual(
                Cylinder(radius=0.016, length=0.02),
                origin=Origin(xyz=(sx * box_w * 0.42, sy * box_w * 0.42, r.base_h * 0.9 + 0.006)),
                material=m["hardware"],
                name=f"floor_bolt_{'p' if sx > 0 else 'n'}{'p' if sy > 0 else 'n'}", material_class_id=("metal.steel_galvanized" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
            )
    frame.visual(
        Box((box_w * 0.7, box_w * 0.7, 0.06)),
        origin=Origin(xyz=(0.0, 0.0, r.base_h + 0.03)),
        material=m["frame"],
        name="rugged_riser", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "warm_brass"} else "metal.paint_coated"),
    )
    # A bolted maintenance fascia on the +X side, kept below the arm plane.
    frame.visual(
        Box((r.cab_w * 0.95, r.cab_d * 0.6, r.cab_h * 0.85)),
        origin=Origin(xyz=(r.cab_cx, 0.0, r.base_h + r.cab_h * 0.42)),
        material=m["frame"],
        name="utility_housing", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "warm_brass"} else "metal.paint_coated"),
    )


# adopted: S3
def _decorate_service_bearing(frame: Part, r: ResolvedTurnstileGatesConfig, m: dict) -> None:
    """Stacked wear rings around the post (S3 bearing_core + wear rings)."""
    ring_zs = [
        r.base_h + 0.10,
        r.base_h + 0.10 + (r.bearing_top_z - r.base_h - 0.18) * 0.5,
        r.bearing_top_z - 0.10,
    ]
    radii = [r.post_radius + 0.045, r.post_radius + 0.034, r.post_radius + 0.028]
    for idx, (z, rad) in enumerate(zip(ring_zs, radii)):
        frame.visual(
            Cylinder(radius=rad, length=0.03),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=m["bearing"] if idx % 2 == 0 else m["bearing_bright"],
            name=f"wear_ring_{idx}", material_class_id=("metal.steel_bare" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
        )
    housing_front_y = -r.cab_d * 0.31
    frame.visual(
        Box((r.cab_w * 0.9, 0.012, r.cab_h)),
        origin=Origin(xyz=(r.cab_cx, housing_front_y - 0.003, r.base_h + r.cab_h * 0.5)),
        material=m["frame"],
        name="service_door_fixed", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "warm_brass"} else "metal.paint_coated"),
    )
    frame.visual(
        Box((r.cab_w * 0.9, r.cab_d * 0.62, r.cab_h)),
        origin=Origin(xyz=(r.cab_cx, 0.0, r.base_h + r.cab_h * 0.5)),
        material=m["frame_dark"],
        name="service_housing", material_class_id=("metal.paint_coated" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
    )


# adopted: S4
def _decorate_split_head(frame: Part, r: ResolvedTurnstileGatesConfig, m: dict) -> None:
    """Two side head modules flanking the post (S4 split bearing/head modules).

    Both heads stay below the arm plane and within a modest radius; the arms
    sweep well above them.
    """
    for sx, tag in ((-1.0, "left"), (1.0, "right")):
        frame.visual(
            Box((r.head_w, r.head_w * 1.2, r.head_h)),
            origin=Origin(xyz=(sx * r.head_offset, 0.0, r.base_h + r.head_h * 0.5)),
            material=m["frame"],
            name=f"head_module_{tag}", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "warm_brass"} else "metal.paint_coated"),
        )
        frame.visual(
            Box((r.head_w * 0.5, r.head_w * 0.18, r.head_h * 0.4)),
            origin=Origin(
                xyz=(
                    sx * r.head_offset,
                    -r.head_w * 0.6 - 0.004,
                    r.base_h + r.head_h * 0.62,
                )
            ),
            material=m["accent"],
            name=f"head_indicator_{tag}", material_class_id="tech.emissive_surface",
        )
        # Low connecting beam back to the central pedestal so the heads read as
        # part of one frame.
        beam_len = r.head_offset
        frame.visual(
            Box((beam_len, 0.05, 0.05)),
            origin=Origin(xyz=(sx * beam_len * 0.5, 0.0, r.base_h + 0.025)),
            material=m["frame_dark"],
            name=f"head_beam_{tag}", material_class_id=("metal.paint_coated" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
        )


# adopted: S3
def _add_fixed_bearing_stack(frame: Part, r: ResolvedTurnstileGatesConfig, m: dict) -> None:
    """Extra fixed bearing wear rings (service_module=fixed_bearing_stack).

    Per Rule 1 these do not articulate, so they are fused onto the frame part
    rather than introduced as separate FIXED-jointed parts.
    """
    for idx in range(3):
        z = r.base_h + 0.07 + idx * 0.055
        if z > r.bearing_top_z - 0.12:
            break
        frame.visual(
            Cylinder(radius=r.post_radius + 0.05 - idx * 0.006, length=0.028),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=m["bearing_bright"] if idx % 2 else m["bearing"],
            name=f"fixed_wear_ring_{idx}", material_class_id=("metal.steel_bare" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
        )
    frame.visual(
        Cylinder(radius=r.post_radius + 0.012, length=0.04),
        origin=Origin(xyz=(0.0, 0.0, r.bearing_top_z - 0.085)),
        material=m["hardware"],
        name="bearing_grease_collar", material_class_id="metal.steel_galvanized",
    )


# adopted: S1
def _add_service_cabinet(frame: Part, r: ResolvedTurnstileGatesConfig, m: dict) -> None:
    """Dedicated maintenance cabinet (S1) that the service panel + hatch mate to.

    Built whenever the service-panel module is selected so the hinged leaves
    always have a known, lane-independent surface to seat against. It overlaps
    the central pedestal so it reads as one frame and stays below the arms.
    """
    cz = r.base_h + r.cab_h * 0.5
    frame.visual(
        Box((r.cab_w, r.cab_d, r.cab_h)),
        origin=Origin(xyz=(r.cab_cx, 0.0, cz)),
        material=m["frame"],
        name="service_cabinet_body", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "warm_brass"} else "metal.paint_coated"),
    )
    frame.visual(
        Box((0.05, 0.04, 0.012)),
        origin=Origin(xyz=(r.cab_cx + r.cab_w * 0.28, 0.0, r.base_h + r.cab_h - 0.006)),
        material=m["accent"],
        name="service_cabinet_label", material_class_id="plastic.opaque_glossy_molded",
    )


def _build_frame(model: ArticulatedObject, r: ResolvedTurnstileGatesConfig, m: dict) -> Part:
    frame = model.part("frame")
    _build_frame_core(frame, r, m)

    if r.lane_style == "refined_frame":
        _decorate_refined_frame(frame, r, m)
    elif r.lane_style == "rugged_base":
        _decorate_rugged_base(frame, r, m)
    elif r.lane_style == "service_bearing":
        _decorate_service_bearing(frame, r, m)
    elif r.lane_style == "split_head":
        _decorate_split_head(frame, r, m)

    if r.service_module == "service_panel_and_hatch":
        _add_service_cabinet(frame, r, m)
    if r.service_module == "fixed_bearing_stack":
        _add_fixed_bearing_stack(frame, r, m)

    frame.inertial = Inertial.from_geometry(
        Box((max(0.3, r.base_radius * 2.0), max(0.3, r.base_radius * 2.0), r.bearing_top_z)),
        mass=180.0,
        origin=Origin(xyz=(0.0, 0.0, r.bearing_top_z * 0.5)),
    )
    return frame


# --------------------------------------------------------------------------- #
# Rotor builders (Slot B) — hub + radial arms fused on the single `rotor` part.
# Local frame: z=0 maps to the joint origin at world ``bearing_top_z``.
# --------------------------------------------------------------------------- #


# adopted: S2
def _build_hub(rotor: Part, r: ResolvedTurnstileGatesConfig, m: dict) -> None:
    """Hub stack adapted from S2 (lower thrust face / hub barrel / cap)."""
    # Lower thrust face: bottom sits ~5 mm below the seat so it embeds ~3 mm
    # into the frame bearing pad (top at seat - 2 mm). The embed is < 5 mm, so
    # connectivity passes while the overlap baseline does not flag it.
    rotor.visual(
        Cylinder(radius=r.hub_radius * 1.22, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, 0.004)),
        material=m["bearing_bright"],
        name="lower_thrust_face", material_class_id=("metal.chrome_polished" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_polished"),
    )
    rotor.visual(
        Cylinder(radius=r.hub_radius, length=0.06),
        origin=Origin(xyz=(0.0, 0.0, 0.034)),
        material=m["hub"],
        name="hub_barrel", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "warm_brass"} else "metal.paint_coated"),
    )
    rotor.visual(
        Cylinder(radius=r.hub_radius * 1.18, length=0.022),
        origin=Origin(xyz=(0.0, 0.0, 0.066)),
        material=m["bearing_bright"],
        name="upper_hub_cap", material_class_id=("metal.chrome_polished" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_polished"),
    )
    rotor.visual(
        Cylinder(radius=r.hub_radius * 0.5, length=0.082),
        origin=Origin(xyz=(0.0, 0.0, 0.04)),
        material=m["hardware"],
        name="inner_hub_core", material_class_id="metal.steel_bare",
    )


# adopted: S1, S5
def _add_hub_detail(rotor: Part, r: ResolvedTurnstileGatesConfig, m: dict) -> None:
    """Barrier-style-specific hub detailing."""
    if r.barrier_style == "rugged_rotor":
        # Bolt circle on the cap (S1 bolt circles).
        for i, ang in enumerate(_arm_angles(6)):
            bx, by = _radial_xy(r.hub_radius * 0.78, ang)
            rotor.visual(
                Cylinder(radius=0.006, length=0.016),
                origin=Origin(xyz=(bx, by, 0.08)),
                material=m["hardware"],
                name=f"hub_bolt_{i}", material_class_id=("metal.steel_galvanized" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
            )
    elif r.barrier_style == "bearing_hub":
        # Visible bearing collar that rides just above the frame bearing pad
        # (sits above the seat so it does not interpenetrate the fixed pad).
        rotor.visual(
            Cylinder(radius=r.hub_radius * 1.05, length=0.022),
            origin=Origin(xyz=(0.0, 0.0, 0.018)),
            material=m["bearing"],
            name="rotor_bearing_collar", material_class_id=("metal.steel_bare" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
        )
    elif r.barrier_style == "modular_arm_hub":
        # A taller arm-hub drum parented (visually) above the seat (S4).
        rotor.visual(
            Cylinder(radius=r.hub_radius * 0.92, length=0.11),
            origin=Origin(xyz=(0.0, 0.0, 0.09)),
            material=m["column"],
            name="arm_hub_drum", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "warm_brass"} else "metal.paint_coated"),
        )
        rotor.visual(
            Cylinder(radius=r.hub_radius * 1.1, length=0.018),
            origin=Origin(xyz=(0.0, 0.0, 0.15)),
            material=m["bearing_bright"],
            name="arm_hub_cap", material_class_id=("metal.chrome_polished" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_polished"),
        )


# adopted: S2, S1
def _add_arm_surface_pattern(
    rotor: Part,
    r: ResolvedTurnstileGatesConfig,
    m: dict,
    *,
    index: int,
    angle: float,
    span_len: float,
) -> None:
    """Add arm-local manufacturing detail while keeping every element bonded.

    The pattern pieces overlap the main arm body by a few millimetres, so the
    compiler sees one connected rotor island. Round/capsule arms get sleeve
    collars and side beads; flat/paddle arms get raised grip plates and ribs.
    """
    z = r.arm_z
    perp_x = -math.sin(angle)
    perp_y = math.cos(angle)
    fractions = (0.30, 0.52, 0.74)

    for band_i, frac in enumerate(fractions):
        pos_r = r.arm_inner_r + span_len * frac
        bx, by = _radial_xy(pos_r, angle)
        if r.arm_style in ("round_tube", "capsule_rail"):
            rotor.visual(
                Cylinder(radius=r.arm_radius * 1.28, length=max(0.026, r.arm_radius * 1.45)),
                origin=Origin(xyz=(bx, by, z), rpy=_radial_cyl_rpy(angle)),
                material=m["accent"] if band_i % 2 == 0 else m["hardware"],
                name=f"arm_{index}_grip_band_{band_i}", material_class_id="rubber.smooth_plain",
            )
        else:
            rotor.visual(
                Box((max(0.035, span_len * 0.08), r.arm_radius * 3.2, r.arm_radius * 0.72)),
                origin=Origin(
                    xyz=(bx, by, z + r.arm_radius * 0.30),
                    rpy=(0.0, 0.0, angle),
                ),
                material=m["accent"] if band_i % 2 == 0 else m["hardware"],
                name=f"arm_{index}_raised_grip_plate_{band_i}", material_class_id="rubber.smooth_plain",
            )

    # A short contrasting root ferrule makes the arms read as bolted into the
    # hub instead of simple sticks.
    ferrule_r = r.arm_inner_r + span_len * 0.10
    fx, fy = _radial_xy(ferrule_r, angle)
    rotor.visual(
        Cylinder(radius=r.arm_radius * 1.38, length=max(0.030, r.arm_radius * 1.7)),
        origin=Origin(xyz=(fx, fy, z), rpy=_radial_cyl_rpy(angle)),
        material=m["bearing_bright"],
        name=f"arm_{index}_root_ferrule", material_class_id=("metal.chrome_polished" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_polished"),
    )

    if r.arm_style == "paddle":
        paddle_center = r.arm_tip_r - span_len * 0.16
        for rib_i, offset in enumerate((-0.95, 0.0, 0.95)):
            rx = math.cos(angle) * paddle_center + perp_x * r.arm_radius * offset
            ry = math.sin(angle) * paddle_center + perp_y * r.arm_radius * offset
            rotor.visual(
                Box((span_len * 0.28, r.arm_radius * 0.52, r.arm_radius * 3.8)),
                origin=Origin(xyz=(rx, ry, z + r.arm_radius * 0.04), rpy=(0.0, 0.0, angle)),
                material=m["hardware"],
                name=f"arm_{index}_paddle_rib_{rib_i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
            )
    elif r.arm_style == "flat_bar":
        for rib_i, frac in enumerate((0.40, 0.66)):
            rr = r.arm_inner_r + span_len * frac
            rx, ry = _radial_xy(rr, angle)
            rotor.visual(
                Box((span_len * 0.18, r.arm_radius * 0.46, r.arm_radius * 2.4)),
                origin=Origin(xyz=(rx, ry, z), rpy=(0.0, 0.0, angle + math.pi / 2.0)),
                material=m["hardware"],
                name=f"arm_{index}_cross_stamp_{rib_i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
            )
    elif r.arm_style == "capsule_rail":
        bead_len = span_len * 0.78
        bead_mid = r.arm_inner_r + span_len * 0.52
        for bead_i, side in enumerate((-1.0, 1.0)):
            cx = math.cos(angle) * bead_mid + perp_x * side * r.arm_radius * 1.05
            cy = math.sin(angle) * bead_mid + perp_y * side * r.arm_radius * 1.05
            rotor.visual(
                Cylinder(radius=r.arm_radius * 0.34, length=bead_len),
                origin=Origin(xyz=(cx, cy, z), rpy=_radial_cyl_rpy(angle)),
                material=m["bearing_bright"],
                name=f"arm_{index}_side_bead_{bead_i}", material_class_id=("metal.chrome_polished" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_polished"),
            )


def _add_arm(
    rotor: Part, r: ResolvedTurnstileGatesConfig, m: dict, *, index: int, angle: float
) -> None:
    """One radial barrier arm, fused onto the rotor part (moves with the hub).

    ``arm_style`` selects the cross-section; all variants are a socket near the
    hub plus a span reaching to ``arm_tip_r`` and an end feature.
    """
    z = r.arm_z
    span_len = r.arm_tip_r - r.arm_inner_r
    mid_r = (r.arm_inner_r + r.arm_tip_r) * 0.5

    # Socket clamp shared by every arm style (S1 arm sockets).
    sx, sy = _radial_xy(r.arm_inner_r + 0.02, angle)
    rotor.visual(
        Cylinder(radius=r.arm_radius * 1.5, length=0.06),
        origin=Origin(xyz=(sx, sy, z), rpy=_radial_cyl_rpy(angle)),
        material=m["hub"],
        name=f"arm_{index}_socket", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "warm_brass"} else "metal.paint_coated"),
    )

    mx, my = _radial_xy(mid_r, angle)
    if r.arm_style == "round_tube":
        rotor.visual(
            Cylinder(radius=r.arm_radius, length=span_len),
            origin=Origin(xyz=(mx, my, z), rpy=_radial_cyl_rpy(angle)),
            material=m["arm"],
            name=f"arm_{index}_tube", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "anthracite", "warm_brass"} else "metal.paint_coated"),
        )
    elif r.arm_style == "flat_bar":
        rotor.visual(
            Box((span_len, r.arm_radius * 2.6, r.arm_radius * 1.4)),
            origin=Origin(xyz=(mx, my, z), rpy=(0.0, 0.0, angle)),
            material=m["arm"],
            name=f"arm_{index}_tube", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "anthracite", "warm_brass"} else "metal.paint_coated"),
        )
    elif r.arm_style == "paddle":
        rotor.visual(
            Box((span_len * 0.74, r.arm_radius * 1.8, r.arm_radius * 1.2)),
            origin=Origin(
                xyz=(*_radial_xy(r.arm_inner_r + span_len * 0.37, angle), z),
                rpy=(0.0, 0.0, angle),
            ),
            material=m["arm"],
            name=f"arm_{index}_tube", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "anthracite", "warm_brass"} else "metal.paint_coated"),
        )
        px, py = _radial_xy(r.arm_tip_r - span_len * 0.16, angle)
        rotor.visual(
            Box((span_len * 0.32, r.arm_radius * 4.6, r.arm_radius * 3.2)),
            origin=Origin(xyz=(px, py, z), rpy=(0.0, 0.0, angle)),
            material=m["accent"],
            name=f"arm_{index}_paddle", material_class_id="metal.paint_coated",
        )
    elif r.arm_style == "capsule_rail":
        rotor.visual(
            Cylinder(radius=r.arm_radius * 0.9, length=span_len),
            origin=Origin(xyz=(mx, my, z), rpy=_radial_cyl_rpy(angle)),
            material=m["arm"],
            name=f"arm_{index}_tube", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "anthracite", "warm_brass"} else "metal.paint_coated"),
        )
        for cap_r, tag in ((r.arm_inner_r, "in"), (r.arm_tip_r, "out")):
            cx, cy = _radial_xy(cap_r, angle)
            rotor.visual(
                Sphere(radius=r.arm_radius * 1.05),
                origin=Origin(xyz=(cx, cy, z)),
                material=m["arm"],
                name=f"arm_{index}_cap_{tag}", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "anthracite", "warm_brass"} else "metal.paint_coated"),
            )

    # End sleeve / bump rubber at the tip (S2 end_sleeve).
    tx, ty = _radial_xy(r.arm_tip_r - 0.012, angle)
    rotor.visual(
        Cylinder(radius=r.arm_radius * 1.25, length=0.04),
        origin=Origin(xyz=(tx, ty, z), rpy=_radial_cyl_rpy(angle)),
        material=m["arm_tip"],
        name=f"arm_{index}_end_sleeve", material_class_id="rubber.smooth_plain",
    )
    _add_arm_surface_pattern(
        rotor,
        r,
        m,
        index=index,
        angle=angle,
        span_len=span_len,
    )


def _pawl_geometry(r: ResolvedTurnstileGatesConfig) -> tuple[float, float, float, float, float]:
    """Shared lockout-pawl placement so the rotor ratchet ring, the fixed
    bracket, and the pawl part all agree.

    Returns ``(pivot_r, tip_r, bar_len, pin_z, ratchet_r)`` where ``pin_z`` is
    the world hinge height (well below the arm plane) and ``ratchet_r`` is the
    ratchet tooth radius the pawl is poised against.
    """
    ratchet_r = r.hub_radius + 0.018
    tip_r = r.hub_radius + 0.075
    pivot_r = r.hub_radius + 0.235
    bar_len = pivot_r - tip_r
    pin_z = r.bearing_top_z - 0.10
    return pivot_r, tip_r, bar_len, pin_z, ratchet_r


def _pawl_engaged_upper_limit(r: ResolvedTurnstileGatesConfig) -> float:
    """Largest lockout-pawl engage angle whose tooth stays clear of the arms.

    The pawl tooth (``pawl_tooth`` in :func:`_build_lockout_pawl`) swings up about
    the hinge toward the rotor arm that lies at the pawl azimuth. Because the
    rotor spins, an arm can be presented at that azimuth at any time (the rest
    pose already aligns ``arm_0`` with the +x pawl), so the engaged tooth must
    stop just *below* the lowest arm surface instead of passing through it.

    Single source (Contract 3c) for the derived engaged limit: solve the tooth's
    top-corner world-z sweep against the arm-plane lowest z with a small
    clearance. ``z_top(theta) = pin_z + tooth_reach*sin + tooth_top*cos`` where
    the tooth box (from ``_build_lockout_pawl``) reaches ``bar_len + 0.02`` in
    -x and its top face sits ``-0.004 + 0.025`` above the hinge.
    """
    _, _, bar_len, pin_z, _ = _pawl_geometry(r)
    tooth_reach = bar_len + 0.02
    tooth_top_local = -0.004 + 0.025
    # Lowest world z of any arm element near the tooth's radius. 1.5*arm_radius
    # below the arm centreline conservatively covers grip bands / root ferrules
    # / cross stamps for every arm_style at that radial band.
    arm_low = r.bearing_top_z + r.arm_z - r.arm_radius * 1.5
    clearance = 0.012
    target = arm_low - clearance - pin_z  # required tooth-top rise to just clear
    radius = math.hypot(tooth_reach, tooth_top_local)
    if target >= radius:
        # Arm plane is out of the tooth's reach; the full configured range is safe.
        return 0.80
    phi = math.atan2(tooth_top_local, tooth_reach)
    theta = math.asin(_clamp(target / radius, -1.0, 1.0)) - phi
    return max(0.0, theta)


def _build_rotor(model: ArticulatedObject, r: ResolvedTurnstileGatesConfig, m: dict) -> Part:
    rotor = model.part("rotor")
    _build_hub(rotor, r, m)
    _add_hub_detail(rotor, r, m)
    for index, angle in enumerate(_arm_angles(r.arm_count)):
        _add_arm(rotor, r, m, index=index, angle=angle)
    rotor.inertial = Inertial.from_geometry(
        Cylinder(radius=r.arm_tip_r, length=0.12),
        mass=16.0,
        origin=Origin(xyz=(0.0, 0.0, r.arm_z)),
    )
    return rotor


# --------------------------------------------------------------------------- #
# Service / locking parts (Slot C) — separate parts with their own joints.
# --------------------------------------------------------------------------- #


# adopted: S1
def _build_service_panel(
    model: ArticulatedObject, r: ResolvedTurnstileGatesConfig, m: dict
) -> Part:
    """Vertical-hinge service panel on the frame cabinet front (S1).

    Local frame: hinge axis along local +z through the origin; the leaf extends
    +x and lies on the cabinet front (-y) face.
    """
    panel = model.part("service_panel")
    panel_h = r.cab_h * 0.72
    panel_w = r.cab_w * 0.74
    panel.visual(
        Cylinder(radius=0.013, length=panel_h),
        origin=Origin(xyz=(0.0, 0.0, panel_h * 0.5)),
        material=m["hardware"],
        name="panel_hinge_barrel", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
    )
    panel.visual(
        Box((panel_w, 0.016, panel_h)),
        origin=Origin(xyz=(panel_w * 0.5, -0.008 + 0.003, panel_h * 0.5)),
        material=m["frame"],
        name="panel_leaf", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "warm_brass"} else "metal.paint_coated"),
    )
    panel.visual(
        Box((0.05, 0.024, 0.10)),
        origin=Origin(xyz=(panel_w * 0.7, -0.024, panel_h * 0.5)),
        material=m["hardware"],
        name="panel_handle", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
    )
    panel.inertial = Inertial.from_geometry(
        Box((panel_w, 0.02, panel_h)),
        mass=5.0,
        origin=Origin(xyz=(panel_w * 0.5, 0.0, panel_h * 0.5)),
    )
    return panel


# adopted: S1
def _build_inspection_hatch(
    model: ArticulatedObject, r: ResolvedTurnstileGatesConfig, m: dict
) -> Part:
    """Horizontal-hinge inspection hatch on the cabinet top (S1).

    Local frame: hinge axis along local y through the origin; the leaf extends
    +x and lies just above the cabinet top.
    """
    hatch = model.part("inspection_hatch")
    hatch_len = r.cab_w * (0.12 if r.lane_style == "split_head" else 0.24)
    hatch_wy = r.cab_d * 0.5
    hatch.visual(
        Cylinder(radius=0.012, length=hatch_wy),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=_y_cyl_rpy()),
        material=m["hardware"],
        name="hatch_hinge_barrel", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
    )
    hatch.visual(
        Box((hatch_len, hatch_wy, 0.014)),
        origin=Origin(xyz=(hatch_len * 0.5, 0.0, 0.004)),
        material=m["frame"],
        name="hatch_leaf", material_class_id=("metal.stainless_matte" if r.material_style in {"satin_steel", "warm_brass"} else "metal.paint_coated"),
    )
    hatch.visual(
        Box((0.035, 0.035, 0.018)),
        origin=Origin(xyz=(hatch_len * 0.22, -hatch_wy * 0.38, 0.019)),
        material=m["hardware"],
        name="hatch_handle", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
    )
    hatch.inertial = Inertial.from_geometry(
        Box((hatch_len, hatch_wy, 0.02)),
        mass=3.5,
        origin=Origin(xyz=(hatch_len * 0.5, 0.0, 0.0)),
    )
    return hatch


# adopted: S5
def _build_lockout_pawl(model: ArticulatedObject, r: ResolvedTurnstileGatesConfig, m: dict) -> Part:
    """Safety lockout pawl (S5 lockout_pawl).

    Local frame: pivot axis along local y through the origin; the pawl bar
    reaches -x toward the rotor ratchet teeth, leaving a rest-pose gap.
    """
    pawl = model.part("lockout_pawl")
    _, _, bar_len, _, _ = _pawl_geometry(r)
    pawl.visual(
        Cylinder(radius=0.02, length=0.06),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=_y_cyl_rpy()),
        material=m["accent"],
        name="pawl_pivot_boss", material_class_id="metal.paint_coated",
    )
    pawl.visual(
        Box((bar_len, 0.018, 0.03)),
        origin=Origin(xyz=(-bar_len * 0.5, 0.0, 0.0)),
        material=m["accent"],
        name="pawl_bar", material_class_id="metal.paint_coated",
    )
    # Engagement tooth at the inboard end, poised just outside the ratchet ring.
    pawl.visual(
        Box((0.04, 0.024, 0.05)),
        origin=Origin(xyz=(-bar_len, 0.0, -0.004)),
        material=m["hardware"],
        name="pawl_tooth", material_class_id="metal.steel_bare",
    )
    # Short grip nub kept below the arm plane (points up only a little).
    pawl.visual(
        Box((0.028, 0.022, 0.05)),
        origin=Origin(xyz=(-bar_len * 0.5, 0.0, 0.04)),
        material=m["accent"],
        name="pawl_grip", material_class_id="rubber.smooth_plain",
    )
    pawl.inertial = Inertial.from_geometry(
        Box((bar_len, 0.03, 0.06)),
        mass=1.2,
        origin=Origin(xyz=(-bar_len * 0.5, 0.0, 0.0)),
    )
    return pawl


def _add_pawl_bracket(
    frame: Part, r: ResolvedTurnstileGatesConfig, m: dict
) -> tuple[float, float, float]:
    """Fixed standoff + hinge pin (frame visuals) that capture the pawl pivot.

    Returns the world joint origin for the pawl hinge. The standoff is grounded
    and tied back to the pedestal by a low foot strut so the bracket reads as
    part of the fixed frame.
    """
    pivot_r, _, _, pin_z, _ = _pawl_geometry(r)
    # Fixed lockout indexing blocks embedded into the central post. Earlier
    # versions placed these as separate rotor teeth at this height, which read
    # as small floating blocks in the viewer; seating them into the fixed post
    # keeps the center detail visually attached.
    block_depth = 0.026
    block_width = 0.014
    block_height = 0.024
    block_embed = 0.003
    block_r = r.post_radius + block_depth * 0.5 - block_embed
    for i, ang in enumerate(_arm_angles(8)):
        bx, by = _radial_xy(block_r, ang)
        frame.visual(
            Box((block_depth, block_width, block_height)),
            origin=Origin(xyz=(bx, by, pin_z), rpy=(0.0, 0.0, ang)),
            material=m["ratchet"],
            name=f"fixed_lockout_index_block_{i}", material_class_id="metal.blackened_gunmetal",
        )

    # Low foot strut from the pedestal out to the standoff (below the arms).
    strut_len = pivot_r + 0.06
    frame.visual(
        Box((strut_len, 0.05, 0.05)),
        origin=Origin(xyz=(strut_len * 0.5, 0.0, r.base_h + 0.03)),
        material=m["hardware"],
        name="pawl_foot_strut", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
    )
    # Vertical standoff post rising from the floor to the hinge pin.
    frame.visual(
        Box((0.05, 0.05, pin_z)),
        origin=Origin(xyz=(pivot_r + 0.025, 0.0, pin_z * 0.5)),
        material=m["hardware"],
        name="pawl_standoff_post", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_aged"),
    )
    # Hinge pin (axis along y) that the pawl boss wraps.
    frame.visual(
        Cylinder(radius=0.01, length=0.09),
        origin=Origin(xyz=(pivot_r, 0.0, pin_z), rpy=_y_cyl_rpy()),
        material=m["bearing_bright"],
        name="pawl_bracket_pin", material_class_id=("metal.chrome_polished" if r.material_style in {"satin_steel", "anthracite", "industrial_safety", "midnight"} else "metal.brass_polished"),
    )
    return (pivot_r, 0.0, pin_z)


# --------------------------------------------------------------------------- #
# Joint emitters
# --------------------------------------------------------------------------- #


def _emit_rotor_joint(
    model: ArticulatedObject, frame: Part, rotor: Part, r: ResolvedTurnstileGatesConfig
) -> None:
    origin = Origin(xyz=(0.0, 0.0, r.bearing_top_z))
    if r.rotor_joint_type == "limited_revolute":
        model.articulation(
            "rotor_spin",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=rotor,
            origin=origin,
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=160.0, velocity=2.4, lower=-math.pi, upper=math.pi),
        )
    else:
        model.articulation(
            "rotor_spin",
            ArticulationType.CONTINUOUS,
            parent=frame,
            child=rotor,
            origin=origin,
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=160.0, velocity=3.0),
        )


def _emit_service_joints(
    model: ArticulatedObject, frame: Part, r: ResolvedTurnstileGatesConfig, m: dict
) -> None:
    if r.service_module != "service_panel_and_hatch":
        return
    panel = _build_service_panel(model, r, m)
    hatch = _build_inspection_hatch(model, r, m)

    # Panel hinge: vertical axis on the cabinet front-left vertical edge.
    panel_h = r.cab_h * 0.72
    hinge_x = r.cab_cx - r.cab_w * 0.5 + 0.02
    # Hinge axis on the cabinet front face; the leaf embeds ~3 mm into it.
    panel_origin = Origin(xyz=(hinge_x, -r.cab_d * 0.5, r.base_h + (r.cab_h - panel_h) * 0.5))
    # The leaf lies on the cabinet -y front face and extends +x from the left
    # hinge. About +z, POSITIVE rotation would drive the leaf into +y (into the
    # cabinet body / utility housing) — a real cabinet door swings OUTWARD, away
    # from the box. So the door opens through the NEGATIVE range: rest pose (0)
    # is flush/closed and the open extreme (-panel_open_angle) sweeps the free
    # edge out into the clear -y half-space in front of the cabinet.
    model.articulation(
        "service_panel_hinge",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=panel,
        origin=panel_origin,
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=24.0, velocity=1.2, lower=-r.panel_open_angle, upper=0.0),
    )

    # Hatch hinge: horizontal axis on the cabinet top rear edge.
    hatch_origin = Origin(xyz=(r.cab_cx - r.cab_w * 0.5 + 0.02, 0.0, r.base_h + r.cab_h + 0.008))
    model.articulation(
        "inspection_hatch_hinge",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=hatch,
        origin=hatch_origin,
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=18.0, velocity=1.1, lower=0.0, upper=r.hatch_open_angle),
    )


def _emit_pawl_joint(
    model: ArticulatedObject, frame: Part, r: ResolvedTurnstileGatesConfig, m: dict
) -> None:
    if r.service_module != "lockout_pawl":
        return
    pawl = _build_lockout_pawl(model, r, m)
    origin_xyz = _add_pawl_bracket(frame, r, m)
    # Cap the engage angle so the tooth stops just below the arm plane instead of
    # swinging up through the arm at the pawl azimuth (derived, single-sourced).
    engage_upper = min(r.pawl_engage_angle, _pawl_engaged_upper_limit(r))
    model.articulation(
        "lockout_pawl_hinge",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=pawl,
        origin=Origin(xyz=origin_xyz),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=1.0, lower=-0.30, upper=engage_upper),
    )


# --------------------------------------------------------------------------- #
# Top-level build
# --------------------------------------------------------------------------- #


def build_turnstile_gates(
    config: TurnstileGatesConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or TurnstileGatesConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    materials = _register_materials(model, r.palette)
    frame = _build_frame(model, r, materials)
    rotor = _build_rotor(model, r, materials)
    _emit_rotor_joint(model, frame, rotor, r)
    _emit_service_joints(model, frame, r, materials)
    _emit_pawl_joint(model, frame, r, materials)
    return model


def build_seeded_turnstile_gates(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_turnstile_gates(config_from_seed(seed), assets=assets)


def slot_choices_for_config(config: TurnstileGatesConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("fixed_support_lane", r.lane_style),
        ("barrier_mechanism", r.barrier_style),
        ("service_and_locking", r.service_module),
        ("arm_count", str(r.arm_count)),
        ("rotor_joint_type", r.rotor_joint_type),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Tests / QC
# --------------------------------------------------------------------------- #


def _allow_expected_overlaps(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedTurnstileGatesConfig
) -> None:
    """Allow the captured-hinge interpenetrations the geometry intends.

    The leaves are designed to embed only a few millimetres (under the overlap
    tolerance), but the hinge barrels / pawl pivot are deliberately captured
    features; mirror the 5-star samples by allowing those specific pairs.
    """
    part_names = {p.name for p in model.parts}
    frame = model.get_part("frame")

    def _allow(part_name: str, elem_a: str, elem_b: str, reason: str) -> None:
        if part_name not in part_names:
            return
        try:
            ctx.allow_overlap(
                frame,
                model.get_part(part_name),
                elem_a=elem_a,
                elem_b=elem_b,
                reason=reason,
            )
        except Exception:
            pass

    cabinet_faces = (
        "service_cabinet_body",
        "service_cabinet_label",
    )
    for face in cabinet_faces:
        _allow(
            "service_panel",
            face,
            "panel_hinge_barrel",
            "service panel hinge barrel is captured in the cabinet edge",
        )
        _allow(
            "service_panel",
            face,
            "panel_leaf",
            "service panel sits flush in the cabinet opening",
        )
        _allow(
            "inspection_hatch",
            face,
            "hatch_hinge_barrel",
            "inspection hatch hinge barrel is captured on the cabinet top",
        )
        _allow(
            "inspection_hatch",
            face,
            "hatch_leaf",
            "inspection hatch lies flush on the cabinet top",
        )
    # Lane-decoration blocks that co-locate with the service cabinet at the same
    # (cab_cx, cab_h) footprint — they ARE the same frame block. The captured
    # hinge barrels seat into their top/edge exactly as they do the cabinet body,
    # so allow ONLY the barrels (not the leaves) against them.
    colocated_frame_blocks = (
        "reader_head",
        "service_housing",
        "service_door_fixed",
        "utility_housing",
    )
    for block in colocated_frame_blocks:
        _allow(
            "inspection_hatch",
            block,
            "hatch_hinge_barrel",
            "inspection hatch hinge barrel is captured on the cabinet top edge",
        )
        _allow(
            "service_panel",
            block,
            "panel_hinge_barrel",
            "service panel hinge barrel is captured in the cabinet edge",
        )
    for fixed_elem in ("pawl_bracket_pin", "pawl_standoff_post"):
        for pawl_elem in ("pawl_pivot_boss", "pawl_bar"):
            _allow(
                "lockout_pawl",
                fixed_elem,
                pawl_elem,
                "lockout pawl is captured on the fixed hinge pin / standoff",
            )


def run_turnstile_gates_tests(
    object_model: ArticulatedObject,
    config: TurnstileGatesConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()

    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.joints}

    # Identity: fixed support + central rotor + vertical spin joint.
    if "frame" not in part_names:
        ctx.fail("identity_frame", "turnstile must have a fixed `frame` support part")
    if "rotor" not in part_names:
        ctx.fail("identity_rotor", "turnstile must have a central `rotor` part")
    if "rotor_spin" not in joint_names:
        ctx.fail("identity_joint", "turnstile must have a `rotor_spin` joint")

    rotor_joint = object_model.get_articulation("rotor_spin")
    ctx.check(
        "rotor_axis_vertical",
        rotor_joint.axis == (0.0, 0.0, 1.0),
        f"rotor axis must be vertical (0,0,1); got {rotor_joint.axis}",
    )
    limits = rotor_joint.motion_limits
    if r.rotor_joint_type == "continuous":
        ctx.check(
            "rotor_is_continuous",
            rotor_joint.joint_type == ArticulationType.CONTINUOUS
            and limits is not None
            and limits.lower is None
            and limits.upper is None,
            f"continuous rotor should be unbounded; type={rotor_joint.joint_type}, limits={limits}",
        )
    else:
        ctx.check(
            "rotor_is_limited_revolute",
            rotor_joint.joint_type == ArticulationType.REVOLUTE
            and limits is not None
            and limits.lower is not None
            and limits.upper is not None,
            f"limited rotor should be a bounded REVOLUTE; type={rotor_joint.joint_type}, limits={limits}",
        )

    # Arms: one span visual per arm, evenly distributed, moving with the rotor.
    rotor = object_model.get_part("rotor")

    def _has_visual(part: Part, name: str) -> bool:
        try:
            part.get_visual(name)
            return True
        except Exception:
            return False

    for i in range(r.arm_count):
        if not _has_visual(rotor, f"arm_{i}_tube"):
            ctx.fail("arm_present", f"missing radial arm visual for arm {i}")

    end_sleeve = rotor.get_visual("arm_0_end_sleeve")
    arm_rest = ctx.part_element_world_aabb(rotor, elem=end_sleeve)
    spin_amount = (2.0 * math.pi / r.arm_count) * 0.5
    with ctx.pose({rotor_joint: spin_amount}):
        arm_rot = ctx.part_element_world_aabb(rotor, elem=end_sleeve)
    if arm_rest is not None and arm_rot is not None:
        rest_c = ((arm_rest[0][0] + arm_rest[1][0]) * 0.5, (arm_rest[0][1] + arm_rest[1][1]) * 0.5)
        rot_c = ((arm_rot[0][0] + arm_rot[1][0]) * 0.5, (arm_rot[0][1] + arm_rot[1][1]) * 0.5)
        moved = abs(rot_c[0] - rest_c[0]) > 0.05 or abs(rot_c[1] - rest_c[1]) > 0.05
        ctx.check(
            "arms_move_with_rotor",
            moved,
            f"arm tip did not move with rotor; rest={rest_c}, rotated={rot_c}",
        )

    # Service / locking joints by module.
    if r.service_module == "service_panel_and_hatch":
        for jname, axis_expected in (
            ("service_panel_hinge", (0.0, 0.0, 1.0)),
            ("inspection_hatch_hinge", (0.0, -1.0, 0.0)),
        ):
            if jname not in joint_names:
                ctx.fail("service_joint", f"missing {jname}")
            else:
                j = object_model.get_articulation(jname)
                ctx.check(
                    f"{jname}_axis",
                    j.axis == axis_expected,
                    f"{jname} axis must be {axis_expected}; got {j.axis}",
                )
    elif r.service_module == "lockout_pawl":
        if "lockout_pawl_hinge" not in joint_names:
            ctx.fail("pawl_joint", "missing lockout_pawl_hinge")
        else:
            j = object_model.get_articulation("lockout_pawl_hinge")
            ctx.check(
                "lockout_pawl_axis",
                j.axis == (0.0, 1.0, 0.0),
                f"lockout pawl axis must be (0,1,0); got {j.axis}",
            )

    # --- Motion-QC locks for the 穿模 fixes ------------------------------------
    # Service panel must swing OUTWARD (-y), not into the cabinet body.
    if r.service_module == "service_panel_and_hatch" and "service_panel_hinge" in joint_names:
        pj = object_model.get_articulation("service_panel_hinge")
        panel = object_model.get_part("service_panel")
        if _has_visual(panel, "panel_leaf") and pj.motion_limits is not None:
            leaf = panel.get_visual("panel_leaf")
            rest = ctx.part_element_world_aabb(panel, elem=leaf)
            open_ang = pj.motion_limits.lower if pj.motion_limits.lower is not None else 0.0
            with ctx.pose({pj: open_ang}):
                opened = ctx.part_element_world_aabb(panel, elem=leaf)
            if rest is not None and opened is not None:
                rest_cy = (rest[0][1] + rest[1][1]) * 0.5
                open_cy = (opened[0][1] + opened[1][1]) * 0.5
                ctx.check(
                    "service_panel_opens_outward",
                    open_cy < rest_cy - 0.05,
                    "service panel must swing outward (-y), away from the cabinet body; "
                    f"rest_cy={rest_cy:.3f}, open_cy={open_cy:.3f}",
                )

    # Lockout pawl tooth must stay clear below the arm plane when engaged.
    if r.service_module == "lockout_pawl" and "lockout_pawl_hinge" in joint_names:
        pj = object_model.get_articulation("lockout_pawl_hinge")
        pawl = object_model.get_part("lockout_pawl")
        if (
            _has_visual(pawl, "pawl_tooth")
            and _has_visual(rotor, "arm_0_tube")
            and pj.motion_limits is not None
            and pj.motion_limits.upper is not None
        ):
            tooth = pawl.get_visual("pawl_tooth")
            arm_tube = rotor.get_visual("arm_0_tube")
            with ctx.pose({pj: pj.motion_limits.upper}):
                tooth_aabb = ctx.part_element_world_aabb(pawl, elem=tooth)
            arm_aabb = ctx.part_element_world_aabb(rotor, elem=arm_tube)
            if tooth_aabb is not None and arm_aabb is not None:
                ctx.check(
                    "pawl_tooth_clears_arm_plane",
                    tooth_aabb[1][2] <= arm_aabb[0][2] + 0.005,
                    "engaged lockout pawl tooth must stop below the arm plane; "
                    f"tooth_top_z={tooth_aabb[1][2]:.4f}, arm_bottom_z={arm_aabb[0][2]:.4f}",
                )

    return ctx.report()


__all__ = [
    "TurnstileGatesConfig",
    "ResolvedTurnstileGatesConfig",
    "build_turnstile_gates",
    "build_seeded_turnstile_gates",
    "config_from_seed",
    "resolve_config",
    "run_turnstile_gates_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
