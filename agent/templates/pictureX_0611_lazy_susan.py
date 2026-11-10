# SPDX-License-Identifier: Apache-2.0

"""Modular template: pictureX_0611 lazy susan.

A serving platter that spins freely about a single vertical (+z) axis on visible
turntable-bearing hardware, carried by a stationary support base. Derived from
the 13 declared 5-star sources listed in
``data/index/subcat/0611__lazy_susan.jsonl`` — see
``articraft_template_authoring/specs_modular_v1/pictureX_0611_lazy_susan.md``
for the per-module source table (record + exact ``model.py:Lx-Ly``).

Slots (all report into ``slot_choices_for_seed``):
  A base_form      flat_disk_base | pedestal_table | concealed_puck |
                   powered_console | cabinet_pullout                 (① skeleton + ③)
  B bearing_style  concealed_cap | flat_race_pair | exposed_ball_ring |
                   roller_set | spindle_thrust                       (① hardware + ③)
  C platter_form   lathe_stone_slab | chamfered_stone_disk | veneered_wood_disk |
                   two_tier_round | segmented_wedge | rounded_rect_tray  (③ Primary Form Family)
  D spin_joint     revolute_bounded | continuous_free                 (② joint type)
  E surface_style  marble_veins | tile_grout | radial_inlay |
                   veneer_seams | plain_polished                      (④ — NOT counted in core)
  F palette_style  6 observed colorways                               (⑥ — NOT counted in core)
  N axes           ball_count | roller_count | divider_count | tier_post_count

Topology: ``deck --spin(REVOLUTE|CONTINUOUS, z)--> platter``. ``cabinet_pullout``
prefixes a real chain ``cabinet_mount --PRISMATIC(+x)--> carriage
--REVOLUTE(z)--> swivel_arm``, and the swivel_arm IS the deck.

Geometric traceability (AUTHORING Contract 3c/3e): every cross-part relation is
derived from ONE helper. The z chain is
``deck_top_z (per base) -> _bearing_stack_height (per bearing) -> bearing.top_z
-> platter local z=0``; the radial chain is
``platter_radius -> _bearing_pitch_radius -> _race_half_width ->
_bearing_outer_radius -> _deck_radius``. No consumer restates any of them.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    LatheGeometry,
    MatingContract,
    MotionLimits,
    MotionProperties,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True


# --------------------------------------------------------------------------- #
# Slot vocabularies
# --------------------------------------------------------------------------- #
BaseForm = Literal[
    "flat_disk_base",
    "pedestal_table",
    "concealed_puck",
    "powered_console",
    "cabinet_pullout",
]
BASE_FORMS: tuple[BaseForm, ...] = (
    "flat_disk_base",
    "pedestal_table",
    "concealed_puck",
    "powered_console",
    "cabinet_pullout",
)

BearingStyle = Literal[
    "concealed_cap",
    "flat_race_pair",
    "exposed_ball_ring",
    "roller_set",
    "spindle_thrust",
]
BEARING_STYLES: tuple[BearingStyle, ...] = (
    "concealed_cap",
    "flat_race_pair",
    "exposed_ball_ring",
    "roller_set",
    "spindle_thrust",
)

PlatterForm = Literal[
    "lathe_stone_slab",
    "chamfered_stone_disk",
    "veneered_wood_disk",
    "two_tier_round",
    "segmented_wedge",
    "rounded_rect_tray",
]
PLATTER_FORMS: tuple[PlatterForm, ...] = (
    "lathe_stone_slab",
    "chamfered_stone_disk",
    "veneered_wood_disk",
    "two_tier_round",
    "segmented_wedge",
    "rounded_rect_tray",
)

SpinJoint = Literal["revolute_bounded", "continuous_free"]
SPIN_JOINTS: tuple[SpinJoint, ...] = ("revolute_bounded", "continuous_free")

SurfaceStyle = Literal[
    "marble_veins",
    "tile_grout",
    "radial_inlay",
    "veneer_seams",
    "plain_polished",
]
SURFACE_STYLES: tuple[SurfaceStyle, ...] = (
    "marble_veins",
    "tile_grout",
    "radial_inlay",
    "veneer_seams",
    "plain_polished",
)

PaletteStyle = Literal[
    "warm_marble_charcoal",
    "rose_marble_walnut",
    "walnut_brass_steel",
    "warm_wood_brass",
    "white_marble_steel",
    "powdercoat_bronze",
]
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "warm_marble_charcoal",
    "rose_marble_walnut",
    "walnut_brass_steel",
    "warm_wood_brass",
    "white_marble_steel",
    "powdercoat_bronze",
)

RGBA = tuple[float, float, float, float]

# ⑥ Six colorways; every rgba is lifted from a declared 5-star source's
# `model.material(...)` calls. Material classes covered: stone, wood, metal,
# painted, rubber/plastic (>= ceil(0.5*6)=3 required).
#   warm_marble_charcoal  S1  model.py:L59-L66
#   rose_marble_walnut    S2  model.py:L91-L97
#   walnut_brass_steel    S9  model.py:L22-L31
#   warm_wood_brass       S13 model.py:L51-L59
#   white_marble_steel    S10 model.py:L80-L86
#   powdercoat_bronze     S6  model.py:L74-L79
PALETTES: dict[PaletteStyle, dict[str, RGBA]] = {
    "warm_marble_charcoal": {
        "base_body": (0.075, 0.073, 0.070, 1.0),
        "base_accent": (0.105, 0.100, 0.092, 1.0),
        "pad": (0.045, 0.047, 0.045, 1.0),
        "metal": (0.48, 0.50, 0.51, 1.0),
        "metal_bright": (0.67, 0.70, 0.72, 1.0),
        "platter_body": (0.82, 0.80, 0.74, 1.0),
        "platter_accent": (0.91, 0.90, 0.86, 1.0),
        "platter_edge": (0.105, 0.100, 0.092, 1.0),
        "decor_line": (0.62, 0.60, 0.56, 1.0),
        "decor_mark": (0.56, 0.57, 0.56, 1.0),
    },
    "rose_marble_walnut": {
        "base_body": (0.29, 0.16, 0.095, 1.0),
        "base_accent": (0.20, 0.105, 0.060, 1.0),
        "pad": (0.035, 0.040, 0.038, 1.0),
        "metal": (0.34, 0.35, 0.34, 1.0),
        "metal_bright": (0.67, 0.70, 0.72, 1.0),
        "platter_body": (0.82, 0.72, 0.68, 1.0),
        "platter_accent": (0.94, 0.90, 0.86, 1.0),
        "platter_edge": (0.31, 0.23, 0.15, 1.0),
        "decor_line": (0.62, 0.46, 0.43, 1.0),
        "decor_mark": (0.94, 0.90, 0.86, 1.0),
    },
    "walnut_brass_steel": {
        "base_body": (0.055, 0.060, 0.065, 1.0),
        "base_accent": (0.28, 0.17, 0.11, 1.0),
        "pad": (0.018, 0.020, 0.022, 1.0),
        "metal": (0.55, 0.58, 0.59, 1.0),
        "metal_bright": (0.69, 0.52, 0.22, 1.0),
        "platter_body": (0.43, 0.25, 0.14, 1.0),
        "platter_accent": (0.70, 0.58, 0.44, 1.0),
        "platter_edge": (0.24, 0.12, 0.065, 1.0),
        "decor_line": (0.69, 0.52, 0.22, 1.0),
        "decor_mark": (0.69, 0.52, 0.22, 1.0),
    },
    "warm_wood_brass": {
        "base_body": (0.31, 0.19, 0.12, 1.0),
        "base_accent": (0.24, 0.14, 0.085, 1.0),
        "pad": (0.035, 0.040, 0.038, 1.0),
        "metal": (0.58, 0.61, 0.62, 1.0),
        "metal_bright": (0.73, 0.76, 0.78, 1.0),
        "platter_body": (0.56, 0.42, 0.30, 1.0),
        "platter_accent": (0.70, 0.58, 0.44, 1.0),
        "platter_edge": (0.31, 0.19, 0.12, 1.0),
        "decor_line": (0.24, 0.14, 0.085, 1.0),
        "decor_mark": (0.62, 0.45, 0.17, 1.0),
    },
    "white_marble_steel": {
        "base_body": (0.19, 0.20, 0.20, 1.0),
        "base_accent": (0.39, 0.41, 0.42, 1.0),
        "pad": (0.045, 0.047, 0.045, 1.0),
        "metal": (0.39, 0.41, 0.42, 1.0),
        "metal_bright": (0.72, 0.75, 0.77, 1.0),
        "platter_body": (0.86, 0.84, 0.78, 1.0),
        "platter_accent": (0.72, 0.66, 0.55, 1.0),
        "platter_edge": (0.47, 0.48, 0.46, 1.0),
        "decor_line": (0.47, 0.48, 0.46, 1.0),
        "decor_mark": (0.72, 0.66, 0.55, 1.0),
    },
    "powdercoat_bronze": {
        "base_body": (0.075, 0.073, 0.070, 1.0),
        "base_accent": (0.105, 0.100, 0.092, 1.0),
        "pad": (0.13, 0.14, 0.13, 1.0),
        "metal": (0.48, 0.50, 0.51, 1.0),
        "metal_bright": (0.67, 0.70, 0.72, 1.0),
        "platter_body": (0.79, 0.77, 0.70, 1.0),
        "platter_accent": (0.88, 0.86, 0.80, 1.0),
        "platter_edge": (0.27, 0.23, 0.18, 1.0),
        "decor_line": (0.27, 0.23, 0.18, 1.0),
        "decor_mark": (0.13, 0.14, 0.13, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Real absolute constants (each carries a one-line basis, Contract 3e)
# --------------------------------------------------------------------------- #

# Fraction of a ball's diameter that stands proud of the fixed race land, i.e.
# the ball's exposed crown that the rotating race actually rides on. Basis: the
# ball sits 45% recessed in the race groove (S5 model.py:L146-L156 seats the ball
# centre on the race top face; S13 model.py:L91-L100 likewise), so 1.55*ball_r of
# it is proud. The rotating race RESTS on those crowns — a loaded ball race has
# no air gap there; S13 model.py:L253-L262's 0.0005-0.002 m clearance band is
# race-to-race, and here it emerges as 1.55*ball_r by construction.
_BALL_PROUD_FACTOR = 1.55

# Radial clearance of a captured spindle in its rotor bore. Basis: S11
# model.py:L87 axle r=0.0065 inside model.py:L113 rotor_hub bore r=0.0075 -> 1.0mm;
# 0.8mm keeps the same fit class at the small end of our radius domain.
_AXLE_BORE_CLEARANCE = 0.0008

# Decoration strip thickness. Basis: S1 model.py:L39 `Box((length, width, 0.00045))`.
_DECO_T = 0.00045

# Tessellation budget (spec §7.5).
_LATHE_SEGMENTS = 64
_CQ_TOL_BODY = 0.0015
_CQ_ATOL_BODY = 0.10
_CQ_TOL_SMALL = 0.0008
_CQ_ATOL_SMALL = 0.12


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class PictureX0611LazySusanConfig:
    base_form: BaseForm = "flat_disk_base"
    bearing_style: BearingStyle = "concealed_cap"
    platter_form: PlatterForm = "lathe_stone_slab"
    spin_joint: SpinJoint = "revolute_bounded"
    surface_style: SurfaceStyle = "marble_veins"
    palette_style: PaletteStyle = "warm_marble_charcoal"
    platter_radius: float = 0.42
    platter_thickness: float = 0.022
    bearing_span_ratio: float = 0.30
    base_span_ratio: float = 0.88
    table_height: float = 0.70
    tier_gap_ratio: float = 0.47
    tray_aspect: float = 0.74
    ball_count: int = 16
    roller_count: int = 3
    divider_count: int = 6
    tier_post_count: int = 3
    name: str = "pictureX_0611_lazy_susan"


@dataclass(frozen=True)
class ResolvedPictureX0611LazySusanConfig:
    base_form: BaseForm
    bearing_style: BearingStyle
    platter_form: PlatterForm
    spin_joint: SpinJoint
    surface_style: SurfaceStyle
    palette_style: PaletteStyle
    platter_radius: float
    platter_thickness: float
    bearing_span_ratio: float
    base_span_ratio: float
    table_height: float
    tier_gap_ratio: float
    tray_aspect: float
    ball_count: int
    roller_count: int
    divider_count: int
    tier_post_count: int
    name: str


# --------------------------------------------------------------------------- #
# Compatibility gates (spec §Compatibility Gates G1-G3)
# --------------------------------------------------------------------------- #
def _gate_platter(base: BaseForm, platter: PlatterForm) -> PlatterForm:
    """G1/G2: a rounded-rectangle tray is not a banquet-table / powered-console form."""
    if platter == "rounded_rect_tray":
        if base == "pedestal_table":
            return "chamfered_stone_disk"
        if base == "powered_console":
            return "veneered_wood_disk"
    return platter


def _gate_bearing(base: BaseForm, bearing: BearingStyle) -> BearingStyle:
    """G3: a single centre spindle cannot carry a 1.3m banquet stone's rim."""
    if bearing == "spindle_thrust" and base == "pedestal_table":
        return "flat_race_pair"
    return bearing


# --------------------------------------------------------------------------- #
# Derived geometry — every shared quantity has exactly ONE definition here
# --------------------------------------------------------------------------- #
def _bearing_pitch_radius(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """Radius of the bearing's load track. S5 model.py:L26 (0.305 at platter 0.660)."""
    return r.platter_radius * r.bearing_span_ratio


def _race_half_width(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """S2 model.py:L123-L127: (0.355-0.255)/2 / 0.305 = 0.164 of the pitch radius."""
    return max(0.008, 0.164 * _bearing_pitch_radius(r))


def _ball_radius(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """S13 model.py:L91-L96: ball 0.0062 at platter 0.407 -> 0.0152*R, capped by packing."""
    pitch = _bearing_pitch_radius(r)
    by_scale = 0.0152 * r.platter_radius
    by_packing = 0.35 * (2.0 * math.pi * pitch / max(1, r.ball_count))
    return max(0.0022, min(by_scale, by_packing))


def _roller_radius(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """S12 model.py:L78-L83: roller 0.019 at platter 0.560 -> 0.034*R, capped by packing."""
    pitch = _bearing_pitch_radius(r)
    by_scale = 0.034 * r.platter_radius
    by_packing = 0.40 * (2.0 * math.pi * pitch / max(1, r.roller_count))
    return max(0.004, min(by_scale, by_packing))


def _roller_thickness(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """S12 model.py:L78-L83: 0.007 at platter 0.560 -> 0.0125*R."""
    return max(0.003, 0.0125 * r.platter_radius)


def _roller_stub(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """Visible axle stub between deck and roller (S12 model.py:L84-L89 axle is proud)."""
    return 0.25 * _roller_thickness(r)


def _race_thickness(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """S2 model.py:L123-L128: race h=0.012 at platter 0.660 -> 0.0182*R."""
    return max(0.004, 0.0182 * r.platter_radius)


def _cap_mount_thickness(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """S1 model.py:L84-L94: bearing_mount and bearing_cap are both 0.003 at platter 0.420."""
    return max(0.002, 0.00714 * r.platter_radius)


def _thrust_pad_thickness(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """S11 model.py:L71-L76: thrust_pad 0.002 at platter 0.275 -> 0.0073*R."""
    return max(0.002, 0.0073 * r.platter_radius)


def _rotor_hub_height(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """S11 model.py:L113: rotor_hub h=0.012 at pitch 0.0665 -> 0.18*pitch."""
    return max(0.006, 0.18 * _bearing_pitch_radius(r))


def _axle_radius(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """S11 model.py:L84-L88: axle r=0.0065 at pitch 0.0665 -> 0.098*pitch."""
    return max(0.0022, 0.098 * _bearing_pitch_radius(r))


def _bearing_outer_radius(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """Outermost radius of the bearing hardware — THE datum the deck is sized to."""
    pitch = _bearing_pitch_radius(r)
    style = r.bearing_style
    if style == "concealed_cap":
        # S1 model.py:L89: bearing_mount 0.112 vs bearing_cap 0.074 -> 1.51x the cap.
        return 1.5 * pitch
    if style == "roller_set":
        return pitch + _roller_radius(r)
    # flat_race_pair / exposed_ball_ring / spindle_thrust all end at the race rim.
    return pitch + _race_half_width(r)


def _bearing_stack_height(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """Height from the deck's top face to the plane the platter's rotor sits on."""
    style = r.bearing_style
    if style == "concealed_cap":
        return 2.0 * _cap_mount_thickness(r)
    if style == "flat_race_pair":
        return _race_thickness(r)
    if style == "exposed_ball_ring":
        return _race_thickness(r) + _BALL_PROUD_FACTOR * _ball_radius(r)
    if style == "roller_set":
        return _roller_stub(r) + _roller_thickness(r)
    return _thrust_pad_thickness(r)


def _deck_land_factor(base: BaseForm) -> float:
    """Fraction of deck_radius that is flat land at deck_top_z.

    `powered_console` raises a `bearing_support` platform narrower than the
    housing (S12 model.py:L61-L66: 0.285 support on a 0.355 housing = 0.80), so
    the bearing must fit inside 0.80*deck_radius, not deck_radius.
    """
    return 0.80 if base == "powered_console" else 1.0


def _deck_radius(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """Derived from the bearing envelope; never independently sampled."""
    needed = (_bearing_outer_radius(r) + 0.010) / _deck_land_factor(r.base_form)
    if r.base_form == "cabinet_pullout":
        # S7 model.py:L147: the swivel support_pad (0.110) is bearing-sized, not
        # platter-sized (it matches S1's bearing_mount 0.112, model.py:L89).
        return needed
    return max(r.platter_radius * r.base_span_ratio, needed)


def _tray_half_extents(
    r: ResolvedPictureX0611LazySusanConfig,
) -> tuple[float, float, float]:
    """rounded_rect_tray master descriptor: (half_w, half_d, corner_r). S6 model.py:L22-L26."""
    half_w = 0.90 * r.platter_radius
    half_d = half_w * r.tray_aspect
    corner_r = 0.268 * min(half_w, half_d)  # S6: 0.075 / 0.280 = 0.268
    return half_w, half_d, corner_r


def _platter_cover_radius(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """Smallest radius at which the platter still covers the bearing hardware."""
    if r.platter_form == "rounded_rect_tray":
        half_w, half_d, _ = _tray_half_extents(r)
        return min(half_w, half_d)
    return r.platter_radius


def _rotor_disc_radius(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """Radius of the platter's carrier / drive disc — sized to the bearing it covers."""
    cover = _platter_cover_radius(r)
    return min(0.93 * cover, max(_bearing_outer_radius(r) + 0.008, 0.35 * r.platter_radius))


def _swing_offset(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """S7 model.py:L24: SWING_OFFSET 0.180 / TOP_RADIUS 0.420 = 0.4286."""
    return 0.43 * r.platter_radius


def _pull_travel(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """S7 model.py:L25: PULL_TRAVEL 0.240 / TOP_RADIUS 0.420 = 0.5714."""
    return 0.571 * r.platter_radius


def _table_radius(r: ResolvedPictureX0611LazySusanConfig) -> float:
    """S2 model.py:L20,L23: TABLE_RADIUS 1.175 / PLATTER_RADIUS 0.660 = 1.780.

    Keeps the category-identity ratio platter_d / table_d = 0.562 (S2 asserts
    0.53-0.59 at model.py:L282-L290).
    """
    return 1.78 * r.platter_radius


# --------------------------------------------------------------------------- #
# Sampling
# --------------------------------------------------------------------------- #
def config_from_seed(seed: int) -> PictureX0611LazySusanConfig:
    """Deterministic procedural sampling for EVERY seed, including seed 0."""
    rng = random.Random(seed)
    base = rng.choice(BASE_FORMS)
    bearing = _gate_bearing(base, rng.choice(BEARING_STYLES))
    platter = _gate_platter(base, rng.choice(PLATTER_FORMS))
    # Weighted small-N multiplicity (spec §8: small N frequent, tail rare).
    ball_count = rng.choices((10, 12, 14, 16, 18, 20, 24, 28), weights=(2, 5, 4, 5, 3, 3, 4, 2))[0]
    roller_count = rng.choices((3, 4, 5, 6), weights=(6, 4, 3, 2))[0]
    divider_count = rng.choices((4, 5, 6, 7, 8), weights=(3, 3, 6, 3, 2))[0]
    tier_post_count = rng.choices((3, 4, 5), weights=(6, 3, 2))[0]
    return PictureX0611LazySusanConfig(
        base_form=base,
        bearing_style=bearing,
        platter_form=platter,
        spin_joint=rng.choice(SPIN_JOINTS),
        surface_style=rng.choice(SURFACE_STYLES),
        palette_style=rng.choice(PALETTE_STYLES),
        platter_radius=round(rng.uniform(0.16, 0.68), 4),
        platter_thickness=round(rng.uniform(0.016, 0.036), 4),
        bearing_span_ratio=round(rng.uniform(0.20, 0.46), 4),
        base_span_ratio=round(rng.uniform(0.42, 0.95), 4),
        table_height=round(rng.uniform(0.62, 0.76), 4),
        tier_gap_ratio=round(rng.uniform(0.40, 0.58), 4),
        tray_aspect=round(rng.uniform(0.62, 0.92), 4),
        ball_count=ball_count,
        roller_count=roller_count,
        divider_count=divider_count,
        tier_post_count=tier_post_count,
        name=f"pictureX_0611_lazy_susan_seed_{seed}",
    )


def _with_span(
    r: ResolvedPictureX0611LazySusanConfig, span: float
) -> ResolvedPictureX0611LazySusanConfig:
    return ResolvedPictureX0611LazySusanConfig(
        base_form=r.base_form,
        bearing_style=r.bearing_style,
        platter_form=r.platter_form,
        spin_joint=r.spin_joint,
        surface_style=r.surface_style,
        palette_style=r.palette_style,
        platter_radius=r.platter_radius,
        platter_thickness=r.platter_thickness,
        bearing_span_ratio=span,
        base_span_ratio=r.base_span_ratio,
        table_height=r.table_height,
        tier_gap_ratio=r.tier_gap_ratio,
        tray_aspect=r.tray_aspect,
        ball_count=r.ball_count,
        roller_count=r.roller_count,
        divider_count=r.divider_count,
        tier_post_count=r.tier_post_count,
        name=r.name,
    )


def resolve_config(
    config: PictureX0611LazySusanConfig,
) -> ResolvedPictureX0611LazySusanConfig:
    """The single legalization/derivation entry point (spec §7 sampling contract)."""
    base = config.base_form
    if base not in BASE_FORMS:
        raise ValueError(f"unknown base_form {base!r}")
    bearing = _gate_bearing(base, config.bearing_style)
    if bearing not in BEARING_STYLES:
        raise ValueError(f"unknown bearing_style {config.bearing_style!r}")
    platter = _gate_platter(base, config.platter_form)
    if platter not in PLATTER_FORMS:
        raise ValueError(f"unknown platter_form {config.platter_form!r}")
    if config.spin_joint not in SPIN_JOINTS:
        raise ValueError(f"unknown spin_joint {config.spin_joint!r}")
    if config.surface_style not in SURFACE_STYLES:
        raise ValueError(f"unknown surface_style {config.surface_style!r}")
    if config.palette_style not in PALETTE_STYLES:
        raise ValueError(f"unknown palette_style {config.palette_style!r}")

    # 1. independent primary scales
    platter_radius = _clamp(config.platter_radius, 0.16, 0.68)
    if base == "cabinet_pullout":
        # Cabinet envelope (spec §7 inequality; S7 authored at R=0.420).
        platter_radius = min(platter_radius, 0.40)
    span = _clamp(config.bearing_span_ratio, 0.20, 0.46)
    base_span = _clamp(config.base_span_ratio, 0.42, 0.95)
    if base == "concealed_puck":
        # S8 model.py:L61 (0.493*R) / S11 model.py:L57 (0.553*R): the puck is
        # deliberately much smaller than the platter that hides it.
        base_span = _clamp(base_span, 0.42, 0.60)

    # 2. derive + 3. project onto the feasible region (the platter must cover the
    #    bearing); `span` is the only free radial variable, so shrink it.
    r = ResolvedPictureX0611LazySusanConfig(
        base_form=base,
        bearing_style=bearing,
        platter_form=platter,
        spin_joint=config.spin_joint,
        surface_style=config.surface_style,
        palette_style=config.palette_style,
        platter_radius=platter_radius,
        platter_thickness=_clamp(config.platter_thickness, 0.016, 0.036),
        bearing_span_ratio=span,
        base_span_ratio=base_span,
        table_height=_clamp(config.table_height, 0.62, 0.76),
        tier_gap_ratio=_clamp(config.tier_gap_ratio, 0.40, 0.58),
        tray_aspect=_clamp(config.tray_aspect, 0.62, 0.92),
        ball_count=int(_clamp(config.ball_count, 10, 28)),
        roller_count=int(_clamp(config.roller_count, 3, 6)),
        divider_count=int(_clamp(config.divider_count, 4, 8)),
        tier_post_count=int(_clamp(config.tier_post_count, 3, 5)),
        name=config.name or "pictureX_0611_lazy_susan",
    )
    limit = 0.90 * _platter_cover_radius(r)
    for _ in range(30):
        if _bearing_outer_radius(r) + 0.010 <= limit:
            break
        r = _with_span(r, max(0.05, r.bearing_span_ratio * 0.92))
    return r


def slot_choices_for_config(
    config: PictureX0611LazySusanConfig | ResolvedPictureX0611LazySusanConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedPictureX0611LazySusanConfig)
        else resolve_config(config)
    )
    choices: list[tuple[str, str]] = [
        ("base_form", r.base_form),
        ("bearing_style", r.bearing_style),
        ("platter_form", r.platter_form),
        ("spin_joint", r.spin_joint),
        ("surface_style", r.surface_style),
        ("palette_style", r.palette_style),
    ]
    # Conditional N axes: only reported when their owning candidate is realized,
    # so axis_realization never claims an unreachable N.
    if r.bearing_style == "exposed_ball_ring":
        choices.append(("ball_count", str(r.ball_count)))
    if r.bearing_style == "roller_set":
        choices.append(("roller_count", str(r.roller_count)))
    if r.platter_form == "segmented_wedge":
        choices.append(("divider_count", str(r.divider_count)))
    if r.platter_form == "two_tier_round":
        choices.append(("tier_post_count", str(r.tier_post_count)))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Small geometry helpers
# --------------------------------------------------------------------------- #
def _annulus(outer: float, inner: float, height: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(outer).circle(max(1e-4, inner)).extrude(height)


def _soft_disc(radius: float, height: float, chamfer: float) -> cq.Workplane:
    """S11 model.py:L31-L34 `_soft_disc`; S8 model.py:L88-L89 uses the same idiom."""
    body = cq.Workplane("XY").circle(radius).extrude(height)
    ch = max(0.0004, min(chamfer, 0.30 * height, 0.10 * radius))
    try:
        return body.edges().chamfer(ch)
    except Exception:  # pragma: no cover - degenerate chamfer guard
        return body


def _rounded_box(width: float, depth: float, height: float, radius: float) -> cq.Workplane:
    """S6 model.py:L30-L37 `_rounded_box` (bottom at local z=0)."""
    body = cq.Workplane("XY").box(width, depth, height, centered=(True, True, False))
    rad = max(0.0005, min(radius, 0.49 * min(width, depth)))
    try:
        return body.edges("|Z").fillet(rad)
    except Exception:  # pragma: no cover
        return body


def _lathe_slab_profile(radius: float, z0: float, thickness: float) -> list[tuple[float, float]]:
    """S1 model.py:L103-L112 eased/chamfered stone rim, expressed as ratios of (R, t)."""
    er1 = 0.024 * radius  # S1: 0.010 / 0.420
    er2 = 0.0048 * radius  # S1: 0.002 / 0.420
    er3 = 0.0071 * radius  # S1: 0.003 / 0.420
    t = thickness
    z1 = z0 + t
    return [
        (0.0, z0),
        (radius - er1, z0),
        (radius - er2, z0 + 0.088 * t),  # S1: 0.0015 / 0.017
        (radius, z0 + 0.235 * t),  # S1: 0.004 / 0.017
        (radius, z1 - 0.176 * t),  # S1: 0.003 / 0.017
        (radius - er3, z1 - 0.059 * t),  # S1: 0.001 / 0.017
        (radius - er1, z1),
        (0.0, z1),
    ]


@dataclass(frozen=True)
class _PlatterSurface:
    """Master descriptor of the platter's FINAL visible top face.

    ④ decoration derives from this and nothing else (Rule 4: derive order is
    ③ form -> ⑤ dims -> ④ decoration), so a decoration hugs a round slab, a
    two-tier upper tray, or a rounded-rectangle tray floor without restating any
    of their dimensions.
    """

    kind: str  # "round" | "rect"
    top_z: float
    radius: float = 0.0
    half_w: float = 0.0
    half_d: float = 0.0
    corner_r: float = 0.0

    def contains(self, x: float, y: float, margin: float = 0.0) -> bool:
        """Exact host-boundary test (circle, or S6's rounded rectangle)."""
        if self.kind == "round":
            return math.hypot(x, y) <= self.radius - margin
        hw = self.half_w - margin
        hd = self.half_d - margin
        cr = min(self.corner_r, hw, hd)
        if hw <= 0.0 or hd <= 0.0:
            return False
        if abs(x) > hw or abs(y) > hd:
            return False
        # Rounded-rectangle SDF: only the corner quadrant is curved.
        qx = max(abs(x) - (hw - cr), 0.0)
        qy = max(abs(y) - (hd - cr), 0.0)
        return math.hypot(qx, qy) <= cr

    def extent_at(self, angle: float) -> float:
        """Usable radius of the host face along `angle` (exact, host-conformal)."""
        if self.kind == "round":
            return self.radius
        ca, sa = math.cos(angle), math.sin(angle)
        lo, hi = 0.0, math.hypot(self.half_w, self.half_d) + 1e-6
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if self.contains(mid * ca, mid * sa):
                lo = mid
            else:
                hi = mid
        return lo

    def clip_half_length(
        self, cx: float, cy: float, angle: float, half_len: float, margin: float
    ) -> float:
        """Longest half-length from (cx, cy) along `angle` keeping BOTH ends inside.

        A strip's centre angle and its own direction are independent (S1's veins
        are laid at arbitrary yaw), so sizing it from the centre's extent alone
        lets an end run off a short side of a rounded-rectangle host. This clips
        against the real boundary in the strip's OWN direction.
        """
        if not self.contains(cx, cy, margin):
            return 0.0
        dx, dy = math.cos(angle), math.sin(angle)
        lo, hi = 0.0, max(0.0, half_len)
        for _ in range(32):
            mid = 0.5 * (lo + hi)
            if self.contains(cx + mid * dx, cy + mid * dy, margin) and self.contains(
                cx - mid * dx, cy - mid * dy, margin
            ):
                lo = mid
            else:
                hi = mid
        return lo


def _deco_line(
    part,
    surface: _PlatterSurface,
    *,
    name: str,
    length: float,
    width: float,
    center_xy: tuple[float, float],
    angle: float,
    material,
) -> bool:
    """S1 model.py:L26-L46 `_add_surface_line`, anchored to the host's final face.

    15% embedded in the host (bonded, never a floating island), 85% proud (reads).
    The length is clipped to the host's real boundary along the strip's own
    direction, so it conforms to a circle, a two-tier upper tray, or S6's
    rounded-rectangle floor alike. Returns False when the strip does not fit.
    """
    cx, cy = center_xy
    margin = 0.5 * width
    half = surface.clip_half_length(cx, cy, angle, 0.5 * length, margin)
    if 2.0 * half < 3.0 * width:  # too stubby to read -> drop rather than float
        return False
    part.visual(
        Box((2.0 * half, width, _DECO_T)),
        origin=Origin(
            xyz=(cx, cy, surface.top_z + 0.35 * _DECO_T),
            rpy=(0.0, 0.0, angle),
        ),
        material=material,
        name=name, appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    return True


# --------------------------------------------------------------------------- #
# Slot A — base_form
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _BaseBuild:
    deck_part_name: str
    deck_top_z: float
    deck_cx: float
    deck_cy: float
    joints: tuple[str, ...]


def _joint_meta(joint_type, axis, origin, limits) -> dict[str, object]:
    return {
        "type": joint_type.value if hasattr(joint_type, "value") else str(joint_type),
        "axis": tuple(float(a) for a in axis),
        "origin": tuple(float(o) for o in origin),
        "range": (
            (float(limits.lower), float(limits.upper))
            if limits is not None and limits.lower is not None and limits.upper is not None
            else "continuous"
        ),
    }


def _build_flat_disk_base(model, r, mats) -> _BaseBuild:
    """S1 model.py:L70-L99."""
    base = model.part("base")
    deck_r = _deck_radius(r)
    pad_t = max(0.002, 0.00714 * r.platter_radius)  # S1 L72-76: 0.003 / 0.420
    disk_t = max(0.003, 0.0143 * r.platter_radius)  # S1 L77-82: 0.006 / 0.420
    base.visual(
        Cylinder(radius=0.689 * deck_r, length=pad_t),  # S1 L72: 0.255 / 0.370
        origin=Origin(xyz=(0.0, 0.0, 0.5 * pad_t)),
        material=mats["pad"],
        name="non_slip_pad", material_class_id="rubber.pebbled",
    )
    base.visual(
        Cylinder(radius=deck_r, length=disk_t),
        origin=Origin(xyz=(0.0, 0.0, pad_t + 0.5 * disk_t)),
        material=mats["base_body"],
        name="support_disk", material_class_id=("metal.paint_coated" if r.palette_style in {"warm_marble_charcoal", "walnut_brass_steel", "white_marble_steel", "powdercoat_bronze"} else "wood.mahogany_teak_dark"),
    )
    base.inertial = Inertial.from_geometry(
        Cylinder(radius=deck_r, length=pad_t + disk_t),
        mass=2.4,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (pad_t + disk_t))),
    )
    return _BaseBuild("base", pad_t + disk_t, 0.0, 0.0, ())


def _build_pedestal_table(model, r, mats) -> _BaseBuild:
    """S2 model.py:L28-L51 (cadquery loft pedestal) + L106-L122."""
    base = model.part("base")
    table_r = _table_radius(r)
    s = table_r / 1.175  # S2 L20 authored TABLE_RADIUS
    hs = r.table_height / 0.700  # S2 L21 authored TABLETOP_BOTTOM_Z

    foot = cq.Workplane("XY").circle(0.500 * s).extrude(0.060 * hs)
    lower_flare = (
        cq.Workplane("XY")
        .workplane(offset=0.060 * hs)
        .circle(0.300 * s)
        .workplane(offset=0.140 * hs)
        .circle(0.205 * s)
        .loft(combine=True)
    )
    column = cq.Workplane("XY").workplane(offset=0.200 * hs).circle(0.175 * s).extrude(0.440 * hs)
    upper_flare = (
        cq.Workplane("XY")
        .workplane(offset=0.640 * hs)
        .circle(0.180 * s)
        .workplane(offset=0.060 * hs)
        .circle(0.285 * s)
        .loft(combine=True)
    )
    pedestal = foot.union(lower_flare).union(column).union(upper_flare)
    base.visual(
        mesh_from_cadquery(
            pedestal,
            "lazy_susan_pedestal",
            tolerance=_CQ_TOL_BODY,
            angular_tolerance=_CQ_ATOL_BODY,
        ),
        material=mats["base_accent"],
        name="pedestal", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.paint_coated"),
    )

    tt_t = 0.070 * hs  # S2 L22 TABLETOP_THICKNESS
    top = cq.Workplane("XY").circle(table_r).extrude(tt_t)
    try:
        top = top.edges().fillet(min(0.010 * s, 0.4 * tt_t))
    except Exception:  # pragma: no cover
        pass
    base.visual(
        mesh_from_cadquery(
            top,
            "lazy_susan_tabletop",
            tolerance=_CQ_TOL_BODY,
            angular_tolerance=_CQ_ATOL_BODY,
        ),
        origin=Origin(xyz=(0.0, 0.0, r.table_height)),
        material=mats["base_body"],
        name="tabletop", material_class_id=("metal.paint_coated" if r.palette_style in {"warm_marble_charcoal", "walnut_brass_steel", "white_marble_steel", "powdercoat_bronze"} else "wood.mahogany_teak_dark"),
    )

    deck_r = _deck_radius(r)
    disk_t = max(0.004, 0.0212 * r.platter_radius)  # S2 L118: 0.014 / 0.660
    base.visual(
        Cylinder(radius=deck_r, length=disk_t),
        origin=Origin(xyz=(0.0, 0.0, r.table_height + tt_t + 0.5 * disk_t)),
        material=mats["platter_edge"],
        name="lower_support_disk", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.bronze_cast"),
    )
    base.inertial = Inertial.from_geometry(
        Cylinder(radius=table_r, length=r.table_height + tt_t),
        mass=48.0,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (r.table_height + tt_t))),
    )
    return _BaseBuild("base", r.table_height + tt_t + disk_t, 0.0, 0.0, ())


def _build_concealed_puck(model, r, mats) -> _BaseBuild:
    """S8 model.py:L54-L80; S11 model.py:L55-L88."""
    base = model.part("base")
    deck_r = _deck_radius(r)
    pad_t = max(0.002, 0.011 * r.platter_radius)  # S11 L65: 0.003 / 0.275
    body_t = max(0.004, 0.029 * r.platter_radius)  # S11 L57: 0.008 / 0.275
    base.visual(
        mesh_from_cadquery(
            _annulus(0.97 * deck_r, 0.70 * deck_r, pad_t),  # S11 L65: 0.148/0.112 on 0.152
            "lazy_susan_rubber_pad",
            tolerance=_CQ_TOL_SMALL,
            angular_tolerance=_CQ_ATOL_SMALL,
        ),
        material=mats["pad"],
        name="rubber_pad", material_class_id="rubber.smooth_plain",
    )
    base.visual(
        mesh_from_cadquery(
            _soft_disc(deck_r, body_t, 0.0073 * r.platter_radius),  # S11 L57: 0.002/0.275
            "lazy_susan_puck_body",
            tolerance=_CQ_TOL_BODY,
            angular_tolerance=_CQ_ATOL_BODY,
        ),
        origin=Origin(xyz=(0.0, 0.0, pad_t)),
        material=mats["base_body"],
        name="base_body", material_class_id=("metal.paint_coated" if r.palette_style in {"warm_marble_charcoal", "walnut_brass_steel", "white_marble_steel", "powdercoat_bronze"} else "wood.mahogany_teak_dark"),
    )
    base.inertial = Inertial.from_geometry(
        Cylinder(radius=deck_r, length=pad_t + body_t),
        mass=1.6,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (pad_t + body_t))),
    )
    return _BaseBuild("base", pad_t + body_t, 0.0, 0.0, ())


def _build_powered_console(model, r, mats) -> _BaseBuild:
    """S12 model.py:L43-L179 (S9 model.py:L44-L179 is the sibling anchor).

    Deviation from S12: S12's `bearing_support` (z 0.056-0.078) floats 8mm above
    `base_housing` (z 0.004-0.048) — a disconnected island. Here its underside is
    DERIVED as the housing's top face, so it is seated.
    """
    base = model.part("base")
    deck_r = _deck_radius(r)
    pad_t = max(0.003, 0.016 * r.platter_radius)  # S12 L56: 0.009 / 0.560
    housing_t = max(0.012, 0.0786 * r.platter_radius)  # S12 L50: 0.044 / 0.560
    support_t = max(0.006, 0.0393 * r.platter_radius)  # S12 L62: 0.022 / 0.560
    housing_top = pad_t + housing_t
    deck_top = housing_top + support_t

    base.visual(
        Cylinder(radius=0.93 * deck_r, length=pad_t),  # S12 L56: 0.330 / 0.355
        origin=Origin(xyz=(0.0, 0.0, 0.5 * pad_t)),
        material=mats["pad"],
        name="rubber_pad", material_class_id="rubber.smooth_plain",
    )
    base.visual(
        Cylinder(radius=deck_r, length=housing_t),
        origin=Origin(xyz=(0.0, 0.0, pad_t + 0.5 * housing_t)),
        material=mats["base_body"],
        name="base_housing", material_class_id=("metal.paint_coated" if r.palette_style in {"warm_marble_charcoal", "walnut_brass_steel", "white_marble_steel", "powdercoat_bronze"} else "wood.mahogany_teak_dark"),
    )
    # Raised bearing platform (annulus) + central drive cover, tops coplanar so
    # together they form ONE flat land at deck_top for the bearing to sit on.
    base.visual(
        mesh_from_cadquery(
            _annulus(_deck_land_factor("powered_console") * deck_r, 0.40 * deck_r, support_t),
            "lazy_susan_bearing_support",
            tolerance=_CQ_TOL_SMALL,
            angular_tolerance=_CQ_ATOL_SMALL,
        ),
        origin=Origin(xyz=(0.0, 0.0, housing_top)),
        material=mats["metal"],
        name="bearing_support", material_class_id="metal.stainless_matte",
    )
    base.visual(
        Cylinder(radius=0.42 * deck_r, length=support_t),  # S12 L68: 0.120 / 0.355
        origin=Origin(xyz=(0.0, 0.0, housing_top + 0.5 * support_t)),
        material=mats["base_accent"],
        name="motor_cover", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.paint_coated"),
    )

    # Side electrical service pod, pushed out so it reads past the housing wall.
    pod_hx = 0.116 * deck_r  # S12 L96: (0.130/2) / 0.355
    pod_hy = 0.253 * deck_r  # S12 L96: (0.180/2) / 0.355
    pod_cx = 1.05 * deck_r
    pod_cz = pad_t + 0.5 * housing_t
    base.visual(
        Box((2.0 * pod_hx, 2.0 * pod_hy, housing_t)),
        origin=Origin(xyz=(pod_cx, 0.0, pod_cz)),
        material=mats["base_body"],
        name="control_pod", material_class_id=("metal.paint_coated" if r.palette_style in {"warm_marble_charcoal", "walnut_brass_steel", "white_marble_steel", "powdercoat_bronze"} else "wood.mahogany_teak_dark"),
    )
    base.visual(
        Box((0.24 * pod_hx, 1.22 * pod_hy, 0.34 * housing_t)),
        origin=Origin(xyz=(pod_cx + pod_hx, 0.0, pod_cz)),
        material=mats["metal_bright"],
        name="inspection_window", material_class_id="glass.clear_transparent",
    )
    for idx, sgn in enumerate((-1.0, 1.0)):
        base.visual(
            Box((0.42 * pod_hx, 0.38 * pod_hy, 0.21 * housing_t)),
            origin=Origin(xyz=(pod_cx + 0.80 * pod_hx, sgn * 0.36 * pod_hy, pod_cz)),
            material=mats["metal_bright"],
            name=f"brass_terminal_{idx}", material_class_id="metal.brass_polished",
        )
        base.visual(
            Cylinder(radius=0.10 * pod_hx, length=0.24 * housing_t),
            origin=Origin(
                xyz=(pod_cx + 0.80 * pod_hx, sgn * 0.36 * pod_hy, pod_cz + 0.16 * housing_t)
            ),
            material=mats["base_accent"],
            name=f"terminal_screw_{idx}", material_class_id="metal.brass_polished",
        )
    base.visual(
        Box((0.9 * pod_hx, 0.06 * pod_hy, 0.30 * housing_t)),
        origin=Origin(xyz=(pod_cx, -pod_hy, pod_cz - 0.12 * housing_t)),
        material=mats["metal_bright"],
        name="warning_label", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    gland_x = pod_cx + pod_hx
    base.visual(
        Cylinder(radius=0.24 * pod_hx, length=0.60 * pod_hx),
        origin=Origin(xyz=(gland_x + 0.20 * pod_hx, 0.0, pod_cz), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="cable_gland", material_class_id="metal.stainless_matte",
    )
    strain_x = gland_x + 0.55 * pod_hx
    base.visual(
        Cylinder(radius=0.17 * pod_hx, length=0.30 * pod_hx),
        origin=Origin(xyz=(strain_x, 0.0, pod_cz), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["pad"],
        name="strain_relief", material_class_id="rubber.smooth_plain",
    )
    cord_x0 = strain_x + 0.10 * pod_hx
    cord = tube_from_spline_points(
        [
            (cord_x0, 0.0, pod_cz),
            (cord_x0 + 0.55 * deck_r, -0.08 * deck_r, 0.75 * pod_cz),
            (cord_x0 + 1.10 * deck_r, -0.34 * deck_r, 0.60 * pod_cz),
            (cord_x0 + 1.65 * deck_r, -0.42 * deck_r, 0.58 * pod_cz),
        ],
        radius=0.12 * pod_hx,
        samples_per_segment=10,
        radial_segments=10,
        cap_ends=True,
    )
    base.visual(
        mesh_from_geometry(cord, "lazy_susan_power_cord"),
        material=mats["pad"],
        name="power_cord", material_class_id="rubber.smooth_plain",
    )
    plug_cx = cord_x0 + 1.65 * deck_r + 0.05 * deck_r
    base.visual(
        Box((0.12 * deck_r, 0.07 * deck_r, 0.055 * deck_r)),
        origin=Origin(xyz=(plug_cx, -0.42 * deck_r, 0.58 * pod_cz)),
        material=mats["base_body"],
        name="power_plug", material_class_id="plastic.opaque_glossy_molded",
    )
    for idx, sgn in enumerate((-1.0, 1.0)):
        base.visual(
            Box((0.05 * deck_r, 0.010 * deck_r, 0.024 * deck_r)),
            origin=Origin(
                xyz=(
                    plug_cx + 0.075 * deck_r,
                    -0.42 * deck_r + sgn * 0.018 * deck_r,
                    0.58 * pod_cz,
                )
            ),
            material=mats["metal_bright"],
            name=f"plug_blade_{idx}", material_class_id="metal.brass_polished",
        )

    base.inertial = Inertial.from_geometry(
        Cylinder(radius=deck_r, length=deck_top),
        mass=9.0,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * deck_top)),
    )
    return _BaseBuild("base", deck_top, 0.0, 0.0, ())


def _build_cabinet_pullout(model, r, mats) -> _BaseBuild:
    """S7 model.py:L77-L155 + L282-L312.

    Every cabinet dimension is a ratio of `platter_radius` (S7 authored them all
    against TOP_RADIUS=0.420), so the swing clearance to `rear_flange` holds for
    ANY radius: the platter reaches x_min = 0.147R - R = -0.853R while the flange
    sits at x ~= -1.215R -> 0.36R clear.

    Deviation from S7: S7's FIXED joint `swivel_arm_to_support` (L314-320) exists
    only to reuse S1's non-articulating `support` part. Per Rule 1 those visuals
    are fused into `swivel_arm` (`support_pad` IS the deck), removing the joint.
    """
    k = r.platter_radius
    deck_r = _deck_radius(r)
    swing = _swing_offset(r)
    travel = _pull_travel(r)

    plate_t = 0.0143 * k  # S7 L79: 0.006 / 0.420
    mount = model.part("cabinet_mount")
    mount.visual(
        Box((1.667 * k, 0.595 * k, plate_t)),  # S7 L79: 0.700 x 0.250
        origin=Origin(xyz=(-0.381 * k, 0.0, 0.5 * plate_t)),
        material=mats["base_accent"],
        name="mounting_plate", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.paint_coated"),
    )
    mount.visual(
        Box((0.0714 * k, 0.595 * k, 0.202 * k)),  # S7 L85: 0.030 x 0.250 x 0.085
        origin=Origin(xyz=(-1.179 * k, 0.0, 0.101 * k)),
        material=mats["base_accent"],
        name="rear_flange", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.paint_coated"),
    )
    for idx, sgn in enumerate((-1.0, 1.0)):
        mount.visual(
            Box((1.452 * k, 0.0619 * k, 0.0238 * k)),  # S7 L92: 0.610 x 0.026 x 0.010
            origin=Origin(xyz=(-0.464 * k, sgn * 0.219 * k, 0.0262 * k)),
            material=mats["metal"],
            name=f"guide_rail_{idx}", material_class_id="metal.stainless_matte",
        )
    mount.inertial = Inertial.from_geometry(
        Box((1.667 * k, 0.595 * k, 0.0381 * k)),
        mass=3.2,
        origin=Origin(xyz=(-0.381 * k, 0.0, 0.019 * k)),
    )

    arm_t = 0.0286 * k  # S7 L109: 0.012 / 0.420
    carriage = model.part("carriage")
    carriage.visual(
        Box((0.952 * k, 0.286 * k, arm_t)),  # S7 L109: 0.400 x 0.120
        origin=Origin(xyz=(-0.476 * k, 0.0, 0.5 * arm_t)),
        material=mats["base_accent"],
        name="pullout_arm", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.paint_coated"),
    )
    carriage.visual(
        Box((0.250 * k, 0.357 * k, arm_t)),  # S7 L114: 0.105 x 0.150
        origin=Origin(xyz=(-0.119 * k, 0.0, 0.5 * arm_t)),
        material=mats["base_accent"],
        name="swivel_yoke", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.paint_coated"),
    )
    boss_t = 0.019 * k  # S7 L119: 0.008 / 0.420
    carriage.visual(
        Cylinder(radius=0.124 * k, length=boss_t),  # S7 L119: 0.052 / 0.420
        origin=Origin(xyz=(0.0, 0.0, arm_t + 0.5 * boss_t)),
        material=mats["metal"],
        name="swivel_boss", material_class_id="metal.stainless_matte",
    )
    carriage.inertial = Inertial.from_geometry(
        Box((0.952 * k, 0.286 * k, arm_t + boss_t)),
        mass=2.0,
        origin=Origin(xyz=(-0.476 * k, 0.0, 0.5 * (arm_t + boss_t))),
    )

    pad_t = 0.00714 * k  # S7 L136: 0.003 / 0.420
    swivel = model.part("swivel_arm")
    swivel.visual(
        Cylinder(radius=0.124 * k, length=pad_t),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * pad_t)),
        material=mats["base_accent"],
        name="pivot_plate", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.paint_coated"),
    )
    swivel.visual(
        Box((swing, 0.167 * k, pad_t)),  # S7 L140: 0.070 / 0.420
        origin=Origin(xyz=(0.5 * swing, 0.0, 0.5 * pad_t)),
        material=mats["base_body"],
        name="offset_bridge", material_class_id=("metal.paint_coated" if r.palette_style in {"warm_marble_charcoal", "walnut_brass_steel", "white_marble_steel", "powdercoat_bronze"} else "wood.mahogany_teak_dark"),
    )
    swivel.visual(
        Cylinder(radius=deck_r, length=pad_t),
        origin=Origin(xyz=(swing, 0.0, 0.5 * pad_t)),
        material=mats["base_body"],
        name="support_pad", material_class_id=("metal.paint_coated" if r.palette_style in {"warm_marble_charcoal", "walnut_brass_steel", "white_marble_steel", "powdercoat_bronze"} else "wood.mahogany_teak_dark"),
    )
    swivel.inertial = Inertial.from_geometry(
        Box((swing + deck_r, 2.0 * deck_r, pad_t)),
        mass=0.65,
        origin=Origin(xyz=(0.5 * swing, 0.0, 0.5 * pad_t)),
    )

    pull_limits = MotionLimits(effort=180.0, velocity=0.35, lower=0.0, upper=travel)
    model.articulation(
        "mount_to_carriage",
        ArticulationType.PRISMATIC,
        parent=mount,
        child=carriage,
        origin=Origin(xyz=(0.0, 0.0, plate_t)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=pull_limits,
        motion_properties=MotionProperties(damping=18.0, friction=7.0),
        mating=MatingContract(
            parent_face_geometry="mounting_plate",
            parent_face_side="positive_z",
            child_face_geometry="pullout_arm",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
        meta=_joint_meta(
            ArticulationType.PRISMATIC, (1.0, 0.0, 0.0), (0.0, 0.0, plate_t), pull_limits
        ),
    )
    swivel_limits = MotionLimits(effort=28.0, velocity=1.2, lower=-1.22, upper=1.22)
    model.articulation(
        "carriage_to_swivel_arm",
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=swivel,
        origin=Origin(xyz=(0.0, 0.0, arm_t + boss_t)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=swivel_limits,
        motion_properties=MotionProperties(damping=0.8, friction=0.25),
        mating=MatingContract(
            parent_face_geometry="swivel_boss",
            parent_face_side="positive_z",
            child_face_geometry="pivot_plate",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
        meta=_joint_meta(
            ArticulationType.REVOLUTE,
            (0.0, 0.0, 1.0),
            (0.0, 0.0, arm_t + boss_t),
            swivel_limits,
        ),
    )
    return _BaseBuild(
        "swivel_arm", pad_t, swing, 0.0, ("mount_to_carriage", "carriage_to_swivel_arm")
    )


_BASE_BUILDERS = {
    "flat_disk_base": _build_flat_disk_base,
    "pedestal_table": _build_pedestal_table,
    "concealed_puck": _build_concealed_puck,
    "powered_console": _build_powered_console,
    "cabinet_pullout": _build_cabinet_pullout,
}


# --------------------------------------------------------------------------- #
# Slot B — bearing_style (stationary half on the deck, rotor half on the platter)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _BearingBuild:
    land_visual: str  # deck-side visual whose +z face the platter sits on
    top_z: float  # deck-frame z of that land == the spin joint origin z


def _build_bearing_static(model, r, mats, base: _BaseBuild) -> _BearingBuild:
    deck = model.get_part(base.deck_part_name)
    cx, cy = base.deck_cx, base.deck_cy
    z0 = base.deck_top_z
    pitch = _bearing_pitch_radius(r)
    style = r.bearing_style

    if style == "concealed_cap":
        t = _cap_mount_thickness(r)
        deck.visual(
            Cylinder(radius=1.5 * pitch, length=t),  # S1 L89: 0.112 vs cap 0.074
            origin=Origin(xyz=(cx, cy, z0 + 0.5 * t)),
            material=mats["base_accent"],
            name="bearing_mount", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.paint_coated"),
        )
        deck.visual(
            Cylinder(radius=pitch, length=t),  # S1 L94
            origin=Origin(xyz=(cx, cy, z0 + 1.5 * t)),
            material=mats["metal"],
            name="bearing_cap", material_class_id="metal.stainless_matte",
        )
        return _BearingBuild("bearing_cap", z0 + 2.0 * t)

    if style == "flat_race_pair":
        t = _race_thickness(r)
        rhw = _race_half_width(r)
        deck.visual(
            mesh_from_cadquery(
                _annulus(pitch + rhw, pitch - rhw, t),  # S2 L123-L128
                "lazy_susan_fixed_race",
                tolerance=_CQ_TOL_SMALL,
                angular_tolerance=_CQ_ATOL_SMALL,
            ),
            origin=Origin(xyz=(cx, cy, z0)),
            material=mats["metal"],
            name="fixed_bearing_race", material_class_id="metal.stainless_matte",
        )
        return _BearingBuild("fixed_bearing_race", z0 + t)

    if style == "exposed_ball_ring":
        t = _race_thickness(r)
        rhw = _race_half_width(r)
        ball_r = _ball_radius(r)
        deck.visual(
            mesh_from_cadquery(
                _annulus(pitch + rhw, pitch - rhw, t),
                "lazy_susan_fixed_race",
                tolerance=_CQ_TOL_SMALL,
                angular_tolerance=_CQ_ATOL_SMALL,
            ),
            origin=Origin(xyz=(cx, cy, z0)),
            material=mats["metal"],
            name="fixed_bearing_race", material_class_id="metal.stainless_matte",
        )
        # S13 model.py:L91-L100 uses the `Sphere` primitive (no per-ball
        # tessellation, unlike S5 L152 which meshes every ball separately).
        # Balls sit 45% recessed into the race land -> retained AND bonded.
        ball_cz = z0 + t + 0.55 * ball_r
        for i in range(r.ball_count):
            angle = 2.0 * math.pi * i / r.ball_count
            deck.visual(
                Sphere(radius=ball_r),
                origin=Origin(
                    xyz=(cx + pitch * math.cos(angle), cy + pitch * math.sin(angle), ball_cz)
                ),
                material=mats["metal_bright"],
                name=f"bearing_ball_{i}", material_class_id="metal.chrome_polished",
            )
        # The rotating race rides on the ball crowns: land == ball apex plane.
        return _BearingBuild("bearing_ball_0", ball_cz + ball_r)

    if style == "roller_set":
        roller_r = _roller_radius(r)
        roller_t = _roller_thickness(r)
        stub = _roller_stub(r)
        axle_r = 0.32 * roller_r
        axle_embed = min(0.6 * roller_t, 0.5 * z0) if z0 > 0.0 else 0.0
        axle_lo = z0 - axle_embed
        axle_hi = z0 + stub + 0.5 * roller_t
        for i in range(r.roller_count):
            angle = 2.0 * math.pi * i / r.roller_count
            px, py = cx + pitch * math.cos(angle), cy + pitch * math.sin(angle)
            deck.visual(
                Cylinder(radius=axle_r, length=axle_hi - axle_lo),  # S12 L84-L89
                origin=Origin(xyz=(px, py, 0.5 * (axle_lo + axle_hi))),
                material=mats["base_accent"],
                name=f"roller_axle_{i}", material_class_id="metal.stainless_matte",
            )
            deck.visual(
                Cylinder(radius=roller_r, length=roller_t),  # S12 L78-L83
                origin=Origin(xyz=(px, py, z0 + stub + 0.5 * roller_t)),
                material=mats["metal_bright"],
                name=f"support_roller_{i}", material_class_id="metal.chrome_polished",
            )
        return _BearingBuild("support_roller_0", z0 + stub + roller_t)

    # spindle_thrust — S11 model.py:L71-L88
    pad_t = _thrust_pad_thickness(r)
    rhw = _race_half_width(r)
    hub_h = _rotor_hub_height(r)
    deck.visual(
        Cylinder(radius=0.72 * pitch, length=pad_t),  # S11 L73: 0.048 / pitch 0.0665
        origin=Origin(xyz=(cx, cy, z0 + 0.5 * pad_t)),
        material=mats["metal"],
        name="thrust_pad", material_class_id="metal.stainless_matte",
    )
    deck.visual(
        mesh_from_cadquery(
            _annulus(pitch + rhw, pitch - rhw, pad_t),  # S11 L78
            "lazy_susan_guide_race",
            tolerance=_CQ_TOL_SMALL,
            angular_tolerance=_CQ_ATOL_SMALL,
        ),
        origin=Origin(xyz=(cx, cy, z0)),
        material=mats["metal"],
        name="bearing_race", material_class_id="metal.stainless_matte",
    )
    # The axle stops 25% short of the rotor hub's top so it never touches the
    # platter's backing plate; the bore keeps _AXLE_BORE_CLEARANCE radially.
    axle_h = pad_t + 0.75 * hub_h
    deck.visual(
        Cylinder(radius=_axle_radius(r), length=axle_h),  # S11 L84-L88
        origin=Origin(xyz=(cx, cy, z0 + 0.5 * axle_h)),
        material=mats["base_accent"],
        name="center_axle", material_class_id="metal.stainless_matte",
    )
    return _BearingBuild("thrust_pad", z0 + pad_t)


@dataclass(frozen=True)
class _RotorBuild:
    mating_visual: str  # platter-side visual whose -z face is at platter z=0
    top_z: float  # platter-frame z the platter body starts from


def _build_bearing_rotor(model, r, mats) -> _RotorBuild:
    """The rotating half of the SAME bearing — derived from the same helpers."""
    platter = model.get_part("platter")
    pitch = _bearing_pitch_radius(r)
    disc_r = _rotor_disc_radius(r)
    style = r.bearing_style

    if style == "concealed_cap":
        t = max(0.0025, 0.0119 * r.platter_radius)  # S1 L120: 0.005 / 0.420
        platter.visual(
            Cylinder(radius=disc_r, length=t),
            origin=Origin(xyz=(0.0, 0.0, 0.5 * t)),
            material=mats["platter_edge"],
            name="carrier_plate", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.bronze_cast"),
        )
        return _RotorBuild("carrier_plate", t)

    if style in ("flat_race_pair", "exposed_ball_ring"):
        rhw = _race_half_width(r)
        race_t = max(0.002, 0.4 * _race_thickness(r))
        platter.visual(
            mesh_from_cadquery(
                _annulus(pitch + rhw, pitch - rhw, race_t),  # S13 L115-L118
                "lazy_susan_rotating_race",
                tolerance=_CQ_TOL_SMALL,
                angular_tolerance=_CQ_ATOL_SMALL,
            ),
            material=mats["metal"],
            name="rotating_bearing_race", material_class_id="metal.stainless_matte",
        )
        carrier_t = max(0.003, 0.0152 * r.platter_radius)  # S2 L145: 0.010 / 0.660
        platter.visual(
            Cylinder(radius=disc_r, length=carrier_t),  # S2 L144-L149
            origin=Origin(xyz=(0.0, 0.0, race_t + 0.5 * carrier_t)),
            material=mats["platter_edge"],
            name="upper_carrier", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.bronze_cast"),
        )
        return _RotorBuild("rotating_bearing_race", race_t + carrier_t)

    if style == "roller_set":
        t = max(0.003, 0.0143 * r.platter_radius)  # S12 L186-L191: 0.008 / 0.560
        platter.visual(
            Cylinder(radius=disc_r, length=t),
            origin=Origin(xyz=(0.0, 0.0, 0.5 * t)),
            material=mats["pad"],
            name="drive_pad", material_class_id="rubber.smooth_plain",
        )
        return _RotorBuild("drive_pad", t)

    # spindle_thrust rotor — S11 model.py:L112-L117
    hub_h = _rotor_hub_height(r)
    bore = _axle_radius(r) + _AXLE_BORE_CLEARANCE
    hub_outer = 0.70 * pitch  # sits on thrust_pad (0.72*pitch), clears race inner
    platter.visual(
        mesh_from_cadquery(
            _annulus(hub_outer, bore, hub_h),
            "lazy_susan_rotor_hub",
            tolerance=_CQ_TOL_SMALL,
            angular_tolerance=_CQ_ATOL_SMALL,
        ),
        material=mats["metal"],
        name="rotor_hub", material_class_id="metal.stainless_matte",
    )
    plate_t = max(0.003, 0.011 * r.platter_radius)  # S11 L107: 0.003 / 0.275
    platter.visual(
        Cylinder(radius=disc_r, length=plate_t),  # S11 L106-L111 backing_plate
        origin=Origin(xyz=(0.0, 0.0, hub_h + 0.5 * plate_t)),
        material=mats["platter_edge"],
        name="backing_plate", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.bronze_cast"),
    )
    return _RotorBuild("rotor_hub", hub_h + plate_t)


# --------------------------------------------------------------------------- #
# Slot C — platter_form
# --------------------------------------------------------------------------- #
def _emit_lathe_tier(platter, r, mats, *, radius: float, z0: float, tag: str) -> _PlatterSurface:
    """S1 model.py:L103-L137 — the eased lathe slab + its polished face."""
    t = r.platter_thickness
    z1 = z0 + t
    platter.visual(
        mesh_from_geometry(
            LatheGeometry(_lathe_slab_profile(radius, z0, t), segments=_LATHE_SEGMENTS),
            f"lazy_susan_{tag}",
        ),
        material=mats["platter_body"],
        name=("top_stone" if tag == "stone_slab" else "upper_tray"), material_class_id=("marble.generic" if r.palette_style in {"warm_marble_charcoal", "rose_marble_walnut", "white_marble_steel", "powdercoat_bronze"} else "wood.mahogany_teak_dark"),
    )
    pf_t = 0.0004
    platter.visual(
        Cylinder(radius=0.964 * radius, length=pf_t),  # S1 L133: 0.405 / 0.420
        origin=Origin(xyz=(0.0, 0.0, z1)),
        material=mats["platter_accent"],
        name=("polished_face" if tag == "stone_slab" else "upper_polished_face"), material_class_id=("marble.generic" if r.palette_style in {"warm_marble_charcoal", "rose_marble_walnut", "white_marble_steel", "powdercoat_bronze"} else "wood.polished_varnished"),
    )
    return _PlatterSurface(kind="round", top_z=z1 + 0.5 * pf_t, radius=0.964 * radius)


def _build_lathe_stone_slab(model, r, mats, z0: float) -> _PlatterSurface:
    return _emit_lathe_tier(
        model.get_part("platter"), r, mats, radius=r.platter_radius, z0=z0, tag="stone_slab"
    )


def _build_chamfered_stone_disk(model, r, mats, z0: float) -> _PlatterSurface:
    """S8 model.py:L88-L94; S11 model.py:L92-L104."""
    platter = model.get_part("platter")
    radius = r.platter_radius
    t = r.platter_thickness
    ch = min(0.009 * radius, 0.13 * t)  # S11 L92: 0.0025 on (0.275, 0.018)
    platter.visual(
        mesh_from_cadquery(
            _soft_disc(radius, t, ch),
            "lazy_susan_marble_slab",
            tolerance=_CQ_TOL_BODY,
            angular_tolerance=_CQ_ATOL_BODY,
        ),
        origin=Origin(xyz=(0.0, 0.0, z0)),
        material=mats["platter_body"],
        name="marble_slab", material_class_id="marble.generic",
    )
    # S11 L99: the polished edge band stands 0.2mm proud of the slab wall.
    platter.visual(
        mesh_from_cadquery(
            _annulus(radius + 0.0006, 0.96 * radius, 0.70 * t),
            "lazy_susan_polished_edge",
            tolerance=_CQ_TOL_SMALL,
            angular_tolerance=_CQ_ATOL_SMALL,
        ),
        origin=Origin(xyz=(0.0, 0.0, z0 + 0.15 * t)),
        material=mats["platter_accent"],
        name="polished_edge", material_class_id="marble.generic",
    )
    return _PlatterSurface(kind="round", top_z=z0 + t, radius=radius - ch)


def _build_veneered_wood_disk(model, r, mats, z0: float) -> _PlatterSurface:
    """S13 model.py:L126-L148 (S9 model.py:L182-L205 is the sibling anchor)."""
    platter = model.get_part("platter")
    radius = r.platter_radius
    t = r.platter_thickness
    core_r = 0.969 * radius  # S13: platter_core 0.407 inside edge_band 0.420
    ch = min(0.010 * radius, 0.13 * t)
    platter.visual(
        mesh_from_cadquery(
            _soft_disc(core_r, t, ch),
            "lazy_susan_platter_core",
            tolerance=_CQ_TOL_BODY,
            angular_tolerance=_CQ_ATOL_BODY,
        ),
        origin=Origin(xyz=(0.0, 0.0, z0)),
        material=mats["platter_body"],
        name="platter_core", material_class_id="wood.engineered_board",
    )
    veneer_t = max(0.0015, 0.006 * radius)  # S13 L132: 0.0025 / 0.407
    # The veneer's top plane is stated ONCE and every consumer below (inlay ring,
    # the returned _PlatterSurface, hence all ④ decoration) reads it from here.
    veneer_center = z0 + t - 0.4 * veneer_t  # 40% sunk into the core -> bonded
    veneer_top = veneer_center + 0.5 * veneer_t
    platter.visual(
        Cylinder(radius=0.957 * radius, length=veneer_t),  # S13 L132: 0.402 / 0.420
        origin=Origin(xyz=(0.0, 0.0, veneer_center)),
        material=mats["platter_accent"],
        name="top_veneer", material_class_id="wood.veneer_panel",
    )
    platter.visual(
        mesh_from_cadquery(
            _annulus(radius, 0.962 * radius, 0.59 * t),  # S13 L138: 0.420 / 0.404
            "lazy_susan_edge_band",
            tolerance=_CQ_TOL_SMALL,
            angular_tolerance=_CQ_ATOL_SMALL,
        ),
        origin=Origin(xyz=(0.0, 0.0, z0 + 0.31 * t)),
        material=mats["platter_edge"],
        name="edge_band", material_class_id="wood.veneer_panel",
    )
    inlay_t = max(0.0008, 0.0033 * radius)  # S13 L144: 0.0014 / 0.420
    platter.visual(
        mesh_from_cadquery(
            _annulus(0.917 * radius, 0.902 * radius, inlay_t),  # S13 L144: 0.385 / 0.379
            "lazy_susan_top_inlay_ring",
            tolerance=_CQ_TOL_SMALL,
            angular_tolerance=_CQ_ATOL_SMALL,
        ),
        # Seated on the veneer's real top plane, 30% sunk in so it is bonded.
        origin=Origin(xyz=(0.0, 0.0, veneer_top - 0.3 * inlay_t)),
        material=mats["decor_line"],
        name="top_inlay_ring", material_class_id=("marble.generic" if r.palette_style in {"warm_marble_charcoal", "rose_marble_walnut", "warm_wood_brass"} else "metal.brass_polished"),
    )
    return _PlatterSurface(kind="round", top_z=veneer_top, radius=0.957 * radius)


def _build_two_tier_round(model, r, mats, z0: float) -> _PlatterSurface:
    """S3 model.py:L192-L246 — both tiers ride the SAME rotating part (one joint)."""
    platter = model.get_part("platter")
    radius = r.platter_radius
    _emit_lathe_tier(platter, r, mats, radius=radius, z0=z0, tag="stone_slab")
    lower_top = z0 + r.platter_thickness

    upper_r = 0.714 * radius  # S3 L24: 0.300 / 0.420
    post_ring_r = 0.536 * radius  # S3 L28: 0.225 / 0.420
    post_r = 0.0286 * radius  # S3 L27: 0.012 / 0.420
    tier_gap = radius * r.tier_gap_ratio
    uc_t = max(0.0025, 0.0119 * radius)  # S3 L216: 0.005 / 0.420
    upper_bottom = lower_top + tier_gap
    post_lo = lower_top
    post_hi = upper_bottom - uc_t
    post_h = max(0.005, post_hi - post_lo)

    for i in range(r.tier_post_count):
        angle = 2.0 * math.pi * i / r.tier_post_count
        platter.visual(
            Cylinder(radius=post_r, length=post_h),
            origin=Origin(
                xyz=(
                    post_ring_r * math.cos(angle),
                    post_ring_r * math.sin(angle),
                    post_lo + 0.5 * post_h,
                )
            ),
            material=mats["platter_edge"],
            name=f"upper_post_{i}", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.bronze_cast"),
        )
    platter.visual(
        Cylinder(radius=0.0714 * radius, length=post_h),  # S3 L210: 0.030 / 0.420
        origin=Origin(xyz=(0.0, 0.0, post_lo + 0.5 * post_h)),
        material=mats["metal"],
        name="central_support", material_class_id="metal.stainless_matte",
    )
    platter.visual(
        Cylinder(radius=0.95 * upper_r, length=uc_t),  # S3 L216: 0.285 / 0.300
        origin=Origin(xyz=(0.0, 0.0, post_hi + 0.5 * uc_t)),
        material=mats["platter_edge"],
        name="upper_carrier_plate", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.bronze_cast"),
    )
    return _emit_lathe_tier(platter, r, mats, radius=upper_r, z0=upper_bottom, tag="upper_tray")


def _build_segmented_wedge(model, r, mats, z0: float) -> _PlatterSurface:
    """S4 model.py:L64-L87 + L188-L212 — ONE divider mesh reused N times."""
    platter = model.get_part("platter")
    radius = r.platter_radius
    t = r.platter_thickness
    ch = min(0.009 * radius, 0.13 * t)
    platter.visual(
        mesh_from_cadquery(
            _soft_disc(radius, t, ch),
            "lazy_susan_marble_slab",
            tolerance=_CQ_TOL_BODY,
            angular_tolerance=_CQ_ATOL_BODY,
        ),
        origin=Origin(xyz=(0.0, 0.0, z0)),
        material=mats["platter_body"],
        name="marble_slab", material_class_id="marble.generic",
    )
    slab_top = z0 + t
    rim_w = 0.039 * radius  # S4 L28: 0.026 / 0.660
    wall_h = 0.033 * radius  # S4 L27: 0.022 / 0.660
    embed = 0.0015 * radius  # S4 L195: 0.001 / 0.660
    platter.visual(
        mesh_from_cadquery(
            _annulus(radius, radius - rim_w, wall_h + 0.006 * radius),  # S4 L64-L71
            "lazy_susan_compartment_rim",
            tolerance=_CQ_TOL_SMALL,
            angular_tolerance=_CQ_ATOL_SMALL,
        ),
        origin=Origin(xyz=(0.0, 0.0, slab_top - embed)),
        material=mats["platter_body"],
        name="compartment_rim", material_class_id="marble.generic",
    )

    inner_r = radius - rim_w
    arc = 2.0 * math.pi * inner_r / r.divider_count
    divider_w = max(0.004, min(0.030 * radius, 0.28 * arc))  # packing gate (spec §8 axis 3)
    divider_len = max(0.01, radius - rim_w - 0.027 * radius)  # S4 L75: PLATTER_RADIUS - 0.018
    divider_solid = cq.Workplane("XY").box(
        divider_len, divider_w, wall_h, centered=(False, True, False)
    )
    try:
        divider_solid = divider_solid.edges("|Z").fillet(min(0.006 * radius, 0.4 * divider_w))
    except Exception:  # pragma: no cover
        divider_solid = cq.Workplane("XY").box(
            divider_len, divider_w, wall_h, centered=(False, True, False)
        )
    divider_mesh = mesh_from_cadquery(
        divider_solid,
        "lazy_susan_compartment_divider",
        tolerance=_CQ_TOL_SMALL,
        angular_tolerance=_CQ_ATOL_SMALL,
    )
    for i in range(r.divider_count):
        platter.visual(
            divider_mesh,  # ONE mesh reused N times (spec §7.5)
            origin=Origin(
                xyz=(0.0, 0.0, slab_top - embed),
                rpy=(0.0, 0.0, 2.0 * math.pi * i / r.divider_count),
            ),
            material=mats["platter_body"],
            name=f"compartment_divider_{i}", material_class_id="marble.generic",
        )
    return _PlatterSurface(kind="round", top_z=slab_top, radius=inner_r - 0.01 * radius)


def _build_rounded_rect_tray(model, r, mats, z0: float) -> _PlatterSurface:
    """S6 model.py:L30-L61 + L114-L165 — ③ Planar Boundary Form (circle -> rounded rect).

    All dependent consumers (guard-ring inner opening, grip liner, the four
    corner posts, and ④ decoration) derive from the SAME (half_w, half_d,
    corner_r) descriptor; none re-picks a boundary.
    """
    platter = model.get_part("platter")
    radius = r.platter_radius
    half_w, half_d, corner_r = _tray_half_extents(r)
    floor_t = 0.0286 * radius  # S6 L24: 0.012 / 0.420
    rail_h = 0.143 * radius  # S6 L25: 0.060 / 0.420
    wall = 0.0476 * radius  # S6 L42: 0.020 / 0.420
    eps = 0.0048 * radius  # S6 L54/L60: 0.002 / 0.420

    floor = _rounded_box(2.0 * half_w, 2.0 * half_d, floor_t, corner_r)
    outer = _rounded_box(2.0 * half_w, 2.0 * half_d, rail_h, corner_r).translate(
        (0.0, 0.0, floor_t - eps)
    )
    inner = _rounded_box(
        2.0 * (half_w - wall),
        2.0 * (half_d - wall),
        rail_h + 2.0 * eps,
        max(0.0005, corner_r - wall),
    ).translate((0.0, 0.0, floor_t + eps))
    tray = floor.union(outer.cut(inner))
    platter.visual(
        mesh_from_cadquery(
            tray,
            "lazy_susan_organizer_tray",
            tolerance=_CQ_TOL_BODY,
            angular_tolerance=_CQ_ATOL_BODY,
        ),
        origin=Origin(xyz=(0.0, 0.0, z0)),
        material=mats["platter_body"],
        name="organizer_tray", material_class_id=("marble.generic" if r.palette_style in {"warm_marble_charcoal", "rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass", "white_marble_steel"} else "metal.paint_coated"),
    )
    liner_t = max(0.0008, 0.0036 * radius)  # S6 L140: 0.0015 / 0.420
    liner_inset = 0.062 * radius  # S6 L137: (0.052/2) / 0.420
    # The liner's top plane is stated ONCE; the returned _PlatterSurface (hence
    # all ④ decoration) reads it from here rather than re-deriving it.
    # NOTE: `_rounded_box` (like every cadquery helper here) is BOTTOM-anchored at
    # local z=0, unlike the SDK's centre-anchored `Cylinder`/`Box` primitives — so
    # the placed origin IS the underside and the top is +liner_t, not +0.5*liner_t.
    liner_bottom = z0 + floor_t - 0.3 * liner_t  # 30% sunk into the floor -> bonded
    liner_top = liner_bottom + liner_t
    platter.visual(
        mesh_from_cadquery(
            _rounded_box(
                2.0 * (half_w - liner_inset),
                2.0 * (half_d - liner_inset),
                liner_t,
                max(0.0005, corner_r - liner_inset),
            ),
            "lazy_susan_grip_liner",
            tolerance=_CQ_TOL_SMALL,
            angular_tolerance=_CQ_ATOL_SMALL,
        ),
        origin=Origin(xyz=(0.0, 0.0, liner_bottom)),
        material=mats["pad"],
        name="grip_liner", material_class_id="rubber.pebbled",
    )
    # Four corner posts DERIVED from the rectangle's four corners (not a free N).
    post_r = 0.0571 * radius  # S6 L161: 0.024 / 0.420
    post_h = rail_h + 0.0143 * radius  # S6 L161: 0.066 vs rail 0.060
    post_lo = z0 + floor_t - 0.0048 * radius
    for idx, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, 1), (1, -1))):
        platter.visual(
            Cylinder(radius=post_r, length=post_h),
            origin=Origin(
                xyz=(
                    sx * (half_w - corner_r),
                    sy * (half_d - corner_r),
                    post_lo + 0.5 * post_h,
                )
            ),
            material=mats["platter_edge"],
            name=f"corner_post_{idx}", material_class_id=("wood.walnut_dark" if r.palette_style in {"rose_marble_walnut", "walnut_brass_steel", "warm_wood_brass"} else "metal.bronze_cast"),
        )
    return _PlatterSurface(
        kind="rect",
        top_z=liner_top,
        half_w=half_w - wall,
        half_d=half_d - wall,
        corner_r=max(0.001, corner_r - wall),
    )


_PLATTER_BUILDERS = {
    "lathe_stone_slab": _build_lathe_stone_slab,
    "chamfered_stone_disk": _build_chamfered_stone_disk,
    "veneered_wood_disk": _build_veneered_wood_disk,
    "two_tier_round": _build_two_tier_round,
    "segmented_wedge": _build_segmented_wedge,
    "rounded_rect_tray": _build_rounded_rect_tray,
}


# --------------------------------------------------------------------------- #
# Slot E — surface_style (④, host-conformal, generated LAST: ③ -> ⑤ -> ④)
# --------------------------------------------------------------------------- #
def _build_surface_decoration(model, r, mats, surface: _PlatterSurface) -> None:
    platter = model.get_part("platter")
    style = r.surface_style

    if style in ("marble_veins", "tile_grout"):
        # S1 model.py:L166-L185 — asymmetric low-contrast veining, unit-disc
        # coordinates scaled by the host's per-angle extent.
        vein_specs = (
            (0.75, 0.0071, (-0.25, 0.49), -0.34),
            (0.45, 0.0052, (0.31, 0.58), 0.74),
            (0.64, 0.0062, (0.54, 0.05), 1.11),
            (0.55, 0.0050, (-0.60, -0.02), 0.43),
            (0.71, 0.0076, (0.12, -0.58), -0.72),
            (0.38, 0.0043, (-0.42, -0.58), 1.20),
            (0.48, 0.0048, (0.04, 0.18), 0.24),
        )
        for idx, (lf, wf, (ux, uy), ang) in enumerate(vein_specs):
            theta = math.atan2(uy, ux)
            reach = surface.extent_at(theta)
            _deco_line(
                platter,
                surface,
                name=f"vein_{idx:02d}",
                length=min(lf * 2.0 * reach, 1.6 * reach),
                width=max(0.0008, wf * 2.0 * reach),
                center_xy=(ux * reach * 0.88, uy * reach * 0.88),
                angle=ang,
                material=(mats["decor_mark"] if idx % 2 == 0 else mats["decor_line"]),
            )
    if style == "tile_grout":
        # S1 model.py:L139-L162 — orthogonal tile joints, clipped to the host face.
        for idx, f in enumerate((-0.32, 0.32)):
            for axis, ang in ((0, math.pi / 2.0), (1, 0.0)):
                theta = 0.0 if axis == 0 else math.pi / 2.0
                reach = surface.extent_at(theta)
                span = surface.extent_at(theta + math.pi / 2.0)
                _deco_line(
                    platter,
                    surface,
                    name=f"tile_joint_{'x' if axis == 0 else 'y'}_{idx}",
                    length=1.70 * span,
                    width=max(0.0008, 0.0029 * 2.0 * reach),
                    center_xy=((f * reach, 0.0) if axis == 0 else (0.0, f * reach)),
                    angle=ang,
                    material=mats["decor_line"],
                )
    elif style == "radial_inlay":
        # S12 model.py:L218-L233 — four radial brass inlays.
        for i in range(4):
            angle = i * math.pi / 2.0
            reach = surface.extent_at(angle)
            _deco_line(
                platter,
                surface,
                name=f"radial_inlay_{i}",
                length=0.62 * reach,
                width=max(0.0008, 0.0071 * reach),
                center_xy=(0.48 * reach * math.cos(angle), 0.48 * reach * math.sin(angle)),
                angle=angle,
                material=mats["decor_line"],
            )
    elif style == "veneer_seams":
        # S13 model.py:L152-L162 — eight radial veneer seams.
        for i in range(8):
            angle = i * math.pi / 4.0
            reach = surface.extent_at(angle)
            _deco_line(
                platter,
                surface,
                name=f"veneer_seam_{i}",
                length=0.85 * reach,
                width=max(0.0008, 0.0040 * reach),
                center_xy=(0.48 * reach * math.cos(angle), 0.48 * reach * math.sin(angle)),
                angle=angle,
                material=mats["decor_line"],
            )

    # ALWAYS: the asymmetric maker medallion. It is both a real source detail
    # (S8 L138-L143 / S13 L166-L171 / S12 L228-L233 `maker_badge`) and the ONLY
    # visible feature that can prove rotation on an axisymmetric platter.
    mark_reach = surface.extent_at(0.0)
    mark_r = max(0.004, 0.037 * mark_reach + 0.0035)
    mark_x = 0.72 * mark_reach
    # Walk it in until the whole disc sits on the host face (exact for the
    # rounded-rect boundary too), so the mark is never a floating island.
    for _ in range(24):
        if surface.contains(mark_x, 0.0, mark_r):
            break
        mark_x *= 0.90
    platter.visual(
        Cylinder(radius=mark_r, length=0.0015),
        # 0.0004 of the 0.0015 disc is sunk into the host -> bonded and proud.
        origin=Origin(xyz=(mark_x, 0.0, surface.top_z + 0.00035)),
        material=mats["decor_mark"],
        name="orientation_mark", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )


# --------------------------------------------------------------------------- #
# Builder
# --------------------------------------------------------------------------- #
def build_picturex_0611_lazy_susan(
    config: PictureX0611LazySusanConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or PictureX0611LazySusanConfig())
    model = ArticulatedObject(name=r.name, assets=assets)

    palette = PALETTES[r.palette_style]
    mats = {k: model.material(f"{r.palette_style}_{k}", rgba=v) for k, v in palette.items()}

    base = _BASE_BUILDERS[r.base_form](model, r, mats)
    bearing = _build_bearing_static(model, r, mats, base)

    model.part("platter")
    rotor = _build_bearing_rotor(model, r, mats)
    surface = _PLATTER_BUILDERS[r.platter_form](model, r, mats, rotor.top_z)
    _build_surface_decoration(model, r, mats, surface)

    platter = model.get_part("platter")
    platter.inertial = Inertial.from_geometry(
        Cylinder(radius=r.platter_radius, length=max(0.01, surface.top_z)),
        mass=3.0 + 14.0 * r.platter_radius,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * surface.top_z)),
    )

    if r.spin_joint == "revolute_bounded":
        spin_type = ArticulationType.REVOLUTE
        spin_limits = MotionLimits(effort=12.0, velocity=2.4, lower=-math.pi, upper=math.pi)
    else:
        spin_type = ArticulationType.CONTINUOUS
        spin_limits = MotionLimits(effort=12.0, velocity=2.4)

    spin_origin = (base.deck_cx, base.deck_cy, bearing.top_z)
    model.articulation(
        "spin",
        spin_type,
        parent=model.get_part(base.deck_part_name),
        child=platter,
        origin=Origin(xyz=spin_origin),
        axis=(0.0, 0.0, 1.0),
        motion_limits=spin_limits,
        motion_properties=MotionProperties(damping=0.08, friction=0.03),
        mating=MatingContract(
            parent_face_geometry=bearing.land_visual,
            parent_face_side="positive_z",
            child_face_geometry=rotor.mating_visual,
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
        meta=_joint_meta(spin_type, (0.0, 0.0, 1.0), spin_origin, spin_limits),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["joint_index"] = {"spin": "spin", "base_chain": list(base.joints)}
    return model


def build_seeded_picturex_0611_lazy_susan(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_lazy_susan(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests (Rule 5)
# --------------------------------------------------------------------------- #
def _mark_center_xy(ctx, part):
    box = ctx.part_element_world_aabb(part, elem="orientation_mark")
    if box is None:
        return None
    return ((box[0][0] + box[1][0]) * 0.5, (box[0][1] + box[1][1]) * 0.5)


def _mark_center_z(ctx, part):
    box = ctx.part_element_world_aabb(part, elem="orientation_mark")
    if box is None:
        return None
    return (box[0][2] + box[1][2]) * 0.5


def run_picturex_0611_lazy_susan_tests(
    object_model: ArticulatedObject,
    config: PictureX0611LazySusanConfig,
) -> TestReport:
    r = resolve_config(config)  # validates enums / re-derives the domain
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joints = {j.name: j for j in object_model.articulations}

    ctx.check("platter part present", "platter" in part_names, details=str(sorted(part_names)))
    ctx.check("spin joint present", "spin" in joints, details=str(sorted(joints)))

    # Category identity: the turntable axis is vertical, on the symmetry line.
    spin = joints["spin"]
    ctx.check(
        "spin is a vertical-axis turntable joint",
        tuple(round(a, 6) for a in spin.axis) == (0.0, 0.0, 1.0)
        and spin.articulation_type in (ArticulationType.REVOLUTE, ArticulationType.CONTINUOUS),
        details=f"type={spin.articulation_type}, axis={spin.axis}",
    )
    if r.spin_joint == "revolute_bounded":
        lim = spin.motion_limits
        ctx.check(
            "bounded turntable covers a full revolution",
            lim is not None
            and lim.lower is not None
            and lim.upper is not None
            and lim.lower <= -math.pi + 1e-6
            and lim.upper >= math.pi - 1e-6,
            details=f"limits={lim}",
        )
    else:
        ctx.check(
            "free turntable is CONTINUOUS",
            spin.articulation_type == ArticulationType.CONTINUOUS,
            details=f"type={spin.articulation_type}",
        )

    for j in object_model.articulations:
        ctx.check(
            f"joint {j.name} metadata complete",
            {"type", "axis", "origin", "range"} <= set(j.meta),
            details=str(sorted(j.meta)),
        )

    choices = dict(object_model.meta.get("slot_choices", ()))
    for key in (
        "base_form",
        "bearing_style",
        "platter_form",
        "spin_joint",
        "surface_style",
        "palette_style",
    ):
        ctx.check(f"slot {key} recorded", key in choices, details=str(choices))

    platter = object_model.get_part("platter")
    platter_visuals = {v.name for v in platter.visuals}
    ctx.check(
        "platter carries an asymmetric orientation mark",
        "orientation_mark" in platter_visuals,
        details=str(sorted(platter_visuals)),
    )

    # Category identity: the platter must cover the bearing hardware it rides on.
    ctx.check(
        "platter covers its bearing envelope",
        _bearing_outer_radius(r) + 0.010 <= _platter_cover_radius(r) + 1e-9,
        details=(
            f"bearing_outer={_bearing_outer_radius(r):.4f}, cover={_platter_cover_radius(r):.4f}"
        ),
    )

    # ── Rule 5: targeted motion semantics ────────────────────────────────────
    # NOTE: the platter's part frame origin sits ON the spin axis, so
    # part_world_position is invariant under this joint BY CONSTRUCTION. Rotation
    # is asserted on a real off-axis ELEMENT's AABB centre instead.
    rest_xy = _mark_center_xy(ctx, platter)
    rest_z = _mark_center_z(ctx, platter)
    with ctx.pose({"spin": math.pi / 2.0}):
        quarter_xy = _mark_center_xy(ctx, platter)
        quarter_z = _mark_center_z(ctx, platter)
    ctx.check(
        "quarter turn swings the platter's mark about the vertical axis",
        rest_xy is not None
        and quarter_xy is not None
        and math.dist(rest_xy, quarter_xy) > 0.25 * r.platter_radius
        and rest_z is not None
        and quarter_z is not None
        and abs(rest_z - quarter_z) < 1e-4,
        details=f"rest={rest_xy}, quarter={quarter_xy}, rest_z={rest_z}, quarter_z={quarter_z}",
    )
    if r.spin_joint == "continuous_free":
        # A continuous joint must stay legible over the FULL cycle.
        with ctx.pose({"spin": math.pi}):
            half_xy = _mark_center_xy(ctx, platter)
        with ctx.pose({"spin": 1.5 * math.pi}):
            three_q_xy = _mark_center_xy(ctx, platter)
        ctx.check(
            "continuous turntable stays legible over the full cycle",
            rest_xy is not None
            and half_xy is not None
            and three_q_xy is not None
            and math.dist(rest_xy, half_xy) > 0.5 * r.platter_radius
            and math.dist(rest_xy, three_q_xy) > 0.25 * r.platter_radius,
            details=f"rest={rest_xy}, half={half_xy}, three_quarter={three_q_xy}",
        )

    if r.base_form == "cabinet_pullout":
        carriage = object_model.get_part("carriage")
        pull = joints["mount_to_carriage"]
        # PRISMATIC: part_world_position IS the right probe (the frame translates).
        rest_pos = ctx.part_world_position(carriage)
        with ctx.pose({"mount_to_carriage": pull.motion_limits.upper}):
            out_pos = ctx.part_world_position(carriage)
        ctx.check(
            "carriage pulls out along +x",
            rest_pos is not None
            and out_pos is not None
            and out_pos[0] > rest_pos[0] + 0.9 * _pull_travel(r)
            and abs(out_pos[1] - rest_pos[1]) < 1e-6,
            details=f"rest={rest_pos}, extended={out_pos}",
        )
        swing = joints["carriage_to_swivel_arm"]
        with ctx.pose(
            {"mount_to_carriage": pull.motion_limits.upper, "carriage_to_swivel_arm": 0.0}
        ):
            straight = _mark_center_xy(ctx, platter)
        with ctx.pose(
            {
                "mount_to_carriage": pull.motion_limits.upper,
                "carriage_to_swivel_arm": swing.motion_limits.upper,
            }
        ):
            swung = _mark_center_xy(ctx, platter)
        ctx.check(
            "pulled-out tray swings around the offset carriage pivot",
            straight is not None
            and swung is not None
            and math.dist(straight, swung) > 0.2 * _swing_offset(r),
            details=f"straight={straight}, swung={swung}",
        )

    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    # No allowances anywhere: every rotor mates by exact contact on its bearing
    # land (flat land, or the ball crowns for exposed_ball_ring), and the only
    # captured pair (center_axle in rotor_hub's bore) keeps a real
    # _AXLE_BORE_CLEARANCE radial gap, so there is no interference to waive.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    return ctx.report()


__all__ = [
    "PictureX0611LazySusanConfig",
    "ResolvedPictureX0611LazySusanConfig",
    "build_picturex_0611_lazy_susan",
    "build_seeded_picturex_0611_lazy_susan",
    "config_from_seed",
    "resolve_config",
    "run_picturex_0611_lazy_susan_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
