# SPDX-License-Identifier: Apache-2.0

"""CD jewel case modular template.

A flat rectangular CD jewel case that holds at least one 120 mm disc
(``DISC_R = 0.060``), with an opening mechanism and a disc-holding mechanism.

Pattern = ``mixed``: a root chassis (the clear rigid ``base`` shell, or the
opaque digipak ``tray_panel``) carries three replaceable layers plus one
multiplicity axis:

  * ``body_type`` (4): standard_rigid / slimline / doublewide / digipak.
    ``digipak`` is a full root replacement (opaque card book-fold, coupled
    ``spine_fold`` closure + native center-hub disc tray).
  * ``closure_hinge`` (3 samplable): clamshell_swing (REVOLUTE +X) /
    topflip (REVOLUTE +Y) / slidingsleeve (PRISMATIC +X).  digipak overrides
    this with the coupled ``spine_fold`` (REVOLUTE +Y).
  * ``inner_tray`` (4): center_hub (CONTINUOUS spin disc) / trayless (disc
    fixed flat in a pocket, N=1) / dualsided_flip (extra REVOLUTE flip tray,
    disc spins on it) / bookletclip (center hub + lid-mounted booklet clips).
  * ``disc_count`` N in [1, 6]: a multiplicity axis with two copy-logics —
    coplanar side-by-side (N=2) and stacked book leaves (N>=3).

Adopted module sources (all 5-star, synced under ``data/records/``):
  S1 parent ``rec_clear-plastic-cd-jewel-case-...61eddc85`` (standard / clamshell
  / center_hub / N=1 baseline), S2 slimline, S3 doublewide, S4 digipak (spine
  fold), S5 topflip, S6 slidingsleeve, S7 trayless, S8 dualsided_flip, S9
  bookletclip, S10 coplanar N=2, S11 booklet leaves N=4.

The case is largely CLEAR/translucent: the base/lid/sleeve shells are open
hollow CAD shells (``outer.cut(inner)``, correct normals) so the cavity reads
genuinely open; the disc tray is a thin floor + a raised hub that never seals
the cavity (cf. the hollow-shell-reads-solid pitfall).

Per-seed colorway diversity is driven by ``palette_style`` (6 colorways from
spec section 7): only clear-shell roles take alpha < 1; the digipak card and
the trayless paper pocket are always opaque.
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot enumerations
# ---------------------------------------------------------------------------
BodyType = Literal["standard_rigid", "slimline", "doublewide", "digipak"]
ClosureHinge = Literal["clamshell_swing", "topflip", "slidingsleeve"]
InnerTray = Literal["center_hub", "trayless", "dualsided_flip", "bookletclip"]
PaletteStyle = Literal[
    "clear_frame_black_tray",
    "clear_frame_white_tray",
    "frosted_grey",
    "smoked_tint_black",
    "opaque_coloured_card",
    "translucent_colour_tray",
]

BODY_TYPES: tuple[BodyType, ...] = ("standard_rigid", "slimline", "doublewide", "digipak")
CLOSURE_HINGES: tuple[ClosureHinge, ...] = ("clamshell_swing", "topflip", "slidingsleeve")
INNER_TRAYS: tuple[InnerTray, ...] = ("center_hub", "trayless", "dualsided_flip", "bookletclip")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "clear_frame_black_tray",
    "clear_frame_white_tray",
    "frosted_grey",
    "smoked_tint_black",
    "opaque_coloured_card",
    "translucent_colour_tray",
)

# Sampling weights (spec section 8). slimline + digipak each collapse to a
# single topology tuple, so they are kept rare; the variety-rich rigid bodies
# (standard_rigid / doublewide) carry the topology diversity.
BODY_WEIGHTS = (0.55, 0.07, 0.30, 0.08)
CLOSURE_WEIGHTS = (0.40, 0.34, 0.26)
TRAY_WEIGHTS = (0.40, 0.22, 0.20, 0.18)
DISC_COUNT_VALUES = (1, 2, 3, 4, 5, 6)
DISC_COUNT_WEIGHTS = (0.46, 0.26, 0.10, 0.10, 0.04, 0.04)

N_MIN = 1
N_MAX = 6

# ---------------------------------------------------------------------------
# Real-world base dimensions (meters). Identity-locked: DISC_R == 0.060 (120 mm
# CD), never sampled. Footprint is derived from the disc radius + margins.
# ---------------------------------------------------------------------------
DISC_R = 0.060
DISC_T = 0.0012
DISC_HOLE_R = 0.0075
DISC_MARKER_R = 0.004
DISC_MARKER_X = 0.030

HUB_R0 = 0.009
HUB_H0 = 0.006
N_TEETH = 8
TOOTH_OFFSET = 0.0015
TOOTH_R = 0.0016

WALL = 0.0018
BASE_FLOOR_T0 = 0.003
FLOOR_T = 0.0022
LID_T = 0.004
LID_WALL = 0.0016

MARGIN_X0 = 0.0095
MARGIN_Y0 = 0.0040
MARGIN_X_MIN, MARGIN_X_MAX = 0.0060, 0.0150
MARGIN_Y_MIN, MARGIN_Y_MAX = 0.0035, 0.0090

DISC_CLEAR = 0.0016  # vertical clearance between top content and the lid cavity

NOTCH_R = 0.013
NOTCH_DX = 0.026

# leaf (booklet) parameters
LEAF_T = 0.0015
BARREL_R = 0.0018
BARREL_W = 0.028

# dual-sided flip tray
TRAY_PANEL_T = 0.002
PIVOT_PIN_R = 0.0015
PIVOT_PIN_L = 0.003
POST_W = 0.006
POST_D = 0.008

# sliding sleeve
SLEEVE_CLEAR = 0.0014
SLEEVE_WALL = 0.0020

# trayless pocket
SLEEVE_SHEET = 0.0008

# booklet clip
CLIP_H = 0.0032
CLIP_W = 0.016
CLIP_WALL_T = 0.0018
CLIP_LIP_EXT = 0.0035
CLIP_LIP_T = 0.0012
BOOKLET_W = 0.112
BOOKLET_D = 0.100
BOOKLET_T = 0.0010

# slimline
SLIM_BASE_T = 0.0010
SLIM_COVER_T = 0.0010
SLIM_TRAY_T = 0.0008
SLIM_HUB_H = 0.0022
SLIM_LID_WALL = 0.0010

# digipak
PANEL_T = 0.0025
SPINE_W = 0.0080

LID_OPEN_DEG0 = 70.0
SPINE_OPEN_DEG0 = 170.0

# ---------------------------------------------------------------------------
# Palette: role -> rgba. Only the "shell" role is translucent (alpha < 0.6);
# "card"/"cover"/"pocket"/"booklet" are always opaque (alpha == 1).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "clear_frame_black_tray": {
        "shell": (0.55, 0.60, 0.68, 0.30),
        "tray": (0.10, 0.10, 0.12, 1.0),
        "disc": (0.80, 0.82, 0.85, 1.0),
        "pocket": (0.92, 0.88, 0.82, 1.0),
        "booklet": (0.95, 0.93, 0.88, 1.0),
        "card": (0.76, 0.70, 0.58, 1.0),
        "cover": (0.22, 0.26, 0.36, 1.0),
    },
    "clear_frame_white_tray": {
        "shell": (0.55, 0.60, 0.68, 0.30),
        "tray": (0.86, 0.87, 0.90, 1.0),
        "disc": (0.80, 0.82, 0.85, 1.0),
        "pocket": (0.94, 0.92, 0.88, 1.0),
        "booklet": (0.97, 0.96, 0.92, 1.0),
        "card": (0.80, 0.76, 0.66, 1.0),
        "cover": (0.30, 0.34, 0.42, 1.0),
    },
    "frosted_grey": {
        "shell": (0.70, 0.72, 0.74, 0.45),
        "tray": (0.45, 0.45, 0.48, 1.0),
        "disc": (0.80, 0.82, 0.85, 1.0),
        "pocket": (0.88, 0.88, 0.86, 1.0),
        "booklet": (0.92, 0.92, 0.90, 1.0),
        "card": (0.70, 0.70, 0.68, 1.0),
        "cover": (0.40, 0.42, 0.46, 1.0),
    },
    "smoked_tint_black": {
        "shell": (0.20, 0.20, 0.24, 0.42),
        "tray": (0.10, 0.10, 0.12, 1.0),
        "disc": (0.80, 0.82, 0.85, 1.0),
        "pocket": (0.32, 0.32, 0.34, 1.0),
        "booklet": (0.40, 0.40, 0.42, 1.0),
        "card": (0.24, 0.24, 0.28, 1.0),
        "cover": (0.14, 0.14, 0.18, 1.0),
    },
    "opaque_coloured_card": {
        "shell": (0.30, 0.14, 0.14, 0.42),
        "tray": (0.10, 0.10, 0.12, 1.0),
        "disc": (0.80, 0.82, 0.85, 1.0),
        "pocket": (0.55, 0.30, 0.28, 1.0),
        "booklet": (0.92, 0.86, 0.80, 1.0),
        "card": (0.50, 0.14, 0.14, 1.0),
        "cover": (0.20, 0.24, 0.34, 1.0),
    },
    "translucent_colour_tray": {
        "shell": (0.42, 0.54, 0.68, 0.34),
        "tray": (0.20, 0.35, 0.62, 0.62),
        "disc": (0.80, 0.82, 0.85, 1.0),
        "pocket": (0.80, 0.86, 0.92, 1.0),
        "booklet": (0.90, 0.93, 0.96, 1.0),
        "card": (0.30, 0.42, 0.62, 1.0),
        "cover": (0.18, 0.30, 0.52, 1.0),
    },
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CdJewelCaseConfig:
    body_type: BodyType | None = None
    closure_hinge: ClosureHinge | None = None
    inner_tray: InnerTray | None = None
    disc_count: int | None = None
    palette_style: PaletteStyle = "clear_frame_black_tray"
    case_margin_scale: float = 1.0
    case_height_scale: float = 1.0
    hub_radius_scale: float = 1.0
    lid_open_scale: float = 1.0
    name: str = "cd_jewel_case"


@dataclass(frozen=True)
class ResolvedCdJewelCaseConfig:
    body_type: BodyType
    closure_hinge: str  # samplable closure or "spine_fold" (digipak coupled)
    inner_tray: InnerTray
    disc_count: int
    palette_style: PaletteStyle
    disc_logic: (
        str  # center_single / coplanar / booklet / trayless / dualsided / slimline / digipak
    )
    # rigid footprint
    n_slots: int
    hub_xs: tuple[float, ...]
    disc_slot_indices: tuple[int, ...]
    slot_pitch: float
    case_w: float
    case_d: float
    wall: float
    base_floor_t: float
    floor_t: float
    hub_r: float
    hub_h: float
    frame_h: float
    hinge_z: float
    disc_seat_z: float
    lid_open: float
    spine_open: float
    sleeve_travel: float
    # booklet
    leaf_first_z: float
    leaf_spacing: float
    leaf_w: float
    leaf_d: float
    # dual-sided
    pivot_z: float
    post_top: float
    tray_w: float
    tray_d: float
    # slimline
    slim_hinge_z: float
    slim_lid_depth: float
    slim_disc_z_local: float
    # digipak
    panel_w: float
    tray_board_w: float
    tray_board_d: float
    tray_center_x: float
    disc_seat_z_dp: float
    name: str


def config_from_seed(seed: int) -> CdJewelCaseConfig:
    rng = random.Random(seed)
    return CdJewelCaseConfig(
        body_type=rng.choices(BODY_TYPES, weights=BODY_WEIGHTS, k=1)[0],
        closure_hinge=rng.choices(CLOSURE_HINGES, weights=CLOSURE_WEIGHTS, k=1)[0],
        inner_tray=rng.choices(INNER_TRAYS, weights=TRAY_WEIGHTS, k=1)[0],
        disc_count=rng.choices(DISC_COUNT_VALUES, weights=DISC_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        case_margin_scale=round(rng.uniform(0.90, 1.30), 4),
        case_height_scale=round(rng.uniform(0.85, 1.25), 4),
        hub_radius_scale=round(rng.uniform(0.92, 1.12), 4),
        lid_open_scale=round(rng.uniform(0.88, 1.18), 4),
        name=f"seeded_cd_jewel_case_{seed}",
    )


def resolve_config(config: CdJewelCaseConfig | None = None) -> ResolvedCdJewelCaseConfig:
    cfg = config or CdJewelCaseConfig()
    palette = _pick(cfg.palette_style, PALETTE_STYLES)
    body = _pick(cfg.body_type, BODY_TYPES)
    closure: str = _pick(cfg.closure_hinge, CLOSURE_HINGES)
    tray = _pick(cfg.inner_tray, INNER_TRAYS)
    n = int(_clamp(int(cfg.disc_count) if cfg.disc_count else 1, N_MIN, N_MAX))

    # ---- compatibility gating (spec section 9) ----
    if body == "digipak":
        closure = "spine_fold"
        tray = "center_hub"
        n = 1
    elif body == "slimline":
        closure = "clamshell_swing"
        tray = "center_hub"
        n = 1
    else:  # standard_rigid / doublewide
        if closure == "slidingsleeve" and tray in ("dualsided_flip", "bookletclip"):
            tray = "center_hub"
        if tray in ("dualsided_flip", "bookletclip"):
            if closure not in ("clamshell_swing", "topflip"):
                tray = "center_hub"
            else:
                n = 1
        if tray == "trayless":
            n = 1
        if tray == "center_hub":
            if n == 2:
                if closure != "clamshell_swing":
                    n = 1
            elif n >= 3:
                if not (body == "standard_rigid" and closure == "clamshell_swing"):
                    n = 1

    # ---- disc-logic ----
    if body == "digipak":
        disc_logic = "digipak"
    elif body == "slimline":
        disc_logic = "slimline"
    elif tray == "trayless":
        disc_logic = "trayless"
    elif tray == "dualsided_flip":
        disc_logic = "dualsided"
    elif tray == "bookletclip":
        disc_logic = "center_single"
    else:  # center_hub
        disc_logic = "center_single" if n == 1 else ("coplanar" if n == 2 else "booklet")

    # ---- continuous scales ----
    margin_scale = _clamp(cfg.case_margin_scale, 0.90, 1.30)
    height_scale = _clamp(cfg.case_height_scale, 0.85, 1.25)
    hub_scale = _clamp(cfg.hub_radius_scale, 0.92, 1.12)
    open_scale = _clamp(cfg.lid_open_scale, 0.88, 1.18)

    margin_x = _clamp(MARGIN_X0 * margin_scale, MARGIN_X_MIN, MARGIN_X_MAX)
    margin_y = _clamp(MARGIN_Y0 * margin_scale, MARGIN_Y_MIN, MARGIN_Y_MAX)

    hub_r = _clamp(HUB_R0 * hub_scale, DISC_HOLE_R + 0.0006, DISC_HOLE_R + 0.0035)
    hub_h = _clamp(HUB_H0 * height_scale, 0.0040, 0.0090)
    base_floor_t = _clamp(BASE_FLOOR_T0 * height_scale, 0.0020, 0.0050)
    floor_t = FLOOR_T

    # ---- footprint ----
    slot_pitch = 2.0 * (DISC_R + margin_x)
    if body == "doublewide":
        n_slots = 2
        disc_slot_indices = (1,) if n == 1 else (0, 1)
    elif disc_logic == "coplanar":
        n_slots = 2
        disc_slot_indices = (0, 1)
    else:
        n_slots = 1
        disc_slot_indices = (0,)
    hub_xs = tuple((i - (n_slots - 1) / 2.0) * slot_pitch for i in range(n_slots))
    case_w = n_slots * slot_pitch + 2.0 * WALL
    case_d = 2.0 * (DISC_R + margin_y) + 2.0 * WALL

    disc_seat_z = base_floor_t + floor_t + hub_h * 0.7

    # ---- frame height by disc-logic ----
    leaf_first_z = base_floor_t + 0.0020
    leaf_spacing = max(hub_h + LEAF_T + DISC_T + 0.0015, 0.0085)
    leaf_w = case_w - 2.0 * WALL - 0.0020
    leaf_d = case_d - 2.0 * WALL - 0.0020

    pivot_z = base_floor_t + hub_h + TRAY_PANEL_T / 2.0 + 0.0020
    post_top = pivot_z + PIVOT_PIN_R + 0.0020
    tray_w = case_w - 2.0 * WALL - 0.0020
    tray_d = case_d - 2.0 * WALL - 0.0060

    if disc_logic == "booklet":
        content_top = leaf_first_z + (n - 1) * leaf_spacing + LEAF_T + hub_h + DISC_T
    elif disc_logic == "dualsided":
        content_top = pivot_z + TRAY_PANEL_T / 2.0 + hub_h
    elif disc_logic == "trayless":
        content_top = base_floor_t + 2.0 * SLEEVE_SHEET + DISC_T + 0.0010
    else:  # center_single / coplanar
        content_top = base_floor_t + floor_t + hub_h
    frame_h = content_top + DISC_CLEAR
    hinge_z = frame_h

    lid_open = _clamp(
        math.radians(LID_OPEN_DEG0 * open_scale), math.radians(60.0), math.radians(85.0)
    )
    spine_open = _clamp(
        math.radians(SPINE_OPEN_DEG0 * open_scale), math.radians(150.0), math.radians(175.0)
    )
    sleeve_travel = case_w - 0.040

    # ---- slimline ----
    slim_lid_depth = SLIM_COVER_T + SLIM_TRAY_T + SLIM_HUB_H
    slim_hinge_z = SLIM_BASE_T + slim_lid_depth
    slim_disc_z_local = -(SLIM_COVER_T + SLIM_TRAY_T + SLIM_HUB_H * 0.7)

    # ---- digipak ----
    panel_w = case_w - SPINE_W
    tray_board_w = panel_w - 0.010
    tray_board_d = case_d - 0.010
    tray_center_x = SPINE_W + panel_w / 2.0
    disc_seat_z_dp = PANEL_T + floor_t + hub_h * 0.7

    return ResolvedCdJewelCaseConfig(
        body_type=body,
        closure_hinge=closure,
        inner_tray=tray,
        disc_count=n,
        palette_style=palette,
        disc_logic=disc_logic,
        n_slots=n_slots,
        hub_xs=hub_xs,
        disc_slot_indices=disc_slot_indices,
        slot_pitch=slot_pitch,
        case_w=case_w,
        case_d=case_d,
        wall=WALL,
        base_floor_t=base_floor_t,
        floor_t=floor_t,
        hub_r=hub_r,
        hub_h=hub_h,
        frame_h=frame_h,
        hinge_z=hinge_z,
        disc_seat_z=disc_seat_z,
        lid_open=lid_open,
        spine_open=spine_open,
        sleeve_travel=sleeve_travel,
        leaf_first_z=leaf_first_z,
        leaf_spacing=leaf_spacing,
        leaf_w=leaf_w,
        leaf_d=leaf_d,
        pivot_z=pivot_z,
        post_top=post_top,
        tray_w=tray_w,
        tray_d=tray_d,
        slim_hinge_z=slim_hinge_z,
        slim_lid_depth=slim_lid_depth,
        slim_disc_z_local=slim_disc_z_local,
        panel_w=panel_w,
        tray_board_w=tray_board_w,
        tray_board_d=tray_board_d,
        tray_center_x=tray_center_x,
        disc_seat_z_dp=disc_seat_z_dp,
        name=cfg.name or "cd_jewel_case",
    )


def with_overrides(config: CdJewelCaseConfig, **kwargs: object) -> CdJewelCaseConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: CdJewelCaseConfig | ResolvedCdJewelCaseConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCdJewelCaseConfig) else resolve_config(config)
    return (
        ("body_type", r.body_type),
        ("closure_hinge", r.closure_hinge),
        ("inner_tray", r.inner_tray),
        ("disc_count", f"n{r.disc_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# CadQuery geometry helpers
# ---------------------------------------------------------------------------
def _mesh(geom, name, assets):
    return mesh_from_cadquery(geom, name, assets=assets)


def _open_top_shell(w: float, d: float, floor_t: float, wall: float, height: float) -> cq.Workplane:
    """Open-topped rectangular shell with a floor + 4 walls (correct normals)."""
    outer = cq.Workplane("XY").box(w, d, height, centered=(True, True, False))
    inner = (
        cq.Workplane("XY")
        .workplane(offset=floor_t)
        .box(w - 2 * wall, d - 2 * wall, height, centered=(True, True, False))
    )
    return outer.cut(inner)


def _hub_rosette(cx: float, cy: float, z0: float, hub_r: float, hub_h: float) -> cq.Workplane:
    """Raised hub boss + 8 rosette teeth, base at z0, around (cx, cy)."""
    hub = cq.Workplane("XY").workplane(offset=z0).moveTo(cx, cy).circle(hub_r).extrude(hub_h)
    for i in range(N_TEETH):
        a = 2.0 * math.pi * i / N_TEETH
        tx = cx + (hub_r + TOOTH_OFFSET) * math.cos(a)
        ty = cy + (hub_r + TOOTH_OFFSET) * math.sin(a)
        hub = hub.union(
            cq.Workplane("XY")
            .workplane(offset=z0)
            .moveTo(tx, ty)
            .circle(TOOTH_R)
            .extrude(hub_h * 0.7)
        )
    return hub


def _center_tray(r: ResolvedCdJewelCaseConfig) -> cq.Workplane:
    """Dark inner tray: thin floor + a hub/rosette per slot + front notches."""
    tw = r.case_w - 2 * r.wall + 0.0008
    td = r.case_d - 2 * r.wall + 0.0008
    floor_z = r.base_floor_t
    tray = (
        cq.Workplane("XY")
        .workplane(offset=floor_z)
        .box(tw, td, r.floor_t, centered=(True, True, False))
    )
    for cx in r.hub_xs:
        tray = tray.union(_hub_rosette(cx, 0.0, floor_z + r.floor_t, r.hub_r, r.hub_h))
        notch = cq.Workplane("XY").workplane(offset=floor_z - 0.001)
        for dx in (-NOTCH_DX, NOTCH_DX):
            notch = notch.moveTo(cx + dx, -td / 2.0).circle(NOTCH_R)
        tray = tray.cut(notch.extrude(r.floor_t + 0.003))
    return tray


def _disc_solid(disc_r: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .circle(disc_r)
        .extrude(DISC_T)
        .faces(">Z")
        .workplane()
        .hole(DISC_HOLE_R * 2.0)
    )


def _lid_cap_rear(w: float, d: float) -> cq.Workplane:
    """Clear lid cap, hinge at the rear-top corner (local origin), body to -Y,
    cavity open downward. World z spans 0..LID_T above the hinge."""
    outer = (
        cq.Workplane("XY")
        .box(w, d, LID_T, centered=(True, True, False))
        .translate((0.0, -d / 2.0, 0.0))
    )
    inner = (
        cq.Workplane("XY")
        .box(w - 2 * LID_WALL, d - 2 * LID_WALL, LID_T - LID_WALL, centered=(True, True, False))
        .translate((0.0, -d / 2.0, 0.0))
    )
    return outer.cut(inner)


def _lid_cap_side(w: float, d: float) -> cq.Workplane:
    """Clear lid cap, hinge at the +X short-side edge (local origin), body to -X."""
    outer = (
        cq.Workplane("XY")
        .box(w, d, LID_T, centered=(True, True, False))
        .translate((-w / 2.0, 0.0, 0.0))
    )
    inner = (
        cq.Workplane("XY")
        .box(w - 2 * LID_WALL, d - 2 * LID_WALL, LID_T - LID_WALL, centered=(True, True, False))
        .translate((-w / 2.0, 0.0, 0.0))
    )
    return outer.cut(inner)


# ---------------------------------------------------------------------------
# Closure builders (lid / sleeve). All hinge at hinge_z = frame_h (lid caps top).
# ---------------------------------------------------------------------------
def _emit_clamshell(model, r, base, mats, *, assets, extra=None):
    lid = model.part("lid")
    lid.visual(
        _mesh(_lid_cap_rear(r.case_w, r.case_d), "lid_shell", assets),
        material=mats["shell"],
        name="lid_shell", material_class_id=("plastic.clear_rigid" if r.palette_style in {"clear_frame_black_tray", "clear_frame_white_tray", "smoked_tint_black", "translucent_colour_tray"} else "plastic.frosted_translucent"),
    )
    if extra is not None:
        extra(lid)
    lid.inertial = Inertial.from_geometry(
        Box((r.case_w, r.case_d, LID_T)),
        mass=0.035,
        origin=Origin(xyz=(0.0, -r.case_d / 2.0, LID_T / 2.0)),
    )
    model.articulation(
        "base_to_lid",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lid,
        origin=Origin(xyz=(0.0, r.case_d / 2.0, r.hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=r.lid_open),
    )
    return lid


def _emit_topflip(model, r, base, mats, *, assets, extra=None):
    lid = model.part("lid")
    lid.visual(
        _mesh(_lid_cap_side(r.case_w, r.case_d), "lid_shell", assets),
        material=mats["shell"],
        name="lid_shell", material_class_id=("plastic.clear_rigid" if r.palette_style in {"clear_frame_black_tray", "clear_frame_white_tray", "smoked_tint_black", "translucent_colour_tray"} else "plastic.frosted_translucent"),
    )
    if extra is not None:
        extra(lid)
    lid.inertial = Inertial.from_geometry(
        Box((r.case_w, r.case_d, LID_T)),
        mass=0.035,
        origin=Origin(xyz=(-r.case_w / 2.0, 0.0, LID_T / 2.0)),
    )
    model.articulation(
        "base_to_lid",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lid,
        origin=Origin(xyz=(r.case_w / 2.0, 0.0, r.hinge_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=r.lid_open),
    )
    return lid


def _sleeve_shell(r: ResolvedCdJewelCaseConfig) -> cq.Workplane:
    sl_ix = r.case_w + 2 * SLEEVE_CLEAR
    sl_iy = r.case_d + 2 * SLEEVE_CLEAR
    sl_iz = r.frame_h + 2 * SLEEVE_CLEAR
    sl_ox = sl_ix + 2 * SLEEVE_WALL
    sl_oy = sl_iy + 2 * SLEEVE_WALL
    sl_oz = sl_iz + 2 * SLEEVE_WALL
    outer = cq.Workplane("XY").box(sl_ox, sl_oy, sl_oz, centered=(True, True, True))
    inner = cq.Workplane("XY").box(sl_ix, sl_iy, sl_iz, centered=(True, True, True))
    tube = outer.cut(inner)
    opener = (
        cq.Workplane("XY")
        .box(SLEEVE_WALL + 0.002, sl_iy - 0.0005, sl_iz - 0.0005, centered=(True, True, True))
        .translate((-sl_ox / 2.0 + SLEEVE_WALL / 2.0, 0.0, 0.0))
    )
    return tube.cut(opener)


def _emit_slidingsleeve(model, r, base, mats, *, assets):
    sleeve = model.part("sleeve")
    sleeve.visual(
        _mesh(_sleeve_shell(r), "sleeve_shell", assets), material=mats["shell"], name="sleeve_shell", material_class_id=("plastic.clear_rigid" if r.palette_style in {"clear_frame_black_tray", "clear_frame_white_tray", "smoked_tint_black", "translucent_colour_tray"} else "plastic.frosted_translucent")
    )
    sleeve.inertial = Inertial.from_geometry(
        Box((r.case_w + 0.006, r.case_d + 0.006, r.frame_h + 0.006)),
        mass=0.040,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    model.articulation(
        "base_to_sleeve",
        ArticulationType.PRISMATIC,
        parent=base,
        child=sleeve,
        origin=Origin(xyz=(0.0, 0.0, r.frame_h / 2.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=0.5, lower=0.0, upper=r.sleeve_travel),
    )
    return sleeve


# ---------------------------------------------------------------------------
# Disc helper
# ---------------------------------------------------------------------------
def _emit_disc(model, r, mats, *, assets, name, body_name, marker_name):
    disc = model.part(name)
    disc.visual(
        _mesh(_disc_solid(DISC_R), body_name, assets), material=mats["disc"], name=body_name, material_class_id="metal.aluminum_bare"
    )
    disc.visual(
        Cylinder(radius=DISC_MARKER_R, length=DISC_T),
        origin=Origin(xyz=(DISC_MARKER_X, 0.0, DISC_T / 2.0)),
        material=mats["tray"],
        name=marker_name, appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    disc.inertial = Inertial.from_geometry(
        Cylinder(radius=DISC_R, length=DISC_T),
        mass=0.016,
        origin=Origin(xyz=(0.0, 0.0, DISC_T / 2.0)),
    )
    return disc


# ---------------------------------------------------------------------------
# Body: standard_rigid / doublewide (and carrier for trayless/dualsided/booklet)
# ---------------------------------------------------------------------------
def _build_rigid(model, r, mats, *, assets):
    base = model.part("base")
    base.visual(
        _mesh(
            _open_top_shell(r.case_w, r.case_d, r.base_floor_t, r.wall, r.frame_h),
            "base_frame",
            assets,
        ),
        material=mats["shell"],
        name="base_frame", material_class_id=("plastic.clear_rigid" if r.palette_style in {"clear_frame_black_tray", "clear_frame_white_tray", "smoked_tint_black", "translucent_colour_tray"} else "plastic.frosted_translucent"),
    )
    base.inertial = Inertial.from_geometry(
        Box((r.case_w, r.case_d, r.frame_h)),
        mass=0.070,
        origin=Origin(xyz=(0.0, 0.0, r.frame_h / 2.0)),
    )

    if r.disc_logic in ("center_single", "coplanar"):
        base.visual(
            _mesh(_center_tray(r), "inner_tray", assets), material=mats["tray"], name="inner_tray", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"clear_frame_black_tray", "clear_frame_white_tray", "frosted_grey", "smoked_tint_black", "opaque_coloured_card"} else "plastic.frosted_translucent")
        )
        lid_extra = _booklet_lid_extra(r, mats, assets) if r.inner_tray == "bookletclip" else None
        _emit_closure(model, r, base, mats, assets=assets, lid_extra=lid_extra)
        for k, idx in enumerate(r.disc_slot_indices):
            cx = r.hub_xs[idx]
            disc = _emit_disc(
                model,
                r,
                mats,
                assets=assets,
                name=f"disc_{k}",
                body_name=f"disc_{k}_body",
                marker_name=f"disc_{k}_marker",
            )
            model.articulation(
                f"hub_to_disc_{k}",
                ArticulationType.CONTINUOUS,
                parent=base,
                child=disc,
                origin=Origin(xyz=(cx, 0.0, r.disc_seat_z)),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=0.2, velocity=8.0),
            )

    elif r.disc_logic == "booklet":
        _emit_closure(model, r, base, mats, assets=assets)
        _emit_booklet_leaves(model, r, base, mats, assets=assets)

    elif r.disc_logic == "trayless":
        _emit_trayless(model, r, base, mats, assets=assets)
        _emit_closure(model, r, base, mats, assets=assets)

    elif r.disc_logic == "dualsided":
        _emit_pivot_posts(model, r, base, mats, assets=assets)
        _emit_closure(model, r, base, mats, assets=assets)
        _emit_dualsided(model, r, base, mats, assets=assets)

    return base


def _emit_closure(model, r, base, mats, *, assets, lid_extra=None):
    if r.closure_hinge == "clamshell_swing":
        _emit_clamshell(model, r, base, mats, assets=assets, extra=lid_extra)
    elif r.closure_hinge == "topflip":
        _emit_topflip(model, r, base, mats, assets=assets, extra=lid_extra)
    else:  # slidingsleeve
        _emit_slidingsleeve(model, r, base, mats, assets=assets)


# ---------------------------------------------------------------------------
# inner_tray = bookletclip: center hub on base + lid carries clips + card
# ---------------------------------------------------------------------------
def _booklet_clip(x: float, y: float, lip_dir: float) -> cq.Workplane:
    ceiling_z = LID_T - LID_WALL
    total_y = CLIP_WALL_T + CLIP_LIP_EXT
    shift_y = lip_dir * (CLIP_LIP_EXT / 2.0)
    return (
        cq.Workplane("XY")
        .workplane(offset=ceiling_z - CLIP_H)
        .center(x, y + shift_y)
        .box(CLIP_W, total_y, CLIP_H, centered=(True, True, False))
    )


def _booklet_card(y0: float) -> cq.Workplane:
    ceiling_z = LID_T - LID_WALL
    card_top_z = ceiling_z - CLIP_H + CLIP_LIP_T
    return (
        cq.Workplane("XY")
        .workplane(offset=card_top_z)
        .center(0.0, y0)
        .box(BOOKLET_W, BOOKLET_D, BOOKLET_T, centered=(True, True, False))
    )


def _booklet_lid_extra(r, mats, assets):
    """Return an ``extra(lid)`` callback that adds 4 booklet clips + a card to
    the lid interior (bookletclip is gated to clamshell/topflip + center hub)."""
    if r.closure_hinge == "topflip":
        positions = [
            (-0.042, -0.025, -1.0),
            (0.042, -0.025, -1.0),
            (-0.042, 0.025, 1.0),
            (0.042, 0.025, 1.0),
        ]
        card_y = 0.0
    else:
        y0 = -r.case_d / 2.0
        positions = [
            (-0.042, y0 + 0.030, 1.0),
            (0.042, y0 + 0.030, 1.0),
            (-0.042, y0 - 0.030, -1.0),
            (0.042, y0 - 0.030, -1.0),
        ]
        card_y = y0

    def _extra(lid):
        for i, (cx, cy, lip) in enumerate(positions):
            lid.visual(
                _mesh(_booklet_clip(cx, cy, lip), f"clip_{i}", assets),
                material=mats["shell"],
                name=f"clip_{i}", material_class_id="plastic.clear_rigid",
            )
        lid.visual(
            _mesh(_booklet_card(card_y), "booklet_card", assets),
            material=mats["booklet"],
            name="booklet_card", material_class_id="paper.cardboard",
        )

    return _extra


# ---------------------------------------------------------------------------
# inner_tray = trayless: paper pocket + inline static disc (N=1, no spin)
# ---------------------------------------------------------------------------
def _sleeve_pocket(r: ResolvedCdJewelCaseConfig) -> cq.Workplane:
    sw = r.case_w - 2 * r.wall + 0.006
    sd = r.case_d - 2 * r.wall + 0.006
    st = SLEEVE_SHEET
    interior = DISC_T + 0.0004
    total_h = st * 2 + interior
    z0 = r.base_floor_t
    outer = (
        cq.Workplane("XY").workplane(offset=z0).box(sw, sd, total_h, centered=(True, True, False))
    )
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=z0 + st)
        .center(0.0, -st)
        .box(sw - 2 * st, sd, interior, centered=(True, True, False))
    )
    pocket = outer.cut(cavity)
    window_z = z0 + st + interior - 0.0001
    window = cq.Workplane("XY").workplane(offset=window_z).circle(DISC_R * 0.5).extrude(st + 0.0002)
    return pocket.cut(window)


def _emit_trayless(model, r, base, mats, *, assets):
    base.visual(
        _mesh(_sleeve_pocket(r), "sleeve_pocket", assets),
        material=mats["pocket"],
        name="sleeve_pocket", material_class_id="paper.cardboard",
    )
    disc_z = r.base_floor_t + SLEEVE_SHEET
    base.visual(
        _mesh(_disc_solid(DISC_R), "disc_body", assets),
        origin=Origin(xyz=(0.0, 0.0, disc_z)),
        material=mats["disc"],
        name="disc_body", material_class_id="metal.aluminum_bare",
    )


# ---------------------------------------------------------------------------
# inner_tray = dualsided_flip: bearing posts on base + flip tray (dual hubs)
# ---------------------------------------------------------------------------
def _pivot_post(r: ResolvedCdJewelCaseConfig, side_sign: int) -> cq.Workplane:
    post_cx = side_sign * (r.case_w / 2.0 - r.wall - POST_W / 2.0)
    return (
        cq.Workplane("XY")
        .workplane(offset=r.base_floor_t - 0.0008)
        .center(post_cx, 0.0)
        .box(POST_W, POST_D, r.post_top - (r.base_floor_t - 0.0008), centered=(True, True, False))
    )


def _emit_pivot_posts(model, r, base, mats, *, assets):
    for i, side in enumerate((1, -1)):
        base.visual(
            _mesh(_pivot_post(r, side), f"pivot_post_{i}", assets),
            material=mats["shell"],
            name=f"pivot_post_{i}", material_class_id=("plastic.clear_rigid" if r.palette_style in {"clear_frame_black_tray", "clear_frame_white_tray", "smoked_tint_black", "translucent_colour_tray"} else "plastic.frosted_translucent"),
        )


def _hub_face(r: ResolvedCdJewelCaseConfig, face_sign: int) -> cq.Workplane:
    face_z = face_sign * TRAY_PANEL_T / 2.0
    if face_sign > 0:
        hub = cq.Workplane("XY").workplane(offset=face_z).circle(r.hub_r).extrude(r.hub_h)
        teeth_z0 = face_z
    else:
        hub = cq.Workplane("XY").workplane(offset=face_z - r.hub_h).circle(r.hub_r).extrude(r.hub_h)
        teeth_z0 = face_z - r.hub_h * 0.7
    teeth_h = r.hub_h * 0.7
    teeth = cq.Workplane("XY").workplane(offset=teeth_z0)
    for i in range(N_TEETH):
        a = 2.0 * math.pi * i / N_TEETH
        tx = (r.hub_r + TOOTH_OFFSET) * math.cos(a)
        ty = (r.hub_r + TOOTH_OFFSET) * math.sin(a)
        teeth = teeth.moveTo(tx, ty).circle(TOOTH_R).extrude(teeth_h)
    return hub.union(teeth)


def _flip_tray_panel(r: ResolvedCdJewelCaseConfig) -> cq.Workplane:
    panel = (
        cq.Workplane("XY")
        .workplane(offset=-TRAY_PANEL_T / 2.0)
        .box(r.tray_w, r.tray_d, TRAY_PANEL_T, centered=(True, True, False))
    )
    notch = cq.Workplane("XY").workplane(offset=-TRAY_PANEL_T / 2.0 - 0.001)
    for nx in (-NOTCH_DX, NOTCH_DX):
        notch = notch.moveTo(nx, -r.tray_d / 2.0).circle(NOTCH_R)
    panel = panel.cut(notch.extrude(TRAY_PANEL_T + 0.002))
    # side notches for the bearing posts (cut each independently)
    notch_w = POST_W + 0.002
    notch_d = POST_D + 0.002
    for side in (1, -1):
        nx = side * (r.tray_w / 2.0 - notch_w / 2.0 + 0.001)
        cut = (
            cq.Workplane("XY")
            .workplane(offset=-TRAY_PANEL_T / 2.0 - 0.001)
            .center(nx, 0.0)
            .rect(notch_w, notch_d)
            .extrude(TRAY_PANEL_T + 0.002)
        )
        panel = panel.cut(cut)
    # integral pivot pins from inside the panel out to the posts
    for side in (1, -1):
        pin_inner_x = side * (r.tray_w * 0.40)
        pin_outer_x = side * (r.tray_w / 2.0 + PIVOT_PIN_L)
        pin_start_x = min(pin_inner_x, pin_outer_x)
        pin_length = abs(pin_outer_x - pin_inner_x)
        pin = (
            cq.Workplane("YZ").workplane(offset=pin_start_x).circle(PIVOT_PIN_R).extrude(pin_length)
        )
        panel = panel.union(pin)
    return panel


def _emit_dualsided(model, r, base, mats, *, assets):
    flip = model.part("flip_tray")
    flip.visual(
        _mesh(_flip_tray_panel(r), "tray_panel", assets), material=mats["tray"], name="tray_panel", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"clear_frame_black_tray", "clear_frame_white_tray", "frosted_grey", "smoked_tint_black", "opaque_coloured_card"} else "plastic.frosted_translucent")
    )
    for i, sign in enumerate((1, -1)):
        flip.visual(
            _mesh(_hub_face(r, sign), f"hub_face_{i}", assets),
            material=mats["tray"],
            name=f"hub_face_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"clear_frame_black_tray", "clear_frame_white_tray", "frosted_grey", "smoked_tint_black", "opaque_coloured_card"} else "plastic.frosted_translucent"),
        )
    flip.inertial = Inertial.from_geometry(
        Box((r.tray_w + 2 * PIVOT_PIN_L, r.tray_d, TRAY_PANEL_T + 2 * r.hub_h)),
        mass=0.025,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    model.articulation(
        "base_to_flip_tray",
        ArticulationType.REVOLUTE,
        parent=base,
        child=flip,
        origin=Origin(xyz=(0.0, 0.0, r.pivot_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=math.pi),
    )
    disc = _emit_disc(
        model,
        r,
        mats,
        assets=assets,
        name="disc_0",
        body_name="disc_0_body",
        marker_name="disc_0_marker",
    )
    disc_hub_z = TRAY_PANEL_T / 2.0 + r.hub_h * 0.7
    model.articulation(
        "tray_to_disc_0",
        ArticulationType.CONTINUOUS,
        parent=flip,
        child=disc,
        origin=Origin(xyz=(0.0, 0.0, disc_hub_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.2, velocity=8.0),
    )


# ---------------------------------------------------------------------------
# disc_count >= 3: stacked book leaves (standard_rigid + clamshell only)
# ---------------------------------------------------------------------------
def _leaf_plate(r: ResolvedCdJewelCaseConfig) -> cq.Workplane:
    plate = (
        cq.Workplane("XY")
        .box(r.leaf_w, r.leaf_d, LEAF_T, centered=(True, True, False))
        .translate((0.0, -r.leaf_d / 2.0, 0.0))
    )
    hub_cy = -r.leaf_d / 2.0
    plate = plate.union(_hub_rosette(0.0, hub_cy, LEAF_T, r.hub_r, r.hub_h))
    for nx in (-NOTCH_DX, NOTCH_DX):
        notch = (
            cq.Workplane("XY")
            .workplane(offset=-0.001)
            .center(nx, -r.leaf_d)
            .circle(NOTCH_R)
            .extrude(LEAF_T + 0.003)
        )
        plate = plate.cut(notch)
    barrel = cq.Solid.makeCylinder(
        BARREL_R,
        BARREL_W,
        pnt=cq.Vector(-BARREL_W / 2.0, 0.0, LEAF_T / 2.0),
        dir=cq.Vector(1.0, 0.0, 0.0),
    )
    return plate.union(cq.Workplane("XY").add(barrel))


def _emit_booklet_leaves(model, r, base, mats, *, assets):
    leaf_mesh = _mesh(_leaf_plate(r), "leaf_plate", assets)
    hub_cy = -r.leaf_d / 2.0
    disc_z_in_leaf = LEAF_T + r.hub_h * 0.7
    leaf_hinge_y = r.case_d / 2.0 - r.wall
    for i in range(r.disc_count):
        leaf_z = r.leaf_first_z + i * r.leaf_spacing
        leaf = model.part(f"leaf_{i}")
        leaf.visual(leaf_mesh, material=mats["tray"], name=f"leaf_plate_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"clear_frame_black_tray", "clear_frame_white_tray", "frosted_grey", "smoked_tint_black", "opaque_coloured_card"} else "plastic.frosted_translucent"))
        leaf.inertial = Inertial.from_geometry(
            Box((r.leaf_w, r.leaf_d, LEAF_T + r.hub_h)),
            mass=0.020,
            origin=Origin(xyz=(0.0, -r.leaf_d / 2.0, 0.0)),
        )
        model.articulation(
            f"base_to_leaf_{i}",
            ArticulationType.REVOLUTE,
            parent=base,
            child=leaf,
            origin=Origin(xyz=(0.0, leaf_hinge_y, leaf_z)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=2.0, velocity=3.0, lower=0.0, upper=math.radians(120.0)
            ),
        )
        disc = _emit_disc(
            model,
            r,
            mats,
            assets=assets,
            name=f"disc_{i}",
            body_name=f"disc_body_{i}",
            marker_name=f"disc_marker_{i}",
        )
        model.articulation(
            f"leaf_{i}_to_disc_{i}",
            ArticulationType.CONTINUOUS,
            parent=leaf,
            child=disc,
            origin=Origin(xyz=(0.0, hub_cy, disc_z_in_leaf)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=0.2, velocity=8.0),
        )


# ---------------------------------------------------------------------------
# Body: slimline (thin base plate + lid carries tray, disc parent = lid)
# ---------------------------------------------------------------------------
def _slim_base_plate(r: ResolvedCdJewelCaseConfig) -> cq.Workplane:
    return cq.Workplane("XY").box(r.case_w, r.case_d, SLIM_BASE_T, centered=(True, True, False))


def _slim_lid_cover(r: ResolvedCdJewelCaseConfig) -> cq.Workplane:
    depth = r.slim_lid_depth
    outer = (
        cq.Workplane("XY")
        .workplane(offset=-depth)
        .box(r.case_w, r.case_d, depth, centered=(True, True, False))
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=-depth)
        .box(
            r.case_w - 2 * SLIM_LID_WALL,
            r.case_d - 2 * SLIM_LID_WALL,
            depth - SLIM_COVER_T,
            centered=(True, True, False),
        )
    )
    return outer.cut(inner)


def _slim_lid_tray(r: ResolvedCdJewelCaseConfig) -> cq.Workplane:
    tw = r.case_w - 2 * SLIM_LID_WALL - 0.0004
    td = r.case_d - 2 * SLIM_LID_WALL - 0.0004
    floor_z_top = -SLIM_COVER_T
    floor_z_bot = floor_z_top - SLIM_TRAY_T
    tray = (
        cq.Workplane("XY")
        .workplane(offset=floor_z_bot)
        .box(tw, td, SLIM_TRAY_T, centered=(True, True, False))
    )
    hub = (
        cq.Workplane("XY")
        .workplane(offset=floor_z_bot - SLIM_HUB_H)
        .circle(r.hub_r)
        .extrude(SLIM_HUB_H)
    )
    tray = tray.union(hub)
    tooth_h = SLIM_HUB_H * 0.7
    teeth_z_bot = floor_z_bot - tooth_h
    for i in range(N_TEETH):
        a = 2.0 * math.pi * i / N_TEETH
        tx = (r.hub_r + TOOTH_OFFSET) * math.cos(a)
        ty = (r.hub_r + TOOTH_OFFSET) * math.sin(a)
        tray = tray.union(
            cq.Workplane("XY")
            .workplane(offset=teeth_z_bot)
            .moveTo(tx, ty)
            .circle(TOOTH_R)
            .extrude(tooth_h)
        )
    notch = cq.Workplane("XY").workplane(offset=floor_z_bot - 0.001)
    for nx in (-NOTCH_DX, NOTCH_DX):
        notch = notch.moveTo(nx, -td / 2.0).circle(NOTCH_R)
    tray = tray.cut(notch.extrude(SLIM_TRAY_T + 0.003))
    return tray


def _build_slimline(model, r, mats, *, assets):
    base = model.part("base")
    base.visual(
        _mesh(_slim_base_plate(r), "base_plate", assets), material=mats["shell"], name="base_plate", material_class_id=("plastic.clear_rigid" if r.palette_style in {"clear_frame_black_tray", "clear_frame_white_tray", "smoked_tint_black", "translucent_colour_tray"} else "plastic.frosted_translucent")
    )
    base.inertial = Inertial.from_geometry(
        Box((r.case_w, r.case_d, SLIM_BASE_T)),
        mass=0.025,
        origin=Origin(xyz=(0.0, 0.0, SLIM_BASE_T / 2.0)),
    )
    hinge_y = r.case_d / 2.0
    lid = model.part("lid")
    lid.visual(
        _mesh(_slim_lid_cover(r), "lid_cover", assets),
        origin=Origin(xyz=(0.0, -hinge_y, 0.0)),
        material=mats["shell"],
        name="lid_cover", material_class_id=("plastic.clear_rigid" if r.palette_style in {"clear_frame_black_tray", "clear_frame_white_tray", "smoked_tint_black", "translucent_colour_tray"} else "plastic.frosted_translucent"),
    )
    lid.visual(
        _mesh(_slim_lid_tray(r), "lid_tray", assets),
        origin=Origin(xyz=(0.0, -hinge_y, 0.0)),
        material=mats["tray"],
        name="lid_tray", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"clear_frame_black_tray", "clear_frame_white_tray", "frosted_grey", "smoked_tint_black", "opaque_coloured_card"} else "plastic.frosted_translucent"),
    )
    lid.inertial = Inertial.from_geometry(
        Box((r.case_w, r.case_d, r.slim_lid_depth)),
        mass=0.030,
        origin=Origin(xyz=(0.0, -hinge_y, -r.slim_lid_depth / 2.0)),
    )
    model.articulation(
        "base_to_lid",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lid,
        origin=Origin(xyz=(0.0, hinge_y, r.slim_hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=r.lid_open),
    )
    disc = _emit_disc(
        model,
        r,
        mats,
        assets=assets,
        name="disc_0",
        body_name="disc_0_body",
        marker_name="disc_0_marker",
    )
    model.articulation(
        "hub_to_disc_0",
        ArticulationType.CONTINUOUS,
        parent=lid,
        child=disc,
        origin=Origin(xyz=(0.0, -hinge_y, r.slim_disc_z_local)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.2, velocity=8.0),
    )
    return base


# ---------------------------------------------------------------------------
# Body: digipak (opaque card book-fold, coupled spine_fold closure)
# ---------------------------------------------------------------------------
def _cardboard_panel(w: float, d: float, t: float, centered_z: bool = False) -> cq.Workplane:
    return cq.Workplane("XY").box(w, d, t, centered=(True, True, centered_z))


def _digipak_disc_tray(r: ResolvedCdJewelCaseConfig) -> cq.Workplane:
    tw, td = r.tray_board_w, r.tray_board_d
    tray = cq.Workplane("XY").box(tw, td, r.floor_t, centered=(True, True, False))
    tray = tray.union(_hub_rosette(0.0, 0.0, r.floor_t, r.hub_r, r.hub_h))
    for nx in (-NOTCH_DX, NOTCH_DX):
        notch = (
            cq.Workplane("XY")
            .workplane(offset=-0.001)
            .moveTo(nx, -td / 2.0)
            .circle(NOTCH_R)
            .extrude(r.floor_t + 0.003)
        )
        tray = tray.cut(notch)
    return tray


def _build_digipak(model, r, mats, *, assets):
    tray_panel = model.part("tray_panel")
    tray_panel.visual(
        _mesh(_cardboard_panel(r.panel_w, r.case_d, PANEL_T), "tray_board", assets),
        origin=Origin(xyz=(SPINE_W + r.panel_w / 2.0, 0.0, 0.0)),
        material=mats["card"],
        name="tray_board", material_class_id="paper.cardboard",
    )
    tray_panel.visual(
        _mesh(_cardboard_panel(SPINE_W, r.case_d, PANEL_T), "spine", assets),
        origin=Origin(xyz=(SPINE_W / 2.0, 0.0, 0.0)),
        material=mats["card"],
        name="spine", material_class_id="paper.cardboard",
    )
    tray_panel.visual(
        _mesh(_digipak_disc_tray(r), "disc_tray", assets),
        origin=Origin(xyz=(r.tray_center_x, 0.0, PANEL_T)),
        material=mats["tray"],
        name="disc_tray", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"clear_frame_black_tray", "clear_frame_white_tray", "frosted_grey", "smoked_tint_black", "opaque_coloured_card"} else "plastic.frosted_translucent"),
    )
    tray_panel.inertial = Inertial.from_geometry(
        Box((r.case_w, r.case_d, PANEL_T + r.floor_t + r.hub_h)),
        mass=0.080,
        origin=Origin(xyz=(SPINE_W + r.panel_w / 2.0, 0.0, PANEL_T / 2.0)),
    )

    cover_panel = model.part("cover_panel")
    cover_panel.visual(
        _mesh(
            _cardboard_panel(r.panel_w, r.case_d, PANEL_T, centered_z=True), "cover_board", assets
        ),
        origin=Origin(xyz=(-r.panel_w / 2.0, 0.0, 0.0)),
        material=mats["cover"],
        name="cover_board", material_class_id="paper.cardboard",
    )
    cover_panel.inertial = Inertial.from_geometry(
        Box((r.panel_w, r.case_d, PANEL_T)),
        mass=0.040,
        origin=Origin(xyz=(-r.panel_w / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "spine_fold",
        ArticulationType.REVOLUTE,
        parent=tray_panel,
        child=cover_panel,
        origin=Origin(xyz=(0.0, 0.0, PANEL_T / 2.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=r.spine_open),
    )

    disc = _emit_disc(
        model,
        r,
        mats,
        assets=assets,
        name="disc_0",
        body_name="disc_0_body",
        marker_name="disc_0_marker",
    )
    model.articulation(
        "hub_to_disc_0",
        ArticulationType.CONTINUOUS,
        parent=tray_panel,
        child=disc,
        origin=Origin(xyz=(r.tray_center_x, 0.0, r.disc_seat_z_dp)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.2, velocity=8.0),
    )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_cd_jewel_case(
    config: CdJewelCaseConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        role: model.material(f"cd_{role}_{r.palette_style}", rgba=rgba)
        for role, rgba in PALETTES[r.palette_style].items()
    }

    if r.body_type == "digipak":
        _build_digipak(model, r, mats, assets=assets)
    elif r.body_type == "slimline":
        _build_slimline(model, r, mats, assets=assets)
    else:
        _build_rigid(model, r, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_cd_jewel_case(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_cd_jewel_case(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_cd_jewel_case_tests(
    object_model: ArticulatedObject,
    config: CdJewelCaseConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}

    # ---- intentional overlaps / isolated parts (declare before checks) ----
    if r.body_type == "digipak":
        tray_panel = object_model.get_part("tray_panel")
        disc = object_model.get_part("disc_0")
        ctx.allow_overlap(
            disc,
            tray_panel,
            elem_a="disc_0_body",
            elem_b="disc_tray",
            reason="The CD center hole drops over the molded disc-tray hub/rosette.",
        )
        ctx.allow_overlap(
            object_model.get_part("cover_panel"),
            tray_panel,
            elem_a="cover_board",
            elem_b="spine",
            reason="The flat-open cover board meets the spine strip at the fold line.",
        )
    elif r.body_type == "slimline":
        base = object_model.get_part("base")
        lid = object_model.get_part("lid")
        disc = object_model.get_part("disc_0")
        ctx.allow_overlap(
            disc,
            lid,
            elem_a="disc_0_body",
            elem_b="lid_tray",
            reason="The CD center hole drops over the lid-carried hub/rosette.",
        )
        ctx.allow_overlap(
            base, lid, reason="The closed slimline lid + disc rest flat over the thin base plate."
        )
        ctx.allow_overlap(
            disc,
            base,
            reason="The lid-carried disc seats just above the thin base plate when closed.",
        )
    else:
        base = object_model.get_part("base")

        # closure-specific
        if r.closure_hinge == "slidingsleeve":
            sleeve = object_model.get_part("sleeve")
            ctx.allow_isolated_part(
                sleeve,
                reason="The clear slipcase sleeve slides over the base with uniform clearance; "
                "the prismatic joint is the mechanical connection, not surface contact.",
            )
        elif "lid" in part_names:
            lid = object_model.get_part("lid")
            ctx.allow_overlap(
                lid,
                base,
                reason="The closed clamshell lid caps over the base contents and seats on the frame rim.",
            )
            if r.inner_tray == "bookletclip":
                for i in range(4):
                    ctx.allow_overlap(
                        lid,
                        lid,
                        elem_a=f"clip_{i}",
                        elem_b="booklet_card",
                        reason="The molded clip lip grips the booklet card edge.",
                    )

        # tray / disc specifics
        if r.disc_logic in ("center_single", "coplanar"):
            for k in range(len(r.disc_slot_indices)):
                d = object_model.get_part(f"disc_{k}")
                ctx.allow_overlap(
                    d,
                    base,
                    elem_a=f"disc_{k}_body",
                    elem_b="inner_tray",
                    reason="The CD center hole drops over the raised tray hub/rosette (captured pin).",
                )
        elif r.disc_logic == "trayless":
            pass  # disc + pocket are inline base visuals; no inter-part overlap
        elif r.disc_logic == "dualsided":
            flip = object_model.get_part("flip_tray")
            disc = object_model.get_part("disc_0")
            ctx.allow_overlap(
                disc,
                flip,
                elem_a="disc_0_body",
                elem_b="hub_face_0",
                reason="The CD center hole drops over the upper flip-tray hub.",
            )
            for i in range(2):
                ctx.allow_overlap(
                    flip,
                    base,
                    elem_a="tray_panel",
                    elem_b=f"pivot_post_{i}",
                    reason="The integral pivot pin seats into the bearing post.",
                )
            if "lid" in part_names:
                ctx.allow_overlap(
                    object_model.get_part("lid"),
                    flip,
                    reason="The closed lid caps over the flip tray.",
                )
        elif r.disc_logic == "booklet":
            for i in range(r.disc_count):
                leaf = object_model.get_part(f"leaf_{i}")
                d = object_model.get_part(f"disc_{i}")
                ctx.allow_overlap(
                    d,
                    leaf,
                    elem_a=f"disc_body_{i}",
                    elem_b=f"leaf_plate_{i}",
                    reason="The CD center hole drops over the leaf hub.",
                )
                ctx.allow_overlap(
                    leaf,
                    base,
                    elem_a=f"leaf_plate_{i}",
                    elem_b="base_frame",
                    reason="The leaf hinge barrel wraps the pivot at the inner rear wall.",
                )
            if "lid" in part_names:
                ctx.allow_overlap(
                    object_model.get_part("lid"),
                    base,
                    reason="The closed lid caps over the stacked leaves.",
                )

    # ---- baseline checks ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- identity: clear shell vs opaque card/pocket ----
    if r.body_type == "digipak":
        tray_panel = object_model.get_part("tray_panel")
        cover_panel = object_model.get_part("cover_panel")
        a1 = tray_panel.get_visual("tray_board").material.rgba[3]
        a2 = cover_panel.get_visual("cover_board").material.rgba[3]
        ctx.check(
            "digipak panels are opaque card (alpha >= 0.95)",
            a1 >= 0.95 and a2 >= 0.95,
            details=f"tray={a1} cover={a2}",
        )
    else:
        base = object_model.get_part("base")
        shell_visual = "base_plate" if r.body_type == "slimline" else "base_frame"
        ba = base.get_visual(shell_visual).material.rgba[3]
        ctx.check(
            "base shell is clear/translucent plastic (alpha < 0.6)", ba < 0.6, details=f"alpha={ba}"
        )
        if r.disc_logic == "trayless":
            pa = base.get_visual("sleeve_pocket").material.rgba[3]
            ctx.check(
                "trayless paper pocket is opaque (alpha >= 0.8)", pa >= 0.8, details=f"alpha={pa}"
            )

    # ---- identity: disc footprint matches a 120 mm CD ----
    disc_parts = [p for p in object_model.parts if p.name.startswith("disc")]
    if disc_parts:
        dp = disc_parts[0]
        body_elem = next((v.name for v in dp.visuals if "body" in v.name), None)
        if body_elem is not None:
            ab = ctx.part_element_world_aabb(dp, elem=body_elem)
            if ab is not None:
                dia = ab[1][0] - ab[0][0]
                ctx.check(
                    "disc reads as a 120 mm CD (diameter ~0.12 m)",
                    0.110 < dia < 0.130,
                    details=f"dia={dia:.4f}",
                )

    # ---- at least one non-fixed closure joint exists ----
    non_fixed = [
        a for a in object_model.articulations if a.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed mechanism joint",
        len(non_fixed) >= 1,
        details=f"count={len(non_fixed)}",
    )

    # ---- closure joint type / axis ----
    if r.body_type == "digipak":
        j = object_model.get_articulation("spine_fold")
        ctx.check(
            "spine fold is REVOLUTE about Y",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.9,
            details=f"axis={tuple(j.axis)}",
        )
    elif r.closure_hinge == "slidingsleeve":
        j = object_model.get_articulation("base_to_sleeve")
        ctx.check(
            "sliding sleeve is PRISMATIC about X",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[0]) > 0.9,
            details=f"axis={tuple(j.axis)}",
        )
        # sleeve covers the base footprint when closed (isolated-part proof)
        ctx.expect_overlap(
            object_model.get_part("sleeve"),
            base,
            axes="xy",
            min_overlap=0.08,
            elem_a="sleeve_shell",
            elem_b="base_frame",
            name="closed sleeve covers the base footprint",
        )
    elif "lid" in part_names:
        j = object_model.get_articulation("base_to_lid")
        if r.closure_hinge == "topflip":
            ctx.check(
                "topflip lid is REVOLUTE about Y",
                j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.9,
                details=f"axis={tuple(j.axis)}",
            )
        else:
            ctx.check(
                "clamshell lid is REVOLUTE about X",
                j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.9,
                details=f"axis={tuple(j.axis)}",
            )

    # ---- closure opens (lid lifts / sleeve slides) ----
    if r.body_type == "digipak":
        j = object_model.get_articulation("spine_fold")
        cover = object_model.get_part("cover_panel")
        closed_top = ctx.part_world_aabb(cover)[1][2]
        with ctx.pose({j: math.radians(90.0)}):
            open_top = ctx.part_world_aabb(cover)[1][2]
        ctx.check(
            "digipak cover folds up and over",
            open_top > closed_top + 0.02,
            details=f"closed={closed_top:.4f} open={open_top:.4f}",
        )
    elif r.closure_hinge == "slidingsleeve":
        sleeve = object_model.get_part("sleeve")
        p0 = ctx.part_world_position(sleeve)
        with ctx.pose({object_model.get_articulation("base_to_sleeve"): r.sleeve_travel * 0.8}):
            p1 = ctx.part_world_position(sleeve)
        ctx.check(
            "sleeve slides open along +X",
            p1[0] > p0[0] + 0.05,
            details=f"x0={p0[0]:.4f} x1={p1[0]:.4f}",
        )
    elif "lid" in part_names:
        j = object_model.get_articulation("base_to_lid")
        lid = object_model.get_part("lid")
        closed_top = ctx.part_world_aabb(lid)[1][2]
        with ctx.pose({j: r.lid_open * 0.8}):
            open_top = ctx.part_world_aabb(lid)[1][2]
        ctx.check(
            "lid swings open and lifts upward",
            open_top > closed_top + 0.02,
            details=f"closed={closed_top:.4f} open={open_top:.4f}",
        )

    # ---- inner_tray topology specifics ----
    if r.disc_logic == "trayless":
        cont = [
            a
            for a in object_model.articulations
            if a.articulation_type == ArticulationType.CONTINUOUS
        ]
        ctx.check(
            "trayless has no spin joint (disc is static)",
            len(cont) == 0,
            details=f"continuous={len(cont)}",
        )
        ctx.check(
            "trayless disc is an inline base visual", base.get_visual("disc_body") is not None
        )
        ctx.check(
            "trayless has exactly 2 parts",
            len(object_model.parts) == 2,
            details=f"parts={sorted(part_names)}",
        )
    elif r.disc_logic == "dualsided":
        flip = object_model.get_part("flip_tray")
        ctx.check(
            "flip tray has dual hub faces",
            flip.get_visual("hub_face_0") is not None and flip.get_visual("hub_face_1") is not None,
        )
        jf = object_model.get_articulation("base_to_flip_tray")
        ctx.check(
            "flip tray is REVOLUTE about X with 180 deg range",
            jf.articulation_type == ArticulationType.REVOLUTE
            and abs(jf.axis[0]) > 0.9
            and jf.motion_limits.upper >= math.pi - 0.01,
            details=f"axis={tuple(jf.axis)} upper={jf.motion_limits.upper}",
        )
        jd = object_model.get_articulation("tray_to_disc_0")
        parent_name = jd.parent if isinstance(jd.parent, str) else jd.parent.name
        ctx.check(
            "dualsided disc is parented to the flip tray",
            parent_name == "flip_tray",
            details=f"parent={parent_name}",
        )
    elif r.disc_logic == "booklet":
        leaves = [p for p in part_names if p.startswith("leaf_")]
        discs = [p for p in part_names if p.startswith("disc_")]
        ctx.check(
            "N leaves present",
            len(leaves) == r.disc_count,
            details=f"leaves={len(leaves)} N={r.disc_count}",
        )
        ctx.check(
            "N discs present",
            len(discs) == r.disc_count,
            details=f"discs={len(discs)} N={r.disc_count}",
        )
        jd0 = object_model.get_articulation("leaf_0_to_disc_0")
        parent_name = jd0.parent if isinstance(jd0.parent, str) else jd0.parent.name
        ctx.check(
            "booklet disc_0 is parented to its own leaf",
            parent_name == "leaf_0",
            details=f"parent={parent_name}",
        )

    # ---- slimline closed height is thin (~half of a standard case) ----
    if r.body_type == "slimline":
        base = object_model.get_part("base")
        lid = object_model.get_part("lid")
        closed_h = max(ctx.part_world_aabb(base)[1][2], ctx.part_world_aabb(lid)[1][2])
        ctx.check(
            "slimline closed height is thin (< 0.010 m)",
            closed_h < 0.010,
            details=f"closed_h={closed_h:.4f}",
        )
        jd = object_model.get_articulation("hub_to_disc_0")
        parent_name = jd.parent if isinstance(jd.parent, str) else jd.parent.name
        ctx.check(
            "slimline disc is parented to the lid",
            parent_name == "lid",
            details=f"parent={parent_name}",
        )

    # ---- doublewide is roughly double-wide ----
    if r.body_type == "doublewide":
        base = object_model.get_part("base")
        bw = ctx.part_world_aabb(base)[1][0] - ctx.part_world_aabb(base)[0][0]
        ctx.check("doublewide case is wide (>= 0.25 m)", bw >= 0.25, details=f"width={bw:.4f}")

    # ---- a spin joint exists unless trayless ----
    if r.disc_logic != "trayless":
        cont = [
            a
            for a in object_model.articulations
            if a.articulation_type == ArticulationType.CONTINUOUS
        ]
        ctx.check(
            "center-hub disc spins (CONTINUOUS +Z)",
            len(cont) >= 1 and all(abs(a.axis[2]) > 0.9 for a in cont),
            details=f"continuous={len(cont)}",
        )

    # ---- slot_choices recorded ----
    ctx.check(
        "slot_choices recorded and consistent",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "CdJewelCaseConfig",
    "ResolvedCdJewelCaseConfig",
    "build_cd_jewel_case",
    "build_seeded_cd_jewel_case",
    "config_from_seed",
    "resolve_config",
    "run_cd_jewel_case_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
