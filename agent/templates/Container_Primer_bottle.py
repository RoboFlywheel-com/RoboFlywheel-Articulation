# SPDX-License-Identifier: Apache-2.0

"""Container primer bottle — modular procedural template (cosmetic primer bottle).

Category identity: a slim, upright cosmetic primer / makeup-base bottle. A
hollow slim body (ROOT ``body``) rests on z=0 with its axis along +Z; a single
applicator / dispensing closure caps the neck and articulates by one of several
mechanisms (the main motion). No multiplicity axis — one bottle, one closure.

Two parallel-children slots (spec ``Container_Primer_bottle.md``):

  * ``body_form`` (4) — the ROOT ``body`` mesh cross-section family:
      - cushion_squircle (baseline): heavily-filleted rect ("cushion") extrude
        + rect shoulder loft + rect neck collar.
      - square_prism: near-sharp rect (fillet≈0.0008) crisp edges, fuller
        shoulder base.
      - round_cylinder: circle().extrude() tube + conical circle-loft shoulder
        + round neck.
      - oval_section: ellipse(rx>ry).extrude() (wide X, shallow Y) + ellipse
        loft shoulder + ellipse neck + base rim lip.
    All carry inline ``gold_band`` + ``label_plate`` fixed visuals.
  * ``closure_mechanism`` (7) — the dispensing closure (>=1 non-fixed joint):
      - airless_press_pump: flat puck actuator, ``pump_press`` PRISMATIC -Z.
      - side_lever_pump: curved lever arm, ``lever_swing`` REVOLUTE -X swing
        (+ body-inline pump_housing + fork_post pair).
      - screw_twist_cap: threaded cap + 16 grip ribs, ``body_to_cap`` REVOLUTE +Z.
      - dropper_cap: collar + lathe squeeze bulb + glass pipette, ``dropper_lift``
        PRISMATIC +Z pull-out.
      - spray_atomizer: finger-pad head + side nozzle, ``spray_press`` PRISMATIC -Z.
      - flip_top_disc: hinged flip disc, ``cap_hinge`` REVOLUTE +X (+ body-inline
        cap_base).
      - treatment_spout_pump: collar + stem + gooseneck sweep spout,
        ``pump_press`` PRISMATIC -Z.

The closure skirt/collar/cap bore is derived per body_form via
``neck_bore_section(body_form)`` (rect bore for cushion/square, circle bore for
round, ellipse bore for oval) so the captured-fit over the neck never gaps or
clips.

Continuous size/proportion variation (height/width/neck/closure/travel scales)
lives in ``resolve_config`` as clamped params, never as slot candidates.
``palette_style`` (9 coordinated colorways × material-finish, with alpha<1 for
frosted/clear/amber) is sampled per seed and drives every ``.visual(material=)``;
it never counts toward slot_choices.

Sources (arti-template ``data/records`` 5-star pool, 1 parent + 9 qwen forks):
parent ``ec0caf66`` (cushion + airless pump), ``var_square_body``,
``var_round_body``, ``var_oval_body`` (body forms); ``var_lever_pump``,
``var_twist_cap``, ``var_dropper_cap``, ``var_spray_atomizer``, ``var_flip_top``,
``var_treatment_spout`` (closures).

Canonical spec:
``articraft_template_authoring/specs_modular_v1/Container_Primer_bottle.md``
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq
from cadquery.func import (
    circle as func_circle,
    face as func_face,
    spline as func_spline,
    sweep as func_sweep,
)

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
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyForm = Literal[
    "cushion_squircle",
    "square_prism",
    "round_cylinder",
    "oval_section",
]
ClosureMechanism = Literal[
    "airless_press_pump",
    "side_lever_pump",
    "screw_twist_cap",
    "dropper_cap",
    "spray_atomizer",
    "flip_top_disc",
    "treatment_spout_pump",
]
PaletteStyle = Literal[
    "matte_black_gold",
    "frosted_glass_gold",
    "clear_gloss_glass_silver",
    "soft_touch_taupe",
    "brushed_metallic_champagne",
    "pearlescent_blush_rosegold",
    "opaque_white_gold",
    "amber_apothecary",
    "two_tone_sage_gold",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "cushion_squircle",
    "square_prism",
    "round_cylinder",
    "oval_section",
)
CLOSURE_MECHANISMS: tuple[ClosureMechanism, ...] = (
    "airless_press_pump",
    "side_lever_pump",
    "screw_twist_cap",
    "dropper_cap",
    "spray_atomizer",
    "flip_top_disc",
    "treatment_spout_pump",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "matte_black_gold",
    "frosted_glass_gold",
    "clear_gloss_glass_silver",
    "soft_touch_taupe",
    "brushed_metallic_champagne",
    "pearlescent_blush_rosegold",
    "opaque_white_gold",
    "amber_apothecary",
    "two_tone_sage_gold",
)

# ---------------------------------------------------------------------------
# Palettes: 9 coordinated colorways x material-finish dimension.
#   body   -> body_shell
#   closure-> pump / cap / dropper / spray / lever / gooseneck
#   accent -> gold_band / label_plate / collar / grip ribs
# frosted / clear-gloss / amber carry alpha<1 (translucent finishes); the rest
# are opaque (alpha=1.0) and differ by hue + finish (metallic/pearlescent/etc).
# rgba anchored on the 5-star measured values + primer real colorway families.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "matte_black_gold": {
        "body": (0.08, 0.08, 0.09, 1.0),
        "closure": (0.05, 0.05, 0.06, 1.0),
        "accent": (0.80, 0.62, 0.22, 1.0),
    },
    "frosted_glass_gold": {
        "body": (0.86, 0.74, 0.46, 0.78),
        "closure": (0.78, 0.60, 0.24, 1.0),
        "accent": (0.80, 0.62, 0.22, 1.0),
    },
    "clear_gloss_glass_silver": {
        "body": (0.85, 0.88, 0.90, 0.55),
        "closure": (0.78, 0.80, 0.82, 1.0),
        "accent": (0.75, 0.76, 0.78, 1.0),
    },
    "soft_touch_taupe": {
        "body": (0.55, 0.50, 0.46, 1.0),
        "closure": (0.10, 0.10, 0.12, 1.0),
        "accent": (0.80, 0.62, 0.22, 1.0),
    },
    "brushed_metallic_champagne": {
        "body": (0.72, 0.66, 0.52, 1.0),
        "closure": (0.58, 0.52, 0.40, 1.0),
        "accent": (0.84, 0.66, 0.26, 1.0),
    },
    "pearlescent_blush_rosegold": {
        "body": (0.90, 0.66, 0.62, 1.0),
        "closure": (0.78, 0.55, 0.45, 1.0),
        "accent": (0.80, 0.58, 0.48, 1.0),
    },
    "opaque_white_gold": {
        "body": (0.95, 0.95, 0.93, 1.0),
        "closure": (0.80, 0.62, 0.22, 1.0),
        "accent": (0.80, 0.62, 0.22, 1.0),
    },
    "amber_apothecary": {
        "body": (0.45, 0.30, 0.18, 0.72),
        "closure": (0.30, 0.22, 0.14, 1.0),
        "accent": (0.78, 0.60, 0.24, 1.0),
    },
    "two_tone_sage_gold": {
        "body": (0.62, 0.68, 0.58, 1.0),
        "closure": (0.30, 0.36, 0.30, 1.0),
        "accent": (0.84, 0.66, 0.26, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Base geometry per body form (meters). Scaled per-build by resolve_config.
# Nominal half-widths/radii so the slim inequality (footprint < 0.045,
# height > footprint + 0.030) holds across the width/height scale ranges.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _FormGeom:
    # Cross-section nominal dimensions (full widths for rect, radii for round/oval).
    body_w: float  # full X extent of the main body footprint
    body_d: float  # full Y extent of the main body footprint
    body_h: float  # body height (below shoulder)
    fillet: float  # vertical edge fillet (rect forms); 0 for round/oval
    shoulder_h: float
    shoulder_top_w: float
    shoulder_top_d: float
    neck_w: float  # full X of neck collar footprint
    neck_d: float  # full Y of neck collar footprint
    neck_h: float
    section: Literal["rect", "circle", "ellipse"]


# Cushion / square share the cushion footprint; only fillet + shoulder base differ.
_FORMS: dict[BodyForm, _FormGeom] = {
    "cushion_squircle": _FormGeom(
        body_w=0.034, body_d=0.024, body_h=0.086, fillet=0.008,
        shoulder_h=0.006, shoulder_top_w=0.020, shoulder_top_d=0.016,
        neck_w=0.018, neck_d=0.014, neck_h=0.006, section="rect",
    ),
    "square_prism": _FormGeom(
        body_w=0.034, body_d=0.024, body_h=0.086, fillet=0.0008,
        shoulder_h=0.006, shoulder_top_w=0.020, shoulder_top_d=0.016,
        neck_w=0.018, neck_d=0.014, neck_h=0.006, section="rect",
    ),
    "round_cylinder": _FormGeom(
        body_w=0.030, body_d=0.030, body_h=0.086, fillet=0.0,
        shoulder_h=0.008, shoulder_top_w=0.020, shoulder_top_d=0.020,
        neck_w=0.018, neck_d=0.018, neck_h=0.006, section="circle",
    ),
    "oval_section": _FormGeom(
        body_w=0.038, body_d=0.022, body_h=0.086, fillet=0.0,
        shoulder_h=0.008, shoulder_top_w=0.020, shoulder_top_d=0.016,
        neck_w=0.018, neck_d=0.014, neck_h=0.006, section="ellipse",
    ),
}

GOLD_BAND_Z = 0.050
GOLD_BAND_H = 0.005


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ContainerPrimerBottleConfig:
    body_form: BodyForm = "cushion_squircle"
    closure_mechanism: ClosureMechanism = "airless_press_pump"
    palette_style: PaletteStyle = "matte_black_gold"
    body_height_scale: float = 1.0
    body_width_scale: float = 1.0
    neck_scale: float = 1.0
    closure_size_scale: float = 1.0
    joint_travel_scale: float = 1.0
    name: str = "container_primer_bottle"


@dataclass(frozen=True)
class ResolvedContainerPrimerBottleConfig:
    body_form: BodyForm
    closure_mechanism: ClosureMechanism
    palette_style: PaletteStyle
    body_height_scale: float
    body_width_scale: float
    neck_scale: float
    closure_size_scale: float
    joint_travel_scale: float
    section: Literal["rect", "circle", "ellipse"]
    # derived body geometry
    body_w: float
    body_d: float
    body_h: float
    fillet: float
    shoulder_h: float
    shoulder_top_w: float
    shoulder_top_d: float
    neck_w: float
    neck_d: float
    neck_h: float
    neck_top_z: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerPrimerBottleConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    return ContainerPrimerBottleConfig(
        body_form=rng.choice(BODY_FORMS),
        closure_mechanism=rng.choice(CLOSURE_MECHANISMS),
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.85, 1.20), 4),
        body_width_scale=round(rng.uniform(0.88, 1.15), 4),
        neck_scale=round(rng.uniform(0.90, 1.10), 4),
        closure_size_scale=round(rng.uniform(0.85, 1.15), 4),
        joint_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_primer_bottle_{seed}",
    )


def resolve_config(
    config: ContainerPrimerBottleConfig | None = None,
) -> ResolvedContainerPrimerBottleConfig:
    cfg = config or ContainerPrimerBottleConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    closure = _pick(cfg.closure_mechanism, CLOSURE_MECHANISMS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    g = _FORMS[body_form]
    h_scale = _clamp(cfg.body_height_scale, 0.85, 1.20)
    w_scale = _clamp(cfg.body_width_scale, 0.88, 1.15)
    n_scale = _clamp(cfg.neck_scale, 0.90, 1.10)
    c_scale = _clamp(cfg.closure_size_scale, 0.85, 1.15)
    jt_scale = _clamp(cfg.joint_travel_scale, 0.85, 1.10)

    body_w = g.body_w * w_scale
    body_d = g.body_d * w_scale
    body_h = g.body_h * h_scale

    # Slim inequality projection: keep footprint strictly slim and height
    # dominant. footprint < 0.045 and height > footprint + 0.030.
    max_foot = max(body_w, body_d)
    if max_foot >= 0.044:
        shrink = 0.044 / max_foot
        body_w *= shrink
        body_d *= shrink
        max_foot = max(body_w, body_d)
    if body_h <= max_foot + 0.032:
        body_h = max_foot + 0.034

    # Neck collar footprint follows the body width scale and neck scale, but is
    # clamped to stay strictly inside the shoulder top so the closure bore
    # (derived from the neck) always seats. neck_scale is the equation knob.
    neck_w = _clamp(g.neck_w * w_scale * n_scale, 0.012, min(g.shoulder_top_w, body_w) - 0.001)
    neck_d = _clamp(g.neck_d * w_scale * n_scale, 0.010, min(g.shoulder_top_d, body_d) - 0.001)
    shoulder_h = g.shoulder_h
    neck_h = g.neck_h
    neck_top_z = body_h + shoulder_h + neck_h

    # Shoulder top follows the neck footprint so the loft always tapers inward.
    shoulder_top_w = max(neck_w + 0.002, g.shoulder_top_w * w_scale)
    shoulder_top_w = min(shoulder_top_w, body_w - 0.001)
    shoulder_top_d = max(neck_d + 0.002, g.shoulder_top_d * w_scale)
    shoulder_top_d = min(shoulder_top_d, body_d - 0.001)

    return ResolvedContainerPrimerBottleConfig(
        body_form=body_form,
        closure_mechanism=closure,
        palette_style=palette,
        body_height_scale=h_scale,
        body_width_scale=w_scale,
        neck_scale=n_scale,
        closure_size_scale=c_scale,
        joint_travel_scale=jt_scale,
        section=g.section,
        body_w=body_w,
        body_d=body_d,
        body_h=body_h,
        fillet=g.fillet,
        shoulder_h=shoulder_h,
        shoulder_top_w=shoulder_top_w,
        shoulder_top_d=shoulder_top_d,
        neck_w=neck_w,
        neck_d=neck_d,
        neck_h=neck_h,
        neck_top_z=neck_top_z,
        name=cfg.name or "container_primer_bottle",
    )


def with_overrides(
    config: ContainerPrimerBottleConfig, **kwargs: object
) -> ContainerPrimerBottleConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerPrimerBottleConfig | ResolvedContainerPrimerBottleConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedContainerPrimerBottleConfig)
        else resolve_config(config)
    )
    return (
        ("body_form", r.body_form),
        ("closure_mechanism", r.closure_mechanism),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared geometry primitives
# ---------------------------------------------------------------------------
def _rounded_prism(w: float, d: float, h: float, fillet: float, z0: float = 0.0) -> cq.Workplane:
    """Upright rounded-rectangle prism: footprint w(X) x d(Y), height h, base z0."""
    f = min(fillet, 0.49 * min(w, d))
    wp = cq.Workplane("XY").workplane(offset=z0).rect(w, d).extrude(h)
    if f > 1e-5:
        wp = wp.edges("|Z").fillet(f)
    return wp


def _cylinder(radius: float, h: float, z0: float = 0.0) -> cq.Workplane:
    return cq.Workplane("XY").workplane(offset=z0).circle(radius).extrude(h)


def _elliptical_prism(rx: float, ry: float, h: float, z0: float = 0.0) -> cq.Workplane:
    return cq.Workplane("XY").workplane(offset=z0).ellipse(rx, ry).extrude(h)


def neck_bore_section(body_form: BodyForm) -> str:
    """Return the bore-primitive family a closure skirt/collar/cap must use to
    seat over this body_form's neck collar (avoids clip / gap at the capture).

    rect bore   -> cushion / square (filleted/sharp rect neck)
    circle bore -> round cylinder (circular neck)
    ellipse bore-> oval section (elliptical neck)
    """
    return _FORMS[body_form].section


def _neck_bore_solid(
    r: ResolvedContainerPrimerBottleConfig,
    *,
    clearance: float,
    z0: float,
    depth: float,
) -> cq.Workplane:
    """A bore solid matching the neck cross-section (rect/circle/ellipse) with a
    small clearance, used to hollow the underside of a closure skirt so it grips
    the neck. Sized slightly under the neck footprint so the skirt captures it."""
    section = r.section
    if section == "circle":
        bore_r = r.neck_w / 2.0 - clearance
        return _cylinder(bore_r, depth, z0=z0)
    if section == "ellipse":
        rx = r.neck_w / 2.0 - clearance
        ry = r.neck_d / 2.0 - clearance
        return _elliptical_prism(rx, ry, depth, z0=z0)
    # rect bore
    return cq.Workplane("XY").workplane(offset=z0).rect(
        r.neck_w - 2 * clearance, r.neck_d - 2 * clearance
    ).extrude(depth)


def _neck_outer_radius(r: ResolvedContainerPrimerBottleConfig) -> float:
    """Effective outer half-extent of the neck (used to size round closures so
    they cover the neck footprint regardless of cross-section)."""
    return max(r.neck_w, r.neck_d) / 2.0


# Hollowing parameters: the bottle is ONE connected hollow shell. The inner
# cavity is cut from the body + shoulder and bored OPEN up through the neck mouth
# so the open interior is visible down the neck (no solid plug/slab under the
# mouth). BODY_WALL keeps an adequate wall on the body/shoulder; NECK_WALL keeps
# a thin, realistic neck wall so the bore reads as a wide open mouth. BASE_WALL
# leaves a closed solid bottom (the bottle stands on a real floor).
BODY_WALL = 0.0025
NECK_WALL = 0.0018
BASE_WALL = 0.003


def _neck_bore_radii(r: ResolvedContainerPrimerBottleConfig) -> tuple[float, float]:
    """Inner half-extents (X, Y) of the open neck bore for this body_form.

    The bore is the neck footprint inset by NECK_WALL, floored at a minimum so
    the mouth always reads as a clearly-open opening into the cavity. For the
    round neck both extents collapse to the same radius.
    """
    bore_x = max(r.neck_w / 2.0 - NECK_WALL, 0.0040)
    bore_y = max(r.neck_d / 2.0 - NECK_WALL, 0.0035)
    if r.section == "circle":
        bore_x = bore_y = max(r.neck_w / 2.0 - NECK_WALL, 0.0040)
    return bore_x, bore_y


def _neck_bore_top_z(r: ResolvedContainerPrimerBottleConfig) -> float:
    """Absolute z of the open neck rim (mouth) — the bore is cut up to here."""
    return r.neck_top_z


def _rect_shoulder_base(r: ResolvedContainerPrimerBottleConfig) -> tuple[float, float]:
    """Full (w, d) of the rect shoulder loft base at z=body_h (mirrors
    ``_rect_body_solid``). The cavity must stay inside this so the shoulder/neck
    stays connected to the body."""
    if r.fillet >= 0.004:
        return r.body_w - 2 * r.fillet + 0.004, r.body_d - 2 * r.fillet + 0.004
    return r.body_w - 0.002, r.body_d - 0.002


def _cavity_solid(r: ResolvedContainerPrimerBottleConfig) -> cq.Workplane:
    """Inner cavity cut from the body to make ONE connected hollow shell with an
    OPEN mouth. Three stacked, fused inner volumes:

      * body cavity (loft): inset from the body footprint at a floor (BASE_WALL
        above z=0, closed bottom) and tapering up to the shoulder-base footprint
        inset by BODY_WALL at body_h. The loft tracks the shoulder step so the
        cavity never breaches the side wall and the shell stays connected.
      * neck/shoulder bore: a narrow column at the open-neck-bore footprint (neck
        inset by NECK_WALL) from just below body_h up THROUGH the rim (a hair
        above neck_top_z). Narrower than the shoulder, so the shoulder stays a
        connected dome pierced by one central bore — the mouth is bored fully open
        (no solid plug/slab under the mouth; the cavity is visible down the neck).

    The volumes overlap in z so the void is a single connected volume; cutting it
    leaves one connected shell (no islands).
    """
    section = r.section
    floor_z = BASE_WALL
    body_top = r.body_h
    bore_x, bore_y = _neck_bore_radii(r)
    # Neck/shoulder bore: from just below body_h up past the rim (open mouth).
    neck_bore_z0 = body_top - 0.002
    neck_bore_h = (_neck_bore_top_z(r) + 0.001) - neck_bore_z0

    if section == "circle":
        bottom_r = max(r.body_w / 2.0 - BODY_WALL, bore_x)
        top_r = max(r.shoulder_top_w / 2.0 - BODY_WALL, bore_x)
        top_r = min(top_r, bottom_r)
        cavity = (
            cq.Workplane("XY")
            .workplane(offset=floor_z)
            .circle(bottom_r)
            .workplane(offset=body_top - floor_z)
            .circle(top_r)
            .loft(ruled=True)
        )
        cavity = cavity.union(_cylinder(bore_x, neck_bore_h, z0=neck_bore_z0))
        return cavity
    if section == "ellipse":
        bottom_rx = max(r.body_w / 2.0 - BODY_WALL, bore_x)
        bottom_ry = max(r.body_d / 2.0 - BODY_WALL, bore_y)
        top_rx = min(max(r.shoulder_top_w / 2.0 - BODY_WALL, bore_x), bottom_rx)
        top_ry = min(max(r.shoulder_top_d / 2.0 - BODY_WALL, bore_y), bottom_ry)
        cavity = (
            cq.Workplane("XY")
            .workplane(offset=floor_z)
            .ellipse(bottom_rx, bottom_ry)
            .workplane(offset=body_top - floor_z)
            .ellipse(top_rx, top_ry)
            .loft(ruled=True)
        )
        cavity = cavity.union(_elliptical_prism(bore_x, bore_y, neck_bore_h, z0=neck_bore_z0))
        return cavity
    # rect (cushion / square): loft from body-inset to shoulder-base-inset.
    bottom_w = max(r.body_w - 2 * BODY_WALL, 2 * bore_x)
    bottom_d = max(r.body_d - 2 * BODY_WALL, 2 * bore_y)
    base_w, base_d = _rect_shoulder_base(r)
    top_w = min(max(base_w - 2 * BODY_WALL, 2 * bore_x), bottom_w)
    top_d = min(max(base_d - 2 * BODY_WALL, 2 * bore_y), bottom_d)
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=floor_z)
        .rect(bottom_w, bottom_d)
        .workplane(offset=body_top - floor_z)
        .rect(top_w, top_d)
        .loft(ruled=True)
    )
    neck_bore = (
        cq.Workplane("XY")
        .workplane(offset=neck_bore_z0)
        .rect(2 * bore_x, 2 * bore_y)
        .extrude(neck_bore_h)
    )
    cavity = cavity.union(neck_bore)
    return cavity


# ---------------------------------------------------------------------------
# Body geometry (Slot A): dispatch on cross-section family.
# Each builder forms the solid outer shell (body + shoulder + neck collar) then
# cuts the inner cavity so the bottle is a single connected hollow shell with an
# open mouth bored down the neck.
# ---------------------------------------------------------------------------
def _body_solid(r: ResolvedContainerPrimerBottleConfig) -> cq.Workplane:
    section = r.section
    if section == "circle":
        body = _round_body_solid(r)
    elif section == "ellipse":
        body = _oval_body_solid(r)
    else:
        body = _rect_body_solid(r)
    return body.cut(_cavity_solid(r))


def _rect_body_solid(r: ResolvedContainerPrimerBottleConfig) -> cq.Workplane:
    """Cushion / square: filleted-rect extrude + rect shoulder loft + rect neck."""
    body = _rounded_prism(r.body_w, r.body_d, r.body_h, r.fillet, z0=0.0)
    # For near-sharp (square) the shoulder base sits closer to the full footprint;
    # for cushion it steps in by 2*fillet (parent behaviour).
    if r.fillet >= 0.004:
        base_w = r.body_w - 2 * r.fillet + 0.004
        base_d = r.body_d - 2 * r.fillet + 0.004
    else:
        base_w = r.body_w - 0.002
        base_d = r.body_d - 0.002
    shoulder = (
        cq.Workplane("XY")
        .workplane(offset=r.body_h)
        .rect(base_w, base_d)
        .workplane(offset=r.shoulder_h)
        .rect(r.shoulder_top_w, r.shoulder_top_d)
        .loft(ruled=True)
    )
    body = body.union(shoulder)
    neck_fillet = 0.003 if r.fillet >= 0.004 else 0.0008
    neck = _rounded_prism(r.neck_w, r.neck_d, r.neck_h, neck_fillet, z0=r.body_h + r.shoulder_h)
    body = body.union(neck)
    return body


def _round_body_solid(r: ResolvedContainerPrimerBottleConfig) -> cq.Workplane:
    """Round cylinder + conical circle-loft shoulder + round neck."""
    body_r = r.body_w / 2.0
    neck_r = r.neck_w / 2.0
    top_r = r.shoulder_top_w / 2.0
    body = _cylinder(body_r, r.body_h, z0=0.0)
    shoulder = (
        cq.Workplane("XY")
        .workplane(offset=r.body_h)
        .circle(body_r)
        .workplane(offset=r.shoulder_h)
        .circle(top_r)
        .loft(ruled=True)
    )
    body = body.union(shoulder)
    neck = _cylinder(neck_r, r.neck_h, z0=r.body_h + r.shoulder_h)
    body = body.union(neck)
    return body


def _oval_body_solid(r: ResolvedContainerPrimerBottleConfig) -> cq.Workplane:
    """Oval: ellipse extrude (wide X) + ellipse loft shoulder + ellipse neck + rim."""
    rx, ry = r.body_w / 2.0, r.body_d / 2.0
    top_rx, top_ry = r.shoulder_top_w / 2.0, r.shoulder_top_d / 2.0
    neck_rx, neck_ry = r.neck_w / 2.0, r.neck_d / 2.0
    body = _elliptical_prism(rx, ry, r.body_h, z0=0.0)
    shoulder = (
        cq.Workplane("XY")
        .workplane(offset=r.body_h)
        .ellipse(rx, ry)
        .workplane(offset=r.shoulder_h)
        .ellipse(top_rx, top_ry)
        .loft()
    )
    body = body.union(shoulder)
    neck = _elliptical_prism(neck_rx, neck_ry, r.neck_h, z0=r.body_h + r.shoulder_h)
    body = body.union(neck)
    rim = _elliptical_prism(rx + 0.0006, ry + 0.0006, 0.002, z0=0.0)
    body = body.union(rim)
    return body


def _gold_band_solid(r: ResolvedContainerPrimerBottleConfig) -> cq.Workplane:
    """Thin accent band wrapping the body at GOLD_BAND_Z, following the section."""
    z0 = GOLD_BAND_Z - GOLD_BAND_H / 2.0
    if r.section == "circle":
        return _cylinder(r.body_w / 2.0 + 0.0004, GOLD_BAND_H, z0=z0)
    if r.section == "ellipse":
        return _elliptical_prism(
            r.body_w / 2.0 + 0.0006, r.body_d / 2.0 + 0.0006, GOLD_BAND_H, z0=z0
        )
    return _rounded_prism(r.body_w + 0.0008, r.body_d + 0.0008, GOLD_BAND_H, r.fillet, z0=z0)


def _label_plate_solid(r: ResolvedContainerPrimerBottleConfig) -> cq.Workplane:
    """Raised label area on the front (+Y) face below the gold band ("PRIMER")."""
    z_bottom = 0.012
    z_top = GOLD_BAND_Z - GOLD_BAND_H / 2.0 - 0.002
    label_h = max(z_top - z_bottom, 0.004)
    if r.section == "circle":
        front_y = r.body_w / 2.0
        plate_w = r.body_w * 0.7
    elif r.section == "ellipse":
        front_y = r.body_d / 2.0
        plate_w = r.body_w * 0.65
    else:
        front_y = r.body_d / 2.0
        plate_w = r.body_w - 0.010
    return (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .center(0.0, front_y - 0.0005)
        .rect(plate_w, 0.0018)
        .extrude(label_h)
    )


def _emit_body(body, r: ResolvedContainerPrimerBottleConfig, *, body_mat, accent_mat) -> None:
    body.visual(
        mesh_from_cadquery(_body_solid(r), "body_shell"),
        material=body_mat,
        name="body_shell", material_class_id=("plastic.opaque_generic" if r.palette_style in {"matte_black_gold", "soft_touch_taupe", "brushed_metallic_champagne", "pearlescent_blush_rosegold", "opaque_white_gold", "two_tone_sage_gold"} else "glass.clear_transparent"),
    )
    body.visual(
        mesh_from_cadquery(_gold_band_solid(r), "gold_band"),
        material=accent_mat,
        name="gold_band", material_class_id=("metal.precious_gold" if r.palette_style in {"matte_black_gold", "frosted_glass_gold", "soft_touch_taupe", "brushed_metallic_champagne", "pearlescent_blush_rosegold", "opaque_white_gold", "amber_apothecary", "two_tone_sage_gold"} else "metal.chrome_polished"),
    )
    body.visual(
        mesh_from_cadquery(_label_plate_solid(r), "label_plate"),
        material=accent_mat,
        name="label_plate", material_class_id=("metal.precious_gold" if r.palette_style in {"matte_black_gold", "frosted_glass_gold", "soft_touch_taupe", "brushed_metallic_champagne", "pearlescent_blush_rosegold", "opaque_white_gold", "amber_apothecary", "two_tone_sage_gold"} else "metal.chrome_polished"),
    )
    body.inertial = Inertial.from_geometry(
        Box((r.body_w, r.body_d, r.body_h)),
        mass=0.090,
        origin=Origin(xyz=(0.0, 0.0, r.body_h / 2.0)),
    )


# ---------------------------------------------------------------------------
# Closure builders (Slot B). Each parents one closure to the root ``body``
# (parallel-children pattern). Geometry authored in absolute body-frame coords.
# ---------------------------------------------------------------------------
def _airless_pump_solid(r: ResolvedContainerPrimerBottleConfig) -> cq.Workplane:
    """Flat airless actuator: rounded-rect puck + hollow neck bore + top orifice."""
    c = r.closure_size_scale
    pump_w = 0.022 * c
    pump_d = 0.018 * c
    pump_h = 0.020 * c
    seat = 0.004
    z0 = r.neck_top_z - seat
    cap = _rounded_prism(pump_w, pump_d, pump_h, 0.004, z0=z0)
    # Bore floor just below the neck top: the puck interior ceiling rests flat on
    # the neck rim (solid Z contact); side walls grip the neck.
    bore_depth = (r.neck_top_z - 0.0015) - (z0 - 0.002)
    bore = _neck_bore_solid(r, clearance=0.0006, z0=z0 - 0.002, depth=bore_depth)
    cap = cap.cut(bore)
    # NO centerline plug: the neck is bored OPEN (visible cavity). The puck ceiling
    # rests flat on the neck rim ring (solid Z contact) + skirt walls grip the neck
    # walls, which is the real captured-fit contact; nothing descends into the mouth.
    hole = _cylinder(0.0016, 0.006, z0=z0 + pump_h - 0.005)
    cap = cap.cut(hole)
    return cap


def _build_airless_pump(model, body, r, *, closure_mat) -> None:
    c = r.closure_size_scale
    pump_h = 0.020 * c
    travel = 0.006 * r.joint_travel_scale
    z0 = r.neck_top_z - 0.004
    zr = r.neck_top_z  # joint origin / local-frame datum (neck rim top)
    pump = model.part("pump_top")
    # Author absolute, then shift to the neck-rim-local frame so local z=0 (the
    # joint origin) lies inside the child geometry (origin-far check) while the
    # joint origin at (0,0,zr) restores the absolute placement.
    pump.visual(
        mesh_from_cadquery(_airless_pump_solid(r).translate((0.0, 0.0, -zr)), "pump_cap"),
        material=closure_mat,
        name="pump_cap", material_class_id=("plastic.opaque_generic" if r.palette_style in {"matte_black_gold", "soft_touch_taupe", "amber_apothecary", "two_tone_sage_gold"} else "metal.precious_gold"),
    )
    pump.inertial = Inertial.from_geometry(
        Box((0.022 * c, 0.018 * c, pump_h)),
        mass=0.010,
        origin=Origin(xyz=(0.0, 0.0, z0 + pump_h / 2.0 - zr)),
    )
    model.articulation(
        "pump_press",
        ArticulationType.PRISMATIC,
        parent=body,
        child=pump,
        # Origin on the real neck-top rim (real hardware, within both AABBs);
        # the child is authored in this same frame so only the +Z stroke moves.
        origin=Origin(xyz=(0.0, 0.0, zr)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.05, lower=-travel, upper=0.0),
    )


def _build_spray_atomizer(model, body, r, *, closure_mat) -> None:
    """Fine-mist head: cylinder actuator + dome + neck bore + side +Y nozzle."""
    c = r.closure_size_scale
    head_d = 0.022 * c
    head_h = 0.022 * c
    seat = 0.004
    travel = 0.006 * r.joint_travel_scale
    z0 = r.neck_top_z - seat
    head_r = head_d / 2.0

    head = _cylinder(head_r, head_h, z0=z0)
    dome = _cylinder(head_r, 0.003, z0=z0 + head_h)
    try:
        dome = dome.edges(">Z").fillet(0.002)
    except Exception:
        pass
    head = head.union(dome)
    # Bore floor just below the neck top so the head ceiling rests flat on the
    # neck rim (solid Z contact) and the skirt grips the neck sides.
    bore_depth = (r.neck_top_z - 0.0015) - (z0 - 0.002)
    bore = _neck_bore_solid(r, clearance=0.0005, z0=z0 - 0.002, depth=bore_depth)
    head = head.cut(bore)
    # NO centerline plug: the neck is bored OPEN. The head ceiling rests flat on
    # the neck rim ring + skirt grips the neck walls (real captured-fit contact).

    # Side nozzle: a real horizontal tube along +Y, reaching past the body front
    # face so the directional mist orifice clears the bottle on every body_form.
    # CadQuery "XZ" workplane normal = -Y, so a positive extrude goes toward -Y;
    # we author from the tip back toward the head with a negated start offset.
    nozzle_z = z0 + 0.008 * c
    nozzle_start_y = head_r - 0.001  # begin just inside the head wall
    # Body front half-extent (Y) per section, plus a clearance margin.
    if r.section == "circle":
        body_front_y = r.body_w / 2.0
    else:
        body_front_y = r.body_d / 2.0
    nozzle_tip_y = max(nozzle_start_y + 0.013 * c, body_front_y + 0.005)
    nozzle = (
        cq.Workplane("XZ")
        .workplane(offset=-nozzle_tip_y)  # -> y = +nozzle_tip_y (tip face)
        .center(0.0, nozzle_z)
        .circle(0.005 / 2.0)
        .extrude(nozzle_tip_y - nozzle_start_y)  # extrudes toward -Y back to head
    )
    head = head.union(nozzle)
    orifice = (
        cq.Workplane("XZ")
        .workplane(offset=-(nozzle_tip_y + 0.001))
        .center(0.0, nozzle_z)
        .circle(0.002 / 2.0)
        .extrude(0.004)
    )
    head = head.cut(orifice)

    zr = r.neck_top_z  # joint origin / local-frame datum (neck rim top)
    spray_head = model.part("spray_head")
    # Author absolute then shift to neck-rim-local frame (see airless note).
    spray_head.visual(
        mesh_from_cadquery(head.translate((0.0, 0.0, -zr)), "atomizer_head"),
        material=closure_mat,
        name="atomizer_head", material_class_id=("plastic.opaque_generic" if r.palette_style in {"matte_black_gold", "soft_touch_taupe", "amber_apothecary", "two_tone_sage_gold"} else "metal.precious_gold"),
    )
    spray_head.inertial = Inertial.from_geometry(
        Box((head_d, head_d, head_h)),
        mass=0.012,
        origin=Origin(xyz=(0.0, 0.0, z0 + head_h / 2.0 - zr)),
    )
    model.articulation(
        "spray_press",
        ArticulationType.PRISMATIC,
        parent=body,
        child=spray_head,
        # Origin on the real neck-top rim; child authored in this frame, +Z stroke.
        origin=Origin(xyz=(0.0, 0.0, zr)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.05, lower=-travel, upper=0.0),
    )


def _build_treatment_spout(model, body, r, *, closure_mat) -> None:
    """Tall gooseneck treatment pump: collar + stem + spline-swept spout + nozzle."""
    c = r.closure_size_scale
    seat = 0.004
    travel = 0.006 * r.joint_travel_scale
    collar_r = 0.010 * c
    collar_h = 0.012 * c
    stem_r = 0.005 * c
    stem_h = 0.018 * c
    spout_r = 0.003 * c
    nozzle_r = 0.0028 * c
    nozzle_h = 0.007 * c

    collar_z0 = r.neck_top_z - seat
    collar_top_z = collar_z0 + collar_h
    stem_top_z = collar_top_z + stem_h

    collar = _cylinder(collar_r, collar_h, z0=collar_z0)
    # Bore floor (collar interior ceiling) just below the neck top so the collar
    # rests as a flat Z-face on the neck rim (solid contact); side walls grip.
    bore_depth = (r.neck_top_z - 0.0015) - (collar_z0 - 0.002)
    bore = _neck_bore_solid(r, clearance=0.0005, z0=collar_z0 - 0.002, depth=bore_depth)
    collar = collar.cut(bore)
    # NO centerline plug: the neck is bored OPEN. The collar ceiling rests flat on
    # the neck rim ring + collar walls grip the neck walls (real captured-fit).
    collar_top_ring = (
        cq.Workplane("XY")
        .workplane(offset=collar_top_z - 0.001)
        .circle(collar_r + 0.001)
        .circle(collar_r - 0.001)
        .extrude(0.002)
    )
    collar = collar.union(collar_top_ring)

    stem = _cylinder(stem_r, stem_h, z0=collar_top_z)
    collar = collar.union(stem)

    # Gooseneck swept along a spline arching to +X then down.
    path_points = [
        (0.000, 0.0, stem_top_z),
        (0.004 * c, 0.0, stem_top_z + 0.008 * c),
        (0.014 * c, 0.0, stem_top_z + 0.013 * c),
        (0.025 * c, 0.0, stem_top_z + 0.008 * c),
        (0.031 * c, 0.0, stem_top_z - 0.002 * c),
        (0.032 * c, 0.0, stem_top_z - 0.016 * c),
    ]
    path_tangents = [(0.0, 0.0, 1.0), (0.0, 0.0, -1.0)]
    path_wire = func_spline(path_points, path_tangents)
    profile = func_face(func_circle(spout_r)).moved(z=stem_top_z)
    gooseneck = func_sweep(profile, path_wire)
    collar = collar.union(cq.Workplane("XY").newObject([gooseneck]))

    nozzle_end = path_points[-1]
    nozzle = (
        cq.Workplane("XY")
        .workplane(offset=nozzle_end[2] - nozzle_h)
        .center(nozzle_end[0], nozzle_end[1])
        .circle(nozzle_r)
        .extrude(nozzle_h + 0.001)
    )
    collar = collar.union(nozzle)
    orifice = (
        cq.Workplane("XY")
        .workplane(offset=nozzle_end[2] - nozzle_h - 0.001)
        .center(nozzle_end[0], nozzle_end[1])
        .circle(0.0012)
        .extrude(0.004)
    )
    collar = collar.cut(orifice)

    zr = r.neck_top_z  # joint origin / local-frame datum (neck rim top)
    pump_head = model.part("pump_head")
    # Author absolute then shift to neck-rim-local frame (see airless note).
    pump_head.visual(
        mesh_from_cadquery(collar.translate((0.0, 0.0, -zr)), "pump_head_shell"),
        material=closure_mat,
        name="pump_head_shell", material_class_id=("plastic.opaque_generic" if r.palette_style in {"matte_black_gold", "soft_touch_taupe", "amber_apothecary", "two_tone_sage_gold"} else "metal.precious_gold"),
    )
    pump_head.inertial = Inertial.from_geometry(
        Cylinder(radius=collar_r, length=collar_h + stem_h + 0.020),
        mass=0.015,
        origin=Origin(xyz=(0.0, 0.0, collar_z0 + (collar_h + stem_h) / 2.0 - zr)),
    )
    model.articulation(
        "pump_press",
        ArticulationType.PRISMATIC,
        parent=body,
        child=pump_head,
        # Origin on the real neck-top rim; child authored in this frame, +Z stroke.
        origin=Origin(xyz=(0.0, 0.0, zr)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.05, lower=-travel, upper=0.0),
    )


def _build_screw_twist_cap(model, body, r, *, closure_mat, accent_mat) -> None:
    """Threaded cylindrical screw cap + 16 grip ribs, REVOLUTE +Z unscrew."""
    c = r.closure_size_scale
    cap_od = max(0.024 * c, _neck_outer_radius(r) * 2.0 + 0.004)
    cap_h = 0.015 * c
    seat = 0.005
    n_ribs = 16
    rib_depth = 0.0008
    rib_width = 0.0015
    R = cap_od / 2.0
    z0 = r.neck_top_z - seat

    cap_solid = _cylinder(R, cap_h, z0=z0)
    # Bore floor (= cap interior ceiling) sits just BELOW the neck top so the
    # cap ceiling rests as a flat Z-face on the neck rim (solid contact) while
    # the bore side walls grip the neck (captured fit). Bore is sized under the
    # neck footprint so there is real volumetric interference, not a thin shell.
    bore_depth = (r.neck_top_z - 0.0015) - (z0 - 0.001)
    bore = _neck_bore_solid(r, clearance=0.0004, z0=z0 - 0.001, depth=bore_depth)
    cap_solid = cap_solid.cut(bore)
    # NO centerline plug: the neck is bored OPEN. The cap ceiling rests flat on the
    # neck rim ring + bore walls grip the neck walls (real captured-fit contact).
    boss = _cylinder(0.004, 0.001, z0=z0 + cap_h - 0.0005)
    cap_solid = cap_solid.union(boss)

    zr = r.neck_top_z  # joint origin / local-frame datum (neck rim top)
    cap = model.part("screw_cap")
    # Author absolute then shift to neck-rim-local frame so local z=0 (the +Z
    # revolute origin) lies inside the cap geometry; the joint origin restores it.
    cap.visual(
        mesh_from_cadquery(cap_solid.translate((0.0, 0.0, -zr)), "cap_shell"),
        material=closure_mat,
        name="cap_shell", material_class_id=("plastic.opaque_generic" if r.palette_style in {"matte_black_gold", "soft_touch_taupe", "amber_apothecary", "two_tone_sage_gold"} else "metal.precious_gold"),
    )
    for i in range(n_ribs):
        angle_deg = i * (360.0 / n_ribs)
        rib = (
            cq.Workplane("XY")
            .workplane(offset=z0 + 0.002)
            .transformed(rotate=(0, 0, angle_deg))
            .center(R, 0)
            .rect(rib_depth * 2, rib_width)
            .extrude(cap_h - 0.004)
            .translate((0.0, 0.0, -zr))
        )
        cap.visual(
            mesh_from_cadquery(rib, f"grip_rib_{i}"),
            material=accent_mat,
            name=f"grip_rib_{i}", material_class_id=("metal.precious_gold" if r.palette_style in {"matte_black_gold", "frosted_glass_gold", "soft_touch_taupe", "brushed_metallic_champagne", "pearlescent_blush_rosegold", "opaque_white_gold", "amber_apothecary", "two_tone_sage_gold"} else "metal.chrome_polished"),
        )
    cap.inertial = Inertial.from_geometry(
        Box((cap_od, cap_od, cap_h)),
        mass=0.012,
        origin=Origin(xyz=(0.0, 0.0, z0 + cap_h / 2.0 - zr)),
    )
    model.articulation(
        "body_to_cap",
        ArticulationType.REVOLUTE,
        parent=body,
        child=cap,
        origin=Origin(xyz=(0.0, 0.0, zr)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=math.pi * 2.0),
    )


def _build_dropper(model, body, r, *, closure_mat, accent_mat) -> None:
    """Dropper assembly: collar + 3 thread ridges + lathe bulb + glass pipette.
    Lifts straight UP (+Z) via PRISMATIC; pipette runs down through the neck."""
    c = r.closure_size_scale
    collar_od = max(0.021 * c, _neck_outer_radius(r) * 2.0 + 0.003)
    collar_h = 0.009 * c
    seat = 0.003
    thread_count = 3
    bulb_h = 0.025 * c
    bulb_base_r = 0.005 * c
    bulb_max_r = 0.008 * c
    pipette_od = 0.004
    pipette_len = 0.038 * c
    pipette_tip_h = 0.004
    pipette_tip_r = 0.0008
    lift = 0.045 * r.joint_travel_scale

    zr = r.neck_top_z  # joint origin / local-frame datum (neck rim top)
    collar_z0 = r.neck_top_z - seat
    collar_top = collar_z0 + collar_h

    dropper = model.part("dropper")
    # Author absolute then shift to neck-rim-local frame so local z=0 (the +Z
    # lift origin) lies inside the dropper geometry; the joint origin restores it.
    # Collar ring (solid; bulb/pipette penetrate into it for connectivity).
    collar = _cylinder(collar_od / 2.0, collar_h, z0=collar_z0)
    dropper.visual(
        mesh_from_cadquery(collar.translate((0.0, 0.0, -zr)), "collar_ring"),
        material=accent_mat,
        name="collar_ring", material_class_id=("metal.precious_gold" if r.palette_style in {"matte_black_gold", "frosted_glass_gold", "soft_touch_taupe", "brushed_metallic_champagne", "pearlescent_blush_rosegold", "opaque_white_gold", "amber_apothecary", "two_tone_sage_gold"} else "metal.chrome_polished"),
    )
    for i in range(thread_count):
        ridge_z = collar_z0 + (i + 1) * collar_h / (thread_count + 1)
        ridge = (
            cq.Workplane("XY")
            .workplane(offset=ridge_z)
            .circle(collar_od / 2.0 + 0.0006)
            .circle(collar_od / 2.0 - 0.0002)
            .extrude(0.001)
            .translate((0.0, 0.0, -zr))
        )
        dropper.visual(
            mesh_from_cadquery(ridge, f"thread_ridge_{i}"),
            material=accent_mat,
            name=f"thread_ridge_{i}", material_class_id=("metal.precious_gold" if r.palette_style in {"matte_black_gold", "frosted_glass_gold", "soft_touch_taupe", "brushed_metallic_champagne", "pearlescent_blush_rosegold", "opaque_white_gold", "amber_apothecary", "two_tone_sage_gold"} else "metal.chrome_polished"),
        )

    # Rubber squeeze bulb (LatheGeometry revolved profile), z relative to zr.
    z_penetrate = collar_top - 0.001
    bulb_profile = [
        (0.000, z_penetrate - zr),
        (0.003, z_penetrate - zr),
        (bulb_base_r, collar_top - zr),
        (bulb_base_r + 0.001, collar_top + bulb_h * 0.08 - zr),
        (bulb_max_r * 0.85, collar_top + bulb_h * 0.20 - zr),
        (bulb_max_r, collar_top + bulb_h * 0.35 - zr),
        (bulb_max_r, collar_top + bulb_h * 0.55 - zr),
        (bulb_max_r * 0.85, collar_top + bulb_h * 0.72 - zr),
        (bulb_max_r * 0.55, collar_top + bulb_h * 0.88 - zr),
        (bulb_max_r * 0.25, collar_top + bulb_h * 0.96 - zr),
        (0.000, collar_top + bulb_h - zr),
    ]
    dropper.visual(
        mesh_from_geometry(LatheGeometry(bulb_profile, segments=32), "squeeze_bulb"),
        material=closure_mat,
        name="squeeze_bulb", material_class_id="rubber.smooth_plain",
    )

    # Glass pipette: tube + tapered tip, penetrating up into the collar.
    z_top = collar_z0 + 0.003
    z_bot = collar_z0 - pipette_len
    or_p = pipette_od / 2.0
    total_len = z_top - z_bot
    tube = _cylinder(or_p, total_len - pipette_tip_h, z0=z_bot + pipette_tip_h)
    tip = (
        cq.Workplane("XY")
        .workplane(offset=z_bot)
        .circle(pipette_tip_r)
        .workplane(offset=pipette_tip_h)
        .circle(or_p)
        .loft(ruled=True)
    )
    pipette = tube.union(tip).translate((0.0, 0.0, -zr))
    dropper.visual(
        mesh_from_cadquery(pipette, "glass_pipette"),
        material=closure_mat,
        name="glass_pipette", material_class_id="glass.clear_transparent",
    )

    dropper_total_h = collar_h + bulb_h + pipette_len
    dropper_mid_z = collar_z0 + (bulb_h + collar_h - pipette_len) / 2.0
    dropper.inertial = Inertial.from_geometry(
        Box((collar_od, collar_od, dropper_total_h)),
        mass=0.012,
        origin=Origin(xyz=(0.0, 0.0, dropper_mid_z - zr)),
    )
    model.articulation(
        "dropper_lift",
        ArticulationType.PRISMATIC,
        parent=body,
        child=dropper,
        # Origin on the real neck-top rim (within both the body neck + dropper
        # collar/pipette AABBs); geometry authored in absolute coords, +Z lift.
        origin=Origin(xyz=(0.0, 0.0, r.neck_top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=0.05, lower=0.0, upper=lift),
    )


def _build_flip_top(model, body, r, *, closure_mat, accent_mat) -> None:
    """Body-inline cap_base + hinged flip disc, REVOLUTE +X opening up."""
    c = r.closure_size_scale
    cap_radius = max(0.012 * c, _neck_outer_radius(r) + 0.002)
    cap_h = 0.007 * c
    seat = 0.003
    flip_radius = cap_radius - 0.001
    flip_thick = 0.0025 * c
    open_angle = min(1.8 * r.joint_travel_scale, 2.2)

    cap_base_z0 = r.neck_top_z - seat
    cap_top_z = cap_base_z0 + cap_h

    # Cap base: low shell over the neck + snap ridge + orifice well (body-inline).
    shell = _cylinder(cap_radius, cap_h, z0=cap_base_z0)
    ridge = (
        cq.Workplane("XY")
        .workplane(offset=cap_base_z0 + 0.001)
        .circle(cap_radius + 0.0006)
        .circle(cap_radius)
        .extrude(0.0012)
    )
    shell = shell.union(ridge)
    well = _cylinder(0.0025, 0.003, z0=cap_top_z - 0.002)
    shell = shell.cut(well)
    body.visual(
        mesh_from_cadquery(shell, "cap_base"),
        material=closure_mat,
        name="cap_base", material_class_id=("plastic.opaque_generic" if r.palette_style in {"matte_black_gold", "soft_touch_taupe", "amber_apothecary", "two_tone_sage_gold"} else "metal.precious_gold"),
    )

    # Flip disc in the hinge frame: origin at the back edge, disc extends +Y.
    disc_cy = cap_radius
    disc = (
        cq.Workplane("XY")
        .workplane(offset=0.0)
        .center(0.0, disc_cy)
        .circle(flip_radius)
        .extrude(flip_thick)
    )
    tab_cy = disc_cy + flip_radius - 0.002
    tab = (
        cq.Workplane("XY")
        .workplane(offset=-0.0004)
        .center(0.0, tab_cy)
        .rect(0.005, 0.005)
        .extrude(flip_thick + 0.0008)
    )
    disc = disc.union(tab)
    plug = (
        cq.Workplane("XY")
        .workplane(offset=-0.0015)
        .center(0.0, disc_cy)
        .circle(0.0022)
        .extrude(0.0018)
    )
    disc = disc.union(plug)

    flip_cap = model.part("flip_cap")
    flip_cap.visual(
        mesh_from_cadquery(disc, "flip_disc"),
        material=accent_mat,
        name="flip_disc", material_class_id=("metal.precious_gold" if r.palette_style in {"matte_black_gold", "frosted_glass_gold", "soft_touch_taupe", "brushed_metallic_champagne", "pearlescent_blush_rosegold", "opaque_white_gold", "amber_apothecary", "two_tone_sage_gold"} else "metal.chrome_polished"),
    )
    flip_cap.inertial = Inertial.from_geometry(
        Cylinder(radius=flip_radius, length=flip_thick),
        mass=0.005,
        origin=Origin(xyz=(0.0, cap_radius, flip_thick / 2.0)),
    )
    model.articulation(
        "cap_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=flip_cap,
        origin=Origin(xyz=(0.0, -cap_radius, cap_top_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=open_angle),
    )


def _build_side_lever_pump(model, body, r, *, closure_mat) -> None:
    """Body-inline pump_housing + fork posts; lever arm swings DOWN (REVOLUTE -X)."""
    c = r.closure_size_scale
    housing_d = 0.016 * c
    housing_h = 0.008 * c
    fork_post_d = 0.003 * c
    fork_post_h = 0.014 * c
    fork_post_spacing = 0.012 * c

    # Housing radius must span the open neck rim ring so it lands on the solid
    # rim wall (not float over the bored-open mouth); recess it slightly into the
    # rim for a robust solid Z-contact with the body shell.
    housing_r = max(housing_d / 2.0, _neck_outer_radius(r) + 0.0010)
    housing_recess = 0.0015
    neck_top = r.neck_top_z
    housing_z0 = neck_top - housing_recess
    housing_top = housing_z0 + housing_h
    pivot_z = housing_top + fork_post_h * 0.65

    hub_d = 0.006 * c
    hub_w = 0.0095 * c
    arm_len = 0.030 * c
    arm_w = 0.005 * c
    arm_t = 0.003 * c
    nozzle_d = 0.004 * c
    nozzle_l = 0.007 * c
    swing_upper = min(1.05 * r.joint_travel_scale, 1.3)

    # Body-inline pump housing collar + fork posts.
    housing = _cylinder(housing_r, housing_h, z0=housing_z0)
    body.visual(
        mesh_from_cadquery(housing, "pump_housing"),
        material=closure_mat,
        name="pump_housing", material_class_id=("plastic.opaque_generic" if r.palette_style in {"matte_black_gold", "soft_touch_taupe", "amber_apothecary", "two_tone_sage_gold"} else "metal.precious_gold"),
    )
    for i in range(2):
        x_sign = -1 if i == 0 else 1
        x_pos = x_sign * fork_post_spacing / 2.0
        post = (
            cq.Workplane("XY")
            .workplane(offset=housing_top)
            .center(x_pos, 0.0)
            .circle(fork_post_d / 2.0)
            .extrude(fork_post_h)
        )
        body.visual(
            mesh_from_cadquery(post, f"fork_post_{i}"),
            material=closure_mat,
            name=f"fork_post_{i}", material_class_id=("plastic.opaque_generic" if r.palette_style in {"matte_black_gold", "soft_touch_taupe", "amber_apothecary", "two_tone_sage_gold"} else "metal.precious_gold"),
        )

    # Lever arm in local pivot frame: hub at origin, arm extends +Y, curves up.
    hub = (
        cq.Workplane("YZ")
        .workplane(offset=-hub_w / 2.0)
        .circle(hub_d / 2.0)
        .extrude(hub_w)
    )
    arm_start_y = hub_d / 2.0 * 0.5
    arm = (
        cq.Workplane("XZ")
        .workplane(offset=-arm_start_y)
        .rect(arm_w, arm_t)
        .workplane(offset=-(arm_len - arm_start_y))
        .center(0, 0.004)
        .rect(arm_w * 0.65, arm_t * 0.7)
        .loft()
    )
    nozzle = (
        cq.Workplane("XZ")
        .workplane(offset=-(arm_len + nozzle_l))
        .center(0, 0.004)
        .circle(nozzle_d / 2.0)
        .extrude(nozzle_l + 0.001)
    )
    lever_solid = hub.union(arm).union(nozzle)

    lever = model.part("lever")
    lever.visual(
        mesh_from_cadquery(lever_solid, "lever_arm"),
        material=closure_mat,
        name="lever_arm", material_class_id=("plastic.opaque_generic" if r.palette_style in {"matte_black_gold", "soft_touch_taupe", "amber_apothecary", "two_tone_sage_gold"} else "metal.precious_gold"),
    )
    lever.inertial = Inertial.from_geometry(
        Box((hub_w, arm_len, hub_d)),
        mass=0.008,
        origin=Origin(xyz=(0.0, arm_len / 2.0, 0.0)),
    )
    model.articulation(
        "lever_swing",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lever,
        origin=Origin(xyz=(0.0, 0.0, pivot_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=swing_upper),
    )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_primer_bottle(
    config: ContainerPrimerBottleConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    body_mat = model.material(f"cpb_body_{r.palette_style}", rgba=pal["body"])
    closure_mat = model.material(f"cpb_closure_{r.palette_style}", rgba=pal["closure"])
    accent_mat = model.material(f"cpb_accent_{r.palette_style}", rgba=pal["accent"])

    # --- ROOT: bottle body ---------------------------------------------------
    body = model.part("body")
    _emit_body(body, r, body_mat=body_mat, accent_mat=accent_mat)

    # --- closure mechanism ---------------------------------------------------
    if r.closure_mechanism == "airless_press_pump":
        _build_airless_pump(model, body, r, closure_mat=closure_mat)
    elif r.closure_mechanism == "spray_atomizer":
        _build_spray_atomizer(model, body, r, closure_mat=closure_mat)
    elif r.closure_mechanism == "treatment_spout_pump":
        _build_treatment_spout(model, body, r, closure_mat=closure_mat)
    elif r.closure_mechanism == "screw_twist_cap":
        _build_screw_twist_cap(model, body, r, closure_mat=closure_mat, accent_mat=accent_mat)
    elif r.closure_mechanism == "dropper_cap":
        _build_dropper(model, body, r, closure_mat=closure_mat, accent_mat=accent_mat)
    elif r.closure_mechanism == "flip_top_disc":
        _build_flip_top(model, body, r, closure_mat=closure_mat, accent_mat=accent_mat)
    elif r.closure_mechanism == "side_lever_pump":
        _build_side_lever_pump(model, body, r, closure_mat=closure_mat)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_primer_bottle(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_primer_bottle(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (closure skirt over the neck, lever hub on
# fork posts, dropper pipette through the neck, flip plug in the cap base) are
# declared element-scoped so the sweep's island/overlap checks pass; each
# closure's articulation action is exercised.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_primer_bottle_tests(
    object_model: ArticulatedObject,
    config: ContainerPrimerBottleConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("body")

    # ---- body reads slim and tall (primer identity) ----
    aabb = ctx.part_world_aabb(body)
    bext = _ext(aabb)
    ctx.check(
        "body rests on the ground (base near z=0)",
        abs(aabb[0][2]) < 0.010,
        details=f"body min z={aabb[0][2]:.4f}",
    )
    ctx.check(
        "body is tall (height dominates footprint)",
        bext[2] > 0.070 and bext[2] > bext[0] + 0.030 and bext[2] > bext[1] + 0.030,
        details=f"body extents={bext}",
    )
    ctx.check(
        "body is slim (footprint under 45mm on both axes)",
        bext[0] < 0.045 and bext[1] < 0.045,
        details=f"body extents={bext}",
    )

    # ---- cross-section identity per body_form ----
    if r.section == "circle":
        ctx.check(
            "round body footprint is approximately circular (X ~= Y)",
            abs(bext[0] - bext[1]) < 0.008,
            details=f"X={bext[0]:.4f}, Y={bext[1]:.4f}",
        )
    elif r.section == "ellipse":
        ctx.check(
            "oval body footprint is wider in X than Y",
            bext[0] > bext[1] + 0.004,
            details=f"X={bext[0]:.4f}, Y={bext[1]:.4f}",
        )

    # ---- gold accent band partway up the body ----
    band_aabb = ctx.part_element_world_aabb(body, elem="gold_band")
    band_z = (band_aabb[0][2] + band_aabb[1][2]) / 2.0
    ctx.check(
        "gold accent band sits partway up the body",
        0.030 < band_z < 0.070,
        details=f"gold band center z={band_z:.4f}",
    )

    # ---- label plate on the front face ----
    ctx.check(
        "label plate visual exists on the body",
        body.get_visual("label_plate") is not None,
        details="label_plate visual not found",
    )

    # ---- closure: actions + captured-fit overlaps ----
    closure = r.closure_mechanism

    if closure in ("airless_press_pump", "spray_atomizer", "treatment_spout_pump"):
        if closure == "airless_press_pump":
            part_name, elem_name, joint_name = "pump_top", "pump_cap", "pump_press"
            travel = 0.006 * r.joint_travel_scale
        elif closure == "spray_atomizer":
            part_name, elem_name, joint_name = "spray_head", "atomizer_head", "spray_press"
            travel = 0.006 * r.joint_travel_scale
        else:
            part_name, elem_name, joint_name = "pump_head", "pump_head_shell", "pump_press"
            travel = 0.006 * r.joint_travel_scale

        closure_part = object_model.get_part(part_name)
        press = object_model.get_articulation(joint_name)
        ctx.allow_overlap(
            closure_part, body, elem_a=elem_name, elem_b="body_shell",
            reason="The closure skirt is intentionally seated down over the neck collar.",
        )
        ctx.check(
            f"{joint_name} is PRISMATIC about +Z, pressing down (lower<0, upper=0)",
            press.articulation_type == ArticulationType.PRISMATIC
            and abs(press.axis[2]) > 0.99
            and press.motion_limits is not None
            and press.motion_limits.lower < 0.0
            and abs(press.motion_limits.upper) < 1e-6,
            details=f"axis={press.axis}, limits={press.motion_limits}",
        )
        # Pump is on top and seated over the neck.
        c_aabb = ctx.part_world_aabb(closure_part)
        c_center_z = (c_aabb[0][2] + c_aabb[1][2]) / 2.0
        ctx.check(
            "closure mounted at the top of the bottle",
            c_aabb[0][2] > r.body_h - 0.012 and c_center_z > r.body_h,
            details=f"closure aabb z=[{c_aabb[0][2]:.4f}, {c_aabb[1][2]:.4f}]",
        )
        ctx.expect_overlap(
            closure_part, body, axes="xy", min_overlap=0.008,
            name="closure seated over neck (footprint)",
        )
        # Spray side nozzle / treatment gooseneck distinguishing geometry.
        if closure == "spray_atomizer":
            ctx.check(
                "spray nozzle protrudes beyond the body front face (+Y)",
                c_aabb[1][1] > aabb[1][1],
                details=f"head y_max={c_aabb[1][1]:.4f}, body y_max={aabb[1][1]:.4f}",
            )
        if closure == "treatment_spout_pump":
            cext = _ext(c_aabb)
            ctx.check(
                "gooseneck spout extends laterally (X span > 0.028)",
                cext[0] > 0.028,
                details=f"pump X span={cext[0]:.4f}",
            )
            ctx.check(
                "treatment pump head is tall (> 0.030)",
                cext[2] > 0.030,
                details=f"pump head height={cext[2]:.4f}",
            )
        # Press action: closure drops when pressed.
        top_rest = ctx.part_world_aabb(closure_part)[1][2]
        with ctx.pose({press: -travel}):
            ctx.expect_overlap(
                closure_part, body, axes="xy", min_overlap=0.008,
                name="closure stays seated when pressed",
            )
            top_down = ctx.part_world_aabb(closure_part)[1][2]
        ctx.check(
            "closure presses straight down (top drops)",
            top_down < top_rest - travel * 0.5,
            details=f"rest_top_z={top_rest:.4f}, pressed_top_z={top_down:.4f}",
        )

    elif closure == "screw_twist_cap":
        cap = object_model.get_part("screw_cap")
        twist = object_model.get_articulation("body_to_cap")
        ctx.allow_overlap(
            cap, body, elem_a="cap_shell", elem_b="body_shell",
            reason="The screw cap skirt intentionally seats over the neck collar.",
        )
        ctx.check(
            "body_to_cap is REVOLUTE about +Z",
            twist.articulation_type == ArticulationType.REVOLUTE and abs(twist.axis[2]) > 0.99,
            details=f"axis={twist.axis}, type={twist.articulation_type}",
        )
        ctx.expect_overlap(
            cap, body, axes="xy", min_overlap=0.008,
            name="cap seated over neck (footprint)",
        )
        rib0_rest = ctx.part_element_world_aabb(cap, elem="grip_rib_0")
        rib0_rest_c = (
            (rib0_rest[0][0] + rib0_rest[1][0]) / 2.0,
            (rib0_rest[0][1] + rib0_rest[1][1]) / 2.0,
            (rib0_rest[0][2] + rib0_rest[1][2]) / 2.0,
        )
        with ctx.pose({twist: math.pi / 2.0}):
            rib0_rot = ctx.part_element_world_aabb(cap, elem="grip_rib_0")
            ctx.expect_overlap(
                cap, body, axes="xy", min_overlap=0.008,
                name="cap stays seated when unscrewed 90deg",
            )
        rib0_rot_c = (
            (rib0_rot[0][0] + rib0_rot[1][0]) / 2.0,
            (rib0_rot[0][1] + rib0_rot[1][1]) / 2.0,
            (rib0_rot[0][2] + rib0_rot[1][2]) / 2.0,
        )
        ctx.check(
            "cap rotates about Z (grip rib moves in XY, not Z)",
            (abs(rib0_rot_c[0] - rib0_rest_c[0]) > 0.002
             or abs(rib0_rot_c[1] - rib0_rest_c[1]) > 0.002)
            and abs(rib0_rot_c[2] - rib0_rest_c[2]) < 0.001,
            details=f"rest={rib0_rest_c}, rot={rib0_rot_c}",
        )

    elif closure == "dropper_cap":
        dropper = object_model.get_part("dropper")
        lift = object_model.get_articulation("dropper_lift")
        lift_travel = 0.045 * r.joint_travel_scale
        ctx.allow_overlap(
            dropper, body, elem_a="collar_ring", elem_b="body_shell",
            reason="The dropper screw collar is intentionally seated over the neck collar.",
        )
        ctx.allow_overlap(
            dropper, body, elem_a="glass_pipette", elem_b="body_shell",
            reason="The glass pipette extends through the neck into the bottle body.",
        )
        ctx.check(
            "dropper_lift is PRISMATIC about +Z, pulling out (lower=0, upper>0)",
            lift.articulation_type == ArticulationType.PRISMATIC
            and abs(lift.axis[2]) > 0.99
            and lift.motion_limits is not None
            and abs(lift.motion_limits.lower) < 1e-6
            and lift.motion_limits.upper > 0.0,
            details=f"axis={lift.axis}, limits={lift.motion_limits}",
        )
        ctx.expect_overlap(
            dropper, body, axes="xy", min_overlap=0.008,
            elem_a="collar_ring",
            name="collar seated over neck (footprint)",
        )
        # Dropper has the three distinct components.
        collar_aabb = ctx.part_element_world_aabb(dropper, elem="collar_ring")
        bulb_aabb = ctx.part_element_world_aabb(dropper, elem="squeeze_bulb")
        pipette_aabb = ctx.part_element_world_aabb(dropper, elem="glass_pipette")
        ctx.check(
            "bulb sits on top of the collar",
            bulb_aabb[0][2] >= collar_aabb[1][2] - 0.002,
            details=f"bulb_bot={bulb_aabb[0][2]:.4f}, collar_top={collar_aabb[1][2]:.4f}",
        )
        ctx.check(
            "pipette hangs below the collar into the neck",
            pipette_aabb[0][2] < collar_aabb[0][2] - 0.010,
            details=f"pipette_bot={pipette_aabb[0][2]:.4f}, collar_bot={collar_aabb[0][2]:.4f}",
        )
        # Lift action.
        rest_bot = ctx.part_world_aabb(dropper)[0][2]
        with ctx.pose({lift: lift_travel}):
            lifted_bot = ctx.part_world_aabb(dropper)[0][2]
        ctx.check(
            "dropper rises when lifted",
            lifted_bot > rest_bot + lift_travel * 0.5,
            details=f"rest_bot={rest_bot:.4f}, lifted_bot={lifted_bot:.4f}",
        )

    elif closure == "flip_top_disc":
        flip_cap = object_model.get_part("flip_cap")
        hinge = object_model.get_articulation("cap_hinge")
        open_angle = min(1.8 * r.joint_travel_scale, 2.2)
        ctx.check(
            "cap_base inline visual exists on the body",
            body.get_visual("cap_base") is not None,
            details="cap_base visual not found",
        )
        ctx.allow_overlap(
            flip_cap, body, elem_a="flip_disc", elem_b="cap_base",
            reason="The flip disc sealing plug intentionally seats into the cap base orifice well.",
        )
        ctx.check(
            "cap_hinge is REVOLUTE about +X",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[0]) > 0.9
            and abs(hinge.axis[2]) < 0.1,
            details=f"axis={hinge.axis}, type={hinge.articulation_type}",
        )
        flip_aabb = ctx.part_world_aabb(flip_cap)
        flip_dx = flip_aabb[1][0] - flip_aabb[0][0]
        flip_dy = flip_aabb[1][1] - flip_aabb[0][1]
        ctx.check(
            "flip disc is roughly circular (aspect near 1)",
            abs(flip_dx - flip_dy) < 0.012,
            details=f"flip dx={flip_dx:.4f}, dy={flip_dy:.4f}",
        )
        ctx.check(
            "flip disc mounted at top of bottle",
            flip_aabb[0][2] > r.body_h,
            details=f"flip aabb z=[{flip_aabb[0][2]:.4f}, {flip_aabb[1][2]:.4f}]",
        )
        ctx.expect_overlap(
            flip_cap, body, axes="xy", min_overlap=0.006,
            elem_a="flip_disc", elem_b="cap_base",
            name="flip disc covers cap base when closed",
        )
        top_rest = flip_aabb[1][2]
        with ctx.pose({hinge: open_angle}):
            top_open = ctx.part_world_aabb(flip_cap)[1][2]
        ctx.check(
            "flip cap opens upward (top rises when opened)",
            top_open > top_rest + 0.005,
            details=f"closed_top={top_rest:.4f}, open_top={top_open:.4f}",
        )

    elif closure == "side_lever_pump":
        lever = object_model.get_part("lever")
        swing = object_model.get_articulation("lever_swing")
        swing_upper = min(1.05 * r.joint_travel_scale, 1.3)
        for i in range(2):
            ctx.check(
                f"fork_post_{i} inline visual exists on the body",
                body.get_visual(f"fork_post_{i}") is not None,
                details=f"fork_post_{i} not found",
            )
            ctx.allow_overlap(
                lever, body, elem_a="lever_arm", elem_b=f"fork_post_{i}",
                reason=f"Lever hub wraps around fork_post_{i} at the revolute pivot axis.",
            )
        ctx.check(
            "pump_housing inline visual exists on the body",
            body.get_visual("pump_housing") is not None,
            details="pump_housing not found",
        )
        ctx.check(
            "lever_swing is REVOLUTE about -X (downstroke)",
            swing.articulation_type == ArticulationType.REVOLUTE and abs(swing.axis[0]) > 0.99,
            details=f"axis={swing.axis}, type={swing.articulation_type}",
        )
        lever_aabb = ctx.part_world_aabb(lever)
        lever_center_z = (lever_aabb[0][2] + lever_aabb[1][2]) / 2.0
        ctx.check(
            "lever mounted at the top of the bottle",
            lever_aabb[0][2] > r.body_h - 0.010 and lever_center_z > r.body_h,
            details=f"lever aabb z=[{lever_aabb[0][2]:.4f}, {lever_aabb[1][2]:.4f}]",
        )
        ctx.check(
            "lever arm extends outward in +Y at rest",
            lever_aabb[1][1] > 0.010,
            details=f"lever max y={lever_aabb[1][1]:.4f}",
        )
        # Swing action: arm tilts down.
        bottom_rest = lever_aabb[0][2]
        tip_y_rest = lever_aabb[1][1]
        with ctx.pose({swing: swing_upper}):
            sw_aabb = ctx.part_world_aabb(lever)
        ctx.check(
            "lever drops when swung (revolute downstroke)",
            sw_aabb[0][2] < bottom_rest - 0.004,
            details=f"rest_bot={bottom_rest:.4f}, swing_bot={sw_aabb[0][2]:.4f}",
        )
        ctx.check(
            "lever arm Y extent shrinks when swung (arm tilts down)",
            sw_aabb[1][1] < tip_y_rest - 0.004,
            details=f"rest_max_y={tip_y_rest:.4f}, swing_max_y={sw_aabb[1][1]:.4f}",
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
