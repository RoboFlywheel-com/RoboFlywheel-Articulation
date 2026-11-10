# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for ``over_ear_headphones``.

Follows ``articraft_template_authoring/specs_modular_v1/Music_Headphone.md``.

A classic adjustable-headband over-ear (circumaural) headphone: a root
``band`` (headband) bridges two mirror-symmetric side chains, each
``band -> {side}_slider`` (PRISMATIC size adjust) -> optional ``{side}_yoke``
-> ``{side}_cup`` (REVOLUTE ear tilt).  World frame:

- +Z is up; the band crown sits highest (z ~ BAND_APEX_Z).
- +Y / -Y are the left / right ears; cups hang below the crown at y = +-LEG_Y.
- Each cup axis runs along +-Y (drum axis Y); the back face points outboard
  (+-Y), the ring ear-pad points inboard (-side, against the ear).

Four slots (pattern = mixed, root ``band``):

    cup_shape      (A) — round_drum / vertical_oval / rounded_rect
    cup_back_style (B) — closed_solid_dome / open_back_vented_grille /
                         exposed_driver_behind_ring
    headband_form  (C) — single_solid_arch / twin_parallel_rods /
                         suspension_strap_under_arch
    cup_attachment (D) — two_tine_gimbal_clevis / single_pivot_hanger /
                         collapsible_folding_hinge  (kinematics slot)

Always: exactly two mirrored cups (over-ear = two cups, fixed x2).  One
conditional multiplicity axis ``vent_count`` (only when B = vented grille).

Adopted sources (spec Module Source Index):
S1 rec_over-ear-headphones-...-5669f0bd — four-slot baselines + shared
   band/slider/yoke/cup spine + captured-pin contract.
S2 rec_over_ear_headphones_var_cup_oval — superellipse-extrude oval cup.
S3 rec_over_ear_headphones_var_cup_rounded_rect — rounded-rect studio cup.
S4 rec_over_ear_headphones_var_back_vented_grille — drilled-plate open back.
S5 rec_over_ear_headphones_var_grille_vent_count — radial-rib vent_count source.
S6 rec_over_ear_headphones_var_back_exposed_driver — exposed driver cone.
S7 rec_over_ear_headphones_var_band_twin_rods — twin parallel wire rods.
S8 rec_over_ear_headphones_var_band_suspension_strap — arch + suspension strap.
S9 rec_over_ear_headphones_var_attach_single_pivot — no-yoke single pivot.
S10 rec_over_ear_headphones_var_attach_folding_hinge — folding hinge revolute.
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
    AssetSession,
    Box,
    BoxGeometry,
    ClearanceProbe,
    ClevisBracketGeometry,
    ConeGeometry,
    CylinderGeometry,
    ExtrudeGeometry,
    Inertial,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    SphereGeometry,
    TestContext,
    TestReport,
    TorusGeometry,
    activate_asset_session,
    mesh_from_geometry,
    rounded_rect_profile,
    superellipse_profile,
    sweep_profile_along_spline,
    tube_from_spline_points,
)

# adopted: S1 5669f0bd — four-slot baselines + shared band/slider/yoke/cup spine
# adopted: S2 cup_oval — superellipse-extrude vertical-oval cup + oval pad/dome
# adopted: S3 cup_rounded_rect — rounded-rect cup body + swept non-circular pad
# adopted: S4/S5 vented_grille — radial-rib open back + vent_count multiplicity
# adopted: S6 exposed_driver — protective ring + fixed bars + driver cone + cap
# adopted: S7 twin_rods — twin parallel wire-rod headband + pad clips
# adopted: S8 suspension_strap — thin arch frame + suspension strap PRISMATIC
# adopted: S9 single_pivot — no yoke, hanger arm inline, slider->cup REVOLUTE
# adopted: S10 folding_hinge — slider->yoke REVOLUTE fold + yoke->cup tilt

__modular__ = True

CupShape = Literal["round_drum", "vertical_oval", "rounded_rect"]
CupBackStyle = Literal["closed_solid_dome", "open_back_vented_grille", "exposed_driver_behind_ring"]
HeadbandForm = Literal["single_solid_arch", "twin_parallel_rods", "suspension_strap_under_arch"]
CupAttachment = Literal[
    "two_tine_gimbal_clevis", "single_pivot_hanger", "collapsible_folding_hinge"
]
PaletteStyle = Literal[
    "silver_black_pads",
    "matte_black_leather",
    "white_grey",
    "tan_leather_brass",
    "studio_grey",
    "polished_steel_black",
]

CUP_SHAPES: tuple[CupShape, ...] = ("round_drum", "vertical_oval", "rounded_rect")
CUP_BACK_STYLES: tuple[CupBackStyle, ...] = (
    "closed_solid_dome",
    "open_back_vented_grille",
    "exposed_driver_behind_ring",
)
HEADBAND_FORMS: tuple[HeadbandForm, ...] = (
    "single_solid_arch",
    "twin_parallel_rods",
    "suspension_strap_under_arch",
)
CUP_ATTACHMENTS: tuple[CupAttachment, ...] = (
    "two_tine_gimbal_clevis",
    "single_pivot_hanger",
    "collapsible_folding_hinge",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "silver_black_pads",
    "matte_black_leather",
    "white_grey",
    "tan_leather_brass",
    "studio_grey",
    "polished_steel_black",
)

# Light weighting toward the classic baselines (spec §sampler note); every value
# still has substantial probability so the 81-combo topology pool is exercised.
_SHAPE_WEIGHTS = (0.40, 0.30, 0.30)
_BACK_WEIGHTS = (0.36, 0.34, 0.30)
_FORM_WEIGHTS = (0.40, 0.30, 0.30)
_ATTACH_WEIGHTS = (0.40, 0.30, 0.30)

# vent_count product domain [4, 16] excluding the test-excluded value 12, with
# small N over-weighted (typical consumer/monitor grille density).
_VENT_CHOICES = (4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16)
_VENT_WEIGHTS = (0.11, 0.12, 0.13, 0.12, 0.13, 0.10, 0.08, 0.06, 0.05, 0.04, 0.03, 0.03)


# --------------------------------------------------------------------------- #
# Palettes (rgba; keys drive every .visual material).
# --------------------------------------------------------------------------- #

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "silver_black_pads": {
        "band": (0.24, 0.24, 0.26, 1.0),
        "pad": (0.08, 0.07, 0.07, 1.0),
        "metal": (0.19, 0.19, 0.21, 1.0),
        "shell": (0.73, 0.74, 0.75, 1.0),
        "driver": (0.12, 0.12, 0.13, 1.0),
        "accent": (0.30, 0.30, 0.32, 1.0),
    },
    "matte_black_leather": {
        "band": (0.10, 0.10, 0.11, 1.0),
        "pad": (0.07, 0.06, 0.06, 1.0),
        "metal": (0.15, 0.15, 0.16, 1.0),
        "shell": (0.11, 0.11, 0.12, 1.0),
        "driver": (0.08, 0.08, 0.09, 1.0),
        "accent": (0.20, 0.20, 0.22, 1.0),
    },
    "white_grey": {
        "band": (0.62, 0.63, 0.65, 1.0),
        "pad": (0.45, 0.45, 0.47, 1.0),
        "metal": (0.40, 0.40, 0.42, 1.0),
        "shell": (0.90, 0.90, 0.91, 1.0),
        "driver": (0.30, 0.30, 0.32, 1.0),
        "accent": (0.55, 0.55, 0.57, 1.0),
    },
    "tan_leather_brass": {
        "band": (0.66, 0.54, 0.30, 1.0),
        "pad": (0.42, 0.30, 0.18, 1.0),
        "metal": (0.40, 0.36, 0.24, 1.0),
        "shell": (0.16, 0.15, 0.14, 1.0),
        "driver": (0.20, 0.18, 0.14, 1.0),
        "accent": (0.66, 0.54, 0.30, 1.0),
    },
    "studio_grey": {
        "band": (0.55, 0.55, 0.57, 1.0),
        "pad": (0.09, 0.08, 0.08, 1.0),
        "metal": (0.40, 0.40, 0.42, 1.0),
        "shell": (0.30, 0.31, 0.33, 1.0),
        "driver": (0.18, 0.18, 0.19, 1.0),
        "accent": (0.50, 0.50, 0.52, 1.0),
    },
    "polished_steel_black": {
        "band": (0.55, 0.56, 0.58, 1.0),
        "pad": (0.08, 0.07, 0.07, 1.0),
        "metal": (0.22, 0.22, 0.24, 1.0),
        "shell": (0.12, 0.12, 0.13, 1.0),
        "driver": (0.12, 0.12, 0.13, 1.0),
        "accent": (0.45, 0.46, 0.48, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Base (pre-scale) constants — adopted from S1 / variants.
# --------------------------------------------------------------------------- #

BAND_C_Z = 0.020
BAND_R0 = 0.082
CROWN_HALF = math.radians(75.0)

HOUSING_H = 0.032
HOUSING_W_SINGLE = 0.015
HOUSING_W_TWIN = 0.028
HOUSING_D = 0.010

SLIDER_TRAVEL0 = 0.022
SLIDER_W = 0.010
SLIDER_D = 0.006
SLIDER_TOP_Z = -0.004
SLIDER_VISIBLE = 0.034
SLIDER_BOT_Z = SLIDER_TOP_Z - SLIDER_VISIBLE  # -0.038

# Clevis yoke (fixed hardware; never scaled).
YOKE_W = 0.030
YOKE_D = 0.016
YOKE_H = 0.026
YOKE_GAP = 0.013
YOKE_BASE = 0.007
YOKE_BORE_D = 0.006
YOKE_BORE_Z = 0.017

# Single-pivot hanger arm (replaces clevis yoke).
ARM_W = 0.008
ARM_D = 0.005
ARM_H = 0.022
PIVOT_R = 0.003
PIVOT_LEN = 0.014

# Folding hinge barrel at the slider-yoke interface.
HINGE_BARREL_D = 0.008
HINGE_BARREL_L = 0.014
FOLD_UPPER0 = 1.50

# Suspension strap (S8).
ARCH_W = 0.014
ARCH_T = 0.003
STRAP_W = 0.028
STRAP_T = 0.003
STRAP_SAG = 0.020
STRAP_DROOP = 0.008

# Twin rods (S7).
ROD_RADIUS = 0.0025
ROD_SPACING = 0.018

# Cup base dims (pre-scale).
CUP_R0 = 0.040
CUP_RX0 = 0.034
CUP_RZ0 = 0.046
CUP_W0 = 0.076
CUP_H0 = 0.088
CUP_FILLET0 = 0.018
CUP_DEPTH0 = 0.024

# Scale ranges.
HEADBAND_SCALE_RANGE = (0.88, 1.12)
CUP_SIZE_SCALE_RANGE = (0.85, 1.15)
CUP_DEPTH_SCALE_RANGE = (0.85, 1.20)
SLIDER_TRAVEL_SCALE_RANGE = (0.80, 1.25)
CUP_TILT_LIMIT_RANGE = (0.30, 0.55)
FOLD_LIMIT_RANGE = (1.20, 1.55)


# --------------------------------------------------------------------------- #
# Config dataclasses.
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class OverEarHeadphonesConfig:
    cup_shape: CupShape = "round_drum"
    cup_back_style: CupBackStyle = "closed_solid_dome"
    headband_form: HeadbandForm = "single_solid_arch"
    cup_attachment: CupAttachment = "two_tine_gimbal_clevis"
    vent_count: int = 8
    palette_style: PaletteStyle = "silver_black_pads"
    headband_scale: float = 1.0
    cup_size_scale: float = 1.0
    cup_depth_scale: float = 1.0
    slider_travel_scale: float = 1.0
    cup_tilt_limit: float = 0.44
    fold_limit: float = FOLD_UPPER0
    name: str = "reference_over_ear_headphones"


@dataclass(frozen=True)
class ResolvedOverEarHeadphonesConfig:
    cup_shape: CupShape
    cup_back_style: CupBackStyle
    headband_form: HeadbandForm
    cup_attachment: CupAttachment
    vent_count: int  # 0 when not a vented grille
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    # continuous scales (clamped)
    headband_scale: float
    cup_size_scale: float
    cup_depth_scale: float
    slider_travel_scale: float
    cup_tilt_limit: float
    fold_limit: float
    # derived band geometry
    band_r: float
    leg_y: float
    leg_z: float
    band_apex_z: float
    housing_w: float
    slider_travel: float
    # derived cup geometry
    cup_depth: float
    cup_hd: float
    cup_r: float
    cup_rx: float
    cup_rz: float
    cup_w: float
    cup_h: float
    cup_fillet: float
    back_r: float
    cup_center_z: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


# --------------------------------------------------------------------------- #
# Sampling.
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> OverEarHeadphonesConfig:
    """Deterministic per-seed sampling of all four slots, vent_count, palette,
    and the continuous scales. ``seed=0`` is not special.

    Sampling order per spec §sampler: resolve Slot B first → if vented, sample
    vent_count (small N weighted, never 12); then A/C/D, palette, and the
    continuous scales. Compatibility gates are resolved in ``resolve_config``.
    """
    rng = random.Random(seed)

    back: CupBackStyle = rng.choices(CUP_BACK_STYLES, weights=_BACK_WEIGHTS, k=1)[0]
    if back == "open_back_vented_grille":
        vent_count = rng.choices(_VENT_CHOICES, weights=_VENT_WEIGHTS, k=1)[0]
    else:
        vent_count = 0

    shape: CupShape = rng.choices(CUP_SHAPES, weights=_SHAPE_WEIGHTS, k=1)[0]
    form: HeadbandForm = rng.choices(HEADBAND_FORMS, weights=_FORM_WEIGHTS, k=1)[0]
    attach: CupAttachment = rng.choices(CUP_ATTACHMENTS, weights=_ATTACH_WEIGHTS, k=1)[0]
    palette: PaletteStyle = rng.choice(PALETTE_STYLES)

    headband_scale = round(rng.uniform(*HEADBAND_SCALE_RANGE), 4)
    cup_size_scale = round(rng.uniform(*CUP_SIZE_SCALE_RANGE), 4)
    cup_depth_scale = round(rng.uniform(*CUP_DEPTH_SCALE_RANGE), 4)
    slider_travel_scale = round(rng.uniform(*SLIDER_TRAVEL_SCALE_RANGE), 4)
    cup_tilt_limit = round(rng.uniform(*CUP_TILT_LIMIT_RANGE), 4)
    fold_limit = round(rng.uniform(*FOLD_LIMIT_RANGE), 4)

    return OverEarHeadphonesConfig(
        cup_shape=shape,
        cup_back_style=back,
        headband_form=form,
        cup_attachment=attach,
        vent_count=vent_count,
        palette_style=palette,
        headband_scale=headband_scale,
        cup_size_scale=cup_size_scale,
        cup_depth_scale=cup_depth_scale,
        slider_travel_scale=slider_travel_scale,
        cup_tilt_limit=cup_tilt_limit,
        fold_limit=fold_limit,
        name=f"seeded_over_ear_headphones_{seed}",
    )


def _cup_geometry(shape: CupShape, s_cup: float, s_depth: float):
    """Return (cup_r, cup_rx, cup_rz, cup_w, cup_h, cup_fillet, back_r,
    cup_center_z, cup_depth, cup_hd) for a shape at the given scales."""
    cup_depth = CUP_DEPTH0 * s_depth
    cup_hd = cup_depth / 2.0
    cup_r = CUP_R0 * s_cup
    cup_rx = CUP_RX0 * s_cup
    cup_rz = CUP_RZ0 * s_cup
    cup_w = CUP_W0 * s_cup
    cup_h = CUP_H0 * s_cup
    cup_fillet = CUP_FILLET0 * s_cup
    if shape == "vertical_oval":
        back_r = cup_rx
        cup_center_z = -cup_rz
    elif shape == "rounded_rect":
        back_r = cup_w / 2.0 - 0.002
        cup_center_z = -cup_h / 2.0
    else:  # round_drum
        back_r = cup_r
        cup_center_z = -cup_r
    return (
        cup_r,
        cup_rx,
        cup_rz,
        cup_w,
        cup_h,
        cup_fillet,
        back_r,
        cup_center_z,
        cup_depth,
        cup_hd,
    )


# Two independently-folding cups can each swing toward Y=0; the motion-QC gate
# samples both fold joints (and both ear-tilts) on a grid, so the worst case is
# BOTH cups folded inward and tilted toward each other. Real fold-flat cans nest
# / stop short of the centreline; keep >= this clearance between the two cup
# envelopes (census target: >= 8mm apart at worst-case both-folded pose).
FOLD_CLEAR_MARGIN = 0.008

# The fold REVOLUTE pivots at the slider bottom; the cup part-frame origin (the
# ear-tilt pivot) sits YOKE_BORE_Z below it, so folding raises the cup origin by
# only YOKE_BORE_Z * (1 - cos(fold)). The "fold raises the cup >= 4mm" identity
# check therefore needs fold >= ~0.78 rad regardless of cup/band size. Below this
# a fold isn't a meaningful fold, so the attachment is rebuilt as a gimbal clevis
# (real deep-cup / small-band combos that cannot fold-flat without cups clashing).
FOLD_IDENTITY_MIN = 0.80

# Every attachment gives each cup a symmetric ear-tilt REVOLUTE about +X. Sampled
# independently by the motion-QC gate, the worst pose is BOTH cups tilted toward
# the centreline (mirror signs), where a small-band / deep-cup combo can drive the
# two cup shells across Y=0 even with NO fold (seed 37 pads penetrated ~23mm at
# fold=0). Keep >= this clearance at the worst inward-tilt pose; the ear-tilt
# limit is capped by the real-mesh solver below to guarantee it.
TILT_CLEAR_MARGIN = 0.008


def resolve_config(
    config: OverEarHeadphonesConfig,
) -> ResolvedOverEarHeadphonesConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    shape = _pick(config.cup_shape, CUP_SHAPES)
    back = _pick(config.cup_back_style, CUP_BACK_STYLES)
    form = _pick(config.headband_form, HEADBAND_FORMS)
    attach = _pick(config.cup_attachment, CUP_ATTACHMENTS)

    # vent_count only meaningful for the vented grille; force 0 otherwise.
    if back == "open_back_vented_grille":
        vent = int(config.vent_count) if config.vent_count else 8
        vent = max(4, min(16, vent))
        if vent == 12:  # test-excluded multiplicity value
            vent = 11
    else:
        vent = 0

    s_band = _clamp(config.headband_scale, *HEADBAND_SCALE_RANGE)
    s_cup = _clamp(config.cup_size_scale, *CUP_SIZE_SCALE_RANGE)
    s_depth = _clamp(config.cup_depth_scale, *CUP_DEPTH_SCALE_RANGE)
    s_travel = _clamp(config.slider_travel_scale, *SLIDER_TRAVEL_SCALE_RANGE)
    tilt_limit = _clamp(config.cup_tilt_limit, *CUP_TILT_LIMIT_RANGE)
    fold_limit = _clamp(config.fold_limit, *FOLD_LIMIT_RANGE)

    # --- band geometry (headband_scale) --------------------------------------
    band_r = BAND_R0 * s_band
    leg_y = band_r * math.sin(CROWN_HALF)
    leg_z = BAND_C_Z + band_r * math.cos(CROWN_HALF)
    band_apex_z = BAND_C_Z + band_r
    housing_w = HOUSING_W_TWIN if form == "twin_parallel_rods" else HOUSING_W_SINGLE

    # --- slider travel (keep slider top captured in housing) -----------------
    slider_travel = SLIDER_TRAVEL0 * s_travel
    # Constraint: SLIDER_TOP_Z - travel >= -HOUSING_H (top still inside housing).
    max_travel = (HOUSING_H + SLIDER_TOP_Z) - 0.001  # = 0.027
    slider_travel = min(slider_travel, max_travel)

    # --- cup geometry (cup_size / cup_depth) ---------------------------------
    (
        cup_r,
        cup_rx,
        cup_rz,
        cup_w,
        cup_h,
        cup_fillet,
        back_r,
        cup_center_z,
        cup_depth,
        cup_hd,
    ) = _cup_geometry(shape, s_cup, s_depth)

    # Slot D = folding: the real cup-cup fold clearance is solved on the exact
    # mesh at build time (``_solve_fold_clearance``), which caps the fold limit or
    # rebuilds the attachment as a gimbal clevis when a deep-cup/small-band combo
    # cannot fold-flat without the two cups clashing. ``fold_limit`` here is only
    # the declared candidate upper the solver tightens from.

    return ResolvedOverEarHeadphonesConfig(
        cup_shape=shape,
        cup_back_style=back,
        headband_form=form,
        cup_attachment=attach,
        vent_count=vent,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        headband_scale=s_band,
        cup_size_scale=s_cup,
        cup_depth_scale=s_depth,
        slider_travel_scale=s_travel,
        cup_tilt_limit=tilt_limit,
        fold_limit=fold_limit,
        band_r=band_r,
        leg_y=leg_y,
        leg_z=leg_z,
        band_apex_z=band_apex_z,
        housing_w=housing_w,
        slider_travel=slider_travel,
        cup_depth=cup_depth,
        cup_hd=cup_hd,
        cup_r=cup_r,
        cup_rx=cup_rx,
        cup_rz=cup_rz,
        cup_w=cup_w,
        cup_h=cup_h,
        cup_fillet=cup_fillet,
        back_r=back_r,
        cup_center_z=cup_center_z,
        name=config.name,
    )


# --------------------------------------------------------------------------- #
# Geometry helpers — headband (Slot C).
# --------------------------------------------------------------------------- #


def _band_arc_path(r: ResolvedOverEarHeadphonesConfig, x_offset: float = 0.0, n: int = 44):
    pts = []
    for i in range(n):
        phi = CROWN_HALF - 2.0 * CROWN_HALF * (i / (n - 1))
        pts.append((x_offset, r.band_r * math.sin(phi), BAND_C_Z + r.band_r * math.cos(phi)))
    return pts


def _band_shell_mesh(r: ResolvedOverEarHeadphonesConfig):
    return sweep_profile_along_spline(
        _band_arc_path(r),
        profile=rounded_rect_profile(0.022, 0.010, radius=0.004),
        samples_per_segment=3,
        cap_profile=True,
        up_hint=(1.0, 0.0, 0.0),
    )


def _arch_mesh(r: ResolvedOverEarHeadphonesConfig):
    return sweep_profile_along_spline(
        _band_arc_path(r),
        profile=rounded_rect_profile(ARCH_W, ARCH_T, radius=0.001),
        samples_per_segment=3,
        cap_profile=True,
        up_hint=(1.0, 0.0, 0.0),
    )


def _band_rod_mesh(r: ResolvedOverEarHeadphonesConfig, x_offset: float):
    return tube_from_spline_points(
        _band_arc_path(r, x_offset=x_offset),
        radius=ROD_RADIUS,
        samples_per_segment=5,
        radial_segments=14,
        cap_ends=True,
        up_hint=(1.0, 0.0, 0.0),
    )


def _crown_pad_mesh(r: ResolvedOverEarHeadphonesConfig):
    span = math.radians(52.0)
    n = 20
    rad = r.band_r - 0.009
    pts = [
        (
            0.0,
            rad * math.sin(span - 2.0 * span * (i / n)),
            BAND_C_Z + rad * math.cos(span - 2.0 * span * (i / n)),
        )
        for i in range(n + 1)
    ]
    return tube_from_spline_points(pts, radius=0.008, samples_per_segment=5, radial_segments=16)


def _rod_clip_mesh(r: ResolvedOverEarHeadphonesConfig, x_offset: float):
    geo = MeshGeometry()
    stem_h = 0.009
    stem = CylinderGeometry(0.003, stem_h, radial_segments=12)
    stem.translate(x_offset, 0.0, BAND_C_Z + r.band_r - 0.005 - stem_h / 2.0)
    geo.merge(stem)
    clamp = TorusGeometry(0.004, 0.0015, radial_segments=8, tubular_segments=16)
    clamp.rotate_y(math.pi / 2.0)
    clamp.translate(x_offset, 0.0, BAND_C_Z + r.band_r - 0.003)
    geo.merge(clamp)
    return geo


def _housing_mesh(r: ResolvedOverEarHeadphonesConfig, side: int):
    geo = BoxGeometry((r.housing_w, HOUSING_D, HOUSING_H))
    geo.translate(0.0, side * r.leg_y, r.leg_z - HOUSING_H / 2.0)
    return geo


def _strap_clip_mesh(r: ResolvedOverEarHeadphonesConfig, side: int):
    clip = BoxGeometry((0.010, 0.008, 0.006))
    clip.translate(0.0, side * r.leg_y, r.leg_z - ARCH_T / 2.0)
    return clip


def _strap_mesh(r: ResolvedOverEarHeadphonesConfig, n: int = 44):
    """Leather suspension strap, built in the strap's own (child) frame so that
    its part-frame origin (0,0,0) lands on the +Y arch endpoint (the joint
    origin), keeping the band->strap articulation origin on real geometry."""
    pts = []
    for i in range(n):
        t = i / (n - 1)
        phi = CROWN_HALF - 2.0 * CROWN_HALF * t
        y = r.band_r * math.sin(phi)
        z_arch = BAND_C_Z + r.band_r * math.cos(phi)
        sag = STRAP_SAG * math.sin(math.pi * t)
        pts.append((0.0, y - r.leg_y, (z_arch - sag) - r.leg_z))
    return sweep_profile_along_spline(
        pts,
        profile=rounded_rect_profile(STRAP_W, STRAP_T, radius=0.001),
        samples_per_segment=3,
        cap_profile=True,
        up_hint=(1.0, 0.0, 0.0),
    )


# --------------------------------------------------------------------------- #
# Geometry helpers — slider / yoke / hanger (Slot D).
# --------------------------------------------------------------------------- #


def _slider_mesh():
    bar = BoxGeometry((SLIDER_W, SLIDER_D, SLIDER_VISIBLE))
    bar.translate(0.0, 0.0, (SLIDER_TOP_Z + SLIDER_BOT_Z) / 2.0)
    return bar


def _yoke_mesh(side: int):
    geo = ClevisBracketGeometry(
        (YOKE_W, YOKE_D, YOKE_H),
        gap_width=YOKE_GAP,
        bore_diameter=YOKE_BORE_D,
        bore_center_z=YOKE_BORE_Z,
        base_thickness=YOKE_BASE,
        corner_radius=0.003,
        center=False,
    )
    geo.rotate_x(math.pi)
    if side < 0:
        geo.scale(1.0, -1.0, 1.0)
    return geo


def _hinge_barrel_mesh():
    geo = CylinderGeometry(HINGE_BARREL_D / 2.0, HINGE_BARREL_L, radial_segments=24)
    geo.rotate_y(math.pi / 2.0)
    return geo


def _hanger_arm_mesh():
    geo = MeshGeometry()
    arm = BoxGeometry((ARM_W, ARM_D, ARM_H))
    arm.translate(0.0, 0.0, SLIDER_BOT_Z - ARM_H / 2.0)
    geo.merge(arm)
    pivot = CylinderGeometry(PIVOT_R, PIVOT_LEN, radial_segments=16)
    pivot.rotate_y(math.pi / 2.0)
    pivot.translate(0.0, 0.0, SLIDER_BOT_Z - ARM_H)
    geo.merge(pivot)
    return geo


# --------------------------------------------------------------------------- #
# Geometry helpers — cup shell (Slot A) + back styles (Slot B) + pad/cap.
# --------------------------------------------------------------------------- #


def _cup_shell_mesh(r: ResolvedOverEarHeadphonesConfig, side: int):
    """Drum-only cup body (no dome — the closed dome is a back-style visual).
    Pivot at cup-local z = 0 (cup top); body hangs below."""
    shape = r.cup_shape
    if shape == "vertical_oval":
        profile = superellipse_profile(2.0 * r.cup_rx, 2.0 * r.cup_rz, exponent=2.0, segments=36)
        drum = ExtrudeGeometry(profile, r.cup_depth, cap=True, center=True)
        drum.rotate_x(math.pi / 2.0)
        drum.translate(0.0, 0.0, -r.cup_rz)
        return drum
    if shape == "rounded_rect":
        body = ExtrudeGeometry(
            rounded_rect_profile(r.cup_w, r.cup_h, r.cup_fillet, corner_segments=6),
            r.cup_depth,
            center=True,
        )
        body.rotate_x(math.pi / 2.0)
        body.translate(0.0, 0.0, -r.cup_h / 2.0)
        return body
    drum = CylinderGeometry(r.cup_r, r.cup_depth, radial_segments=52)
    drum.rotate_x(math.pi / 2.0)
    drum.translate(0.0, 0.0, -r.cup_r)
    return drum


def _dome_mesh(r: ResolvedOverEarHeadphonesConfig, side: int):
    """Closed-back outer dome / raised panel, shaped to match the cup outline."""
    shape = r.cup_shape
    if shape == "vertical_oval":
        dome = SphereGeometry(r.cup_rz, width_segments=28, height_segments=16)
        dome.scale(r.cup_rx / r.cup_rz, 0.28, 1.0)
        dome.translate(0.0, side * (r.cup_hd + 0.006), r.cup_center_z)
        return dome
    if shape == "rounded_rect":
        dome_w = r.cup_w - 0.014
        dome_h = r.cup_h - 0.014
        dome_f = max(0.005, r.cup_fillet - 0.005)
        dome = ExtrudeGeometry(
            rounded_rect_profile(dome_w, dome_h, dome_f, corner_segments=6),
            0.005,
            center=True,
        )
        dome.rotate_x(math.pi / 2.0)
        dome.translate(0.0, side * (r.cup_hd + 0.0025), r.cup_center_z)
        return dome
    dome = SphereGeometry(r.cup_r, width_segments=40, height_segments=22)
    dome.scale(1.0, 0.28, 1.0)
    dome.translate(0.0, side * (r.cup_hd + 0.006), r.cup_center_z)
    return dome


def _grille_ring_mesh(r: ResolvedOverEarHeadphonesConfig, side: int):
    ring = TorusGeometry(r.back_r - 0.006, 0.003, radial_segments=8, tubular_segments=28)
    ring.rotate_x(math.pi / 2.0)
    ring.translate(0.0, side * r.cup_hd, r.cup_center_z)
    return ring


def _grille_hub_mesh(r: ResolvedOverEarHeadphonesConfig, side: int):
    hub = CylinderGeometry(max(0.006, r.back_r * 0.30), 0.005, radial_segments=16)
    hub.rotate_x(math.pi / 2.0)
    hub.translate(0.0, side * r.cup_hd, r.cup_center_z)
    return hub


def _vent_slot_mesh(r: ResolvedOverEarHeadphonesConfig):
    inner_r = r.back_r * 0.24
    outer_r = r.back_r - 0.004
    length = max(0.006, outer_r - inner_r)
    rib = BoxGeometry((0.004, 0.005, length))
    rib.translate(0.0, 0.0, inner_r + length / 2.0)
    return rib


def _back_ring_mesh(r: ResolvedOverEarHeadphonesConfig, side: int):
    ring = TorusGeometry(r.back_r - 0.004, 0.004, radial_segments=14, tubular_segments=52)
    ring.rotate_x(math.pi / 2.0)
    ring.translate(0.0, side * (r.cup_hd + 0.003), r.cup_center_z)
    return ring


def _grille_bars_mesh(r: ResolvedOverEarHeadphonesConfig, side: int):
    geo = MeshGeometry()
    n_bars = 3
    bar_half = r.back_r - 0.008
    for i in range(n_bars):
        angle = math.pi * i / n_bars
        bar = BoxGeometry((2.0 * bar_half, 0.002, 0.003))
        bar.rotate_y(angle)
        bar.translate(0.0, side * (r.cup_hd + 0.003), r.cup_center_z)
        geo.merge(bar)
    return geo


def _driver_cone_mesh(r: ResolvedOverEarHeadphonesConfig, side: int):
    driver_r = r.back_r - 0.010
    cone = ConeGeometry(driver_r, 0.006, radial_segments=48)
    cone.rotate_x(side * math.pi / 2.0)
    cone.translate(0.0, side * (r.cup_hd - 0.003), r.cup_center_z)
    return cone


def _dust_cap_mesh(r: ResolvedOverEarHeadphonesConfig, side: int):
    cap = SphereGeometry(0.009, width_segments=20, height_segments=12)
    cap.scale(1.0, 0.5, 1.0)
    cap.translate(0.0, side * (r.cup_hd - 0.006), r.cup_center_z)
    return cap


def _cup_inner_cap_mesh(r: ResolvedOverEarHeadphonesConfig, side: int):
    shape = r.cup_shape
    if shape == "vertical_oval":
        profile = superellipse_profile(
            2.0 * (r.cup_rx - 0.003), 2.0 * (r.cup_rz - 0.003), exponent=2.0, segments=36
        )
        cap = ExtrudeGeometry(profile, 0.004, cap=True, center=True)
        cap.rotate_x(math.pi / 2.0)
        cap.translate(0.0, -side * (r.cup_hd + 0.001), r.cup_center_z)
        return cap
    if shape == "rounded_rect":
        cap = ExtrudeGeometry(
            rounded_rect_profile(
                r.cup_w - 0.006,
                r.cup_h - 0.006,
                max(0.005, r.cup_fillet - 0.003),
                corner_segments=6,
            ),
            0.004,
            center=True,
        )
        cap.rotate_x(math.pi / 2.0)
        cap.translate(0.0, -side * (r.cup_hd + 0.001), r.cup_center_z)
        return cap
    cap = CylinderGeometry(r.cup_r - 0.003, 0.004, radial_segments=52)
    cap.rotate_x(math.pi / 2.0)
    cap.translate(0.0, -side * (r.cup_hd + 0.001), r.cup_center_z)
    return cap


def _ear_pad_mesh(r: ResolvedOverEarHeadphonesConfig, side: int):
    shape = r.cup_shape
    if shape == "vertical_oval":
        pad_rx = r.cup_rx - 0.004
        pad_rz = r.cup_rz - 0.004
        avg_r = (pad_rx + pad_rz) / 2.0
        pad = TorusGeometry(avg_r, 0.012, radial_segments=14, tubular_segments=36)
        pad.rotate_x(math.pi / 2.0)
        pad.scale(pad_rx / avg_r, 1.0, pad_rz / avg_r)
        pad.translate(0.0, -side * (r.cup_hd + 0.002), r.cup_center_z)
        return pad
    if shape == "rounded_rect":
        pad_w = r.cup_w - 0.014
        pad_h = r.cup_h - 0.014
        pad_f = max(0.004, r.cup_fillet - 0.005)
        profile_2d = rounded_rect_profile(pad_w, pad_h, pad_f, corner_segments=6)
        y_pos = -side * (r.cup_hd + 0.002)
        pts_3d = [(x, y_pos, y2d + r.cup_center_z) for (x, y2d) in profile_2d]
        return tube_from_spline_points(
            pts_3d,
            radius=0.011,
            closed_spline=True,
            samples_per_segment=3,
            radial_segments=12,
            up_hint=(0.0, 1.0, 0.0),
        )
    pad_major = CUP_R0 * 0.80 * r.cup_size_scale
    pad = TorusGeometry(pad_major, 0.012, radial_segments=20, tubular_segments=56)
    pad.rotate_x(math.pi / 2.0)
    pad.translate(0.0, -side * (r.cup_hd + 0.002), r.cup_center_z)
    return pad


# --------------------------------------------------------------------------- #
# Build.
# --------------------------------------------------------------------------- #


def _materials(model: ArticulatedObject, r: ResolvedOverEarHeadphonesConfig) -> dict:
    out = {}
    for key, rgba in r.palette.items():
        out[key] = model.material(f"oeh_{key}_{r.palette_style}", rgba=rgba)
    return out


def _build_band(model: ArticulatedObject, r: ResolvedOverEarHeadphonesConfig, mats: dict):
    """Root headband (Slot C). Root part is always named ``band``; the optional
    suspension strap is a separate part returned for jointing."""
    band = model.part("band")
    strap = None

    if r.headband_form == "twin_parallel_rods":
        for i, x_off in enumerate((-ROD_SPACING / 2.0, ROD_SPACING / 2.0)):
            band.visual(
                mesh_from_geometry(_band_rod_mesh(r, x_off), f"band_rod_{i}"),
                material=mats["band"],
                name=f"band_rod_{i}", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
            )
        band.visual(
            mesh_from_geometry(_crown_pad_mesh(r), "band_pad"),
            material=mats["pad"],
            name="band_pad", material_class_id=("leather.smooth_plain" if r.palette_style in {"matte_black_leather", "tan_leather_brass"} else "fabric.upholstery_plain"),
        )
        for i, x_off in enumerate((-ROD_SPACING / 2.0, ROD_SPACING / 2.0)):
            band.visual(
                mesh_from_geometry(_rod_clip_mesh(r, x_off), f"pad_clip_{i}"),
                material=mats["metal"],
                name=f"pad_clip_{i}", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
            )
    elif r.headband_form == "suspension_strap_under_arch":
        band.visual(
            mesh_from_geometry(_arch_mesh(r), "arch_frame"),
            material=mats["band"],
            name="arch_frame", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
        )
        for i, side in enumerate((+1, -1)):
            band.visual(
                mesh_from_geometry(_strap_clip_mesh(r, side), f"strap_clip_{i}"),
                material=mats["metal"],
                name=f"strap_clip_{i}", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
            )
    else:  # single_solid_arch
        band.visual(
            mesh_from_geometry(_band_shell_mesh(r), "band_shell"),
            material=mats["band"],
            name="band_shell", material_class_id=("leather.smooth_plain" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
        )
        band.visual(
            mesh_from_geometry(_crown_pad_mesh(r), "band_pad"),
            material=mats["pad"],
            name="band_pad", material_class_id=("leather.smooth_plain" if r.palette_style in {"matte_black_leather", "tan_leather_brass"} else "fabric.upholstery_plain"),
        )

    for side, hn in ((+1, "housing_l"), (-1, "housing_r")):
        band.visual(
            mesh_from_geometry(_housing_mesh(r, side), hn),
            material=mats["band"],
            name=hn, material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
        )
    band.inertial = Inertial.from_geometry(
        Box((0.026, 2.0 * r.leg_y, r.band_apex_z)),
        mass=0.110,
        origin=Origin(xyz=(0.0, 0.0, r.band_apex_z * 0.45)),
    )

    if r.headband_form == "suspension_strap_under_arch":
        strap = model.part("suspension_strap")
        strap.visual(
            mesh_from_geometry(_strap_mesh(r), "strap_body"),
            material=mats["pad"],
            name="strap_body", material_class_id=("leather.smooth_plain" if r.palette_style in {"matte_black_leather", "tan_leather_brass"} else "fabric.upholstery_plain"),
        )
        strap.inertial = Inertial.from_geometry(
            Box((STRAP_W, 2.0 * r.leg_y, STRAP_SAG + 0.010)),
            mass=0.022,
            origin=Origin(xyz=(0.0, -r.leg_y, -0.010)),
        )
        # Re-anchored: joint origin sits on the +Y arch endpoint (real geometry)
        # and the strap's part-frame origin lands there too.
        model.articulation(
            "band_to_suspension_strap",
            ArticulationType.PRISMATIC,
            parent=band,
            child=strap,
            origin=Origin(xyz=(0.0, r.leg_y, r.leg_z)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=4.0, velocity=0.02, lower=0.0, upper=STRAP_DROOP),
            mating=MatingContract(
                parent_face_geometry="strap_clip_0",
                parent_face_side="positive_y",
                child_face_geometry="strap_body",
                child_face_side="positive_y",
                contact_tol=0.010,
            ),
        )
    return band, strap


def _build_cup(
    model: ArticulatedObject,
    r: ResolvedOverEarHeadphonesConfig,
    mats: dict,
    cp_nm: str,
    side: int,
):
    cup = model.part(cp_nm)
    cup.visual(
        mesh_from_geometry(_cup_shell_mesh(r, side), f"{cp_nm}_shell"),
        material=mats["shell"],
        name=f"{cp_nm}_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"silver_black_pads", "white_grey", "polished_steel_black"} else "plastic.opaque_generic"),
    )

    if r.cup_back_style == "closed_solid_dome":
        cup.visual(
            mesh_from_geometry(_dome_mesh(r, side), f"{cp_nm}_dome"),
            material=mats["shell"],
            name=f"{cp_nm}_dome", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"silver_black_pads", "white_grey", "polished_steel_black"} else "plastic.opaque_generic"),
        )
    elif r.cup_back_style == "open_back_vented_grille":
        cup.visual(
            mesh_from_geometry(_grille_ring_mesh(r, side), f"{cp_nm}_grille_ring"),
            material=mats["metal"],
            name=f"{cp_nm}_grille_ring", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
        )
        cup.visual(
            mesh_from_geometry(_grille_hub_mesh(r, side), f"{cp_nm}_grille_hub"),
            material=mats["metal"],
            name=f"{cp_nm}_grille_hub", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
        )
        for i in range(r.vent_count):
            rib = _vent_slot_mesh(r)
            rib.rotate_y(2.0 * math.pi * i / r.vent_count)
            rib.translate(0.0, side * r.cup_hd, r.cup_center_z)
            cup.visual(
                mesh_from_geometry(rib, f"{cp_nm}_vent_{i}"),
                material=mats["metal"],
                name=f"{cp_nm}_vent_{i}", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
            )
    else:  # exposed_driver_behind_ring
        cup.visual(
            mesh_from_geometry(_back_ring_mesh(r, side), f"{cp_nm}_ring"),
            material=mats["metal"],
            name=f"{cp_nm}_ring", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
        )
        cup.visual(
            mesh_from_geometry(_grille_bars_mesh(r, side), f"{cp_nm}_bars"),
            material=mats["metal"],
            name=f"{cp_nm}_bars", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
        )
        cup.visual(
            mesh_from_geometry(_driver_cone_mesh(r, side), f"{cp_nm}_driver"),
            material=mats["driver"],
            name=f"{cp_nm}_driver", material_class_id="paper.plain_sheet",
        )
        cup.visual(
            mesh_from_geometry(_dust_cap_mesh(r, side), f"{cp_nm}_dustcap"),
            material=mats["accent"],
            name=f"{cp_nm}_dustcap", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
        )

    cup.visual(
        mesh_from_geometry(_cup_inner_cap_mesh(r, side), f"{cp_nm}_cap"),
        material=mats["metal"],
        name=f"{cp_nm}_cap", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
    )
    cup.visual(
        mesh_from_geometry(_ear_pad_mesh(r, side), f"{cp_nm}_pad"),
        material=mats["pad"],
        name=f"{cp_nm}_pad", material_class_id=("leather.smooth_plain" if r.palette_style in {"matte_black_leather", "tan_leather_brass"} else "fabric.upholstery_plain"),
    )
    cup.inertial = Inertial.from_geometry(
        Box((2.0 * r.back_r, r.cup_depth + 0.025, 2.0 * abs(r.cup_center_z))),
        mass=0.055,
        origin=Origin(xyz=(0.0, 0.0, r.cup_center_z)),
    )
    return cup


def _add_side_chain(
    model: ArticulatedObject,
    r: ResolvedOverEarHeadphonesConfig,
    mats: dict,
    band,
    side: int,
):
    s = "left" if side > 0 else "right"
    sl_nm = f"{s}_slider"
    yk_nm = f"{s}_yoke"
    cp_nm = f"{s}_cup"
    housing = "housing_l" if side > 0 else "housing_r"

    # --- slider (PRISMATIC size adjust, shared spine) ----------------------- #
    slider = model.part(sl_nm)
    slider.visual(
        mesh_from_geometry(_slider_mesh(), f"{sl_nm}_bar"),
        material=mats["metal"],
        name=f"{sl_nm}_bar", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
    )
    if r.cup_attachment == "single_pivot_hanger":
        slider.visual(
            mesh_from_geometry(_hanger_arm_mesh(), f"{sl_nm}_arm"),
            material=mats["metal"],
            name=f"{sl_nm}_arm", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
        )
        slider.inertial = Inertial.from_geometry(
            Box((SLIDER_W, SLIDER_D, SLIDER_VISIBLE + ARM_H)),
            mass=0.015,
            origin=Origin(xyz=(0.0, 0.0, (SLIDER_TOP_Z + SLIDER_BOT_Z - ARM_H) / 2.0)),
        )
    else:
        slider.inertial = Inertial.from_geometry(
            Box((SLIDER_W, SLIDER_D, SLIDER_VISIBLE)),
            mass=0.012,
            origin=Origin(xyz=(0.0, 0.0, (SLIDER_TOP_Z + SLIDER_BOT_Z) / 2.0)),
        )
    model.articulation(
        f"band_to_{sl_nm}",
        ArticulationType.PRISMATIC,
        parent=band,
        child=slider,
        origin=Origin(xyz=(0.0, side * r.leg_y, r.leg_z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=12.0, velocity=0.04, lower=0.0, upper=r.slider_travel),
        mating=MatingContract(
            parent_face_geometry=housing,
            parent_face_side="positive_z",
            child_face_geometry=f"{sl_nm}_bar",
            child_face_side="positive_z",
            contact_tol=0.007,
        ),
    )

    tilt_limits = MotionLimits(
        effort=2.0, velocity=2.0, lower=-r.cup_tilt_limit, upper=r.cup_tilt_limit
    )

    if r.cup_attachment == "single_pivot_hanger":
        # No yoke: cup REVOLUTE hangs directly off the slider's hanger arm.
        cup = _build_cup(model, r, mats, cp_nm, side)
        model.articulation(
            f"{sl_nm}_to_{cp_nm}",
            ArticulationType.REVOLUTE,
            parent=slider,
            child=cup,
            origin=Origin(xyz=(0.0, 0.0, SLIDER_BOT_Z - ARM_H)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=tilt_limits,
            mating=MatingContract(
                parent_face_geometry=f"{sl_nm}_arm",
                parent_face_side="negative_z",
                child_face_geometry=f"{cp_nm}_shell",
                child_face_side="positive_z",
                contact_tol=0.010,
            ),
        )
        return

    # --- yoke (gimbal = FIXED, folding = REVOLUTE fold) --------------------- #
    yoke = model.part(yk_nm)
    yoke.visual(
        mesh_from_geometry(_yoke_mesh(side), f"{yk_nm}_body"),
        material=mats["metal"],
        name=f"{yk_nm}_body", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
    )
    if r.cup_attachment == "collapsible_folding_hinge":
        yoke.visual(
            mesh_from_geometry(_hinge_barrel_mesh(), f"{yk_nm}_hinge"),
            material=mats["band"],
            name=f"{yk_nm}_hinge", material_class_id=("metal.brass_aged" if r.palette_style in {"silver_black_pads", "matte_black_leather", "white_grey", "tan_leather_brass", "studio_grey"} else "metal.chrome_polished"),
        )
    yoke.inertial = Inertial.from_geometry(Box((YOKE_W, YOKE_D, YOKE_H)), mass=0.007)

    if r.cup_attachment == "collapsible_folding_hinge":
        model.articulation(
            f"{sl_nm}_to_{yk_nm}",
            ArticulationType.REVOLUTE,
            parent=slider,
            child=yoke,
            origin=Origin(xyz=(0.0, 0.0, SLIDER_BOT_Z)),
            axis=(-side, 0.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=r.fold_limit),
            mating=MatingContract(
                parent_face_geometry=f"{sl_nm}_bar",
                parent_face_side="negative_z",
                child_face_geometry=f"{yk_nm}_hinge",
                child_face_side="positive_z",
                contact_tol=0.007,
            ),
        )
    else:  # two_tine_gimbal_clevis
        model.articulation(
            f"{sl_nm}_to_{yk_nm}",
            ArticulationType.FIXED,
            parent=slider,
            child=yoke,
            origin=Origin(xyz=(0.0, 0.0, SLIDER_BOT_Z)),
        )

    cup = _build_cup(model, r, mats, cp_nm, side)
    model.articulation(
        f"{yk_nm}_to_{cp_nm}",
        ArticulationType.REVOLUTE,
        parent=yoke,
        child=cup,
        origin=Origin(xyz=(0.0, 0.0, -YOKE_BORE_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=tilt_limits,
        mating=MatingContract(
            parent_face_geometry=f"{yk_nm}_body",
            parent_face_side="negative_z",
            child_face_geometry=f"{cp_nm}_shell",
            child_face_side="positive_z",
            contact_tol=0.012,
        ),
    )


def _solve_tilt_clearance(model: ArticulatedObject, r: ResolvedOverEarHeadphonesConfig) -> float:
    """Cap both ear-tilt limits so the two cups never clash at inward tilt.

    Every attachment gives each cup a symmetric ear-tilt REVOLUTE about +X. The
    motion-QC gate samples the two tilt joints independently, so the worst pose is
    BOTH cups tilted toward the centreline (left ``-tl`` / right ``+tl`` — mirror
    signs), where a small-band / deep-cup combo can drive the two cup shells across
    Y=0 with NO fold applied (seed 37 pads penetrated ~23mm at fold=0; the fold
    solver only guards its own ``fold_max`` pose, never fold=0).

    Probe the EXACT mesh at that worst inward-tilt pose and bisect the largest
    symmetric tilt upper that keeps the two cup assemblies >= ``TILT_CLEAR_MARGIN``
    apart, then write it to both tilt joints. Returned so the fold solver samples
    the capped (real) tilt, not the declared one. Runs for every attachment (a
    no-op when the declared tilt already clears).
    """
    if r.cup_attachment == "single_pivot_hanger":
        lt, rt = "left_slider_to_left_cup", "right_slider_to_right_cup"
    else:
        lt, rt = "left_yoke_to_left_cup", "right_yoke_to_right_cup"
    declared = r.cup_tilt_limit
    probe = ClearanceProbe(model, joint_name=lt, keepout=["right_cup"])

    def clears(tilt: float) -> bool:
        # Both mirror-inward sign pairings (robust to per-side axis convention).
        return (
            probe.min_clearance({lt: -tilt, rt: tilt}) >= TILT_CLEAR_MARGIN
            and probe.min_clearance({lt: tilt, rt: -tilt}) >= TILT_CLEAR_MARGIN
        )

    if clears(declared):
        tilt_max = declared
    else:
        lo, hi = 0.0, declared
        for _ in range(18):
            mid = 0.5 * (lo + hi)
            if clears(mid):
                lo = mid
            else:
                hi = mid
        tilt_max = lo

    if tilt_max < declared:
        for jn in (lt, rt):
            joint = model.get_articulation(jn)
            ml = joint.motion_limits
            joint.motion_limits = MotionLimits(
                effort=ml.effort, velocity=ml.velocity, lower=-tilt_max, upper=tilt_max
            )
    return tilt_max


def _solve_fold_clearance(
    model: ArticulatedObject, r: ResolvedOverEarHeadphonesConfig, tilt_limit: float
) -> float | None:
    """Cap both fold-hinge limits so the two cups never clash (census 穿模).

    The ``collapsible_folding_hinge`` gives each cup its OWN inward fold REVOLUTE.
    Sampled independently by the motion-QC gate, the worst pose is BOTH cups
    folded inward AND ear-tilted toward each other — analytic centre-gap guards
    under-count the real cup shell/pad envelope (seed 5 clashed by ~15mm).

    Probe the EXACT mesh: with both fold joints driven together (the worst,
    most-inward case, since each cup's inward reach is monotone in its own fold
    angle) and every ear-tilt sign combination, bisect the largest common fold
    upper that keeps the two cup assemblies >= ``FOLD_CLEAR_MARGIN`` apart. If
    that upper is still a meaningful fold (``>= FOLD_IDENTITY_MIN``), write it to
    both fold joints and return it. Otherwise return ``None`` — the caller
    rebuilds the attachment as a gimbal clevis, because this deep-cup/small-band
    combo cannot fold-flat without the cups penetrating each other.
    """
    lf, rf = "left_slider_to_left_yoke", "right_slider_to_right_yoke"
    lt, rt = "left_yoke_to_left_cup", "right_yoke_to_right_cup"
    tl = tilt_limit  # the ear-tilt already capped by _solve_tilt_clearance
    declared = r.fold_limit
    probe = ClearanceProbe(model, joint_name=lf, keepout=["right_cup", "right_yoke"])
    tilt_combos = [(a, b) for a in (tl, -tl, 0.0) for b in (tl, -tl, 0.0)]

    def clears(fold: float) -> bool:
        return all(
            probe.min_clearance({lf: fold, rf: fold, lt: a, rt: b}) >= FOLD_CLEAR_MARGIN
            for a, b in tilt_combos
        )

    if clears(declared):
        fold_max = declared
    elif not clears(0.0):
        fold_max = 0.0
    else:
        lo, hi = 0.0, declared
        for _ in range(18):
            mid = 0.5 * (lo + hi)
            if clears(mid):
                lo = mid
            else:
                hi = mid
        fold_max = lo

    if fold_max < FOLD_IDENTITY_MIN:
        return None

    for jn in (lf, rf):
        joint = model.get_articulation(jn)
        ml = joint.motion_limits
        joint.motion_limits = MotionLimits(
            effort=ml.effort, velocity=ml.velocity, lower=ml.lower, upper=fold_max
        )
    return fold_max


def build_over_ear_headphones(
    config: OverEarHeadphonesConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or OverEarHeadphonesConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-over-ear-headphones-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["adopted_source_ids"] = (
        "S1",
        "S2",
        "S3",
        "S4",
        "S5",
        "S6",
        "S7",
        "S8",
        "S9",
        "S10",
    )
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]

    mats = _materials(model, r)
    session = AssetSession(assets.root, mesh_subdir=assets.mesh_subdir)
    with activate_asset_session(session):
        band, _strap = _build_band(model, r, mats)
        _add_side_chain(model, r, mats, band, +1)
        _add_side_chain(model, r, mats, band, -1)

    # Ear-tilt clearance (all attachments): cap the symmetric tilt limit on the
    # real mesh so both cups tilted toward the centreline never cross Y=0 (census
    # 穿模 seed 37, ~23mm pad penetration at fold=0). The capped tilt is the real
    # tilt range and is fed to the fold solver so it samples the true worst pose.
    solved_tilt = _solve_tilt_clearance(model, r)
    if solved_tilt < r.cup_tilt_limit:
        model.meta["solved_tilt_limit"] = solved_tilt

    # Folding hinge: solve the real-mesh fold clearance so the two cups nest /
    # stop short instead of clashing at the centreline (census 穿模 seed 5). When
    # a deep-cup / small-band combo cannot fold-flat without the cups clashing the
    # solver returns None and the attachment is rebuilt as a gimbal clevis. The
    # EFFECTIVE attachment is recorded in meta so run_tests reads one source of
    # truth (the built model), not the requested config.
    if r.cup_attachment == "collapsible_folding_hinge":
        solved = _solve_fold_clearance(model, r, solved_tilt)
        if solved is None:
            from dataclasses import replace

            gimbal_config = replace(config, cup_attachment="two_tine_gimbal_clevis")
            return build_over_ear_headphones(gimbal_config, assets=assets)
        model.meta["solved_fold_limit"] = solved

    model.meta["effective_cup_attachment"] = r.cup_attachment
    return model


def build_seeded_over_ear_headphones(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_over_ear_headphones(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Slot choices.
# --------------------------------------------------------------------------- #


def slot_choices_for_config(
    r: ResolvedOverEarHeadphonesConfig,
) -> tuple[tuple[str, str], ...]:
    choices = [
        ("cup_shape", r.cup_shape),
        ("cup_back_style", r.cup_back_style),
        ("headband_form", r.headband_form),
        ("cup_attachment", r.cup_attachment),
    ]
    if r.cup_back_style == "open_back_vented_grille":
        choices.append(("vent_count", str(r.vent_count)))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests.
# --------------------------------------------------------------------------- #


def _declare_overlap_allowances(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedOverEarHeadphonesConfig
) -> None:
    band = model.get_part("band")
    left_slider = model.get_part("left_slider")
    right_slider = model.get_part("right_slider")
    left_cup = model.get_part("left_cup")
    right_cup = model.get_part("right_cup")

    # The build may rebuild a requested folding hinge as a gimbal clevis when it
    # cannot fold-flat without the cups clashing; honour the EFFECTIVE attachment.
    attach = model.meta.get("effective_cup_attachment", r.cup_attachment)

    for slider in (left_slider, right_slider):
        ctx.allow_overlap(slider, band, reason="slider bar slides inside the band housing tube")

    if attach == "single_pivot_hanger":
        ctx.allow_overlap(
            left_cup, left_slider, reason="cup top pivots on the slider hanger arm post"
        )
        ctx.allow_overlap(
            right_cup, right_slider, reason="cup top pivots on the slider hanger arm post"
        )
    else:
        left_yoke = model.get_part("left_yoke")
        right_yoke = model.get_part("right_yoke")
        ctx.allow_overlap(left_yoke, left_slider, reason="yoke seated at the slider bottom")
        ctx.allow_overlap(right_yoke, right_slider, reason="yoke seated at the slider bottom")
        ctx.allow_overlap(left_cup, left_yoke, reason="cup top inserts into the yoke clevis gap")
        ctx.allow_overlap(right_cup, right_yoke, reason="cup top inserts into the yoke clevis gap")

    if r.headband_form == "suspension_strap_under_arch":
        strap = model.get_part("suspension_strap")
        ctx.allow_overlap(strap, band, reason="suspension strap ends are captured on the arch")


def run_over_ear_headphones_tests(
    object_model: ArticulatedObject, config: OverEarHeadphonesConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlap_allowances(ctx, object_model, r)

    band = object_model.get_part("band")
    left_slider = object_model.get_part("left_slider")
    left_cup = object_model.get_part("left_cup")
    right_cup = object_model.get_part("right_cup")
    part_names = {p.name for p in object_model.parts}

    # Single source of truth (Contract 3c): the build may rebuild a requested
    # ``collapsible_folding_hinge`` as a ``two_tine_gimbal_clevis`` when a deep-cup
    # / small-band combo cannot fold-flat without the two cups clashing. Every
    # topology / kinematics assertion below must read the EFFECTIVE attachment
    # that was actually built (recorded in meta), not the requested config —
    # otherwise the folding branch samples FIXED gimbal joints (motion_limits is
    # None) and crashes.
    attach = object_model.meta.get("effective_cup_attachment", r.cup_attachment)

    tilt_parent = "left_slider" if attach == "single_pivot_hanger" else "left_yoke"
    l_slide = object_model.get_articulation("band_to_left_slider")
    l_tilt = object_model.get_articulation(f"{tilt_parent}_to_left_cup")
    # Single source: the build-time clearance solver may cap the ear-tilt upper
    # below the declared r.cup_tilt_limit so the two inward-tilted cups clear;
    # pose at the joint's ACTUAL limit, never the requested one.
    tilt_up = l_tilt.motion_limits.upper

    # --- over-ear identity: exactly two mirrored circumaural cups ----------- #
    lp = ctx.part_world_position(left_cup)
    rp = ctx.part_world_position(right_cup)
    ctx.check("left cup on +Y side", lp is not None and lp[1] > 0.04, details=f"{lp}")
    ctx.check("right cup on -Y side", rp is not None and rp[1] < -0.04, details=f"{rp}")
    ctx.check(
        "cups mirror-symmetric about y=0",
        lp is not None and rp is not None and abs(lp[1] + rp[1]) < 0.006,
        details=f"lp={lp}, rp={rp}",
    )
    band_top = ctx.part_world_aabb(band)[1][2]
    ctx.check(
        "cups hang below the band crown",
        lp[2] < band_top - 0.04 and rp[2] < band_top - 0.04,
        details=f"band_top={band_top:.4f}, lc_z={lp[2]:.4f}, rc_z={rp[2]:.4f}",
    )

    # ear pad is on the inner (ear-side) face, inboard of the cup back -------- #
    pad_bb = ctx.part_element_world_aabb(left_cup, elem="left_cup_pad")
    shell_bb = ctx.part_element_world_aabb(left_cup, elem="left_cup_shell")
    pad_cy = 0.5 * (pad_bb[0][1] + pad_bb[1][1])
    shell_cy = 0.5 * (shell_bb[0][1] + shell_bb[1][1])
    ctx.check(
        "left ear-pad faces inboard (toward the ear)",
        pad_cy < shell_cy + 0.002,
        details=f"pad_cy={pad_cy:.4f}, shell_cy={shell_cy:.4f}",
    )

    # --- shared spine: slider captured in housing --------------------------- #
    sl = ctx.part_world_aabb(left_slider)
    ctx.check(
        "slider top inside housing (no exposed band gap)",
        sl[1][2] <= r.leg_z + 0.003,
        details=f"slider_top={sl[1][2]:.4f}, leg_z={r.leg_z:.4f}",
    )
    with ctx.pose({l_slide: r.slider_travel}):
        sl_ext = ctx.part_world_aabb(left_slider)
        ctx.check(
            "slider top stays in housing at max extension",
            sl_ext[1][2] >= r.leg_z - HOUSING_H - 0.003,
            details=f"sl_top_ext={sl_ext[1][2]:.4f}, housing_bot={r.leg_z - HOUSING_H:.4f}",
        )

    # --- shared spine: cup ear-tilt REVOLUTE -------------------------------- #
    ctx.check(
        "cup tilt joint is REVOLUTE about +X",
        l_tilt.articulation_type == ArticulationType.REVOLUTE and abs(l_tilt.axis[0]) > 0.99,
        details=f"type={l_tilt.articulation_type}, axis={l_tilt.axis}",
    )
    cp0 = ctx.part_world_aabb(left_cup)
    with ctx.pose({l_tilt: tilt_up}):
        cp1 = ctx.part_world_aabb(left_cup)
    # Tilt rotates the hanging cup about +X, so its AABB center swings in the
    # Y-Z plane (robust across cup shapes/sizes; the bare min-z barely moves for
    # tall thin cups).
    c0y, c0z = 0.5 * (cp0[0][1] + cp0[1][1]), 0.5 * (cp0[0][2] + cp0[1][2])
    c1y, c1z = 0.5 * (cp1[0][1] + cp1[1][1]), 0.5 * (cp1[0][2] + cp1[1][2])
    tilt_disp = math.hypot(c1y - c0y, c1z - c0z)
    ctx.check(
        "cup tilts on its pivot",
        tilt_disp > 0.004,
        details=f"disp={tilt_disp:.4f}, dy={c1y - c0y:.4f}, dz={c1z - c0z:.4f}",
    )

    # Strengthened (all attachments): both cups ear-tilted toward the centreline
    # must keep a Y-gap — the solver-capped tilt limit guards against the two cup
    # shells crossing Y=0 (census 穿模 seed 37). Measure the REAL mesh clearance
    # (not the AABB, which inflates for a tilted cup) at both mirror sign pairings.
    from sdk import min_clearance_at_pose

    l_tilt_nm = f"{tilt_parent}_to_left_cup"
    r_tilt_nm = f"{tilt_parent.replace('left', 'right')}_to_right_cup"
    tilt_min_clr = min(
        min_clearance_at_pose(
            object_model,
            joint=l_tilt_nm,
            joint_positions={l_tilt_nm: lts, r_tilt_nm: rts},
            keepout=["right_cup"],
        )
        for lts, rts in ((-tilt_up, tilt_up), (tilt_up, -tilt_up))
    )
    ctx.check(
        "inward-tilted cups keep mesh clearance (no cup-cup 穿模)",
        tilt_min_clr >= 0.006,
        details=f"min_clearance={tilt_min_clr:.4f} at worst inward ear-tilt",
    )

    # --- Slot A: cup-shape footprint --------------------------------------- #
    lc_aabb = ctx.part_world_aabb(left_cup)
    cup_dx = lc_aabb[1][0] - lc_aabb[0][0]
    cup_dz = lc_aabb[1][2] - lc_aabb[0][2]
    if r.cup_shape in ("vertical_oval", "rounded_rect"):
        ctx.check(
            f"{r.cup_shape} cup is taller than wide",
            cup_dz > cup_dx + 0.004,
            details=f"dx={cup_dx:.4f}, dz={cup_dz:.4f}",
        )

    # --- Slot B: back-style visuals ---------------------------------------- #
    for cp_nm, cup_part in (("left_cup", left_cup), ("right_cup", right_cup)):
        vis = {v.name for v in cup_part.visuals}
        if r.cup_back_style == "open_back_vented_grille":
            vents = [n for n in vis if n.startswith(f"{cp_nm}_vent_")]
            ctx.check(
                f"{cp_nm} has exactly {r.vent_count} vent ribs",
                len(vents) == r.vent_count,
                details=f"found {len(vents)}",
            )
            ctx.check(
                f"{cp_nm} grille ring+hub present",
                f"{cp_nm}_grille_ring" in vis and f"{cp_nm}_grille_hub" in vis,
                details=f"{sorted(vis)}",
            )
        elif r.cup_back_style == "exposed_driver_behind_ring":
            ctx.check(
                f"{cp_nm} exposes driver behind ring",
                f"{cp_nm}_ring" in vis and f"{cp_nm}_driver" in vis and f"{cp_nm}_dustcap" in vis,
                details=f"{sorted(vis)}",
            )
        else:  # closed_solid_dome
            ctx.check(
                f"{cp_nm} closed dome (no vents/driver)",
                f"{cp_nm}_dome" in vis
                and not any(n.startswith(f"{cp_nm}_vent_") for n in vis)
                and f"{cp_nm}_driver" not in vis,
                details=f"{sorted(vis)}",
            )
    if r.cup_back_style == "open_back_vented_grille":
        ctx.check("vent count differs from 12", r.vent_count != 12, details=f"N={r.vent_count}")

    # --- Slot C: headband form --------------------------------------------- #
    band_vis = {v.name for v in band.visuals}
    if r.headband_form == "twin_parallel_rods":
        ctx.check(
            "twin-rod band has two parallel rods",
            "band_rod_0" in band_vis and "band_rod_1" in band_vis,
            details=f"{sorted(band_vis)}",
        )
        rod0 = ctx.part_element_world_aabb(band, elem="band_rod_0")
        rod1 = ctx.part_element_world_aabb(band, elem="band_rod_1")
        sep = abs(0.5 * (rod0[0][0] + rod0[1][0]) - 0.5 * (rod1[0][0] + rod1[1][0]))
        ctx.check("twin rods separated in X", sep > 0.010, details=f"sep={sep:.4f}")
    elif r.headband_form == "suspension_strap_under_arch":
        ctx.check(
            "suspension band keeps root name 'band' + arch frame",
            "band" in part_names and "arch_frame" in band_vis,
            details=f"{sorted(band_vis)}",
        )
        strap = object_model.get_part("suspension_strap")
        droop = object_model.get_articulation("band_to_suspension_strap")
        ctx.check(
            "strap droop joint is PRISMATIC along -Z",
            droop.articulation_type == ArticulationType.PRISMATIC
            and abs(droop.axis[2] + 1.0) < 0.01,
            details=f"type={droop.articulation_type}, axis={droop.axis}",
        )
        arch_bb = ctx.part_element_world_aabb(band, elem="arch_frame")
        strap_bb = ctx.part_world_aabb(strap)
        ctx.check(
            "visible sag gap between arch crown and strap",
            arch_bb[1][2] - strap_bb[1][2] >= 0.006,
            details=f"arch_top={arch_bb[1][2]:.4f}, strap_top={strap_bb[1][2]:.4f}",
        )
        rest = ctx.part_world_position(strap)
        with ctx.pose({droop: STRAP_DROOP}):
            drooped = ctx.part_world_position(strap)
        ctx.check(
            "droop joint lowers the strap",
            rest is not None and drooped is not None and drooped[2] < rest[2] - 0.004,
            details=f"rest_z={rest[2]:.4f}, droop_z={drooped[2]:.4f}",
        )
    else:  # single_solid_arch
        ctx.check(
            "single solid arch band shell present",
            "band_shell" in band_vis,
            details=f"{sorted(band_vis)}",
        )

    # --- Slot D: cup-attachment topology ----------------------------------- #
    if attach == "single_pivot_hanger":
        ctx.check(
            "single pivot: no yoke parts",
            not any("yoke" in n for n in part_names),
            details=f"{sorted(part_names)}",
        )
        ctx.check(
            "single pivot: cup REVOLUTE parented to slider",
            l_tilt.parent == "left_slider",
            details=f"parent={l_tilt.parent}",
        )
    else:
        ctx.check(
            "gimbal/folding: yoke parts present",
            "left_yoke" in part_names and "right_yoke" in part_names,
            details=f"{sorted(part_names)}",
        )
        sl_yk = object_model.get_articulation("left_slider_to_left_yoke")
        if attach == "collapsible_folding_hinge":
            ctx.check(
                "folding: slider->yoke is a fold REVOLUTE about X",
                sl_yk.articulation_type == ArticulationType.REVOLUTE and abs(sl_yk.axis[0]) > 0.99,
                details=f"type={sl_yk.articulation_type}, axis={sl_yk.axis}",
            )
            l_fold = sl_yk
            r_fold = object_model.get_articulation("right_slider_to_right_yoke")
            # Single source: the build-time clearance solver may tighten the fold
            # upper below the declared r.fold_limit so the two cups nest instead of
            # clashing; pose at the joint's ACTUAL upper.
            fold_up = l_fold.motion_limits.upper
            l_tilt_j = l_tilt
            r_tilt_j = object_model.get_articulation("right_yoke_to_right_cup")
            lc_rest = ctx.part_world_position(left_cup)
            with ctx.pose({l_fold: fold_up, r_fold: fold_up}):
                lc_fold = ctx.part_world_position(left_cup)
            ctx.check(
                "folding: cup folds inward toward Y=0",
                lc_rest is not None
                and lc_fold is not None
                and abs(lc_fold[1]) < abs(lc_rest[1]) - 0.005,
                details=f"rest_y={lc_rest[1]:.4f}, fold_y={lc_fold[1]:.4f}",
            )
            ctx.check(
                "folding: fold raises the cup",
                lc_fold[2] > lc_rest[2] + 0.004,
                details=f"rest_z={lc_rest[2]:.4f}, fold_z={lc_fold[2]:.4f}",
            )
            # Strengthened: both cups fully folded + ear-tilted toward each other
            # must keep a Y-gap (mirror halves never cross the centreline). Pose at
            # the joints' ACTUAL (solver-capped) limits, not the requested ones.
            min_gap = float("inf")
            for lts in (tilt_up, -tilt_up):
                for rts in (tilt_up, -tilt_up):
                    with ctx.pose(
                        {
                            l_fold: fold_up,
                            r_fold: fold_up,
                            l_tilt_j: lts,
                            r_tilt_j: rts,
                        }
                    ):
                        la = ctx.part_world_aabb(left_cup)
                        ra = ctx.part_world_aabb(right_cup)
                    min_gap = min(min_gap, la[0][1] - ra[1][1])
            ctx.check(
                "folded cups keep a centreline Y-gap (no cup-cup 穿模)",
                min_gap >= 0.006,
                details=f"min_y_gap={min_gap:.4f} at both-folded worst tilt",
            )
        else:  # two_tine_gimbal_clevis
            ctx.check(
                "gimbal: slider->yoke is FIXED",
                sl_yk.articulation_type == ArticulationType.FIXED,
                details=f"type={sl_yk.articulation_type}",
            )

    # --- captured-pin contacts --------------------------------------------- #
    ctx.expect_contact(left_slider, band, name="left slider captured in band housing")
    ctx.expect_contact(object_model.get_part("right_slider"), band, name="right slider in housing")
    ctx.expect_contact(left_cup, object_model.get_part(tilt_parent), name="left cup on its mount")

    return ctx.report()


__all__ = [
    "OverEarHeadphonesConfig",
    "ResolvedOverEarHeadphonesConfig",
    "build_over_ear_headphones",
    "build_seeded_over_ear_headphones",
    "config_from_seed",
    "resolve_config",
    "run_over_ear_headphones_tests",
    "slot_choices_for_seed",
    "__modular__",
]
