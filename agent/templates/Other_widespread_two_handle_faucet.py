# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for ``widespread_two_handle_faucet``.

Follows ``articraft_template_authoring/specs_modular_v1/Other_Other_widespread_two_handle_faucet.md``.

A widespread / 8-inch three-piece deck-mounted two-handle bathroom faucet: a deck
slab root carrying THREE independent columns — a central spout column plus a
mirrored pair of valve columns (hot left / cold right) spaced ``2*spread_half``
apart. World frame:

- +Z is up; the deck slab rests on z = 0 (top face at z = DECK_T).
- +Y is the spout reach direction (spout overhangs the front edge).
- Symmetry plane is YZ (x = 0): the center spout is on-axis, hot/cold mirror.

Structure (pattern = mixed: parallel children + fixed ×2 valve multiplicity):

    deck (root)
      ├─[FIXED]──> center_column ──[Slot B joint]──> center_spout (+ optional finial)
      ├─[FIXED]──> hot_valve_column  ──[REVOLUTE z]──> hot_handle
      └─[FIXED]──> cold_valve_column ──[REVOLUTE z]──> cold_handle

Three STRUCTURAL slots (these are what ``module_topology_diversity`` counts):

    deck_column_family (A) — cylindrical_flange / tapered_pyramid
    center_spout       (B) — gooseneck_swivel / waterfall_diverter /
                             gooseneck_diverter / gooseneck_pulldown_tilt
    valve_handle       (C) — t_lever / cross_spoke  (mirrored to both stations)

FIVE appearance sub-axes (parent.visual / static decoration ONLY — they add NO
joint and are NOT part of slot_choices, so they do not inflate topology
diversity; they exist purely to make every seed look different):

    AX-1 section_profile      — round / square / hexagonal column+riser section
    AX-2 cross_spoke_form     — 4 / 5 / 6 spoke or spoked_rim (cross handles)
    AX-3 lever_blade_form     — round_rod / flat_strip / tapered_leaf (t_lever)
    AX-4 escutcheon_ring      — none / decorative torus base ring (×3 columns)
    AX-5 collar_ring          — none / spout-root collar (gooseneck family)

plus continuous scales (spread, column radius/taper/height, spout reach / arc
curvature / outlet height, handle span / bar thickness, escutcheon / collar).

Adopted sources (spec Source Index):
M_BLK matte-black widespread (round flange column + swept gooseneck swivel +
      offset T-lever) — cylindrical_flange / gooseneck_swivel / t_lever baseline.
M_CHR polished-chrome Art-Deco (square-pyramid column + waterfall slab spout +
      oval diverter finial + 4-spoke cross handle) — tapered_pyramid /
      waterfall_diverter / cross_spoke baseline.
C_006v01 gooseneck spout body FIXED + top diverter finial — gooseneck_diverter.
C_001v20 pull-down gooseneck on a horizontal hinge — gooseneck_pulldown_tilt.
C_001v05 .polygon(6) hexagonal column section — AX-1 hexagonal.
C_003v04 TorusGeometry base/seam ring — AX-4 escutcheon ring.
C_001v22 Box flat-strip lever blade — AX-3 flat_strip.
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #

DeckColumnFamily = Literal["cylindrical_flange", "tapered_pyramid"]
CenterSpout = Literal[
    "gooseneck_swivel",
    "waterfall_diverter",
    "gooseneck_diverter",
    "gooseneck_pulldown_tilt",
]
ValveHandle = Literal["t_lever", "cross_spoke"]
PaletteStyle = Literal[
    "polished_chrome",
    "matte_black",
    "polished_gold_brass",
    "brushed_nickel",
    "oil_rubbed_bronze",
]
# Appearance sub-axes (NOT counted in slot_choices / topology diversity).
SectionProfile = Literal["round", "square", "hexagonal"]
CrossSpokeForm = Literal["4_spoke", "5_spoke", "6_spoke", "spoked_rim"]
LeverBladeForm = Literal["round_rod", "flat_strip", "tapered_leaf"]
EscutcheonRing = Literal["none", "ring"]
CollarRing = Literal["none", "collar"]

DECK_COLUMN_FAMILIES: tuple[DeckColumnFamily, ...] = (
    "cylindrical_flange",
    "tapered_pyramid",
)
CENTER_SPOUTS: tuple[CenterSpout, ...] = (
    "gooseneck_swivel",
    "waterfall_diverter",
    "gooseneck_diverter",
    "gooseneck_pulldown_tilt",
)
VALVE_HANDLES: tuple[ValveHandle, ...] = ("t_lever", "cross_spoke")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "polished_chrome",
    "matte_black",
    "polished_gold_brass",
    "brushed_nickel",
    "oil_rubbed_bronze",
)
SECTION_PROFILES: tuple[SectionProfile, ...] = ("round", "square", "hexagonal")
CROSS_SPOKE_FORMS: tuple[CrossSpokeForm, ...] = (
    "4_spoke",
    "5_spoke",
    "6_spoke",
    "spoked_rim",
)
LEVER_BLADE_FORMS: tuple[LeverBladeForm, ...] = (
    "round_rod",
    "flat_strip",
    "tapered_leaf",
)

# Sampling weights — near-uniform on the structural axes so the 16-combo pool is
# covered within 0-49; pulldown_tilt is the long-tail spout (low weight).
_FAMILY_WEIGHTS = (0.50, 0.50)
_SPOUT_WEIGHTS = (0.34, 0.26, 0.25, 0.15)
_HANDLE_WEIGHTS = (0.50, 0.50)

# --------------------------------------------------------------------------- #
# Palettes (metal body + deck slab; hot/cold indicator accents shared).
# --------------------------------------------------------------------------- #

HOT_RED = (0.78, 0.08, 0.08, 1.0)
COLD_BLUE = (0.10, 0.25, 0.82, 1.0)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "polished_chrome": {
        "metal": (0.88, 0.89, 0.92, 1.0),
        "deck": (0.09, 0.09, 0.10, 1.0),
        "hot": HOT_RED,
        "cold": COLD_BLUE,
    },
    "matte_black": {
        "metal": (0.07, 0.07, 0.07, 1.0),
        "deck": (0.80, 0.79, 0.76, 1.0),
        "hot": HOT_RED,
        "cold": COLD_BLUE,
    },
    "polished_gold_brass": {
        "metal": (0.85, 0.66, 0.20, 1.0),
        "deck": (0.16, 0.15, 0.15, 1.0),
        "hot": HOT_RED,
        "cold": COLD_BLUE,
    },
    "brushed_nickel": {
        "metal": (0.66, 0.67, 0.68, 1.0),
        "deck": (0.78, 0.77, 0.74, 1.0),
        "hot": HOT_RED,
        "cold": COLD_BLUE,
    },
    "oil_rubbed_bronze": {
        "metal": (0.20, 0.13, 0.09, 1.0),
        "deck": (0.74, 0.73, 0.70, 1.0),
        "hot": HOT_RED,
        "cold": COLD_BLUE,
    },
}

# --------------------------------------------------------------------------- #
# Base real-world dimensions (meters), pre-scale.
# --------------------------------------------------------------------------- #

DECK_T = 0.020  # deck slab thickness (top face at z = DECK_T)
DECK_DEPTH = 0.160  # deck slab depth (Y)
DECK_MARGIN_X = 0.055  # deck overhang past the outermost column (X)

FL_H = 0.007  # column flange height
CENTER_FLANGE_R = 0.024
CENTER_BODY_R = 0.018  # center column base section radius (×column_radius_scale)
CENTER_BODY_H = 0.075  # center column body height (×center_col_height_scale)
VALVE_FLANGE_R = 0.020
VALVE_BODY_H = 0.055  # valve column body height (×valve_col_height_scale)
VALVE_RADIUS_RATIO = 0.90  # valve body radius = center body radius × ratio

BONNET_R = 0.0075  # captured bonnet stem (handle/spout/finial grip it)
BONNET_H = 0.013

# Spout (gooseneck family), authored in the spout part frame (origin = col top).
RISER_H = 0.050  # straight riser height before the bend (×spout_outlet_height_scale)
SPOUT_REACH = 0.105  # forward reach in +Y (×spout_reach_scale)
ARC_HEIGHT = 0.050  # bend apex rise (×spout_arc_curvature_scale)
TUBE_R = 0.011
AERATOR_R = 0.012
AERATOR_LEN = 0.016
COLLAR_R = 0.016  # AX-5 root collar (×collar_size_scale)
COLLAR_H = 0.009

# Waterfall slab spout.
WF_NECK_H = 0.026
WF_SLAB_W = 0.060  # width in X
WF_SLAB_TH = 0.012
WF_LIP_DROP = 0.018

# Diverter finial.
FIN_SEAT_R = 0.012
FIN_SEAT_H = 0.004
FIN_STEM_R = 0.006
FIN_STEM_H = 0.012
FIN_OVAL_R = 0.010
FIN_TAB_LEN = 0.014  # off-axis pointer so the spin is observable

# Handles, authored in the handle part frame (origin = valve column top).
HANDLE_SPAN = 0.090  # tip-to-tip span (×handle_span_scale)
BAR_R = 0.006  # T-bar rod / spoke radius (×handle_bar_thickness_scale)
HUB_R = 0.013
HUB_H = 0.018
STEM_R = 0.011  # t_lever stem (captures the bonnet)
STEM_H = 0.022

# Joint ranges.
SWIVEL_LIMIT = math.pi / 4.0
DIVERTER_LIMIT = math.pi / 2.0
TILT_LOWER = -0.60
TILT_UPPER = 0.35
LEVER_LIMIT = math.pi / 2.0
CROSS_LIMIT = math.pi

HANDLE_CLEARANCE = 0.012


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class WidespreadTwoHandleFaucetConfig:
    deck_column_family: DeckColumnFamily = "cylindrical_flange"
    center_spout: CenterSpout = "gooseneck_swivel"
    valve_handle: ValveHandle = "t_lever"
    palette_style: PaletteStyle = "polished_chrome"
    # appearance sub-axes
    section_profile: SectionProfile = "round"
    cross_spoke_form: CrossSpokeForm = "4_spoke"
    lever_blade_form: LeverBladeForm = "round_rod"
    escutcheon_ring: EscutcheonRing = "none"
    collar_ring: CollarRing = "none"
    # continuous
    spread_half: float = 0.15
    center_col_height_scale: float = 1.0
    valve_col_height_scale: float = 1.0
    column_radius_scale: float = 1.0
    column_taper_ratio: float = 0.75
    spout_reach_scale: float = 1.0
    spout_arc_curvature_scale: float = 1.0
    spout_outlet_height_scale: float = 1.0
    handle_span_scale: float = 1.0
    handle_bar_thickness_scale: float = 1.0
    escutcheon_diameter_scale: float = 1.0
    escutcheon_thickness_scale: float = 1.0
    collar_size_scale: float = 1.0
    name: str = "reference_widespread_two_handle_faucet"


@dataclass(frozen=True)
class ResolvedConfig:
    deck_column_family: DeckColumnFamily
    center_spout: CenterSpout
    valve_handle: ValveHandle
    palette_style: PaletteStyle
    section: SectionProfile
    cross_spoke_form: CrossSpokeForm
    lever_blade_form: LeverBladeForm
    escutcheon_ring: EscutcheonRing
    collar_ring: CollarRing
    name: str
    palette: dict[str, tuple[float, float, float, float]]
    # geometry (resolved, scaled)
    spread_half: float
    deck_width: float
    center_flange_r: float
    valve_flange_r: float
    center_body_botr: float
    valve_body_botr: float
    center_body_h: float
    valve_body_h: float
    taper: float
    riser_h: float
    reach: float
    arc_h: float
    collar_r: float
    collar_h: float
    handle_span: float
    bar_r: float
    esc_major_center: float
    esc_major_valve: float
    esc_h: float

    @property
    def center_top_r(self) -> float:
        return self.center_body_botr * self.taper

    @property
    def valve_top_r(self) -> float:
        return self.valve_body_botr * self.taper

    @property
    def center_col_top(self) -> float:
        return FL_H + self.center_body_h

    @property
    def valve_col_top(self) -> float:
        return FL_H + self.valve_body_h


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


# --------------------------------------------------------------------------- #
# Sampling
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> WidespreadTwoHandleFaucetConfig:
    """Deterministic per-seed sampling. ``seed=0`` is not special.

    Three structural enums (near-uniform), a colorway, the five appearance
    sub-axes (each an independent weighted draw — these do NOT enter
    slot_choices), and the continuous scales are all sampled here. The
    cross-part inequalities are projected back in ``resolve_config``.
    """
    rng = random.Random(seed)

    family = rng.choices(DECK_COLUMN_FAMILIES, weights=_FAMILY_WEIGHTS, k=1)[0]
    spout = rng.choices(CENTER_SPOUTS, weights=_SPOUT_WEIGHTS, k=1)[0]
    handle = rng.choices(VALVE_HANDLES, weights=_HANDLE_WEIGHTS, k=1)[0]
    palette = rng.choice(PALETTE_STYLES)

    # AX-1 section: bias toward each family's native section but allow any.
    if family == "cylindrical_flange":
        section = rng.choices(SECTION_PROFILES, weights=(0.55, 0.15, 0.30), k=1)[0]
    else:
        section = rng.choices(SECTION_PROFILES, weights=(0.15, 0.55, 0.30), k=1)[0]
    cross_form = rng.choices(CROSS_SPOKE_FORMS, weights=(0.40, 0.25, 0.20, 0.15), k=1)[0]
    lever_form = rng.choice(LEVER_BLADE_FORMS)
    escutcheon = rng.choices(("none", "ring"), weights=(0.5, 0.5), k=1)[0]
    collar = rng.choices(("none", "collar"), weights=(0.45, 0.55), k=1)[0]

    return WidespreadTwoHandleFaucetConfig(
        deck_column_family=family,
        center_spout=spout,
        valve_handle=handle,
        palette_style=palette,
        section_profile=section,
        cross_spoke_form=cross_form,
        lever_blade_form=lever_form,
        escutcheon_ring=escutcheon,
        collar_ring=collar,
        spread_half=round(rng.uniform(0.10, 0.19), 4),
        center_col_height_scale=round(rng.uniform(0.80, 1.35), 4),
        valve_col_height_scale=round(rng.uniform(0.80, 1.25), 4),
        column_radius_scale=round(rng.uniform(0.80, 1.45), 4),
        column_taper_ratio=round(rng.uniform(0.55, 0.95), 4),
        spout_reach_scale=round(rng.uniform(0.80, 1.45), 4),
        spout_arc_curvature_scale=round(rng.uniform(0.80, 1.30), 4),
        spout_outlet_height_scale=round(rng.uniform(0.85, 1.25), 4),
        handle_span_scale=round(rng.uniform(0.80, 1.30), 4),
        handle_bar_thickness_scale=round(rng.uniform(0.75, 1.40), 4),
        escutcheon_diameter_scale=round(rng.uniform(0.90, 1.50), 4),
        escutcheon_thickness_scale=round(rng.uniform(0.70, 1.60), 4),
        collar_size_scale=round(rng.uniform(0.80, 1.40), 4),
        name=f"seeded_widespread_two_handle_faucet_{seed}",
    )


def resolve_config(
    config: WidespreadTwoHandleFaucetConfig | None = None,
) -> ResolvedConfig:
    cfg = config or WidespreadTwoHandleFaucetConfig()
    if cfg.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {cfg.palette_style}")

    family = _pick(cfg.deck_column_family, DECK_COLUMN_FAMILIES)
    spout = _pick(cfg.center_spout, CENTER_SPOUTS)
    handle = _pick(cfg.valve_handle, VALVE_HANDLES)
    section = _pick(cfg.section_profile, SECTION_PROFILES)
    cross_form = _pick(cfg.cross_spoke_form, CROSS_SPOKE_FORMS)
    lever_form = _pick(cfg.lever_blade_form, LEVER_BLADE_FORMS)
    escutcheon = _pick(cfg.escutcheon_ring, ("none", "ring"))
    collar = _pick(cfg.collar_ring, ("none", "collar"))

    # AX-5: waterfall slab has no riser root, so a collar is impossible there.
    if spout == "waterfall_diverter":
        collar = "none"

    radius_scale = _clamp(cfg.column_radius_scale, 0.80, 1.45)
    center_body_botr = CENTER_BODY_R * radius_scale
    valve_body_botr = center_body_botr * VALVE_RADIUS_RATIO
    center_flange_r = max(CENTER_FLANGE_R * radius_scale, center_body_botr + 0.004)
    valve_flange_r = max(VALVE_FLANGE_R * radius_scale, valve_body_botr + 0.004)

    center_body_h = CENTER_BODY_H * _clamp(cfg.center_col_height_scale, 0.80, 1.35)
    valve_body_h = VALVE_BODY_H * _clamp(cfg.valve_col_height_scale, 0.80, 1.25)

    # Taper: the column top section must still contain the captured bonnet bore.
    # For hexagonal the binding dimension is the inscribed (flat-to-flat) radius
    # = top_r * cos(30deg).  Worst case is the smaller valve column.
    taper = _clamp(cfg.column_taper_ratio, 0.55, 0.95)
    sec_factor = math.cos(math.pi / 6.0) if section == "hexagonal" else 1.0
    mount_min = (BONNET_R + 0.0015) / sec_factor
    taper_min = mount_min / valve_body_botr
    taper = _clamp(max(taper, taper_min), 0.55, 0.95)

    # Spread: hot/cold handles + columns must not collide with each other or the
    # center spout.  spread_half >= valve_radius + half handle span + clearance.
    spread_half = _clamp(cfg.spread_half, 0.10, 0.19)
    handle_span = HANDLE_SPAN * _clamp(cfg.handle_span_scale, 0.80, 1.30)
    bar_r = BAR_R * _clamp(cfg.handle_bar_thickness_scale, 0.75, 1.40)
    # The handle's inboard tip (cross spoke reaches span/2 inward) must clear the
    # CENTER column/spout radius, which is the largest obstruction toward x=0.
    min_spread = center_body_botr + 0.5 * handle_span + HANDLE_CLEARANCE
    if spread_half < min_spread:
        # First trim the handle span, then if still short widen the spread.
        handle_span = max(0.060, 2.0 * (spread_half - center_body_botr - HANDLE_CLEARANCE))
        min_spread = center_body_botr + 0.5 * handle_span + HANDLE_CLEARANCE
        if spread_half < min_spread:
            spread_half = min_spread
    spread_half = _clamp(spread_half, 0.10, 0.22)

    deck_width = 2.0 * spread_half + 2.0 * DECK_MARGIN_X

    # Spout reach must not overhang the deck front past a sane margin.
    reach = SPOUT_REACH * _clamp(cfg.spout_reach_scale, 0.80, 1.45)
    reach = min(reach, DECK_DEPTH / 2.0 + 0.070)
    arc_h = ARC_HEIGHT * _clamp(cfg.spout_arc_curvature_scale, 0.80, 1.30)
    riser_h = RISER_H * _clamp(cfg.spout_outlet_height_scale, 0.85, 1.25)

    collar_r = max(COLLAR_R * _clamp(cfg.collar_size_scale, 0.80, 1.40), TUBE_R + 0.003)
    collar_h = COLLAR_H * _clamp(cfg.collar_size_scale, 0.80, 1.40)

    # AX-4 escutcheon: a flat trim disc at the column base (wider than the
    # flange so it reads as a decorative base ring). Adjacent center/valve discs
    # must not overlap; cap each at ~45% of the spread. It always surrounds and
    # overlaps its own flange (no floating island) and sits just above the deck.
    esc_diam_scale = _clamp(cfg.escutcheon_diameter_scale, 0.90, 1.50)
    esc_major_center = max(center_flange_r * esc_diam_scale, center_flange_r + 0.002)
    esc_major_valve = max(valve_flange_r * esc_diam_scale, valve_flange_r + 0.002)
    max_major = max(center_flange_r + 0.002, 0.45 * spread_half)
    esc_major_center = min(esc_major_center, max_major)
    esc_major_valve = min(esc_major_valve, max_major)
    esc_h = 0.004 * _clamp(cfg.escutcheon_thickness_scale, 0.70, 1.60)

    return ResolvedConfig(
        deck_column_family=family,
        center_spout=spout,
        valve_handle=handle,
        palette_style=cfg.palette_style,
        section=section,
        cross_spoke_form=cross_form,
        lever_blade_form=lever_form,
        escutcheon_ring=escutcheon,
        collar_ring=collar,
        name=cfg.name or "widespread_two_handle_faucet",
        palette=dict(PALETTES[cfg.palette_style]),
        spread_half=spread_half,
        deck_width=deck_width,
        center_flange_r=center_flange_r,
        valve_flange_r=valve_flange_r,
        center_body_botr=center_body_botr,
        valve_body_botr=valve_body_botr,
        center_body_h=center_body_h,
        valve_body_h=valve_body_h,
        taper=taper,
        riser_h=riser_h,
        reach=reach,
        arc_h=arc_h,
        collar_r=collar_r,
        collar_h=collar_h,
        handle_span=handle_span,
        bar_r=bar_r,
        esc_major_center=esc_major_center,
        esc_major_valve=esc_major_valve,
        esc_h=esc_h,
    )


# --------------------------------------------------------------------------- #
# slot choices (structural only — appearance axes are deliberately excluded so
# they do not inflate module_topology_diversity).
# --------------------------------------------------------------------------- #


def slot_choices_for_config(r: ResolvedConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("deck_column_family", r.deck_column_family),
        ("center_spout", r.center_spout),
        ("valve_handle", r.valve_handle),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #


def _section_solid(section: SectionProfile, r_bot: float, r_top: float, h: float, name, assets, *, z0: float):
    """A frustum solid (round / square / hexagonal section), base at z0.

    AX-1 only swaps the extrusion section primitive; the flange/joint geometry
    is untouched. (round = circle loft, square = rect loft, hexagonal =
    .polygon(6) loft — the C_001v05 hexagonal column source.)
    """
    wp = cq.Workplane("XY", origin=(0.0, 0.0, z0))
    if section == "square":
        solid = (
            wp.rect(2.0 * r_bot, 2.0 * r_bot)
            .workplane(offset=h)
            .rect(2.0 * r_top, 2.0 * r_top)
            .loft(combine=True)
        )
    elif section == "hexagonal":
        solid = (
            wp.polygon(6, 2.0 * r_bot)
            .workplane(offset=h)
            .polygon(6, 2.0 * r_top)
            .loft(combine=True)
        )
    else:  # round
        solid = wp.circle(r_bot).workplane(offset=h).circle(r_top).loft(combine=True)
    return mesh_from_cadquery(solid, name, assets=assets)


def _circle_profile(radius: float, n: int = 16) -> list[tuple[float, float]]:
    return [
        (radius * math.cos(2.0 * math.pi * k / n), radius * math.sin(2.0 * math.pi * k / n))
        for k in range(n)
    ]


def _gooseneck_path(riser_h: float, reach: float, arc_h: float, n_arc: int = 22):
    """Riser (z) then an elliptical bend reaching +Y, ending pointing down.

    Outlet at (0, reach, riser_h); curvature (arc_h) decoupled from reach.
    """
    pts: list[tuple[float, float, float]] = []
    for i in range(5):
        pts.append((0.0, 0.0, riser_h * i / 4.0))
    a = reach / 2.0
    for i in range(1, n_arc + 1):
        ph = math.pi * i / n_arc
        y = a * (1.0 - math.cos(ph))
        z = riser_h + arc_h * math.sin(ph)
        pts.append((0.0, y, z))
    return pts


def _unit(v):
    n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if n < 1e-9:
        return (0.0, 0.0, 1.0)
    return (v[0] / n, v[1] / n, v[2] / n)


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _hollow_pipe_mesh(points, outer_r, inner_r, segments=16):
    """Thin-wall hollow swept tube (outer + inner wall + annular end rings).

    The central bore is an open tunnel end-to-end: the base end is buried in the
    riser stub + column (bore hidden there) and the outlet end shows a real open
    mouth, so the spout reads as a water pipe rather than a solid rod. Winding
    mirrors the proven gooseneck ``_variable_tube``.
    """
    inner_r = max(min(inner_r, outer_r - 1e-4), 1e-4)
    verts: list = []
    faces: list = []
    rings: list = []
    n = len(points)
    for i, p in enumerate(points):
        if i == 0:
            tan = (points[1][0] - p[0], points[1][1] - p[1], points[1][2] - p[2])
        elif i == n - 1:
            tan = (p[0] - points[i - 1][0], p[1] - points[i - 1][1], p[2] - points[i - 1][2])
        else:
            tan = (
                points[i + 1][0] - points[i - 1][0],
                points[i + 1][1] - points[i - 1][1],
                points[i + 1][2] - points[i - 1][2],
            )
        tan = _unit(tan)
        u = (1.0, 0.0, 0.0)
        if abs(tan[0]) > 0.92:
            u = (0.0, 1.0, 0.0)
        v = _unit(_cross(tan, u))
        u = _unit(_cross(v, tan))
        outer: list = []
        inner: list = []
        for k in range(segments):
            a = 2.0 * math.pi * k / segments
            ca, sa = math.cos(a), math.sin(a)
            dx = u[0] * ca + v[0] * sa
            dy = u[1] * ca + v[1] * sa
            dz = u[2] * ca + v[2] * sa
            outer.append(len(verts))
            verts.append((p[0] + outer_r * dx, p[1] + outer_r * dy, p[2] + outer_r * dz))
            inner.append(len(verts))
            verts.append((p[0] + inner_r * dx, p[1] + inner_r * dy, p[2] + inner_r * dz))
        rings.append((outer, inner))
    for i in range(n - 1):
        o0, i0 = rings[i]
        o1, i1 = rings[i + 1]
        for k in range(segments):
            j = (k + 1) % segments
            faces.append((o0[k], o1[k], o1[j]))
            faces.append((o0[k], o1[j], o0[j]))
            faces.append((i0[k], i1[j], i1[k]))
            faces.append((i0[k], i0[j], i1[j]))
    for ri in (0, n - 1):
        outer, inner = rings[ri]
        for k in range(segments):
            j = (k + 1) % segments
            if ri == 0:
                faces.append((outer[k], inner[j], inner[k]))
                faces.append((outer[k], outer[j], inner[j]))
            else:
                faces.append((outer[k], inner[k], inner[j]))
                faces.append((outer[k], inner[j], outer[j]))
    return MeshGeometry(vertices=verts, faces=faces)


def _gooseneck_mesh(name: str, r: ResolvedConfig, assets):
    path = _gooseneck_path(r.riser_h, r.reach, r.arc_h)
    # hollow thin-wall pipe (~1.8 mm wall) with an open outlet bore
    geom = _hollow_pipe_mesh(path, TUBE_R, TUBE_R - 0.0018)
    return mesh_from_geometry(geom, name)


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict:
    out = {}
    for key, rgba in r.palette.items():
        out[key] = model.material(f"faucet_{key}_{r.palette_style}", rgba=rgba)
    return out


# --------------------------------------------------------------------------- #
# Deck root
# --------------------------------------------------------------------------- #


def _build_deck(model: ArticulatedObject, r: ResolvedConfig, mats: dict):
    deck = model.part("deck")
    deck.visual(
        Box((r.deck_width, DECK_DEPTH, DECK_T)),
        origin=Origin(xyz=(0.0, 0.0, DECK_T / 2.0)),
        material=mats["deck"],
        name="deck_slab", material_class_id="stone.polished_granite",
    )
    return deck


# --------------------------------------------------------------------------- #
# Column factory (Slot A + AX-1 section + AX-4 escutcheon ring)
# --------------------------------------------------------------------------- #


def _build_column(
    model: ArticulatedObject,
    deck,
    part_name: str,
    vp: str,
    world_x: float,
    r: ResolvedConfig,
    mats: dict,
    assets,
    *,
    is_center: bool,
):
    flange_r = r.center_flange_r if is_center else r.valve_flange_r
    body_botr = r.center_body_botr if is_center else r.valve_body_botr
    body_h = r.center_body_h if is_center else r.valve_body_h
    top_r = body_botr * r.taper
    col_top = FL_H + body_h
    esc_major = r.esc_major_center if is_center else r.esc_major_valve

    col = model.part(part_name)
    # Flange (sits on the deck top; its -Z face mates the deck +Z face).
    col.visual(
        _section_solid(r.section, flange_r, flange_r, FL_H, f"{vp}_flange_mesh", assets, z0=0.0),
        material=mats["metal"],
        name=f"{vp}_flange", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    # Tapered body.
    col.visual(
        _section_solid(r.section, body_botr, top_r, body_h, f"{vp}_body_mesh", assets, z0=FL_H),
        material=mats["metal"],
        name=f"{vp}_body", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    # Captured bonnet stem at the top (handle/spout/finial grip it).
    col.visual(
        Cylinder(radius=BONNET_R, length=BONNET_H),
        origin=Origin(xyz=(0.0, 0.0, col_top + BONNET_H / 2.0)),
        material=mats["metal"],
        name=f"{vp}_bonnet", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    # AX-4 escutcheon base trim disc (wider than the flange, sits on the deck).
    if r.escutcheon_ring == "ring":
        col.visual(
            Cylinder(radius=esc_major, length=r.esc_h),
            origin=Origin(xyz=(0.0, 0.0, r.esc_h / 2.0 + 0.001)),
            material=mats["metal"],
            name=f"{vp}_escutcheon", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
        )

    model.articulation(
        f"deck_to_{part_name}",
        ArticulationType.FIXED,
        parent=deck,
        child=col,
        origin=Origin(xyz=(world_x, 0.0, DECK_T)),
        mating=MatingContract(
            parent_face_geometry="deck_slab",
            parent_face_side="positive_z",
            child_face_geometry=f"{vp}_flange",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
    )
    return col, col_top, top_r


# --------------------------------------------------------------------------- #
# Slot B — center spout
# --------------------------------------------------------------------------- #


def _emit_collar(spout, r: ResolvedConfig, mats):
    """AX-5 root collar on the spout riser (gooseneck family)."""
    if r.collar_ring == "collar":
        spout.visual(
            Cylinder(radius=r.collar_r, length=r.collar_h),
            origin=Origin(xyz=(0.0, 0.0, r.collar_h / 2.0 + 0.002)),
            material=mats["metal"],
            name="spout_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
        )


def _emit_gooseneck_visuals(spout, r: ResolvedConfig, mats, assets):
    """Riser + swept gooseneck tube + downturned aerator (shared body)."""
    # Short solid riser stub whose -Z face seats on the column top (mating face)
    # and whose bore captures the bonnet.
    spout.visual(
        Cylinder(radius=TUBE_R, length=r.riser_h * 0.5),
        origin=Origin(xyz=(0.0, 0.0, r.riser_h * 0.25)),
        material=mats["metal"],
        name="riser", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    spout.visual(
        _gooseneck_mesh("gooseneck_tube", r, assets),
        material=mats["metal"],
        name="spout_arc", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    aer = (
        cq.Workplane("XY")
        .circle(AERATOR_R)
        .circle(AERATOR_R * 0.5)
        .extrude(AERATOR_LEN)
    )
    spout.visual(
        mesh_from_cadquery(aer, "aerator", assets=assets),
        origin=Origin(xyz=(0.0, r.reach, r.riser_h - AERATOR_LEN)),
        material=mats["metal"],
        name="aerator", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    _emit_collar(spout, r, mats)


def _build_gooseneck_swivel(model, r: ResolvedConfig, mats, center_col, c_top, assets):
    spout = model.part("center_spout")
    _emit_gooseneck_visuals(spout, r, mats, assets)
    model.articulation(
        "center_spout_swivel",
        ArticulationType.REVOLUTE,
        parent=center_col,
        child=spout,
        origin=Origin(xyz=(0.0, 0.0, c_top)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=-SWIVEL_LIMIT, upper=SWIVEL_LIMIT),
        mating=MatingContract(
            parent_face_geometry="center_body",
            parent_face_side="positive_z",
            child_face_geometry="riser",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
    )


def _build_gooseneck_pulldown_tilt(model, r: ResolvedConfig, mats, center_col, c_top, assets):
    spout = model.part("center_spout")
    _emit_gooseneck_visuals(spout, r, mats, assets)
    model.articulation(
        "center_spout_tilt",
        ArticulationType.REVOLUTE,
        parent=center_col,
        child=spout,
        origin=Origin(xyz=(0.0, 0.0, c_top)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=TILT_LOWER, upper=TILT_UPPER),
        mating=MatingContract(
            parent_face_geometry="center_body",
            parent_face_side="positive_z",
            child_face_geometry="riser",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
    )


def _emit_diverter_finial(model, r: ResolvedConfig, mats, spout, seat_world_z_local: tuple):
    """The moving diverter finial: seat (on the spout) + stem + oval + pointer tab.

    ``seat_world_z_local`` = (sx, sy, sz) of the seat centre in the SPOUT frame.
    The seat is a spout visual; the finial is a separate REVOLUTE part whose stem
    -Z face kisses the seat +Z face.
    """
    sx, sy, sz = seat_world_z_local
    spout.visual(
        Cylinder(radius=FIN_SEAT_R, length=FIN_SEAT_H),
        origin=Origin(xyz=(sx, sy, sz + FIN_SEAT_H / 2.0)),
        material=mats["metal"],
        name="diverter_seat", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    seat_top = sz + FIN_SEAT_H

    finial = model.part("diverter_finial")
    finial.visual(
        Cylinder(radius=FIN_STEM_R, length=FIN_STEM_H),
        origin=Origin(xyz=(0.0, 0.0, FIN_STEM_H / 2.0)),
        material=mats["metal"],
        name="finial_stem", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    finial.visual(
        Sphere(radius=FIN_OVAL_R),
        origin=Origin(xyz=(0.0, 0.0, FIN_STEM_H + FIN_OVAL_R * 0.6)),
        material=mats["metal"],
        name="finial_oval", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    # Off-axis pointer so the diverter rotation is observable / lever-like.
    finial.visual(
        Box((FIN_TAB_LEN, 0.005, 0.006)),
        origin=Origin(xyz=(FIN_TAB_LEN / 2.0 + FIN_OVAL_R * 0.5, 0.0, FIN_STEM_H + FIN_OVAL_R * 0.6)),
        material=mats["metal"],
        name="finial_tab", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    model.articulation(
        "diverter_spin",
        ArticulationType.REVOLUTE,
        parent=spout,
        child=finial,
        origin=Origin(xyz=(sx, sy, seat_top)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=1.0, velocity=2.0, lower=-DIVERTER_LIMIT, upper=DIVERTER_LIMIT
        ),
        mating=MatingContract(
            parent_face_geometry="diverter_seat",
            parent_face_side="positive_z",
            child_face_geometry="finial_stem",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
    )


def _build_waterfall_diverter(model, r: ResolvedConfig, mats, center_col, c_top, assets):
    spout = model.part("center_spout")
    # Neck stub seats on the column top.
    spout.visual(
        Cylinder(radius=max(TUBE_R, r.center_top_r), length=WF_NECK_H + 0.004),
        origin=Origin(xyz=(0.0, 0.0, (WF_NECK_H + 0.004) / 2.0)),
        material=mats["metal"],
        name="spout_neck", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    # Forward waterfall slab.
    slab_z = WF_NECK_H + WF_SLAB_TH / 2.0
    spout.visual(
        Box((WF_SLAB_W, r.reach, WF_SLAB_TH)),
        origin=Origin(xyz=(0.0, r.reach / 2.0, slab_z)),
        material=mats["metal"],
        name="waterfall_slab", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    # Front waterfall lip dropping down.
    spout.visual(
        Box((WF_SLAB_W, 0.010, WF_LIP_DROP)),
        origin=Origin(xyz=(0.0, r.reach - 0.005, slab_z - WF_LIP_DROP / 2.0)),
        material=mats["metal"],
        name="waterfall_lip", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    model.articulation(
        "center_spout_fixed",
        ArticulationType.FIXED,
        parent=center_col,
        child=spout,
        origin=Origin(xyz=(0.0, 0.0, c_top)),
        mating=MatingContract(
            parent_face_geometry="center_body",
            parent_face_side="positive_z",
            child_face_geometry="spout_neck",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
    )
    # Diverter button sits on TOP of the waterfall slab near its base (clear of
    # the neck below and the slab body).
    _emit_diverter_finial(model, r, mats, spout, (0.0, 0.020, WF_NECK_H + WF_SLAB_TH - 0.002))


def _build_gooseneck_diverter(model, r: ResolvedConfig, mats, center_col, c_top, assets):
    spout = model.part("center_spout")
    _emit_gooseneck_visuals(spout, r, mats, assets)
    model.articulation(
        "center_spout_fixed",
        ArticulationType.FIXED,
        parent=center_col,
        child=spout,
        origin=Origin(xyz=(0.0, 0.0, c_top)),
        mating=MatingContract(
            parent_face_geometry="center_body",
            parent_face_side="positive_z",
            child_face_geometry="riser",
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
    )
    # Diverter finial on top of the bend apex.
    apex = (0.0, r.reach / 2.0, r.riser_h + r.arc_h + TUBE_R - FIN_SEAT_H)
    _emit_diverter_finial(model, r, mats, spout, apex)


_SPOUT_BUILDERS = {
    "gooseneck_swivel": _build_gooseneck_swivel,
    "waterfall_diverter": _build_waterfall_diverter,
    "gooseneck_diverter": _build_gooseneck_diverter,
    "gooseneck_pulldown_tilt": _build_gooseneck_pulldown_tilt,
}


# --------------------------------------------------------------------------- #
# Slot C — valve handles (×2 stations, mirrored)
# --------------------------------------------------------------------------- #


def _emit_t_lever(handle, r: ResolvedConfig, mats, ind_mat, mirror: float):
    """Vertical stem + offset horizontal T-bar (AX-3 blade form) + indicator.

    The bar offsets OUTBOARD (away from the center spout) by ``mirror`` so the
    two stations read as a mirrored pair and the tip never reaches the center.
    """
    span = r.handle_span
    bar_r = r.bar_r
    stub = 0.20 * span
    bar_len = span + stub
    bar_cx = ((span - stub) / 2.0) * mirror
    cap_x = span * mirror
    stub_x = -stub * mirror
    bar_z = STEM_H * 0.72

    handle.visual(
        Cylinder(radius=STEM_R, length=STEM_H),
        origin=Origin(xyz=(0.0, 0.0, STEM_H / 2.0)),
        material=mats["metal"],
        name="stem", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    if r.lever_blade_form == "flat_strip":
        handle.visual(
            Box((bar_len, max(0.010, bar_r * 2.2), max(0.005, bar_r * 1.1))),
            origin=Origin(xyz=(bar_cx, 0.0, bar_z)),
            material=mats["metal"],
            name="lever_bar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
        )
    elif r.lever_blade_form == "tapered_leaf":
        # Loft from a wide root near the stem to a narrow tip (cadquery loft
        # along X; M_CHR-style frustum loft technique).
        root_w, root_h = max(0.012, bar_r * 2.6), max(0.006, bar_r * 1.3)
        tip_w, tip_h = max(0.005, bar_r * 1.0), max(0.004, bar_r * 0.8)
        solid = (
            cq.Workplane("YZ", origin=(stub_x, 0.0, bar_z))
            .rect(root_w, root_h)
            .workplane(offset=bar_len * mirror)
            .rect(tip_w, tip_h)
            .loft(combine=True)
        )
        handle.visual(
            mesh_from_cadquery(solid, "lever_leaf"),
            material=mats["metal"],
            name="lever_bar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
        )
    else:  # round_rod
        handle.visual(
            Cylinder(radius=bar_r, length=bar_len),
            origin=Origin(xyz=(bar_cx, 0.0, bar_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name="lever_bar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
        )
        handle.visual(
            Sphere(radius=bar_r * 1.35),
            origin=Origin(xyz=(stub_x, 0.0, bar_z)),
            material=mats["metal"],
            name="lever_stub_cap", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
        )
    # End cap (off-axis — used by the spin test).
    handle.visual(
        Sphere(radius=bar_r * 1.5),
        origin=Origin(xyz=(cap_x, 0.0, bar_z)),
        material=mats["metal"],
        name="lever_cap", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    # Hot/cold indicator dot embedded into the top of the bar.
    handle.visual(
        Cylinder(radius=bar_r * 0.9, length=0.004),
        origin=Origin(xyz=(bar_cx, 0.0, bar_z + bar_r * 0.5)),
        material=ind_mat,
        name="indicator", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )


def _emit_cross_spoke(handle, r: ResolvedConfig, mats, ind_mat):
    """Hub + dome + N radial spokes (AX-2) + end balls (+ optional rim)."""
    span = r.handle_span
    bar_r = r.bar_r
    tip_r = span / 2.0
    # Spokes start a few mm inside the hub wall (solid overlap -> connected) but
    # stay outboard of the central bonnet bore so they don't clash with it.
    inner_r = max(BONNET_R + 0.0015, HUB_R - 0.004)
    spoke_len = max(0.012, tip_r - inner_r)
    spoke_z = HUB_H / 2.0

    n_map = {"4_spoke": 4, "5_spoke": 5, "6_spoke": 6, "spoked_rim": 4}
    n = n_map[r.cross_spoke_form]

    handle.visual(
        Cylinder(radius=HUB_R, length=HUB_H),
        origin=Origin(xyz=(0.0, 0.0, HUB_H / 2.0)),
        material=mats["metal"],
        name="hub", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    handle.visual(
        Sphere(radius=HUB_R * 0.85),
        origin=Origin(xyz=(0.0, 0.0, HUB_H)),
        material=mats["metal"],
        name="hub_dome", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
    )
    handle.visual(
        Cylinder(radius=HUB_R * 0.6, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, HUB_H + HUB_R * 0.5)),
        material=ind_mat,
        name="indicator", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        cr = inner_r + spoke_len / 2.0
        cx = cr * math.cos(ang)
        cy = cr * math.sin(ang)
        handle.visual(
            Cylinder(radius=bar_r, length=spoke_len),
            origin=Origin(xyz=(cx, cy, spoke_z), rpy=(0.0, math.pi / 2.0, ang)),
            material=mats["metal"],
            name=f"spoke_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
        )
        bx = (inner_r + spoke_len) * math.cos(ang)
        by = (inner_r + spoke_len) * math.sin(ang)
        handle.visual(
            Sphere(radius=bar_r * 1.45),
            origin=Origin(xyz=(bx, by, spoke_z)),
            material=mats["metal"],
            name=f"spoke_ball_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
        )
    if r.cross_spoke_form == "spoked_rim":
        handle.visual(
            mesh_from_geometry(
                TorusGeometry(tip_r, bar_r, radial_segments=12, tubular_segments=32),
                "spoke_rim_mesh",
            ),
            origin=Origin(xyz=(0.0, 0.0, spoke_z)),
            material=mats["metal"],
            name="spoke_rim", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "matte_black", "brushed_nickel", "oil_rubbed_bronze"} else "metal.brass_polished"),
        )


def _build_handle(
    model: ArticulatedObject,
    prefix: str,
    valve_col,
    v_top: float,
    r: ResolvedConfig,
    mats: dict,
    ind_key: str,
    mirror: float,
):
    handle = model.part(f"{prefix}_handle")
    ind_mat = mats[ind_key]
    if r.valve_handle == "t_lever":
        _emit_t_lever(handle, r, mats, ind_mat, mirror)
        child_face = "stem"
    else:
        _emit_cross_spoke(handle, r, mats, ind_mat)
        child_face = "hub"

    limit = LEVER_LIMIT if r.valve_handle == "t_lever" else CROSS_LIMIT
    vp = f"{prefix}_valve"
    model.articulation(
        f"{prefix}_handle_turn",
        ArticulationType.REVOLUTE,
        parent=valve_col,
        child=handle,
        origin=Origin(xyz=(0.0, 0.0, v_top)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=-limit, upper=limit),
        mating=MatingContract(
            parent_face_geometry=f"{vp}_body",
            parent_face_side="positive_z",
            child_face_geometry=child_face,
            child_face_side="negative_z",
            contact_tol=0.0015,
        ),
    )
    return handle


# --------------------------------------------------------------------------- #
# Top-level build
# --------------------------------------------------------------------------- #


def build_widespread_two_handle_faucet(
    config: WidespreadTwoHandleFaucetConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-faucet-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]

    mats = _materials(model, r)

    deck = _build_deck(model, r, mats)

    center_col, c_top, _ = _build_column(
        model, deck, "center_column", "center", 0.0, r, mats, assets, is_center=True
    )
    _SPOUT_BUILDERS[r.center_spout](model, r, mats, center_col, c_top, assets)

    # Two fixed valve stations (hot = -X / red, cold = +X / blue), mirrored.
    for prefix, x_sign, ind in (("hot", -1.0, "hot"), ("cold", +1.0, "cold")):
        vcol, v_top, _ = _build_column(
            model,
            deck,
            f"{prefix}_valve_column",
            f"{prefix}_valve",
            x_sign * r.spread_half,
            r,
            mats,
            assets,
            is_center=False,
        )
        _build_handle(model, prefix, vcol, v_top, r, mats, ind, x_sign)

    return model


def build_seeded_widespread_two_handle_faucet(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_widespread_two_handle_faucet(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedConfig) -> None:
    spout = model.get_part("center_spout")
    center_col = model.get_part("center_column")

    # Center spout captures the center bonnet.
    if r.center_spout == "waterfall_diverter":
        ctx.allow_overlap(
            spout, center_col, elem_a="spout_neck", elem_b="center_bonnet",
            reason="Waterfall spout neck bore captures the center column bonnet stem.",
        )
    else:
        ctx.allow_overlap(
            spout, center_col, elem_a="riser", elem_b="center_bonnet",
            reason="Spout riser bore captures the center column bonnet stem.",
        )
        ctx.allow_overlap(
            spout, center_col, elem_a="spout_arc", elem_b="center_bonnet",
            reason="Swept gooseneck base runs coaxially over the captured bonnet stem.",
        )

    # AX-5 collar wraps the bonnet too.
    if r.collar_ring == "collar" and r.center_spout != "waterfall_diverter":
        ctx.allow_overlap(
            spout, center_col, elem_a="spout_collar", elem_b="center_bonnet",
            reason="Spout root collar sits over the captured bonnet stem.",
        )

    # Diverter finial captured on its seat.
    if "diverter_finial" in {p.name for p in model.parts}:
        finial = model.get_part("diverter_finial")
        ctx.allow_overlap(
            finial, spout, elem_a="finial_stem", elem_b="diverter_seat",
            reason="Diverter finial stem is captured in the spout diverter seat.",
        )

    # Handles capture the valve bonnets (the bonnet protrudes up into the hub /
    # stem and the elements that straddle the axis).
    capture_elems = ("stem", "lever_bar") if r.valve_handle == "t_lever" else ("hub", "hub_dome")
    for prefix in ("hot", "cold"):
        handle = model.get_part(f"{prefix}_handle")
        vcol = model.get_part(f"{prefix}_valve_column")
        vp = f"{prefix}_valve"
        for ce in capture_elems:
            ctx.allow_overlap(
                handle, vcol, elem_a=ce, elem_b=f"{vp}_bonnet",
                reason=f"{prefix} handle {ce} captures/overlaps the valve bonnet stem.",
            )


def run_widespread_two_handle_faucet_tests(
    object_model: ArticulatedObject,
    config: WidespreadTwoHandleFaucetConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlaps(ctx, object_model, r)

    part_names = {p.name for p in object_model.parts}
    joint_names = {a.name for a in object_model.articulations}

    # ---- Baseline structural / connectivity / mating gates. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity: three pieces, two mirrored valve stations. ----
    for required in ("deck", "center_column", "center_spout", "hot_valve_column",
                     "cold_valve_column", "hot_handle", "cold_handle"):
        ctx.check(f"part present: {required}", required in part_names, details=str(sorted(part_names)))

    # Exactly two valve stations (two-handle identity) — no third handle.
    handle_parts = [n for n in part_names if n.endswith("_handle")]
    ctx.check(
        "exactly two valve handles (two-handle identity)",
        len(handle_parts) == 2,
        details=str(sorted(handle_parts)),
    )

    # ---- Deck grounded, columns FIXED & seated on the deck. ----
    deck = object_model.get_part("deck")
    deck_bb = ctx.part_world_aabb(deck)
    ctx.check("deck rests on the ground", deck_bb[0][2] < 0.005, details=f"z_min={deck_bb[0][2]:.4f}")
    for col_name in ("center_column", "hot_valve_column", "cold_valve_column"):
        j = object_model.get_articulation(f"deck_to_{col_name}")
        ctx.check(
            f"{col_name} FIXED to deck",
            j.articulation_type == ArticulationType.FIXED,
            details=f"type={j.articulation_type}",
        )
        ctx.expect_contact(object_model.get_part(col_name), deck, name=f"{col_name} seated on deck")

    # ---- Widespread three-piece geometry. ----
    hot_bb = ctx.part_world_aabb(object_model.get_part("hot_valve_column"))
    cold_bb = ctx.part_world_aabb(object_model.get_part("cold_valve_column"))
    hot_cx = 0.5 * (hot_bb[0][0] + hot_bb[1][0])
    cold_cx = 0.5 * (cold_bb[0][0] + cold_bb[1][0])
    spacing = abs(cold_cx - hot_cx)
    ctx.check(
        "valve stations spaced ~2*spread_half apart",
        abs(spacing - 2.0 * r.spread_half) < 0.012 and hot_cx < cold_cx,
        details=f"spacing={spacing:.4f} expected={2.0 * r.spread_half:.4f}",
    )
    cen_bb = ctx.part_world_aabb(object_model.get_part("center_column"))
    cen_cx = 0.5 * (cen_bb[0][0] + cen_bb[1][0])
    ctx.check("center spout on the symmetry axis", abs(cen_cx) < 0.006, details=f"x={cen_cx:.4f}")

    # ---- Hot = -X (red), cold = +X (blue). ----
    ctx.check("hot station on -X, cold on +X", hot_cx < 0.0 < cold_cx, details=f"hot={hot_cx:.4f} cold={cold_cx:.4f}")
    for prefix, ind_key in (("hot", "hot"), ("cold", "cold")):
        handle = object_model.get_part(f"{prefix}_handle")
        ind_vis = next((v for v in handle.visuals if v.name == "indicator"), None)
        ctx.check(f"{prefix} handle has an indicator", ind_vis is not None)
        if ind_vis is not None:
            want = PALETTES[r.palette_style][ind_key]
            got = ind_vis.material.rgba if ind_vis.material is not None else None
            ctx.check(
                f"{prefix} indicator color is {ind_key}",
                got is not None and tuple(round(c, 3) for c in got) == tuple(round(c, 3) for c in want),
                details=f"got={got} want={want}",
            )

    # ---- Slot B topology + actuation. ----
    if r.center_spout == "gooseneck_swivel":
        j = object_model.get_articulation("center_spout_swivel")
        ctx.check(
            "gooseneck swivel REVOLUTE about +Z",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99,
            details=f"type={j.articulation_type} axis={j.axis}",
        )
        _check_spin(ctx, object_model, j, "center_spout", "aerator", 0.5, "spout swivels")
    elif r.center_spout == "gooseneck_pulldown_tilt":
        j = object_model.get_articulation("center_spout_tilt")
        ctx.check(
            "pulldown spout REVOLUTE about +X (horizontal hinge)",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
            details=f"type={j.articulation_type} axis={j.axis}",
        )
        aer = object_model.get_part("center_spout")
        rest = ctx.part_element_world_aabb(aer, elem="aerator")
        rest_z = 0.5 * (rest[0][2] + rest[1][2])
        with ctx.pose({j: TILT_LOWER}):
            down = ctx.part_element_world_aabb(aer, elem="aerator")
            down_z = 0.5 * (down[0][2] + down[1][2])
            ctx.check("pull-down lowers the outlet", down_z < rest_z - 0.004, details=f"rest={rest_z:.4f} down={down_z:.4f}")
            ctx.check("outlet stays above the deck while tilted", down[0][2] > DECK_T - 0.002, details=f"z_min={down[0][2]:.4f}")
    else:  # diverter families
        jf = object_model.get_articulation("center_spout_fixed")
        ctx.check("diverter spout body FIXED", jf.articulation_type == ArticulationType.FIXED, details=f"type={jf.articulation_type}")
        ctx.check("diverter finial part present", "diverter_finial" in part_names)
        jd = object_model.get_articulation("diverter_spin")
        ctx.check(
            "diverter finial REVOLUTE about +Z",
            jd.articulation_type == ArticulationType.REVOLUTE and abs(jd.axis[2]) > 0.99,
            details=f"type={jd.articulation_type} axis={jd.axis}",
        )
        _check_spin(ctx, object_model, jd, "diverter_finial", "finial_tab", DIVERTER_LIMIT * 0.6, "diverter turns")

    # ---- Slot C topology + handle spin. ----
    for prefix in ("hot", "cold"):
        j = object_model.get_articulation(f"{prefix}_handle_turn")
        ctx.check(
            f"{prefix} handle REVOLUTE about +Z",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99,
            details=f"type={j.articulation_type} axis={j.axis}",
        )
        spin_elem = "lever_cap" if r.valve_handle == "t_lever" else "spoke_ball_0"
        _check_spin(ctx, object_model, j, f"{prefix}_handle", spin_elem, math.pi / 4.0, f"{prefix} handle turns")

    # ---- Appearance sub-axes did NOT add joints (only the baseline set). ----
    expected_joints = {"deck_to_center_column", "deck_to_hot_valve_column",
                       "deck_to_cold_valve_column", "hot_handle_turn", "cold_handle_turn"}
    if r.center_spout == "gooseneck_swivel":
        expected_joints.add("center_spout_swivel")
    elif r.center_spout == "gooseneck_pulldown_tilt":
        expected_joints.add("center_spout_tilt")
    else:
        expected_joints.update({"center_spout_fixed", "diverter_spin"})
    ctx.check(
        "no appearance-driven joints (joint set matches baseline)",
        joint_names == expected_joints,
        details=f"got={sorted(joint_names)} expected={sorted(expected_joints)}",
    )

    # ---- AX-4 / AX-5 decoration presence (when sampled). ----
    if r.escutcheon_ring == "ring":
        cc = object_model.get_part("center_column")
        ctx.check(
            "escutcheon ring present on center column",
            any(v.name == "center_escutcheon" for v in cc.visuals),
        )
    if r.collar_ring == "collar" and r.center_spout != "waterfall_diverter":
        sp = object_model.get_part("center_spout")
        ctx.check(
            "spout root collar present",
            any(v.name == "spout_collar" for v in sp.visuals),
        )

    # ---- AX-1 section integrity: hexagonal still contains the bonnet bore. ----
    if r.section == "hexagonal":
        inscribed = r.valve_top_r * math.cos(math.pi / 6.0)
        ctx.check(
            "hexagonal column top inscribed circle still holds the bonnet bore",
            inscribed >= BONNET_R,
            details=f"inscribed={inscribed:.4f} bonnet_r={BONNET_R:.4f}",
        )

    # ---- slot_choices recorded (structural only). ----
    ctx.check(
        "slot_choices recorded (structural only)",
        tuple(tuple(t) for t in object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


def _check_spin(ctx, model, joint, part_name, elem, pose_val, label):
    """Pose the joint and assert an OFF-AXIS element actually moves (3D)."""
    part = model.get_part(part_name)
    rest = ctx.part_element_world_aabb(part, elem=elem)
    rc = (0.5 * (rest[0][0] + rest[1][0]), 0.5 * (rest[0][1] + rest[1][1]), 0.5 * (rest[0][2] + rest[1][2]))
    with ctx.pose({joint: pose_val}):
        posed = ctx.part_element_world_aabb(part, elem=elem)
        pc = (0.5 * (posed[0][0] + posed[1][0]), 0.5 * (posed[0][1] + posed[1][1]), 0.5 * (posed[0][2] + posed[1][2]))
    disp = math.dist(rc, pc)
    ctx.check(f"{label} (off-axis displacement)", disp > 0.003, details=f"disp={disp:.4f}")


__all__ = [
    "WidespreadTwoHandleFaucetConfig",
    "ResolvedConfig",
    "build_widespread_two_handle_faucet",
    "build_seeded_widespread_two_handle_faucet",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "run_widespread_two_handle_faucet_tests",
    "__modular__",
]
