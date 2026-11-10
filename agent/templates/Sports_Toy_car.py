# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for ``toy_car``.

Follows ``articraft_template_authoring/specs_modular_v1/Sports_Toy_car.md``.

A chunky wooden push-along toddler toy car.  World frame convention:

- +X is the car length: the character face / nose sits at the +X front.
- +Y is the car width; +Z is up.  The car rests on its wheels at ground z = 0.
- The deck top is around ``BODY_TOP_Z``; the deck-top play mechanism mounts there.

Three slots plus one multiplicity axis (pattern = mixed, root ``body``):

    body_form        (A) — bug_face_beetle / classic_car_driver
                           / pickup_truck_bed / open_racer_cockpit
    deck_mechanism   (B) — bead_maze_arch (FIXED arch + 3 CONTINUOUS beads)
                           / rooftop_spinner (CONTINUOUS about +Z)
                           / steering_column (CONTINUOUS about a tilted column)
    wheel_form       (C) — round_disc / knobby_offroad / spoked_wheel
    wheel_count      (N) — multiplicity axis over wheels [3..8]; odd N puts a
                           single centerline wheel at the front axle.

Each wheel is an independent CONTINUOUS roll joint about its local +Y axle.

Adopted 5-star sources (all read in full):
S1 rec_wooden-push-toy-car-...2a7a9bf4 — bug body + bead-maze arch + round disc wheels.
S2 rec_toy_car_var_classic   — classic two-box body with raised cabin + driver.
S3 rec_toy_car_var_pickup    — pickup truck body (cab + open cargo bed).
S4 rec_toy_car_var_racer     — open-racer hull with a cockpit pocket + driver.
S5 rec_toy_car_var_spinner   — rooftop pinwheel spinner (CONTINUOUS +Z).
S6 rec_toy_car_var_steering  — tilted steering column + wheel (CONTINUOUS).
S7 rec_toy_car_var_knobby    — fat knobby off-road tire.
S8 rec_toy_car_var_spoked    — open spoked cartwheel (lathe rim + spokes).
S9 rec_toy_car_var_wheels3   — 3-wheel trike (centerline front wheel).
S10 rec_toy_car_var_wheels6  — 6-wheel hauler (3 axles, stretched body).
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
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AssetSession,
    Box,
    BoxGeometry,
    Cylinder,
    CylinderGeometry,
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    SphereGeometry,
    TestContext,
    TestReport,
    TorusGeometry,
    activate_asset_session,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

BodyForm = Literal[
    "bug_face_beetle",
    "classic_car_driver",
    "pickup_truck_bed",
    "open_racer_cockpit",
]
DeckMechanism = Literal["bead_maze_arch", "rooftop_spinner", "steering_column"]
WheelForm = Literal["round_disc", "knobby_offroad", "spoked_wheel"]
PaletteStyle = Literal[
    "natural_wood_red",
    "painted_primary",
    "candy_pastel",
    "monochrome_black_white",
    "retro_teal_orange",
    "bright_rainbow",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "bug_face_beetle",
    "classic_car_driver",
    "pickup_truck_bed",
    "open_racer_cockpit",
)
DECK_MECHANISMS: tuple[DeckMechanism, ...] = (
    "bead_maze_arch",
    "rooftop_spinner",
    "steering_column",
)
WHEEL_FORMS: tuple[WheelForm, ...] = ("round_disc", "knobby_offroad", "spoked_wheel")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "natural_wood_red",
    "painted_primary",
    "candy_pastel",
    "monochrome_black_white",
    "retro_teal_orange",
    "bright_rainbow",
)

# Light weighting toward the classic baselines; every value keeps substantial
# probability so the slot pool is exercised within seeds 0-49.
_BODY_WEIGHTS = (0.30, 0.26, 0.22, 0.22)
_MECH_WEIGHTS = (0.38, 0.32, 0.30)
_WHEEL_WEIGHTS = (0.40, 0.30, 0.30)

# Multiplicity over wheels: small N heavily favoured (standard toy car).
WHEEL_COUNTS: tuple[int, ...] = (3, 4, 6, 8)
_WHEEL_COUNT_WEIGHTS = (0.25, 0.50, 0.15, 0.10)

# ---- shared key dimensions (meters), from the 5-star sources ----
WHEEL_R = 0.025
WHEEL_W = 0.016
AXLE_Y = 0.052          # half track at nominal scale
BODY_BOT_Z = 0.022
BODY_TOP_Z = 0.070
_CLASSIC_DRIVER_HEAD_R = 0.015
_CLASSIC_DRIVER_TARGET_VISIBLE_FRACTION = 0.82
_CLASSIC_DRIVER_MIN_VISIBLE_FRACTION = 0.78


# --------------------------------------------------------------------------- #
# Palettes
# --------------------------------------------------------------------------- #
#
# Every keyed slot is consumed by a ``.visual(..., material=mats[...])`` call so
# the swept output is colourful per seed (structure diversity is counted
# separately by module_topology_diversity).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "natural_wood_red": {
        "body": (0.80, 0.62, 0.36, 1.0),
        "body_dark": (0.66, 0.47, 0.26, 1.0),
        "accent": (0.85, 0.13, 0.12, 1.0),
        "hub": (0.88, 0.86, 0.82, 1.0),
        "black": (0.10, 0.10, 0.11, 1.0),
        "skin": (0.90, 0.74, 0.56, 1.0),
        "wire": (0.35, 0.62, 0.80, 1.0),
        "bead_a": (0.88, 0.18, 0.16, 1.0),
        "bead_b": (0.93, 0.55, 0.10, 1.0),
        "bead_c": (0.30, 0.66, 0.26, 1.0),
        "wheel": (0.85, 0.13, 0.12, 1.0),
    },
    "painted_primary": {
        "body": (0.20, 0.42, 0.82, 1.0),
        "body_dark": (0.14, 0.30, 0.60, 1.0),
        "accent": (0.90, 0.16, 0.14, 1.0),
        "hub": (0.94, 0.92, 0.88, 1.0),
        "black": (0.10, 0.10, 0.12, 1.0),
        "skin": (0.92, 0.78, 0.58, 1.0),
        "wire": (0.30, 0.32, 0.36, 1.0),
        "bead_a": (0.90, 0.16, 0.14, 1.0),
        "bead_b": (0.20, 0.42, 0.82, 1.0),
        "bead_c": (0.95, 0.82, 0.22, 1.0),
        "wheel": (0.95, 0.82, 0.22, 1.0),
    },
    "candy_pastel": {
        "body": (0.96, 0.72, 0.80, 1.0),
        "body_dark": (0.84, 0.58, 0.68, 1.0),
        "accent": (0.55, 0.82, 0.86, 1.0),
        "hub": (0.98, 0.96, 0.94, 1.0),
        "black": (0.34, 0.30, 0.36, 1.0),
        "skin": (0.97, 0.84, 0.74, 1.0),
        "wire": (0.74, 0.66, 0.86, 1.0),
        "bead_a": (0.98, 0.72, 0.78, 1.0),
        "bead_b": (0.74, 0.88, 0.74, 1.0),
        "bead_c": (0.74, 0.80, 0.96, 1.0),
        "wheel": (0.66, 0.84, 0.88, 1.0),
    },
    "monochrome_black_white": {
        "body": (0.92, 0.92, 0.93, 1.0),
        "body_dark": (0.40, 0.40, 0.43, 1.0),
        "accent": (0.12, 0.12, 0.14, 1.0),
        "hub": (0.96, 0.96, 0.97, 1.0),
        "black": (0.08, 0.08, 0.09, 1.0),
        "skin": (0.80, 0.80, 0.82, 1.0),
        "wire": (0.55, 0.55, 0.58, 1.0),
        "bead_a": (0.14, 0.14, 0.16, 1.0),
        "bead_b": (0.70, 0.70, 0.72, 1.0),
        "bead_c": (0.34, 0.34, 0.37, 1.0),
        "wheel": (0.14, 0.14, 0.16, 1.0),
    },
    "retro_teal_orange": {
        "body": (0.16, 0.55, 0.55, 1.0),
        "body_dark": (0.10, 0.38, 0.39, 1.0),
        "accent": (0.93, 0.46, 0.13, 1.0),
        "hub": (0.94, 0.90, 0.80, 1.0),
        "black": (0.12, 0.16, 0.16, 1.0),
        "skin": (0.93, 0.78, 0.58, 1.0),
        "wire": (0.20, 0.62, 0.62, 1.0),
        "bead_a": (0.93, 0.46, 0.13, 1.0),
        "bead_b": (0.95, 0.70, 0.20, 1.0),
        "bead_c": (0.18, 0.58, 0.58, 1.0),
        "wheel": (0.93, 0.46, 0.13, 1.0),
    },
    "bright_rainbow": {
        "body": (0.82, 0.64, 0.38, 1.0),
        "body_dark": (0.62, 0.44, 0.24, 1.0),
        "accent": (0.90, 0.16, 0.50, 1.0),
        "hub": (0.96, 0.94, 0.88, 1.0),
        "black": (0.12, 0.12, 0.14, 1.0),
        "skin": (0.92, 0.76, 0.56, 1.0),
        "wire": (0.40, 0.30, 0.82, 1.0),
        "bead_a": (0.90, 0.16, 0.16, 1.0),
        "bead_b": (0.20, 0.66, 0.30, 1.0),
        "bead_c": (0.25, 0.40, 0.88, 1.0),
        "wheel": (0.90, 0.16, 0.50, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ToyCarConfig:
    """Public configuration sampled by ``config_from_seed`` or supplied directly."""

    body_form: BodyForm = "bug_face_beetle"
    deck_mechanism: DeckMechanism = "bead_maze_arch"
    wheel_form: WheelForm = "round_disc"
    wheel_count: int = 4
    palette_style: PaletteStyle = "natural_wood_red"
    body_length_scale: float = 1.0
    body_width_scale: float = 1.0
    deck_height_scale: float = 1.0
    wheel_radius_scale: float = 1.0
    axle_track_scale: float = 1.0
    mechanism_scale: float = 1.0
    name: str = "reference_toy_car"


@dataclass(frozen=True)
class ResolvedToyCarConfig:
    body_form: BodyForm
    deck_mechanism: DeckMechanism
    wheel_form: WheelForm
    wheel_count: int
    palette_style: PaletteStyle
    body_length_scale: float
    body_width_scale: float
    deck_height_scale: float
    wheel_radius_scale: float
    axle_track_scale: float
    mechanism_scale: float
    name: str
    # derived
    palette: dict[str, tuple[float, float, float, float]]
    wheel_r: float
    axle_z: float
    axle_y: float
    body_len: float
    body_top_z: float
    deck_h: float
    width_w: float            # half-width scale factor applied to body Y extents
    axle_x_positions: tuple[float, ...]
    wheel_specs: tuple[tuple[int, float], ...]  # (axle_index, y_sign) y_sign 0 = centerline


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> ToyCarConfig:
    """Deterministic per-seed sampling of all slots, multiplicity, palette, scales.

    ``seed=0`` is not special: every seed independently samples Slot A/B/C, the
    weighted wheel_count, a colorway, and the continuous scales. Compatibility
    gates (racer×arch foot placement, pickup×spinner wall clearance) and the
    cross-part scale dependencies are resolved later in ``resolve_config``.
    """
    rng = random.Random(seed)

    body: BodyForm = rng.choices(BODY_FORMS, weights=_BODY_WEIGHTS, k=1)[0]
    mech: DeckMechanism = rng.choices(DECK_MECHANISMS, weights=_MECH_WEIGHTS, k=1)[0]
    wheel: WheelForm = rng.choices(WHEEL_FORMS, weights=_WHEEL_WEIGHTS, k=1)[0]
    wheel_count: int = rng.choices(WHEEL_COUNTS, weights=_WHEEL_COUNT_WEIGHTS, k=1)[0]
    palette: PaletteStyle = rng.choice(PALETTE_STYLES)

    body_length_scale = round(rng.uniform(0.92, 1.18), 4)
    body_width_scale = round(rng.uniform(0.92, 1.10), 4)
    deck_height_scale = round(rng.uniform(0.92, 1.10), 4)
    wheel_radius_scale = round(rng.uniform(0.88, 1.12), 4)
    axle_track_scale = round(rng.uniform(0.90, 1.12), 4)
    mechanism_scale = round(rng.uniform(0.85, 1.15), 4)

    return ToyCarConfig(
        body_form=body,
        deck_mechanism=mech,
        wheel_form=wheel,
        wheel_count=wheel_count,
        palette_style=palette,
        body_length_scale=body_length_scale,
        body_width_scale=body_width_scale,
        deck_height_scale=deck_height_scale,
        wheel_radius_scale=wheel_radius_scale,
        axle_track_scale=axle_track_scale,
        mechanism_scale=mechanism_scale,
        name=f"seeded_toy_car_{seed}",
    )


def _axle_layout(
    wheel_count: int, body_len: float, body_form: str = "bug_face_beetle"
) -> tuple[tuple[float, ...], tuple[tuple[int, float], ...]]:
    """Resolve axle X stations and per-wheel (axle_index, y_sign) placements.

    Even N: ceil(N/2) axles, each carrying an L/R pair (y_sign = +1/-1).
    Odd N: one axle carries a single centerline wheel (y_sign = 0); the remaining
    axles each carry an L/R pair. The centerline wheel goes on the FRONT axle for
    most bodies, but on the REAR axle for the open racer (its nose is a thin
    tapered point where the wheel-well clearance cut would detach the tip; the
    rear tail is wide and tall and absorbs the cut cleanly).
    """
    n_axles = (wheel_count + 1) // 2
    odd = wheel_count % 2 == 1
    center_on_rear = body_form == "open_racer_cockpit"
    # Spread axles along X from rear (-) to front (+) inside the body footprint.
    # For odd N pull the single-wheel axle inboard (0.20 vs 0.29) so its wheel
    # well lands in thicker mid-body rather than a thin tapered end.
    front_x = body_len * (0.20 if (odd and not center_on_rear) else 0.29)
    rear_x = -body_len * (0.20 if (odd and center_on_rear) else 0.29)
    if n_axles == 1:
        xs = (front_x,)
    else:
        xs = tuple(
            rear_x + (front_x - rear_x) * i / (n_axles - 1) for i in range(n_axles)
        )

    specs: list[tuple[int, float]] = []
    if odd:
        center_axle = 0 if center_on_rear else (n_axles - 1)
        specs.append((center_axle, 0.0))
        for ai in range(n_axles):
            if ai == center_axle:
                continue
            specs.append((ai, 1.0))
            specs.append((ai, -1.0))
    else:
        for ai in range(n_axles):
            specs.append((ai, 1.0))
            specs.append((ai, -1.0))
    # exactly wheel_count entries
    specs = specs[:wheel_count]
    return xs, tuple(specs)


def resolve_config(config: ToyCarConfig) -> ResolvedToyCarConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    body_form = _pick(config.body_form, BODY_FORMS)
    mech = _pick(config.deck_mechanism, DECK_MECHANISMS)
    wheel = _pick(config.wheel_form, WHEEL_FORMS)
    wheel_count = int(config.wheel_count)
    wheel_count = max(3, min(8, wheel_count))

    body_width_scale = _clamp(config.body_width_scale, 0.92, 1.10)
    deck_height_scale = _clamp(config.deck_height_scale, 0.92, 1.10)
    wheel_radius_scale = _clamp(config.wheel_radius_scale, 0.88, 1.12)
    axle_track_scale = _clamp(config.axle_track_scale, 0.90, 1.12)
    mechanism_scale = _clamp(config.mechanism_scale, 0.85, 1.15)

    # equation: AXLE_Z = WHEEL_R * scale guarantees the wheels reach the ground.
    wheel_r = WHEEL_R * wheel_radius_scale
    axle_z = wheel_r

    # body_length lower bound is the raw clamp; the upper bound rises with N so
    # the chassis can span more axles (conditional on wheel_count).
    n_axles = (wheel_count + 1) // 2
    body_length_scale = _clamp(config.body_length_scale, 0.92, 1.18)
    # require enough length for the axle count: each extra axle needs ~0.045 m.
    min_len_for_axles = 0.150 * (1.0 + 0.16 * max(0, n_axles - 2))
    # also require enough axle SPACING that adjacent wheels do not overlap:
    # the axle span is 0.58*body_len (rear -0.29 .. front +0.29), divided into
    # (n_axles-1) gaps; each gap must exceed one wheel diameter + clearance.
    if n_axles >= 2:
        needed_gap = 2.0 * wheel_r + 0.008
        min_len_for_spacing = needed_gap * (n_axles - 1) / 0.58
    else:
        min_len_for_spacing = 0.0
    body_len = max(0.150 * body_length_scale, min_len_for_axles, min_len_for_spacing)

    # deck top scales with deck_height_scale.
    deck_h = (BODY_TOP_Z - BODY_BOT_Z) * deck_height_scale
    body_top_z = BODY_BOT_Z + deck_h

    # inequality: axle half-track must keep the wheel clear of the body side
    # wall. Body half width ~ 0.042 * width_scale; need axle_y >= half_w +
    # WHEEL_W/2 + clearance. Project up if too narrow.
    width_w = body_width_scale
    # The widest body cross-section reaches ~0.045*width_w in Y; knobby/spoked
    # tires are a touch wider than WHEEL_W and have radial lugs, so keep a
    # generous gap between the wheel inner face and the body side wall.
    body_half_w = 0.045 * width_w
    axle_y = AXLE_Y * axle_track_scale
    min_axle_y = body_half_w + WHEEL_W / 2.0 + 0.007
    axle_y = max(axle_y, min_axle_y)

    axle_x_positions, wheel_specs = _axle_layout(wheel_count, body_len, body_form)

    return ResolvedToyCarConfig(
        body_form=body_form,
        deck_mechanism=mech,
        wheel_form=wheel,
        wheel_count=wheel_count,
        palette_style=config.palette_style,
        body_length_scale=body_length_scale,
        body_width_scale=body_width_scale,
        deck_height_scale=deck_height_scale,
        wheel_radius_scale=wheel_radius_scale,
        axle_track_scale=axle_track_scale,
        mechanism_scale=mechanism_scale,
        name=config.name,
        palette=dict(PALETTES[config.palette_style]),
        wheel_r=wheel_r,
        axle_z=axle_z,
        axle_y=axle_y,
        body_len=body_len,
        body_top_z=body_top_z,
        deck_h=deck_h,
        width_w=width_w,
        axle_x_positions=axle_x_positions,
        wheel_specs=wheel_specs,
    )


# --------------------------------------------------------------------------- #
# Slot A — body geometry (CadQuery solids) + character parent visuals.
# --------------------------------------------------------------------------- #


def _loft(sections) -> cq.Workplane:
    wp = cq.Workplane("YZ")
    prev = 0.0
    for i, s in enumerate(sections):
        x = s[1]
        off = x if i == 0 else x - prev
        if i > 0 or abs(off) > 1e-12:
            wp = wp.workplane(offset=off)
        if s[0] == "circle":
            wp = wp.circle(s[2])
        else:
            wp = wp.rect(s[2], s[3])
        prev = x
    return wp.loft(ruled=False)


def _scaled_sections(sections, *, xs: float, ws: float, hs: float):
    """Scale (rect, x, w, h) tuples by length / width / height factors."""
    out = []
    for s in sections:
        out.append(("rect", s[1] * xs, s[2] * ws, s[3] * hs))
    return out


def _bug_body_solid(r: ResolvedToyCarConfig) -> cq.Workplane:
    xs = r.body_len / 0.150
    ws = r.width_w
    hs = r.deck_h / 0.048
    zc = (BODY_BOT_Z + r.body_top_z) / 2.0
    h = r.deck_h
    base = [
        ("rect", -0.072, 0.066, h * 0.86 / hs),
        ("rect", -0.060, 0.080, h / hs),
        ("rect", 0.020, 0.084, h / hs),
        ("rect", 0.058, 0.080, h * 0.92 / hs),
        ("rect", 0.078, 0.060, h * 0.74 / hs),
    ]
    body = _loft(_scaled_sections(base, xs=xs, ws=ws, hs=hs))
    try:
        body = body.edges("|X").fillet(0.009)
    except Exception:
        pass
    return body.translate((0.0, 0.0, zc))


def _classic_nominal_cabin_height(r: ResolvedToyCarConfig) -> float:
    return 0.032 * (r.deck_h / 0.048)


def _classic_cabin_height(r: ResolvedToyCarConfig) -> float:
    """Derived cabin height that keeps the driver head visibly above the roof."""
    nominal = _classic_nominal_cabin_height(r)
    head_top = _classic_driver_head_z(r) + _CLASSIC_DRIVER_HEAD_R
    target_visible_h = 2.0 * _CLASSIC_DRIVER_HEAD_R * _CLASSIC_DRIVER_TARGET_VISIBLE_FRACTION
    max_for_head_readability = head_top - target_visible_h - r.body_top_z
    min_structural_h = max(0.012, r.deck_h * 0.24)
    return _clamp(min(nominal, max_for_head_readability), min_structural_h, nominal)


def _classic_cabin_top_z(r: ResolvedToyCarConfig) -> float:
    return r.body_top_z + _classic_cabin_height(r)


def _classic_driver_head_z(r: ResolvedToyCarConfig) -> float:
    # Keep the driver's original world-height placement. The cabin/roof thins
    # around it; the head is not lifted to satisfy the visibility constraint.
    return r.body_top_z + _classic_nominal_cabin_height(r) - 0.005


def _classic_body_solid(r: ResolvedToyCarConfig) -> cq.Workplane:
    xs = r.body_len / 0.150
    ws = r.width_w
    hs = r.deck_h / 0.048
    zc = (BODY_BOT_Z + r.body_top_z) / 2.0
    deck_h = r.deck_h
    base = [
        ("rect", -0.072, 0.068, deck_h * 0.90 / hs),
        ("rect", -0.055, 0.082, deck_h / hs),
        ("rect", -0.010, 0.084, deck_h / hs),
        ("rect", 0.025, 0.082, deck_h * 0.72 / hs),
        ("rect", 0.044, 0.080, deck_h * 0.68 / hs),
        ("rect", 0.060, 0.074, deck_h * 0.54 / hs),
        ("rect", 0.076, 0.058, deck_h * 0.44 / hs),
    ]
    deck = _loft(_scaled_sections(base, xs=xs, ws=ws, hs=hs))
    try:
        deck = deck.edges("|X").fillet(0.008)
    except Exception:
        pass
    deck = deck.translate((0.0, 0.0, zc))

    cabin_h = _classic_cabin_height(r)
    cabin = cq.Workplane("XY").box(0.058 * xs, 0.074 * ws, cabin_h)
    try:
        cabin = cabin.edges("|Z").fillet(0.008)
    except Exception:
        pass
    cabin = cabin.translate((-0.030 * xs, 0.0, r.body_top_z + cabin_h / 2.0))
    return deck.union(cabin)


def _pickup_body_solid(r: ResolvedToyCarConfig) -> cq.Workplane:
    xs = r.body_len / 0.150
    ws = r.width_w
    hs = r.deck_h / 0.048
    base_h = 0.022 * hs
    cab_h = 0.050 * hs
    bed_wall_h = 0.026 * hs
    cab_xc = 0.038 * xs
    cab_len = 0.065 * xs
    cab_w = 0.078 * ws
    bed_xc = -0.030 * xs
    bed_len = 0.080 * xs
    bed_w = 0.082 * ws
    wall_t = 0.007 * ws
    well_r = 0.016 * min(xs, ws)
    well_depth = 0.020 * hs

    base_zc = BODY_BOT_Z + base_h / 2.0
    cab_zc = BODY_BOT_Z + base_h + cab_h / 2.0
    cab_top_z = BODY_BOT_Z + base_h + cab_h
    wall_zc = BODY_BOT_Z + base_h + bed_wall_h / 2.0

    result = cq.Workplane("XY").box(r.body_len, 0.084 * ws, base_h).translate((0, 0, base_zc))
    try:
        result = result.edges("|Z").fillet(0.008)
    except Exception:
        pass
    cab = cq.Workplane("XY").box(cab_len, cab_w, cab_h).translate((cab_xc, 0, cab_zc))
    try:
        cab = cab.edges("|Z").fillet(0.008)
    except Exception:
        pass
    result = result.union(cab)
    bed_outer = cq.Workplane("XY").box(bed_len, bed_w, bed_wall_h).translate((bed_xc, 0, wall_zc))
    try:
        bed_outer = bed_outer.edges("|Z").fillet(0.006)
    except Exception:
        pass
    result = result.union(bed_outer)

    cavity_l = bed_len - wall_t
    cavity_w = bed_w - 2 * wall_t
    cavity_h = bed_wall_h + 0.004
    cavity_xc = bed_xc + wall_t / 2.0
    cavity_zc = BODY_BOT_Z + base_h + cavity_h / 2.0 + 0.002
    cavity = cq.Workplane("XY").box(cavity_l, cavity_w, cavity_h).translate(
        (cavity_xc, 0, cavity_zc)
    )
    result = result.cut(cavity)

    well = (
        cq.Workplane("XY")
        .circle(well_r)
        .extrude(well_depth + 0.005)
        .translate((cab_xc, 0, cab_top_z - well_depth))
    )
    result = result.cut(well)
    try:
        result = result.edges(">Z").fillet(0.004)
    except Exception:
        pass
    return result


def _racer_body_solid(r: ResolvedToyCarConfig) -> cq.Workplane:
    xs = r.body_len / 0.150
    ws = r.width_w
    hs = r.deck_h / 0.048
    zc = (BODY_BOT_Z + r.body_top_z) / 2.0
    h = r.deck_h
    base = [
        ("rect", -0.070, 0.040, h * 0.76 / hs),
        ("rect", -0.054, 0.080, h * 0.92 / hs),
        ("rect", -0.018, 0.084, h / hs),
        ("rect", 0.024, 0.068, h * 0.88 / hs),
        ("rect", 0.054, 0.036, h * 0.62 / hs),
        ("rect", 0.074, 0.014, h * 0.36 / hs),
    ]
    body = _loft(_scaled_sections(base, xs=xs, ws=ws, hs=hs))
    try:
        body = body.edges("|X").fillet(0.006)
    except Exception:
        pass
    body = body.translate((0.0, 0.0, zc))

    cockpit_x = -0.005 * xs
    cockpit_r = 0.020 * min(xs, ws)
    cockpit_depth = 0.018 * hs
    cutter_bottom = r.body_top_z - cockpit_depth - 0.002
    cutter_height = cockpit_depth + 0.009
    cutter = (
        cq.Workplane("XY")
        .workplane(offset=cutter_bottom)
        .center(cockpit_x, 0.0)
        .circle(cockpit_r)
        .extrude(cutter_height)
    )
    return body.cut(cutter)


# Geometry markers describing where the character face / cockpit sits for each
# body form, used by both the builder and tests.
@dataclass(frozen=True)
class _BodyInfo:
    block_elem: str
    # deck-top mounting Z for the mechanism feet (absolute world Z)
    deck_mount_z: float
    # cockpit / occupied X region the mechanism feet must avoid (for racer)
    cockpit_x: float
    cockpit_r: float


def _body_info(r: ResolvedToyCarConfig) -> _BodyInfo:
    xs = r.body_len / 0.150
    if r.body_form == "pickup_truck_bed":
        base_h = 0.022 * (r.deck_h / 0.048)
        bed_wall_h = 0.026 * (r.deck_h / 0.048)
        bed_top_z = BODY_BOT_Z + base_h + bed_wall_h
        return _BodyInfo("truck_body", bed_top_z, 0.0, 0.0)
    if r.body_form == "open_racer_cockpit":
        return _BodyInfo("racer_hull", r.body_top_z, -0.005 * xs, 0.020 * min(xs, r.width_w))
    if r.body_form == "classic_car_driver":
        return _BodyInfo("body_block", r.body_top_z, 0.0, 0.0)
    return _BodyInfo("body_block", r.body_top_z, 0.0, 0.0)


def _centerline_wheel_x(r: ResolvedToyCarConfig) -> float | None:
    """X station of the single centerline wheel for odd wheel_count, else None."""
    for axle_idx, ys in r.wheel_specs:
        if ys == 0.0:
            return r.axle_x_positions[axle_idx]
    return None


def _center_well_dims(r: ResolvedToyCarConfig) -> tuple[float, float, float, float]:
    """Shared centerline wheel-well dimensions (well_len, well_w, well_bot,
    well_top). Sized generously so knobby/spoked tires (wider + radial lugs than
    a plain disc) clear the slot."""
    wheel_top = r.axle_z + r.wheel_r
    well_len = 2.0 * (r.wheel_r * 1.10) + 0.012
    well_w = WHEEL_W + 0.018
    well_bot = BODY_BOT_Z - 0.010
    well_top = wheel_top + 0.006
    return well_len, well_w, well_bot, well_top


def _cut_center_wheel_well(solid: cq.Workplane, r: ResolvedToyCarConfig) -> cq.Workplane:
    """Carve a centerline clearance well so the single front centerline wheel
    (odd wheel_count) does not interpenetrate the body solid. Paired wheels sit
    at y=±axle_y outside the body; the centerline wheel runs through y=0 and must
    have a slot cut for it."""
    cx = _centerline_wheel_x(r)
    if cx is None:
        return solid
    well_len, well_w, well_bot, well_top = _center_well_dims(r)
    well_h = well_top - well_bot
    well = cq.Workplane("XY").box(well_len, well_w, well_h).translate(
        (cx, 0.0, well_bot + well_h / 2.0)
    )
    try:
        return solid.cut(well)
    except Exception:
        return solid


def _add_body(model: ArticulatedObject, r: ResolvedToyCarConfig, mats: dict):
    body = model.part("body")
    info = _body_info(r)

    if r.body_form == "bug_face_beetle":
        body.visual(
            mesh_from_cadquery(_cut_center_wheel_well(_bug_body_solid(r), r), "body_block"),
            material=mats["body"],
            name="body_block", material_class_id=("wood.polished_varnished" if r.palette_style in {"natural_wood_red", "bright_rainbow"} else "wood.painted_clean"),
        )
        _add_bug_face(body, r, mats)
    elif r.body_form == "classic_car_driver":
        body.visual(
            mesh_from_cadquery(_cut_center_wheel_well(_classic_body_solid(r), r), "body_block"),
            material=mats["body"],
            name="body_block", material_class_id=("wood.polished_varnished" if r.palette_style in {"natural_wood_red", "bright_rainbow"} else "wood.painted_clean"),
        )
        _add_classic_driver(body, r, mats)
    elif r.body_form == "pickup_truck_bed":
        body.visual(
            mesh_from_cadquery(_cut_center_wheel_well(_pickup_body_solid(r), r), "truck_body"),
            material=mats["body"],
            name="truck_body", material_class_id=("wood.polished_varnished" if r.palette_style in {"natural_wood_red", "bright_rainbow"} else "wood.painted_clean"),
        )
        _add_pickup_driver(body, r, mats)
    else:  # open_racer_cockpit
        body.visual(
            mesh_from_cadquery(_cut_center_wheel_well(_racer_body_solid(r), r), "racer_hull"),
            material=mats["body"],
            name="racer_hull", material_class_id=("wood.polished_varnished" if r.palette_style in {"natural_wood_red", "bright_rainbow"} else "wood.painted_clean"),
        )
        _add_racer_driver(body, r, mats)

    body.inertial = Inertial.from_geometry(
        Box((r.body_len, 0.085 * r.width_w, 0.080)),
        mass=0.30,
        origin=Origin(xyz=(0.0, 0.0, max(0.045, (BODY_BOT_Z + r.body_top_z) / 2.0))),
    )
    return body, info


def _add_bug_face(body, r: ResolvedToyCarConfig, mats: dict):
    xs = r.body_len / 0.150
    head_x = 0.082 * xs
    head_z = r.body_top_z - 0.010
    head_r = 0.026
    head = SphereGeometry(head_r, width_segments=32, height_segments=24)
    head.translate(head_x, 0.0, head_z)
    body.visual(mesh_from_geometry(head, "bug_head"), material=mats["body"], name="bug_head", material_class_id=("wood.polished_varnished" if r.palette_style in {"natural_wood_red", "bright_rainbow"} else "wood.painted_clean"))

    for i, ey in enumerate((-0.010, 0.010)):
        eye = CylinderGeometry(0.0045, 0.006, radial_segments=18).rotate_y(math.pi / 2.0)
        eye.translate(head_x + 0.022, ey, head_z + 0.006)
        body.visual(mesh_from_geometry(eye, f"eye_{i}"), material=mats["black"], name=f"eye_{i}", material_class_id="plastic.opaque_glossy_molded")

    smile = TorusGeometry(0.011, 0.0016, radial_segments=10, tubular_segments=28)
    smile.rotate_x(math.pi / 2.0)
    smile.rotate_z(math.pi / 2.0)
    smile.translate(head_x + 0.0215, 0.0, head_z - 0.004)
    body.visual(mesh_from_geometry(smile, "smile"), material=mats["black"], name="smile", material_class_id="plastic.opaque_glossy_molded")

    nose = SphereGeometry(0.007, width_segments=20, height_segments=14)
    nose.translate(head_x + 0.0205, 0.0, head_z - 0.006)
    body.visual(mesh_from_geometry(nose, "nose"), material=mats["accent"], name="nose", material_class_id="plastic.opaque_glossy_molded")

    for i, ay in enumerate((-0.011, 0.011)):
        stalk = tube_from_spline_points(
            [
                (head_x - 0.004 * (1 - 2 * i), ay * 0.6, head_z + 0.020),
                (head_x - 0.006, ay, head_z + 0.034),
                (head_x - 0.012, ay * 1.3, head_z + 0.044),
            ],
            radius=0.0013,
            samples_per_segment=12,
            radial_segments=10,
        )
        tip = SphereGeometry(0.0035, width_segments=14, height_segments=10)
        tip.translate(head_x - 0.012, ay * 1.3, head_z + 0.044)
        stalk.merge(tip)
        body.visual(
            mesh_from_geometry(stalk, f"antenna_{i}"), material=mats["black"], name=f"antenna_{i}", material_class_id="rubber.smooth_plain"
        )


def _add_classic_driver(body, r: ResolvedToyCarConfig, mats: dict):
    xs = r.body_len / 0.150
    driver_x = -0.038 * xs
    driver_r = _CLASSIC_DRIVER_HEAD_R
    driver_z = _classic_driver_head_z(r)
    head = SphereGeometry(driver_r, width_segments=28, height_segments=20)
    head.translate(driver_x, 0.0, driver_z)
    body.visual(mesh_from_geometry(head, "driver_head"), material=mats["skin"], name="driver_head", material_class_id="organic.biological_surface")
    for i, ey in enumerate((-0.006, 0.006)):
        eye = CylinderGeometry(0.003, 0.004, radial_segments=16).rotate_y(math.pi / 2.0)
        eye.translate(driver_x + driver_r * 0.88, ey, driver_z + 0.004)
        body.visual(
            mesh_from_geometry(eye, f"driver_eye_{i}"),
            material=mats["black"],
            name=f"driver_eye_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    smile = TorusGeometry(0.007, 0.0012, radial_segments=10, tubular_segments=24)
    smile.rotate_x(math.pi / 2.0)
    smile.rotate_z(math.pi / 2.0)
    smile.translate(driver_x + driver_r * 0.84, 0.0, driver_z - 0.004)
    body.visual(mesh_from_geometry(smile, "driver_smile"), material=mats["black"], name="driver_smile", material_class_id="plastic.opaque_glossy_molded")


def _add_pickup_driver(body, r: ResolvedToyCarConfig, mats: dict):
    xs = r.body_len / 0.150
    hs = r.deck_h / 0.048
    base_h = 0.022 * hs
    cab_h = 0.050 * hs
    well_depth = 0.020 * hs
    cab_xc = 0.038 * xs
    cab_top_z = BODY_BOT_Z + base_h + cab_h
    stem_bot_z = cab_top_z - well_depth - 0.003
    stem_top_z = cab_top_z - 0.002
    stem_h = stem_top_z - stem_bot_z
    stem = CylinderGeometry(0.006, stem_h, radial_segments=14)
    stem.translate(cab_xc, 0.0, stem_bot_z + stem_h / 2.0)
    body.visual(mesh_from_geometry(stem, "driver_stem"), material=mats["hub"], name="driver_stem", material_class_id="plastic.opaque_glossy_molded")

    head_r = 0.014
    head = SphereGeometry(head_r, width_segments=28, height_segments=20)
    head.translate(cab_xc, 0.0, cab_top_z)
    body.visual(mesh_from_geometry(head, "driver_head"), material=mats["skin"], name="driver_head", material_class_id="organic.biological_surface")
    for i, ey in enumerate((-0.006, 0.006)):
        eye = CylinderGeometry(0.0025, 0.004, radial_segments=12).rotate_y(math.pi / 2.0)
        eye.translate(cab_xc + head_r - 0.005, ey, cab_top_z + 0.004)
        body.visual(
            mesh_from_geometry(eye, f"driver_eye_{i}"),
            material=mats["black"],
            name=f"driver_eye_{i}", material_class_id="plastic.opaque_glossy_molded",
        )


def _add_racer_driver(body, r: ResolvedToyCarConfig, mats: dict):
    xs = r.body_len / 0.150
    cockpit_x = -0.005 * xs
    driver_r = 0.015
    driver_x = cockpit_x
    driver_z = r.body_top_z + driver_r * 0.55
    head = SphereGeometry(driver_r, width_segments=28, height_segments=20)
    head.translate(driver_x, 0.0, driver_z)
    # Seat stem: bridge the head down to the cockpit-pocket floor so the driver
    # is anchored to the hull (the carved pocket otherwise leaves the head
    # floating above the deck). Merged into the head visual = one island.
    cockpit_depth = 0.018 * (r.deck_h / 0.048)
    pocket_floor_z = r.body_top_z - cockpit_depth - 0.002
    stem_bot = pocket_floor_z
    stem_top = driver_z
    stem_h = max(0.008, stem_top - stem_bot)
    seat = CylinderGeometry(0.010, stem_h, radial_segments=16)
    seat.translate(driver_x, 0.0, stem_bot + stem_h / 2.0)
    head.merge(seat)
    body.visual(mesh_from_geometry(head, "driver_head"), material=mats["skin"], name="driver_head", material_class_id="organic.biological_surface")
    eye_fwd = driver_x + driver_r * 0.82
    eye_z = driver_z + driver_r * 0.15
    for i, ey in enumerate((-0.006, 0.006)):
        eye = CylinderGeometry(0.003, 0.005, radial_segments=16).rotate_y(math.pi / 2.0)
        eye.translate(eye_fwd, ey, eye_z)
        body.visual(
            mesh_from_geometry(eye, f"driver_eye_{i}"),
            material=mats["black"],
            name=f"driver_eye_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    smile_z = driver_z - driver_r * 0.28
    smile = TorusGeometry(0.008, 0.0013, radial_segments=10, tubular_segments=24)
    smile.rotate_x(math.pi / 2.0)
    smile.rotate_z(math.pi / 2.0)
    smile.translate(driver_x + driver_r * 0.78, 0.0, smile_z)
    body.visual(mesh_from_geometry(smile, "driver_smile"), material=mats["black"], name="driver_smile", material_class_id="plastic.opaque_glossy_molded")


# --------------------------------------------------------------------------- #
# Axle pegs + wheels (Slot C, multiplicity).
# --------------------------------------------------------------------------- #


def _add_axle_pegs(body, r: ResolvedToyCarConfig, mats: dict):
    """One peg per axle station. Centerline-only axles get a short peg."""
    # which axles carry a centerline-only wheel (odd N, front axle)
    centerline_axles = {ai for ai, ys in r.wheel_specs if ys == 0.0}
    paired_axles = {ai for ai, ys in r.wheel_specs if ys != 0.0}

    center_x = _centerline_wheel_x(r)
    saddle_bot = r.axle_z - 0.004
    # Reach well up into the body solid (not just to mid-height): the body's
    # convex-hull collision shape is inset behind its filleted surface, so a
    # shallow saddle ends up a fraction of a mm short and reads as a floating
    # island. Penetrate to ~the deck so the overlap is unambiguous.
    saddle_top = r.body_top_z - 0.006

    # Central chassis spine: a longitudinal block at the body centerline,
    # embedded deep into the THICK central body solid (where the convex-hull
    # collision shape is solid, unlike the thin filleted front/rear edges). It
    # bridges all axle saddles to a single trunk that is unambiguously fused with
    # the body, so no axle peg can float. For odd wheel_count there is a
    # centerline wheel spinning at y=0 over the front axle; the spine must stop
    # short of that wheel-well so it does not foul the wheel.
    xs_pos = list(r.axle_x_positions)
    spine_x0 = min(xs_pos) - 0.012
    spine_x1 = max(xs_pos) + 0.012
    if center_x is not None:
        # Keep the spine on the rear side of the centerline wheel.
        well_half = r.wheel_r + 0.006
        if center_x >= 0:
            spine_x1 = min(spine_x1, center_x - well_half)
        else:
            spine_x0 = max(spine_x0, center_x + well_half)
    if spine_x1 - spine_x0 > 0.02:
        spine_bot = r.axle_z - 0.004
        spine_top = r.body_top_z - 0.006
        spine_h = max(0.022, spine_top - spine_bot)
        spine_len = spine_x1 - spine_x0
        spine = BoxGeometry((spine_len, 0.022, spine_h))
        spine.translate((spine_x0 + spine_x1) / 2.0, 0.0, spine_bot + spine_h / 2.0)
        body.visual(
            mesh_from_geometry(spine, "chassis_spine"),
            material=mats["body_dark"],
            name="chassis_spine", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"natural_wood_red", "bright_rainbow"} else "wood.painted_clean"),
        )

    for ai, ax_x in enumerate(r.axle_x_positions):
        is_centerline = ai in centerline_axles and ai not in paired_axles
        if is_centerline:
            _, well_w, _, _ = _center_well_dims(r)
            # Longer peg so its ends reach BEYOND the wheel-well side walls into
            # the surrounding body, anchoring the centerline wheel's axle without
            # a central saddle (which would sit inside the cleared well).
            length = well_w + 0.018
        else:
            length = 2 * r.axle_y + 0.010
        peg = CylinderGeometry(0.005, length, radial_segments=16).rotate_x(math.pi / 2.0)
        peg.translate(ax_x, 0.0, r.axle_z)

        if is_centerline:
            _, well_w, _, _ = _center_well_dims(r)
            # Two side saddles flanking the well, embedding the peg ends up into
            # the body side walls beside the cleared wheel-well.
            saddle_h = max(0.020, saddle_top - saddle_bot)
            for sgn in (-1.0, 1.0):
                side = BoxGeometry((0.018, 0.012, saddle_h))
                side.translate(
                    ax_x,
                    sgn * (well_w / 2.0 + 0.008),
                    saddle_bot + saddle_h / 2.0,
                )
                peg.merge(side)
        else:
            # Axle bearing saddle: a vertical block at the centerline that
            # straddles the peg and reaches up into the body solid, guaranteeing
            # the peg is connected even where the tapered/raised body bottom sits
            # above the peg top.
            saddle_h = max(0.020, saddle_top - saddle_bot)
            saddle = BoxGeometry((0.020, 0.024, saddle_h))
            saddle.translate(ax_x, 0.0, saddle_bot + saddle_h / 2.0)
            peg.merge(saddle)
        body.visual(mesh_from_geometry(peg, f"axle_{ai}"), material=mats["body_dark"], name=f"axle_{ai}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"natural_wood_red", "bright_rainbow"} else "wood.painted_clean"))


def _round_disc_mesh(r: ResolvedToyCarConfig):
    from sdk import WheelBore, WheelFace, WheelGeometry, WheelHub, WheelRim

    s = r.wheel_radius_scale
    wheel = WheelGeometry(
        r.wheel_r,
        WHEEL_W,
        rim=WheelRim(inner_radius=0.018 * s, flange_height=0.004, flange_thickness=0.003),
        hub=WheelHub(radius=0.009 * s, width=WHEEL_W * 0.6, cap_style="recessed"),
        face=WheelFace(dish_depth=0.004, front_inset=0.002),
        bore=WheelBore(style="round", diameter=0.006),
    )
    wheel.rotate_z(math.pi / 2.0)
    return mesh_from_geometry(wheel, "wheel_body")


def _knobby_mesh(r: ResolvedToyCarConfig):
    tire_body_r = r.wheel_r * 0.82
    knob_r = 0.006
    knob_n = 8
    knob_rows = 2
    tire = CylinderGeometry(tire_body_r, WHEEL_W, radial_segments=28)
    for side in (-1, 1):
        wall = CylinderGeometry(tire_body_r * 1.06, WHEEL_W * 0.18, radial_segments=24)
        wall.translate(0.0, 0.0, side * (WHEEL_W * 0.40))
        tire.merge(wall)
    tread_band = CylinderGeometry(tire_body_r * 1.04, WHEEL_W * 0.70, radial_segments=28)
    tire.merge(tread_band)
    for row_i in range(knob_rows):
        z_off = (row_i - (knob_rows - 1) / 2.0) * (WHEEL_W * 0.32)
        angle_offset = (math.pi / knob_n) * row_i
        for i in range(knob_n):
            angle = 2.0 * math.pi * i / knob_n + angle_offset
            r_mount = tire_body_r * 1.04 + knob_r * 0.30
            kx = r_mount * math.cos(angle)
            ky = r_mount * math.sin(angle)
            knob = SphereGeometry(knob_r, width_segments=10, height_segments=8)
            knob.translate(kx, ky, z_off)
            tire.merge(knob)
    tire.rotate_x(math.pi / 2.0)
    return mesh_from_geometry(tire, "wheel_body")


def _add_spoked_wheel_visuals(w, r: ResolvedToyCarConfig, mats: dict, ysign: float):
    n_spokes = 6
    rim_t = 0.004
    rim_inner = r.wheel_r - rim_t
    half_w = WHEEL_W / 2.0
    hub_r = 0.007
    spoke_w = 0.005
    spoke_h = WHEEL_W * 0.80
    spoke_overlap = 0.001

    profile = [
        (rim_inner, -half_w),
        (r.wheel_r, -half_w),
        (r.wheel_r, half_w),
        (rim_inner, half_w),
    ]
    rim = LatheGeometry(profile, segments=36)
    rim.rotate_x(-math.pi / 2.0)
    w.visual(mesh_from_geometry(rim, "wheel_body"), material=mats["wheel"], name="wheel_body", material_class_id="wood.painted_clean")

    hub = CylinderGeometry(hub_r, WHEEL_W * 0.92, radial_segments=20)
    hub.rotate_x(-math.pi / 2.0)
    w.visual(mesh_from_geometry(hub, "hub"), material=mats["wheel"], name="hub", material_class_id="wood.painted_clean")

    inner_r = hub_r - spoke_overlap
    outer_r = rim_inner + spoke_overlap
    length = outer_r - inner_r
    mid_r = (inner_r + outer_r) / 2.0
    for i in range(n_spokes):
        angle = i * (2.0 * math.pi / n_spokes)
        geom = BoxGeometry((length, spoke_h, spoke_w))
        geom.translate(mid_r, 0.0, 0.0)
        geom.rotate((0.0, 1.0, 0.0), angle)
        w.visual(mesh_from_geometry(geom, f"spoke_{i}"), material=mats["wheel"], name=f"spoke_{i}", material_class_id="wood.painted_clean")


def _add_wheels(model: ArticulatedObject, body, r: ResolvedToyCarConfig, mats: dict):
    half_w = WHEEL_W / 2.0
    for i, (axle_idx, ysign) in enumerate(r.wheel_specs):
        ax_x = r.axle_x_positions[axle_idx]
        nm = f"wheel_{i}"
        w = model.part(nm)
        # hub cap face side: centerline wheels cap on +Y, paired follow their side.
        cap_side = ysign if ysign != 0.0 else 1.0

        if r.wheel_form == "round_disc":
            w.visual(_round_disc_mesh(r), material=mats["wheel"], name="wheel_body", material_class_id="wood.painted_clean")
        elif r.wheel_form == "knobby_offroad":
            w.visual(_knobby_mesh(r), material=mats["black"], name="wheel_body", material_class_id="rubber.pebbled")
        else:
            _add_spoked_wheel_visuals(w, r, mats, cap_side)

        hub = CylinderGeometry(0.010, 0.008, radial_segments=20).rotate_x(math.pi / 2.0)
        hub.translate(0.0, cap_side * (half_w - 0.002), 0.0)
        w.visual(mesh_from_geometry(hub, "hub_cap"), material=mats["hub"], name="hub_cap", material_class_id="plastic.opaque_glossy_molded")

        marker = CylinderGeometry(0.0022, 0.010, radial_segments=10).rotate_x(math.pi / 2.0)
        marker.translate(0.013, cap_side * (half_w - 0.003), 0.0)
        w.visual(mesh_from_geometry(marker, "spin_marker"), material=mats["black"], name="spin_marker", material_class_id="plastic.opaque_generic")

        w.inertial = Inertial.from_geometry(
            Box((2 * r.wheel_r, WHEEL_W, 2 * r.wheel_r)), mass=0.02
        )
        model.articulation(
            f"axle_{nm}",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=w,
            origin=Origin(xyz=(ax_x, ysign * r.axle_y, r.axle_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=0.5, velocity=20.0),
        )


# --------------------------------------------------------------------------- #
# Slot B — deck-top play mechanism.
# --------------------------------------------------------------------------- #


def _add_bead_maze_arch(model: ArticulatedObject, body, r: ResolvedToyCarConfig, mats: dict, info: _BodyInfo):
    ms = r.mechanism_scale
    hs = r.deck_h / 0.048
    foot_z = info.deck_mount_z - 0.004
    apex_z = info.deck_mount_z + 0.042 * ms
    mid_z = info.deck_mount_z + 0.022 * ms

    # Raised features (classic cabin, pickup cab, driver heads) stick up through
    # the arch span; lift the wire's mid/apex so the wire AND the threaded beads
    # (radius ~0.011) clear them instead of intersecting.
    bead_clear = 0.011 + 0.006
    feature_top = info.deck_mount_z
    if r.body_form == "classic_car_driver":
        feature_top = _classic_driver_head_z(r) + _CLASSIC_DRIVER_HEAD_R
    elif r.body_form == "pickup_truck_bed":
        base_h = 0.022 * hs
        cab_h = 0.050 * hs
        feature_top = BODY_BOT_Z + base_h + cab_h + 0.028  # + driver head
    elif r.body_form == "open_racer_cockpit":
        feature_top = r.body_top_z + 0.030
    mid_z = max(mid_z, feature_top + bead_clear)
    apex_z = max(apex_z, mid_z + 0.016)
    # Anchor the FIXED joint at a real mating point on the deck (where the arch
    # foot seats) rather than world origin, then build the arch/bead geometry
    # RELATIVE to that anchor so the world pose is unchanged. This keeps the
    # joint origin inside both parent (deck) and child (foot) geometry.
    anchor = (-0.050, -0.030, foot_z)

    def _rel(p):
        return (p[0] - anchor[0], p[1] - anchor[1], p[2] - anchor[2])

    arch_pts = [
        _rel((-0.050, -0.030, foot_z)),
        _rel((-0.040, -0.028, mid_z)),
        _rel((-0.010, -0.010, apex_z)),
        _rel((0.020, 0.012, apex_z - 0.004)),
        _rel((0.046, 0.026, mid_z)),
        _rel((0.052, 0.030, foot_z)),
    ]
    wire = tube_from_spline_points(
        arch_pts, radius=0.0022, samples_per_segment=18, radial_segments=14, cap_ends=True
    )
    arch = model.part("wire_arch")
    arch.visual(mesh_from_geometry(wire, "arch_wire"), material=mats["wire"], name="arch_wire", material_class_id="metal.paint_coated")
    arch.inertial = Inertial.from_geometry(
        Box((0.11, 0.07, 0.05)), mass=0.02, origin=Origin(xyz=_rel((0.0, 0.0, mid_z)))
    )
    model.articulation(
        "body_to_arch",
        ArticulationType.FIXED,
        parent=body,
        child=arch,
        origin=Origin(xyz=anchor),
    )

    bead_mats = (mats["bead_a"], mats["bead_b"], mats["bead_c"])
    bead_specs = [
        ((-0.030, -0.020, mid_z + (apex_z - mid_z) * 0.45), (0.55, 0.22, 0.45)),
        ((0.004, -0.001, apex_z - 0.001), (0.80, 0.40, -0.08)),
        ((0.034, 0.020, mid_z + (apex_z - mid_z) * 0.30), (0.55, 0.35, -0.62)),
    ]
    for idx, (center, tangent) in enumerate(bead_specs):
        n = math.sqrt(sum(c * c for c in tangent))
        ax = tuple(c / n for c in tangent)
        disc = CylinderGeometry(0.011, 0.012, radial_segments=22).rotate_y(math.pi / 2.0)
        yaw = math.atan2(ax[1], ax[0])
        pitch = math.asin(max(-1.0, min(1.0, ax[2])))
        disc.rotate_y(-pitch)
        disc.rotate_z(yaw)
        nm = f"bead_{idx}"
        bead = model.part(nm)
        bead.visual(mesh_from_geometry(disc, "bead_disc"), material=bead_mats[idx], name="bead_disc", material_class_id="plastic.opaque_glossy_molded")
        bead.inertial = Inertial.from_geometry(Cylinder(0.011, 0.012), mass=0.004)
        model.articulation(
            f"arch_to_{nm}",
            ArticulationType.CONTINUOUS,
            parent=arch,
            child=bead,
            # bead center is in body frame; the arch link frame is offset by the
            # anchor, so express the joint origin relative to the anchor.
            origin=Origin(xyz=_rel(center)),
            axis=ax,
            motion_limits=MotionLimits(effort=0.2, velocity=10.0),
        )


def _add_rooftop_spinner(model: ArticulatedObject, body, r: ResolvedToyCarConfig, mats: dict, info: _BodyInfo):
    ms = r.mechanism_scale
    xs = r.body_len / 0.150
    hs = r.deck_h / 0.048
    deck_z = info.deck_mount_z
    post_x = info.cockpit_x if r.body_form == "open_racer_cockpit" else -0.010 * xs
    # The pickup deck_mount_z is the bed-WALL top, but the bed centre is hollow,
    # so a collar there would float. Seat the pickup spinner on the cab roof
    # (a solid surface) instead. The wall-clearance gate in the spec is met by
    # moving the post forward over the cab rather than into the open bed.
    if r.body_form == "pickup_truck_bed":
        base_h = 0.022 * hs
        cab_h = 0.050 * hs
        deck_z = BODY_BOT_Z + base_h + cab_h
        post_x = 0.038 * xs  # cab centre
    elif r.body_form == "classic_car_driver":
        # The classic cabin + driver head rise above the deck at the rear; mount
        # the spinner FORWARD on the open front deck (hood) so the disc clears
        # the driver instead of sitting on top of it.
        post_x = 0.030 * xs
    post_y = 0.0
    collar_r = 0.010
    collar_h = 0.006
    post_r = 0.006
    post_h = 0.038 * ms
    post_top_z = deck_z + collar_h + post_h

    # Embed the collar downward so it penetrates the body solid even where the
    # local deck surface slopes below deck_z.
    collar_embed = 0.014
    collar_total_h = collar_h + collar_embed
    collar = CylinderGeometry(collar_r, collar_total_h, radial_segments=22)
    collar.translate(post_x, post_y, deck_z + collar_h / 2.0 - collar_embed / 2.0)
    body.visual(mesh_from_geometry(collar, "post_collar"), material=mats["body_dark"], name="post_collar", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"natural_wood_red", "bright_rainbow"} else "wood.painted_clean"))
    post = CylinderGeometry(post_r, post_h, radial_segments=16)
    post.translate(post_x, post_y, deck_z + collar_h + post_h / 2.0)
    body.visual(mesh_from_geometry(post, "spinner_post"), material=mats["body_dark"], name="spinner_post", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"natural_wood_red", "bright_rainbow"} else "wood.painted_clean"))

    num_blades = 4
    blade_reach = 0.024 * ms
    hub_r = 0.012
    hub_h = 0.006
    blade_w = 0.015 * ms
    blade_t = 0.005
    # Make each blade penetrate deep into the hub (inner edge well past the hub
    # centre) so the boolean union is a single solid that survives convex
    # decomposition in the connectivity check — otherwise the 4 blades decompose
    # into islands disconnected from the hub.
    blade_outer = blade_reach + 0.018 * ms
    blade_len = blade_outer + hub_r  # inner edge sits at -hub_r (through centre)
    blade_center = blade_outer - blade_len / 2.0

    hub = cq.Workplane("XY").circle(hub_r).extrude(hub_h).translate((0, 0, -hub_h / 2.0))
    for i in range(num_blades):
        angle_deg = i * (360.0 / num_blades)
        blade = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, angle_deg))
            .transformed(offset=(blade_center, 0, 0))
            .box(blade_len, blade_w, blade_t)
        )
        hub = hub.union(blade)
    try:
        hub = hub.edges("|Z").fillet(0.0015)
    except Exception:
        pass

    spinner = model.part("spinner_disc")
    spinner.visual(mesh_from_cadquery(hub, "disc_body"), material=mats["body"], name="disc_body", material_class_id=("wood.polished_varnished" if r.palette_style in {"natural_wood_red", "bright_rainbow"} else "wood.painted_clean"))
    blade_dot_mats = (mats["bead_a"], mats["wire"], mats["bead_b"], mats["bead_c"])
    for i in range(num_blades):
        angle = i * (2.0 * math.pi / num_blades)
        mx = blade_reach * math.cos(angle)
        my = blade_reach * math.sin(angle)
        dot = CylinderGeometry(0.004, 0.006, radial_segments=14)
        # Seat the dot so its lower half penetrates the blade top (z=blade_t/2)
        # — a grazing touch is not registered by the convex-decomposed check.
        dot.translate(mx, my, blade_t / 2.0)
        spinner.visual(
            mesh_from_geometry(dot, f"blade_dot_{i}"),
            material=blade_dot_mats[i % len(blade_dot_mats)],
            name=f"blade_dot_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    bore_cap = CylinderGeometry(0.007, 0.002, radial_segments=18)
    bore_cap.translate(0.0, 0.0, hub_h / 2.0 + 0.001)
    spinner.visual(mesh_from_geometry(bore_cap, "hub_bore_cap"), material=mats["black"], name="hub_bore_cap", material_class_id="plastic.opaque_generic")
    spinner.inertial = Inertial.from_geometry(Cylinder(0.048, 0.008), mass=0.015)

    model.articulation(
        "body_to_spinner",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=spinner,
        origin=Origin(xyz=(post_x, post_y, post_top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.3, velocity=15.0),
    )


def _add_steering_column(model: ArticulatedObject, body, r: ResolvedToyCarConfig, mats: dict, info: _BodyInfo):
    ms = r.mechanism_scale
    xs = r.body_len / 0.150
    hs = r.deck_h / 0.048
    deck_z = info.deck_mount_z
    tilt = math.radians(30)
    col_base_x = 0.020 * xs
    if r.body_form == "open_racer_cockpit":
        col_base_x = info.cockpit_x
    rim_r = 0.026 * ms
    cos_t = math.cos(tilt)
    sin_t = math.sin(tilt)

    # Local body-top height under the steering wheel, so the tilted wheel rim
    # clears the cab / cabin instead of dipping into it. For the pickup, mount
    # the column on the cab roof (a solid raised surface) rather than the bed.
    if r.body_form == "pickup_truck_bed":
        base_h = 0.022 * hs
        cab_h = 0.050 * hs
        deck_z = BODY_BOT_Z + base_h + cab_h
        col_base_x = 0.038 * xs  # cab centre
        local_top = deck_z
    elif r.body_form == "classic_car_driver":
        col_base_x = 0.042 * xs
        local_top = max(
            _classic_cabin_top_z(r),
            _classic_driver_head_z(r) + _CLASSIC_DRIVER_HEAD_R,
        )
    else:
        local_top = r.body_top_z

    # Column length: long enough that the wheel (radius rim_r, tilted) sits a
    # clear margin above the local body top. col_top_z = deck_z + cos*col_len,
    # require col_top_z - rim_r >= local_top + clearance.
    clearance = 0.006
    min_col_len = (local_top + rim_r + clearance - deck_z) / cos_t
    col_len = max(0.042 * ms, min_col_len)
    col_r = 0.006
    boss_r = 0.010
    boss_h = 0.005
    col_top_x = col_base_x - sin_t * col_len
    col_top_z = deck_z + cos_t * col_len
    col_mid_x = col_base_x - sin_t * col_len / 2.0
    col_mid_z = deck_z + cos_t * col_len / 2.0

    # Extend the boss DOWN into the body solid so it stays embedded even where
    # the local deck surface slopes below deck_z (classic hood / racer tail).
    embed = 0.016
    boss_total_h = boss_h + embed
    boss = CylinderGeometry(boss_r, boss_total_h, radial_segments=18)
    boss.translate(col_base_x, 0.0, deck_z + boss_h / 2.0 - embed / 2.0)
    body.visual(mesh_from_geometry(boss, "column_boss"), material=mats["body_dark"], name="column_boss", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"natural_wood_red", "bright_rainbow"} else "wood.painted_clean"))
    post = CylinderGeometry(col_r, col_len, radial_segments=14)
    post.rotate_y(-tilt)
    post.translate(col_mid_x, 0.0, col_mid_z)
    body.visual(mesh_from_geometry(post, "column_post"), material=mats["body_dark"], name="column_post", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"natural_wood_red", "bright_rainbow"} else "wood.painted_clean"))

    rim_r = 0.026 * ms
    tube_r = 0.004
    hub_r = 0.007
    hub_h = 0.010
    spoke_r = 0.003
    spoke_len = rim_r - hub_r
    spoke_offset = hub_r + spoke_len / 2.0
    wheel = TorusGeometry(rim_r, tube_r, radial_segments=14, tubular_segments=32)
    hub = CylinderGeometry(hub_r, hub_h, radial_segments=18)
    wheel.merge(hub)
    for i in range(4):
        angle = i * math.pi / 2.0
        spoke = CylinderGeometry(spoke_r, spoke_len, radial_segments=10)
        spoke.rotate_y(math.pi / 2.0)
        spoke.rotate_z(angle)
        spoke.translate(spoke_offset * math.cos(angle), spoke_offset * math.sin(angle), 0.0)
        wheel.merge(spoke)

    sw = model.part("steering_wheel")
    sw.visual(mesh_from_geometry(wheel, "steering_wheel_body"), material=mats["body_dark"], name="steering_wheel_body", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"natural_wood_red", "bright_rainbow"} else "wood.painted_clean"))
    marker = CylinderGeometry(0.003, 0.006, radial_segments=10)
    marker.translate(rim_r, 0.0, 0.0)
    sw.visual(mesh_from_geometry(marker, "steer_marker"), material=mats["accent"], name="steer_marker", material_class_id="plastic.opaque_glossy_molded")
    sw.inertial = Inertial.from_geometry(Cylinder(0.056, 0.012), mass=0.015)

    model.articulation(
        "body_to_steering",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=sw,
        origin=Origin(xyz=(col_top_x, 0.0, col_top_z), rpy=(0.0, -tilt, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.3, velocity=10.0),
    )


# --------------------------------------------------------------------------- #
# Materials + build.
# --------------------------------------------------------------------------- #


def _materials(model: ArticulatedObject, r: ResolvedToyCarConfig) -> dict:
    pal = r.palette
    return {
        key: model.material(f"toycar_{key}", rgba=rgba) for key, rgba in pal.items()
    }


def build_toy_car(
    config: ToyCarConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or ToyCarConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-toy_car-")))
    session = AssetSession(assets.root, mesh_subdir=assets.mesh_subdir)
    with activate_asset_session(session):
        model = ArticulatedObject(name=r.name, assets=assets)
        model.meta["adopted_source_ids"] = tuple(f"S{i}" for i in range(1, 11))
        model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]

        mats = _materials(model, r)
        body, info = _add_body(model, r, mats)
        _add_axle_pegs(body, r, mats)
        _add_wheels(model, body, r, mats)

        if r.deck_mechanism == "bead_maze_arch":
            _add_bead_maze_arch(model, body, r, mats, info)
        elif r.deck_mechanism == "rooftop_spinner":
            _add_rooftop_spinner(model, body, r, mats, info)
        else:
            _add_steering_column(model, body, r, mats, info)

        return model


def build_seeded_toy_car(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_toy_car(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Slot choices.
# --------------------------------------------------------------------------- #


def slot_choices_for_config(r: ResolvedToyCarConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("body_form", r.body_form),
        ("deck_mechanism", r.deck_mechanism),
        ("wheel_form", r.wheel_form),
        ("wheel_count", str(r.wheel_count)),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests.
# --------------------------------------------------------------------------- #


def _declare_overlap_allowances(ctx: TestContext, model: ArticulatedObject, r: ResolvedToyCarConfig):
    body = model.get_part("body")
    info = _body_info(r)
    wheel_elem = "wheel_body"

    # Each wheel seats over its body axle peg: the rim/tire body, the inner hub
    # (spoked form) and the outer hub cap all share volume with the peg tip by
    # design. Declare every wheel seat element against the peg.
    seat_elems = (wheel_elem, "hub", "hub_cap")
    for i, (axle_idx, _ys) in enumerate(r.wheel_specs):
        w = model.get_part(f"wheel_{i}")
        for se in seat_elems:
            ctx.allow_overlap(
                w,
                body,
                elem_a=se,
                elem_b=f"axle_{axle_idx}",
                reason="Wheel hub bore is intentionally seated over the body axle peg.",
            )

    if r.deck_mechanism == "bead_maze_arch":
        arch = model.get_part("wire_arch")
        ctx.allow_overlap(
            arch,
            body,
            elem_a="arch_wire",
            elem_b=info.block_elem,
            reason="Wire-arch feet are intentionally seated into the deck.",
        )
        ctx.expect_contact(arch, body, name="wire arch attached to body")
        for idx in range(3):
            bd = model.get_part(f"bead_{idx}")
            ctx.allow_overlap(
                bd,
                arch,
                elem_a="bead_disc",
                elem_b="arch_wire",
                reason="Bead is threaded onto the wire; disc bore intentionally overlaps the wire.",
            )
            ctx.expect_contact(bd, arch, name=f"bead_{idx} threaded on the wire")
    elif r.deck_mechanism == "rooftop_spinner":
        spinner = model.get_part("spinner_disc")
        ctx.allow_overlap(
            spinner,
            body,
            elem_a="disc_body",
            elem_b="spinner_post",
            reason="Spinner hub is seated over the post; disc bore intentionally overlaps the post.",
        )
        ctx.expect_contact(spinner, body, name="spinner seated on post")
    else:
        sw = model.get_part("steering_wheel")
        ctx.allow_overlap(
            sw,
            body,
            elem_a="steering_wheel_body",
            elem_b="column_post",
            reason="Steering wheel hub is seated over the tilted column top.",
        )
        ctx.expect_contact(sw, body, name="steering wheel seated on column")


def run_toy_car_tests(object_model: ArticulatedObject, config: ToyCarConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlap_allowances(ctx, object_model, r)

    body = object_model.get_part("body")
    part_names = {p.name for p in object_model.parts}
    info = _body_info(r)

    # ---- identity: wooden body present with the expected block element ----
    body_aabb = ctx.part_world_aabb(body)
    ctx.check(
        "body present and oriented along +X (car length)",
        body_aabb is not None and (body_aabb[1][0] - body_aabb[0][0]) > (body_aabb[1][1] - body_aabb[0][1]),
        details=f"body_aabb={body_aabb}",
    )

    head_elem = "bug_head" if r.body_form == "bug_face_beetle" else "driver_head"
    head_aabb = ctx.part_element_world_aabb(body, elem=head_elem)
    ctx.check(
        "character head is present and emerges above the body",
        head_aabb is not None and head_aabb[1][2] > info.deck_mount_z + 0.008,
        details=f"body_form={r.body_form}, head_elem={head_elem}, head_aabb={head_aabb}, deck={info.deck_mount_z}",
    )
    if r.body_form == "classic_car_driver":
        cabin_top_z = _classic_cabin_top_z(r)
        visible_h = (head_aabb[1][2] - cabin_top_z) if head_aabb else 0.0
        min_visible_h = 2.0 * _CLASSIC_DRIVER_HEAD_R * _CLASSIC_DRIVER_MIN_VISIBLE_FRACTION
        ctx.check(
            "classic driver head visibly clears the cabin roof",
            head_aabb is not None and visible_h >= min_visible_h,
            details=f"visible_h={visible_h:.4f}, min_visible_h={min_visible_h:.4f}, cabin_top_z={cabin_top_z:.4f}, head_aabb={head_aabb}",
        )

    # ---- wheel_count multiplicity: correct number of wheels ----
    wheel_parts = [nm for nm in part_names if nm.startswith("wheel_")]
    ctx.check(
        "wheel_count matches multiplicity",
        len(wheel_parts) == r.wheel_count,
        details=f"wheels={sorted(wheel_parts)}, expected={r.wheel_count}",
    )

    # ---- every wheel reaches the ground (landing constraint) ----
    for i in range(r.wheel_count):
        w = object_model.get_part(f"wheel_{i}")
        w_aabb = ctx.part_world_aabb(w)
        ctx.check(
            f"wheel_{i} reaches the ground",
            w_aabb is not None and w_aabb[0][2] <= 0.004,
            details=f"wheel_{i} min_z={w_aabb[0][2] if w_aabb else None}",
        )

    # ---- centerline parity: odd N has exactly one centerline wheel, even N none ----
    centerline_count = sum(1 for _ai, ys in r.wheel_specs if ys == 0.0)
    if r.wheel_count % 2 == 1:
        ctx.check(
            "odd wheel_count has exactly one centerline wheel",
            centerline_count == 1,
            details=f"centerline_count={centerline_count}",
        )
    else:
        ctx.check(
            "even wheel_count has no centerline wheel",
            centerline_count == 0,
            details=f"centerline_count={centerline_count}",
        )

    # ---- each wheel rolls about its Y axle (marker sweeps in X/Z) ----
    for i in range(r.wheel_count):
        w = object_model.get_part(f"wheel_{i}")
        joint = object_model.get_articulation(f"axle_wheel_{i}")
        ctx.check(
            f"wheel_{i} is a CONTINUOUS roll about +Y",
            joint.articulation_type == ArticulationType.CONTINUOUS and abs(joint.axis[1]) > 0.99,
            details=f"type={joint.articulation_type}, axis={joint.axis}",
        )
        m0 = ctx.part_element_world_aabb(w, elem="spin_marker")
        with ctx.pose({joint: math.pi / 2.0}):
            m1 = ctx.part_element_world_aabb(w, elem="spin_marker")
        c0 = ((m0[0][0] + m0[1][0]) / 2.0, (m0[0][2] + m0[1][2]) / 2.0)
        c1 = ((m1[0][0] + m1[1][0]) / 2.0, (m1[0][2] + m1[1][2]) / 2.0)
        moved = math.hypot(c1[0] - c0[0], c1[1] - c0[1])
        ctx.check(
            f"wheel_{i} rolls about its axle (marker moves)",
            moved > 0.006,
            details=f"wheel_{i} marker moved={moved:.4f}",
        )

    # ---- deck mechanism: structure + motion per slot ----
    if r.deck_mechanism == "bead_maze_arch":
        arch = object_model.get_part("wire_arch")
        arch_joint = object_model.get_articulation("body_to_arch")
        ctx.check(
            "bead-maze arch is FIXED to the body",
            arch_joint.articulation_type == ArticulationType.FIXED,
            details=f"type={arch_joint.articulation_type}",
        )
        arch_aabb = ctx.part_world_aabb(arch)
        ctx.check(
            "wire arch rises above the deck",
            arch_aabb is not None and arch_aabb[1][2] > info.deck_mount_z + 0.015,
            details=f"arch top_z={arch_aabb[1][2] if arch_aabb else None}, deck={info.deck_mount_z}",
        )
        bead = object_model.get_part("bead_1")
        bjoint = object_model.get_articulation("arch_to_bead_1")
        ctx.check(
            "bead spins (CONTINUOUS)",
            bjoint.articulation_type == ArticulationType.CONTINUOUS,
            details=f"type={bjoint.articulation_type}",
        )
        b0 = ctx.part_world_aabb(bead)
        with ctx.pose({bjoint: math.pi / 2.0}):
            b1 = ctx.part_world_aabb(bead)
        d0 = (b0[1][0] - b0[0][0], b0[1][1] - b0[0][1], b0[1][2] - b0[0][2])
        d1 = (b1[1][0] - b1[0][0], b1[1][1] - b1[0][1], b1[1][2] - b1[0][2])
        delta = abs(d0[0] - d1[0]) + abs(d0[1] - d1[1]) + abs(d0[2] - d1[2])
        ctx.check(
            "bead spins about the wire (extents change)",
            delta > 0.002,
            details=f"delta={delta:.4f}",
        )
    elif r.deck_mechanism == "rooftop_spinner":
        spinner = object_model.get_part("spinner_disc")
        sjoint = object_model.get_articulation("body_to_spinner")
        ctx.check(
            "spinner is CONTINUOUS about +Z",
            sjoint.articulation_type == ArticulationType.CONTINUOUS and abs(sjoint.axis[2]) > 0.99,
            details=f"type={sjoint.articulation_type}, axis={sjoint.axis}",
        )
        s0 = ctx.part_element_world_aabb(spinner, elem="blade_dot_0")
        with ctx.pose({sjoint: math.pi / 2.0}):
            s1 = ctx.part_element_world_aabb(spinner, elem="blade_dot_0")
        c0 = ((s0[0][0] + s0[1][0]) / 2.0, (s0[0][1] + s0[1][1]) / 2.0)
        c1 = ((s1[0][0] + s1[1][0]) / 2.0, (s1[0][1] + s1[1][1]) / 2.0)
        moved = math.hypot(c1[0] - c0[0], c1[1] - c0[1])
        ctx.check(
            "spinner blade sweeps when spun",
            moved > 0.006,
            details=f"blade moved={moved:.4f}",
        )
        spin_aabb = ctx.part_world_aabb(spinner)
        ctx.check(
            "spinner sits above the deck",
            spin_aabb is not None and spin_aabb[0][2] >= info.deck_mount_z - 0.002,
            details=f"spinner min_z={spin_aabb[0][2] if spin_aabb else None}, deck={info.deck_mount_z}",
        )
    else:
        sw = object_model.get_part("steering_wheel")
        stjoint = object_model.get_articulation("body_to_steering")
        ctx.check(
            "steering wheel is CONTINUOUS about the tilted column",
            stjoint.articulation_type == ArticulationType.CONTINUOUS,
            details=f"type={stjoint.articulation_type}",
        )
        m0 = ctx.part_element_world_aabb(sw, elem="steer_marker")
        with ctx.pose({stjoint: math.pi / 2.0}):
            m1 = ctx.part_element_world_aabb(sw, elem="steer_marker")
        cen0 = tuple((m0[0][k] + m0[1][k]) / 2.0 for k in range(3))
        cen1 = tuple((m1[0][k] + m1[1][k]) / 2.0 for k in range(3))
        moved = math.sqrt(sum((cen1[k] - cen0[k]) ** 2 for k in range(3)))
        ctx.check(
            "steering wheel turns (marker moves)",
            moved > 0.006,
            details=f"steer marker moved={moved:.4f}",
        )
        sw_aabb = ctx.part_world_aabb(sw)
        ctx.check(
            "steering wheel sits above the deck",
            sw_aabb is not None and sw_aabb[1][2] > info.deck_mount_z,
            details=f"steer top_z={sw_aabb[1][2] if sw_aabb else None}",
        )
        if r.body_form == "classic_car_driver":
            head_aabb = ctx.part_element_world_aabb(body, elem="driver_head")
            ctx.check(
                "classic steering wheel clears the driver head",
                sw_aabb is not None
                and head_aabb is not None
                and sw_aabb[0][2] >= head_aabb[1][2] + 0.002,
                details=f"steer_min_z={sw_aabb[0][2] if sw_aabb else None}, head_top_z={head_aabb[1][2] if head_aabb else None}",
            )
            sw_elems, _sw_part, _sw_elem, sw_err = ctx._resolve_exact_elements(
                sw, elem="steering_wheel_body", kind_prefix="elem_a"
            )
            head_elems, _head_part, _head_elem, head_err = ctx._resolve_exact_elements(
                body, elem="driver_head", kind_prefix="elem_b"
            )
            if sw_err or head_err or sw_elems is None or head_elems is None:
                ctx.check(
                    "classic steering wheel exact geometry is available for head clearance",
                    False,
                    details="; ".join(item for item in (sw_err, head_err) if item),
                )
            else:
                min_distance, collided = ctx._exact_pair_distance(sw_elems, head_elems)
                ctx.check(
                    "classic steering wheel does not collide with driver head",
                    (not collided) and min_distance >= 0.001,
                    details=f"min_distance={min_distance:.4g}, collided={collided}",
                )

    return ctx.report()
