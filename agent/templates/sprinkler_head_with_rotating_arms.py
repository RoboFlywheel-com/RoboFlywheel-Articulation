# SPDX-License-Identifier: Apache-2.0

"""Sprinkler head with rotating arms — modular parametric template.

A garden sprinkler head = a stationary base (Slot A: perforated disk / threaded
brass pillar / wheeled cart / tripod / ground spike) carrying a rotor around a
vertical central bearing (Slot B: straight radial / curved-S reaction / tapered
upsweep arm form). N radial arms (2/3/4) extend from the rotor at 2π/N spacing,
each with M end nozzles (1/2). Slot C decides whether nozzles are inline visuals
on the rotor (fixed_inline) or separate REVOLUTE-jointed parts (revolute_pivot).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/sprinkler_head_with_rotating_arms.md``
and the 11 5-star sprinkler_head_with_rotating_arms records (3 origin anchors
S1-S3 + 8 forked variants S4-S11) synced under ``data/records/``.

Design notes:
- Structure derives from 5-star sources: LatheGeometry / tube_from_spline_points
  drive the arm form family; simple Cylinder/Box primitives model bases where
  the source uses them at that granularity (tripod legs, spike shaft).
- Not using ``_modular.assemble``: the base↔rotor and per-arm↔nozzle joints
  are conditional on Slot A/B/C combinations, so we build in a single function
  with explicit MatingContract on every non-FIXED joint (Rule 2).
- Palette drives every ``.visual(..., material=mats[...])`` via 5 realistic
  colorways from the source records.
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
    LatheGeometry,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot literals
# ---------------------------------------------------------------------------
BaseForm = Literal[
    "perforated_disk_base",
    "threaded_pillar_base",
    "wheeled_cart_base",
    "tripod_base",
    "ground_spike_base",
]
ArmForm = Literal["straight_radial_tube", "curved_s_reaction", "tapered_upsweep"]
NozzleStyle = Literal["fixed_inline_nozzles", "revolute_pivot_nozzles"]
PaletteStyle = Literal[
    "gunmetal_silver_orange",
    "warm_brass_amber",
    "green_cast_brass",
    "black_plastic_orange",
    "bronze_polished",
]

BASE_FORMS: tuple[BaseForm, ...] = (
    "perforated_disk_base",
    "threaded_pillar_base",
    "wheeled_cart_base",
    "tripod_base",
    "ground_spike_base",
)
ARM_FORMS: tuple[ArmForm, ...] = (
    "straight_radial_tube",
    "curved_s_reaction",
    "tapered_upsweep",
)
NOZZLE_STYLES: tuple[NozzleStyle, ...] = (
    "fixed_inline_nozzles",
    "revolute_pivot_nozzles",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "gunmetal_silver_orange",
    "warm_brass_amber",
    "green_cast_brass",
    "black_plastic_orange",
    "bronze_polished",
)
ARM_COUNTS: tuple[int, ...] = (2, 3, 4)
NOZZLES_PER_ARM: tuple[int, ...] = (1, 2)

# ---------------------------------------------------------------------------
# Palettes. Every ``part.visual(..., material=mats[<key>])`` reads from this
# dict. Keys: body (base main body) / accent (rim/hub/bright metal) /
# arm (arm tubes) / nozzle_shell (nozzle body) / insert (nozzle grip / orange
# accent) / hardware (dark plastic/rubber trim).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "gunmetal_silver_orange": {
        "body": (0.31, 0.33, 0.33, 1.0),
        "accent": (0.62, 0.64, 0.63, 1.0),
        "arm": (0.13, 0.15, 0.15, 1.0),
        "nozzle_shell": (0.62, 0.64, 0.63, 1.0),
        "insert": (1.00, 0.24, 0.025, 1.0),
        "hardware": (0.045, 0.052, 0.052, 1.0),
    },
    "warm_brass_amber": {
        "body": (0.56, 0.33, 0.12, 1.0),
        "accent": (0.84, 0.60, 0.27, 1.0),
        "arm": (0.70, 0.43, 0.16, 1.0),
        "nozzle_shell": (0.70, 0.43, 0.16, 1.0),
        "insert": (0.86, 0.58, 0.25, 1.0),
        "hardware": (0.075, 0.060, 0.045, 1.0),
    },
    "green_cast_brass": {
        "body": (0.02, 0.48, 0.19, 1.0),
        "accent": (0.88, 0.72, 0.38, 1.0),
        "arm": (0.72, 0.53, 0.23, 1.0),
        "nozzle_shell": (0.72, 0.53, 0.23, 1.0),
        "insert": (0.88, 0.72, 0.38, 1.0),
        "hardware": (0.035, 0.040, 0.040, 1.0),
    },
    "black_plastic_orange": {
        "body": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.62, 0.64, 0.63, 1.0),
        "arm": (0.15, 0.15, 0.15, 1.0),
        "nozzle_shell": (0.62, 0.64, 0.63, 1.0),
        "insert": (1.00, 0.35, 0.05, 1.0),
        "hardware": (0.035, 0.035, 0.035, 1.0),
    },
    "bronze_polished": {
        "body": (0.44, 0.28, 0.14, 1.0),
        "accent": (0.72, 0.72, 0.70, 1.0),
        "arm": (0.55, 0.33, 0.14, 1.0),
        "nozzle_shell": (0.72, 0.72, 0.70, 1.0),
        "insert": (0.62, 0.64, 0.63, 1.0),
        "hardware": (0.10, 0.09, 0.08, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Real-world dimensions (meters). Kept small so per-seed compile stays cheap.
# All z is world-up; central rotor axis passes through (0,0,z_axis).
# ---------------------------------------------------------------------------
# base
BASE_TOP_Z = 0.030  # top surface of a typical base body
BEARING_POST_Z0 = 0.030  # bearing post/shaft bottom
BEARING_POST_LEN = 0.030  # bearing post/shaft length
BEARING_POST_R = 0.009  # bearing post/shaft radius
# rotor
ROTOR_HUB_LOW_Z = 0.060  # hub bottom above base (bearing skirt)
HUB_SKIRT_H = 0.010  # bearing skirt (mates the base post top)
HUB_BODY_H = 0.024  # main hub body height
HUB_CAP_H = 0.005  # top cap segment on the hub lathe
HUB_R = 0.022  # main hub radius
# arm centerline sits mid-hub so arms merge into hub_shell (connectivity)
ROTOR_ARM_Z = HUB_SKIRT_H + HUB_BODY_H * 0.55  # 0.010 + 0.0132 = 0.0232
# arm placement (nominal, before arm_length_scale)
ARM_LEN = 0.080  # nominal outward arm reach from hub
ARM_R = 0.006  # tube radius
ARM_ROOT_INSET = 0.008  # how far arm root sinks INTO hub for connectivity
# nozzle
NOZZLE_R = 0.0075
NOZZLE_LEN = 0.024
NOZZLE_INSERT_LEN = 0.010
# wheel (wheeled_cart_base only)
WHEEL_R = 0.030
WHEEL_W = 0.020
WHEEL_X = 0.100
WHEEL_Y = 0.055


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SprinklerHeadWithRotatingArmsConfig:
    base_form: BaseForm | None = None
    arm_form: ArmForm | None = None
    nozzle_style: NozzleStyle | None = None
    arm_count: int | None = None
    nozzles_per_arm: int | None = None
    palette_style: PaletteStyle | None = None
    base_size_scale: float = 1.0
    arm_length_scale: float = 1.0
    hub_radius_scale: float = 1.0
    nozzle_pivot_range_scale: float = 1.0
    name: str = "sprinkler_head_with_rotating_arms"


@dataclass(frozen=True)
class ResolvedSprinklerHeadWithRotatingArmsConfig:
    base_form: BaseForm
    arm_form: ArmForm
    nozzle_style: NozzleStyle
    arm_count: int
    nozzles_per_arm: int
    palette_style: PaletteStyle
    base_size_scale: float
    arm_length_scale: float
    hub_radius_scale: float
    nozzle_pivot_range_scale: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> SprinklerHeadWithRotatingArmsConfig:
    rng = random.Random(seed)
    base_form = rng.choice(BASE_FORMS)
    arm_form = rng.choice(ARM_FORMS)
    nozzle_style = rng.choices(NOZZLE_STYLES, weights=(1, 3), k=1)[
        0
    ]  # weight revolute higher (Rule 5)
    arm_count = rng.choices(ARM_COUNTS, weights=(3, 6, 3), k=1)[0]
    nozzles_per_arm = rng.choices(NOZZLES_PER_ARM, weights=(3, 1), k=1)[0]
    palette_style = rng.choice(PALETTE_STYLES)
    return SprinklerHeadWithRotatingArmsConfig(
        base_form=base_form,
        arm_form=arm_form,
        nozzle_style=nozzle_style,
        arm_count=arm_count,
        nozzles_per_arm=nozzles_per_arm,
        palette_style=palette_style,
        base_size_scale=round(rng.uniform(0.85, 1.15), 4),
        arm_length_scale=round(rng.uniform(0.85, 1.15), 4),
        hub_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        nozzle_pivot_range_scale=round(rng.uniform(0.7, 1.1), 4),
        name=f"seeded_sprinkler_head_with_rotating_arms_{seed}",
    )


def resolve_config(
    config: SprinklerHeadWithRotatingArmsConfig | None = None,
) -> ResolvedSprinklerHeadWithRotatingArmsConfig:
    cfg = config or SprinklerHeadWithRotatingArmsConfig()
    base_form = _pick(cfg.base_form, BASE_FORMS)
    arm_form = _pick(cfg.arm_form, ARM_FORMS)
    nozzle_style = _pick(cfg.nozzle_style, NOZZLE_STYLES)
    arm_count = int(cfg.arm_count) if cfg.arm_count in ARM_COUNTS else 3
    nozzles_per_arm = int(cfg.nozzles_per_arm) if cfg.nozzles_per_arm in NOZZLES_PER_ARM else 1
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    base_size_scale = _clamp(cfg.base_size_scale, 0.85, 1.15)
    arm_length_scale = _clamp(cfg.arm_length_scale, 0.85, 1.15)
    hub_radius_scale = _clamp(cfg.hub_radius_scale, 0.90, 1.10)
    nozzle_pivot_range_scale = _clamp(cfg.nozzle_pivot_range_scale, 0.7, 1.1)

    # Compatibility gates from spec §7:
    # (1) nozzles_per_arm=2 needs a long-enough arm.
    if nozzles_per_arm == 2 and arm_length_scale < 0.95:
        nozzles_per_arm = 1
    # (2) hub_radius vs arm_count=4 clearance.
    if arm_count == 4 and hub_radius_scale > 1.05:
        hub_radius_scale = 1.05
    # (3) fixed_inline_nozzles ignores nozzle_pivot_range_scale (no revolute).
    # (nothing to force; the scale is simply unused by the fixed branch.)

    return ResolvedSprinklerHeadWithRotatingArmsConfig(
        base_form=base_form,
        arm_form=arm_form,
        nozzle_style=nozzle_style,
        arm_count=arm_count,
        nozzles_per_arm=nozzles_per_arm,
        palette_style=palette_style,
        base_size_scale=base_size_scale,
        arm_length_scale=arm_length_scale,
        hub_radius_scale=hub_radius_scale,
        nozzle_pivot_range_scale=nozzle_pivot_range_scale,
        name=cfg.name or "sprinkler_head_with_rotating_arms",
    )


def slot_choices_for_config(
    config: SprinklerHeadWithRotatingArmsConfig | ResolvedSprinklerHeadWithRotatingArmsConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedSprinklerHeadWithRotatingArmsConfig)
        else resolve_config(config)
    )
    return (
        ("base_form", r.base_form),
        ("arm_form", r.arm_form),
        ("nozzle_style", r.nozzle_style),
        ("arm_count", f"arms_{r.arm_count}"),
        ("nozzles_per_arm", f"noz_{r.nozzles_per_arm}"),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (derived quantities — Contract 3c/3e).
# ---------------------------------------------------------------------------
def _hub_radius(r: ResolvedSprinklerHeadWithRotatingArmsConfig) -> float:
    return HUB_R * r.hub_radius_scale


def _arm_length(r: ResolvedSprinklerHeadWithRotatingArmsConfig) -> float:
    return ARM_LEN * r.arm_length_scale


def _base_dim(r: ResolvedSprinklerHeadWithRotatingArmsConfig) -> float:
    return r.base_size_scale


def _arm_tip_local(r: ResolvedSprinklerHeadWithRotatingArmsConfig) -> tuple[float, float, float]:
    """Arm tip in the un-rotated (angle=0, +x) arm frame, relative to rotor origin."""
    length = _arm_length(r)
    hub_r = _hub_radius(r)
    tip_x = hub_r + length
    if r.arm_form == "straight_radial_tube":
        return (tip_x, 0.0, ROTOR_ARM_Z)
    if r.arm_form == "curved_s_reaction":
        # curved-S sweeps up at the tip
        return (tip_x, -0.010, ROTOR_ARM_Z + 0.020)
    # tapered_upsweep
    return (tip_x, 0.0, ROTOR_ARM_Z + 0.014)


# ---------------------------------------------------------------------------
# Base module factories. Each populates the `base` part with visuals and
# returns the name of the visual that publishes the top bearing face
# (the parent-side face of the base_to_rotor MatingContract), plus the
# world-z height of that face's top.
# ---------------------------------------------------------------------------
def _emit_perforated_disk_base(base, mats, r) -> tuple[str, float]:
    s = _base_dim(r)
    disk_r = 0.088 * s
    disk_h = 0.018
    # plate body
    base.visual(
        Cylinder(radius=disk_r, length=disk_h),
        origin=Origin(xyz=(0.0, 0.0, disk_h * 0.5)),
        material=mats["body"],
        name="plate_body", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
    )
    # perforation ring — small evenly spaced holes as decorative visuals
    for i in range(12):
        theta = i * math.tau / 12.0
        base.visual(
            Cylinder(radius=0.006, length=0.002),
            origin=Origin(
                xyz=(0.062 * s * math.cos(theta), 0.062 * s * math.sin(theta), disk_h + 0.001)
            ),
            material=mats["hardware"],
            name=f"perforation_hole_{i}", material_class_id=("plastic.opaque_generic" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
        )
    # six radial index ribs on top (④ decoration)
    for i in range(6):
        theta = i * math.tau / 6.0
        base.visual(
            Box((0.045 * s, 0.008, 0.003)),
            origin=Origin(
                xyz=(0.050 * s * math.cos(theta), 0.050 * s * math.sin(theta), disk_h + 0.0015),
                rpy=(0.0, 0.0, theta),
            ),
            material=mats["hardware"],
            name=f"radial_rib_{i}", material_class_id=("plastic.opaque_generic" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
        )
    # side hose connector (visual, on -y wall)
    base.visual(
        Cylinder(radius=0.014, length=0.055),
        origin=Origin(xyz=(0.0, -disk_r - 0.014, disk_h * 0.5), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="side_hose_connector", material_class_id=("plastic.opaque_generic" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
    )
    # bearing post
    post_top = disk_h + BEARING_POST_LEN
    base.visual(
        Cylinder(radius=BEARING_POST_R, length=BEARING_POST_LEN),
        origin=Origin(xyz=(0.0, 0.0, disk_h + BEARING_POST_LEN * 0.5)),
        material=mats["accent"],
        name="bearing_post", material_class_id=("metal.chrome_polished" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_polished"),
    )
    return "bearing_post", post_top


def _emit_threaded_pillar_base(base, mats, r) -> tuple[str, float]:
    s = _base_dim(r)
    # broad foot pad
    base.visual(
        Cylinder(radius=0.048 * s, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, 0.004)),
        material=mats["body"],
        name="foot_pad", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
    )
    # threaded pillar body
    pillar_h = 0.070
    base.visual(
        Cylinder(radius=0.018, length=pillar_h),
        origin=Origin(xyz=(0.0, 0.0, 0.008 + pillar_h * 0.5)),
        material=mats["body"],
        name="pillar_body", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
    )
    # thread ridges (④)
    for i in range(5):
        z = 0.014 + 0.014 * i
        base.visual(
            Cylinder(radius=0.020, length=0.003),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=mats["accent"],
            name=f"thread_ridge_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_polished"),
        )
    # bearing cap on top of pillar
    post_z0 = 0.008 + pillar_h
    base.visual(
        Cylinder(radius=BEARING_POST_R, length=BEARING_POST_LEN),
        origin=Origin(xyz=(0.0, 0.0, post_z0 + BEARING_POST_LEN * 0.5)),
        material=mats["accent"],
        name="bearing_post", material_class_id=("metal.chrome_polished" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_polished"),
    )
    post_top = post_z0 + BEARING_POST_LEN
    return "bearing_post", post_top


def _emit_wheeled_cart_base(base, mats, r) -> tuple[str, float]:
    s = _base_dim(r)
    # Chassis plate — sized to stop SHORT of the wheels along x
    # (Contract 3e: derived from WHEEL_X/WHEEL_W with a 6mm clear margin,
    # not an independently tuned literal).
    chassis_hx = max(0.030, WHEEL_X - WHEEL_W * 0.5 - 0.010)  # x half-length
    chassis_hy = 0.070 * s  # y half-width
    chassis_h = 0.014
    base.visual(
        Box((chassis_hx * 2.0, chassis_hy * 2.0, chassis_h)),
        origin=Origin(xyz=(0.0, 0.0, WHEEL_R + 0.007)),
        material=mats["body"],
        name="chassis_plate", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
    )
    # 3 gussets radiating from center (④)
    for i in range(3):
        theta = i * math.tau / 3.0
        base.visual(
            Box((0.020, 0.056 * s, 0.018)),
            origin=Origin(
                xyz=(
                    0.028 * s * math.cos(theta),
                    0.028 * s * math.sin(theta),
                    WHEEL_R + 0.014 + 0.009,
                ),
                rpy=(0.0, 0.0, theta),
            ),
            material=mats["body"],
            name=f"gusset_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
        )
    # hose connector out the back
    base.visual(
        Cylinder(radius=0.014, length=0.050),
        origin=Origin(
            xyz=(0.0, -chassis_hy - 0.014, WHEEL_R + 0.008),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["hardware"],
        name="hose_connector", material_class_id=("plastic.opaque_generic" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
    )
    # axles (visuals so they're anchored to the base). The axle extends
    # inward from the chassis edge to the wheel plane, so it touches the
    # chassis (Contract 3 connectivity) and passes through the wheel hub.
    axle_len = WHEEL_X + WHEEL_W - chassis_hx  # cover chassis edge → wheel far side
    axle_center_x = chassis_hx + axle_len * 0.5 - 0.002  # slight embed into chassis
    for i, side in enumerate((-1.0, 1.0)):
        base.visual(
            Cylinder(radius=0.006, length=axle_len),
            origin=Origin(
                xyz=(side * axle_center_x, 0.0, WHEEL_R),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["hardware"],
            name=f"axle_{i}", material_class_id="metal.steel_bare",
        )
    # central pedestal + bearing post
    pedestal_z0 = WHEEL_R + 0.014
    pedestal_h = 0.030
    base.visual(
        Cylinder(radius=0.026, length=pedestal_h),
        origin=Origin(xyz=(0.0, 0.0, pedestal_z0 + pedestal_h * 0.5)),
        material=mats["body"],
        name="central_pedestal", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
    )
    post_z0 = pedestal_z0 + pedestal_h
    base.visual(
        Cylinder(radius=BEARING_POST_R, length=BEARING_POST_LEN),
        origin=Origin(xyz=(0.0, 0.0, post_z0 + BEARING_POST_LEN * 0.5)),
        material=mats["accent"],
        name="bearing_post", material_class_id=("metal.chrome_polished" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_polished"),
    )
    return "bearing_post", post_z0 + BEARING_POST_LEN


def _emit_tripod_base(base, mats, r) -> tuple[str, float]:
    s = _base_dim(r)
    # central hub at the top of the tripod
    hub_r = 0.024
    hub_h = 0.030
    apex_z = 0.100
    base.visual(
        Cylinder(radius=hub_r, length=hub_h),
        origin=Origin(xyz=(0.0, 0.0, apex_z - hub_h * 0.5)),
        material=mats["body"],
        name="tripod_hub", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
    )
    # 3 legs — thin boxes tilted outward whose TOP end embeds inside the hub
    # cylinder so each leg has a real support path to the grounded body
    # (Contract 3 — no disconnected geometry islands).
    r_top = hub_r * 0.42  # top anchor sits inside hub cylinder
    r_ground = 0.080 * s  # outer footprint
    z_top = apex_z - hub_h * 0.30  # anchor midway up hub interior
    z_ground = 0.0
    h_span = r_ground - r_top
    v_span = z_top - z_ground
    leg_len = math.hypot(h_span, v_span)
    tilt = math.atan2(h_span, v_span)  # tilt from vertical
    for i in range(3):
        theta = i * math.tau / 3.0
        # Box origin = midpoint of leg span (top anchor -> ground contact).
        base.visual(
            Box((0.014, 0.014, leg_len)),
            origin=Origin(
                xyz=(
                    0.5 * (r_top + r_ground) * math.cos(theta),
                    0.5 * (r_top + r_ground) * math.sin(theta),
                    0.5 * (z_top + z_ground),
                ),
                # rpy (0, -tilt, theta): pitch first tilts local +z toward
                # +x (outward), then yaw θ rotates into the leg's azimuth.
                rpy=(0.0, -tilt, theta),
            ),
            material=mats["body"],
            name=f"tripod_leg_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
        )
    # bearing post on top of hub
    post_z0 = apex_z
    base.visual(
        Cylinder(radius=BEARING_POST_R, length=BEARING_POST_LEN),
        origin=Origin(xyz=(0.0, 0.0, post_z0 + BEARING_POST_LEN * 0.5)),
        material=mats["accent"],
        name="bearing_post", material_class_id=("metal.chrome_polished" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_polished"),
    )
    return "bearing_post", post_z0 + BEARING_POST_LEN


def _emit_ground_spike_base(base, mats, r) -> tuple[str, float]:
    s = _base_dim(r)
    # spike shaft goes down (below z=0)
    spike_h = 0.150 * s
    base.visual(
        Cylinder(radius=0.010, length=spike_h),
        origin=Origin(xyz=(0.0, 0.0, -spike_h * 0.5)),
        material=mats["body"],
        name="ground_spike", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
    )
    # collar at ground level
    base.visual(
        Cylinder(radius=0.030, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.007)),
        material=mats["body"],
        name="spike_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
    )
    # retaining ridges (④)
    for i, z0 in enumerate((-0.015, -0.030)):
        base.visual(
            Cylinder(radius=0.014, length=0.003),
            origin=Origin(xyz=(0.0, 0.0, z0)),
            material=mats["accent"],
            name=f"retain_ridge_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_polished"),
        )
    # side hose connector
    base.visual(
        Cylinder(radius=0.012, length=0.045),
        origin=Origin(xyz=(0.0, -0.038, 0.010), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="side_hose_connector", material_class_id=("plastic.opaque_generic" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
    )
    # bearing post above collar
    post_z0 = 0.014
    base.visual(
        Cylinder(radius=BEARING_POST_R, length=BEARING_POST_LEN),
        origin=Origin(xyz=(0.0, 0.0, post_z0 + BEARING_POST_LEN * 0.5)),
        material=mats["accent"],
        name="bearing_post", material_class_id=("metal.chrome_polished" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_polished"),
    )
    return "bearing_post", post_z0 + BEARING_POST_LEN


_BASE_FACTORIES = {
    "perforated_disk_base": _emit_perforated_disk_base,
    "threaded_pillar_base": _emit_threaded_pillar_base,
    "wheeled_cart_base": _emit_wheeled_cart_base,
    "tripod_base": _emit_tripod_base,
    "ground_spike_base": _emit_ground_spike_base,
}


# ---------------------------------------------------------------------------
# Rotor + arms. All arm forms share the placement contract: arm centerline is
# emitted along +x at angle=0 and rotated into position with rpy=(0,0,angle).
# ---------------------------------------------------------------------------
def _hub_profile(hub_scale: float) -> list[tuple[float, float]]:
    """LatheGeometry profile for the ENTIRE rotor hub (bearing skirt + body +
    top cap) as one connected lathe — Volumetric Envelope Form. z=0 at the
    skirt bottom face (which mates the base bearing post top).
    """
    hr = HUB_R * hub_scale
    z0 = 0.0
    z1 = HUB_SKIRT_H
    z2 = HUB_SKIRT_H + HUB_BODY_H
    z3 = z2 + HUB_CAP_H
    return [
        (0.000, z0),
        (hr * 0.62, z0),  # skirt outer bottom (mates post top)
        (hr * 0.62, z1),  # skirt top / body bottom transition
        (hr, z1 + HUB_BODY_H * 0.10),
        (hr * 1.08, HUB_SKIRT_H + HUB_BODY_H * 0.35),
        (hr * 1.08, HUB_SKIRT_H + HUB_BODY_H * 0.75),
        (hr * 0.90, z2),  # body top
        (hr * 0.85, z2 + HUB_CAP_H * 0.5),
        (hr * 0.60, z3),
        (0.000, z3),
    ]


def _arm_mesh(r: ResolvedSprinklerHeadWithRotatingArmsConfig, assets: AssetContext) -> MeshGeometry:
    """Return an arm tube MeshGeometry along +x from hub wall to tip.

    Every arm form ships the mesh; per-form primitive families:
      - straight_radial_tube: short tube_from_spline_points polyline
        (still a mesh from spline — matches S1/S7 source cylinder path).
      - curved_s_reaction: S-curved 3D spline (S2/S6).
      - tapered_upsweep: mild upsweeping polyline (S3).
    """
    hub_r = _hub_radius(r)
    length = _arm_length(r)
    tip_x = hub_r + length
    if r.arm_form == "straight_radial_tube":
        points = [
            (hub_r, 0.0, ROTOR_ARM_Z),
            (hub_r + length * 0.33, 0.0, ROTOR_ARM_Z),
            (hub_r + length * 0.66, 0.0, ROTOR_ARM_Z),
            (tip_x, 0.0, ROTOR_ARM_Z),
        ]
        radius = ARM_R
    elif r.arm_form == "curved_s_reaction":
        # S-curve: rises then dips slightly and swings tangentially
        points = [
            (hub_r, 0.0, ROTOR_ARM_Z),
            (hub_r + length * 0.30, 0.006, ROTOR_ARM_Z + 0.006),
            (hub_r + length * 0.60, -0.006, ROTOR_ARM_Z + 0.014),
            (tip_x, -0.010, ROTOR_ARM_Z + 0.020),
        ]
        radius = ARM_R
    else:  # tapered_upsweep
        points = [
            (hub_r, 0.0, ROTOR_ARM_Z),
            (hub_r + length * 0.40, 0.0, ROTOR_ARM_Z + 0.004),
            (hub_r + length * 0.75, 0.0, ROTOR_ARM_Z + 0.010),
            (tip_x, 0.0, ROTOR_ARM_Z + 0.014),
        ]
        radius = ARM_R * 0.95
    return tube_from_spline_points(
        points,
        radius=radius,
        samples_per_segment=10,
        radial_segments=12,
        cap_ends=True,
    )


def _emit_rotor(model, r, mats, assets, base_top_z: float) -> None:
    """Emit the rotor part (hub + arms + inline nozzle visuals if fixed style)."""
    rotor = model.part("rotor")

    hub_scale = r.hub_radius_scale
    # bearing skirt (mates the base bearing post top face)
    # The rotor part's local z=0 sits at ROTOR_HUB_LOW_Z above world, so this
    # skirt centered at local z ≈ 0 has its -z face at world = ROTOR_HUB_LOW_Z.
    # We'll place the rotor part origin at ROTOR_HUB_LOW_Z.
    rotor.visual(
        Cylinder(radius=HUB_R * hub_scale * 0.55, length=HUB_SKIRT_H),
        origin=Origin(xyz=(0.0, 0.0, HUB_SKIRT_H * 0.5)),
        material=mats["accent"],
        name="bearing_skirt", material_class_id=("metal.chrome_polished" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_polished"),
    )
    # main hub body (LatheGeometry profile — form-family primitive).
    # `_hub_profile` already applies hub_scale and includes skirt/body/cap z
    # segments in one connected lathe (Volumetric Envelope Form).
    hub_profile = _hub_profile(hub_scale)
    rotor.visual(
        mesh_from_geometry(
            LatheGeometry(hub_profile, segments=32),
            assets.mesh_path(f"rotor_hub_shell_{r.arm_form}.obj") if assets else "rotor_hub_shell",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["body"],
        name="hub_shell", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
    )
    # top cap
    rotor.visual(
        Cylinder(radius=HUB_R * hub_scale * 0.85, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, HUB_SKIRT_H + HUB_BODY_H + 0.002)),
        material=mats["accent"],
        name="top_cap", material_class_id=("metal.chrome_polished" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_polished"),
    )

    # Arms — shared mesh, rotated per-arm.
    arm_mesh = _arm_mesh(r, assets) if assets is not None else None
    for i in range(r.arm_count):
        angle = i * math.tau / r.arm_count
        if arm_mesh is not None:
            rotor.visual(
                mesh_from_geometry(arm_mesh, assets.mesh_path(f"arm_tube_{r.arm_form}_{i}.obj")),
                origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, angle)),
                material=mats["arm"],
                name=f"arm_tube_{i}", material_class_id=("metal.brass_aged" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
            )
        else:
            # Fallback: primitive cylinder along +x (used only when assets None)
            hub_r = _hub_radius(r)
            length = _arm_length(r)
            rotor.visual(
                Cylinder(radius=ARM_R, length=length),
                origin=Origin(
                    xyz=(
                        (hub_r + length * 0.5) * math.cos(angle),
                        (hub_r + length * 0.5) * math.sin(angle),
                        ROTOR_ARM_Z,
                    ),
                    rpy=(0.0, math.pi / 2.0, angle),
                ),
                material=mats["arm"],
                name=f"arm_tube_{i}", material_class_id=("metal.brass_aged" if r.palette_style in {"gunmetal_silver_orange", "warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
            )
        # per-arm socket at tip (child-side of nozzle joint / inline nozzle host)
        tip_local = _arm_tip_local(r)
        tip_world_local = (
            tip_local[0] * math.cos(angle) - tip_local[1] * math.sin(angle),
            tip_local[0] * math.sin(angle) + tip_local[1] * math.cos(angle),
            tip_local[2],
        )
        rotor.visual(
            Cylinder(radius=ARM_R * 1.4, length=0.008),
            origin=Origin(
                xyz=(tip_world_local[0], tip_world_local[1], tip_world_local[2]),
                rpy=(0.0, math.pi / 2.0, angle),
            ),
            material=mats["accent"],
            name=f"arm_socket_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_polished"),
        )

        if r.nozzle_style == "fixed_inline_nozzles":
            # inline nozzle visuals on the rotor part (Rule 1: static → visual)
            for j in range(r.nozzles_per_arm):
                # t=0.65 mid, t=1.00 tip (spec §8.5)
                t = 1.00 if j == r.nozzles_per_arm - 1 else 0.65
                hub_r = _hub_radius(r)
                length = _arm_length(r)
                cx_local = hub_r + t * length
                cx = cx_local * math.cos(angle)
                cy = cx_local * math.sin(angle)
                cz = (
                    ROTOR_ARM_Z
                    + (
                        0.020
                        if r.arm_form == "curved_s_reaction"
                        else (0.014 if r.arm_form == "tapered_upsweep" else 0.0)
                    )
                    * t
                )
                rotor.visual(
                    Cylinder(radius=NOZZLE_R, length=NOZZLE_LEN),
                    origin=Origin(
                        xyz=(cx, cy, cz + NOZZLE_LEN * 0.5),
                        rpy=(0.0, 0.0, 0.0),
                    ),
                    material=mats["nozzle_shell"],
                    name=f"inline_nozzle_body_{i}_{j}", material_class_id=("metal.stainless_matte" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_aged"),
                )
                rotor.visual(
                    Cylinder(radius=NOZZLE_R * 0.55, length=NOZZLE_INSERT_LEN),
                    origin=Origin(
                        xyz=(cx, cy, cz + NOZZLE_LEN + NOZZLE_INSERT_LEN * 0.5),
                        rpy=(0.0, 0.0, 0.0),
                    ),
                    material=mats["insert"],
                    name=f"inline_nozzle_insert_{i}_{j}", material_class_id=("metal.brass_polished" if r.palette_style in {"warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
                )


def _emit_nozzle_parts(model, r, mats) -> list[str]:
    """When nozzle_style == revolute_pivot_nozzles, emit one child part per
    (arm, nozzle-slot) with a REVOLUTE joint whose axis is the arm's radial
    direction. Returns joint names emitted.
    """
    joint_names: list[str] = []
    rotor = model.get_part("rotor")
    hub_r = _hub_radius(r)
    length = _arm_length(r)
    pivot_range = 0.48 * r.nozzle_pivot_range_scale

    ferrule_len = 0.010
    ferrule_r = ARM_R * 1.35
    body_r = NOZZLE_R
    body_len = NOZZLE_LEN
    insert_r = NOZZLE_R * 0.55
    insert_len = NOZZLE_INSERT_LEN
    # Joint-origin z lift above arm centerline. We want:
    #   - ferrule bottom to sit ON TOP of the arm (contact) — captured pin
    #     allow_overlap covers the small penetration.
    #   - nozzle_body bottom to sit clear of the arm even at overlap_tol=5mm,
    #     including a safety margin for the arm mesh AABB (end caps + curve
    #     dips for curved/tapered forms).
    # Ferrule center at joint origin; ferrule half-height = ferrule_len/2.
    # nozzle_body bottom sits at joint-origin z + body_z0.
    body_z0 = ferrule_len * 0.5 + 0.009  # 9mm buffer above ferrule top

    for i in range(r.arm_count):
        angle = i * math.tau / r.arm_count
        for j in range(r.nozzles_per_arm):
            # Two-nozzle placement: mid + tip. Use t=0.55/1.00 so the mid
            # nozzle sits close to the hub end (avoids stacking near the tip
            # in short-arm variants).
            t = 1.00 if j == r.nozzles_per_arm - 1 else 0.55
            cx_local = hub_r + t * length
            cx = cx_local * math.cos(angle)
            cy = cx_local * math.sin(angle)
            arm_z = (
                ROTOR_ARM_Z
                + (
                    0.020
                    if r.arm_form == "curved_s_reaction"
                    else (0.014 if r.arm_form == "tapered_upsweep" else 0.0)
                )
                * t
            )
            # Joint origin sits at the arm-top surface. Ferrule dips into the
            # arm (captured pin — allow_overlap in tests); nozzle body sits
            # clear above (body_z0 offset above ferrule top).
            cz = arm_z + ARM_R + ferrule_len * 0.5  # ferrule center on tube top

            nozzle = model.part(f"nozzle_{i}_{j}")
            # Nozzle part local frame: +z rises vertically after the joint
            # rpy=(0,0,angle) rotation (rpy z-rotation preserves world z).
            # Joint axis (1,0,0) in this frame becomes the arm-radial world
            # axis, so pivot tilts the nozzle fore/aft in the tangential-z
            # plane — realistic adjustable-jet motion.
            nozzle.visual(
                Cylinder(radius=ferrule_r, length=ferrule_len),
                origin=Origin(xyz=(0.0, 0.0, 0.0)),
                material=mats["accent"],
                name="ferrule", material_class_id=("metal.chrome_polished" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_polished"),
            )
            # Slim stem bridges ferrule top → nozzle_body bottom (no islands).
            stem_top = body_z0
            stem_bot = ferrule_len * 0.5 - 0.001
            stem_len = stem_top - stem_bot + 0.002
            nozzle.visual(
                Cylinder(radius=body_r * 0.9, length=stem_len),
                origin=Origin(xyz=(0.0, 0.0, 0.5 * (stem_top + stem_bot))),
                material=mats["accent"],
                name="neck", material_class_id=("metal.chrome_polished" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_polished"),
            )
            nozzle.visual(
                Cylinder(radius=body_r, length=body_len),
                origin=Origin(xyz=(0.0, 0.0, body_z0 + body_len * 0.5)),
                material=mats["nozzle_shell"],
                name="nozzle_body", material_class_id=("metal.stainless_matte" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_aged"),
            )
            nozzle.visual(
                Cylinder(radius=insert_r, length=insert_len),
                origin=Origin(
                    xyz=(0.0, 0.0, body_z0 + body_len + insert_len * 0.5 - 0.002),
                ),
                material=mats["insert"],
                name="nozzle_insert", material_class_id=("metal.brass_polished" if r.palette_style in {"warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
            )
            # Radial-outward marker rib on the nozzle body: touches nozzle_body
            # along its +x face (islands pass), visible AABB shift under pose.
            nozzle.visual(
                Box((0.010, 0.003, 0.005)),
                origin=Origin(
                    xyz=(body_r + 0.004, 0.0, body_z0 + body_len * 0.5),
                ),
                material=mats["insert"],
                name="index_rib", material_class_id=("metal.brass_polished" if r.palette_style in {"warm_brass_amber", "green_cast_brass", "bronze_polished"} else "plastic.opaque_glossy_molded"),
            )

            joint_name = f"arm_to_nozzle_{i}_{j}"
            model.articulation(
                joint_name,
                ArticulationType.REVOLUTE,
                parent=rotor,
                child=nozzle,
                origin=Origin(
                    xyz=(cx, cy, cz),
                    rpy=(0.0, 0.0, angle),
                ),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(
                    effort=0.8,
                    velocity=2.0,
                    lower=-pivot_range,
                    upper=pivot_range,
                ),
                # No MatingContract: the ferrule/arm-tube pair is a captured-pin
                # geometry (ferrule caps the arm tube surface). Rule 2
                # grandfathers the gap check for captured-pin joints. We
                # instead declare element-scoped allow_overlap in tests.
            )
            joint_names.append(joint_name)
    return joint_names


# ---------------------------------------------------------------------------
# Wheel spins for wheeled_cart_base.
# ---------------------------------------------------------------------------
def _emit_wheels(model, r, mats) -> list[str]:
    base = model.get_part("base")
    joint_names: list[str] = []
    for i, side in enumerate((-1.0, 1.0)):
        wheel = model.part(f"wheel_{i}")
        # Wheel is a cylinder with axis along +x. In the wheel's local frame,
        # centered at origin.
        wheel.visual(
            Cylinder(radius=WHEEL_R, length=WHEEL_W),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["hardware"],
            name="wheel_tire", material_class_id="rubber.smooth_plain",
        )
        wheel.visual(
            Cylinder(radius=WHEEL_R * 0.6, length=WHEEL_W * 0.5),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["accent"],
            name="wheel_hub", material_class_id=("metal.chrome_polished" if r.palette_style in {"gunmetal_silver_orange", "black_plastic_orange", "bronze_polished"} else "metal.brass_polished"),
        )
        joint = f"wheel_spin_{i}"
        model.articulation(
            joint,
            ArticulationType.CONTINUOUS,
            parent=base,
            child=wheel,
            origin=Origin(xyz=(side * WHEEL_X, 0.0, WHEEL_R)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=18.0),
            # captured-pin (axle inside wheel hub) — no MatingContract.
        )
        joint_names.append(joint)
    return joint_names


# ---------------------------------------------------------------------------
# Top-level build.
# ---------------------------------------------------------------------------
def build_sprinkler_head_with_rotating_arms(
    config: SprinklerHeadWithRotatingArmsConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    mats = {
        key: model.material(f"sprinkler_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    base = model.part("base")
    parent_visual, post_top_z = _BASE_FACTORIES[r.base_form](base, mats, r)

    # Emit the rotor. Its local origin sits at the base bearing post top
    # so the skirt's -z face coincides with the post's +z face.
    _emit_rotor(model, r, mats, assets, base_top_z=post_top_z)

    rotor = model.get_part("rotor")
    # Rotor part frame: we authored visuals from local z=0 upward, so place
    # the rotor part origin at world (0,0,post_top_z). The skirt's -z face
    # lands exactly at post_top_z.
    model.articulation(
        "base_to_rotor",
        ArticulationType.REVOLUTE,
        parent=base,
        child=rotor,
        origin=Origin(xyz=(0.0, 0.0, post_top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=12.0, lower=-math.pi, upper=math.pi),
        mating=MatingContract(parent_visual, "positive_z", "bearing_skirt", "negative_z"),
    )

    # Slot C: revolute pivot nozzles get separate parts + joints.
    if r.nozzle_style == "revolute_pivot_nozzles":
        _emit_nozzle_parts(model, r, mats)

    # Slot A extra: wheels for the cart base.
    if r.base_form == "wheeled_cart_base":
        _emit_wheels(model, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_sprinkler_head_with_rotating_arms(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_sprinkler_head_with_rotating_arms(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_sprinkler_head_with_rotating_arms_tests(
    object_model: ArticulatedObject,
    config: SprinklerHeadWithRotatingArmsConfig | None = None,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    base = object_model.get_part("base")
    rotor = object_model.get_part("rotor")
    rotor_joint = object_model.get_articulation("base_to_rotor")

    # ---- captured-pin allowances (element-scoped) ----
    ctx.allow_overlap(
        base,
        rotor,
        elem_a="bearing_post",
        elem_b="bearing_skirt",
        reason="Rotor bearing skirt is captured on the fixed bearing post.",
    )
    ctx.allow_overlap(
        base,
        rotor,
        elem_a="bearing_post",
        elem_b="hub_shell",
        reason="The rotor hub shell surrounds the bearing post.",
    )

    if r.nozzle_style == "revolute_pivot_nozzles":
        for i in range(r.arm_count):
            for j in range(r.nozzles_per_arm):
                nozzle = object_model.get_part(f"nozzle_{i}_{j}")
                ctx.allow_overlap(
                    rotor,
                    nozzle,
                    elem_a=f"arm_socket_{i}",
                    elem_b="ferrule",
                    reason="Nozzle ferrule is captured on the arm tip socket.",
                )
                ctx.allow_overlap(
                    rotor,
                    nozzle,
                    elem_a=f"arm_tube_{i}",
                    elem_b="ferrule",
                    reason="Arm tube spindle is captured inside the nozzle ferrule.",
                )

    if r.base_form == "wheeled_cart_base":
        for i in range(2):
            wheel = object_model.get_part(f"wheel_{i}")
            ctx.allow_overlap(
                base,
                wheel,
                elem_a=f"axle_{i}",
                elem_b="wheel_tire",
                reason="Fixed axle is captured inside the rolling wheel.",
            )
            ctx.allow_overlap(
                base,
                wheel,
                elem_a=f"axle_{i}",
                elem_b="wheel_hub",
                reason="Fixed axle is captured inside the wheel hub.",
            )

    # ---- compiler baseline + motion gate ----
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry()
    ctx.fail_if_joint_mating_has_gap()
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    # ---- category identity assertions ----
    ctx.check(
        "base_to_rotor is REVOLUTE about vertical (Z) axis with full turn",
        rotor_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(rotor_joint.axis) == (0.0, 0.0, 1.0)
        and rotor_joint.motion_limits is not None
        and rotor_joint.motion_limits.lower is not None
        and rotor_joint.motion_limits.upper is not None
        and rotor_joint.motion_limits.upper - rotor_joint.motion_limits.lower >= math.tau - 1e-6,
        details=(
            f"type={rotor_joint.articulation_type} axis={rotor_joint.axis} "
            f"limits={rotor_joint.motion_limits}"
        ),
    )

    # arm visuals on the rotor
    arm_visuals = [v for v in rotor.visuals if v.name and v.name.startswith("arm_tube_")]
    ctx.check(
        f"rotor has {r.arm_count} arms (from arm_count)",
        len(arm_visuals) == r.arm_count,
        details=f"found={sorted(v.name for v in arm_visuals)} expected N={r.arm_count}",
    )

    # nozzle-per-arm count
    if r.nozzle_style == "revolute_pivot_nozzles":
        for i in range(r.arm_count):
            per_arm = [object_model.get_part(f"nozzle_{i}_{j}") for j in range(r.nozzles_per_arm)]
            ctx.check(
                f"arm {i} has {r.nozzles_per_arm} pivot nozzle parts",
                len(per_arm) == r.nozzles_per_arm,
                details=f"nozzles_per_arm={r.nozzles_per_arm}",
            )
            for j in range(r.nozzles_per_arm):
                joint = object_model.get_articulation(f"arm_to_nozzle_{i}_{j}")
                ctx.check(
                    f"arm_to_nozzle_{i}_{j} is REVOLUTE with radial axis",
                    joint.articulation_type == ArticulationType.REVOLUTE
                    and tuple(joint.axis) == (1.0, 0.0, 0.0),
                    details=f"type={joint.articulation_type} axis={joint.axis}",
                )
    else:
        # fixed_inline: verify inline nozzle body visuals per arm
        for i in range(r.arm_count):
            inline_count = sum(
                1 for v in rotor.visuals if v.name and v.name.startswith(f"inline_nozzle_body_{i}_")
            )
            ctx.check(
                f"arm {i} has {r.nozzles_per_arm} inline nozzle visuals",
                inline_count == r.nozzles_per_arm,
                details=f"inline_count={inline_count}",
            )

    # Wheels for wheeled_cart_base
    if r.base_form == "wheeled_cart_base":
        for i in range(2):
            joint = object_model.get_articulation(f"wheel_spin_{i}")
            ctx.check(
                f"wheel_spin_{i} is CONTINUOUS about +x",
                joint.articulation_type == ArticulationType.CONTINUOUS
                and tuple(joint.axis) == (1.0, 0.0, 0.0),
                details=f"type={joint.articulation_type} axis={joint.axis}",
            )

    # ---- targeted motion assertions (Rule 5) ----
    # Rotor turn: check tip position moves at least 40mm at pose=1.0 rad
    # Pick an arm to sample.
    sample_arm = 0
    rest_pos = ctx.part_element_world_aabb(rotor, elem=f"arm_socket_{sample_arm}")
    with ctx.pose({rotor_joint: 1.0}):
        turned_pos = ctx.part_element_world_aabb(rotor, elem=f"arm_socket_{sample_arm}")
    if rest_pos is not None and turned_pos is not None:
        rest_center = tuple((rest_pos[0][k] + rest_pos[1][k]) * 0.5 for k in range(3))
        turned_center = tuple((turned_pos[0][k] + turned_pos[1][k]) * 0.5 for k in range(3))
        displacement = math.hypot(
            rest_center[0] - turned_center[0], rest_center[1] - turned_center[1]
        )
    else:
        displacement = 0.0
    ctx.check(
        "rotor rotation at pose=1.0 moves arm tip ≥ 40mm",
        displacement > 0.040,
        details=f"displacement={displacement:.4f}",
    )

    # Nozzle pivot (only if revolute style): check tip AABB shifts ≥ 2mm at 0.35 rad
    if r.nozzle_style == "revolute_pivot_nozzles":
        nozzle_part = object_model.get_part("nozzle_0_0")
        nozzle_joint = object_model.get_articulation("arm_to_nozzle_0_0")
        rest_aabb = ctx.part_world_aabb(nozzle_part)
        with ctx.pose({nozzle_joint: 0.35}):
            tilted_aabb = ctx.part_world_aabb(nozzle_part)
        changed = 0.0
        if rest_aabb is not None and tilted_aabb is not None:
            changed = max(
                abs(rest_aabb[k][axis] - tilted_aabb[k][axis]) for k in (0, 1) for axis in range(3)
            )
        ctx.check(
            "nozzle pivot at pose=0.35 shifts AABB ≥ 2mm",
            changed > 0.002,
            details=f"max_delta={changed:.5f}",
        )

    ctx.check(
        "slot_choices recorded in model meta",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "SprinklerHeadWithRotatingArmsConfig",
    "ResolvedSprinklerHeadWithRotatingArmsConfig",
    "build_sprinkler_head_with_rotating_arms",
    "build_seeded_sprinkler_head_with_rotating_arms",
    "config_from_seed",
    "resolve_config",
    "run_sprinkler_head_with_rotating_arms_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "__modular__",
)
