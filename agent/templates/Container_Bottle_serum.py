# SPDX-License-Identifier: Apache-2.0

"""Container bottle serum — modular procedural template (small serum/skincare bottle).

Category identity: an upright, short (squat), narrow hollow glass serum bottle.
The hollow body (ROOT) rests on z=0 with its axis along +Z; a small serum-specific
closure (the main articulation) opens/dispenses on top. No multiplicity axis — one
bottle, one closure. A white label band wraps the body middle (fixed body visual).

Two parallel slots (spec ``Container_Bottle_serum.md``):

  * ``body_shape`` (6) — the ROOT ``body`` ``body_glass`` mesh + ``label_band``:
      - round_cylinder    : circle.extrude straight body + lofted round shoulder
      - tapered_cone      : circle→circle loft tapered body
      - squared_faceted   : rect+fillet box-shell + rect→circle shoulder loft
      - boston_round      : LatheGeometry.from_shell_profiles (catmull-rom spline)
      - tall_slim_vial    : tall slim circle.extrude tube (ampoule/test-tube)
      - faceted_prism     : polygon(8).extrude octagonal prism + polygon→circle loft
  * ``closure`` (6) — the serum closure mechanism (>=1 non-fixed joint each):
      - dropper_prismatic        : collar+bulb+pipette single rigid part, PRISMATIC +Z pull
      - screw_cap_revolute       : ribbed twist cap, REVOLUTE +Z
      - pump_dispenser_prismatic : body-fixed collar+dip_tube + pump_head PRISMATIC -Z press
      - mist_sprayer_prismatic   : body-fixed crimp collar+ridges+dip_tube + actuator PRISMATIC -Z
      - roller_ball_revolute     : body-fixed housing + roller_ball REVOLUTE +X + overcap PRISMATIC +Z
      - brush_wand_prismatic     : cap+stem+doe-foot single rigid part, PRISMATIC +Z pull

Continuous size/proportion variation (height/radius/neck/closure/travel scales)
lives in ``resolve_config`` as clamped params, never as slot candidates.
``palette_style`` (10 coordinated colorways + finish) is palette-only and not a slot.

Sources (articraft_data ``picture/Container/Bottle serum`` 5-star pool): parent
``...98768519`` (round body + dropper) plus single-axis forks
``container_bottle_serum_var_{tapered_body,squared_body,boston_round_body,
tall_slim_vial,faceted_prism,screw_cap,pump_dispenser,mist_sprayer,roller_ball,
brush_wand}``. Each module factory adapts the named source verbatim.

Canonical spec:
``articraft_template_authoring/specs_modular_v1/Container_Bottle_serum.md``
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
    Cylinder,
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    sample_catmull_rom_spline_2d,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyShape = Literal[
    "round_cylinder",
    "tapered_cone",
    "squared_faceted",
    "boston_round",
    "tall_slim_vial",
    "faceted_prism",
]
Closure = Literal[
    "dropper_prismatic",
    "screw_cap_revolute",
    "pump_dispenser_prismatic",
    "mist_sprayer_prismatic",
    "roller_ball_revolute",
    "brush_wand_prismatic",
]
PaletteStyle = Literal[
    "amber_apothecary",
    "clear_minimal",
    "frosted_white",
    "cobalt_blue",
    "green_glass",
    "opaque_white",
    "soft_touch_black",
    "gold_luxe",
    "pearlescent_blush",
    "matte_sage",
]

BODY_SHAPES: tuple[BodyShape, ...] = (
    "round_cylinder",
    "tapered_cone",
    "squared_faceted",
    "boston_round",
    "tall_slim_vial",
    "faceted_prism",
)
CLOSURES: tuple[Closure, ...] = (
    "dropper_prismatic",
    "screw_cap_revolute",
    "pump_dispenser_prismatic",
    "mist_sprayer_prismatic",
    "roller_ball_revolute",
    "brush_wand_prismatic",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "amber_apothecary",
    "clear_minimal",
    "frosted_white",
    "cobalt_blue",
    "green_glass",
    "opaque_white",
    "soft_touch_black",
    "gold_luxe",
    "pearlescent_blush",
    "matte_sage",
)

# ---------------------------------------------------------------------------
# Palette: 10 coordinated colorways + an explicit finish dimension.
# Each colorway colors four components: body_glass / closure_cap /
# collar_accent / label. Glass finishes carry alpha < 1.
# Anchored on the 5-star source materials (amber/white_plastic/clear/steel_ball/
# cap_gray/pump_grey) + structure-neutral inferred colorways.
# ---------------------------------------------------------------------------
PALETTES: dict[
    PaletteStyle, dict[str, tuple[float, float, float, float] | str]
] = {
    "amber_apothecary": {
        "finish": "gloss_glass",
        "body": (0.45, 0.24, 0.06, 0.5),
        "cap": (0.95, 0.95, 0.94, 1.0),
        "accent": (0.95, 0.95, 0.94, 1.0),
        "label": (0.97, 0.97, 0.96, 1.0),
    },
    "clear_minimal": {
        "finish": "gloss_glass",
        "body": (0.85, 0.90, 0.92, 0.40),
        "cap": (0.95, 0.95, 0.94, 1.0),
        "accent": (0.92, 0.92, 0.91, 1.0),
        "label": (0.97, 0.97, 0.96, 1.0),
    },
    "frosted_white": {
        "finish": "frosted_glass",
        "body": (0.93, 0.93, 0.92, 0.58),
        "cap": (0.95, 0.95, 0.94, 1.0),
        "accent": (0.88, 0.88, 0.90, 1.0),
        "label": (0.97, 0.97, 0.96, 1.0),
    },
    "cobalt_blue": {
        "finish": "gloss_glass",
        "body": (0.10, 0.18, 0.45, 0.5),
        "cap": (0.95, 0.95, 0.94, 1.0),
        "accent": (0.72, 0.73, 0.76, 1.0),
        "label": (0.97, 0.97, 0.96, 1.0),
    },
    "green_glass": {
        "finish": "gloss_glass",
        "body": (0.16, 0.34, 0.18, 0.5),
        "cap": (0.95, 0.95, 0.94, 1.0),
        "accent": (0.95, 0.95, 0.94, 1.0),
        "label": (0.97, 0.97, 0.96, 1.0),
    },
    "opaque_white": {
        "finish": "opaque_matte",
        "body": (0.96, 0.96, 0.95, 1.0),
        "cap": (0.95, 0.95, 0.94, 1.0),
        "accent": (0.88, 0.88, 0.90, 1.0),
        "label": (0.97, 0.97, 0.96, 1.0),
    },
    "soft_touch_black": {
        "finish": "soft_touch",
        "body": (0.10, 0.10, 0.11, 1.0),
        "cap": (0.14, 0.14, 0.15, 1.0),
        "accent": (0.20, 0.20, 0.21, 1.0),
        "label": (0.93, 0.93, 0.92, 1.0),
    },
    "gold_luxe": {
        "finish": "metallic",
        "body": (0.18, 0.13, 0.06, 0.55),
        "cap": (0.78, 0.62, 0.30, 1.0),
        "accent": (0.78, 0.62, 0.30, 1.0),
        "label": (0.85, 0.74, 0.50, 1.0),
    },
    "pearlescent_blush": {
        "finish": "pearlescent",
        "body": (0.93, 0.84, 0.83, 0.85),
        "cap": (0.96, 0.90, 0.88, 1.0),
        "accent": (0.82, 0.70, 0.62, 1.0),
        "label": (0.97, 0.95, 0.94, 1.0),
    },
    "matte_sage": {
        "finish": "opaque_matte",
        "body": (0.62, 0.66, 0.55, 1.0),
        "cap": (0.95, 0.95, 0.94, 1.0),
        "accent": (0.55, 0.55, 0.56, 1.0),
        "label": (0.93, 0.93, 0.91, 1.0),
    },
}

# Functional sub-part materials (keep their own appearance per the 5-star
# sources; do not follow the colorway): clear glass pipette / dip tube, steel
# roller ball, flocked doe-foot tip, grey pump stem.
_CLEAR_RGBA = (0.85, 0.90, 0.92, 0.35)
_STEEL_RGBA = (0.72, 0.73, 0.76, 1.0)
_FLOCK_RGBA = (0.90, 0.88, 0.85, 1.0)
_PUMP_GREY_RGBA = (0.55, 0.55, 0.56, 1.0)


# ---------------------------------------------------------------------------
# Base geometry per body shape (meters). Scaled per-build by resolve_config.
# Each shape declares its own neck datum (NECK_R / NECK_TOP / SHOULDER_TOP /
# BORE_R) which the closure builders mount onto.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _ShapeGeom:
    kind: str  # "round" | "taper" | "square" | "lathe" | "vial" | "polygon"
    body_r: float  # nominal outer radius / apothem / max-belly radius
    body_top: float  # top of the straight wall (round/taper/square/vial/poly)
    shoulder_top: float
    neck_r: float
    neck_top: float
    wall: float
    # taper-only
    body_r_top: float
    # square / polygon facet count
    facets: int
    # label band z extents
    label_z0: float
    label_z1: float


_SHAPES: dict[BodyShape, _ShapeGeom] = {
    # round cylinder (parent ...98768519)
    "round_cylinder": _ShapeGeom(
        kind="round", body_r=0.015, body_top=0.060, shoulder_top=0.070,
        neck_r=0.0080, neck_top=0.0820, wall=0.0018, body_r_top=0.015,
        facets=64, label_z0=0.012, label_z1=0.044,
    ),
    # tapered cone (var_tapered_body): base R 0.017 -> top R 0.011
    "tapered_cone": _ShapeGeom(
        kind="taper", body_r=0.017, body_top=0.060, shoulder_top=0.070,
        neck_r=0.0080, neck_top=0.0820, wall=0.0018, body_r_top=0.011,
        facets=64, label_z0=0.012, label_z1=0.044,
    ),
    # squared faceted (var_squared_body): W=0.028 across flats, half = 0.014
    "squared_faceted": _ShapeGeom(
        kind="square", body_r=0.014, body_top=0.060, shoulder_top=0.070,
        neck_r=0.0080, neck_top=0.0820, wall=0.0018, body_r_top=0.014,
        facets=4, label_z0=0.012, label_z1=0.044,
    ),
    # boston round (var_boston_round_body): lathe spline, tall, waisted neck
    "boston_round": _ShapeGeom(
        kind="lathe", body_r=0.019, body_top=0.050, shoulder_top=0.062,
        neck_r=0.0075, neck_top=0.098, wall=0.0018, body_r_top=0.019,
        facets=64, label_z0=0.018, label_z1=0.048,
    ),
    # tall slim vial (var_tall_slim_vial): R=0.0065 H=0.098, narrow neck
    "tall_slim_vial": _ShapeGeom(
        kind="vial", body_r=0.0065, body_top=0.098, shoulder_top=0.103,
        neck_r=0.0052, neck_top=0.115, wall=0.0012, body_r_top=0.0065,
        facets=64, label_z0=0.022, label_z1=0.062,
    ),
    # faceted octagonal prism (var_faceted_prism): apothem 0.015
    "faceted_prism": _ShapeGeom(
        kind="polygon", body_r=0.015, body_top=0.060, shoulder_top=0.070,
        neck_r=0.0080, neck_top=0.0820, wall=0.0018, body_r_top=0.015,
        facets=8, label_z0=0.012, label_z1=0.044,
    ),
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ContainerBottleSerumConfig:
    body_shape: BodyShape = "round_cylinder"
    closure: Closure = "dropper_prismatic"
    palette_style: PaletteStyle = "amber_apothecary"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    neck_radius_scale: float = 1.0
    closure_size_scale: float = 1.0
    joint_travel_scale: float = 1.0
    name: str = "container_bottle_serum"


@dataclass(frozen=True)
class ResolvedContainerBottleSerumConfig:
    body_shape: BodyShape
    closure: Closure
    palette_style: PaletteStyle
    body_height_scale: float
    body_radius_scale: float
    neck_radius_scale: float
    closure_size_scale: float
    joint_travel_scale: float
    # derived body geometry (after scales)
    kind: str
    body_r: float
    body_r_top: float
    body_top: float
    shoulder_top: float
    neck_r: float
    neck_top: float
    wall: float
    bore_r: float
    facets: int
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
def config_from_seed(seed: int) -> ContainerBottleSerumConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    return ContainerBottleSerumConfig(
        body_shape=rng.choice(BODY_SHAPES),
        closure=rng.choice(CLOSURES),
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.85, 1.18), 4),
        body_radius_scale=round(rng.uniform(0.88, 1.15), 4),
        neck_radius_scale=round(rng.uniform(0.92, 1.10), 4),
        closure_size_scale=round(rng.uniform(0.90, 1.12), 4),
        joint_travel_scale=round(rng.uniform(0.85, 1.12), 4),
        name=f"seeded_container_bottle_serum_{seed}",
    )


def resolve_config(
    config: ContainerBottleSerumConfig | None = None,
) -> ResolvedContainerBottleSerumConfig:
    cfg = config or ContainerBottleSerumConfig()
    body_shape = _pick(cfg.body_shape, BODY_SHAPES)
    closure = _pick(cfg.closure, CLOSURES)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    g = _SHAPES[body_shape]

    h_scale = _clamp(cfg.body_height_scale, 0.85, 1.18)
    r_scale = _clamp(cfg.body_radius_scale, 0.88, 1.15)
    n_scale = _clamp(cfg.neck_radius_scale, 0.92, 1.10)
    jt_scale = _clamp(cfg.joint_travel_scale, 0.85, 1.12)

    # body radius scales freely; neck radius follows its own scale, clamped to
    # stay strictly inside the body so the shoulder always tapers inward.
    body_r = g.body_r * r_scale
    body_r_top = g.body_r_top * r_scale
    # closure_size equation: tracks neck radius (closure scales with the mouth).
    closure_size = _clamp(0.9 * n_scale + 0.1, 0.90, 1.12)

    # height scales applied to the vertical datums above the base.
    body_top = g.body_top * h_scale
    shoulder_top = g.shoulder_top * h_scale
    neck_top = g.neck_top * h_scale

    neck_r = _clamp(g.neck_r * n_scale, 0.0045, max(body_r, body_r_top) - 0.0018)
    bore_r = neck_r - g.wall

    return ResolvedContainerBottleSerumConfig(
        body_shape=body_shape,
        closure=closure,
        palette_style=palette,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        neck_radius_scale=n_scale,
        closure_size_scale=closure_size,
        joint_travel_scale=jt_scale,
        kind=g.kind,
        body_r=body_r,
        body_r_top=body_r_top,
        body_top=body_top,
        shoulder_top=shoulder_top,
        neck_r=neck_r,
        neck_top=neck_top,
        wall=g.wall,
        bore_r=bore_r,
        facets=g.facets,
        label_z0=g.label_z0 * h_scale,
        label_z1=g.label_z1 * h_scale,
        name=cfg.name or "container_bottle_serum",
    )


def with_overrides(
    config: ContainerBottleSerumConfig, **kwargs: object
) -> ContainerBottleSerumConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerBottleSerumConfig | ResolvedContainerBottleSerumConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedContainerBottleSerumConfig)
        else resolve_config(config)
    )
    return (
        ("body_shape", r.body_shape),
        ("closure", r.closure),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Body geometry (Slot A). Each shape adapts its named 5-star source verbatim.
# ---------------------------------------------------------------------------
def _round_body_solid(r: ResolvedContainerBottleSerumConfig) -> cq.Workplane:
    """Round straight cylinder body (parent ...98768519 ``_body_glass_mesh``)."""
    br, bt, st, nr, nt, w, bore = (
        r.body_r, r.body_top, r.shoulder_top, r.neck_r, r.neck_top, r.wall, r.bore_r
    )
    outer = cq.Workplane("XY").circle(br).extrude(bt)
    shoulder = (
        cq.Workplane("XY")
        .workplane(offset=bt)
        .circle(br)
        .workplane(offset=(st - bt))
        .circle(nr + 0.0015)
        .loft(ruled=False)
    )
    neck = (
        cq.Workplane("XY")
        .workplane(offset=st)
        .circle(nr)
        .extrude(nt - st)
    )
    solid = outer.union(shoulder).union(neck)
    # ruled=True cavity loft: a smooth (spline) inner profile can overshoot the
    # outer wall when body_r is large vs neck_r, splitting the shell into two
    # disconnected solids. The ruled (conical) loft keeps a uniform wall.
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=w)
        .circle(br - w)
        .workplane(offset=(bt - w))
        .circle(br - w)
        .workplane(offset=(st - bt))
        .circle(bore)
        .workplane(offset=(nt - st + 0.001))
        .circle(bore)
        .loft(ruled=True)
    )
    return solid.cut(cavity)


def _taper_body_solid(r: ResolvedContainerBottleSerumConfig) -> cq.Workplane:
    """Tapered cone body (var_tapered_body ``_body_glass_mesh``)."""
    br, brt, bt, st, nr, nt, w, bore = (
        r.body_r, r.body_r_top, r.body_top, r.shoulder_top, r.neck_r,
        r.neck_top, r.wall, r.bore_r,
    )
    outer = (
        cq.Workplane("XY")
        .circle(br)
        .workplane(offset=bt)
        .circle(brt)
        .loft()
    )
    shoulder = (
        cq.Workplane("XY")
        .workplane(offset=bt)
        .circle(brt)
        .workplane(offset=(st - bt))
        .circle(nr + 0.0015)
        .loft(ruled=False)
    )
    neck = (
        cq.Workplane("XY")
        .workplane(offset=st)
        .circle(nr)
        .extrude(nt - st)
    )
    solid = outer.union(shoulder).union(neck)
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=w)
        .circle(br - w)
        .workplane(offset=(bt - w))
        .circle(brt - w)
        .workplane(offset=(st - bt))
        .circle(bore)
        .workplane(offset=(nt - st + 0.001))
        .circle(bore)
        .loft(ruled=True)
    )
    return solid.cut(cavity)


def _rounded_rect_solid(w, corner_r, z_start, height):
    """Extruded rounded-rectangle solid centered at origin (var_squared_body)."""
    return (
        cq.Workplane("XY")
        .workplane(offset=z_start)
        .rect(w, w)
        .extrude(height)
        .edges("|Z")
        .fillet(min(corner_r, w / 2.0 - 0.0001))
    )


def _square_body_solid(r: ResolvedContainerBottleSerumConfig) -> cq.Workplane:
    """Squared faceted box-shell body (var_squared_body ``_body_glass_mesh``)."""
    bw = 2.0 * r.body_r  # width across flats
    corner_r = 0.003
    bt, st, nr, nt, w, bore = (
        r.body_top, r.shoulder_top, r.neck_r, r.neck_top, r.wall, r.bore_r
    )
    body_outer = (
        cq.Workplane("XY")
        .rect(bw, bw)
        .extrude(bt)
        .edges("|Z")
        .fillet(corner_r)
    )
    shoulder = (
        cq.Workplane("XY")
        .workplane(offset=bt)
        .rect(bw, bw)
        .workplane(offset=(st - bt))
        .circle(nr + 0.0015)
        .loft(ruled=True)
    )
    neck = (
        cq.Workplane("XY")
        .workplane(offset=st)
        .circle(nr)
        .extrude(nt - st)
    )
    solid = body_outer.union(shoulder).union(neck)

    inner_w = bw - 2.0 * w
    inner_cr = max(corner_r - w, 0.0005)
    cavity_body = _rounded_rect_solid(inner_w, inner_cr, w, bt - w)
    cavity_shoulder = (
        cq.Workplane("XY")
        .workplane(offset=bt)
        .rect(inner_w, inner_w)
        .workplane(offset=(st - bt))
        .circle(bore)
        .loft(ruled=True)
    )
    cavity_neck = (
        cq.Workplane("XY")
        .workplane(offset=st)
        .circle(bore)
        .extrude(nt - st + 0.001)
    )
    cavity = cavity_body.union(cavity_shoulder).union(cavity_neck)
    return solid.cut(cavity)


def _lathe_body_mesh(r: ResolvedContainerBottleSerumConfig):
    """Boston-round lathe spline body (var_boston_round_body).

    Profiles scale with body_r / neck_r / height datums while keeping the
    catmull-rom waisted shape of the source.
    """
    w = r.wall
    rmax = r.body_r
    rbase = rmax * 0.58
    nr = r.neck_r
    bore = r.bore_r
    # vertical datums (scaled by height already via body_top/shoulder/neck_top)
    z_base = 0.0
    z_belly_low = r.body_top * 0.32
    z_belly_top = r.body_top
    z_shoulder = r.shoulder_top
    z_neck_trans = r.shoulder_top + (r.neck_top - r.shoulder_top) * 0.42
    z_neck_top = r.neck_top

    outer_pts = [
        (0.000, z_base),
        (rbase, z_base + 0.001),
        (rmax * 0.79, z_belly_low * 0.38),
        (rmax - 0.002, z_belly_low * 0.62),
        (rmax, z_belly_low),
        (rmax, z_belly_top),
        (rmax - 0.003, z_shoulder),
        (rmax * 0.63, z_shoulder + (z_neck_trans - z_shoulder) * 0.45),
        (nr + 0.002, z_neck_trans),
        (nr, z_neck_trans + 0.004),
        (nr, z_neck_top),
    ]
    inner_pts = [
        (0.000, z_base + w),
        (rbase - w, z_base + w + 0.001),
        (rmax * 0.79 - w, z_belly_low * 0.38 + w * 0.5),
        (rmax - w - 0.002, z_belly_low * 0.62 + w * 0.3),
        (rmax - w, z_belly_low + w * 0.3),
        (rmax - w, z_belly_top),
        (rmax - w - 0.003, z_shoulder),
        (rmax * 0.63 - w, z_shoulder + (z_neck_trans - z_shoulder) * 0.45),
        (bore, z_neck_trans + 0.002),
        (bore, z_neck_top),
    ]
    outer = sample_catmull_rom_spline_2d(outer_pts, samples_per_segment=8)
    inner = sample_catmull_rom_spline_2d(inner_pts, samples_per_segment=8)
    geom = LatheGeometry.from_shell_profiles(
        outer, inner,
        segments=48,
        start_cap="flat",
        end_cap="flat",
        lip_samples=8,
    )
    return mesh_from_geometry(geom, "body_glass")


def _vial_body_solid(r: ResolvedContainerBottleSerumConfig) -> cq.Workplane:
    """Tall slim vial body (var_tall_slim_vial ``_body_glass_mesh``)."""
    br, bt, st, nr, nt, w, bore = (
        r.body_r, r.body_top, r.shoulder_top, r.neck_r, r.neck_top, r.wall, r.bore_r
    )
    tube = cq.Workplane("XY").circle(br).extrude(bt)
    shoulder = (
        cq.Workplane("XY")
        .workplane(offset=bt)
        .circle(br)
        .workplane(offset=(st - bt))
        .circle(nr + 0.0008)
        .loft(ruled=False)
    )
    neck = (
        cq.Workplane("XY")
        .workplane(offset=st)
        .circle(nr)
        .extrude(nt - st)
    )
    solid = tube.union(shoulder).union(neck)
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=w)
        .circle(br - w)
        .workplane(offset=(bt - w))
        .circle(br - w)
        .workplane(offset=(st - bt))
        .circle(bore)
        .workplane(offset=(nt - st + 0.001))
        .circle(bore)
        .loft(ruled=True)
    )
    solid = solid.cut(cavity)
    base_round = (
        cq.Workplane("XY")
        .workplane(offset=-0.001)
        .circle(br - 0.001)
        .extrude(0.001)
    )
    return solid.cut(base_round)


def _polygon_body_solid(r: ResolvedContainerBottleSerumConfig) -> cq.Workplane:
    """Faceted octagonal prism body (var_faceted_prism ``_body_glass_mesh``)."""
    n = r.facets
    apothem = r.body_r
    circum_r = apothem / math.cos(math.pi / n)
    diam = 2.0 * circum_r
    inner_apothem = apothem - r.wall
    inner_circum_r = inner_apothem / math.cos(math.pi / n)
    inner_diam = 2.0 * inner_circum_r
    bt, st, nr, nt, bore = (
        r.body_top, r.shoulder_top, r.neck_r, r.neck_top, r.bore_r
    )
    outer_body = cq.Workplane("XY").polygon(n, diam).extrude(bt)
    shoulder = (
        cq.Workplane("XY")
        .workplane(offset=bt)
        .polygon(n, diam)
        .workplane(offset=(st - bt))
        .circle(nr + 0.0015)
        .loft(ruled=False)
    )
    neck = (
        cq.Workplane("XY")
        .workplane(offset=st)
        .circle(nr)
        .extrude(nt - st)
    )
    solid = outer_body.union(shoulder).union(neck)
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=r.wall)
        .polygon(n, inner_diam)
        .workplane(offset=(bt - r.wall))
        .polygon(n, inner_diam)
        .workplane(offset=(st - bt))
        .circle(bore)
        .workplane(offset=(nt - st + 0.001))
        .circle(bore)
        .loft(ruled=True)
    )
    return solid.cut(cavity)


def _label_band_mesh(r: ResolvedContainerBottleSerumConfig):
    """White label band that follows the body cross-section family."""
    z0, z1 = r.label_z0, r.label_z1
    if r.kind == "taper":
        # follow the linear taper
        def rad(z):
            t = max(0.0, min(1.0, z / r.body_top))
            return r.body_r + (r.body_r_top - r.body_r) * t

        r_out_lo = rad(z0) + 0.0006
        r_out_hi = rad(z1) + 0.0006
        r_in_lo = rad(z0) - 0.0002
        r_in_hi = rad(z1) - 0.0002
        outer = (
            cq.Workplane("XY")
            .workplane(offset=z0)
            .circle(r_out_lo)
            .workplane(offset=z1 - z0)
            .circle(r_out_hi)
            .loft()
        )
        inner = (
            cq.Workplane("XY")
            .workplane(offset=z0 - 0.001)
            .circle(r_in_lo)
            .workplane(offset=z1 - z0 + 0.002)
            .circle(r_in_hi)
            .loft()
        )
        return mesh_from_cadquery(outer.cut(inner), "label_band")
    if r.kind == "square":
        bw = 2.0 * r.body_r
        offset = 0.0006
        label_w = bw + 2.0 * offset
        label_cr = 0.003 + offset
        outer = _rounded_rect_solid(label_w, label_cr, z0, z1 - z0)
        inner_cut = _rounded_rect_solid(
            bw - 0.0004, max(0.003 - 0.0002, 0.0005), z0 - 0.001, (z1 - z0) + 0.002
        )
        return mesh_from_cadquery(outer.cut(inner_cut), "label_band")
    if r.kind == "polygon":
        n = r.facets
        apothem = r.body_r

        def poly_diam(ap):
            return 2.0 * (ap / math.cos(math.pi / n))

        outer = (
            cq.Workplane("XY")
            .workplane(offset=z0)
            .polygon(n, poly_diam(apothem + 0.0006))
            .extrude(z1 - z0)
        )
        inner = (
            cq.Workplane("XY")
            .workplane(offset=z0 - 0.0005)
            .polygon(n, poly_diam(apothem - 0.0002))
            .extrude(z1 - z0 + 0.001)
        )
        return mesh_from_cadquery(outer.cut(inner), "label_band")
    # round / lathe / vial: simple cylindrical ring (use belly/body radius)
    label_r = r.body_r + (0.0005 if r.kind == "lathe" else 0.0006)
    inner_r = r.body_r - (0.001 if r.kind in ("lathe",) else 0.0002)
    label = (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .circle(label_r)
        .circle(inner_r)
        .extrude(z1 - z0)
    )
    return mesh_from_cadquery(label, "label_band")


def _body_glass_mesh(r: ResolvedContainerBottleSerumConfig):
    if r.kind == "round":
        solid = _round_body_solid(r)
    elif r.kind == "taper":
        solid = _taper_body_solid(r)
    elif r.kind == "square":
        solid = _square_body_solid(r)
    elif r.kind == "vial":
        solid = _vial_body_solid(r)
    elif r.kind == "polygon":
        solid = _polygon_body_solid(r)
    else:  # lathe — emitted directly as a mesh
        return _lathe_body_mesh(r)
    return mesh_from_cadquery(solid, "body_glass")


def _emit_body(body, r: ResolvedContainerBottleSerumConfig, *, body_mat, label_mat) -> None:
    body.visual(_body_glass_mesh(r), material=body_mat, name="body_glass", material_class_id=("glass.smoked_tinted" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "soft_touch_black", "gold_luxe", "pearlescent_blush"} else "plastic.opaque_generic"))
    body.visual(_label_band_mesh(r), material=label_mat, name="label_band", material_class_id="paper.plain_sheet")
    body.inertial = Inertial.from_geometry(
        Cylinder(max(r.body_r, r.body_r_top), r.body_top),
        mass=0.040,
        origin=Origin(xyz=(0.0, 0.0, r.body_top / 2.0)),
    )


# ---------------------------------------------------------------------------
# Closure builders (Slot B). Each adapts its named 5-star source verbatim.
# ---------------------------------------------------------------------------
def _collar_mesh(r: ResolvedContainerBottleSerumConfig, *, collar_r, z0, z_top, name):
    """White collar that grips the neck, hollowed to slip over it (parent /
    dropper / pump / wand pattern)."""
    outer = (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .circle(collar_r)
        .extrude(z_top - z0)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=z0 - 0.001)
        .circle(r.neck_r + 0.0006)
        .extrude((z_top - 0.002) - (z0 - 0.001))
    )
    return mesh_from_cadquery(outer.cut(inner), name)


def _build_dropper(model, body, r, *, cap_mat, accent_mat) -> None:
    """Dropper closure (parent ...98768519): collar + bulb + pipette as ONE
    rigid part, PRISMATIC +Z pull-out. Origin (0,0,0) on the bottle axis."""
    cs = r.closure_size_scale
    collar_r = (r.neck_r + 0.0025) * cs
    collar_z0 = r.shoulder_top - 0.004
    collar_top = r.neck_top + 0.008
    bulb_r = (r.neck_r + 0.0015) * cs
    bulb_cz = collar_top + bulb_r + 0.008
    pip_r = 0.0024 * cs
    # pipette tip seated deep near the bottle floor (also keeps the child AABB
    # within 15mm of the joint origin at z=0 for the articulation-origin check).
    pip_bottom = r.wall + 0.005
    travel = (r.neck_top - r.shoulder_top + 0.05) * r.joint_travel_scale

    dropper = model.part("dropper")
    dropper.visual(
        _collar_mesh(r, collar_r=collar_r, z0=collar_z0, z_top=collar_top, name="collar"),
        material=cap_mat,
        name="collar", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"),
    )
    dropper.visual(
        Sphere(bulb_r),
        origin=Origin(xyz=(0.0, 0.0, bulb_cz)),
        material=cap_mat,
        name="bulb", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"),
    )
    dropper.visual(
        Cylinder(0.0045, (bulb_cz - bulb_r) - collar_top + 0.004),
        origin=Origin(xyz=(0.0, 0.0, (collar_top + (bulb_cz - bulb_r)) / 2.0)),
        material=cap_mat,
        name="bulb_stem", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"),
    )
    pip_len = collar_top - pip_bottom
    clear_mat = accent_mat  # clear pipette
    dropper.visual(
        Cylinder(pip_r, pip_len),
        origin=Origin(xyz=(0.0, 0.0, pip_bottom + pip_len / 2.0)),
        material=clear_mat,
        name="pipette", material_class_id="glass.clear_transparent",
    )
    dropper.inertial = Inertial.from_geometry(
        Cylinder(collar_r, collar_top - pip_bottom),
        mass=0.008,
        origin=Origin(xyz=(0.0, 0.0, (pip_bottom + bulb_cz) / 2.0)),
    )
    model.articulation(
        "body_to_dropper",
        ArticulationType.PRISMATIC,
        parent=body,
        child=dropper,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=travel, effort=5.0, velocity=0.1),
    )


def _build_screw_cap(model, body, r, *, cap_mat) -> None:
    """Screw cap (var_screw_cap): ribbed twist cap, REVOLUTE +Z about the
    bottle axis at the neck top. 24 grip ribs via for-loop (fixed visuals)."""
    cs = r.closure_size_scale
    cap_r = (r.neck_r + 0.003) * cs
    skirt_drop = 0.010
    cap_above = 0.006
    cap_total_h = skirt_drop + cap_above
    cap_bore_r = r.neck_r - 0.0003
    n_ribs = 24
    rib_bottom = -skirt_drop + 0.002
    rib_top = cap_above - 0.002
    rib_h = rib_top - rib_bottom
    rib_w = 0.0010
    rib_d = 0.0005
    nt = r.neck_top

    # cap shell mesh (mesh bottom z=0 .. z=cap_total_h; placed via -skirt_drop)
    outer = cq.Workplane("XY").circle(cap_r).extrude(cap_total_h)
    bore = (
        cq.Workplane("XY")
        .workplane(offset=-0.001)
        .circle(cap_bore_r)
        .extrude(skirt_drop + 0.001)
    )
    cap_shell = outer.cut(bore)
    rib = cq.Workplane("XY").rect(rib_d, rib_w).extrude(rib_h)
    rib_mesh = mesh_from_cadquery(rib, "cap_rib")

    cap = model.part("cap")
    cap.visual(
        mesh_from_cadquery(cap_shell, "cap_shell"),
        origin=Origin(xyz=(0.0, 0.0, -skirt_drop)),
        material=cap_mat,
        name="cap_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"),
    )
    for i in range(n_ribs):
        angle = 2.0 * math.pi * i / n_ribs
        x = cap_r * math.cos(angle)
        y = cap_r * math.sin(angle)
        cap.visual(
            rib_mesh,
            origin=Origin(xyz=(x, y, rib_bottom), rpy=(0.0, 0.0, angle)),
            material=cap_mat,
            name=f"rib_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"),
        )
    cap.inertial = Inertial.from_geometry(
        Cylinder(cap_r, cap_total_h),
        mass=0.005,
        origin=Origin(xyz=(0.0, 0.0, (cap_above - skirt_drop) / 2.0)),
    )
    model.articulation(
        "body_to_cap",
        ArticulationType.REVOLUTE,
        parent=body,
        child=cap,
        origin=Origin(xyz=(0.0, 0.0, nt)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            lower=0.0, upper=2.0 * math.pi, effort=2.0, velocity=1.0
        ),
    )


def _build_pump(model, body, r, *, cap_mat, accent_mat) -> None:
    """Pump dispenser (var_pump_dispenser): body-fixed collar + dip_tube,
    pump_head (head+nozzle+stem) PRISMATIC -Z press at the collar top."""
    cs = r.closure_size_scale
    collar_r = (r.neck_r + 0.0025) * cs
    collar_z0 = r.shoulder_top - 0.004
    collar_top = r.neck_top + 0.008
    head_r = (r.neck_r + 0.004) * cs
    head_h = 0.006
    nozzle_r = 0.0025
    nozzle_len = 0.013
    stem_r = 0.003
    stem_len = 0.022
    dip_r = 0.0020
    dip_bottom = max(r.wall + 0.004, r.shoulder_top * 0.12)
    dip_flange_r = r.neck_r + 0.001
    dip_flange_h = 0.004
    travel = 0.008 * r.joint_travel_scale

    # collar with stem bore (fixed body visual)
    outer = (
        cq.Workplane("XY")
        .workplane(offset=collar_z0)
        .circle(collar_r)
        .extrude(collar_top - collar_z0)
    )
    bore = (
        cq.Workplane("XY")
        .workplane(offset=collar_z0 - 0.001)
        .circle(r.neck_r + 0.0006)
        .extrude((collar_top - 0.002) - (collar_z0 - 0.001))
    )
    collar = outer.cut(bore)
    stem_bore = (
        cq.Workplane("XY")
        .workplane(offset=collar_top - 0.004)
        .circle(stem_r + 0.0008)
        .extrude(0.006)
    )
    collar = collar.cut(stem_bore)
    body.visual(mesh_from_cadquery(collar, "pump_collar"), material=cap_mat, name="pump_collar", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"))

    # dip tube (fixed body visual)
    tube = (
        cq.Workplane("XY")
        .workplane(offset=dip_bottom)
        .circle(dip_r)
        .extrude(collar_z0 - dip_bottom)
    )
    flange = (
        cq.Workplane("XY")
        .workplane(offset=collar_z0 - dip_flange_h)
        .circle(dip_flange_r)
        .circle(dip_r - 0.0002)
        .extrude(dip_flange_h)
    )
    body.visual(
        mesh_from_cadquery(tube.union(flange), "dip_tube"),
        material=accent_mat,
        name="dip_tube", material_class_id="glass.clear_transparent",
    )

    # pump actuator (head + nozzle + stem) — moving child
    head = cq.Workplane("XY").circle(head_r).extrude(head_h)
    nozzle_z = head_h * 0.55
    nozzle = (
        cq.Workplane("YZ")
        .workplane(offset=head_r - 0.001)
        .center(0, nozzle_z)
        .circle(nozzle_r)
        .extrude(nozzle_len)
    )
    head = head.union(nozzle)
    stem = (
        cq.Workplane("XY")
        .workplane(offset=-stem_len)
        .circle(stem_r)
        .extrude(stem_len + 0.002)
    )
    head = head.union(stem)
    tip = (
        cq.Workplane("XY")
        .workplane(offset=0)
        .transformed(offset=(head_r - 0.001 + nozzle_len, 0, nozzle_z))
        .sphere(nozzle_r)
    )
    head = head.union(tip)

    pump = model.part("pump_head")
    pump.visual(mesh_from_cadquery(head, "pump_actuator"), material=cap_mat, name="pump_actuator", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"))
    pump.inertial = Inertial.from_geometry(
        Cylinder(head_r, head_h + stem_len),
        mass=0.006,
        origin=Origin(xyz=(0.0, 0.0, (head_h - stem_len) / 2.0)),
    )
    model.articulation(
        "body_to_pump",
        ArticulationType.PRISMATIC,
        parent=body,
        child=pump,
        origin=Origin(xyz=(0.0, 0.0, collar_top)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(lower=0.0, upper=travel, effort=8.0, velocity=0.15),
    )


def _build_mist(model, body, r, *, cap_mat, accent_mat) -> None:
    """Mist sprayer (var_mist_sprayer): body-fixed crimped collar + 12 crimp
    ridges + dip_tube; actuator (button + +Y nozzle + stem) PRISMATIC -Z press."""
    cs = r.closure_size_scale
    collar_r = (r.neck_r + 0.0025) * cs
    collar_z0 = r.shoulder_top - 0.002
    collar_top = r.neck_top + 0.008
    collar_bore_r = max(r.neck_r - 0.003, 0.0035)
    n_crimp = 12
    crimp_r = 0.0012
    crimp_h = 0.006
    crimp_z0 = collar_z0 + 0.002
    dip_r = 0.0018
    dip_bottom = max(r.wall + 0.004, r.shoulder_top * 0.14)
    dip_top = r.neck_top
    button_r = (r.neck_r + 0.0015) * cs
    button_h = 0.005
    nozzle_r = 0.0014
    nozzle_len = 0.009
    nozzle_local_z = button_h * 0.55
    stem_r = 0.003
    stem_world_bottom = collar_z0 + 0.004
    stem_local_bottom = stem_world_bottom - collar_top
    stem_len = 0.0 - stem_local_bottom
    travel = 0.006 * r.joint_travel_scale

    # crimped collar (fixed body visual)
    outer = (
        cq.Workplane("XY")
        .workplane(offset=collar_z0)
        .circle(collar_r)
        .extrude(collar_top - collar_z0)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=collar_z0 - 0.001)
        .circle(collar_bore_r)
        .extrude((collar_top + 0.001) - (collar_z0 - 0.001))
    )
    body.visual(
        mesh_from_cadquery(outer.cut(inner), "crimped_collar"),
        material=cap_mat,
        name="crimped_collar", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"),
    )
    # crimp ridges (fixed body visuals)
    for i in range(n_crimp):
        angle = 2.0 * math.pi * i / n_crimp
        cx = (collar_r + crimp_r * 0.3) * math.cos(angle)
        cy = (collar_r + crimp_r * 0.3) * math.sin(angle)
        ridge = (
            cq.Workplane("XY")
            .workplane(offset=crimp_z0)
            .center(cx, cy)
            .rect(crimp_r * 2, crimp_r * 1.2)
            .extrude(crimp_h)
        )
        body.visual(
            mesh_from_cadquery(ridge, f"crimp_ridge_{i}"),
            material=cap_mat,
            name=f"crimp_ridge_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"),
        )
    # dip tube (fixed body visual)
    tube = (
        cq.Workplane("XY")
        .workplane(offset=dip_bottom)
        .circle(dip_r)
        .extrude(dip_top - dip_bottom)
    )
    flange = (
        cq.Workplane("XY")
        .workplane(offset=collar_z0 + 0.002)
        .circle(collar_bore_r + 0.0004)  # embed into the collar bore wall (contact)
        .circle(dip_r)
        .extrude(0.004)
    )
    body.visual(
        mesh_from_cadquery(tube.union(flange), "dip_tube"),
        material=accent_mat,
        name="dip_tube", material_class_id="plastic.opaque_generic",
    )

    # actuator (moving child)
    actuator = model.part("actuator")
    disc = cq.Workplane("XY").circle(button_r).extrude(button_h)
    actuator.visual(mesh_from_cadquery(disc, "spray_button"), material=cap_mat, name="spray_button", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"))

    base = cq.Workplane("XY").circle(nozzle_r * 2.0).extrude(0.003)
    base = base.rotate((0, 0, 0), (1, 0, 0), -90)
    base = base.translate((0, button_r - 0.003, nozzle_local_z))
    ntube = cq.Workplane("XY").circle(nozzle_r).extrude(nozzle_len)
    ntube = ntube.rotate((0, 0, 0), (1, 0, 0), -90)
    ntube = ntube.translate((0, button_r - 0.001, nozzle_local_z))
    tip_len = 0.003
    tip_start_y = button_r - 0.001 + nozzle_len - tip_len + 0.001
    tip = cq.Workplane("XY").circle(nozzle_r * 1.5).extrude(tip_len)
    tip = tip.rotate((0, 0, 0), (1, 0, 0), -90)
    tip = tip.translate((0, tip_start_y, nozzle_local_z))
    nozzle = base.union(ntube).union(tip)
    actuator.visual(mesh_from_cadquery(nozzle, "nozzle"), material=cap_mat, name="nozzle", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"))

    stem_center_local = stem_local_bottom + stem_len / 2.0
    actuator.visual(
        Cylinder(stem_r, stem_len),
        origin=Origin(xyz=(0.0, 0.0, stem_center_local)),
        material=accent_mat,
        name="pump_stem", material_class_id="plastic.opaque_generic",
    )
    actuator.inertial = Inertial.from_geometry(
        Cylinder(button_r, button_h),
        mass=0.005,
        origin=Origin(xyz=(0.0, 0.0, button_h / 2.0)),
    )
    model.articulation(
        "body_to_actuator",
        ArticulationType.PRISMATIC,
        parent=body,
        child=actuator,
        origin=Origin(xyz=(0.0, 0.0, collar_top)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(lower=0.0, upper=travel, effort=8.0, velocity=0.05),
    )


def _build_roller(model, body, r, *, cap_mat, accent_mat) -> None:
    """Roller ball (var_roller_ball): body-fixed housing + 3 retainer tabs;
    roller_ball REVOLUTE +X (rolls in socket) + overcap PRISMATIC +Z pull-off.
    Two moving children — the richest joint topology."""
    cs = r.closure_size_scale
    nt = r.neck_top
    housing_r = (r.neck_r + 0.003) * cs
    housing_bore_r = r.neck_r
    housing_z0 = r.shoulder_top + (nt - r.shoulder_top) * 0.5
    platform_top = nt + 0.006
    ball_r = 0.004 * cs
    ball_cz = nt + 0.003
    channel_r = 0.003
    socket_r = ball_r - 0.0001
    retainer_count = 3
    tab_r_offset = ball_r + 0.003
    overcap_r = housing_r + 0.002
    overcap_wall = 0.002
    overcap_top_thick = 0.002
    overcap_height = 0.026
    overcap_z0 = nt - 0.014
    overcap_travel = 0.055 * r.joint_travel_scale
    ridge_z = nt - 0.005
    ridge_inner = housing_r - 0.0001

    # housing (fixed body visual)
    outer = (
        cq.Workplane("XY")
        .workplane(offset=housing_z0)
        .circle(housing_r)
        .extrude(platform_top - housing_z0)
    )
    h_bore = (
        cq.Workplane("XY")
        .workplane(offset=housing_z0 - 0.001)
        .circle(housing_bore_r)
        .extrude(nt - housing_z0 + 0.003)
    )
    housing = outer.cut(h_bore)
    channel = (
        cq.Workplane("XY")
        .workplane(offset=nt - 0.001)
        .circle(channel_r)
        .extrude(platform_top - nt + 0.002)
    )
    housing = housing.cut(channel)
    socket = cq.Workplane("XY").workplane(offset=ball_cz).sphere(socket_r)
    housing = housing.cut(socket)
    body.visual(mesh_from_cadquery(housing, "housing"), material=cap_mat, name="housing", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"))

    # retainer tabs (fixed body visuals)
    tab_solid = cq.Workplane("XY").box(0.003, 0.002, 0.002, centered=(True, True, False))
    tab_mesh = mesh_from_cadquery(tab_solid, "retainer_tab")
    for i in range(retainer_count):
        angle = i * (2.0 * math.pi / retainer_count)
        tx = tab_r_offset * math.cos(angle)
        ty = tab_r_offset * math.sin(angle)
        body.visual(
            tab_mesh,
            origin=Origin(xyz=(tx, ty, platform_top)),
            material=cap_mat,
            name=f"retainer_tab_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"),
        )

    # roller ball (moving child) — frame at the ball centre
    roller_ball = model.part("roller_ball")
    roller_ball.visual(
        Sphere(ball_r), origin=Origin(xyz=(0.0, 0.0, 0.0)), material=accent_mat, name="ball", material_class_id="metal.stainless_matte"
    )
    roller_ball.inertial = Inertial.from_geometry(
        Sphere(ball_r), mass=0.003, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )

    # overcap (moving child). Authored in a LOCAL frame whose origin sits at the
    # cap bottom rim (z=overcap_z0 in world): build at world z then translate by
    # -overcap_z0 so the joint origin (0,0,overcap_z0) lands on real cap geometry
    # (within the 15mm articulation-origin tolerance). Pure +Z prismatic, so the
    # rest pose and kinematics are unchanged.
    o_outer = (
        cq.Workplane("XY")
        .workplane(offset=overcap_z0)
        .circle(overcap_r)
        .extrude(overcap_height)
    )
    o_inner = (
        cq.Workplane("XY")
        .workplane(offset=overcap_z0 - 0.001)
        .circle(overcap_r - overcap_wall)
        .extrude(overcap_height - overcap_top_thick + 0.001)
    )
    cap = o_outer.cut(o_inner)
    ridge = (
        cq.Workplane("XY")
        .workplane(offset=ridge_z)
        .circle(overcap_r - overcap_wall + 0.0001)
        .circle(ridge_inner)
        .extrude(0.002)
    )
    cap = cap.union(ridge).translate((0.0, 0.0, -overcap_z0))
    overcap = model.part("overcap")
    overcap.visual(mesh_from_cadquery(cap, "overcap_shell"), material=accent_mat, name="overcap_shell", material_class_id="metal.stainless_matte")
    overcap.inertial = Inertial.from_geometry(
        Cylinder(overcap_r, overcap_height),
        mass=0.005,
        origin=Origin(xyz=(0.0, 0.0, overcap_height / 2.0)),
    )

    model.articulation(
        "body_to_ball",
        ArticulationType.REVOLUTE,
        parent=body,
        child=roller_ball,
        origin=Origin(xyz=(0.0, 0.0, ball_cz)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=-math.pi, upper=math.pi, effort=1.0, velocity=5.0),
    )
    model.articulation(
        "body_to_overcap",
        ArticulationType.PRISMATIC,
        parent=body,
        child=overcap,
        origin=Origin(xyz=(0.0, 0.0, overcap_z0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=overcap_travel, effort=5.0, velocity=0.1),
    )


def _build_wand(model, body, r, *, cap_mat, accent_mat) -> None:
    """Brush wand (var_brush_wand): twist-off cap shell (dome+grip ring) + long
    stem + doe-foot applicator as ONE rigid part, PRISMATIC +Z pull-out."""
    cs = r.closure_size_scale
    cap_r = (r.neck_r + 0.0028) * cs
    cap_z0 = r.shoulder_top - 0.004
    cap_top = r.neck_top + 0.014
    cap_ceil = 0.003
    stem_r = 0.0012 * cs
    applicator_r = 0.0035 * cs
    applicator_h = 0.010
    # applicator tip seated deep near the bottle floor (also keeps the child
    # AABB within 15mm of the joint origin at z=0).
    stem_tip_z = r.wall + 0.005
    travel = (r.neck_top - r.shoulder_top + 0.055) * r.joint_travel_scale

    # cap shell (white): hollow cylinder + gloss dome + grip ring
    outer = (
        cq.Workplane("XY")
        .workplane(offset=cap_z0)
        .circle(cap_r)
        .extrude(cap_top - cap_z0)
    )
    bore_r = r.neck_r + 0.0006
    bore_start = cap_z0 - 0.001
    bore_end = cap_top - cap_ceil
    inner = (
        cq.Workplane("XY")
        .workplane(offset=bore_start)
        .circle(bore_r)
        .extrude(bore_end - bore_start)
    )
    shell = outer.cut(inner)
    dome = (
        cq.Workplane("XY")
        .workplane(offset=cap_top)
        .circle(cap_r)
        .workplane(offset=0.004)
        .circle(cap_r * 0.35)
        .loft(ruled=False)
    )
    shell = shell.union(dome)
    grip_ring = (
        cq.Workplane("XY")
        .workplane(offset=cap_z0)
        .circle(cap_r + 0.0008)
        .circle(cap_r - 0.0002)
        .extrude(0.003)
    )
    shell = shell.union(grip_ring)

    wand = model.part("wand")
    wand.visual(mesh_from_cadquery(shell, "cap_shell"), material=cap_mat, name="cap_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"))

    stem_top_z = cap_top - cap_ceil
    stem_bottom_z = stem_tip_z + applicator_h
    stem_len = stem_top_z - stem_bottom_z
    stem_cz = (stem_top_z + stem_bottom_z) / 2.0
    wand.visual(
        Cylinder(stem_r, stem_len),
        origin=Origin(xyz=(0.0, 0.0, stem_cz)),
        material=cap_mat,
        name="stem", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"amber_apothecary", "clear_minimal", "frosted_white", "cobalt_blue", "green_glass", "opaque_white", "soft_touch_black", "pearlescent_blush", "matte_sage"} else "metal.precious_gold"),
    )
    # doe-foot applicator tip (loft profile)
    solid = (
        cq.Workplane("XY")
        .workplane(offset=stem_tip_z)
        .circle(0.0005)
        .workplane(offset=applicator_h * 0.30)
        .circle(applicator_r * 0.80)
        .workplane(offset=applicator_h * 0.20)
        .circle(applicator_r)
        .workplane(offset=applicator_h * 0.25)
        .circle(applicator_r * 0.60)
        .workplane(offset=applicator_h * 0.25)
        .circle(stem_r + 0.0002)
        .loft(ruled=False)
    )
    wand.visual(mesh_from_cadquery(solid, "applicator_tip"), material=accent_mat, name="applicator_tip", material_class_id="fabric.velvet")
    wand.inertial = Inertial.from_geometry(
        Cylinder(cap_r, cap_top - stem_tip_z),
        mass=0.010,
        origin=Origin(xyz=(0.0, 0.0, (stem_tip_z + cap_top) / 2.0)),
    )
    model.articulation(
        "body_to_wand",
        ArticulationType.PRISMATIC,
        parent=body,
        child=wand,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=travel, effort=5.0, velocity=0.1),
    )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_bottle_serum(
    config: ContainerBottleSerumConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    body_mat = model.material(f"cbs_body_{r.palette_style}", rgba=pal["body"])  # type: ignore[arg-type]
    cap_mat = model.material(f"cbs_cap_{r.palette_style}", rgba=pal["cap"])  # type: ignore[arg-type]
    accent_mat = model.material(f"cbs_accent_{r.palette_style}", rgba=pal["accent"])  # type: ignore[arg-type]
    label_mat = model.material(f"cbs_label_{r.palette_style}", rgba=pal["label"])  # type: ignore[arg-type]

    # functional sub-part materials (do not follow the colorway)
    clear_mat = model.material("cbs_clear", rgba=_CLEAR_RGBA)
    steel_mat = model.material("cbs_steel", rgba=_STEEL_RGBA)
    flock_mat = model.material("cbs_flock", rgba=_FLOCK_RGBA)
    grey_mat = model.material("cbs_pump_grey", rgba=_PUMP_GREY_RGBA)

    # --- ROOT: serum bottle body ---
    body = model.part("body")
    _emit_body(body, r, body_mat=body_mat, label_mat=label_mat)

    # --- closure mechanism ---
    if r.closure == "dropper_prismatic":
        _build_dropper(model, body, r, cap_mat=cap_mat, accent_mat=clear_mat)
    elif r.closure == "screw_cap_revolute":
        _build_screw_cap(model, body, r, cap_mat=cap_mat)
    elif r.closure == "pump_dispenser_prismatic":
        _build_pump(model, body, r, cap_mat=cap_mat, accent_mat=clear_mat)
    elif r.closure == "mist_sprayer_prismatic":
        _build_mist(model, body, r, cap_mat=cap_mat, accent_mat=grey_mat)
    elif r.closure == "roller_ball_revolute":
        _build_roller(model, body, r, cap_mat=cap_mat, accent_mat=steel_mat)
    elif r.closure == "brush_wand_prismatic":
        _build_wand(model, body, r, cap_mat=cap_mat, accent_mat=flock_mat)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_bottle_serum(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_bottle_serum(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (collar/cap/stem/ball/applicator slipping
# over the neck or captured in a socket) are declared element-scoped so the
# sweep's island/overlap checks pass; the closure action is exercised.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_bottle_serum_tests(
    object_model: ArticulatedObject,
    config: ContainerBottleSerumConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("body")

    # ---- bottle body rests on the ground (base near z=0) ----
    aabb = ctx.part_world_aabb(body)
    bext = _ext(aabb)
    ctx.check(
        "serum bottle body rests on the ground (base near z=0)",
        abs(aabb[0][2]) < 0.012,
        details=f"body min z={aabb[0][2]:.4f}",
    )
    ctx.check(
        "serum bottle body has real volume",
        bext[0] > 0.008 and bext[1] > 0.008 and bext[2] > 0.03,
        details=f"body extents={bext}",
    )

    # ---- body glass material reads as the chosen colorway ----
    glass = body.get_visual("body_glass")
    rgba = getattr(glass.material, "rgba", None)
    ctx.check(
        "body glass material is set from the palette",
        rgba is not None,
        details=f"body_glass rgba={rgba}",
    )

    # ---- label band wraps the body middle ----
    label_aabb = ctx.part_element_world_aabb(body, elem="label_band")
    lmn, lmx = label_aabb
    ctx.check(
        "label band is on the body wall, around the middle",
        lmn[2] > 0.003 and lmx[2] < r.shoulder_top + 0.001,
        details=f"label z=[{lmn[2]:.4f},{lmx[2]:.4f}]",
    )

    # ---- closure: actions + captured-fit overlaps ----
    if r.closure == "dropper_prismatic":
        dropper = object_model.get_part("dropper")
        pull = object_model.get_articulation("body_to_dropper")
        ctx.allow_isolated_part(
            dropper,
            reason="dropper pulls out of the bottle neck and loses body contact",
        )
        ctx.allow_overlap(
            dropper, body, elem_a="collar", elem_b="body_glass",
            reason="The collar intentionally slips over the bottle neck (seated grip).",
        )
        ctx.allow_overlap(
            dropper, body, elem_a="pipette", elem_b="body_glass",
            reason="The pipette is intentionally inserted down through the neck into the bottle.",
        )
        ctx.check(
            "body_to_dropper is PRISMATIC about +Z",
            pull.articulation_type == ArticulationType.PRISMATIC and abs(pull.axis[2]) > 0.99,
            details=f"axis={pull.axis}, type={pull.articulation_type}",
        )
        pip_rest = ctx.part_element_world_aabb(dropper, elem="pipette")
        ctx.check(
            "pipette tip is seated deep inside the bottle at rest",
            pip_rest[0][2] < r.shoulder_top - 0.005,
            details=f"pipette bottom z(rest)={pip_rest[0][2]:.4f}",
        )
        rest = ctx.part_world_position(dropper)
        with ctx.pose({pull: pull.motion_limits.upper}):
            up = ctx.part_world_position(dropper)
        ctx.check(
            "dropper pulls straight up (no lateral shift)",
            up[2] > rest[2] + 0.03
            and abs(up[0] - rest[0]) < 1e-4 and abs(up[1] - rest[1]) < 1e-4,
            details=f"rest={rest}, up={up}",
        )

    elif r.closure == "screw_cap_revolute":
        cap = object_model.get_part("cap")
        twist = object_model.get_articulation("body_to_cap")
        ctx.allow_overlap(
            cap, body, elem_a="cap_shell", elem_b="body_glass",
            reason="The cap bore has a slight interference fit over the neck (screw-cap grip).",
        )
        ctx.expect_overlap(
            cap, body, axes="z", elem_a="cap_shell", elem_b="body_glass",
            min_overlap=0.004, name="cap skirt overlaps the neck along Z",
        )
        ctx.check(
            "body_to_cap is REVOLUTE about +Z",
            twist.articulation_type == ArticulationType.REVOLUTE and abs(twist.axis[2]) > 0.99,
            details=f"axis={twist.axis}, type={twist.articulation_type}",
        )
        rest = ctx.part_world_position(cap)
        with ctx.pose({twist: math.pi}):
            half = ctx.part_world_position(cap)
        ctx.check(
            "cap rotates in place (same height, no lateral shift)",
            abs(half[2] - rest[2]) < 1e-4
            and abs(half[0] - rest[0]) < 1e-4 and abs(half[1] - rest[1]) < 1e-4,
            details=f"rest={rest}, half_turn={half}",
        )

    elif r.closure == "pump_dispenser_prismatic":
        pump = object_model.get_part("pump_head")
        press = object_model.get_articulation("body_to_pump")
        ctx.allow_overlap(
            body, pump, elem_a="pump_collar", elem_b="pump_actuator",
            reason="The pump stem is intentionally captured inside the collar bore (sliding fit).",
        )
        ctx.allow_overlap(
            body, pump, elem_a="dip_tube", elem_b="pump_actuator",
            reason="The pump stem meets the dip-tube top inside the collar bore (captured fluid path).",
        )
        ctx.allow_overlap(
            body, pump, elem_a="body_glass", elem_b="pump_actuator",
            reason="The pump stem is inserted through the neck bore into the bottle interior (deep insertion).",
        )
        ctx.check(
            "body_to_pump is PRISMATIC about -Z",
            press.articulation_type == ArticulationType.PRISMATIC and press.axis[2] < -0.99,
            details=f"axis={press.axis}, type={press.articulation_type}",
        )
        ctx.expect_origin_distance(
            pump, body, axes="xy", max_dist=0.001,
            name="pump stem axis stays aligned with body axis (XY)",
        )
        dip_rest = ctx.part_element_world_aabb(body, elem="dip_tube")
        ctx.check(
            "dip tube reaches deep into the bottle",
            dip_rest[0][2] < r.body_top * 0.6,
            details=f"dip_tube bottom z={dip_rest[0][2]:.4f}",
        )
        rest = ctx.part_world_position(pump)
        with ctx.pose({press: press.motion_limits.upper}):
            pressed = ctx.part_world_position(pump)
            dip_pressed = ctx.part_element_world_aabb(body, elem="dip_tube")
        ctx.check(
            "pump head presses straight down (no lateral shift)",
            pressed[2] < rest[2] - 0.003
            and abs(pressed[0] - rest[0]) < 1e-4 and abs(pressed[1] - rest[1]) < 1e-4,
            details=f"rest={rest}, pressed={pressed}",
        )
        ctx.check(
            "dip tube stays stationary when pump is pressed",
            abs(dip_rest[0][2] - dip_pressed[0][2]) < 1e-5,
            details=f"rest={dip_rest[0][2]:.4f}, pressed={dip_pressed[0][2]:.4f}",
        )

    elif r.closure == "mist_sprayer_prismatic":
        actuator = object_model.get_part("actuator")
        press = object_model.get_articulation("body_to_actuator")
        ctx.allow_overlap(
            actuator, body, elem_a="pump_stem", elem_b="crimped_collar",
            reason="The pump stem is intentionally inserted down into the collar bore.",
        )
        ctx.allow_overlap(
            actuator, body, elem_a="pump_stem", elem_b="dip_tube",
            reason="The pump stem meets the dip-tube top inside the collar bore (captured fluid path).",
        )
        ctx.expect_overlap(
            actuator, body, axes="z", elem_a="pump_stem", elem_b="crimped_collar",
            min_overlap=0.0015, name="pump stem inserted into collar at rest",
        )
        ctx.check(
            "body_to_actuator is PRISMATIC about -Z",
            press.articulation_type == ArticulationType.PRISMATIC and press.axis[2] < -0.99,
            details=f"axis={press.axis}, type={press.articulation_type}",
        )
        n_ridges = sum(1 for v in body.visuals if v.name.startswith("crimp_ridge_"))
        ctx.check(
            "collar has 12 crimp ridges (fixed body visuals)",
            n_ridges == 12,
            details=f"found {n_ridges} ridges",
        )
        rest = ctx.part_world_position(actuator)
        with ctx.pose({press: press.motion_limits.upper}):
            pressed = ctx.part_world_position(actuator)
        ctx.check(
            "actuator presses straight down (no lateral shift)",
            pressed[2] < rest[2] - 0.002
            and abs(pressed[0] - rest[0]) < 1e-4 and abs(pressed[1] - rest[1]) < 1e-4,
            details=f"rest={rest}, pressed={pressed}",
        )

    elif r.closure == "roller_ball_revolute":
        roller_ball = object_model.get_part("roller_ball")
        overcap = object_model.get_part("overcap")
        ball_joint = object_model.get_articulation("body_to_ball")
        cap_joint = object_model.get_articulation("body_to_overcap")
        ctx.allow_overlap(
            roller_ball, body, elem_a="ball", elem_b="housing",
            reason="The roller ball is intentionally captured in the housing socket cup.",
        )
        ctx.allow_overlap(
            overcap, body, elem_a="overcap_shell", elem_b="housing",
            reason="The overcap retention ridge intentionally clips over the housing exterior.",
        )
        ctx.check(
            "body_to_ball is REVOLUTE about +X",
            ball_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(ball_joint.axis[0]) > 0.99,
            details=f"axis={ball_joint.axis}, type={ball_joint.articulation_type}",
        )
        ctx.check(
            "body_to_overcap is PRISMATIC about +Z (second mover)",
            cap_joint.articulation_type == ArticulationType.PRISMATIC
            and abs(cap_joint.axis[2]) > 0.99,
            details=f"axis={cap_joint.axis}, type={cap_joint.articulation_type}",
        )
        # ball rotation: sphere invariant (AABB does not move)
        ball0 = ctx.part_element_world_aabb(roller_ball, elem="ball")
        with ctx.pose({ball_joint: 1.0}):
            ball1 = ctx.part_element_world_aabb(roller_ball, elem="ball")
        ctx.check(
            "ball stays centred after rotation (sphere invariant)",
            abs(ball1[0][2] - ball0[0][2]) < 0.002 and abs(ball1[1][2] - ball0[1][2]) < 0.002,
            details=f"rest z=[{ball0[0][2]:.4f},{ball0[1][2]:.4f}], rot z=[{ball1[0][2]:.4f},{ball1[1][2]:.4f}]",
        )
        # overcap pulls up and clears the ball
        rest = ctx.part_world_position(overcap)
        with ctx.pose({cap_joint: cap_joint.motion_limits.upper}):
            off = ctx.part_world_position(overcap)
            cap_off_bottom = ctx.part_world_aabb(overcap)[0]
        ctx.check(
            "overcap pulls straight up off the bottle",
            off[2] > rest[2] + 0.03
            and abs(off[0] - rest[0]) < 1e-4 and abs(off[1] - rest[1]) < 1e-4,
            details=f"rest={rest}, off={off}",
        )
        ctx.check(
            "overcap clears the ball at full removal",
            cap_off_bottom[2] > ball0[1][2],
            details=f"cap bottom(off)={cap_off_bottom[2]:.4f}, ball top={ball0[1][2]:.4f}",
        )

    elif r.closure == "brush_wand_prismatic":
        wand = object_model.get_part("wand")
        pull = object_model.get_articulation("body_to_wand")
        ctx.allow_isolated_part(
            wand,
            reason="wand pulls out of the bottle neck and loses body contact",
        )
        ctx.allow_overlap(
            wand, body, elem_a="cap_shell", elem_b="body_glass",
            reason="The twist-off cap shell intentionally slips over the neck for a seated grip.",
        )
        ctx.allow_overlap(
            wand, body, elem_a="stem", elem_b="body_glass",
            reason="The wand stem passes through the neck bore into the bottle interior.",
        )
        ctx.allow_overlap(
            wand, body, elem_a="applicator_tip", elem_b="body_glass",
            reason="The doe-foot applicator tip is intentionally inserted into the bottle.",
        )
        ctx.check(
            "body_to_wand is PRISMATIC about +Z",
            pull.articulation_type == ArticulationType.PRISMATIC and abs(pull.axis[2]) > 0.99,
            details=f"axis={pull.axis}, type={pull.articulation_type}",
        )
        tip_rest = ctx.part_element_world_aabb(wand, elem="applicator_tip")
        ctx.check(
            "applicator tip is seated deep inside the bottle at rest",
            tip_rest[0][2] < r.shoulder_top - 0.005,
            details=f"applicator bottom z(rest)={tip_rest[0][2]:.4f}",
        )
        rest = ctx.part_world_position(wand)
        with ctx.pose({pull: pull.motion_limits.upper}):
            up = ctx.part_world_position(wand)
        ctx.check(
            "wand pulls straight up (no lateral shift)",
            up[2] > rest[2] + 0.03
            and abs(up[0] - rest[0]) < 1e-4 and abs(up[1] - rest[1]) < 1e-4,
            details=f"rest={rest}, up={up}",
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

    return ctx.report()
