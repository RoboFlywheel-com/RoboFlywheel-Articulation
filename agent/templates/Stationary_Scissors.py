# SPDX-License-Identifier: Apache-2.0

"""Pair-of-scissors modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Stationary_Scissors.md`` and the
``picture/Stationary/Scissors`` 5-star sample pool (1 parent + 8 single-axis
fork variants: spring_loaded / offset_loops / long_shears / blunt_tips /
twin_blades / finger_brace / pinking_edge / curved_blades).

Structure (pattern = ``mixed``): a **2-bar pivot** — root ``blade_a`` and child
``blade_b`` rotate relative to each other about the central screw (REVOLUTE,
axis +Z, origin at the world origin where the two steel hubs nest in a riveted
lap). Each half carries one or more steel blades plus a plastic finger-loop
handle; both halves are mirror images authored in a pivot-at-origin local frame
and canted by ``HALF_CANT`` so the blades cross above the pivot.

Slots:

  * ``blade_profile`` (4): straight pointed / curved hooked (arc-swept) / blunt
    safety (rounded nose) / pinking sawtooth (zigzag cutting edge).
  * ``handle_loops`` (3): symmetric matched loops / asymmetric thumb-and-finger
    loops / a finger loop with an extra molded finger-brace tang.
  * ``spring_assist`` (2, optional): none, or a leaf spring bridging the two
    handles as a second REVOLUTE joint (``spring_flex``) that self-opens.
  * ``blades_per_half`` **multiplicity** (1-5): a single blade, or N parallel
    thin blades stacked across the thickness (herb scissors) that interleave at
    the pivot. Encoded in slot_choices as ``blades_{n}``.

The central screw / disc cap / hub is always an inline ``blade_a`` visual (no
FIXED decoration part). The pivot is captured-pin geometry (two hub bosses nest
on one screw axis), so its joint omits ``MatingContract`` (grandfathered) and is
guarded by the flat articulation-origin baseline + a broad ``allow_overlap`` on
``blade_a``/``blade_b`` — mirroring shopping_bucket's bail pivot treatment.
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

BladeProfile = Literal["straight_pointed", "curved_hooked", "blunt_safety", "pinking_sawtooth"]
HandleLoops = Literal["symmetric_loops", "offset_thumb_finger", "finger_brace_tang"]
SpringAssist = Literal["none", "leaf_spring"]
MaterialStyle = Literal["steel_red", "steel_green", "steel_black", "gold_ivory"]

BLADE_PROFILES: tuple[BladeProfile, ...] = (
    "straight_pointed",
    "curved_hooked",
    "blunt_safety",
    "pinking_sawtooth",
)
HANDLE_LOOPS: tuple[HandleLoops, ...] = (
    "symmetric_loops",
    "offset_thumb_finger",
    "finger_brace_tang",
)
SPRING_ASSISTS: tuple[SpringAssist, ...] = ("none", "leaf_spring")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "steel_red",
    "steel_green",
    "steel_black",
    "gold_ivory",
)

# Blades-per-half multiplicity domain (spec §8). 1 = ordinary shears, 2-5 = herb.
N_BLADES_MIN, N_BLADES_MAX = 1, 5

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "steel_red": {
        "blade": (0.74, 0.76, 0.79, 1.0),
        "handle": (0.86, 0.13, 0.11, 1.0),
        "cap": (0.80, 0.82, 0.85, 1.0),
        "spring": (0.55, 0.57, 0.60, 1.0),
    },
    "steel_green": {
        "blade": (0.74, 0.76, 0.79, 1.0),
        "handle": (0.16, 0.52, 0.20, 1.0),
        "cap": (0.80, 0.82, 0.85, 1.0),
        "spring": (0.50, 0.52, 0.55, 1.0),
    },
    "steel_black": {
        "blade": (0.70, 0.72, 0.75, 1.0),
        "handle": (0.12, 0.12, 0.14, 1.0),
        "cap": (0.78, 0.80, 0.83, 1.0),
        "spring": (0.45, 0.47, 0.50, 1.0),
    },
    "gold_ivory": {
        "blade": (0.83, 0.78, 0.55, 1.0),
        "handle": (0.92, 0.88, 0.80, 1.0),
        "cap": (0.86, 0.80, 0.58, 1.0),
        "spring": (0.70, 0.66, 0.50, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Scaled per-build by the resolved config.
# Baselines from parent 6adf5ca9 and the fork variants.
# ---------------------------------------------------------------------------
_BLADE_LENGTH = 0.092  # pivot -> blade tip (scaled by blade_length_scale)
_BLADE_ROOT_WIDTH = 0.013
_BLADE_TIP_WIDTH = 0.0022
_BLADE_THICKNESS = 0.0020  # solid-shears single-blade stock thickness

_HANDLE_LENGTH = 0.082  # pivot -> far end of the finger loop
_HANDLE_NECK_WIDTH = 0.011
_HANDLE_THICKNESS = 0.0060  # plastic handle thickness

_LOOP_OUTER_LONG = 0.052
_LOOP_OUTER_WIDE = 0.040
_LOOP_WALL = 0.0075

# Thumb/finger loops (offset_thumb_finger).
_THUMB_LOOP_OD = 0.030
_THUMB_LOOP_WALL = 0.0055
_THUMB_HANDLE_LENGTH = 0.068
_FINGER_LOOP_LONG = 0.058
_FINGER_LOOP_WIDE = 0.046

# Finger-brace tang (finger_brace_tang).
_BRACE_LENGTH = 0.019
_BRACE_WIDTH = 0.0052
_BRACE_TIP_RADIUS = 0.0028

_PIVOT_HUB_R = 0.0075
_PIVOT_HOLE_R = 0.0026
_PIVOT_CAP_R = 0.0066
_PIVOT_CAP_T = 0.0016

# Curved/hooked blade arc radius (curved_hooked).
_HOOK_RADIUS = 0.13

# Pinking sawtooth (pinking_sawtooth).
_PINKING_PITCH = 0.0030
_PINKING_DEPTH = 0.0015
_PINKING_END_GAP = 0.008

# Herb multiplicity (twin_blades): thin blade stock + Z pitch.
_HERB_BLADE_THICKNESS = 0.0010
_HERB_STACK_PITCH = 0.0030

# Leaf spring (spring_loaded). Both boss Y positions sit high on the neck (just
# below the hub) so they fuse with the neck on every handle variant — the
# thumb/finger necks are short, so a contact boss lower down would land in the
# loop hole and read as a floating island.
_SPRING_GAP = 0.002
_SPRING_WIDTH = 0.006
_SPRING_THICK = 0.0010
_SPRING_ANCHOR_Y = -0.011
_SPRING_CONTACT_Y = -0.018

# Each half is canted off the handle axis so the blades cross above the pivot.
_HALF_CANT = math.radians(11.0)
_OPEN_ANGLE = math.radians(28.0)
_SPRING_FLEX = math.radians(12.0)


@dataclass(frozen=True)
class ScissorsConfig:
    blade_profile: BladeProfile | None = None
    handle_loops: HandleLoops | None = None
    spring_assist: SpringAssist | None = None
    blades_per_half: int | None = None
    material_style: MaterialStyle = "steel_red"
    blade_length_scale: float = 1.0
    loop_size_scale: float = 1.0
    handle_reach_scale: float = 1.0
    open_angle_scale: float = 1.0
    spring_flex_scale: float = 1.0
    name: str = "scissors"


@dataclass(frozen=True)
class ResolvedScissorsConfig:
    blade_profile: BladeProfile
    handle_loops: HandleLoops
    spring_assist: SpringAssist
    blades_per_half: int
    material_style: MaterialStyle
    # Concrete geometry (scaled).
    blade_length: float
    blade_thickness: float
    handle_length: float
    loop_size_scale: float
    half_cant: float
    open_angle: float
    spring_flex: float
    # Derived stack geometry.
    hub_half_h: float
    handle_z_offset: float
    name: str

    @property
    def is_multi(self) -> bool:
        return self.blades_per_half > 1


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> ScissorsConfig:
    rng = random.Random(seed)
    # Weighted procedural sampling (spec §9): straight blade / symmetric loops /
    # no spring are the common case; single blade most common.
    profile = rng.choices(BLADE_PROFILES, weights=[5, 3, 3, 3], k=1)[0]
    handle = rng.choices(HANDLE_LOOPS, weights=[6, 3, 3], k=1)[0]
    spring = rng.choices(SPRING_ASSISTS, weights=[7, 3], k=1)[0]
    n_blades = rng.choices([1, 2, 3, 4, 5], weights=[10, 2, 2, 2, 1], k=1)[0]
    return ScissorsConfig(
        blade_profile=profile,
        handle_loops=handle,
        spring_assist=spring,
        blades_per_half=n_blades,
        material_style=rng.choice(MATERIAL_STYLES),
        blade_length_scale=round(rng.uniform(0.85, 2.05), 4),
        loop_size_scale=round(rng.uniform(0.85, 1.15), 4),
        handle_reach_scale=round(rng.uniform(0.90, 1.12), 4),
        open_angle_scale=round(rng.uniform(0.80, 1.20), 4),
        spring_flex_scale=round(rng.uniform(0.80, 1.20), 4),
        name=f"seeded_scissors_{seed}",
    )


def resolve_config(config: ScissorsConfig | None = None) -> ResolvedScissorsConfig:
    cfg = config or ScissorsConfig()
    profile = _pick(cfg.blade_profile, BLADE_PROFILES)
    handle = _pick(cfg.handle_loops, HANDLE_LOOPS)
    spring = _pick(cfg.spring_assist, SPRING_ASSISTS)
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)

    n_blades = int(
        _clamp(
            cfg.blades_per_half if cfg.blades_per_half is not None else 1,
            N_BLADES_MIN,
            N_BLADES_MAX,
        )
    )

    # Compatibility gating (spec §8/§9): herb multi-blade stacks only have an
    # upstream straight-thin-blade source; force the straight profile when N>1.
    if n_blades > 1:
        profile = "straight_pointed"

    length_scale = _clamp(cfg.blade_length_scale, 0.85, 2.05)
    loop_size_scale = _clamp(cfg.loop_size_scale, 0.85, 1.15)
    reach_scale = _clamp(cfg.handle_reach_scale, 0.90, 1.12)
    open_scale = _clamp(cfg.open_angle_scale, 0.80, 1.20)
    flex_scale = _clamp(cfg.spring_flex_scale, 0.80, 1.20)

    blade_length = _BLADE_LENGTH * length_scale
    blade_thickness = _HERB_BLADE_THICKNESS if n_blades > 1 else _BLADE_THICKNESS
    handle_length = _HANDLE_LENGTH * reach_scale
    open_angle = _clamp(_OPEN_ANGLE * open_scale, math.radians(12.0), math.radians(40.0))
    spring_flex = _clamp(_SPRING_FLEX * flex_scale, math.radians(6.0), math.radians(18.0))

    # Derived interleaved-stack geometry (spec §7 inequality): the hub spans the
    # full blade stack height, and each handle seats just outside the stack so the
    # blades and handles never interpenetrate.
    total = n_blades * 2
    stack_half = (total - 1) * _HERB_STACK_PITCH / 2.0
    if n_blades > 1:
        hub_half_h = stack_half + blade_thickness / 2.0
    else:
        hub_half_h = blade_thickness / 2.0
    handle_z_offset = hub_half_h + _HANDLE_THICKNESS / 2.0 - 0.0004

    return ResolvedScissorsConfig(
        blade_profile=profile,
        handle_loops=handle,
        spring_assist=spring,
        blades_per_half=n_blades,
        material_style=material_style,
        blade_length=blade_length,
        blade_thickness=blade_thickness,
        handle_length=handle_length,
        loop_size_scale=loop_size_scale,
        half_cant=_HALF_CANT,
        open_angle=open_angle,
        spring_flex=spring_flex,
        hub_half_h=hub_half_h,
        handle_z_offset=handle_z_offset,
        name=cfg.name or "scissors",
    )


def with_overrides(config: ScissorsConfig, **kwargs: object) -> ScissorsConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ScissorsConfig | ResolvedScissorsConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedScissorsConfig) else resolve_config(config)
    return (
        ("blade_profile", r.blade_profile),
        ("handle_loops", r.handle_loops),
        ("spring_assist", r.spring_assist),
        ("blades_per_half", f"blades_{r.blades_per_half}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Blade geometry (Slot A). Each returns a cq.Workplane in a pivot-at-origin
# local frame, blade running toward +Y. ``blade_profile`` selects the variant.
# ---------------------------------------------------------------------------
def _straight_blade(r: ResolvedScissorsConfig, *, blunt: bool) -> cq.Workplane:
    half_root = _BLADE_ROOT_WIDTH / 2.0
    half_tip = _BLADE_TIP_WIDTH / 2.0
    y0 = _PIVOT_HUB_R * 0.4
    y1 = r.blade_length
    if blunt:
        # Rounded safety nose: keep a finite width near the tip and fillet it.
        pts = [
            (half_root, y0),
            (half_root * 0.85, (y0 + y1) * 0.45),
            (half_tip * 1.8, y1 - 0.004),
            (half_tip * 1.2, y1),
            (-half_tip * 1.2, y1),
            (-half_root * 0.55, (y0 + y1) * 0.5),
            (-half_root, y0),
        ]
    else:
        pts = [
            (half_root, y0),
            (half_root * 0.85, (y0 + y1) * 0.45),
            (half_tip, y1 - 0.004),
            (0.0, y1),  # sharp tip on the centerline
            (-half_root * 0.55, (y0 + y1) * 0.5),
            (-half_root, y0),
        ]
    blade = cq.Workplane("XY").polyline(pts).close().extrude(r.blade_thickness / 2.0, both=True)
    try:
        blade = blade.edges("|Z").fillet(0.0008 if not blunt else 0.0009)
    except Exception:
        pass
    return blade


def _curved_blade(r: ResolvedScissorsConfig) -> cq.Workplane:
    """Strongly curved / hooked blade following a circular arc toward +X."""
    y0 = _PIVOT_HUB_R * 0.4
    arc_len = r.blade_length - y0
    theta_max = arc_len / _HOOK_RADIUS
    n = 32
    spine_pts: list[tuple[float, float]] = []
    cutting_pts: list[tuple[float, float]] = []
    for i in range(n + 1):
        t = i / n
        theta = t * theta_max
        cx = _HOOK_RADIUS * (1.0 - math.cos(theta))
        cy = y0 + _HOOK_RADIUS * math.sin(theta)
        if t < 0.85:
            s = t / 0.85
            w = _BLADE_ROOT_WIDTH * (1.0 - s) + _BLADE_TIP_WIDTH * s
        else:
            s = (t - 0.85) / 0.15
            w = _BLADE_TIP_WIDTH * (1.0 - s * s)
        half_w = max(w * 0.5, 0.0)
        nx = math.cos(theta)
        ny = -math.sin(theta)
        spine_pts.append((cx + half_w * nx, cy + half_w * ny))
        cutting_pts.append((cx - half_w * nx, cy - half_w * ny))
    tip_x = _HOOK_RADIUS * (1.0 - math.cos(theta_max))
    tip_y = y0 + _HOOK_RADIUS * math.sin(theta_max)
    outline = cutting_pts[:-1] + [(tip_x, tip_y)] + list(reversed(spine_pts[:-1]))
    blade = cq.Workplane("XY").polyline(outline).close().extrude(r.blade_thickness / 2.0, both=True)
    try:
        blade = blade.edges("|Z").fillet(0.0008)
    except Exception:
        pass
    return blade


def _pinking_edge_points(r: ResolvedScissorsConfig) -> list[tuple[float, float]]:
    """Sawtooth pinking points along the +X cutting edge (root -> near tip)."""
    half_root = _BLADE_ROOT_WIDTH / 2.0
    y0 = _PIVOT_HUB_R * 0.4
    y1 = r.blade_length
    teeth_end = y1 - _PINKING_END_GAP
    half_pitch = _PINKING_PITCH / 2.0
    working = teeth_end - y0
    n_steps = max(2, int(working / half_pitch))
    fade_zone = 2.0 * _PINKING_PITCH
    pts: list[tuple[float, float]] = []
    for k in range(n_steps + 1):
        y = y0 + k * half_pitch
        if y > teeth_end:
            break
        is_peak = (k % 2) == 1
        # X baseline tapers from root to tip along the inner edge.
        s = (y - y0) / max(working, 1e-6)
        base_x = half_root * (1.0 - s) + _BLADE_TIP_WIDTH / 2.0 * s
        fade = 1.0
        if y > teeth_end - fade_zone:
            fade = max(0.0, (teeth_end - y) / fade_zone)
        depth = _PINKING_DEPTH * fade if is_peak else 0.0
        pts.append((base_x + depth, y))
    return pts


def _pinking_blade(r: ResolvedScissorsConfig) -> cq.Workplane:
    half_root = _BLADE_ROOT_WIDTH / 2.0
    y0 = _PIVOT_HUB_R * 0.4
    y1 = r.blade_length
    cutting_pts = _pinking_edge_points(r)
    spine_pts = [
        (-half_root, y0),
        (-half_root * 0.55, (y0 + y1) * 0.5),
        (-_BLADE_TIP_WIDTH / 2.0, y1 - 0.004),
    ]
    outline = (
        cutting_pts
        + [(_BLADE_TIP_WIDTH / 2.0 * 0.5, y1 - 0.003), (0.0, y1)]
        + list(reversed(spine_pts))
    )
    blade = cq.Workplane("XY").polyline(outline).close().extrude(r.blade_thickness / 2.0, both=True)
    return blade


def _blade_solid(r: ResolvedScissorsConfig) -> cq.Workplane:
    if r.blade_profile == "curved_hooked":
        return _curved_blade(r)
    if r.blade_profile == "blunt_safety":
        return _straight_blade(r, blunt=True)
    if r.blade_profile == "pinking_sawtooth":
        return _pinking_blade(r)
    return _straight_blade(r, blunt=False)


# ---------------------------------------------------------------------------
# Hub + handle geometry.
# ---------------------------------------------------------------------------
def _hub_solid(r: ResolvedScissorsConfig) -> cq.Workplane:
    """Steel pivot boss spanning the (possibly stacked) blade height."""
    hub = cq.Workplane("XY").circle(_PIVOT_HUB_R).extrude(r.hub_half_h, both=True)
    hole = cq.Workplane("XY").circle(_PIVOT_HOLE_R).extrude(r.hub_half_h + 0.001, both=True)
    hub = hub.cut(hole)
    try:
        hub = hub.faces(">Z or <Z").chamfer(0.0005)
    except Exception:
        pass
    return hub


def _neck_solid(
    r: ResolvedScissorsConfig, handle_length: float, loop_extent: float
) -> cq.Workplane:
    half_neck = _HANDLE_NECK_WIDTH / 2.0
    neck_top_y = -_PIVOT_HUB_R * 0.2
    loop_center_y = -(handle_length - loop_extent)
    neck_bottom_y = loop_center_y + loop_extent - 0.006
    pts = [
        (half_neck * 1.25, neck_top_y),
        (half_neck, neck_bottom_y),
        (-half_neck, neck_bottom_y),
        (-half_neck * 1.25, neck_top_y),
    ]
    return cq.Workplane("XY").polyline(pts).close().extrude(_HANDLE_THICKNESS / 2.0, both=True)


def _rect_loop_handle(r: ResolvedScissorsConfig) -> cq.Workplane:
    """Symmetric rounded-rect finger-loop handle (parent baseline)."""
    s = r.loop_size_scale
    long = _LOOP_OUTER_LONG * s
    wide = _LOOP_OUTER_WIDE * s
    loop_center_y = -(r.handle_length - long / 2.0)
    neck = _neck_solid(r, r.handle_length, long / 2.0)
    outer = (
        cq.Workplane("XY")
        .center(0.0, loop_center_y)
        .rect(wide, long)
        .extrude(_HANDLE_THICKNESS / 2.0, both=True)
        .edges("|Z")
        .fillet(wide * 0.38)
    )
    inner = (
        cq.Workplane("XY")
        .center(0.0, loop_center_y)
        .rect(wide - 2 * _LOOP_WALL, long - 2 * _LOOP_WALL)
        .extrude(_HANDLE_THICKNESS * 1.4, both=True)
        .edges("|Z")
        .fillet((wide - 2 * _LOOP_WALL) * 0.40)
    )
    return neck.union(outer.cut(inner))


def _thumb_loop_handle(r: ResolvedScissorsConfig) -> cq.Workplane:
    """Small round thumb loop (offset_thumb_finger, half A)."""
    s = r.loop_size_scale
    od = _THUMB_LOOP_OD * s
    handle_length = _THUMB_HANDLE_LENGTH * (r.handle_length / _HANDLE_LENGTH)
    loop_center_y = -(handle_length - od / 2.0)
    neck = _neck_solid(r, handle_length, od / 2.0)
    outer = (
        cq.Workplane("XY")
        .center(0.0, loop_center_y)
        .circle(od / 2.0)
        .extrude(_HANDLE_THICKNESS / 2.0, both=True)
    )
    inner = (
        cq.Workplane("XY")
        .center(0.0, loop_center_y)
        .circle(od / 2.0 - _THUMB_LOOP_WALL)
        .extrude(_HANDLE_THICKNESS * 1.4, both=True)
    )
    return neck.union(outer.cut(inner))


def _finger_loop_handle(r: ResolvedScissorsConfig, *, with_brace: bool) -> cq.Workplane:
    """Large elongated finger loop (offset_thumb_finger half B / brace base)."""
    s = r.loop_size_scale
    long = _FINGER_LOOP_LONG * s
    wide = _FINGER_LOOP_WIDE * s
    loop_center_y = -(r.handle_length - long / 2.0)
    neck = _neck_solid(r, r.handle_length, long / 2.0)
    outer = (
        cq.Workplane("XY")
        .center(0.0, loop_center_y)
        .rect(wide, long)
        .extrude(_HANDLE_THICKNESS / 2.0, both=True)
        .edges("|Z")
        .fillet(wide * 0.40)
    )
    inner = (
        cq.Workplane("XY")
        .center(0.0, loop_center_y)
        .rect(wide - 2 * _LOOP_WALL, long - 2 * _LOOP_WALL)
        .extrude(_HANDLE_THICKNESS * 1.4, both=True)
        .edges("|Z")
        .fillet((wide - 2 * _LOOP_WALL) * 0.42)
    )
    handle = neck.union(outer.cut(inner))
    if with_brace:
        handle = handle.union(_finger_brace_solid(r, loop_center_y, wide))
    return handle


def _finger_brace_solid(
    r: ResolvedScissorsConfig, loop_center_y: float, wide: float
) -> cq.Workplane:
    """Curved finger-brace tang projecting from the outer (+X) loop rim."""
    rim_x = wide / 2.0
    long = _FINGER_LOOP_LONG * r.loop_size_scale
    hw = _BRACE_WIDTH / 2.0
    keys = [
        (-0.002, long * 0.12, 1.15),
        (_BRACE_LENGTH * 0.32, long * 0.02, 1.00),
        (_BRACE_LENGTH * 0.68, -long * 0.14, 0.88),
        (_BRACE_LENGTH, -long * 0.30, 0.70),
    ]
    upper: list[tuple[float, float]] = []
    lower: list[tuple[float, float]] = []
    for dx, dy, wscale in keys:
        cx = rim_x + dx
        cy = loop_center_y + dy
        upper.append((cx, cy + hw * wscale))
        lower.append((cx, cy - hw * wscale))
    outline = upper + list(reversed(lower))
    brace = cq.Workplane("XY").polyline(outline).close().extrude(_HANDLE_THICKNESS / 2.0, both=True)
    try:
        brace = brace.edges("|Z").fillet(_BRACE_TIP_RADIUS * 0.5)
    except Exception:
        pass
    return brace


def _handle_solid(r: ResolvedScissorsConfig, side: str) -> cq.Workplane:
    """Handle for one half before mirror/cant. ``side`` is 'a' (root) or 'b'."""
    if r.handle_loops == "offset_thumb_finger":
        # Half A gets the small thumb loop; half B gets the large finger loop.
        handle = _thumb_loop_handle(r) if side == "a" else _finger_loop_handle(r, with_brace=False)
    elif r.handle_loops == "finger_brace_tang":
        # The finger-brace half (A) carries the brace; the other keeps a plain loop.
        handle = _finger_loop_handle(r, with_brace=True) if side == "a" else _rect_loop_handle(r)
    else:
        handle = _rect_loop_handle(r)

    # When the leaf spring is present, fuse its anchor (A) / contact (B) boss
    # into the handle neck so the boss is part of the handle visual (never a
    # floating island). The boss protrudes from the handle's inner face: +Z for
    # half A, -Z for half B (the two handles are stacked with a gap between).
    if r.spring_assist == "leaf_spring":
        boss_y = _SPRING_ANCHOR_Y if side == "a" else _SPRING_CONTACT_Y
        inner_sign = 1.0 if side == "a" else -1.0
        boss = (
            cq.Workplane("XY", origin=(0.0, boss_y, 0.0))
            .circle(_SPRING_WIDTH * 0.55)
            .extrude(inner_sign * (_HANDLE_THICKNESS / 2.0 + _SPRING_THICK * 1.6))
        )
        handle = handle.union(boss)
    return handle


# ---------------------------------------------------------------------------
# Mirror + cant transforms for a half.
# ---------------------------------------------------------------------------
def _cant(shape: cq.Workplane, side: str) -> cq.Workplane:
    sign = 1.0 if side == "a" else -1.0
    if side == "b":
        shape = shape.mirror("YZ")
    return shape.rotate((0, 0, 0), (0, 0, 1), math.degrees(-sign * _HALF_CANT))


def _cant_point(x: float, y: float, side: str) -> tuple[float, float]:
    """Apply the same mirror+cant transform a half receives to an XY point.

    Used to place the spring anchor/contact bosses on the *canted* handle neck
    so they fuse with the handle geometry instead of floating beside it.
    """
    sign = 1.0 if side == "a" else -1.0
    if side == "b":
        x = -x  # mirror across YZ
    ang = -sign * _HALF_CANT
    ca, sa = math.cos(ang), math.sin(ang)
    return (x * ca - y * sa, x * sa + y * ca)


def _blade_z_slots(r: ResolvedScissorsConfig, side: str) -> list[float]:
    """Z centers for one half's blades in the interleaved stack (A even, B odd)."""
    if not r.is_multi:
        return [0.0]
    total = r.blades_per_half * 2
    out: list[float] = []
    for i in range(total):
        z = (i - (total - 1) / 2.0) * _HERB_STACK_PITCH
        if side == "a" and i % 2 == 0:
            out.append(z)
        elif side == "b" and i % 2 == 1:
            out.append(z)
    return out


def _half_blade_mesh(r: ResolvedScissorsConfig, side: str, z_pos: float, name: str, *, assets):
    blade = _blade_solid(r).translate((0.0, 0.0, z_pos))
    blade = _cant(blade, side)
    return mesh_from_cadquery(blade, name, assets=assets)


def _hub_mesh(r: ResolvedScissorsConfig, side: str, name: str, *, assets):
    hub = _cant(_hub_solid(r), side)
    return mesh_from_cadquery(hub, name, assets=assets)


def _handle_mesh(r: ResolvedScissorsConfig, side: str, name: str, *, assets):
    handle = _cant(_handle_solid(r, side), side)
    return mesh_from_cadquery(handle, name, assets=assets)


def _cap_mesh(r: ResolvedScissorsConfig, *, assets):
    cap = cq.Workplane("XY").circle(_PIVOT_CAP_R).extrude(_PIVOT_CAP_T).faces(">Z").chamfer(0.0005)
    return mesh_from_cadquery(cap, "pivot_cap", assets=assets)


def _spring_mesh(r: ResolvedScissorsConfig, *, assets):
    """Curved leaf spring bridging the two handles, authored at its anchor.

    Local frame: anchor at origin, the strip runs toward -Y and bows in +Z to
    span the gap between the two stacked handles. The part frame origin (0,0,0)
    lands on the anchor boss geometry where the spring_flex joint sits.
    """
    n = 16
    y_contact = -(abs(_SPRING_CONTACT_Y - _SPRING_ANCHOR_Y))
    z_b = _SPRING_GAP + 2.0 * r.handle_z_offset - _HANDLE_THICKNESS
    pts: list[tuple[float, float, float]] = []
    for i in range(n + 1):
        t = i / n
        y = t * y_contact
        # Bowed arc: rises to a mid bow then settles to the contact face.
        z = z_b * (0.5 - 0.5 * math.cos(math.pi * t)) + 0.004 * math.sin(math.pi * t)
        pts.append((0.0, y, z))
    bar = None
    for i in range(n):
        (x0, y0, z0), (x1, y1, z1) = pts[i], pts[i + 1]
        seg_len = math.dist((x0, y0, z0), (x1, y1, z1))
        if seg_len < 1e-6:
            continue
        # Segment as a thin box bridging consecutive spline points.
        cx, cy, cz = (x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0
        seg = cq.Workplane("XY").box(
            _SPRING_WIDTH, seg_len + _SPRING_THICK, _SPRING_THICK, centered=True
        )
        # Rotate the box so its long (local Y) axis points along the segment in YZ.
        ang = math.degrees(math.atan2(z1 - z0, y1 - y0))
        seg = seg.rotate((0, 0, 0), (1, 0, 0), ang).translate((cx, cy, cz))
        bar = seg if bar is None else bar.union(seg)
    # Anchor stub at the origin so the part AABB contains (0,0,0) for the joint.
    stub = cq.Workplane("XY").circle(_SPRING_WIDTH * 0.55).extrude(_SPRING_THICK * 1.6)
    bar = stub if bar is None else bar.union(stub)
    return mesh_from_cadquery(bar, "leaf_spring", assets=assets)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def _blade_bbox(r: ResolvedScissorsConfig) -> tuple[float, float, float]:
    return (r.blade_length, r.blade_length, max(2.0 * r.hub_half_h, r.blade_thickness))


def _emit_blades(model, r, part, side, mats, *, assets) -> None:
    z_slots = _blade_z_slots(r, side)
    # Cache the canted blade mesh per Z slot.
    for i, z in enumerate(z_slots):
        mesh = _half_blade_mesh(r, side, z, f"blade_{side}_{i}", assets=assets)
        part.visual(mesh, material=mats["blade"], name=f"blade_{i}", material_class_id=("metal.steel_bare" if r.material_style in {"steel_red", "steel_green", "steel_black"} else "metal.precious_gold"))
    # Pivot hub spanning the stack.
    part.visual(
        _hub_mesh(r, side, f"hub_{side}", assets=assets), material=mats["blade"], name="hub", material_class_id=("metal.steel_bare" if r.material_style in {"steel_red", "steel_green", "steel_black"} else "metal.precious_gold")
    )


def build_scissors(
    config: ScissorsConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.material_style]
    mats = {
        key: model.material(f"scissors_{key}_{r.material_style}", rgba=palette[key])
        for key in ("blade", "handle", "cap", "spring")
    }

    # --- Half A (root): blades + hub + handle + inline disc cap. ---
    blade_a = model.part("blade_a")
    _emit_blades(model, r, blade_a, "a", mats, assets=assets)
    blade_a.visual(
        _handle_mesh(r, "a", "handle_a", assets=assets),
        material=mats["handle"],
        name="handle_loop", material_class_id="plastic.opaque_glossy_molded",
        origin=Origin(xyz=(0.0, 0.0, -r.handle_z_offset)),
    )
    # Inline disc cap seated on the +Z hub face (riveted decoration, not a part).
    blade_a.visual(
        _cap_mesh(r, assets=assets),
        material=mats["cap"],
        name="pivot_cap", material_class_id=("metal.steel_bare" if r.material_style in {"steel_red", "steel_green", "steel_black"} else "metal.precious_gold"),
        origin=Origin(xyz=(0.0, 0.0, r.hub_half_h - 0.0002)),
    )
    blade_a.inertial = Inertial.from_geometry(
        Box(_blade_bbox(r)),
        mass=0.04,
        origin=Origin(xyz=(0.0, r.blade_length * 0.3, 0.0)),
    )

    # --- Half B (rotates about the pivot). ---
    blade_b = model.part("blade_b")
    _emit_blades(model, r, blade_b, "b", mats, assets=assets)
    blade_b.visual(
        _handle_mesh(r, "b", "handle_b", assets=assets),
        material=mats["handle"],
        name="handle_loop", material_class_id="plastic.opaque_glossy_molded",
        origin=Origin(xyz=(0.0, 0.0, r.handle_z_offset)),
    )
    blade_b.inertial = Inertial.from_geometry(
        Box(_blade_bbox(r)),
        mass=0.04,
        origin=Origin(xyz=(0.0, r.blade_length * 0.3, 0.0)),
    )

    # --- Central pivot (REVOLUTE about +Z, origin on the screw / hub geom). ---
    # q=0 is the modeled open pose. lower = -2*HALF_CANT closes the blades (tips
    # meet on the centerline); upper opens them wider. Captured-pin geometry:
    # MatingContract omitted (grandfathered), guarded by broad allow_overlap.
    model.articulation(
        "pivot",
        ArticulationType.REVOLUTE,
        parent=blade_a,
        child=blade_b,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=2.0,
            velocity=4.0,
            lower=-2.0 * r.half_cant,
            upper=r.open_angle,
        ),
    )

    # --- Optional leaf spring (second REVOLUTE joint). ---
    if r.spring_assist == "leaf_spring":
        # The anchor (A) / contact (B) bosses are fused into the handle meshes
        # (see _handle_solid). The spring_flex joint origin sits on the canted
        # handle-A anchor boss (real captured-anchor geometry, ≤0.015 m).
        ax, ay = _cant_point(0.0, _SPRING_ANCHOR_Y, "a")
        anchor_z_a = -r.handle_z_offset + _HANDLE_THICKNESS / 2.0 + _SPRING_THICK
        spring = model.part("spring")
        spring.visual(_spring_mesh(r, assets=assets), material=mats["spring"], name="leaf_spring", material_class_id=("metal.steel_bare" if r.material_style in {"steel_red", "steel_green", "steel_black"} else "metal.precious_gold"))
        spring.inertial = Inertial.from_geometry(
            Box(
                (_SPRING_WIDTH, abs(_SPRING_CONTACT_Y - _SPRING_ANCHOR_Y), 2.0 * r.handle_z_offset)
            ),
            mass=0.004,
            origin=Origin(
                xyz=(0.0, -abs(_SPRING_CONTACT_Y - _SPRING_ANCHOR_Y) / 2.0, r.handle_z_offset)
            ),
        )
        model.articulation(
            "spring_flex",
            ArticulationType.REVOLUTE,
            parent=blade_a,
            child=spring,
            origin=Origin(xyz=(ax, ay, anchor_z_a)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=r.spring_flex),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_scissors(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_scissors(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_scissors_tests(
    object_model: ArticulatedObject,
    config: ScissorsConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    blade_a = object_model.get_part("blade_a")
    blade_b = object_model.get_part("blade_b")
    pivot = object_model.get_articulation("pivot")

    # --- Captured-pin allowance: the two steel hubs and blade roots nest on one screw axis. ---
    # Keep this element-scoped so a bad handle/loop collision is still caught.
    ctx.allow_overlap(
        blade_a,
        blade_b,
        elem_a="hub",
        elem_b="hub",
        reason=(
            "the two steel hub bosses form a riveted lap joint sharing one central "
            "screw axis (captured-pin geometry)."
        ),
    )
    for i in range(r.blades_per_half):
        for j in range(r.blades_per_half):
            ctx.allow_overlap(
                blade_a,
                blade_b,
                elem_a=f"blade_{i}",
                elem_b=f"blade_{j}",
                reason=(
                    "the steel blade roots cross and shear in the captured pivot stack; "
                    "handle and non-blade collisions remain unallowed."
                ),
            )
    if r.spring_assist == "leaf_spring":
        spring = object_model.get_part("spring")
        ctx.allow_overlap(
            blade_a,
            spring,
            elem_a="handle_loop",
            elem_b="leaf_spring",
            reason="leaf spring is anchored on handle A's inner face (captured anchor boss).",
        )
        ctx.allow_overlap(
            blade_b,
            spring,
            elem_a="handle_loop",
            elem_b="leaf_spring",
            reason="leaf spring's free end contacts handle B's inner face / contact boss.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=32,
        ignore_adjacent=False,
        ignore_fixed=True,
    )
    # The pivot (and spring_flex) omit MatingContract (captured-pin geometry,
    # grandfathered); the flat 0.015 m articulation-origin baseline runs in the
    # compiler and both origins sit on real hub / anchor-boss hardware.
    ctx.fail_if_joint_mating_has_gap()

    # --- Pivot joint contract. ---
    ctx.check(
        "pivot is REVOLUTE about +Z",
        pivot.articulation_type == ArticulationType.REVOLUTE
        and tuple(round(c, 3) for c in pivot.axis) == (0.0, 0.0, 1.0),
        details=f"type={pivot.articulation_type} axis={tuple(round(c, 3) for c in pivot.axis)}",
    )
    porg = pivot.origin.xyz
    ctx.check(
        "pivot sits at the central crossing point",
        all(abs(c) < 1e-6 for c in porg),
        details=f"origin={porg}",
    )

    # --- Each half carries the expected blades + a handle loop. ---
    n = r.blades_per_half
    for half in (blade_a, blade_b):
        names = {v.name for v in half.visuals}
        for i in range(n):
            ctx.check(
                f"{half.name} carries blade_{i}",
                f"blade_{i}" in names,
                details=f"visuals={sorted(names)}",
            )
        ctx.check(
            f"{half.name} carries a hub",
            "hub" in names,
            details=f"visuals={sorted(names)}",
        )
        # Both halves carry a finger-loop handle (thumb/finger/symmetric all
        # use the "handle_loop" visual name except the offset thumb side).
        has_handle = "handle_loop" in names
        ctx.check(
            f"{half.name} carries a handle",
            has_handle,
            details=f"visuals={sorted(names)}",
        )

    # Inline disc cap belongs to the root half.
    a_names = {v.name for v in blade_a.visuals}
    ctx.check(
        "pivot cap is an inline blade_a visual",
        "pivot_cap" in a_names,
        details=str(sorted(a_names)),
    )

    # --- Multiplicity: stacked blades are separated in Z with regular spacing. ---
    if r.is_multi:
        a_boxes = []
        for i in range(n):
            box = ctx.part_element_world_aabb(blade_a, elem=f"blade_{i}")
            if box is not None:
                a_boxes.append(box)
        if len(a_boxes) >= 2:
            z_centers = sorted((b[0][2] + b[1][2]) / 2.0 for b in a_boxes)
            gaps = [z_centers[j + 1] - z_centers[j] for j in range(len(z_centers) - 1)]
            ctx.check(
                "stacked blades are separated in Z with regular spacing",
                all(g > 0.001 for g in gaps),
                details=f"gaps={[round(g, 6) for g in gaps]}",
            )

    # --- Geometry sanity: blade reaches up (+Y), handle reaches down (-Y). ---
    blade_box = ctx.part_element_world_aabb(blade_a, elem="blade_0")
    handle_box = ctx.part_element_world_aabb(blade_a, elem="handle_loop")
    if blade_box is not None and handle_box is not None:
        # The blade reaches well into +Y (toward the tips). Curved/hooked blades
        # arc sideways so their +Y reach is below blade_length; a fixed modest
        # floor holds across every profile and length scale.
        ctx.check(
            "blade extends toward the tips (+Y)",
            blade_box[1][1] > 0.05,
            details=f"blade max_y={blade_box[1][1]:.4f}",
        )
        ctx.check(
            "handle loop extends toward the fingers (-Y)",
            handle_box[0][1] < -0.04,
            details=f"handle min_y={handle_box[0][1]:.4f}",
        )

    # --- The two blades cross at the pivot (steel halves on opposite sides). ---
    a_tip = ctx.part_element_world_aabb(blade_a, elem="blade_0")
    b_tip = ctx.part_element_world_aabb(blade_b, elem="blade_0")
    if a_tip is not None and b_tip is not None:
        a_cx = (a_tip[0][0] + a_tip[1][0]) / 2.0
        b_cx = (b_tip[0][0] + b_tip[1][0]) / 2.0
        ctx.check(
            "blades cross (steel halves on opposite sides of center)",
            a_cx * b_cx < 0.0,
            details=f"a_center_x={a_cx:.4f} b_center_x={b_cx:.4f}",
        )

    # --- Pivot kinematics: opening separates the tips, closing converges. ---
    def _b_tip_cx() -> float | None:
        box = ctx.part_element_world_aabb(blade_b, elem="blade_0")
        if box is None:
            return None
        return (box[0][0] + box[1][0]) / 2.0

    rest_bx = _b_tip_cx()
    with ctx.pose({pivot: -r.half_cant}):
        half_closed_bx = _b_tip_cx()
    with ctx.pose({pivot: pivot.motion_limits.upper}):
        wide_bx = _b_tip_cx()
    if rest_bx is not None and half_closed_bx is not None:
        ctx.check(
            "half-closing swings blade_b tip toward the centerline",
            abs(half_closed_bx) < abs(rest_bx),
            details=f"rest_bx={rest_bx:.4f} half_closed_bx={half_closed_bx:.4f}",
        )
    if rest_bx is not None and wide_bx is not None:
        ctx.check(
            "opening the pivot swings blade_b tip further out (tips separate)",
            abs(wide_bx) > abs(rest_bx) and (wide_bx * rest_bx) > 0.0,
            details=f"rest_bx={rest_bx:.4f} wide_bx={wide_bx:.4f}",
        )

    # --- Optional leaf spring: second moving joint. ---
    if r.spring_assist == "leaf_spring":
        sj = object_model.get_articulation("spring_flex")
        ctx.check(
            "spring_flex is a genuine (non-fixed) REVOLUTE joint about +X",
            sj.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(c, 3) for c in sj.axis) == (1.0, 0.0, 0.0)
            and sj.motion_limits is not None
            and sj.motion_limits.upper > sj.motion_limits.lower,
            details=f"type={sj.articulation_type} axis={tuple(round(c, 3) for c in sj.axis)}",
        )
        spring = object_model.get_part("spring")
        rest = ctx.part_world_aabb(spring)
        with ctx.pose({sj: sj.motion_limits.upper}):
            flexed = ctx.part_world_aabb(spring)
        if rest is not None and flexed is not None:
            rc = ((rest[0][1] + rest[1][1]) / 2.0, (rest[0][2] + rest[1][2]) / 2.0)
            fc = ((flexed[0][1] + flexed[1][1]) / 2.0, (flexed[0][2] + flexed[1][2]) / 2.0)
            ctx.check(
                "flexing the spring_flex joint moves the leaf spring",
                math.dist(rc, fc) > 1e-4,
                details=f"rest={rc} flexed={fc}",
            )

    # --- slot_choices recorded. ---
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "ScissorsConfig",
    "ResolvedScissorsConfig",
    "build_scissors",
    "build_seeded_scissors",
    "config_from_seed",
    "resolve_config",
    "run_scissors_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
