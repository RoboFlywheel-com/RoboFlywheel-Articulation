# SPDX-License-Identifier: Apache-2.0

"""pictureX_0611_compass — modular procedural template.

Magnetic pocket/field direction compass (NOT a drawing compass): a shallow
compass capsule with a graduated dial (degree ticks + N/E/S/W cardinals), a
freely rotating magnetic indicator (two-color needle or full rotating compass
card) on a central pivot, a coaxial rotating bezel carrying the glass lens,
and a real rear-hinged protective cover. Carrier platforms range from the
round pocket shell through a square lensatic field shell and a transparent
hiking baseplate to a wrist-cradle mount.

Slots (spec: articraft_template_authoring/specs_modular_v1/pictureX_0611_compass.md):

- Slot A case_platform (root, ③+①): round_pocket_case / square_lensatic_case /
  rectangular_baseplate / wrist_cradle_case.  hanging_ring part is emitted by
  the round/square case modules only (skeleton delta).
- Slot B indicator (②): two_color_needle / full_dial_card / liquid_damped_needle.
- Slot C cover (③): domed_lid / mirror_sighting_lid / sight_wire_lid /
  square_flat_lid / flat_clear_lid, gated per case via _COVERS_BY_CASE.

Module sources (all rating=5):

- origin  rec_picturex_0611__compass__001__png__airflex_batch_20260710_5dc1d1be20f148ab990f9a9c4b4f551c
- forks   rec_picturex0611_compass_fork_{rectangular_baseplate,square_lensatic_case,
          full_dial_card,liquid_damped_capsule,mirror_sighting_cover,
          sight_wire_cover,wrist_mount_cradle}_20260714

Joint mating policy (AUTHORING §A Rule 2):

- case_to_bezel and case_to_indicator carry real MatingContracts (flat seats:
  case top face <-> bezel_ring bottom; pivot_pin top <-> indicator hub bottom).
- case_to_cover and case_to_ring are captured-pin joints (hinge pin through the
  cover knuckle; hanging-ring eye around its retaining pin).  Their geometry is
  not two axis-aligned faces in contact, so per Rule 2 they omit ``mating`` and
  are grandfathered; run_tests pins them with expect_contact / expect_within
  plus element-scoped allow_overlap.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

CaseStyle = Literal[
    "round_pocket_case",
    "square_lensatic_case",
    "rectangular_baseplate",
    "wrist_cradle_case",
]
IndicatorStyle = Literal["two_color_needle", "full_dial_card", "liquid_damped_needle"]
CoverStyle = Literal[
    "domed_lid",
    "mirror_sighting_lid",
    "sight_wire_lid",
    "square_flat_lid",
    "flat_clear_lid",
]
PaletteStyle = Literal["nickel_silver", "olive_field", "black_polymer", "antique_brass"]

_CASE_STYLES: tuple[CaseStyle, ...] = (
    "round_pocket_case",
    "square_lensatic_case",
    "rectangular_baseplate",
    "wrist_cradle_case",
)
_INDICATOR_STYLES: tuple[IndicatorStyle, ...] = (
    "two_color_needle",
    "full_dial_card",
    "liquid_damped_needle",
)
_PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "nickel_silver",
    "olive_field",
    "black_polymer",
    "antique_brass",
)

# Compatibility matrix (spec §9): which lid families a case platform accepts.
_COVERS_BY_CASE: dict[str, tuple[str, ...]] = {
    "round_pocket_case": ("domed_lid", "mirror_sighting_lid", "sight_wire_lid"),
    "wrist_cradle_case": ("domed_lid", "mirror_sighting_lid", "sight_wire_lid"),
    "square_lensatic_case": ("square_flat_lid", "mirror_sighting_lid", "sight_wire_lid"),
    "rectangular_baseplate": ("flat_clear_lid",),
}

# Fixed small-hardware dimensions (standardized pocket-instrument hardware;
# source: origin model.py L191-L247).
_KNUCKLE_R = 0.0031
_PIN_R = 0.00145
_HUB_R = 0.0030
_HUB_H = 0.0012
_PIVOT_R = 0.00115
_LID_ROOT = 0.0039  # lid body starts this far from the hinge axis (clears pin+knuckles)
# Hinge-leaf tab reach (see _leaf_tabs). Near edge stays inside the cover
# knuckle and clear of the hinge pin; far edge must pass _LID_ROOT to embed in
# the lid body. Source leaf depth is 7mm (origin L61-L63); 5.8mm here.
_LEAF_TAB_NEAR_Y = -0.0017
_LEAF_TAB_FAR_Y = -0.0075
_RIM_BAR_EMBED = 0.0010  # sight-frame cross bar embed into the 3.5mm rim wall
_LENS_LOCAL_C = 0.00285
_LENS_TH = 0.00065


@dataclass(frozen=True)
class PictureX0611CompassConfig:
    case_style: CaseStyle = "round_pocket_case"
    indicator_style: IndicatorStyle = "two_color_needle"
    cover_style: CoverStyle = "domed_lid"
    palette_style: PaletteStyle = "nickel_silver"
    dial_tick_count: int = 36
    bezel_grip_count: int = 24

    radial_scale: float = 1.0
    height_scale: float = 1.0
    open_angle_deg: float = 112.0
    indicator_rest_deg: float = 24.0
    plate_length: float = 0.130
    plate_width: float = 0.058
    strap_length_scale: float = 1.0


@dataclass(frozen=True)
class ResolvedPictureX0611CompassConfig:
    case_style: str
    indicator_style: str
    cover_style: str
    palette_style: str
    dial_tick_count: int
    bezel_grip_count: int

    s: float  # radial scale
    h: float  # height scale
    open_rad: float
    rest_rad: float

    # case platform
    deck_z: float
    dial_top_z: float
    case_top_z: float
    dial_r: float
    case_outer_r: float  # envelope radius (round family) / half diag proxy
    square_side: float
    plate_len: float
    plate_wid: float
    plate_th: float
    cap_in: float
    cap_out: float
    cap_h: float
    has_ring: bool
    ring_pin_y: float
    ring_z: float
    case_top_visual: str
    strap_len: float

    # bezel
    bez_ring_out: float
    bez_ring_in: float
    bez_seat_out: float
    bez_seat_in: float
    glass_r: float
    grip_r: float
    bez_z: float
    bezel_top_z: float
    lens_bottom_z: float
    has_glass_lens: bool
    bowl_apex_z: float

    # hinge
    hinge_y: float
    hinge_z: float
    knuckle_x: float
    knuckle_len: float
    pin_len: float
    cover_knuckle_len: float

    # indicator
    pivot_top_z: float
    needle_len_n: float
    needle_len_s: float
    card_r: float
    indicator_part: str
    bowl_r: float
    bowl_sphere_r: float
    bowl_base_z: float
    bowl_clip_h: float
    fluid_r: float
    fluid_h: float

    # cover
    dome_r: float
    frame_r: float
    panel_w: float
    panel_l: float
    lid_len_y: float  # square lid
    disc_r: float
    cover_under_drop: float
    lid_visual: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _weighted(rng: random.Random, weights: dict):
    keys = list(weights.keys())
    return rng.choices(keys, weights=[weights[k] for k in keys], k=1)[0]


def config_from_seed(seed: int) -> PictureX0611CompassConfig:
    rng = random.Random(seed)
    case_style: CaseStyle = _weighted(
        rng,
        {
            "round_pocket_case": 0.34,
            "square_lensatic_case": 0.24,
            "rectangular_baseplate": 0.22,
            "wrist_cradle_case": 0.20,
        },
    )
    cover_style: CoverStyle = rng.choice(_COVERS_BY_CASE[case_style])
    indicator_style: IndicatorStyle = _weighted(
        rng,
        {"two_color_needle": 0.40, "full_dial_card": 0.32, "liquid_damped_needle": 0.28},
    )
    if case_style == "square_lensatic_case":
        palette_style: PaletteStyle = _weighted(
            rng,
            {
                "olive_field": 0.45,
                "nickel_silver": 0.20,
                "black_polymer": 0.20,
                "antique_brass": 0.15,
            },
        )
    else:
        palette_style = rng.choice(_PALETTE_STYLES)
    return PictureX0611CompassConfig(
        case_style=case_style,
        indicator_style=indicator_style,
        cover_style=cover_style,
        palette_style=palette_style,
        dial_tick_count=rng.choice((24, 36)),
        bezel_grip_count=rng.choice((16, 24)),
        radial_scale=round(rng.uniform(0.92, 1.12), 4),
        height_scale=round(rng.uniform(0.90, 1.15), 4),
        open_angle_deg=round(rng.uniform(95.0, 120.0), 2),
        indicator_rest_deg=round(rng.uniform(-60.0, 60.0), 2),
        plate_length=round(rng.uniform(0.120, 0.148), 4),
        plate_width=round(rng.uniform(0.052, 0.066), 4),
        strap_length_scale=round(rng.uniform(0.90, 1.15), 4),
    )


def resolve_config(
    config: PictureX0611CompassConfig,
) -> ResolvedPictureX0611CompassConfig:
    case_style = config.case_style if config.case_style in _CASE_STYLES else "round_pocket_case"
    indicator_style = (
        config.indicator_style
        if config.indicator_style in _INDICATOR_STYLES
        else "two_color_needle"
    )
    legal_covers = _COVERS_BY_CASE[case_style]
    cover_style = config.cover_style if config.cover_style in legal_covers else legal_covers[0]
    palette_style = (
        config.palette_style if config.palette_style in _PALETTE_STYLES else "nickel_silver"
    )
    tick = int(config.dial_tick_count) if int(config.dial_tick_count) in (24, 36) else 36
    grips = int(config.bezel_grip_count) if int(config.bezel_grip_count) in (16, 24) else 24

    s = _clamp(float(config.radial_scale), 0.92, 1.12)
    h = _clamp(float(config.height_scale), 0.90, 1.15)
    open_rad = math.radians(_clamp(float(config.open_angle_deg), 95.0, 120.0))
    rest_rad = math.radians(_clamp(float(config.indicator_rest_deg), -60.0, 60.0))
    strap_scale = _clamp(float(config.strap_length_scale), 0.90, 1.15)

    plate_th = 0.003
    square_side = 0.082 * s
    cap_in = 0.0420 * s
    cap_out = 0.0445 * s
    cap_h = 0.0140 * h
    plate_wid = _clamp(float(config.plate_width), 0.052, 0.066)
    # capsule must leave readable baseplate strips on both ends (spec inequality)
    plate_len = max(_clamp(float(config.plate_length), 0.120, 0.148), 2.55 * cap_out)

    if case_style == "rectangular_baseplate":
        deck_z = plate_th
        case_top_z = plate_th + cap_h
        dial_r = 0.0360 * s
        case_outer_r = cap_out
        # The bezel ring must LAND ON the capsule wall's top face (r in
        # [cap_in, cap_out]), mirroring how the round case's ring straddles its
        # shell lip (origin: ring band [0.0368,0.0410] over top face
        # [0.0358,0.0388] -> 2mm annular seat; ring_out = case_outer_r+0.0015).
        # The fork seated the ring wholly inside the bore (band
        # [cap_in-0.0045, cap_in-0.0005]), so no wall material sat beneath it
        # and the bezel floated off the plate as an isolated part.
        # Inner radius / seat / lens are unchanged, so the fork's internal
        # ring-seat-lens-grip relationships are preserved exactly.
        bez_ring_out = cap_out + 0.0008
        bez_ring_in = cap_in - 0.0045
        bez_seat_out = cap_in - 0.0040
        bez_seat_in = cap_in - 0.0058
        glass_r = cap_in - 0.0050
        grip_r = bez_ring_out - 0.0007
        knuckle_x = 0.0140 * s
        knuckle_len = 0.010 * s
        has_ring = False
        case_top_visual = "capsule_wall"
    elif case_style == "square_lensatic_case":
        deck_z = 0.0108 * h
        case_top_z = 0.0130 * h
        dial_r = 0.0355 * s
        case_outer_r = square_side / 2.0
        bez_ring_out = 0.0410 * s
        bez_ring_in = 0.0368 * s
        bez_seat_out = 0.0375 * s
        bez_seat_in = 0.0358 * s
        glass_r = 0.0373 * s
        grip_r = 0.0403 * s
        knuckle_x = 0.0210 * s
        knuckle_len = 0.0140 * s
        has_ring = True
        case_top_visual = "case_shell"
    else:  # round_pocket_case / wrist_cradle_case
        deck_z = 0.0108 * h
        case_top_z = 0.0128 * h
        dial_r = 0.0355 * s
        case_outer_r = 0.0395 * s
        bez_ring_out = 0.0410 * s
        bez_ring_in = 0.0368 * s
        bez_seat_out = 0.0375 * s
        bez_seat_in = 0.0358 * s
        glass_r = 0.0373 * s
        grip_r = 0.0403 * s
        knuckle_x = 0.0210 * s
        knuckle_len = 0.0140 * s
        has_ring = case_style == "round_pocket_case"
        case_top_visual = "case_shell"

    dial_top_z = deck_z + 0.0007
    # Seat the bezel bottom face directly on the authored case top face for
    # every case style (round/wrist/square: shell lip; baseplate: capsule wall
    # top, which case_top_z already equals via plate_th + cap_h).  The former
    # -0.0004 baseplate offset was an unsourced tuned constant (Contract 3e)
    # that only masked the real defect: the ring band sat inside the bore.
    bez_z = case_top_z
    lens_bottom_z = bez_z + _LENS_LOCAL_C - _LENS_TH / 2.0
    bezel_top_z = bez_z + _LENS_LOCAL_C + _LENS_TH / 2.0

    # hinge tower fully outside the bezel swept envelope (grips included), so
    # bezel rotation can never clip the hinge (Contract 3c single-sourcing).
    grip_outer = grip_r + 0.00105
    bezel_swept_r = max(bez_ring_out, grip_outer) + 0.0006
    if case_style == "rectangular_baseplate":
        hinge_y = max(cap_out + 0.0005, bezel_swept_r + _KNUCKLE_R + 0.0003)
    else:
        hinge_y = bezel_swept_r + _KNUCKLE_R + 0.0003

    # indicator stack
    bowl_base_z = dial_top_z + 0.0001
    if indicator_style == "liquid_damped_needle":
        pivot_top_z = bowl_base_z + 0.0004
        needle_len_n = 0.0245 * s
        needle_len_s = 0.0215 * s
        indicator_part = "magnetic_needle"
    elif indicator_style == "full_dial_card":
        pivot_top_z = dial_top_z + 0.0023
        needle_len_n = 0.0275 * s
        needle_len_s = 0.0240 * s
        indicator_part = "dial_card"
    else:
        pivot_top_z = dial_top_z + 0.0023
        needle_len_n = 0.0275 * s
        needle_len_s = 0.0240 * s
        indicator_part = "magnetic_needle"
    card_r = 0.0330 * s
    bowl_r = 0.0338 * s
    bowl_sphere_r = 0.090 * s
    bowl_clip_h = 0.0065
    fluid_r = 0.0325 * s
    fluid_h = 0.0032

    # --- Sealed-capsule window resolution (spec Reject #8) -------------------
    # A liquid-damped compass has ONE transparent window: the sealed capsule
    # dome itself.  The liquid fork inherited the bezel's flat glass_lens from
    # the origin AND added the dome, stacking two windows -- so the dome had to
    # punch ~2.5mm through the lens on every non-baseplate seed.  The dome
    # cannot instead shrink under the lens: the headroom there (~2.9mm) is less
    # than the needle stack the dome must contain, so the lens is the redundant
    # element.  On liquid seeds the dome IS the window and the bezel's lens is
    # omitted; the dome rises through the bezel bore with real radial clearance
    # (bowl_r < bez_seat_in < bez_ring_in, asserted in run_tests).  The bezel
    # stays a connected solid via its ring<->seat overlap, and no
    # capsule_bowl x glass_lens allowance is needed.
    has_glass_lens = indicator_style != "liquid_damped_needle"
    bowl_apex_z = bowl_base_z + min(
        bowl_clip_h, bowl_sphere_r - math.sqrt(max(bowl_sphere_r**2 - bowl_r**2, 0.0))
    )
    # True top of the case+bezel stack the closed cover must clear.  Single
    # source (Contract 3c): on liquid seeds the dome, not the lens, is highest.
    stack_top_z = bezel_top_z
    if indicator_style == "liquid_damped_needle":
        stack_top_z = max(stack_top_z, bowl_apex_z)

    cover_under_drop = 0.0010 if cover_style == "domed_lid" else 0.0
    hinge_z = stack_top_z + cover_under_drop + 0.0007

    pin_len = 2.0 * knuckle_x + knuckle_len + 0.004 * s
    cover_knuckle_len = 2.0 * (knuckle_x - knuckle_len / 2.0 - 0.001)

    # covers (built in the CLOSED frame; hinge edge at y=-_LID_ROOT)
    dome_r = hinge_y - _LID_ROOT
    frame_r = hinge_y - _LID_ROOT
    panel_w = min(0.0760 * s, square_side - 0.004) if case_style == "square_lensatic_case" else 0.0760 * s
    panel_l = hinge_y + dial_r - 0.004 * s - _LID_ROOT
    lid_len_y = hinge_y + square_side / 2.0 - _LID_ROOT
    disc_r = cap_in - 0.001
    lid_visual = {
        "domed_lid": "cover_dome",
        "mirror_sighting_lid": "cover_panel",
        "sight_wire_lid": "sight_frame",
        "square_flat_lid": "cover_plate",
        "flat_clear_lid": "cover_disc",
    }[cover_style]

    ring_pin_y = -(case_outer_r + 0.0055 * s)
    if case_style == "square_lensatic_case":
        ring_pin_y = -(square_side / 2.0 + 0.004 * s)
    ring_z = 0.0070 * h

    return ResolvedPictureX0611CompassConfig(
        case_style=case_style,
        indicator_style=indicator_style,
        cover_style=cover_style,
        palette_style=palette_style,
        dial_tick_count=tick,
        bezel_grip_count=grips,
        s=s,
        h=h,
        open_rad=open_rad,
        rest_rad=rest_rad,
        deck_z=deck_z,
        dial_top_z=dial_top_z,
        case_top_z=case_top_z,
        dial_r=dial_r,
        case_outer_r=case_outer_r,
        square_side=square_side,
        plate_len=plate_len,
        plate_wid=plate_wid,
        plate_th=plate_th,
        cap_in=cap_in,
        cap_out=cap_out,
        cap_h=cap_h,
        has_ring=has_ring,
        ring_pin_y=ring_pin_y,
        ring_z=ring_z,
        case_top_visual=case_top_visual,
        strap_len=0.052 * strap_scale * s,
        bez_ring_out=bez_ring_out,
        bez_ring_in=bez_ring_in,
        bez_seat_out=bez_seat_out,
        bez_seat_in=bez_seat_in,
        glass_r=glass_r,
        grip_r=grip_r,
        bez_z=bez_z,
        bezel_top_z=bezel_top_z,
        has_glass_lens=has_glass_lens,
        bowl_apex_z=bowl_apex_z,
        lens_bottom_z=lens_bottom_z,
        hinge_y=hinge_y,
        hinge_z=hinge_z,
        knuckle_x=knuckle_x,
        knuckle_len=knuckle_len,
        pin_len=pin_len,
        cover_knuckle_len=cover_knuckle_len,
        pivot_top_z=pivot_top_z,
        needle_len_n=needle_len_n,
        needle_len_s=needle_len_s,
        card_r=card_r,
        indicator_part=indicator_part,
        bowl_r=bowl_r,
        bowl_sphere_r=bowl_sphere_r,
        bowl_base_z=bowl_base_z,
        bowl_clip_h=bowl_clip_h,
        fluid_r=fluid_r,
        fluid_h=fluid_h,
        dome_r=dome_r,
        frame_r=frame_r,
        panel_w=panel_w,
        panel_l=panel_l,
        lid_len_y=lid_len_y,
        disc_r=disc_r,
        cover_under_drop=cover_under_drop,
        lid_visual=lid_visual,
    )


def slot_choices_for_config(
    r: ResolvedPictureX0611CompassConfig,
) -> tuple[tuple[str, str], ...]:
    return (
        ("case_platform", r.case_style),
        ("indicator", r.indicator_style),
        ("cover", r.cover_style),
        ("palette", r.palette_style),
        ("dial_ticks", str(r.dial_tick_count)),
        ("bezel_grips", str(r.bezel_grip_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# palettes / materials
# ---------------------------------------------------------------------------

_PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "nickel_silver": {
        "body": (0.68, 0.69, 0.68, 1.0),
        "hardware": (0.82, 0.84, 0.83, 1.0),
        "cover": (0.68, 0.69, 0.68, 1.0),
    },
    "olive_field": {
        "body": (0.18, 0.22, 0.13, 1.0),
        "hardware": (0.78, 0.80, 0.79, 1.0),
        "cover": (0.20, 0.24, 0.14, 1.0),
    },
    "black_polymer": {
        "body": (0.10, 0.10, 0.11, 1.0),
        "hardware": (0.75, 0.77, 0.78, 1.0),
        "cover": (0.12, 0.12, 0.13, 1.0),
    },
    "antique_brass": {
        "body": (0.55, 0.44, 0.20, 1.0),
        "hardware": (0.72, 0.62, 0.35, 1.0),
        "cover": (0.52, 0.42, 0.19, 1.0),
    },
}


def _materials(model: ArticulatedObject, r: ResolvedPictureX0611CompassConfig) -> dict:
    pal = _PALETTES[r.palette_style]
    mats = {
        "body": model.material("case_body", rgba=pal["body"]),
        "hardware": model.material("polished_steel", rgba=pal["hardware"]),
        "cover": model.material("cover_body", rgba=pal["cover"]),
        "dial": model.material("dial_black", rgba=(0.035, 0.040, 0.038, 1.0)),
        "mark": model.material("marking_white", rgba=(0.88, 0.88, 0.82, 1.0)),
        "ivory": model.material("needle_ivory", rgba=(0.91, 0.86, 0.63, 1.0)),
        "green": model.material("needle_green", rgba=(0.10, 0.34, 0.25, 1.0)),
        "dark": model.material("latch_black", rgba=(0.045, 0.047, 0.045, 1.0)),
        "glass": model.material("clear_glass", rgba=(0.72, 0.82, 0.82, 0.22)),
        "red": model.material("direction_red", rgba=(0.78, 0.12, 0.10, 1.0)),
    }
    if r.case_style == "rectangular_baseplate" or r.cover_style == "flat_clear_lid":
        mats["acrylic"] = model.material("clear_acrylic", rgba=(0.85, 0.90, 0.92, 0.35))
        mats["capsule_dark"] = model.material("capsule_dark", rgba=(0.08, 0.09, 0.08, 1.0))
    if r.cover_style == "mirror_sighting_lid":
        mats["mirror"] = model.material("mirror_glass", rgba=(0.88, 0.90, 0.92, 0.85))
    if r.cover_style == "sight_wire_lid":
        mats["luminous"] = model.material("luminous_green", rgba=(0.35, 0.78, 0.32, 1.0))
    if r.indicator_style == "liquid_damped_needle":
        mats["fluid"] = model.material("damping_fluid", rgba=(0.62, 0.78, 0.76, 0.18))
        mats["capsule_glass"] = model.material("capsule_window", rgba=(0.74, 0.84, 0.82, 0.28))
        mats["gasket"] = model.material("gasket_rubber", rgba=(0.12, 0.13, 0.12, 1.0))
        mats["luminous_n"] = model.material("luminous_north", rgba=(0.55, 0.92, 0.48, 1.0))
    if r.case_style == "wrist_cradle_case":
        mats["rubber"] = model.material("strap_rubber", rgba=(0.04, 0.04, 0.05, 1.0))
    return mats


# ---------------------------------------------------------------------------
# cadquery geometry helpers (adapted from the 5-star sources; primitive
# sophistication preserved — lathe revolve / sphere booleans / text glyphs)
# ---------------------------------------------------------------------------


def _annulus(outer_radius: float, inner_radius: float, height: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(outer_radius).circle(inner_radius).extrude(height)


def _round_case_shell(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    """Stepped stamped cup, revolved radial section (origin L27-L44)."""
    s, h = r.s, r.h
    radial_section = [
        (0.0, 0.0),
        (0.0378 * s, 0.0),
        (0.0390 * s, 0.0012 * h),
        (0.0395 * s, 0.0098 * h),
        (0.0388 * s, 0.0128 * h),
        (0.0358 * s, 0.0128 * h),
        (0.0358 * s, 0.0108 * h),
        (0.0, 0.0108 * h),
    ]
    return (
        cq.Workplane("XZ").polyline(radial_section).close().revolve(360.0, (0, 0), (0, 1))
    )


def _square_case_shell(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    """Rounded-square field shell with circular capsule well (square fork L39-L56)."""
    body = (
        cq.Workplane("XY")
        .rect(r.square_side, r.square_side)
        .extrude(r.case_top_z)
        .edges("|Z")
        .fillet(0.008 * r.s)
    )
    well_depth = r.case_top_z - r.deck_z + 0.001
    well = (
        cq.Workplane("XY")
        .workplane(offset=r.deck_z)
        .circle(0.036 * r.s)
        .extrude(well_depth)
    )
    return body.cut(well)


def _baseplate_plate(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    """Transparent rectangular baseplate with capsule cutout (rect fork L41-L56)."""
    plate = (
        cq.Workplane("XY")
        .rect(r.plate_len, r.plate_wid)
        .extrude(r.plate_th)
        .edges("|Z")
        .fillet(0.006)
    )
    hole = cq.Workplane("XY").circle(r.cap_in - 0.001).extrude(r.plate_th)
    return plate.cut(hole)


def _bezel_ring_mesh(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    ring = _annulus(r.bez_ring_out, r.bez_ring_in, 0.0030)
    seat = _annulus(r.bez_seat_out, r.bez_seat_in, 0.0010).translate((0, 0, 0.0018))
    return ring.union(seat)


def _needle_half(length: float, half_width: float, forward: bool = True) -> cq.Workplane:
    tip = length if forward else -length
    points = [(0.0, -half_width), (0.0, half_width), (tip, 0.0)]
    return cq.Workplane("XY").polyline(points).close().extrude(0.00055)


def _hanging_ring_mesh(s: float) -> cq.Workplane:
    large = _annulus(0.0128 * s, 0.0103 * s, 0.0021 * s).translate((0, -0.0120 * s, -0.00105 * s))
    eye = _annulus(0.0042 * s, 0.0021 * s, 0.0021 * s).translate((0, 0, -0.00105 * s))
    bridge = (
        cq.Workplane("XY")
        .box(0.0060 * s, 0.0070 * s, 0.0021 * s)
        .translate((0, -0.0040 * s, -0.00105 * s))
    )
    return large.union(eye).union(bridge)


_CARDINAL_FONT_PATH = Path(__file__).resolve().parent / "fonts" / "DroidSans.ttf"
_TEXT_EXTRUDE = 0.00032
# Glyphs the box-stroke fallback can draw (the only letters this template emits).
_STROKED_GLYPHS = frozenset("NESW")


def _occ_text_solid(letter: str, size: float, font_path: Optional[str]) -> Optional[cq.Workplane]:
    """Extruded OCC glyph solid; None when OCC yields a zero-face shape.

    When the font cannot be resolved (headless worker with no fontconfig fonts,
    bundled TTF absent), Font_BRepTextBuilder returns an EMPTY compound and
    cadquery dies with ``IndexError: list index out of range`` at
    ``text_flat.Faces()[0]`` in occ_impl/shapes.py.  Contain that here.
    """
    try:
        glyph = cq.Workplane("XY").text(
            letter, size, _TEXT_EXTRUDE, combine=False, halign="center", valign="center",
            fontPath=font_path,
        )
    except Exception:
        return None
    return glyph if glyph.faces().vals() else None


def _stroked_cardinal_mesh(letter: str, size: float) -> cq.Workplane:
    """Box-stroke block letter (N/E/S/W) for environments where OCC font
    rendering is unavailable; centered at the origin like halign/valign=center."""
    bar_w = size * 0.16
    half_h = size / 2.0
    half_w = size * 0.32

    def _bar(cx: float, cy: float, dx: float, dy: float, yaw_deg: float = 0.0) -> cq.Workplane:
        bar = cq.Workplane("XY").box(dx, dy, _TEXT_EXTRUDE)
        if yaw_deg:
            bar = bar.rotate((0, 0, 0), (0, 0, 1), yaw_deg)
        return bar.translate((cx, cy, _TEXT_EXTRUDE / 2.0))

    n_yaw = math.degrees(math.atan2(2.0 * half_h, 2.0 * half_w))
    n_diag = math.hypot(2.0 * half_w, 2.0 * half_h)
    w_yaw = math.degrees(math.atan2(2.0 * half_h, half_w / 2.0))
    w_diag = math.hypot(half_w / 2.0, 2.0 * half_h)
    strokes = {
        "N": [
            _bar(-half_w, 0.0, bar_w, 2.0 * half_h),
            _bar(half_w, 0.0, bar_w, 2.0 * half_h),
            _bar(0.0, 0.0, n_diag, bar_w, n_yaw),
        ],
        "E": [
            _bar(-half_w, 0.0, bar_w, 2.0 * half_h),
            _bar(0.0, half_h - bar_w / 2.0, 2.0 * half_w, bar_w),
            _bar(-0.1 * half_w, 0.0, 1.8 * half_w, bar_w),
            _bar(0.0, -(half_h - bar_w / 2.0), 2.0 * half_w, bar_w),
        ],
        "S": [
            _bar(0.0, half_h - bar_w / 2.0, 2.0 * half_w, bar_w),
            _bar(0.0, 0.0, 2.0 * half_w, bar_w),
            _bar(0.0, -(half_h - bar_w / 2.0), 2.0 * half_w, bar_w),
            _bar(-(half_w - bar_w / 2.0), half_h / 2.0, bar_w, half_h),
            _bar(half_w - bar_w / 2.0, -half_h / 2.0, bar_w, half_h),
        ],
        "W": [
            # continuous zigzag: each stroke shares an endpoint with the next,
            # so the union is a single connected solid
            _bar(-0.75 * half_w, 0.0, w_diag, bar_w, -w_yaw),
            _bar(-0.25 * half_w, 0.0, w_diag, bar_w, w_yaw),
            _bar(0.25 * half_w, 0.0, w_diag, bar_w, -w_yaw),
            _bar(0.75 * half_w, 0.0, w_diag, bar_w, w_yaw),
        ],
    }[letter]
    mesh = strokes[0]
    for stroke in strokes[1:]:
        mesh = mesh.union(stroke)
    return mesh


def _cardinal_text(
    letter: str, x: float, y: float, yaw_deg: float, size: float
) -> Optional[cq.Workplane]:
    """Cardinal glyph solid placed at (x, y); None for empty/unsupported text.

    combine=False builds the glyph as a standalone solid (the pattern used by
    mechanical_timer); the default combine="cut" cuts into the (empty)
    workplane and produces zero faces under the worker's OCC build.  Font
    resolution chains bundled DroidSans -> OCC system font -> stroked block
    letter, so no environment can produce a zero-face text solid.
    """
    letter = (letter or "").strip()
    if not letter:
        return None
    font_path = str(_CARDINAL_FONT_PATH) if _CARDINAL_FONT_PATH.is_file() else None
    glyph = _occ_text_solid(letter, size, font_path)
    if glyph is None and font_path is not None:
        glyph = _occ_text_solid(letter, size, None)
    if glyph is None:
        if letter not in _STROKED_GLYPHS:
            return None
        glyph = _stroked_cardinal_mesh(letter, size)
    return glyph.rotate((0, 0, 0), (0, 0, 1), yaw_deg).translate((x, y, 0.0))


def _leaf_tabs() -> cq.Workplane:
    """Two hinge-leaf tabs bridging the lid body to the cover knuckle.

    Depth is source-faithful: the origin's hinge leaf is a 7mm-deep box
    (``box(0.026, 0.007, 0.0022)`` at origin L61-L63) that reaches from the
    knuckle well into the lid body. A 2.5mm tab (y in [-0.0042, -0.0017]) never
    reached any lid body -- every lid's near surface sits at y <= -0.00393 (the
    sight frame's rim starts at -0.00429 at x=+-0.0055 and -0.00508 at
    x=+-0.0095) -- so the tabs + knuckle floated off as an island.

    Tab span y in [_LEAF_TAB_FAR_Y, _LEAF_TAB_NEAR_Y]:
    - near edge -0.0017 stays inside the cover knuckle (r 0.0030) and clears the
      case hinge pin (r 0.00145), so pin clearance is unchanged;
    - far edge -0.0075 embeds >=2.4mm into every lid body at both tab x bands.

    Extending the FAR edge adds swept volume only in the radius band
    [0.00465, 0.00776] about the hinge axis, which the lid body itself already
    sweeps (its own near edge is _LID_ROOT=0.0039), so no new collision.
    """
    tabs: Optional[cq.Workplane] = None
    depth = _LEAF_TAB_NEAR_Y - _LEAF_TAB_FAR_Y
    for x in (-0.0055, 0.0055):
        tab = (
            cq.Workplane("XY")
            .box(0.008, depth, 0.0020)
            .translate((x, (_LEAF_TAB_NEAR_Y + _LEAF_TAB_FAR_Y) / 2.0, 0.0010))
        )
        tabs = tab if tabs is None else tabs.union(tab)
    assert tabs is not None
    return tabs


def _dome_lid_mesh(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    """Open-backed spherical-cap shell + rolled rim (origin L47-L64)."""
    radius = r.dome_r
    sphere_radius = radius * (0.112 / 0.0388)
    sphere_center_z = -math.sqrt(sphere_radius**2 - radius**2)
    clip = cq.Workplane("XY").circle(radius).extrude(0.012 * r.h)
    outer = (
        cq.Workplane("XY").sphere(sphere_radius).translate((0, 0, sphere_center_z)).intersect(clip)
    )
    inner = (
        cq.Workplane("XY")
        .sphere(sphere_radius)
        .translate((0, 0, sphere_center_z - 0.0010))
        .intersect(clip)
    )
    shell = outer.cut(inner)
    rim = _annulus(radius, radius - 0.0030, 0.0020).translate((0, 0, -0.0010))
    lid = shell.union(rim).translate((0, -(radius + _LID_ROOT), 0.0))
    return lid.union(_leaf_tabs())


def _mirror_panel_mesh(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    """Framed sighting panel: sight slot + distal notch (mirror fork L47-L92)."""
    width, length, thickness = r.panel_w, r.panel_l, 0.0015
    panel = cq.Workplane("XY").rect(width, length).extrude(thickness)
    panel = panel.edges("|Z").fillet(0.0030)
    slot = (
        cq.Workplane("XY")
        .rect(0.0025, length * 0.70)
        .extrude(thickness + 0.002)
        .translate((0, 0, -0.001))
    )
    panel = panel.cut(slot)
    notch = (
        cq.Workplane("XY")
        .rect(0.0080, 0.0050)
        .extrude(thickness + 0.002)
        .translate((0, -length / 2.0 + 0.0050 / 2.0 - 0.001, -0.001))
    )
    panel = panel.cut(notch)
    panel = panel.translate((0, -(length / 2.0 + _LID_ROOT), 0.0))
    return panel.union(_leaf_tabs())


def _mirror_face_mesh(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    w = r.panel_w - 0.008
    length = r.panel_l - 0.010
    return (
        cq.Workplane("XY")
        .rect(w, length)
        .extrude(0.0004)
        .translate((0, -(r.panel_l / 2.0 + _LID_ROOT), 0.00150))
    )


def _sight_line_mesh(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .rect(0.0006, r.panel_l * 0.88)
        .extrude(0.00018)
        .translate((0, -(r.panel_l / 2.0 + _LID_ROOT), 0.00190))
    )


def _sight_frame_mesh(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    """Protective rim + cross bar (sight-wire fork L47-L61; bar re-oriented
    along x so the sight wire itself spans the opening along y)."""
    radius = r.frame_r
    rim_width = 0.0035
    rim_height = 0.0028
    inner_r = radius - rim_width
    rim = _annulus(radius, inner_r, rim_height)
    # The bar must land INSIDE the rim wall, not merely span the bore: at
    # 2*inner_r - 0.001 it stopped 0.5mm short of the bore on each side, so the
    # cq union returned two disjoint solids and the bar meshed as an island.
    # Embed _RIM_BAR_EMBED into the (rim_width=3.5mm) wall on each side.
    cross_bar = (
        cq.Workplane("XY")
        .box(2.0 * (inner_r + _RIM_BAR_EMBED), 0.0028, rim_height)
        .translate((0, 0, rim_height / 2.0))
    )
    frame = rim.union(cross_bar).translate((0, -(radius + _LID_ROOT), 0.0))
    return frame.union(_leaf_tabs())


def _sight_wire_mesh(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    """Sighting wire spanning the frame opening IN the lid plane (spec Reject #6:
    a wire along the lid normal would stab the lens at the closed pose)."""
    inner_r = r.frame_r - 0.0035
    wire_len = 2.0 * inner_r - 0.001
    wire = (
        cq.Workplane("XZ")
        .circle(0.0007)
        .extrude(wire_len)
        .translate((0, wire_len / 2.0, 0.0))  # recenter along y
    )
    return wire.translate((0, -(r.frame_r + _LID_ROOT), 0.0014))


def _sight_dot_mesh(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    return cq.Workplane("XY").sphere(0.0015).translate((0, -(r.frame_r + _LID_ROOT), 0.0014))


def _square_lid_mesh(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    """Rounded-square flat lid (square fork L58-L69)."""
    thickness = 0.002
    plate = (
        cq.Workplane("XY")
        .rect(r.square_side, r.lid_len_y)
        .extrude(thickness)
        .edges("|Z")
        .fillet(0.008 * r.s)
    )
    plate = plate.translate((0, -(r.lid_len_y / 2.0 + _LID_ROOT), 0.0))
    return plate.union(_leaf_tabs())


def _clear_disc_mesh(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    """Clear acrylic disc lid (rect fork L85-L94)."""
    disc = cq.Workplane("XY").circle(r.disc_r).extrude(0.0012)
    disc = disc.translate((0, -(r.disc_r + _LID_ROOT), 0.0))
    return disc.union(_leaf_tabs())


def _capsule_bowl_mesh(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    """Sealed transparent dome for the liquid capsule (liquid fork L79-L99)."""
    radius = r.bowl_r
    sphere_radius = r.bowl_sphere_r
    sphere_center_z = -math.sqrt(sphere_radius**2 - radius**2)
    clip = cq.Workplane("XY").circle(radius).extrude(r.bowl_clip_h)
    outer = (
        cq.Workplane("XY").sphere(sphere_radius).translate((0, 0, sphere_center_z)).intersect(clip)
    )
    inner = (
        cq.Workplane("XY")
        .sphere(sphere_radius - 0.0009)
        .translate((0, 0, sphere_center_z))
        .intersect(clip)
    )
    shell = outer.cut(inner)
    base_flange = _annulus(radius + 0.0012, radius - 0.0006, 0.0008)
    return shell.union(base_flange)


def _damping_vane_mesh() -> cq.Workplane:
    blade = cq.Workplane("XY").box(0.0140, 0.0050, 0.0006)
    spine = cq.Workplane("XY").box(0.0020, 0.0050, 0.0012)
    return blade.union(spine)


def _wrist_cradle_mesh(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    """Curved wrist cradle under the case (wrist fork L79-L109)."""
    s = r.s
    radius = 0.050 * s
    t = 0.003
    w = 0.058 * s
    half_y = 0.024 * s
    outer = cq.Workplane("YZ").circle(radius).extrude(w / 2.0, both=True)
    inner = cq.Workplane("YZ").circle(radius - t).extrude(w / 2.0, both=True)
    tube = outer.cut(inner)
    cut_below = (
        cq.Workplane("XY")
        .box(w + 0.01, 2 * radius + 0.01, radius + 0.01)
        .translate((0, 0, -(radius + 0.01) / 2.0))
    )
    cut_side_p = (
        cq.Workplane("XY")
        .box(w + 0.01, radius, 2 * radius + 0.01)
        .translate((0, half_y + radius / 2.0, 0))
    )
    cut_side_n = (
        cq.Workplane("XY")
        .box(w + 0.01, radius, 2 * radius + 0.01)
        .translate((0, -(half_y + radius / 2.0), 0))
    )
    result = tube.cut(cut_below).cut(cut_side_p).cut(cut_side_n)
    return result.translate((0, 0, -(radius - 0.0005)))


def _strap_band_mesh(r: ResolvedPictureX0611CompassConfig) -> cq.Workplane:
    length = r.strap_len
    width = 0.020 * r.s
    thickness = 0.003
    body = cq.Workplane("XY").box(length, width, thickness)
    for x_sign in (-1.0, 1.0):
        cap = (
            cq.Workplane("XY")
            .circle(width / 2.0)
            .extrude(thickness)
            .translate((x_sign * length / 2.0, 0, -thickness / 2.0))
        )
        body = body.union(cap)
    return body


# ---------------------------------------------------------------------------
# module emitters
# ---------------------------------------------------------------------------


def _emit_dial_deck(case, r: ResolvedPictureX0611CompassConfig, mats, *, with_markings: bool):
    """Dial face + graduation decoration on the case deck (origin L143-L196).

    Decoration is derived from the final dial surface (dial_top_z / dial_r), so
    it hugs the deck across case prototypes and s/h scaling (Rule 4).
    """
    case.visual(
        Cylinder(radius=r.dial_r, length=0.0007),
        origin=Origin(xyz=(0.0, 0.0, r.deck_z + 0.00035)),
        material=mats["dial"],
        name="dial_face", material_class_id="metal.paint_coated",
    )
    if with_markings:
        n = r.dial_tick_count
        for index in range(n):
            angle = 2.0 * math.pi * index / n
            major = index % 3 == 0
            radial_length = (0.0052 if major else 0.0032) * r.s
            width = (0.00075 if major else 0.00042) * r.s
            radius = r.dial_r - 0.0033 * r.s - radial_length / 2.0
            case.visual(
                Box((radial_length, width, 0.00030)),
                origin=Origin(
                    xyz=(radius * math.cos(angle), radius * math.sin(angle), r.dial_top_z + 0.0001),
                    rpy=(0.0, 0.0, angle),
                ),
                material=mats["mark"],
                name=f"dial_tick_{index}", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
        cardinal_r = r.dial_r * 0.648
        for letter, x, y, yaw in (
            ("N", 0.0, cardinal_r, 0.0),
            ("E", cardinal_r, 0.0, -90.0),
            ("S", 0.0, -cardinal_r, 180.0),
            ("W", -cardinal_r, 0.0, 90.0),
        ):
            glyph = _cardinal_text(letter, x, y, yaw, 0.0062 * r.s)
            if glyph is None:
                continue
            case.visual(
                mesh_from_cadquery(
                    glyph,
                    f"cardinal_{letter.lower()}",
                    tolerance=0.00012,
                ),
                origin=Origin(xyz=(0.0, 0.0, r.dial_top_z - 0.00002)),
                material=mats["mark"],
                name=f"cardinal_{letter.lower()}", appearance_only=AppearanceOnlySpec(kind="text", text=str(letter)),
            )
        case.visual(
            Box((0.0048 * r.s, 0.0015 * r.s, 0.00035)),
            origin=Origin(
                xyz=(0.0, r.dial_r * 0.789, r.dial_top_z + 0.00014),
                rpy=(0.0, 0.0, math.pi / 2.0),
            ),
            material=mats["ivory"],
            name="north_index", material_class_id="metal.paint_coated",
        )
    # central pivot post (fixed to case; carries the indicator)
    pivot_len = r.pivot_top_z - (r.dial_top_z - 0.0004)
    case.visual(
        Cylinder(radius=_PIVOT_R, length=pivot_len),
        origin=Origin(xyz=(0.0, 0.0, r.pivot_top_z - pivot_len / 2.0)),
        material=mats["hardware"],
        name="pivot_pin", material_class_id="metal.chrome_polished",
    )


def _emit_hinge_tower(case, r: ResolvedPictureX0611CompassConfig, mats):
    """Rear hinge: bridge on the case top -> riser posts -> knuckles + pin.

    All z/y positions derive from bezel_top_z / hinge_y / hinge_z so the tower
    always clears the bezel swept envelope (Contract 3c).
    """
    bridge_top = r.bez_z - 0.0002
    bridge_bot = r.case_top_z - (0.0020 if r.case_style == "rectangular_baseplate" else 0.0028)
    if r.case_style == "rectangular_baseplate":
        bridge_y_in = r.cap_in + 0.0002
    elif r.case_style == "square_lensatic_case":
        bridge_y_in = 0.0360 * r.s
    else:
        bridge_y_in = 0.0350 * r.s
    bridge_y_out = r.hinge_y + 0.0032
    case.visual(
        Box((2.0 * r.knuckle_x + 0.018 * r.s, bridge_y_out - bridge_y_in, bridge_top - bridge_bot)),
        origin=Origin(
            xyz=(0.0, (bridge_y_in + bridge_y_out) / 2.0, (bridge_top + bridge_bot) / 2.0)
        ),
        material=mats["body"],
        name="hinge_bridge", material_class_id="metal.brushed_silver",
    )
    post_bot = bridge_top - 0.0006
    post_top = r.hinge_z - _KNUCKLE_R + 0.0008
    for suffix, x in (("0", -r.knuckle_x), ("1", r.knuckle_x)):
        case.visual(
            Box((0.010 * r.s, 0.0064, post_top - post_bot)),
            origin=Origin(xyz=(x, r.hinge_y, (post_top + post_bot) / 2.0)),
            material=mats["body"],
            name=f"hinge_post_{suffix}", material_class_id="metal.brushed_silver",
        )
        case.visual(
            Cylinder(radius=_KNUCKLE_R, length=r.knuckle_len),
            origin=Origin(xyz=(x, r.hinge_y, r.hinge_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["body"],
            name=f"hinge_knuckle_{suffix}", material_class_id="metal.brushed_silver",
        )
    case.visual(
        Cylinder(radius=_PIN_R, length=r.pin_len),
        origin=Origin(xyz=(0.0, r.hinge_y, r.hinge_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["hardware"],
        name="hinge_pin", material_class_id="metal.chrome_polished",
    )


def _emit_side_latch(case, r: ResolvedPictureX0611CompassConfig, mats):
    """Side latch fully below the bezel plane (adapted from origin L224-L229)."""
    latch_z = (r.case_top_z - 0.0025 + r.bez_z - 0.0002) / 2.0
    latch_h = (r.bez_z - 0.0002) - (r.case_top_z - 0.0025)
    latch_x = r.case_outer_r + 0.0005
    case.visual(
        Box((0.0060 * r.s, 0.0050 * r.s, latch_h)),
        origin=Origin(xyz=(latch_x, 0.0110 * r.s, latch_z), rpy=(0.0, 0.0, 0.35)),
        material=mats["dark"],
        name="side_latch", material_class_id="metal.blackened_gunmetal",
    )


_RING_PIN_LEN_C = 0.0060  # origin L237: Cylinder(radius=0.0018, length=0.0060)
_RING_PIN_HEAD_TH = 0.0008  # origin L243: head disc thickness
_RING_PIN_HEAD_EMBED = 0.0002  # head sinks 0.2mm onto the pin top (no float-drift island)


def _ring_pin_top_z(r: ResolvedPictureX0611CompassConfig) -> float:
    """Single source of truth for the ring pin's top face z (Contract 3c).

    The pin-head disc used to hard-code ``ring_z + 0.0034*h`` while the pin top
    is ``ring_z + (0.0060*h)/2``; the two agreed only at h==1, so every seed
    with h>1 opened a ``0.0004*(h-1)`` gap and the head fell off as an island.
    Both the pin and its head now derive from this one helper.
    """
    return r.ring_z + (_RING_PIN_LEN_C * r.h) / 2.0


def _emit_ring_lug(case, r: ResolvedPictureX0611CompassConfig, mats):
    """Front lug + retaining pin for the hanging ring (origin L230-L247)."""
    lug_y = r.ring_pin_y + 0.0032 * r.s
    case.visual(
        Box((0.0090 * r.s, 0.0090 * r.s, 0.0050 * r.h)),
        origin=Origin(xyz=(0.0, lug_y, 0.0068 * r.h)),
        material=mats["body"],
        name="ring_lug", material_class_id="metal.brushed_silver",
    )
    case.visual(
        Cylinder(radius=0.0018, length=_RING_PIN_LEN_C * r.h),
        origin=Origin(xyz=(0.0, r.ring_pin_y, r.ring_z)),
        material=mats["hardware"],
        name="ring_pin", material_class_id="metal.chrome_polished",
    )
    # Head centered so its underside sits _RING_PIN_HEAD_EMBED below the pin top
    # face -> guaranteed material overlap at every sampled height_scale.
    head_z = _ring_pin_top_z(r) - _RING_PIN_HEAD_EMBED + _RING_PIN_HEAD_TH / 2.0
    case.visual(
        Cylinder(radius=0.0030, length=_RING_PIN_HEAD_TH),
        origin=Origin(xyz=(0.0, r.ring_pin_y, head_z)),
        material=mats["hardware"],
        name="ring_pin_head", material_class_id="metal.chrome_polished",
    )


def _emit_case(model: ArticulatedObject, r: ResolvedPictureX0611CompassConfig, mats):
    """Slot A: case platform (root). Non-articulating carrier details (cradle,
    straps, ruler marks, corner screws) are fused case visuals per Rule 1."""
    case = model.part(
        "case",
        meta={"module": r.case_style, "construction": "compass carrier platform"},
    )
    if r.case_style == "rectangular_baseplate":
        case.visual(
            mesh_from_cadquery(_baseplate_plate(r), "baseplate_body", tolerance=0.0003),
            material=mats["acrylic"],
            name="base_plate", material_class_id="plastic.clear_rigid",
        )
        case.visual(
            mesh_from_cadquery(
                _annulus(r.cap_out, r.cap_in, r.cap_h).translate((0, 0, r.plate_th)),
                "capsule_wall",
                tolerance=0.00025,
            ),
            material=mats["body"],
            name="capsule_wall", material_class_id="metal.brushed_silver",
        )
        case.visual(
            mesh_from_cadquery(
                cq.Workplane("XY").circle(r.cap_in).extrude(r.plate_th),
                "capsule_floor",
                tolerance=0.00025,
            ),
            material=mats["capsule_dark"],
            name="capsule_floor", material_class_id="plastic.opaque_generic",
        )
        # ruler marks + direction-of-travel arrow: derived from the realized
        # plate footprint (Rule 4 host-conformal decoration).
        ruler_z = r.plate_th + 0.0001
        for i in range(12):
            y_pos = -r.plate_wid / 2.0 + 0.008 + i * (r.plate_wid - 0.016) / 11.0
            tick_len = 0.004 if i % 5 == 0 else 0.002
            for side, x_edge in (("left", -r.plate_len / 2.0), ("right", r.plate_len / 2.0)):
                sign = 1.0 if side == "left" else -1.0
                case.visual(
                    Box((tick_len, 0.0004, 0.0003)),
                    origin=Origin(xyz=(x_edge + sign * (tick_len / 2.0 + 0.001), y_pos, ruler_z)),
                    material=mats["mark"],
                    name=f"ruler_{side}_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
                )
        arrow_y = -r.plate_wid / 2.0 + 0.012
        case.visual(
            Box((0.003, 0.018, 0.0004)),
            origin=Origin(xyz=(0.0, arrow_y, ruler_z)),
            material=mats["red"],
            name="direction_arrow_shaft", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        case.visual(
            Box((0.006, 0.004, 0.0004)),
            origin=Origin(xyz=(0.0, arrow_y - 0.011, ruler_z)),
            material=mats["red"],
            name="direction_arrow_head", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    elif r.case_style == "square_lensatic_case":
        case.visual(
            mesh_from_cadquery(_square_case_shell(r), "field_case_shell", tolerance=0.00025),
            material=mats["body"],
            name="case_shell", material_class_id="metal.brushed_silver",
        )
        corner_inset = 0.032 * r.s
        for i, (cx, cy) in enumerate(
            [
                (corner_inset, corner_inset),
                (-corner_inset, corner_inset),
                (corner_inset, -corner_inset),
                (-corner_inset, -corner_inset),
            ]
        ):
            case.visual(
                Cylinder(radius=0.0018, length=0.0010),
                origin=Origin(xyz=(cx, cy, r.case_top_z + 0.0002)),
                material=mats["hardware"],
                name=f"corner_screw_{i}", material_class_id="metal.chrome_polished",
            )
    else:  # round_pocket_case / wrist_cradle_case
        case.visual(
            mesh_from_cadquery(_round_case_shell(r), "compass_case_shell", tolerance=0.00025),
            material=mats["body"],
            name="case_shell", material_class_id="metal.brushed_silver",
        )

    with_markings = r.indicator_style != "full_dial_card"
    _emit_dial_deck(case, r, mats, with_markings=with_markings)
    _emit_hinge_tower(case, r, mats)
    if r.case_style != "rectangular_baseplate":
        _emit_side_latch(case, r, mats)
    if r.has_ring:
        _emit_ring_lug(case, r, mats)

    if r.case_style == "wrist_cradle_case":
        case.visual(
            mesh_from_cadquery(_wrist_cradle_mesh(r), "wrist_cradle_plate", tolerance=0.0002),
            material=mats["body"],
            name="wrist_cradle", material_class_id="metal.brushed_silver",
        )
        for x_sign in (-1.0, 1.0):
            side = "left" if x_sign < 0 else "right"
            for lug_idx in range(2):
                y_off = 0.012 * r.s * (2 * lug_idx - 1)
                case.visual(
                    Box((0.012 * r.s, 0.007 * r.s, 0.005)),
                    origin=Origin(xyz=(x_sign * 0.041 * r.s, y_off, 0.0050)),
                    material=mats["body"],
                    name=f"strap_lug_{side}_{lug_idx}", material_class_id="metal.brushed_silver",
                )
            case.visual(
                Cylinder(radius=0.0012, length=0.028 * r.s),
                origin=Origin(xyz=(x_sign * 0.041 * r.s, 0.0, 0.0050), rpy=(math.pi / 2.0, 0, 0)),
                material=mats["hardware"],
                name=f"spring_bar_{side}", material_class_id="metal.chrome_polished",
            )
            strap_center = 0.041 * r.s + r.strap_len / 2.0 - 0.001
            case.visual(
                mesh_from_cadquery(_strap_band_mesh(r), f"strap_band_{side}", tolerance=0.0002),
                origin=Origin(xyz=(x_sign * strap_center, 0.0, 0.0050)),
                material=mats["rubber"],
                name=f"strap_band_{side}", material_class_id="rubber.smooth_plain",
            )
            case.visual(
                Box((0.005, 0.024 * r.s, 0.006)),
                origin=Origin(xyz=(x_sign * (0.041 * r.s + 0.019 * r.s), 0.0, 0.0050)),
                material=mats["rubber"],
                name=f"strap_keeper_{side}", material_class_id="rubber.smooth_plain",
            )
            for hole_idx in range(3):
                hole_x = x_sign * (strap_center + (hole_idx - 1) * 0.008)
                case.visual(
                    Cylinder(radius=0.0014, length=0.006),
                    origin=Origin(xyz=(hole_x, 0.0, 0.0050)),
                    material=mats["dark"],
                    name=f"strap_hole_{side}_{hole_idx}", material_class_id="rubber.smooth_plain",
                )
    return case


def _emit_bezel(model: ArticulatedObject, case, r: ResolvedPictureX0611CompassConfig, mats):
    """Rotating bezel with glass lens + grip serration (origin L249-L271).
    Seats flat on the case top face — real MatingContract."""
    bezel = model.part("bezel")
    bezel.visual(
        mesh_from_cadquery(_bezel_ring_mesh(r), "compass_bezel_ring", tolerance=0.00018),
        material=mats["hardware"] if r.palette_style == "black_polymer" else mats["body"],
        name="bezel_ring", material_class_id="metal.brushed_silver",
    )
    # On liquid-damped seeds the sealed capsule dome is the window, so the flat
    # bezel lens is omitted (see resolve_config: "Sealed-capsule window
    # resolution").  The bezel remains one connected solid through its
    # ring<->seat radial overlap, which does not depend on the lens.
    if r.has_glass_lens:
        bezel.visual(
            Cylinder(radius=r.glass_r, length=_LENS_TH),
            origin=Origin(xyz=(0.0, 0.0, _LENS_LOCAL_C)),
            material=mats["glass"],
            name="glass_lens", material_class_id="glass.clear_transparent",
        )
    n = r.bezel_grip_count
    for index in range(n):
        angle = 2.0 * math.pi * index / n
        bezel.visual(
            Box((0.0021, 0.00055, 0.0018)),
            origin=Origin(
                xyz=(r.grip_r * math.cos(angle), r.grip_r * math.sin(angle), 0.0015),
                rpy=(0.0, 0.0, angle),
            ),
            material=mats["hardware"],
            name=f"bezel_grip_{index}", material_class_id="metal.chrome_polished",
        )
    model.articulation(
        "case_to_bezel",
        ArticulationType.REVOLUTE,
        parent=case,
        child=bezel,
        origin=Origin(xyz=(0.0, 0.0, r.bez_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.25, velocity=2.0, lower=-math.pi, upper=math.pi),
        mating=MatingContract(
            parent_face_geometry=r.case_top_visual,
            parent_face_side="positive_z",
            child_face_geometry="bezel_ring",
            child_face_side="negative_z",
            contact_tol=0.001,
        ),
    )
    return bezel


def _emit_indicator(model: ArticulatedObject, case, r: ResolvedPictureX0611CompassConfig, mats):
    """Slot B: free-rotating magnetic indicator on the pivot pin.

    The hub SEATS ON the pivot-pin top face (flat contact -> real
    MatingContract), adapting the sources' captured-bore pivot while keeping
    the same part tree and primitives."""
    if r.indicator_style == "full_dial_card":
        card = model.part("dial_card")
        card_thickness = 0.00050
        card.visual(
            mesh_from_cadquery(
                cq.Workplane("XY").circle(r.card_r).circle(0.0014).extrude(card_thickness),
                "card_disk",
                tolerance=0.00018,
            ),
            origin=Origin(xyz=(0.0, 0.0, 0.0002), rpy=(0.0, 0.0, r.rest_rad)),
            material=mats["dial"],
            name="card_disk", material_class_id="plastic.opaque_glossy_molded",
        )
        half_w = 0.0022 * r.s
        tri = cq.Workplane("XY").polyline(
            [(0.0, -half_w), (0.0, half_w), (r.card_r * 0.63, 0.0)]
        ).close().extrude(0.00035)
        card.visual(
            mesh_from_cadquery(tri, "card_north_triangle", tolerance=0.00015),
            origin=Origin(xyz=(0.0, 0.0, 0.0002 + card_thickness), rpy=(0.0, 0.0, r.rest_rad)),
            material=mats["ivory"],
            name="north_triangle", material_class_id="metal.paint_coated",
        )
        n = r.dial_tick_count
        for index in range(n):
            angle = 2.0 * math.pi * index / n + r.rest_rad
            major = index % 3 == 0
            radial_length = (0.0052 if major else 0.0032) * r.s
            width = (0.00075 if major else 0.00042) * r.s
            tick_r = r.card_r - 0.0008 - radial_length / 2.0
            card.visual(
                Box((radial_length, width, 0.00030)),
                origin=Origin(
                    xyz=(
                        tick_r * math.cos(angle),
                        tick_r * math.sin(angle),
                        0.0002 + card_thickness + 0.0001,
                    ),
                    rpy=(0.0, 0.0, angle),
                ),
                material=mats["mark"],
                name=f"card_tick_{index}", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
        label_r = r.card_r - 0.0090 * r.s
        for letter, lx, ly, yaw in (
            ("N", 0.0, label_r, 0.0),
            ("E", label_r, 0.0, -90.0),
            ("S", 0.0, -label_r, 180.0),
            ("W", -label_r, 0.0, 90.0),
        ):
            glyph = _cardinal_text(letter, lx, ly, yaw, 0.0062 * r.s)
            if glyph is None:
                continue
            card.visual(
                mesh_from_cadquery(
                    glyph,
                    f"card_cardinal_{letter.lower()}",
                    tolerance=0.00012,
                ),
                origin=Origin(xyz=(0.0, 0.0, 0.0002 + card_thickness - 0.00008), rpy=(0.0, 0.0, r.rest_rad)),
                material=mats["mark"],
                name=f"cardinal_{letter.lower()}", appearance_only=AppearanceOnlySpec(kind="text", text=str(letter)),
            )
        card.visual(
            Cylinder(radius=_HUB_R, length=_HUB_H),
            origin=Origin(xyz=(0.0, 0.0, _HUB_H / 2.0)),
            material=mats["hardware"],
            name="card_hub", material_class_id="metal.chrome_polished",
        )
        indicator = card
        hub_visual = "card_hub"
    else:
        needle = model.part("magnetic_needle")
        needle.visual(
            mesh_from_cadquery(
                _needle_half(r.needle_len_n, 0.0022 * r.s, True), "needle_north"
            ),
            origin=Origin(xyz=(0.0, 0.0, 0.0003), rpy=(0.0, 0.0, r.rest_rad)),
            material=mats["ivory"],
            name="north_pointer", material_class_id="metal.paint_coated",
        )
        needle.visual(
            mesh_from_cadquery(
                _needle_half(r.needle_len_s, 0.0018 * r.s, False), "needle_south"
            ),
            origin=Origin(xyz=(0.0, 0.0, 0.0003), rpy=(0.0, 0.0, r.rest_rad)),
            material=mats["green"],
            name="south_pointer", material_class_id="metal.paint_coated",
        )
        needle.visual(
            Cylinder(radius=_HUB_R, length=_HUB_H),
            origin=Origin(xyz=(0.0, 0.0, _HUB_H / 2.0)),
            material=mats["hardware"],
            name="needle_hub", material_class_id="metal.chrome_polished",
        )
        if r.indicator_style == "liquid_damped_needle":
            needle.visual(
                mesh_from_cadquery(_damping_vane_mesh(), "needle_damping_vane", tolerance=0.00014),
                origin=Origin(xyz=(0.0, 0.0, 0.00135), rpy=(0.0, 0.0, r.rest_rad)),
                material=mats["hardware"],
                name="damping_vane", material_class_id="metal.chrome_polished",
            )
            tip_r = r.needle_len_n - 0.0015
            needle.visual(
                Cylinder(radius=0.0018, length=0.0004),
                origin=Origin(
                    xyz=(tip_r * math.cos(r.rest_rad), tip_r * math.sin(r.rest_rad), 0.00055)
                ),
                material=mats["luminous_n"],
                name="luminous_north_tip", material_class_id="tech.emissive_surface",
            )
            # sealed capsule assembly rides the case (liquid fork L232-L254)
            case.visual(
                mesh_from_cadquery(_capsule_bowl_mesh(r), "capsule_bowl_shell", tolerance=0.00022),
                origin=Origin(xyz=(0.0, 0.0, r.bowl_base_z)),
                material=mats["capsule_glass"],
                name="capsule_bowl", material_class_id="glass.clear_transparent",
            )
            case.visual(
                Cylinder(radius=r.fluid_r, length=r.fluid_h),
                origin=Origin(xyz=(0.0, 0.0, r.bowl_base_z + r.fluid_h / 2.0)),
                material=mats["fluid"],
                name="fluid_fill", material_class_id="liquid.water_wave_foam",
            )
            case.visual(
                mesh_from_cadquery(
                    _annulus(r.bowl_r + 0.0012, r.bowl_r - 0.0006, 0.0010),
                    "capsule_gasket_ring",
                    tolerance=0.00018,
                ),
                origin=Origin(xyz=(0.0, 0.0, r.bowl_base_z - 0.0001)),
                material=mats["gasket"],
                name="capsule_gasket", material_class_id="rubber.smooth_plain",
            )
        indicator = needle
        hub_visual = "needle_hub"

    model.articulation(
        "case_to_indicator",
        ArticulationType.REVOLUTE,
        parent=case,
        child=indicator,
        origin=Origin(xyz=(0.0, 0.0, r.pivot_top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.01, velocity=8.0, lower=-math.pi, upper=math.pi),
        mating=MatingContract(
            parent_face_geometry="pivot_pin",
            parent_face_side="positive_z",
            child_face_geometry=hub_visual,
            child_face_side="negative_z",
            contact_tol=0.001,
        ),
    )
    return indicator


def _emit_cover(model: ArticulatedObject, case, r: ResolvedPictureX0611CompassConfig, mats):
    """Slot C: hinged protective lid.

    Lids are modeled in the CLOSED frame (hinge edge at y=-_LID_ROOT, body
    toward -y, thickness +z) and authored OPEN via visual rpy=(-open,0,0);
    joint zero = open reference pose, lower=-open = closed, upper=+8 deg.

    case_to_cover is a captured-pin hinge (pin through the cover knuckle):
    per Rule 2 it has no flat mating faces, so ``mating`` is omitted
    (grandfathered); run_tests declares the scoped allow_overlap and
    expect_contact for the captured pin."""
    cover = model.part("cover", meta={"module": r.cover_style})
    open_rpy = (-r.open_rad, 0.0, 0.0)
    cover_mat = mats["cover"]
    if r.cover_style == "domed_lid":
        cover.visual(
            mesh_from_cadquery(_dome_lid_mesh(r), "compass_cover_dome", tolerance=0.00025),
            origin=Origin(rpy=open_rpy),
            material=cover_mat,
            name="cover_dome", material_class_id="metal.brushed_silver",
        )
    elif r.cover_style == "mirror_sighting_lid":
        cover.visual(
            mesh_from_cadquery(_mirror_panel_mesh(r), "mirror_sighting_panel", tolerance=0.00025),
            origin=Origin(rpy=open_rpy),
            material=cover_mat,
            name="cover_panel", material_class_id="metal.brushed_silver",
        )
        cover.visual(
            mesh_from_cadquery(_mirror_face_mesh(r), "cover_mirror_face", tolerance=0.00018),
            origin=Origin(rpy=open_rpy),
            material=mats["mirror"],
            name="mirror_face", material_class_id="glass.mirror",
        )
        cover.visual(
            mesh_from_cadquery(_sight_line_mesh(r), "cover_sight_line", tolerance=0.00012),
            origin=Origin(rpy=open_rpy),
            material=mats["mark"],
            name="sight_line", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    elif r.cover_style == "sight_wire_lid":
        cover.visual(
            mesh_from_cadquery(_sight_frame_mesh(r), "compass_sight_frame", tolerance=0.00022),
            origin=Origin(rpy=open_rpy),
            material=cover_mat,
            name="sight_frame", material_class_id="metal.brushed_silver",
        )
        cover.visual(
            mesh_from_cadquery(_sight_wire_mesh(r), "compass_sight_wire", tolerance=0.00014),
            origin=Origin(rpy=open_rpy),
            material=mats["hardware"],
            name="sight_wire", material_class_id="metal.chrome_polished",
        )
        cover.visual(
            mesh_from_cadquery(_sight_dot_mesh(r), "compass_sight_dot", tolerance=0.00014),
            origin=Origin(rpy=open_rpy),
            material=mats["luminous"],
            name="sight_dot", material_class_id="tech.emissive_surface",
        )
    elif r.cover_style == "square_flat_lid":
        cover.visual(
            mesh_from_cadquery(_square_lid_mesh(r), "field_cover_plate", tolerance=0.00025),
            origin=Origin(rpy=open_rpy),
            material=cover_mat,
            name="cover_plate", material_class_id="metal.brushed_silver",
        )
    else:  # flat_clear_lid
        cover.visual(
            mesh_from_cadquery(_clear_disc_mesh(r), "compass_clear_cover", tolerance=0.00025),
            origin=Origin(rpy=open_rpy),
            material=mats["glass"],
            name="cover_disc", material_class_id="glass.clear_transparent",
        )
    cover.visual(
        Cylinder(radius=0.0030, length=r.cover_knuckle_len),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=cover_mat,
        name="cover_knuckle", material_class_id="metal.brushed_silver",
    )
    model.articulation(
        "case_to_cover",
        ArticulationType.REVOLUTE,
        parent=case,
        child=cover,
        origin=Origin(xyz=(0.0, r.hinge_y, r.hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=1.0, velocity=3.0, lower=-r.open_rad, upper=math.radians(8.0)
        ),
    )
    return cover


def _emit_hanging_ring(model: ArticulatedObject, case, r: ResolvedPictureX0611CompassConfig, mats):
    """Swinging carry ring on the front retaining pin (origin L311-L373).

    Captured-pin joint (ring eye around the pin, 0.3 mm radial clearance):
    Rule 2 grandfather — no flat mating faces exist; capture is asserted in
    run_tests via expect_within at swung poses."""
    ring = model.part("hanging_ring")
    ring.visual(
        mesh_from_cadquery(_hanging_ring_mesh(r.s), "compass_hanging_ring", tolerance=0.00016),
        material=mats["hardware"],
        name="ring_loop", material_class_id="metal.chrome_polished",
    )
    model.articulation(
        "case_to_ring",
        ArticulationType.REVOLUTE,
        parent=case,
        child=ring,
        origin=Origin(xyz=(0.0, r.ring_pin_y, r.ring_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=0.15, velocity=5.0, lower=math.radians(-75.0), upper=math.radians(75.0)
        ),
    )
    return ring


# ---------------------------------------------------------------------------
# build + tests
# ---------------------------------------------------------------------------


def build_picturex_0611_compass(
    config: PictureX0611CompassConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or PictureX0611CompassConfig())
    model = ArticulatedObject(
        name="pictureX_0611_compass",
        meta={
            "template_slug": "pictureX_0611_compass",
            "source_subcategory": "pictureX/0611/compass",
            "classification_note": "magnetic direction compass (not a drawing compass)",
            "slot_choices": [list(t) for t in slot_choices_for_config(r)],
        },
    )
    mats = _materials(model, r)
    case = _emit_case(model, r, mats)
    _emit_bezel(model, case, r, mats)
    _emit_indicator(model, case, r, mats)
    _emit_cover(model, case, r, mats)
    if r.has_ring:
        _emit_hanging_ring(model, case, r, mats)
    return model


def build_seeded_picturex_0611_compass(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_compass(config_from_seed(seed), assets=assets)


def run_picturex_0611_compass_tests(
    object_model: ArticulatedObject,
    config: PictureX0611CompassConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    case = object_model.get_part("case")
    bezel = object_model.get_part("bezel")
    indicator = object_model.get_part(r.indicator_part)
    cover = object_model.get_part("cover")
    cover_joint = object_model.get_articulation("case_to_cover")
    indicator_joint = object_model.get_articulation("case_to_indicator")
    bezel_joint = object_model.get_articulation("case_to_bezel")

    # ---- joint structure per resolved config ----
    expected_joints = {"case_to_bezel", "case_to_indicator", "case_to_cover"}
    if r.has_ring:
        expected_joints.add("case_to_ring")
    actual_joints = {j.name for j in object_model.articulations}
    ctx.check(
        "all moving compass parts have independent revolute joints",
        actual_joints == expected_joints
        and all(
            j.articulation_type == ArticulationType.REVOLUTE
            for j in object_model.articulations
        ),
        details=f"expected={sorted(expected_joints)}, actual={sorted(actual_joints)}",
    )
    ctx.check(
        "single connected case-rooted hierarchy",
        len(object_model.root_parts()) == 1
        and object_model.root_parts()[0].name == "case"
        and all(
            (j.parent if isinstance(j.parent, str) else j.parent.name) == "case"
            for j in object_model.articulations
        ),
        details=f"roots={[p.name for p in object_model.root_parts()]}",
    )
    expected_geometry = {
        "case_to_bezel": ((0.0, 0.0, 1.0), -math.pi, math.pi),
        "case_to_indicator": ((0.0, 0.0, 1.0), -math.pi, math.pi),
        "case_to_cover": ((-1.0, 0.0, 0.0), -r.open_rad, math.radians(8.0)),
    }
    if r.has_ring:
        expected_geometry["case_to_ring"] = (
            (0.0, 0.0, 1.0),
            math.radians(-75.0),
            math.radians(75.0),
        )
    for joint_name, (axis, lo, hi) in expected_geometry.items():
        joint = object_model.get_articulation(joint_name)
        lim = joint.motion_limits
        ctx.check(
            f"{joint_name} axis and travel",
            joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(joint.axis) == axis
            and lim is not None
            and math.isclose(lim.lower, lo, abs_tol=1e-7)
            and math.isclose(lim.upper, hi, abs_tol=1e-7),
            details=f"axis={joint.axis}, limits={lim}",
        )

    # ---- category identity: readable dial + free magnetic indicator ----
    if r.indicator_style == "full_dial_card":
        card_ticks = {v.name for v in indicator.visuals if v.name.startswith("card_tick_")}
        ctx.check(
            "rotating compass card carries graduation ticks and cardinals",
            len(card_ticks) == r.dial_tick_count
            and {"cardinal_n", "cardinal_e", "cardinal_s", "cardinal_w"}.issubset(
                {v.name for v in indicator.visuals}
            ),
            details=f"tick_count={len(card_ticks)}",
        )
    else:
        case_ticks = {v.name for v in case.visuals if v.name.startswith("dial_tick_")}
        ctx.check(
            "case dial carries graduation ticks and cardinals",
            len(case_ticks) == r.dial_tick_count
            and {"cardinal_n", "cardinal_e", "cardinal_s", "cardinal_w"}.issubset(
                {v.name for v in case.visuals}
            ),
            details=f"tick_count={len(case_ticks)}",
        )

    # ---- module-specific construction ----
    required_visuals: dict[str, set[str]] = {
        # glass_lens only on non-liquid seeds: the liquid capsule dome is itself
        # the transparent window (resolve_config "Sealed-capsule window
        # resolution"), so the identity guard below requires one window OR the
        # other, never a stacked pair.
        "bezel": {"bezel_ring", "bezel_grip_0"} | ({"glass_lens"} if r.has_glass_lens else set()),
        "cover": {r.lid_visual, "cover_knuckle"},
        "case": {"dial_face", "pivot_pin", "hinge_bridge", "hinge_pin", r.case_top_visual},
    }
    # Category identity: a compass always reads its dial through exactly one
    # transparent window -- the flat bezel lens, or the sealed capsule dome.
    bezel_visuals = {v.name for v in bezel.visuals}
    case_visuals_now = {v.name for v in case.visuals}
    window_count = int("glass_lens" in bezel_visuals) + int("capsule_bowl" in case_visuals_now)
    ctx.check(
        "exactly one transparent dial window (flat lens xor sealed capsule dome)",
        window_count == 1,
        details=(
            f"glass_lens={'glass_lens' in bezel_visuals} "
            f"capsule_bowl={'capsule_bowl' in case_visuals_now} "
            f"indicator_style={r.indicator_style}"
        ),
    )
    if r.indicator_style == "full_dial_card":
        required_visuals["dial_card"] = {"card_disk", "card_hub", "north_triangle"}
    else:
        required_visuals["magnetic_needle"] = {"north_pointer", "south_pointer", "needle_hub"}
    if r.indicator_style == "liquid_damped_needle":
        required_visuals["magnetic_needle"].add("damping_vane")
        required_visuals["case"].update({"capsule_bowl", "fluid_fill", "capsule_gasket"})
    if r.cover_style == "mirror_sighting_lid":
        required_visuals["cover"].update({"mirror_face", "sight_line"})
    if r.cover_style == "sight_wire_lid":
        required_visuals["cover"].update({"sight_wire", "sight_dot"})
    if r.case_style == "wrist_cradle_case":
        required_visuals["case"].update({"wrist_cradle", "strap_band_left", "strap_band_right"})
    if r.case_style == "rectangular_baseplate":
        required_visuals["case"].update({"base_plate", "capsule_floor", "direction_arrow_shaft"})
    if r.case_style == "square_lensatic_case":
        required_visuals["case"].update({f"corner_screw_{i}" for i in range(4)})
    if r.has_ring:
        required_visuals["hanging_ring"] = {"ring_loop"}
        required_visuals["case"].update({"ring_lug", "ring_pin"})
    for part_name, expected in required_visuals.items():
        authored = {v.name for v in object_model.get_part(part_name).visuals}
        ctx.check(
            f"{part_name} includes module-specific construction",
            expected.issubset(authored),
            details=f"expected={sorted(expected)}, authored={sorted(authored)}",
        )

    # ---- case-form assertions (③ slot realized) ----
    if r.case_style == "rectangular_baseplate":
        plate_aabb = ctx.part_element_world_aabb(case, elem="base_plate")
        if plate_aabb is not None:
            dx = plate_aabb[1][0] - plate_aabb[0][0]
            dy = plate_aabb[1][1] - plate_aabb[0][1]
            ctx.check(
                "baseplate is rectangular (length >> width)",
                dx > dy * 1.5,
                details=f"dx={dx:.4f}, dy={dy:.4f}",
            )
    elif r.case_style == "square_lensatic_case":
        shell_aabb = ctx.part_element_world_aabb(case, elem="case_shell")
        if shell_aabb is not None:
            dx = shell_aabb[1][0] - shell_aabb[0][0]
            dy = shell_aabb[1][1] - shell_aabb[0][1]
            ctx.check(
                "field case shell is square",
                abs(dx - dy) < 0.005,
                details=f"dx={dx:.4f}, dy={dy:.4f}",
            )
    elif r.case_style == "wrist_cradle_case":
        cradle_aabb = ctx.part_element_world_aabb(case, elem="wrist_cradle")
        case_aabb = ctx.part_element_world_aabb(case, elem="case_shell")
        ctx.check(
            "wrist cradle sits below the case body",
            cradle_aabb is not None
            and case_aabb is not None
            and (cradle_aabb[0][2] + cradle_aabb[1][2]) / 2.0
            < (case_aabb[0][2] + case_aabb[1][2]) / 2.0 - 0.003,
            details=f"cradle_aabb={cradle_aabb}, case_aabb={case_aabb}",
        )

    # ---- seats / capture relations ----
    ctx.expect_gap(
        bezel,
        case,
        axis="z",
        positive_elem="bezel_ring",
        negative_elem=r.case_top_visual,
        min_gap=-0.0005,
        max_gap=0.002,
        name="bezel seats on the case top face",
    )
    hub_visual = "card_hub" if r.indicator_style == "full_dial_card" else "needle_hub"
    if r.has_glass_lens:
        ctx.expect_within(
            indicator,
            bezel,
            axes="xy",
            inner_elem=hub_visual,
            outer_elem="glass_lens",
            margin=0.0,
            name="indicator pivot remains centered under the lens",
        )
    else:
        # Liquid seeds: the sealed capsule dome is the window, so the pivot is
        # centered under the dome instead of a flat lens.
        ctx.expect_within(
            indicator,
            case,
            axes="xy",
            inner_elem=hub_visual,
            outer_elem="capsule_bowl",
            margin=0.0,
            name="indicator pivot remains centered under the sealed capsule dome",
        )
    ctx.expect_contact(
        case,
        indicator,
        elem_a="pivot_pin",
        elem_b=hub_visual,
        contact_tol=0.001,
        name="indicator hub seats on the pivot pin top",
    )
    ctx.allow_overlap(
        case,
        cover,
        elem_a="hinge_pin",
        elem_b="cover_knuckle",
        reason="The steel hinge pin is intentionally captured inside the cover knuckle.",
    )
    ctx.expect_contact(
        case,
        cover,
        elem_a="hinge_pin",
        elem_b="cover_knuckle",
        contact_tol=0.0005,
        name="cover knuckle is captured by the hinge pin",
    )

    if r.indicator_style == "liquid_damped_needle":
        for elem in ("damping_vane", "north_pointer", "south_pointer", "needle_hub",
                     "luminous_north_tip"):
            ctx.allow_overlap(
                case,
                indicator,
                elem_a="fluid_fill",
                elem_b=elem,
                reason="The needle assembly is intentionally immersed in the sealed damping fluid.",
            )
        # Spec Reject #8: the dome must NOT punch through the bezel window.
        # It is resolved geometrically (the dome IS the window and rises through
        # the bezel bore), so there is no capsule_bowl x glass_lens allowance to
        # declare -- assert the real radial clearance instead of waiving it.
        ctx.check(
            "sealed capsule dome clears the bezel bore (spec Reject #8)",
            not r.has_glass_lens
            and r.bowl_r < r.bez_seat_in
            and r.bowl_r < r.bez_ring_in,
            details=(
                f"bowl_r={r.bowl_r:.5f} bez_seat_in={r.bez_seat_in:.5f} "
                f"bez_ring_in={r.bez_ring_in:.5f} has_glass_lens={r.has_glass_lens}"
            ),
        )
        ctx.expect_within(
            case,
            bezel,
            axes="xy",
            inner_elem="capsule_bowl",
            outer_elem="bezel_ring",
            margin=0.0,
            name="sealed capsule dome rises through the bezel ring bore",
        )
        ctx.expect_overlap(
            case,
            indicator,
            axes="xy",
            elem_a="fluid_fill",
            elem_b="damping_vane",
            min_overlap=0.004,
            name="damping vane rides inside the fluid fill footprint",
        )
        ctx.expect_within(
            indicator,
            case,
            axes="xy",
            inner_elem="damping_vane",
            outer_elem="capsule_bowl",
            margin=0.002,
            name="damping vane is contained within the sealed capsule",
        )

    # ---- Rule 5: full-travel sampled collision + targeted motion proofs ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    # indicator spins freely on the vertical axis
    ref_elem = "north_triangle" if r.indicator_style == "full_dial_card" else "north_pointer"
    rest_aabb = ctx.part_element_world_aabb(indicator, elem=ref_elem)
    with ctx.pose({indicator_joint: math.radians(90.0)}):
        rot_aabb = ctx.part_element_world_aabb(indicator, elem=ref_elem)
    ctx.check(
        "indicator rotates freely about the vertical pivot",
        rest_aabb is not None
        and rot_aabb is not None
        and (
            abs(rot_aabb[0][0] - rest_aabb[0][0]) > 0.002
            or abs(rot_aabb[0][1] - rest_aabb[0][1]) > 0.002
        ),
        details=f"rest={rest_aabb}, rotated={rot_aabb}",
    )

    # bezel ring rotates (grip displacement)
    grip_rest = ctx.part_element_world_aabb(bezel, elem="bezel_grip_0")
    with ctx.pose({bezel_joint: math.radians(45.0)}):
        grip_rot = ctx.part_element_world_aabb(bezel, elem="bezel_grip_0")
    ctx.check(
        "bezel rotates about the dial axis",
        grip_rest is not None
        and grip_rot is not None
        and (
            abs(grip_rot[0][0] - grip_rest[0][0]) > 0.002
            or abs(grip_rot[0][1] - grip_rest[0][1]) > 0.002
        ),
        details=f"rest={grip_rest}, rotated={grip_rot}",
    )

    # cover closes down over the dial
    open_aabb = ctx.part_world_aabb(cover)
    ctx.check(
        "reference pose keeps the lid open behind/above the dial",
        open_aabb is not None and open_aabb[1][2] > r.hinge_z + 0.02,
        details=f"open_cover_aabb={open_aabb}",
    )
    with ctx.pose({cover_joint: -r.open_rad}):
        closed_aabb = ctx.part_world_aabb(cover)
        open_cz = (open_aabb[0][2] + open_aabb[1][2]) / 2.0 if open_aabb else None
        closed_cz = (closed_aabb[0][2] + closed_aabb[1][2]) / 2.0 if closed_aabb else None
        ctx.check(
            "cover hinge swings the lid down over the case",
            closed_aabb is not None
            and open_cz is not None
            and closed_cz is not None
            and closed_cz < open_cz - 0.015,
            details=f"open={open_aabb}, closed={closed_aabb}",
        )
        ctx.expect_overlap(
            cover,
            case,
            axes="xy",
            elem_a=r.lid_visual,
            elem_b="dial_face",
            min_overlap=1.5 * r.dial_r,
            name="closed lid spans the compass dial",
        )

    # hanging ring stays captured while swinging
    if r.has_ring:
        ring = object_model.get_part("hanging_ring")
        ring_joint = object_model.get_articulation("case_to_ring")
        for angle, label in ((math.radians(-60.0), "ccw"), (math.radians(60.0), "cw")):
            with ctx.pose({ring_joint: angle}):
                ctx.expect_within(
                    case,
                    ring,
                    axes="xy",
                    inner_elem="ring_pin",
                    outer_elem="ring_loop",
                    margin=0.003,
                    name=f"hanging ring remains captured when swung {label}",
                )

    return ctx.report()


__all__ = [
    "CaseStyle",
    "IndicatorStyle",
    "CoverStyle",
    "PaletteStyle",
    "PictureX0611CompassConfig",
    "ResolvedPictureX0611CompassConfig",
    "build_picturex_0611_compass",
    "build_seeded_picturex_0611_compass",
    "config_from_seed",
    "resolve_config",
    "run_picturex_0611_compass_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "__modular__",
]
