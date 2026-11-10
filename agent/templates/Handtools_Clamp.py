# SPDX-License-Identifier: Apache-2.0

"""Screw-driven hand clamp (C-clamp / G-clamp) modular template.

NOTE on the slug name: "clamp" here = a **screw-driven hand clamp** (a C / G
shaped cast-iron clamp), NOT a binder clip / spring clip (that is the separate
``clip`` slug), nor a bench vise, nor pliers. The structure family is a screw
clamp: a fixed C-shaped ``frame`` (root; lower jaw carries a fixed anvil pad,
upper arm carries a threaded boss) + a ``screw`` spindle that feeds vertically
through the boss (PRISMATIC), a user handle at the top, and a pressing foot at
the tip (optionally a swivel pad on a REVOLUTE).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Handtools_Clamp.md`` and the
``picture/Handtools/Clamp`` 5-star sample pool (2 parents + 4 slot-fork
variants), all synced under ``data/records/``.

Coordinate convention (unified to the A-family, spec §13): +Z is up = the screw
axis; the C mouth opens toward -Y (the solid spine is on +Y); the handle T-bar
lies along X; the ``screw`` part frame origin is the BOTTOM TIP of the spindle;
``frame_to_screw`` is PRISMATIC axis=(0,0,-1) (positive q drives the foot DOWN to
clamp); the swivel pad REVOLUTE turns about Y. The B-family modules (tbar_balls,
boxy_deep) are rebased into this convention.

Structure (pattern = ``parallel_children``): a single root ``frame`` part (C
silhouette mesh chosen by ``frame_silhouette``), with three named module axes:

  * ``frame_silhouette`` (2): rounded_C (filleted shallow throat) / boxy_deep
    (deep square throat, sharp corners). A frame mesh-profile dimension; it does
    not change the part tree or joint topology. (parent A / frame variant)
  * ``foot`` (3): the screw-tip pressing foot — swivel_ball_pad (an independent
    ``pad`` part on a REVOLUTE about Y) / fixed_flat_pad (a screw visual, no
    joint) / anvil_disc (a wide flat screw visual, no joint). (parent A /
    parent B / anvilfoot variant)
  * ``handle`` (4): the top user handle — tbar_caps (T-bar + end caps, screw
    visual) / tbar_balls (T-bar + ball ends, screw visual) / side_lever (an
    independent ``lever`` part on a REVOLUTE about Z, parallel to screw on the
    frame) / butterfly_wing (hub + two flat wings, screw visual). (parent A /
    parent B / leverhandle / winghandle variants)

The fixed anvil, T-bar/caps/balls/wings, and grip ridges are always fixed
frame/screw/lever visuals (no FIXED decoration parts; Rule 1). The screw-in-boss
threaded fit, pad-neck-in-tip capture, T-bar cross-hole, ball-on-bar, wing-root-
in-hub, and screw-in-lever-hub captures are all captured-pin geometry, so those
joints omit ``MatingContract`` (grandfathered) and rely on the flat
articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring each
source record's run_tests allow_overlap block).
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
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

FrameSilhouette = Literal["rounded_C", "boxy_deep"]
Foot = Literal["swivel_ball_pad", "fixed_flat_pad", "anvil_disc"]
Handle = Literal["tbar_caps", "tbar_balls", "side_lever", "butterfly_wing"]
PaletteStyle = Literal[
    "red_blue_classic",
    "black_zinc_chrome",
    "cast_iron_steel",
    "galvanized_industrial",
    "orange_safety",
]

FRAME_SILHOUETTES: tuple[FrameSilhouette, ...] = ("rounded_C", "boxy_deep")
FEET: tuple[Foot, ...] = ("swivel_ball_pad", "fixed_flat_pad", "anvil_disc")
HANDLES: tuple[Handle, ...] = (
    "tbar_caps",
    "tbar_balls",
    "side_lever",
    "butterfly_wing",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "red_blue_classic",
    "black_zinc_chrome",
    "cast_iron_steel",
    "galvanized_industrial",
    "orange_safety",
)

# ---------------------------------------------------------------------------
# Per-seed palettes (spec §7). Keys: frame / screw / handle / accent (caps,
# wings, grip) / pad / ridge (rubber grip ridge). Every .visual material is
# driven off this dict so the swept pool is colorful (module_topology_diversity
# only counts structure).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "red_blue_classic": {
        "frame": (0.86, 0.13, 0.10, 1.0),
        "screw": (0.13, 0.32, 0.72, 1.0),
        "handle": (0.36, 0.20, 0.62, 1.0),
        "accent": (0.95, 0.42, 0.08, 1.0),
        "pad": (0.13, 0.32, 0.72, 1.0),
        "ridge": (0.18, 0.18, 0.20, 1.0),
        "steel": (0.62, 0.64, 0.67, 1.0),
    },
    "black_zinc_chrome": {
        "frame": (0.10, 0.10, 0.11, 1.0),
        "screw": (0.74, 0.76, 0.79, 1.0),
        "handle": (0.82, 0.84, 0.86, 1.0),
        "accent": (0.07, 0.07, 0.08, 1.0),
        "pad": (0.74, 0.76, 0.79, 1.0),
        "ridge": (0.07, 0.07, 0.08, 1.0),
        "steel": (0.66, 0.68, 0.71, 1.0),
    },
    "cast_iron_steel": {
        "frame": (0.24, 0.25, 0.27, 1.0),
        "screw": (0.62, 0.64, 0.67, 1.0),
        "handle": (0.50, 0.52, 0.55, 1.0),
        "accent": (0.38, 0.40, 0.43, 1.0),
        "pad": (0.58, 0.60, 0.63, 1.0),
        "ridge": (0.12, 0.12, 0.14, 1.0),
        "steel": (0.66, 0.68, 0.71, 1.0),
    },
    "galvanized_industrial": {
        "frame": (0.55, 0.57, 0.60, 1.0),
        "screw": (0.74, 0.76, 0.79, 1.0),
        "handle": (0.62, 0.64, 0.67, 1.0),
        "accent": (0.46, 0.48, 0.51, 1.0),
        "pad": (0.70, 0.72, 0.75, 1.0),
        "ridge": (0.20, 0.20, 0.22, 1.0),
        "steel": (0.70, 0.72, 0.75, 1.0),
    },
    "orange_safety": {
        "frame": (0.92, 0.48, 0.06, 1.0),
        "screw": (0.74, 0.76, 0.79, 1.0),
        "handle": (0.92, 0.48, 0.06, 1.0),
        "accent": (0.16, 0.16, 0.18, 1.0),
        "pad": (0.62, 0.64, 0.67, 1.0),
        "ridge": (0.18, 0.18, 0.20, 1.0),
        "steel": (0.62, 0.64, 0.67, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), A-family convention (parent A / variants).
# A small bench C-clamp: frame ~0.13-0.18 m tall, screw ~0.085 m. Mechanical
# fits (thread embed, clearances) are never scaled; geometry/throat are scaled.
# ---------------------------------------------------------------------------
_FRAME_DEPTH = 0.034  # frame thickness along X
_FRAME_BAR = 0.026  # C cross-section width (in the YZ plane)
_THROAT = 0.060  # clear vertical opening between the jaws (Z) at rest
_THROAT_Y = 0.060  # throat depth (how far the mouth reaches in Y)
_BOTTOM_Z = 0.0  # lower-jaw reference plane

_ANVIL_R = 0.018
_ANVIL_H = 0.010
_ANVIL_Y = 0.0  # the fixed anvil sits on the throat centerline in Y

_SCREW_R = 0.0085  # core radius of the threaded spindle
_THREAD_R = 0.0030  # thread ridge radius
_SCREW_LEN = 0.085  # visible threaded length of the spindle
_BOSS_R = 0.016  # threaded boss on the top arm
_BOSS_H = 0.020
_BORE_EMBED = 0.0006  # bore cut just inside thread crest -> screw-in-boss fit

_COLLAR_R = 0.014
_COLLAR_H = 0.009

# T-bar handle (along X).
_HANDLE_R = 0.0065
_HANDLE_LEN = 0.050  # HALF length of the T-bar along X (full span = 0.10)
_HANDLE_CAP_R = 0.010
_HANDLE_CAP_H = 0.012
_BALL_R = 0.0125
_HUB_R = 0.012
_HUB_H = 0.018

# Butterfly wing (winghandle variant).
_WING_LENGTH = 0.040
_WING_WIDTH = 0.020
_WING_THICK = 0.005

# Side lever (leverhandle variant).
_LEVER_HUB_R = 0.014
_LEVER_HUB_H = 0.016
_LEVER_ARM_R = 0.006
_LEVER_ARM_LEN = 0.072
_LEVER_GRIP_R = 0.010
_LEVER_GRIP_LEN = 0.030
_GRIP_RIDGE_R = 0.0125
_GRIP_RIDGE_W = 0.0025
_GRIP_RIDGE_COUNT = 5

# Swivel / flat pad (foot).
_PAD_R = 0.016
_PAD_H = 0.009
_PAD_NECK_R = 0.007
_PAD_NECK_H = 0.006

# Anvil-disc foot (wide flat pressing disc).
_DISC_R = 0.024
_DISC_H = 0.007
_DISC_HUB_R = 0.012
_DISC_HUB_H = 0.004

_OPEN_GAP = 0.030  # rest throat opening above the anvil


@dataclass(frozen=True)
class ClampConfig:
    frame_silhouette: FrameSilhouette | None = None
    foot: Foot | None = None
    handle: Handle | None = None
    palette_style: PaletteStyle = "red_blue_classic"
    throat_height_scale: float = 1.0
    throat_depth_scale: float = 1.0
    frame_section_scale: float = 1.0
    screw_radius_scale: float = 1.0
    screw_travel_scale: float = 1.0
    pad_radius_scale: float = 1.0
    swivel_range_scale: float = 1.0
    lever_arm_scale: float = 1.0
    lever_open_scale: float = 1.0
    handle_span_scale: float = 1.0
    name: str = "clamp"


@dataclass(frozen=True)
class ResolvedClampConfig:
    frame_silhouette: FrameSilhouette
    foot: Foot
    handle: Handle
    palette_style: PaletteStyle
    # Concrete geometry (scaled / derived).
    frame_depth: float
    frame_bar: float
    throat: float
    throat_y: float
    spine_y: float
    top_arm_z: float
    anvil_r: float
    anvil_h: float
    screw_r: float
    thread_r: float
    screw_len: float
    boss_r: float
    boss_h: float
    bore_r: float
    collar_r: float
    collar_h: float
    handle_len: float
    handle_cap_r: float
    ball_r: float
    hub_r: float
    hub_h: float
    wing_length: float
    lever_arm_len: float
    lever_hub_r: float
    lever_open: float
    pad_r: float
    pad_h: float
    pad_neck_h: float
    disc_r: float
    swivel_lower: float
    swivel_upper: float
    # Derived placement.
    anvil_top_z: float
    rest_tip_z: float  # world Z of the spindle bottom tip at rest (open throat)
    screw_anchor_z: float  # world Z of the frame_to_screw origin (on the boss bore)
    screw_z_shift: float  # offset applied to screw visuals (tip-authored at 0)
    screw_travel: float  # PRISMATIC upper (clamp travel)
    name: str

    @property
    def foot_thickness(self) -> float:
        """Z extent below the screw tip occupied by the foot at rest."""
        if self.foot == "swivel_ball_pad" or self.foot == "fixed_flat_pad":
            return self.pad_neck_h + self.pad_h
        return _DISC_H  # anvil_disc

    @property
    def boss_top_z(self) -> float:
        return self.top_arm_z + self.frame_bar / 2.0 + self.boss_h


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> ClampConfig:
    rng = random.Random(seed)
    return ClampConfig(
        frame_silhouette=rng.choice(FRAME_SILHOUETTES),
        foot=rng.choice(FEET),
        handle=rng.choice(HANDLES),
        palette_style=rng.choice(PALETTE_STYLES),
        throat_height_scale=round(rng.uniform(0.85, 1.20), 4),
        throat_depth_scale=round(rng.uniform(0.85, 1.30), 4),
        frame_section_scale=round(rng.uniform(0.90, 1.15), 4),
        screw_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        screw_travel_scale=round(rng.uniform(0.80, 1.10), 4),
        pad_radius_scale=round(rng.uniform(0.85, 1.20), 4),
        swivel_range_scale=round(rng.uniform(0.80, 1.10), 4),
        lever_arm_scale=round(rng.uniform(0.85, 1.20), 4),
        lever_open_scale=round(rng.uniform(0.80, 1.10), 4),
        handle_span_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_clamp_{seed}",
    )


def resolve_config(config: ClampConfig | None = None) -> ResolvedClampConfig:
    cfg = config or ClampConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    frame_silhouette = _pick(cfg.frame_silhouette, FRAME_SILHOUETTES)
    foot = _pick(cfg.foot, FEET)
    handle = _pick(cfg.handle, HANDLES)

    height_scale = _clamp(cfg.throat_height_scale, 0.85, 1.20)
    depth_scale = _clamp(cfg.throat_depth_scale, 0.85, 1.30)
    section_scale = _clamp(cfg.frame_section_scale, 0.90, 1.15)
    screw_radius_scale = _clamp(cfg.screw_radius_scale, 0.90, 1.12)
    travel_scale = _clamp(cfg.screw_travel_scale, 0.80, 1.10)
    pad_radius_scale = _clamp(cfg.pad_radius_scale, 0.85, 1.20)
    swivel_range_scale = _clamp(cfg.swivel_range_scale, 0.80, 1.10)
    lever_arm_scale = _clamp(cfg.lever_arm_scale, 0.85, 1.20)
    lever_open_scale = _clamp(cfg.lever_open_scale, 0.80, 1.10)
    handle_span_scale = _clamp(cfg.handle_span_scale, 0.85, 1.15)

    # boxy_deep is intrinsically deeper/taller throat (spec §13: keep the deep
    # square silhouette intent, rebased into A coordinates).
    if frame_silhouette == "boxy_deep":
        throat = _THROAT * 1.55 * height_scale
        throat_y = _THROAT_Y * 1.30 * depth_scale
        frame_bar = _FRAME_BAR * 1.10 * section_scale
        frame_depth = _FRAME_DEPTH * section_scale
    else:  # rounded_C
        throat = _THROAT * height_scale
        throat_y = _THROAT_Y * depth_scale
        frame_bar = _FRAME_BAR * section_scale
        frame_depth = _FRAME_DEPTH * section_scale

    spine_y = throat_y / 2.0 + frame_bar / 2.0
    top_arm_z = throat + frame_bar

    screw_r = _SCREW_R * screw_radius_scale
    thread_r = _THREAD_R * screw_radius_scale
    boss_r = max(_BOSS_R, screw_r + thread_r + 0.004)
    # Screw-in-boss interference band (spec §7): bore just inside thread crest.
    bore_r = (screw_r + thread_r) - _BORE_EMBED
    # Screw length scales gently with throat height so the spindle still spans
    # the boss and reaches the throat across the whole height range.
    screw_len = _SCREW_LEN * (0.70 + 0.30 * (top_arm_z / (_THROAT + _FRAME_BAR)))

    # Foot dimensions (conditional baselines, spec §7).
    pad_r = _PAD_R * pad_radius_scale
    disc_r = _DISC_R * pad_radius_scale

    # Anvil placement and rest tip Z (open throat).
    anvil_top_z = _BOTTOM_Z + frame_bar / 2.0 + _ANVIL_H
    open_gap = max(_OPEN_GAP * height_scale, 0.012)  # rest opening positive

    if foot == "swivel_ball_pad" or foot == "fixed_flat_pad":
        foot_thick = _PAD_NECK_H + _PAD_H
    else:  # anvil_disc
        foot_thick = _DISC_H
    rest_foot_bottom_z = anvil_top_z + open_gap
    rest_tip_z = rest_foot_bottom_z + foot_thick

    # frame_to_screw origin sits on REAL frame hardware (the boss bore center),
    # not on the spindle tip floating in the open throat — otherwise the flat
    # 0.015 m articulation-origin baseline FAILs for deep throats (the tip can be
    # >15 mm from the nearest frame geometry). The screw visuals are authored
    # with the tip at part-frame z=0; we shift them by screw_z_shift so the tip
    # lands at world rest_tip_z while the child frame origin sits at the boss.
    boss_bore_center_z = top_arm_z + frame_bar / 2.0 + _BOSS_H / 2.0
    screw_anchor_z = boss_bore_center_z
    screw_z_shift = rest_tip_z - screw_anchor_z

    # Desired clamp travel, bounded so the foot never punches through the anvil
    # (spec §7).
    max_travel = (rest_tip_z - anvil_top_z) - foot_thick - 0.001
    desired_travel = min(0.028 * travel_scale, max(0.006, max_travel))

    # The handle hub / T-bar is WIDER than the boss bore, so as the spindle screws
    # DOWN (positive q) it would otherwise drive the hub straight into the boss /
    # frame top face (genuine 穿模; the thread-through-the-bore is the mechanism,
    # but the over-size hub reaching the frame is not). Only the thread crest
    # threads through the bore; the hub must stay clear of the frame across the
    # WHOLE travel range. Two derived guards (single source, spec §7):
    #   1) lengthen the spindle so the hub starts high enough above the boss to
    #      afford the desired travel plus HUB_FRAME_CLR of standoff, and
    #   2) cap the travel so the descending hub never closes that standoff.
    # Both ends stay >= HUB_FRAME_CLR from the boss top face (rest = highest hub;
    # full clamp = lowest hub).
    HUB_FRAME_CLR = 0.008
    boss_top_z = top_arm_z + frame_bar / 2.0 + _BOSS_H
    min_screw_len = (boss_top_z + desired_travel + HUB_FRAME_CLR) - _COLLAR_H - rest_tip_z
    screw_len = max(screw_len, min_screw_len)

    hub_bottom_rest = rest_tip_z + screw_len + _COLLAR_H
    hub_travel_cap = (hub_bottom_rest - boss_top_z) - HUB_FRAME_CLR
    screw_travel = max(0.006, min(desired_travel, hub_travel_cap))

    swivel_base = 0.30 * swivel_range_scale
    swivel_upper = min(0.35, swivel_base)
    swivel_lower = -swivel_upper

    lever_arm_len = _LEVER_ARM_LEN * lever_arm_scale
    # The side-lever hub is a bearing sleeve on the spindle. The lever rides on the
    # frame while the screw slides through it, so the spindle COLLAR (wider than
    # the core) travels vertically past the lever at some clamp positions. Size the
    # hub beyond the collar and attach the arm root OUTBOARD of the collar radius,
    # so neither the core nor the passing collar ever sweeps through the arm root
    # (genuine 穿模); the sleeve still fully encloses both (bearing seat).
    lever_hub_r = max(_LEVER_HUB_R, _COLLAR_R + 0.006)
    lever_open = _clamp(1.5 * lever_open_scale, 0.8, math.pi * 0.55)

    handle_len = _HANDLE_LEN * handle_span_scale
    wing_length = _WING_LENGTH * handle_span_scale

    return ResolvedClampConfig(
        frame_silhouette=frame_silhouette,
        foot=foot,
        handle=handle,
        palette_style=palette_style,
        frame_depth=frame_depth,
        frame_bar=frame_bar,
        throat=throat,
        throat_y=throat_y,
        spine_y=spine_y,
        top_arm_z=top_arm_z,
        anvil_r=_ANVIL_R,
        anvil_h=_ANVIL_H,
        screw_r=screw_r,
        thread_r=thread_r,
        screw_len=screw_len,
        boss_r=boss_r,
        boss_h=_BOSS_H,
        bore_r=bore_r,
        collar_r=_COLLAR_R,
        collar_h=_COLLAR_H,
        handle_len=handle_len,
        handle_cap_r=_HANDLE_CAP_R,
        ball_r=_BALL_R,
        hub_r=_HUB_R,
        hub_h=_HUB_H,
        wing_length=wing_length,
        lever_arm_len=lever_arm_len,
        lever_hub_r=lever_hub_r,
        lever_open=lever_open,
        pad_r=pad_r,
        pad_h=_PAD_H,
        pad_neck_h=_PAD_NECK_H,
        disc_r=disc_r,
        swivel_lower=swivel_lower,
        swivel_upper=swivel_upper,
        anvil_top_z=anvil_top_z,
        rest_tip_z=rest_tip_z,
        screw_anchor_z=screw_anchor_z,
        screw_z_shift=screw_z_shift,
        screw_travel=screw_travel,
        name=cfg.name or "clamp",
    )


def with_overrides(config: ClampConfig, **kwargs: object) -> ClampConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ClampConfig | ResolvedClampConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedClampConfig) else resolve_config(config)
    return (
        ("frame_silhouette", r.frame_silhouette),
        ("foot", r.foot),
        ("handle", r.handle),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Frame mesh (Slot C). Both silhouettes use the A-family 3-box-union C body so
# they share the unified +Z screw / -Y mouth convention; boxy_deep keeps the
# "deep square throat, almost no fillet" intent from the frame variant.
# ---------------------------------------------------------------------------
def _build_frame_mesh(r: ResolvedClampConfig, *, assets):
    inner_y = -r.throat_y / 2.0
    outer_y = r.spine_y + r.frame_bar / 2.0

    spine_z0 = _BOTTOM_Z - r.frame_bar / 2.0
    spine_z1 = r.top_arm_z + r.frame_bar / 2.0
    spine = (
        cq.Workplane("XY")
        .box(r.frame_depth, r.frame_bar, spine_z1 - spine_z0, centered=(True, True, False))
        .translate((0.0, r.spine_y, spine_z0))
    )
    jaw_len_y = r.spine_y + r.frame_bar / 2.0 - inner_y
    lower = (
        cq.Workplane("XY")
        .box(r.frame_depth, jaw_len_y, r.frame_bar, centered=(True, True, True))
        .translate((0.0, (outer_y + inner_y) / 2.0, _BOTTOM_Z))
    )
    upper = (
        cq.Workplane("XY")
        .box(r.frame_depth, jaw_len_y, r.frame_bar, centered=(True, True, True))
        .translate((0.0, (outer_y + inner_y) / 2.0, r.top_arm_z))
    )
    frame = spine.union(lower).union(upper)

    # rounded_C softens the outer corners; boxy_deep keeps sharp right angles.
    fillet = 0.006 if r.frame_silhouette == "rounded_C" else 0.002
    frame = frame.edges("|X").fillet(fillet)

    # Threaded boss on the upper arm, centered over the throat (Y=ANVIL_Y).
    boss = (
        cq.Workplane("XY")
        .circle(r.boss_r)
        .extrude(r.boss_h)
        .translate((0.0, _ANVIL_Y, r.top_arm_z + r.frame_bar / 2.0))
    )
    frame = frame.union(boss)

    # Through-bore for the screw; just inside the thread crest so the spindle's
    # thread engages the boss wall (screw-in-boss fit, not floating).
    bore = (
        cq.Workplane("XY")
        .circle(r.bore_r)
        .extrude(r.frame_bar + r.boss_h + 0.02)
        .translate((0.0, _ANVIL_Y, r.top_arm_z - r.frame_bar / 2.0 - 0.005))
    )
    frame = frame.cut(bore)
    return mesh_from_cadquery(frame, "frame_body", assets=assets)


def _build_anvil_mesh(r: ResolvedClampConfig, *, assets):
    z0 = _BOTTOM_Z + r.frame_bar / 2.0
    anvil = cq.Workplane("XY").circle(r.anvil_r).extrude(r.anvil_h).translate((0.0, _ANVIL_Y, z0))
    return mesh_from_cadquery(anvil, "anvil_pad", assets=assets)


# ---------------------------------------------------------------------------
# Screw mesh (shared spindle core + collar; the screw part origin is the bottom
# tip, growing +Z). Cylinder@thread_crest (parent-stable; spec §13).
# ---------------------------------------------------------------------------
def _build_screw_core_mesh(r: ResolvedClampConfig, *, assets):
    core = cq.Workplane("XY").circle(r.screw_r + r.thread_r).extrude(r.screw_len)
    return mesh_from_cadquery(core, "screw_core", assets=assets)


def _build_collar_mesh(r: ResolvedClampConfig, *, assets):
    collar = (
        cq.Workplane("XY")
        .polygon(6, r.collar_r * 2.0)
        .extrude(r.collar_h)
        .translate((0.0, 0.0, r.screw_len))
        .edges("|Z")
        .fillet(0.0015)
    )
    return mesh_from_cadquery(collar, "screw_collar", assets=assets)


def _build_hub_mesh(r: ResolvedClampConfig, *, assets):
    hub = (
        cq.Workplane("XY")
        .circle(r.hub_r)
        .extrude(r.hub_h)
        .translate((0.0, 0.0, r.screw_len + r.collar_h))
    )
    return mesh_from_cadquery(hub, "handle_hub", assets=assets)


# ---------------------------------------------------------------------------
# Handle module helpers (Slot B). Non-lever handles are screw visuals.
# ---------------------------------------------------------------------------
def _handle_top_z(r: ResolvedClampConfig) -> float:
    return r.screw_len + r.collar_h + r.hub_h / 2.0


def _build_handle_bar_mesh(r: ResolvedClampConfig, *, assets):
    """Purple horizontal T-bar through the hub, along X (parent A)."""
    z = _handle_top_z(r)
    bar = (
        cq.Workplane("YZ")
        .circle(_HANDLE_R)
        .extrude(r.handle_len, both=True)  # along X (YZ workplane normal = X)
        .translate((0.0, 0.0, z))
    )
    return mesh_from_cadquery(bar, "handle_bar", assets=assets)


def _build_handle_caps_mesh(r: ResolvedClampConfig, *, assets):
    """Two orange rounded end caps on the T-bar (parent A, for sign in (-1,1))."""
    z = _handle_top_z(r)
    caps = None
    for sign in (-1.0, 1.0):
        cap = (
            cq.Workplane("YZ")
            .circle(r.handle_cap_r)
            .extrude(_HANDLE_CAP_H)
            .translate((sign * (r.handle_len - _HANDLE_CAP_H / 2.0), 0.0, z))
            .edges()
            .fillet(0.003)
        )
        caps = cap if caps is None else caps.union(cap)
    return mesh_from_cadquery(caps, "handle_caps", assets=assets)


def _build_tbar_mesh(r: ResolvedClampConfig, *, assets):
    """Chrome T-bar (tommy bar) along X (B rebased from Y to X, spec §13)."""
    z = _handle_top_z(r)
    bar = (
        cq.Workplane("YZ")
        .circle(_HANDLE_R)
        .extrude(r.handle_len, both=True)
        .translate((0.0, 0.0, z))
    )
    return mesh_from_cadquery(bar, "tbar", assets=assets)


# ---------------------------------------------------------------------------
# Side-lever module helpers (Slot B / side_lever).
# ---------------------------------------------------------------------------
def _build_lever_hub_mesh(r: ResolvedClampConfig, *, assets):
    hub = cq.Workplane("XY").circle(r.lever_hub_r).extrude(_LEVER_HUB_H / 2.0, both=True)
    return mesh_from_cadquery(hub, "lever_hub", assets=assets)


def _build_lever_arm_mesh(r: ResolvedClampConfig, *, assets):
    # Attach the arm root OUTBOARD of the spindle collar (the widest thing that
    # slides vertically past the lever as the screw travels) yet inside the
    # widened hub OD, so the arm never sweeps through the core or the passing
    # collar while staying fused to the hub.
    arm_start_x = r.collar_r + 0.002
    arm_length = r.lever_arm_len - arm_start_x
    arm = (
        cq.Workplane("YZ")
        .circle(_LEVER_ARM_R)
        .extrude(arm_length)
        .translate((arm_start_x, 0.0, 0.0))
    )
    return mesh_from_cadquery(arm, "lever_arm", assets=assets)


def _build_lever_grip_mesh(r: ResolvedClampConfig, *, assets):
    grip = (
        cq.Workplane("YZ")
        .circle(_LEVER_GRIP_R)
        .extrude(_LEVER_GRIP_LEN)
        .translate((r.lever_arm_len, 0.0, 0.0))
        .edges()
        .fillet(0.003)
    )
    return mesh_from_cadquery(grip, "lever_grip", assets=assets)


def _build_grip_ridge_mesh(r: ResolvedClampConfig, index: int, *, assets):
    margin = 0.004
    usable = _LEVER_GRIP_LEN - 2.0 * margin
    spacing = usable / (_GRIP_RIDGE_COUNT - 1) if _GRIP_RIDGE_COUNT > 1 else 0.0
    x_center = r.lever_arm_len + margin + index * spacing
    ridge = (
        cq.Workplane("YZ")
        .circle(_GRIP_RIDGE_R)
        .extrude(_GRIP_RIDGE_W)
        .translate((x_center - _GRIP_RIDGE_W / 2.0, 0.0, 0.0))
    )
    return mesh_from_cadquery(ridge, f"grip_ridge_{index}", assets=assets)


# ---------------------------------------------------------------------------
# Foot module helpers (Slot A).
# ---------------------------------------------------------------------------
def _build_pad_mesh(r: ResolvedClampConfig, *, assets):
    """Swivel / flat clamping foot. Origin = swivel center (top of the neck);
    neck reaches up (+Z) to the screw tip, pad disc below (-Z), flat face down."""
    neck = cq.Workplane("XY").circle(_PAD_NECK_R).extrude(r.pad_neck_h)
    pad = cq.Workplane("XY").circle(r.pad_r).extrude(-r.pad_h).edges(">Z or <Z").fillet(0.002)
    return mesh_from_cadquery(neck.union(pad), "swivel_pad", assets=assets)


def _build_pressing_disc_mesh(r: ResolvedClampConfig, *, assets):
    """Broad flat anvil-style pressing disc fixed rigidly to the screw tip.
    Origin = top face of the disc (flush with the spindle tip); disc extends
    downward (-Z) with a small raised hub on top (anvilfoot variant)."""
    disc = cq.Workplane("XY").circle(r.disc_r).extrude(-_DISC_H)
    hub = cq.Workplane("XY").circle(_DISC_HUB_R).extrude(_DISC_HUB_H)
    return mesh_from_cadquery(hub.union(disc), "pressing_disc", assets=assets)


# ---------------------------------------------------------------------------
# Part builders.
# ---------------------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedClampConfig, mats, *, assets):
    frame = model.part("frame")
    frame.visual(_build_frame_mesh(r, assets=assets), material=mats["frame"], name="frame_body", material_class_id=("metal.paint_coated" if r.palette_style in {"red_blue_classic", "cast_iron_steel", "galvanized_industrial", "orange_safety"} else "metal.blackened_gunmetal"))
    frame.visual(_build_anvil_mesh(r, assets=assets), material=mats["steel"], name="anvil_pad", material_class_id="metal.steel_bare")
    frame.inertial = Inertial.from_geometry(
        Box((r.frame_depth, 2.0 * r.spine_y, r.top_arm_z + r.frame_bar)),
        mass=0.55,
        origin=Origin(xyz=(0.0, r.spine_y * 0.4, (r.top_arm_z) / 2.0)),
    )
    return frame


def _emit_screw_and_handle(
    model: ArticulatedObject, r: ResolvedClampConfig, frame, mats, *, assets
) -> list[str]:
    """Emit the screw part (with its non-lever handle visuals + foot visuals),
    the frame_to_screw PRISMATIC, and (for side_lever) the lever part + REVOLUTE.
    Returns the list of emitted part names besides the frame."""
    emitted: list[str] = []
    # The screw mesh helpers author the spindle tip at part-frame z=0 growing
    # +Z. The screw part frame origin is the frame_to_screw joint origin, placed
    # on the boss bore (real frame hardware). dz shifts every screw visual down
    # so the tip lands at the rest open-throat position.
    dz = r.screw_z_shift
    screw = model.part("screw")
    screw.visual(
        _build_screw_core_mesh(r, assets=assets),
        origin=Origin(xyz=(0.0, 0.0, dz)),
        material=mats["screw"],
        name="screw_core", material_class_id=("metal.steel_galvanized" if r.palette_style in {"red_blue_classic", "cast_iron_steel", "galvanized_industrial", "orange_safety"} else "metal.chrome_polished"),
    )
    screw.visual(
        _build_collar_mesh(r, assets=assets),
        origin=Origin(xyz=(0.0, 0.0, dz)),
        material=mats["screw"],
        name="screw_collar", material_class_id=("metal.steel_galvanized" if r.palette_style in {"red_blue_classic", "cast_iron_steel", "galvanized_industrial", "orange_safety"} else "metal.chrome_polished"),
    )

    # --- Handle visuals on the screw (non-lever candidates). ---
    if r.handle in ("tbar_caps", "tbar_balls", "butterfly_wing"):
        screw.visual(
            _build_hub_mesh(r, assets=assets),
            origin=Origin(xyz=(0.0, 0.0, dz)),
            material=mats["handle"],
            name="handle_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"red_blue_classic", "cast_iron_steel", "galvanized_industrial", "orange_safety"} else "metal.chrome_polished"),
        )
    if r.handle == "tbar_caps":
        screw.visual(
            _build_handle_bar_mesh(r, assets=assets),
            origin=Origin(xyz=(0.0, 0.0, dz)),
            material=mats["handle"],
            name="handle_bar", material_class_id=("metal.paint_coated" if r.palette_style in {"red_blue_classic", "cast_iron_steel", "galvanized_industrial", "orange_safety"} else "metal.chrome_polished"),
        )
        screw.visual(
            _build_handle_caps_mesh(r, assets=assets),
            origin=Origin(xyz=(0.0, 0.0, dz)),
            material=mats["accent"],
            name="handle_caps", material_class_id="plastic.opaque_glossy_molded",
        )
    elif r.handle == "tbar_balls":
        screw.visual(
            _build_tbar_mesh(r, assets=assets),
            origin=Origin(xyz=(0.0, 0.0, dz)),
            material=mats["handle"],
            name="tbar", material_class_id="metal.chrome_polished",
        )
        z = _handle_top_z(r) + dz
        for i, sign in enumerate((-1.0, 1.0)):
            screw.visual(
                Sphere(radius=r.ball_r),
                origin=Origin(xyz=(sign * r.handle_len, 0.0, z)),
                material=mats["accent"],
                name=f"ball_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"red_blue_classic", "black_zinc_chrome", "orange_safety"} else "metal.steel_bare"),
            )
    elif r.handle == "butterfly_wing":
        z = _handle_top_z(r) + dz
        for i, sign in enumerate((-1.0, 1.0)):
            screw.visual(
                Box((r.wing_length, _WING_WIDTH, _WING_THICK)),
                origin=Origin(xyz=(sign * r.wing_length / 2.0, 0.0, z)),
                material=mats["accent"],
                name=f"wing_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"red_blue_classic", "black_zinc_chrome", "orange_safety"} else "metal.steel_bare"),
            )
    # side_lever: the screw carries no handle visual (the lever is its own part).

    # --- Foot visuals on the screw (fixed_flat_pad / anvil_disc); swivel_ball_pad
    #     is an independent pad part emitted separately. ---
    if r.foot == "fixed_flat_pad":
        screw.visual(
            _build_pad_mesh(r, assets=assets),
            origin=Origin(xyz=(0.0, 0.0, dz)),
            material=mats["pad"],
            name="swivel_pad", material_class_id="metal.steel_bare",
        )
    elif r.foot == "anvil_disc":
        screw.visual(
            _build_pressing_disc_mesh(r, assets=assets),
            origin=Origin(xyz=(0.0, 0.0, dz)),
            material=mats["steel"],
            name="pressing_disc", material_class_id="metal.steel_bare",
        )

    screw.inertial = Inertial.from_geometry(
        Cylinder(radius=max(r.collar_r, r.hub_r), length=r.screw_len + r.collar_h + r.hub_h),
        mass=0.12,
        origin=Origin(xyz=(0.0, 0.0, dz + r.screw_len / 2.0)),
    )

    # --- frame -> screw PRISMATIC (shared main clamp motion). Origin on the boss
    #     bore (real frame hardware) so the flat 0.015 m baseline holds. ---
    model.articulation(
        "frame_to_screw",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=screw,
        origin=Origin(xyz=(0.0, _ANVIL_Y, r.screw_anchor_z)),
        axis=(0.0, 0.0, -1.0),  # positive q drives the screw DOWN to clamp
        motion_limits=MotionLimits(effort=120.0, velocity=0.05, lower=0.0, upper=r.screw_travel),
    )
    emitted.append("screw")

    # --- side_lever: independent lever part on a REVOLUTE about Z, PARALLEL to
    #     the screw on the frame (lever parent = frame). ---
    if r.handle == "side_lever":
        lever = model.part("lever")
        lever.visual(
            _build_lever_hub_mesh(r, assets=assets), material=mats["handle"], name="lever_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"red_blue_classic", "cast_iron_steel", "galvanized_industrial", "orange_safety"} else "metal.chrome_polished")
        )
        lever.visual(
            _build_lever_arm_mesh(r, assets=assets), material=mats["handle"], name="lever_arm", material_class_id=("metal.paint_coated" if r.palette_style in {"red_blue_classic", "cast_iron_steel", "galvanized_industrial", "orange_safety"} else "metal.chrome_polished")
        )
        lever.visual(
            _build_lever_grip_mesh(r, assets=assets), material=mats["accent"], name="lever_grip", material_class_id="plastic.opaque_glossy_molded"
        )
        for i in range(_GRIP_RIDGE_COUNT):
            lever.visual(
                _build_grip_ridge_mesh(r, i, assets=assets),
                material=mats["ridge"],
                name=f"grip_ridge_{i}", material_class_id="rubber.smooth_plain",
            )
        lever.inertial = Inertial.from_geometry(
            Cylinder(radius=_LEVER_GRIP_R, length=r.lever_arm_len + _LEVER_GRIP_LEN),
            mass=0.04,
            origin=Origin(xyz=(r.lever_arm_len / 2.0, 0.0, 0.0)),
        )
        lever_pivot_z = r.boss_top_z + _LEVER_HUB_H / 2.0
        model.articulation(
            "frame_to_lever",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=lever,
            origin=Origin(xyz=(0.0, _ANVIL_Y, lever_pivot_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=8.0, velocity=4.0, lower=0.0, upper=r.lever_open),
        )
        emitted.append("lever")

    # --- swivel_ball_pad: independent pad part on a REVOLUTE about Y (child of
    #     the screw); pad neck captured into the screw tip. ---
    if r.foot == "swivel_ball_pad":
        pad = model.part("pad")
        pad.visual(_build_pad_mesh(r, assets=assets), material=mats["pad"], name="swivel_pad", material_class_id="metal.steel_bare")
        pad.inertial = Inertial.from_geometry(
            Cylinder(radius=r.pad_r, length=r.pad_neck_h + r.pad_h),
            mass=0.02,
            origin=Origin(xyz=(0.0, 0.0, -r.pad_neck_h)),
        )
        model.articulation(
            "screw_to_pad",
            ArticulationType.REVOLUTE,
            parent=screw,
            child=pad,
            # Swivel center just below the spindle tip (tip is at part-frame z=dz).
            origin=Origin(xyz=(0.0, 0.0, dz - r.pad_neck_h)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(
                effort=2.0, velocity=2.0, lower=r.swivel_lower, upper=r.swivel_upper
            ),
        )
        emitted.append("pad")

    return emitted


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_clamp(
    config: ClampConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"clamp_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    frame = _build_frame(model, r, mats, assets=assets)
    _emit_screw_and_handle(model, r, frame, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_clamp(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_clamp(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_clamp_tests(
    object_model: ArticulatedObject,
    config: ClampConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    screw = object_model.get_part("screw")

    # ---- Captured-pin / threaded-fit allowances (element-scoped). ----
    ctx.allow_overlap(
        screw,
        frame,
        elem_a="screw_core",
        elem_b="frame_body",
        reason="The spindle thread crest engages (threads into) the boss bore (screw-in-boss fit).",
    )
    ctx.allow_overlap(
        screw,
        frame,
        elem_a="screw_collar",
        elem_b="frame_body",
        reason="The collar nut rides into the threaded boss top (screw-in-boss fit).",
    )
    if r.handle == "tbar_balls":
        for i in range(2):
            ctx.allow_overlap(
                screw,
                screw,
                elem_a=f"ball_{i}",
                elem_b="tbar",
                reason="The ball end is seated on the end of the tommy bar.",
            )
    elif r.handle == "butterfly_wing":
        for i in range(2):
            ctx.allow_overlap(
                screw,
                screw,
                elem_a=f"wing_{i}",
                elem_b="handle_hub",
                reason="The butterfly wing root embeds into the hub (cast integral).",
            )
    elif r.handle == "side_lever":
        lever = object_model.get_part("lever")
        ctx.allow_overlap(
            screw,
            lever,
            elem_a="screw_core",
            elem_b="lever_hub",
            reason="The screw spindle passes through the lever hub bore (bearing seat).",
        )
        ctx.allow_overlap(
            screw,
            lever,
            elem_a="screw_collar",
            elem_b="lever_hub",
            reason="The screw collar sits inside the lever hub bore at the boss top.",
        )
    if r.foot == "swivel_ball_pad":
        pad = object_model.get_part("pad")
        ctx.allow_overlap(
            pad,
            screw,
            elem_a="swivel_pad",
            elem_b="screw_core",
            reason="The swivel pad neck is captured on the spindle tip.",
        )
    elif r.foot == "fixed_flat_pad":
        ctx.allow_overlap(
            screw,
            screw,
            elem_a="swivel_pad",
            elem_b="screw_core",
            reason="The fixed pad neck is captured on the spindle tip.",
        )
    elif r.foot == "anvil_disc":
        ctx.allow_overlap(
            screw,
            screw,
            elem_a="pressing_disc",
            elem_b="screw_core",
            reason="The pressing-disc hub is captured on the spindle tip.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- Single root + shared PRISMATIC clamp motion (all candidates). ----
    roots = object_model.root_parts()
    ctx.check(
        "frame is the single root",
        len(roots) == 1 and roots[0].name == "frame",
        details=f"roots={[p.name for p in roots]}",
    )
    prismatic = object_model.get_articulation("frame_to_screw")
    ctx.check(
        "frame_to_screw is PRISMATIC about the vertical axis",
        prismatic.articulation_type == ArticulationType.PRISMATIC
        and abs(prismatic.axis[2]) > 0.99
        and abs(prismatic.axis[0]) < 1e-6
        and abs(prismatic.axis[1]) < 1e-6,
        details=f"type={prismatic.articulation_type} axis={tuple(prismatic.axis)}",
    )

    # ---- Foot joint topology. ----
    part_names = {p.name for p in object_model.parts}
    articulation_names = {a.name for a in object_model.articulations}
    if r.foot == "swivel_ball_pad":
        ctx.check(
            "swivel pad is an independent part",
            "pad" in part_names,
            details=str(sorted(part_names)),
        )
        swivel = object_model.get_articulation("screw_to_pad")
        ctx.check(
            "screw_to_pad is REVOLUTE about Y",
            swivel.articulation_type == ArticulationType.REVOLUTE and abs(swivel.axis[1]) > 0.99,
            details=f"type={swivel.articulation_type} axis={tuple(swivel.axis)}",
        )
    else:
        # fixed_flat_pad / anvil_disc: foot is a screw visual, no joint, no part.
        ctx.check(
            "no swivel joint for fixed foot",
            "screw_to_pad" not in articulation_names,
            details=str(sorted(articulation_names)),
        )
        ctx.check(
            "no separate pad part for fixed foot",
            "pad" not in part_names,
            details=str(sorted(part_names)),
        )

    # ---- Handle joint topology. ----
    if r.handle == "side_lever":
        ctx.check(
            "side lever is an independent part",
            "lever" in part_names,
            details=str(sorted(part_names)),
        )
        lever_joint = object_model.get_articulation("frame_to_lever")
        ctx.check(
            "frame_to_lever is REVOLUTE about Z, parented to the frame",
            lever_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(lever_joint.axis[2]) > 0.99
            and lever_joint.parent == "frame",
            details=f"type={lever_joint.articulation_type} axis={tuple(lever_joint.axis)} parent={lever_joint.parent}",
        )
        ctx.check(
            "screw is parented to the frame",
            prismatic.parent == "frame",
            details=f"parent={prismatic.parent}",
        )
        ridges = [
            v.name
            for v in object_model.get_part("lever").visuals
            if v.name.startswith("grip_ridge_")
        ]
        ctx.check(
            "lever has 5 grip ridges",
            len(ridges) == _GRIP_RIDGE_COUNT,
            details=f"ridges={sorted(ridges)}",
        )
    else:
        ctx.check(
            "no lever joint for non-lever handle",
            "frame_to_lever" not in articulation_names,
            details=str(sorted(articulation_names)),
        )
        ctx.check(
            "no separate lever part for non-lever handle",
            "lever" not in part_names,
            details=str(sorted(part_names)),
        )

    # ---- Frame identity: spans the full clamp height (open C). ----
    frame_aabb = ctx.part_world_aabb(frame)
    if frame_aabb is not None:
        (fx0, fy0, fz0), (fx1, fy1, fz1) = frame_aabb
        ctx.check(
            "frame spans the full clamp height",
            (fz1 - fz0) > r.throat,
            details=f"frame z-span={fz1 - fz0:.4f} throat={r.throat:.4f}",
        )
        if r.frame_silhouette == "boxy_deep":
            ctx.check(
                "boxy_deep frame is tall (deep throat)",
                (fz1 - fz0) > 0.110,
                details=f"frame z-span={fz1 - fz0:.4f}",
            )

    # ---- Handle silhouette identity. ----
    if r.handle in ("tbar_caps", "tbar_balls"):
        bar_elem = "handle_bar" if r.handle == "tbar_caps" else "tbar"
        bar_aabb = ctx.part_element_world_aabb(screw, elem=bar_elem)
        if bar_aabb is not None:
            (bx0, by0, bz0), (bx1, by1, bz1) = bar_aabb
            ctx.check(
                "T-bar is long along X and above the frame top",
                (bx1 - bx0) > 0.06 and (bx1 - bx0) > (by1 - by0) * 3.0 and bz0 > r.top_arm_z,
                details=f"x-span={bx1 - bx0:.4f} y-span={by1 - by0:.4f} z0={bz0:.4f}",
            )
    elif r.handle == "butterfly_wing":
        w0 = ctx.part_element_world_aabb(screw, elem="wing_0")
        w1 = ctx.part_element_world_aabb(screw, elem="wing_1")
        if w0 is not None and w1 is not None:
            combined_x = max(w0[1][0], w1[1][0]) - min(w0[0][0], w1[0][0])
            ctx.check(
                "butterfly wings span wide along X, above the frame top",
                combined_x > 0.06 and min(w0[0][2], w1[0][2]) > r.top_arm_z,
                details=f"combined_x={combined_x:.4f}",
            )

    # ---- Rest pose: clamp throat is OPEN (foot hovers above the anvil). ----
    foot_part = object_model.get_part("pad") if r.foot == "swivel_ball_pad" else screw
    foot_elem = (
        "swivel_pad"
        if r.foot in ("swivel_ball_pad", "fixed_flat_pad")
        else ("pressing_disc" if r.foot == "anvil_disc" else "swivel_pad")
    )
    rest_foot = ctx.part_element_world_aabb(foot_part, elem=foot_elem)
    if rest_foot is not None:
        ctx.check(
            "rest clamp throat is open above the anvil",
            rest_foot[0][2] > r.anvil_top_z + 0.008,
            details=f"foot_bottom={rest_foot[0][2]:.4f} anvil_top={r.anvil_top_z:.4f}",
        )

    # ---- Mechanism: advancing the screw drives the foot DOWN to clamp. ----
    p0 = ctx.part_world_position(screw)
    with ctx.pose({prismatic: r.screw_travel}):
        p1 = ctx.part_world_position(screw)
        hub_full = (
            ctx.part_element_world_aabb(screw, elem="handle_hub")
            if r.handle in ("tbar_caps", "tbar_balls", "butterfly_wing")
            else None
        )
    if p0 is not None and p1 is not None:
        ctx.check(
            "advancing the screw drives the foot down to clamp",
            p1[2] < p0[2] - 0.5 * r.screw_travel,
            details=f"rest_z={p0[2]:.4f} clamped_z={p1[2]:.4f} travel={r.screw_travel:.4f}",
        )

    # ---- Handle hub (wider than the boss bore) stays clear of the frame across
    #      the whole travel: worst case is full clamp (lowest hub). ----
    if hub_full is not None:
        ctx.check(
            "handle hub stops clear of the frame boss at full clamp",
            hub_full[0][2] > r.boss_top_z + 0.006,
            details=f"hub_bottom={hub_full[0][2]:.4f} boss_top={r.boss_top_z:.4f}",
        )

    # ---- Side lever: the arm root must attach OUTBOARD of the spindle core so it
    #      never sweeps through the core as the lever turns. ----
    if r.handle == "side_lever":
        core_r = r.screw_r + r.thread_r
        arm_root_r = r.collar_r + 0.002
        ctx.check(
            "lever arm root clears the core and the passing collar, inside the hub",
            arm_root_r > core_r and arm_root_r > r.collar_r and r.lever_hub_r > arm_root_r,
            details=f"arm_root_r={arm_root_r:.4f} core_r={core_r:.4f} "
            f"collar_r={r.collar_r:.4f} lever_hub_r={r.lever_hub_r:.4f}",
        )

    return ctx.report()


__all__ = (
    "ClampConfig",
    "ResolvedClampConfig",
    "build_clamp",
    "build_seeded_clamp",
    "config_from_seed",
    "resolve_config",
    "run_clamp_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
