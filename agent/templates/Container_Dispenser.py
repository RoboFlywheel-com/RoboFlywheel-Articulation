# SPDX-License-Identifier: Apache-2.0

"""Container dispenser — modular procedural template (pump / press-top bottle).

Category identity: an upright pump-dispenser bottle (soap / lotion / sanitizer).
A hollow, usually-transparent bottle (ROOT) rests on z=0 with its axis along +Z;
a ribbed threaded ``collar`` is FIXED on the neck; an exposed press pump
(``pump_head``) presses down via a PRISMATIC +Z joint and回弹; a side ``spout``
swivels horizontally via a REVOLUTE +Z joint; a ``dip_tube`` FIXED under the pump
descends into the transparent bottle. Some pump variants add a ``lock_ring``
(REVOLUTE +Z quarter-turn twist-lock). No closure / cap. No multiplicity.

Four parallel slots (spec ``Container_Dispenser.md``):

  * ``body_form`` (5) — the ROOT ``bottle`` mesh + label + liquid:
      round_clear_bottle (revolve Lathe), square_rounded_body (rounded-rect
      loft), oval_flask_body (flattened ellipse loft), narrow_oval_footprint
      (front-back ellipse loft), square_prism_footprint (square-prism loft).
  * ``pump_head`` (4) — the main mechanism (>=1 non-fixed joint each):
      - press_swivel_pump: PRISMATIC press + REVOLUTE spout swivel (baseline).
      - long_spout_lotion_pump: tall plunger + long curved spout, same joints.
      - service_lift_pump: seal/guide ring + PRISMATIC press with positive lift.
      - twist_lock_pump: adds a ``lock_ring`` REVOLUTE +Z quarter turn; pump
        re-parents onto the lock ring (3 non-fixed joints total).
  * ``neck_collar`` (2) — FIXED visual on the bottle neck:
      standard_ribbed_collar (28 vertical ribs) / oversized_industrial_collar
      (two-tier stepped: thread ribs + flutes + knurl + lip).
  * ``dip_tube`` (2) — FIXED under the pump:
      straight_dip_tube (near-vertical spline) / s_curved_dip_tube (S spline).

Per-seed palette diversity: 10 coordinated colorways x finish (clear_soap,
amber_lotion, frosted_white, blue_teal, ceramic_cream, matte_black,
soft_touch_sage, pearlescent_blush, chrome_pump_clear, sanitizer_aqua_gel).
Opaque colorways relax the transparency assertion and hide the liquid fill.

Continuous size/proportion variation (height/radius/collar/travel/reach scales)
lives in ``resolve_config`` as clamped params, never as slot candidates.

Sources (articraft_data ``picture/Container/Dispenser`` 5-star pool): parent
``rec_container_dispenser_v01`` (full round-bottle press-pump chain) + qwen forks
square_body / oval_body / tall_plunger_long_spout / detached_pump_insert /
twist_lock_pump / ribbed_collar / curved_dip_tube.

Canonical spec:
``articraft_template_authoring/specs_modular_v1/Container_Dispenser.md``
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    BoxGeometry,
    Cylinder,
    CylinderGeometry,
    Inertial,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    min_clearance_at_pose,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyForm = Literal[
    "round_clear_bottle",
    "square_rounded_body",
    "oval_flask_body",
    "narrow_oval_footprint",
    "square_prism_footprint",
]
PumpHead = Literal[
    "press_swivel_pump",
    "long_spout_lotion_pump",
    "service_lift_pump",
    "twist_lock_pump",
]
NeckCollar = Literal[
    "standard_ribbed_collar",
    "oversized_industrial_collar",
]
DipTube = Literal[
    "straight_dip_tube",
    "s_curved_dip_tube",
]
PaletteStyle = Literal[
    "clear_soap",
    "amber_lotion",
    "frosted_white",
    "blue_teal",
    "ceramic_cream",
    "matte_black",
    "soft_touch_sage",
    "pearlescent_blush",
    "chrome_pump_clear",
    "sanitizer_aqua_gel",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "round_clear_bottle",
    "square_rounded_body",
    "oval_flask_body",
    "narrow_oval_footprint",
    "square_prism_footprint",
)
PUMP_HEADS: tuple[PumpHead, ...] = (
    "press_swivel_pump",
    "long_spout_lotion_pump",
    "service_lift_pump",
    "twist_lock_pump",
)
NECK_COLLARS: tuple[NeckCollar, ...] = (
    "standard_ribbed_collar",
    "oversized_industrial_collar",
)
DIP_TUBES: tuple[DipTube, ...] = (
    "straight_dip_tube",
    "s_curved_dip_tube",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "clear_soap",
    "amber_lotion",
    "frosted_white",
    "blue_teal",
    "ceramic_cream",
    "matte_black",
    "soft_touch_sage",
    "pearlescent_blush",
    "chrome_pump_clear",
    "sanitizer_aqua_gel",
)

# Opaque colorways: skip the transparency assertion + hide the liquid fill.
_OPAQUE_PALETTES: frozenset[PaletteStyle] = frozenset(
    {"ceramic_cream", "matte_black", "soft_touch_sage"}
)


# ---------------------------------------------------------------------------
# Palettes: 10 coordinated colorways, each with bottle / liquid / pump / collar
# accent / dip-tube rgba + an explicit ``finish`` surface dimension. rgba values
# are anchored on the 5-star source materials (clear_plastic / pale_soap /
# warm_white / soft_grey / milky_tube / pale_blue_tube) and shifted per colorway.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Palette:
    bottle: tuple[float, float, float, float]
    liquid: tuple[float, float, float, float]
    pump: tuple[float, float, float, float]
    accent: tuple[float, float, float, float]
    tube: tuple[float, float, float, float]
    label: tuple[float, float, float, float]
    finish: str


PALETTES: dict[PaletteStyle, _Palette] = {
    "clear_soap": _Palette(
        bottle=(0.78, 0.88, 0.92, 0.34),
        liquid=(0.78, 0.90, 0.84, 0.62),
        pump=(0.94, 0.93, 0.90, 1.0),
        accent=(0.70, 0.72, 0.72, 1.0),
        tube=(0.88, 0.92, 0.92, 0.78),
        label=(0.96, 0.96, 0.91, 1.0),
        finish="clear_gloss",
    ),
    "amber_lotion": _Palette(
        bottle=(0.80, 0.62, 0.34, 0.40),
        liquid=(0.86, 0.66, 0.40, 0.70),
        pump=(0.94, 0.93, 0.90, 1.0),
        accent=(0.70, 0.72, 0.72, 1.0),
        tube=(0.88, 0.92, 0.92, 0.78),
        label=(0.96, 0.96, 0.91, 1.0),
        finish="amber_translucent",
    ),
    "frosted_white": _Palette(
        bottle=(0.92, 0.93, 0.94, 0.48),
        liquid=(0.78, 0.90, 0.84, 0.62),
        pump=(0.94, 0.93, 0.90, 1.0),
        accent=(0.70, 0.72, 0.72, 1.0),
        tube=(0.88, 0.92, 0.92, 0.78),
        label=(0.96, 0.96, 0.91, 1.0),
        finish="frosted_translucent",
    ),
    "blue_teal": _Palette(
        bottle=(0.55, 0.72, 0.90, 0.40),
        liquid=(0.45, 0.78, 0.80, 0.66),
        pump=(0.94, 0.93, 0.90, 1.0),
        accent=(0.70, 0.72, 0.72, 1.0),
        tube=(0.55, 0.72, 0.90, 0.85),
        label=(0.96, 0.96, 0.91, 1.0),
        finish="clear_gloss",
    ),
    "ceramic_cream": _Palette(
        bottle=(0.95, 0.92, 0.85, 1.0),
        liquid=(0.95, 0.92, 0.85, 1.0),
        pump=(0.94, 0.93, 0.90, 1.0),
        accent=(0.70, 0.72, 0.72, 1.0),
        tube=(0.88, 0.92, 0.92, 0.78),
        label=(0.80, 0.74, 0.62, 1.0),
        finish="ceramic_glaze",
    ),
    "matte_black": _Palette(
        bottle=(0.18, 0.18, 0.20, 1.0),
        liquid=(0.18, 0.18, 0.20, 1.0),
        pump=(0.30, 0.30, 0.32, 1.0),
        accent=(0.30, 0.30, 0.32, 1.0),
        tube=(0.22, 0.22, 0.24, 1.0),
        label=(0.55, 0.55, 0.58, 1.0),
        finish="opaque_matte",
    ),
    "soft_touch_sage": _Palette(
        bottle=(0.66, 0.72, 0.62, 1.0),
        liquid=(0.66, 0.72, 0.62, 1.0),
        pump=(0.60, 0.66, 0.56, 1.0),
        accent=(0.70, 0.72, 0.72, 1.0),
        tube=(0.88, 0.92, 0.92, 0.78),
        label=(0.92, 0.94, 0.88, 1.0),
        finish="soft_touch_matte",
    ),
    "pearlescent_blush": _Palette(
        bottle=(0.95, 0.84, 0.86, 0.48),
        liquid=(0.92, 0.74, 0.76, 0.70),
        pump=(0.96, 0.94, 0.93, 1.0),
        accent=(0.70, 0.72, 0.72, 1.0),
        tube=(0.88, 0.92, 0.92, 0.78),
        label=(0.97, 0.93, 0.94, 1.0),
        finish="pearlescent",
    ),
    "chrome_pump_clear": _Palette(
        bottle=(0.78, 0.88, 0.92, 0.34),
        liquid=(0.78, 0.90, 0.84, 0.62),
        pump=(0.82, 0.84, 0.86, 1.0),
        accent=(0.82, 0.84, 0.86, 1.0),
        tube=(0.88, 0.92, 0.92, 0.78),
        label=(0.96, 0.96, 0.91, 1.0),
        finish="metallic_chrome_pump",
    ),
    "sanitizer_aqua_gel": _Palette(
        bottle=(0.62, 0.86, 0.88, 0.36),
        liquid=(0.55, 0.84, 0.86, 0.60),
        pump=(0.94, 0.93, 0.90, 1.0),
        accent=(0.70, 0.72, 0.72, 1.0),
        tube=(0.55, 0.72, 0.90, 0.85),
        label=(0.96, 0.96, 0.91, 1.0),
        finish="clear_gloss",
    ),
}


# ---------------------------------------------------------------------------
# Base geometry per body form (meters). Authored on the parent round bottle
# constants (BODY_R=0.033, BODY_H=0.142, NECK_R=0.014, NECK_TOP=0.188) and the
# fork bodies; scaled per-build by resolve_config.
# ---------------------------------------------------------------------------
_NECK_R = 0.014  # neck radius is FIXED across forms so the collar always fits.


@dataclass(frozen=True)
class _FormGeom:
    # nominal body half-extents (x is "width", y is "depth"); body_r is the
    # round equivalent used for inertials / liquid fill.
    body_r: float
    body_h: float
    shoulder_top: float
    neck_top: float
    half_x: float  # outer half-width at the widest section
    half_y: float  # outer half-depth at the widest section
    kind: str  # "round" | "rounded_rect" | "flask" | "oval" | "square_prism"


_FORMS: dict[BodyForm, _FormGeom] = {
    # parent round clear bottle.
    "round_clear_bottle": _FormGeom(0.033, 0.142, 0.166, 0.188, 0.033, 0.033, "round"),
    # squat rounded square block (chunky_rect): wide flat panels, short body.
    "square_rounded_body": _FormGeom(0.041, 0.110, 0.140, 0.190, 0.041, 0.041, "rounded_rect"),
    # tall flattened oval flask: wide lens front, slim side.
    "oval_flask_body": _FormGeom(0.040, 0.180, 0.204, 0.226, 0.045, 0.012, "flask"),
    # narrow oval footprint: front-back flattened, broad front, short.
    "narrow_oval_footprint": _FormGeom(0.033, 0.142, 0.166, 0.188, 0.037, 0.022, "oval"),
    # square prism footprint: dx ~= dy, broad flat footprint.
    "square_prism_footprint": _FormGeom(0.033, 0.142, 0.166, 0.188, 0.033, 0.033, "square_prism"),
}

# Nominal hardware bands (parent round bottle, absolute world z).
_COLLAR_R = 0.0185
_COLLAR_BAND = 0.026  # collar_z1 - collar_z0
# Press stroke. Kept to a realistic pump depth so the head + swivel spout (which
# ride down with the plunger) never plunge INTO the collar/neck: the spout is
# socketed high on the head and this stroke keeps its lowest point above the
# collar top at full press (see _spout_socket_local_z + the pressed-clearance
# assertion). A fat 0.018 stroke drove the spout ~17 mm below the collar top.
_PRESS_TRAVEL = 0.013
_PUMP_LOCAL_TOP = 0.041  # pump head top above its mount origin (local z)
_PUMP_LOCAL_BOTTOM = -0.044  # pump stem bottom below its mount origin (local z)


@dataclass(frozen=True)
class ContainerDispenserConfig:
    body_form: BodyForm = "round_clear_bottle"
    pump_head: PumpHead = "press_swivel_pump"
    neck_collar: NeckCollar = "standard_ribbed_collar"
    dip_tube: DipTube = "straight_dip_tube"
    palette_style: PaletteStyle = "clear_soap"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    collar_radius_scale: float = 1.0
    pump_travel_scale: float = 1.0
    spout_reach_scale: float = 1.0
    name: str = "container_dispenser"


@dataclass(frozen=True)
class ResolvedContainerDispenserConfig:
    body_form: BodyForm
    pump_head: PumpHead
    neck_collar: NeckCollar
    dip_tube: DipTube
    palette_style: PaletteStyle
    opaque_body: bool
    finish: str
    body_height_scale: float
    body_radius_scale: float
    collar_radius_scale: float
    pump_travel_scale: float
    spout_reach_scale: float
    # derived geometry (absolute world z unless noted local)
    kind: str
    body_r: float
    body_h: float
    shoulder_top: float
    neck_top: float
    neck_r: float
    half_x: float
    half_y: float
    collar_z0: float
    collar_z1: float
    collar_outer_r: float
    pump_mount_z: float  # world z of the pump_press joint origin (collar top)
    press_travel: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerDispenserConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    return ContainerDispenserConfig(
        body_form=rng.choice(BODY_FORMS),
        pump_head=rng.choice(PUMP_HEADS),
        neck_collar=rng.choice(NECK_COLLARS),
        dip_tube=rng.choice(DIP_TUBES),
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.88, 1.18), 4),
        body_radius_scale=round(rng.uniform(0.88, 1.15), 4),
        collar_radius_scale=round(rng.uniform(0.92, 1.12), 4),
        pump_travel_scale=round(rng.uniform(0.85, 1.12), 4),
        spout_reach_scale=round(rng.uniform(0.90, 1.15), 4),
        name=f"seeded_container_dispenser_{seed}",
    )


def resolve_config(
    config: ContainerDispenserConfig | None = None,
) -> ResolvedContainerDispenserConfig:
    cfg = config or ContainerDispenserConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    pump_head = _pick(cfg.pump_head, PUMP_HEADS)
    neck_collar = _pick(cfg.neck_collar, NECK_COLLARS)
    dip_tube = _pick(cfg.dip_tube, DIP_TUBES)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    g = _FORMS[body_form]
    h_scale = _clamp(cfg.body_height_scale, 0.88, 1.18)
    r_scale = _clamp(cfg.body_radius_scale, 0.88, 1.15)
    cr_scale = _clamp(cfg.collar_radius_scale, 0.92, 1.12)
    pt_scale = _clamp(cfg.pump_travel_scale, 0.85, 1.12)
    sr_scale = _clamp(cfg.spout_reach_scale, 0.90, 1.15)

    # neck radius FIXED (collar fit invariant); body radius / height scale.
    body_r = g.body_r * r_scale
    body_h = g.body_h * h_scale
    half_x = g.half_x * r_scale
    half_y = g.half_y * r_scale
    neck_r = _NECK_R

    # The whole hardware stack (shoulder_top, neck_top, collar, pump) rides up
    # with body height. The forms keep a fixed neck->collar->pump offset above
    # the body so the press chain geometry stays consistent (neck_z equation).
    shoulder_top = body_h + (g.shoulder_top - g.body_h)
    neck_top = shoulder_top + (g.neck_top - g.shoulder_top)
    collar_z0 = neck_top - 0.018
    collar_z1 = collar_z0 + _COLLAR_BAND
    # Pump press joint origin: on real hardware at the collar bore. For the
    # twist-lock pump the head parents to the lock ring (sat on the collar top),
    # so the origin rides up into the ring; otherwise it sits just inside the
    # collar top so the on-axis origin lands within the collar mesh.
    if pump_head == "twist_lock_pump":
        pump_mount_z = collar_z1 + 0.0025
    else:
        pump_mount_z = collar_z1 - 0.003

    # Collar outer radius (oversized collar is wider). Bore is held to neck_r so
    # the pump stem (r ~ 0.006) always passes; pump fit is invariant.
    base_collar_r = 0.032 if neck_collar == "oversized_industrial_collar" else _COLLAR_R
    collar_outer_r = base_collar_r * cr_scale

    press_travel = _PRESS_TRAVEL * pt_scale

    return ResolvedContainerDispenserConfig(
        body_form=body_form,
        pump_head=pump_head,
        neck_collar=neck_collar,
        dip_tube=dip_tube,
        palette_style=palette,
        opaque_body=palette in _OPAQUE_PALETTES,
        finish=PALETTES[palette].finish,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        collar_radius_scale=cr_scale,
        pump_travel_scale=pt_scale,
        spout_reach_scale=sr_scale,
        kind=g.kind,
        body_r=body_r,
        body_h=body_h,
        shoulder_top=shoulder_top,
        neck_top=neck_top,
        neck_r=neck_r,
        half_x=half_x,
        half_y=half_y,
        collar_z0=collar_z0,
        collar_z1=collar_z1,
        collar_outer_r=collar_outer_r,
        pump_mount_z=pump_mount_z,
        press_travel=press_travel,
        name=cfg.name or "container_dispenser",
    )


def with_overrides(config: ContainerDispenserConfig, **kwargs: object) -> ContainerDispenserConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerDispenserConfig | ResolvedContainerDispenserConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedContainerDispenserConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("pump_head", r.pump_head),
        ("neck_collar", r.neck_collar),
        ("dip_tube", r.dip_tube),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers — bottle body (Slot A). Authored in the bottle (root) frame
# with the base at z=0. Round form is a revolved Lathe; the others are lofted
# sections (Mesh), per Rule 3 (never downgrade to Box/Cylinder).
# ---------------------------------------------------------------------------
def _rounded_rect_points(width: float, depth: float, radius: float, n: int = 6):
    pts = []
    centers = [
        (width / 2 - radius, depth / 2 - radius, 0.0),
        (-width / 2 + radius, depth / 2 - radius, math.pi / 2),
        (-width / 2 + radius, -depth / 2 + radius, math.pi),
        (width / 2 - radius, -depth / 2 + radius, 3 * math.pi / 2),
    ]
    for cx, cy, a0 in centers:
        for i in range(n + 1):
            a = a0 + (math.pi / 2) * i / n
            pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return pts


def _loft_sections(sections, name: str):
    geom = MeshGeometry()
    rings = []
    for z, pts in sections:
        ring = [geom.add_vertex(x, y, z) for x, y in pts]
        rings.append(ring)
    count = len(rings[0])
    for ring in rings:
        if len(ring) != count:
            raise ValueError("all sections must share a point count")
    for s in range(len(rings) - 1):
        a_ring, b_ring = rings[s], rings[s + 1]
        for i in range(count):
            j = (i + 1) % count
            geom.add_face(a_ring[i], a_ring[j], b_ring[j])
            geom.add_face(a_ring[i], b_ring[j], b_ring[i])
    bottom_center = geom.add_vertex(0.0, 0.0, sections[0][0])
    top_center = geom.add_vertex(0.0, 0.0, sections[-1][0])
    for i in range(count):
        j = (i + 1) % count
        geom.add_face(bottom_center, rings[0][j], rings[0][i])
        geom.add_face(top_center, rings[-1][i], rings[-1][j])
    return mesh_from_geometry(geom, name)


def _round_bottle_mesh(r: ResolvedContainerDispenserConfig):
    """Parent revolve LatheGeometry: outer wall -> shoulder -> neck -> inner
    wall back down to a thick base, plus body ribs + neck thread tori."""
    body_r, body_h = r.body_r, r.body_h
    neck_r, neck_top = r.neck_r, r.neck_top
    shoulder_top = r.shoulder_top
    wall = 0.0022
    outer = [
        (0.0, 0.000),
        (body_r - 0.006, 0.000),
        (body_r, 0.008),
        (body_r, body_h),
        (body_r - 0.010, shoulder_top - 0.006),
        (neck_r + 0.004, shoulder_top),
        (neck_r, shoulder_top + 0.004),
        (neck_r, neck_top),
    ]
    inner = [
        (neck_r - wall, neck_top + 0.002),
        (neck_r - wall, shoulder_top + 0.004),
        (body_r - wall - 0.010, shoulder_top - 0.008),
        (body_r - wall, body_h - 0.004),
        (body_r - wall, 0.014),
        (body_r - wall - 0.006, 0.006),
        (0.0, 0.006),
    ]
    geom = LatheGeometry(outer + inner, segments=72, closed=True)
    for frac in (0.35, 0.58, 0.82):
        z = body_h * frac
        rib = TorusGeometry(body_r + 0.0004, 0.0009, radial_segments=8, tubular_segments=72)
        rib.translate(0.0, 0.0, z)
        geom.merge(rib)
    for z in (r.collar_z0 + 0.004, r.collar_z0 + 0.011, r.collar_z0 + 0.017):
        thread = TorusGeometry(neck_r + 0.0003, 0.0010, radial_segments=8, tubular_segments=60)
        thread.translate(0.0, 0.0, z)
        geom.merge(thread)
    return mesh_from_geometry(geom, "bottle_shell")


def _ellipse_points(rx: float, ry: float, count: int = 64):
    return [
        (rx * math.cos(2 * math.pi * i / count), ry * math.sin(2 * math.pi * i / count))
        for i in range(count)
    ]


def _rounded_rect_bottle_mesh(r: ResolvedContainerDispenserConfig):
    """Squat rounded-square block bottle (chunky_rect fork): wide flat panels,
    broad shoulders, rounded vertical corners -> circular neck."""
    hx, hy = r.half_x, r.half_y
    corner_r = min(0.014, hx * 0.34)
    body_h = r.body_h
    shoulder_top = r.shoulder_top
    neck_top = r.neck_top
    base = _rounded_rect_points(2 * hx, 2 * hy, corner_r, n=6)
    shoulder = _rounded_rect_points(2 * (hx - 0.012), 2 * (hy - 0.012), 0.010, n=6)
    count = len(base)
    neck = [
        (r.neck_r * math.cos(2 * math.pi * i / count), r.neck_r * math.sin(2 * math.pi * i / count))
        for i in range(count)
    ]
    return _loft_sections(
        [(0.0, base), (body_h, base), (shoulder_top, shoulder), (neck_top, neck)],
        "bottle_shell",
    )


def _flask_bottle_mesh(r: ResolvedContainerDispenserConfig):
    """Tall flattened oval flask (oval_body fork): lens-shaped front, slim side,
    tapered waist, circular neck."""
    hx, hy = r.half_x, r.half_y
    bh = r.body_h
    st = r.shoulder_top
    nt = r.neck_top
    sections = [
        (0.000, _ellipse_points(hx * 0.62, hy * 0.75, 72)),
        (0.008 * (bh / 0.180), _ellipse_points(hx * 0.80, hy * 0.83, 72)),
        (0.030 * (bh / 0.180), _ellipse_points(hx * 0.96, hy, 72)),
        (0.055 * (bh / 0.180), _ellipse_points(hx, hy, 72)),
        (0.085 * (bh / 0.180), _ellipse_points(hx * 0.76, hy * 0.75, 72)),
        (0.115 * (bh / 0.180), _ellipse_points(hx * 0.84, hy * 0.83, 72)),
        (0.148 * (bh / 0.180), _ellipse_points(hx * 0.96, hy, 72)),
        (bh - 0.006, _ellipse_points(hx * 0.67, hy * 0.83, 72)),
        (st, _ellipse_points(hx * 0.38, hy * 0.75, 72)),
        (nt, _ellipse_points(r.neck_r, r.neck_r, 72)),
    ]
    return _loft_sections(sections, "bottle_shell")


def _oval_bottle_mesh(r: ResolvedContainerDispenserConfig):
    """Front-back flattened oval (narrow_oval_footprint): broad front, shallow
    side; shorter than the flask."""
    hx, hy = r.half_x, r.half_y
    bh, st, nt = r.body_h, r.shoulder_top, r.neck_top
    return _loft_sections(
        [
            (0.0, _ellipse_points(hx * 0.81, hy * 0.91, 64)),
            (0.040 * (bh / 0.142), _ellipse_points(hx, hy, 64)),
            (bh, _ellipse_points(hx * 0.86, hy * 0.91, 64)),
            (st, _ellipse_points(hx * 0.51, hy * 0.64, 64)),
            (nt, _ellipse_points(r.neck_r, r.neck_r, 64)),
        ],
        "bottle_shell",
    )


def _square_prism_bottle_mesh(r: ResolvedContainerDispenserConfig):
    """Equal width/depth square prism (square_prism_footprint): broad flat
    footprint, rounded-square cross-section -> circular neck."""
    half = r.half_x
    bh, st, nt = r.body_h, r.shoulder_top, r.neck_top
    base = _rounded_rect_points(2 * half, 2 * half, 0.010, n=5)
    shoulder = _rounded_rect_points(2 * (half - 0.008), 2 * (half - 0.008), 0.008, n=5)
    count = len(base)
    neck = [
        (r.neck_r * math.cos(2 * math.pi * i / count), r.neck_r * math.sin(2 * math.pi * i / count))
        for i in range(count)
    ]
    return _loft_sections(
        [(0.0, base), (bh, base), (st, shoulder), (nt, neck)],
        "bottle_shell",
    )


def _bottle_mesh(r: ResolvedContainerDispenserConfig):
    if r.kind == "rounded_rect":
        return _rounded_rect_bottle_mesh(r)
    if r.kind == "flask":
        return _flask_bottle_mesh(r)
    if r.kind == "oval":
        return _oval_bottle_mesh(r)
    if r.kind == "square_prism":
        return _square_prism_bottle_mesh(r)
    return _round_bottle_mesh(r)


def _front_label_mesh(r: ResolvedContainerDispenserConfig):
    """Thin front label plate hugging the bottle front face (a body visual).

    The label inner face is pushed slightly inside the shell wall so it stays
    connected to ``bottle_shell`` (no part-internal floating island)."""
    geom = MeshGeometry()
    if r.kind in ("rounded_rect", "square_prism"):
        w = 2 * r.half_x * 0.7
        y = r.half_y - 0.003
    elif r.kind in ("flask", "oval"):
        # At the label band z (mid body) the ellipse front half-depth ~ half_y;
        # sit the label just inside that front surface.
        w = 2 * r.half_x * 0.55
        y = r.half_y - 0.003
    else:
        w = 0.036
        y = r.body_r - 0.003
    z0 = r.body_h * 0.36
    z1 = r.body_h * 0.82
    t = 0.0035  # thick enough to bridge from inside the wall to proud of it
    # Eight corners (inner face + proud face); face indices below assume this
    # exact add order (0..7).
    geom.add_vertex(-w / 2, y, z0)
    geom.add_vertex(w / 2, y, z0)
    geom.add_vertex(w / 2, y, z1)
    geom.add_vertex(-w / 2, y, z1)
    geom.add_vertex(-w / 2, y + t, z0)
    geom.add_vertex(w / 2, y + t, z0)
    geom.add_vertex(w / 2, y + t, z1)
    geom.add_vertex(-w / 2, y + t, z1)
    faces = [
        (0, 1, 2),
        (0, 2, 3),
        (4, 6, 5),
        (4, 7, 6),
        (0, 4, 5),
        (0, 5, 1),
        (3, 2, 6),
        (3, 6, 7),
        (1, 5, 6),
        (1, 6, 2),
        (0, 3, 7),
        (0, 7, 4),
    ]
    for face in faces:
        geom.add_face(*face)
    return mesh_from_geometry(geom, "front_label")


def _liquid_fill_mesh(r: ResolvedContainerDispenserConfig):
    """Visible liquid volume inside the transparent bottle (a body visual).

    Sized to reach the inner wall (slight embed) so it stays connected to
    ``bottle_shell`` rather than floating as a part-internal island."""
    z_base = 0.012
    height = max(r.body_h * 0.46, 0.030)
    if r.kind in ("rounded_rect", "square_prism"):
        geom = BoxGeometry((2 * r.half_x * 0.97, 2 * r.half_y * 0.97, height))
        geom.translate(0.0, 0.0, z_base + height / 2)
        return mesh_from_geometry(geom, "liquid_fill")
    if r.kind in ("flask", "oval"):
        rx, ry = r.half_x * 0.97, r.half_y * 0.97
        segments = 48
        geom = MeshGeometry()
        bottom, top = [], []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            x, y = rx * math.cos(a), ry * math.sin(a)
            bottom.append(geom.add_vertex(x, y, z_base))
            top.append(geom.add_vertex(x, y, z_base + height))
        bc = geom.add_vertex(0.0, 0.0, z_base)
        tc = geom.add_vertex(0.0, 0.0, z_base + height)
        for i in range(segments):
            j = (i + 1) % segments
            geom.add_face(bottom[i], bottom[j], top[j])
            geom.add_face(bottom[i], top[j], top[i])
            geom.add_face(bc, bottom[j], bottom[i])
            geom.add_face(tc, top[i], top[j])
        return mesh_from_geometry(geom, "liquid_fill")
    geom = CylinderGeometry(r.body_r * 0.97, height, radial_segments=48)
    geom.translate(0.0, 0.0, z_base + height / 2)
    return mesh_from_geometry(geom, "liquid_fill")


# ---------------------------------------------------------------------------
# Collar geometry (Slot C). Authored in the COLLAR-LOCAL frame whose origin sits
# at world z = neck_top (the neck rim, where the bottle geometry is tightest to
# the axis). So local z=0 is the neck rim; the collar band spans
# [collar_z0 - neck_top, collar_z1 - neck_top] (below the rim).
# ---------------------------------------------------------------------------
def _collar_band_local(r: ResolvedContainerDispenserConfig) -> tuple[float, float]:
    return (r.collar_z0 - r.neck_top, r.collar_z1 - r.neck_top)


def _standard_collar_mesh(r: ResolvedContainerDispenserConfig):
    """Single-tier ribbed screw collar: lathe ring + 28 vertical ribs."""
    z0, z1 = _collar_band_local(r)
    co = r.collar_outer_r
    nr = r.neck_r
    # Inner bore reaches close to the axis (still clears the pump stem r~0.006)
    # so the on-axis FIXED/PRISMATIC joint origins sit within the collar mesh.
    bore = nr - 0.004
    geom = LatheGeometry(
        [(bore, z0), (co, z0), (co, z1), (bore, z1)],
        segments=64,
        closed=True,
    )
    for i in range(28):
        a = 2 * math.pi * i / 28
        rib = CylinderGeometry(0.0008, z1 - z0, radial_segments=5)
        rib.translate(co + 0.0004, 0.0, (z0 + z1) / 2)
        rib.rotate_z(a)
        geom.merge(rib)
    return mesh_from_geometry(geom, "collar_shell")


def _oversized_collar_mesh(r: ResolvedContainerDispenserConfig):
    """Two-tier industrial stepped collar: lower thread ribs + upper flutes +
    knurl band + top lip (ribbed_collar fork)."""
    z0, z1 = _collar_band_local(r)
    band = z1 - z0
    z_step = z0 + band * 0.50
    nr = r.neck_r
    lower_r = r.collar_outer_r
    upper_r = r.collar_outer_r * 0.80
    bore = nr - 0.004  # reach near the axis (clears the pump stem)
    geom = LatheGeometry(
        [
            (bore, z0),
            (lower_r + 0.003, z0),
            (lower_r + 0.001, z0 + 0.006),
            (lower_r, z_step - 0.004),
            (lower_r - 0.001, z_step),
            (upper_r + 0.002, z_step + 0.003),
            (upper_r, z_step + 0.008),
            (upper_r, z1 - 0.004),
            (upper_r - 0.004, z1),
            (bore, z1),
        ],
        segments=72,
        closed=True,
    )
    n_ribs = 10
    for i in range(n_ribs):
        z = z0 + 0.004 + (z_step - z0 - 0.008) * i / max(n_ribs - 1, 1)
        rib = TorusGeometry(lower_r, 0.0020, radial_segments=6, tubular_segments=72)
        rib.translate(0.0, 0.0, z)
        geom.merge(rib)
    n_flutes = 28
    flute_h = max(z1 - z_step - 0.012, 0.006)
    for i in range(n_flutes):
        a = 2 * math.pi * i / n_flutes
        flute = CylinderGeometry(0.0020, flute_h, radial_segments=6)
        flute.translate(upper_r + 0.001, 0.0, z_step + 0.006 + flute_h / 2)
        flute.rotate_z(a)
        geom.merge(flute)
    knurl_z = z_step + (z1 - z_step) * 0.48
    band_ring = TorusGeometry(upper_r + 0.0012, 0.0020, radial_segments=8, tubular_segments=72)
    band_ring.translate(0.0, 0.0, knurl_z)
    geom.merge(band_ring)
    for i in range(40):
        a = 2 * math.pi * i / 40
        bump = CylinderGeometry(0.0009, 0.005, radial_segments=4)
        bump.rotate_x(math.pi / 2)
        bump.translate(upper_r + 0.001, 0.0, knurl_z)
        bump.rotate_z(a)
        geom.merge(bump)
    lip = TorusGeometry(upper_r - 0.001, 0.0015, radial_segments=6, tubular_segments=72)
    lip.translate(0.0, 0.0, z1 - 0.001)
    geom.merge(lip)
    return mesh_from_geometry(geom, "collar_shell")


def _collar_mesh(r: ResolvedContainerDispenserConfig):
    if r.neck_collar == "oversized_industrial_collar":
        return _oversized_collar_mesh(r)
    return _standard_collar_mesh(r)


# ---------------------------------------------------------------------------
# Lock ring geometry (twist_lock_pump only). Authored in LOCK-RING-LOCAL frame:
# the REVOLUTE joint origin sits at world z = collar_z1, so local z=0 is the
# ring bottom (flush on the collar top).
# ---------------------------------------------------------------------------
def _lock_ring_mesh(r: ResolvedContainerDispenserConfig):
    """Narrow twist-lock ring: thin annular lathe + grip tabs + indicator
    bumps + cam-slot grooves (twist_lock fork)."""
    ring_h = 0.005
    z0, z1 = 0.0, ring_h
    r_outer = max(r.collar_outer_r + 0.0015, 0.020)
    # Inner edge reaches close to the axis (still clears the pump stem) so the
    # on-axis REVOLUTE twist origin sits within the lock ring mesh.
    r_inner = r.neck_r - 0.004
    geom = LatheGeometry(
        [
            (r_inner, z0),
            (r_outer, z0),
            (r_outer, z1),
            (r_outer - 0.001, z1 + 0.0005),
            (r_inner + 0.001, z1 + 0.0005),
            (r_inner, z1),
        ],
        segments=64,
        closed=True,
    )
    tab_w = 0.004
    tab_proud = 0.0015
    for sign in (1, -1):
        tab = BoxGeometry((tab_w, tab_proud, ring_h))
        tab.translate(sign * (r_outer + tab_proud / 2), 0.0, (z0 + z1) / 2)
        geom.merge(tab)
    for angle_deg in (90, 270):
        a = math.radians(angle_deg)
        bump = CylinderGeometry(0.0008, 0.0008, radial_segments=6)
        bump.translate(
            (r_outer + 0.0004) * math.cos(a),
            (r_outer + 0.0004) * math.sin(a),
            (z0 + z1) / 2,
        )
        geom.merge(bump)
    for i in range(4):
        a = math.pi / 2 * i + math.pi / 8
        r_mid = (r_outer + r_inner) / 2
        slot = BoxGeometry((0.004, 0.002, 0.001))
        slot.translate(r_mid, 0.0, z1 + 0.0005)
        slot.rotate_z(a)
        geom.merge(slot)
    return mesh_from_geometry(geom, "lock_ring_shell")


# ---------------------------------------------------------------------------
# Pump head geometry (Slot B). Authored in PUMP-LOCAL frame: the PRISMATIC
# press joint origin sits at world z = pump_mount_z, so local z=0 is the collar
# top. The stem descends below 0 (down through the collar bore); the head /
# button rise above 0. ``z`` below = world z - pump_mount_z.
# ---------------------------------------------------------------------------
def _press_swivel_pump_mesh(r: ResolvedContainerDispenserConfig):
    """Baseline pump head: slim stem -> wider body -> shoulder -> press disk."""
    m = r.pump_mount_z
    stem_bottom = r.collar_z0 - 0.004 - m  # down into the collar bore
    body_z0 = -0.001
    body_z1 = 0.034
    geom = LatheGeometry(
        [
            (0.004, stem_bottom),
            (0.006, stem_bottom),
            (0.006, body_z0),
            (0.017, body_z0),
            (0.017, body_z1),
            (0.010, body_z1 + 0.006),
            (0.004, body_z1 + 0.006),
        ],
        segments=56,
        closed=True,
    )
    disk = CylinderGeometry(0.020, 0.007, radial_segments=48)
    disk.translate(0.0, 0.0, body_z1 + 0.0095)
    geom.merge(disk)
    return mesh_from_geometry(geom, "pump_head_shell")


def _long_spout_pump_mesh(r: ResolvedContainerDispenserConfig):
    """Tall slim-plunger lotion pump: long stem + wider body + oval press
    button (long_spout fork)."""
    m = r.pump_mount_z
    stem_bottom = r.collar_z0 - 0.004 - m
    stem_r = 0.005
    body_z0 = -0.004
    # Wide body band raised so the swivel spout can socket high (z=0.028) and ride
    # above the collar top through the full press stroke; the slim plunger still
    # rises above it to the button.
    body_z1 = 0.030
    body_r = 0.016
    stem_z1 = 0.050  # tall plunger top
    geom = LatheGeometry(
        [
            (0.004, stem_bottom),
            (stem_r, stem_bottom),
            (stem_r, body_z0),
            (body_r, body_z0 + 0.002),
            (body_r, body_z1),
            (stem_r + 0.001, body_z1 + 0.002),
            (stem_r + 0.001, stem_z1),
            (stem_r + 0.002, stem_z1 + 0.002),
            (0.004, stem_z1 + 0.002),
        ],
        segments=48,
        closed=True,
    )
    # oval press button
    button_z = stem_z1 + 0.002
    button_rx, button_ry, button_h = 0.016, 0.012, 0.006
    n_seg = 48
    button = MeshGeometry()
    bottom_ring, top_ring = [], []
    for i in range(n_seg):
        a = 2 * math.pi * i / n_seg
        x = button_rx * math.cos(a)
        y = button_ry * math.sin(a)
        bottom_ring.append(button.add_vertex(x, y, button_z))
        top_ring.append(button.add_vertex(x, y, button_z + button_h))
    for i in range(n_seg):
        j = (i + 1) % n_seg
        button.add_face(bottom_ring[i], bottom_ring[j], top_ring[j])
        button.add_face(bottom_ring[i], top_ring[j], top_ring[i])
    bc = button.add_vertex(0.0, 0.0, button_z)
    tc = button.add_vertex(0.0, 0.0, button_z + button_h)
    for i in range(n_seg):
        j = (i + 1) % n_seg
        button.add_face(bc, bottom_ring[j], bottom_ring[i])
        button.add_face(tc, top_ring[i], top_ring[j])
    geom.merge(button)
    neck = CylinderGeometry(stem_r + 0.002, button_z - stem_z1 + 0.001, radial_segments=24)
    neck.translate(0.0, 0.0, (stem_z1 + button_z) / 2)
    geom.merge(neck)
    return mesh_from_geometry(geom, "pump_head_shell")


def _service_lift_pump_mesh(r: ResolvedContainerDispenserConfig):
    """Serviceable pump insert: stem with a wider seal/guide ring inside the
    collar bore (service_lift fork)."""
    m = r.pump_mount_z
    stem_bottom = r.collar_z0 - 0.004 - m
    seal_r = 0.0155
    seal_z0 = (r.collar_z0 + 0.006) - m
    seal_z1 = (r.collar_z1 - 0.003) - m
    body_z0 = -0.001
    body_z1 = 0.034
    geom = LatheGeometry(
        [
            (0.004, stem_bottom),
            (0.006, stem_bottom),
            (0.006, seal_z0),
            (seal_r, seal_z0 + 0.003),
            (seal_r, seal_z1 - 0.003),
            (0.006, seal_z1),
            (0.006, body_z0),
            (0.017, body_z0),
            (0.017, body_z1),
            (0.010, body_z1 + 0.006),
            (0.004, body_z1 + 0.006),
        ],
        segments=56,
        closed=True,
    )
    disk = CylinderGeometry(0.020, 0.007, radial_segments=48)
    disk.translate(0.0, 0.0, body_z1 + 0.0095)
    geom.merge(disk)
    return mesh_from_geometry(geom, "pump_head_shell")


def _twist_lock_pump_mesh(r: ResolvedContainerDispenserConfig):
    """Baseline-shaped pump head plus small engagement pins that ride the lock
    ring cam slots (twist_lock fork). Stem reaches down past the lock ring."""
    m = r.pump_mount_z
    stem_bottom = r.collar_z0 - 0.004 - m
    body_z0 = -0.001
    body_z1 = 0.034
    geom = LatheGeometry(
        [
            (0.004, stem_bottom),
            (0.006, stem_bottom),
            (0.006, body_z0),
            (0.017, body_z0),
            (0.017, body_z1),
            (0.010, body_z1 + 0.006),
            (0.004, body_z1 + 0.006),
        ],
        segments=56,
        closed=True,
    )
    disk = CylinderGeometry(0.020, 0.007, radial_segments=48)
    disk.translate(0.0, 0.0, body_z1 + 0.0095)
    geom.merge(disk)
    # Engagement pins ride out of the pump body wall (r~0.017) to sit in the
    # lock-ring cam slots; rooted in the body so they stay connected.
    pin_z = body_z0 + 0.004
    for i in range(2):
        a = math.pi * i + math.pi / 8
        pin = CylinderGeometry(0.0015, 0.006, radial_segments=6)
        pin.rotate_y(math.pi / 2)
        pin.translate(0.016 * math.cos(a), 0.016 * math.sin(a), pin_z)
        geom.merge(pin)
    return mesh_from_geometry(geom, "pump_head_shell")


def _pump_head_mesh(r: ResolvedContainerDispenserConfig):
    if r.pump_head == "long_spout_lotion_pump":
        return _long_spout_pump_mesh(r)
    if r.pump_head == "service_lift_pump":
        return _service_lift_pump_mesh(r)
    if r.pump_head == "twist_lock_pump":
        return _twist_lock_pump_mesh(r)
    return _press_swivel_pump_mesh(r)


# ---------------------------------------------------------------------------
# Spout geometry. Authored in the SPOUT-LOCAL frame: the REVOLUTE swivel joint
# origin coincides with the pump-local socket point (so spout local origin
# (0,0,0) is at the swivel axis). The spout reaches out along +X.
# ---------------------------------------------------------------------------
def _spout_socket_local_z(r: ResolvedContainerDispenserConfig) -> float:
    """World z of the spout swivel socket on the pump, expressed pump-local.

    Placed HIGH on the pump head (still within the widest body band so the spout
    root embeds — no support gap) so that when the head presses down the whole
    stroke the swivel spout's lowest point stays above the collar top rather than
    plunging into the collar / neck. The old mid-body sockets (0.006 / 0.012) sat
    only ~3 mm above the collar top at rest, so any press drove the spout in."""
    if r.pump_head == "long_spout_lotion_pump":
        # Widest band of the long-spout body now reaches to z=0.030 (see the
        # mesh); socket just below its top so the long spout rides high.
        return 0.028
    return 0.030


def _spout_mesh(r: ResolvedContainerDispenserConfig):
    reach = r.spout_reach_scale
    if r.pump_head == "long_spout_lotion_pump":
        # Long gently-curved horizontal spout + downward nozzle. Root starts
        # inside the pump body (r~0.016) so it embeds the head.
        sx = 0.010
        pts = [
            (sx, 0.0, 0.0),
            (sx + 0.018 * reach, 0.0, 0.012),
            (sx + 0.038 * reach, 0.0, 0.018),
            (sx + 0.060 * reach, 0.0, 0.016),
        ]
        geom = tube_from_spline_points(
            pts, radius=0.0042, samples_per_segment=12, radial_segments=16
        )
        nx = sx + 0.060 * reach
        nozzle = CylinderGeometry(0.0038, 0.009, radial_segments=16)
        nozzle.translate(nx, 0.0, 0.016 - 0.0045)
        geom.merge(nozzle)
        tip = CylinderGeometry(0.0042, 0.002, radial_segments=16)
        tip.translate(nx, 0.0, 0.016 - 0.010)
        geom.merge(tip)
        return mesh_from_geometry(geom, "spout_shell")
    # baseline short curved spout + axial tip.
    pts = [
        (0.013, 0.0, 0.001),
        (0.030 * reach, 0.0, 0.003),
        (0.047 * reach, 0.0, -0.006),
    ]
    geom = tube_from_spline_points(pts, radius=0.0038, samples_per_segment=10, radial_segments=14)
    tip = CylinderGeometry(0.0043, 0.008, radial_segments=16)
    tip.rotate_y(math.pi / 2)
    tip.translate(0.050 * reach, 0.0, -0.006)
    geom.merge(tip)
    return mesh_from_geometry(geom, "spout_shell")


# ---------------------------------------------------------------------------
# Dip tube geometry (Slot D). Authored in the DIP-TUBE-LOCAL frame: the FIXED
# joint origin sits at the tube top (world z = dip_top_z), so dip-tube local
# z=0 is the tube top. The tube descends to near the bottle base (negative
# local z). ``_dip_top_z`` returns that world z (= collar_z0 - 0.012).
# ---------------------------------------------------------------------------
def _dip_top_z(r: ResolvedContainerDispenserConfig) -> float:
    # The pump stem bottom sits at world z = collar_z0 - 0.004; the dip tube top
    # reaches up well past it so the tube plugs into the stem bore (captured fit,
    # allow_overlap). Extra overlap keeps the contact robust under scaling.
    return r.collar_z0 + 0.004


def _dip_tube_mesh(r: ResolvedContainerDispenserConfig):
    top = _dip_top_z(r)
    z_top = 0.0
    z_bot = 0.020 - top
    if r.dip_tube == "s_curved_dip_tube":
        # Keep the tube near-axis while it threads the (tight) neck / collar bore
        # so a service-lift withdrawal cannot pull the S-bend up through the
        # collar wall — the S only starts once the tube is below the collar, in
        # the wide bottle interior. (A real dip tube is straight through the
        # neck.) The near-axis run reaches below collar_z0 - the max up-lift.
        z_neck = 0.140 - top
        z_mid_hi = 0.108 - top
        z_mid_md = 0.078 - top
        z_mid_lo = 0.045 - top
        pts = [
            (0.000, 0.000, z_top),
            (0.003, 0.000, z_neck),
            (0.024, 0.004, z_mid_hi),
            (-0.018, -0.004, z_mid_md),
            (0.022, 0.006, z_mid_lo),
            (0.020, 0.000, z_bot),
        ]
        geom = tube_from_spline_points(
            pts, radius=0.0042, samples_per_segment=16, radial_segments=14
        )
        return mesh_from_geometry(geom, "dip_tube")
    z_mid = 0.115 - top
    pts = [
        (0.0, 0.0, z_top),
        (0.006, 0.0, z_mid),
        (0.004, 0.0, z_bot),
    ]
    geom = tube_from_spline_points(pts, radius=0.0030, samples_per_segment=12, radial_segments=10)
    # Short fat plug cap at the tube top that clearly seats up into the pump stem
    # bore (r~0.006), guaranteeing surface contact (captured fit, allow_overlap).
    plug = CylinderGeometry(0.0048, 0.012, radial_segments=16)
    plug.translate(0.0, 0.0, 0.004)
    geom.merge(plug)
    return mesh_from_geometry(geom, "dip_tube")


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_dispenser(
    config: ContainerDispenserConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    bottle_mat = model.material(f"cd_bottle_{r.palette_style}", rgba=pal.bottle)
    liquid_mat = model.material(f"cd_liquid_{r.palette_style}", rgba=pal.liquid)
    pump_mat = model.material(f"cd_pump_{r.palette_style}", rgba=pal.pump)
    accent_mat = model.material(f"cd_accent_{r.palette_style}", rgba=pal.accent)
    tube_mat = model.material(f"cd_tube_{r.palette_style}", rgba=pal.tube)
    label_mat = model.material(f"cd_label_{r.palette_style}", rgba=pal.label)

    # --- ROOT: bottle body (Slot A) -----------------------------------------
    bottle = model.part("bottle")
    bottle.visual(_bottle_mesh(r), material=bottle_mat, name="bottle_shell", material_class_id=("plastic.clear_rigid" if r.palette_style in {"clear_soap", "amber_lotion", "frosted_white", "blue_teal", "matte_black", "soft_touch_sage", "pearlescent_blush", "chrome_pump_clear", "sanitizer_aqua_gel"} else "ceramic.porcelain_glazed_plain"))
    bottle.visual(_front_label_mesh(r), material=label_mat, name="front_label", material_class_id="paper.plain_sheet")
    if not r.opaque_body:
        bottle.visual(_liquid_fill_mesh(r), material=liquid_mat, name="liquid_fill", material_class_id="liquid.water_wave_foam")
    bottle.inertial = Inertial.from_geometry(
        Cylinder(max(r.half_x, r.body_r), r.body_h),
        mass=0.22,
        origin=Origin(xyz=(0.0, 0.0, r.body_h / 2.0)),
    )

    # --- Slot C: collar (FIXED on the neck) ---------------------------------
    collar = model.part("collar")
    collar.visual(_collar_mesh(r), material=pump_mat, name="collar_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"clear_soap", "amber_lotion", "frosted_white", "blue_teal", "ceramic_cream", "matte_black", "soft_touch_sage", "pearlescent_blush", "sanitizer_aqua_gel"} else "metal.chrome_polished"))
    _cb0, _cb1 = _collar_band_local(r)
    collar.inertial = Inertial.from_geometry(
        Cylinder(r.collar_outer_r, r.collar_z1 - r.collar_z0),
        mass=0.018,
        origin=Origin(xyz=(0.0, 0.0, (_cb0 + _cb1) / 2.0)),
    )
    # Collar local origin sits at the neck rim (world z = neck_top).
    model.articulation(
        "bottle_to_collar",
        ArticulationType.FIXED,
        parent=bottle,
        child=collar,
        origin=Origin(xyz=(0.0, 0.0, r.neck_top)),
    )

    # --- twist_lock: lock_ring REVOLUTE on the collar top -------------------
    parent_for_head = collar
    head_parent_z_offset = r.neck_top  # world z of head-parent (collar) local origin
    if r.pump_head == "twist_lock_pump":
        lock_ring = model.part("lock_ring")
        lock_ring.visual(_lock_ring_mesh(r), material=accent_mat, name="lock_ring_shell", material_class_id=("plastic.opaque_generic" if r.palette_style in {"clear_soap", "amber_lotion", "frosted_white", "blue_teal", "ceramic_cream", "matte_black", "soft_touch_sage", "pearlescent_blush", "sanitizer_aqua_gel"} else "metal.chrome_polished"))
        lock_ring.inertial = Inertial.from_geometry(
            Cylinder(max(r.collar_outer_r + 0.0015, 0.020), 0.006),
            mass=0.004,
            origin=Origin(xyz=(0.0, 0.0, 0.003)),
        )
        # lock ring local origin = world z collar_z1; collar-local origin is at
        # world z neck_top, so the joint origin in collar frame is collar_z1 -
        # neck_top (= the collar band top, local).
        model.articulation(
            "lock_ring_twist",
            ArticulationType.REVOLUTE,
            parent=collar,
            child=lock_ring,
            origin=Origin(xyz=(0.0, 0.0, r.collar_z1 - r.neck_top)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=math.pi / 2),
        )
        parent_for_head = lock_ring
        head_parent_z_offset = r.collar_z1

    # --- Slot B: pump head (PRISMATIC press) --------------------------------
    pump = model.part("pump_head")
    pump.visual(_pump_head_mesh(r), material=pump_mat, name="pump_head_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"clear_soap", "amber_lotion", "frosted_white", "blue_teal", "ceramic_cream", "matte_black", "soft_touch_sage", "pearlescent_blush", "sanitizer_aqua_gel"} else "metal.chrome_polished"))
    pump.inertial = Inertial.from_geometry(
        Cylinder(0.020, 0.080),
        mass=0.035,
        origin=Origin(xyz=(0.0, 0.0, 0.005)),
    )
    if r.pump_head == "service_lift_pump":
        lower, upper = -0.012 * r.pump_travel_scale, 0.015 * r.pump_travel_scale
    else:
        lower, upper = -r.press_travel, 0.0
    # joint origin in head-parent local frame: pump_mount_z minus the parent's
    # local-origin world z.
    model.articulation(
        "pump_press",
        ArticulationType.PRISMATIC,
        parent=parent_for_head,
        child=pump,
        origin=Origin(xyz=(0.0, 0.0, r.pump_mount_z - head_parent_z_offset)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.15, lower=lower, upper=upper),
    )

    # --- Slot D: dip tube (FIXED under the pump stem) -----------------------
    # Dip tube is authored top-anchored (local z=0 at the tube top); the FIXED
    # joint origin sits at the tube top expressed in the pump-local frame.
    dip = model.part("dip_tube")
    dip.visual(_dip_tube_mesh(r), material=tube_mat, name="dip_tube", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"clear_soap", "amber_lotion", "frosted_white", "blue_teal", "ceramic_cream", "soft_touch_sage", "pearlescent_blush", "chrome_pump_clear", "sanitizer_aqua_gel"} else "plastic.opaque_generic"))
    dip_top = _dip_top_z(r)
    dip_len = dip_top - 0.020
    dip.inertial = Inertial.from_geometry(
        Cylinder(0.003, dip_len),
        mass=0.004,
        origin=Origin(xyz=(0.003, 0.0, -dip_len / 2.0)),
    )
    model.articulation(
        "pump_to_dip_tube",
        ArticulationType.FIXED,
        parent=pump,
        child=dip,
        origin=Origin(xyz=(0.0, 0.0, dip_top - r.pump_mount_z)),
    )

    # --- spout (REVOLUTE swivel on the pump side socket) --------------------
    spout = model.part("spout")
    spout.visual(_spout_mesh(r), material=pump_mat, name="spout_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"clear_soap", "amber_lotion", "frosted_white", "blue_teal", "ceramic_cream", "matte_black", "soft_touch_sage", "pearlescent_blush", "sanitizer_aqua_gel"} else "metal.chrome_polished"))
    spout.inertial = Inertial.from_geometry(
        Cylinder(0.005, 0.050),
        mass=0.006,
        origin=Origin(xyz=(0.030, 0.0, 0.0)),
    )
    model.articulation(
        "spout_swivel",
        ArticulationType.REVOLUTE,
        parent=pump,
        child=spout,
        origin=Origin(xyz=(0.0, 0.0, _spout_socket_local_z(r))),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=3.0, lower=-math.pi, upper=math.pi),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_dispenser(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_dispenser(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (collar over neck, pump stem in collar bore,
# dip tube inside the bottle, spout in the pump socket, lock ring on the collar)
# are declared element-scoped so the sweep's island / overlap checks pass; the
# pump press / spout swivel / lock twist actions are exercised.
# ---------------------------------------------------------------------------
def _z_top(ctx: TestContext, part, elem: str) -> float:
    aabb = ctx.part_element_world_aabb(part, elem=elem)
    return aabb[1][2] if aabb else -999.0


def _z_min(ctx: TestContext, part, elem: str) -> float:
    aabb = ctx.part_element_world_aabb(part, elem=elem)
    return aabb[0][2] if aabb else 999.0


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_dispenser_tests(
    object_model: ArticulatedObject,
    config: ContainerDispenserConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    bottle = object_model.get_part("bottle")
    collar = object_model.get_part("collar")
    pump = object_model.get_part("pump_head")
    dip = object_model.get_part("dip_tube")
    spout = object_model.get_part("spout")

    # ---- captured-fit overlap allowances (element-scoped) ----
    ctx.allow_overlap(
        collar,
        bottle,
        elem_a="collar_shell",
        elem_b="bottle_shell",
        reason="The threaded collar screws over the bottle neck.",
    )
    ctx.allow_overlap(
        pump,
        collar,
        elem_a="pump_head_shell",
        elem_b="collar_shell",
        reason="The pump stem passes through the collar bore.",
    )
    ctx.allow_overlap(
        pump,
        bottle,
        elem_a="pump_head_shell",
        elem_b="bottle_shell",
        reason="The pump stem passes through the bottle neck / shoulder interior.",
    )
    ctx.allow_overlap(
        dip,
        bottle,
        elem_a="dip_tube",
        elem_b="bottle_shell",
        reason="The suction dip tube runs inside the transparent bottle.",
    )
    if not r.opaque_body:
        ctx.allow_overlap(
            dip,
            bottle,
            elem_a="dip_tube",
            elem_b="liquid_fill",
            reason="The dip tube runs down through the visible liquid volume.",
        )
    ctx.allow_overlap(
        dip,
        pump,
        elem_a="dip_tube",
        elem_b="pump_head_shell",
        reason="The dip tube plugs into the pump stem bottom.",
    )
    ctx.allow_overlap(
        spout,
        pump,
        elem_a="spout_shell",
        elem_b="pump_head_shell",
        reason="The swivel spout plugs into the pump head side socket.",
    )
    if not r.opaque_body:
        ctx.allow_overlap(
            bottle,
            bottle,
            elem_a="liquid_fill",
            elem_b="bottle_shell",
            reason="The visible liquid volume is contained by the transparent bottle wall.",
        )

    # ---- bottle rests on the ground & has real volume ----
    aabb = ctx.part_world_aabb(bottle)
    bext = _ext(aabb)
    ctx.check(
        "bottle rests on the ground (base near z=0)",
        abs(aabb[0][2]) < 0.012,
        details=f"bottle min z={aabb[0][2]:.4f}",
    )
    ctx.check(
        "bottle has real volume",
        bext[0] > 0.02 and bext[1] > 0.01 and bext[2] > 0.05,
        details=f"bottle extents={bext}",
    )

    # ---- transparency assertion is per-colorway ----
    has_liquid = any(v.name == "liquid_fill" for v in bottle.visuals)
    if r.opaque_body:
        ctx.check(
            "opaque colorway: bottle is fully opaque (no liquid shown)",
            bottle.get_visual("bottle_shell").material.rgba[3] >= 0.99 and not has_liquid,
            details=f"alpha={bottle.get_visual('bottle_shell').material.rgba[3]}, has_liquid={has_liquid}",
        )
    else:
        ctx.check(
            "transparent bottle material (alpha < 0.5)",
            bottle.get_visual("bottle_shell").material.rgba[3] < 0.5,
            details=f"alpha={bottle.get_visual('bottle_shell').material.rgba[3]}",
        )

    # ---- collar is FIXED, centered on the neck ----
    ctx.expect_overlap(collar, bottle, axes="xy", min_overlap=0.020, name="collar centered on neck")

    # ---- dip tube descends below the label into the bottle ----
    ctx.check(
        "dip tube descends below label (near bottle base)",
        _z_min(ctx, dip, "dip_tube") < 0.030,
        details=f"dip tube min z={_z_min(ctx, dip, 'dip_tube'):.4f}",
    )

    # ---- pump press: PRISMATIC +Z, head presses / lifts ----
    press = object_model.get_articulation("pump_press")
    ctx.check(
        "pump_press is PRISMATIC about +Z",
        press.articulation_type == ArticulationType.PRISMATIC and abs(press.axis[2]) > 0.99,
        details=f"axis={press.axis}, type={press.articulation_type}",
    )
    rest_z = ctx.part_world_position(pump)[2]
    if r.pump_head == "service_lift_pump":
        # service lift can withdraw upward (positive travel).
        up = 0.015 * r.pump_travel_scale
        with ctx.pose({press: up}):
            lifted_z = ctx.part_world_position(pump)[2]
        ctx.check(
            "service pump lifts upward (partially withdrawn)",
            lifted_z > rest_z + up * 0.5,
            details=f"rest={rest_z:.4f}, lifted={lifted_z:.4f}",
        )
    else:
        with ctx.pose({press: -r.press_travel}):
            pressed_z = ctx.part_world_position(pump)[2]
        ctx.check(
            "pump head presses downward",
            pressed_z < rest_z - r.press_travel * 0.5,
            details=f"rest={rest_z:.4f}, pressed={pressed_z:.4f}",
        )

    # ---- spout swivel: REVOLUTE +Z, observable horizontal rotation ----
    swivel = object_model.get_articulation("spout_swivel")
    ctx.check(
        "spout_swivel is REVOLUTE about +Z",
        swivel.articulation_type == ArticulationType.REVOLUTE and abs(swivel.axis[2]) > 0.99,
        details=f"axis={swivel.axis}, type={swivel.articulation_type}",
    )
    ext0 = ctx.part_element_world_aabb(spout, elem="spout_shell")
    with ctx.pose({swivel: math.pi / 2}):
        ext90 = ctx.part_element_world_aabb(spout, elem="spout_shell")
    ctx.check(
        "spout visibly swivels (x-extent shrinks at 90deg)",
        ext0 is not None
        and ext90 is not None
        and (ext0[1][0] - ext0[0][0]) > (ext90[1][0] - ext90[0][0]) + 0.008,
        details=f"x0={ext0[1][0] - ext0[0][0]:.4f}, x90={ext90[1][0] - ext90[0][0]:.4f}",
    )

    # ---- pump remains exposed (no cap): spout near / above pump top ----
    ctx.check(
        "pump spout remains exposed like the reference",
        _z_top(ctx, spout, "spout_shell") > _z_top(ctx, pump, "pump_head_shell") - 0.040,
    )

    # ---- twist_lock: lock_ring REVOLUTE +Z quarter turn ----
    if r.pump_head == "twist_lock_pump":
        ring = object_model.get_part("lock_ring")
        twist = object_model.get_articulation("lock_ring_twist")
        ctx.allow_overlap(
            ring,
            collar,
            elem_a="lock_ring_shell",
            elem_b="collar_shell",
            reason="The lock ring rides around the collar throat.",
        )
        ctx.allow_overlap(
            pump,
            ring,
            elem_a="pump_head_shell",
            elem_b="lock_ring_shell",
            reason="Pump engagement pins ride in the lock ring cam slots.",
        )
        ctx.check(
            "lock_ring_twist is REVOLUTE about +Z, quarter turn",
            twist.articulation_type == ArticulationType.REVOLUTE
            and abs(twist.axis[2]) > 0.99
            and twist.motion_limits is not None
            and twist.motion_limits.upper is not None
            and twist.motion_limits.upper >= math.pi / 2 - 0.001,
            details=f"type={twist.articulation_type}, axis={twist.axis}",
        )

    # ---- body-form identity assertions ----
    body_aabb = ctx.part_element_world_aabb(bottle, elem="bottle_shell")
    if body_aabb is not None:
        dx = body_aabb[1][0] - body_aabb[0][0]
        dy = body_aabb[1][1] - body_aabb[0][1]
        if r.body_form == "oval_flask_body":
            ctx.check(
                "flask body is a flat lens (width >> depth)",
                dx > dy * 2.6,
                details=f"dx={dx:.4f}, dy={dy:.4f}",
            )
        elif r.body_form == "narrow_oval_footprint":
            ctx.check(
                "narrow oval body is flattened front-to-back",
                dx > dy * 1.30,
                details=f"dx={dx:.4f}, dy={dy:.4f}",
            )
        elif r.body_form == "square_prism_footprint":
            ctx.check(
                "square prism body has broad flat (dx ~= dy) footprint",
                abs(dx - dy) < 0.006,
                details=f"dx={dx:.4f}, dy={dy:.4f}",
            )
        elif r.body_form == "square_rounded_body":
            ctx.check(
                "rounded square body is wide and squat (dx ~= dy)",
                abs(dx - dy) < 0.006 and dx > 0.060,
                details=f"dx={dx:.4f}, dy={dy:.4f}",
            )

    # ---- pressing / lifting the pump keeps the swivel spout and dip tube clear
    # of the collar and bottle (the head + spout + dip ride with the plunger; the
    # captured-fit pass-throughs — pump stem in the collar bore, dip tube in the
    # bottle — are exempted). Scans the press extremes across swivel angles so a
    # spout plunging INTO the collar or a lifted dip tube spearing the collar wall
    # is caught, not just the rest pose. ----
    press_j = object_model.get_articulation("pump_press")
    captured = [("pump_head", "collar"), ("pump_head", "bottle"), ("dip_tube", "bottle")]
    press_lo = press_j.motion_limits.lower
    press_hi = press_j.motion_limits.upper
    press_samples = {0.0, press_lo, press_hi}
    swivels = (-math.pi, -math.pi / 2, 0.0, math.pi / 2, math.pi)
    motion_clear = min(
        min_clearance_at_pose(
            object_model,
            joint="pump_press",
            joint_positions={"pump_press": float(pz), "spout_swivel": float(sw)},
            keepout=["collar", "bottle"],
            allowed_pairs=captured,
        )
        for pz in press_samples
        for sw in swivels
    )
    ctx.check(
        "spout + dip clear the collar/bottle throughout the press & swivel range",
        motion_clear > 0.002,
        details=f"min spout/dip vs collar,bottle clearance over press+swivel={motion_clear:.5f}",
    )

    # ---- at least one non-fixed mechanism joint exists ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed pump joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()
