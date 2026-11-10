# SPDX-License-Identifier: Apache-2.0

"""Binder / bulldog clip modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Stationary_Clip.md`` and the
``picture/Stationary/Clip`` 5-star sample pool (1 parent + 8 single-axis fork
variants: double_wire_handles / flat_lever_handles / eyelet_knuckle_pivot /
wide_mouth_footprint / serrated_mouth / round_back_body / single_handle /
round_loop_handles).

Structure (pattern = ``mixed``): a root ``clip_body`` front jaw and a
``moving_jaw`` rear jaw form the folded spring-steel clamp body. The rear jaw
has its own limited REVOLUTE hinge at the spring ridge, while each rolled lip
carries a **parallel handle child** plus a **handle multiplicity** axis:

  * ``body_form`` (2): folded triangular-prism band (sharp apex) vs softened
    folded roof band (straight panels with a mild crown). (parent S0 vs round_back S5)
  * ``lip_bearing`` (2): continuous rolled barrel running the full width vs a row
    of discrete pierced knuckle eyelets. (parent S0 vs eyelet S2)
  * ``handle_style`` (4): U-shaped wire loop / flat stamped paddle lever / smooth
    teardrop wire loop / doubled side-by-side wire strands. Each handle is a
    REVOLUTE lever pivoting about its rolled-lip (Y) axis. (S0 / flat_lever S1 /
    round_loop S8 / double_wire S3)
  * ``mouth_grip`` (2, optional): plain smooth mouth vs a row of triangular
    serration teeth fused into the body as body visuals. (parent S0 vs serrated S4)
  * ``jaw_open_hinge``: the rear spring-steel jaw opens about the top fold /
    ridge axis, so the clip itself has an articulated mouth independent of the
    handle pivots.
  * handle **multiplicity**: 1 (front lip only) or 2 (front + rear lips) lever
    handles, each a ``handle_{i}`` REVOLUTE about its lip. Encoded in
    slot_choices as ``handles_{n}`` so the ``module_topology_diversity`` gate sees
    distinct handle topologies. (single_handle S6 vs parent S0)

The body footprint (mouth depth / apex height / handle reach) is a controlled
continuous scale (wide_mouth S7). Serration teeth and lip bearings union into the
jaw visuals; no FIXED decoration parts. The wire/paddle handle is captured
on the rolled lip barrel, so its REVOLUTE joint omits ``MatingContract``
(grandfathered) and relies on the flat articulation-origin baseline (the joint
origin sits on the real lip barrel) plus a broad ``allow_overlap`` for the
wire/lip capture nest, mirroring the parent's lip-capture treatment.
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
    tube_from_spline_points,
)

__modular__ = True

BodyForm = Literal["folded_triangular", "rounded_dome"]
LipBearing = Literal["continuous_barrel", "knuckle_eyelets"]
HandleStyle = Literal[
    "wire_u_loop", "flat_paddle_lever", "teardrop_wire_loop", "double_wire_strand"
]
MouthGrip = Literal["plain", "serrated_teeth"]
MaterialStyle = Literal["orange_steel", "black_steel", "silver_steel"]

BODY_FORMS: tuple[BodyForm, ...] = ("folded_triangular", "rounded_dome")
LIP_BEARINGS: tuple[LipBearing, ...] = ("continuous_barrel", "knuckle_eyelets")
HANDLE_STYLES: tuple[HandleStyle, ...] = (
    "wire_u_loop",
    "flat_paddle_lever",
    "teardrop_wire_loop",
    "double_wire_strand",
)
MOUTH_GRIPS: tuple[MouthGrip, ...] = ("plain", "serrated_teeth")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = ("orange_steel", "black_steel", "silver_steel")

# Handle multiplicity domain (spec §8). 1 = front lip only, 2 = front + rear.
N_HANDLES_MIN, N_HANDLES_MAX = 1, 2

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "orange_steel": {
        "body": (0.86, 0.34, 0.13, 1.0),
        "handle": (0.30, 0.30, 0.33, 1.0),
    },
    "black_steel": {
        "body": (0.14, 0.14, 0.16, 1.0),
        "handle": (0.62, 0.63, 0.66, 1.0),
    },
    "silver_steel": {
        "body": (0.70, 0.71, 0.74, 1.0),
        "handle": (0.34, 0.35, 0.38, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). A standard ~32 mm "medium" binder clip.
# Baselines from parent 6a1d52ff; wide-mouth depth/reach from wide_mouth S7.
# ---------------------------------------------------------------------------
_WIDTH = 0.032  # clip width along Y (the lip / pivot axis span) — not scaled
_DEPTH = 0.026  # front-to-back mouth span (X) — scaled by mouth_scale
_APEX_Z = 0.018  # height of the folded ridge above the mouth (Z)

_SHEET_T = 0.0010  # spring-steel sheet thickness
_LIP_R = 0.0018  # outer radius of each rolled lip (barrel / knuckle)
_LIP_INNER_R = 0.0011  # hollow inner radius of each rolled lip

_WIRE_R = 0.00085  # handle wire radius
_HANDLE_LEN = 0.030  # how far a handle reaches from its lip when laid flat
_HANDLE_HALF_W = 0.0085  # half the span between a handle's two legs

# Knuckle eyelets.
_N_KNUCKLES = 5

# Flat paddle lever.
_PLATE_T = 0.0008
_PADDLE_W = 0.022
_PADDLE_L = 0.024
_HOOK_GAP_HALF_ANGLE = 50.0

# Teardrop loop bulge.
_TEARDROP_MAX_HW = 0.013
_TEARDROP_TIP_HW = 0.0045

# Doubled wire strand.
_STRAND_COUNT = 2
_STRAND_SPACING = 0.0022

# Serration teeth.
_N_TEETH_PER_EDGE = 10
_TOOTH_H = 0.0014
_TOOTH_D = 0.0012

_HANDLE_OPEN_LIMIT = 0.18


@dataclass(frozen=True)
class ClipConfig:
    body_form: BodyForm | None = None
    lip_bearing: LipBearing | None = None
    handle_style: HandleStyle | None = None
    mouth_grip: MouthGrip | None = None
    n_handles: int | None = None
    material_style: MaterialStyle = "orange_steel"
    mouth_scale: float = 1.0
    apex_scale: float = 1.0
    handle_reach_scale: float = 1.0
    name: str = "clip"


@dataclass(frozen=True)
class ResolvedClipConfig:
    body_form: BodyForm
    lip_bearing: LipBearing
    handle_style: HandleStyle
    mouth_grip: MouthGrip
    n_handles: int
    material_style: MaterialStyle
    # Concrete geometry (scaled).
    width: float
    half_w: float
    depth: float
    half_d: float
    apex_z: float
    sheet_t: float
    lip_r: float
    lip_inner_r: float
    wire_r: float
    handle_len: float
    handle_half_w: float
    name: str

    @property
    def is_dome(self) -> bool:
        return self.body_form == "rounded_dome"

    @property
    def front_lip(self) -> tuple[float, float]:
        return (-self.half_d, 0.0)

    @property
    def rear_lip(self) -> tuple[float, float]:
        return (self.half_d, 0.0)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> ClipConfig:
    rng = random.Random(seed)
    # Weighted procedural sampling: the dome body, eyelet bearing, exotic handle
    # styles and serration are rarer; two handles are the common case (spec §9).
    body = rng.choices(BODY_FORMS, weights=[7, 3], k=1)[0]
    lip = rng.choices(LIP_BEARINGS, weights=[7, 3], k=1)[0]
    handle = rng.choices(HANDLE_STYLES, weights=[5, 3, 2, 2], k=1)[0]
    grip = rng.choices(MOUTH_GRIPS, weights=[6, 4], k=1)[0]
    n_handles = rng.choices([1, 2], weights=[3, 7], k=1)[0]
    return ClipConfig(
        body_form=body,
        lip_bearing=lip,
        handle_style=handle,
        mouth_grip=grip,
        n_handles=n_handles,
        material_style=rng.choice(MATERIAL_STYLES),
        mouth_scale=round(rng.uniform(0.92, 1.65), 4),
        apex_scale=round(rng.uniform(0.90, 1.18), 4),
        handle_reach_scale=round(rng.uniform(0.90, 1.15), 4),
        name=f"seeded_clip_{seed}",
    )


def resolve_config(config: ClipConfig | None = None) -> ResolvedClipConfig:
    cfg = config or ClipConfig()
    body = _pick(cfg.body_form, BODY_FORMS)
    lip = _pick(cfg.lip_bearing, LIP_BEARINGS)
    handle = _pick(cfg.handle_style, HANDLE_STYLES)
    grip = _pick(cfg.mouth_grip, MOUTH_GRIPS)
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)

    n_handles = int(
        _clamp(cfg.n_handles if cfg.n_handles is not None else 2, N_HANDLES_MIN, N_HANDLES_MAX)
    )

    mouth_scale = _clamp(cfg.mouth_scale, 0.92, 1.65)
    apex_scale = _clamp(cfg.apex_scale, 0.90, 1.18)
    reach_scale = _clamp(cfg.handle_reach_scale, 0.90, 1.15)

    depth = _DEPTH * mouth_scale
    half_d = depth / 2.0
    # Apex grows only mildly with depth. Real binder clips are broad folded
    # panels, not high semicircular arches, so wide-mouth variants should not
    # balloon upward.
    apex_z = _clamp(_APEX_Z * (0.78 + 0.22 * mouth_scale) * apex_scale, 0.012, 0.030)

    # Handle reach tracks the mouth depth (a wider mouth gets a longer lever) and
    # is then nudged by reach_scale; clamp so the lever never collapses inward.
    handle_len = _clamp(_HANDLE_LEN * mouth_scale * reach_scale, 0.018, 0.060)

    return ResolvedClipConfig(
        body_form=body,
        lip_bearing=lip,
        handle_style=handle,
        mouth_grip=grip,
        n_handles=n_handles,
        material_style=material_style,
        width=_WIDTH,
        half_w=_WIDTH / 2.0,
        depth=depth,
        half_d=half_d,
        apex_z=apex_z,
        sheet_t=_SHEET_T,
        lip_r=_LIP_R,
        lip_inner_r=_LIP_INNER_R,
        wire_r=_WIRE_R,
        handle_len=handle_len,
        handle_half_w=_HANDLE_HALF_W,
        name=cfg.name or "clip",
    )


def with_overrides(config: ClipConfig, **kwargs: object) -> ClipConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ClipConfig | ResolvedClipConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedClipConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("lip_bearing", r.lip_bearing),
        ("handle_style", r.handle_style),
        ("mouth_grip", r.mouth_grip),
        ("handles", f"handles_{r.n_handles}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Body band cross-section + lip geometry.
# ---------------------------------------------------------------------------
def _band_profile(r: ResolvedClipConfig) -> list[tuple[float, float]]:
    """Folded triangular (x, z) center-line: front lip -> apex -> rear lip."""
    fx = r.front_lip[0]
    rx = r.rear_lip[0]
    return [
        (fx, r.lip_r),
        (fx * 0.55, r.apex_z * 0.62),
        (0.0, r.apex_z),
        (rx * 0.55, r.apex_z * 0.62),
        (rx, r.lip_r),
    ]


def _jaw_centerlines(
    r: ResolvedClipConfig,
) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """Return front/root and rear/moving jaw center-lines in body coordinates."""
    if r.is_dome:
        pts = _dome_centerline(r)
    else:
        pts = _band_profile(r)
    apex_i = len(pts) // 2
    return pts[: apex_i + 1], pts[apex_i:]


def _dome_centerline(r: ResolvedClipConfig, n_control: int = 9) -> list[tuple[float, float]]:
    """Soft folded roof profile from front lip to rear lip.

    Real binder clips read as two broad spring-steel panels meeting at a rounded
    crown, not as a semicircular bridge. Keep the rounded-back variant, but bias
    it toward straight side panels with only the ridge softened.
    """
    fx = r.front_lip[0]
    rx = r.rear_lip[0]
    return [
        (fx, r.lip_r),
        (fx * 0.80, r.apex_z * 0.22),
        (fx * 0.54, r.apex_z * 0.66),
        (fx * 0.22, r.apex_z * 0.96),
        (0.0, r.apex_z),
        (rx * 0.22, r.apex_z * 0.96),
        (rx * 0.54, r.apex_z * 0.66),
        (rx * 0.80, r.apex_z * 0.22),
        (rx, r.lip_r),
    ]


def _offset_curve(pts: list[tuple[float, float]], offset: float) -> list[tuple[float, float]]:
    """Offset a 2-D (x, z) polyline along outward (upward-ish) normals."""
    n = len(pts)
    result: list[tuple[float, float]] = []
    for i in range(n):
        px, pz = pts[i]
        x0, z0 = pts[max(i - 1, 0)]
        x1, z1 = pts[min(i + 1, n - 1)]
        tx, tz = x1 - x0, z1 - z0
        tl = math.hypot(tx, tz) or 1.0
        tx, tz = tx / tl, tz / tl
        nx, nz = -tz, tx
        if nz < 0:
            nx, nz = -nx, -nz
        result.append((px + nx * offset, pz + nz * offset))
    return result


def _band_solid(r: ResolvedClipConfig) -> cq.Workplane:
    """The folded / domed sheet band as a swept solid, centered on Y=0."""
    h = r.sheet_t / 2.0
    if r.is_dome:
        centerline = _dome_centerline(r)
        outer_pts = _offset_curve(centerline, +h)
        inner_pts = _offset_curve(centerline, -h)
        inner_rev = list(reversed(inner_pts))
        wp = cq.Workplane("XZ").moveTo(*outer_pts[0])
        wp = wp.spline(outer_pts[1:], includeCurrent=True)
        wp = wp.lineTo(*inner_rev[0])
        wp = wp.spline(inner_rev[1:], includeCurrent=True)
        wp = wp.close()
        band = wp.extrude(r.width)
    else:
        centerline = _band_profile(r)
        outer = _offset_curve(centerline, +h)
        inner = _offset_curve(centerline, -h)
        loop = outer + list(reversed(inner))
        band = cq.Workplane("XZ").polyline(loop).close().extrude(r.width)
    return band.translate((0, r.half_w, 0))


def _jaw_band_solid(r: ResolvedClipConfig, *, rear: bool) -> cq.Workplane:
    """One spring-steel jaw leaf as a swept solid.

    The returned rear jaw is still in body coordinates; callers localize it to
    the jaw hinge frame after fusing the rear lip and optional teeth.
    """
    front_pts, rear_pts = _jaw_centerlines(r)
    centerline = rear_pts if rear else front_pts
    h = r.sheet_t / 2.0
    outer = _offset_curve(centerline, +h)
    inner = _offset_curve(centerline, -h)
    inner_rev = list(reversed(inner))
    loop = outer + inner_rev
    band = cq.Workplane("XZ").polyline(loop).close().extrude(r.width)
    return band.translate((0, r.half_w, 0))


def _barrel(r: ResolvedClipConfig, cx: float, cz: float) -> cq.Workplane:
    """Continuous hollow rolled-lip barrel running the full width along Y."""
    outer_tube = cq.Workplane("XY").center(cx, 0).circle(r.lip_r).extrude(r.width)
    outer_tube = outer_tube.rotate((0, 0, 0), (1, 0, 0), -90)
    inner_tube = cq.Workplane("XY").center(cx, 0).circle(r.lip_inner_r).extrude(r.width)
    inner_tube = inner_tube.rotate((0, 0, 0), (1, 0, 0), -90)
    return outer_tube.cut(inner_tube).translate((0, -r.half_w, cz))


def _knuckle_eyelet(r: ResolvedClipConfig, cx: float, cz: float, cy: float) -> cq.Workplane:
    """One short hollow cylindrical knuckle eyelet at (cx, cy, cz) along Y."""
    knuckle_len = r.width / (_N_KNUCKLES * 1.55)
    half_len = knuckle_len / 2.0
    outer_cyl = (
        cq.Workplane("XZ")
        .workplane(offset=cy - half_len)
        .center(cx, cz)
        .circle(r.lip_r)
        .extrude(knuckle_len)
    )
    inner_cyl = (
        cq.Workplane("XZ")
        .workplane(offset=cy - half_len)
        .center(cx, cz)
        .circle(r.lip_inner_r)
        .extrude(knuckle_len)
    )
    return outer_cyl.cut(inner_cyl)


def _knuckle_y_positions(r: ResolvedClipConfig) -> list[float]:
    knuckle_len = r.width / (_N_KNUCKLES * 1.55)
    span = r.width - knuckle_len
    step = span / (_N_KNUCKLES - 1)
    return [-span / 2.0 + i * step for i in range(_N_KNUCKLES)]


def _add_lip(r: ResolvedClipConfig, body: cq.Workplane, cx: float, cz: float) -> cq.Workplane:
    """Union the chosen lip bearing (barrel or knuckle row) onto the body."""
    if r.lip_bearing == "knuckle_eyelets":
        for cy in _knuckle_y_positions(r):
            body = body.union(_knuckle_eyelet(r, cx, cz, cy))
        return body
    return body.union(_barrel(r, cx, cz))


def _serration_tooth(
    r: ResolvedClipConfig, base_x: float, inward_sign: float, y_center: float
) -> cq.Workplane:
    """One downward-pointing triangular serration tooth (prism along Y)."""
    spacing = r.width / (_N_TEETH_PER_EDGE + 1)
    tooth_w = spacing * 0.60
    z_top = r.lip_r + 0.0002
    z_tip = z_top - _TOOTH_H
    x0 = base_x
    x1 = base_x + inward_sign * _TOOTH_D
    xm = base_x + inward_sign * _TOOTH_D * 0.5
    tooth = (
        cq.Workplane("XZ")
        .moveTo(x0, z_top)
        .lineTo(x1, z_top)
        .lineTo(xm, z_tip)
        .close()
        .extrude(tooth_w)
    )
    return tooth.translate((0, y_center + tooth_w / 2.0, 0))


def _build_jaw_mesh(r: ResolvedClipConfig, *, rear: bool, assets):
    """One jaw shell: folded/domed leaf + its rolled lip (+ optional teeth)."""
    body = _jaw_band_solid(r, rear=rear)
    lip_x, lip_z = r.rear_lip if rear else r.front_lip
    body = _add_lip(r, body, lip_x, lip_z)

    if r.mouth_grip == "serrated_teeth":
        spacing = r.width / (_N_TEETH_PER_EDGE + 1)
        for i in range(_N_TEETH_PER_EDGE):
            yc = -r.half_w + spacing * (i + 1)
            inward = -1.0 if rear else +1.0
            body = body.union(_serration_tooth(r, lip_x, inward, yc))

    name = "rear_jaw_shell" if rear else "front_jaw_shell"
    if rear:
        body = body.translate((0.0, 0.0, -r.apex_z))

    return mesh_from_cadquery(body, name, assets=assets, tolerance=0.0004, angular_tolerance=0.2)


def _build_body_mesh(r: ResolvedClipConfig, *, assets):
    """Backward-compatible full body mesh helper retained for direct callers."""
    body = _band_solid(r)
    body = _add_lip(r, body, r.front_lip[0], r.front_lip[1])
    body = _add_lip(r, body, r.rear_lip[0], r.rear_lip[1])

    if r.mouth_grip == "serrated_teeth":
        spacing = r.width / (_N_TEETH_PER_EDGE + 1)
        for i in range(_N_TEETH_PER_EDGE):
            yc = -r.half_w + spacing * (i + 1)
            body = body.union(_serration_tooth(r, r.front_lip[0], +1.0, yc))
            body = body.union(_serration_tooth(r, r.rear_lip[0], -1.0, yc))

    return mesh_from_cadquery(
        body, "body_shell", assets=assets, tolerance=0.0004, angular_tolerance=0.2
    )


# ---------------------------------------------------------------------------
# Handle meshes. Authored in the lip-local frame: origin at the lip center,
# x toward the free end, y across the width, z up. The hook roots dip below /
# behind the barrel so the part AABB contains the joint origin (0,0,0) which
# sits on the real lip barrel geometry.
# ---------------------------------------------------------------------------
def _wire_u_points(r: ResolvedClipConfig, reach_dir: float) -> list[tuple[float, float, float]]:
    yw = r.handle_half_w
    wrap = r.lip_r + r.wire_r * 0.2
    lean_x = reach_dir * r.handle_len * 0.38
    stem_x = reach_dir * r.handle_len * 0.13
    top_z = r.handle_len * 0.95
    mid_z = top_z * 0.58
    hook_x = -reach_dir * wrap * 0.85
    hook_z = -wrap * 0.45
    return [
        (hook_x, +yw, hook_z),
        (reach_dir * wrap, +yw, r.lip_r + r.wire_r),
        (stem_x, +yw, mid_z),
        (lean_x, +yw * 0.76, top_z * 0.92),
        (lean_x * 1.04, 0.0, top_z),
        (lean_x, -yw * 0.76, top_z * 0.92),
        (stem_x, -yw, mid_z),
        (reach_dir * wrap, -yw, r.lip_r + r.wire_r),
        (hook_x, -yw, hook_z),
    ]


def _teardrop_points(r: ResolvedClipConfig, reach_dir: float) -> list[tuple[float, float, float]]:
    wrap = r.lip_r + r.wire_r * 0.2
    hook_x = -reach_dir * wrap * 0.85
    hook_z = -wrap * 0.45
    yw_narrow = r.handle_half_w * 0.62
    yw_wide = _TEARDROP_MAX_HW
    yw_tip = _TEARDROP_TIP_HW
    x0 = reach_dir * wrap
    x1 = reach_dir * r.handle_len * 0.08
    x2 = reach_dir * r.handle_len * 0.14
    x3 = reach_dir * r.handle_len * 0.21
    x4 = reach_dir * r.handle_len * 0.29
    x5 = reach_dir * r.handle_len * 0.36
    x6 = reach_dir * r.handle_len * 0.40
    x7 = reach_dir * r.handle_len * 0.42
    z0 = r.lip_r + r.wire_r
    z1 = r.handle_len * 0.22
    z2 = r.handle_len * 0.42
    z3 = r.handle_len * 0.60
    z4 = r.handle_len * 0.76
    z5 = r.handle_len * 0.90
    z6 = r.handle_len * 0.98
    z7 = r.handle_len * 1.02
    return [
        (hook_x, +yw_narrow, hook_z),
        (x0, +yw_narrow, z0),
        (x1, +yw_wide * 0.78, z1),
        (x2, +yw_wide * 0.92, z2),
        (x3, +yw_wide, z3),
        (x4, +yw_wide * 0.95, z4),
        (x5, +yw_tip * 1.4, z5),
        (x6, +yw_tip, z6),
        (x7, 0.0, z7),
        (x6, -yw_tip, z6),
        (x5, -yw_tip * 1.4, z5),
        (x4, -yw_wide * 0.95, z4),
        (x3, -yw_wide, z3),
        (x2, -yw_wide * 0.92, z2),
        (x1, -yw_wide * 0.78, z1),
        (x0, -yw_narrow, z0),
        (hook_x, -yw_narrow, hook_z),
    ]


def _strand_points(
    r: ResolvedClipConfig, reach_dir: float, y_offset: float
) -> list[tuple[float, float, float]]:
    yw = r.handle_half_w
    wrap = r.lip_r + r.wire_r * 0.2
    lean_x = reach_dir * r.handle_len * 0.38
    stem_x = reach_dir * r.handle_len * 0.13
    top_z = r.handle_len * 0.95
    mid_z = top_z * 0.58
    hook_x = -reach_dir * wrap * 0.85
    hook_z = -wrap * 0.45
    yo = y_offset
    yo_tip = y_offset * 0.35
    return [
        (hook_x, +yw, hook_z),
        (reach_dir * wrap, +yw + yo, r.lip_r + r.wire_r),
        (stem_x, +yw + yo, mid_z),
        (lean_x, +yw * 0.7 + yo_tip, top_z * 0.92),
        (lean_x * 1.04, 0.0, top_z),
        (lean_x, -yw * 0.7 + yo_tip, top_z * 0.92),
        (stem_x, -yw + yo, mid_z),
        (reach_dir * wrap, -yw + yo, r.lip_r + r.wire_r),
        (hook_x, -yw, hook_z),
    ]


def _wire_mesh(pts, name, *, samples=14):
    geom = tube_from_spline_points(
        pts, radius=_WIRE_R, samples_per_segment=samples, radial_segments=14, cap_ends=True
    )
    return mesh_from_geometry(geom, name)


def _paddle_cq(r: ResolvedClipConfig, reach_dir: float) -> cq.Workplane:
    """Flat sheet-metal paddle lever with a C-shaped rolled hook root."""
    hook_inner_r = r.lip_r + 0.0002
    hook_outer_r = hook_inner_r + _PLATE_T
    opening = 0.0 if reach_dir < 0 else 180.0
    a_start = math.radians(opening + _HOOK_GAP_HALF_ANGLE)
    a_end = math.radians(opening + 360.0 - _HOOK_GAP_HALF_ANGLE)
    n = 28
    profile: list[tuple[float, float]] = []
    for i in range(n + 1):
        a = a_start + (a_end - a_start) * i / n
        profile.append((hook_outer_r * math.cos(a), hook_outer_r * math.sin(a)))
    for i in range(n + 1):
        a = a_end - (a_end - a_start) * i / n
        profile.append((hook_inner_r * math.cos(a), hook_inner_r * math.sin(a)))

    half_w = _PADDLE_W / 2.0
    hook = cq.Workplane("XZ").polyline(profile).close().extrude(_PADDLE_W)
    hook = hook.translate((0, half_w, 0))

    blade_h = r.handle_len * 0.92
    blade_wx = max(_PLATE_T * 4.0, r.handle_len * 0.30)
    blade = (
        cq.Workplane("XY")
        .box(blade_wx, _PADDLE_W, blade_h)
        .translate((reach_dir * r.handle_len * 0.15, 0, blade_h / 2.0))
    )
    paddle = hook.union(blade)
    try:
        paddle = paddle.edges("|Z").fillet(_PLATE_T * 1.5)
    except Exception:
        pass
    return paddle


def _build_handle_visuals(r: ResolvedClipConfig, handle, reach_dir: float, *, mat, assets) -> None:
    """Emit the chosen handle style's visual(s) onto ``handle`` (lip-local frame)."""
    if r.handle_style == "flat_paddle_lever":
        paddle = _paddle_cq(r, reach_dir)
        handle.visual(
            mesh_from_cadquery(
                paddle, "paddle", assets=assets, tolerance=0.0004, angular_tolerance=0.2
            ),
            material=mat,
            name="paddle", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"orange_steel", "silver_steel"} else "metal.stainless_matte"),
        )
        return
    if r.handle_style == "double_wire_strand":
        offsets = [(i - (_STRAND_COUNT - 1) / 2.0) * _STRAND_SPACING for i in range(_STRAND_COUNT)]
        for i in range(_STRAND_COUNT):
            pts = _strand_points(r, reach_dir, offsets[i])
            handle.visual(
                _wire_mesh(pts, f"strand_{i}"),
                material=mat,
                name=f"strand_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"orange_steel", "silver_steel"} else "metal.stainless_matte"),
            )
        return
    if r.handle_style == "teardrop_wire_loop":
        pts = _teardrop_points(r, reach_dir)
        handle.visual(_wire_mesh(pts, "loop", samples=18), material=mat, name="loop", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"orange_steel", "silver_steel"} else "metal.stainless_matte"))
        return
    # wire_u_loop (baseline)
    pts = _wire_u_points(r, reach_dir)
    handle.visual(_wire_mesh(pts, "loop"), material=mat, name="loop", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"orange_steel", "silver_steel"} else "metal.stainless_matte"))


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
# Handle config table: index i -> handle_{i}. Front lip first, then rear lip.
def _handle_specs(r: ResolvedClipConfig):
    """(lip_x, lip_z, reach_dir, axis_y) for each of the n_handles levers."""
    specs = [(r.front_lip[0], r.front_lip[1], -1.0, 1.0)]
    if r.n_handles >= 2:
        specs.append((r.rear_lip[0], r.rear_lip[1], 1.0, -1.0))
    return specs


def _handle_inertial_box(r: ResolvedClipConfig) -> tuple[float, float, float]:
    if r.handle_style == "flat_paddle_lever":
        return (r.handle_len * 0.45, _PADDLE_W, r.handle_len)
    return (r.handle_len * 0.45, 2.0 * r.handle_half_w, r.handle_len)


def build_clip(
    config: ClipConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.material_style]
    mats = {
        key: model.material(f"clip_{key}_{r.material_style}", rgba=palette[key])
        for key in ("body", "handle")
    }

    # Root: front spring-steel jaw; child: rear jaw opening about the top fold.
    body = model.part("clip_body")
    body.visual(
        _build_jaw_mesh(r, rear=False, assets=assets),
        material=mats["body"],
        name="front_jaw_shell", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "silver_steel"} else "metal.paint_coated"),
    )
    body.inertial = Inertial.from_geometry(
        Box((r.half_d + 2.0 * r.lip_r, r.width, r.apex_z)),
        mass=0.012,
        origin=Origin(xyz=(-r.half_d * 0.45, 0.0, r.apex_z / 2.0)),
    )

    moving_jaw = model.part("moving_jaw")
    moving_jaw.visual(
        _build_jaw_mesh(r, rear=True, assets=assets),
        material=mats["body"],
        name="rear_jaw_shell", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "silver_steel"} else "metal.paint_coated"),
    )
    moving_jaw.inertial = Inertial.from_geometry(
        Box((r.half_d + 2.0 * r.lip_r, r.width, r.apex_z)),
        mass=0.012,
        origin=Origin(xyz=(r.half_d * 0.45, 0.0, -r.apex_z / 2.0)),
    )
    model.articulation(
        "jaw_open_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=moving_jaw,
        origin=Origin(xyz=(0.0, 0.0, r.apex_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=1.2, velocity=3.0, lower=0.0, upper=0.55),
    )

    # Parallel handle children: n_handles lever pivots about the lip Y axis.
    hbox = _handle_inertial_box(r)
    for i, (lip_x, lip_z, reach_dir, axis_y) in enumerate(_handle_specs(r)):
        parent = body if i == 0 else moving_jaw
        parent_lip_z = lip_z if i == 0 else lip_z - r.apex_z
        handle = model.part(f"handle_{i}")
        _build_handle_visuals(r, handle, reach_dir, mat=mats["handle"], assets=assets)
        handle.inertial = Inertial.from_geometry(
            Box(hbox),
            mass=0.004,
            origin=Origin(xyz=(reach_dir * r.handle_len * 0.22, 0.0, r.handle_len * 0.45)),
        )
        # REVOLUTE lever: joint frame at the lip center (on the real barrel),
        # axis along the lip (Y); positive q lifts the free end up (+Z).
        model.articulation(
            f"handle_{i}_pivot",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=handle,
            origin=Origin(xyz=(lip_x, 0.0, parent_lip_z)),
            axis=(0.0, axis_y, 0.0),
            motion_limits=MotionLimits(
                effort=0.4, velocity=4.0, lower=0.0, upper=_HANDLE_OPEN_LIMIT
            ),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_clip(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_clip(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _handle_visual_names(r: ResolvedClipConfig) -> list[str]:
    if r.handle_style == "flat_paddle_lever":
        return ["paddle"]
    if r.handle_style == "double_wire_strand":
        return [f"strand_{i}" for i in range(_STRAND_COUNT)]
    return ["loop"]


def run_clip_tests(
    object_model: ArticulatedObject,
    config: ClipConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("clip_body")
    moving_jaw = object_model.get_part("moving_jaw")

    # --- Captured-pin allowance: each handle is threaded through / hooked over
    #     the rolled lip barrel (the real capture fit). ---
    ctx.allow_overlap(
        body,
        moving_jaw,
        reason=(
            "the front and rear spring-steel leaves share the folded ridge where "
            "the jaw hinge is modeled."
        ),
    )
    for i in range(r.n_handles):
        handle = object_model.get_part(f"handle_{i}")
        handle_parent = body if i == 0 else moving_jaw
        ctx.allow_overlap(
            handle_parent,
            handle,
            reason=(
                "the lever handle is threaded through / hooked over the rolled lip "
                "barrel; a small handle/lip nest is the real capture fit."
            ),
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32)
    # Joints omit MatingContract (captured-pin lever / folded spring jaw,
    # grandfathered); the flat 0.015 m articulation-origin baseline runs in the
    # compiler and every pivot origin sits on real lip or ridge geometry.
    ctx.fail_if_joint_mating_has_gap()

    jaw_joint = object_model.get_articulation("jaw_open_hinge")
    ctx.check(
        "clip body has its own jaw-opening REVOLUTE joint",
        jaw_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(round(c, 3) for c in jaw_joint.axis) == (0.0, -1.0, 0.0),
        details=f"type={jaw_joint.articulation_type} axis={tuple(round(c, 3) for c in jaw_joint.axis)}",
    )
    closed_rear = ctx.part_world_aabb(moving_jaw)
    with ctx.pose({jaw_joint: 0.50}):
        open_rear = ctx.part_world_aabb(moving_jaw)
    if closed_rear is not None and open_rear is not None:
        ctx.check(
            "jaw_open_hinge swings the rear jaw outward to open the mouth",
            open_rear[1][0] > closed_rear[1][0] + 0.004,
            details=f"closed_xmax={closed_rear[1][0]:.4f} open_xmax={open_rear[1][0]:.4f}",
        )

    def _union_aabb(*aabbs):
        valid = [a for a in aabbs if a is not None]
        if not valid:
            return None
        mins = tuple(min(a[0][i] for a in valid) for i in range(3))
        maxs = tuple(max(a[1][i] for a in valid) for i in range(3))
        return mins, maxs

    # --- Body silhouette: folded jaw assembly resting on z=0, full width, apex up. ---
    body_aabb = ctx.part_world_aabb(body)
    rear_aabb = ctx.part_world_aabb(moving_jaw)
    jaw_aabb = _union_aabb(body_aabb, rear_aabb)
    if jaw_aabb is not None:
        (bx0, by0, bz0), (bx1, by1, bz1) = jaw_aabb
        ctx.check(
            "jaw assembly has the folded/dome apex height",
            (bz1 - bz0) > 0.010,
            details=f"height={bz1 - bz0:.4f}",
        )
        ctx.check(
            "jaw assembly spans the full clip width",
            (by1 - by0) > 0.028,
            details=f"width={by1 - by0:.4f}",
        )
        ctx.check(
            "jaw assembly mouth sits near z=0",
            bz0 < 0.003,
            details=f"z_min={bz0:.4f}",
        )
        ctx.check(
            "jaw assembly spans both lips front-to-rear",
            bx0 < r.front_lip[0] + 0.003 and bx1 > r.rear_lip[0] - 0.003,
            details=f"x=[{bx0:.4f},{bx1:.4f}] lips={r.front_lip[0]:.4f},{r.rear_lip[0]:.4f}",
        )

    # --- Handle multiplicity: exactly n_handles handle parts. ---
    handle_names = [p.name for p in object_model.parts if p.name.startswith("handle_")]
    ctx.check(
        "handle count matches n_handles",
        len(handle_names) == r.n_handles,
        details=f"handles={handle_names} expected={r.n_handles}",
    )

    # --- Per-handle: REVOLUTE about the lip Y axis, reaches past its lip, and
    #     squeezing lifts the free end. ---
    specs = _handle_specs(r)
    for i, (lip_x, _lip_z, reach_dir, _axis_y) in enumerate(specs):
        handle = object_model.get_part(f"handle_{i}")
        joint = object_model.get_articulation(f"handle_{i}_pivot")
        ctx.check(
            f"handle_{i} is REVOLUTE about the lip (Y) axis",
            joint.articulation_type == ArticulationType.REVOLUTE
            and abs(round(joint.axis[1], 3)) == 1.0
            and abs(round(joint.axis[0], 3)) == 0.0,
            details=f"type={joint.articulation_type} axis={tuple(round(c, 3) for c in joint.axis)}",
        )
        # Expected handle visuals exist.
        vis = {v.name for v in handle.visuals}
        expected = set(_handle_visual_names(r))
        ctx.check(
            f"handle_{i} has the {r.handle_style} visuals",
            expected.issubset(vis),
            details=f"visuals={sorted(vis)} expected={sorted(expected)}",
        )
        h_aabb = ctx.part_world_aabb(handle)
        if h_aabb is not None:
            if reach_dir < 0:
                ctx.check(
                    f"handle_{i} reaches outward past its lip (-X)",
                    h_aabb[0][0] < lip_x - 0.004,
                    details=f"x_min={h_aabb[0][0]:.4f} lip_x={lip_x:.4f}",
                )
            else:
                ctx.check(
                    f"handle_{i} reaches outward past its lip (+X)",
                    h_aabb[1][0] > lip_x + 0.004,
                    details=f"x_max={h_aabb[1][0]:.4f} lip_x={lip_x:.4f}",
                )
            with ctx.pose({joint: joint.motion_limits.upper}):
                open_aabb = ctx.part_world_aabb(handle)
            if open_aabb is not None:
                ctx.check(
                    f"handle_{i} swing stays above the clamp body instead of cutting through it",
                    open_aabb[1][2] > r.apex_z * 0.75,
                    details=f"apex_z={r.apex_z:.4f} swung_top={open_aabb[1][2]:.4f}",
                )

    # --- double_wire_strand: the two strands are side-by-side separated in Y. ---
    if r.handle_style == "double_wire_strand":
        h0 = object_model.get_part("handle_0")
        a0 = ctx.part_element_world_aabb(h0, elem="strand_0")
        a1 = ctx.part_element_world_aabb(h0, elem="strand_1")
        if a0 is not None and a1 is not None:
            c0 = (a0[0][1] + a0[1][1]) / 2.0
            c1 = (a1[0][1] + a1[1][1]) / 2.0
            ctx.check(
                "double-wire strands are separated in Y",
                abs(c1 - c0) > 0.0008,
                details=f"strand_0 yc={c0:.4f} strand_1 yc={c1:.4f}",
            )

    # --- serration teeth are body visuals (no FIXED decoration parts). ---
    if r.mouth_grip == "serrated_teeth":
        ctx.check(
            "serration teeth are fused into jaw meshes (no extra parts)",
            len(handle_names) == r.n_handles
            and "front_jaw_shell" in {v.name for v in body.visuals}
            and "rear_jaw_shell" in {v.name for v in moving_jaw.visuals},
            details=str([p.name for p in object_model.parts]),
        )

    # --- slot_choices recorded. ---
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "ClipConfig",
    "ResolvedClipConfig",
    "build_clip",
    "build_seeded_clip",
    "config_from_seed",
    "resolve_config",
    "run_clip_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
