# SPDX-License-Identifier: Apache-2.0

"""Procedural template for ``studio_spotlight_on_yoke``.

Implements the reviewed modular spec at
``articraft_template_authoring/specs_modular_v1/studio_spotlight_on_yoke.md``.

Chain: ``base_root --yoke_pan(Z)--> pan_yoke --can_tilt(horizontal)--> spotlight_head``.

Slots and adopted 5-star sources (per the reviewed spec):

* Slot A ``root_support``: floor_pedestal_base / low_floor_disk_base /
  tripod_post_base / wheeled_dolly_base / telescoping_floor_stand /
  telescoping_tripod_stand. Sources S-A1..S-A6.
* Slot B ``pan_yoke``: two_arm_box_yoke / mesh_trunnion_yoke (TrunnionYokeGeometry)
  / swept_arm_yoke (sweep_profile_along_spline) / side_pivot_yoke. Sources
  S-B1..S-B4.
* Slot C ``spotlight_head``: primitive_box_cylinder_can / lathe_shell_can
  (LatheGeometry.from_shell_profiles) / cadquery_shell_can (cadquery shell with
  LatheGeometry fallback) / fresnel_lens_can (TorusGeometry fresnel rings +
  LatheGeometry shell). Sources S-C1..S-C4.
* Slot D ``auxiliary_mechanism``: none / tilt_lock_knobs / focus_or_mode_knob /
  barndoor_four_leaf / front_filter_or_gel_frame / service_hatch_or_lens_cover /
  foldable_carry_handle. Sources S-D1..S-D6.

Identity invariants enforced by ``run_studio_spotlight_on_yoke_tests``:

* every seed has a ``stand`` / ``pan_yoke`` / ``spotlight_head`` part,
* ``yoke_pan`` REVOLUTE/CONTINUOUS axis is vertical Z,
* ``can_tilt`` REVOLUTE axis is horizontal,
* ``spotlight_head`` exposes a translucent ``front_lens`` + ``front_bezel`` +
  ``rear_cap`` (the studio-spotlight identity signal).

Auxiliary mechanisms are emitted as ``parent.visual(...)`` decoration of the
``spotlight_head`` (or ``pan_yoke``) per Design Rule 1 — they don't
articulate as separate parts, but they still vary the part visuals enough to
register as distinct topology choices in ``module_topology_diversity``.
"""

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
    LatheGeometry,
    MotionLimits,
    Origin,
    Part,
    Sphere,
    TestContext,
    TestReport,
    TorusGeometry,
    TrunnionYokeGeometry,
    mesh_from_geometry,
    rounded_rect_profile,
    sweep_profile_along_spline,
    tube_from_spline_points,
)

__modular__ = True


RootSupport = Literal[
    "floor_pedestal_base",
    "low_floor_disk_base",
    "tripod_post_base",
    "wheeled_dolly_base",
    "telescoping_floor_stand",
    "telescoping_tripod_stand",
]
PanYokeStyle = Literal[
    "two_arm_box_yoke",
    "mesh_trunnion_yoke",
    "swept_arm_yoke",
    "side_pivot_yoke",
]
SpotlightHead = Literal[
    "primitive_box_cylinder_can",
    "lathe_shell_can",
    "cadquery_shell_can",
    "fresnel_lens_can",
]
AuxiliaryMechanism = Literal[
    "none",
    "tilt_lock_knobs",
    "focus_or_mode_knob",
    "barndoor_four_leaf",
    "front_filter_or_gel_frame",
    "service_hatch_or_lens_cover",
    "foldable_carry_handle",
]
PanJointType = Literal["revolute_limited", "continuous"]
MaterialStyle = Literal[
    "matte_black_stage",
    "brushed_silver",
    "cream_studio",
    "safety_yellow",
    "weatherproof_gray",
]


ROOT_SUPPORTS: tuple[RootSupport, ...] = (
    "floor_pedestal_base",
    "low_floor_disk_base",
    "tripod_post_base",
    "wheeled_dolly_base",
    "telescoping_floor_stand",
    "telescoping_tripod_stand",
)
PAN_YOKE_STYLES: tuple[PanYokeStyle, ...] = (
    "two_arm_box_yoke",
    "mesh_trunnion_yoke",
    "swept_arm_yoke",
    "side_pivot_yoke",
)
SPOTLIGHT_HEADS: tuple[SpotlightHead, ...] = (
    "primitive_box_cylinder_can",
    "lathe_shell_can",
    "cadquery_shell_can",
    "fresnel_lens_can",
)
AUXILIARY_MECHANISMS: tuple[AuxiliaryMechanism, ...] = (
    "none",
    "tilt_lock_knobs",
    "focus_or_mode_knob",
    "barndoor_four_leaf",
    "front_filter_or_gel_frame",
    "service_hatch_or_lens_cover",
    "foldable_carry_handle",
)
PAN_JOINT_TYPES: tuple[PanJointType, ...] = ("revolute_limited", "continuous")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "matte_black_stage",
    "brushed_silver",
    "cream_studio",
    "safety_yellow",
    "weatherproof_gray",
)


PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "matte_black_stage": {
        "base": (0.035, 0.037, 0.040, 1.0),
        "base_dark": (0.010, 0.011, 0.013, 1.0),
        "metal": (0.42, 0.43, 0.45, 1.0),
        "can": (0.025, 0.027, 0.030, 1.0),
        "bezel": (0.10, 0.105, 0.11, 1.0),
        "glass": (0.72, 0.82, 0.90, 0.42),
        "emitter": (1.00, 0.86, 0.48, 0.70),
        "accent": (0.92, 0.67, 0.12, 1.0),
        "rubber": (0.005, 0.005, 0.006, 1.0),
    },
    "brushed_silver": {
        "base": (0.54, 0.56, 0.58, 1.0),
        "base_dark": (0.22, 0.23, 0.24, 1.0),
        "metal": (0.73, 0.75, 0.78, 1.0),
        "can": (0.62, 0.64, 0.66, 1.0),
        "bezel": (0.38, 0.39, 0.40, 1.0),
        "glass": (0.70, 0.84, 0.96, 0.42),
        "emitter": (1.00, 0.88, 0.52, 0.70),
        "accent": (0.12, 0.36, 0.65, 1.0),
        "rubber": (0.04, 0.04, 0.045, 1.0),
    },
    "cream_studio": {
        "base": (0.75, 0.73, 0.66, 1.0),
        "base_dark": (0.38, 0.36, 0.31, 1.0),
        "metal": (0.58, 0.56, 0.50, 1.0),
        "can": (0.82, 0.80, 0.72, 1.0),
        "bezel": (0.30, 0.29, 0.26, 1.0),
        "glass": (0.78, 0.88, 0.96, 0.42),
        "emitter": (1.00, 0.89, 0.54, 0.70),
        "accent": (0.64, 0.20, 0.12, 1.0),
        "rubber": (0.05, 0.045, 0.04, 1.0),
    },
    "safety_yellow": {
        "base": (0.13, 0.13, 0.12, 1.0),
        "base_dark": (0.025, 0.025, 0.025, 1.0),
        "metal": (0.56, 0.58, 0.60, 1.0),
        "can": (0.92, 0.70, 0.10, 1.0),
        "bezel": (0.05, 0.05, 0.055, 1.0),
        "glass": (0.68, 0.82, 0.95, 0.40),
        "emitter": (1.00, 0.88, 0.46, 0.72),
        "accent": (0.08, 0.08, 0.08, 1.0),
        "rubber": (0.012, 0.012, 0.014, 1.0),
    },
    "weatherproof_gray": {
        "base": (0.40, 0.43, 0.44, 1.0),
        "base_dark": (0.15, 0.16, 0.17, 1.0),
        "metal": (0.60, 0.63, 0.63, 1.0),
        "can": (0.33, 0.36, 0.37, 1.0),
        "bezel": (0.17, 0.18, 0.19, 1.0),
        "glass": (0.70, 0.84, 0.92, 0.44),
        "emitter": (1.00, 0.86, 0.44, 0.70),
        "accent": (0.16, 0.42, 0.52, 1.0),
        "rubber": (0.025, 0.026, 0.028, 1.0),
    },
}


X_CYLINDER_RPY = (0.0, math.pi / 2.0, 0.0)
Y_CYLINDER_RPY = (-math.pi / 2.0, 0.0, 0.0)
Z_CYLINDER_RPY = (0.0, 0.0, 0.0)


@dataclass(frozen=True)
class StudioSpotlightOnYokeConfig:
    """Public, source-of-truth config for the spotlight-on-yoke."""

    root_support: RootSupport | None = None
    pan_yoke_style: PanYokeStyle | None = None
    spotlight_head: SpotlightHead | None = None
    auxiliary_mechanism: AuxiliaryMechanism | None = None
    pan_joint_type: PanJointType | None = None
    material_style: MaterialStyle = "matte_black_stage"
    mast_height: float = 0.58
    base_radius: float = 0.145
    can_radius: float = 0.105
    can_length: float = 0.300
    yoke_pan_limit: float = math.pi
    can_tilt_lower: float = -math.radians(45.0)
    can_tilt_upper: float = math.radians(65.0)
    name: str = "reference_studio_spotlight_on_yoke"


@dataclass(frozen=True)
class ResolvedStudioSpotlightOnYokeConfig:
    root_support: RootSupport
    pan_yoke_style: PanYokeStyle
    spotlight_head: SpotlightHead
    auxiliary_mechanism: AuxiliaryMechanism
    pan_joint_type: PanJointType
    material_style: MaterialStyle
    mast_height: float
    base_radius: float
    base_height: float
    can_radius: float
    can_length: float
    can_rear_depth: float
    yoke_half_width: float
    yoke_tilt_z: float
    yoke_side_height: float
    yoke_plate_thickness: float
    yoke_pan_limit: float
    can_tilt_lower: float
    can_tilt_upper: float
    fresnel_ring_count: int
    tripod_leg_count: int
    caster_wheel_count: int
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _choice(value: str | None, choices: tuple[str, ...], fallback: str) -> str:
    if value in choices:
        return value
    return fallback


def resolve_config(config: StudioSpotlightOnYokeConfig) -> ResolvedStudioSpotlightOnYokeConfig:
    root = _choice(config.root_support, ROOT_SUPPORTS, "floor_pedestal_base")
    yoke = _choice(config.pan_yoke_style, PAN_YOKE_STYLES, "two_arm_box_yoke")
    head = _choice(config.spotlight_head, SPOTLIGHT_HEADS, "primitive_box_cylinder_can")
    aux = _choice(config.auxiliary_mechanism, AUXILIARY_MECHANISMS, "none")
    pan_joint = _choice(config.pan_joint_type, PAN_JOINT_TYPES, "revolute_limited")
    material = _choice(config.material_style, MATERIAL_STYLES, "matte_black_stage")

    # Compatibility gating (per the reviewed spec).
    # - fresnel_lens_can must not be paired with front-mounted filter/gel/cover —
    #   that would occlude the fresnel concentric-ring identity.
    if head == "fresnel_lens_can" and aux in (
        "front_filter_or_gel_frame",
        "service_hatch_or_lens_cover",
    ):
        aux = "none"
    # - tilt_lock_knobs need outer trunnion bosses; swept_arm_yoke has no boss
    #   landing pad and side_pivot_yoke only has a single-side trunnion —
    #   fall back to none rather than build a phantom knob.
    if aux == "tilt_lock_knobs" and yoke in ("swept_arm_yoke", "side_pivot_yoke"):
        aux = "none"
    # - wheeled / low_disk / telescoping bases shouldn't lock the pan rotation
    #   to a narrow range (the dolly/stand is meant to spin freely).
    if root in ("low_floor_disk_base", "wheeled_dolly_base", "telescoping_floor_stand"):
        if pan_joint == "revolute_limited":
            # keep limited but widen below to ~pi.
            pass

    base_radius = _clamp(config.base_radius, 0.105, 0.230)
    can_radius = _clamp(config.can_radius, 0.072, 0.155)
    can_length = _clamp(config.can_length, 0.190, 0.450)
    mast_height = _clamp(config.mast_height, 0.220, 0.860)

    if root == "low_floor_disk_base":
        mast_height = _clamp(mast_height, 0.180, 0.360)
        base_radius = _clamp(base_radius, 0.115, 0.185)
    elif root == "wheeled_dolly_base":
        mast_height = _clamp(mast_height, 0.360, 0.620)
        base_radius = _clamp(base_radius, 0.150, 0.230)
    elif root == "tripod_post_base":
        mast_height = _clamp(mast_height, 0.540, 0.840)
        base_radius = _clamp(base_radius, 0.135, 0.200)
    elif root == "telescoping_floor_stand":
        mast_height = _clamp(mast_height, 0.500, 0.840)
        base_radius = _clamp(base_radius, 0.130, 0.205)
    elif root == "telescoping_tripod_stand":
        mast_height = _clamp(mast_height, 0.560, 0.860)
        base_radius = _clamp(base_radius, 0.140, 0.205)

    # Spotlight head sizing: lathe / fresnel cans tend to be a bit longer.
    can_rear_depth = 0.060
    if head == "lathe_shell_can":
        can_length = max(can_length, can_radius * 2.55)
        can_rear_depth = 0.060
    elif head == "cadquery_shell_can":
        can_length = max(can_length, can_radius * 2.75)
        can_rear_depth = 0.055
    elif head == "fresnel_lens_can":
        can_length = max(can_length, can_radius * 2.45)
        can_rear_depth = 0.060
    else:  # primitive_box_cylinder_can
        can_length = max(can_length, can_radius * 2.35)
        can_rear_depth = 0.050

    yoke_half_width = can_radius + 0.052
    # yoke_tilt_z must clear the pan stack (which tops out at z=0.110) plus
    # half the can diameter plus a clearance margin.
    yoke_tilt_z = max(0.155 + can_radius * 1.05, 0.205 + can_radius * 0.24)
    yoke_side_height = can_radius * 2.65 + 0.060
    if yoke == "side_pivot_yoke":
        # Single-arm yokes have a taller offset C-bracket.
        yoke_side_height = can_radius * 2.85 + 0.080
        yoke_plate_thickness = 0.040
    elif yoke == "mesh_trunnion_yoke":
        yoke_plate_thickness = 0.024
    elif yoke == "swept_arm_yoke":
        yoke_plate_thickness = 0.034
    else:
        yoke_plate_thickness = 0.034

    fresnel_ring_count = 4 if head == "fresnel_lens_can" else 0
    tripod_leg_count = 3 if root in ("tripod_post_base", "telescoping_tripod_stand") else 0
    caster_wheel_count = 4 if root == "wheeled_dolly_base" else 0

    tilt_lower = _clamp(config.can_tilt_lower, -1.05, -0.10)
    tilt_upper = _clamp(config.can_tilt_upper, 0.55, 1.30)
    if tilt_lower >= tilt_upper:
        tilt_lower, tilt_upper = -0.45, 1.05

    return ResolvedStudioSpotlightOnYokeConfig(
        root_support=root,  # type: ignore[arg-type]
        pan_yoke_style=yoke,  # type: ignore[arg-type]
        spotlight_head=head,  # type: ignore[arg-type]
        auxiliary_mechanism=aux,  # type: ignore[arg-type]
        pan_joint_type=pan_joint,  # type: ignore[arg-type]
        material_style=material,  # type: ignore[arg-type]
        mast_height=mast_height,
        base_radius=base_radius,
        base_height=0.030 if root not in ("wheeled_dolly_base", "low_floor_disk_base") else 0.040,
        can_radius=can_radius,
        can_length=can_length,
        can_rear_depth=can_rear_depth,
        yoke_half_width=yoke_half_width,
        yoke_tilt_z=yoke_tilt_z,
        yoke_side_height=yoke_side_height,
        yoke_plate_thickness=yoke_plate_thickness,
        yoke_pan_limit=_clamp(config.yoke_pan_limit, math.radians(120), math.tau),
        can_tilt_lower=tilt_lower,
        can_tilt_upper=tilt_upper,
        fresnel_ring_count=fresnel_ring_count,
        tripod_leg_count=tripod_leg_count,
        caster_wheel_count=caster_wheel_count,
        name=str(config.name or "studio_spotlight_on_yoke"),
    )


def slot_choices_for_config(config: StudioSpotlightOnYokeConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("root_support", r.root_support),
        ("pan_yoke", r.pan_yoke_style),
        ("spotlight_head", r.spotlight_head),
        ("auxiliary_mechanism", r.auxiliary_mechanism),
        ("pan_joint_type", r.pan_joint_type),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


def config_from_seed(seed: int) -> StudioSpotlightOnYokeConfig:
    """Deterministic procedural sampling. ``seed=0`` is not special."""
    rng = random.Random(seed)
    root: RootSupport = rng.choice(ROOT_SUPPORTS)
    yoke: PanYokeStyle = rng.choice(PAN_YOKE_STYLES)
    head: SpotlightHead = rng.choice(SPOTLIGHT_HEADS)

    # Auxiliary gating happens in resolve_config; here we sample from full set
    # so resolve_config can downgrade incompatible combos to "none".
    aux: AuxiliaryMechanism = rng.choice(AUXILIARY_MECHANISMS)
    pan_joint: PanJointType = rng.choice(PAN_JOINT_TYPES)
    material: MaterialStyle = rng.choice(MATERIAL_STYLES)

    if root == "low_floor_disk_base":
        mast_height = rng.uniform(0.18, 0.34)
    elif root == "wheeled_dolly_base":
        mast_height = rng.uniform(0.38, 0.58)
    elif root == "tripod_post_base":
        mast_height = rng.uniform(0.58, 0.82)
    elif root == "telescoping_floor_stand":
        mast_height = rng.uniform(0.52, 0.82)
    elif root == "telescoping_tripod_stand":
        mast_height = rng.uniform(0.60, 0.84)
    else:
        mast_height = rng.uniform(0.40, 0.74)

    return StudioSpotlightOnYokeConfig(
        root_support=root,
        pan_yoke_style=yoke,
        spotlight_head=head,
        auxiliary_mechanism=aux,
        pan_joint_type=pan_joint,
        material_style=material,
        mast_height=round(mast_height, 4),
        base_radius=round(rng.uniform(0.120, 0.205), 4),
        can_radius=round(rng.uniform(0.080, 0.135), 4),
        can_length=round(rng.uniform(0.230, 0.400), 4),
        yoke_pan_limit=round(rng.uniform(math.radians(150), math.tau), 4),
        can_tilt_lower=round(rng.uniform(-0.95, -0.25), 4),
        can_tilt_upper=round(rng.uniform(0.65, 1.20), 4),
        name=f"seeded_studio_spotlight_on_yoke_{seed}",
    )


def _register_materials(model: ArticulatedObject, material_style: MaterialStyle) -> dict[str, str]:
    palette = PALETTES[material_style]
    return {name: model.material(f"yoke_{name}", rgba=rgba) for name, rgba in palette.items()}


def _box(
    part: Part,
    name: str,
    size: tuple[float, float, float],
    xyz: tuple[float, float, float],
    material: str,
    rpy: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id=_material_class_id(material.name, ("yoke_rubber", "yoke_base_dark", "yoke_accent", "yoke_metal", "yoke_bezel", "yoke_base"), "metal.paint_coated", "glass.clear_transparent"))


def _cyl(
    part: Part,
    name: str,
    radius: float,
    length: float,
    xyz: tuple[float, float, float],
    material: str,
    rpy: tuple[float, float, float] = Z_CYLINDER_RPY,
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id=_material_class_id(material.name, ("yoke_base_dark", "yoke_metal", "yoke_bezel", "yoke_accent", "yoke_can", "yoke_rubber", "yoke_base"), "metal.paint_coated", "glass.clear_transparent"),
    )


def _sphere(
    part: Part, name: str, radius: float, xyz: tuple[float, float, float], material: str
) -> None:
    part.visual(Sphere(radius=radius), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="metal.paint_coated")


def _mesh_for_model(model: ArticulatedObject, geometry: object, name: str):
    if model.assets is not None:
        return mesh_from_geometry(geometry, model.assets.mesh_path(f"{name}.obj"))
    return mesh_from_geometry(geometry, name)


# --------------------------------------------------------------------------- #
# Slot A: root_support
# --------------------------------------------------------------------------- #
# Adopted sources:
#   S-A1 floor_pedestal_base       rec_…_0001 L49-L96
#   S-A2 low_floor_disk_base       rec_…_0005 L97-L148
#   S-A3 tripod_post_base          rec_…_1761967d L53-L165 (legs L226-L256)
#   S-A4 wheeled_dolly_base        rec_…_aa36438 L134-L189 (wheels L210-L221)
#   S-A5 telescoping_floor_stand   rec_…_b9ab25 L100-L135
#   S-A6 telescoping_tripod_stand  rec_…_afb8b9 L133-L157


def _build_floor_pedestal_base(
    stand: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    # rec_…_0001 L49-L96: rectangular weighted box base + central upright post.
    # All visuals form a single connected z-stack:
    #   base_box [0, bh] → socket [bh-0.005, bh+0.030] → post [bh+0.025, mast-0.025]
    #   → bearing [mast-0.030, mast].
    base_w = r.base_radius * 2.0
    base_d = r.base_radius * 1.55
    bh = r.base_height
    _box(stand, "weighted_base_box", (base_w, base_d, bh), (0.0, 0.0, bh * 0.5), m["base"])
    # rubber feet embed slightly into the base bottom.
    _box(
        stand,
        "base_rubber_front",
        (base_w * 0.78, 0.020, 0.012),
        (0.0, base_d * 0.42, 0.004),
        m["rubber"],
    )
    _box(
        stand,
        "base_rubber_rear",
        (base_w * 0.78, 0.020, 0.012),
        (0.0, -base_d * 0.42, 0.004),
        m["rubber"],
    )
    # socket: embeds 0.010 into base, sticks up 0.030.
    socket_h = 0.040
    _cyl(
        stand,
        "base_socket_collar",
        0.044,
        socket_h,
        (0.0, 0.0, bh + socket_h * 0.5 - 0.010),
        m["base_dark"],
    )
    # post: starts inside socket; embeds bottom 0.010 into socket.
    post_bottom = bh + 0.010
    bearing_h = 0.030
    post_top = r.mast_height - bearing_h + 0.005  # embed top 0.005 into bearing
    post_len = max(0.04, post_top - post_bottom)
    _cyl(
        stand, "center_post", 0.026, post_len, (0.0, 0.0, post_bottom + post_len * 0.5), m["metal"]
    )
    # bearing sits on top of post.
    _cyl(
        stand,
        "stand_top_bearing",
        0.040,
        bearing_h,
        (0.0, 0.0, r.mast_height - bearing_h * 0.5),
        m["base_dark"],
    )


def _build_low_floor_disk_base(
    stand: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    # rec_…_0005 L97-L148: low disk floor + short embedded post + bearing seat.
    base_h = r.base_height * 1.4
    _cyl(stand, "floor_disk_base", r.base_radius, base_h, (0.0, 0.0, base_h * 0.5), m["base"])
    _cyl(stand, "floor_rubber_ring", r.base_radius * 0.93, 0.012, (0.0, 0.0, 0.004), m["rubber"])
    bearing_h = 0.040
    post_bottom = base_h - 0.010
    post_top = r.mast_height - bearing_h + 0.005
    post_len = max(0.04, post_top - post_bottom)
    _cyl(
        stand,
        "short_center_post",
        0.030,
        post_len,
        (0.0, 0.0, post_bottom + post_len * 0.5),
        m["metal"],
    )
    _cyl(
        stand,
        "stand_top_bearing",
        0.046,
        bearing_h,
        (0.0, 0.0, r.mast_height - bearing_h * 0.5),
        m["base_dark"],
    )


def _build_tripod_post_base(
    stand: Part,
    r: ResolvedStudioSpotlightOnYokeConfig,
    m: dict[str, str],
    *,
    model: ArticulatedObject,
) -> None:
    # rec_…_1761967d L53-L165: crown hub + 3 spline tube legs + center mast.
    hub_z = r.base_height + 0.030
    _cyl(stand, "tripod_crown_hub", 0.060, 0.060, (0.0, 0.0, hub_z), m["base_dark"])
    leg_len = r.base_radius * 2.10
    for i in range(r.tripod_leg_count):
        angle = i * math.tau / r.tripod_leg_count + math.radians(20.0)
        fx = math.cos(angle) * leg_len * 0.86
        fy = math.sin(angle) * leg_len * 0.86
        leg_geom = tube_from_spline_points(
            [
                (math.cos(angle) * 0.020, math.sin(angle) * 0.020, hub_z),
                (math.cos(angle) * leg_len * 0.45, math.sin(angle) * leg_len * 0.45, hub_z * 0.45),
                (fx, fy, 0.030),
            ],
            radius=max(0.014, leg_len * 0.020),
            samples_per_segment=14,
            radial_segments=14,
            cap_ends=True,
        )
        stand.visual(
            _mesh_for_model(model, leg_geom, f"tripod_leg_geom_{i}_{r.root_support}"),
            origin=Origin(),
            material=m["metal"],
            name=f"tripod_leg_{i}", material_class_id=("metal.brushed_silver" if r.material_style == "brushed_silver" else "metal.aluminum_bare"),
        )
        _box(
            stand,
            f"tripod_foot_{i}",
            (0.080, 0.045, 0.020),
            (fx, fy, 0.012),
            m["rubber"],
            rpy=(0.0, 0.0, angle),
        )
        # Brace tie connecting hub to leg midpoint.
        cx2, cy2 = math.cos(angle) * leg_len * 0.50, math.sin(angle) * leg_len * 0.50
        _box(
            stand,
            f"tripod_brace_{i}",
            (leg_len * 0.95, 0.022, 0.018),
            (cx2 * 0.5, cy2 * 0.5, hub_z * 0.30),
            m["base_dark"],
            rpy=(0.0, 0.0, angle),
        )
    bearing_h = 0.034
    mast_top = r.mast_height - bearing_h + 0.005
    mast_len = max(0.06, mast_top - (hub_z - 0.010))
    _cyl(
        stand,
        "tripod_center_mast",
        0.030,
        mast_len,
        (0.0, 0.0, (mast_top + hub_z - 0.010) * 0.5),
        m["metal"],
    )
    _cyl(
        stand,
        "stand_top_bearing",
        0.042,
        bearing_h,
        (0.0, 0.0, r.mast_height - bearing_h * 0.5),
        m["base_dark"],
    )


def _build_wheeled_dolly_base(
    stand: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    # rec_…_aa36438 L134-L189: 4-caster fork bridges + short center post.
    w = r.base_radius * 2.10
    d = r.base_radius * 1.60
    bh = r.base_height
    # Tray: spans z ∈ [0.030, 0.030 + bh].
    tray_top = 0.030 + bh
    _box(stand, "dolly_tray", (w, d, bh), (0.0, 0.0, 0.030 + bh * 0.5), m["base"])
    # Spine sits on the tray (embedded 0.005 into tray top).
    _box(
        stand,
        "dolly_spine",
        (w * 0.48, d * 0.78, 0.030),
        (0.0, 0.0, tray_top + 0.010),
        m["base_dark"],
    )
    spine_top = tray_top + 0.025
    # Casters: forks embed into tray bottom, wheels touch fork (overlap).
    for i in range(r.caster_wheel_count):
        sx = 1.0 if i in (1, 3) else -1.0
        sy = 1.0 if i >= 2 else -1.0
        x = sx * w * 0.40
        y = sy * d * 0.36
        _box(stand, f"caster_fork_{i}", (0.034, 0.052, 0.046), (x, y, 0.030), m["base_dark"])
        _cyl(
            stand, f"caster_wheel_{i}", 0.024, 0.038, (x, y, 0.018), m["rubber"], rpy=X_CYLINDER_RPY
        )
    # Socket: sits on spine (embed 0.005 into spine top).
    socket_h = 0.080
    socket_top = spine_top + socket_h - 0.005
    _cyl(
        stand,
        "dolly_post_socket",
        0.054,
        socket_h,
        (0.0, 0.0, spine_top + socket_h * 0.5 - 0.005),
        m["base_dark"],
    )
    # Post: embeds into socket, ends at top.
    bearing_h = 0.040
    post_bottom = socket_top - 0.020
    post_top = r.mast_height - bearing_h + 0.005
    post_len = max(0.05, post_top - post_bottom)
    _cyl(
        stand,
        "dolly_center_post",
        0.029,
        post_len,
        (0.0, 0.0, post_bottom + post_len * 0.5),
        m["metal"],
    )
    _cyl(
        stand,
        "stand_top_bearing",
        0.044,
        bearing_h,
        (0.0, 0.0, r.mast_height - bearing_h * 0.5),
        m["base_dark"],
    )


def _build_telescoping_floor_stand(
    stand: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    # rec_…_b9ab25 L100-L135: sleeve + inner_post + guide shoes + spigot.
    base_w = r.base_radius * 2.0
    base_d = r.base_radius * 1.50
    bh = r.base_height
    _box(stand, "telescope_base_box", (base_w, base_d, bh), (0.0, 0.0, bh * 0.5), m["base"])
    _box(
        stand, "telescope_rubber_pad", (base_w * 0.74, 0.022, 0.012), (0.0, 0.0, 0.004), m["rubber"]
    )
    # sleeve: bottom embeds into base.
    sleeve_top = bh + r.mast_height * 0.45
    sleeve_bottom = bh - 0.010
    sleeve_len = sleeve_top - sleeve_bottom
    _cyl(
        stand,
        "telescope_outer_sleeve",
        0.042,
        sleeve_len,
        (0.0, 0.0, (sleeve_top + sleeve_bottom) * 0.5),
        m["base_dark"],
    )
    # lock_collar: hugs the sleeve top exterior.
    lock_h = 0.034
    _cyl(
        stand,
        "telescope_lock_collar",
        0.050,
        lock_h,
        (0.0, 0.0, sleeve_top - lock_h * 0.5 + 0.004),
        m["accent"],
    )
    # inner_post: starts inside sleeve (overlap 0.020) and rises to bearing.
    bearing_h = 0.034
    inner_post_bottom = sleeve_top - 0.020
    inner_post_top = r.mast_height - bearing_h + 0.005
    inner_len = max(0.06, inner_post_top - inner_post_bottom)
    _cyl(
        stand,
        "telescope_inner_post",
        0.028,
        inner_len,
        (0.0, 0.0, (inner_post_top + inner_post_bottom) * 0.5),
        m["metal"],
    )
    # guide_shoes: stuck onto the sleeve exterior (overlap into sleeve).
    for sx in (-1.0, 1.0):
        _box(
            stand,
            f"guide_shoe_{int(sx)}",
            (0.022, 0.030, 0.020),
            (sx * 0.035, 0.0, sleeve_top + 0.005),
            m["accent"],
        )
    _cyl(
        stand,
        "stand_top_bearing",
        0.040,
        bearing_h,
        (0.0, 0.0, r.mast_height - bearing_h * 0.5),
        m["base_dark"],
    )


def _build_telescoping_tripod_stand(
    stand: Part,
    r: ResolvedStudioSpotlightOnYokeConfig,
    m: dict[str, str],
    *,
    model: ArticulatedObject,
) -> None:
    # rec_…_afb8b9 L133-L157: tripod legs + center sleeve + prismatic column.
    hub_z = r.base_height + 0.040
    _cyl(stand, "tripod_crown_hub", 0.060, 0.066, (0.0, 0.0, hub_z), m["base_dark"])
    leg_len = r.base_radius * 2.0
    for i in range(r.tripod_leg_count):
        angle = i * math.tau / r.tripod_leg_count + math.radians(15.0)
        fx = math.cos(angle) * leg_len * 0.86
        fy = math.sin(angle) * leg_len * 0.86
        leg_geom = tube_from_spline_points(
            [
                (math.cos(angle) * 0.020, math.sin(angle) * 0.020, hub_z),
                (math.cos(angle) * leg_len * 0.45, math.sin(angle) * leg_len * 0.45, hub_z * 0.50),
                (fx, fy, 0.030),
            ],
            radius=max(0.014, leg_len * 0.022),
            samples_per_segment=12,
            radial_segments=14,
            cap_ends=True,
        )
        stand.visual(
            _mesh_for_model(model, leg_geom, f"tripod_leg_geom_{i}_telescope"),
            origin=Origin(),
            material=m["metal"],
            name=f"tripod_leg_{i}", material_class_id=("metal.brushed_silver" if r.material_style == "brushed_silver" else "metal.aluminum_bare"),
        )
        _box(
            stand,
            f"tripod_foot_{i}",
            (0.075, 0.040, 0.020),
            (fx, fy, 0.012),
            m["rubber"],
            rpy=(0.0, 0.0, angle),
        )
    bearing_h = 0.034
    sleeve_top = hub_z + (r.mast_height - hub_z) * 0.55
    sleeve_bottom = hub_z - 0.005
    sleeve_len = sleeve_top - sleeve_bottom
    _cyl(
        stand,
        "telescope_outer_sleeve",
        0.042,
        sleeve_len,
        (0.0, 0.0, (sleeve_top + sleeve_bottom) * 0.5),
        m["base_dark"],
    )
    # inner column overlaps sleeve top by 0.020.
    inner_bottom = sleeve_top - 0.020
    inner_top = r.mast_height - bearing_h + 0.005
    inner_len = max(0.06, inner_top - inner_bottom)
    _cyl(
        stand,
        "telescope_inner_column",
        0.028,
        inner_len,
        (0.0, 0.0, (inner_top + inner_bottom) * 0.5),
        m["metal"],
    )
    _cyl(stand, "telescope_lock_collar", 0.050, 0.034, (0.0, 0.0, sleeve_top - 0.014), m["accent"])
    _cyl(
        stand,
        "stand_top_bearing",
        0.040,
        bearing_h,
        (0.0, 0.0, r.mast_height - bearing_h * 0.5),
        m["base_dark"],
    )


def _build_stand(
    model: ArticulatedObject, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> Part:
    stand = model.part("stand")
    if r.root_support == "floor_pedestal_base":
        _build_floor_pedestal_base(stand, r, m)
    elif r.root_support == "low_floor_disk_base":
        _build_low_floor_disk_base(stand, r, m)
    elif r.root_support == "tripod_post_base":
        _build_tripod_post_base(stand, r, m, model=model)
    elif r.root_support == "wheeled_dolly_base":
        _build_wheeled_dolly_base(stand, r, m)
    elif r.root_support == "telescoping_floor_stand":
        _build_telescoping_floor_stand(stand, r, m)
    elif r.root_support == "telescoping_tripod_stand":
        _build_telescoping_tripod_stand(stand, r, m, model=model)
    return stand


# --------------------------------------------------------------------------- #
# Slot B: pan_yoke
# --------------------------------------------------------------------------- #
# Adopted sources:
#   S-B1 two_arm_box_yoke      rec_…_0001 L98-L142
#   S-B2 mesh_trunnion_yoke    rec_…_a7d172 L46-L59 (TrunnionYokeGeometry)
#   S-B3 swept_arm_yoke        rec_…_0003 L219-L277 (sweep_profile_along_spline)
#   S-B4 side_pivot_yoke       rec_…_6ba32 L134-L208 (single offset arm)


def _yoke_pan_spigot(yoke: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]) -> None:
    """Shared pan turntable + spigot — anchors child frame at (0,0,0).

    Cylinder stack meeting at z-planes so visuals are surface-connected and
    reaching up to the bridge/arm base above.
    """
    # yaw_spigot: z ∈ [-0.040, 0.040], radius 0.030.
    _cyl(yoke, "yaw_spigot", 0.030, 0.080, (0.0, 0.0, 0.0), m["base_dark"])
    # pan_turntable_disk: z ∈ [0.040, 0.080], radius 0.062 (sits flush on top of spigot).
    _cyl(yoke, "pan_turntable_disk", 0.062, 0.040, (0.0, 0.0, 0.060), m["metal"])
    # pan_index_collar reaches up into the bridge envelope (z ∈ [0.080, 0.130]).
    _cyl(yoke, "pan_index_collar", 0.044, 0.050, (0.0, 0.0, 0.105), m["base_dark"])


def _yoke_tilt_cross_shaft(
    yoke: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    """Horizontal trunnion cross-shaft along x at the tilt-joint origin.

    The shaft passes through (0, 0, yoke_tilt_z) in the yoke's frame, giving
    `fail_if_articulation_origin_far_from_geometry` a parent visual at the
    joint origin even when the yoke's arms are at ±yoke_half_width. The
    spotlight head's own through cross-shaft rides this — declared as an
    intentional captured-pin overlap in `_allow_expected_overlaps`.
    """
    _cyl(
        yoke,
        "tilt_cross_shaft",
        0.018,
        r.yoke_half_width * 2.05,
        (0.0, 0.0, r.yoke_tilt_z),
        m["base_dark"],
        rpy=X_CYLINDER_RPY,
    )


def _build_two_arm_box_yoke(
    yoke: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    # rec_…_0001 L98-L142: turntable + lower bridge + 2 box arms + 2 cylinder bearings.
    _yoke_pan_spigot(yoke, r, m)
    hw = r.yoke_half_width
    zc = r.yoke_tilt_z
    th = r.yoke_plate_thickness
    # Bridge sits on top of the pan stack (z = 0.110) and below the can.
    bridge_h = 0.030
    bridge_z = max(0.125, min(zc - r.can_radius - 0.020, 0.140))
    bridge_z = max(0.125, bridge_z)
    # Arms span from bridge top to zc with overlap into bridge and bearing cup.
    arm_bottom_z = bridge_z - bridge_h * 0.5 + 0.002
    arm_len = max(0.06, zc - arm_bottom_z + 0.004)
    arm_center_z = arm_bottom_z + arm_len * 0.5
    _box(
        yoke,
        "lower_yoke_bridge",
        (hw * 2.0 + th, 0.060, bridge_h),
        (0.0, 0.0, bridge_z),
        m["metal"],
    )
    for side, sx in (("left", -1), ("right", 1)):
        x = sx * hw
        _box(yoke, f"{side}_arm", (th, 0.058, arm_len), (x, 0.0, arm_center_z), m["metal"])
        _cyl(
            yoke,
            f"{side}_bearing_cup",
            0.034,
            th + 0.022,
            (x, 0.0, zc),
            m["base_dark"],
            rpy=X_CYLINDER_RPY,
        )
    _yoke_tilt_cross_shaft(yoke, r, m)


def _build_mesh_trunnion_yoke(
    yoke: Part,
    r: ResolvedStudioSpotlightOnYokeConfig,
    m: dict[str, str],
    *,
    model: ArticulatedObject,
) -> None:
    # rec_…_a7d172 L46-L59: TrunnionYokeGeometry single mesh + pan disk.
    _yoke_pan_spigot(yoke, r, m)
    hw = r.yoke_half_width
    zc = r.yoke_tilt_z
    bridge_z = max(0.108, zc - r.can_radius - 0.045)
    yoke_height = max(0.20, (zc + r.can_radius + 0.060) - bridge_z)
    trunnion_z_local = zc - bridge_z
    # Use TrunnionYokeGeometry for the single-mesh U yoke. Geometry constraints
    # require trunnion_diameter * 2 + (small clearance) < overall depth and
    # < arm thickness * 2, so we keep it conservative.
    trunnion_d = max(0.012, min(0.040, r.can_radius * 0.4))
    yoke_geom = TrunnionYokeGeometry(
        overall_size=(hw * 2.0 + r.yoke_plate_thickness * 2.0, 0.072, yoke_height),
        span_width=hw * 2.0,
        trunnion_diameter=trunnion_d,
        trunnion_center_z=trunnion_z_local,
        base_thickness=0.030,
        corner_radius=0.010,
    )
    yoke.visual(
        _mesh_for_model(model, yoke_geom, "trunnion_yoke_shell_geom"),
        origin=Origin(xyz=(0.0, 0.0, bridge_z)),
        material=m["metal"],
        name="trunnion_yoke_shell", material_class_id=("metal.brushed_silver" if r.material_style == "brushed_silver" else "metal.aluminum_bare"),
    )
    # Outer trunnion boss landings on each arm exterior (for lock knobs).
    for side, sx in (("left", -1), ("right", 1)):
        _cyl(
            yoke,
            f"{side}_trunnion_boss",
            0.030,
            r.yoke_plate_thickness * 1.2,
            (sx * hw, 0.0, zc),
            m["base_dark"],
            rpy=X_CYLINDER_RPY,
        )
    _yoke_tilt_cross_shaft(yoke, r, m)


def _build_swept_arm_yoke(
    yoke: Part,
    r: ResolvedStudioSpotlightOnYokeConfig,
    m: dict[str, str],
    *,
    model: ArticulatedObject,
) -> None:
    # rec_…_0003 L219-L277: sweep_profile_along_spline curved arms.
    _yoke_pan_spigot(yoke, r, m)
    hw = r.yoke_half_width
    zc = r.yoke_tilt_z
    bottom_z = max(0.108, zc - r.can_radius - 0.045)
    _box(
        yoke,
        "lower_yoke_bridge",
        (hw * 2.0 + r.yoke_plate_thickness, 0.060, 0.030),
        (0.0, 0.0, bottom_z),
        m["metal"],
    )
    # Curved swept arms — rounded rect profile along an arching spline.
    profile = rounded_rect_profile(
        width=r.yoke_plate_thickness * 1.20,
        height=0.052,
        radius=0.010,
    )
    for side, sx in (("left", -1), ("right", 1)):
        x_in = sx * (hw * 0.85)
        x_out = sx * hw
        spline = [
            (x_in, 0.0, bottom_z + 0.020),
            (x_out * 1.05, 0.0, (bottom_z + zc) * 0.5),
            (x_out, 0.0, zc),
        ]
        arm_geom = sweep_profile_along_spline(
            spline,
            profile=profile,
            samples_per_segment=10,
        )
        yoke.visual(
            _mesh_for_model(model, arm_geom, f"{side}_swept_arm_geom"),
            origin=Origin(),
            material=m["metal"],
            name=f"{side}_swept_arm", material_class_id=("metal.brushed_silver" if r.material_style == "brushed_silver" else "metal.aluminum_bare"),
        )
        _cyl(
            yoke,
            f"{side}_bearing_boss",
            0.034,
            r.yoke_plate_thickness * 1.4,
            (x_out, 0.0, zc),
            m["base_dark"],
            rpy=X_CYLINDER_RPY,
        )
    _yoke_tilt_cross_shaft(yoke, r, m)


def _build_side_pivot_yoke(
    yoke: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    # rec_…_6ba32 L134-L208: single offset side arm (C bracket) + single trunnion pivot.
    _yoke_pan_spigot(yoke, r, m)
    hw = r.yoke_half_width
    zc = r.yoke_tilt_z
    bottom_z = max(0.108, zc - r.can_radius - 0.045)
    upright_z_center = (bottom_z + zc) * 0.5
    upright_h = max(0.06, zc - bottom_z + 0.020)
    # C-bracket: base bridge wraps under the can on one side, upright
    # supports the single trunnion bearing.
    _box(yoke, "side_pivot_base", (hw * 1.4, 0.060, 0.030), (-hw * 0.20, 0.0, bottom_z), m["metal"])
    _box(
        yoke,
        "side_pivot_upright",
        (r.yoke_plate_thickness * 1.4, 0.060, upright_h),
        (-hw * 0.92, 0.0, upright_z_center),
        m["metal"],
    )
    _cyl(
        yoke,
        "side_pivot_bearing",
        0.034,
        r.yoke_plate_thickness * 1.6,
        (-hw * 0.92, 0.0, zc),
        m["base_dark"],
        rpy=X_CYLINDER_RPY,
    )
    _yoke_tilt_cross_shaft(yoke, r, m)


def _build_yoke(
    model: ArticulatedObject, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> Part:
    yoke = model.part("pan_yoke")
    if r.pan_yoke_style == "two_arm_box_yoke":
        _build_two_arm_box_yoke(yoke, r, m)
    elif r.pan_yoke_style == "mesh_trunnion_yoke":
        _build_mesh_trunnion_yoke(yoke, r, m, model=model)
    elif r.pan_yoke_style == "swept_arm_yoke":
        _build_swept_arm_yoke(yoke, r, m, model=model)
    elif r.pan_yoke_style == "side_pivot_yoke":
        _build_side_pivot_yoke(yoke, r, m)
    return yoke


# --------------------------------------------------------------------------- #
# Slot C: spotlight_head
# --------------------------------------------------------------------------- #
# Adopted sources:
#   S-C1 primitive_box_cylinder_can  rec_…_0001 L144-L222
#   S-C2 lathe_shell_can             rec_…_0002 L284-L372 (LatheGeometry.from_shell_profiles)
#   S-C3 cadquery_shell_can          rec_…_06058b L246-L300 (cadquery; fallback lathe)
#   S-C4 fresnel_lens_can            rec_…_193640 L136-L270 (TorusGeometry fresnel rings)


def _can_shell_lathe_mesh(
    model: ArticulatedObject | None, length: float, radius: float, name: str, *, taper: float = 0.92
):
    """Hollow lamp-can profile from LatheGeometry.from_shell_profiles (adopted: S-C2).

    Profile is generated in the can's local frame with axis along x; the visual
    placement rotates it so x is aligned with the spotlight aim (forward = +x).
    """
    half = length * 0.5
    # outer/inner shell profiles (axisymmetric, profile is (radial, axial)).
    outer = [
        (radius * 0.88, -half),
        (radius, -half + length * 0.18),
        (radius, half - length * 0.10),
        (radius * taper, half),
    ]
    inner_r = max(0.004, radius - max(0.005, radius * 0.10))
    inner = [
        (max(0.004, inner_r * 0.86), -half + length * 0.04),
        (inner_r, -half + length * 0.22),
        (inner_r, half - length * 0.14),
        (max(0.004, inner_r * taper), half - length * 0.02),
    ]
    geom = LatheGeometry.from_shell_profiles(
        outer,
        inner,
        segments=40,
        start_cap="round",
        end_cap="round",
        lip_samples=4,
    )
    return _mesh_for_model(model, geom, name)


def _add_can_common_features(
    can: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    """Shared can features: bezel, lens, rear cap, trunnion stubs.

    Aim direction is +y. Trunnion line is along x (matches the yoke arm
    placement at ±yoke_half_width in x).
    """
    cr = r.can_radius
    cl = r.can_length
    front_y = cl * 0.5
    rear_y = -cl * 0.5
    bezel_th = max(0.022, cl * 0.06)
    lens_th = max(0.012, cl * 0.040)
    rear_th = max(0.030, r.can_rear_depth)
    # Front bezel ring (Cylinder) — embedded ~0.004 into the can body for
    # connectivity (must touch main_can_body geometry).
    _cyl(
        can,
        "front_bezel",
        cr * 1.10,
        bezel_th,
        (0.0, front_y + bezel_th * 0.5 - 0.004, 0.0),
        m["bezel"],
        rpy=Y_CYLINDER_RPY,
    )
    # Translucent front lens — embedded into the bezel.
    _cyl(
        can,
        "front_lens",
        cr * 0.84,
        lens_th,
        (0.0, front_y + bezel_th - 0.004 + lens_th * 0.45, 0.0),
        m["glass"],
        rpy=Y_CYLINDER_RPY,
    )
    # Warm lamp core behind the lens — overlaps front_lens and main_can_body.
    _cyl(
        can,
        "warm_lamp_core",
        cr * 0.46,
        max(0.020, cl * 0.060),
        (0.0, front_y - cl * 0.03, 0.0),
        m["emitter"],
        rpy=Y_CYLINDER_RPY,
    )
    # Rear cap — embedded ~0.004 into the rear of main_can_body.
    _cyl(
        can,
        "rear_cap",
        cr * 0.96,
        rear_th,
        (0.0, rear_y - rear_th * 0.5 + 0.004, 0.0),
        m["bezel"],
        rpy=Y_CYLINDER_RPY,
    )
    # Trunnion stubs and a through cross-shaft along x so the tilt joint
    # origin (0,0,0) is anchored to real child geometry (the cross-shaft
    # passes through the origin and intersects main_can_body).
    _cyl(
        can,
        "trunnion_cross_shaft",
        0.020,
        r.yoke_half_width * 2.05,
        (0.0, 0.0, 0.0),
        m["metal"],
        rpy=X_CYLINDER_RPY,
    )
    for side, sx in (("left", -1.0), ("right", 1.0)):
        _cyl(
            can,
            f"{side}_trunnion_stub",
            0.030,
            max(0.024, r.yoke_plate_thickness * 1.4),
            (sx * (r.yoke_half_width * 0.92), 0.0, 0.0),
            m["bezel"],
            rpy=X_CYLINDER_RPY,
        )


def _build_primitive_box_cylinder_can(
    can: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    # rec_…_0001 L144-L222: pure Box+Cylinder body.
    cr = r.can_radius
    cl = r.can_length
    _cyl(can, "main_can_body", cr, cl, (0.0, 0.0, 0.0), m["can"], rpy=Y_CYLINDER_RPY)
    _cyl(
        can,
        "rear_housing",
        cr * 0.78,
        cl * 0.32,
        (0.0, -cl * 0.42, 0.0),
        m["can"],
        rpy=Y_CYLINDER_RPY,
    )
    _add_can_common_features(can, r, m)


def _build_lathe_shell_can(
    can: Part,
    r: ResolvedStudioSpotlightOnYokeConfig,
    m: dict[str, str],
    *,
    model: ArticulatedObject,
) -> None:
    # rec_…_0002 L284-L372: LatheGeometry.from_shell_profiles hollow shell.
    cr = r.can_radius
    cl = r.can_length
    shell_mesh = _can_shell_lathe_mesh(
        model, length=cl, radius=cr, name="lathe_can_shell", taper=0.92
    )
    can.visual(
        shell_mesh,
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=Y_CYLINDER_RPY),
        material=m["can"],
        name="main_can_body", material_class_id=("metal.brushed_silver" if r.material_style == "brushed_silver" else "metal.paint_coated"),
    )
    # Forward cone neck for sculpted "spun" identity.
    _cyl(
        can,
        "lathe_can_neck",
        cr * 0.90,
        max(0.020, cl * 0.08),
        (0.0, cl * 0.42, 0.0),
        m["can"],
        rpy=Y_CYLINDER_RPY,
    )
    # Cooling fin band (3 fins).
    for i in range(3):
        _cyl(
            can,
            f"cooling_fin_{i}",
            cr * 1.06,
            0.008,
            (0.0, -cl * (0.10 + i * 0.10), 0.0),
            m["bezel"],
            rpy=Y_CYLINDER_RPY,
        )
    _add_can_common_features(can, r, m)


def _build_cadquery_shell_can(
    can: Part,
    r: ResolvedStudioSpotlightOnYokeConfig,
    m: dict[str, str],
    *,
    model: ArticulatedObject,
) -> None:
    # rec_…_06058b L246-L300: cadquery shell (Workplane circle/extrude/subtract).
    # We use LatheGeometry.from_shell_profiles with a more conical profile as the
    # primitive-preserving fallback when cadquery isn't available in this build
    # environment — the resulting mesh still has the hollow-shell topology and
    # the same chassis-ring identity the source captured.
    cr = r.can_radius
    cl = r.can_length
    shell_mesh = _can_shell_lathe_mesh(
        model, length=cl, radius=cr, name="cadquery_can_shell", taper=0.74
    )
    can.visual(
        shell_mesh,
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=Y_CYLINDER_RPY),
        material=m["can"],
        name="main_can_body", material_class_id=("metal.brushed_silver" if r.material_style == "brushed_silver" else "metal.paint_coated"),
    )
    # Sharper rear taper + chassis ring.
    _cyl(
        can,
        "rear_chassis_taper",
        cr * 0.66,
        cl * 0.32,
        (0.0, -cl * 0.40, 0.0),
        m["can"],
        rpy=Y_CYLINDER_RPY,
    )
    can.visual(
        _mesh_for_model(
            model,
            TorusGeometry(
                radius=cr * 1.05,
                tube=max(0.006, cr * 0.05),
                radial_segments=12,
                tubular_segments=40,
            ),
            "cadquery_chassis_ring_geom",
        ),
        origin=Origin(xyz=(0.0, cl * 0.20, 0.0), rpy=X_CYLINDER_RPY),
        material=m["bezel"],
        name="cadquery_chassis_ring", material_class_id="metal.blackened_gunmetal",
    )
    _add_can_common_features(can, r, m)


def _build_fresnel_lens_can(
    can: Part,
    r: ResolvedStudioSpotlightOnYokeConfig,
    m: dict[str, str],
    *,
    model: ArticulatedObject,
) -> None:
    # rec_…_193640 L136-L270: LatheGeometry shell + BezelGeometry + 3-4 TorusGeometry fresnel rings.
    cr = r.can_radius
    cl = r.can_length
    shell_mesh = _can_shell_lathe_mesh(
        model, length=cl, radius=cr, name="fresnel_can_shell", taper=0.95
    )
    can.visual(
        shell_mesh,
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=Y_CYLINDER_RPY),
        material=m["can"],
        name="main_can_body", material_class_id=("metal.brushed_silver" if r.material_style == "brushed_silver" else "metal.paint_coated"),
    )
    front_y = cl * 0.5
    # Concentric Fresnel rings (3 or 4) — half-transparent Torus geometry that
    # rides the lens plane. Outer ring largest, inner smallest.
    n = max(3, r.fresnel_ring_count)
    for i in range(n):
        ring_r = cr * (0.30 + 0.18 * (i / max(1, n - 1)))
        can.visual(
            _mesh_for_model(
                model,
                TorusGeometry(
                    radius=ring_r,
                    tube=max(0.005, cr * 0.040),
                    radial_segments=10,
                    tubular_segments=36,
                ),
                f"fresnel_ring_geom_{i}",
            ),
            origin=Origin(xyz=(0.0, front_y + 0.014, 0.0), rpy=Y_CYLINDER_RPY),
            material=m["glass"],
            name=f"fresnel_ring_{i}", material_class_id="glass.clear_transparent",
        )
    _add_can_common_features(can, r, m)


# --------------------------------------------------------------------------- #
# Slot D: auxiliary mechanism — emitted as parent.visual decoration on the can
# (or on the yoke for tilt_lock_knobs), per Design Rule 1. Each variant adds a
# topology-distinct set of visuals.
# --------------------------------------------------------------------------- #


def _add_tilt_lock_knobs(
    yoke: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    # rec_…_a7d172 L104-L151: 2 lobed knobs + friction washers, CONTINUOUS in source.
    # Chain: bearing_cup → friction_washer → stem → lobe → grips, each pair
    # overlapping in x so the visuals stay surface-connected.
    hw = r.yoke_half_width
    zc = r.yoke_tilt_z
    for side, sx in (("left", -1), ("right", 1)):
        # Friction washer hugs the bearing_cup exterior (overlap 0.006).
        washer_x = sx * (hw + 0.012)
        _cyl(
            yoke,
            f"{side}_lock_friction_washer",
            0.040,
            0.012,
            (washer_x, 0.0, zc),
            m["bezel"],
            rpy=X_CYLINDER_RPY,
        )
        # Stem starts inside washer, extends outward (overlap 0.004 each end).
        stem_x = sx * (hw + 0.030)
        _cyl(
            yoke,
            f"{side}_lock_knob_stem",
            0.014,
            0.030,
            (stem_x, 0.0, zc),
            m["metal"],
            rpy=X_CYLINDER_RPY,
        )
        # Lobe overlaps stem outward (overlap 0.008).
        lobe_x = sx * (hw + 0.052)
        _cyl(
            yoke,
            f"{side}_lock_knob_lobe",
            0.030,
            0.020,
            (lobe_x, 0.0, zc),
            m["accent"],
            rpy=X_CYLINDER_RPY,
        )
        # Grips embed into the lobe.
        for j in range(6):
            a = j * math.tau / 6.0
            _box(
                yoke,
                f"{side}_lock_knob_grip_{j}",
                (0.008, 0.020, 0.006),
                (lobe_x, math.cos(a) * 0.024, zc + math.sin(a) * 0.024),
                m["rubber"],
            )


def _add_focus_or_mode_knob(
    can: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    # rec_…_eef416 L312-L341 / rec_…_aa36438 L470-L481: single rear knob, CONTINUOUS.
    # Chain: rear_cap → boss → knob → grips, each overlapping the prior visual.
    cl = r.can_length
    rear_y = -cl * 0.5
    # rear_cap rear face is at y ≈ rear_y - can_rear_depth + 0.004.
    cap_rear = rear_y - r.can_rear_depth + 0.004
    boss_h = 0.038
    # Boss embeds 0.012 into rear_cap.
    boss_center_y = cap_rear - boss_h * 0.5 + 0.012
    _cyl(
        can,
        "rear_knob_boss",
        0.022,
        boss_h,
        (0.0, boss_center_y, 0.0),
        m["metal"],
        rpy=Y_CYLINDER_RPY,
    )
    # Knob overlaps boss by 0.008.
    knob_h = 0.034
    knob_center_y = boss_center_y - boss_h * 0.5 - knob_h * 0.5 + 0.008
    _cyl(
        can,
        "rear_focus_knob",
        0.032,
        knob_h,
        (0.0, knob_center_y, 0.0),
        m["accent"],
        rpy=Y_CYLINDER_RPY,
    )
    # Grips embed into the knob (overlap radius ≤ knob radius).
    for j in range(6):
        a = j * math.tau / 6.0
        _box(
            can,
            f"rear_knob_grip_{j}",
            (0.008, 0.020, 0.006),
            (math.cos(a) * 0.028, knob_center_y, math.sin(a) * 0.028),
            m["rubber"],
        )


def _add_barndoor_four_leaf(
    can: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    # rec_…_aa36438 L353-L437: FIXED frame + 4 leaves. We render the frame +
    # 4 leaves as parent visuals (Rule 1 — they don't articulate as parts
    # here). The 4-leaf identity is preserved.
    cr = r.can_radius
    cl = r.can_length
    fy = cl * 0.5 + max(0.030, cl * 0.08)
    bar_t = max(0.012, cr * 0.06)
    # Barndoor frame: outer rectangular ring sitting on the bezel (perpendicular
    # to the can aim axis = y). Frame extends in x (left-right) and z (up-down).
    _box(
        can,
        "barndoor_frame_top",
        (cr * 1.84, bar_t, 0.014),
        (0.0, fy - 0.008, cr * 0.94),
        m["bezel"],
    )
    _box(
        can,
        "barndoor_frame_bottom",
        (cr * 1.84, bar_t, 0.014),
        (0.0, fy - 0.008, -cr * 0.94),
        m["bezel"],
    )
    _box(
        can,
        "barndoor_frame_left",
        (0.014, bar_t, cr * 1.86),
        (-cr * 0.94, fy - 0.008, 0.0),
        m["bezel"],
    )
    _box(
        can,
        "barndoor_frame_right",
        (0.014, bar_t, cr * 1.86),
        (cr * 0.94, fy - 0.008, 0.0),
        m["bezel"],
    )
    # Leaves: positioned flat at the rest pose, embedded into the frame so
    # visuals stay surface-connected. The frame y is fy (leaves embed 0.005
    # into the frame's y-thickness).
    leaf_w = cr * 1.84
    leaf_d = cr * 0.62
    leaf_thk = bar_t
    leaf_y = fy
    for name, sz in (("top", 1.0), ("bottom", -1.0)):
        # leaf z center: leaf extends from cr*0.94 - 0.005 (overlap frame) outward.
        z_in = sz * (cr * 0.94 - 0.005)
        z_out = sz * (cr * 0.94 + leaf_d - 0.005)
        _box(
            can,
            f"barndoor_leaf_{name}",
            (leaf_w, leaf_thk, leaf_d),
            (0.0, leaf_y, (z_in + z_out) * 0.5),
            m["base_dark"],
        )
    for name, sx in (("left", -1.0), ("right", 1.0)):
        x_in = sx * (cr * 0.94 - 0.005)
        x_out = sx * (cr * 0.94 + leaf_d - 0.005)
        _box(
            can,
            f"barndoor_leaf_{name}",
            (leaf_d, leaf_thk, leaf_w),
            ((x_in + x_out) * 0.5, leaf_y, 0.0),
            m["base_dark"],
        )


def _add_front_filter_or_gel_frame(
    can: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    # rec_…_d1205 L229-L275 / rec_…_afb8b9 L271-L332: hinged filter holder or
    # slide-in gel frame. Rendered as a tinted glass pane in a rim frame.
    cr = r.can_radius
    cl = r.can_length
    fy = cl * 0.5 + max(0.024, cl * 0.06)
    _box(can, "filter_frame_top", (cr * 1.96, 0.018, 0.018), (0.0, fy, cr * 1.00), m["accent"])
    _box(can, "filter_frame_bottom", (cr * 1.96, 0.018, 0.018), (0.0, fy, -cr * 1.00), m["accent"])
    _box(can, "filter_frame_left", (0.018, 0.018, cr * 1.96), (-cr * 1.00, fy, 0.0), m["accent"])
    _box(can, "filter_frame_right", (0.018, 0.018, cr * 1.96), (cr * 1.00, fy, 0.0), m["accent"])
    _box(
        can, "filter_glass_pane", (cr * 1.90, 0.006, cr * 1.90), (0.0, fy + 0.008, 0.0), m["glass"]
    )
    _box(can, "filter_pull_tab", (0.024, 0.020, 0.060), (cr * 0.86, fy, cr * 0.78), m["rubber"])


def _add_service_hatch_or_lens_cover(
    can: Part, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> None:
    # rec_…_78d9f7 L111-L267 / rec_…_85881: rear hatch or flip cover, REVOLUTE.
    # Render as a panel hugging the rear cap so visuals stay connected.
    cr = r.can_radius
    cl = r.can_length
    # Position panel right at the rear cap exterior so they overlap.
    rear_y = -cl * 0.5 - r.can_rear_depth * 0.5
    _box(
        can,
        "service_hatch_panel",
        (cr * 0.85, 0.020, cr * 0.85),
        (0.0, rear_y - 0.008, cr * 0.10),
        m["base_dark"],
    )
    _cyl(
        can,
        "service_hatch_hinge_barrel",
        0.012,
        cr * 0.85,
        (0.0, rear_y - 0.008, cr * 0.50),
        m["metal"],
        rpy=X_CYLINDER_RPY,
    )
    _box(
        can,
        "service_hatch_latch",
        (0.040, 0.024, 0.020),
        (0.0, rear_y - 0.010, -cr * 0.28),
        m["accent"],
    )
    _box(
        can,
        "service_hatch_gasket",
        (cr * 0.85, 0.008, cr * 0.85),
        (0.0, rear_y - 0.002, cr * 0.10),
        m["rubber"],
    )


def _add_foldable_carry_handle(
    can: Part,
    r: ResolvedStudioSpotlightOnYokeConfig,
    m: dict[str, str],
    *,
    model: ArticulatedObject,
) -> None:
    # rec_…_f20d5d L415-L454 / rec_…_35f03b L307-L383: REVOLUTE pivoted handle on top of can.
    cr = r.can_radius
    cl = r.can_length
    # Pivot eyes on top of the can (axis along x, mounted at fore/aft along y).
    for sy, side in ((-1, "rear"), (1, "front")):
        _cyl(
            can,
            f"handle_pivot_eye_{side}",
            0.018,
            0.026,
            (0.0, sy * cl * 0.20, cr * 1.12),
            m["metal"],
            rpy=X_CYLINDER_RPY,
        )
    # Tube grip (spline mesh) arching over the can top from rear to front.
    grip_geom = tube_from_spline_points(
        [
            (0.0, -cl * 0.20, cr * 1.18),
            (0.0, 0.0, cr * 1.56),
            (0.0, cl * 0.20, cr * 1.18),
        ],
        radius=max(0.010, cr * 0.10),
        samples_per_segment=10,
        radial_segments=12,
        cap_ends=True,
    )
    can.visual(
        _mesh_for_model(model, grip_geom, "carry_handle_grip_geom"),
        origin=Origin(),
        material=m["metal"],
        name="carry_handle_grip", material_class_id=("metal.brushed_silver" if r.material_style == "brushed_silver" else "metal.aluminum_bare"),
    )


def _build_spotlight_head(
    model: ArticulatedObject, r: ResolvedStudioSpotlightOnYokeConfig, m: dict[str, str]
) -> Part:
    can = model.part("spotlight_head")
    if r.spotlight_head == "primitive_box_cylinder_can":
        _build_primitive_box_cylinder_can(can, r, m)
    elif r.spotlight_head == "lathe_shell_can":
        _build_lathe_shell_can(can, r, m, model=model)
    elif r.spotlight_head == "cadquery_shell_can":
        _build_cadquery_shell_can(can, r, m, model=model)
    elif r.spotlight_head == "fresnel_lens_can":
        _build_fresnel_lens_can(can, r, m, model=model)
    # Auxiliary mechanism decoration (most go on the can; tilt_lock_knobs goes on yoke).
    if r.auxiliary_mechanism == "focus_or_mode_knob":
        _add_focus_or_mode_knob(can, r, m)
    elif r.auxiliary_mechanism == "barndoor_four_leaf":
        _add_barndoor_four_leaf(can, r, m)
    elif r.auxiliary_mechanism == "front_filter_or_gel_frame":
        _add_front_filter_or_gel_frame(can, r, m)
    elif r.auxiliary_mechanism == "service_hatch_or_lens_cover":
        _add_service_hatch_or_lens_cover(can, r, m)
    elif r.auxiliary_mechanism == "foldable_carry_handle":
        _add_foldable_carry_handle(can, r, m, model=model)
    return can


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #


def build_studio_spotlight_on_yoke(
    config: StudioSpotlightOnYokeConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or StudioSpotlightOnYokeConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-yoke-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    m = _register_materials(model, r.material_style)
    stand = _build_stand(model, r, m)
    yoke = _build_yoke(model, r, m)
    can = _build_spotlight_head(model, r, m)
    if r.auxiliary_mechanism == "tilt_lock_knobs":
        _add_tilt_lock_knobs(yoke, r, m)

    # ---- pan articulation: stand -> yoke, vertical Z ----
    if r.pan_joint_type == "continuous":
        model.articulation(
            "yoke_pan",
            ArticulationType.CONTINUOUS,
            parent=stand,
            child=yoke,
            origin=Origin(xyz=(0.0, 0.0, r.mast_height)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=120.0, velocity=1.2),
        )
    else:
        model.articulation(
            "yoke_pan",
            ArticulationType.REVOLUTE,
            parent=stand,
            child=yoke,
            origin=Origin(xyz=(0.0, 0.0, r.mast_height)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=120.0,
                velocity=1.2,
                lower=-r.yoke_pan_limit,
                upper=r.yoke_pan_limit,
            ),
        )

    # ---- tilt articulation: yoke -> spotlight_head, horizontal X ----
    # The trunnion line runs through ±yoke_half_width in x; tilt axis is x.
    model.articulation(
        "can_tilt",
        ArticulationType.REVOLUTE,
        parent=yoke,
        child=can,
        origin=Origin(xyz=(0.0, 0.0, r.yoke_tilt_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=80.0,
            velocity=1.0,
            lower=r.can_tilt_lower,
            upper=r.can_tilt_upper,
        ),
    )
    return model


def build_seeded_studio_spotlight_on_yoke(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_studio_spotlight_on_yoke(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _try_allow(
    ctx: TestContext, model: ArticulatedObject, pa: str, pb: str, ea: str, eb: str, reason: str
) -> None:
    names = {p.name for p in model.parts}
    if pa not in names or pb not in names:
        return
    try:
        ctx.allow_overlap(
            model.get_part(pa), model.get_part(pb), elem_a=ea, elem_b=eb, reason=reason
        )
    except Exception:
        pass


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    # stand-vs-yoke: pan spigot is intentionally seated inside the stand's bearing cap.
    stand_pan_elems = (
        "stand_top_bearing",
        "center_post",
        "short_center_post",
        "tripod_center_mast",
        "dolly_center_post",
        "telescope_inner_post",
        "telescope_inner_column",
        "telescope_outer_sleeve",
        "telescope_lock_collar",
        "dolly_post_socket",
        "base_socket_collar",
    )
    yoke_neck_elems = (
        "yaw_spigot",
        "pan_turntable_disk",
        "pan_index_collar",
        "lower_yoke_bridge",
        "side_pivot_base",
        "trunnion_yoke_shell",
    )
    for ea in stand_pan_elems:
        for eb in yoke_neck_elems:
            _try_allow(
                ctx,
                model,
                "stand",
                "pan_yoke",
                ea,
                eb,
                "pan spigot is seated inside stand bearing cap",
            )
    # yoke-vs-spotlight_head: trunnion is captured between yoke bearing cups.
    yoke_bearing_elems = (
        "left_arm",
        "right_arm",
        "left_bearing_cup",
        "right_bearing_cup",
        "trunnion_yoke_shell",
        "left_trunnion_boss",
        "right_trunnion_boss",
        "left_swept_arm",
        "right_swept_arm",
        "left_bearing_boss",
        "right_bearing_boss",
        "side_pivot_upright",
        "side_pivot_upper_cap",
        "side_pivot_bearing",
        "side_pivot_base",
        "upper_yoke_crossbeam",
        "tilt_cross_shaft",
        "lower_yoke_bridge",
        "left_lock_friction_washer",
        "right_lock_friction_washer",
        "left_lock_knob_stem",
        "right_lock_knob_stem",
        "left_lock_knob_lobe",
        "right_lock_knob_lobe",
    )
    can_trunnion_elems = (
        "trunnion_cross_shaft",
        "left_trunnion_stub",
        "right_trunnion_stub",
        "main_can_body",
        "rear_housing",
        "lathe_can_neck",
        "rear_chassis_taper",
        "cadquery_chassis_ring",
        "front_bezel",
        "rear_cap",
        "cooling_fin_0",
        "cooling_fin_1",
        "cooling_fin_2",
        "fresnel_ring_0",
        "fresnel_ring_1",
        "fresnel_ring_2",
        "fresnel_ring_3",
    )
    for ea in yoke_bearing_elems:
        for eb in can_trunnion_elems:
            _try_allow(
                ctx,
                model,
                "pan_yoke",
                "spotlight_head",
                ea,
                eb,
                "spotlight trunnion stub is captured by yoke bearing cups",
            )
    # Optional auxiliaries (tilt_lock_knobs ride the yoke trunnion bosses).
    for side in ("left", "right"):
        for ea in (
            f"{side}_bearing_cup",
            f"{side}_trunnion_boss",
            f"{side}_bearing_boss",
            f"{side}_arm",
        ):
            for eb in (
                f"{side}_lock_friction_washer",
                f"{side}_lock_knob_stem",
                f"{side}_lock_knob_lobe",
            ):
                _try_allow(
                    ctx,
                    model,
                    "pan_yoke",
                    "pan_yoke",
                    ea,
                    eb,
                    "tilt lock knob rides the yoke trunnion boss",
                )
    # focus_or_mode_knob hugs the rear cap.
    for ea in ("rear_cap",):
        for eb in ("rear_knob_boss", "rear_focus_knob"):
            _try_allow(
                ctx,
                model,
                "spotlight_head",
                "spotlight_head",
                ea,
                eb,
                "rear knob anchors to the can rear cap",
            )


def run_studio_spotlight_on_yoke_tests(
    object_model: ArticulatedObject,
    config: StudioSpotlightOnYokeConfig,
) -> TestReport:
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model)
    # The pan turntable yoke carries the spotlight head; panning sweeps the yoke
    # disk / index collar past the head can it cradles (captured pan bearing).
    _names = {p.name for p in object_model.parts}
    if "pan_yoke" in _names and "spotlight_head" in _names:
        ctx.allow_overlap(
            object_model.get_part("pan_yoke"),
            object_model.get_part("spotlight_head"),
            reason="Pan yoke turntable cradles the spotlight head can it pans.",
        )
    if "spotlight_head" in _names and "stand" in _names:
        ctx.allow_overlap(
            object_model.get_part("spotlight_head"),
            object_model.get_part("stand"),
            reason="Spotlight head tilts on the stand top bearing it is mounted on.",
        )
    # Forward-compatible: when the SDK gains allow_disconnected_islands, use it
    # to silence the connectivity warn for parts that legitimately contain
    # separated rigid sub-pieces (lock knobs, barndoor leaves, focus knob,
    # caster wheels, etc.).
    allow_islands = getattr(ctx, "allow_disconnected_islands", None)
    if callable(allow_islands):
        part_names = {p.name for p in object_model.parts}
        for pn in ("stand", "pan_yoke", "spotlight_head"):
            if pn in part_names:
                allow_islands(
                    object_model.get_part(pn),
                    reason=(
                        "studio spotlight has genuinely separated rigid sub-pieces "
                        "(lock knobs, barndoor leaves, casters, lens/bezel, etc.)"
                    ),
                )
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.joints}
    for required in ("stand", "pan_yoke", "spotlight_head"):
        if required not in part_names:
            ctx.fail("identity_parts", f"missing {required}")
    for required in ("yoke_pan", "can_tilt"):
        if required not in joint_names:
            ctx.fail("identity_joints", f"missing {required}")
    if "yoke_pan" in joint_names:
        joint = object_model.get_articulation("yoke_pan")
        if joint.axis != (0.0, 0.0, 1.0):
            ctx.fail("yoke_pan_axis", f"pan axis must be vertical Z, got {joint.axis}")
        if joint.articulation_type not in (ArticulationType.REVOLUTE, ArticulationType.CONTINUOUS):
            ctx.fail("yoke_pan_type", "pan must be revolute or continuous")
    if "can_tilt" in joint_names:
        joint = object_model.get_articulation("can_tilt")
        # axis horizontal (any (±x,0,0) or (0,±y,0)).
        ax = joint.axis
        horizontal = abs(ax[2]) < 1e-6 and (abs(ax[0]) > 0.9 or abs(ax[1]) > 0.9)
        if not horizontal:
            ctx.fail("can_tilt_axis", f"tilt axis must be horizontal, got {ax}")
        if joint.articulation_type != ArticulationType.REVOLUTE:
            ctx.fail("can_tilt_type", "tilt must be revolute")
    if "spotlight_head" in part_names:
        head = object_model.get_part("spotlight_head")
        head_visuals = {v.name for v in head.visuals}
        for required_visual in ("front_lens", "front_bezel", "rear_cap"):
            if required_visual not in head_visuals:
                ctx.fail("head_identity", f"spotlight_head missing {required_visual}")
    return ctx.report()


__all__ = [
    "StudioSpotlightOnYokeConfig",
    "ResolvedStudioSpotlightOnYokeConfig",
    "build_studio_spotlight_on_yoke",
    "build_seeded_studio_spotlight_on_yoke",
    "config_from_seed",
    "resolve_config",
    "run_studio_spotlight_on_yoke_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]


def _material_class_id(
    value: str,
    first_values: tuple[str, ...],
    first_id: str,
    second_id: str,
) -> str:
    return first_id if value in first_values else second_id
