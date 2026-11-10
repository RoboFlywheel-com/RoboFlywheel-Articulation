# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Self-contained `rivet_squeeze` template - hand-held COMPRESSION riveters.

A forged frame whose throat carries TWO OPPOSED DIES on one shared axis, a hand
drive that closes the upper die onto the lower one, and an independently
adjustable lower die that sets rivet length.  It is not a blind-rivet puller;
that is the explicit `must_not_become` sibling and origin 003 is the pool's own
negative example.

Slots (TemplateDesign `designs/rivet_squeeze.json`, no multiplicity axis):
  yoke_frame        5   deep_c_yoke_forging | throated_forged_body |
                        long_c_yoke_throat | compact_straight_head | alligator_jaw
  squeeze_mechanism 6   hidden_internal_toggle | dogbone_mimic_link |
                        long_toggle_cheek | eccentric_cam | screw_press |
                        direct_jaw_lever
  head_module       4   stepped_cylinder_dies | plain_die_pair |
                        rotating_set_holder | quick_change_yoke_clip
  return_element    4   wire_extension_spring | leaf_return_spring |
                        torsion_handle_spring | no_return_element
  handle_lock       3   wire_hook_latch | eye_and_wire_loop_latch | no_handle_lock
core_domain = 5*6*4*4*3 = 1440, raw_domain = 1440.  Every one must build.

FRAME CONVENTION (SourceMap "Frame convention for the rebuild", origin 002's):
the main handle pivot is the world origin, the grips extend +X, the jaw throat
opens -X, the tool width runs along Y and the squeeze/die axis is +Z.  `+-Y` is
the hinge axis of every revolute in the pool (13/13 records); the one declared
exception is `screw_press`, whose drive head turns about the squeeze axis itself
(rec ..._screw_press model.py:L288) and which therefore carries its own anchor.

--------------------------------------------------------------------------
THE CONTACT CONTRACT - why this template declares no `ctx.allow_overlap`
--------------------------------------------------------------------------
All 13 source records use `ctx.allow_overlap` (41 calls); a Design-backed
template has it blocked in preflight.  The design's `contact_policy` binding
splits every site into three classes and this file honours the split literally:

  SAME PART  -> weld with `_EMBED` (0.5 mm).  Collision is computed only
    between parts (`fail_if_parts_overlap_*` is pairwise over links), so two
    visuals of one part may interpenetrate freely.  The 1e-6 connectivity check
    (`find_part_geometry_connectivity_findings`) is INTRA-part, so a same-part
    weld must be a real embed, never a coincident face.
  CONNECTION -> `_CONNECT` (0.25 mm) along ONE contact normal.
    `find_geometry_overlaps` only calls `fcl.collide` when the AABB intersection
    depth exceeds `overlap_tol` on ALL THREE axes, and `overlap_tol` defaults to
    1e-3, so a 0.25 mm lap on a single axis is invisible to the gate while being
    250x the connectivity tolerance.
  RUNNING FIT -> a real gap, never an overlap.  `pin_r = bore_r - 0.6 mm` and
    `guide_bore_r = shaft_r + 1.1..1.2 mm`, both generalised from record 001,
    the only record in the pool that needs no allowance anywhere.

The three rebuild moves, all implemented here:
  (a) THE PIN VISUAL BELONGS TO THE MOVING MEMBER (001 L311-L316 puts
      `main_pivot_pin` on `moving_handle`).  It is welded into the lever's own
      hub - intra-part, free - and only the FRAME bore is a cross-part
      clearance, cut at `lever_bore + 0.4 mm` so the pin clears it by 1.0 mm.
      Removes allow_overlap sites 5, 7, 8, 10, 14.
  (b) THE COUNTERBORES AND THROUGH-BORES ARE ACTUALLY CUT.  002 declares its
      anvil collar 5.0-6.5 mm inside the forging (L444-L463) instead of
      machining the pocket; `screw_press` declares `max_penetration=0.0035` for
      its drive register (L497-L516); `alligator_jaw` runs its set through an
      uncut jaw tip (L749-L757).  All three are real `cut()` operations here,
      each sized off the moving part's envelope per MECHANICAL_PRIORS 7.
      Removes sites 3, 6, 9, 11, 12, 13.
  (c) `ctx.allow_isolated_part` FOR JOINT-CARRIED MEMBERS.  The lever, the
      compound link, the latch and both die parts are retained by their joints
      and separated from every other part by a running clearance, which is
      exactly the case `sdk_base.md` still permits.  Removes sites 1 and 2.

WELD RULE.  `sdk/_core/v0/exact_collisions.py` derives one collision solid per
visual, 1:1.  `screw_press` builds 9 + 13 visuals on two ~15 mm parts = 22
collision solids.  Every die, set, anvil and screw here is ONE welded CadQuery
solid emitted as ONE visual, following the pool's own
`_rotating_set_holder_shape` (rec ..._rotating_set_holder L220-L249) and
`_nosepiece_shape` (003 L52-L77); thread crests become a lathed groove in the
same body.  The frame and each lever are likewise one solid apiece.

LATERAL LAYERING.  The frame occupies |y| <= frame_width/2.  Every moving member
sits in its own outboard Y band with at least the 1.0 mm stand-off that 001
(L293/L305) and 003 (L308) both build, so no pose of any joint can bring two
parts into contact except through their own bores, which are running fits.
Frame-borne extras (springs, quick-change clip, latch axle) sit on +Y and are
welded into the frame body; moving members sit on -Y.

No source runtime, snapshot or other template is imported: stdlib + cadquery +
sdk only.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, fields
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Cylinder,
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
    mesh_from_geometry,
    register_interface_mate,
    tube_from_spline_points,
)

YokeFrame = Literal[
    "deep_c_yoke_forging",
    "throated_forged_body",
    "long_c_yoke_throat",
    "compact_straight_head",
    "alligator_jaw",
]
SqueezeMechanism = Literal[
    "hidden_internal_toggle",
    "dogbone_mimic_link",
    "long_toggle_cheek",
    "eccentric_cam",
    "screw_press",
    "direct_jaw_lever",
]
HeadModule = Literal[
    "stepped_cylinder_dies",
    "plain_die_pair",
    "rotating_set_holder",
    "quick_change_yoke_clip",
]
ReturnElement = Literal[
    "wire_extension_spring",
    "leaf_return_spring",
    "torsion_handle_spring",
    "no_return_element",
]
HandleLock = Literal["wire_hook_latch", "eye_and_wire_loop_latch", "no_handle_lock"]
PaletteStyle = Literal["red_forged", "black_oxide", "teal_cast"]

YOKE_FRAMES: tuple[YokeFrame, ...] = (
    "deep_c_yoke_forging",
    "throated_forged_body",
    "long_c_yoke_throat",
    "compact_straight_head",
    "alligator_jaw",
)
SQUEEZE_MECHANISMS: tuple[SqueezeMechanism, ...] = (
    "hidden_internal_toggle",
    "dogbone_mimic_link",
    "long_toggle_cheek",
    "eccentric_cam",
    "screw_press",
    "direct_jaw_lever",
)
HEAD_MODULES: tuple[HeadModule, ...] = (
    "stepped_cylinder_dies",
    "plain_die_pair",
    "rotating_set_holder",
    "quick_change_yoke_clip",
)
RETURN_ELEMENTS: tuple[ReturnElement, ...] = (
    "wire_extension_spring",
    "leaf_return_spring",
    "torsion_handle_spring",
    "no_return_element",
)
HANDLE_LOCKS: tuple[HandleLock, ...] = (
    "wire_hook_latch",
    "eye_and_wire_loop_latch",
    "no_handle_lock",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("red_forged", "black_oxide", "teal_cast")

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("yoke_frame", YOKE_FRAMES, role="grounded forged frame carrying both dies"),
        component_slot(
            "squeeze_mechanism",
            SQUEEZE_MECHANISMS,
            role="drive layer between the hand and the upper die",
        ),
        component_slot(
            "head_module", HEAD_MODULES, role="opposed rivet die/set pair and retention"
        ),
        component_slot(
            "return_element", RETURN_ELEMENTS, role="return spring for the driven member"
        ),
        component_slot("handle_lock", HANDLE_LOCKS, role="handle lock / latch"),
    )
)

# ---------------------------------------------------------------------------
# contact_policy binding -- see the module docstring.
# ---------------------------------------------------------------------------
_CONNECT = 0.00025  # connection_overlap_m  : cross-part CONNECTION lap
_CHORD = 0.00015  # mesh_chord_tol_m      : 0.6 * _CONNECT, tessellation bound
_EMBED = 0.0005  # intra_part_embed_m    : same-part weld depth (free)
_RUNNING = 0.0006  # running_fit_min_m     : floor for every cross-part running fit
_ANG_TOL = 0.10

# Which mechanisms own which structure (SourceMap slot table, Slot B).
_MECH_HAS_HAND_LEVER = {
    "hidden_internal_toggle": True,
    "dogbone_mimic_link": True,
    "long_toggle_cheek": True,
    "eccentric_cam": True,
    "screw_press": False,
    "direct_jaw_lever": True,
}
_MECH_HAS_LINK = {
    "hidden_internal_toggle": False,
    "dogbone_mimic_link": True,
    "long_toggle_cheek": True,
    "eccentric_cam": True,
    "screw_press": True,
    "direct_jaw_lever": False,
}
_MECH_HAS_RAM = {
    "hidden_internal_toggle": True,
    "dogbone_mimic_link": True,
    "long_toggle_cheek": True,
    "eccentric_cam": True,
    "screw_press": True,
    "direct_jaw_lever": False,
}

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    # 001 red_painted_metal / black_rubber / polished_steel / dark_steel.
    "red_forged": {
        "forging": (0.88, 0.075, 0.035, 1.0),
        "grip": (0.025, 0.028, 0.028, 1.0),
        "polished": (0.76, 0.79, 0.81, 1.0),
        "dark": (0.22, 0.24, 0.25, 1.0),
        "zinc": (0.72, 0.74, 0.75, 1.0),
    },
    # 002 black_oxide_steel / red_powder_coat / zinc_plated_steel.
    "black_oxide": {
        "forging": (0.045, 0.050, 0.052, 1.0),
        "grip": (0.88, 0.025, 0.055, 1.0),
        "polished": (0.55, 0.58, 0.60, 1.0),
        "dark": (0.085, 0.090, 0.095, 1.0),
        "zinc": (0.72, 0.74, 0.75, 1.0),
    },
    # 003 / alligator_jaw teal cast body with satin steel hardware.
    "teal_cast": {
        "forging": (0.055, 0.36, 0.38, 1.0),
        "grip": (0.05, 0.055, 0.06, 1.0),
        "polished": (0.70, 0.73, 0.75, 1.0),
        "dark": (0.20, 0.22, 0.23, 1.0),
        "zinc": (0.66, 0.68, 0.70, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Candidate-local independent parameter domains, verbatim from the
# TemplateDesign.  Sampling and validation are scoped to the ACTIVE candidate so
# a parameter is never driven outside the range its own candidate declares.
# ---------------------------------------------------------------------------
_CANDIDATE_PARAMS: dict[str, dict[str, object]] = {
    "deep_c_yoke_forging": {
        "frame_width_m": (0.017, 0.034),
        "die_station_x_m": (0.058, 0.14),
        "main_pivot_bore_r_m": (0.0046, 0.008),
        "frame_reach_m": (0.07, 0.185),
        "body_profile_points": [14, 18, 22],
        "upper_beam_h_m": (0.02, 0.042),
        "lower_beam_h_m": (0.015, 0.034),
        "jaw_throat_height_m": (0.026, 0.058),
        "jaw_boss_r_m": (0.008, 0.02),
        "fixture_hole_r_m": (0.005, 0.012),
    },
    "throated_forged_body": {
        "frame_width_m": (0.017, 0.034),
        "die_station_x_m": (0.058, 0.14),
        "main_pivot_bore_r_m": (0.0046, 0.008),
        "frame_reach_m": (0.07, 0.185),
        "outer_profile_points": [8, 12, 16],
        "throat_profile_points": [5, 9, 13],
        "throat_cut_width_m": (0.038, 0.07),
        "edge_fillet_m": (0.0015, 0.006),
        "jaw_throat_height_m": (0.026, 0.058),
    },
    "long_c_yoke_throat": {
        "frame_width_m": (0.017, 0.034),
        "die_station_x_m": (0.058, 0.14),
        "main_pivot_bore_r_m": (0.0046, 0.008),
        "frame_reach_m": (0.07, 0.185),
        "outer_profile_points": [8, 12, 16],
        "throat_profile_points": [5, 9, 13],
        "throat_cut_width_m": (0.038, 0.07),
        "edge_fillet_m": (0.0015, 0.006),
        "heel_cheek_points": [7, 11, 15],
        "cheek_thickness_m": (0.0012, 0.0035),
        "jaw_throat_height_m": (0.026, 0.062),
    },
    "compact_straight_head": {
        "frame_width_m": (0.017, 0.034),
        "die_station_x_m": (0.058, 0.14),
        "main_pivot_bore_r_m": (0.0046, 0.008),
        "frame_reach_m": (0.07, 0.185),
        "body_profile_points": [14, 18, 22],
        "upper_beam_len_m": (0.036, 0.075),
        "lower_beam_len_m": (0.032, 0.07),
        "upper_beam_h_m": (0.02, 0.042),
        "lower_beam_h_m": (0.015, 0.034),
        "jaw_boss_r_m": (0.008, 0.02),
        "jaw_throat_height_m": (0.024, 0.052),
    },
    "alligator_jaw": {
        "frame_width_m": (0.017, 0.034),
        "die_station_x_m": (0.058, 0.14),
        "main_pivot_bore_r_m": (0.0046, 0.008),
        "frame_reach_m": (0.07, 0.185),
        "frame_profile_points": [18, 22, 25, 29],
        "receiver_od_m": (0.008, 0.014),
        "receiver_id_m": (0.0055, 0.0098),
        "receiver_len_m": (0.022, 0.048),
        "lever_relief_slot_h_m": (0.008, 0.02),
        "jaw_throat_height_m": (0.026, 0.062),
    },
    "hidden_internal_toggle": {
        "lever_travel_rad": (0.1, 0.3),
        "lever_effort_n": (180.0, 520.0),
        "ram_effort_n": (3000.0, 11000.0),
        "lever_plate_width_m": (0.006, 0.05),
        "lever_profile_points": [12, 16, 20],
    },
    "dogbone_mimic_link": {
        "lever_travel_rad": (0.14, 0.36),
        "lever_effort_n": (180.0, 520.0),
        "ram_effort_n": (3000.0, 11000.0),
        "lever_plate_width_m": (0.006, 0.05),
        "link_thickness_m": (0.0025, 0.007),
        "link_profile_points": [4, 5, 7],
        "link_eye_r_m": (0.0022, 0.005),
        "link_cheek_offset_m": (0.016, 0.038),
        "mimic_multiplier": (-0.95, -0.45),
    },
    "long_toggle_cheek": {
        "lever_travel_rad": (0.14, 0.36),
        "lever_effort_n": (180.0, 520.0),
        "ram_effort_n": (3000.0, 11000.0),
        "lever_plate_width_m": (0.006, 0.05),
        "toggle_half_width_m": (0.004, 0.0095),
        "toggle_boss_r_m": (0.0055, 0.0125),
        "link_eye_r_m": (0.0022, 0.005),
        "ram_head_w_m": (0.012, 0.028),
        "ram_cross_pin_len_m": (0.04, 0.08),
        "mimic_multiplier": (0.4, 0.9),
    },
    "eccentric_cam": {
        "lever_travel_rad": (0.14, 0.36),
        "lever_effort_n": (180.0, 520.0),
        "ram_effort_n": (3000.0, 11000.0),
        "lever_plate_width_m": (0.006, 0.05),
        "cam_lobe_r_m": (0.0125, 0.026),
        "cam_eccentricity_m": (0.006, 0.015),
        "cam_bore_r_m": (0.004, 0.008),
        "cam_thickness_m": (0.0045, 0.0115),
        "reaction_pin_r_m": (0.0048, 0.0105),
        "bracket_thickness_m": (0.0025, 0.0065),
        "follower_head_r_m": (0.0055, 0.012),
        "mimic_multiplier": (-0.85, -0.35),
    },
    "screw_press": {
        "screw_turn_range_rad": (1.5708, 6.2832),
        "drive_hub_r_m": (0.01, 0.02),
        "drive_hub_h_m": (0.0125, 0.026),
        "register_r_m": (0.0072, 0.0145),
        "register_h_m": (0.0018, 0.0055),
        "tommy_bore_r_m": (0.003, 0.0065),
        "tommy_bar_len_m": (0.11, 0.24),
        "tommy_slide_range_m": (0.012, 0.045),
        "lead_m_per_turn": (0.001, 0.003),
        "ram_effort_n": (3000.0, 11000.0),
        "thread_crest_count": [5, 7, 9],
    },
    "direct_jaw_lever": {
        "lever_travel_rad": (0.0175, 0.07),
        "lever_effort_n": (180.0, 520.0),
        "jaw_reach_m": (0.13, 0.215),
        "jaw_profile_points": [17, 19, 23, 27],
        "jaw_thickness_m": (0.0075, 0.022),
        "lower_set_boss_r_m": (0.0035, 0.008),
        "lower_set_boss_h_m": (0.01, 0.026),
    },
    "stepped_cylinder_dies": {
        "open_die_gap_m": (0.0035, 0.015),
        "closing_residual_m": (0.0, 0.0045),
        "die_tip_r_m": (0.0028, 0.0078),
        "upper_die_shaft_r_m": (0.0038, 0.0062),
        "anvil_adjust_range_m": (0.0025, 0.005),
        "anvil_effort_n": (700.0, 2400.0),
        "holder_r_m": (0.0055, 0.0115),
        "ram_cap_r_m": (0.0055, 0.0115),
        "adjuster_wheel_r_m": (0.0055, 0.012),
        "stack_step_count": [3, 4, 5],
    },
    "plain_die_pair": {
        "open_die_gap_m": (0.0035, 0.015),
        "closing_residual_m": (0.0, 0.0045),
        "die_tip_r_m": (0.0028, 0.0078),
        "upper_die_shaft_r_m": (0.0038, 0.0062),
        "anvil_adjust_range_m": (0.0025, 0.005),
        "anvil_effort_n": (700.0, 2400.0),
        "knurled_adjuster_r_m": (0.0052, 0.0105),
        "knurled_adjuster_h_m": (0.028, 0.062),
        "adjuster_stop_r_m": (0.0065, 0.013),
        "retaining_collar_r_m": (0.007, 0.0145),
        "stack_step_count": [3, 5, 7],
    },
    "rotating_set_holder": {
        "open_die_gap_m": (0.0035, 0.015),
        "closing_residual_m": (0.0, 0.0045),
        "die_tip_r_m": (0.0028, 0.0078),
        "upper_die_shaft_r_m": (0.0038, 0.0062),
        "anvil_adjust_range_m": (0.0025, 0.005),
        "anvil_effort_n": (700.0, 2400.0),
        "collar_facets": [8, 12, 16],
        "collar_across_flats_m": (0.0125, 0.023),
        "upper_holder_h_m": (0.0035, 0.0075),
        "lower_holder_h_m": (0.0028, 0.0065),
        "socket_r_m": (0.0026, 0.005),
        "socket_depth_m": (0.0012, 0.0026),
        "land_r_m": (0.004, 0.0085),
    },
    "quick_change_yoke_clip": {
        "open_die_gap_m": (0.0035, 0.015),
        "closing_residual_m": (0.0, 0.0045),
        "die_tip_r_m": (0.0028, 0.0078),
        "upper_die_shaft_r_m": (0.0038, 0.0062),
        "anvil_adjust_range_m": (0.0025, 0.005),
        "anvil_effort_n": (700.0, 2400.0),
        "set_shank_r_m": (0.0045, 0.008),
        "set_collar_r_m": (0.0048, 0.0125),
        "set_tip_r_m": (0.0032, 0.0065),
        "set_bore_r_m": (0.0012, 0.0028),
        "clip_od_r_m": (0.0052, 0.0105),
        "clip_id_r_m": (0.0024, 0.005),
        "clip_thickness_m": (0.0018, 0.0048),
        "clip_slot_w_m": (0.0026, 0.0058),
        "thumb_tab_hole_r_m": (0.0008, 0.002),
    },
    "wire_extension_spring": {
        "wire_r_m": (0.0008, 0.002),
        "zigzag_points": [5, 7, 9],
        "spring_len_m": (0.035, 0.09),
        "zigzag_amplitude_m": (0.0035, 0.012),
    },
    "leaf_return_spring": {
        "leaf_thickness_m": (0.001, 0.0026),
        "leaf_profile_points": [13, 17, 21],
        "leaf_len_m": (0.048, 0.082),
        "leaf_bow_m": (0.008, 0.02),
    },
    "torsion_handle_spring": {
        "wire_r_m": (0.0008, 0.002),
        "coil_r_m": (0.008, 0.0175),
        "coil_turns": (1.25, 3.5),
        "coil_samples": [24, 34, 44],
        "axial_advance_m": (0.003, 0.0105),
        "reaction_leg_points": [2, 3, 4],
    },
    "no_return_element": {},
    "wire_hook_latch": {
        "wire_r_m": (0.0008, 0.002),
        "hook_points": [4, 5, 7],
        "hook_reach_m": (0.04, 0.11),
        "latch_swing_rad": (0.85, 1.45),
        "latch_effort_n": (0.8, 6.0),
    },
    "eye_and_wire_loop_latch": {
        "eye_od_r_m": (0.0032, 0.0068),
        "eye_id_r_m": (0.0016, 0.0038),
        "eye_thickness_m": (0.0025, 0.0065),
        "loop_points": [6, 8, 10],
        "wire_r_m": (0.0008, 0.002),
        "latch_swing_rad": (1.05, 1.6),
        "latch_effort_n": (0.8, 6.0),
    },
    "no_handle_lock": {},
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    yoke_frame: YokeFrame = "deep_c_yoke_forging"
    squeeze_mechanism: SqueezeMechanism = "hidden_internal_toggle"
    head_module: HeadModule = "stepped_cylinder_dies"
    return_element: ReturnElement = "wire_extension_spring"
    handle_lock: HandleLock = "wire_hook_latch"
    palette_style: PaletteStyle = "red_forged"
    # --- yoke_frame ---------------------------------------------------------
    frame_width_m: float = 0.0255
    die_station_x_m: float = 0.099
    main_pivot_bore_r_m: float = 0.0063
    frame_reach_m: float = 0.1275
    body_profile_points: int = 18
    upper_beam_h_m: float = 0.031
    lower_beam_h_m: float = 0.0245
    jaw_throat_height_m: float = 0.042
    jaw_boss_r_m: float = 0.014
    fixture_hole_r_m: float = 0.0085
    outer_profile_points: int = 12
    throat_profile_points: int = 9
    throat_cut_width_m: float = 0.054
    edge_fillet_m: float = 0.00375
    heel_cheek_points: int = 11
    cheek_thickness_m: float = 0.00235
    upper_beam_len_m: float = 0.0555
    lower_beam_len_m: float = 0.051
    frame_profile_points: int = 25
    receiver_od_m: float = 0.011
    receiver_id_m: float = 0.00765
    receiver_len_m: float = 0.035
    lever_relief_slot_h_m: float = 0.014
    # --- squeeze_mechanism --------------------------------------------------
    lever_travel_rad: float = 0.2
    lever_effort_n: float = 350.0
    ram_effort_n: float = 7000.0
    lever_plate_width_m: float = 0.028
    lever_profile_points: int = 16
    link_thickness_m: float = 0.00475
    link_profile_points: int = 5
    link_eye_r_m: float = 0.0036
    link_cheek_offset_m: float = 0.027
    mimic_multiplier: float = -0.7
    toggle_half_width_m: float = 0.00675
    toggle_boss_r_m: float = 0.009
    ram_head_w_m: float = 0.02
    ram_cross_pin_len_m: float = 0.06
    cam_lobe_r_m: float = 0.01925
    cam_eccentricity_m: float = 0.0105
    cam_bore_r_m: float = 0.006
    cam_thickness_m: float = 0.008
    reaction_pin_r_m: float = 0.00765
    bracket_thickness_m: float = 0.0045
    follower_head_r_m: float = 0.00875
    screw_turn_range_rad: float = 3.927
    drive_hub_r_m: float = 0.015
    drive_hub_h_m: float = 0.01925
    register_r_m: float = 0.01085
    register_h_m: float = 0.00365
    tommy_bore_r_m: float = 0.00475
    tommy_bar_len_m: float = 0.175
    tommy_slide_range_m: float = 0.0285
    lead_m_per_turn: float = 0.002
    thread_crest_count: int = 7
    jaw_reach_m: float = 0.1725
    jaw_profile_points: int = 23
    jaw_thickness_m: float = 0.01475
    lower_set_boss_r_m: float = 0.00575
    lower_set_boss_h_m: float = 0.018
    # --- head_module --------------------------------------------------------
    open_die_gap_m: float = 0.00925
    closing_residual_m: float = 0.00225
    die_tip_r_m: float = 0.0053
    upper_die_shaft_r_m: float = 0.005
    anvil_adjust_range_m: float = 0.00375
    anvil_effort_n: float = 1550.0
    holder_r_m: float = 0.0085
    ram_cap_r_m: float = 0.0085
    adjuster_wheel_r_m: float = 0.00875
    stack_step_count: int = 4
    knurled_adjuster_r_m: float = 0.00785
    knurled_adjuster_h_m: float = 0.045
    adjuster_stop_r_m: float = 0.00975
    retaining_collar_r_m: float = 0.01075
    collar_facets: int = 12
    collar_across_flats_m: float = 0.01775
    upper_holder_h_m: float = 0.0055
    lower_holder_h_m: float = 0.00465
    socket_r_m: float = 0.0038
    socket_depth_m: float = 0.0019
    land_r_m: float = 0.00625
    set_shank_r_m: float = 0.00625
    set_collar_r_m: float = 0.00865
    set_tip_r_m: float = 0.00485
    set_bore_r_m: float = 0.002
    clip_od_r_m: float = 0.00785
    clip_id_r_m: float = 0.0037
    clip_thickness_m: float = 0.0033
    clip_slot_w_m: float = 0.0042
    thumb_tab_hole_r_m: float = 0.0014
    # --- return_element -----------------------------------------------------
    wire_r_m: float = 0.0014
    zigzag_points: int = 7
    spring_len_m: float = 0.0625
    zigzag_amplitude_m: float = 0.00775
    leaf_thickness_m: float = 0.0018
    leaf_profile_points: int = 17
    leaf_len_m: float = 0.065
    leaf_bow_m: float = 0.014
    coil_r_m: float = 0.01275
    coil_turns: float = 2.375
    coil_samples: int = 34
    axial_advance_m: float = 0.00675
    reaction_leg_points: int = 3
    # --- handle_lock --------------------------------------------------------
    hook_points: int = 5
    hook_reach_m: float = 0.075
    latch_swing_rad: float = 1.15
    latch_effort_n: float = 3.4
    eye_od_r_m: float = 0.005
    eye_id_r_m: float = 0.0027
    eye_thickness_m: float = 0.0045
    loop_points: int = 8
    name: str = "rivet_squeeze"


@dataclass(frozen=True)
class ResolvedConfig:
    # slot choices
    yoke_frame: YokeFrame
    squeeze_mechanism: SqueezeMechanism
    head_module: HeadModule
    return_element: ReturnElement
    handle_lock: HandleLock
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    # clamped independent values (only those the active candidates own matter)
    p: dict[str, float]
    # ---- derived: contact policy ------------------------------------------
    connection_overlap_m: float
    intra_part_embed_m: float
    running_fit_min_m: float
    mesh_chord_tol_m: float
    # ---- derived: pin_bore_fit --------------------------------------------
    lever_pivot_bore_r_m: float
    main_pivot_pin_r_m: float
    link_pin_r_m: float
    lever_standoff_m: float
    lever_fork_slot_w_m: float
    # ---- derived: guide_bore_fit ------------------------------------------
    anvil_shaft_r_m: float
    ram_guide_bore_r_m: float
    anvil_guide_bore_r_m: float
    max_die_step_r_m: float
    set_collar_r_eff_m: float
    ram_guide_depth_m: float
    anvil_guide_depth_m: float
    # ---- derived: die_coaxiality ------------------------------------------
    die_axis_x_m: float
    die_axis_y_m: float
    upper_die_tip_offset_m: float
    lower_die_tip_offset_m: float
    lower_die_parent_role: str
    die_retention_z_m: float
    die_retention_r_m: float
    # ---- derived: ram_stroke_from_gap -------------------------------------
    closing_residual_eff_m: float
    anvil_adjust_eff_m: float
    upper_die_travel_m: float
    upper_seat_z_m: float
    ram_travel_m: float
    ram_travel_available_m: float
    screw_turn_range_eff_rad: float
    upper_die_stack_h_m: float
    lower_die_stack_h_m: float
    upper_jaw_underside_z_m: float
    lower_jaw_top_z_m: float
    throat_open_m: float
    throat_stroke_clearance_m: float
    upper_beam_top_z_m: float
    lower_beam_bottom_z_m: float
    upper_beam_bearing_len_m: float
    lower_beam_bearing_len_m: float
    upper_beam_h_eff_m: float
    lower_beam_h_eff_m: float
    frame_reach_eff_m: float
    # ---- derived: counterbore_seats ---------------------------------------
    anvil_collar_counterbore_r_m: float
    anvil_collar_counterbore_h_m: float
    screw_register_counterbore_r_m: float
    screw_register_counterbore_h_m: float
    tommy_bushing_r_m: float
    set_through_bore_r_m: float
    # ---- derived: grip_closure --------------------------------------------
    fixed_grip_is_separate_part: str
    fixed_grip_root_x_m: float
    grip_lever_arm_m: float
    grip_travel_m: float
    fixed_grip_len_m: float
    grip_section_w_m: float
    closed_grip_gap_m: float
    fixed_grip_centre_z_m: float
    moving_grip_centre_z_m: float
    moving_grip_centre_x_m: float
    moving_grip_stop_x_m: float
    lever_travel_eff_rad: float
    grip_phi_rad: float
    grip_drop_m: float
    # ---- derived: cam_reaction_adaptation ---------------------------------
    reaction_bracket_required: str
    reaction_bracket_x_m: float
    reaction_bracket_offset_y_m: float
    cam_bearing_clearance_m: float
    # ---- derived: return_and_latch_adaptation -----------------------------
    return_spring_pivot_xyz: tuple[float, float, float]
    return_spring_standoff_m: float
    latch_parent_role: str
    latch_eye_bore_r_m: float
    latch_axle_r_m: float
    latch_support_mode: str
    latch_origin_xyz: tuple[float, float, float]
    # ---- derived: toggle_geometry -----------------------------------------
    link_station_x_m: float
    toggle_span_m: float
    toggle_cheek_offset_m: float
    mimic_offset_rad: float
    mimic_multiplier_eff: float
    # ---- lateral Y bands ---------------------------------------------------
    frame_half_w_m: float
    member_band_w_m: float
    lever_y_outer_m: float
    lever_y_inner_m: float
    throat_die_max_r_m: float
    link_y_centre_m: float
    latch_y_centre_m: float
    # ---- joint efforts (anchor: ram > anvil > drive > latch) ---------------
    ram_effort_eff_n: float
    anvil_effort_eff_n: float
    drive_effort_eff_n: float
    latch_effort_eff_n: float
    name: str = "rivet_squeeze"

    def __getattr__(self, item: str) -> float:
        """Read a clamped independent parameter by its design name.

        `p` holds every independent parameter after it has been clamped into the
        range its OWN active candidate declares, so the build functions can name
        design parameters directly without a second copy of 110 fields.
        """
        values = object.__getattribute__(self, "p")
        if item in values:
            return values[item]
        raise AttributeError(item)


_CONFIG_FIELDS: frozenset[str] = frozenset(f.name for f in fields(Config))


def _active_candidates(cfg: Config) -> tuple[str, ...]:
    return (
        cfg.yoke_frame,
        cfg.squeeze_mechanism,
        cfg.head_module,
        cfg.return_element,
        cfg.handle_lock,
    )


def _active_domain(cfg: Config) -> dict[str, object]:
    domain: dict[str, object] = {}
    for candidate in _active_candidates(cfg):
        domain.update(_CANDIDATE_PARAMS[candidate])
    return domain


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x0611_5219_5EE2)
    base = Config(
        yoke_frame=choices["yoke_frame"],
        squeeze_mechanism=choices["squeeze_mechanism"],
        head_module=choices["head_module"],
        return_element=choices["return_element"],
        handle_lock=choices["handle_lock"],
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"rivet_squeeze_seed_{seed}",
    )
    sampled: dict[str, object] = {}
    for name, domain in sorted(_active_domain(base).items()):
        if isinstance(domain, list):
            sampled[name] = domain[rng.randrange(len(domain))]
        else:
            low, high = domain
            sampled[name] = round(rng.uniform(float(low), float(high)), 6)
    return Config(**{**base.__dict__, **sampled})


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _resolve_independent(cfg: Config) -> dict[str, float]:
    """Clamp every parameter to the range its OWN active candidate declares."""
    domain = _active_domain(cfg)
    out: dict[str, float] = {}
    for field in fields(Config):
        value = getattr(cfg, field.name)
        if field.name not in domain:
            out[field.name] = value
            continue
        spec = domain[field.name]
        if isinstance(spec, list):
            out[field.name] = value if value in spec else spec[len(spec) // 2]
        else:
            out[field.name] = _clamp(float(value), float(spec[0]), float(spec[1]))
    return out


def _beam_heights(p: dict[str, float], *, built_up: bool) -> tuple[float, float]:
    """Upper / lower jaw beam section heights.

    `deep_c_yoke_forging` and `compact_straight_head` declare these as their own
    independent parameters (source 001 L65-L88 rect(96,30) / rect(76,22)); the
    cut-throat and alligator families take the Config defaults, which is what
    002's outer silhouette leaves above and below its throat cut (L52-L77).

    In the built-up families the rounded nose boss is unioned onto the beam end
    (001 L70-L75 `circle(15)` on a rect of half-height 15), so a boss larger
    than half the section makes the BEAM taller.  The real section height has
    to account for that, or everything that seats on the jaw top -- the ram cap,
    the screw-press register pocket -- would be derived against a face that is
    not the outer one.
    """
    upper = float(p["upper_beam_h_m"])
    lower = float(p["lower_beam_h_m"])
    if built_up:
        boss = 2.0 * float(p["jaw_boss_r_m"])
        upper = max(upper, boss)
        lower = max(lower, boss)
    return upper, lower


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()
    TEMPLATE_DOMAIN.validate(
        {
            "yoke_frame": cfg.yoke_frame,
            "squeeze_mechanism": cfg.squeeze_mechanism,
            "head_module": cfg.head_module,
            "return_element": cfg.return_element,
            "handle_lock": cfg.handle_lock,
        }
    )
    if cfg.palette_style not in PALETTES:
        raise ValueError(f"unknown palette_style {cfg.palette_style!r}")
    p = _resolve_independent(cfg)

    frame = cfg.yoke_frame
    mech = cfg.squeeze_mechanism
    head = cfg.head_module
    ret = cfg.return_element
    lock = cfg.handle_lock

    # ---- contact_policy ----------------------------------------------------
    connection_overlap_m = _CONNECT
    intra_part_embed_m = _EMBED
    running_fit_min_m = _RUNNING
    mesh_chord_tol_m = connection_overlap_m * 0.6

    # ---- pin_bore_fit ------------------------------------------------------
    # host_bore_r = member_bore_r + 0.4 mm and pin_r = member_bore_r - 0.6 mm,
    # both inverted from source 001 (frame bore 0.0072 L99-L104, lever bore
    # 0.0068 L150-L154, pin 0.0062 L312) -- the only record in the pool that
    # needs no allowance.  The pin ends up clearing the FRAME bore by 1.0 mm.
    main_pivot_bore_r_m = float(p["main_pivot_bore_r_m"])
    lever_pivot_bore_r_m = main_pivot_bore_r_m - 0.0004
    main_pivot_pin_r_m = lever_pivot_bore_r_m - 0.0006
    link_eye_r_m = float(p["link_eye_r_m"])
    link_pin_r_m = link_eye_r_m - 0.0006
    frame_width_m = float(p["frame_width_m"])
    lever_plate_width_m = float(p["lever_plate_width_m"])
    lever_standoff_m = 0.0010 if lever_plate_width_m < frame_width_m else 0.0
    lever_fork_slot_w_m = frame_width_m + 0.0020
    # DELIBERATE DEPARTURE, documented.  The pool offers three stand-off
    # solutions (SourceMap "Lever lateral stand-off"); this rebuild always uses
    # 001's OFFSET PLATE (L293/L305, 1.0 mm air gap) rather than 002's forked
    # root, because an outboard plate keeps the lever in a Y band the frame
    # never enters at ANY pose of ANY of the 1440 combinations, while a fork
    # would have to straddle a frame whose grip length is itself derived.  The
    # fork slot width stays derived and is used for real: it is the width of the
    # lever relief slot alligator_jaw cuts through its cheeks (L129-L135).
    lateral_gap_m = max(lever_standoff_m, 0.0010)

    # ---- guide_bore_fit ----------------------------------------------------
    upper_die_shaft_r_m = float(p["upper_die_shaft_r_m"])
    anvil_shaft_r_m = upper_die_shaft_r_m - 0.0005
    ram_guide_bore_r_m = upper_die_shaft_r_m + 0.0012
    anvil_guide_bore_r_m = anvil_shaft_r_m + 0.0011
    max_die_step_r_m = min(ram_guide_bore_r_m, anvil_guide_bore_r_m) - 0.0011
    set_collar_r_eff_m = min(float(p["set_collar_r_m"]), max_die_step_r_m)

    # ---- ram_stroke_from_gap ----------------------------------------------
    open_die_gap_m = float(p["open_die_gap_m"])
    # `closing_residual_m` is sampled independently, so it is capped at 60 % of
    # the open gap; the stroke is `gap - residual` and must stay positive.
    # The anvil's symmetric adjustment (001 L428-L429 +-0.003, 002 L421-L422
    # +-0.004) "must not be allowed to close the gap on its own" (SourceMap 3),
    # so it is capped against the open gap and the closing residual is then
    # raised to cover it.  That makes the WORST coupled pose -- ram at full
    # stroke AND anvil fully raised -- still leave 0.4 mm, which is what keeps
    # the closed pose a real gap: `fcl.collide` reports a zero distance as
    # contact, and 001's own closed-pose test already tolerates 0.25 mm of
    # residual gap (L651-L660).  The stroke is still gap - residual, never a
    # free constant.
    anvil_adjust_eff_m = min(float(p["anvil_adjust_range_m"]), (open_die_gap_m - 0.0010) * 0.40)
    closing_residual_eff_m = min(
        max(float(p["closing_residual_m"]), 0.0004 + anvil_adjust_eff_m),
        open_die_gap_m * 0.75,
    )
    ram_travel_m = open_die_gap_m - closing_residual_eff_m
    die_tip_r_m = float(p["die_tip_r_m"])
    if head == "rotating_set_holder":
        upper_die_stack_h_m = float(p["upper_holder_h_m"]) + die_tip_r_m * 2.0
        lower_die_stack_h_m = float(p["lower_holder_h_m"]) + die_tip_r_m * 2.0
    else:
        upper_die_stack_h_m = die_tip_r_m * 3.0
        lower_die_stack_h_m = die_tip_r_m * 3.0

    # Drive authority.  screw_press delivers turns x lead; the source's pi rad
    # over 0.00175 m/turn is 0.875 mm (L293/L379), well under plain_die_pair's
    # stroke, so the MECHANISM widens its own turn range rather than the head
    # module shrinking its gap -- the design's stated resolution of risk 2.
    screw_turn_range_eff_rad = float(p["screw_turn_range_rad"])
    lead_m_per_turn = float(p["lead_m_per_turn"])
    if mech == "screw_press":
        needed_turns = ram_travel_m / max(lead_m_per_turn, 1e-6) * 2.0 * math.pi
        screw_turn_range_eff_rad = max(screw_turn_range_eff_rad, needed_turns)
        ram_travel_available_m = screw_turn_range_eff_rad / (2.0 * math.pi) * lead_m_per_turn
    elif mech == "eccentric_cam":
        ram_travel_available_m = float(p["cam_eccentricity_m"]) * 2.0
    else:
        ram_travel_available_m = ram_travel_m

    built_up_beams = frame in ("deep_c_yoke_forging", "compact_straight_head", "alligator_jaw")
    upper_beam_h_m, lower_beam_h_m = _beam_heights(p, built_up=built_up_beams)
    clip_thickness_m = float(p["clip_thickness_m"])
    min_pad_m = 0.0018 + (clip_thickness_m + 0.0010 if head == "quick_change_yoke_clip" else 0.0)
    # DELIBERATE DEPARTURE, documented.  The design writes
    # throat_stroke_clearance = jaw_throat_height - (gap + stacks); that
    # expression goes NEGATIVE at legitimate corners of the declared domain
    # (open_die_gap 0.015 with die_tip_r 0.0078 needs 0.062 m against
    # compact_straight_head's 0.024 m floor), and TemplateDomain has no
    # compatibility gates.  The design's own assembly note settles it: "the
    # frame's beam faces are placed from upper_jaw_underside_z_m /
    # lower_jaw_top_z_m, so the throat grows with the head module instead of
    # being a fixed silhouette number".  So the stack sets the opening and
    # jaw_throat_height_m scales the clearance on top of it, which keeps the
    # clearance strictly positive for all 1440 combinations while leaving the
    # frame parameter a real, monotone structural effect.
    throat_pad_m = min_pad_m + float(p["jaw_throat_height_m"]) * 0.10
    die_span_m = open_die_gap_m + upper_die_stack_h_m + lower_die_stack_h_m
    # The lower beam face additionally clears the anvil's DOWNWARD travel.  The
    # ram retracts away from its own beam, but the anvil's full negative
    # adjustment drives its turned stack -- which is wider than the guide bore
    # by construction -- straight into the lower jaw unless the face is placed
    # from the moving part's envelope (MECHANICAL_PRIORS 7) rather than from its
    # rest height.  001 L428-L429 and 002 L421-L422 both give the anvil a
    # symmetric range, so this is a real pose of every seed, not a corner.
    lower_travel_pad_m = 0.0 if mech == "direct_jaw_lever" else anvil_adjust_eff_m
    upper_jaw_underside_z_m = open_die_gap_m * 0.5 + upper_die_stack_h_m + throat_pad_m
    lower_jaw_top_z_m = -(
        open_die_gap_m * 0.5 + lower_die_stack_h_m + throat_pad_m + lower_travel_pad_m
    )
    throat_open_m = upper_jaw_underside_z_m - lower_jaw_top_z_m
    throat_stroke_clearance_m = throat_open_m - die_span_m
    upper_beam_top_z_m = upper_jaw_underside_z_m + upper_beam_h_m
    lower_beam_bottom_z_m = lower_jaw_top_z_m - lower_beam_h_m
    # `alligator_jaw` welds a vertical rivet-set receiver onto the jaw tip
    # (L195/L200), so everything that seats on top of the head -- the ram cap,
    # the screw-press register pocket and its drive hub -- stacks above the
    # receiver rather than above the bare beam.
    upper_seat_z_m = upper_beam_top_z_m + (
        float(p["receiver_len_m"]) if frame == "alligator_jaw" else 0.0
    )
    # Under `direct_jaw_lever` the swinging jaw does the squeezing and the upper
    # member is the short screw adjustment the source keeps (alligator L360-L365,
    # travel 0..0.003 m); the two closures must sum to less than the open gap.
    upper_die_travel_m = min(ram_travel_m, 0.0025) if mech == "direct_jaw_lever" else ram_travel_m

    # Guide engagement: source 002 L515-L523 keeps the ram >= 0.025 m inside its
    # bore at every pose, so the bore is at least the stroke plus that
    # engagement (MECHANICAL_PRIORS 7 -- derived from the moving envelope).
    ram_guide_depth_m = max(0.025, ram_travel_m + open_die_gap_m + 0.015)
    anvil_guide_depth_m = max(0.020, anvil_adjust_eff_m * 2.0 + 0.015)

    # ---- die_coaxiality ----------------------------------------------------
    die_station_x_m = float(p["die_station_x_m"])
    die_axis_x_m = -die_station_x_m
    die_axis_y_m = 0.0
    upper_die_tip_offset_m = open_die_gap_m * 0.5
    lower_die_tip_offset_m = open_die_gap_m * 0.5
    lower_die_parent_role = "moving_jaw" if mech == "direct_jaw_lever" else "frame"
    die_retention_z_m = upper_die_tip_offset_m + die_tip_r_m * 1.5
    die_retention_r_m = min(max_die_step_r_m, die_tip_r_m * 2.2)

    # ---- counterbore_seats -------------------------------------------------
    frame_half_w_m = frame_width_m * 0.5
    retaining_collar_r_m = min(float(p["retaining_collar_r_m"]), frame_half_w_m * 0.9)
    anvil_collar_counterbore_r_m = retaining_collar_r_m + 0.0008
    # The design's 6.5 mm + 0.2 mm pocket is the source's own declared
    # penetration (002 L444-L463).  The pocket must also swallow the anvil's
    # FULL symmetric adjustment or the collar leaves it at one extreme, so the
    # envelope term is added per MECHANICAL_PRIORS 7 and the pocket is clamped
    # so it never breaks through the beam.
    anvil_collar_counterbore_h_m = min(
        0.0065 + 0.0008 + 2.0 * anvil_adjust_eff_m, lower_beam_h_m - 0.0030
    )
    register_r_m = float(p["register_r_m"])
    register_h_m = float(p["register_h_m"])
    screw_register_counterbore_r_m = register_r_m + 0.0008
    screw_register_counterbore_h_m = register_h_m + 0.0008
    tommy_bore_r_m = float(p["tommy_bore_r_m"])
    tommy_bushing_r_m = tommy_bore_r_m - 0.0006
    set_through_bore_r_m = set_collar_r_eff_m + 0.0010 if head == "quick_change_yoke_clip" else 0.0

    # ---- grip_closure ------------------------------------------------------
    # `fixed_grip_is_separate_part` is 'no' for ALL six mechanisms: 001
    # (L250-L260), 003 (L177-L186) and their eight forks make the fixed grip a
    # VISUAL ON THE FRAME, and welding it in removes allow_overlap site 4
    # outright.  eccentric_cam's reaction bracket is FIXED to the frame either
    # way, so the merge costs it nothing.
    fixed_grip_is_separate_part = "no"
    fixed_grip_root_x_m = frame_width_m * 0.6
    # `long_c_yoke_throat` proves nose reach and die station are two parameters
    # (it lengthens the frame to 0.160 while keeping the station at 0.124), but
    # the nose can never fall SHORT of the station or the jaw lands would hang
    # in air.  The authored reach is therefore a floor-limited value, not a
    # replaced one, so the parameter keeps its full structural effect upward.
    frame_reach_m = max(
        float(p["frame_reach_m"]), die_station_x_m + float(p["jaw_boss_r_m"]) + 0.008
    )
    lever_travel_rad = float(p["lever_travel_rad"])
    if mech == "direct_jaw_lever":
        # The handle IS the jaw, so the arm is the jaw's own reach (source
        # L274: the outline starts at x = -190 mm) and the >= 25 mm hand-lever
        # travel bound does not apply -- that is why this candidate carries
        # `rivet_squeeze_direct_jaw_identity` instead.  Its arc is additionally
        # capped so the swinging set closes exactly onto the upper die instead
        # of driving through it, which is the mechanical reason the source
        # collapses lever travel from 24 deg to 2 deg (L331).
        grip_lever_arm_m = float(p["jaw_reach_m"])
        jaw_rise_m = max(open_die_gap_m - upper_die_travel_m - 0.0004, 0.0005)
        lever_travel_rad = min(
            lever_travel_rad,
            math.asin(_clamp(jaw_rise_m / max(die_station_x_m, 1e-6), 0.0, 0.5)),
        )
    elif mech == "screw_press":
        lever_travel_rad = 0.0
        grip_lever_arm_m = frame_reach_m * 0.9
    else:
        # 0.031 rather than the design's 0.026: the >= 25 mm bound is on the
        # VERTICAL drop R*(sin(phi) - sin(phi - travel)), which is strictly less
        # than the arc R*travel, so the arc target carries the cos margin.
        grip_lever_arm_m = max(0.031 / max(lever_travel_rad, 1e-6), frame_reach_m * 0.9)
    grip_travel_m = lever_travel_rad * grip_lever_arm_m
    grip_section_w_m = frame_width_m * 1.1
    fixed_grip_len_m = min(
        max(grip_travel_m * 3.2, grip_lever_arm_m * 0.45),
        max(grip_lever_arm_m - fixed_grip_root_x_m, 0.03),
    )
    closed_grip_gap_m = 0.0025
    fixed_grip_centre_z_m = -(grip_section_w_m * 0.5 + 0.004)
    # Rest angle of the moving grip, solved BACKWARDS from the closed pose so
    # the closed gap lands on `closed_grip_gap_m` exactly: rotating by theta
    # about +Y takes a point at radius R and angle phi to z = R*sin(phi-theta),
    # so phi = travel + asin(z_closed / R).  001 L638-L647 asserts 1-5 mm and
    # 002 L664 a 0.5 mm minimum; both hold with margin at 2.5 mm.
    z_closed = fixed_grip_centre_z_m + grip_section_w_m + closed_grip_gap_m
    grip_phi_rad = lever_travel_rad + math.asin(
        _clamp(z_closed / max(grip_lever_arm_m, 1e-6), -0.9, 0.9)
    )
    moving_grip_centre_z_m = grip_lever_arm_m * math.sin(grip_phi_rad)
    moving_grip_centre_x_m = grip_lever_arm_m * math.cos(grip_phi_rad)
    grip_drop_m = moving_grip_centre_z_m - z_closed
    moving_grip_stop_x_m = fixed_grip_root_x_m + closed_grip_gap_m + grip_section_w_m

    # ---- cam_reaction_adaptation ------------------------------------------
    reaction_bracket_required = "yes" if mech == "eccentric_cam" else "no"
    reaction_pin_r_m = float(p["reaction_pin_r_m"])
    cam_thickness_m = float(p["cam_thickness_m"])
    bracket_thickness_m = float(p["bracket_thickness_m"])
    reaction_bracket_x_m = reaction_pin_r_m * 8.3
    reaction_bracket_offset_y_m = cam_thickness_m * 0.5 + lateral_gap_m + bracket_thickness_m * 0.5
    cam_bearing_clearance_m = 0.0002

    # Largest turning either die presents inside the open throat -- what any
    # frame-borne feature in the throat has to clear.
    throat_die_max_r_m = max(
        die_tip_r_m,
        float(p["holder_r_m"]) if head == "stepped_cylinder_dies" else 0.0,
        float(p["collar_across_flats_m"]) * 0.62 if head == "rotating_set_holder" else 0.0,
        set_collar_r_eff_m if head == "quick_change_yoke_clip" else 0.0,
    )

    # ---- lateral Y bands ---------------------------------------------------
    # The frame is not a flat plate: its moulded grip is 1.1 x the forging width
    # (001 builds both grips at 0.027 m on a 0.020 m frame, L176/L208) and the
    # cam candidate grows a reaction bracket outboard of the cheek.  The lever
    # band is measured from the widest of those, not from the plate, so the
    # 1.0 mm stand-off 001 (L293/L305) and 003 (L308) build is real everywhere.
    frame_outer_y_m = max(
        frame_half_w_m,
        grip_section_w_m * 0.5,
        reaction_bracket_offset_y_m if reaction_bracket_required == "yes" else 0.0,
    )
    lever_y_near_m = -(frame_outer_y_m + lateral_gap_m)
    # The moving member's plate thickness is CANDIDATE-SCOPED: four mechanisms
    # own `lever_plate_width_m` (001 L147 0.008, 002 L230/L276 0.044) but
    # `direct_jaw_lever` owns `jaw_thickness_m` instead (alligator L298:
    # `_front_plate(..., 12.0)`) and `screw_press` carries a turned hub, not a
    # plate.  Deriving the band from a parameter the ACTIVE candidate does not
    # own leaves whatever is welded to the member's outer face -- the latch
    # axle -- hanging in air at some corner of the declared ranges.  001 also
    # builds both grips at 0.027 m on a 0.020 m frame (L176/L208), so the
    # moulded grip is routinely thicker than the plate it sits on; the band is
    # therefore the widest piece the member actually carries.
    if mech == "direct_jaw_lever":
        member_plate_width_m = float(p["jaw_thickness_m"])
    elif mech == "screw_press":
        member_plate_width_m = float(p["drive_hub_r_m"]) * 2.0
    else:
        member_plate_width_m = lever_plate_width_m
    member_band_w_m = member_plate_width_m
    if _MECH_HAS_HAND_LEVER[mech]:
        member_band_w_m = max(member_band_w_m, grip_section_w_m)
    lever_y_far_m = lever_y_near_m - member_band_w_m
    link_thickness_m = float(p["link_thickness_m"])
    link_y_centre_m = -(
        abs(lever_y_far_m)
        + lateral_gap_m
        + link_thickness_m * 0.5
        + (float(p["link_cheek_offset_m"]) - 0.016) * 0.5
    )

    # ---- return_and_latch_adaptation --------------------------------------
    wire_r_m = float(p["wire_r_m"])
    if mech == "screw_press":
        # No handle pivot, but the drive head IS a real revolute about the
        # squeeze axis (L287-L288), so the coil moves onto that station.
        return_spring_pivot_xyz = (die_axis_x_m, 0.0, upper_jaw_underside_z_m)
    else:
        return_spring_pivot_xyz = (0.0, 0.0, 0.0)
    return_spring_standoff_m = lever_plate_width_m * 0.5 + 0.0017
    latch_parent_role = (
        "moving_lever" if (lock == "wire_hook_latch" and mech != "screw_press") else "frame"
    )
    latch_eye_bore_r_m = (
        float(p["eye_id_r_m"]) if lock == "eye_and_wire_loop_latch" else wire_r_m * 1.8
    )
    latch_axle_r_m = latch_eye_bore_r_m - 0.0002
    latch_support_mode = "allow_isolated_part"
    eye_thickness_m = float(p["eye_thickness_m"])
    frame_extra_out_m = (
        float(p["axial_advance_m"]) + 2.0 * wire_r_m if ret == "torsion_handle_spring" else 0.0012
    )
    if latch_parent_role == "frame":
        latch_y_centre_m = frame_half_w_m + frame_extra_out_m + 0.0018 + eye_thickness_m * 0.5
        latch_origin_xyz = (
            fixed_grip_root_x_m + fixed_grip_len_m * 0.55,
            latch_y_centre_m,
            fixed_grip_centre_z_m,
        )
    else:
        # 001 parents its hook to the MOVING handle (L453-L458); it therefore
        # rides the lever's own outboard band, beyond the compound link so no
        # combination can bring the two together.
        latch_y_centre_m = link_y_centre_m - link_thickness_m * 0.5 - 0.0018 - eye_thickness_m * 0.5
        latch_origin_xyz = (
            moving_grip_centre_x_m * 0.55,
            latch_y_centre_m,
            moving_grip_centre_z_m * 0.55,
        )

    # ---- toggle_geometry ---------------------------------------------------
    link_station_x_m = grip_lever_arm_m * 0.13
    toggle_span_m = math.hypot(die_station_x_m + link_station_x_m, upper_jaw_underside_z_m)
    toggle_cheek_offset_m = frame_half_w_m + lateral_gap_m + link_thickness_m * 0.5
    mimic_offset_rad = 0.0
    mimic_multiplier_eff = float(p["mimic_multiplier"])

    # ---- effort hierarchy: ram > anvil > drive > latch (anchor 7) ----------
    ram_effort_eff_n = float(p["ram_effort_n"])
    anvil_effort_eff_n = min(float(p["anvil_effort_n"]), ram_effort_eff_n * 0.5)
    drive_base = 180.0 if mech == "screw_press" else float(p["lever_effort_n"])
    drive_effort_eff_n = min(drive_base, anvil_effort_eff_n * 0.5)
    latch_effort_eff_n = min(float(p["latch_effort_n"]), drive_effort_eff_n * 0.1)

    return ResolvedConfig(
        yoke_frame=frame,
        squeeze_mechanism=mech,
        head_module=head,
        return_element=ret,
        handle_lock=lock,
        palette_style=cfg.palette_style,
        palette=PALETTES[cfg.palette_style],
        p=p,
        connection_overlap_m=connection_overlap_m,
        intra_part_embed_m=intra_part_embed_m,
        running_fit_min_m=running_fit_min_m,
        mesh_chord_tol_m=mesh_chord_tol_m,
        lever_pivot_bore_r_m=lever_pivot_bore_r_m,
        main_pivot_pin_r_m=main_pivot_pin_r_m,
        link_pin_r_m=link_pin_r_m,
        lever_standoff_m=lever_standoff_m,
        lever_fork_slot_w_m=lever_fork_slot_w_m,
        anvil_shaft_r_m=anvil_shaft_r_m,
        ram_guide_bore_r_m=ram_guide_bore_r_m,
        anvil_guide_bore_r_m=anvil_guide_bore_r_m,
        max_die_step_r_m=max_die_step_r_m,
        set_collar_r_eff_m=set_collar_r_eff_m,
        ram_guide_depth_m=ram_guide_depth_m,
        anvil_guide_depth_m=anvil_guide_depth_m,
        die_axis_x_m=die_axis_x_m,
        die_axis_y_m=die_axis_y_m,
        upper_die_tip_offset_m=upper_die_tip_offset_m,
        lower_die_tip_offset_m=lower_die_tip_offset_m,
        lower_die_parent_role=lower_die_parent_role,
        die_retention_z_m=die_retention_z_m,
        die_retention_r_m=die_retention_r_m,
        closing_residual_eff_m=closing_residual_eff_m,
        anvil_adjust_eff_m=anvil_adjust_eff_m,
        upper_die_travel_m=upper_die_travel_m,
        upper_seat_z_m=upper_seat_z_m,
        ram_travel_m=ram_travel_m,
        ram_travel_available_m=ram_travel_available_m,
        screw_turn_range_eff_rad=screw_turn_range_eff_rad,
        upper_die_stack_h_m=upper_die_stack_h_m,
        lower_die_stack_h_m=lower_die_stack_h_m,
        upper_jaw_underside_z_m=upper_jaw_underside_z_m,
        lower_jaw_top_z_m=lower_jaw_top_z_m,
        throat_open_m=throat_open_m,
        throat_stroke_clearance_m=throat_stroke_clearance_m,
        upper_beam_top_z_m=upper_beam_top_z_m,
        lower_beam_bottom_z_m=lower_beam_bottom_z_m,
        upper_beam_bearing_len_m=max(0.030, die_station_x_m * 0.55),
        lower_beam_bearing_len_m=max(0.026, die_station_x_m * 0.50),
        upper_beam_h_eff_m=upper_beam_h_m,
        lower_beam_h_eff_m=lower_beam_h_m,
        frame_reach_eff_m=frame_reach_m,
        anvil_collar_counterbore_r_m=anvil_collar_counterbore_r_m,
        anvil_collar_counterbore_h_m=anvil_collar_counterbore_h_m,
        screw_register_counterbore_r_m=screw_register_counterbore_r_m,
        screw_register_counterbore_h_m=screw_register_counterbore_h_m,
        tommy_bushing_r_m=tommy_bushing_r_m,
        set_through_bore_r_m=set_through_bore_r_m,
        fixed_grip_is_separate_part=fixed_grip_is_separate_part,
        fixed_grip_root_x_m=fixed_grip_root_x_m,
        grip_lever_arm_m=grip_lever_arm_m,
        grip_travel_m=grip_travel_m,
        fixed_grip_len_m=fixed_grip_len_m,
        grip_section_w_m=grip_section_w_m,
        closed_grip_gap_m=closed_grip_gap_m,
        fixed_grip_centre_z_m=fixed_grip_centre_z_m,
        moving_grip_centre_z_m=moving_grip_centre_z_m,
        moving_grip_centre_x_m=moving_grip_centre_x_m,
        moving_grip_stop_x_m=moving_grip_stop_x_m,
        lever_travel_eff_rad=lever_travel_rad,
        grip_phi_rad=grip_phi_rad,
        grip_drop_m=grip_drop_m,
        reaction_bracket_required=reaction_bracket_required,
        reaction_bracket_x_m=reaction_bracket_x_m,
        reaction_bracket_offset_y_m=reaction_bracket_offset_y_m,
        cam_bearing_clearance_m=cam_bearing_clearance_m,
        return_spring_pivot_xyz=return_spring_pivot_xyz,
        return_spring_standoff_m=return_spring_standoff_m,
        latch_parent_role=latch_parent_role,
        latch_eye_bore_r_m=latch_eye_bore_r_m,
        latch_axle_r_m=latch_axle_r_m,
        latch_support_mode=latch_support_mode,
        latch_origin_xyz=latch_origin_xyz,
        link_station_x_m=link_station_x_m,
        toggle_span_m=toggle_span_m,
        toggle_cheek_offset_m=toggle_cheek_offset_m,
        mimic_offset_rad=mimic_offset_rad,
        mimic_multiplier_eff=mimic_multiplier_eff,
        frame_half_w_m=frame_half_w_m,
        member_band_w_m=member_band_w_m,
        lever_y_outer_m=lever_y_far_m,
        lever_y_inner_m=lever_y_near_m,
        throat_die_max_r_m=throat_die_max_r_m,
        link_y_centre_m=link_y_centre_m,
        latch_y_centre_m=latch_y_centre_m,
        ram_effort_eff_n=ram_effort_eff_n,
        anvil_effort_eff_n=anvil_effort_eff_n,
        drive_effort_eff_n=drive_effort_eff_n,
        latch_effort_eff_n=latch_effort_eff_n,
        name=cfg.name,
    )


def slot_choices_for_config(r: Config | ResolvedConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("yoke_frame", r.yoke_frame),
        ("squeeze_mechanism", r.squeeze_mechanism),
        ("head_module", r.head_module),
        ("return_element", r.return_element),
        ("handle_lock", r.handle_lock),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Geometry helpers.  Everything is authored directly in METRES; the source
# records mix millimetre workplanes with `unit_scale=MM` (001/003) and metre
# workplanes (002), and normalising on metres removes a whole class of unit
# bugs from a template that has to combine both families.
# ===========================================================================
def _xz_plate(points: list[tuple[float, float]], width: float, fillet: float = 0.0) -> cq.Workplane:
    """Extrude an XZ side silhouette symmetrically through the tool width.

    This is the pool's universal frame primitive: `_plate_from_profile`
    (001 L25-L35) and `_side_extrusion` (002 L20-L31) are the same operation,
    the latter with an optional `|Y` edge fillet.
    """
    solid = cq.Workplane("XZ").polyline(points).close().extrude(width / 2.0, both=True)
    if fillet > 0.0:
        try:
            solid = solid.edges("|Y").fillet(fillet)
        except Exception:
            # A fillet larger than a local feature is a cosmetic loss, never a
            # reason to fail a combination (TemplateDomain has no gates).
            pass
    return solid


def _y_cyl(x: float, z: float, radius: float, length: float) -> cq.Workplane:
    """Cylinder centred on (x, 0, z) with its axis along Y -- 002 L34-L46."""
    return cq.Workplane("XZ").center(x, z).circle(radius).extrude(length / 2.0, both=True)


def _z_cyl(x: float, y: float, radius: float, z0: float, z1: float) -> cq.Workplane:
    """Cylinder on the squeeze axis, from z0 to z1."""
    return (
        cq.Workplane("XY")
        .center(x, y)
        .circle(radius)
        .extrude(max(z1 - z0, 1e-6))
        .translate((0.0, 0.0, z0))
    )


def _bowed_edge(
    start: tuple[float, float], end: tuple[float, float], count: int, bow: float
) -> list[tuple[float, float]]:
    """`count` points along a gently bowed edge.

    The point count is a declared structural parameter in three frame
    candidates (001's 18-point body, 002's 8-point outer, the fork's 12), so the
    polygon really does gain and lose vertices instead of being resampled onto
    the same shape.
    """
    count = max(2, int(count))
    dx, dz = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dz) or 1.0
    nx, nz = -dz / length, dx / length
    pts: list[tuple[float, float]] = []
    for i in range(count):
        t = i / (count - 1)
        k = math.sin(math.pi * t) * bow
        pts.append((start[0] + dx * t + nx * k, start[1] + dz * t + nz * k))
    return pts


def _frame_extra_centre_y(r: ResolvedConfig, thickness: float) -> float:
    """Y centre of a frame-borne extra welded into the +Y cheek.

    The extra must overlap the frame body by at least `intra_part_embed_m` (the
    connectivity check is intra-part at 1e-6, so a kiss would read as a
    disconnected island) while protruding at most 1.2 mm, which keeps the +Y
    band clear for the latch part.  This is exactly what the pool does with its
    own attached features: 002's `side_cover` is 0.002 m thick at y=+0.015
    against a +0.015 face (L175-L192) and 003's `main_pivot_cap` sits 0.5 mm
    inside its cheek (L209-L214).
    """
    overlap = max(r.intra_part_embed_m, thickness - 0.0012)
    overlap = min(overlap, thickness * 0.9)
    return r.frame_half_w_m - overlap + thickness * 0.5


def _grip_profile(
    r: ResolvedConfig, x0: float, length: float, centre_z: float, half_h: float
) -> list[tuple[float, float]]:
    """Waisted hand-grip side profile.

    Source 001 `_fixed_grip_shape` (L158-L186) and `_moving_grip_shape`
    (L189-L217) are 13/14-point outlines with a pronounced finger waist and six
    tactile ribs unioned into the SAME solid (L178-L185).  Reproduced here as a
    parametric waist so the grip still reads as a moulded hand grip at every
    derived length instead of a plain bar.
    """
    x1 = x0 + length
    pts: list[tuple[float, float]] = [(x0, centre_z - half_h * 0.72)]
    steps = 7
    for i in range(steps + 1):
        t = i / steps
        x = x0 + length * t
        waist = 1.0 - 0.22 * math.sin(math.pi * t * 3.0) ** 2
        pts.append((x, centre_z - half_h * waist))
    pts.append((x1 + half_h * 0.55, centre_z))
    for i in range(steps, -1, -1):
        t = i / steps
        x = x0 + length * t
        waist = 1.0 - 0.18 * math.sin(math.pi * t * 3.0) ** 2
        pts.append((x, centre_z + half_h * waist))
    pts.append((x0, centre_z + half_h * 0.72))
    return pts


def _grip_ribs(
    r: ResolvedConfig, x0: float, length: float, centre_z: float, half_h: float, width: float
) -> cq.Workplane | None:
    """Six tactile ribs unioned into the grip solid -- 001 L178-L185 / L209-L216.

    Decoration density (six ribs) is explicitly NOT a candidate or an N axis per
    the SourceMap, and the ribs are welded into the same body so they cost no
    extra collision solid.
    """
    ribs: cq.Workplane | None = None
    for i in range(6):
        t = 0.30 + 0.55 * (i / 5.0)
        rib = _xz_plate(
            [
                (x0 + length * t - length * 0.028, centre_z - half_h * 1.06),
                (x0 + length * t + length * 0.028, centre_z - half_h * 1.06),
                (x0 + length * t + length * 0.028, centre_z + half_h * 1.06),
                (x0 + length * t - length * 0.028, centre_z + half_h * 1.06),
            ],
            width * 0.72,
        )
        ribs = rib if ribs is None else ribs.union(rib)
    return ribs


# ===========================================================================
# Slot A -- yoke_frame.  Each candidate returns ONE welded CadQuery solid; the
# fixed grip, jaw beams, bosses, cheeks and brackets are all unioned into it,
# and every bore/counterbore is genuinely CUT (MECHANICAL_PRIORS 7).
# ===========================================================================
def _frame_hub_and_tang(r: ResolvedConfig) -> cq.Workplane:
    """Pivot hub and grip-supporting tang shared by all frame candidates.

    The grip remains a visual on this same frame part, as in 001/003, but is
    emitted separately so the source's rubber/paint material break survives.
    """
    hub_r = max(r.main_pivot_bore_r_m * 2.6, r.frame_half_w_m * 0.9)
    solid = _y_cyl(0.0, 0.0, hub_r, r.frame_width_m)

    gz = r.fixed_grip_centre_z_m
    half_h = r.grip_section_w_m * 0.5
    # Tang bridging the hub into the moulded grip -- 001's forging flows into
    # the stationary handle across L46-L59 of its 18-point body profile.
    tang = _xz_plate(
        [
            (-hub_r * 0.35, hub_r * 0.55),
            (r.fixed_grip_root_x_m + 0.004, gz + half_h * 0.85),
            (r.fixed_grip_root_x_m + 0.004, gz - half_h * 0.85),
            (-hub_r * 0.35, -hub_r * 0.55),
        ],
        r.frame_width_m,
    )
    return solid.union(tang)


def _fixed_grip_skin(r: ResolvedConfig) -> cq.Workplane:
    """Thin, separately coloured moulded skin over the stationary hand grip.

    The source photographs all use a strong material break at the hand-contact
    region: black rubber on 001/003 and red moulded handle shells on 002.  The
    structural grip remains welded into the frame, but a same-part visual skin
    preserves that source-readable colour and surface hierarchy.
    """
    length = r.fixed_grip_len_m + 0.0010
    x0 = r.fixed_grip_root_x_m - 0.0005
    half_h = r.grip_section_w_m * 0.5
    width = r.grip_section_w_m
    skin = _xz_plate(_grip_profile(r, x0, length, r.fixed_grip_centre_z_m, half_h), width, 0.0012)
    ribs = _grip_ribs(r, x0, length, r.fixed_grip_centre_z_m, half_h, width)
    return skin if ribs is None else skin.union(ribs)


def _moving_grip_skin(r: ResolvedConfig) -> cq.Workplane:
    """Separately coloured distal grip skin for ordinary squeeze levers."""
    arm = r.grip_lever_arm_m
    half_h = r.grip_section_w_m * 0.5
    width = r.grip_section_w_m
    x0 = arm * 0.42
    length = arm * 0.58
    skin = _xz_plate(_grip_profile(r, x0, length, 0.0, half_h), width, 0.0012)
    ribs = _grip_ribs(r, x0, length, 0.0, half_h, width)
    if ribs is not None:
        skin = skin.union(ribs)
    return _rot_y(_in_band(skin, width, r.lever_y_inner_m), r.grip_phi_rad)


def _frame_side_details(r: ResolvedConfig) -> tuple[cq.Workplane, cq.Workplane]:
    """Far-cheek pivot cap and paired handle fasteners visible in the photos."""
    pivot_side_y = r.frame_half_w_m + 0.00045
    grip_side_y = r.grip_section_w_m * 0.5 + 0.00045
    pivot_cap = _y_cyl(
        0.0,
        0.0,
        max(r.main_pivot_pin_r_m * 1.45, 0.0062),
        0.0014,
    ).translate((0.0, pivot_side_y, 0.0))
    fastener_r = max(0.0022, r.main_pivot_pin_r_m * 0.48)
    fasteners = _y_cyl(
        r.fixed_grip_root_x_m + r.fixed_grip_len_m * 0.18,
        r.fixed_grip_centre_z_m + r.grip_section_w_m * 0.22,
        fastener_r,
        0.0012,
    ).translate((0.0, grip_side_y, 0.0))
    fasteners = fasteners.union(
        _y_cyl(
            r.fixed_grip_root_x_m + r.fixed_grip_len_m * 0.31,
            r.fixed_grip_centre_z_m - r.grip_section_w_m * 0.18,
            fastener_r * 0.78,
            0.0012,
        ).translate((0.0, grip_side_y, 0.0))
    )
    return pivot_cap, fasteners


def _frame_jaw_beams(r: ResolvedConfig, *, upper_x0: float, lower_x0: float) -> cq.Workplane:
    """Built-up jaw beams with rounded nose bosses.

    Source 001 L64-L88: upper `rect(96,30)@(-82,375)` unioned with
    `circle(15)@(-130,375)`, lower `rect(76,22)@(-72,311)` with
    `circle(11)@(-110,311)`.  `compact_straight_head` L68-L91 keeps the
    construction and shortens both beams (52x30 / 48x24) while pulling the
    bosses in from -130/-110 mm to -76/-72 mm.
    """
    ubh, lbh = r.upper_beam_h_eff_m, r.lower_beam_h_eff_m
    boss_r = float(r.p["jaw_boss_r_m"])
    nose_x = r.die_axis_x_m
    upper_h = max(ubh, 2.0 * boss_r)
    lower_h = max(lbh, 2.0 * boss_r)
    upper = _xz_plate(
        [
            (nose_x - boss_r * 0.2, r.upper_jaw_underside_z_m),
            (upper_x0, r.upper_jaw_underside_z_m),
            (upper_x0, r.upper_jaw_underside_z_m + upper_h),
            (nose_x - boss_r * 0.2, r.upper_jaw_underside_z_m + upper_h),
        ],
        r.frame_width_m,
    ).union(_y_cyl(nose_x, r.upper_jaw_underside_z_m + upper_h * 0.5, boss_r, r.frame_width_m))
    lower = _xz_plate(
        [
            (nose_x - boss_r * 0.2, r.lower_jaw_top_z_m - lower_h),
            (lower_x0, r.lower_jaw_top_z_m - lower_h),
            (lower_x0, r.lower_jaw_top_z_m),
            (nose_x - boss_r * 0.2, r.lower_jaw_top_z_m),
        ],
        r.frame_width_m,
    ).union(_y_cyl(nose_x, r.lower_jaw_top_z_m - lower_h * 0.5, boss_r, r.frame_width_m))
    return upper.union(lower)


def _frame_spine(r: ResolvedConfig, points: int, x_back: float) -> cq.Workplane:
    """Solid back web joining the two jaw beams to the pivot hub.

    001's 18-point body profile (L40-L60) spans x -50..+35 mm, i.e. it stops
    well short of the die station at -102 mm; the throat is the space the BEAMS
    leave, not a cut.  `body_profile_points` resamples this silhouette.
    """
    hub_r = max(r.main_pivot_bore_r_m * 2.6, r.frame_half_w_m * 0.9)
    x_hub = max(hub_r * 1.15, r.fixed_grip_root_x_m + 0.003)
    top = _bowed_edge(
        (x_back, r.upper_beam_top_z_m), (x_hub, hub_r * 1.05), max(3, points // 2), 0.004
    )
    bot = _bowed_edge(
        (x_hub, -hub_r * 1.05),
        (x_back, r.lower_beam_bottom_z_m),
        max(3, points - points // 2),
        0.004,
    )
    return _xz_plate(top + bot, r.frame_width_m)


def _hub_radius(r: ResolvedConfig) -> float:
    return max(r.main_pivot_bore_r_m * 2.6, r.frame_half_w_m * 0.9)


def _jaw_beam_web(r: ResolvedConfig, land_r: float, *, upper: bool) -> cq.Workplane:
    """Load path from the die station back into the pivot hub.

    001 draws its jaw beams as `rect(96,30)`/`rect(76,22)` running from the nose
    boss into the forged body (L65-L88); 002 leaves the same two beams above and
    below its throat cut (L66-L77).  Both silhouettes here are BOWED polygons,
    so at some parameter combinations the bearing land at the die station is the
    only material at that station and the bow leaves it a separate island.  This
    web is that beam, stated explicitly: it runs from the land to a station well
    inside the pivot hub (which is solid for every candidate), and it dips below
    the jaw face only for x > `x_knee`, which is on the closed side of BOTH
    throat back walls (-0.36 and -0.40 of the die station), so no candidate's
    open throat is filled in.
    """
    hub_r = _hub_radius(r)
    x0 = r.die_axis_x_m - land_r
    x_knee = -r.die_station_x_m * 0.30
    x_hub = hub_r * 0.5
    if upper:
        face, back = r.upper_jaw_underside_z_m, r.upper_beam_top_z_m
        pts = [
            (x0, face),
            (x_knee, face),
            (x_hub, hub_r * 0.10),
            (x_hub, hub_r * 0.55),
            (x_knee, back),
            (x0, back),
        ]
    else:
        face, back = r.lower_jaw_top_z_m, r.lower_beam_bottom_z_m
        pts = [
            (x0, back),
            (x_knee, back),
            (x_hub, -hub_r * 0.55),
            (x_hub, -hub_r * 0.10),
            (x_knee, face),
            (x0, face),
        ]
    return _xz_plate(pts, r.frame_width_m)


def _frame_common_cuts(r: ResolvedConfig, solid: cq.Workplane) -> cq.Workplane:
    """Every bore this category needs, actually cut through material.

    - main pivot bore, 001 L99-L104 (`circle(7.2)` through the side plate);
    - ram guide bore, 001 L108-L114 (`circle(6.4) x 58 mm`, a true clearance
      bore rather than a solid sleeve proxy);
    - anvil guide bore, 001 L115-L121 (`circle(5.6) x 42 mm`);
    - the anvil collar counterbore 002 L444-L463 declared but never machined;
    - the screw-register pocket `screw_press` L497-L516 declared as 3.5 mm of
      penetration;
    - the set through-bore `alligator_jaw` L749-L757 ran through uncut material.
    """
    # Bearing lands at the die station.  Every candidate's silhouette is a bowed
    # polygon, so the material actually present ABOVE the throat at x =
    # die_station is not the nominal beam top; 001 solves the same problem with
    # explicit `circle(15)`/`circle(11)` bosses unioned at the beam ends
    # (L70-L75, L82-L87).  These lands guarantee that the guide bores, the
    # counterbores and anything seated on the jaw top all meet real metal.
    land_r = max(
        r.ram_guide_bore_r_m + 0.0035,
        r.screw_register_counterbore_r_m + 0.0015 if r.squeeze_mechanism == "screw_press" else 0.0,
        r.set_through_bore_r_m + 0.0015,
    )
    solid = solid.union(
        _z_cyl(
            r.die_axis_x_m,
            0.0,
            land_r,
            r.upper_jaw_underside_z_m,
            r.upper_beam_top_z_m,
        )
    )
    solid = solid.union(_jaw_beam_web(r, land_r, upper=True))
    if r.lower_die_parent_role == "frame":
        lower_land_r = max(r.anvil_guide_bore_r_m + 0.0035, r.anvil_collar_counterbore_r_m + 0.0015)
        solid = solid.union(
            _z_cyl(
                r.die_axis_x_m,
                0.0,
                lower_land_r,
                r.lower_beam_bottom_z_m,
                r.lower_jaw_top_z_m,
            )
        )
        solid = solid.union(_jaw_beam_web(r, lower_land_r, upper=False))
    # Local throat relief on the squeeze axis.  Every candidate's jaw underside
    # is a bowed polygon edge, so a little material can sit below the nominal
    # `upper_jaw_underside_z_m` right where the die stack runs; 002 solves the
    # same problem by cutting its throat with a profile WIDER than the body
    # (L66-L77) so the cut goes clean through.  This is that cut, localised.
    relief_w = max(r.throat_die_max_r_m, r.ram_guide_bore_r_m, r.anvil_guide_bore_r_m) + 0.0015
    if r.lower_die_parent_role == "moving_jaw":
        relief_w = max(relief_w, float(r.p["lower_set_boss_r_m"]) * 1.35)
    solid = solid.cut(
        _xz_plate(
            [
                (r.die_axis_x_m - relief_w, r.lower_jaw_top_z_m),
                (r.die_axis_x_m + relief_w, r.lower_jaw_top_z_m),
                (r.die_axis_x_m + relief_w, r.upper_jaw_underside_z_m),
                (r.die_axis_x_m - relief_w, r.upper_jaw_underside_z_m),
            ],
            r.frame_width_m * 3.0,
        )
    )
    solid = solid.cut(_y_cyl(0.0, 0.0, r.main_pivot_bore_r_m, r.frame_width_m * 3.0))
    solid = solid.cut(
        _z_cyl(
            r.die_axis_x_m,
            0.0,
            r.ram_guide_bore_r_m,
            r.upper_jaw_underside_z_m - 0.002,
            r.upper_seat_z_m + 0.040,
        )
    )
    if r.lower_die_parent_role == "frame":
        solid = solid.cut(
            _z_cyl(
                r.die_axis_x_m,
                0.0,
                r.anvil_guide_bore_r_m,
                r.lower_beam_bottom_z_m - 0.030,
                r.lower_jaw_top_z_m + 0.002,
            )
        )
    if r.head_module == "plain_die_pair" and r.anvil_collar_counterbore_h_m > 0.0005:
        solid = solid.cut(
            _z_cyl(
                r.die_axis_x_m,
                0.0,
                r.anvil_collar_counterbore_r_m,
                r.lower_beam_bottom_z_m - 0.001,
                r.lower_beam_bottom_z_m + r.anvil_collar_counterbore_h_m,
            )
        )
    if r.head_module == "quick_change_yoke_clip":
        solid = solid.cut(
            _z_cyl(
                r.die_axis_x_m,
                0.0,
                r.set_through_bore_r_m,
                r.upper_jaw_underside_z_m - 0.002,
                r.upper_seat_z_m + 0.040,
            )
        )
    if r.squeeze_mechanism == "screw_press":
        solid = solid.cut(
            _z_cyl(
                r.die_axis_x_m,
                0.0,
                r.screw_register_counterbore_r_m,
                r.upper_seat_z_m - r.screw_register_counterbore_h_m,
                r.upper_seat_z_m + 0.001,
            )
        )
    if r.reaction_bracket_required == "yes":
        # The cam lobe bears OUTWARD against the reaction bracket, so the frame
        # grows one: 6-point plate + r 0.007 reaction pin + Box bridge, source
        # eccentric_cam L254-L284.  It is welded into the frame because the
        # source's `fixed_handle` is a FIXED child either way.
        bx = r.reaction_bracket_x_m
        by = -r.reaction_bracket_offset_y_m
        bt = float(r.p["bracket_thickness_m"])
        bracket = _xz_plate(
            [
                (bx * 0.28, -r.grip_section_w_m * 0.55),
                (bx * 0.78, -r.grip_section_w_m * 0.68),
                (bx * 1.10, -r.grip_section_w_m * 0.55),
                (bx * 1.10, -r.grip_section_w_m * 0.18),
                (bx * 0.66, r.grip_section_w_m * 0.20),
                (bx * 0.28, r.grip_section_w_m * 0.26),
            ],
            bt,
        ).translate((0.0, by + bt * 0.5, 0.0))
        pin = _y_cyl_span(
            bx,
            -r.grip_section_w_m * 0.42,
            float(r.p["reaction_pin_r_m"]),
            by,
            by + bt * 1.6,
        )
        bridge = _xz_plate(
            [
                (bx * 0.55, -r.grip_section_w_m * 0.10),
                (bx * 1.05, -r.grip_section_w_m * 0.10),
                (bx * 1.05, r.grip_section_w_m * 0.85),
                (bx * 0.55, r.grip_section_w_m * 0.85),
            ],
            bt,
        ).translate((0.0, by + bt * 0.5, 0.0))
        # `reaction_bracket_offset_y_m` is the OUTERMOST station the host may
        # reach on this side, because the lever band is derived from it.  The
        # web, the bridge and the reaction pin are therefore seated flush with
        # the bracket's outer face instead of straddling it.
        web_y0 = by
        web_y1 = r.frame_half_w_m * 0.5
        web = _xz_plate(
            [
                (bx * 0.20, -r.grip_section_w_m * 0.30),
                (bx * 0.62, -r.grip_section_w_m * 0.30),
                (bx * 0.62, r.grip_section_w_m * 0.60),
                (bx * 0.20, r.grip_section_w_m * 0.60),
            ],
            web_y1 - web_y0,
        ).translate((0.0, 0.5 * (web_y0 + web_y1), 0.0))
        solid = solid.union(web).union(bracket).union(bridge).union(pin)
    return solid


def _yoke_frame_deep_c_yoke_forging_build(r: ResolvedConfig) -> cq.Workplane:
    """rec ...001... model.py:L38-L122 -- 18-point body + two built-up jaw beams.

    The body plate is extruded +-10 mm, the two jaw beams (rect + circular nose
    boss) are unioned on, and four bores are cut: the r 8 mm fixture hole at
    (8,365), the r 7.2 mm pivot bore at (0,320) and the two vertical clearance
    bores at x = -102 mm.  One welded solid, one visual.
    """
    x_back = -r.die_station_x_m * 0.40
    solid = _frame_spine(r, int(r.p["body_profile_points"]), x_back)
    solid = solid.union(_frame_jaw_beams(r, upper_x0=x_back + 0.006, lower_x0=x_back + 0.006))
    solid = solid.union(_frame_hub_and_tang(r))
    # The photographed tool's large hanging/fixture hole, a real cut (L93-L98).
    hub_r = max(r.main_pivot_bore_r_m * 2.6, r.frame_half_w_m * 0.9)
    solid = solid.cut(
        _y_cyl(
            -x_back * 0.45,
            hub_r * 0.2 + r.upper_beam_top_z_m * 0.42,
            float(r.p["fixture_hole_r_m"]),
            r.frame_width_m * 3.0,
        )
    )
    return _frame_common_cuts(r, solid)


def _throat_cut_solid(r: ResolvedConfig, points: int, fillet: float, x_back: float) -> cq.Workplane:
    """The subtracted throat profile of the 002 family.

    002 L66-L77 cuts a 5-point relief 0.050 m wide through a 0.030 m body, so it
    cuts clean through instead of leaving a web; `long_c_yoke_throat` L71-L88
    takes the same cut to 13 points for a gently tapering throat with a rounded
    inner heel.  The extra points are spent on the rear wall, which is exactly
    where the fork spends them.
    """
    nose = -(r.frame_reach_eff_m + 0.010)
    back = x_back
    rear = _bowed_edge(
        (back, r.lower_jaw_top_z_m),
        (back, r.upper_jaw_underside_z_m),
        max(3, points - 2),
        -min(0.006, r.throat_open_m * 0.18),
    )
    pts = [(nose, r.lower_jaw_top_z_m)] + rear + [(nose, r.upper_jaw_underside_z_m)]
    return _xz_plate(pts, float(r.p["throat_cut_width_m"]), fillet)


def _yoke_frame_throated_forged_body_build(r: ResolvedConfig) -> cq.Workplane:
    """rec ...002... model.py:L49-L100 -- 8-point outer silhouette, cut throat.

    The inverse construction of 001: a filleted outer body over the whole tool,
    then the throat subtracted with an over-wide cutting profile, then the two
    STOPPED bores at x = -0.124 so both jaw beams remain structural.
    """
    x_back = -r.die_station_x_m * 0.36
    fillet = float(r.p["edge_fillet_m"])
    n = int(r.p["outer_profile_points"])
    hub_r = max(r.main_pivot_bore_r_m * 2.6, r.frame_half_w_m * 0.9)
    x_hub = max(hub_r * 1.15, r.fixed_grip_root_x_m + 0.003)
    top = _bowed_edge(
        (-r.frame_reach_eff_m, r.upper_beam_top_z_m), (x_hub, hub_r * 1.05), max(3, n // 2), 0.005
    )
    bot = _bowed_edge(
        (x_hub, -hub_r * 1.05),
        (-r.frame_reach_eff_m, r.lower_beam_bottom_z_m),
        max(3, n - n // 2),
        0.005,
    )
    solid = _xz_plate(top + bot, r.frame_width_m, fillet)
    solid = solid.cut(
        _throat_cut_solid(r, int(r.p["throat_profile_points"]), fillet * 0.75, x_back)
    )
    solid = solid.union(_frame_hub_and_tang(r))
    return _frame_common_cuts(r, solid)


def _yoke_frame_long_c_yoke_throat_build(r: ResolvedConfig) -> cq.Workplane:
    """rec ..._var_yoke_frame_deep_c_yoke model.py:L49-L114 + L186-L212.

    Fork of `throated_forged_body`: outer 8 -> 12 points, throat 5 -> 13 points
    with the fillet dropped 3 -> 2 mm, and the `side_cover` retopologised from a
    full-body plate into an 11-point heel cheek that deliberately "does not
    bridge across or visually cap the open throat".  The die station stays put,
    which is what proves frame reach and die station are two parameters.
    """
    solid = _yoke_frame_throated_forged_body_build(r)
    # Heel cheek, welded into the +Y face exactly as the source's 0.002 m plate
    # sits half-embedded in a face at y=+0.015 (L207) -- same part, so free.
    n = int(r.p["heel_cheek_points"])
    t = float(r.p["cheek_thickness_m"])
    hub_r = max(r.main_pivot_bore_r_m * 2.6, r.frame_half_w_m * 0.9)
    x_hub = max(hub_r * 1.15, r.fixed_grip_root_x_m + 0.003)
    x0 = -r.die_station_x_m * 0.30
    top = _bowed_edge(
        (x0, r.upper_beam_top_z_m * 0.72), (x_hub, hub_r * 0.85), max(3, n // 2), 0.003
    )
    bot = _bowed_edge(
        (x_hub, -hub_r * 0.85), (x0, r.lower_beam_bottom_z_m * 0.72), max(3, n - n // 2), 0.003
    )
    cheek = _xz_plate(top + bot, t).translate((0.0, _frame_extra_centre_y(r, t), 0.0))
    return solid.union(cheek)


def _yoke_frame_compact_straight_head_build(r: ResolvedConfig) -> cq.Workplane:
    """rec ..._var_yoke_frame_compact_straight_head model.py:L38-L125.

    Fork of `deep_c_yoke_forging`.  Both jaw beams shorten (96x30 -> 52x30 and
    76x22 -> 48x24) and both bosses pull in (-130 -> -76, -110 -> -72), and the
    die station itself is re-derived from -0.102 to -0.065 -- both prismatic
    joint origins move with the geometry, which is where the single
    `die_station_x_m` parameter comes from (its author test asserts the two
    origins are equal to 1e-9 at L614-L625).
    """
    x_back = -r.die_station_x_m * 0.40
    solid = _frame_spine(r, int(r.p["body_profile_points"]), x_back)
    # The compact head's beams are LENGTH-driven rather than running back to the
    # spine, which is the fork's whole structural point.
    upper_x0 = min(x_back + 0.006, r.die_axis_x_m + float(r.p["upper_beam_len_m"]))
    lower_x0 = min(x_back + 0.006, r.die_axis_x_m + float(r.p["lower_beam_len_m"]))
    solid = solid.union(_frame_jaw_beams(r, upper_x0=upper_x0, lower_x0=lower_x0))
    # Straight web tying the shortened beams back into the spine.
    web = _xz_plate(
        [
            (min(upper_x0, lower_x0) - 0.002, r.lower_beam_bottom_z_m),
            (x_back + 0.008, r.lower_beam_bottom_z_m),
            (x_back + 0.008, r.upper_beam_top_z_m),
            (min(upper_x0, lower_x0) - 0.002, r.upper_beam_top_z_m),
        ],
        r.frame_width_m,
    )
    solid = solid.union(web).union(_frame_hub_and_tang(r))
    solid = solid.cut(_throat_cut_solid(r, 5, 0.0, min(upper_x0, lower_x0) - 0.0015))
    return _frame_common_cuts(r, solid)


def _yoke_frame_alligator_jaw_build(r: ResolvedConfig) -> cq.Workplane:
    """rec ..._var_yoke_frame_alligator_jaw model.py:L102-L147 + L193-L203.

    A 25-point casting whose nose runs out to x = -170 mm, forming a long upper
    jaw over the moving lower jaw, plus the barrel receiver re-origined to
    (-0.145, 0.021, 0.329) with `rpy=(0,-pi/2,0)` so the set travels along the
    world squeeze axis instead of outward along a horizontal barrel.  Here the
    receiver is simply built vertical, and the internal lever relief slot
    (L129-L135, `box(70,105,12.5)`) is genuinely cut, as it is in the source.
    """
    n = int(r.p["frame_profile_points"])
    hub_r = max(r.main_pivot_bore_r_m * 2.6, r.frame_half_w_m * 0.9)
    x_hub = max(hub_r * 1.15, r.fixed_grip_root_x_m + 0.003)
    # Long upper jaw: a single deep beam from the hub out past the die station.
    top = _bowed_edge(
        (-r.frame_reach_eff_m, r.upper_beam_top_z_m), (x_hub, hub_r * 1.05), max(3, n // 2), 0.006
    )
    under = _bowed_edge(
        (x_hub, hub_r * 0.2),
        (-r.frame_reach_eff_m, r.upper_jaw_underside_z_m),
        max(3, n - n // 2),
        -0.004,
    )
    solid = _xz_plate(top + under, r.frame_width_m, 0.0024)
    # Short lower beam so the throat still carries an anvil for the five
    # mechanisms that are not `direct_jaw_lever` -- the design's own resolution
    # of the alligator_jaw x screw_press combination.
    lower = _xz_plate(
        [
            (r.die_axis_x_m - float(r.p["jaw_boss_r_m"]), r.lower_beam_bottom_z_m),
            (x_hub, r.lower_beam_bottom_z_m),
            (x_hub, r.lower_jaw_top_z_m),
            (r.die_axis_x_m - float(r.p["jaw_boss_r_m"]), r.lower_jaw_top_z_m),
        ],
        r.frame_width_m,
    )
    solid = solid.union(lower).union(_frame_hub_and_tang(r))
    # Vertical rivet-set receiver welded into the jaw tip -- L195/L200.
    rec_od = max(float(r.p["receiver_od_m"]), r.ram_guide_bore_r_m + 0.0018)
    rec_len = float(r.p["receiver_len_m"])
    solid = solid.union(
        _z_cyl(
            r.die_axis_x_m,
            0.0,
            rec_od,
            r.upper_beam_top_z_m - r.intra_part_embed_m,
            r.upper_beam_top_z_m - r.intra_part_embed_m + rec_len,
        )
    )
    # Genuinely cut lever relief slot, "while retaining two substantial cheek
    # plates" (L129-L135: `box(70,105,12.5)` in a 30 mm forging).  The declared
    # parameter is that 12.5 mm slot WIDTH through Y, so it is clamped to leave
    # real cheeks rather than parting the casting in two -- the source's own
    # `lever_fork_slot_w_m` route would cut this frame clean through.
    slot_w = min(float(r.p["lever_relief_slot_h_m"]), r.frame_width_m - 0.006)
    z_lo = hub_r * 1.25
    z_hi = min(r.upper_jaw_underside_z_m - 0.003, z_lo + hub_r * 1.6)
    if slot_w > 0.002 and z_hi > z_lo + 0.002:
        solid = solid.cut(
            _xz_plate(
                [
                    (x_hub * 0.10, z_lo),
                    (x_hub * 0.92, z_lo),
                    (x_hub * 0.92, z_hi),
                    (x_hub * 0.10, z_hi),
                ],
                slot_w,
            )
        )
    return _frame_common_cuts(r, solid)


_FRAME_BUILDERS = {
    "deep_c_yoke_forging": _yoke_frame_deep_c_yoke_forging_build,
    "throated_forged_body": _yoke_frame_throated_forged_body_build,
    "long_c_yoke_throat": _yoke_frame_long_c_yoke_throat_build,
    "compact_straight_head": _yoke_frame_compact_straight_head_build,
    "alligator_jaw": _yoke_frame_alligator_jaw_build,
}


# ===========================================================================
# Slot C -- head_module.  THE WELD RULE: each die is ONE CadQuery solid emitted
# as ONE visual.  `screw_press` in the source builds its ram from 9 visuals and
# its anvil from 13 (thread crests as separate rings), which is 22 mutually
# embedded collision solids on two ~15 mm parts; the pool's own
# `_rotating_set_holder_shape` (L220-L249) and `_nosepiece_shape` (003 L52-L77)
# already show the better route and it is used for every die here.
#
# Local frame of BOTH die parts is the shared squeeze station
# (die_axis_x_m, 0, 0), so their two prismatic joint origins are identical by
# construction and the category's defining coaxiality assertion
# (`expect_origin_distance(axes="xy", max_dist=0.0005)`, 001 L611-L617) holds
# exactly rather than by luck.  The upper die's working face is at +gap/2 and
# the lower die's at -gap/2, so the rest gap IS `open_die_gap_m`.
# ===========================================================================
def _upper_shank(r: ResolvedConfig, z_from: float) -> cq.Workplane:
    """Guide shank + top cap, common to every upper die form.

    `guide_bore_r = shaft_r + 1.2 mm` (001 L108-L114: bore 0.0064 over a 0.0052
    shaft) is a RUNNING FIT and stays a real gap -- 002 makes both 0.0052 and
    declares `allow_overlap` (L498-L507).  The shank is long enough that the cap
    still clears the beam top at FULL stroke, which is the envelope rule from
    MECHANICAL_PRIORS 7 rather than the source's fixed 0.052 m.
    """
    shaft_r = r.upper_die_shaft_r_m
    if r.squeeze_mechanism == "screw_press":
        # The press screw ends INSIDE the guide bore, below the drive head's
        # seating pocket, so the rotating hub and the translating screw keep a
        # real axial running clearance instead of the source's declared
        # `max_penetration=0.0035` (L497-L516).  Thread crests become a lathed
        # groove in this same solid rather than 7 separate visuals (L352-L358).
        top = r.upper_seat_z_m - r.screw_register_counterbore_h_m - 0.0008
        top = max(top, z_from + 0.010)
        solid = _z_cyl(0.0, 0.0, shaft_r, z_from - r.intra_part_embed_m, top)
        crests = int(r.p["thread_crest_count"])
        crest_r = min(shaft_r + 0.0004, r.max_die_step_r_m)
        span = top - z_from
        for i in range(crests):
            f = (i + 0.5) / crests
            solid = solid.union(
                _z_cyl(0.0, 0.0, crest_r, z_from + span * f, z_from + span * f + span * 0.035)
            )
        return solid
    # Everything the mechanism welds onto the ram head hangs DOWN from the top
    # of the shank, so the shank has to be long enough that the LOWEST of those
    # features still clears the jaw seat at the ram's full stroke.  This is the
    # envelope rule (MECHANICAL_PRIORS 7) rather than 001's fixed 0.052 m.
    feature_h = 0.006
    if r.squeeze_mechanism == "eccentric_cam":
        feature_h = 0.012
    elif r.squeeze_mechanism == "long_toggle_cheek":
        feature_h = max(feature_h, float(r.p["ram_head_w_m"]) * 0.55 + 0.005)
    top = max(
        z_from + r.ram_guide_depth_m,
        r.upper_seat_z_m + r.upper_die_travel_m + 0.003 + feature_h,
    )
    solid = _z_cyl(0.0, 0.0, shaft_r, z_from - r.intra_part_embed_m, top)
    cap_r = min(float(r.p["ram_cap_r_m"]), shaft_r + 0.0045)
    solid = solid.union(_z_cyl(0.0, 0.0, cap_r, top - 0.006, top))
    if r.squeeze_mechanism == "eccentric_cam":
        # Hardened pad the lobe drives -- source eccentric_cam L409-L414
        # (`cam_follower_head`, r 0.0080 x 0.005 on the ram).
        pad_r = min(float(r.p["follower_head_r_m"]), cap_r + 0.0035)
        solid = solid.union(_z_cyl(0.0, 0.0, pad_r, top - 0.011, top - 0.006 + 0.0002))
    if r.squeeze_mechanism == "long_toggle_cheek":
        # `ram_head` Box(0.018,0.020,0.008) + `ram_toggle_pin` r0.0032 x 0.062,
        # source long_toggle_cheek L373-L384: the toggle actually terminates on
        # the ram.  The cross pin is truncated before the link's own Y band so
        # the pair keeps a running clearance instead of the source's declared
        # 0.05 mm press-fit (allow_overlap site 8).
        hw = float(r.p["ram_head_w_m"]) * 0.5
        head_z = top - 0.005 - hw * 0.5
        solid = solid.union(
            _xz_plate(
                [
                    (-hw, head_z - hw * 0.5),
                    (hw, head_z - hw * 0.5),
                    (hw, head_z + hw * 0.5),
                    (-hw, head_z + hw * 0.5),
                ],
                hw * 1.1,
            )
        )
        pin_half = min(
            float(r.p["ram_cross_pin_len_m"]) * 0.5,
            abs(r.link_y_centre_m) - float(r.p["link_thickness_m"]) * 0.5 - r.running_fit_min_m,
        )
        solid = solid.union(_y_cyl(0.0, head_z, r.link_pin_r_m, pin_half * 2.0))
    return solid


def _lower_shank(r: ResolvedConfig, z_from: float) -> cq.Workplane:
    """Guide stem + adjuster tail below the lower beam.

    `anvil bore = shank + 1.1 mm` (001 L115-L121).  The tail starts far enough
    below the beam that the full symmetric adjustment (001 L428-L429 +-0.003,
    002 L421-L422 +-0.004) never drives it into the forging.
    """
    stem_r = r.anvil_shaft_r_m
    tail_top = r.lower_beam_bottom_z_m - r.anvil_adjust_eff_m - 0.002
    stem_bottom = min(z_from - r.anvil_guide_depth_m, tail_top - 0.001)
    return _z_cyl(0.0, 0.0, stem_r, stem_bottom, z_from + r.intra_part_embed_m), tail_top


def _head_module_stepped_cylinder_dies_build(r: ResolvedConfig, *, upper: bool) -> cq.Workplane:
    """rec ...001... model.py:L349-L373 (ram) and L393-L417 (adjustment die).

    Four turnings per part -- shaft, holder, tip, cap on the ram; shank,
    adjuster wheel, holder, tip on the anvil -- and the two tips are the
    IDENTICAL r 0.0035 m, which is the opposed-set signature.  Emitted here as
    one welded solid instead of four primitives.
    """
    tip_r = r.die_tip_r_m
    holder_r = min(float(r.p["holder_r_m"]), r.die_retention_r_m * 1.9)
    steps = int(r.p["stack_step_count"])
    if upper:
        z0 = r.upper_die_tip_offset_m
        solid = _z_cyl(0.0, 0.0, tip_r, z0, z0 + tip_r * 1.2)
        solid = solid.union(
            _z_cyl(
                0.0,
                0.0,
                holder_r,
                z0 + tip_r * 1.2 - r.intra_part_embed_m,
                z0 + r.upper_die_stack_h_m,
            )
        )
        # `stack_step_count` turns the holder into a real stepped stack.
        for i in range(1, max(1, steps - 1)):
            f = i / max(1, steps - 1)
            solid = solid.union(
                _z_cyl(
                    0.0,
                    0.0,
                    holder_r - (holder_r - tip_r) * f * 0.55,
                    z0 + tip_r * 1.2 + (r.upper_die_stack_h_m - tip_r * 1.2) * f * 0.9,
                    z0 + r.upper_die_stack_h_m + 0.0012,
                )
            )
        return solid.union(_upper_shank(r, z0 + r.upper_die_stack_h_m))
    z0 = -r.lower_die_tip_offset_m
    solid = _z_cyl(0.0, 0.0, tip_r, z0 - tip_r * 1.2, z0)
    solid = solid.union(
        _z_cyl(
            0.0, 0.0, holder_r, z0 - r.lower_die_stack_h_m, z0 - tip_r * 1.2 + r.intra_part_embed_m
        )
    )
    stem, tail_top = _lower_shank(r, z0 - r.lower_die_stack_h_m)
    solid = solid.union(stem)
    # Knurled thumb wheel on the shank -- 001 L400-L405.
    wheel_r = float(r.p["adjuster_wheel_r_m"])
    solid = solid.union(_z_cyl(0.0, 0.0, wheel_r, tail_top - 0.006, tail_top))
    return solid


def _head_module_plain_die_pair_build(r: ResolvedConfig, *, upper: bool) -> cq.Workplane:
    """rec ...002... model.py:L345-L357 (ram) and L380-L410 (anvil screw).

    A minimal two-turning ram and a five-turning anvil whose long knurled tail
    below the jaw is what reads as "adjustable anvil".  The r 0.0100 retaining
    collar is the one the source declared 5.0-6.5 mm INSIDE the forging with
    `allow_overlap` (L444-L463); here it seats in a real counterbore with a
    0.5 mm radial and a full-adjustment axial clearance.
    """
    tip_r = r.die_tip_r_m
    if upper:
        z0 = r.upper_die_tip_offset_m
        solid = _z_cyl(0.0, 0.0, tip_r, z0, z0 + r.upper_die_stack_h_m)
        return solid.union(_upper_shank(r, z0 + r.upper_die_stack_h_m))
    z0 = -r.lower_die_tip_offset_m
    solid = _z_cyl(0.0, 0.0, tip_r, z0 - r.lower_die_stack_h_m, z0)
    stem, tail_top = _lower_shank(r, z0 - r.lower_die_stack_h_m)
    solid = solid.union(stem)
    collar_r = min(float(r.p["retaining_collar_r_m"]), r.frame_half_w_m * 0.9)
    pocket_h = r.anvil_collar_counterbore_h_m
    if pocket_h > 0.0005:
        seat_z = r.lower_beam_bottom_z_m + r.anvil_adjust_eff_m + 0.0006
        solid = solid.union(_z_cyl(0.0, 0.0, collar_r, seat_z, seat_z + 0.006))
    knurl_r = float(r.p["knurled_adjuster_r_m"])
    knurl_h = float(r.p["knurled_adjuster_h_m"])
    solid = solid.union(_z_cyl(0.0, 0.0, knurl_r, tail_top - knurl_h, tail_top))
    stop_r = float(r.p["adjuster_stop_r_m"])
    solid = solid.union(
        _z_cyl(0.0, 0.0, stop_r, tail_top - knurl_h - 0.005, tail_top - knurl_h + 0.0005)
    )
    # Knurl flutes, welded into the same body (decoration density, not an N).
    steps = int(r.p["stack_step_count"])
    for i in range(steps):
        f = (i + 0.5) / steps
        solid = solid.union(
            _z_cyl(
                0.0, 0.0, knurl_r + 0.0004, tail_top - knurl_h * (f + 0.06), tail_top - knurl_h * f
            )
        )
    return solid


def _rotating_set_holder_shape(r: ResolvedConfig, height: float) -> cq.Workplane:
    """rec ..._var_head_module_rotating_set_holder model.py:L220-L249, verbatim.

    `circle(5.6).extrude(1.2)` lower land, `polygon(12, 16.8)` grip collar at
    offset 0.9 and height h-1.7, `circle(6.2).extrude(0.8)` upper land, minus a
    `circle(3.55).extrude(1.7)` blind socket at offset -0.05 -- three turnings
    and a socket unioned and cut into ONE solid emitted as ONE visual.  This is
    the pool's own reference welded construction and the reason every die here
    follows it.
    """
    land_r = float(r.p["land_r_m"])
    facets = int(r.p["collar_facets"])
    flats = float(r.p["collar_across_flats_m"])
    lower_land = cq.Workplane("XY").circle(land_r * 0.90).extrude(height * 0.24)
    collar = (
        cq.Workplane("XY")
        .workplane(offset=height * 0.18)
        .polygon(facets, flats)
        .extrude(height * 0.66)
    )
    upper_land = (
        cq.Workplane("XY")
        .workplane(offset=height - height * 0.16)
        .circle(land_r)
        .extrude(height * 0.16)
    )
    holder = lower_land.union(collar).union(upper_land)
    socket = (
        cq.Workplane("XY")
        .workplane(offset=-0.00005)
        .circle(min(float(r.p["socket_r_m"]), land_r * 0.72))
        .extrude(float(r.p["socket_depth_m"]))
    )
    return holder.cut(socket)


def _head_module_rotating_set_holder_build(r: ResolvedConfig, *, upper: bool) -> cq.Workplane:
    """Faceted hand-turnable socket holders -- L220-L249, L388-L399, L444-L455.

    Called at h=5.0 mm for the upper holder (origin z -0.009) and h=4.0 mm for
    the lower one, exactly as the source parameterises it by height.
    """
    # Every step overlaps its neighbour by `intra_part_embed_m`.  A tangent
    # stack would be a WELD THAT NEVER TOOK: CadQuery can keep two touching
    # solids separate and `find_part_geometry_connectivity_findings` works at
    # 1e-6, so the holder would read as a floating island inside the die part.
    tip_r = r.die_tip_r_m
    e = r.intra_part_embed_m
    if upper:
        z0 = r.upper_die_tip_offset_m
        h = float(r.p["upper_holder_h_m"])
        holder_base = z0 + tip_r * 1.2
        solid = _z_cyl(0.0, 0.0, tip_r, z0, holder_base)
        holder = _rotating_set_holder_shape(r, h).rotate((0, 0, 0), (1, 0, 0), 180.0)
        holder_top = holder_base - e + h
        solid = solid.union(holder.translate((0.0, 0.0, holder_top)))
        # The blind socket is the visible interface that RETAINS the set
        # (L244-L248), so the stem has to fill it: a shank that merely lands on
        # the socket mouth would float inside a 1.7 mm void and the part would
        # report a disconnected island.
        socket_d = float(r.p["socket_depth_m"])
        plug_r = min(float(r.p["socket_r_m"]), float(r.p["land_r_m"]) * 0.72) + e
        solid = solid.union(_z_cyl(0.0, 0.0, plug_r, holder_top - socket_d - e, holder_top))
        return solid.union(_upper_shank(r, holder_top))
    z0 = -r.lower_die_tip_offset_m
    h = float(r.p["lower_holder_h_m"])
    holder_base = z0 - tip_r * 1.2
    solid = _z_cyl(0.0, 0.0, tip_r, holder_base, z0)
    holder = _rotating_set_holder_shape(r, h)
    holder_bottom = holder_base + e - h
    solid = solid.union(holder.translate((0.0, 0.0, holder_bottom)))
    socket_d = float(r.p["socket_depth_m"])
    plug_r = min(float(r.p["socket_r_m"]), float(r.p["land_r_m"]) * 0.72) + e
    solid = solid.union(_z_cyl(0.0, 0.0, plug_r, holder_bottom, holder_bottom + socket_d + e))
    stem, tail_top = _lower_shank(r, holder_bottom)
    solid = solid.union(stem)
    solid = solid.union(_rotating_set_holder_shape(r, h).translate((0.0, 0.0, tail_top - h)))
    return solid


def _nosepiece_shape(r: ResolvedConfig, *, upper: bool) -> cq.Workplane:
    """rec ..._var_head_module_quick_change_yoke model.py:L52-L77.

    shank r 6.2 union collar r 9.0 union tip r 4.5 minus a r 1.8 through bore --
    one welded solid.  The collar is allow_overlap site 9: at source size it is
    1.8 mm LARGER than the 7.2 mm receiver bore it runs in, so `max_die_step_r_m`
    clamps it below the bore instead of nesting it inside the tube wall.
    """
    shank_r = min(float(r.p["set_shank_r_m"]), r.max_die_step_r_m)
    collar_r = r.set_collar_r_eff_m
    tip_r = min(float(r.p["set_tip_r_m"]), r.die_tip_r_m * 1.35)
    bore_r = min(float(r.p["set_bore_r_m"]), tip_r * 0.55)
    if upper:
        z0 = r.upper_die_tip_offset_m
        stack = r.upper_die_stack_h_m
        tip = _z_cyl(0.0, 0.0, tip_r, z0, z0 + stack * 0.55)
        collar = _z_cyl(0.0, 0.0, collar_r, z0 + stack * 0.50, z0 + stack)
        shank = _z_cyl(0.0, 0.0, shank_r, z0 + stack - r.intra_part_embed_m, z0 + stack + 0.004)
        solid = tip.union(collar).union(shank)
        solid = solid.cut(_z_cyl(0.0, 0.0, bore_r, z0 - 0.001, z0 + stack + 0.004))
        return solid.union(_upper_shank(r, z0 + stack))
    z0 = -r.lower_die_tip_offset_m
    stack = r.lower_die_stack_h_m
    tip = _z_cyl(0.0, 0.0, tip_r, z0 - stack * 0.55, z0)
    collar = _z_cyl(0.0, 0.0, collar_r, z0 - stack, z0 - stack * 0.50)
    solid = tip.union(collar)
    solid = solid.cut(_z_cyl(0.0, 0.0, bore_r, z0 - stack, z0 + 0.001))
    stem, tail_top = _lower_shank(r, z0 - stack)
    solid = solid.union(stem)
    solid = solid.union(_z_cyl(0.0, 0.0, collar_r, tail_top - 0.008, tail_top))
    return solid


def _head_module_quick_change_yoke_clip_build(r: ResolvedConfig, *, upper: bool) -> cq.Workplane:
    return _nosepiece_shape(r, upper=upper)


def _quick_change_yoke_shape(r: ResolvedConfig) -> cq.Workplane:
    """rec ..._var_head_module_quick_change_yoke model.py:L80-L107.

    A stamped horseshoe: `circle(7.2).circle(3.3)` annulus extruded +-1.5, minus
    a `rect(10,3.8)@(-5,0)` release slot that opens the ring toward -X, plus a
    `rect(6,5)@(8.7,0)` thumb tab pierced by `circle(1.2)@(9.4,0)`.  It is a
    VISUAL ON THE FRAME (source L254-L264 seats it tangent to the frame cheek and
    verifies it FRAME-TO-FRAME at L528-L537), so here it is welded into the
    upper beam underside by `intra_part_embed_m` -- MECHANICAL_PRIORS 1c now
    calls the source's exact tangency fragile, and a same-part weld costs
    nothing.  Its bore keeps a real running clearance over the set shank, which
    is the only cross-part relation it has.
    """
    t = float(r.p["clip_thickness_m"])
    inner = max(
        float(r.p["clip_id_r_m"]),
        r.upper_die_shaft_r_m + r.running_fit_min_m + 0.0004,
    )
    outer = max(float(r.p["clip_od_r_m"]), inner + 0.0022)
    ring = cq.Workplane("XY").circle(outer).circle(inner).extrude(t)
    slot = (
        cq.Workplane("XY")
        .center(-outer * 0.7, 0.0)
        .rect(outer * 1.4, float(r.p["clip_slot_w_m"]))
        .extrude(t * 2.0)
        .translate((0.0, 0.0, -t * 0.5))
    )
    tab = cq.Workplane("XY").center(outer * 1.2, 0.0).rect(outer * 0.85, outer * 0.70).extrude(t)
    hole = (
        cq.Workplane("XY")
        .center(outer * 1.30, 0.0)
        .circle(float(r.p["thumb_tab_hole_r_m"]))
        .extrude(t * 2.0)
        .translate((0.0, 0.0, -t * 0.5))
    )
    return ring.cut(slot).union(tab).cut(hole)


_HEAD_BUILDERS = {
    "stepped_cylinder_dies": _head_module_stepped_cylinder_dies_build,
    "plain_die_pair": _head_module_plain_die_pair_build,
    "rotating_set_holder": _head_module_rotating_set_holder_build,
    "quick_change_yoke_clip": _head_module_quick_change_yoke_clip_build,
}


def _y_cyl_span(x: float, z: float, radius: float, y0: float, y1: float) -> cq.Workplane:
    """Y-axis cylinder spanning an explicit [y0, y1]."""
    length = max(y1 - y0, 1e-6)
    return _y_cyl(x, z, radius, length).translate((0.0, 0.5 * (y0 + y1), 0.0))


def _profile_z_at(points: list[tuple[float, float]], x: float) -> float | None:
    """Mean z of a polyline edge where it crosses the vertical line at `x`."""
    hits: list[float] = []
    for (x0, z0), (x1, z1) in zip(points, points[1:], strict=False):
        if x0 == x1:
            continue
        lo, hi = (x0, x1) if x0 < x1 else (x1, x0)
        if lo <= x <= hi:
            hits.append(z0 + (z1 - z0) * (x - x0) / (x1 - x0))
    if not hits:
        return None
    return sum(hits) / len(hits)


def _in_band(solid: cq.Workplane, thickness: float, inner_y: float) -> cq.Workplane:
    """Place a piece authored symmetrically about y=0 into an outboard band.

    `_xz_plate` extrudes +-width/2, so a grip section (1.1 x the frame width)
    and a lever plate cannot simply share one translate: the wider piece would
    reach back across the stand-off into the frame's own band.  Each piece is
    instead seated so its INNER face lands on `inner_y` and it grows outward.
    """
    return solid.translate((0.0, inner_y - thickness * 0.5, 0.0))


def _rot_y(solid: cq.Workplane, phi: float) -> cq.Workplane:
    """Rotate about +Y so a feature authored along +X lands at polar angle phi."""
    return solid.rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), -math.degrees(phi))


# ===========================================================================
# Slot B -- squeeze_mechanism.  One welded solid per moving part.  THE PIN
# VISUAL LIVES ON THE MOVING MEMBER (001 L311-L316) and is welded into the
# member's own hub, so only the frame bore is a cross-part clearance.
# ===========================================================================
def _lever_arm_solid(r: ResolvedConfig, points: int, half_h_root: float) -> cq.Workplane:
    """Hand-lever plate: hub + tapered arm + moulded grip + welded pivot pin.

    Source 001 `_moving_handle_shape` L125-L155 is a 16-point plate with a
    r 6.8 mm through-bore around the joint pin; here the bore is implicit (the
    pin is the lever's own welded hardware) and the arm is re-derived so the
    grip lands at the angle that makes the CLOSED grip gap exact.
    """
    hub_r = max(r.lever_pivot_bore_r_m * 2.3, r.main_pivot_pin_r_m * 2.2)
    phi = r.grip_phi_rad
    arm = r.grip_lever_arm_m
    half_h = r.grip_section_w_m * 0.5
    # The forged lever terminates under the moulded distal grip instead of
    # duplicating its full volume.  A small overlap keeps the same-part
    # visuals connected while preserving a clean material boundary.
    plate_end_x = arm * 0.45
    top = _bowed_edge((0.0, half_h_root), (plate_end_x, half_h * 0.82), max(3, points // 2), 0.004)
    bot = _bowed_edge(
        (plate_end_x, -half_h * 0.82), (0.0, -half_h_root), max(3, points - points // 2), 0.004
    )
    plate = _in_band(
        _xz_plate(top + bot, r.lever_plate_width_m), r.lever_plate_width_m, r.lever_y_inner_m
    )
    solid = _rot_y(plate, phi)
    solid = solid.union(
        _in_band(
            _y_cyl(0.0, 0.0, hub_r, r.lever_plate_width_m),
            r.lever_plate_width_m,
            r.lever_y_inner_m,
        )
    )
    if _MECH_HAS_LINK[r.squeeze_mechanism] and r.squeeze_mechanism != "screw_press":
        # Clevis bore for the compound link's own welded pin, cut 0.4 mm larger
        # than the pin exactly as binding `pin_bore_fit` inverts 001's numbers.
        # Source 002 L481-L490 instead ran the pair at zero clearance and
        # declared `allow_overlap` (site 7).
        solid = solid.cut(
            _y_cyl_span(
                r.link_station_x_m,
                0.0,
                r.link_pin_r_m + 0.0004,
                r.lever_y_outer_m - 0.002,
                0.002,
            )
        )
    # Main pivot pin: welded into the lever hub (intra-part, free) and running
    # in the frame bore with the 1.0 mm clearance 001 builds.
    solid = solid.union(
        _y_cyl_span(
            0.0,
            0.0,
            r.main_pivot_pin_r_m,
            r.lever_y_outer_m + r.intra_part_embed_m,
            r.frame_half_w_m * 0.55,
        )
    )
    return solid


def _squeeze_mechanism_hidden_internal_toggle_build(r: ResolvedConfig) -> cq.Workplane:
    """rec ...001... model.py:L349-L391 -- one PRISMATIC joint, NO link part.

    The mechanism is deliberately not exposed: `frame_to_ram` carries
    `meta["mechanism_note"] = "Actuated by the internal compound toggle hidden
    by the frame."` (L389).  The whole squeeze layer is one joint and zero extra
    parts, which is the low-part-count baseline of the slot.
    """
    return _lever_arm_solid(r, int(r.p["lever_profile_points"]), r.grip_section_w_m * 0.55)


def _squeeze_mechanism_dogbone_mimic_link_build(r: ResolvedConfig) -> cq.Workplane:
    """rec ...002... model.py:L262-L295 -- forked red lever carrying the link pin."""
    return _lever_arm_solid(r, 16, r.grip_section_w_m * 0.62)


def _squeeze_mechanism_long_toggle_cheek_build(r: ResolvedConfig) -> cq.Workplane:
    return _lever_arm_solid(r, 16, r.grip_section_w_m * 0.62)


def _squeeze_mechanism_eccentric_cam_build(r: ResolvedConfig) -> cq.Workplane:
    """rec ..._var_squeeze_mechanism_eccentric_cam_lever model.py:L330-L339.

    `_y_cylinder(0.009, 0.003, 0.018, 0.007)` minus a r 0.0056 bore on the pivot
    axis, on the outer cheek at y=-0.0245: the lobe centre sits ahead of the
    pivot centre by the eccentricity, and the record's own test (L655-L671)
    asserts that offset is at least 7 mm rather than assuming it.  The lobe is
    welded into the lever solid, so it costs no extra collision body.
    """
    solid = _lever_arm_solid(r, 16, r.grip_section_w_m * 0.62)
    ecc = float(r.p["cam_eccentricity_m"])
    lobe_r = float(r.p["cam_lobe_r_m"])
    lobe = _y_cyl(ecc * 0.95, ecc * 0.31, lobe_r, float(r.p["cam_thickness_m"]))
    lobe = lobe.cut(
        _y_cyl(0.0, 0.0, float(r.p["cam_bore_r_m"]), float(r.p["cam_thickness_m"]) * 3.0)
    )
    lobe = _in_band(lobe, float(r.p["cam_thickness_m"]), r.lever_y_inner_m)
    return solid.union(lobe)


def _squeeze_mechanism_screw_press_build(r: ResolvedConfig) -> cq.Workplane:
    """rec ..._var_squeeze_mechanism_screw_press model.py:L262-L280.

    `circle(0.014).extrude(0.018)` drive hub, a r 0.010 x 0.003 seating register
    below it, a transverse r 0.0042 tommy bore cut through, and a r 0.0075 x
    0.004 keying boss on top.  The joint moves to the die station with axis
    (0,0,-1) and 0..180 deg -- the only joint in the pool that is not about +-Y,
    which is why this candidate carries its own anchor.  Built in the joint's
    own local frame, so the local origin is the drive axis.
    """
    hub_r = float(r.p["drive_hub_r_m"])
    hub_h = float(r.p["drive_hub_h_m"])
    reg_r = float(r.p["register_r_m"])
    reg_h = float(r.p["register_h_m"])
    # The hub body stands 0.8 mm clear of the jaw seat and only the register
    # enters the pocket: a hub bottom flush with the forging's top face would be
    # a COINCIDENT face pair, and `fcl.collide` reports coplanar contact as a
    # collision.  That is the same reason the source's declared
    # `max_penetration=0.0035` seat (L497-L516) had to become a machined pocket.
    seat_gap = 0.0008
    solid = _z_cyl(0.0, 0.0, hub_r, seat_gap, hub_h)
    solid = solid.union(_z_cyl(0.0, 0.0, reg_r, -reg_h, seat_gap + r.intra_part_embed_m))
    solid = solid.union(_z_cyl(0.0, 0.0, hub_r * 0.54, hub_h - r.intra_part_embed_m, hub_h + 0.004))
    # Transverse tommy bore, really cut; the bar runs in it at bore - 0.6 mm.
    solid = solid.cut(_y_cyl(0.0, hub_h * 0.62, float(r.p["tommy_bore_r_m"]), hub_r * 4.0))
    return solid


def _squeeze_mechanism_direct_jaw_lever_build(r: ResolvedConfig) -> cq.Workplane:
    """rec ..._var_yoke_frame_alligator_jaw model.py:L261-L316 + L318-L337.

    The swinging member IS the lower jaw: a 23-point plate 12 mm thick in
    `dark_steel` (not rubber, L314 -- it is structure now) with a
    `circle(5.0).extrude(17.0)` lower rivet set unioned in at x = -172 mm
    (L299-L306), and lever travel collapsed 24 deg -> 2 deg (L331) because a
    24 deg arc would drive the jaws through each other.

    DELIBERATE DEPARTURE: the source runs this member INSIDE the frame's cut
    relief slot at y ~ 0 (L129-L135).  Here the jaw plate sits in the outboard
    -Y band like every other moving member and reaches the squeeze axis through
    a lateral spur, because the relief slot would have to be re-cut through five
    different frame silhouettes -- including two whose lower beam carries an
    anvil bore for the other five mechanisms -- and TemplateDomain has no
    compatibility gates.  The visible result is unchanged: a long swinging lower
    jaw whose rivet set is coaxial with the upper die.
    """
    n = int(r.p["jaw_profile_points"])
    reach = float(r.p["jaw_reach_m"])
    t = float(r.p["jaw_thickness_m"])
    hub_r = max(r.lever_pivot_bore_r_m * 2.3, r.main_pivot_pin_r_m * 2.2)
    jaw_z = r.lower_die_tip_offset_m * -1.0
    boss_r = float(r.p["lower_set_boss_r_m"])
    boss_h = min(
        float(r.p["lower_set_boss_h_m"]),
        max(
            0.004,
            r.lower_die_stack_h_m
            + (r.upper_jaw_underside_z_m - r.upper_die_tip_offset_m - r.upper_die_stack_h_m)
            - 0.002,
        ),
    )
    # Long lower jaw running out past the die station, plus the handle arm.
    jaw_top = _bowed_edge((-reach, jaw_z), (0.0, hub_r * 0.55), max(3, n // 2), 0.004)
    jaw_bot = _bowed_edge(
        (0.0, -hub_r * 0.9), (-reach, jaw_z - t * 1.6), max(3, n - n // 2), -0.004
    )
    jaw = _in_band(_xz_plate(jaw_top + jaw_bot, t), t, r.lever_y_inner_m)
    half_h = r.grip_section_w_m * 0.5
    arm = r.grip_lever_arm_m
    handle = _rot_y(
        _in_band(
            _xz_plate(
                _bowed_edge((0.0, half_h * 0.62), (arm * 0.98, half_h * 0.9), 6, 0.003)
                + _bowed_edge((arm * 0.98, -half_h * 0.9), (0.0, -half_h * 0.62), 6, 0.003),
                t,
            ),
            t,
            r.lever_y_inner_m,
        ).union(
            _in_band(
                _xz_plate(
                    _grip_profile(r, arm * 0.42, arm * 0.58, 0.0, half_h), r.grip_section_w_m
                ),
                r.grip_section_w_m,
                r.lever_y_inner_m,
            )
        ),
        r.grip_phi_rad,
    )
    solid = jaw.union(handle).union(_in_band(_y_cyl(0.0, 0.0, hub_r, t), t, r.lever_y_inner_m))
    # Lateral spur carrying the welded lower rivet set onto the squeeze axis.
    # Column tying the set boss back into the jaw plate.  Its top is solved from
    # the plate's OWN outline at the die station rather than assumed, because
    # the outline is a bowed polygon whose local depth changes with
    # `jaw_reach_m`, `jaw_thickness_m` and the open gap; a fixed top reaches the
    # plate at the authored proportions and misses it at the range edges.  The
    # column lives in the jaw's outboard band, so it may rise past the working
    # face without ever approaching the upper die on the axis.
    z_top = _profile_z_at(jaw_top, r.die_axis_x_m)
    z_bot = _profile_z_at(jaw_bot, r.die_axis_x_m)
    if z_top is None or z_bot is None:
        anchor_z = jaw_z
    else:
        anchor_z = 0.5 * (z_top + z_bot)
    column = _xz_plate(
        [
            (r.die_axis_x_m - boss_r * 0.9, jaw_z - boss_h),
            (r.die_axis_x_m + boss_r * 0.9, jaw_z - boss_h),
            (r.die_axis_x_m + boss_r * 0.9, max(anchor_z, jaw_z - boss_h * 0.30)),
            (r.die_axis_x_m - boss_r * 0.9, max(anchor_z, jaw_z - boss_h * 0.30)),
        ],
        t,
    )
    column = _in_band(column, t, r.lever_y_inner_m)
    spur = _z_cyl(r.die_axis_x_m, 0.0, boss_r * 1.05, jaw_z - boss_h, jaw_z - boss_h * 0.45)
    # Lateral spur bridging the outboard jaw plate onto the squeeze axis.  It
    # runs entirely in the OPEN THROAT, above the frame's lower beam and below
    # the upper die's working face, so it meets no frame material at any pose.
    bridge_y0 = r.lever_y_inner_m - t
    bridge_y1 = boss_r * 0.6
    bridge = _xz_plate(
        [
            (r.die_axis_x_m - boss_r, jaw_z - boss_h),
            (r.die_axis_x_m + boss_r, jaw_z - boss_h),
            (r.die_axis_x_m + boss_r, jaw_z - boss_h * 0.45),
            (r.die_axis_x_m - boss_r, jaw_z - boss_h * 0.45),
        ],
        bridge_y1 - bridge_y0,
    ).translate((0.0, 0.5 * (bridge_y0 + bridge_y1), 0.0))
    set_boss = _z_cyl(r.die_axis_x_m, 0.0, boss_r, jaw_z - boss_h, jaw_z)
    return solid.union(column).union(bridge).union(spur).union(set_boss)


_MECH_BUILDERS = {
    "hidden_internal_toggle": _squeeze_mechanism_hidden_internal_toggle_build,
    "dogbone_mimic_link": _squeeze_mechanism_dogbone_mimic_link_build,
    "long_toggle_cheek": _squeeze_mechanism_long_toggle_cheek_build,
    "eccentric_cam": _squeeze_mechanism_eccentric_cam_build,
    "screw_press": _squeeze_mechanism_screw_press_build,
    "direct_jaw_lever": _squeeze_mechanism_direct_jaw_lever_build,
}


def _linkage_shape(r: ResolvedConfig) -> cq.Workplane:
    """The compound link, built in its own joint frame.

    `dogbone_mimic_link` (002 L125-L140): a 5-point dog-bone plate 0.004 m thick
    with two r 0.0032 eyes.  `long_toggle_cheek` (L125-L158): a computed-normal
    rectangular web from (0,0) to the ram station with r 0.008 end bosses --
    the first link in the pool that actually terminates on the ram, and the
    construction is index-general in the pin-to-pin vector, so only the
    endpoints move when the die station or throat height changes.
    In BOTH cases the eye pins are welded into the LINK (intra-part, free)
    instead of into their hosts, which is what removes allow_overlap sites 7/8.
    """
    t = float(r.p["link_thickness_m"])
    end_x = r.die_axis_x_m - r.link_station_x_m
    end_z = r.upper_jaw_underside_z_m
    length = math.hypot(end_x, end_z) or 1.0
    if r.squeeze_mechanism == "long_toggle_cheek":
        half = float(r.p["toggle_half_width_m"])
        boss = float(r.p["toggle_boss_r_m"])
    else:
        half = max(0.004, float(r.p["link_eye_r_m"]) * 1.6)
        boss = float(r.p["link_eye_r_m"]) * 2.2
    nx = -end_z / length * half
    nz = end_x / length * half
    web = _xz_plate([(nx, nz), (end_x + nx, end_z + nz), (end_x - nx, end_z - nz), (-nx, -nz)], t)
    if r.squeeze_mechanism == "dogbone_mimic_link":
        n = int(r.p["link_profile_points"])
        # 002's dog-bone silhouette: a lens-shaped waist between the two eyes.
        fwd = _bowed_edge((0.0, 0.0), (end_x, end_z), max(3, n), half * 1.5)
        back = _bowed_edge((end_x, end_z), (0.0, 0.0), max(3, n), half * 1.5)
        web = web.union(_xz_plate(fwd[:-1] + back[:-1], t * 0.85))
    solid = web.union(_y_cyl(0.0, 0.0, boss, t)).union(_y_cyl(end_x, end_z, boss, t))
    # Welded eye pins -- the pin belongs to the moving member (binding
    # `pin_bore_fit`), sized `eye_r - 0.6 mm` off the link's own eyes.  Built in
    # the LINK's own joint frame, so the pins reach inboard toward the lever.
    # The LEVER-end pin runs into the clevis bore cut for it; the RAM-end pin is
    # a stub that stops short of the lever plate, because the toggle terminates
    # on the ram's own cross pin (long_toggle L373-L384) and never on the lever.
    clevis_reach = max(
        (r.lever_y_outer_m - r.link_y_centre_m) + r.lever_plate_width_m * 0.6,
        t * 0.5 + 0.003,
    )
    stub_reach = min(
        t * 0.5 + 0.004,
        (r.lever_y_outer_m - r.link_y_centre_m) - r.running_fit_min_m,
    )
    stub_reach = max(stub_reach, t * 0.5 + 0.0005)
    solid = solid.union(
        _y_cyl_span(0.0, 0.0, r.link_pin_r_m, t * 0.5 - r.intra_part_embed_m, clevis_reach)
    )
    solid = solid.union(
        _y_cyl_span(end_x, end_z, r.link_pin_r_m, t * 0.5 - r.intra_part_embed_m, stub_reach)
    )
    return solid


def _tommy_bar_shape(r: ResolvedConfig) -> cq.Workplane:
    """rec ..._var_squeeze_mechanism_screw_press model.py:L304-L338.

    A real sliding tommy bar: `Cylinder(r 0.0034, len 0.170)` with a r 0.0042
    bushing and two r 0.0070 end knobs, on a PRISMATIC joint along (0,1,0) with
    +-0.025 m of travel.  The source builds the bushing at exactly the hub's
    bore radius (0.0042 = 0.0042) and declares `allow_overlap`; here the bushing
    is `bore - 0.6 mm`, which is 001's running-fit rule.
    """
    half = float(r.p["tommy_bar_len_m"]) * 0.5
    bar_r = max(r.tommy_bushing_r_m * 0.78, 0.0018)
    solid = _y_cyl(0.0, 0.0, bar_r, half * 2.0)
    solid = solid.union(_y_cyl(0.0, 0.0, r.tommy_bushing_r_m, 0.020))
    for sign in (-1.0, 1.0):
        solid = solid.union(
            _y_cyl_span(
                0.0,
                0.0,
                r.tommy_bushing_r_m * 1.65,
                sign * half - (0.014 if sign > 0 else 0.0),
                sign * half + (0.0 if sign > 0 else 0.014),
            )
        )
    return solid


# ===========================================================================
# Slot D -- return_element.  All three real springs are VISUALS ON THE FRAME,
# exactly as the pool builds them, so their embed into the frame cheek is
# intra-part and free (MECHANICAL_PRIORS 1c).  They are welded into the frame
# body by at least `intra_part_embed_m` because the connectivity check is
# intra-part at 1e-6 and a floating spring would read as a disconnected island.
# `no_return_element` is source-attested: 002 and 003 carry no spring at all.
# ===========================================================================
def _return_element_wire_extension_spring_build(r: ResolvedConfig):
    """rec ...001... model.py:L262-L281.

    `tube_from_spline_points` over 7 zig-zag points (x alternating
    -0.039/-0.046, z 0.292 -> 0.232), radius 0.0012, 6 samples/segment, 12
    radial segments, capped.  Emitted on the FRAME at y ~ -0.0115, straddling
    the frame's -0.010 cheek face.
    """
    n = int(r.p["zigzag_points"])
    wire_r = float(r.p["wire_r_m"])
    amp = float(r.p["zigzag_amplitude_m"])
    span = min(float(r.p["spring_len_m"]), (r.upper_beam_top_z_m - r.lower_beam_bottom_z_m) * 0.7)
    x0 = -r.die_station_x_m * 0.22
    z0 = r.upper_beam_top_z_m * 0.55
    y = _frame_extra_centre_y(r, wire_r * 2.0)
    hub_r = _hub_radius(r)
    # The clamped end is anchored INSIDE the pivot hub, the one region of the
    # forging that is solid for every candidate; the cheek embed alone is not
    # enough, because at some parameter combinations the bowed silhouette has
    # no material under the authored mount station and the spring -- a single
    # visual on the frame -- would read as a disconnected island at 1e-6.
    pts = [(hub_r * 0.32, y, hub_r * 0.32)]
    pts += [(x0 + (amp if i % 2 else 0.0), y, z0 - span * i / max(1, n - 1)) for i in range(n)]
    return tube_from_spline_points(
        pts, radius=wire_r, samples_per_segment=6, radial_segments=12, cap_ends=True
    )


def _return_element_leaf_return_spring_build(r: ResolvedConfig):
    """rec ..._var_return_leaf_return_spring model.py:L220-L245 + L291-L302.

    A 17-point CLOSED side profile extruded to just 1.6 mm by the parent's own
    `_plate_from_profile`, i.e. a genuine pre-bowed leaf with a broad clamped
    upper tang and a narrow bowed lower end; its author test bounds the Y extent
    at <= 0.002 m, which is what keeps it a leaf rather than a bar.
    """
    n = int(r.p["leaf_profile_points"])
    t = float(r.p["leaf_thickness_m"])
    bow = float(r.p["leaf_bow_m"])
    length = min(float(r.p["leaf_len_m"]), (r.upper_beam_top_z_m - r.lower_beam_bottom_z_m) * 0.75)
    hub_r = _hub_radius(r)
    # Broad clamped upper tang anchored inside the pivot hub -- same reason as
    # the wire spring: the leaf is one visual on the frame and has to overlap
    # the forging at EVERY parameter combination, not just the authored one.
    x0 = hub_r * 0.30
    z0 = hub_r * 0.30
    half = max(3, n // 2)
    outer = _bowed_edge((x0, z0), (x0, z0 - length), half, bow)
    inner = _bowed_edge((x0, z0 - length), (x0, z0), n - half, -(bow - t))
    plate = _xz_plate(outer[:-1] + inner[:-1], t)
    return plate.translate((0.0, _frame_extra_centre_y(r, t), 0.0))


def _torsion_handle_spring_geometry(r: ResolvedConfig):
    """rec ..._var_return_torsion_handle_spring model.py:L220-L261.

    A real helix generated in code: coil_radius 0.0115 about the pivot,
    start_angle 225 deg, 2.25 turns, 34 samples, with the axial coordinate
    walking so the coil advances instead of stacking on itself, plus three
    formed reaction-leg points before and after.  This is the pool's only spring
    with a genuine CROSS-part clearance problem (1.7 mm to the moving handle
    plate), so its stand-off is re-derived from the lever width rather than
    inherited as a constant -- and here it additionally sits on the opposite
    cheek from every moving member, so the clearance can never be eaten.

    Under `screw_press` there is no handle pivot, so the coil moves onto the
    drive head's own revolute -- the squeeze axis at the die station (L287-L288)
    -- which is binding `return_and_latch_adaptation`'s stated adaptation.  Its
    radius is then held clear of the largest turning in the throat.
    """
    wire_r = float(r.p["wire_r_m"])
    turns = float(r.p["coil_turns"])
    samples = int(r.p["coil_samples"])
    legs = int(r.p["reaction_leg_points"])
    start = math.radians(225.0)
    pts: list[tuple[float, float, float]] = []
    if r.squeeze_mechanism == "screw_press":
        # Around the drive head, above the jaw top and below the tommy bore, so
        # the coil wraps the tool's only revolute without ever entering the
        # throat where the two dies run.
        # Wrapped on the drive-head axis but BELOW the jaw seat: the drive hub
        # occupies everything above it and the tommy bar sweeps a 0.11-0.24 m
        # disc through that band, so the only clear annulus on this axis is the
        # one just under the seat.  Its radius clears both the guide bore the
        # dies run in and the forging's own half-width, so the coil reads
        # outboard of the beam in Y.
        # The rotating drive register occupies the axis right here, so both the
        # coil AND its anchoring leg have to stay radially outside it with a
        # real running clearance -- the register turns, the spring does not.
        clear_r = float(r.p["register_r_m"]) + r.running_fit_min_m + 0.0004
        coil_r = max(
            float(r.p["coil_r_m"]),
            r.frame_half_w_m + 0.004,
            r.ram_guide_bore_r_m + 0.005,
            clear_r + 0.0005,
        )
        advance = min(float(r.p["axial_advance_m"]), r.upper_beam_h_eff_m * 0.5)
        advance = max(advance, 0.0015)
        # The jaw TOP, not the drive seat: under `alligator_jaw` the seat is the
        # top of the welded receiver (L195/L200) and a coil hung under it would
        # float in the air beside the tube.  The forged beam is what the legs
        # can actually reach.
        z1 = r.upper_beam_top_z_m - 0.002
        cx, cy = r.die_axis_x_m, 0.0
        end_a = start + turns * 2.0 * math.pi
        for i in range(legs):
            f = i / max(1, legs - 1)
            # The first leg point sits INSIDE the beam plate (within half the
            # forging width of the axis), so the coil is welded to the frame at
            # every parameter combination rather than only where the ring
            # happens to cross material.
            inner = max(clear_r, min(coil_r, r.frame_half_w_m * 0.45))
            rad = inner + (coil_r - inner) * f
            pts.append((cx + rad * math.cos(start), cy + rad * math.sin(start), z1 - advance))
        for i in range(samples):
            f = i / max(1, samples - 1)
            a = start + f * turns * 2.0 * math.pi
            pts.append(
                (cx + coil_r * math.cos(a), cy + coil_r * math.sin(a), z1 - advance * (1.0 - f))
            )
        for i in range(legs):
            f = (i + 1) / legs
            rad = coil_r * (1.0 + 0.40 * f)
            pts.append((cx + rad * math.cos(end_a), cy + rad * math.sin(end_a), z1))
        return tube_from_spline_points(
            pts, radius=wire_r, samples_per_segment=4, radial_segments=12, cap_ends=True
        )
    coil_r = float(r.p["coil_r_m"])
    advance = float(r.p["axial_advance_m"])
    y0 = r.frame_half_w_m - r.intra_part_embed_m
    end_a = start + turns * 2.0 * math.pi
    hub_r = _hub_radius(r)
    for i in range(legs):
        f = i / max(1, legs - 1)
        # Formed reaction leg running from INSIDE the pivot hub out to the coil
        # start, so the helix is welded to the forging whatever `coil_r_m` is.
        rad = hub_r * 0.35 + (coil_r - hub_r * 0.35) * f
        pts.append(
            (
                rad * math.cos(start),
                y0 - r.intra_part_embed_m * 2.0 * (1.0 - f),
                rad * math.sin(start),
            )
        )
    for i in range(samples):
        f = i / max(1, samples - 1)
        a = start + f * turns * 2.0 * math.pi
        pts.append((coil_r * math.cos(a), y0 + advance * f, coil_r * math.sin(a)))
    for i in range(legs):
        f = (i + 1) / legs
        rad = coil_r * (1.0 + 0.50 * f)
        pts.append((rad * math.cos(end_a), y0 + advance, rad * math.sin(end_a)))
    return tube_from_spline_points(
        pts, radius=wire_r, samples_per_segment=4, radial_segments=12, cap_ends=True
    )


# ===========================================================================
# Slot E -- handle_lock.  Both real latches use 003's construction, the pool's
# ONLY allowance-free rotary capture: a real annular eye centred ON the joint
# origin whose bore clears the axle by 0.2 mm (003 L355-L356 / L393, verified
# with `expect_within` at L546-L554 and NO `allow_overlap`).  001's own latch
# is speared by a pin 3 mm off the hinge axis and hooked around the fixed grip
# with 1.4 mm of interference -- allow_overlap sites 1 and 2, both removed here.
# The latch is carried by its hinge alone, so it is declared with
# `ctx.allow_isolated_part`, which preflight permits.
# ===========================================================================
def _latch_eye_radii(r: ResolvedConfig) -> tuple[float, float, float]:
    """Eye bore, eye OD and the radius the wire springs from.

    The wire has to leave the annulus OUTSIDE the axle that fills the bore, or
    the two cross: 003 seeds its loop at x=0.0042 against a 2.2 mm bore and a
    4.5 mm OD (L371/L355-L356).  The OD is therefore opened up whenever the
    authored wire is thick enough to close that band.
    """
    bore = r.latch_eye_bore_r_m
    wire_r = float(r.p["wire_r_m"])
    od = max(float(r.p["eye_od_r_m"]), bore * 1.9, bore + 2.0 * wire_r + 0.0010)
    seed = max((bore + od) * 0.5, bore + wire_r + 0.0005)
    return bore, od, seed


def _latch_eye(r: ResolvedConfig) -> cq.Workplane:
    bore, od, _ = _latch_eye_radii(r)
    t = float(r.p["eye_thickness_m"])
    return _y_cyl(0.0, 0.0, od, t).cut(_y_cyl(0.0, 0.0, bore, t * 3.0))


def _handle_lock_wire_hook_latch_build(r: ResolvedConfig):
    """rec ...001... model.py:L434-L452 -- a 5-point open spline hook.

    Tubed at r 0.0012 with 10 samples/segment and 14 radial segments, parented
    to the MOVING handle.  The rebuild keeps the open hook and gives it the
    formed eye the source never modelled, so the capture is geometric.
    """
    n = int(r.p["hook_points"])
    wire_r = float(r.p["wire_r_m"])
    reach = float(r.p["hook_reach_m"])
    _, _, seed_r = _latch_eye_radii(r)
    pts = [(seed_r, 0.0, 0.0)]
    for i in range(1, n):
        f = i / (n - 1)
        pts.append(
            (
                seed_r + reach * f,
                0.0,
                -reach * 0.16 * math.sin(math.pi * f) - reach * 0.20 * f * f,
            )
        )
    return tube_from_spline_points(
        pts, radius=wire_r, samples_per_segment=10, radial_segments=14, cap_ends=True
    )


def _handle_lock_eye_and_wire_loop_latch_build(r: ResolvedConfig):
    """rec ...003... model.py:L370-L390 -- a CLOSED 8-point wire loop.

    Tubed at r 0.0011 with 12 samples/segment and 14 radial segments, springing
    from the annular eye rather than from an open hook, which is the joint-count
    / capture-topology difference this candidate carries.
    """
    n = int(r.p["loop_points"])
    wire_r = float(r.p["wire_r_m"])
    _, od, seed_r = _latch_eye_radii(r)
    reach = od * 5.5
    pts: list[tuple[float, float, float]] = []
    for i in range(n):
        a = 2.0 * math.pi * i / n
        pts.append(
            (
                seed_r + reach * 0.5 * (1.0 - math.cos(a)),
                0.0,
                reach * 0.30 * math.sin(a),
            )
        )
    return tube_from_spline_points(
        pts,
        radius=wire_r,
        samples_per_segment=12,
        radial_segments=14,
        closed_spline=True,
        cap_ends=True,
    )


_LATCH_BUILDERS = {
    "wire_hook_latch": _handle_lock_wire_hook_latch_build,
    "eye_and_wire_loop_latch": _handle_lock_eye_and_wire_loop_latch_build,
}
_RETURN_BUILDERS = {
    "wire_extension_spring": _return_element_wire_extension_spring_build,
    "leaf_return_spring": _return_element_leaf_return_spring_build,
    "torsion_handle_spring": _torsion_handle_spring_geometry,
}


# ===========================================================================
# Assembly
# ===========================================================================
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    for key, rgba in r.palette.items():
        model.material(f"rivet_squeeze_{key}", rgba=rgba)
    return {key: f"rivet_squeeze_{key}" for key in r.palette}


def _cq_visual(part, solid: cq.Workplane, r: ResolvedConfig, material: str, name: str) -> None:
    part.visual(
        mesh_from_cadquery(solid, name, tolerance=r.mesh_chord_tol_m, angular_tolerance=_ANG_TOL),
        material=material,
        name=name, material_class_id=("metal.paint_coated" if r.palette_style in {"red_forged", "teal_cast"} else "metal.blackened_gunmetal"),
    )


def _axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    joint_type: ArticulationType,
    parent,
    child,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    limits: MotionLimits,
    radius: float,
    mimic: Mimic | None = None,
    meta: dict | None = None,
):
    """Every joint in this template is solved by `mate_axes` on the true design
    axis and registered with `register_interface_mate` (AUTHORING 4)."""
    radial = (1.0, 0.0, 0.0) if abs(axis[0]) < 0.9 else (0.0, 0.0, 1.0)
    provider = AxisInterface(
        name=f"{name}__provider", point=point, axis=axis, radial=radial, radius=radius
    )
    consumer = AxisInterface(name=f"{name}__consumer", axis=axis, radial=radial, radius=radius)
    mate = mate_axes(provider, consumer)
    joint = model.articulation(
        name,
        joint_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        mimic=mimic,
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)
    return joint


def _build_frame(model: ArticulatedObject, r: ResolvedConfig, mats) -> object:
    frame = model.part("frame", meta={"role": "frame", "candidate": r.yoke_frame})
    solid = _FRAME_BUILDERS[r.yoke_frame](r)
    _cq_visual(frame, solid, r, mats["forging"], f"yoke_frame__{r.yoke_frame}__forged_body")
    _cq_visual(
        frame,
        _fixed_grip_skin(r),
        r,
        mats["grip"],
        f"yoke_frame__{r.yoke_frame}__fixed_grip_skin",
    )
    pivot_cap, fasteners = _frame_side_details(r)
    _cq_visual(
        frame,
        pivot_cap,
        r,
        mats["dark"],
        f"yoke_frame__{r.yoke_frame}__pivot_cap",
    )
    _cq_visual(
        frame,
        fasteners,
        r,
        mats["polished"],
        f"yoke_frame__{r.yoke_frame}__handle_fasteners",
    )
    if r.head_module == "quick_change_yoke_clip":
        clip = _quick_change_yoke_shape(r).translate(
            (
                r.die_axis_x_m,
                0.0,
                r.upper_jaw_underside_z_m - float(r.p["clip_thickness_m"]) + r.intra_part_embed_m,
            )
        )
        _cq_visual(
            frame,
            clip,
            r,
            mats["zinc"],
            f"head_module__{r.head_module}__quick_change_clip",
        )
    if r.return_element != "no_return_element":
        geom = _RETURN_BUILDERS[r.return_element](r)
        name = f"return_element__{r.return_element}__spring"
        if isinstance(geom, cq.Workplane):
            _cq_visual(frame, geom, r, mats["polished"], name)
        else:
            frame.visual(mesh_from_geometry(geom, name), material=mats["polished"], name=name, material_class_id="metal.steel_bare")
    if r.handle_lock != "no_handle_lock" and r.latch_parent_role == "frame":
        _add_latch_axle(frame, r, mats, host_face_y=r.frame_half_w_m)
    return frame


def _add_latch_axle(part, r: ResolvedConfig, mats, *, host_face_y: float) -> None:
    """The frame- or lever-borne axle the latch eye turns on.

    003 L392-L397 builds it as `Cylinder(r 0.0020, len 0.008)` sitting exactly
    on the joint origin, so the r 0.0022 eye keeps a 0.2 mm radial clearance --
    the pool's only allowance-free rotary capture (verified there by
    `expect_within` at L546-L554, with no allowance).  The axle's SPAN is
    derived rather than authored: it starts `intra_part_embed_m` inside its
    host's own outer face, so the weld cannot open anywhere in the declared
    ranges, and ends just past the eye it retains.
    """
    ox, oy, oz = r.latch_origin_xyz
    outward = 1.0 if oy > 0.0 else -1.0
    y_root = outward * (host_face_y - r.intra_part_embed_m)
    y_tip = oy + outward * (float(r.p["eye_thickness_m"]) * 0.5 + 0.0006)
    part.visual(
        Cylinder(radius=r.latch_axle_r_m, length=abs(y_tip - y_root)),
        origin=Origin(xyz=(ox, 0.5 * (y_root + y_tip), oz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["polished"],
        name=f"handle_lock__{r.handle_lock}__latch_axle", material_class_id="metal.steel_bare",
    )


def _build_dies(model: ArticulatedObject, r: ResolvedConfig, mats, frame):
    upper = model.part(
        f"head_module__{r.head_module}__upper_die",
        meta={"role": "upper_die", "candidate": r.head_module},
    )
    _cq_visual(
        upper,
        _HEAD_BUILDERS[r.head_module](r, upper=True),
        r,
        mats["polished"],
        f"head_module__{r.head_module}__upper_die_body",
    )
    drive_name = _drive_joint_name(r)
    _axis_joint(
        model,
        name=f"head_module__{r.head_module}__upper_die_drive",
        joint_type=ArticulationType.PRISMATIC,
        parent=frame,
        child=upper,
        point=(r.die_axis_x_m, r.die_axis_y_m, 0.0),
        axis=(0.0, 0.0, 1.0),
        limits=MotionLimits(
            effort=r.ram_effort_eff_n,
            velocity=0.025,
            lower=-r.upper_die_travel_m,
            upper=0.0,
        ),
        radius=r.upper_die_shaft_r_m,
        meta={
            "positive_motion": "retracts the upper rivet die away from the work",
            "mechanical_driver": drive_name,
            "coupling_note": "revolute-to-prismatic squeeze coupling",
        },
    )
    lower = None
    if r.lower_die_parent_role == "frame":
        lower = model.part(
            f"head_module__{r.head_module}__lower_die",
            meta={"role": "lower_die", "candidate": r.head_module},
        )
        _cq_visual(
            lower,
            _HEAD_BUILDERS[r.head_module](r, upper=False),
            r,
            mats["dark"],
            f"head_module__{r.head_module}__lower_die_body",
        )
        _axis_joint(
            model,
            name=f"head_module__{r.head_module}__lower_die_adjust",
            joint_type=ArticulationType.PRISMATIC,
            parent=frame,
            child=lower,
            point=(r.die_axis_x_m, r.die_axis_y_m, 0.0),
            axis=(0.0, 0.0, 1.0),
            limits=MotionLimits(
                effort=r.anvil_effort_eff_n,
                velocity=0.012,
                lower=-r.anvil_adjust_eff_m,
                upper=r.anvil_adjust_eff_m,
            ),
            radius=r.anvil_shaft_r_m,
            meta={"positive_motion": "raises the lower die to set rivet length"},
        )
    return upper, lower


def _drive_joint_name(r: ResolvedConfig) -> str:
    if r.squeeze_mechanism == "screw_press":
        return "squeeze_mechanism__screw_press__drive_head"
    if r.squeeze_mechanism == "direct_jaw_lever":
        return "squeeze_mechanism__direct_jaw_lever__jaw_pivot"
    return f"squeeze_mechanism__{r.squeeze_mechanism}__lever_pivot"


def _build_mechanism(model: ArticulatedObject, r: ResolvedConfig, mats, frame):
    mech = r.squeeze_mechanism
    solid = _MECH_BUILDERS[mech](r)
    if mech == "direct_jaw_lever":
        member = model.part(
            "squeeze_mechanism__direct_jaw_lever__moving_jaw",
            meta={"role": "moving_jaw", "candidate": mech},
        )
        _cq_visual(
            member,
            solid,
            r,
            mats["dark"],
            "squeeze_mechanism__direct_jaw_lever__moving_jaw_body",
        )
        drive = _axis_joint(
            model,
            name=_drive_joint_name(r),
            joint_type=ArticulationType.REVOLUTE,
            parent=frame,
            child=member,
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 1.0, 0.0),
            limits=MotionLimits(
                effort=r.drive_effort_eff_n,
                velocity=2.0,
                lower=0.0,
                upper=r.lever_travel_eff_rad,
            ),
            radius=r.main_pivot_pin_r_m,
            meta={"positive_motion": "swings the alligator jaw up onto the upper set"},
        )
        return member, drive, None
    member = model.part(
        f"squeeze_mechanism__{mech}__squeeze_lever",
        meta={"role": "squeeze_lever", "candidate": mech},
    )
    _cq_visual(
        member,
        solid,
        r,
        mats["forging" if mech != "screw_press" else "grip"],
        f"squeeze_mechanism__{mech}__lever_body",
    )
    if mech != "screw_press":
        _cq_visual(
            member,
            _moving_grip_skin(r),
            r,
            mats["grip"],
            f"squeeze_mechanism__{mech}__moving_grip_skin",
        )
    if mech == "screw_press":
        drive = _axis_joint(
            model,
            name=_drive_joint_name(r),
            joint_type=ArticulationType.REVOLUTE,
            parent=frame,
            child=member,
            point=(r.die_axis_x_m, 0.0, r.upper_seat_z_m),
            axis=(0.0, 0.0, 1.0),
            limits=MotionLimits(
                effort=r.drive_effort_eff_n,
                velocity=2.0,
                lower=0.0,
                upper=r.screw_turn_range_eff_rad,
            ),
            radius=float(r.p["register_r_m"]),
            meta={
                "positive_motion": "turns the screw-press head down onto the work",
                "mechanism": "threaded screw press",
                "lead_m_per_turn": float(r.p["lead_m_per_turn"]),
            },
        )
    else:
        drive = _axis_joint(
            model,
            name=_drive_joint_name(r),
            joint_type=ArticulationType.REVOLUTE,
            parent=frame,
            child=member,
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 1.0, 0.0),
            limits=MotionLimits(
                effort=r.drive_effort_eff_n,
                velocity=1.5,
                lower=0.0,
                upper=r.lever_travel_eff_rad,
            ),
            radius=r.main_pivot_pin_r_m,
            meta={"positive_motion": "closes the moving grip toward the fixed grip"},
        )
    link = None
    if _MECH_HAS_LINK[mech]:
        link = model.part(
            f"squeeze_mechanism__{mech}__compound_link",
            meta={"role": "compound_link", "candidate": mech},
        )
        if mech == "screw_press":
            _cq_visual(
                link,
                _tommy_bar_shape(r),
                r,
                mats["zinc"],
                f"squeeze_mechanism__{mech}__sliding_tommy_bar",
            )
            _axis_joint(
                model,
                name=f"squeeze_mechanism__{mech}__tommy_slide",
                joint_type=ArticulationType.PRISMATIC,
                parent=member,
                child=link,
                point=(0.0, 0.0, float(r.p["drive_hub_h_m"]) * 0.62),
                axis=(0.0, 1.0, 0.0),
                limits=MotionLimits(
                    effort=min(80.0, r.drive_effort_eff_n * 0.5),
                    velocity=0.15,
                    lower=-float(r.p["tommy_slide_range_m"]),
                    upper=float(r.p["tommy_slide_range_m"]),
                ),
                radius=r.tommy_bushing_r_m,
                meta={"positive_motion": "slides the tommy bar through the screw head"},
            )
        else:
            _cq_visual(
                link,
                _linkage_shape(r),
                r,
                mats["zinc"],
                f"squeeze_mechanism__{mech}__compound_link_plate",
            )
            span = abs(r.mimic_multiplier_eff) * r.lever_travel_eff_rad
            _axis_joint(
                model,
                name=f"squeeze_mechanism__{mech}__link_pivot",
                joint_type=ArticulationType.REVOLUTE,
                parent=member,
                child=link,
                point=(r.link_station_x_m, r.link_y_centre_m, 0.0),
                axis=(0.0, 1.0, 0.0),
                limits=MotionLimits(
                    effort=min(90.0, r.drive_effort_eff_n * 0.5),
                    velocity=2.0,
                    lower=min(0.0, math.copysign(span, r.mimic_multiplier_eff)),
                    upper=max(0.0, math.copysign(span, r.mimic_multiplier_eff)),
                ),
                mimic=Mimic(
                    joint=_drive_joint_name(r),
                    multiplier=r.mimic_multiplier_eff,
                    offset=r.mimic_offset_rad,
                ),
                radius=r.link_pin_r_m,
                meta={"positive_motion": "the compound link follows the hand lever"},
            )
    return member, drive, link


def _build_handle_lock(model: ArticulatedObject, r: ResolvedConfig, mats, frame, member):
    if r.handle_lock == "no_handle_lock":
        return None
    latch = model.part(
        f"handle_lock__{r.handle_lock}__latch",
        meta={"role": "handle_lock", "candidate": r.handle_lock},
    )
    ox, oy, oz = r.latch_origin_xyz
    _cq_visual(
        latch,
        _latch_eye(r),
        r,
        mats["polished"],
        f"handle_lock__{r.handle_lock}__latch_eye",
    )
    wire = _LATCH_BUILDERS[r.handle_lock](r)
    latch.visual(
        mesh_from_geometry(wire, f"handle_lock__{r.handle_lock}__latch_wire"),
        material=mats["polished"],
        name=f"handle_lock__{r.handle_lock}__latch_wire", material_class_id="metal.steel_bare",
    )
    parent = frame if r.latch_parent_role == "frame" else member
    if r.latch_parent_role != "frame":
        # The latch sits on the moulded distal grip, whose outboard face can be
        # wider than the forged lever plate.  Seat the axle from that real face
        # so it remains connected after the two materials are split.
        moving_grip_outer_y = abs(r.lever_y_inner_m - r.grip_section_w_m)
        _add_latch_axle(member, r, mats, host_face_y=moving_grip_outer_y)
    _axis_joint(
        model,
        name=f"handle_lock__{r.handle_lock}__latch_pivot",
        joint_type=ArticulationType.REVOLUTE,
        parent=parent,
        child=latch,
        point=(ox, oy, oz),
        axis=(0.0, 1.0, 0.0),
        limits=MotionLimits(
            effort=r.latch_effort_eff_n,
            velocity=2.5,
            lower=0.0,
            upper=float(r.p["latch_swing_rad"]),
        ),
        radius=r.latch_axle_r_m,
        meta={"positive_motion": "swings the lock away from the opposite grip"},
    )
    return latch


def build_rivet_squeeze(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "rivet_squeeze",
            "small_class": "rivet_squeeze",
            "slot_choices": slot_choices_for_config(r),
            "source_family": "pictureX/0611/rivet_squeeze",
        },
    )
    mats = _materials(model, r)
    frame = _build_frame(model, r, mats)
    member, drive, link = _build_mechanism(model, r, mats, frame)
    _build_dies(model, r, mats, frame)
    _build_handle_lock(model, r, mats, frame, member)

    drive_name = _drive_joint_name(r)
    ram_name = f"head_module__{r.head_module}__upper_die_drive"
    risk = [
        {drive_name: drive.motion_limits.upper, ram_name: -r.upper_die_travel_m},
        {drive_name: drive.motion_limits.upper},
        {ram_name: -r.upper_die_travel_m},
    ]
    if r.lower_die_parent_role == "frame":
        anvil = f"head_module__{r.head_module}__lower_die_adjust"
        risk.append({ram_name: -r.upper_die_travel_m, anvil: r.anvil_adjust_eff_m})
        risk.append({ram_name: 0.0, anvil: -r.anvil_adjust_eff_m})
        model.meta["coupled_joint_pairs"] = ((ram_name, anvil), (drive_name, ram_name))
    else:
        model.meta["coupled_joint_pairs"] = ((drive_name, ram_name),)
    model.meta["risk_poses"] = tuple(risk)
    return model


def build_seeded_rivet_squeeze(seed: int, *, assets: AssetContext | None = None):
    return build_rivet_squeeze(config_from_seed(seed), assets=assets)


# ===========================================================================
# Author tests.  These express the category's own mechanical invariants -- the
# ones the SourceMap distilled from all 13 records -- as derived-parameter
# arithmetic and part/joint structure.  Mesh assets, exact collision, sampled
# poses and isolated-geometry belong to the sweep harness, so nothing here
# probes a mesh element.
# ===========================================================================
def _part_by_role(model: ArticulatedObject, role: str):
    for part in model.parts:
        if part.meta.get("role") == role:
            return part
    return None


def _joint(model: ArticulatedObject, name: str):
    for joint in model.articulations:
        if joint.name == name:
            return joint
    return None


def _axis(joint) -> tuple[float, float, float]:
    return tuple(round(float(v), 9) for v in joint.axis)


def _origin_xyz(joint) -> tuple[float, float, float]:
    return tuple(round(float(v), 9) for v in joint.origin.xyz)


def run_rivet_squeeze_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    frame = _part_by_role(object_model, "frame")
    upper = _part_by_role(object_model, "upper_die")
    lower = _part_by_role(object_model, "lower_die")
    jaw = _part_by_role(object_model, "moving_jaw")
    lever = _part_by_role(object_model, "squeeze_lever")
    link = _part_by_role(object_model, "compound_link")
    latch = _part_by_role(object_model, "handle_lock")
    drive = _joint(object_model, _drive_joint_name(r))
    ram_joint = _joint(object_model, f"head_module__{r.head_module}__upper_die_drive")
    anvil_joint = _joint(object_model, f"head_module__{r.head_module}__lower_die_adjust")
    latch_joint = (
        _joint(object_model, f"handle_lock__{r.handle_lock}__latch_pivot")
        if r.handle_lock != "no_handle_lock"
        else None
    )
    frame_elems = {v.name or "" for v in frame.visuals} if frame is not None else set()
    roots = [
        p.name
        for p in object_model.parts
        if not any(j.child == p.name for j in object_model.articulations)
    ]

    # ---- anchor: rivet_squeeze_frame_bores_identity ------------------------
    ctx.check(
        "category_anchor: the frame is the single grounded root and carries the fixed grip",
        frame is not None
        and roots == ["frame"]
        and f"yoke_frame__{r.yoke_frame}__forged_body" in frame_elems
        and r.fixed_grip_is_separate_part == "no"
        and r.fixed_grip_len_m > 0.02,
        details=f"roots={roots}, grip_len={r.fixed_grip_len_m:.4f}, elems={sorted(frame_elems)}",
    )
    ctx.check(
        "category_anchor: the handle pivot bore and both die guide bores are really cut through material",
        r.main_pivot_bore_r_m > r.main_pivot_pin_r_m
        and r.ram_guide_bore_r_m > r.upper_die_shaft_r_m
        and r.anvil_guide_bore_r_m > r.anvil_shaft_r_m
        and r.ram_guide_depth_m >= 0.020
        and r.anvil_guide_depth_m >= 0.020,
        details=(
            f"pivot {r.main_pivot_bore_r_m:.5f}/{r.main_pivot_pin_r_m:.5f}, "
            f"ram {r.ram_guide_bore_r_m:.5f}/{r.upper_die_shaft_r_m:.5f}, "
            f"anvil {r.anvil_guide_bore_r_m:.5f}/{r.anvil_shaft_r_m:.5f}"
        ),
    )
    ctx.check(
        "category_anchor: every shaft clears its guide bore by at least 1.0 mm radially",
        (r.ram_guide_bore_r_m - r.upper_die_shaft_r_m) >= 0.0011 - 1e-9
        and (r.anvil_guide_bore_r_m - r.anvil_shaft_r_m) >= 0.0010 - 1e-9
        and (r.main_pivot_bore_r_m - r.main_pivot_pin_r_m) >= 0.0009 - 1e-9
        and r.max_die_step_r_m > 0.0,
        details=(
            f"ram={r.ram_guide_bore_r_m - r.upper_die_shaft_r_m:.5f}, "
            f"anvil={r.anvil_guide_bore_r_m - r.anvil_shaft_r_m:.5f}, "
            f"pivot={r.main_pivot_bore_r_m - r.main_pivot_pin_r_m:.5f}"
        ),
    )
    die_span = r.open_die_gap_m + r.upper_die_stack_h_m + r.lower_die_stack_h_m
    ctx.check(
        "category_anchor: the throat opening exceeds the die stack plus the full squeeze stroke",
        r.throat_open_m >= die_span + 0.003 - 1e-9
        and r.throat_stroke_clearance_m > 0.0
        and r.upper_jaw_underside_z_m > r.upper_die_tip_offset_m + r.upper_die_stack_h_m - 1e-9
        and r.lower_jaw_top_z_m < -(r.lower_die_tip_offset_m + r.lower_die_stack_h_m) + 1e-9,
        details=(
            f"throat={r.throat_open_m:.5f}, span={die_span:.5f}, "
            f"clearance={r.throat_stroke_clearance_m:.5f}"
        ),
    )

    # ---- anchor: rivet_squeeze_effort_ordering -----------------------------
    efforts = [r.ram_effort_eff_n, r.anvil_effort_eff_n, r.drive_effort_eff_n]
    if latch_joint is not None:
        efforts.append(r.latch_effort_eff_n)
    ctx.check(
        "category_anchor: joint effort is ordered upper die > lower die > hand drive > latch",
        all(a > b for a, b in zip(efforts, efforts[1:], strict=False))
        and ram_joint is not None
        and abs(float(ram_joint.motion_limits.effort) - r.ram_effort_eff_n) < 1e-6
        and (
            anvil_joint is None
            or abs(float(anvil_joint.motion_limits.effort) - r.anvil_effort_eff_n) < 1e-6
        ),
        details=f"efforts={[round(e, 3) for e in efforts]}",
    )
    die_parts = [p for p in (upper, lower) if p is not None]
    ctx.check(
        "category_anchor: each die is emitted as a single welded solid, one visual per die part",
        bool(die_parts) and all(len(p.visuals) == 1 for p in die_parts),
        details=f"visual_counts={[len(p.visuals) for p in die_parts]}",
    )

    # ---- anchor: rivet_squeeze_opposed_dies_identity -----------------------
    if _MECH_HAS_RAM[r.squeeze_mechanism]:
        coaxial = (
            ram_joint is not None
            and anvil_joint is not None
            and abs(_origin_xyz(ram_joint)[0] - _origin_xyz(anvil_joint)[0]) < 0.0005
            and abs(_origin_xyz(ram_joint)[1] - _origin_xyz(anvil_joint)[1]) < 0.0005
        )
        ctx.check(
            "category_anchor: the two die tips are coaxial in plan within 0.5 mm",
            coaxial
            and upper is not None
            and lower is not None
            and _axis(ram_joint) == (0.0, 0.0, 1.0),
            details=(
                f"ram={None if ram_joint is None else _origin_xyz(ram_joint)}, "
                f"anvil={None if anvil_joint is None else _origin_xyz(anvil_joint)}"
            ),
        )
        ctx.check(
            "category_anchor: the two die tips stay coaxial through the full anvil adjustment",
            coaxial
            and anvil_joint is not None
            and _axis(anvil_joint) == _axis(ram_joint)
            and r.die_axis_y_m == 0.0,
            details="both prismatic axes are the shared squeeze axis, so travel is purely axial",
        )
        closed_gap = r.open_die_gap_m - r.upper_die_travel_m
        worst = closed_gap - r.anvil_adjust_eff_m
        ctx.check(
            "category_anchor: the squeeze stroke closes the die gap to at most 6 mm without penetrating",
            0.0 < closed_gap <= 0.006 + 1e-9
            and worst > 0.0
            and abs(r.ram_travel_m - (r.open_die_gap_m - r.closing_residual_eff_m)) < 1e-9,
            details=(
                f"open={r.open_die_gap_m:.5f}, travel={r.upper_die_travel_m:.5f}, "
                f"closed={closed_gap:.5f}, worst_with_anvil={worst:.5f}"
            ),
        )
        ctx.check(
            "category_anchor: the lower die adjustment is bidirectional about its rest position",
            anvil_joint is not None
            and anvil_joint.motion_limits.lower < 0.0 < anvil_joint.motion_limits.upper
            and r.anvil_adjust_eff_m > 0.0,
            details=f"adjust=+-{r.anvil_adjust_eff_m:.5f}",
        )

    # ---- anchor: rivet_squeeze_direct_jaw_identity -------------------------
    if r.squeeze_mechanism == "direct_jaw_lever":
        ctx.check(
            "category_anchor: the moving jaw carries a lower rivet set on the squeeze axis",
            jaw is not None
            and r.lower_die_parent_role == "moving_jaw"
            and lower is None
            and float(r.p["lower_set_boss_r_m"]) > 0.0,
            details=f"jaw={None if jaw is None else jaw.name}",
        )
        ctx.check(
            "category_anchor: the upper die and the moving jaw set are coaxial in plan within 0.5 mm",
            ram_joint is not None
            and abs(_origin_xyz(ram_joint)[0] - r.die_axis_x_m) < 0.0005
            and abs(_origin_xyz(ram_joint)[1] - r.die_axis_y_m) < 0.0005,
            details=f"station={r.die_axis_x_m:.5f}",
        )
        jaw_rise = r.grip_lever_arm_m * 0.0 + r.die_station_x_m * math.sin(r.lever_travel_eff_rad)
        ctx.check(
            "category_anchor: closing the jaw reduces the set gap without the jaws interpenetrating",
            jaw_rise > 0.0 and (r.open_die_gap_m - r.upper_die_travel_m - jaw_rise) >= 0.0003,
            details=(
                f"rise={jaw_rise:.5f}, upper_travel={r.upper_die_travel_m:.5f}, "
                f"gap={r.open_die_gap_m:.5f}"
            ),
        )

    # ---- anchor: rivet_squeeze_hand_lever_identity -------------------------
    if _MECH_HAS_HAND_LEVER[r.squeeze_mechanism] and _MECH_HAS_RAM[r.squeeze_mechanism]:
        ctx.check(
            "category_anchor: the hand lever turns about the tool width axis through its pivot bore",
            lever is not None
            and drive is not None
            and drive.articulation_type == ArticulationType.REVOLUTE
            and _axis(drive) == (0.0, 1.0, 0.0)
            and _origin_xyz(drive) == (0.0, 0.0, 0.0)
            and abs(r.lever_pivot_bore_r_m - (r.main_pivot_bore_r_m - 0.0004)) < 1e-9
            and abs(r.main_pivot_pin_r_m - (r.lever_pivot_bore_r_m - 0.0006)) < 1e-9,
            details=f"axis={None if drive is None else _axis(drive)}",
        )
        ctx.check(
            "category_anchor: the lever rest angle is the open pose and travel is one-directional",
            drive is not None
            and abs(float(drive.motion_limits.lower)) < 1e-12
            and 0.03 <= float(drive.motion_limits.upper) <= 0.45,
            details=f"limits=({drive.motion_limits.lower}, {drive.motion_limits.upper})",
        )
        ctx.check(
            "category_anchor: the closed grip gap stays between 0.5 mm and 5 mm",
            0.0005 <= r.closed_grip_gap_m <= 0.005
            and r.moving_grip_centre_z_m > r.fixed_grip_centre_z_m,
            details=f"closed_gap={r.closed_grip_gap_m:.5f}",
        )
        ctx.check(
            "category_anchor: full lever travel moves the moving grip at least 25 mm",
            r.grip_drop_m >= 0.025,
            details=f"drop={r.grip_drop_m:.5f}, arm={r.grip_lever_arm_m:.5f}",
        )

    # ---- anchor: rivet_squeeze_screw_drive_identity ------------------------
    if r.squeeze_mechanism == "screw_press":
        ctx.check(
            "category_anchor: the drive head turns about the squeeze axis, not the tool width axis",
            drive is not None
            and drive.articulation_type == ArticulationType.REVOLUTE
            and _axis(drive) == (0.0, 0.0, 1.0)
            and abs(_origin_xyz(drive)[0] - r.die_axis_x_m) < 1e-9,
            details=f"axis={None if drive is None else _axis(drive)}",
        )
        slide = _joint(object_model, "squeeze_mechanism__screw_press__tommy_slide")
        ctx.check(
            "category_anchor: the tommy bar slides through the drive head and stays retained at both extremes",
            link is not None
            and slide is not None
            and slide.articulation_type == ArticulationType.PRISMATIC
            and _axis(slide) == (0.0, 1.0, 0.0)
            and r.tommy_bushing_r_m < float(r.p["tommy_bore_r_m"])
            and 2.0 * float(r.p["tommy_slide_range_m"]) < float(r.p["tommy_bar_len_m"]) * 0.9,
            details=(
                f"slide=+-{r.p['tommy_slide_range_m']:.4f}, bar={r.p['tommy_bar_len_m']:.4f}, "
                f"bushing={r.tommy_bushing_r_m:.5f}/{r.p['tommy_bore_r_m']:.5f}"
            ),
        )
        ctx.check(
            "category_anchor: the declared turn range times the screw lead covers the authored ram travel",
            r.ram_travel_available_m >= r.ram_travel_m - 1e-9
            and r.screw_turn_range_eff_rad >= float(r.p["screw_turn_range_rad"]) - 1e-9,
            details=(
                f"available={r.ram_travel_available_m:.5f}, needed={r.ram_travel_m:.5f}, "
                f"turns={r.screw_turn_range_eff_rad:.4f}"
            ),
        )

    # ---- template-level invariants ----------------------------------------
    ctx.check(
        "the moving members keep a real lateral stand-off from the frame cheek",
        r.lever_y_inner_m <= -(r.frame_half_w_m + 0.0010) + 1e-9
        and abs(r.link_y_centre_m) > abs(r.lever_y_outer_m),
        details=(
            f"frame_half={r.frame_half_w_m:.5f}, lever={r.lever_y_inner_m:.5f}"
            f"..{r.lever_y_outer_m:.5f}, link={r.link_y_centre_m:.5f}"
        ),
    )
    ctx.check(
        "the latch eye is a real annulus centred on its own hinge axis",
        r.handle_lock == "no_handle_lock"
        or (
            latch is not None
            and latch_joint is not None
            and abs(r.latch_eye_bore_r_m - r.latch_axle_r_m - 0.0002) < 1e-9
            and _origin_xyz(latch_joint) == tuple(round(v, 9) for v in r.latch_origin_xyz)
        ),
        details=f"eye={r.latch_eye_bore_r_m:.5f}, axle={r.latch_axle_r_m:.5f}",
    )
    ctx.check(
        "the cam candidate grows its reaction bracket and no other candidate does",
        (r.reaction_bracket_required == "yes") == (r.squeeze_mechanism == "eccentric_cam")
        and (
            r.reaction_bracket_required == "no"
            or (r.reaction_bracket_x_m > 0.0 and r.cam_bearing_clearance_m > 0.0)
        ),
        details=f"required={r.reaction_bracket_required}, x={r.reaction_bracket_x_m:.5f}",
    )
    ctx.check(
        "domain choices are recorded on the model",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )

    # ---- allowances: joint-carried members, per contact_policy -------------
    for part in (lever, jaw, link, latch, upper, lower):
        if part is None:
            continue
        ctx.allow_isolated_part(
            part,
            reason=(
                "Joint-retained member intentionally disconnected by clearance: this part "
                "runs in a bored guide or on a pivot pin with the running fit generalised "
                "from record 001 (pin_r = bore_r - 0.6 mm, guide_bore_r = shaft_r + "
                "1.1-1.2 mm), and its registered axis mate is what carries it. Closing "
                "that clearance to make contact would jam the mechanism."
            ),
        )
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    return ctx.report()


# ===========================================================================
# High-risk cross-slot corners.  The design names two explicitly; the rest are
# the coupled continuous extremes the sweeps cannot reach on their own.
# ===========================================================================
TEMPLATE_CORNERS = (
    corner_case(
        "tightest_throat_tallest_stack",
        {
            "yoke_frame": "compact_straight_head",
            "squeeze_mechanism": "hidden_internal_toggle",
            "head_module": "plain_die_pair",
            "return_element": "torsion_handle_spring",
            "handle_lock": "wire_hook_latch",
            "jaw_throat_height_m": 0.024,
            "die_station_x_m": 0.058,
            "open_die_gap_m": 0.015,
            "die_tip_r_m": 0.0078,
            "anvil_adjust_range_m": 0.005,
        },
        reason=(
            "Design risk 1: the pool's tightest throat against the tallest die stack and "
            "the largest open gap, at the shortest die station."
        ),
    ),
    corner_case(
        "screw_drive_against_the_largest_stroke",
        {
            "yoke_frame": "compact_straight_head",
            "squeeze_mechanism": "screw_press",
            "head_module": "plain_die_pair",
            "return_element": "torsion_handle_spring",
            "handle_lock": "eye_and_wire_loop_latch",
            "open_die_gap_m": 0.015,
            "closing_residual_m": 0.0,
            "lead_m_per_turn": 0.001,
            "screw_turn_range_rad": 1.5708,
            "tommy_bar_len_m": 0.24,
            "tommy_slide_range_m": 0.045,
        },
        reason=(
            "Design risk 2: the screw press must widen its own turn range to deliver the "
            "largest authored stroke at the finest lead, with the longest tommy bar."
        ),
    ),
    corner_case(
        "alligator_jaw_with_a_screw_press_anvil",
        {
            "yoke_frame": "alligator_jaw",
            "squeeze_mechanism": "screw_press",
            "head_module": "quick_change_yoke_clip",
            "return_element": "torsion_handle_spring",
            "handle_lock": "eye_and_wire_loop_latch",
            "receiver_len_m": 0.048,
            "frame_reach_m": 0.185,
            "die_station_x_m": 0.14,
        },
        reason=(
            "The slot-decomposition correction's own worked example: a screw press under a "
            "long upper jaw with a normal anvil in the throat, at the deepest receiver."
        ),
    ),
    corner_case(
        "direct_jaw_at_the_shortest_arc",
        {
            "yoke_frame": "alligator_jaw",
            "squeeze_mechanism": "direct_jaw_lever",
            "head_module": "rotating_set_holder",
            "return_element": "leaf_return_spring",
            "handle_lock": "wire_hook_latch",
            "lever_travel_rad": 0.0175,
            "jaw_reach_m": 0.215,
            "open_die_gap_m": 0.0035,
            "die_station_x_m": 0.14,
        },
        reason=(
            "The alligator squeezer at its source arc: the handle IS the jaw, so the "
            "smallest gap and the longest jaw have to close without interpenetrating."
        ),
    ),
    corner_case(
        "widest_lever_on_the_narrowest_frame",
        {
            "yoke_frame": "long_c_yoke_throat",
            "squeeze_mechanism": "long_toggle_cheek",
            "head_module": "stepped_cylinder_dies",
            "return_element": "torsion_handle_spring",
            "handle_lock": "wire_hook_latch",
            "frame_width_m": 0.017,
            "lever_plate_width_m": 0.05,
            "link_cheek_offset_m": 0.038,
            "ram_cross_pin_len_m": 0.08,
            "lever_travel_rad": 0.36,
        },
        reason=(
            "The lateral layering at its worst: 002's widest forked handle on the narrowest "
            "forging, with the longest toggle cross pin reaching toward the link band."
        ),
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_rivet_squeeze",
    "build_seeded_rivet_squeeze",
    "run_rivet_squeeze_tests",
]
