# SPDX-License-Identifier: Apache-2.0

"""Telescoping pointer — modular procedural template (0611/telescoping_pointer).

Spec: articraft_template_authoring/specs_modular_v1/telescoping_pointer.md
Pattern: mixed — linear multiplicity chain (grip → N stages → tip) with an
optional parallel-child REVOLUTE pocket clip on the grip.

Slots (§spec 4):
  * ``body_form`` (2): ``foam_grip_body`` (S1 baseline, r=0.0108, GRIP_TOP=0.190)
    / ``pen_style_body`` (S7 slim, r=0.0048, GRIP_TOP=0.135, static pocket clip).
  * ``stage_count`` (multiplicity 4): 2 / 3 / 4 / 5 nested PRISMATIC(+Z) tubes,
    each tube's shaft/collar drawn from the S1-S4 shared helpers.
  * ``tip_form`` (4): ``rounded_stem_tip`` (S1, Volumetric Envelope Form),
    ``ball_tip`` (S5, Volumetric Envelope Form),
    ``hand_silhouette_tip`` (S6, Planar Boundary Form — flat plate),
    ``flat_disc_tip`` (world_knowledge, Planar Boundary Form — disc).
  * ``secondary`` (2): ``none`` / ``hinged_pocket_clip`` (S9 REVOLUTE(-Y) clip
    child of ``grip``, 0..0.55 rad).
  * ``lock`` (2): ``rubber_bushings`` (S1 hidden dark_rubber guides) /
    ``twist_collars`` (S8 exposed matte-black collar overlays at each junction).

Palette (⑥ axis, 5 realistic styles): office_black / chrome_business /
matte_industrial / retail_bronze / student_bright.

Mating model: the PRISMATIC nested-tube joints are deliberately
**grandfathered** — telescoping tubes slide inside one another with the guide
bushing capturing the child radially, so there is no clean axis-aligned face
contact for ``fail_if_joint_mating_has_gap`` to verify (same rationale as
``threestage_telescoping_slide``). We omit ``mating=`` on those joints and use
element-scoped ``ctx.allow_overlap(...)`` in run_tests for the intentional
guide↔tube overlap. The ``grip_to_clip`` REVOLUTE joint does declare a real
``MatingContract`` between the ``clip_mount`` visual on the grip and the
``clip_barrel`` visual on the clip part.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True


# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------
BodyForm = Literal["foam_grip_body", "pen_style_body"]
TipForm = Literal[
    "rounded_stem_tip",
    "ball_tip",
    "hand_silhouette_tip",
    "flat_disc_tip",
]
Secondary = Literal["none", "hinged_pocket_clip"]
Lock = Literal["rubber_bushings", "twist_collars"]
PaletteStyle = Literal[
    "office_black",
    "chrome_business",
    "matte_industrial",
    "retail_bronze",
    "student_bright",
]

BODY_FORMS: tuple[BodyForm, ...] = ("foam_grip_body", "pen_style_body")
STAGE_COUNTS: tuple[int, ...] = (2, 3, 4, 5)
# Weights: 3 most common, 2/4 next, 5 rare.
STAGE_COUNT_WEIGHTS: tuple[float, ...] = (0.25, 0.40, 0.25, 0.10)
TIP_FORMS: tuple[TipForm, ...] = (
    "rounded_stem_tip",
    "ball_tip",
    "hand_silhouette_tip",
    "flat_disc_tip",
)
SECONDARIES: tuple[Secondary, ...] = ("none", "hinged_pocket_clip")
LOCKS: tuple[Lock, ...] = ("rubber_bushings", "twist_collars")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "office_black",
    "chrome_business",
    "matte_industrial",
    "retail_bronze",
    "student_bright",
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "office_black": {
        "grip": (0.025, 0.026, 0.028, 1.0),
        "grip_trim": (0.015, 0.016, 0.018, 1.0),
        "metal_a": (0.73, 0.75, 0.76, 1.0),
        "metal_b": (0.84, 0.85, 0.84, 1.0),
        "tip": (0.82, 0.78, 0.68, 1.0),
        "lock": (0.06, 0.06, 0.07, 1.0),
        "clip": (0.42, 0.44, 0.46, 1.0),
    },
    "chrome_business": {
        "grip": (0.035, 0.036, 0.040, 1.0),
        "grip_trim": (0.020, 0.022, 0.025, 1.0),
        "metal_a": (0.78, 0.80, 0.82, 1.0),
        "metal_b": (0.88, 0.89, 0.90, 1.0),
        "tip": (0.82, 0.72, 0.42, 1.0),
        "lock": (0.10, 0.10, 0.12, 1.0),
        "clip": (0.62, 0.63, 0.64, 1.0),
    },
    "matte_industrial": {
        "grip": (0.10, 0.10, 0.11, 1.0),
        "grip_trim": (0.06, 0.06, 0.07, 1.0),
        "metal_a": (0.36, 0.38, 0.40, 1.0),
        "metal_b": (0.52, 0.53, 0.55, 1.0),
        "tip": (0.15, 0.15, 0.16, 1.0),
        "lock": (0.04, 0.04, 0.05, 1.0),
        "clip": (0.30, 0.31, 0.33, 1.0),
    },
    "retail_bronze": {
        "grip": (0.34, 0.28, 0.20, 1.0),
        "grip_trim": (0.18, 0.14, 0.10, 1.0),
        "metal_a": (0.62, 0.46, 0.24, 1.0),
        "metal_b": (0.82, 0.68, 0.36, 1.0),
        "tip": (0.94, 0.78, 0.36, 1.0),
        "lock": (0.22, 0.16, 0.10, 1.0),
        "clip": (0.66, 0.52, 0.30, 1.0),
    },
    "student_bright": {
        "grip": (0.72, 0.14, 0.14, 1.0),
        "grip_trim": (0.30, 0.05, 0.05, 1.0),
        "metal_a": (0.75, 0.76, 0.77, 1.0),
        "metal_b": (0.86, 0.86, 0.85, 1.0),
        "tip": (0.82, 0.78, 0.68, 1.0),
        "lock": (0.06, 0.06, 0.07, 1.0),
        "clip": (0.42, 0.44, 0.46, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Reference geometry (all lengths in meters).
# ---------------------------------------------------------------------------
# S1 baseline foam grip.
_FOAM_GRIP_RADIUS = 0.0108
_FOAM_GRIP_LEN = 0.190
_FOAM_GRIP_SOCKET_R = 0.00525
_FOAM_GRIP_SOCKET_LEN = 0.095
_FOAM_GRIP_SOCKET_START = 0.100
_FOAM_END_CAP_R = 0.0095

# S7 pen-style barrel.
_PEN_GRIP_RADIUS = 0.0048
_PEN_GRIP_LEN = 0.135
_PEN_GRIP_SOCKET_R = 0.00370
_PEN_GRIP_SOCKET_LEN = 0.062
_PEN_GRIP_SOCKET_START = 0.076
_PEN_END_CAP_R = 0.0046

# Stage 0 (outermost) shaft/collar dims from S1.
_STAGE0_SHAFT_OUTER_R = 0.00445
_STAGE0_SHAFT_INNER_R = 0.00365
_STAGE0_SHAFT_LEN = 0.068
_STAGE0_SHAFT_Z0 = -0.028  # relative to joint origin at parent-top
_STAGE0_COLLAR_LO_R = 0.00530
_STAGE0_COLLAR_HI_R = 0.00435
_STAGE0_COLLAR_INNER_R = 0.00355
_STAGE0_COLLAR_BASE_LEN = 0.004
_STAGE0_COLLAR_BASE_Z = 0.033
_STAGE0_COLLAR_TAPER_LEN = 0.008
_STAGE0_COLLAR_TAPER_Z = 0.037

# S1 base travels; scaled per-stage below.
_BASE_TRAVELS = (0.025, 0.018, 0.014, 0.010, 0.008)
_BASE_JOINT_Z = (0.040, 0.030, 0.024, 0.020)  # child-local joint z, for stage_i→i+1


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TelescopingPointerConfig:
    body_form: BodyForm | None = None
    stage_count: int | None = None
    tip_form: TipForm | None = None
    secondary: Secondary | None = None
    lock: Lock | None = None
    palette_style: PaletteStyle | None = None
    grip_length_scale: float = 1.0
    stage_ratio: float = 0.78
    travel_scale: float = 1.0
    clip_open_scale: float = 1.0
    name: str = "telescoping_pointer"


@dataclass(frozen=True)
class ResolvedTelescopingPointerConfig:
    body_form: BodyForm
    stage_count: int
    tip_form: TipForm
    secondary: Secondary
    lock: Lock
    palette_style: PaletteStyle
    grip_length_scale: float
    stage_ratio: float
    travel_scale: float
    clip_open_scale: float
    # Derived:
    grip_radius: float
    grip_length: float
    grip_socket_r: float
    grip_socket_len: float
    grip_socket_start: float
    end_cap_r: float
    grip_top: float
    # Per-stage geometry (length == stage_count).
    stage_outer_r: tuple[float, ...]
    stage_inner_r: tuple[float, ...]
    stage_shaft_len: tuple[float, ...]
    # Joint z-offset in parent local frame for grip→stage_0 and stage_i→stage_{i+1}.
    joint_z_offsets: tuple[float, ...]  # len == stage_count
    stage_travels: tuple[float, ...]  # len == stage_count
    # Clip:
    clip_lower: float
    clip_upper: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


def config_from_seed(seed: int) -> TelescopingPointerConfig:
    rng = random.Random(seed)
    body = rng.choice(BODY_FORMS)
    # Weighted stage_count.
    r = rng.random()
    acc = 0.0
    stage_count = STAGE_COUNTS[-1]
    for n, w in zip(STAGE_COUNTS, STAGE_COUNT_WEIGHTS):
        acc += w
        if r <= acc:
            stage_count = n
            break
    tip = rng.choice(TIP_FORMS)
    secondary = rng.choice(SECONDARIES)
    lock = rng.choice(LOCKS)
    palette = rng.choice(PALETTE_STYLES)
    return TelescopingPointerConfig(
        body_form=body,
        stage_count=stage_count,
        tip_form=tip,
        secondary=secondary,
        lock=lock,
        palette_style=palette,
        grip_length_scale=round(rng.uniform(0.90, 1.10), 4),
        stage_ratio=round(rng.uniform(0.74, 0.82), 4),
        travel_scale=round(rng.uniform(0.85, 1.15), 4),
        clip_open_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_telescoping_pointer_{seed}",
    )


def resolve_config(
    config: TelescopingPointerConfig | None = None,
) -> ResolvedTelescopingPointerConfig:
    cfg = config or TelescopingPointerConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    stage_count = cfg.stage_count if cfg.stage_count in STAGE_COUNTS else 3
    tip_form = _pick(cfg.tip_form, TIP_FORMS)
    secondary = _pick(cfg.secondary, SECONDARIES)
    lock = _pick(cfg.lock, LOCKS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    grip_length_scale = _clamp(cfg.grip_length_scale, 0.90, 1.10)
    stage_ratio = _clamp(cfg.stage_ratio, 0.72, 0.82)
    travel_scale = _clamp(cfg.travel_scale, 0.85, 1.15)
    clip_open_scale = _clamp(cfg.clip_open_scale, 0.85, 1.15)

    if body_form == "foam_grip_body":
        grip_radius = _FOAM_GRIP_RADIUS
        grip_length = _FOAM_GRIP_LEN * grip_length_scale
        grip_socket_r = _FOAM_GRIP_SOCKET_R
        grip_socket_len = _FOAM_GRIP_SOCKET_LEN * grip_length_scale
        grip_socket_start = _FOAM_GRIP_SOCKET_START * grip_length_scale
        end_cap_r = _FOAM_END_CAP_R
    else:  # pen_style_body
        grip_radius = _PEN_GRIP_RADIUS
        grip_length = _PEN_GRIP_LEN * grip_length_scale
        grip_socket_r = _PEN_GRIP_SOCKET_R
        grip_socket_len = _PEN_GRIP_SOCKET_LEN * grip_length_scale
        grip_socket_start = _PEN_GRIP_SOCKET_START * grip_length_scale
        end_cap_r = _PEN_END_CAP_R
    grip_top = grip_length

    # Per-stage radii: stage_i.outer_r = base_r * stage_ratio^i, keeping the
    # invariant `stage_{i+1}.outer_r + clearance < stage_i.inner_r`.
    # stage_0.outer_r is DERIVED from the grip socket radius (Contract 3c:
    # single-sourced): tube must nest inside the socket bore with a clearance
    # gap. This keeps `expect_within` valid across both body_form candidates
    # (foam grip_r=0.0108 vs pen grip_r=0.0048).
    outer_r_list: list[float] = []
    inner_r_list: list[float] = []
    shaft_len_list: list[float] = []
    stage0_outer_target = min(_STAGE0_SHAFT_OUTER_R, grip_socket_r - 0.0006)
    stage0_outer_target = max(0.0025, stage0_outer_target)
    stage0_inner_target = max(0.0015, stage0_outer_target * 0.80)
    outer_r = stage0_outer_target
    inner_r = stage0_inner_target
    shaft_len = _STAGE0_SHAFT_LEN * grip_length_scale
    for i in range(stage_count):
        outer_r_list.append(outer_r)
        inner_r_list.append(inner_r)
        shaft_len_list.append(shaft_len)
        # Prepare next stage — strictly nested inside current stage's bore.
        next_outer = min(outer_r * stage_ratio, inner_r - 0.00025)
        next_outer = max(0.0006, next_outer)
        # Ensure strict monotonic decrease so downstream stages nest inside.
        if next_outer > outer_r - 0.00005:
            next_outer = outer_r * 0.90
        next_inner = max(0.0004, next_outer * 0.78)
        outer_r = next_outer
        inner_r = next_inner
        shaft_len = shaft_len * 0.88

    # Joint z offsets. Joint 0 is grip→stage_0 with origin at grip_top.
    # Subsequent joints stage_i → stage_{i+1} have origin ≈ parent-local
    # (0,0,0.040) style; we use _BASE_JOINT_Z scaled with grip_length_scale.
    joint_offsets: list[float] = [grip_top]
    for i in range(stage_count - 1):
        z = _BASE_JOINT_Z[min(i, len(_BASE_JOINT_Z) - 1)] * grip_length_scale
        joint_offsets.append(z)
    # travels
    travels_list: list[float] = []
    for i in range(stage_count):
        base = _BASE_TRAVELS[min(i, len(_BASE_TRAVELS) - 1)]
        t = base * travel_scale
        # Cap so travel keeps retention: t <= shaft_len_list[i] * 0.5.
        t = min(t, shaft_len_list[i] * 0.45)
        # Cap so the extended (q=-t) shaft bottom stays within its parent
        # cavity: joint_origin - shaft_len/2 - t >= parent_cavity_bottom. For
        # stage_0 the parent cavity is the grip socket; for i>=1 the parent
        # cavity is the tube bore inside stage_{i-1} whose bottom in the
        # parent's frame is roughly (parent joint_z - parent shaft_len - 0.005).
        # Shaft extends 0.028 m below the joint plane. At q=-t the shaft
        # bottom (in parent frame) sits at joint_z - 0.028 - t. Require it to
        # stay above the parent's cavity bottom with 2 mm safety.
        if i == 0:
            allowed = grip_top - 0.028 - grip_socket_start - 0.002
        else:
            # Parent shaft bottom (parent local) = -0.028; child shaft
            # bottom (parent local) = joint_offsets[i] - 0.028 - t. Require
            # joint_offsets[i] - 0.028 - t >= -0.028 + 0.002, i.e.
            # t <= joint_offsets[i] - 0.002.
            allowed = joint_offsets[i] - 0.002
        t = min(t, max(0.003, allowed))
        t = max(0.003, t)
        travels_list.append(t)

    clip_lower = 0.0
    clip_upper = _clamp(0.55 * clip_open_scale, 0.35, 0.75)

    return ResolvedTelescopingPointerConfig(
        body_form=body_form,
        stage_count=stage_count,
        tip_form=tip_form,
        secondary=secondary,
        lock=lock,
        palette_style=palette_style,
        grip_length_scale=grip_length_scale,
        stage_ratio=stage_ratio,
        travel_scale=travel_scale,
        clip_open_scale=clip_open_scale,
        grip_radius=grip_radius,
        grip_length=grip_length,
        grip_socket_r=grip_socket_r,
        grip_socket_len=grip_socket_len,
        grip_socket_start=grip_socket_start,
        end_cap_r=end_cap_r,
        grip_top=grip_top,
        stage_outer_r=tuple(outer_r_list),
        stage_inner_r=tuple(inner_r_list),
        stage_shaft_len=tuple(shaft_len_list),
        joint_z_offsets=tuple(joint_offsets),
        stage_travels=tuple(travels_list),
        clip_lower=clip_lower,
        clip_upper=clip_upper,
        name=cfg.name or "telescoping_pointer",
    )


def with_overrides(config: TelescopingPointerConfig, **kwargs) -> TelescopingPointerConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: TelescopingPointerConfig | ResolvedTelescopingPointerConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedTelescopingPointerConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("stage_count", str(r.stage_count)),
        ("tip_form", r.tip_form),
        ("secondary", r.secondary),
        ("lock", r.lock),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (adapted from S1-S9 shared cadquery helpers).
# ---------------------------------------------------------------------------
def _tube(outer_r: float, inner_r: float, length: float, start_z: float) -> cq.Workplane:
    inner_r = max(0.0002, min(inner_r, outer_r - 0.0002))
    return (
        cq.Workplane("XY")
        .circle(outer_r)
        .circle(inner_r)
        .extrude(length)
        .translate((0.0, 0.0, start_z))
    )


def _hollow_frustum(
    lo_r: float, hi_r: float, inner_r: float, length: float, start_z: float
) -> cq.Workplane:
    inner_r = max(0.0002, min(inner_r, min(lo_r, hi_r) - 0.0002))
    outer = (
        cq.Workplane("XY")
        .circle(lo_r)
        .workplane(offset=length)
        .circle(hi_r)
        .loft(combine=True)
        .translate((0.0, 0.0, start_z))
    )
    bore = (
        cq.Workplane("XY")
        .circle(inner_r)
        .extrude(length + 0.002)
        .translate((0.0, 0.0, start_z - 0.001))
    )
    return outer.cut(bore)


def _foam_grip_shape(r: ResolvedTelescopingPointerConfig) -> cq.Workplane:
    body = cq.Workplane("XY").circle(r.grip_radius).extrude(r.grip_length).edges().fillet(0.0035)
    socket = (
        cq.Workplane("XY")
        .circle(r.grip_socket_r)
        .extrude(r.grip_socket_len)
        .translate((0.0, 0.0, r.grip_socket_start))
    )
    return body.cut(socket)


def _pen_grip_shape(r: ResolvedTelescopingPointerConfig) -> cq.Workplane:
    body = cq.Workplane("XY").circle(r.grip_radius).extrude(r.grip_length).edges().fillet(0.0012)
    socket = (
        cq.Workplane("XY")
        .circle(r.grip_socket_r)
        .extrude(r.grip_socket_len)
        .translate((0.0, 0.0, r.grip_socket_start))
    )
    return body.cut(socket)


_SHAFT_BELOW_ORIGIN = 0.028  # S1 convention: shaft extends 28 mm below joint origin


def _stage_shape(
    outer_r: float,
    inner_r: float,
    shaft_len: float,
    *,
    with_collar: bool = True,
) -> cq.Workplane:
    """Outermost / intermediate stage tube with a collar at its top.

    Part frame convention: shaft extends only ``_SHAFT_BELOW_ORIGIN`` (6 mm)
    below the part-frame origin (the joint origin plane), with the rest of
    the shaft length rising +Z above the origin. This keeps the portion of
    the child that lives inside the parent bore SHORT — even at full
    extension (q=-travel with travel≤ ~0.028 m), the shaft tip stays inside
    the parent's cavity (grip socket ≥ 0.025 m deep; parent stage tube
    lengths ≥ 0.045 m).
    """
    shaft = _tube(outer_r, inner_r, shaft_len, -_SHAFT_BELOW_ORIGIN)
    if not with_collar:
        return shaft
    collar_lo = outer_r * 1.19
    collar_hi = outer_r * 0.98
    collar_inner = inner_r
    top = shaft_len - _SHAFT_BELOW_ORIGIN
    collar_base_len = max(0.003, shaft_len * 0.05)
    collar_base_z = top - collar_base_len - max(0.005, shaft_len * 0.10)
    collar_taper_len = max(0.005, shaft_len * 0.10)
    collar_taper_z = collar_base_z + collar_base_len
    collar_base = _tube(collar_lo, collar_inner, collar_base_len, collar_base_z)
    collar_taper = _hollow_frustum(
        collar_lo, collar_hi, collar_inner, collar_taper_len, collar_taper_z
    )
    return shaft.union(collar_base).union(collar_taper)


def _innermost_stage_shape(outer_r: float, inner_r: float, shaft_len: float) -> cq.Workplane:
    """Innermost tube with the tip-holder nose. Part-frame origin at z=0,
    shaft extending ``_SHAFT_BELOW_ORIGIN`` mm below origin, rest above with
    a holder + nose that carries the tip visual on top."""
    shaft = _tube(outer_r, inner_r, shaft_len, -_SHAFT_BELOW_ORIGIN)
    top = shaft_len - _SHAFT_BELOW_ORIGIN
    holder_r = outer_r * 1.55
    holder_h = max(0.012, shaft_len * 0.30)
    holder_z = max(0.001, top - holder_h - 0.004)
    holder = cq.Workplane("XY").circle(holder_r).extrude(holder_h).translate((0.0, 0.0, holder_z))
    nose_h = 0.004
    nose_lo = holder_r
    nose_hi = holder_r * 0.90
    nose_z = holder_z + holder_h
    nose = (
        cq.Workplane("XY")
        .circle(nose_lo)
        .workplane(offset=nose_h)
        .circle(nose_hi)
        .loft(combine=True)
        .translate((0.0, 0.0, nose_z))
    )
    return shaft.union(holder).union(nose)


def _rounded_stem_tip_shape(holder_top_z: float, holder_r: float) -> cq.Workplane:
    stem_r = holder_r * 0.85
    stem_len = 0.006
    stem = cq.Workplane("XY").circle(stem_r).extrude(stem_len).translate((0.0, 0.0, holder_top_z))
    ball = cq.Workplane("XY").sphere(stem_r).translate((0.0, 0.0, holder_top_z + stem_len))
    return stem.union(ball)


def _ball_tip_shape(holder_top_z: float, holder_r: float) -> cq.Workplane:
    neck_r = holder_r * 0.55
    neck_len = 0.004
    ball_r = holder_r * 1.15
    neck = cq.Workplane("XY").circle(neck_r).extrude(neck_len).translate((0.0, 0.0, holder_top_z))
    ball = (
        cq.Workplane("XY")
        .sphere(ball_r)
        .translate((0.0, 0.0, holder_top_z + neck_len + ball_r * 0.5))
    )
    return neck.union(ball)


def _flat_disc_tip_shape(holder_top_z: float, holder_r: float) -> cq.Workplane:
    stem_r = holder_r * 0.7
    stem_len = 0.005
    stem = cq.Workplane("XY").circle(stem_r).extrude(stem_len).translate((0.0, 0.0, holder_top_z))
    disc_r = holder_r * 2.6
    disc_h = 0.002
    disc = (
        cq.Workplane("XY")
        .circle(disc_r)
        .extrude(disc_h)
        .translate((0.0, 0.0, holder_top_z + stem_len))
    )
    return stem.union(disc)


def _hand_silhouette_tip_shape(holder_top_z: float, holder_r: float) -> cq.Workplane:
    """Flat hand silhouette (plate) sitting on a mounting collar. Adapted from
    S6 `_hand_silhouette_shape` (rec_..._var_tip_form_hand_silhouette L122-L222).
    """
    t = 0.002
    collar_outer = max(holder_r + 0.0005, 0.004)
    collar_inner = holder_r * 0.5
    collar_h = 0.006
    collar = (
        cq.Workplane("XY")
        .circle(collar_outer)
        .circle(collar_inner)
        .extrude(collar_h)
        .translate((0.0, 0.0, holder_top_z))
    )
    base_z = holder_top_z + collar_h
    # Palm: three trapezoidal slabs in XZ plane, thickness t along Y.
    palm_lower = (
        cq.Workplane("XZ")
        .workplane(offset=-t / 2)
        .center(0.0, base_z + 0.0035)
        .rect(0.013, 0.003)
        .extrude(t)
    )
    palm_body = (
        cq.Workplane("XZ")
        .workplane(offset=-t / 2)
        .center(0.0, base_z + 0.0075)
        .rect(0.014, 0.009)
        .extrude(t)
    )
    palm_upper = (
        cq.Workplane("XZ")
        .workplane(offset=-t / 2)
        .center(0.0, base_z + 0.0115)
        .rect(0.012, 0.003)
        .extrude(t)
    )
    wrist = (
        cq.Workplane("XZ")
        .workplane(offset=-t / 2)
        .center(0.0, base_z + 0.0)
        .rect(0.005, 0.006)
        .extrude(t)
    )
    hand = collar.union(wrist).union(palm_lower).union(palm_body).union(palm_upper)
    palm_top = base_z + 0.013
    finger_specs = [
        (-0.0040, 0.0080),
        (-0.0013, 0.0100),
        (0.0013, 0.0085),
        (0.0040, 0.0060),
    ]
    finger_w = 0.0025
    for fx, fl in finger_specs:
        finger = (
            cq.Workplane("XZ")
            .workplane(offset=-t / 2)
            .center(fx, palm_top + fl / 2)
            .rect(finger_w, fl)
            .extrude(t)
        )
        hand = hand.union(finger)
    thumb = (
        cq.Workplane("XZ")
        .workplane(offset=-t / 2)
        .center(-0.0085, base_z + 0.0045)
        .rect(0.003, 0.007)
        .extrude(t)
    )
    return hand.union(thumb)


def _twist_collar_shape(
    outer_r: float, inner_r: float, length: float, start_z: float
) -> cq.Workplane:
    """S8 twist-lock collar: hollow body + wider central band + top/bottom lips."""
    inner_r = max(0.0003, inner_r)
    body = _tube(outer_r, inner_r, length, start_z)
    band_w = length * 0.20
    band_z = start_z + (length - band_w) / 2
    band = _tube(outer_r * 1.06, inner_r, band_w, band_z)
    lip_w = length * 0.08
    top_lip = _tube(outer_r * 1.03, inner_r, lip_w, start_z + length - lip_w)
    bot_lip = _tube(outer_r * 1.03, inner_r, lip_w, start_z)
    return body.union(band).union(top_lip).union(bot_lip)


def _pocket_clip_arm_shape(hinge_z: float, hinge_offset: float) -> cq.Workplane:
    """Spring-steel clip arm. Adapted from S9 `_pocket_clip_shape` (L139-L168).

    Frame convention: joint origin at (0,0,0) in the clip part frame; the
    hinge barrel is along Y, and the arm hangs down (-Z) and wraps forward (+X).
    """
    # Hinge barrel centered on origin along Y (extrude length 0.014 centered).
    barrel = cq.Workplane("XZ").circle(0.0018).extrude(0.014).translate((0.0, -0.007, 0.0))
    # Arm hangs from barrel down along -Z. Give the arm a substantial +z
    # extension INTO the barrel and full +Y width matching the barrel length,
    # so the boolean union produces one connected component.
    arm = cq.Workplane("XY").transformed(offset=(0.00075, 0.0, -0.024)).box(0.0018, 0.014, 0.064)
    bend = cq.Workplane("XY").transformed(offset=(0.0025, 0.0, -0.053)).box(0.005, 0.014, 0.006)
    ball = cq.Workplane("XY").sphere(0.0024).translate((0.003, 0.0, -0.053))
    return barrel.union(arm).union(bend).union(ball)


def _clip_mount_shape() -> cq.Workplane:
    """Two-ear hinge bracket on the grip side. Adapted from S9 (L171-L193)."""
    ear_t = 0.0012
    ear_h = 0.006
    ear_w = 0.005
    half_gap = 0.006
    ear_a = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, -(half_gap + ear_t / 2), 0.0))
        .box(ear_w, ear_t, ear_h)
    )
    ear_b = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, half_gap + ear_t / 2, 0.0))
        .box(ear_w, ear_t, ear_h)
    )
    pad = cq.Workplane("XY").transformed(offset=(-0.001, 0.0, 0.0)).box(0.003, 0.014, ear_h)
    return ear_a.union(ear_b).union(pad)


def _pen_static_clip_shape(grip_len: float, grip_r: float) -> cq.Workplane:
    """Flat pen-style static clip. Adapted from S7 `_pen_clip_shape` (L134-L153)."""
    clip_body = (
        cq.Workplane("XZ")
        .moveTo(0.0, grip_len * 0.22)
        .lineTo(0.0, grip_len * 0.85)
        .lineTo(0.002, grip_len * 0.87)
        .lineTo(0.002, grip_len * 0.22)
        .close()
        .extrude(0.003)
        .translate((-0.0015, grip_r + 0.0001, 0.0))
    )
    return clip_body


# ---------------------------------------------------------------------------
# Model assembly
# ---------------------------------------------------------------------------
def _tol(radius: float) -> float:
    """Coarse mesh tolerance keyed to feature radius (compile budget §7.5)."""
    return max(0.00012, min(0.00035, radius * 0.08))


def _build_grip(model, r: ResolvedTelescopingPointerConfig, mats, *, assets):
    grip = model.part("grip")
    if r.body_form == "foam_grip_body":
        grip_mesh = mesh_from_cadquery(
            _foam_grip_shape(r), "pointer_foam_grip", tolerance=0.00035, assets=assets
        )
    else:
        grip_mesh = mesh_from_cadquery(
            _pen_grip_shape(r), "pointer_pen_grip", tolerance=0.00030, assets=assets
        )
    grip.visual(grip_mesh, material=mats["grip"], name="grip_body", material_class_id=("plastic.opaque_glossy_molded" if r.body_form == "pen_style_body" else "rubber.sponge_foam"))

    # End cap (Rule 1 inline decoration).
    grip.visual(
        mesh_from_cadquery(
            cq.Workplane("XY").sphere(r.end_cap_r).translate((0.0, 0.0, r.end_cap_r * 0.15)),
            "pointer_end_cap",
            tolerance=0.00025,
            assets=assets,
        ),
        material=mats["grip_trim"],
        name="end_cap", material_class_id="plastic.opaque_glossy_molded",
    )

    # Entry ring visual around the grip top.
    entry_r_outer = max(r.stage_outer_r[0] * 1.35, r.grip_socket_r + 0.0010)
    entry_r_inner = max(r.stage_outer_r[0] * 1.10, r.grip_socket_r + 0.0005)
    entry_len = 0.006
    grip.visual(
        mesh_from_cadquery(
            _tube(entry_r_outer, entry_r_inner, entry_len, r.grip_top - entry_len),
            "pointer_entry_ring",
            tolerance=0.00020,
            assets=assets,
        ),
        material=mats["grip_trim"],
        name="entry_ring", material_class_id="plastic.opaque_glossy_molded",
    )

    # Stage-0 guide bushing INSIDE the grip socket. Positioned so its top
    # coincides with r.grip_top (the joint origin plane), giving the stage_0
    # tube shaft a real bearing surface. The inner radius is a hair less than
    # stage_0.outer_r (interference contact), the outer radius exceeds
    # r.grip_socket_r (welds it to the grip body — no island).
    guide_outer = max(r.grip_socket_r + 0.0005, r.stage_outer_r[0] + 0.0005)
    guide_inner = max(0.0006, r.stage_outer_r[0] - 0.0002)
    guide_len = 0.005
    guide_z = r.grip_top - 0.019  # sits just below the entry ring
    grip.visual(
        mesh_from_cadquery(
            _tube(guide_outer, guide_inner, guide_len, guide_z),
            "pointer_stage_0_guide",
            tolerance=0.00015,
            assets=assets,
        ),
        material=mats["grip_trim"],
        name="stage_0_guide", material_class_id=("metal.blackened_gunmetal" if r.lock == "twist_collars" else "rubber.smooth_plain"),
    )

    # Optional: twist collar OVERLAY around grip top for lock=twist_collars
    # (§spec Slot E). Derived from grip's entry ring radius — host-conformal
    # (Rule 4) so it hugs the grip surface across pen/foam variants.
    if r.lock == "twist_collars":
        tc_outer = entry_r_outer * 1.55
        tc_inner = entry_r_inner - 0.0002
        tc_len = 0.014
        tc_start = r.grip_top - tc_len
        grip.visual(
            mesh_from_cadquery(
                _twist_collar_shape(tc_outer, tc_inner, tc_len, tc_start),
                "pointer_twist_collar_grip",
                tolerance=0.00020,
                assets=assets,
            ),
            material=mats["lock"],
            name="twist_collar_grip", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"office_black", "chrome_business", "matte_industrial", "student_bright"} else "metal.brass_aged"),
        )

    # Static pen-style clip if body is pen and NO dynamic clip (§spec compat).
    if r.body_form == "pen_style_body" and r.secondary != "hinged_pocket_clip":
        grip.visual(
            mesh_from_cadquery(
                _pen_static_clip_shape(r.grip_length, r.grip_radius),
                "pointer_pen_static_clip",
                tolerance=0.00025,
                assets=assets,
            ),
            material=mats["clip"],
            name="pen_static_clip", material_class_id=("metal.stainless_matte" if r.palette_style in {"office_black", "chrome_business", "retail_bronze", "student_bright"} else "metal.blackened_gunmetal"),
        )

    return grip


def _build_stages(model, r: ResolvedTelescopingPointerConfig, grip, mats, *, assets):
    """Emit N tube stages and the N PRISMATIC joints chaining them.

    Stage part frames: origin at the local joint anchor (parent's r.joint_z_offsets[i]
    in world), shaft centered so its geometric center contains the origin. The
    child's `-Z` half is inside the parent at rest; `+Z` half rises above the
    parent-top joint plane.
    """
    stages: list = []
    parents: list = [grip]
    n = r.stage_count
    for i in range(n):
        stage = model.part(f"stage_{i}")
        stages.append(stage)

        outer_r = r.stage_outer_r[i]
        inner_r = r.stage_inner_r[i]
        shaft_len = r.stage_shaft_len[i]

        # Metal tube visual: outermost / intermediate use collared tube; innermost
        # uses the tip-holder helper.
        if i == n - 1:
            tube_shape = _innermost_stage_shape(outer_r, inner_r, shaft_len)
        else:
            tube_shape = _stage_shape(outer_r, inner_r, shaft_len, with_collar=True)
        mat = mats["metal_a"] if i % 2 == 0 else mats["metal_b"]
        stage.visual(
            mesh_from_cadquery(
                tube_shape, f"pointer_stage_{i}_tube", tolerance=_tol(outer_r), assets=assets
            ),
            material=mat,
            name=f"tube_{i}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"office_black", "chrome_business", "retail_bronze", "student_bright"} else "metal.blackened_gunmetal"),
        )

        # Guide bushing for the NEXT stage sits inside this stage's collar top,
        # co-planar with the next joint origin so the child's shaft can bear on
        # it. Skip on the innermost stage.
        if i < n - 1:
            next_outer = r.stage_outer_r[i + 1]
            # Guide bushing: outer_r slightly BEYOND the parent tube's inner
            # bore so the bushing welds into the tube shell (no island); inner_r
            # slightly below the child tube's outer radius (interference fit →
            # touching → passes expect_contact).
            # 0.0005 m interference into the tube shell so the guide welds
            # even when radii are sub-mm; ensure guide bore never exceeds
            # its outer radius by keeping a 0.0002 m wall.
            g_outer = inner_r + 0.0005
            g_inner = max(0.00025, min(next_outer - 0.0002, g_outer - 0.0003))
            if g_outer <= g_inner + 0.0002:
                g_outer = g_inner + 0.0004
            g_len = 0.005
            # Position the guide so its top face sits at the next joint origin
            # (local = joint_z_offsets[i+1]) and its BOTTOM sinks 2 mm INTO the
            # tube shell z-range so the two visuals share a solid overlap in Z
            # (avoids an island right at the collar's top ring).
            g_top_local = r.joint_z_offsets[i + 1]
            g_z = g_top_local - g_len - 0.002
            stage.visual(
                mesh_from_cadquery(
                    _tube(g_outer, g_inner, g_len, g_z),
                    f"pointer_stage_{i + 1}_guide",
                    tolerance=_tol(g_outer),
                    assets=assets,
                ),
                material=mats["grip_trim"],
                name=f"stage_{i + 1}_guide", material_class_id=("metal.blackened_gunmetal" if r.lock == "twist_collars" else "rubber.smooth_plain"),
            )

            # Optional twist collar OVERLAY at this junction (Slot E).
            if r.lock == "twist_collars":
                tc_outer = max(outer_r * 1.35, g_outer * 1.10)
                tc_inner = g_inner
                tc_len = 0.010
                tc_start = g_top_local - tc_len - 0.0005
                stage.visual(
                    mesh_from_cadquery(
                        _twist_collar_shape(tc_outer, tc_inner, tc_len, tc_start),
                        f"pointer_twist_collar_{i}",
                        tolerance=0.00018,
                        assets=assets,
                    ),
                    material=mats["lock"],
                    name=f"twist_collar_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"office_black", "chrome_business", "matte_industrial", "student_bright"} else "metal.brass_aged"),
                )

    # Emit joints. i=0 is grip→stage_0; i>=1 is stage_{i-1}→stage_i.
    joints = []
    for i in range(n):
        parent_part = grip if i == 0 else stages[i - 1]
        child_part = stages[i]
        joint_name = "grip_to_stage_0" if i == 0 else f"stage_{i - 1}_to_stage_{i}"
        joint_z = r.joint_z_offsets[i]
        travel = r.stage_travels[i]
        # Deliberately GRANDFATHERED: telescoping tubes slide inside their
        # parent bushing; there is no axis-aligned clean face contact. Rely on
        # element-scoped allow_overlap + expect_overlap in run_tests instead.
        j = model.articulation(
            joint_name,
            ArticulationType.PRISMATIC,
            parent=parent_part,
            child=child_part,
            origin=Origin(xyz=(0.0, 0.0, joint_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=max(4.0, 18.0 - i * 2.5),
                velocity=0.20 + i * 0.01,
                lower=-travel,
                upper=0.0,
            ),
        )
        joints.append(j)
        _ = parent_part  # silence linters (not returned)

    return stages, joints, parents


def _build_tip(model, r: ResolvedTelescopingPointerConfig, innermost_stage, mats, *, assets):
    outer_r = r.stage_outer_r[-1]
    shaft_len = r.stage_shaft_len[-1]
    # Compute the holder top z in innermost-stage part frame:
    # innermost helper places holder centered at half - 0.004 with height
    # 0.30*shaft_len; add nose 0.004 → holder_top_z = half + holder_h - 0.004 + 0.004
    holder_r = outer_r * 1.55
    holder_h = max(0.012, shaft_len * 0.30)
    top = shaft_len - _SHAFT_BELOW_ORIGIN
    holder_z = max(0.001, top - holder_h - 0.004)
    holder_top_z = holder_z + holder_h + 0.004  # includes nose height

    if r.tip_form == "rounded_stem_tip":
        shape = _rounded_stem_tip_shape(holder_top_z, holder_r)
    elif r.tip_form == "ball_tip":
        shape = _ball_tip_shape(holder_top_z, holder_r)
    elif r.tip_form == "hand_silhouette_tip":
        shape = _hand_silhouette_tip_shape(holder_top_z, holder_r)
    else:  # flat_disc_tip
        shape = _flat_disc_tip_shape(holder_top_z, holder_r)
    innermost_stage.visual(
        mesh_from_cadquery(shape, f"pointer_tip_{r.tip_form}", tolerance=0.00015, assets=assets),
        material=mats["tip"],
        name="tip", material_class_id=("metal.brass_polished" if r.palette_style in {"office_black", "chrome_business", "retail_bronze", "student_bright"} else "metal.blackened_gunmetal"),
    )


def _build_clip(model, r: ResolvedTelescopingPointerConfig, grip, mats, *, assets):
    """Optional REVOLUTE pocket clip (Slot D=hinged_pocket_clip)."""
    hinge_offset_x = r.grip_radius + 0.0005
    hinge_z = r.grip_length * 0.84  # near the grip top, matches S9

    # Clip mount bracket visual (Rule 2: real anchoring visual on parent).
    grip.visual(
        mesh_from_cadquery(
            _clip_mount_shape(),
            "pointer_clip_mount",
            tolerance=0.00020,
            assets=assets,
        ),
        material=mats["clip"],
        origin=Origin(xyz=(hinge_offset_x, 0.0, hinge_z)),
        name="clip_mount", material_class_id=("metal.stainless_matte" if r.palette_style in {"office_black", "chrome_business", "retail_bronze", "student_bright"} else "metal.blackened_gunmetal"),
    )

    clip = model.part("pocket_clip")
    clip.visual(
        mesh_from_cadquery(
            _pocket_clip_arm_shape(hinge_z, hinge_offset_x),
            "pointer_pocket_clip",
            tolerance=0.00020,
            assets=assets,
        ),
        material=mats["clip"],
        name="clip_arm", material_class_id=("metal.stainless_matte" if r.palette_style in {"office_black", "chrome_business", "retail_bronze", "student_bright"} else "metal.blackened_gunmetal"),
    )

    model.articulation(
        "grip_to_clip",
        ArticulationType.REVOLUTE,
        parent=grip,
        child=clip,
        origin=Origin(xyz=(hinge_offset_x, 0.0, hinge_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0,
            velocity=2.0,
            lower=r.clip_lower,
            upper=r.clip_upper,
        ),
        mating=MatingContract(
            parent_face_geometry="clip_mount",
            parent_face_side="positive_x",
            child_face_geometry="clip_arm",
            child_face_side="negative_x",
            contact_tol=0.010,
        ),
    )
    return clip


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------
def build_telescoping_pointer(
    config: TelescopingPointerConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"tp_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    grip = _build_grip(model, r, mats, assets=assets)
    stages, joints, _ = _build_stages(model, r, grip, mats, assets=assets)
    _build_tip(model, r, stages[-1], mats, assets=assets)
    if r.secondary == "hinged_pocket_clip":
        _build_clip(model, r, grip, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["stage_count"] = r.stage_count
    return model


def build_seeded_telescoping_pointer(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_telescoping_pointer(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests (Rule 5: sampled-pose overlap + targeted ctx.pose).
# ---------------------------------------------------------------------------
def run_telescoping_pointer_tests(
    object_model: ArticulatedObject, config: TelescopingPointerConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    grip = object_model.get_part("grip")
    stages = [object_model.get_part(f"stage_{i}") for i in range(r.stage_count)]
    joints = [
        object_model.get_articulation(
            "grip_to_stage_0" if i == 0 else f"stage_{i - 1}_to_stage_{i}"
        )
        for i in range(r.stage_count)
    ]
    parents = [grip] + stages[:-1]

    # Structural.
    expected_parts = 1 + r.stage_count + (1 if r.secondary == "hinged_pocket_clip" else 0)
    expected_joints = r.stage_count + (1 if r.secondary == "hinged_pocket_clip" else 0)
    ctx.check(
        "telescoping pointer part / joint count",
        len(object_model.parts) == expected_parts
        and len(object_model.articulations) == expected_joints
        and [p.name for p in object_model.root_parts()] == ["grip"],
        details=(
            f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}, "
            f"expected_parts={expected_parts}, expected_joints={expected_joints}"
        ),
    )

    ctx.check(
        "every telescoping section has a coaxial negative-collapse prismatic joint",
        all(j.articulation_type == ArticulationType.PRISMATIC for j in joints)
        and all(tuple(j.axis) == (0.0, 0.0, 1.0) for j in joints)
        and all(
            j.motion_limits is not None
            and j.motion_limits.upper == 0.0
            and j.motion_limits.lower < 0.0
            for j in joints
        ),
        details=f"joint types={[j.articulation_type for j in joints]}",
    )

    # slot_choices reported.
    ctx.check(
        "slot_choices recorded on model.meta",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # XY containment for each stage inside its parent.
    for i, (child, parent) in enumerate(zip(stages, parents)):
        parent_elem = "grip_body" if i == 0 else f"tube_{i - 1}"
        ctx.expect_within(
            child,
            parent,
            axes="xy",
            inner_elem=f"tube_{i}",
            outer_elem=parent_elem,
            name=f"stage_{i} tube centered in parent {parent.name}",
        )

    # Z retention (rest / extended pose).
    min_overlaps_rest = [max(0.008, r.stage_travels[i] * 0.55) for i in range(r.stage_count)]
    for i, (child, parent) in enumerate(zip(stages, parents)):
        ctx.expect_overlap(
            child,
            parent,
            axes="z",
            min_overlap=min_overlaps_rest[i],
            name=f"stage_{i} retained in parent at rest",
        )

    # Non-adjacent nested pair allowances: every inner stage tube lives inside
    # every outer stage tube's bore (which the mesh collision engine sees as
    # solid because bored OBJ volumes aren't preserved). Declare the intended
    # overlap between every non-adjacent (parent, grand-child, ...) pair.
    for i in range(r.stage_count):
        for j in range(i + 2, r.stage_count):
            ctx.allow_overlap(
                stages[i],
                stages[j],
                elem_a=f"tube_{i}",
                elem_b=f"tube_{j}",
                reason=(
                    f"stage_{j} tube nests inside stage_{i} tube's bore; "
                    "intentional coaxial captured-slide."
                ),
            )
            # Twist-collar overlays on outer stage also intersect nested
            # inner tubes (they cover the same z-band as the inner tube).
            if r.lock == "twist_collars" and i < r.stage_count - 1:
                ctx.allow_overlap(
                    stages[i],
                    stages[j],
                    elem_a=f"twist_collar_{i}",
                    elem_b=f"tube_{j}",
                    reason=(
                        f"Twist collar at stage_{i} sits around all nested "
                        f"inner tubes including stage_{j}."
                    ),
                )
        if i >= 1:
            # grip ↔ stage_i for i>=1 (grand-child of grip inside grip socket bore).
            ctx.allow_overlap(
                grip,
                stages[i],
                elem_a="grip_body",
                elem_b=f"tube_{i}",
                reason=(
                    f"stage_{i} tube nests inside the grip socket via the "
                    "outer stages; intentional captured-slide space."
                ),
            )
            if r.lock == "twist_collars":
                ctx.allow_overlap(
                    grip,
                    stages[i],
                    elem_a="twist_collar_grip",
                    elem_b=f"tube_{i}",
                    reason=(f"Grip twist collar surrounds all nested stages including stage_{i}."),
                )

    # Element-scoped allowances: guide bushing ↔ tube (intended radial interference).
    for i in range(r.stage_count):
        parent = grip if i == 0 else stages[i - 1]
        child = stages[i]
        guide_elem = f"stage_{i}_guide" if i == 0 else f"stage_{i}_guide"
        ctx.allow_overlap(
            parent,
            child,
            elem_a=guide_elem,
            elem_b=f"tube_{i}",
            reason=f"stage_{i} tube is captured by the {guide_elem} bushing.",
        )
        ctx.expect_contact(
            parent,
            child,
            elem_a=guide_elem,
            elem_b=f"tube_{i}",
            name=f"stage_{i} tube bears in {guide_elem}",
        )
        # Element-scoped allowance: the child tube physically slides INSIDE
        # the parent's cavity (grip socket bore, or the parent tube's inner
        # bore). The mesh-level collision engine treats those bored volumes
        # as solid because OBJ export doesn't preserve interior cavities;
        # declare the overlap as intentional captured-slide contact.
        parent_elem = "grip_body" if i == 0 else f"tube_{i - 1}"
        ctx.allow_overlap(
            parent,
            child,
            elem_a=parent_elem,
            elem_b=f"tube_{i}",
            reason=(
                f"stage_{i} tube slides inside the {parent_elem} bore/cavity; "
                "the bored inner volume is intentional captured-slide space."
            ),
        )
        # Twist collar overlaps its own inner face on both parent and child.
        if r.lock == "twist_collars":
            if i == 0:
                ctx.allow_overlap(
                    parent,
                    child,
                    elem_a="twist_collar_grip",
                    elem_b=f"tube_{i}",
                    reason="Twist collar at grip captures the outer tube.",
                )
            else:
                ctx.allow_overlap(
                    parent,
                    child,
                    elem_a=f"twist_collar_{i - 1}",
                    elem_b=f"tube_{i}",
                    reason=f"Twist collar at stage_{i - 1} captures the stage_{i} tube.",
                )

    # Extended-pose envelope: tip lies above grip.
    grip_box = ctx.part_world_aabb(grip)
    tip_box = ctx.part_element_world_aabb(stages[-1], elem="tip")
    ctx.check(
        "extended pose: tip lies above grip top",
        grip_box is not None and tip_box is not None and tip_box[1][2] > grip_box[1][2] + 0.010,
        details=f"grip={grip_box}, tip={tip_box}",
    )

    # Collapse pose: drive all stages to their lower limit; every stage should
    # move DOWN in world z (toward grip) and remain engaged with its parent.
    rest_positions = [ctx.part_world_position(s) for s in stages]
    collapse_pose = {joints[i]: -r.stage_travels[i] for i in range(r.stage_count)}
    with ctx.pose(collapse_pose):
        collapsed_positions = [ctx.part_world_position(s) for s in stages]
        for i, (child, parent) in enumerate(zip(stages, parents)):
            ctx.expect_overlap(
                child,
                parent,
                axes="z",
                min_overlap=min_overlaps_rest[i] * 0.6,
                name=f"collapsed stage_{i} remains engaged",
            )

    ctx.check(
        "all stages descend on collapse",
        all(
            rp is not None and cp is not None and cp[2] < rp[2] - 0.002
            for rp, cp in zip(rest_positions, collapsed_positions)
        ),
        details=f"rest={rest_positions}, collapsed={collapsed_positions}",
    )

    # Optional clip: pose test — swing to upper, clip's world +X moves outward.
    if r.secondary == "hinged_pocket_clip":
        clip = object_model.get_part("pocket_clip")
        clip_joint = object_model.get_articulation("grip_to_clip")
        rest_box = ctx.part_element_world_aabb(clip, elem="clip_arm")
        with ctx.pose({clip_joint: clip_joint.motion_limits.upper}):
            opened_box = ctx.part_element_world_aabb(clip, elem="clip_arm")
        ctx.check(
            "pocket clip swings outward on open",
            rest_box is not None
            and opened_box is not None
            # The clip's max X extent should move outward (+X) when opened.
            and opened_box[1][0] > rest_box[1][0] + 0.0005,
            details=f"rest_bbox={rest_box}, opened_bbox={opened_box}",
        )
        # Element-scoped allowances around the hinge hardware.
        ctx.allow_overlap(
            grip,
            clip,
            elem_a="clip_mount",
            elem_b="clip_arm",
            reason="Clip barrel is captured inside the two-ear clip_mount bracket.",
        )
        ctx.allow_overlap(
            grip,
            clip,
            elem_a="grip_body",
            elem_b="clip_arm",
            reason=(
                "Clip arm springs against the grip body along its retention "
                "sweep (spring-steel pocket clip)."
            ),
        )

    # Rule 5 sampled-pose overlap gate. Cap combos: each joint sampled at
    # {0, lower, upper=0, mid}; for stage_count=5 + clip, keep the budget low.
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=48,
        ignore_fixed=True,
    )

    return ctx.report()


__all__ = (
    "BODY_FORMS",
    "LOCKS",
    "PALETTES",
    "PALETTE_STYLES",
    "SECONDARIES",
    "STAGE_COUNTS",
    "TIP_FORMS",
    "ResolvedTelescopingPointerConfig",
    "TelescopingPointerConfig",
    "build_seeded_telescoping_pointer",
    "build_telescoping_pointer",
    "config_from_seed",
    "resolve_config",
    "run_telescoping_pointer_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
