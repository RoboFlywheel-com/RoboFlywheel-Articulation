# SPDX-License-Identifier: Apache-2.0

"""Container pump — modular procedural template (lotion / soap / cosmetic pump bottle).

Category identity: an upright pump-dispenser bottle whose top mechanism is the
class identity. A hollow, usually-transparent bottle (ROOT ``bottle``) rests on
z=0 with its axis along +Z; a white threaded ``collar`` is FIXED on the neck as a
shared mating interface; and one of seven top dispensing / closure mechanisms
rides on the collar:

  * press_pump / foaming_pump / gooseneck_pump — a massless ``head_carrier``
    swivels (``pump_swivel`` REVOLUTE +Z) and the head presses down
    (``pump_press`` PRISMATIC +Z); long dip tube into the bottle.
  * twist_lock_pump — a SOLID ``lock_ring`` twists (``twist_lock`` REVOLUTE +Z,
    limited 0..π/2) and the head presses on ``pump_press`` PRISMATIC +Z
    (parent = lock_ring, no massless carrier).
  * trigger_sprayer — the whole ``sprayer_head`` swivels (``sprayer_swivel``
    REVOLUTE +Z) and a finger ``trigger`` squeezes (``trigger_squeeze``
    REVOLUTE -Y).
  * flip_top_cap — a hinged ``flip_cap`` (``cap_hinge`` REVOLUTE -X) opens to
    reveal a dispensing orifice on the collar (no pump / no dip tube).
  * disc_top_cap — a FIXED ``cap_base`` (bore + side slot) carries a central
    ``disc`` that pushes down (``cap_to_disc`` PRISMATIC +Z; no pump / no tube).

Two parallel slots (spec ``Container_Pump.md``):

  * ``body_profile`` (4) — the ROOT ``bottle`` shell:
      round_body (revolve Lathe), boxy_oval (superellipse loft),
      tapered_waisted (waisted Lathe), tall_rectangular (CadQuery rect-extrude).
    All shoulders collapse to the SAME round neck so the collar always fits.
  * ``dispenser_head`` (7) — the main mechanism (each has >=1 non-fixed joint).

Per-seed palette diversity: 9 coordinated colorways x finish (clear_white_pump,
amber_natural, frosted_sage, cobalt_clinical, matte_charcoal, pearl_blush,
ceramic_ivory, chrome_apothecary, soft_touch_olive). Only clear / frosted / amber
colorways carry a transparent (alpha<1) bottle; opaque colorways relax the
transparency assertion.

Continuous size/proportion variation (height/radius/neck/head/travel/reach
scales) lives in ``resolve_config`` as clamped params, never as slot candidates.

Sources (articraft_data ``picture/Container/Pump`` 5-star pool): parent
``rec_clear-soap-dispenser-bottle-...`` + qwen forks boxy_oval / tapered_waisted /
tall_rectangular / foaming_pump / gooseneck_pump / twist_lock_pump /
trigger_sprayer / flip_top_cap / disc_top_cap.

Canonical spec:
``articraft_template_authoring/specs_modular_v1/Container_Pump.md``
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
    BoxGeometry,
    Cylinder,
    CylinderGeometry,
    Inertial,
    LatheGeometry,
    LoftGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    superellipse_profile,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyProfile = Literal[
    "round_body",
    "boxy_oval",
    "tapered_waisted",
    "tall_rectangular",
]
DispenserHead = Literal[
    "press_pump",
    "foaming_pump",
    "gooseneck_pump",
    "twist_lock_pump",
    "trigger_sprayer",
    "flip_top_cap",
    "disc_top_cap",
]
PaletteStyle = Literal[
    "clear_white_pump",
    "amber_natural",
    "frosted_sage",
    "cobalt_clinical",
    "matte_charcoal",
    "pearl_blush",
    "ceramic_ivory",
    "chrome_apothecary",
    "soft_touch_olive",
]

BODY_PROFILES: tuple[BodyProfile, ...] = (
    "round_body",
    "boxy_oval",
    "tapered_waisted",
    "tall_rectangular",
)
DISPENSER_HEADS: tuple[DispenserHead, ...] = (
    "press_pump",
    "foaming_pump",
    "gooseneck_pump",
    "twist_lock_pump",
    "trigger_sprayer",
    "flip_top_cap",
    "disc_top_cap",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "clear_white_pump",
    "amber_natural",
    "frosted_sage",
    "cobalt_clinical",
    "matte_charcoal",
    "pearl_blush",
    "ceramic_ivory",
    "chrome_apothecary",
    "soft_touch_olive",
)

# Heads that emit the massless ``head_carrier`` (swivel + press chain).
_CARRIER_HEADS: frozenset[DispenserHead] = frozenset(
    {"press_pump", "foaming_pump", "gooseneck_pump"}
)
# Heads that emit a dip tube (pump / sprayer类); flip / disc go without.
_DIP_TUBE_HEADS: frozenset[DispenserHead] = frozenset(
    {"press_pump", "foaming_pump", "gooseneck_pump", "twist_lock_pump", "trigger_sprayer"}
)
# Colorways whose bottle shell is transparent (alpha < 1).
_TRANSPARENT_PALETTES: frozenset[PaletteStyle] = frozenset(
    {"clear_white_pump", "amber_natural", "frosted_sage", "chrome_apothecary"}
)


# ---------------------------------------------------------------------------
# Palettes: 9 coordinated colorways, each with bottle / pump-head / collar-accent
# / dip-tube / label rgba + an explicit ``finish`` surface dimension. rgba values
# are anchored on the parent + foaming / twist 5-star materials and the spec's
# §Palette Style table.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Palette:
    bottle: tuple[float, float, float, float]
    head: tuple[float, float, float, float]
    accent: tuple[float, float, float, float]
    tube: tuple[float, float, float, float]
    label: tuple[float, float, float, float]
    finish: str


PALETTES: dict[PaletteStyle, _Palette] = {
    "clear_white_pump": _Palette(
        bottle=(0.74, 0.80, 0.82, 0.25),
        head=(0.93, 0.93, 0.94, 1.0),
        accent=(0.93, 0.93, 0.94, 1.0),
        tube=(0.88, 0.90, 0.90, 0.85),
        label=(0.96, 0.96, 0.94, 1.0),
        finish="clear_gloss",
    ),
    "amber_natural": _Palette(
        bottle=(0.55, 0.32, 0.10, 0.45),
        head=(0.92, 0.90, 0.84, 1.0),
        accent=(0.66, 0.50, 0.30, 1.0),
        tube=(0.55, 0.34, 0.14, 0.70),
        label=(0.86, 0.78, 0.62, 1.0),
        finish="amber_translucent",
    ),
    "frosted_sage": _Palette(
        bottle=(0.52, 0.68, 0.48, 0.55),
        head=(0.66, 0.78, 0.60, 1.0),
        accent=(0.44, 0.56, 0.38, 1.0),
        tube=(0.60, 0.74, 0.54, 0.65),
        label=(0.50, 0.64, 0.44, 1.0),
        finish="frosted_translucent",
    ),
    "cobalt_clinical": _Palette(
        bottle=(0.13, 0.28, 0.52, 1.0),
        head=(0.95, 0.96, 0.97, 1.0),
        accent=(0.95, 0.96, 0.97, 1.0),
        tube=(0.88, 0.90, 0.90, 0.85),
        label=(0.97, 0.97, 0.97, 1.0),
        finish="opaque_matte",
    ),
    "matte_charcoal": _Palette(
        bottle=(0.16, 0.16, 0.18, 1.0),
        head=(0.10, 0.10, 0.11, 1.0),
        accent=(0.22, 0.22, 0.24, 1.0),
        tube=(0.18, 0.18, 0.20, 0.90),
        label=(0.78, 0.79, 0.80, 1.0),
        finish="soft_touch_matte",
    ),
    "pearl_blush": _Palette(
        bottle=(0.90, 0.66, 0.64, 1.0),
        head=(0.86, 0.58, 0.56, 1.0),
        accent=(0.62, 0.36, 0.32, 1.0),
        tube=(0.84, 0.60, 0.58, 0.90),
        label=(0.92, 0.74, 0.72, 1.0),
        finish="pearlescent",
    ),
    "ceramic_ivory": _Palette(
        bottle=(0.86, 0.76, 0.56, 1.0),
        head=(0.88, 0.79, 0.60, 1.0),
        accent=(0.62, 0.48, 0.24, 1.0),
        tube=(0.82, 0.72, 0.52, 0.90),
        label=(0.70, 0.60, 0.42, 1.0),
        finish="ceramic_glaze",
    ),
    "chrome_apothecary": _Palette(
        bottle=(0.62, 0.46, 0.24, 0.40),
        head=(0.82, 0.84, 0.87, 1.0),
        accent=(0.80, 0.82, 0.85, 1.0),
        tube=(0.55, 0.55, 0.58, 0.75),
        label=(0.20, 0.20, 0.22, 1.0),
        finish="metallic_chrome_pump",
    ),
    "soft_touch_olive": _Palette(
        bottle=(0.28, 0.32, 0.20, 1.0),
        head=(0.11, 0.12, 0.10, 1.0),
        accent=(0.34, 0.38, 0.26, 1.0),
        tube=(0.16, 0.18, 0.14, 0.90),
        label=(0.90, 0.88, 0.78, 1.0),
        finish="soft_touch_matte",
    ),
}


# ---------------------------------------------------------------------------
# Base geometry constants (meters). Authored directly on the 5-star sources:
# BODY_R=0.030, NECK_R=0.0150, COLLAR_R=0.0185, COLLAR_TOP=0.176, etc. The whole
# hardware stack scales / rides up via resolve_config.
# ---------------------------------------------------------------------------
_BODY_R = 0.030
_BODY_TOP = 0.130  # body cylinder top / shoulder base
_SHOULDER_TOP = 0.150
_NECK_TOP = 0.168
_NECK_R = 0.0150
_COLLAR_R = 0.0185
_COLLAR_BOTTOM = 0.150
_COLLAR_TOP = 0.176
_PRESS_TRAVEL = 0.015


@dataclass(frozen=True)
class ContainerPumpConfig:
    body_profile: BodyProfile = "round_body"
    dispenser_head: DispenserHead = "press_pump"
    palette_style: PaletteStyle = "clear_white_pump"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    neck_radius_scale: float = 1.0
    head_height_scale: float = 1.0
    press_travel_scale: float = 1.0
    spout_reach_scale: float = 1.0
    name: str = "container_pump"


@dataclass(frozen=True)
class ResolvedContainerPumpConfig:
    body_profile: BodyProfile
    dispenser_head: DispenserHead
    palette_style: PaletteStyle
    transparent_body: bool
    finish: str
    emit_dip_tube: bool
    emit_carrier: bool
    # continuous scales (clamped)
    body_height_scale: float
    body_radius_scale: float
    neck_radius_scale: float
    head_height_scale: float
    press_travel_scale: float
    spout_reach_scale: float
    # derived geometry (absolute world z)
    body_r: float
    body_top: float
    shoulder_top: float
    neck_top: float
    neck_r: float
    collar_r: float
    collar_bottom: float
    collar_top: float
    bore_r: float  # collar / head bore radius (neck-driven)
    press_travel: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerPumpConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    return ContainerPumpConfig(
        body_profile=rng.choice(BODY_PROFILES),
        dispenser_head=rng.choice(DISPENSER_HEADS),
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.85, 1.20), 4),
        body_radius_scale=round(rng.uniform(0.88, 1.15), 4),
        neck_radius_scale=round(rng.uniform(0.92, 1.08), 4),
        head_height_scale=round(rng.uniform(0.85, 1.20), 4),
        press_travel_scale=round(rng.uniform(0.80, 1.15), 4),
        spout_reach_scale=round(rng.uniform(0.85, 1.20), 4),
        name=f"seeded_container_pump_{seed}",
    )


def resolve_config(
    config: ContainerPumpConfig | None = None,
) -> ResolvedContainerPumpConfig:
    cfg = config or ContainerPumpConfig()
    body_profile = _pick(cfg.body_profile, BODY_PROFILES)
    dispenser_head = _pick(cfg.dispenser_head, DISPENSER_HEADS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    h_scale = _clamp(cfg.body_height_scale, 0.85, 1.20)
    r_scale = _clamp(cfg.body_radius_scale, 0.88, 1.15)
    nr_scale = _clamp(cfg.neck_radius_scale, 0.92, 1.08)
    hh_scale = _clamp(cfg.head_height_scale, 0.85, 1.20)
    pt_scale = _clamp(cfg.press_travel_scale, 0.80, 1.15)
    sr_scale = _clamp(cfg.spout_reach_scale, 0.85, 1.20)

    # neck radius FIXED-ish (equation): the collar / head bores follow it so the
    # mechanism always fits over the neck. Body radius / height scale freely.
    neck_r = _NECK_R * nr_scale
    collar_r = neck_r + 0.0035  # COLLAR_R = NECK_R + 0.0035 (≈0.0185 nominal)
    bore_r = neck_r + 0.0010  # collar / head stem bore clearance over neck

    body_r = _BODY_R * r_scale
    # The body section scales in height; shoulder / neck / collar offsets above
    # the body top stay constant so the head-mount geometry is consistent.
    body_top = _BODY_TOP * h_scale
    shoulder_top = body_top + (_SHOULDER_TOP - _BODY_TOP)
    neck_top = shoulder_top + (_NECK_TOP - _SHOULDER_TOP)
    collar_top = neck_top + (_COLLAR_TOP - _NECK_TOP)  # collar rim 0.008 above neck top
    collar_bottom = collar_top - (_COLLAR_TOP - _COLLAR_BOTTOM)

    press_travel = _PRESS_TRAVEL * pt_scale
    # The foamer's wide mixing chamber is the translating body, unlike the
    # narrow-stem press/gooseneck heads.  Preserve a real 5 mm clearance above
    # the collar at full travel instead of letting the chamber telescope into
    # the collar shell.  This keeps the source mechanism's down-press action
    # while deriving a compatible travel from the shared collar interface.
    if dispenser_head == "foaming_pump":
        press_travel = min(press_travel, 0.005)

    return ResolvedContainerPumpConfig(
        body_profile=body_profile,
        dispenser_head=dispenser_head,
        palette_style=palette,
        transparent_body=palette in _TRANSPARENT_PALETTES,
        finish=PALETTES[palette].finish,
        emit_dip_tube=dispenser_head in _DIP_TUBE_HEADS,
        emit_carrier=dispenser_head in _CARRIER_HEADS,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        neck_radius_scale=nr_scale,
        head_height_scale=hh_scale,
        press_travel_scale=pt_scale,
        spout_reach_scale=sr_scale,
        body_r=body_r,
        body_top=body_top,
        shoulder_top=shoulder_top,
        neck_top=neck_top,
        neck_r=neck_r,
        collar_r=collar_r,
        collar_bottom=collar_bottom,
        collar_top=collar_top,
        bore_r=bore_r,
        press_travel=press_travel,
        name=cfg.name or "container_pump",
    )


def with_overrides(config: ContainerPumpConfig, **kwargs: object) -> ContainerPumpConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerPumpConfig | ResolvedContainerPumpConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedContainerPumpConfig) else resolve_config(config)
    return (
        ("body_profile", r.body_profile),
        ("dispenser_head", r.dispenser_head),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Bottle body geometry (Slot A). Authored in the bottle (root) frame, base at
# z=0. Round / waisted are revolved Lathe shells; boxy_oval is a superellipse
# loft; tall_rectangular is a CadQuery rect-extrude — never downgraded to a
# Box/Cylinder placeholder (Rule 3). All collapse the shoulder to a round neck
# at NECK_R so the collar / mechanism always fit.
# ---------------------------------------------------------------------------
def _round_body_mesh(r: ResolvedContainerPumpConfig):
    body_r, body_top = r.body_r, r.body_top
    neck_r, neck_top = r.neck_r, r.neck_top
    shoulder_top = r.shoulder_top
    wall = 0.0022
    outer = [
        (0.0, 0.0),
        (body_r, 0.004),
        (body_r, body_top),
        (neck_r + 0.004, shoulder_top),
        (neck_r, shoulder_top + 0.004),
        (neck_r, neck_top),
    ]
    inner = [
        (0.0, 0.006),
        (body_r - wall, 0.010),
        (body_r - wall, body_top),
        (neck_r + 0.004 - wall, shoulder_top),
        (neck_r - wall, shoulder_top + 0.004),
        (neck_r - wall, neck_top + 0.002),
    ]
    geo = LatheGeometry.from_shell_profiles(outer, inner, segments=48)
    return mesh_from_geometry(geo, "bottle_shell")


def _waisted_radius_at(r: ResolvedContainerPumpConfig, z: float) -> float:
    base_r = r.body_r * 1.2
    waist_r = r.body_r * 0.767
    upper_r = r.body_r * 0.933
    body_top = r.body_top
    pts = [
        (0.004, base_r),
        (0.020 * (body_top / _BODY_TOP), base_r),
        (0.040 * (body_top / _BODY_TOP), base_r - 0.004),
        (0.065 * (body_top / _BODY_TOP), waist_r),
        (0.085 * (body_top / _BODY_TOP), waist_r + 0.003),
        (0.100 * (body_top / _BODY_TOP), upper_r),
        (body_top, upper_r - 0.002),
    ]
    if z <= pts[0][0]:
        return pts[0][1]
    if z >= pts[-1][0]:
        return pts[-1][1]
    for i in range(len(pts) - 1):
        z0, r0 = pts[i]
        z1, r1 = pts[i + 1]
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0)
            return r0 + t * (r1 - r0)
    return pts[-1][1]


def _tapered_waisted_mesh(r: ResolvedContainerPumpConfig):
    base_r = r.body_r * 1.2
    waist_r = r.body_r * 0.767
    upper_r = r.body_r * 0.933
    body_top = r.body_top
    shoulder_top = r.shoulder_top
    neck_top = r.neck_top
    neck_r = r.neck_r
    w = 0.0022
    sc = body_top / _BODY_TOP
    outer = [
        (0.0, 0.0),
        (base_r - 0.006, 0.003),
        (base_r, 0.008),
        (base_r, 0.020 * sc),
        (base_r - 0.004, 0.040 * sc),
        (waist_r, 0.065 * sc),
        (waist_r + 0.003, 0.085 * sc),
        (upper_r, 0.100 * sc),
        (upper_r, body_top - 0.010),
        (upper_r - 0.002, body_top),
        (neck_r + 0.004, shoulder_top),
        (neck_r, shoulder_top + 0.004),
        (neck_r, neck_top),
    ]
    inner = [
        (0.0, 0.006),
        (base_r - 0.006 - w, 0.009),
        (base_r - w, 0.012),
        (base_r - w, 0.020 * sc),
        (base_r - 0.004 - w, 0.040 * sc),
        (waist_r - w, 0.065 * sc),
        (waist_r + 0.003 - w, 0.085 * sc),
        (upper_r - w, 0.100 * sc),
        (upper_r - w, body_top - 0.010),
        (upper_r - 0.002 - w, body_top),
        (neck_r + 0.004 - w, shoulder_top),
        (neck_r - w, shoulder_top + 0.004),
        (neck_r - w, neck_top + 0.002),
    ]
    geo = LatheGeometry.from_shell_profiles(outer, inner, segments=48)
    return mesh_from_geometry(geo, "bottle_shell")


def _se3d(w: float, d: float, exp: float, z: float):
    pts = superellipse_profile(w, d, exp, segments=48)
    return [(x, y, z) for x, y in pts]


def _ring_cap(outer_pts, inner_pts):
    geo = MeshGeometry()
    n = len(outer_pts)
    for pt in outer_pts:
        geo.add_vertex(*pt)
    for pt in inner_pts:
        geo.add_vertex(*pt)
    for i in range(n):
        j = (i + 1) % n
        geo.add_face(i, j, n + i)
        geo.add_face(j, n + j, n + i)
    return geo


def _boxy_oval_mesh(r: ResolvedContainerPumpConfig):
    # wider X than Y rounded-rect (superellipse) section lofted to a round neck.
    body_w = r.body_r * 2.0  # ~0.060 at nominal
    body_d = r.body_r * 1.2  # ~0.036 at nominal
    exp = 4.0
    body_top = r.body_top
    shoulder_top = r.shoulder_top
    neck_top = r.neck_top
    neck_r = r.neck_r
    wall = 0.0022
    outer = [
        _se3d(body_w, body_d, exp, 0.004),
        _se3d(body_w, body_d, exp, body_top),
        _se3d(body_w * 0.733, body_d * 0.944, 3.0, body_top + 0.010),
        _se3d(neck_r * 2.35, neck_r * 2.35, 2.2, shoulder_top),
        _se3d(neck_r * 2.0, neck_r * 2.0, 2.0, neck_top),
    ]
    iw = body_w - 2 * wall
    idd = body_d - 2 * wall
    inner = [
        _se3d(iw, idd, exp, 0.010),
        _se3d(iw, idd, exp, body_top),
        _se3d(body_w * 0.733 - 2 * wall, body_d * 0.944 - 2 * wall, 3.0, body_top + 0.010),
        _se3d(neck_r * 2.35 - 2 * wall, neck_r * 2.35 - 2 * wall, 2.2, shoulder_top),
        _se3d(neck_r * 2.0 - 2 * wall, neck_r * 2.0 - 2 * wall, 2.0, neck_top + 0.002),
    ]
    outer_shell = LoftGeometry(outer, cap=False, closed=True)
    inner_shell = LoftGeometry(inner, cap=False, closed=True)
    bottom_cap = _ring_cap(outer[0], inner[0])
    top_lip = _ring_cap(outer[-1], inner[-1])
    geo = outer_shell.merge(inner_shell).merge(bottom_cap).merge(top_lip)
    return mesh_from_geometry(geo, "bottle_shell")


def _tall_rectangular_mesh(r: ResolvedContainerPumpConfig):
    neck_r = r.neck_r
    body_w = r.body_r * 2.167  # ~0.065 at nominal
    # Narrow (Y) axis floored well above the neck diameter so the shoulder always
    # tapers strictly inward to the round neck (keeps the CadQuery loft valid).
    body_d = max(r.body_r * 1.267, neck_r * 2.0 + 0.014)  # ~0.038 at nominal
    body_top = r.body_top
    shoulder_top = r.shoulder_top
    neck_top = r.neck_top
    wall = 0.0022
    shoulder_h = shoulder_top - body_top
    neck_h = neck_top - shoulder_top
    # The shoulder must taper strictly inward from the body rect in BOTH axes
    # (a narrow-Y body that tapers *outward* to the neck collar degenerates the
    # CadQuery loft). The neck (diameter 2*neck_r) must fit inside the shoulder
    # top rect with margin, so the shoulder top is clamped between those bounds.
    shoulder_top_w = _clamp(neck_r * 2.0 + 0.008, neck_r * 2.0 + 0.004, body_w - 0.006)
    shoulder_top_d = _clamp(neck_r * 2.0 + 0.008, neck_r * 2.0 + 0.004, body_d - 0.006)

    # Primary path: CadQuery rect-extrude body -> rect->rect shoulder loft ->
    # round neck, hollowed by an independent inner-loft boolean cut (matches the
    # 5-star source's rect-extrude+cut primitive). A few extreme scale combos
    # trip OCC's loft/boolean robustness; those fall back to an equivalent
    # rounded-rect *lofted hollow shell* (still a genuine sculpted shell, not a
    # Box/Cylinder downgrade — the same primitive class as the round/oval bodies).
    try:
        outer_body = cq.Workplane("XY").rect(body_w, body_d).extrude(body_top)
        outer_shoulder = (
            outer_body.faces(">Z").workplane()
            .rect(body_w, body_d).toPending()
            .workplane(offset=shoulder_h)
            .rect(shoulder_top_w, shoulder_top_d).toPending()
            .loft()
        )
        outer_neck = (
            outer_shoulder.faces(">Z").workplane().circle(neck_r).extrude(neck_h)
        )
        iw = body_w - 2 * wall
        idd = body_d - 2 * wall
        inner_body = (
            cq.Workplane("XY").workplane(offset=wall).rect(iw, idd).extrude(body_top - wall)
        )
        istw = shoulder_top_w - 2 * wall
        istd = shoulder_top_d - 2 * wall
        inner_shoulder = (
            inner_body.faces(">Z").workplane()
            .rect(iw, idd).toPending()
            .workplane(offset=shoulder_h)
            .rect(istw, istd).toPending()
            .loft()
        )
        inner_neck = (
            inner_shoulder.faces(">Z").workplane().circle(neck_r - wall).extrude(neck_h + wall)
        )
        bottle_solid = outer_neck.cut(inner_neck)
        # Sanity-check the boolean did not collapse or over-cut the neck (some
        # compressed scale combos silently produce a body whose neck is removed,
        # leaving the collar / threads floating). Require the full footprint AND a
        # neck reaching near neck_top; otherwise fall back to the lofted shell.
        #
        # ALSO require the cavity to be genuinely HOLLOW & OPEN at the mouth: the
        # CadQuery loft+cut occasionally returns a body whose inner cut silently
        # no-ops (the on-axis core stays solid up to the neck), which reads as a
        # molded slab under the mouth. Probe the axis just below the rim and inside
        # the body; if either is solid, the mouth is plugged — fall back to the
        # explicit lofted hollow shell (which is open by construction).
        bb = bottle_solid.val().BoundingBox()
        solid = bottle_solid.val()
        mouth_open = not solid.isInside(
            cq.Vector(0.0, 0.0, neck_top - 0.004), tolerance=1e-6
        )
        core_hollow = not solid.isInside(
            cq.Vector(0.0, 0.0, body_top * 0.5), tolerance=1e-6
        )
        if (
            max(bb.xlen, bb.ylen) > body_w * 0.7
            and bb.zmax > neck_top - 0.006
            and bb.zmin < 0.004
            and mouth_open
            and core_hollow
        ):
            return mesh_from_cadquery(bottle_solid, "bottle_shell")
    except Exception:
        pass
    return _rect_loft_shell(r, body_w, body_d, shoulder_top_w, shoulder_top_d, wall)


def _rect_loft_shell(r, body_w, body_d, st_w, st_d, wall):
    """Rounded-rect lofted hollow shell fallback for tall_rectangular: outer +
    inner rounded-rect sections lofted to the round neck, capped at the base and
    top lip — an equivalent sculpted hollow shell (not a Box)."""
    body_top, shoulder_top, neck_top, neck_r = r.body_top, r.shoulder_top, r.neck_top, r.neck_r
    corner = 0.006

    def rr(w, d, z):
        return [(x, y, z) for x, y in _rounded_rect_pts(w, d, corner)]

    def circ(rad, z, n):
        return [(rad * math.cos(2 * math.pi * i / n), rad * math.sin(2 * math.pi * i / n), z)
                for i in range(n)]

    base = rr(body_w, body_d, 0.004)
    count = len(base)
    # A straight ROUND neck section (circle at neck_r) from just above the
    # shoulder up to the rim, so the round neck-thread rings always touch the
    # wall (no part-internal island) on this lofted fallback body.
    neck_base_z = neck_top - 0.016
    outer = [
        rr(body_w, body_d, 0.004),
        rr(body_w, body_d, body_top),
        rr(st_w, st_d, shoulder_top),
        circ(neck_r, neck_base_z, count),
        circ(neck_r, neck_top, count),
    ]
    inner = [
        rr(body_w - 2 * wall, body_d - 2 * wall, 0.010),
        rr(body_w - 2 * wall, body_d - 2 * wall, body_top),
        rr(st_w - 2 * wall, st_d - 2 * wall, shoulder_top),
        circ(neck_r - wall, neck_base_z, count),
        circ(neck_r - wall, neck_top + 0.002, count),
    ]
    outer_shell = LoftGeometry(outer, cap=False, closed=True)
    inner_shell = LoftGeometry(inner, cap=False, closed=True)
    bottom_cap = _ring_cap(
        [(p[0], p[1], p[2]) for p in outer[0]], [(p[0], p[1], p[2]) for p in inner[0]]
    )
    top_lip = _ring_cap(
        [(p[0], p[1], p[2]) for p in outer[-1]], [(p[0], p[1], p[2]) for p in inner[-1]]
    )
    geo = outer_shell.merge(inner_shell).merge(bottom_cap).merge(top_lip)
    return mesh_from_geometry(geo, "bottle_shell")


def _rounded_rect_pts(width: float, depth: float, radius: float, n: int = 6):
    radius = min(radius, width / 2 - 0.001, depth / 2 - 0.001)
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


def _bottle_mesh(r: ResolvedContainerPumpConfig):
    if r.body_profile == "boxy_oval":
        return _boxy_oval_mesh(r)
    if r.body_profile == "tapered_waisted":
        return _tapered_waisted_mesh(r)
    if r.body_profile == "tall_rectangular":
        return _tall_rectangular_mesh(r)
    return _round_body_mesh(r)


def _label_mesh(r: ResolvedContainerPumpConfig):
    """Wrap-around label sleeve on the lower body (a body visual). Hugs the
    body wall so it stays connected (no part-internal island)."""
    z0 = r.body_top * 0.31
    z1 = r.body_top * 0.85
    if r.body_profile == "boxy_oval":
        body_w = r.body_r * 2.0
        body_d = r.body_r * 1.2
        exp = 4.0
        lo, li = 0.0008, -0.0002
        ob = _se3d(body_w + 2 * lo, body_d + 2 * lo, exp, z0)
        ot = _se3d(body_w + 2 * lo, body_d + 2 * lo, exp, z1)
        ib = _se3d(body_w + 2 * li, body_d + 2 * li, exp, z0)
        it = _se3d(body_w + 2 * li, body_d + 2 * li, exp, z1)
        outer_sleeve = LoftGeometry([ob, ot], cap=False, closed=True)
        inner_sleeve = LoftGeometry([ib, it], cap=False, closed=True)
        geo = outer_sleeve.merge(inner_sleeve).merge(_ring_cap(ob, ib)).merge(_ring_cap(ot, it))
        return mesh_from_geometry(geo, "label_band")
    if r.body_profile == "tall_rectangular":
        body_w = r.body_r * 2.167
        body_d = r.body_r * 1.267
        proud = 0.0008
        label_outer = (
            cq.Workplane("XY").workplane(offset=z0)
            .rect(body_w + 2 * proud, body_d + 2 * proud).extrude(z1 - z0)
        )
        label_inner = (
            cq.Workplane("XY").workplane(offset=z0)
            .rect(body_w - 0.0004, body_d - 0.0004).extrude(z1 - z0)
        )
        return mesh_from_cadquery(label_outer.cut(label_inner), "label_band")
    if r.body_profile == "tapered_waisted":
        n = 6
        outer = [
            (_waisted_radius_at(r, z0 + (z1 - z0) * i / (n - 1)) + 0.0008,
             z0 + (z1 - z0) * i / (n - 1))
            for i in range(n)
        ]
        inner = [
            (_waisted_radius_at(r, z0 + (z1 - z0) * i / (n - 1)) - 0.0002,
             z0 + (z1 - z0) * i / (n - 1))
            for i in range(n)
        ]
        geo = LatheGeometry.from_shell_profiles(outer, inner, segments=48)
        return mesh_from_geometry(geo, "label_band")
    # round
    body_r = r.body_r
    geo = LatheGeometry.from_shell_profiles(
        [(body_r + 0.0008, z0), (body_r + 0.0008, z1)],
        [(body_r - 0.0002, z0), (body_r - 0.0002, z1)],
        segments=48,
    )
    return mesh_from_geometry(geo, "label_band")


def _neck_threads_mesh(r: ResolvedContainerPumpConfig):
    # Thread ridges sit in the round-neck zone just below the rim (where EVERY
    # body profile is a circle of radius neck_r) and embed slightly into the wall
    # (ring center at neck_r, tube straddling it) so they always touch the shell —
    # avoiding a part-internal island on the lofted / cadquery body profiles.
    neck_r = r.neck_r
    solids: list[cq.Shape] = []
    # Place the rings in the SOLID round-neck band (between the shoulder and just
    # below the open rim) — the tall_rectangular cadquery body is open-topped at
    # the rim, so threads too close to neck_top would float above the wall.
    lo = r.shoulder_top + 0.003
    span = (r.neck_top - 0.005) - lo
    for frac in (0.0, 0.5, 1.0):
        solids.append(
            cq.Solid.makeTorus(
                neck_r,
                0.0013,
                cq.Vector(0.0, 0.0, lo + span * frac),
            )
        )
    # Keep the three disjoint ridges as one exact CadQuery compound.  BRep
    # provenance makes each torus a closed, evaluable material region; the
    # previous merged surface mesh was open and correctly blocked formal mass.
    return mesh_from_cadquery(cq.Compound.makeCompound(solids), "neck_threads")


# ---------------------------------------------------------------------------
# Collar (shared mating interface). Authored in absolute world z then rebased to
# a COLLAR-LOCAL frame (local z=0 at the joint origin, world z=collar_bottom) by a
# final ``geo.translate(0,0,-mount)`` — so the FIXED joint origin lands inside both
# the bottle and the collar AABB (baseline articulation-origin check). flip_top_cap
# adds hinge lugs + top plate + dispensing orifice; disc_top_cap keeps the plain
# collar (cap_base carries the bore). All heads ride on this collar.
# ---------------------------------------------------------------------------
def _collar_mount_z(r: ResolvedContainerPumpConfig) -> float:
    # Collar-local origin sits just below the neck rim — inside both the bottle
    # neck AABB (every body profile reaches neck_top) and the collar band — so
    # the bottle_to_collar FIXED joint origin clears the articulation-origin check
    # for all four body profiles.
    return r.neck_top - 0.006


def _collar_bore_r(r: ResolvedContainerPumpConfig) -> float:
    # OPEN MOUTH bore. Tracks the bottle neck (realistic thin wall ~cr-bore) but is
    # capped at _BORE_CAP so the ON-AXIS closure joint origins (the +Z swivel /
    # twist spins and the FIXED bottle/cap origins, all on the centerline so the
    # heads spin TRUE about world +Z) stay within the baseline 15mm
    # origin-to-geometry tolerance against the (now hollow) collar wall. The bore
    # is always wider than the bottle's inner neck so looking down the neck you see
    # straight into the hollow cavity — no molded slab, no on-axis floor / plug.
    return _clamp(r.neck_r - 0.0015, 0.0120, 0.0135)


def _collar_mesh(r: ResolvedContainerPumpConfig):
    cb, ct = r.collar_bottom, r.collar_top
    cr = r.collar_r
    # OPEN MOUTH: the collar is an open annular tube (no on-axis floor / plug). The
    # bore is open all the way through from the rim down to the bottle neck, so the
    # inner cavity is visible through the mouth. One connected shell, ~5mm wall.
    bore = _collar_bore_r(r)
    # The inner bore wall runs slightly proud of the outer rim (to ct+0.002) so the
    # collar throat seats the head stack / sprayer body that rests just above the
    # rim — preserving the seated contact that the narrow-bore version provided.
    outer = [
        (bore, cb),
        (cr, cb),
        (cr, ct),
        (bore, ct),
    ]
    inner = [
        (bore, cb),
        (bore, ct + 0.002),
    ]
    geo = LatheGeometry.from_shell_profiles(outer, inner, segments=48)

    if r.dispenser_head == "flip_top_cap":
        geo = geo.merge(_flip_collar_extras(r))
    return mesh_from_geometry(geo, "collar_shell")


def _collar_knurl_mesh(r: ResolvedContainerPumpConfig):
    cr = r.collar_r
    cb, ct = r.collar_bottom, r.collar_top
    h = ct - cb
    geo = None
    for i in range(22):
        ang = 2 * math.pi * i / 22
        rib = CylinderGeometry(0.0012, h, radial_segments=6)
        rib.translate(cr - 0.0002, 0.0, cb + h / 2.0)
        rib.rotate_z(ang)
        geo = rib if geo is None else geo.merge(rib)
    return mesh_from_geometry(geo, "collar_knurl")


# flip_top_cap collar hinge geometry (world z).
def _flip_params(r: ResolvedContainerPumpConfig):
    lug_height = 0.006
    hinge_y = r.collar_r - 0.002
    hinge_z = r.collar_top + lug_height / 2.0
    return lug_height, hinge_y, hinge_z


def _flip_collar_extras(r: ResolvedContainerPumpConfig):
    lug_height, hinge_y, _ = _flip_params(r)
    ct, cr = r.collar_top, r.collar_r
    orifice_r = 0.004
    orifice_h = 0.004
    plate_thickness = 0.0015
    plate_inner = orifice_r - 0.0005
    geo = LatheGeometry(
        [
            (plate_inner, ct),
            (cr - 0.001, ct),
            (cr - 0.001, ct + plate_thickness),
            (plate_inner, ct + plate_thickness),
        ],
        segments=36,
    )
    lug_w, lug_d = 0.004, 0.005
    for sign in (-1.0, 1.0):
        lug = BoxGeometry((lug_w, lug_d, lug_height + 0.002))
        lug.translate(sign * 0.006, hinge_y, ct + (lug_height + 0.002) / 2.0 - 0.001)
        geo = geo.merge(lug)
    pin = CylinderGeometry(0.0012, 0.022, radial_segments=12)
    pin.rotate_y(math.pi / 2.0)
    pin.translate(0.0, hinge_y, ct + lug_height / 2.0)
    geo = geo.merge(pin)
    orifice = CylinderGeometry(orifice_r, orifice_h + 0.002, radial_segments=16)
    orifice.translate(0.0, 0.0, ct + (orifice_h + 0.002) / 2.0 - 0.001)
    geo = geo.merge(orifice)
    return geo


def _flip_cap_mesh(r: ResolvedContainerPumpConfig):
    lug_height, hinge_y, hinge_z = _flip_params(r)
    ct = r.collar_top
    cap_radius = r.bore_r + 0.0023  # ≈0.0165 nominal (just inside collar bore rim)
    cap_thickness = 0.003
    disc_center_y = -hinge_y
    disc_center_z = ct + cap_thickness / 2.0 - hinge_z
    disc_profile = [
        (0.0, disc_center_z - cap_thickness / 2.0),
        (cap_radius - 0.001, disc_center_z - cap_thickness / 2.0),
        (cap_radius, disc_center_z - cap_thickness / 2.0 + 0.0005),
        (cap_radius, disc_center_z + cap_thickness / 2.0 - 0.0005),
        (cap_radius - 0.001, disc_center_z + cap_thickness / 2.0),
        (0.0, disc_center_z + cap_thickness / 2.0),
    ]
    geo = LatheGeometry(disc_profile, segments=36)
    geo.translate(0.0, disc_center_y, 0.0)
    tab = BoxGeometry((0.008, 0.005, lug_height - 0.001))
    tab.translate(0.0, 0.002, 0.0)
    geo = geo.merge(tab)
    thumb = BoxGeometry((0.008, 0.005, 0.005))
    thumb.translate(0.0, disc_center_y - cap_radius - 0.001, disc_center_z + 0.001)
    geo = geo.merge(thumb)
    return mesh_from_geometry(geo, "cap_disc")


# ---------------------------------------------------------------------------
# Carrier (massless swivel link) for press / foaming / gooseneck. The carrier
# flange rests on the collar top so the head spins on a real seat.
# ---------------------------------------------------------------------------
def _head_mount_z(r: ResolvedContainerPumpConfig) -> float:
    # World z of the head-stack local origin (carrier / sprayer). At the collar
    # top rim: the on-axis swivel / press origin lands in the (now narrow-bore)
    # collar throat, and the carrier hub / sprayer base straddle it. Children are
    # authored in world z and rebased by this mount (world placement unchanged).
    return r.collar_top


def _carrier_hub_mesh(r: ResolvedContainerPumpConfig):
    cr, ct = r.collar_r, r.collar_top
    hub = CylinderGeometry(cr, 0.004, radial_segments=24)
    hub.translate(0.0, 0.0, ct + 0.002)
    return mesh_from_geometry(hub, "carrier_hub")


# ---------------------------------------------------------------------------
# Pump heads (press / gooseneck) — cap body + curved spout/gooseneck + stem.
# Authored in absolute world z (parent / fork convention). The press joint
# origin is (0,0,0) and the stem geometry contains the +Z axis so the on-axis
# joint origin lands within the head AABB.
# ---------------------------------------------------------------------------
def _press_head_mesh(r: ResolvedContainerPumpConfig):
    ct = r.collar_top
    hh = r.head_height_scale
    reach = r.spout_reach_scale
    cap_z0 = ct + 0.008  # ≈0.184 nominal
    cap_h = 0.024 * hh
    body = LatheGeometry(
        [
            (0.0, cap_z0),
            (0.013, cap_z0),
            (0.015, cap_z0 + 0.006 * hh),
            (0.015, cap_z0 + cap_h - 0.008 * hh),
            (0.013, cap_z0 + cap_h - 0.002 * hh),
            (0.0, cap_z0 + cap_h),
        ],
        segments=40,
    )
    geo = body
    spout_z = cap_z0 + 0.012 * hh
    spout_pts = [
        (0.010, 0.0, spout_z),
        (0.022 * reach, 0.0, spout_z),
        (0.033 * reach, 0.0, spout_z - 0.004),
        (0.040 * reach, 0.0, spout_z - 0.013),
        (0.041 * reach, 0.0, spout_z - 0.023),
    ]
    spout = tube_from_spline_points(spout_pts, radius=0.0055, samples_per_segment=14, radial_segments=14)
    geo = geo.merge(spout)
    tip = CylinderGeometry(0.0062, 0.004, radial_segments=16)
    tip.translate(0.041 * reach, 0.0, spout_z - 0.025)
    geo = geo.merge(tip)
    stem = CylinderGeometry(0.0085, 0.040, radial_segments=20)
    stem.translate(0.0, 0.0, ct - 0.010)  # spans down through the collar bore
    geo = geo.merge(stem)
    return mesh_from_geometry(geo, "head_shell")


def _gooseneck_head_mesh(r: ResolvedContainerPumpConfig):
    ct = r.collar_top
    hh = r.head_height_scale
    reach = r.spout_reach_scale
    cap_z0 = ct + 0.008
    cap_h = 0.024 * hh
    body = LatheGeometry(
        [
            (0.0, cap_z0),
            (0.013, cap_z0),
            (0.015, cap_z0 + 0.006 * hh),
            (0.015, cap_z0 + cap_h - 0.008 * hh),
            (0.013, cap_z0 + cap_h - 0.002 * hh),
            (0.0, cap_z0 + cap_h),
        ],
        segments=40,
    )
    geo = body
    base = cap_z0 + 0.014  # ≈0.198 nominal exit
    arc = 0.106 * hh  # rise above the head
    gooseneck_pts = [
        (0.012, 0.0, base),
        (0.013, 0.0, base + 0.027 * hh),
        (0.016, 0.0, base + 0.057 * hh),
        (0.024 * reach, 0.0, base + 0.082 * hh),
        (0.040 * reach, 0.0, base + 0.100 * hh),
        (0.058 * reach, 0.0, base + arc),
        (0.074 * reach, 0.0, base + 0.096 * hh),
        (0.084 * reach, 0.0, base + 0.076 * hh),
        (0.088 * reach, 0.0, base + 0.052 * hh),
        (0.086 * reach, 0.0, base + 0.032 * hh),
        (0.082 * reach, 0.0, base + 0.017 * hh),
    ]
    gooseneck = tube_from_spline_points(gooseneck_pts, radius=0.004, samples_per_segment=16, radial_segments=16)
    geo = geo.merge(gooseneck)
    tip = CylinderGeometry(0.0050, 0.004, radial_segments=16)
    tip.translate(0.082 * reach, 0.0, base + 0.015 * hh)
    geo = geo.merge(tip)
    stem = CylinderGeometry(0.0085, 0.040, radial_segments=20)
    stem.translate(0.0, 0.0, ct - 0.010)
    geo = geo.merge(stem)
    return mesh_from_geometry(geo, "head_shell")


# Foaming head: tall wide chamber + grip + flat actuator + stubby spout + stem.
def _foamer_chamber_mesh(r: ResolvedContainerPumpConfig):
    ct = r.collar_top
    hh = r.head_height_scale
    foamer_r = max(r.collar_r + 0.0015, 0.020)
    f_bottom = ct + 0.010  # ≈0.186
    f_top = f_bottom + 0.072 * hh
    outer = [
        (0.0, f_bottom),
        (foamer_r - 0.003, f_bottom),
        (foamer_r, f_bottom + 0.004),
        (foamer_r, f_top - 0.004),
        (foamer_r - 0.003, f_top),
        (0.0, f_top),
    ]
    wall = 0.002
    inner = [
        (0.0, f_bottom + 0.003),
        (foamer_r - wall - 0.003, f_bottom + 0.003),
        (foamer_r - wall, f_bottom + 0.006),
        (foamer_r - wall, f_top - 0.004),
        (foamer_r - wall - 0.003, f_top - 0.001),
        (0.0, f_top - 0.001),
    ]
    geo = LatheGeometry.from_shell_profiles(outer, inner, segments=48)
    return mesh_from_geometry(geo, "foamer_chamber")


def _foamer_geom(r: ResolvedContainerPumpConfig):
    ct = r.collar_top
    hh = r.head_height_scale
    foamer_r = max(r.collar_r + 0.0015, 0.020)
    f_bottom = ct + 0.010
    f_top = f_bottom + 0.072 * hh
    return foamer_r, f_bottom, f_top


def _chamber_grip_mesh(r: ResolvedContainerPumpConfig):
    foamer_r, f_bottom, f_top = _foamer_geom(r)
    geo = None
    n_ribs = 16
    grip_h = f_top - f_bottom - 0.012
    grip_center_z = (f_bottom + f_top) / 2.0
    for i in range(n_ribs):
        ang = 2 * math.pi * i / n_ribs
        rib = CylinderGeometry(0.0009, grip_h, radial_segments=4)
        rib.translate(foamer_r + 0.0003, 0.0, grip_center_z)
        rib.rotate_z(ang)
        geo = rib if geo is None else geo.merge(rib)
    return mesh_from_geometry(geo, "chamber_grip")


def _actuator_mesh(r: ResolvedContainerPumpConfig):
    _, _, f_top = _foamer_geom(r)
    act_r = max(r.collar_r + 0.0045, 0.023)
    act_h = 0.007
    profile = [
        (0.0, f_top),
        (act_r - 0.002, f_top),
        (act_r, f_top + 0.002),
        (act_r, f_top + act_h - 0.002),
        (act_r - 0.002, f_top + act_h),
        (0.0, f_top + act_h),
    ]
    geo = LatheGeometry(profile, segments=48)
    return mesh_from_geometry(geo, "actuator_cap")


def _foamer_spout_mesh(r: ResolvedContainerPumpConfig):
    foamer_r, _, f_top = _foamer_geom(r)
    reach = r.spout_reach_scale
    spout_z = f_top - 0.014
    spout_r = 0.007
    spout_reach = 0.015 * reach
    spout_pts = [
        (foamer_r - 0.002, 0.0, spout_z),
        (foamer_r + 0.005, 0.0, spout_z - 0.001),
        (foamer_r + spout_reach, 0.0, spout_z - 0.004),
    ]
    geo = tube_from_spline_points(spout_pts, radius=spout_r, samples_per_segment=10, radial_segments=14)
    tip = CylinderGeometry(spout_r + 0.001, 0.005, radial_segments=16)
    tip.translate(foamer_r + spout_reach, 0.0, spout_z - 0.004)
    geo = geo.merge(tip)
    return mesh_from_geometry(geo, "foamer_spout")


def _foamer_stem_mesh(r: ResolvedContainerPumpConfig):
    _, f_bottom, _ = _foamer_geom(r)
    stem_h = 0.040
    stem = CylinderGeometry(0.009, stem_h, radial_segments=20)
    stem.translate(0.0, 0.0, f_bottom - stem_h / 2.0)
    return mesh_from_geometry(stem, "foamer_stem")


# Twist-lock: solid lock_ring (grip ribs + bayonet lugs) + head with cam pins.
def _lock_ring_geom(r: ResolvedContainerPumpConfig):
    ring_h = 0.010
    z_bot = r.collar_top
    z_top = z_bot + ring_h
    ring_outer_r = r.collar_r - 0.001
    ring_inner_r = r.bore_r - 0.005  # bore for the head stem (clears the stem)
    return ring_h, z_bot, z_top, ring_outer_r, ring_inner_r


def _lock_ring_mesh(r: ResolvedContainerPumpConfig):
    ring_h, z_bot, z_top, ring_outer_r, ring_inner_r = _lock_ring_geom(r)
    outer_profile = [
        (ring_inner_r, z_bot),
        (ring_outer_r, z_bot),
        (ring_outer_r, z_top),
        (ring_inner_r, z_top),
    ]
    inner_profile = [
        (ring_inner_r - 0.001, z_bot + 0.001),
        (ring_inner_r - 0.001, z_top - 0.001),
    ]
    geo = LatheGeometry.from_shell_profiles(outer_profile, inner_profile, segments=36)
    for i in range(6):
        ang = 2 * math.pi * i / 6
        rib = CylinderGeometry(0.0015, ring_h - 0.001, radial_segments=6)
        rib.translate(ring_outer_r + 0.0005, 0.0, z_bot + ring_h / 2.0)
        rib.rotate_z(ang)
        geo = geo.merge(rib)
    lug_z = z_bot + ring_h * 0.35
    for i in range(2):
        ang = 2 * math.pi * i / 2 + math.pi / 4.0
        lug = CylinderGeometry(0.002, 0.006, radial_segments=8)
        lug.rotate_x(math.pi / 2.0)
        lug.translate(ring_inner_r - 0.006 * 0.3, 0.0, lug_z)
        lug.rotate_z(ang)
        geo = geo.merge(lug)
    return mesh_from_geometry(geo, "lock_ring_shell")


def _twist_head_mesh(r: ResolvedContainerPumpConfig):
    ct = r.collar_top
    hh = r.head_height_scale
    reach = r.spout_reach_scale
    cap_z0 = ct + 0.008
    cap_h = 0.024 * hh
    body = LatheGeometry(
        [
            (0.0, cap_z0),
            (0.013, cap_z0),
            (0.015, cap_z0 + 0.006 * hh),
            (0.015, cap_z0 + cap_h - 0.008 * hh),
            (0.013, cap_z0 + cap_h - 0.002 * hh),
            (0.0, cap_z0 + cap_h),
        ],
        segments=40,
    )
    geo = body
    spout_z = cap_z0 + 0.012 * hh
    spout_pts = [
        (0.010, 0.0, spout_z),
        (0.022 * reach, 0.0, spout_z),
        (0.033 * reach, 0.0, spout_z - 0.004),
        (0.040 * reach, 0.0, spout_z - 0.013),
        (0.041 * reach, 0.0, spout_z - 0.023),
    ]
    spout = tube_from_spline_points(spout_pts, radius=0.0055, samples_per_segment=14, radial_segments=14)
    geo = geo.merge(spout)
    tip = CylinderGeometry(0.0062, 0.004, radial_segments=16)
    tip.translate(0.041 * reach, 0.0, spout_z - 0.025)
    geo = geo.merge(tip)
    stem = CylinderGeometry(0.0085, 0.040, radial_segments=20)
    stem.translate(0.0, 0.0, ct - 0.010)
    geo = geo.merge(stem)
    # cam pins on the stem that engage the lock ring bayonet lugs.
    ring_h, z_bot, _, _, _ = _lock_ring_geom(r)
    cam_z = z_bot + ring_h * 0.35
    for i in range(2):
        ang = 2 * math.pi * i / 2 + math.pi / 4.0
        pin = CylinderGeometry(0.0018, 0.008, radial_segments=8)
        pin.rotate_x(math.pi / 2.0)
        pin.translate(0.007, 0.0, cam_z)
        pin.rotate_z(ang)
        geo = geo.merge(pin)
    return mesh_from_geometry(geo, "head_shell")


# Trigger sprayer: body (with inline pivot bosses) + nozzle + stem; trigger lever.
def _sprayer_geom(r: ResolvedContainerPumpConfig):
    hh = r.head_height_scale
    # Seat the sprayer body base on the collar rim (its base flange drops onto the
    # open collar throat lip) so it contacts the collar even with the widened bore.
    body_bottom = r.collar_top
    body_top = body_bottom + 0.037 * hh
    body_r = 0.0135
    nozzle_exit_z = body_bottom + 0.022 * hh
    pivot_z = body_bottom + 0.018 * hh
    pivot_x = 0.020
    return body_bottom, body_top, body_r, nozzle_exit_z, pivot_z, pivot_x


def _sprayer_body_mesh(r: ResolvedContainerPumpConfig):
    body_bottom, body_top, body_r, _, _, _ = _sprayer_geom(r)
    body = LatheGeometry(
        [
            (0.0, body_bottom),
            (body_r, body_bottom),
            (body_r, body_bottom + 0.004),
            (body_r, body_top - 0.006),
            (body_r - 0.003, body_top - 0.002),
            (body_r - 0.005, body_top),
            (0.0, body_top + 0.002),
        ],
        segments=40,
    )
    geo = body
    # stem reaches down through the collar bore.
    stem = CylinderGeometry(0.0080, 0.034, radial_segments=20)
    stem.translate(0.0, 0.0, body_bottom - 0.017)
    geo = geo.merge(stem)
    # pivot bosses (inline visuals on the body, not separate parts).
    _, _, _, _, pivot_z, pivot_x = _sprayer_geom(r)
    length = pivot_x - body_r + 0.006
    center_x = (body_r + pivot_x) / 2.0
    for y_sign in (-1.0, 1.0):
        bracket = BoxGeometry((length, 0.006, 0.010))
        bracket.translate(center_x, y_sign * 0.007, pivot_z)
        geo = geo.merge(bracket)
    return mesh_from_geometry(geo, "sprayer_body")


def _nozzle_mesh(r: ResolvedContainerPumpConfig):
    _, _, body_r, nozzle_exit_z, _, _ = _sprayer_geom(r)
    reach = r.spout_reach_scale
    nozzle_pts = [
        (body_r - 0.002, 0.0, nozzle_exit_z),
        (body_r + 0.008 * reach, 0.0, nozzle_exit_z - 0.001),
        (body_r + 0.022 * reach, 0.0, nozzle_exit_z - 0.003),
        (body_r + 0.036 * reach, 0.0, nozzle_exit_z - 0.005),
        (body_r + 0.046 * reach, 0.0, nozzle_exit_z - 0.006),
    ]
    geo = tube_from_spline_points(nozzle_pts, radius=0.0045, samples_per_segment=14, radial_segments=14)
    tip = CylinderGeometry(0.0055, 0.005, radial_segments=16)
    tip.translate(body_r + 0.048 * reach, 0.0, nozzle_exit_z - 0.006)
    geo = geo.merge(tip)
    return mesh_from_geometry(geo, "nozzle")


def _trigger_lever_mesh(r: ResolvedContainerPumpConfig):
    lever = BoxGeometry((0.006, 0.013, 0.024))
    lever.translate(0.0, 0.0, -0.015)
    geo = lever
    pad = BoxGeometry((0.008, 0.015, 0.006))
    pad.translate(0.001, 0.0, -0.028)
    geo = geo.merge(pad)
    pin = CylinderGeometry(0.003, 0.018, radial_segments=12)
    pin.rotate_x(math.pi / 2.0)
    geo = geo.merge(pin)
    return mesh_from_geometry(geo, "trigger_lever")


# Disc-top cap: cap_base (bore + side slot, CadQuery) + disc tile + grip nubs.
def _disc_geom(r: ResolvedContainerPumpConfig):
    cap_h = 0.012
    cap_base_bottom = r.collar_top
    cap_base_top = cap_base_bottom + cap_h
    cap_base_r = r.collar_r
    cap_bore_r = max(r.bore_r + 0.002, 0.012)
    disc_r = cap_bore_r + 0.0003
    disc_h = 0.004
    disc_rest_bottom = cap_base_top - disc_h
    return cap_h, cap_base_bottom, cap_base_top, cap_base_r, cap_bore_r, disc_r, disc_h, disc_rest_bottom


def _cap_base_mesh(r: ResolvedContainerPumpConfig):
    cap_h, cap_base_bottom, _, cap_base_r, cap_bore_r, _, disc_h, _ = _disc_geom(r)
    cap_bore_depth = cap_h - 0.002
    slot_w = 0.010
    cap = cq.Workplane("XY").cylinder(cap_h, cap_base_r)
    cap = cap.faces(">Z").workplane().circle(cap_bore_r).cutBlind(-cap_bore_depth)
    slot_z = cap_h / 2.0 - disc_h / 2.0
    slot_x = (cap_bore_r + cap_base_r) / 2.0
    slot_radial_w = (cap_base_r - cap_bore_r) + 0.004
    slot_cutter = cq.Workplane("XY").box(slot_radial_w, slot_w, disc_h).translate((slot_x, 0.0, slot_z))
    cap = cap.cut(slot_cutter)
    cap = cap.translate((0.0, 0.0, cap_base_bottom + cap_h / 2.0))
    return mesh_from_cadquery(cap, "cap_base_shell")


def _slot_marker_mesh(r: ResolvedContainerPumpConfig):
    _, _, _, cap_base_r, _, _, disc_h, disc_rest_bottom = _disc_geom(r)
    slot_w = 0.010
    pad_w = slot_w + 0.004
    pad_h = disc_h + 0.004
    pad_d = 0.0015
    geo = BoxGeometry((pad_d, pad_w, pad_h))
    geo.translate(cap_base_r + pad_d / 2.0, 0.0, disc_rest_bottom + disc_h / 2.0)
    return mesh_from_geometry(geo, "slot_marker")


def _disc_tile_mesh(r: ResolvedContainerPumpConfig):
    *_, disc_r, disc_h, _ = _disc_geom(r)
    geo = CylinderGeometry(disc_r, disc_h, radial_segments=36)
    geo.translate(0.0, 0.0, disc_h / 2.0)
    return mesh_from_geometry(geo, "disc_tile")


def _grip_nub_mesh(r: ResolvedContainerPumpConfig, index: int):
    *_, disc_r, disc_h, _ = _disc_geom(r)
    nub_r = 0.0015
    nub_h = 0.001
    orbit = disc_r * 0.6
    ang = 2.0 * math.pi * index / 4
    geo = CylinderGeometry(nub_r, nub_h, radial_segments=8)
    geo.translate(orbit * math.cos(ang), orbit * math.sin(ang), disc_h + nub_h / 2.0)
    return mesh_from_geometry(geo, f"grip_nub_{index}")


# Dip tube (pump / sprayer heads only). Hangs from the head down to near the
# bottle bottom; the foaming pump uses a shorter tube.
def _dip_tube_mesh(r: ResolvedContainerPumpConfig):
    if r.dispenser_head == "foaming_pump":
        _, f_bottom, _ = _foamer_geom(r)
        tube_top = f_bottom - 0.040
        tube_h = 0.100
        tube = CylinderGeometry(0.003, tube_h, radial_segments=12)
        tube.translate(0.0, 0.0, tube_top - tube_h / 2.0)
        return mesh_from_geometry(tube, "dip_tube")
    # press / gooseneck / twist / trigger: long tube to near the bottle bottom.
    tube_h = max(r.body_top + 0.018, 0.090)
    tube = CylinderGeometry(0.0028, tube_h, radial_segments=12)
    tube.translate(0.0, 0.0, 0.008 + tube_h / 2.0)
    return mesh_from_geometry(tube, "dip_tube")


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def _rv(part, mesh, *, material, name, rebase: float):
    """Add a world-z-authored visual to a child part whose link origin sits at
    world z=``rebase``. The visual origin shifts the geometry down by ``rebase``
    so the child link AABB contains its own local z=0 (the joint origin) — this
    is what keeps the baseline articulation-origin check happy while the part
    still renders at the intended world z."""
    return part.visual(mesh, material=material, name=name, material_class_id="plastic.opaque_glossy_molded", origin=Origin(xyz=(0.0, 0.0, -rebase)))


def build_container_pump(
    config: ContainerPumpConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name)
    if assets is not None:
        model.assets = assets

    pal = PALETTES[r.palette_style]
    bottle_mat = model.material(f"cp_bottle_{r.palette_style}", rgba=pal.bottle)
    head_mat = model.material(f"cp_head_{r.palette_style}", rgba=pal.head)
    accent_mat = model.material(f"cp_accent_{r.palette_style}", rgba=pal.accent)
    tube_mat = model.material(f"cp_tube_{r.palette_style}", rgba=pal.tube)
    label_mat = model.material(f"cp_label_{r.palette_style}", rgba=pal.label)

    # --- ROOT: bottle body (Slot A) -----------------------------------------
    bottle = model.part("bottle")
    bottle.visual(_bottle_mesh(r), material=bottle_mat, name="bottle_shell", material_class_id=("plastic.opaque_generic" if r.palette_style in {"clear_white_pump", "amber_natural", "frosted_sage", "cobalt_clinical", "matte_charcoal", "pearl_blush", "chrome_apothecary", "soft_touch_olive"} else "ceramic.porcelain_glazed_plain"))
    bottle.visual(
        _label_mesh(r),
        material=label_mat,
        name="label_band",
        appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    bottle.visual(_neck_threads_mesh(r), material=bottle_mat, name="neck_threads", material_class_id=("plastic.opaque_generic" if r.palette_style in {"clear_white_pump", "amber_natural", "frosted_sage", "cobalt_clinical", "matte_charcoal", "pearl_blush", "chrome_apothecary", "soft_touch_olive"} else "ceramic.porcelain_glazed_plain"))
    bottle.inertial = Inertial.from_geometry(
        Cylinder(max(r.body_r, r.body_r), r.body_top),
        mass=0.20,
        origin=Origin(xyz=(0.0, 0.0, r.body_top / 2.0)),
    )

    # --- Shared collar (FIXED on the neck) ----------------------------------
    # Collar link origin at world z=collar_bottom; visuals rebased so the FIXED
    # joint origin lands inside both the bottle and the collar AABB.
    collar_mount = _collar_mount_z(r)
    collar = model.part("collar")
    _rv(collar, _collar_mesh(r), material=head_mat, name="collar_shell", rebase=collar_mount)
    _rv(collar, _collar_knurl_mesh(r), material=head_mat, name="collar_knurl", rebase=collar_mount)
    collar.inertial = Inertial.from_geometry(
        Cylinder(r.collar_r, r.collar_top - r.collar_bottom),
        mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, (r.collar_bottom + r.collar_top) / 2.0 - collar_mount)),
    )
    model.articulation(
        "bottle_to_collar",
        ArticulationType.FIXED,
        parent=bottle,
        child=collar,
        origin=Origin(xyz=(0.0, 0.0, collar_mount)),
    )

    head = r.dispenser_head
    if head in ("press_pump", "foaming_pump", "gooseneck_pump"):
        _build_carrier_pump(model, r, collar, head_mat, accent_mat, tube_mat)
    elif head == "twist_lock_pump":
        _build_twist_lock(model, r, collar, head_mat, accent_mat, tube_mat)
    elif head == "trigger_sprayer":
        _build_trigger_sprayer(model, r, collar, head_mat, accent_mat, tube_mat)
    elif head == "flip_top_cap":
        _build_flip_top_cap(model, r, collar, head_mat)
    else:  # disc_top_cap
        _build_disc_top_cap(model, r, collar, head_mat, accent_mat)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def _build_carrier_pump(model, r, collar, head_mat, accent_mat, tube_mat):
    # massless head_carrier swivels (REVOLUTE +Z), head presses (PRISMATIC +Z).
    # All head-stack parts share a local origin at world z=collar_top (mount).
    mount = _head_mount_z(r)
    collar_mount = _collar_mount_z(r)
    carrier = model.part("head_carrier")
    _rv(carrier, _carrier_hub_mesh(r), material=head_mat, name="carrier_hub", rebase=mount)
    carrier.inertial = Inertial.from_geometry(
        Cylinder(r.collar_r, 0.004),
        mass=0.001,
        origin=Origin(xyz=(0.0, 0.0, r.collar_top + 0.002 - mount)),
    )
    # Swivel origin (collar-local) on the collar-top rim.
    model.articulation(
        "pump_swivel",
        ArticulationType.REVOLUTE,
        parent=collar,
        child=carrier,
        origin=Origin(xyz=(0.0, 0.0, mount - collar_mount)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=2.0, lower=-math.pi, upper=math.pi),
    )

    if r.dispenser_head == "foaming_pump":
        head = model.part("foamer_head")
        _rv(head, _foamer_chamber_mesh(r), material=head_mat, name="foamer_chamber", rebase=mount)
        _rv(head, _chamber_grip_mesh(r), material=accent_mat, name="chamber_grip", rebase=mount)
        _rv(head, _actuator_mesh(r), material=head_mat, name="actuator_cap", rebase=mount)
        _rv(head, _foamer_spout_mesh(r), material=head_mat, name="foamer_spout", rebase=mount)
        _rv(head, _foamer_stem_mesh(r), material=head_mat, name="foamer_stem", rebase=mount)
        _rv(head, _dip_tube_mesh(r), material=tube_mat, name="dip_tube", rebase=mount)
        _, f_bottom, f_top = _foamer_geom(r)
        head.inertial = Inertial.from_geometry(
            Cylinder(0.020, f_top - f_bottom + 0.007),
            mass=0.04,
            origin=Origin(xyz=(0.0, 0.0, (f_bottom + f_top) / 2.0 - mount)),
        )
    else:
        head = model.part("head")
        if r.dispenser_head == "gooseneck_pump":
            _rv(head, _gooseneck_head_mesh(r), material=head_mat, name="head_shell", rebase=mount)
            head.inertial = Inertial.from_geometry(
                Box((0.100, 0.030, 0.130)),
                mass=0.035,
                origin=Origin(xyz=(0.040, 0.0, r.collar_top + 0.064 - mount)),
            )
        else:
            _rv(head, _press_head_mesh(r), material=head_mat, name="head_shell", rebase=mount)
            head.inertial = Inertial.from_geometry(
                Box((0.085, 0.030, 0.060)),
                mass=0.03,
                origin=Origin(xyz=(0.015, 0.0, r.collar_top + 0.014 - mount)),
            )
        _rv(head, _dip_tube_mesh(r), material=tube_mat, name="dip_tube", rebase=mount)

    # Press origin: both carrier and head share the same mount, so 0 in the
    # carrier-local frame (the press axis is +Z; rest pose q=0).
    model.articulation(
        "pump_press",
        ArticulationType.PRISMATIC,
        parent=carrier,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.1, lower=-r.press_travel, upper=0.0),
    )


def _build_twist_lock(model, r, collar, head_mat, accent_mat, tube_mat):
    # solid lock_ring twists (REVOLUTE +Z limited 0..π/2), head presses on it.
    # The lock_ring sits ABOVE the collar, so its local origin is set to its own
    # mid-height (not the collar mid-band) — that keeps the twist origin inside
    # both the collar throat and the lock_ring AABB. The head shares this mount.
    ring_h, z_bot, _, ring_outer_r, _ = _lock_ring_geom(r)
    mount = z_bot + ring_h / 2.0
    collar_mount = _collar_mount_z(r)
    lock_ring = model.part("lock_ring")
    _rv(lock_ring, _lock_ring_mesh(r), material=accent_mat, name="lock_ring_shell", rebase=mount)
    lock_ring.inertial = Inertial.from_geometry(
        Cylinder(ring_outer_r, ring_h),
        mass=0.008,
        origin=Origin(xyz=(0.0, 0.0, z_bot + ring_h / 2.0 - mount)),
    )
    model.articulation(
        "twist_lock",
        ArticulationType.REVOLUTE,
        parent=collar,
        child=lock_ring,
        origin=Origin(xyz=(0.0, 0.0, mount - collar_mount)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=math.pi / 2.0),
    )

    head = model.part("head")
    _rv(head, _twist_head_mesh(r), material=head_mat, name="head_shell", rebase=mount)
    _rv(head, _dip_tube_mesh(r), material=tube_mat, name="dip_tube", rebase=mount)
    head.inertial = Inertial.from_geometry(
        Box((0.085, 0.030, 0.060)),
        mass=0.03,
        origin=Origin(xyz=(0.015, 0.0, r.collar_top + 0.014 - mount)),
    )
    model.articulation(
        "pump_press",
        ArticulationType.PRISMATIC,
        parent=lock_ring,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.1, lower=-r.press_travel, upper=0.0),
    )


def _build_trigger_sprayer(model, r, collar, head_mat, accent_mat, tube_mat):
    # whole sprayer_head swivels (REVOLUTE +Z); finger trigger squeezes (REV -Y).
    mount = _head_mount_z(r)
    collar_mount = _collar_mount_z(r)
    sprayer_head = model.part("sprayer_head")
    _rv(sprayer_head, _sprayer_body_mesh(r), material=head_mat, name="sprayer_body", rebase=mount)
    _rv(sprayer_head, _nozzle_mesh(r), material=head_mat, name="nozzle", rebase=mount)
    _rv(sprayer_head, _dip_tube_mesh(r), material=tube_mat, name="dip_tube", rebase=mount)
    sprayer_head.inertial = Inertial.from_geometry(
        Box((0.080, 0.030, 0.050)),
        mass=0.04,
        origin=Origin(xyz=(0.015, 0.0, r.collar_top + 0.020 - mount)),
    )
    model.articulation(
        "sprayer_swivel",
        ArticulationType.REVOLUTE,
        parent=collar,
        child=sprayer_head,
        origin=Origin(xyz=(0.0, 0.0, mount - collar_mount)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=2.0, lower=-math.pi, upper=math.pi),
    )

    # The trigger lever is authored in its own pivot-local frame (pivot at 0),
    # so it needs no rebase; the joint origin is in the sprayer_head-local frame.
    trigger = model.part("trigger")
    trigger.visual(_trigger_lever_mesh(r), material=accent_mat, name="trigger_lever", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"clear_white_pump", "amber_natural", "frosted_sage", "cobalt_clinical", "matte_charcoal", "pearl_blush", "ceramic_ivory", "soft_touch_olive"} else "metal.chrome_polished"))
    trigger.inertial = Inertial.from_geometry(
        Box((0.010, 0.016, 0.034)),
        mass=0.008,
        origin=Origin(xyz=(0.0, 0.0, -0.016)),
    )
    _, _, _, _, pivot_z, pivot_x = _sprayer_geom(r)
    model.articulation(
        "trigger_squeeze",
        ArticulationType.REVOLUTE,
        parent=sprayer_head,
        child=trigger,
        origin=Origin(xyz=(pivot_x, 0.0, pivot_z - mount)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=4.0, lower=0.0, upper=0.55),
    )


def _build_flip_top_cap(model, r, collar, head_mat):
    # hinged flip_cap opens about cap_hinge REVOLUTE -X (no pump / no dip tube).
    # The cap mesh is already authored in the hinge-local frame (z relative to
    # hinge_z), so it needs no rebase; the joint origin is collar-local.
    collar_mount = _collar_mount_z(r)
    _, hinge_y, hinge_z = _flip_params(r)
    flip_cap = model.part("flip_cap")
    flip_cap.visual(_flip_cap_mesh(r), material=head_mat, name="cap_disc", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"clear_white_pump", "amber_natural", "frosted_sage", "cobalt_clinical", "matte_charcoal", "pearl_blush", "chrome_apothecary", "soft_touch_olive"} else "ceramic.porcelain_glazed_plain"))
    cap_radius = r.bore_r + 0.0023
    flip_cap.inertial = Inertial.from_geometry(
        Cylinder(cap_radius, 0.003),
        mass=0.008,
        origin=Origin(xyz=(0.0, -hinge_y, 0.003 / 2.0)),
    )
    model.articulation(
        "cap_hinge",
        ArticulationType.REVOLUTE,
        parent=collar,
        child=flip_cap,
        origin=Origin(xyz=(0.0, hinge_y, hinge_z - collar_mount)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=0.0, upper=2.4),
    )


def _build_disc_top_cap(model, r, collar, head_mat, accent_mat):
    # FIXED cap_base (bore + side slot) carries a disc that pushes down (PRIS +Z).
    # The cap_base sits ABOVE the collar; its local origin is its own mid-height
    # so the FIXED joint origin lands inside both the collar throat and the
    # cap_base AABB.
    collar_mount = _collar_mount_z(r)
    cap_h, cap_base_bottom, cap_base_top, cap_base_r, _, _, disc_h, disc_rest_bottom = _disc_geom(r)
    mount = cap_base_bottom + cap_h / 2.0
    cap_base = model.part("cap_base")
    _rv(cap_base, _cap_base_mesh(r), material=head_mat, name="cap_base_shell", rebase=mount)
    _rv(cap_base, _slot_marker_mesh(r), material=accent_mat, name="slot_marker", rebase=mount)
    cap_base.inertial = Inertial.from_geometry(
        Cylinder(cap_base_r, cap_h),
        mass=0.012,
        origin=Origin(xyz=(0.0, 0.0, cap_base_bottom + cap_h / 2.0 - mount)),
    )
    model.articulation(
        "collar_to_cap_base",
        ArticulationType.FIXED,
        parent=collar,
        child=cap_base,
        origin=Origin(xyz=(0.0, 0.0, mount - collar_mount)),
    )

    # The disc tile is authored in its own local frame (z=0 at the disc bottom),
    # so it needs no rebase; the PRISMATIC origin is in the cap_base-local frame.
    disc = model.part("disc")
    disc.visual(_disc_tile_mesh(r), material=accent_mat, name="disc_tile", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"clear_white_pump", "amber_natural", "frosted_sage", "cobalt_clinical", "matte_charcoal", "pearl_blush", "ceramic_ivory", "soft_touch_olive"} else "metal.chrome_polished"))
    for i in range(4):
        disc.visual(_grip_nub_mesh(r, i), material=accent_mat, name=f"grip_nub_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"clear_white_pump", "amber_natural", "frosted_sage", "cobalt_clinical", "matte_charcoal", "pearl_blush", "ceramic_ivory", "soft_touch_olive"} else "metal.chrome_polished"))
    disc.inertial = Inertial.from_geometry(
        Cylinder(0.013, disc_h),
        mass=0.005,
        origin=Origin(xyz=(0.0, 0.0, disc_h / 2.0)),
    )
    model.articulation(
        "cap_to_disc",
        ArticulationType.PRISMATIC,
        parent=cap_base,
        child=disc,
        origin=Origin(xyz=(0.0, 0.0, disc_rest_bottom - mount)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.05, lower=-0.004, upper=0.0),
    )


def build_seeded_container_pump(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_pump(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (collar over neck, head stem in collar bore,
# dip tube inside the bottle, carrier hub in the collar, lock ring on collar,
# disc in cap_base bore, cap tab in collar lugs) are element-scoped so the
# sweep's island / overlap checks pass; the pump / twist / squeeze / flip / disc
# actions are exercised. Transparency is asserted per-colorway.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_pump_tests(
    object_model: ArticulatedObject,
    config: ContainerPumpConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    bottle = object_model.get_part("bottle")
    collar = object_model.get_part("collar")

    # ---- shared captured-fit overlaps (collar over neck) ----
    ctx.allow_overlap(
        collar, bottle, elem_a="collar_shell", elem_b="neck_threads",
        reason="The collar is threaded over the bottle neck; threads engage inside.",
    )
    ctx.allow_overlap(
        collar, bottle, elem_a="collar_shell", elem_b="bottle_shell",
        reason="The collar skirt wraps over the bottle neck wall.",
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
        bext[0] > 0.02 and bext[1] > 0.02 and bext[2] > 0.05,
        details=f"bottle extents={bext}",
    )

    # ---- per-colorway transparency assertion ----
    shell_rgba = bottle.get_visual("bottle_shell").material.rgba
    if r.transparent_body:
        ctx.check(
            "transparent colorway: bottle is translucent (alpha < 1)",
            shell_rgba is not None and shell_rgba[3] < 1.0,
            details=f"bottle_shell rgba={shell_rgba}",
        )
    else:
        ctx.check(
            "opaque colorway: bottle shell is fully opaque",
            shell_rgba is not None and shell_rgba[3] >= 0.99,
            details=f"bottle_shell rgba={shell_rgba}",
        )

    # ---- collar seated on the neck ----
    ctx.expect_overlap(collar, bottle, axes="z", min_overlap=0.005, name="collar seated over the neck")

    # ---- body-profile identity assertions ----
    shell_aabb = ctx.part_element_world_aabb(bottle, elem="bottle_shell")
    if shell_aabb is not None:
        dx = shell_aabb[1][0] - shell_aabb[0][0]
        dy = shell_aabb[1][1] - shell_aabb[0][1]
        if r.body_profile == "boxy_oval":
            ctx.check(
                "boxy_oval body is wider in X than Y",
                dx > dy + 0.010,
                details=f"dx={dx:.4f}, dy={dy:.4f}",
            )
        elif r.body_profile == "tall_rectangular":
            ctx.check(
                "tall_rectangular body is a wide slab (X > Y)",
                dx > dy + 0.010,
                details=f"dx={dx:.4f}, dy={dy:.4f}",
            )
        elif r.body_profile == "tapered_waisted":
            ctx.check(
                "tapered_waisted body widest point exceeds round base radius",
                dx > 2 * r.body_r + 0.004,
                details=f"dx={dx:.4f}, base diameter≈{2*r.body_r*1.2:.4f}",
            )

    # ---- per-head mechanism assertions ----
    head_name = r.dispenser_head
    if head_name in ("press_pump", "foaming_pump", "gooseneck_pump"):
        _check_carrier_pump(ctx, object_model, r, collar, bottle)
    elif head_name == "twist_lock_pump":
        _check_twist_lock(ctx, object_model, r, collar, bottle)
    elif head_name == "trigger_sprayer":
        _check_trigger_sprayer(ctx, object_model, r, collar, bottle)
    elif head_name == "flip_top_cap":
        _check_flip_top_cap(ctx, object_model, r, collar)
    else:
        _check_disc_top_cap(ctx, object_model, r, collar)

    # ---- at least one non-fixed mechanism joint exists ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed mechanism joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()


def _check_carrier_pump(ctx, model, r, collar, bottle):
    carrier = model.get_part("head_carrier")
    head = model.get_part("foamer_head" if r.dispenser_head == "foaming_pump" else "head")
    stem_elem = "foamer_stem" if r.dispenser_head == "foaming_pump" else "head_shell"

    ctx.allow_overlap(carrier, collar, elem_a="carrier_hub", elem_b="collar_shell",
                      reason="The swivel hub sits in the collar throat.")
    ctx.allow_overlap(head, collar, elem_a=stem_elem, elem_b="collar_shell",
                      reason="The pump stem passes down through the collar bore.")
    ctx.allow_overlap(head, carrier, elem_a=stem_elem, elem_b="carrier_hub",
                      reason="The stem passes through the carrier hub it mounts on.")
    ctx.allow_overlap(head, bottle, elem_a=stem_elem, elem_b="bottle_shell",
                      reason="The actuating stem reaches into the bottle neck.")
    ctx.allow_overlap(head, bottle, elem_a="dip_tube", elem_b="bottle_shell",
                      reason="The dip tube hangs inside the bottle.")

    swivel = model.get_articulation("pump_swivel")
    press = model.get_articulation("pump_press")
    ctx.check(
        "pump_swivel is REVOLUTE about +Z",
        swivel.articulation_type == ArticulationType.REVOLUTE and abs(swivel.axis[2]) > 0.99,
        details=f"axis={swivel.axis}, type={swivel.articulation_type}",
    )
    ctx.check(
        "pump_press is PRISMATIC about +Z",
        press.articulation_type == ArticulationType.PRISMATIC and abs(press.axis[2]) > 0.99,
        details=f"axis={press.axis}, type={press.articulation_type}",
    )
    # massless carrier
    ctx.check(
        "head_carrier is massless (carrier link decouples swivel/press)",
        carrier.inertial is not None and carrier.inertial.mass <= 0.0015,
        details=f"carrier mass={carrier.inertial.mass if carrier.inertial else None}",
    )
    # press action
    rest = ctx.part_world_position(head)
    with ctx.pose({press: -r.press_travel}):
        pressed = ctx.part_world_position(head)
    ctx.check(
        "pump head presses straight down",
        pressed[2] < rest[2] - r.press_travel * 0.5,
        details=f"rest_z={rest[2]:.4f}, pressed_z={pressed[2]:.4f}",
    )
    # swivel action
    ext0 = _ext(ctx.part_world_aabb(head))
    with ctx.pose({swivel: math.pi / 2.0}):
        ext90 = _ext(ctx.part_world_aabb(head))
    ctx.check(
        "spout/head points along +X at rest, swivels about +Z",
        ext0[0] > ext0[1] + 0.008 and ext90[1] > ext90[0] + 0.008,
        details=f"rest={ext0}, q90={ext90}",
    )
    # spout off-axis
    spout_elem = "foamer_spout" if r.dispenser_head == "foaming_pump" else "head_shell"
    spout_aabb = ctx.part_element_world_aabb(head, elem=spout_elem)
    ctx.check(
        "spout/nozzle extends off the vertical axis (+X)",
        spout_aabb is not None and spout_aabb[1][0] > 0.030,
        details=f"spout max_x={spout_aabb[1][0] if spout_aabb else None}",
    )
    ctx.expect_contact(carrier, collar, name="swivel carrier seated on collar")
    # dip tube depth: long for press/gooseneck, short for foaming
    tube_aabb = ctx.part_element_world_aabb(head, elem="dip_tube")
    if r.dispenser_head == "foaming_pump":
        ctx.check(
            "foaming dip tube is short (does not reach bottle bottom)",
            tube_aabb is not None and tube_aabb[0][2] > 0.030,
            details=f"dip min z={tube_aabb[0][2] if tube_aabb else None}",
        )
    else:
        ctx.check(
            "dip tube reaches near the bottle bottom",
            tube_aabb is not None and tube_aabb[0][2] < 0.025,
            details=f"dip min z={tube_aabb[0][2] if tube_aabb else None}",
        )


def _check_twist_lock(ctx, model, r, collar, bottle):
    lock_ring = model.get_part("lock_ring")
    head = model.get_part("head")
    ctx.allow_overlap(lock_ring, collar, elem_a="lock_ring_shell", elem_b="collar_shell",
                      reason="The twist-lock ring sits in the collar throat.")
    ctx.allow_overlap(head, lock_ring, elem_a="head_shell", elem_b="lock_ring_shell",
                      reason="The stem with cam pins passes through the lock ring bore.")
    ctx.allow_overlap(head, collar, elem_a="head_shell", elem_b="collar_shell",
                      reason="The pump stem passes down through the collar bore.")
    ctx.allow_overlap(head, bottle, elem_a="head_shell", elem_b="bottle_shell",
                      reason="The actuating stem reaches into the bottle neck.")
    ctx.allow_overlap(head, bottle, elem_a="dip_tube", elem_b="bottle_shell",
                      reason="The dip tube hangs inside the bottle.")

    twist = model.get_articulation("twist_lock")
    press = model.get_articulation("pump_press")
    ctx.check(
        "twist_lock is REVOLUTE +Z, limited to a quarter turn",
        twist.articulation_type == ArticulationType.REVOLUTE
        and abs(twist.axis[2]) > 0.99
        and twist.motion_limits is not None
        and twist.motion_limits.upper is not None
        and twist.motion_limits.upper - twist.motion_limits.lower <= math.pi / 2.0 + 0.01,
        details=f"axis={twist.axis}, limits={twist.motion_limits}",
    )
    ctx.check(
        "pump_press is PRISMATIC about +Z (parent=lock_ring)",
        press.articulation_type == ArticulationType.PRISMATIC and abs(press.axis[2]) > 0.99,
        details=f"axis={press.axis}",
    )
    rest = ctx.part_world_position(head)
    with ctx.pose({press: -r.press_travel}):
        pressed = ctx.part_world_position(head)
    ctx.check(
        "pump head presses straight down when unlocked",
        pressed[2] < rest[2] - r.press_travel * 0.5,
        details=f"rest_z={rest[2]:.4f}, pressed_z={pressed[2]:.4f}",
    )
    ext0 = _ext(ctx.part_world_aabb(head))
    with ctx.pose({twist: math.pi / 2.0}):
        ext_locked = _ext(ctx.part_world_aabb(head))
    ctx.check(
        "twist quarter-turn rotates the spout heading about +Z",
        ext0[0] > ext0[1] + 0.008 and ext_locked[1] > ext_locked[0] + 0.008,
        details=f"unlocked={ext0}, locked={ext_locked}",
    )
    ctx.expect_contact(lock_ring, collar, name="lock ring seated on collar")


def _check_trigger_sprayer(ctx, model, r, collar, bottle):
    sprayer_head = model.get_part("sprayer_head")
    trigger = model.get_part("trigger")
    ctx.allow_overlap(sprayer_head, collar, elem_a="sprayer_body", elem_b="collar_shell",
                      reason="The sprayer body base sits in the collar throat.")
    ctx.allow_overlap(sprayer_head, bottle, elem_a="sprayer_body", elem_b="bottle_shell",
                      reason="The stem reaches into the bottle neck.")
    ctx.allow_overlap(sprayer_head, bottle, elem_a="dip_tube", elem_b="bottle_shell",
                      reason="The dip tube hangs inside the bottle.")

    swivel = model.get_articulation("sprayer_swivel")
    squeeze = model.get_articulation("trigger_squeeze")
    ctx.check(
        "sprayer_swivel is REVOLUTE about +Z",
        swivel.articulation_type == ArticulationType.REVOLUTE and abs(swivel.axis[2]) > 0.99,
        details=f"axis={swivel.axis}",
    )
    ctx.check(
        "trigger_squeeze is REVOLUTE about -Y",
        squeeze.articulation_type == ArticulationType.REVOLUTE and abs(squeeze.axis[1]) > 0.99,
        details=f"axis={squeeze.axis}",
    )
    nozzle_aabb = ctx.part_element_world_aabb(sprayer_head, elem="nozzle")
    ctx.check(
        "nozzle extends off the vertical axis (+X)",
        nozzle_aabb is not None and nozzle_aabb[1][0] > 0.040,
        details=f"nozzle max_x={nozzle_aabb[1][0] if nozzle_aabb else None}",
    )
    rest_aabb = ctx.part_world_aabb(trigger)
    with ctx.pose({squeeze: 0.55}):
        squeezed_aabb = ctx.part_world_aabb(trigger)
    ctx.check(
        "trigger squeeze swings the lever forward (+X)",
        squeezed_aabb[1][0] > rest_aabb[1][0] + 0.004,
        details=f"rest_max_x={rest_aabb[1][0]:.4f}, squeezed_max_x={squeezed_aabb[1][0]:.4f}",
    )
    ext0 = _ext(ctx.part_world_aabb(sprayer_head))
    with ctx.pose({swivel: math.pi / 2.0}):
        ext90 = _ext(ctx.part_world_aabb(sprayer_head))
    ctx.check(
        "sprayer head swivels about +Z",
        ext0[0] > ext0[1] + 0.008 and ext90[1] > ext90[0] + 0.008,
        details=f"rest={ext0}, q90={ext90}",
    )
    ctx.expect_contact(sprayer_head, collar, name="sprayer head seated on collar")


def _check_flip_top_cap(ctx, model, r, collar):
    flip_cap = model.get_part("flip_cap")
    ctx.allow_overlap(flip_cap, collar, elem_a="cap_disc", elem_b="collar_shell",
                      reason="The cap hinge tab nests between the collar lugs at the rim.")
    hinge = model.get_articulation("cap_hinge")
    ctx.check(
        "cap_hinge is REVOLUTE about -X",
        hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[0]) > 0.99,
        details=f"axis={hinge.axis}, type={hinge.articulation_type}",
    )
    # no dip tube / no carrier for flip
    ctx.check(
        "flip_top_cap has no pump carrier or dip tube",
        "head_carrier" not in [p.name for p in model.parts]
        and not any("dip_tube" == v.name for v in flip_cap.visuals),
        details=f"parts={[p.name for p in model.parts]}",
    )
    rest_aabb = ctx.part_world_aabb(flip_cap)
    with ctx.pose({hinge: 1.5}):
        open_aabb = ctx.part_world_aabb(flip_cap)
    ctx.check(
        "flip cap opens upward (hinge raises the cap)",
        open_aabb[1][2] > rest_aabb[1][2] + 0.010,
        details=f"rest_max_z={rest_aabb[1][2]:.4f}, open_max_z={open_aabb[1][2]:.4f}",
    )
    with ctx.pose({hinge: 0.0}):
        ctx.expect_contact(flip_cap, collar, elem_a="cap_disc", elem_b="collar_shell",
                           name="closed cap seats on collar top")


def _check_disc_top_cap(ctx, model, r, collar):
    cap_base = model.get_part("cap_base")
    disc = model.get_part("disc")
    ctx.allow_overlap(cap_base, collar, elem_a="cap_base_shell", elem_b="collar_shell",
                      reason="The cap base sits on the collar top rim seating surface.")
    ctx.allow_overlap(disc, cap_base, elem_a="disc_tile", elem_b="cap_base_shell",
                      reason="The disc tile is a press-fit inside the cap base bore.")
    for i in range(4):
        ctx.allow_overlap(disc, cap_base, elem_a=f"grip_nub_{i}", elem_b="cap_base_shell",
                          reason=f"Grip nub {i} sits near the bore edge.")

    base_join = model.get_articulation("collar_to_cap_base")
    push = model.get_articulation("cap_to_disc")
    ctx.check(
        "collar_to_cap_base is FIXED",
        base_join.articulation_type == ArticulationType.FIXED,
        details=f"type={base_join.articulation_type}",
    )
    ctx.check(
        "cap_to_disc is PRISMATIC about +Z",
        push.articulation_type == ArticulationType.PRISMATIC and abs(push.axis[2]) > 0.99,
        details=f"axis={push.axis}, type={push.articulation_type}",
    )
    ctx.check(
        "disc_top_cap has no pump carrier or dip tube",
        "head_carrier" not in [p.name for p in model.parts]
        and not any("dip_tube" == v.name for v in disc.visuals),
        details=f"parts={[p.name for p in model.parts]}",
    )
    marker_aabb = ctx.part_element_world_aabb(cap_base, elem="slot_marker")
    ctx.check(
        "dispensing slot marker extends off-axis on +X",
        marker_aabb is not None and marker_aabb[1][0] > r.collar_r,
        details=f"slot_marker max_x={marker_aabb[1][0] if marker_aabb else None}",
    )
    rest = ctx.part_world_position(disc)
    with ctx.pose({push: -0.004}):
        pressed = ctx.part_world_position(disc)
    ctx.check(
        "disc depresses downward when pushed",
        pressed[2] < rest[2] - 0.002,
        details=f"rest_z={rest[2]:.4f}, pressed_z={pressed[2]:.4f}",
    )
