# SPDX-License-Identifier: Apache-2.0

"""Roller conveyor — Design-backed single-file template.

Built from ``articraft_template_authoring/source_maps/roller_conveyor.md`` and
``articraft_template_authoring/designs/roller_conveyor.json``.

Frame convention: ``+X`` is the conveying direction, ``+Y`` is the roller spin
axis, ``+Z`` is up and ``z = 0`` is the floor.  ``swept_curved_arc`` is the one
candidate whose spin axis is not global ``+Y``: it is the local radial direction
``(sin d, cos d, 0)`` at each station (source
``rec_0611_roller_conveyor_var_frame_form_curved_arc`` model.py:L391-L398).

Part tree — the frame is the only root:

* ``frame_form__<candidate>__frame`` (role ``conveyor_frame``) — rails, under-bed
  members, bearing inserts, and every leg that stays frame geometry.
* ``roller_form__<candidate>__roller_{i}`` (role ``conveyor_roller``) — N rollers,
  each on its own CONTINUOUS joint, all parented to the frame, never chained.
* ``support_form__<candidate>__leveling_foot_{k}`` (role ``leveling_foot``).
* ``support_form__folding_hinged_legs__folding_leg_{k}`` (role ``folding_leg``) —
  the only depth-2 chain in the category; its foot re-parents onto the leg.

Contact handling follows ``MECHANICAL_PRIORS.md`` 1c through the Design's named
overlaps rather than through allowances:

* Anything that never moves is a frame visual meeting another frame visual, so it
  is INTRA-part and invisible to ``fail_if_parts_overlap_*``.  Those joins take a
  deliberate ``structural_weld_embed_m`` / ``fitting_weld_embed_m`` embed instead
  of the source's exact tangency (002 L142-L149 web top 0.865 = flange bottom
  0.865; L39-L41 vs L165 leg top 0.640 = crossmember bottom 0.640).
* Anything that moves keeps a real gap: the axle end against the bearing insert,
  the frame ring against the end cap, adjacent rollers at ``pitch - 2r >= 0.016``,
  the leveler jaw against the stem, the telescoping sleeve bore.
* ``interpart_connection_policy = 'none_all_joint_carried'`` — there is no rigid
  inter-part connection anywhere in this category, so every non-root part is
  carried by its joint and declared with ``ctx.allow_isolated_part``.
  ``ctx.allow_overlap`` is never called; the source pool's 96 calls are all
  replaced by real bores, real clearances and a re-derived curved bearing.

Three source defects the rebuild corrects, each marked ``SOURCE DEFECT`` below:

1. ``support_scissor_base`` L85-L98 authors the pivot bolt and both flanges as
   Z-axis cylinders although the arms lie in the YZ plane; the pin runs along X.
2. ``support_folding_legs`` L79-L84 puts the pivot bolt at local ``z = -0.008``,
   8 mm below the hinge axis its own joint declares at ``HINGE_Z``.
3. ``frame_form_expanding_straight`` L150 bottoms its pads at ``z = 0.015``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    LatheGeometry,
    MotionLimits,
    MotionProperties,
    Origin,
    PlaneInterface,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mate_planes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
    sweep_profile_along_spline,
)

FrameForm = Literal[
    "low_profile_extrusion_deck",
    "deep_channel_rail_bed",
    "pantograph_scissor_chords",
    "swept_curved_arc",
]
SupportForm = Literal[
    "fixed_corner_plate_feet",
    "square_tube_legs_leveling_feet",
    "telescoping_sleeve_legs",
    "folding_hinged_legs",
    "scissor_crossed_base",
]
RollerForm = Literal[
    "shell_axle_endcaps",
    "steel_tube_endcaps",
    "split_twin_half_roller",
]
RollerLayout = Literal["uniform_inline", "staggered_alternating_height"]

FRAME_FORMS: tuple[FrameForm, ...] = (
    "low_profile_extrusion_deck",
    "deep_channel_rail_bed",
    "pantograph_scissor_chords",
    "swept_curved_arc",
)
SUPPORT_FORMS: tuple[SupportForm, ...] = (
    "fixed_corner_plate_feet",
    "square_tube_legs_leveling_feet",
    "telescoping_sleeve_legs",
    "folding_hinged_legs",
    "scissor_crossed_base",
)
ROLLER_FORMS: tuple[RollerForm, ...] = (
    "shell_axle_endcaps",
    "steel_tube_endcaps",
    "split_twin_half_roller",
)
ROLLER_LAYOUTS: tuple[RollerLayout, ...] = (
    "uniform_inline",
    "staggered_alternating_height",
)
# N is multiplicity: contiguous 4..24.  The bounds come from the mechanism, the
# host capacity and the pose/collision budget, not from the source integers.
ROLLER_COUNTS: tuple[int, ...] = tuple(range(4, 25))

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("frame_form", FRAME_FORMS, role="host beam frame"),
        component_slot("support_form", SUPPORT_FORMS, role="floor support"),
        component_slot("roller_form", ROLLER_FORMS, role="rotating member"),
        component_slot("roller_layout", ROLLER_LAYOUTS, role="station placement rule"),
        multiplicity_slot(
            "roller_count",
            ROLLER_COUNTS,
            role="rollers on the bed",
            item_slot="roller_form",
        ),
    )
)

# --------------------------------------------------------------------------- #
# Declared independent-parameter ranges, one entry per Design parameter.
# Names repeat across candidates in a slot; the range that applies is the one
# declared by the candidate that is actually built, so every clamp below is
# candidate-scoped.
# --------------------------------------------------------------------------- #

_FRAME_RANGES: dict[str, dict[str, tuple[float, float]]] = {
    "low_profile_extrusion_deck": {
        "frame_outer_width_m": (0.500, 1.000),
        "rail_thickness_m": (0.028, 0.055),
        "bed_height_m": (0.170, 0.900),
        "roller_pitch_m": (0.055, 0.200),
        "end_inset_m": (0.060, 0.140),
        "upper_rail_height_m": (0.055, 0.130),
        "lower_rail_height_m": (0.022, 0.055),
        "rail_top_above_crown_m": (-0.024, -0.004),
    },
    "deep_channel_rail_bed": {
        "frame_outer_width_m": (0.500, 1.000),
        "rail_thickness_m": (0.028, 0.055),
        "bed_height_m": (0.170, 0.900),
        "frame_length_authored_m": (1.200, 3.000),
        "web_height_m": (0.095, 0.210),
        "top_flange_h_m": (0.015, 0.040),
        "bottom_flange_h_m": (0.010, 0.028),
        "flange_width_m": (0.050, 0.110),
        "rail_top_above_crown_m": (0.018, 0.058),
    },
    "pantograph_scissor_chords": {
        "frame_outer_width_m": (0.500, 1.000),
        "rail_thickness_m": (0.028, 0.055),
        "bed_height_m": (0.170, 0.900),
        "roller_pitch_m": (0.055, 0.200),
        "end_inset_m": (0.060, 0.140),
        "chord_height_m": (0.012, 0.034),
        "chord_width_m": (0.024, 0.052),
        "bottom_chord_z_m": (0.018, 0.060),
        "scissor_bar_thickness_m": (0.0035, 0.0090),
        "rail_top_above_crown_m": (-0.014, -0.002),
    },
    "swept_curved_arc": {
        "frame_outer_width_m": (0.500, 1.000),
        "rail_thickness_m": (0.028, 0.055),
        "bed_height_m": (0.170, 0.900),
        "arc_radius_m": (1.500, 8.000),
        "arc_angle_rad": (0.300, 1.200),
        "web_height_m": (0.095, 0.210),
        "top_flange_h_m": (0.015, 0.040),
        "bottom_flange_h_m": (0.010, 0.028),
        "flange_width_m": (0.050, 0.110),
        "rail_top_above_crown_m": (0.018, 0.058),
    },
}
_FRAME_CHOICES: dict[str, dict[str, tuple[int, ...]]] = {
    "low_profile_extrusion_deck": {"cross_brace_count": (2, 3, 4)},
    "deep_channel_rail_bed": {"crossmember_count": (5, 7, 9)},
    "pantograph_scissor_chords": {"scissor_bays": (2, 3, 4)},
    "swept_curved_arc": {"arc_path_samples": (32, 48, 64)},
}

_SUPPORT_RANGES: dict[str, dict[str, tuple[float, float]]] = {
    "fixed_corner_plate_feet": {
        "corner_plate_inset_m": (0.008, 0.030),
        "corner_plate_h_m": (0.120, 0.320),
        "corner_plate_t_m": (0.012, 0.032),
        "foot_pad_l_m": (0.065, 0.145),
        "foot_pad_w_m": (0.038, 0.085),
        "foot_pad_h_m": (0.008, 0.020),
    },
    "square_tube_legs_leveling_feet": {
        "foot_pad_r_m": (0.035, 0.075),
        "foot_pad_h_m": (0.016, 0.038),
        "leg_outer_m": (0.040, 0.090),
        "leg_wall_m": (0.004, 0.012),
        "leg_height_m": (0.320, 0.760),
        "foot_travel_m": (0.018, 0.090),
        "foot_stem_r_m": (0.007, 0.017),
        "foot_stem_length_m": (0.100, 0.230),
    },
    "telescoping_sleeve_legs": {
        "foot_pad_r_m": (0.035, 0.075),
        "foot_pad_h_m": (0.016, 0.038),
        "sleeve_outer_r_m": (0.020, 0.045),
        "sleeve_wall_m": (0.003, 0.008),
        "inner_tube_r_m": (0.015, 0.036),
        "inner_tube_length_m": (0.180, 0.400),
        "collar_r_m": (0.024, 0.054),
        "leg_height_m": (0.320, 0.760),
        "foot_travel_m": (0.040, 0.120),
    },
    "folding_hinged_legs": {
        "foot_pad_r_m": (0.035, 0.075),
        "foot_pad_h_m": (0.016, 0.038),
        "leg_outer_m": (0.040, 0.090),
        "leg_wall_m": (0.004, 0.012),
        "leg_height_m": (0.320, 0.760),
        "fold_upper_rad": (0.900, 1.570),
        "hinge_lug_half_gap_m": (0.016, 0.038),
        "hinge_lug_h_m": (0.050, 0.120),
        "foot_travel_m": (0.018, 0.090),
        "foot_stem_r_m": (0.007, 0.017),
        "foot_stem_length_m": (0.100, 0.230),
    },
    "scissor_crossed_base": {
        "foot_pad_r_m": (0.035, 0.075),
        "foot_pad_h_m": (0.016, 0.038),
        "foot_stance_y_m": (0.300, 0.700),
        "scissor_arm_thickness_m": (0.011, 0.028),
        "scissor_arm_width_m": (0.035, 0.080),
        "pivot_bolt_r_m": (0.010, 0.026),
        "scissor_top_z_m": (0.400, 0.900),
        "foot_travel_m": (0.018, 0.090),
        "foot_stem_r_m": (0.007, 0.017),
        "foot_stem_length_m": (0.100, 0.230),
    },
}
_LEG_STATION_CHOICES: tuple[int, ...] = (2, 3)

_ROLLER_RANGES_SHARED: dict[str, tuple[float, float]] = {
    "roller_radius_m": (0.018, 0.042),
    "roller_length_m": (0.380, 0.820),
    "axle_r_m": (0.0040, 0.0105),
    "axle_overhang_m": (0.004, 0.055),
    "end_cap_r_m": (0.012, 0.040),
    "end_cap_length_m": (0.005, 0.026),
    "end_cap_inset_m": (-0.020, 0.020),
    "running_clearance_m": (0.00015, 0.00060),
}
_ROLLER_RANGES: dict[str, dict[str, tuple[float, float]]] = {
    "shell_axle_endcaps": dict(
        _ROLLER_RANGES_SHARED,
        highlight_strip_w_m=(0.004, 0.010),
        highlight_proud_m=(0.0002, 0.0010),
    ),
    "steel_tube_endcaps": dict(_ROLLER_RANGES_SHARED),
    "split_twin_half_roller": dict(
        _ROLLER_RANGES_SHARED,
        split_gap_m=(0.016, 0.055),
        sleeve_bore_r_m=(0.0065, 0.0180),
        sleeve_outer_r_m=(0.020, 0.040),
    ),
}
_STAGGER_RANGE = (0.010, 0.045)

# Hard mechanical constants of the category (not diversity dimensions).
_MIN_ROLLER_GAP = 0.016  # 001 L419-L427 asserts 0.016..0.020 per adjacent pair.
_MIN_BARREL_CLEARANCE = 0.010  # 001 runs 0.014, 002 runs 0.0555.
_MIN_BEARING_INSERT = 0.004
_BEARING_WALL = 0.010  # 001: bore 0.0085 -> outer 0.019.  002: r 0.018.
_MIN_STEM_RETENTION = 0.025  # 002 L460-L467 asserts 0.025 at full extension.
_BEARING_HOST_MARGIN = 0.002
# Lathe tessellation for every annular fitting; a lathed surface is inscribed in
# its nominal radius, so welds onto one measure from `r * cos(pi / segments)`.
_LATHE_SEGMENTS = 20


@dataclass(frozen=True)
class RollerConveyorConfig:
    frame_form: FrameForm = "deep_channel_rail_bed"
    support_form: SupportForm = "square_tube_legs_leveling_feet"
    roller_form: RollerForm = "steel_tube_endcaps"
    roller_layout: RollerLayout = "uniform_inline"
    roller_count: int = 24

    # frame_form
    frame_outer_width_m: float = 0.915
    rail_thickness_m: float = 0.045
    bed_height_m: float = 0.820
    roller_pitch_m: float = 0.070
    end_inset_m: float = 0.095
    upper_rail_height_m: float = 0.090
    lower_rail_height_m: float = 0.035
    rail_top_above_crown_m: float = 0.036
    cross_brace_count: int = 2
    frame_length_authored_m: float = 2.400
    web_height_m: float = 0.150
    top_flange_h_m: float = 0.025
    bottom_flange_h_m: float = 0.015
    flange_width_m: float = 0.075
    crossmember_count: int = 7
    scissor_bays: int = 3
    chord_height_m: float = 0.020
    chord_width_m: float = 0.035
    bottom_chord_z_m: float = 0.030
    scissor_bar_thickness_m: float = 0.005
    arc_radius_m: float = 3.000
    arc_angle_rad: float = 0.800
    arc_path_samples: int = 48

    # support_form
    leg_station_count: int = 3
    corner_plate_inset_m: float = 0.015
    corner_plate_h_m: float = 0.209
    corner_plate_t_m: float = 0.020
    foot_pad_l_m: float = 0.100
    foot_pad_w_m: float = 0.058
    foot_pad_r_m: float = 0.052
    foot_pad_h_m: float = 0.025
    leg_outer_m: float = 0.060
    leg_wall_m: float = 0.007
    leg_height_m: float = 0.520
    foot_travel_m: float = 0.030
    foot_stem_r_m: float = 0.011
    foot_stem_length_m: float = 0.155
    sleeve_outer_r_m: float = 0.030
    sleeve_wall_m: float = 0.005
    inner_tube_r_m: float = 0.024
    inner_tube_length_m: float = 0.280
    collar_r_m: float = 0.036
    fold_upper_rad: float = 1.300
    hinge_lug_half_gap_m: float = 0.024
    hinge_lug_h_m: float = 0.080
    foot_stance_y_m: float = 0.500
    scissor_arm_thickness_m: float = 0.018
    scissor_arm_width_m: float = 0.055
    pivot_bolt_r_m: float = 0.016
    scissor_top_z_m: float = 0.520

    # roller_form
    roller_radius_m: float = 0.034
    roller_length_m: float = 0.684
    axle_r_m: float = 0.006
    axle_overhang_m: float = 0.0405
    end_cap_r_m: float = 0.032
    end_cap_length_m: float = 0.018
    end_cap_inset_m: float = 0.009
    running_clearance_m: float = 0.00030
    highlight_strip_w_m: float = 0.006
    highlight_proud_m: float = 0.0004
    split_gap_m: float = 0.030
    sleeve_bore_r_m: float = 0.012

    # roller_layout
    stagger_offset_m: float = 0.025

    name: str = "roller_conveyor"


@dataclass(frozen=True)
class ResolvedRollerConveyorConfig:
    frame_form: FrameForm
    support_form: SupportForm
    roller_form: RollerForm
    roller_layout: RollerLayout
    roller_count: int

    # --- binding count_to_station_rule ------------------------------------
    frame_length_mode: str
    frame_length_m: float
    station_pitch_m: float
    station_span_m: float
    frame_end_crossmember_x_m: float
    frame_corner_plate_x_m: float
    frame_groove_length_m: float
    frame_cross_brace_x_m: float
    roller_gap_m: float

    # --- binding frame_rail_to_roller_bearing -----------------------------
    frame_outer_width_m: float
    rail_thickness_m: float
    rail_centre_y_m: float
    rail_inner_y_m: float
    roller_radius_m: float
    roller_length_m: float
    roller_half_length_m: float
    axle_r_m: float
    axle_overhang_m: float
    axle_half_length_m: float
    end_cap_r_m: float
    end_cap_length_m: float
    end_cap_inset_m: float
    running_clearance_m: float
    barrel_axial_clearance_m: float
    end_cap_axial_clearance_m: float
    structural_weld_embed_m: float
    fitting_weld_embed_m: float
    interpart_connection_policy: str
    bearing_insert_length_m: float
    bearing_inner_face_y_m: float
    bearing_bore_r_m: float
    bearing_outer_r_m: float
    roller_support_policy: str
    split_gap_m: float
    sleeve_bore_r_m: float
    split_sleeve_bore_clearance_m: float
    split_sleeve_outer_r_m: float
    highlight_strip_w_m: float
    highlight_proud_m: float

    # --- binding frame_deck_to_roller_bed ---------------------------------
    bed_height_m: float
    bed_plane_z_m: float
    rail_top_above_crown_m: float
    rail_top_z_m: float
    rail_guard_height_m: float
    rail_stack_height_m: float
    bed_clear_width_m: float
    roller_containment_margin_m: float
    stagger_offset_m: float

    # --- binding frame_to_support_mount -----------------------------------
    support_mount_z_m: float
    under_bed_drop_m: float
    leg_head_z_m: float
    leg_head_engagement_z_m: float
    leg_station_count: int
    leg_station_span_m: float
    leg_station_y_m: float
    leg_footprint_u_m: float
    leg_footprint_v_m: float
    support_joint_topology: str
    foot_part_count: int
    folding_leg_part_count: int

    # --- binding support_leg_to_foot_stroke -------------------------------
    support_drop_m: float
    leg_local_length_m: float
    hinge_standoff_m: float
    hinge_pin_r_m: float
    leg_bottom_z_m: float
    foot_joint_origin_z_m: float
    sliding_member_length_m: float
    sliding_member_r_m: float
    stem_local_offset_m: float
    stem_top_local_m: float
    stem_insertion_min_m: float
    foot_travel_m: float
    foot_pad_r_m: float
    foot_pad_h_m: float
    foot_pad_l_m: float
    foot_pad_w_m: float
    floor_pad_u_m: float
    floor_pad_v_m: float
    ground_plane_z_m: float
    sleeve_bore_clearance_m: float
    hinge_axis_z_m: float

    # --- candidate-local geometry ----------------------------------------
    upper_rail_height_m: float
    lower_rail_height_m: float
    cross_brace_count: int
    web_height_m: float
    top_flange_h_m: float
    bottom_flange_h_m: float
    flange_width_m: float
    crossmember_count: int
    crossmember_h_m: float
    crossmember_w_m: float
    scissor_bays: int
    chord_height_m: float
    chord_width_m: float
    scissor_bar_thickness_m: float
    scissor_bar_width_m: float
    scissor_height_m: float
    arc_radius_m: float
    arc_angle_rad: float
    arc_path_samples: int
    corner_plate_inset_m: float
    corner_plate_h_m: float
    corner_plate_t_m: float
    leg_outer_m: float
    leg_wall_m: float
    sleeve_outer_r_m: float
    sleeve_wall_m: float
    inner_tube_r_m: float
    inner_tube_length_m: float
    collar_r_m: float
    fold_upper_rad: float
    hinge_lug_half_gap_m: float
    hinge_lug_h_m: float
    foot_stance_y_m: float
    scissor_arm_thickness_m: float
    scissor_arm_width_m: float
    pivot_bolt_r_m: float
    scissor_cross_z_m: float
    member_scale: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    if high < low:
        high = low
    return max(low, min(high, float(value)))


def _pick(rng: random.Random, bounds: tuple[float, float], digits: int = 4) -> float:
    return round(rng.uniform(bounds[0], bounds[1]), digits)


def config_from_seed(seed: int) -> RollerConveyorConfig:
    """Sample one legal combination.  Seed 0 reproduces source origin 002."""

    if seed == 0:
        return RollerConveyorConfig()
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x0611_2026)
    frame = choices["frame_form"]
    support = choices["support_form"]
    roller = choices["roller_form"]
    frame_ranges = _FRAME_RANGES[frame]
    support_ranges = _SUPPORT_RANGES[support]
    roller_ranges = _ROLLER_RANGES[roller]

    def frame_value(name: str, default: float) -> float:
        bounds = frame_ranges.get(name)
        return _pick(rng, bounds) if bounds else default

    def support_value(name: str, default: float) -> float:
        bounds = support_ranges.get(name)
        return _pick(rng, bounds) if bounds else default

    def roller_value(name: str, default: float) -> float:
        bounds = roller_ranges.get(name)
        return _pick(rng, bounds, 5) if bounds else default

    base = RollerConveyorConfig()
    return replace(
        base,
        frame_form=frame,
        support_form=support,
        roller_form=roller,
        roller_layout=choices["roller_layout"],
        roller_count=choices["roller_count"],
        frame_outer_width_m=frame_value("frame_outer_width_m", base.frame_outer_width_m),
        rail_thickness_m=frame_value("rail_thickness_m", base.rail_thickness_m),
        bed_height_m=frame_value("bed_height_m", base.bed_height_m),
        roller_pitch_m=frame_value("roller_pitch_m", base.roller_pitch_m),
        end_inset_m=frame_value("end_inset_m", base.end_inset_m),
        upper_rail_height_m=frame_value("upper_rail_height_m", base.upper_rail_height_m),
        lower_rail_height_m=frame_value("lower_rail_height_m", base.lower_rail_height_m),
        rail_top_above_crown_m=frame_value(
            "rail_top_above_crown_m", base.rail_top_above_crown_m
        ),
        frame_length_authored_m=frame_value(
            "frame_length_authored_m", base.frame_length_authored_m
        ),
        web_height_m=frame_value("web_height_m", base.web_height_m),
        top_flange_h_m=frame_value("top_flange_h_m", base.top_flange_h_m),
        bottom_flange_h_m=frame_value("bottom_flange_h_m", base.bottom_flange_h_m),
        flange_width_m=frame_value("flange_width_m", base.flange_width_m),
        chord_height_m=frame_value("chord_height_m", base.chord_height_m),
        chord_width_m=frame_value("chord_width_m", base.chord_width_m),
        bottom_chord_z_m=frame_value("bottom_chord_z_m", base.bottom_chord_z_m),
        scissor_bar_thickness_m=frame_value(
            "scissor_bar_thickness_m", base.scissor_bar_thickness_m
        ),
        arc_radius_m=frame_value("arc_radius_m", base.arc_radius_m),
        arc_angle_rad=frame_value("arc_angle_rad", base.arc_angle_rad),
        cross_brace_count=rng.choice(_FRAME_CHOICES[frame].get("cross_brace_count", (2,))),
        crossmember_count=rng.choice(_FRAME_CHOICES[frame].get("crossmember_count", (7,))),
        scissor_bays=rng.choice(_FRAME_CHOICES[frame].get("scissor_bays", (3,))),
        arc_path_samples=rng.choice(_FRAME_CHOICES[frame].get("arc_path_samples", (48,))),
        leg_station_count=rng.choice(_LEG_STATION_CHOICES),
        corner_plate_inset_m=support_value(
            "corner_plate_inset_m", base.corner_plate_inset_m
        ),
        corner_plate_h_m=support_value("corner_plate_h_m", base.corner_plate_h_m),
        corner_plate_t_m=support_value("corner_plate_t_m", base.corner_plate_t_m),
        foot_pad_l_m=support_value("foot_pad_l_m", base.foot_pad_l_m),
        foot_pad_w_m=support_value("foot_pad_w_m", base.foot_pad_w_m),
        foot_pad_r_m=support_value("foot_pad_r_m", base.foot_pad_r_m),
        foot_pad_h_m=support_value("foot_pad_h_m", base.foot_pad_h_m),
        leg_outer_m=support_value("leg_outer_m", base.leg_outer_m),
        leg_wall_m=support_value("leg_wall_m", base.leg_wall_m),
        leg_height_m=support_value("leg_height_m", base.leg_height_m),
        foot_travel_m=support_value("foot_travel_m", base.foot_travel_m),
        foot_stem_r_m=support_value("foot_stem_r_m", base.foot_stem_r_m),
        foot_stem_length_m=support_value("foot_stem_length_m", base.foot_stem_length_m),
        sleeve_wall_m=support_value("sleeve_wall_m", base.sleeve_wall_m),
        inner_tube_r_m=support_value("inner_tube_r_m", base.inner_tube_r_m),
        inner_tube_length_m=support_value("inner_tube_length_m", base.inner_tube_length_m),
        collar_r_m=support_value("collar_r_m", base.collar_r_m),
        fold_upper_rad=support_value("fold_upper_rad", base.fold_upper_rad),
        hinge_lug_half_gap_m=support_value(
            "hinge_lug_half_gap_m", base.hinge_lug_half_gap_m
        ),
        hinge_lug_h_m=support_value("hinge_lug_h_m", base.hinge_lug_h_m),
        foot_stance_y_m=support_value("foot_stance_y_m", base.foot_stance_y_m),
        scissor_arm_thickness_m=support_value(
            "scissor_arm_thickness_m", base.scissor_arm_thickness_m
        ),
        scissor_arm_width_m=support_value(
            "scissor_arm_width_m", base.scissor_arm_width_m
        ),
        pivot_bolt_r_m=support_value("pivot_bolt_r_m", base.pivot_bolt_r_m),
        scissor_top_z_m=support_value("scissor_top_z_m", base.scissor_top_z_m),
        # `sleeve_outer_r_m` is declared by telescoping_sleeve_legs and by
        # split_twin_half_roller; sample from whichever candidate is active and
        # let resolve_config clamp it for the other reader.
        sleeve_outer_r_m=(
            _pick(rng, support_ranges["sleeve_outer_r_m"])
            if "sleeve_outer_r_m" in support_ranges
            else roller_value("sleeve_outer_r_m", base.sleeve_outer_r_m)
        ),
        roller_radius_m=roller_value("roller_radius_m", base.roller_radius_m),
        roller_length_m=roller_value("roller_length_m", base.roller_length_m),
        axle_r_m=roller_value("axle_r_m", base.axle_r_m),
        axle_overhang_m=roller_value("axle_overhang_m", base.axle_overhang_m),
        end_cap_r_m=roller_value("end_cap_r_m", base.end_cap_r_m),
        end_cap_length_m=roller_value("end_cap_length_m", base.end_cap_length_m),
        end_cap_inset_m=roller_value("end_cap_inset_m", base.end_cap_inset_m),
        running_clearance_m=roller_value("running_clearance_m", base.running_clearance_m),
        highlight_strip_w_m=roller_value(
            "highlight_strip_w_m", base.highlight_strip_w_m
        ),
        highlight_proud_m=roller_value("highlight_proud_m", base.highlight_proud_m),
        split_gap_m=roller_value("split_gap_m", base.split_gap_m),
        sleeve_bore_r_m=roller_value("sleeve_bore_r_m", base.sleeve_bore_r_m),
        stagger_offset_m=_pick(rng, _STAGGER_RANGE),
    )


def _slot_range(table: dict[str, dict[str, tuple[float, float]]], candidate: str, name: str):
    return table[candidate].get(name)


def resolve_config(config: RollerConveyorConfig) -> ResolvedRollerConveyorConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "frame_form": config.frame_form,
            "support_form": config.support_form,
            "roller_form": config.roller_form,
            "roller_layout": config.roller_layout,
            "roller_count": config.roller_count,
        }
    )
    frame_form = config.frame_form
    support_form = config.support_form
    roller_form = config.roller_form
    roller_layout = config.roller_layout
    count = int(config.roller_count)

    frame_ranges = _FRAME_RANGES[frame_form]
    support_ranges = _SUPPORT_RANGES[support_form]
    roller_ranges = _ROLLER_RANGES[roller_form]

    def fclamp(name: str, value: float) -> float:
        bounds = frame_ranges.get(name)
        return _clamp(value, *bounds) if bounds else float(value)

    def sclamp(name: str, value: float) -> float:
        bounds = support_ranges.get(name)
        return _clamp(value, *bounds) if bounds else float(value)

    def rclamp(name: str, value: float) -> float:
        bounds = roller_ranges.get(name)
        return _clamp(value, *bounds) if bounds else float(value)

    def choice(name: str, table: dict[str, tuple[int, ...]], value: int, fallback: int) -> int:
        allowed = table.get(name)
        if not allowed:
            return fallback
        return int(value) if int(value) in allowed else allowed[len(allowed) // 2]

    # --- rail datum: the whole axial chain hangs off rail_inner_y ----------
    frame_outer_width = fclamp("frame_outer_width_m", config.frame_outer_width_m)
    rail_thickness = fclamp("rail_thickness_m", config.rail_thickness_m)
    rail_centre_y = frame_outer_width / 2.0 - rail_thickness / 2.0
    rail_inner_y = rail_centre_y - rail_thickness / 2.0
    member_scale = _clamp(frame_outer_width / 0.915, 0.55, 1.30)

    # --- binding count_to_station_rule: which frame-length strategy --------
    # Derived, never commented: Mode A is the 001 family (fixed pitch, grow the
    # frame), Mode B is 002 (fixed frame, spread the pitch, because it carries
    # fixed leg stations), Mode C is the arc (length = radius * angle).
    if frame_form in ("low_profile_extrusion_deck", "pantograph_scissor_chords"):
        frame_length_mode = "A"
    elif frame_form == "swept_curved_arc":
        frame_length_mode = "C"
    else:
        frame_length_mode = "B"

    roller_pitch = fclamp("roller_pitch_m", config.roller_pitch_m)
    end_inset = fclamp("end_inset_m", config.end_inset_m)
    frame_length_authored = fclamp(
        "frame_length_authored_m", config.frame_length_authored_m
    )
    arc_radius = fclamp("arc_radius_m", config.arc_radius_m)
    arc_angle = fclamp("arc_angle_rad", config.arc_angle_rad)
    min_station_pitch = 0.055

    if frame_length_mode == "A":
        # 001 family: FRAME_LENGTH = (N-1)*pitch + 2*end_inset, exact at
        # 4*0.070+0.190=0.470 (N=5), 7*0.070+0.190=0.680 (N=8), 17*0.070+0.190=1.380.
        frame_length = (count - 1) * roller_pitch + 2.0 * end_inset
        station_pitch = roller_pitch
    elif frame_length_mode == "C":
        # The curved fork spreads stations across the FULL arc with ZERO end
        # inset (source L41-L44), so pitch = arc_length/(N-1) and the arc must be
        # long enough to hold N stations at the minimum pitch.
        required_length = (count - 1) * min_station_pitch
        arc_radius = max(arc_radius, required_length / _FRAME_RANGES[frame_form]["arc_angle_rad"][1])
        arc_angle = _clamp(
            max(arc_angle, required_length / arc_radius),
            *_FRAME_RANGES[frame_form]["arc_angle_rad"],
        )
        frame_length = arc_radius * arc_angle
        station_pitch = frame_length / (count - 1)
    else:
        # 002: var_roller_count_12 changes ONLY N and pitch, leaving
        # FRAME_LENGTH = 2.400 alone; 2.280/24 = 0.095 and 2.280/12 = 0.190.
        frame_length = frame_length_authored
        station_pitch = (frame_length - 0.120) / count
    station_span = (count - 1) * station_pitch

    # --- layout: one helper feeds the fixed bearings AND the joint origins --
    stagger_offset = (
        _clamp(config.stagger_offset_m, *_STAGGER_RANGE)
        if roller_layout == "staggered_alternating_height"
        else 0.0
    )
    centre_distance = math.hypot(station_pitch, stagger_offset)

    # --- roller: the pitch-clearance rule is a hard per-config constraint ---
    roller_radius = rclamp("roller_radius_m", config.roller_radius_m)
    roller_radius = max(0.008, min(roller_radius, (centre_distance - _MIN_ROLLER_GAP - 0.0005) / 2.0))
    roller_gap = centre_distance - 2.0 * roller_radius
    running_clearance = rclamp("running_clearance_m", config.running_clearance_m)
    end_cap_length = rclamp("end_cap_length_m", config.end_cap_length_m)
    end_cap_inset = min(
        rclamp("end_cap_inset_m", config.end_cap_inset_m),
        rclamp("end_cap_length_m", config.end_cap_length_m) / 2.0 - 0.0008,
    )
    end_cap_r = min(rclamp("end_cap_r_m", config.end_cap_r_m), roller_radius - 0.0005)
    cap_reach = max(0.0, end_cap_inset + end_cap_length / 2.0)
    max_half_length = rail_inner_y - _MIN_BARREL_CLEARANCE - cap_reach
    roller_half_length = _clamp(
        rclamp("roller_length_m", config.roller_length_m) / 2.0, 0.05, max(0.05, max_half_length)
    )
    roller_length = 2.0 * roller_half_length
    # The axle end must clear the end cap axially (otherwise a wide cap and a
    # short overhang would drive the cap into the fixed bearing insert) and must
    # still leave a real insert between itself and the rail.
    axle_overhang = _clamp(
        rclamp("axle_overhang_m", config.axle_overhang_m),
        cap_reach + running_clearance + 0.001,
        max(
            cap_reach + running_clearance + 0.0015,
            rail_inner_y - roller_half_length - running_clearance - _MIN_BEARING_INSERT,
        ),
    )
    axle_half_length = roller_half_length + axle_overhang
    axle_r = rclamp("axle_r_m", config.axle_r_m)
    barrel_axial_clearance = rail_inner_y - roller_half_length
    end_cap_axial_clearance = rail_inner_y - (roller_half_length + cap_reach)

    # --- rail section per candidate, and the rail-vs-crown flip ------------
    upper_rail_height = fclamp("upper_rail_height_m", config.upper_rail_height_m)
    lower_rail_height = fclamp("lower_rail_height_m", config.lower_rail_height_m)
    web_height = fclamp("web_height_m", config.web_height_m)
    top_flange_h = fclamp("top_flange_h_m", config.top_flange_h_m)
    bottom_flange_h = fclamp("bottom_flange_h_m", config.bottom_flange_h_m)
    flange_width = max(fclamp("flange_width_m", config.flange_width_m), rail_thickness + 0.004)
    chord_height = fclamp("chord_height_m", config.chord_height_m)
    chord_width = fclamp("chord_width_m", config.chord_width_m)
    scissor_bar_thickness = fclamp("scissor_bar_thickness_m", config.scissor_bar_thickness_m)

    if frame_form in ("deep_channel_rail_bed", "swept_curved_arc"):
        rail_stack_height = top_flange_h + web_height + bottom_flange_h
        bearing_host_offset = top_flange_h
        bearing_host_height = web_height
    elif frame_form == "pantograph_scissor_chords":
        rail_stack_height = chord_height
        bearing_host_offset = 0.0
        bearing_host_height = chord_height
    else:
        rail_stack_height = upper_rail_height + lower_rail_height
        bearing_host_offset = 0.0
        bearing_host_height = upper_rail_height

    bed_plane_z_raw = config.bed_height_m + roller_radius
    # The bearing insert welds into a real rail member, so the roller axis must
    # lie inside that member's vertical band.  This is what keeps the insert
    # attached to the frame at every sampled proportion.
    rtac_low = bearing_host_offset + _BEARING_HOST_MARGIN - roller_radius
    rtac_high = bearing_host_offset + bearing_host_height - _BEARING_HOST_MARGIN - roller_radius
    if bearing_host_offset > 0.0:
        # The 002 family's top flange is WIDER than its web, so it reaches inboard
        # of rail_inner_y and over the bed.  It must therefore sit clear above the
        # highest roller crown, staggered stations included.
        rtac_low = max(rtac_low, bearing_host_offset + 0.004 + stagger_offset)
    rail_top_above_crown = _clamp(
        fclamp("rail_top_above_crown_m", config.rail_top_above_crown_m), rtac_low, rtac_high
    )

    # A staggered station lifts its axis, and its bearing insert has to stay
    # welded into the same rail member: the HIGH level must not climb out of the
    # host band.  var_roller_layout_staggered_rollers keeps 0.025 inside a 0.150
    # web; a thin extrusion or chord cannot host that much, so the stagger is
    # derived against the host band and the roller radius is then re-derived
    # against the new centre distance (which only ever shrinks).
    if stagger_offset > 0.0:
        stagger_ceiling = (
            roller_radius + rail_top_above_crown - bearing_host_offset - _BEARING_HOST_MARGIN
        )
        stagger_offset = _clamp(stagger_offset, 0.004, max(0.004, stagger_ceiling))
        centre_distance = math.hypot(station_pitch, stagger_offset)
        shrunk_radius = max(
            0.008, min(roller_radius, (centre_distance - _MIN_ROLLER_GAP - 0.0005) / 2.0)
        )
        if shrunk_radius < roller_radius:
            # Keep the axis inside the band after the radius moves.
            rail_top_above_crown += roller_radius - shrunk_radius
            end_cap_r = min(end_cap_r, shrunk_radius - 0.0005)
            roller_radius = shrunk_radius
        roller_gap = centre_distance - 2.0 * roller_radius

    foot_pad_h = sclamp("foot_pad_h_m", config.foot_pad_h_m)
    foot_travel_raw = sclamp("foot_travel_m", config.foot_travel_m)
    if support_form == "fixed_corner_plate_feet":
        min_support_room = foot_pad_h + 0.030
    else:
        min_support_room = foot_pad_h + foot_travel_raw + _MIN_STEM_RETENTION + 0.045
        if support_form == "folding_hinged_legs":
            min_support_room += 0.060
    min_mount_z = min_support_room + 0.080

    # Raise the bed rather than letting the rail underside sink below the floor.
    bed_height = _clamp(
        max(
            fclamp("bed_height_m", config.bed_height_m),
            min_mount_z + rail_stack_height - rail_top_above_crown - roller_radius,
        ),
        *frame_ranges.get("bed_height_m", (0.170, 4.000)),
    )
    bed_height = max(
        bed_height, min_mount_z + rail_stack_height - rail_top_above_crown - roller_radius
    )
    bed_plane_z = bed_height + roller_radius
    rail_top_z = bed_plane_z + rail_top_above_crown
    rail_guard_height = max(0.0, rail_top_above_crown)
    support_mount_z = rail_top_z - rail_stack_height
    bed_clear_width = 2.0 * rail_inner_y
    roller_containment_margin = end_cap_axial_clearance

    # --- under-bed band and the plane the support slot attaches to ---------
    crossmember_count = choice(
        "crossmember_count", _FRAME_CHOICES[frame_form], config.crossmember_count, 7
    )
    cross_brace_count = choice(
        "cross_brace_count", _FRAME_CHOICES[frame_form], config.cross_brace_count, 2
    )
    scissor_bays = choice("scissor_bays", _FRAME_CHOICES[frame_form], config.scissor_bays, 3)
    arc_path_samples = choice(
        "arc_path_samples", _FRAME_CHOICES[frame_form], config.arc_path_samples, 48
    )
    crossmember_w = _clamp(0.055 * member_scale, 0.030, 0.090)

    if frame_form in ("deep_channel_rail_bed", "swept_curved_arc"):
        # 002 hangs its ladder below the rail underside (0.640..0.700) and the
        # legs abut its bottom face, which is also where the fold hinge sits.
        crossmember_h = _clamp(
            0.060 * member_scale, 0.020, max(0.020, support_mount_z - min_support_room)
        )
        under_bed_drop = crossmember_h
    elif frame_form == "pantograph_scissor_chords":
        crossmember_h = chord_height
        # The source authors an absolute floor height (L35: 0.030 under a 0.202
        # top chord).  bed_height_m is independent here and the support slot
        # needs its own room underneath, so the same number is re-expressed as
        # the pantograph's SHARE of the height between the support's minimum
        # room and the top chord.  0.030 lands mid-range, as in the source.
        depth_lo, depth_hi = frame_ranges["bottom_chord_z_m"]
        share = _clamp(
            (fclamp("bottom_chord_z_m", config.bottom_chord_z_m) - depth_lo)
            / max(1e-9, depth_hi - depth_lo),
            0.0,
            1.0,
        )
        head_room = max(0.0, support_mount_z - 0.050 - min_support_room)
        pantograph_bottom_z = min_support_room + share * head_room
        under_bed_drop = max(0.0, support_mount_z - pantograph_bottom_z)
    else:
        # 001's end crossmembers and braces sit between the rails, above the
        # rail underside, so nothing hangs into the support slot's space.
        crossmember_h = _clamp(
            0.055 * member_scale,
            0.015,
            max(0.015, (bed_height - roller_radius) - support_mount_z - 0.005),
        )
        under_bed_drop = 0.0
    leg_head_z = support_mount_z - under_bed_drop

    # --- welds: scale-aware named overlaps, MECHANICAL_PRIORS 1c -----------
    structural_weld = min(0.0010, max(0.0003, frame_length * 0.00025))
    fitting_weld = max(0.0002, structural_weld * 0.6)
    leg_head_engagement_z = leg_head_z + structural_weld

    # --- the central derivation: the insert is a solved gap ----------------
    # outer end welded INTO the rail (intra-part), inner end holding a running
    # clearance off the rotating axle (inter-part running fit).
    bearing_insert_length = max(
        _MIN_BEARING_INSERT,
        rail_inner_y + fitting_weld - axle_half_length - running_clearance,
    )
    bearing_inner_face_y = rail_inner_y + fitting_weld - bearing_insert_length
    bearing_bore_r = axle_r + running_clearance + 0.0015
    bearing_outer_r = bearing_bore_r + _BEARING_WALL * member_scale

    # --- split roller: a real bore replaces 24 unscoped allowances ---------
    split_gap = rclamp("split_gap_m", config.split_gap_m)
    split_gap = _clamp(split_gap, 0.010, max(0.012, roller_length * 0.35))
    sleeve_bore_r = max(
        rclamp("sleeve_bore_r_m", config.sleeve_bore_r_m), axle_r + running_clearance + 0.0010
    )
    split_sleeve_outer_r = _clamp(
        config.sleeve_outer_r_m, sleeve_bore_r + 0.004, max(sleeve_bore_r + 0.005, roller_radius - 0.001)
    )
    split_sleeve_bore_clearance = (
        sleeve_bore_r - axle_r - running_clearance
        if roller_form == "split_twin_half_roller"
        else 0.0
    )
    highlight_strip_w = rclamp("highlight_strip_w_m", config.highlight_strip_w_m)
    highlight_proud = rclamp("highlight_proud_m", config.highlight_proud_m)

    # --- support geometry --------------------------------------------------
    leg_station_count = (
        int(config.leg_station_count)
        if int(config.leg_station_count) in _LEG_STATION_CHOICES
        else 3
    )
    foot_pad_r = sclamp("foot_pad_r_m", config.foot_pad_r_m)
    foot_pad_l = sclamp("foot_pad_l_m", config.foot_pad_l_m)
    foot_pad_w = sclamp("foot_pad_w_m", config.foot_pad_w_m)
    leg_outer = sclamp("leg_outer_m", config.leg_outer_m)
    leg_wall = min(sclamp("leg_wall_m", config.leg_wall_m), leg_outer * 0.18)
    inner_tube_r = max(0.006, sclamp("inner_tube_r_m", config.inner_tube_r_m))
    sleeve_wall = min(
        sclamp("sleeve_wall_m", config.sleeve_wall_m),
        sclamp("sleeve_outer_r_m", config.sleeve_outer_r_m) * 0.30,
    )
    # A bigger inner tube needs a bigger sleeve, not a truncated tube: the bore
    # is `sleeve_outer - wall` and must clear the tube by a running clearance.
    sleeve_outer_r = max(
        sclamp("sleeve_outer_r_m", config.sleeve_outer_r_m),
        inner_tube_r + sleeve_wall + 0.0015,
    )
    collar_r = max(sclamp("collar_r_m", config.collar_r_m), sleeve_outer_r + 0.003)
    sleeve_bore_clearance = (sleeve_outer_r - sleeve_wall) - inner_tube_r
    foot_stance_y = max(sclamp("foot_stance_y_m", config.foot_stance_y_m), rail_centre_y + 0.030)
    scissor_arm_thickness = sclamp("scissor_arm_thickness_m", config.scissor_arm_thickness_m)
    scissor_arm_width = sclamp("scissor_arm_width_m", config.scissor_arm_width_m)
    pivot_bolt_r = sclamp("pivot_bolt_r_m", config.pivot_bolt_r_m)
    # The source straddles the tube from INSIDE (lugs at +-0.024 on a 0.060
    # tube), which puts frame geometry inside the leg part.  The rebuild moves
    # the lugs outboard of the tube and reads the parameter as the clear offset
    # beyond the tube face, so the clevis interleaves instead of intersecting.
    lug_bounds = _SUPPORT_RANGES["folding_hinged_legs"]["hinge_lug_half_gap_m"]
    hinge_lug_half_gap = (
        leg_outer / 2.0
        + max(0.004, 0.006 * member_scale)
        + 0.002
        + (sclamp("hinge_lug_half_gap_m", config.hinge_lug_half_gap_m) - lug_bounds[0])
    )
    hinge_lug_h = sclamp("hinge_lug_h_m", config.hinge_lug_h_m)

    max_drop = leg_head_z - foot_pad_h - 0.020
    if support_form == "scissor_crossed_base":
        # Source L33 SCISSOR_RAIL_Z = 0.640 is where the arms meet the frame,
        # which here is `leg_head_z` and therefore already derived.  The
        # parameter is read as the arm RISE, mapped onto the height the frame
        # actually offers so it stays a live dimension at every bed height.
        rise_lo, rise_hi = _SUPPORT_RANGES[support_form]["scissor_top_z_m"]
        share = _clamp(
            (sclamp("scissor_top_z_m", config.scissor_top_z_m) - rise_lo)
            / max(1e-9, rise_hi - rise_lo),
            0.0,
            1.0,
        )
        support_drop = 0.040 + share * max(0.0, max(0.040, max_drop) - 0.040)
    else:
        support_drop = _clamp(
            sclamp("leg_height_m", config.leg_height_m), 0.040, max(0.040, max_drop)
        )
    leg_bottom_z = leg_head_z - support_drop

    stem_local_offset = 0.050 if support_form == "telescoping_sleeve_legs" else -0.0175
    if support_form == "telescoping_sleeve_legs":
        sliding_member_length = sclamp("inner_tube_length_m", config.inner_tube_length_m)
        sliding_member_r = inner_tube_r
    elif support_form == "fixed_corner_plate_feet":
        sliding_member_length = 0.0
        sliding_member_r = 0.0
    else:
        sliding_member_length = sclamp("foot_stem_length_m", config.foot_stem_length_m)
        sliding_member_r = min(
            sclamp("foot_stem_r_m", config.foot_stem_r_m), leg_outer / 2.0 - leg_wall - 0.002
        )
        sliding_member_r = max(0.004, sliding_member_r)
    # Retention is the invariant, not the authored length: 002 L460-L467 asserts
    # 0.025 m of stem still inside the leg at FULL extension.
    stem_top_local = _clamp(
        sliding_member_length / 2.0 + stem_local_offset,
        _MIN_STEM_RETENTION + 0.004,
        max(_MIN_STEM_RETENTION + 0.004, support_drop - 0.005),
    )
    if support_form == "fixed_corner_plate_feet":
        foot_travel = 0.0
        stem_insertion_min = 0.0
    else:
        foot_travel = _clamp(foot_travel_raw, 0.004, max(0.004, stem_top_local - _MIN_STEM_RETENTION))
        stem_insertion_min = stem_top_local - foot_travel

    inner_tube_length = (
        sliding_member_length
        if support_form == "telescoping_sleeve_legs"
        else sclamp("inner_tube_length_m", config.inner_tube_length_m)
    )

    fold_upper = sclamp("fold_upper_rad", config.fold_upper_rad)
    leg_span = min(
        0.75 * frame_length, frame_length - max(leg_outer, 2.0 * collar_r) - 0.020
    )
    leg_span = max(0.0, leg_span)
    if support_form == "folding_hinged_legs" and leg_station_count > 2:
        # Host capacity: a folding leg needs a bay it can lie down in.  With
        # three stations the middle leg always folds toward a neighbour, so a
        # frame that cannot give it that bay carries two stations instead.
        required_bay = (
            (support_drop + foot_pad_h) * math.sin(fold_upper) + 2.0 * foot_pad_r + 0.010
        )
        if leg_span / (leg_station_count - 1) < required_bay:
            leg_station_count = 2
    leg_station_gap = leg_span / max(1, leg_station_count - 1)
    # Neighbouring floor pads have to stay apart: along the frame at the station
    # gap, and across it at the stance the support candidate actually uses.
    foot_pad_r = min(
        foot_pad_r,
        max(0.012, (leg_station_gap - 0.008) / 2.0),
        max(0.012, leg_station_y_span := (
            foot_stance_y if support_form == "scissor_crossed_base" else rail_centre_y
        ) - 0.004),
    )
    if support_form == "folding_hinged_legs":
        # Legs fold OUTWARD from the frame centre so neighbouring stations open
        # away from each other; where the bay is still too short for the leg to
        # lie down, the hinge range is derived from the real clearance instead
        # of from the authored limit.  (The source fixes one fold direction and
        # a 0.9 m bay, which never conflicts at its own scale.)
        swept_reach = support_drop + foot_pad_h
        clear = max(0.0, leg_station_gap - leg_outer / 2.0 - 2.0 * foot_pad_r - 0.010)
        if swept_reach > 1e-6 and clear < swept_reach:
            fold_upper = min(
                fold_upper, max(0.35, math.asin(_clamp(clear / swept_reach, 0.0, 1.0)))
            )
    # The hinge drops one bolt radius below the frame underside so the leg part,
    # INCLUDING the pivot pin that is now coaxial with the axis, stays entirely
    # clear of frame geometry through the whole fold.  The Design names this
    # plane `support_mount_z`; its own rationale names the crossmember underside
    # (source L33 HINGE_Z = 0.640 = leg top), which is `leg_head_z` here.
    hinge_pin_r = max(0.004, 0.006 * member_scale)
    fold_leaf_half = max(leg_outer, max(0.040, 0.070 * member_scale)) / 2.0
    if support_form == "folding_hinged_legs":
        # A leaf of half-extent R sweeps R*sin(q) ABOVE its own hinge, so the
        # hinge has to stand that far below the frame underside or the leaf digs
        # into the frame at full fold.  The source hides this behind an 80 mm lug
        # and a leaf that overlaps its own crossmember; deriving the standoff
        # from the real swept envelope is the MECHANICAL_PRIORS 4/7 answer.
        fixed_part = 1.5 * hinge_pin_r + 0.006 + structural_weld
        desired = fold_leaf_half * math.sin(fold_upper) + fixed_part
        budget = max(0.0, support_drop - 0.050)
        if desired > budget:
            sin_allow = _clamp(
                (budget - fixed_part) / max(1e-6, fold_leaf_half), 0.0, 1.0
            )
            fold_upper = max(0.300, min(fold_upper, math.asin(sin_allow)))
            desired = fold_leaf_half * math.sin(fold_upper) + fixed_part
        hinge_standoff = min(desired, max(fixed_part, support_drop - 0.030))
    else:
        hinge_standoff = 0.0
    hinge_axis_z = leg_head_z - hinge_standoff
    leg_local_length = max(0.020, support_drop - hinge_standoff)
    hinge_lug_h = max(hinge_lug_h, hinge_standoff + 0.040)

    support_joint_topology = (
        "none"
        if support_form == "fixed_corner_plate_feet"
        else (
            "revolute_legs_prismatic_feet"
            if support_form == "folding_hinged_legs"
            else "prismatic_feet"
        )
    )
    foot_part_count = 0 if support_form == "fixed_corner_plate_feet" else 2 * leg_station_count
    folding_leg_part_count = (
        2 * leg_station_count if support_form == "folding_hinged_legs" else 0
    )
    leg_station_y = rail_centre_y if support_form != "scissor_crossed_base" else foot_stance_y
    if support_form in ("square_tube_legs_leveling_feet", "folding_hinged_legs"):
        leg_footprint_u = leg_outer
        leg_footprint_v = leg_outer
    elif support_form == "telescoping_sleeve_legs":
        leg_footprint_u = 2.0 * collar_r
        leg_footprint_v = 2.0 * collar_r
    elif support_form == "scissor_crossed_base":
        leg_footprint_u = scissor_arm_thickness
        leg_footprint_v = 2.0 * foot_stance_y
    else:
        leg_footprint_u = sclamp("corner_plate_t_m", config.corner_plate_t_m)
        leg_footprint_v = sclamp("corner_plate_h_m", config.corner_plate_h_m)
    floor_pad_u = 2.0 * foot_pad_r if support_form != "fixed_corner_plate_feet" else foot_pad_l
    floor_pad_v = 2.0 * foot_pad_r if support_form != "fixed_corner_plate_feet" else foot_pad_w

    corner_plate_inset = sclamp("corner_plate_inset_m", config.corner_plate_inset_m)
    corner_plate_t = sclamp("corner_plate_t_m", config.corner_plate_t_m)
    corner_plate_h = _clamp(
        sclamp("corner_plate_h_m", config.corner_plate_h_m),
        0.020,
        max(0.020, leg_head_z - foot_pad_h - 0.010),
    )

    # scissor crossing, derived rather than authored (source L82-L84)
    scissor_dy = foot_stance_y + rail_centre_y
    scissor_dz = max(0.010, leg_head_z - leg_bottom_z)
    t_cross = foot_stance_y / scissor_dy if scissor_dy > 1e-9 else 0.5
    scissor_cross_z = leg_bottom_z + t_cross * scissor_dz

    scissor_height = max(
        0.020, support_mount_z - chord_height - (leg_head_z + chord_height)
    ) if frame_form == "pantograph_scissor_chords" else 0.0
    if frame_form == "pantograph_scissor_chords":
        scissor_height = max(0.020, (support_mount_z) - (leg_head_z + chord_height))
    scissor_bar_width = _clamp(0.028 * member_scale, 0.010, max(0.012, scissor_height * 0.45))

    # --- derived frame features that must re-derive with N -----------------
    frame_end_crossmember_x = min(
        station_span / 2.0 + 0.070 * member_scale, frame_length / 2.0 - crossmember_w / 2.0
    )
    frame_corner_plate_x = frame_length / 2.0 - (
        corner_plate_inset if support_form == "fixed_corner_plate_feet" else 0.015
    )
    frame_groove_length = max(0.050, frame_length - 0.070)
    frame_cross_brace_x = frame_length / 4.0

    return ResolvedRollerConveyorConfig(
        frame_form=frame_form,
        support_form=support_form,
        roller_form=roller_form,
        roller_layout=roller_layout,
        roller_count=count,
        frame_length_mode=frame_length_mode,
        frame_length_m=frame_length,
        station_pitch_m=station_pitch,
        station_span_m=station_span,
        frame_end_crossmember_x_m=frame_end_crossmember_x,
        frame_corner_plate_x_m=frame_corner_plate_x,
        frame_groove_length_m=frame_groove_length,
        frame_cross_brace_x_m=frame_cross_brace_x,
        roller_gap_m=roller_gap,
        frame_outer_width_m=frame_outer_width,
        rail_thickness_m=rail_thickness,
        rail_centre_y_m=rail_centre_y,
        rail_inner_y_m=rail_inner_y,
        roller_radius_m=roller_radius,
        roller_length_m=roller_length,
        roller_half_length_m=roller_half_length,
        axle_r_m=axle_r,
        axle_overhang_m=axle_overhang,
        axle_half_length_m=axle_half_length,
        end_cap_r_m=end_cap_r,
        end_cap_length_m=end_cap_length,
        end_cap_inset_m=end_cap_inset,
        running_clearance_m=running_clearance,
        barrel_axial_clearance_m=barrel_axial_clearance,
        end_cap_axial_clearance_m=end_cap_axial_clearance,
        structural_weld_embed_m=structural_weld,
        fitting_weld_embed_m=fitting_weld,
        interpart_connection_policy="none_all_joint_carried",
        bearing_insert_length_m=bearing_insert_length,
        bearing_inner_face_y_m=bearing_inner_face_y,
        bearing_bore_r_m=bearing_bore_r,
        bearing_outer_r_m=bearing_outer_r,
        roller_support_policy="allow_isolated_part",
        split_gap_m=split_gap,
        sleeve_bore_r_m=sleeve_bore_r,
        split_sleeve_bore_clearance_m=split_sleeve_bore_clearance,
        split_sleeve_outer_r_m=split_sleeve_outer_r,
        highlight_strip_w_m=highlight_strip_w,
        highlight_proud_m=highlight_proud,
        bed_height_m=bed_height,
        bed_plane_z_m=bed_plane_z,
        rail_top_above_crown_m=rail_top_above_crown,
        rail_top_z_m=rail_top_z,
        rail_guard_height_m=rail_guard_height,
        rail_stack_height_m=rail_stack_height,
        bed_clear_width_m=bed_clear_width,
        roller_containment_margin_m=roller_containment_margin,
        stagger_offset_m=stagger_offset,
        support_mount_z_m=support_mount_z,
        under_bed_drop_m=under_bed_drop,
        leg_head_z_m=leg_head_z,
        leg_head_engagement_z_m=leg_head_engagement_z,
        leg_station_count=leg_station_count,
        leg_station_span_m=leg_span,
        leg_station_y_m=leg_station_y,
        leg_footprint_u_m=leg_footprint_u,
        leg_footprint_v_m=leg_footprint_v,
        support_joint_topology=support_joint_topology,
        foot_part_count=foot_part_count,
        folding_leg_part_count=folding_leg_part_count,
        support_drop_m=support_drop,
        leg_local_length_m=leg_local_length,
        hinge_standoff_m=hinge_standoff,
        hinge_pin_r_m=hinge_pin_r,
        leg_bottom_z_m=leg_bottom_z,
        foot_joint_origin_z_m=(
            leg_bottom_z if support_form != "folding_hinged_legs" else -leg_local_length
        ),
        sliding_member_length_m=sliding_member_length,
        sliding_member_r_m=sliding_member_r,
        stem_local_offset_m=stem_local_offset,
        stem_top_local_m=stem_top_local,
        stem_insertion_min_m=stem_insertion_min,
        foot_travel_m=foot_travel,
        foot_pad_r_m=foot_pad_r,
        foot_pad_h_m=foot_pad_h,
        foot_pad_l_m=foot_pad_l,
        foot_pad_w_m=foot_pad_w,
        floor_pad_u_m=floor_pad_u,
        floor_pad_v_m=floor_pad_v,
        ground_plane_z_m=0.0,
        sleeve_bore_clearance_m=sleeve_bore_clearance,
        hinge_axis_z_m=hinge_axis_z,
        upper_rail_height_m=upper_rail_height,
        lower_rail_height_m=lower_rail_height,
        cross_brace_count=cross_brace_count,
        web_height_m=web_height,
        top_flange_h_m=top_flange_h,
        bottom_flange_h_m=bottom_flange_h,
        flange_width_m=flange_width,
        crossmember_count=crossmember_count,
        crossmember_h_m=crossmember_h,
        crossmember_w_m=crossmember_w,
        scissor_bays=scissor_bays,
        chord_height_m=chord_height,
        chord_width_m=chord_width,
        scissor_bar_thickness_m=scissor_bar_thickness,
        scissor_bar_width_m=scissor_bar_width,
        scissor_height_m=scissor_height,
        arc_radius_m=arc_radius,
        arc_angle_rad=arc_angle,
        arc_path_samples=arc_path_samples,
        corner_plate_inset_m=corner_plate_inset,
        corner_plate_h_m=corner_plate_h,
        corner_plate_t_m=corner_plate_t,
        leg_outer_m=leg_outer,
        leg_wall_m=leg_wall,
        sleeve_outer_r_m=sleeve_outer_r,
        sleeve_wall_m=sleeve_wall,
        inner_tube_r_m=inner_tube_r,
        inner_tube_length_m=inner_tube_length,
        collar_r_m=collar_r,
        fold_upper_rad=fold_upper,
        hinge_lug_half_gap_m=hinge_lug_half_gap,
        hinge_lug_h_m=hinge_lug_h,
        foot_stance_y_m=foot_stance_y,
        scissor_arm_thickness_m=scissor_arm_thickness,
        scissor_arm_width_m=scissor_arm_width,
        pivot_bolt_r_m=pivot_bolt_r,
        scissor_cross_z_m=scissor_cross_z,
        member_scale=member_scale,
        name=config.name,
    )


def slot_choices_for_config(r: ResolvedRollerConveyorConfig) -> dict[str, object]:
    return {
        "frame_form": r.frame_form,
        "support_form": r.support_form,
        "roller_form": r.roller_form,
        "roller_layout": r.roller_layout,
        "roller_count": r.roller_count,
    }


# --------------------------------------------------------------------------- #
# Placement helpers.  Straight frames are the identity; `swept_curved_arc` maps
# the local (tangent u, radial v) pair onto the arc, with `yaw = -delta` so a
# box's local Y lands on the radial direction (source L258-L283).
# --------------------------------------------------------------------------- #


def _is_arc(r: ResolvedRollerConveyorConfig) -> bool:
    return r.frame_form == "swept_curved_arc"


def _arc_xy(r: ResolvedRollerConveyorConfig, delta: float, radial: float = 0.0):
    radius = r.arc_radius_m + radial
    return (radius * math.sin(delta), -r.arc_radius_m + radius * math.cos(delta))


def _xy(r: ResolvedRollerConveyorConfig, u: float, v: float, delta: float = 0.0):
    """Local (along-path, radial) -> world (x, y)."""
    if not _is_arc(r):
        return (u, v)
    x, y = _arc_xy(r, delta, v)
    return (x + u * math.cos(delta), y - u * math.sin(delta))


def _yaw(r: ResolvedRollerConveyorConfig, delta: float) -> float:
    return -delta if _is_arc(r) else 0.0


def _station_delta(r: ResolvedRollerConveyorConfig, index: int) -> float:
    if not _is_arc(r) or r.roller_count < 2:
        return 0.0
    return -r.arc_angle_rad / 2.0 + index * r.arc_angle_rad / (r.roller_count - 1)


def _station_u(r: ResolvedRollerConveyorConfig, index: int) -> float:
    """THE index-general station rule, 001 L110-L113 / L222 and 002 L209/L234."""
    if _is_arc(r):
        return 0.0
    return (index - (r.roller_count - 1) / 2.0) * r.station_pitch_m


def _station_axis_z(r: ResolvedRollerConveyorConfig, index: int) -> float:
    """One helper feeds BOTH the fixed bearing inserts and the joint origins
    (var_roller_layout_staggered_rollers L36-L38, called at L224 and L250/L286)."""
    if r.roller_layout != "staggered_alternating_height":
        return r.bed_height_m
    return r.bed_height_m + (r.stagger_offset_m if index % 2 else 0.0)


def _leg_station_u(r: ResolvedRollerConveyorConfig, index: int) -> float:
    if r.leg_station_count < 2:
        return 0.0
    return (index - (r.leg_station_count - 1) / 2.0) * (
        r.leg_station_span_m / (r.leg_station_count - 1)
    )


def _leg_station_delta(r: ResolvedRollerConveyorConfig, index: int) -> float:
    if not _is_arc(r) or r.frame_length_m <= 1e-9:
        return 0.0
    return _leg_station_u(r, index) / r.arc_radius_m


def _leg_station_positions(r: ResolvedRollerConveyorConfig):
    """(index, station_delta, local_u) per support station."""
    return [
        (index, _leg_station_delta(r, index), 0.0 if _is_arc(r) else _leg_station_u(r, index))
        for index in range(r.leg_station_count)
    ]


def _box(part, size, *, u, v, z, delta=0.0, material, name, r):
    x, y = _xy(r, u, v, delta)
    part.visual(
        Box(size),
        origin=Origin(xyz=(x, y, z), rpy=(0.0, 0.0, _yaw(r, delta))),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _radial_cylinder(part, radius, length, *, u, v, z, delta=0.0, material, name, r):
    """Cylinder whose axis is the local radial direction (the roller spin axis)."""
    x, y = _xy(r, u, v, delta)
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=(x, y, z), rpy=(math.pi / 2.0, 0.0, math.pi - delta)),
        material=material,
        name=name, material_class_id="metal.steel_galvanized",
    )


def _bearing_ring_mesh(r: ResolvedRollerConveyorConfig):
    """Annular bearing face, authored hollow rather than as a solid disk.

    001 L32-L41 builds exactly this (outer 0.019, bore 0.0085 around a 0.006
    axle); the rebuild uses the annular construction for every frame candidate
    so `bearing_bore_r_m` is a real bore rather than a nominal number.
    """
    half = r.bearing_insert_length_m / 2.0
    profile = [
        (r.bearing_bore_r_m, -half),
        (r.bearing_outer_r_m, -half),
        (r.bearing_outer_r_m, half),
        (r.bearing_bore_r_m, half),
    ]
    return mesh_from_geometry(
        LatheGeometry(profile, segments=_LATHE_SEGMENTS),
        f"frame_form__{r.frame_form}__bearing_ring",
    )


def _add_bearing_inserts(frame, r: ResolvedRollerConveyorConfig, mats) -> None:
    """Fixed bearing insert at both ends of every station.

    The insert carries TWO interfaces with opposite signs: its outer end is
    welded INTO the rail by `fitting_weld_embed_m` (intra-part, free), and its
    inner end holds `running_clearance_m` off the rotating axle.  The length is
    not chosen, it is the solved gap:
    ``rail_inner_y + fitting_weld - axle_half_length - running_clearance``
    (002 L213: 0.3975 - 0.3825 = 0.015; 001 L36: 0.255 - 0.247 = 0.008).
    """
    solid_boss = r.roller_form == "split_twin_half_roller"
    ring = None if solid_boss else _bearing_ring_mesh(r)
    inner_face = r.bearing_inner_face_y_m
    centre = inner_face + r.bearing_insert_length_m / 2.0
    for index in range(r.roller_count):
        delta = _station_delta(r, index)
        u = _station_u(r, index)
        z = _station_axis_z(r, index)
        for side_index, side in enumerate((-1.0, 1.0)):
            x, y = _xy(r, u, side * centre, delta)
            frame.visual(
                Cylinder(radius=r.bearing_outer_r_m, length=r.bearing_insert_length_m)
                if solid_boss
                else ring,
                origin=Origin(
                    xyz=(x, y, z), rpy=(math.pi / 2.0, 0.0, math.pi - delta)
                ),
                material=mats["bearing"],
                name=f"frame_form__{r.frame_form}__bearing_{index}_{side_index}", material_class_id="metal.blackened_gunmetal",
            )


def _add_transverse_member(
    frame,
    r: ResolvedRollerConveyorConfig,
    mats,
    *,
    u: float,
    delta: float,
    z_centre: float,
    height: float,
    width: float,
    name: str,
    material_key: str = "frame",
) -> None:
    """Under-bed member spanning rail to rail, welded into both webs."""
    span = 2.0 * (r.rail_inner_y_m + r.fitting_weld_embed_m)
    _box(
        frame,
        (width, span, height),
        u=u,
        v=0.0,
        z=z_centre,
        delta=delta,
        material=mats[material_key],
        name=name,
        r=r,
    )


def _spread(count: int, span: float):
    if count <= 1:
        return [0.0]
    return [(-0.5 + index / (count - 1)) * span for index in range(count)]


# --------------------------------------------------------------------------- #
# Slot: frame_form
# --------------------------------------------------------------------------- #


def _frame_form_low_profile_extrusion_deck_build(frame, r, mats) -> None:
    """001 model.py:L44-L136 — low-profile aluminium extrusion deck.

    Twin side rails per side (upper 0.680x0.035x0.090 at z=0.170, lower
    0.680x0.028x0.035 at z=0.090), two end crossmembers, under-bed cross braces
    and four extrusion grooves.  The corner plates, feet and plate screws of
    L81-L95/L124-L136 belong to `fixed_corner_plate_feet`, not to the deck.
    """
    prefix = f"frame_form__{r.frame_form}"
    weld = r.structural_weld_embed_m
    for side_index, side in enumerate((-1.0, 1.0)):
        y = side * r.rail_centre_y_m
        _box(
            frame,
            (r.frame_length_m, r.rail_thickness_m, r.upper_rail_height_m),
            u=0.0,
            v=y,
            z=r.rail_top_z_m - r.upper_rail_height_m / 2.0,
            material=mats["frame"],
            name=f"{prefix}__upper_side_{side_index}",
            r=r,
        )
        # The two extrusions stack; the lower one is welded up into the upper so
        # the pair is one connected solid instead of an exactly tangent seam.
        _box(
            frame,
            (r.frame_length_m, r.rail_thickness_m, r.lower_rail_height_m + weld),
            u=0.0,
            v=y,
            z=r.support_mount_z_m + (r.lower_rail_height_m + weld) / 2.0,
            material=mats["frame"],
            name=f"{prefix}__lower_side_{side_index}",
            r=r,
        )
        for groove_index, fraction in enumerate((0.30, 0.62)):
            _box(
                frame,
                (r.frame_groove_length_m, 0.0016, 0.004),
                u=0.0,
                v=side * (r.rail_centre_y_m + r.rail_thickness_m / 2.0 - 0.0008),
                z=r.rail_top_z_m - r.upper_rail_height_m * fraction,
                material=mats["accent"],
                name=f"{prefix}__rail_groove_{side_index}_{groove_index}",
                r=r,
            )
    # End crossmembers support the first/last roller station:
    # x = ROLLER_SPAN_HALF + 0.070 (var_roller_count_5 L64-L72).
    for index, sign in enumerate((-1.0, 1.0)):
        _add_transverse_member(
            frame,
            r,
            mats,
            u=sign * r.frame_end_crossmember_x_m,
            delta=0.0,
            z_centre=r.support_mount_z_m + r.crossmember_h_m / 2.0,
            height=r.crossmember_h_m,
            width=r.crossmember_w_m,
            name=f"{prefix}__end_crossmember_{index}",
        )
    # Visible structural cross braces under the roller bed, spread over the
    # +-FRAME_LENGTH/4 band the three count forks agree on to within 3 percent.
    for index, u in enumerate(_spread(r.cross_brace_count, 2.0 * r.frame_cross_brace_x_m)):
        _add_transverse_member(
            frame,
            r,
            mats,
            u=u,
            delta=0.0,
            z_centre=r.support_mount_z_m + r.crossmember_h_m * 0.35,
            height=r.crossmember_h_m * 0.55,
            width=r.crossmember_w_m * 0.55,
            name=f"{prefix}__cross_brace_{index}",
        )


def _frame_form_deep_channel_rail_bed_build(frame, r, mats) -> None:
    """002 model.py:L139-L205 — three-piece channel per side plus the ladder.

    web 2.400x0.045x0.150 at z=0.790, top flange 2.400x0.075x0.025 at 0.8775,
    bottom flange 2.400x0.075x0.015 at 0.7075.  The source lands web top 0.865
    exactly on flange bottom 0.865; per 1c that exact tangency becomes a
    deliberate `structural_weld_embed_m`.
    """
    prefix = f"frame_form__{r.frame_form}"
    weld = r.structural_weld_embed_m
    for side_index, side in enumerate((-1.0, 1.0)):
        y = side * r.rail_centre_y_m
        _box(
            frame,
            (r.frame_length_m, r.flange_width_m, r.bottom_flange_h_m),
            u=0.0,
            v=y,
            z=r.support_mount_z_m + r.bottom_flange_h_m / 2.0,
            material=mats["frame"],
            name=f"{prefix}__bottom_flange_{side_index}",
            r=r,
        )
        _box(
            frame,
            (r.frame_length_m, r.rail_thickness_m, r.web_height_m + 2.0 * weld),
            u=0.0,
            v=y,
            z=r.support_mount_z_m + r.bottom_flange_h_m + r.web_height_m / 2.0,
            material=mats["frame"],
            name=f"{prefix}__side_web_{side_index}",
            r=r,
        )
        _box(
            frame,
            (r.frame_length_m, r.flange_width_m, r.top_flange_h_m),
            u=0.0,
            v=y,
            z=r.rail_top_z_m - r.top_flange_h_m / 2.0,
            material=mats["accent"],
            name=f"{prefix}__top_flange_{side_index}",
            r=r,
        )
    _add_under_bed_ladder(frame, r, mats, prefix)


def _add_under_bed_ladder(frame, r, mats, prefix: str) -> None:
    """002 L160-L168: under-bed crossmembers forming the visible blue ladder.

    They hang below the rail underside, welded up into the bottom flange, and
    their bottom face is the plane the support slot attaches to — which is also
    the fold hinge plane, so a folded leg can never reach frame geometry.
    """
    height = r.crossmember_h_m + r.structural_weld_embed_m
    z_centre = r.support_mount_z_m + r.structural_weld_embed_m - height / 2.0
    span = r.frame_length_m - r.crossmember_w_m - 0.020
    if _is_arc(r):
        half = r.arc_angle_rad / 2.0
        deltas = [
            -half + index * r.arc_angle_rad / max(1, r.crossmember_count - 1)
            for index in range(r.crossmember_count)
        ]
        deltas = [d * 0.96 for d in deltas]
        for index, delta in enumerate(deltas):
            x_in, y_in = _arc_xy(r, delta, -(r.rail_inner_y_m + r.fitting_weld_embed_m))
            x_out, y_out = _arc_xy(r, delta, r.rail_inner_y_m + r.fitting_weld_embed_m)
            length = math.hypot(x_out - x_in, y_out - y_in)
            frame.visual(
                Box((r.crossmember_w_m, length, height)),
                origin=Origin(
                    xyz=((x_in + x_out) / 2.0, (y_in + y_out) / 2.0, z_centre),
                    rpy=(0.0, 0.0, -delta),
                ),
                material=mats["frame"],
                name=f"{prefix}__crossmember_{index}", material_class_id="metal.paint_coated",
            )
        return
    for index, u in enumerate(_spread(r.crossmember_count, span)):
        _add_transverse_member(
            frame,
            r,
            mats,
            u=u,
            delta=0.0,
            z_centre=z_centre,
            height=height,
            width=r.crossmember_w_m,
            name=f"{prefix}__crossmember_{index}",
        )


def _frame_form_pantograph_scissor_chords_build(frame, r, mats) -> None:
    """var_frame_form_expanding_straight model.py:L63-L175 — pantograph deck.

    Top and bottom chord rails with SCISSOR_BAYS bays of crossed flat-bar
    diagonals and a pivot pin at every crossing.  Every dimension is derived
    (L36-L46): BAY_WIDTH = FRAME_LENGTH/bays, bar_length = sqrt(bay^2 + h^2),
    angle = atan2(h, bay).  The two diagonals of a bay genuinely intersect, and
    so do the pins — all on one part, so per 1c that costs nothing.

    SOURCE DEFECT 3 (L150): the source's pads bottom out at z = 0.015 rather
    than 0, so the object floats.  The rebuild moves grounding entirely into the
    support slot, which lands every candidate's floor contact on z = 0 exactly.
    """
    prefix = f"frame_form__{r.frame_form}"
    weld = r.structural_weld_embed_m
    top_z = r.rail_top_z_m - r.chord_height_m / 2.0
    bottom_z = r.leg_head_z_m + r.chord_height_m / 2.0
    for side_index, side in enumerate((-1.0, 1.0)):
        # The chord's inner face is the bearing weld datum, so it is placed off
        # rail_inner_y rather than off its own centreline.
        v = side * (r.rail_inner_y_m + r.chord_width_m / 2.0)
        for name, z in (("top_rail", top_z), ("bottom_rail", bottom_z)):
            _box(
                frame,
                (r.frame_length_m, r.chord_width_m, r.chord_height_m),
                u=0.0,
                v=v,
                z=z,
                material=mats["frame"],
                name=f"{prefix}__{name}_{side_index}",
                r=r,
            )
    bay_width = r.frame_length_m / r.scissor_bays
    height = max(0.010, r.scissor_height_m)
    bar_length = math.hypot(bay_width, height)
    bar_angle = math.atan2(height, bay_width)
    mid_z = (top_z - r.chord_height_m / 2.0 + bottom_z + r.chord_height_m / 2.0) / 2.0
    for bay in range(r.scissor_bays):
        u = -r.frame_length_m / 2.0 + bay_width / 2.0 + bay * bay_width
        for side_index, side in enumerate((-1.0, 1.0)):
            v = side * (r.rail_inner_y_m + r.chord_width_m / 2.0)
            for name, sign in (("scissor_rise", -1.0), ("scissor_fall", 1.0)):
                x, y = _xy(r, u, v)
                frame.visual(
                    Box((bar_length, r.scissor_bar_thickness_m, r.scissor_bar_width_m)),
                    origin=Origin(xyz=(x, y, mid_z), rpy=(0.0, sign * bar_angle, 0.0)),
                    material=mats["frame"],
                    name=f"{prefix}__{name}_{side_index}_{bay}", material_class_id="metal.paint_coated",
                )
            # Pivot pin at the crossing, coaxial with the pivot: the bars lie in
            # the XZ plane at fixed y, so the pin runs along Y.
            x, y = _xy(r, u, v)
            frame.visual(
                Cylinder(
                    radius=max(0.004, 0.008 * r.member_scale),
                    length=r.chord_width_m + 2.0 * weld + 0.008,
                ),
                origin=Origin(xyz=(x, y, mid_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["fastener"],
                name=f"{prefix}__pivot_pin_{side_index}_{bay}", material_class_id="metal.stainless_matte",
            )
    # Top crossmembers sit at the chord level, which is BELOW the roller crown in
    # this family, so the source puts them at the frame ends only "to avoid
    # roller paths" (L142).  The width is therefore derived from the free end
    # inset rather than authored: it is whatever fits outboard of the last
    # station plus the roller radius.
    free_inset = r.frame_length_m / 2.0 - r.station_span_m / 2.0
    # near face at L/2 - w must clear the last station by the roller radius:
    # end_inset - w >= roller_radius + clearance.
    top_member_w = min(r.crossmember_w_m, free_inset - r.roller_radius_m - 0.004)
    if top_member_w > 0.006:
        for index, sign in enumerate((-1.0, 1.0)):
            _add_transverse_member(
                frame,
                r,
                mats,
                u=sign * (r.frame_length_m / 2.0 - top_member_w / 2.0),
                delta=0.0,
                z_centre=top_z,
                height=r.chord_height_m,
                width=top_member_w,
                name=f"{prefix}__top_crossmember_{index}",
            )
    for index, u in enumerate(
        _spread(r.scissor_bays + 1, r.frame_length_m - r.crossmember_w_m)
    ):
        _add_transverse_member(
            frame,
            r,
            mats,
            u=u,
            delta=0.0,
            z_centre=bottom_z,
            height=r.chord_height_m,
            width=r.crossmember_w_m,
            name=f"{prefix}__bottom_crossmember_{index}",
        )


def _frame_form_swept_curved_arc_build(frame, r, mats) -> None:
    """var_frame_form_curved_arc model.py:L211-L283 — swept channel rails.

    The three channel pieces per side become `sweep_profile_along_spline`
    meshes over the arc path with 4-point rectangular profiles and
    `up_hint=(0,0,1)`; profile X is the horizontal radial width and profile Y is
    the vertical height (L76-L96).  Crossmembers stay boxes whose length is the
    true inner->outer chord and whose `yaw = -delta` aligns the box Y with the
    radial direction.
    """
    prefix = f"frame_form__{r.frame_form}"
    weld = r.structural_weld_embed_m
    samples = max(8, r.arc_path_samples)

    def path(radial: float, z: float):
        points = []
        for index in range(samples + 1):
            delta = -r.arc_angle_rad / 2.0 + index * r.arc_angle_rad / samples
            x, y = _arc_xy(r, delta, radial)
            points.append((x, y, z))
        return points

    def rect(width: float, height: float):
        half_w = width / 2.0
        half_h = height / 2.0
        return [(-half_w, -half_h), (half_w, -half_h), (half_w, half_h), (-half_w, half_h)]

    pieces = (
        (
            "bottom_flange",
            rect(r.flange_width_m, r.bottom_flange_h_m),
            r.support_mount_z_m + r.bottom_flange_h_m / 2.0,
            "frame",
        ),
        (
            "side_web",
            rect(r.rail_thickness_m, r.web_height_m + 2.0 * weld),
            r.support_mount_z_m + r.bottom_flange_h_m + r.web_height_m / 2.0,
            "frame",
        ),
        (
            "top_flange",
            rect(r.flange_width_m, r.top_flange_h_m),
            r.rail_top_z_m - r.top_flange_h_m / 2.0,
            "accent",
        ),
    )
    for side_index, side in enumerate((-1.0, 1.0)):
        radial = side * r.rail_centre_y_m
        for name, profile, z, material_key in pieces:
            mesh = sweep_profile_along_spline(
                path(radial, z),
                profile=profile,
                samples_per_segment=2,
                cap_profile=True,
                up_hint=(0.0, 0.0, 1.0),
            )
            frame.visual(
                mesh_from_geometry(mesh, f"{prefix}__{name}_{side_index}"),
                material=mats[material_key],
                name=f"{prefix}__{name}_{side_index}", material_class_id="metal.paint_coated",
            )
    _add_under_bed_ladder(frame, r, mats, prefix)


_FRAME_BUILDERS = {
    "low_profile_extrusion_deck": _frame_form_low_profile_extrusion_deck_build,
    "deep_channel_rail_bed": _frame_form_deep_channel_rail_bed_build,
    "pantograph_scissor_chords": _frame_form_pantograph_scissor_chords_build,
    "swept_curved_arc": _frame_form_swept_curved_arc_build,
}


# --------------------------------------------------------------------------- #
# Slot: support_form
# --------------------------------------------------------------------------- #


def _foot_axis(r: ResolvedRollerConveyorConfig, *, u: float, v: float, delta: float, host: bool):
    """Prismatic leveling axis, declared rather than guessed (MECHANICAL_PRIORS 4)."""
    if host:
        x, y = _xy(r, u, v, delta)
        point = (x, y, r.foot_joint_origin_z_m)
    else:
        # The foot's own frame: the stem axis passes through its local origin.
        point = (0.0, 0.0, 0.0)
    return AxisInterface(
        point=point,
        axis=(0.0, 0.0, -1.0),
        radial=(1.0, 0.0, 0.0),
        radius=max(1e-4, r.sliding_member_r_m + r.running_clearance_m),
        name="leg_bore_axis" if host else "leveling_stem_axis",
    )


def _add_leveling_foot(
    model,
    parent,
    r: ResolvedRollerConveyorConfig,
    mats,
    *,
    index: int,
    u: float,
    v: float,
    delta: float,
    frame_parented: bool,
):
    """002 L278-L315 — threaded stem plus round floor pad on a PRISMATIC joint.

    The pad bottoms out at z = 0 at minimum stroke in every source record
    (002 L294-L295 with joint origin L304 gives 0.120 - 0.1075 - 0.0125 = 0.000);
    extension then drives it below the floor plane, which is source behaviour.
    """
    prefix = f"support_form__{r.support_form}"
    foot = model.part(
        f"{prefix}__leveling_foot_{index}",
        meta={
            "role": "leveling_foot",
            "station": index // 2,
            "function": "threaded height adjustment and floor pad",
        },
    )
    pad_centre = r.foot_pad_h_m / 2.0 - r.leg_bottom_z_m
    pad_top = r.foot_pad_h_m - r.leg_bottom_z_m
    stem_bottom = pad_top - r.structural_weld_embed_m
    stem_length = max(0.006, r.stem_top_local_m - stem_bottom)
    foot.visual(
        Cylinder(radius=r.sliding_member_r_m, length=stem_length),
        origin=Origin(xyz=(0.0, 0.0, stem_bottom + stem_length / 2.0)),
        material=mats["steel"],
        name=(
            "inner_tube"
            if r.support_form == "telescoping_sleeve_legs"
            else "threaded_stem"
        ), material_class_id="metal.steel_galvanized",
    )
    foot.visual(
        Cylinder(radius=r.foot_pad_r_m, length=r.foot_pad_h_m),
        origin=Origin(xyz=(0.0, 0.0, pad_centre)),
        material=mats["pad"],
        name="round_pad", material_class_id="rubber.smooth_plain",
    )
    mate = mate_axes(
        _foot_axis(r, u=u, v=v, delta=delta, host=True),
        _foot_axis(r, u=u, v=v, delta=delta, host=False),
        radial_clearance=r.running_clearance_m,
    )
    joint_name = f"{prefix}__foot_adjust_{index}"
    model.articulation(
        joint_name,
        ArticulationType.PRISMATIC,
        parent=parent,
        child=foot,
        origin=mate.origin,
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(
            effort=250.0, velocity=0.015, lower=0.0, upper=r.foot_travel_m
        ),
        motion_properties=MotionProperties(damping=8.0, friction=4.0),
        meta={"mechanism": "threaded leveling stem retained inside its leg"},
    )
    return foot


def _add_leveler_jaws(
    part, r, mats, *, u, v, delta, prefix: str, index: int, local: bool, signs=(-1.0, 1.0)
):
    """002 L71-L77 — opposed guide jaws whose inner faces sit at the stem radius.

    The source makes them exactly tangent; the stem is a separate PART, so the
    rebuild holds a running clearance there instead of a zero-distance touch.
    """
    jaw_gap = r.sliding_member_r_m + 2.0 * r.running_clearance_m
    # The jaw bridges the tube wall to the stem: its inner face is the stem
    # radius plus a running clearance and its outer face welds into the wall,
    # which is what keeps the leveler insert connected to its leg.
    wall_inner = (
        r.leg_outer_m / 2.0 - r.leg_wall_m + r.structural_weld_embed_m
        if r.support_form in ("square_tube_legs_leveling_feet", "folding_hinged_legs")
        else jaw_gap + max(0.006, 0.012 * r.member_scale)
    )
    jaw_w = max(0.004, wall_inner - jaw_gap)
    jaw_h = max(0.012, 0.030 * r.member_scale)
    z = r.leg_bottom_z_m + jaw_h / 2.0 if not local else -r.leg_local_length_m + jaw_h / 2.0
    for jaw_index, sign in enumerate(signs):
        if local:
            part.visual(
                Box((jaw_w, jaw_h * 0.55, jaw_h)),
                origin=Origin(xyz=(sign * (jaw_gap + jaw_w / 2.0), 0.0, z)),
                material=mats["frame"],
                name=f"leveler_jaw_{index}_{jaw_index}", material_class_id="metal.paint_coated",
            )
        else:
            x, y = _xy(r, u + sign * (jaw_gap + jaw_w / 2.0), v, delta)
            part.visual(
                Box((jaw_w, jaw_h * 0.55, jaw_h)),
                origin=Origin(xyz=(x, y, z), rpy=(0.0, 0.0, _yaw(r, delta))),
                material=mats["frame"],
                name=f"{prefix}__leveler_jaw_{index}_{jaw_index}", material_class_id="metal.paint_coated",
            )


def _add_square_tube(part, r, mats, *, u, v, delta, prefix, index, local: bool):
    """002 L36-L67 — an open-bottom square tube built from four connected walls,
    not a solid box, so the leveling stem runs inside a real cavity."""
    outer = r.leg_outer_m
    wall = r.leg_wall_m
    half = (outer - wall) / 2.0
    if local:
        # A hinged leg is a PART: it must not weld into the frame, so the tube
        # top stops one weld short of the hinge plane and the leg is carried by
        # its joint (`allow_isolated_part`).
        height = max(0.010, r.leg_local_length_m - 2.0 * r.structural_weld_embed_m)
        z_centre = -r.leg_local_length_m + height / 2.0
    else:
        # Frame-geometry legs run past the hanging under-bed ladder and weld
        # into the rail underside itself; only the fold hinge lives at the
        # ladder's bottom face.
        height = r.support_mount_z_m + r.structural_weld_embed_m - r.leg_bottom_z_m
        z_centre = r.leg_bottom_z_m + height / 2.0
    walls = (
        ("outer_wall", (outer, wall, height), (0.0, half)),
        ("inner_wall", (outer, wall, height), (0.0, -half)),
        ("end_wall_a", (wall, outer - 2.0 * wall, height), (half, 0.0)),
        ("end_wall_b", (wall, outer - 2.0 * wall, height), (-half, 0.0)),
    )
    for name, size, (du, dv) in walls:
        if local:
            part.visual(
                Box(size),
                origin=Origin(xyz=(du, dv, z_centre)),
                material=mats["frame"],
                name=name, material_class_id="metal.paint_coated",
            )
        else:
            x, y = _xy(r, u + du, v + dv, delta)
            part.visual(
                Box(size),
                origin=Origin(xyz=(x, y, z_centre), rpy=(0.0, 0.0, _yaw(r, delta))),
                material=mats["frame"],
                name=f"{prefix}__leg_{index}_{name}", material_class_id="metal.paint_coated",
            )


def _add_leg_braces(frame, r, mats, prefix: str) -> None:
    """002 L183-L205 — continuous lower side braces plus trigonometric knee
    braces.  They brace the legs, so they are authored with the leg candidate
    rather than with the frame: without legs they would float in space."""
    if r.leg_station_count < 2 or r.leg_station_span_m < 0.10:
        return
    # 002 puts the brace at z=0.340 against a stem that tops out at 0.180: the
    # brace crosses the leg centreline, so it has to sit above the sliding
    # member's retracted top or it would spear it.
    z_low = max(
        r.leg_bottom_z_m + r.support_drop_m * 0.35,
        r.leg_bottom_z_m + r.stem_top_local_m + max(0.018, 0.050 * r.member_scale) / 2.0 + 0.010,
    )
    if z_low > r.leg_head_z_m - 0.020:
        return
    thickness = max(0.020, 0.045 * r.member_scale)
    height = max(0.018, 0.050 * r.member_scale)
    for side_index, side in enumerate((-1.0, 1.0)):
        v = side * r.leg_station_y_m
        if _is_arc(r):
            half = _leg_station_delta(r, r.leg_station_count - 1)
            steps = 8
            points = []
            for step in range(steps + 1):
                delta = -half + step * (2.0 * half) / steps
                x, y = _arc_xy(r, delta, v)
                points.append((x, y, z_low))
            mesh = sweep_profile_along_spline(
                points,
                profile=[
                    (-thickness / 2.0, -height / 2.0),
                    (thickness / 2.0, -height / 2.0),
                    (thickness / 2.0, height / 2.0),
                    (-thickness / 2.0, height / 2.0),
                ],
                samples_per_segment=2,
                cap_profile=True,
                up_hint=(0.0, 0.0, 1.0),
            )
            frame.visual(
                mesh_from_geometry(mesh, f"{prefix}__lower_side_brace_{side_index}"),
                material=mats["frame"],
                name=f"{prefix}__lower_side_brace_{side_index}", material_class_id="metal.paint_coated",
            )
        else:
            _box(
                frame,
                (r.leg_station_span_m + r.leg_outer_m, thickness, height),
                u=0.0,
                v=v,
                z=z_low,
                material=mats["frame"],
                name=f"{prefix}__lower_side_brace_{side_index}",
                r=r,
            )
        for index, delta, u in _leg_station_positions(r):
            # 002 L192-L205 runs a trigonometric knee brace from the leg out to
            # the frame.  Its top end lands on the RAIL underside, which exists
            # along the whole length in every frame form, rather than on a
            # crossmember that may not sit at this station.
            reach = math.copysign(0.220 * r.member_scale, 1.0 if u >= 0.0 else -1.0)
            delta_end = delta + (reach / r.arc_radius_m if _is_arc(r) else 0.0)
            u_end = u if _is_arc(r) else u + reach
            z0 = max(z_low, r.leg_bottom_z_m + r.support_drop_m * 0.45)
            z1 = r.support_mount_z_m + r.structural_weld_embed_m
            ax, ay = _xy(r, u, v, delta)
            bx, by = _xy(r, u_end, v, delta_end)
            span = math.hypot(bx - ax, by - ay)
            if span < 1e-6 or z1 <= z0:
                continue
            length = math.hypot(span, z1 - z0)
            frame.visual(
                Box((length, thickness * 0.75, height * 0.68)),
                origin=Origin(
                    xyz=((ax + bx) / 2.0, (ay + by) / 2.0, (z0 + z1) / 2.0),
                    rpy=(0.0, -math.atan2(z1 - z0, span), math.atan2(by - ay, bx - ax)),
                ),
                material=mats["frame"],
                name=f"{prefix}__knee_brace_{side_index}_{index}", material_class_id="metal.paint_coated",
            )


def _support_form_fixed_corner_plate_feet_build(model, frame, r, mats) -> None:
    """001 model.py:L81-L95 (+ L124-L136) — four corner plates with foot pads.

    No legs and ZERO support joints: the whole object is then N roller joints and
    nothing else, which is the source's own topology for 001.  The plate hangs
    from the rail underside; where it is shorter than the drop, a narrower post
    carries it down to the pad so the frame stays one connected solid and the
    pad still bottoms out at exactly z = 0.
    """
    prefix = f"support_form__{r.support_form}"
    weld = r.structural_weld_embed_m
    plate_top = r.support_mount_z_m + weld
    plate_bottom = max(r.foot_pad_h_m - weld, plate_top - r.corner_plate_h_m)
    for x_index, sign_u in enumerate((-1.0, 1.0)):
        u = sign_u * r.frame_corner_plate_x_m
        delta = (u / r.arc_radius_m) if _is_arc(r) else 0.0
        u_local = 0.0 if _is_arc(r) else u
        for y_index, side in enumerate((-1.0, 1.0)):
            plate_index = x_index * 2 + y_index
            v = side * r.rail_centre_y_m
            _box(
                frame,
                (
                    max(0.030, 0.070 * r.member_scale),
                    r.corner_plate_t_m,
                    plate_top - plate_bottom,
                ),
                u=u_local,
                v=v,
                z=(plate_top + plate_bottom) / 2.0,
                delta=delta,
                material=mats["frame"],
                name=f"{prefix}__corner_plate_{plate_index}",
                r=r,
            )
            if plate_bottom > r.foot_pad_h_m:
                post_h = plate_bottom - r.foot_pad_h_m + 2.0 * weld
                _box(
                    frame,
                    (
                        max(0.020, 0.045 * r.member_scale),
                        r.corner_plate_t_m * 0.75,
                        post_h,
                    ),
                    u=u_local,
                    v=v,
                    z=r.foot_pad_h_m - weld + post_h / 2.0,
                    delta=delta,
                    material=mats["frame"],
                    name=f"{prefix}__corner_post_{plate_index}",
                    r=r,
                )
            _box(
                frame,
                (r.foot_pad_l_m, r.foot_pad_w_m, r.foot_pad_h_m),
                u=u_local,
                v=v,
                z=r.foot_pad_h_m / 2.0,
                delta=delta,
                material=mats["pad"],
                name=f"{prefix}__foot_{plate_index}",
                r=r,
            )
            # Two recessed fasteners per plate, at thirds of the plate height so
            # corner_plate_h_m drives their position as well as the plate.
            for screw_index, fraction in enumerate((0.34, 0.68)):
                x, y = _xy(
                    r, u_local, side * (r.rail_centre_y_m + r.corner_plate_t_m / 2.0 - 0.0015), delta
                )
                frame.visual(
                    Cylinder(radius=max(0.003, 0.0055 * r.member_scale), length=0.003),
                    origin=Origin(
                        xyz=(x, y, plate_bottom + (plate_top - plate_bottom) * fraction),
                        rpy=(math.pi / 2.0, 0.0, -delta),
                    ),
                    material=mats["fastener"],
                    name=f"{prefix}__plate_screw_{plate_index}_{screw_index}", material_class_id="metal.stainless_matte",
                )


def _support_form_square_tube_legs_leveling_feet_build(model, frame, r, mats) -> None:
    """002 L36-L77 legs, L170-L181 placement, L278-L315 feet."""
    prefix = f"support_form__{r.support_form}"
    foot_index = 0
    for index, delta, u in _leg_station_positions(r):
        for side in (-1.0, 1.0):
            v = side * r.rail_centre_y_m
            _add_square_tube(
                frame, r, mats, u=u, v=v, delta=delta, prefix=prefix,
                index=foot_index, local=False,
            )
            _add_leveler_jaws(
                frame, r, mats, u=u, v=v, delta=delta, prefix=prefix,
                index=foot_index, local=False,
            )
            _add_leveling_foot(
                model, frame, r, mats, index=foot_index, u=u, v=v, delta=delta,
                frame_parented=True,
            )
            foot_index += 1
    _add_leg_braces(frame, r, mats, prefix)


def _support_form_telescoping_sleeve_legs_build(model, frame, r, mats) -> None:
    """var_height_telescoping_legs L36-L83 — cylindrical sleeve, locking collar,
    mount plate and lock lever.

    The source authors the sleeve and the collar SOLID and then buys the
    interference with 12 `allow_overlap` calls (L498-L519).  The rebuild bores
    both on `sleeve_wall_m`, turning the same 6 mm of radius into wall plus a
    real running clearance, exactly as 002's square leg is already hollow.
    """
    prefix = f"support_form__{r.support_form}"
    bore = r.sleeve_outer_r_m - r.sleeve_wall_m
    height = r.support_mount_z_m + r.structural_weld_embed_m - r.leg_bottom_z_m
    sleeve_mesh = mesh_from_geometry(
        LatheGeometry(
            [
                (bore, -height / 2.0),
                (r.sleeve_outer_r_m, -height / 2.0),
                (r.sleeve_outer_r_m, height / 2.0),
                (bore, height / 2.0),
            ],
            segments=_LATHE_SEGMENTS,
        ),
        f"{prefix}__sleeve_tube",
    )
    collar_h = max(0.012, 0.030 * r.member_scale)
    collar_mesh = mesh_from_geometry(
        LatheGeometry(
            [
                (bore, -collar_h / 2.0),
                (r.collar_r_m, -collar_h / 2.0),
                (r.collar_r_m, collar_h / 2.0),
                (bore, collar_h / 2.0),
            ],
            segments=_LATHE_SEGMENTS,
        ),
        f"{prefix}__collar_tube",
    )
    foot_index = 0
    for index, delta, u in _leg_station_positions(r):
        for side in (-1.0, 1.0):
            v = side * r.rail_centre_y_m
            x, y = _xy(r, u, v, delta)
            frame.visual(
                sleeve_mesh,
                origin=Origin(xyz=(x, y, r.leg_bottom_z_m + height / 2.0)),
                material=mats["frame"],
                name=f"{prefix}__leg_{foot_index}_outer_sleeve", material_class_id="metal.paint_coated",
            )
            frame.visual(
                collar_mesh,
                origin=Origin(xyz=(x, y, r.leg_bottom_z_m + collar_h)),
                material=mats["frame"],
                name=f"{prefix}__leg_{foot_index}_locking_collar", material_class_id="metal.paint_coated",
            )
            _box(
                frame,
                (
                    2.0 * r.collar_r_m,
                    2.0 * r.collar_r_m,
                    max(0.006, 0.008 * r.member_scale),
                ),
                u=u,
                v=v,
                z=r.support_mount_z_m
                + r.structural_weld_embed_m
                - max(0.006, 0.008 * r.member_scale) / 2.0,
                delta=delta,
                material=mats["frame"],
                name=f"{prefix}__leg_{foot_index}_mount_plate",
                r=r,
            )
            lever_len = max(0.020, 0.038 * r.member_scale)
            lever_w = max(0.008, 0.012 * r.member_scale)
            # The lever is a flat block on a round collar, so it only touches
            # along one line: the weld has to swallow the collar's sagitta over
            # the lever's own width or the lever floats off as an island.
            # The collar is a lathed MESH, so its faceted surface is inscribed in
            # the nominal radius; the weld datum is that inscribed radius, not
            # the nominal one.
            facet_r = r.collar_r_m * math.cos(math.pi / _LATHE_SEGMENTS)
            lever_sag = r.collar_r_m - math.sqrt(
                max(1e-9, facet_r ** 2 - min(lever_w / 2.0, facet_r * 0.9) ** 2)
            )
            _box(
                frame,
                (lever_w, lever_len, max(0.008, 0.014 * r.member_scale)),
                u=u,
                v=v
                + side
                * (r.collar_r_m - lever_sag - r.structural_weld_embed_m + lever_len / 2.0),
                z=r.leg_bottom_z_m + collar_h,
                delta=delta,
                material=mats["fastener"],
                name=f"{prefix}__leg_{foot_index}_lock_lever",
                r=r,
            )
            _add_leveling_foot(
                model, frame, r, mats, index=foot_index, u=u, v=v, delta=delta,
                frame_parented=True,
            )
            foot_index += 1
    _add_leg_braces(frame, r, mats, prefix)


def _support_form_folding_hinged_legs_build(model, frame, r, mats) -> None:
    """var_support_folding_legs L41-L140 (leg + joint), L236-L252 (frame lugs),
    L358-L394 (feet re-parented onto the leg).

    The leg's local origin is on the hinge and the tube runs along -Z, so every
    leg point stays at or below the hinge plane and the fold can never reach
    frame geometry.  Leaf plates and frame lugs interleave in Y without ever
    touching — a real clevis, which is why this record needs no allowance.

    SOURCE DEFECT 2 (L79-L84): the source places the pivot bolt at local
    z = -0.008, i.e. 8 mm below the hinge axis its own joint declares at
    HINGE_Z.  MECHANICAL_PRIORS 4 requires the pin coaxial with the hinge, so
    the rebuild puts it at local z = 0.
    """
    prefix = f"support_form__{r.support_form}"
    lug_t = max(0.004, 0.006 * r.member_scale)
    plate_t = max(0.004, 0.005 * r.member_scale)
    plate_h = max(0.030, 0.060 * r.member_scale)
    plate_len = max(0.040, 0.070 * r.member_scale)
    plate_len = min(plate_len, 2.0 * max(r.leg_outer_m, plate_len) / 2.0)
    # Clevis: the frame lugs stand OUTSIDE the tube in X and INSIDE the leaf
    # plates in Y, so lug and leaf interleave and never touch at any fold angle.
    leaf_v = r.leg_outer_m / 2.0 + plate_t / 2.0 + 0.002
    lug_v = leaf_v + plate_t / 2.0 + 0.0015 + lug_t / 2.0
    leg_index = 0
    for index, delta, u in _leg_station_positions(r):
        for side in (-1.0, 1.0):
            v = side * r.rail_centre_y_m
            # Fixed half of the hinge.  The source straddles the tube from the
            # INSIDE (L246: lugs at x = +-0.024 across a 0.060 tube), which puts
            # frame geometry inside the swept envelope of a moving part.  The
            # rebuild keeps the clevis but separates it in Y: a mounting pad
            # welded up into the frame carries two lugs OUTBOARD of the leaf
            # plates, so lug and leaf interleave and never touch at any angle.
            pad_top = (
                r.leg_head_z_m + min(r.under_bed_drop_m, 0.080) + r.structural_weld_embed_m
            )
            pad_bottom = r.leg_head_z_m - 0.006
            _box(
                frame,
                (2.0 * r.hinge_lug_half_gap_m, 2.0 * lug_v + lug_t, pad_top - pad_bottom),
                u=u,
                v=v,
                z=(pad_top + pad_bottom) / 2.0,
                delta=delta,
                material=mats["frame"],
                name=f"{prefix}__hinge_pad_{leg_index}",
                r=r,
            )
            # 002's lug is 0.080 tall (L246); it hangs from the pad and has to
            # reach well past the pin so the pivot is captured on both sides.
            lug_bottom = pad_bottom + 0.006 - r.hinge_lug_h_m
            for lug_index, lug_sign in enumerate((-1.0, 1.0)):
                _box(
                    frame,
                    (
                        2.0 * r.hinge_lug_half_gap_m,
                        lug_t,
                        pad_bottom + 0.006 - lug_bottom,
                    ),
                    u=u,
                    v=v + lug_sign * lug_v,
                    z=(pad_bottom + 0.006 + lug_bottom) / 2.0,
                    delta=delta,
                    material=mats["frame"],
                    name=f"{prefix}__hinge_lug_{leg_index}_{lug_index}",
                    r=r,
                )
            leg = model.part(
                f"{prefix}__folding_leg_{leg_index}",
                meta={"role": "folding_leg", "station": index,
                      "function": "folding support leg with hinge bracket"},
            )
            for plate_index, plate_sign in enumerate((-1.0, 1.0)):
                leg.visual(
                    Box((plate_len, plate_t, plate_h)),
                    origin=Origin(xyz=(0.0, plate_sign * leaf_v, -plate_h / 2.0 - 0.002)),
                    material=mats["frame"],
                    name=f"hinge_plate_{plate_index}", material_class_id="metal.paint_coated",
                )
            leg.visual(
                Cylinder(radius=r.hinge_pin_r_m,
                         length=2.0 * (leaf_v + plate_t / 2.0 + 0.0005)),
                origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["fastener"],
                name="pivot_bolt", material_class_id="metal.stainless_matte",
            )
            _add_square_tube(
                leg, r, mats, u=0.0, v=0.0, delta=0.0, prefix=prefix,
                index=leg_index, local=True,
            )
            _add_leveler_jaws(
                leg, r, mats, u=0.0, v=0.0, delta=0.0, prefix=prefix,
                index=leg_index, local=True,
            )
            x, y = _xy(r, u, v, delta)
            world_axis = (
                (math.sin(delta), math.cos(delta), 0.0) if _is_arc(r) else (0.0, 1.0, 0.0)
            )
            hinge_mate = mate_axes(
                AxisInterface(point=(x, y, r.hinge_axis_z_m), axis=world_axis,
                              radial=(0.0, 0.0, 1.0), name="hinge_lug_line"),
                AxisInterface(point=(0.0, 0.0, 0.0), axis=(0.0, 1.0, 0.0),
                              radial=(0.0, 0.0, 1.0), name="leg_hinge_bore"),
            )
            joint_name = f"{prefix}__leg_fold_{leg_index}"
            # Legs fold OUTWARD, away from the frame centre, so a folded leg
            # opens away from its neighbour instead of sweeping through it.  The
            # source fixes one direction because its 0.9 m bay never conflicts;
            # the axis stays (0, 1, 0) and only the signed travel changes.
            outward = -1.0 if _leg_station_u(r, index) < 0.0 else 1.0
            lower, upper = (
                (0.0, r.fold_upper_rad) if outward < 0.0 else (-r.fold_upper_rad, 0.0)
            )
            model.articulation(
                joint_name,
                ArticulationType.REVOLUTE,
                parent=frame,
                child=leg,
                origin=hinge_mate.origin,
                axis=hinge_mate.axis,
                motion_limits=MotionLimits(
                    effort=15.0, velocity=1.5, lower=lower, upper=upper
                ),
                motion_properties=MotionProperties(damping=2.0, friction=1.0),
                meta={"mechanism": "folding leg hinge for transport/storage"},
            )
            register_interface_mate(model, joint_name, hinge_mate)
            _add_leveling_foot(
                model, leg, r, mats, index=leg_index, u=0.0, v=0.0, delta=0.0,
                frame_parented=False,
            )
            leg_index += 1


def _support_form_scissor_crossed_base_build(model, frame, r, mats) -> None:
    """var_support_scissor_base L40-L118 — X-shaped stations in the YZ plane.

    Arms run from the outboard foot stance up to the rail attachment; the
    crossing point is derived, not authored: t = foot_y/(foot_y + rail_y).

    SOURCE DEFECT 1 (L85-L98): the arms lie in the YZ plane (their X extent is
    the bar thickness), so the pivot bolt through them must run along X, but the
    source authors bolt and both flanges with rpy=(0,0,0), i.e. as Z-axis
    cylinders.  The rebuild builds them with rpy=(0, pi/2, 0).
    """
    prefix = f"support_form__{r.support_form}"
    dy = r.foot_stance_y_m + r.rail_centre_y_m
    dz = r.leg_head_z_m - r.leg_bottom_z_m
    arm_length = math.hypot(dy, dz)
    # The leveling stem stands on the arm's own foot point, so the pair of arms
    # straddles it in X instead of running through it.  002's tangent-jaw
    # capture (L71-L77) then retains the stem, which is what removes the
    # source's 12 `allow_overlap` calls (L505-L525) without an allowance.
    arm_offset = r.sliding_member_r_m + r.scissor_arm_thickness_m / 2.0 + 2.0 * r.running_clearance_m
    foot_index = 0
    for index, delta, u in _leg_station_positions(r):
        for arm_index, arm_sign in enumerate((-1.0, 1.0)):
            roll = math.atan2(dz, arm_sign * dy)
            mid_v = (-arm_sign * r.foot_stance_y_m + arm_sign * r.rail_centre_y_m) / 2.0
            x, y = _xy(r, u + arm_sign * arm_offset, mid_v, delta)
            frame.visual(
                Box((r.scissor_arm_thickness_m, arm_length, r.scissor_arm_width_m)),
                origin=Origin(
                    xyz=(x, y, (r.leg_bottom_z_m + r.leg_head_z_m) / 2.0),
                    rpy=(roll, 0.0, _yaw(r, delta)),
                ),
                material=mats["frame"],
                name=f"{prefix}__scissor_{index}_arm_{arm_index}", material_class_id="metal.paint_coated",
            )
        x, y = _xy(r, u, 0.0, delta)
        frame.visual(
            Cylinder(
                radius=r.pivot_bolt_r_m,
                length=2.0 * arm_offset + r.scissor_arm_thickness_m + 0.012,
            ),
            origin=Origin(xyz=(x, y, r.scissor_cross_z_m), rpy=(0.0, math.pi / 2.0, _yaw(r, delta))),
            material=mats["frame"],
            name=f"{prefix}__scissor_{index}_pivot_bolt", material_class_id="metal.paint_coated",
        )
        for flange_index, flange_sign in enumerate((-1.0, 1.0)):
            fx, fy = _xy(
                r,
                u + flange_sign * (arm_offset + r.scissor_arm_thickness_m / 2.0 + 0.003),
                0.0,
                delta,
            )
            frame.visual(
                Cylinder(radius=r.pivot_bolt_r_m * 1.35, length=0.006),
                origin=Origin(
                    xyz=(fx, fy, r.scissor_cross_z_m),
                    rpy=(0.0, math.pi / 2.0, _yaw(r, delta)),
                ),
                material=mats["frame"],
                name=f"{prefix}__scissor_{index}_bolt_flange_{flange_index}", material_class_id="metal.paint_coated",
            )
        for gusset_index, side in enumerate((-1.0, 1.0)):
            gusset_top = r.support_mount_z_m + r.structural_weld_embed_m
            gusset_bottom = r.leg_head_z_m - max(0.018, 0.030 * r.member_scale)
            _box(
                frame,
                (
                    max(0.024, 0.040 * r.member_scale),
                    max(0.024, 0.040 * r.member_scale),
                    gusset_top - gusset_bottom,
                ),
                u=u + side * arm_offset,
                v=side * r.rail_centre_y_m,
                z=(gusset_top + gusset_bottom) / 2.0,
                delta=delta,
                material=mats["frame"],
                name=f"{prefix}__scissor_{index}_top_gusset_{gusset_index}",
                r=r,
            )
        for side in (-1.0, 1.0):
            v = side * r.foot_stance_y_m
            # The arm that lands on this stance is the one that rises to the
            # OPPOSITE rail, so the plate and its jaw share that arm's X offset.
            arm_u = u - side * arm_offset
            plate_u = max(
                0.006,
                2.0 * (arm_offset - r.sliding_member_r_m - 2.0 * r.running_clearance_m),
            )
            _box(
                frame,
                (
                    plate_u,
                    max(0.036, 0.060 * r.member_scale),
                    max(0.008, 0.012 * r.member_scale),
                ),
                u=arm_u,
                v=v,
                z=r.leg_bottom_z_m + max(0.008, 0.012 * r.member_scale) / 2.0,
                delta=delta,
                material=mats["frame"],
                name=f"{prefix}__scissor_{index}_foot_plate_{foot_index % 2}",
                r=r,
            )
            # The source drives the stem through the solid foot plate and buys it
            # with 12 allowances (L505-L525).  The parent's own tangent-jaw
            # capture solves it instead, so no allowance is needed.
            _add_leveler_jaws(
                frame, r, mats, u=u, v=v, delta=delta, prefix=prefix,
                index=foot_index, local=False, signs=(-side,),
            )
            _add_leveling_foot(
                model, frame, r, mats, index=foot_index, u=u, v=v, delta=delta,
                frame_parented=True,
            )
            foot_index += 1


_SUPPORT_BUILDERS = {
    "fixed_corner_plate_feet": _support_form_fixed_corner_plate_feet_build,
    "square_tube_legs_leveling_feet": _support_form_square_tube_legs_leveling_feet_build,
    "telescoping_sleeve_legs": _support_form_telescoping_sleeve_legs_build,
    "folding_hinged_legs": _support_form_folding_hinged_legs_build,
    "scissor_crossed_base": _support_form_scissor_crossed_base_build,
}


# --------------------------------------------------------------------------- #
# Slot: roller_form
# --------------------------------------------------------------------------- #


def _annulus_mesh(outer: float, bore: float, length: float, name: str):
    half = length / 2.0
    bore = _clamp(bore, 1e-4, outer - 5e-4)
    return mesh_from_geometry(
        LatheGeometry(
            [(bore, -half), (outer, -half), (outer, half), (bore, half)],
            segments=_LATHE_SEGMENTS,
        ),
        name,
    )


def _roller_form_shell_axle_endcaps_build(roller, r, mats, *, delta: float) -> None:
    """001 model.py:L139-L168 — shell, through-axle, two end caps and the
    polished strip.  The strip is deliberately part-embedded (bottom 0.02565
    inside a 0.026 radius) and exists so pose tests have a NON-axisymmetric
    feature to track; intra-part embedding is free per 1c."""
    spin = Origin(rpy=(math.pi / 2.0, 0.0, math.pi - delta))
    roller.visual(
        Cylinder(radius=r.roller_radius_m, length=r.roller_length_m),
        origin=spin,
        material=mats["roller"],
        name="roller_shell", material_class_id="metal.steel_bare",
    )
    roller.visual(
        Cylinder(radius=r.axle_r_m, length=2.0 * r.axle_half_length_m),
        origin=spin,
        material=mats["steel"],
        name="axle", material_class_id="metal.steel_galvanized",
    )
    cap_centre = r.roller_half_length_m + r.end_cap_inset_m
    for side_index, side in enumerate((-1.0, 1.0)):
        roller.visual(
            Cylinder(radius=r.end_cap_r_m, length=r.end_cap_length_m),
            origin=Origin(
                xyz=(side * cap_centre * math.sin(delta), side * cap_centre * math.cos(delta), 0.0),
                rpy=(math.pi / 2.0, 0.0, math.pi - delta),
            ),
            material=mats["cap"],
            name=f"end_cap_{side_index}", material_class_id="metal.blackened_gunmetal",
        )
    # 001 L163-L167 embeds the strip in the barrel (bottom 0.02565 inside a
    # 0.026 radius).  A flat strip on a round barrel only touches along the
    # crown line, so the embed has to swallow the sagitta at the strip EDGE as
    # well as the authored stand-off, or the strip lifts off as an island at
    # the wide/proud end of the range.  Thickness therefore derives from both.
    half_w = min(r.highlight_strip_w_m, 1.8 * r.roller_radius_m) / 2.0
    sagitta = r.roller_radius_m - math.sqrt(max(1e-9, r.roller_radius_m ** 2 - half_w ** 2))
    strip_bottom = r.roller_radius_m - sagitta - r.fitting_weld_embed_m
    strip_top = r.roller_radius_m + r.highlight_proud_m
    roller.visual(
        Box((2.0 * half_w, r.roller_length_m * 0.94, strip_top - strip_bottom)),
        origin=Origin(
            xyz=(0.0, 0.0, (strip_top + strip_bottom) / 2.0), rpy=(0.0, 0.0, -delta)
        ),
        material=mats["accent"],
        name="surface_highlight", material_class_id="metal.paint_coated",
    )


def _roller_form_steel_tube_endcaps_build(roller, r, mats, *, delta: float) -> None:
    """002 model.py:L239-L260 — heavy steel tube, two nearly flush black end
    caps and the axle.  The source declares ROLLER_TUBE_LENGTH = 0.720 (L23) but
    draws the literal 0.684; the rebuild derives both from `roller_length_m`."""
    spin = Origin(rpy=(math.pi / 2.0, 0.0, math.pi - delta))
    roller.visual(
        Cylinder(radius=r.roller_radius_m, length=r.roller_length_m),
        origin=spin,
        material=mats["roller"],
        name="tube", material_class_id="metal.steel_bare",
    )
    cap_centre = r.roller_half_length_m + r.end_cap_inset_m
    for side_index, side in enumerate((-1.0, 1.0)):
        roller.visual(
            Cylinder(radius=r.end_cap_r_m, length=r.end_cap_length_m),
            origin=Origin(
                xyz=(side * cap_centre * math.sin(delta), side * cap_centre * math.cos(delta), 0.0),
                rpy=(math.pi / 2.0, 0.0, math.pi - delta),
            ),
            material=mats["cap"],
            name=f"end_cap_{side_index}", material_class_id="metal.blackened_gunmetal",
        )
    roller.visual(
        Cylinder(radius=r.axle_r_m, length=2.0 * r.axle_half_length_m),
        origin=spin,
        material=mats["steel"],
        name="axle", material_class_id="metal.steel_galvanized",
    )


def _roller_form_split_twin_half_roller_build(roller, r, mats, *, delta: float, meshes) -> None:
    """var_roller_layout_split_rollers L212-L213, L256-L338 — twin-half tube on a
    frame-owned axle.

    The source leaves every roller member SOLID around that axle and blankets the
    whole `frame x roller_i` pair with 24 unscoped `allow_overlap` calls
    (L487-L493).  The rebuild bores them instead — exactly the annular
    construction 001 already uses for `_bearing_ring_mesh` — and folds the split
    rings and the frame spacer into one bored sleeve, which also removes 3N
    collision solids.  Both halves stay ONE part on one joint, so the split reads
    visually without adding a joint.
    """
    half_offset = (r.roller_length_m - r.split_gap_m) / 4.0 + r.split_gap_m / 2.0
    for name, side in (("tube_left", -1.0), ("tube_right", 1.0)):
        roller.visual(
            meshes["half_tube"],
            origin=Origin(
                xyz=(
                    side * half_offset * math.sin(delta),
                    side * half_offset * math.cos(delta),
                    0.0,
                ),
                rpy=(math.pi / 2.0, 0.0, math.pi - delta),
            ),
            material=mats["roller"],
            name=name, material_class_id="metal.steel_bare",
        )
    roller.visual(
        meshes["bearing_sleeve"],
        origin=Origin(rpy=(math.pi / 2.0, 0.0, math.pi - delta)),
        material=mats["cap"],
        name="bearing_sleeve", material_class_id="metal.blackened_gunmetal",
    )
    cap_centre = r.roller_half_length_m + r.end_cap_inset_m
    for side_index, side in enumerate((-1.0, 1.0)):
        roller.visual(
            meshes["end_cap"],
            origin=Origin(
                xyz=(side * cap_centre * math.sin(delta), side * cap_centre * math.cos(delta), 0.0),
                rpy=(math.pi / 2.0, 0.0, math.pi - delta),
            ),
            material=mats["cap"],
            name=f"end_cap_{side_index}", material_class_id="metal.blackened_gunmetal",
        )


def _split_roller_meshes(r: ResolvedRollerConveyorConfig):
    prefix = f"roller_form__{r.roller_form}"
    half_length = (r.roller_length_m - r.split_gap_m) / 2.0
    bore = r.sleeve_bore_r_m
    return {
        "half_tube": _annulus_mesh(
            r.roller_radius_m, bore, half_length, f"{prefix}__half_tube"
        ),
        "bearing_sleeve": _annulus_mesh(
            r.split_sleeve_outer_r_m,
            bore,
            r.split_gap_m + 2.0 * r.structural_weld_embed_m + r.split_gap_m * 0.4,
            f"{prefix}__bearing_sleeve",
        ),
        "end_cap": _annulus_mesh(
            r.end_cap_r_m, bore, r.end_cap_length_m, f"{prefix}__end_cap"
        ),
    }


def _add_frame_axle(frame, r, mats) -> None:
    """split_twin_half_roller inverts the axle ownership (L215-L224): the axle
    lives on the FRAME.  Its ends weld into the two bearing inserts, so the frame
    stays one connected solid, and the running fit moves to the sleeve bore."""
    half = r.bearing_inner_face_y_m + r.fitting_weld_embed_m
    for index in range(r.roller_count):
        delta = _station_delta(r, index)
        _radial_cylinder(
            frame,
            r.axle_r_m,
            2.0 * half,
            u=_station_u(r, index),
            v=0.0,
            z=_station_axis_z(r, index),
            delta=delta,
            material=mats["steel"],
            name=f"frame_form__{r.frame_form}__axle_{index}",
            r=r,
        )


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #


def _materials(model: ArticulatedObject) -> dict[str, str]:
    model.material("conveyor_frame_paint", rgba=(0.025, 0.36, 0.72, 1.0))
    model.material("conveyor_edge", rgba=(0.055, 0.48, 0.86, 1.0))
    model.material("roller_steel", rgba=(0.19, 0.21, 0.21, 1.0))
    model.material("roller_end_black", rgba=(0.045, 0.052, 0.055, 1.0))
    model.material("axle_zinc", rgba=(0.66, 0.68, 0.67, 1.0))
    model.material("bearing_black", rgba=(0.035, 0.040, 0.042, 1.0))
    model.material("fastener_steel", rgba=(0.43, 0.45, 0.45, 1.0))
    model.material("foot_pad_blue", rgba=(0.025, 0.31, 0.63, 1.0))
    return {
        "frame": "conveyor_frame_paint",
        "accent": "conveyor_edge",
        "roller": "roller_steel",
        "cap": "roller_end_black",
        "steel": "axle_zinc",
        "bearing": "bearing_black",
        "fastener": "fastener_steel",
        "pad": "foot_pad_blue",
    }


def _spin_axis_provider(r: ResolvedRollerConveyorConfig, index: int) -> AxisInterface:
    delta = _station_delta(r, index)
    x, y = _xy(r, _station_u(r, index), 0.0, delta)
    axis = (math.sin(delta), math.cos(delta), 0.0) if _is_arc(r) else (0.0, 1.0, 0.0)
    return AxisInterface(
        point=(x, y, _station_axis_z(r, index)),
        axis=axis,
        radial=(0.0, 0.0, 1.0),
        radius=r.bearing_bore_r_m,
        name=f"frame_bearing_bore_{index}",
    )


def _spin_axis_consumer(r: ResolvedRollerConveyorConfig, index: int) -> AxisInterface:
    """The roller's own frame: local +Y is its axle, local +Z is up.

    `mate_axes` then yaws the child frame onto the station's radial direction, so
    the WORLD spin axis is `(sin d, cos d, 0)` exactly as the curved source
    authors it (L391-L398) while the joint axis stays the roller's own axle in
    its own frame.  A roller is thereby never spun about a chord.
    """
    return AxisInterface(
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=r.axle_r_m,
        name=f"roller_spin_axis_{index}",
    )


def _check_support_footprint(r: ResolvedRollerConveyorConfig) -> None:
    """MECHANICAL_PRIORS 2: the real carrying area, never the host AABB.  The
    provider extent is the crossmember underside the legs actually land on."""
    if r.support_form == "fixed_corner_plate_feet" or r.leg_station_count < 1:
        return
    provider = PlaneInterface(
        point=(0.0, 0.0, r.leg_head_z_m),
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.frame_length_m, 2.0 * r.rail_centre_y_m + r.leg_footprint_v_m),
        name="support_mount_plane",
    )
    consumer = PlaneInterface(
        point=(0.0, 0.0, 0.0),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(
            max(1e-3, r.leg_footprint_u_m),
            max(1e-3, min(r.leg_footprint_v_m, 2.0 * r.rail_centre_y_m)),
        ),
        name="leg_head_plane",
    )
    for index in range(r.leg_station_count):
        mate_planes(provider, consumer, uv=(_leg_station_u(r, index), 0.0))


def build_roller_conveyor(
    config: RollerConveyorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or RollerConveyorConfig()
    r = resolve_config(config)
    _check_support_footprint(r)

    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "roller_conveyor",
            "slot_choices": slot_choices_for_config(r),
            "frame_length_mode": r.frame_length_mode,
        },
    )
    mats = _materials(model)
    frame = model.part(
        f"frame_form__{r.frame_form}__frame",
        meta={
            "role": "conveyor_frame",
            "frame_form": r.frame_form,
            "frame_length_mode": r.frame_length_mode,
            "station_count": r.roller_count,
        },
    )
    _FRAME_BUILDERS[r.frame_form](frame, r, mats)
    _add_bearing_inserts(frame, r, mats)
    if r.roller_form == "split_twin_half_roller":
        _add_frame_axle(frame, r, mats)
    _SUPPORT_BUILDERS[r.support_form](model, frame, r, mats)

    split_meshes = (
        _split_roller_meshes(r) if r.roller_form == "split_twin_half_roller" else None
    )
    for index in range(r.roller_count):
        delta = _station_delta(r, index)
        roller = model.part(
            f"roller_form__{r.roller_form}__roller_{index}",
            meta={
                "role": "conveyor_roller",
                "roller_index": index,
                "stagger_level": (
                    "high"
                    if r.roller_layout == "staggered_alternating_height" and index % 2
                    else "low"
                ),
            },
        )
        if r.roller_form == "shell_axle_endcaps":
            _roller_form_shell_axle_endcaps_build(roller, r, mats, delta=0.0)
        elif r.roller_form == "steel_tube_endcaps":
            _roller_form_steel_tube_endcaps_build(roller, r, mats, delta=0.0)
        else:
            _roller_form_split_twin_half_roller_build(
                roller, r, mats, delta=0.0, meshes=split_meshes
            )
        mate = mate_axes(
            _spin_axis_provider(r, index),
            _spin_axis_consumer(r, index),
            radial_clearance=r.running_clearance_m,
        )
        joint_name = f"roller_form__{r.roller_form}__roller_spin_{index}"
        model.articulation(
            joint_name,
            ArticulationType.CONTINUOUS,
            parent=frame,
            child=roller,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(effort=2.0, velocity=18.0),
            motion_properties=MotionProperties(damping=0.01, friction=0.015),
            meta={"mechanism": "free-spinning gravity roller about its own axle"},
        )
        register_interface_mate(model, joint_name, mate)
    return model


def build_seeded_roller_conveyor(seed: int, *, assets: AssetContext | None = None):
    return build_roller_conveyor(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Author tests — the Design's `required_author_checks`, verbatim.
# --------------------------------------------------------------------------- #


def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def _joint_by_child(model: ArticulatedObject):
    return {str(joint.child): joint for joint in model.articulations}


def run_roller_conveyor_tests(
    object_model: ArticulatedObject,
    config: RollerConveyorConfig | None = None,
) -> TestReport:
    r = resolve_config(config or RollerConveyorConfig())
    ctx = TestContext(object_model)
    ctx.check_model_valid()

    frames = _parts_by_role(object_model, "conveyor_frame")
    rollers = _parts_by_role(object_model, "conveyor_roller")
    feet = _parts_by_role(object_model, "leveling_foot")
    folding_legs = _parts_by_role(object_model, "folding_leg")
    frame = frames[0] if frames else None
    joints = _joint_by_child(object_model)

    # Every non-root member is carried by its joint on a running clearance:
    # `interpart_connection_policy = none_all_joint_carried`.
    for part in rollers:
        ctx.allow_isolated_part(
            part, reason="gravity roller on a running fit, carried by its spin joint"
        )
    for part in feet:
        ctx.allow_isolated_part(
            part, reason="leveling foot on a running fit inside its leg, carried by its prismatic joint"
        )
    for part in folding_legs:
        ctx.allow_isolated_part(
            part, reason="folding leg on a clevis clearance, carried by its hinge"
        )
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=6)

    roller_names = {part.name for part in rollers}
    frame_name = getattr(frame, "name", None)
    roller_joints = [joints.get(name) for name in sorted(roller_names)]
    roller_joints = [joint for joint in roller_joints if joint is not None]

    ctx.check(
        "category_anchor: exactly one root frame part and every other part descends from it",
        len(frames) == 1
        and frame is not None
        and len(object_model.parts)
        == 1 + r.roller_count + r.foot_part_count + r.folding_leg_part_count
        and {str(joint.child) for joint in object_model.articulations}
        == {part.name for part in object_model.parts if part.name != frame_name},
        details=(
            f"frames={len(frames)} parts={len(object_model.parts)} "
            f"expected={1 + r.roller_count + r.foot_part_count + r.folding_leg_part_count}"
        ),
    )

    axis_ok = True
    origin_ok = True
    for index in range(r.roller_count):
        joint = joints.get(f"roller_form__{r.roller_form}__roller_{index}")
        if joint is None:
            axis_ok = False
            continue
        delta = _station_delta(r, index)
        axis_ok = axis_ok and all(
            abs(float(a) - b) <= 1e-6 for a, b in zip(tuple(joint.axis), (0.0, 1.0, 0.0))
        )
        x, y = _xy(r, _station_u(r, index), 0.0, delta)
        origin_ok = origin_ok and all(
            abs(a - b) <= 1e-6
            for a, b in zip(
                tuple(joint.origin.xyz), (x, y, _station_axis_z(r, index))
            )
        )
    ctx.check(
        "category_anchor: every roller spins about the transverse axis through its own centre",
        len(roller_joints) == r.roller_count
        and axis_ok
        and origin_ok
        and all(
            joint.articulation_type == ArticulationType.CONTINUOUS for joint in roller_joints
        ),
        details=f"roller_joints={len(roller_joints)} axis_ok={axis_ok} origin_ok={origin_ok}",
    )
    ctx.check(
        "category_anchor: rollers are parented to the frame, never chained roller to roller",
        len(rollers) == r.roller_count
        and all(str(joint.parent) == frame_name for joint in roller_joints)
        and not any(str(joint.parent) in roller_names for joint in object_model.articulations),
        details=f"parents={sorted({str(j.parent) for j in roller_joints})}",
    )

    if _is_arc(r):
        steps = [
            _station_delta(r, index + 1) - _station_delta(r, index)
            for index in range(r.roller_count - 1)
        ]
        want_step = r.arc_angle_rad / (r.roller_count - 1)
    else:
        steps = [
            _station_u(r, index + 1) - _station_u(r, index)
            for index in range(r.roller_count - 1)
        ]
        want_step = r.station_pitch_m
    ctx.check(
        "category_anchor: roller stations are evenly pitched along the conveying direction",
        bool(steps) and all(abs(step - want_step) <= 1e-7 for step in steps),
        details=f"step={steps[0] if steps else None} expected={want_step}",
    )
    ctx.check(
        "category_anchor: adjacent rollers keep at least 0.016 m of clear gap",
        r.roller_gap_m >= _MIN_ROLLER_GAP - 1e-9,
        details=(
            f"gap={r.roller_gap_m:.5f} pitch={r.station_pitch_m:.5f} "
            f"radius={r.roller_radius_m:.5f} stagger={r.stagger_offset_m:.5f}"
        ),
    )

    contained = True
    if frame is not None:
        for index in (0, r.roller_count - 1):
            part = object_model.get_part(f"roller_form__{r.roller_form}__roller_{index}")
            contained = contained and bool(
                ctx.expect_within(
                    part,
                    frame,
                    axes="xy",
                    margin=r.roller_radius_m,
                    name=f"roller {index} lies inside the frame in plan",
                )
            )
    ctx.check(
        "category_anchor: every roller lies within the frame in plan and clears both rails axially",
        contained
        and r.barrel_axial_clearance_m >= _MIN_BARREL_CLEARANCE - 1e-9
        and r.end_cap_axial_clearance_m > 0.0
        and r.bearing_insert_length_m >= _MIN_BEARING_INSERT - 1e-9,
        details=(
            f"barrel_clearance={r.barrel_axial_clearance_m:.5f} "
            f"cap_clearance={r.end_cap_axial_clearance_m:.5f} "
            f"insert={r.bearing_insert_length_m:.5f}"
        ),
    )

    lowest = None
    for part in object_model.parts:
        aabb = ctx.part_world_aabb(part)
        if aabb is None:
            continue
        lowest = aabb[0][2] if lowest is None else min(lowest, aabb[0][2])
    ctx.check(
        "category_anchor: the object is grounded at z=0 at minimum support stroke",
        lowest is not None and abs(lowest - r.ground_plane_z_m) <= 0.0015,
        details=f"lowest_z={lowest} ground_plane_z={r.ground_plane_z_m}",
    )
    ctx.check(
        "category_anchor: the roller bed plane is level and derived from the rail section",
        abs(r.rail_top_z_m - (r.bed_plane_z_m + r.rail_top_above_crown_m)) <= 1e-12
        and abs(r.support_mount_z_m - (r.rail_top_z_m - r.rail_stack_height_m)) <= 1e-12
        and abs(r.bed_plane_z_m - (r.bed_height_m + r.roller_radius_m)) <= 1e-12
        and r.support_mount_z_m > 0.0,
        details=(
            f"bed_plane={r.bed_plane_z_m:.5f} rail_top={r.rail_top_z_m:.5f} "
            f"stack={r.rail_stack_height_m:.5f} mount={r.support_mount_z_m:.5f}"
        ),
    )
    emitted = [str(item) for item in getattr(ctx, "_allowances", ())]
    ctx.check(
        "category_anchor: no seed emits an allow_overlap allowance",
        not any(item.lstrip().startswith("allow_overlap(") for item in emitted),
        details=f"allowances={len(emitted)}",
    )

    foot_joints = [joints.get(part.name) for part in feet]
    foot_joints = [joint for joint in foot_joints if joint is not None]
    ctx.check(
        "category_anchor: every leveling foot slides down its own leg axis",
        len(feet) == r.foot_part_count
        and len(foot_joints) == r.foot_part_count
        and all(
            joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(float(value) for value in joint.axis) == (0.0, 0.0, -1.0)
            and (joint.motion_limits.upper or 0.0) > 0.0
            for joint in foot_joints
        ),
        details=f"feet={len(feet)} expected={r.foot_part_count}",
    )
    ctx.check(
        "category_anchor: the sliding member stays retained in its leg at full extension",
        r.support_form == "fixed_corner_plate_feet"
        or (
            r.stem_insertion_min_m >= _MIN_STEM_RETENTION - 1e-9
            and r.foot_travel_m > 0.0
            and (
                r.support_form != "telescoping_sleeve_legs"
                or r.sleeve_bore_clearance_m > 0.0
            )
        ),
        details=(
            f"insertion_at_full_extension={r.stem_insertion_min_m:.5f} "
            f"travel={r.foot_travel_m:.5f} bore_clearance={r.sleeve_bore_clearance_m:.5f}"
        ),
    )

    fold_joints = [joints.get(part.name) for part in folding_legs]
    fold_joints = [joint for joint in fold_joints if joint is not None]
    ctx.check(
        "category_anchor: folding legs hinge about the transverse axis on the frame underside",
        len(folding_legs) == r.folding_leg_part_count
        and len(fold_joints) == r.folding_leg_part_count
        and all(
            joint.articulation_type == ArticulationType.REVOLUTE
            and abs(float(joint.axis[2])) <= 1e-9
            and str(joint.parent) == frame_name
            and abs(float(joint.origin.xyz[2]) - r.hinge_axis_z_m) <= 1e-6
            for joint in fold_joints
        ),
        details=f"folding_legs={len(folding_legs)} hinge_z={r.hinge_axis_z_m:.5f}",
    )
    clears = True
    for part, joint in zip(folding_legs, fold_joints):
        limits = joint.motion_limits
        edge = (limits.upper or 0.0) if (limits.upper or 0.0) != 0.0 else (limits.lower or 0.0)
        for value in (0.0, edge * 0.5, edge):
            with ctx.pose({joint: value}):
                aabb = ctx.part_world_aabb(part)
            if aabb is None:
                clears = False
                continue
            clears = clears and aabb[1][2] <= r.leg_head_z_m - 1e-6
    ctx.check(
        "category_anchor: the folded leg clears the frame across its whole hinge range",
        clears,
        details=f"hinge_axis_z={r.hinge_axis_z_m:.5f} fold_upper={r.fold_upper_rad:.4f}",
    )
    leg_names = {part.name for part in folding_legs}
    ctx.check(
        "category_anchor: leveling feet are carried by their folding leg, not by the frame",
        r.support_form != "folding_hinged_legs"
        or (
            len(foot_joints) == r.foot_part_count
            and all(str(joint.parent) in leg_names for joint in foot_joints)
        ),
        details=f"foot_parents={sorted({str(j.parent) for j in foot_joints})}",
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "curved_arc_split_rollers_folding_legs_at_max_N",
        {
            "frame_form": "swept_curved_arc",
            "roller_form": "split_twin_half_roller",
            "support_form": "folding_hinged_legs",
            "roller_layout": "staggered_alternating_height",
            "roller_count": 24,
            "arc_radius_m": 1.5,
            "arc_angle_rad": 1.2,
        },
        reason=(
            "The radial spin axis, the frame-owned axle bore, the depth-2 fold chain "
            "and the tightest arc all at the largest N and pose budget."
        ),
    ),
    corner_case(
        "pantograph_on_scissor_base_at_min_N",
        {
            "frame_form": "pantograph_scissor_chords",
            "support_form": "scissor_crossed_base",
            "roller_form": "shell_axle_endcaps",
            "roller_count": 4,
            "roller_pitch_m": 0.200,
            "end_inset_m": 0.140,
            "foot_stance_y_m": 0.700,
            "bed_height_m": 0.900,
        },
        reason=(
            "Shallowest rail section under the widest outboard stance: the pantograph "
            "must leave the scissor base room to reach z=0 and the bearing insert must "
            "still land inside the thin chord."
        ),
    ),
    corner_case(
        "widest_rollers_in_the_narrowest_frame",
        {
            "frame_form": "deep_channel_rail_bed",
            "support_form": "telescoping_sleeve_legs",
            "roller_form": "steel_tube_endcaps",
            "roller_count": 24,
            "frame_length_authored_m": 1.200,
            "frame_outer_width_m": 0.500,
            "roller_length_m": 0.820,
            "roller_radius_m": 0.042,
            "foot_travel_m": 0.120,
        },
        reason=(
            "Mode B at its shortest frame and largest N drives the pitch-clearance "
            "rule; the roller length and the telescoping stroke are simultaneously "
            "at the edge that the rail datum has to absorb."
        ),
    ),
    corner_case(
        "low_deck_corner_plate_feet_at_min_N",
        {
            "frame_form": "low_profile_extrusion_deck",
            "support_form": "fixed_corner_plate_feet",
            "roller_form": "shell_axle_endcaps",
            "roller_layout": "uniform_inline",
            "roller_count": 4,
            "bed_height_m": 0.170,
            "corner_plate_h_m": 0.120,
            "cross_brace_count": 4,
        },
        reason=(
            "The zero-support-joint topology at the lowest bed: the corner plate must "
            "still carry the rail down to a pad that bottoms out at exactly z=0."
        ),
    ),
)


# The corner harness materializes a case as `Config(**payload)`, so the generic
# names are exported alongside the slug-qualified ones.
Config = RollerConveyorConfig
ResolvedConfig = ResolvedRollerConveyorConfig


__all__ = [
    "Config",
    "FrameForm",
    "ResolvedConfig",
    "ResolvedRollerConveyorConfig",
    "RollerConveyorConfig",
    "RollerForm",
    "RollerLayout",
    "SupportForm",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_roller_conveyor",
    "build_seeded_roller_conveyor",
    "config_from_seed",
    "resolve_config",
    "run_roller_conveyor_tests",
    "slot_choices_for_config",
]
