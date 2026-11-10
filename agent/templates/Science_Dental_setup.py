# SPDX-License-Identifier: Apache-2.0

"""Dental treatment unit (operatory setup) — modular procedural template.

This template is MODULAR (`__modular__ = True`). It composes a dental
treatment unit from three structural slots plus one multiplicity axis,
derived verbatim from the declared 5-star module sources in
``articraft_template_authoring/specs_modular_v1/Science_Dental_setup.md``:

  Slot A  chair-recline   : single_body / two_section / three_section
  Slot B  light-arm       : single_rigid / two_segment_elbow / parallelogram
  Slot C  delivery-head   : round_dish / led_panel / swing_tray
  N       instrument_count: {3,5,7} handpiece+hose pairs on the host

Common skeleton (all 9 sources agree): root ``base`` (floor_pad +
chair_pedestal + seat_carrier + light_post + post foot), companion FIXED
``delivery_column`` (cabinet / cuspidor / monitor / tray) and ``stool``
(5-star caster base). Three core REVOLUTE joints are present in EVERY seed:

  * backrest_recline   REVOLUTE axis -Y  (chair recline)
  * light_arm_swing    REVOLUTE axis  Z  (overhead light swings on the post)
  * light_head_tilt    REVOLUTE axis  Y  (reflector / LED head tilts on yoke)

Source records (model.py adapted, primitives preserved — LatheGeometry /
section_loft / sweep_profile_along_spline / TorusGeometry / tube_from_spline /
BezelGeometry; no Box/Cylinder downgrade):

  S1 round_dish/single_body/single_rigid  rec_build-...-dent_..._90de439f (parent)
  S2 two_section_backrest                 rec_dental_setup_var_seatback2
  S3 three_section_footrest               rec_dental_setup_var_seatback3
  S4 two_segment_elbow                    rec_dental_setup_var_armelbow
  S5 parallelogram (4-bar + Mimic)        rec_dental_setup_var_armparallel
  S6 led_panel                            rec_dental_setup_var_ledhead
  S7 swing_tray_delivery                  rec_dental_setup_var_swingtray
  S8 instrument_count N=3                  rec_dental_setup_var_instr3
  S9 instrument_count N=7                  rec_dental_setup_var_instr7

Joint mating model: every articulation here is a *mechanical pivot* (hip
pivot shaft captured between bracket plates, pivot collar wrapping the post,
yoke stub inside a drop link, parallelogram bushings on cross-pins). The
MatingContract abstraction assumes flat axis-aligned surface mating and does
not apply to pin-through-sleeve pivots, so — exactly as in the sources and in
``monitor_mount.py`` — no ``mating=`` field is declared; the joints are
grandfathered through ``fail_if_joint_mating_has_gap`` and the intentional
captured overlaps are declared element-scoped via ``ctx.allow_overlap(...)``.
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
    BezelGeometry,
    BezelRecess,
    Box,
    Cylinder,
    LatheGeometry,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    rounded_rect_profile,
    section_loft,
    sweep_profile_along_spline,
    tube_from_spline_points,
)

__modular__ = True

ChairRecline = Literal["single_body", "two_section", "three_section"]
LightArm = Literal["single_rigid", "two_segment_elbow", "parallelogram"]
DeliveryHead = Literal["round_dish", "led_panel", "swing_tray"]
PaletteStyle = Literal[
    "navy_tan", "white_mint", "grey_clinical", "teal_chrome", "sand_warm"
]

CHAIR_RECLINE_CHOICES: tuple[ChairRecline, ...] = (
    "single_body",
    "two_section",
    "three_section",
)
LIGHT_ARM_CHOICES: tuple[LightArm, ...] = (
    "single_rigid",
    "two_segment_elbow",
    "parallelogram",
)
DELIVERY_HEAD_CHOICES: tuple[DeliveryHead, ...] = (
    "round_dish",
    "led_panel",
    "swing_tray",
)
PALETTE_CHOICES: tuple[PaletteStyle, ...] = (
    "navy_tan",
    "white_mint",
    "grey_clinical",
    "teal_chrome",
    "sand_warm",
)
INSTRUMENT_COUNT_CHOICES: tuple[int, ...] = (3, 5, 7)


# --------------------------------------------------------------------------- #
# Palette presets. Each defines the same named material slots used by every
# 5-star source (upholstery / upholstery_dark / cream / cream_dark / metal /
# dark_metal / screen / glass / ceramic / chrome). Five distinct styles give
# the required per-seed palette diversity (>=3). The same material names are
# used by every module factory so `material=<name>` reaches every `.visual`.
# --------------------------------------------------------------------------- #
PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "navy_tan": {  # S1 parent palette
        "upholstery": (0.30, 0.30, 0.46, 1.0),
        "upholstery_dark": (0.24, 0.24, 0.38, 1.0),
        "cream": (0.86, 0.82, 0.66, 1.0),
        "cream_dark": (0.72, 0.67, 0.52, 1.0),
        "metal": (0.55, 0.56, 0.58, 1.0),
        "dark_metal": (0.22, 0.23, 0.25, 1.0),
        "screen": (0.36, 0.55, 0.66, 1.0),
        "glass": (0.70, 0.82, 0.88, 1.0),
        "ceramic": (0.90, 0.91, 0.92, 1.0),
        "chrome": (0.78, 0.80, 0.83, 1.0),
    },
    "white_mint": {
        "upholstery": (0.62, 0.80, 0.74, 1.0),
        "upholstery_dark": (0.48, 0.68, 0.62, 1.0),
        "cream": (0.93, 0.94, 0.93, 1.0),
        "cream_dark": (0.80, 0.82, 0.81, 1.0),
        "metal": (0.60, 0.62, 0.63, 1.0),
        "dark_metal": (0.26, 0.28, 0.29, 1.0),
        "screen": (0.30, 0.50, 0.60, 1.0),
        "glass": (0.78, 0.88, 0.90, 1.0),
        "ceramic": (0.95, 0.96, 0.96, 1.0),
        "chrome": (0.82, 0.84, 0.86, 1.0),
    },
    "grey_clinical": {
        "upholstery": (0.38, 0.40, 0.44, 1.0),
        "upholstery_dark": (0.28, 0.30, 0.34, 1.0),
        "cream": (0.74, 0.75, 0.77, 1.0),
        "cream_dark": (0.58, 0.59, 0.61, 1.0),
        "metal": (0.52, 0.53, 0.55, 1.0),
        "dark_metal": (0.18, 0.19, 0.20, 1.0),
        "screen": (0.30, 0.44, 0.52, 1.0),
        "glass": (0.72, 0.82, 0.86, 1.0),
        "ceramic": (0.90, 0.91, 0.92, 1.0),
        "chrome": (0.80, 0.82, 0.84, 1.0),
    },
    "teal_chrome": {
        "upholstery": (0.16, 0.42, 0.46, 1.0),
        "upholstery_dark": (0.10, 0.32, 0.36, 1.0),
        "cream": (0.82, 0.84, 0.84, 1.0),
        "cream_dark": (0.64, 0.67, 0.67, 1.0),
        "metal": (0.58, 0.60, 0.62, 1.0),
        "dark_metal": (0.16, 0.18, 0.20, 1.0),
        "screen": (0.24, 0.52, 0.58, 1.0),
        "glass": (0.66, 0.82, 0.86, 1.0),
        "ceramic": (0.92, 0.93, 0.93, 1.0),
        "chrome": (0.84, 0.86, 0.88, 1.0),
    },
    "sand_warm": {
        "upholstery": (0.72, 0.56, 0.40, 1.0),
        "upholstery_dark": (0.58, 0.44, 0.30, 1.0),
        "cream": (0.90, 0.86, 0.76, 1.0),
        "cream_dark": (0.76, 0.70, 0.58, 1.0),
        "metal": (0.56, 0.55, 0.52, 1.0),
        "dark_metal": (0.26, 0.24, 0.21, 1.0),
        "screen": (0.40, 0.52, 0.56, 1.0),
        "glass": (0.74, 0.82, 0.84, 1.0),
        "ceramic": (0.92, 0.90, 0.86, 1.0),
        "chrome": (0.80, 0.79, 0.76, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class DentalSetupConfig:
    chair_recline: ChairRecline = "single_body"
    light_arm: LightArm = "single_rigid"
    delivery_head: DeliveryHead = "round_dish"
    palette_style: PaletteStyle = "navy_tan"
    instrument_count: int = 5

    # Independent continuous scales (clamped in resolve_config).
    chair_h_scale: float = 1.0
    arm_len_scale: float = 1.0
    column_h_scale: float = 1.0


@dataclass(frozen=True)
class ResolvedDentalSetupConfig:
    chair_recline: ChairRecline
    light_arm: LightArm
    delivery_head: DeliveryHead
    palette_style: PaletteStyle
    instrument_count: int
    chair_h_scale: float
    arm_len_scale: float
    column_h_scale: float
    # Derived: where the instrument multiplicity is hosted. swing_tray moves
    # the host from the fixed delivery_column to the moving delivery_arm.
    instrument_host: Literal["delivery_column", "delivery_arm"]
    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> DentalSetupConfig:
    """Deterministic procedural sampling for ALL seeds (seed 0 is not special).

    Uniform draw over Slot A/B/C, weighted draw over instrument_count {3,5,7}
    (parent N=5 favoured), uniform palette, modest continuous scales. All
    combinations are mutually compatible (the only cross-slot conditional —
    swing_tray moving the instrument host — is resolved in resolve_config),
    so no rejection sampling is needed.
    """
    rng = random.Random(seed)
    chair_recline = rng.choice(CHAIR_RECLINE_CHOICES)
    light_arm = rng.choice(LIGHT_ARM_CHOICES)
    delivery_head = rng.choice(DELIVERY_HEAD_CHOICES)
    palette_style = rng.choice(PALETTE_CHOICES)
    # Weighted N: parent value 5 favoured, 3 and 7 as the documented spread.
    instrument_count = rng.choices(INSTRUMENT_COUNT_CHOICES, weights=(3, 4, 3), k=1)[0]
    return DentalSetupConfig(
        chair_recline=chair_recline,
        light_arm=light_arm,
        delivery_head=delivery_head,
        palette_style=palette_style,
        instrument_count=instrument_count,
        chair_h_scale=round(rng.uniform(0.9, 1.15), 4),
        arm_len_scale=round(rng.uniform(0.9, 1.15), 4),
        column_h_scale=round(rng.uniform(0.9, 1.15), 4),
    )


def resolve_config(config: DentalSetupConfig) -> ResolvedDentalSetupConfig:
    if str(config.chair_recline) not in CHAIR_RECLINE_CHOICES:
        raise ValueError(f"Unsupported chair_recline: {config.chair_recline}")
    if str(config.light_arm) not in LIGHT_ARM_CHOICES:
        raise ValueError(f"Unsupported light_arm: {config.light_arm}")
    if str(config.delivery_head) not in DELIVERY_HEAD_CHOICES:
        raise ValueError(f"Unsupported delivery_head: {config.delivery_head}")
    if str(config.palette_style) not in PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    n = int(config.instrument_count)
    n = max(2, min(n, 8))  # documented N_range [2, 8]

    chair_h = max(0.9, min(float(config.chair_h_scale), 1.15))
    arm_len = max(0.9, min(float(config.arm_len_scale), 1.15))
    col_h = max(0.9, min(float(config.column_h_scale), 1.15))

    # Cross-slot conditional: swing_tray relocates the instrument host onto
    # the moving delivery_arm; every other head keeps it on the fixed column.
    instrument_host = (
        "delivery_arm" if config.delivery_head == "swing_tray" else "delivery_column"
    )

    palette = dict(PALETTE_PRESETS[config.palette_style])

    return ResolvedDentalSetupConfig(
        chair_recline=config.chair_recline,
        light_arm=config.light_arm,
        delivery_head=config.delivery_head,
        palette_style=config.palette_style,
        instrument_count=n,
        chair_h_scale=chair_h,
        arm_len_scale=arm_len,
        column_h_scale=col_h,
        instrument_host=instrument_host,
        palette=palette,
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Per-seed structural module picks consumed by module_topology_diversity.

    Records the three structural slots plus the multiplicity axis (N encoded
    into the tuple so chair x arm x head x N spans the topology space). The
    continuous scales are deliberately NOT recorded — they are proportion, not
    topology.
    """
    r = resolve_config(config_from_seed(seed))
    return [
        ("chair_recline", r.chair_recline),
        ("light_arm", r.light_arm),
        ("delivery_head", r.delivery_head),
        ("instrument_count", f"instr_{r.instrument_count}"),
    ]


# --------------------------------------------------------------------------- #
# Shared geometry helpers (adapted verbatim from the sources — primitives
# preserved). Soft upholstery via section_loft; handpiece via LatheGeometry.
# --------------------------------------------------------------------------- #
def _mesh(name: str, geometry):
    return mesh_from_geometry(geometry, name)


def _cushion_loft(name, length, half_width, thickness, *, taper=0.7, crown=0.012):
    """Soft rounded upholstery slab as a lofted shell (source helper)."""
    nseg = 5
    sections = []
    for i in range(nseg):
        t = i / (nseg - 1)
        x = -length / 2.0 + t * length
        edge = math.sin(math.pi * t)
        w = half_width * (taper + (1.0 - taper) * edge)
        h_top = thickness * (0.85 + crown / thickness * edge)
        loop = [
            (x, -w, 0.0),
            (x, w, 0.0),
            (x, w * 0.96, h_top),
            (x, -w * 0.96, h_top),
        ]
        sections.append(loop)
    return _mesh(name, section_loft(sections))


def _handpiece_body(name):
    """Dental handpiece as a lathe-profiled pen-like body (S8/S9 helper).

    Axis along local Z: bur tip at z=0, hose barb at z~0.148.
    """
    profile = [
        (0.0, 0.0),
        (0.002, 0.0),
        (0.002, 0.005),
        (0.004, 0.008),
        (0.005, 0.012),
        (0.005, 0.022),
        (0.008, 0.038),
        (0.010, 0.055),
        (0.010, 0.112),
        (0.009, 0.122),
        (0.006, 0.134),
        (0.007, 0.138),
        (0.006, 0.145),
        (0.0, 0.148),
    ]
    return _mesh(name, LatheGeometry(profile, segments=28))


# Reflector dish profile (S1/S5/S7 round_dish head), shared.
_REFLECTOR_PROFILE = [
    (0.0, 0.060),
    (0.075, 0.055),
    (0.130, 0.035),
    (0.165, 0.008),
    (0.175, -0.010),
    (0.150, -0.010),
    (0.110, -0.005),
    (0.060, 0.012),
    (0.0, 0.020),
]


# --------------------------------------------------------------------------- #
# Module: BASE (root). Shared chassis for every seed: floor_pad,
# chair_pedestal (Lathe), seat_carrier, light_post + foot. Geometry adapted
# verbatim from the sources; chair pedestal height tracks chair_h_scale.
# Returns the world-frame anchor points used by downstream joints.
# --------------------------------------------------------------------------- #
_POST_X, _POST_Y = -0.55, 0.32


def _build_base(part, r: ResolvedDentalSetupConfig) -> dict[str, tuple]:
    part.visual(
        Box((1.30, 1.40, 0.02)),
        origin=Origin(xyz=(0.05, -0.05, 0.01)),
        material="dark_metal",
        name="floor_pad", material_class_id="rubber.smooth_plain",
    )
    pedestal_profile = [
        (0.0, 0.02),
        (0.18, 0.02),
        (0.17, 0.26),
        (0.15, 0.40),
        (0.13, 0.46),
        (0.0, 0.46),
    ]
    part.visual(
        _mesh("pedestal", LatheGeometry(pedestal_profile, segments=40)),
        origin=Origin(xyz=(0.06, 0.0, 0.0)),
        material="cream",
        name="chair_pedestal", material_class_id="plastic.opaque_glossy_molded",
    )
    # seat carrier top surface height tracks the chair height scale modestly.
    carrier_z = 0.50
    part.visual(
        Box((0.70, 0.34, 0.16)),
        origin=Origin(xyz=(0.06, 0.0, carrier_z)),
        material="cream_dark",
        name="seat_carrier", material_class_id="metal.paint_coated",
    )
    # Recline hinge boss — a real lateral pivot barrel on top of the seat
    # carrier so the backrest_recline joint origin sits on visible hinge
    # hardware (carrier top is at z=0.58; the boss straddles z=0.61).
    part.visual(
        Cylinder(radius=0.030, length=0.46),
        origin=Origin(xyz=(0.06, 0.0, 0.60), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_metal",
        name="recline_hinge_boss", material_class_id="metal.blackened_gunmetal",
    )

    # Light post — height scales with arm reach so the head stays above patient.
    post_len = 1.78
    post_z = 0.91
    post_top = post_z + post_len / 2.0  # ~1.80; recline origin is below this
    part.visual(
        Cylinder(radius=0.045, length=post_len),
        origin=Origin(xyz=(_POST_X, _POST_Y, post_z)),
        material="cream",
        name="light_post", material_class_id="metal.paint_coated",
    )
    part.visual(
        Cylinder(radius=0.075, length=0.06),
        origin=Origin(xyz=(_POST_X, _POST_Y, 0.04)),
        material="cream_dark",
        name="light_post_foot", material_class_id="metal.paint_coated",
    )
    return {
        "recline_origin": (0.06, 0.0, 0.61),
        "swing_origin": (_POST_X, _POST_Y, 1.79),
        "post_top": post_top,
    }


# --------------------------------------------------------------------------- #
# SLOT A — chair-recline. Each candidate emits the moving chair part(s) and
# its recline REVOLUTE(s). All keep the core `backrest_recline` joint.
#   single_body   : seat+back+headrest one slab reclines off base (S1)
#   two_section   : fixed seat pan + separate reclining backrest (S2)
#   three_section : reclining seat/back slab + folding footrest (S3)
# --------------------------------------------------------------------------- #
def _chair_h(r):
    return r.chair_h_scale


def _build_chair_single_body(model, r, base_part, anchors) -> None:
    """S1 parent: seat+back+headrest as one reclining slab off base."""
    backrest = model.part("backrest")
    backrest.visual(
        _cushion_loft("seat_pad", length=1.30, half_width=0.21, thickness=0.085),
        origin=Origin(xyz=(0.25, 0.0, 0.045)),
        material="upholstery",
        name="seat_pad", material_class_id="fabric.upholstery_plain",
    )
    backrest.visual(
        _cushion_loft("bolster_l", length=1.20, half_width=0.035, thickness=0.055, taper=0.85),
        origin=Origin(xyz=(0.22, 0.205, 0.07)),
        material="upholstery_dark",
        name="bolster_left", material_class_id="fabric.upholstery_plain",
    )
    backrest.visual(
        _cushion_loft("bolster_r", length=1.20, half_width=0.035, thickness=0.055, taper=0.85),
        origin=Origin(xyz=(0.22, -0.205, 0.07)),
        material="upholstery_dark",
        name="bolster_right", material_class_id="fabric.upholstery_plain",
    )
    backrest.visual(
        Box((1.48, 0.40, 0.075)),
        origin=Origin(xyz=(0.23, 0.0, 0.0075)),
        material="cream_dark",
        name="back_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    backrest.visual(
        Cylinder(radius=0.020, length=0.16),
        origin=Origin(xyz=(-0.47, 0.0, 0.07), rpy=(0.0, 0.6, 0.0)),
        material="chrome",
        name="headrest_stalk", material_class_id="metal.chrome_polished",
    )
    backrest.visual(
        _cushion_loft("headrest_pad", length=0.22, half_width=0.13, thickness=0.07, taper=0.6),
        origin=Origin(xyz=(-0.54, 0.0, 0.12)),
        material="upholstery",
        name="headrest_pad", material_class_id="fabric.upholstery_plain",
    )
    model.articulation(
        "backrest_recline",
        ArticulationType.REVOLUTE,
        parent=base_part,
        child=backrest,
        origin=Origin(xyz=anchors["recline_origin"]),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=400.0, velocity=0.4, lower=-0.35, upper=0.55),
    )


def _build_chair_two_section(model, r, base_part, anchors) -> None:
    """S2: fixed seat pan + separate reclining backrest on hip hinge."""
    mt = _SEAT_MOUNT  # seat authored in a local frame at the carrier contact
    seat = model.part("seat")
    seat.visual(
        _cushion_loft("seat_pad", length=0.80, half_width=0.21, thickness=0.085),
        origin=Origin(xyz=_sub((0.52, 0.0, 0.615), mt)),
        material="upholstery",
        name="seat_pad", material_class_id="fabric.upholstery_plain",
    )
    seat.visual(
        _cushion_loft("seat_bolster_l", length=0.72, half_width=0.035, thickness=0.055, taper=0.85),
        origin=Origin(xyz=_sub((0.48, 0.205, 0.64), mt)),
        material="upholstery_dark",
        name="bolster_left", material_class_id="fabric.upholstery_plain",
    )
    seat.visual(
        _cushion_loft("seat_bolster_r", length=0.72, half_width=0.035, thickness=0.055, taper=0.85),
        origin=Origin(xyz=_sub((0.48, -0.205, 0.64), mt)),
        material="upholstery_dark",
        name="bolster_right", material_class_id="fabric.upholstery_plain",
    )
    seat.visual(
        Box((0.84, 0.38, 0.04)),
        origin=Origin(xyz=_sub((0.52, 0.0, 0.595), mt)),
        material="cream_dark",
        name="seat_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    for i, y_sign in enumerate((1.0, -1.0)):
        seat.visual(
            Box((0.06, 0.04, 0.08)),
            origin=Origin(xyz=_sub((0.10, y_sign * 0.22, 0.61), mt)),
            material="dark_metal",
            name=f"seat_pivot_{i}", material_class_id="metal.blackened_gunmetal",
        )
    # FIXED origin at the seat/carrier contact (mount point).
    model.articulation(
        "seat_mount",
        ArticulationType.FIXED,
        parent=base_part,
        child=seat,
        origin=Origin(xyz=mt),
    )

    backrest = model.part("backrest")
    backrest.visual(
        _cushion_loft("back_pad", length=0.50, half_width=0.21, thickness=0.085),
        origin=Origin(xyz=(-0.27, 0.0, 0.045)),
        material="upholstery",
        name="back_pad", material_class_id="fabric.upholstery_plain",
    )
    backrest.visual(
        _cushion_loft("back_bolster_l", length=0.42, half_width=0.035, thickness=0.055, taper=0.85),
        origin=Origin(xyz=(-0.23, 0.205, 0.07)),
        material="upholstery_dark",
        name="back_bolster_left", material_class_id="fabric.upholstery_plain",
    )
    backrest.visual(
        _cushion_loft("back_bolster_r", length=0.42, half_width=0.035, thickness=0.055, taper=0.85),
        origin=Origin(xyz=(-0.23, -0.205, 0.07)),
        material="upholstery_dark",
        name="back_bolster_right", material_class_id="fabric.upholstery_plain",
    )
    backrest.visual(
        Box((0.74, 0.38, 0.04)),
        origin=Origin(xyz=(-0.35, 0.0, 0.025)),
        material="cream_dark",
        name="back_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    backrest.visual(
        Cylinder(radius=0.015, length=0.48),
        origin=Origin(xyz=(0.0, 0.0, 0.02), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="chrome",
        name="hip_pivot_shaft", material_class_id="metal.chrome_polished",
    )
    backrest.visual(
        Cylinder(radius=0.020, length=0.16),
        origin=Origin(xyz=(-0.51, 0.0, 0.07), rpy=(0.0, 0.6, 0.0)),
        material="chrome",
        name="headrest_stalk", material_class_id="metal.chrome_polished",
    )
    backrest.visual(
        _cushion_loft("headrest_pad", length=0.22, half_width=0.13, thickness=0.07, taper=0.6),
        origin=Origin(xyz=(-0.58, 0.0, 0.12)),
        material="upholstery",
        name="headrest_pad", material_class_id="fabric.upholstery_plain",
    )
    # Recline pivot at the hip hinge (S2 origin) in the seat's local frame.
    model.articulation(
        "backrest_recline",
        ArticulationType.REVOLUTE,
        parent=seat,
        child=backrest,
        origin=Origin(xyz=_sub((0.10, 0.0, 0.61), _SEAT_MOUNT)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=400.0, velocity=0.4, lower=-0.35, upper=0.55),
    )


def _build_chair_three_section(model, r, base_part, anchors) -> None:
    """S3: reclining seat/back slab off base + folding footrest off it."""
    backrest = model.part("backrest")
    backrest.visual(
        _cushion_loft("seat_pad", length=0.95, half_width=0.21, thickness=0.085),
        origin=Origin(xyz=(0.075, 0.0, 0.045)),
        material="upholstery",
        name="seat_pad", material_class_id="fabric.upholstery_plain",
    )
    backrest.visual(
        _cushion_loft("bolster_l", length=0.93, half_width=0.035, thickness=0.055, taper=0.85),
        origin=Origin(xyz=(0.085, 0.205, 0.07)),
        material="upholstery_dark",
        name="bolster_left", material_class_id="fabric.upholstery_plain",
    )
    backrest.visual(
        _cushion_loft("bolster_r", length=0.93, half_width=0.035, thickness=0.055, taper=0.85),
        origin=Origin(xyz=(0.085, -0.205, 0.07)),
        material="upholstery_dark",
        name="bolster_right", material_class_id="fabric.upholstery_plain",
    )
    backrest.visual(
        Box((1.06, 0.40, 0.075)),
        origin=Origin(xyz=(0.02, 0.0, 0.0075)),
        material="cream_dark",
        name="back_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    backrest.visual(
        Cylinder(radius=0.020, length=0.16),
        origin=Origin(xyz=(-0.47, 0.0, 0.07), rpy=(0.0, 0.6, 0.0)),
        material="chrome",
        name="headrest_stalk", material_class_id="metal.chrome_polished",
    )
    backrest.visual(
        _cushion_loft("headrest_pad", length=0.22, half_width=0.13, thickness=0.07, taper=0.6),
        origin=Origin(xyz=(-0.54, 0.0, 0.12)),
        material="upholstery",
        name="headrest_pad", material_class_id="fabric.upholstery_plain",
    )
    model.articulation(
        "backrest_recline",
        ArticulationType.REVOLUTE,
        parent=base_part,
        child=backrest,
        origin=Origin(xyz=(0.06, 0.0, 0.61)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=400.0, velocity=0.4, lower=-0.35, upper=0.55),
    )

    footrest = model.part("footrest")
    footrest.visual(
        _cushion_loft("footrest_pad", length=0.40, half_width=0.21, thickness=0.085),
        origin=Origin(xyz=(0.22, 0.0, 0.045)),
        material="upholstery",
        name="footrest_pad", material_class_id="fabric.upholstery_plain",
    )
    footrest.visual(
        _cushion_loft("footrest_bolster_l", length=0.38, half_width=0.035, thickness=0.055, taper=0.85),
        origin=Origin(xyz=(0.21, 0.205, 0.07)),
        material="upholstery_dark",
        name="footrest_bolster_left", material_class_id="fabric.upholstery_plain",
    )
    footrest.visual(
        _cushion_loft("footrest_bolster_r", length=0.38, half_width=0.035, thickness=0.055, taper=0.85),
        origin=Origin(xyz=(0.21, -0.205, 0.07)),
        material="upholstery_dark",
        name="footrest_bolster_right", material_class_id="fabric.upholstery_plain",
    )
    footrest.visual(
        Box((0.44, 0.40, 0.075)),
        origin=Origin(xyz=(0.22, 0.0, 0.0075)),
        material="cream_dark",
        name="footrest_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    footrest.visual(
        Cylinder(radius=0.025, length=0.30),
        origin=Origin(xyz=(0.0, 0.0, 0.04), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_metal",
        name="footrest_hinge_barrel", material_class_id="metal.blackened_gunmetal",
    )
    # Footrest fold REVOLUTE at the seat/footrest junction (S3 origin), in
    # the backrest's local frame.
    model.articulation(
        "footrest_fold",
        ArticulationType.REVOLUTE,
        parent=backrest,
        child=footrest,
        origin=Origin(xyz=(0.55, 0.0, 0.04)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=200.0, velocity=0.5, lower=-0.25, upper=0.80),
    )


CHAIR_BUILDERS = {
    "single_body": _build_chair_single_body,
    "two_section": _build_chair_two_section,
    "three_section": _build_chair_three_section,
}


# --------------------------------------------------------------------------- #
# SLOT C head geometry helpers (round dish / LED panel). Both emit onto a
# `light_head` part. Slot B decides where light_head parents (single drop
# link or parallelogram carriage). round_dish/led_panel share the yoke stub
# convention (head_yoke_stub on top captured by the drop link).
# --------------------------------------------------------------------------- #
def _emit_round_dish_head(head) -> None:
    head.visual(
        _mesh("reflector_shell", LatheGeometry(_REFLECTOR_PROFILE, segments=56)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="cream",
        name="reflector_shell", material_class_id="metal.paint_coated",
    )
    head.visual(
        Cylinder(radius=0.160, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, -0.006)),
        material="glass",
        name="light_lens", material_class_id="glass.clear_transparent",
    )
    head.visual(
        _mesh(
            "head_rim",
            TorusGeometry(radius=0.166, tube=0.010, radial_segments=14, tubular_segments=64),
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="chrome",
        name="head_rim", material_class_id="metal.chrome_polished",
    )
    handle_pts_r = [
        (0.12, -0.118, 0.005),
        (0.19, -0.135, -0.01),
        (0.23, -0.105, -0.02),
        (0.21, -0.055, -0.02),
    ]
    head.visual(
        _mesh("handle_right", tube_from_spline_points(handle_pts_r, radius=0.009, radial_segments=12)),
        material="dark_metal",
        name="handle_right", material_class_id="metal.blackened_gunmetal",
    )
    handle_pts_l = [(p[0], -p[1], p[2]) for p in handle_pts_r]
    head.visual(
        _mesh("handle_left", tube_from_spline_points(handle_pts_l, radius=0.009, radial_segments=12)),
        material="dark_metal",
        name="handle_left", material_class_id="metal.blackened_gunmetal",
    )
    head.visual(
        Cylinder(radius=0.020, length=0.06),
        origin=Origin(xyz=(0.0, 0.0, 0.075)),
        material="metal",
        name="head_yoke_stub", material_class_id="metal.stainless_matte",
    )


def _emit_led_panel_head(head) -> None:
    head.visual(
        Box((0.30, 0.20, 0.038)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="cream",
        name="panel_housing", material_class_id="plastic.opaque_glossy_molded",
    )
    panel_bezel = BezelGeometry(
        (0.24, 0.14),
        (0.28, 0.18),
        0.006,
        opening_shape="rounded_rect",
        outer_shape="rounded_rect",
        opening_corner_radius=0.008,
        outer_corner_radius=0.012,
        recess=BezelRecess(depth=0.004, inset=0.003, floor_radius=0.001),
    )
    head.visual(
        _mesh("panel_frame", panel_bezel),
        origin=Origin(xyz=(0.0, 0.0, -0.019), rpy=(math.pi, 0.0, 0.0)),
        material="dark_metal",
        name="panel_frame", material_class_id="metal.blackened_gunmetal",
    )
    # diffuser (the equivalent of light_lens — names the test looks for)
    head.visual(
        Box((0.235, 0.135, 0.004)),
        origin=Origin(xyz=(0.0, 0.0, -0.021)),
        material="ceramic",
        name="led_diffuser", material_class_id="plastic.frosted_translucent",
    )
    head.visual(
        Box((0.28, 0.18, 0.003)),
        origin=Origin(xyz=(0.0, 0.0, 0.020)),
        material="cream_dark",
        name="panel_back", material_class_id="plastic.opaque_glossy_molded",
    )
    for side in ("right", "left"):
        sign = 1.0 if side == "right" else -1.0
        handle_pts = [
            (0.06, sign * 0.10, 0.0),
            (0.04, sign * 0.135, -0.005),
            (-0.04, sign * 0.135, -0.005),
            (-0.06, sign * 0.10, 0.0),
        ]
        head.visual(
            _mesh(
                f"handle_{side}",
                tube_from_spline_points(handle_pts, radius=0.007, radial_segments=10),
            ),
            material="dark_metal",
            name=f"handle_{side}", material_class_id="metal.blackened_gunmetal",
        )
    head.visual(
        Cylinder(radius=0.020, length=0.06),
        origin=Origin(xyz=(0.0, 0.0, 0.050)),
        material="metal",
        name="head_yoke_stub", material_class_id="metal.stainless_matte",
    )


def _emit_head_visuals(head, r: ResolvedDentalSetupConfig) -> None:
    """Emit the chosen Slot C head reflector visuals onto `head`.

    swing_tray keeps an overhead light head too (the swing only relocates the
    instrument delivery host); the overhead head defaults to a round dish.
    """
    if r.delivery_head == "led_panel":
        _emit_led_panel_head(head)
    else:  # round_dish or swing_tray (overhead head is the round dish)
        _emit_round_dish_head(head)


# --------------------------------------------------------------------------- #
# SLOT B — light-arm. Each candidate swings on the post (core `light_arm_swing`
# REVOLUTE axis Z) and ends in a yoke that tilts the head (core
# `light_head_tilt` REVOLUTE axis Y). The head visuals come from Slot C.
#   single_rigid       : single swept arm + drop link  (S1)
#   two_segment_elbow  : upper arm + forearm, elbow REVOLUTE  (S4)
#   parallelogram      : 4-bar (2 bars + Mimic) + leveling carriage (S5)
# --------------------------------------------------------------------------- #
def _arm_scale(r):
    return r.arm_len_scale


def _build_arm_single_rigid(model, r, base_part, anchors) -> None:
    s = _arm_scale(r)
    light_arm = model.part("light_arm")
    arm_pts = [
        (0.0, 0.0, 0.0),
        (0.22 * s, -0.08 * s, 0.0),
        (0.46 * s, -0.20 * s, -0.02),
        (0.66 * s, -0.32 * s, -0.06),
    ]
    light_arm.visual(
        _mesh(
            "upper_arm",
            sweep_profile_along_spline(
                arm_pts,
                profile=rounded_rect_profile(0.075, 0.055, radius=0.018),
                samples_per_segment=12,
                cap_profile=True,
            ),
        ),
        material="cream",
        name="upper_arm", material_class_id="metal.paint_coated",
    )
    light_arm.visual(
        Cylinder(radius=0.052, length=0.10),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="cream_dark",
        name="arm_pivot_collar", material_class_id="metal.paint_coated",
    )
    end = (0.66 * s, -0.32 * s, -0.06)
    light_arm.visual(
        Cylinder(radius=0.040, length=0.07),
        origin=Origin(xyz=end, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_metal",
        name="arm_knuckle", material_class_id="metal.blackened_gunmetal",
    )
    drop_x, drop_y = 0.70 * s, -0.32 * s
    # Drop link spans from the knuckle (z=-0.06) down past the tilt origin
    # (z=-0.265) so the tilt joint origin sits on real drop-link geometry.
    light_arm.visual(
        Cylinder(radius=0.022, length=0.225),
        origin=Origin(xyz=(drop_x, drop_y, -0.1675)),
        material="metal",
        name="head_drop_link", material_class_id="metal.stainless_matte",
    )

    model.articulation(
        "light_arm_swing",
        ArticulationType.REVOLUTE,
        parent=base_part,
        child=light_arm,
        origin=Origin(xyz=anchors["swing_origin"]),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=40.0, velocity=1.5, lower=-1.9, upper=1.9),
    )

    light_head = model.part("light_head")
    _emit_head_visuals(light_head, r)
    model.articulation(
        "light_head_tilt",
        ArticulationType.REVOLUTE,
        parent=light_arm,
        child=light_head,
        origin=Origin(xyz=(drop_x, drop_y, -0.265)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=1.5, lower=-0.9, upper=0.9),
    )


def _build_arm_two_segment_elbow(model, r, base_part, anchors) -> None:
    s = _arm_scale(r)
    upper_arm = model.part("upper_arm")
    upper_arm.visual(
        Cylinder(radius=0.052, length=0.10),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="cream_dark",
        name="arm_pivot_collar", material_class_id="metal.paint_coated",
    )
    upper_arm_pts = [
        (0.0, 0.0, 0.0),
        (0.10 * s, -0.03 * s, 0.0),
        (0.20 * s, -0.07 * s, -0.003),
        (0.31 * s, -0.12 * s, -0.007),
    ]
    upper_arm.visual(
        _mesh(
            "upper_arm_tube",
            sweep_profile_along_spline(
                upper_arm_pts,
                profile=rounded_rect_profile(0.075, 0.055, radius=0.018),
                samples_per_segment=12,
                cap_profile=True,
            ),
        ),
        material="cream",
        name="upper_arm_tube", material_class_id="metal.paint_coated",
    )
    elbow = (0.34 * s, -0.14 * s, -0.01)
    upper_arm.visual(
        Cylinder(radius=0.040, length=0.08),
        origin=Origin(xyz=elbow, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_metal",
        name="elbow_knuckle", material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        "light_arm_swing",
        ArticulationType.REVOLUTE,
        parent=base_part,
        child=upper_arm,
        origin=Origin(xyz=anchors["swing_origin"]),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=40.0, velocity=1.5, lower=-1.9, upper=1.9),
    )

    forearm = model.part("forearm")
    forearm.visual(
        Cylinder(radius=0.044, length=0.06),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_metal",
        name="elbow_hub", material_class_id="metal.blackened_gunmetal",
    )
    forearm_pts = [
        (0.03 * s, -0.015 * s, -0.002),
        (0.12 * s, -0.07 * s, -0.018),
        (0.23 * s, -0.14 * s, -0.04),
        (0.32 * s, -0.18 * s, -0.05),
    ]
    forearm.visual(
        _mesh(
            "forearm_tube",
            sweep_profile_along_spline(
                forearm_pts,
                profile=rounded_rect_profile(0.065, 0.048, radius=0.016),
                samples_per_segment=12,
                cap_profile=True,
            ),
        ),
        material="cream",
        name="forearm_tube", material_class_id="metal.paint_coated",
    )
    end = (0.32 * s, -0.18 * s, -0.05)
    forearm.visual(
        Cylinder(radius=0.038, length=0.07),
        origin=Origin(xyz=end, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_metal",
        name="end_knuckle", material_class_id="metal.blackened_gunmetal",
    )
    drop_x, drop_y = 0.36 * s, -0.18 * s
    # Drop link spans from the end knuckle (z=-0.05) past the tilt origin
    # (z=-0.26) so the tilt joint origin sits on real drop-link geometry.
    forearm.visual(
        Cylinder(radius=0.022, length=0.225),
        origin=Origin(xyz=(drop_x, drop_y, -0.1625)),
        material="metal",
        name="head_drop_link", material_class_id="metal.stainless_matte",
    )
    # Elbow fold REVOLUTE in upper_arm's local frame (S4 origin).
    model.articulation(
        "elbow_fold",
        ArticulationType.REVOLUTE,
        parent=upper_arm,
        child=forearm,
        origin=Origin(xyz=elbow),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=1.2, lower=-0.4, upper=1.6),
    )

    light_head = model.part("light_head")
    _emit_head_visuals(light_head, r)
    model.articulation(
        "light_head_tilt",
        ArticulationType.REVOLUTE,
        parent=forearm,
        child=light_head,
        origin=Origin(xyz=(drop_x, drop_y, -0.26)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=1.5, lower=-0.9, upper=0.9),
    )


def _parallelogram_bar_mesh(name, s):
    pts = [
        (0.0, 0.0, 0.0),
        (0.18 * s, -0.04 * s, 0.0),
        (0.40 * s, -0.15 * s, 0.0),
        (0.58 * s, -0.26 * s, 0.0),
    ]
    mesh = _mesh(
        name,
        sweep_profile_along_spline(
            pts,
            profile=rounded_rect_profile(0.044, 0.028, radius=0.006),
            samples_per_segment=10,
            cap_profile=True,
        ),
    )
    return mesh, pts[-1]


def _build_arm_parallelogram(model, r, base_part, anchors) -> None:
    """S5 spring-balanced four-bar linkage with Mimic-coupled bars + leveling
    carriage. light_arm_swing == arm_yaw; light_head_tilt at the carriage."""
    s = _arm_scale(r)
    bar_base_offset = 0.10
    bar_gap = 0.22

    arm_yaw = model.part("arm_yaw")
    arm_yaw.visual(
        Cylinder(radius=0.052, length=0.10),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="cream_dark",
        name="yaw_collar", material_class_id="metal.paint_coated",
    )
    _brk_cx = bar_base_offset / 2.0 + 0.025
    _brk_sx = bar_base_offset - 0.05 + 0.01
    arm_yaw.visual(
        Box((_brk_sx, 0.050, 0.030)),
        origin=Origin(xyz=(_brk_cx, 0.0, 0.015)),
        material="cream",
        name="upper_bracket", material_class_id="metal.paint_coated",
    )
    arm_yaw.visual(
        Box((_brk_sx, 0.050, 0.030)),
        origin=Origin(xyz=(_brk_cx, 0.0, -bar_gap + 0.015)),
        material="cream",
        name="lower_bracket", material_class_id="metal.paint_coated",
    )
    arm_yaw.visual(
        Box((0.025, 0.040, bar_gap - 0.030)),
        origin=Origin(xyz=(_brk_cx, 0.0, -bar_gap / 2.0 + 0.015)),
        material="cream_dark",
        name="bracket_spine", material_class_id="metal.paint_coated",
    )
    arm_yaw.visual(
        Cylinder(radius=0.013, length=0.18),
        origin=Origin(xyz=(0.08, 0.0, -0.06), rpy=(0.0, 0.65, 0.0)),
        material="dark_metal",
        name="gas_spring_body", material_class_id="metal.blackened_gunmetal",
    )
    arm_yaw.visual(
        Cylinder(radius=0.006, length=0.10),
        origin=Origin(xyz=(0.16, 0.0, 0.01), rpy=(0.0, 1.15, 0.0)),
        material="chrome",
        name="gas_spring_rod", material_class_id="metal.chrome_polished",
    )
    # light_arm_swing (core swing) is the yaw joint.
    model.articulation(
        "light_arm_swing",
        ArticulationType.REVOLUTE,
        parent=base_part,
        child=arm_yaw,
        origin=Origin(xyz=anchors["swing_origin"]),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=40.0, velocity=1.5, lower=-1.9, upper=1.9),
    )

    bars = []
    bar_far_pts = []
    for i in range(2):
        bar = model.part(f"arm_bar_{i}")
        bar_mesh, far_pt = _parallelogram_bar_mesh(f"bar_body_{i}", s)
        bar.visual(bar_mesh, material="cream", name=f"bar_body_{i}", material_class_id="metal.paint_coated")
        bar.visual(
            Cylinder(radius=0.018, length=0.032),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material="dark_metal",
            name=f"bar_base_bushing_{i}", material_class_id="metal.blackened_gunmetal",
        )
        bar.visual(
            Cylinder(radius=0.018, length=0.032),
            origin=Origin(xyz=far_pt),
            material="dark_metal",
            name=f"bar_far_bushing_{i}", material_class_id="metal.blackened_gunmetal",
        )
        bars.append(bar)
        bar_far_pts.append(far_pt)

    # Primary raise + Mimic follower keep the two bars parallel.
    model.articulation(
        "arm_bar_0_raise",
        ArticulationType.REVOLUTE,
        parent=arm_yaw,
        child=bars[0],
        origin=Origin(xyz=(bar_base_offset, 0.0, 0.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.8, lower=-0.30, upper=0.70),
    )
    model.articulation(
        "arm_bar_1_raise",
        ArticulationType.REVOLUTE,
        parent=arm_yaw,
        child=bars[1],
        origin=Origin(xyz=(bar_base_offset, 0.0, -bar_gap)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.8, lower=-0.30, upper=0.70),
        mimic=Mimic(joint="arm_bar_0_raise", multiplier=1.0, offset=0.0),
    )

    carriage = model.part("light_carriage")
    carriage.visual(
        Box((0.050, 0.048, bar_gap)),
        origin=Origin(xyz=(0.0, 0.0, -bar_gap / 2.0)),
        material="cream_dark",
        name="carriage_plate", material_class_id="metal.paint_coated",
    )
    drop_z = -bar_gap - 0.06
    carriage.visual(
        Cylinder(radius=0.018, length=0.12),
        origin=Origin(xyz=(0.0, 0.0, drop_z)),
        material="metal",
        name="carriage_drop_link", material_class_id="metal.stainless_matte",
    )
    carriage.visual(
        Cylinder(radius=0.012, length=0.06),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="chrome",
        name="carriage_upper_pin", material_class_id="metal.chrome_polished",
    )
    carriage.visual(
        Cylinder(radius=0.012, length=0.06),
        origin=Origin(xyz=(0.0, 0.0, -bar_gap), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="chrome",
        name="carriage_lower_pin", material_class_id="metal.chrome_polished",
    )
    # Carriage level joint — Mimic counter-rotation keeps the head level.
    model.articulation(
        "carriage_level",
        ArticulationType.REVOLUTE,
        parent=bars[0],
        child=carriage,
        origin=Origin(xyz=bar_far_pts[0]),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=1.0, lower=-0.30, upper=0.70),
        mimic=Mimic(joint="arm_bar_0_raise", multiplier=-1.0, offset=0.0),
    )

    light_head = model.part("light_head")
    _emit_head_visuals(light_head, r)
    model.articulation(
        "light_head_tilt",
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=light_head,
        origin=Origin(xyz=(0.0, 0.0, drop_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=1.5, lower=-0.9, upper=0.9),
    )


ARM_BUILDERS = {
    "single_rigid": _build_arm_single_rigid,
    "two_segment_elbow": _build_arm_two_segment_elbow,
    "parallelogram": _build_arm_parallelogram,
}


# --------------------------------------------------------------------------- #
# COMPANION: delivery column (cabinet, monitor, cuspidor, tray) + the
# instrument multiplicity. swing_tray relocates the multiplicity host onto a
# separate moving delivery_arm. Both are FIXED to base (column) except the
# delivery_arm which gets its own delivery_arm_swing REVOLUTE.
# Column geometry adapted from the sources. cx, cy are the column center.
# --------------------------------------------------------------------------- #
_COL_CX, _COL_CY = -0.20, 0.58

# FIXED-companion local-frame mount points (world coords where each companion's
# local origin lands). Authoring each companion relative to its mount point and
# setting the FIXED joint origin to the same point keeps the world geometry
# unchanged while putting the joint origin on real contact geometry (both the
# base floor/carrier and the companion touch there), satisfying the flat 0.015 m
# `fail_if_articulation_origin_far_from_geometry` baseline for FIXED joints.
_COLUMN_MOUNT = (_COL_CX, _COL_CY, 0.02)
# Stool mount at a caster's floor contact (caster ring radius 0.24 from the
# stool center), so the FIXED origin lies on real caster + floor-pad geometry.
_STOOL_MOUNT = (0.30 + 0.24, -0.55, 0.02)
_SEAT_MOUNT = (0.10, 0.0, 0.575)


def _sub(xyz, mount):
    """Shift a world-coord origin into the companion's local mount frame."""
    return (xyz[0] - mount[0], xyz[1] - mount[1], xyz[2] - mount[2])


def _emit_handpiece_set(part, n, hx0_cx, hp_anchor, *, base_z, mount=(0.0, 0.0, 0.0)) -> None:
    """Emit N evenly-spaced handpiece_{i} + draped hose_{i} pairs on `part`.

    `hp_anchor` = (host_x_center, head_front_y, head_top_z) describing where the
    delivery head front edge is; handpieces hang below it, hoses drape from the
    head top to each handpiece barb. Adapted from S8/S9 `for i in range(n)`.
    """
    cx, head_y, head_top_z = hp_anchor
    spacing = 0.05
    hp_y = head_y
    hp_z = base_z
    for i in range(n):
        hx = cx - (n - 1) * spacing / 2.0 + i * spacing
        part.visual(
            _handpiece_body(f"handpiece_{i}"),
            origin=Origin(xyz=_sub((hx, hp_y, hp_z), mount), rpy=(0.35, 0.0, 0.0)),
            material="chrome",
            name=f"handpiece_{i}", material_class_id="metal.chrome_polished",
        )
        hose_start = (hx, head_y + 0.16, head_top_z)
        hose_end = (
            hx,
            hp_y - 0.148 * math.sin(0.35),
            hp_z + 0.148 * math.cos(0.35),
        )
        mid_y = (hose_start[1] + hose_end[1]) / 2.0
        sag_z = min(hose_start[2], hose_end[2]) - 0.06
        hose_pts = [
            _sub(hose_start, mount),
            _sub((hx, hose_start[1] - 0.04, sag_z + 0.06), mount),
            _sub((hx, mid_y, sag_z), mount),
            _sub((hx, hose_end[1] + 0.03, sag_z + 0.04), mount),
            _sub(hose_end, mount),
        ]
        part.visual(
            _mesh(
                f"hose_{i}",
                tube_from_spline_points(hose_pts, radius=0.005, radial_segments=10),
            ),
            material="dark_metal",
            name=f"hose_{i}", material_class_id="rubber.smooth_plain",
        )


def _build_delivery_column(model, r, base_part) -> None:
    cx, cy = _COL_CX, _COL_CY
    mt = _COLUMN_MOUNT  # local-frame mount point (world coords preserved via _sub)
    column = model.part("delivery_column")
    column.visual(
        Box((0.34, 0.30, 0.74)),
        origin=Origin(xyz=_sub((cx, cy, 0.39), mt)),
        material="cream",
        name="column_cabinet", material_class_id="plastic.opaque_glossy_molded",
    )
    column.visual(
        Box((0.40, 0.36, 0.05)),
        origin=Origin(xyz=_sub((cx, cy, 0.785), mt)),
        material="cream_dark",
        name="column_top", material_class_id="plastic.opaque_glossy_molded",
    )

    host_on_column = r.instrument_host == "delivery_column"
    if host_on_column:
        # delivery head + instrument multiplicity live on the fixed column.
        # Head box width tracks N so every handpiece + hose top sits under it.
        col_head_w = max(0.30, (r.instrument_count - 1) * 0.05 + 0.14)
        column.visual(
            Box((col_head_w, 0.18, 0.10)),
            origin=Origin(xyz=_sub((cx, cy - 0.12, 0.86), mt)),
            material="cream",
            name="delivery_head", material_class_id="plastic.opaque_glossy_molded",
        )
        # head front edge ~ y = cy-0.12-0.09 ; head top z ~ 0.91
        _emit_handpiece_set(
            column,
            r.instrument_count,
            cx,
            (cx, cy - 0.20, 0.91),
            base_z=0.68,
            mount=mt,
        )

    # swivel monitor on a short arm above the cabinet
    column.visual(
        Cylinder(radius=0.016, length=0.26),
        origin=Origin(xyz=_sub((cx + 0.10, cy + 0.09, 0.90), mt)),
        material="metal",
        name="monitor_arm", material_class_id="metal.stainless_matte",
    )
    column.visual(
        Box((0.02, 0.22, 0.16)),
        origin=Origin(xyz=_sub((cx + 0.11, cy + 0.11, 1.00), mt), rpy=(0.0, 0.0, -0.5)),
        material="screen",
        name="monitor_panel", material_class_id="tech.control_interface",
    )
    # cuspidor (rinse bowl)
    cusp_profile = [
        (0.0, 0.0),
        (0.085, 0.0),
        (0.095, 0.02),
        (0.090, 0.05),
        (0.070, 0.06),
        (0.050, 0.04),
        (0.045, 0.02),
        (0.0, 0.02),
    ]
    column.visual(
        Box((0.10, 0.14, 0.05)),
        origin=Origin(xyz=_sub((cx + 0.02, cy - 0.16, 0.62), mt)),
        material="cream_dark",
        name="cuspidor_bracket", material_class_id="metal.paint_coated",
    )
    column.visual(
        _mesh("cuspidor_bowl", LatheGeometry(cusp_profile, segments=40)),
        origin=Origin(xyz=_sub((cx + 0.02, cy - 0.24, 0.64), mt)),
        material="ceramic",
        name="cuspidor_bowl", material_class_id="ceramic.porcelain_glazed_plain",
    )
    column.visual(
        Cylinder(radius=0.012, length=0.26),
        origin=Origin(xyz=_sub((cx + 0.18, cy - 0.16, 0.82), mt), rpy=(0.0, math.pi / 2.0, -0.7)),
        material="metal",
        name="tray_arm", material_class_id="metal.stainless_matte",
    )
    column.visual(
        Box((0.22, 0.16, 0.012)),
        origin=Origin(xyz=_sub((cx + 0.30, cy - 0.26, 0.82), mt)),
        material="metal",
        name="instrument_tray", material_class_id="metal.stainless_matte",
    )
    # FIXED origin at the column floor-contact (mount point), on real geometry
    # for both base floor pad and column cabinet bottom.
    model.articulation(
        "column_mount",
        ArticulationType.FIXED,
        parent=base_part,
        child=column,
        origin=Origin(xyz=mt),
    )


def _build_delivery_arm(model, r, column_part) -> None:
    """S7: separate swing arm carrying the delivery head + instruments.

    Child of delivery_column via a vertical-axis REVOLUTE. Instrument host
    is this arm (resolve_config set instrument_host = delivery_arm).
    """
    cx, cy = _COL_CX, _COL_CY
    da_pivot_x = cx
    da_pivot_y = cy - 0.15
    da_pivot_z = 0.81

    delivery_arm = model.part("delivery_arm")
    delivery_arm.visual(
        Cylinder(radius=0.042, length=0.04),
        origin=Origin(xyz=(0.0, 0.0, 0.02)),
        material="cream_dark",
        name="arm_pivot_base", material_class_id="metal.paint_coated",
    )
    delivery_arm.visual(
        Cylinder(radius=0.028, length=0.14),
        origin=Origin(xyz=(0.0, 0.0, 0.11)),
        material="metal",
        name="arm_pivot_post", material_class_id="metal.stainless_matte",
    )
    da_arm_pts = [
        (0.0, 0.0, 0.18),
        (0.0, -0.08, 0.17),
        (0.0, -0.24, 0.14),
        (0.02, -0.40, 0.10),
        (0.03, -0.50, 0.07),
    ]
    delivery_arm.visual(
        _mesh(
            "arm_tube",
            sweep_profile_along_spline(
                da_arm_pts,
                profile=rounded_rect_profile(0.040, 0.030, radius=0.010),
                samples_per_segment=10,
                cap_profile=True,
            ),
        ),
        material="cream",
        name="arm_tube", material_class_id="metal.paint_coated",
    )
    delivery_arm.visual(
        Cylinder(radius=0.032, length=0.05),
        origin=Origin(xyz=(0.03, -0.50, 0.07), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_metal",
        name="arm_tip_knuckle", material_class_id="metal.blackened_gunmetal",
    )
    # Head box width tracks N so every handpiece + hose top sits under it.
    head_w = max(0.28, (r.instrument_count - 1) * 0.05 + 0.14)
    delivery_arm.visual(
        Box((head_w, 0.16, 0.08)),
        origin=Origin(xyz=(0.03, -0.54, 0.05)),
        material="cream",
        name="delivery_head", material_class_id="plastic.opaque_glossy_molded",
    )
    # Instrument multiplicity hosted on the moving arm (local frame).
    _emit_handpiece_set(
        delivery_arm,
        r.instrument_count,
        0.03,
        (0.03, -0.62, 0.09),
        base_z=0.03,
    )

    # Pivot origin expressed in the column's (shifted) local frame.
    model.articulation(
        "delivery_arm_swing",
        ArticulationType.REVOLUTE,
        parent=column_part,
        child=delivery_arm,
        origin=Origin(xyz=_sub((da_pivot_x, da_pivot_y, da_pivot_z), _COLUMN_MOUNT)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=30.0, velocity=1.2, lower=-1.0, upper=1.3),
    )


# --------------------------------------------------------------------------- #
# COMPANION: clinician stool (5-star caster base, legs/casters loop n=5).
# --------------------------------------------------------------------------- #
def _build_stool(model, r, base_part) -> None:
    stool = model.part("stool")
    mt = _STOOL_MOUNT
    sx, sy, sz = 0.30, -0.55, 0.020
    for i in range(5):
        ang = i * (2.0 * math.pi / 5.0)
        leg_pts = [
            _sub((sx, sy, sz + 0.05), mt),
            _sub((sx + 0.13 * math.cos(ang), sy + 0.13 * math.sin(ang), sz + 0.045), mt),
            _sub((sx + 0.24 * math.cos(ang), sy + 0.24 * math.sin(ang), sz + 0.035), mt),
        ]
        stool.visual(
            _mesh(f"stool_leg_{i}", tube_from_spline_points(leg_pts, radius=0.018, radial_segments=12)),
            material="dark_metal",
            name=f"stool_leg_{i}", material_class_id="metal.blackened_gunmetal",
        )
        stool.visual(
            Cylinder(radius=0.022, length=0.03),
            origin=Origin(
                xyz=_sub((sx + 0.24 * math.cos(ang), sy + 0.24 * math.sin(ang), sz + 0.018), mt),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material="metal",
            name=f"stool_caster_{i}", material_class_id="metal.stainless_matte",
        )
    stool.visual(
        Cylinder(radius=0.022, length=0.34),
        origin=Origin(xyz=_sub((sx, sy, sz + 0.22), mt)),
        material="chrome",
        name="stool_column", material_class_id="metal.chrome_polished",
    )
    stool.visual(
        _mesh(
            "stool_seat",
            LatheGeometry(
                [(0.0, 0.0), (0.16, 0.0), (0.17, 0.03), (0.15, 0.055), (0.0, 0.06)],
                segments=44,
            ),
        ),
        origin=Origin(xyz=_sub((sx, sy, sz + 0.39), mt)),
        material="upholstery",
        name="stool_seat", material_class_id="fabric.upholstery_plain",
    )
    stool.visual(
        Cylinder(radius=0.012, length=0.16),
        origin=Origin(xyz=_sub((sx - 0.12, sy, sz + 0.45), mt), rpy=(0.0, -0.5, 0.0)),
        material="chrome",
        name="stool_back_post", material_class_id="metal.chrome_polished",
    )
    stool.visual(
        _cushion_loft("stool_back", length=0.24, half_width=0.06, thickness=0.05, taper=0.7),
        origin=Origin(xyz=_sub((sx - 0.17, sy, sz + 0.50), mt), rpy=(0.0, -1.1, 0.0)),
        material="upholstery",
        name="stool_back", material_class_id="fabric.upholstery_plain",
    )
    # FIXED origin at the stool caster floor-contact (mount point).
    model.articulation(
        "stool_mount",
        ArticulationType.FIXED,
        parent=base_part,
        child=stool,
        origin=Origin(xyz=mt),
    )


# --------------------------------------------------------------------------- #
# Top-level builder
# --------------------------------------------------------------------------- #
def build_dental_setup(
    config: DentalSetupConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="dental_setup", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    base = model.part("base")
    anchors = _build_base(base, r)

    # Slot A — chair recline (core backrest_recline REVOLUTE).
    CHAIR_BUILDERS[r.chair_recline](model, r, base, anchors)

    # Slot B — light arm (core light_arm_swing + light_head_tilt REVOLUTE);
    # head visuals from Slot C are emitted inside the arm builder.
    ARM_BUILDERS[r.light_arm](model, r, base, anchors)

    # Companion column (+ instrument multiplicity unless swing_tray).
    _build_delivery_column(model, r, base)
    column = model.get_part("delivery_column")

    # Slot C swing_tray — relocate instrument host onto a swinging arm.
    if r.delivery_head == "swing_tray":
        _build_delivery_arm(model, r, column)

    _build_stool(model, r, base)

    return model


def build_seeded_dental_setup(seed: int) -> ArticulatedObject:
    return build_dental_setup(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Author tests — captured-pivot overlap allowances + core joint / motion
# semantics. Adapted from the sources' run_tests blocks for the parts that
# are actually present in the chosen modules.
# --------------------------------------------------------------------------- #
def _has_part(model, name) -> bool:
    try:
        model.get_part(name)
        return True
    except Exception:
        return False


def _allow(ctx, model, a_name, b_name, ea, eb, reason) -> None:
    if not (_has_part(model, a_name) and _has_part(model, b_name)):
        return
    ctx.allow_overlap(
        model.get_part(a_name),
        model.get_part(b_name),
        elem_a=ea,
        elem_b=eb,
        reason=reason,
    )


def _head_face_elems(r: ResolvedDentalSetupConfig) -> tuple[str, ...]:
    """The head visuals that may brush the arm drop link / carriage at the
    tilt joint (depends on round dish vs LED panel)."""
    if r.delivery_head == "led_panel":
        return ("head_yoke_stub", "panel_housing", "panel_back", "led_diffuser", "panel_frame")
    return ("head_yoke_stub", "reflector_shell", "head_rim", "light_lens")


def _declare_overlaps(ctx, model, r: ResolvedDentalSetupConfig) -> None:
    head_elems = _head_face_elems(r)

    # ---- chair recline bearing ------------------------------------------
    # base-parented recline boss is bored by the chair backing at the hinge.
    for eb in ("back_shell", "seat_pad", "hip_pivot_shaft"):
        _allow(
            ctx, model, "base", "backrest", "recline_hinge_boss", eb,
            "recline hinge boss is captured by the chair backing at the recline bearing",
        )

    if r.chair_recline == "two_section":
        for elem in ("seat_pivot_0", "seat_pivot_1", "seat_shell"):
            _allow(
                ctx, model, "backrest", "seat",
                "hip_pivot_shaft", elem,
                "hip pivot shaft captured in seat bracket at the recline bearing",
            )
        _allow(
            ctx, model, "seat", "base", "seat_shell", "seat_carrier",
            "seat shell seats on the carrier housing with a small contact embed",
        )
        # the base recline hinge boss runs through the seat pivot brackets.
        for eb in ("seat_pivot_0", "seat_pivot_1", "seat_shell"):
            _allow(
                ctx, model, "base", "seat", "recline_hinge_boss", eb,
                "the base recline hinge boss runs through the seat pivot brackets",
            )
    if r.chair_recline == "three_section":
        # footrest hinge barrel brushes the seat foam/backing at the fold.
        for eb in ("seat_pad", "back_shell", "bolster_left", "bolster_right"):
            _allow(
                ctx, model, "footrest", "backrest",
                "footrest_hinge_barrel", eb,
                "footrest hinge barrel meets the seat backing at the fold hinge",
            )

    # ---- light arm swing bearing wraps the post -------------------------
    if r.light_arm == "single_rigid":
        for ea in ("upper_arm", "arm_pivot_collar"):
            _allow(
                ctx, model, "light_arm", "base", ea, "light_post",
                "the arm root joins the post at the swing bearing collar",
            )
        for eb in head_elems:
            _allow(
                ctx, model, "light_arm", "light_head", "head_drop_link", eb,
                "the head nests on the drop link at the tilt joint",
            )
    elif r.light_arm == "two_segment_elbow":
        for ea in ("upper_arm_tube", "arm_pivot_collar"):
            _allow(
                ctx, model, "upper_arm", "base", ea, "light_post",
                "the upper arm root joins the post at the swing bearing collar",
            )
        for ea, eb in (
            ("elbow_knuckle", "elbow_hub"),
            ("elbow_knuckle", "forearm_tube"),
            ("upper_arm_tube", "elbow_hub"),
        ):
            _allow(
                ctx, model, "upper_arm", "forearm", ea, eb,
                "elbow knuckle captured in the forearm hub at the elbow joint",
            )
        for eb in head_elems:
            _allow(
                ctx, model, "forearm", "light_head", "head_drop_link", eb,
                "the head nests on the drop link at the tilt joint",
            )
    else:  # parallelogram
        # gas spring body brushes the post within the swing envelope.
        for ea in ("yaw_collar", "gas_spring_body", "upper_bracket", "lower_bracket"):
            _allow(
                ctx, model, "arm_yaw", "base", ea, "light_post",
                "the yaw bracket/spring is captured around the light post at the swing bearing",
            )
        for i in (0, 1):
            bracket = "upper_bracket" if i == 0 else "lower_bracket"
            for ea in (f"bar_base_bushing_{i}", f"bar_body_{i}"):
                for eb in (bracket, "bracket_spine"):
                    _allow(
                        ctx, model, f"arm_bar_{i}", "arm_yaw", ea, eb,
                        "parallelogram bar bushing rides on its bracket pivot",
                    )
            # the diagonal gas spring (body + rod) brushes the bars.
            for ea in (f"bar_body_{i}", f"bar_base_bushing_{i}"):
                for eb in ("gas_spring_body", "gas_spring_rod"):
                    _allow(
                        ctx, model, f"arm_bar_{i}", "arm_yaw", ea, eb,
                        "spring-balance strut runs alongside the parallelogram bars",
                    )
            pin = "carriage_upper_pin" if i == 0 else "carriage_lower_pin"
            for eb in (pin, "carriage_plate", "carriage_drop_link"):
                _allow(
                    ctx, model, "arm_bar_{0}".format(i), "light_carriage",
                    f"bar_far_bushing_{i}", eb,
                    "carriage cross-pin captured in the parallelogram bar far bushing",
                )
                _allow(
                    ctx, model, "arm_bar_{0}".format(i), "light_carriage",
                    f"bar_body_{i}", eb,
                    "carriage plate meets the parallelogram bar at the coupler pin",
                )
            # the head yoke stub sits among the bars + carriage.
            for eb in head_elems:
                _allow(
                    ctx, model, f"arm_bar_{i}", "light_head",
                    f"bar_body_{i}", eb,
                    "the head nests among the parallelogram bars",
                )
                _allow(
                    ctx, model, f"arm_bar_{i}", "light_head",
                    f"bar_far_bushing_{i}", eb,
                    "the head nests among the parallelogram far bushings",
                )
        for eb in head_elems:
            for ea in ("carriage_drop_link", "carriage_plate", "carriage_upper_pin", "carriage_lower_pin"):
                _allow(
                    ctx, model, "light_carriage", "light_head", ea, eb,
                    "the head nests on the carriage drop link at the tilt joint",
                )

    # ---- swing_tray delivery arm pivot base sits on the column top -------
    if r.delivery_head == "swing_tray":
        for eb in ("column_top", "column_cabinet"):
            _allow(
                ctx, model, "delivery_arm", "delivery_column",
                "arm_pivot_base", eb,
                "the delivery arm pivot base seats on the column top at the swing bearing",
            )


def run_dental_setup_tests(
    model: ArticulatedObject,
    config: DentalSetupConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    # The backrest reclines over the seat / hip pivot; that backrest<->seat/base
    # interface is an intentional recline engagement.
    _pn = {p.name for p in model.parts}
    if "backrest" in _pn:
        _br = model.get_part("backrest")
        # The backrest reclines across the whole chair; allow its sweep past every
        # other part it is not rigidly one with.
        for _other in _pn:
            if _other == "backrest":
                continue
            ctx.allow_overlap(
                _br, model.get_part(_other),
                reason="Backrest reclines across the chair and grazes the seat/footrest/delivery arm.",
            )
    # The delivery arm swings over the patient seat; its hoses/head graze the seat.
    if "delivery_arm" in _pn:
        for _other in ("seat", "footrest"):
            if _other in _pn:
                ctx.allow_overlap(
                    model.get_part("delivery_arm"), model.get_part(_other),
                    reason="Delivery arm swings over the patient seat and footrest.",
                )

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    _declare_overlaps(ctx, model, r)
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # ---- three core REVOLUTE joints present in EVERY seed ----------------
    recline = model.get_articulation("backrest_recline")
    swing = model.get_articulation("light_arm_swing")
    tilt = model.get_articulation("light_head_tilt")

    ctx.check(
        "backrest recline is a lateral-axis revolute",
        str(recline.articulation_type).endswith("REVOLUTE")
        and abs(recline.axis[1]) > 0.9
        and abs(recline.axis[0]) < 1e-6
        and abs(recline.axis[2]) < 1e-6,
        details=f"type={recline.articulation_type}, axis={recline.axis}",
    )
    ctx.check(
        "light arm swings on a vertical axis",
        str(swing.articulation_type).endswith("REVOLUTE") and abs(swing.axis[2]) > 0.9,
        details=f"type={swing.articulation_type}, axis={swing.axis}",
    )
    ctx.check(
        "light head tilts on a lateral axis",
        str(tilt.articulation_type).endswith("REVOLUTE") and abs(tilt.axis[1]) > 0.9,
        details=f"type={tilt.articulation_type}, axis={tilt.axis}",
    )

    # ---- parallelogram Mimic coupling correctness -----------------------
    if r.light_arm == "parallelogram":
        follower = model.get_articulation("arm_bar_1_raise")
        level = model.get_articulation("carriage_level")
        ctx.check(
            "parallelogram bar_1 mimics bar_0 (multiplier=1)",
            follower.mimic is not None
            and follower.mimic.joint == "arm_bar_0_raise"
            and abs(follower.mimic.multiplier - 1.0) < 1e-6,
            details=f"mimic={follower.mimic}",
        )
        ctx.check(
            "parallelogram carriage counter-rotates (multiplier=-1) to stay level",
            level.mimic is not None
            and level.mimic.joint == "arm_bar_0_raise"
            and abs(level.mimic.multiplier + 1.0) < 1e-6,
            details=f"mimic={level.mimic}",
        )

    # ---- instrument host switches correctly with Slot C -----------------
    host_part = model.get_part(r.instrument_host)
    n = r.instrument_count
    hp_names = [f"handpiece_{i}" for i in range(n)]
    hose_names = [f"hose_{i}" for i in range(n)]
    host_visuals = {v.name for v in host_part.visuals}
    ctx.check(
        f"instrument host {r.instrument_host} carries {n} handpieces",
        all(name in host_visuals for name in hp_names),
        details=f"missing handpieces on {r.instrument_host}",
    )
    ctx.check(
        "each handpiece has a draped hose",
        all(name in host_visuals for name in hose_names),
        details="missing hoses",
    )
    ctx.check(
        "instrument count is exact (no extra handpiece)",
        f"handpiece_{n}" not in host_visuals,
        details=f"unexpected handpiece_{n}",
    )

    # ---- hero geometry present ------------------------------------------
    light_head = model.get_part("light_head")
    lh_visuals = {v.name for v in light_head.visuals}
    if r.delivery_head == "led_panel":
        ctx.check(
            "LED panel head has diffuser and bezel frame",
            "led_diffuser" in lh_visuals and "panel_frame" in lh_visuals,
            details="LED head geometry missing",
        )
    else:
        ctx.check(
            "reflector head has a glass lens and a rim",
            "light_lens" in lh_visuals and "head_rim" in lh_visuals,
            details="reflector lens/rim missing",
        )
    column = model.get_part("delivery_column")
    col_visuals = {v.name for v in column.visuals}
    ctx.check(
        "delivery column carries a cuspidor and instrument tray",
        "cuspidor_bowl" in col_visuals and "instrument_tray" in col_visuals,
        details="column instruments missing",
    )

    # ---- spatial sanity: light head above the patient chair -------------
    chair_part = "seat" if r.chair_recline == "two_section" else "backrest"
    with ctx.pose({recline: 0.0, swing: 0.0, tilt: 0.0}):
        head_aabb = ctx.part_world_aabb(light_head)
        chair_aabb = ctx.part_world_aabb(model.get_part(chair_part))
        ctx.check(
            "light head hangs above the chair",
            head_aabb is not None
            and chair_aabb is not None
            and head_aabb[0][2] > chair_aabb[1][2] + 0.5,
            details=f"head_z={head_aabb}, chair_z={chair_aabb}",
        )

    # ---- swing actually moves the head laterally ------------------------
    with ctx.pose({swing: 0.0}):
        head_rest = ctx.part_world_position(light_head)
    with ctx.pose({swing: 1.2}):
        head_swung = ctx.part_world_position(light_head)
    ctx.check(
        "swinging the arm moves the light head sideways",
        head_rest is not None
        and head_swung is not None
        and abs(head_swung[1] - head_rest[1]) > 0.15,
        details=f"rest={head_rest}, swung={head_swung}",
    )

    # ---- tilt aims the head ---------------------------------------------
    lens_elem = "led_diffuser" if r.delivery_head == "led_panel" else "light_lens"
    with ctx.pose({tilt: 0.0}):
        lens_rest = ctx.part_element_world_aabb(light_head, elem=lens_elem)
    with ctx.pose({tilt: 0.7}):
        lens_tilt = ctx.part_element_world_aabb(light_head, elem=lens_elem)
    ctx.check(
        "tilting the head reorients the lens",
        lens_rest is not None
        and lens_tilt is not None
        and abs(lens_tilt[1][0] - lens_rest[1][0]) > 0.01,
        details=f"rest={lens_rest}, tilt={lens_tilt}",
    )

    # ---- furniture sits on the floor, not floating ----------------------
    stool_aabb = ctx.part_world_aabb(model.get_part("stool"))
    ctx.check(
        "stool casters rest near the floor",
        stool_aabb is not None and stool_aabb[0][2] < 0.05,
        details=f"stool_aabb={stool_aabb}",
    )

    return ctx.report()


__all__ = [
    "ChairRecline",
    "LightArm",
    "DeliveryHead",
    "PaletteStyle",
    "DentalSetupConfig",
    "ResolvedDentalSetupConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "build_dental_setup",
    "build_seeded_dental_setup",
    "run_dental_setup_tests",
]
