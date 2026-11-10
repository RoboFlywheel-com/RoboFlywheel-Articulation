# SPDX-License-Identifier: Apache-2.0

"""Forged articulated blacksmith tongs — modular template.

NOTE on the slug name: "blacksmith_tongs" here = a **forged articulated
blacksmith tong** (two symmetric forged-steel arms — each a jaw + half-lapped
elliptical boss + a very long rein/handle — crossing at the boss and joined by
ONE round-head rivet, so squeezing the reins swings the jaws shut about the
rivet). This is NOT scissors (finger-loop cutting), NOT pliers / a wrench
(mid-cross box-joint hand tool), NOT a wooden serving tong (the separate
``wooden_tongs`` slug), and NOT a screw clamp / vise (the separate ``clamp``
slug).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Others_Others_blacksmith_tongs.md`` and the
``picture/Others/blacksmith tongs`` 5-star sample pool (3 parents + 8 variants
= 11), all synced under ``data/records/``.

Coordinate convention (unified across the whole template on the wolf-jaw XY
convention — 9/11 samples use it directly; the bow-ring & pincers XZ parents
are rebased into it). The tool lies flat in the XY plane (flat-bar normal = Z);
a jaw runs along **+X** from the boss (x≈0) to its tip (x≈0.086), the rein runs
along **−X** to its tip (x≈−0.462); the two arms stack in **±Z** at the boss as
a half-lap, the moving arm being the same forging flipped 180° about the X axis
(jaw/rein swap sides, the lap faces oppose). The shared ``rivet_pivot`` REVOLUTE
has **axis=(0,0,−1)** (⟂ tool plane), origin at ``(0,0,Z_LIFT)`` (boss-center
rivet axis), ``lower=0`` (jaws nearly meet — relaxed closed rest) / ``upper``
≈0.3 (jaws open + moving rein swings away). The arm count is FIXED at 2 (emitted
by a shared ``_emit_arm`` enumerate loop, NOT a multiplicity axis); the rivet is
the single captured pivot pin carried by the fixed arm.

Three named module axes (all are jaw/boss/rein MESH or decoration dimensions —
none change the part tree or the single-REVOLUTE joint topology):

  * ``jaw_shape`` (6): the working-end mesh + closed-contact semantics —
    wolf_flat (flat V-notch) / ring_bow (half-ring oval bow loop) /
    pincer_claw (thick inward claw + bite edge) / flat_box (parallel-face
    pickup) / vgroove (longitudinal V diamond socket) / hollow_bit (concave
    half-cylinder bore). The primary defining axis.
  * ``rein_form`` (4 + 1 secondary): the long handle's mesh / tip —
    long_straight (superellipse taper) / scrolled (volute spiral tip) /
    looped_eye (closed torus eye loop) / square_bar (constant square bar) +
    short_stout_handle (a short bowed lofted handle, secondary, rebased from
    the pincers parent).
  * ``boss_rivet`` (3): the boss/rivet pivot detail — flat_boss_domed (flat
    boss + round dome heads, proud) / countersunk_flush (conical heads flush in
    a countersink) / raised_boss_collar (an inline forged collar hub raising
    the rivet heads).

The jaw V-grooves / dimples / claw bite-edge & neck web / rein scroll / eye
loop / boss collar / countersink are all forged INTO the arm mesh (Rule 1: arm
visuals, never FIXED decoration parts). The rivet is the fixed arm's captured
pivot pin passing through the moving arm boss, so the joint omits a
``MatingContract`` (grandfathered captured pin) and relies on the flat
articulation-origin baseline + an element-scoped ``allow_overlap(rivet, boss)``
mirroring every source record's run_tests.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

JawShape = Literal[
    "wolf_flat",
    "ring_bow",
    "pincer_claw",
    "flat_box",
    "vgroove",
    "hollow_bit",
]
ReinForm = Literal[
    "long_straight",
    "scrolled",
    "looped_eye",
    "square_bar",
    "short_stout_handle",
]
BossRivet = Literal[
    "flat_boss_domed",
    "countersunk_flush",
    "raised_boss_collar",
]
PaletteStyle = Literal[
    "dark_forged",
    "weathered_gray",
    "polished_highlight",
    "browned_blued",
    "bright_bare_steel",
    "aged_pewter",
]

JAW_SHAPES: tuple[JawShape, ...] = (
    "wolf_flat",
    "ring_bow",
    "pincer_claw",
    "flat_box",
    "vgroove",
    "hollow_bit",
)
REIN_FORMS: tuple[ReinForm, ...] = (
    "long_straight",
    "scrolled",
    "looped_eye",
    "square_bar",
    "short_stout_handle",
)
BOSS_RIVETS: tuple[BossRivet, ...] = (
    "flat_boss_domed",
    "countersunk_flush",
    "raised_boss_collar",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "dark_forged",
    "weathered_gray",
    "polished_highlight",
    "browned_blued",
    "bright_bare_steel",
    "aged_pewter",
)

# ---------------------------------------------------------------------------
# Per-seed palettes (spec §7). Keys: body (rein/arm), jaw (working end), boss,
# rivet. Every .visual material is driven off this dict so the swept pool is
# colorful (module_topology_diversity only counts structure).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "dark_forged": {
        "body": (0.27, 0.28, 0.30, 1.0),
        "jaw": (0.23, 0.24, 0.26, 1.0),
        "boss": (0.23, 0.24, 0.26, 1.0),
        "rivet": (0.20, 0.21, 0.23, 1.0),
    },
    "weathered_gray": {
        "body": (0.37, 0.38, 0.40, 1.0),
        "jaw": (0.30, 0.31, 0.33, 1.0),
        "boss": (0.26, 0.27, 0.29, 1.0),
        "rivet": (0.25, 0.26, 0.28, 1.0),
    },
    "polished_highlight": {
        "body": (0.37, 0.38, 0.40, 1.0),
        "jaw": (0.55, 0.57, 0.59, 1.0),
        "boss": (0.30, 0.31, 0.33, 1.0),
        "rivet": (0.44, 0.45, 0.47, 1.0),
    },
    "browned_blued": {
        "body": (0.22, 0.18, 0.16, 1.0),
        "jaw": (0.18, 0.15, 0.13, 1.0),
        "boss": (0.16, 0.16, 0.20, 1.0),
        "rivet": (0.14, 0.14, 0.18, 1.0),
    },
    "bright_bare_steel": {
        "body": (0.62, 0.63, 0.65, 1.0),
        "jaw": (0.66, 0.67, 0.69, 1.0),
        "boss": (0.58, 0.59, 0.61, 1.0),
        "rivet": (0.70, 0.71, 0.73, 1.0),
    },
    "aged_pewter": {
        "body": (0.45, 0.46, 0.47, 1.0),
        "jaw": (0.40, 0.41, 0.42, 1.0),
        "boss": (0.42, 0.43, 0.44, 1.0),
        "rivet": (0.36, 0.37, 0.38, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), unified wolf-jaw XY convention.
# A long forged tong: ~0.55 m overall, boss ~0.035 m across, rivet ~0.012 m.
# Mechanical fits (boss plate thickness, lap clearance, rivet shaft) are never
# scaled; rein length / jaw width&length / boss size / splay / travel / rivet
# head ARE scaled (per the spec parameter table).
# ---------------------------------------------------------------------------
Z_LIFT = 0.0085             # tool plane height (the tongs lie flat above z=0)
Z_LIFT_COLLAR = 0.014       # raised_boss_collar needs a taller stack

JAW_T = 0.0096              # bar thickness at the jaw (Z)
JAW_T_BORE = 0.011          # thicker bar for hollow_bit (contains the bore)
JAW_TIP_X = 0.086

BOSS_A = 0.020              # boss ellipse semi-axis along X
BOSS_B = 0.0155             # boss ellipse semi-axis along Y
BOSS_PLATE_T = 0.0048       # one half-lapped boss plate thickness

LAP_R = 0.022               # half-lap clearance radius around the rivet
LAP_EPS = 0.00006

REIN_TIP_X = -0.462
REIN_TIP_Y = -0.036
REIN_TIP_R = 0.0035
REIN_BAR_HALF = 0.0065      # square_bar half-side
REIN_SECTION_PTS = 32

RIVET_SHAFT_R = 0.0045
RIVET_HEAD_R = 0.0060       # domed head radius
FLUSH_HEAD_R = 0.0070       # countersink outer radius
HEAD_DEPTH = 0.0020

# Raised boss collar.
COLLAR_R = 0.0090
COLLAR_H = 0.0030

# Scroll volute (scrolled).
SCROLL_OUTER_R = 0.016
SCROLL_INNER_R = 0.004
SCROLL_TURNS = 1.5
SCROLL_SECTIONS = 28
SCROLL_CIRCLE_N = 18

# Eye loop (looped_eye).
EYE_LOOP_R = 0.011
EYE_TUBE_R = 0.0035

# V-groove (vgroove).
V_GROOVE_DEPTH = 0.0020
V_GROOVE_HALF_Z = 0.0035

# Hollow bit bore (hollow_bit).
BORE_R = 0.005
BIT_FACE_GAP = 0.0005

# Wolf-jaw plan outline (fixed +Y half).
JAW_PTS = [
    (0.010, 0.0150),
    (0.050, 0.0100),
    (0.086, 0.0058),
    (0.086, 0.0036),
    (0.073, 0.0008),
    (0.040, 0.0016),
    (0.010, 0.0045),
]
# Flat box jaw outline (parallel inner/outer faces).
JAW_BOX_INNER_Y = 0.0010
JAW_BOX_OUTER_Y = 0.0150
JAW_BOX_START_X = 0.010
JAW_BOX_TIP_X = 0.080
JAW_BOX_PTS = [
    (JAW_BOX_START_X, JAW_BOX_OUTER_Y),
    (JAW_BOX_TIP_X, JAW_BOX_OUTER_Y),
    (JAW_BOX_TIP_X, JAW_BOX_INNER_Y),
    (JAW_BOX_START_X, JAW_BOX_INNER_Y),
]
# Hollow bit jaw outline (inner face near centerline; bore carves the scoop).
BIT_JAW_PTS = [
    (0.010, 0.0150),
    (0.050, 0.0120),
    (0.086, 0.0080),
    (0.086, BIT_FACE_GAP),
    (0.073, BIT_FACE_GAP),
    (0.040, BIT_FACE_GAP),
    (0.010, BIT_FACE_GAP),
]
# V-groove stations along the inner face (x, face_y).
V_GROOVE_STATIONS = [
    (0.015, 0.00402),
    (0.030, 0.00257),
    (0.045, 0.00148),
    (0.060, 0.00112),
    (0.073, 0.00080),
    (0.082, 0.00274),
]

GROOVE_R = 0.0014
GROOVE_SINK = 0.0008
GROOVES = [
    (0.047, 0.0016 - 0.0008 * (0.047 - 0.040) / 0.033),
    (0.056, 0.0016 - 0.0008 * (0.056 - 0.040) / 0.033),
    (0.065, 0.0016 - 0.0008 * (0.065 - 0.040) / 0.033),
]
DIMPLE_R = 0.004
DIMPLE_DEPTH = 0.0005
BOSS_DIMPLES = [(0.006, 0.0065), (-0.0075, -0.0045), (-0.0115, 0.0060), (0.0015, -0.0105)]
JAW_DIMPLES_TOP = [(0.024, 0.0085), (0.040, 0.0062), (0.057, 0.0048)]
JAW_DIMPLES_BOT = [(0.031, 0.0072), (0.049, 0.0052)]

# Base rein superellipse stations (x, y_center, half_w, half_h, exponent).
REIN_SECTIONS_BASE = [
    (-0.014, -0.0090, 0.0070, 0.0047, 5.0),
    (-0.052, -0.0125, 0.00775, 0.00775, 5.0),
    (-0.130, -0.0190, 0.00675, 0.00675, 4.0),
    (-0.240, -0.0268, 0.00575, 0.00575, 3.2),
    (-0.350, -0.0322, 0.00475, 0.00475, 2.6),
    (REIN_TIP_X, REIN_TIP_Y, REIN_TIP_R, REIN_TIP_R, 2.0),
]

# ---- short_stout_handle (rebased from pincers parent) ----
# Original pincers handle ran along -Z (z, center_x, width, thickness); the X
# axis was lateral and Y was thickness. Rebased to the wolf-jaw XY convention:
# the handle runs along -X (replacing the rein), the lateral bow is in Y, and
# the bar thickness is Z. (z->-x, center_x->-y_bow, thickness->z).
HANDLE_SECTIONS = (
    (-0.0080, 0.0000, 0.0200, 0.0150),
    (-0.0600, 0.0200, 0.0190, 0.0145),
    (-0.1300, 0.0330, 0.0165, 0.0125),
    (-0.1900, 0.0330, 0.0140, 0.0105),
    (-0.2200, 0.0300, 0.0150, 0.0115),
)
HANDLE_TIP_R = 0.0055
HANDLE_TIP_C = (-0.2230, 0.0295)  # (x, y_bow) of the handle-tip ball center


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class BlacksmithTongsConfig:
    jaw_shape: JawShape | None = None
    rein_form: ReinForm | None = None
    boss_rivet: BossRivet | None = None
    palette_style: PaletteStyle = "dark_forged"
    rein_length_scale: float = 1.0
    jaw_width_scale: float = 1.0
    jaw_length_scale: float = 1.0
    boss_size_scale: float = 1.0
    splay_angle_scale: float = 1.0
    pivot_travel_scale: float = 1.0
    rivet_head_scale: float = 1.0
    bore_radius_scale: float = 1.0
    vgroove_depth_scale: float = 1.0
    scroll_turns_scale: float = 1.0
    eye_loop_scale: float = 1.0
    collar_height_scale: float = 1.0
    name: str = "blacksmith_tongs"


@dataclass(frozen=True)
class ResolvedBlacksmithTongsConfig:
    jaw_shape: JawShape
    rein_form: ReinForm
    boss_rivet: BossRivet
    palette_style: PaletteStyle
    # Stacking / pivot.
    z_lift: float
    jaw_t: float
    pivot_upper: float
    # Boss / rivet.
    boss_a: float
    boss_b: float
    rivet_shaft_r: float
    rivet_head_r: float
    flush_head_r: float
    collar_h: float
    collar_r: float
    # Jaw scales.
    jaw_width_scale: float
    jaw_length_scale: float
    bore_r: float
    vgroove_depth: float
    vgroove_half_z: float
    # Rein scales.
    rein_length_scale: float
    splay_scale: float
    scroll_turns: float
    scroll_outer_r: float
    eye_loop_r: float
    name: str


# ---------------------------------------------------------------------------
# Seed sampling + resolution
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> BlacksmithTongsConfig:
    rng = random.Random(seed)
    # 1. named slots (the topology / mesh-class axes).
    jaw_shape = rng.choice(JAW_SHAPES)
    rein_form = rng.choice(REIN_FORMS)
    boss_rivet = rng.choice(BOSS_RIVETS)
    # 2. conditional params (always drawn so the RNG stream is stable; only
    #    active for the matching module).
    bore_radius_scale = round(rng.uniform(0.85, 1.12), 4)
    vgroove_depth_scale = round(rng.uniform(0.80, 1.15), 4)
    scroll_turns_scale = round(rng.uniform(0.80, 1.15), 4)
    eye_loop_scale = round(rng.uniform(0.85, 1.12), 4)
    collar_height_scale = round(rng.uniform(0.85, 1.15), 4)
    # 3. independent scales.
    rein_length_scale = round(rng.uniform(0.85, 1.15), 4)
    jaw_width_scale = round(rng.uniform(0.88, 1.15), 4)
    jaw_length_scale = round(rng.uniform(0.90, 1.12), 4)
    boss_size_scale = round(rng.uniform(0.88, 1.15), 4)
    splay_angle_scale = round(rng.uniform(0.80, 1.15), 4)
    pivot_travel_scale = round(rng.uniform(0.85, 1.15), 4)
    rivet_head_scale = round(rng.uniform(0.85, 1.15), 4)
    # 4. palette (not a slot_choice).
    palette_style = rng.choice(PALETTE_STYLES)
    return BlacksmithTongsConfig(
        jaw_shape=jaw_shape,
        rein_form=rein_form,
        boss_rivet=boss_rivet,
        palette_style=palette_style,
        rein_length_scale=rein_length_scale,
        jaw_width_scale=jaw_width_scale,
        jaw_length_scale=jaw_length_scale,
        boss_size_scale=boss_size_scale,
        splay_angle_scale=splay_angle_scale,
        pivot_travel_scale=pivot_travel_scale,
        rivet_head_scale=rivet_head_scale,
        bore_radius_scale=bore_radius_scale,
        vgroove_depth_scale=vgroove_depth_scale,
        scroll_turns_scale=scroll_turns_scale,
        eye_loop_scale=eye_loop_scale,
        collar_height_scale=collar_height_scale,
        name=f"seeded_blacksmith_tongs_{seed}",
    )


def resolve_config(
    config: BlacksmithTongsConfig | None = None,
) -> ResolvedBlacksmithTongsConfig:
    cfg = config or BlacksmithTongsConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    jaw_shape = _pick(cfg.jaw_shape, JAW_SHAPES)
    rein_form = _pick(cfg.rein_form, REIN_FORMS)
    boss_rivet = _pick(cfg.boss_rivet, BOSS_RIVETS)

    rein_length_scale = _clamp(cfg.rein_length_scale, 0.85, 1.15)
    jaw_width_scale = _clamp(cfg.jaw_width_scale, 0.88, 1.15)
    jaw_length_scale = _clamp(cfg.jaw_length_scale, 0.90, 1.12)
    boss_size_scale = _clamp(cfg.boss_size_scale, 0.88, 1.15)
    splay_scale = _clamp(cfg.splay_angle_scale, 0.80, 1.15)
    pivot_travel_scale = _clamp(cfg.pivot_travel_scale, 0.85, 1.15)
    rivet_head_scale = _clamp(cfg.rivet_head_scale, 0.85, 1.15)
    bore_radius_scale = _clamp(cfg.bore_radius_scale, 0.85, 1.12)
    vgroove_depth_scale = _clamp(cfg.vgroove_depth_scale, 0.80, 1.15)
    scroll_turns_scale = _clamp(cfg.scroll_turns_scale, 0.80, 1.15)
    eye_loop_scale = _clamp(cfg.eye_loop_scale, 0.85, 1.12)
    collar_height_scale = _clamp(cfg.collar_height_scale, 0.85, 1.15)

    # ---- Boss / rivet ----
    boss_a = BOSS_A * boss_size_scale
    boss_b = BOSS_B * boss_size_scale
    rivet_shaft_r = RIVET_SHAFT_R
    rivet_head_r = RIVET_HEAD_R * rivet_head_scale
    flush_head_r = FLUSH_HEAD_R * rivet_head_scale
    # Inequality (spec §7 #1): the captured rivet head must stay inside the boss
    # footprint (expect_within(rivet, boss) with margin). Cap the head radius to
    # the smaller boss semi-axis minus a margin.
    head_cap = min(boss_a, boss_b) - 0.0015
    rivet_head_r = min(rivet_head_r, head_cap)
    flush_head_r = min(flush_head_r, head_cap)
    # Domed/collar heads must stay proud => keep a sane minimum.
    rivet_head_r = max(rivet_head_r, rivet_shaft_r + 0.0008)
    flush_head_r = max(flush_head_r, rivet_shaft_r + 0.0015)

    collar_h = COLLAR_H * collar_height_scale
    collar_r = COLLAR_R

    # ---- Stacking / Z lift ----
    if boss_rivet == "raised_boss_collar":
        # The collar rivet head seats on the collar outer face; keep it small so
        # the whole stack (boss plate + collar + head) stays under the flat-tool
        # budget on each side of the lap plane.
        rivet_head_r = min(rivet_head_r, collar_r - 0.0010, 0.0050)
        # Inequality (spec §7 #3): one side's outward stack = boss plate + collar
        # + head radius. z_lift = that stack + a small ground margin lifts the
        # whole tool above z=0; total z_extent = 2*stack stays <= 0.030. With the
        # pincer claw's short neck the collar would otherwise foul the jaw back,
        # so the lift gets a touch more clearance (spec §13 conditional).
        side_stack = BOSS_PLATE_T + collar_h + rivet_head_r
        z_lift = side_stack + 0.0006
        if jaw_shape == "pincer_claw":
            z_lift += 0.0008  # extra clearance for the short claw neck
    else:
        z_lift = Z_LIFT

    jaw_t = JAW_T_BORE if jaw_shape == "hollow_bit" else JAW_T

    # ---- Pivot travel ----
    # Spec: nominal upper = 0.3 (jaws open + moving rein swings away). Keep the
    # baseline upper EXACTLY 0.3 when the scale is ~1 so the per-jaw open-pose
    # gap assertions (calibrated from the source records at q=0.3) stay valid;
    # scale only modestly and never below the value that opens the jaws.
    pivot_upper = _clamp(0.3 * pivot_travel_scale, 0.26, 0.36)

    # ---- Jaw conditional scales ----
    bore_r = BORE_R * bore_radius_scale
    # Inequality (spec §7 #5): the bore must not cut through the jaw thickness.
    bore_r = min(bore_r, jaw_t / 2.0 - 0.0008)
    vgroove_depth = V_GROOVE_DEPTH * vgroove_depth_scale
    vgroove_half_z = min(V_GROOVE_HALF_Z * vgroove_depth_scale, jaw_t / 2.0 - 0.0008)

    # ---- Rein conditional scales ----
    scroll_turns = SCROLL_TURNS * scroll_turns_scale
    scroll_outer_r = SCROLL_OUTER_R * scroll_turns_scale
    eye_loop_r = EYE_LOOP_R * eye_loop_scale

    return ResolvedBlacksmithTongsConfig(
        jaw_shape=jaw_shape,
        rein_form=rein_form,
        boss_rivet=boss_rivet,
        palette_style=palette_style,
        z_lift=z_lift,
        jaw_t=jaw_t,
        pivot_upper=pivot_upper,
        boss_a=boss_a,
        boss_b=boss_b,
        rivet_shaft_r=rivet_shaft_r,
        rivet_head_r=rivet_head_r,
        flush_head_r=flush_head_r,
        collar_h=collar_h,
        collar_r=collar_r,
        jaw_width_scale=jaw_width_scale,
        jaw_length_scale=jaw_length_scale,
        bore_r=bore_r,
        vgroove_depth=vgroove_depth,
        vgroove_half_z=vgroove_half_z,
        rein_length_scale=rein_length_scale,
        splay_scale=splay_scale,
        scroll_turns=scroll_turns,
        scroll_outer_r=scroll_outer_r,
        eye_loop_r=eye_loop_r,
        name=cfg.name or "blacksmith_tongs",
    )


def with_overrides(config: BlacksmithTongsConfig, **kwargs: object) -> BlacksmithTongsConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: BlacksmithTongsConfig | ResolvedBlacksmithTongsConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedBlacksmithTongsConfig)
        else resolve_config(config)
    )
    return (
        ("jaw_shape", r.jaw_shape),
        ("rein_form", r.rein_form),
        ("boss_rivet", r.boss_rivet),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared low-level builders (boss / rivet / dimples).
# ---------------------------------------------------------------------------
def _lap_cutter() -> cq.Workplane:
    """Material below z=LAP_EPS within LAP_R of the rivet is forged away. The
    cutter only needs to reach a little below the bar (the boss / jaw / rein are
    all <= ~0.006 m thick), so a short cutter is used; an over-tall cutter makes
    the boolean against the thin lofted rein fragile (it can leave the cutter
    body behind as a stray sliver on some scaled-rein seeds)."""
    return (
        cq.Workplane("XY")
        .workplane(offset=-0.014)
        .circle(LAP_R)
        .extrude(0.014 + LAP_EPS)
    )


def _dimple(x: float, y: float, z_face: float, sign: int) -> cq.Workplane:
    cz = z_face + sign * (DIMPLE_R - DIMPLE_DEPTH)
    return cq.Workplane("XY", origin=(x, y, cz)).sphere(DIMPLE_R)


def _scale_xy(solid: cq.Workplane, sx: float, sy: float) -> cq.Workplane:
    """Anisotropic in-plane scale via a TopoDS transform (X and Y only)."""
    if abs(sx - 1.0) < 1e-9 and abs(sy - 1.0) < 1e-9:
        return solid
    from cadquery import Matrix

    m = Matrix(
        [
            [sx, 0.0, 0.0, 0.0],
            [0.0, sy, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
        ]
    )
    shape = solid.val().transformGeometry(m)
    return cq.Workplane(obj=shape)


# ---------------------------------------------------------------------------
# Jaw mesh helpers (Slot A). Both arms share one helper per shape.
# ---------------------------------------------------------------------------
def _jaw_flat_outline(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    return cq.Workplane("XY").polyline(JAW_PTS).close().extrude(r.jaw_t / 2.0, both=True)


def _add_grooves_dimples(r: ResolvedBlacksmithTongsConfig, jaw: cq.Workplane, *, grooves: bool) -> cq.Workplane:
    if grooves:
        for gx, face_y in GROOVES:
            groove = (
                cq.Workplane("XY")
                .center(gx, face_y + GROOVE_SINK)
                .circle(GROOVE_R)
                .extrude(0.02, both=True)
            )
            jaw = jaw.cut(groove)
    for dx, dy in JAW_DIMPLES_TOP:
        jaw = jaw.cut(_dimple(dx, dy, r.jaw_t / 2.0, +1))
    for dx, dy in JAW_DIMPLES_BOT:
        jaw = jaw.cut(_dimple(dx, dy, -r.jaw_t / 2.0, -1))
    return jaw


def _wolf_jaw_solid(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    jaw = _jaw_flat_outline(r)
    jaw = _add_grooves_dimples(r, jaw, grooves=True)
    return jaw.cut(_lap_cutter())


def _box_jaw_solid(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    jaw = cq.Workplane("XY").polyline(JAW_BOX_PTS).close().extrude(r.jaw_t / 2.0, both=True)
    jaw = _add_grooves_dimples(r, jaw, grooves=False)
    return jaw.cut(_lap_cutter())


def _vgroove_cutter(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    lip_overshoot = 0.0004
    wires: list[cq.Wire] = []
    for x, fy in V_GROOVE_STATIONS:
        pts = [
            cq.Vector(x, fy - lip_overshoot, -r.vgroove_half_z),
            cq.Vector(x, fy + r.vgroove_depth, 0.0),
            cq.Vector(x, fy - lip_overshoot, +r.vgroove_half_z),
        ]
        pts.append(pts[0])
        wires.append(cq.Wire.makePolygon(pts))
    return cq.Workplane(obj=cq.Solid.makeLoft(wires))


def _vgroove_jaw_solid(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    jaw = _jaw_flat_outline(r)
    jaw = jaw.cut(_vgroove_cutter(r))
    jaw = _add_grooves_dimples(r, jaw, grooves=False)
    return jaw.cut(_lap_cutter())


def _bore_cutter(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    return (
        cq.Workplane("YZ", origin=(0.005, 0.0, 0.0))
        .circle(r.bore_r)
        .extrude(JAW_TIP_X + 0.002)
    )


def _bit_jaw_solid(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    jaw = cq.Workplane("XY").polyline(BIT_JAW_PTS).close().extrude(r.jaw_t / 2.0, both=True)
    jaw = jaw.cut(_bore_cutter(r))
    jaw = _add_grooves_dimples(r, jaw, grooves=False)
    return jaw.cut(_lap_cutter())


# ---- ring_bow (rebased from bow-ring XZ parent to XY) ----
# Original: ring in the world XZ plane (X across, Z up the tool, Y thickness).
# Rebase: jaw runs along +X, lateral/splay in Y, lap thickness in Z. The half
# ring becomes a flat band in the XY plane whose ring center sits OUT ALONG +X
# (a caliper bow loop forming when the two halves close). We swap the parent's
# (X_lat, Z_up) -> (Y_lat, X_along) and thickness Y -> Z.
RING_OUT_ALONG = 0.045   # outer semi-extent along +X (was RING_OUT_Z up)
RING_OUT_LAT = 0.045     # outer semi-extent in Y (was RING_OUT_X across)
RING_BAR_W = 0.013
RING_CX = 0.060          # ring center distance along +X from the boss
RING_SEAM = 0.0008       # the band stops just short of the centerline (own side)


def _ring_half_solid(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    """Flat half-ring bow loop for the fixed (+Y) half, in the XY plane.

    The bow is a flat elliptical band (outer ellipse minus inner ellipse)
    extruded through the bar thickness in Z. The band is kept strictly on its
    own (+Y) side of the centerline (stopping ``RING_SEAM`` short of y=0, the
    same +Y convention the wolf jaw uses), so the flipped moving half (-Y) runs
    alongside without interpenetrating; the two halves read as one large open
    oval bow with a thin centerline seam at the boss end and the far +X apex
    (caliper-style ring jaws)."""
    half_t = r.jaw_t / 2.0
    outer = (
        cq.Workplane("XY", origin=(RING_CX, 0.0, 0.0))
        .ellipse(RING_OUT_ALONG, RING_OUT_LAT)
        .extrude(half_t, both=True)
    )
    inner = (
        cq.Workplane("XY", origin=(RING_CX, 0.0, 0.0))
        .ellipse(RING_OUT_ALONG - RING_BAR_W, RING_OUT_LAT - RING_BAR_W)
        .extrude(half_t * 3.0, both=True)
    )
    band = outer.cut(inner)
    # Keep strictly the +Y half (centerline side, short of the seam) so the two
    # arms close into one oval without crossing the centerline.
    keep = (
        cq.Workplane("XY")
        .box(0.4, 0.4, 0.4)
        .translate((RING_CX, 0.2 + RING_SEAM, 0.0))
    )
    band = band.intersect(keep)
    return band.cut(_lap_cutter())


# ---- pincer_claw (rebased from pincers XZ parent to XY) ----
# Original claw profile in XZ (X lateral, Z up the tool), thickness extruded in
# Y. Rebase: the "up the tool" Z axis becomes +X (jaw along), the lateral X
# becomes Y (splay), and the thickness Y becomes Z. We build the claw profile in
# the XY plane (X = former Z up, Y = former lateral X) and extrude through Z.
CLAW_T = JAW_T  # full claw thickness in Z (bar-thickness band, not the thick head)
CLAW_BITE_Y = 0.0010   # worn bite edge inner face (own +Y side, just short of y=0)


def _claw_jaw_solid(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    """Thick inward-hooking claw jaw for the fixed (+Y) half, rebased to XY.

    Profile drawn in XY: X runs from the boss (low x) out to the bite tip (high
    x); Y is the lateral/centerline direction (the claw body curves outward to
    +Y and hooks back toward the centerline, the same +Y convention the wolf
    jaw uses). The whole jaw stays strictly on its own (+Y) side so the flipped
    moving claw runs alongside without interlocking; the worn bite edges nearly
    meet at the centerline while the jaw backs keep a visible throat (nipper /
    end-cutter identity).
    """
    half_t = CLAW_T / 2.0
    # Body: a thick claw that bulges out to +Y mid-length and hooks back so the
    # leading (bite) face returns toward the centerline near the tip.
    prof = (
        cq.Workplane("XY")
        .moveTo(0.0265, 0.0085)
        .lineTo(0.0270, 0.0240)
        .spline(
            [
                (0.0400, 0.0298),
                (0.0520, 0.0290),
                (0.0650, 0.0180),
                (0.0705, 0.0075),
                (0.0718, 0.0040),
            ],
            includeCurrent=True,
        )
        .lineTo(0.0640, 0.0050)
        .spline(
            [
                (0.0560, 0.0110),
                (0.0450, 0.0140),
                (0.0340, 0.0120),
            ],
            includeCurrent=True,
        )
        .close()
        .extrude(half_t, both=True)
    )
    # Narrow worn bite-edge strip at the tip, reaching nearest the centerline.
    bite = (
        cq.Workplane("XY")
        .moveTo(0.0625, CLAW_BITE_Y)
        .lineTo(0.0585, 0.0050)
        .lineTo(0.0718, 0.0050)
        .lineTo(0.0718, CLAW_BITE_Y)
        .close()
        .extrude(half_t, both=True)
    )
    prof = prof.union(bite)
    # Neck web carrying the jaw down onto the boss (forged into the jaw).
    neck = (
        cq.Workplane("XY")
        .moveTo(0.0080, 0.0040)
        .lineTo(0.0080, 0.0200)
        .lineTo(0.0330, 0.0240)
        .lineTo(0.0330, 0.0060)
        .close()
        .extrude(half_t, both=True)
    )
    prof = prof.union(neck)
    return prof.cut(_lap_cutter())


def _build_jaw(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    if r.jaw_shape == "flat_box":
        jaw = _box_jaw_solid(r)
    elif r.jaw_shape == "vgroove":
        jaw = _vgroove_jaw_solid(r)
    elif r.jaw_shape == "hollow_bit":
        jaw = _bit_jaw_solid(r)
    elif r.jaw_shape == "ring_bow":
        jaw = _ring_half_solid(r)
    elif r.jaw_shape == "pincer_claw":
        jaw = _claw_jaw_solid(r)
    else:  # wolf_flat
        jaw = _wolf_jaw_solid(r)
    # Independent jaw width (Y) / length (X) scaling. ring/claw already carry
    # their identity geometry; scale them gently too (kept in-plane only).
    return _scale_xy(jaw, r.jaw_length_scale, r.jaw_width_scale)


# ---------------------------------------------------------------------------
# Boss mesh helpers (Slot C).
# ---------------------------------------------------------------------------
def _countersink_cutter(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    z_inner = BOSS_PLATE_T - HEAD_DEPTH
    z_surface = BOSS_PLATE_T + 0.0005
    return (
        cq.Workplane("XZ")
        .moveTo(0.0, z_inner)
        .lineTo(r.rivet_shaft_r, z_inner)
        .lineTo(r.flush_head_r, z_surface)
        .lineTo(0.0, z_surface)
        .close()
        .revolve(360, (0, 0), (0, 1))
    )


def _boss_solid(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    boss = cq.Workplane("XY").ellipse(r.boss_a, r.boss_b).extrude(BOSS_PLATE_T)
    for dx, dy in BOSS_DIMPLES:
        boss = boss.cut(_dimple(dx, dy, BOSS_PLATE_T, +1))
    if r.boss_rivet == "countersunk_flush":
        boss = boss.cut(_countersink_cutter(r))
    boss = boss.cut(_lap_cutter())
    if r.boss_rivet == "raised_boss_collar":
        collar_bore_r = r.rivet_shaft_r + 0.0003
        collar = (
            cq.Workplane("XY")
            .workplane(offset=BOSS_PLATE_T)
            .circle(r.collar_r)
            .circle(collar_bore_r)
            .extrude(r.collar_h)
        )
        boss = boss.union(collar)
    return boss


# ---------------------------------------------------------------------------
# Rivet mesh helpers (Slot C).
# ---------------------------------------------------------------------------
def _rivet_solid(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    if r.boss_rivet == "countersunk_flush":
        # Flush conical heads peened into the boss countersinks.
        sr = r.rivet_shaft_r
        fr = r.flush_head_r
        hd = HEAD_DEPTH
        bt = BOSS_PLATE_T
        return (
            cq.Workplane("XZ")
            .moveTo(0.0, -bt)
            .lineTo(fr, -bt)
            .lineTo(sr, -bt + hd)
            .lineTo(sr, bt - hd)
            .lineTo(fr, bt)
            .lineTo(0.0, bt)
            .close()
            .revolve(360, (0, 0), (0, 1))
        )
    if r.boss_rivet == "raised_boss_collar":
        # Shaft spans both boss plates + collars; heads seat on collar outer face.
        head_z = BOSS_PLATE_T + r.collar_h
        shaft_half = head_z + 0.0002
        shaft = (
            cq.Workplane("XY")
            .workplane(offset=-shaft_half)
            .circle(r.rivet_shaft_r)
            .extrude(2.0 * shaft_half)
        )
        head_top = cq.Workplane("XY", origin=(0.0, 0.0, head_z)).sphere(r.rivet_head_r)
        head_bot = cq.Workplane("XY", origin=(0.0, 0.0, -head_z)).sphere(r.rivet_head_r)
        return shaft.union(head_top).union(head_bot)
    # flat_boss_domed (baseline): cylinder shaft + two domed sphere heads, proud.
    shaft = (
        cq.Workplane("XY")
        .workplane(offset=-0.0046)
        .circle(r.rivet_shaft_r)
        .extrude(0.0092)
    )
    head_top = cq.Workplane("XY", origin=(0.0, 0.0, 0.0022)).sphere(r.rivet_head_r)
    head_bot = cq.Workplane("XY", origin=(0.0, 0.0, -0.0022)).sphere(r.rivet_head_r)
    return shaft.union(head_top).union(head_bot)


# ---------------------------------------------------------------------------
# Rein / handle mesh helpers (Slot B).
# ---------------------------------------------------------------------------
def _rein_sections(r: ResolvedBlacksmithTongsConfig):
    """Superellipse stations with the splay (Y) and length (X) scaled."""
    out = []
    for x, yc, hw, hh, n_exp in REIN_SECTIONS_BASE:
        out.append((x * r.rein_length_scale, yc * r.splay_scale, hw, hh, n_exp))
    return out


def _rein_tip_xy(r: ResolvedBlacksmithTongsConfig) -> tuple[float, float]:
    return (REIN_TIP_X * r.rein_length_scale, REIN_TIP_Y * r.splay_scale)


def _rein_loft(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    wires: list[cq.Wire] = []
    for x, yc, hw, hh, n_exp in _rein_sections(r):
        pts: list[cq.Vector] = []
        for i in range(REIN_SECTION_PTS):
            t = 2.0 * math.pi * i / REIN_SECTION_PTS
            c, s = math.cos(t), math.sin(t)
            dy = hw * math.copysign(abs(c) ** (2.0 / n_exp), c)
            dz = hh * math.copysign(abs(s) ** (2.0 / n_exp), s)
            pts.append(cq.Vector(x, yc + dy, dz))
        pts.append(pts[0])
        wires.append(cq.Wire.makePolygon(pts))
    return cq.Workplane(obj=cq.Solid.makeLoft(wires))


def _square_bar_loft(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    hw = REIN_BAR_HALF
    wires: list[cq.Wire] = []
    for x, yc, _hwid, _hht, _n in _rein_sections(r):
        pts = [
            cq.Vector(x, yc - hw, -hw),
            cq.Vector(x, yc + hw, -hw),
            cq.Vector(x, yc + hw, hw),
            cq.Vector(x, yc - hw, hw),
            cq.Vector(x, yc - hw, -hw),
        ]
        wires.append(cq.Wire.makePolygon(pts))
    return cq.Workplane(obj=cq.Solid.makeLoft(wires))


def _scroll_solid(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    tip_x, tip_y = _rein_tip_xy(r)
    cx = tip_x + r.scroll_outer_r
    cy = tip_y
    bar_r0 = REIN_TIP_R * 0.92
    bar_r1 = REIN_TIP_R * 0.40
    loft_wires: list[cq.Wire] = []
    for i in range(SCROLL_SECTIONS + 1):
        t = i / SCROLL_SECTIONS
        angle = math.pi + t * r.scroll_turns * 2.0 * math.pi
        rad = r.scroll_outer_r - t * (r.scroll_outer_r - SCROLL_INNER_R)
        x = cx + rad * math.cos(angle)
        y = cy + rad * math.sin(angle)
        bar_r = bar_r0 + t * (bar_r1 - bar_r0)
        dt = 1.0e-4
        if t < 1.0 - dt:
            t2 = t + dt
            sign = 1.0
        else:
            t2 = t - dt
            sign = -1.0
        a2 = math.pi + t2 * r.scroll_turns * 2.0 * math.pi
        r2 = r.scroll_outer_r - t2 * (r.scroll_outer_r - SCROLL_INNER_R)
        x2 = cx + r2 * math.cos(a2)
        y2 = cy + r2 * math.sin(a2)
        tx = sign * (x2 - x)
        ty = sign * (y2 - y)
        tlen = math.sqrt(tx * tx + ty * ty)
        if tlen > 1.0e-12:
            tx /= tlen
            ty /= tlen
        nx, ny = -ty, tx
        pts: list[cq.Vector] = []
        for j in range(SCROLL_CIRCLE_N):
            a = 2.0 * math.pi * j / SCROLL_CIRCLE_N
            ca, sa = math.cos(a), math.sin(a)
            px = x + bar_r * ca * nx
            py = y + bar_r * ca * ny
            pz = bar_r * sa
            pts.append(cq.Vector(px, py, pz))
        pts.append(pts[0])
        loft_wires.append(cq.Wire.makePolygon(pts))
    scroll = cq.Workplane(obj=cq.Solid.makeLoft(loft_wires))
    scroll = scroll.union(cq.Workplane("XY", origin=(tip_x, tip_y, 0.0)).sphere(bar_r0))
    angle_end = math.pi + r.scroll_turns * 2.0 * math.pi
    end_x = cx + SCROLL_INNER_R * math.cos(angle_end)
    end_y = cy + SCROLL_INNER_R * math.sin(angle_end)
    scroll = scroll.union(cq.Workplane("XY", origin=(end_x, end_y, 0.0)).sphere(bar_r1))
    return scroll


def _eye_loop_solid(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    from cadquery.func import circle as cq_circle
    from cadquery.func import face, revolve

    tip_x, tip_y = _rein_tip_xy(r)
    cx = tip_x - r.eye_loop_r
    cy = tip_y
    disk = face(cq_circle(EYE_TUBE_R))
    cross_section = disk.moved(rx=90, x=r.eye_loop_r)
    torus_shape = revolve(cross_section, (0, 0, 0), (0, 0, 1), 360)
    torus = cq.Workplane(obj=torus_shape).translate((cx, cy, 0.0))
    blend = (
        cq.Workplane("XY", origin=(tip_x, tip_y, 0.0)).sphere(EYE_TUBE_R * 1.15)
    )
    return torus.union(blend)


# Base Y offset that keeps the whole short handle on its own (-Y) side: its
# root half-width is ~0.010, so the root center must sit clear of the
# centerline (the flipped moving handle mirrors to +Y).
HANDLE_BASE_Y = -0.013


def _handle_solid(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    """Short stout bowed handle (rebased from pincers), running along -X.

    Sections are (x_along, y_bow, width_y, thick_z) lofted from the boss out to
    the worn tip in the YZ plane: width is in Y, thickness in Z; the bow plus a
    base offset put the center on the -Y side so the flipped moving handle
    mirrors cleanly to +Y without crossing the centerline. Length scaled by
    rein_length_scale; the lateral bow + base offset scale with the splay."""
    wires: list[cq.Wire] = []
    for x_local, y_bow, w, t in HANDLE_SECTIONS:
        x = x_local * r.rein_length_scale
        yc = (HANDLE_BASE_Y - y_bow) * r.splay_scale
        hw = w / 2.0
        ht = t / 2.0
        pts = [
            cq.Vector(x, yc - hw, -ht),
            cq.Vector(x, yc + hw, -ht),
            cq.Vector(x, yc + hw, ht),
            cq.Vector(x, yc - hw, ht),
            cq.Vector(x, yc - hw, -ht),
        ]
        wires.append(cq.Wire.makePolygon(pts))
    handle = cq.Workplane(obj=cq.Solid.makeLoft(wires))
    tx, ty = HANDLE_TIP_C
    tip = cq.Workplane(
        "XY",
        origin=(tx * r.rein_length_scale, (HANDLE_BASE_Y - ty) * r.splay_scale, 0.0),
    ).sphere(HANDLE_TIP_R)
    # Not lap-cut: the handle stays on its own (-Y) side via HANDLE_BASE_Y, so it
    # never collides with the mirrored moving handle; its root laps the opposite
    # boss (declared via allow_overlap(rein, boss)).
    return _robust_union(handle, tip)


def _build_rein(r: ResolvedBlacksmithTongsConfig) -> cq.Workplane:
    if r.rein_form == "short_stout_handle":
        return _handle_solid(r)
    # The rein is NOT lap-cut: the two reins are kept apart in Y by the splay,
    # so they never collide, and the rein root forged continuous with the boss
    # laps the opposite boss (declared via allow_overlap(rein, boss)). Cutting
    # the rein with the tall lap cylinder produced fragile OCC booleans (stray
    # cutter slivers), which the lap allowances make unnecessary.
    if r.rein_form == "square_bar":
        return _square_bar_loft(r)
    rein = _rein_loft(r)
    if r.rein_form == "scrolled":
        rein = _robust_union(rein, _scroll_solid(r))
    elif r.rein_form == "looped_eye":
        rein = _robust_union(rein, _eye_loop_solid(r))
    else:  # long_straight
        tip_x, tip_y = _rein_tip_xy(r)
        rein = _robust_union(
            rein, cq.Workplane("XY", origin=(tip_x, tip_y, 0.0)).sphere(REIN_TIP_R)
        )
    return rein


def _robust_union(a: cq.Workplane, b: cq.Workplane) -> cq.Workplane:
    """Union two forged-continuous pieces (rein body + scroll / eye / tip ball).

    Some barely-touching loft/torus pairs make the OCC fuse drop a piece (it
    returns a shape with only one input's volume, or a null shape). When the
    fuse is not at least as big as the larger input, fall back to a compound
    (the pieces still read as one continuous forging and the mesh exporter
    handles the compound) so the build never loses the rein body."""
    av = a.val()
    bv = b.val()
    try:
        va = av.Volume()
        vb = bv.Volume()
    except Exception:
        va = vb = 0.0
    need = max(va, vb) - 1e-9
    try:
        fused = av.fuse(bv)
        if fused is not None and not fused.isNull() and fused.Volume() >= need:
            return cq.Workplane(obj=fused)
    except Exception:
        pass
    comp = cq.Compound.makeCompound([av, bv])
    return cq.Workplane(obj=comp)


# ---------------------------------------------------------------------------
# Placement + part emission
# ---------------------------------------------------------------------------
def _place(solid: cq.Workplane, *, flipped: bool, z_lift: float, skip_lift: bool) -> cq.Workplane:
    """Lift into the lying-flat pose. The moving (child) half is the identical
    forging flipped 180° about X (jaw/rein swap sides, lap faces oppose). The
    fixed (root) arm bakes z_lift into its mesh; the moving arm stays at z=0 in
    the child frame (the articulation origin already provides z_lift)."""
    if flipped:
        solid = solid.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 180.0)
    if not skip_lift:
        solid = solid.translate((0.0, 0.0, z_lift))
    return solid


def _arm_inertial(r: ResolvedBlacksmithTongsConfig, z: float) -> Inertial:
    return Inertial.from_geometry(
        Box((0.55, 0.10, 0.03)),
        mass=0.4,
        origin=Origin(xyz=(-0.18, 0.0, z)),
    )


def _emit_arm(
    model: ArticulatedObject,
    r: ResolvedBlacksmithTongsConfig,
    mats,
    *,
    i: int,
    arm_name: str,
    flipped: bool,
    assets,
):
    """Emit one arm (jaw + boss + rein + (fixed only) rivet). i=0 fixed/root
    bakes z_lift; i=1 moving/child stays in the child frame."""
    skip_lift = flipped  # the moving (flipped) arm is the child
    arm = model.part(arm_name)
    arm.visual(
        mesh_from_cadquery(
            _place(_build_jaw(r), flipped=flipped, z_lift=r.z_lift, skip_lift=skip_lift),
            f"jaw_{i}",
            assets=assets,
            tolerance=0.00015,
        ),
        name="jaw", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_forged", "polished_highlight", "browned_blued", "bright_bare_steel", "aged_pewter"} else "rust.oxidized_metal"),
        material=mats["jaw"],
    )
    arm.visual(
        mesh_from_cadquery(
            _place(_boss_solid(r), flipped=flipped, z_lift=r.z_lift, skip_lift=skip_lift),
            f"boss_{i}",
            assets=assets,
            tolerance=0.00015,
        ),
        name="boss", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_forged", "polished_highlight", "browned_blued", "bright_bare_steel", "aged_pewter"} else "rust.oxidized_metal"),
        material=mats["boss"],
    )
    arm.visual(
        mesh_from_cadquery(
            _place(_build_rein(r), flipped=flipped, z_lift=r.z_lift, skip_lift=skip_lift),
            f"rein_{i}",
            assets=assets,
            tolerance=0.00015,
        ),
        name="rein", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_forged", "polished_highlight", "browned_blued", "bright_bare_steel", "aged_pewter"} else "rust.oxidized_metal"),
        material=mats["body"],
    )
    if i == 0:
        # The rivet is the captured pivot pin, carried by the fixed (root) arm
        # and baked at z_lift.
        arm.visual(
            mesh_from_cadquery(
                _place(_rivet_solid(r), flipped=False, z_lift=r.z_lift, skip_lift=False),
                "rivet",
                assets=assets,
                tolerance=0.0001,
            ),
            name="rivet", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"dark_forged", "polished_highlight", "browned_blued", "bright_bare_steel", "aged_pewter"} else "rust.oxidized_metal"),
            material=mats["rivet"],
        )
    arm.inertial = _arm_inertial(r, r.z_lift if not skip_lift else 0.0)
    return arm


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_blacksmith_tongs(
    config: BlacksmithTongsConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"blacksmith_tongs_{key}_{r.palette_style}", rgba=palette[key])
        for key in ("body", "jaw", "boss", "rivet")
    }

    fixed_arm = _emit_arm(
        model, r, mats, i=0, arm_name="fixed_arm", flipped=False, assets=assets
    )
    moving_arm = _emit_arm(
        model, r, mats, i=1, arm_name="moving_arm", flipped=True, assets=assets
    )

    model.articulation(
        "rivet_pivot",
        ArticulationType.REVOLUTE,
        parent=fixed_arm,
        child=moving_arm,
        origin=Origin(xyz=(0.0, 0.0, r.z_lift)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(
            effort=80.0, velocity=2.5, lower=0.0, upper=r.pivot_upper
        ),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_blacksmith_tongs(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_blacksmith_tongs(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_blacksmith_tongs_tests(
    object_model: ArticulatedObject,
    config: BlacksmithTongsConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    fixed_arm = object_model.get_part("fixed_arm")
    moving_arm = object_model.get_part("moving_arm")
    pivot = object_model.get_articulation("rivet_pivot")

    # ---- Captured pivot pin: the rivet passes through the moving boss. ----
    if r.boss_rivet == "countersunk_flush":
        reason = (
            "The flush countersunk rivet is the captured pivot pin; its shaft "
            "and conical heads intentionally pass through the moving arm boss."
        )
    elif r.boss_rivet == "raised_boss_collar":
        reason = (
            "The round-head rivet is the captured pivot pin passing through "
            "both raised boss collars and the half-lapped boss plates."
        )
    else:
        reason = (
            "The round-head rivet is the captured pivot pin and intentionally "
            "passes through the moving arm boss plate."
        )
    ctx.allow_overlap(
        fixed_arm, moving_arm, elem_a="rivet", elem_b="boss", reason=reason
    )
    # The two arms half-lap at the boss: each arm's boss plate (and the rein root
    # forged continuous out of it) rides in the lap layer against the other arm's
    # boss. This boss/rein-root lap is the captured contact that the single rivet
    # clamps; declare it both ways so the lapped roots are justified.
    _lap_reason = (
        "The two forged arms half-lap at the boss; each arm's boss plate and the "
        "jaw / rein roots forged continuous with it ride in the lap layer against "
        "the other arm's boss, clamped by the captured rivet."
    )
    for ea, eb in (("rein", "boss"), ("boss", "rein"), ("jaw", "boss"), ("boss", "jaw")):
        ctx.allow_overlap(
            fixed_arm, moving_arm, elem_a=ea, elem_b=eb, reason=_lap_reason
        )
    if r.boss_rivet == "raised_boss_collar":
        # The taller collar rivet's heads reach across the boss-center lap plane
        # where the moving arm's rein is forged continuous out of its boss; the
        # captured pin legitimately passes through that lapped rein root too.
        ctx.allow_overlap(
            fixed_arm, moving_arm, elem_a="rivet", elem_b="rein",
            reason=(
                "The raised-collar rivet is the captured pivot pin; its heads "
                "pass through the moving arm boss and the rein root forged "
                "continuous with it at the boss-center lap plane."
            ),
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- Single root + the single shared REVOLUTE pivot. ----
    roots = object_model.root_parts()
    ctx.check(
        "fixed_arm is the single root",
        len(roots) == 1 and roots[0].name == "fixed_arm",
        details=f"roots={[p.name for p in roots]}",
    )
    arts = list(object_model.articulations)
    ctx.check(
        "exactly one articulation (rivet_pivot)",
        len(arts) == 1 and arts[0].name == "rivet_pivot",
        details=str([a.name for a in arts]),
    )
    ax = pivot.axis
    ctx.check(
        "rivet_pivot is REVOLUTE about the tool-plane normal (Z)",
        pivot.articulation_type == ArticulationType.REVOLUTE
        and abs(ax[2]) > 0.99
        and abs(ax[0]) < 0.02
        and abs(ax[1]) < 0.02,
        details=f"type={pivot.articulation_type} axis={tuple(ax)}",
    )
    limits = pivot.motion_limits
    ctx.check(
        "rivet_pivot rest at q=0 (closed), opens to a positive upper",
        limits is not None
        and limits.lower is not None
        and limits.upper is not None
        and abs(limits.lower) < 1e-9
        and 0.25 <= limits.upper <= 0.37,
        details=f"limits={limits}",
    )

    # ---- Two arms (fixed at 2). ----
    arm_parts = [p for p in object_model.parts if p.name in ("fixed_arm", "moving_arm")]
    ctx.check("exactly two arms", len(arm_parts) == 2, details=str([p.name for p in arm_parts]))

    # ---- Rivet seated, centered in the boss footprint. ----
    ctx.expect_within(
        fixed_arm, moving_arm, axes="xy",
        inner_elem="rivet", outer_elem="boss", margin=0.0005,
        name="rivet centered inside the boss footprint",
    )
    riv = ctx.part_element_world_aabb(fixed_arm, elem="rivet")
    boss_f = ctx.part_element_world_aabb(fixed_arm, elem="boss")
    boss_m = ctx.part_element_world_aabb(moving_arm, elem="boss")

    # ---- Rivet head: proud (domed/collar) vs flush (countersunk). ----
    if r.boss_rivet == "countersunk_flush":
        ctx.check(
            "rivet top flush with the upper boss face",
            riv is not None and boss_f is not None and abs(riv[1][2] - boss_f[1][2]) < 0.0012,
            details=f"rivet={riv}, fixed_boss={boss_f}",
        )
        ctx.check(
            "rivet bottom flush with the lower boss face",
            riv is not None and boss_m is not None and abs(riv[0][2] - boss_m[0][2]) < 0.0012,
            details=f"rivet={riv}, moving_boss={boss_m}",
        )
    else:
        ctx.check(
            "rivet head proud of the upper boss face",
            riv is not None and boss_f is not None and riv[1][2] > boss_f[1][2] + 0.0015,
            details=f"rivet={riv}, fixed_boss={boss_f}",
        )
        ctx.check(
            "rivet head proud of the lower boss face",
            riv is not None and boss_m is not None and riv[0][2] < boss_m[0][2] - 0.0015,
            details=f"rivet={riv}, moving_boss={boss_m}",
        )

    # ---- raised_boss_collar: each boss is taller than the plate alone. ----
    if r.boss_rivet == "raised_boss_collar":
        boss_f_z = (boss_f[1][2] - boss_f[0][2]) if boss_f else 0.0
        boss_m_z = (boss_m[1][2] - boss_m[0][2]) if boss_m else 0.0
        ctx.check(
            "both boss collars raise the plate (z-extent > plate alone)",
            boss_f is not None and boss_m is not None and boss_f_z > 0.006 and boss_m_z > 0.006,
            details=f"fixed_boss_z={boss_f_z:.4f}, moving_boss_z={boss_m_z:.4f}",
        )
        ctx.check(
            "both boss collars are symmetric in height",
            boss_f is not None and boss_m is not None and abs(boss_f_z - boss_m_z) < 0.0015,
            details=f"fixed_z={boss_f_z:.4f}, moving_z={boss_m_z:.4f}",
        )

    # ---- Boss is a flattened ellipse roughly 0.035 m across. ----
    if boss_f is not None:
        bw = boss_f[1][0] - boss_f[0][0]
        bh = boss_f[1][1] - boss_f[0][1]
        ctx.check(
            "boss roughly 0.035 m across",
            0.026 <= bw <= 0.050 and 0.024 <= bh <= 0.044,
            details=f"boss_w={bw:.4f}, boss_h={bh:.4f}",
        )

    # ---- Overall proportions: lying flat in one plane. ----
    fa = ctx.part_world_aabb(fixed_arm)
    ma = ctx.part_world_aabb(moving_arm)
    if fa is not None and ma is not None:
        length = max(fa[1][0], ma[1][0]) - min(fa[0][0], ma[0][0])
        if r.rein_form == "short_stout_handle":
            ctx.check("overall length about 0.30 m (short handle)", 0.22 <= length <= 0.40, details=f"length={length:.4f}")
        else:
            ctx.check("overall length about 0.55 m", 0.45 <= length <= 0.65, details=f"length={length:.4f}")
        z_extent = max(fa[1][2], ma[1][2]) - min(fa[0][2], ma[0][2])
        ctx.check("tool lies flat in one plane", z_extent <= 0.032, details=f"z_extent={z_extent:.4f}")
        ctx.check(
            "tongs rest just above the ground plane",
            min(fa[0][2], ma[0][2]) >= -0.001,
            details=f"min_z={min(fa[0][2], ma[0][2]):.5f}",
        )

    # ---- Jaws run side by side along the jaw end. ----
    ctx.expect_overlap(
        fixed_arm, moving_arm, axes="x",
        elem_a="jaw", elem_b="jaw", min_overlap=0.04,
        name="the two jaws run side by side along the jaw end",
    )

    # ---- Per-jaw closed-pose contact semantics (q=0). ----
    if r.jaw_shape == "ring_bow":
        # The two half-rings lap at the far apex, forming one closed oval bow.
        ctx.expect_overlap(
            fixed_arm, moving_arm, axes="x",
            elem_a="jaw", elem_b="jaw", min_overlap=0.02,
            name="the two half-rings close into one oval bow loop",
        )
        jf = ctx.part_element_world_aabb(fixed_arm, elem="jaw")
        if jf is not None:
            ring_along = jf[1][0] - jf[0][0]
            ctx.check(
                "ring bow extends well past the boss (large open loop)",
                ring_along > 0.06,
                details=f"ring_along_x={ring_along:.4f}",
            )
    elif r.jaw_shape == "pincer_claw":
        # Bite edges nearly meet; the jaw backs keep a visible throat.
        ctx.expect_gap(
            fixed_arm, moving_arm, axis="y",
            positive_elem="jaw", negative_elem="jaw",
            min_gap=-0.001, max_gap=0.006,
            name="closed claw bite edges nearly meet at the centerline",
        )
    elif r.jaw_shape == "vgroove":
        ctx.expect_gap(
            fixed_arm, moving_arm, axis="y",
            positive_elem="jaw", negative_elem="jaw",
            min_gap=-0.0015, max_gap=0.006,
            name="closed V-groove jaw lips nearly meet (diamond socket)",
        )
        jf = ctx.part_element_world_aabb(fixed_arm, elem="jaw")
        if jf is not None:
            ctx.check(
                "V-groove is on the Y face (jaw Z-extent ~ bar thickness)",
                abs((jf[1][2] - jf[0][2]) - r.jaw_t) < 0.0025,
                details=f"jaw_z={(jf[1][2]-jf[0][2]):.4f}, jaw_t={r.jaw_t:.4f}",
            )
    elif r.jaw_shape == "hollow_bit":
        ctx.expect_gap(
            fixed_arm, moving_arm, axis="y",
            positive_elem="jaw", negative_elem="jaw",
            min_gap=0.0001, max_gap=0.005,
            name="closed concave bit jaws keep a small bore-channel gap",
        )
        jf = ctx.part_element_world_aabb(fixed_arm, elem="jaw")
        if jf is not None:
            ctx.check(
                "bore diameter fits within the jaw thickness",
                (jf[1][2] - jf[0][2]) > 2.0 * r.bore_r + 0.0002,
                details=f"jaw_z={(jf[1][2]-jf[0][2]):.5f}, bore_d={2.0*r.bore_r:.4f}",
            )
    elif r.jaw_shape == "flat_box":
        ctx.expect_gap(
            fixed_arm, moving_arm, axis="y",
            positive_elem="jaw", negative_elem="jaw",
            min_gap=0.0005, max_gap=0.005,
            name="closed flat box jaws present parallel faces with a small gap",
        )
    else:  # wolf_flat
        ctx.expect_gap(
            fixed_arm, moving_arm, axis="y",
            positive_elem="jaw", negative_elem="jaw",
            min_gap=0.0003, max_gap=0.005,
            name="closed wolf jaws nearly meet at the tip (narrow V notch)",
        )

    # ---- Reins / handle: long and splayed (or short bowed handle). ----
    rein_f = ctx.part_element_world_aabb(fixed_arm, elem="rein")
    rein_m = ctx.part_element_world_aabb(moving_arm, elem="rein")
    if r.rein_form == "short_stout_handle":
        ctx.check(
            "handles are short and splay to opposite sides",
            rein_f is not None and rein_m is not None
            and rein_f[0][1] < -0.018 and rein_m[1][1] > 0.018,
            details=f"fixed_rein={rein_f}, moving_rein={rein_m}",
        )
    else:
        ctx.check(
            "reins run long from the boss",
            rein_f is not None and 0.34 <= (rein_f[1][0] - rein_f[0][0]) <= 0.55,
            details=f"fixed_rein={rein_f}",
        )
        ctx.check(
            "rein tips splay to opposite sides",
            rein_f is not None and rein_m is not None
            and rein_f[0][1] < -0.025 and rein_m[1][1] > 0.025,
            details=f"fixed_rein={rein_f}, moving_rein={rein_m}",
        )

    # ---- Per-rein tip-form identity. ----
    if r.rein_form == "scrolled":
        # The flat scroll volute reaches outward in Y beyond the plain splayed
        # tip (compared relative to the splayed tip so it holds at any scale).
        _, plain_tip_y = _rein_tip_xy(r)
        ctx.check(
            "rein tips end in forged scrolls beyond the bare splay",
            rein_f is not None and rein_m is not None
            and rein_f[0][1] < plain_tip_y - 0.004 and rein_m[1][1] > -plain_tip_y + 0.004,
            details=(
                f"fixed_min_y={rein_f[0][1] if rein_f else None}, "
                f"moving_max_y={rein_m[1][1] if rein_m else None}, plain_tip_y={plain_tip_y:.4f}"
            ),
        )
    elif r.rein_form == "looped_eye":
        tip_x, _ = _rein_tip_xy(r)
        ctx.check(
            "rein tips end in eye loops extending beyond the bare tip",
            rein_f is not None and rein_m is not None
            and rein_f[0][0] < tip_x - 0.006 and rein_m[0][0] < tip_x - 0.006,
            details=f"fixed_min_x={rein_f[0][0] if rein_f else None}, tip_x={tip_x:.4f}",
        )
    elif r.rein_form == "square_bar":
        ctx.check(
            "rein is a chunky constant square bar (no taper to round)",
            rein_f is not None and (rein_f[1][2] - rein_f[0][2]) >= 0.011,
            details=f"fixed_rein_z={rein_f[1][2]-rein_f[0][2]:.4f}" if rein_f else "missing",
        )

    # ---- Open pose: jaws open + moving rein swings away. ----
    rein_m_rest_max_y = rein_m[1][1] if rein_m is not None else None
    with ctx.pose({pivot: pivot.motion_limits.upper}):
        ctx.expect_gap(
            fixed_arm, moving_arm, axis="y",
            positive_elem="jaw", negative_elem="jaw",
            min_gap=0.003,
            name="jaws open apart at full pivot travel",
        )
        rein_m_open = ctx.part_element_world_aabb(moving_arm, elem="rein")
        # The short stout handle (~0.22 m) swings ~0.048 m at the lowest travel
        # (vs ~0.10 m for the long ~0.46 m reins); both are decisive, readable
        # swings, so the threshold tracks the handle/rein length class.
        swing = 0.04 if r.rein_form == "short_stout_handle" else 0.07
        ctx.check(
            "moving rein swings away from the fixed rein",
            rein_m_open is not None and rein_m_rest_max_y is not None
            and rein_m_open[1][1] > rein_m_rest_max_y + swing,
            details=f"rest_max_y={rein_m_rest_max_y}, open={rein_m_open}",
        )

    return ctx.report()


__all__ = (
    "BlacksmithTongsConfig",
    "ResolvedBlacksmithTongsConfig",
    "build_blacksmith_tongs",
    "build_seeded_blacksmith_tongs",
    "config_from_seed",
    "resolve_config",
    "run_blacksmith_tongs_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
