# SPDX-License-Identifier: Apache-2.0

"""Handheld marker / highlighter pen modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Stationary_Pen.md`` and the
``picture/Stationary/Pen`` 5-star sample pool (1 parent + 9 single-axis fork
variants: bullet_tip / twin_tip / twist_extend / click_retract / twist_cap /
round_barrel / flip_cap / sprung_clip / grip_section).

Structure (pattern = ``mixed``): a single root ``barrel`` (a slender rod whose
long axis is +X) carries a set of children plus a grip-rib multiplicity axis:

  * ``barrel_profile`` (2): rounded-rectangular highlighter prism, or round
    cylindrical marker. footprint of barrel + collar + cap vary together.
    (parent S0 vs round_barrel S6)
  * ``tip_form`` (2): flat black chisel wedge nib, or a revolved bullet cone
    nib. inlined as a visual on the barrel (cap actuation) or on the sliding
    carrier (click / twist-extend). (parent S0 vs bullet_tip S1)
  * ``actuation`` (6): the core writing-tip mechanism — pull-off friction cap
    (PRISMATIC +X), twin dual-ended pull-off caps (2 PRISMATIC), click-retract
    carrier (PRISMATIC +X inside the bore), twist-extend (REVOLUTE +X collar +
    PRISMATIC +X nib carrier), screw twist-cap (REVOLUTE +X), or tethered flip
    cap (REVOLUTE about a transverse -Y hinge). This is the main topology axis.
  * ``pocket_clip`` (3): fixed flat clip (inline visual), sprung pivoting clip
    (REVOLUTE +Y on the cap), or none. sprung requires a separate cap part.
  * grip **multiplicity**: ``n_grip_ribs`` evenly-spaced raised rubber ribs
    behind the front collar (each a FIXED-semantics barrel visual). Encoded in
    slot_choices as ``grip_{n}`` so the diversity gate sees distinct grip
    topologies. (clean ``for i in range(n)`` emission from grip_section S9.)

The felt ink tip, rear click button, fixed clip, and grip ribs are always
fixed barrel/carrier visuals (no FIXED decoration parts). The cap-over-collar
capture fit and carrier-in-bore nested fit are real intentional overlaps, so
their joints omit ``MatingContract`` (grandfathered) and rely on the flat
articulation-origin baseline + element-scoped ``allow_overlap``, mirroring the
parent sample's seated-cap treatment.
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
)

__modular__ = True

BarrelProfile = Literal["rounded_rect", "round_cylindrical"]
TipForm = Literal["chisel_wedge", "bullet_cone"]
Actuation = Literal[
    "pull_off_cap",
    "twin_pull_off_cap",
    "click_retract",
    "twist_extend",
    "twist_cap",
    "flip_cap",
]
PocketClip = Literal["fixed_flat", "sprung_pivot", "none"]
MaterialStyle = Literal["lime_black", "cobalt_blue", "magenta_grey", "graphite"]

BARREL_PROFILES: tuple[BarrelProfile, ...] = ("rounded_rect", "round_cylindrical")
TIP_FORMS: tuple[TipForm, ...] = ("chisel_wedge", "bullet_cone")
ACTUATIONS: tuple[Actuation, ...] = (
    "pull_off_cap",
    "twin_pull_off_cap",
    "click_retract",
    "twist_extend",
    "twist_cap",
    "flip_cap",
)
POCKET_CLIPS: tuple[PocketClip, ...] = ("fixed_flat", "sprung_pivot", "none")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "lime_black",
    "cobalt_blue",
    "magenta_grey",
    "graphite",
)

# Actuations that produce a separate cap part (a real cap that closes over the
# nib). Only these allow a sprung pivot clip (clips onto the cap top) and a
# fixed clip on the cap; click/twist_extend have no cap.
CAP_ACTUATIONS: tuple[Actuation, ...] = (
    "pull_off_cap",
    "twin_pull_off_cap",
    "twist_cap",
    "flip_cap",
)

# Grip-rib multiplicity domain (spec §8).
N_GRIP_MIN, N_GRIP_MAX = 0, 12

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "lime_black": {
        "body": (0.82, 0.93, 0.13, 1.0),
        "cap": (0.07, 0.07, 0.08, 1.0),
        "nib": (0.07, 0.07, 0.08, 1.0),
        "felt": (0.78, 0.90, 0.15, 1.0),
        "clip": (0.28, 0.28, 0.30, 1.0),
        "grip": (0.16, 0.16, 0.18, 1.0),
    },
    "cobalt_blue": {
        "body": (0.18, 0.45, 0.78, 1.0),
        "cap": (0.07, 0.07, 0.08, 1.0),
        "nib": (0.07, 0.07, 0.08, 1.0),
        "felt": (0.12, 0.35, 0.65, 1.0),
        "clip": (0.62, 0.64, 0.68, 1.0),
        "grip": (0.10, 0.10, 0.12, 1.0),
    },
    "magenta_grey": {
        "body": (0.86, 0.18, 0.52, 1.0),
        "cap": (0.20, 0.20, 0.22, 1.0),
        "nib": (0.10, 0.10, 0.11, 1.0),
        "felt": (0.78, 0.20, 0.50, 1.0),
        "clip": (0.55, 0.56, 0.58, 1.0),
        "grip": (0.24, 0.24, 0.26, 1.0),
    },
    "graphite": {
        "body": (0.26, 0.27, 0.30, 1.0),
        "cap": (0.10, 0.11, 0.12, 1.0),
        "nib": (0.06, 0.06, 0.07, 1.0),
        "felt": (0.40, 0.42, 0.46, 1.0),
        "clip": (0.70, 0.72, 0.74, 1.0),
        "grip": (0.14, 0.14, 0.15, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). The pen is a slender rod ~0.14 m long
# along +X. Mechanical sizes (wall, clearances, travel margins) are never
# scaled; footprint/length are scaled per-build.
# Baselines from parent bd7a9b72 (rounded-rect highlighter) and round_barrel S6.
# ---------------------------------------------------------------------------
_BARREL_LEN = 0.092  # lime body length (X)
_BARREL_W = 0.0170  # body width (Y) — rounded-rect
_BARREL_H = 0.0120  # body height (Z) — rounded-rect
_BARREL_R = 0.0070  # body radius — round
_BODY_CORNER_R = 0.0030

_COLLAR_LEN = 0.0060  # short stepped front collar where the cap registers
_COLLAR_W = 0.0150
_COLLAR_H = 0.0105
_COLLAR_R = 0.0060
_COLLAR_CORNER_R = 0.0028

# Nib (chisel + bullet share a base holder; tip geometry differs).
_NIB_BASE_LEN = 0.0080
_NIB_BASE_W = 0.0120
_NIB_BASE_H = 0.0090
_NIB_BASE_R = 0.0050
_NIB_WEDGE_LEN = 0.0120  # chisel taper length
_NIB_TIP_W = 0.0090
_NIB_TIP_H = 0.0018
_NIB_CONE_LEN = 0.0140  # bullet cone length
_NIB_TIP_R = 0.0012  # bullet rounded point radius

# Cap (hollow shell, closed front, open rear; slides/screws/flips over the nib).
_CAP_LEN = 0.0420
_CAP_OUTER_W = 0.0184
_CAP_OUTER_H = 0.0134
_CAP_OUTER_R = 0.0092
_CAP_WALL = 0.0014
_CAP_CORNER_R = 0.0034
_CAP_SEAT_OVERLAP = 0.0060  # how far the cap mouth slides back onto the barrel

# Click / twist-extend internal carrier.
_NOSE_LEN = 0.018
_CARRIER_LEN = 0.030
_CARRIER_R = 0.0050
_EXTENSION = 0.030  # carrier prismatic travel

# Twist-extend collar.
_COLLAR_BODY_LEN = 0.030
_N_KNURL_RIBS = 12

# Click button (rear visual).
_CLICK_LEN = 0.008
_CLICK_R = 0.0040

# Pocket clip.
_CLIP_LEN = 0.0260
_CLIP_W = 0.0070
_CLIP_THICK = 0.0016

# Grip rib band.
_GRIP_RIB_W = 0.0012  # rib thickness along X
_GRIP_RIB_PROUD = 0.0008  # how far ribs stand proud of the barrel surface
_GRIP_ZONE_LEN = 0.022  # nominal grip-band length behind the collar


@dataclass(frozen=True)
class PenConfig:
    barrel_profile: BarrelProfile | None = None
    tip_form: TipForm | None = None
    actuation: Actuation | None = None
    pocket_clip: PocketClip | None = None
    n_grip_ribs: int | None = None
    material_style: MaterialStyle = "lime_black"
    barrel_len_scale: float = 1.0
    barrel_girth_scale: float = 1.0
    cap_travel_scale: float = 1.0
    nib_len_scale: float = 1.0
    grip_band_scale: float = 1.0
    name: str = "pen"


@dataclass(frozen=True)
class ResolvedPenConfig:
    barrel_profile: BarrelProfile
    tip_form: TipForm
    actuation: Actuation
    pocket_clip: PocketClip
    n_grip_ribs: int
    material_style: MaterialStyle
    # Concrete geometry (scaled).
    barrel_len: float
    barrel_w: float
    barrel_h: float
    barrel_r: float
    collar_len: float
    nib_base_len: float
    nib_len_scale: float
    cap_travel_scale: float
    grip_zone_len: float
    name: str

    @property
    def is_round(self) -> bool:
        return self.barrel_profile == "round_cylindrical"

    @property
    def has_cap(self) -> bool:
        return self.actuation in CAP_ACTUATIONS

    @property
    def nib_total_len(self) -> float:
        tip_len = _NIB_WEDGE_LEN if self.tip_form == "chisel_wedge" else _NIB_CONE_LEN + _NIB_TIP_R
        return (self.nib_base_len + tip_len) * self.nib_len_scale

    @property
    def collar_front_x(self) -> float:
        return self.barrel_len + self.collar_len


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> PenConfig:
    rng = random.Random(seed)
    # Weighted procedural sampling: round barrel / bullet tip / exotic
    # actuations slightly rarer; no grip ribs is the most common (spec §9).
    profile = rng.choices(BARREL_PROFILES, weights=[7, 3], k=1)[0]
    tip = rng.choices(TIP_FORMS, weights=[6, 4], k=1)[0]
    actuation = rng.choices(
        ACTUATIONS,
        weights=[5, 2, 3, 3, 3, 3],  # pull_off common; twin rarest
        k=1,
    )[0]
    clip = rng.choices(POCKET_CLIPS, weights=[5, 3, 2], k=1)[0]
    n_grip = rng.choices(
        [0, 4, 6, 8, 10, 12],
        weights=[8, 3, 4, 4, 2, 1],
        k=1,
    )[0]
    return PenConfig(
        barrel_profile=profile,
        tip_form=tip,
        actuation=actuation,
        pocket_clip=clip,
        n_grip_ribs=n_grip,
        material_style=rng.choice(MATERIAL_STYLES),
        barrel_len_scale=round(rng.uniform(0.90, 1.12), 4),
        barrel_girth_scale=round(rng.uniform(0.92, 1.10), 4),
        cap_travel_scale=round(rng.uniform(0.95, 1.15), 4),
        nib_len_scale=round(rng.uniform(0.90, 1.10), 4),
        grip_band_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_pen_{seed}",
    )


def resolve_config(config: PenConfig | None = None) -> ResolvedPenConfig:
    cfg = config or PenConfig()
    profile = _pick(cfg.barrel_profile, BARREL_PROFILES)
    tip = _pick(cfg.tip_form, TIP_FORMS)
    actuation = _pick(cfg.actuation, ACTUATIONS)
    clip = _pick(cfg.pocket_clip, POCKET_CLIPS)
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)

    has_cap = actuation in CAP_ACTUATIONS
    # sprung_pivot clips onto a cap top: only legal when there is a cap part.
    if clip == "sprung_pivot" and not has_cap:
        clip = "fixed_flat"

    n_grip = int(cfg.n_grip_ribs) if cfg.n_grip_ribs is not None else 0
    n_grip = int(_clamp(n_grip, N_GRIP_MIN, N_GRIP_MAX))

    len_scale = _clamp(cfg.barrel_len_scale, 0.90, 1.12)
    girth_scale = _clamp(cfg.barrel_girth_scale, 0.92, 1.10)
    cap_travel_scale = _clamp(cfg.cap_travel_scale, 0.95, 1.15)
    nib_len_scale = _clamp(cfg.nib_len_scale, 0.90, 1.10)
    grip_band_scale = _clamp(cfg.grip_band_scale, 0.85, 1.10)

    barrel_len = _BARREL_LEN * len_scale
    barrel_w = _BARREL_W * girth_scale
    barrel_h = _BARREL_H * girth_scale
    barrel_r = _BARREL_R * girth_scale

    # Grip band must fit in the barrel segment behind the collar; cap a generous
    # fraction of the barrel length (spec §7 inequality).
    grip_zone_len = min(_GRIP_ZONE_LEN * grip_band_scale, barrel_len * 0.45)

    return ResolvedPenConfig(
        barrel_profile=profile,
        tip_form=tip,
        actuation=actuation,
        pocket_clip=clip,
        n_grip_ribs=n_grip,
        material_style=material_style,
        barrel_len=barrel_len,
        barrel_w=barrel_w,
        barrel_h=barrel_h,
        barrel_r=barrel_r,
        collar_len=_COLLAR_LEN,
        nib_base_len=_NIB_BASE_LEN,
        nib_len_scale=nib_len_scale,
        cap_travel_scale=cap_travel_scale,
        grip_zone_len=grip_zone_len,
        name=cfg.name or "pen",
    )


def with_overrides(config: PenConfig, **kwargs: object) -> PenConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: PenConfig | ResolvedPenConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedPenConfig) else resolve_config(config)
    return (
        ("barrel_profile", r.barrel_profile),
        ("tip_form", r.tip_form),
        ("actuation", r.actuation),
        ("pocket_clip", r.pocket_clip),
        ("grip", f"grip_{r.n_grip_ribs}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _rounded_rect_prism(length: float, width: float, height: float, corner_r: float):
    """A rounded-rectangle prism whose long axis is +X, centered on Y/Z,
    spanning X in [0, length]."""
    f = min(corner_r, 0.49 * min(width, height))
    return cq.Workplane("YZ").rect(width, height).extrude(length).edges("|X").fillet(f)


def _cylinder(radius: float, length: float, x_offset: float = 0.0):
    """A round cylinder along +X starting at x_offset."""
    return cq.Workplane("YZ").workplane(offset=x_offset).circle(radius).extrude(length)


def _section_dims(r: ResolvedPenConfig) -> tuple[float, float]:
    """Effective (width, height) bounding the barrel cross-section."""
    if r.is_round:
        return 2.0 * r.barrel_r, 2.0 * r.barrel_r
    return r.barrel_w, r.barrel_h


def _build_barrel_mesh(r: ResolvedPenConfig, *, assets):
    """Root barrel: body + stepped front collar as one solid. For click /
    twist_extend it also gets a front nose cone with a bore for nib passage."""
    twin = r.actuation == "twin_pull_off_cap"
    if r.is_round:
        body = _cylinder(r.barrel_r, r.barrel_len)
        collar = _cylinder(_COLLAR_R, r.collar_len, x_offset=r.barrel_len)
        rear = _cylinder(r.barrel_r, 0.0010, x_offset=-0.0010)
        barrel = body.union(collar).union(rear)
        if twin:
            # Mirror a rear collar so the rear cap registers on a real shoulder.
            rear_collar = _cylinder(_COLLAR_R, r.collar_len, x_offset=-r.collar_len)
            barrel = barrel.union(rear_collar)
    else:
        body = _rounded_rect_prism(r.barrel_len, r.barrel_w, r.barrel_h, _BODY_CORNER_R)
        collar = _rounded_rect_prism(
            r.collar_len, _COLLAR_W, _COLLAR_H, _COLLAR_CORNER_R
        ).translate((r.barrel_len, 0.0, 0.0))
        barrel = body.union(collar)
        if twin:
            rear_collar = _rounded_rect_prism(
                r.collar_len, _COLLAR_W, _COLLAR_H, _COLLAR_CORNER_R
            ).translate((-r.collar_len, 0.0, 0.0))
            barrel = barrel.union(rear_collar)

    if r.actuation in ("click_retract", "twist_extend"):
        # Replace the collar with a tapered nose cone that has a bore for the
        # nib to slide through (the nib lives on an internal carrier).
        nose_w, nose_h = _section_dims(r)
        tip_w, tip_h = nose_w * 0.82, nose_h * 0.90
        nose = (
            cq.Workplane("YZ")
            .workplane(offset=r.barrel_len)
            .rect(nose_w, nose_h)
            .workplane(offset=_NOSE_LEN)
            .rect(tip_w, tip_h)
            .loft()
        )
        bore = (
            cq.Workplane("YZ")
            .workplane(offset=r.barrel_len - 0.002)
            .rect(2.0 * _CARRIER_R + 0.0018, 2.0 * _CARRIER_R + 0.0018)
            .extrude(_NOSE_LEN + 0.004)
        )
        barrel = barrel.union(nose).cut(bore)

    return mesh_from_cadquery(barrel, "barrel_body", assets=assets)


def _build_nib_mesh(r: ResolvedPenConfig, *, assets):
    """Writing nib authored with its base at local X=0, extending in +X.
    chisel_wedge = holder + wedge loft; bullet_cone = holder + cone + sphere.
    Cross-section primitive derives from barrel_profile."""
    s = r.nib_len_scale
    base_len = r.nib_base_len * s
    if r.is_round:
        holder = _cylinder(_NIB_BASE_R, base_len)
    else:
        holder = _rounded_rect_prism(base_len, _NIB_BASE_W, _NIB_BASE_H, 0.0018)

    if r.tip_form == "chisel_wedge":
        wedge = (
            cq.Workplane("YZ")
            .workplane(offset=base_len)
            .rect(_NIB_BASE_W if not r.is_round else 2.0 * _NIB_BASE_R, _NIB_BASE_H)
            .workplane(offset=_NIB_WEDGE_LEN * s)
            .rect(_NIB_TIP_W, _NIB_TIP_H)
            .loft(combine=True)
        )
        nib = holder.union(wedge)
    else:
        cone = (
            cq.Workplane("YZ")
            .workplane(offset=base_len)
            .circle(_NIB_BASE_R)
            .workplane(offset=_NIB_CONE_LEN * s)
            .circle(_NIB_TIP_R)
            .loft(combine=True)
        )
        tip_x = base_len + _NIB_CONE_LEN * s
        cap_sphere = cq.Workplane("YZ").workplane(offset=tip_x).sphere(_NIB_TIP_R)
        nib = holder.union(cone).union(cap_sphere)
    return mesh_from_cadquery(nib, "nib", assets=assets)


def _build_felt_mesh(r: ResolvedPenConfig, *, assets):
    """Exposed ink-soaked felt sliver at the very tip (a barrel/carrier visual).
    Authored with its base at local X=0 so callers shift it to the tip."""
    s = r.nib_len_scale
    if r.tip_form == "chisel_wedge":
        x0 = (r.nib_base_len + _NIB_WEDGE_LEN) * s
        felt = (
            cq.Workplane("YZ")
            .workplane(offset=x0 - 0.0015)
            .rect(_NIB_TIP_W * 0.96, _NIB_TIP_H * 1.05)
            .workplane(offset=0.0025)
            .rect(_NIB_TIP_W * 0.9, _NIB_TIP_H * 0.8)
            .loft(combine=True)
        )
    else:
        x0 = (r.nib_base_len + _NIB_CONE_LEN) * s
        felt = _cylinder(0.0007, 0.0020, x_offset=x0)
    return mesh_from_cadquery(felt, "felt_tip", assets=assets)


def _cap_top_z(r: ResolvedPenConfig) -> float:
    """Z of the cap's top outer surface (where clips/hinges anchor)."""
    if r.is_round:
        return r.barrel_r + _CAP_WALL
    return _CAP_OUTER_H / 2.0


def _build_cap_mesh(r: ResolvedPenConfig, *, threaded: bool, hinged: bool, assets):
    """Hollow cap, closed front (+X), open rear (-X); mouth at local X=0. For
    fixed_flat clips it carries the inline clip rib. ``threaded`` adds a screw
    boss visual at the mouth; ``hinged`` adds a side hinge knuckle at the mouth."""
    if r.is_round:
        # Size the round cap to the barrel so the mouth bore is slightly smaller
        # than the barrel radius -> a real snug friction fit (guaranteed contact;
        # the intentional overlap is covered by allow_overlap).
        cap_outer_r = r.barrel_r + _CAP_WALL
        outer = _cylinder(cap_outer_r, _CAP_LEN)
        bore = _cylinder(r.barrel_r - 0.0004, _CAP_LEN - _CAP_WALL)
        cap = outer.cut(bore)
        clip_z = cap_outer_r + _CLIP_THICK / 2.0 - 0.0002
        top_z = cap_outer_r
    else:
        outer = _rounded_rect_prism(_CAP_LEN, _CAP_OUTER_W, _CAP_OUTER_H, _CAP_CORNER_R)
        bore = (
            cq.Workplane("YZ")
            .rect(_CAP_OUTER_W - 2 * _CAP_WALL, _CAP_OUTER_H - 2 * _CAP_WALL)
            .extrude(_CAP_LEN - _CAP_WALL)
            .edges("|X")
            .fillet(_CAP_CORNER_R - _CAP_WALL)
        )
        cap = outer.cut(bore)
        clip_z = _CAP_OUTER_H / 2.0 + _CLIP_THICK / 2.0 - 0.0002
        top_z = _CAP_OUTER_H / 2.0

    if r.pocket_clip == "fixed_flat":
        clip_x0 = _CAP_LEN - _CLIP_LEN
        clip = (
            cq.Workplane("YZ")
            .workplane(offset=clip_x0)
            .center(0.0, clip_z)
            .rect(_CLIP_W, _CLIP_THICK)
            .extrude(_CLIP_LEN)
            .edges("|X")
            .fillet(0.0006)
        )
        boss = (
            cq.Workplane("YZ")
            .workplane(offset=_CAP_LEN - 0.0050)
            .center(0.0, top_z - 0.0010)
            .rect(_CLIP_W, 0.0040)
            .extrude(0.0045)
        )
        cap = cap.union(clip).union(boss)

    if threaded:
        # A short threaded boss band at the cap mouth that meshes onto the barrel
        # collar; placed as a proud annulus embedded in the cap wall so it fuses
        # into one solid (the joint origin sits on it).
        if r.is_round:
            band_o = _cylinder(top_z + 0.0006, 0.0040)
            band_i = _cylinder(top_z - _CAP_WALL - 0.0006, 0.0050, x_offset=-0.0005)
            band = band_o.cut(band_i)
        else:
            band = _rounded_rect_prism(
                0.0040, _CAP_OUTER_W + 0.0012, _CAP_OUTER_H + 0.0012, _CAP_CORNER_R
            ).cut(
                _rounded_rect_prism(
                    0.0050,
                    _CAP_OUTER_W - 2 * _CAP_WALL,
                    _CAP_OUTER_H - 2 * _CAP_WALL,
                    _CAP_CORNER_R,
                ).translate((-0.0005, 0.0, 0.0))
            )
        cap = cap.union(band)

    if hinged:
        # A side hinge knuckle at the mouth top, with a transverse-Y axle so the
        # flip hinge origin sits on real geometry.
        knuckle = (
            cq.Workplane("XZ", origin=(0.0, 0.0, top_z))
            .circle(0.0016)
            .extrude(_CAP_OUTER_W if not r.is_round else 2.0 * top_z, both=True)
        )
        cap = cap.union(knuckle)

    return mesh_from_cadquery(cap, "cap_shell", assets=assets)


def _build_carrier_mesh(r: ResolvedPenConfig, *, assets):
    """Internal nib carrier cylinder (the cartridge slider). Authored so its
    body spans local X in [-CARRIER_LEN, 0]; the nib base is added at X=0."""
    stem = _cylinder(_CARRIER_R, _CARRIER_LEN, x_offset=-_CARRIER_LEN)
    return mesh_from_cadquery(stem, "carrier_body", assets=assets)


def _build_click_button_mesh(r: ResolvedPenConfig, *, assets):
    """Rear click plunger button (barrel visual) authored at local X=0,
    extending in -X behind the barrel rear face."""
    btn = _cylinder(_CLICK_R, _CLICK_LEN, x_offset=-_CLICK_LEN)
    return mesh_from_cadquery(btn, "click_button", assets=assets)


def _build_collar_mesh(r: ResolvedPenConfig, *, assets):
    """Twist-extend rotating rear collar: a short knurled band section that
    abuts the barrel rear (seam at local X=0), extending in -X with N grip ribs
    so it reads as a grippable twist knob and its AABB contains X=0."""
    nose_w, nose_h = _section_dims(r)
    radius = max(nose_w, nose_h) / 2.0 + 0.0006
    body = _cylinder(radius, _COLLAR_BODY_LEN, x_offset=-_COLLAR_BODY_LEN)
    # Knurl ribs around the band.
    for i in range(_N_KNURL_RIBS):
        ang = 2.0 * math.pi * i / _N_KNURL_RIBS
        rib = (
            cq.Workplane("YZ")
            .workplane(offset=-_COLLAR_BODY_LEN)
            .center(radius * math.cos(ang), radius * math.sin(ang))
            .circle(0.0006)
            .extrude(_COLLAR_BODY_LEN)
        )
        body = body.union(rib)
    return mesh_from_cadquery(body, "collar_body", assets=assets)


def _build_clip_mesh(r: ResolvedPenConfig, *, assets):
    """Sprung pocket clip part. Authored with its hinge line at local
    (0, 0, 0): the strip lies flat (extends in -X) just above z=0 with a
    contoured tail, plus a transverse-Y axle rod through the origin so the
    REVOLUTE child origin lands on real hardware."""
    # The strip's near end reaches slightly past the origin (+0.001) so the
    # transverse axle rod is fully embedded in it (single solid, no island).
    strip = (
        cq.Workplane("XY")
        .box(_CLIP_LEN, _CLIP_W, _CLIP_THICK, centered=(True, True, True))
        .edges("|Z")
        .fillet(0.0008)
        .translate((-_CLIP_LEN / 2.0 + 0.0010, 0.0, 0.0))
    )
    # Contoured free-end tail bent slightly down toward the cap. Overlap the
    # strip end (centered inside the strip span) so the union is one solid.
    tail = (
        cq.Workplane("XY")
        .box(0.0060, _CLIP_W, 0.0022, centered=(True, True, True))
        .translate((-_CLIP_LEN + 0.0020, 0.0, -0.0008))
    )
    # Transverse-Y hinge knuckle straddling the origin, sized so it clearly
    # overlaps the strip near end (one solid; the joint origin lands on it).
    knuckle = cq.Workplane("XY").box(
        0.0030, _CLIP_W * 1.25, _CLIP_THICK + 0.0016, centered=(True, True, True)
    )
    clip = strip.union(knuckle).union(tail)
    return mesh_from_cadquery(clip, "clip_body", assets=assets)


def _build_grip_rib_mesh(r: ResolvedPenConfig, *, assets):
    """One raised rubber grip rib encircling the barrel, authored at local X in
    [0, _GRIP_RIB_W], centered on Y/Z. Hollow interior matches the barrel so it
    rests flush; outer profile stands proud by _GRIP_RIB_PROUD."""
    if r.is_round:
        outer = _cylinder(r.barrel_r + _GRIP_RIB_PROUD, _GRIP_RIB_W)
        inner = _cylinder(r.barrel_r - 0.0002, _GRIP_RIB_W + 0.0004, x_offset=-0.0002)
        rib = outer.cut(inner)
    else:
        ow = r.barrel_w + 2.0 * _GRIP_RIB_PROUD
        oh = r.barrel_h + 2.0 * _GRIP_RIB_PROUD
        orad = min(_BODY_CORNER_R + _GRIP_RIB_PROUD, min(ow, oh) / 2.0 * 0.9)
        outer = _rounded_rect_prism(_GRIP_RIB_W, ow, oh, orad)
        inner = _rounded_rect_prism(
            _GRIP_RIB_W + 0.0004, r.barrel_w - 0.0002, r.barrel_h - 0.0002, _BODY_CORNER_R
        ).translate((-0.0002, 0.0, 0.0))
        rib = outer.cut(inner)
    return mesh_from_cadquery(rib, "grip_rib", assets=assets)


# ---------------------------------------------------------------------------
# Build helpers (emit children for the chosen actuation)
# ---------------------------------------------------------------------------
def _nib_inertial(r: ResolvedPenConfig, mass: float, *, x0: float = 0.0) -> Inertial:
    w, h = _section_dims(r)
    return Inertial.from_geometry(
        Box((r.nib_total_len, max(w, _NIB_BASE_W), max(h, _NIB_BASE_H))),
        mass=mass,
        origin=Origin(xyz=(x0 + r.nib_total_len / 2.0, 0.0, 0.0)),
    )


def _attach_tip_visuals(part, r, mats, *, x0: float, assets) -> None:
    """Attach nib + felt visuals at local X=x0 (the front shoulder)."""
    part.visual(
        _build_nib_mesh(r, assets=assets),
        origin=Origin(xyz=(x0, 0.0, 0.0)),
        material=mats["nib"],
        name="nib", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        _build_felt_mesh(r, assets=assets),
        origin=Origin(xyz=(x0, 0.0, 0.0)),
        material=mats["felt"],
        name="felt_tip", material_class_id="fabric.felt",
    )


def _cap_inertial(r: ResolvedPenConfig) -> Inertial:
    w, h = _section_dims(r)
    return Inertial.from_geometry(
        Box((_CAP_LEN, _CAP_OUTER_W, _CAP_OUTER_H)),
        mass=0.006,
        origin=Origin(xyz=(_CAP_LEN / 2.0, 0.0, 0.0)),
    )


def _emit_pull_off_caps(model, r, barrel, mats, *, n_ends: int, assets) -> list[str]:
    """One or two pull-off caps that slide off along +X (and -X for twin). Each
    cap mouth seats _CAP_SEAT_OVERLAP inside its own barrel-body end face and
    covers the nib protruding from that end's collar."""
    nib_tip_local = r.collar_len + r.nib_total_len  # tip distance past the end face
    full_clear = ((_CAP_SEAT_OVERLAP + nib_tip_local) + 0.006) * r.cap_travel_scale
    names: list[str] = []
    for i in range(n_ends):
        direction = 1.0 if i == 0 else -1.0
        # Front end face = barrel_len (opens +X); rear end face = 0 (opens -X).
        end_face = r.barrel_len if direction > 0 else 0.0
        seat = end_face - direction * _CAP_SEAT_OVERLAP
        cap = model.part(f"cap_{i}" if n_ends > 1 else "cap")
        cap_mesh = _build_cap_mesh(r, threaded=False, hinged=False, assets=assets)
        # For the rear cap (direction < 0) the joint origin rpy spins the child
        # frame 180° about Z so the mouth-at-X=0 cap opens toward -X.
        rpy = (0.0, 0.0, 0.0) if direction > 0 else (0.0, 0.0, math.pi)
        cap.visual(cap_mesh, material=mats["cap"], name="cap_shell", material_class_id="plastic.opaque_glossy_molded")
        cap.inertial = _cap_inertial(r)
        model.articulation(
            f"barrel_to_{cap.name}",
            ArticulationType.PRISMATIC,
            parent=barrel,
            child=cap,
            origin=Origin(xyz=(seat, 0.0, 0.0), rpy=rpy),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=15.0, velocity=0.25, lower=0.0, upper=full_clear),
        )
        names.append(cap.name)
    return names


def _emit_twist_cap(model, r, barrel, mats, *, assets) -> list[str]:
    seat_x = r.collar_front_x
    cap = model.part("cap")
    cap.visual(
        _build_cap_mesh(r, threaded=True, hinged=False, assets=assets),
        material=mats["cap"],
        name="cap_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    cap.inertial = _cap_inertial(r)
    unscrew_angle = 2.0 * 2.0 * math.pi + math.pi / 2.0  # ~2.5 turns
    model.articulation(
        "barrel_to_cap",
        ArticulationType.REVOLUTE,
        parent=barrel,
        child=cap,
        origin=Origin(xyz=(seat_x, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=2.0, lower=0.0, upper=unscrew_angle),
    )
    return ["cap"]


def _emit_flip_cap(model, r, barrel, mats, *, assets) -> list[str]:
    # Cap authored with its mouth at local X=0; the hinge sits at the cap mouth
    # top, mating the barrel collar top edge. We translate the cap mesh so the
    # hinge (mouth top) lands at the child origin.
    top_z = _cap_top_z(r)
    cap = model.part("cap")
    cap_mesh = _build_cap_mesh(r, threaded=False, hinged=True, assets=assets)
    cap.visual(
        cap_mesh,
        material=mats["cap"],
        name="cap_shell", material_class_id="plastic.opaque_glossy_molded",
        # Shift so the mouth-top hinge knuckle sits at the part origin (0,0,0).
        origin=Origin(xyz=(0.0, 0.0, -top_z)),
    )
    cap.inertial = Inertial.from_geometry(
        Box((_CAP_LEN, _CAP_OUTER_W, _CAP_OUTER_H)),
        mass=0.006,
        origin=Origin(xyz=(_CAP_LEN / 2.0, 0.0, -top_z + _CAP_OUTER_H / 2.0)),
    )
    hinge_x = r.barrel_len
    hinge_z = _COLLAR_R if r.is_round else _COLLAR_H / 2.0
    model.articulation(
        "barrel_to_cap",
        ArticulationType.REVOLUTE,
        parent=barrel,
        child=cap,
        origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=2.4),
    )
    return ["cap"]


def _emit_click_retract(model, r, barrel, mats, *, assets) -> list[str]:
    retracted_x = r.barrel_len - 0.010
    carrier = model.part("nib_carrier")
    carrier.visual(_build_carrier_mesh(r, assets=assets), material=mats["nib"], name="carrier_body", material_class_id="plastic.opaque_glossy_molded")
    _attach_tip_visuals(carrier, r, mats, x0=0.0, assets=assets)
    carrier.inertial = _nib_inertial(r, 0.003)
    model.articulation(
        "barrel_to_carrier",
        ArticulationType.PRISMATIC,
        parent=barrel,
        child=carrier,
        origin=Origin(xyz=(retracted_x, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=0.30, lower=0.0, upper=_EXTENSION),
    )
    # Rear click button (barrel visual).
    barrel.visual(
        _build_click_button_mesh(r, assets=assets), material=mats["cap"], name="click_button", material_class_id="plastic.opaque_glossy_molded"
    )
    return ["nib_carrier"]


def _emit_twist_extend(model, r, barrel, mats, *, assets) -> list[str]:
    # Rotating rear collar (REVOLUTE +X) at the barrel rear seam (X=0).
    collar = model.part("twist_collar")
    collar.visual(_build_collar_mesh(r, assets=assets), material=mats["grip"], name="collar_body", material_class_id="rubber.directional_grooved")
    nose_w, nose_h = _section_dims(r)
    collar.inertial = Inertial.from_geometry(
        Box((_COLLAR_BODY_LEN, max(nose_w, nose_h), max(nose_w, nose_h))),
        mass=0.004,
        origin=Origin(xyz=(-_COLLAR_BODY_LEN / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "body_to_collar",
        ArticulationType.REVOLUTE,
        parent=barrel,
        child=collar,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=2.0 * math.pi),
    )
    # Nib carrier (PRISMATIC +X) sliding through the nose bore.
    retracted_x = r.barrel_len - 0.010
    carrier = model.part("nib_carrier")
    carrier.visual(_build_carrier_mesh(r, assets=assets), material=mats["nib"], name="carrier_body", material_class_id="plastic.opaque_glossy_molded")
    _attach_tip_visuals(carrier, r, mats, x0=0.0, assets=assets)
    carrier.inertial = _nib_inertial(r, 0.003)
    model.articulation(
        "body_to_nib",
        ArticulationType.PRISMATIC,
        parent=barrel,
        child=carrier,
        origin=Origin(xyz=(retracted_x, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=0.10, lower=0.0, upper=_EXTENSION),
    )
    return ["twist_collar", "nib_carrier"]


def _emit_sprung_clip(model, r, cap_name: str, mats, *, assets) -> list[str]:
    """Sprung pivot clip hinged on the cap top (serial: barrel→cap→clip)."""
    cap = model.get_part(cap_name)
    top_z = _cap_top_z(r)
    clip = model.part("clip")
    clip.visual(_build_clip_mesh(r, assets=assets), material=mats["clip"], name="clip_body", material_class_id="metal.brushed_silver")
    clip.inertial = Inertial.from_geometry(
        Box((_CLIP_LEN, _CLIP_W, _CLIP_THICK)),
        mass=0.0015,
        origin=Origin(xyz=(-_CLIP_LEN / 2.0, 0.0, 0.0)),
    )
    hinge_x = _CAP_LEN - 0.0040  # cap-local X, near the closed front
    hinge_z = top_z + 0.0012
    model.articulation(
        "cap_to_clip",
        ArticulationType.REVOLUTE,
        parent=cap,
        child=clip,
        origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=0.55),
    )
    return ["clip"]


def _emit_grip(model, r, barrel, mats, *, assets) -> None:
    if r.n_grip_ribs <= 0:
        return
    grip_start = r.barrel_len - r.grip_zone_len - 0.001
    grip_start = max(grip_start, 0.002)
    pitch = r.grip_zone_len / r.n_grip_ribs
    rib_mesh = _build_grip_rib_mesh(r, assets=assets)
    for i in range(r.n_grip_ribs):
        rib_x = grip_start + i * pitch
        barrel.visual(
            rib_mesh,
            origin=Origin(xyz=(rib_x, 0.0, 0.0)),
            material=mats["grip"],
            name=f"grip_rib_{i}", material_class_id="rubber.smooth_plain",
        )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_pen(
    config: PenConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.material_style]
    mats = {
        key: model.material(f"pen_{key}_{r.material_style}", rgba=palette[key])
        for key in ("body", "cap", "nib", "felt", "clip", "grip")
    }

    # Root barrel (carries body + collar/nose; tip visuals when cap actuation).
    barrel = model.part("barrel")
    barrel.visual(_build_barrel_mesh(r, assets=assets), material=mats["body"], name="barrel_body", material_class_id="plastic.opaque_glossy_molded")
    w, h = _section_dims(r)
    barrel.inertial = Inertial.from_geometry(
        Box((r.barrel_len, w, h)),
        mass=0.012,
        origin=Origin(xyz=(r.barrel_len / 2.0, 0.0, 0.0)),
    )

    # Cap-style actuations keep the nib fixed on the barrel; sliding actuations
    # put the nib on the moving carrier instead.
    if r.actuation in ("click_retract", "twist_extend"):
        pass  # nib lives on the carrier emitted below
    elif r.actuation == "twin_pull_off_cap":
        # Nib + felt at both ends. Front shoulder = collar_front_x; rear shoulder
        # = -collar_len (the mirrored rear collar face). Each nib's base sits on
        # its own shoulder and extends outward (rpy flips the rear nib to -X).
        for i in range(2):
            direction = 1.0 if i == 0 else -1.0
            x0 = r.collar_front_x if direction > 0 else -r.collar_len
            barrel.visual(
                _build_nib_mesh(r, assets=assets),
                origin=Origin(
                    xyz=(x0, 0.0, 0.0), rpy=(0.0, 0.0, 0.0 if direction > 0 else math.pi)
                ),
                material=mats["nib"],
                name=f"nib_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
            barrel.visual(
                _build_felt_mesh(r, assets=assets),
                origin=Origin(
                    xyz=(x0, 0.0, 0.0), rpy=(0.0, 0.0, 0.0 if direction > 0 else math.pi)
                ),
                material=mats["felt"],
                name=f"felt_tip_{i}", material_class_id="fabric.felt",
            )
    else:
        _attach_tip_visuals(barrel, r, mats, x0=r.collar_front_x, assets=assets)

    # Actuation children.
    cap_names: list[str] = []
    if r.actuation == "pull_off_cap":
        cap_names = _emit_pull_off_caps(model, r, barrel, mats, n_ends=1, assets=assets)
    elif r.actuation == "twin_pull_off_cap":
        cap_names = _emit_pull_off_caps(model, r, barrel, mats, n_ends=2, assets=assets)
    elif r.actuation == "twist_cap":
        cap_names = _emit_twist_cap(model, r, barrel, mats, assets=assets)
    elif r.actuation == "flip_cap":
        cap_names = _emit_flip_cap(model, r, barrel, mats, assets=assets)
    elif r.actuation == "click_retract":
        _emit_click_retract(model, r, barrel, mats, assets=assets)
    elif r.actuation == "twist_extend":
        _emit_twist_extend(model, r, barrel, mats, assets=assets)

    # Pocket clip.
    if r.pocket_clip == "sprung_pivot" and cap_names:
        _emit_sprung_clip(model, r, cap_names[0], mats, assets=assets)
    elif r.pocket_clip == "fixed_flat" and not r.has_cap:
        # No cap to carry the inline clip: put a fixed flat clip on the barrel.
        clip_z = (r.barrel_r if r.is_round else r.barrel_h / 2.0) + _CLIP_THICK / 2.0
        clip = (
            cq.Workplane("YZ")
            .workplane(offset=0.012)
            .center(0.0, clip_z)
            .rect(_CLIP_W, _CLIP_THICK)
            .extrude(0.035)
            .edges("|X")
            .fillet(0.0006)
        )
        boss = (
            cq.Workplane("YZ")
            .workplane(offset=0.012)
            .center(0.0, (r.barrel_r if r.is_round else r.barrel_h / 2.0) - 0.001)
            .rect(_CLIP_W, 0.004)
            .extrude(0.005)
        )
        barrel.visual(
            mesh_from_cadquery(clip.union(boss), "pocket_clip", assets=assets),
            material=mats["clip"],
            name="pocket_clip", material_class_id="metal.brushed_silver",
        )

    # Grip ribs (multiplicity).
    _emit_grip(model, r, barrel, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pen(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_pen(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_pen_tests(
    object_model: ArticulatedObject,
    config: PenConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    barrel = object_model.get_part("barrel")

    part_names = {p.name for p in object_model.parts}

    # --- Captured-pin / nested-fit allowances for the articulated children. ---
    for cap_name in ("cap", "cap_0", "cap_1"):
        if cap_name in part_names:
            cap = object_model.get_part(cap_name)
            ctx.allow_isolated_part(
                cap,
                reason="cap pulls off the barrel and loses body contact when removed",
            )
            ctx.allow_overlap(
                cap,
                barrel,
                reason=(
                    "seated cap is a friction/screw/flip fit that intentionally "
                    "encloses the nib and wraps the front collar (capture fit)."
                ),
            )
    if "nib_carrier" in part_names:
        carrier = object_model.get_part("nib_carrier")
        ctx.allow_isolated_part(
            carrier,
            reason="nib carrier slides inside the barrel bore as a nested prismatic mechanism.",
        )
        ctx.allow_overlap(
            barrel,
            carrier,
            reason="carrier stem + nib slide inside the barrel bore (nested prismatic fit).",
        )
    if "twist_collar" in part_names:
        collar = object_model.get_part("twist_collar")
        ctx.allow_overlap(
            barrel,
            collar,
            reason="twist collar abuts and overlaps the barrel rear seam (rotating knob).",
        )
    if "clip" in part_names and "cap" in part_names:
        ctx.allow_overlap(
            object_model.get_part("cap"),
            object_model.get_part("clip"),
            reason="sprung clip hinge edge rests on the cap top (captured-pin pivot).",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    # Joints omit MatingContract (captured-pin / nested-fit geometry,
    # grandfathered); the flat 0.015 m articulation-origin baseline runs in the
    # compiler and all origins sit on real hardware (collar seat / bore mouth /
    # hinge knuckle / cap top).
    ctx.fail_if_joint_mating_has_gap()

    # --- slot_choices recorded. ---
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # --- Barrel silhouette: a slender rod along +X (length >> girth). ---
    body_aabb = ctx.part_world_aabb(barrel)
    if body_aabb is not None:
        (bx0, by0, bz0), (bx1, by1, bz1) = body_aabb
        ext_x = bx1 - bx0
        ext_y = by1 - by0
        ext_z = bz1 - bz0
        ctx.check(
            "barrel is a slender rod along +X",
            ext_x > 2.5 * max(ext_y, ext_z),
            details=f"ext_x={ext_x:.4f} ext_y={ext_y:.4f} ext_z={ext_z:.4f}",
        )

    # --- Actuation-specific mechanism checks. ---
    if r.actuation in ("pull_off_cap", "twin_pull_off_cap"):
        cap_names = ["cap"] if r.actuation == "pull_off_cap" else ["cap_0", "cap_1"]
        nib_tip_x = r.collar_front_x + r.nib_total_len
        for cap_name in cap_names:
            j = object_model.get_articulation(f"barrel_to_{cap_name}")
            ctx.check(
                f"{cap_name} is PRISMATIC along the pen axis",
                j.articulation_type == ArticulationType.PRISMATIC
                and round(abs(j.axis[0]), 3) == 1.0,
                details=f"type={j.articulation_type} axis={tuple(round(c, 3) for c in j.axis)}",
            )
            cap = object_model.get_part(cap_name)
            with ctx.pose({j: 0.0}):
                seated = ctx.part_world_aabb(cap)
            with ctx.pose({j: j.motion_limits.upper}):
                opened = ctx.part_world_aabb(cap)
            if seated is not None and opened is not None:
                moved = abs((opened[0][0] + opened[1][0]) - (seated[0][0] + seated[1][0])) / 2.0
                ctx.check(
                    f"pulling {cap_name} moves it clear of the nib",
                    moved > 0.015,
                    details=f"moved={moved:.4f}",
                )
        del nib_tip_x

    elif r.actuation == "twist_cap":
        j = object_model.get_articulation("barrel_to_cap")
        ctx.check(
            "twist cap is REVOLUTE about the pen axis (+X)",
            j.articulation_type == ArticulationType.REVOLUTE and round(j.axis[0], 3) == 1.0,
            details=f"type={j.articulation_type} axis={tuple(round(c, 3) for c in j.axis)}",
        )

    elif r.actuation == "flip_cap":
        j = object_model.get_articulation("barrel_to_cap")
        ctx.check(
            "flip cap is REVOLUTE about a transverse (Y) hinge",
            j.articulation_type == ArticulationType.REVOLUTE and round(abs(j.axis[1]), 3) == 1.0,
            details=f"type={j.articulation_type} axis={tuple(round(c, 3) for c in j.axis)}",
        )
        cap = object_model.get_part("cap")
        with ctx.pose({j: 0.0}):
            c0 = ctx.part_world_aabb(cap)
        with ctx.pose({j: 2.0}):
            c1 = ctx.part_world_aabb(cap)
        if c0 is not None and c1 is not None:
            ctx.check(
                "flipping the cap lifts it off the nib",
                c1[1][2] > c0[1][2] + 0.005,
                details=f"closed_top={c0[1][2]:.4f} open_top={c1[1][2]:.4f}",
            )

    elif r.actuation in ("click_retract", "twist_extend"):
        jname = "barrel_to_carrier" if r.actuation == "click_retract" else "body_to_nib"
        j = object_model.get_articulation(jname)
        ctx.check(
            "nib carrier is PRISMATIC along the pen axis (+X)",
            j.articulation_type == ArticulationType.PRISMATIC and round(j.axis[0], 3) == 1.0,
            details=f"type={j.articulation_type} axis={tuple(round(c, 3) for c in j.axis)}",
        )
        carrier = object_model.get_part("nib_carrier")
        with ctx.pose({j: 0.0}):
            n0 = ctx.part_element_world_aabb(carrier, elem="nib")
        with ctx.pose({j: j.motion_limits.upper}):
            n1 = ctx.part_element_world_aabb(carrier, elem="nib")
        if n0 is not None and n1 is not None:
            ctx.check(
                "extending the carrier pushes the nib forward",
                n1[1][0] > n0[1][0] + 0.015,
                details=f"retracted_front={n0[1][0]:.4f} extended_front={n1[1][0]:.4f}",
            )
        if r.actuation == "twist_extend":
            jc = object_model.get_articulation("body_to_collar")
            ctx.check(
                "twist collar is REVOLUTE about the pen axis (+X)",
                jc.articulation_type == ArticulationType.REVOLUTE and round(jc.axis[0], 3) == 1.0,
                details=f"type={jc.articulation_type} axis={tuple(round(c, 3) for c in jc.axis)}",
            )

    # --- Pocket clip. ---
    if r.pocket_clip == "sprung_pivot" and "clip" in part_names:
        jk = object_model.get_articulation("cap_to_clip")
        ctx.check(
            "sprung clip is REVOLUTE about a transverse (Y) hinge",
            jk.articulation_type == ArticulationType.REVOLUTE and round(abs(jk.axis[1]), 3) == 1.0,
            details=f"type={jk.articulation_type} axis={tuple(round(c, 3) for c in jk.axis)}",
        )
        clip = object_model.get_part("clip")
        with ctx.pose({jk: 0.0}):
            k0 = ctx.part_world_aabb(clip)
        with ctx.pose({jk: 0.55}):
            k1 = ctx.part_world_aabb(clip)
        if k0 is not None and k1 is not None:
            ctx.check(
                "lifting the sprung clip raises its tail",
                k1[1][2] > k0[1][2] + 0.001,
                details=f"flat_top={k0[1][2]:.4f} lifted_top={k1[1][2]:.4f}",
            )

    # --- Grip ribs: regular multiplicity band when present. ---
    grip_names = [v.name for v in barrel.visuals if v.name and v.name.startswith("grip_rib_")]
    ctx.check(
        "grip ribs match the configured count",
        len(grip_names) == r.n_grip_ribs,
        details=f"emitted={len(grip_names)} expected={r.n_grip_ribs}",
    )

    # --- Felt tip is always present (writing point). ---
    has_felt = any(
        v.name and v.name.startswith("felt_tip") for p in object_model.parts for v in p.visuals
    )
    ctx.check("felt writing tip present", has_felt, details=str(part_names))

    return ctx.report()


__all__ = (
    "PenConfig",
    "ResolvedPenConfig",
    "build_pen",
    "build_seeded_pen",
    "config_from_seed",
    "resolve_config",
    "run_pen_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
