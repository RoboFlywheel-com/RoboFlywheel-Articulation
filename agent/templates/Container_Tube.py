# SPDX-License-Identifier: Apache-2.0

"""Container tube — modular procedural template (soft squeeze tube).

Category identity: an upright soft squeeze tube (toothpaste / cosmetic cream /
serum / hand cream / glue). A hollow lofted shell ROOT rests on z=0 with a
**crimped flat tail** (wide and thin) at the base, rises through the body to a
narrowing shoulder, and dispenses through a top closure (the main articulation).
No multiplicity axis — one tube, one dispensing closure.

Two parallel slots (spec ``Container_Tube.md``):

  * ``body_footprint`` (5) — the ROOT ``tube_body`` ``body_shell`` mesh, a
    ``loft``-ed hollow shell with a crimped flat tail and a top bore:
      - slab_rect      : superellipse (p=3.4) slab — broad face, Y wide / X thin
      - round_to_flat  : classic squeeze tube — wide-thin crimp tail -> round neck
      - cylindrical    : constant-radius round barrel, soft tapered base
      - oval_lozenge   : smooth ellipse lozenge cross-section
      - tapered_cone   : monotone-narrowing cone/funnel from a wide crimp tail
  * ``closure_mechanism`` (8) — the dispensing/closing mechanism (>=1 non-fixed
    joint each), determines joint topology:
      - lift_cap          : PRISMATIC +Z lift-off cap over the open neck
      - screw_cap         : CONTINUOUS +Z spin + PRISMATIC +Z slide via a massless
                            ``cap_carrier`` (decoupled twist / lift)
      - flip_top          : REVOLUTE +X rear-hinged living-hinge flip cap
      - pull_cone         : PRISMATIC +Z pull-off cap over a pointed nozzle tip
      - standup_flip_cap  : body-fixed wide stand-up base disc + small REVOLUTE
                            -Y flip lid over the orifice
      - slant_applicator  : tilted applicator tip + PRISMATIC pull-off cap along
                            the tilted TIP_AXIS (not +Z)
      - roller_ball       : body-fixed dome housing + CONTINUOUS +X roller ball +
                            PRISMATIC +Z pull-off overcap (two movers)
      - twist_up_stick    : bottom CONTINUOUS +Z twist ring -> chained PRISMATIC
                            +Z platform inside the bore (two coupled joints)

Continuous size/proportion variation (height/radius/neck/closure/travel scales)
lives in ``resolve_config`` as clamped params, never as slot candidates.
``palette_style`` (10 coordinated colorways + finish) is palette-only and not a
slot; translucent finishes carry alpha < 1.

Sources (articraft_data ``picture/Container/Tube`` 5-star pool): parents
``...60b00467`` (slab + lift cap) and ``...7c11d416`` (round-to-flat + screw cap)
plus single-axis forks ``rec_container_tube_var_{cylindrical,oval_lozenge,
tapered_cone,flip_top,pull_cone,standup_cap,slant_applicator,roller_ball,
twist_up}``. Each module factory adapts the named source verbatim.

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Container_Tube.md``
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyFootprint = Literal[
    "slab_rect",
    "round_to_flat",
    "cylindrical",
    "oval_lozenge",
    "tapered_cone",
]
BodyProfileStyle = Literal[
    "straight",
    "waisted",
    "bulged",
]
ClosureMechanism = Literal[
    "lift_cap",
    "screw_cap",
    "flip_top",
    "pull_cone",
    "standup_flip_cap",
    "slant_applicator",
    "roller_ball",
    "twist_up_stick",
]
GraphicsStyle = Literal[
    "front_panel",
    "vertical_stripe",
    "dual_stripe",
    "wrap_band",
    "none",
]
TailDetailStyle = Literal[
    "plain",
    "single_crimp",
    "double_crimp",
]
ClosureTrimStyle = Literal[
    "plain",
    "single_band",
    "double_band",
    "ribbed",
]
PaletteStyle = Literal[
    "blue_sunscreen",
    "pale_yellow_cream",
    "white_minimal",
    "teal_serum",
    "orange_glue",
    "steel_rollon",
    "pearl_blush_cosmetic",
    "bare_aluminum_glue",
    "charcoal_softtouch_twotone",
    "mint_translucent_gel",
]

BODY_FOOTPRINTS: tuple[BodyFootprint, ...] = (
    "slab_rect",
    "round_to_flat",
    "cylindrical",
    "oval_lozenge",
    "tapered_cone",
)
BODY_PROFILE_STYLES: tuple[BodyProfileStyle, ...] = (
    "straight",
    "waisted",
    "bulged",
)
CLOSURE_MECHANISMS: tuple[ClosureMechanism, ...] = (
    "lift_cap",
    "screw_cap",
    "flip_top",
    "pull_cone",
    "standup_flip_cap",
    "slant_applicator",
    "roller_ball",
    "twist_up_stick",
)
GRAPHICS_STYLES: tuple[GraphicsStyle, ...] = (
    "front_panel",
    "vertical_stripe",
    "dual_stripe",
    "wrap_band",
    "none",
)
TAIL_DETAIL_STYLES: tuple[TailDetailStyle, ...] = (
    "plain",
    "single_crimp",
    "double_crimp",
)
TRIM_STYLES: tuple[ClosureTrimStyle, ...] = (
    "plain",
    "single_band",
    "double_band",
    "ribbed",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "blue_sunscreen",
    "pale_yellow_cream",
    "white_minimal",
    "teal_serum",
    "orange_glue",
    "steel_rollon",
    "pearl_blush_cosmetic",
    "bare_aluminum_glue",
    "charcoal_softtouch_twotone",
    "mint_translucent_gel",
)

# ---------------------------------------------------------------------------
# Palette: 10 coordinated colorways + an explicit finish dimension.
# Each colorway colors body / cap (closure) / accent (shoulder, nozzle, housing)
# / print (labels, ridges, markers). Translucent finishes carry alpha < 1.
# Anchored on the 5-star source materials; inferred colorways are
# structure-neutral. ``body2`` is an optional two-tone upper-body color.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, object]] = {
    "blue_sunscreen": {
        "finish": "gloss_laminate",
        "body": (0.62, 0.80, 0.92, 1.0),
        "cap": (0.95, 0.96, 0.97, 1.0),
        "accent": (0.95, 0.96, 0.97, 1.0),
        "print": (1.0, 1.0, 1.0, 1.0),
    },
    "pale_yellow_cream": {
        "finish": "matte",
        "body": (0.93, 0.89, 0.66, 1.0),
        "cap": (0.96, 0.96, 0.95, 1.0),
        "accent": (0.78, 0.80, 0.82, 1.0),
        "print": (0.78, 0.80, 0.82, 1.0),
    },
    "white_minimal": {
        "finish": "matte",
        "body": (0.96, 0.96, 0.95, 1.0),
        "cap": (0.94, 0.94, 0.93, 1.0),
        "accent": (0.82, 0.82, 0.80, 1.0),
        "print": (0.82, 0.82, 0.80, 1.0),
    },
    "teal_serum": {
        "finish": "gloss_laminate",
        "body": (0.93, 0.89, 0.66, 1.0),
        "cap": (0.30, 0.58, 0.62, 1.0),
        "accent": (0.72, 0.76, 0.78, 1.0),
        "print": (0.72, 0.76, 0.78, 1.0),
    },
    "orange_glue": {
        "finish": "gloss_laminate",
        "body": (0.62, 0.80, 0.92, 1.0),
        "cap": (0.95, 0.65, 0.25, 1.0),
        "accent": (1.0, 1.0, 1.0, 1.0),
        "print": (1.0, 1.0, 1.0, 1.0),
    },
    "steel_rollon": {
        "finish": "metallic_laminate",
        "body": (0.93, 0.89, 0.66, 1.0),
        "cap": (0.88, 0.92, 0.95, 0.85),  # translucent overcap
        "accent": (0.72, 0.73, 0.75, 1.0),
        "print": (0.85, 0.25, 0.20, 1.0),
    },
    "pearl_blush_cosmetic": {
        "finish": "pearlescent",
        "body": (0.95, 0.84, 0.86, 1.0),
        "cap": (0.86, 0.70, 0.62, 1.0),
        "accent": (0.97, 0.93, 0.92, 1.0),
        "print": (0.86, 0.70, 0.62, 1.0),
    },
    "bare_aluminum_glue": {
        "finish": "bare_aluminum",
        "body": (0.80, 0.81, 0.83, 1.0),
        "cap": (0.94, 0.94, 0.93, 1.0),
        "accent": (0.72, 0.73, 0.75, 1.0),
        "print": (0.15, 0.15, 0.15, 1.0),
    },
    "charcoal_softtouch_twotone": {
        "finish": "soft_touch_twotone",
        "body": (0.22, 0.23, 0.25, 1.0),
        "body2": (0.46, 0.36, 0.28, 1.0),  # two-tone upper body
        "cap": (0.18, 0.19, 0.21, 1.0),
        "accent": (0.13, 0.13, 0.14, 1.0),
        "print": (0.72, 0.52, 0.34, 1.0),
    },
    "mint_translucent_gel": {
        "finish": "translucent",
        "body": (0.70, 0.92, 0.82, 0.72),  # translucent gel body
        "cap": (0.95, 0.96, 0.97, 1.0),
        "accent": (0.62, 0.86, 0.80, 0.72),
        "print": (0.18, 0.45, 0.36, 1.0),
    },
}

# Functional sub-part materials that keep their own appearance per the 5-star
# sources (do not follow the colorway): steel roller ball.
_STEEL_RGBA = (0.72, 0.73, 0.75, 1.0)


# ---------------------------------------------------------------------------
# Base geometry per footprint (meters). Scaled per-build by resolve_config.
# A squeeze tube stands on a crimped flat tail at z=0 (wide across Y, thin
# across X), rises through the body to a narrowing shoulder, then an open round
# neck. Each footprint declares its cross-section family + datums; the closure
# builders mount onto the shared neck datum (NECK_R / NECK_TOP / SHOULDER_TOP).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _FootprintGeom:
    kind: str  # "slab" | "round_flat" | "cyl" | "oval" | "cone"
    half_w: float  # half-width across Y at the belly (the broad face)
    half_t: float  # half-thickness across X at the belly (the thin face)
    crimp_half_w: float  # half-width of the flat crimp tail at z=0 (wide)
    crimp_half_t: float  # half-thickness of the flat crimp tail at z=0 (thin)
    body_top: float  # top of the main body wall (start of the shoulder)
    shoulder_top: float  # top of the shoulder (neck base)
    neck_r: float
    neck_top: float
    wall: float
    # label band z extents
    label_z0: float
    label_z1: float


_FOOTPRINTS: dict[BodyFootprint, _FootprintGeom] = {
    # slab superellipse (parent ...60b00467): broad Y face, thin X
    "slab_rect": _FootprintGeom(
        kind="slab", half_w=0.018, half_t=0.0095, crimp_half_w=0.018,
        crimp_half_t=0.0022, body_top=0.090, shoulder_top=0.104,
        neck_r=0.0070, neck_top=0.118, wall=0.0016,
        label_z0=0.020, label_z1=0.072,
    ),
    # classic round-to-flat squeeze tube (parent ...7c11d416)
    "round_to_flat": _FootprintGeom(
        kind="round_flat", half_w=0.016, half_t=0.016, crimp_half_w=0.018,
        crimp_half_t=0.0022, body_top=0.090, shoulder_top=0.104,
        neck_r=0.0072, neck_top=0.118, wall=0.0016,
        label_z0=0.020, label_z1=0.072,
    ),
    # constant-radius round barrel (var_cylindrical)
    "cylindrical": _FootprintGeom(
        kind="cyl", half_w=0.0150, half_t=0.0150, crimp_half_w=0.0150,
        crimp_half_t=0.0150, body_top=0.092, shoulder_top=0.106,
        neck_r=0.0072, neck_top=0.120, wall=0.0016,
        label_z0=0.020, label_z1=0.074,
    ),
    # smooth ellipse lozenge (var_oval_lozenge)
    "oval_lozenge": _FootprintGeom(
        kind="oval", half_w=0.0185, half_t=0.0105, crimp_half_w=0.0185,
        crimp_half_t=0.0030, body_top=0.090, shoulder_top=0.104,
        neck_r=0.0070, neck_top=0.118, wall=0.0016,
        label_z0=0.020, label_z1=0.072,
    ),
    # monotone-narrowing cone/funnel (var_tapered_cone)
    "tapered_cone": _FootprintGeom(
        kind="cone", half_w=0.020, half_t=0.012, crimp_half_w=0.020,
        crimp_half_t=0.0024, body_top=0.092, shoulder_top=0.106,
        neck_r=0.0066, neck_top=0.120, wall=0.0016,
        label_z0=0.022, label_z1=0.074,
    ),
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ContainerTubeConfig:
    body_footprint: BodyFootprint = "slab_rect"
    body_profile_style: BodyProfileStyle = "straight"
    closure_mechanism: ClosureMechanism = "lift_cap"
    graphics_style: GraphicsStyle = "front_panel"
    tail_detail_style: TailDetailStyle = "single_crimp"
    closure_trim_style: ClosureTrimStyle = "plain"
    palette_style: PaletteStyle = "blue_sunscreen"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    neck_radius_scale: float = 1.0
    closure_size_scale: float = 1.0
    joint_travel_scale: float = 1.0
    name: str = "container_tube"


@dataclass(frozen=True)
class ResolvedContainerTubeConfig:
    body_footprint: BodyFootprint
    body_profile_style: BodyProfileStyle
    closure_mechanism: ClosureMechanism
    graphics_style: GraphicsStyle
    tail_detail_style: TailDetailStyle
    closure_trim_style: ClosureTrimStyle
    palette_style: PaletteStyle
    body_height_scale: float
    body_radius_scale: float
    neck_radius_scale: float
    closure_size_scale: float
    joint_travel_scale: float
    # derived body geometry (after scales)
    kind: str
    half_w: float
    half_t: float
    crimp_half_w: float
    crimp_half_t: float
    body_top: float
    shoulder_top: float
    neck_r: float
    neck_top: float
    wall: float
    bore_r: float
    label_z0: float
    label_z1: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerTubeConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    return ContainerTubeConfig(
        body_footprint=rng.choice(BODY_FOOTPRINTS),
        body_profile_style=rng.choice(BODY_PROFILE_STYLES),
        closure_mechanism=rng.choice(CLOSURE_MECHANISMS),
        graphics_style=rng.choice(GRAPHICS_STYLES),
        tail_detail_style=rng.choice(TAIL_DETAIL_STYLES),
        closure_trim_style=rng.choice(TRIM_STYLES),
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.85, 1.20), 4),
        body_radius_scale=round(rng.uniform(0.85, 1.18), 4),
        neck_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        closure_size_scale=round(rng.uniform(0.88, 1.15), 4),
        joint_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_tube_{seed}",
    )


def resolve_config(
    config: ContainerTubeConfig | None = None,
) -> ResolvedContainerTubeConfig:
    cfg = config or ContainerTubeConfig()
    footprint = _pick(cfg.body_footprint, BODY_FOOTPRINTS)
    profile = _pick(cfg.body_profile_style, BODY_PROFILE_STYLES)
    closure = _pick(cfg.closure_mechanism, CLOSURE_MECHANISMS)
    graphics = _pick(cfg.graphics_style, GRAPHICS_STYLES)
    tail_detail = _pick(cfg.tail_detail_style, TAIL_DETAIL_STYLES)
    trim = _pick(cfg.closure_trim_style, TRIM_STYLES)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    g = _FOOTPRINTS[footprint]

    h_scale = _clamp(cfg.body_height_scale, 0.85, 1.20)
    r_scale = _clamp(cfg.body_radius_scale, 0.85, 1.18)
    n_scale = _clamp(cfg.neck_radius_scale, 0.90, 1.10)
    cs_scale = _clamp(cfg.closure_size_scale, 0.88, 1.15)
    jt_scale = _clamp(cfg.joint_travel_scale, 0.85, 1.10)

    half_w = g.half_w * r_scale
    half_t = g.half_t * r_scale
    # crimp tail: keep the wide-thin flat ratio (>= 4:1) for round_flat / cone /
    # slab / oval; cylindrical keeps a round soft base (no flat crimp).
    crimp_half_w = g.crimp_half_w * r_scale
    crimp_half_t = g.crimp_half_t * r_scale
    if g.kind != "cyl":
        # enforce CRIMP_HALF_W >= 4 * CRIMP_HALF_T (flat squeeze crimp)
        crimp_half_t = min(crimp_half_t, crimp_half_w / 4.0)

    body_top = g.body_top * h_scale
    shoulder_top = g.shoulder_top * h_scale
    neck_top = g.neck_top * h_scale

    # neck radius follows its own scale, clamped to stay inside the shoulder.
    neck_r = _clamp(g.neck_r * n_scale, 0.0045, min(half_w, half_t) - 0.0016)
    bore_r = max(neck_r - g.wall, 0.0025)

    return ResolvedContainerTubeConfig(
        body_footprint=footprint,
        body_profile_style=profile,
        closure_mechanism=closure,
        graphics_style=graphics,
        tail_detail_style=tail_detail,
        closure_trim_style=trim,
        palette_style=palette,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        neck_radius_scale=n_scale,
        closure_size_scale=cs_scale,
        joint_travel_scale=jt_scale,
        kind=g.kind,
        half_w=half_w,
        half_t=half_t,
        crimp_half_w=crimp_half_w,
        crimp_half_t=crimp_half_t,
        body_top=body_top,
        shoulder_top=shoulder_top,
        neck_r=neck_r,
        neck_top=neck_top,
        wall=g.wall,
        bore_r=bore_r,
        label_z0=g.label_z0 * h_scale,
        label_z1=g.label_z1 * h_scale,
        name=cfg.name or "container_tube",
    )


def with_overrides(config: ContainerTubeConfig, **kwargs: object) -> ContainerTubeConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerTubeConfig | ResolvedContainerTubeConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedContainerTubeConfig)
        else resolve_config(config)
    )
    return (
        ("body_footprint", r.body_footprint),
        ("closure_mechanism", r.closure_mechanism),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Body geometry (Slot A). Each footprint adapts its named 5-star source.
# A squeeze tube is a hollow lofted shell: a crimped flat tail at z=0 widens to
# the belly, rises through the body, and tapers at the shoulder to a round open
# neck with a through bore. Built as outer loft solid - inner cavity loft.
# ---------------------------------------------------------------------------
def _superellipse_pts(half_w: float, half_t: float, p: float, n: int = 48):
    """Superellipse loop in the XY plane: |x/half_t|^p + |y/half_w|^p = 1.

    X is the thin axis (half_t), Y is the broad axis (half_w)."""
    pts = []
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        c = math.cos(ang)
        s = math.sin(ang)
        x = half_t * math.copysign(abs(c) ** (2.0 / p), c)
        y = half_w * math.copysign(abs(s) ** (2.0 / p), s)
        pts.append((x, y))
    return pts


def _ellipse_pts(half_w: float, half_t: float, n: int = 48):
    """Pure ellipse loop: X thin (half_t), Y broad (half_w)."""
    return [
        (half_t * math.cos(2.0 * math.pi * i / n), half_w * math.sin(2.0 * math.pi * i / n))
        for i in range(n)
    ]


def _circle_pts(radius: float, n: int = 48):
    return [
        (radius * math.cos(2.0 * math.pi * i / n), radius * math.sin(2.0 * math.pi * i / n))
        for i in range(n)
    ]


def _wire_at(pts, z: float) -> cq.Wire:
    """A closed planar wire from XY points, lifted to height z."""
    vecs = [cq.Vector(x, y, z) for (x, y) in pts]
    vecs.append(vecs[0])
    return cq.Wire.makePolygon(vecs)


def _section_pts(r: ResolvedContainerTubeConfig, hw: float, ht: float):
    """Cross-section loop points at scale (hw, ht) for this footprint family."""
    kind = r.kind
    if kind == "slab":
        return _superellipse_pts(hw, ht, 3.4)
    if kind == "oval":
        return _ellipse_pts(hw, ht)
    if kind in ("round_flat", "cone"):
        # rounded super-ellipse blending wide-thin crimp toward round neck
        return _superellipse_pts(hw, ht, 2.2)
    # cyl: circle
    return _circle_pts(max(hw, ht))


def _crimp_pts(r: ResolvedContainerTubeConfig, hw: float, ht: float):
    """The flat crimp tail loop at the base (wide-thin) for non-round footprints."""
    if r.kind == "cyl":
        return _circle_pts(max(hw, ht))
    # a thin wide rounded slot
    return _superellipse_pts(hw, ht, 6.0)


def _body_levels(r: ResolvedContainerTubeConfig):
    """(z, half_w, half_t) levels from the crimp tail up to the neck base.

    Returns the outer-profile control levels for the loft."""
    chw, cht = r.crimp_half_w, r.crimp_half_t
    bw, bt = r.half_w, r.half_t
    bp = r.body_top
    st = r.shoulder_top
    nr = r.neck_r
    if r.kind == "cyl":
        # barrel: soft tapered base -> constant radius
        levels = [
            (0.0, chw * 0.78, cht * 0.78),
            (0.006, chw, cht),
            (bp, bw, bt),
            (st, nr + 0.0015, nr + 0.0015),
        ]
    elif r.kind == "cone":
        # monotone narrowing from wide crimp to round neck
        levels = [
            (0.0, chw, cht),
            (bp * 0.5, (chw + bw) * 0.5 * 0.86, (cht + bt) * 0.5 + bt * 0.5),
            (bp, bw * 0.72, bt * 1.0),
            (st, nr + 0.0015, nr + 0.0015),
        ]
    else:
        # slab / round_flat / oval: crimp tail -> belly -> shoulder
        levels = [
            (0.0, chw, cht),
            (0.010, chw * 0.98, (cht + bt) * 0.5),
            (bp, bw, bt),
            (st, nr + 0.0015, nr + 0.0015),
        ]

    shoulder = (st, nr + 0.0015, nr + 0.0015)
    if r.body_profile_style == "waisted":
        if r.kind == "cyl":
            return [
                levels[0],
                levels[1],
                (bp * 0.48, bw * 0.92, bt * 0.92),
                (bp, bw * 0.98, bt * 0.98),
                shoulder,
            ]
        if r.kind == "cone":
            return [
                levels[0],
                (bp * 0.38, bw * 0.80, bt * 0.95),
                (bp * 0.72, bw * 0.66, bt * 0.88),
                shoulder,
            ]
        return [
            levels[0],
            levels[1],
            (bp * 0.52, bw * 0.90, bt * 0.90),
            (bp, bw * 0.97, bt * 0.97),
            shoulder,
        ]
    if r.body_profile_style == "bulged":
        if r.kind == "cyl":
            return [
                levels[0],
                levels[1],
                (bp * 0.45, bw * 1.06, bt * 1.06),
                (bp, bw * 1.01, bt * 1.01),
                shoulder,
            ]
        if r.kind == "cone":
            return [
                levels[0],
                (bp * 0.34, bw * 0.92, bt * 1.02),
                (bp * 0.70, bw * 0.78, bt * 1.04),
                shoulder,
            ]
        return [
            levels[0],
            levels[1],
            (bp * 0.44, bw * 1.05, bt * 1.05),
            (bp, bw * 1.01, bt * 1.01),
            shoulder,
        ]
    return levels


def _inner_profile_dims(
    hw: float,
    ht: float,
    *,
    wall: float,
    min_skin: float = 0.00045,
) -> tuple[float, float]:
    """Inset one body section while guaranteeing a real outer shell remains."""
    inner_hw = max(min(hw - wall, hw - min_skin), min_skin)
    inner_ht = max(min(ht - wall, ht - min_skin), min_skin)
    return inner_hw, inner_ht


def _body_inner_levels(
    r: ResolvedContainerTubeConfig,
    outer_levels: list[tuple[float, float, float]],
) -> list[tuple[float, float, float]]:
    """Inner cavity profile with a sealed tail and safe inset at every section.

    The previous implementation clamped lower sections to ``bore_r`` too early,
    which could exceed the thin crimp-tail section and punch through the bottom.
    This keeps the cavity strictly inside the outer shell until it reaches the
    shoulder/neck transition where the round bore takes over.
    """
    seal_z = max(r.wall * 1.6, 0.0018)
    min_skin = max(r.wall * 0.38, 0.00045)

    levels: list[tuple[float, float, float]] = []
    for idx, (z, hw, ht) in enumerate(outer_levels):
        if idx == len(outer_levels) - 1:
            bore = max(min(r.bore_r, r.neck_r - min_skin), 0.0025)
            levels.append((z, bore, bore))
            continue

        inner_hw, inner_ht = _inner_profile_dims(hw, ht, wall=r.wall, min_skin=min_skin)
        if idx == 0:
            levels.append((seal_z, inner_hw, inner_ht))
            continue

        # Keep the cavity from flaring wider than the local shell near the tail.
        if z <= r.body_top * 0.18:
            inner_ht = min(inner_ht, max(ht - min_skin, min_skin * 1.1))
        z = max(z, levels[-1][0] + 0.0006)
        levels.append((z, inner_hw, inner_ht))

    return levels


def _loft_levels(r: ResolvedContainerTubeConfig, levels, *, crimp_base: bool) -> cq.Workplane:
    wires = []
    for idx, (z, hw, ht) in enumerate(levels):
        if idx == 0 and crimp_base:
            pts = _crimp_pts(r, hw, ht)
        else:
            pts = _section_pts(r, hw, ht)
        wires.append(_wire_at(pts, z))
    solid = cq.Solid.makeLoft(wires, ruled=True)
    return cq.Workplane("XY").newObject([solid])


def _body_shell_solid(r: ResolvedContainerTubeConfig) -> cq.Workplane:
    """Hollow lofted squeeze-tube shell with a through bore at the neck."""
    levels = _body_levels(r)
    w = r.wall
    outer = _loft_levels(r, levels, crimp_base=True)
    # neck: round open tube from shoulder_top to neck_top
    neck = (
        cq.Workplane("XY")
        .workplane(offset=r.shoulder_top)
        .circle(r.neck_r)
        .extrude(r.neck_top - r.shoulder_top)
    )
    solid = outer.union(neck)

    # inner cavity: leave a real sealed tail, then transition into the bore.
    inner_levels = _body_inner_levels(r, levels)
    cavity = _loft_levels(r, inner_levels, crimp_base=True)
    bore = (
        cq.Workplane("XY")
        .workplane(offset=r.shoulder_top - 0.001)
        .circle(r.bore_r)
        .extrude(r.neck_top - r.shoulder_top + 0.002)
    )
    cavity = cavity.union(bore)
    return solid.cut(cavity)


def _surface_dims_at_z(r: ResolvedContainerTubeConfig, z: float) -> tuple[float, float]:
    """Interpolate the resolved body profile at a given z for host-derived overlays."""
    levels = _body_levels(r)
    if z <= levels[0][0]:
        return levels[0][1], levels[0][2]
    for (z0, hw0, ht0), (z1, hw1, ht1) in zip(levels, levels[1:]):
        if z <= z1:
            span = max(z1 - z0, 1e-6)
            t = (z - z0) / span
            return hw0 + (hw1 - hw0) * t, ht0 + (ht1 - ht0) * t
    return levels[-1][1], levels[-1][2]


def _overlay_levels(r: ResolvedContainerTubeConfig, z0: float, z1: float) -> list[tuple[float, float, float]]:
    if z1 <= z0:
        z1 = z0 + 0.001
    zmid = (z0 + z1) * 0.5
    zq1 = z0 + (z1 - z0) * 0.28
    zq3 = z0 + (z1 - z0) * 0.72
    zs = [z0, zq1, zmid, zq3, z1]
    return [(z, *_surface_dims_at_z(r, z)) for z in zs]


def _offset_levels(
    levels: list[tuple[float, float, float]],
    *,
    offset: float,
) -> list[tuple[float, float, float]]:
    return [(z, hw + offset, ht + offset) for z, hw, ht in levels]


def _body_overlay_shell(
    r: ResolvedContainerTubeConfig,
    *,
    z0: float,
    z1: float,
    inner_offset: float = -0.0012,
    outer_offset: float = 0.00055,
) -> cq.Workplane:
    """Thin shell derived from the final body surface, used for conformal decoration.

    inner_offset is negative so the overlay's inner face sits *inside* the body
    wall (embedded 1.2mm, under the 1.6mm wall). A flush overlay only touches
    the shell within mesh tolerance (1mm tessellation deflection on both
    surfaces), and the disconnected-geometry QC can then flag it as a floating
    island; the embedded core guarantees real contact while the visible outer
    face is unchanged.
    """
    levels = _overlay_levels(r, z0, z1)
    outer = _loft_levels(r, _offset_levels(levels, offset=outer_offset), crimp_base=False)
    inner = _loft_levels(r, _offset_levels(levels, offset=inner_offset), crimp_base=False)
    return outer.cut(inner)


def _front_clip(
    r: ResolvedContainerTubeConfig,
    *,
    z0: float,
    z1: float,
    y_half: float,
    x_depth: float = 0.006,
) -> cq.Workplane:
    center_z = (z0 + z1) * 0.5
    # The front face recedes below the belly half-thickness across most of the
    # label band; a clip anchored on the belly max can miss the overlay shell
    # entirely and leave floating slivers (disconnected-geometry islands).
    # Size the clip from the actual surface sweep over [z0, z1], with margins
    # that cover the embedded inner offset and the proud outer face.
    surface_ht = [ht for (_z, _hw, ht) in _overlay_levels(r, z0, z1)]
    x_min = min(surface_ht) - 0.0022
    x_max = max(surface_ht) + 0.0022
    x_span = max(x_max - x_min, x_depth)
    x_center = (x_min + x_max) * 0.5
    return (
        cq.Workplane("XY")
        .box(x_span, max(y_half * 2.0, 0.0015), max(z1 - z0, 0.0015), centered=(True, True, True))
        .translate((x_center, 0.0, center_z))
    )


def _label_band_mesh(r: ResolvedContainerTubeConfig):
    """Conformal wrap band derived from the resolved body surface."""
    return mesh_from_cadquery(
        _body_overlay_shell(r, z0=r.label_z0, z1=r.label_z1),
        "label_band",
    )


def _add_cadquery_visual(part, solid: cq.Workplane, *, mesh_name: str, material, name: str) -> bool:
    """Attach a CadQuery-derived visual, returning False when the shape is empty."""
    try:
        mesh = mesh_from_cadquery(solid, mesh_name)
    except ValueError:
        return False
    part.visual(mesh, material=material, name=name, appearance_only=AppearanceOnlySpec(kind="overlay"))
    return True


def _emit_graphics(body, r: ResolvedContainerTubeConfig, *, print_mat) -> None:
    """Appearance-only packaging graphics; stays off the joint interfaces."""
    style = r.graphics_style
    if style == "none":
        return
    shell = _body_overlay_shell(r, z0=r.label_z0, z1=r.label_z1)
    if style == "wrap_band":
        _add_cadquery_visual(body, shell, mesh_name="label_band", material=print_mat, name="label_band")
        return

    if style == "front_panel":
        clip = _front_clip(r, z0=r.label_z0, z1=r.label_z1, y_half=r.half_w * 0.58)
        if not _add_cadquery_visual(
            body, shell.intersect(clip), mesh_name="front_panel", material=print_mat, name="front_panel"
        ):
            _add_cadquery_visual(body, shell, mesh_name="label_band", material=print_mat, name="label_band")
        return
    if style == "vertical_stripe":
        clip = _front_clip(r, z0=r.label_z0, z1=r.label_z1, y_half=r.half_w * 0.17)
        if not _add_cadquery_visual(
            body, shell.intersect(clip), mesh_name="front_stripe", material=print_mat, name="front_stripe"
        ):
            fallback = _front_clip(r, z0=r.label_z0, z1=r.label_z1, y_half=r.half_w * 0.30)
            if not _add_cadquery_visual(
                body, shell.intersect(fallback), mesh_name="front_stripe_fallback", material=print_mat, name="front_stripe"
            ):
                _add_cadquery_visual(body, shell, mesh_name="label_band", material=print_mat, name="label_band")
        return

    # dual_stripe
    stripe_y = r.half_w * 0.30
    emitted = False
    for side, sign in (("left", -1.0), ("right", 1.0)):
        clip = (
            _front_clip(r, z0=r.label_z0, z1=r.label_z1, y_half=r.half_w * 0.11)
            .translate((0.0, sign * stripe_y, 0.0))
        )
        emitted = _add_cadquery_visual(
            body,
            shell.intersect(clip),
            mesh_name=f"{side}_stripe",
            material=print_mat,
            name=f"{side}_stripe",
        ) or emitted
    if not emitted:
        _add_cadquery_visual(
            body,
            shell,
            mesh_name="label_band",
            material=print_mat,
            name="label_band",
        )


def _emit_tail_detail(body, r: ResolvedContainerTubeConfig, *, accent_mat) -> None:
    style = r.tail_detail_style
    if style == "plain":
        return
    seam_clip_x = max(r.crimp_half_t * 5.0, r.half_t * 2.6, 0.0080)
    seam_span_y = max(r.crimp_half_w * 2.05, r.half_w * 1.28)
    z_positions = (0.0042,) if style == "single_crimp" else (0.0034, 0.0060)
    for idx, zc in enumerate(z_positions, start=1):
        band = _body_overlay_shell(
            r,
            z0=max(zc - 0.00055, 0.0014),
            z1=zc + 0.00055,
            outer_offset=0.00038,
        )
        clip = (
            cq.Workplane("XY")
            .box(seam_clip_x, seam_span_y, 0.0022, centered=(True, True, True))
            .translate((0.0, 0.0, zc))
        )
        _add_cadquery_visual(
            body,
            band.intersect(clip),
            mesh_name=f"tail_crimp_{idx}",
            material=accent_mat,
            name=f"tail_crimp_{idx}",
        )


def _cap_trim_solid(*, radius: float, z0: float, z1: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .circle(radius + 0.00045)
        .circle(max(radius - 0.00015, 0.0008))
        .extrude(max(z1 - z0, 0.0006))
    )


def _cap_trim_shell(
    *,
    radius: float,
    z_bottom: float,
    height: float,
    style: ClosureTrimStyle,
) -> cq.Workplane | None:
    if style == "plain" or height <= 0.004:
        return None
    if style == "single_band":
        return _cap_trim_solid(
            radius=radius,
            z0=z_bottom + height * 0.44,
            z1=z_bottom + height * 0.60,
        )
    if style == "double_band":
        return _cap_trim_solid(
            radius=radius,
            z0=z_bottom + height * 0.16,
            z1=z_bottom + height * 0.28,
        ).union(
            _cap_trim_solid(
                radius=radius,
                z0=z_bottom + height * 0.56,
                z1=z_bottom + height * 0.70,
            )
        )

    rings = []
    rib_h = max(height * 0.07, 0.0008)
    rib_gap = max(height * 0.12, 0.0014)
    cursor = z_bottom + height * 0.12
    while cursor + rib_h < z_bottom + height * 0.88:
        rings.append(_cap_trim_solid(radius=radius, z0=cursor, z1=cursor + rib_h))
        cursor += rib_gap
    if not rings:
        return None
    trim = rings[0]
    for ring in rings[1:]:
        trim = trim.union(ring)
    return trim


def _disc_trim_shell(
    *,
    radius: float,
    thickness: float,
    style: ClosureTrimStyle,
    hole_r: float = 0.0,
) -> cq.Workplane | None:
    if style == "plain":
        return None
    inner_r = max(radius * 0.48, 0.0012)
    outer_r = max(radius * 0.86, inner_r + 0.0012)
    if style == "single_band":
        rings = [(inner_r, outer_r)]
    elif style == "double_band":
        rings = [
            (max(radius * 0.28, 0.0010), max(radius * 0.52, 0.0022)),
            (max(radius * 0.64, 0.0034), max(radius * 0.88, 0.0046)),
        ]
    else:
        rings = [
            (max(radius * 0.20, 0.0010), max(radius * 0.34, 0.0018)),
            (max(radius * 0.42, 0.0020), max(radius * 0.56, 0.0028)),
            (max(radius * 0.64, 0.0030), max(radius * 0.80, 0.0038)),
        ]
    trim = None
    for r0, r1 in rings:
        # keep every ring fully supported on the disc: a ring that lands on
        # the center bore opening floats above the hole (geometry island).
        r0 = max(r0, hole_r + 0.0004)
        if r1 <= r0 + 0.0006:
            continue
        ring = (
            cq.Workplane("XY")
            .circle(r1)
            .circle(min(r0, r1 - 0.0006))
            .extrude(thickness)
        )
        trim = ring if trim is None else trim.union(ring)
    return trim


def _emit_body(
    body,
    r: ResolvedContainerTubeConfig,
    *,
    body_mat,
    body2_mat,
    print_mat,
    accent_mat,
) -> None:
    body.visual(mesh_from_cadquery(_body_shell_solid(r), "body_shell"), material=body_mat, name="body_shell", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))
    if body2_mat is not None:
        # two-tone upper-body band (decorative parent visual, no joint)
        z0 = r.body_top * 0.55
        z1 = r.shoulder_top
        body.visual(
            mesh_from_cadquery(
                _body_overlay_shell(r, z0=z0, z1=z1, outer_offset=0.00075),
                "body_twotone",
            ),
            material=body2_mat,
            name="body_twotone", material_class_id="rubber.smooth_plain",
        )
    _emit_graphics(body, r, print_mat=print_mat)
    _emit_tail_detail(body, r, accent_mat=accent_mat)
    body.inertial = Inertial.from_geometry(
        Box((2 * r.half_t, 2 * r.half_w, r.body_top)),
        mass=0.040,
        origin=Origin(xyz=(0.0, 0.0, r.body_top / 2.0)),
    )


# ---------------------------------------------------------------------------
# Closure builders (Slot B). Each adapts its named 5-star source verbatim.
# All rest poses are CLOSED / SEATED (q=0); opening is viewer-inspected motion.
# ---------------------------------------------------------------------------
def _open_neck_visual(body, r: ResolvedContainerTubeConfig, *, accent_mat) -> None:
    """Shared body-fixed open neck collar + lip ring at the shoulder top."""
    nr, nt = r.neck_r, r.neck_top
    lip = (
        cq.Workplane("XY")
        .workplane(offset=nt - 0.003)
        .circle(nr + 0.0012)
        .circle(r.bore_r)
        .extrude(0.003)
    )
    body.visual(mesh_from_cadquery(lip, "neck_lip"), material=accent_mat, name="neck_lip", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))


def _cap_shell_solid(r, *, cap_r, cap_h, wall, z_bottom):
    """Hollow round cap shell open at the bottom (skirt) — slips over the neck."""
    outer = cq.Workplane("XY").workplane(offset=z_bottom).circle(cap_r).extrude(cap_h)
    inner = (
        cq.Workplane("XY")
        .workplane(offset=z_bottom - 0.001)
        .circle(cap_r - wall)
        .extrude(cap_h - wall + 0.001)
    )
    return outer.cut(inner)


def _build_lift_cap(model, body, r, *, cap_mat, accent_mat) -> None:
    """Lift-off cap over the open neck — single PRISMATIC +Z (parent ...60b00467).

    Rest q=0 = seated. Origin anchored on the neck wall (off-axis, real glass on
    the parent side) per the 15mm origin check; the cap mesh is offset by
    -anchor so it stays centered on +Z."""
    _open_neck_visual(body, r, accent_mat=accent_mat)
    cs = r.closure_size_scale
    cap_r = max((r.neck_r + 0.0028) * cs, r.neck_r + 0.0014)
    cap_h = (r.neck_top - r.shoulder_top + 0.010)
    # wall sized so the skirt inner radius sits 0.4mm inside the open neck outer
    # radius (captured clip contact over the neck, regardless of closure scale).
    wall = max(cap_r - (r.neck_r - 0.0004), 0.0014)
    cap_bottom = r.shoulder_top + 0.002  # seated underside z at rest
    travel = (cap_h + 0.018) * r.joint_travel_scale
    anchor = r.neck_r

    cap = model.part("lift_cap")
    # Authored in the cap-local frame: skirt underside at local z=0 (= the joint
    # origin's seat z), shifted by -anchor in X so the off-axis origin re-centers
    # the cap on the tube axis.
    cap_solid = _cap_shell_solid(r, cap_r=cap_r, cap_h=cap_h, wall=wall, z_bottom=0.0).translate((-anchor, 0.0, 0.0))
    cap.visual(mesh_from_cadquery(cap_solid, "cap_shell"), material=cap_mat, name="cap_shell", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"pale_yellow_cream", "white_minimal", "steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.opaque_glossy_molded"))
    trim = _cap_trim_shell(radius=cap_r, z_bottom=0.0, height=cap_h, style=r.closure_trim_style)
    if trim is not None:
        cap.visual(
            mesh_from_cadquery(trim.translate((-anchor, 0.0, 0.0)), "cap_trim"),
            material=accent_mat,
            name="cap_trim", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"),
        )
    cap.inertial = Inertial.from_geometry(
        Cylinder(cap_r, cap_h), mass=0.006,
        origin=Origin(xyz=(-anchor, 0.0, cap_h * 0.5)),
    )
    model.articulation(
        "cap_lift",
        ArticulationType.PRISMATIC,
        parent=body,
        child=cap,
        origin=Origin(xyz=(anchor, 0.0, cap_bottom)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=travel, effort=6.0, velocity=0.2),
    )


def _build_screw_cap(model, body, r, *, cap_mat, accent_mat) -> None:
    """Screw cap: CONTINUOUS +Z spin + PRISMATIC +Z slide via a massless
    ``cap_carrier`` (parent ...7c11d416). The cap is authored in the carrier
    frame whose origin sits at the nozzle top (world z = neck_top)."""
    cs = r.closure_size_scale
    nt = r.neck_top
    # threaded nozzle (body-fixed visual) on top of the shoulder. Its outer
    # radius is kept wide enough that the cap skirt (inner radius) clips over it
    # for a captured screw-thread contact.
    nozzle_outer = r.neck_r + 0.0022
    nozzle = (
        cq.Workplane("XY")
        .workplane(offset=r.shoulder_top)
        .circle(nozzle_outer)
        .circle(r.bore_r)
        .extrude(nt - r.shoulder_top)
    )
    body.visual(mesh_from_cadquery(nozzle, "nozzle"), material=accent_mat, name="nozzle", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))

    cap_r = max((r.neck_r + 0.0034) * cs, nozzle_outer + 0.0014)
    # skirt drop stays 1.2mm above the shoulder even on the shortest neck, so
    # the skirt tube never grazes the widening shoulder wall below the nozzle.
    skirt_drop = min(0.012, (nt - r.shoulder_top) - 0.0012)
    cap_above = 0.007
    cap_h = skirt_drop + cap_above
    # wall sized so the skirt inner radius sits 0.4mm inside the nozzle outer
    # radius (captured clip contact, regardless of closure_size_scale).
    wall = max(cap_r - (nozzle_outer - 0.0004), 0.0014)
    # slide travel stays below the skirt drop: at full lift the skirt still
    # wraps the nozzle (a screw cap unscrews but stays captured on the thread),
    # instead of lifting clear and floating free of the body.
    lift = skirt_drop * 0.55 * r.joint_travel_scale

    carrier = model.part("cap_carrier")
    carrier.inertial = Inertial.from_geometry(Box((0.006, 0.006, 0.006)), mass=1e-4)
    model.articulation(
        "cap_rotate",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=carrier,
        origin=Origin(xyz=(0.0, 0.0, nt)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.0),
    )

    # cap authored about carrier frame: skirt bottom at local z=-skirt_drop.
    cap_solid = _cap_shell_solid(r, cap_r=cap_r, cap_h=cap_h, wall=wall, z_bottom=-skirt_drop)
    cap = model.part("cap")
    cap.visual(mesh_from_cadquery(cap_solid, "cap_shell"), material=cap_mat, name="cap_shell", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"pale_yellow_cream", "white_minimal", "steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.opaque_glossy_molded"))
    trim = _cap_trim_shell(radius=cap_r, z_bottom=-skirt_drop, height=cap_h, style=r.closure_trim_style)
    if trim is not None:
        cap.visual(mesh_from_cadquery(trim, "cap_trim"), material=accent_mat, name="cap_trim", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))
    # off-axis knurl marker so rotation is observable
    cap.visual(
        Box((0.0030, 0.0030, 0.0020)),
        origin=Origin(xyz=(cap_r - 0.0015, 0.0, cap_above - 0.002)),
        material=accent_mat,
        name="cap_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    cap.inertial = Inertial.from_geometry(
        Cylinder(cap_r, cap_h), mass=0.005,
        origin=Origin(xyz=(0.0, 0.0, (cap_above - skirt_drop) / 2.0)),
    )
    model.articulation(
        "cap_slide",
        ArticulationType.PRISMATIC,
        parent=carrier,
        child=cap,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=lift, effort=2.0, velocity=0.3),
    )


def _build_flip_top(model, body, r, *, cap_mat, accent_mat) -> None:
    """Rear-hinged living-hinge flip cap, REVOLUTE +X at the rear neck rim.
    Rest q=0 = closed over the mouth (parent var_flip_top)."""
    _open_neck_visual(body, r, accent_mat=accent_mat)
    cs = r.closure_size_scale
    nt = r.neck_top
    hinge_y = -(r.neck_r + 0.0022)
    open_upper = 2.4 * r.joint_travel_scale  # ~138 deg

    lid = model.part("flip_cap")
    # disc lid authored about the hinge frame (lid plane at local z=0), centered
    # forward by -hinge_y so it caps the mouth when closed (q=0).
    cap_r = (r.neck_r + 0.0022) * cs
    disc = (
        cq.Workplane("XY")
        .circle(cap_r)
        .extrude(0.0035)
        .translate((0.0, -hinge_y, 0.0))
    )
    # downward plug that seats into the bore
    plug = (
        cq.Workplane("XY")
        .workplane(offset=-0.004)
        .circle(r.bore_r - 0.0004)
        .extrude(0.004)
        .translate((0.0, -hinge_y, 0.0))
    )
    lid_solid = disc.union(plug)
    lid.visual(mesh_from_cadquery(lid_solid, "lid_shell"), material=cap_mat, name="lid_shell", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"pale_yellow_cream", "white_minimal", "steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.opaque_glossy_molded"))
    trim = _disc_trim_shell(radius=cap_r * 0.96, thickness=0.0012, style=r.closure_trim_style)
    if trim is not None:
        lid.visual(
            mesh_from_cadquery(trim.translate((0.0, -hinge_y, 0.0030)), "lid_trim"),
            material=accent_mat,
            name="lid_trim", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"),
        )
    # hinge knuckle on the lid at its local origin (on the hinge axis hardware)
    knuckle = (
        cq.Workplane("YZ")
        .circle(0.0028)
        .extrude(0.012)
        .translate((-0.006, 0.0, 0.0))
    )
    lid.visual(mesh_from_cadquery(knuckle, "lid_knuckle"), material=accent_mat, name="lid_knuckle", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))
    lid.inertial = Inertial.from_geometry(
        Cylinder(cap_r, 0.008), mass=0.004,
        origin=Origin(xyz=(0.0, -hinge_y, 0.002)),
    )
    model.articulation(
        "flip_cap",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, hinge_y, nt)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=open_upper, effort=3.0, velocity=2.0),
    )


def _build_pull_cone(model, body, r, *, cap_mat, accent_mat) -> None:
    """Pointed nozzle dispensing tip (body-fixed) + pull-off hollow cone cap,
    PRISMATIC +Z over the nozzle. Rest q=0 = seated (parent var_pull_cone)."""
    cs = r.closure_size_scale
    st = r.shoulder_top
    nozzle_base_r = r.neck_r + 0.0010
    tip_r = max(r.bore_r * 0.45, 0.0016)
    # mount the cone tip on a short upright collar that rises just above the
    # body's neck top, so the pull cap (seated over the tip) never reaches down
    # into the wide body shoulder.
    mount_z = r.neck_top + 0.002
    cone_h = 0.016
    # body-fixed upright collar from the shoulder up to the mount plane
    collar = (
        cq.Workplane("XY")
        .workplane(offset=st)
        .circle(nozzle_base_r)
        .circle(r.bore_r)
        .extrude(mount_z - st)
    )
    # body-fixed pointed cone tip with a through bore, sitting on the collar
    cone = (
        cq.Workplane("XY")
        .workplane(offset=mount_z)
        .circle(nozzle_base_r)
        .workplane(offset=cone_h)
        .circle(tip_r)
        .loft()
    )
    bore = (
        cq.Workplane("XY")
        .workplane(offset=st - 0.001)
        .circle(tip_r - 0.0006)
        .extrude((mount_z - st) + cone_h + 0.002)
    )
    body.visual(mesh_from_cadquery(collar.union(cone).cut(bore), "nozzle_tip"), material=accent_mat, name="nozzle_tip", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))

    cap_r = max((nozzle_base_r + 0.0022) * cs, nozzle_base_r + 0.0012)
    cap_h = cone_h + 0.006
    # wall sized so the skirt inner radius sits well inside the cone base
    # (captured fit), 1.0mm overlap so the cone's upward narrowing never gaps.
    wall = max(cap_r - (nozzle_base_r - 0.0010), 0.0014)
    cap_bottom = mount_z  # seated over the cone at rest (above the body neck)
    travel = (cap_h + 0.016) * r.joint_travel_scale
    anchor = nozzle_base_r

    cap = model.part("pull_cap")
    # cap-local frame: skirt underside at local z=0 (= joint origin seat z).
    cap_solid = _cap_shell_solid(r, cap_r=cap_r, cap_h=cap_h, wall=wall, z_bottom=0.0).translate((-anchor, 0.0, 0.0))
    cap.visual(mesh_from_cadquery(cap_solid, "cap_shell"), material=cap_mat, name="cap_shell", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"pale_yellow_cream", "white_minimal", "steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.opaque_glossy_molded"))
    trim = _cap_trim_shell(radius=cap_r, z_bottom=0.0, height=cap_h, style=r.closure_trim_style)
    if trim is not None:
        cap.visual(
            mesh_from_cadquery(trim.translate((-anchor, 0.0, 0.0)), "cap_trim"),
            material=accent_mat,
            name="cap_trim", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"),
        )
    cap.inertial = Inertial.from_geometry(
        Cylinder(cap_r, cap_h), mass=0.005,
        origin=Origin(xyz=(-anchor, 0.0, cap_h * 0.5)),
    )
    model.articulation(
        "cap_pull",
        ArticulationType.PRISMATIC,
        parent=body,
        child=cap,
        origin=Origin(xyz=(anchor, 0.0, cap_bottom)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=travel, effort=5.0, velocity=0.2),
    )


def _build_standup_flip_cap(model, body, r, *, cap_mat, accent_mat) -> None:
    """Wide stand-up base disc (body-fixed) on top of the shoulder/nozzle +
    a small REVOLUTE -Y flip lid over the orifice. The tube can stand inverted
    on the disc. Rest q=0 = closed (parent var_standup_cap)."""
    st = r.shoulder_top
    nt = r.neck_top
    # body-fixed nozzle short stub
    nozzle = (
        cq.Workplane("XY")
        .workplane(offset=st)
        .circle(r.neck_r + 0.0006)
        .circle(r.bore_r)
        .extrude(nt - st)
    )
    body.visual(mesh_from_cadquery(nozzle, "nozzle"), material=accent_mat, name="nozzle", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))
    # wide octagonal stand-up base disc (body-fixed), R > body radius for stability
    base_r = max(r.half_w, r.half_t) * 1.18 + 0.002
    disc_h = 0.006
    disc_z0 = nt
    disc = (
        cq.Workplane("XY")
        .workplane(offset=disc_z0)
        .polygon(8, 2.0 * base_r / math.cos(math.pi / 8))
        .circle(r.bore_r)
        .extrude(disc_h)
    )
    body.visual(mesh_from_cadquery(disc, "base_cap_disc"), material=cap_mat, name="base_cap_disc", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"pale_yellow_cream", "white_minimal", "steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.opaque_glossy_molded"))
    base_trim = _disc_trim_shell(radius=base_r * 0.96, thickness=0.0012, style=r.closure_trim_style, hole_r=r.bore_r)
    if base_trim is not None:
        body.visual(
            mesh_from_cadquery(base_trim.translate((0.0, 0.0, disc_z0 + disc_h - 0.0005)), "base_cap_trim"),
            material=accent_mat,
            name="base_cap_trim", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"),
        )
    # orifice ring on the disc top
    orifice = (
        cq.Workplane("XY")
        .workplane(offset=disc_z0 + disc_h)
        .circle(r.bore_r + 0.0018)
        .circle(r.bore_r)
        .extrude(0.0018)
    )
    body.visual(mesh_from_cadquery(orifice, "orifice_ring"), material=accent_mat, name="orifice_ring", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))
    # hinge barrel just behind the central orifice on the disc top (real flip-cap
    # hinge sits close to the dispensing hole, not at the wide disc's rim).
    lid_r = r.bore_r + 0.004
    hinge_x = -(lid_r + 0.0015)
    barrel_z = disc_z0 + disc_h + 0.0015
    barrel = (
        cq.Workplane("XZ")
        .workplane(offset=0.006)
        .circle(0.0022)
        .extrude(-0.012)
        .translate((hinge_x, 0.0, barrel_z))
    )
    body.visual(mesh_from_cadquery(barrel, "hinge_barrel"), material=accent_mat, name="hinge_barrel", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))

    open_upper = 2.0 * r.joint_travel_scale  # ~115 deg
    lid = model.part("flip_lid")
    # small lid disc authored about the hinge frame, centered forward over the
    # orifice (orifice at world x=0, hinge at x=hinge_x -> forward by -hinge_x).
    fwd = -hinge_x
    lid_disc = (
        cq.Workplane("XY")
        .circle(lid_r)
        .extrude(0.0030)
        .translate((fwd, 0.0, 0.0))
    )
    plug = (
        cq.Workplane("XY")
        .workplane(offset=-0.0028)
        .circle(r.bore_r - 0.0003)
        .extrude(0.0028)
        .translate((fwd, 0.0, 0.0))
    )
    # hinge strap bridging the lid disc back-edge to the hinge axis (local x=0),
    # keeping the part a single connected piece anchored on the hinge hardware.
    strap = (
        cq.Workplane("XY")
        .box(fwd + 0.001, 0.006, 0.0030, centered=(False, True, False))
        .translate((-0.0005, 0.0, 0.0))
    )
    lid.visual(mesh_from_cadquery(lid_disc.union(plug).union(strap), "lid_shell"), material=cap_mat, name="lid_shell", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"pale_yellow_cream", "white_minimal", "steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.opaque_glossy_molded"))
    lid_trim = _disc_trim_shell(radius=lid_r * 0.94, thickness=0.0010, style=r.closure_trim_style)
    if lid_trim is not None:
        lid.visual(
            mesh_from_cadquery(lid_trim.translate((fwd, 0.0, 0.0025)), "lid_trim"),
            material=accent_mat,
            name="lid_trim", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"),
        )
    # hinge knuckle at the lid local origin (on the hinge axis hardware, axis=-Y)
    knuckle = (
        cq.Workplane("XZ")
        .workplane(offset=0.005)
        .circle(0.0024)
        .extrude(-0.010)
    )
    lid.visual(mesh_from_cadquery(knuckle, "lid_knuckle"), material=accent_mat, name="lid_knuckle", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))
    lid.inertial = Inertial.from_geometry(
        Cylinder(lid_r, 0.006), mass=0.003,
        origin=Origin(xyz=(fwd * 0.5, 0.0, 0.0015)),
    )
    model.articulation(
        "lid_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(hinge_x, 0.0, barrel_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=open_upper, effort=2.0, velocity=2.0),
    )


def _build_slant_applicator(model, body, r, *, cap_mat, accent_mat) -> None:
    """Upright applicator tip with a slanted mouth cut + snap cap that pulls
    off along +Z. Rest q=0 = seated.

    The visual language stays "applicator-like", but the dispensing axis
    remains centered on the tube so the mouth no longer reads as skewed."""
    cs = r.closure_size_scale
    st = r.shoulder_top
    base_r = r.neck_r + 0.0010
    tip_r = max(r.bore_r * 0.5, 0.0018)
    # Keep the applicator centered on the tube axis; only the mouth opening
    # gets a slanted cosmetic cut.
    mount_z = r.neck_top + 0.004
    tip_len = 0.014

    riser = (
        cq.Workplane("XY")
        .workplane(offset=st)
        .circle(base_r)
        .circle(r.bore_r)
        .extrude(mount_z - st)
    )
    body.visual(mesh_from_cadquery(riser, "nozzle"), material=accent_mat, name="nozzle", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))

    # Body-fixed upright applicator tip with a tapered body.
    nozzle = (
        cq.Workplane("XY")
        .circle(base_r)
        .workplane(offset=tip_len)
        .circle(tip_r)
        .loft()
    )
    # Slanted mouth cut at the top without moving the overall tip off-axis.
    mouth_cut = (
        cq.Workplane("XZ")
        .box(base_r * 2.6, tip_len * 0.9, base_r * 2.6, centered=(True, True, True))
        .rotate((0, 0, 0), (1, 0, 0), -22.0)
        .translate((0.0, tip_len * 0.12, tip_len * 0.92))
    )
    bore = (
        cq.Workplane("XY")
        .workplane(offset=-0.001)
        .circle(tip_r - 0.0006)
        .extrude(tip_len + 0.002)
    )
    nozzle = nozzle.cut(bore).cut(mouth_cut).translate((0.0, 0.0, mount_z))
    body.visual(mesh_from_cadquery(nozzle, "applicator_tip"), material=accent_mat, name="applicator_tip", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))

    # Snap cap remains coaxial with the upright tip so the closure looks stable.
    cap_r = max((base_r + 0.0022) * cs, base_r + 0.0012)
    cap_h = tip_len + 0.006
    # wall sized so the skirt inner radius clips the tip base (captured fit).
    wall = max(cap_r - (base_r - 0.0004), 0.0014)
    cap = model.part("snap_cap")
    cap_solid = _cap_shell_solid(r, cap_r=cap_r, cap_h=cap_h, wall=wall, z_bottom=0.0)
    cap.visual(mesh_from_cadquery(cap_solid, "cap_shell"), material=cap_mat, name="cap_shell", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"pale_yellow_cream", "white_minimal", "steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.opaque_glossy_molded"))
    trim = _cap_trim_shell(radius=cap_r, z_bottom=0.0, height=cap_h, style=r.closure_trim_style)
    if trim is not None:
        cap.visual(
            mesh_from_cadquery(trim, "cap_trim"),
            material=accent_mat,
            name="cap_trim", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"),
        )
    cap.inertial = Inertial.from_geometry(
        Cylinder(cap_r, cap_h), mass=0.005,
        origin=Origin(xyz=(0.0, 0.0, cap_h * 0.5)),
    )
    travel = (cap_h + 0.014) * r.joint_travel_scale
    model.articulation(
        "cap_pull",
        ArticulationType.PRISMATIC,
        parent=body,
        child=cap,
        origin=Origin(xyz=(0.0, 0.0, mount_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=travel, effort=5.0, velocity=0.2),
    )


def _build_roller_ball(model, body, r, *, cap_mat, accent_mat, steel_mat) -> None:
    """Dome socket housing (body-fixed) + CONTINUOUS +X roller ball + PRISMATIC
    +Z pull-off overcap. Two movers. Rest q=0 = seated (parent var_roller_ball)."""
    cs = r.closure_size_scale
    st = r.shoulder_top
    nt = r.neck_top
    housing_r = (r.neck_r + 0.0030) * cs
    ball_r = 0.0042 * cs
    ball_cz = nt + 0.0020
    # body-fixed dome housing with a ball socket cup
    outer = (
        cq.Workplane("XY")
        .workplane(offset=st)
        .circle(housing_r)
        .extrude((nt - st) + 0.004)
    )
    h_bore = (
        cq.Workplane("XY")
        .workplane(offset=st - 0.001)
        .circle(r.bore_r)
        .extrude((nt - st) + 0.002)
    )
    housing = outer.cut(h_bore)
    socket = cq.Workplane("XY").workplane(offset=ball_cz).sphere(ball_r - 0.0001)
    housing = housing.cut(socket)
    body.visual(mesh_from_cadquery(housing, "housing"), material=accent_mat, name="housing", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))

    # roller ball — frame at the ball centre (origin sits on real ball geometry)
    ball = model.part("applicator_ball")
    ball.visual(Sphere(ball_r), origin=Origin(xyz=(0.0, 0.0, 0.0)), material=steel_mat, name="ball", material_class_id="metal.stainless_matte")
    # off-axis marker so the roll is observable
    ball.visual(
        Box((0.0010, 0.0010, 0.0010)),
        origin=Origin(xyz=(0.0, 0.0, ball_r - 0.0004)),
        material=accent_mat,
        name="ball_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    ball.inertial = Inertial.from_geometry(Sphere(ball_r), mass=0.003, origin=Origin(xyz=(0.0, 0.0, 0.0)))
    model.articulation(
        "ball_roll",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=ball,
        origin=Origin(xyz=(0.0, 0.0, ball_cz)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=5.0),
    )

    # pull-off translucent overcap — authored about its bottom rim frame. The
    # skirt inner radius (overcap_r - wall) is kept just inside the housing outer
    # radius so the overcap clips over the housing exterior (captured contact).
    overcap_r = housing_r + 0.0024
    overcap_h = (ball_cz - st) + ball_r + 0.012
    overcap_z0 = st + 0.002
    wall = 0.0030
    travel = (overcap_h + 0.012) * r.joint_travel_scale
    anchor = housing_r
    overcap = model.part("overcap")
    # overcap-local frame: skirt underside at local z=0 (= joint origin seat z).
    cap_solid = _cap_shell_solid(r, cap_r=overcap_r, cap_h=overcap_h, wall=wall, z_bottom=0.0).translate((-anchor, 0.0, 0.0))
    overcap.visual(mesh_from_cadquery(cap_solid, "overcap_shell"), material=cap_mat, name="overcap_shell", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"pale_yellow_cream", "white_minimal", "steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.opaque_glossy_molded"))
    trim = _cap_trim_shell(radius=overcap_r, z_bottom=0.0, height=overcap_h, style=r.closure_trim_style)
    if trim is not None:
        overcap.visual(
            mesh_from_cadquery(trim.translate((-anchor, 0.0, 0.0)), "overcap_trim"),
            material=accent_mat,
            name="overcap_trim", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"),
        )
    overcap.inertial = Inertial.from_geometry(
        Cylinder(overcap_r, overcap_h), mass=0.005,
        origin=Origin(xyz=(-anchor, 0.0, overcap_h * 0.5)),
    )
    model.articulation(
        "overcap_lift",
        ArticulationType.PRISMATIC,
        parent=body,
        child=overcap,
        origin=Origin(xyz=(anchor, 0.0, overcap_z0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=travel, effort=5.0, velocity=0.2),
    )


def _build_twist_up_stick(model, body, r, *, cap_mat, accent_mat) -> None:
    """Bottom twist ring (CONTINUOUS +Z) -> chained platform inside the bore
    (PRISMATIC +Z, parent=twist_ring). The mechanism is at the tube bottom +
    inside the cavity; the top is just an open mouth rim. Rest q=0 = platform
    retracted (parent var_twist_up)."""
    # body-fixed mouth rim at the top
    _open_neck_visual(body, r, accent_mat=accent_mat)

    # bottom knurled twist ring (CONTINUOUS +Z), frame at the tube bottom z=0
    ring_outer_r = max(r.crimp_half_w, r.crimp_half_t, r.half_t) * 0.9 + 0.001
    ring_inner_r = max(ring_outer_r - 0.004, r.bore_r + 0.001)
    ring_h = 0.008
    ring = model.part("twist_ring")
    ring_solid = (
        cq.Workplane("XY")
        .circle(ring_outer_r)
        .circle(ring_inner_r)
        .extrude(ring_h)
    )
    # closed drive hub across the ring bottom — the platform stem rides on this
    # hub (the rotating screw base), giving the chained platform a real support.
    hub = (
        cq.Workplane("XY")
        .circle(ring_inner_r + 0.0004)
        .extrude(ring_h * 0.55)
    )
    ring.visual(mesh_from_cadquery(ring_solid.union(hub), "ring_shell"), material=cap_mat, name="ring_shell", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"pale_yellow_cream", "white_minimal", "steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.opaque_glossy_molded"))
    ring_trim = _cap_trim_shell(radius=ring_outer_r, z_bottom=0.0, height=ring_h, style=r.closure_trim_style)
    if ring_trim is not None:
        ring.visual(mesh_from_cadquery(ring_trim, "ring_trim"), material=accent_mat, name="ring_trim", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"))
    # off-axis knurl marker so twist is observable
    ring.visual(
        Box((0.0014, 0.0014, ring_h * 0.8)),
        origin=Origin(xyz=(ring_outer_r - 0.0007, 0.0, ring_h * 0.5)),
        material=accent_mat,
        name="ring_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    ring.inertial = Inertial.from_geometry(
        Cylinder(ring_outer_r, ring_h), mass=0.006,
        origin=Origin(xyz=(0.0, 0.0, ring_h * 0.5)),
    )
    model.articulation(
        "body_to_twist_ring",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=ring,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.0),
    )

    # platform disc inside the bore (PRISMATIC +Z, child of the twist_ring).
    # Frame origin at the cavity bottom; platform rises toward (not out of) the
    # mouth. Authored so platform-local z=0 is the cavity bottom.
    cavity_bottom_z = r.wall + 0.004
    plat_r = r.bore_r - 0.0006
    plat_h = 0.004
    # platform seated near the cavity bottom at rest; rises but stays below the
    # mouth at full travel.
    max_rise = (r.shoulder_top - cavity_bottom_z - plat_h - 0.002)
    travel = max(min(max_rise, 0.040) * r.joint_travel_scale, 0.010)
    # central drive stem reaching down from the platform into the twist ring
    # hub, so the platform is physically supported by (and connected to) the
    # rotating ring (real twist-up screw shaft), not floating in the cavity.
    # The platform part is a CHILD of the ring: its joint origin is at world
    # cavity_bottom_z, so author the geometry in a local frame where local z=0 is
    # cavity_bottom_z. The stem bottom (local) reaches down into the ring hub.
    stem_r = max(min(ring_inner_r - 0.0004, plat_r - 0.0010), 0.0014)
    stem_top_local = 0.0  # platform disc base
    stem_bottom_local = (ring_h * 0.4) - cavity_bottom_z  # into the ring hub
    platform = model.part("platform")
    plat_solid = (
        cq.Workplane("XY")
        .circle(plat_r)
        .extrude(plat_h)
    )
    stem_solid = (
        cq.Workplane("XY")
        .workplane(offset=stem_bottom_local)
        .circle(stem_r)
        .extrude((stem_top_local - stem_bottom_local) + 0.0005)
    )
    platform.visual(
        mesh_from_cadquery(plat_solid.union(stem_solid), "platform_disk"),
        material=accent_mat,
        name="platform_disk", material_class_id=("metal.aluminum_bare" if r.palette_style in {"steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.frosted_translucent"),
    )
    # product stick column rising from the platform into the neck bore (the
    # "stick" a twist-up tube ejects at full twist). Its 0.4mm radial clearance
    # to the bore wall keeps the platform in near-contact support at every
    # travel, so the elevator never floats free inside the wide cavity.
    stick_r = r.bore_r - 0.0004
    stick_top_local = (r.shoulder_top - 0.001) - cavity_bottom_z + 0.006
    platform.visual(
        mesh_from_cadquery(
            cq.Workplane("XY").circle(stick_r).extrude(stick_top_local),
            "stick_column",
        ),
        material=cap_mat,
        name="stick_column", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"pale_yellow_cream", "white_minimal", "steel_rollon", "bare_aluminum_glue", "charcoal_softtouch_twotone"} else "plastic.opaque_glossy_molded"),
    )
    platform.inertial = Inertial.from_geometry(
        Cylinder(plat_r, stick_top_local - stem_bottom_local),
        mass=0.004,
        origin=Origin(xyz=(0.0, 0.0, (stem_bottom_local + stick_top_local) * 0.5)),
    )
    model.articulation(
        "twist_ring_to_platform",
        ArticulationType.PRISMATIC,
        parent=ring,
        child=platform,
        origin=Origin(xyz=(0.0, 0.0, cavity_bottom_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=travel, effort=2.0, velocity=0.2),
    )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_tube(
    config: ContainerTubeConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    body_mat = model.material(f"ct_body_{r.palette_style}", rgba=pal["body"])  # type: ignore[arg-type]
    cap_mat = model.material(f"ct_cap_{r.palette_style}", rgba=pal["cap"])  # type: ignore[arg-type]
    accent_mat = model.material(f"ct_accent_{r.palette_style}", rgba=pal["accent"])  # type: ignore[arg-type]
    print_mat = model.material(f"ct_print_{r.palette_style}", rgba=pal["print"])  # type: ignore[arg-type]
    body2_mat = None
    if "body2" in pal:
        body2_mat = model.material(f"ct_body2_{r.palette_style}", rgba=pal["body2"])  # type: ignore[arg-type]

    # functional sub-part material (do not follow the colorway): steel ball
    steel_mat = model.material("ct_steel", rgba=_STEEL_RGBA)

    # --- ROOT: squeeze tube body ---
    body = model.part("tube_body")
    _emit_body(
        body,
        r,
        body_mat=body_mat,
        body2_mat=body2_mat,
        print_mat=print_mat,
        accent_mat=accent_mat,
    )

    # --- closure mechanism ---
    if r.closure_mechanism == "lift_cap":
        _build_lift_cap(model, body, r, cap_mat=cap_mat, accent_mat=accent_mat)
    elif r.closure_mechanism == "screw_cap":
        _build_screw_cap(model, body, r, cap_mat=cap_mat, accent_mat=accent_mat)
    elif r.closure_mechanism == "flip_top":
        _build_flip_top(model, body, r, cap_mat=cap_mat, accent_mat=accent_mat)
    elif r.closure_mechanism == "pull_cone":
        _build_pull_cone(model, body, r, cap_mat=cap_mat, accent_mat=accent_mat)
    elif r.closure_mechanism == "standup_flip_cap":
        _build_standup_flip_cap(model, body, r, cap_mat=cap_mat, accent_mat=accent_mat)
    elif r.closure_mechanism == "slant_applicator":
        _build_slant_applicator(model, body, r, cap_mat=cap_mat, accent_mat=accent_mat)
    elif r.closure_mechanism == "roller_ball":
        _build_roller_ball(model, body, r, cap_mat=cap_mat, accent_mat=accent_mat, steel_mat=steel_mat)
    elif r.closure_mechanism == "twist_up_stick":
        _build_twist_up_stick(model, body, r, cap_mat=cap_mat, accent_mat=accent_mat)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_tube(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_tube(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (caps slipping over the neck/nozzle, ball in
# socket, platform inside the bore) are declared element-scoped so the sweep's
# island/overlap checks pass; the closure action is exercised.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_tube_tests(
    object_model: ArticulatedObject,
    config: ContainerTubeConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.check_mesh_files_exist()

    body = object_model.get_part("tube_body")

    # ---- tube body rests on the ground (crimp tail near z=0) ----
    aabb = ctx.part_world_aabb(body)
    bext = _ext(aabb)
    ctx.check(
        "tube body rests on the ground (crimp tail near z=0)",
        abs(aabb[0][2]) < 0.012,
        details=f"body min z={aabb[0][2]:.4f}",
    )
    ctx.check(
        "tube body has real volume (tall hollow shell)",
        bext[0] > 0.006 and bext[1] > 0.010 and bext[2] > 0.06,
        details=f"body extents={bext}",
    )
    bottom_probe_h = max(r.wall * 1.35, 0.0018)
    bottom_probe = (
        cq.Workplane("XY")
        .box(
            max(min(r.half_t * 0.9, 0.006), 0.0022),
            max(min(r.half_w * 0.9, 0.010), 0.0032),
            bottom_probe_h,
            centered=(True, True, False),
        )
        .translate((0.0, 0.0, 0.0))
    )
    bottom_seal_volume = _body_shell_solid(r).val().intersect(bottom_probe.val()).Volume()
    ctx.check(
        "tube body has a sealed bottom cap",
        bottom_seal_volume > 1e-8,
        details=f"bottom seal volume={bottom_seal_volume:.8e}",
    )

    # ---- body shell material reads as the chosen colorway ----
    shell = body.get_visual("body_shell")
    rgba = getattr(shell.material, "rgba", None)
    ctx.check(
        "body shell material is set from the palette",
        rgba is not None,
        details=f"body_shell rgba={rgba}",
    )

    # ---- closure: actions + captured-fit overlaps ----
    if r.closure_mechanism == "lift_cap":
        cap = object_model.get_part("lift_cap")
        lift = object_model.get_articulation("cap_lift")
        ctx.allow_isolated_part(
            cap,
            reason="The lift-off cap lifts clear of the neck and loses contact with the tube body.",
        )
        ctx.allow_overlap(
            cap, body, elem_a="cap_shell", elem_b="body_shell",
            reason="The cap skirt intentionally slips down over the open neck (seated fit).",
        )
        ctx.allow_overlap(
            cap, body, elem_a="cap_shell", elem_b="neck_lip",
            reason="The cap captures the neck lip ring at rest.",
        )
        ctx.check(
            "cap_lift is PRISMATIC about +Z",
            lift.articulation_type == ArticulationType.PRISMATIC and abs(lift.axis[2]) > 0.99,
            details=f"axis={lift.axis}, type={lift.articulation_type}",
        )
        rest = ctx.part_world_position(cap)
        with ctx.pose({lift: lift.motion_limits.upper}):
            up = ctx.part_world_position(cap)
        ctx.check(
            "cap lifts straight up off the tube (no lateral shift)",
            up[2] > rest[2] + 0.02
            and abs(up[0] - rest[0]) < 1e-4 and abs(up[1] - rest[1]) < 1e-4,
            details=f"rest={rest}, up={up}",
        )

    elif r.closure_mechanism == "screw_cap":
        carrier = object_model.get_part("cap_carrier")
        cap = object_model.get_part("cap")
        rotate = object_model.get_articulation("cap_rotate")
        slide = object_model.get_articulation("cap_slide")
        ctx.allow_overlap(
            cap, body, elem_a="cap_shell", elem_b="nozzle",
            reason="The cap bore has a slight interference fit over the threaded nozzle.",
        )
        ctx.check(
            "cap_carrier is massless (no visuals)",
            len(carrier.visuals) == 0,
            details=f"carrier visuals={len(carrier.visuals)}",
        )
        ctx.check(
            "cap_rotate is CONTINUOUS about +Z",
            rotate.articulation_type == ArticulationType.CONTINUOUS and abs(rotate.axis[2]) > 0.99,
            details=f"axis={rotate.axis}, type={rotate.articulation_type}",
        )
        ctx.check(
            "cap_slide is PRISMATIC about +Z (child of carrier)",
            slide.articulation_type == ArticulationType.PRISMATIC and abs(slide.axis[2]) > 0.99,
            details=f"axis={slide.axis}, type={slide.articulation_type}",
        )
        # rotate spins the cap: off-axis marker moves
        m0 = ctx.part_element_world_aabb(cap, elem="cap_marker")
        m0c = ((m0[0][0] + m0[1][0]) / 2.0, (m0[0][1] + m0[1][1]) / 2.0)
        with ctx.pose({rotate: math.pi / 2.0}):
            m1 = ctx.part_element_world_aabb(cap, elem="cap_marker")
            m1c = ((m1[0][0] + m1[1][0]) / 2.0, (m1[0][1] + m1[1][1]) / 2.0)
        ctx.check(
            "cap_rotate spins the cap (marker moves)",
            math.hypot(m1c[0] - m0c[0], m1c[1] - m0c[1]) > 0.003,
            details=f"marker rest={m0c}, quarter-turn={m1c}",
        )
        rest_z = ctx.part_world_position(cap)[2]
        with ctx.pose({slide: slide.motion_limits.upper}):
            lift_z = ctx.part_world_position(cap)[2]
        ctx.check(
            "cap_slide lifts the cap off the nozzle",
            lift_z > rest_z + slide.motion_limits.upper * 0.5,
            details=f"rest_z={rest_z:.4f}, lifted_z={lift_z:.4f}",
        )

    elif r.closure_mechanism == "flip_top":
        lid = object_model.get_part("flip_cap")
        hinge = object_model.get_articulation("flip_cap")
        ctx.allow_overlap(
            lid, body, elem_a="lid_shell", elem_b="neck_lip",
            reason="The flip lid plug seats into the neck mouth when closed.",
        )
        ctx.allow_overlap(
            lid, body, elem_a="lid_shell", elem_b="body_shell",
            reason="The closed flip lid rests over the neck opening.",
        )
        ctx.check(
            "flip_cap is REVOLUTE about +X (horizontal hinge)",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[0]) > 0.9 and abs(hinge.axis[2]) < 0.01,
            details=f"axis={hinge.axis}, type={hinge.articulation_type}",
        )
        rest = ctx.part_element_world_aabb(lid, elem="lid_shell")
        with ctx.pose({hinge: hinge.motion_limits.upper}):
            opened = ctx.part_element_world_aabb(lid, elem="lid_shell")
        ctx.check(
            "flip lid swings up and back when opened",
            opened[1][2] > rest[1][2] + 0.004,
            details=f"rest top z={rest[1][2]:.4f}, open top z={opened[1][2]:.4f}",
        )

    elif r.closure_mechanism == "pull_cone":
        cap = object_model.get_part("pull_cap")
        pull = object_model.get_articulation("cap_pull")
        ctx.allow_isolated_part(
            cap,
            reason="The pull cap lifts clear of the nozzle and loses contact with the tube body.",
        )
        ctx.allow_overlap(
            cap, body, elem_a="cap_shell", elem_b="nozzle_tip",
            reason="The hollow cone cap intentionally seats over the pointed nozzle.",
        )
        ctx.check(
            "cap_pull is PRISMATIC about +Z",
            pull.articulation_type == ArticulationType.PRISMATIC and abs(pull.axis[2]) > 0.99,
            details=f"axis={pull.axis}, type={pull.articulation_type}",
        )
        rest = ctx.part_world_position(cap)
        with ctx.pose({pull: pull.motion_limits.upper}):
            up = ctx.part_world_position(cap)
        ctx.check(
            "pull cap pulls straight up off the nozzle (no lateral shift)",
            up[2] > rest[2] + 0.02
            and abs(up[0] - rest[0]) < 1e-4 and abs(up[1] - rest[1]) < 1e-4,
            details=f"rest={rest}, up={up}",
        )

    elif r.closure_mechanism == "standup_flip_cap":
        lid = object_model.get_part("flip_lid")
        hinge = object_model.get_articulation("lid_hinge")
        ctx.allow_overlap(
            lid, body, elem_a="lid_shell", elem_b="orifice_ring",
            reason="The small flip lid plug seats into the orifice when closed.",
        )
        ctx.allow_overlap(
            lid, body, elem_a="lid_shell", elem_b="base_cap_disc",
            reason="The closed flip lid rests on the stand-up base disc.",
        )
        # base disc is wider than the body (stand-up stability)
        disc_aabb = ctx.part_element_world_aabb(body, elem="base_cap_disc")
        disc_w = max(disc_aabb[1][0] - disc_aabb[0][0], disc_aabb[1][1] - disc_aabb[0][1])
        ctx.check(
            "stand-up base disc is wider than the body (stable)",
            disc_w > 2.0 * max(r.half_w, r.half_t),
            details=f"disc width={disc_w:.4f}, body width={2 * max(r.half_w, r.half_t):.4f}",
        )
        ctx.check(
            "lid_hinge is REVOLUTE about a horizontal axis (-Y)",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[2]) < 0.01 and abs(hinge.axis[1]) > 0.9,
            details=f"axis={hinge.axis}, type={hinge.articulation_type}",
        )
        rest = ctx.part_element_world_aabb(lid, elem="lid_shell")
        with ctx.pose({hinge: hinge.motion_limits.upper}):
            opened = ctx.part_element_world_aabb(lid, elem="lid_shell")
        ctx.check(
            "small flip lid swings up when opened",
            opened[1][2] > rest[1][2] + 0.003,
            details=f"rest top z={rest[1][2]:.4f}, open top z={opened[1][2]:.4f}",
        )

    elif r.closure_mechanism == "slant_applicator":
        cap = object_model.get_part("snap_cap")
        pull = object_model.get_articulation("cap_pull")
        ctx.allow_isolated_part(
            cap,
            reason="The pull-off snap cap pulls clear of the applicator tip and loses contact with the tube body.",
        )
        ctx.allow_overlap(
            cap, body, elem_a="cap_shell", elem_b="applicator_tip",
            reason="The snap cap intentionally seats over the tilted applicator tip.",
        )
        ctx.allow_overlap(
            cap, body, elem_a="cap_shell", elem_b="nozzle",
            reason="The snap cap skirt sleeves down over the upright neck riser (captured snap fit).",
        )
        ctx.check(
            "cap_pull is PRISMATIC about +Z",
            pull.articulation_type == ArticulationType.PRISMATIC
            and abs(pull.axis[2]) > 0.99,
            details=f"axis={pull.axis}, type={pull.articulation_type}",
        )
        rest = ctx.part_world_position(cap)
        with ctx.pose({pull: pull.motion_limits.upper}):
            off = ctx.part_world_position(cap)
        ctx.check(
            "snap cap pulls straight up off the applicator",
            off[2] > rest[2] + 0.02
            and abs(off[0] - rest[0]) < 1e-4 and abs(off[1] - rest[1]) < 1e-4,
            details=f"rest={rest}, off={off}",
        )

    elif r.closure_mechanism == "roller_ball":
        ball = object_model.get_part("applicator_ball")
        overcap = object_model.get_part("overcap")
        ball_joint = object_model.get_articulation("ball_roll")
        cap_joint = object_model.get_articulation("overcap_lift")
        ctx.allow_overlap(
            ball, body, elem_a="ball", elem_b="housing",
            reason="The roller ball is intentionally captured in the housing socket cup.",
        )
        ctx.allow_isolated_part(
            overcap,
            reason="The overcap lifts clear of the housing and loses contact with the tube body.",
        )
        ctx.allow_overlap(
            overcap, body, elem_a="overcap_shell", elem_b="housing",
            reason="The overcap intentionally clips over the housing exterior.",
        )
        ctx.check(
            "ball_roll is CONTINUOUS about +X",
            ball_joint.articulation_type == ArticulationType.CONTINUOUS
            and abs(ball_joint.axis[0]) > 0.99,
            details=f"axis={ball_joint.axis}, type={ball_joint.articulation_type}",
        )
        ctx.check(
            "overcap_lift is PRISMATIC about +Z (second mover)",
            cap_joint.articulation_type == ArticulationType.PRISMATIC
            and abs(cap_joint.axis[2]) > 0.99,
            details=f"axis={cap_joint.axis}, type={cap_joint.articulation_type}",
        )
        # ball rotation: marker moves
        m0 = ctx.part_element_world_aabb(ball, elem="ball_marker")
        m0c = (m0[0][1] + m0[1][1]) / 2.0, (m0[0][2] + m0[1][2]) / 2.0
        with ctx.pose({ball_joint: math.pi / 2.0}):
            m1 = ctx.part_element_world_aabb(ball, elem="ball_marker")
            m1c = (m1[0][1] + m1[1][1]) / 2.0, (m1[0][2] + m1[1][2]) / 2.0
        ctx.check(
            "ball_roll spins the ball (marker moves)",
            math.hypot(m1c[0] - m0c[0], m1c[1] - m0c[1]) > 0.002,
            details=f"marker rest={m0c}, quarter-turn={m1c}",
        )
        rest = ctx.part_world_position(overcap)
        with ctx.pose({cap_joint: cap_joint.motion_limits.upper}):
            off = ctx.part_world_position(overcap)
        ctx.check(
            "overcap pulls straight up off the tube (no lateral shift)",
            off[2] > rest[2] + 0.02
            and abs(off[0] - rest[0]) < 1e-4 and abs(off[1] - rest[1]) < 1e-4,
            details=f"rest={rest}, off={off}",
        )

    elif r.closure_mechanism == "twist_up_stick":
        ring = object_model.get_part("twist_ring")
        platform = object_model.get_part("platform")
        ring_joint = object_model.get_articulation("body_to_twist_ring")
        plat_joint = object_model.get_articulation("twist_ring_to_platform")
        ctx.allow_overlap(
            ring, body, elem_a="ring_shell", elem_b="body_shell",
            reason="The bottom twist ring intentionally wraps the tube base.",
        )
        ctx.allow_overlap(
            platform, body, elem_a="platform_disk", elem_b="body_shell",
            reason="The platform disc rides inside the tube bore (captured fit).",
        )
        ctx.allow_overlap(
            platform, body, elem_a="stick_column", elem_b="body_shell",
            reason="The product stick column rides inside the tube bore (captured fit).",
        )
        ctx.check(
            "body_to_twist_ring is CONTINUOUS about +Z",
            ring_joint.articulation_type == ArticulationType.CONTINUOUS
            and abs(ring_joint.axis[2]) > 0.99,
            details=f"axis={ring_joint.axis}, type={ring_joint.articulation_type}",
        )
        ctx.check(
            "twist_ring_to_platform is PRISMATIC +Z, child of the twist ring (chained)",
            plat_joint.articulation_type == ArticulationType.PRISMATIC
            and abs(plat_joint.axis[2]) > 0.99
            and plat_joint.parent == "twist_ring",
            details=f"axis={plat_joint.axis}, parent={plat_joint.parent}",
        )
        # platform stays within the body bore at full travel (does not exit mouth)
        rest_z = ctx.part_world_position(platform)[2]
        with ctx.pose({plat_joint: plat_joint.motion_limits.upper}):
            up_aabb = ctx.part_element_world_aabb(platform, elem="platform_disk")
            up_z = ctx.part_world_position(platform)[2]
        ctx.check(
            "platform rises inside the bore but stays below the mouth",
            up_z > rest_z + plat_joint.motion_limits.upper * 0.4
            and up_aabb[1][2] < r.neck_top,
            details=f"rest_z={rest_z:.4f}, up_z={up_z:.4f}, top={up_aabb[1][2]:.4f}, mouth={r.neck_top:.4f}",
        )

    # ---- at least one non-fixed closure joint exists ----
    non_fixed = [
        j for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed closure joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=96,
        ignore_fixed=True,
    )

    return ctx.report()
