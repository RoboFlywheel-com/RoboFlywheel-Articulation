# SPDX-License-Identifier: Apache-2.0

"""Container can — modular procedural template (lidded metal beverage/food/tin can).

Category identity: an upright hollow metal can / tin. The hollow can body (ROOT)
rests on z=0 with its axis along +Z; a lid/cap closes the mouth by one of several
mechanisms (the main articulation). No multiplicity axis — one can, one closure.

Two parallel slots (spec ``Container_Can.md``):

  * ``body_shape`` (5) — the ROOT ``body`` mesh, a thick-walled hollow open-top
    shell. Different cross-sections / footprints, each a real open cavity:
      - round_cylinder: straight-wall cylinder (extrude circle), taller-than-wide.
      - round_tapered_tub: loft cone wall (mouth wider than base) + rolled rim
        flange, wider-than-tall (deli tub).
      - rounded_square: filleted box shell with an inset rabbet rim, near-cube.
      - hex_prism: regular hexagonal prism (polygon(6)), across-flats footprint.
      - flat_rect_flask: flat hip-flask box (width>depth), filleted vertical and
        top/bottom edges.
  * ``closure`` (4) — the lid/cap mechanism (>=1 non-fixed joint each):
      - lift_off_lid: single PRISMATIC +Z lift-off lid, skirt sleeves the rim.
      - press_fit_skirt_lid: PRISMATIC +Z, inset skirt wraps an inset rabbet rim.
      - screw_cap: CONTINUOUS spin + PRISMATIC lift via a massless ``cap_carrier``
        on a round threaded neck (KnobGeometry knurled cap).
      - hinge_lid: REVOLUTE +X flip lid hinged at the back rim (ear + knuckle).

Continuous size/proportion variation (height/radius/neck/lid/travel scales) lives
in ``resolve_config`` as clamped params, never as slot candidates. The
``palette_style`` (10 coordinated colorways, each with a finish hint) is palette
only and not counted as a slot choice.

Sources (articraft_data ``picture/Container/Can`` 5-star pool): parents
``fb4296aa`` (round canister lift-off), ``6b6cb24d`` (deli tub), ``c6ba1d09``
(square press-fit), ``f4f34d34`` (hex tea tin), ``6e35123f`` (fuel-flask screw
cap), plus the ``rec_container_can_var_*`` forks that fill the body×closure grid
(round/square/hex/flatrect × screw/hinge, flatrect × lift-off).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Container_Can.md``
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
    KnobBore,
    KnobGeometry,
    KnobGrip,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyShape = Literal[
    "round_cylinder",
    "round_tapered_tub",
    "rounded_square",
    "hex_prism",
    "flat_rect_flask",
]
Closure = Literal[
    "lift_off_lid",
    "press_fit_skirt_lid",
    "screw_cap",
    "hinge_lid",
]
PaletteStyle = Literal[
    "brushed_steel",
    "brushed_pewter",
    "brass_lid_accent",
    "dark_bronze_cap",
    "clear_pet_tint",
    "painted_tin",
    "glossy_print",
    "anodized_gold",
    "anodized_blue",
    "hammered_tin",
]

BODY_SHAPES: tuple[BodyShape, ...] = (
    "round_cylinder",
    "round_tapered_tub",
    "rounded_square",
    "hex_prism",
    "flat_rect_flask",
)
CLOSURES: tuple[Closure, ...] = (
    "lift_off_lid",
    "press_fit_skirt_lid",
    "screw_cap",
    "hinge_lid",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brushed_steel",
    "brushed_pewter",
    "brass_lid_accent",
    "dark_bronze_cap",
    "clear_pet_tint",
    "painted_tin",
    "glossy_print",
    "anodized_gold",
    "anodized_blue",
    "hammered_tin",
)

# ---------------------------------------------------------------------------
# Palettes: 10 coordinated colorways. Each = body + lid/cap + accent rgba plus a
# ``finish`` hint (render-semantics only, not a slot choice). First six are
# sampled directly from 5-star source RGBA; the last four are plausible metal-can
# colorways. ``accent`` drives label / marker / gasket / hinge / seam visuals.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, object]] = {
    "brushed_steel": {
        "finish": "brushed_metal",
        "body": (0.80, 0.81, 0.83, 1.0),
        "lid": (0.80, 0.81, 0.83, 1.0),
        "accent": (0.70, 0.71, 0.73, 1.0),
    },
    "brushed_pewter": {
        "finish": "brushed_metal",
        "body": (0.74, 0.75, 0.77, 1.0),
        "lid": (0.70, 0.71, 0.73, 1.0),
        "accent": (0.66, 0.67, 0.69, 1.0),
    },
    "brass_lid_accent": {
        "finish": "brass_bronze_accent",
        "body": (0.62, 0.64, 0.67, 1.0),
        "lid": (0.72, 0.60, 0.30, 1.0),
        "accent": (0.55, 0.48, 0.30, 1.0),
    },
    "dark_bronze_cap": {
        "finish": "dark_bronze",
        "body": (0.74, 0.76, 0.79, 1.0),
        "lid": (0.42, 0.33, 0.24, 1.0),
        "accent": (0.12, 0.12, 0.12, 1.0),
    },
    "clear_pet_tint": {
        "finish": "clear_pet",
        "body": (0.80, 0.86, 0.88, 0.30),
        "lid": (0.78, 0.85, 0.88, 0.30),
        "accent": (0.93, 0.93, 0.90, 1.0),
    },
    "painted_tin": {
        "finish": "matte_paint",
        "body": (0.82, 0.16, 0.14, 1.0),
        "lid": (0.82, 0.16, 0.14, 1.0),
        "accent": (0.93, 0.93, 0.90, 1.0),
    },
    "glossy_print": {
        "finish": "glossy_print",
        "body": (0.10, 0.42, 0.78, 1.0),
        "lid": (0.86, 0.87, 0.89, 1.0),
        "accent": (0.86, 0.14, 0.16, 1.0),
    },
    "anodized_gold": {
        "finish": "anodized",
        "body": (0.83, 0.69, 0.32, 1.0),
        "lid": (0.83, 0.69, 0.32, 1.0),
        "accent": (0.55, 0.48, 0.30, 1.0),
    },
    "anodized_blue": {
        "finish": "anodized",
        "body": (0.18, 0.34, 0.55, 1.0),
        "lid": (0.18, 0.34, 0.55, 1.0),
        "accent": (0.74, 0.76, 0.79, 1.0),
    },
    "hammered_tin": {
        "finish": "hammered",
        "body": (0.66, 0.63, 0.58, 1.0),
        "lid": (0.66, 0.63, 0.58, 1.0),
        "accent": (0.40, 0.42, 0.45, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Base geometry per body shape (meters). Scaled per-build by resolve_config.
#   body_dim = the controlling plan half-size: round=outer radius,
#              square=half-width, hex=circumradius, flask=half-width(X).
#   For flask, depth_ratio applies the secondary (Y) half-depth.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _ShapeGeom:
    body_dim: float  # plan half-size (radius / half-width / circumradius)
    body_h: float  # body height (rim sits near this z)
    wall: float
    floor: float
    depth_ratio: float  # flask: half-depth / half-width; else 1.0
    kind: str  # "round" | "tub" | "square" | "hex" | "flask"


_SHAPES: dict[BodyShape, _ShapeGeom] = {
    # round canister: taller-than-wide cylinder (fb4296aa).
    "round_cylinder": _ShapeGeom(0.050, 0.118, 0.0035, 0.004, 1.0, "round"),
    # deli tub: loft cone (mouth wider than base) + rolled rim, wider-than-tall.
    "round_tapered_tub": _ShapeGeom(0.058, 0.058, 0.0030, 0.0035, 1.0, "tub"),
    # square tin: near-cube filleted box shell + inset rabbet rim (c6ba1d09).
    "rounded_square": _ShapeGeom(0.060, 0.108, 0.0035, 0.004, 1.0, "square"),
    # hex tea tin: tall hexagonal prism across-flats (f4f34d34).
    "hex_prism": _ShapeGeom(0.0404, 0.130, 0.0025, 0.004, 1.0, "hex"),
    # flat hip-flask: width(X) > depth(Y), filleted edges (6e35123f).
    "flat_rect_flask": _ShapeGeom(0.065, 0.130, 0.0035, 0.004, 0.46, "flask"),
}

# closure nominal sizes.
_LID_TOP_H = 0.010  # flat lid top-plate thickness
_SKIRT_H = 0.018  # how far a lift-off / press-fit skirt drops over the rim
_SKIRT_OVERLAP = 0.010  # seated skirt-over-rim overlap depth
_LID_LIFT = 0.040  # straight lift-off travel
_RABBET_INSET = 0.004  # press-fit rim rabbet inset (square body)
_NECK_H = 0.020  # screw neck height
_SHOULDER_H = 0.004  # screw shoulder plate thickness
_CAP_H = 0.028  # screw cap total height
_CARRIER_RING_H = 0.003  # tamper-ring carrier height
_CAP_LIFT = 0.050  # screw carrier prismatic travel


@dataclass(frozen=True)
class ContainerCanConfig:
    body_shape: BodyShape = "round_cylinder"
    closure: Closure = "lift_off_lid"
    palette_style: PaletteStyle = "brushed_steel"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    neck_radius_scale: float = 1.0
    lid_height_scale: float = 1.0
    joint_travel_scale: float = 1.0
    name: str = "container_can"


@dataclass(frozen=True)
class ResolvedContainerCanConfig:
    body_shape: BodyShape
    closure: Closure
    palette_style: PaletteStyle
    body_height_scale: float
    body_radius_scale: float
    neck_radius_scale: float
    lid_height_scale: float
    joint_travel_scale: float
    # derived geometry
    body_dim: float  # plan half-size
    body_h: float  # body height
    wall: float
    floor: float
    depth_dim: float  # secondary half-size (flask Y); == body_dim for others
    kind: str
    inradius: float  # inscribed-circle radius of the plan section (neck must fit)
    rim_top_z: float  # world z of the rim seam plane (lift/press/hinge mount)
    # screw neck (only meaningful for closure == screw_cap)
    neck_r: float
    neck_ir: float
    neck_base_z: float
    neck_top_z: float
    cap_od: float
    cap_bore_d: float
    # lid sizing
    lid_outer_dim: float  # lid plan half-size (proud of body)
    lid_h: float
    # hinge
    hinge_back: float  # y of the back rim hinge line (negative)
    hinge_open_upper: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerCanConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    return ContainerCanConfig(
        body_shape=rng.choice(BODY_SHAPES),
        closure=rng.choice(CLOSURES),
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.85, 1.20), 4),
        body_radius_scale=round(rng.uniform(0.88, 1.15), 4),
        neck_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        lid_height_scale=round(rng.uniform(0.85, 1.15), 4),
        joint_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_can_{seed}",
    )


def resolve_config(
    config: ContainerCanConfig | None = None,
) -> ResolvedContainerCanConfig:
    cfg = config or ContainerCanConfig()
    body_shape = _pick(cfg.body_shape, BODY_SHAPES)
    closure = _pick(cfg.closure, CLOSURES)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    g = _SHAPES[body_shape]
    h_scale = _clamp(cfg.body_height_scale, 0.85, 1.20)
    r_scale = _clamp(cfg.body_radius_scale, 0.88, 1.15)
    n_scale = _clamp(cfg.neck_radius_scale, 0.90, 1.10)
    lh_scale = _clamp(cfg.lid_height_scale, 0.85, 1.15)
    jt_scale = _clamp(cfg.joint_travel_scale, 0.85, 1.10)

    body_dim = g.body_dim * r_scale
    body_h = g.body_h * h_scale
    depth_dim = body_dim * g.depth_ratio

    # Inscribed-circle radius of the plan section (the largest round neck that
    # fits inside the mouth without piercing the wall).
    if g.kind == "hex":
        # across-flats inradius = circumradius * cos(30deg).
        inradius = body_dim * math.cos(math.radians(30.0))
    elif g.kind in ("round", "tub"):
        inradius = body_dim
    else:  # square / flask: limited by the smaller plan half-size
        inradius = min(body_dim, depth_dim)

    rim_top_z = body_h

    # ---- screw neck (round, centered on the top deck) ----
    # NECK_R follows the body radius and its own scale, clamped strictly inside
    # the inscribed circle so the neck never pierces the wall (conditional).
    neck_r = _clamp(0.030 * r_scale * n_scale, 0.012, max(inradius - 0.006, 0.013))
    neck_ir = max(neck_r - 0.0035, 0.006)
    neck_base_z = body_h + _SHOULDER_H
    neck_top_z = neck_base_z + _NECK_H
    # Cap bore grips the neck outer with a slight interference (equation: bore =
    # neck - small, a captured friction/thread fit allowed via allow_overlap) so
    # the cap actually contacts the neck rather than floating off it; cap OD is
    # proud of the bore so the cap reads as a real cap.
    cap_bore_d = 2.0 * (neck_r - 0.0004)
    cap_od = cap_bore_d + 0.012

    # ---- lift / press lid sizing ----
    lid_outer_dim = body_dim + 0.0015  # lid slightly proud of the body rim
    lid_h = _LID_TOP_H * lh_scale

    # ---- hinge back rim line + open limit (conditional on body shape) ----
    if g.kind in ("round", "tub"):
        hinge_back = -body_dim
        hinge_open_upper = 2.8 * jt_scale
    elif g.kind == "hex":
        hinge_back = -inradius
        hinge_open_upper = 2.6 * jt_scale
    elif g.kind == "square":
        hinge_back = -body_dim
        hinge_open_upper = 2.6 * jt_scale
    else:  # flask: shallow mouth, limit the open angle so the lid clears the body
        hinge_back = -depth_dim
        hinge_open_upper = 2.0 * jt_scale

    return ResolvedContainerCanConfig(
        body_shape=body_shape,
        closure=closure,
        palette_style=palette,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        neck_radius_scale=n_scale,
        lid_height_scale=lh_scale,
        joint_travel_scale=jt_scale,
        body_dim=body_dim,
        body_h=body_h,
        wall=g.wall,
        floor=g.floor,
        depth_dim=depth_dim,
        kind=g.kind,
        inradius=inradius,
        rim_top_z=rim_top_z,
        neck_r=neck_r,
        neck_ir=neck_ir,
        neck_base_z=neck_base_z,
        neck_top_z=neck_top_z,
        cap_od=cap_od,
        cap_bore_d=cap_bore_d,
        lid_outer_dim=lid_outer_dim,
        lid_h=lid_h,
        hinge_back=hinge_back,
        hinge_open_upper=hinge_open_upper,
        name=cfg.name or "container_can",
    )


def with_overrides(config: ContainerCanConfig, **kwargs: object) -> ContainerCanConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerCanConfig | ResolvedContainerCanConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedContainerCanConfig) else resolve_config(config)
    return (
        ("body_shape", r.body_shape),
        ("closure", r.closure),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Slot A — body shell solids (open-top hollow). Authored standing on z=0.
# ===========================================================================
def _hex_diam(circum: float) -> float:
    """cq.polygon(6, diameter) inscribes vertices on radius diameter/2."""
    return circum * 2.0


def _round_body_solid(r: ResolvedContainerCanConfig) -> cq.Workplane:
    """Straight-wall hollow cylinder, open top (fb4296aa ``_body_solid``)."""
    outer = cq.Workplane("XY").circle(r.body_dim).extrude(r.body_h)
    inner = (
        cq.Workplane("XY")
        .workplane(offset=r.floor)
        .circle(r.body_dim - r.wall)
        .extrude(r.body_h)  # overshoots the top so the rim is open
    )
    return outer.cut(inner)


def _tub_body_solid(r: ResolvedContainerCanConfig) -> cq.Workplane:
    """Tapered loft wall (mouth wider than base) + rolled rim flange
    (6b6cb24d ``_tub_solid``)."""
    base_r = r.body_dim - 0.011
    mouth_r = r.body_dim
    outer = (
        cq.Workplane("XY")
        .circle(base_r)
        .workplane(offset=r.body_h)
        .circle(mouth_r)
        .loft(ruled=True)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=r.floor)
        .circle(base_r - r.wall)
        .workplane(offset=r.body_h)
        .circle(mouth_r - r.wall)
        .loft(ruled=True)
    )
    shell = outer.cut(inner)
    rim = (
        cq.Workplane("XY")
        .workplane(offset=r.body_h)
        .circle(mouth_r + 0.004)
        .circle(mouth_r - r.wall)
        .extrude(-0.004)
    )
    return shell.union(rim)


def _rounded_square_prism(half: float, fillet: float, z0: float, z1: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .rect(2.0 * half, 2.0 * half)
        .extrude(z1 - z0)
        .edges("|Z")
        .fillet(fillet)
    )


def _rounded_rect_prism(
    half_x: float, half_y: float, fillet: float, z0: float, z1: float
) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .rect(2.0 * half_x, 2.0 * half_y)
        .extrude(z1 - z0)
        .edges("|Z")
        .fillet(fillet)
    )


def _square_body_solid(r: ResolvedContainerCanConfig) -> cq.Workplane:
    """Filleted box shell with an inset rabbet rim (c6ba1d09 ``_body_solid``).

    The rabbet band (where a press-fit lid skirt seats against an inset rim
    shoulder) is only cut for the lid closures that consume it; screw/hinge keep
    the full rim for a clean neck/ear weld."""
    half = r.body_dim
    fillet = min(0.012, half * 0.2)
    rim_top = r.body_h
    outer = _rounded_square_prism(half, fillet, 0.0, rim_top)
    inner = _rounded_square_prism(
        half - r.wall, max(fillet - r.wall, 0.002), r.floor, rim_top + 0.001
    )
    shell = outer.cut(inner)
    if r.closure == "press_fit_skirt_lid":
        # Shave a thin outer sliver off the top band so an inset rim shoulder
        # remains for the press-fit skirt to seat against. The sliver must be
        # thinner than the wall (else the whole rim is removed).
        sliver = min(_RABBET_INSET, r.wall * 0.6)
        rabbet_outer = _rounded_square_prism(half + 0.001, fillet, rim_top - 0.014, rim_top + 0.001)
        rabbet_inner = _rounded_square_prism(
            half - sliver, max(fillet - sliver, 0.002), rim_top - 0.014, rim_top + 0.001
        )
        shell = shell.cut(rabbet_outer.cut(rabbet_inner))
    return shell


def _hex_body_solid(r: ResolvedContainerCanConfig) -> cq.Workplane:
    """Hollow regular hexagonal prism, open top (f4f34d34 ``_hex_body``)."""
    circum = r.body_dim
    inner_circum = circum - r.wall / math.cos(math.radians(30.0))
    outer = cq.Workplane("XY").polygon(6, _hex_diam(circum)).extrude(r.body_h)
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=r.floor)
        .polygon(6, _hex_diam(inner_circum))
        .extrude(r.body_h)
    )
    return outer.cut(cavity)


def _flask_body_solid(r: ResolvedContainerCanConfig) -> cq.Workplane:
    """Flat hip-flask box, width(X)>depth(Y), filleted edges
    (6e35123f ``_flask_body``)."""
    bw = 2.0 * r.body_dim
    bd = 2.0 * r.depth_dim
    bh = r.body_h
    edge_r = min(0.012, r.depth_dim * 0.35)
    body = (
        cq.Workplane("XY")
        .box(bw, bd, bh, centered=(True, True, False))
        .edges("|Z")
        .fillet(edge_r)
    )
    body = body.edges("|X or |Y").fillet(min(0.006, edge_r * 0.6))
    inner = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, r.floor))
        .box(bw - 2 * r.wall, bd - 2 * r.wall, bh - r.floor, centered=(True, True, False))
        .edges("|Z")
        .fillet(max(edge_r - r.wall, 0.002))
    )
    return body.cut(inner)


def _body_solid(r: ResolvedContainerCanConfig) -> cq.Workplane:
    if r.kind == "round":
        return _round_body_solid(r)
    if r.kind == "tub":
        return _tub_body_solid(r)
    if r.kind == "square":
        return _square_body_solid(r)
    if r.kind == "hex":
        return _hex_body_solid(r)
    return _flask_body_solid(r)


def _screw_neck_solid(r: ResolvedContainerCanConfig) -> cq.Workplane:
    """Round shoulder plate + threaded neck rising from the body mouth, centered
    on the top deck (round_screwcap ``_body_solid`` neck section).

    For non-round bodies this caps the open mouth with a section-matched deck
    plate that dips into the body wall so it fuses into one solid, then rises a
    round neck — exactly the variant pattern."""
    # Deck plate caps the mouth, shaped to the body section and dipping well DOWN
    # into the body (below any rim rabbet band) so it overlaps the inner wall
    # solidly (a true fused solid, not a tangent-touch compound). A central hole
    # keeps the neck bore.
    deck_z0 = r.body_h - 0.020
    deck_z1 = r.body_h + _SHOULDER_H
    if r.kind in ("round", "tub"):
        deck = (
            cq.Workplane("XY")
            .workplane(offset=deck_z0)
            .circle(r.body_dim - r.wall * 0.5)
            .extrude(deck_z1 - deck_z0)
        )
    elif r.kind == "hex":
        deck = (
            cq.Workplane("XY")
            .workplane(offset=deck_z0)
            .polygon(6, _hex_diam(r.body_dim - r.wall * 0.5))
            .extrude(deck_z1 - deck_z0)
        )
    elif r.kind == "square":
        deck = _rounded_square_prism(
            r.body_dim - r.wall * 0.5, min(0.010, r.body_dim * 0.18), deck_z0, deck_z1
        )
    else:  # flask
        deck = _rounded_rect_prism(
            r.body_dim - r.wall * 0.5,
            r.depth_dim - r.wall * 0.5,
            min(0.008, r.depth_dim * 0.3),
            deck_z0,
            deck_z1,
        )
    bore = (
        cq.Workplane("XY")
        .workplane(offset=deck_z0 - 0.001)
        .circle(r.neck_ir)
        .extrude((deck_z1 - deck_z0) + 0.002)
    )
    shoulder = deck.cut(bore)
    neck_outer = (
        cq.Workplane("XY")
        .workplane(offset=r.neck_base_z)
        .circle(r.neck_r)
        .extrude(_NECK_H)
    )
    neck_bore = (
        cq.Workplane("XY")
        .workplane(offset=r.neck_base_z - 0.001)
        .circle(r.neck_ir)
        .extrude(_NECK_H + 0.002)
    )
    neck = neck_outer.cut(neck_bore)
    solid = shoulder.union(neck)
    # Thread grooves: a few ring cuts on the neck exterior (decorative density).
    for i in range(4):
        gz = r.neck_base_z + 0.003 + i * 0.004
        if gz > r.neck_top_z - 0.0015:
            break
        groove = (
            cq.Workplane("XY")
            .workplane(offset=gz)
            .circle(r.neck_r + 0.001)
            .circle(r.neck_r - 0.0012)
            .extrude(0.0015)
        )
        solid = solid.cut(groove)
    return solid


def _hinge_ear_solid(r: ResolvedContainerCanConfig) -> cq.Workplane:
    """Hinge ear: a small tab rising from the back rim, embedded into the body
    wall for connectivity (round_hingelid body ear L64-L74)."""
    ear_w = 0.022
    ear_d = 0.012
    ear_h = 0.007
    # Embed deep enough to reach below the square rabbet band (~14mm) into solid
    # wall so the ear fuses to the body rather than landing on a cut rim.
    ear_embed = 0.018
    ear_center_y = r.hinge_back + (ear_d / 2 - 0.006)  # radial overlap into wall
    return (
        cq.Workplane("XY")
        .workplane(offset=r.rim_top_z - ear_embed)
        .center(0.0, ear_center_y)
        .rect(ear_w, ear_d)
        .extrude(ear_h + ear_embed)
    )


def _inertial_box(r: ResolvedContainerCanConfig, top_z: float):
    return Inertial.from_geometry(
        Box((2 * r.body_dim, 2 * r.depth_dim, top_z)),
        mass=0.18,
        origin=Origin(xyz=(0.0, 0.0, top_z / 2.0)),
    )


def _emit_body(body, r: ResolvedContainerCanConfig, *, body_mat) -> None:
    solid = _body_solid(r)
    if r.closure == "screw_cap":
        solid = solid.union(_screw_neck_solid(r))
    if r.closure == "hinge_lid":
        solid = solid.union(_hinge_ear_solid(r))
    body.visual(mesh_from_cadquery(solid, "body_shell"), material=body_mat, name="body_shell", material_class_id=("metal.aluminum_bare" if r.palette_style in {"brushed_steel", "brushed_pewter", "brass_lid_accent", "dark_bronze_cap", "painted_tin", "glossy_print", "anodized_gold", "anodized_blue", "hammered_tin"} else "plastic.clear_rigid"))
    top_z = r.neck_top_z if r.closure == "screw_cap" else r.rim_top_z
    body.inertial = _inertial_box(r, top_z)


# ===========================================================================
# Slot B — closure builders. Each attaches one closure mechanism to the body.
# ===========================================================================
def _lift_lid_solid(r: ResolvedContainerCanConfig, *, inset: bool, fwd: float) -> cq.Workplane:
    """Flat top plate + downward skirt that sleeves the rim. Authored in the
    lid's own frame with the skirt bottom at local z=0 (so the joint origin sits
    on the rim seam). The whole lid is centered at local y=``fwd`` so it caps the
    can after the off-axis (back-rim) prismatic origin re-centers it; the back
    skirt wall then passes through the child-local origin so child geometry exists
    at the joint origin. ``inset`` => press-fit skirt wrapping an inset rabbet rim.

    Round/tub use a round skirt; square uses a rounded-square skirt; flask a
    rounded-rect skirt; hex a hex skirt — the skirt section follows the body
    section so the back skirt wall passes through the child-local origin."""
    skirt_h = _SKIRT_H * r.lid_height_scale
    outer = r.lid_outer_dim

    if r.kind in ("round", "tub"):
        lid_r = r.body_dim + 0.0015
        # Skirt inner hugs the body wall with a slight interference (captured
        # friction fit, allowed via allow_overlap) so the lid actually contacts.
        skirt_inner = (r.body_dim - (_RABBET_INSET if inset else 0.0)) - 0.0006
        skirt = (
            cq.Workplane("XY")
            .center(0.0, fwd)
            .circle(lid_r)
            .circle(skirt_inner)
            .extrude(skirt_h)
        )
        top = (
            cq.Workplane("XY")
            .workplane(offset=skirt_h)
            .center(0.0, fwd)
            .circle(lid_r)
            .extrude(r.lid_h)
        )
        return skirt.union(top)

    if r.kind == "flask":
        hx = r.body_dim + 0.0015
        hy = r.depth_dim + 0.0015
        fillet = min(0.010, r.depth_dim * 0.35)
        skirt_in_y = r.depth_dim - 0.0006
        skirt_in_x = r.body_dim - 0.0006
        skirt_outer = _rounded_rect_prism(hx, hy, fillet, 0.0, skirt_h)
        skirt_inner = _rounded_rect_prism(
            skirt_in_x, skirt_in_y, max(fillet - r.wall, 0.002), -0.001, skirt_h + 0.001
        )
        skirt = skirt_outer.cut(skirt_inner)
        top = _rounded_rect_prism(hx, hy, fillet, skirt_h, skirt_h + r.lid_h)
        return skirt.union(top).translate((0.0, fwd, 0.0))

    if r.kind == "square":
        fillet = min(0.012, outer * 0.2)
        # press-fit grips the inset rim shoulder (body_dim - sliver); lift-off
        # grips the full outer wall. Slight interference so it actually contacts.
        rim_half = r.body_dim - (min(_RABBET_INSET, r.wall * 0.6) if inset else 0.0)
        skirt_inner_half = rim_half - 0.0006
        skirt_outer = _rounded_square_prism(outer, fillet, 0.0, skirt_h)
        skirt_inner = _rounded_square_prism(
            skirt_inner_half, max(fillet - r.wall, 0.002), -0.001, skirt_h + 0.001
        )
        skirt = skirt_outer.cut(skirt_inner)
        top = _rounded_square_prism(outer, fillet, skirt_h, skirt_h + r.lid_h)
        return skirt.union(top).translate((0.0, fwd, 0.0))

    # hex
    lid_circum = outer
    inner_circum = r.body_dim - 0.0006
    skirt_outer = (
        cq.Workplane("XY").center(0.0, fwd).polygon(6, _hex_diam(lid_circum)).extrude(skirt_h)
    )
    skirt_inner = (
        cq.Workplane("XY")
        .workplane(offset=-0.001)
        .center(0.0, fwd)
        .polygon(6, _hex_diam(inner_circum))
        .extrude(skirt_h + 0.002)
    )
    skirt = skirt_outer.cut(skirt_inner)
    top = (
        cq.Workplane("XY")
        .workplane(offset=skirt_h)
        .center(0.0, fwd)
        .polygon(6, _hex_diam(lid_circum))
        .extrude(r.lid_h)
    )
    return skirt.union(top)


def _build_lift_lid(model, body, r: ResolvedContainerCanConfig, *, lid_mat, accent_mat, inset: bool) -> None:
    """PRISMATIC +Z lift-off / press-fit lid. The joint origin is anchored on the
    back rim wall (real body material, ``y = hinge_back``) at the seam plane, not
    on the hollow centerline; the lid mesh is authored centered at local
    ``y = -hinge_back`` so it caps the can after the off-axis origin re-centers it,
    and the back skirt wall passes through the child-local origin. Positive travel
    lifts the lid straight up (axis +Z, world xy unchanged)."""
    skirt_h = _SKIRT_H * r.lid_height_scale
    travel = _LID_LIFT * r.joint_travel_scale
    seam_z = r.rim_top_z - _SKIRT_OVERLAP
    fwd = -r.hinge_back  # forward offset so the lid re-centers on the can axis

    lid = model.part("lid")
    lid.visual(
        mesh_from_cadquery(_lift_lid_solid(r, inset=inset, fwd=fwd), "lid_shell"),
        material=lid_mat,
        name="lid_shell", material_class_id=("metal.aluminum_bare" if r.palette_style in {"brushed_steel", "brushed_pewter", "brass_lid_accent", "dark_bronze_cap", "painted_tin", "glossy_print", "anodized_gold", "anodized_blue", "hammered_tin"} else "plastic.clear_rigid"),
    )
    # Top seam ring marker (folds a decorative accent band into the lid).
    lid.visual(
        Box((0.006, 0.006, 0.0015)),
        origin=Origin(xyz=(r.lid_outer_dim - 0.008, fwd, skirt_h + r.lid_h - 0.0005)),
        material=accent_mat,
        name="lid_seam", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_steel", "brushed_pewter", "brass_lid_accent", "dark_bronze_cap", "painted_tin", "glossy_print", "anodized_gold", "anodized_blue", "hammered_tin"} else "plastic.opaque_generic"),
    )
    lid.inertial = Inertial.from_geometry(
        Box((2 * r.lid_outer_dim, 2 * r.lid_outer_dim, skirt_h + r.lid_h)),
        mass=0.04,
        origin=Origin(xyz=(0.0, fwd, (skirt_h + r.lid_h) / 2.0)),
    )
    model.articulation(
        "body_to_lid",
        ArticulationType.PRISMATIC,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, r.hinge_back, seam_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=travel, effort=10.0, velocity=0.2),
    )


def _cap_knob(r: ResolvedContainerCanConfig) -> KnobGeometry:
    """Knurled screw cap via KnobGeometry with a BLIND bore for the neck
    (round_screwcap ``_cap_knob``). The bore stops short of the top so the cap
    keeps a solid crown plate; the crown's center carries the spin axis. Mounting
    face at z=0 (center=False), so the cap is translated by -crown so its solid
    crown center coincides with the cap-local origin (the continuous-spin axis)."""
    cap_h = _CAP_H * r.lid_height_scale
    crown_t = 0.005  # solid crown thickness above the blind bore
    return KnobGeometry(
        r.cap_od,
        cap_h,
        body_style="cylindrical",
        grip=KnobGrip(style="knurled", count=36, depth=0.0009, helix_angle_deg=25.0),
        bore=KnobBore(style="round", diameter=r.cap_bore_d, through=False, flat_depth=cap_h - crown_t),
        center=False,
    )


def _build_screw_cap(model, body, r: ResolvedContainerCanConfig, *, lid_mat, accent_mat) -> None:
    """CONTINUOUS spin + PRISMATIC lift through a MASSLESS ``cap_carrier`` link
    (fuel-flask 6e35123f CONT->PRIS ordering, equally legal per spec). The
    carrier has no visual (truly massless) so it decouples spin from lift; the
    knurled KnobGeometry cap carries the mesh. Both screw joints touch the
    no-visual carrier, so they are grandfathered out of the origin/mating checks;
    the cap self-anchors (closed crown at the spin axis) and seats over the round
    threaded neck. The off-axis marker makes the spin observable."""
    cap_h = _CAP_H * r.lid_height_scale
    lift = _CAP_LIFT * r.joint_travel_scale

    # carrier: massless, NO visual — decouples rotate (CONTINUOUS) from lift
    # (PRISMATIC). Origin frames sit on the neck axis (the body neck is the real
    # geometry the cap mates to).
    carrier = model.part("cap_carrier")
    carrier.inertial = Inertial.from_geometry(Box((0.008, 0.008, 0.008)), mass=1e-4)

    # cap: knurled screw cap. KnobGeometry mounting face at z=0 (skirt opening
    # down so its blind bore sleeves the neck); the solid crown is at z=cap_h.
    cap = model.part("cap")
    cap.visual(mesh_from_geometry(_cap_knob(r), "cap_shell"), material=lid_mat, name="cap_shell", material_class_id=("metal.aluminum_bare" if r.palette_style in {"brushed_steel", "brushed_pewter", "brass_lid_accent", "dark_bronze_cap", "painted_tin", "glossy_print", "anodized_gold", "anodized_blue", "hammered_tin"} else "plastic.clear_rigid"))
    # Off-axis marker on the crown so spin about +Z is observable.
    cap.visual(
        Box((0.004, 0.004, 0.004)),
        origin=Origin(xyz=(r.cap_od / 2.0 - 0.004, 0.0, cap_h - 0.002)),
        material=accent_mat,
        name="cap_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    cap.inertial = Inertial.from_geometry(
        Cylinder(r.cap_od / 2.0, cap_h),
        mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, cap_h / 2.0)),
    )

    # body --CONT--> carrier --PRIS--> cap. CONT origin on the neck top axis; the
    # cap's mounting face (z=0) seats at the neck top, the bore sleeving the neck.
    seat_z = r.neck_top_z - 0.012  # cap mounting face sits just below neck top
    model.articulation(
        "cap_rotate",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=carrier,
        origin=Origin(xyz=(0.0, 0.0, seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=6.0),
    )
    model.articulation(
        "cap_slide",
        ArticulationType.PRISMATIC,
        parent=carrier,
        child=cap,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=lift, effort=5.0, velocity=0.1),
    )


def _hinge_lid_solid(r: ResolvedContainerCanConfig) -> cq.Workplane:
    """Hinge flip lid authored in the hinge frame: origin at the hinge line, the
    disc/cap extends +Y so it caps the mouth when closed (round_hingelid
    ``_lid_cap``). Section follows the body section."""
    skirt_h = _SKIRT_H * r.lid_height_scale
    # forward offset so the lid centers over the mouth (hinge at the back rim).
    fwd = -r.hinge_back

    if r.kind in ("round", "tub"):
        lid_r = r.body_dim + 0.0015
        skirt_inner = r.body_dim - 0.0006
        top = (
            cq.Workplane("XY")
            .center(0.0, fwd)
            .circle(lid_r)
            .extrude(r.lid_h)
        )
        skirt = (
            cq.Workplane("XY")
            .workplane(offset=-skirt_h)
            .center(0.0, fwd)
            .circle(lid_r)
            .circle(skirt_inner)
            .extrude(skirt_h)
        )
        return top.union(skirt)

    if r.kind == "flask":
        hx = r.body_dim + 0.0015
        hy = r.depth_dim + 0.0015
        fillet = min(0.010, r.depth_dim * 0.35)
        top = _rounded_rect_prism(hx, hy, fillet, 0.0, r.lid_h).translate((0.0, fwd, 0.0))
        skirt_outer = _rounded_rect_prism(hx, hy, fillet, -skirt_h, 0.0).translate((0.0, fwd, 0.0))
        skirt_inner = _rounded_rect_prism(
            r.body_dim - 0.0006, r.depth_dim - 0.0006,
            max(fillet - r.wall, 0.002), -skirt_h - 0.001, 0.001,
        ).translate((0.0, fwd, 0.0))
        skirt = skirt_outer.cut(skirt_inner)
        return top.union(skirt)

    if r.kind == "square":
        outer = r.lid_outer_dim
        fillet = min(0.012, outer * 0.2)
        top = _rounded_square_prism(outer, fillet, 0.0, r.lid_h).translate((0.0, fwd, 0.0))
        skirt_outer = _rounded_square_prism(outer, fillet, -skirt_h, 0.0).translate((0.0, fwd, 0.0))
        skirt_inner = _rounded_square_prism(
            r.body_dim - 0.0016, max(fillet - r.wall, 0.002), -skirt_h - 0.001, 0.001
        ).translate((0.0, fwd, 0.0))
        skirt = skirt_outer.cut(skirt_inner)
        return top.union(skirt)

    # hex
    lid_circum = r.lid_outer_dim
    inner_circum = r.body_dim - 0.0006
    top = (
        cq.Workplane("XY")
        .center(0.0, fwd)
        .polygon(6, _hex_diam(lid_circum))
        .extrude(r.lid_h)
    )
    skirt_outer = (
        cq.Workplane("XY")
        .workplane(offset=-skirt_h)
        .center(0.0, fwd)
        .polygon(6, _hex_diam(lid_circum))
        .extrude(skirt_h)
    )
    skirt_inner = (
        cq.Workplane("XY")
        .workplane(offset=-skirt_h - 0.001)
        .center(0.0, fwd)
        .polygon(6, _hex_diam(inner_circum))
        .extrude(skirt_h + 0.002)
    )
    skirt = skirt_outer.cut(skirt_inner)
    return top.union(skirt)


def _lid_knuckle_solid(r: ResolvedContainerCanConfig) -> cq.Workplane:
    """Hinge knuckle on the lid: a horizontal cylinder along +X at the lid local
    origin (on the hinge axis hardware) (round_hingelid ``_lid_knuckle``)."""
    knuckle_len = 0.016
    return (
        cq.Workplane("YZ")
        .circle(0.003)
        .extrude(knuckle_len)
        .translate((-knuckle_len / 2.0, 0.0, 0.0))
    )


def _build_hinge_lid(model, body, r: ResolvedContainerCanConfig, *, lid_mat, accent_mat) -> None:
    """REVOLUTE +X flip lid hinged at the back rim. q=0 caps the mouth; positive q
    swings the front edge up and back. Open limit is conditional on body shape."""
    fwd = -r.hinge_back

    lid = model.part("lid")
    lid.visual(mesh_from_cadquery(_hinge_lid_solid(r), "lid_shell"), material=lid_mat, name="lid_shell", material_class_id=("metal.aluminum_bare" if r.palette_style in {"brushed_steel", "brushed_pewter", "brass_lid_accent", "dark_bronze_cap", "painted_tin", "glossy_print", "anodized_gold", "anodized_blue", "hammered_tin"} else "plastic.clear_rigid"))
    lid.visual(
        mesh_from_cadquery(_lid_knuckle_solid(r), "hinge_knuckle"),
        material=accent_mat,
        name="hinge_knuckle", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_steel", "brushed_pewter", "brass_lid_accent", "dark_bronze_cap", "painted_tin", "glossy_print", "anodized_gold", "anodized_blue", "hammered_tin"} else "plastic.opaque_generic"),
    )
    lid.inertial = Inertial.from_geometry(
        Cylinder(r.lid_outer_dim, r.lid_h + _SKIRT_H),
        mass=0.03,
        origin=Origin(xyz=(0.0, fwd, 0.0)),
    )
    model.articulation(
        "body_to_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, r.hinge_back, r.rim_top_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            lower=0.0, upper=r.hinge_open_upper, effort=5.0, velocity=2.0
        ),
    )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_can(
    config: ContainerCanConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    body_mat = model.material(f"cc_body_{r.palette_style}", rgba=pal["body"])
    lid_mat = model.material(f"cc_lid_{r.palette_style}", rgba=pal["lid"])
    accent_mat = model.material(f"cc_accent_{r.palette_style}", rgba=pal["accent"])

    # --- ROOT: can body ------------------------------------------------------
    body = model.part("body")
    _emit_body(body, r, body_mat=body_mat)

    # --- closure mechanism ---------------------------------------------------
    if r.closure == "lift_off_lid":
        _build_lift_lid(model, body, r, lid_mat=lid_mat, accent_mat=accent_mat, inset=False)
    elif r.closure == "press_fit_skirt_lid":
        _build_lift_lid(model, body, r, lid_mat=lid_mat, accent_mat=accent_mat, inset=True)
    elif r.closure == "screw_cap":
        _build_screw_cap(model, body, r, lid_mat=lid_mat, accent_mat=accent_mat)
    elif r.closure == "hinge_lid":
        _build_hinge_lid(model, body, r, lid_mat=lid_mat, accent_mat=accent_mat)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_can(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_can(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (lid skirt over the rim, cap shell over the
# neck, hinge knuckle over the ear) are declared element-scoped; the closure
# mechanism actions are exercised. Mating contracts are grandfathered (captured
# friction/screw/hinge fits) per spec; the baseline guards joint origins.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_can_tests(
    object_model: ArticulatedObject,
    config: ContainerCanConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("body")

    # ---- can body rests on the ground (base near z=0) and has real volume ----
    aabb = ctx.part_world_aabb(body)
    bext = _ext(aabb)
    ctx.check(
        "can body rests on the ground (base near z=0)",
        abs(aabb[0][2]) < 0.012,
        details=f"body min z={aabb[0][2]:.4f}",
    )
    ctx.check(
        "can body has real volume",
        bext[0] > 0.02 and bext[1] > 0.02 and bext[2] > 0.02,
        details=f"body extents={bext}",
    )

    # ---- closure: mechanism actions + captured-fit overlaps ----
    if r.closure in ("lift_off_lid", "press_fit_skirt_lid"):
        lid = object_model.get_part("lid")
        lift = object_model.get_articulation("body_to_lid")
        ctx.allow_isolated_part(
            lid,
            reason="lid lifts off the can and loses body contact when opened",
        )
        ctx.allow_overlap(
            lid, body, elem_a="lid_shell", elem_b="body_shell",
            reason="The lid skirt intentionally sleeves down over the body rim (captured friction fit).",
        )
        ctx.check(
            "body_to_lid is PRISMATIC about +Z",
            lift.articulation_type == ArticulationType.PRISMATIC and abs(lift.axis[2]) > 0.99,
            details=f"axis={lift.axis}, type={lift.articulation_type}",
        )
        rest_z = ctx.part_world_position(lid)[2]
        rest_xy = ctx.part_world_position(lid)[:2]
        travel = _LID_LIFT * r.joint_travel_scale
        with ctx.pose({lift: travel}):
            up = ctx.part_world_position(lid)
        ctx.check(
            "lid lifts straight up off the can",
            up[2] > rest_z + travel * 0.5
            and abs(up[0] - rest_xy[0]) < 1e-6
            and abs(up[1] - rest_xy[1]) < 1e-6,
            details=f"rest_z={rest_z:.4f}, lifted_z={up[2]:.4f}",
        )

    elif r.closure == "screw_cap":
        carrier = object_model.get_part("cap_carrier")
        cap = object_model.get_part("cap")
        rotate = object_model.get_articulation("cap_rotate")
        slide = object_model.get_articulation("cap_slide")
        ctx.allow_overlap(
            cap, body, elem_a="cap_shell", elem_b="body_shell",
            reason="The screw cap bore is intentionally seated over the threaded neck.",
        )
        ctx.check(
            "carrier link is massless (no visuals)",
            len(carrier.visuals) == 0,
            details=f"carrier visuals={len(carrier.visuals)}",
        )
        ctx.check(
            "cap_slide is PRISMATIC about +Z",
            slide.articulation_type == ArticulationType.PRISMATIC and abs(slide.axis[2]) > 0.99,
            details=f"axis={slide.axis}, type={slide.articulation_type}",
        )
        ctx.check(
            "cap_rotate is CONTINUOUS about +Z",
            rotate.articulation_type == ArticulationType.CONTINUOUS and abs(rotate.axis[2]) > 0.99,
            details=f"axis={rotate.axis}, type={rotate.articulation_type}",
        )
        # cap_rotate spins the cap: off-axis marker moves around the axis.
        m0 = ctx.part_element_world_aabb(cap, elem="cap_marker")
        m0c = ((m0[0][0] + m0[1][0]) / 2.0, (m0[0][1] + m0[1][1]) / 2.0)
        with ctx.pose({rotate: math.pi / 2.0}):
            m1 = ctx.part_element_world_aabb(cap, elem="cap_marker")
            m1c = ((m1[0][0] + m1[1][0]) / 2.0, (m1[0][1] + m1[1][1]) / 2.0)
        ctx.check(
            "cap marker sweeps around the neck axis when spun",
            math.hypot(m1c[0] - m0c[0], m1c[1] - m0c[1]) > 0.005,
            details=f"marker rest={m0c}, quarter-turn={m1c}",
        )
        # cap_slide lifts the cap assembly off the neck.
        rest_z = ctx.part_world_position(cap)[2]
        travel = _CAP_LIFT * r.joint_travel_scale
        with ctx.pose({slide: travel}):
            up_z = ctx.part_world_position(cap)[2]
        ctx.check(
            "cap slides straight up off the neck",
            up_z > rest_z + travel * 0.5,
            details=f"rest_z={rest_z:.4f}, lifted_z={up_z:.4f}",
        )

    elif r.closure == "hinge_lid":
        lid = object_model.get_part("lid")
        hinge = object_model.get_articulation("body_to_lid")
        ctx.allow_overlap(
            lid, body, elem_a="lid_shell", elem_b="body_shell",
            reason="The flip lid skirt sleeves over the body rim when closed (seam ring).",
        )
        ctx.allow_overlap(
            lid, body, elem_a="hinge_knuckle", elem_b="body_shell",
            reason="The hinge knuckle wraps the body hinge ear at the back rim (captured pin fit).",
        )
        ctx.check(
            "body_to_lid is REVOLUTE about +X",
            hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[0]) > 0.99,
            details=f"axis={hinge.axis}, type={hinge.articulation_type}",
        )
        ctx.check(
            "hinge origin sits at the back rim",
            hinge.origin is not None and hinge.origin.xyz[1] < -r.inradius * 0.5,
            details=f"hinge origin y={hinge.origin.xyz[1] if hinge.origin else None}",
        )
        # Flip the lid up: the top rises.
        top0 = ctx.part_world_aabb(lid)[1][2]
        with ctx.pose({hinge: min(1.4, r.hinge_open_upper * 0.6)}):
            top1 = ctx.part_world_aabb(lid)[1][2]
        ctx.check(
            "hinge flips the lid up (top rises)",
            top1 > top0 + 0.005,
            details=f"closed_top_z={top0:.4f}, open_top_z={top1:.4f}",
        )

    # ---- at least one non-fixed joint exists ----
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
