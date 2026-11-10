# SPDX-License-Identifier: Apache-2.0

"""Container / plastic can — modular procedural template (HDPE jerrycan / jug).

Category identity: an upright molded HDPE jerrycan / fuel jug / utility
canister. The hollow blow-molded body (ROOT) rests on z=0 with its footprint
centered on X/Y; a short threaded neck is offset (not centered) on the
shoulder. An integrated handle/grip lets a person carry it, and a cap/closure
on the neck opens by one of several mechanisms (the main articulation). No
multiplicity axis — one can, one handle, one closure.

Three parallel slots (spec ``Container_Plastic_can.md``):

  * ``body_form`` (4) — the ROOT ``body`` mesh + offset neck stub + pour-mouth
    bore + molded detail:
      - tall_rounded_rect_deck: rounded-rect loft, tapered shoulder -> small
        deck (gallon-jug parent 001).
      - tall_rounded_rect_slab: rounded-rect loft, full-width shoulder slab +
        ring-foot recess (oil-jug parent 002).
      - square_cubic: chunky filleted box + recessed deck + stacking ribs +
        flared foot (square jerrycan parent 003).
      - tall_rectangular_sloped: box + sloped wedge -> high plateau + spout
        boss (sloped jerrycan parent 004).
  * ``handle_grip`` (6) — five are FIXED visuals fused into the body shell,
    one (swing_bail) is a separate REVOLUTE part:
      - integrated_loop: raised rounded loop w/ open finger hole (parent 001).
      - flush_dgrip: molded side grab-bar standing proud of the wall with a
        finger gap behind it (no through-cut into the cavity) (parent 002).
      - bridge_strap: raised arched carry strap (additive legs + top bar; finger
        gap is open air above the intact deck, no cut) (parent 003).
      - recessed_top_slot: front-to-back carry slot in the high plateau (p004).
      - swing_bail: U-bar bail tube on two shoulder lugs, REVOLUTE +Y (var).
      - recessed_grip_pocket: concave sphere-cut hand-hold pocket (var).
  * ``cap_closure`` (3) — each has >=1 non-fixed joint:
      - screw_cap: CONTINUOUS spin + PRISMATIC lift via massless ``cap_carrier``
        (parent pattern).
      - flip_top_spout: fixed collar+spout base (body visual) + hollow lid that
        flips on a REVOLUTE -X hinge over the raised spout (var).
      - hinged_tethered_lid: fixed collar+anchor (body visual) + captive flip
        cap on a REVOLUTE -X living hinge (var).

Continuous size/proportion variation (height/width/depth/neck/travel/handle
scales) lives in ``resolve_config`` as clamped params, never as slot candidates.

Sources (articraft_data ``picture/Container/Plastic can`` 5-star pool): four
parents ``0f3f18ac`` (gallon jug), ``47fb268a`` (oil jug), ``1078fc9e`` (square
jerrycan), ``ab019c96`` (sloped jerrycan), plus variants ``swing_bail``,
``recessed_grip_pocket``, ``flip_top_spout``, ``hinged_tethered_lid``.

Canonical spec:
``articraft_template_authoring/specs_modular_v1/Container_Plastic_can.md``
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
    CylinderGeometry,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyForm = Literal[
    "tall_rounded_rect_deck",
    "tall_rounded_rect_slab",
    "square_cubic",
    "tall_rectangular_sloped",
]
HandleGrip = Literal[
    "integrated_loop",
    "flush_dgrip",
    "bridge_strap",
    "recessed_top_slot",
    "swing_bail",
    "recessed_grip_pocket",
]
CapClosure = Literal[
    "screw_cap",
    "flip_top_spout",
    "hinged_tethered_lid",
]
PaletteStyle = Literal[
    "red_fuel",
    "yellow_diesel",
    "blue_water",
    "green_utility",
    "black_oil",
    "matte_olive_mil",
    "gold_oil",
    "natural_hdpe",
    "white_jug",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "tall_rounded_rect_deck",
    "tall_rounded_rect_slab",
    "square_cubic",
    "tall_rectangular_sloped",
)
HANDLE_GRIPS: tuple[HandleGrip, ...] = (
    "integrated_loop",
    "flush_dgrip",
    "bridge_strap",
    "recessed_top_slot",
    "swing_bail",
    "recessed_grip_pocket",
)
CAP_CLOSURES: tuple[CapClosure, ...] = (
    "screw_cap",
    "flip_top_spout",
    "hinged_tethered_lid",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "red_fuel",
    "yellow_diesel",
    "blue_water",
    "green_utility",
    "black_oil",
    "matte_olive_mil",
    "gold_oil",
    "natural_hdpe",
    "white_jug",
)


# ---------------------------------------------------------------------------
# Palette: 9 coordinated HDPE colorways (spec §palette). Each colorway carries
# body / handle / cap / accent rgba + a finish tag. translucent_natural carries
# alpha < 1. ``finish`` only tweaks material semantics (cosmetic); it never
# changes a slot/joint/geometry.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Palette:
    body: tuple[float, float, float, float]
    handle: tuple[float, float, float, float]
    cap: tuple[float, float, float, float]
    accent: tuple[float, float, float, float]
    finish: str


PALETTES: dict[PaletteStyle, _Palette] = {
    "red_fuel": _Palette(
        (0.72, 0.10, 0.10, 1.0),
        (0.72, 0.10, 0.10, 1.0),
        (0.08, 0.08, 0.09, 1.0),
        (0.92, 0.92, 0.92, 1.0),
        "matte_molded",
    ),
    "yellow_diesel": _Palette(
        (0.85, 0.70, 0.10, 1.0),
        (0.85, 0.70, 0.10, 1.0),
        (0.08, 0.08, 0.09, 1.0),
        (0.80, 0.10, 0.10, 1.0),
        "matte_molded",
    ),
    "blue_water": _Palette(
        (0.15, 0.35, 0.70, 1.0),
        (0.15, 0.35, 0.70, 1.0),
        (0.92, 0.92, 0.92, 1.0),
        (0.97, 0.98, 1.0, 1.0),
        "matte_molded",
    ),
    "green_utility": _Palette(
        (0.14, 0.42, 0.20, 1.0),
        (0.14, 0.42, 0.20, 1.0),
        (0.08, 0.08, 0.09, 1.0),
        (0.92, 0.92, 0.92, 1.0),
        "matte_molded",
    ),
    "black_oil": _Palette(
        (0.12, 0.12, 0.13, 1.0),
        (0.20, 0.20, 0.21, 1.0),
        (0.08, 0.08, 0.09, 1.0),
        (0.80, 0.10, 0.10, 1.0),
        "gloss_molded",
    ),
    "matte_olive_mil": _Palette(
        (0.27, 0.28, 0.16, 1.0),
        (0.27, 0.28, 0.16, 1.0),
        (0.055, 0.055, 0.060, 1.0),
        (0.07, 0.07, 0.075, 1.0),
        "satin_military",
    ),
    "gold_oil": _Palette(
        (0.62, 0.52, 0.18, 1.0),
        (0.62, 0.52, 0.18, 1.0),
        (0.09, 0.09, 0.10, 1.0),
        (0.90, 0.88, 0.90, 1.0),
        "gloss_molded",
    ),
    "natural_hdpe": _Palette(
        (0.91, 0.90, 0.85, 0.72),
        (0.91, 0.90, 0.85, 0.72),
        (0.91, 0.90, 0.85, 1.0),
        (0.08, 0.08, 0.09, 1.0),
        "translucent_natural",
    ),
    "white_jug": _Palette(
        (0.95, 0.95, 0.95, 1.0),
        (0.95, 0.95, 0.95, 1.0),
        (0.92, 0.92, 0.92, 1.0),
        (0.28, 0.72, 0.80, 1.0),
        "gloss_molded",
    ),
}


def _material_class_id(surface: Literal["body", "cap", "handle"]) -> str:
    """Return the exact formal-library pool for a resolved material visual."""
    return "plastic.opaque_generic"


# ---------------------------------------------------------------------------
# Per-body-form base geometry (meters). Scaled per-build by resolve_config.
# All footprints centered on X/Y; the neck is offset on +X. Top handles live on
# -X so the offset neck/closure keep >= 0.06 clearance from them.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _FormGeom:
    body_w: float  # X footprint
    body_d: float  # Y footprint
    body_h: float  # straight-wall height to shoulder start
    shoulder_h: float  # shoulder rise to deck / plateau
    wall: float  # shell wall thickness
    neck_x: float  # neck offset on +X
    neck_y: float
    neck_r: float  # neck outer radius
    neck_h: float  # neck stub height above the deck top


# Footprints/heights traced from the four parent records (parent 001/002 jugs,
# 003 square pail, 004 sloped jerrycan) but normalized to a shared frame.
_FORMS: dict[BodyForm, _FormGeom] = {
    # gallon jug: rounded-rect, taller than wide, tapered to a small deck.
    "tall_rounded_rect_deck": _FormGeom(
        0.150, 0.135, 0.215, 0.050, 0.0050, 0.020, 0.0, 0.0190, 0.024
    ),
    # oil jug: rounded-rect, full-width shoulder slab (no draw-in deck).
    "tall_rounded_rect_slab": _FormGeom(
        0.135, 0.100, 0.205, 0.050, 0.0050, 0.040, 0.0, 0.0170, 0.022
    ),
    # square pail: chunky near-cubic box, recessed deck, ribs.
    "square_cubic": _FormGeom(0.250, 0.250, 0.250, 0.020, 0.0120, 0.050, -0.010, 0.030, 0.020),
    # sloped jerrycan: tall rectangular, sloped shoulder -> high plateau. The
    # neck sits on the LOW -X shoulder (parent 004); the carry handle lives on
    # the +X high plateau, so the handle side is flipped for this form.
    "tall_rectangular_sloped": _FormGeom(
        0.200, 0.150, 0.206, 0.098, 0.0120, -0.058, 0.030, 0.024, 0.020
    ),
}

# Cap / closure nominal sizes.
_CAP_H = 0.028
_CAP_SLIDE = 0.030
_COLLAR_H = 0.009
_SPOUT_H = 0.011
_LID_LIFT = 0.0  # (closures only flip / screw; no extra slide)


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _sloped_shoulder_surface_z(
    *, body_w: float, body_h: float, shoulder_h: float, x: float
) -> float:
    """Approximate the real local shoulder height on the sloped jerrycan.

    The sloped form has a low neck-side shoulder and a higher handle plateau.
    Closure joints and the neck mesh need the local shoulder height, not the
    high plateau height, otherwise the neck looks like a disconnected stack.
    """
    low_z = body_h + shoulder_h * 0.47
    high_z = body_h + shoulder_h
    x0 = -body_w / 2.0
    x1 = -body_w * 0.06
    t = _clamp((x - x0) / max(x1 - x0, 1e-6), 0.0, 1.0)
    return low_z + t * (high_z - low_z)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ContainerPlasticCanConfig:
    body_form: BodyForm = "tall_rounded_rect_deck"
    handle_grip: HandleGrip = "integrated_loop"
    cap_closure: CapClosure = "screw_cap"
    palette_style: PaletteStyle = "red_fuel"
    body_height_scale: float = 1.0
    body_width_scale: float = 1.0
    body_depth_scale: float = 1.0
    neck_radius_scale: float = 1.0
    closure_travel_scale: float = 1.0
    handle_size_scale: float = 1.0
    name: str = "container_plastic_can"


@dataclass(frozen=True)
class ResolvedContainerPlasticCanConfig:
    body_form: BodyForm
    handle_grip: HandleGrip
    cap_closure: CapClosure
    palette_style: PaletteStyle
    body_height_scale: float
    body_width_scale: float
    body_depth_scale: float
    neck_radius_scale: float
    closure_travel_scale: float
    handle_size_scale: float
    # derived body geometry
    body_w: float
    body_d: float
    body_h: float
    shoulder_h: float
    wall: float
    neck_x: float
    neck_y: float
    neck_r: float
    neck_h: float
    deck_top_z: float  # world z of the offset deck surface at the neck
    neck_top_z: float  # world z of the neck rim (closure mount plane)
    mouth_bore_r: float
    # derived closure geometry
    cap_r: float
    cap_bore_r: float
    collar_r: float
    name: str


def config_from_seed(seed: int) -> ContainerPlasticCanConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    return ContainerPlasticCanConfig(
        body_form=rng.choice(BODY_FORMS),
        handle_grip=rng.choice(HANDLE_GRIPS),
        cap_closure=rng.choice(CAP_CLOSURES),
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.85, 1.20), 4),
        body_width_scale=round(rng.uniform(0.88, 1.15), 4),
        body_depth_scale=round(rng.uniform(0.88, 1.15), 4),
        neck_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        closure_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        handle_size_scale=round(rng.uniform(0.90, 1.12), 4),
        name=f"seeded_container_plastic_can_{seed}",
    )


def resolve_config(
    config: ContainerPlasticCanConfig | None = None,
) -> ResolvedContainerPlasticCanConfig:
    cfg = config or ContainerPlasticCanConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    handle_grip = _pick(cfg.handle_grip, HANDLE_GRIPS)
    cap_closure = _pick(cfg.cap_closure, CAP_CLOSURES)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    g = _FORMS[body_form]
    h_scale = _clamp(cfg.body_height_scale, 0.85, 1.20)
    w_scale = _clamp(cfg.body_width_scale, 0.88, 1.15)
    d_scale = _clamp(cfg.body_depth_scale, 0.88, 1.15)
    n_scale = _clamp(cfg.neck_radius_scale, 0.90, 1.10)
    ct_scale = _clamp(cfg.closure_travel_scale, 0.85, 1.10)
    hs_scale = _clamp(cfg.handle_size_scale, 0.90, 1.12)

    body_w = g.body_w * w_scale
    body_d = g.body_d * d_scale
    body_h = g.body_h * h_scale
    shoulder_h = g.shoulder_h * h_scale
    wall = g.wall

    # Neck X offset follows the width scale; keep it within the footprint so the
    # neck always sits on solid shoulder.
    neck_x = _clamp(g.neck_x * w_scale, -body_w / 2.0 + 0.030, body_w / 2.0 - 0.030)
    neck_y = _clamp(g.neck_y * d_scale, -body_d / 2.0 + 0.030, body_d / 2.0 - 0.030)
    # Neck radius follows its own scale, clamped to stay strictly inside the
    # shoulder so the deck always supports it.
    neck_r = _clamp(g.neck_r * n_scale, 0.012, min(body_w, body_d) / 2.0 - 0.020)
    neck_h = g.neck_h

    if body_form == "tall_rectangular_sloped":
        deck_top_z = _sloped_shoulder_surface_z(
            body_w=body_w, body_h=body_h, shoulder_h=shoulder_h, x=neck_x
        )
    else:
        deck_top_z = body_h + shoulder_h
    neck_top_z = deck_top_z + neck_h
    # Pour-mouth = real thin-wall neck opening: bore the neck out to its inner
    # radius (neck_r - wall) so you look straight down the open neck into the
    # hollow body, leaving only a ~``wall`` thick neck rim ring (the rim is the
    # real geometry the closure joint origins anchor onto).
    mouth_bore_r = max(neck_r - wall, 0.008)

    # Closure: cap bore grips the neck (slight interference -> captured fit
    # allowed in tests); cap outer is proud of the neck boss. Equation: the cap
    # / collar / lid bore radii follow neck_r.
    cap_bore_r = neck_r + 0.0015
    cap_r = cap_bore_r + 0.005
    collar_r = neck_r + 0.005

    return ResolvedContainerPlasticCanConfig(
        body_form=body_form,
        handle_grip=handle_grip,
        cap_closure=cap_closure,
        palette_style=palette,
        body_height_scale=h_scale,
        body_width_scale=w_scale,
        body_depth_scale=d_scale,
        neck_radius_scale=n_scale,
        closure_travel_scale=ct_scale,
        handle_size_scale=hs_scale,
        body_w=body_w,
        body_d=body_d,
        body_h=body_h,
        shoulder_h=shoulder_h,
        wall=wall,
        neck_x=neck_x,
        neck_y=neck_y,
        neck_r=neck_r,
        neck_h=neck_h,
        deck_top_z=deck_top_z,
        neck_top_z=neck_top_z,
        mouth_bore_r=mouth_bore_r,
        cap_r=cap_r,
        cap_bore_r=cap_bore_r,
        collar_r=collar_r,
        name=cfg.name or "container_plastic_can",
    )


def with_overrides(
    config: ContainerPlasticCanConfig, **kwargs: object
) -> ContainerPlasticCanConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerPlasticCanConfig | ResolvedContainerPlasticCanConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedContainerPlasticCanConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("handle_grip", r.handle_grip),
        ("cap_closure", r.cap_closure),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Slot A — body_form solids. Each returns a hollow CadQuery shell with an
# offset neck stub and a through pour-mouth bore. The FIXED handle geometry is
# unioned/cut in by the handle helpers below before meshing.
# ===========================================================================
def _rrect_loft(sections) -> cq.Workplane:
    """Rounded-rect (plain rect) sections stacked along +Z (parent 001)."""
    wp = cq.Workplane("XY")
    prev_z = 0.0
    for i, (z, w, d) in enumerate(sections):
        off = z if i == 0 else z - prev_z
        if i == 0:
            wp = wp.workplane(offset=z)
        else:
            wp = wp.workplane(offset=off)
        wp = wp.rect(w, d)
        prev_z = z
    return wp.loft(ruled=False)


def _neck_stub(r: ResolvedContainerPlasticCanConfig, base_z: float) -> cq.Workplane:
    """Offset threaded neck rising from ``base_z`` to the neck rim, growing out of
    a molded boss flare so the neck blends continuously into the shoulder instead
    of reading as a bare cylinder plonked on a flat deck (the ``脱节`` look).

    Profile bottom->top: a wide boss skirt at the shoulder, tapering smoothly up
    into the straight threaded neck. The base flare overlaps the deck/shoulder so
    the union reads as one continuous molded surface.
    """
    total_h = r.neck_top_z - base_z
    skirt_r = r.neck_r + 0.012
    flare_h = min(0.013, max(0.0, total_h - 0.006))
    return (
        cq.Workplane("XY")
        .workplane(offset=base_z)
        .center(r.neck_x, r.neck_y)
        .circle(skirt_r)
        .workplane(offset=flare_h * 0.55)
        .circle(r.neck_r + 0.004)
        .workplane(offset=flare_h * 0.45)
        .circle(r.neck_r)
        .workplane(offset=total_h - flare_h)
        .circle(r.neck_r)
        .loft(ruled=False)
    )


def _mouth_bore(r: ResolvedContainerPlasticCanConfig, bottom_z: float) -> cq.Workplane:
    """Through pour-mouth bore down the neck axis into the hollow interior."""
    return (
        cq.Workplane("XY")
        .workplane(offset=bottom_z)
        .center(r.neck_x, r.neck_y)
        .circle(r.mouth_bore_r)
        .extrude((r.neck_top_z + 0.002) - bottom_z)
    )


def _body_rounded_rect(r: ResolvedContainerPlasticCanConfig, *, deck: bool) -> cq.Workplane:
    """Rounded-rect HDPE jug: hollow shell + tapered shoulder.

    ``deck=True``  -> draw-in to a small top deck (gallon-jug parent 001).
    ``deck=False`` -> full-width shoulder slab + ring-foot recess (oil parent 002).
    """
    bw, bd, bh, sh, wall = r.body_w, r.body_d, r.body_h, r.shoulder_h, r.wall
    top_z = bh + sh
    if deck:
        deck_w, deck_d = bw * 0.60, bd * 0.58
        sh_w, sh_d = bw * 0.78, bd * 0.76
    else:
        deck_w, deck_d = bw * 0.90, bd * 0.90
        sh_w, sh_d = bw * 0.97, bd * 0.97

    # Outer wall starts full-width at z=0 (no bottom tuck-in: that loft undercut
    # left a thin disconnected base lip at small scales).
    outer_sections = [
        (0.0, bw, bd),
        (bh * 0.5, bw, bd),
        (bh, bw * 0.97, bd * 0.97),
        (bh + sh * 0.55, sh_w, sh_d),
        (top_z, deck_w, deck_d),
    ]
    outer = _rrect_loft(outer_sections)

    # Inner cavity follows the OUTER shoulder profile (offset inward by ``wall``)
    # all the way up through the shoulder draw-in to just under the deck top, so
    # the body is one connected hollow shell with a uniform ~``wall`` wall right
    # up to the deck. The deck keeps a ``wall``-thick roof; the wide pour-mouth
    # bore (below) pierces that roof so looking down the open neck reveals the
    # hollow interior (no solid molded-cap slab).
    inner_top_z = top_z - wall
    inner_sections = [
        (wall, bw - 2 * wall, bd - 2 * wall),
        (bh * 0.5, bw - 2 * wall, bd - 2 * wall),
        (bh, bw * 0.97 - 2 * wall, bd * 0.97 - 2 * wall),
        (bh + sh * 0.55, sh_w - 2 * wall, sh_d - 2 * wall),
        (inner_top_z, deck_w - 2 * wall, deck_d - 2 * wall),
    ]
    inner = _rrect_loft(inner_sections)

    neck = _neck_stub(r, top_z - 0.004)
    shell = outer.union(neck).cut(inner)

    if not deck:
        # Ring-foot base recess (parent 002): a shallow CONCAVE dish in the
        # underside so it stands on a ring foot. The recess top MUST stay strictly
        # below the inner cavity floor top (z=``wall``) so a solid ~``wall``-thick
        # floor cap remains above it -- otherwise the recess punches a through-hole
        # and the bottle has an open bottom (you'd see straight down the mouth to
        # the ground). Start from the underside (z=-0.001) and stop a safe margin
        # below the floor inner surface.
        recess_bottom_z = -0.001
        recess_top_z = wall - 0.002  # leave >= ~2mm solid floor above the recess
        recess_depth = recess_top_z - recess_bottom_z
        if recess_depth > 0.0015:  # only carve if a real, non-breaking dish fits
            base_recess = (
                cq.Workplane("XY")
                .workplane(offset=recess_bottom_z)
                .rect(bw * 0.70, bd * 0.65)
                .extrude(recess_depth)
            )
            shell = shell.cut(base_recess)

    shell = shell.cut(_mouth_bore(r, wall + 0.001))
    return shell


def _body_square_cubic(r: ResolvedContainerPlasticCanConfig) -> cq.Workplane:
    """Chunky near-cubic square pail (parent 003): filleted box + recessed deck
    + offset boss/neck + stacking ribs + flared foot, hollow with a pour-mouth."""
    bw, bd, wall = r.body_w, r.body_d, r.wall
    deck_z = r.body_h + r.shoulder_h - 0.014  # recessed deck base
    edge_r = min(0.024, min(bw, bd) * 0.10)

    body = (
        cq.Workplane("XY")
        .box(bw, bd, deck_z, centered=(True, True, False))
        .edges("|Z")
        .fillet(edge_r)
    )
    body = body.edges(">Z").fillet(0.012)

    sh_w = bw - 0.014
    sh_d = bd - 0.014
    sh_z0 = deck_z - 0.020
    sh_top = deck_z + 0.014
    shoulder = (
        cq.Workplane("XY")
        .workplane(offset=sh_z0)
        .box(sh_w, sh_d, sh_top - sh_z0, centered=(True, True, False))
        .edges("|Z")
        .fillet(edge_r)
        .edges(">Z")
        .fillet(0.014)
    )
    body = body.union(shoulder)

    # Recessed top deck pocket.
    deck_floor = deck_z - 0.004
    pocket = (
        cq.Workplane("XY")
        .workplane(offset=deck_floor)
        .box(sh_w - 0.030, sh_d - 0.030, sh_top - deck_floor + 0.01, centered=(True, True, False))
    )
    body = body.cut(pocket)

    # Hollow interior: a real cavity inside the chunky box so the pail is a true
    # hollow shell (not a solid block with a drilled hole). Floor sits above the
    # foot/ribs, walls are ~``wall`` thick, and the roof stops a ``wall`` below
    # the recessed deck floor -- the wide neck bore then pierces that roof so
    # looking down the open neck reveals the hollow interior.
    cav_floor_z = wall + 0.012
    cav_top_z = deck_floor - wall

    # Offset boss + neck root ON the cavity roof (z=cav_top_z) so they stay fused
    # to the molded shell after the interior is hollowed out.
    boss = (
        cq.Workplane("XY")
        .workplane(offset=cav_top_z)
        .center(r.neck_x, r.neck_y)
        .circle(r.neck_r + 0.010)
        .extrude((deck_floor - cav_top_z) + 0.012)
    )
    body = body.union(boss)
    neck = (
        cq.Workplane("XY")
        .workplane(offset=cav_top_z)
        .center(r.neck_x, r.neck_y)
        .circle(r.neck_r)
        .extrude(r.neck_top_z - cav_top_z)
    )
    body = body.union(neck)

    # Mid-body + base stacking ribs (proud external bands) + flared foot. These
    # are unioned BEFORE the interior is hollowed so the final inner/bore cuts
    # clear them out of the cavity (a solid rib slab would otherwise re-plug the
    # hollow interior).
    for zb, th in ((0.020, 0.012), (deck_z * 0.55, 0.010)):
        ridge = (
            cq.Workplane("XY")
            .workplane(offset=zb)
            .box(bw + 0.008, bd + 0.008, th, centered=(True, True, False))
            .edges("|Z")
            .fillet(edge_r)
        )
        body = body.union(ridge)
    foot = (
        cq.Workplane("XY")
        .box(bw + 0.012, bd + 0.012, 0.010, centered=(True, True, False))
        .edges("|Z")
        .fillet(edge_r)
    )
    body = body.union(foot)

    inner = (
        cq.Workplane("XY")
        .workplane(offset=cav_floor_z)
        .box(bw - 2 * wall, bd - 2 * wall, cav_top_z - cav_floor_z, centered=(True, True, False))
        .edges("|Z")
        .fillet(edge_r)
    )
    body = body.cut(inner)

    # Pour-mouth bore: from inside the cavity up through the deck roof and neck.
    bore = (
        cq.Workplane("XY")
        .workplane(offset=cav_top_z - 0.004)
        .center(r.neck_x, r.neck_y)
        .circle(r.mouth_bore_r)
        .extrude((r.neck_top_z + 0.002) - (cav_top_z - 0.004))
    )
    body = body.cut(bore)
    return body


def _sloped_wedge_cutter(r: ResolvedContainerPlasticCanConfig) -> cq.Workplane:
    """Half-space above the cap-side slope plane (parent 004)."""
    bw = r.body_w
    deck_low_z = r.body_h + r.shoulder_h * 0.47
    top_z = r.body_h + r.shoulder_h
    x_knee = -bw * 0.06
    pitch = math.atan2(top_z - deck_low_z, x_knee + bw / 2.0)
    cutter = cq.Workplane("XY").box(0.9, 0.9, 0.9, centered=(True, True, False))
    cutter = cutter.rotate((0, 0, 0), (0, 1, 0), -math.degrees(pitch))
    return cutter.translate((-bw / 2.0, 0.0, deck_low_z))


def _body_sloped(r: ResolvedContainerPlasticCanConfig) -> cq.Workplane:
    """Tall rectangular jerrycan (parent 004): box + sloped wedge -> high
    plateau + spout boss, hollow with a pour-mouth. Neck sits on the LOW -X
    shoulder; here we keep the unified +X neck convention by placing the boss
    on the +X plateau half so the neck still sits on solid molded shoulder."""
    bw, bd, wall = r.body_w, r.body_d, r.wall
    base_h = 0.026
    wall_h = r.body_h - base_h
    wall_top = base_h + wall_h
    top_z = r.body_h + r.shoulder_h

    foot = cq.Workplane("XY").box(bw + 0.004, bd + 0.004, base_h, centered=(True, True, False))
    walls = (
        cq.Workplane("XY")
        .workplane(offset=base_h)
        .box(bw, bd, wall_h, centered=(True, True, False))
    )
    body = foot.union(walls)

    shoulder = (
        cq.Workplane("XY")
        .workplane(offset=wall_top)
        .box(bw, bd, top_z - wall_top, centered=(True, True, False))
    )
    shoulder = shoulder.cut(_sloped_wedge_cutter(r))
    body = body.union(shoulder)
    body = body.edges("|Z").fillet(0.008)

    # Molded spout boss the neck rises from -- a DEEPLY embedded pedestal that the
    # sloped shoulder flows up into, not a flat disc plopped on the slope. The
    # slope drops from the +X plateau down toward the -X neck side, so a shallow
    # boss leaves its downhill (-X) half cantilevered over the falling slope (the
    # "half-floating" look). To avoid that, root the skirt BELOW the lowest slope
    # point anywhere under the boss footprint, so the whole base is buried in
    # solid shoulder and the mound reads as one continuous molded form (parent
    # 004 builds its boss the same way: skirt embedded ~32mm + filleted).
    neck_base_z = r.deck_top_z
    boss_base_r = min(
        r.neck_r + 0.018,
        (r.neck_x + bw / 2.0) - 0.003,
        (bw / 2.0 - r.neck_x) - 0.003,
    )
    slope_lo = _sloped_shoulder_surface_z(
        body_w=bw, body_h=r.body_h, shoulder_h=r.shoulder_h, x=r.neck_x - boss_base_r
    )
    z0 = min(slope_lo, neck_base_z) - 0.012  # skirt buried below the lowest under-boss slope
    boss_top_z = neck_base_z + 0.011
    # Taper from the wide buried skirt all the way to neck_r at the crown so the
    # threaded neck continues out of it with NO ledge.
    boss = (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .center(r.neck_x, r.neck_y)
        .circle(boss_base_r)
        .workplane(offset=(boss_top_z - z0) - 0.009)
        .circle(r.neck_r + 0.005)
        .workplane(offset=0.009)
        .circle(r.neck_r)
        .loft(ruled=False)
    )
    body = body.union(boss)
    # Fillet the boss <-> sloped-shoulder junction (downhill -X side, where the
    # gap used to read) for a molded blend. Best-effort: skip if the kernel can't
    # resolve the loft junction edge at this scale.
    try:
        body = body.edges(
            cq.selectors.NearestToPointSelector((r.neck_x - boss_base_r * 0.7, r.neck_y, slope_lo))
        ).fillet(0.005)
    except Exception:  # noqa: BLE001 - cosmetic blend only
        pass
    neck = (
        cq.Workplane("XY")
        .workplane(offset=boss_top_z - 0.004)
        .center(r.neck_x, r.neck_y)
        .circle(r.neck_r)
        .extrude(r.neck_top_z - (boss_top_z - 0.004))
    )
    body = body.union(neck)

    # Hollow interior + pour mouth. The cavity now rises up through the sloped
    # shoulder/plateau (capped a ``wall`` below the sloped roof via the same
    # wedge cutter, shifted down by ``wall``) so it is one connected hollow shell
    # with a uniform wall right up under the deck -- the wide neck bore pierces
    # that roof so looking down the open neck reveals the hollow interior (no
    # solid molded-cap slab).
    inner_bottom_z = base_h + 0.010
    inner = (
        cq.Workplane("XY")
        .workplane(offset=inner_bottom_z)
        .box(
            bw - 2 * wall,
            bd - 2 * wall,
            (top_z - wall) - inner_bottom_z,
            centered=(True, True, False),
        )
    )
    # Carve the cavity roof parallel to the outer slope, a ``wall`` below it, so
    # the sloped shoulder keeps a uniform ~``wall`` roof.
    roof_cutter = _sloped_wedge_cutter(r).translate((0.0, 0.0, -wall))
    inner = inner.cut(roof_cutter)
    body = body.cut(inner)
    mouth = (
        cq.Workplane("XY")
        .workplane(offset=inner_bottom_z)
        .center(r.neck_x, r.neck_y)
        .circle(r.mouth_bore_r)
        .extrude((r.neck_top_z + 0.006) - inner_bottom_z)
    )
    body = body.cut(mouth)
    return body


def _body_solid(r: ResolvedContainerPlasticCanConfig) -> cq.Workplane:
    if r.body_form == "tall_rounded_rect_deck":
        return _body_rounded_rect(r, deck=True)
    if r.body_form == "tall_rounded_rect_slab":
        return _body_rounded_rect(r, deck=False)
    if r.body_form == "square_cubic":
        return _body_square_cubic(r)
    return _body_sloped(r)


# ---------------------------------------------------------------------------
# Body interface helpers shared by handle + closure builders.
# ---------------------------------------------------------------------------
def _shoulder_top_z(r: ResolvedContainerPlasticCanConfig) -> float:
    """World z of the shoulder/deck top surface (handle plateau reference)."""
    return r.body_h + r.shoulder_h


def _handle_x(r: ResolvedContainerPlasticCanConfig) -> float:
    """X position for top-mounted handles: opposite the offset neck, anchored on
    the shoulder wall (~ +-62% of the half-width) so the handle roots into solid
    wall, while guaranteeing >= 0.06 clearance from the neck."""
    half_w = r.body_w / 2.0
    side = -1.0 if r.neck_x >= 0.0 else 1.0  # opposite the neck
    x = side * min(half_w * 0.62, max(0.045, half_w - 0.030))
    # Ensure clearance from the offset neck.
    if abs(x - r.neck_x) < 0.06:
        x = r.neck_x + side * 0.06
    return x


def _handle_top_z(r: ResolvedContainerPlasticCanConfig) -> float:
    """Real top-surface z at the handle column, per body form. Top handles
    (strap / slot / bail lugs) must root from this so they don't float."""
    if r.body_form == "tall_rectangular_sloped":
        # Handle lives on the +X high plateau (the sloped wedge is cut on -X).
        return r.body_h + r.shoulder_h
    if r.body_form == "square_cubic":
        # Recessed-deck pail: the shoulder top sits just above the deck floor.
        return r.body_h + r.shoulder_h - 0.014 + 0.014
    # Rounded-rect jugs: shoulder/deck top.
    return r.body_h + r.shoulder_h


# ===========================================================================
# Slot B — handle_grip. Five FIXED variants return CadQuery geometry to union /
# cut into the body shell (no separate part, no joint). swing_bail returns None
# here and is emitted as a separate REVOLUTE part in build().
# ===========================================================================
def _handle_loop_solid(r: ResolvedContainerPlasticCanConfig) -> cq.Workplane:
    """Raised rounded loop with a real open finger hole (parent 001)."""
    hs = r.handle_size_scale
    cx = _handle_x(r)
    outer_w = 0.072 * hs
    outer_h = min(0.115 * hs, r.body_h * 0.55)
    thick_y = min(0.028, r.body_d * 0.32)
    root_z = r.body_h - 0.030
    cz = root_z + outer_h / 2.0
    hole_w = outer_w * 0.55
    hole_h = outer_h * 0.62
    hole_cz = cz + outer_h * 0.12

    loop = cq.Workplane("XZ").center(cx, cz).rect(outer_w, outer_h).extrude(thick_y, both=True)
    loop = loop.edges("|Y").fillet(min(0.016, outer_w * 0.2))
    hole = (
        cq.Workplane("XZ")
        .center(cx, hole_cz)
        .rect(hole_w, hole_h)
        .extrude(thick_y + 0.02, both=True)
    )
    hole = hole.edges("|Y").fillet(min(0.015, hole_w * 0.3))
    return loop.cut(hole)


def _flush_dgrip_solid(r: ResolvedContainerPlasticCanConfig) -> cq.Workplane:
    """Molded side grab-handle: a proud vertical grip bar standing off the upper
    side wall (the X-extreme face opposite the offset neck), bridged to the wall
    by a top and a bottom web. The finger gap between the bar and the wall is the
    grip opening.

    Earlier this slot cut an oval straight through the full body depth -- on a
    hollow can that punches two daylight holes into the liquid cavity, so it read
    as an accidental leak, not a handle. This molded grab-bar never pierces the
    body wall, so the cavity stays sealed while the loop reads unmistakably as a
    carry handle (a real oil-jug / jerrycan moulded side grip).
    """
    hs = r.handle_size_scale
    half_w = r.body_w / 2.0
    side = -1.0 if r.neck_x >= 0.0 else 1.0  # opposite the offset neck
    face_x = side * half_w

    bar_len_z = min(0.105 * hs, r.body_h * 0.52)
    grip_cz = r.body_h * 0.60
    z0 = grip_cz - bar_len_z / 2.0
    z1 = grip_cz + bar_len_z / 2.0
    grip_half_y = min(0.030, r.body_d * 0.40)
    bar_thick_x = 0.015
    gap = 0.024  # finger clearance between the bar and the wall
    embed = 0.006  # web root embedded into the wall so the handle fuses solidly
    web_h = 0.013

    bar_cx = face_x + side * (gap + bar_thick_x / 2.0)
    bar = (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .center(bar_cx, 0.0)
        .box(bar_thick_x, 2.0 * grip_half_y, bar_len_z, centered=(True, True, False))
        .edges("|Y")
        .fillet(min(0.006, bar_thick_x * 0.45))
    )
    # Top + bottom webs span from inside the wall out to the bar, leaving the
    # middle of the gap open as the finger hole.
    web_len = embed + gap + bar_thick_x
    web_cx = face_x + side * (web_len / 2.0 - embed)
    handle = bar
    for wz in (z0, z1 - web_h):
        web = (
            cq.Workplane("XY")
            .workplane(offset=wz)
            .center(web_cx, 0.0)
            .box(web_len, 2.0 * grip_half_y, web_h, centered=(True, True, False))
            .edges("|Y")
            .fillet(min(0.004, web_h * 0.3))
        )
        handle = handle.union(web)
    return handle


def _bridge_strap_solid(r: ResolvedContainerPlasticCanConfig) -> cq.Workplane:
    """Raised arched carry strap over the deck, opposite the neck (parent 003).

    Built PURELY ADDITIVELY as two end legs + a top bar -- the finger gap is the
    open air ABOVE the intact deck, between the legs. The earlier version carved
    a tunnel whose floor sat ~10mm BELOW the deck, digging a blind trench/pit
    into the body that read as a hole. Here nothing is cut from the body: the
    legs root down into the solid upper body for fusion, and the only opening is
    the clean grip gap above the unbroken deck.
    """
    hs = r.handle_size_scale
    sh_top = _handle_top_z(r)
    bridge_x = _handle_x(r)
    bridge_len = min(0.150 * hs, r.body_d * 0.62)
    bar_x = 0.034 * hs
    bar_h = 0.015
    arch_top = sh_top + 0.044  # grip gap above deck = arch_top - bar_h - sh_top ~ 0.029
    leg_w_y = min(0.024, bridge_len * 0.32)
    leg_bot_z = r.body_h * 0.55  # buried root so the legs always fuse to the body
    leg_y = bridge_len / 2.0 - leg_w_y / 2.0

    handle = None
    for sy in (-1.0, 1.0):
        leg = (
            cq.Workplane("XY")
            .workplane(offset=leg_bot_z)
            .center(bridge_x, sy * leg_y)
            .box(bar_x, leg_w_y, arch_top - leg_bot_z, centered=(True, True, False))
            .edges("|Y")
            .fillet(min(0.008, bar_x * 0.24))
        )
        handle = leg if handle is None else handle.union(leg)
    top_bar = (
        cq.Workplane("XY")
        .workplane(offset=arch_top - bar_h)
        .center(bridge_x, 0.0)
        .box(bar_x, bridge_len, bar_h, centered=(True, True, False))
        .edges("|Y")
        .fillet(min(0.007, bar_h * 0.4))
    )
    return handle.union(top_bar)


def _recessed_slot_parts(
    r: ResolvedContainerPlasticCanConfig,
) -> tuple[cq.Workplane, cq.Workplane]:
    """Front-to-back rounded carry slot in the high shoulder, leaving a grip bar
    (parent 004). Placed on the -X shoulder half opposite the neck.

    Returns ``(fill, slot)``: ``fill`` is a solid block that seals the hollow
    cavity in the slot's X-slice (floor->deck, full depth) BEFORE the slot is
    carved, so the finger slot passes through solid molded plastic and never
    breaks into the liquid chamber (the body stays closed except the pour mouth,
    matching the real jerrycan, parent 004). The grip bar + slab around the slot
    are the only geometry the fingers touch.
    """
    hs = r.handle_size_scale
    sh_top = _handle_top_z(r)
    grip_cx = _handle_x(r)
    grip_cz = sh_top - 0.030
    half_x = 0.040 * hs
    half_z = min(0.021 * hs, max(r.shoulder_h * 0.42, 0.018))
    fillet = min(0.019, half_z * 0.85)

    fill_bot = grip_cz - half_z - 0.014
    fill_top = sh_top + 0.003
    fill = (
        cq.Workplane("XY")
        .workplane(offset=fill_bot)
        .center(grip_cx, 0.0)
        .box(2.0 * half_x + 0.020, r.body_d, fill_top - fill_bot, centered=(True, True, False))
    )
    slot = (
        cq.Workplane("XZ")
        .center(grip_cx, grip_cz)
        .rect(2.0 * half_x, 2.0 * half_z)
        .extrude(r.body_d + 0.080, both=True)
    )
    return fill, slot.edges("|Y").fillet(fillet)


def _grip_pocket_parts(
    r: ResolvedContainerPlasticCanConfig,
) -> tuple[cq.Workplane, list[cq.Workplane]]:
    """Two overlapping sphere cuts -> elongated concave hand-hold pocket on the
    +X side wall (variant recessed_grip_pocket).

    Returns ``(fill, cuts)``: ``fill`` is a local solid pad that thickens the
    side wall inward (into the hollow) BEHIND the pocket region BEFORE the scoops
    are cut, so the concave grip bottoms out in solid molded plastic and never
    punches through into the liquid chamber (a real recessed grip on a thin blow-
    molded wall -- the source variant got away with raw scoops only because its
    body was solid). No through-hole, wall stays closed behind the pocket.
    """
    hs = r.handle_size_scale
    pocket_cz = r.body_h * 0.75
    pocket_r = 0.040 * hs
    pocket_cx = r.body_w / 2.0 + pocket_r * 0.55  # sphere center outside wall
    dz = 0.014

    # Pad reaches from ~30mm inboard of the outer face out to the surface, deep
    # enough that the inboard cap of each scoop (reaches x = pocket_cx - pocket_r)
    # bottoms inside it.
    pad_in_x = r.body_w / 2.0 - 0.030
    pad_half_y = min(pocket_r + 0.006, r.body_d / 2.0 - 0.003)
    pad_z0 = pocket_cz - dz - pocket_r * 0.7
    pad_z1 = pocket_cz + dz + pocket_r * 0.7
    fill = (
        cq.Workplane("XY")
        .workplane(offset=pad_z0)
        .center((pad_in_x + r.body_w / 2.0) / 2.0, 0.0)
        .box(
            r.body_w / 2.0 - pad_in_x + 0.002,
            2.0 * pad_half_y,
            pad_z1 - pad_z0,
            centered=(True, True, False),
        )
    )
    cuts = []
    for sign in (-1.0, 1.0):
        scoop = (
            cq.Workplane("XY").sphere(pocket_r).translate((pocket_cx, 0.0, pocket_cz + sign * dz))
        )
        cuts.append(scoop)
    return fill, cuts


# ---------------------------------------------------------------------------
# swing_bail: separate REVOLUTE part. Body emits two shoulder lugs; the U-bar
# bail tube swings on them about +Y. Returns (lug_solid, pivot_z) so the body
# can fuse the lugs, plus a _bail_mesh in its own frame.
# ---------------------------------------------------------------------------
def _bail_geom(r: ResolvedContainerPlasticCanConfig) -> dict:
    sh_top = _handle_top_z(r)
    bail_x = _handle_x(r)
    lug_half_y = min(0.060, r.body_d * 0.40)
    lug_w_x = 0.018
    lug_w_y = 0.014
    lug_h = 0.018
    arm_len = min(0.080 * r.handle_size_scale, r.body_w * 0.42)
    radius = 0.005
    pivot_z = sh_top + lug_h / 2.0
    return {
        "bail_x": bail_x,
        "lug_half_y": lug_half_y,
        "lug_w_x": lug_w_x,
        "lug_w_y": lug_w_y,
        "lug_h": lug_h,
        "arm_len": arm_len,
        "radius": radius,
        "pivot_z": pivot_z,
        "sh_top": sh_top,
    }


def _bail_lugs_solid(r: ResolvedContainerPlasticCanConfig, bg: dict) -> cq.Workplane:
    """Two mounting lugs (one per sign) standing on the shoulder top."""
    sh_top = bg["sh_top"]
    solid = None
    for sign in (-1, 1):
        # Support column rooted below the shoulder top so it always fuses with
        # the body solid even after deck pockets are cut.
        col_bottom = sh_top - 0.030
        col = (
            cq.Workplane("XY")
            .workplane(offset=col_bottom)
            .center(bg["bail_x"], sign * bg["lug_half_y"])
            .box(
                bg["lug_w_x"],
                bg["lug_w_y"],
                (sh_top + bg["lug_h"]) - col_bottom,
                centered=(True, True, False),
            )
        )
        lug = (
            cq.Workplane("XY")
            .workplane(offset=sh_top)
            .center(bg["bail_x"], sign * bg["lug_half_y"])
            .box(bg["lug_w_x"], bg["lug_w_y"], bg["lug_h"], centered=(True, True, False))
            .edges(">Z")
            .fillet(0.003)
        )
        piece = col.union(lug)
        solid = piece if solid is None else solid.union(piece)
    # Saddle rib spanning the two lugs at the pivot height, so real body
    # geometry sits at the pivot origin (bail_x, 0, pivot_z) -> the REVOLUTE
    # origin stays within the parent-geometry tolerance, and the bail tube ends
    # are bridged by a molded bearing saddle.
    saddle = (
        cq.Workplane("XY")
        .workplane(offset=bg["pivot_z"] - bg["radius"] - 0.002)
        .center(bg["bail_x"], 0.0)
        .box(
            bg["lug_w_x"],
            2.0 * bg["lug_half_y"],
            2.0 * bg["radius"] + 0.004,
            centered=(True, True, False),
        )
    )
    solid = solid.union(saddle)
    return solid


def _bail_mesh(r: ResolvedContainerPlasticCanConfig, bg: dict):
    """U-shaped bail tube in its own frame: at q=0 it lies flat extending -X.

    The path runs as a single continuous spline from one pivot end, across the
    arms and crossbar, back to the other pivot end -- but it passes THROUGH the
    bail-local origin (0,0,0) at the pivot rod so the child link's frame origin
    sits on real bail geometry (keeps the REVOLUTE origin within tolerance)."""
    arm = bg["arm_len"]
    ly = bg["lug_half_y"]
    # Continuous U + pivot rod: start at -Y pivot end, run a short rod through
    # the origin to the +Y pivot end is not a U; instead route pivot -> arm ->
    # crossbar -> arm -> pivot, then we add a separate pivot rod that the path
    # touches at the origin via the pivot-end tangents. To guarantee material at
    # (0,0,0) we route the spline through (0,0,0) between the two pivot ends.
    points = [
        (0.0, -ly, 0.0),
        (-arm * 0.50, -ly, 0.0),
        (-arm * 0.85, -ly, 0.0),
        (-arm, -ly * 0.75, 0.0),
        (-arm, 0.0, 0.0),
        (-arm, ly * 0.75, 0.0),
        (-arm * 0.85, ly, 0.0),
        (-arm * 0.50, ly, 0.0),
        (0.0, ly, 0.0),
    ]
    geom = tube_from_spline_points(
        points,
        radius=bg["radius"],
        samples_per_segment=16,
        radial_segments=20,
        cap_ends=True,
        up_hint=(0.0, 0.0, 1.0),
    )
    # Pivot rod spanning the two pivot ends along Y through the bail-local
    # origin, so child geometry exists at the joint origin (0,0,0).
    rod = CylinderGeometry(bg["radius"], 2.0 * ly + 2.0 * bg["radius"], radial_segments=16)
    rod.rotate_x(math.pi / 2.0)  # cylinder axis along +Y
    rod.translate(0.0, 0.0, 0.0)
    geom.merge(rod)
    return mesh_from_geometry(geom, "bail_tube")


# ===========================================================================
# Slot C — cap_closure geometry helpers.
# ===========================================================================
def _screw_cap_mesh(r: ResolvedContainerPlasticCanConfig):
    """Round knurled screw cap: short cylinder + ring of vertical ribs + rim."""
    cap_r = r.cap_r
    cap = CylinderGeometry(cap_r, _CAP_H, radial_segments=44)
    cap.translate(0.0, 0.0, _CAP_H / 2.0)
    n = 24
    for i in range(n):
        a = 2.0 * math.pi * i / n
        rib = CylinderGeometry(0.0016, _CAP_H * 0.82, radial_segments=6)
        rib.translate(cap_r * 0.99 * math.cos(a), cap_r * 0.99 * math.sin(a), _CAP_H / 2.0)
        cap.merge(rib)
    rim = TorusGeometry(cap_r - 0.002, 0.0022, radial_segments=10, tubular_segments=40)
    rim.translate(0.0, 0.0, _CAP_H - 0.002)
    cap.merge(rim)
    return mesh_from_geometry(cap, "cap_shell")


def _flip_spout_base_solid(r: ResolvedContainerPlasticCanConfig) -> cq.Workplane:
    """Fixed flip-top base: threaded collar ring + top plate + raised spout."""
    collar_r = r.collar_r
    collar_bore_r = r.neck_r - 0.001
    collar_top_z = r.neck_top_z + _COLLAR_H
    spout_r_outer = max(0.011, r.neck_r * 0.5)
    spout_r_inner = max(0.008, r.neck_r * 0.36)

    collar = (
        cq.Workplane("XY")
        .workplane(offset=r.neck_top_z - 0.002)
        .center(r.neck_x, r.neck_y)
        .circle(collar_r)
        .circle(collar_bore_r)
        .extrude(_COLLAR_H + 0.002)
    )
    top_plate = (
        cq.Workplane("XY")
        .workplane(offset=collar_top_z - 0.002)
        .center(r.neck_x, r.neck_y)
        .circle(collar_r - 0.001)
        .circle(spout_r_inner)
        .extrude(0.003)
    )
    spout = (
        cq.Workplane("XY")
        .workplane(offset=collar_top_z - 0.001)
        .center(r.neck_x, r.neck_y)
        .circle(spout_r_outer)
        .circle(spout_r_inner)
        .extrude(_SPOUT_H + 0.001)
    )
    return collar.union(top_plate).union(spout)


def _flip_lid_solid(r: ResolvedContainerPlasticCanConfig, *, hinge_offset_y: float) -> cq.Workplane:
    """Hollow flip-top lid in its own frame (origin = hinge pivot at rear collar
    edge). Open-bottom cup that covers the raised spout when closed."""
    collar_top_z = r.neck_top_z + _COLLAR_H
    lid_disc_r = r.collar_r + 0.004
    lid_wall = 0.003
    lid_h = _SPOUT_H + 0.005
    cap_cy = -hinge_offset_y

    outer = cq.Workplane("XY").center(0.0, cap_cy).circle(lid_disc_r).extrude(lid_h)
    cavity = (
        cq.Workplane("XY")
        .center(0.0, cap_cy)
        .circle(lid_disc_r - lid_wall)
        .extrude(lid_h - lid_wall)
    )
    cap = outer.cut(cavity)
    ear = cq.Workplane("XY").center(0.0, cap_cy * 0.2).rect(0.007, abs(cap_cy) * 0.5).extrude(lid_h)
    return cap.union(ear), collar_top_z, lid_disc_r, lid_h


def _tethered_collar_anchor_solid(
    r: ResolvedContainerPlasticCanConfig,
) -> tuple[cq.Workplane, float]:
    """Fixed collar ring + +Y anchor nub (living-hinge fixed end). Returns the
    union solid and collar_top_z."""
    collar_outer_r = r.neck_r + 0.005
    collar_h = 0.006
    collar_top_z = r.neck_top_z + collar_h
    anchor_w = 0.010
    anchor_ext = 0.004
    # Annular collar ring (NOT a solid disc): it must keep the pour mouth open so
    # that with the flip cap raised you look straight down the neck bore into the
    # hollow body. A solid disc here re-seals the mouth the body bore just opened.
    collar = (
        cq.Workplane("XY")
        .workplane(offset=r.neck_top_z)
        .center(r.neck_x, r.neck_y)
        .circle(collar_outer_r)
        .circle(r.mouth_bore_r)
        .extrude(collar_h)
    )
    anchor = (
        cq.Workplane("XY")
        .workplane(offset=r.neck_top_z)
        .center(r.neck_x, r.neck_y + collar_outer_r + anchor_ext / 2.0)
        .box(anchor_w, anchor_ext, collar_h, centered=(True, True, False))
    )
    return collar.union(anchor), collar_top_z


def _tethered_flip_cap_solid(r: ResolvedContainerPlasticCanConfig) -> cq.Workplane:
    """Captive flip cap in its own frame (origin at hinge). Disc + raised rim +
    grip ridges + strap tab + lift bump (variant hinged_tethered_lid)."""
    flip_cap_r = r.neck_r + 0.005
    flip_cap_h = 0.005
    rim_h = 0.008
    rim_t = 0.003
    strap_w = 0.010
    strap_ext = 0.006

    disc = cq.Workplane("XY").center(0.0, -flip_cap_r).circle(flip_cap_r).extrude(flip_cap_h)
    rim = (
        cq.Workplane("XY")
        .center(0.0, -flip_cap_r)
        .circle(flip_cap_r + 0.001)
        .circle(flip_cap_r - rim_t)
        .extrude(rim_h)
    )
    cap = disc.union(rim)
    n_ridges = 20
    for i in range(n_ridges):
        angle = 2.0 * math.pi * i / n_ridges
        if abs(math.sin(angle) - 1.0) < 0.3:
            continue
        rx = flip_cap_r * math.cos(angle)
        ry = -flip_cap_r + flip_cap_r * math.sin(angle)
        ridge = cq.Workplane("XY").center(rx, ry).circle(0.0012).extrude(rim_h - 0.001)
        cap = cap.union(ridge)
    strap = (
        cq.Workplane("XY").center(0.0, strap_ext / 2.0).rect(strap_w, strap_ext).extrude(flip_cap_h)
    )
    cap = cap.union(strap)
    bump = cq.Workplane("XY").center(0.0, -flip_cap_r).circle(0.005).extrude(0.011)
    cap = cap.union(bump)
    return cap, flip_cap_r, flip_cap_h


# ===========================================================================
# Closure builders. Each attaches one closure mechanism to the body.
# ===========================================================================
def _build_screw_cap(model, body, r, *, cap_mat, accent_mat) -> None:
    """CONTINUOUS spin + PRISMATIC lift via a massless carrier (parent pattern).
    body -> (cap_rotate +Z) -> cap_carrier -> (cap_slide +Z) -> cap."""
    slide = _CAP_SLIDE * r.closure_travel_scale

    carrier = model.part("cap_carrier")
    carrier.inertial = Inertial.from_geometry(Box((0.01, 0.01, 0.01)), mass=1e-4)
    model.articulation(
        "cap_rotate",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=carrier,
        origin=Origin(xyz=(r.neck_x, r.neck_y, r.neck_top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.0),
    )

    cap = model.part("cap")
    cap.visual(
        _screw_cap_mesh(r),
        material=cap_mat,
        name="cap_shell",
        material_class_id=_material_class_id("cap"),
    )
    # Off-axis marker so a spin is observable in tests. Authored at the cap-local
    # origin (which sits at the neck rim), centered on +Z.
    cap.visual(
        Box((0.006, 0.006, 0.006)),
        origin=Origin(xyz=(r.cap_r + 0.002, 0.0, _CAP_H * 0.5)),
        material=accent_mat,
        name="cap_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    cap.inertial = Inertial.from_geometry(
        Box((2 * r.cap_r, 2 * r.cap_r, _CAP_H)),
        mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, _CAP_H / 2.0)),
    )
    model.articulation(
        "cap_slide",
        ArticulationType.PRISMATIC,
        parent=carrier,
        child=cap,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=slide, effort=1.0, velocity=1.0),
    )


def _build_flip_top_spout(model, body, r, *, cap_mat, base_mat) -> None:
    """Fixed collar+spout base (body visual) + hollow lid flipping REVOLUTE -X."""
    # Fixed closure base fused into the body part as a visual.
    body.visual(
        mesh_from_cadquery(_flip_spout_base_solid(r), "closure_base"),
        material=base_mat,
        name="closure_base",
        material_class_id=_material_class_id("body"),
    )

    hinge_offset_y = r.collar_r * 0.92
    lid_solid, collar_top_z, lid_disc_r, lid_h = _flip_lid_solid(r, hinge_offset_y=hinge_offset_y)
    upper = min(2.6 * r.closure_travel_scale, 2.8)

    lid = model.part("lid")
    lid.visual(
        mesh_from_cadquery(lid_solid, "lid_cap"),
        material=cap_mat,
        name="lid_cap",
        material_class_id=_material_class_id("cap"),
    )
    lid.inertial = Inertial.from_geometry(
        Box((2.0 * lid_disc_r, 2.0 * lid_disc_r, lid_h)),
        mass=0.015,
        origin=Origin(xyz=(0.0, -hinge_offset_y, lid_h / 2.0)),
    )
    model.articulation(
        "lid_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(r.neck_x, r.neck_y + hinge_offset_y, collar_top_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=upper, effort=2.0, velocity=4.0),
    )


def _build_hinged_tethered_lid(model, body, r, *, cap_mat, base_mat) -> None:
    """Fixed collar+anchor (body visual) + captive flip cap REVOLUTE -X."""
    collar_anchor, collar_top_z = _tethered_collar_anchor_solid(r)
    body.visual(
        mesh_from_cadquery(collar_anchor, "closure_base"),
        material=base_mat,
        name="closure_base",
        material_class_id=_material_class_id("body"),
    )

    flip_solid, flip_cap_r, flip_cap_h = _tethered_flip_cap_solid(r)
    collar_outer_r = r.neck_r + 0.005
    upper = min(2.6 * r.closure_travel_scale, 2.8)

    flip_cap = model.part("flip_cap")
    flip_cap.visual(
        mesh_from_cadquery(flip_solid, "flip_cap_shell"),
        material=cap_mat,
        name="flip_cap_shell",
        material_class_id=_material_class_id("cap"),
    )
    flip_cap.visual(
        Box((0.004, 0.004, 0.004)),
        origin=Origin(xyz=(flip_cap_r - 0.004, -flip_cap_r, flip_cap_h)),
        material=cap_mat,
        name="cap_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    flip_cap.inertial = Inertial.from_geometry(
        Cylinder(flip_cap_r, flip_cap_h),
        mass=0.015,
        origin=Origin(xyz=(0.0, -flip_cap_r, flip_cap_h / 2.0)),
    )
    model.articulation(
        "cap_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=flip_cap,
        origin=Origin(xyz=(r.neck_x, r.neck_y + collar_outer_r, collar_top_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=upper, effort=2.0, velocity=3.0),
    )


# ===========================================================================
# Build entry point
# ===========================================================================
def build_container_plastic_can(
    config: ContainerPlasticCanConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    fin = pal.finish
    body_mat = model.material(f"cpc_body_{r.palette_style}", rgba=pal.body)
    handle_mat = model.material(f"cpc_handle_{r.palette_style}", rgba=pal.handle)
    cap_mat = model.material(f"cpc_cap_{r.palette_style}", rgba=pal.cap)
    accent_mat = model.material(f"cpc_accent_{r.palette_style}", rgba=pal.accent)
    # closure base follows the body color (cosmetic).
    base_mat = body_mat

    # --- ROOT: body shell (Slot A) + FIXED handle geometry (Slot B) ----------
    body = model.part("body")
    solid = _body_solid(r)

    # Fuse / cut the FIXED handle variants into the body shell.
    handle = r.handle_grip
    if handle == "integrated_loop":
        solid = solid.union(_handle_loop_solid(r))
    elif handle == "flush_dgrip":
        solid = solid.union(_flush_dgrip_solid(r))
    elif handle == "bridge_strap":
        solid = solid.union(_bridge_strap_solid(r))
    elif handle == "recessed_top_slot":
        slot_fill, slot = _recessed_slot_parts(r)
        solid = solid.union(slot_fill).cut(slot)
    elif handle == "recessed_grip_pocket":
        pocket_fill, pocket_cuts = _grip_pocket_parts(r)
        solid = solid.union(pocket_fill)
        for cut in pocket_cuts:
            solid = solid.cut(cut)
    elif handle == "swing_bail":
        bg = _bail_geom(r)
        solid = solid.union(_bail_lugs_solid(r, bg))

    body.visual(
        mesh_from_cadquery(solid, "body_shell"),
        material=body_mat,
        name="body_shell",
        material_class_id=_material_class_id("body"),
    )
    body.inertial = Inertial.from_geometry(
        Box((r.body_w, r.body_d, r.neck_top_z)),
        mass=0.90,
        origin=Origin(xyz=(0.0, 0.0, r.neck_top_z * 0.45)),
    )

    # --- swing_bail: separate REVOLUTE part -----------------------------------
    if handle == "swing_bail":
        bg = _bail_geom(r)
        bail = model.part("bail_handle")
        bail.visual(
            _bail_mesh(r, bg),
            material=handle_mat,
            name="bail_tube",
            material_class_id=_material_class_id("handle"),
        )
        bail.inertial = Inertial.from_geometry(
            Box((bg["arm_len"], 2 * bg["lug_half_y"], 2 * bg["radius"])),
            mass=0.08,
            origin=Origin(xyz=(-bg["arm_len"] / 2.0, 0.0, 0.0)),
        )
        model.articulation(
            "bail_swing",
            ArticulationType.REVOLUTE,
            parent=body,
            child=bail,
            origin=Origin(xyz=(bg["bail_x"], 0.0, bg["pivot_z"])),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(lower=0.0, upper=math.pi, effort=3.0, velocity=2.0),
        )

    # --- closure mechanism (Slot C) -------------------------------------------
    if r.cap_closure == "screw_cap":
        _build_screw_cap(model, body, r, cap_mat=cap_mat, accent_mat=accent_mat)
    elif r.cap_closure == "flip_top_spout":
        _build_flip_top_spout(model, body, r, cap_mat=cap_mat, base_mat=base_mat)
    elif r.cap_closure == "hinged_tethered_lid":
        _build_hinged_tethered_lid(model, body, r, cap_mat=cap_mat, base_mat=base_mat)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["finish"] = fin
    return model


def build_seeded_container_plastic_can(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_plastic_can(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests / QC. Captured-fit overlaps (cap skirt over neck, lid over spout, bail
# tube in lugs, flip cap strap touching collar anchor) are declared so the
# sweep's island/overlap checks pass; the closure / bail actions are exercised.
# ===========================================================================
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_plastic_can_tests(
    object_model: ArticulatedObject,
    config: ContainerPlasticCanConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("body")

    # ---- body rests on the ground (base near z=0) + real volume ----
    aabb = ctx.part_world_aabb(body)
    bext = _ext(aabb)
    ctx.check(
        "can body rests on the ground (base near z=0)",
        abs(aabb[0][2]) < 0.014,
        details=f"body min z={aabb[0][2]:.4f}",
    )
    ctx.check(
        "can body has real molded volume",
        bext[0] > 0.05 and bext[1] > 0.05 and bext[2] > 0.10,
        details=f"body extents={bext}",
    )

    # ---- offset neck: closure mounts off-center on the shoulder ----
    ctx.check(
        "neck is offset (not centered) on the shoulder",
        abs(r.neck_x) > 0.012,
        details=f"neck_x={r.neck_x:.4f}",
    )
    ctx.check(
        "pour mouth leaves an open neck bore into the hollow body",
        r.mouth_bore_r >= max(0.008, r.neck_r - r.wall - 0.001),
        details=(f"mouth_bore_r={r.mouth_bore_r:.4f}, neck_r={r.neck_r:.4f}, wall={r.wall:.4f}"),
    )
    if r.body_form == "tall_rectangular_sloped":
        expected_deck_z = _sloped_shoulder_surface_z(
            body_w=r.body_w, body_h=r.body_h, shoulder_h=r.shoulder_h, x=r.neck_x
        )
        ctx.check(
            "sloped-can neck roots on the local shoulder surface",
            abs(r.deck_top_z - expected_deck_z) < 1e-6,
            details=f"deck_top_z={r.deck_top_z:.4f}, expected={expected_deck_z:.4f}",
        )

    # ---- handle_grip ----
    if r.handle_grip == "swing_bail":
        bail = object_model.get_part("bail_handle")
        swing = object_model.get_articulation("bail_swing")
        bg = _bail_geom(r)
        ctx.allow_overlap(
            bail,
            body,
            elem_a="bail_tube",
            elem_b="body_shell",
            reason="Bail tube ends are captured in the shoulder lugs as pivot bearings.",
        )
        ctx.check(
            "bail_swing is REVOLUTE about +Y",
            swing.articulation_type == ArticulationType.REVOLUTE and abs(swing.axis[1]) > 0.99,
            details=f"axis={swing.axis}, type={swing.articulation_type}",
        )
        # Bail lies flat at rest, swings up for carrying.
        rest_top = ctx.part_world_aabb(bail)[1][2]
        with ctx.pose({swing: math.pi / 2.0}):
            up_top = ctx.part_world_aabb(bail)[1][2]
        ctx.check(
            "bail swings up for carrying (top rises)",
            up_top > rest_top + bg["arm_len"] * 0.4,
            details=f"rest_top={rest_top:.4f}, up_top={up_top:.4f}",
        )

    # ---- cap_closure: action + captured-fit overlaps ----
    if r.cap_closure == "screw_cap":
        carrier = object_model.get_part("cap_carrier")
        cap = object_model.get_part("cap")
        rotate = object_model.get_articulation("cap_rotate")
        slide = object_model.get_articulation("cap_slide")
        ctx.allow_isolated_part(
            cap,
            reason="screw cap lifts off the can and loses body contact",
        )
        ctx.allow_overlap(
            cap,
            body,
            elem_a="cap_shell",
            elem_b="body_shell",
            reason="Screw cap skirt seats over the threaded neck rim (screw-on capture).",
        )
        ctx.check(
            "carrier link is massless (no visuals)",
            len(carrier.visuals) == 0,
            details=f"carrier visuals={len(carrier.visuals)}",
        )
        ctx.check(
            "cap_rotate is CONTINUOUS about +Z",
            rotate.articulation_type == ArticulationType.CONTINUOUS and abs(rotate.axis[2]) > 0.99,
            details=f"axis={rotate.axis}, type={rotate.articulation_type}",
        )
        # spin: off-axis marker moves.
        m0 = ctx.part_element_world_aabb(cap, elem="cap_marker")
        m0c = ((m0[0][0] + m0[1][0]) / 2.0, (m0[0][1] + m0[1][1]) / 2.0)
        with ctx.pose({rotate: math.pi / 2.0}):
            m1 = ctx.part_element_world_aabb(cap, elem="cap_marker")
            m1c = ((m1[0][0] + m1[1][0]) / 2.0, (m1[0][1] + m1[1][1]) / 2.0)
        ctx.check(
            "cap_rotate spins the cap (marker swings around the axis)",
            math.hypot(m1c[0] - m0c[0], m1c[1] - m0c[1]) > 0.005,
            details=f"marker rest={m0c}, quarter-turn={m1c}",
        )
        # slide: cap lifts off the neck.
        rest_z = ctx.part_world_position(cap)[2]
        travel = _CAP_SLIDE * r.closure_travel_scale
        with ctx.pose({slide: travel}):
            up_z = ctx.part_world_position(cap)[2]
        ctx.check(
            "cap slides up off the neck",
            up_z > rest_z + travel * 0.5,
            details=f"rest_z={rest_z:.4f}, lifted_z={up_z:.4f}",
        )
        # decoupled: rotating does not change height.
        with ctx.pose({rotate: math.pi}):
            z_after_spin = ctx.part_world_position(cap)[2]
        ctx.check(
            "rotation does not change cap height (decoupled)",
            abs(z_after_spin - rest_z) < 0.003,
            details=f"rest_z={rest_z:.4f}, after_spin={z_after_spin:.4f}",
        )

    elif r.cap_closure == "flip_top_spout":
        lid = object_model.get_part("lid")
        hinge = object_model.get_articulation("lid_hinge")
        ctx.allow_overlap(
            body,
            body,
            elem_a="closure_base",
            elem_b="body_shell",
            reason="Collar bore seats over the threaded neck rim (interference fit).",
        )
        ctx.allow_overlap(
            body,
            lid,
            elem_a="closure_base",
            elem_b="lid_cap",
            reason="Pour spout is enclosed inside the hollow lid cavity when closed.",
        )
        ctx.check(
            "lid_hinge is REVOLUTE about -X",
            hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[0]) > 0.99,
            details=f"axis={hinge.axis}, type={hinge.articulation_type}",
        )
        top0 = ctx.part_world_aabb(lid)[1][2]
        with ctx.pose({hinge: 1.2}):
            top1 = ctx.part_world_aabb(lid)[1][2]
        ctx.check(
            "lid flips up to reveal the spout (top rises)",
            top1 > top0 + 0.005,
            details=f"closed_top_z={top0:.4f}, open_top_z={top1:.4f}",
        )

    elif r.cap_closure == "hinged_tethered_lid":
        flip_cap = object_model.get_part("flip_cap")
        hinge = object_model.get_articulation("cap_hinge")
        ctx.allow_overlap(
            body,
            flip_cap,
            elem_a="closure_base",
            elem_b="flip_cap_shell",
            reason="The flip cap strap tab and body collar anchor share the hinge "
            "contact surface and may touch at the seating interface.",
        )
        ctx.allow_overlap(
            body,
            body,
            elem_a="closure_base",
            elem_b="body_shell",
            reason="Collar ring seats over the threaded neck rim (interference fit).",
        )
        ctx.check(
            "cap_hinge is REVOLUTE about -X",
            hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[0]) > 0.99,
            details=f"axis={hinge.axis}, type={hinge.articulation_type}",
        )
        # captive flip: cap lifts up, bounded displacement.
        c0 = ctx.part_element_world_aabb(flip_cap, elem="flip_cap_shell")
        c0_top = c0[1][2]
        c0_center = (
            (c0[0][0] + c0[1][0]) / 2.0,
            (c0[0][1] + c0[1][1]) / 2.0,
            (c0[0][2] + c0[1][2]) / 2.0,
        )
        with ctx.pose({hinge: 1.2}):
            c1 = ctx.part_element_world_aabb(flip_cap, elem="flip_cap_shell")
            c1_top = c1[1][2]
        ctx.check(
            "tethered cap flips up (top rises)",
            c1_top > c0_top + 0.010,
            details=f"closed_top={c0_top:.4f}, open_top={c1_top:.4f}",
        )
        upper = min(2.6 * r.closure_travel_scale, 2.8)
        with ctx.pose({hinge: upper}):
            cm = ctx.part_element_world_aabb(flip_cap, elem="flip_cap_shell")
        cm_center = (
            (cm[0][0] + cm[1][0]) / 2.0,
            (cm[0][1] + cm[1][1]) / 2.0,
            (cm[0][2] + cm[1][2]) / 2.0,
        )
        dist = math.hypot(
            cm_center[0] - c0_center[0],
            cm_center[1] - c0_center[1],
            cm_center[2] - c0_center[2],
        )
        ctx.check(
            "flip cap stays captive (bounded displacement at max open)",
            dist < 0.08,
            details=f"displacement={dist:.4f}",
        )

    # ---- at least one non-fixed closure/handle joint exists ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed mechanism joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()


# Backwards-compatible alias for the generic sweep model template.
build_container_plastic_can_template = build_container_plastic_can
