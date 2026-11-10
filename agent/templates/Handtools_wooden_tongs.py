# SPDX-License-Identifier: Apache-2.0

"""One-piece sprung wooden serving / cooking tongs — modular template.

NOTE on the slug name: "wooden_tongs" here = a **sprung wooden serving /
cooking tong** (two long flat/round wooden arms that splay into a relaxed open
"V" and pinch shut about a pivot to grip food), NOT a screw-driven hand clamp
(that is the separate ``clamp`` slug), NOT pliers / scissors (metal cutting
tools), and NOT chopsticks (two un-hinged sticks with no closing mechanism).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Handtools_Handtools_wooden_tongs.md`` and the
``picture/Handtools/wooden tongs`` 5-star sample pool (1 parent + 2 original
variants + 6 gap variants = 9), all synced under ``data/records/``.

Coordinate convention (unified across all 9 samples; template adopts it as-is):
the flat arms lie in the XY plane (flat-face normal = +Z); an arm runs along
**+X** from the pivot (x≈0) to its tip (x≈ARM_LENGTH=0.300); the two arms stack
in **±Z** at the pivot (fixed/root arm at -Z, moving arm at +Z, with a small
clearance gap); the splay half-angle ``HALF_SPLAY`` (~7-8.5°) is applied through
the visual / joint ``rpy=(0,0,±HALF_SPLAY)`` (each arm is modeled straight); the
shared ``pivot`` REVOLUTE has **axis=(0,0,1)** with q=0 = relaxed open "V" (tips
in ±Y), ``upper`` = squeezed closed, small negative q opens wider. The lock_ring
``slide`` PRISMATIC has **axis=(1,0,0)** (collar slides toward the tips to lock).

Structure (pattern = ``parallel_children``): a fixed root arm (``fixed_arm`` /
``arm_0``) with the moving arm (``moving_arm`` / ``arm_1``) hinged to it by the
shared ``pivot`` REVOLUTE; the arm count is FIXED at 2 (emitted by a shared
helper, NOT a multiplicity axis). Three named module axes:

  * ``close_mechanism`` (4): the closing hardware + pivot topology —
    onepiece_spring_clip (top metal spring clip bridging both arms, 1 REVOLUTE)
    / scissor_pin (a round pin crossing both arms partway, 1 REVOLUTE mid-cross,
    short handle + long tip on each side) / spring_clip_with_lock_ring (the
    spring clip PLUS an independent ``slide_ring`` collar on a PRISMATIC slide,
    1 REVOLUTE + 1 PRISMATIC) / onepiece_bend (a continuous bent-wood U at the
    top IS the spring — NO metal, 1 REVOLUTE). This is the real joint-topology
    axis. (parent / scissor_pin / lock_ring / onepiece_bend variants)
  * ``arm_shape`` (5): the two arms' cross-section / tip footprint —
    flat_paddle (tapered flat strip flaring to a rounded paddle) / round_dowel
    (circular section_loft dowel, ``mesh_from_geometry``) / straight_slat
    (constant-width flat rect) / spoon_ends (thicker bowl with a sphere-cut
    concave dish, ``dish_up`` so the two dishes face each other) / square_ends
    (flat paddle held full-width to a blunt square-cut tip). A mesh-profile
    dimension; it does not change the part tree or joint topology. Both arms
    share one helper. (parent / round_dowel / straight_slat / spoon_ends /
    square_ends variants)
  * ``grip_detail`` (2): the grip-section surface decoration — plain (smooth,
    perimeter fillet only) / scalloped_grip (a row of finger-scallop ridges on
    both faces of both arms). A module-internal decoration layer; the ridges are
    always arm visuals (no FIXED decoration parts; Rule 1). (parent /
    scalloped_grip variants)

The metal spring clip, scissor pin, bent-wood U, ring grip nubs, and finger
scallop ridges are all fixed arm / ring visuals (Rule 1). The clip-bridging,
pin-through-arm, bend-junction, and ring-bore-around-arm captures are all
captured/bridging geometry, so those joints omit ``MatingContract``
(grandfathered) and rely on the flat articulation-origin baseline +
element-scoped ``allow_overlap`` (mirroring each source record's run_tests
allow_overlap block).
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
    mesh_from_geometry,
    section_loft,
)

__modular__ = True

CloseMechanism = Literal[
    "onepiece_spring_clip",
    "scissor_pin",
    "spring_clip_with_lock_ring",
    "onepiece_bend",
]
ArmShape = Literal[
    "flat_paddle",
    "round_dowel",
    "straight_slat",
    "spoon_ends",
    "square_ends",
]
GripDetail = Literal["plain", "scalloped_grip"]
PaletteStyle = Literal[
    "natural_birch",
    "walnut_stained",
    "cherry_warm",
    "painted_white",
    "bamboo_blond",
    "ebony_dark",
]

CLOSE_MECHANISMS: tuple[CloseMechanism, ...] = (
    "onepiece_spring_clip",
    "scissor_pin",
    "spring_clip_with_lock_ring",
    "onepiece_bend",
)
ARM_SHAPES: tuple[ArmShape, ...] = (
    "flat_paddle",
    "round_dowel",
    "straight_slat",
    "spoon_ends",
    "square_ends",
)
GRIP_DETAILS: tuple[GripDetail, ...] = ("plain", "scalloped_grip")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "natural_birch",
    "walnut_stained",
    "cherry_warm",
    "painted_white",
    "bamboo_blond",
    "ebony_dark",
)

# ---------------------------------------------------------------------------
# Per-seed palettes (spec §7). Keys: wood (fixed arm), wood_dark (moving arm),
# metal (clip / pin), ring (lock-ring collar + grip nubs). onepiece_bend uses
# NO metal material (spec: bent-wood design has no metal); the build only
# registers/uses the metal material when the mechanism actually has a metal
# part. Every .visual material is driven off this dict so the swept pool is
# colorful (module_topology_diversity only counts structure).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "natural_birch": {
        "wood": (0.52, 0.36, 0.20, 1.0),
        "wood_dark": (0.42, 0.28, 0.15, 1.0),
        "metal": (0.72, 0.74, 0.78, 1.0),
        "ring": (0.62, 0.44, 0.24, 1.0),
    },
    "walnut_stained": {
        "wood": (0.40, 0.26, 0.14, 1.0),
        "wood_dark": (0.30, 0.18, 0.09, 1.0),
        "metal": (0.70, 0.72, 0.76, 1.0),
        "ring": (0.46, 0.30, 0.16, 1.0),
    },
    "cherry_warm": {
        "wood": (0.58, 0.40, 0.22, 1.0),
        "wood_dark": (0.46, 0.30, 0.16, 1.0),
        "metal": (0.72, 0.74, 0.78, 1.0),
        "ring": (0.60, 0.42, 0.24, 1.0),
    },
    "painted_white": {
        "wood": (0.90, 0.89, 0.86, 1.0),
        "wood_dark": (0.82, 0.80, 0.76, 1.0),
        "metal": (0.82, 0.84, 0.86, 1.0),
        "ring": (0.88, 0.87, 0.84, 1.0),
    },
    "bamboo_blond": {
        "wood": (0.78, 0.68, 0.45, 1.0),
        "wood_dark": (0.68, 0.56, 0.36, 1.0),
        "metal": (0.72, 0.74, 0.78, 1.0),
        "ring": (0.80, 0.70, 0.48, 1.0),
    },
    "ebony_dark": {
        "wood": (0.16, 0.13, 0.11, 1.0),
        "wood_dark": (0.10, 0.08, 0.07, 1.0),
        "metal": (0.20, 0.20, 0.22, 1.0),
        "ring": (0.18, 0.15, 0.13, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), unified A-family convention.
# A small serving tong: arms ~0.30 m long, flat strips ~4.5 mm thick. Mechanical
# fits (stack clearance, pin radius, clip bridge) are never scaled; arm
# length / width / splay / travel ARE scaled.
# ---------------------------------------------------------------------------
ARM_LENGTH = 0.300          # pivot to paddle tip, along the arm centerline (X)
ARM_THICKNESS = 0.0045      # flat strip thickness (Z)
ROOT_WIDTH = 0.012          # narrow strip width at the pivot end
MID_WIDTH = 0.020           # widest part of the shaft
TIP_WIDTH = 0.030           # rounded paddle tip width
TIP_LENGTH = 0.045          # length of the wider paddle section
SLAT_WIDTH = 0.022          # constant width for straight_slat
HALF_SPLAY = math.radians(8.5)  # rest open-V half angle (per arm)

# Metal spring clip (onepiece_spring_clip / lock_ring).
CLIP_LEN = 0.022            # along the arms (X)
CLIP_WIDTH = 0.014          # across (Y)

# Scissor pin (scissor_pin).
HANDLE_LENGTH = 0.110       # pivot to handle end (short, -X side)
TIP_REACH = 0.190           # pivot to tip end (long, +X side); sum ~0.300
SCISSOR_THICK = 0.005       # scissor arm strip thickness
SCISSOR_HANDLE_W = 0.025
SCISSOR_PIVOT_W = 0.016
SCISSOR_TIP_W = 0.028
PIN_RADIUS = 0.004
PIN_EXTRA = 0.002

# Bent-wood U (onepiece_bend).
BEND_RADIUS = 0.012

# Round dowel (round_dowel) radii at key stations.
DOWEL_ROOT_R = 0.005
DOWEL_SHAFT_R = 0.006
DOWEL_TIP_R = 0.008

# Spoon bowl (spoon_ends).
BOWL_LENGTH = 0.052
BOWL_WIDTH = 0.040
BOWL_THICK = 0.008
DISH_RADIUS = 0.024
DISH_DEPTH = 0.004

# Lock ring (spring_clip_with_lock_ring) collar.
RING_BORE_Y = 0.030
RING_BORE_Z = 0.016
RING_OUTER_Y = 0.046
RING_OUTER_Z = 0.032
RING_LENGTH = 0.015
RING_REST_X = 0.040
RING_TRAVEL = 0.100
N_GRIPS = 4

# Scalloped grip (scalloped_grip).
SCALLOP_SPACING = 0.016
GRIP_START_X = 0.085
RIDGE_R = 0.0020
RIDGE_W = MID_WIDTH * 0.72

# Pivot travel baselines per mechanism (spec §participate: scissor 0.28, others 0.18).
_PIVOT_UPPER_SPRING = 0.18
_PIVOT_UPPER_SCISSOR = 0.28
_PIVOT_LOWER_SPRING = -0.04
_PIVOT_LOWER_SCISSOR = -0.05


@dataclass(frozen=True)
class WoodenTongsConfig:
    close_mechanism: CloseMechanism | None = None
    arm_shape: ArmShape | None = None
    grip_detail: GripDetail | None = None
    palette_style: PaletteStyle = "natural_birch"
    arm_length_scale: float = 1.0
    arm_width_scale: float = 1.0
    arm_thickness_scale: float = 1.0
    splay_angle_scale: float = 1.0
    pivot_close_scale: float = 1.0
    dowel_radius_scale: float = 1.0
    bowl_dish_scale: float = 1.0
    ring_travel_scale: float = 1.0
    scallop_count: int = 6
    scallop_spacing_scale: float = 1.0
    name: str = "wooden_tongs"


@dataclass(frozen=True)
class ResolvedWoodenTongsConfig:
    close_mechanism: CloseMechanism
    arm_shape: ArmShape
    grip_detail: GripDetail
    palette_style: PaletteStyle
    # Scaled / derived geometry.
    arm_length: float
    arm_thickness: float
    root_width: float
    mid_width: float
    tip_width: float
    tip_length: float
    slat_width: float
    half_splay: float
    # Pivot.
    pivot_lower: float
    pivot_upper: float
    arm_stack: float        # half Z offset of each arm from the midplane
    clip_span: float        # metal clip Z extent (bridges both stacked arms)
    # Scissor.
    handle_length: float
    tip_reach: float
    scissor_handle_w: float
    scissor_pivot_w: float
    scissor_tip_w: float
    pin_height: float
    scissor_stack: float
    # Bend.
    bend_radius: float
    # Dowel.
    dowel_root_r: float
    dowel_shaft_r: float
    dowel_tip_r: float
    dowel_stack: float
    # Spoon.
    bowl_length: float
    bowl_width: float
    bowl_thick: float
    dish_radius: float
    dish_depth: float
    spoon_stack: float
    # Ring.
    ring_bore_y: float
    ring_bore_z: float
    ring_outer_y: float
    ring_outer_z: float
    ring_length: float
    ring_rest_x: float
    ring_travel: float
    # Scallop.
    scallop_count: int
    scallop_spacing: float
    grip_start_x: float
    ridge_r: float
    ridge_w: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed sampling + resolution
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> WoodenTongsConfig:
    rng = random.Random(seed)
    # 1. named slots (the topology axes).
    close_mechanism = rng.choice(CLOSE_MECHANISMS)
    arm_shape = rng.choice(ARM_SHAPES)
    grip_detail = rng.choice(GRIP_DETAILS)
    # 2. conditional params (resolved/clamped later; only active for the
    #    matching module, but always drawn so the RNG stream is stable).
    dowel_radius_scale = round(rng.uniform(0.85, 1.15), 4)
    bowl_dish_scale = round(rng.uniform(0.80, 1.15), 4)
    ring_travel_scale = round(rng.uniform(0.80, 1.10), 4)
    scallop_count = rng.randint(4, 8)
    scallop_spacing_scale = round(rng.uniform(0.85, 1.15), 4)
    # 3. independent scales.
    arm_length_scale = round(rng.uniform(0.85, 1.15), 4)
    arm_width_scale = round(rng.uniform(0.88, 1.15), 4)
    arm_thickness_scale = round(rng.uniform(0.90, 1.15), 4)
    splay_angle_scale = round(rng.uniform(0.80, 1.15), 4)
    pivot_close_scale = round(rng.uniform(0.85, 1.15), 4)
    # 4. palette (not a slot_choice).
    palette_style = rng.choice(PALETTE_STYLES)
    return WoodenTongsConfig(
        close_mechanism=close_mechanism,
        arm_shape=arm_shape,
        grip_detail=grip_detail,
        palette_style=palette_style,
        arm_length_scale=arm_length_scale,
        arm_width_scale=arm_width_scale,
        arm_thickness_scale=arm_thickness_scale,
        splay_angle_scale=splay_angle_scale,
        pivot_close_scale=pivot_close_scale,
        dowel_radius_scale=dowel_radius_scale,
        bowl_dish_scale=bowl_dish_scale,
        ring_travel_scale=ring_travel_scale,
        scallop_count=scallop_count,
        scallop_spacing_scale=scallop_spacing_scale,
        name=f"seeded_wooden_tongs_{seed}",
    )


def resolve_config(config: WoodenTongsConfig | None = None) -> ResolvedWoodenTongsConfig:
    cfg = config or WoodenTongsConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    close_mechanism = _pick(cfg.close_mechanism, CLOSE_MECHANISMS)
    arm_shape = _pick(cfg.arm_shape, ARM_SHAPES)
    grip_detail = _pick(cfg.grip_detail, GRIP_DETAILS)

    length_scale = _clamp(cfg.arm_length_scale, 0.85, 1.15)
    width_scale = _clamp(cfg.arm_width_scale, 0.88, 1.15)
    thickness_scale = _clamp(cfg.arm_thickness_scale, 0.90, 1.15)
    splay_scale = _clamp(cfg.splay_angle_scale, 0.80, 1.15)
    close_scale = _clamp(cfg.pivot_close_scale, 0.85, 1.15)
    dowel_radius_scale = _clamp(cfg.dowel_radius_scale, 0.85, 1.15)
    bowl_dish_scale = _clamp(cfg.bowl_dish_scale, 0.80, 1.15)
    ring_travel_scale = _clamp(cfg.ring_travel_scale, 0.80, 1.10)
    scallop_spacing_scale = _clamp(cfg.scallop_spacing_scale, 0.85, 1.15)

    arm_length = ARM_LENGTH * length_scale
    arm_thickness = ARM_THICKNESS * thickness_scale
    root_width = ROOT_WIDTH * width_scale
    mid_width = MID_WIDTH * width_scale
    tip_width = TIP_WIDTH * width_scale
    tip_length = TIP_LENGTH * length_scale
    slat_width = SLAT_WIDTH * width_scale
    # Keep splay readable as "open" (>= ~6 deg) so even the scissor arm (whose
    # whole-arm AABB-center Y is a weak splay signal) reads clearly as an open V.
    half_splay = max(math.radians(6.0), HALF_SPLAY * splay_scale)

    # Pivot travel: per-mechanism baseline; scale the close-travel (upper) but
    # keep it from overshooting the centerline (spec §7 constraint 1: upper
    # must not exceed ~the opposite-side splay sweep). The relaxed rest is q=0
    # at +-half_splay; closing past ~2*half_splay is enough to mate the tips,
    # so cap upper at a generous multiple while preserving the source ratios.
    if close_mechanism == "scissor_pin":
        base_upper = _PIVOT_UPPER_SCISSOR
        pivot_lower = _PIVOT_LOWER_SCISSOR
    else:
        base_upper = _PIVOT_UPPER_SPRING
        pivot_lower = _PIVOT_LOWER_SPRING
    # Closing must overshoot the rest splay so the tips truly meet, but not run
    # so far that the tips cross past the centerline grossly. Cap relative to
    # the total splay sweep (2*half_splay) with headroom.
    pivot_upper_cap = 2.4 * half_splay
    pivot_upper = _clamp(base_upper * close_scale, 1.2 * half_splay, max(pivot_upper_cap, base_upper))

    # ---- Per-shape Z stacking (so the bridging clip / bore / pin spans both) ----
    arm_stack = arm_thickness / 2.0 + 0.0010
    clip_span = 2.0 * arm_stack + arm_thickness + 0.002

    # Scissor uses its own thicker strip + crossing stack.
    scissor_stack = SCISSOR_THICK / 2.0 + 0.001
    pin_height = 2.0 * (scissor_stack + SCISSOR_THICK / 2.0) + 2.0 * PIN_EXTRA
    handle_length = HANDLE_LENGTH * length_scale
    tip_reach = TIP_REACH * length_scale
    scissor_handle_w = SCISSOR_HANDLE_W * width_scale
    scissor_pivot_w = SCISSOR_PIVOT_W * width_scale
    scissor_tip_w = SCISSOR_TIP_W * width_scale

    # Dowel: stack + clip span by dowel diameter, not flat thickness.
    dowel_root_r = DOWEL_ROOT_R * dowel_radius_scale
    dowel_shaft_r = DOWEL_SHAFT_R * dowel_radius_scale
    dowel_tip_r = DOWEL_TIP_R * dowel_radius_scale
    dowel_stack = dowel_root_r + 0.001

    # Spoon: thicker bowl → bigger stack so the clip still bridges; dish bounded
    # not to cut through the bowl floor (spec §7 constraint 5).
    bowl_thick = BOWL_THICK
    spoon_stack = bowl_thick / 2.0 + 0.0020
    dish_depth = min(DISH_DEPTH * bowl_dish_scale, bowl_thick - 0.0020)
    # Keep the dish a shallow central dimple: small enough that its spherical
    # footprint stays inside the bowl (radius capped so the cut never reaches the
    # bowl perimeter / tip, which would fragment the mesh into islands).
    dish_radius = DISH_RADIUS * (0.70 + 0.12 * bowl_dish_scale)

    # Ring: the collar's rectangular bore must lightly CONTACT both splayed arms
    # at the rest position (an oversized bore leaves the band floating → isolated
    # part). Size the bore to the actual two-arm envelope at ``ring_rest_x``
    # minus a small interference so the band walls overlap the arm surfaces
    # (mirrors the source's allow_overlap(ring_band, arm) locking semantics).
    # For round_dowel the arms stack by dowel diameter (conditional, spec §9 #1).
    if arm_shape == "round_dowel":
        ring_z_hw = dowel_shaft_r
        ring_z_stack = dowel_stack
        ring_y_hw = dowel_shaft_r
    elif arm_shape == "straight_slat":
        ring_z_hw = arm_thickness / 2.0
        ring_z_stack = arm_stack
        ring_y_hw = slat_width / 2.0
    else:  # flat_paddle / square_ends / spoon_ends share the flat shaft here
        ring_z_hw = arm_thickness / 2.0
        ring_z_stack = arm_stack
        ring_y_hw = mid_width / 2.0
    splay_y = math.sin(half_splay) * RING_REST_X
    env_y = 2.0 * (splay_y + ring_y_hw)
    env_z = 2.0 * (ring_z_stack + ring_z_hw)
    # Bore hugs the two-arm envelope with only a HAIRLINE bite (0.8mm, was 1.5mm)
    # so the band stays in real contact with the arms (fail_if_isolated_parts /
    # articulation-origin need the collar to touch the arm) while the arms no
    # longer visibly poke through the ring walls (the earlier 1.5mm bite read as
    # clip-through / 穿模).
    interference = 0.0008
    ring_bore_y = max(0.012, env_y - interference)
    ring_bore_z = max(0.008, env_z - interference)
    ring_outer_y = ring_bore_y + 0.016
    ring_outer_z = ring_bore_z + 0.016
    ring_length = RING_LENGTH
    ring_rest_x = RING_REST_X
    # Ring must not slide off the tip (spec §7 constraint 3).
    max_travel = arm_length - ring_rest_x - ring_length - 0.030
    ring_travel = min(RING_TRAVEL * ring_travel_scale, max(0.030, max_travel))

    # Scallops: keep the whole row inside the grip section (past pivot, before
    # the paddle); shrink count/spacing to fit (spec §7 constraint 6).
    grip_start_x = GRIP_START_X * length_scale
    scallop_spacing = SCALLOP_SPACING * scallop_spacing_scale
    paddle_start = arm_length - tip_length
    grip_room = max(0.0, paddle_start - 0.010 - grip_start_x)
    scallop_count = max(2, int(cfg.scallop_count))
    # If the row overruns, reduce count to fit.
    while scallop_count > 2 and (scallop_count - 1) * scallop_spacing > grip_room:
        scallop_count -= 1
    ridge_w = (mid_width * 0.72)

    return ResolvedWoodenTongsConfig(
        close_mechanism=close_mechanism,
        arm_shape=arm_shape,
        grip_detail=grip_detail,
        palette_style=palette_style,
        arm_length=arm_length,
        arm_thickness=arm_thickness,
        root_width=root_width,
        mid_width=mid_width,
        tip_width=tip_width,
        tip_length=tip_length,
        slat_width=slat_width,
        half_splay=half_splay,
        pivot_lower=pivot_lower,
        pivot_upper=pivot_upper,
        arm_stack=arm_stack,
        clip_span=clip_span,
        handle_length=handle_length,
        tip_reach=tip_reach,
        scissor_handle_w=scissor_handle_w,
        scissor_pivot_w=scissor_pivot_w,
        scissor_tip_w=scissor_tip_w,
        pin_height=pin_height,
        scissor_stack=scissor_stack,
        bend_radius=BEND_RADIUS,
        dowel_root_r=dowel_root_r,
        dowel_shaft_r=dowel_shaft_r,
        dowel_tip_r=dowel_tip_r,
        dowel_stack=dowel_stack,
        bowl_length=BOWL_LENGTH,
        bowl_width=BOWL_WIDTH,
        bowl_thick=bowl_thick,
        dish_radius=dish_radius,
        dish_depth=dish_depth,
        spoon_stack=spoon_stack,
        ring_bore_y=ring_bore_y,
        ring_bore_z=ring_bore_z,
        ring_outer_y=ring_outer_y,
        ring_outer_z=ring_outer_z,
        ring_length=ring_length,
        ring_rest_x=ring_rest_x,
        ring_travel=ring_travel,
        scallop_count=scallop_count,
        scallop_spacing=scallop_spacing,
        grip_start_x=grip_start_x,
        ridge_r=RIDGE_R,
        ridge_w=ridge_w,
        name=cfg.name or "wooden_tongs",
    )


def with_overrides(config: WoodenTongsConfig, **kwargs: object) -> WoodenTongsConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: WoodenTongsConfig | ResolvedWoodenTongsConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedWoodenTongsConfig)
        else resolve_config(config)
    )
    return (
        ("close_mechanism", r.close_mechanism),
        ("arm_shape", r.arm_shape),
        ("grip_detail", r.grip_detail),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _stack_for_shape(r: ResolvedWoodenTongsConfig, *, scissor: bool = False) -> float:
    """Per-arm Z half-offset for the active arm_shape (and scissor crossing)."""
    if scissor:
        return r.scissor_stack
    if r.arm_shape == "round_dowel":
        return r.dowel_stack
    if r.arm_shape == "spoon_ends":
        return r.spoon_stack
    return r.arm_stack


def _fixed_arm_z(r: ResolvedWoodenTongsConfig) -> float:
    """Signed Z offset applied to the FIXED arm's visual (and its scallops).

    onepiece_bend separates the two arm roots by the bend radius (the bent-wood
    U connects them across that gap), so the fixed arm sits at -bend_radius and
    the moving arm is authored at z=0 with the pivot at +bend_radius. The clip /
    ring / scissor mechanisms stack the arms tightly at ±stack instead.
    """
    if r.close_mechanism == "onepiece_bend":
        return -r.bend_radius
    return -_stack_for_shape(r, scissor=(r.close_mechanism == "scissor_pin"))


# ---------------------------------------------------------------------------
# Arm mesh helpers (Slot B). Both arms share one helper per shape. The arm is
# authored straight along +X from x=0 (pivot) to x=arm_length (tip); splay /
# stacking is applied by the part/joint frame.
# ---------------------------------------------------------------------------
def _flat_outline(r: ResolvedWoodenTongsConfig, *, square_tip: bool) -> list[tuple[float, float]]:
    """Closed top+bottom outline for the flat tapered strip (paddle / square)."""
    shaft_end = r.arm_length - r.tip_length
    end_flat = 0.0030
    half_tip = r.tip_width / 2.0
    if square_tip:
        pts = [
            (0.0, end_flat),
            (0.018, r.root_width / 2.0 + 0.0015),
            (0.090, r.mid_width / 2.0),
            (shaft_end - 0.020, r.mid_width / 2.0),
            (shaft_end, half_tip - 0.003),
            (shaft_end + 0.010, half_tip),
            (r.arm_length, half_tip),
        ]
    else:
        pts = [
            (0.0, end_flat),
            (0.018, r.root_width / 2.0 + 0.0015),
            (0.090, r.mid_width / 2.0),
            (shaft_end - 0.020, r.mid_width / 2.0),
            (shaft_end, half_tip - 0.004),
            (shaft_end + 0.012, half_tip),
            (r.arm_length - 0.016, half_tip),
            (r.arm_length - 0.004, half_tip - 0.006),
            (r.arm_length, end_flat),
        ]
    lower = [(x, -y) for (x, y) in reversed(pts)]
    return pts + lower


def _arm_solid(r: ResolvedWoodenTongsConfig, *, square_tip: bool = False) -> cq.Workplane:
    half_t = r.arm_thickness / 2.0
    outline = _flat_outline(r, square_tip=square_tip)
    arm = (
        cq.Workplane("XY")
        .polyline(outline)
        .close()
        .extrude(r.arm_thickness)
        .translate((0.0, 0.0, -half_t))
    )
    try:
        arm = arm.edges("|Z").fillet(0.0006 if square_tip else 0.0010)
    except Exception:
        pass
    return arm


def _slat_solid(r: ResolvedWoodenTongsConfig) -> cq.Workplane:
    half_t = r.arm_thickness / 2.0
    arm = (
        cq.Workplane("XY")
        .rect(r.arm_length, r.slat_width)
        .extrude(r.arm_thickness)
        .translate((r.arm_length / 2.0, 0.0, -half_t))
    )
    try:
        arm = arm.edges("|Z").fillet(0.0012)
    except Exception:
        pass
    try:
        arm = arm.edges(">X").fillet(0.0008)
    except Exception:
        pass
    return arm


def _circle_section(x: float, radius: float, segments: int = 20):
    return [
        (
            x,
            radius * math.cos(i * 2.0 * math.pi / segments),
            radius * math.sin(i * 2.0 * math.pi / segments),
        )
        for i in range(segments)
    ]


def _arm_dowel(r: ResolvedWoodenTongsConfig):
    shaft_end = r.arm_length - r.tip_length
    profile = [
        (0.0, r.dowel_root_r),
        (0.020, r.dowel_root_r + 0.001),
        (0.090, r.dowel_shaft_r),
        (shaft_end - 0.020, r.dowel_shaft_r),
        (shaft_end, r.dowel_shaft_r + 0.002),
        (shaft_end + 0.015, r.dowel_tip_r),
        (r.arm_length - 0.015, r.dowel_tip_r),
        (r.arm_length - 0.005, r.dowel_shaft_r + 0.001),
        (r.arm_length, r.dowel_root_r),
    ]
    sections = [_circle_section(x, rad) for x, rad in profile]
    return section_loft(sections)


def _arm_scoop_loft(r: ResolvedWoodenTongsConfig, *, dish_up: bool):
    """Salad-server scoop arm via ``section_loft`` (clean Python mesh path).

    Authored straight along +X from x=0 (pivot) to x=arm_length (spoon tip). The
    shaft is a thin flat rectangle that widens + thickens into the spoon bowl,
    whose inner (gripping) face dips into a concave dish (``dish_up`` puts the
    dish on the +Z face so the two arms' dishes face each other when assembled).

    A CadQuery sphere-cut-then-union bowl tessellates with degenerate seam
    slivers that the disconnected-island check flags; section_loft's repair pass
    keeps the result a single watertight component.
    """
    arm_len = r.arm_length
    bowl_len = r.bowl_length
    shaft_end = arm_len - bowl_len
    half_t = r.arm_thickness / 2.0
    bht = r.bowl_thick / 2.0
    bowl_x0 = shaft_end + 0.004

    xs = [0.0, 0.018, 0.090, shaft_end - 0.010, bowl_x0]
    n = 10
    for i in range(1, n + 1):
        xs.append(bowl_x0 + (i / n) * (arm_len - bowl_x0))

    sections: list[list[tuple[float, float, float]]] = []
    for x in xs:
        if x <= 0.090:
            w = max(r.root_width / 2.0 + (x / 0.090) * (r.mid_width / 2.0 - r.root_width / 2.0), 0.003)
            t = half_t
            dish = 0.0
        elif x <= bowl_x0:
            w = r.mid_width / 2.0
            t = half_t
            dish = 0.0
        else:
            bt = (x - bowl_x0) / (arm_len - bowl_x0)
            w = r.mid_width / 2.0 + bt * (r.bowl_width / 2.0 - r.mid_width / 2.0)
            if bt > 0.85:
                w = max(w * math.cos((bt - 0.85) / 0.15 * math.pi / 2.0), 0.003)
            t = half_t + bt * (bht - half_t)
            dish = r.dish_depth * math.sin(min(bt / 0.85, 1.0) * math.pi)
        if dish_up:
            pts = [(x, -w, -t), (x, w, -t), (x, w, t), (x, 0.0, t - dish), (x, -w, t)]
        else:
            pts = [(x, -w, -t), (x, 0.0, -t + dish), (x, w, -t), (x, w, t), (x, -w, t)]
        sections.append(pts)

    return section_loft(sections, repair="auto", cap=True, solid=True)


def _build_arm_mesh(r: ResolvedWoodenTongsConfig, name: str, *, dish_up: bool, assets):
    """Build one arm's mesh for the active arm_shape (both arms share the shape)."""
    if r.arm_shape == "round_dowel":
        return mesh_from_geometry(_arm_dowel(r), name)
    if r.arm_shape == "straight_slat":
        return mesh_from_cadquery(_slat_solid(r), name, assets=assets)
    if r.arm_shape == "spoon_ends":
        return mesh_from_geometry(_arm_scoop_loft(r, dish_up=dish_up), name)
    if r.arm_shape == "square_ends":
        return mesh_from_cadquery(_arm_solid(r, square_tip=True), name, assets=assets)
    # flat_paddle (default)
    return mesh_from_cadquery(_arm_solid(r, square_tip=False), name, assets=assets)


def _arm_visual_name(i: int) -> str:
    """Per-arm strip visual name (used by tests / allow_overlap)."""
    return f"arm_strip_{i}"


# ---------------------------------------------------------------------------
# close_mechanism hardware helpers (Slot A).
# ---------------------------------------------------------------------------
def _clip_solid(r: ResolvedWoodenTongsConfig, span: float) -> cq.Workplane:
    clip = (
        cq.Workplane("XY")
        .box(CLIP_LEN, CLIP_WIDTH, span)
        .translate((CLIP_LEN / 2.0 - 0.003, 0.0, 0.0))
    )
    try:
        clip = clip.edges("|X").fillet(0.0022)
    except Exception:
        pass
    return clip


def _pin_solid(height: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .circle(PIN_RADIUS)
        .extrude(height)
        .translate((0.0, 0.0, -height / 2.0))
    )


def _scissor_arm_solid(r: ResolvedWoodenTongsConfig) -> cq.Workplane:
    """Scissor arm: handle on -X, tip on +X, pivot crossing at x=0."""
    half_t = SCISSOR_THICK / 2.0
    hl = r.handle_length
    tr = r.tip_reach
    hw = r.scissor_handle_w
    pw = r.scissor_pivot_w
    tw = r.scissor_tip_w
    pts = [
        (-hl + 0.003, 0.003),
        (-hl + 0.015, hw / 2.0),
        (-hl + 0.040, hw / 2.0),
        (-0.020, pw / 2.0 + 0.002),
        (-0.006, pw / 2.0),
        (0.006, pw / 2.0),
        (0.020, pw / 2.0 + 0.001),
        (tr - 0.050, tw / 2.0 - 0.003),
        (tr - 0.018, tw / 2.0),
        (tr - 0.004, tw / 2.0 - 0.005),
        (tr, 0.003),
    ]
    lower = [(x, -y) for (x, y) in reversed(pts)]
    outline = pts + lower
    arm = (
        cq.Workplane("XY")
        .polyline(outline)
        .close()
        .extrude(SCISSOR_THICK)
        .translate((0.0, 0.0, -half_t))
    )
    try:
        arm = arm.edges("|Z").fillet(0.0008)
    except Exception:
        pass
    return arm


def _bend_solid(r: ResolvedWoodenTongsConfig) -> cq.Workplane:
    """U-shaped wooden bend (half-torus, rectangular section, curves into -X)."""
    R = r.bend_radius
    hw = r.root_width / 2.0
    ht = r.arm_thickness / 2.0
    pts = [
        (-hw, -R - ht),
        (hw, -R - ht),
        (hw, -R + ht),
        (-hw, -R + ht),
    ]
    bend = (
        cq.Workplane("YZ")
        .polyline(pts)
        .close()
        .revolve(180, (0, 0), (1, 0))
    )
    # No edge fillet: filleting all edges of the revolved half-torus tessellates
    # with degenerate zero-area seam slivers (disconnected mesh islands). The
    # revolved bend already reads as a smooth wooden U.
    return bend


def _ring_solid(r: ResolvedWoodenTongsConfig) -> cq.Workplane:
    outer = cq.Workplane("XY").box(r.ring_length, r.ring_outer_y, r.ring_outer_z)
    bore = cq.Workplane("XY").box(r.ring_length + 0.004, r.ring_bore_y, r.ring_bore_z)
    ring = outer.cut(bore)
    try:
        ring = ring.edges("|X").fillet(0.003)
    except Exception:
        pass
    return ring


def _grip_nub(r: ResolvedWoodenTongsConfig) -> cq.Workplane:
    return cq.Workplane("XY").box(r.ring_length * 0.80, 0.006, 0.003)


# ---------------------------------------------------------------------------
# grip_detail helpers (Slot C).
# ---------------------------------------------------------------------------
def _finger_scallop(r: ResolvedWoodenTongsConfig, *, half_w: float | None = None) -> cq.Workplane:
    rr = r.ridge_r
    w = 2.0 * (half_w if half_w is not None else r.ridge_w / 2.0)
    shape = (
        cq.Workplane("XZ")
        .moveTo(-rr, 0)
        .radiusArc((rr, 0), -rr)
        .close()
        .extrude(w)
        .translate((0, -w / 2, 0))
    )
    return shape


def _finger_scallop_inverted(r: ResolvedWoodenTongsConfig, *, half_w: float | None = None) -> cq.Workplane:
    rr = r.ridge_r
    w = 2.0 * (half_w if half_w is not None else r.ridge_w / 2.0)
    shape = (
        cq.Workplane("XZ")
        .moveTo(-rr, 0)
        .radiusArc((rr, 0), rr)
        .close()
        .extrude(w)
        .translate((0, -w / 2, 0))
    )
    return shape


# ---------------------------------------------------------------------------
# Part emission
# ---------------------------------------------------------------------------
def _arm_face_half_t(r: ResolvedWoodenTongsConfig) -> float:
    """Z half-thickness of the arm surface AT THE GRIP SECTION (mid shaft) where
    the scallops sit. The grip section is the shaft for every arm_shape (the bowl
    / paddle is further out at the tip), so spoon_ends uses the shaft thickness,
    not the bowl thickness. round_dowel uses the shaft radius."""
    if r.arm_shape == "round_dowel":
        return r.dowel_shaft_r
    return r.arm_thickness / 2.0


def _emit_scallops(
    part,
    r: ResolvedWoodenTongsConfig,
    mats,
    *,
    is_fixed: bool,
    assets,
) -> None:
    """Emit the finger-scallop ridge visuals on both faces (Rule 1: arm visuals,
    no joints). The fixed arm's strip is rotated by +half_splay about Z, so its
    scallops are rotated + offset in -Z by arm_stack; the moving arm is straight.
    """
    scissor = r.close_mechanism == "scissor_pin"
    # Each arm's scallops must follow that arm's actual visual placement (its z
    # offset and its in-plane splay rotation) so every ridge lands on the wood.
    #   fixed arm:  z = fixed_arm_z,  splay = +half_splay
    #   moving arm: non-scissor -> z=0, splay=0 (authored straight, joint splays)
    #               scissor     -> z=+scissor_stack, splay=-half_splay
    if is_fixed:
        arm_z = _fixed_arm_z(r)
        arm_splay = r.half_splay
    elif scissor:
        arm_z = r.scissor_stack
        arm_splay = -r.half_splay
    else:
        arm_z = 0.0
        arm_splay = 0.0
    cos_s = math.cos(arm_splay)
    sin_s = math.sin(arm_splay)
    mat = mats["wood"] if is_fixed else mats["wood_dark"]
    # Sink each ridge's flat base a good way BELOW the surface so the whole ridge
    # bar (including its ends) overlaps / is supported by the arm rather than
    # floating off it (a tangent or air-gapped ridge reads as a disconnected
    # island). On a round dowel the surface curves away from the ridge ends, so
    # narrow the ridge to fit within the dowel and embed it deeper.
    if scissor:
        # Scissor arm: ridges go on the wide HANDLE (the actual grip), on the
        # -X side, sized within the handle width and using the scissor strip
        # thickness.
        half_t = SCISSOR_THICK / 2.0
        ridge_half_w = min(r.ridge_w, r.scissor_handle_w * 0.7) / 2.0
        embed = min(0.0014, half_t * 0.6)
    elif r.arm_shape == "round_dowel":
        half_t = _arm_face_half_t(r)
        ridge_half_w = min(r.ridge_w, 1.2 * r.dowel_shaft_r) / 2.0
        embed = half_t * 0.7
    else:
        half_t = _arm_face_half_t(r)
        ridge_half_w = r.ridge_w / 2.0
        embed = min(0.0014, half_t * 0.6)
    top_z = half_t - embed
    bot_z = -half_t + embed

    scallop_top = mesh_from_cadquery(
        _finger_scallop(r, half_w=ridge_half_w), "scallop_top", assets=assets
    )
    scallop_bot = mesh_from_cadquery(
        _finger_scallop_inverted(r, half_w=ridge_half_w), "scallop_bot", assets=assets
    )

    # Scallop X stations: on the +X shaft grip for single-ended arms; on the
    # -X handle grip for the scissor arm (kept inside the constant-width handle
    # so every ridge rests on full-width wood, not the tapered tip).
    if scissor:
        # The scissor handle is full-width only between ~(-handle_length+0.015)
        # and (-handle_length+0.040); beyond that it tapers toward the pivot. Lay
        # the ridges inside that constant-width grip band so they rest on full
        # wood (not the taper, which would leave the ridge ends floating).
        handle_lo = -r.handle_length + 0.016
        handle_hi = -r.handle_length + 0.040
        room = max(0.0, handle_hi - handle_lo)
        count = r.scallop_count
        spacing = (room / max(1, count - 1)) if count > 1 else 0.0
        x_positions = [handle_lo + i * spacing for i in range(count)]
    else:
        x_positions = [r.grip_start_x + i * r.scallop_spacing for i in range(r.scallop_count)]

    for i in range(r.scallop_count):
        x_pos = x_positions[i]
        part.visual(
            scallop_top,
            origin=Origin(
                xyz=(x_pos * cos_s, x_pos * sin_s, top_z + arm_z),
                rpy=(0.0, 0.0, arm_splay),
            ),
            material=mat,
            name=f"scallop_{i}", material_class_id=("wood.walnut_dark" if r.palette_style in {"natural_birch", "walnut_stained", "cherry_warm", "painted_white", "ebony_dark"} else "wood.bamboo"),
        )
        part.visual(
            scallop_bot,
            origin=Origin(
                xyz=(x_pos * cos_s, x_pos * sin_s, bot_z + arm_z),
                rpy=(0.0, 0.0, arm_splay),
            ),
            material=mat,
            name=f"scallop_bot_{i}", material_class_id=("wood.walnut_dark" if r.palette_style in {"natural_birch", "walnut_stained", "cherry_warm", "painted_white", "ebony_dark"} else "wood.bamboo"),
        )


def _arm_inertial(r: ResolvedWoodenTongsConfig) -> Inertial:
    return Inertial.from_geometry(
        Box((r.arm_length, max(r.mid_width, r.tip_width), max(r.arm_thickness, 0.012))),
        mass=0.03,
        origin=Origin(xyz=(r.arm_length / 2.0, 0.0, 0.0)),
    )


def _emit_arms_and_pivot(
    model: ArticulatedObject,
    r: ResolvedWoodenTongsConfig,
    mats,
    *,
    assets,
) -> tuple[object, object]:
    """Emit the two arms + the shared ``pivot`` REVOLUTE for the active
    close_mechanism. Returns (fixed_arm, moving_arm). Arm count is FIXED at 2."""
    scissor = r.close_mechanism == "scissor_pin"
    stack = _stack_for_shape(r, scissor=scissor)

    if scissor:
        # Scissor: both arms cross at x=0; handle on -X, tip on +X. Use the
        # scissor arm mesh (the arm_shape mesh tips would not be centered on the
        # crossing). arm_0 = root (splay +), arm_1 = child (splay -).
        arm_geo = _scissor_arm_solid(r)
        arm_mesh = mesh_from_cadquery(arm_geo, "scissor_arm", assets=assets)
        fixed_arm = model.part("fixed_arm")
        fixed_arm.visual(
            arm_mesh,
            origin=Origin(xyz=(0.0, 0.0, -stack), rpy=(0.0, 0.0, r.half_splay)),
            material=mats["wood"],
            name=_arm_visual_name(0), material_class_id=("wood.walnut_dark" if r.palette_style in {"natural_birch", "walnut_stained", "cherry_warm", "painted_white", "ebony_dark"} else "wood.bamboo"),
        )
        fixed_arm.inertial = _arm_inertial(r)
        moving_arm = model.part("moving_arm")
        moving_arm.visual(
            arm_mesh,
            origin=Origin(xyz=(0.0, 0.0, stack), rpy=(0.0, 0.0, -r.half_splay)),
            material=mats["wood_dark"],
            name=_arm_visual_name(1), material_class_id=("wood.walnut_dark" if r.palette_style in {"natural_birch", "walnut_stained", "cherry_warm", "painted_white", "ebony_dark"} else "wood.bamboo"),
        )
        moving_arm.inertial = _arm_inertial(r)
        # Pivot pin (root visual) crosses both arms vertically at x=0.
        fixed_arm.visual(
            mesh_from_cadquery(_pin_solid(r.pin_height), "pivot_pin", assets=assets),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["metal"],
            name="pivot_pin", material_class_id=("metal.stainless_matte" if r.palette_style in {"natural_birch", "walnut_stained", "cherry_warm", "painted_white", "bamboo_blond"} else "metal.blackened_gunmetal"),
        )
        model.articulation(
            "pivot",
            ArticulationType.REVOLUTE,
            parent=fixed_arm,
            child=moving_arm,
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=2.0, velocity=3.0, lower=r.pivot_lower, upper=r.pivot_upper
            ),
        )
        return fixed_arm, moving_arm

    # Non-scissor: arms run +X from the pivot; the pivot origin depends on the
    # mechanism (clip/ring: stacked face; bend: bend top).
    fixed_mesh = _build_arm_mesh(r, "fixed_arm", dish_up=True, assets=assets)
    moving_mesh = _build_arm_mesh(r, "moving_arm", dish_up=False, assets=assets)

    fixed_z = _fixed_arm_z(r)
    fixed_arm = model.part("fixed_arm")
    fixed_arm.visual(
        fixed_mesh,
        origin=Origin(xyz=(0.0, 0.0, fixed_z), rpy=(0.0, 0.0, r.half_splay)),
        material=mats["wood"],
        name=_arm_visual_name(0), material_class_id=("wood.walnut_dark" if r.palette_style in {"natural_birch", "walnut_stained", "cherry_warm", "painted_white", "ebony_dark"} else "wood.bamboo"),
    )
    fixed_arm.inertial = _arm_inertial(r)

    moving_arm = model.part("moving_arm")
    moving_arm.visual(
        moving_mesh,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["wood_dark"],
        name=_arm_visual_name(1), material_class_id=("wood.walnut_dark" if r.palette_style in {"natural_birch", "walnut_stained", "cherry_warm", "painted_white", "ebony_dark"} else "wood.bamboo"),
    )
    moving_arm.inertial = _arm_inertial(r)

    if r.close_mechanism == "onepiece_bend":
        # Bent-wood U is rigid with the root; NO metal. Pivot origin at bend top.
        fixed_arm.visual(
            mesh_from_cadquery(_bend_solid(r), "wood_bend", assets=assets),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["wood"],
            name="wood_bend", material_class_id=("wood.walnut_dark" if r.palette_style in {"natural_birch", "walnut_stained", "cherry_warm", "painted_white", "ebony_dark"} else "wood.bamboo"),
        )
        # moving arm sits at the +bend_radius junction (not stacked offset).
        # Re-author the moving arm visual at z=0; the joint shifts it.
        pivot_origin = Origin(xyz=(0.0, 0.0, r.bend_radius), rpy=(0.0, 0.0, -r.half_splay))
    else:
        # spring clip (onepiece_spring_clip / lock_ring): metal box bridges both
        # stacked arms at the pivot.
        fixed_arm.visual(
            mesh_from_cadquery(_clip_solid(r, r.clip_span), "clip", assets=assets),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["metal"],
            name="spring_clip", material_class_id=("metal.stainless_matte" if r.palette_style in {"natural_birch", "walnut_stained", "cherry_warm", "painted_white", "bamboo_blond"} else "metal.blackened_gunmetal"),
        )
        pivot_origin = Origin(xyz=(0.0, 0.0, stack), rpy=(0.0, 0.0, -r.half_splay))

    model.articulation(
        "pivot",
        ArticulationType.REVOLUTE,
        parent=fixed_arm,
        child=moving_arm,
        origin=pivot_origin,
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=3.0, lower=r.pivot_lower, upper=r.pivot_upper
        ),
    )
    return fixed_arm, moving_arm


def _emit_lock_ring(
    model: ArticulatedObject,
    r: ResolvedWoodenTongsConfig,
    fixed_arm,
    mats,
    *,
    assets,
) -> None:
    """Emit the sliding lock-ring part + the ``slide`` PRISMATIC (lock_ring only)."""
    slide_ring = model.part("slide_ring")
    slide_ring.visual(
        mesh_from_cadquery(_ring_solid(r), "ring_band", assets=assets),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["ring"],
        name="ring_band", material_class_id=("wood.walnut_dark" if r.palette_style in {"natural_birch", "walnut_stained", "cherry_warm", "painted_white", "ebony_dark"} else "wood.bamboo"),
    )
    # Four cardinal grip nubs (FIXED decoration, Rule 1: ring visuals, no joint).
    _grip_faces = [
        (0.0, 1.0, 0.0),
        (0.0, -1.0, math.pi),
        (1.0, 0.0, math.pi / 2.0),
        (-1.0, 0.0, -math.pi / 2.0),
    ]
    nub_mesh = mesh_from_cadquery(_grip_nub(r), "grip_nub", assets=assets)
    for i in range(N_GRIPS):
        dy, dz, rx = _grip_faces[i]
        gy = dy * (r.ring_outer_y / 2.0 + 0.001)
        gz = dz * (r.ring_outer_z / 2.0 + 0.001)
        slide_ring.visual(
            nub_mesh,
            origin=Origin(xyz=(0.0, gy, gz), rpy=(rx, 0.0, 0.0)),
            material=mats["ring"],
            name=f"grip_{i}", material_class_id=("wood.walnut_dark" if r.palette_style in {"natural_birch", "walnut_stained", "cherry_warm", "painted_white", "ebony_dark"} else "wood.bamboo"),
        )
    slide_ring.inertial = Inertial.from_geometry(
        Box((r.ring_length, r.ring_outer_y, r.ring_outer_z)),
        mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    model.articulation(
        "slide",
        ArticulationType.PRISMATIC,
        parent=fixed_arm,
        child=slide_ring,
        origin=Origin(xyz=(r.ring_rest_x, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=0.15, lower=0.0, upper=r.ring_travel
        ),
    )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_wooden_tongs(
    config: WoodenTongsConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    # Register only the materials the active mechanism uses; onepiece_bend has
    # NO metal (spec: bent-wood design asserts no metal material).
    palette = PALETTES[r.palette_style]
    keys = ["wood", "wood_dark"]
    if r.close_mechanism != "onepiece_bend":
        keys.append("metal")
    if r.close_mechanism == "spring_clip_with_lock_ring":
        keys.append("ring")
    mats = {
        key: model.material(f"wooden_tongs_{key}_{r.palette_style}", rgba=palette[key])
        for key in keys
    }

    fixed_arm, _moving_arm = _emit_arms_and_pivot(model, r, mats, assets=assets)

    if r.grip_detail == "scalloped_grip":
        _emit_scallops(fixed_arm, r, mats, is_fixed=True, assets=assets)
        _emit_scallops(_moving_arm, r, mats, is_fixed=False, assets=assets)

    if r.close_mechanism == "spring_clip_with_lock_ring":
        _emit_lock_ring(model, r, fixed_arm, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_wooden_tongs(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_wooden_tongs(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _tip_y(ctx: TestContext, part) -> float:
    lo, hi = ctx.part_world_aabb(part)
    return (lo[1] + hi[1]) / 2.0


def run_wooden_tongs_tests(
    object_model: ArticulatedObject,
    config: WoodenTongsConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    fixed_arm = object_model.get_part("fixed_arm")
    moving_arm = object_model.get_part("moving_arm")

    # ---- Captured / bridging overlaps (element-scoped). ----
    if r.close_mechanism == "scissor_pin":
        ctx.allow_overlap(
            fixed_arm, moving_arm,
            elem_a="pivot_pin", elem_b=_arm_visual_name(1),
            reason="The pivot pin passes through both arms at the scissor crossing.",
        )
    elif r.close_mechanism == "onepiece_bend":
        ctx.allow_overlap(
            fixed_arm, moving_arm,
            elem_a="wood_bend", elem_b=_arm_visual_name(1),
            reason="The moving arm seats into the wooden bend at the flex junction.",
        )
    else:
        # spring clip wraps over the moving arm strip at the pivot.
        ctx.allow_overlap(
            fixed_arm, moving_arm,
            elem_a="spring_clip", elem_b=_arm_visual_name(1),
            reason="The spring clip bridges and clamps both stacked arms at the pivot.",
        )

    if r.close_mechanism == "spring_clip_with_lock_ring":
        slide_ring = object_model.get_part("slide_ring")
        ctx.allow_overlap(
            slide_ring, fixed_arm,
            elem_a="ring_band", elem_b=_arm_visual_name(0),
            reason="The ring bore encircles / locks against the fixed arm when slid toward the tips.",
        )
        ctx.allow_overlap(
            slide_ring, moving_arm,
            elem_a="ring_band", elem_b=_arm_visual_name(1),
            reason="The ring bore encircles / locks against the moving arm when slid toward the tips.",
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

    # ---- Single root + shared REVOLUTE pivot (all candidates). ----
    roots = object_model.root_parts()
    ctx.check(
        "fixed_arm is the single root",
        len(roots) == 1 and roots[0].name == "fixed_arm",
        details=f"roots={[p.name for p in roots]}",
    )
    pivot = object_model.get_articulation("pivot")
    ax = pivot.axis
    ctx.check(
        "pivot is REVOLUTE about the flat-plane normal (Z)",
        pivot.articulation_type == ArticulationType.REVOLUTE
        and abs(ax[2]) > 0.99
        and abs(ax[0]) < 0.02
        and abs(ax[1]) < 0.02,
        details=f"type={pivot.articulation_type} axis={tuple(ax)}",
    )

    # ---- Two long arms (~0.30 m, fixed at 2). ----
    arm_parts = [p for p in object_model.parts if p.name in ("fixed_arm", "moving_arm")]
    ctx.check("exactly two arms", len(arm_parts) == 2, details=str([p.name for p in arm_parts]))
    lo_len = 0.85 * ARM_LENGTH
    hi_len = 1.20 * ARM_LENGTH
    for p in (fixed_arm, moving_arm):
        lo, hi = ctx.part_world_aabb(p)
        length = hi[0] - lo[0]
        ctx.check(
            f"{p.name} is a long arm (~0.30 m)",
            lo_len < length < hi_len,
            details=f"len={length:.3f}",
        )

    # ---- Arm shape topology. ----
    # scissor_pin authors its own flat crossing arm (handle on -X, tip on +X) so
    # the arm-shape mesh is overridden there; the shape-specific cross-section
    # assertions only apply to the +X single-ended (non-scissor) arms.
    if r.close_mechanism != "scissor_pin":
        if r.arm_shape == "round_dowel":
            d0_lo, d0_hi = ctx.part_element_world_aabb(fixed_arm, elem=_arm_visual_name(0))
            dowel_z = d0_hi[2] - d0_lo[2]
            ctx.check(
                "round_dowel arm has round (not flat-strip) cross-section in Z",
                dowel_z > 2.0 * r.dowel_root_r * 0.9,
                details=f"z_extent={dowel_z:.4f}",
            )
        elif r.arm_shape == "spoon_ends":
            flo, fhi = ctx.part_world_aabb(fixed_arm)
            ctx.check(
                "spoon_ends arm tip is thicker than a flat shaft (bowl)",
                (fhi[2] - flo[2]) > r.bowl_thick - 0.003,
                details=f"z_span={(fhi[2]-flo[2]):.4f}",
            )

    # ---- close_mechanism topology. ----
    part_names = {p.name for p in object_model.parts}
    art_names = {a.name for a in object_model.articulations}
    if r.close_mechanism == "scissor_pin":
        pin_lo, pin_hi = ctx.part_element_world_aabb(fixed_arm, elem="pivot_pin")
        arm_lo, arm_hi = ctx.part_world_aabb(fixed_arm)
        pin_x = (pin_lo[0] + pin_hi[0]) / 2.0
        handle_side = pin_x - arm_lo[0]
        tip_side = arm_hi[0] - pin_x
        ctx.check(
            "scissor pin is partway along the arm (not at an end)",
            handle_side > 0.05 and tip_side > 0.05,
            details=f"pin_x={pin_x:.3f} handle={handle_side:.3f} tip={tip_side:.3f}",
        )
        pin_dx = pin_hi[0] - pin_lo[0]
        pin_dy = pin_hi[1] - pin_lo[1]
        ctx.check(
            "scissor pin is round (circular cross-section)",
            0.5 < pin_dx / max(pin_dy, 1e-6) < 2.0 and pin_dx < 0.015,
            details=f"pin dx={pin_dx:.4f} dy={pin_dy:.4f}",
        )
    elif r.close_mechanism == "onepiece_bend":
        # No metal material, no spring_clip / pivot_pin visual anywhere.
        metal_mats = [
            m for m in object_model.materials
            if "metal" in m.name.lower() or "clip" in m.name.lower()
        ]
        ctx.check(
            "onepiece_bend has no metal material",
            len(metal_mats) == 0,
            details=f"found={[m.name for m in metal_mats]}",
        )
        for p in (fixed_arm, moving_arm):
            vnames = [v.name for v in p.visuals]
            ctx.check(
                f"{p.name} has no spring_clip / pivot_pin visual (bent-wood)",
                "spring_clip" not in vnames and "pivot_pin" not in vnames,
                details=f"visuals={vnames}",
            )
        bend_lo, bend_hi = ctx.part_element_world_aabb(fixed_arm, elem="wood_bend")
        ctx.check(
            "wood bend curves outward in -X (U/hairpin)",
            bend_lo[0] < -0.004,
            details=f"bend min_x={bend_lo[0]:.4f}",
        )
        ctx.check("no slide joint for bend", "slide" not in art_names, details=str(sorted(art_names)))
    else:
        # spring clip (onepiece_spring_clip / lock_ring): metal clip at pivot.
        clo, chi = ctx.part_element_world_aabb(fixed_arm, elem="spring_clip")
        ctx.check(
            "spring clip sits at the pivot end (near x=0)",
            clo[0] < 0.025 and chi[0] < 0.035,
            details=f"clip x=[{clo[0]:.3f},{chi[0]:.3f}]",
        )
        ctx.check(
            "spring clip bridges both stacked arms in Z",
            (chi[2] - clo[2]) > r.arm_thickness,
            details=f"clip z-span={(chi[2]-clo[2]):.4f}",
        )

    # ---- lock_ring slide topology (only that mechanism). ----
    if r.close_mechanism == "spring_clip_with_lock_ring":
        ctx.check("slide_ring is an independent part", "slide_ring" in part_names, details=str(sorted(part_names)))
        slide = object_model.get_articulation("slide")
        sax = slide.axis
        ctx.check(
            "slide is PRISMATIC along the arm length (X)",
            slide.articulation_type == ArticulationType.PRISMATIC
            and abs(sax[0]) > 0.99 and abs(sax[1]) < 0.02 and abs(sax[2]) < 0.02,
            details=f"type={slide.articulation_type} axis={tuple(sax)}",
        )
        slide_ring = object_model.get_part("slide_ring")
        rest_x = ctx.part_world_position(slide_ring)
        with ctx.pose({slide: slide.motion_limits.upper}):
            ext_x = ctx.part_world_position(slide_ring)
        if rest_x is not None and ext_x is not None:
            ctx.check(
                "slide moves the ring toward the tips (+X)",
                ext_x[0] > rest_x[0] + 0.02,
                details=f"rest_x={rest_x[0]:.3f} ext_x={ext_x[0]:.3f}",
            )
        # Ring still encircles both arms (Y/Z) at rest (has not slipped off).
        ctx.expect_overlap(
            fixed_arm, slide_ring, axes="yz", min_overlap=0.003,
            elem_a=_arm_visual_name(0), elem_b="ring_band",
            name="ring bore encircles the fixed arm at rest",
        )
        ctx.expect_overlap(
            moving_arm, slide_ring, axes="yz", min_overlap=0.003,
            elem_a=_arm_visual_name(1), elem_b="ring_band",
            name="ring bore encircles the moving arm at rest",
        )
    else:
        ctx.check("no slide_ring part", "slide_ring" not in part_names, details=str(sorted(part_names)))
        ctx.check("no slide joint", "slide" not in art_names, details=str(sorted(art_names)))

    # ---- grip_detail topology. ----
    if r.grip_detail == "scalloped_grip":
        for p in (fixed_arm, moving_arm):
            vnames = {v.name for v in p.visuals}
            present = all(
                f"scallop_{i}" in vnames and f"scallop_bot_{i}" in vnames
                for i in range(r.scallop_count)
            )
            ctx.check(
                f"{p.name} has {r.scallop_count} scallop ridge pairs",
                present,
                details=f"visuals={sorted(vnames)}",
            )
        slo, shi = ctx.part_element_world_aabb(fixed_arm, elem="scallop_0")
        if r.close_mechanism == "scissor_pin":
            # Scissor scallops sit on the -X handle grip (away from the pivot).
            ctx.check(
                "first scallop is on the handle grip (negative X)",
                slo[0] < -0.010,
                details=f"scallop_0 x_min={slo[0]:.3f}",
            )
        else:
            ctx.check(
                "first scallop is on the grip section (past the pivot)",
                slo[0] > 0.030,
                details=f"scallop_0 x_min={slo[0]:.3f}",
            )

    # ---- Rest pose: arms splay open into a "V" (tips on opposite Y sides). ----
    # The whole-arm AABB-center Y is a weak splay signal for the scissor arm (it
    # spans both -X handle and +X tip, which lie on opposite Y sides after the
    # splay, nearly cancelling). The real open/close verification is the pose
    # sweep below; here just confirm the two arm centers sit on opposite sides.
    open_margin = 0.0012 if r.close_mechanism == "scissor_pin" else 0.004
    ctx.check(
        "arms splay to opposite sides at rest (open V)",
        _tip_y(ctx, fixed_arm) > open_margin and _tip_y(ctx, moving_arm) < -open_margin,
        details=f"fixed_tip_y={_tip_y(ctx, fixed_arm):.3f} moving_tip_y={_tip_y(ctx, moving_arm):.3f}",
    )

    # ---- Mechanism: pivot opens / closes the tips. ----
    rest_gap = _tip_y(ctx, fixed_arm) - _tip_y(ctx, moving_arm)
    with ctx.pose({pivot: pivot.motion_limits.upper}):
        closed_gap = _tip_y(ctx, fixed_arm) - _tip_y(ctx, moving_arm)
    with ctx.pose({pivot: pivot.motion_limits.lower}):
        open_gap = _tip_y(ctx, fixed_arm) - _tip_y(ctx, moving_arm)
    ctx.check(
        "squeezing (upper limit) closes the tips together",
        closed_gap < rest_gap - 0.005,
        details=f"rest={rest_gap:.3f} closed={closed_gap:.3f}",
    )
    ctx.check(
        "opening (lower limit) spreads the tips wider",
        open_gap > rest_gap,
        details=f"rest={rest_gap:.3f} open={open_gap:.3f}",
    )

    # ---- Arms share the pivot origin (hinged together). ----
    ctx.expect_origin_distance(
        fixed_arm, moving_arm, axes="xy", max_dist=0.020,
        name="arms share the pivot origin",
    )

    return ctx.report()


__all__ = (
    "WoodenTongsConfig",
    "ResolvedWoodenTongsConfig",
    "build_wooden_tongs",
    "build_seeded_wooden_tongs",
    "config_from_seed",
    "resolve_config",
    "run_wooden_tongs_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
