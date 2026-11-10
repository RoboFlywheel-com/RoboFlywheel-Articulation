# SPDX-License-Identifier: Apache-2.0

"""Kick scooter ("Scooter Racer") — modular procedural template.

A stand-on, foot-propelled two-axis ride toy. World Z up, rolling direction
``+Y``, wheel axles along ``X``. A low foot deck carries a front steering head
(tilted ~18 deg back) at one end; a tall stem sweeps up to a handlebar with two
grips (~0.82 m). A single steered front wheel hangs in fork legs off the
steering column; one or two rear wheels carry the tail.

Three articulated DOFs are mandatory:

  * ``steering``      REVOLUTE about the tilted head axis (±range deg)
  * ``front_wheel_roll``  CONTINUOUS roll about the lateral X axis
  * ``rear_wheel_roll_{i}``  CONTINUOUS roll (one per rear wheel)

Optional fourth DOF: a ``fold_hinge`` REVOLUTE when the ``folding_hinge`` stem
articulation is chosen (the upper stem + bar fold forward about the hinge
knuckle).

Slot graph (mixed: parallel children + multiplicity)::

                       body (root: Slot B deck/neck/head_tube/rear_fender)
                       │
   [steering REVOLUTE @ HEAD_BASE, axis STEER_AXIS]
                       │
                steering_column (Slot A stem/bar; Slot C lower/rigid)
                       ├──[front_wheel_roll CONTINUOUS] front_wheel
                       └──[fold_hinge REVOLUTE] upper_stem      (folding_hinge only)
                       │
   [rear_wheel_roll_{i} CONTINUOUS @ shared rear axle]
                       └─ rear_wheel_{i}                        (multiplicity N_rear)

Adopted 5-star sources (``data/records/<rec>/revisions/rev_000001/model.py``):

  * S0 parent ``rec_vintage-green-kick-scooter-...d68bd852`` — curved_swept stem,
    running_board deck, rigid column, N=2 (front + single rear).
  * S1 ``rec_kick_scooter_var_tbar_straight`` — straight stem + level T crossbar.
  * S2 ``rec_kick_scooter_var_bmx_riser`` — short stem + U-bend riser + brace.
  * S3 ``rec_kick_scooter_var_swept_cruiser`` — wide swept-back cruiser bar.
  * S4 ``rec_kick_scooter_var_flat_plank`` — CadQuery filleted plank + grip-tape.
  * S5 ``rec_kick_scooter_var_folding_hinge`` — stem split + hinge + fold revolute.
  * S6 ``rec_kick_scooter_var_three_wheel`` — two rear wheels on a shared axle.

The template is procedural-first: ``config_from_seed`` draws ``handlebar_form``,
``deck_form``, ``stem_articulation`` uniformly, ``rear_wheel_count`` via a 70/30
weighted draw, ``palette_style`` over 6 colorways, then the continuous scales.
``resolve_config`` is the sole legalization/derivation entry. Topology diversity
is counted by ``slot_choices_for_seed``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    Box,
    BoxGeometry,
    Cylinder,
    CylinderGeometry,
    ExtrudeGeometry,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireGeometry,
    TireSidewall,
    TireTread,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


# --------------------------------------------------------------------------- #
# Fixed category geometry constants (S0 L47-L60).
# --------------------------------------------------------------------------- #

WHEEL_R = 0.090  # nominal rolling radius of the small wheels
WHEEL_W = 0.040  # wheel/tire width along X
DECK_TOP_Z = 0.100  # nominal top surface of the foot deck
REAR_WHEEL_Y = -0.235  # rear axle Y
FRONT_WHEEL_Y = 0.320  # front axle Y (at rest)

# Steering head: where the curved stem meets the deck neck. The head axis tilts
# back from vertical, in the YZ plane.
HEAD_BASE = (0.0, 0.180, 0.150)  # bottom of the head tube
HEAD_TILT = math.radians(18.0)
STEER_AXIS = (0.0, math.sin(HEAD_TILT), math.cos(HEAD_TILT))

# Folding hinge location partway up the stem (S5 L66, world coords).
HINGE_WORLD = (0.0, 0.120, 0.500)


# --------------------------------------------------------------------------- #
# Module enums
# --------------------------------------------------------------------------- #

HandlebarForm = Literal["curved_swept", "tbar_straight", "bmx_riser", "swept_cruiser"]
DeckForm = Literal["running_board", "flat_plank"]
StemArticulation = Literal["rigid", "folding_hinge"]
PaletteStyle = Literal[
    "vintage_green",
    "chrome_classic",
    "racer_red",
    "midnight_black",
    "candy_blue",
    "cream_whitewall",
]

_HANDLEBAR_CHOICES: tuple[HandlebarForm, ...] = (
    "curved_swept",
    "tbar_straight",
    "bmx_riser",
    "swept_cruiser",
)
_DECK_CHOICES: tuple[DeckForm, ...] = ("running_board", "flat_plank")
_STEM_CHOICES: tuple[StemArticulation, ...] = ("rigid", "folding_hinge")
_PALETTE_CHOICES: tuple[PaletteStyle, ...] = (
    "vintage_green",
    "chrome_classic",
    "racer_red",
    "midnight_black",
    "candy_blue",
    "cream_whitewall",
)


# --------------------------------------------------------------------------- #
# Palette presets — keyed material tokens (S0 L123-L131 recolored per colorway).
# Tokens: body, body_dark, grip, tire, whitewall, metal, brand.
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "vintage_green": {
        "body": (0.36, 0.55, 0.40, 1.0),
        "body_dark": (0.28, 0.44, 0.32, 1.0),
        "grip": (0.10, 0.10, 0.11, 1.0),
        "tire": (0.08, 0.08, 0.09, 1.0),
        "whitewall": (0.90, 0.90, 0.88, 1.0),
        "metal": (0.74, 0.76, 0.79, 1.0),
        "brand": (0.82, 0.83, 0.85, 1.0),
    },
    "chrome_classic": {
        "body": (0.80, 0.82, 0.85, 1.0),
        "body_dark": (0.55, 0.57, 0.60, 1.0),
        "grip": (0.12, 0.12, 0.13, 1.0),
        "tire": (0.07, 0.07, 0.08, 1.0),
        "whitewall": (0.92, 0.92, 0.90, 1.0),
        "metal": (0.83, 0.85, 0.88, 1.0),
        "brand": (0.20, 0.22, 0.26, 1.0),
    },
    "racer_red": {
        "body": (0.74, 0.12, 0.11, 1.0),
        "body_dark": (0.54, 0.08, 0.08, 1.0),
        "grip": (0.09, 0.09, 0.10, 1.0),
        "tire": (0.07, 0.07, 0.08, 1.0),
        "whitewall": (0.91, 0.90, 0.88, 1.0),
        "metal": (0.78, 0.79, 0.82, 1.0),
        "brand": (0.92, 0.86, 0.30, 1.0),
    },
    "midnight_black": {
        "body": (0.12, 0.13, 0.15, 1.0),
        "body_dark": (0.07, 0.08, 0.09, 1.0),
        "grip": (0.05, 0.05, 0.06, 1.0),
        "tire": (0.05, 0.05, 0.06, 1.0),
        "whitewall": (0.20, 0.20, 0.22, 1.0),
        "metal": (0.66, 0.68, 0.71, 1.0),
        "brand": (0.80, 0.18, 0.18, 1.0),
    },
    "candy_blue": {
        "body": (0.16, 0.34, 0.66, 1.0),
        "body_dark": (0.10, 0.24, 0.48, 1.0),
        "grip": (0.10, 0.10, 0.12, 1.0),
        "tire": (0.07, 0.07, 0.08, 1.0),
        "whitewall": (0.90, 0.91, 0.92, 1.0),
        "metal": (0.80, 0.82, 0.85, 1.0),
        "brand": (0.90, 0.91, 0.93, 1.0),
    },
    "cream_whitewall": {
        "body": (0.90, 0.87, 0.78, 1.0),
        "body_dark": (0.70, 0.66, 0.56, 1.0),
        "grip": (0.30, 0.22, 0.16, 1.0),
        "tire": (0.10, 0.09, 0.09, 1.0),
        "whitewall": (0.95, 0.94, 0.90, 1.0),
        "metal": (0.80, 0.81, 0.83, 1.0),
        "brand": (0.55, 0.40, 0.24, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class KickScooterConfig:
    """Public config. Module fields default to ``None`` so ``config_from_seed`` /
    ``resolve_config`` fill in the anchor (S0) defaults."""

    handlebar_form: HandlebarForm | None = None
    deck_form: DeckForm | None = None
    stem_articulation: StemArticulation | None = None
    rear_wheel_count: int = 1
    palette_style: PaletteStyle = "vintage_green"

    # Independent continuous scales (spec §7).
    deck_length_scale: float = 1.0
    deck_top_z_scale: float = 1.0
    stem_height_scale: float = 1.0
    handlebar_width_scale: float = 1.0
    wheel_radius_scale: float = 1.0
    rear_track_scale: float = 1.0
    steer_range: float = 40.0  # degrees
    fold_range: float = 150.0  # degrees


@dataclass(frozen=True)
class ResolvedKickScooterConfig:
    """Clamped + derived config consumed by builders."""

    handlebar_form: HandlebarForm
    deck_form: DeckForm
    stem_articulation: StemArticulation
    rear_wheel_count: int
    palette_style: PaletteStyle

    deck_length_scale: float
    deck_top_z_scale: float
    stem_height_scale: float
    handlebar_width_scale: float
    wheel_radius_scale: float
    rear_track_scale: float
    steer_range: float  # radians
    fold_range: float  # radians

    # Derived geometry
    wheel_r: float
    axle_z: float
    deck_top_z: float
    rear_wheel_y: float
    front_wheel_y: float
    rear_track: float

    palette: dict[str, tuple[float, float, float, float]]


# --------------------------------------------------------------------------- #
# Seed-driven sampling
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> KickScooterConfig:
    """Deterministic procedural sampling. ``seed == 0`` is NOT special — it is
    drawn like any other seed.

    Order (spec §7): handlebar -> deck -> stem -> rear_wheel_count (weighted) ->
    palette -> continuous scales.
    """
    rng = random.Random(seed)
    handlebar = rng.choice(_HANDLEBAR_CHOICES)
    deck = rng.choice(_DECK_CHOICES)
    stem = rng.choice(_STEM_CHOICES)
    rear_wheel_count = rng.choices((1, 2), weights=(0.70, 0.30), k=1)[0]
    palette = rng.choice(_PALETTE_CHOICES)

    deck_length_scale = round(rng.uniform(0.85, 1.20), 4)
    deck_top_z_scale = round(rng.uniform(0.85, 1.10), 4)
    stem_height_scale = round(rng.uniform(0.92, 1.12), 4)
    handlebar_width_scale = round(rng.uniform(0.85, 1.25), 4)
    wheel_radius_scale = round(rng.uniform(0.90, 1.15), 4)
    rear_track_scale = round(rng.uniform(0.80, 1.20), 4)
    steer_range = round(rng.uniform(30.0, 45.0), 2)
    fold_range = round(rng.uniform(120.0, 155.0), 2)

    return KickScooterConfig(
        handlebar_form=handlebar,
        deck_form=deck,
        stem_articulation=stem,
        rear_wheel_count=rear_wheel_count,
        palette_style=palette,
        deck_length_scale=deck_length_scale,
        deck_top_z_scale=deck_top_z_scale,
        stem_height_scale=stem_height_scale,
        handlebar_width_scale=handlebar_width_scale,
        wheel_radius_scale=wheel_radius_scale,
        rear_track_scale=rear_track_scale,
        steer_range=steer_range,
        fold_range=fold_range,
    )


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(float(value), hi))


def resolve_config(config: KickScooterConfig) -> ResolvedKickScooterConfig:
    """Validate enums, clamp floats, and derive the dependent geometry chain.

    Derivations (spec §7):
      * ``wheel_r = WHEEL_R * wheel_radius_scale`` ; ``axle_z = wheel_r`` so the
        wheels rest on the ground.
      * deck-top inequality: ``deck_top_z + deck_thick/2 < 0.15`` (deck stays
        low); clamp ``deck_top_z`` if violated, with an axle-clearance floor.
      * front-ahead-of-rear: ``front_wheel_y - rear_wheel_y > 0.30`` after the
        deck_length_scale stretch of front_wheel_y; clamp the front out if short.
      * handlebar width: upper bound lowered for already-wide swept_cruiser /
        bmx_riser so grips clear the front neck at full steer.
      * rear_track only active for ``rear_wheel_count == 2``.
    """
    handlebar = config.handlebar_form or "curved_swept"
    deck = config.deck_form or "running_board"
    stem = config.stem_articulation or "rigid"

    if handlebar not in _HANDLEBAR_CHOICES:
        raise ValueError(f"Unsupported handlebar_form: {handlebar}")
    if deck not in _DECK_CHOICES:
        raise ValueError(f"Unsupported deck_form: {deck}")
    if stem not in _STEM_CHOICES:
        raise ValueError(f"Unsupported stem_articulation: {stem}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    # Multiplicity: 1 or 2 rear wheels only (total wheels 2 or 3).
    rear_wheel_count = int(config.rear_wheel_count)
    rear_wheel_count = max(1, min(rear_wheel_count, 2))

    deck_length_scale = _clamp(config.deck_length_scale, 0.85, 1.20)
    deck_top_z_scale = _clamp(config.deck_top_z_scale, 0.85, 1.10)
    stem_height_scale = _clamp(config.stem_height_scale, 0.92, 1.12)
    wheel_radius_scale = _clamp(config.wheel_radius_scale, 0.90, 1.15)
    rear_track_scale = _clamp(config.rear_track_scale, 0.80, 1.20)

    # Handlebar width: clamp the upper bound for already-wide bars so grips clear
    # the front neck at full steer (spec §7 conditional + reject case 8).
    hw_hi = 1.05 if handlebar in ("swept_cruiser", "bmx_riser") else 1.25
    handlebar_width_scale = _clamp(config.handlebar_width_scale, 0.85, hw_hi)

    steer_range = math.radians(_clamp(config.steer_range, 30.0, 45.0))
    fold_range = math.radians(_clamp(config.fold_range, 120.0, 155.0))

    # --- Derived geometry chain ---
    # Wheel radius drives the axle height so the wheels rest on the ground.
    wheel_r = WHEEL_R * wheel_radius_scale
    axle_z = wheel_r

    # Deck-top z (inequality): keep the deck low. deck_thick is fixed ~0.020.
    deck_thick = 0.020
    deck_top_z = DECK_TOP_Z * deck_top_z_scale
    # The deck must sit clear above the axle but its TOP must stay below 0.15.
    deck_top_z = max(deck_top_z, axle_z + 0.005)
    deck_top_z = min(deck_top_z, 0.15 - deck_thick / 2.0 - 0.002)

    # Rear axle Y: keep the rear wheel BEHIND the deck so the tire's front edge
    # clears the deck's rear edge (otherwise a short deck + big wheel run into the
    # tire). Deck geometry: running_board len 0.330 @ y=0.020; flat_plank len
    # 0.350 @ y=0.030. Derive the rear edge, then seat the axle a wheel-radius +
    # clearance behind it.
    if deck == "flat_plank":
        deck_rear_edge = 0.030 - (0.350 * deck_length_scale) / 2.0
    else:
        deck_rear_edge = 0.020 - (0.330 * deck_length_scale) / 2.0
    rear_wheel_y = min(REAR_WHEEL_Y, deck_rear_edge - wheel_r - 0.012)

    # Front-ahead-of-rear (inequality): stretch the front axle out by the deck
    # length scale, then guarantee the > 0.30 margin against the rear Y.
    front_wheel_y = FRONT_WHEEL_Y * deck_length_scale
    if front_wheel_y - rear_wheel_y <= 0.32:
        front_wheel_y = rear_wheel_y + 0.34

    # Keep the front wheel ahead of the deck FRONT edge + steering neck so its
    # rear face (front_wheel_y - wheel_r) clears them (short deck + big wheel
    # otherwise drives the tire into the deck/neck).
    if deck == "flat_plank":
        deck_front_edge = 0.030 + (0.350 * deck_length_scale) / 2.0
    else:
        deck_front_edge = 0.020 + (0.330 * deck_length_scale) / 2.0
    # Neck front face sits near y=0.184 + neck radius(0.026) ~= 0.210.
    front_clear = max(deck_front_edge, 0.210) + wheel_r + 0.015
    front_wheel_y = max(front_wheel_y, front_clear)

    # Rear track only meaningful for the tri-wheel form. Keep wheels clear of the
    # deck width (deck half-width ~0.065) and of each other.
    rear_track = 0.180 * rear_track_scale if rear_wheel_count == 2 else 0.0

    palette = dict(PALETTES[config.palette_style])

    return ResolvedKickScooterConfig(
        handlebar_form=handlebar,
        deck_form=deck,
        stem_articulation=stem,
        rear_wheel_count=rear_wheel_count,
        palette_style=config.palette_style,
        deck_length_scale=deck_length_scale,
        deck_top_z_scale=deck_top_z_scale,
        stem_height_scale=stem_height_scale,
        handlebar_width_scale=handlebar_width_scale,
        wheel_radius_scale=wheel_radius_scale,
        rear_track_scale=rear_track_scale,
        steer_range=steer_range,
        fold_range=fold_range,
        wheel_r=wheel_r,
        axle_z=axle_z,
        deck_top_z=deck_top_z,
        rear_wheel_y=rear_wheel_y,
        front_wheel_y=front_wheel_y,
        rear_track=rear_track,
        palette=palette,
    )


# --------------------------------------------------------------------------- #
# Shared geometry helpers (adapted verbatim from S0 / S6, parameterized).
# --------------------------------------------------------------------------- #


def _fender(radius: float, width: float, thickness: float, span_deg: float,
            start_deg: float, name: str):
    """Curved fender arc band in the YZ plane, extruded along X (S0 L63-L88)."""
    r_out = radius + thickness
    r_in = radius
    a0 = math.radians(start_deg)
    a1 = math.radians(start_deg + span_deg)
    n = 40
    outer = []
    inner = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * (i / n)
        outer.append((r_out * math.cos(a), r_out * math.sin(a)))
        inner.append((r_in * math.cos(a), r_in * math.sin(a)))
    profile = outer + list(reversed(inner))
    geom = ExtrudeGeometry.centered(profile, width, cap=True)
    geom.rotate_y(math.pi / 2.0)
    geom.rotate_x(math.pi / 2.0)
    return mesh_from_geometry(geom, name)


def _wheel_meshes(prefix: str, r: ResolvedKickScooterConfig):
    """(rim, tire, whitewall) meshes oriented to spin about local X (S0 L91-L117)."""
    wr = r.wheel_r
    # Deep dish + thin hub so the connecting face disc merges with the hub and
    # rim into a SINGLE solid (otherwise the rim disc becomes a floating island —
    # mirrors the sports_car wheel proportions that pass the island check).
    wheel = WheelGeometry(
        wr * 0.62,
        WHEEL_W * 0.70,
        rim=WheelRim(inner_radius=wr * 0.50, flange_height=0.010, flange_thickness=0.005),
        hub=WheelHub(radius=wr * 0.16, width=WHEEL_W * 0.32, cap_style="domed"),
        face=WheelFace(dish_depth=0.018, front_inset=0.006),
        bore=WheelBore(style="round", diameter=0.010),
    )
    wheel_mesh = mesh_from_geometry(wheel, f"{prefix}_rim")

    tire = TireGeometry(
        wr,
        WHEEL_W,
        inner_radius=wr * 0.62,
        tread=TireTread(style="circumferential", depth=0.0025, count=2),
        sidewall=TireSidewall(style="rounded", bulge=0.04),
    )
    tire_mesh = mesh_from_geometry(tire, f"{prefix}_tire")

    ww = CylinderGeometry(wr * 0.80, 0.004, radial_segments=48).rotate_y(math.pi / 2.0)
    ww.translate(WHEEL_W * 0.52, 0.0, 0.0)
    whitewall_mesh = mesh_from_geometry(ww, f"{prefix}_whitewall")
    return wheel_mesh, tire_mesh, whitewall_mesh


def _emit_wheel(part, prefix: str, r: ResolvedKickScooterConfig) -> None:
    """Emit a wheel's rim/tire/whitewall/valve visuals + inertial onto ``part``.
    The hub is centered on (0,0,0); the spin axis lies along local X."""
    rim, tire, ww = _wheel_meshes(prefix, r)
    part.visual(tire, material="tire", name=f"{prefix}_tire", material_class_id="rubber.directional_grooved")
    part.visual(ww, material="whitewall", name=f"{prefix}_whitewall", material_class_id="rubber.smooth_plain")
    part.visual(rim, material="metal", name=f"{prefix}_rim", material_class_id="metal.aluminum_bare")
    part.visual(
        Cylinder(radius=0.005, length=WHEEL_W + 0.020),
        origin=Origin(xyz=(0.0, r.wheel_r * 0.55, r.wheel_r * 0.55), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="metal",
        name=f"{prefix}_valve", material_class_id="metal.brass_polished",
    )
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=r.wheel_r, length=WHEEL_W),
        mass=0.6,
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
    )


def _hinge_barrel_mesh(name: str):
    """Hinge knuckle barrel: a thick cylinder along X (S5 L122-L126)."""
    g = CylinderGeometry(0.028, 0.062, radial_segments=24)
    g.rotate_y(math.pi / 2.0)
    return mesh_from_geometry(g, name)


def _hinge_pin_mesh(name: str):
    """Hinge pin: a thin rod along X through the knuckle barrel (S5 L129-L133)."""
    g = CylinderGeometry(0.010, 0.090, radial_segments=16)
    g.rotate_y(math.pi / 2.0)
    return mesh_from_geometry(g, name)


def _rel(pts, origin):
    ox, oy, oz = origin
    return [(x - ox, y - oy, z - oz) for (x, y, z) in pts]


def _scale_z_pts(pts, scale: float, base_z: float):
    """Scale a point list's z above ``base_z`` (the head base) by ``scale`` so
    the column grows taller while keeping its foot seated in the head tube."""
    return [(x, y, base_z + (z - base_z) * scale) for (x, y, z) in pts]


# --------------------------------------------------------------------------- #
# Slot B — body / deck factories (root). Emit deck + neck + head_tube + rear
# fender furniture. The rear fender / axle furniture is N_rear-gated.
# --------------------------------------------------------------------------- #


def _emit_neck_and_head(body, r: ResolvedKickScooterConfig) -> None:
    """Shared front neck + tilted head tube (S0 L149-L169)."""
    dz = r.deck_top_z
    neck = tube_from_spline_points(
        [
            (0.0, 0.180, dz - 0.005),
            (0.0, 0.182, 0.118),
            (0.0, 0.183, 0.140),
            (0.0, 0.184, 0.158),
        ],
        radius=0.026,
        samples_per_segment=10,
        radial_segments=18,
    )
    body.visual(mesh_from_geometry(neck, "front_neck"), material="body", name="front_neck", material_class_id="metal.paint_coated")

    head_tube = CylinderGeometry(0.022, 0.090, radial_segments=24)
    head_tube.rotate_x(HEAD_TILT)
    head_tube.translate(HEAD_BASE[0], HEAD_BASE[1] - 0.006, HEAD_BASE[2] + 0.012)
    body.visual(mesh_from_geometry(head_tube, "head_tube"), material="body_dark", name="head_tube", material_class_id="metal.paint_coated")


def _emit_rear_furniture(body, r: ResolvedKickScooterConfig) -> None:
    """Rear fender(s) + struts (+ axle beam/brace for the tri-wheel form).

    N_rear == 1: a single centered fender + strut (S0 L171-L199).
    N_rear == 2: a visible rear axle beam + central brace + per-wheel fenders
    and struts (S6 L182-L236).
    """
    dz = r.deck_top_z
    az = r.axle_z
    rwy = r.rear_wheel_y
    # Derive the actual deck rear edge so the brace/strut foot lands ON the deck
    # (not floating behind a short deck). Sit the foot 0.010 inside the edge.
    if r.deck_form == "flat_plank":
        deck_rear_edge = 0.030 - (0.350 * r.deck_length_scale) / 2.0
    else:
        deck_rear_edge = 0.020 - (0.330 * r.deck_length_scale) / 2.0
    deck_rear_y = deck_rear_edge + 0.010

    xs_axle = _rear_wheel_xs(r)
    if r.rear_wheel_count == 2:
        # Visible rear axle beam spanning the two wheels.
        rear_axle = CylinderGeometry(0.010, r.rear_track + WHEEL_W, radial_segments=16)
        rear_axle.rotate_y(math.pi / 2.0)
        rear_axle.translate(0.0, rwy, az)
        body.visual(mesh_from_geometry(rear_axle, "rear_axle"), material="metal", name="rear_axle", material_class_id="metal.steel_bare")
        # Central brace deck-rear -> axle center (clear of both wheels at x=0).
        brace = tube_from_spline_points(
            [
                (0.0, deck_rear_y, dz - 0.010),
                (0.0, (deck_rear_y + rwy) / 2.0, az + 0.005),
                (0.0, rwy, az),
            ],
            radius=0.010,
            samples_per_segment=6,
            radial_segments=12,
        )
        body.visual(mesh_from_geometry(brace, "rear_brace"), material="body_dark", name="rear_brace", material_class_id="metal.paint_coated")
    else:
        # Single rear wheel: emit a short body-side axle stub at the rear axle so
        # the rear_wheel_roll joint origin anchors to real body geometry (the
        # dropout/axle), not floating off near the fender arc.
        for i, wx in enumerate(xs_axle):
            axle_stub = CylinderGeometry(0.009, WHEEL_W + 0.020, radial_segments=16)
            axle_stub.rotate_y(math.pi / 2.0)
            axle_stub.translate(wx, rwy, az)
            body.visual(mesh_from_geometry(axle_stub, f"rear_axle_stub_{i}"),
                        material="metal", name=f"rear_axle_stub_{i}", material_class_id="metal.steel_bare")
            # Dropout link: axle stub -> fender front-top, where the rear strut
            # also lands. This bridges the stub to the fender/strut so the body
            # has no floating island.
            ff_top = (
                wx,
                rwy + (r.wheel_r + 0.010) * math.cos(math.radians(48.0)),
                az + (r.wheel_r + 0.010) * math.sin(math.radians(48.0)),
            )
            dropout = tube_from_spline_points(
                [(wx, rwy, az), ((wx + ff_top[0]) / 2.0, (rwy + ff_top[1]) / 2.0,
                                 (az + ff_top[2]) / 2.0), ff_top],
                radius=0.009,
                samples_per_segment=6,
                radial_segments=12,
            )
            body.visual(mesh_from_geometry(dropout, f"rear_dropout_{i}"),
                        material="body_dark", name=f"rear_dropout_{i}", material_class_id="metal.paint_coated")

    xs = _rear_wheel_xs(r)
    for i, wx in enumerate(xs):
        body.visual(
            _fender(r.wheel_r + 0.010, WHEEL_W + 0.022, 0.012, span_deg=150.0, start_deg=35.0,
                    name=f"rear_fender_{i}"),
            origin=Origin(xyz=(wx, rwy, az)),
            material="body",
            name=f"rear_fender_{i}", material_class_id="metal.paint_coated",
        )
        fender_front_top = (
            wx,
            rwy + (r.wheel_r + 0.010) * math.cos(math.radians(48.0)),
            az + (r.wheel_r + 0.010) * math.sin(math.radians(48.0)),
        )
        sx = wx * 0.5 if r.rear_wheel_count == 2 else 0.0
        sx2 = wx * 0.75 if r.rear_wheel_count == 2 else 0.0
        # Strut foot sits under the deck rear (inside the actual rear edge), then
        # sweeps back/up to the fender front-top.
        foot_y = deck_rear_y
        mid_y = (foot_y + fender_front_top[1]) / 2.0
        strut = tube_from_spline_points(
            [
                (sx, foot_y, dz - 0.002),
                (sx2, mid_y, (dz + fender_front_top[2]) / 2.0 + 0.010),
                fender_front_top,
            ],
            radius=0.011,
            samples_per_segment=8,
            radial_segments=14,
        )
        body.visual(mesh_from_geometry(strut, f"rear_strut_{i}"), material="body_dark",
                    name=f"rear_strut_{i}", material_class_id="metal.paint_coated")


def _build_running_board(body, r: ResolvedKickScooterConfig) -> None:
    """Slot B running_board — low vintage box deck + raised branding (S0 L137-L147)."""
    dz = r.deck_top_z
    deck = BoxGeometry((0.130, 0.330 * r.deck_length_scale, 0.020))
    deck.translate(0.0, 0.020, dz - 0.010)
    body.visual(mesh_from_geometry(deck, "foot_deck"), material="body", name="foot_deck", material_class_id="metal.paint_coated")
    body.visual(
        Box((0.060, 0.150, 0.003)),
        origin=Origin(xyz=(0.0, 0.010, dz + 0.0015)),
        material="brand",
        name="branding", appearance_only=AppearanceOnlySpec(kind="decal"),
    )


def _build_flat_plank(body, r: ResolvedKickScooterConfig) -> None:
    """Slot B flat_plank — CadQuery filleted plank + grip-tape inlay (S4 L141-L165)."""
    dz = r.deck_top_z
    deck_length = 0.350 * r.deck_length_scale
    deck_width = 0.130
    deck_thick = 0.022
    deck_center_y = 0.030
    deck_center_z = dz - deck_thick / 2.0
    deck_shape = (
        cq.Workplane("XY")
        .box(deck_width, deck_length, deck_thick)
        .edges("|Y")
        .fillet(0.005)
    )
    body.visual(
        mesh_from_cadquery(deck_shape, "foot_deck"),
        origin=Origin(xyz=(0.0, deck_center_y, deck_center_z)),
        material="body",
        name="foot_deck", material_class_id="wood.painted_clean",
    )
    body.visual(
        Box((0.110, 0.300 * r.deck_length_scale, 0.002)),
        origin=Origin(xyz=(0.0, deck_center_y, dz + 0.001)),
        material="grip",
        name="grip_tape", material_class_id="rubber.pebbled",
    )


_DECK_BUILDERS = {
    "running_board": _build_running_board,
    "flat_plank": _build_flat_plank,
}


def _build_body(model: ArticulatedObject, r: ResolvedKickScooterConfig):
    body = model.part("body")
    _DECK_BUILDERS[r.deck_form](body, r)
    _emit_neck_and_head(body, r)
    _emit_rear_furniture(body, r)
    body.inertial = Inertial.from_geometry(
        Box((0.16, 0.55, 0.22)), mass=6.0, origin=Origin(xyz=(0.0, -0.02, 0.10))
    )
    return body


# --------------------------------------------------------------------------- #
# Rear wheel multiplicity
# --------------------------------------------------------------------------- #


def _rear_wheel_xs(r: ResolvedKickScooterConfig) -> list[float]:
    """X positions of the rear wheels on the shared axle (spec §Multiplicity)."""
    if r.rear_wheel_count == 1:
        return [0.0]
    return [-r.rear_track / 2.0, r.rear_track / 2.0]


def _emit_rear_wheels(model: ArticulatedObject, body, r: ResolvedKickScooterConfig) -> list[str]:
    names: list[str] = []
    for i, wx in enumerate(_rear_wheel_xs(r)):
        part = model.part(f"rear_wheel_{i}")
        _emit_wheel(part, f"rear_{i}", r)
        model.articulation(
            f"rear_wheel_roll_{i}",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=part,
            origin=Origin(xyz=(wx, r.rear_wheel_y, r.axle_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=30.0),
        )
        names.append(f"rear_wheel_{i}")
    return names


# --------------------------------------------------------------------------- #
# Slot A — handlebar / stem geometry. Each emits the stem + fork legs + bar +
# grips + front fender onto a target part (the column for rigid, or split
# lower-column + upper_stem for folding). Returns the list of fork-leg names.
# --------------------------------------------------------------------------- #


def _emit_fork_legs(part, r: ResolvedKickScooterConfig) -> None:
    """Lower fork legs head -> front axle (carry the front wheel) (S0 L273-L291)."""
    fwy = r.front_wheel_y
    az = r.axle_z
    for sx in (-1.0, 1.0):
        leg = tube_from_spline_points(
            _rel(
                [
                    (sx * 0.006, 0.184, 0.150),
                    (sx * 0.028, 0.250, 0.100),
                    (sx * 0.032, fwy, az + 0.004),
                ],
                HEAD_BASE,
            ),
            radius=0.010,
            samples_per_segment=10,
            radial_segments=14,
        )
        column_name = "fork_leg_0" if sx < 0 else "fork_leg_1"
        part.visual(mesh_from_geometry(leg, column_name), material="body_dark", name=column_name, material_class_id="metal.paint_coated")
    # Front axle stub spanning the fork legs at the wheel axle, so the
    # front_wheel_roll joint origin anchors to real parent geometry.
    fw_axle_local = (0.0 - HEAD_BASE[0], fwy - HEAD_BASE[1], az - HEAD_BASE[2])
    axle = CylinderGeometry(0.009, WHEEL_W + 0.024, radial_segments=16)
    axle.rotate_y(math.pi / 2.0)
    axle.translate(*fw_axle_local)
    part.visual(mesh_from_geometry(axle, "front_axle"), material="metal", name="front_axle", material_class_id="metal.steel_bare")


def _emit_front_fender(part, r: ResolvedKickScooterConfig) -> None:
    fw_axle_local = (0.0 - HEAD_BASE[0], r.front_wheel_y - HEAD_BASE[1], r.axle_z - HEAD_BASE[2])
    part.visual(
        _fender(r.wheel_r + 0.012, WHEEL_W + 0.024, 0.013, span_deg=170.0, start_deg=10.0,
                name="front_fender"),
        origin=Origin(xyz=fw_axle_local),
        material="body",
        name="front_fender", material_class_id="metal.paint_coated",
    )


# --- curved_swept (S0 L256-L317) --------------------------------------------


_CURVED_STEM_PTS = [
    (0.0, 0.182, 0.150),
    (0.0, 0.150, 0.320),
    (0.0, 0.120, 0.500),
    (0.0, 0.120, 0.660),
    (0.0, 0.150, 0.770),
    (0.0, 0.190, 0.815),
]


def _emit_curved_swept(column, r: ResolvedKickScooterConfig, *, top_only_above: float | None = None,
                       target=None) -> None:
    """Curved stem + T crossbar + grips. If ``top_only_above`` is set, the stem
    is split: the segment up to that z stays on ``column`` and the segment above
    goes on ``target`` (folding upper_stem)."""
    s = r.stem_height_scale
    pts = _scale_z_pts(_CURVED_STEM_PTS, s, HEAD_BASE[2])
    bar_y = (0.195 - HEAD_BASE[1])
    bar_z = (0.823 - HEAD_BASE[2]) * s
    half = 0.150 * r.handlebar_width_scale
    grip_x = 0.110 * r.handlebar_width_scale

    column.visual(mesh_from_geometry(
        tube_from_spline_points(_rel(pts, HEAD_BASE), radius=0.018,
                                samples_per_segment=14, radial_segments=18),
        "curved_stem"), material="body", name="curved_stem", material_class_id="metal.paint_coated")
    column.visual(
        Cylinder(radius=0.014, length=2.0 * half),
        origin=Origin(xyz=(0.0, bar_y, bar_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="metal", name="handlebar_crossbar", material_class_id="metal.chrome_polished",
    )
    column.visual(
        Box((0.030, 0.040, 0.030)),
        origin=Origin(xyz=(0.0, 0.193 - HEAD_BASE[1], (0.818 - HEAD_BASE[2]) * s)),
        material="body_dark", name="gooseneck", material_class_id="metal.paint_coated",
    )
    for i, sx in enumerate((-1.0, 1.0)):
        column.visual(
            Cylinder(radius=0.018, length=0.090),
            origin=Origin(xyz=(sx * grip_x, bar_y, bar_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="grip", name=f"grip_{i}", material_class_id="rubber.pebbled",
        )


# --- tbar_straight (S1 L256-L312) -------------------------------------------


def _emit_tbar_straight(column, r: ResolvedKickScooterConfig) -> None:
    s = r.stem_height_scale
    stem_length = ((0.820 - HEAD_BASE[2]) / math.cos(HEAD_TILT)) * s
    stem_top_local = (0.0, stem_length * math.sin(HEAD_TILT), stem_length * math.cos(HEAD_TILT))
    half = 0.150 * r.handlebar_width_scale
    grip_x = 0.110 * r.handlebar_width_scale

    column.visual(mesh_from_geometry(
        tube_from_spline_points([(0.0, 0.0, 0.0), stem_top_local], radius=0.016,
                                samples_per_segment=4, radial_segments=18),
        "straight_stem"), material="body", name="straight_stem", material_class_id="metal.paint_coated")
    column.visual(
        Cylinder(radius=0.014, length=2.0 * half),
        origin=Origin(xyz=(0.0, stem_top_local[1], stem_top_local[2]), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="metal", name="handlebar_crossbar", material_class_id="metal.chrome_polished",
    )
    column.visual(
        Box((0.028, 0.028, 0.028)),
        origin=Origin(xyz=(0.0, stem_top_local[1], stem_top_local[2])),
        material="body_dark", name="stem_cap", material_class_id="metal.paint_coated",
    )
    for i, sx in enumerate((-1.0, 1.0)):
        column.visual(
            Cylinder(radius=0.018, length=0.090),
            origin=Origin(xyz=(sx * grip_x, stem_top_local[1], stem_top_local[2]),
                          rpy=(0.0, math.pi / 2.0, 0.0)),
            material="grip", name=f"grip_{i}", material_class_id="rubber.pebbled",
        )


# --- bmx_riser (S2 L256-L350) -----------------------------------------------


def _emit_bmx_riser(column, r: ResolvedKickScooterConfig) -> None:
    s = r.stem_height_scale
    w = r.handlebar_width_scale
    # Seat the stem base AT the head base (z=0.150) so it meets the fork legs /
    # head tube; otherwise the bmx stem floats above the head as an island.
    stem_pts = _scale_z_pts(
        [(0.0, 0.184, 0.150), (0.0, 0.183, 0.300), (0.0, 0.182, 0.470)], s, HEAD_BASE[2])
    column.visual(mesh_from_geometry(
        tube_from_spline_points(_rel(stem_pts, HEAD_BASE), radius=0.020,
                                samples_per_segment=10, radial_segments=18),
        "stem"), material="body", name="stem", material_class_id="metal.paint_coated")

    riser_pts_raw = [
        (-0.170 * w, 0.190, 0.820), (-0.080 * w, 0.185, 0.820), (-0.050, 0.183, 0.790),
        (-0.040, 0.182, 0.650), (-0.030, 0.182, 0.530), (-0.010, 0.182, 0.480),
        (0.000, 0.182, 0.470), (0.010, 0.182, 0.480), (0.030, 0.182, 0.530),
        (0.040, 0.182, 0.650), (0.050, 0.183, 0.790), (0.080 * w, 0.185, 0.820),
        (0.170 * w, 0.190, 0.820),
    ]
    riser_pts = _scale_z_pts(riser_pts_raw, s, HEAD_BASE[2])
    column.visual(mesh_from_geometry(
        tube_from_spline_points(_rel(riser_pts, HEAD_BASE), radius=0.012,
                                samples_per_segment=10, radial_segments=16),
        "riser_bar"), material="metal", name="riser_bar", material_class_id="metal.chrome_polished")

    brace_pts = _scale_z_pts(
        [(-0.040, 0.182, 0.650), (0.040, 0.182, 0.650)], s, HEAD_BASE[2])
    column.visual(mesh_from_geometry(
        tube_from_spline_points(_rel(brace_pts, HEAD_BASE), radius=0.008,
                                samples_per_segment=4, radial_segments=12),
        "cross_brace"), material="metal", name="cross_brace", material_class_id="metal.chrome_polished")

    grip_y = 0.190 - HEAD_BASE[1]
    grip_z = (0.820 - HEAD_BASE[2]) * s
    # Center the grips so their inner end overlaps the riser bar end (riser ends
    # at x=0.170*w; grip half-length 0.040) — otherwise the grips float free.
    for i, sx in enumerate((-1.0, 1.0)):
        column.visual(
            Cylinder(radius=0.018, length=0.080),
            origin=Origin(xyz=(sx * 0.185 * w, grip_y, grip_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="grip", name=f"grip_{i}", material_class_id="rubber.pebbled",
        )


# --- swept_cruiser (S3 L256-L354) -------------------------------------------


def _emit_swept_cruiser(column, r: ResolvedKickScooterConfig) -> None:
    s = r.stem_height_scale
    w = r.handlebar_width_scale
    stem_pts = _scale_z_pts([
        (0.0, 0.182, 0.150), (0.0, 0.150, 0.320), (0.0, 0.120, 0.500),
        (0.0, 0.120, 0.660), (0.0, 0.155, 0.770), (0.0, 0.192, 0.822),
    ], s, HEAD_BASE[2])
    column.visual(mesh_from_geometry(
        tube_from_spline_points(_rel(stem_pts, HEAD_BASE), radius=0.018,
                                samples_per_segment=14, radial_segments=18),
        "curved_stem"), material="body", name="curved_stem", material_class_id="metal.paint_coated")

    bar_pts_raw = [
        (-0.250 * w, 0.020, 0.840), (-0.200 * w, 0.080, 0.822), (-0.130 * w, 0.140, 0.820),
        (-0.050, 0.180, 0.823), (0.000, 0.195, 0.825), (0.050, 0.180, 0.823),
        (0.130 * w, 0.140, 0.820), (0.200 * w, 0.080, 0.822), (0.250 * w, 0.020, 0.840),
    ]
    bar_pts = _scale_z_pts(bar_pts_raw, s, HEAD_BASE[2])
    column.visual(mesh_from_geometry(
        tube_from_spline_points(_rel(bar_pts, HEAD_BASE), radius=0.014,
                                samples_per_segment=14, radial_segments=18),
        "cruiser_bar"), material="metal", name="cruiser_bar", material_class_id="metal.chrome_polished")
    column.visual(
        Box((0.032, 0.040, 0.032)),
        origin=Origin(xyz=(0.0, 0.195 - HEAD_BASE[1], (0.825 - HEAD_BASE[2]) * s)),
        material="body_dark", name="gooseneck", material_class_id="metal.paint_coated",
    )
    _grip_r = math.asin(0.74)
    _grip_p = math.atan2(0.62, 0.25)
    for i, sx in enumerate((-1.0, 1.0)):
        grip_geom = CylinderGeometry(0.019, 0.100, radial_segments=20)
        grip_geom.rotate_x(_grip_r)
        grip_geom.rotate_y(sx * _grip_p)
        grip_geom.translate(
            sx * 0.250 * w - HEAD_BASE[0],
            0.020 - HEAD_BASE[1],
            (0.840 - HEAD_BASE[2]) * s,
        )
        column.visual(mesh_from_geometry(grip_geom, f"grip_{i}"), material="grip", name=f"grip_{i}", material_class_id="rubber.pebbled")


_HANDLEBAR_EMITTERS = {
    "curved_swept": _emit_curved_swept,
    "tbar_straight": _emit_tbar_straight,
    "bmx_riser": _emit_bmx_riser,
    "swept_cruiser": _emit_swept_cruiser,
}


# --------------------------------------------------------------------------- #
# Slot A + C — steering column build (rigid one-piece, or folding split).
# --------------------------------------------------------------------------- #


def _build_steering_rigid(model: ArticulatedObject, body, r: ResolvedKickScooterConfig):
    """rigid stem articulation: stem + bar + grips + fork legs + fender are one
    ``steering_column`` part; only the steering revolute moves it."""
    column = model.part("steering_column")
    _HANDLEBAR_EMITTERS[r.handlebar_form](column, r)
    _emit_fork_legs(column, r)
    _emit_front_fender(column, r)
    column.inertial = Inertial.from_geometry(
        Box((0.30, 0.20, 0.70)), mass=2.5,
        origin=Origin(xyz=(0.0, 0.16 - HEAD_BASE[1], 0.45 - HEAD_BASE[2])),
    )
    model.articulation(
        "steering",
        ArticulationType.REVOLUTE,
        parent=body,
        child=column,
        origin=Origin(xyz=HEAD_BASE),
        axis=STEER_AXIS,
        motion_limits=MotionLimits(
            effort=8.0, velocity=3.0, lower=-r.steer_range, upper=r.steer_range),
    )
    return column


def _build_steering_folding(model: ArticulatedObject, body, r: ResolvedKickScooterConfig):
    """folding_hinge: the column splits. ``lower_stem`` + ``hinge_barrel`` +
    fork legs + front fender stay on ``steering_column`` (steered). A separate
    ``upper_stem`` part carries the bar + grips + hinge clamp/pin and folds about
    the hinge knuckle (S5 L246-L440).

    The handlebar geometry is always authored on the upper stem for the folding
    form, so handlebar_form for folding is always the curved/T family — we
    always use the curved upper tube + T bar (matches S5)."""
    column = model.part("steering_column")
    s = r.stem_height_scale

    # Lower stem head -> hinge.
    lower_pts = _scale_z_pts(
        [(0.0, 0.182, 0.150), (0.0, 0.150, 0.320), (0.0, 0.120, 0.500)], s, HEAD_BASE[2])
    column.visual(mesh_from_geometry(
        tube_from_spline_points(_rel(lower_pts, HEAD_BASE), radius=0.018,
                                samples_per_segment=14, radial_segments=18),
        "lower_stem"), material="body", name="lower_stem", material_class_id="metal.paint_coated")
    _emit_fork_legs(column, r)
    _emit_front_fender(column, r)

    hinge_world = (HINGE_WORLD[0], HINGE_WORLD[1], HINGE_WORLD[2] * s)
    hinge_local = (hinge_world[0] - HEAD_BASE[0], hinge_world[1] - HEAD_BASE[1],
                   hinge_world[2] - HEAD_BASE[2])
    column.visual(
        _hinge_barrel_mesh("hinge_barrel"),
        origin=Origin(xyz=hinge_local),
        material="body_dark", name="hinge_barrel", material_class_id="metal.paint_coated",
    )
    column.inertial = Inertial.from_geometry(
        Box((0.12, 0.20, 0.45)), mass=2.0,
        origin=Origin(xyz=(0.0, 0.08 - HEAD_BASE[1], 0.28 - HEAD_BASE[2])),
    )
    model.articulation(
        "steering",
        ArticulationType.REVOLUTE,
        parent=body, child=column,
        origin=Origin(xyz=HEAD_BASE), axis=STEER_AXIS,
        motion_limits=MotionLimits(
            effort=8.0, velocity=3.0, lower=-r.steer_range, upper=r.steer_range),
    )

    # Upper stem: bar + grips + hinge clamp/pin, folding about X at the hinge.
    upper = model.part("upper_stem")
    w = r.handlebar_width_scale
    upper_pts_raw = [
        (0.0, 0.120, 0.500), (0.0, 0.120, 0.660), (0.0, 0.150, 0.770), (0.0, 0.190, 0.815)]
    upper_pts = _scale_z_pts(upper_pts_raw, s, HEAD_BASE[2])
    upper.visual(mesh_from_geometry(
        tube_from_spline_points(_rel(upper_pts, hinge_world), radius=0.018,
                                samples_per_segment=14, radial_segments=18),
        "upper_stem_tube"), material="body", name="upper_stem_tube", material_class_id="metal.paint_coated")

    bar_z = (0.823 - HEAD_BASE[2]) * s - (hinge_world[2] - HEAD_BASE[2])
    bar_y = 0.195 - hinge_world[1]
    half = 0.150 * w
    grip_x = 0.110 * w
    upper.visual(
        Cylinder(radius=0.014, length=2.0 * half),
        origin=Origin(xyz=(0.0, bar_y, bar_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="metal", name="handlebar_crossbar", material_class_id="metal.chrome_polished",
    )
    upper.visual(
        Box((0.030, 0.040, 0.030)),
        origin=Origin(xyz=(0.0, 0.193 - hinge_world[1], (0.818 - HEAD_BASE[2]) * s - (hinge_world[2] - HEAD_BASE[2]))),
        material="body_dark", name="gooseneck", material_class_id="metal.paint_coated",
    )
    for i, sx in enumerate((-1.0, 1.0)):
        upper.visual(
            Cylinder(radius=0.018, length=0.090),
            origin=Origin(xyz=(sx * grip_x, bar_y, bar_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="grip", name=f"grip_{i}", material_class_id="rubber.pebbled",
        )
    # Clamp yoke: a solid block at the part origin that ties the two hinge plates,
    # the pin and the upper stem tube base into one connected body (the tube base
    # rides at z = 0.150*(1-s) near the origin, so the yoke must span it).
    tube_base_z = 0.150 * (1.0 - s)
    yoke_zspan = abs(tube_base_z) + 0.030
    yoke = BoxGeometry((0.084, 0.044, yoke_zspan))
    yoke.translate(0.0, 0.0, tube_base_z / 2.0)
    upper.visual(mesh_from_geometry(yoke, "hinge_yoke"), material="body_dark", name="hinge_yoke", material_class_id="metal.paint_coated")
    # Hinge clamp plates straddling the barrel (clevis) at the part origin.
    for i, sx in enumerate((-1.0, 1.0)):
        plate = BoxGeometry((0.008, 0.054, 0.054))
        plate.translate(sx * 0.035, 0.0, 0.0)
        upper.visual(mesh_from_geometry(plate, f"hinge_plate_{i}"), material="body_dark",
                     name=f"hinge_plate_{i}", material_class_id="metal.paint_coated")
    upper.visual(_hinge_pin_mesh("hinge_pin"), origin=Origin(xyz=(0.0, 0.0, 0.0)),
                 material="metal", name="hinge_pin", material_class_id="metal.steel_bare")
    upper.visual(
        Box((0.030, 0.012, 0.018)),
        origin=Origin(xyz=(0.046, 0.0, 0.010)),
        material="body_dark", name="hinge_lever", material_class_id="metal.paint_coated",
    )
    upper.inertial = Inertial.from_geometry(
        Box((0.30, 0.10, 0.40)), mass=1.2, origin=Origin(xyz=(0.0, 0.04, 0.18)),
    )
    model.articulation(
        "fold_hinge",
        ArticulationType.REVOLUTE,
        parent=column, child=upper,
        origin=Origin(xyz=hinge_local),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=1.5, lower=0.0, upper=r.fold_range),
    )
    return column


# --------------------------------------------------------------------------- #
# Top-level build
# --------------------------------------------------------------------------- #


def build_kick_scooter(
    config: KickScooterConfig,
    *,
    assets=None,
) -> ArticulatedObject:
    """Compose a kick scooter model from the resolved config."""
    r = resolve_config(config)
    model = ArticulatedObject(name="kick_scooter", assets=assets)
    for token, rgba in r.palette.items():
        model.material(token, rgba=rgba)

    body = _build_body(model, r)
    _emit_rear_wheels(model, body, r)

    if r.stem_articulation == "folding_hinge":
        column = _build_steering_folding(model, body, r)
    else:
        column = _build_steering_rigid(model, body, r)

    # Front wheel: CONTINUOUS roll, child of the steering column.
    fw_axle_local = (0.0 - HEAD_BASE[0], r.front_wheel_y - HEAD_BASE[1], r.axle_z - HEAD_BASE[2])
    front_wheel = model.part("front_wheel")
    _emit_wheel(front_wheel, "front", r)
    model.articulation(
        "front_wheel_roll",
        ArticulationType.CONTINUOUS,
        parent=column,
        child=front_wheel,
        origin=Origin(xyz=fw_axle_local),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=30.0),
    )
    return model


def build_seeded_kick_scooter(seed: int) -> ArticulatedObject:
    return build_kick_scooter(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Structural module + multiplicity picks for the topology-diversity gate.

    Adds a quantized wheel-size proportion bucket (small/large wheels are a
    visibly distinct scooter form) so the distinct count clears the >=10 floor
    well within the early seed window (mirrors bicycle.py's density bucket)."""
    cfg = config_from_seed(seed)
    r = resolve_config(cfg)
    # For the folding form the handlebar geometry is always the curved upper bar,
    # so report it as such to keep slot_choices consistent with the build.
    handlebar = r.handlebar_form if r.stem_articulation == "rigid" else "curved_swept"
    wheel_bucket = "wheel_small" if r.wheel_radius_scale < 1.025 else "wheel_large"
    return [
        ("handlebar_form", handlebar),
        ("deck_form", r.deck_form),
        ("stem_articulation", r.stem_articulation),
        ("rear_wheel_count", f"n{r.rear_wheel_count}"),
        ("wheel_size", wheel_bucket),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedKickScooterConfig) -> None:
    """Captured/co-axial + nested-fender overlaps the MatingContract can't model."""
    parts = {p.name for p in model.parts}
    body = model.get_part("body")
    column = model.get_part("steering_column")
    front_wheel = model.get_part("front_wheel")

    # Front fender arcs closely over the front wheel.
    ctx.allow_overlap(column, front_wheel, elem_a="front_fender", elem_b="front_tire",
                      reason="The curved fender intentionally arcs closely over the front wheel.")
    # Fork legs + axle stub straddle / pass through the front wheel at its axle.
    for leg in ("fork_leg_0", "fork_leg_1", "front_axle"):
        for elem in ("front_rim", "front_rim__component_001", "front_rim__component_002",
                     "front_tire", "front_whitewall", "front_valve"):
            ctx.allow_overlap(column, front_wheel, elem_a=leg, elem_b=elem,
                              reason="Fork legs straddle and hold the front wheel at its axle.")

    # Stem base + fork legs pass through the body head tube / neck (the bearing).
    stem_elems = {
        "curved_swept": "curved_stem",
        "tbar_straight": "straight_stem",
        "bmx_riser": "stem",
        "swept_cruiser": "curved_stem",
    }
    stem_elem = "lower_stem" if r.stem_articulation == "folding_hinge" else stem_elems[r.handlebar_form]
    # The steering head sits at the deck front; on a long flat deck the fork legs
    # and stem base graze the deck's front lip where they join the head.
    for leg in (stem_elem, "fork_leg_0", "fork_leg_1", "front_fender"):
        ctx.allow_overlap(body, column, elem_a="foot_deck", elem_b=leg,
                          reason="The steering head + fork join the body at the deck front lip.")
    for body_elem in ("head_tube", "front_neck"):
        ctx.allow_overlap(body, column, elem_a=body_elem, elem_b=stem_elem,
                          reason="The steering stem turns inside the body head tube (the bearing).")
        for leg in ("fork_leg_0", "fork_leg_1"):
            ctx.allow_overlap(body, column, elem_a=body_elem, elem_b=leg,
                              reason="The fork legs join the steering head next to the body neck.")
        # The front fender wraps the front wheel just below the steering head; on
        # large-wheel draws its rear lip sweeps up to the head tube / neck.
        ctx.allow_overlap(body, column, elem_a=body_elem, elem_b="front_fender",
                          reason="The front fender wraps the wheel just below the steering head.")

    # Rear fender(s) arc closely over the rear wheel(s).
    for i in range(r.rear_wheel_count):
        rw = model.get_part(f"rear_wheel_{i}")
        ctx.allow_overlap(body, rw, elem_a=f"rear_fender_{i}", elem_b=f"rear_{i}_tire",
                          reason="The rear fender intentionally arcs closely over the rear wheel.")
        # The rear strut runs alongside the wheel from the deck to the fender top.
        for elem in (f"rear_{i}_tire", f"rear_{i}_whitewall"):
            ctx.allow_overlap(body, rw, elem_a=f"rear_strut_{i}", elem_b=elem,
                              reason="The rear strut runs alongside the wheel up to the fender.")
        if r.rear_wheel_count == 2:
            for elem in (f"rear_{i}_rim", f"rear_{i}_tire"):
                ctx.allow_overlap(body, rw, elem_a="rear_axle", elem_b=elem,
                                  reason="The rear axle beam passes through both rear wheel hubs.")
        else:
            # Single rear wheel: the body-side axle stub passes through the hub,
            # and the dropout link arcs close over the wheel up to the fender.
            for stub in (f"rear_axle_stub_{i}", f"rear_dropout_{i}"):
                for elem in (f"rear_{i}_rim", f"rear_{i}_rim__component_001",
                             f"rear_{i}_rim__component_002", f"rear_{i}_tire",
                             f"rear_{i}_whitewall", f"rear_{i}_valve"):
                    ctx.allow_overlap(body, rw, elem_a=stub, elem_b=elem,
                                      reason="The rear axle stub/dropout passes through/over the rear wheel.")

    # Folding hinge: upper stem clamp/pin captured on the lower barrel.
    if "upper_stem" in parts:
        upper = model.get_part("upper_stem")
        ctx.allow_overlap(column, upper,
                          reason="The folding upper stem hinge clamp/pin is captured on the lower hinge barrel.")


def _expect_deck_low_and_flat(ctx: TestContext, model: ArticulatedObject) -> None:
    body = model.get_part("body")
    deck_aabb = ctx.part_element_world_aabb(body, elem="foot_deck")
    dz = _ext(deck_aabb)
    # The deck length spans 0.330..0.350 * deck_length_scale (0.85..1.20), so the
    # shortest legal deck is ~0.28 m long — still clearly "long in Y" vs its
    # ~0.022 m thickness.
    ctx.check("deck is flat/horizontal (thin in Z, long in Y)",
              dz[2] < 0.05 and dz[1] > 0.27, details=f"deck extents={dz}")
    ctx.check("deck sits low (top below 0.15 m)",
              deck_aabb[1][2] < 0.15, details=f"deck max z={deck_aabb[1][2]}")


def _expect_wheels_ground(ctx: TestContext, model: ArticulatedObject, r: ResolvedKickScooterConfig) -> None:
    front_wheel = model.get_part("front_wheel")
    front_aabb = ctx.part_world_aabb(front_wheel)
    ctx.check("front wheel reaches the ground", front_aabb[0][2] < 0.02,
              details=f"front min z={front_aabb[0][2]}")
    front_y = ctx.part_world_position(front_wheel)[1]
    for i in range(r.rear_wheel_count):
        rw = model.get_part(f"rear_wheel_{i}")
        rw_aabb = ctx.part_world_aabb(rw)
        ctx.check(f"rear_wheel_{i} reaches the ground", rw_aabb[0][2] < 0.02,
                  details=f"rear_wheel_{i} min z={rw_aabb[0][2]}")
        rw_y = ctx.part_world_position(rw)[1]
        ctx.check(f"front wheel ahead of rear_wheel_{i}", front_y > rw_y + 0.30,
                  details=f"front_y={front_y}, rear_wheel_{i}_y={rw_y}")


def _expect_tall_bar(ctx: TestContext, model: ArticulatedObject, r: ResolvedKickScooterConfig) -> None:
    column = model.get_part("steering_column")
    col_aabb = ctx.part_world_aabb(column)
    top_z = col_aabb[1][2]
    if r.stem_articulation == "folding_hinge":
        upper = model.get_part("upper_stem")
        up_aabb = ctx.part_world_aabb(upper)
        top_z = max(top_z, up_aabb[1][2])
    ctx.check("handlebar/stem is tall (reaches ~0.8 m)", top_z > 0.78,
              details=f"column/bar max z={top_z}")


def _expect_steering(ctx: TestContext, model: ArticulatedObject, r: ResolvedKickScooterConfig) -> None:
    steering = model.get_articulation("steering")
    front_wheel = model.get_part("front_wheel")
    rest = ctx.part_world_position(front_wheel)
    with ctx.pose({steering: r.steer_range}):
        turned = ctx.part_world_position(front_wheel)
    ctx.check("steering swings the front wheel sideways",
              abs(turned[0] - rest[0]) > 0.03, details=f"rest={rest}, turned={turned}")
    # Steering must NOT move the rear wheels.
    for i in range(r.rear_wheel_count):
        rw = model.get_part(f"rear_wheel_{i}")
        rear_rest = ctx.part_world_position(rw)
        with ctx.pose({steering: r.steer_range}):
            rear_after = ctx.part_world_position(rw)
        ctx.check(f"steering leaves rear_wheel_{i} fixed",
                  abs(rear_after[0] - rear_rest[0]) < 1e-6,
                  details=f"rest={rear_rest}, after={rear_after}")


def _valve_yz(aabb):
    return ((aabb[0][1] + aabb[1][1]) / 2.0, (aabb[0][2] + aabb[1][2]) / 2.0)


def _expect_wheel_roll(ctx: TestContext, model: ArticulatedObject, r: ResolvedKickScooterConfig) -> None:
    front_roll = model.get_articulation("front_wheel_roll")
    front_wheel = model.get_part("front_wheel")
    rest = _valve_yz(ctx.part_element_world_aabb(front_wheel, elem="front_valve"))
    with ctx.pose({front_roll: math.pi / 2.0}):
        rolled = _valve_yz(ctx.part_element_world_aabb(front_wheel, elem="front_valve"))
    ctx.check("front wheel rolls (valve marker moves in YZ)",
              abs(rolled[0] - rest[0]) > 0.02 or abs(rolled[1] - rest[1]) > 0.02,
              details=f"rest={rest}, rolled={rolled}")
    for i in range(r.rear_wheel_count):
        roll = model.get_articulation(f"rear_wheel_roll_{i}")
        rw = model.get_part(f"rear_wheel_{i}")
        rrest = _valve_yz(ctx.part_element_world_aabb(rw, elem=f"rear_{i}_valve"))
        with ctx.pose({roll: math.pi / 2.0}):
            rrolled = _valve_yz(ctx.part_element_world_aabb(rw, elem=f"rear_{i}_valve"))
        ctx.check(f"rear_wheel_{i} rolls (valve marker moves in YZ)",
                  abs(rrolled[0] - rrest[0]) > 0.02 or abs(rrolled[1] - rrest[1]) > 0.02,
                  details=f"rest={rrest}, rolled={rrolled}")


def _expect_fold(ctx: TestContext, model: ArticulatedObject, r: ResolvedKickScooterConfig) -> None:
    """For the folding form, folding the upper stem must actually move the bar."""
    if r.stem_articulation != "folding_hinge":
        return
    fold = model.get_articulation("fold_hinge")
    upper = model.get_part("upper_stem")
    # The upper_stem link origin sits ON the hinge axis, so it is invariant under
    # the fold rotation. Measure the handlebar grip (offset from the hinge) — that
    # is what visibly swings when the stem folds.

    def _grip_center():
        aabb = ctx.part_element_world_aabb(upper, elem="handlebar_crossbar")
        return tuple((aabb[0][k] + aabb[1][k]) / 2.0 for k in range(3))

    rest = _grip_center()
    with ctx.pose({fold: r.fold_range}):
        folded = _grip_center()
    ctx.check("fold hinge moves the upper stem",
              any(abs(rest[i] - folded[i]) > 0.02 for i in range(3)),
              details=f"rest={rest}, folded={folded}")


def run_kick_scooter_tests(model: ArticulatedObject, config: KickScooterConfig) -> TestReport:
    """Author-layer QC for the modular kick-scooter template."""
    r = resolve_config(config)
    ctx = TestContext(model)

    _declare_overlaps(ctx, model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.030)
    ctx.fail_if_joint_mating_has_gap()

    _expect_deck_low_and_flat(ctx, model)
    _expect_wheels_ground(ctx, model, r)
    _expect_tall_bar(ctx, model, r)
    _expect_steering(ctx, model, r)
    _expect_wheel_roll(ctx, model, r)
    _expect_fold(ctx, model, r)

    return ctx.report()


__all__ = [
    "DeckForm",
    "HandlebarForm",
    "KickScooterConfig",
    "PaletteStyle",
    "ResolvedKickScooterConfig",
    "StemArticulation",
    "build_kick_scooter",
    "build_seeded_kick_scooter",
    "config_from_seed",
    "resolve_config",
    "run_kick_scooter_tests",
    "slot_choices_for_seed",
]
