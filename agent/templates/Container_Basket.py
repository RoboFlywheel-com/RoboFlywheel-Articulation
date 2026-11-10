# SPDX-License-Identifier: Apache-2.0

"""Container basket — modular procedural template (lidded woven rattan basket).

Category identity: an upright hollow woven rattan / cane storage basket that
rests on the ground (base near z=0, centered on x=0,y=0). The ``basket_body``
(ROOT) is emitted strand-by-strand through a shared ``tube_from_spline_points``
helper (SDK tube + ``mesh_from_geometry``): a braided foot ring, a crossed-cane
woven floor, vertical ``stakes`` (``for j``), a selectable horizontal wall-weave
layer (``for i``), and a braided mouth rim. Above the mouth a lid opens by one of
three mechanisms (the main articulation), optionally carries a grip feature, and
the body may carry one pair of woven side handles.

Four slot axes + one multiplicity axis (spec ``Container_Basket.md``):

  * ``body_form`` (5) — ROOT ``basket_body`` mesh profile family: round (radius
    of z), hexagonal (6-vertex perimeter), oval (superellipse n=3.15),
    rectangular (superellipse n=5.2), cylindrical (straight radius of z). This
    drives the perimeter helper ``_profile_point``; floor / stakes / wall-weave /
    braided rim all share it. Not an independent chain slot but it joins the
    cartesian product.
  * ``lid_closure`` (3) — the lid mechanism (>=1 non-fixed joint each):
      - prismatic_liftoff: single PRISMATIC +Z lift-off cover (parent baseline).
      - hinged_flip_lid: REVOLUTE +X flip at the back rim; lid geometry is
        ``_offset_y(+mouth_r)`` so the woven disc caps the mouth at q=0; visible
        hinge barrels (body) interleave with knuckles (lid).
      - bail_swing_handle: fixed-fit PRISMATIC +Z lid PLUS a swinging woven
        ``carry_bail`` part on a REVOLUTE +Y joint through two rim lugs.
  * ``lid_grip`` (6) — the grip on the lid (fixed visuals, except the twist
    knob which adds a REVOLUTE +Z part):
      - bare: no grip part (woven lid only).
      - raised_oval_knob: low woven oval knob (2 braid rings + 12 risers).
      - raised_rect_handle: small box handle (2 rims + 16 stakes + top weave).
      - black_ring_handle: upright black ring loop + 2 mount posts.
      - arched_carry_bail: tall FIXED picnic bail (2 posts + parabolic arch).
      - twist_turn_knob_latch: a separate ``turn_knob`` part on a REVOLUTE +Z
        quarter-turn joint, with 4 lug arms engaging body rim slots.
  * ``wall_weave`` (5) — the body side-wall layer: dense_over_under (baseline),
    patterned_wall_weave (wave bands + stitches + herringbone), diagonal_twill
    (two spiral over-2-under-2 families), dense_checker (row-phase checker),
    banded_wave (lobed sinusoidal bands + girdles).
  * ``side_handle_count`` (multiplicity {0,2}, weighted {0:0.6, 2:0.4}) — one
    pair of woven side carry handles on the body wall (fixed visuals, no joint),
    placed at the +/-Y faces; N=2 only for non-round body forms (round's strong
    belly would float a recessed grip → forced 0).

Continuous size/proportion variation (height/radius/lid-overhang/grip/travel
scales) lives in ``resolve_config`` as clamped params, never as slot candidates.

Sources (articraft_data ``picture/Container/Basket`` 5-star pool): 5 parents
(round ``66ae2d28``, hex ``a27c9e51``, oval ``003basket``, rect ``99719568``,
cyl ``basket005``) + 9 ``rec_container_basket_var_*`` forks (hinged_flip_lid,
bail_swing_handle, arched_carry_bail, twist_turn_knob_latch, open_lattice_weave,
diagonal_twill_weave, dense_checker_weave, banded_wave_weave, side_carry_handles).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Container_Basket.md``
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
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    tube_from_spline_points as _sdk_tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyForm = Literal["round", "hexagonal", "oval", "rectangular", "cylindrical"]
LidClosure = Literal["prismatic_liftoff", "hinged_flip_lid", "bail_swing_handle"]
LidGrip = Literal[
    "bare",
    "raised_oval_knob",
    "raised_rect_handle",
    "black_ring_handle",
    "arched_carry_bail",
    "twist_turn_knob_latch",
]
WallWeave = Literal[
    "dense_over_under",
    "patterned_wall_weave",
    "diagonal_twill_weave",
    "dense_checker_weave",
    "banded_wave_weave",
]
PaletteStyle = Literal[
    "natural_tan",
    "honey_rattan",
    "dark_walnut_reed",
    "teal_red_accent",
    "two_tone_wheat_umber",
    "black_handle_natural",
    "lacquered_chestnut",
    "sage_powdercoat_wire",
    "seagrass_natural",
    "charcoal_painted",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "round",
    "hexagonal",
    "oval",
    "rectangular",
    "cylindrical",
)
LID_CLOSURES: tuple[LidClosure, ...] = (
    "prismatic_liftoff",
    "hinged_flip_lid",
    "bail_swing_handle",
)
LID_GRIPS: tuple[LidGrip, ...] = (
    "bare",
    "raised_oval_knob",
    "raised_rect_handle",
    "black_ring_handle",
    "arched_carry_bail",
    "twist_turn_knob_latch",
)
WALL_WEAVES: tuple[WallWeave, ...] = (
    "dense_over_under",
    "patterned_wall_weave",
    "diagonal_twill_weave",
    "dense_checker_weave",
    "banded_wave_weave",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "natural_tan",
    "honey_rattan",
    "dark_walnut_reed",
    "teal_red_accent",
    "two_tone_wheat_umber",
    "black_handle_natural",
    "lacquered_chestnut",
    "sage_powdercoat_wire",
    "seagrass_natural",
    "charcoal_painted",
)

# Body forms with near-vertical flat-ish sides that can carry a recessed side
# grip. Round's strong belly floats a recessed loop -> N forced to 0.
_FLAT_SIDE_FORMS: frozenset[BodyForm] = frozenset(
    {"hexagonal", "oval", "rectangular", "cylindrical"}
)

# ---------------------------------------------------------------------------
# Palettes — 10 coordinated colorways x explicit finish (nominal). Each carries
# body weave (light / mid / shadow), lid (light / shadow), grip, and an optional
# trim/accent. Grip/trim colors are only consumed when the picked grip/weave
# actually emits that part (palette never adds parts). Anchored to 5-star source
# rgba for the first 6; the last 3 are same-family inferred colorways.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Palette:
    finish: str
    light: tuple[float, float, float, float]
    mid: tuple[float, float, float, float]
    shadow: tuple[float, float, float, float]
    lid_light: tuple[float, float, float, float]
    lid_shadow: tuple[float, float, float, float]
    grip: tuple[float, float, float, float]
    accent: tuple[float, float, float, float]


def _rgb(r: float, g: float, b: float) -> tuple[float, float, float, float]:
    return (r, g, b, 1.0)


PALETTES: dict[PaletteStyle, _Palette] = {
    "natural_tan": _Palette(
        finish="matte_natural",
        light=_rgb(0.91, 0.72, 0.40),
        mid=_rgb(0.80, 0.58, 0.28),
        shadow=_rgb(0.56, 0.35, 0.14),
        lid_light=_rgb(0.88, 0.67, 0.35),
        lid_shadow=_rgb(0.68, 0.45, 0.20),
        grip=_rgb(0.78, 0.55, 0.24),
        accent=_rgb(0.56, 0.35, 0.14),
    ),
    "honey_rattan": _Palette(
        finish="lacquered",
        light=_rgb(0.91, 0.70, 0.38),
        mid=_rgb(0.76, 0.50, 0.21),
        shadow=_rgb(0.49, 0.30, 0.11),
        lid_light=_rgb(0.91, 0.70, 0.38),
        lid_shadow=_rgb(0.49, 0.30, 0.11),
        grip=_rgb(0.84, 0.62, 0.30),
        accent=_rgb(0.34, 0.20, 0.07),
    ),
    "dark_walnut_reed": _Palette(
        finish="lacquered",
        light=_rgb(0.78, 0.53, 0.28),
        mid=_rgb(0.62, 0.39, 0.18),
        shadow=_rgb(0.36, 0.22, 0.10),
        lid_light=_rgb(0.76, 0.51, 0.25),
        lid_shadow=_rgb(0.52, 0.31, 0.13),
        grip=_rgb(0.60, 0.37, 0.17),
        accent=_rgb(0.36, 0.22, 0.10),
    ),
    "teal_red_accent": _Palette(
        finish="two_tone_stained",
        light=_rgb(0.90, 0.68, 0.36),
        mid=_rgb(0.76, 0.50, 0.22),
        shadow=_rgb(0.50, 0.31, 0.12),
        lid_light=_rgb(0.90, 0.68, 0.36),
        lid_shadow=_rgb(0.50, 0.31, 0.12),
        grip=_rgb(0.80, 0.56, 0.26),
        accent=_rgb(0.02, 0.48, 0.41),
    ),
    "two_tone_wheat_umber": _Palette(
        finish="two_tone_stained",
        light=_rgb(0.96, 0.80, 0.48),
        mid=_rgb(0.88, 0.66, 0.34),
        shadow=_rgb(0.40, 0.24, 0.10),
        lid_light=_rgb(0.90, 0.69, 0.38),
        lid_shadow=_rgb(0.48, 0.28, 0.12),
        grip=_rgb(0.88, 0.66, 0.34),
        accent=_rgb(0.56, 0.31, 0.13),
    ),
    "black_handle_natural": _Palette(
        finish="matte_natural",
        light=_rgb(0.78, 0.53, 0.28),
        mid=_rgb(0.62, 0.39, 0.18),
        shadow=_rgb(0.36, 0.22, 0.10),
        lid_light=_rgb(0.76, 0.51, 0.25),
        lid_shadow=_rgb(0.52, 0.31, 0.13),
        grip=_rgb(0.015, 0.012, 0.010),
        accent=_rgb(0.36, 0.22, 0.10),
    ),
    "lacquered_chestnut": _Palette(
        finish="lacquered",
        light=_rgb(0.70, 0.42, 0.16),
        mid=_rgb(0.55, 0.31, 0.13),
        shadow=_rgb(0.43, 0.24, 0.09),
        lid_light=_rgb(0.66, 0.40, 0.16),
        lid_shadow=_rgb(0.40, 0.22, 0.09),
        grip=_rgb(0.58, 0.34, 0.14),
        accent=_rgb(0.28, 0.16, 0.06),
    ),
    "sage_powdercoat_wire": _Palette(
        finish="powder_coated",
        light=_rgb(0.52, 0.58, 0.46),
        mid=_rgb(0.42, 0.48, 0.37),
        shadow=_rgb(0.30, 0.35, 0.26),
        lid_light=_rgb(0.50, 0.56, 0.44),
        lid_shadow=_rgb(0.34, 0.39, 0.29),
        grip=_rgb(0.42, 0.48, 0.37),
        accent=_rgb(0.30, 0.35, 0.26),
    ),
    "seagrass_natural": _Palette(
        finish="natural_fiber",
        light=_rgb(0.80, 0.74, 0.55),
        mid=_rgb(0.68, 0.61, 0.43),
        shadow=_rgb(0.50, 0.44, 0.30),
        lid_light=_rgb(0.78, 0.72, 0.53),
        lid_shadow=_rgb(0.54, 0.48, 0.33),
        grip=_rgb(0.68, 0.61, 0.43),
        accent=_rgb(0.62, 0.56, 0.40),
    ),
    "charcoal_painted": _Palette(
        finish="painted",
        light=_rgb(0.22, 0.22, 0.24),
        mid=_rgb(0.16, 0.16, 0.18),
        shadow=_rgb(0.10, 0.10, 0.12),
        lid_light=_rgb(0.20, 0.20, 0.22),
        lid_shadow=_rgb(0.12, 0.12, 0.14),
        grip=_rgb(0.30, 0.30, 0.33),
        accent=_rgb(0.30, 0.30, 0.33),
    ),
}


# ---------------------------------------------------------------------------
# Nominal body geometry per form (meters). Scaled per-build by resolve_config.
# All forms are normalized to seat on z=0 with H_BODY tall and centered.
# ---------------------------------------------------------------------------
H_BODY = 0.300
Z_FOOT = 0.008
Z_FLOOR = 0.018

# Per-form perimeter half-extents (ax, ay) at the mouth and superellipse power.
@dataclass(frozen=True)
class _FormGeom:
    ax: float  # half-extent in x at the widest belly
    ay: float  # half-extent in y at the widest belly
    super_n: float  # superellipse power (round/cyl use circle; hex special)
    belly: float  # extra belly bulge fraction at mid-height
    taper: float  # top mouth shrink fraction vs belly
    cylindrical: bool  # straight wall (cyl): minimal belly/taper
    hexagonal: bool


_FORMS: dict[BodyForm, _FormGeom] = {
    "round": _FormGeom(ax=0.150, ay=0.150, super_n=2.0, belly=0.10, taper=0.30, cylindrical=False, hexagonal=False),
    "hexagonal": _FormGeom(ax=0.150, ay=0.112, super_n=2.0, belly=0.07, taper=0.05, cylindrical=False, hexagonal=True),
    "oval": _FormGeom(ax=0.176, ay=0.120, super_n=3.15, belly=0.06, taper=0.03, cylindrical=False, hexagonal=False),
    "rectangular": _FormGeom(ax=0.150, ay=0.112, super_n=5.2, belly=0.05, taper=0.02, cylindrical=False, hexagonal=False),
    "cylindrical": _FormGeom(ax=0.124, ay=0.124, super_n=2.0, belly=0.03, taper=0.02, cylindrical=True, hexagonal=False),
}

# Strand thicknesses.
T_HORIZ = 0.0046
T_VERTICAL = 0.0032
T_RIM = 0.0052
T_LID = 0.0030
T_FLOOR = 0.0028
T_HANDLE = 0.0037
WEAVE_RELIEF = 0.0022

HORIZONTAL_ROWS = 22
STAKE_COUNT = 44
RING_SAMPLES = 200

# Lid nominal.
LID_DOME = 0.018
LID_SEAT_Z = H_BODY
LID_LIFT = 0.150
HINGE_UPPER = 2.0
BAIL_UPPER = math.pi
KNOB_TURN = math.pi / 2.0


@dataclass(frozen=True)
class ContainerBasketConfig:
    body_form: BodyForm = "round"
    lid_closure: LidClosure = "prismatic_liftoff"
    lid_grip: LidGrip = "bare"
    wall_weave: WallWeave = "dense_over_under"
    side_handle_count: int = 0
    palette_style: PaletteStyle = "natural_tan"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    lid_overhang_scale: float = 1.0
    grip_size_scale: float = 1.0
    joint_travel_scale: float = 1.0
    name: str = "container_basket"


@dataclass(frozen=True)
class ResolvedContainerBasketConfig:
    body_form: BodyForm
    lid_closure: LidClosure
    lid_grip: LidGrip
    wall_weave: WallWeave
    side_handle_count: int
    palette_style: PaletteStyle
    body_height_scale: float
    body_radius_scale: float
    lid_overhang_scale: float
    grip_size_scale: float
    joint_travel_scale: float
    finish: str
    # derived geometry
    ax: float
    ay: float
    super_n: float
    belly: float
    taper: float
    cylindrical: bool
    hexagonal: bool
    h_body: float
    mouth_ax: float  # half-extent in x at the mouth
    mouth_ay: float  # half-extent in y at the mouth
    mouth_r: float  # mean mouth radius (for joints / handles)
    lid_outer_ax: float
    lid_outer_ay: float
    lid_seat_z: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerBasketConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    body_form = rng.choice(BODY_FORMS)
    lid_closure = rng.choice(LID_CLOSURES)
    lid_grip = rng.choice(LID_GRIPS)
    wall_weave = rng.choice(WALL_WEAVES)
    # Weighted multiplicity: {0: 0.6, 2: 0.4}. Gating to N=0 for round happens
    # in resolve_config.
    side_handle_count = rng.choices((0, 2), weights=(0.6, 0.4), k=1)[0]
    return ContainerBasketConfig(
        body_form=body_form,
        lid_closure=lid_closure,
        lid_grip=lid_grip,
        wall_weave=wall_weave,
        side_handle_count=side_handle_count,
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.88, 1.15), 4),
        body_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        lid_overhang_scale=round(rng.uniform(0.95, 1.10), 4),
        grip_size_scale=round(rng.uniform(0.85, 1.15), 4),
        joint_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_basket_{seed}",
    )


def resolve_config(
    config: ContainerBasketConfig | None = None,
) -> ResolvedContainerBasketConfig:
    cfg = config or ContainerBasketConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    lid_closure = _pick(cfg.lid_closure, LID_CLOSURES)
    lid_grip = _pick(cfg.lid_grip, LID_GRIPS)
    wall_weave = _pick(cfg.wall_weave, WALL_WEAVES)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    g = _FORMS[body_form]
    h_scale = _clamp(cfg.body_height_scale, 0.88, 1.15)
    r_scale = _clamp(cfg.body_radius_scale, 0.90, 1.12)
    overhang = _clamp(cfg.lid_overhang_scale, 0.95, 1.10)
    grip_scale = _clamp(cfg.grip_size_scale, 0.85, 1.15)
    jt_scale = _clamp(cfg.joint_travel_scale, 0.85, 1.10)

    ax = g.ax * r_scale
    ay = g.ay * r_scale
    h_body = H_BODY * h_scale

    # Soft compatibility resolution (spec compatibility matrix):
    # (1) side_handle_count=2 only on flat-ish body forms; round -> 0.
    side_n = cfg.side_handle_count if cfg.side_handle_count in (0, 2) else 0
    if side_n == 2 and body_form not in _FLAT_SIDE_FORMS:
        side_n = 0
    # (3) arched_carry_bail (fixed bail grip) + bail_swing_handle (active bail
    # closure) -> two overhead bails collide; keep the active closure bail and
    # downgrade the grip to bare.
    if lid_grip == "arched_carry_bail" and lid_closure == "bail_swing_handle":
        lid_grip = "bare"

    # Mouth half-extents at the rim (taper applied vs belly).
    mouth_ax = ax * (1.0 - g.taper)
    mouth_ay = ay * (1.0 - g.taper)
    mouth_r = 0.5 * (mouth_ax + mouth_ay)

    # lid_overhang equation: the lid caps the mouth and overhangs it slightly.
    lid_outer_ax = mouth_ax * (1.0 + 0.07) * overhang
    lid_outer_ay = mouth_ay * (1.0 + 0.07) * overhang
    # Inequality projection: ensure the lid stays proud of the mouth (covers it)
    # and not absurdly larger than the belly.
    lid_outer_ax = _clamp(lid_outer_ax, mouth_ax + 0.004, ax + 0.030)
    lid_outer_ay = _clamp(lid_outer_ay, mouth_ay + 0.004, ay + 0.030)

    return ResolvedContainerBasketConfig(
        body_form=body_form,
        lid_closure=lid_closure,
        lid_grip=lid_grip,
        wall_weave=wall_weave,
        side_handle_count=side_n,
        palette_style=palette,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        lid_overhang_scale=overhang,
        grip_size_scale=grip_scale,
        joint_travel_scale=jt_scale,
        finish=PALETTES[palette].finish,
        ax=ax,
        ay=ay,
        super_n=g.super_n,
        belly=g.belly,
        taper=g.taper,
        cylindrical=g.cylindrical,
        hexagonal=g.hexagonal,
        h_body=h_body,
        mouth_ax=mouth_ax,
        mouth_ay=mouth_ay,
        mouth_r=mouth_r,
        lid_outer_ax=lid_outer_ax,
        lid_outer_ay=lid_outer_ay,
        lid_seat_z=h_body,
        name=cfg.name or "container_basket",
    )


def with_overrides(
    config: ContainerBasketConfig, **kwargs: object
) -> ContainerBasketConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerBasketConfig | ResolvedContainerBasketConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedContainerBasketConfig)
        else resolve_config(config)
    )
    side = "pair" if r.side_handle_count == 2 else "none"
    return (
        ("body_form", r.body_form),
        ("lid_closure", r.lid_closure),
        ("lid_grip", r.lid_grip),
        ("wall_weave", r.wall_weave),
        ("side_handle_count", side),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared tube helper. Wraps the SDK sweep + mesh_from_geometry with a unique
# name per strand (the canonical 5-star contract). Never downgrades to Box.
# ---------------------------------------------------------------------------
_TUBE_COUNTER = 0


def _tube(points, **kwargs):
    global _TUBE_COUNTER
    _TUBE_COUNTER += 1
    geom = _sdk_tube_from_spline_points(points, **kwargs)
    return mesh_from_geometry(geom, f"woven_rattan_tube_{_TUBE_COUNTER:04d}")


# ---------------------------------------------------------------------------
# Body profile: a unified perimeter for all body forms. s in [0,1) parameterizes
# the rim; returns the (x, y) on the perimeter at half-extents (hx, hy).
# ---------------------------------------------------------------------------
def _sgn(v: float) -> float:
    return math.copysign(1.0, v) if v != 0.0 else 0.0


def _hex_vertices(hx: float, hy: float) -> list[tuple[float, float]]:
    shoulder = 0.58 * hx
    return [
        (hx, 0.0),
        (shoulder, hy),
        (-shoulder, hy),
        (-hx, 0.0),
        (-shoulder, -hy),
        (shoulder, -hy),
    ]


def _profile_point(
    r: ResolvedContainerBasketConfig, s: float, hx: float, hy: float
) -> tuple[float, float]:
    """Perimeter point at parameter s in [0,1) for the resolved body form."""
    if r.hexagonal:
        verts = _hex_vertices(hx, hy)
        n = len(verts)
        seg = s * n
        edge = int(seg) % n
        u = seg - int(seg)
        a = verts[edge]
        b = verts[(edge + 1) % n]
        return (_lerp(a[0], b[0], u), _lerp(a[1], b[1], u))
    theta = 2.0 * math.pi * s
    power = 2.0 / r.super_n
    c = math.cos(theta)
    q = math.sin(theta)
    x = hx * _sgn(c) * (abs(c) ** power)
    y = hy * _sgn(q) * (abs(q) ** power)
    return (x, y)


def _outward_xy(x: float, y: float, hx: float, hy: float) -> tuple[float, float]:
    nx = x / max(hx, 1e-6)
    ny = y / max(hy, 1e-6)
    mag = math.hypot(nx, ny)
    if mag < 1e-9:
        return (1.0, 0.0)
    return (nx / mag, ny / mag)


def _half_extents_at_z(r: ResolvedContainerBasketConfig, z: float) -> tuple[float, float]:
    """Body half-extents at height z: bottom -> belly bulge -> tapered mouth."""
    t = _clamp((z - Z_FOOT) / max(r.h_body - Z_FOOT, 1e-6), 0.0, 1.0)
    if r.cylindrical:
        belly = math.sin(math.pi * t)
        hx = r.ax + 0.004 * belly - 0.003 * t * r.ax / 0.124
        hy = r.ay + 0.004 * belly - 0.003 * t * r.ay / 0.124
        return (hx, hy)
    bulge = math.sin(math.pi * t)
    # Bottom is a bit narrower, mid bulges out by belly, mouth tapers in.
    base_x = r.ax * (0.86 + 0.14 * t) - r.ax * r.taper * t
    base_y = r.ay * (0.86 + 0.14 * t) - r.ay * r.taper * t
    hx = base_x + r.ax * r.belly * bulge
    hy = base_y + r.ay * r.belly * bulge
    return (hx, hy)


def _ring_path(
    r: ResolvedContainerBasketConfig,
    z: float,
    hx: float,
    hy: float,
    *,
    samples: int = RING_SAMPLES,
    wave_count: int = 0,
    phase: float = 0.0,
    outward_amp: float = 0.0,
    z_amp: float = 0.0,
) -> list[tuple[float, float, float]]:
    points: list[tuple[float, float, float]] = []
    for i in range(samples):
        s = i / samples
        x, y = _profile_point(r, s, hx, hy)
        wave = math.cos(2.0 * math.pi * wave_count * s + phase) if wave_count else 0.0
        if outward_amp:
            nx, ny = _outward_xy(x, y, hx, hy)
            x += outward_amp * wave * nx
            y += outward_amp * wave * ny
        zz = z + (z_amp * math.sin(2.0 * math.pi * wave_count * s + phase) if wave_count else 0.0)
        points.append((x, y, zz))
    return points


def _braid_ring_path(
    r: ResolvedContainerBasketConfig,
    z: float,
    hx: float,
    hy: float,
    *,
    phase: float,
    turns: int,
    amp: float = 0.0024,
    samples: int = RING_SAMPLES,
) -> list[tuple[float, float, float]]:
    points: list[tuple[float, float, float]] = []
    for i in range(samples):
        s = i / samples
        x, y = _profile_point(r, s, hx, hy)
        twist = turns * 2.0 * math.pi * s + phase
        nx, ny = _outward_xy(x, y, hx, hy)
        off = amp * math.sin(twist)
        points.append((x + off * nx, y + off * ny, z + 0.65 * amp * math.cos(twist)))
    return points


def _stake_path(r: ResolvedContainerBasketConfig, s: float, index: int) -> list[tuple[float, float, float]]:
    points: list[tuple[float, float, float]] = []
    samples = 30
    for i in range(samples):
        t = i / (samples - 1)
        z = Z_FOOT + (r.h_body - Z_FOOT) * t
        hx, hy = _half_extents_at_z(r, z)
        x, y = _profile_point(r, s, hx, hy)
        nx, ny = _outward_xy(x, y, hx, hy)
        flutter = 0.0009 * math.sin(2.0 * math.pi * HORIZONTAL_ROWS * t + index * 0.41)
        off = 0.0012 + flutter
        points.append((x + off * nx, y + off * ny, z))
    return points


def _hex_axis_extent(
    hx: float, hy: float, offset: float, orientation: str
) -> float:
    """Axis-parallel half-extent of the hexagon at a fixed cross-line.

    For orientation "x" the cross-line is y=offset (return max |x| on the
    polygon at that y); for "y" the cross-line is x=offset (max |y|). Returns
    0.0 if the line misses the hull entirely.
    """
    verts = _hex_vertices(hx, hy)
    n = len(verts)
    best = 0.0
    hit = False
    for i in range(n):
        ax, ay = verts[i]
        bx, by = verts[(i + 1) % n]
        if orientation == "x":
            p0, p1, c0, c1 = ay, by, ax, bx  # cross on y, coordinate of interest x
        else:
            p0, p1, c0, c1 = ax, bx, ay, by  # cross on x, coordinate of interest y
        lo, hi = (p0, p1) if p0 <= p1 else (p1, p0)
        if offset < lo - 1e-9 or offset > hi + 1e-9:
            continue
        denom = p1 - p0
        if abs(denom) < 1e-12:
            # Edge parallel to the cross-line (offset lies on it): both endpoints.
            cand = max(abs(c0), abs(c1))
        else:
            t = (offset - p0) / denom
            cand = abs(c0 + (c1 - c0) * t)
        if cand > best:
            best = cand
        hit = True
    return best if hit else 0.0


def _chord_points(
    r: ResolvedContainerBasketConfig,
    offset: float,
    *,
    orientation: str,
    z_base: float,
    radius_a: float,
    radius_b: float,
    dome: float,
    phase: float,
    samples: int = 10,
    tube_radius: float = 0.0,
) -> list[tuple[float, float, float]]:
    """Floor / lid crossing strip clipped to the TRUE body/lid perimeter.

    The body & lid forms are superellipses (power ``r.super_n``; n=2 is a plain
    ellipse for round/cylindrical) or hexagonal. Clipping to a plain inscribed
    ellipse made oval/rect/hex strip ends float short of the wall/rim; we instead
    clip to the real perimeter so the ends seat into the braided wall/rim.

    The strips are cane TUBES of radius ``tube_radius`` whose rounded end cap
    extends ~tube_radius past the centerline endpoint. We therefore place the
    centerline endpoint ``tube_radius`` inside the perimeter so the tube's OUTER
    surface sits flush with the true wall/rim — touching it but not protruding
    past the basket's outer silhouette.
    """
    if r.hexagonal:
        half = _hex_axis_extent(radius_a, radius_b, offset, orientation)
    else:
        n = max(r.super_n, 1e-6)
        if orientation == "x":
            ratio = abs(offset) / max(radius_b, 1e-6)
            half = radius_a * max(0.0, 1.0 - ratio**n) ** (1.0 / n)
        else:
            ratio = abs(offset) / max(radius_a, 1e-6)
            half = radius_b * max(0.0, 1.0 - ratio**n) ** (1.0 / n)
    # Inset the centerline endpoint by the tube radius so the rounded end cap's
    # outer surface lands flush with the true perimeter, not past it.
    half = half - tube_radius
    # Keep samples valid even when the cross-line grazes the hull at a vertex.
    half = max(half, 1e-4)
    points: list[tuple[float, float, float]] = []
    for i in range(samples):
        u = -half + 2.0 * half * i / (samples - 1)
        if orientation == "x":
            x, y = u, offset
        else:
            x, y = offset, u
        rho2 = (x / max(radius_a, 1e-6)) ** 2 + (y / max(radius_b, 1e-6)) ** 2
        dome_z = dome * max(0.0, 1.0 - rho2)
        weave = 0.0010 * math.cos((i / (samples - 1)) * math.pi * 8.0 + phase)
        points.append((x, y, z_base + dome_z + weave))
    return points


# ---------------------------------------------------------------------------
# Body emission: floor + stakes + wall-weave + braided mouth rim.
# ---------------------------------------------------------------------------
def _emit_floor(body, r: ResolvedContainerBasketConfig, *, mats) -> None:
    # Floor strips must reach the wall so the floor weave is not a disconnected
    # island, but must not protrude past the basket's outer silhouette.
    # Clip floor strips to the TRUE foot-ring perimeter (no outward overshoot).
    # The per-strip tube-radius inset in _chord_points makes the tube's outer
    # surface land flush with the wall, and the ends still overlap the foot-ring
    # braid (a tube centered on this perimeter) so the floor stays connected.
    floor_ax, floor_ay = _half_extents_at_z(r, Z_FOOT)
    # Braided foot ring sits on the ground.
    body.visual(
        _tube(
            _ring_path(r, Z_FOOT, *_half_extents_at_z(r, Z_FOOT)),
            radius=T_RIM,
            closed_spline=True,
            samples_per_segment=1,
            radial_segments=10,
            cap_ends=False,
        ),
        material=mats["mid"],
        name="bottom_braided_foot_ring", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
    )
    n_floor = 7
    # Distribute the parallel strips across ~0.94 of the foot half-extent so the
    # weave fills the floor; each strip's ENDS are clipped to the true perimeter
    # (tube-radius inset) in _chord_points, so they reach the wall without
    # protruding regardless of where in this span the strip's offset falls.
    span = 2.0 * floor_ay * 0.94
    for i in range(n_floor):
        off = -0.5 * span + span * i / (n_floor - 1)
        body.visual(
            _tube(
                _chord_points(
                    r, off, orientation="x", z_base=Z_FLOOR - 0.003,
                    radius_a=floor_ax, radius_b=floor_ay, dome=0.0, phase=i * math.pi, samples=8,
                    tube_radius=T_FLOOR,
                ),
                radius=T_FLOOR, samples_per_segment=1, radial_segments=6, cap_ends=True,
            ),
            material=mats["light"] if i % 2 == 0 else mats["mid"],
            name=f"floor_weave_x_{i:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
        spanx = 2.0 * floor_ax * 0.94
        offx = -0.5 * spanx + spanx * i / (n_floor - 1)
        body.visual(
            _tube(
                _chord_points(
                    r, offx, orientation="y", z_base=Z_FLOOR - 0.001,
                    radius_a=floor_ax, radius_b=floor_ay, dome=0.0, phase=i * math.pi + math.pi, samples=8,
                    tube_radius=T_FLOOR,
                ),
                radius=T_FLOOR, samples_per_segment=1, radial_segments=6, cap_ends=True,
            ),
            material=mats["mid"] if i % 2 == 0 else mats["light"],
            name=f"floor_weave_y_{i:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    body.visual(
        Cylinder(radius=0.012, length=0.007),
        origin=Origin(xyz=(0.0, 0.0, Z_FLOOR - 0.003)),
        material=mats["shadow"],
        name="dark_floor_center_shadow", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
    )


def _emit_stakes(body, r: ResolvedContainerBasketConfig, *, mats, count: int) -> None:
    for j in range(count):
        s = j / count
        body.visual(
            _tube(
                _stake_path(r, s, j),
                radius=T_VERTICAL,
                samples_per_segment=2,
                radial_segments=7,
                cap_ends=True,
                up_hint=(1.0, 0.0, 0.0),
            ),
            material=mats["shadow"] if j % 4 == 0 else mats["mid"],
            name=f"vertical_weave_stake_{j:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )


def _emit_mouth_rim(body, r: ResolvedContainerBasketConfig, *, mats) -> None:
    hx, hy = _half_extents_at_z(r, r.h_body)
    for strand, phase in enumerate((0.0, math.pi)):
        body.visual(
            _tube(
                _braid_ring_path(r, r.h_body, hx + 0.003, hy + 0.003, phase=phase, turns=28),
                radius=T_RIM,
                closed_spline=True,
                samples_per_segment=1,
                radial_segments=10,
                cap_ends=False,
            ),
            material=mats["light"] if strand == 0 else mats["mid"],
            name=f"body_braided_mouth_rim_{strand}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    # Mouth-center locating cross: two thin cane spokes spanning the mouth and
    # crossing on the centerline at z=h_body. This is the seat the lift-off /
    # bail lid centers on, and gives the body real geometry AT the lid joint
    # origin (0,0,h_body) so it is not floating in the open mouth. The spokes
    # reach the rim, so they are part of the body's connected weave (no island).
    rim_z = r.h_body
    sag = 0.006
    for label, s_a, s_b in (("x", 0.0, 0.5), ("y", 0.25, 0.75)):
        ax_, ay_ = _profile_point(r, s_a, hx, hy)
        bx_, by_ = _profile_point(r, s_b, hx, hy)
        pts = []
        for k in range(13):
            t = k / 12
            x = _lerp(ax_, bx_, t)
            y = _lerp(ay_, by_, t)
            # Slight downward sag toward the center keeps the mouth readable as
            # open while planting geometry on the centerline.
            z = rim_z - sag * math.sin(math.pi * t)
            pts.append((x, y, z))
        body.visual(
            _tube(
                pts,
                radius=0.0030,
                samples_per_segment=1,
                radial_segments=6,
                cap_ends=True,
            ),
            material=mats["mid"] if label == "x" else mats["shadow"],
            name=f"mouth_center_spoke_{label}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )


def _z_rows(r: ResolvedContainerBasketConfig, count: int) -> list[float]:
    z0 = Z_FLOOR + 0.012
    z1 = r.h_body - 0.024
    return [z0 + (z1 - z0) * (i / (count - 1)) for i in range(count)]


def _emit_wall_dense_over_under(body, r: ResolvedContainerBasketConfig, *, mats) -> None:
    for i, z in enumerate(_z_rows(r, HORIZONTAL_ROWS)):
        hx, hy = _half_extents_at_z(r, z)
        body.visual(
            _tube(
                _ring_path(
                    r, z, hx, hy,
                    wave_count=STAKE_COUNT, phase=(i % 2) * math.pi,
                    outward_amp=WEAVE_RELIEF, z_amp=0.0008,
                ),
                radius=T_HORIZ,
                closed_spline=True,
                samples_per_segment=1,
                radial_segments=8,
                cap_ends=False,
            ),
            material=mats["light"] if i % 2 == 0 else mats["mid"],
            name=f"horizontal_weave_band_{i:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )


def _emit_wall_patterned(body, r: ResolvedContainerBasketConfig, *, mats) -> None:
    # Patterned wall: wave bands + short vertical stitches + herringbone stabs.
    bands = 18
    for row, z in enumerate(_z_rows(r, bands)):
        hx, hy = _half_extents_at_z(r, z)
        body.visual(
            _tube(
                _ring_path(
                    r, z, hx, hy,
                    wave_count=42, phase=row * 0.65,
                    outward_amp=0.0020, z_amp=0.0008,
                ),
                radius=T_HORIZ,
                closed_spline=True,
                samples_per_segment=1,
                radial_segments=8,
                cap_ends=False,
            ),
            material=mats["light"] if row % 3 == 0 else mats["mid"],
            name=f"woven_wall_wave_band_{row:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    z_rows = _z_rows(r, bands)
    stitch_cols = 48
    for col in range(stitch_cols):
        s = ((col + 0.5 * (col % 2)) / stitch_cols) % 1.0
        band = col % (bands - 2)
        z0 = z_rows[band]
        z1 = z_rows[band + 1]
        pts = []
        for i in range(7):
            t = i / 6
            z = _lerp(z0, z1, t)
            hx, hy = _half_extents_at_z(r, z)
            x, y = _profile_point(r, s, hx, hy)
            nx, ny = _outward_xy(x, y, hx, hy)
            tuck = 0.0014 + 0.0006 * math.sin(math.pi * t + col * 0.41)
            pts.append((x + tuck * nx, y + tuck * ny, z))
        body.visual(
            _tube(pts, radius=0.0030, samples_per_segment=1, radial_segments=6, cap_ends=True),
            material=mats["shadow"] if col % 3 == 0 else mats["mid"],
            name=f"woven_wall_short_vertical_stitch_{col:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    herring_cols = 44
    for col in range(herring_cols):
        band = col % (bands - 4)
        z0 = z_rows[band]
        for direction, label in ((1, "right"), (-1, "left")):
            s_mid = (col + 0.25) / herring_cols
            pts = []
            for i in range(9):
                t = i / 8
                z = z0 + 0.022 * t
                s = (s_mid + direction * 0.018 * (t - 0.5)) % 1.0
                hx, hy = _half_extents_at_z(r, z)
                x, y = _profile_point(r, s, hx, hy)
                nx, ny = _outward_xy(x, y, hx, hy)
                ou = 0.0016 + 0.0007 * math.sin(2.0 * math.pi * t + col * 0.31)
                pts.append((x + ou * nx, y + ou * ny, z))
            body.visual(
                _tube(pts, radius=0.0028, samples_per_segment=1, radial_segments=6, cap_ends=True),
                material=mats["light"] if (col % 2 == 0) else mats["mid"],
                name=f"woven_wall_herringbone_{label}_{col:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
            )


def _emit_wall_twill(body, r: ResolvedContainerBasketConfig, *, mats) -> None:
    twill_strands = 20
    twill_turns = 1.5
    for fam, (direction, family_phase, label) in enumerate(
        ((1, 0.0, "right"), (-1, math.pi, "left"))
    ):
        for i in range(twill_strands):
            theta_start = 2.0 * math.pi * i / twill_strands + (math.pi / twill_strands if fam else 0.0)
            pts = []
            samples = 110
            for k in range(samples):
                t = k / (samples - 1)
                z = Z_FOOT + (r.h_body - Z_FOOT) * t
                hx, hy = _half_extents_at_z(r, z)
                s = (theta_start / (2.0 * math.pi) + direction * twill_turns * t) % 1.0
                x, y = _profile_point(r, s, hx, hy)
                nx, ny = _outward_xy(x, y, hx, hy)
                weave = math.cos(STAKE_COUNT * 2.0 * math.pi * s / 4.0 + family_phase)
                off = 0.0014 + 0.0026 * weave
                pts.append((x + off * nx, y + off * ny, z))
            if fam == 0:
                mat = mats["light"] if i % 2 == 0 else mats["mid"]
            else:
                mat = mats["mid"] if i % 2 == 0 else mats["shadow"]
            body.visual(
                _tube(pts, radius=0.0044, samples_per_segment=2, radial_segments=7, cap_ends=True),
                material=mat,
                name=f"twill_strand_{label}_{i:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
            )


def _emit_wall_checker(body, r: ResolvedContainerBasketConfig, *, mats) -> None:
    checker_rows = 26
    for i, z in enumerate(_z_rows(r, checker_rows)):
        hx, hy = _half_extents_at_z(r, z)
        body.visual(
            _tube(
                _ring_path(
                    r, z, hx, hy,
                    wave_count=STAKE_COUNT, phase=i * math.pi,
                    outward_amp=0.0021, z_amp=0.0007,
                ),
                radius=T_HORIZ,
                closed_spline=True,
                samples_per_segment=1,
                radial_segments=8,
                cap_ends=False,
            ),
            material=mats["light"] if i % 2 == 0 else mats["mid"],
            name=f"checker_horizontal_band_{i:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )


def _emit_wall_banded_wave(body, r: ResolvedContainerBasketConfig, *, mats) -> None:
    wave_bands = 18
    wave_lobes = 8
    z_rows = _z_rows(r, wave_bands)
    for row, z in enumerate(z_rows):
        hx, hy = _half_extents_at_z(r, z)
        phase = (row % 4) * math.pi / 2.0
        primary_dark = (row // 3) % 2 == 1
        body.visual(
            _tube(
                _ring_path(
                    r, z, hx + 0.0018, hy + 0.0018,
                    wave_count=wave_lobes, phase=phase,
                    outward_amp=0.0034, z_amp=0.0042,
                ),
                radius=0.0040,
                closed_spline=True,
                samples_per_segment=1,
                radial_segments=8,
                cap_ends=False,
            ),
            material=mats["shadow"] if primary_dark else mats["light"],
            name=f"primary_horizontal_wave_band_{row:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
        hx2, hy2 = _half_extents_at_z(r, min(z + 0.0065, r.h_body - 0.020))
        body.visual(
            _tube(
                _ring_path(
                    r, z + 0.0065, hx2 + 0.0004, hy2 + 0.0004,
                    wave_count=wave_lobes, phase=phase + math.pi,
                    outward_amp=0.0026, z_amp=0.0034,
                ),
                radius=0.0029,
                closed_spline=True,
                samples_per_segment=1,
                radial_segments=8,
                cap_ends=False,
            ),
            material=mats["accent"] if primary_dark else mats["mid"],
            name=f"contrasting_reverse_wave_band_{row:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    girdle_zs = (
        Z_FLOOR + 0.030,
        0.5 * r.h_body,
        r.h_body - 0.045,
    )
    for k, z in enumerate(girdle_zs):
        hx, hy = _half_extents_at_z(r, z)
        body.visual(
            _tube(
                _ring_path(
                    r, z, hx + 0.0024, hy + 0.0024,
                    wave_count=wave_lobes, phase=k * math.pi / 2.0,
                    outward_amp=0.0030, z_amp=0.0030,
                ),
                radius=0.0050,
                closed_spline=True,
                samples_per_segment=1,
                radial_segments=9,
                cap_ends=False,
            ),
            material=mats["accent"] if k == 1 else mats["light"],
            name=f"wide_contrast_girdle_wave_band_{k}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )


_WALL_EMITTERS = {
    "dense_over_under": _emit_wall_dense_over_under,
    "patterned_wall_weave": _emit_wall_patterned,
    "diagonal_twill_weave": _emit_wall_twill,
    "dense_checker_weave": _emit_wall_checker,
    "banded_wave_weave": _emit_wall_banded_wave,
}


# ---------------------------------------------------------------------------
# Side handle pair (multiplicity, fixed body visuals; no joint).
# ---------------------------------------------------------------------------
def _emit_side_handles(body, r: ResolvedContainerBasketConfig, *, mats, count: int) -> None:
    if count <= 0:
        return
    handle_z = min(0.30 * r.h_body, r.lid_seat_z - 0.07)
    width = 0.052 * r.mouth_r / 0.135
    height = 0.040 * r.mouth_r / 0.135
    protrusion = 0.014
    wall_offset = 0.003
    anchor_spread = 0.008
    # +/-Y faces (perimeter s = 0.25 and 0.75).
    face_specs = [(0.25, (0.0, 1.0)), (0.75, (0.0, -1.0))]
    for i in range(count):
        s, outward = face_specs[i % 2]
        nx, ny = outward
        hx_h, hy_h = _half_extents_at_z(r, handle_z)
        fx, fy = _profile_point(r, s, hx_h, hy_h)
        tx, ty = -ny, nx
        ox = fx + protrusion * nx
        oy = fy + protrusion * ny
        loop = []
        for k in range(48):
            th = 2.0 * math.pi * k / 48
            along = 0.5 * width * math.cos(th)
            up = 0.5 * height * math.sin(th)
            loop.append((ox + along * tx, oy + along * ty, handle_z + up))
        body.visual(
            _tube(loop, radius=0.0040, closed_spline=True, samples_per_segment=1,
                  radial_segments=9, cap_ends=False),
            material=mats["shadow"],
            name=f"side_handle_loop_{i}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
        for j, z_sign in enumerate((1, -1)):
            z_ring = handle_z + z_sign * 0.5 * height
            z_wall = z_ring + z_sign * anchor_spread
            wall_pt = (fx + wall_offset * nx, fy + wall_offset * ny, z_wall)
            ring_pt = (fx + protrusion * nx, fy + protrusion * ny, z_ring)
            body.visual(
                _tube([wall_pt, ring_pt], radius=0.0045, samples_per_segment=1,
                      radial_segments=7, cap_ends=True),
                material=mats["mid"],
                name=f"side_handle_anchor_{i}_{j}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
            )
        for k, z_off in enumerate((-1.0, 1.0)):
            strip_z = handle_z + z_off * (0.5 * height + anchor_spread + 0.004)
            shx, shy = _half_extents_at_z(r, strip_z)
            ds = 0.022
            arc = []
            for sm in (s - ds, s, s + ds):
                px, py = _profile_point(r, sm % 1.0, shx, shy)
                pnx, pny = _outward_xy(px, py, shx, shy)
                arc.append((px + wall_offset * pnx, py + wall_offset * pny, strip_z))
            body.visual(
                _tube(arc, radius=0.0032, samples_per_segment=1, radial_segments=7, cap_ends=True),
                material=mats["light"] if k == 0 else mats["shadow"],
                name=f"side_handle_weave_trim_{i}_{k}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
            )


# ---------------------------------------------------------------------------
# Lid woven face + braided rim (built in a frame whose z=0 is the lid base).
# ---------------------------------------------------------------------------
def _emit_lid_face(lid, r: ResolvedContainerBasketConfig, *, mats, y_shift: float = 0.0) -> None:
    la = r.lid_outer_ax
    lb = r.lid_outer_ay
    # Weave strips clip right out to the braided rim radius so their ends meet the
    # braid ring (otherwise the rim is a disconnected island).
    weave_a = la
    weave_b = lb
    n_strips = 16
    span_y = 2.0 * weave_b * 0.97
    span_x = 2.0 * weave_a * 0.97
    for i in range(n_strips):
        offx = -0.5 * span_y + span_y * i / (n_strips - 1)
        pts = _chord_points(
            r, offx, orientation="x", z_base=0.006,
            radius_a=weave_a, radius_b=weave_b, dome=LID_DOME, phase=i * math.pi,
            tube_radius=T_LID,
        )
        pts = [(x, y + y_shift, z) for x, y, z in pts]
        lid.visual(
            _tube(pts, radius=T_LID, samples_per_segment=1, radial_segments=7, cap_ends=True),
            material=mats["lid_light"] if i % 2 == 0 else mats["lid_shadow"],
            name=f"lid_weave_x_strip_{i:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
        offy = -0.5 * span_x + span_x * i / (n_strips - 1)
        pts2 = _chord_points(
            r, offy, orientation="y", z_base=0.008,
            radius_a=weave_a, radius_b=weave_b, dome=LID_DOME, phase=i * math.pi + math.pi,
            tube_radius=T_LID,
        )
        pts2 = [(x, y + y_shift, z) for x, y, z in pts2]
        lid.visual(
            _tube(pts2, radius=T_LID, samples_per_segment=1, radial_segments=7, cap_ends=True),
            material=mats["lid_shadow"] if i % 2 == 0 else mats["lid_light"],
            name=f"lid_weave_y_strip_{i:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    for strand, phase in enumerate((0.0, math.pi)):
        pts = _braid_ring_path(r, 0.005, la, lb, phase=phase, turns=30, amp=0.0030)
        pts = [(x, y + y_shift, z) for x, y, z in pts]
        lid.visual(
            _tube(pts, radius=0.0058, closed_spline=True, samples_per_segment=1,
                  radial_segments=10, cap_ends=False),
            material=mats["lid_light"] if strand == 0 else mats["lid_shadow"],
            name=f"braided_lid_outer_rim_{strand}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    # Central woven knot at the lid's own local origin (0,0,~0). The lid frame
    # origin is the joint child point, so a small boss here keeps the joint
    # origin on real lid geometry (child distance check). It tucks under the
    # crossing weave strips, so it stays part of the connected lid mesh.
    # A short central cane stem rising from the lid local origin (0,0,0) up to
    # the domed center where the crossing weave strips meet (z ~ 0.006+LID_DOME).
    # The base plants geometry at the joint child point (0,0,0); the top tucks
    # into the crossing strips so it is connected (not an island). One continuous
    # cane: it rises on the centerline from (0,0,0) (planting geometry at the lid
    # local origin = joint child point) then spirals outward to ~0.014 radius at
    # the dome top, so a single tube reliably touches both the origin and the
    # nearest crossing strips (no strip lands exactly on the center).
    stem_top = 0.006 + LID_DOME + 0.001
    knot = [(0.0, y_shift, 0.0)]
    turns = 1.5
    n = 26
    for k in range(1, n + 1):
        t = k / n
        rad = 0.014 * t
        ang = 2.0 * math.pi * turns * t
        z = (0.5 * stem_top) + (stem_top - 0.5 * stem_top) * t
        knot.append((rad * math.cos(ang), rad * math.sin(ang) + y_shift, z))
    lid.visual(
        _tube(knot, radius=0.0042, samples_per_segment=2, radial_segments=8,
              cap_ends=True, up_hint=(1.0, 0.0, 0.0)),
        material=mats["lid_shadow"],
        name="lid_center_weave_knot", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
    )


# ---------------------------------------------------------------------------
# Lid grips (fixed visuals on the lid, except twist which adds a part). These
# are emitted in lid-local frame, shifted by y_shift for the flip-lid case.
# ---------------------------------------------------------------------------
def _emit_grip_oval_knob(lid, r: ResolvedContainerBasketConfig, *, mats, y_shift: float) -> None:
    a = 0.044 * r.grip_size_scale
    b = 0.024 * r.grip_size_scale
    base_z = 0.006 + LID_DOME + 0.004
    top_z = base_z + 0.018
    # base + top braids
    for k, (label, zz, aa, bb) in enumerate(
        (("base", base_z, a, b), ("top", top_z, a * 0.92, b * 0.92))
    ):
        for strand, phase in enumerate((0.0, math.pi)):
            pts = _braid_ring_path(r, zz, aa, bb, phase=phase, turns=12, amp=0.0022)
            pts = [(x, y + y_shift, z) for x, y, z in pts]
            lid.visual(
                _tube(pts, radius=T_HANDLE, closed_spline=True, samples_per_segment=1,
                      radial_segments=8, cap_ends=False),
                material=mats["grip"] if strand == 0 else mats["lid_light"],
                name=f"raised_handle_{label}_braid_{strand}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
            )
    for i in range(12):
        th = 2.0 * math.pi * i / 12
        x0 = a * math.cos(th)
        y0 = b * math.sin(th)
        x1 = a * 0.92 * math.cos(th)
        y1 = b * 0.92 * math.sin(th)
        pts = [(x0, y0 + y_shift, base_z - 0.001), (x1, y1 + y_shift, top_z)]
        lid.visual(
            _tube(pts, radius=0.0024, samples_per_segment=1, radial_segments=6,
                  cap_ends=True, up_hint=(1.0, 0.0, 0.0)),
            material=mats["grip"] if i % 3 == 0 else mats["lid_light"],
            name=f"raised_handle_vertical_weave_{i:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )


def _emit_grip_rect_handle(lid, r: ResolvedContainerBasketConfig, *, mats, y_shift: float) -> None:
    hx = 0.044 * r.grip_size_scale
    hy = 0.027 * r.grip_size_scale
    base_z = 0.006 + LID_DOME + 0.002
    top_z = base_z + 0.021
    for k, z in enumerate((base_z, top_z)):
        pts = []
        for i in range(80):
            s = i / 80
            theta = 2.0 * math.pi * s
            power = 2.0 / 5.2
            c, q = math.cos(theta), math.sin(theta)
            x = hx * _sgn(c) * (abs(c) ** power)
            y = hy * _sgn(q) * (abs(q) ** power)
            pts.append((x, y + y_shift, z))
        lid.visual(
            _tube(pts, radius=T_HANDLE, closed_spline=True, samples_per_segment=1,
                  radial_segments=8, cap_ends=False),
            material=mats["grip"] if k == 0 else mats["lid_light"],
            name=f"raised_rect_handle_rim_{k}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    for j in range(16):
        s = j / 16.0
        theta = 2.0 * math.pi * s
        power = 2.0 / 5.2
        c, q = math.cos(theta), math.sin(theta)
        x = hx * _sgn(c) * (abs(c) ** power)
        y = hy * _sgn(q) * (abs(q) ** power)
        pts = [
            (x, y + y_shift, 0.006 + LID_DOME - 0.001),
            (x, y + y_shift, base_z),
            (x, y + y_shift, top_z),
        ]
        lid.visual(
            _tube(pts, radius=0.0028, samples_per_segment=1, radial_segments=7, cap_ends=True),
            material=mats["grip"] if j % 4 == 0 else mats["lid_light"],
            name=f"handle_vertical_stake_{j:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    for i, off in enumerate((-0.017, -0.008, 0.001, 0.010, 0.019)):
        half = hx * 0.95 * max(0.0, 1.0 - (abs(off) / (hy * 0.95)) ** 5.2) ** (1.0 / 5.2)
        pts = [(_lerp(-half, half, t / 7), off + y_shift, top_z + 0.001) for t in range(8)]
        lid.visual(
            _tube(pts, radius=0.0027, samples_per_segment=1, radial_segments=6, cap_ends=True),
            material=mats["lid_light"] if i % 2 == 0 else mats["grip"],
            name=f"handle_top_weave_x_{i:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    for i, off in enumerate((-0.030, -0.018, -0.006, 0.006, 0.018, 0.030)):
        half = hy * 0.95 * max(0.0, 1.0 - (abs(off) / (hx * 0.95)) ** 5.2) ** (1.0 / 5.2)
        pts = [(off, _lerp(-half, half, t / 7) + y_shift, top_z + 0.002) for t in range(8)]
        lid.visual(
            _tube(pts, radius=0.0027, samples_per_segment=1, radial_segments=6, cap_ends=True),
            material=mats["grip"] if i % 2 == 0 else mats["lid_light"],
            name=f"handle_top_weave_y_{i:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )


def _emit_grip_black_ring(lid, r: ResolvedContainerBasketConfig, *, mats, y_shift: float) -> None:
    half_w = 0.020 * r.grip_size_scale
    half_h = 0.018 * r.grip_size_scale
    center_z = 0.006 + LID_DOME + 0.018
    loop = []
    for i in range(96):
        th = 2.0 * math.pi * i / 96
        x = half_w * math.cos(th)
        z = center_z + half_h * math.sin(th)
        y = 0.003 * math.sin(th) ** 2
        loop.append((x, y + y_shift, z))
    lid.visual(
        _tube(loop, radius=T_HANDLE, closed_spline=True, samples_per_segment=1,
              radial_segments=8, cap_ends=False, up_hint=(0.0, 1.0, 0.0)),
        material=mats["grip"],
        name="black_ring_handle_loop", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "seagrass_natural"} else "metal.paint_coated"),
    )
    for idx, x in enumerate((-half_w * 0.55, half_w * 0.55)):
        pts = [
            (x * 0.70, 0.0 + y_shift, 0.006 + LID_DOME - 0.001),
            (x * 0.86, 0.001 + y_shift, center_z - half_h + 0.003),
        ]
        lid.visual(
            _tube(pts, radius=0.0026, samples_per_segment=1, radial_segments=7,
                  cap_ends=True, up_hint=(0.0, 1.0, 0.0)),
            material=mats["grip"],
            name=f"black_ring_handle_mount_{idx}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "seagrass_natural"} else "metal.paint_coated"),
        )


def _emit_grip_arched_bail(lid, r: ResolvedContainerBasketConfig, *, mats, y_shift: float) -> None:
    spread = min(0.088 * r.grip_size_scale, r.lid_outer_ay * 0.72)
    post_h = 0.095 * r.grip_size_scale
    arch_peak = 0.145 * r.grip_size_scale
    base_z = 0.006 + LID_DOME
    # The lid woven dome surface at the post's y (disc-local) — start each post
    # a hair below it so the post foot sinks into the weave (connected, not
    # floating above the dome).
    weave_b = r.lid_outer_ay
    rho2 = min(1.0, (spread / max(weave_b, 1e-6)) ** 2)
    foot_z = 0.006 + LID_DOME * (1.0 - rho2) - 0.001
    for i, y_sign in enumerate((-1.0, 1.0)):
        pts = []
        for k in range(30):
            t = k / 29
            z = foot_z + (base_z + post_h - foot_z) * t
            twist = 0.0012 * math.sin(6.0 * math.pi * t)
            pts.append((twist, spread * y_sign + y_shift + twist * 0.4, z))
        lid.visual(
            _tube(pts, radius=0.005, samples_per_segment=2, radial_segments=7,
                  cap_ends=True, up_hint=(1.0, 0.0, 0.0)),
            material=mats["mid"] if i == 0 else mats["grip"],
            name=f"bail_post_{i}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    spring_z = base_z + post_h
    peak_z = base_z + arch_peak
    main = []
    for k in range(64):
        t = k / 63
        u = -1.0 + 2.0 * t
        y = spread * u
        z = spring_z + (peak_z - spring_z) * (1.0 - u * u)
        wave = 0.0008 * math.sin(12.0 * math.pi * t)
        main.append((wave, y + y_shift, z + wave * 0.3))
    lid.visual(
        _tube(main, radius=0.005, samples_per_segment=2, radial_segments=8,
              cap_ends=True, up_hint=(0.0, 1.0, 0.0)),
        material=mats["lid_light"],
        name="bail_arch_main", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
    )
    for i, offset in enumerate((0.0, math.pi)):
        wrap = []
        for k in range(64):
            t = k / 63
            u = -1.0 + 2.0 * t
            y = spread * u
            z = spring_z + (peak_z - spring_z) * (1.0 - u * u)
            angle = 8.0 * math.pi * t + offset
            wrap.append((0.002 * math.cos(angle), y + y_shift, z + 0.002 * math.sin(angle)))
        lid.visual(
            _tube(wrap, radius=0.0025, samples_per_segment=2, radial_segments=6,
                  cap_ends=True, up_hint=(0.0, 1.0, 0.0)),
            material=mats["mid"] if i == 0 else mats["grip"],
            name=f"bail_arch_wrap_{i}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )


_GRIP_EMITTERS = {
    "raised_oval_knob": _emit_grip_oval_knob,
    "raised_rect_handle": _emit_grip_rect_handle,
    "black_ring_handle": _emit_grip_black_ring,
    "arched_carry_bail": _emit_grip_arched_bail,
}


# ---------------------------------------------------------------------------
# Twist turn-knob latch (separate `turn_knob` part + REVOLUTE +Z joint).
# ---------------------------------------------------------------------------
def _emit_twist_knob(
    model, body, lid, r: ResolvedContainerBasketConfig, *, mats, y_shift: float
) -> None:
    knob_r = 0.032 * r.grip_size_scale
    knob_h = 0.014 * r.grip_size_scale
    base_z = 0.006 + LID_DOME + 0.002  # KNOB_BASE_Z in lid frame
    lug_len = 0.038 * r.grip_size_scale
    n_lugs = 4

    knob = model.part("turn_knob")
    # Knob base plate at z=0 of the knob frame (so the joint origin sits on real
    # geometry) — a flat woven oval disc.
    plate = []
    for i in range(48):
        s = i / 48
        x, y = _profile_point(r, s, knob_r + 0.005, knob_r + 0.005)
        plate.append((x, y, 0.0))
    knob.visual(
        _tube(plate, radius=0.0035, closed_spline=True, samples_per_segment=1,
              radial_segments=8, cap_ends=False),
        material=mats["grip"],
        name="knob_base_plate_ring", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
    )
    # Central hub at the knob's local origin (0,0,0): the REVOLUTE +Z child point
    # is the part origin, so two short cane spokes crossing the center plant real
    # geometry right there (origin-distance check) and tie the plate into the hub.
    pr = knob_r + 0.005
    for label, ang in (("x", 0.0), ("y", math.pi / 2.0)):
        c, q = math.cos(ang), math.sin(ang)
        knob.visual(
            _tube(
                [(-pr * c, -pr * q, 0.0), (0.0, 0.0, 0.0), (pr * c, pr * q, 0.0)],
                radius=0.0030, samples_per_segment=2, radial_segments=6,
                cap_ends=True, up_hint=(c, q, 0.0),
            ),
            material=mats["grip"] if label == "x" else mats["lid_light"],
            name=f"knob_hub_spoke_{label}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    for k, (label, zz, rr) in enumerate(
        (("base", 0.001, knob_r), ("top", knob_h, knob_r * 0.88))
    ):
        for strand, phase in enumerate((0.0, math.pi)):
            pts = _braid_ring_path(r, zz, rr, rr, phase=phase, turns=12, amp=0.0020)
            knob.visual(
                _tube(pts, radius=0.0032, closed_spline=True, samples_per_segment=1,
                      radial_segments=8, cap_ends=False),
                material=mats["grip"] if strand == 0 else mats["lid_light"],
                name=f"knob_{label}_braid_{strand}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
            )
    for i in range(12):
        th = 2.0 * math.pi * i / 12
        x = knob_r * math.cos(th)
        y = knob_r * math.sin(th)
        knob.visual(
            _tube([(x, y, 0.001), (x * 0.96, y * 0.96, knob_h)], radius=0.0022,
                  samples_per_segment=1, radial_segments=6, cap_ends=True,
                  up_hint=(1.0, 0.0, 0.0)),
            material=mats["grip"] if i % 3 == 0 else mats["lid_light"],
            name=f"knob_vertical_weave_{i:02d}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    lug_z = knob_h * 0.4
    for i in range(n_lugs):
        angle = 2.0 * math.pi * i / n_lugs
        arm = []
        for k in range(12):
            t = k / 11
            rad = knob_r * 0.5 + (lug_len - knob_r * 0.5) * t
            drop = 0.010 * max(0.0, (t - 0.6) / 0.4) if t > 0.6 else 0.0
            arm.append((rad * math.cos(angle), rad * math.sin(angle), lug_z - drop))
        end = arm[-1]
        knob.visual(
            _tube(arm, radius=0.003, samples_per_segment=2, radial_segments=6, cap_ends=True,
                  up_hint=(math.cos(angle), math.sin(angle), 0.0)),
            material=mats["accent"],
            name=f"lug_arm_{i}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
        perp = angle + math.pi / 2
        mid_r = lug_len * 0.85
        cx, cy, cz = mid_r * math.cos(angle), mid_r * math.sin(angle), end[2] + 0.002
        hw = 0.006
        knob.visual(
            _tube(
                [
                    (cx - hw * math.cos(perp), cy - hw * math.sin(perp), cz),
                    (cx + hw * math.cos(perp), cy + hw * math.sin(perp), cz),
                ],
                radius=0.0027, samples_per_segment=1, radial_segments=6, cap_ends=True,
            ),
            material=mats["grip"],
            name=f"lug_crossbar_{i}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
        tip = []
        for k in range(8):
            t = k / 7
            rad = lug_len - 0.006 * t
            tip.append((rad * math.cos(angle), rad * math.sin(angle), end[2] - 0.003 * t))
        knob.visual(
            _tube(tip, radius=0.0024, samples_per_segment=2, radial_segments=6, cap_ends=True),
            material=mats["accent"],
            name=f"lug_tip_{i}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    knob.inertial = Inertial.from_geometry(
        Cylinder(radius=lug_len, length=knob_h),
        mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, knob_h * 0.5)),
    )

    # Body-side rim lug slots that receive the lugs (fixed body visuals).
    hx, hy = _half_extents_at_z(r, r.h_body)
    for i in range(n_lugs):
        angle = 2.0 * math.pi * i / n_lugs + math.pi / n_lugs
        s = angle / (2.0 * math.pi)
        px, py = _profile_point(r, s, hx + 0.005, hy + 0.005)
        pnx, pny = _outward_xy(px, py, hx, hy)
        perp_x, perp_y = -pny, pnx
        slot = []
        for k in range(8):
            off = -0.0072 + 0.0144 * k / 7
            slot.append((px + off * perp_x, py + off * perp_y, r.h_body - 0.003))
        body.visual(
            _tube(slot, radius=0.003, samples_per_segment=1, radial_segments=6, cap_ends=True),
            material=mats["shadow"],
            name=f"rim_lug_slot_{i}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )

    model.articulation(
        "lid_to_knob",
        ArticulationType.REVOLUTE,
        parent=lid,
        child=knob,
        origin=Origin(xyz=(0.0, y_shift, base_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=5.0, velocity=2.0, lower=0.0, upper=KNOB_TURN * r.joint_travel_scale
        ),
    )


# ---------------------------------------------------------------------------
# Lid closures.
# ---------------------------------------------------------------------------
def _body_inertial(body, r: ResolvedContainerBasketConfig) -> None:
    body.inertial = Inertial.from_geometry(
        Box((2 * r.ax, 2 * r.ay, r.h_body)),
        mass=0.5,
        origin=Origin(xyz=(0.0, 0.0, r.h_body / 2.0)),
    )


def _lid_inertial(lid, r: ResolvedContainerBasketConfig, *, y_shift: float = 0.0) -> None:
    lid.inertial = Inertial.from_geometry(
        Cylinder(radius=max(r.lid_outer_ax, r.lid_outer_ay), length=0.02),
        mass=0.05,
        origin=Origin(xyz=(0.0, y_shift, 0.012)),
    )


def _build_grip(model, body, lid, r, *, mats, y_shift: float) -> None:
    if r.lid_grip == "bare":
        return
    if r.lid_grip == "twist_turn_knob_latch":
        _emit_twist_knob(model, body, lid, r, mats=mats, y_shift=y_shift)
        return
    _GRIP_EMITTERS[r.lid_grip](lid, r, mats=mats, y_shift=y_shift)


def _build_liftoff_lid(model, body, r, *, mats) -> None:
    lid = model.part("basket_lid")
    _emit_lid_face(lid, r, mats=mats, y_shift=0.0)
    _lid_inertial(lid, r)
    _build_grip(model, body, lid, r, mats=mats, y_shift=0.0)
    model.articulation(
        "body_to_lid",
        ArticulationType.PRISMATIC,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, 0.0, r.lid_seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=18.0, velocity=0.4, lower=0.0, upper=LID_LIFT * r.joint_travel_scale
        ),
    )


def _build_flip_lid(model, body, r, *, mats) -> None:
    # Hinge at the back rim (0, -mouth_ay, h). Lid geometry is offset +mouth_ay
    # in Y so the woven disc caps the mouth at q=0; knuckles stay at the frame
    # origin on the hinge line.
    y_shift = r.mouth_ay
    lid = model.part("basket_lid")
    _emit_lid_face(lid, r, mats=mats, y_shift=y_shift)
    # Lid hinge knuckles on the hinge axis (y=0). Each anchors on the continuous
    # braided lid rim at the disc's back edge (lid frame y = y_shift - lb, which
    # is guaranteed to exist as a closed ring) and runs in to the hinge line at
    # y=0, so the knuckle is firmly connected to the lid mesh rather than
    # floating. The end segment at y=0 sits on the REVOLUTE axis. The anchor sweeps
    # +/- a little in y to straddle the braid ring even if the back point shifts.
    rim_back_y = y_shift - r.lid_outer_ay  # back braid ring point, lid frame
    for i, xoff in enumerate((-0.025, 0.025)):
        lid.visual(
            _tube(
                [
                    (xoff, rim_back_y - 0.004, 0.005),
                    (xoff, rim_back_y + 0.006, 0.004),
                    (xoff, 0.5 * (rim_back_y + 0.006), 0.003),
                    (xoff, 0.0, 0.002),
                ],
                radius=0.0046, samples_per_segment=2, radial_segments=8,
                cap_ends=True, up_hint=(1.0, 0.0, 0.0),
            ),
            material=mats["accent"],
            name=f"lid_hinge_knuckle_{i}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    _lid_inertial(lid, r, y_shift=y_shift)
    _build_grip(model, body, lid, r, mats=mats, y_shift=y_shift)
    # Body-side hinge barrels at the back rim, interleaved with the knuckles.
    for i, xoff in enumerate((-0.038, 0.0, 0.038)):
        body.visual(
            _tube(
                [
                    (xoff - 0.010, -r.mouth_ay + 0.002, r.h_body + 0.002),
                    (xoff + 0.010, -r.mouth_ay + 0.002, r.h_body + 0.002),
                ],
                radius=0.0048, radial_segments=8, cap_ends=True, up_hint=(0.0, 0.0, 1.0),
            ),
            material=mats["accent"],
            name=f"hinge_barrel_{i}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    model.articulation(
        "body_to_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, -r.mouth_ay, r.h_body)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=10.0, velocity=1.5, lower=0.0, upper=HINGE_UPPER * r.joint_travel_scale
        ),
    )


def _build_bail_swing(model, body, r, *, mats) -> None:
    # Fixed-fit lift-off lid (PRISMATIC) + a swinging carry_bail on REVOLUTE +Y.
    lid = model.part("basket_lid")
    _emit_lid_face(lid, r, mats=mats, y_shift=0.0)
    _lid_inertial(lid, r)
    _build_grip(model, body, lid, r, mats=mats, y_shift=0.0)
    model.articulation(
        "body_to_lid",
        ArticulationType.PRISMATIC,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, 0.0, r.lid_seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=18.0, velocity=0.35, lower=0.0, upper=LID_LIFT * r.joint_travel_scale
        ),
    )

    # Anchor lugs on the body rim (fixed body visuals) where the bail pivots.
    lug_y = r.mouth_ay + 0.012
    for i, y_sign in enumerate((1, -1)):
        y_center = y_sign * lug_y
        loop = []
        for k in range(24):
            ang = 2.0 * math.pi * k / 24
            loop.append(
                (0.009 * math.cos(ang), y_center + 0.0027 * math.sin(ang), 0.009 * math.sin(ang))
            )
        body.visual(
            _tube(loop, radius=0.0050, closed_spline=True, samples_per_segment=1,
                  radial_segments=8, cap_ends=False),
            origin=Origin(xyz=(0.0, 0.0, r.h_body)),
            material=mats["shadow"],
            name=f"bail_anchor_lug_{i}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )

    # The carry_bail: a woven arch in its own frame. At q=0 it hangs DOWN
    # alongside the body (z negative); the pivot axis is +Y through the lugs.
    bail = model.part("carry_bail")
    half_span = lug_y
    arch_drop = 0.155
    for i in range(3):
        x_off = (i - 1) * 0.005
        pts = []
        for k in range(48):
            t = k / 47
            angle = math.pi * t
            y = half_span * math.cos(angle)
            z = -arch_drop * (1.0 + 0.04 * (i - 1)) * math.sin(angle)
            pts.append((x_off, y, z))
        bail.visual(
            _tube(pts, radius=0.0040, samples_per_segment=2, radial_segments=8, cap_ends=True),
            material=mats["grip"] if i != 1 else mats["mid"],
            name=f"bail_arch_strand_{i}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    for i, phase in enumerate((0.0, math.pi)):
        pts = []
        for k in range(160):
            t = k / 159
            angle = math.pi * t
            y = half_span * math.cos(angle)
            z_base = -arch_drop * math.sin(angle)
            twist = 16 * 2.0 * math.pi * t + phase
            pts.append((0.0055 * math.cos(twist), y, z_base + 0.0055 * math.sin(twist)))
        bail.visual(
            _tube(pts, radius=0.0032, samples_per_segment=1, radial_segments=7, cap_ends=True),
            material=mats["accent"] if i == 0 else mats["light"],
            name=f"bail_braided_wrap_{i}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    # Pivot spine: a cane pin running along the +Y pivot axis through the bail's
    # own local origin (0,0,0), joining the two lug ends. The child joint point
    # is the part's local origin, so this plants real bail geometry there (child
    # distance check) and ties the two pivot wraps + arch into one connected mesh.
    spine = [
        (0.0, -half_span, 0.0),
        (0.0, 0.0, 0.0),
        (0.0, half_span, 0.0),
    ]
    bail.visual(
        _tube(spine, radius=0.0040, samples_per_segment=2, radial_segments=7,
              cap_ends=True, up_hint=(0.0, 1.0, 0.0)),
        material=mats["shadow"],
        name="bail_pivot_spine", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
    )
    # Pivot wraps at the lug ends — real child geometry at the joint axis (y=±span,
    # x=0, z=0), so the joint origin (0,0,h) sits on bail geometry too.
    for i, y_sign in enumerate((1, -1)):
        ring = []
        for k in range(20):
            ang = 2.0 * math.pi * k / 20
            ring.append((0.007 * math.cos(ang), y_sign * half_span, 0.007 * math.sin(ang)))
        bail.visual(
            _tube(ring, radius=0.0045, closed_spline=True, samples_per_segment=1,
                  radial_segments=6, cap_ends=False),
            material=mats["shadow"],
            name=f"bail_pivot_wrap_{i}", material_class_id=("wood.woven_plant_fiber" if r.palette_style in {"natural_tan", "honey_rattan", "dark_walnut_reed", "teal_red_accent", "two_tone_wheat_umber", "black_handle_natural", "lacquered_chestnut", "sage_powdercoat_wire", "charcoal_painted"} else "organic.woven_plant_fiber"),
        )
    bail.inertial = Inertial.from_geometry(
        Cylinder(radius=0.006, length=2 * half_span),
        mass=0.04,
        origin=Origin(xyz=(0.0, 0.0, -arch_drop * 0.5), rpy=(math.pi / 2, 0.0, 0.0)),
    )
    model.articulation(
        "body_to_bail",
        ArticulationType.REVOLUTE,
        parent=body,
        child=bail,
        origin=Origin(xyz=(0.0, 0.0, r.h_body)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0, velocity=2.0, lower=0.0, upper=BAIL_UPPER * r.joint_travel_scale
        ),
    )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_basket(
    config: ContainerBasketConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    global _TUBE_COUNTER
    _TUBE_COUNTER = 0
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    p = r.palette_style
    f = r.finish
    mats = {
        "light": model.material(f"cb_{f}_{p}_light", rgba=pal.light),
        "mid": model.material(f"cb_{f}_{p}_mid", rgba=pal.mid),
        "shadow": model.material(f"cb_{f}_{p}_shadow", rgba=pal.shadow),
        "lid_light": model.material(f"cb_{f}_{p}_lid_light", rgba=pal.lid_light),
        "lid_shadow": model.material(f"cb_{f}_{p}_lid_shadow", rgba=pal.lid_shadow),
        "grip": model.material(f"cb_{f}_{p}_grip", rgba=pal.grip),
        "accent": model.material(f"cb_{f}_{p}_accent", rgba=pal.accent),
    }

    # --- ROOT: basket body ---------------------------------------------------
    body = model.part("basket_body")
    _emit_floor(body, r, mats=mats)
    # Vertical stakes are always emitted: they span foot ring -> mouth rim and
    # are the structural bridge that keeps the floor, wall and rim in one
    # connected body mesh (the patterned wall's stitches alone are too short to
    # bridge, which would leave the floor/rim as a separate island).
    _emit_stakes(body, r, mats=mats, count=STAKE_COUNT)
    _WALL_EMITTERS[r.wall_weave](body, r, mats=mats)
    _emit_mouth_rim(body, r, mats=mats)
    _emit_side_handles(body, r, mats=mats, count=r.side_handle_count)
    _body_inertial(body, r)

    # --- lid mechanism -------------------------------------------------------
    if r.lid_closure == "prismatic_liftoff":
        _build_liftoff_lid(model, body, r, mats=mats)
    elif r.lid_closure == "hinged_flip_lid":
        _build_flip_lid(model, body, r, mats=mats)
    elif r.lid_closure == "bail_swing_handle":
        _build_bail_swing(model, body, r, mats=mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["palette_style"] = r.palette_style
    model.meta["finish"] = r.finish
    return model


def build_seeded_container_basket(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_basket(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (lid weave rim over the mouth rim, bail
# folded against the body, knob lugs through the lid, side handles on the wall)
# are declared so the sweep's island/overlap checks pass; the lid / bail / knob
# actions are exercised.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_basket_tests(
    object_model: ArticulatedObject,
    config: ContainerBasketConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("basket_body")

    # ---- basket body rests on the ground (base near z=0) ----
    aabb = ctx.part_world_aabb(body)
    bext = _ext(aabb)
    ctx.check(
        "basket body rests on the ground (base near z=0)",
        abs(aabb[0][2]) < 0.020,
        details=f"body min z={aabb[0][2]:.4f}",
    )
    ctx.check(
        "basket body has real volume",
        bext[0] > 0.05 and bext[1] > 0.05 and bext[2] > 0.10,
        details=f"body extents={bext}",
    )

    # ---- woven body: stakes (unless patterned) + selected wall-weave layer ----
    stake_count = sum(
        1 for v in body.visuals if (v.name or "").startswith("vertical_weave_stake")
    )
    if r.wall_weave == "patterned_wall_weave":
        wall = sum(
            1 for v in body.visuals if (v.name or "").startswith("woven_wall_")
        )
        ctx.check("patterned wall weave present", wall >= 100, details=f"wall={wall}")
    elif r.wall_weave == "diagonal_twill_weave":
        twill = sum(1 for v in body.visuals if (v.name or "").startswith("twill_strand_"))
        ctx.check(
            "diagonal twill strands + stakes present",
            twill >= 40 and stake_count >= STAKE_COUNT,
            details=f"twill={twill}, stakes={stake_count}",
        )
    elif r.wall_weave == "dense_checker_weave":
        rows = sum(1 for v in body.visuals if (v.name or "").startswith("checker_horizontal_band"))
        ctx.check(
            "checker bands + stakes present",
            rows >= 24 and stake_count >= STAKE_COUNT,
            details=f"checker_rows={rows}, stakes={stake_count}",
        )
    elif r.wall_weave == "banded_wave_weave":
        prim = sum(1 for v in body.visuals if (v.name or "").startswith("primary_horizontal_wave_band"))
        ctx.check(
            "banded wave bands + stakes present",
            prim >= 16 and stake_count >= STAKE_COUNT,
            details=f"primary={prim}, stakes={stake_count}",
        )
    else:
        rows = sum(1 for v in body.visuals if (v.name or "").startswith("horizontal_weave_band"))
        ctx.check(
            "dense over-under bands + stakes present",
            rows >= HORIZONTAL_ROWS and stake_count >= STAKE_COUNT,
            details=f"rows={rows}, stakes={stake_count}",
        )

    rim = sum(1 for v in body.visuals if (v.name or "").startswith("body_braided_mouth_rim"))
    ctx.check("braided mouth rim present", rim >= 2, details=f"rim={rim}")

    # ---- lid woven face + braided rim ----
    lid = object_model.get_part("basket_lid")
    # The fitted lid (and its twist knob) lifts clear of the basket mouth in
    # every closure variant, losing body contact.
    for pname in ("basket_lid", "turn_knob"):
        if any(p.name == pname for p in object_model.parts):
            ctx.allow_isolated_part(
                object_model.get_part(pname),
                reason="lid lifts off the basket mouth and loses body contact",
            )
    lid_x = sum(1 for v in lid.visuals if (v.name or "").startswith("lid_weave_x"))
    lid_y = sum(1 for v in lid.visuals if (v.name or "").startswith("lid_weave_y"))
    lid_braid = sum(1 for v in lid.visuals if (v.name or "").startswith("braided_lid_outer_rim"))
    ctx.check(
        "woven lid face + braided rim",
        lid_x >= 10 and lid_y >= 10 and lid_braid >= 2,
        details=f"lid_x={lid_x}, lid_y={lid_y}, braid={lid_braid}",
    )

    # ---- closure action + captured-fit overlaps ----
    if r.lid_closure == "prismatic_liftoff":
        joint = object_model.get_articulation("body_to_lid")
        ctx.allow_isolated_part(
            lid,
            reason="lid lifts off the basket mouth and loses body contact",
        )
        ctx.allow_overlap(
            lid, body, reason="The lid braided rim rests over the basket mouth rim (lift-off fit).",
        )
        ctx.check(
            "body_to_lid PRISMATIC +Z",
            joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(joint.axis) == (0.0, 0.0, 1.0),
            details=f"type={joint.articulation_type}, axis={joint.axis}",
        )
        rest_z = ctx.part_world_position(lid)[2]
        with ctx.pose({joint: LID_LIFT * r.joint_travel_scale}):
            up_z = ctx.part_world_position(lid)[2]
        ctx.check(
            "lid lifts straight up off the basket",
            up_z > rest_z + LID_LIFT * r.joint_travel_scale * 0.5,
            details=f"rest_z={rest_z:.4f}, up_z={up_z:.4f}",
        )

    elif r.lid_closure == "hinged_flip_lid":
        joint = object_model.get_articulation("body_to_lid")
        ctx.allow_overlap(
            lid, body, reason="The flip lid woven disc rests on the mouth rim when closed.",
        )
        barrels = sum(1 for v in body.visuals if (v.name or "").startswith("hinge_barrel"))
        knuckles = sum(1 for v in lid.visuals if (v.name or "").startswith("lid_hinge_knuckle"))
        ctx.check(
            "hinge barrels + knuckles present",
            barrels >= 3 and knuckles >= 2,
            details=f"barrels={barrels}, knuckles={knuckles}",
        )
        ctx.check(
            "body_to_lid REVOLUTE +X at back rim",
            joint.articulation_type == ArticulationType.REVOLUTE
            and abs(joint.axis[0]) > 0.9
            and joint.origin is not None
            and joint.origin.xyz[1] < -r.mouth_ay + 0.02
            and abs(joint.origin.xyz[2] - r.h_body) < 0.02,
            details=f"axis={joint.axis}, origin={joint.origin.xyz if joint.origin else None}",
        )
        top0 = ctx.part_world_aabb(lid)[1][2]
        with ctx.pose({joint: 1.4 * r.joint_travel_scale}):
            top1 = ctx.part_world_aabb(lid)[1][2]
        ctx.check(
            "flip lid swings up (top rises)",
            top1 > top0 + 0.005,
            details=f"closed_top_z={top0:.4f}, open_top_z={top1:.4f}",
        )

    elif r.lid_closure == "bail_swing_handle":
        lid_joint = object_model.get_articulation("body_to_lid")
        bail_joint = object_model.get_articulation("body_to_bail")
        bail = object_model.get_part("carry_bail")
        ctx.allow_overlap(
            lid, body, reason="The fitted lid braided rim rests over the basket mouth rim.",
        )
        ctx.allow_overlap(
            bail, body, reason="The carry bail arch rests against the body exterior when folded down.",
        )
        ctx.allow_overlap(
            bail, lid, reason="The bail pivot wraps sit at the mouth rim adjacent to the lid rim.",
        )
        ctx.check(
            "body_to_lid PRISMATIC +Z (fitted cover)",
            lid_joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(lid_joint.axis) == (0.0, 0.0, 1.0),
            details=f"type={lid_joint.articulation_type}, axis={lid_joint.axis}",
        )
        ctx.check(
            "body_to_bail REVOLUTE +Y at mouth rim",
            bail_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(bail_joint.axis[1]) > 0.9
            and bail_joint.origin is not None
            and abs(bail_joint.origin.xyz[2] - r.h_body) < 0.005,
            details=f"axis={bail_joint.axis}, origin={bail_joint.origin.xyz if bail_joint.origin else None}",
        )
        lug_count = sum(1 for v in body.visuals if (v.name or "").startswith("bail_anchor_lug"))
        ctx.check("anchor lugs on rim", lug_count >= 2, details=f"lugs={lug_count}")
        # q=0 the bail hangs down alongside the body.
        rest_aabb = ctx.part_world_aabb(bail)
        ctx.check(
            "bail folds down at rest",
            rest_aabb[0][2] < r.h_body - 0.06,
            details=f"bail_rest_min_z={rest_aabb[0][2]:.4f}",
        )
        with ctx.pose({bail_joint: BAIL_UPPER * r.joint_travel_scale}):
            up_aabb = ctx.part_world_aabb(bail)
        ctx.check(
            "bail swings up for carrying",
            up_aabb[1][2] > r.h_body + 0.03,
            details=f"bail_up_max_z={up_aabb[1][2]:.4f}",
        )

    # ---- lid grip: fixed visuals or active twist knob ----
    if r.lid_grip == "twist_turn_knob_latch":
        knob = object_model.get_part("turn_knob")
        knob_joint = object_model.get_articulation("lid_to_knob")
        ctx.allow_overlap(
            knob, lid, reason="The twist knob lug arms pass through the lid plane.",
        )
        ctx.allow_overlap(
            knob, body, reason="The twist knob lugs engage the body rim slots.",
        )
        lug_arms = sum(1 for v in knob.visuals if (v.name or "").startswith("lug_arm"))
        slots = sum(1 for v in body.visuals if (v.name or "").startswith("rim_lug_slot"))
        ctx.check(
            "turn_knob lugs + body rim slots present",
            lug_arms >= 4 and slots >= 4,
            details=f"lug_arms={lug_arms}, slots={slots}",
        )
        ctx.check(
            "lid_to_knob REVOLUTE +Z quarter-turn",
            knob_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(knob_joint.axis[2]) > 0.99
            and knob_joint.motion_limits is not None
            and knob_joint.motion_limits.upper is not None,
            details=f"type={knob_joint.articulation_type}, axis={knob_joint.axis}",
        )
        # Knob rotation is about the vertical axis (z position unchanged).
        z0 = ctx.part_world_position(knob)[2]
        with ctx.pose({knob_joint: KNOB_TURN * r.joint_travel_scale}):
            z1 = ctx.part_world_position(knob)[2]
        ctx.check(
            "twist knob rotates about +Z (z unchanged)",
            abs(z1 - z0) < 0.005,
            details=f"z0={z0:.4f}, z1={z1:.4f}",
        )
    elif r.lid_grip == "raised_oval_knob":
        grip = sum(1 for v in lid.visuals if (v.name or "").startswith("raised_handle"))
        ctx.check("raised oval knob present", grip >= 16, details=f"grip={grip}")
    elif r.lid_grip == "raised_rect_handle":
        rims = sum(1 for v in lid.visuals if (v.name or "").startswith("raised_rect_handle_rim"))
        stakes = sum(1 for v in lid.visuals if (v.name or "").startswith("handle_vertical_stake"))
        ctx.check(
            "raised rect handle present",
            rims >= 2 and stakes >= 16,
            details=f"rims={rims}, stakes={stakes}",
        )
    elif r.lid_grip == "black_ring_handle":
        ring = sum(1 for v in lid.visuals if (v.name or "").startswith("black_ring_handle"))
        ctx.check("black ring handle present", ring >= 3, details=f"ring={ring}")
    elif r.lid_grip == "arched_carry_bail":
        posts = sum(1 for v in lid.visuals if (v.name or "").startswith("bail_post"))
        arches = sum(1 for v in lid.visuals if (v.name or "").startswith("bail_arch"))
        ctx.check(
            "arched carry bail grip present",
            posts >= 2 and arches >= 3,
            details=f"posts={posts}, arches={arches}",
        )

    # ---- side handle pair (multiplicity) ----
    if r.side_handle_count == 2:
        loops = sum(1 for v in body.visuals if (v.name or "").startswith("side_handle_loop"))
        ctx.check(
            "side handle pair present",
            loops == 2,
            details=f"loops={loops}",
        )
        # Handles must not block the lid: top below the lid seat line.
        for i in range(2):
            v = body.get_visual(f"side_handle_loop_{i}")
            if v is not None:
                hb = ctx.part_element_world_aabb(body, elem=f"side_handle_loop_{i}")
                ctx.check(
                    f"side handle {i} below lid seat",
                    hb[1][2] < r.lid_seat_z - 0.005,
                    details=f"handle_top_z={hb[1][2]:.4f}, seat={r.lid_seat_z:.4f}",
                )

    # ---- at least one non-fixed joint exists ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()
