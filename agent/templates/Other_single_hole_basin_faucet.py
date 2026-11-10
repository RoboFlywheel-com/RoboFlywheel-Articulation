# SPDX-License-Identifier: Apache-2.0

"""single_hole_basin_faucet — monobloc single-hole basin mixer (modular template).

A single-hole basin mixer: one root ``body`` (deck base + upright column + a
single forward-reaching spout, all fixed visuals on the root part), plus a
single operating mechanism (lever / knob / push-cap) that controls flow + hot
/ cold mix. The spout points +X; the deck rests on z=0.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Other_Other_single_hole_basin_faucet.md``.

Structure (pattern = ``mixed``): a fixed root ``body`` with deck/column/spout
visuals, and an articulation chain for the handle. Three STRUCTURAL slots
(36 topologies) + four COSMETIC sub-axes (``parent.visual`` only — no new
parts/joints, NOT counted in module_topology_diversity):

  * Slot A ``handle_mechanism`` (4) — the joint-topology axis:
      - lever_top_swivel_lift : 2 REVOLUTE (swivel Z + lift -Y) on a top post
      - lever_side_disc_twist : 2 REVOLUTE (lift -Y + twist +X) on a side boss
      - knob_quarter_turn     : 1 REVOLUTE Z on the top post
      - push_cap_press_turn   : 1 PRISMATIC -z + 1 REVOLUTE Z on the neck
  * Slot B ``spout_form`` (3) — root-body inline visual mesh family:
      - tubular_downturned : swept round tube arcing down to the outlet
      - open_channel       : open U-trough swept forward (mild droop)
      - flat_blade         : flat cantilever blade + aerator collar + outlet
  * Slot C ``deck_base`` (3) — root-body base primitive/mesh family:
      - round_flange / square_step_plate / raised_pedestal

  * COSMETIC ``body_section`` (round/square) — column primitive (Cyl vs filleted Box)
  * COSMETIC ``knob_grip`` (knurled/fluted/ribbed) — KnobGrip texture, knob only
  * COSMETIC ``spout_tip_collar`` (collared/plain) — aerator ring at outlet
  * COSMETIC ``base_escutcheon`` (ring/none) — decorative ring on the deck top

Every non-FIXED joint carries a ``MatingContract`` to real visual faces.
Captured stems/pins use element-scoped ``allow_overlap`` (mirroring the master
records). No multiplicity / copy axis (single mechanism, single spout).
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
    KnobGeometry,
    KnobGrip,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Enum domains
# --------------------------------------------------------------------------- #
HandleMechanism = Literal[
    "lever_top_swivel_lift",
    "lever_side_disc_twist",
    "knob_quarter_turn",
    "push_cap_press_turn",
]
SpoutForm = Literal["tubular_downturned", "open_channel", "flat_blade"]
DeckBase = Literal["round_flange", "square_step_plate", "raised_pedestal"]
PaletteStyle = Literal["polished_chrome", "brushed_stainless", "matte_black", "brushed_gold"]
BodySection = Literal["round", "square"]
KnobGripStyle = Literal["knurled", "fluted", "ribbed", "na"]
SpoutTipCollar = Literal["collared", "plain"]
BaseEscutcheon = Literal["ring", "none"]

HANDLE_MECHANISMS: tuple[HandleMechanism, ...] = (
    "lever_top_swivel_lift",
    "lever_side_disc_twist",
    "knob_quarter_turn",
    "push_cap_press_turn",
)
# lever ~52% (split top/side), knob ~29%, push_cap ~19% (spec §样本覆盖分析).
HANDLE_WEIGHTS = (0.28, 0.24, 0.29, 0.19)

SPOUT_FORMS: tuple[SpoutForm, ...] = ("tubular_downturned", "open_channel", "flat_blade")
SPOUT_WEIGHTS = (0.35, 0.36, 0.29)

DECK_BASES: tuple[DeckBase, ...] = ("round_flange", "square_step_plate", "raised_pedestal")
DECK_WEIGHTS = (0.50, 0.30, 0.20)

PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "polished_chrome",
    "brushed_stainless",
    "matte_black",
    "brushed_gold",
)

BODY_SECTIONS: tuple[BodySection, ...] = ("round", "square")
BODY_SECTION_WEIGHTS = (0.60, 0.40)

KNOB_GRIPS: tuple[KnobGripStyle, ...] = ("knurled", "fluted", "ribbed")
KNOB_GRIP_WEIGHTS = (0.35, 0.45, 0.20)

SPOUT_TIP_COLLARS: tuple[SpoutTipCollar, ...] = ("collared", "plain")
SPOUT_TIP_COLLAR_WEIGHTS = (0.60, 0.40)

BASE_ESCUTCHEONS: tuple[BaseEscutcheon, ...] = ("ring", "none")
BASE_ESCUTCHEON_WEIGHTS = (0.45, 0.55)

# --------------------------------------------------------------------------- #
# Palettes (token -> rgba). Each .visual(..., material=mats[...]) is driven by
# palette_style so swept seeds are colourfully diverse.
# --------------------------------------------------------------------------- #
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "polished_chrome": {
        "body": (0.82, 0.84, 0.87, 1.0),
        "accent": (0.10, 0.10, 0.12, 1.0),
        "gasket": (0.05, 0.05, 0.05, 1.0),
        "hot": (0.80, 0.13, 0.13, 1.0),
        "cold": (0.13, 0.32, 0.80, 1.0),
    },
    "brushed_stainless": {
        "body": (0.64, 0.66, 0.67, 1.0),
        "accent": (0.14, 0.14, 0.15, 1.0),
        "gasket": (0.06, 0.06, 0.06, 1.0),
        "hot": (0.74, 0.16, 0.16, 1.0),
        "cold": (0.16, 0.30, 0.72, 1.0),
    },
    "matte_black": {
        "body": (0.08, 0.08, 0.09, 1.0),
        "accent": (0.42, 0.43, 0.45, 1.0),
        "gasket": (0.03, 0.03, 0.03, 1.0),
        "hot": (0.72, 0.18, 0.18, 1.0),
        "cold": (0.22, 0.38, 0.78, 1.0),
    },
    "brushed_gold": {
        "body": (0.80, 0.65, 0.32, 1.0),
        "accent": (0.20, 0.16, 0.08, 1.0),
        "gasket": (0.05, 0.05, 0.05, 1.0),
        "hot": (0.78, 0.16, 0.16, 1.0),
        "cold": (0.16, 0.32, 0.74, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Base real-world dimensions (meters). Spout points +X; deck on z=0.
# --------------------------------------------------------------------------- #
DECK_R_BASE = 0.050           # round-flange radius / half square side
DECK_H_FLANGE = 0.013
DECK_H_SQUARE = 0.018
DECK_H_PEDESTAL = 0.030
COL_R_BASE = 0.022            # column bottom radius
EMB = 0.003                   # embed depths
POST_R = 0.014
POST_H = 0.013
NECK_R = 0.016
NECK_H = 0.020
SPOUT_R_BASE = 0.011
SPOUT_REACH_BASE = 0.120
SPOUT_DROOP_BASE = 0.035
SPOUT_ROOT_FRAC = 0.72        # spout root height as fraction of column height

MIN_SPOUT_CLEAR = 0.020       # top-mount handle must clear spout top by this


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SingleHoleBasinFaucetConfig:
    handle_mechanism: HandleMechanism | None = None
    spout_form: SpoutForm | None = None
    deck_base: DeckBase | None = None
    palette_style: PaletteStyle = "polished_chrome"
    # cosmetic enums
    body_section: BodySection | None = None
    knob_grip: KnobGripStyle | None = None
    spout_tip_collar: SpoutTipCollar | None = None
    base_escutcheon: BaseEscutcheon | None = None
    # continuous (independent)
    body_height: float = 0.20
    column_radius_scale: float = 1.0
    column_taper_ratio: float = 1.0
    spout_reach_scale: float = 1.0
    spout_droop_scale: float = 1.0
    aerator_size_scale: float = 1.0
    deck_footprint_scale: float = 1.0
    deck_height_scale: float = 1.0
    edge_round_scale: float = 0.5
    # continuous (conditional)
    handle_len_scale: float = 1.0
    handle_rest_tilt: float = 0.0
    knob_size_scale: float = 1.0
    collar_size_scale: float = 1.0
    escutcheon_size_scale: float = 1.0
    name: str = "single_hole_basin_faucet"


@dataclass(frozen=True)
class ResolvedConfig:
    handle_mechanism: HandleMechanism
    spout_form: SpoutForm
    deck_base: DeckBase
    palette_style: PaletteStyle
    body_section: BodySection
    knob_grip: KnobGripStyle
    spout_tip_collar: SpoutTipCollar
    base_escutcheon: BaseEscutcheon
    # geometry (resolved, scaled, derived)
    body_height: float
    col_rb: float
    col_rt: float
    deck_r: float
    deck_h: float
    deck_top_z: float
    col_base_z: float
    body_top_z: float
    spout_root_z: float
    spout_reach: float
    spout_droop: float
    spout_r: float
    aerator_scale: float
    edge_round_scale: float
    post_top_z: float
    neck_top_z: float
    handle_len_scale: float
    handle_rest_tilt: float
    knob_size_scale: float
    collar_size_scale: float
    escutcheon_size_scale: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# --------------------------------------------------------------------------- #
# config_from_seed: deterministic procedural sampling
# --------------------------------------------------------------------------- #
def config_from_seed(seed: int) -> SingleHoleBasinFaucetConfig:
    rng = random.Random(seed)
    handle = rng.choices(HANDLE_MECHANISMS, weights=HANDLE_WEIGHTS, k=1)[0]
    spout = rng.choices(SPOUT_FORMS, weights=SPOUT_WEIGHTS, k=1)[0]
    deck = rng.choices(DECK_BASES, weights=DECK_WEIGHTS, k=1)[0]
    # cosmetic enums (independent, conditional on upstream where the spec says so)
    body_section = rng.choices(BODY_SECTIONS, weights=BODY_SECTION_WEIGHTS, k=1)[0]
    knob_grip = rng.choices(KNOB_GRIPS, weights=KNOB_GRIP_WEIGHTS, k=1)[0]
    spout_tip_collar = rng.choices(
        SPOUT_TIP_COLLARS, weights=SPOUT_TIP_COLLAR_WEIGHTS, k=1
    )[0]
    base_escutcheon = rng.choices(
        BASE_ESCUTCHEONS, weights=BASE_ESCUTCHEON_WEIGHTS, k=1
    )[0]
    return SingleHoleBasinFaucetConfig(
        handle_mechanism=handle,
        spout_form=spout,
        deck_base=deck,
        palette_style=rng.choice(PALETTE_STYLES),
        body_section=body_section,
        knob_grip=knob_grip,
        spout_tip_collar=spout_tip_collar,
        base_escutcheon=base_escutcheon,
        body_height=round(rng.uniform(0.12, 0.28), 4),
        column_radius_scale=round(rng.uniform(0.75, 1.25), 4),
        column_taper_ratio=round(rng.uniform(0.78, 1.08), 4),
        spout_reach_scale=round(rng.uniform(0.70, 1.30), 4),
        spout_droop_scale=round(rng.uniform(0.75, 1.30), 4),
        aerator_size_scale=round(rng.uniform(0.80, 1.25), 4),
        deck_footprint_scale=round(rng.uniform(0.80, 1.25), 4),
        deck_height_scale=round(rng.uniform(0.80, 1.30), 4),
        edge_round_scale=round(rng.uniform(0.0, 1.0), 4),
        handle_len_scale=round(rng.uniform(0.80, 1.25), 4),
        handle_rest_tilt=round(rng.uniform(-0.14, 0.21), 4),
        knob_size_scale=round(rng.uniform(0.85, 1.20), 4),
        collar_size_scale=round(rng.uniform(0.85, 1.20), 4),
        escutcheon_size_scale=round(rng.uniform(0.90, 1.25), 4),
        name=f"seeded_single_hole_basin_faucet_{seed}",
    )


# --------------------------------------------------------------------------- #
# resolve_config: clamp -> derive equations -> inequality projection
# --------------------------------------------------------------------------- #
def resolve_config(config: SingleHoleBasinFaucetConfig | None = None) -> ResolvedConfig:
    cfg = config or SingleHoleBasinFaucetConfig()

    handle = _pick(cfg.handle_mechanism, HANDLE_MECHANISMS)
    spout = _pick(cfg.spout_form, SPOUT_FORMS)
    deck = _pick(cfg.deck_base, DECK_BASES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    body_section = _pick(cfg.body_section, BODY_SECTIONS)
    # conditional cosmetics ---------------------------------------------------
    is_knob = handle == "knob_quarter_turn"
    if is_knob:
        knob_grip = _pick(cfg.knob_grip if cfg.knob_grip not in (None, "na") else "fluted", KNOB_GRIPS)
    else:
        knob_grip = "na"
    if spout == "flat_blade":
        spout_tip_collar: SpoutTipCollar = "collared"  # flat_blade is natively collared
    else:
        spout_tip_collar = _pick(cfg.spout_tip_collar, SPOUT_TIP_COLLARS)
    base_escutcheon = _pick(cfg.base_escutcheon, BASE_ESCUTCHEONS)

    # continuous independent --------------------------------------------------
    body_height = _clamp(cfg.body_height, 0.12, 0.28)
    col_radius_scale = _clamp(cfg.column_radius_scale, 0.75, 1.25)
    taper = _clamp(cfg.column_taper_ratio, 0.78, 1.08)
    reach_scale = _clamp(cfg.spout_reach_scale, 0.70, 1.30)
    droop_scale = _clamp(cfg.spout_droop_scale, 0.75, 1.30)
    aerator_scale = _clamp(cfg.aerator_size_scale, 0.80, 1.25)
    deck_fp_scale = _clamp(cfg.deck_footprint_scale, 0.80, 1.25)
    deck_h_scale = _clamp(cfg.deck_height_scale, 0.80, 1.30)
    edge_round_scale = _clamp(cfg.edge_round_scale, 0.0, 1.0)

    col_rb = COL_R_BASE * col_radius_scale
    col_rt = col_rb * taper
    deck_r = DECK_R_BASE * deck_fp_scale
    # keep column inside the deck footprint
    col_rb = min(col_rb, deck_r - 0.006)
    col_rt = min(col_rt, deck_r - 0.006)

    deck_h_base = {
        "round_flange": DECK_H_FLANGE,
        "square_step_plate": DECK_H_SQUARE,
        "raised_pedestal": DECK_H_PEDESTAL,
    }[deck]
    deck_h = deck_h_base * deck_h_scale
    deck_top_z = deck_h

    col_base_z = deck_top_z - EMB
    body_top_z = col_base_z + body_height

    spout_root_z = deck_top_z + body_height * SPOUT_ROOT_FRAC
    spout_reach = SPOUT_REACH_BASE * reach_scale
    spout_droop = SPOUT_DROOP_BASE * droop_scale
    spout_r = SPOUT_R_BASE

    # equations (handle mount heights derived from body height) ---------------
    post_top_z = body_top_z + POST_H
    neck_top_z = body_top_z + NECK_H

    # inequality: top-mount handle must clear the spout top. The spout top is at
    # ~spout_root_z + spout_r; post_top_z is above body_top_z >> spout_root_z,
    # but project to be safe (raise the mount if a tiny body would violate it).
    spout_top_z = spout_root_z + spout_r
    if post_top_z < spout_top_z + MIN_SPOUT_CLEAR:
        post_top_z = spout_top_z + MIN_SPOUT_CLEAR
    if neck_top_z < spout_top_z + MIN_SPOUT_CLEAR:
        neck_top_z = spout_top_z + MIN_SPOUT_CLEAR

    # conditional continuous --------------------------------------------------
    is_lever = handle in ("lever_top_swivel_lift", "lever_side_disc_twist")
    handle_len_scale = _clamp(cfg.handle_len_scale, 0.80, 1.25) if is_lever else 1.0
    handle_rest_tilt = _clamp(cfg.handle_rest_tilt, -0.14, 0.21) if is_lever else 0.0
    knob_size_scale = _clamp(cfg.knob_size_scale, 0.85, 1.20) if is_knob else 1.0
    collar_size_scale = (
        _clamp(cfg.collar_size_scale, 0.85, 1.20)
        if spout_tip_collar == "collared"
        else 1.0
    )
    escutcheon_size_scale = (
        _clamp(cfg.escutcheon_size_scale, 0.90, 1.25)
        if base_escutcheon == "ring"
        else 1.0
    )

    return ResolvedConfig(
        handle_mechanism=handle,
        spout_form=spout,
        deck_base=deck,
        palette_style=palette_style,
        body_section=body_section,
        knob_grip=knob_grip,
        spout_tip_collar=spout_tip_collar,
        base_escutcheon=base_escutcheon,
        body_height=body_height,
        col_rb=col_rb,
        col_rt=col_rt,
        deck_r=deck_r,
        deck_h=deck_h,
        deck_top_z=deck_top_z,
        col_base_z=col_base_z,
        body_top_z=body_top_z,
        spout_root_z=spout_root_z,
        spout_reach=spout_reach,
        spout_droop=spout_droop,
        spout_r=spout_r,
        aerator_scale=aerator_scale,
        edge_round_scale=edge_round_scale,
        post_top_z=post_top_z,
        neck_top_z=neck_top_z,
        handle_len_scale=handle_len_scale,
        handle_rest_tilt=handle_rest_tilt,
        knob_size_scale=knob_size_scale,
        collar_size_scale=collar_size_scale,
        escutcheon_size_scale=escutcheon_size_scale,
        name=cfg.name or "single_hole_basin_faucet",
    )


def with_overrides(
    config: SingleHoleBasinFaucetConfig, **kwargs: object
) -> SingleHoleBasinFaucetConfig:
    return replace(config, **kwargs)


# --------------------------------------------------------------------------- #
# slot_choices (STRUCTURAL only — cosmetics live in meta["cosmetic_choices"])
# --------------------------------------------------------------------------- #
def slot_choices_for_config(
    config: SingleHoleBasinFaucetConfig | ResolvedConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("handle_mechanism", r.handle_mechanism),
        ("spout_form", r.spout_form),
        ("deck_base", r.deck_base),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def cosmetic_choices_for_config(
    config: SingleHoleBasinFaucetConfig | ResolvedConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("body_section", r.body_section),
        ("knob_grip", r.knob_grip),
        ("spout_tip_collar", r.spout_tip_collar),
        ("base_escutcheon", r.base_escutcheon),
    )


# --------------------------------------------------------------------------- #
# Mesh helpers (swept tube / swept box) — for the spout mesh families.
# --------------------------------------------------------------------------- #
def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _unit(v):
    n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if n < 1e-9:
        return (0.0, 0.0, 1.0)
    return (v[0] / n, v[1] / n, v[2] / n)


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _frame(tangent, up_ref=(0.0, 0.0, 1.0)):
    t = _unit(tangent)
    u = _cross(up_ref, t)
    if u[0] * u[0] + u[1] * u[1] + u[2] * u[2] < 1e-9:
        u = _cross((1.0, 0.0, 0.0), t)
    u = _unit(u)
    v = _unit(_cross(t, u))
    return t, u, v


def _path_tangents(points):
    n = len(points)
    out = []
    for i in range(n):
        if i == 0:
            out.append(_sub(points[1], points[0]))
        elif i == n - 1:
            out.append(_sub(points[-1], points[-2]))
        else:
            out.append(_sub(points[i + 1], points[i - 1]))
    return out


def _solid_tube_mesh(points, radius, segments=18):
    verts: list = []
    faces: list = []
    rings: list = []
    tans = _path_tangents(points)
    for p, tan in zip(points, tans):
        _, u, v = _frame(tan)
        ring = []
        for k in range(segments):
            a = 2.0 * math.pi * k / segments
            ca, sa = math.cos(a), math.sin(a)
            ring.append(len(verts))
            verts.append(
                (
                    p[0] + radius * (ca * u[0] + sa * v[0]),
                    p[1] + radius * (ca * u[1] + sa * v[1]),
                    p[2] + radius * (ca * u[2] + sa * v[2]),
                )
            )
        rings.append(ring)
    for i in range(len(points) - 1):
        r0, r1 = rings[i], rings[i + 1]
        for k in range(segments):
            k2 = (k + 1) % segments
            faces.append((r0[k], r0[k2], r1[k2]))
            faces.append((r0[k], r1[k2], r1[k]))
    c0 = len(verts)
    verts.append(points[0])
    for k in range(segments):
        faces.append((c0, rings[0][(k + 1) % segments], rings[0][k]))
    c1 = len(verts)
    verts.append(points[-1])
    for k in range(segments):
        faces.append((c1, rings[-1][k], rings[-1][(k + 1) % segments]))
    return MeshGeometry(vertices=verts, faces=faces)


def _hollow_tube_mesh(points, outer_r, inner_r, segments=18):
    """Thin-wall hollow swept tube: outer wall + inner wall + annular end rings.

    The central bore is an open tunnel end-to-end. The root end is embedded in
    the column (bore hidden there); the outlet end shows a real open mouth so the
    spout reads as a water pipe rather than a solid rod. Winding mirrors the
    proven gooseneck ``_variable_tube`` (outer faces out, inner faces in, washer
    rings close the wall at both ends).
    """
    inner_r = max(min(inner_r, outer_r - 1e-4), 1e-4)
    verts: list = []
    faces: list = []
    rings: list = []  # (outer_idx_list, inner_idx_list) per path point
    tans = _path_tangents(points)
    for p, tan in zip(points, tans):
        _, u, v = _frame(tan)
        outer: list = []
        inner: list = []
        for k in range(segments):
            a = 2.0 * math.pi * k / segments
            ca, sa = math.cos(a), math.sin(a)
            dx = ca * u[0] + sa * v[0]
            dy = ca * u[1] + sa * v[1]
            dz = ca * u[2] + sa * v[2]
            outer.append(len(verts))
            verts.append((p[0] + outer_r * dx, p[1] + outer_r * dy, p[2] + outer_r * dz))
            inner.append(len(verts))
            verts.append((p[0] + inner_r * dx, p[1] + inner_r * dy, p[2] + inner_r * dz))
        rings.append((outer, inner))
    n = len(points)
    for i in range(n - 1):
        o0, i0 = rings[i]
        o1, i1 = rings[i + 1]
        for k in range(segments):
            j = (k + 1) % segments
            faces.append((o0[k], o1[k], o1[j]))
            faces.append((o0[k], o1[j], o0[j]))
            faces.append((i0[k], i1[j], i1[k]))
            faces.append((i0[k], i0[j], i1[j]))
    for ring_index in (0, n - 1):
        outer, inner = rings[ring_index]
        for k in range(segments):
            j = (k + 1) % segments
            if ring_index == 0:
                faces.append((outer[k], inner[j], inner[k]))
                faces.append((outer[k], outer[j], inner[j]))
            else:
                faces.append((outer[k], inner[k], inner[j]))
                faces.append((outer[k], inner[j], outer[j]))
    return MeshGeometry(vertices=verts, faces=faces)


def _swept_box_mesh(points, half_u, half_v, off_u=0.0, off_v=0.0, up_ref=(0.0, 0.0, 1.0)):
    verts: list = []
    faces: list = []
    rings: list = []
    corners = [(-half_u, -half_v), (half_u, -half_v), (half_u, half_v), (-half_u, half_v)]
    tans = _path_tangents(points)
    for p, tan in zip(points, tans):
        _, u, v = _frame(tan, up_ref)
        ring = []
        for cu, cv in corners:
            uu, vv = cu + off_u, cv + off_v
            ring.append(len(verts))
            verts.append(
                (
                    p[0] + uu * u[0] + vv * v[0],
                    p[1] + uu * u[1] + vv * v[1],
                    p[2] + uu * u[2] + vv * v[2],
                )
            )
        rings.append(ring)
    for i in range(len(points) - 1):
        r0, r1 = rings[i], rings[i + 1]
        for k in range(4):
            k2 = (k + 1) % 4
            faces.append((r0[k], r0[k2], r1[k2]))
            faces.append((r0[k], r1[k2], r1[k]))
    # caps (quads)
    a = rings[0]
    faces.append((a[0], a[2], a[1]))
    faces.append((a[0], a[3], a[2]))
    b = rings[-1]
    faces.append((b[0], b[1], b[2]))
    faces.append((b[0], b[2], b[3]))
    return MeshGeometry(vertices=verts, faces=faces)


def _combine(*geoms):
    verts: list = []
    faces: list = []
    for g in geoms:
        off = len(verts)
        verts.extend(g.vertices)
        faces.extend((a + off, b + off, c + off) for a, b, c in g.faces)
    return MeshGeometry(vertices=verts, faces=faces)


# --------------------------------------------------------------------------- #
# Spout meshes (Slot B) — authored in body-local frame (deck on z=0).
# Returns (mesh_geometry, tip_xyz).
# --------------------------------------------------------------------------- #
def _tubular_spout(r: ResolvedConfig):
    z0 = r.spout_root_z
    reach = r.spout_reach
    droop = r.spout_droop
    pts = []
    n1 = 4
    for i in range(n1 + 1):
        pts.append((reach * 0.5 * (i / n1) - r.col_rb * 0.5, 0.0, z0))
    n2 = 10
    for i in range(1, n2 + 1):
        t = i / n2
        x = reach * 0.5 + (reach * 0.5) * math.sin(t * math.pi / 2.0)
        z = z0 - droop * (1.0 - math.cos(t * math.pi / 2.0))
        pts.append((x, 0.0, z))
    tip = pts[-1]
    # hollow thin-wall pipe (~1.8 mm wall) with an open outlet bore
    return _hollow_tube_mesh(pts, r.spout_r, r.spout_r - 0.0018), tip


def _open_channel_spout(r: ResolvedConfig):
    z0 = r.spout_root_z
    reach = r.spout_reach
    droop = r.spout_droop * 0.6
    pts = []
    n = 10
    for i in range(n + 1):
        t = i / n
        x = reach * t - r.col_rb * 0.5
        z = z0 - droop * (t * t)
        pts.append((x, 0.0, z))
    cw = r.spout_r * 1.35   # channel half width
    ch = r.spout_r * 1.7    # channel height
    wt = r.spout_r * 0.55   # wall thickness
    bottom = _swept_box_mesh(pts, cw, wt * 0.5, off_v=-(ch * 0.5 - wt * 0.5))
    left = _swept_box_mesh(pts, wt * 0.5, ch * 0.5, off_u=-(cw - wt * 0.5))
    right = _swept_box_mesh(pts, wt * 0.5, ch * 0.5, off_u=(cw - wt * 0.5))
    tip = pts[-1]
    return _combine(bottom, left, right), tip


# --------------------------------------------------------------------------- #
# Column visual (cosmetic body_section): round cone vs filleted square box.
# Authored z=0..body_height in column-local; placed at col_base_z.
# --------------------------------------------------------------------------- #
def _column_mesh(r: ResolvedConfig):
    h = r.body_height
    if r.body_section == "square":
        side = 2.0 * r.col_rb
        wp = cq.Workplane("XY").box(side, side, h, centered=(True, True, False))
        corner_r = (0.0015 + 0.006 * r.edge_round_scale)
        corner_r = min(corner_r, side * 0.45)
        if corner_r > 0.0005:
            wp = wp.edges("|Z").fillet(corner_r)
        return mesh_from_cadquery(wp, "body_column")
    rb = max(r.col_rb, 0.004)
    rt = max(r.col_rt, 0.004)
    wp = cq.Workplane("XY").circle(rb).workplane(offset=h).circle(rt).loft(combine=True)
    return mesh_from_cadquery(wp, "body_column")


# --------------------------------------------------------------------------- #
# Deck base visuals (Slot C).
# --------------------------------------------------------------------------- #
def _emit_deck(body, r: ResolvedConfig, mats):
    if r.deck_base == "round_flange":
        body.visual(
            Cylinder(radius=r.deck_r, length=r.deck_h),
            origin=Origin(xyz=(0.0, 0.0, r.deck_h / 2.0)),
            material=mats["body"],
            name="base_flange", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
        )
    elif r.deck_base == "square_step_plate":
        h_lo = r.deck_h * 0.55
        h_up = r.deck_h - h_lo
        body.visual(
            Box((2.0 * r.deck_r, 2.0 * r.deck_r, h_lo)),
            origin=Origin(xyz=(0.0, 0.0, h_lo / 2.0)),
            material=mats["body"],
            name="base_plate_lower", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
        )
        body.visual(
            Box((2.0 * r.deck_r * 0.72, 2.0 * r.deck_r * 0.72, h_up)),
            origin=Origin(xyz=(0.0, 0.0, h_lo + h_up / 2.0)),
            material=mats["body"],
            name="base_plate_upper", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
        )
    else:  # raised_pedestal (oval extruded base)
        ped = (
            cq.Workplane("XY").ellipse(r.deck_r, r.deck_r * 0.78).extrude(r.deck_h)
        )
        body.visual(
            mesh_from_cadquery(ped, "pedestal"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["body"],
            name="pedestal", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
        )


# --------------------------------------------------------------------------- #
# Cosmetic emitters (parent.visual only).
# --------------------------------------------------------------------------- #
def _emit_base_ring(body, r: ResolvedConfig, mats):
    """base_escutcheon == ring: a thin decorative ring on the deck top
    (half-embedded into the deck, footprint <= deck)."""
    if r.base_escutcheon != "ring":
        return
    ring_r = min(r.deck_r * 0.92 * r.escutcheon_size_scale, r.deck_r - 0.002)
    ring_h = 0.004
    body.visual(
        Cylinder(radius=ring_r, length=ring_h),
        origin=Origin(xyz=(0.0, 0.0, r.deck_top_z - ring_h * 0.5)),
        material=mats["gasket"],
        name="base_escutcheon_ring", material_class_id="rubber.smooth_plain",
    )


def _emit_tip_collar(body, r: ResolvedConfig, mats, tip):
    """spout_tip_collar == collared: a thin annular aerator collar half-embedded
    into the outlet (non-flat_blade spouts only; flat_blade is native)."""
    if r.spout_tip_collar != "collared":
        return
    outer = (r.spout_r + 0.0035) * r.collar_size_scale
    inner = r.spout_r * 0.55
    outer = max(outer, inner + 0.0015)
    ring = (
        cq.Workplane("XY").circle(outer).circle(inner).extrude(0.006)
    )
    body.visual(
        mesh_from_cadquery(ring, "aerator_collar"),
        origin=Origin(xyz=(tip[0] - 0.003, tip[1], tip[2])),
        material=mats["accent"],
        name="aerator_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "brushed_stainless", "matte_black"} else "metal.brass_aged"),
    )


# --------------------------------------------------------------------------- #
# Root body (deck + column + spout + cosmetics). All fixed visuals.
# --------------------------------------------------------------------------- #
def _build_body(model: ArticulatedObject, r: ResolvedConfig, mats) -> object:
    body = model.part("body")
    _emit_deck(body, r, mats)
    # column
    body.visual(
        _column_mesh(r),
        origin=Origin(xyz=(0.0, 0.0, r.col_base_z)),
        material=mats["body"],
        name="body_column", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )
    _emit_base_ring(body, r, mats)

    # spout (root-body inline visual)
    if r.spout_form == "flat_blade":
        _emit_flat_blade(body, r, mats)
    elif r.spout_form == "tubular_downturned":
        mesh, tip = _tubular_spout(r)
        body.visual(
            mesh_from_geometry(mesh, "spout_tube"),
            material=mats["body"],
            name="spout_tube", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
        )
        _emit_tip_collar(body, r, mats, tip)
        _emit_outlet_disc(body, r, mats, tip)
    else:  # open_channel
        mesh, tip = _open_channel_spout(r)
        body.visual(
            mesh_from_geometry(mesh, "spout_channel"),
            material=mats["body"],
            name="spout_channel", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
        )
        _emit_tip_collar(body, r, mats, tip)
        _emit_outlet_disc(body, r, mats, tip)

    body.inertial = Inertial.from_geometry(
        Box((2.0 * r.deck_r, 2.0 * r.deck_r, r.body_top_z)),
        mass=1.4,
        origin=Origin(xyz=(0.0, 0.0, r.body_top_z * 0.5)),
    )
    return body


def _emit_outlet_disc(body, r: ResolvedConfig, mats, tip):
    """Dark aerator ring at the spout tip: an annulus with a real central hole so
    the hollow bore reads open. Its outer edge overlaps the tube wall so it is
    never a floating island."""
    outer = r.spout_r * 0.92
    inner = r.spout_r * 0.42
    ring = cq.Workplane("XY").circle(outer).circle(inner).extrude(0.006)
    body.visual(
        mesh_from_cadquery(ring, "outlet_disc"),
        origin=Origin(xyz=(tip[0], tip[1], tip[2] - 0.001)),
        material=mats["accent"],
        name="outlet_disc", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "brushed_stainless", "matte_black"} else "metal.brass_aged"),
    )


def _emit_flat_blade(body, r: ResolvedConfig, mats):
    reach = r.spout_reach
    blade_w = r.spout_r * 2.6
    blade_h = r.spout_r * 1.4
    length = reach + r.col_rb
    cx = (reach - r.col_rb) * 0.5
    z0 = r.spout_root_z
    body.visual(
        Box((length, blade_w, blade_h)),
        origin=Origin(xyz=(cx, 0.0, z0)),
        material=mats["body"],
        name="spout_blade", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )
    tip_x = reach
    # native aerator collar (flat_blade is always collared)
    outer = (r.spout_r * 1.2) * r.collar_size_scale * r.aerator_scale
    inner = r.spout_r * 0.55
    outer = max(outer, inner + 0.0015)
    ring = cq.Workplane("XY").circle(outer).circle(inner).extrude(0.006)
    body.visual(
        mesh_from_cadquery(ring, "aerator_collar"),
        origin=Origin(xyz=(tip_x - outer, 0.0, z0 - blade_h * 0.5)),
        material=mats["accent"],
        name="aerator_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "brushed_stainless", "matte_black"} else "metal.brass_aged"),
    )
    body.visual(
        Cylinder(radius=inner * 0.8, length=0.004),
        origin=Origin(xyz=(tip_x - outer, 0.0, z0 - blade_h * 0.5 + 0.001)),
        material=mats["accent"],
        name="outlet_disc", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "brushed_stainless", "matte_black"} else "metal.brass_aged"),
    )


# --------------------------------------------------------------------------- #
# Handle mechanisms (Slot A). Each adds its own mount feature onto `body`,
# emits part(s) + REVOLUTE/PRISMATIC joints with MatingContract.
# --------------------------------------------------------------------------- #
def _emit_top_post(body, r: ResolvedConfig, mats):
    """Mounting post on the column top (for lever_top / knob)."""
    post_bot = r.body_top_z - 0.004
    post_h = r.post_top_z - post_bot
    body.visual(
        Cylinder(radius=POST_R, length=post_h),
        origin=Origin(xyz=(0.0, 0.0, post_bot + post_h / 2.0)),
        material=mats["body"],
        name="mounting_post", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )


def _emit_neck(body, r: ResolvedConfig, mats):
    """Neck stub on the column top (for push_cap)."""
    neck_bot = r.body_top_z - 0.004
    neck_h = r.neck_top_z - neck_bot
    body.visual(
        Cylinder(radius=NECK_R, length=neck_h),
        origin=Origin(xyz=(0.0, 0.0, neck_bot + neck_h / 2.0)),
        material=mats["body"],
        name="valve_neck", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )


def _build_lever_top(model, r: ResolvedConfig, body, mats):
    _emit_top_post(body, r, mats)
    block_h = 0.012
    # pivot block (child of body) ----------------------------------------------
    block = model.part("lever_pivot_block")
    block.visual(
        Cylinder(radius=0.012, length=block_h),
        origin=Origin(xyz=(0.0, 0.0, block_h / 2.0)),
        material=mats["body"],
        name="lever_pivot_block", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )
    block.inertial = Inertial.from_geometry(
        Cylinder(radius=0.012, length=block_h), mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, block_h / 2.0)),
    )
    model.articulation(
        "body_to_pivot_block",
        ArticulationType.REVOLUTE,
        parent=body,
        child=block,
        origin=Origin(xyz=(0.0, 0.0, r.post_top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=4.0, velocity=1.5, lower=-0.785, upper=0.785),
        mating=MatingContract(
            parent_face_geometry="mounting_post",
            parent_face_side="positive_z",
            child_face_geometry="lever_pivot_block",
            child_face_side="negative_z",
            contact_tol=0.004,
        ),
    )
    # lever handle (child of block) -------------------------------------------
    bar_len = 0.060 * r.handle_len_scale
    handle = model.part("lever_handle")
    handle.visual(
        Box((0.016, 0.016, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, 0.005)),
        material=mats["body"],
        name="lever_handle", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )
    handle.visual(
        Box((bar_len, 0.012, 0.009)),
        origin=Origin(xyz=(bar_len / 2.0, 0.0, 0.008)),
        material=mats["body"],
        name="handle_blade", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )
    handle.visual(
        Cylinder(radius=0.004, length=0.0025),
        origin=Origin(xyz=(0.012, 0.0, 0.013)),
        material=mats["hot"],
        name="hot_dot", material_class_id="plastic.opaque_glossy_molded",
    )
    handle.inertial = Inertial.from_geometry(
        Box((bar_len, 0.016, 0.012)), mass=0.04,
        origin=Origin(xyz=(bar_len / 2.0, 0.0, 0.006)),
    )
    model.articulation(
        "pivot_block_to_handle",
        ArticulationType.REVOLUTE,
        parent=block,
        child=handle,
        origin=Origin(xyz=(0.0, 0.0, block_h)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=4.0, velocity=1.5, lower=-0.10, upper=0.44
        ),
        mating=MatingContract(
            parent_face_geometry="lever_pivot_block",
            parent_face_side="positive_z",
            child_face_geometry="lever_handle",
            child_face_side="negative_z",
            contact_tol=0.004,
        ),
    )
    return ["lever_pivot_block", "lever_handle"], [
        "body_to_pivot_block",
        "pivot_block_to_handle",
    ]


def _build_lever_side(model, r: ResolvedConfig, body, mats):
    boss_z = r.deck_top_z + r.body_height * 0.60
    # column radius at boss height
    frac = (boss_z - r.col_base_z) / max(r.body_height, 1e-6)
    col_r_boss = r.col_rb + (r.col_rt - r.col_rb) * _clamp(frac, 0.0, 1.0)
    # Dedicated side mounting pad on the column -Y face at boss height (mirrors
    # the top post). Mating to the tapered round column's bbox face would gap;
    # the pad gives a clean, near -Y face exactly at the joint.
    pad_r = 0.012
    pad_len = 0.009
    pad_outer_y = -(col_r_boss - EMB + pad_len)
    body.visual(
        Cylinder(radius=pad_r, length=pad_len),
        origin=Origin(
            xyz=(0.0, -(col_r_boss - EMB) - pad_len / 2.0, boss_z),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["body"],
        name="side_mount_pad", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )
    boss_len = 0.030
    boss_r = 0.010
    # boss (child of body), axis along Y, inboard +Y face at local y=0 ----------
    boss = model.part("lever_boss")
    boss.visual(
        Cylinder(radius=boss_r, length=boss_len),
        origin=Origin(xyz=(0.0, -boss_len / 2.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["body"],
        name="lever_boss", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )
    boss.inertial = Inertial.from_geometry(
        Cylinder(radius=boss_r, length=boss_len), mass=0.02,
        origin=Origin(xyz=(0.0, -boss_len / 2.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "body_to_boss",
        ArticulationType.REVOLUTE,
        parent=body,
        child=boss,
        origin=Origin(xyz=(0.0, pad_outer_y + 0.001, boss_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=1.5, lower=-0.70, upper=0.70),
        mating=MatingContract(
            parent_face_geometry="side_mount_pad",
            parent_face_side="negative_y",
            child_face_geometry="lever_boss",
            child_face_side="positive_y",
            contact_tol=0.004,
        ),
    )
    # handle = disc + bar + twist rib (child of boss), twist about +X ----------
    disc_r = 0.018
    bar_len = 0.050 * r.handle_len_scale
    handle = model.part("lever_handle")
    handle.visual(
        Box((0.010, 0.008, 0.020)),
        origin=Origin(xyz=(0.0, -0.004, 0.0)),
        material=mats["body"],
        name="lever_handle", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )
    handle.visual(
        Cylinder(radius=disc_r, length=0.010),
        origin=Origin(xyz=(-0.004, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["body"],
        name="control_disc", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )
    handle.visual(
        Box((bar_len, 0.012, 0.010)),
        origin=Origin(xyz=(bar_len / 2.0, 0.0, 0.0)),
        material=mats["body"],
        name="lever_bar", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )
    # off-axis rib protruding PAST the disc rim so twisting about +X sweeps the
    # AABB (a rib inside the disc envelope would be spin-invariant).
    handle.visual(
        Box((0.012, 0.006, 0.014)),
        origin=Origin(xyz=(0.004, 0.0, disc_r + 0.004)),
        material=mats["cold"],
        name="twist_rib", material_class_id="plastic.opaque_glossy_molded",
    )
    handle.inertial = Inertial.from_geometry(
        Box((bar_len, 0.020, 0.040)), mass=0.04,
        origin=Origin(xyz=(bar_len / 3.0, 0.0, 0.0)),
    )
    model.articulation(
        "boss_to_handle",
        ArticulationType.REVOLUTE,
        parent=boss,
        child=handle,
        origin=Origin(xyz=(0.0, -boss_len, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=1.5, lower=-0.52, upper=0.52),
        mating=MatingContract(
            parent_face_geometry="lever_boss",
            parent_face_side="negative_y",
            child_face_geometry="lever_handle",
            child_face_side="positive_y",
            contact_tol=0.006,
        ),
    )
    return ["lever_boss", "lever_handle"], ["body_to_boss", "boss_to_handle"]


def _build_knob(model, r: ResolvedConfig, body, mats):
    _emit_top_post(body, r, mats)
    knob_d = 0.030 * r.knob_size_scale
    knob_h = 0.020 * r.knob_size_scale
    grip_style = r.knob_grip if r.knob_grip != "na" else "fluted"
    knob_geom = KnobGeometry(
        knob_d,
        knob_h,
        body_style="cylindrical",
        grip=KnobGrip(style=grip_style, count=18, depth=0.0008),
        center=True,
    )
    knob = model.part("flow_knob")
    knob.visual(
        mesh_from_geometry(knob_geom, "flow_knob"),
        origin=Origin(xyz=(0.0, 0.0, knob_h / 2.0)),
        material=mats["body"],
        name="flow_knob", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )
    # captured stem dipping into the post (allow_overlap), not the mating face
    knob.visual(
        Cylinder(radius=POST_R * 0.7, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, -0.005)),
        material=mats["accent"],
        name="knob_stem", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "brushed_stainless", "matte_black"} else "metal.brass_aged"),
    )
    # off-axis flow tab so the REVOLUTE turn registers on the AABB spin check
    knob.visual(
        Box((0.008, 0.010, knob_h * 0.7)),
        origin=Origin(xyz=(knob_d * 0.5 + 0.002, 0.0, knob_h * 0.5)),
        material=mats["cold"],
        name="flow_tab", material_class_id="plastic.opaque_glossy_molded",
    )
    knob.inertial = Inertial.from_geometry(
        Cylinder(radius=knob_d / 2.0, length=knob_h), mass=0.03,
        origin=Origin(xyz=(0.0, 0.0, knob_h / 2.0)),
    )
    model.articulation(
        "body_to_flow_knob",
        ArticulationType.REVOLUTE,
        parent=body,
        child=knob,
        origin=Origin(xyz=(0.0, 0.0, r.post_top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=4.0, velocity=1.5, lower=0.0, upper=1.5708),
        mating=MatingContract(
            parent_face_geometry="mounting_post",
            parent_face_side="positive_z",
            child_face_geometry="flow_knob",
            child_face_side="negative_z",
            contact_tol=0.004,
        ),
    )
    return ["flow_knob"], ["body_to_flow_knob"]


def _build_push_cap(model, r: ResolvedConfig, body, mats):
    _emit_neck(body, r, mats)
    stem_h = 0.012
    # valve stem (child of body), PRISMATIC -z press --------------------------
    stem = model.part("valve_stem")
    stem.visual(
        Cylinder(radius=0.009, length=stem_h),
        origin=Origin(xyz=(0.0, 0.0, stem_h / 2.0)),
        material=mats["accent"],
        name="valve_stem", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "brushed_stainless", "matte_black"} else "metal.brass_aged"),
    )
    # captured pin dipping into the neck bore (allow_overlap, not mating face)
    stem.visual(
        Cylinder(radius=0.006, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, -0.005)),
        material=mats["accent"],
        name="stem_pin", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"polished_chrome", "brushed_stainless", "matte_black"} else "metal.brass_aged"),
    )
    stem.inertial = Inertial.from_geometry(
        Cylinder(radius=0.009, length=stem_h), mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, stem_h / 2.0)),
    )
    model.articulation(
        "body_to_valve_stem",
        ArticulationType.PRISMATIC,
        parent=body,
        child=stem,
        origin=Origin(xyz=(0.0, 0.0, r.neck_top_z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.1, lower=0.0, upper=0.008),
        mating=MatingContract(
            parent_face_geometry="valve_neck",
            parent_face_side="positive_z",
            child_face_geometry="valve_stem",
            child_face_side="negative_z",
            contact_tol=0.004,
        ),
    )
    # push cap (child of stem), REVOLUTE Z turn -------------------------------
    cap_r = NECK_R + 0.002
    cap_h = 0.010
    cap = model.part("push_cap")
    cap.visual(
        Cylinder(radius=cap_r, length=cap_h),
        origin=Origin(xyz=(0.0, 0.0, cap_h / 2.0)),
        material=mats["body"],
        name="push_cap", material_class_id=("metal.chrome_polished" if r.palette_style in {"polished_chrome", "brushed_stainless", "brushed_gold"} else "metal.paint_coated"),
    )
    # off-axis temperature indicator protruding PAST the cap rim so the REVOLUTE
    # turn sweeps the AABB (a feature inside the cap radius is spin-invariant).
    cap.visual(
        Box((0.008, 0.006, cap_h * 0.8)),
        origin=Origin(xyz=(cap_r + 0.002, 0.0, cap_h * 0.5)),
        material=mats["hot"],
        name="temp_dot", material_class_id="plastic.opaque_glossy_molded",
    )
    cap.inertial = Inertial.from_geometry(
        Cylinder(radius=cap_r, length=cap_h), mass=0.03,
        origin=Origin(xyz=(0.0, 0.0, cap_h / 2.0)),
    )
    model.articulation(
        "valve_stem_to_push_cap",
        ArticulationType.REVOLUTE,
        parent=stem,
        child=cap,
        origin=Origin(xyz=(0.0, 0.0, stem_h)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=3.0, velocity=1.5, lower=-1.047, upper=1.047),
        mating=MatingContract(
            parent_face_geometry="valve_stem",
            parent_face_side="positive_z",
            child_face_geometry="push_cap",
            child_face_side="negative_z",
            contact_tol=0.004,
        ),
    )
    return ["valve_stem", "push_cap"], ["body_to_valve_stem", "valve_stem_to_push_cap"]


_HANDLE_BUILDERS = {
    "lever_top_swivel_lift": _build_lever_top,
    "lever_side_disc_twist": _build_lever_side,
    "knob_quarter_turn": _build_knob,
    "push_cap_press_turn": _build_push_cap,
}


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build_single_hole_basin_faucet(
    config: SingleHoleBasinFaucetConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"shbf_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }
    body = _build_body(model, r, mats)
    _HANDLE_BUILDERS[r.handle_mechanism](model, r, body, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["cosmetic_choices"] = cosmetic_choices_for_config(r)
    return model


def build_seeded_single_hole_basin_faucet(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_single_hole_basin_faucet(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def _aabb_center(aabb):
    (lo, hi) = aabb
    return tuple(0.5 * (lo[i] + hi[i]) for i in range(3))


def run_single_hole_basin_faucet_tests(
    object_model: ArticulatedObject,
    config: SingleHoleBasinFaucetConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")

    # ---- captured / seated allow_overlaps (element-scoped) ----
    if r.handle_mechanism == "lever_top_swivel_lift":
        block = object_model.get_part("lever_pivot_block")
        handle = object_model.get_part("lever_handle")
        ctx.allow_overlap(block, body, reason="pivot block seats on the mounting post top.")
        ctx.allow_overlap(handle, block, reason="lever handle heel seats on the pivot block.")
    elif r.handle_mechanism == "lever_side_disc_twist":
        boss = object_model.get_part("lever_boss")
        handle = object_model.get_part("lever_handle")
        ctx.allow_overlap(boss, body, reason="side boss is seated into the column side face.")
        ctx.allow_overlap(handle, boss, reason="control disc hub seats on the boss outboard face.")
    elif r.handle_mechanism == "knob_quarter_turn":
        knob = object_model.get_part("flow_knob")
        ctx.allow_overlap(knob, body, reason="knob stem is captured inside the mounting post bore.")
    else:  # push_cap_press_turn
        stem = object_model.get_part("valve_stem")
        cap = object_model.get_part("push_cap")
        ctx.allow_overlap(stem, body, reason="valve stem pin is captured inside the neck bore.")
        ctx.allow_overlap(cap, stem, reason="push cap seats on the valve stem top.")
        ctx.allow_overlap(cap, body, reason="push cap skirt sits over the neck top.")

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()
    ctx.fail_if_articulation_origin_far_from_geometry()

    # ---- identity / structure ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("root body present", "body" in part_names, details=str(sorted(part_names)))

    expected_handle_parts = {
        "lever_top_swivel_lift": 2,
        "lever_side_disc_twist": 2,
        "knob_quarter_turn": 1,
        "push_cap_press_turn": 2,
    }[r.handle_mechanism]
    # part / joint counts depend ONLY on the handle (cosmetics add no parts/joints)
    ctx.check(
        "part count = body + handle parts only (cosmetics add no parts)",
        len(object_model.parts) == 1 + expected_handle_parts,
        details=f"parts={sorted(part_names)} expected={1 + expected_handle_parts}",
    )
    expected_joints = {
        "lever_top_swivel_lift": 2,
        "lever_side_disc_twist": 2,
        "knob_quarter_turn": 1,
        "push_cap_press_turn": 2,
    }[r.handle_mechanism]
    ctx.check(
        "joint count depends only on handle (cosmetics add no joints)",
        len(object_model.articulations) == expected_joints,
        details=f"n_joints={len(object_model.articulations)} expected={expected_joints}",
    )

    # spout extends forward (+X) beyond the column
    body_aabb = ctx.part_world_aabb(body)
    if body_aabb is not None:
        (bxmn, _, bzmn), (bxmx, _, _) = body_aabb
        ctx.check(
            "single spout reaches forward (+X)",
            bxmx > r.col_rt + 0.04,
            details=f"x_max={bxmx:.4f} col_rt={r.col_rt:.4f}",
        )
        ctx.check("deck rests on the ground (z=0)", bzmn < 0.01, details=f"z_min={bzmn:.4f}")

    # ---- joint topology + actuation per handle ----
    if r.handle_mechanism == "lever_top_swivel_lift":
        js = object_model.get_articulation("body_to_pivot_block")
        jl = object_model.get_articulation("pivot_block_to_handle")
        ctx.check(
            "swivel is REVOLUTE about Z",
            js.articulation_type == ArticulationType.REVOLUTE and abs(js.axis[2]) > 0.99,
            details=f"type={js.articulation_type} axis={tuple(js.axis)}",
        )
        ctx.check(
            "lift is REVOLUTE about -Y",
            jl.articulation_type == ArticulationType.REVOLUTE and abs(jl.axis[1]) > 0.99,
            details=f"type={jl.articulation_type} axis={tuple(jl.axis)}",
        )
        handle = object_model.get_part("lever_handle")
        rest = ctx.part_world_aabb(handle)
        with ctx.pose({jl: 0.44}):
            lifted = ctx.part_world_aabb(handle)
        if rest is not None and lifted is not None:
            ctx.check(
                "lifting the lever raises the handle",
                lifted[1][2] > rest[1][2] + 0.010,
                details=f"rest_top={rest[1][2]:.4f} lifted_top={lifted[1][2]:.4f}",
            )
        rest_c = _aabb_center(rest) if rest is not None else None
        with ctx.pose({js: 0.785}):
            sw = ctx.part_world_aabb(handle)
        if rest_c is not None and sw is not None:
            ctx.check(
                "swivelling the lever registers",
                math.dist(rest_c, _aabb_center(sw)) > 0.003,
                details=f"disp={math.dist(rest_c, _aabb_center(sw)):.4f}",
            )

    elif r.handle_mechanism == "lever_side_disc_twist":
        jl = object_model.get_articulation("body_to_boss")
        jt = object_model.get_articulation("boss_to_handle")
        ctx.check(
            "side lift is REVOLUTE about -Y",
            jl.articulation_type == ArticulationType.REVOLUTE and abs(jl.axis[1]) > 0.99,
            details=f"type={jl.articulation_type} axis={tuple(jl.axis)}",
        )
        ctx.check(
            "twist is REVOLUTE about +X",
            jt.articulation_type == ArticulationType.REVOLUTE and abs(jt.axis[0]) > 0.99,
            details=f"type={jt.articulation_type} axis={tuple(jt.axis)}",
        )
        handle = object_model.get_part("lever_handle")
        rest = ctx.part_world_aabb(handle)
        with ctx.pose({jl: 0.70}):
            lifted = ctx.part_world_aabb(handle)
        if rest is not None and lifted is not None:
            ctx.check(
                "side lift moves the handle",
                math.dist(_aabb_center(rest), _aabb_center(lifted)) > 0.006,
                details=f"disp={math.dist(_aabb_center(rest), _aabb_center(lifted)):.4f}",
            )
        rest_c = _aabb_center(rest) if rest is not None else None
        with ctx.pose({jt: 0.52}):
            tw = ctx.part_world_aabb(handle)
        if rest_c is not None and tw is not None:
            ctx.check(
                "twisting the disc registers (off-axis rib sweeps)",
                math.dist(rest_c, _aabb_center(tw)) > 0.003,
                details=f"disp={math.dist(rest_c, _aabb_center(tw)):.4f}",
            )

    elif r.handle_mechanism == "knob_quarter_turn":
        j = object_model.get_articulation("body_to_flow_knob")
        ctx.check(
            "knob is REVOLUTE about Z",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        lim = j.motion_limits
        ctx.check(
            "knob quarter-turn range",
            lim is not None and lim.upper is not None and 1.0 < lim.upper <= 1.7,
            details=f"upper={None if lim is None else lim.upper}",
        )
        knob = object_model.get_part("flow_knob")
        rest = ctx.part_world_aabb(knob)
        with ctx.pose({j: 1.5708}):
            turned = ctx.part_world_aabb(knob)
        if rest is not None and turned is not None:
            ctx.check(
                "turning the knob registers (flow tab sweeps)",
                math.dist(_aabb_center(rest), _aabb_center(turned)) > 0.003,
                details=f"disp={math.dist(_aabb_center(rest), _aabb_center(turned)):.4f}",
            )

    else:  # push_cap_press_turn
        jp = object_model.get_articulation("body_to_valve_stem")
        jt = object_model.get_articulation("valve_stem_to_push_cap")
        ctx.check(
            "press is PRISMATIC about -z",
            jp.articulation_type == ArticulationType.PRISMATIC and abs(jp.axis[2]) > 0.99,
            details=f"type={jp.articulation_type} axis={tuple(jp.axis)}",
        )
        ctx.check(
            "cap turn is REVOLUTE about Z",
            jt.articulation_type == ArticulationType.REVOLUTE and abs(jt.axis[2]) > 0.99,
            details=f"type={jt.articulation_type} axis={tuple(jt.axis)}",
        )
        cap = object_model.get_part("push_cap")
        rest = ctx.part_world_position(cap)
        with ctx.pose({jp: 0.008}):
            pressed = ctx.part_world_position(cap)
        if rest is not None and pressed is not None:
            ctx.check(
                "pressing the cap moves it down",
                pressed[2] < rest[2] - 0.004,
                details=f"rest_z={rest[2]:.4f} pressed_z={pressed[2]:.4f}",
            )
        rest_a = ctx.part_world_aabb(cap)
        with ctx.pose({jt: 1.047}):
            turned_a = ctx.part_world_aabb(cap)
        if rest_a is not None and turned_a is not None:
            ctx.check(
                "turning the cap registers (temp dot sweeps)",
                math.dist(_aabb_center(rest_a), _aabb_center(turned_a)) > 0.003,
                details=f"disp={math.dist(_aabb_center(rest_a), _aabb_center(turned_a)):.4f}",
            )

    # ---- slot_choices / cosmetic_choices recorded ----
    ctx.check(
        "slot_choices recorded (structural triple)",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )
    ctx.check(
        "cosmetic_choices recorded separately",
        tuple(object_model.meta.get("cosmetic_choices", ())) == cosmetic_choices_for_config(r),
        details=str(object_model.meta.get("cosmetic_choices")),
    )

    return ctx.report()


__all__ = (
    "SingleHoleBasinFaucetConfig",
    "ResolvedConfig",
    "build_single_hole_basin_faucet",
    "build_seeded_single_hole_basin_faucet",
    "config_from_seed",
    "resolve_config",
    "run_single_hole_basin_faucet_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "cosmetic_choices_for_config",
    "with_overrides",
)
