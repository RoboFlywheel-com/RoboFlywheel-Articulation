# SPDX-License-Identifier: Apache-2.0

"""Handheld hinged garlic press (pictureX / 0611 / garlic_press).

Design-backed rebuild.  Authoring artifacts:

  * ``articraft_template_authoring/source_maps/pictureX_0611_garlic_press.md``
  * ``articraft_template_authoring/designs/pictureX_0611_garlic_press.json``
    (filled by ``scripts/design_fill/pictureX_0611_garlic_press.py``)

Frame convention
----------------
The pool's dominant layout (origins 003/004/005) is kept verbatim: the hinge pin
sits at the **nose**, the perforated chamber sits just behind it, and both hand
arms run away from the pin along **+X**.  ``+Z`` is up, the chamber mouth opens
``+Z``, and the lower arm's top face is the ``z = 0`` datum, so the chamber rim
is flush with it exactly as in 004 (``CHAMBER_RIM_Z`` == the handle top).

``z = 0``      lower arm top face and chamber rim
``z = -arm_t`` lower arm underside (lower grip pad hangs below it)
``z = pivot_z`` hinge axis, above the arm; the lever bar rides above the lugs

Every rotating member is authored in a **world-oriented** frame translated so its
joint point is the local origin.  Both sides of every ``mate_axes`` call then use
the same ``(axis, radial)`` basis, the solved ``Origin`` has zero rpy, and the
joint axis is a world direction, which keeps ``register_interface_mate`` honest
without any rotation bookkeeping.

Screen frame
------------
The one thing that genuinely differs across the seven chambers is *where the
perforated screen is*.  Five of them (004, round_cup_grid, 005, deep_oval_hopper,
006) pierce the **floor**; 001 pierces a **vertical circular end plate** across
the tool; 002 pierces the **front wall**.  Every chamber therefore publishes a
``_Screen`` (outer-surface origin, outward normal ``n``, tangents ``u``/``v``,
half extents and the hole field in ``(u, v)``), and the three screen-registered
accessories -- ``swing_cleaner``, ``sliding_ejector``, ``lift_out_insert`` --
are built once in that frame instead of seven times.

Deliberate deviations from the sources, and why
-----------------------------------------------
* ``ctx.allow_overlap`` is never called.  The pool leans on it heavily (001, 003,
  005, 006 and every fork), but it is blocked for Design-backed templates.  Each
  captured-pin fit is replaced by a real running clearance: shafts are
  ``r``, bores are ``r + bore_clearance`` (0.35 mm), so the members are carried by
  their joints on a fit that is inside the 1 mm support band and never overlaps.
* ``swing_cleaner`` is hinged on the **outside** of the screen.  Source 001/
  swing_cleaner_grid mount the strap inside the drum because 001's chamber is open
  at the rear; that mounting exists for exactly one of the seven chambers.  Mounted
  outside, the same comb registers with all seven screens.  An externally mounted
  module gets its footprint from ``_module_screen`` rather than from the raw
  screen: the two vertical screens are partly covered by the cast nose head
  (002's front wall) or cut away by the loading mouth (001's end plate), and the
  band's ``v`` runs down the tool so the hinge hardware hangs into free air.
* ``sliding_ejector`` keeps its plate wholly outside the screen and gets its travel
  from long cleaning pins that sit flush in the holes at rest.  The source lets the
  disc travel *into* the floor plate; here the plate would collide with the chamber.
* Lofts are ``ruled=True``.  A spline loft bulges outside its own section table and
  puts every downstream boolean on BSpline faces.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Mimic,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

Vec3 = tuple[float, float, float]

# --------------------------------------------------------------------------- #
# Domain
# --------------------------------------------------------------------------- #
Chamber = Literal[
    "round_cup",
    "ribbed_cup",
    "rect_trough",
    "oval_hopper",
    "taper_cup",
    "drum_face",
    "loft_hopper",
]
PlungerDrive = Literal[
    "rigid_pad",
    "stud_plate",
    "self_leveling",
    "cam_follower",
    "toggle_link",
]
Accessory = Literal[
    "hang_loop",
    "swing_cleaner",
    "sliding_ejector",
    "storage_latch",
    "lift_out_insert",
    "flip_basket",
]
ArmProfile = Literal["flat_bar", "round_tube", "lofted_ellipse"]
PaletteStyle = Literal[
    "cast_aluminium",
    "brushed_stainless",
    "polished_steel",
    "black_grip_alloy",
    "dark_anodised",
]

CHAMBERS: tuple[Chamber, ...] = (
    "round_cup",
    "ribbed_cup",
    "rect_trough",
    "oval_hopper",
    "taper_cup",
    "drum_face",
    "loft_hopper",
)
PLUNGER_DRIVES: tuple[PlungerDrive, ...] = (
    "rigid_pad",
    "stud_plate",
    "self_leveling",
    "cam_follower",
    "toggle_link",
)
ACCESSORIES: tuple[Accessory, ...] = (
    "hang_loop",
    "swing_cleaner",
    "sliding_ejector",
    "storage_latch",
    "lift_out_insert",
    "flip_basket",
)
ARM_PROFILES: tuple[ArmProfile, ...] = ("flat_bar", "round_tube", "lofted_ellipse")
SCREEN_ROWS: tuple[int, ...] = (3, 4, 5, 6, 7)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "cast_aluminium",
    "brushed_stainless",
    "polished_steel",
    "black_grip_alloy",
    "dark_anodised",
)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "chamber",
            CHAMBERS,
            role="source-backed perforated pressing chamber and its nose casting",
        ),
        component_slot(
            "plunger_drive",
            PLUNGER_DRIVES,
            role="source-backed plunger body and its drive from the lever arm",
        ),
        component_slot(
            "accessory",
            ACCESSORIES,
            role="source-backed cleaning, ejection or retention module",
        ),
        component_slot(
            "arm_profile",
            ARM_PROFILES,
            role="source-backed hand arm cross-section, tip and grip treatment",
        ),
        multiplicity_slot("screen_rows", SCREEN_ROWS, item_slot="chamber"),
    )
)

# Palette keys: cast body, screen / perforated plate, bright hardware (pin, rails,
# rivets), polymer grip, and an accent for the release tab / cleaning module.
# Albedo ceiling: the shared preview/gallery rig keys at 45 * dist**2 with
# view_transform "Standard" and no tonemap, so a face turned toward the key clips
# to pure white above roughly 0.6. The two arms are this category's largest flat
# surfaces, so a bright `body` erases the whole tool -- four of these five styles
# used to render as a featureless white slab. `body` and `screen` are held well
# under the ceiling; `hardware` and `accent` stay brighter because they only ever
# appear on small or curved parts (pins, bosses, studs) that never present a broad
# flat face. Relative lightness between the styles is preserved.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "cast_aluminium": {
        "body": (0.50, 0.51, 0.53, 1.0),
        "screen": (0.38, 0.40, 0.42, 1.0),
        "hardware": (0.57, 0.59, 0.60, 1.0),
        "grip": (0.055, 0.058, 0.062, 1.0),
        "accent": (0.62, 0.18, 0.13, 1.0),
    },
    "brushed_stainless": {
        "body": (0.46, 0.48, 0.50, 1.0),
        "screen": (0.32, 0.34, 0.36, 1.0),
        "hardware": (0.55, 0.57, 0.59, 1.0),
        "grip": (0.08, 0.09, 0.10, 1.0),
        "accent": (0.14, 0.36, 0.58, 1.0),
    },
    "polished_steel": {
        "body": (0.54, 0.56, 0.58, 1.0),
        "screen": (0.36, 0.38, 0.40, 1.0),
        "hardware": (0.60, 0.61, 0.62, 1.0),
        "grip": (0.14, 0.15, 0.17, 1.0),
        "accent": (0.66, 0.55, 0.10, 1.0),
    },
    "black_grip_alloy": {
        "body": (0.40, 0.42, 0.44, 1.0),
        "screen": (0.24, 0.25, 0.27, 1.0),
        "hardware": (0.54, 0.56, 0.58, 1.0),
        "grip": (0.030, 0.032, 0.036, 1.0),
        "accent": (0.50, 0.50, 0.52, 1.0),
    },
    "dark_anodised": {
        "body": (0.26, 0.27, 0.30, 1.0),
        "screen": (0.17, 0.18, 0.20, 1.0),
        "hardware": (0.52, 0.54, 0.56, 1.0),
        "grip": (0.10, 0.11, 0.12, 1.0),
        "accent": (0.68, 0.38, 0.09, 1.0),
    },
}

_SEPARATE_PLUNGER = frozenset({"self_leveling", "cam_follower", "toggle_link"})
_SCREEN_ACCESSORIES = frozenset({"swing_cleaner", "sliding_ejector", "lift_out_insert"})
# The two that hang a body on the *outside* of the screen; lift_out_insert lives
# inside the cavity and is not affected by what the frame puts over the screen.
_EXTERNAL_MODULES = frozenset({"swing_cleaner", "sliding_ejector"})

# Every running fit in this template is a sub-millimetre clearance, so the
# tessellation sagitta has to stay well under it.
_MESH_TOL = 0.00035
_ANG_TOL = 0.35
_BORE_CLEARANCE = 0.00035
_LUG_T = 0.0038
_LUG_X0 = -0.0045
_LUG_X1 = 0.0155
_MAX_HOLES = 56
# A screen is only a screen if it carries a real field; the authored category
# anchor asks for at least this many holes.
_MIN_SCREEN_HOLES = 10
# Solid material two neighbouring lift-out-insert holes must leave between them.
# The source drills 0.85 mm holes on a 3.5 mm pitch (1.8 mm of ligament); this
# plate is a fraction of that size, so it keeps a proportionate 0.6 mm.
_INSERT_LIGAMENT = 0.0006


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Config:
    chamber: Chamber = "round_cup"
    plunger_drive: PlungerDrive = "rigid_pad"
    accessory: Accessory = "hang_loop"
    arm_profile: ArmProfile = "flat_bar"
    screen_rows: int = 5
    palette_style: PaletteStyle = "cast_aluminium"

    # arm_profile / flat_bar -- shared frame geometry
    handle_len_m: float = 0.130
    arm_thickness_m: float = 0.0085
    arm_half_width_m: float = 0.0100
    arm_taper_ratio: float = 0.82
    pivot_rise_m: float = 0.0105
    lever_lift_m: float = 0.0075
    lug_inner_y_m: float = 0.0072
    pin_radius_m: float = 0.0029
    open_rad: float = 1.05
    grip_len_ratio: float = 0.56
    grip_pad_t_m: float = 0.0055
    # arm_profile / round_tube
    tube_radius_m: float = 0.0060
    neck_len_m: float = 0.0150
    # arm_profile / lofted_ellipse
    palm_swell_ratio: float = 1.22
    slot_grip_w_m: float = 0.0175

    # chamber / round_cup -- shared chamber geometry
    chamber_offset_m: float = 0.0380
    chamber_span_m: float = 0.0150
    chamber_depth_m: float = 0.0230
    chamber_wall_m: float = 0.0028
    screen_thickness_m: float = 0.0030
    hole_radius_m: float = 0.00110
    side_hole_count: int = 8
    collar_height_m: float = 0.0060
    # chamber / ribbed_cup
    rib_count: int = 4
    rib_reach_m: float = 0.0050
    flange_proud_m: float = 0.0024
    # chamber / rect_trough
    trough_aspect: float = 1.80
    trough_fillet_m: float = 0.0028
    # chamber / oval_hopper
    oval_aspect: float = 1.70
    hopper_extra_depth_m: float = 0.0070
    # chamber / taper_cup
    taper_ratio: float = 1.16
    lip_proud_m: float = 0.0024
    # chamber / drum_face
    drum_sink_ratio: float = 0.34
    face_thickness_m: float = 0.0030
    # chamber / loft_hopper
    hopper_taper_ratio: float = 0.84
    hopper_front_wall_m: float = 0.0034

    # plunger_drive / rigid_pad -- shared plunger geometry
    plunger_fill_ratio: float = 0.82
    plunger_thickness_m: float = 0.0080
    engage_depth_m: float = 0.0035
    plunger_stem_w_m: float = 0.0115
    # plunger_drive / stud_plate
    stud_rows: int = 4
    stud_radius_m: float = 0.00120
    stud_len_m: float = 0.00160
    # plunger_drive / self_leveling
    tilt_rad: float = 0.22
    hub_radius_m: float = 0.0052
    puck_taper_ratio: float = 0.94
    # plunger_drive / cam_follower
    cam_radius_m: float = 0.0085
    roller_radius_m: float = 0.0036
    cam_offset_y_m: float = 0.0160
    # plunger_drive / toggle_link
    rocker_span_m: float = 0.0205
    link_len_m: float = 0.0150
    rocker_mult: float = 0.32
    rocker_lift_m: float = 0.0125

    # accessory / hang_loop
    loop_radius_m: float = 0.0078
    loop_tube_m: float = 0.0022
    # accessory / swing_cleaner
    cleaner_pin_len_m: float = 0.0045
    cleaner_plate_t_m: float = 0.0026
    cleaner_open_rad: float = 1.10
    # accessory / sliding_ejector
    ejector_travel_m: float = 0.0055
    ejector_pin_ratio: float = 0.72
    rail_span_ratio: float = 0.66
    # accessory / storage_latch
    latch_arm_len_m: float = 0.0165
    latch_release_rad: float = 1.05
    capture_pin_r_m: float = 0.00165
    # accessory / lift_out_insert
    insert_thickness_m: float = 0.0021
    insert_fill_ratio: float = 0.88
    insert_lift_rad: float = 0.90
    # accessory / flip_basket
    flip_rad: float = 0.95
    cradle_plate_t_m: float = 0.0034

    name: str = "pictureX_0611_garlic_press"


def _clamp(value: float, low: float, high: float) -> float:
    return float(min(max(float(value), low), high))


def _pick(value, allowed):
    return value if value in allowed else allowed[0]


@dataclass(frozen=True)
class _Screen:
    """Outer face of the perforated screen, in world coordinates."""

    origin: Vec3
    normal: Vec3  # outward, i.e. the direction the extruded garlic leaves
    u: Vec3
    v: Vec3
    hu: float
    hv: float
    thickness: float
    holes: tuple[tuple[float, float], ...]
    hole_r: float
    clip: str  # "circle" | "ellipse" | "rect"


@dataclass(frozen=True)
class _ChamberSpec:
    cx: float
    liner_hv: float
    hx: float
    hy: float
    rim_z: float
    bottom_z: float
    top_z: float
    cavity_floor_z: float
    mouth_hx: float
    mouth_hy: float
    mouth_kind: str  # "circle" | "ellipse" | "rect"
    screen: _Screen


@dataclass(frozen=True)
class ResolvedConfig:
    chamber: Chamber
    plunger_drive: PlungerDrive
    accessory: Accessory
    arm_profile: ArmProfile
    screen_rows: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]

    handle_len_m: float
    arm_thickness_m: float
    arm_half_width_m: float
    arm_taper_ratio: float
    pivot_rise_m: float
    lever_lift_m: float
    lug_inner_y_m: float
    pin_radius_m: float
    open_rad: float
    grip_len_ratio: float
    grip_pad_t_m: float
    tube_radius_m: float
    neck_len_m: float
    palm_swell_ratio: float
    slot_grip_w_m: float

    chamber_offset_m: float
    chamber_span_m: float
    chamber_depth_m: float
    chamber_wall_m: float
    screen_thickness_m: float
    hole_radius_m: float
    side_hole_count: int
    collar_height_m: float
    rib_count: int
    rib_reach_m: float
    flange_proud_m: float
    trough_aspect: float
    trough_fillet_m: float
    oval_aspect: float
    hopper_extra_depth_m: float
    taper_ratio: float
    lip_proud_m: float
    drum_sink_ratio: float
    face_thickness_m: float
    hopper_taper_ratio: float
    hopper_front_wall_m: float

    plunger_fill_ratio: float
    plunger_thickness_m: float
    engage_depth_m: float
    plunger_stem_w_m: float
    stud_rows: int
    stud_radius_m: float
    stud_len_m: float
    tilt_rad: float
    hub_radius_m: float
    puck_taper_ratio: float
    cam_radius_m: float
    roller_radius_m: float
    cam_offset_y_m: float
    rocker_span_m: float
    link_len_m: float
    rocker_mult: float
    rocker_lift_m: float

    loop_radius_m: float
    loop_tube_m: float
    cleaner_pin_len_m: float
    cleaner_plate_t_m: float
    cleaner_open_rad: float
    ejector_travel_m: float
    ejector_pin_ratio: float
    rail_span_ratio: float
    latch_arm_len_m: float
    latch_release_rad: float
    capture_pin_r_m: float
    insert_thickness_m: float
    insert_fill_ratio: float
    insert_lift_rad: float
    flip_rad: float
    cradle_plate_t_m: float

    # derived -- frame stations
    arm_t: float
    arm_hy: float
    pivot_z: float
    pin_r: float
    pin_cap_r: float
    knuckle_r: float
    lug_in_y: float
    lug_out_y: float
    lug_top_z: float
    lever_lift: float
    lever_t: float
    lever_bar_z0: float
    lever_bar_z1: float
    cx: float
    tail_x: float
    lever_tail_x: float
    grip_len: float
    separate_plunger: bool
    flip_chamber: bool

    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x0611_6741_524C)
    return Config(
        chamber=choices["chamber"],
        plunger_drive=choices["plunger_drive"],
        accessory=choices["accessory"],
        arm_profile=choices["arm_profile"],
        screen_rows=int(choices["screen_rows"]),
        palette_style=rng.choice(PALETTE_STYLES),
        handle_len_m=round(rng.uniform(0.108, 0.156), 5),
        arm_thickness_m=round(rng.uniform(0.0062, 0.0110), 5),
        arm_half_width_m=round(rng.uniform(0.0082, 0.0125), 5),
        arm_taper_ratio=round(rng.uniform(0.66, 1.00), 4),
        pivot_rise_m=round(rng.uniform(0.0075, 0.0155), 5),
        lever_lift_m=round(rng.uniform(0.0045, 0.0125), 5),
        lug_inner_y_m=round(rng.uniform(0.0058, 0.0092), 5),
        pin_radius_m=round(rng.uniform(0.0023, 0.0037), 5),
        open_rad=round(rng.uniform(0.90, 1.42), 4),
        grip_len_ratio=round(rng.uniform(0.42, 0.70), 4),
        grip_pad_t_m=round(rng.uniform(0.0040, 0.0078), 5),
        tube_radius_m=round(rng.uniform(0.0050, 0.0076), 5),
        neck_len_m=round(rng.uniform(0.0100, 0.0225), 5),
        palm_swell_ratio=round(rng.uniform(1.06, 1.42), 4),
        slot_grip_w_m=round(rng.uniform(0.0140, 0.0215), 5),
        chamber_offset_m=round(rng.uniform(0.0320, 0.0520), 5),
        chamber_span_m=round(rng.uniform(0.0122, 0.0180), 5),
        chamber_depth_m=round(rng.uniform(0.0185, 0.0315), 5),
        chamber_wall_m=round(rng.uniform(0.0021, 0.0037), 5),
        screen_thickness_m=round(rng.uniform(0.0023, 0.0041), 5),
        hole_radius_m=round(rng.uniform(0.00088, 0.00135), 6),
        side_hole_count=rng.choice((6, 8, 10)),
        collar_height_m=round(rng.uniform(0.0042, 0.0088), 5),
        rib_count=rng.choice((3, 4, 6)),
        rib_reach_m=round(rng.uniform(0.0035, 0.0070), 5),
        flange_proud_m=round(rng.uniform(0.0016, 0.0034), 5),
        trough_aspect=round(rng.uniform(1.40, 2.35), 4),
        trough_fillet_m=round(rng.uniform(0.0020, 0.0040), 5),
        oval_aspect=round(rng.uniform(1.35, 2.10), 4),
        hopper_extra_depth_m=round(rng.uniform(0.0030, 0.0085), 5),
        taper_ratio=round(rng.uniform(1.06, 1.26), 4),
        lip_proud_m=round(rng.uniform(0.0015, 0.0035), 5),
        drum_sink_ratio=round(rng.uniform(0.22, 0.48), 4),
        face_thickness_m=round(rng.uniform(0.0022, 0.0040), 5),
        hopper_taper_ratio=round(rng.uniform(0.70, 0.96), 4),
        hopper_front_wall_m=round(rng.uniform(0.0025, 0.0046), 5),
        plunger_fill_ratio=round(rng.uniform(0.70, 0.90), 4),
        plunger_thickness_m=round(rng.uniform(0.0050, 0.0120), 5),
        engage_depth_m=round(rng.uniform(0.0016, 0.0062), 5),
        plunger_stem_w_m=round(rng.uniform(0.0080, 0.0160), 5),
        stud_rows=rng.choice((3, 4, 5)),
        stud_radius_m=round(rng.uniform(0.00090, 0.00160), 6),
        stud_len_m=round(rng.uniform(0.00100, 0.00220), 6),
        tilt_rad=round(rng.uniform(0.12, 0.30), 4),
        hub_radius_m=round(rng.uniform(0.0040, 0.0066), 5),
        puck_taper_ratio=round(rng.uniform(0.86, 1.00), 4),
        cam_radius_m=round(rng.uniform(0.0060, 0.0110), 5),
        roller_radius_m=round(rng.uniform(0.0028, 0.0046), 5),
        cam_offset_y_m=round(rng.uniform(0.0130, 0.0195), 5),
        rocker_span_m=round(rng.uniform(0.0160, 0.0265), 5),
        link_len_m=round(rng.uniform(0.0100, 0.0205), 5),
        rocker_mult=round(rng.uniform(0.20, 0.46), 4),
        rocker_lift_m=round(rng.uniform(0.0080, 0.0185), 5),
        loop_radius_m=round(rng.uniform(0.0055, 0.0102), 5),
        loop_tube_m=round(rng.uniform(0.0016, 0.0029), 5),
        cleaner_pin_len_m=round(rng.uniform(0.0030, 0.0062), 5),
        cleaner_plate_t_m=round(rng.uniform(0.0020, 0.0036), 5),
        cleaner_open_rad=round(rng.uniform(0.80, 1.40), 4),
        ejector_travel_m=round(rng.uniform(0.0035, 0.0082), 5),
        ejector_pin_ratio=round(rng.uniform(0.60, 0.85), 4),
        rail_span_ratio=round(rng.uniform(0.48, 0.80), 4),
        latch_arm_len_m=round(rng.uniform(0.0120, 0.0225), 5),
        latch_release_rad=round(rng.uniform(0.78, 1.35), 4),
        capture_pin_r_m=round(rng.uniform(0.0012, 0.0022), 5),
        insert_thickness_m=round(rng.uniform(0.0016, 0.0029), 5),
        insert_fill_ratio=round(rng.uniform(0.78, 0.94), 4),
        insert_lift_rad=round(rng.uniform(0.45, 1.25), 4),
        flip_rad=round(rng.uniform(0.55, 1.28), 4),
        cradle_plate_t_m=round(rng.uniform(0.0025, 0.0046), 5),
        name=f"seeded_garlic_press_{seed}",
    )


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()

    chamber = _pick(cfg.chamber, CHAMBERS)
    plunger_drive = _pick(cfg.plunger_drive, PLUNGER_DRIVES)
    accessory = _pick(cfg.accessory, ACCESSORIES)
    arm_profile = _pick(cfg.arm_profile, ARM_PROFILES)
    screen_rows = int(_pick(int(cfg.screen_rows), SCREEN_ROWS))
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    handle_len = _clamp(cfg.handle_len_m, 0.108, 0.156)
    arm_taper = _clamp(cfg.arm_taper_ratio, 0.66, 1.00)
    pivot_rise = _clamp(cfg.pivot_rise_m, 0.0075, 0.0155)
    lug_in_y = _clamp(cfg.lug_inner_y_m, 0.0058, 0.0092)
    pin_r = _clamp(cfg.pin_radius_m, 0.0023, 0.0037)
    grip_len_ratio = _clamp(cfg.grip_len_ratio, 0.42, 0.70)
    grip_pad_t = _clamp(cfg.grip_pad_t_m, 0.0040, 0.0078)
    tube_r = _clamp(cfg.tube_radius_m, 0.0050, 0.0076)
    neck_len = _clamp(cfg.neck_len_m, 0.0100, 0.0225)
    palm_swell = _clamp(cfg.palm_swell_ratio, 1.06, 1.42)
    slot_grip_w = _clamp(cfg.slot_grip_w_m, 0.0140, 0.0215)

    arm_hy = _clamp(cfg.arm_half_width_m, 0.0082, 0.0125)
    arm_t = _clamp(cfg.arm_thickness_m, 0.0062, 0.0110)
    if arm_profile == "round_tube":
        arm_t = 2.0 * tube_r
        arm_hy = max(arm_hy, tube_r + 0.0004)
    # The lever neck has to pass between the lugs, so the lug gap follows the arm.
    lug_in_y = max(lug_in_y, pin_r + 0.0030)
    pin_cap_r = pin_r + 0.0018
    knuckle_r = pin_r + 0.0038
    lug_out_y = lug_in_y + _LUG_T
    pivot_z = max(pivot_rise, knuckle_r + 0.0016)
    lug_top_z = pivot_z + pin_cap_r + 0.0022
    lever_lift = max(_clamp(cfg.lever_lift_m, 0.0045, 0.0125), pin_cap_r + 0.0038)
    lever_t = max(arm_t * 0.85, 0.0050)

    chamber_span = _clamp(cfg.chamber_span_m, 0.0122, 0.0180)
    chamber_wall = _clamp(cfg.chamber_wall_m, 0.0021, 0.0037)
    screen_t = _clamp(cfg.screen_thickness_m, 0.0023, 0.0041)
    depth = _clamp(cfg.chamber_depth_m, 0.0185, 0.0315)
    depth = max(depth, screen_t + 0.0105)
    if chamber == "loft_hopper" and accessory in _EXTERNAL_MODULES:
        # 002's screen is the front wall, and the cast nose head runs straight
        # across it down to z = -arm_t.  A module hung on that wall lives in the
        # band between the head's underside and the hopper floor, so the hopper
        # has to be deep enough to leave one.  arm_t tops out at 15.2 mm
        # (round_tube), so this floor tops out at 27.7 mm against a 31.5 mm
        # ceiling: the depth range never collapses.
        depth = min(max(depth, arm_t + 0.0125), 0.0315)
    hole_r = _clamp(cfg.hole_radius_m, 0.00088, 0.00135)

    trough_aspect = _clamp(cfg.trough_aspect, 1.40, 2.35)
    oval_aspect = _clamp(cfg.oval_aspect, 1.35, 2.10)
    # The widest chamber in X decides how far back the pivot lugs must sit.
    if chamber == "rect_trough":
        span_x = chamber_span * trough_aspect
    elif chamber == "oval_hopper":
        span_x = chamber_span * oval_aspect
    elif chamber == "loft_hopper":
        span_x = chamber_span * 1.35
    else:
        span_x = chamber_span
    cx = max(_clamp(cfg.chamber_offset_m, 0.0320, 0.0520), _LUG_X1 + span_x + 0.0075)

    tail_x = cx + span_x + handle_len
    lever_tail_x = tail_x - 0.0065
    grip_len = handle_len * grip_len_ratio

    engage = _clamp(cfg.engage_depth_m, 0.0016, 0.0062)
    engage = min(engage, (depth - screen_t) * 0.30)

    # The chamber rim is the z=0 datum for every candidate, so the plunger's own
    # stack is resolvable here -- and the drives that hang the pressing face on
    # its own pivot need the lever bar raised clear of that pivot's hardware.
    hub_r = _clamp(cfg.hub_radius_m, 0.0040, 0.0066)
    plunger_top_z = -engage + _clamp(cfg.plunger_thickness_m, 0.0050, 0.0120)
    plunger_pivot_z = plunger_top_z + hub_r + 0.0016
    if plunger_drive == "toggle_link":
        lever_lift = max(lever_lift, plunger_pivot_z + 0.0100 - pivot_z)
    elif plunger_drive in {"self_leveling", "cam_follower"}:
        lever_lift = max(lever_lift, plunger_pivot_z + hub_r + 0.0034 - pivot_z)
    lever_bar_z0 = pivot_z + lever_lift
    lever_bar_z1 = lever_bar_z0 + lever_t

    return ResolvedConfig(
        chamber=chamber,
        plunger_drive=plunger_drive,
        accessory=accessory,
        arm_profile=arm_profile,
        screen_rows=screen_rows,
        palette_style=palette_style,
        palette=PALETTES[palette_style],
        handle_len_m=handle_len,
        arm_thickness_m=arm_t,
        arm_half_width_m=arm_hy,
        arm_taper_ratio=arm_taper,
        pivot_rise_m=pivot_rise,
        lever_lift_m=lever_lift,
        lug_inner_y_m=lug_in_y,
        pin_radius_m=pin_r,
        open_rad=_clamp(cfg.open_rad, 0.90, 1.42),
        grip_len_ratio=grip_len_ratio,
        grip_pad_t_m=grip_pad_t,
        tube_radius_m=tube_r,
        neck_len_m=neck_len,
        palm_swell_ratio=palm_swell,
        slot_grip_w_m=slot_grip_w,
        chamber_offset_m=cx,
        chamber_span_m=chamber_span,
        chamber_depth_m=depth,
        chamber_wall_m=chamber_wall,
        screen_thickness_m=screen_t,
        hole_radius_m=hole_r,
        side_hole_count=int(_pick(int(cfg.side_hole_count), (6, 8, 10))),
        collar_height_m=_clamp(cfg.collar_height_m, 0.0042, 0.0088),
        rib_count=int(_pick(int(cfg.rib_count), (3, 4, 6))),
        rib_reach_m=_clamp(cfg.rib_reach_m, 0.0035, 0.0070),
        flange_proud_m=_clamp(cfg.flange_proud_m, 0.0016, 0.0034),
        trough_aspect=trough_aspect,
        trough_fillet_m=_clamp(cfg.trough_fillet_m, 0.0020, 0.0040),
        oval_aspect=oval_aspect,
        hopper_extra_depth_m=_clamp(cfg.hopper_extra_depth_m, 0.0030, 0.0085),
        taper_ratio=_clamp(cfg.taper_ratio, 1.06, 1.26),
        lip_proud_m=_clamp(cfg.lip_proud_m, 0.0015, 0.0035),
        drum_sink_ratio=_clamp(cfg.drum_sink_ratio, 0.22, 0.48),
        face_thickness_m=_clamp(cfg.face_thickness_m, 0.0022, 0.0040),
        hopper_taper_ratio=_clamp(cfg.hopper_taper_ratio, 0.70, 0.96),
        hopper_front_wall_m=_clamp(cfg.hopper_front_wall_m, 0.0025, 0.0046),
        plunger_fill_ratio=_clamp(cfg.plunger_fill_ratio, 0.70, 0.90),
        plunger_thickness_m=_clamp(cfg.plunger_thickness_m, 0.0050, 0.0120),
        engage_depth_m=engage,
        plunger_stem_w_m=_clamp(cfg.plunger_stem_w_m, 0.0080, 0.0160),
        stud_rows=int(_pick(int(cfg.stud_rows), (3, 4, 5))),
        stud_radius_m=_clamp(cfg.stud_radius_m, 0.00090, 0.00160),
        stud_len_m=_clamp(cfg.stud_len_m, 0.00100, 0.00220),
        tilt_rad=_clamp(cfg.tilt_rad, 0.12, 0.30),
        hub_radius_m=_clamp(cfg.hub_radius_m, 0.0040, 0.0066),
        puck_taper_ratio=_clamp(cfg.puck_taper_ratio, 0.86, 1.00),
        cam_radius_m=_clamp(cfg.cam_radius_m, 0.0060, 0.0110),
        roller_radius_m=_clamp(cfg.roller_radius_m, 0.0028, 0.0046),
        cam_offset_y_m=_clamp(cfg.cam_offset_y_m, 0.0130, 0.0195),
        rocker_span_m=_clamp(cfg.rocker_span_m, 0.0160, 0.0265),
        link_len_m=_clamp(cfg.link_len_m, 0.0100, 0.0205),
        rocker_mult=_clamp(cfg.rocker_mult, 0.20, 0.46),
        rocker_lift_m=_clamp(cfg.rocker_lift_m, 0.0080, 0.0185),
        loop_radius_m=_clamp(cfg.loop_radius_m, 0.0055, 0.0102),
        loop_tube_m=_clamp(cfg.loop_tube_m, 0.0016, 0.0029),
        cleaner_pin_len_m=_clamp(cfg.cleaner_pin_len_m, 0.0030, 0.0062),
        cleaner_plate_t_m=_clamp(cfg.cleaner_plate_t_m, 0.0020, 0.0036),
        cleaner_open_rad=_clamp(cfg.cleaner_open_rad, 0.80, 1.40),
        ejector_travel_m=_clamp(cfg.ejector_travel_m, 0.0035, 0.0082),
        ejector_pin_ratio=_clamp(cfg.ejector_pin_ratio, 0.60, 0.85),
        rail_span_ratio=_clamp(cfg.rail_span_ratio, 0.48, 0.80),
        latch_arm_len_m=_clamp(cfg.latch_arm_len_m, 0.0120, 0.0225),
        latch_release_rad=_clamp(cfg.latch_release_rad, 0.78, 1.35),
        capture_pin_r_m=_clamp(cfg.capture_pin_r_m, 0.0012, 0.0022),
        insert_thickness_m=_clamp(cfg.insert_thickness_m, 0.0016, 0.0029),
        insert_fill_ratio=_clamp(cfg.insert_fill_ratio, 0.78, 0.94),
        insert_lift_rad=_clamp(cfg.insert_lift_rad, 0.45, 1.25),
        flip_rad=_clamp(cfg.flip_rad, 0.55, 1.28),
        cradle_plate_t_m=_clamp(cfg.cradle_plate_t_m, 0.0025, 0.0046),
        arm_t=arm_t,
        arm_hy=arm_hy,
        pivot_z=pivot_z,
        pin_r=pin_r,
        pin_cap_r=pin_cap_r,
        knuckle_r=knuckle_r,
        lug_in_y=lug_in_y,
        lug_out_y=lug_out_y,
        lug_top_z=lug_top_z,
        lever_lift=lever_lift,
        lever_t=lever_t,
        lever_bar_z0=lever_bar_z0,
        lever_bar_z1=lever_bar_z1,
        cx=cx,
        tail_x=tail_x,
        lever_tail_x=lever_tail_x,
        grip_len=grip_len,
        separate_plunger=plunger_drive in _SEPARATE_PLUNGER,
        flip_chamber=accessory == "flip_basket",
        name=cfg.name,
    )


def slot_choices_for_config(r: ResolvedConfig) -> dict[str, object]:
    return {
        "chamber": r.chamber,
        "plunger_drive": r.plunger_drive,
        "accessory": r.accessory,
        "arm_profile": r.arm_profile,
        "screen_rows": r.screen_rows,
    }


def slot_choices_for_seed(seed: int) -> dict[str, object]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# CadQuery primitives (metres, like origins 003/004/005/006)
# --------------------------------------------------------------------------- #
def _wp(shape) -> cq.Workplane:
    return cq.Workplane(obj=shape)


def _box(dx: float, dy: float, dz: float, center: Vec3) -> cq.Workplane:
    return _wp(
        cq.Solid.makeBox(
            dx,
            dy,
            dz,
            cq.Vector(center[0] - dx / 2.0, center[1] - dy / 2.0, center[2] - dz / 2.0),
        )
    )


def _cyl(radius: float, length: float, base: Vec3, direction: Vec3) -> cq.Workplane:
    return _wp(cq.Solid.makeCylinder(radius, length, cq.Vector(*base), cq.Vector(*direction)))


def _cone(r0: float, r1: float, length: float, base: Vec3, direction: Vec3) -> cq.Workplane:
    return _wp(cq.Solid.makeCone(r0, r1, length, cq.Vector(*base), cq.Vector(*direction)))


# Terminal rings of a rounded handle nose, as (axial fraction, section scale)
# sampled off a quarter ellipse.  002 ``_lofted_handle`` L53-L74 finishes its own
# handle with a small terminal loft section rather than a point or a sphere; a
# CadQuery sphere carries two parametric poles that OCC tessellates into detached
# zero-area slivers, so a sphere-capped handle exports a non-manifold mesh.
_NOSE_RINGS: tuple[tuple[float, float], ...] = ((0.55, 0.835), (0.85, 0.527), (1.0, 0.26))


def _nose_rings(wp: cq.Workplane, a: float, b: float, length: float) -> cq.Workplane:
    """Append 002's terminal loft sections to an open section chain."""

    previous = 0.0
    for fraction, scale in _NOSE_RINGS:
        wp = wp.workplane(offset=(fraction - previous) * length).ellipse(a * scale, b * scale)
        previous = fraction
    return wp


def _nose_cap(a: float, b: float, length: float, x_start: float, z_axis: float) -> cq.Workplane:
    """A standalone domed nose for a section that was built some other way."""

    start = cq.Workplane("YZ").workplane(offset=x_start).center(0.0, z_axis).ellipse(a, b)
    return _nose_rings(start, a, b, length).loft(ruled=True)


def _clear_of(value: float, avoid: float, margin: float) -> float:
    """Keep a union operand's face off a tangency with the body it joins.

    Two solids whose surfaces meet exactly tangentially fuse into a shell that
    OCC then tessellates with detached zero-area slivers, and the exported mesh
    is non-manifold.  Collision QC cannot run its exact penetration and
    intersection-volume test against a non-manifold mesh, so it falls back to a
    conservative world-AABB estimate and reports overlaps that do not exist.
    Independent parameters can land on such a tangency, so a face that comes
    within ``margin`` of one is pushed clear of it.  It is pushed along the side
    it was already on: which solid swallows the other's end face is a real
    topological difference, and flipping it would only trade one grazing
    configuration for another.
    """

    if abs(value - avoid) >= margin:
        return value
    return avoid + margin if value > avoid else avoid - margin


def _ellipse_prism(a: float, b: float, height: float, center: Vec3) -> cq.Workplane:
    return (
        cq.Workplane("XY", origin=(center[0], center[1], center[2] - height / 2.0))
        .ellipse(a, b)
        .extrude(height)
    )


def _mesh(shape, name: str, tolerance: float = _MESH_TOL):
    return mesh_from_cadquery(
        shape, name, tolerance=min(tolerance, _MESH_TOL), angular_tolerance=_ANG_TOL
    )


def _add(base, shape):
    return shape if base is None else base.union(shape)


def _vadd(*vectors: Vec3) -> Vec3:
    return (
        sum(v[0] for v in vectors),
        sum(v[1] for v in vectors),
        sum(v[2] for v in vectors),
    )


def _vscale(v: Vec3, s: float) -> Vec3:
    return (v[0] * s, v[1] * s, v[2] * s)


def _screen_point(screen: _Screen, a: float, b: float, c: float) -> Vec3:
    """Point at (u=a, v=b, n=c) measured from the screen's outer-face centre."""

    return _vadd(
        screen.origin,
        _vscale(screen.u, a),
        _vscale(screen.v, b),
        _vscale(screen.normal, c),
    )


# --------------------------------------------------------------------------- #
# Perforation fields
# --------------------------------------------------------------------------- #
def _lattice_points(
    hu: float,
    hv: float,
    rows: int,
    hole_r: float,
    *,
    stagger: bool,
    clip: str,
    min_count: int = 0,
) -> tuple[tuple[float, float], ...]:
    """Staggered / square hole lattice inside a screen footprint.

    ``rows`` is the multiplicity ``screen_rows``; the column count follows the
    footprint's own aspect so the pitch stays square, which is how 005
    (``_chamber_hole_points`` L62-L74) and perforation_grid_n30 (L98-L119) both
    lay their fields out.  The total is capped so tessellation stays affordable.

    ``min_count`` is a floor on the field size for a rectangular footprint, where
    nothing is clipped away so the count is exact.  A tall narrow front wall
    (002) at ``screen_rows = 3`` otherwise lands on 3 x 2 - 1 = 5 holes, which
    reads as a slot pattern rather than a screen; the floor widens the field by
    columns only, so the row count still tracks the multiplicity and
    ``_safe_hole_r`` re-derives the radius from the new pitch.
    """

    margin = hole_r + 0.0009
    hu_e = max(hu - margin, hole_r)
    hv_e = max(hv - margin, hole_r)
    rows = max(2, int(rows))
    if clip in {"circle", "ellipse"}:
        # A round footprint throws away its lattice corners, so the lattice is
        # densified by two steps per axis; the field still grows with ``rows``.
        rows = rows + 2
    cols = int(round(rows * (hu_e / max(hv_e, 1e-6))))
    cap = max(2, _MAX_HOLES // rows)
    cols = max(2, min(cols, cap))
    if clip == "rect" and min_count > 0:
        need = min_count + (rows // 2 if stagger else 0)
        cols = max(cols, min(-(-need // rows), cap))
    pv = (2.0 * hv_e) / (rows - 1) if rows > 1 else 0.0
    pu = (2.0 * hu_e) / (cols - 1) if cols > 1 else 0.0
    points: list[tuple[float, float]] = []
    for i in range(rows):
        v = -hv_e + i * pv
        odd = stagger and (i % 2 == 1)
        n = cols - 1 if odd else cols
        shift = pu / 2.0 if odd else 0.0
        for j in range(max(n, 1)):
            u = -hu_e + j * pu + shift
            if u > hu_e + 1e-9:
                continue
            if clip == "circle":
                rad = min(hu_e, hv_e)
                if u * u + v * v > rad * rad + 1e-12:
                    continue
            elif clip == "ellipse":
                if (u / hu_e) ** 2 + (v / hv_e) ** 2 > 1.0 + 1e-9:
                    continue
            points.append((u, v))
    return tuple(points[:_MAX_HOLES])


def _ring_points(radius: float, rings: int, hole_r: float) -> tuple[tuple[float, float], ...]:
    """Concentric radial hole rings (round_cup_grid ``_floor_hole_points`` L70-L88).

    ``rings`` is ``screen_rows``: a centre hole plus ``rings - 1`` rings whose
    counts grow with circumference, each offset by half a pitch so the pattern
    reads as the source's 1 / 6 / 10 / 14 rosette rather than radial spokes.
    """

    # Both the radial and the angular pitch are floored, because two overlapping
    # hole cylinders in the cut compound make OCC delete the whole shell.
    sep = 0.0022
    rings = max(2, int(rings))
    r_eff = max(radius - hole_r - 0.0011, hole_r)
    rings = max(2, min(rings, 1 + int(r_eff / sep)))
    points: list[tuple[float, float]] = [(0.0, 0.0)]
    dr = r_eff / (rings - 1)
    pitch = max(dr, sep)
    for k in range(1, rings):
        rk = k * dr
        count = max(4, min(10, int(2.0 * math.pi * rk / pitch)))
        phase = (math.pi / count) * (k % 2)
        for i in range(count):
            a = phase + 2.0 * math.pi * i / count
            points.append((rk * math.cos(a), rk * math.sin(a)))
        if len(points) >= _MAX_HOLES:
            break
    return tuple(points[:_MAX_HOLES])


def _min_pitch(points: tuple[tuple[float, float], ...]) -> float:
    """Closest centre-to-centre distance in a hole field (inf for < 2 holes)."""

    best = float("inf")
    for i in range(len(points)):
        ux, vx = points[i]
        for j in range(i + 1, len(points)):
            uy, vy = points[j]
            d = math.hypot(ux - uy, vx - vy)
            if d < best:
                best = d
    return best


def _safe_hole_r(points: tuple[tuple[float, float], ...], hole_r: float, margin: float) -> float:
    """Largest hole radius the field's own pitch can carry without self-overlap.

    Every hole is cut as one compound of cylinders; if two of those cylinders
    intersect, OCC's boolean returns garbage and the whole shell disappears
    (a dense `_ring_points` rosette used to do exactly that).  Denser screens
    therefore get finer holes, which is also what a fine screen really is.
    """

    if len(points) < 2:
        return hole_r
    best = _min_pitch(points)
    if not math.isfinite(best) or best <= 0.0:
        return hole_r
    return max(min(hole_r, 0.40 * best - margin), 0.00050)


def _hole_extents(screen: _Screen) -> tuple[float, float]:
    """Half extents of the actual hole field, so a registered plate covers it."""

    if not screen.holes:
        return (screen.hu * 0.8, screen.hv * 0.8)
    return (
        max(abs(u) for u, _ in screen.holes),
        max(abs(v) for _, v in screen.holes),
    )


def _hole_cutter(screen: _Screen, radius: float, start_n: float, length: float):
    """One compound of hole cylinders driven along ``-normal`` through the screen."""

    direction = _vscale(screen.normal, -1.0)
    solids = []
    for u, v in screen.holes:
        base = _screen_point(screen, u, v, start_n)
        solids.append(
            cq.Solid.makeCylinder(radius, length, cq.Vector(*base), cq.Vector(*direction))
        )
    if not solids:
        return None
    return _wp(cq.Compound.makeCompound(solids))


# --------------------------------------------------------------------------- #
# chamber -- round_cup   (004 L68-L74, L77-L84, L107-L122, L125-L137;
#                         collar + side-hole ring from 003 L147-L156, L132-L142)
# --------------------------------------------------------------------------- #
def _chamber_round_cup_build(r: ResolvedConfig):
    cup_r = r.chamber_span_m
    cav_r = cup_r - r.chamber_wall_m
    bottom = -r.chamber_depth_m
    floor_top = bottom + r.screen_thickness_m
    _pts = _lattice_points(
        cav_r, cav_r, r.screen_rows, r.hole_radius_m, stagger=False, clip="circle"
    )
    _hr = _safe_hole_r(_pts, r.hole_radius_m, 0.00045)
    screen = _Screen(
        origin=(r.cx, 0.0, bottom),
        normal=(0.0, 0.0, -1.0),
        u=(1.0, 0.0, 0.0),
        v=(0.0, 1.0, 0.0),
        hu=cav_r,
        hv=cav_r,
        thickness=r.screen_thickness_m,
        holes=_pts,
        hole_r=_hr,
        clip="circle",
    )
    body = _cyl(cup_r, r.chamber_depth_m, (r.cx, 0.0, bottom), (0.0, 0.0, 1.0))
    # Cavity runs past the rim so the top is genuinely open (004 `_cavity_solid`).
    body = body.cut(_cyl(cav_r, r.chamber_depth_m + 0.004, (r.cx, 0.0, floor_top), (0.0, 0.0, 1.0)))
    # Polished collar wrapping the rim (003 L147-L156).
    collar_h = min(r.collar_height_m, r.chamber_depth_m - r.screen_thickness_m - 0.003)
    body = body.union(
        _cyl(cup_r + 0.0018, collar_h, (r.cx, 0.0, -collar_h), (0.0, 0.0, 1.0)).cut(
            _cyl(cav_r, collar_h + 0.004, (r.cx, 0.0, -collar_h - 0.002), (0.0, 0.0, 1.0))
        )
    )
    cutter = _hole_cutter(screen, screen.hole_r, 0.0015, r.screen_thickness_m + 0.004)
    if cutter is not None:
        body = body.cut(cutter)
    # One ring of radial holes low on the side wall (003 L132-L142).
    side_z = floor_top + (r.chamber_depth_m - r.screen_thickness_m) * 0.30
    side = None
    for k in range(r.side_hole_count):
        a = 2.0 * math.pi * k / r.side_hole_count
        c, s = math.cos(a), math.sin(a)
        side = _add(
            side,
            _cyl(
                screen.hole_r,
                r.chamber_wall_m * 2.4,
                (r.cx + c * (cav_r - 0.0004), s * (cav_r - 0.0004), side_z),
                (c, s, 0.0),
            ),
        )
    if side is not None:
        body = body.cut(side)
    spec = _ChamberSpec(
        cx=r.cx,
        liner_hv=cav_r,
        hx=cup_r + 0.0018,
        hy=cup_r + 0.0018,
        rim_z=0.0,
        bottom_z=bottom,
        top_z=0.0,
        cavity_floor_z=floor_top,
        mouth_hx=cav_r,
        mouth_hy=cav_r,
        mouth_kind="circle",
        screen=screen,
    )
    return spec, [("shell", body, "body")]


# --------------------------------------------------------------------------- #
# chamber -- ribbed_cup   (round_cup_grid L70-L88, L121-L144, L147-L161, L164-L199)
# --------------------------------------------------------------------------- #
def _chamber_ribbed_cup_build(r: ResolvedConfig):
    cup_r = r.chamber_span_m
    cav_r = cup_r - r.chamber_wall_m
    bottom = -r.chamber_depth_m
    floor_top = bottom + r.screen_thickness_m
    _RING_PTS = _ring_points(cav_r, r.screen_rows, r.hole_radius_m)
    _RING_HR = _safe_hole_r(_RING_PTS, r.hole_radius_m, 0.00075)
    screen = _Screen(
        origin=(r.cx, 0.0, bottom),
        normal=(0.0, 0.0, -1.0),
        u=(1.0, 0.0, 0.0),
        v=(0.0, 1.0, 0.0),
        hu=cav_r,
        hv=cav_r,
        thickness=r.screen_thickness_m,
        holes=_RING_PTS,
        hole_r=_RING_HR,
        clip="circle",
    )
    body = _cyl(cup_r, r.chamber_depth_m, (r.cx, 0.0, bottom), (0.0, 0.0, 1.0))
    body = body.cut(_cyl(cav_r, r.chamber_depth_m + 0.004, (r.cx, 0.0, floor_top), (0.0, 0.0, 1.0)))
    cutter = _hole_cutter(screen, screen.hole_r, 0.0015, r.screen_thickness_m + 0.004)
    if cutter is not None:
        body = body.cut(cutter)
    # Countersink bevels on the cavity side of every hole (L138-L143).
    bevel = _hole_cutter(
        screen, screen.hole_r + 0.0004, 0.0005, 0.0005 + r.screen_thickness_m * 0.42
    )
    if bevel is not None:
        body = body.cut(bevel)
    # Proud radial rim flange (L147-L161).
    flange_h = 0.0028
    body = body.union(
        _cyl(cup_r + r.flange_proud_m, flange_h, (r.cx, 0.0, -flange_h), (0.0, 0.0, 1.0)).cut(
            _cyl(cav_r, flange_h + 0.004, (r.cx, 0.0, -flange_h - 0.002), (0.0, 0.0, 1.0))
        )
    )
    # Cast radial support fins embedded 2 mm into the barrel (L164-L199).
    rib_lo = bottom + 0.0022
    rib_hi = -flange_h - 0.0008
    rib_h = max(rib_hi - rib_lo, 0.004)
    for k in range(r.rib_count):
        a = 2.0 * math.pi * k / r.rib_count
        r_in = cup_r - 0.0020
        r_out = cup_r + r.rib_reach_m
        r_mid = 0.5 * (r_in + r_out)
        length = r_out - r_in
        rib = _box(length, 0.0022, rib_h, (r_mid, 0.0, rib_lo + rib_h / 2.0))
        rib = rib.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(a))
        body = body.union(rib.translate((r.cx, 0.0, 0.0)))
    spec = _ChamberSpec(
        cx=r.cx,
        liner_hv=cav_r,
        hx=cup_r + max(r.flange_proud_m, r.rib_reach_m),
        hy=cup_r + max(r.flange_proud_m, r.rib_reach_m),
        rim_z=0.0,
        bottom_z=bottom,
        top_z=0.0,
        cavity_floor_z=floor_top,
        mouth_hx=cav_r,
        mouth_hy=cav_r,
        mouth_kind="circle",
        screen=screen,
    )
    return spec, [("shell", body, "body")]


# --------------------------------------------------------------------------- #
# chamber -- rect_trough   (005 L62-L74, L98-L117)
# --------------------------------------------------------------------------- #
def _chamber_rect_trough_build(r: ResolvedConfig):
    hx = r.chamber_span_m * r.trough_aspect
    hy = r.chamber_span_m
    cav_hx = hx - r.chamber_wall_m
    cav_hy = hy - r.chamber_wall_m
    bottom = -r.chamber_depth_m
    floor_top = bottom + r.screen_thickness_m
    _pts = _lattice_points(
        cav_hx,
        cav_hy,
        r.screen_rows,
        r.hole_radius_m,
        stagger=True,
        clip="rect",
        min_count=_MIN_SCREEN_HOLES,
    )
    _hr = _safe_hole_r(_pts, r.hole_radius_m, 0.00045)
    screen = _Screen(
        origin=(r.cx, 0.0, bottom),
        normal=(0.0, 0.0, -1.0),
        u=(1.0, 0.0, 0.0),
        v=(0.0, 1.0, 0.0),
        hu=cav_hx,
        hv=cav_hy,
        thickness=r.screen_thickness_m,
        holes=_pts,
        hole_r=_hr,
        clip="rect",
    )
    body = _box(
        2.0 * hx, 2.0 * hy, r.chamber_depth_m, (r.cx, 0.0, bottom + r.chamber_depth_m / 2.0)
    )
    try:
        body = body.edges("(|X or |Y) and <Z").fillet(r.trough_fillet_m)
    except Exception:  # pragma: no cover - fillet is cosmetic only
        pass
    body = body.cut(
        _box(
            2.0 * cav_hx,
            2.0 * cav_hy,
            r.chamber_depth_m,
            (r.cx, 0.0, floor_top + r.chamber_depth_m / 2.0),
        )
    )
    cutter = _hole_cutter(screen, screen.hole_r, 0.0015, r.screen_thickness_m + 0.004)
    if cutter is not None:
        body = body.cut(cutter)
    spec = _ChamberSpec(
        cx=r.cx,
        liner_hv=cav_hy,
        hx=hx,
        hy=hy,
        rim_z=0.0,
        bottom_z=bottom,
        top_z=0.0,
        cavity_floor_z=floor_top,
        mouth_hx=cav_hx,
        mouth_hy=cav_hy,
        mouth_kind="rect",
        screen=screen,
    )
    return spec, [("shell", body, "body")]


# --------------------------------------------------------------------------- #
# chamber -- oval_hopper   (deep_oval_hopper L69-L93, L130-L153)
# --------------------------------------------------------------------------- #
def _chamber_oval_hopper_build(r: ResolvedConfig):
    hx = r.chamber_span_m * r.oval_aspect
    hy = r.chamber_span_m
    cav_hx = hx - r.chamber_wall_m
    cav_hy = hy - r.chamber_wall_m
    depth = r.chamber_depth_m + r.hopper_extra_depth_m
    bottom = -depth
    floor_top = bottom + r.screen_thickness_m
    _pts = _lattice_points(
        cav_hx, cav_hy, r.screen_rows, r.hole_radius_m, stagger=True, clip="ellipse"
    )
    _hr = _safe_hole_r(_pts, r.hole_radius_m, 0.00045)
    screen = _Screen(
        origin=(r.cx, 0.0, bottom),
        normal=(0.0, 0.0, -1.0),
        u=(1.0, 0.0, 0.0),
        v=(0.0, 1.0, 0.0),
        hu=cav_hx,
        hv=cav_hy,
        thickness=r.screen_thickness_m,
        holes=_pts,
        hole_r=_hr,
        clip="ellipse",
    )
    body = _ellipse_prism(hx, hy, depth, (r.cx, 0.0, bottom + depth / 2.0))
    body = body.cut(_ellipse_prism(cav_hx, cav_hy, depth, (r.cx, 0.0, floor_top + depth / 2.0)))
    cutter = _hole_cutter(screen, screen.hole_r, 0.0015, r.screen_thickness_m + 0.004)
    if cutter is not None:
        body = body.cut(cutter)
    spec = _ChamberSpec(
        cx=r.cx,
        liner_hv=cav_hy,
        hx=hx,
        hy=hy,
        rim_z=0.0,
        bottom_z=bottom,
        top_z=0.0,
        cavity_floor_z=floor_top,
        mouth_hx=cav_hx,
        mouth_hy=cav_hy,
        mouth_kind="ellipse",
        screen=screen,
    )
    return spec, [("shell", body, "body")]


# --------------------------------------------------------------------------- #
# chamber -- taper_cup   (006 L25-L36, L39-L60, L63-L79, L82-L89)
# --------------------------------------------------------------------------- #
def _chamber_taper_cup_build(r: ResolvedConfig):
    rim_r = r.chamber_span_m
    bot_r = rim_r / r.taper_ratio
    depth = r.chamber_depth_m
    bottom = -depth
    wall = r.chamber_wall_m
    floor_top = bottom + r.screen_thickness_m
    cav_bot_r = bot_r - wall
    cav_rim_r = rim_r - wall * 0.75
    _pts = _lattice_points(
        cav_bot_r, cav_bot_r, r.screen_rows, r.hole_radius_m, stagger=True, clip="circle"
    )
    _hr = _safe_hole_r(_pts, r.hole_radius_m, 0.00045)
    screen = _Screen(
        origin=(r.cx, 0.0, bottom),
        normal=(0.0, 0.0, -1.0),
        u=(1.0, 0.0, 0.0),
        v=(0.0, 1.0, 0.0),
        hu=cav_bot_r,
        hv=cav_bot_r,
        thickness=r.screen_thickness_m,
        holes=_pts,
        hole_r=_hr,
        clip="circle",
    )
    outer = _cone(bot_r, rim_r, depth, (r.cx, 0.0, bottom), (0.0, 0.0, 1.0))
    inner = _cone(
        cav_bot_r,
        cav_rim_r,
        depth + 0.004,
        (r.cx, 0.0, floor_top),
        (0.0, 0.0, 1.0),
    )
    body = outer.cut(inner)
    cutter = _hole_cutter(screen, screen.hole_r, 0.0015, r.screen_thickness_m + 0.004)
    if cutter is not None:
        body = body.cut(cutter)
    # Rolled upper lip standing proud of the shell (006 L71-L78).
    lip_h = 0.0032
    body = body.union(
        _cyl(rim_r + r.lip_proud_m, lip_h, (r.cx, 0.0, -lip_h), (0.0, 0.0, 1.0)).cut(
            _cyl(cav_rim_r, lip_h + 0.004, (r.cx, 0.0, -lip_h - 0.002), (0.0, 0.0, 1.0))
        )
    )
    # The perforated bottom web is a separate, darker visual (006 L82-L89):
    # that is what makes the screen read as a screen instead of a cup floor.
    face = _cyl(
        cav_bot_r + wall * 0.55,
        r.face_thickness_m,
        (r.cx, 0.0, bottom - r.face_thickness_m + 0.0004),
        (0.0, 0.0, 1.0),
    )
    face_screen = _Screen(
        origin=(r.cx, 0.0, bottom - r.face_thickness_m + 0.0004),
        normal=(0.0, 0.0, -1.0),
        u=screen.u,
        v=screen.v,
        hu=screen.hu,
        hv=screen.hv,
        thickness=r.face_thickness_m,
        holes=screen.holes,
        hole_r=screen.hole_r,
        clip="circle",
    )
    face_cut = _hole_cutter(face_screen, screen.hole_r, 0.0015, r.face_thickness_m + 0.004)
    if face_cut is not None:
        face = face.cut(face_cut)
    spec = _ChamberSpec(
        cx=r.cx,
        liner_hv=cav_bot_r,
        hx=rim_r + r.lip_proud_m,
        hy=rim_r + r.lip_proud_m,
        rim_z=0.0,
        bottom_z=bottom - r.face_thickness_m,
        top_z=0.0,
        cavity_floor_z=floor_top,
        mouth_hx=cav_rim_r,
        mouth_hy=cav_rim_r,
        mouth_kind="circle",
        screen=_Screen(
            origin=(r.cx, 0.0, bottom - r.face_thickness_m + 0.0004),
            normal=(0.0, 0.0, -1.0),
            u=screen.u,
            v=screen.v,
            hu=screen.hu,
            hv=screen.hv,
            thickness=r.screen_thickness_m + r.face_thickness_m,
            holes=screen.holes,
            hole_r=screen.hole_r,
            clip="circle",
        ),
    )
    return spec, [("shell", body, "body"), ("screen", face, "screen")]


# --------------------------------------------------------------------------- #
# chamber -- drum_face   (001 L128-L176)
# --------------------------------------------------------------------------- #
def _chamber_drum_face_build(r: ResolvedConfig):
    drum_r = r.chamber_span_m
    drum_hl = r.chamber_span_m * 0.95
    wall = r.chamber_wall_m
    face_t = r.face_thickness_m
    inner_r = drum_r - wall
    sink = inner_r * r.drum_sink_ratio
    drum_cz = -sink - (r.chamber_depth_m - inner_r - sink) * 0.0 - sink * 0.0
    # Axis height is fixed by the mouth cut: the rim is at z = 0, the axis sinks
    # by `sink` so the loading mouth spans 2*sqrt(inner_r^2 - sink^2) in X.
    drum_cz = -sink
    mouth_hx = math.sqrt(max(inner_r * inner_r - sink * sink, 1e-8))
    face_y = -drum_hl
    _pts = _lattice_points(
        inner_r, inner_r, r.screen_rows, r.hole_radius_m, stagger=False, clip="circle"
    )
    _hr = _safe_hole_r(_pts, r.hole_radius_m, 0.00045)
    screen = _Screen(
        origin=(r.cx, face_y, drum_cz),
        normal=(0.0, -1.0, 0.0),
        u=(1.0, 0.0, 0.0),
        v=(0.0, 0.0, 1.0),
        hu=inner_r,
        hv=inner_r,
        thickness=face_t,
        holes=_pts,
        hole_r=_hr,
        clip="circle",
    )
    body = _cyl(drum_r, 2.0 * drum_hl, (r.cx, face_y, drum_cz), (0.0, 1.0, 0.0))
    # Bore from the rear, leaving the full-thickness circular end plate at -Y.
    body = body.cut(
        _cyl(
            inner_r,
            2.0 * drum_hl - face_t + 0.004,
            (r.cx, face_y + face_t, drum_cz),
            (0.0, 1.0, 0.0),
        )
    )
    # Rounded box cut removes the upper rear: the loading mouth (001 L136-L142).
    body = body.cut(
        _box(
            2.0 * drum_r + 0.006,
            2.0 * drum_hl + 0.006,
            2.0 * drum_r,
            (r.cx, 0.0, drum_r),
        )
    )
    cutter = _hole_cutter(screen, screen.hole_r, 0.0015, face_t + 0.004)
    if cutter is not None:
        body = body.cut(cutter)
    spec = _ChamberSpec(
        cx=r.cx,
        liner_hv=min(inner_r, sink * 0.72),
        hx=drum_r,
        hy=drum_hl,
        rim_z=0.0,
        bottom_z=drum_cz - drum_r,
        top_z=0.0,
        cavity_floor_z=drum_cz - inner_r,
        mouth_hx=mouth_hx,
        mouth_hy=drum_hl - face_t - 0.0015,
        mouth_kind="rect",
        screen=screen,
    )
    return spec, [("shell", body, "body")]


# --------------------------------------------------------------------------- #
# chamber -- loft_hopper   (002 L76-L114)
# --------------------------------------------------------------------------- #
def _chamber_loft_hopper_build(r: ResolvedConfig):
    hx = r.chamber_span_m * 1.35
    front_hy = r.chamber_span_m
    rear_hy = front_hy * r.hopper_taper_ratio
    depth = r.chamber_depth_m
    bottom = -depth
    wall = r.chamber_wall_m
    front_x = r.cx - hx
    front_wall = r.hopper_front_wall_m
    cav_front_hy = front_hy - wall
    cav_rear_hy = rear_hy - wall
    cav_bottom = bottom + wall
    screen_cz = (cav_bottom + 0.0) / 2.0
    screen_hv = (0.0 - cav_bottom) / 2.0 - 0.0008
    _pts = _lattice_points(
        cav_front_hy,
        max(screen_hv, 0.0025),
        r.screen_rows,
        r.hole_radius_m,
        stagger=True,
        clip="rect",
        min_count=_MIN_SCREEN_HOLES,
    )
    _hr = _safe_hole_r(_pts, r.hole_radius_m, 0.00045)
    screen = _Screen(
        origin=(front_x, 0.0, screen_cz),
        normal=(-1.0, 0.0, 0.0),
        u=(0.0, 1.0, 0.0),
        v=(0.0, 0.0, 1.0),
        hu=cav_front_hy,
        hv=max(screen_hv, 0.0025),
        thickness=front_wall,
        holes=_pts,
        hole_r=_hr,
        clip="rect",
    )
    # Ruled loft between two rectangles along the tool axis (002 L77-L85).
    outer = (
        cq.Workplane("YZ")
        .workplane(offset=front_x)
        .center(0.0, bottom + depth / 2.0)
        .rect(2.0 * front_hy, depth)
        .workplane(offset=2.0 * hx)
        .rect(2.0 * rear_hy, depth)
        .loft(ruled=True)
    )
    cavity = (
        cq.Workplane("YZ")
        .workplane(offset=front_x + front_wall)
        .center(0.0, cav_bottom + (depth + 0.006) / 2.0)
        .rect(2.0 * cav_front_hy, depth + 0.006)
        .workplane(offset=2.0 * hx - front_wall - wall)
        .rect(2.0 * cav_rear_hy, depth + 0.006)
        .loft(ruled=True)
    )
    body = outer.cut(cavity)
    cutter = _hole_cutter(screen, screen.hole_r, 0.0015, front_wall + 0.004)
    if cutter is not None:
        body = body.cut(cutter)
    spec = _ChamberSpec(
        cx=r.cx,
        liner_hv=max(screen_hv, 0.0025) * 0.72,
        hx=hx,
        hy=front_hy,
        rim_z=0.0,
        bottom_z=bottom,
        top_z=0.0,
        cavity_floor_z=cav_bottom,
        mouth_hx=hx - front_wall - wall - 0.0012,
        mouth_hy=cav_rear_hy - 0.0008,
        mouth_kind="rect",
        screen=screen,
    )
    return spec, [("shell", body, "body")]


_CHAMBER_BUILDERS = {
    "round_cup": _chamber_round_cup_build,
    "ribbed_cup": _chamber_ribbed_cup_build,
    "rect_trough": _chamber_rect_trough_build,
    "oval_hopper": _chamber_oval_hopper_build,
    "taper_cup": _chamber_taper_cup_build,
    "drum_face": _chamber_drum_face_build,
    "loft_hopper": _chamber_loft_hopper_build,
}


def _build_chamber(r: ResolvedConfig):
    return _CHAMBER_BUILDERS[r.chamber](r)


def _cavity_clear_solid(spec: _ChamberSpec, grow: float = 0.0):
    """Solid filling the chamber mouth, used to keep the frame out of the cup."""

    height = (spec.rim_z - spec.cavity_floor_z) + 0.030
    zc = spec.cavity_floor_z + height / 2.0
    if spec.mouth_kind == "circle":
        return _cyl(
            spec.mouth_hx + grow, height, (spec.cx, 0.0, spec.cavity_floor_z), (0.0, 0.0, 1.0)
        )
    if spec.mouth_kind == "ellipse":
        return _ellipse_prism(
            spec.mouth_hx + grow, spec.mouth_hy + grow, height, (spec.cx, 0.0, zc)
        )
    return _box(
        2.0 * (spec.mouth_hx + grow),
        2.0 * (spec.mouth_hy + grow),
        height,
        (spec.cx, 0.0, zc),
    )


def _face_solid(kind: str, hx: float, hy: float, thickness: float, center: Vec3):
    """A pressing face / liner plate in the chamber's own mouth shape."""

    if kind == "circle":
        return _cyl(
            hx, thickness, (center[0], center[1], center[2] - thickness / 2.0), (0.0, 0.0, 1.0)
        )
    if kind == "ellipse":
        return _ellipse_prism(hx, hy, thickness, center)
    return _box(2.0 * hx, 2.0 * hy, thickness, center)


# --------------------------------------------------------------------------- #
# arm_profile -- one arm body, three source-backed sections
# --------------------------------------------------------------------------- #
def _arm_profile_flat_bar_build(
    r: ResolvedConfig, x0: float, x1: float, z_axis: float, hw0: float, hw1: float, hh: float
) -> cq.Workplane:
    """Tapered polyline bar swept in plan and extruded (004 L86-L104, L153-L184)."""

    pts = [(x0, hw0), (x1, hw1), (x1, -hw1), (x0, -hw0)]
    bar = cq.Workplane("XY", origin=(0.0, 0.0, z_axis - hh)).polyline(pts).close().extrude(2.0 * hh)
    try:
        bar = bar.edges("|Z and >X").fillet(min(hw1 * 0.85, hh * 1.4))
    except Exception:  # pragma: no cover - the tail radius is cosmetic
        pass
    return bar


def _arm_profile_round_tube_build(
    r: ResolvedConfig, x0: float, x1: float, z_axis: float, hw0: float, hw1: float, hh: float
) -> cq.Workplane:
    """Round tube out of a cone neck, closed by a domed cap (003 L177-L189, L229-L238).

    003 fuses a literal sphere of the tube's own radius onto the tube end.  That
    sphere's two parametric poles tessellate into detached zero-area slivers, so
    the exported handle is non-manifold and collision QC loses its exact
    penetration test on every arm.  The dome is built from 002's terminal loft
    rings instead, which reaches the same ``x1 + tube_r`` tip watertight.
    """

    tube_r = min(hh, hw1)
    neck = min(r.neck_len_m, (x1 - x0) * 0.35)
    body = _cone(tube_r * 0.62, tube_r, neck, (x0, 0.0, z_axis), (1.0, 0.0, 0.0))
    body = body.union(_cyl(tube_r, (x1 - x0) - neck, (x0 + neck, 0.0, z_axis), (1.0, 0.0, 0.0)))
    return body.union(_nose_cap(tube_r, tube_r, tube_r, x1, z_axis))


def _arm_profile_lofted_ellipse_build(
    r: ResolvedConfig, x0: float, x1: float, z_axis: float, hw0: float, hw1: float, hh: float
) -> cq.Workplane:
    """Elliptical loft carried into 002's own rounded terminal sections.

    002 ``_lofted_handle`` L53-L74 lofts three ellipses and then adds a small
    1.2 mm terminal ellipse -- a finite section, not a collapsed point.  006
    L92-L102 builds the same loft and fuses a sphere onto it instead; that
    alternative is not used here because a CadQuery sphere's two parametric
    poles tessellate into detached zero-area slivers, which makes the exported
    handle non-manifold and costs collision QC its exact penetration test.
    Continuing the loft through three shrinking rings keeps 002's structure,
    reaches the same tip station, and stays watertight.
    """

    run = x1 - x0
    mid = x0 + run * 0.42
    swell = r.palm_swell_ratio
    end_a = hw1 * 0.86
    end_b = hh * 0.84
    sections = (
        cq.Workplane("YZ")
        .workplane(offset=x0)
        .center(0.0, z_axis)
        .ellipse(hw0 * 0.82, hh * 0.86)
        .workplane(offset=mid - x0)
        .ellipse(hw0 * swell * 0.86, hh * swell * 0.80)
        .workplane(offset=x1 - mid)
        .ellipse(end_a, end_b)
    )
    return _nose_rings(sections, end_a, end_b, min(end_a, end_b)).loft(ruled=True)


_ARM_BUILDERS = {
    "flat_bar": _arm_profile_flat_bar_build,
    "round_tube": _arm_profile_round_tube_build,
    "lofted_ellipse": _arm_profile_lofted_ellipse_build,
}


def _arm_body(
    r: ResolvedConfig, x0: float, x1: float, z_axis: float, hw0: float, hw1: float, hh: float
) -> cq.Workplane:
    return _ARM_BUILDERS[r.arm_profile](r, x0, x1, z_axis, hw0, hw1, hh)


def _arm_start_half_y(r: ResolvedConfig, hw0: float, hw1: float, hh: float) -> float:
    """``|y|`` the arm section reaches at ``x0``, whatever profile it is.

    Whatever joins the arm at that station has to stay off this value or the two
    surfaces meet tangentially and the fused solid tessellates non-manifold.
    """

    if r.arm_profile == "lofted_ellipse":
        return hw0 * 0.82
    if r.arm_profile == "round_tube":
        return min(hh, hw1) * 0.62
    return hw0


def _grip_pad(
    r: ResolvedConfig, x_end: float, z_face: float, half_w: float, upward: bool
) -> cq.Workplane | None:
    """Polymer grip let into the arm: a filleted pad (004) or a slot profile (002).

    ``round_tube`` returns None -- origin 003's handles are bare metal end to end,
    which is a part-list difference and not just a material difference.
    """

    if r.arm_profile == "round_tube":
        return None
    length = max(r.grip_len, 0.020)
    x_c = x_end - length / 2.0 - 0.0035
    t = r.grip_pad_t_m
    z_c = z_face + (t / 2.0 - 0.0006) * (1.0 if upward else -1.0)
    if r.arm_profile == "lofted_ellipse":
        width = min(r.slot_grip_w_m, 2.0 * half_w * 0.94)
        pad = cq.Workplane("XY", origin=(x_c, 0.0, z_c - t / 2.0)).slot2D(length, width).extrude(t)
        return pad
    pad = _box(length, min(2.0 * half_w * 0.92, 0.024), t, (x_c, 0.0, z_c))
    try:
        pad = pad.edges("|Z").fillet(min(half_w * 0.55, 0.0055))
    except Exception:  # pragma: no cover
        pass
    return pad


# --------------------------------------------------------------------------- #
# Nose casting, lugs and the welded lower frame
# --------------------------------------------------------------------------- #
def _chamber_envelope(spec: _ChamberSpec, gap: float) -> cq.Workplane:
    return _box(
        2.0 * (spec.hx + gap),
        2.0 * (spec.hy + gap),
        (spec.rim_z - spec.bottom_z) + 2.0 * gap + 0.030,
        (
            spec.cx,
            0.0,
            spec.bottom_z - gap + ((spec.rim_z - spec.bottom_z) + 2.0 * gap + 0.030) / 2.0,
        ),
    )


def _rail_y(r: ResolvedConfig, spec: _ChamberSpec) -> float:
    """Lateral station of the two cast side cheeks that tie nose to handle.

    001 ``_make_basket_metal`` L161-L171 runs exactly these cheeks down both sides
    of the cup, leaving a central lane for the plunger.  They are what keeps the
    welded frame one solid once the mouth is cut out of it.
    """

    inner = spec.mouth_hy + 0.0021
    outer = max(spec.hy - 0.0012, inner)
    rail = min(max(inner, 0.5 * (inner + outer)), spec.hy + 0.0035)
    if abs(spec.screen.normal[0]) > 0.5:
        # The front-wall screen's own u axis is +Y, so the cheeks have to stand
        # outboard of the hole field or they sit inside the module's footprint.
        rail = max(rail, spec.screen.hu + 0.0045)
    return rail


def _rail_station(r: ResolvedConfig, spec: _ChamberSpec) -> tuple[float, float]:
    """(cheek station, cheek thickness) -- the flip cradle replaces both."""

    if r.flip_chamber:
        return (spec.hy + 0.0006 + r.cradle_plate_t_m / 2.0, r.cradle_plate_t_m)
    return (_rail_y(r, spec), 0.0036)


def _frame_reach_hy(r: ResolvedConfig, spec: _ChamberSpec) -> float:
    """Widest ``|y|`` the lower frame reaches between the pivot and the chamber.

    The clevis lugs, the cast head and the two side cheeks all live at that
    station, which is exactly the station a lever-mounted body swings over.
    """

    rail_y, rail_t = _rail_station(r, spec)
    return max(r.lug_out_y, rail_y + rail_t / 2.0)


def _flip_hinge(r: ResolvedConfig, spec: _ChamberSpec) -> tuple[float, float, float]:
    """(x, z, barrel half length) of the flip_basket hinge, shared with the frame.

    The frame has to know where the basket's barrel is: the barrel is a hub
    coaxial with the flip axis, so its swept envelope is that cylinder and the
    welded frame has to stand clear of it at every angle.
    """

    hinge_x = spec.cx + spec.hx + 0.0024
    hinge_z = spec.bottom_z + max(0.0030, r.screen_thickness_m * 0.6)
    cradle_y = spec.hy + 0.0006 + r.cradle_plate_t_m / 2.0
    return (hinge_x, hinge_z, min(spec.hy * 0.72, cradle_y - 0.0012))


def _build_frame_body(r: ResolvedConfig, spec: _ChamberSpec) -> cq.Workplane:
    arm_z = -r.arm_t / 2.0
    hh = r.arm_t / 2.0
    hw0 = r.arm_hy
    hw1 = r.arm_hy * r.arm_taper_ratio
    # The arm starts behind the chamber; the two cast side cheeks carry the load
    # forward past the mouth to the clevis, which is what keeps the welded frame
    # one connected solid after the mouth is cut out of it.
    gap = (0.0007 + r.cradle_plate_t_m) if r.flip_chamber else 0.0
    arm_start = spec.cx + spec.hx + gap - (0.0 if r.flip_chamber else 0.0040)
    barrel_clear = 0.0
    if r.flip_chamber:
        # The basket's hinge barrel stands just behind the chamber, in the very
        # station the hand arm starts from, so the arm has to start behind it.
        hinge_x, hinge_z, barrel_half = _flip_hinge(r, spec)
        barrel_clear = 0.0044 + 0.0010
        arm_start = max(arm_start, hinge_x + barrel_clear + 0.0012)
    body = _arm_body(r, arm_start, r.tail_x, arm_z, hw0, hw1, hh)

    # Nose bridge: from the clevis back to the chamber front wall (004 L136).
    bridge_x1 = spec.cx - spec.hx + (0.0 if r.flip_chamber else 0.004)
    if r.flip_chamber:
        bridge_x1 -= 0.0018
    rail_y, rail_t = _rail_station(r, spec)
    # The cast head is as wide as the cheeks it has to carry, which is how 001's
    # `_make_basket_metal` ties its two side cheeks back into the clevis.
    head_hy = _frame_reach_hy(r, spec)
    if abs(spec.screen.normal[1]) > 0.5 and not r.flip_chamber:
        # 001's screen *is* the chamber's own -Y end face.  A head wider than the
        # drum would stand between that face and anything registered on it, so
        # the casting stops at the drum -- the lugs still meet it (lug_in_y is at
        # most 9.2 mm against a 11.6 mm minimum half length) and so do the
        # cheeks, which `_rail_y` already keeps inboard of the end faces.
        head_hy = max(min(head_hy, spec.hy - 0.0006), r.lug_in_y + 0.0008)
    bridge = _box(
        bridge_x1 - _LUG_X0,
        2.0 * head_hy,
        r.arm_t,
        ((_LUG_X0 + bridge_x1) / 2.0, 0.0, arm_z),
    )
    body = body.union(bridge)

    # Two cast side cheeks bridging the chamber station.
    rail_x1 = arm_start + 0.0075
    for sy in (-rail_y, rail_y):
        body = body.union(
            _box(
                rail_x1 - _LUG_X0,
                rail_t,
                r.arm_t,
                ((_LUG_X0 + rail_x1) / 2.0, sy, arm_z),
            )
        )
    # Transition tie block behind the chamber: it is what ties both cheeks into
    # the hand arm whatever the arm's own section is.  Its half width follows the
    # cheek station, which is derived from the chamber and so is free to land on
    # the arm section's own half width; ``_clear_of`` keeps the two off a tangency.
    tie_half = max(
        0.0035, _clear_of(rail_y + rail_t / 2.0, _arm_start_half_y(r, hw0, hw1, hh), 0.0004)
    )
    body = body.union(
        _box(
            0.0130,
            2.0 * tie_half,
            r.arm_t,
            (arm_start + 0.0035, 0.0, arm_z),
        )
    )

    # Twin clevis lugs with rounded pin noses and a tie web (004 L125-L137 /
    # 005 L131-L144).
    for sy in (-1.0, 1.0):
        y_c = sy * (r.lug_in_y + _LUG_T / 2.0)
        lug = _box(
            _LUG_X1 - _LUG_X0,
            _LUG_T,
            r.lug_top_z + r.arm_t,
            ((_LUG_X0 + _LUG_X1) / 2.0, y_c, (r.lug_top_z - r.arm_t) / 2.0),
        )
        nose = _cyl(
            r.pin_cap_r + 0.0026,
            _LUG_T,
            (0.0, y_c - _LUG_T / 2.0, r.pivot_z),
            (0.0, 1.0, 0.0),
        )
        body = body.union(lug).union(nose)
    web_top = min(0.0, r.pivot_z - r.knuckle_r - 0.0012)
    body = body.union(
        _box(
            _LUG_X1 - _LUG_X0 - 0.001,
            2.0 * r.lug_out_y,
            max(web_top + r.arm_t, 0.0025),
            (
                (_LUG_X0 + _LUG_X1) / 2.0,
                0.0,
                -r.arm_t + max(web_top + r.arm_t, 0.0025) / 2.0,
            ),
        )
    )

    # Keep the frame out of the chamber mouth (004 L104) or, when the chamber is
    # a moving part, out of its whole swept envelope.
    if r.flip_chamber:
        body = body.cut(_chamber_envelope(spec, 0.0007))
        # ... and out of the barrel's own swept cylinder, which stands proud of
        # that envelope.  Only the central lane is taken, so the two cheeks that
        # carry the casting back to the arm are untouched.
        body = body.cut(
            _cyl(
                barrel_clear,
                2.0 * (barrel_half + 0.0010),
                (hinge_x, -(barrel_half + 0.0010), hinge_z),
                (0.0, 1.0, 0.0),
            )
        )
    else:
        body = body.cut(_cavity_clear_solid(spec, 0.0008))

    # True clearance bore for the hinge pin through both lugs (005 L146).
    body = body.cut(
        _cyl(
            r.pin_r + _BORE_CLEARANCE,
            2.0 * (r.lug_out_y + 0.004),
            (0.0, -(r.lug_out_y + 0.004), r.pivot_z),
            (0.0, 1.0, 0.0),
        )
    )
    return body


def _build_pivot_pin(r: ResolvedConfig) -> cq.Workplane:
    """Captured steel pin with proud cap heads, in its own frame at the pivot."""

    span = r.lug_out_y + 0.0006
    pin = _cyl(r.pin_r, 2.0 * span, (0.0, -span, 0.0), (0.0, 1.0, 0.0))
    for sy in (-1.0, 1.0):
        base = sy * (r.lug_out_y - 0.0003)
        pin = pin.union(
            _cyl(r.pin_cap_r, 0.0016, (0.0, min(base, base + sy * 0.0016), 0.0), (0.0, 1.0, 0.0))
        )
    return pin


# --------------------------------------------------------------------------- #
# plunger geometry shared by every drive
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _PlungerSpec:
    hx: float
    hy: float
    kind: str
    bottom_z: float
    top_z: float
    center_x: float
    pivot_z: float


def _plunger_spec(r: ResolvedConfig, spec: _ChamberSpec) -> _PlungerSpec:
    fill = r.plunger_fill_ratio
    phx = min(spec.mouth_hx * fill, spec.mouth_hx - 0.0016)
    phy = min(spec.mouth_hy * fill, spec.mouth_hy - 0.0016)
    phx = max(phx, 0.0035)
    phy = max(phy, 0.0035)
    bottom = spec.rim_z - r.engage_depth_m
    top = bottom + r.plunger_thickness_m
    pivot_z = top + r.hub_radius_m + 0.0016
    return _PlungerSpec(
        hx=phx,
        hy=phy,
        kind=spec.mouth_kind,
        bottom_z=bottom,
        top_z=top,
        center_x=spec.cx,
        pivot_z=pivot_z,
    )


def _plunger_face(r: ResolvedConfig, p: _PlungerSpec) -> cq.Workplane:
    return _face_solid(
        p.kind,
        p.hx,
        p.hy,
        p.top_z - p.bottom_z,
        (p.center_x, 0.0, (p.bottom_z + p.top_z) / 2.0),
    )


def _stud_field(r: ResolvedConfig, p: _PlungerSpec) -> cq.Workplane | None:
    """Cylindrical pressing studs extruded down off the plate (005 L76-L83, L188-L202)."""

    rows = max(2, r.stud_rows)
    hu = p.hx - r.stud_radius_m - 0.0010
    hv = p.hy - r.stud_radius_m - 0.0010
    if hu <= 0.0 or hv <= 0.0:
        return None
    cols = max(2, min(int(round(rows * hu / max(hv, 1e-6))), 10))
    pu = (2.0 * hu) / (cols - 1)
    pv = (2.0 * hv) / (rows - 1)
    studs = None
    for i in range(rows):
        v = -hv + i * pv
        for j in range(cols):
            u = -hu + j * pu
            if p.kind == "circle" and u * u + v * v > min(hu, hv) ** 2:
                continue
            if p.kind == "ellipse" and (u / hu) ** 2 + (v / hv) ** 2 > 1.0:
                continue
            studs = _add(
                studs,
                _cyl(
                    r.stud_radius_m,
                    r.stud_len_m + 0.0006,
                    (p.center_x + u, v, p.bottom_z - r.stud_len_m),
                    (0.0, 0.0, 1.0),
                ),
            )
    return studs


def _plunger_stem(r: ResolvedConfig, p: _PlungerSpec, z_top: float) -> cq.Workplane:
    w = min(r.plunger_stem_w_m, 2.0 * min(p.hx, p.hy) * 0.9)
    z0 = p.top_z - 0.0015
    return _box(
        w, w, max(z_top - z0, 0.003), (p.center_x, 0.0, (z0 + max(z_top, z0 + 0.003)) / 2.0)
    )


# --------------------------------------------------------------------------- #
# plunger_drive builders -- each returns (lever_extra, plunger_solid_or_None)
# --------------------------------------------------------------------------- #
def _plunger_drive_rigid_pad_build(r: ResolvedConfig, spec: _ChamberSpec, p: _PlungerSpec):
    """Pad cast rigidly onto the lever through a stem (002 L135-L186)."""

    pad = _plunger_face(r, p)
    pad = pad.union(_plunger_stem(r, p, r.lever_bar_z0 + 0.002))
    return pad, None


def _plunger_drive_stud_plate_build(r: ResolvedConfig, spec: _ChamberSpec, p: _PlungerSpec):
    """Thin plate carrying a full grid of pressing studs (005 L188-L202)."""

    plate = _plunger_face(r, p)
    studs = _stud_field(r, p)
    if studs is not None:
        plate = plate.union(studs)
    plate = plate.union(_plunger_stem(r, p, r.lever_bar_z0 + 0.002))
    return plate, None


def _hinge_stub(r: ResolvedConfig, x: float, z: float, half_span: float, radius: float):
    return _cyl(radius, 2.0 * half_span, (x, -half_span, z), (0.0, 1.0, 0.0))


def _bored_hub(radius: float, bore: float, half_len: float, center: Vec3) -> cq.Workplane:
    hub = _cyl(
        radius, 2.0 * half_len, (center[0], center[1] - half_len, center[2]), (0.0, 1.0, 0.0)
    )
    return hub.cut(
        _cyl(
            bore,
            2.0 * half_len + 0.004,
            (center[0], center[1] - half_len - 0.002, center[2]),
            (0.0, 1.0, 0.0),
        )
    )


def _plunger_drive_self_leveling_build(r: ResolvedConfig, spec: _ChamberSpec, p: _PlungerSpec):
    """Puck on its own rivet between twin bored ears (006 L194-L210, L220-L244)."""

    hub_half = 0.0036
    ear_gap = hub_half + 0.0006  # 0.6 mm running clearance beside the hub
    ear_t = 0.0032
    ear_r = r.hub_radius_m + 0.0026
    lever = None
    for sy in (-1.0, 1.0):
        y_base = ear_gap if sy > 0 else -(ear_gap + ear_t)
        lever = _add(
            lever,
            _cyl(ear_r, ear_t, (p.center_x, y_base, p.pivot_z), (0.0, 1.0, 0.0)),
        )
    box_z0 = p.pivot_z + r.hub_radius_m + 0.0012
    box_z1 = max(r.lever_bar_z0 + 0.002, box_z0 + 0.004)
    lever = lever.union(
        _box(
            min(r.plunger_stem_w_m, 0.016),
            2.0 * (ear_gap + ear_t),
            box_z1 - box_z0,
            (p.center_x, 0.0, (box_z0 + box_z1) / 2.0),
        )
    )
    # Rivet through both ears, carried by the lever.
    lever = lever.union(_hinge_stub(r, p.center_x, p.pivot_z, ear_gap + 0.0008, r.pin_r * 0.72))
    puck = _face_solid(
        p.kind,
        p.hx * r.puck_taper_ratio,
        p.hy * r.puck_taper_ratio,
        p.top_z - p.bottom_z,
        (p.center_x, 0.0, (p.bottom_z + p.top_z) / 2.0),
    )
    # The stem runs up the back of the puck into its own hub.  ``hub_radius_m``
    # is sampled across 4.0-6.6 mm, so the stem's side faces can land exactly on
    # the hub cylinder's silhouette and fuse tangentially; keep them off it.
    stem_w = _clear_of(0.0090, 2.0 * r.hub_radius_m, 0.0012)
    puck = puck.union(
        _box(
            stem_w,
            0.0090,
            max(p.pivot_z - p.top_z + 0.002, 0.003),
            (p.center_x, 0.0, (p.top_z - 0.001 + p.pivot_z) / 2.0),
        )
    )
    puck = puck.union(
        _bored_hub(
            r.hub_radius_m,
            r.pin_r * 0.72 + _BORE_CLEARANCE,
            hub_half,
            (p.center_x, 0.0, p.pivot_z),
        )
    )
    return lever, puck


def _plunger_drive_cam_follower_build(r: ResolvedConfig, spec: _ChamberSpec, p: _PlungerSpec):
    """Cam disc on the lever running a follower roller on the plunger arm
    (cam_follower_plunger L336-L400, L403-L450).

    The cam's working face is authored as an arc concentric with the plunger
    pivot: the cam centre sits radially outboard of the roller, so the roller
    rolls along it and the joint's own travel opens the contact instead of
    driving the roller into the lobe.  The source stacks nine `allow_overlap`
    calls to hide that penetration; those are blocked here.
    """

    lever, puck = _plunger_drive_self_leveling_build(r, spec, p)
    # The cam disc is up to 22 mm across and hangs off the lever ahead of the
    # plunger pivot, i.e. straight over the clevis lugs, the cast head and the
    # chamber.  Its own radius decides how far below the lever it reaches, so it
    # is placed outboard of everything the lower frame owns at that station
    # rather than being trimmed to fit between them.
    cam_y = max(
        r.cam_offset_y_m,
        p.hy + 0.0075,
        max(_frame_reach_hy(r, spec), spec.hy) + 0.0045 + 0.0014,
    )
    roller_r = r.roller_radius_m
    arm_reach = max(r.cam_radius_m * 0.9, r.hub_radius_m + 0.0062, 0.0100)
    arm_z = p.pivot_z + r.hub_radius_m * 0.52
    # Roller centre in the plunger frame: outboard in +Y, ahead of the pivot in -X.
    roller_c = (p.center_x - arm_reach, cam_y, p.pivot_z - 0.0010)
    cam_c = (roller_c[0] - (r.cam_radius_m + roller_r + 0.0004), cam_y, roller_c[2])
    # Cam disc plus the eccentric rise lobe (outside the joint's own travel).
    cam = _cyl(r.cam_radius_m, 0.0090, (cam_c[0], cam_y - 0.0045, cam_c[2]), (0.0, 1.0, 0.0))
    cam = cam.union(
        _cyl(
            r.cam_radius_m * 0.62,
            0.0090,
            (cam_c[0] - r.cam_radius_m * 0.55, cam_y - 0.0045, cam_c[2] + r.cam_radius_m * 0.5),
            (0.0, 1.0, 0.0),
        )
    )
    cam = cam.cut(_cyl(0.0018, 0.012, (cam_c[0], cam_y - 0.006, cam_c[2]), (0.0, 1.0, 0.0)))
    # Carrier bracket back to the lever's ear block.  It runs ABOVE the whole
    # follower assembly: the source routes it straight through the plunger arm
    # and covers the result with `allow_overlap`, which is blocked here.
    bridge_z0 = p.pivot_z + r.hub_radius_m + 0.0026
    bridge_z1 = bridge_z0 + 0.0060
    cam = cam.union(
        _box(
            (p.center_x - cam_c[0]) + 0.0040,
            0.0090,
            bridge_z1 - bridge_z0,
            ((p.center_x + cam_c[0] - 0.0040) / 2.0 + 0.0020, cam_y, (bridge_z0 + bridge_z1) / 2.0),
        )
    )
    cam = cam.union(
        _box(
            0.0080,
            cam_y + 0.0045 - 0.0046,
            bridge_z1 - bridge_z0,
            (p.center_x - 0.0020, (cam_y + 0.0045 + 0.0046) / 2.0, (bridge_z0 + bridge_z1) / 2.0),
        )
    )
    # Post down from the carrier onto the cam disc.
    cam = cam.union(
        _box(
            0.0075,
            0.0075,
            max(bridge_z0 - cam_c[2], 0.003),
            (cam_c[0], cam_y, (cam_c[2] + max(bridge_z0, cam_c[2] + 0.003)) / 2.0),
        )
    )
    lever = lever.union(cam)

    # Follower: L-bracket off the plunger hub carrying the roller on an axle.
    # It has to stay clear of the lever's own ear block, which starts at
    # ``pivot_z + hub_radius + 1.2 mm``, so the bracket runs low and reaches out.
    arm = _box(
        0.0052,
        0.0060,
        r.hub_radius_m * 1.04,
        (p.center_x, 0.0, p.pivot_z + r.hub_radius_m * 0.52),
    )
    arm = arm.union(
        _box(
            arm_reach + 0.0052,
            0.0050,
            0.0042,
            (p.center_x - arm_reach / 2.0, 0.0, arm_z),
        )
    )
    arm = arm.union(
        _box(
            0.0050,
            cam_y - 0.0020,
            0.0042,
            (roller_c[0], (cam_y - 0.0020) / 2.0, arm_z),
        )
    )
    arm = arm.union(_cyl(0.0016, cam_y + 0.0060, (roller_c[0], 0.0, roller_c[2]), (0.0, 1.0, 0.0)))
    roller = _cyl(roller_r, 0.0072, (roller_c[0], cam_y - 0.0036, roller_c[2]), (0.0, 1.0, 0.0))
    roller = roller.union(
        _cyl(roller_r + 0.0006, 0.0012, (roller_c[0], cam_y - 0.0048, roller_c[2]), (0.0, 1.0, 0.0))
    )
    roller = roller.union(
        _cyl(roller_r + 0.0006, 0.0012, (roller_c[0], cam_y + 0.0036, roller_c[2]), (0.0, 1.0, 0.0))
    )
    # The follower bracket belongs to the roller visual: keeping it out of the
    # puck visual is what lets the pressing-face containment check see the face
    # footprint rather than the arm's lateral reach.
    return lever, (puck, roller.union(arm))


def _plunger_drive_toggle_link_build(r: ResolvedConfig, spec: _ChamberSpec, p: _PlungerSpec):
    """Yoke rocker plus mirrored toggle links between lever and pressing face
    (compound_toggle_link L202-L249, L252-L267, L270-L287, L465-L543).

    The source hangs its rocker off the upper handle's *bridge*, above the bar
    (rocker origin z=26 mm against a handle centred on 9.5 mm), and lets the
    stem reach the plunger through the handle -- covered there by three
    `allow_overlap` calls.  Those are blocked here, so the rocker keeps the
    source's above-the-bar station and reaches the pressing face through two
    yoke side plates that straddle the lever instead of passing through it.
    That is the same yoke the source's `_make_rocker_bracket` already builds.
    """

    span = max(r.rocker_span_m, spec.hy + 0.0050, r.arm_hy + 0.0050)
    rock_z = r.lever_bar_z1 + max(0.0055, r.rocker_lift_m * 0.6)
    rock_hub_r = 0.0055
    rock_hub_half = 0.0060
    cheek_gap = rock_hub_half + 0.0006
    cheek_t = 0.0028
    cheek_r = rock_hub_r + 0.0030
    face_hub_r = 0.0050
    face_hub_half = 0.0044
    face_gap = face_hub_half + 0.0006
    face_cheek_t = 0.0026
    link_z = p.pivot_z + 0.0090

    # ---- lever side: stub axle, two cheeks and the riser off the bar --------
    lever = _hinge_stub(r, p.center_x, rock_z, cheek_gap + 0.0008, r.pin_r * 0.72)
    for sy in (-1.0, 1.0):
        y_base = cheek_gap if sy > 0 else -(cheek_gap + cheek_t)
        lever = lever.union(_cyl(cheek_r, cheek_t, (p.center_x, y_base, rock_z), (0.0, 1.0, 0.0)))
    # The riser stops short of the rocker hub; the two fork cheeks bridge the
    # last few millimetres, which is what keeps the hub bore free.
    riser_z0 = r.lever_bar_z0 + r.lever_t * 0.35
    riser_z1 = max(rock_z - rock_hub_r - 0.0010, riser_z0 + 0.004)
    lever = lever.union(
        _box(
            0.0110,
            2.0 * (cheek_gap + cheek_t),
            riser_z1 - riser_z0,
            (p.center_x, 0.0, (riser_z0 + riser_z1) / 2.0),
        )
    )

    # ---- rocker: bored hub, crossbar, diagonals and the two yoke plates -----
    rocker = _bored_hub(
        rock_hub_r,
        r.pin_r * 0.72 + _BORE_CLEARANCE,
        rock_hub_half,
        (p.center_x, 0.0, rock_z),
    )
    rocker = rocker.union(
        _box(0.0060, 2.0 * (rock_hub_half - 0.0004), 0.0045, (p.center_x, 0.0, rock_z))
    )
    # Central post carrying the diagonals above the lever's fork cheeks.
    post_z0 = rock_z + 0.0040
    diag_z = rock_z + cheek_r + 0.0032
    rocker = rocker.union(
        _box(
            0.0058,
            2.0 * (rock_hub_half - 0.0004),
            diag_z - post_z0,
            (p.center_x, 0.0, (post_z0 + diag_z) / 2.0),
        )
    )
    for sy in (-1.0, 1.0):
        # Diagonal above the hub, out to the yoke plate station.
        rocker = rocker.union(
            _box(
                0.0050,
                span - rock_hub_half + 0.0030,
                0.0044,
                (p.center_x, sy * (span + rock_hub_half - 0.0030) / 2.0, diag_z),
            )
        )
        # Yoke side plate reaching down past the lever to the pressing face.
        plate_z0 = p.pivot_z + 0.0038
        plate_z1 = diag_z + 0.0022
        rocker = rocker.union(
            _box(
                0.0068,
                0.0038,
                plate_z1 - plate_z0,
                (p.center_x, sy * span, (plate_z0 + plate_z1) / 2.0),
            )
        )
        # Toggle-link boss with its rivet cap at the plate's mid height.
        rocker = rocker.union(
            _cyl(
                r.pin_r * 0.62,
                0.0086,
                (p.center_x, sy * span - 0.0043, link_z),
                (0.0, 1.0, 0.0),
            )
        )
    # Bottom crossbar of the yoke plus the cheeks that straddle the face hub.
    rocker = rocker.union(_box(0.0060, 2.0 * span, 0.0044, (p.center_x, 0.0, p.pivot_z + 0.0060)))
    for sy in (-1.0, 1.0):
        y_base = face_gap if sy > 0 else -(face_gap + face_cheek_t)
        rocker = rocker.union(
            _cyl(0.0078, face_cheek_t, (p.center_x, y_base, p.pivot_z), (0.0, 1.0, 0.0))
        )
    rocker = rocker.union(_hinge_stub(r, p.center_x, p.pivot_z, face_gap + 0.0008, r.pin_r * 0.62))

    # ---- flat toggle link bar, authored about its own upper pivot -----------
    link = _bored_hub(0.0034, r.pin_r * 0.62 + _BORE_CLEARANCE, 0.0026, (0.0, 0.0, 0.0))
    link = link.union(_box(0.0038, 0.0044, r.link_len_m, (0.0, 0.0, -r.link_len_m / 2.0)))
    link = link.union(_cyl(0.0034, 0.0052, (0.0, -0.0026, -r.link_len_m), (0.0, 1.0, 0.0)))
    link = link.union(_cyl(0.0019, 0.0024, (0.0, 0.0018, 0.0), (0.0, 1.0, 0.0)))

    # ---- pressing face with the source's back ribs -------------------------
    face = _plunger_face(r, p)
    face = face.union(
        _box(
            0.0080,
            0.0055,
            max(p.pivot_z - p.top_z + 0.002, 0.003),
            (p.center_x, 0.0, (p.top_z - 0.001 + p.pivot_z) / 2.0),
        )
    )
    face = face.union(
        _box(min(p.hx * 1.4, 0.020), 0.0042, 0.0032, (p.center_x, 0.0, p.top_z + 0.0012))
    )
    face = face.union(
        _box(0.0042, min(p.hy * 1.5, 0.022), 0.0032, (p.center_x, 0.0, p.top_z + 0.0012))
    )
    face = face.union(
        _bored_hub(
            face_hub_r,
            r.pin_r * 0.62 + _BORE_CLEARANCE,
            face_hub_half,
            (p.center_x, 0.0, p.pivot_z),
        )
    )
    return lever, (rocker, link, face, span, rock_z, link_z)


_PLUNGER_BUILDERS = {
    "rigid_pad": _plunger_drive_rigid_pad_build,
    "stud_plate": _plunger_drive_stud_plate_build,
    "self_leveling": _plunger_drive_self_leveling_build,
    "cam_follower": _plunger_drive_cam_follower_build,
    "toggle_link": _plunger_drive_toggle_link_build,
}


# --------------------------------------------------------------------------- #
# Screen-frame construction helpers
# --------------------------------------------------------------------------- #
def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _screen_box(
    screen: _Screen, du: float, dv: float, dn: float, cu: float, cv: float, cn: float
) -> cq.Workplane:
    """Axis-aligned box sized in screen coordinates (u, v, n are unit world axes)."""

    u, v, n = screen.u, screen.v, screen.normal
    size = tuple(abs(u[i]) * du + abs(v[i]) * dv + abs(n[i]) * dn for i in range(3))
    return _box(size[0], size[1], size[2], _screen_point(screen, cu, cv, cn))


def _screen_cyl_n(
    screen: _Screen, radius: float, length: float, cu: float, cv: float, n_start: float
) -> cq.Workplane:
    """Cylinder from ``n_start`` running along ``-normal`` (into the chamber)."""

    base = _screen_point(screen, cu, cv, n_start)
    return _cyl(radius, length, base, _vscale(screen.normal, -1.0))


def _screen_cyl_u(
    screen: _Screen, radius: float, half_len: float, cu: float, cv: float, cn: float
) -> cq.Workplane:
    base = _screen_point(screen, cu - half_len, cv, cn)
    return _cyl(radius, 2.0 * half_len, base, screen.u)


def _swing_axis(screen: _Screen) -> Vec3:
    """Rotation axis (parallel to u) that lifts a ``-v`` point in the ``+n`` sense.

    ``(u, v, n)`` handedness flips between the floor screens and the vertical
    ones, so the sign has to be read off the basis rather than hard-coded.
    """

    handed = _dot(_cross(screen.u, screen.v), screen.normal)
    return screen.u if handed < 0.0 else _vscale(screen.u, -1.0)


def _module_screen(r: ResolvedConfig, spec: _ChamberSpec) -> _Screen:
    """The band of a screen an externally mounted module may actually occupy.

    ``swing_cleaner`` and ``sliding_ejector`` both hang a body off the *outside*
    of the screen and carry hardware past one of its ``v`` edges: the cleaner's
    strap, bored bosses and axle sit beyond the edge exactly as
    ``swing_cleaner_grid`` L223-L228 places its strap at ``y = 25`` and the two
    bored rings at ``y = 29``, i.e. just off the plate the strap is cast to.

    On the five floor screens that edge points sideways at the bottom of the cup
    and everything past it is free air, so the screen is returned unchanged.
    The two vertical screens are not free:

    * 001's drum (``drum_face``) pierces the same circular end plate that the
      loading-mouth box cut removes above ``rim_z``.  Anything the module puts
      above that plane is cast onto nothing and floats off the part.
    * 002's front wall (``loft_hopper``) is covered end to end by the cast nose
      head, which runs from the clevis to the chamber front at ``z >= -arm_t``.

    Both therefore publish a sub-band, and the band's ``v`` is *flipped* so the
    hardware the module carries past its own edge hangs into the free air below
    the chamber instead of into the casting (or the open mouth) above it.  With
    the hinge at the low edge the swept envelope of the flap is bounded by its
    rest pose, so clearing the band clears the whole motion.
    """

    screen = spec.screen
    if abs(screen.normal[2]) > 0.5:
        return screen

    origin_v = screen.origin[2]
    # Top of the band: backed by chamber skin, and clear of the cast nose head
    # when the head runs across this face.
    v_hi = min(screen.hv + 0.0010, (spec.rim_z - origin_v) - 0.0010)
    if abs(screen.normal[0]) > 0.5:
        v_hi = min(v_hi, (-r.arm_t - 0.0018) - origin_v)
    # Bottom of the band: the strap is 4 mm tall and bites 0.5 mm into the skin,
    # so it may hang 1.6 mm below the chamber's own outer bottom and still weld.
    v_lo = max((spec.bottom_z - origin_v) - 0.0016, v_hi - 2.0 * screen.hv)
    v_c = 0.5 * (v_hi + v_lo)
    # ``plate_hv`` is allowed to overshoot ``hv`` by 1 mm, so the half extent
    # published here is the band minus that overshoot.
    half = max(0.5 * (v_hi - v_lo) - 0.0010, 0.0015)
    return _Screen(
        origin=_vadd(screen.origin, _vscale(screen.v, v_c)),
        normal=screen.normal,
        u=screen.u,
        v=_vscale(screen.v, -1.0),
        hu=screen.hu,
        hv=half,
        thickness=screen.thickness,
        holes=tuple((u_pt, v_c - v_pt) for u_pt, v_pt in screen.holes),
        hole_r=screen.hole_r,
        clip="rect",
    )


def _cavity_depth_along_n(r: ResolvedConfig, spec: _ChamberSpec) -> float:
    n = spec.screen.normal
    if abs(n[2]) > 0.5:
        return max((spec.rim_z - spec.cavity_floor_z) - r.engage_depth_m - 0.0018, 0.0035)
    if abs(n[1]) > 0.5:
        return max(2.0 * spec.hy * 0.72, 0.0035)
    return max(2.0 * spec.hx * 0.62, 0.0035)


# --------------------------------------------------------------------------- #
# accessory -- hang_loop   (003 L241-L248)
# --------------------------------------------------------------------------- #
def _accessory_hang_loop_build(r: ResolvedConfig, spec: _ChamberSpec):
    tip_z = (r.lever_bar_z0 + r.lever_bar_z1) / 2.0
    reach = r.loop_radius_m + r.loop_tube_m
    centre = (r.lever_tail_x + reach - 0.0012, 0.0, tip_z)
    loop = _wp(
        cq.Solid.makeTorus(
            r.loop_radius_m,
            r.loop_tube_m,
            pnt=cq.Vector(*centre),
            dir=cq.Vector(0.0, 1.0, 0.0),
        )
    )
    return {"lever_extra": loop}


# --------------------------------------------------------------------------- #
# accessory -- swing_cleaner   (swing_cleaner_grid L223-L228, L231-L246, L249-L281)
# --------------------------------------------------------------------------- #
def _accessory_swing_cleaner_build(r: ResolvedConfig, spec: _ChamberSpec):
    screen = _module_screen(r, spec)
    hu, hv = screen.hu, screen.hv
    plate_t = r.cleaner_plate_t_m
    pin_len = r.cleaner_pin_len_m
    gap = 0.0006
    plate_n = gap + pin_len + plate_t / 2.0
    hinge_v = hv + 0.0062
    axle_r = 0.0022
    boss_u = hu * 0.78

    # Frame-side strap and two bored bosses (001 `_make_cleaner_mount` L223-L228).
    mount = _screen_box(screen, 2.0 * hu * 0.86, 0.0040, 0.0030, 0.0, hv - 0.0004, 0.0010)
    for su in (-1.0, 1.0):
        mount = mount.union(
            _screen_box(
                screen,
                0.0042,
                0.0072,
                plate_n + 0.0042,
                su * boss_u,
                hv + 0.0030,
                (plate_n + 0.0042) / 2.0 - 0.0012,
            )
        )
    mount = mount.cut(
        _screen_cyl_u(screen, axle_r + _BORE_CLEARANCE, hu * 1.2, 0.0, hinge_v, plate_n)
    )

    # Cleaner: axle, two mounting arms, backing plate and the registered pin field.
    hinge_pt = _screen_point(screen, 0.0, hinge_v, plate_n)
    cleaner = _screen_cyl_u(screen, axle_r, boss_u + 0.0028, 0.0, hinge_v, plate_n)
    for su in (-1.0, 1.0):
        cleaner = cleaner.union(
            _screen_box(
                screen,
                0.0045,
                hinge_v - hv * 0.55,
                plate_t,
                su * hu * 0.62,
                (hinge_v + hv * 0.55) / 2.0,
                plate_n,
            )
        )
    ehu, ehv = _hole_extents(screen)
    pin_r = max(screen.hole_r * 0.62, 0.00055)
    plate_hu = min(max(ehu + pin_r + 0.0012, hu * 0.55), hu + 0.0010)
    plate_hv = min(max(min(ehv, hv) + pin_r + 0.0012, hv * 0.55), hv + 0.0010)
    cleaner = cleaner.union(
        _screen_box(screen, 2.0 * plate_hu, 2.0 * plate_hv, plate_t, 0.0, 0.0, plate_n)
    )
    pins = None
    for u_pt, v_pt in screen.holes:
        if abs(u_pt) > plate_hu - pin_r - 0.0004 or abs(v_pt) > plate_hv - pin_r - 0.0004:
            continue
        pins = _add(
            pins,
            _screen_cyl_n(
                screen, pin_r, pin_len + 0.0008, u_pt, v_pt, plate_n - plate_t / 2.0 + 0.0006
            ),
        )
    if pins is not None:
        cleaner = cleaner.union(pins)
    cleaner = cleaner.translate(_vscale(hinge_pt, -1.0))
    return {
        "frame_extra": mount,
        "part": ("cleaner", cleaner, "cleaning_module"),
        "joint": {
            "name": "frame_to_cleaner",
            "point": hinge_pt,
            "axis": _swing_axis(screen),
            "radius": axle_r,
            "lower": 0.0,
            "upper": r.cleaner_open_rad,
            "type": ArticulationType.REVOLUTE,
        },
    }


# --------------------------------------------------------------------------- #
# accessory -- sliding_ejector   (sliding_ejector_plate L74-L87, L183-L214, L281-L319)
# --------------------------------------------------------------------------- #
def _accessory_sliding_ejector_build(r: ResolvedConfig, spec: _ChamberSpec):
    screen = _module_screen(r, spec)
    hu, hv = screen.hu, screen.hv
    travel = r.ejector_travel_m
    plate_t = 0.0022
    plate_n0 = travel + 0.0009
    plate_nc = plate_n0 + plate_t / 2.0
    pin_len = plate_n0 + screen.thickness - 0.0004
    pin_r = max(screen.hole_r * r.ejector_pin_ratio, 0.00050)
    rail_u = max(min(hu * r.rail_span_ratio, hu - 0.0022), screen.hole_r + 0.0024)
    if screen.clip == "circle":
        rail_u = min(rail_u, min(hu, hv) - 0.0022)
    rail_r = 0.0013
    rail_top = plate_n0 + plate_t + 0.0030

    rails = None
    for su in (-1.0, 1.0):
        rails = _add(
            rails,
            _screen_cyl_n(screen, rail_r, rail_top + 0.0030, su * rail_u, 0.0, rail_top),
        )
        # Retention shoulder the disc rests on at the retracted position.
        rails = rails.union(
            _screen_cyl_n(screen, 0.0030, 0.0010, su * rail_u, 0.0, plate_n0 + plate_t + 0.0014)
        )
        # Stop head at the far end.
        rails = rails.union(_screen_cyl_n(screen, 0.0021, 0.0011, su * rail_u, 0.0, rail_top))

    ehu, ehv = _hole_extents(screen)
    circular = screen.clip == "circle" and abs(screen.normal[2]) > 0.5
    if circular and screen.holes:
        erad = max(math.hypot(u, v) for u, v in screen.holes)
        ehu = ehv = erad
    plate_hu = min(max(ehu + pin_r + 0.0014, hu * 0.55), hu - 0.0004)
    plate_hv = min(max(min(ehv, hv) + pin_r + 0.0014, hv * 0.55), hv - 0.0004)
    plate_centre = _screen_point(screen, 0.0, 0.0, plate_nc)
    plate = _face_solid_screen(screen, plate_hu, plate_hv, plate_t, 0.0, 0.0, plate_nc, spec)
    for su in (-1.0, 1.0):
        plate = plate.cut(
            _screen_cyl_n(
                screen, rail_r + 0.00040, plate_t + 0.004, su * rail_u, 0.0, plate_nc + plate_t
            )
        )
    pins = None
    for u_pt, v_pt in screen.holes:
        # A pin that overhangs its own disc is a floating island, not a pin.
        if circular:
            if math.hypot(u_pt, v_pt) > min(plate_hu, plate_hv) - pin_r - 0.0004:
                continue
        elif abs(u_pt) > plate_hu - pin_r - 0.0004 or abs(v_pt) > plate_hv - pin_r - 0.0004:
            continue
        # ... nor one standing over a guide-rail clearance hole, which has no
        # plate under it to be rooted in.
        if any(
            math.hypot(u_pt - su * rail_u, v_pt) < rail_r + pin_r + 0.0010 for su in (-1.0, 1.0)
        ):
            continue
        pins = _add(
            pins,
            _screen_cyl_n(screen, pin_r, pin_len, u_pt, v_pt, plate_n0 + 0.0004),
        )
    if pins is not None:
        plate = plate.union(pins)
    # Thumb tab for manual actuation (L311-L317).
    plate = plate.union(
        _screen_box(screen, 0.0080, 0.0080, 0.0026, 0.0, plate_hv + 0.0028, plate_nc)
    )
    plate = plate.translate(_vscale(plate_centre, -1.0))
    return {
        "frame_extra": rails,
        "part": ("ejector", plate, "cleaning_module"),
        "joint": {
            "name": "frame_to_ejector",
            "point": plate_centre,
            "axis": _vscale(screen.normal, -1.0),
            "radius": rail_r + 0.0004,
            "lower": 0.0,
            "upper": travel,
            "type": ArticulationType.PRISMATIC,
        },
    }


def _face_solid_screen(
    screen: _Screen,
    hu: float,
    hv: float,
    thickness: float,
    cu: float,
    cv: float,
    cn: float,
    spec: _ChamberSpec,
) -> cq.Workplane:
    if screen.clip == "circle" and abs(screen.normal[2]) > 0.5:
        return _cyl(
            min(hu, hv),
            thickness,
            _screen_point(screen, cu, cv, cn + thickness / 2.0),
            _vscale(screen.normal, -1.0),
        )
    return _screen_box(screen, 2.0 * hu, 2.0 * hv, thickness, cu, cv, cn)


# --------------------------------------------------------------------------- #
# accessory -- lift_out_insert   (removable_basket L206-L260, L263-L281)
# --------------------------------------------------------------------------- #
def _accessory_lift_out_insert_build(r: ResolvedConfig, spec: _ChamberSpec):
    screen = spec.screen
    hu, hv = screen.hu, screen.hv
    t = r.insert_thickness_m
    plate_n = -(screen.thickness + 0.0012 + t / 2.0)
    usable_hv = max(min(hv, spec.liner_hv), 0.0035)
    plate_hv = max(usable_hv * r.insert_fill_ratio, 0.0030)
    hinge_v = plate_hv
    # Half width of the cavity at the hinge station: a rectangular liner in a
    # round cup has to be inscribed, or its hinge bosses land outside the wall.
    if screen.clip == "circle":
        wall_hu = math.sqrt(max(hu * hu - hinge_v * hinge_v, (0.35 * hu) ** 2))
    elif screen.clip == "ellipse":
        wall_hu = hu * math.sqrt(max(1.0 - (hinge_v / max(hv, 1e-6)) ** 2, 0.1225))
    else:
        wall_hu = hu
    plate_hu = max(wall_hu - 0.0034, 0.0035)
    boss_r = 0.0016
    boss_u = plate_hu + 0.0028

    # Pivot bosses and ribs cast on the cavity walls (L263-L281).
    bosses = None
    for su in (-1.0, 1.0):
        base = _screen_point(screen, su * (boss_u + 0.0012), hinge_v, plate_n)
        bosses = _add(
            bosses,
            _cyl(boss_r, 0.0034, base, _vscale(screen.u, -su)),
        )
        bosses = bosses.union(
            _screen_box(screen, 0.0035, 0.0040, 0.0035, su * (boss_u + 0.0006), hinge_v, plate_n)
        )

    hinge_pt = _screen_point(screen, 0.0, hinge_v, plate_n)
    insert = _screen_box(screen, 2.0 * plate_hu, 2.0 * plate_hv, t, 0.0, 0.0, plate_n)
    # The insert's own field is far tighter than the chamber screen's: it is the
    # same `screen_rows` laid into a plate that is a fraction of the screen's
    # footprint.  The hole radius therefore has to be re-derived against *this*
    # pitch.  L226-L239 of the source drills r = 0.85 mm on a 3.5 mm pitch, i.e.
    # it leaves 1.8 mm of ligament; two cut cylinders that reach each other here
    # would instead merge into a slot and dice the plate into strips, and the
    # liner is one part, so the strips become islands.
    holes: tuple[tuple[float, float], ...] = ()
    hole_r = 0.0
    rows = max(3, r.screen_rows)
    while rows >= 2:
        field = _lattice_points(plate_hu, plate_hv, rows, screen.hole_r, stagger=True, clip="rect")
        radius = min(screen.hole_r * 0.85, 0.5 * (_min_pitch(field) - _INSERT_LIGAMENT))
        if radius >= 0.00040:
            holes, hole_r = field, radius
            break
        rows -= 1
    cut = None
    for u_pt, v_pt in holes:
        cut = _add(
            cut,
            _screen_cyl_n(screen, hole_r, t + 0.004, u_pt, v_pt, plate_n + t),
        )
    if cut is not None:
        insert = insert.cut(cut)
    for su in (-1.0, 1.0):
        # Hinge ear reaching out to the wall boss.  The bore only eats the outer
        # half of the ear, so the inner half still welds into the plate.
        ear = _screen_box(
            screen, 0.0074, 0.0058, 0.0052, su * (plate_hu + 0.0006), hinge_v, plate_n
        )
        ear = ear.cut(
            _cyl(
                boss_r + _BORE_CLEARANCE,
                0.0038,
                _screen_point(screen, su * (plate_hu + 0.0043), hinge_v, plate_n),
                _vscale(screen.u, -su),
            )
        )
        insert = insert.union(ear)
        # Latch tab at the free end that snaps over the rim (L251-L258).
        insert = insert.union(
            _screen_box(
                screen,
                0.0038,
                0.0030,
                0.0050,
                su * plate_hu * 0.72,
                -plate_hv - 0.0012,
                plate_n - 0.0008,
            )
        )
    insert = insert.translate(_vscale(hinge_pt, -1.0))

    room = _cavity_depth_along_n(r, spec)
    span = 2.0 * plate_hv
    lift = math.asin(min(max(room / max(span, 1e-6), 0.24), 0.94))
    return {
        "frame_extra": bosses,
        "part": ("chamber_liner", insert, "chamber_liner"),
        "joint": {
            "name": "frame_to_liner",
            "point": hinge_pt,
            "axis": _vscale(_swing_axis(screen), -1.0),
            "radius": boss_r,
            "lower": 0.0,
            "upper": min(lift, r.insert_lift_rad),
            "type": ArticulationType.REVOLUTE,
        },
    }


# --------------------------------------------------------------------------- #
# accessory -- storage_latch   (handle_storage_latch L85-L98, L235-L328)
# --------------------------------------------------------------------------- #
def _accessory_storage_latch_build(r: ResolvedConfig, spec: _ChamberSpec):
    capture_x = r.lever_tail_x - 0.0080
    pin_z = (r.lever_bar_z0 + r.lever_bar_z1) / 2.0
    latch_z = _clamp(pin_z - r.latch_arm_len_m, 0.0020, max(pin_z - 0.0075, 0.0025))
    latch_x = capture_x - 0.0110
    arm_y = r.arm_hy + 0.0058
    barrel_r = 0.0022
    # The bracket ears have to stand ON the lower arm, so their lateral station
    # is read off the arm's own half width at the latch station.
    bar_half = r.arm_hy * r.arm_taper_ratio
    barrel_half = _clamp(bar_half * 0.52, 0.0026, 0.0068)

    ears = None
    for sy in (-1.0, 1.0):
        ears = _add(
            ears,
            _box(
                0.0072,
                0.0028,
                latch_z + r.arm_t * 0.75 + 0.0040,
                (
                    latch_x,
                    sy * (barrel_half + 0.0016),
                    (latch_z + 0.0040 - r.arm_t * 0.75) / 2.0,
                ),
            ),
        )
    # Saddle tying both ears together inside the arm body.
    ears = ears.union(
        _box(
            0.0072,
            2.0 * (barrel_half + 0.0030),
            r.arm_t * 0.42,
            (latch_x, 0.0, -r.arm_t * 0.55),
        )
    )
    ears = ears.cut(
        _cyl(
            barrel_r + _BORE_CLEARANCE,
            0.030,
            (latch_x, -0.015, latch_z),
            (0.0, 1.0, 0.0),
        )
    )
    # Capture pin protruding from the +Y side of the lever bar (L263-L273).
    # The pin is rooted on the lever's centreline so it always welds into the
    # bar whatever the bar's taper and section are, then protrudes past +Y.
    capture = _cyl(
        r.capture_pin_r_m,
        arm_y + 0.0034,
        (capture_x, 0.0, pin_z),
        (0.0, 1.0, 0.0),
    )
    capture = capture.union(
        _cyl(
            r.capture_pin_r_m * 1.7,
            0.0012,
            (capture_x, arm_y + 0.0022, pin_z),
            (0.0, 1.0, 0.0),
        )
    )

    arm_h = (pin_z - latch_z) + r.capture_pin_r_m + 0.0030
    latch = _cyl(barrel_r, 2.0 * barrel_half, (0.0, -barrel_half, 0.0), (0.0, 1.0, 0.0))
    # The bridge to the side arm and the release tab both sit on the +X side of
    # the barrel: the arm leans back as the latch releases, so anything on the
    # -X side would swing down into the lower handle.
    latch = latch.union(_box(0.0060, 2.0 * barrel_half * 0.9, 0.0044, (0.0015, 0.0, 0.0)))
    latch = latch.union(
        _box(0.0042, arm_y - 0.0010, 0.0055, (0.0060, (arm_y + 0.0038) / 2.0, 0.0008))
    )
    latch = latch.union(_box(0.0038, 0.0034, arm_h, (0.0060, arm_y, arm_h / 2.0 - 0.0012)))
    # Hook lip curling back over the capture pin.
    latch = latch.union(_box(0.0099, 0.0040, 0.0024, (0.00905, arm_y - 0.0004, arm_h - 0.0012)))
    # Release tab outboard on the +X side so it rises, never dips into the arm.
    tab = _box(0.0080, 0.0060, 0.0028, (0.0113, 0.0, 0.0))
    return {
        "frame_extra": ears,
        "lever_extra": capture,
        "part": ("storage_latch", latch, "storage_latch"),
        "part_accent": tab,
        "joint": {
            "name": "frame_to_latch",
            "point": (latch_x, 0.0, latch_z),
            "axis": (0.0, -1.0, 0.0),
            "radius": barrel_r,
            "lower": 0.0,
            "upper": r.latch_release_rad,
            "type": ArticulationType.REVOLUTE,
        },
    }


# --------------------------------------------------------------------------- #
# accessory -- flip_basket   (flip_out_basket L132-L165, L244-L268)
# --------------------------------------------------------------------------- #
def _accessory_flip_basket_build(r: ResolvedConfig, spec: _ChamberSpec):
    # Keep the hinge inside the chamber's own bottom plate: that is the one
    # station where every one of the seven chamber shells is solid, so the
    # barrel's tie web always welds into the shell.  `_build_frame_body` reads
    # the same station so the welded frame can stand clear of the barrel.
    hinge_x, hinge_z, barrel_half = _flip_hinge(r, spec)
    cradle_y = spec.hy + 0.0006 + r.cradle_plate_t_m / 2.0
    pin_r = 0.0022

    cradle = None
    for sy in (-1.0, 1.0):
        cradle = _add(
            cradle,
            _box(
                0.0130,
                r.cradle_plate_t_m,
                -hinge_z + 0.0060,
                (hinge_x, sy * cradle_y, (hinge_z - 0.0035) / 2.0),
            ),
        )
    cradle = cradle.union(
        _cyl(
            pin_r,
            2.0 * (cradle_y + r.cradle_plate_t_m),
            (hinge_x, -(cradle_y + r.cradle_plate_t_m), hinge_z),
            (0.0, 1.0, 0.0),
        )
    )
    barrel = _bored_hub(0.0044, pin_r + _BORE_CLEARANCE, barrel_half, (hinge_x, 0.0, hinge_z))
    # Tie web from the barrel back into the chamber's bottom plate.
    barrel = barrel.union(
        _box(
            hinge_x - spec.cx + 0.0044,
            2.0 * barrel_half,
            max(2.0 * (hinge_z - spec.bottom_z) + 0.0012, 0.0035),
            ((spec.cx + hinge_x + 0.0022) / 2.0, 0.0, hinge_z),
        )
    )
    return {
        "frame_extra": cradle,
        "chamber_barrel": barrel,
        "joint": {
            "name": "frame_to_chamber",
            "point": (hinge_x, 0.0, hinge_z),
            "axis": (0.0, -1.0, 0.0),
            "radius": pin_r,
            "lower": 0.0,
            "upper": r.flip_rad,
            "type": ArticulationType.REVOLUTE,
        },
    }


_ACCESSORY_BUILDERS = {
    "hang_loop": _accessory_hang_loop_build,
    "swing_cleaner": _accessory_swing_cleaner_build,
    "sliding_ejector": _accessory_sliding_ejector_build,
    "storage_latch": _accessory_storage_latch_build,
    "lift_out_insert": _accessory_lift_out_insert_build,
    "flip_basket": _accessory_flip_basket_build,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def _axis_mate(name_a: str, point: Vec3, axis: Vec3, name_b: str, radius: float):
    radial = (0.0, 0.0, 1.0) if abs(axis[2]) < 0.5 else (1.0, 0.0, 0.0)
    return mate_axes(
        AxisInterface(name=name_a, point=point, axis=axis, radial=radial, radius=radius),
        AxisInterface(
            name=name_b, point=(0.0, 0.0, 0.0), axis=axis, radial=radial, radius=radius * 0.92
        ),
    )


def _open_travel(r: ResolvedConfig, spec: _ChamberSpec, p: _PlungerSpec) -> float:
    """Lever travel that lifts the pressing face clear of the chamber rim.

    The face's lowest point rides a circle of radius ``R`` about the pivot; the
    joint has to turn far enough that it clears ``rim + 6 mm`` before the sweep
    can reach the wall.
    """

    dx = p.center_x
    dz = p.bottom_z - r.pivot_z
    radius = math.hypot(dx, dz)
    phi = math.atan2(dz, dx)
    target = spec.top_z + 0.0065 - r.pivot_z
    if radius <= 1e-6:
        return r.open_rad
    ratio = min(max(target / radius, -0.98), 0.98)
    needed = math.asin(ratio) - phi
    return float(min(max(r.open_rad, needed + 0.05), 1.75))


def _rocker_ratio(r: ResolvedConfig, p: _PlungerSpec, rock_z: float, open_rad: float) -> float:
    """Mimic ratio from the squeeze hinge to the yoke rocker.

    The compound toggle exists to add pressing travel: ``compound_toggle_link``
    L474-L479 says the rocker "pushes arm tips forward, amplifying the pressing
    motion", and L525-L543 hangs the pressing face on the same rocker so that
    forward push lands on the face.  What the source amplifies is a *stroke*, and
    the yoke delivers it on a circle of radius ``reach`` about the rocker hub, so
    the swing angle has to be solved from the stroke and that radius.

    ``rocker_mult`` is therefore the share of the plunger's own engagement into
    the chamber that the toggle adds on top of the hinge's travel: 20-46 % of
    ``engage_depth_m``, i.e. 0.3-2.9 mm of extra face travel.  Reading it instead
    as a bare angle ratio -- ``rocker_mult * open_rad`` straight into the mimic --
    ignored ``reach`` entirely and drove the face 10-25 mm along the lever, past
    the 6-24 mm pocket between the pressing face and the lever's neck, so the face
    landed inside the neck block near the open limit.
    """

    reach = max(rock_z - p.pivot_z, 0.0010)
    stroke = r.rocker_mult * r.engage_depth_m
    swing = 2.0 * math.asin(min(stroke / (2.0 * reach), 0.5))
    return float(swing / max(open_rad, 1e-6))


def _arm_face_offsets(r: ResolvedConfig) -> tuple[float, float]:
    """(lower arm underside, lever bar top) for the two grip pads."""

    if r.arm_profile == "lofted_ellipse":
        return (-0.92 * r.arm_t, r.lever_bar_z0 + r.lever_t * 0.5 + r.lever_t * 0.42)
    return (-r.arm_t, r.lever_bar_z1)


def _build_lever_body(r: ResolvedConfig) -> cq.Workplane:
    """Knuckle, neck between the lugs and the raised bar, in world coordinates."""

    knuckle_half = r.lug_in_y - 0.0005
    body = _cyl(r.knuckle_r, 2.0 * knuckle_half, (0.0, -knuckle_half, r.pivot_z), (0.0, 1.0, 0.0))
    neck_x0 = -r.knuckle_r * 0.6
    neck_x1 = _LUG_X1 + 0.0045
    neck_z0 = r.pivot_z - r.knuckle_r * 0.45
    neck_z1 = r.lever_bar_z1
    # The neck reaches as wide as the lug window allows, but ``lug_in_y`` and
    # ``arm_half_width_m`` are independent, so that width can land exactly on the
    # bar section's own half width and the two solids would fuse tangentially.
    # Whichever way it is pushed it still has to clear the frame's lug faces.
    neck_half = min(
        max(
            0.0035,
            _clear_of(
                r.lug_in_y - 0.0006,
                _arm_start_half_y(
                    r, r.arm_hy * 0.94, r.arm_hy * 0.94 * r.arm_taper_ratio, r.lever_t / 2.0
                ),
                0.0004,
            ),
        ),
        r.lug_in_y - 0.0002,
    )
    body = body.union(
        _box(
            neck_x1 - neck_x0,
            2.0 * neck_half,
            neck_z1 - neck_z0,
            ((neck_x0 + neck_x1) / 2.0, 0.0, (neck_z0 + neck_z1) / 2.0),
        )
    )
    body = body.cut(
        _cyl(
            r.pin_r + _BORE_CLEARANCE,
            2.0 * (knuckle_half + 0.003),
            (0.0, -(knuckle_half + 0.003), r.pivot_z),
            (0.0, 1.0, 0.0),
        )
    )
    bar_z = (r.lever_bar_z0 + r.lever_bar_z1) / 2.0
    bar = _arm_body(
        r,
        _LUG_X1,
        r.lever_tail_x,
        bar_z,
        r.arm_hy * 0.94,
        r.arm_hy * 0.94 * r.arm_taper_ratio,
        r.lever_t / 2.0,
    )
    return body.union(bar)


def build_pictureX_0611_garlic_press(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    spec, chamber_solids = _build_chamber(r)
    p = _plunger_spec(r, spec)
    acc = _ACCESSORY_BUILDERS[r.accessory](r, spec)
    open_rad = _open_travel(r, spec, p)

    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_garlic_press",
            "slot_choices": tuple(slot_choices_for_config(r).items()),
            "screen_holes": len(spec.screen.holes),
            "source_pool_reviewed": "17 workbench records / rev_000001",
        },
    )
    for key, rgba in r.palette.items():
        model.material(key, rgba=rgba)

    # ---------------- lower frame ------------------------------------------
    frame = model.part(
        "press_frame",
        meta={
            "role": "press_frame",
            "chamber": r.chamber,
            "arm_profile": r.arm_profile,
            "screen_rows": r.screen_rows,
        },
    )
    frame_body = _build_frame_body(r, spec)
    frame.visual(
        _mesh(frame_body, f"frame__{r.arm_profile}__body"),
        material="body",
        name=f"frame__{r.arm_profile}__body", material_class_id=("metal.aluminum_bare" if r.palette_style in {"cast_aluminium", "brushed_stainless", "polished_steel", "dark_anodised"} else "metal.blackened_gunmetal"),
    )
    if not r.flip_chamber:
        for local_name, solid, mat in chamber_solids:
            frame.visual(
                _mesh(solid, f"chamber__{r.chamber}__{local_name}"),
                material=mat,
                name=f"chamber__{r.chamber}__{local_name}", material_class_id="metal.patterned_sheet_panel",
            )
    lower_face, upper_face = _arm_face_offsets(r)
    lower_grip = _grip_pad(r, r.tail_x, lower_face, r.arm_hy * r.arm_taper_ratio, upward=False)
    if lower_grip is not None:
        frame.visual(
            _mesh(lower_grip, f"frame__{r.arm_profile}__grip"),
            material="grip",
            name=f"frame__{r.arm_profile}__grip", material_class_id="rubber.smooth_plain",
        )
    if acc.get("frame_extra") is not None:
        frame.visual(
            _mesh(acc["frame_extra"], f"accessory__{r.accessory}__mount"),
            material="hardware",
            name=f"accessory__{r.accessory}__mount", material_class_id="metal.chrome_polished",
        )

    # ---------------- captured hinge pin ------------------------------------
    pin_part = model.part("pivot_pin", meta={"role": "hinge_pin"})
    pin_part.visual(
        _mesh(_build_pivot_pin(r), "hinge__pin__shaft"),
        material="hardware",
        name="hinge__pin__shaft", material_class_id="metal.chrome_polished",
    )
    model.articulation(
        "frame_to_pin",
        ArticulationType.FIXED,
        parent=frame,
        child=pin_part,
        origin=Origin(xyz=(0.0, 0.0, r.pivot_z)),
        meta={"role": "captured pivot pin"},
    )

    # ---------------- upper lever ------------------------------------------
    lever = model.part(
        "lever_arm",
        meta={"role": "press_lever", "plunger_drive": r.plunger_drive},
    )
    lever_body = _build_lever_body(r)
    plunger_lever_extra, plunger_payload = _PLUNGER_BUILDERS[r.plunger_drive](r, spec, p)
    if acc.get("lever_extra") is not None:
        lever_body = lever_body.union(acc["lever_extra"])
    lever_body = lever_body.translate((0.0, 0.0, -r.pivot_z))
    lever.visual(
        _mesh(lever_body, f"lever__{r.arm_profile}__body"),
        material="body",
        name=f"lever__{r.arm_profile}__body", material_class_id=("metal.aluminum_bare" if r.palette_style in {"cast_aluminium", "brushed_stainless", "polished_steel", "dark_anodised"} else "metal.blackened_gunmetal"),
    )
    if plunger_lever_extra is not None:
        lever.visual(
            _mesh(
                plunger_lever_extra.translate((0.0, 0.0, -r.pivot_z)),
                f"plunger_drive__{r.plunger_drive}__face",
            ),
            material="hardware" if r.separate_plunger else "body",
            name=(
                f"plunger_drive__{r.plunger_drive}__mount"
                if r.separate_plunger
                else f"plunger_drive__{r.plunger_drive}__face"
            ), material_class_id=("metal.chrome_polished" if r.plunger_drive in {"self_leveling", "cam_follower", "toggle_link"} else "metal.aluminum_bare"),
        )
    upper_grip = _grip_pad(
        r, r.lever_tail_x, upper_face, r.arm_hy * 0.94 * r.arm_taper_ratio, upward=True
    )
    if upper_grip is not None:
        lever.visual(
            _mesh(upper_grip.translate((0.0, 0.0, -r.pivot_z)), f"lever__{r.arm_profile}__grip"),
            material="grip",
            name=f"lever__{r.arm_profile}__grip", material_class_id="rubber.smooth_plain",
        )

    lever_mate = _axis_mate(
        "frame.hinge_axis",
        (0.0, 0.0, r.pivot_z),
        (0.0, -1.0, 0.0),
        "lever.knuckle_axis",
        r.pin_r + _BORE_CLEARANCE,
    )
    lever_joint = model.articulation(
        "frame_to_lever",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=lever,
        origin=lever_mate.origin,
        axis=lever_mate.axis,
        motion_limits=MotionLimits(effort=180.0, velocity=3.0, lower=0.0, upper=open_rad),
        meta={"role": "squeeze hinge", "positive_motion": "opens the two hand arms"},
    )
    register_interface_mate(model, lever_joint.name, lever_mate)

    # ---------------- separate plunger bodies -------------------------------
    if r.plunger_drive in {"self_leveling", "cam_follower"}:
        plunger = model.part("plunger", meta={"role": "pressing_plunger", "drive": r.plunger_drive})
        if r.plunger_drive == "cam_follower":
            puck, roller = plunger_payload
        else:
            puck, roller = plunger_payload, None
        shift = (-p.center_x, 0.0, -p.pivot_z)
        plunger.visual(
            _mesh(puck.translate(shift), f"plunger_drive__{r.plunger_drive}__puck"),
            material="body",
            name=f"plunger_drive__{r.plunger_drive}__puck", material_class_id=("metal.aluminum_bare" if r.palette_style in {"cast_aluminium", "brushed_stainless", "polished_steel", "dark_anodised"} else "metal.blackened_gunmetal"),
        )
        if roller is not None:
            plunger.visual(
                _mesh(roller.translate(shift), f"plunger_drive__{r.plunger_drive}__roller"),
                material="hardware",
                name=f"plunger_drive__{r.plunger_drive}__roller", material_class_id="metal.chrome_polished",
            )
        mate = _axis_mate(
            "lever.plunger_axis",
            (p.center_x, 0.0, p.pivot_z - r.pivot_z),
            (0.0, -1.0, 0.0),
            "plunger.hub_axis",
            r.pin_r * 0.72 + _BORE_CLEARANCE,
        )
        joint = model.articulation(
            "lever_to_plunger",
            ArticulationType.REVOLUTE,
            parent=lever,
            child=plunger,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(
                effort=90.0, velocity=3.0, lower=-r.tilt_rad, upper=r.tilt_rad
            ),
            meta={"role": "self-levelling pressing face"},
        )
        register_interface_mate(model, joint.name, mate)

    elif r.plunger_drive == "toggle_link":
        rocker_solid, link_solid, face_solid, span, rock_z, link_z = plunger_payload
        # The yoke's swing is the stroke it adds to the press divided by its own
        # moment arm; see ``_rocker_ratio``.
        rocker_ratio = _rocker_ratio(r, p, rock_z, open_rad)
        rocker = model.part("toggle_rocker", meta={"role": "toggle_rocker"})
        rocker.visual(
            _mesh(
                rocker_solid.translate((-p.center_x, 0.0, -rock_z)),
                "plunger_drive__toggle_link__rocker",
            ),
            material="hardware",
            name="plunger_drive__toggle_link__rocker", material_class_id="metal.chrome_polished",
        )
        mate = _axis_mate(
            "lever.rocker_axis",
            (p.center_x, 0.0, rock_z - r.pivot_z),
            (0.0, -1.0, 0.0),
            "rocker.hub_axis",
            r.pin_r * 0.72 + _BORE_CLEARANCE,
        )
        joint = model.articulation(
            "lever_to_rocker",
            ArticulationType.REVOLUTE,
            parent=lever,
            child=rocker,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(
                effort=200.0,
                velocity=3.0,
                lower=-rocker_ratio * open_rad - 0.05,
                upper=0.05,
            ),
            mimic=Mimic(joint="frame_to_lever", multiplier=-rocker_ratio, offset=0.0),
            meta={"role": "compound toggle rocker"},
        )
        register_interface_mate(model, joint.name, mate)

        link_mult = 0.55 * rocker_ratio
        for index, sy in enumerate((-1.0, 1.0)):
            side = "left" if sy < 0 else "right"
            link = model.part(f"toggle_link_{side}", meta={"role": "toggle_link"})
            link.visual(
                _mesh(link_solid, f"plunger_drive__toggle_link__bar_{side}"),
                material="hardware",
                name=f"plunger_drive__toggle_link__bar_{side}", material_class_id="metal.chrome_polished",
            )
            axis = (0.0, -1.0, 0.0) if sy < 0 else (0.0, 1.0, 0.0)
            mate = _axis_mate(
                f"rocker.link_axis_{side}",
                (0.0, sy * span, link_z - rock_z),
                axis,
                f"link_{side}.hub_axis",
                r.pin_r * 0.62 + _BORE_CLEARANCE,
            )
            joint = model.articulation(
                f"rocker_to_link_{side}",
                ArticulationType.REVOLUTE,
                parent=rocker,
                child=link,
                origin=mate.origin,
                axis=mate.axis,
                motion_limits=MotionLimits(effort=120.0, velocity=3.0, lower=-0.55, upper=0.55),
                mimic=Mimic(
                    joint="frame_to_lever",
                    multiplier=link_mult * (1.0 if sy < 0 else -1.0),
                    offset=0.0,
                ),
                meta={"role": f"{side} toggle link"},
            )
            register_interface_mate(model, joint.name, mate)

        plunger = model.part("plunger", meta={"role": "pressing_plunger", "drive": "toggle_link"})
        plunger.visual(
            _mesh(
                face_solid.translate((-p.center_x, 0.0, -p.pivot_z)),
                "plunger_drive__toggle_link__face",
            ),
            material="body",
            name="plunger_drive__toggle_link__face", material_class_id=("metal.aluminum_bare" if r.palette_style in {"cast_aluminium", "brushed_stainless", "polished_steel", "dark_anodised"} else "metal.blackened_gunmetal"),
        )
        mate = _axis_mate(
            "rocker.plunger_axis",
            (0.0, 0.0, p.pivot_z - rock_z),
            (0.0, -1.0, 0.0),
            "plunger.hub_axis",
            r.pin_r * 0.62 + _BORE_CLEARANCE,
        )
        joint = model.articulation(
            "rocker_to_plunger",
            ArticulationType.REVOLUTE,
            parent=rocker,
            child=plunger,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(effort=300.0, velocity=2.0, lower=-0.55, upper=0.55),
            mimic=Mimic(joint="frame_to_lever", multiplier=0.6 * rocker_ratio, offset=0.0),
            meta={"role": "toggle-driven pressing face"},
        )
        register_interface_mate(model, joint.name, mate)

    # ---------------- accessory bodies --------------------------------------
    joint_spec = acc.get("joint")
    if r.flip_chamber:
        chamber_part = model.part(
            "chamber_body", meta={"role": "pressing_chamber", "chamber": r.chamber}
        )
        hinge_pt = joint_spec["point"]
        shift = _vscale(hinge_pt, -1.0)
        for local_name, solid, mat in chamber_solids:
            chamber_part.visual(
                _mesh(solid.translate(shift), f"chamber__{r.chamber}__{local_name}"),
                material=mat,
                name=f"chamber__{r.chamber}__{local_name}", material_class_id="metal.patterned_sheet_panel",
            )
        chamber_part.visual(
            _mesh(acc["chamber_barrel"].translate(shift), "accessory__flip_basket__barrel"),
            material="hardware",
            name="accessory__flip_basket__barrel", material_class_id="metal.chrome_polished",
        )
        mate = _axis_mate(
            "frame.basket_axis",
            hinge_pt,
            joint_spec["axis"],
            "chamber.barrel_axis",
            joint_spec["radius"] + _BORE_CLEARANCE,
        )
        joint = model.articulation(
            joint_spec["name"],
            ArticulationType.REVOLUTE,
            parent=frame,
            child=chamber_part,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(
                effort=40.0,
                velocity=2.5,
                lower=joint_spec["lower"],
                upper=joint_spec["upper"],
            ),
            meta={"role": "flip-out perforated basket"},
        )
        register_interface_mate(model, joint.name, mate)
    elif acc.get("part") is not None:
        part_name, solid, role = acc["part"]
        acc_part = model.part(part_name, meta={"role": role, "accessory": r.accessory})
        acc_part.visual(
            _mesh(solid, f"accessory__{r.accessory}__body"),
            material="hardware",
            name=f"accessory__{r.accessory}__body", material_class_id="metal.chrome_polished",
        )
        if acc.get("part_accent") is not None:
            acc_part.visual(
                _mesh(acc["part_accent"], f"accessory__{r.accessory}__tab"),
                material="accent",
                name=f"accessory__{r.accessory}__tab", material_class_id="plastic.opaque_glossy_molded",
            )
        if joint_spec["type"] is ArticulationType.PRISMATIC:
            mate = _axis_mate(
                "frame.ejector_axis",
                joint_spec["point"],
                joint_spec["axis"],
                "ejector.slide_axis",
                joint_spec["radius"],
            )
            joint = model.articulation(
                joint_spec["name"],
                ArticulationType.PRISMATIC,
                parent=frame,
                child=acc_part,
                origin=mate.origin,
                axis=mate.axis,
                motion_limits=MotionLimits(
                    effort=25.0,
                    velocity=0.2,
                    lower=joint_spec["lower"],
                    upper=joint_spec["upper"],
                ),
                meta={"role": "self-cleaning ejector slide"},
            )
            register_interface_mate(model, joint.name, mate)
        else:
            mate = _axis_mate(
                "frame.accessory_axis",
                joint_spec["point"],
                joint_spec["axis"],
                "accessory.hinge_axis",
                joint_spec["radius"] + _BORE_CLEARANCE,
            )
            joint = model.articulation(
                joint_spec["name"],
                ArticulationType.REVOLUTE,
                parent=frame,
                child=acc_part,
                origin=mate.origin,
                axis=mate.axis,
                motion_limits=MotionLimits(
                    effort=20.0,
                    velocity=3.0,
                    lower=joint_spec["lower"],
                    upper=joint_spec["upper"],
                ),
                meta={"role": f"{r.accessory} module"},
            )
            register_interface_mate(model, joint.name, mate)

    return model


def build_seeded_pictureX_0611_garlic_press(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_pictureX_0611_garlic_press(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Authored tests
# --------------------------------------------------------------------------- #
def _meshes_materialized(model: ArticulatedObject) -> bool:
    for part in model.parts:
        for visual in getattr(part, "visuals", []):
            filename = getattr(getattr(visual, "geometry", None), "filename", None)
            if filename and "__preflight_probe__" in str(filename):
                return False
    return True


def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def _aabb_center(aabb):
    if aabb is None:
        return None
    low, high = aabb
    return tuple((low[i] + high[i]) / 2.0 for i in range(3))


def _visual_names(part) -> set[str]:
    return {v.name for v in getattr(part, "visuals", [])}


def run_pictureX_0611_garlic_press_tests(model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    spec, _ = _build_chamber(r)
    p = _plunger_spec(r, spec)
    ctx = TestContext(model)
    joints = {joint.name: joint for joint in model.articulations}
    exact = _meshes_materialized(model)

    frames = _parts_by_role(model, "press_frame")
    levers = _parts_by_role(model, "press_lever")
    pins = _parts_by_role(model, "hinge_pin")
    plungers = _parts_by_role(model, "pressing_plunger")
    rockers = _parts_by_role(model, "toggle_rocker")
    links = _parts_by_role(model, "toggle_link")
    chambers = _parts_by_role(model, "pressing_chamber")
    cleaners = _parts_by_role(model, "cleaning_module")
    liners = _parts_by_role(model, "chamber_liner")
    latches = _parts_by_role(model, "storage_latch")

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_interface_mate_mismatch()
    if exact:
        ctx.fail_if_part_contains_disconnected_geometry_islands()
        ctx.fail_if_parts_overlap_in_current_pose()
        ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)

    # --- category anchor: the two-arm hinged press ---------------------------
    lever_joint = joints.get("frame_to_lever")
    ctx.check(
        "garlic press core hinge assembly",
        len(frames) == 1
        and len(levers) == 1
        and len(pins) == 1
        and lever_joint is not None
        and lever_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(lever_joint.axis) == (0.0, -1.0, 0.0)
        and "interface_mate" in (lever_joint.meta or {})
        and lever_joint.motion_limits is not None
        and lever_joint.motion_limits.upper > 0.6,
        details=(
            f"frames={len(frames)} levers={len(levers)} pins={len(pins)} "
            f"joint={None if lever_joint is None else (lever_joint.articulation_type, tuple(lever_joint.axis))}"
        ),
    )

    # --- category anchor: the perforated screen is a real hole field ---------
    screen = spec.screen
    hole_area = len(screen.holes) * math.pi * screen.hole_r**2
    footprint = 4.0 * screen.hu * screen.hv
    ctx.check(
        "perforated pressing screen is a real hole field",
        len(screen.holes) >= 10
        and screen.hole_r >= 0.00048
        and hole_area > 0.028 * footprint
        and int(model.meta.get("screen_holes", 0)) == len(screen.holes),
        details=(
            f"holes={len(screen.holes)} rows={r.screen_rows} r={screen.hole_r:.5f} "
            f"open_fraction={hole_area / max(footprint, 1e-9):.3f}"
        ),
    )

    # --- category anchor: the plunger enters the chamber ---------------------
    chamber_host = chambers[0] if chambers else (frames[0] if frames else None)
    chamber_elem = f"chamber__{r.chamber}__shell"
    if r.plunger_drive in {"rigid_pad", "stud_plate"}:
        plunger_host = levers[0] if levers else None
        plunger_elem = f"plunger_drive__{r.plunger_drive}__face"
    else:
        plunger_host = plungers[0] if plungers else None
        plunger_elem = (
            "plunger_drive__toggle_link__face"
            if r.plunger_drive == "toggle_link"
            else f"plunger_drive__{r.plunger_drive}__puck"
        )
    fits = (
        p.hx <= spec.mouth_hx - 0.0015 + 1e-9
        and p.hy <= spec.mouth_hy - 0.0015 + 1e-9
        and p.bottom_z < spec.rim_z - 1e-9
        and p.bottom_z > spec.cavity_floor_z + 0.0030
    )
    ctx.check(
        "plunger enters the pressing chamber",
        plunger_host is not None
        and chamber_host is not None
        and plunger_elem in _visual_names(plunger_host)
        and chamber_elem in _visual_names(chamber_host)
        and fits,
        details=(
            f"plunger=({p.hx:.4f},{p.hy:.4f}) mouth=({spec.mouth_hx:.4f},{spec.mouth_hy:.4f}) "
            f"bottom={p.bottom_z:.4f} rim={spec.rim_z:.4f} floor={spec.cavity_floor_z:.4f}"
        ),
    )
    if exact and plunger_host is not None and chamber_host is not None:
        ctx.expect_within(
            plunger_host,
            chamber_host,
            axes="xy",
            inner_elem=plunger_elem,
            outer_elem=chamber_elem,
            margin=0.0012,
            name="pressing face stays inside the chamber footprint",
        )
        ctx.expect_overlap(
            plunger_host,
            chamber_host,
            axes="z",
            elem_a=plunger_elem,
            elem_b=chamber_elem,
            min_overlap=0.0010,
            name="pressing face is engaged in the chamber mouth at rest",
        )

    # --- category anchor: the hinged plunger has its own pivot ---------------
    if r.plunger_drive in {"self_leveling", "cam_follower"}:
        joint = joints.get("lever_to_plunger")
        ctx.check(
            "plunger is carried on its own pivot",
            len(plungers) == 1
            and joint is not None
            and joint.articulation_type == ArticulationType.REVOLUTE
            and "interface_mate" in (joint.meta or {})
            and joint.motion_limits is not None
            and joint.motion_limits.lower < 0.0 < joint.motion_limits.upper,
            details=f"plungers={len(plungers)} joint={None if joint is None else joint.name}",
        )
    if r.plunger_drive == "cam_follower":
        ctx.check(
            "cam and follower roller are the drive pair",
            len(plungers) == 1
            and f"plunger_drive__{r.plunger_drive}__roller" in _visual_names(plungers[0])
            and f"plunger_drive__{r.plunger_drive}__mount" in _visual_names(levers[0]),
            details=(
                f"plunger visuals={sorted(_visual_names(plungers[0])) if plungers else []} "
                f"lever visuals={sorted(_visual_names(levers[0])) if levers else []}"
            ),
        )
        if exact and plungers and levers:
            ctx.expect_contact(
                levers[0],
                plungers[0],
                elem_a=f"plunger_drive__{r.plunger_drive}__mount",
                elem_b=f"plunger_drive__{r.plunger_drive}__roller",
                contact_tol=0.0012,
                name="follower roller rides the cam profile",
            )
    if r.plunger_drive == "toggle_link":
        toggle_joints = [
            joints.get("lever_to_rocker"),
            joints.get("rocker_to_link_left"),
            joints.get("rocker_to_link_right"),
            joints.get("rocker_to_plunger"),
        ]
        ctx.check(
            "toggle linkage drives the pressing face",
            len(rockers) == 1
            and len(links) == 2
            and len(plungers) == 1
            and all(j is not None for j in toggle_joints)
            and all(
                j.articulation_type == ArticulationType.REVOLUTE
                and "interface_mate" in (j.meta or {})
                and j.mimic is not None
                and j.mimic.joint == "frame_to_lever"
                for j in toggle_joints
            ),
            details=(
                f"rockers={len(rockers)} links={len(links)} plungers={len(plungers)} "
                f"joints={[None if j is None else j.name for j in toggle_joints]}"
            ),
        )

    # --- category anchor: the accessory module ------------------------------
    if r.accessory == "hang_loop":
        ctx.check(
            "hanging loop rides the lever tip",
            bool(levers) and r.loop_radius_m >= 0.0055,
            details=f"loop_r={r.loop_radius_m:.4f}",
        )
    elif r.accessory in {"swing_cleaner", "sliding_ejector"}:
        joint = joints.get("frame_to_cleaner") or joints.get("frame_to_ejector")
        expected = (
            ArticulationType.REVOLUTE
            if r.accessory == "swing_cleaner"
            else ArticulationType.PRISMATIC
        )
        ctx.check(
            "cleaning module registers with the screen",
            len(cleaners) == 1
            and joint is not None
            and joint.articulation_type == expected
            and joint.motion_limits is not None
            and joint.motion_limits.upper > 0.002,
            details=f"modules={len(cleaners)} joint={None if joint is None else (joint.name, joint.articulation_type)}",
        )
        if exact and cleaners and frames:
            ctx.expect_contact(
                cleaners[0],
                frames[0],
                elem_a=f"accessory__{r.accessory}__body",
                elem_b=f"accessory__{r.accessory}__mount",
                contact_tol=0.0016,
                name="cleaning module is captured on its frame mount",
            )
    elif r.accessory == "lift_out_insert":
        joint = joints.get("frame_to_liner")
        ctx.check(
            "lift-out liner sits inside the chamber",
            len(liners) == 1
            and joint is not None
            and joint.articulation_type == ArticulationType.REVOLUTE
            and joint.motion_limits is not None
            and joint.motion_limits.upper > 0.20,
            details=f"liners={len(liners)} joint={None if joint is None else joint.name}",
        )
    elif r.accessory == "storage_latch":
        joint = joints.get("frame_to_latch")
        ctx.check(
            "storage latch captures the lever",
            len(latches) == 1
            and joint is not None
            and joint.articulation_type == ArticulationType.REVOLUTE
            and joint.motion_limits is not None
            and joint.motion_limits.upper > 0.6,
            details=f"latches={len(latches)} joint={None if joint is None else joint.name}",
        )
    elif r.accessory == "flip_basket":
        joint = joints.get("frame_to_chamber")
        ctx.check(
            "chamber flips clear of the frame",
            len(chambers) == 1
            and joint is not None
            and joint.articulation_type == ArticulationType.REVOLUTE
            and "interface_mate" in (joint.meta or {})
            and joint.motion_limits is not None
            and joint.motion_limits.upper > 0.4,
            details=f"chambers={len(chambers)} joint={None if joint is None else joint.name}",
        )

    # --- silhouette: a handheld ~17-24 cm two-arm press ----------------------
    boxes = [ctx.part_world_aabb(part) for part in model.parts]
    boxes = [b for b in boxes if b is not None]
    if boxes:
        lo = [min(b[0][i] for b in boxes) for i in range(3)]
        hi = [max(b[1][i] for b in boxes) for i in range(3)]
        length, width, height = (hi[i] - lo[i] for i in range(3))
    else:
        length = width = height = 0.0
    ctx.check(
        "handheld two-arm press silhouette",
        0.150 <= length <= 0.260 and 0.018 <= width <= 0.085 and 0.018 <= height <= 0.105,
        details=f"length={length:.4f} width={width:.4f} height={height:.4f}",
    )

    # --- the two arms separate when the hinge opens --------------------------
    if lever_joint is not None and levers and frames:
        rest = _aabb_center(ctx.part_world_aabb(levers[0]))
        with ctx.pose({lever_joint: lever_joint.motion_limits.upper}):
            opened = _aabb_center(ctx.part_world_aabb(levers[0]))
            if exact and plunger_host is not None and chamber_host is not None:
                ctx.expect_gap(
                    plunger_host,
                    chamber_host,
                    axis="z",
                    positive_elem=plunger_elem,
                    negative_elem=chamber_elem,
                    min_gap=0.0005,
                    name="opening the hinge lifts the pressing face clear of the chamber",
                )
        ctx.check(
            "opening the hinge raises the upper arm",
            rest is not None and opened is not None and opened[2] > rest[2] + 0.012,
            details=f"rest={rest} open={opened}",
        )

    return ctx.report()


# --------------------------------------------------------------------------- #
# High-risk authored corners
# --------------------------------------------------------------------------- #
TEMPLATE_CORNERS = (
    corner_case(
        "drum_screen_with_toggle_and_flip",
        {
            "chamber": "drum_face",
            "plunger_drive": "toggle_link",
            "accessory": "flip_basket",
            "arm_profile": "round_tube",
            "screen_rows": 7,
            "chamber_span_m": 0.0180,
            "chamber_depth_m": 0.0315,
            "drum_sink_ratio": 0.48,
            "rocker_span_m": 0.0160,
            "flip_rad": 1.28,
            "plunger_fill_ratio": 0.90,
        },
        reason=(
            "the pool's only side-facing screen carried on the pool's only multi-body "
            "linkage, with the chamber itself turned into a flipping part: the rocker "
            "arms have to clear the widest drum while the drum swings out of the cradle"
        ),
    ),
    corner_case(
        "front_wall_screen_with_ejector",
        {
            "chamber": "loft_hopper",
            "plunger_drive": "stud_plate",
            "accessory": "sliding_ejector",
            "arm_profile": "lofted_ellipse",
            "screen_rows": 7,
            "ejector_travel_m": 0.0082,
            "rail_span_ratio": 0.80,
            "ejector_pin_ratio": 0.85,
            "hole_radius_m": 0.00135,
            "screen_thickness_m": 0.0023,
            "stud_rows": 5,
        },
        reason=(
            "the prismatic ejector run on the front-wall screen at maximum travel, "
            "widest rail span and fattest cleaning pins in the thinnest screen plate"
        ),
    ),
    corner_case(
        "deepest_hopper_with_liner_and_cam",
        {
            "chamber": "oval_hopper",
            "plunger_drive": "cam_follower",
            "accessory": "lift_out_insert",
            "arm_profile": "flat_bar",
            "screen_rows": 6,
            "chamber_depth_m": 0.0315,
            "hopper_extra_depth_m": 0.0085,
            "oval_aspect": 2.10,
            "insert_fill_ratio": 0.94,
            "insert_lift_rad": 1.25,
            "engage_depth_m": 0.0062,
            "cam_radius_m": 0.0110,
            "roller_radius_m": 0.0046,
        },
        reason=(
            "the deepest and most elongated hopper with the largest liner lifting "
            "under a cam-driven plunger at its deepest engagement -- the combination "
            "where the liner's swing and the plunger's travel share the same cavity"
        ),
    ),
    corner_case(
        "tapered_cup_with_cleaner_at_smallest_frame",
        {
            "chamber": "taper_cup",
            "plunger_drive": "self_leveling",
            "accessory": "swing_cleaner",
            "arm_profile": "round_tube",
            "screen_rows": 3,
            "chamber_span_m": 0.0122,
            "chamber_depth_m": 0.0185,
            "taper_ratio": 1.26,
            "handle_len_m": 0.108,
            "pivot_rise_m": 0.0075,
            "lug_inner_y_m": 0.0058,
            "pin_radius_m": 0.0037,
            "cleaner_pin_len_m": 0.0062,
            "cleaner_open_rad": 1.40,
            "tilt_rad": 0.30,
        },
        reason=(
            "smallest cup and shortest arms on the fattest pin in the narrowest clevis, "
            "with the longest cleaner pins swinging off the separately-materialled "
            "perforated face and the plunger at maximum self-levelling tilt"
        ),
    ),
    corner_case(
        "ribbed_cup_with_latch_at_largest_frame",
        {
            "chamber": "ribbed_cup",
            "plunger_drive": "rigid_pad",
            "accessory": "storage_latch",
            "arm_profile": "lofted_ellipse",
            "screen_rows": 7,
            "chamber_span_m": 0.0180,
            "rib_count": 6,
            "rib_reach_m": 0.0070,
            "flange_proud_m": 0.0034,
            "handle_len_m": 0.156,
            "arm_half_width_m": 0.0125,
            "palm_swell_ratio": 1.42,
            "latch_arm_len_m": 0.0225,
            "latch_release_rad": 1.35,
            "plunger_thickness_m": 0.0120,
        },
        reason=(
            "the longest and widest lofted arms with the tallest latch reaching the "
            "highest capture pin, over the most heavily ribbed and flanged cup"
        ),
    ),
    corner_case(
        "rect_trough_widest_with_flip_and_stud_plate",
        {
            "chamber": "rect_trough",
            "plunger_drive": "stud_plate",
            "accessory": "flip_basket",
            "arm_profile": "flat_bar",
            "screen_rows": 5,
            "trough_aspect": 2.35,
            "chamber_span_m": 0.0180,
            "cradle_plate_t_m": 0.0046,
            "flip_rad": 0.55,
            "chamber_offset_m": 0.0320,
            "stud_rows": 5,
            "stud_len_m": 0.0022,
        },
        reason=(
            "the longest trough pushed as far forward as the clevis allows, flipping "
            "on the thickest cradle plates while a full stud field sits in its mouth"
        ),
    ),
)


__all__ = [
    "Config",
    "PALETTES",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pictureX_0611_garlic_press",
    "build_seeded_pictureX_0611_garlic_press",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_garlic_press_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
