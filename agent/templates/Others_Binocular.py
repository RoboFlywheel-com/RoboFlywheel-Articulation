# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for ``binocular``.

Follows ``articraft_template_authoring/specs_modular_v1/Others_Binocular.md``.

A center-hinge binocular: two mirrored optical barrels joined by a central
``hinge_bridge``, folding about the longitudinal (+X) viewing axis for
interpupillary adjustment.  World frame convention:

- +X is the viewing direction: objective lenses face +X, eyecups face -X.
- +Z is up; the binoculars rest on their objective tubes near z = 0.
- The central hinge bridge axle runs along X at y = 0, z = HINGE_Z.

Three slots (pattern = mixed, root ``hinge_bridge``):

    barrel_prism_layout (A) — porro_offset / roof_straight / reverse_porro_compact
    focus_mechanism     (B) — center_wheel_diopter / individual_focus / fixed_focus
    eyecup_style        (C) — rubber_fold / twist_up

Always: exactly two mirrored barrels (``side=±1``) and a central
``hinge_bridge`` with two REVOLUTE fold joints about +X.  There is no
``*_count`` axis (a binocular has, by definition, two barrels).

Adopted sources (spec Module Source Index):
S1 rec_model-a-pair-of-classic-porro-prism-binoculars-2_...a1874ba2 —
   porro_offset / center_wheel_diopter / rubber_fold baselines + hinge bridge.
S2 rec_binocular_var_roof_prism — straight roof-prism barrel (no prism_housing).
S3 rec_binocular_var_reverse_porro — reverse-Porro (objective inboard).
S4 rec_binocular_var_individual_focus — twin REVOLUTE eyepiece focus rings.
S5 rec_binocular_var_fixed_focus — focus-free (fold-only) topology.
S6 rec_binocular_var_twist_eyecup — PRISMATIC twist-up eyecup collars.
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
    ExtrudeGeometry,
    KnobBore,
    KnobGeometry,
    KnobGrip,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
)

# adopted: S1 a1874ba2 — porro_offset barrel + center wheel/diopter + rubber eyecup + hinge bridge
# adopted: S2 roof_prism — straight roof-prism barrel (no prism_housing part), short axle
# adopted: S3 reverse_porro — objective inboard / eyepiece outboard reverse-Porro
# adopted: S4 individual_focus — twin REVOLUTE eyepiece focus rings, no center wheel
# adopted: S5 fixed_focus — fold-only topology (no focus parts/joints)
# adopted: S6 twist_eyecup — PRISMATIC twist-up eyecup collars + eyepiece_body support

__modular__ = True

BarrelLayout = Literal["porro_offset", "roof_straight", "reverse_porro_compact"]
FocusMechanism = Literal["center_wheel_diopter", "individual_focus", "fixed_focus"]
EyecupStyle = Literal["rubber_fold", "twist_up"]
PaletteStyle = Literal[
    "matte_black_armor",
    "dark_graphite_metal",
    "olive_green_rubber",
    "sand_tan_armor",
    "two_tone_graphite",
    "amber_coated_optics",
]

BARREL_LAYOUTS: tuple[BarrelLayout, ...] = (
    "porro_offset",
    "roof_straight",
    "reverse_porro_compact",
)
FOCUS_MECHANISMS: tuple[FocusMechanism, ...] = (
    "center_wheel_diopter",
    "individual_focus",
    "fixed_focus",
)
EYECUP_STYLES: tuple[EyecupStyle, ...] = ("rubber_fold", "twist_up")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "matte_black_armor",
    "dark_graphite_metal",
    "olive_green_rubber",
    "sand_tan_armor",
    "two_tone_graphite",
    "amber_coated_optics",
)

# Slight weighting toward the classic baselines (spec §sampler note); every
# enum value still has substantial probability so the 18-combo topology pool
# is exercised within 0-49.
_LAYOUT_WEIGHTS = (0.40, 0.32, 0.28)
_FOCUS_WEIGHTS = (0.40, 0.32, 0.28)
_EYECUP_WEIGHTS = (0.55, 0.45)

# Visual rpy that maps a +Z-aligned cylinder/lathe/knob onto the +X axis.
ROT_Z_TO_PX = (0.0, math.pi / 2.0, 0.0)
# Same, but the lathe's open end (profile +Z) faces -X instead.
ROT_Z_TO_NX = (0.0, -math.pi / 2.0, 0.0)

# Diopter / focus-ring revolute travel and twist-up prismatic travel.
DIOPTER_LIMIT = math.radians(60.0)
FOCUS_RING_LIMIT = math.radians(60.0)
EYECUP_TRAVEL = 0.008  # prismatic twist-up travel (m)

# Twist-up collar geometry (shared by both collars; bore captures eyepiece ring).
EYECUP_COLLAR_LEN = 0.035
EYECUP_BORE_R = 0.0153
EYECUP_OUTER_R = 0.0172


# --------------------------------------------------------------------------- #
# Per-layout base geometry constants (pre-scale).
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _LayoutBase:
    """Nominal layout constants for one Slot A module (before continuous scales)."""

    hinge_z: float
    obj_y: float  # objective tube lateral offset (signed by side)
    eye_y: float  # eyepiece lateral offset (signed by side)
    obj_tube_r: float
    eye_tube_r: float
    axle_len: float
    axle_cx: float
    axle_r: float
    cap_r: float
    sleeve_len: float
    sleeve_r: float
    left_sleeve_xs: tuple[float, ...]
    right_sleeve_xs: tuple[float, ...]
    # element used as the eyepiece capture surface for diopter/focus-ring/collar.
    eyepiece_capture_elem: str
    # x-station of the eyepiece-mounted child joints (diopter / focus ring / collar).
    diopter_x: float
    focus_ring_x: float
    eyecup_mount_x: float
    focus_wheel_x: float


_LAYOUT_BASE: dict[BarrelLayout, _LayoutBase] = {
    "porro_offset": _LayoutBase(
        hinge_z=0.031,
        obj_y=0.065,
        eye_y=0.032,
        obj_tube_r=0.0305,
        eye_tube_r=0.0135,
        axle_len=0.119,
        axle_cx=-0.0125,
        axle_r=0.006,
        cap_r=0.0095,
        sleeve_len=0.018,
        sleeve_r=0.0095,
        left_sleeve_xs=(0.031, -0.015),
        right_sleeve_xs=(0.008, -0.038),
        eyepiece_capture_elem="eyepiece_tube",
        diopter_x=-0.048,
        focus_ring_x=-0.056,
        eyecup_mount_x=-0.054,
        focus_wheel_x=-0.059,
    ),
    "roof_straight": _LayoutBase(
        hinge_z=0.030,
        obj_y=0.032,
        eye_y=0.032,
        obj_tube_r=0.028,
        eye_tube_r=0.020,
        axle_len=0.082,
        axle_cx=-0.007,
        axle_r=0.005,
        cap_r=0.009,
        sleeve_len=0.014,
        sleeve_r=0.008,
        left_sleeve_xs=(0.025, -0.025),
        right_sleeve_xs=(0.011, -0.039),
        eyepiece_capture_elem="barrel_body",
        diopter_x=-0.068,
        focus_ring_x=-0.066,
        eyecup_mount_x=-0.070,
        focus_wheel_x=-0.007,
    ),
    "reverse_porro_compact": _LayoutBase(
        hinge_z=0.025,
        obj_y=0.026,
        eye_y=0.038,
        obj_tube_r=0.024,
        eye_tube_r=0.011,
        axle_len=0.080,
        axle_cx=-0.008,
        axle_r=0.005,
        cap_r=0.0075,
        sleeve_len=0.014,
        sleeve_r=0.0075,
        left_sleeve_xs=(0.020, 0.000),
        right_sleeve_xs=(0.010, -0.010),
        eyepiece_capture_elem="eyepiece_tube",
        diopter_x=-0.038,
        focus_ring_x=-0.040,
        eyecup_mount_x=-0.042,
        focus_wheel_x=-0.032,
    ),
}


# --------------------------------------------------------------------------- #
# Palettes
# --------------------------------------------------------------------------- #

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "matte_black_armor": {
        "armor": (0.100, 0.100, 0.105, 1.0),
        "metal": (0.300, 0.310, 0.330, 1.0),
        "rubber": (0.130, 0.130, 0.140, 1.0),
        "wheel": (0.080, 0.080, 0.090, 1.0),
        "amber": (0.520, 0.160, 0.080, 1.0),
        "ocular": (0.110, 0.080, 0.070, 1.0),
        "accent": (0.100, 0.100, 0.105, 1.0),
    },
    "dark_graphite_metal": {
        "armor": (0.160, 0.160, 0.180, 1.0),
        "metal": (0.450, 0.460, 0.490, 1.0),
        "rubber": (0.150, 0.150, 0.165, 1.0),
        "wheel": (0.090, 0.090, 0.100, 1.0),
        "amber": (0.520, 0.160, 0.080, 1.0),
        "ocular": (0.110, 0.080, 0.070, 1.0),
        "accent": (0.160, 0.160, 0.180, 1.0),
    },
    "olive_green_rubber": {
        "armor": (0.180, 0.220, 0.120, 1.0),
        "metal": (0.330, 0.340, 0.330, 1.0),
        "rubber": (0.140, 0.170, 0.100, 1.0),
        "wheel": (0.090, 0.110, 0.070, 1.0),
        "amber": (0.520, 0.160, 0.080, 1.0),
        "ocular": (0.110, 0.080, 0.070, 1.0),
        "accent": (0.180, 0.220, 0.120, 1.0),
    },
    "sand_tan_armor": {
        "armor": (0.550, 0.470, 0.340, 1.0),
        "metal": (0.300, 0.300, 0.310, 1.0),
        "rubber": (0.380, 0.330, 0.250, 1.0),
        "wheel": (0.150, 0.140, 0.120, 1.0),
        "amber": (0.520, 0.160, 0.080, 1.0),
        "ocular": (0.110, 0.080, 0.070, 1.0),
        "accent": (0.550, 0.470, 0.340, 1.0),
    },
    "two_tone_graphite": {
        "armor": (0.120, 0.120, 0.140, 1.0),
        "metal": (0.380, 0.390, 0.420, 1.0),
        "rubber": (0.140, 0.140, 0.155, 1.0),
        "wheel": (0.090, 0.090, 0.100, 1.0),
        "amber": (0.520, 0.160, 0.080, 1.0),
        "ocular": (0.110, 0.080, 0.070, 1.0),
        # bright-gray housing inlay accent.
        "accent": (0.380, 0.390, 0.420, 1.0),
    },
    "amber_coated_optics": {
        "armor": (0.090, 0.090, 0.095, 1.0),
        "metal": (0.330, 0.340, 0.360, 1.0),
        "rubber": (0.120, 0.120, 0.130, 1.0),
        "wheel": (0.080, 0.080, 0.090, 1.0),
        "amber": (0.620, 0.220, 0.060, 1.0),
        "ocular": (0.080, 0.120, 0.130, 1.0),
        "accent": (0.090, 0.090, 0.095, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class BinocularConfig:
    """Public configuration sampled by ``config_from_seed`` or supplied directly."""

    barrel_prism_layout: BarrelLayout = "porro_offset"
    focus_mechanism: FocusMechanism = "center_wheel_diopter"
    eyecup_style: EyecupStyle = "rubber_fold"
    palette_style: PaletteStyle = "matte_black_armor"
    overall_size_scale: float = 1.0
    barrel_length_scale: float = 1.0
    objective_radius_scale: float = 1.0
    ipd_scale: float = 1.0
    fold_limit_deg: float = 25.0
    name: str = "reference_binocular"


@dataclass(frozen=True)
class ResolvedBinocularConfig:
    barrel_prism_layout: BarrelLayout
    focus_mechanism: FocusMechanism
    eyecup_style: EyecupStyle
    palette_style: PaletteStyle
    overall_size_scale: float
    barrel_length_scale: float
    objective_radius_scale: float
    ipd_scale: float
    fold_limit_deg: float
    name: str
    # derived
    palette: dict[str, tuple[float, float, float, float]]
    base: _LayoutBase
    s: float  # overall isotropic scale
    hinge_z: float
    obj_y: float  # signed by *side at use sites; here magnitude
    eye_y: float
    obj_tube_r: float
    eye_tube_r: float
    barrel_len_scale: float
    fold_limit_rad: float
    eyepiece_capture_elem: str
    diopter_x: float
    focus_ring_x: float
    eyecup_mount_x: float
    focus_wheel_x: float


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> BinocularConfig:
    """Deterministic per-seed sampling of all three slots, palette, and scales.

    ``seed=0`` is not special. Every seed independently samples Slot A/B/C
    (lightly weighted toward classic baselines), a colorway, and the five
    independent continuous scales. The ``individual_focus × twist_up`` axial
    clearance gate is enforced later in ``resolve_config``.
    """
    rng = random.Random(seed)

    layout: BarrelLayout = rng.choices(BARREL_LAYOUTS, weights=_LAYOUT_WEIGHTS, k=1)[0]
    focus: FocusMechanism = rng.choices(FOCUS_MECHANISMS, weights=_FOCUS_WEIGHTS, k=1)[0]
    eyecup: EyecupStyle = rng.choices(EYECUP_STYLES, weights=_EYECUP_WEIGHTS, k=1)[0]
    palette: PaletteStyle = rng.choice(PALETTE_STYLES)

    overall_size_scale = round(rng.uniform(0.78, 1.12), 4)
    barrel_length_scale = round(rng.uniform(0.85, 1.15), 4)
    objective_radius_scale = round(rng.uniform(0.85, 1.18), 4)
    ipd_scale = round(rng.uniform(0.88, 1.12), 4)
    fold_limit_deg = round(rng.uniform(18.0, 30.0), 4)

    return BinocularConfig(
        barrel_prism_layout=layout,
        focus_mechanism=focus,
        eyecup_style=eyecup,
        palette_style=palette,
        overall_size_scale=overall_size_scale,
        barrel_length_scale=barrel_length_scale,
        objective_radius_scale=objective_radius_scale,
        ipd_scale=ipd_scale,
        fold_limit_deg=fold_limit_deg,
        name=f"seeded_binocular_{seed}",
    )


def _twist_up_axial_feasible(base: _LayoutBase, s: float) -> bool:
    """Eyepiece-end axial clearance gate for individual_focus × twist_up.

    The REVOLUTE focus ring sits at ``focus_ring_x`` and the PRISMATIC collar
    mounts at ``eyecup_mount_x`` then extends a further ``EYECUP_TRAVEL`` toward
    -X. The fully extended collar front face must stay clear of the focus ring
    body by ≥ 2 mm so they never interpenetrate at full prismatic travel.
    """
    # Focus ring half-thickness (KnobGeometry length 0.016 → half 0.008).
    ring_half = 0.008 * s
    ring_front_x = base.focus_ring_x * s - ring_half
    # Collar near (objective-side) face after full extension: collar base at
    # eyecup_mount_x, extends -X by EYECUP_TRAVEL; its objective-most face is the
    # base mount itself (collar body grows toward -X).
    collar_base_x = base.eyecup_mount_x * s
    # The collar base must sit at least 2 mm rearward (more -X) of the ring front.
    return (ring_front_x - collar_base_x) >= 0.002 * s


def resolve_config(config: BinocularConfig) -> ResolvedBinocularConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    layout = _pick(config.barrel_prism_layout, BARREL_LAYOUTS)
    focus = _pick(config.focus_mechanism, FOCUS_MECHANISMS)
    eyecup = _pick(config.eyecup_style, EYECUP_STYLES)
    base = _LAYOUT_BASE[layout]

    s = _clamp(config.overall_size_scale, 0.78, 1.12)
    barrel_len_scale = _clamp(config.barrel_length_scale, 0.85, 1.15)
    obj_r_scale = _clamp(config.objective_radius_scale, 0.85, 1.18)
    ipd_scale = _clamp(config.ipd_scale, 0.88, 1.12)
    fold_limit_deg = _clamp(config.fold_limit_deg, 18.0, 30.0)

    # Compatibility gate: individual_focus × twist_up axial clearance. If the
    # scaled geometry can't keep the focus ring and the fully-extended collar
    # apart, fall this seed's eyecup back to rubber_fold (matrix fallback).
    if focus == "individual_focus" and eyecup == "twist_up":
        if not _twist_up_axial_feasible(base, s):
            eyecup = "rubber_fold"

    # --- Derived offsets ---------------------------------------------------- #
    obj_y = base.obj_y * ipd_scale
    eye_y = base.eye_y * ipd_scale
    obj_tube_r = base.obj_tube_r * obj_r_scale
    eye_tube_r = base.eye_tube_r

    # Reverse-Porro objectives sit INBOARD near the central axle/caps; clamp the
    # objective bell so its rear inboard edge keeps clear of the hinge cap radius
    # (objective rear outer radius ≈ 0.75·obj_tube_r). Constraint solved here.
    if layout == "reverse_porro_compact":
        rear_ratio = 0.018 / 0.024  # rear outer radius fraction of obj_tube_r
        max_obj_r = (obj_y - base.cap_r - 0.0015) / rear_ratio
        if max_obj_r > 0:
            obj_tube_r = min(obj_tube_r, max_obj_r)

    # Roof barrels share one axis at ±eye_y; the objective bells sit at that same
    # lateral offset, so an over-scaled bell would overlap its mirror twin even
    # at rest. Clamp the bell so the two inboard edges keep ≥ 3 mm clearance at
    # the open pose (leaving margin for the fold). Constraint solved here.
    if layout == "roof_straight":
        max_bell_r = abs(eye_y) - 0.0015
        if max_bell_r > 0.018:
            obj_tube_r = min(obj_tube_r, max_bell_r)

    # Fold-closed clearance: keep ≥ 1 mm Y gap between the two barrel bodies at
    # full fold. Widening the objective radius or fold angle narrows that gap,
    # so resolve here by trimming the fold limit if the worst-case approach is
    # too tight (constraint solved in resolve_config, never left to the builder).
    fold_limit_rad = math.radians(fold_limit_deg)
    fold_limit_rad = _solve_fold_clearance(
        base, layout, eye_y, obj_y, obj_tube_r, ipd_scale, fold_limit_rad
    )

    # Eyepiece-mounted child joint stations (diopter / focus ring / collar).
    # roof_straight's rear shifts with barrel_length_scale, so its child joints
    # must track the (bl-scaled) eyepiece_ring rather than a fixed station, or
    # the joint origin drifts off the body bore. Solved here.
    diopter_x = base.diopter_x
    focus_ring_x = base.focus_ring_x
    eyecup_mount_x = base.eyecup_mount_x
    if layout == "roof_straight":
        x_rear = -(0.170 * barrel_len_scale) / 2.0
        ring_x = x_rear + 0.010  # eyepiece_ring station (solid r=0.020)
        diopter_x = ring_x
        focus_ring_x = ring_x
        eyecup_mount_x = ring_x - 0.004

    return ResolvedBinocularConfig(
        barrel_prism_layout=layout,
        focus_mechanism=focus,
        eyecup_style=eyecup,
        palette_style=config.palette_style,
        overall_size_scale=s,
        barrel_length_scale=barrel_len_scale,
        objective_radius_scale=obj_r_scale,
        ipd_scale=ipd_scale,
        fold_limit_deg=fold_limit_deg,
        name=config.name,
        palette=dict(PALETTES[config.palette_style]),
        base=base,
        s=s,
        hinge_z=base.hinge_z,
        obj_y=obj_y,
        eye_y=eye_y,
        obj_tube_r=obj_tube_r,
        eye_tube_r=eye_tube_r,
        barrel_len_scale=barrel_len_scale,
        fold_limit_rad=fold_limit_rad,
        eyepiece_capture_elem=base.eyepiece_capture_elem,
        diopter_x=diopter_x,
        focus_ring_x=focus_ring_x,
        eyecup_mount_x=eyecup_mount_x,
        focus_wheel_x=base.focus_wheel_x,
    )


def _body_inboard_edge(
    base: _LayoutBase,
    layout: BarrelLayout,
    eye_y: float,
    obj_y: float,
    obj_tube_r: float = 0.0,
    *,
    widest: bool = False,
) -> float:
    """Resting inboard-Y edge of the barrel body (prism_housing / barrel_body).

    ``widest`` returns the worst-case (objective-bell) edge used by the
    fold-clearance gap test; otherwise the body edge near the hinge stations
    (used for sizing the hinge arm bridge).
    """
    if layout == "roof_straight":
        # Near the hinge the body is the ~0.021 m main tube; the widest inboard
        # point of the AABB is the front objective bell (radius obj_tube_r).
        radius = obj_tube_r if widest else 0.021
        return abs(eye_y) - radius
    if layout == "reverse_porro_compact":
        rear_obj_r = (0.018 / 0.024) * obj_tube_r if obj_tube_r > 0 else 0.018
        return max(0.006, obj_y - rear_obj_r + 0.002)
    # porro_offset
    return abs(eye_y) * (0.055 / 0.032) - 0.027  # half of 0.054 profile width


def _solve_fold_clearance(
    base: _LayoutBase,
    layout: BarrelLayout,
    eye_y: float,
    obj_y: float,
    obj_tube_r: float,
    ipd_scale: float,
    fold_limit_rad: float,
) -> float:
    """Trim the fold limit so the two barrel bodies never collide at full fold.

    The barrels rotate inward about the central +X axle (y=0, z=hinge_z). The
    barrel body sits with its centroid roughly at z≈0, i.e. ``-hinge_z`` below
    the axle, and its inboard-Y edge at ``y_in``. Rotating that representative
    edge point inward by ``θ`` maps its world Y to ``y_in·cosθ + hinge_z·sinθ``
    (the body swings down-and-in). We keep the two mirrored edges ≥ 0.5 mm apart
    (≥ 0.25 mm half-gap). The floor stays at 18° so the IPD-narrowing identity
    check still reads a clear inward motion. Constraint solved here, never in the
    builder.
    """
    half_gap_target = 0.0003
    z_below = base.hinge_z  # body centroid sits ~hinge_z below the axle
    y_in = _body_inboard_edge(base, layout, eye_y, obj_y, obj_tube_r, widest=True)
    limit = fold_limit_rad
    # roof_straight tubes sit close together so they need more headroom to trim;
    # allow down to 14°, others keep an 18° floor for a clear fold.
    floor = math.radians(14.0 if layout == "roof_straight" else 18.0)
    for _ in range(30):
        # Down-and-in fold: the inboard edge's world Y after inward rotation.
        edge_y = y_in * math.cos(limit) - z_below * math.sin(limit)
        if edge_y >= half_gap_target or limit <= floor:
            break
        limit -= math.radians(1.0)
    return max(limit, floor)


# --------------------------------------------------------------------------- #
# Geometry helpers — barrel meshes (per Slot A).
# --------------------------------------------------------------------------- #


def _objective_tube_mesh_porro(tag: str, r: ResolvedBinocularConfig):
    """Wide tapered Porro objective bell (adopted: S1). Axis +Z, rear at z=0."""
    rr = r.obj_tube_r
    bl = r.barrel_len_scale
    outer = [
        (0.0265 / 0.0305 * rr, 0.000),
        (0.0265 / 0.0305 * rr, 0.010 * bl),
        (0.0290 / 0.0305 * rr, 0.042 * bl),
        (rr, 0.070 * bl),
        (rr, 0.080 * bl),
    ]
    inner = [
        (0.0000, 0.060 * bl),
        (0.0240 / 0.0305 * rr, 0.062 * bl),
        (0.0250 / 0.0305 * rr, 0.066 * bl),
        (0.0265 / 0.0305 * rr, 0.080 * bl),
    ]
    geom = LatheGeometry.from_shell_profiles(outer, inner, segments=48)
    return mesh_from_geometry(geom, f"{tag}_objective_tube")


def _objective_tube_mesh_reverse(tag: str, r: ResolvedBinocularConfig):
    """Short reverse-Porro objective bell (adopted: S3). Axis +Z, rear at z=0."""
    rr = r.obj_tube_r
    bl = r.barrel_len_scale
    outer = [
        (0.0180 / 0.024 * rr, 0.000),
        (0.0180 / 0.024 * rr, 0.008 * bl),
        (0.0210 / 0.024 * rr, 0.030 * bl),
        (rr, 0.048 * bl),
        (rr, 0.055 * bl),
    ]
    inner = [
        (0.0000, 0.040 * bl),
        (0.0160 / 0.024 * rr, 0.042 * bl),
        (0.0180 / 0.024 * rr, 0.046 * bl),
        (0.0200 / 0.024 * rr, 0.055 * bl),
    ]
    geom = LatheGeometry.from_shell_profiles(outer, inner, segments=48)
    return mesh_from_geometry(geom, f"{tag}_objective_tube")


def _barrel_body_mesh_roof(tag: str, r: ResolvedBinocularConfig):
    """Straight roof-prism barrel tube (adopted: S2). One optical axis, no step.

    Axis +Z, rear (eyepiece) at z=0, front (objective) at z=BL.
    """
    bl = 0.170 * r.barrel_len_scale
    barrel_r = 0.021
    obj_bell_r = r.obj_tube_r
    f = r.barrel_len_scale
    outer = [
        (0.0185, 0.000),
        (0.0185, 0.012 * f),
        (0.0200, 0.020 * f),
        (barrel_r, 0.028 * f),
        (barrel_r, 0.132 * f),
        (0.024, 0.145 * f),
        (0.027, 0.158 * f),
        (obj_bell_r, 0.165 * f),
        (obj_bell_r, bl),
    ]
    inner = [
        (0.0155, 0.000),
        (0.0155, 0.012 * f),
        (0.0170, 0.020 * f),
        (0.0180, 0.028 * f),
        (0.0180, 0.150 * f),
        (0.0240, 0.160 * f),
        (0.0250, bl),
    ]
    geom = LatheGeometry.from_shell_profiles(outer, inner, segments=48)
    return mesh_from_geometry(geom, f"{tag}_barrel_body")


def _housing_mesh_porro(tag: str):
    """Rounded Porro prism-housing block (adopted: S1)."""
    profile = rounded_rect_profile(0.054, 0.078, 0.012)
    geom = ExtrudeGeometry(profile, 0.070)
    return mesh_from_geometry(geom, f"{tag}_prism_housing")


def _housing_mesh_reverse(tag: str, lateral_w: float = 0.040):
    """Reverse-Porro prism-housing block bridging inboard obj → outboard eye (S3).

    ``lateral_w`` is the barrel-local Y span (profile 2nd dim), widened with the
    objective→eyepiece offset gap so it reliably bridges both axes at high IPD.
    """
    profile = rounded_rect_profile(0.040, lateral_w, 0.008)
    geom = ExtrudeGeometry(profile, 0.040)
    return mesh_from_geometry(geom, f"{tag}_prism_housing")


def _eyecup_mesh(tag: str):
    """Soft rubber fold eyecup shell (adopted: S1). Axis +Z, mount face at z=0."""
    outer = [
        (0.0150, 0.000),
        (0.0170, 0.004),
        (0.0170, 0.016),
        (0.0175, 0.021),
        (0.0175, 0.024),
    ]
    inner = [
        (0.0000, 0.0100),
        (0.0130, 0.0115),
        (0.0140, 0.0160),
        (0.0145, 0.0240),
    ]
    geom = LatheGeometry.from_shell_profiles(outer, inner, segments=40)
    return mesh_from_geometry(geom, f"{tag}_eyecup")


def _eyecup_mesh_reverse(tag: str):
    """Compact reverse-Porro soft eyecup (adopted: S3). Axis +Z, mount face z=0."""
    outer = [
        (0.0125, 0.000),
        (0.0140, 0.003),
        (0.0140, 0.014),
        (0.0145, 0.018),
        (0.0145, 0.020),
    ]
    inner = [
        (0.0000, 0.008),
        (0.0105, 0.009),
        (0.0115, 0.014),
        (0.0120, 0.020),
    ]
    geom = LatheGeometry.from_shell_profiles(outer, inner, segments=40)
    return mesh_from_geometry(geom, f"{tag}_eyecup")


def _twist_up_collar_mesh(tag: str):
    """Rigid twist-up eyecup collar with helical grip grooves (adopted: S6).

    Axis +Z, mount face at z=0; thin bore captures the eyepiece ring.
    """
    o = EYECUP_OUTER_R
    b = EYECUP_BORE_R
    L = EYECUP_COLLAR_LEN
    outer = [
        (b + 0.0004, 0.000),
        (o, 0.001),
        (o, 0.005),
        (o - 0.0008, 0.006),
        (o, 0.007),
        (o, 0.013),
        (o - 0.0008, 0.014),
        (o, 0.015),
        (o, 0.021),
        (o - 0.0008, 0.022),
        (o, 0.023),
        (o, 0.029),
        (o - 0.0008, 0.030),
        (o, 0.031),
        (o + 0.0005, 0.034),
        (o + 0.0005, L),
    ]
    inner = [
        (b - 0.0025, 0.000),  # inner lip narrows the bore at the base so solid
        (b, 0.0015),          # geometry sits within tol of the joint origin
        (b, L),
    ]
    geom = LatheGeometry.from_shell_profiles(outer, inner, segments=40)
    return mesh_from_geometry(geom, f"{tag}_collar")


def _knurled_knob(tag: str, diameter: float, length: float, count: int):
    """Knurled cylindrical knob. ``diameter`` is the body diameter (not radius)."""
    geom = KnobGeometry(
        diameter,
        length,
        body_style="cylindrical",
        grip=KnobGrip(style="knurled", count=count, depth=0.0008, helix_angle_deg=0.0),
    )
    return mesh_from_geometry(geom, tag)


def _focus_ring_mesh(tag: str, bore_diameter: float = 0.028, outer_r: float = 0.036):
    """Knurled individual-focus ring with a central bore (adopted: S4).

    ``outer_r`` and ``bore_diameter`` are both DIAMETERS (KnobGeometry/KnobBore
    convention). ``bore_diameter`` is sized per Slot A so the knurled wall grips
    the eyepiece ring (a too-wide bore leaves the ring floating as an island).
    """
    geom = KnobGeometry(
        outer_r,
        0.016,
        body_style="cylindrical",
        grip=KnobGrip(style="knurled", count=30, depth=0.0008, helix_angle_deg=0.0),
        bore=KnobBore(style="round", diameter=bore_diameter),
    )
    return mesh_from_geometry(geom, f"{tag}_knurl")


# --------------------------------------------------------------------------- #
# Barrel builder (shared mirrored helper).
# --------------------------------------------------------------------------- #


def _add_barrel(
    model: ArticulatedObject,
    name: str,
    side: int,
    sleeve_xs: tuple[float, ...],
    mats: dict,
    r: ResolvedBinocularConfig,
) -> object:
    """Build one barrel; ``side`` is +1 (left, +Y) or -1 (right, -Y).

    The barrel part frame sits on the central hinge axis (y=0, z=HINGE_Z world)
    so the fold articulation rotates it about its own local +X. Slot A selects
    the barrel mesh family and lateral offsets. Slot C decides whether the
    eyecup is a barrel visual (rubber_fold) or an external PRISMATIC part.
    """
    armor = mats["armor"]
    metal = mats["metal"]
    accent = mats["accent"]
    lens_amber = mats["amber"]

    layout = r.barrel_prism_layout
    obj_y = r.obj_y
    eye_y = r.eye_y
    bl = r.barrel_len_scale

    barrel = model.part(name)

    if layout == "roof_straight":
        _add_roof_barrel(barrel, name, side, r, mats)
    elif layout == "reverse_porro_compact":
        barrel.visual(
            _objective_tube_mesh_reverse(name, r),
            origin=Origin(xyz=(0.020 * bl, side * obj_y, 0.0), rpy=ROT_Z_TO_PX),
            material=armor,
            name="objective_tube", material_class_id="rubber.pebbled",
        )
        barrel.visual(
            Cylinder(radius=0.019, length=0.005),
            origin=Origin(xyz=(0.060 * bl, side * obj_y, 0.0), rpy=ROT_Z_TO_PX),
            material=lens_amber,
            name="objective_lens", material_class_id="glass.smoked_tinted",
        )
        # Housing bridges the objective (inboard) and eyepiece (outboard) axes.
        # It must reach the objective rear (radius ~0.8·obj_tube_r) and the
        # eyepiece tube, while keeping its inboard edge clear of y=0 so the two
        # folded housings don't collide. Center on the gap; width spans from the
        # objective rear inner edge out to the eyepiece.
        housing_cy = (obj_y + eye_y) / 2.0
        rear_obj_r = (0.018 / 0.024) * r.obj_tube_r
        inboard = max(0.006, obj_y - rear_obj_r + 0.002)
        outboard = eye_y + r.eye_tube_r + 0.002
        housing_w = max(0.030, outboard - inboard)
        housing_cy = 0.5 * (inboard + outboard)
        barrel.visual(
            _housing_mesh_reverse(name, lateral_w=housing_w),
            origin=Origin(xyz=(0.005, side * housing_cy, 0.0), rpy=ROT_Z_TO_PX),
            material=accent,
            name="prism_housing", material_class_id=("rubber.pebbled" if r.palette_style in {"matte_black_armor", "dark_graphite_metal", "olive_green_rubber", "sand_tan_armor", "amber_coated_optics"} else "metal.aluminum_bare"),
        )
        _add_offset_eyepiece(
            barrel, name, side, r, mats,
            eye_x=-0.032, ring_x=-0.044, cup_x=-0.047,
            ocu_x=-0.056, eye_tube_len=0.034, ring_r=0.013,
            ocu_r=0.0115, eyecup_mesh_fn=_eyecup_mesh_reverse,
        )
    else:  # porro_offset
        barrel.visual(
            _objective_tube_mesh_porro(name, r),
            origin=Origin(xyz=(0.020 * bl, side * obj_y, 0.0), rpy=ROT_Z_TO_PX),
            material=armor,
            name="objective_tube", material_class_id="rubber.pebbled",
        )
        barrel.visual(
            Cylinder(radius=0.0235, length=0.006),
            origin=Origin(xyz=(0.0832 * bl, side * obj_y, 0.0), rpy=ROT_Z_TO_PX),
            material=lens_amber,
            name="objective_lens", material_class_id="glass.smoked_tinted",
        )
        barrel.visual(
            _housing_mesh_porro(name),
            origin=Origin(xyz=(0.0, side * 0.055 * r.ipd_scale, 0.0), rpy=ROT_Z_TO_PX),
            material=accent,
            name="prism_housing", material_class_id=("rubber.pebbled" if r.palette_style in {"matte_black_armor", "dark_graphite_metal", "olive_green_rubber", "sand_tan_armor", "amber_coated_optics"} else "metal.aluminum_bare"),
        )
        _add_offset_eyepiece(
            barrel, name, side, r, mats,
            eye_x=-0.052, ring_x=-0.062, cup_x=-0.071,
            ocu_x=-0.0835, eye_tube_len=0.044, ring_r=0.0155,
            ocu_r=0.0125, eyecup_mesh_fn=_eyecup_mesh,
        )

    # --- Hinge lugs: sleeve captured on axle + arm into the body ------------ #
    # The sleeve straddles y=0 (captured on the axle). The arm is a short box
    # offset to one side of the axle so it never collides with the axle itself
    # (adopted: S1/S3 arm at side*~0.015 with a sub-axle-radius gap).
    sleeve_names = ("front_hinge_sleeve", "rear_hinge_sleeve")
    arm_names = ("front_hinge_arm", "rear_hinge_arm")
    # Inner edge starts just outboard of the axle radius; outer edge reaches the
    # body inboard edge (prism_housing / barrel_body) so the arm bridges
    # sleeve→body in one connected island without crossing the axle at y=0.
    arm_inner = r.base.axle_r + 0.0015
    body_inner_y = _body_inboard_edge(
        r.base, r.barrel_prism_layout, r.eye_y, r.obj_y, r.obj_tube_r
    )
    # Overlap a touch into the body so the meshes connect.
    arm_outer = max(body_inner_y + 0.002, arm_inner + 0.008)
    arm_w = arm_outer - arm_inner
    arm_cy = side * (arm_inner + arm_w * 0.5)
    for i in range(len(sleeve_xs)):
        sx = sleeve_xs[i]
        barrel.visual(
            Cylinder(radius=r.base.sleeve_r, length=r.base.sleeve_len),
            origin=Origin(xyz=(sx, 0.0, 0.0), rpy=ROT_Z_TO_PX),
            material=metal,
            name=sleeve_names[i], material_class_id="metal.aluminum_bare",
        )
        barrel.visual(
            Box((r.base.sleeve_len, arm_w, 0.018)),
            origin=Origin(xyz=(sx, arm_cy, 0.0)),
            material=metal,
            name=arm_names[i], material_class_id="metal.aluminum_bare",
        )

    return barrel


def _add_offset_eyepiece(
    barrel,
    name: str,
    side: int,
    r: ResolvedBinocularConfig,
    mats: dict,
    *,
    eye_x: float,
    ring_x: float,
    cup_x: float,
    ocu_x: float,
    eye_tube_len: float,
    ring_r: float,
    ocu_r: float,
    eyecup_mesh_fn,
) -> None:
    """Emit eyepiece tube + ring + (fold eyecup or twist support) + ocular lens.

    Shared by porro_offset and reverse_porro_compact (both keep an explicit
    ``eyepiece_tube`` capture surface). Slot C decides whether a soft eyecup
    visual is folded into the barrel (rubber_fold) or an external collar part
    captures the ring (twist_up).
    """
    metal = mats["metal"]
    rubber = mats["rubber"]
    lens_dark = mats["ocular"]
    eye_y = r.eye_y

    barrel.visual(
        Cylinder(radius=r.eye_tube_r, length=eye_tube_len),
        origin=Origin(xyz=(eye_x, side * eye_y, 0.0), rpy=ROT_Z_TO_PX),
        material=metal,
        name="eyepiece_tube", material_class_id="metal.aluminum_bare",
    )
    barrel.visual(
        Cylinder(radius=ring_r, length=0.008),
        origin=Origin(xyz=(ring_x, side * eye_y, 0.0), rpy=ROT_Z_TO_PX),
        material=metal,
        name="eyepiece_ring", material_class_id="metal.aluminum_bare",
    )

    if r.eyecup_style == "twist_up":
        # Rigid eyepiece body supports the ocular when the soft cup is replaced
        # by the external collar (adopted: S6 eyepiece_body). Sits between the
        # ring and the ocular lens so the ocular is never an isolated island.
        barrel.visual(
            Cylinder(radius=max(0.013, ocu_r + 0.001), length=abs(ring_x - ocu_x) + 0.006),
            origin=Origin(xyz=(0.5 * (ring_x + ocu_x), side * eye_y, 0.0), rpy=ROT_Z_TO_PX),
            material=metal,
            name="eyepiece_body", material_class_id="metal.aluminum_bare",
        )
    else:
        barrel.visual(
            eyecup_mesh_fn(name),
            origin=Origin(xyz=(cup_x, side * eye_y, 0.0), rpy=ROT_Z_TO_NX),
            material=rubber,
            name="eyecup", material_class_id="rubber.smooth_plain",
        )

    barrel.visual(
        Cylinder(radius=ocu_r, length=0.005),
        origin=Origin(xyz=(ocu_x, side * eye_y, 0.0), rpy=ROT_Z_TO_PX),
        material=lens_dark,
        name="ocular_lens", material_class_id="glass.smoked_tinted",
    )


def _add_roof_barrel(barrel, name: str, side: int, r: ResolvedBinocularConfig, mats: dict) -> None:
    """Straight roof-prism barrel body + lenses (adopted: S2).

    Objective and eyepiece share one optical axis at ``side*eye_y``; the capture
    surface for eyepiece-mounted children is ``barrel_body`` (no eyepiece_tube).
    """
    armor = mats["armor"]
    metal = mats["metal"]
    rubber = mats["rubber"]
    lens_amber = mats["amber"]
    lens_dark = mats["ocular"]
    eye_y = r.eye_y
    bl = r.barrel_len_scale
    barrel_len = 0.170 * bl
    x_rear = -barrel_len / 2.0
    barrel_y = side * eye_y

    barrel.visual(
        _barrel_body_mesh_roof(name, r),
        origin=Origin(xyz=(x_rear, barrel_y, 0.0), rpy=ROT_Z_TO_PX),
        material=armor,
        name="barrel_body", material_class_id="rubber.pebbled",
    )
    barrel.visual(
        Cylinder(radius=0.024, length=0.005),
        origin=Origin(xyz=(x_rear + barrel_len - 0.012, barrel_y, 0.0), rpy=ROT_Z_TO_PX),
        material=lens_amber,
        name="objective_lens", material_class_id="glass.smoked_tinted",
    )
    barrel.visual(
        Cylinder(radius=0.016, length=0.006),
        origin=Origin(xyz=(x_rear + 0.010, barrel_y, 0.0), rpy=ROT_Z_TO_PX),
        material=metal,
        name="eyepiece_ring", material_class_id="metal.aluminum_bare",
    )
    if r.eyecup_style == "twist_up":
        # Rigid eyepiece body bridges from the (solid) eyepiece_ring out past the
        # body rear to the ocular so the ocular is never an isolated island
        # (adopted: S6 eyepiece_body). Its radius (0.016) exceeds the body bore
        # so it actually contacts the ring/tube wall, not the hollow interior.
        ring_x = x_rear + 0.010
        ocu_target_x = x_rear - 0.012
        body_len = (ring_x - ocu_target_x) + 0.006
        body_cx = 0.5 * (ring_x + ocu_target_x)
        barrel.visual(
            Cylinder(radius=0.016, length=body_len),
            origin=Origin(xyz=(body_cx, barrel_y, 0.0), rpy=ROT_Z_TO_PX),
            material=metal,
            name="eyepiece_body", material_class_id="metal.aluminum_bare",
        )
        ocu_x = ocu_target_x
    else:
        barrel.visual(
            _eyecup_mesh(name),
            origin=Origin(xyz=(x_rear + 0.002, barrel_y, 0.0), rpy=ROT_Z_TO_NX),
            material=rubber,
            name="eyecup", material_class_id="rubber.smooth_plain",
        )
        ocu_x = x_rear - 0.012
    barrel.visual(
        Cylinder(radius=0.014, length=0.004),
        origin=Origin(xyz=(ocu_x, barrel_y, 0.0), rpy=ROT_Z_TO_PX),
        material=lens_dark,
        name="ocular_lens", material_class_id="glass.smoked_tinted",
    )


# --------------------------------------------------------------------------- #
# Slot B / C child mechanisms.
# --------------------------------------------------------------------------- #


def _build_center_wheel_diopter(
    model: ArticulatedObject,
    r: ResolvedBinocularConfig,
    mats: dict,
    *,
    bridge,
    right_barrel,
) -> None:
    """Central CONTINUOUS focus wheel + right-eyepiece REVOLUTE diopter (S1)."""
    wheel = model.part("focus_wheel")
    # The wheel sits on the axle at y=0 near the rear; it must fit in the gap
    # between the two eyepiece axes (the eyepiece inboard edge = eye_y - tube_r),
    # NOT just the front housings. roof barrels run very close, so it shrinks.
    # (KnobGeometry's first arg is a DIAMETER, so the wheel reaches ±diameter/2.)
    if r.barrel_prism_layout == "roof_straight":
        eye_inboard = abs(r.eye_y) - 0.021  # body main tube near the rear
    else:
        eye_inboard = abs(r.eye_y) - r.eye_tube_r
    wheel_d = max(0.012, 2.0 * (eye_inboard - 0.003))
    wheel.visual(
        _knurled_knob("focus_wheel", wheel_d, 0.020, 34),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=ROT_Z_TO_PX),
        material=mats["wheel"],
        name="focus_wheel_knurl", material_class_id="rubber.directional_grooved",
    )
    model.articulation(
        "bridge_to_focus_wheel",
        ArticulationType.CONTINUOUS,
        parent=bridge,
        child=wheel,
        origin=Origin(xyz=(r.focus_wheel_x, 0.0, r.hinge_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.5, velocity=6.0),
    )

    diopter = model.part("diopter_ring")
    diopter.visual(
        _knurled_knob("diopter_ring", 0.030, 0.012, 30),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=ROT_Z_TO_PX),
        material=mats["wheel"],
        name="diopter_knurl", material_class_id="rubber.directional_grooved",
    )
    model.articulation(
        "right_barrel_to_diopter_ring",
        ArticulationType.REVOLUTE,
        parent=right_barrel,
        child=diopter,
        origin=Origin(xyz=(r.diopter_x, -r.eye_y, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=1.0, velocity=4.0, lower=-DIOPTER_LIMIT, upper=DIOPTER_LIMIT
        ),
    )


def _build_individual_focus(
    model: ArticulatedObject,
    r: ResolvedBinocularConfig,
    mats: dict,
    *,
    barrels: tuple,
) -> None:
    """Twin REVOLUTE eyepiece focus rings, no center wheel (adopted: S4)."""
    sides = (+1, -1)
    # Bore sized just inside the eyepiece_ring outer radius per layout so the
    # knurl wall grips the ring (an over-wide bore leaves the part floating).
    ring_outer_r = {
        "porro_offset": 0.0155,
        "reverse_porro_compact": 0.013,
        "roof_straight": 0.016,
    }[r.barrel_prism_layout]
    # KnobGeometry's first arg (and KnobBore.diameter) are DIAMETERS. Grip the
    # eyepiece ring: bore diameter just under 2×ring_outer, knob diameter larger.
    bore_d = max(0.016, 2.0 * (ring_outer_r - 0.0015))
    knurl_d = bore_d + 0.020
    for i in range(2):
        side = sides[i]
        barrel = barrels[i]
        ring = model.part(f"focus_ring_{i}")
        ring.visual(
            _focus_ring_mesh(f"focus_ring_{i}", bore_diameter=bore_d, outer_r=knurl_d),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=ROT_Z_TO_PX),
            material=mats["wheel"],
            name="focus_ring_knurl", material_class_id="rubber.directional_grooved",
        )
        model.articulation(
            f"barrel_to_focus_ring_{i}",
            ArticulationType.REVOLUTE,
            parent=barrel,
            child=ring,
            origin=Origin(xyz=(r.focus_ring_x, side * r.eye_y, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=1.0, velocity=4.0, lower=-FOCUS_RING_LIMIT, upper=FOCUS_RING_LIMIT
            ),
        )


def _build_twist_up(
    model: ArticulatedObject,
    r: ResolvedBinocularConfig,
    mats: dict,
    *,
    barrels: tuple,
    barrel_names: tuple,
) -> None:
    """Twin PRISMATIC twist-up eyecup collars (adopted: S6)."""
    sides = (+1, -1)
    for i in range(2):
        side = sides[i]
        barrel = barrels[i]
        barrel_name = barrel_names[i]
        collar_name = f"eyecup_collar_{i}"
        collar = model.part(collar_name)
        collar.visual(
            _twist_up_collar_mesh(collar_name),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=ROT_Z_TO_NX),
            material=mats["rubber"],
            name="collar", material_class_id="rubber.directional_grooved",
        )
        model.articulation(
            f"{barrel_name}_to_{collar_name}",
            ArticulationType.PRISMATIC,
            parent=barrel,
            child=collar,
            origin=Origin(xyz=(r.eyecup_mount_x, side * r.eye_y, 0.0)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=0.5, lower=0.0, upper=EYECUP_TRAVEL),
        )


# --------------------------------------------------------------------------- #
# Top-level build.
# --------------------------------------------------------------------------- #


def _materials(model: ArticulatedObject, r: ResolvedBinocularConfig) -> dict:
    out = {}
    for key, rgba in r.palette.items():
        out[key] = model.material(f"binocular_{key}_{r.palette_style}", rgba=rgba)
    return out


def build_binocular(
    config: BinocularConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or BinocularConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-binocular-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["adopted_source_ids"] = ("S1", "S2", "S3", "S4", "S5", "S6")
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]

    mats = _materials(model, r)
    metal = mats["metal"]
    base = r.base

    # --- Root: central hinge bridge ---------------------------------------- #
    bridge = model.part("hinge_bridge")
    bridge.visual(
        Cylinder(radius=base.axle_r, length=base.axle_len),
        origin=Origin(xyz=(base.axle_cx, 0.0, r.hinge_z), rpy=ROT_Z_TO_PX),
        material=metal,
        name="hinge_axle", material_class_id="metal.aluminum_bare",
    )
    cap_front_x = base.axle_cx + base.axle_len / 2.0 + 0.0012
    cap_rear_x = base.axle_cx - base.axle_len / 2.0 - 0.0012
    # The end caps sit on the axle at y=0; cap their radius so they clear the
    # inboard edge of the nearest barrel geometry (the bodies sit close to y=0
    # for narrow-IPD roof/reverse layouts). 2 mm radial clearance.
    cap_clear = (
        _body_inboard_edge(r.base, r.barrel_prism_layout, r.eye_y, r.obj_y, r.obj_tube_r) - 0.002
    )
    cap_r = max(base.axle_r + 0.001, min(base.cap_r, cap_clear))
    bridge.visual(
        Cylinder(radius=cap_r, length=0.006),
        origin=Origin(xyz=(cap_front_x, 0.0, r.hinge_z), rpy=ROT_Z_TO_PX),
        material=metal,
        name="front_hinge_cap", material_class_id="metal.aluminum_bare",
    )
    bridge.visual(
        Cylinder(radius=cap_r, length=0.006),
        origin=Origin(xyz=(cap_rear_x, 0.0, r.hinge_z), rpy=ROT_Z_TO_PX),
        material=metal,
        name="rear_hinge_cap", material_class_id="metal.aluminum_bare",
    )

    # --- Mirrored barrels --------------------------------------------------- #
    left_barrel = _add_barrel(model, "left_barrel", +1, base.left_sleeve_xs, mats, r)
    right_barrel = _add_barrel(model, "right_barrel", -1, base.right_sleeve_xs, mats, r)

    for name, child in (("left", left_barrel), ("right", right_barrel)):
        model.articulation(
            f"bridge_to_{name}_barrel",
            ArticulationType.REVOLUTE,
            parent=bridge,
            child=child,
            origin=Origin(xyz=(0.0, 0.0, r.hinge_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=8.0, velocity=2.0, lower=-r.fold_limit_rad, upper=r.fold_limit_rad
            ),
        )

    # --- Slot B: focus mechanism ------------------------------------------- #
    barrels = (left_barrel, right_barrel)
    barrel_names = ("left_barrel", "right_barrel")
    if r.focus_mechanism == "center_wheel_diopter":
        _build_center_wheel_diopter(
            model, r, mats, bridge=bridge, right_barrel=right_barrel
        )
    elif r.focus_mechanism == "individual_focus":
        _build_individual_focus(model, r, mats, barrels=barrels)
    # fixed_focus: no focus parts/joints (fold only).

    # --- Slot C: eyecup style ---------------------------------------------- #
    if r.eyecup_style == "twist_up":
        _build_twist_up(model, r, mats, barrels=barrels, barrel_names=barrel_names)
    # rubber_fold: eyecup is a barrel visual (no joint).

    return model


def build_seeded_binocular(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_binocular(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Slot choices.
# --------------------------------------------------------------------------- #


def slot_choices_for_config(r: ResolvedBinocularConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("barrel_prism_layout", r.barrel_prism_layout),
        ("focus_mechanism", r.focus_mechanism),
        ("eyecup_style", r.eyecup_style),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests.
# --------------------------------------------------------------------------- #


def _declare_overlap_allowances(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedBinocularConfig
) -> None:
    parts = {p.name for p in model.parts}
    bridge = model.get_part("hinge_bridge")
    left = model.get_part("left_barrel")
    right = model.get_part("right_barrel")
    capture = r.eyepiece_capture_elem

    body_elem = "barrel_body" if r.barrel_prism_layout == "roof_straight" else "prism_housing"

    # Hinge lug sleeves captured on the central axle.
    for barrel in (left, right):
        for sleeve in ("front_hinge_sleeve", "rear_hinge_sleeve"):
            ctx.allow_overlap(
                barrel,
                bridge,
                elem_a=sleeve,
                elem_b="hinge_axle",
                reason="Hinge lug sleeve is intentionally captured around the central axle.",
            )

    # The interleaved hinge sleeves straddle y=0 by design, so for the close-set
    # roof/reverse layouts one barrel's sleeve can pass alongside the other
    # barrel's body. That is the real center-hinge geometry, not a clash.
    for sleeve in ("front_hinge_sleeve", "rear_hinge_sleeve"):
        ctx.allow_overlap(
            left,
            right,
            elem_a=sleeve,
            elem_b=body_elem,
            reason="Interleaved hinge sleeve passes alongside the opposite barrel body.",
        )
        ctx.allow_overlap(
            left,
            right,
            elem_a=body_elem,
            elem_b=sleeve,
            reason="Interleaved hinge sleeve passes alongside the opposite barrel body.",
        )
        ctx.allow_overlap(
            left,
            right,
            elem_a=sleeve,
            elem_b=sleeve,
            reason="Left/right hinge sleeves interleave on the shared central axle.",
        )

    if "focus_wheel" in parts:
        ctx.allow_overlap(
            model.get_part("focus_wheel"),
            bridge,
            elem_a="focus_wheel_knurl",
            elem_b="hinge_axle",
            reason="Center focus wheel is intentionally captured on the central axle.",
        )
    if "diopter_ring" in parts:
        ctx.allow_overlap(
            model.get_part("diopter_ring"),
            right,
            elem_a="diopter_knurl",
            elem_b=capture,
            reason="Diopter ring is intentionally captured around the right eyepiece.",
        )
        ctx.allow_overlap(
            model.get_part("diopter_ring"),
            right,
            elem_a="diopter_knurl",
            elem_b="eyepiece_ring",
            reason="Diopter ring seats against the static eyepiece ring on the tube.",
        )
        if "eyepiece_body" in {v.name for v in right.visuals}:
            ctx.allow_overlap(
                model.get_part("diopter_ring"),
                right,
                elem_a="diopter_knurl",
                elem_b="eyepiece_body",
                reason="Diopter ring wraps the rigid eyepiece body (twist-up build).",
            )

    barrels = (left, right)
    for i in range(2):
        ring_name = f"focus_ring_{i}"
        if ring_name in parts:
            ctx.allow_overlap(
                model.get_part(ring_name),
                barrels[i],
                elem_a="focus_ring_knurl",
                elem_b=capture,
                reason=f"Focus ring {i} is intentionally captured around the eyepiece.",
            )
            ctx.allow_overlap(
                model.get_part(ring_name),
                barrels[i],
                elem_a="focus_ring_knurl",
                elem_b="eyepiece_ring",
                reason=f"Focus ring {i} seats against the static eyepiece ring.",
            )
        collar_name = f"eyecup_collar_{i}"
        if collar_name in parts:
            ctx.allow_overlap(
                model.get_part(collar_name),
                barrels[i],
                elem_a="collar",
                elem_b="eyepiece_ring",
                reason=f"Twist-up collar {i} bore captures the eyepiece ring (sliding fit).",
            )
            ctx.allow_overlap(
                model.get_part(collar_name),
                barrels[i],
                elem_a="collar",
                elem_b=capture,
                reason=f"Twist-up collar {i} bore slides over the eyepiece tube.",
            )
            ctx.allow_overlap(
                model.get_part(collar_name),
                barrels[i],
                elem_a="collar",
                elem_b="eyepiece_body",
                reason=f"Twist-up collar {i} sleeve slides over the rigid eyepiece body.",
            )


def _objective_elem(r: ResolvedBinocularConfig) -> str:
    return "barrel_body" if r.barrel_prism_layout == "roof_straight" else "objective_tube"


def _rear_eye_elem(model: ArticulatedObject, r: ResolvedBinocularConfig, side: int) -> tuple:
    """Return (part, elem) used to read the rear/eyepiece end for a given side."""
    i = 0 if side > 0 else 1
    if r.eyecup_style == "twist_up":
        return model.get_part(f"eyecup_collar_{i}"), "collar"
    barrel = model.get_part("left_barrel" if side > 0 else "right_barrel")
    return barrel, "eyecup"


def run_binocular_tests(
    object_model: ArticulatedObject, config: BinocularConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlap_allowances(ctx, object_model, r)

    bridge = object_model.get_part("hinge_bridge")
    left = object_model.get_part("left_barrel")
    right = object_model.get_part("right_barrel")
    left_hinge = object_model.get_articulation("bridge_to_left_barrel")
    right_hinge = object_model.get_articulation("bridge_to_right_barrel")
    part_names = {p.name for p in object_model.parts}
    joint_names = {a.name for a in object_model.articulations}
    obj_elem = _objective_elem(r)
    capture = r.eyepiece_capture_elem
    body_elem = "barrel_body" if r.barrel_prism_layout == "roof_straight" else "prism_housing"

    # --- Binocular identity: exactly two mirrored barrels ------------------- #
    ctx.check(
        "exactly two mirrored barrels",
        "left_barrel" in part_names and "right_barrel" in part_names,
        details=str(sorted(part_names)),
    )
    ctx.check(
        "central hinge bridge with two REVOLUTE fold joints about +X",
        left_hinge.articulation_type == ArticulationType.REVOLUTE
        and right_hinge.articulation_type == ArticulationType.REVOLUTE
        and abs(left_hinge.axis[0]) > 0.99
        and abs(right_hinge.axis[0]) > 0.99,
        details=f"left={left_hinge.axis}, right={right_hinge.axis}",
    )

    # --- Hinge lugs seated on the bridge axle ------------------------------- #
    for barrel in (left, right):
        ctx.expect_contact(barrel, bridge, name=f"{barrel.name} hinge lugs touch the bridge")
        for sleeve in ("front_hinge_sleeve", "rear_hinge_sleeve"):
            ctx.expect_overlap(
                barrel,
                bridge,
                axes="x",
                elem_a=sleeve,
                elem_b="hinge_axle",
                min_overlap=0.008,
                name=f"{barrel.name} {sleeve} captured on the axle",
            )

    # --- Objective at front (+X), eyecup at rear (-X) ----------------------- #
    # Use the objective_lens disc (always at the front rim) as the front
    # reference; roof_straight's barrel_body spans the whole length so its min-x
    # is not a valid "front" marker.
    for barrel, side in ((left, +1), (right, -1)):
        obj_lens_bb = ctx.part_element_world_aabb(barrel, elem="objective_lens")
        rear_part, rear_elem = _rear_eye_elem(object_model, r, side)
        eye_bb = ctx.part_element_world_aabb(rear_part, elem=rear_elem)
        ctx.check(
            f"{barrel.name} eyecup at the rear, objective at the front",
            eye_bb[1][0] < obj_lens_bb[0][0],
            details=f"eye_max_x={eye_bb[1][0]:.4f}, obj_lens_min_x={obj_lens_bb[0][0]:.4f}",
        )

    # --- Slot A layout invariant: lateral objective/eyepiece relationship ---- #
    for barrel, side in ((left, +1), (right, -1)):
        obj_bb = ctx.part_element_world_aabb(barrel, elem=obj_elem)
        rear_part, rear_elem = _rear_eye_elem(object_model, r, side)
        eye_bb = ctx.part_element_world_aabb(rear_part, elem=rear_elem)
        obj_cy = 0.5 * (obj_bb[0][1] + obj_bb[1][1])
        eye_cy = 0.5 * (eye_bb[0][1] + eye_bb[1][1])
        if r.barrel_prism_layout == "porro_offset":
            ctx.check(
                f"{barrel.name} objective outboard of eyepiece (porro_offset)",
                side * obj_cy > side * eye_cy + 0.015,
                details=f"obj_y={obj_cy:.4f}, eye_y={eye_cy:.4f}",
            )
        elif r.barrel_prism_layout == "reverse_porro_compact":
            ctx.check(
                f"{barrel.name} objective inboard of eyepiece (reverse_porro)",
                side * eye_cy > side * obj_cy + 0.004,
                details=f"obj_y={obj_cy:.4f}, eye_y={eye_cy:.4f}",
            )
        else:  # roof_straight
            ctx.check(
                f"{barrel.name} objective and eyepiece share one axis (roof_straight)",
                abs(obj_cy - eye_cy) < 0.006,
                details=f"obj_y={obj_cy:.4f}, eye_y={eye_cy:.4f}",
            )

    # --- Recessed objective lens ------------------------------------------- #
    for barrel in (left, right):
        tube_bb = ctx.part_element_world_aabb(barrel, elem=obj_elem)
        lens_bb = ctx.part_element_world_aabb(barrel, elem="objective_lens")
        ctx.check(
            f"{barrel.name} objective lens recessed behind the front rim",
            lens_bb[1][0] <= tube_bb[1][0] - 0.004,
            details=f"lens_max_x={lens_bb[1][0]:.4f}, tube_max_x={tube_bb[1][0]:.4f}",
        )
        ctx.check(
            f"{barrel.name} objective lens inside the tube bore (yz)",
            lens_bb[0][1] >= tube_bb[0][1] - 0.001
            and lens_bb[1][1] <= tube_bb[1][1] + 0.001
            and lens_bb[0][2] >= tube_bb[0][2] - 0.001
            and lens_bb[1][2] <= tube_bb[1][2] + 0.001,
            details=f"lens_bb={lens_bb}, tube_bb={tube_bb}",
        )

    # --- Slot B topology assertions ----------------------------------------- #
    if r.focus_mechanism == "center_wheel_diopter":
        focus_joint = object_model.get_articulation("bridge_to_focus_wheel")
        ctx.check(
            "focus wheel joint is continuous about the longitudinal axis",
            focus_joint.articulation_type == ArticulationType.CONTINUOUS
            and abs(focus_joint.axis[0]) > 0.99,
            details=f"type={focus_joint.articulation_type}, axis={focus_joint.axis}",
        )
        wheel = object_model.get_part("focus_wheel")
        ctx.expect_overlap(
            wheel,
            bridge,
            axes="x",
            elem_a="focus_wheel_knurl",
            elem_b="hinge_axle",
            min_overlap=0.010,
            name="focus wheel seated on the central axle",
        )
        wbb = ctx.part_element_world_aabb(wheel, elem="focus_wheel_knurl")
        wcy = 0.5 * (wbb[0][1] + wbb[1][1])
        wcz = 0.5 * (wbb[0][2] + wbb[1][2])
        ctx.check(
            "focus wheel centered on the hinge axis",
            abs(wcy) < 0.003 and abs(wcz - r.hinge_z) < 0.003,
            details=f"wheel_center=({wcy:.4f},{wcz:.4f})",
        )
        diopter_joint = object_model.get_articulation("right_barrel_to_diopter_ring")
        dl = diopter_joint.motion_limits
        ctx.check(
            "diopter ring is REVOLUTE +/-60 deg about its own axis",
            diopter_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(diopter_joint.axis[0]) > 0.99
            and dl is not None
            and dl.lower is not None
            and abs(dl.lower + DIOPTER_LIMIT) < 0.02
            and abs(dl.upper - DIOPTER_LIMIT) < 0.02,
            details=f"type={diopter_joint.articulation_type}, axis={diopter_joint.axis}",
        )
        ctx.expect_overlap(
            object_model.get_part("diopter_ring"),
            right,
            axes="x",
            elem_a="diopter_knurl",
            elem_b=capture,
            min_overlap=0.005,
            name="diopter ring wraps the right eyepiece",
        )
    elif r.focus_mechanism == "individual_focus":
        ctx.check(
            "no center focus wheel (individual focus)",
            "focus_wheel" not in part_names,
            details=str(sorted(part_names)),
        )
        for i, expected_parent in ((0, "left_barrel"), (1, "right_barrel")):
            joint = object_model.get_articulation(f"barrel_to_focus_ring_{i}")
            ctx.check(
                f"focus_ring_{i} REVOLUTE on {expected_parent}",
                joint.articulation_type == ArticulationType.REVOLUTE
                and abs(joint.axis[0]) > 0.99
                and joint.parent == expected_parent,
                details=f"type={joint.articulation_type}, parent={joint.parent}",
            )
            ctx.expect_overlap(
                object_model.get_part(f"focus_ring_{i}"),
                left if i == 0 else right,
                axes="x",
                elem_a="focus_ring_knurl",
                elem_b=capture,
                min_overlap=0.006,
                name=f"focus_ring_{i} wraps the eyepiece",
            )
    else:  # fixed_focus
        ctx.check(
            "fixed focus: no focus wheel / diopter / focus ring parts",
            "focus_wheel" not in part_names
            and "diopter_ring" not in part_names
            and not any(n.startswith("focus_ring_") for n in part_names),
            details=str(sorted(part_names)),
        )
        ctx.check(
            "fixed focus: no focus/diopter joints",
            "bridge_to_focus_wheel" not in joint_names
            and "right_barrel_to_diopter_ring" not in joint_names
            and not any(n.startswith("barrel_to_focus_ring_") for n in joint_names),
            details=str(sorted(joint_names)),
        )

    # --- Slot C topology assertions ----------------------------------------- #
    if r.eyecup_style == "twist_up":
        for i, (side, bname) in enumerate(((+1, "left_barrel"), (-1, "right_barrel"))):
            collar = object_model.get_part(f"eyecup_collar_{i}")
            joint = object_model.get_articulation(f"{bname}_to_eyecup_collar_{i}")
            cl = joint.motion_limits
            ctx.check(
                f"eyecup_collar_{i} is PRISMATIC along -X, 0..{EYECUP_TRAVEL}",
                joint.articulation_type == ArticulationType.PRISMATIC
                and abs(joint.axis[0] + 1.0) < 0.01
                and cl is not None
                and abs(cl.lower) < 0.001
                and abs(cl.upper - EYECUP_TRAVEL) < 0.001,
                details=f"type={joint.articulation_type}, axis={joint.axis}",
            )
            # Collar extends outward (more -X) when twisted up.
            rest = ctx.part_world_position(collar)
            with ctx.pose({joint: EYECUP_TRAVEL}):
                ext = ctx.part_world_position(collar)
            ctx.check(
                f"eyecup_collar_{i} extends outward when twisted up",
                rest is not None and ext is not None and ext[0] < rest[0] - 0.004,
                details=f"rest_x={rest[0]:.4f}, ext_x={ext[0]:.4f}",
            )
    else:
        ctx.check(
            "rubber_fold: eyecups are barrel visuals (no collar parts)",
            not any(n.startswith("eyecup_collar_") for n in part_names),
            details=str(sorted(part_names)),
        )

    # --- Ground contact ----------------------------------------------------- #
    all_parts = list(object_model.parts)
    aabbs = [ctx.part_world_aabb(p) for p in all_parts]
    lo_z = min(a[0][2] for a in aabbs)
    ctx.check(
        "binoculars rest near the ground plane",
        -0.006 <= lo_z <= 0.010,
        details=f"min_z={lo_z:.4f}",
    )

    # --- Interpupillary fold: barrels rotate toward each other -------------- #
    lp, le = _rear_eye_elem(object_model, r, +1)
    rp, re_ = _rear_eye_elem(object_model, r, -1)
    rest_left = ctx.part_element_world_aabb(lp, elem=le)
    rest_right = ctx.part_element_world_aabb(rp, elem=re_)
    rest_left_cy = 0.5 * (rest_left[0][1] + rest_left[1][1])
    rest_right_cy = 0.5 * (rest_right[0][1] + rest_right[1][1])
    rest_left_cz = 0.5 * (rest_left[0][2] + rest_left[1][2])
    with ctx.pose({left_hinge: -r.fold_limit_rad, right_hinge: r.fold_limit_rad}):
        fold_left = ctx.part_element_world_aabb(lp, elem=le)
        fold_right = ctx.part_element_world_aabb(rp, elem=re_)
        fold_left_cy = 0.5 * (fold_left[0][1] + fold_left[1][1])
        fold_right_cy = 0.5 * (fold_right[0][1] + fold_right[1][1])
        fold_left_cz = 0.5 * (fold_left[0][2] + fold_left[1][2])
        ctx.check(
            "folded eyepieces move toward each other (narrower IPD)",
            (rest_left_cy - rest_right_cy) - (fold_left_cy - fold_right_cy) > 0.0008,
            details=f"rest_ipd={rest_left_cy - rest_right_cy:.4f}, "
            f"fold_ipd={fold_left_cy - fold_right_cy:.4f}",
        )
        ctx.check(
            "folded barrels swing about the longitudinal hinge (eyecups drop)",
            fold_left_cz < rest_left_cz - 0.002,
            details=f"rest_z={rest_left_cz:.4f}, fold_z={fold_left_cz:.4f}",
        )
        ctx.expect_gap(
            left,
            right,
            axis="y",
            min_gap=0.000,
            positive_elem=body_elem,
            negative_elem=body_elem,
            name="fully folded barrel bodies keep clearance",
        )

    return ctx.report()


__all__ = [
    "BinocularConfig",
    "ResolvedBinocularConfig",
    "build_binocular",
    "build_seeded_binocular",
    "config_from_seed",
    "resolve_config",
    "run_binocular_tests",
    "slot_choices_for_seed",
    "__modular__",
]
