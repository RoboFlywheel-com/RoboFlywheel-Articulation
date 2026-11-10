# SPDX-License-Identifier: Apache-2.0

"""Pop-up bread toaster modular template (slot-count multiplicity).

NOTE on the slug: ``toaster`` here = a **pop-up bread toaster** (a fused hollow
``body`` carbon shell with N top bread slots, a single shared push-down
``carriage_lever`` that lowers every bread shelf together, a brushed-silver +X
control panel carrying a browning control + 3 function buttons, four feet, and an
optional pull-out crumb tray), NOT a toaster oven (no side/drop glass door + inner
rack — that is a different category, ``rec_toaster_oven_*``), NOT a bread maker
(no tall bin + kneading paddle), and NOT a sandwich/panini press (no clamshell
hinged heating plates). Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Kitchen_Toaster.md`` and the
``picture/Kitchen/Toaster`` 5-star pool (1 parent + 7 slot/multiplicity fork
variants), all synced under ``data/records/``.

Structure (pattern = ``multiplicity``; the bread-slot count is the dominant
multiplicity axis). A single root ``body`` part holds the hollow shell +
recessed slot rim plate + brushed-silver control panel + four feet + dial/slider
marks + brand strip (all inline visuals, Rule 1); everything that moves parents
directly to it as a parallel child:

  * ``carriage_lever`` (PRISMATIC axis (0,0,-1), 0.070 m DOWN) — the **defining
    motion**. lever_knob + lever_stem + carriage_crossbar + N ``bread_shelf_{i}``
    visuals. ALL N shelves ride this ONE carriage (one joint regardless of N).
    slot_count is therefore a **visual / cut multiplicity**, not a joint
    multiplicity (contrast tool_cart's per-N drawer joints).
  * browning control (Slot A): ``rotary_dial`` (1 REVOLUTE +X knob) /
    ``slider`` (1 PRISMATIC +Z tab) / ``digital`` (2 PRISMATIC -X up/down pads +
    inline display).
  * 3 function buttons (cancel/frozen/bagel) — fixed structure, 3 PRISMATIC -X.
  * optional ``crumb_tray`` (Slot C): pullout (1 PRISMATIC +X, 0.180 m) or none
    (disabled state — no tray geometry, sealed floor).

Slot B (lever_placement) chooses the carriage mount face: ``front_lever``
(control-panel slot) / ``side_lever`` (+Y side-wall slot + ``lever_guide_plate``);
the carriage joint type / axis / 0.070 m travel are identical either way.
Slot D (body_silhouette) chooses the root shell primitive: ``square_box``
(box + fillet) / ``retro_round`` (3-section ``slot2D.loft`` dome barrel — a real
loft, not a box placeholder).

Compatibility (spec §9): retro_round gates slot_count to N=2 (the dome taper
narrows the top Y and the loft is tuned for a 2-slice body); side_lever requires
square_box (it assumes a flat side wall). browning_control is orthogonal to
everything.

All carriage / browning / tray / button fits are captured/seated geometry, so
those joints omit ``MatingContract`` (grandfathered) and are guarded by the flat
0.015 m articulation-origin baseline plus element-scoped ``allow_overlap``
(mirroring each source's run_tests block).
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
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

BrowningControl = Literal["rotary_dial", "slider", "digital"]
LeverPlacement = Literal["front_lever", "side_lever"]
CrumbTray = Literal["none", "pullout"]
BodySilhouette = Literal["square_box", "retro_round"]
PaletteStyle = Literal[
    "chrome_silver",
    "matte_black",
    "pastel_cream",
    "brushed_steel",
    "retro_red",
]

BROWNING_CONTROLS: tuple[BrowningControl, ...] = ("rotary_dial", "slider", "digital")
LEVER_PLACEMENTS: tuple[LeverPlacement, ...] = ("front_lever", "side_lever")
CRUMB_TRAYS: tuple[CrumbTray, ...] = ("none", "pullout")
BODY_SILHOUETTES: tuple[BodySilhouette, ...] = ("square_box", "retro_round")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "chrome_silver",
    "matte_black",
    "pastel_cream",
    "brushed_steel",
    "retro_red",
)

# slot_count multiplicity domain (spec §8). Weighted small: N=2 high, N=4 common,
# N=3 occasional. retro_round gates to N=2 in resolve_config.
N_SLOT_MIN, N_SLOT_MAX = 2, 4
_SLOT_COUNT_CHOICES = (2, 3, 4)
_SLOT_COUNT_WEIGHTS = (0.55, 0.15, 0.30)

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). From the parent (d8fcb465) 2-slice body.
# ---------------------------------------------------------------------------
BODY_W = 0.160  # along Y (shared across N)
BODY_H = 0.190  # overall height including feet
FOOT_H = 0.014
FOOT_R = 0.011

# Two-slice baseline body length; N=4 extends to 0.396 (derived per N below).
BODY_L_2SLICE = 0.280
BODY_L_4SLICE = 0.396

# Internal toasting cavity (square_box, 2-slice reference).
CAV_X_MARGIN = 0.020  # cavity ends inset this far from the body X faces (front)
CAV_X_BACK_MARGIN = 0.020  # back inset
CAV_Y = 0.052  # half width (square_box)
CAV_Z0, CAV_Z1 = 0.060, 0.168

# Bread slots cut through the top.
SLOT_W = 0.030  # y width of each slot opening
SLOT_YC = 0.034  # +/- y centers (2-slice pair / 4-slice pairs)
SLOT_CUT_Z0 = 0.158  # cut from here up through the top
SLOT_PAIR_DX = 0.060  # X offset of each pair for N=4 (rear/front)
SLOT_L_2SLICE = 0.200
SLOT_L_4SLICE = 0.130

# Recessed lighter-gray rim plate.
RECESS_W = 0.114
RECESS_Z0 = 0.185
RIM_T = 0.0048

# Front control panel plate (+X face).
PANEL_T = 0.0045
PANEL_W = 0.116
PANEL_Z0, PANEL_Z1 = 0.032, 0.172

# Carriage lever (defining motion).
LEVER_TRAVEL = 0.070
LEVER_YC = 0.005  # slot slightly right of panel center (front mount)
LEVER_REST_Z = 0.150
LEVER_SLOT_W = 0.012
LEVER_SLOT_Z0, LEVER_SLOT_Z1 = 0.070, 0.160

# Side-lever placement.
LEVER_XC_SIDE = 0.020  # X of the lever on the +Y side wall

# Function buttons (CANCEL / FROZEN / BAGEL), stacked on the -Y half.
BTN_Y = -0.036
BTN_Z = (0.112, 0.086, 0.060)
BTN_CAP_R = 0.0065
BTN_CAP_L = 0.0065
BTN_STEM_R = 0.0045
BTN_HOLE_R = 0.0060
BTN_TRAVEL = 0.003

# Browning rotary dial.
DIAL_Y = 0.030
DIAL_Z = 0.054
DIAL_D = 0.030
DIAL_H = 0.014
DIAL_SHAFT_R = 0.004
DIAL_HOLE_R = 0.0047
DIAL_RANGE = math.radians(270.0)

# Browning slider.
SLIDER_Y = 0.030
SLIDER_REST_Z = 0.052
SLIDER_TRAVEL = 0.044
SLIDER_TAB_W = 0.018
SLIDER_TAB_H = 0.012
SLIDER_TAB_D = 0.008
TRACK_SLOT_W = 0.006
SLIDER_STEM_W = 0.004
SLIDER_STEM_D = 0.030

# Browning digital.
DIGI_Y = 0.030
DIGI_DISPLAY_W = 0.022
DIGI_DISPLAY_H = 0.013
DIGI_DISPLAY_Z = 0.054
DIGI_BTN_W = 0.010
DIGI_BTN_H = 0.008
DIGI_BTN_D = 0.005
DIGI_BTN_STEM_R = 0.003
DIGI_BTN_HOLE_R = 0.004
DIGI_BTN_TRAVEL = 0.003

# Crumb tray (pullout). Width kept narrower than the body so the corner feet
# (along the +/-Y side walls) sit on solid floor outboard of the tray + pocket.
TRAY_W = 0.100
TRAY_T = 0.003
TRAY_LIP_H = 0.006
TRAY_LIP_T = 0.002
TRAY_TOTAL_H = TRAY_T + TRAY_LIP_H  # 0.009
TRAY_TAB_W = 0.032
TRAY_TAB_T = TRAY_LIP_T + 0.005
TRAY_TAB_H = TRAY_TOTAL_H + 0.006
TRAY_Z_BASE = FOOT_H + 0.001  # 0.015
TRAY_TRAVEL = 0.180

# retro_round loft factors (relative to BODY_L / BODY_W).
LOFT_BOTTOM_L_F, LOFT_BOTTOM_W_F = 0.99, 0.97
LOFT_MIDDLE_L_F, LOFT_MIDDLE_W_F = 1.01, 1.02
LOFT_TOP_L_F, LOFT_TOP_W_F = 0.97, 0.78
# retro_round shifts several Z anchors down for the dome taper.
RETRO_CAV_Z1 = 0.160
RETRO_SLOT_CUT_Z0 = 0.145
RETRO_RECESS_Z0 = 0.175
RETRO_RECESS_W = 0.108
RETRO_PANEL_Z1 = 0.152
RETRO_LEVER_REST_Z = 0.148
RETRO_LEVER_SLOT_Z1 = 0.155
RETRO_LEVER_SLOT_X0 = 0.098  # lever slot extends inward for dome taper

SHELL_H = BODY_H - FOOT_H  # 0.176
SHELL_TOP = BODY_H

# ---------------------------------------------------------------------------
# Palettes (5 colorways, spec §7). Keys are role tokens used by every visual.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "chrome_silver": {
        "shell": (0.40, 0.40, 0.41, 1.0),
        "rim": (0.63, 0.64, 0.65, 1.0),
        "panel": (0.78, 0.79, 0.81, 1.0),
        "dark": (0.11, 0.11, 0.12, 1.0),
        "knob": (0.48, 0.49, 0.50, 1.0),
        "control": (0.24, 0.25, 0.26, 1.0),
        "button": (0.72, 0.73, 0.75, 1.0),
        "carriage": (0.56, 0.57, 0.59, 1.0),
        "mark": (0.18, 0.18, 0.19, 1.0),
        "display": (0.04, 0.06, 0.08, 1.0),
        "tray": (0.15, 0.15, 0.16, 1.0),
    },
    "matte_black": {
        "shell": (0.10, 0.10, 0.11, 1.0),
        "rim": (0.18, 0.18, 0.19, 1.0),
        "panel": (0.16, 0.16, 0.18, 1.0),
        "dark": (0.07, 0.07, 0.08, 1.0),
        "knob": (0.72, 0.74, 0.78, 1.0),
        "control": (0.72, 0.74, 0.78, 1.0),
        "button": (0.66, 0.67, 0.69, 1.0),
        "carriage": (0.30, 0.31, 0.33, 1.0),
        "mark": (0.60, 0.61, 0.63, 1.0),
        "display": (0.05, 0.07, 0.09, 1.0),
        "tray": (0.09, 0.09, 0.10, 1.0),
    },
    "pastel_cream": {
        "shell": (0.92, 0.88, 0.78, 1.0),
        "rim": (0.78, 0.76, 0.70, 1.0),
        "panel": (0.94, 0.91, 0.83, 1.0),
        "dark": (0.30, 0.29, 0.28, 1.0),
        "knob": (0.74, 0.75, 0.77, 1.0),
        "control": (0.40, 0.39, 0.38, 1.0),
        "button": (0.80, 0.81, 0.83, 1.0),
        "carriage": (0.66, 0.66, 0.64, 1.0),
        "mark": (0.32, 0.31, 0.30, 1.0),
        "display": (0.10, 0.14, 0.12, 1.0),
        "tray": (0.55, 0.54, 0.50, 1.0),
    },
    "brushed_steel": {
        "shell": (0.74, 0.75, 0.77, 1.0),
        "rim": (0.66, 0.67, 0.69, 1.0),
        "panel": (0.30, 0.31, 0.33, 1.0),
        "dark": (0.10, 0.10, 0.11, 1.0),
        "knob": (0.20, 0.20, 0.22, 1.0),
        "control": (0.16, 0.16, 0.18, 1.0),
        "button": (0.12, 0.12, 0.13, 1.0),
        "carriage": (0.60, 0.61, 0.63, 1.0),
        "mark": (0.86, 0.87, 0.89, 1.0),
        "display": (0.04, 0.06, 0.08, 1.0),
        "tray": (0.20, 0.20, 0.21, 1.0),
    },
    "retro_red": {
        "shell": (0.78, 0.80, 0.85, 1.0),
        "rim": (0.66, 0.68, 0.72, 1.0),
        "panel": (0.74, 0.10, 0.10, 1.0),
        "dark": (0.12, 0.12, 0.13, 1.0),
        "knob": (0.80, 0.81, 0.84, 1.0),
        "control": (0.20, 0.20, 0.22, 1.0),
        "button": (0.82, 0.83, 0.86, 1.0),
        "carriage": (0.62, 0.63, 0.66, 1.0),
        "mark": (0.90, 0.90, 0.92, 1.0),
        "display": (0.05, 0.07, 0.09, 1.0),
        "tray": (0.60, 0.10, 0.10, 1.0),
    },
}


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class ToasterConfig:
    browning_control: BrowningControl | None = None
    lever_placement: LeverPlacement | None = None
    crumb_tray: CrumbTray | None = None
    body_silhouette: BodySilhouette | None = None
    slot_count: int | None = None
    palette_style: PaletteStyle = "chrome_silver"
    body_len_scale: float = 1.0
    body_width_scale: float = 1.0
    body_height_scale: float = 1.0
    lever_travel_scale: float = 1.0
    browning_range_scale: float = 1.0
    tray_travel_scale: float = 1.0
    slot_pitch_scale: float = 1.0
    name: str = "toaster"


@dataclass(frozen=True)
class ResolvedToasterConfig:
    browning_control: BrowningControl
    lever_placement: LeverPlacement
    crumb_tray: CrumbTray
    body_silhouette: BodySilhouette
    slot_count: int
    palette_style: PaletteStyle
    # Derived / scaled geometry.
    body_l: float
    body_w: float
    body_h: float
    foot_h: float
    cav_y: float
    cav_z0: float
    cav_z1: float
    slot_cut_z0: float
    recess_z0: float
    recess_w: float
    panel_z1: float
    lever_rest_z: float
    lever_slot_z1: float
    lever_slot_x0: float
    slot_l: float
    slot_yc: float
    slot_positions: tuple[tuple[float, float], ...]
    recess_l: float
    lever_travel: float
    browning_range: float  # meaningful only for rotary_dial / slider
    tray_travel: float  # meaningful only for pullout
    name: str

    @property
    def shell_face_x(self) -> float:
        return self.body_l / 2.0

    @property
    def panel_x0(self) -> float:
        return self.shell_face_x - 0.0005

    @property
    def panel_x1(self) -> float:
        return self.panel_x0 + PANEL_T

    @property
    def shell_h(self) -> float:
        return self.body_h - self.foot_h

    @property
    def shell_top(self) -> float:
        return self.body_h


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> ToasterConfig:
    rng = random.Random(seed)
    body_silhouette = rng.choice(BODY_SILHOUETTES)
    browning = rng.choice(BROWNING_CONTROLS)
    # side_lever requires a flat side wall -> square_box only (spec §9 #2).
    if body_silhouette == "retro_round":
        lever = "front_lever"
    else:
        lever = rng.choice(LEVER_PLACEMENTS)
    crumb = rng.choice(CRUMB_TRAYS)
    # retro_round gates slot_count to N=2 (dome taper, spec §9 #1).
    if body_silhouette == "retro_round":
        slot_count = 2
    else:
        slot_count = rng.choices(_SLOT_COUNT_CHOICES, weights=_SLOT_COUNT_WEIGHTS, k=1)[0]
    return ToasterConfig(
        browning_control=browning,
        lever_placement=lever,
        crumb_tray=crumb,
        body_silhouette=body_silhouette,
        slot_count=slot_count,
        palette_style=rng.choice(PALETTE_STYLES),
        body_len_scale=round(rng.uniform(0.92, 1.10), 4),
        body_width_scale=round(rng.uniform(0.92, 1.10), 4),
        body_height_scale=round(rng.uniform(0.90, 1.12), 4),
        lever_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        browning_range_scale=round(rng.uniform(0.85, 1.10), 4),
        tray_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        slot_pitch_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_toaster_{seed}",
    )


def _slot_positions(slot_count: int, slot_yc: float, slot_l: float) -> tuple[tuple[float, float], ...]:
    """Absolute (xc, yc) of each bread slot. No drift: each position is resolved
    from N + layout. N=2 -> one X-center pair ±yc; N=4 -> two X pairs; N=3 ->
    one pair + one centered single (front pair becomes a single centered slot)."""
    if slot_count == 2:
        return ((0.0, slot_yc), (0.0, -slot_yc))
    if slot_count == 4:
        return tuple(
            (px, py)
            for px in (-SLOT_PAIR_DX, SLOT_PAIR_DX)
            for py in (slot_yc, -slot_yc)
        )
    # N=3: rear pair (±yc) + one centered front slot.
    return (
        (-SLOT_PAIR_DX, slot_yc),
        (-SLOT_PAIR_DX, -slot_yc),
        (SLOT_PAIR_DX, 0.0),
    )


def resolve_config(config: ToasterConfig | None = None) -> ResolvedToasterConfig:
    cfg = config or ToasterConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    browning = _pick(cfg.browning_control, BROWNING_CONTROLS)
    lever = _pick(cfg.lever_placement, LEVER_PLACEMENTS)
    crumb = _pick(cfg.crumb_tray, CRUMB_TRAYS)
    silhouette = _pick(cfg.body_silhouette, BODY_SILHOUETTES)

    # --- slot_count clamp + compatibility gating. ---
    slot_count = int(cfg.slot_count) if cfg.slot_count is not None else 2
    slot_count = int(_clamp(slot_count, N_SLOT_MIN, N_SLOT_MAX))
    if silhouette == "retro_round":
        slot_count = 2  # dome taper -> single Y pair only (spec §9 #1)
    if lever == "side_lever" and silhouette == "retro_round":
        lever = "front_lever"  # side lever needs a flat wall (spec §9 #2)

    # --- continuous scales (clamped to declared ranges). ---
    len_scale = _clamp(cfg.body_len_scale, 0.92, 1.10)
    width_scale = _clamp(cfg.body_width_scale, 0.92, 1.10)
    height_scale = _clamp(cfg.body_height_scale, 0.90, 1.12)
    lever_travel_scale = _clamp(cfg.lever_travel_scale, 0.85, 1.10)
    browning_range_scale = _clamp(cfg.browning_range_scale, 0.85, 1.10)
    tray_travel_scale = _clamp(cfg.tray_travel_scale, 0.85, 1.10)
    pitch_scale = _clamp(cfg.slot_pitch_scale, 0.90, 1.10)

    # --- body length derived from N, then len-scaled. ---
    if slot_count >= 4:
        base_len = BODY_L_4SLICE
        slot_l = SLOT_L_4SLICE
    elif slot_count == 3:
        base_len = (BODY_L_2SLICE + BODY_L_4SLICE) / 2.0  # 0.338
        slot_l = SLOT_L_4SLICE
    else:
        base_len = BODY_L_2SLICE
        slot_l = SLOT_L_2SLICE
    body_l = base_len * len_scale
    body_w = BODY_W * width_scale
    body_h = BODY_H * height_scale

    # --- slot pitch (N>=2): scale the ±Y pair separation, clamp under the top. ---
    slot_yc = SLOT_YC * pitch_scale
    # Keep the Y pair inside the top face (margin from the rim plate edge).
    max_yc = (RECESS_W * width_scale) / 2.0 - SLOT_W / 2.0 - 0.006
    slot_yc = _clamp(slot_yc, 0.022, max_yc)

    slot_positions = _slot_positions(slot_count, slot_yc, slot_l)
    # Recess plate spans all slots in X with margin.
    xs = [xc for xc, _ in slot_positions]
    recess_l = (max(xs) - min(xs)) + slot_l + 0.020
    recess_w = (RETRO_RECESS_W if silhouette == "retro_round" else RECESS_W) * 1.0

    # --- silhouette-dependent Z anchors. ---
    # The rim plate (thickness RIM_T, unscaled) must always sit just below the
    # scaled shell top, so anchor recess_z0 to shell_top minus a fixed gap
    # (square_box gap 0.005, retro_round gap 0.015 in the sources) rather than
    # scaling the absolute recess_z0 (which breaks against the fixed RIM_T).
    shell_top = body_h
    if silhouette == "retro_round":
        cav_z1 = RETRO_CAV_Z1 * height_scale
        slot_cut_z0 = RETRO_SLOT_CUT_Z0 * height_scale
        recess_z0 = shell_top - (BODY_H - RETRO_RECESS_Z0)  # gap 0.015
        panel_z1 = RETRO_PANEL_Z1 * height_scale
        lever_rest_z = RETRO_LEVER_REST_Z * height_scale
        lever_slot_z1 = RETRO_LEVER_SLOT_Z1 * height_scale
        lever_slot_x0 = RETRO_LEVER_SLOT_X0
        cav_y = CAV_Y * width_scale
    else:
        cav_z1 = CAV_Z1 * height_scale
        slot_cut_z0 = SLOT_CUT_Z0 * height_scale
        recess_z0 = shell_top - (BODY_H - RECESS_Z0)  # gap 0.005
        panel_z1 = PANEL_Z1 * height_scale
        lever_rest_z = LEVER_REST_Z * height_scale
        lever_slot_z1 = LEVER_SLOT_Z1 * height_scale
        lever_slot_x0 = None  # filled below from body_l
        cav_y = CAV_Y * width_scale
    cav_z0 = CAV_Z0 * height_scale
    # Keep the slot top-cut starting just below recess so the slot still opens.
    slot_cut_z0 = min(slot_cut_z0, recess_z0 - 0.010)

    # --- lever travel: clamp so the pressed shelf stays above the cavity floor. ---
    lever_travel = LEVER_TRAVEL * lever_travel_scale
    # shelf rest center ~= lever_rest_z; pressed center = rest - travel; shelf half
    # height ~0.0025. Keep pressed shelf bottom > cav_z0 + 0.006.
    shelf_half_h = 0.0025
    max_travel = (lever_rest_z - shelf_half_h) - (cav_z0 + 0.008)
    lever_travel = _clamp(lever_travel, 0.030, max(0.030, max_travel))

    # --- browning range (conditional on control type). ---
    if browning == "rotary_dial":
        browning_range = min(DIAL_RANGE * browning_range_scale, math.radians(300.0))
    elif browning == "slider":
        browning_range = min(SLIDER_TRAVEL * browning_range_scale, SLIDER_TRAVEL * 1.15)
    else:
        browning_range = DIGI_BTN_TRAVEL  # digital pads fixed

    # --- tray travel (conditional on pullout); keep >=0.040 retained insertion. ---
    tray_l = _tray_len(body_l)
    tray_travel = TRAY_TRAVEL * tray_travel_scale
    tray_travel = min(tray_travel, 0.95 * (tray_l - 0.040))

    return ResolvedToasterConfig(
        browning_control=browning,
        lever_placement=lever,
        crumb_tray=crumb,
        body_silhouette=silhouette,
        slot_count=slot_count,
        palette_style=palette_style,
        body_l=body_l,
        body_w=body_w,
        body_h=body_h,
        foot_h=FOOT_H * 1.0,
        cav_y=cav_y,
        cav_z0=cav_z0,
        cav_z1=cav_z1,
        slot_cut_z0=slot_cut_z0,
        recess_z0=recess_z0,
        recess_w=recess_w,
        panel_z1=panel_z1,
        lever_rest_z=lever_rest_z,
        lever_slot_z1=lever_slot_z1,
        lever_slot_x0=(lever_slot_x0 if lever_slot_x0 is not None else body_l / 2.0 - 0.022),
        slot_l=slot_l,
        slot_yc=slot_yc,
        slot_positions=slot_positions,
        recess_l=recess_l,
        lever_travel=lever_travel,
        browning_range=browning_range,
        tray_travel=tray_travel,
        name=cfg.name or "toaster",
    )


def _tray_len(body_l: float) -> float:
    """Crumb tray X length: spans the cavity floor, inset from both faces."""
    return max(0.140, body_l - 0.040)


def _tray_pocket_x_bounds(r: ResolvedToasterConfig) -> tuple[float, float]:
    """Bottom tray channel X bounds, open through the exterior shell faces."""
    through_margin = 0.012
    return -r.shell_face_x - through_margin, r.shell_face_x + through_margin


def with_overrides(config: ToasterConfig, **kwargs: object) -> ToasterConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ToasterConfig | ResolvedToasterConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedToasterConfig) else resolve_config(config)
    return (
        ("body_silhouette", r.body_silhouette),
        ("browning_control", r.browning_control),
        ("lever_placement", r.lever_placement),
        ("crumb_tray", r.crumb_tray),
        ("slot_count", f"n{r.slot_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# CadQuery primitives (照搬 sources)
# ===========================================================================
def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0)
        .translate(((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0))
    )


def _xcyl(x0: float, x1: float, y: float, z: float, r: float) -> cq.Workplane:
    """Cylinder along +X from x0 to x1 at (y, z)."""
    return cq.Workplane("YZ").circle(r).extrude(x1 - x0).translate((x0, y, z))


def _cav_x(r: ResolvedToasterConfig) -> tuple[float, float]:
    """Cavity X bounds, inset from the body faces."""
    x1 = r.shell_face_x - CAV_X_MARGIN
    x0 = -r.body_l / 2.0 + CAV_X_BACK_MARGIN
    return x0, x1


def _wall_cut_x(r: ResolvedToasterConfig) -> tuple[float, float]:
    """X range used for front-wall slot/hole cuts (straddles the +X wall)."""
    return r.shell_face_x - 0.022, r.shell_face_x + 0.012


# ===========================================================================
# Shell + rim + panel mesh helpers
# ===========================================================================
def _apply_front_wall_cuts(s: cq.Workplane, r: ResolvedToasterConfig) -> cq.Workplane:
    """Lever slot (front only) + button holes + browning hole through +X wall."""
    wx0, wx1 = _wall_cut_x(r)
    # vertical lever slot (front_lever only)
    if r.lever_placement == "front_lever":
        lx0 = r.lever_slot_x0
        s = s.cut(
            _box(
                lx0,
                wx1,
                LEVER_YC - LEVER_SLOT_W / 2.0,
                LEVER_YC + LEVER_SLOT_W / 2.0,
                LEVER_SLOT_Z0,
                r.lever_slot_z1,
            )
        )
    # button stem holes
    for z in BTN_Z:
        s = s.cut(_xcyl(wx0, wx1, BTN_Y, z, BTN_HOLE_R))
    # browning control passage
    if r.browning_control == "rotary_dial":
        s = s.cut(_xcyl(wx0, wx1, DIAL_Y, DIAL_Z, DIAL_HOLE_R))
    elif r.browning_control == "slider":
        z0 = SLIDER_REST_Z - SLIDER_TAB_H / 2.0 - 0.001
        z1 = SLIDER_REST_Z + r.browning_range + SLIDER_TAB_H / 2.0 + 0.001
        s = s.cut(_box(wx0, wx1, SLIDER_Y - TRACK_SLOT_W / 2.0, SLIDER_Y + TRACK_SLOT_W / 2.0, z0, z1))
    else:  # digital
        for z in _digi_btn_z():
            s = s.cut(_xcyl(wx0, wx1, DIGI_Y, z, DIGI_BTN_HOLE_R))
    return s


def _apply_side_lever_cut(s: cq.Workplane, r: ResolvedToasterConfig) -> cq.Workplane:
    """Vertical lever slot through the +Y side wall (side_lever only)."""
    s = s.cut(
        _box(
            LEVER_XC_SIDE - LEVER_SLOT_W / 2.0,
            LEVER_XC_SIDE + LEVER_SLOT_W / 2.0,
            r.cav_y - 0.002,
            r.body_w / 2.0 + 0.01,
            LEVER_SLOT_Z0,
            r.lever_slot_z1,
        )
    )
    return s


def _apply_tray_pocket_cut(s: cq.Workplane, r: ResolvedToasterConfig) -> cq.Workplane:
    # Snug pocket: small clearance so the tray stays in CONTACT with the shell
    # at rest (captured slide). Too much clearance lets the tray float free of
    # the body and trip fail_if_isolated_parts.
    pocket_x0, pocket_x1 = _tray_pocket_x_bounds(r)
    pocket_w = TRAY_W + 0.0015
    pocket_z_top = TRAY_Z_BASE + TRAY_TOTAL_H + 0.0008
    # Cut the pocket all the way through the shell floor and both exterior X
    # faces, so the pull-out tray has a real open channel instead of a blind
    # bottom recess hidden behind a closed outside wall. The solid side-wall
    # floor band (outboard of pocket_w) carries the feet.
    s = s.cut(
        _box(
            pocket_x0,
            pocket_x1,
            -pocket_w / 2.0,
            pocket_w / 2.0,
            -0.01,
            pocket_z_top,
        )
    )
    return s


def _apply_top_cuts(s: cq.Workplane, r: ResolvedToasterConfig) -> cq.Workplane:
    """Cavity + N bread-slot openings + recess for the rim plate."""
    cx0, cx1 = _cav_x(r)
    s = s.cut(_box(cx0, cx1, -r.cav_y, r.cav_y, r.cav_z0, r.cav_z1))
    for xc, yc in r.slot_positions:
        s = s.cut(
            _box(
                xc - r.slot_l / 2.0,
                xc + r.slot_l / 2.0,
                yc - SLOT_W / 2.0,
                yc + SLOT_W / 2.0,
                r.slot_cut_z0,
                r.shell_top + 0.01,
            )
        )
    s = s.cut(
        _box(
            -r.recess_l / 2.0,
            r.recess_l / 2.0,
            -r.recess_w / 2.0,
            r.recess_w / 2.0,
            r.recess_z0,
            r.shell_top + 0.01,
        )
    )
    return s


def _shell_shape(r: ResolvedToasterConfig) -> cq.Workplane:
    if r.body_silhouette == "retro_round":
        mid_offset = r.shell_h * 0.48
        top_offset = r.shell_h * 0.52
        s = (
            cq.Workplane("XY", origin=(0.0, 0.0, r.foot_h))
            .slot2D(r.body_l * LOFT_BOTTOM_L_F, r.body_w * LOFT_BOTTOM_W_F)
            .workplane(offset=mid_offset)
            .slot2D(r.body_l * LOFT_MIDDLE_L_F, r.body_w * LOFT_MIDDLE_W_F)
            .workplane(offset=top_offset)
            .slot2D(r.body_l * LOFT_TOP_L_F, r.body_w * LOFT_TOP_W_F)
            .loft()
        )
        for sel, rad in ((">Z", 0.016), ("<Z", 0.005)):
            try:
                s = s.edges(sel).fillet(rad)
            except Exception:
                pass
    else:
        s = (
            cq.Workplane("XY", origin=(0.0, 0.0, r.foot_h))
            .box(r.body_l, r.body_w, r.shell_h, centered=(True, True, False))
        )
        for sel, rad in (("|Z", 0.030), (">Z", 0.016), ("<Z", 0.005)):
            try:
                s = s.edges(sel).fillet(rad)
            except Exception:
                pass

    s = _apply_top_cuts(s, r)
    s = _apply_front_wall_cuts(s, r)
    if r.lever_placement == "side_lever":
        s = _apply_side_lever_cut(s, r)
    if r.crumb_tray == "pullout":
        s = _apply_tray_pocket_cut(s, r)
    return s


def _rim_plate_shape(r: ResolvedToasterConfig) -> cq.Workplane:
    p = (
        cq.Workplane("XY", origin=(0.0, 0.0, r.recess_z0 - 0.0002))
        .box(r.recess_l - 0.001, r.recess_w - 0.002, RIM_T, centered=(True, True, False))
    )
    try:
        p = p.edges("|Z").fillet(0.006)
    except Exception:
        pass
    for xc, yc in r.slot_positions:
        p = p.cut(
            _box(
                xc - r.slot_l / 2.0 - 0.001,
                xc + r.slot_l / 2.0 + 0.001,
                yc - SLOT_W / 2.0 - 0.00075,
                yc + SLOT_W / 2.0 + 0.00075,
                r.recess_z0 - 0.01,
                r.shell_top + 0.01,
            )
        )
    return p


def _panel_shape(r: ResolvedToasterConfig) -> cq.Workplane:
    panel_z0 = PANEL_Z0 * (r.body_h / BODY_H)
    panel_zc = (panel_z0 + r.panel_z1) / 2.0
    p = (
        cq.Workplane("YZ", origin=(r.panel_x0, 0.0, panel_zc))
        .rect(PANEL_W, r.panel_z1 - panel_z0)
        .extrude(PANEL_T)
    )
    try:
        p = p.edges("|X").fillet(0.010)
    except Exception:
        pass
    px0, px1 = r.panel_x0 - 0.005, r.panel_x1 + 0.005
    # lever slot (front mount only)
    if r.lever_placement == "front_lever":
        p = p.cut(
            _box(
                px0,
                px1,
                LEVER_YC - LEVER_SLOT_W / 2.0,
                LEVER_YC + LEVER_SLOT_W / 2.0,
                LEVER_SLOT_Z0,
                r.lever_slot_z1,
            )
        )
    # button holes
    for z in BTN_Z:
        p = p.cut(_xcyl(px0, px1, BTN_Y, z, BTN_HOLE_R))
    # browning passage
    if r.browning_control == "rotary_dial":
        p = p.cut(_xcyl(px0, px1, DIAL_Y, DIAL_Z, DIAL_HOLE_R))
    elif r.browning_control == "slider":
        z0 = SLIDER_REST_Z - SLIDER_TAB_H / 2.0 - 0.001
        z1 = SLIDER_REST_Z + r.browning_range + SLIDER_TAB_H / 2.0 + 0.001
        p = p.cut(_box(px0, px1, SLIDER_Y - TRACK_SLOT_W / 2.0, SLIDER_Y + TRACK_SLOT_W / 2.0, z0, z1))
    else:
        for z in _digi_btn_z():
            p = p.cut(_xcyl(px0, px1, DIGI_Y, z, DIGI_BTN_HOLE_R))
    return p


def _side_guide_shape(r: ResolvedToasterConfig) -> cq.Workplane:
    """Lighter-gray guide plate on the +Y side, flanking the lever slot."""
    gw = 0.048
    gt = 0.004
    gh = r.lever_slot_z1 - LEVER_SLOT_Z0 + 0.016
    gzc = (LEVER_SLOT_Z0 + r.lever_slot_z1) / 2.0
    y_inner = r.body_w / 2.0
    g = cq.Workplane("XY").box(gw, gt, gh).translate((LEVER_XC_SIDE, y_inner + gt / 2.0, gzc))
    try:
        g = g.edges("|Y").fillet(0.004)
    except Exception:
        pass
    slot_hw = LEVER_SLOT_W / 2.0 + 0.002
    g = g.cut(
        _box(
            LEVER_XC_SIDE - slot_hw,
            LEVER_XC_SIDE + slot_hw,
            y_inner - 0.01,
            y_inner + gt + 0.01,
            LEVER_SLOT_Z0 - 0.005,
            r.lever_slot_z1 + 0.005,
        )
    )
    return g


def _front_lever_knob_shape() -> cq.Workplane:
    k = cq.Workplane("XY").box(0.014, 0.024, 0.016)
    return k.edges().fillet(0.003)


def _side_lever_knob_shape() -> cq.Workplane:
    k = cq.Workplane("XY").box(0.034, 0.014, 0.018)
    return k.edges().fillet(0.003)


def _slider_tab_shape() -> cq.Workplane:
    tab = cq.Workplane("XY").box(SLIDER_TAB_D, SLIDER_TAB_W, SLIDER_TAB_H)
    for sel, rad in (("|Z", 0.002), (">Z", 0.0015), ("<Z", 0.0015)):
        try:
            tab = tab.edges(sel).fillet(rad)
        except Exception:
            pass
    return tab


def _rounded_pad(w: float, h: float, d: float, fillet: float = 0.0015) -> cq.Workplane:
    return cq.Workplane("YZ").rect(w, h).extrude(d).edges("|X").fillet(fillet)


def _crumb_tray_shape(r: ResolvedToasterConfig) -> cq.Workplane:
    tray_l = _tray_len(r.body_l)
    base = (
        cq.Workplane("XY")
        .box(tray_l, TRAY_W, TRAY_T, centered=(True, True, False))
        .translate((0.0, 0.0, 0.0))
    )
    back = (
        cq.Workplane("XY")
        .box(TRAY_LIP_T, TRAY_W - 2 * TRAY_LIP_T, TRAY_LIP_H, centered=(True, True, False))
        .translate((-tray_l / 2.0 + TRAY_LIP_T / 2.0, 0.0, TRAY_T))
    )
    for sign in (-1.0, 1.0):
        lip = (
            cq.Workplane("XY")
            .box(tray_l - 2 * TRAY_LIP_T, TRAY_LIP_T, TRAY_LIP_H, centered=(True, True, False))
            .translate((0.0, sign * (TRAY_W / 2.0 - TRAY_LIP_T / 2.0), TRAY_T))
        )
        base = base.union(lip)
    base = base.union(back)
    tab = (
        cq.Workplane("XY")
        .box(TRAY_TAB_T, TRAY_TAB_W, TRAY_TAB_H, centered=(True, True, False))
        .translate((tray_l / 2.0 - TRAY_TAB_T / 2.0, 0.0, 0.0))
    )
    base = base.union(tab)
    try:
        base = base.edges(">Z").edges(
            cq.selectors.BoxSelector(
                (tray_l / 2.0 - TRAY_TAB_T - 0.001, -TRAY_TAB_W / 2.0 - 0.001, TRAY_TAB_H - 0.002),
                (tray_l / 2.0 + TRAY_TAB_T + 0.001, TRAY_TAB_W / 2.0 + 0.001, TRAY_TAB_H + 0.002),
            )
        ).fillet(0.002)
    except Exception:
        pass
    return base


def _digi_btn_z() -> tuple[float, float]:
    return (
        DIGI_DISPLAY_Z + DIGI_DISPLAY_H / 2.0 + 0.006 + DIGI_BTN_H / 2.0,  # UP
        DIGI_DISPLAY_Z - DIGI_DISPLAY_H / 2.0 - 0.006 - DIGI_BTN_H / 2.0,  # DOWN
    )


# ===========================================================================
# Body (root) assembly
# ===========================================================================
def _build_body(model, r, mats, *, assets):
    body = model.part("body")
    body.visual(
        mesh_from_cadquery(_shell_shape(r), "shell", assets=assets),
        material=mats["shell"],
        name="shell", material_class_id=("metal.paint_coated" if r.palette_style in {"chrome_silver", "matte_black", "pastel_cream", "retro_red"} else "metal.brushed_silver"),
    )
    body.visual(
        mesh_from_cadquery(_rim_plate_shape(r), "slot_rim_plate", assets=assets),
        material=mats["rim"],
        name="slot_rim_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"matte_black", "pastel_cream", "retro_red"} else "metal.brushed_silver"),
    )
    body.visual(
        mesh_from_cadquery(_panel_shape(r), "control_panel", assets=assets),
        material=mats["panel"],
        name="control_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"matte_black", "pastel_cream", "retro_red"} else "metal.brushed_silver"),
    )
    if r.lever_placement == "side_lever":
        body.visual(
            mesh_from_cadquery(_side_guide_shape(r), "lever_guide_plate", assets=assets),
            material=mats["rim"],
            name="lever_guide_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"matte_black", "pastel_cream", "retro_red"} else "metal.brushed_silver"),
        )
    # Four feet at the outer corners, seated under the SOLID shell floor band
    # along the +/-Y side walls (outboard of BOTH the crumb-tray pocket void
    # and the tray body, which occupy the central floor). The foot embeds
    # ~0.006 up into the shell so it is never a floating island, and its inner
    # edge clears the tray body so the rest pose has no foot/tray overlap.
    foot_len = r.foot_h + 0.006
    foot_r = FOOT_R
    # The bottom-floor footprint: square_box keeps the full body box; retro_round
    # lofts from a slightly smaller rounded slot (body_l*0.99 x body_w*0.97) with
    # rounded ends, so retro feet must pull well inside that rounded floor.
    if r.body_silhouette == "retro_round":
        floor_half_l = r.body_l * LOFT_BOTTOM_L_F / 2.0
        floor_half_w = r.body_w * LOFT_BOTTOM_W_F / 2.0
        fx = floor_half_l - 0.045  # inside the rounded X ends
    else:
        floor_half_w = r.body_w / 2.0
        fx = r.body_l / 2.0 - 0.020
    # Y placement: foot disc fully outboard of the tray pocket void (so it never
    # floats off the solid side-floor band) and clear of the tray body, but
    # inside the floor footprint.
    pocket_half_w = (TRAY_W + 0.0015) / 2.0  # matches _apply_tray_pocket_cut
    fy_hi = floor_half_w - foot_r - 0.002
    fy_lo = max(pocket_half_w + 0.001, TRAY_W / 2.0 + foot_r + 0.001)
    if fy_lo > fy_hi:
        # Tight floor (narrow retro / scaled-down body): shrink the foot so it
        # still sits on solid floor outboard of the tray pocket.
        foot_r = max(0.005, (fy_hi + 0.002 - TRAY_W / 2.0 - 0.001))
        pocket_half_w = (TRAY_W + 0.0015) / 2.0
        fy_lo = max(pocket_half_w + 0.001, TRAY_W / 2.0 + foot_r + 0.001)
        fy_hi = floor_half_w - foot_r - 0.002
    fy = _clamp(floor_half_w - 0.018, fy_lo, max(fy_lo, fy_hi))
    for i, (sx, sy) in enumerate([(-1, -1), (-1, 1), (1, -1), (1, 1)]):
        body.visual(
            Cylinder(radius=foot_r, length=foot_len),
            origin=Origin(xyz=(sx * fx, sy * fy, foot_len / 2.0)),
            material=mats["dark"],
            name=f"foot_{i}", material_class_id="rubber.smooth_plain",
        )

    px1 = r.panel_x1
    # browning marks / display (inline body visuals, Rule 1)
    if r.browning_control == "rotary_dial":
        tick_r = 0.0205
        for i, ang_deg in enumerate((235.0, 180.0, 125.0, 70.0)):
            t = math.radians(ang_deg)
            body.visual(
                Box((0.0018, 0.0024, 0.0024)),
                origin=Origin(
                    xyz=(px1 + 0.0006, DIAL_Y + tick_r * math.cos(t), DIAL_Z + tick_r * math.sin(t))
                ),
                material=mats["mark"],
                name=f"dial_mark_{i + 1}", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
    elif r.browning_control == "slider":
        mark_y = SLIDER_Y + 0.014
        for i in range(4):
            mark_z = SLIDER_REST_Z + (i / 3.0) * r.browning_range
            body.visual(
                Box((0.0018, 0.008, 0.002)),
                origin=Origin(xyz=(px1 + 0.0006, mark_y, mark_z)),
                material=mats["mark"],
                name=f"slider_mark_{i + 1}", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
    else:  # digital display + bezel
        body.visual(
            Box((0.0008, DIGI_DISPLAY_W + 0.004, DIGI_DISPLAY_H + 0.004)),
            origin=Origin(xyz=(px1 + 0.0001, DIGI_Y, DIGI_DISPLAY_Z)),
            material=mats["dark"],
            name="display_bezel", material_class_id="plastic.opaque_glossy_molded",
        )
        body.visual(
            Box((0.001, DIGI_DISPLAY_W, DIGI_DISPLAY_H)),
            origin=Origin(xyz=(px1 + 0.0002, DIGI_Y, DIGI_DISPLAY_Z)),
            material=mats["display"],
            name="digital_display", material_class_id="tech.emissive_surface",
        )

    # brand strip near the top of the panel
    body.visual(
        Box((0.0014, 0.044, 0.0065)),
        origin=Origin(xyz=(px1 + 0.0004, 0.000, min(0.1660, r.panel_z1 - 0.006))),
        material=mats["mark"],
        name="brand_strip", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    body.inertial = Inertial.from_geometry(
        Box((r.body_l, r.body_w, r.shell_h)),
        mass=1.6,
        origin=Origin(xyz=(0.0, 0.0, r.foot_h + r.shell_h / 2.0)),
    )
    return body


# ===========================================================================
# Carriage lever (defining motion — single PRISMATIC, N shelves)
# ===========================================================================
def _build_carriage(model, r, mats, body, *, assets):
    carriage = model.part("carriage_lever")
    xs = [xc for xc, _ in r.slot_positions]
    multi_x = (max(xs) - min(xs)) > 0.01  # X-distributed slot pairs (N>=3)
    # Crossbar Y-span covers every shelf Y-line (all |yc|<=slot_yc) yet stays
    # inside the cavity so it never pokes into the solid shell walls.
    ys = [yc for _, yc in r.slot_positions]
    crossbar_w = min(2.0 * r.cav_y - 0.010, max(0.060, (max(ys) - min(ys)) + 0.024))

    if r.lever_placement == "side_lever":
        carriage_origin_x = LEVER_XC_SIDE
        carriage_origin_y = r.body_w / 2.0
        # side-mount knob extends +Y from the side wall surface
        carriage.visual(
            mesh_from_cadquery(_side_lever_knob_shape(), "lever_knob", assets=assets),
            origin=Origin(xyz=(0.0, 0.007, 0.0)),
            material=mats["knob"],
            name="lever_knob", material_class_id="plastic.opaque_glossy_molded",
        )
        # Stem spans from the knob (y~0) all the way IN to the crossbar so the
        # knob/stem/crossbar are one connected component regardless of body_w.
        stem_len_y = carriage_origin_y - r.cav_y + 0.030
        carriage.visual(
            Box((0.010, stem_len_y, 0.008)),
            origin=Origin(xyz=(0.0, -stem_len_y / 2.0 + 0.004, 0.0)),
            material=mats["carriage"],
            name="lever_stem", material_class_id="metal.stainless_matte",
        )
        carriage.visual(
            Box((0.012, crossbar_w, 0.012)),
            origin=Origin(xyz=(0.0, -carriage_origin_y, 0.0)),
            material=mats["carriage"],
            name="carriage_crossbar", material_class_id="metal.stainless_matte",
        )
        shelf_dx = lambda xc: xc - carriage_origin_x  # noqa: E731
        shelf_dy = lambda yc: yc - carriage_origin_y  # noqa: E731
        shelf_len = max(0.150, r.body_l - 0.070)
        crossbar_x_rel = 0.0
    else:
        carriage_origin_x = r.shell_face_x - 0.010
        carriage_origin_y = LEVER_YC
        carriage.visual(
            mesh_from_cadquery(_front_lever_knob_shape(), "lever_knob", assets=assets),
            origin=Origin(xyz=(0.0188, 0.0, 0.0)),
            material=mats["knob"],
            name="lever_knob", material_class_id="plastic.opaque_glossy_molded",
        )
        carriage.visual(
            Box((0.030, 0.008, 0.010)),
            origin=Origin(xyz=(-0.001, 0.0, 0.0)),
            material=mats["carriage"],
            name="lever_stem", material_class_id="metal.stainless_matte",
        )
        carriage.visual(
            Box((0.012, crossbar_w, 0.012)),
            origin=Origin(xyz=(-0.020, -LEVER_YC, 0.0)),
            material=mats["carriage"],
            name="carriage_crossbar", material_class_id="metal.stainless_matte",
        )
        shelf_dx = lambda xc: xc - carriage_origin_x  # noqa: E731
        shelf_dy = lambda yc: yc - LEVER_YC  # noqa: E731
        shelf_len = max(0.150, r.body_l - 0.050)
        crossbar_x_rel = -0.020

    # Longitudinal rail per distinct shelf Y-line: each runs from the crossbar
    # X out to (just past) the farthest shelf at that Y, so EVERY shelf has a
    # rigid connection back to the crossbar/stem/knob (one component).
    distinct_ys = sorted(set(round(yc, 5) for yc in ys))
    for j, yline in enumerate(distinct_ys):
        # Rail spans in X from the crossbar to the rearmost shelf at this Y line.
        line_xs = [xc for xc, yc in r.slot_positions if round(yc, 5) == yline]
        rail_rear_x = min(line_xs) - r.slot_l / 2.0 + 0.010 if multi_x else 0.0
        rail_front_x = carriage_origin_x + crossbar_x_rel  # crossbar X (world)
        if rail_rear_x > rail_front_x:
            rail_rear_x, rail_front_x = rail_front_x, rail_rear_x
        rail_span = max(0.030, rail_front_x - rail_rear_x)
        rail_cx = (rail_rear_x + rail_front_x) / 2.0
        carriage.visual(
            Box((rail_span, 0.008, 0.008)),
            origin=Origin(xyz=(rail_cx - carriage_origin_x, yline - carriage_origin_y, 0.0)),
            material=mats["carriage"],
            name=f"side_rail_{j}", material_class_id="metal.stainless_matte",
        )

    for i, (xc, yc) in enumerate(r.slot_positions):
        # Per-shelf length matches its slot (multi-pair shelves are shorter).
        if multi_x:
            s_len = r.slot_l - 0.010
            s_x = shelf_dx(xc)
        else:
            s_len = shelf_len
            s_x = shelf_dx(0.0)
        carriage.visual(
            Box((s_len, 0.024, 0.005)),
            origin=Origin(xyz=(s_x, shelf_dy(yc), 0.0)),
            material=mats["carriage"],
            name=f"bread_shelf_{i}", material_class_id="metal.stainless_matte",
        )

    carriage.inertial = Inertial.from_geometry(
        Box((shelf_len, r.body_w * 0.6, 0.030)),
        mass=0.4,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    model.articulation(
        "body_to_carriage_lever",
        ArticulationType.PRISMATIC,
        parent=body,
        child=carriage,
        origin=Origin(xyz=(carriage_origin_x, carriage_origin_y, r.lever_rest_z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=15.0, velocity=0.3, lower=0.0, upper=r.lever_travel),
    )
    return carriage


# ===========================================================================
# Browning control (Slot A)
# ===========================================================================
def _build_rotary_dial(model, r, mats, body, *, assets):
    dial_geo = KnobGeometry(
        DIAL_D,
        DIAL_H,
        body_style="cylindrical",
        edge_radius=0.0015,
        grip=KnobGrip(style="ribbed", count=14, depth=0.0006, width=0.0016),
        indicator=KnobIndicator(style="line", mode="raised", angle_deg=0.0, depth=0.0006),
        center=False,
    )
    dial = model.part("browning_dial")
    dial.visual(
        mesh_from_geometry(dial_geo, "browning_dial_cap"),
        origin=Origin(xyz=(-0.0003, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["control"],
        name="dial_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    dial.visual(
        Cylinder(radius=DIAL_SHAFT_R, length=0.022),
        origin=Origin(xyz=(-0.008, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["dark"],
        name="dial_shaft", material_class_id="metal.blackened_gunmetal",
    )
    dial.visual(
        Cylinder(radius=0.0022, length=0.004),
        origin=Origin(xyz=(DIAL_H - 0.0023, 0.0, -0.0095), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["button"],
        name="dial_pointer_nub", material_class_id="plastic.opaque_glossy_molded",
    )
    dial.inertial = Inertial.from_geometry(
        Cylinder(radius=DIAL_D / 2.0, length=DIAL_H),
        mass=0.03,
        origin=Origin(xyz=(DIAL_H / 2.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
    )
    model.articulation(
        "body_to_browning_dial",
        ArticulationType.REVOLUTE,
        parent=body,
        child=dial,
        origin=Origin(xyz=(r.panel_x1, DIAL_Y, DIAL_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=r.browning_range),
    )


def _build_slider(model, r, mats, body, *, assets):
    slider = model.part("browning_slider")
    slider.visual(
        mesh_from_cadquery(_slider_tab_shape(), "slider_tab", assets=assets),
        origin=Origin(xyz=(SLIDER_TAB_D / 2.0 - 0.0003, 0.0, 0.0)),
        material=mats["control"],
        name="slider_tab", material_class_id="plastic.opaque_glossy_molded",
    )
    slider.visual(
        Box((SLIDER_STEM_D, SLIDER_STEM_W, SLIDER_TAB_H - 0.002)),
        origin=Origin(xyz=(-SLIDER_STEM_D / 2.0 + 0.002, 0.0, 0.0)),
        material=mats["dark"],
        name="slider_stem", material_class_id="plastic.opaque_generic",
    )
    slider.visual(
        Box((0.004, 0.014, 0.016)),
        origin=Origin(xyz=(-SLIDER_STEM_D + 0.002, 0.0, 0.0)),
        material=mats["carriage"],
        name="slider_carriage_plate", material_class_id="metal.stainless_matte",
    )
    slider.inertial = Inertial.from_geometry(
        Box((SLIDER_STEM_D, SLIDER_TAB_W, SLIDER_TAB_H)),
        mass=0.02,
        origin=Origin(xyz=(-SLIDER_STEM_D / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "body_to_browning_slider",
        ArticulationType.PRISMATIC,
        parent=body,
        child=slider,
        origin=Origin(xyz=(r.panel_x1, SLIDER_Y, SLIDER_REST_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=4.0, velocity=0.2, lower=0.0, upper=r.browning_range),
    )


def _build_digital(model, r, mats, body, *, assets):
    for i, z in enumerate(_digi_btn_z()):
        btn = model.part(f"browning_button_{i}")
        btn.visual(
            mesh_from_cadquery(_rounded_pad(DIGI_BTN_W, DIGI_BTN_H, DIGI_BTN_D), f"browning_pad_{i}", assets=assets),
            origin=Origin(xyz=(-0.0003, 0.0, 0.0)),
            material=mats["button"],
            name=f"browning_pad_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        btn.visual(
            Cylinder(radius=DIGI_BTN_STEM_R, length=0.018),
            origin=Origin(xyz=(-0.009, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["dark"],
            name=f"browning_stem_{i}", material_class_id="plastic.opaque_generic",
        )
        arrow_h = 0.003 if i == 0 else -0.003
        btn.visual(
            Box((0.0006, 0.004, 0.002)),
            origin=Origin(xyz=(DIGI_BTN_D - 0.0003, 0.0, arrow_h)),
            material=mats["mark"],
            name=f"browning_indicator_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        btn.inertial = Inertial.from_geometry(
            Box((DIGI_BTN_D, DIGI_BTN_W, DIGI_BTN_H)),
            mass=0.008,
            origin=Origin(xyz=(DIGI_BTN_D / 2.0, 0.0, 0.0)),
        )
        model.articulation(
            f"body_to_browning_button_{i}",
            ArticulationType.PRISMATIC,
            parent=body,
            child=btn,
            origin=Origin(xyz=(r.panel_x1, DIGI_Y, z)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=0.1, lower=0.0, upper=DIGI_BTN_TRAVEL),
        )


_BROWNING_BUILDERS = {
    "rotary_dial": _build_rotary_dial,
    "slider": _build_slider,
    "digital": _build_digital,
}


# ===========================================================================
# Function buttons (fixed structure) + crumb tray (Slot C)
# ===========================================================================
def _build_function_buttons(model, r, mats, body, *, assets):
    for name, z in zip(("cancel_button", "frozen_button", "bagel_button"), BTN_Z):
        btn = model.part(name)
        btn.visual(
            Cylinder(radius=BTN_CAP_R, length=BTN_CAP_L),
            origin=Origin(xyz=(BTN_CAP_L / 2.0 - 0.0003, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["button"],
            name=f"{name}_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        btn.visual(
            Cylinder(radius=BTN_STEM_R, length=0.021),
            origin=Origin(xyz=(-0.0095, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["dark"],
            name=f"{name}_stem", material_class_id="plastic.opaque_generic",
        )
        btn.inertial = Inertial.from_geometry(
            Cylinder(radius=BTN_CAP_R, length=0.027),
            mass=0.006,
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        )
        model.articulation(
            f"body_to_{name}",
            ArticulationType.PRISMATIC,
            parent=body,
            child=btn,
            origin=Origin(xyz=(r.panel_x1, BTN_Y, z)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=0.1, lower=0.0, upper=BTN_TRAVEL),
        )


def _build_crumb_tray(model, r, mats, body, *, assets):
    tray = model.part("crumb_tray")
    tray_center_z = TRAY_Z_BASE + TRAY_TOTAL_H / 2.0
    tray.visual(
        mesh_from_cadquery(_crumb_tray_shape(r), "tray_body", assets=assets),
        origin=Origin(xyz=(0.0, 0.0, -(tray_center_z - TRAY_Z_BASE))),
        material=mats["tray"],
        name="tray_body", material_class_id="metal.paint_coated",
    )
    tray.inertial = Inertial.from_geometry(
        Box((_tray_len(r.body_l), TRAY_W, TRAY_TOTAL_H)),
        mass=0.10,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    model.articulation(
        "body_to_crumb_tray",
        ArticulationType.PRISMATIC,
        parent=body,
        child=tray,
        origin=Origin(xyz=(0.0, 0.0, tray_center_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.2, lower=0.0, upper=r.tray_travel),
    )


# ===========================================================================
# Build
# ===========================================================================
def build_toaster(
    config: ToasterConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"toaster_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in pal.items()
    }

    body = _build_body(model, r, mats, assets=assets)
    _build_carriage(model, r, mats, body, assets=assets)
    _BROWNING_BUILDERS[r.browning_control](model, r, mats, body, assets=assets)
    _build_function_buttons(model, r, mats, body, assets=assets)
    if r.crumb_tray == "pullout":
        _build_crumb_tray(model, r, mats, body, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_toaster(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_toaster(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_toaster_tests(
    object_model: ArticulatedObject,
    config: ToasterConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("body")
    carriage = object_model.get_part("carriage_lever")
    lever_joint = object_model.get_articulation("body_to_carriage_lever")

    # ---- intentional seated/flush embeddings (all tiny) ----
    seat_face = "lever_guide_plate" if r.lever_placement == "side_lever" else "control_panel"
    ctx.allow_overlap(
        carriage,
        body,
        elem_a="lever_knob",
        elem_b=seat_face,
        reason="The carriage lever knob intentionally rides flush on its mount face (seat).",
    )

    # ---- overall identity: grounded + recognizable toaster proportions ----
    aabb = ctx.part_world_aabb(body)
    ctx.check(
        "body is grounded near z=0",
        aabb is not None and abs(aabb[0][2]) < 0.004,
        details=f"body aabb={aabb}",
    )
    if aabb is not None:
        dz = aabb[1][2] - aabb[0][2]
        dy = aabb[1][1] - aabb[0][1]
        ctx.check(
            "toaster has plausible body proportions (~0.16 W, ~0.19 H)",
            0.13 < dy < 0.20 and 0.16 < dz < 0.23,
            details=f"dy={dy:.4f}, dz={dz:.4f}",
        )

    # ---- rim plate recessed below the shell top ----
    rim = ctx.part_element_world_aabb(body, elem="slot_rim_plate")
    ctx.check(
        "lighter-gray rim plate sits recessed just below the shell top",
        rim is not None and rim[1][2] < r.shell_top - 0.0001,
        details=f"rim aabb={rim}",
    )

    # ---- control panel on the +X front face ----
    panel = ctx.part_element_world_aabb(body, elem="control_panel")
    ctx.check(
        "brushed-silver control panel is on the +X front face",
        panel is not None and panel[1][0] > r.shell_face_x - 0.001,
        details=f"panel aabb={panel}",
    )

    # ---- N bread shelves under the slots (visual / cut multiplicity) ----
    shelf_names = [v.name for v in carriage.visuals if v.name.startswith("bread_shelf_")]
    ctx.check(
        f"carriage carries {r.slot_count} bread shelves (one per slot)",
        len(shelf_names) == r.slot_count,
        details=f"shelves={sorted(shelf_names)}",
    )
    for i, (xc, yc) in enumerate(r.slot_positions):
        shelf = ctx.part_element_world_aabb(carriage, elem=f"bread_shelf_{i}")
        ctx.check(
            f"bread shelf {i} sits under its slot inside the cavity at rest",
            shelf is not None
            and abs((shelf[0][1] + shelf[1][1]) / 2.0 - yc) < 0.004
            and shelf[0][2] > r.cav_z0
            and shelf[1][2] < r.cav_z1 + 0.001,
            details=f"shelf {i} aabb={shelf}, slot=({xc:.3f},{yc:.3f})",
        )

    # ---- defining motion: single carriage PRISMATIC, downward, N-independent ----
    rest_pos = ctx.part_world_position(carriage)
    with ctx.pose({lever_joint: r.lever_travel}):
        pressed_pos = ctx.part_world_position(carriage)
        shelf_dn = ctx.part_element_world_aabb(carriage, elem="bread_shelf_0")
        ctx.check(
            "pressed carriage stays above the cavity floor",
            shelf_dn is not None and shelf_dn[0][2] > r.cav_z0 + 0.003,
            details=f"pressed shelf aabb={shelf_dn}",
        )
    ctx.check(
        "carriage lever travels straight DOWN (defining motion)",
        rest_pos is not None
        and pressed_pos is not None
        and abs((rest_pos[2] - pressed_pos[2]) - r.lever_travel) < 1e-6
        and abs(rest_pos[0] - pressed_pos[0]) < 1e-9
        and abs(rest_pos[1] - pressed_pos[1]) < 1e-9,
        details=f"rest={rest_pos}, pressed={pressed_pos}",
    )
    ctx.check(
        "carriage joint is a single PRISMATIC with downward travel",
        lever_joint.articulation_type == ArticulationType.PRISMATIC
        and lever_joint.axis[2] < -0.99
        and abs(lever_joint.motion_limits.upper - r.lever_travel) < 1e-6,
        details=f"axis={lever_joint.axis}, upper={lever_joint.motion_limits.upper}",
    )

    # ---- lever placement face check ----
    knob = ctx.part_element_world_aabb(carriage, elem="lever_knob")
    if r.lever_placement == "side_lever":
        ctx.check(
            "side lever knob protrudes from the +Y side wall",
            knob is not None and knob[1][1] > r.body_w / 2.0 - 0.002,
            details=f"knob aabb={knob}, side_y={r.body_w / 2.0:.3f}",
        )
        guide = ctx.part_element_world_aabb(body, elem="lever_guide_plate")
        ctx.check(
            "side lever guide plate present on the side wall",
            guide is not None and guide[1][1] > r.body_w / 2.0 - 0.001,
            details=f"guide aabb={guide}",
        )
        ctx.expect_contact(
            carriage, body, elem_a="lever_knob", elem_b="lever_guide_plate",
            name="side lever knob rides on the guide plate",
        )
    else:
        ctx.check(
            "front lever knob protrudes from the +X front face",
            knob is not None and knob[1][0] > r.shell_face_x - 0.001,
            details=f"knob aabb={knob}, front_x={r.shell_face_x:.3f}",
        )
        ctx.expect_contact(
            carriage, body, elem_a="lever_knob", elem_b="control_panel",
            name="front lever knob rides on the control panel",
        )

    # ---- browning control (Slot A) ----
    if r.browning_control == "rotary_dial":
        dial = object_model.get_part("browning_dial")
        dial_joint = object_model.get_articulation("body_to_browning_dial")
        ctx.allow_overlap(
            dial, body, elem_a="dial_cap", elem_b="control_panel",
            reason="The dial cap mounting face seats flush against the panel.",
        )
        ctx.check(
            "browning dial rotates about the horizontal +X panel normal",
            dial_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(dial_joint.axis[0]) > 0.99
            and dial_joint.motion_limits.upper > math.radians(150.0),
            details=f"axis={dial_joint.axis}, upper={dial_joint.motion_limits.upper}",
        )
        nub0 = ctx.part_element_world_aabb(dial, elem="dial_pointer_nub")
        with ctx.pose({dial_joint: min(math.pi, dial_joint.motion_limits.upper)}):
            nub1 = ctx.part_element_world_aabb(dial, elem="dial_pointer_nub")
        ctx.check(
            "off-axis pointer nub sweeps with dial rotation",
            nub0 is not None
            and nub1 is not None
            and abs(((nub1[0][2] + nub1[1][2]) - (nub0[0][2] + nub0[1][2])) / 2.0) > 0.010,
            details=f"nub rest={nub0}, rotated={nub1}",
        )
        ctx.expect_contact(
            dial, body, elem_a="dial_cap", elem_b="control_panel",
            name="dial cap seats on the control panel",
        )
    elif r.browning_control == "slider":
        slider = object_model.get_part("browning_slider")
        slider_joint = object_model.get_articulation("body_to_browning_slider")
        ctx.allow_overlap(
            slider, body, elem_a="slider_tab", elem_b="control_panel",
            reason="The slider tab seats flush against the panel face.",
        )
        ctx.check(
            "browning slider slides vertically (+Z) on the panel",
            slider_joint.articulation_type == ArticulationType.PRISMATIC
            and abs(slider_joint.axis[2]) > 0.99
            and slider_joint.motion_limits.upper > 0.020,
            details=f"axis={slider_joint.axis}, upper={slider_joint.motion_limits.upper}",
        )
        s0 = ctx.part_world_position(slider)
        with ctx.pose({slider_joint: slider_joint.motion_limits.upper}):
            s1 = ctx.part_world_position(slider)
        ctx.check(
            "raising the slider moves the tab up in +Z",
            s0 is not None and s1 is not None and (s1[2] - s0[2]) > 0.015,
            details=f"rest={s0}, raised={s1}",
        )
    else:  # digital
        digi = [object_model.get_part(f"browning_button_{i}") for i in range(2)]
        for i, b in enumerate(digi):
            ctx.allow_overlap(
                b, body, elem_a=f"browning_pad_{i}", elem_b="control_panel",
                reason="The digital pad rim seats flush against the panel face.",
            )
            joint = object_model.get_articulation(f"body_to_browning_button_{i}")
            ctx.check(
                f"digital button {i} presses inward along -X",
                joint.articulation_type == ArticulationType.PRISMATIC
                and joint.axis[0] < -0.99
                and abs(joint.motion_limits.upper - DIGI_BTN_TRAVEL) < 1e-9,
                details=f"axis={joint.axis}, upper={joint.motion_limits.upper}",
            )
        up = ctx.part_world_position(digi[0])
        dn = ctx.part_world_position(digi[1])
        ctx.check(
            "digital UP pad sits above DOWN pad",
            up is not None and dn is not None and (up[2] - dn[2]) > 0.010,
            details=f"up={up}, down={dn}",
        )

    # ---- three function buttons ----
    buttons = [
        object_model.get_part(n) for n in ("cancel_button", "frozen_button", "bagel_button")
    ]
    for btn in buttons:
        ctx.allow_overlap(
            btn, body, elem_a=f"{btn.name}_cap", elem_b="control_panel",
            reason="The function button cap rim seats flush against the panel face.",
        )
        joint = object_model.get_articulation(f"body_to_{btn.name}")
        ctx.check(
            f"{btn.name} is a 3 mm prismatic press into the panel",
            joint.articulation_type == ArticulationType.PRISMATIC
            and abs(joint.motion_limits.upper - BTN_TRAVEL) < 1e-9
            and joint.axis[0] < 0.0,
            details=f"axis={joint.axis}, upper={joint.motion_limits.upper}",
        )

    # ---- crumb tray (Slot C) ----
    if r.crumb_tray == "pullout":
        tray = object_model.get_part("crumb_tray")
        tray_joint = object_model.get_articulation("body_to_crumb_tray")
        ctx.allow_overlap(
            tray, body, elem_a="tray_body", elem_b="shell",
            reason="The crumb tray slides inside the body floor pocket as a prismatic fit.",
        )
        ctx.check(
            "crumb tray pulls out along +X",
            tray_joint.articulation_type == ArticulationType.PRISMATIC
            and tray_joint.axis[0] > 0.99
            and tray_joint.motion_limits.upper > 0.10,
            details=f"axis={tray_joint.axis}, upper={tray_joint.motion_limits.upper}",
        )
        tray_aabb = ctx.part_world_aabb(tray)
        ctx.check(
            "crumb tray sits near the base of the toaster",
            tray_aabb is not None and tray_aabb[1][2] < 0.045,
            details=f"tray aabb={tray_aabb}",
        )
        pocket_x0, pocket_x1 = _tray_pocket_x_bounds(r)
        ctx.check(
            "crumb tray bottom pocket is cut through to the exterior faces",
            pocket_x0 < -r.shell_face_x - 0.004 and pocket_x1 > r.shell_face_x + 0.004,
            details=(
                f"pocket_x=({pocket_x0:.4f}, {pocket_x1:.4f}), "
                f"shell_face_x={r.shell_face_x:.4f}"
            ),
        )
        rest_tray = ctx.part_world_position(tray)
        with ctx.pose({tray_joint: tray_joint.motion_limits.upper}):
            ext_tray = ctx.part_world_position(tray)
            ctx.expect_overlap(
                tray, body, axes="x", elem_a="tray_body", elem_b="shell",
                min_overlap=0.030,
                name="crumb tray retains insertion in body when extended",
            )
        ctx.check(
            "crumb tray actually moves out in +X",
            rest_tray is not None and ext_tray is not None and (ext_tray[0] - rest_tray[0]) > 0.10,
            details=f"rest={rest_tray}, extended={ext_tray}",
        )

    return ctx.report()
