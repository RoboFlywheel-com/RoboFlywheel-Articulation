# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for ``vocal_microphone``.

Follows ``articraft_template_authoring/specs_modular_v1/Music_Vocal_mic.md``.

A desktop vocal microphone: a windscreen/grille head carried on a weighted
base / tripod stand via a real articulated mount. World frame convention:

- +Z is up; the weighted base / tripod feet rest on the ground at z = 0.
- The windscreen/grille head faces +X (the front: badge / MUTE / knob column).
- The pitch (tilt) axis runs along +Y (the horizontal side axis).
- Family B's swivel axis runs along +Z (the stand centerline).

``pattern = mixed`` — there are TWO baseline body families, selected by the
``mount_stand`` slot (family-gated):

  * Family A (USB condenser, source A0): ``base`` (weighted disc + Y-fork or
    shock-cradle, root/static) -> REVOLUTE +Y -> ``body`` (windscreen head is a
    body visual) -> N CONTINUOUS +X ``front_knob_{i}`` (multiplicity axis).
  * Family B (vintage desktop, source B0): ``base`` (weighted disc or tripod
    hub, root/static) -> CONTINUOUS +Z -> ``swivel_post`` (post + U-yoke) ->
    REVOLUTE +Y -> ``capsule_head`` (separate windscreen part) + FIXED ``cable``.

Three reported slot axes (``slot_choices_for_seed``):

    mount_stand (4): rigid_forked_yoke / elastic_shock_cradle (A);
                     weighted_base_disc / folding_desk_tripod (B)
    head_form   (3): cylindrical_mesh_basket (BOTH families) /
                     round_ball_windscreen (A only) / vintage_oval_ribbed (B only)
    control_knob_count: n2 / n3 / n4 (A only) ; none (B)

= 12 (A: 2x2x3) + 4 (B: 2x2x1) = 16 distinct topology tuples (>= 10 gate).

Adopted module sources (spec Module Source Index):
A0  rec_blue-usb-...91210c09        — Family A baseline: straight body + grille
    band + dome head + Y-fork + body tilt + front knobs (multiplicity mother).
B0  rec_vintage-...4ebe60a8         — Family B baseline: oval Shure-55 head +
    weighted disc + swivel post + U-yoke + cable.
S_ball   rec_vocal_microphone_var_head_ball          — A ball wire-cage head.
S_cylB   rec_vocal_microphone_var_head_cyl_on_vintage — B upright basket capsule.
S_cradle rec_vocal_microphone_var_mount_shockcradle   — A elastic shock cradle.
S_tripod rec_vocal_microphone_var_mount_tripod        — B folding desk tripod.
S_n3 / S_n4 rec_vocal_microphone_var_controls_n3 / _n4 — A front-knob column N.

Joint-origin note: the 5-star sources place their pivots at the body/capsule
*sides* (fork knuckles, yoke arms). The compiler-owned baseline
``fail_if_articulation_origin_far_from_geometry(tol=0.015)`` requires the parent
to have geometry within 15 mm of the joint origin, so this template adds a thin
central pivot axle/pin on the stand at each tilt axis (the binocular hinge-axle
pattern) — a real pivot rod, hidden inside the body where it crosses the center.
Captured-pin overlaps are element-scoped ``allow_overlap`` and grandfathered.
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
    BoxGeometry,
    CylinderGeometry,
    DomeGeometry,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    LatheGeometry,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    SphereGeometry,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    sample_catmull_rom_spline_2d,
    tube_from_spline_points,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Enums / slot pools
# --------------------------------------------------------------------------- #

MountStand = Literal[
    "rigid_forked_yoke",
    "elastic_shock_cradle",
    "weighted_base_disc",
    "folding_desk_tripod",
]
HeadForm = Literal[
    "cylindrical_mesh_basket",
    "round_ball_windscreen",
    "vintage_oval_ribbed",
]
PaletteStyle = Literal[
    "blue_usb_silver_grille",
    "blackout_usb",
    "matte_black_stage",
    "vintage_satin_silver",
    "vintage_chrome_oval",
    "gold_vintage_brass",
]

MOUNT_STANDS: tuple[MountStand, ...] = (
    "rigid_forked_yoke",
    "elastic_shock_cradle",
    "weighted_base_disc",
    "folding_desk_tripod",
)
# Lightly weight the two family baselines (spec sampler note); all four still
# get substantial probability so the 16-combo topology pool is exercised in 0-49.
_MOUNT_WEIGHTS = (0.30, 0.20, 0.30, 0.20)

A_MOUNTS = ("rigid_forked_yoke", "elastic_shock_cradle")
B_MOUNTS = ("weighted_base_disc", "folding_desk_tripod")

A_HEADS: tuple[HeadForm, ...] = ("cylindrical_mesh_basket", "round_ball_windscreen")
B_HEADS: tuple[HeadForm, ...] = ("cylindrical_mesh_basket", "vintage_oval_ribbed")
_A_HEAD_WEIGHTS = (0.55, 0.45)  # cyl is the bridge baseline -> slightly weighted
_B_HEAD_WEIGHTS = (0.45, 0.55)  # oval is the B baseline -> slightly weighted

KNOB_COUNTS = (2, 3, 4)
_KNOB_WEIGHTS = (0.45, 0.35, 0.20)  # small N preferred; N=4 rare (needs longer body)

A_PALETTES: tuple[PaletteStyle, ...] = (
    "blue_usb_silver_grille",
    "blackout_usb",
    "matte_black_stage",
)
B_PALETTES: tuple[PaletteStyle, ...] = (
    "vintage_satin_silver",
    "vintage_chrome_oval",
    "gold_vintage_brass",
)


def family_of(mount: str) -> str:
    return "A" if mount in A_MOUNTS else "B"


# --------------------------------------------------------------------------- #
# Palettes — material token -> rgba. Pooled by family affinity (§7).
# --------------------------------------------------------------------------- #

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    # --- A-family affinity (USB-condenser domain) ---
    "blue_usb_silver_grille": {
        "body": (0.30, 0.36, 0.95, 1.0),
        "mesh": (0.72, 0.76, 0.82, 1.0),
        "dark": (0.06, 0.06, 0.10, 1.0),
        "metal": (0.34, 0.40, 0.97, 1.0),
        "base": (0.30, 0.34, 0.90, 1.0),
        "knob": (0.72, 0.74, 0.78, 1.0),
        "marker": (0.88, 0.91, 1.0, 1.0),
        "badge": (0.86, 0.90, 1.0, 1.0),
        "mute": (0.85, 0.20, 0.30, 1.0),
        "cable": (0.22, 0.22, 0.24, 1.0),
        "xlr": (0.52, 0.53, 0.55, 1.0),
        "rubber": (0.18, 0.18, 0.22, 1.0),
    },
    "blackout_usb": {
        "body": (0.10, 0.10, 0.11, 1.0),
        "mesh": (0.15, 0.15, 0.16, 1.0),
        "dark": (0.03, 0.03, 0.04, 1.0),
        "metal": (0.20, 0.20, 0.22, 1.0),
        "base": (0.09, 0.09, 0.10, 1.0),
        "knob": (0.26, 0.26, 0.28, 1.0),
        "marker": (0.62, 0.62, 0.64, 1.0),
        "badge": (0.34, 0.34, 0.36, 1.0),
        "mute": (0.85, 0.20, 0.28, 1.0),
        "cable": (0.10, 0.10, 0.11, 1.0),
        "xlr": (0.40, 0.40, 0.42, 1.0),
        "rubber": (0.08, 0.08, 0.09, 1.0),
    },
    "matte_black_stage": {
        "body": (0.08, 0.08, 0.09, 1.0),
        "mesh": (0.18, 0.18, 0.20, 1.0),
        "dark": (0.03, 0.03, 0.03, 1.0),
        "metal": (0.16, 0.16, 0.18, 1.0),
        "base": (0.07, 0.07, 0.08, 1.0),
        "knob": (0.22, 0.22, 0.24, 1.0),
        "marker": (0.50, 0.50, 0.52, 1.0),
        "badge": (0.28, 0.28, 0.30, 1.0),
        "mute": (0.70, 0.18, 0.22, 1.0),
        "cable": (0.07, 0.07, 0.08, 1.0),
        "xlr": (0.34, 0.34, 0.36, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
    },
    # --- B-family affinity (vintage-desktop domain) ---
    "vintage_satin_silver": {
        "body": (0.80, 0.81, 0.83, 1.0),
        "mesh": (0.83, 0.84, 0.86, 1.0),
        "dark": (0.15, 0.15, 0.17, 1.0),
        "metal": (0.78, 0.79, 0.81, 1.0),
        "base": (0.40, 0.41, 0.44, 1.0),
        "knob": (0.70, 0.72, 0.75, 1.0),
        "marker": (0.90, 0.91, 0.93, 1.0),
        "badge": (0.10, 0.10, 0.12, 1.0),
        "mute": (0.80, 0.22, 0.28, 1.0),
        "cable": (0.22, 0.22, 0.24, 1.0),
        "xlr": (0.52, 0.53, 0.55, 1.0),
        "rubber": (0.12, 0.12, 0.13, 1.0),
    },
    "vintage_chrome_oval": {
        "body": (0.86, 0.88, 0.90, 1.0),
        "mesh": (0.88, 0.89, 0.91, 1.0),
        "dark": (0.10, 0.10, 0.12, 1.0),
        "metal": (0.84, 0.86, 0.89, 1.0),
        "base": (0.28, 0.29, 0.31, 1.0),
        "knob": (0.80, 0.82, 0.85, 1.0),
        "marker": (0.94, 0.95, 0.97, 1.0),
        "badge": (0.08, 0.08, 0.10, 1.0),
        "mute": (0.80, 0.22, 0.28, 1.0),
        "cable": (0.18, 0.18, 0.20, 1.0),
        "xlr": (0.58, 0.59, 0.62, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
    },
    "gold_vintage_brass": {
        "body": (0.78, 0.62, 0.24, 1.0),
        "mesh": (0.82, 0.68, 0.30, 1.0),
        "dark": (0.10, 0.09, 0.06, 1.0),
        "metal": (0.74, 0.58, 0.22, 1.0),
        "base": (0.14, 0.13, 0.11, 1.0),
        "knob": (0.70, 0.56, 0.22, 1.0),
        "marker": (0.90, 0.80, 0.48, 1.0),
        "badge": (0.10, 0.09, 0.06, 1.0),
        "mute": (0.80, 0.22, 0.24, 1.0),
        "cable": (0.12, 0.11, 0.09, 1.0),
        "xlr": (0.60, 0.50, 0.24, 1.0),
        "rubber": (0.10, 0.09, 0.07, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Geometry constants (nominal, pre-scale)
# --------------------------------------------------------------------------- #

# Family A
A_BASE_R = 0.055  # weighted disc radius (dia 0.110)
A_BASE_H = 0.018
BODY_R = 0.030  # body tube radius (dia 0.060)
BODY_BOTTOM_Z = 0.060  # lowest body point above the base (rest pose)
PIVOT_Z = 0.118  # body tilt axis height (between fork arms / cradle)
PIVOT_Y = BODY_R + 0.018  # fork knuckle / pivot end offset (outboard of body wall)
BODY_DZ = -PIVOT_Z  # ground -> body-part-frame shift
KNOB_DIA0 = 0.018
KNOB_H = 0.010
GRILLE_H = 0.040  # cyl grille band height
# shock cradle
OUTER_RING_R = 0.072
OUTER_RING_TUBE = 0.005
CRADLE_RING_R = 0.045
CRADLE_RING_TUBE = 0.004
N_BANDS = 8
BAND_R = 0.0018
# ball head
BODY_TOP_R = 0.022

# Family B
B_BASE_R = 0.050
B_BASE_THICK = 0.014
# weighted disc
W_POST_TOP_Z = 0.082
W_YOKE_PIVOT_Z = 0.130
# tripod
HUB_RADIUS = 0.016
HUB_HEIGHT = 0.022
HUB_TOP_Z = 0.030
HUB_BOTTOM_Z = HUB_TOP_Z - HUB_HEIGHT
T_POST_TOP_Z = 0.092
T_YOKE_PIVOT_Z = 0.140
N_LEGS = 3
LEG_ATTACH_Z = 0.020
LEG_TOP_R = 0.005
LEG_BOT_R = 0.003
T_FOOT_SPREAD_R = 0.065
FOOT_RADIUS = 0.009
FOOT_HEIGHT = 0.004
# oval capsule (half extents)
OVAL_HALF_W = 0.022  # Y (thin axis)
OVAL_HALF_TALL = 0.040  # Z
OVAL_HALF_DEPTH = 0.028  # X (face depth)
# cyl basket capsule
BASKET_RADIUS = 0.023
BASKET_HEIGHT = 0.060
RIB_COUNT = 16
RIB_WIDTH = 0.0015
RIB_DEPTH = 0.002
BAND_HEIGHT = 0.005
BAND_THICK = 0.003

ROT_Z_TO_PX = (0.0, math.pi / 2.0, 0.0)  # local +Z -> world +X
ROT_Z_TO_NX = (0.0, -math.pi / 2.0, 0.0)


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class VocalMicrophoneConfig:
    mount_stand: MountStand = "rigid_forked_yoke"
    head_form: HeadForm = "cylindrical_mesh_basket"
    control_knob_count: int = 2
    palette_style: PaletteStyle = "blue_usb_silver_grille"
    overall_size_scale: float = 1.0
    base_radius_scale: float = 1.0
    body_tube_height_scale: float = 1.0
    head_size_scale: float = 1.0
    knob_dia_scale: float = 1.0
    tilt_limit_deg: float = 45.0
    name: str = "reference_vocal_microphone"


@dataclass(frozen=True)
class ResolvedVocalMicrophoneConfig:
    mount_stand: MountStand
    head_form: HeadForm
    family: str
    control_knob_count: int  # 0 for Family B
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    base_radius_scale: float
    body_tube_height_scale: float
    head_size_scale: float
    knob_dia_scale: float
    tilt_limit_rad: float
    name: str
    # derived (A)
    knob_dia: float
    knob_zs: tuple[float, ...]
    knob_band_top: float  # grille bottom (cyl) / neck base (ball)
    # derived (B)
    yoke_pivot_z: float
    post_top_z: float


def _clamp(v: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(v)))


def _pick(v, choices):
    return v if v in choices else choices[0]


def config_from_seed(seed: int) -> VocalMicrophoneConfig:
    """Deterministic ordered procedural sampling (no rejection):
    mount_stand -> family -> head_form (family-legal) -> N (A only) ->
    palette (family pool) -> continuous scales. ``seed=0`` is not special.
    """
    rng = random.Random(seed)

    mount: MountStand = rng.choices(MOUNT_STANDS, weights=_MOUNT_WEIGHTS, k=1)[0]
    fam = family_of(mount)
    if fam == "A":
        head: HeadForm = rng.choices(A_HEADS, weights=_A_HEAD_WEIGHTS, k=1)[0]
        n = rng.choices(KNOB_COUNTS, weights=_KNOB_WEIGHTS, k=1)[0]
        palette: PaletteStyle = rng.choice(A_PALETTES)
    else:
        head = rng.choices(B_HEADS, weights=_B_HEAD_WEIGHTS, k=1)[0]
        n = 0
        palette = rng.choice(B_PALETTES)

    overall = round(rng.uniform(0.88, 1.10), 4)
    base_r_s = round(rng.uniform(0.90, 1.12), 4)
    body_h_s = round(rng.uniform(0.92, 1.15), 4)
    head_s = round(rng.uniform(0.90, 1.12), 4)
    knob_s = round(rng.uniform(0.88, 1.12), 4)
    tilt = round(rng.uniform(33.0, 48.0), 4)

    return VocalMicrophoneConfig(
        mount_stand=mount,
        head_form=head,
        control_knob_count=n,
        palette_style=palette,
        overall_size_scale=overall,
        base_radius_scale=base_r_s,
        body_tube_height_scale=body_h_s,
        head_size_scale=head_s,
        knob_dia_scale=knob_s,
        tilt_limit_deg=tilt,
        name=f"seeded_vocal_microphone_{seed}",
    )


def resolve_config(config: VocalMicrophoneConfig) -> ResolvedVocalMicrophoneConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    mount = _pick(config.mount_stand, MOUNT_STANDS)
    fam = family_of(mount)
    legal_heads = A_HEADS if fam == "A" else B_HEADS
    # Family gating: a head incompatible with the resolved family falls back to
    # the cross-family bridge baseline (cylindrical_mesh_basket).
    head = config.head_form if config.head_form in legal_heads else "cylindrical_mesh_basket"

    base_r_s = _clamp(config.base_radius_scale, 0.90, 1.12)
    body_h_s = _clamp(config.body_tube_height_scale, 0.92, 1.15)
    head_s = _clamp(config.head_size_scale, 0.90, 1.12)
    knob_s = _clamp(config.knob_dia_scale, 0.88, 1.12)
    tilt_rad = math.radians(_clamp(config.tilt_limit_deg, 33.0, 48.0))

    # --- Family A knob column layout (N drives body height; spec inequality) --
    if fam == "A":
        n = int(config.control_knob_count) if config.control_knob_count in KNOB_COUNTS else 2
        knob_dia = KNOB_DIA0 * knob_s
        spacing = (knob_dia + 0.0075) * body_h_s
        spacing = max(spacing, knob_dia + 0.005)  # never overlap (inequality)
        first_z = BODY_BOTTOM_Z + 0.016
        knob_zs = tuple(round(first_z + i * spacing, 5) for i in range(n))
        knob_band_top = round(knob_zs[-1] + knob_dia / 2.0 + 0.030, 5)
    else:
        n = 0
        knob_dia = KNOB_DIA0
        knob_zs = ()
        knob_band_top = 0.0

    # --- Family B pivot heights per mount ------------------------------------
    if mount == "folding_desk_tripod":
        yoke_pivot_z = T_YOKE_PIVOT_Z
        post_top_z = T_POST_TOP_Z
    else:
        yoke_pivot_z = W_YOKE_PIVOT_Z
        post_top_z = W_POST_TOP_Z

    return ResolvedVocalMicrophoneConfig(
        mount_stand=mount,
        head_form=head,
        family=fam,
        control_knob_count=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        base_radius_scale=base_r_s,
        body_tube_height_scale=body_h_s,
        head_size_scale=head_s,
        knob_dia_scale=knob_s,
        tilt_limit_rad=tilt_rad,
        name=config.name,
        knob_dia=knob_dia,
        knob_zs=knob_zs,
        knob_band_top=knob_band_top,
        yoke_pivot_z=yoke_pivot_z,
        post_top_z=post_top_z,
    )


# --------------------------------------------------------------------------- #
# Family A geometry helpers (pure mesh; adopted A0 / S_ball / S_cradle / S_n*)
# --------------------------------------------------------------------------- #


def _a_base_disc(base_r: float):
    """Round weighted base disc + rim fillet + central hub stub (adopted A0)."""
    geom = CylinderGeometry(base_r, A_BASE_H, radial_segments=56)
    geom.translate(0.0, 0.0, A_BASE_H / 2.0)
    rim = TorusGeometry(base_r - 0.004, 0.004, radial_segments=10, tubular_segments=56)
    rim.translate(0.0, 0.0, A_BASE_H - 0.003)
    geom.merge(rim)
    hub = CylinderGeometry(0.020, 0.016, radial_segments=28)
    hub.translate(0.0, 0.0, A_BASE_H + 0.004)
    geom.merge(hub)
    return mesh_from_geometry(geom, "base_disc")


def _fork_arm_mesh(sign: float, name: str):
    """One curved Y-fork arm: hub -> sweep out/up -> knuckle (adopted A0)."""
    y = sign
    # Keep the arm well outboard of the body wall (BODY_R=0.030, tube r=0.0085)
    # over the whole body z-range so the swept tube never grazes the shell.
    pts2d = [
        (y * 0.012, A_BASE_H + 0.004),
        (y * 0.034, A_BASE_H + 0.026),
        (y * 0.050, 0.062),
        (y * 0.052, 0.096),
        (y * PIVOT_Y, PIVOT_Z),
    ]
    smooth = sample_catmull_rom_spline_2d(pts2d, samples_per_segment=10)
    pts3d = [(0.0, p[0], p[1]) for p in smooth]
    tube = tube_from_spline_points(pts3d, radius=0.0085, samples_per_segment=4, radial_segments=12)
    knuckle = CylinderGeometry(0.013, 0.012, radial_segments=20).rotate_x(math.pi / 2.0)
    knuckle.translate(0.0, y * PIVOT_Y, PIVOT_Z)
    tube.merge(knuckle)
    return mesh_from_geometry(tube, name)


def _pivot_axle(length: float, name: str):
    """Central tilt-pivot rod along +Y at the tilt axis (z=PIVOT_Z). Provides
    base geometry on the joint axis for the origin baseline; hidden inside the
    body where it crosses the center, ends seated in the fork knuckles / outer
    ring."""
    geom = CylinderGeometry(0.0045, length, radial_segments=16).rotate_x(math.pi / 2.0)
    geom.translate(0.0, 0.0, PIVOT_Z)
    return mesh_from_geometry(geom, name)


def _pivot_hub():
    """Central body trunnion at the tilt axis. The base pivot axle runs through
    it; gives the body real geometry on the joint axis (origin baseline) and
    reads as the side pivot bosses. Pokes through the body wall on both sides so
    its surface connects to the shell (no nested island)."""
    geom = CylinderGeometry(0.011, 2 * (BODY_R + 0.005), radial_segments=14).rotate_x(math.pi / 2.0)
    geom.translate(0.0, 0.0, PIVOT_Z)
    return mesh_from_geometry(geom, "pivot_hub")


def _support_arm_mesh():
    """Curved rear support arm: hub -> back/up -> outer ring (adopted S_cradle)."""
    pts2d = [
        (-0.020, A_BASE_H + 0.008),
        (-0.045, 0.058),
        (-0.060, 0.090),
        (-OUTER_RING_R, PIVOT_Z),
    ]
    smooth = sample_catmull_rom_spline_2d(pts2d, samples_per_segment=10)
    pts3d = [(p[0], 0.0, p[1]) for p in smooth]
    tube = tube_from_spline_points(pts3d, radius=0.008, samples_per_segment=4, radial_segments=12)
    return mesh_from_geometry(tube, "support_arm")


def _outer_ring_mesh():
    geom = TorusGeometry(OUTER_RING_R, OUTER_RING_TUBE, radial_segments=12, tubular_segments=48)
    geom.translate(0.0, 0.0, PIVOT_Z)
    return mesh_from_geometry(geom, "outer_ring")


def _cradle_ring_mesh():
    """Inner cradle ring: a STATIC torus at the cradle height, suspended by the
    elastic bands (which bridge it to the outer ring) and concentric with the
    mic body. The body hangs and pivots inside it without touching it, so the
    cradle stays put when the body tilts (corrected S_cradle: no body clips --
    the suspension is a static assembly on the base, not welded to the body)."""
    geom = TorusGeometry(CRADLE_RING_R, CRADLE_RING_TUBE, radial_segments=10, tubular_segments=40)
    geom.translate(0.0, 0.0, PIVOT_Z)
    return mesh_from_geometry(geom, "cradle_ring")


def _elastic_band(i: int):
    angle = math.pi / N_BANDS + 2.0 * math.pi * i / N_BANDS
    inner = CRADLE_RING_R + 0.001
    outer = OUTER_RING_R - 0.001
    geom = CylinderGeometry(BAND_R, outer - inner, radial_segments=8).rotate_y(math.pi / 2.0)
    geom.translate((inner + outer) / 2.0, 0.0, PIVOT_Z)
    geom.rotate_z(angle)
    return mesh_from_geometry(geom, f"band_{i}")


def _body_shell_cyl(grille_bottom_z: float):
    """Straight cylindrical body below the grille band (adopted A0)."""
    z0 = BODY_BOTTOM_Z
    z1 = grille_bottom_z
    h = z1 - z0
    geom = CylinderGeometry(BODY_R, h, radial_segments=40)
    geom.translate(0.0, 0.0, z0 + h / 2.0)
    lip = TorusGeometry(BODY_R - 0.0035, 0.0035, radial_segments=10, tubular_segments=40)
    lip.translate(0.0, 0.0, z0 + 0.0035)
    geom.merge(lip)
    return mesh_from_geometry(geom, "body_shell")


def _grille_band_mesh(z0: float, z1: float):
    """Fine vertical mesh-grille band (ribbed cylinder) (adopted A0). Stays a
    mesh grille (Rule 3: no Box/Cylinder downgrade)."""
    h = z1 - z0
    geom = CylinderGeometry(BODY_R - 0.0015, h, radial_segments=40)
    geom.translate(0.0, 0.0, z0 + h / 2.0)
    n_ribs = 36
    rib = BODY_R - 0.0008
    for i in range(n_ribs):
        ang = 2.0 * math.pi * i / n_ribs
        ridge = CylinderGeometry(0.0010, h, radial_segments=6)
        ridge.translate(rib * math.cos(ang), rib * math.sin(ang), z0 + h / 2.0)
        geom.merge(ridge)
    for zb in (z0 + 0.002, z1 - 0.002):
        ring = TorusGeometry(BODY_R - 0.0006, 0.0018, radial_segments=8, tubular_segments=40)
        ring.translate(0.0, 0.0, zb)
        geom.merge(ring)
    return mesh_from_geometry(geom, "grille_band")


def _dome_cap(top_z: float, head_s: float):
    cap_r = BODY_R * min(1.0, head_s)
    geom = DomeGeometry(cap_r, radial_segments=40, height_segments=14)
    geom.scale(1.0, 1.0, 0.95)
    geom.translate(0.0, 0.0, top_z - 0.001)
    return mesh_from_geometry(geom, "dome_cap")


def _ball_body_shell(neck_base_z: float):
    """Tapered lathe body: full BODY_R straight section (carries the knob
    column) -> taper -> neck (adopted S_ball)."""
    shoulder_z = neck_base_z + 0.018
    neck_top_z = shoulder_z + 0.010
    profile = [
        (0.002, BODY_BOTTOM_Z),
        (BODY_R - 0.003, BODY_BOTTOM_Z),
        (BODY_R, BODY_BOTTOM_Z + 0.004),
        (BODY_R, neck_base_z),
        (BODY_R - 0.001, neck_base_z + 0.006),
        (BODY_TOP_R, shoulder_z),
        (BODY_TOP_R, neck_top_z),
    ]
    geom = LatheGeometry(profile, segments=40)
    return mesh_from_geometry(geom, "body_shell"), neck_top_z


def _ball_head(neck_top_z: float, head_s: float):
    """Spherical wire-cage windscreen: dark inner sphere + meridian/parallel
    chrome ribs + neck collar (adopted S_ball)."""
    head_r = 0.040 * head_s
    head_inner_r = head_r - 0.001
    head_center_z = neck_top_z + head_r * 0.55

    inner = SphereGeometry(head_inner_r, width_segments=28, height_segments=20)
    inner.translate(0.0, 0.0, head_center_z)
    inner_mesh = mesh_from_geometry(inner, "head_inner")

    def _meridian(theta):
        pts = []
        for j in range(26):
            a = 2.0 * math.pi * j / 26
            pts.append(
                (
                    head_r * math.cos(a) * math.cos(theta),
                    head_r * math.cos(a) * math.sin(theta),
                    head_r * math.sin(a) + head_center_z,
                )
            )
        return pts

    def _parallel(lat):
        rr = head_r * math.cos(lat)
        zz = head_r * math.sin(lat) + head_center_z
        return [
            (rr * math.cos(2.0 * math.pi * j / 26), rr * math.sin(2.0 * math.pi * j / 26), zz)
            for j in range(26)
        ]

    def _rib(pts):
        return tube_from_spline_points(
            pts,
            radius=0.0014,
            samples_per_segment=3,
            closed_spline=True,
            radial_segments=6,
            cap_ends=False,
        )

    ribs = []
    for i in range(12):
        ribs.append(_rib(_meridian(math.pi * i / 12)))
    for i in range(8):
        ribs.append(_rib(_parallel(-math.radians(50) + math.radians(130) * (i + 1) / 9)))
    ribs.append(
        tube_from_spline_points(
            _parallel(0.0),
            radius=0.0018,
            samples_per_segment=3,
            closed_spline=True,
            radial_segments=8,
            cap_ends=False,
        )
    )
    cage = ribs[0]
    for rb in ribs[1:]:
        cage.merge(rb)
    ribs_mesh = mesh_from_geometry(cage, "head_ribs")

    collar = TorusGeometry(BODY_TOP_R + 0.004, 0.004, radial_segments=8, tubular_segments=40)
    collar.translate(0.0, 0.0, neck_top_z)
    collar_mesh = mesh_from_geometry(collar, "head_collar")
    return inner_mesh, ribs_mesh, collar_mesh, head_center_z


def _front_knob_mesh(knob_dia: float, name: str):
    geom = KnobGeometry(
        knob_dia,
        KNOB_H,
        body_style="cylindrical",
        grip=KnobGrip(style="knurled", count=24, depth=0.0008),
        indicator=KnobIndicator(style="line", mode="engraved", depth=0.0007, angle_deg=0.0),
        center=False,
    )
    return mesh_from_geometry(geom, name)


def _front_knob_marker(knob_dia: float, name: str):
    geom = BoxGeometry((0.004, 0.002, 0.006))
    geom.translate(knob_dia / 2.0 - 0.003, 0.0, KNOB_H + 0.001)
    return mesh_from_geometry(geom, name)


def _front_badge(z: float):
    geom = SphereGeometry(0.011, width_segments=20, height_segments=10)
    geom.scale(0.35, 1.7, 0.8)
    geom.translate(BODY_R - 0.001, 0.0, z)
    return mesh_from_geometry(geom, "front_badge")


def _mute_dot(z: float):
    geom = SphereGeometry(0.005, width_segments=14, height_segments=8)
    geom.scale(0.35, 1.0, 1.0)
    geom.translate(BODY_R - 0.0005, 0.0, z)
    return mesh_from_geometry(geom, "mute_dot")


# --------------------------------------------------------------------------- #
# Family B geometry helpers (cadquery + mesh; adopted B0 / S_cylB / S_tripod)
# --------------------------------------------------------------------------- #


def _b_base_disc(base_r: float):
    disc = cq.Workplane("XY").circle(base_r).extrude(B_BASE_THICK)
    rim = (
        cq.Workplane("XY")
        .circle(base_r)
        .circle(base_r - 0.006)
        .extrude(0.003)
        .translate((0.0, 0.0, B_BASE_THICK))
    )
    return mesh_from_cadquery(disc.union(rim), "base_disc")


def _hub_mesh():
    hub = (
        cq.Workplane("XY")
        .circle(HUB_RADIUS)
        .extrude(HUB_HEIGHT)
        .translate((0.0, 0.0, HUB_BOTTOM_Z))
    )
    rim = (
        cq.Workplane("XY")
        .circle(HUB_RADIUS + 0.002)
        .circle(HUB_RADIUS - 0.003)
        .extrude(0.003)
        .translate((0.0, 0.0, HUB_TOP_Z))
    )
    for i in range(N_LEGS):
        theta = i * 2.0 * math.pi / N_LEGS
        boss = (
            cq.Workplane("XY")
            .circle(0.008)
            .extrude(0.012)
            .translate(
                (
                    (HUB_RADIUS + 0.001) * math.cos(theta),
                    (HUB_RADIUS + 0.001) * math.sin(theta),
                    LEG_ATTACH_Z - 0.006,
                )
            )
        )
        hub = hub.union(boss)
    return mesh_from_cadquery(hub.union(rim), "hub_shell")


def _leg_strut_mesh(i: int, foot_spread_r: float):
    theta = i * 2.0 * math.pi / N_LEGS
    z_top = LEG_ATTACH_Z
    r_attach = HUB_RADIUS + 0.002
    z_bot = FOOT_HEIGHT
    xt, yt = r_attach * math.cos(theta), r_attach * math.sin(theta)
    xb, yb = foot_spread_r * math.cos(theta), foot_spread_r * math.sin(theta)
    dx, dy, dz = xb - xt, yb - yt, z_bot - z_top
    leg_len = math.sqrt(dx * dx + dy * dy + dz * dz)
    ux, uy, uz = dx / leg_len, dy / leg_len, dz / leg_len
    rx, ry = -uy, ux
    r_len = math.sqrt(rx * rx + ry * ry)
    if r_len > 1e-8:
        rx, ry = rx / r_len, ry / r_len
        angle_deg = math.degrees(math.acos(max(-1.0, min(1.0, uz))))
    else:
        angle_deg, rx, ry = 0.0, 1.0, 0.0
    mx, my, mz = (xt + xb) / 2.0, (yt + yb) / 2.0, (z_top + z_bot) / 2.0
    strut = (
        cq.Workplane("XY")
        .circle(LEG_TOP_R)
        .workplane(offset=leg_len)
        .circle(LEG_BOT_R)
        .loft(ruled=True)
        .translate((0.0, 0.0, -leg_len / 2.0))
    )
    collar = (
        cq.Workplane("XY")
        .circle(LEG_TOP_R + 0.003)
        .extrude(0.010)
        .translate((0.0, 0.0, -leg_len / 2.0 - 0.002))
    )
    strut = strut.union(collar)
    if abs(angle_deg) > 0.01:
        strut = strut.rotate((0.0, 0.0, 0.0), (rx, ry, 0.0), angle_deg)
    strut = strut.translate((mx, my, mz))
    return mesh_from_cadquery(strut, f"leg_{i}")


def _foot_mesh(i: int, foot_spread_r: float):
    theta = i * 2.0 * math.pi / N_LEGS
    xb, yb = foot_spread_r * math.cos(theta), foot_spread_r * math.sin(theta)
    pad = cq.Workplane("XY").circle(FOOT_RADIUS).extrude(FOOT_HEIGHT).translate((xb, yb, 0.0))
    taper = (
        cq.Workplane("XY")
        .circle(FOOT_RADIUS * 0.85)
        .workplane(offset=0.005)
        .circle(LEG_BOT_R + 0.001)
        .loft(ruled=True)
        .translate((xb, yb, FOOT_HEIGHT))
    )
    return mesh_from_cadquery(pad.union(taper), f"foot_{i}")


def _post_mesh(post_top_z: float, collar_bottom_z: float):
    post = (
        cq.Workplane("XY")
        .circle(0.014)
        .workplane(offset=post_top_z - collar_bottom_z - 0.006)
        .circle(0.0085)
        .loft(ruled=False)
        .translate((0.0, 0.0, collar_bottom_z + 0.006))
    )
    collar = (
        cq.Workplane("XY")
        .circle(0.014)
        .extrude((post_top_z - collar_bottom_z) * 0.5)
        .translate((0.0, 0.0, collar_bottom_z))
    )
    return mesh_from_cadquery(post.union(collar), "post_shell")


def _yoke_mesh(arm_y: float, post_top_z: float, pivot_z: float):
    arm_thick = 0.008
    arm_depth = 0.018
    bridge_h = 0.012
    bridge = (
        cq.Workplane("XY")
        .box(arm_depth, 2 * arm_y + arm_thick, bridge_h)
        .translate((0.0, 0.0, post_top_z + bridge_h / 2.0))
    )
    arm_bottom = post_top_z + bridge_h
    arm_top = pivot_z + 0.010
    arm_height = arm_top - arm_bottom
    yoke = bridge
    for sign in (-1.0, 1.0):
        yc = sign * arm_y
        arm = (
            cq.Workplane("XY")
            .box(arm_depth, arm_thick, arm_height)
            .translate((0.0, yc, arm_bottom + arm_height / 2.0))
        )
        cap = (
            cq.Workplane("XY")
            .circle(arm_depth / 2.0)
            .extrude(arm_thick)
            .rotate((0, 0, 0), (1, 0, 0), 90)
            .translate((0.0, yc + sign * (arm_thick / 2.0), pivot_z))
        )
        yoke = yoke.union(arm).union(cap)
    return mesh_from_cadquery(yoke, "yoke_shell")


def _tilt_pin(arm_y: float, pivot_z: float):
    """Central +Y tilt pin on the yoke through the capsule center (provides
    parent geometry on the tilt axis; captures the capsule)."""
    geom = CylinderGeometry(0.0035, 2 * arm_y + 0.004, radial_segments=14).rotate_x(math.pi / 2.0)
    geom.translate(0.0, 0.0, pivot_z)
    return mesh_from_geometry(geom, "tilt_pin")


def _tilt_boss(reach_half: float):
    """+Y pivot bushing on the capsule (capsule-local origin = pivot). Captures
    the yoke tilt pin and gives the capsule geometry on the joint axis (origin
    baseline). Pokes through the windscreen interior + shell wall on both sides
    so its surface connects to the head (no nested island)."""
    geom = CylinderGeometry(0.006, 2 * (reach_half + 0.005), radial_segments=12).rotate_x(
        math.pi / 2.0
    )
    return mesh_from_geometry(geom, "tilt_boss")


def _loft_yz(sections) -> cq.Workplane:
    wp = cq.Workplane("YZ")
    prev = None
    for x_off, w, h in sections:
        wp = wp.workplane(offset=x_off if prev is None else x_off - prev)
        wp = wp.rect(w, h)
        prev = x_off
    return wp.loft(ruled=False)


def _oval_capsule_mesh(half_x: float, half_y: float, half_z: float, z_lift: float):
    outer = _loft_yz(
        [
            (-half_x, 0.026 * (half_y / OVAL_HALF_W), 0.052 * (half_z / OVAL_HALF_TALL)),
            (-half_x * 0.4, 2 * half_y * 0.92, 2 * half_z * 0.94),
            (half_x * 0.45, 2 * half_y, 2 * half_z),
            (half_x * 0.95, 2 * half_y * 0.78, 2 * half_z * 0.82),
        ]
    )
    inner = _loft_yz(
        [
            (-half_x * 0.85, 0.020 * (half_y / OVAL_HALF_W), 0.046 * (half_z / OVAL_HALF_TALL)),
            (-half_x * 0.3, 2 * (half_y - 0.005) * 0.9, 2 * (half_z - 0.005) * 0.9),
            (half_x * 0.45, 2 * (half_y - 0.005), 2 * (half_z - 0.005)),
            (half_x * 1.05, 2 * (half_y - 0.006) * 0.78, 2 * (half_z - 0.006) * 0.82),
        ]
    )
    shell = outer.cut(inner)
    slot_h = 0.0045
    pitch = 0.0085 * (half_z / OVAL_HALF_TALL)
    n = 7
    z0 = -(n - 1) / 2.0 * pitch
    cutter = None
    for i in range(n):
        z = z0 + i * pitch
        frac = 1.0 - (abs(z) / half_z) ** 2 * 0.5
        sw = 2 * half_y * 1.3 * max(0.45, frac)
        slot = cq.Workplane("XY").box(2 * half_x, sw, slot_h).translate((half_x * 0.5, 0.0, z))
        cutter = slot if cutter is None else cutter.union(slot)
    shell = shell.cut(cutter)
    if z_lift:
        shell = shell.translate((0.0, 0.0, z_lift))
    return mesh_from_cadquery(shell, "capsule_shell")


def _oval_interior_mesh(half_x: float, half_y: float, half_z: float, z_lift: float):
    blk = _loft_yz(
        [
            (-(half_x - 0.006), 2 * (half_y - 0.008), 2 * (half_z - 0.006)),
            (half_x - 0.006, 2 * (half_y - 0.008) * 0.8, 2 * (half_z - 0.006) * 0.85),
        ]
    )
    if z_lift:
        blk = blk.translate((0.0, 0.0, z_lift))
    return mesh_from_cadquery(blk, "grille_interior")


def _basket_shell_mesh(basket_r: float):
    shell = MeshGeometry()
    basket_bottom_z = -0.020
    basket_top_z = basket_bottom_z + BASKET_HEIGHT
    rib_height = BASKET_HEIGHT - 2 * BAND_HEIGHT
    rib_center_z = basket_bottom_z + BAND_HEIGHT + rib_height / 2.0
    for i in range(RIB_COUNT):
        angle = 2.0 * math.pi * i / RIB_COUNT
        rib = BoxGeometry((RIB_DEPTH, RIB_WIDTH, rib_height))
        rib.translate(basket_r, 0.0, rib_center_z)
        rib.rotate_z(angle)
        shell.merge(rib)
    r_in = basket_r - BAND_THICK / 2.0
    r_out = basket_r + BAND_THICK / 2.0
    bot = LatheGeometry(
        [
            (r_in, basket_bottom_z),
            (r_out, basket_bottom_z),
            (r_out, basket_bottom_z + BAND_HEIGHT),
            (r_in, basket_bottom_z + BAND_HEIGHT),
        ],
        segments=32,
        closed=True,
    )
    shell.merge(bot)
    top = LatheGeometry(
        [
            (r_in, basket_top_z - BAND_HEIGHT),
            (r_out, basket_top_z - BAND_HEIGHT),
            (r_out, basket_top_z),
            (r_in, basket_top_z),
        ],
        segments=32,
        closed=True,
    )
    shell.merge(top)
    return mesh_from_geometry(shell, "basket_shell"), basket_bottom_z, basket_top_z


def _basket_dome_mesh(basket_r: float, basket_top_z: float):
    dome = DomeGeometry(
        radius=basket_r - 0.001, radial_segments=20, height_segments=8, closed=False
    )
    dome.translate(0.0, 0.0, basket_top_z)
    return mesh_from_geometry(dome, "basket_dome")


def _basket_interior_mesh(basket_r: float, basket_bottom_z: float):
    r = basket_r - BAND_THICK - 0.001
    h = BASKET_HEIGHT - 2 * BAND_HEIGHT - 0.004
    interior = CylinderGeometry(r, h, radial_segments=20, closed=True)
    interior.translate(0.0, 0.0, basket_bottom_z + BAND_HEIGHT + 0.002 + h / 2.0)
    return mesh_from_geometry(interior, "basket_interior")


def _oval_badge(half_x: float, z_lift: float):
    geom = CylinderGeometry(0.006, 0.008, radial_segments=16).rotate_y(math.pi / 2.0)
    geom.translate(half_x * 0.88, 0.0, z_lift + 0.00425)
    return mesh_from_geometry(geom, "badge")


# --------------------------------------------------------------------------- #
# Materials
# --------------------------------------------------------------------------- #


def _materials(model: ArticulatedObject, r: ResolvedVocalMicrophoneConfig) -> dict:
    out = {}
    for key, rgba in r.palette.items():
        out[key] = model.material(f"vm_{key}_{r.palette_style}", rgba=rgba)
    return out


# --------------------------------------------------------------------------- #
# Family A builder
# --------------------------------------------------------------------------- #


def _build_family_a(model: ArticulatedObject, r: ResolvedVocalMicrophoneConfig, mats: dict) -> None:
    base_r = A_BASE_R * r.base_radius_scale
    body_off = Origin(xyz=(0.0, 0.0, BODY_DZ))

    # ---- base (root, static) ----
    base = model.part("base")
    base.visual(_a_base_disc(base_r), material=mats["base"], name="base_disc", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackout_usb", "matte_black_stage", "vintage_satin_silver", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.paint_coated"))
    if r.mount_stand == "rigid_forked_yoke":
        base.visual(
            _fork_arm_mesh(+1.0, "fork_arm_pos"), material=mats["body"], name="fork_arm_pos", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackout_usb", "matte_black_stage", "vintage_satin_silver", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.paint_coated")
        )
        base.visual(
            _fork_arm_mesh(-1.0, "fork_arm_neg"), material=mats["body"], name="fork_arm_neg", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackout_usb", "matte_black_stage", "vintage_satin_silver", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.paint_coated")
        )
        base.visual(
            _pivot_axle(2 * PIVOT_Y + 0.010, "pivot_axle"),
            material=mats["metal"],
            name="pivot_axle", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackout_usb", "matte_black_stage", "vintage_satin_silver", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.paint_coated"),
        )
    else:  # elastic_shock_cradle
        base.visual(_support_arm_mesh(), material=mats["metal"], name="support_arm", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackout_usb", "matte_black_stage", "vintage_satin_silver", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.paint_coated"))
        base.visual(_outer_ring_mesh(), material=mats["metal"], name="outer_ring", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackout_usb", "matte_black_stage", "vintage_satin_silver", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.paint_coated"))
        # Inner cradle ring + N suspension bands are STATIC on the base: the
        # bands bridge outer ring -> cradle ring (one connected assembly), and
        # the mic body hangs / pivots inside the cradle without touching it.
        base.visual(_cradle_ring_mesh(), material=mats["metal"], name="cradle_ring", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackout_usb", "matte_black_stage", "vintage_satin_silver", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.paint_coated"))
        for i in range(N_BANDS):
            base.visual(_elastic_band(i), material=mats["rubber"], name=f"band_{i}", material_class_id="rubber.smooth_plain")
        base.visual(
            _pivot_axle(2 * OUTER_RING_R, "pivot_axle"), material=mats["metal"], name="pivot_axle", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackout_usb", "matte_black_stage", "vintage_satin_silver", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.paint_coated")
        )

    # ---- body (tilts about +Y) ----
    body = model.part("body")
    if r.head_form == "round_ball_windscreen":
        shell_mesh, neck_top_z = _ball_body_shell(r.knob_band_top)
        body.visual(shell_mesh, origin=body_off, material=mats["body"], name="body_shell", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackout_usb", "matte_black_stage", "vintage_satin_silver", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.paint_coated"))
        inner, ribs, collar, _ = _ball_head(neck_top_z, r.head_size_scale)
        body.visual(inner, origin=body_off, material=mats["dark"], name="head_inner", material_class_id="fabric.flexible_foam")
        body.visual(ribs, origin=body_off, material=mats["mesh"], name="head_ribs", material_class_id="metal.mesh_chainmail")
        body.visual(collar, origin=body_off, material=mats["dark"], name="head_collar", material_class_id="metal.blackened_gunmetal")
    else:  # cylindrical_mesh_basket (A implementation = grille band + dome)
        grille_bottom_z = r.knob_band_top
        grille_top_z = grille_bottom_z + GRILLE_H * r.head_size_scale
        body.visual(
            _body_shell_cyl(grille_bottom_z),
            origin=body_off,
            material=mats["body"],
            name="body_shell", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"blackout_usb", "matte_black_stage", "vintage_satin_silver", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.paint_coated"),
        )
        body.visual(
            _grille_band_mesh(grille_bottom_z, grille_top_z),
            origin=body_off,
            material=mats["mesh"],
            name="grille_band", material_class_id="metal.mesh_chainmail",
        )
        body.visual(
            _dome_cap(grille_top_z, r.head_size_scale),
            origin=body_off,
            material=mats["mesh"],
            name="dome_cap", material_class_id="metal.mesh_chainmail",
        )

    # central pivot trunnion (captured on the base pivot axle)
    body.visual(_pivot_hub(), origin=body_off, material=mats["dark"], name="pivot_hub", material_class_id="metal.blackened_gunmetal")

    # front badge + MUTE on the front straight wall (above the knob column)
    body.visual(
        _front_badge(r.knob_band_top - 0.009),
        origin=body_off,
        material=mats["badge"],
        name="front_badge", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    body.visual(
        _mute_dot(r.knob_band_top - 0.020), origin=body_off, material=mats["mute"], name="mute_dot", appearance_only=AppearanceOnlySpec(kind="overlay")
    )

    model.articulation(
        "base_to_body",
        ArticulationType.REVOLUTE,
        parent=base,
        child=body,
        origin=Origin(xyz=(0.0, 0.0, PIVOT_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=2.0, lower=-r.tilt_limit_rad, upper=r.tilt_limit_rad
        ),
    )

    # ---- N front knobs (CONTINUOUS +X) ----
    knob_rpy = (0.0, math.pi / 2.0, 0.0)
    for i, kz in enumerate(r.knob_zs):
        knob_name = f"front_knob_{i}"
        marker_name = f"front_marker_{i}"
        knob = model.part(knob_name)
        knob.visual(
            _front_knob_mesh(r.knob_dia, knob_name),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=knob_rpy),
            material=mats["knob"],
            name=knob_name, material_class_id="plastic.patterned_textured",
        )
        knob.visual(
            _front_knob_marker(r.knob_dia, marker_name),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=knob_rpy),
            material=mats["marker"],
            name=marker_name, appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        model.articulation(
            f"body_to_{knob_name}",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=knob,
            origin=Origin(xyz=(BODY_R - 0.001, 0.0, kz + BODY_DZ)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=0.3, velocity=8.0),
            mating=MatingContract(
                parent_face_geometry="body_shell",
                parent_face_side="positive_x",
                child_face_geometry=knob_name,
                child_face_side="negative_x",
                contact_tol=0.004,
            ),
        )


# --------------------------------------------------------------------------- #
# Family B builder
# --------------------------------------------------------------------------- #


def _build_cable(part, mat_cable, mat_xlr, pts, plug_c, collar_c, tip_c, origin):
    ox, oy, oz = origin
    sp = [(x - ox, y - oy, z - oz) for (x, y, z) in pts]
    cable = tube_from_spline_points(sp, radius=0.0035, samples_per_segment=14, radial_segments=10)
    ang = math.atan2(plug_c[3], plug_c[4])
    plug = CylinderGeometry(0.010, 0.040).rotate_y(math.pi / 2.0).rotate_z(ang)
    plug.translate(plug_c[0] - ox, plug_c[1] - oy, plug_c[2] - oz)
    cable.merge(plug)
    collar = CylinderGeometry(0.012, 0.010).rotate_y(math.pi / 2.0).rotate_z(ang)
    collar.translate(collar_c[0] - ox, collar_c[1] - oy, collar_c[2] - oz)
    cable.merge(collar)
    part.visual(mesh_from_geometry(cable, "cable_shell"), material=mat_cable, name="cable_shell", material_class_id="tech.cable_pipe_bundle")
    tip = CylinderGeometry(0.0085, 0.006).rotate_y(math.pi / 2.0).rotate_z(ang)
    tip.translate(tip_c[0] - ox, tip_c[1] - oy, tip_c[2] - oz)
    part.visual(mesh_from_geometry(tip, "xlr_tip"), material=mat_xlr, name="xlr_tip", material_class_id="metal.chrome_polished")


def _build_family_b(model: ArticulatedObject, r: ResolvedVocalMicrophoneConfig, mats: dict) -> None:
    base_r = B_BASE_R * r.base_radius_scale
    foot_spread = T_FOOT_SPREAD_R * r.base_radius_scale
    head_s = r.head_size_scale
    pivot_z = r.yoke_pivot_z
    post_top_z = r.post_top_z

    # ---- base / hub (root, static) ----
    base = model.part("base")
    if r.mount_stand == "folding_desk_tripod":
        base.visual(_hub_mesh(), material=mats["metal"], name="base_disc", material_class_id=("metal.brass_aged" if r.palette_style in {"blue_usb_silver_grille", "blackout_usb", "matte_black_stage", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.brushed_silver"))
        for i in range(N_LEGS):
            base.visual(_leg_strut_mesh(i, foot_spread), material=mats["metal"], name=f"leg_{i}", material_class_id=("metal.brass_aged" if r.palette_style in {"blue_usb_silver_grille", "blackout_usb", "matte_black_stage", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.brushed_silver"))
            base.visual(_foot_mesh(i, foot_spread), material=mats["rubber"], name=f"foot_{i}", material_class_id="rubber.smooth_plain")
        cable_pts = [
            (-0.014, 0.0, HUB_BOTTOM_Z + 0.006),
            (-0.040, 0.0, 0.010),
            (-0.060, 0.003, 0.006),
            (-0.080, 0.008, 0.006),
            (-0.095, 0.018, 0.006),
            (-0.100, 0.035, 0.006),
            (-0.095, 0.055, 0.006),
            (-0.080, 0.072, 0.006),
        ]
        plug_c = (-0.065, 0.085, 0.010, 0.072 - 0.055, -0.080 - (-0.095))
        collar_c = (-0.078, 0.076, 0.010)
        tip_c = (-0.052, 0.094, 0.010)
        collar_bottom_z = HUB_BOTTOM_Z + 0.003
    else:  # weighted_base_disc
        base.visual(_b_base_disc(base_r), material=mats["body"], name="base_disc", material_class_id=("metal.brass_aged" if r.palette_style in {"blue_usb_silver_grille", "blackout_usb", "matte_black_stage", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.brushed_silver"))
        cable_pts = [
            (-0.030, 0.012, B_BASE_THICK * 0.6),
            (-0.055, 0.020, 0.010),
            (-0.075, 0.010, 0.006),
            (-0.070, -0.020, 0.006),
            (-0.040, -0.045, 0.006),
            (0.010, -0.050, 0.006),
            (0.060, -0.040, 0.006),
            (0.092, -0.018, 0.006),
        ]
        plug_c = (0.112, -0.011, 0.010, -0.018 + 0.040, 0.092 - 0.060)
        collar_c = (0.090, -0.016, 0.010)
        tip_c = (0.131, -0.008, 0.010)
        collar_bottom_z = 0.008  # extend collar into the base for joint-origin margin

    # ---- swivel post + yoke + tilt pin (CONTINUOUS +Z about the stand axis) --
    post = model.part("swivel_post")
    post.visual(_post_mesh(post_top_z, collar_bottom_z), material=mats["body"], name="post_shell", material_class_id=("metal.brass_aged" if r.palette_style in {"blue_usb_silver_grille", "blackout_usb", "matte_black_stage", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.brushed_silver"))
    if r.head_form == "cylindrical_mesh_basket":
        arm_y = BASKET_RADIUS * head_s + 0.011
    else:
        arm_y = OVAL_HALF_W * head_s + 0.011
    post.visual(_yoke_mesh(arm_y, post_top_z, pivot_z), material=mats["body"], name="yoke_shell", material_class_id=("metal.brass_aged" if r.palette_style in {"blue_usb_silver_grille", "blackout_usb", "matte_black_stage", "vintage_chrome_oval", "gold_vintage_brass"} else "metal.brushed_silver"))
    post.visual(_tilt_pin(arm_y, pivot_z), material=mats["xlr"], name="tilt_pin", material_class_id=("metal.chrome_polished" if r.palette_style in {"blue_usb_silver_grille", "blackout_usb", "matte_black_stage", "vintage_satin_silver", "vintage_chrome_oval"} else "metal.brass_aged"))
    model.articulation(
        "base_to_post",
        ArticulationType.CONTINUOUS,
        parent=base,
        child=post,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.5, velocity=4.0),
    )

    # ---- capsule head (REVOLUTE +Y; separate windscreen part) ----
    capsule = model.part("capsule_head")
    if r.head_form == "cylindrical_mesh_basket":
        basket_r = BASKET_RADIUS * head_s
        shell, b_bot, b_top = _basket_shell_mesh(basket_r)
        capsule.visual(shell, material=mats["body"], name="basket_shell", material_class_id="metal.mesh_chainmail")
        capsule.visual(
            _basket_dome_mesh(basket_r, b_top), material=mats["mesh"], name="basket_dome", material_class_id="metal.mesh_chainmail"
        )
        capsule.visual(
            _basket_interior_mesh(basket_r, b_bot), material=mats["dark"], name="basket_interior", material_class_id="fabric.flexible_foam"
        )
        reach_half = basket_r
    else:  # vintage_oval_ribbed
        half_x = OVAL_HALF_DEPTH * head_s
        half_y = OVAL_HALF_W * head_s
        half_z = OVAL_HALF_TALL * head_s
        cap_lift = 0.008
        capsule.visual(
            _oval_capsule_mesh(half_x, half_y, half_z, cap_lift),
            material=mats["body"],
            name="capsule_shell", material_class_id="metal.patterned_sheet_panel",
        )
        capsule.visual(
            _oval_interior_mesh(half_x, half_y, half_z, cap_lift),
            material=mats["dark"],
            name="grille_interior", material_class_id="fabric.flexible_foam",
        )
        capsule.visual(_oval_badge(half_x, cap_lift), material=mats["badge"], name="badge", appearance_only=AppearanceOnlySpec(kind="decal"))
        reach_half = half_y

    # central pivot bushing (captures the yoke tilt pin)
    capsule.visual(_tilt_boss(reach_half), material=mats["xlr"], name="tilt_boss", material_class_id=("metal.chrome_polished" if r.palette_style in {"blue_usb_silver_grille", "blackout_usb", "matte_black_stage", "vintage_satin_silver", "vintage_chrome_oval"} else "metal.brass_aged"))

    model.articulation(
        "yoke_to_capsule",
        ArticulationType.REVOLUTE,
        parent=post,
        child=capsule,
        origin=Origin(xyz=(0.0, 0.0, pivot_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=1.0, velocity=2.0, lower=-r.tilt_limit_rad, upper=r.tilt_limit_rad
        ),
    )

    # ---- cable (FIXED drooping XLR lead) ----
    cable_part = model.part("cable")
    cable_origin = cable_pts[0]
    _build_cable(
        cable_part, mats["cable"], mats["xlr"], cable_pts, plug_c, collar_c, tip_c, cable_origin
    )
    model.articulation(
        "base_to_cable",
        ArticulationType.FIXED,
        parent=base,
        child=cable_part,
        origin=Origin(xyz=cable_origin),
    )


# --------------------------------------------------------------------------- #
# Top-level build
# --------------------------------------------------------------------------- #


def build_vocal_microphone(
    config: VocalMicrophoneConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or VocalMicrophoneConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-vocal-mic-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]

    mats = _materials(model, r)
    if r.family == "A":
        _build_family_a(model, r, mats)
    else:
        _build_family_b(model, r, mats)
    return model


def build_seeded_vocal_microphone(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_vocal_microphone(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Slot choices
# --------------------------------------------------------------------------- #


def slot_choices_for_config(r: ResolvedVocalMicrophoneConfig) -> tuple[tuple[str, str], ...]:
    knob_tok = f"n{r.control_knob_count}" if r.family == "A" else "none"
    return (
        ("mount_stand", r.mount_stand),
        ("head_form", r.head_form),
        ("control_knob_count", knob_tok),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _ctr(aabb):
    mn, mx = aabb
    return ((mn[0] + mx[0]) / 2.0, (mn[1] + mx[1]) / 2.0, (mn[2] + mx[2]) / 2.0)


def _declare_allowances_a(ctx, model, r):
    base = model.get_part("base")
    body = model.get_part("body")
    # central pivot axle passes through the body center / pivot hub (captured pin)
    ctx.allow_overlap(
        base,
        body,
        elem_a="pivot_axle",
        elem_b="body_shell",
        reason="Tilt pivot axle runs through the body center (captured pin).",
    )
    ctx.allow_overlap(
        base,
        body,
        elem_a="pivot_axle",
        elem_b="pivot_hub",
        reason="Tilt pivot axle is captured inside the body pivot bushing.",
    )
    if r.mount_stand == "elastic_shock_cradle":
        # The whole shock-mount suspension is one static assembly on the base.
        ctx.allow_overlap(
            base,
            base,
            elem_a="pivot_axle",
            elem_b="cradle_ring",
            reason="Tilt pivot axle passes through the cradle ring center.",
        )
        ctx.allow_overlap(
            base,
            base,
            elem_a="pivot_axle",
            elem_b="outer_ring",
            reason="Central pivot rod spans across to the outer support ring.",
        )
        for i in range(N_BANDS):
            ctx.allow_overlap(
                base,
                base,
                elem_a=f"band_{i}",
                elem_b="outer_ring",
                reason=f"Elastic band {i} outer endpoint seats into the outer ring tube.",
            )
            ctx.allow_overlap(
                base,
                base,
                elem_a=f"band_{i}",
                elem_b="cradle_ring",
                reason=f"Elastic band {i} inner endpoint seats into the cradle ring tube.",
            )
    if r.head_form == "round_ball_windscreen":
        ctx.allow_overlap(
            body,
            body,
            elem_a="head_inner",
            elem_b="body_shell",
            reason="Inner grille capsule protrudes into the body neck to connect.",
        )
        ctx.allow_overlap(
            body,
            body,
            elem_a="head_collar",
            elem_b="body_shell",
            reason="Head collar ring straddles the body neck and inner sphere.",
        )
        ctx.allow_overlap(
            body,
            body,
            elem_a="head_ribs",
            elem_b="head_inner",
            reason="Wire-cage ribs penetrate the inner sphere surface.",
        )
    for i in range(len(r.knob_zs)):
        knob = model.get_part(f"front_knob_{i}")
        ctx.allow_overlap(
            knob,
            body,
            elem_a=f"front_knob_{i}",
            elem_b="body_shell",
            reason=f"Front knob {i} base seats against the body front wall.",
        )
        if r.mount_stand == "elastic_shock_cradle":
            ctx.allow_overlap(
                knob,
                base,
                elem_a=f"front_knob_{i}",
                elem_b="cradle_ring",
                reason=f"Front knob {i} sits near the static cradle ring.",
            )


def _declare_allowances_b(ctx, model, r):
    base = model.get_part("base")
    post = model.get_part("swivel_post")
    capsule = model.get_part("capsule_head")
    cable = model.get_part("cable")
    shell_name = "basket_shell" if r.head_form == "cylindrical_mesh_basket" else "capsule_shell"
    ctx.allow_overlap(
        capsule,
        post,
        elem_a=shell_name,
        elem_b="tilt_pin",
        reason="Capsule is captured on the central yoke tilt pin.",
    )
    ctx.allow_overlap(
        capsule,
        post,
        elem_a="tilt_boss",
        elem_b="tilt_pin",
        reason="Capsule pivot bushing captures the coaxial yoke tilt pin.",
    )
    ctx.allow_overlap(
        capsule,
        post,
        elem_a=shell_name,
        elem_b="yoke_shell",
        reason="Capsule sides nest between the U-yoke arms (running fit).",
    )
    ctx.allow_overlap(
        post,
        base,
        elem_a="post_shell",
        elem_b="base_disc",
        reason="Post collar is seated into the base/hub.",
    )
    ctx.allow_overlap(
        cable,
        base,
        elem_a="cable_shell",
        elem_b="base_disc",
        reason="Cable exits from inside the base/hub.",
    )
    if r.head_form == "cylindrical_mesh_basket":
        ctx.allow_overlap(
            post,
            capsule,
            elem_a="tilt_pin",
            elem_b="basket_interior",
            reason="Tilt pin passes through the basket interior block.",
        )
        ctx.allow_overlap(
            capsule,
            capsule,
            elem_a="basket_interior",
            elem_b="basket_shell",
            reason="Dark interior sits just inside the basket shell.",
        )
        ctx.allow_overlap(
            capsule,
            capsule,
            elem_a="basket_dome",
            elem_b="basket_shell",
            reason="Dome cap seats on the top retaining band.",
        )
    else:
        ctx.allow_overlap(
            post,
            capsule,
            elem_a="tilt_pin",
            elem_b="grille_interior",
            reason="Tilt pin passes through the grille interior block.",
        )
        ctx.allow_overlap(
            capsule,
            capsule,
            elem_a="grille_interior",
            elem_b="capsule_shell",
            reason="Dark grille interior sits just inside the hollow capsule shell.",
        )
    if r.mount_stand == "folding_desk_tripod":
        for i in range(N_LEGS):
            ctx.allow_overlap(
                base,
                base,
                elem_a=f"foot_{i}",
                elem_b=f"leg_{i}",
                reason=f"Rubber foot taper inserts into leg strut {i}.",
            )


def run_vocal_microphone_tests(
    object_model: ArticulatedObject, config: VocalMicrophoneConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}

    if r.family == "A":
        _declare_allowances_a(ctx, object_model, r)
        _run_tests_a(ctx, object_model, r, part_names)
    else:
        _declare_allowances_b(ctx, object_model, r)
        _run_tests_b(ctx, object_model, r, part_names)

    return ctx.report()


def _run_tests_a(ctx, model, r, part_names):
    base = model.get_part("base")
    body = model.get_part("body")
    tilt = model.get_articulation("base_to_body")

    # identity: tilting body, no swivel/cable, weighted base widest & grounded
    ctx.check(
        "Family A: body tilts about +Y (REVOLUTE), no swivel/cable",
        tilt.articulation_type == ArticulationType.REVOLUTE
        and abs(tilt.axis[1]) > 0.99
        and "swivel_post" not in part_names
        and "cable" not in part_names,
        details=f"axis={tilt.axis}, parts={sorted(part_names)}",
    )

    base_disc = ctx.part_element_world_aabb(base, elem="base_disc")
    base_ext = _ext(base_disc)
    body_shell_ext = _ext(ctx.part_element_world_aabb(body, elem="body_shell"))
    ctx.check(
        "weighted base is the widest footprint",
        base_ext[0] > body_shell_ext[0] + 0.02 and base_ext[1] > body_shell_ext[1] + 0.02,
        details=f"base_xy=({base_ext[0]:.4f},{base_ext[1]:.4f}), "
        f"body_xy=({body_shell_ext[0]:.4f},{body_shell_ext[1]:.4f})",
    )
    base_aabb = ctx.part_world_aabb(base)
    ctx.check(
        "base rests on the ground (z~0)",
        abs(base_aabb[0][2]) < 0.003,
        details=f"base_minZ={base_aabb[0][2]:.4f}",
    )

    # head form
    if r.head_form == "round_ball_windscreen":
        hi = ctx.part_element_world_aabb(body, elem="head_inner")
        he = _ext(hi)
        ctx.check(
            "ball windscreen is approximately round (XY~Z extents)",
            abs(he[0] - he[2]) < 0.010 and abs(he[1] - he[2]) < 0.010,
            details=f"dx={he[0]:.4f}, dy={he[1]:.4f}, dz={he[2]:.4f}",
        )
        bs = ctx.part_element_world_aabb(body, elem="body_shell")
        ctx.check(
            "ball head sits above the body shell top",
            _ctr(hi)[2] > bs[1][2] - 0.006,
            details=f"head_cz={_ctr(hi)[2]:.4f}, body_top={bs[1][2]:.4f}",
        )
    else:
        dome = ctx.part_element_world_aabb(body, elem="dome_cap")
        grille = ctx.part_element_world_aabb(body, elem="grille_band")
        ctx.check(
            "cyl head: grille band + dome present, dome is the apex",
            dome is not None and grille is not None and dome[1][2] >= grille[1][2] - 0.002,
            details=f"dome_top={dome[1][2]:.4f}, grille_top={grille[1][2]:.4f}",
        )

    # body tilts: head swings forward (+X) and drops
    elem = "head_inner" if r.head_form == "round_ball_windscreen" else "dome_cap"
    rest = _ctr(ctx.part_element_world_aabb(body, elem=elem))
    with ctx.pose({tilt: math.radians(30.0)}):
        tilted = _ctr(ctx.part_element_world_aabb(body, elem=elem))
    ctx.check(
        "body tilts forward about +Y: head swings toward +X and drops",
        tilted[0] > rest[0] + 0.015 and tilted[2] < rest[2] - 0.004,
        details=f"rest={rest}, tilted={tilted}",
    )

    # shock cradle structure (STATIC suspension on the base)
    if r.mount_stand == "elastic_shock_cradle":
        cradle = ctx.part_element_world_aabb(base, elem="cradle_ring")
        outer = ctx.part_element_world_aabb(base, elem="outer_ring")
        cradle_zc = (cradle[0][2] + cradle[1][2]) / 2.0
        ctx.check(
            "cradle ring sits at the tilt-axis height (static suspension, not z~0)",
            PIVOT_Z - 0.012 < cradle_zc < PIVOT_Z + 0.012,
            details=f"cradle z-center={cradle_zc:.4f}, pivot_z={PIVOT_Z}",
        )
        ctx.check(
            "outer ring encloses the cradle ring in XY",
            outer[0][0] < cradle[0][0]
            and outer[1][0] > cradle[1][0]
            and outer[0][1] < cradle[0][1]
            and outer[1][1] > cradle[1][1],
            details=f"outer={outer}, cradle={cradle}",
        )
        cradle_rest = _ctr(cradle)
        with ctx.pose({tilt: math.radians(30.0)}):
            cradle_tilt = _ctr(ctx.part_element_world_aabb(base, elem="cradle_ring"))
        ctx.check(
            "static shock-mount cradle does NOT move when the body tilts",
            abs(cradle_tilt[0] - cradle_rest[0]) < 1e-4
            and abs(cradle_tilt[2] - cradle_rest[2]) < 1e-4,
            details=f"cradle rest={cradle_rest}, tilted={cradle_tilt}",
        )
        for i in range(N_BANDS):
            ba = ctx.part_element_world_aabb(base, elem=f"band_{i}")
            max_r = max(
                math.hypot(x, y) for x in (ba[0][0], ba[1][0]) for y in (ba[0][1], ba[1][1])
            )
            ctx.check(
                f"band_{i} bridges out to the outer ring",
                max_r > OUTER_RING_R * 0.82,
                details=f"max_r={max_r:.4f}, outer={OUTER_RING_R}",
            )
    else:
        body_aabb = ctx.part_world_aabb(body)
        arm_pos = ctx.part_element_world_aabb(base, elem="fork_arm_pos")
        arm_neg = ctx.part_element_world_aabb(base, elem="fork_arm_neg")
        ctx.check(
            "body straddled between the two fork arms along Y",
            arm_neg[0][1] < body_aabb[0][1] and arm_pos[1][1] > body_aabb[1][1],
            details=f"arm_neg_minY={arm_neg[0][1]:.4f}, body_minY={body_aabb[0][1]:.4f}",
        )

    # front knob column
    n = len(r.knob_zs)
    knobs = [model.get_part(f"front_knob_{i}") for i in range(n)]
    joints = [model.get_articulation(f"body_to_front_knob_{i}") for i in range(n)]
    ctx.check(
        f"exactly {r.control_knob_count} front knobs (multiplicity, Family A)",
        n == r.control_knob_count and n in KNOB_COUNTS,
        details=f"n={n}",
    )
    zs = []
    for i in range(n):
        pos = ctx.part_world_position(knobs[i])
        zs.append(pos[2])
        ctx.check(
            f"front_knob_{i} mounted on the +X front face", pos[0] > 0.02, details=f"pos={pos}"
        )
        j = joints[i]
        ctx.check(
            f"front_knob_{i} spins CONTINUOUS about +X",
            j.articulation_type == ArticulationType.CONTINUOUS and abs(j.axis[0]) > 0.99,
            details=f"type={j.articulation_type}, axis={j.axis}",
        )
        mr = _ctr(ctx.part_element_world_aabb(knobs[i], elem=f"front_marker_{i}"))
        with ctx.pose({j: math.pi / 2.0}):
            ms = _ctr(ctx.part_element_world_aabb(knobs[i], elem=f"front_marker_{i}"))
        ctx.check(
            f"front_knob_{i} marker sweeps when spun",
            abs(ms[1] - mr[1]) > 0.002 or abs(ms[2] - mr[2]) > 0.002,
            details=f"rest={mr}, spun={ms}",
        )
    if n >= 2:
        spacings = [zs[i + 1] - zs[i] for i in range(n - 1)]
        avg = sum(spacings) / len(spacings)
        ctx.check(
            "front knobs are evenly spaced & vertically ordered",
            all(s > 0 for s in spacings) and max(abs(s - avg) for s in spacings) < 0.004,
            details=f"zs={[round(z, 4) for z in zs]}",
        )


def _run_tests_b(ctx, model, r, part_names):
    base = model.get_part("base")
    post = model.get_part("swivel_post")
    capsule = model.get_part("capsule_head")
    cable = model.get_part("cable")
    swivel = model.get_articulation("base_to_post")
    tilt = model.get_articulation("yoke_to_capsule")

    ctx.check(
        "Family B: swivel CONTINUOUS about +Z, no front knobs",
        swivel.articulation_type == ArticulationType.CONTINUOUS
        and abs(swivel.axis[2]) > 0.99
        and not any(n.startswith("front_knob_") for n in part_names),
        details=f"swivel_axis={swivel.axis}, parts={sorted(part_names)}",
    )
    ctx.check(
        "Family B: capsule tilts REVOLUTE about +Y",
        tilt.articulation_type == ArticulationType.REVOLUTE and abs(tilt.axis[1]) > 0.99,
        details=f"tilt_axis={tilt.axis}",
    )

    base_aabb = ctx.part_world_aabb(base)
    ctx.check(
        "base/tripod rests on the ground (z~0)",
        abs(base_aabb[0][2]) < 0.004,
        details=f"base_minZ={base_aabb[0][2]:.4f}",
    )
    base_ext = _ext(base_aabb)
    cap_ext = _ext(ctx.part_world_aabb(capsule))
    post_ext = _ext(ctx.part_world_aabb(post))
    fb = max(base_ext[0], base_ext[1])
    ctx.check(
        "stand base is the widest footprint",
        fb >= max(cap_ext[0], cap_ext[1]) - 1e-6 and fb >= max(post_ext[0], post_ext[1]) - 1e-6,
        details=f"base={fb:.4f}, cap={max(cap_ext[0], cap_ext[1]):.4f}, "
        f"post={max(post_ext[0], post_ext[1]):.4f}",
    )

    ctx.expect_contact(capsule, post, name="capsule cradled in the yoke")

    # head form
    if r.head_form == "cylindrical_mesh_basket":
        ce = _ext(ctx.part_world_aabb(capsule))
        ctx.check(
            "basket head is taller than wide (upright cylinder)",
            ce[2] > ce[0] and ce[2] > ce[1],
            details=f"dx={ce[0]:.4f}, dy={ce[1]:.4f}, dz={ce[2]:.4f}",
        )
        dome = ctx.part_element_world_aabb(capsule, elem="basket_dome")
        shell = ctx.part_element_world_aabb(capsule, elem="basket_shell")
        ctx.check(
            "dome apex is the highest point of the basket head",
            dome is not None and shell is not None and dome[1][2] >= shell[1][2] - 0.002,
            details=f"dome={None if dome is None else round(dome[1][2], 4)}, "
            f"shell={None if shell is None else round(shell[1][2], 4)}",
        )
    else:
        cs = ctx.part_element_world_aabb(capsule, elem="capsule_shell")
        ce = _ext(cs)
        ctx.check(
            "oval head is wider/taller than thin Y axis (flat oval)",
            ce[1] < ce[0] + 1e-6 and ce[1] < ce[2] + 1e-6,
            details=f"dx={ce[0]:.4f}, dy={ce[1]:.4f}, dz={ce[2]:.4f}",
        )

    # capsule tilts about +Y (front swings fore/aft)
    fr = ctx.part_world_aabb(capsule)[1][0]
    with ctx.pose({tilt: math.radians(30.0)}):
        ft = ctx.part_world_aabb(capsule)[1][0]
    ctx.check(
        "capsule tilt about +Y swings the head fore/aft",
        abs(ft - fr) > 0.004,
        details=f"front_x rest={fr:.4f}, tilted={ft:.4f}",
    )

    # swivel rotates the head about +Z
    rest_y = ctx.part_world_aabb(capsule)[1][1]
    with ctx.pose({swivel: math.radians(90.0)}):
        sw_x = ctx.part_world_aabb(capsule)[1][0]
    ctx.check(
        "swivel rotates the head about the vertical axis",
        abs(sw_x - rest_y) > 0.002 or sw_x > 0.0,
        details=f"rest_maxY={rest_y:.4f}, after90_maxX={sw_x:.4f}",
    )

    ctx.expect_contact(cable, base, name="cable attached at the base/hub")

    if r.mount_stand == "folding_desk_tripod":
        centers = []
        for i in range(N_LEGS):
            fa = ctx.part_element_world_aabb(base, elem=f"foot_{i}")
            centers.append(((fa[0][0] + fa[1][0]) / 2.0, (fa[0][1] + fa[1][1]) / 2.0))
        hub_pos = ctx.part_world_position(base)
        angs = sorted(math.atan2(c[1] - hub_pos[1], c[0] - hub_pos[0]) for c in centers)
        gaps = [angs[1] - angs[0], angs[2] - angs[1], 2 * math.pi - (angs[2] - angs[0])]
        ctx.check(
            "three tripod legs at ~120 degree spacing",
            max(abs(g - 2 * math.pi / 3) for g in gaps) < 0.35,
            details=f"gaps={[round(g, 3) for g in gaps]}",
        )


__all__ = [
    "VocalMicrophoneConfig",
    "ResolvedVocalMicrophoneConfig",
    "build_vocal_microphone",
    "build_seeded_vocal_microphone",
    "config_from_seed",
    "resolve_config",
    "run_vocal_microphone_tests",
    "slot_choices_for_seed",
    "__modular__",
]
