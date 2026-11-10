# SPDX-License-Identifier: Apache-2.0

"""Sliding measuring caliper modular template (analog dial / digital / vernier).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Handtools_Handtools_dial_caliper.md`` and the
``picture/Handtools/dial caliper`` 5-star sample pool (1 parent + 8 single-axis
fork variants).

Structure (pattern = ``parallel_children``): a flat graduated ``beam`` (root,
long axis +X) carries a fixed jaw head and a sliding ``slider`` carriage. The
defining mechanism is ``beam_to_slider`` PRISMATIC along +X — every candidate
has it (positive q opens the jaw gap and pushes the depth rod out the tail).
Four slots hang off this beam/slider skeleton:

  * ``readout`` (3): analog_dial (round chrome bezel + white face + 50-tick
    dial + a separate ``needle`` part on a CONTINUOUS +Z mimic joint) /
    digital_lcd (flat LCD housing + screen + segment bars + 2 button pads, no
    needle) / vernier_scale (beam main-scale ticks + slider vernier window, no
    needle). This is the part/joint-topology axis: ``has_needle =
    (readout == analog_dial)``.
  * ``jaw_config`` (4): dual_inside_outside / depth_flat (short flat
    registration foot) / internal_only (no lower blade) / step_jaw (compound
    step shoulder). A mesh-profile axis — re-skins the fixed_jaw + slider jaw
    polylines, part tree unchanged.
  * ``accessory`` (3): rod_and_roller (depth_rod + 18-flute thumb_roller) /
    lock_screw (lock_screw_boss + a separate ``lock_screw`` part on a REVOLUTE
    +Z joint, keeps depth_rod) / simplified_no_rod (thumb_lip, no depth_rod).
    ``has_depth_rod = (accessory in {rod_and_roller, lock_screw})``.
  * ``beam_profile`` (2): flat_bar (rounded box beam + rectangular saddle) /
    channel_beam (I-section beam + rail groove + I-cavity saddle + gib). A
    mesh-profile axis, joint topology unchanged.

Rule 1 ("不动就不是 part") is upheld: dial ticks, graduations, knurl flutes,
LCD segments and the depth rod are all slider/beam ``part.visual(...)`` loops,
never FIXED-joint decoration parts. The only separate parts are ``needle``
(CONTINUOUS) and ``lock_screw`` (REVOLUTE) — both genuinely articulate.
Rule 2 / grandfathering: the saddle-wraps-beam, rod-in-channel and
screw-in-boss fits are captured overlaps that cannot be modeled as two
axis-aligned faces in contact, so their joints omit ``MatingContract`` and rely
on the flat 0.015 m articulation-origin baseline + element-scoped
``allow_overlap`` (mirroring every source sample's run_tests).
Rule 3: all geometry is adapted from the declared 5-star CadQuery sources;
``mesh_from_cadquery`` primitives are preserved, never downgraded to Box.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
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

Readout = Literal["analog_dial", "digital_lcd", "vernier_scale"]
JawConfig = Literal["dual_inside_outside", "depth_flat", "internal_only", "step_jaw"]
Accessory = Literal["rod_and_roller", "lock_screw", "simplified_no_rod"]
BeamProfile = Literal["flat_bar", "channel_beam"]
PaletteStyle = Literal[
    "satin_stainless",
    "polished_chrome",
    "white_dial",
    "black_dial",
    "digital_grey",
    "vernier_steel",
]

READOUTS: tuple[Readout, ...] = ("analog_dial", "digital_lcd", "vernier_scale")
JAW_CONFIGS: tuple[JawConfig, ...] = (
    "dual_inside_outside",
    "depth_flat",
    "internal_only",
    "step_jaw",
)
ACCESSORIES: tuple[Accessory, ...] = ("rod_and_roller", "lock_screw", "simplified_no_rod")
BEAM_PROFILES: tuple[BeamProfile, ...] = ("flat_bar", "channel_beam")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "satin_stainless",
    "polished_chrome",
    "white_dial",
    "black_dial",
    "digital_grey",
    "vernier_steel",
)

# Accessories with a depth rod (has_depth_rod gate, spec §7).
ROD_ACCESSORIES: tuple[Accessory, ...] = ("rod_and_roller", "lock_screw")
# jaw_config values where the lower outside blade can be scaled (jaw_drop_scale
# is conditional; depth_flat uses a fixed short foot, internal_only has no
# lower jaw — spec §7).
JAW_DROP_CONFIGS: tuple[JawConfig, ...] = ("dual_inside_outside", "step_jaw")

# ---------------------------------------------------------------------------
# Palette presets (6 realistic colorways, spec §7). Every keyed colour drives a
# .visual(material=...) below; per-seed diversity comes from rng.choice here.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "satin_stainless": {
        "steel": (0.74, 0.76, 0.79, 1.0),
        "steel_dark": (0.55, 0.57, 0.60, 1.0),
        "chrome": (0.82, 0.84, 0.87, 1.0),
        "dial_white": (0.93, 0.93, 0.90, 1.0),
        "needle_black": (0.10, 0.10, 0.11, 1.0),
        "scale_dark": (0.30, 0.31, 0.33, 1.0),
        "lcd_bg": (0.18, 0.22, 0.20, 1.0),
        "lcd_seg": (0.72, 0.78, 0.65, 1.0),
        "button_dark": (0.15, 0.15, 0.17, 1.0),
        "housing_dark": (0.22, 0.23, 0.25, 1.0),
        "vernier_plate": (0.88, 0.88, 0.85, 1.0),
    },
    "polished_chrome": {
        "steel": (0.82, 0.84, 0.87, 1.0),
        "steel_dark": (0.68, 0.70, 0.74, 1.0),
        "chrome": (0.90, 0.92, 0.95, 1.0),
        "dial_white": (0.95, 0.95, 0.93, 1.0),
        "needle_black": (0.09, 0.09, 0.10, 1.0),
        "scale_dark": (0.28, 0.29, 0.31, 1.0),
        "lcd_bg": (0.20, 0.24, 0.22, 1.0),
        "lcd_seg": (0.74, 0.80, 0.67, 1.0),
        "button_dark": (0.16, 0.16, 0.18, 1.0),
        "housing_dark": (0.30, 0.31, 0.33, 1.0),
        "vernier_plate": (0.90, 0.90, 0.88, 1.0),
    },
    "white_dial": {
        "steel": (0.76, 0.78, 0.80, 1.0),
        "steel_dark": (0.52, 0.54, 0.57, 1.0),
        "chrome": (0.84, 0.86, 0.89, 1.0),
        "dial_white": (0.96, 0.96, 0.94, 1.0),
        "needle_black": (0.06, 0.06, 0.07, 1.0),
        "scale_dark": (0.10, 0.10, 0.12, 1.0),
        "lcd_bg": (0.18, 0.22, 0.20, 1.0),
        "lcd_seg": (0.72, 0.78, 0.65, 1.0),
        "button_dark": (0.14, 0.14, 0.16, 1.0),
        "housing_dark": (0.22, 0.23, 0.25, 1.0),
        "vernier_plate": (0.90, 0.90, 0.87, 1.0),
    },
    "black_dial": {
        "steel": (0.72, 0.74, 0.77, 1.0),
        "steel_dark": (0.48, 0.50, 0.53, 1.0),
        "chrome": (0.80, 0.82, 0.85, 1.0),
        "dial_white": (0.12, 0.12, 0.14, 1.0),  # black dial face
        "needle_black": (0.93, 0.93, 0.90, 1.0),  # white needle on black face
        "scale_dark": (0.85, 0.85, 0.82, 1.0),  # white ticks reversed
        "lcd_bg": (0.16, 0.20, 0.18, 1.0),
        "lcd_seg": (0.70, 0.76, 0.63, 1.0),
        "button_dark": (0.12, 0.12, 0.14, 1.0),
        "housing_dark": (0.18, 0.19, 0.21, 1.0),
        "vernier_plate": (0.86, 0.86, 0.83, 1.0),
    },
    "digital_grey": {
        "steel": (0.70, 0.72, 0.75, 1.0),
        "steel_dark": (0.40, 0.42, 0.45, 1.0),
        "chrome": (0.78, 0.80, 0.83, 1.0),
        "dial_white": (0.92, 0.92, 0.89, 1.0),
        "needle_black": (0.10, 0.10, 0.11, 1.0),
        "scale_dark": (0.26, 0.27, 0.29, 1.0),
        "lcd_bg": (0.14, 0.18, 0.16, 1.0),
        "lcd_seg": (0.78, 0.84, 0.70, 1.0),
        "button_dark": (0.10, 0.10, 0.12, 1.0),
        "housing_dark": (0.18, 0.19, 0.21, 1.0),
        "vernier_plate": (0.86, 0.86, 0.83, 1.0),
    },
    "vernier_steel": {
        "steel": (0.70, 0.72, 0.75, 1.0),
        "steel_dark": (0.50, 0.52, 0.55, 1.0),
        "chrome": (0.80, 0.82, 0.85, 1.0),
        "dial_white": (0.93, 0.93, 0.90, 1.0),
        "needle_black": (0.10, 0.10, 0.11, 1.0),
        "scale_dark": (0.16, 0.16, 0.18, 1.0),
        "lcd_bg": (0.18, 0.22, 0.20, 1.0),
        "lcd_seg": (0.72, 0.78, 0.65, 1.0),
        "button_dark": (0.15, 0.15, 0.17, 1.0),
        "housing_dark": (0.22, 0.23, 0.25, 1.0),
        "vernier_plate": (0.90, 0.90, 0.86, 1.0),
    },
}

# Per-readout weak palette preference (any palette × any readout is legal;
# spec §7). Order matches PALETTE_STYLES.
_PALETTE_WEIGHTS: dict[Readout, tuple[int, ...]] = {
    #                  satin chrome white black dgrey vsteel
    "analog_dial": (5, 3, 4, 4, 1, 2),
    "digital_lcd": (3, 3, 1, 1, 6, 1),
    "vernier_scale": (3, 3, 1, 1, 1, 6),
}

# ---------------------------------------------------------------------------
# Nominal real-world dimensions (meters). Adapted from parent S0 (L48-67).
# Mechanical clearances / thicknesses are never scaled; beam length / height,
# slide travel, jaw drop, dial radius, LCD size and lock-screw turn are.
# ---------------------------------------------------------------------------
_BEAM_LEN = 0.205  # full graduated beam length along X
_BEAM_H = 0.020  # beam height (Y)
_BEAM_T = 0.0045  # beam thickness (Z)

_JAW_DOWN_LEN = 0.040  # large outside-measuring jaw drop (down, -Y)
_JAW_UP_LEN = 0.022  # small inside-measuring tip rise (up, +Y)
_JAW_T = 0.0040  # jaw thickness (Z)
_DEPTH_FOOT_DROP = 0.014  # short flat registration foot drop (depthjaw S3 L54)

_SLIDE_TRAVEL = 0.150  # usable measuring travel (6")
_FIXED_JAW_X = 0.011  # X of fixed jaw centerline (near left / -X end)
_SLIDER_REST_X = 0.044  # slider carriage center X at q=0 (small rest gap)
_CARRIAGE_W = 0.034  # slider carriage width along X

_DIAL_R = 0.0220  # dial bezel outer radius
_DIAL_FACE_R = 0.0185  # white graduated face radius

_LCD_W = 0.042  # LCD module width (X)
_LCD_H = 0.026  # LCD module height (Y)
_LCD_D = 0.008  # LCD module depth (Z)
_SCREEN_W = 0.034
_SCREEN_H = 0.014

_ROD_R = 0.0016  # depth rod radius
_ROD_LEN = 0.150  # depth rod length

# I-section profile constants (channel_beam S8 L54-58).
_FLANGE_T = 0.003
_WEB_T = 0.002
_RAIL_W = 0.002
_RAIL_D = 0.0015

# step jaw constants (stepjaw S5 L61-62).
_STEP_DEPTH = 0.0045
_STEP_HEIGHT = 0.012


@dataclass(frozen=True)
class DialCaliperConfig:
    readout: Readout | None = None
    jaw_config: JawConfig | None = None
    accessory: Accessory | None = None
    beam_profile: BeamProfile | None = None
    palette_style: PaletteStyle = "satin_stainless"
    beam_len_scale: float = 1.0
    beam_height_scale: float = 1.0
    slide_travel_scale: float = 1.0
    jaw_drop_scale: float = 1.0
    dial_radius_scale: float = 1.0
    lcd_size_scale: float = 1.0
    lock_screw_turn_scale: float = 1.0
    name: str = "dial_caliper"


@dataclass(frozen=True)
class ResolvedDialCaliperConfig:
    readout: Readout
    jaw_config: JawConfig
    accessory: Accessory
    beam_profile: BeamProfile
    palette_style: PaletteStyle
    # derived flags
    has_needle: bool
    has_depth_rod: bool
    # resolved geometry
    beam_len: float
    beam_h: float
    slide_travel: float
    slider_rest_x: float
    jaw_down_len: float
    dial_r: float
    dial_face_r: float
    lcd_w: float
    lcd_h: float
    lock_screw_turn: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> DialCaliperConfig:
    """Deterministic procedural sampling (seed=0 is not special, spec §9)."""
    rng = random.Random(seed)
    readout: Readout = rng.choice(READOUTS)
    jaw_config: JawConfig = rng.choice(JAW_CONFIGS)
    accessory: Accessory = rng.choice(ACCESSORIES)
    beam_profile: BeamProfile = rng.choice(BEAM_PROFILES)
    palette_style: PaletteStyle = rng.choices(
        PALETTE_STYLES, weights=_PALETTE_WEIGHTS[readout], k=1
    )[0]
    return DialCaliperConfig(
        readout=readout,
        jaw_config=jaw_config,
        accessory=accessory,
        beam_profile=beam_profile,
        palette_style=palette_style,
        beam_len_scale=round(rng.uniform(0.85, 1.15), 4),
        beam_height_scale=round(rng.uniform(0.90, 1.12), 4),
        slide_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        jaw_drop_scale=round(rng.uniform(0.85, 1.15), 4),
        dial_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        lcd_size_scale=round(rng.uniform(0.90, 1.10), 4),
        lock_screw_turn_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_dial_caliper_{seed}",
    )


def resolve_config(config: DialCaliperConfig | None = None) -> ResolvedDialCaliperConfig:
    cfg = config or DialCaliperConfig()
    readout = _pick(cfg.readout, READOUTS)
    jaw_config = _pick(cfg.jaw_config, JAW_CONFIGS)
    accessory = _pick(cfg.accessory, ACCESSORIES)
    beam_profile = _pick(cfg.beam_profile, BEAM_PROFILES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # Derived gates (spec §7).
    has_needle = readout == "analog_dial"
    has_depth_rod = accessory in ROD_ACCESSORIES

    # Independent scales.
    beam_len = _BEAM_LEN * _clamp(cfg.beam_len_scale, 0.85, 1.15)
    beam_h = _BEAM_H * _clamp(cfg.beam_height_scale, 0.90, 1.12)

    # slide_travel derived from beam length minus the head and carriage usage,
    # then bounded so the carriage never runs off the tail or into the fixed jaw
    # head (spec §7 inequalities). Base usable run = beam_len - rest_x - margin.
    rest_x = _SLIDER_REST_X
    travel_scale = _clamp(cfg.slide_travel_scale, 0.85, 1.10)
    usable = beam_len - rest_x - _CARRIAGE_W / 2.0 - 0.006
    slide_travel = _clamp(_SLIDE_TRAVEL * travel_scale, 0.080, usable)

    # Conditional jaw drop (only dual / step jaws have a scalable lower blade).
    if jaw_config in JAW_DROP_CONFIGS:
        jaw_down_len = _JAW_DOWN_LEN * _clamp(cfg.jaw_drop_scale, 0.85, 1.15)
    elif jaw_config == "depth_flat":
        jaw_down_len = _DEPTH_FOOT_DROP
    else:  # internal_only — no lower jaw
        jaw_down_len = 0.0

    # Conditional dial radius (analog only). Clamp so the bezel <= boss pad and
    # fits over the carriage top (footprint <= carriage_w + margin, spec §7).
    if readout == "analog_dial":
        dial_r = _DIAL_R * _clamp(cfg.dial_radius_scale, 0.90, 1.10)
        dial_r = min(dial_r, (_CARRIAGE_W + 0.012) / 2.0)
        dial_face_r = dial_r * (_DIAL_FACE_R / _DIAL_R)
    else:
        dial_r = _DIAL_R
        dial_face_r = _DIAL_FACE_R

    # Conditional LCD size (digital only). Clamp so screen < housing.
    if readout == "digital_lcd":
        s = _clamp(cfg.lcd_size_scale, 0.90, 1.10)
        lcd_w = _LCD_W * s
        lcd_h = _LCD_H * s
    else:
        lcd_w = _LCD_W
        lcd_h = _LCD_H

    # Conditional lock-screw turn upper (lock_screw only). Clamp <= 2*pi*1.1.
    if accessory == "lock_screw":
        lock_screw_turn = min(6.28 * _clamp(cfg.lock_screw_turn_scale, 0.85, 1.10), 6.28 * 1.1)
    else:
        lock_screw_turn = 6.28

    return ResolvedDialCaliperConfig(
        readout=readout,
        jaw_config=jaw_config,
        accessory=accessory,
        beam_profile=beam_profile,
        palette_style=palette_style,
        has_needle=has_needle,
        has_depth_rod=has_depth_rod,
        beam_len=beam_len,
        beam_h=beam_h,
        slide_travel=slide_travel,
        slider_rest_x=rest_x,
        jaw_down_len=jaw_down_len,
        dial_r=dial_r,
        dial_face_r=dial_face_r,
        lcd_w=lcd_w,
        lcd_h=lcd_h,
        lock_screw_turn=lock_screw_turn,
        name=cfg.name or "dial_caliper",
    )


def slot_choices_for_config(
    config: DialCaliperConfig | ResolvedDialCaliperConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedDialCaliperConfig) else resolve_config(config)
    return (
        ("readout", r.readout),
        ("jaw_config", r.jaw_config),
        ("accessory", r.accessory),
        ("beam_profile", r.beam_profile),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# CadQuery geometry builders — adapted from the declared 5-star sources with
# literal constants promoted to ResolvedConfig. Primitive type (CadQuery solids
# via mesh_from_cadquery) is preserved per Rule 3.
# ---------------------------------------------------------------------------
def _beam_body_flat(r: ResolvedDialCaliperConfig) -> cq.Workplane:
    """Flat graduated beam (parent S0 L81-89)."""
    return (
        cq.Workplane("XY")
        .box(r.beam_len, r.beam_h, _BEAM_T, centered=(False, True, True))
        .edges("|Z")
        .fillet(0.0015)
    )


def _beam_body_channel(r: ResolvedDialCaliperConfig) -> cq.Workplane:
    """Reinforced I-section beam with a bottom guide-rail groove
    (channel_beam S8 L89-126)."""
    half_h = r.beam_h / 2.0
    top_flange = (
        cq.Workplane("XY")
        .box(r.beam_len, _FLANGE_T, _BEAM_T, centered=(False, True, True))
        .translate((0.0, half_h - _FLANGE_T / 2.0, 0.0))
    )
    bot_flange = (
        cq.Workplane("XY")
        .box(r.beam_len, _FLANGE_T, _BEAM_T, centered=(False, True, True))
        .translate((0.0, -half_h + _FLANGE_T / 2.0, 0.0))
    )
    web_h = r.beam_h - 2.0 * _FLANGE_T
    web = cq.Workplane("XY").box(r.beam_len, web_h, _WEB_T, centered=(False, True, True))
    body = top_flange.union(bot_flange).union(web)
    rail_cut = (
        cq.Workplane("XY")
        .box(r.beam_len, _RAIL_D, _RAIL_W, centered=(False, True, True))
        .translate((0.0, -half_h + _RAIL_D / 2.0, 0.0))
    )
    return body.cut(rail_cut)


def _beam_body(r: ResolvedDialCaliperConfig) -> cq.Workplane:
    if r.beam_profile == "channel_beam":
        return _beam_body_channel(r)
    return _beam_body_flat(r)


def _jaw_lower_pts_fixed(r: ResolvedDialCaliperConfig, mface: float) -> list[tuple[float, float]] | None:
    """Lower (outside / foot / step) jaw polyline for the FIXED head, in the
    beam frame. Returns None for internal_only (no lower jaw)."""
    bh = r.beam_h
    drop = r.jaw_down_len
    if r.jaw_config == "internal_only":
        return None
    if r.jaw_config == "depth_flat":
        foot_w = 0.014
        return [
            (mface, -bh / 2.0),
            (mface, -bh / 2.0 - drop),
            (mface - foot_w, -bh / 2.0 - drop),
            (mface - foot_w, -bh / 2.0),
        ]
    if r.jaw_config == "step_jaw":
        return [
            (mface - _STEP_DEPTH, -bh / 2.0),
            (mface - _STEP_DEPTH, -bh / 2.0 - _STEP_HEIGHT),
            (mface, -bh / 2.0 - _STEP_HEIGHT),
            (mface, -bh / 2.0 - drop),
            (mface - 0.010, -bh / 2.0 - drop),
            (mface - 0.013, -bh / 2.0 - drop * 0.45),
            (mface - 0.013, -bh / 2.0),
        ]
    # dual_inside_outside (parent S0 L109-115)
    return [
        (mface, -bh / 2.0),
        (mface, -bh / 2.0 - drop),
        (mface - 0.010, -bh / 2.0 - drop),
        (mface - 0.013, -bh / 2.0 - drop * 0.45),
        (mface - 0.013, -bh / 2.0),
    ]


def _jaw_lower_pts_slider(r: ResolvedDialCaliperConfig, xj: float) -> list[tuple[float, float]] | None:
    """Mirror lower jaw polyline for the SLIDER carriage (measuring face on -X)."""
    bh = r.beam_h
    drop = r.jaw_down_len
    if r.jaw_config == "internal_only":
        return None
    if r.jaw_config == "depth_flat":
        foot_w = 0.014
        return [
            (xj, -bh / 2.0 + 0.001),
            (xj, -bh / 2.0 - drop),
            (xj + foot_w, -bh / 2.0 - drop),
            (xj + foot_w, -bh / 2.0 + 0.001),
        ]
    if r.jaw_config == "step_jaw":
        return [
            (xj + _STEP_DEPTH, -bh / 2.0 + 0.001),
            (xj + _STEP_DEPTH, -bh / 2.0 - _STEP_HEIGHT),
            (xj, -bh / 2.0 - _STEP_HEIGHT),
            (xj, -bh / 2.0 - drop),
            (xj + 0.010, -bh / 2.0 - drop),
            (xj + 0.013, -bh / 2.0 - drop * 0.45),
            (xj + 0.013, -bh / 2.0 + 0.001),
        ]
    return [
        (xj, -bh / 2.0 + 0.001),
        (xj, -bh / 2.0 - drop),
        (xj + 0.010, -bh / 2.0 - drop),
        (xj + 0.013, -bh / 2.0 - drop * 0.45),
        (xj + 0.013, -bh / 2.0 + 0.001),
    ]


def _extrude_thick(pts: list[tuple[float, float]], thick: float) -> cq.Workplane:
    return cq.Workplane("XY").polyline(pts).close().extrude(thick, both=True)


def _fixed_jaw(r: ResolvedDialCaliperConfig) -> cq.Workplane:
    """Fixed head jaws (jaw_config re-skins the polylines; parent S0 / S3 / S4 / S5)."""
    bh = r.beam_h
    x = _FIXED_JAW_X
    mface = x + 0.007
    upper_pts = [
        (mface - 0.011, bh / 2.0),
        (mface, bh / 2.0),
        (mface - 0.002, bh / 2.0 + _JAW_UP_LEN),
        (mface - 0.006, bh / 2.0 + _JAW_UP_LEN),
    ]
    upper = _extrude_thick(upper_pts, _JAW_T * 0.75)

    if r.jaw_config == "internal_only":
        # Slim root plate at the beam top — no lower blade (S4 L108-112).
        root = (
            cq.Workplane("XY")
            .box(0.014, bh * 0.55, _JAW_T, centered=(True, True, True))
            .translate((x, bh * 0.225, 0.0))
        )
        return root.union(upper)

    lower_root = (
        cq.Workplane("XY")
        .box(0.014, bh, _JAW_T, centered=(True, True, True))
        .translate((x, 0.0, 0.0))
    )
    lower_pts = _jaw_lower_pts_fixed(r, mface)
    assert lower_pts is not None
    blade_thick = _JAW_T * (1.2 if r.jaw_config == "depth_flat" else 1.0)
    lower_blade = _extrude_thick(lower_pts, blade_thick)
    return lower_root.union(lower_blade).union(upper)


def _slider_body(r: ResolvedDialCaliperConfig) -> cq.Workplane:
    """Sliding carriage: saddle (flat or I-cavity+gib) + mirrored jaws + a
    readout mounting boss/platform/plate. Authored centered at X=0."""
    bh = r.beam_h
    carriage_w = _CARRIAGE_W

    if r.beam_profile == "channel_beam":
        # I-cavity saddle + gib (channel_beam S8 L182-224).
        wall_t = 0.0025
        clr = 0.0005
        outer_h = bh + 2.0 * wall_t
        outer_d = _BEAM_T + 2.0 * wall_t
        saddle = (
            cq.Workplane("XY")
            .box(carriage_w, outer_h, outer_d, centered=(True, True, True))
            .edges("|Z")
            .fillet(0.0018)
        )
        top_cav = (
            cq.Workplane("XY")
            .box(carriage_w + 0.002, _FLANGE_T + clr, _BEAM_T + clr, centered=(True, True, True))
            .translate((0.0, bh / 2.0 - _FLANGE_T / 2.0, 0.0))
        )
        bot_cav = (
            cq.Workplane("XY")
            .box(carriage_w + 0.002, _FLANGE_T + clr, _BEAM_T + clr, centered=(True, True, True))
            .translate((0.0, -bh / 2.0 + _FLANGE_T / 2.0, 0.0))
        )
        web_cav = cq.Workplane("XY").box(
            carriage_w + 0.002, bh - 2.0 * _FLANGE_T + clr, _WEB_T + clr, centered=(True, True, True)
        )
        saddle = saddle.cut(top_cav).cut(bot_cav).cut(web_cav)
        gib_h = _RAIL_D - clr
        gib_w = _RAIL_W - clr
        gib_y = -bh / 2.0 - clr / 2.0 + gib_h / 2.0
        gib = (
            cq.Workplane("XY")
            .box(carriage_w - 0.006, gib_h, gib_w, centered=(True, True, True))
            .translate((0.0, gib_y, 0.0))
        )
        saddle = saddle.union(gib)
        neck_h = 0.016
        neck_y = bh / 2.0 + 0.001
    else:
        # Flat rectangular saddle (parent S0 L148-153).
        saddle = (
            cq.Workplane("XY")
            .box(carriage_w, bh + 0.006, _BEAM_T + 0.0050, centered=(True, True, True))
            .edges("|Z")
            .fillet(0.0018)
        )
        neck_h = 0.012
        neck_y = bh / 2.0 - 0.002

    body = saddle
    xj = -carriage_w / 2.0
    # Mirrored lower jaw (skip for internal_only).
    lower_pts = _jaw_lower_pts_slider(r, xj)
    if lower_pts is not None:
        blade_thick = _JAW_T * (1.2 if r.jaw_config == "depth_flat" else 1.0)
        body = body.union(_extrude_thick(lower_pts, blade_thick))
    # Upper inside-measuring tip.
    upper_pts = [
        (xj, bh / 2.0),
        (xj + 0.011, bh / 2.0),
        (xj + 0.006, bh / 2.0 + _JAW_UP_LEN),
        (xj + 0.002, bh / 2.0 + _JAW_UP_LEN),
    ]
    body = body.union(_extrude_thick(upper_pts, _JAW_T * 0.75))

    # Readout mounting structure on the +Z face, with a neck tying it to the
    # saddle top (so the gauge reads as truly mounted, not floating).
    if r.readout == "analog_dial":
        boss = (
            cq.Workplane("XY")
            .workplane(offset=_BEAM_T / 2.0 - 0.0010)
            .circle(r.dial_r)
            .extrude(0.0070)
            .translate((0.004, bh / 2.0 + 0.004, 0.0))
        )
        neck = (
            cq.Workplane("XY")
            .box(0.024, neck_h, _BEAM_T + 0.006, centered=(True, True, True))
            .translate((0.004, neck_y, 0.0))
        )
        body = body.union(neck).union(boss)
    elif r.readout == "digital_lcd":
        platform = (
            cq.Workplane("XY")
            .workplane(offset=_BEAM_T / 2.0 - 0.0010)
            .rect(r.lcd_w * 0.85, r.lcd_h * 0.80)
            .extrude(0.0050)
            .translate((0.004, bh / 2.0 + r.lcd_h / 2.0 - 0.002, 0.0))
        )
        neck = (
            cq.Workplane("XY")
            .box(0.026, max(neck_h, 0.014), _BEAM_T + 0.006, centered=(True, True, True))
            .translate((0.004, bh / 2.0 - 0.002, 0.0))
        )
        body = body.union(neck).union(platform)
    else:  # vernier_scale — plate + engraved vernier ticks fused into the body
        plate_height = 0.010
        plate = (
            cq.Workplane("XY")
            .workplane(offset=_BEAM_T / 2.0 + 0.0010)
            .box(0.028, plate_height, 0.0018, centered=(True, True, True))
            .translate((0.002, bh / 2.0 - plate_height / 2.0 + 0.001, 0.0))
        )
        neck = (
            cq.Workplane("XY")
            .box(0.022, max(neck_h, 0.008), _BEAM_T + 0.006, centered=(True, True, True))
            .translate((0.002, bh / 2.0 - 0.002, 0.0))
        )
        body = body.union(neck).union(plate)
        # Vernier ticks fused (vernier S2 L269-285).
        vernier_n = 10
        vernier_spacing = 0.0018
        beam_top_z = _BEAM_T / 2.0
        tick_z = beam_top_z + 0.0020
        total_span = (vernier_n - 1) * vernier_spacing
        x_start = 0.002 - total_span / 2.0
        for i in range(vernier_n):
            x_pos = x_start + i * vernier_spacing
            endpoint = (i == 0) or (i == vernier_n - 1)
            tick_len = 0.0040 if endpoint else 0.0028
            tick_w = 0.00035 if endpoint else 0.00025
            tick = (
                cq.Workplane("XY")
                .box(tick_w, tick_len, 0.0008, centered=(True, True, True))
                .translate((x_pos, bh / 2.0 - tick_len / 2.0 + 0.001, tick_z))
            )
            body = body.union(tick)
    return body


def _dial_bezel(r: ResolvedDialCaliperConfig) -> cq.Workplane:
    """Round chrome bezel: back plate + raised hollow ring (parent S0 L205-221)."""
    back_plate = cq.Workplane("XY").circle(r.dial_r).extrude(0.0012)
    ring = (
        cq.Workplane("XY")
        .circle(r.dial_r)
        .circle(r.dial_r - 0.0030)
        .extrude(0.0072)
        .translate((0.0, 0.0, 0.0010))
    )
    return back_plate.union(ring)


def _dial_face(r: ResolvedDialCaliperConfig) -> cq.Workplane:
    return cq.Workplane("XY").circle(r.dial_face_r).extrude(0.0014).translate((0.0, 0.0, 0.0006))


def _dial_ticks(r: ResolvedDialCaliperConfig) -> cq.Workplane:
    """50 radial graduation ticks, every 5th major (parent S0 L236-253)."""
    ticks = None
    n = 50
    for i in range(n):
        a = 2.0 * math.pi * i / n
        major = (i % 5) == 0
        r_out = r.dial_face_r - 0.0010
        r_in = r_out - (0.0030 if major else 0.0018)
        w = 0.00045 if major else 0.00025
        seg = (
            cq.Workplane("XY")
            .box(r_out - r_in, w, 0.0008, centered=(False, True, True))
            .translate((r_in, 0.0, 0.0))
            .rotate((0, 0, 0), (0, 0, 1), math.degrees(a))
        )
        ticks = seg if ticks is None else ticks.union(seg)
    return ticks


def _dial_needle(r: ResolvedDialCaliperConfig) -> cq.Workplane:
    """Indicator needle, points +X at q=0 (parent S0 L256-275)."""
    pointer = (
        cq.Workplane("XY")
        .polyline(
            [
                (-0.0030, 0.00060),
                (r.dial_face_r - 0.0020, 0.00018),
                (r.dial_face_r - 0.0020, -0.00018),
                (-0.0030, -0.00060),
            ]
        )
        .close()
        .extrude(0.0009)
    )
    hub = cq.Workplane("XY").circle(0.0016).extrude(0.0012)
    return pointer.union(hub)


def _lcd_housing(r: ResolvedDialCaliperConfig) -> cq.Workplane:
    """Flat LCD module housing with a recessed screen window (digital S1 L212-228)."""
    outer = (
        cq.Workplane("XY")
        .box(r.lcd_w, r.lcd_h, _LCD_D, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.002)
    )
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=_LCD_D - 0.0015)
        .rect(_SCREEN_W, _SCREEN_H)
        .extrude(0.002)
    )
    return outer.cut(cavity)


def _lcd_screen(r: ResolvedDialCaliperConfig) -> cq.Workplane:
    return cq.Workplane("XY").rect(_SCREEN_W - 0.001, _SCREEN_H - 0.001).extrude(0.0012)


def _lcd_segments(r: ResolvedDialCaliperConfig) -> cq.Workplane:
    """Connected backing plate + 4 digit-like 7-seg groups (digital S1 L240-280)."""
    backing = (
        cq.Workplane("XY")
        .box(_SCREEN_W - 0.004, _SCREEN_H - 0.004, 0.0003, centered=(True, True, True))
        .translate((0.0, 0.0, -0.0003))
    )
    bars = backing
    for dx in (-0.012, -0.004, 0.004, 0.012):
        for i in range(3):
            dy = -0.004 + i * 0.004
            seg = (
                cq.Workplane("XY")
                .box(0.005, 0.0008, 0.0006, centered=(True, True, True))
                .translate((dx, dy, 0.0))
            )
            bars = bars.union(seg)
        for side in (-1, 1):
            vseg = (
                cq.Workplane("XY")
                .box(0.0006, 0.008, 0.0006, centered=(True, True, True))
                .translate((dx + side * 0.003, 0.0, 0.0))
            )
            bars = bars.union(vseg)
    dot = (
        cq.Workplane("XY")
        .box(0.0012, 0.0012, 0.0006, centered=(True, True, True))
        .translate((0.000, -0.005, 0.0))
    )
    return bars.union(dot)


def _button_pad() -> cq.Workplane:
    base = cq.Workplane("XY").circle(0.0025).extrude(0.0018)
    cap = cq.Workplane("XY").workplane(offset=0.0018).circle(0.0022).extrude(0.0006)
    return base.union(cap)


def _main_scale_ticks(r: ResolvedDialCaliperConfig) -> cq.Workplane:
    """Engraved main-scale ticks along the beam top (vernier S2 L155-198).

    A connecting base strip ties all ticks into one mesh component."""
    n_major = 17
    minor_per_major = 10
    total = n_major * minor_per_major + 1
    x_start = 0.025
    x_end = min(0.195, r.beam_len - 0.010)
    span = x_end - x_start
    spacing = span / (total - 1)
    beam_top_z = _BEAM_T / 2.0
    tick_z = beam_top_z + 0.0003
    strip = (
        cq.Workplane("XY")
        .box(span + 0.002, 0.0008, 0.0004, centered=(True, True, True))
        .translate(((x_start + x_end) / 2.0, r.beam_h / 2.0 - 0.0004, beam_top_z + 0.0001))
    )
    result = strip
    for i in range(total):
        x_pos = x_start + i * spacing
        is_major = (i % minor_per_major) == 0
        is_half = (i % (minor_per_major // 2)) == 0 and not is_major
        if is_major:
            tick_len, tick_w = 0.0050, 0.00040
        elif is_half:
            tick_len, tick_w = 0.0035, 0.00030
        else:
            tick_len, tick_w = 0.0022, 0.00022
        tick = (
            cq.Workplane("XY")
            .box(tick_w, tick_len, 0.0006, centered=(True, True, True))
            .translate((x_pos, r.beam_h / 2.0 - tick_len / 2.0, tick_z))
        )
        result = result.union(tick)
    return result


def _thumb_roller() -> cq.Workplane:
    """18-flute knurled thumb roller (parent S0 L278-294)."""
    body = cq.Workplane("XY").circle(0.0060).extrude(0.0050, both=True)
    flutes = None
    for i in range(18):
        a = 2.0 * math.pi * i / 18
        cut = (
            cq.Workplane("XY")
            .box(0.0010, 0.0012, 0.0110, centered=(True, True, True))
            .translate((0.0060, 0.0, 0.0))
            .rotate((0, 0, 0), (0, 0, 1), math.degrees(a))
        )
        flutes = cut if flutes is None else flutes.union(cut)
    body = body.cut(flutes)
    hub = cq.Workplane("XY").circle(0.0016).extrude(0.0070, both=True)
    return body.union(hub)


def _depth_rod() -> cq.Workplane:
    return cq.Workplane("YZ").circle(_ROD_R).extrude(_ROD_LEN)


def _thumb_lip() -> cq.Workplane:
    """Molded push ridge with 3 grooves (norod S7 L275-299)."""
    ridge = (
        cq.Workplane("XY")
        .box(0.005, 0.008, _BEAM_T + 0.004, centered=(True, True, True))
        .edges("|Z")
        .fillet(0.0018)
    )
    grooves = None
    for i in range(3):
        z_off = -0.003 + i * 0.003
        groove = (
            cq.Workplane("XY")
            .box(0.006, 0.001, 0.0012, centered=(True, True, True))
            .translate((0.0, 0.003, z_off))
        )
        grooves = groove if grooves is None else grooves.union(groove)
    return ridge.cut(grooves)


def _lock_screw() -> cq.Workplane:
    """20-flute knurled lock-screw head + shaft (lockscrew S6 L279-322)."""
    head_r = 0.0040
    head_h = 0.0045
    shaft_r = 0.0018
    shaft_h = 0.0060
    head = cq.Workplane("XY").circle(head_r).extrude(head_h)
    flutes = None
    for i in range(20):
        a = 2.0 * math.pi * i / 20
        cut = (
            cq.Workplane("XY")
            .box(0.0008, 0.0010, head_h + 0.001, centered=(True, True, True))
            .translate((head_r, 0.0, head_h / 2.0))
            .rotate((0, 0, 0), (0, 0, 1), math.degrees(a))
        )
        flutes = cut if flutes is None else flutes.union(cut)
    head = head.cut(flutes)
    top_chamfer = (
        cq.Workplane("XY")
        .workplane(offset=head_h - 0.0006)
        .circle(head_r + 0.001)
        .circle(head_r - 0.0008)
        .extrude(0.0008)
    )
    head = head.cut(top_chamfer)
    shaft = cq.Workplane("XY").circle(shaft_r).extrude(shaft_h).translate((0.0, 0.0, -shaft_h))
    return head.union(shaft)


def _lock_screw_boss() -> cq.Workplane:
    return cq.Workplane("XY").circle(0.0055).extrude(0.0025)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_dial_caliper(
    config: DialCaliperConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    pal = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"caliper_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in pal.items()
    }

    def m(geom, name):
        return mesh_from_cadquery(geom, name, assets=assets)

    # --- Beam (root) -------------------------------------------------------
    beam = model.part("beam")
    beam.visual(m(_beam_body(r), "beam_body"), material=mats["steel"], name="beam_body", material_class_id="metal.stainless_matte")
    # Engraved scale strip along the +Z top face.
    beam.visual(
        m(
            cq.Workplane("XY")
            .box(r.beam_len - 0.02, 0.006, 0.0006, centered=(False, True, True))
            .translate((0.01, r.beam_h / 2.0 - 0.005, _BEAM_T / 2.0)),
            "beam_scale",
        ),
        material=mats["scale_dark"],
        name="beam_scale", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    # channel_beam: visible web + guide-rail marker visuals (S8 L405-427).
    if r.beam_profile == "channel_beam":
        beam.visual(
            m(
                cq.Workplane("XY")
                .box(
                    r.beam_len - 0.01, r.beam_h - 2.0 * _FLANGE_T - 0.002, _WEB_T - 0.0002,
                    centered=(False, True, True),
                )
                .translate((0.005, 0.0, 0.0)),
                "beam_web",
            ),
            material=mats["steel_dark"],
            name="beam_web", material_class_id="metal.blackened_gunmetal",
        )
        beam.visual(
            m(
                cq.Workplane("XY")
                .box(r.beam_len - 0.01, 0.0004, _RAIL_W + 0.0004, centered=(False, True, True))
                .translate((0.005, -r.beam_h / 2.0 + _RAIL_D + 0.0002, 0.0)),
                "guide_rail_mark",
            ),
            material=mats["scale_dark"],
            name="guide_rail_mark", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    # vernier: main-scale ticks on the beam top (vernier readout only).
    if r.readout == "vernier_scale":
        beam.visual(m(_main_scale_ticks(r), "main_scale_ticks"), material=mats["scale_dark"],
                    name="main_scale_ticks", appearance_only=AppearanceOnlySpec(kind="overlay"))
    beam.visual(m(_fixed_jaw(r), "fixed_jaw"), material=mats["steel"], name="fixed_jaw", material_class_id="metal.stainless_matte")
    beam.inertial = Inertial.from_geometry(
        Box((r.beam_len, r.beam_h + 2.0 * r.jaw_down_len, _BEAM_T)),
        mass=0.18,
        origin=Origin(xyz=(r.beam_len / 2.0, 0.0, 0.0)),
    )

    # --- Slider carriage ---------------------------------------------------
    slider = model.part("slider")
    slider.visual(m(_slider_body(r), "slider_body"), material=mats["steel_dark"], name="slider_body", material_class_id="metal.blackened_gunmetal")

    # Readout装置 (slider visuals; needle is a separate part below for analog).
    if r.readout == "analog_dial":
        dial_cx = 0.004
        dial_cy = r.beam_h / 2.0 + 0.004
        dial_cz = 0.0070
        slider.visual(m(_dial_bezel(r), "dial_bezel"), origin=Origin(xyz=(dial_cx, dial_cy, dial_cz)),
                      material=mats["chrome"], name="dial_bezel", material_class_id="metal.chrome_polished")
        slider.visual(m(_dial_face(r), "dial_face"), origin=Origin(xyz=(dial_cx, dial_cy, dial_cz)),
                      material=mats["dial_white"], name="dial_face", material_class_id="plastic.opaque_glossy_molded")
        slider.visual(m(_dial_ticks(r), "dial_ticks"),
                      origin=Origin(xyz=(dial_cx, dial_cy, dial_cz + 0.0018)),
                      material=mats["scale_dark"], name="dial_ticks", appearance_only=AppearanceOnlySpec(kind="overlay"))
    elif r.readout == "digital_lcd":
        lcd_cx = 0.004
        lcd_cy = r.beam_h / 2.0 + r.lcd_h / 2.0 - 0.002
        lcd_cz = 0.0050
        slider.visual(m(_lcd_housing(r), "lcd_housing"), origin=Origin(xyz=(lcd_cx, lcd_cy, lcd_cz)),
                      material=mats["housing_dark"], name="lcd_housing", material_class_id="plastic.opaque_glossy_molded")
        slider.visual(m(_lcd_screen(r), "lcd_screen"),
                      origin=Origin(xyz=(lcd_cx, lcd_cy, lcd_cz + _LCD_D - 0.0018)),
                      material=mats["lcd_bg"], name="lcd_screen", material_class_id="tech.control_interface")
        slider.visual(m(_lcd_segments(r), "lcd_segments"),
                      origin=Origin(xyz=(lcd_cx, lcd_cy, lcd_cz + _LCD_D - 0.0012)),
                      material=mats["lcd_seg"], name="lcd_segments", appearance_only=AppearanceOnlySpec(kind="screen", emission_strength=1.0))
        for i in range(2):
            bx = lcd_cx + (-0.010 + i * 0.020)
            by = lcd_cy - r.lcd_h / 2.0 + 0.004
            bz = lcd_cz + _LCD_D - 0.0002
            slider.visual(m(_button_pad(), f"button_{i}"), origin=Origin(xyz=(bx, by, bz)),
                          material=mats["button_dark"], name=f"button_{i}", material_class_id="plastic.opaque_glossy_molded")
    # vernier readout's ticks are fused into slider_body / beam main_scale_ticks.

    # Accessory (slider visuals; lock_screw is a separate part below).
    if r.accessory == "rod_and_roller":
        roller_x = 0.014
        roller_y = -r.beam_h / 2.0 + 0.002
        slider.visual(m(_thumb_roller(), "thumb_roller"), origin=Origin(xyz=(roller_x, roller_y, 0.0)),
                      material=mats["steel_dark"], name="thumb_roller", material_class_id="metal.blackened_gunmetal")
    elif r.accessory == "simplified_no_rod":
        lip_x = 0.014
        lip_y = -r.beam_h / 2.0 - 0.003
        slider.visual(m(_thumb_lip(), "thumb_lip"), origin=Origin(xyz=(lip_x, lip_y, 0.0)),
                      material=mats["steel_dark"], name="thumb_lip", material_class_id="metal.blackened_gunmetal")
    elif r.accessory == "lock_screw":
        saddle_top_z = (_BEAM_T + 0.005) / 2.0
        boss_x = -0.010
        slider.visual(m(_lock_screw_boss(), "lock_screw_boss"),
                      origin=Origin(xyz=(boss_x, 0.0, saddle_top_z)),
                      material=mats["steel_dark"], name="lock_screw_boss", material_class_id="metal.blackened_gunmetal")

    # Depth rod (has_depth_rod gate).
    if r.has_depth_rod:
        slider.visual(m(_depth_rod(), "depth_rod"), origin=Origin(xyz=(0.0, 0.0, 0.0)),
                      material=mats["steel"], name="depth_rod", material_class_id="metal.stainless_matte")

    slider.inertial = Inertial.from_geometry(
        Box((_CARRIAGE_W, r.beam_h + 2.0 * r.jaw_down_len, _BEAM_T + 0.02)),
        mass=0.05,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )

    # --- Skeleton PRISMATIC slide joint (every candidate) ------------------
    model.articulation(
        "beam_to_slider",
        ArticulationType.PRISMATIC,
        parent=beam,
        child=slider,
        origin=Origin(xyz=(r.slider_rest_x, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.20, lower=0.0, upper=r.slide_travel),
    )

    # --- Needle (analog only): CONTINUOUS +Z mimic of the slide -----------
    if r.has_needle:
        dial_cx = 0.004
        dial_cy = r.beam_h / 2.0 + 0.004
        dial_cz = 0.0070
        needle = model.part("needle")
        needle.visual(m(_dial_needle(r), "needle"), material=mats["needle_black"], name="needle", material_class_id="metal.blackened_gunmetal")
        needle.inertial = Inertial.from_geometry(
            Box((2.0 * r.dial_face_r, 0.002, 0.001)),
            mass=0.001,
            origin=Origin(xyz=(r.dial_face_r / 2.0, 0.0, 0.0)),
        )
        model.articulation(
            "slider_to_needle",
            ArticulationType.CONTINUOUS,
            parent=slider,
            child=needle,
            origin=Origin(xyz=(dial_cx, dial_cy, dial_cz + 0.0021)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=0.5, velocity=10.0),
        )

    # --- Lock screw (lock_screw only): REVOLUTE +Z on the boss ------------
    if r.accessory == "lock_screw":
        saddle_top_z = (_BEAM_T + 0.005) / 2.0
        boss_x = -0.010
        boss_top_z = saddle_top_z + 0.0025
        lock_screw = model.part("lock_screw")
        lock_screw.visual(m(_lock_screw(), "lock_screw"), material=mats["chrome"],
                          name="lock_screw_head", material_class_id="metal.chrome_polished")
        lock_screw.inertial = Inertial.from_geometry(
            Box((0.008, 0.008, 0.011)),
            mass=0.002,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        model.articulation(
            "slider_to_lock_screw",
            ArticulationType.REVOLUTE,
            parent=slider,
            child=lock_screw,
            origin=Origin(xyz=(boss_x, 0.0, boss_top_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=5.0, lower=0.0, upper=r.lock_screw_turn),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_dial_caliper(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_dial_caliper(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_dial_caliper_tests(
    model: ArticulatedObject,
    config: DialCaliperConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    beam = model.get_part("beam")
    slider = model.get_part("slider")
    slide = model.get_articulation("beam_to_slider")

    # --- Captured-interface element-scoped allowances (grandfathered joints). ---
    # Saddle wraps the beam (captured prismatic fit) — constant.
    ctx.allow_overlap(
        slider, beam, elem_a="slider_body", elem_b="beam_body",
        reason="The slider saddle wraps and rides on the beam (captured prismatic fit).",
    )
    # Depth rod rides the beam tail channel — only when has_depth_rod.
    if r.has_depth_rod:
        ctx.allow_overlap(
            slider, beam, elem_a="depth_rod", elem_b="beam_body",
            reason="The depth rod slides through the beam's tail channel (proxy solid beam).",
        )
    # Lock screw shaft threads into slider boss/body (captured fastener).
    if r.accessory == "lock_screw":
        lock_screw = model.get_part("lock_screw")
        ctx.allow_overlap(
            lock_screw, slider, elem_a="lock_screw_head", elem_b="slider_body",
            reason="The lock screw shaft is threaded into the slider body (captured fastener fit).",
        )
        ctx.allow_overlap(
            lock_screw, slider, elem_a="lock_screw_head", elem_b="lock_screw_boss",
            reason="The lock screw shaft passes through the mounting boss (captured fastener fit).",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # --- slot_choices recorded. ---
    ctx.check(
        "slot_choices_recorded",
        tuple(model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(model.meta.get("slot_choices")),
    )

    # --- Skeleton joint type / axis. ---
    ctx.check(
        "slide joint is PRISMATIC along +X",
        slide.joint_type == "prismatic"
        and tuple(round(c, 6) for c in slide.axis) == (1.0, 0.0, 0.0),
        details=f"type={slide.joint_type}, axis={slide.axis}",
    )

    # --- Articulation count matches the joint-topology class. ---
    n_joints = len(list(model.articulations))
    expected = 1 + (1 if r.has_needle else 0) + (1 if r.accessory == "lock_screw" else 0)
    ctx.check(
        "articulation count matches readout/accessory topology",
        n_joints == expected,
        details=f"got {n_joints} expected {expected}: {[j.name for j in model.articulations]}",
    )

    # --- Needle gating + CONTINUOUS +Z semantics. ---
    part_names = {p.name for p in model.parts}
    if r.has_needle:
        ctx.check("needle part present for analog_dial", "needle" in part_names,
                  details=str(part_names))
        nj = model.get_articulation("slider_to_needle")
        ctx.check(
            "needle joint is CONTINUOUS about +Z",
            nj.joint_type == "continuous"
            and tuple(round(c, 6) for c in nj.axis) == (0.0, 0.0, 1.0),
            details=f"type={nj.joint_type}, axis={nj.axis}",
        )
        needle = model.get_part("needle")
        with ctx.pose({nj: 0.0}):
            t0 = ctx.part_world_aabb(needle)
        with ctx.pose({nj: math.pi / 2.0}):
            t90 = ctx.part_world_aabb(needle)
        if t0 is not None and t90 is not None:
            ctx.check(
                "needle pivots about the dial center",
                abs(t90[1][1] - t0[1][1]) > 0.008 or abs(t90[1][0] - t0[1][0]) > 0.008,
                details=f"t0={t0[1]}, t90={t90[1]}",
            )
    else:
        ctx.check("no needle part on digital/vernier", "needle" not in part_names,
                  details=str(part_names))
        ctx.check(
            "no dial_ticks visual on digital/vernier",
            not any(v.name == "dial_ticks" for v in slider.visuals),
            details=str([v.name for v in slider.visuals]),
        )

    # --- Lock screw gating + REVOLUTE +Z semantics. ---
    if r.accessory == "lock_screw":
        ctx.check("lock_screw part present", "lock_screw" in part_names, details=str(part_names))
        lj = model.get_articulation("slider_to_lock_screw")
        ctx.check(
            "lock screw joint is REVOLUTE about +Z",
            lj.joint_type == "revolute"
            and tuple(round(c, 6) for c in lj.axis) == (0.0, 0.0, 1.0),
            details=f"type={lj.joint_type}, axis={lj.axis}",
        )
    else:
        ctx.check("no lock_screw part unless lock_screw accessory",
                  "lock_screw" not in part_names, details=str(part_names))

    # --- Depth rod gating. ---
    has_rod_visual = any(v.name == "depth_rod" for v in slider.visuals)
    ctx.check(
        "depth_rod present iff has_depth_rod",
        has_rod_visual == r.has_depth_rod,
        details=f"rod_visual={has_rod_visual}, has_depth_rod={r.has_depth_rod}",
    )

    # --- Identity: a slender caliper beam along +X. ---
    beam_aabb = ctx.part_element_world_aabb(beam, elem="beam_body")
    if beam_aabb is not None:
        ext_x = beam_aabb[1][0] - beam_aabb[0][0]
        ext_y = beam_aabb[1][1] - beam_aabb[0][1]
        ext_z = beam_aabb[1][2] - beam_aabb[0][2]
        ctx.check(
            "beam is a slender graduated bar along +X",
            ext_x > 4.0 * max(ext_y, ext_z),
            details=f"ext_x={ext_x:.4f} ext_y={ext_y:.4f} ext_z={ext_z:.4f}",
        )

    # --- Mechanism: sliding opens the jaw gap (and extends the rod). ---
    def jaw_gap() -> float | None:
        sj = ctx.part_element_world_aabb(slider, elem="slider_body")
        fjb = ctx.part_element_world_aabb(beam, elem="fixed_jaw")
        if sj is None or fjb is None:
            return None
        return sj[0][0] - fjb[1][0]

    with ctx.pose({slide: slide.motion_limits.lower}):
        gap0 = jaw_gap()
        rest_cx = ctx.part_world_position(slider)
        ctx.fail_if_parts_overlap_in_current_pose(name="rest_no_overlap")
    with ctx.pose({slide: slide.motion_limits.upper}):
        gap1 = jaw_gap()
        ext_cx = ctx.part_world_position(slider)
        ctx.fail_if_parts_overlap_in_current_pose(name="extended_no_overlap")

    if rest_cx is not None and ext_cx is not None:
        ctx.check(
            "carriage advances by full travel along +X only",
            abs((ext_cx[0] - rest_cx[0]) - r.slide_travel) < 0.002
            and abs(ext_cx[1] - rest_cx[1]) < 0.001
            and abs(ext_cx[2] - rest_cx[2]) < 0.001,
            details=f"rest={rest_cx}, ext={ext_cx}, travel={r.slide_travel:.4f}",
        )
    if gap0 is not None and gap1 is not None:
        ctx.check(
            "sliding opens the jaw gap",
            gap1 > gap0 + 0.05,
            details=f"gap0={gap0:.4f}, gap1={gap1:.4f}",
        )

    return ctx.report()


__all__ = (
    "DialCaliperConfig",
    "ResolvedDialCaliperConfig",
    "build_dial_caliper",
    "build_seeded_dial_caliper",
    "config_from_seed",
    "resolve_config",
    "run_dial_caliper_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
