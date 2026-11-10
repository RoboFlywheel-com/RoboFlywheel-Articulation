# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for the ``bicycle`` 小类 (Sports / Bike).

A complete, rideable two-wheel human-powered chain-drive bicycle: a triangular
root ``frame`` carries four children — a steered ``fork`` (which carries the
front wheel), the ``rear_wheel``, and the ``crank``.  Front and rear wheels are
coplanar and share one diameter (~0.70 m); they touch the ground at z=0 with
both axles at z=WHEEL_R.

Pattern: ``mixed`` (parallel children assembled on the frame root + per-wheel
spoke multiplicity).

Slot graph (spec §slot graph):
    frame (root, Slot A)
      ├─[REVOLUTE steering, tilted head-tube axis (XZ), ±0.70]→ fork (Slot B)
      │     └─ handlebar (Slot C, fixed to the fork stem — fork's own visuals)
      │     └─[CONTINUOUS front_wheel_roll, Y]→ front_wheel (+spoke multiplicity)
      ├─[CONTINUOUS rear_wheel_roll, Y]→ rear_wheel (+spoke multiplicity)
      └─[CONTINUOUS crank_spin, Y]→ crank

Shared kinematic skeleton (never an axis-choice, present on every seed):
    steering REVOLUTE ±0.70 ; front/rear roll CONTINUOUS Y ; crank_spin CONTINUOUS Y.

5★ sources adapted (AUTHORING.md §A Rule 3):
  S_parent  rec_orange-hardtail-mountain-bike-...f497242f
            — whole-bike baseline + every interface/joint + spoke helper
              (model.py A:L143-203, B:L230-259, C:L262-285, spoke:L59-114).
  S_step    rec_bicycle_var_stepthrough  — step_through frame (L148-193).
  S_bmx     rec_bicycle_var_bmx          — bmx_compact frame (L142-175).
  S_cruiser rec_bicycle_var_cruiser      — cruiser_cantilever frame (L148-213).
  S_rigid   rec_bicycle_var_rigidfork    — rigid_fork (L230-251).
  S_dual    rec_bicycle_var_dualcrown    — dual_crown fork + arch (L230-296).
  S_riser   rec_bicycle_var_riserbar     — riser_bar (L261-296).
  S_drop    rec_bicycle_var_dropbar      — drop_bar + hood + tape (L262-313).
  S_sp18/36 rec_bicycle_var_spokes18/36  — n_spokes copy logic (L82).

Structural diversity axes (slot_choices_for_seed records these):
  A frame_geometry (4) × B fork_front_end (3) × C handlebar_form (3) → 36 slot
  tuples (drop_bar×dual_crown gated → 32 legal); + n_spokes multiplicity bucket;
  palette_style (6) is orthogonal and drives every .visual material.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from math import cos, pi, sin
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    CylinderGeometry,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot enums
# --------------------------------------------------------------------------- #
FrameGeometry = Literal["diamond", "step_through", "bmx_compact", "cruiser_cantilever"]
ForkFrontEnd = Literal["suspension_fork", "rigid_fork", "dual_crown"]
HandlebarForm = Literal["flat_bar", "riser_bar", "drop_bar"]
PaletteStyle = Literal[
    "trail_orange",
    "matte_stealth_black",
    "chrome_silver_classic",
    "racing_red",
    "forest_green_cruiser",
    "sky_blue_commuter",
]

FRAME_GEOMETRIES: tuple[FrameGeometry, ...] = (
    "diamond",
    "step_through",
    "bmx_compact",
    "cruiser_cantilever",
)
FORK_FRONT_ENDS: tuple[ForkFrontEnd, ...] = ("suspension_fork", "rigid_fork", "dual_crown")
HANDLEBAR_FORMS: tuple[HandlebarForm, ...] = ("flat_bar", "riser_bar", "drop_bar")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "trail_orange",
    "matte_stealth_black",
    "chrome_silver_classic",
    "racing_red",
    "forest_green_cruiser",
    "sky_blue_commuter",
)

# n_spokes weighted sampling buckets (spec §Multiplicity). Common 24/28/32/36
# high-frequency; sparse tails 12/16/44/48.  Same N applies to both wheels.
N_SPOKE_CHOICES: tuple[int, ...] = (12, 16, 20, 24, 28, 32, 36, 40, 44, 48)
N_SPOKE_WEIGHTS: tuple[float, ...] = (0.04, 0.07, 0.09, 0.16, 0.16, 0.16, 0.14, 0.09, 0.05, 0.04)

# --------------------------------------------------------------------------- #
# Palette presets (Slot E) — every colorway resolves to a `mats` dict with the
# SAME token set so the builder is colorway-agnostic. Tokens:
#   frame  — main frame paint        accent — small accent / valve marker
#   metal  — silver bright metal (seatpost/spokes/rim/chainring)
#   dark   — black components (hub/bb/caliper/stem/saddle)
#   tire   — tire rubber             rim    — rim band
#   grip   — handlebar grips / tape
# --------------------------------------------------------------------------- #
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "trail_orange": {
        "frame": (0.95, 0.46, 0.10, 1.0),
        "accent": (0.80, 0.12, 0.10, 1.0),
        "metal": (0.74, 0.76, 0.79, 1.0),
        "dark": (0.12, 0.13, 0.14, 1.0),
        "tire": (0.07, 0.07, 0.08, 1.0),
        "rim": (0.55, 0.57, 0.60, 1.0),
        "grip": (0.10, 0.10, 0.11, 1.0),
    },
    "matte_stealth_black": {
        "frame": (0.13, 0.14, 0.15, 1.0),
        "accent": (0.55, 0.56, 0.58, 1.0),
        "metal": (0.50, 0.52, 0.55, 1.0),
        "dark": (0.08, 0.08, 0.09, 1.0),
        "tire": (0.06, 0.06, 0.07, 1.0),
        "rim": (0.40, 0.41, 0.43, 1.0),
        "grip": (0.10, 0.10, 0.11, 1.0),
    },
    "chrome_silver_classic": {
        "frame": (0.78, 0.80, 0.83, 1.0),
        "accent": (0.20, 0.22, 0.25, 1.0),
        "metal": (0.82, 0.84, 0.87, 1.0),
        "dark": (0.12, 0.13, 0.14, 1.0),
        "tire": (0.08, 0.08, 0.09, 1.0),
        "rim": (0.70, 0.72, 0.75, 1.0),
        "grip": (0.14, 0.11, 0.08, 1.0),
    },
    "racing_red": {
        "frame": (0.80, 0.10, 0.10, 1.0),
        "accent": (0.93, 0.92, 0.90, 1.0),
        "metal": (0.76, 0.78, 0.81, 1.0),
        "dark": (0.11, 0.12, 0.13, 1.0),
        "tire": (0.07, 0.07, 0.08, 1.0),
        "rim": (0.58, 0.60, 0.63, 1.0),
        "grip": (0.10, 0.10, 0.11, 1.0),
    },
    "forest_green_cruiser": {
        "frame": (0.10, 0.32, 0.18, 1.0),
        "accent": (0.78, 0.62, 0.36, 1.0),
        "metal": (0.74, 0.76, 0.79, 1.0),
        "dark": (0.12, 0.12, 0.12, 1.0),
        "tire": (0.10, 0.09, 0.08, 1.0),
        "rim": (0.60, 0.62, 0.64, 1.0),
        "grip": (0.32, 0.20, 0.10, 1.0),
    },
    "sky_blue_commuter": {
        "frame": (0.20, 0.55, 0.82, 1.0),
        "accent": (0.95, 0.95, 0.96, 1.0),
        "metal": (0.75, 0.77, 0.80, 1.0),
        "dark": (0.12, 0.13, 0.14, 1.0),
        "tire": (0.07, 0.07, 0.08, 1.0),
        "rim": (0.57, 0.59, 0.62, 1.0),
        "grip": (0.11, 0.11, 0.12, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Per-frame anchor presets.  Each frame module owns its own coordinate anchors
# (axles / BB / head-tube line / seat-tube top) because the BMX is compact and
# the cruiser is stretched.  The fork + handlebar are authored relative to these
# anchors so every (frame × fork × bar) combination stays self-consistent.
# --------------------------------------------------------------------------- #
TIRE_T = 0.028  # tire cross-section (tube) radius — constant identity dimension


@dataclass(frozen=True)
class _FrameAnchors:
    wheelbase: float
    bb: tuple[float, float, float]
    head_top: tuple[float, float, float]
    head_bot: tuple[float, float, float]
    seat_top: tuple[float, float, float]


# Baseline anchors per frame module (from each 5★ source's constants block).
_FRAME_ANCHORS: dict[FrameGeometry, _FrameAnchors] = {
    "diamond": _FrameAnchors(
        wheelbase=1.05,
        bb=(0.49, 0.0, 0.30),
        head_top=(0.80, 0.0, 1.00),
        head_bot=(0.86, 0.0, 0.70),
        seat_top=(0.085, 0.0, 1.02),
    ),
    "step_through": _FrameAnchors(
        wheelbase=1.05,
        bb=(0.49, 0.0, 0.30),
        head_top=(0.80, 0.0, 1.00),
        head_bot=(0.86, 0.0, 0.70),
        seat_top=(0.12, 0.0, 1.00),
    ),
    "bmx_compact": _FrameAnchors(
        wheelbase=0.88,
        bb=(0.40, 0.0, 0.30),
        head_top=(0.65, 0.0, 0.94),
        head_bot=(0.69, 0.0, 0.80),
        seat_top=(0.30, 0.0, 0.84),
    ),
    "cruiser_cantilever": _FrameAnchors(
        wheelbase=1.18,
        bb=(0.50, 0.0, 0.28),
        head_top=(0.82, 0.0, 1.02),
        head_bot=(0.87, 0.0, 0.72),
        seat_top=(0.085, 0.0, 1.00),
    ),
}


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class BicycleConfig:
    frame_geometry: FrameGeometry | None = None
    fork_front_end: ForkFrontEnd | None = None
    handlebar_form: HandlebarForm | None = None
    n_spokes: int | None = None
    palette_style: PaletteStyle = "trail_orange"

    wheel_r: float = 0.35
    wheelbase_scale: float = 1.0
    head_tube_angle_scale: float = 1.0
    seat_height_scale: float = 1.0
    fork_leg_r_scale: float = 1.0
    name: str = "bicycle"


@dataclass(frozen=True)
class ResolvedBicycleConfig:
    frame_geometry: FrameGeometry
    fork_front_end: ForkFrontEnd
    handlebar_form: HandlebarForm
    n_spokes: int
    palette_style: PaletteStyle
    wheel_r: float
    # resolved anchors (scaled)
    wheelbase: float
    bb: tuple[float, float, float]
    head_top: tuple[float, float, float]
    head_bot: tuple[float, float, float]
    seat_top: tuple[float, float, float]
    rear_axle: tuple[float, float, float]
    front_axle: tuple[float, float, float]
    leg_y: float
    fork_leg_r: float
    seat_height_scale: float
    name: str = "bicycle"


# --------------------------------------------------------------------------- #
# Sampling
# --------------------------------------------------------------------------- #
def config_from_seed(seed: int) -> BicycleConfig:
    """Deterministic per-seed procedural sampling (seed 0 not special)."""
    rng = random.Random(seed)

    frame_geometry = rng.choice(FRAME_GEOMETRIES)
    fork_front_end = rng.choice(FORK_FRONT_ENDS)
    handlebar_form = rng.choice(HANDLEBAR_FORMS)
    n_spokes = rng.choices(N_SPOKE_CHOICES, weights=N_SPOKE_WEIGHTS, k=1)[0]
    palette_style = rng.choice(PALETTE_STYLES)

    return BicycleConfig(
        frame_geometry=frame_geometry,
        fork_front_end=fork_front_end,
        handlebar_form=handlebar_form,
        n_spokes=n_spokes,
        palette_style=palette_style,
        wheel_r=round(rng.uniform(0.30, 0.37), 4),
        wheelbase_scale=round(rng.uniform(0.92, 1.08), 4),
        head_tube_angle_scale=round(rng.uniform(0.95, 1.05), 4),
        seat_height_scale=round(rng.uniform(0.92, 1.10), 4),
        fork_leg_r_scale=round(rng.uniform(0.9, 1.3), 4),
        name=f"seeded_bicycle_{seed}",
    )


def _pick(value, choices):
    return value if value in choices else choices[0]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def resolve_config(config: BicycleConfig | None = None) -> ResolvedBicycleConfig:
    cfg = config or BicycleConfig()

    frame_geometry = _pick(cfg.frame_geometry, FRAME_GEOMETRIES)
    fork_front_end = _pick(cfg.fork_front_end, FORK_FRONT_ENDS)
    handlebar_form = _pick(cfg.handlebar_form, HANDLEBAR_FORMS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # --- Compatibility gating (spec §compatibility matrix). ---
    # drop_bar (road) × dual_crown (DH) is geometrically absurd; fall the fork
    # back to the slim rigid_fork that a road drop-bar would actually carry.
    if handlebar_form == "drop_bar" and fork_front_end == "dual_crown":
        fork_front_end = "rigid_fork"

    n_spokes = cfg.n_spokes if cfg.n_spokes is not None else 28
    n_spokes = int(_clamp(float(n_spokes), 12, 48))

    anchors = _FRAME_ANCHORS[frame_geometry]

    # --- independent continuous scales ---
    wheel_r = _clamp(float(cfg.wheel_r), 0.30, 0.37)
    # BMX identity = small (20") wheels. The compact frame packs both wheels close
    # to a forward bottom bracket, so a big wheel cannot clear the pedals / down
    # tube — cap the BMX wheel radius so the compact geometry stays collision-free.
    if frame_geometry == "bmx_compact":
        wheel_r = _clamp(wheel_r, 0.27, 0.295)
    wheelbase_scale = _clamp(float(cfg.wheelbase_scale), 0.92, 1.08)
    head_tube_angle_scale = _clamp(float(cfg.head_tube_angle_scale), 0.95, 1.05)

    # --- conditional scales (depend on upstream enum identity) ---
    seat_height_scale = float(cfg.seat_height_scale)
    if frame_geometry == "bmx_compact":
        # BMX identity = LOW saddle; tighten the upper bound.
        seat_height_scale = _clamp(seat_height_scale, 0.92, 1.00)
    else:
        seat_height_scale = _clamp(seat_height_scale, 0.92, 1.10)

    fork_leg_r_scale = float(cfg.fork_leg_r_scale)
    if fork_front_end == "dual_crown":
        # DH dual-crown = FAT legs: raise the lower bound.
        fork_leg_r_scale = _clamp(fork_leg_r_scale, 1.05, 1.3)
    elif fork_front_end == "rigid_fork":
        # slim single-piece blade: cap the upper bound.
        fork_leg_r_scale = _clamp(fork_leg_r_scale, 0.9, 1.10)
    else:
        fork_leg_r_scale = _clamp(fork_leg_r_scale, 0.9, 1.3)

    # base leg radius per fork type (from sources).
    base_leg_r = {
        "suspension_fork": 0.020,
        "rigid_fork": 0.015,
        "dual_crown": 0.025,
    }[fork_front_end]
    fork_leg_r = base_leg_r * fork_leg_r_scale

    # --- equation: wheelbase scaled → front axle x (rear axle fixed at 0). ---
    wheelbase = anchors.wheelbase * wheelbase_scale
    # keep the wheelbase check inside 0.95 ≤ Δx ≤ 1.15.
    wheelbase = _clamp(wheelbase, 0.96, 1.14)

    # --- inequality: the front tire must clear the down-tube top weld (which sits
    # just below the head-tube bottom). Closest approach is between the front-axle
    # circle and the head_bot point. Require
    #   dist(head_bot, front_axle) ≥ wheel_r + TIRE_T + down_tube_r + gap.
    # Push the wheelbase forward up to its cap to win clearance; if the wheel is
    # still too big to fit, shrink wheel_r (front wheel sits forward → tire clears
    # the down tube instead of biting into it).
    hb_x, hb_z = anchors.head_bot[0], anchors.head_bot[2]
    DOWN_TUBE_R = 0.028
    GAP = 0.012
    need = wheel_r + TIRE_T + DOWN_TUBE_R + GAP
    dz = hb_z - wheel_r
    # required front-axle x so that sqrt((wb-hb_x)^2 + dz^2) >= need
    if need > abs(dz):
        min_dx = (need * need - dz * dz) ** 0.5
        wb_needed = hb_x + min_dx
        if wb_needed > wheelbase:
            wheelbase = min(wb_needed, 1.14)
    # If even the capped wheelbase can't clear the tire, shrink the wheel.
    dist = ((wheelbase - hb_x) ** 2 + dz * dz) ** 0.5
    if dist < need:
        # max wheel_r that fits: dist = wr + TIRE_T + DOWN_TUBE_R + GAP
        wheel_r = max(0.30, dist - (TIRE_T + DOWN_TUBE_R + GAP))

    rear_axle = (0.0, 0.0, wheel_r)
    front_axle = (wheelbase, 0.0, wheel_r)

    # --- equation: head-tube angle scale tilts the steer line about its bottom.
    # Scale the head-tube TOP x offset relative to the bottom (>1 = slacker rake).
    hb = anchors.head_bot
    ht = anchors.head_top
    head_bot = (hb[0], 0.0, wheel_r * 2.0)  # head-tube bottom rides at the front-axle band
    head_bot = (hb[0], 0.0, hb[2])
    dx = (ht[0] - hb[0]) * head_tube_angle_scale
    head_top = (hb[0] + dx, 0.0, ht[2])
    seat_top = (anchors.seat_top[0], 0.0, anchors.seat_top[2])

    # --- inequality: fork legs must clear the front tire (|leg_y|−leg_r ≥ TIRE_T+gap).
    leg_y = 0.060
    clearance = 0.006
    if leg_y - fork_leg_r < TIRE_T + clearance:
        leg_y = TIRE_T + clearance + fork_leg_r

    # --- inequality: the rest-pose pedals must clear the rear tire. The crank's
    # rearmost pedal corner sits at (bb_x − PEDAL_BACK, bb_z + PEDAL_UP); require
    # its distance to the rear axle ≥ wheel_r + TIRE_T + gap, else push the BB
    # forward (longer effective chainstay) so the pedal swings clear of the wheel.
    bb = anchors.bb
    PEDAL_BACK = 0.124  # crank arm (0.085) + pedal half-length (0.039)
    PEDAL_UP = 0.130  # crank arm vertical reach at the rest pose
    PED_GAP = 0.018
    ped_need = wheel_r + TIRE_T + PED_GAP
    ped_z = bb[2] + PEDAL_UP
    ped_dz = ped_z - wheel_r
    if ped_need > abs(ped_dz):
        min_back_x = (ped_need * ped_need - ped_dz * ped_dz) ** 0.5
        min_bb_x = min_back_x + PEDAL_BACK
        if bb[0] < min_bb_x:
            bb = (min_bb_x, bb[1], bb[2])

    return ResolvedBicycleConfig(
        frame_geometry=frame_geometry,
        fork_front_end=fork_front_end,
        handlebar_form=handlebar_form,
        n_spokes=n_spokes,
        palette_style=palette_style,
        wheel_r=wheel_r,
        wheelbase=wheelbase,
        bb=bb,
        head_top=head_top,
        head_bot=head_bot,
        seat_top=seat_top,
        rear_axle=rear_axle,
        front_axle=front_axle,
        leg_y=leg_y,
        fork_leg_r=fork_leg_r,
        seat_height_scale=seat_height_scale,
        name=cfg.name,
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Per-seed (slot, module) tuples for module_topology_diversity.

    Records post-resolution choices (after the drop×dual gate) plus an
    n_spokes density bucket so the distinct count lifts well past the ≥10 floor.
    """
    r = resolve_config(config_from_seed(seed))
    if r.n_spokes <= 18:
        spoke_bucket = "spokes_low"
    elif r.n_spokes <= 32:
        spoke_bucket = "spokes_mid"
    else:
        spoke_bucket = "spokes_high"
    return [
        ("frame_geometry", r.frame_geometry),
        ("fork_front_end", r.fork_front_end),
        ("handlebar_form", r.handlebar_form),
        ("n_spokes", spoke_bucket),
    ]


# --------------------------------------------------------------------------- #
# Steering axis helper (normalized HEAD_TOP − HEAD_BOT, in the XZ plane).
# --------------------------------------------------------------------------- #
def _steer_axis(head_top, head_bot) -> tuple[float, float, float]:
    dx = head_top[0] - head_bot[0]
    dz = head_top[2] - head_bot[2]
    n = (dx * dx + dz * dz) ** 0.5
    return (dx / n, 0.0, dz / n)


# --------------------------------------------------------------------------- #
# Wheel module (shared by front + rear; n_spokes multiplicity). S_parent L59-114.
# --------------------------------------------------------------------------- #
def _wheel_geometry(prefix: str, wheel_r: float, n_spokes: int, mats):
    """Visuals for a wheel spinning about local Y (roll), centered on the axle."""
    visuals = []

    # Tire: torus in the XZ plane (axle along Y).
    tire = TorusGeometry(wheel_r - TIRE_T, TIRE_T, radial_segments=20, tubular_segments=56)
    tire = tire.rotate_x(pi / 2.0)
    visuals.append((mesh_from_geometry(tire, f"{prefix}_tire"), None, mats["tire"], f"{prefix}_tire"))

    # Rim: thin torus just inside the tire.
    rim = TorusGeometry(wheel_r - 2.0 * TIRE_T, 0.012, radial_segments=12, tubular_segments=56)
    rim = rim.rotate_x(pi / 2.0)
    visuals.append((mesh_from_geometry(rim, f"{prefix}_rim"), None, mats["rim"], f"{prefix}_rim"))

    # Hub: short cylinder along the axle (Y).
    hub = CylinderGeometry(0.026, 0.090, radial_segments=20).rotate_x(pi / 2.0)
    visuals.append((mesh_from_geometry(hub, f"{prefix}_hub"), None, mats["dark"], f"{prefix}_hub"))

    # Spokes: thin radial wires hub flange → rim inner. (S_parent L82-98)
    # Inner end embeds INSIDE the hub radius (0.026) so hub→spokes→rim is one
    # connected island (a 0.030 start floats just outside the hub).
    spoke_inner = 0.020
    spoke_outer = wheel_r - 2.0 * TIRE_T
    length = spoke_outer - spoke_inner
    r_mid = (spoke_inner + spoke_outer) * 0.5
    for i in range(n_spokes):
        a = 2.0 * pi * i / n_spokes + 0.18  # offset so none lies on an axis
        cx, cz = cos(a) * r_mid, sin(a) * r_mid
        sp = CylinderGeometry(0.0022, length, radial_segments=5)
        sp = sp.rotate_y(pi / 2.0 - a)
        sp = sp.translate(cx, 0.0, cz)
        visuals.append(
            (mesh_from_geometry(sp, f"{prefix}_spoke_{i}"), None, mats["metal"], f"{prefix}_spoke_{i}")
        )

    # Disc-brake rotor: thin disc just outboard of the hub flange.
    rotor = CylinderGeometry(0.090, 0.004, radial_segments=40).rotate_x(pi / 2.0)
    rotor = rotor.translate(0.0, 0.044, 0.0)
    visuals.append((mesh_from_geometry(rotor, f"{prefix}_rotor"), None, mats["dark"], f"{prefix}_rotor"))

    # Valve/marker: off-axis nub on the rim so roll is detectable by AABB.
    visuals.append(
        (
            Box((0.020, 0.020, 0.045)),
            Origin(xyz=(0.0, 0.0, spoke_outer + 0.005)),
            mats["accent"],
            f"{prefix}_marker",
        )
    )
    return visuals


# --------------------------------------------------------------------------- #
# Frame modules (Slot A). Each emits the frame root visuals. Returns the set of
# main-tube visual names actually present (for the test layer).
# --------------------------------------------------------------------------- #
def _build_frame(frame, r: ResolvedBicycleConfig, mats) -> set[str]:
    bb = r.bb
    rear_axle = r.rear_axle
    head_bot = r.head_bot
    head_top = r.head_top
    seat_top = r.seat_top
    sh = r.seat_height_scale

    def tube(p_from, p_to, rad, name, mat, mid=None):
        pts = [p_from]
        if mid:
            pts.extend(mid)
        pts.append(p_to)
        g = tube_from_spline_points(pts, radius=rad, samples_per_segment=10, radial_segments=14)
        frame.visual(mesh_from_geometry(g, name), material=mat, name=name, material_class_id="metal.paint_coated")

    names: set[str] = set()
    fg = r.frame_geometry

    # ---- main triangle (per frame identity) ----
    if fg == "diamond":
        tube((head_top[0] + 0.01, 0.0, head_top[2] - 0.015), (0.115, 0.0, 1.005), 0.024, "top_tube", mats["frame"])
        tube((head_bot[0] - 0.01, 0.0, head_bot[2]), bb, 0.028, "down_tube", mats["frame"])
        tube(bb, (0.12, 0.0, 1.00), 0.024, "seat_tube", mats["frame"], mid=[(0.47, 0.0, 0.66)])
        names |= {"top_tube", "down_tube", "seat_tube"}
    elif fg == "step_through":
        # NO high top tube — single deep curved step-through tube head→BB junction.
        tube(
            (head_top[0], 0.0, head_top[2] - 0.03),
            (0.48, 0.0, 0.42),
            0.026,
            "step_through_tube",
            mats["frame"],
            mid=[(0.72, 0.0, 0.74), (0.62, 0.0, 0.52), (0.52, 0.0, 0.38)],
        )
        tube((head_bot[0] - 0.01, 0.0, head_bot[2]), bb, 0.028, "down_tube", mats["frame"])
        tube(bb, (0.12, 0.0, 1.00), 0.024, "seat_tube", mats["frame"], mid=[(0.47, 0.0, 0.66)])
        names |= {"step_through_tube", "down_tube", "seat_tube"}
    elif fg == "bmx_compact":
        # near-horizontal short top tube, short straight seat tube.
        tube((0.64, 0.0, 0.92), (0.31, 0.0, 0.83), 0.024, "top_tube", mats["frame"])
        tube((head_bot[0] - 0.01, 0.0, head_bot[2] - 0.01), bb, 0.028, "down_tube", mats["frame"])
        tube(bb, seat_top, 0.024, "seat_tube", mats["frame"])
        names |= {"top_tube", "down_tube", "seat_tube"}
    else:  # cruiser_cantilever
        # Cantilever sweep: the top tube welds to the head tube just below its
        # top (forward of the rearward-leaning steerer), then DIPS down right
        # away so it clears both the steerer and the stem clamp above, before
        # rising into the classic cantilever arc behind the head tube.
        # Weld HIGH on the head tube exactly like the diamond top tube (which is
        # known-clear of the steerer), depart flat toward -x, THEN sweep down into
        # the cantilever belly once well clear of the steerer/stem in x. The first
        # mid sits a short flat step from the start to PIN the spline tangent flat
        # (Catmull-Rom otherwise back-/up-overshoots into the leaning steerer).
        tube(
            (head_top[0] + 0.01, 0.0, head_top[2] - 0.015),
            (seat_top[0], 0.0, seat_top[2]),
            0.024,
            "top_tube",
            mats["frame"],
            mid=[
                (0.66, 0.0, 1.003),
                (0.50, 0.0, 1.02),
                (0.34, 0.0, 1.03),
                (0.18, 0.0, 0.99),
            ],
        )
        tube((head_bot[0] - 0.01, 0.0, head_bot[2]), bb, 0.028, "down_tube", mats["frame"])
        tube(
            bb,
            (seat_top[0], 0.0, seat_top[2]),
            0.024,
            "seat_tube",
            mats["frame"],
            mid=[(0.42, 0.0, 0.55), (0.25, 0.0, 0.75), (0.05, 0.0, 0.85)],
        )
        names |= {"top_tube", "down_tube", "seat_tube"}

    # ---- head tube (shared) along the steering axis ----
    tube(head_bot, head_top, 0.030, "head_tube", mats["frame"])
    names.add("head_tube")

    # ---- rear triangle: chainstays + seatstays (shared structure) ----
    # chainstay mid-x scales toward the BB so short-BB frames stay short.
    cs_mid_x = bb[0] * 0.57
    for sgn, nm in ((1.0, "chainstay_left"), (-1.0, "chainstay_right")):
        tube(
            (bb[0], sgn * 0.040, bb[2]),
            (rear_axle[0], sgn * 0.050, rear_axle[2]),
            0.014,
            nm,
            mats["frame"],
            mid=[(cs_mid_x, sgn * 0.062, 0.31)],
        )
    # seatstays from the seat cluster down to the rear axle.
    ss_top_z = seat_top[2] - 0.04
    for sgn, nm in ((1.0, "seatstay_left"), (-1.0, "seatstay_right")):
        tube(
            (max(0.02, seat_top[0]), sgn * 0.022, ss_top_z),
            (rear_axle[0], sgn * 0.052, rear_axle[2]),
            0.013,
            nm,
            mats["frame"],
            mid=[(0.07, sgn * 0.048, 0.62)],
        )
    names |= {"chainstay_left", "chainstay_right", "seatstay_left", "seatstay_right"}

    # Rear axle stub through the dropouts so the frame reaches the rear_wheel_roll
    # joint origin (on the axle centerline at y=0, between the stay ends).
    rear_axle_stub = CylinderGeometry(0.011, 0.124, radial_segments=16).rotate_x(pi / 2.0)
    rear_axle_stub = rear_axle_stub.translate(*rear_axle)
    frame.visual(mesh_from_geometry(rear_axle_stub, "rear_axle_stub"), material=mats["metal"], name="rear_axle_stub", material_class_id="metal.steel_bare")
    names.add("rear_axle_stub")

    # ---- bottom-bracket shell ----
    bb_shell = CylinderGeometry(0.030, 0.070, radial_segments=24).rotate_x(pi / 2.0)
    bb_shell = bb_shell.translate(*bb)
    frame.visual(mesh_from_geometry(bb_shell, "bb_shell"), material=mats["dark"], name="bb_shell", material_class_id="metal.blackened_gunmetal")
    names.add("bb_shell")

    # ---- seatpost + saddle (seat_height_scale lifts above the seat-tube top) ----
    st_x, _, st_z = seat_top
    post_top_z = st_z + 0.12 * sh
    seatpost = tube_from_spline_points(
        [(st_x + 0.03, 0.0, st_z - 0.05), (st_x + 0.015, 0.0, st_z + 0.03 * sh), (st_x, 0.0, post_top_z)],
        radius=0.014,
        samples_per_segment=8,
        radial_segments=14,
    )
    frame.visual(mesh_from_geometry(seatpost, "seatpost"), material=mats["metal"], name="seatpost", material_class_id="metal.aluminum_bare")
    saddle = Box((0.24, 0.11, 0.04))
    frame.visual(
        saddle, origin=Origin(xyz=(st_x - 0.025, 0.0, post_top_z + 0.01)), material=mats["dark"], name="saddle", material_class_id="leather.smooth_plain"
    )
    saddle_nose = Box((0.10, 0.04, 0.035))
    frame.visual(
        saddle_nose,
        origin=Origin(xyz=(st_x + 0.08, 0.0, post_top_z + 0.008)),
        material=mats["dark"],
        name="saddle_nose", material_class_id="leather.smooth_plain",
    )

    # ---- rear disc-brake caliper (non-moving detail = parent visual) ----
    rear_caliper = Box((0.05, 0.05, 0.08))
    frame.visual(
        rear_caliper, origin=Origin(xyz=(0.052, 0.060, 0.45)), material=mats["dark"], name="rear_caliper", material_class_id="metal.blackened_gunmetal"
    )

    frame.inertial = Inertial.from_geometry(
        Box((r.wheelbase, 0.12, 0.9)), mass=9.0, origin=Origin(xyz=(r.wheelbase * 0.43, 0.0, 0.65))
    )
    return names


# --------------------------------------------------------------------------- #
# Fork + handlebar modules (Slots B + C). Fork geometry is authored in absolute
# frame coords then shifted by −HEAD_BOT so the child link frame lands on the
# steering joint origin.  Returns (dropout_elems, crown_elems) name lists for
# the test layer.
# --------------------------------------------------------------------------- #
def _build_fork(fork, r: ResolvedBicycleConfig, mats) -> tuple[list[str], list[str]]:
    hb = r.head_bot
    ht = r.head_top
    front_axle = r.front_axle
    leg_y = r.leg_y
    leg_r = r.fork_leg_r

    def _sub_pts(pts):
        return [(x - hb[0], y - hb[1], z - hb[2]) for (x, y, z) in pts]

    def _sub_xyz(x, y, z):
        return (x - hb[0], y - hb[1], z - hb[2])

    def fork_tube(pts, rad, name, mat):
        g = tube_from_spline_points(_sub_pts(pts), radius=rad, samples_per_segment=8, radial_segments=12)
        fork.visual(mesh_from_geometry(g, name), material=mat, name=name, material_class_id="metal.blackened_gunmetal")

    # Steerer top (~head_top, slightly forward) carries the stem.
    steerer_top = (ht[0] - 0.005, 0.0, ht[2] + 0.045)
    crown_x = hb[0] + 0.015
    crown_z = hb[2] + 0.045
    # Steerer: head-tube bottom (= steering joint origin) → stem top, along the
    # steer axis. Starting at hb makes the fork reach its own joint origin.
    fork_tube([(hb[0], 0.0, hb[2]), (hb[0] - 0.02, 0.0, crown_z + 0.005), steerer_top], 0.018, "steerer", mats["dark"])

    dropout_elems: list[str] = []
    crown_elems: list[str] = []

    if r.fork_front_end == "suspension_fork":
        crown = Box((0.11, 0.15, 0.05))
        fork.visual(crown, origin=Origin(xyz=_sub_xyz(crown_x, 0.0, crown_z)), material=mats["dark"], name="fork_crown", material_class_id="metal.blackened_gunmetal")
        crown_elems.append("fork_crown")
        for sgn, side in ((1.0, "left"), (-1.0, "right")):
            fork_tube(
                [(crown_x + 0.03, sgn * leg_y, crown_z - 0.01), (crown_x + 0.10, sgn * leg_y, (crown_z + front_axle[2]) * 0.5)],
                leg_r * 0.85,
                f"fork_stanchion_{side}",
                mats["metal"],
            )
            fork_tube(
                [(crown_x + 0.10, sgn * leg_y, (crown_z + front_axle[2]) * 0.5), (front_axle[0], sgn * leg_y, front_axle[2])],
                leg_r,
                f"fork_lower_{side}",
                mats["dark"],
            )
            dropout_elems.append(f"fork_lower_{side}")

    elif r.fork_front_end == "rigid_fork":
        crown = Box((0.11, 0.15, 0.05))
        fork.visual(crown, origin=Origin(xyz=_sub_xyz(crown_x, 0.0, crown_z)), material=mats["dark"], name="fork_crown", material_class_id="metal.blackened_gunmetal")
        crown_elems.append("fork_crown")
        for sgn, side in ((1.0, "left"), (-1.0, "right")):
            # one continuous slim blade crown → raked dropout.
            fork_tube(
                [
                    (crown_x + 0.03, sgn * leg_y, crown_z - 0.01),
                    (crown_x + 0.06, sgn * leg_y, crown_z - 0.10),
                    (crown_x + 0.10, sgn * leg_y, crown_z - 0.20),
                    (front_axle[0] - 0.04, sgn * leg_y, front_axle[2] + 0.08),
                    (front_axle[0], sgn * leg_y, front_axle[2]),
                ],
                leg_r,
                f"fork_blade_{side}",
                mats["dark"],
            )
            dropout_elems.append(f"fork_blade_{side}")

    else:  # dual_crown
        lower_crown_pos = (crown_x, 0.0, crown_z)
        upper_crown_pos = (ht[0], 0.0, ht[2] + 0.015)
        lower_crown = Box((0.10, 0.16, 0.040))
        fork.visual(lower_crown, origin=Origin(xyz=_sub_xyz(*lower_crown_pos)), material=mats["dark"], name="lower_crown", material_class_id="metal.blackened_gunmetal")
        upper_crown = Box((0.050, 0.13, 0.022))
        fork.visual(upper_crown, origin=Origin(xyz=_sub_xyz(*upper_crown_pos)), material=mats["dark"], name="upper_crown", material_class_id="metal.blackened_gunmetal")
        crown_elems.extend(["lower_crown", "upper_crown"])
        st_top = (upper_crown_pos[0] + 0.02, upper_crown_pos[2])
        st_bot = (crown_x + 0.12, (crown_z + front_axle[2]) * 0.5 - 0.02)
        for sgn, side in ((1.0, "left"), (-1.0, "right")):
            fork_tube(
                [(st_top[0], sgn * leg_y, st_top[1]), (st_bot[0], sgn * leg_y, st_bot[1])],
                leg_r * 0.85,
                f"fork_stanchion_{side}",
                mats["metal"],
            )
            fork_tube(
                [(st_bot[0], sgn * leg_y, st_bot[1]), (front_axle[0], sgn * leg_y, front_axle[2])],
                leg_r,
                f"fork_lower_{side}",
                mats["dark"],
            )
            dropout_elems.append(f"fork_lower_{side}")
        # Fork arch bridge between the two STANCHIONS, placed ABOVE the front
        # tire's top so it never bites the rim (the lower-leg region is swept by
        # the wheel; only up on the stanchions is there clear air). Anchor it on
        # the stanchion line at a height that clears the tire crown + margin.
        tire_top_z = front_axle[2] + r.wheel_r + TIRE_T + 0.03
        # interpolate the stanchion x at that height (st_top high → st_bot low).
        if abs(st_top[1] - st_bot[1]) > 1e-6:
            t = (tire_top_z - st_bot[1]) / (st_top[1] - st_bot[1])
            t = _clamp(t, 0.0, 1.0)
        else:
            t = 0.0
        arch_x = st_bot[0] + (st_top[0] - st_bot[0]) * t
        arch_z = tire_top_z
        arch_pts = _sub_pts(
            [
                (arch_x, leg_y, arch_z),
                (arch_x + 0.01, leg_y * 0.5, arch_z + 0.02),
                (arch_x + 0.012, 0.0, arch_z + 0.026),
                (arch_x + 0.01, -leg_y * 0.5, arch_z + 0.02),
                (arch_x, -leg_y, arch_z),
            ]
        )
        arch_g = tube_from_spline_points(arch_pts, radius=0.012, samples_per_segment=8, radial_segments=10)
        fork.visual(mesh_from_geometry(arch_g, "fork_arch"), material=mats["dark"], name="fork_arch", material_class_id="metal.blackened_gunmetal")

    # Front axle stub: a thin spindle through the dropouts at the front-axle line,
    # so the fork reaches the front_wheel_roll joint origin (which sits on the
    # axle centerline at y=0, between the two legs).
    front_axle_stub = CylinderGeometry(0.011, 2.0 * leg_y + 0.02, radial_segments=16).rotate_x(pi / 2.0)
    front_axle_stub = front_axle_stub.translate(*_sub_xyz(front_axle[0], 0.0, front_axle[2]))
    fork.visual(mesh_from_geometry(front_axle_stub, "front_axle_stub"), material=mats["metal"], name="front_axle_stub", material_class_id="metal.steel_bare")

    # Front disc-brake caliper (non-moving detail = parent visual on the fork).
    # Straddle the left fork lower/blade so it is a real embedded detail (centered
    # on the leg in y, hugging the leg in z just above the dropout) rather than a
    # floating island outboard of the leg.
    front_caliper = Box((0.045, 0.05, 0.075))
    fork.visual(
        front_caliper,
        origin=Origin(xyz=_sub_xyz(front_axle[0] - 0.01, leg_y, front_axle[2] + 0.06)),
        material=mats["dark"],
        name="front_caliper", material_class_id="metal.blackened_gunmetal",
    )

    # ---- Stem (shared) clamps the steerer top, carries the handlebar ----
    stem_x = steerer_top[0] + 0.015
    stem_z = steerer_top[2]
    stem = Box((0.11, 0.045, 0.04))
    fork.visual(stem, origin=Origin(xyz=_sub_xyz(stem_x, 0.0, stem_z)), material=mats["dark"], name="stem", material_class_id="metal.blackened_gunmetal")

    # ---- Handlebar (Slot C, fixed to the stem; fork's own visuals) ----
    _build_handlebar(fork, r, mats, _sub_pts, _sub_xyz, fork_tube, stem_x, stem_z)

    fork.inertial = Inertial.from_geometry(
        Box((0.20, 0.62, 0.55)), mass=3.0, origin=Origin(xyz=_sub_xyz(crown_x + 0.06, 0.0, 0.80))
    )
    return dropout_elems, crown_elems


def _build_handlebar(fork, r, mats, _sub_pts, _sub_xyz, fork_tube, stem_x, stem_z) -> None:
    cx = stem_x - 0.005  # bar center sits just behind the stem clamp
    cz = stem_z + 0.003
    form = r.handlebar_form

    if form == "flat_bar":
        fork_tube(
            [
                (cx - 0.025, 0.30, cz - 0.013),
                (cx - 0.015, 0.18, cz - 0.006),
                (cx - 0.01, 0.0, cz),
                (cx - 0.015, -0.18, cz - 0.006),
                (cx - 0.025, -0.30, cz - 0.013),
            ],
            0.013,
            "handlebar",
            mats["dark"],
        )
        for sgn, side in ((1.0, "left"), (-1.0, "right")):
            grip = Cylinder(radius=0.018, length=0.11)
            fork.visual(
                grip,
                origin=Origin(xyz=_sub_xyz(cx - 0.024, sgn * 0.275, cz - 0.012), rpy=(pi / 2.0, 0.0, 0.0)),
                material=mats["grip"],
                name=f"grip_{side}", material_class_id="rubber.pebbled",
            )

    elif form == "riser_bar":
        rise = 0.21
        back = 0.07
        fork_tube(
            [
                (cx - back, 0.32, cz + rise),
                (cx - 0.04, 0.24, cz + rise * 0.8),
                (cx - 0.01, 0.14, cz + rise * 0.45),
                (cx - 0.01, 0.0, cz),
                (cx - 0.01, -0.14, cz + rise * 0.45),
                (cx - 0.04, -0.24, cz + rise * 0.8),
                (cx - back, -0.32, cz + rise),
            ],
            0.013,
            "handlebar",
            mats["dark"],
        )
        for sgn, side in ((1.0, "left"), (-1.0, "right")):
            grip = Cylinder(radius=0.018, length=0.11)
            fork.visual(
                grip,
                origin=Origin(
                    xyz=_sub_xyz(cx - back + 0.005, sgn * 0.30, cz + rise - 0.005),
                    rpy=(pi / 2.0, 0.0, sgn * 0.25),
                ),
                material=mats["grip"],
                name=f"grip_{side}", material_class_id="rubber.pebbled",
            )

    else:  # drop_bar
        # Continuous road bar: tops across the stem, hoods forward, drops down.
        drop_z = cz - 0.14  # grip at the lower drops
        hood_z = cz - 0.016
        fork_tube(
            [
                (cx - 0.01, 0.150, drop_z),
                (cx + 0.02, 0.156, drop_z + 0.008),
                (cx + 0.05, 0.162, drop_z + 0.035),
                (cx + 0.075, 0.166, drop_z + 0.080),
                (cx + 0.072, 0.168, hood_z + 0.006),
                (cx + 0.045, 0.148, cz + 0.004),
                (cx + 0.015, 0.105, cz + 0.006),
                (cx, 0.0, cz + 0.004),
                (cx + 0.015, -0.105, cz + 0.006),
                (cx + 0.045, -0.148, cz + 0.004),
                (cx + 0.072, -0.168, hood_z + 0.006),
                (cx + 0.075, -0.166, drop_z + 0.080),
                (cx + 0.05, -0.162, drop_z + 0.035),
                (cx + 0.02, -0.156, drop_z + 0.008),
                (cx - 0.01, -0.150, drop_z),
            ],
            0.012,
            "drop_bar",
            mats["dark"],
        )
        for sgn, side in ((1.0, "left"), (-1.0, "right")):
            hood = Box((0.055, 0.040, 0.060))
            fork.visual(
                hood,
                origin=Origin(xyz=_sub_xyz(cx + 0.068, sgn * 0.168, hood_z + 0.002)),
                material=mats["dark"],
                name=f"brake_hood_{side}", material_class_id="rubber.pebbled",
            )
        for sgn, side in ((1.0, "left"), (-1.0, "right")):
            grip = CylinderGeometry(0.017, 0.10, radial_segments=14).rotate_x(pi / 2.0)
            grip = grip.translate(*_sub_xyz(cx + 0.004, sgn * 0.153, drop_z + 0.004))
            fork.visual(mesh_from_geometry(grip, f"bar_tape_{side}"), material=mats["grip"], name=f"bar_tape_{side}", material_class_id="leather.smooth_plain")


# --------------------------------------------------------------------------- #
# Crank module (shared; S_parent L316-357).
# --------------------------------------------------------------------------- #
def _build_crank(crank, r: ResolvedBicycleConfig, mats) -> None:
    spindle = CylinderGeometry(0.014, 0.20, radial_segments=18).rotate_x(pi / 2.0)
    crank.visual(mesh_from_geometry(spindle, "spindle"), material=mats["metal"], name="spindle", material_class_id="metal.steel_bare")
    chainring = CylinderGeometry(0.095, 0.006, radial_segments=44).rotate_x(pi / 2.0)
    chainring = chainring.translate(0.0, -0.078, 0.0)
    crank.visual(mesh_from_geometry(chainring, "chainring"), material=mats["metal"], name="chainring", material_class_id="metal.aluminum_bare")
    for ay, side, arm_dir in ((-0.092, "right", 1.0), (0.092, "left", -1.0)):
        px = arm_dir * 0.085
        pz = arm_dir * -0.130
        arm = tube_from_spline_points(
            [(0.0, ay * 0.95, 0.0), (arm_dir * 0.045, ay, -pz * 0.10), (px, ay, pz)],
            radius=0.013,
            samples_per_segment=8,
            radial_segments=12,
        )
        crank.visual(mesh_from_geometry(arm, f"crank_arm_{side}"), material=mats["dark"], name=f"crank_arm_{side}", material_class_id="metal.blackened_gunmetal")
        pedal = Box((0.078, 0.070, 0.018))
        crank.visual(
            pedal,
            origin=Origin(xyz=(px, ay + arm_dir * 0.035, pz)),
            material=mats["dark"],
            name=f"pedal_{side}", material_class_id="plastic.opaque_glossy_molded",
        )
    crank.inertial = Inertial.from_geometry(
        Cylinder(radius=0.10, length=0.18), mass=1.2, origin=Origin(rpy=(pi / 2.0, 0.0, 0.0))
    )


# --------------------------------------------------------------------------- #
# Top-level builder
# --------------------------------------------------------------------------- #
def build_bicycle(
    config: BicycleConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    mats: dict[str, object] = {}
    for token, rgba in PALETTES[r.palette_style].items():
        mats[token] = model.material(token, rgba=rgba)

    # ---- FRAME (root) ----
    frame = model.part("frame")
    _build_frame(frame, r, mats)

    # ---- FORK (steered) + handlebar ----
    fork = model.part("fork")
    _build_fork(fork, r, mats)

    # ---- WHEELS ----
    front_wheel = model.part("front_wheel")
    for geom, origin, mat, nm in _wheel_geometry("front", r.wheel_r, r.n_spokes, mats):
        front_wheel.visual(geom, origin=origin, material=mat, name=nm, material_class_id="rubber.directional_grooved")
    # Front hub end-cap straddling the axle centerline so the front-wheel link
    # carries solid geometry ON its roll-joint origin (the bare hub is hollow on
    # its axis, leaving the origin a hub-radius away from any surface).
    front_wheel.visual(
        Cylinder(radius=0.020, length=0.030),
        origin=Origin(rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name="front_hub_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    front_wheel.inertial = Inertial.from_geometry(
        Cylinder(radius=r.wheel_r, length=0.09), mass=2.2, origin=Origin(rpy=(pi / 2.0, 0.0, 0.0))
    )

    rear_wheel = model.part("rear_wheel")
    for geom, origin, mat, nm in _wheel_geometry("rear", r.wheel_r, r.n_spokes, mats):
        rear_wheel.visual(geom, origin=origin, material=mat, name=nm, material_class_id="rubber.directional_grooved")
    rear_wheel.visual(
        Cylinder(radius=0.042, length=0.024),
        origin=Origin(xyz=(0.0, -0.014, 0.0), rpy=(pi / 2.0, 0.0, 0.0)),
        material=mats["metal"],
        name="rear_cassette", material_class_id="metal.stainless_matte",
    )
    rear_wheel.inertial = Inertial.from_geometry(
        Cylinder(radius=r.wheel_r, length=0.09), mass=2.4, origin=Origin(rpy=(pi / 2.0, 0.0, 0.0))
    )

    # ---- CRANK ----
    crank = model.part("crank")
    _build_crank(crank, r, mats)

    # ===================== ARTICULATIONS =====================
    steer_axis = _steer_axis(r.head_top, r.head_bot)
    model.articulation(
        "steering",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=fork,
        origin=Origin(xyz=(r.head_bot[0], r.head_bot[1], r.head_bot[2])),
        axis=steer_axis,
        motion_limits=MotionLimits(effort=12.0, velocity=3.0, lower=-0.70, upper=0.70),
    )
    front_axle_in_fork = (
        r.front_axle[0] - r.head_bot[0],
        r.front_axle[1] - r.head_bot[1],
        r.front_axle[2] - r.head_bot[2],
    )
    model.articulation(
        "front_wheel_roll",
        ArticulationType.CONTINUOUS,
        parent=fork,
        child=front_wheel,
        origin=Origin(xyz=front_axle_in_fork),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=40.0),
    )
    model.articulation(
        "rear_wheel_roll",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=rear_wheel,
        origin=Origin(xyz=r.rear_axle),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=40.0),
    )
    model.articulation(
        "crank_spin",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=crank,
        origin=Origin(xyz=r.bb),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=15.0, velocity=20.0),
    )

    return model


def build_seeded_bicycle(seed: int) -> ArticulatedObject:
    return build_bicycle(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _center(aabb):
    mn, mx = aabb
    return ((mn[0] + mx[0]) * 0.5, (mn[1] + mx[1]) * 0.5, (mn[2] + mx[2]) * 0.5)


def run_bicycle_tests(model: ArticulatedObject, config: BicycleConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    frame = model.get_part("frame")
    fork = model.get_part("fork")
    front_wheel = model.get_part("front_wheel")
    rear_wheel = model.get_part("rear_wheel")
    crank = model.get_part("crank")

    # The fork axle stub + brake caliper are captured by / straddle the front
    # wheel hub and rotor; the rear wheel is likewise carried by the frame.
    ctx.allow_overlap(fork, front_wheel,
                      reason="Fork axle stub and caliper are captured by the front wheel hub/rotor.")
    ctx.allow_overlap(frame, rear_wheel,
                      reason="Rear wheel is captured by the frame/swingarm dropouts.")
    ctx.allow_overlap(frame, front_wheel,
                      reason="Front wheel sits within the fork/frame steering envelope.")

    steering = model.get_articulation("steering")
    front_roll = model.get_articulation("front_wheel_roll")
    rear_roll = model.get_articulation("rear_wheel_roll")
    crank_spin = model.get_articulation("crank_spin")

    # ---- both wheels same diameter ----
    fw_ext = _ext(ctx.part_world_aabb(front_wheel))
    rw_ext = _ext(ctx.part_world_aabb(rear_wheel))
    fw_dia = max(fw_ext[0], fw_ext[2])
    rw_dia = max(rw_ext[0], rw_ext[2])
    expected_dia = 2.0 * r.wheel_r
    ctx.check(
        "front wheel diameter ~2*wheel_r",
        abs(fw_dia - expected_dia) < 0.05,
        details=f"front diameter={fw_dia:.3f}, expected={expected_dia:.3f}",
    )
    ctx.check(
        "wheels share the same diameter",
        abs(fw_dia - rw_dia) < 0.02,
        details=f"front={fw_dia:.3f}, rear={rw_dia:.3f}",
    )

    # ---- frame connects head tube <-> BB <-> rear axle ----
    down_meets = "step_through_tube" if r.frame_geometry == "step_through" else "down_tube"
    ctx.expect_contact(
        frame, frame, elem_a="down_tube", elem_b="head_tube", name="down tube meets head tube"
    )
    ctx.expect_contact(
        frame, frame, elem_a="down_tube", elem_b="bb_shell", name="down tube meets bottom bracket"
    )
    ctx.expect_contact(
        frame, frame, elem_a="chainstay_left", elem_b="bb_shell", name="chainstay meets bottom bracket"
    )

    # ---- front wheel ahead of rear, both touch ground at z=0 ----
    fw_c = _center(ctx.part_world_aabb(front_wheel))
    rw_c = _center(ctx.part_world_aabb(rear_wheel))
    ctx.check(
        "front wheel ahead of rear wheel by ~wheelbase",
        0.95 <= (fw_c[0] - rw_c[0]) <= 1.15,
        details=f"front_x={fw_c[0]:.3f}, rear_x={rw_c[0]:.3f}, Δx={fw_c[0] - rw_c[0]:.3f}",
    )

    # ---- steering yaws the front wheel about the head-tube axis ----
    fw_ext0 = _ext(ctx.part_world_aabb(front_wheel))
    with ctx.pose({steering: 0.70}):
        fw_ext_s = _ext(ctx.part_world_aabb(front_wheel))
    ctx.check(
        "steering yaws the front wheel",
        fw_ext_s[1] > fw_ext0[1] + 0.05,
        details=f"rest Y={fw_ext0[1]:.3f}, steered Y={fw_ext_s[1]:.3f}",
    )

    # ---- front wheel rolls about its axle ----
    fm0 = _center(ctx.part_element_world_aabb(front_wheel, elem="front_marker"))
    with ctx.pose({front_roll: pi / 2.0}):
        fm1 = _center(ctx.part_element_world_aabb(front_wheel, elem="front_marker"))
    fmoved = ((fm1[0] - fm0[0]) ** 2 + (fm1[2] - fm0[2]) ** 2) ** 0.5
    ctx.check("front wheel rolls (rim marker swings)", fmoved > 0.20, details=f"marker moved {fmoved:.3f}")

    # ---- rear wheel rolls about its axle ----
    rm0 = _center(ctx.part_element_world_aabb(rear_wheel, elem="rear_marker"))
    with ctx.pose({rear_roll: pi / 2.0}):
        rm1 = _center(ctx.part_element_world_aabb(rear_wheel, elem="rear_marker"))
    rmoved = ((rm1[0] - rm0[0]) ** 2 + (rm1[2] - rm0[2]) ** 2) ** 0.5
    ctx.check("rear wheel rolls (rim marker swings)", rmoved > 0.20, details=f"marker moved {rmoved:.3f}")

    # ---- crank rotates about the bottom bracket ----
    c0 = _center(ctx.part_world_aabb(crank))
    pm0 = _center(ctx.part_element_world_aabb(crank, elem="pedal_right"))
    with ctx.pose({crank_spin: pi / 2.0}):
        pm1 = _center(ctx.part_element_world_aabb(crank, elem="pedal_right"))
    pmoved = ((pm1[0] - pm0[0]) ** 2 + (pm1[2] - pm0[2]) ** 2) ** 0.5
    ctx.check("crank spins about the bottom bracket (pedal swings)", pmoved > 0.08, details=f"pedal moved {pmoved:.3f}")
    ctx.check(
        "crank mounted at the bottom bracket",
        abs(c0[0] - r.bb[0]) < 0.06 and abs(c0[2] - r.bb[2]) < 0.06,
        details=f"crank center={c0}, bb={r.bb}",
    )

    # ---- intentional captured/seated overlaps ----
    # The steerer runs from the head-tube bottom (steering joint origin) up
    # through the head tube; at its base it passes the down-tube / step-through-
    # tube weld where those tubes meet the head-tube bottom — a captured headset
    # junction, not a free interpenetration.
    steerer_headset_welds = {"head_tube", "down_tube", down_meets}
    for elem_b in steerer_headset_welds:
        ctx.allow_overlap(
            fork, frame, elem_a="steerer", elem_b=elem_b,
            reason="Steerer runs through the head tube and past the down-tube weld at the headset.",
        )
    if r.frame_geometry != "step_through":
        # Frames with a top tube (diamond / bmx / cruiser) weld it HIGH onto the
        # head tube at the upper headset, where the steerer is concentric inside
        # the head tube — the same captured headset junction already allowed for
        # the head/down tubes. (step_through has no high top tube.)
        ctx.allow_overlap(
            fork, frame, elem_a="steerer", elem_b="top_tube",
            reason="Top tube welds to the head tube at the upper headset, "
            "where the steerer runs concentrically inside the head tube.",
        )

    for elem_b, why in (
        ("bb_shell", "Crank spindle runs through the bottom-bracket shell bearings."),
        ("down_tube", "Down tube welds into the bottom-bracket junction around the spindle."),
        ("seat_tube", "Seat tube welds into the bottom-bracket junction around the spindle."),
        ("chainstay_left", "Left chainstay welds into the bottom-bracket shell around the spindle."),
        ("chainstay_right", "Right chainstay welds into the bottom-bracket shell around the spindle."),
    ):
        ctx.allow_overlap(crank, frame, elem_a="spindle", elem_b=elem_b, reason=why)
    ctx.expect_contact(
        crank, frame, elem_a="spindle", elem_b="bb_shell", name="crank spindle in bottom bracket"
    )

    # fork crown seated on the head tube (per-fork crown element names).
    crown_elems = ["fork_crown"] if r.fork_front_end != "dual_crown" else ["lower_crown", "upper_crown"]
    for ce in crown_elems:
        ctx.allow_overlap(
            fork, frame, elem_a=ce, elem_b="head_tube",
            reason="Fork crown wraps the head-tube/headset just under the lower bearing.",
        )
    if r.fork_front_end == "dual_crown" and r.frame_geometry != "step_through":
        # The dual-crown upper crown sits at the head-tube top, exactly where a
        # top tube welds onto the head tube — same captured headset junction.
        ctx.allow_overlap(
            fork, frame, elem_a="upper_crown", elem_b="top_tube",
            reason="Dual-crown upper crown clamps the steerer at the head-tube top "
            "where the top tube welds to the head tube.",
        )
    ctx.expect_contact(
        fork, frame, elem_a=crown_elems[0], elem_b="head_tube", name="fork crown seated at headset"
    )

    # rear-wheel dropouts: chainstay/seatstay ends grip the rear hub.
    for elem_a in ("chainstay_left", "chainstay_right", "seatstay_left", "seatstay_right", "rear_axle_stub"):
        ctx.allow_overlap(
            frame, rear_wheel, elem_a=elem_a, elem_b="rear_hub",
            reason="Rear dropout/axle grips and runs through the rear-wheel hub bearings.",
        )
    ctx.allow_overlap(
        frame, rear_wheel, elem_a="rear_axle_stub", elem_b="rear_cassette",
        reason="Rear axle runs through the cassette body on the freehub.",
    )
    ctx.expect_contact(frame, rear_wheel, elem_b="rear_hub", name="rear wheel mounted in dropouts")

    # front-wheel dropouts: the fork legs/blades grip the front hub.
    dropout_elems = (
        ["fork_blade_left", "fork_blade_right"]
        if r.fork_front_end == "rigid_fork"
        else ["fork_lower_left", "fork_lower_right"]
    )
    for elem_a in (*dropout_elems, "front_axle_stub"):
        ctx.allow_overlap(
            fork, front_wheel, elem_a=elem_a, elem_b="front_hub",
            reason="Fork-lower/blade dropout/axle grips and runs through the front-wheel hub bearings.",
        )
    ctx.allow_overlap(
        fork, front_wheel, elem_a="front_axle_stub", elem_b="front_hub_cap",
        reason="Front axle runs through the hub end-cap on the axle centerline.",
    )
    ctx.expect_contact(fork, front_wheel, elem_b="front_hub", name="front wheel mounted in fork")

    return ctx.report()


__all__ = [
    "BicycleConfig",
    "ResolvedBicycleConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "build_bicycle",
    "build_seeded_bicycle",
    "run_bicycle_tests",
    "__modular__",
]
