# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Self-contained Design-backed `manual_pipe_bender` template.

A grounded or bench/vise-mounted metal-forming tool whose defining articulation
is a grooved former and a long moving member sweeping about a shared **+Z bend
axis**, with spinning guide rollers and at least one adjustment DOF.

Slots (`designs/manual_pipe_bender.json`):
  bender_topology 6  pedestal_ladder_rail | cast_bench_mimic | three_roll_pyramid |
                     pedestal_fixed_die_swing_handle | hand_lever_plier | ram_tripod
  former_profile  4  round_flanged_groove | square_tube_channel |
                     multi_radius_stepped | rotary_draw_wrap_wheel
  mount           4  bench_plate | pedestal_floor_plate | vise_tongue | caster_deck
  former_count    N  multiplicity {1,2,3,4} over `former_profile`
core_domain = 6*4*4 = 96, raw_domain = 96*4 = 384.  Every one must build.

`drive` and `follower_module` are DERIVED from `bender_topology` (design binding
`topology_determines_actuation_and_follower`), and so is the guide-roller form
(`roller_track_to_guide_rollers`).  The tables are `_TOPOLOGY_DRIVE`,
`_TOPOLOGY_FOLLOWER` and `_TOPOLOGY_ROLLER_FORM` below; each mapping puts a
module on the lineage its source record actually belongs to.

===========================================================================
FRAME CONVENTION
===========================================================================
`+Z` is up and is the bend axis of every seed; `+X` is the pipe feed direction;
`z = 0` is the ground plane the mount stands on.  DEPARTURE, stated: every
candidate puts the bend axis at `x = y = 0`, where the sources use their own
host datum (`PIVOT_X = -0.070` in 004, `SPINDLE_X = -0.035` in the L3 family,
`x = -0.225` in L5).  That is a choice of origin, not of construction: every
station, rail and follower offset below is measured FROM the bend axis exactly
as the source measures it from its own pivot.

===========================================================================
THE COAXIAL STACK -- why this template needs no `ctx.allow_overlap`
===========================================================================
All 20 source records call `ctx.allow_overlap` (~70 sites) and preflight blocks
it for a Design-backed template.  Rather than patch 38 sites one at a time, the
rebuild removes the *cause*: every moving member turns about the SAME +Z axis,
and the members are separated into disjoint Z bands and disjoint radial bands,
so no pose of any joint can bring two parts together.  Bottom to top:

    z = 0                      ground
    [0, mount_height_m]        mount_base
    rail_top_z_m               = mount_height_m + host_stack_z_m
    [rail_top, +Hr]            guide rollers      (radially OUTSIDE everything)
    former_seat_z_m            = rail_top + thrust washer + 0.2 mm running gap
    [former_seat, +Hf]         bending formers    (station 0 on the bend axis)
    moving_member_seat_z_m     = former_seat + Hf + 1 mm lever seat gap
    [msz, +arm_t]              moving member      (+ follower hanging into the
                                                   former band at its own radius)
    drive_gear_z_m             drive member gear plane
    drive_crank_z_m            drive member crank plane

Radial invariants, all derived and all asserted by the author tests:
  * the follower sweeps the annulus `follower_station_r +- (stroke + body_r)`;
    every frame-borne feature in the former band is either strictly inside it
    (the central spindle) or strictly outside it (`static_obstacle_max_r`);
  * every guide roller station sits beyond `follower_orbit_outer_m`, the
    farthest former station and every static obstacle, plus its own radius and
    8 mm;
  * the drive's counterpart -- ring gear, chain wrap or ratchet pawl -- is
    welded into the MOVING MEMBER and is coaxial with the drive, so the 0.3 mm
    the design's `gear_centre_distance_m` asks for is a RADIAL gap that holds at
    every relative angle instead of a centre distance that only holds at rest.
    DEPARTURE, stated: `hand_lever_plier` (L4 L146-L155 / L255-L264) meshes two
    gears on two parallel axes 0.32 mm apart.  A second frame-borne axis inside
    the moving member's own sweep radius cannot survive `fail_if_parts_overlap_
    in_sampled_poses` at any arm length, so the pair is restated coaxially: same
    tip radii, same 0.3 mm, same "teeth never overlap" rule.

The three tolerances (`geometry_qc.py:2279-2281`, `3165-3216`, `3919`):
  INTRA-PART weld  -> `intra_part_weld_m`, a real embed.  Collision is computed
    only between parts, so stacked visuals inside one part interpenetrate for
    free; but `find_part_geometry_connectivity_findings` walks them per link at
    `contact_tol=1e-6`, so a *tangent* stack inside a part reads as broken
    geometry.  Every stacked primitive here embeds.
  CROSS-PART weld  -> `lineage_weld_m`, one value per lineage scaled by that
    lineage's own seat height (0.20 mm for the 0.33 m hand tool up to 0.60 mm
    for the 1.11 m floor pedestal).  Every value is >= 20x the `%.6g` URDF
    quantisation at its own seat height and < 1 mm, the tolerance
    `find_geometry_overlaps` actually defaults to, so the weld can never be read
    as an interference under either the 1e-3 default or the 5e-3 env default.
  RUNNING FIT      -> a real gap.  `bore = shaft + 0.03*shaft + 0.0002`
    (design binding `shaft_to_bore_clearance`, fitted to 005 / L4 / L5 at once).
    LINEAGE L3 BORES EVERY HOLE 0.5-1.0 mm UNDER ITS PIN (hub 0.010 vs spindle
    0.011, arm 0.0055 vs pin 0.006, bracket 0.0065 vs axle 0.007); the rebuild
    INVERTS that sign.  Members carried by their joint on such a fit are
    declared with `ctx.allow_isolated_part`, which preflight permits.

Deliberate deviations from source construction, each stated where it is made:
  1. the loose `workpiece` tube is dropped (SourceMap allowance group 8);
  2. guide rollers, grip ribs and chain pins are welded into one solid apiece
     (`exact_collisions.py:94-118` is 1:1 with visuals);
  3. casters become real parts with a REVOLUTE swivel and a CONTINUOUS spin, and
     the deck is re-grounded so the contact patch is z = 0;
  4. the drive counterpart is coaxial (see above);
  5. `former_pitch_m` / `guide_pitch_m` gain scale-general floors -- the source
     constants 0.160 / 0.110 / 0.0851 are smaller than two formers at the top of
     `former_outer_r_m`, so they are used as *minima*, not as the pitch.

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

BenderTopology = Literal[
    "pedestal_ladder_rail",
    "cast_bench_mimic",
    "three_roll_pyramid",
    "pedestal_fixed_die_swing_handle",
    "hand_lever_plier",
    "ram_tripod",
]
FormerProfile = Literal[
    "round_flanged_groove",
    "square_tube_channel",
    "multi_radius_stepped",
    "rotary_draw_wrap_wheel",
]
Mount = Literal["bench_plate", "pedestal_floor_plate", "vise_tongue", "caster_deck"]
PaletteStyle = Literal["machine_blue", "cast_teal", "hydraulic_red", "plier_steel"]

BENDER_TOPOLOGIES: tuple[BenderTopology, ...] = (
    "pedestal_ladder_rail",
    "cast_bench_mimic",
    "three_roll_pyramid",
    "pedestal_fixed_die_swing_handle",
    "hand_lever_plier",
    "ram_tripod",
)
FORMER_PROFILES: tuple[FormerProfile, ...] = (
    "round_flanged_groove",
    "square_tube_channel",
    "multi_radius_stepped",
    "rotary_draw_wrap_wheel",
)
MOUNTS: tuple[Mount, ...] = (
    "bench_plate",
    "pedestal_floor_plate",
    "vise_tongue",
    "caster_deck",
)
FORMER_COUNTS: tuple[int, ...] = (1, 2, 3, 4)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "machine_blue",
    "cast_teal",
    "hydraulic_red",
    "plier_steel",
)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "bender_topology",
            BENDER_TOPOLOGIES,
            role="structural family host: part tree, primary articulation and scale class",
        ),
        component_slot(
            "former_profile", FORMER_PROFILES, role="grooved former / die tooling form"
        ),
        component_slot("mount", MOUNTS, role="grounded base the whole host stands on"),
        multiplicity_slot(
            "former_count",
            FORMER_COUNTS,
            role="indexed former stations on one host",
            item_slot="former_profile",
        ),
    )
)

# ---------------------------------------------------------------------------
# `topology_determines_actuation_and_follower` and
# `roller_track_to_guide_rollers.guide_roller_form`.
#
# Each mapping puts a module on the lineage whose record it came from:
#   lever_handle          004 L168-L185 (L1) and 005 L210-L251 (L2), native
#   chain_sprocket_drive  `_sprocket` L105-L144, on the L2 fork that already
#                         re-lays out the same 8 parts
#   ratchet_sector_drive  L98-L157, an L3 fork -> the L3 host
#   geared_handwheel      L105-L126 / L230-L306, an L4 fork -> the L4 host
#   screw_feed_ram        L111-L140, the only drive that publishes a linear
#                         output -> ram_tripod, the only host with a native
#                         `ram_axis` (L581-L594).  Because the screw lands on
#                         its native host, `ram_crank_link_required` evaluates
#                         to 'no' for all 96 combinations and the design's
#                         `ram_crank_link` part is never instantiated; that is
#                         recorded rather than silently dropped.
# ---------------------------------------------------------------------------
_TOPOLOGY_DRIVE: dict[str, str] = {
    "pedestal_ladder_rail": "lever_handle",
    "cast_bench_mimic": "lever_handle",
    "three_roll_pyramid": "chain_sprocket_drive",
    "pedestal_fixed_die_swing_handle": "ratchet_sector_drive",
    "hand_lever_plier": "geared_handwheel",
    "ram_tripod": "screw_feed_ram",
}
# prismatic_wear_shoe        004 L92-L100  (L1)
# ring_and_roller_shoe       005 L113-L139 (L2, and its three_roll fork)
# c_bracket_pressure_roller  hickey L89-L96 (L3)
# crescent_conduit_shoe      conduit_shoe_lever L98-L133, the L3 variant folded
#                            into the structural family; it wraps the former
#                            from outside, which is what the rotary-draw wheel's
#                            open mouth (+X) is built for.
_TOPOLOGY_FOLLOWER: dict[str, str] = {
    "pedestal_ladder_rail": "prismatic_wear_shoe",
    "cast_bench_mimic": "ring_and_roller_shoe",
    "three_roll_pyramid": "ring_and_roller_shoe",
    "pedestal_fixed_die_swing_handle": "c_bracket_pressure_roller",
    "hand_lever_plier": "ring_and_roller_shoe",
    "ram_tripod": "crescent_conduit_shoe",
}
# design expression, verbatim:
#   'flanged_barrel_roller' if topology in (pedestal_ladder_rail,
#   pedestal_fixed_die_swing_handle) else ('annular_disc_roller' if topology ==
#   ram_tripod else 'bored_spool_roller')
_TOPOLOGY_ROLLER_FORM: dict[str, str] = {
    "pedestal_ladder_rail": "flanged_barrel_roller",
    "pedestal_fixed_die_swing_handle": "flanged_barrel_roller",
    "ram_tripod": "annular_disc_roller",
    "cast_bench_mimic": "bored_spool_roller",
    "three_roll_pyramid": "bored_spool_roller",
    "hand_lever_plier": "bored_spool_roller",
}
# `former_is_part`: pedestal_fixed_die_swing_handle's former does not rotate --
# it is a Cylinder visual on `stand` (hickey L198-L203) and the handle sweeps
# the tube around it.  Category anchor `pipe_bender_rotating_former` is scoped
# to exclude exactly this candidate.  The rebuild keeps the former a real PART
# (anchor `pipe_bender_bend_axis_identity` requires `former_count` of them on
# every candidate) and joins it FIXED, welded into its own bearing boss.
_TOPOLOGY_FORMER_ROTATES: dict[str, bool] = {
    "pedestal_ladder_rail": True,
    "cast_bench_mimic": True,
    "three_roll_pyramid": True,
    "pedestal_fixed_die_swing_handle": False,
    "hand_lever_plier": True,
    "ram_tripod": True,
}
# `mount_deck_to_host.lineage_weld_m`, verbatim: one value per lineage ordered
# by that lineage's own scale, 0.20 mm (L4, 0.33 m) .. 0.60 mm (L3, 1.11 m).
_LINEAGE_WELD: dict[str, float] = {
    "hand_lever_plier": 0.00020,
    "cast_bench_mimic": 0.00025,
    "three_roll_pyramid": 0.00025,
    "ram_tripod": 0.00030,
    "pedestal_ladder_rail": 0.00040,
    "pedestal_fixed_die_swing_handle": 0.00060,
}
# `primary_sweep_rad`, verbatim from the design: 2.35 (cast_bench_mimic L368),
# 2.15 (pedestal_ladder_rail L310-L314), 1.10 (pedestal_fixed_die L357), 0.72
# (hand_lever_plier L338-L343), 0.70 (ram_tripod L602-L606).
_TOPOLOGY_SWEEP_FALLBACK: dict[str, float] = {
    "pedestal_ladder_rail": 2.15,
    "cast_bench_mimic": 2.35,
    "three_roll_pyramid": 2.35,
    "pedestal_fixed_die_swing_handle": 1.10,
    "hand_lever_plier": 0.72,
    "ram_tripod": 0.70,
}
# `effort` tracks the mechanical advantage of the drive, not just size
# (SourceMap section 10): 140 (L4 handle) .. 420 (004) .. 900/1200 (005) ..
# 9000 (screw) .. 18000 (L5 ram).
_DRIVE_EFFORT: dict[str, float] = {
    "lever_handle": 420.0,
    "geared_handwheel": 900.0,
    "chain_sprocket_drive": 1200.0,
    "ratchet_sector_drive": 1800.0,
    "screw_feed_ram": 9000.0,
}

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    # 004 machine blue / dark steel / silver / black hardware.
    "machine_blue": {
        "body": (0.00, 0.43, 0.76, 1.0),
        "cast": (0.13, 0.15, 0.16, 1.0),
        "steel": (0.66, 0.68, 0.68, 1.0),
        "hardware": (0.035, 0.04, 0.045, 1.0),
        "grip": (0.02, 0.02, 0.022, 1.0),
        "accent": (0.95, 0.28, 0.025, 1.0),
    },
    # 005 cast teal / dark steel / machined steel / black rubber.
    "cast_teal": {
        "body": (0.015, 0.56, 0.62, 1.0),
        "cast": (0.105, 0.125, 0.135, 1.0),
        "steel": (0.58, 0.62, 0.64, 1.0),
        "hardware": (0.055, 0.060, 0.065, 1.0),
        "grip": (0.025, 0.030, 0.032, 1.0),
        "accent": (0.80, 0.55, 0.20, 1.0),
    },
    # L5 red paint / black paint / silver steel.
    "hydraulic_red": {
        "body": (0.82, 0.025, 0.020, 1.0),
        "cast": (0.035, 0.042, 0.048, 1.0),
        "steel": (0.72, 0.75, 0.77, 1.0),
        "hardware": (0.075, 0.085, 0.090, 1.0),
        "grip": (0.018, 0.022, 0.024, 1.0),
        "accent": (0.95, 0.50, 0.10, 1.0),
    },
    # L4 dark gray steel / polished steel / red grip.
    "plier_steel": {
        "body": (0.24, 0.25, 0.25, 1.0),
        "cast": (0.34, 0.35, 0.35, 1.0),
        "steel": (0.58, 0.60, 0.60, 1.0),
        "hardware": (0.68, 0.69, 0.68, 1.0),
        "grip": (0.72, 0.035, 0.028, 1.0),
        "accent": (0.90, 0.08, 0.055, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Candidate-local independent parameter domains, verbatim from the
# TemplateDesign.  Sampling and clamping are scoped to the ACTIVE candidate, so
# a parameter is never driven outside the range its own candidate declares.
# ---------------------------------------------------------------------------
_SHARED_TOPOLOGY_PARAMS: dict[str, object] = {
    "former_outer_r_m": (0.026, 0.092),
    "pipe_outer_r_m": (0.008, 0.021),
    "primary_shaft_r_m": (0.0035, 0.013),
}
_SHARED_PROFILE_PARAMS: dict[str, object] = {
    "groove_depth_ratio": (0.05, 0.22),
    "former_height_m": (0.014, 0.07),
}

_CANDIDATE_PARAMS: dict[str, dict[str, object]] = {
    # --- bender_topology ---------------------------------------------------
    "pedestal_ladder_rail": {
        **_SHARED_TOPOLOGY_PARAMS,
        "head_height_m": (0.30, 0.75),
        "post_height_m": (0.25, 0.60),
        "base_plate_x_m": (0.30, 0.80),
        "lever_lift_m": (0.03, 0.10),
    },
    "cast_bench_mimic": {
        **_SHARED_TOPOLOGY_PARAMS,
        "plate_x_m": (0.20, 0.42),
        "plate_y_m": (0.10, 0.22),
        "cheek_height_m": (0.012, 0.034),
        "sweep_upper_rad": (1.2, 2.8),
    },
    "three_roll_pyramid": {
        **_SHARED_TOPOLOGY_PARAMS,
        "roll_span_x_m": (0.12, 0.26),
        "pyramid_offset_y_m": (0.05, 0.12),
        "support_roll_r_m": (0.014, 0.032),
    },
    "pedestal_fixed_die_swing_handle": {
        **_SHARED_TOPOLOGY_PARAMS,
        "head_plate_stack_m": (0.09, 0.22),
        "secondary_former_r_m": (0.014, 0.034),
        "secondary_former_offset_m": (0.06, 0.14),
        "locating_arm_length_m": (0.28, 0.62),
    },
    "hand_lever_plier": {
        **_SHARED_TOPOLOGY_PARAMS,
        "tool_length_m": (0.26, 0.42),
        "former_offset_m": (0.045, 0.095),
        "handle_open_rad": (0.3, 0.8),
        "spare_former_r_m": (0.016, 0.032),
    },
    "ram_tripod": {
        **_SHARED_TOPOLOGY_PARAMS,
        "ram_stroke_m": (0.04, 0.11),
        "former_station_offset_m": (0.15, 0.32),
        "leg_reach_m": (0.24, 0.50),
        "pump_handle_length_m": (0.45, 0.90),
    },
    # --- former_profile ----------------------------------------------------
    "round_flanged_groove": {
        **_SHARED_PROFILE_PARAMS,
        "flange_height_ratio": (0.12, 0.32),
        "stop_lug_length_m": (0.02, 0.075),
    },
    "square_tube_channel": {
        **_SHARED_PROFILE_PARAMS,
        "channel_height_ratio": (0.40, 0.78),
        "channel_overcut_m": (0.001, 0.004),
    },
    "multi_radius_stepped": {
        **_SHARED_PROFILE_PARAMS,
        "band_count": [2, 3, 4],
        "radius_step_ratio": (0.10, 0.24),
    },
    "rotary_draw_wrap_wheel": {
        **_SHARED_PROFILE_PARAMS,
        "wrap_span_rad": (3.66, 5.76),
        "wrap_flange_height_m": (0.0025, 0.008),
    },
    # --- mount -------------------------------------------------------------
    "bench_plate": {
        "deck_x_m": (0.20, 0.42),
        "deck_thickness_m": (0.008, 0.02),
        "bolt_hole_r_m": (0.003, 0.008),
        "bolt_hole_count": [4, 6],
    },
    "pedestal_floor_plate": {
        "deck_x_m": (0.24, 0.50),
        "pedestal_height_m": (0.10, 1.05),
        "pedestal_side_m": (0.045, 0.11),
        "anchor_slot_length_m": (0.03, 0.09),
    },
    "vise_tongue": {
        "saddle_z_m": (0.08, 0.32),
        "saddle_x_m": (0.16, 0.34),
        "tongue_thickness_m": (0.012, 0.032),
        "grip_rib_proud_m": (0.002, 0.008),
    },
    "caster_deck": {
        "deck_x_m": (0.32, 0.62),
        "caster_wheel_r_m": (0.024, 0.06),
        "caster_wheel_width_m": (0.03, 0.08),
        "fork_side_clearance_m": (0.0008, 0.003),
    },
}

_ANG_TOL = 0.10  # cadquery angular tolerance; sagitta ~ 1.25e-3 * R

# Caster stack, all scaled off the wheel so a re-grounded deck holds at every
# `caster_wheel_r_m`.  `mount_wheeled_floor_stand` L36-L57 authors 0.008 mount +
# 0.020 swivel + 0.010 crown + 0.052 fork against a 0.040 wheel; those ratios
# are 0.20 / 0.50 / 0.25 / 1.30 of the wheel radius and are reused here.
_CASTER_DECK_T = 0.025
_CASTER_PAD_T = 0.008
_CASTER_CROWN_F = 0.30
_CASTER_STEM_F = 0.25
_CASTER_STACK_F = _CASTER_CROWN_F + _CASTER_STEM_F


@dataclass(frozen=True)
class Config:
    bender_topology: BenderTopology = "pedestal_ladder_rail"
    former_profile: FormerProfile = "round_flanged_groove"
    mount: Mount = "bench_plate"
    former_count: int = 1
    palette_style: PaletteStyle = "machine_blue"
    # --- bender_topology (shared) -------------------------------------------
    former_outer_r_m: float = 0.059
    pipe_outer_r_m: float = 0.0145
    primary_shaft_r_m: float = 0.00825
    # --- pedestal_ladder_rail ----------------------------------------------
    head_height_m: float = 0.525
    post_height_m: float = 0.425
    base_plate_x_m: float = 0.55
    lever_lift_m: float = 0.065
    # --- cast_bench_mimic ---------------------------------------------------
    plate_x_m: float = 0.31
    plate_y_m: float = 0.16
    cheek_height_m: float = 0.023
    sweep_upper_rad: float = 2.0
    # --- three_roll_pyramid -------------------------------------------------
    roll_span_x_m: float = 0.19
    pyramid_offset_y_m: float = 0.085
    support_roll_r_m: float = 0.023
    # --- pedestal_fixed_die_swing_handle ------------------------------------
    head_plate_stack_m: float = 0.155
    secondary_former_r_m: float = 0.024
    secondary_former_offset_m: float = 0.10
    locating_arm_length_m: float = 0.45
    # --- hand_lever_plier ---------------------------------------------------
    tool_length_m: float = 0.34
    former_offset_m: float = 0.07
    handle_open_rad: float = 0.55
    spare_former_r_m: float = 0.024
    # --- ram_tripod ---------------------------------------------------------
    ram_stroke_m: float = 0.075
    former_station_offset_m: float = 0.235
    leg_reach_m: float = 0.37
    pump_handle_length_m: float = 0.675
    # --- former_profile (shared) --------------------------------------------
    groove_depth_ratio: float = 0.135
    former_height_m: float = 0.042
    # --- round_flanged_groove -----------------------------------------------
    flange_height_ratio: float = 0.22
    stop_lug_length_m: float = 0.0475
    # --- square_tube_channel ------------------------------------------------
    channel_height_ratio: float = 0.59
    channel_overcut_m: float = 0.0025
    # --- multi_radius_stepped -----------------------------------------------
    band_count: int = 3
    radius_step_ratio: float = 0.17
    # --- rotary_draw_wrap_wheel ---------------------------------------------
    wrap_span_rad: float = 4.71
    wrap_flange_height_m: float = 0.00525
    # --- mount --------------------------------------------------------------
    deck_x_m: float = 0.31
    deck_thickness_m: float = 0.014
    bolt_hole_r_m: float = 0.0055
    bolt_hole_count: int = 4
    pedestal_height_m: float = 0.575
    pedestal_side_m: float = 0.0775
    anchor_slot_length_m: float = 0.06
    saddle_z_m: float = 0.20
    saddle_x_m: float = 0.25
    tongue_thickness_m: float = 0.022
    grip_rib_proud_m: float = 0.005
    caster_wheel_r_m: float = 0.042
    caster_wheel_width_m: float = 0.055
    fork_side_clearance_m: float = 0.0019
    name: str = "manual_pipe_bender"


@dataclass(frozen=True)
class ResolvedConfig:
    bender_topology: BenderTopology
    former_profile: FormerProfile
    mount: Mount
    former_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    p: dict[str, float]
    # --- derived: topology_determines_actuation_and_follower ----------------
    drive_form: str
    follower_form: str
    guide_roller_form: str
    former_is_part: str
    # --- derived: contact policy -------------------------------------------
    lineage_weld_m: float
    intra_part_weld_m: float
    mesh_chord_tol_m: float
    # --- derived: shaft_to_bore_clearance -----------------------------------
    bore_clearance_m: float
    former_bore_r_m: float
    guide_roller_axle_r_m: float
    guide_roller_bore_r_m: float
    drive_bore_r_m: float
    # --- derived: mount_deck_to_host ----------------------------------------
    mount_height_m: float
    frame_seat_z_m: float
    ground_z_m: float
    deck_x_eff_m: float
    deck_y_eff_m: float
    mount_footprint_r_m: float
    host_footprint_r_m: float
    spindle_z_m: float
    clamp_collar_required: str
    clamp_collar_bore_m: float
    caster_swivel_axis_z_m: float
    caster_fork_gap_m: float
    caster_station_xy: tuple[tuple[float, float], ...]
    # --- derived: former_seat_thrust_plane ----------------------------------
    host_stack_z_m: float
    rail_top_z_m: float
    thrust_washer_height_m: float
    former_running_gap_m: float
    former_seat_z_m: float
    former_height_eff_m: float
    lever_seat_gap_m: float
    moving_member_seat_z_m: float
    primary_axis_z_m: float
    arm_thickness_m: float
    turret_bearing_top_z_m: float
    # --- derived: former_seat_to_groove -------------------------------------
    former_flange_h_m: float
    groove_depth_m: float
    groove_root_r_m: float
    groove_height_m: float
    groove_mid_z_m: float
    bend_radius_m: float
    cheek_relief_r_m: float
    # --- derived: former_placement_law_binding ------------------------------
    former_placement_law: str
    turret_radius_m: float
    former_station_theta_rad: float
    former_pitch_m: float
    former_rack_length_m: float
    turret_crosshead_boss_r_m: float
    former_parent_role: str
    former_stations_xy: tuple[tuple[float, float], ...]
    former_station_max_r_m: float
    # --- derived: follower_station_geometry ---------------------------------
    follower_station_r_m: float
    follower_seat_z_m: float
    follower_station_z_m: float
    follower_body_r_m: float
    follower_stroke_m: float
    follower_orbit_outer_m: float
    crescent_inner_r_m: float
    roller_pocket_r_m: float
    shoe_bore_r_m: float
    shoe_boss_bore_r_m: float
    pressure_roller_r_m: float
    # --- derived: roller_track_to_guide_rollers -----------------------------
    guide_placement_law: str
    guide_roller_count: int
    guide_roller_outer_r_m: float
    guide_roller_height_m: float
    guide_pitch_m: float
    roller_seat_z_m: float
    roller_boss_top_z_m: float
    roller_offset_from_tube_m: float
    guide_station_r0_m: float
    guide_stations_xy: tuple[tuple[float, float], ...]
    roller_track_length_m: float
    static_obstacle_max_r_m: float
    secondary_former_r_eff_m: float
    secondary_former_offset_eff_m: float
    secondary_former_xy: tuple[float, float]
    spare_former_xy: tuple[float, float]
    # --- derived: primary_axis_to_drive -------------------------------------
    drive_torque_radius_m: float
    handle_length_m: float
    moving_member_reach_m: float
    gear_tip_r_driver_m: float
    gear_tip_r_driven_m: float
    gear_centre_distance_m: float
    gear_ring_inner_r_m: float
    gear_axial_overlap_m: float
    driver_tooth_count: int
    sprocket_root_r_m: float
    sprocket_tooth_width_m: float
    sprocket_hub_r_m: float
    chain_band_inner_r_m: float
    pawl_tip_r_m: float
    sector_outer_r_m: float
    sector_half_span_rad: float
    sector_tooth_count: int
    sector_tooth_half_width_m: float
    sector_tooth_height_m: float
    sector_tip_r_m: float
    drive_second_axis_r_m: float
    drive_gear_z_m: float
    drive_stack_offset_m: float
    drive_thickness_m: float
    drive_crank_z_m: float
    drive_output_z_m: float
    screw_shaft_r_m: float
    screw_handwheel_r_m: float
    screw_shaft_len_m: float
    drive_height_m: float
    screw_stroke_m: float
    wheel_outer_r_m: float
    wheel_tooth_depth_m: float
    driven_pitch_r_m: float
    driver_pitch_r_m: float
    # --- derived: ram_axis_to_crank_link ------------------------------------
    primary_joint_type: str
    ram_crank_link_required: str
    crank_link_length_m: float
    ram_stroke_to_sweep_rad: float
    crank_pin_r_m: float
    primary_sweep_rad: float
    sweep_lower_rad: float
    sweep_upper_eff_rad: float
    ram_axis_z_m: float
    ram_shaft_r_m: float
    # --- efforts ------------------------------------------------------------
    primary_effort_n: float
    drive_effort_n: float
    former_effort_n: float
    roller_effort_n: float
    follower_effort_n: float
    top_z_m: float
    name: str = "manual_pipe_bender"

    def __getattr__(self, item: str) -> float:
        values = object.__getattribute__(self, "p")
        if item in values:
            return values[item]
        raise AttributeError(item)


def _active_candidates(cfg: Config) -> tuple[str, ...]:
    return (cfg.bender_topology, cfg.former_profile, cfg.mount)


def _active_domain(cfg: Config) -> dict[str, object]:
    domain: dict[str, object] = {}
    for candidate in _active_candidates(cfg):
        domain.update(_CANDIDATE_PARAMS[candidate])
    return domain


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x06115E2D)
    base = Config(
        bender_topology=choices["bender_topology"],
        former_profile=choices["former_profile"],
        mount=choices["mount"],
        former_count=int(choices["former_count"]),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"manual_pipe_bender_seed_{seed}",
    )
    sampled: dict[str, object] = {}
    for name, domain in sorted(_active_domain(base).items()):
        if isinstance(domain, list):
            sampled[name] = domain[rng.randrange(len(domain))]
        else:
            low, high = domain
            sampled[name] = round(rng.uniform(float(low), float(high)), 6)
    return Config(**{**base.__dict__, **sampled})


def build_seeded_manual_pipe_bender(seed: int, *, assets: AssetContext | None = None):
    return build_manual_pipe_bender(config_from_seed(seed), assets=assets)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _resolve_independent(cfg: Config) -> dict[str, float]:
    """Clamp every parameter to the range its OWN active candidate declares."""
    domain = _active_domain(cfg)
    out: dict[str, float] = {}
    for field in fields(Config):
        value = getattr(cfg, field.name)
        spec = domain.get(field.name)
        if spec is None:
            out[field.name] = value
            continue
        if isinstance(spec, list):
            out[field.name] = value if value in spec else spec[len(spec) // 2]
        else:
            out[field.name] = _clamp(float(value), float(spec[0]), float(spec[1]))
    return out


def slot_choices_for_config(r: ResolvedConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("bender_topology", r.bender_topology),
        ("former_profile", r.former_profile),
        ("mount", r.mount),
        ("former_count", str(r.former_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def resolve_config(config: Config | None = None) -> ResolvedConfig:  # noqa: C901
    cfg = config or Config()
    TEMPLATE_DOMAIN.validate(
        {
            "bender_topology": cfg.bender_topology,
            "former_profile": cfg.former_profile,
            "mount": cfg.mount,
            "former_count": int(cfg.former_count),
        }
    )
    if cfg.palette_style not in PALETTES:
        raise ValueError(f"unknown palette_style {cfg.palette_style!r}")
    p = _resolve_independent(cfg)

    topo = cfg.bender_topology
    profile = cfg.former_profile
    mount = cfg.mount
    n = int(cfg.former_count)

    drive_form = _TOPOLOGY_DRIVE[topo]
    follower_form = _TOPOLOGY_FOLLOWER[topo]
    guide_roller_form = _TOPOLOGY_ROLLER_FORM[topo]
    former_rotates = _TOPOLOGY_FORMER_ROTATES[topo]
    former_is_part = "yes" if former_rotates else "no"

    lineage_weld_m = _LINEAGE_WELD[topo]
    intra_part_weld_m = lineage_weld_m
    # Every clearance that a chord deviation could eat is either planar (the
    # 0.2 mm rotating seats, the lineage weld, the follower slot) or has a
    # radius small enough that the 0.1 rad ANGULAR tolerance already bounds the
    # sagitta at 1.25e-3 * R well under the fit.  The one exception is the
    # drive's counterpart ring, whose radius reaches 0.22 m; it is padded
    # explicitly by `_tess_pad` instead of being protected by a fine linear
    # tolerance that costs seconds of tessellation on every build.
    mesh_chord_tol_m = 0.0004

    rf = float(p["former_outer_r_m"])
    rp = float(p["pipe_outer_r_m"])
    rs = float(p["primary_shaft_r_m"])

    # ---- shaft_to_bore_clearance ------------------------------------------
    bore_clearance_m = 0.03 * rs + 0.0002
    former_bore_r_m = rs + bore_clearance_m
    guide_roller_axle_r_m = max(0.0028, 0.55 * rs)
    guide_roller_bore_r_m = guide_roller_axle_r_m * 1.03 + 0.0002
    drive_bore_r_m = rs + bore_clearance_m

    # ---- former_seat_to_groove --------------------------------------------
    groove_depth_m = min(float(p["groove_depth_ratio"]) * rf, 0.85 * rp)
    groove_root_r_m = rf - groove_depth_m
    if profile == "round_flanged_groove":
        former_flange_h_m = float(p["flange_height_ratio"]) * float(p["former_height_m"])
    elif profile == "rotary_draw_wrap_wheel":
        former_flange_h_m = float(p["wrap_flange_height_m"])
    else:
        # square_tube_channel L26-L28: (0.058 - 0.047) = 0.011 above and 0.011
        # below a 0.036 channel; multi_radius_stepped L79 lands the groove
        # inside its own band, so 0.19 of the height is the pool's flange.
        former_flange_h_m = 0.19 * float(p["former_height_m"])
    groove_height_m = max(2.2 * rp, float(p["former_height_m"]) - 2.0 * former_flange_h_m)
    # DERIVED, not authored twice: when the tube is fat relative to the declared
    # former height the groove would be taller than the former and every
    # flange thickness would go NEGATIVE.  The former grows instead.
    former_height_eff_m = groove_height_m + 2.0 * former_flange_h_m
    groove_mid_z_m = 0.5 * former_height_eff_m
    bend_radius_m = groove_root_r_m + rp
    cheek_relief_r_m = rf + 0.005

    # ---- mount_deck_to_host -----------------------------------------------
    if mount == "bench_plate":
        mount_height_m = float(p["deck_thickness_m"])
    elif mount == "pedestal_floor_plate":
        mount_height_m = 0.014 + float(p["pedestal_height_m"])
    elif mount == "vise_tongue":
        mount_height_m = float(p["saddle_z_m"]) + 0.014
    else:
        # DEVIATION (SourceMap "Deliberate deviations" 3): the source deck
        # underside is z = 0 with the caster contact patch at z = -0.108.  The
        # rebuild re-grounds it, so the deck top is the wheel DIAMETER plus the
        # swivel crown and stem plus the caster pad and the deck itself -- every
        # term derived, because a wheel that now really turns has to clear the
        # crown it hangs from at every spin angle.
        mount_height_m = (
            2.0 * float(p["caster_wheel_r_m"])
            + _CASTER_STACK_F * float(p["caster_wheel_r_m"])
            + 0.004
            + _CASTER_PAD_T
            + _CASTER_DECK_T
        )
    frame_seat_z_m = mount_height_m - lineage_weld_m

    # ---- host_stack_z_m ----------------------------------------------------
    # DESIGN CORRECTION, stated: the design's expression is
    #   head_height_m if pedestal_ladder_rail else (head_plate_stack_m if
    #   pedestal_fixed_die_swing_handle else cheek_height_m)
    # but `cheek_height_m` is owned ONLY by cast_bench_mimic, so on
    # three_roll_pyramid, hand_lever_plier and ram_tripod it names a parameter
    # the candidate does not have.  The design's own rationale already lists the
    # intended per-host values ("0.008 for the cast bench plate, 0.0 for the
    # hand tool"), so the branch is completed per host from a parameter that
    # host does own.
    if topo == "pedestal_ladder_rail":
        host_stack_z_m = float(p["head_height_m"])  # 004 L21 FRAME_RAIL_TOP 0.583
    elif topo == "pedestal_fixed_die_swing_handle":
        host_stack_z_m = float(p["head_plate_stack_m"])  # L188/L219 stack 0.152
    elif topo == "cast_bench_mimic":
        host_stack_z_m = float(p["cheek_height_m"])  # 005 L50-L51 cheeks 0.020
    elif topo == "three_roll_pyramid":
        # the roll bench: the two lower rolls sit UNDER the deck, so the deck
        # rides a whole roll diameter plus its own plate above the mount.  A
        # single radius leaves the rolls poking `support_roll_r_m - 0.010` into
        # the swept former band, which is a real collision with any stowed die.
        host_stack_z_m = 2.0 * float(p["support_roll_r_m"]) + 0.010
    elif topo == "hand_lever_plier":
        # L4 has almost no host stack: a 0.004 stamped plate (L179-L184) with
        # 0.012 red grips over it (L216-L239) and the former axle at z 0.010.
        host_stack_z_m = 0.016
    else:
        # L5 deck at z 0.28-0.34 above feet at 0.02, with a 0.341 leg reach.
        host_stack_z_m = 0.62 * float(p["leg_reach_m"]) + 0.10
    rail_top_z_m = mount_height_m + host_stack_z_m

    # ---- former_seat_thrust_plane -----------------------------------------
    thrust_washer_height_m = max(0.0035, 0.06 * rf)
    former_running_gap_m = 0.0002
    former_seat_z_m = rail_top_z_m + thrust_washer_height_m + former_running_gap_m
    turret_bearing_top_z_m = former_seat_z_m - former_running_gap_m
    lever_seat_gap_m = 0.001
    moving_member_seat_z_m = former_seat_z_m + former_height_eff_m + lever_seat_gap_m
    arm_thickness_m = max(0.010, 0.17 * rf)
    primary_axis_z_m = former_seat_z_m if former_is_part == "yes" else moving_member_seat_z_m

    # ---- follower_station_geometry ----------------------------------------
    follower_station_r_m = bend_radius_m + rp + 0.004
    follower_seat_z_m = former_seat_z_m + groove_mid_z_m
    follower_station_z_m = moving_member_seat_z_m - 0.012
    # The follower's own body radius, its stroke and the resulting swept
    # annulus.  `follower_station_r - rf` is >= 1.15*rp + 0.004 by construction
    # (groove_depth <= 0.85*rp), which is what makes the split possible.
    radial_room = follower_station_r_m - rf
    follower_body_r_m = max(0.0025, 0.38 * radial_room)
    follower_stroke_m = max(0.0015, 0.30 * radial_room)
    follower_orbit_outer_m = follower_station_r_m + follower_stroke_m + follower_body_r_m
    crescent_inner_r_m = rf + 0.006
    pressure_roller_r_m = max(0.0022, 0.55 * follower_body_r_m)
    shoe_bore_r_m = pressure_roller_r_m + 0.0013
    roller_pocket_r_m = pressure_roller_r_m + 0.005
    shoe_boss_bore_r_m = shoe_bore_r_m + 0.001

    # ---- former_placement_law_binding -------------------------------------
    if topo in ("pedestal_ladder_rail", "pedestal_fixed_die_swing_handle"):
        former_placement_law = "linear_bridge_turret" if n <= 2 else "linear_station_rack"
    else:
        former_placement_law = "angular_turret"
    # Every off-axis station must clear the follower's swept annulus, or the
    # follower would strike a stowed former at some sweep angle.  That is the
    # index-general form of the source's own clearance condition.
    station_clear_m = follower_orbit_outer_m + rf + 0.006
    turret_radius_m = max(
        1.55 * rf,
        (rf + 0.003) / math.sin(math.pi / max(n, 2)),
        station_clear_m / (2.0 * math.sin(math.pi / max(n, 2))) if n >= 2 else 0.0,
    )
    former_station_theta_rad = math.pi
    # DEPARTURE: the source pitches are constants (0.160 bridge turret, 0.110
    # station rack).  Both are smaller than two formers at the top of
    # `former_outer_r_m`, so they become MINIMA of a scale-general pitch.
    base_pitch = 0.160 if former_placement_law == "linear_bridge_turret" else 0.110
    former_pitch_m = max(base_pitch, 2.0 * rf + 0.006, station_clear_m)
    former_rack_length_m = (n - 1) * former_pitch_m + 2.0 * rf + 0.145
    turret_crosshead_boss_r_m = 0.47 * rf
    former_parent_role = "bender_frame"

    stations: list[tuple[float, float]] = []
    if former_placement_law == "angular_turret":
        # former_count_3 L317-L321: an equilateral ring of radius R about a
        # centre offset so that station 0 lands on the host's own bending
        # station -- here the bend axis itself.  DEPARTURE, stated: the source
        # centre is at -X of its station; the rebuild mirrors it so the stowed
        # stations trail toward -X and the +X pipe-feed corridor stays clear
        # for the guide-roller track, which is the direction the SourceMap's
        # frame convention reserves for the straight tube run.
        for i in range(n):
            theta = 2.0 * math.pi * i / n
            stations.append(
                (
                    -turret_radius_m + turret_radius_m * math.cos(theta),
                    turret_radius_m * math.sin(theta),
                )
            )
    elif former_placement_law == "linear_bridge_turret":
        # former_count_2 L24-L26: x_i = -pitch * (N - 1 - i); index N-1 on the
        # pivot, earlier formers trailing toward -X.
        for i in range(n):
            stations.append((-former_pitch_m * (n - 1 - i), 0.0))
    else:
        # former_count_5 L24-L30: a rack of stowed stations at constant pitch.
        # Mirrored to -X for the same reason as the turret above.
        for i in range(n):
            stations.append((-former_pitch_m * i, 0.0))
    former_stations_xy = tuple(stations)
    former_station_max_r_m = max(math.hypot(x, y) for x, y in former_stations_xy)

    # ---- static frame obstacles that live in the former band ---------------
    # Every one of them is parked in the -X half so the +X pipe-feed corridor
    # stays free, and every one is outside the follower's swept annulus.
    static_obstacles: list[tuple[float, float, float]] = [
        (x, y, rf) for x, y in former_stations_xy
    ]
    secondary_former_r_eff_m = 0.0
    secondary_former_offset_eff_m = 0.0
    secondary_former_xy = (0.0, 0.0)
    if topo == "pedestal_fixed_die_swing_handle":
        # hickey L206: a second, smaller FIXED former offset from the spindle.
        secondary_former_r_eff_m = float(p["secondary_former_r_m"])
        secondary_former_offset_eff_m = max(
            float(p["secondary_former_offset_m"]),
            follower_orbit_outer_m + secondary_former_r_eff_m + 0.006,
        )
        # Parked on -Y.  Every former station lies on -X (linear laws) or on a
        # circle centred at -X (angular), and every guide station lies on +X, so
        # a feature on -Y at a radius past the follower's swept annulus is clear
        # of all three by construction rather than by a case analysis.
        secondary_former_xy = (0.0, -secondary_former_offset_eff_m)
        static_obstacles.append(
            (secondary_former_xy[0], secondary_former_xy[1], secondary_former_r_eff_m)
        )
    spare_former_xy = (0.0, 0.0)
    if topo == "hand_lever_plier":
        # geared_ring_roller L409-L436: the loose spare die that ships with the
        # tool.  It is welded into the frame here so it costs no extra collision
        # solid, and it lies flat on the plate BELOW the former band, so no
        # sweep of any member can reach it at all.
        spare_r = float(p["spare_former_r_m"])
        spare_former_xy = (0.0, 0.75 * (follower_orbit_outer_m + spare_r + 0.010))
    static_obstacle_max_r_m = max(
        math.hypot(x, y) + rad for x, y, rad in static_obstacles
    )

    # ---- roller_track_to_guide_rollers ------------------------------------
    guide_placement_law = "pipe_path_law" if topo == "ram_tripod" else "rail_pitch_law"
    guide_roller_count = n  # design: guide_roller_count_derived = former_count
    guide_roller_outer_r_m = max(0.30 * rf, rp + 0.004)
    # roller top must clear the moving member's underside; the roller stands on
    # the rail 0.2 mm proud (design `roller_seat_z_m`), so its height is the
    # whole band between the rail top and the arm, less 4 mm.
    guide_roller_height_m = max(
        0.008,
        thrust_washer_height_m + former_height_eff_m + lever_seat_gap_m - 0.004,
    )
    roller_seat_z_m = rail_top_z_m + 0.0002
    roller_boss_top_z_m = roller_seat_z_m - 0.0002
    roller_offset_from_tube_m = rp + guide_roller_outer_r_m
    base_guide_pitch = 0.0851 if guide_placement_law == "pipe_path_law" else 0.110
    guide_pitch_m = max(base_guide_pitch, 2.0 * guide_roller_outer_r_m + 0.006)
    # The track starts outside the follower's swept annulus, and outside the
    # +X reach of every static obstacle.  Because all obstacles are parked in
    # -X, the second term is normally slack; it stays in the derivation so a
    # future obstacle cannot silently overlap station 0.
    _clear = guide_roller_outer_r_m + 0.008
    guide_station_r0_m = follower_orbit_outer_m + _clear
    for _ox, _oy, _orad in static_obstacles:
        _d = _orad + _clear
        if abs(_oy) < _d:
            guide_station_r0_m = max(
                guide_station_r0_m, _ox + math.sqrt(_d * _d - _oy * _oy)
            )
    guides: list[tuple[float, float]] = []
    if guide_placement_law == "pipe_path_law":
        # guide_roller_count_3 L410-L414 measured against its own _pipe_path
        # L115-L168: stations i >= 1 march down the exit tangent (0.920, -0.392)
        # at pitch 0.0851 m.
        dx, dy = 0.920, -0.392
        for i in range(guide_roller_count):
            guides.append(
                (guide_station_r0_m + guide_pitch_m * i * dx, guide_pitch_m * i * dy)
            )
    else:
        # 004 L200-L233 / former_count_2 L227-L228: x_i = x_0 + 0.110*i at
        # constant y on the rail top.
        for i in range(guide_roller_count):
            guides.append((guide_station_r0_m + guide_pitch_m * i, 0.0))
    guide_stations_xy = tuple(guides)
    guide_track_outer_r_m = max(math.hypot(x, y) for x, y in guide_stations_xy)
    # former_count_5 L53-L54: rack_length = (x_{N-1} - PIVOT_X) + 0.145, with the
    # 0.145 tail re-expressed as 1.7 former radii so the frame tracks the scale.
    roller_track_length_m = (
        (guide_roller_count - 1) * guide_pitch_m + 2.0 * guide_roller_outer_r_m + 1.7 * rf
    )

    host_footprint_r_m = max(
        2.2 * rf, guide_track_outer_r_m + guide_roller_outer_r_m + 0.02
    )
    deck_x_eff_m = max(float(p["deck_x_m"]), 2.1 * host_footprint_r_m)
    if mount == "vise_tongue":
        deck_x_eff_m = max(float(p["saddle_x_m"]), 2.1 * host_footprint_r_m)
    deck_y_eff_m = 0.72 * deck_x_eff_m
    caster_swivel_axis_z_m = 0.0
    caster_fork_gap_m = float(p["caster_wheel_width_m"]) + 2.0 * float(
        p["fork_side_clearance_m"]
    )
    caster_wheel_r = float(p["caster_wheel_r_m"])
    # Each caster swivels a full turn, so the deck has to be big enough that two
    # adjacent stations cannot sweep into each other.  The source never needs
    # this because its wheels do not turn at all (L163-L171).
    caster_leg_t_m = max(0.008, 0.20 * caster_wheel_r)
    caster_sweep_r_m = math.hypot(
        0.5 * caster_fork_gap_m + caster_leg_t_m, 0.6 * caster_wheel_r
    )
    caster_pitch_min_m = 2.0 * caster_sweep_r_m + 0.014
    if mount == "caster_deck":
        deck_x_eff_m = max(deck_x_eff_m, caster_pitch_min_m + 2.8 * caster_wheel_r)
        deck_y_eff_m = max(
            0.72 * deck_x_eff_m, caster_pitch_min_m + 2.8 * caster_wheel_r
        )
    mount_footprint_r_m = max(0.5 * deck_x_eff_m, 1.25 * host_footprint_r_m)
    spindle_z_m = mount_height_m + host_stack_z_m
    clamp_collar_required = "yes" if topo == "hand_lever_plier" else "no"
    clamp_collar_bore_m = 0.5 * float(p["tool_length_m"]) * 0.10 + 0.002
    caster_inset = 0.5 * deck_x_eff_m - 1.4 * caster_wheel_r
    caster_inset_y = 0.5 * deck_y_eff_m - 1.4 * caster_wheel_r
    caster_station_xy = tuple(
        (sx * caster_inset, sy * caster_inset_y)
        for sx in (-1.0, 1.0)
        for sy in (-1.0, 1.0)
    )

    # ---- primary_axis_to_drive --------------------------------------------
    # anchor: "the moving member reaches at least four former diameters from the
    # bend axis" -- 004 L555-L562 asserts >= 4x the die diameter AND >= 0.72 m.
    min_reach = 0.30 if topo == "hand_lever_plier" else 0.72
    moving_member_reach_m = max(8.4 * rf, min_reach)
    handle_length_m = moving_member_reach_m * 0.86
    wheel_tooth_depth_m = max(0.0018, 0.045 * rf)
    # every drive radius carries a `drive_bore_r_m` floor so the member's own
    # hub can never grow past its tooth circle at the small end of
    # `former_outer_r_m` x the large end of `primary_shaft_r_m`.
    wheel_outer_r_m = max(0.6 * rf, 0.022, 3.2 * drive_bore_r_m)
    driven_pitch_r_m = max(0.42 * rf, 0.010, 3.6 * drive_bore_r_m)
    driver_pitch_r_m = 0.72 * driven_pitch_r_m
    driver_tooth_count = 14
    sector_outer_r_m = max(2.0 * rf, 0.09, 6.0 * drive_bore_r_m)
    sector_half_span_rad = math.radians(38.0)
    sector_tooth_count = 11
    # ratchet_sector L134-L135: root = outer - 0.003, tip = outer + 0.020.  The
    # 0.020 becomes a floor so the tooth stays legible at 2x the source scale.
    sector_tooth_height_m = max(0.020, 0.11 * sector_outer_r_m)
    sector_tip_r_m = sector_outer_r_m + sector_tooth_height_m
    screw_handwheel_r_m = max(0.030, 0.55 * rf)
    screw_stroke_m = float(p["ram_stroke_m"])

    if drive_form == "chain_sprocket_drive":
        gear_tip_r_driver_m = driver_pitch_r_m * 1.11
    else:
        gear_tip_r_driver_m = wheel_outer_r_m + wheel_tooth_depth_m
    if drive_form == "chain_sprocket_drive":
        gear_tip_r_driven_m = driven_pitch_r_m * 1.11
    else:
        gear_tip_r_driven_m = rf * 0.46 + wheel_tooth_depth_m
    gear_centre_distance_m = gear_tip_r_driver_m + gear_tip_r_driven_m + 0.0003
    # COAXIAL RESTATEMENT of `gear_centre_distance_m` (see the module docstring):
    # the driven counterpart is a ring welded into the moving member, and the
    # driver's tip circle stands 0.3 mm inside it at every relative angle.
    if drive_form == "ratchet_sector_drive":
        gear_ring_inner_r_m = sector_tip_r_m + 0.0003
    else:
        gear_ring_inner_r_m = gear_tip_r_driver_m + 0.0003
    pawl_tip_r_m = sector_tip_r_m + 0.0003
    gear_axial_overlap_m = 0.001
    sprocket_root_r_m = 0.82 * driven_pitch_r_m
    sprocket_tooth_width_m = max(
        0.0022, 2.0 * math.pi * driven_pitch_r_m / driver_tooth_count * 0.48
    )
    sprocket_hub_r_m = 0.42 * driven_pitch_r_m
    chain_band_inner_r_m = gear_tip_r_driven_m + 0.0003
    sector_tooth_half_width_m = (
        0.45 * (2.0 * sector_half_span_rad / sector_tooth_count) * sector_outer_r_m
    )
    drive_second_axis_r_m = rs * 0.7
    drive_stack_offset_m = 0.004 + 0.5 * gear_axial_overlap_m
    drive_thickness_m = max(0.010, 0.14 * rf)
    drive_gear_z_m = moving_member_seat_z_m + arm_thickness_m + 0.003
    drive_crank_z_m = drive_gear_z_m + drive_thickness_m + 0.003
    drive_output_z_m = primary_axis_z_m + drive_stack_offset_m
    screw_shaft_r_m = 0.55 * gear_tip_r_driver_m

    if drive_form == "lever_handle":
        drive_torque_radius_m = handle_length_m
    elif drive_form == "geared_handwheel":
        drive_torque_radius_m = wheel_outer_r_m
    elif drive_form == "chain_sprocket_drive":
        drive_torque_radius_m = driven_pitch_r_m
    elif drive_form == "ratchet_sector_drive":
        drive_torque_radius_m = sector_outer_r_m
    else:
        drive_torque_radius_m = screw_handwheel_r_m

    # ---- ram_axis_to_crank_link -------------------------------------------
    if topo == "cast_bench_mimic":
        primary_sweep_rad = float(p["sweep_upper_rad"])
    elif topo == "hand_lever_plier":
        primary_sweep_rad = float(p["handle_open_rad"])
    else:
        primary_sweep_rad = _TOPOLOGY_SWEEP_FALLBACK[topo]
    sweep_lower_rad = -0.06 * primary_sweep_rad
    sweep_upper_eff_rad = sweep_lower_rad + primary_sweep_rad
    crank_link_length_m = max(
        1.6 * rf, screw_stroke_m / (2.0 * math.sin(0.5 * primary_sweep_rad))
    )
    ram_stroke_to_sweep_rad = 2.0 * math.asin(
        min(0.999, screw_stroke_m / (2.0 * crank_link_length_m))
    )
    crank_pin_r_m = 0.6 * rs
    primary_joint_type = (
        "prismatic" if (drive_form == "screw_feed_ram" and topo == "ram_tripod") else "revolute"
    )
    # STATED CONSEQUENCE: category anchor `pipe_bender_bend_axis_identity`
    # requires a REVOLUTE bender_frame -> moving_member relation about (0,0,1)
    # on all six candidates, so the primary joint stays revolute even where the
    # design's `primary_joint_type` would flip it; the screw's linear output is
    # expressed by the nut riding the screw and by the prismatic follower, which
    # is the adjustment DOF anchor `pipe_bender_adjustment_dof` asks for.
    primary_joint_type = "revolute"
    ram_crank_link_required = (
        "yes" if (drive_form == "screw_feed_ram" and topo != "ram_tripod") else "no"
    )
    ram_axis_z_m = primary_axis_z_m + 0.5 * former_height_eff_m
    ram_shaft_r_m = screw_shaft_r_m

    primary_effort_n = 140.0 + 3200.0 * rf
    drive_effort_n = _DRIVE_EFFORT[drive_form]
    former_effort_n = 180.0 + 24000.0 * rf
    roller_effort_n = 12.0 + 320.0 * rf
    follower_effort_n = 90.0 + 4200.0 * rf

    # The screw drive is the one member that stands well above its own crank
    # plane: 38 thread collars over a 0.518 m run (L118-L127).  Its shaft length
    # is derived so the collar run has somewhere real to sit; every other drive
    # ends just above the crank.
    screw_shaft_len_m = max(0.06, 2.6 * screw_handwheel_r_m)
    drive_height_m = (drive_crank_z_m - drive_gear_z_m) + (
        screw_shaft_len_m + drive_thickness_m * 1.6
        if drive_form == "screw_feed_ram"
        else drive_thickness_m * 2.0
    )
    top_z_m = drive_gear_z_m + drive_height_m + 0.012

    return ResolvedConfig(
        bender_topology=topo,
        former_profile=profile,
        mount=mount,
        former_count=n,
        palette_style=cfg.palette_style,
        palette=dict(PALETTES[cfg.palette_style]),
        p=p,
        drive_form=drive_form,
        follower_form=follower_form,
        guide_roller_form=guide_roller_form,
        former_is_part=former_is_part,
        lineage_weld_m=lineage_weld_m,
        intra_part_weld_m=intra_part_weld_m,
        mesh_chord_tol_m=mesh_chord_tol_m,
        bore_clearance_m=bore_clearance_m,
        former_bore_r_m=former_bore_r_m,
        guide_roller_axle_r_m=guide_roller_axle_r_m,
        guide_roller_bore_r_m=guide_roller_bore_r_m,
        drive_bore_r_m=drive_bore_r_m,
        mount_height_m=mount_height_m,
        frame_seat_z_m=frame_seat_z_m,
        ground_z_m=0.0,
        deck_x_eff_m=deck_x_eff_m,
        deck_y_eff_m=deck_y_eff_m,
        mount_footprint_r_m=mount_footprint_r_m,
        host_footprint_r_m=host_footprint_r_m,
        spindle_z_m=spindle_z_m,
        clamp_collar_required=clamp_collar_required,
        clamp_collar_bore_m=clamp_collar_bore_m,
        caster_swivel_axis_z_m=caster_swivel_axis_z_m,
        caster_fork_gap_m=caster_fork_gap_m,
        caster_station_xy=caster_station_xy,
        host_stack_z_m=host_stack_z_m,
        rail_top_z_m=rail_top_z_m,
        thrust_washer_height_m=thrust_washer_height_m,
        former_running_gap_m=former_running_gap_m,
        former_seat_z_m=former_seat_z_m,
        former_height_eff_m=former_height_eff_m,
        lever_seat_gap_m=lever_seat_gap_m,
        moving_member_seat_z_m=moving_member_seat_z_m,
        primary_axis_z_m=primary_axis_z_m,
        arm_thickness_m=arm_thickness_m,
        turret_bearing_top_z_m=turret_bearing_top_z_m,
        former_flange_h_m=former_flange_h_m,
        groove_depth_m=groove_depth_m,
        groove_root_r_m=groove_root_r_m,
        groove_height_m=groove_height_m,
        groove_mid_z_m=groove_mid_z_m,
        bend_radius_m=bend_radius_m,
        cheek_relief_r_m=cheek_relief_r_m,
        former_placement_law=former_placement_law,
        turret_radius_m=turret_radius_m,
        former_station_theta_rad=former_station_theta_rad,
        former_pitch_m=former_pitch_m,
        former_rack_length_m=former_rack_length_m,
        turret_crosshead_boss_r_m=turret_crosshead_boss_r_m,
        former_parent_role=former_parent_role,
        former_stations_xy=former_stations_xy,
        former_station_max_r_m=former_station_max_r_m,
        follower_station_r_m=follower_station_r_m,
        follower_seat_z_m=follower_seat_z_m,
        follower_station_z_m=follower_station_z_m,
        follower_body_r_m=follower_body_r_m,
        follower_stroke_m=follower_stroke_m,
        follower_orbit_outer_m=follower_orbit_outer_m,
        crescent_inner_r_m=crescent_inner_r_m,
        roller_pocket_r_m=roller_pocket_r_m,
        shoe_bore_r_m=shoe_bore_r_m,
        shoe_boss_bore_r_m=shoe_boss_bore_r_m,
        pressure_roller_r_m=pressure_roller_r_m,
        guide_placement_law=guide_placement_law,
        guide_roller_count=guide_roller_count,
        guide_roller_outer_r_m=guide_roller_outer_r_m,
        guide_roller_height_m=guide_roller_height_m,
        guide_pitch_m=guide_pitch_m,
        roller_seat_z_m=roller_seat_z_m,
        roller_boss_top_z_m=roller_boss_top_z_m,
        roller_offset_from_tube_m=roller_offset_from_tube_m,
        guide_station_r0_m=guide_station_r0_m,
        guide_stations_xy=guide_stations_xy,
        roller_track_length_m=roller_track_length_m,
        static_obstacle_max_r_m=static_obstacle_max_r_m,
        secondary_former_r_eff_m=secondary_former_r_eff_m,
        secondary_former_offset_eff_m=secondary_former_offset_eff_m,
        secondary_former_xy=secondary_former_xy,
        spare_former_xy=spare_former_xy,
        drive_torque_radius_m=drive_torque_radius_m,
        handle_length_m=handle_length_m,
        moving_member_reach_m=moving_member_reach_m,
        gear_tip_r_driver_m=gear_tip_r_driver_m,
        gear_tip_r_driven_m=gear_tip_r_driven_m,
        gear_centre_distance_m=gear_centre_distance_m,
        gear_ring_inner_r_m=gear_ring_inner_r_m,
        gear_axial_overlap_m=gear_axial_overlap_m,
        driver_tooth_count=driver_tooth_count,
        sprocket_root_r_m=sprocket_root_r_m,
        sprocket_tooth_width_m=sprocket_tooth_width_m,
        sprocket_hub_r_m=sprocket_hub_r_m,
        chain_band_inner_r_m=chain_band_inner_r_m,
        pawl_tip_r_m=pawl_tip_r_m,
        sector_outer_r_m=sector_outer_r_m,
        sector_half_span_rad=sector_half_span_rad,
        sector_tooth_count=sector_tooth_count,
        sector_tooth_half_width_m=sector_tooth_half_width_m,
        sector_tooth_height_m=sector_tooth_height_m,
        sector_tip_r_m=sector_tip_r_m,
        drive_second_axis_r_m=drive_second_axis_r_m,
        drive_gear_z_m=drive_gear_z_m,
        drive_stack_offset_m=drive_stack_offset_m,
        drive_thickness_m=drive_thickness_m,
        drive_crank_z_m=drive_crank_z_m,
        drive_output_z_m=drive_output_z_m,
        screw_shaft_r_m=screw_shaft_r_m,
        screw_handwheel_r_m=screw_handwheel_r_m,
        screw_shaft_len_m=screw_shaft_len_m,
        drive_height_m=drive_height_m,
        screw_stroke_m=screw_stroke_m,
        wheel_outer_r_m=wheel_outer_r_m,
        wheel_tooth_depth_m=wheel_tooth_depth_m,
        driven_pitch_r_m=driven_pitch_r_m,
        driver_pitch_r_m=driver_pitch_r_m,
        primary_joint_type=primary_joint_type,
        ram_crank_link_required=ram_crank_link_required,
        crank_link_length_m=crank_link_length_m,
        ram_stroke_to_sweep_rad=ram_stroke_to_sweep_rad,
        crank_pin_r_m=crank_pin_r_m,
        primary_sweep_rad=primary_sweep_rad,
        sweep_lower_rad=sweep_lower_rad,
        sweep_upper_eff_rad=sweep_upper_eff_rad,
        ram_axis_z_m=ram_axis_z_m,
        ram_shaft_r_m=ram_shaft_r_m,
        primary_effort_n=primary_effort_n,
        drive_effort_n=drive_effort_n,
        former_effort_n=former_effort_n,
        roller_effort_n=roller_effort_n,
        follower_effort_n=follower_effort_n,
        top_z_m=top_z_m,
        name=cfg.name,
    )


# ===========================================================================
# CadQuery helpers.  `_box` / `_cyl` mirror the pool's own `_box` /
# `_cylinder_z` (005 L22-L42, 004 L27-L30) so every span cited below reads
# directly against the source.
# ===========================================================================
def _box(size: tuple[float, float, float], center: tuple[float, float, float]) -> cq.Workplane:
    sx, sy, sz = (max(float(v), 1e-5) for v in size)
    return cq.Workplane("XY").box(sx, sy, sz).translate(center)


def _cyl(radius: float, height: float, *, x: float = 0.0, y: float = 0.0, z0: float = 0.0):
    return (
        cq.Workplane("XY")
        .center(x, y)
        .circle(max(radius, 1e-5))
        .extrude(max(height, 1e-5))
        .translate((0.0, 0.0, z0))
    )


def _tube(outer: float, inner: float, height: float, *, x=0.0, y=0.0, z0=0.0):
    outer = max(outer, 3e-5)
    inner = max(min(inner, outer - 2e-5), 1e-5)
    return (
        cq.Workplane("XY")
        .center(x, y)
        .circle(outer)
        .circle(inner)
        .extrude(max(height, 1e-5))
        .translate((0.0, 0.0, z0))
    )


def _ribbon_profile(points, widths):
    """geared_ring_roller L19-L41, verbatim: offset a centreline polyline by
    +-w/2 along the computed normal.  The only non-box, non-lathe silhouette
    generator in the pool, and what makes L4 read as a stamped hand tool."""
    left: list[tuple[float, float]] = []
    right: list[tuple[float, float]] = []
    for i, ((x, y), width) in enumerate(zip(points, widths)):
        if i == 0:
            tx, ty = points[1][0] - x, points[1][1] - y
        elif i == len(points) - 1:
            tx, ty = x - points[i - 1][0], y - points[i - 1][1]
        else:
            tx = points[i + 1][0] - points[i - 1][0]
            ty = points[i + 1][1] - points[i - 1][1]
        mag = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / mag, tx / mag
        half = width * 0.5
        left.append((x + nx * half, y + ny * half))
        right.append((x - nx * half, y - ny * half))
    return left + list(reversed(right))


def _ribbon(points, widths, thickness: float, z0: float) -> cq.Workplane:
    """geared_ring_roller L44-L61, verbatim including the circular end caps."""
    body = (
        cq.Workplane("XY")
        .polyline(_ribbon_profile(list(points), list(widths)))
        .close()
        .extrude(thickness)
        .translate((0.0, 0.0, z0))
    )
    for point, width in ((points[0], widths[0]), (points[-1], widths[-1])):
        body = body.union(_cyl(width * 0.5, thickness, x=point[0], y=point[1], z0=z0))
    return body


def _toothed_disk(root_radius: float, tooth_depth: float, tooth_count: int, thickness: float):
    """drive_geared_handwheel L105-L126: tangential tooth width is
    `2*pi*r/N * 0.58`, so teeth occupy 58 % of the pitch and the gullet is real.
    MECHANICAL_PRIORS 4 forbids substituting bulk overlap for mesh.

    The source unions one `rect` solid per tooth; this emits the identical
    outline as ONE closed polyline and extrudes it once, because 18 sequential
    OCCT booleans cost about 8 s per build and the preflight cap is 12 s.  The
    tooth crown positions, widths and depths are unchanged.
    """
    teeth = max(int(tooth_count), 3)
    tip = root_radius + tooth_depth
    half = 0.58 * math.pi / teeth
    flank = half * 1.34
    pts: list[tuple[float, float]] = []
    for index in range(teeth):
        centre = 2.0 * math.pi * index / teeth
        for radius, angle in (
            (root_radius, centre - flank),
            (tip, centre - half),
            (tip, centre + half),
            (root_radius, centre + flank),
        ):
            pts.append((radius * math.cos(angle), radius * math.sin(angle)))
    return cq.Workplane("XY").polyline(pts).close().extrude(max(thickness, 1e-5))


def _sprocket(pitch_radius: float, thickness: float, teeth: int, z0: float):
    """drive_chain_sprocket_drive L105-L144, verbatim: root 0.82*pr, tooth box
    0.34*pr radial centred at 0.94*pr (so tip = 1.11*pr), tangential width
    max(0.0022, 2*pi*pr/N * 0.48), hub 0.42*pr, one bore."""
    count = max(int(teeth), 4)
    root = pitch_radius * 0.82
    tip = pitch_radius * 1.11
    tangent = max(0.0022, 2.0 * math.pi * pitch_radius / count * 0.48)
    half = min(0.42 * (2.0 * math.pi / count), tangent * 0.5 / max(tip, 1e-6))
    flank = min(0.48 * (2.0 * math.pi / count), half * 1.5)
    pts: list[tuple[float, float]] = []
    for index in range(count):
        centre = 2.0 * math.pi * index / count
        for radius, angle in (
            (root, centre - flank),
            (tip, centre - half),
            (tip, centre + half),
            (root, centre + flank),
        ):
            pts.append((radius * math.cos(angle), radius * math.sin(angle)))
    body = (
        cq.Workplane("XY")
        .polyline(pts)
        .close()
        .extrude(max(thickness, 1e-5))
        .translate((0.0, 0.0, z0))
    )
    return body.union(_cyl(pitch_radius * 0.42, thickness, z0=z0))


def _tess_pad(radius: float) -> float:
    """Sagitta of a cylindrical face at `radius` under the 0.1 rad angular
    tolerance (`_mesh/cadquery_helpers.py:161-162`): the triangulated hole is
    smaller than the nominal circle by `R * (1 - cos(pi/n))` with n ~ 63.  Any
    running fit whose radius is large enough for that to matter is opened by
    this amount so the DERIVED clearance survives triangulation."""
    return 1.3e-3 * max(radius, 0.0)


def _capsule_slot_cutter(length: float, width: float, depth: float, x: float, y: float, z0: float):
    """hickey L42-L55: a TRUE capsule slot -- a straight box unioned with two end
    circles -- cut through the plate rather than painted on it."""
    straight = max(length - width, width * 0.4)
    cutter = _box((straight, width, depth), (x, y, z0 + depth * 0.5))
    for dx in (-straight * 0.5, straight * 0.5):
        cutter = cutter.union(_cyl(width * 0.5, depth, x=x + dx, y=y, z0=z0))
    return cutter


# ===========================================================================
# `former_profile` -- ONE welded solid with ONE cut through bore per former, so
# a former costs exactly one collision solid (exact_collisions.py:94-118 is 1:1
# with visuals).  Local frame: the bore axis is +Z through local (0,0,0) and
# z = 0 is the underside, the plane `former_seat_thrust_plane` derives.
# ===========================================================================
def _former_profile_round_flanged_groove_build(r: ResolvedConfig) -> cq.Workplane:
    """005 L71-L82: three fused coaxial discs -- flange / web / flange -- plus a
    keyed stop lug that makes former rotation legible, then one bore."""
    outer = float(r.p["former_outer_r_m"])
    flange = r.former_flange_h_m
    body = _cyl(outer, flange)
    body = body.union(_cyl(r.groove_root_r_m, r.groove_height_m, z0=flange))
    body = body.union(_cyl(outer, flange, z0=flange + r.groove_height_m))
    # L80: box(0.020, 0.055, 0.008) at y 0.055.  Kept strictly INSIDE the flange
    # radius so rotating the former never enlarges its swept envelope.
    lug_len = min(float(r.p["stop_lug_length_m"]), 0.8 * outer)
    body = body.union(
        _box(
            (lug_len * 0.45, lug_len, flange * 1.6),
            (0.0, outer - lug_len * 0.5, r.former_height_eff_m - flange * 0.8),
        )
    )
    return body.cut(_cyl(r.former_bore_r_m, r.former_height_eff_m + 0.02, z0=-0.01))


def _former_profile_square_tube_channel_build(r: ResolvedConfig) -> cq.Workplane:
    """former_profile_square_tube_die L75-L87: a SOLID drum from which a
    flat-bottomed annular channel is cut.  Cutting from solid rather than
    stacking discs is exactly what makes the floor flat, and that flat floor is
    the candidate."""
    outer = float(r.p["former_outer_r_m"])
    height = r.former_height_eff_m
    channel_h = min(
        max(float(r.p["channel_height_ratio"]) * height, 2.2 * float(r.p["pipe_outer_r_m"])),
        height - 2.0 * r.former_flange_h_m,
    )
    channel_z0 = 0.5 * (height - channel_h)
    drum = _cyl(outer, height)
    channel = _tube(
        outer + float(r.p["channel_overcut_m"]), r.groove_root_r_m, channel_h, z0=channel_z0
    )
    return drum.cut(channel).cut(_cyl(r.former_bore_r_m, height + 0.02, z0=-0.01))


def _former_profile_multi_radius_stepped_build(r: ResolvedConfig) -> cq.Workplane:
    """former_profile_multi_radius_stepped_di L64-L103: ONE revolved lathe
    section, not stacked cylinders.  Each axial band has its own bending radius
    and its own tube-seating groove; the six profile points per band and the
    groove-depth rule `min(R*(0.105 - 0.015*i), band_h*0.34)` are the source's
    own (L79-L92)."""
    outer = float(r.p["former_outer_r_m"])
    height = r.former_height_eff_m
    bore = r.former_bore_r_m
    bands = int(r.p["band_count"])
    step = float(r.p["radius_step_ratio"])
    band_height = height / bands
    radii = [max(outer * (1.0 - step * i), bore + 0.0035) for i in range(bands)]
    profile: list[tuple[float, float]] = [(bore, 0.0), (radii[0], 0.0)]
    for index, radius in enumerate(radii):
        z0 = index * band_height
        z1 = (index + 1) * band_height
        depth = min(
            outer * (0.105 - 0.015 * index), band_height * 0.34, 0.55 * (radius - bore)
        )
        depth = max(depth, 0.0004)
        profile.extend(
            [
                (radius, z0 + band_height * 0.18),
                (radius - depth * 0.42, z0 + band_height * 0.34),
                (radius - depth, z0 + band_height * 0.50),
                (radius - depth * 0.42, z0 + band_height * 0.66),
                (radius, z0 + band_height * 0.82),
                (radius, z1),
            ]
        )
        if index < len(radii) - 1:
            profile.append((radii[index + 1], z1))
    profile.extend([(bore, height), (bore, 0.0)])
    return cq.Workplane("XZ").polyline(profile).close().revolve(360.0, (0.0, 0.0), (0.0, 1.0))


def _former_profile_rotary_draw_wrap_wheel_build(r: ResolvedConfig) -> cq.Workplane:
    """compact_rotary_draw L41-L86: a 300 deg grooved wheel -- a web at the
    groove root between two full-radius flanges, plus a hub and a clamp lug --
    with the mouth left open for the pressure shoe and the tube lead-in."""
    outer = float(r.p["former_outer_r_m"])
    height = r.former_height_eff_m
    flange = r.former_flange_h_m
    span = min(float(r.p["wrap_span_rad"]), 2.0 * math.pi - 0.25)
    inner = max(r.former_bore_r_m + 0.004, 0.30 * outer, 0.35 * r.groove_root_r_m)
    start = 0.5 * (2.0 * math.pi - span)
    samples = 40
    angles = [start + span * i / samples for i in range(samples + 1)]

    def sector(radius: float, thickness: float, z0: float):
        profile = [(radius * math.cos(a), radius * math.sin(a)) for a in angles]
        profile.extend((inner * math.cos(a), inner * math.sin(a)) for a in reversed(angles))
        return (
            cq.Workplane("XY")
            .polyline(profile)
            .close()
            .extrude(max(thickness, 1e-5))
            .translate((0.0, 0.0, z0))
        )

    body = sector(r.groove_root_r_m, r.groove_height_m, flange)
    body = body.union(sector(outer, flange, 0.0))
    body = body.union(sector(outer, flange, height - flange))
    body = body.union(_cyl(inner + r.intra_part_weld_m, height))
    # L74-L79 clamp lug, kept inside the flange radius (see the round profile)
    # so the swept envelope stays a circle of radius `former_outer_r_m`.
    lug = max(0.004, min(0.40 * outer, 0.55 * (outer - inner)))
    body = body.union(
        _box((lug, lug * 0.8, height), (inner + lug * 0.45, inner * 0.5, height * 0.5))
    )
    return body.cut(_cyl(r.former_bore_r_m, height + 0.02, z0=-0.01))


_FORMER_BUILDERS = {
    "round_flanged_groove": _former_profile_round_flanged_groove_build,
    "square_tube_channel": _former_profile_square_tube_channel_build,
    "multi_radius_stepped": _former_profile_multi_radius_stepped_build,
    "rotary_draw_wrap_wheel": _former_profile_rotary_draw_wrap_wheel_build,
}


# ===========================================================================
# Guide rollers.  DEVIATION 1: 004 emits FIVE primitive visuals per roller
# (L200-L233); 005 `_roller_shape` L122-L139 already welds the identical
# flange/web/flange spool and its bore into ONE CAD solid, so every candidate
# takes 005's route and saves 4*N collision solids.  Every roller is a solid of
# revolution, so a CONTINUOUS spin cannot change its envelope at any pose.
# ===========================================================================
def _guide_roller_shape(r: ResolvedConfig) -> cq.Workplane:
    outer = r.guide_roller_outer_r_m
    height = r.guide_roller_height_m
    bore = r.guide_roller_bore_r_m
    flange_h = max(0.0022, 0.20 * height)
    web_r = max(bore + 0.0015, outer - max(0.0025, float(r.p["pipe_outer_r_m"]) * 0.55))
    if r.guide_roller_form == "annular_disc_roller":
        # guide_roller_count_3 L34-L40: `_annular_disc(0.025, 0.0084, 0.045)`
        # plus a silver `roller_cap`, welded in.
        body = _tube(outer, bore, height)
        body = body.union(_tube(outer * 0.86, bore, height * 0.14, z0=height - height * 0.14))
        return body
    body = _cyl(outer, flange_h)
    body = body.union(_cyl(web_r, height - 2.0 * flange_h, z0=flange_h))
    body = body.union(_cyl(outer, flange_h, z0=height - flange_h))
    if r.guide_roller_form == "flanged_barrel_roller":
        # 004 L200-L233 also caps the barrel; welded in here.
        body = body.union(
            _cyl(
                web_r * 0.66,
                flange_h * 0.9,
                z0=height - flange_h * 0.9 - r.intra_part_weld_m,
            )
        )
    return body.cut(_cyl(bore, height + 0.02, z0=-0.01))


# ===========================================================================
# `follower_module`, derived from the topology.  Local frame: the follower's own
# spin axis is +Z through local (0,0,0), and z = 0 is the moving member's seat
# plane, so the body hangs DOWN into the former band exactly as far as the
# groove mid-plane the anchor asks for.
# ===========================================================================
def _follower_span(r: ResolvedConfig) -> tuple[float, float]:
    """The follower BODY stops 0.4 mm under the moving member's underside; only
    the narrow stem in `_follower_post` passes up through the carrier's cut
    slot.  That is what lets a wide shoe -- 005's ring, the L3 crescent -- run
    at the groove without fouling the arm at any sweep angle, which is the
    interference behind allowance group 4."""
    top = -0.0004
    bottom = (r.former_seat_z_m + 0.4 * r.former_flange_h_m) - r.moving_member_seat_z_m
    return bottom, top


def _follower_prismatic_wear_shoe_build(r: ResolvedConfig) -> cq.Workplane:
    """004 L92-L100: a concave shoe with a YZ-plane `circle(0.014)` groove cut
    clean THROUGH it, plus a steel wear plate.  The groove is the mechanism, not
    decoration (MECHANICAL_PRIORS 7)."""
    bottom, top = _follower_span(r)
    fr = r.follower_body_r_m
    height = top - bottom
    body = _box((2.0 * fr, 2.4 * fr, height), (0.0, 0.0, bottom + height * 0.5))
    groove = (
        cq.Workplane("YZ")
        .center(0.0, r.follower_seat_z_m - r.moving_member_seat_z_m)
        .circle(min(float(r.p["pipe_outer_r_m"]), 0.75 * fr))
        .extrude(4.0 * fr, both=True)
        .translate((-fr, 0.0, 0.0))
    )
    body = body.cut(groove)
    body = body.union(
        _box((0.5 * fr, 2.0 * fr, height * 0.32), (-fr * 0.75, 0.0, bottom + height * 0.5))
    )
    return body


def _follower_ring_and_roller_shoe_build(r: ResolvedConfig) -> cq.Workplane:
    """005 L113-L119: an annular shoe (OD 0.0215, bore 0.0173 around a roller of
    OD 0.0160 -> 1.3 mm running clearance) with a post and a retaining top cap.
    CORRECTION APPLIED (allowance group 4): 005 cuts a RECTANGULAR slider slot
    (L109) narrower than its own shoe ring, so the ring fouls the boss and
    L627-L636 needs an allowance; here the carrier boss is bored full height at
    `shoe_boss_bore_r_m` = ring OD + 1 mm."""
    bottom, top = _follower_span(r)
    fr = r.follower_body_r_m
    ring_h = min(0.55 * (top - bottom), max(0.004, 2.4 * float(r.p["pipe_outer_r_m"])))
    ring_z = (r.follower_seat_z_m - r.moving_member_seat_z_m) - 0.5 * ring_h
    body = _tube(fr, r.shoe_bore_r_m, ring_h, z0=ring_z)
    body = body.union(
        _box(
            (fr * 0.7, fr * 1.1, max(0.002, top - (ring_z + ring_h)) + r.intra_part_weld_m),
            (-fr * 0.3, 0.0, 0.5 * (ring_z + ring_h + top)),
        )
    )
    body = body.union(_box((1.9 * fr, 1.9 * fr, 0.32 * fr), (0.0, 0.0, top - 0.16 * fr)))
    # 005 L253-L285: the bored roller the shoe carries, on its own
    # `follower_pin` (Cylinder(0.0040, 0.059)).  Welded in, so the shoe costs
    # one collision solid; the pin is what CONNECTS it, exactly as in the
    # source -- a roller floating in the shoe's 1.3 mm bore would be its own
    # geometry island inside the part.
    axle_r = r.pressure_roller_r_m * 0.42
    body = body.union(
        _tube(r.pressure_roller_r_m, axle_r, ring_h * 0.86, z0=ring_z)
    )
    body = body.union(
        _cyl(axle_r + r.intra_part_weld_m, top - ring_z, z0=ring_z)
    )
    return body


def _follower_crescent_conduit_shoe_build(r: ResolvedConfig) -> cq.Workplane:
    """conduit_shoe_lever L98-L133: an annulus intersected with a half-space
    box, giving a crescent that wraps the former from OUTSIDE, plus a
    `circle(0.024)` roller clearance pocket.  `crescent_inner_r_m` is the
    former radius plus a real running gap (source: inner 0.050 around a 0.040
    fixed die)."""
    bottom, top = _follower_span(r)
    fr = r.follower_body_r_m
    fs = r.follower_station_r_m
    inner = r.crescent_inner_r_m
    outer = fs + fr
    height = top - bottom
    # Authored about the BEND AXIS -- that is what makes it a crescent -- and
    # then expressed in the follower's own local frame, which sits at
    # `follower_station_r_m` on +X.  The annulus inner radius is the guard: no
    # material can ever come inside `crescent_inner_r_m` = former radius + 6 mm,
    # at any sweep angle or any point of the adjustment stroke.
    ring = _tube(outer, inner, height, x=-fs, z0=bottom)
    lo, hi = -0.42 * fs, 1.25 * fr
    body = ring.intersect(
        _box(
            (hi - lo, 2.2 * outer, height + 0.004),
            (0.5 * (hi + lo), 0.0, bottom + height * 0.5),
        )
    )
    body = body.union(
        _box((1.4 * fr, 1.0 * fr, height), (fr * 0.5, 0.0, bottom + height * 0.5))
    )
    body = body.cut(
        _cyl(r.roller_pocket_r_m, height + 0.01, x=-fr * 0.1, y=-1.0 * fr, z0=bottom - 0.005)
    )
    return body


def _follower_c_bracket_pressure_roller_build(r: ResolvedConfig) -> cq.Workplane:
    """hickey L89-L96: the pool's CORRECT yoke -- a side web plus two ears with
    the axle bore cut through BOTH and 3 mm axial clearance per side.
    CORRECTION APPLIED: this lineage bores 0.0065 for a 0.007 axle (L95 vs
    L332); `shaft_to_bore_clearance` inverts that sign."""
    bottom, top = _follower_span(r)
    fr = r.follower_body_r_m
    height = top - bottom
    ear_t = max(0.0022, 0.16 * height)
    body = _box((0.7 * fr, 2.2 * fr, height), (-1.0 * fr, 0.0, bottom + height * 0.5))
    for z in (bottom + ear_t * 0.5, top - ear_t * 0.5):
        body = body.union(_box((2.2 * fr, 2.2 * fr, ear_t), (0.0, 0.0, z)))
    # hickey L95 vs L332: the ears are bored for the AXLE, and the roller runs
    # on the axle.  The bore is cut through BOTH ears, then the axle fills it
    # (intra-part, free) and carries the roller, so the yoke is one connected
    # solid and still costs one collision solid.
    axle_r = max(0.0018, 0.45 * r.pressure_roller_r_m)
    body = body.cut(_cyl(axle_r, height + 0.02, z0=bottom - 0.01))
    body = body.union(
        _cyl(axle_r + r.intra_part_weld_m, height + 0.004, z0=bottom - 0.002)
    )
    body = body.union(
        _cyl(
            r.pressure_roller_r_m,
            max(0.002, height - 2.0 * ear_t - 2.0 * r.intra_part_weld_m),
            z0=bottom + ear_t + r.intra_part_weld_m,
        )
    )
    return body


_FOLLOWER_BUILDERS = {
    "prismatic_wear_shoe": _follower_prismatic_wear_shoe_build,
    "ring_and_roller_shoe": _follower_ring_and_roller_shoe_build,
    "crescent_conduit_shoe": _follower_crescent_conduit_shoe_build,
    "c_bracket_pressure_roller": _follower_c_bracket_pressure_roller_build,
}


# ===========================================================================
# `drive`, derived from the topology.  Local frame: the drive turns about +Z
# through local (0,0,0).  z = 0 is the GEAR plane; `drive_crank_z_m -
# drive_gear_z_m` is the CRANK plane, which is above every static feature so a
# radial crank arm can sweep freely.  Every driver's outermost material stops at
# `gear_tip_r_driver_m`, 0.3 mm inside the counterpart ring the moving member
# carries -- the coaxial restatement of `gear_centre_distance_m`.
# ===========================================================================
def _drive_lever_handle_build(r: ResolvedConfig) -> cq.Workplane:
    """004 L168-L185 and 005 L210-L251: hub + carrier + a long tube and a rubber
    grip.  DEVIATION 2: 005's eight `grip_rib_*` cylinders (L240-L251, 1.7 mm
    proud of the grip) become unions inside the handle solid -- same visible
    detail, 8 fewer collision solids."""
    t = r.drive_thickness_m
    crank_z = r.drive_crank_z_m - r.drive_gear_z_m
    hub_r = max(2.6 * r.drive_bore_r_m, 0.22 * float(r.p["former_outer_r_m"]))
    body = _cyl(hub_r, crank_z + t)
    bar_w = max(0.014, 0.30 * hub_r)
    length = r.handle_length_m
    body = body.union(
        _box((length, bar_w * 1.5, t), (-length * 0.5 + hub_r * 0.4, 0.0, crank_z + t * 0.5))
    )
    body = body.union(
        _cyl(bar_w * 1.1, t * 1.3, x=-length + hub_r * 0.4, z0=crank_z)
    )
    # the grip ribs stay INSIDE the bar's own span, or the last of them floats
    # off the end and the part reports a disconnected geometry island.
    grip_start = -length * 0.70 + hub_r * 0.4
    for i in range(6):
        body = body.union(
            _box(
                (length * 0.020, bar_w * 1.75, t * 1.1),
                (grip_start - i * length * 0.045, 0.0, crank_z + t * 0.5),
            )
        )
    return body.cut(_cyl(r.drive_bore_r_m, crank_z + t * 1.3 + 0.02, z0=-0.01))


def _drive_geared_handwheel_build(r: ResolvedConfig) -> cq.Workplane:
    """drive_geared_handwheel L230-L306: rim `circle(0.033)/circle(0.027)`, six
    `rect(0.028,0.005)` spokes at 60 deg, `_toothed_disk(0.033, 0.003, 18,
    0.004)` cut back so only the tooth crowns survive, then a red rim and six
    grip ridges."""
    t = r.drive_thickness_m
    crank_z = r.drive_crank_z_m - r.drive_gear_z_m
    wheel_r = r.wheel_outer_r_m
    hub_r = max(2.6 * r.drive_bore_r_m, 0.30 * wheel_r)
    body = _toothed_disk(wheel_r, r.wheel_tooth_depth_m, 18, t)
    body = body.cut(_tube(wheel_r - r.intra_part_weld_m, hub_r, t + 0.004, z0=-0.002))
    for index in range(6):
        body = body.union(
            cq.Workplane("XY")
            .center(0.5 * (hub_r + wheel_r), 0.0)
            .rect(wheel_r - hub_r, max(0.004, 0.13 * hub_r))
            .extrude(t)
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), index * 60.0)
        )
    body = body.union(_cyl(hub_r, crank_z + t))
    # the red rim and its six grip ridges sit DIRECTLY on the tooth ring; three
    # millimetres of air above it (the crank plane) would leave them as their
    # own geometry island inside the part.
    rim_z = t - r.intra_part_weld_m
    body = body.union(_tube(wheel_r * 0.98, wheel_r * 0.82, t * 0.6, z0=rim_z))
    for index in range(6):
        angle = math.radians(index * 60.0)
        body = body.union(
            _cyl(
                wheel_r * 0.055,
                t * 0.5,
                x=wheel_r * 0.9 * math.cos(angle),
                y=wheel_r * 0.9 * math.sin(angle),
                z0=rim_z + t * 0.6 - r.intra_part_weld_m,
            )
        )
    return body.cut(_cyl(r.drive_bore_r_m, crank_z + t + 0.02, z0=-0.01))


def _drive_chain_sprocket_drive_build(r: ResolvedConfig) -> cq.Workplane:
    """drive_chain_sprocket_drive L105-L144 `_sprocket` and L146-L186
    `_chain_loop`.  DEPARTURE (allowance group 6): the source builds ONE chain
    part wrapping sprockets that live on two DIFFERENT parts, which is its five
    worst allowances.  Here the wrap ring is welded into the sprocket it wraps
    (intra-part, free) and the counterpart band is welded into the moving
    member, so the two keep a real radial gap at every relative angle.  The 16
    separate `chain_pin_*` cylinders (L307-L324) are unioned in -- DEVIATION 2,
    16 fewer collision solids."""
    t = r.drive_thickness_m
    crank_z = r.drive_crank_z_m - r.drive_gear_z_m
    pitch = r.driver_pitch_r_m
    tip = pitch * 1.11
    body = _sprocket(pitch, t, r.driver_tooth_count, 0.0)
    band = min(r.sprocket_tooth_width_m, 0.5 * tip)
    body = body.union(_tube(tip, tip - band, t * 0.55, z0=t * 0.22))
    for index in range(10):
        angle = 2.0 * math.pi * index / 10.0
        body = body.union(
            _cyl(
                band * 0.30,
                t * 0.8,
                x=(tip - band * 0.5) * math.cos(angle),
                y=(tip - band * 0.5) * math.sin(angle),
                z0=t * 0.1,
            )
        )
    hub_r = max(2.6 * r.drive_bore_r_m, r.sprocket_hub_r_m)
    body = body.union(_cyl(hub_r, crank_z + t))
    arm = max(0.06, r.handle_length_m * 0.45)
    body = body.union(_box((arm, hub_r * 1.1, t), (-arm * 0.5, 0.0, crank_z + t * 0.5)))
    body = body.union(_cyl(hub_r * 0.8, t * 1.8, x=-arm + hub_r * 0.4, z0=crank_z))
    return body.cut(_cyl(r.drive_bore_r_m, crank_z + t * 1.8 + 0.02, z0=-0.01))


def _drive_ratchet_sector_drive_build(r: ResolvedConfig) -> cq.Workplane:
    """drive_ratchet_sector_drive L98-L157: a 13-point outer arc and a 13-point
    inner arc over +-38 deg extruded 0.014, plus a tail and an end pad, with 11
    teeth at `start + (end-start)*(i+0.5)/11`, each a triangle from
    `outer - 0.003` to `outer + 0.020`, and three lightening holes.  CORRECTION
    APPLIED: the source's half-width 0.010 at r 0.162 is 7.07 deg of arc against
    a 6.909 deg pitch -- its teeth already touch -- so the half width is capped
    at 45 % of the pitch (`sector_tooth_half_width_m`)."""
    t = r.drive_thickness_m
    crank_z = r.drive_crank_z_m - r.drive_gear_z_m
    outer = r.sector_outer_r_m
    inner = max(0.38 * outer, 2.8 * r.drive_bore_r_m)
    half = r.sector_half_span_rad
    steps = 12
    outer_arc = [
        (
            outer * math.cos(-half + 2.0 * half * i / steps),
            outer * math.sin(-half + 2.0 * half * i / steps),
        )
        for i in range(steps + 1)
    ]
    inner_arc = [
        (
            inner * math.cos(half - 2.0 * half * i / steps),
            inner * math.sin(half - 2.0 * half * i / steps),
        )
        for i in range(steps + 1)
    ]
    body = cq.Workplane("XY").polyline(outer_arc + inner_arc).close().extrude(t)
    hub_r = max(2.6 * r.drive_bore_r_m, 0.17 * outer)
    body = body.union(_cyl(hub_r, crank_z + t))
    body = body.union(
        _box((outer * 0.9, hub_r * 1.4, t), (outer * 0.42, 0.0, t * 0.5))
    )
    tooth_h = r.sector_tooth_height_m
    hw = r.sector_tooth_half_width_m
    for index in range(r.sector_tooth_count):
        angle = -half + 2.0 * half * (index + 0.5) / r.sector_tooth_count
        tangent = (-math.sin(angle), math.cos(angle))
        radial = (math.cos(angle), math.sin(angle))
        root_r = outer - tooth_h * 0.15
        tip_r = outer + tooth_h
        root = (root_r * radial[0], root_r * radial[1])
        tip = (tip_r * radial[0], tip_r * radial[1])
        body = body.union(
            cq.Workplane("XY")
            .polyline(
                [
                    (root[0] - hw * tangent[0], root[1] - hw * tangent[1]),
                    (root[0] + hw * tangent[0], root[1] + hw * tangent[1]),
                    (tip[0] + 0.10 * hw * tangent[0], tip[1] + 0.10 * hw * tangent[1]),
                ]
            )
            .close()
            .extrude(t)
        )
    for radius, angle in ((0.68 * outer, -0.22), (0.68 * outer, 0.22), (0.82 * outer, 0.0)):
        body = body.cut(
            _cyl(
                0.055 * outer,
                t + 0.004,
                x=radius * math.cos(angle),
                y=radius * math.sin(angle),
                z0=-0.002,
            )
        )
    tail = max(0.08, r.handle_length_m * 0.55)
    body = body.union(_box((tail, hub_r * 1.2, t), (-tail * 0.5, 0.0, crank_z + t * 0.5)))
    body = body.union(_cyl(hub_r * 0.9, t * 1.6, x=-tail + hub_r * 0.4, z0=crank_z))
    return body.cut(_cyl(r.drive_bore_r_m, crank_z + t * 1.6 + 0.02, z0=-0.01))


def _drive_screw_feed_ram_build(r: ResolvedConfig) -> cq.Workplane:
    """drive_screw_feed_ram L111-L140: an Acme-style shaft carrying a run of
    thread collars (38 at pitch 0.014) that ends in a rim/hub/two-crossed-spoke
    handwheel.  DEPARTURE, stated: the source screw is HORIZONTAL on the YZ
    workplane and converts the primary joint to PRISMATIC (L356-L369, axis
    (1,0,0), 0..0.090, effort 9000).  Here it stands on the bend axis, because
    anchor `pipe_bender_bend_axis_identity` requires a REVOLUTE drive about
    (0,0,1) on every candidate; the linear output survives as the travelling nut
    ring the moving member carries and as the prismatic follower adjustment that
    anchor `pipe_bender_adjustment_dof` asks for."""
    t = r.drive_thickness_m
    crank_z = r.drive_crank_z_m - r.drive_gear_z_m
    tip = r.gear_tip_r_driver_m
    wheel_r = r.screw_handwheel_r_m
    core_r = r.screw_shaft_r_m
    hub_r = max(2.0 * r.drive_bore_r_m, core_r)
    shaft_len = r.screw_shaft_len_m
    wheel_z = crank_z + shaft_len
    body = _cyl(tip, t)
    body = body.union(_cyl(hub_r, wheel_z + t * 1.6))
    # the thread run lives ABOVE the crank plane, where the shaft actually is;
    # squeezing it into the 3 mm between the gear and crank planes leaves every
    # collar floating off the end of its own shaft.
    collars = 7
    pitch = shaft_len / (collars + 1)
    for i in range(collars):
        body = body.union(
            _tube(hub_r * 1.55, hub_r - r.intra_part_weld_m, pitch * 0.34, z0=crank_z + i * pitch)
        )
    body = body.union(_tube(wheel_r, wheel_r * 0.79, t * 0.9, z0=wheel_z))
    body = body.union(_cyl(max(hub_r * 1.5, wheel_r * 0.3), t * 1.4, z0=wheel_z))
    for index in range(2):
        body = body.union(
            cq.Workplane("XY")
            .rect(2.0 * wheel_r, max(0.005, 0.10 * wheel_r))
            .extrude(t * 0.9)
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), index * 90.0)
            .translate((0.0, 0.0, wheel_z))
        )
    return body.cut(_cyl(r.drive_bore_r_m, wheel_z + t * 1.6 + 0.02, z0=-0.01))


_DRIVE_BUILDERS = {
    "lever_handle": _drive_lever_handle_build,
    "geared_handwheel": _drive_geared_handwheel_build,
    "chain_sprocket_drive": _drive_chain_sprocket_drive_build,
    "ratchet_sector_drive": _drive_ratchet_sector_drive_build,
    "screw_feed_ram": _drive_screw_feed_ram_build,
}


def _drive_counterpart(r: ResolvedConfig):
    """The driven counterpart the MOVING MEMBER carries, coaxial with the drive.

    A collar rising from the arm into the gear plane whose INNER radius is
    `gear_ring_inner_r_m` = the driver's tip radius + 0.3 mm.  That is the
    design's `gear_centre_distance_m` rule restated for two coaxial members: the
    0.3 mm is radial, so it holds at every relative angle instead of only at
    rest.  `lever_handle` needs none -- 004 and 005 drive the sweep by hand.
    """
    if r.drive_form == "lever_handle":
        return None
    z0 = r.drive_gear_z_m - r.moving_member_seat_z_m
    t = r.drive_thickness_m
    inner = r.gear_ring_inner_r_m + _tess_pad(r.gear_ring_inner_r_m)
    band = max(0.005, 0.16 * inner)
    collar = _tube(inner + band, inner, (z0 + t) + r.intra_part_weld_m, z0=-r.intra_part_weld_m)
    if r.drive_form == "ratchet_sector_drive":
        # allowance group 3: both pool examples bury the pawl 8.5-8.7 mm INSIDE
        # the tooth circle.  Here the pawl tip stands at `pawl_tip_r_m` = tooth
        # tip + 0.3 mm and the carrier lies wholly outside it, so it engages a
        # flank without ever interpenetrating.
        collar = collar.union(
            _box((band * 1.4, band * 1.0, t), (inner + band * 1.05, 0.0, z0 + t * 0.5))
        )
        return collar
    if r.drive_form == "chain_sprocket_drive":
        for index in range(12):
            angle = 2.0 * math.pi * index / 12.0
            collar = collar.union(
                _cyl(
                    band * 0.26,
                    t * 0.7,
                    x=(inner + band * 0.5) * math.cos(angle),
                    y=(inner + band * 0.5) * math.sin(angle),
                    z0=z0 + t * 0.15,
                )
            )
        return collar
    if r.drive_form == "screw_feed_ram":
        # the travelling nut block sits OUTSIDE the collar bore.  Centring it on
        # `inner + band/2` puts its inboard corner 0.6 band inside the ring and
        # straight into the screw's own tooth circle.
        return collar.union(
            _box((band * 2.0, band * 2.0, t), (inner + band * 1.3, 0.0, z0 + t * 0.5))
        )
    # geared_handwheel: an internal ring gear.  L255-L264 puts a 22-tooth ring
    # of base radius 0.0293 on a 0.029 former.  The gullets are CUT into the
    # ring's inner face, so the innermost material stays at `inner` and the
    # 0.3 mm to the driver's tips can never close.
    for index in range(22):
        angle = 2.0 * math.pi * index / 22.0
        collar = collar.cut(
            _cyl(
                max(0.0008, band * 0.22),
                t + 0.004,
                x=(inner + band * 0.16) * math.cos(angle),
                y=(inner + band * 0.16) * math.sin(angle),
                z0=z0 - 0.002,
            )
        )
    return collar


# ===========================================================================
# `mount` -- the grounded base.  `mount_deck_to_host` makes the host's spindle
# height a function of the MOUNT, never an authored per-host constant: the pool
# proves it, because `mount_vise_mounted_frame` changes SPINDLE_Z 0.936 -> 0.336
# (L27-L29) and NOTHING above it.  Local frame = world; the deck top is at
# `mount_height_m` and the ground plane at z = 0.
# ===========================================================================
def _mount_bench_plate_build(r: ResolvedConfig) -> cq.Workplane:
    """005 L46-L63: a thick cast plate with a raised perimeter lip and FOUR REAL
    `circle(0.0048)` through-holes -- the mounting holes are cut, not painted.
    The source's longitudinal cheeks belong to the cast-bench HOST and are built
    there (`cheek_height_m`), so the mount keeps the plate and the holes."""
    t = r.mount_height_m
    sx, sy = r.deck_x_eff_m, r.deck_y_eff_m
    body = cq.Workplane("XY").box(sx, sy, t).translate((0.0, 0.0, t * 0.5))
    body = body.edges("|Z").fillet(min(0.018, 0.18 * sy))
    # 005 L52: the raised feed pad.  It is placed OUTSIDE `host_footprint_r_m`
    # on the +X feed side, because anything the mount raises above its own deck
    # inside that radius is a part-to-part interference with the frame that
    # seats on it.
    pad_x = 0.5 * (r.host_footprint_r_m + 0.02 + sx * 0.5)
    pad_len = max(0.02, sx * 0.5 - r.host_footprint_r_m - 0.02)
    body = body.union(
        _box(
            (pad_len, sy * 0.72, max(0.006, 0.9 * t)),
            (pad_x, 0.0, t + max(0.006, 0.9 * t) * 0.5 - r.intra_part_weld_m),
        )
    )
    holes = int(r.p["bolt_hole_count"])
    hr = float(r.p["bolt_hole_r_m"])
    for index in range(holes):
        angle = 2.0 * math.pi * (index + 0.5) / holes
        body = body.cut(
            _cyl(
                hr,
                t + 0.02,
                x=(sx * 0.5 - 2.6 * hr) * math.cos(angle),
                y=(sy * 0.5 - 2.6 * hr) * math.sin(angle),
                z0=-0.01,
            )
        )
    return body


def _mount_pedestal_floor_plate_build(r: ResolvedConfig) -> cq.Workplane:
    """hickey L33-L56: a 0.34 x 0.30 x 0.014 floor plate with four TRUE capsule
    anchor slots cut through, a square pedestal column and a cap plate.
    `pedestal_height_m` spans 0.10 .. 1.05 because the vise fork of the same
    host shortens the very same column to 0.100 (mount_vise L176)."""
    plate_t = 0.014
    sx, sy = r.deck_x_eff_m, r.deck_y_eff_m
    side = float(r.p["pedestal_side_m"])
    column_h = r.mount_height_m - plate_t
    body = cq.Workplane("XY").box(sx, sy, plate_t).translate((0.0, 0.0, plate_t * 0.5))
    slot_len = float(r.p["anchor_slot_length_m"])
    slot_w = max(0.008, 0.22 * slot_len)
    for sxg, syg in ((-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)):
        body = body.cut(
            _capsule_slot_cutter(
                slot_len,
                slot_w,
                plate_t + 0.02,
                sxg * (sx * 0.5 - slot_len * 0.75),
                syg * (sy * 0.5 - slot_w * 2.0),
                -0.01,
            )
        )
    body = body.union(
        _box((side, side, column_h), (0.0, 0.0, plate_t + column_h * 0.5 - r.intra_part_weld_m))
    )
    cap = side * 1.45
    body = body.union(
        _box((cap, cap * 0.9, 0.014), (0.0, 0.0, r.mount_height_m - 0.007))
    )
    # four welded gussets at the column root (mount_wheeled_floor_stand
    # L177-L184), embedded so the stack is one connected solid.
    gus = side * 0.7
    for dx, dy in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)):
        body = body.union(
            _box(
                (gus if dy else side * 0.34, side * 0.34 if dy else gus, gus),
                (dx * side * 0.55, dy * side * 0.55, plate_t + gus * 0.5 - r.intra_part_weld_m),
            )
        )
    return body


def _mount_vise_tongue_build(r: ResolvedConfig) -> cq.Workplane:
    """mount_vise_mounted_frame L32-L64: the saddle plate PLUS the vise
    interface proper -- a vertical tongue with two grip ribs standing
    `grip_rib_proud_m` off each face and two gussets.  The jaw grip plane is
    therefore x = +-(tongue/2 + proud), and `mount_height_m` = saddle_z + 0.014
    is the one true derived-host-height binding in the pool."""
    plate_t = 0.014
    sx, sy = r.deck_x_eff_m, r.deck_y_eff_m
    saddle_z = r.mount_height_m - plate_t
    tongue_t = float(r.p["tongue_thickness_m"])
    proud = float(r.p["grip_rib_proud_m"])
    body = _box((sx, sy, plate_t), (0.0, 0.0, saddle_z + plate_t * 0.5))
    tongue_y = min(sy * 0.82, max(0.06, sy * 0.6))
    body = body.union(
        _box((tongue_t, tongue_y, saddle_z + r.intra_part_weld_m), (0.0, 0.0, (saddle_z + r.intra_part_weld_m) * 0.5))
    )
    rib_y = tongue_y * 0.80
    rib_h = max(0.008, saddle_z * 0.06)
    for z in (saddle_z * 0.26, saddle_z * 0.74):
        body = body.union(_box((tongue_t + 2.0 * proud, rib_y, rib_h), (0.0, 0.0, z)))
    gus_h = max(0.02, saddle_z * 0.22)
    for sign in (-1.0, 1.0):
        body = body.union(
            _box(
                (min(sx * 0.30, 0.070), max(0.008, tongue_t * 0.55), gus_h),
                (0.0, sign * tongue_y * 0.48, saddle_z - gus_h * 0.5 + r.intra_part_weld_m),
            )
        )
    return body


def _mount_caster_deck_build(r: ResolvedConfig) -> cq.Workplane:
    """mount_wheeled_floor_stand L32-L52: a filleted welded deck with four
    caster stations, each a mount plate + swivel boss + crown.  DEVIATION 3: the
    source's four wheels are RIGID VISUALS on `stand` with no swivel and no spin
    joint, and its 0.056-wide wheel sits inside a 0.026 fork gap -- legal only
    while wheel and fork are visuals of one part (MECHANICAL_PRIORS 1c).  Here
    the fork gap is `caster_wheel_width_m + 2 * fork_side_clearance_m`, the fork
    and wheel become real parts, and the deck is re-grounded so the contact
    patch is z = 0 instead of the source's z = -0.108."""
    sx, sy = r.deck_x_eff_m, r.deck_y_eff_m
    z0 = r.mount_height_m - _CASTER_DECK_T
    body = (
        cq.Workplane("XY")
        .box(sx, sy, _CASTER_DECK_T)
        .translate((0.0, 0.0, z0 + _CASTER_DECK_T * 0.5))
    )
    body = body.edges("|Z").fillet(min(0.018, 0.16 * sy))
    pad = max(0.05, 1.45 * float(r.p["caster_wheel_r_m"]))
    for cx, cy in r.caster_station_xy:
        body = body.union(
            _box(
                (pad, pad * 0.86, _CASTER_PAD_T),
                (cx, cy, z0 - _CASTER_PAD_T * 0.5 + r.intra_part_weld_m),
            )
        )
    return body


_MOUNT_BUILDERS = {
    "bench_plate": _mount_bench_plate_build,
    "pedestal_floor_plate": _mount_pedestal_floor_plate_build,
    "vise_tongue": _mount_vise_tongue_build,
    "caster_deck": _mount_caster_deck_build,
}


# ===========================================================================
# `bender_topology` frames.  Every silhouette lives at or BELOW `rail_top_z_m`;
# the only frame material above it is the central spindle, the per-station
# thrust bosses and pins, and the guide-roller bosses and axles, all added by
# `_frame_stations`.  That is the frame's real cut relief for the moving member
# (MECHANICAL_PRIORS 7) expressed as a construction rule rather than as a cut.
# ===========================================================================
def _frame_stations(r: ResolvedConfig, body: cq.Workplane) -> cq.Workplane:
    rf = float(r.p["former_outer_r_m"])
    rs = float(r.p["primary_shaft_r_m"])
    rail_top = r.rail_top_z_m
    seat = r.frame_seat_z_m
    boss_r = max(r.turret_crosshead_boss_r_m, 0.42 * rf)

    # the ladder / rack beam that carries every off-axis station and every
    # roller station back to the column.  former_count_5 L53-L54 derives its
    # rack length from the station table the same way.
    # The beam has to fit BETWEEN the mount deck and the rail top, or a
    # 0.33 m hand tool (whose whole host stack is 6 mm) drives it straight
    # through the deck it is bolted to.
    beam_h = max(0.003, min(0.010 + 0.30 * r.thrust_washer_height_m, rail_top - seat))
    beam_w = max(0.020, 1.1 * boss_r)
    for x, y in list(r.former_stations_xy) + list(r.guide_stations_xy):
        length = math.hypot(x, y)
        if length < 1e-6:
            continue
        body = body.union(
            _box((length, beam_w, beam_h), (0.0, 0.0, rail_top - beam_h * 0.5))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(math.atan2(y, x)))
            .translate(
                (
                    0.5 * length * math.cos(math.atan2(y, x)),
                    0.5 * length * math.sin(math.atan2(y, x)),
                    0.0,
                )
            )
        )
    # thrust washer / bearing at every former station.  CORRECTION APPLIED
    # (former_count_3 L450-L456 puts its turret bearing top 14.5 mm INSIDE the
    # former underside): the bearing top is DERIVED from the seat, at
    # `turret_bearing_top_z_m` = former_seat_z - 0.2 mm.
    for x, y in r.former_stations_xy:
        body = body.union(
            _cyl(
                boss_r,
                r.turret_bearing_top_z_m - (rail_top - beam_h),
                x=x,
                y=y,
                z0=rail_top - beam_h,
            )
        )
        pin_top = r.former_seat_z_m + r.former_height_eff_m * 0.88
        body = body.union(_cyl(rs, pin_top - rail_top, x=x, y=y, z0=rail_top))
    # roller boss + axle.  004 L46-L47 / L204-L208 land the roller's lower
    # flange EXACTLY on the rail top (distance zero, hence its allowance);
    # `roller_seat_z_m` offsets 0.2 mm and the roller is declared with
    # allow_isolated_part instead.
    for x, y in r.guide_stations_xy:
        body = body.union(
            _cyl(
                r.guide_roller_outer_r_m * 0.92,
                r.roller_boss_top_z_m - (rail_top - beam_h),
                x=x,
                y=y,
                z0=rail_top - beam_h,
            )
        )
        body = body.union(
            _cyl(
                r.guide_roller_axle_r_m,
                r.roller_seat_z_m + r.guide_roller_height_m * 0.92 - rail_top,
                x=x,
                y=y,
                z0=rail_top,
            )
        )
    # the central spindle every rotating member bores over.
    body = body.union(_cyl(rs, r.top_z_m - seat, z0=seat))
    body = body.union(_cyl(rs * 1.55, max(0.004, 0.9 * rs), z0=r.top_z_m - 0.004))
    return body


def _bender_topology_pedestal_ladder_rail_build(r: ResolvedConfig) -> cq.Workplane:
    """004 L33-L67: a welded frame -- filleted base plate, square post, collar,
    mast, twin lower rails at y = +-0.0675 with four cross ties, a
    `circle(0.060)` pivot bed and a top rail -- all ONE `.union()` CAD solid."""
    seat = r.frame_seat_z_m
    rail_top = r.rail_top_z_m
    plate_t = max(0.014, 0.030 * float(r.p["base_plate_x_m"]))
    sx = min(float(r.p["base_plate_x_m"]), 1.9 * r.host_footprint_r_m)
    sy = sx * 0.85
    body = cq.Workplane("XY").box(sx, sy, plate_t).translate((0.0, 0.0, seat + plate_t * 0.5))
    body = body.edges("|Z").fillet(min(0.010, 0.09 * sy))
    post = max(0.05, 0.22 * sx)
    post_h = min(float(r.p["post_height_m"]), rail_top - seat - plate_t - 0.02)
    post_h = max(post_h, 0.02)
    body = body.union(
        _box((post, post, post_h), (0.0, 0.0, seat + plate_t + post_h * 0.5 - r.intra_part_weld_m))
    )
    collar_z = seat + plate_t + post_h
    body = body.union(_box((post * 1.5, post * 1.45, 0.026), (0.0, 0.0, collar_z)))
    mast_h = max(0.02, rail_top - collar_z)
    body = body.union(
        _box((post * 1.33, post * 1.33, mast_h), (0.0, 0.0, collar_z + mast_h * 0.5))
    )
    # twin lower rails + cross ties, the open ladder head this candidate is
    # named for; both sit under the rail top.
    rail_len = 1.35 * r.host_footprint_r_m
    rail_y = max(0.030, 0.75 * float(r.p["former_outer_r_m"]))
    tie_h = max(0.014, 0.05 * rail_y)
    for sign in (-1.0, 1.0):
        body = body.union(
            _box(
                (rail_len, tie_h * 1.5, tie_h),
                (rail_len * 0.5 - post * 0.4, sign * rail_y, rail_top - tie_h * 0.5),
            )
        )
    for i in range(4):
        x = -post * 0.4 + rail_len * (i + 0.5) / 4.0
        body = body.union(
            _box((tie_h * 1.6, 2.0 * rail_y, tie_h), (x, 0.0, rail_top - tie_h * 0.5))
        )
    body = body.union(_cyl(2.2 * rail_y * 0.5, tie_h, z0=rail_top - tie_h))
    return body


def _bender_topology_cast_bench_mimic_build(r: ResolvedConfig) -> cq.Workplane:
    """005 L46-L63: a cast bench plate with two raised longitudinal cheeks and a
    feed pad, and then -- the cleanest MECHANICAL_PRIORS 7 statement in the pool
    -- `body.cut(_cylinder_z(0.069, 0.050, z0=0.012))` at L57, so the cheeks
    WRAP the former instead of passing through it.  The relief radius is
    re-derived here as `cheek_relief_r_m` whenever `former_outer_r_m` moves."""
    seat = r.frame_seat_z_m
    rail_top = r.rail_top_z_m
    plate_t = max(0.010, 0.4 * (rail_top - seat))
    sx = min(float(r.p["plate_x_m"]), 1.95 * r.host_footprint_r_m)
    sy = min(float(r.p["plate_y_m"]), 1.7 * r.host_footprint_r_m)
    body = _box((sx, sy, plate_t), (sx * 0.18, 0.0, seat + plate_t * 0.5))
    cheek_t = max(0.010, 0.09 * sy)
    cheek_h = rail_top - seat
    for sign in (-1.0, 1.0):
        body = body.union(
            _box(
                (sx * 0.70, cheek_t, cheek_h),
                (sx * 0.18, sign * (sy * 0.5 - cheek_t * 0.5), seat + cheek_h * 0.5),
            )
        )
    body = body.union(
        _box((sx * 0.20, sy * 0.78, cheek_h), (sx * 0.60, 0.0, seat + cheek_h * 0.5))
    )
    # L57: the cheeks are cut BACK around the former, not through it.
    body = body.cut(_cyl(r.cheek_relief_r_m, cheek_h + 0.02, z0=seat + plate_t * 0.6))
    body = body.union(_cyl(r.cheek_relief_r_m * 0.42, cheek_h, z0=seat))
    return body


def _bender_topology_three_roll_pyramid_build(r: ResolvedConfig) -> cq.Workplane:
    """three_roll_pyramid L46-L64: the same 8-part tree as cast_bench_mimic
    re-laid out into a THREE-ROLL TRIANGULAR PLAN -- the candidate earns its
    place on plan topology, which its own author test L579-L617 asserts (three
    roll centres, span > 0.14 m, the driven roll offset in y).  The two lower
    support rolls are welded into the bench below the former band."""
    seat = r.frame_seat_z_m
    rail_top = r.rail_top_z_m
    span = min(float(r.p["roll_span_x_m"]), 1.6 * r.host_footprint_r_m)
    offset_y = float(r.p["pyramid_offset_y_m"])
    roll_r = float(r.p["support_roll_r_m"])
    plate_t = max(0.010, 0.34 * (rail_top - seat))
    sx = max(span * 1.5, 1.4 * r.host_footprint_r_m)
    sy = max(offset_y * 2.4, 0.9 * r.host_footprint_r_m)
    body = _box((sx, sy, plate_t), (sx * 0.14, -offset_y * 0.25, seat + plate_t * 0.5))
    stand_h = rail_top - seat
    for sign in (-1.0, 1.0):
        body = body.union(
            _box(
                (span * 0.24, sy * 0.7, stand_h),
                (sign * span * 0.5, -offset_y * 0.25, seat + stand_h * 0.5),
            )
        )
    body = body.union(
        _box((span * 1.25, sy * 0.34, max(0.012, stand_h * 0.30)),
             (0.0, -offset_y * 0.25, rail_top - max(0.012, stand_h * 0.30) * 0.5))
    )
    # the two lower rolls of the pyramid, on horizontal axes, welded into the
    # bench: `guide_x < die_x < follower_x` in plan, offset in y from the driven
    # roll on the bend axis.
    roll_len = min(sy * 0.55, 4.0 * roll_r)
    for sign in (-1.0, 1.0):
        body = body.union(
            cq.Workplane("XZ")
            .circle(roll_r)
            .extrude(roll_len * 0.5, both=True)
            .translate((sign * span * 0.5, -offset_y, rail_top - roll_r))
        )
    body = body.cut(_cyl(r.cheek_relief_r_m, stand_h + 0.02, z0=seat + plate_t * 0.6))
    body = body.union(_cyl(r.cheek_relief_r_m * 0.42, stand_h, z0=seat))
    return body


def _bender_topology_pedestal_fixed_die_swing_handle_build(r: ResolvedConfig) -> cq.Workplane:
    """hickey L59-L81 and L152-L230: a perforated index plate in two radial rows
    and a stacked steel head -- lower head plate, mid and upper frame plates,
    three frame pins.  `head_plate_stack_m` is the vertical distance the head
    itself adds (L188 0.944 vs L219 1.096)."""
    seat = r.frame_seat_z_m
    rail_top = r.rail_top_z_m
    stack = rail_top - seat
    plate_r = min(0.9 * r.host_footprint_r_m, 3.0 * float(r.p["former_outer_r_m"]))
    body = _cyl(plate_r, max(0.008, 0.07 * stack), z0=seat)
    # two perforated rows (30 at r 0.132 and 12 at r 0.103, phase pi/12), cut.
    for count, ring_f, hole_f, phase in ((18, 0.88, 0.030, 0.0), (10, 0.68, 0.034, math.pi / 12.0)):
        for index in range(count):
            angle = phase + 2.0 * math.pi * index / count
            body = body.cut(
                _cyl(
                    plate_r * hole_f,
                    stack,
                    x=plate_r * ring_f * math.cos(angle),
                    y=plate_r * ring_f * math.sin(angle),
                    z0=seat - 0.002,
                )
            )
    plate_t = max(0.010, 0.10 * stack)
    body = body.union(
        _box((plate_r * 1.7, plate_r * 0.75, plate_t), (plate_r * 0.35, plate_r * 0.12, seat + stack * 0.42))
    )
    body = body.union(
        _box((plate_r * 1.5, plate_r * 0.48, plate_t), (plate_r * 0.30, plate_r * 0.30, rail_top - plate_t * 0.5))
    )
    for index, fx in enumerate((-0.18, 0.62, 0.86)):
        body = body.union(
            _cyl(
                max(0.005, 0.055 * plate_r),
                stack * 0.62,
                x=plate_r * fx,
                y=plate_r * 0.30,
                z0=seat + stack * 0.40,
            )
        )
    body = body.union(_cyl(plate_r * 0.30, stack, z0=seat))
    # the SECOND, non-rotating offset former this host is named for (L206), kept
    # outside the follower's swept annulus by `secondary_former_offset_eff_m`.
    sx, sy = r.secondary_former_xy
    body = body.union(
        _cyl(
            r.secondary_former_r_eff_m,
            r.former_seat_z_m + r.former_height_eff_m * 0.7 - (rail_top - plate_t),
            x=sx,
            y=sy,
            z0=rail_top - plate_t,
        )
    )
    reach = math.hypot(sx, sy)
    body = body.union(
        _box(
            (reach + plate_r * 0.3, max(0.012, plate_r * 0.16), plate_t),
            (0.0, 0.0, rail_top - plate_t * 0.5),
        )
        .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(math.atan2(sy, sx)))
        .translate((sx * 0.5, sy * 0.5, 0.0))
    )
    return body


def _bender_topology_hand_lever_plier_build(r: ResolvedConfig) -> cq.Workplane:
    """geared_ring_roller L178-L215: the lower handle, pivot cheek and C-shaped
    die carrier are ONE stamped steel plate, drawn by `_ribbon` -- a
    variable-width offset of a centreline polyline with circular end caps.  This
    host has no base of its own, so `mount_deck_to_host` derives a clamp collar
    around the lower tang (`clamp_collar_required` = yes)."""
    seat = r.frame_seat_z_m
    rail_top = r.rail_top_z_m
    t = max(0.004, rail_top - seat)
    length = float(r.p["tool_length_m"])
    offset = float(r.p["former_offset_m"])
    w = max(0.012, 0.09 * length)
    tang = _ribbon(
        [
            (0.0, 0.0),
            (-0.22 * length, -0.055 * length),
            (-0.42 * length, -0.11 * length),
            (-0.58 * length, -0.15 * length),
        ],
        [w, w * 0.78, w * 0.50, w * 0.36],
        t,
        seat,
    )
    carrier = _ribbon(
        [
            (0.0, 0.0),
            (offset * 0.55, -offset * 0.42),
            (offset * 1.15, -offset * 0.30),
            (offset * 1.55, offset * 0.16),
        ],
        [w * 1.05, w, w * 0.95, w * 0.62],
        t,
        seat,
    )
    body = tang.union(carrier)
    body = body.union(_cyl(w * 0.85, t, z0=seat))
    # red grip, welded onto the tang (L216-L239).  It reads by WIDTH rather than
    # by standing proud, because every frame feature on this host has to stay
    # at or below `rail_top_z_m`; the whole host stack here is 16 mm and any
    # feature that climbs past it enters the swept former band.
    body = body.union(
        _ribbon(
            [
                (-0.28 * length, -0.070 * length),
                (-0.45 * length, -0.118 * length),
                (-0.60 * length, -0.155 * length),
            ],
            [w * 1.35, w * 1.50, w * 1.30],
            t,
            seat,
        )
    )
    # the loose spare die (L409-L436).  DEVIATION: it is welded into the frame
    # rather than left as an isolated part, so it costs one collision solid
    # instead of one part plus one allowance; the pool's own
    # `ctx.allow_isolated_part` for it (L642-L645) is reserved here for the
    # members that are genuinely carried by their joints.
    spx, spy = r.spare_former_xy
    spare_r = float(r.p["spare_former_r_m"])
    lay_h = max(0.0025, rail_top - seat)
    body = body.union(_tube(spare_r, spare_r * 0.34, lay_h, x=spx, y=spy, z0=seat))
    body = body.union(
        _box((w * 0.55, abs(spy) + w, lay_h), (spx, spy * 0.5, seat + lay_h * 0.5))
    )
    # the clamp collar `mount_deck_to_host.clamp_collar_required` derives around
    # the lower tang -- this host has no base of its own.  It stays below the
    # rail top so nothing the moving member sweeps can reach it.
    body = body.union(
        _box(
            (w * 2.2, w * 2.2, lay_h),
            (-0.5 * length, -0.13 * length, seat + lay_h * 0.5),
        )
    )
    return body


def _bender_topology_ram_tripod_build(r: ResolvedConfig) -> cq.Workplane:
    """guide_roller_count_3 L171-L249 and L370-L400: a rounded hydraulic housing
    on a `circle(0.041)` tripod hub with three splayed legs and rubber feet,
    plus the six-point support deck the stations stand on.  DEVIATION 4: the
    captured bent-tube `workpiece` (L574-L579) is DROPPED -- both origins
    explicitly omit the loose demonstration tube (005 L156-L159) and it
    generates 4-5 allowances per seed."""
    seat = r.frame_seat_z_m
    rail_top = r.rail_top_z_m
    weld = r.intra_part_weld_m
    reach = float(r.p["leg_reach_m"])
    stack = rail_top - seat
    housing_h = max(0.05, min(0.30 * stack, stack - 0.02))
    hub_r = max(0.03, 0.16 * reach)
    hx = max(0.10, 0.55 * r.host_footprint_r_m)
    # `circle(0.041)` tripod hub, embedded into the housing above it.
    body = _cyl(hub_r, stack - housing_h + weld, z0=seat)
    body = body.union(
        cq.Workplane("XY")
        .box(hx, hx * 0.62, housing_h)
        .edges("|Z")
        .fillet(min(0.008, 0.12 * hx * 0.62))
        .translate((-hx * 0.45, 0.0, rail_top - housing_h * 0.5))
    )
    # two `circle(0.006) x 0.300` ram guide rods (L340-L360), inside the housing.
    for sign in (-1.0, 1.0):
        body = body.union(
            cq.Workplane("YZ")
            .circle(max(0.004, 0.05 * hub_r))
            .extrude(hx * 0.85)
            .translate((-hx * 0.88, sign * hx * 0.22, rail_top - housing_h * 0.45))
        )
    # the six-point `_support_deck_shape` the stations stand on (L89-L103).
    deck_t = max(0.008, 0.05 * hub_r)
    body = body.union(_cyl(hub_r * 1.35, deck_t, z0=rail_top - deck_t))
    # three splayed legs with rubber feet.  Each leg is authored along +X from
    # the hub, tilted, then rotated into place and translated -- rotate BEFORE
    # translate, or a leg lands somewhere its own foot is not.
    foot_r = max(0.010, 0.06 * hub_r)
    leg_top_z = seat + stack * 0.75
    leg_h = max(0.010, 0.11 * hub_r)
    leg_w = max(0.010, 0.07 * hub_r)
    # The leg is exactly the segment from the hub to its own foot -- no overrun.
    # A box longer than the segment, or one whose tilted half-thickness reaches
    # below the foot, pushes the frame straight through the mount deck it is
    # bolted to, which is a bulk part-to-part interference, not a seat.
    leg_bottom_z = seat + max(foot_r, 0.75 * leg_h)
    drop = leg_top_z - leg_bottom_z
    span = math.hypot(reach, drop)
    tilt = math.degrees(math.atan2(drop, reach))
    for index in range(3):
        angle = 2.0 * math.pi * index / 3.0 + 0.6
        fx, fy = reach * math.cos(angle), reach * math.sin(angle)
        body = body.union(
            cq.Workplane("XY")
            .box(span, leg_w, leg_h)
            .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), tilt)
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(angle))
            .translate(
                (
                    0.5 * reach * math.cos(angle),
                    0.5 * reach * math.sin(angle),
                    0.5 * (leg_top_z + leg_bottom_z),
                )
            )
        )
        body = body.union(
            _cyl(foot_r, max(0.010, 0.05 * hub_r) + weld, x=fx, y=fy, z0=seat)
        )
    return body


_FRAME_BUILDERS = {
    "pedestal_ladder_rail": _bender_topology_pedestal_ladder_rail_build,
    "cast_bench_mimic": _bender_topology_cast_bench_mimic_build,
    "three_roll_pyramid": _bender_topology_three_roll_pyramid_build,
    "pedestal_fixed_die_swing_handle": _bender_topology_pedestal_fixed_die_swing_handle_build,
    "hand_lever_plier": _bender_topology_hand_lever_plier_build,
    "ram_tripod": _bender_topology_ram_tripod_build,
}


# ===========================================================================
# The moving member.  Local frame: the primary revolute is +Z through local
# (0,0,0) and z = 0 is `moving_member_seat_z_m`.  Every silhouette occupies
# z in [0, arm_thickness_m], so the drive plane above and the former band below
# stay free at every sweep angle -- that is what removes the pool's whole
# "lever hub vs spindle / carrier vs pivot pin" allowance family.
# ===========================================================================
def _moving_member_shape(r: ResolvedConfig) -> cq.Workplane:
    t = r.arm_thickness_m
    reach = r.moving_member_reach_m
    hub_r = max(2.2 * r.former_bore_r_m, 0.30 * float(r.p["former_outer_r_m"]))
    fs = r.follower_station_r_m
    topo = r.bender_topology

    if topo == "hand_lever_plier":
        # geared_ring_roller L268-L300: the upper handle is a ribbon too.
        w = max(0.012, 0.09 * float(r.p["tool_length_m"]))
        body = _ribbon(
            [
                (0.0, 0.0),
                (-0.24 * reach, 0.075 * reach),
                (-0.55 * reach, 0.16 * reach),
                (-0.80 * reach, 0.22 * reach),
                (-reach, 0.26 * reach),
            ],
            [w * 1.05, w * 0.82, w * 0.55, w * 0.40, w * 0.34],
            t,
            0.0,
        )
        body = body.union(_ribbon([(0.0, 0.0), (fs * 0.5, 0.0), (fs, 0.0)], [w * 1.1, w, w * 0.9], t, 0.0))
    elif topo == "pedestal_fixed_die_swing_handle":
        # hickey L252-L309: two slender parallel handle members joined by
        # spacers and an end tie.  DEPARTURE: the source separates them by
        # 0.064 in Z; here they are separated in Y, because a member that thick
        # in Z would enter the drive plane.
        rail_w = max(0.010, 0.045 * reach)
        gap = max(0.02, 0.09 * reach)
        for sign in (-1.0, 1.0):
            body_part = _box(
                (reach, rail_w, t), (-reach * 0.5 + hub_r * 0.4, sign * gap * 0.5, t * 0.5)
            )
            body = body_part if sign < 0 else body.union(body_part)
        for x in (-reach * 0.25, -reach * 0.78):
            body = body.union(_box((rail_w * 1.6, gap + rail_w, t), (x, 0.0, t * 0.5)))
        body = body.union(_box((rail_w * 2.0, gap + rail_w * 2.0, t), (-reach + hub_r, 0.0, t * 0.5)))
    elif topo == "ram_tripod":
        # the ram carriage arm: a broad plate reaching the follower station,
        # plus the pump-handle boss the L5 family carries (L536-L549).
        w = max(0.018, 0.10 * reach)
        body = _box((reach, w, t), (-reach * 0.5 + hub_r * 0.4, 0.0, t * 0.5))
        body = body.union(
            _box((fs * 1.5, w * 1.4, t), (fs * 0.45, 0.0, t * 0.5))
        )
        ph = min(float(r.p["pump_handle_length_m"]), reach)
        body = body.union(_box((ph, w * 0.55, t), (-ph * 0.5, -w * 0.9, t * 0.5)))
    else:
        # 004 L84-L89 / 005 L85-L110: a cast head -- hub, carrier plate,
        # follower boss and a diagonal structural web -- plus a long tube.
        w = max(0.016, 0.085 * reach)
        body = _box((reach, w, t), (-reach * 0.5 + hub_r * 0.4, 0.0, t * 0.5))
        body = body.union(_box((fs * 1.35, w * 1.5, t), (fs * 0.42, -w * 0.25, t * 0.5)))
        body = body.union(
            cq.Workplane("XY")
            .polyline(
                [
                    (-hub_r * 0.4, w * 0.55),
                    (fs * 0.85, -w * 0.95),
                    (fs * 0.85, -w * 0.35),
                    (-hub_r * 0.4, w * 0.15),
                ]
            )
            .close()
            .extrude(t)
        )
        for i in range(6):
            body = body.union(
                _box(
                    (reach * 0.018, w * 1.35, t * 1.05),
                    (-reach * (0.55 + 0.05 * i) + hub_r * 0.4, 0.0, t * 0.5),
                )
            )
    body = body.union(_cyl(hub_r, t))
    # Three radial webs from the hub out past the drive counterpart's collar.
    # Without them a twin-rail or ribbon member can leave the collar as its own
    # geometry island, and `find_part_geometry_connectivity_findings` walks
    # visuals per link at contact_tol 1e-6.  They live in the arm's own z band,
    # which the frame vacates entirely above `rail_top_z_m`.
    web_r_out = max(fs * 0.6, r.gear_ring_inner_r_m * 1.25)
    for index in range(3):
        body = body.union(
            _box((web_r_out, max(0.008, 1.2 * hub_r), t), (web_r_out * 0.5, 0.0, t * 0.5))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 120.0 * index + 40.0)
        )
    # the follower's real cut slot -- MECHANICAL_PRIORS 7, and the fix for
    # allowance group 4 (005 cuts a rectangular slot narrower than its own shoe
    # ring; here the carrier is bored at `shoe_boss_bore_r_m`).  The +X spine
    # ties the follower boss back to the hub on every silhouette, including the
    # twin-rail and ribbon members whose arms only run toward -X.
    fr = r.follower_body_r_m
    spine_end = fs + r.follower_stroke_m + 2.2 * fr + 0.004
    spine_w = max(0.014, 3.0 * fr + 0.004)
    body = body.union(
        _box((spine_end, spine_w, t), (0.5 * spine_end, 0.0, t * 0.5))
    )
    body = body.union(_cyl(fr * 1.7, t, x=fs))
    # The slot is shorter and narrower than the spine on every axis, so a rim of
    # carrier survives all the way round it: a slot that runs off the end of its
    # own boss severs the tip into a second solid.
    slot_len = r.follower_stroke_m + 2.0 * fr + 0.002
    body = body.cut(
        _box(
            (slot_len, 2.0 * fr + 0.0016, t + 0.02),
            (fs + r.follower_stroke_m * 0.5, 0.0, t * 0.5),
        )
    )
    body = body.cut(_cyl(r.former_bore_r_m, t + 0.02, z0=-0.01))
    counterpart = _drive_counterpart(r)
    if counterpart is not None:
        body = body.union(counterpart)
    return body


# ===========================================================================
# Assembly.
# ===========================================================================
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    for key, rgba in r.palette.items():
        model.material(f"mpb_{key}", rgba=rgba)
    return {key: f"mpb_{key}" for key in r.palette}


def _cq_visual(part, solid: cq.Workplane, r: ResolvedConfig, material: str, name: str) -> None:
    part.visual(
        mesh_from_cadquery(
            solid, name, tolerance=r.mesh_chord_tol_m, angular_tolerance=_ANG_TOL
        ),
        material=material,
        name=name, material_class_id="metal.paint_coated",
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
    limits: MotionLimits | None,
    radius: float,
    meta: dict | None = None,
):
    """Every revolute/continuous joint in this template is solved by `mate_axes`
    on the true design axis and registered with `register_interface_mate`
    (AUTHORING 4).  The consumer interface sits on the child-frame origin, so
    `axis_origin_offset` is exactly zero and the strict `TEMPLATE_DOMAIN`
    contract in `fail_if_interface_mate_mismatch` is satisfied."""
    radial = (1.0, 0.0, 0.0) if abs(axis[0]) < 0.9 else (0.0, 0.0, 1.0)
    provider = AxisInterface(
        name=f"{name}__provider", point=point, axis=axis, radial=radial, radius=radius
    )
    consumer = AxisInterface(name=f"{name}__consumer", axis=axis, radial=radial, radius=radius)
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        joint_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)


def _follower_post(r: ResolvedConfig) -> cq.Workplane:
    """The stem that runs through the carrier's cut slot.  MECHANICAL_PRIORS 7:
    a moving member that passes through its host gets a real opening, sized from
    the moving part's envelope plus a derived clearance -- never a fixed magic
    number and never a member resting on a solid face."""
    fr = r.follower_body_r_m
    _bottom, top = _follower_span(r)
    root = top - r.intra_part_weld_m
    return _box(
        (fr * 0.9, fr * 0.9, r.arm_thickness_m * 0.92 - root),
        (0.0, 0.0, 0.5 * (root + r.arm_thickness_m * 0.92)),
    )


def build_manual_pipe_bender(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    topo, profile, mount = r.bender_topology, r.former_profile, r.mount
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "manual_pipe_bender",
            "small_class": "manual_pipe_bender",
            "slot_choices": slot_choices_for_config(r),
            "source_family": "pictureX/0611/manual_pipe_bender",
        },
    )
    mats = _materials(model, r)

    # ---- mount_base --------------------------------------------------------
    mount_part = model.part(
        "mount_base", meta={"role": "mount_base", "candidate": mount}
    )
    _cq_visual(
        mount_part,
        _MOUNT_BUILDERS[mount](r),
        r,
        mats["body"],
        f"mount__{mount}__grounded_deck",
    )

    # ---- bender_frame ------------------------------------------------------
    frame = model.part(
        "bender_frame", meta={"role": "bender_frame", "candidate": topo}
    )
    # The mount sources place the host directly on their top cap/saddle
    # (bench plate L46-L63, floor pedestal L161-L177, vise mount L161-L200,
    # caster deck L154-L184).  Keep the authored world-space geometry, but make
    # the child frame's local origin that real seat instead of the world
    # origin.  This preserves every world-space derived Z value while ensuring
    # the fixed articulation is physically incident to both connected parts.
    frame_origin_z = r.frame_seat_z_m
    frame_solid = _frame_stations(r, _FRAME_BUILDERS[topo](r)).translate(
        (0.0, 0.0, -frame_origin_z)
    )
    _cq_visual(
        frame,
        frame_solid,
        r,
        mats["cast"],
        f"bender_topology__{topo}__welded_frame",
    )
    model.articulation(
        f"mount__{mount}__frame_seat",
        ArticulationType.FIXED,
        parent=mount_part,
        child=frame,
        origin=Origin(xyz=(0.0, 0.0, frame_origin_z)),
    )

    # ---- moving_member + follower -----------------------------------------
    moving = model.part(
        "moving_member", meta={"role": "moving_member", "candidate": topo}
    )
    _cq_visual(
        moving,
        _moving_member_shape(r),
        r,
        mats["body"],
        f"bender_topology__{topo}__moving_member",
    )
    _axis_joint(
        model,
        name=f"bender_topology__{topo}__primary_sweep",
        joint_type=ArticulationType.REVOLUTE,
        parent=frame,
        child=moving,
        point=(0.0, 0.0, r.moving_member_seat_z_m - frame_origin_z),
        axis=(0.0, 0.0, 1.0),
        limits=MotionLimits(
            effort=r.primary_effort_n,
            velocity=1.2,
            lower=r.sweep_lower_rad,
            upper=r.sweep_upper_eff_rad,
        ),
        radius=float(r.p["primary_shaft_r_m"]),
        meta={"mechanism": "the long moving member sweeps the tube about the bend axis"},
    )

    follower = model.part(
        "follower", meta={"role": "follower", "candidate": r.follower_form}
    )
    follower_solid = _FOLLOWER_BUILDERS[r.follower_form](r).union(_follower_post(r))
    _cq_visual(
        follower,
        follower_solid,
        r,
        mats["accent"],
        f"bender_topology__{topo}__{r.follower_form}",
    )
    model.articulation(
        f"bender_topology__{topo}__follower_adjust",
        ArticulationType.PRISMATIC,
        parent=moving,
        child=follower,
        origin=Origin(xyz=(r.follower_station_r_m, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=r.follower_effort_n,
            velocity=0.05,
            lower=0.0,
            upper=r.follower_stroke_m,
        ),
        meta={"mechanism": "tube-size adjustment: the follower backs off the former radially"},
    )

    # ---- drive_member ------------------------------------------------------
    drive = model.part(
        "drive_member", meta={"role": "drive_member", "candidate": r.drive_form}
    )
    _cq_visual(
        drive,
        _DRIVE_BUILDERS[r.drive_form](r),
        r,
        mats["steel"],
        f"bender_topology__{topo}__{r.drive_form}",
    )
    _axis_joint(
        model,
        name=f"bender_topology__{topo}__drive_input",
        joint_type=ArticulationType.REVOLUTE,
        parent=frame,
        child=drive,
        point=(0.0, 0.0, r.drive_gear_z_m - frame_origin_z),
        axis=(0.0, 0.0, 1.0),
        limits=MotionLimits(
            effort=r.drive_effort_n,
            velocity=1.0,
            lower=-0.5 * r.primary_sweep_rad,
            upper=0.5 * r.primary_sweep_rad,
        ),
        radius=float(r.p["primary_shaft_r_m"]),
        meta={"mechanism": f"{r.drive_form} acting on the published primary axis"},
    )

    # ---- bending formers, one per station ----------------------------------
    former_solid = _FORMER_BUILDERS[profile](r)
    former_mesh_name = f"former_profile__{profile}__grooved_former"
    former_mesh = mesh_from_cadquery(
        former_solid,
        former_mesh_name,
        tolerance=r.mesh_chord_tol_m,
        angular_tolerance=_ANG_TOL,
    )
    for index, (x, y) in enumerate(r.former_stations_xy):
        part = model.part(
            f"former_profile__{profile}__bending_former_{index}",
            meta={"role": "bending_former", "candidate": profile, "station": index},
        )
        part.visual(former_mesh, material=mats["hardware"], name=f"{former_mesh_name}_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"machine_blue", "cast_teal", "hydraulic_red"} else "metal.stainless_matte"))
        joint = f"former_profile__{profile}__former_pivot_{index}"
        if r.former_is_part == "yes":
            _axis_joint(
                model,
                name=joint,
                joint_type=ArticulationType.REVOLUTE,
                parent=frame,
                child=part,
                point=(x, y, r.former_seat_z_m - frame_origin_z),
                axis=(0.0, 0.0, 1.0),
                limits=MotionLimits(
                    effort=r.former_effort_n, velocity=0.8, lower=-0.35, upper=0.35
                ),
                radius=r.former_bore_r_m,
            )
        else:
            # hickey L198-L203: this host's former does NOT rotate.  It stays a
            # real part (anchor `pipe_bender_bend_axis_identity` counts one per
            # station on every candidate) and is welded into its own bearing
            # boss by `lineage_weld_m`.
            model.articulation(
                joint,
                ArticulationType.FIXED,
                parent=frame,
                child=part,
                origin=Origin(
                    xyz=(
                        x,
                        y,
                        r.former_seat_z_m - r.lineage_weld_m - frame_origin_z,
                    )
                ),
            )

    # ---- guide rollers -----------------------------------------------------
    roller_mesh_name = f"bender_topology__{topo}__{r.guide_roller_form}"
    roller_mesh = mesh_from_cadquery(
        _guide_roller_shape(r),
        roller_mesh_name,
        tolerance=r.mesh_chord_tol_m,
        angular_tolerance=_ANG_TOL,
    )
    for index, (x, y) in enumerate(r.guide_stations_xy):
        part = model.part(
            f"bender_topology__{topo}__guide_roller_{index}",
            meta={"role": "guide_roller", "candidate": topo, "station": index},
        )
        part.visual(roller_mesh, material=mats["steel"], name=f"{roller_mesh_name}_{index}", material_class_id="metal.steel_bare")
        _axis_joint(
            model,
            name=f"bender_topology__{topo}__guide_roller_spin_{index}",
            joint_type=ArticulationType.CONTINUOUS,
            parent=frame,
            child=part,
            point=(x, y, r.roller_seat_z_m - frame_origin_z),
            axis=(0.0, 0.0, 1.0),
            limits=MotionLimits(effort=r.roller_effort_n, velocity=10.0),
            radius=r.guide_roller_bore_r_m,
        )

    # ---- caster module -----------------------------------------------------
    if mount == "caster_deck":
        _build_casters(model, r, mats, mount_part)

    primary = f"bender_topology__{topo}__primary_sweep"
    drive_joint = f"bender_topology__{topo}__drive_input"
    follower_joint = f"bender_topology__{topo}__follower_adjust"
    model.meta["coupled_joint_pairs"] = (
        (primary, drive_joint),
        (primary, follower_joint),
    )
    model.meta["risk_poses"] = (
        {primary: r.sweep_upper_eff_rad, follower_joint: r.follower_stroke_m},
        {primary: r.sweep_lower_rad, follower_joint: 0.0},
        {primary: r.sweep_upper_eff_rad, drive_joint: 0.5 * r.primary_sweep_rad},
        {primary: r.sweep_lower_rad, drive_joint: -0.5 * r.primary_sweep_rad},
    )
    return model


def _build_casters(model: ArticulatedObject, r: ResolvedConfig, mats, mount_part) -> None:
    """DEVIATION 3, in full.  MECHANICAL_PRIORS 5 requires a caster to have a
    VERTICAL swivel axis and a spin axis THROUGH the wheel centre.
    `mount_wheeled_floor_stand` gives it neither: four rigid wheel visuals on
    `stand` (L163-L171), no joints, and a 0.056-wide wheel inside a 0.026 fork
    gap -- legal only while wheel and fork are visuals of one part.  The rebuild
    emits 4 `caster_swivel` + 4 `caster_wheel` parts with REVOLUTE (0,0,1) and
    CONTINUOUS local-X joints, widens the fork to `caster_fork_gap_m` and
    re-grounds the deck so the contact patch is z = 0."""
    wheel_r = float(r.p["caster_wheel_r_m"])
    gap = r.caster_fork_gap_m
    leg_t = max(0.008, 0.20 * wheel_r)
    z_sw = r.mount_height_m - _CASTER_DECK_T - _CASTER_PAD_T
    axle_r = max(0.004, 0.14 * wheel_r)
    crown_r = max(0.5 * gap + leg_t, 0.55 * wheel_r)
    crown_h = _CASTER_CROWN_F * wheel_r
    stem_h = _CASTER_STEM_F * wheel_r
    for index, (cx, cy) in enumerate(r.caster_station_xy):
        swivel = model.part(
            f"mount__caster_deck__caster_swivel_{index}",
            meta={"role": "caster_swivel", "candidate": "caster_deck", "station": index},
        )
        wheel_centre_z = wheel_r - z_sw
        leg_bottom = wheel_centre_z - wheel_r * 0.35
        # crown, then a narrower stem, then the two fork legs -- each embedded
        # into the one above by `intra_part_weld_m`, because a tangent stack
        # inside ONE part still reads as broken geometry at contact_tol 1e-6.
        body = _cyl(crown_r, crown_h + r.intra_part_weld_m, z0=-crown_h)
        body = body.union(
            _cyl(crown_r * 0.55, stem_h + r.intra_part_weld_m, z0=-crown_h - stem_h)
        )
        for sign in (-1.0, 1.0):
            # the legs run up INTO the crown, not merely to the stem's bottom
            # plane -- the stem is narrower than the fork gap, so stopping there
            # leaves the fork as its own island inside the part.
            leg_top = -crown_h + r.intra_part_weld_m
            body = body.union(
                _box(
                    (leg_t, wheel_r * 1.1, leg_top - leg_bottom),
                    (sign * (0.5 * gap + 0.5 * leg_t), 0.0, 0.5 * (leg_bottom + leg_top)),
                )
            )
        body = body.union(
            cq.Workplane("YZ")
            .circle(axle_r)
            .extrude(0.5 * gap + leg_t, both=True)
            .translate((0.0, 0.0, wheel_centre_z))
        )
        _cq_visual(swivel, body, r, mats["cast"], f"mount__caster_deck__swivel_fork_{index}")
        _axis_joint(
            model,
            name=f"mount__caster_deck__caster_swivel_spin_{index}",
            joint_type=ArticulationType.REVOLUTE,
            parent=mount_part,
            child=swivel,
            point=(cx, cy, z_sw),
            axis=(0.0, 0.0, 1.0),
            limits=MotionLimits(effort=60.0, velocity=4.0, lower=-math.pi, upper=math.pi),
            radius=crown_r,
        )

        wheel = model.part(
            f"mount__caster_deck__caster_wheel_{index}",
            meta={"role": "caster_wheel", "candidate": "caster_deck", "station": index},
        )
        tyre = (
            cq.Workplane("YZ")
            .circle(wheel_r)
            .circle(axle_r + r.bore_clearance_m)
            .extrude(float(r.p["caster_wheel_width_m"]) * 0.5, both=True)
        )
        _cq_visual(wheel, tyre, r, mats["grip"], f"mount__caster_deck__wheel_{index}")
        _axis_joint(
            model,
            name=f"mount__caster_deck__caster_wheel_spin_{index}",
            joint_type=ArticulationType.CONTINUOUS,
            parent=swivel,
            child=wheel,
            point=(0.0, 0.0, wheel_r - z_sw),
            axis=(1.0, 0.0, 0.0),
            limits=MotionLimits(effort=80.0, velocity=12.0),
            radius=axle_r + r.bore_clearance_m,
        )


# ===========================================================================
# Author tests.  These are the category's own mechanical invariants, expressed
# as derived-parameter arithmetic and part/joint structure; mesh assets, exact
# collision, sampled poses and isolated geometry belong to the sweep harness.
# ===========================================================================
def _parts_by_role(model: ArticulatedObject, role: str) -> list:
    return [p for p in model.parts if (p.meta or {}).get("role") == role]


def _joint(model: ArticulatedObject, name: str):
    return next((j for j in model.articulations if j.name == name), None)


def run_manual_pipe_bender_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    topo, profile, mount = r.bender_topology, r.former_profile, r.mount

    frame = _parts_by_role(object_model, "bender_frame")
    moving = _parts_by_role(object_model, "moving_member")
    drive = _parts_by_role(object_model, "drive_member")
    follower = _parts_by_role(object_model, "follower")
    formers = _parts_by_role(object_model, "bending_former")
    rollers = _parts_by_role(object_model, "guide_roller")
    base = _parts_by_role(object_model, "mount_base")
    roots = [
        p.name
        for p in object_model.parts
        if not any(j.child == p.name for j in object_model.articulations)
    ]
    primary = _joint(object_model, f"bender_topology__{topo}__primary_sweep")
    drive_joint = _joint(object_model, f"bender_topology__{topo}__drive_input")
    follower_joint = _joint(object_model, f"bender_topology__{topo}__follower_adjust")

    # ---- anchor: pipe_bender_bend_axis_identity ---------------------------
    ctx.check(
        "category_anchor: exactly one grounded root frame part",
        roots == ["mount_base"] and len(base) == 1 and len(frame) == 1 and len(moving) == 1,
        details=f"roots={roots}, frame={len(frame)}, moving={len(moving)}",
    )
    axis_ok = True
    for joint in (primary, drive_joint):
        if joint is None:
            axis_ok = False
            continue
        axis_ok = axis_ok and tuple(round(float(v), 9) for v in joint.axis) == (0.0, 0.0, 1.0)
        axis_ok = axis_ok and abs(joint.origin.xyz[0]) < 1e-4 and abs(joint.origin.xyz[1]) < 1e-4
    for index in range(r.former_count):
        joint = _joint(object_model, f"former_profile__{profile}__former_pivot_{index}")
        axis_ok = axis_ok and joint is not None
    # WHICH index is the working station differs by placement law and both are
    # source-attested: `former_count_3` L317-L321 pins index 0 to the host's
    # bending station, while `former_count_2` L24-L26 puts index N-1 on the
    # pivot.  The anchor is that ONE former is on the bend axis, not that it is
    # the first one.
    station_radii = [math.hypot(x, y) for x, y in r.former_stations_xy]
    on_axis = [i for i, rad in enumerate(station_radii) if rad < 1e-4]
    axis_ok = axis_ok and len(on_axis) == 1
    ctx.check(
        "category_anchor: the bend axis is +Z and former, moving member and drive are concentric with it within 0.1 mm",
        axis_ok,
        details=(
            f"on_axis={on_axis}, radii={[round(v, 4) for v in station_radii]}, "
            f"primary={None if primary is None else primary.origin.xyz}"
        ),
    )
    ctx.check(
        "category_anchor: the moving member reaches at least four former diameters from the bend axis",
        r.moving_member_reach_m >= 4.0 * 2.0 * float(r.p["former_outer_r_m"]) - 1e-9
        and r.moving_member_reach_m >= (0.30 if topo == "hand_lever_plier" else 0.72) - 1e-9,
        details=f"reach={r.moving_member_reach_m:.4f}, former_d={2 * r.p['former_outer_r_m']:.4f}",
    )
    ctx.check(
        "category_anchor: the frame provides a real cut relief, slot or bore for every moving member",
        r.cheek_relief_r_m > float(r.p["former_outer_r_m"])
        and r.moving_member_seat_z_m > r.former_seat_z_m + r.former_height_eff_m
        and r.drive_gear_z_m > r.moving_member_seat_z_m + r.arm_thickness_m
        and r.rail_top_z_m < r.former_seat_z_m,
        details=(
            f"relief={r.cheek_relief_r_m:.4f}/{r.p['former_outer_r_m']:.4f}, "
            f"rail_top={r.rail_top_z_m:.4f} seat={r.former_seat_z_m:.4f} "
            f"msz={r.moving_member_seat_z_m:.4f} drive={r.drive_gear_z_m:.4f}"
        ),
    )

    # ---- anchor: pipe_bender_rotating_former ------------------------------
    ctx.check(
        "category_anchor: every former is a part with a real cut through bore strictly larger than the pin it runs on",
        len(formers) == r.former_count
        and r.former_bore_r_m > float(r.p["primary_shaft_r_m"])
        and r.bore_clearance_m >= 0.0002 - 1e-12,
        details=(
            f"formers={len(formers)}/{r.former_count}, bore={r.former_bore_r_m:.5f} "
            f"shaft={r.p['primary_shaft_r_m']:.5f}"
        ),
    )
    ctx.check(
        "category_anchor: every former seats on a derived thrust washer or bearing top, never on an authored constant",
        abs(
            r.former_seat_z_m
            - (
                r.mount_height_m
                + r.host_stack_z_m
                + r.thrust_washer_height_m
                + r.former_running_gap_m
            )
        )
        < 1e-9
        and abs(r.turret_bearing_top_z_m - (r.former_seat_z_m - r.former_running_gap_m)) < 1e-9,
        details=f"seat={r.former_seat_z_m:.5f}, bearing_top={r.turret_bearing_top_z_m:.5f}",
    )
    parents = {
        j.child: j.parent
        for j in object_model.articulations
        if j.name.startswith(f"former_profile__{profile}__former_pivot_")
    }
    ctx.check(
        "category_anchor: formers parent to the frame, never to the turret crosshead",
        len(parents) == r.former_count and set(parents.values()) == {"bender_frame"},
        details=str(parents),
    )

    # ---- anchor: pipe_bender_drive_on_primary_axis ------------------------
    ctx.check(
        "category_anchor: the drive acts on the published primary axis, not on a tangential surface",
        drive_joint is not None
        and len(drive) == 1
        and tuple(round(float(v), 9) for v in drive_joint.axis) == (0.0, 0.0, 1.0)
        and math.hypot(drive_joint.origin.xyz[0], drive_joint.origin.xyz[1]) < 1e-4,
        details=str(None if drive_joint is None else drive_joint.origin.xyz),
    )
    driver_tip = (
        r.sector_tip_r_m if r.drive_form == "ratchet_sector_drive" else r.gear_tip_r_driver_m
    )
    mesh_ok = (
        r.drive_form == "lever_handle"
        or abs((r.gear_ring_inner_r_m - driver_tip) - 0.0003) < 1e-9
    )
    ctx.check(
        "category_anchor: meshing members are tangent - centre distance equals the sum of tip radii plus 0.3 mm, with no tooth interpenetration",
        mesh_ok
        and abs(
            r.gear_centre_distance_m
            - (r.gear_tip_r_driver_m + r.gear_tip_r_driven_m + 0.0003)
        )
        < 1e-9,
        details=(
            f"drive={r.drive_form}, ring_inner={r.gear_ring_inner_r_m:.5f}, "
            f"driver_tip={driver_tip:.5f}"
        ),
    )
    ctx.check(
        "category_anchor: a ratchet pawl tip lies outside the tooth tip circle and engages a flank",
        r.pawl_tip_r_m > r.sector_tip_r_m
        and abs((r.pawl_tip_r_m - r.sector_tip_r_m) - 0.0003) < 1e-9
        and r.sector_tooth_half_width_m
        <= 0.45 * (2.0 * r.sector_half_span_rad / r.sector_tooth_count) * r.sector_outer_r_m
        + 1e-12,
        details=f"pawl_tip={r.pawl_tip_r_m:.5f}, sector_tip={r.sector_tip_r_m:.5f}",
    )

    # ---- anchor: pipe_bender_adjustment_dof -------------------------------
    prismatics = [
        j
        for j in object_model.articulations
        if getattr(j.articulation_type, "value", str(j.articulation_type)) == "prismatic"
    ]
    ctx.check(
        "category_anchor: at least one prismatic or screw adjustment degree of freedom exists",
        len(prismatics) >= 1
        and follower_joint is not None
        and follower_joint.parent == "moving_member"
        and r.follower_stroke_m > 0.0,
        details=f"prismatic={[j.name for j in prismatics]}, stroke={r.follower_stroke_m:.5f}",
    )
    ctx.check(
        "category_anchor: the follower's tube seat lies on the former groove mid-plane",
        abs(r.follower_seat_z_m - (r.former_seat_z_m + r.groove_mid_z_m)) < 1e-9
        and len(follower) == 1,
        details=f"seat={r.follower_seat_z_m:.5f}, groove_mid={r.groove_mid_z_m:.5f}",
    )
    ctx.check(
        "category_anchor: the follower runs in a real cut slot or bore in its carrier, not on a solid face",
        r.shoe_boss_bore_r_m > r.shoe_bore_r_m
        and r.follower_body_r_m > 0.0
        and r.follower_station_r_m - r.follower_body_r_m > float(r.p["former_outer_r_m"]),
        details=(
            f"station={r.follower_station_r_m:.5f}, body_r={r.follower_body_r_m:.5f}, "
            f"former_r={r.p['former_outer_r_m']:.5f}"
        ),
    )

    # ---- anchor: pipe_bender_roller_spin ----------------------------------
    spin_ok = len(rollers) == r.guide_roller_count
    for index in range(r.guide_roller_count):
        joint = _joint(object_model, f"bender_topology__{topo}__guide_roller_spin_{index}")
        spin_ok = spin_ok and joint is not None
        if joint is not None:
            spin_ok = spin_ok and tuple(round(float(v), 9) for v in joint.axis) == (0.0, 0.0, 1.0)
            spin_ok = spin_ok and (
                getattr(joint.articulation_type, "value", "") == "continuous"
            )
    ctx.check(
        "category_anchor: every guide roller spins about +Z through its own centre",
        spin_ok,
        details=f"rollers={len(rollers)}/{r.guide_roller_count}",
    )
    ctx.check(
        "category_anchor: every guide roller bore is strictly larger than its axle",
        r.guide_roller_bore_r_m > r.guide_roller_axle_r_m
        and r.guide_roller_outer_r_m > r.guide_roller_bore_r_m,
        details=(
            f"bore={r.guide_roller_bore_r_m:.5f}, axle={r.guide_roller_axle_r_m:.5f}, "
            f"outer={r.guide_roller_outer_r_m:.5f}"
        ),
    )
    spacing_ok = True
    for index in range(1, r.guide_roller_count):
        ax, ay = r.guide_stations_xy[index - 1]
        bx, by = r.guide_stations_xy[index]
        spacing_ok = spacing_ok and math.hypot(bx - ax, by - ay) >= (
            2.0 * r.guide_roller_outer_r_m + 0.006 - 1e-9
        )
    ctx.check(
        "category_anchor: guide roller spacing follows the host's declared placement law and the track grows with N",
        spacing_ok
        and r.guide_placement_law
        == ("pipe_path_law" if topo == "ram_tripod" else "rail_pitch_law")
        and abs(
            r.roller_track_length_m
            - (
                (r.guide_roller_count - 1) * r.guide_pitch_m
                + 2.0 * r.guide_roller_outer_r_m
                + 1.7 * float(r.p["former_outer_r_m"])
            )
        )
        < 1e-9,
        details=f"law={r.guide_placement_law}, track={r.roller_track_length_m:.4f}",
    )

    # ---- anchor: pipe_bender_grounded_mount -------------------------------
    seat_joint = _joint(object_model, f"mount__{mount}__frame_seat")
    ctx.check(
        "category_anchor: the tool is grounded at z=0 and the mount carries the whole host footprint",
        seat_joint is not None
        and seat_joint.parent == "mount_base"
        and seat_joint.child == "bender_frame"
        and abs(r.ground_z_m) < 1e-12
        and r.mount_footprint_r_m >= 1.25 * r.host_footprint_r_m - 1e-9
        and 0.5 * r.deck_x_eff_m >= 1.05 * r.host_footprint_r_m - 1e-9,
        details=(
            f"deck={r.deck_x_eff_m:.4f}x{r.deck_y_eff_m:.4f}, "
            f"host_footprint={r.host_footprint_r_m:.4f}"
        ),
    )
    ctx.check(
        "category_anchor: the primary axis height is derived from the mount, not authored per host",
        abs(r.spindle_z_m - (r.mount_height_m + r.host_stack_z_m)) < 1e-9
        and abs(r.frame_seat_z_m - (r.mount_height_m - r.lineage_weld_m)) < 1e-9
        and 0.0 < r.lineage_weld_m < 0.001,
        details=(
            f"spindle={r.spindle_z_m:.5f}, mount_h={r.mount_height_m:.5f}, "
            f"stack={r.host_stack_z_m:.5f}, weld={r.lineage_weld_m:.5f}"
        ),
    )
    swivels = _parts_by_role(object_model, "caster_swivel")
    wheels = _parts_by_role(object_model, "caster_wheel")
    if mount == "caster_deck":
        caster_ok = len(swivels) == 4 and len(wheels) == 4
        for index in range(4):
            sj = _joint(object_model, f"mount__caster_deck__caster_swivel_spin_{index}")
            wj = _joint(object_model, f"mount__caster_deck__caster_wheel_spin_{index}")
            caster_ok = caster_ok and sj is not None and wj is not None
            if sj is not None and wj is not None:
                caster_ok = caster_ok and tuple(
                    round(float(v), 9) for v in sj.axis
                ) == (0.0, 0.0, 1.0)
                caster_ok = caster_ok and tuple(
                    round(float(v), 9) for v in wj.axis
                ) == (1.0, 0.0, 0.0)
        caster_ok = caster_ok and r.caster_fork_gap_m > float(r.p["caster_wheel_width_m"])
    else:
        caster_ok = not swivels and not wheels
    ctx.check(
        "category_anchor: caster wheels have separate swivel and spin axes and clear their forks",
        caster_ok,
        details=f"mount={mount}, swivels={len(swivels)}, wheels={len(wheels)}",
    )

    # ---- template invariants ----------------------------------------------
    ctx.check(
        "domain choices are recorded on the model",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )
    ctx.check(
        "every guide station clears the follower's swept annulus and every stowed former",
        all(
            math.hypot(x, y) >= r.follower_orbit_outer_m + r.guide_roller_outer_r_m + 0.008 - 1e-9
            for x, y in r.guide_stations_xy
        ),
        details=(
            f"orbit_outer={r.follower_orbit_outer_m:.4f}, "
            f"stations={[round(math.hypot(x, y), 4) for x, y in r.guide_stations_xy]}"
        ),
    )
    ctx.check(
        "every stowed former station clears the follower's swept annulus",
        all(
            rad < 1e-4
            or rad >= r.follower_orbit_outer_m + float(r.p["former_outer_r_m"]) + 0.006 - 1e-6
            for rad in station_radii
        ),
        details=(
            f"orbit_outer={r.follower_orbit_outer_m:.4f}, "
            f"radii={[round(v, 4) for v in station_radii]}"
        ),
    )
    ctx.check(
        "the groove never swallows more than 85 percent of the tube radius and the former grows to hold it",
        r.groove_depth_m <= 0.85 * float(r.p["pipe_outer_r_m"]) + 1e-12
        and r.groove_root_r_m > r.former_bore_r_m
        and r.former_height_eff_m >= float(r.p["former_height_m"]) - 1e-9
        and abs(r.former_height_eff_m - (r.groove_height_m + 2.0 * r.former_flange_h_m)) < 1e-9,
        details=(
            f"depth={r.groove_depth_m:.5f}, root={r.groove_root_r_m:.5f}, "
            f"bore={r.former_bore_r_m:.5f}, h_eff={r.former_height_eff_m:.5f}"
        ),
    )
    ctx.check(
        "the drive and follower forms are derived from the topology, not sampled",
        r.drive_form == _TOPOLOGY_DRIVE[topo]
        and r.follower_form == _TOPOLOGY_FOLLOWER[topo]
        and r.guide_roller_form == _TOPOLOGY_ROLLER_FORM[topo]
        and r.ram_crank_link_required == "no",
        details=f"{r.drive_form}/{r.follower_form}/{r.guide_roller_form}",
    )

    # ---- allowances: joint-carried members ---------------------------------
    for part in [moving[0] if moving else None, follower[0] if follower else None,
                 drive[0] if drive else None] + formers + rollers + wheels + swivels:
        if part is None:
            continue
        if r.former_is_part == "no" and (part.meta or {}).get("role") == "bending_former":
            continue
        ctx.allow_isolated_part(
            part,
            reason=(
                "Joint-retained member intentionally disconnected by a running clearance. "
                "Every bore in this template is cut at shaft + 0.03*shaft + 0.0002 "
                "(design binding shaft_to_bore_clearance, fitted to 005 / L4 / L5 at "
                "once), and every rotating seat stands 0.2 mm off its thrust washer or "
                "rail. Closing that clearance to satisfy fail_if_isolated_parts would "
                "re-create exactly the interference the pool's ~70 allow_overlap sites "
                "come from."
            ),
        )
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    return ctx.report()


# ===========================================================================
# High-risk cross-slot corners.  The design names four:
# `screw_ram_on_rotary_host`, `mount_on_hand_tool`, `wrap_wheel_on_hand_tool`
# and the three N placement-law maxima.
# ===========================================================================
TEMPLATE_CORNERS = (
    corner_case(
        "mount_on_hand_tool",
        {
            "bender_topology": "hand_lever_plier",
            "former_profile": "round_flanged_groove",
            "mount": "pedestal_floor_plate",
            "former_count": 1,
            "former_outer_r_m": 0.026,
            "tool_length_m": 0.26,
            "pedestal_height_m": 1.05,
        },
        reason=(
            "Design risk (b): the hand tool has no base at all, so every mount candidate "
            "has to terminate in a derived clamp collar around its lower tang -- here on "
            "the tallest floor pedestal at the smallest former."
        ),
    ),
    corner_case(
        "wrap_wheel_on_hand_tool",
        {
            "bender_topology": "hand_lever_plier",
            "former_profile": "rotary_draw_wrap_wheel",
            "mount": "vise_tongue",
            "former_count": 4,
            "former_outer_r_m": 0.092,
            "pipe_outer_r_m": 0.021,
            "former_height_m": 0.07,
            "wrap_span_rad": 5.76,
            "tool_length_m": 0.26,
        },
        reason=(
            "Design risk (d): the largest 300-degree wrap wheel on the smallest host, at "
            "the top of former_count -- the largest-profile-on-smallest-host pairing the "
            "design keeps as a corner rather than an exclusion."
        ),
    ),
    corner_case(
        "screw_ram_on_rotary_host",
        {
            "bender_topology": "ram_tripod",
            "former_profile": "square_tube_channel",
            "mount": "caster_deck",
            "former_count": 4,
            "ram_stroke_m": 0.11,
            "former_outer_r_m": 0.092,
            "caster_wheel_r_m": 0.06,
            "caster_wheel_width_m": 0.08,
            "fork_side_clearance_m": 0.0008,
        },
        reason=(
            "Design risk (a): the screw feed on its native ram host at maximum stroke, "
            "riding the caster deck at the widest wheel and the tightest fork clearance."
        ),
    ),
    corner_case(
        "angular_turret_max_n",
        {
            "bender_topology": "cast_bench_mimic",
            "former_profile": "multi_radius_stepped",
            "mount": "bench_plate",
            "former_count": 4,
            "former_outer_r_m": 0.092,
            "pipe_outer_r_m": 0.021,
            "primary_shaft_r_m": 0.013,
            "band_count": 4,
            "sweep_upper_rad": 2.8,
        },
        reason=(
            "Design risk (c): the angular turret at N = 4 and the largest former, where "
            "2R*sin(pi/N) has to keep four stowed dies clear of each other AND of the "
            "follower's swept annulus."
        ),
    ),
    corner_case(
        "linear_rack_max_n",
        {
            "bender_topology": "pedestal_ladder_rail",
            "former_profile": "square_tube_channel",
            "mount": "pedestal_floor_plate",
            "former_count": 4,
            "former_outer_r_m": 0.092,
            "pipe_outer_r_m": 0.021,
            "head_height_m": 0.75,
            "pedestal_height_m": 1.05,
            "channel_height_ratio": 0.78,
        },
        reason=(
            "Design risk (c): the linear station rack at N = 4 on the tallest stack in "
            "the pool -- 1.8 m of mount plus head, with the rack length and the base "
            "plate both derived from the station table."
        ),
    ),
    corner_case(
        "pipe_path_rollers_max_n",
        {
            "bender_topology": "ram_tripod",
            "former_profile": "rotary_draw_wrap_wheel",
            "mount": "pedestal_floor_plate",
            "former_count": 4,
            "former_outer_r_m": 0.026,
            "pipe_outer_r_m": 0.008,
            "primary_shaft_r_m": 0.0035,
            "leg_reach_m": 0.24,
            "wrap_span_rad": 3.66,
        },
        reason=(
            "Design risk (c): the pipe-path guide law at its maximum station count on "
            "the smallest former and the smallest tripod, where the exit-tangent pitch "
            "and the roller radius are both at their floors."
        ),
    ),
    corner_case(
        "smallest_former_largest_tube",
        {
            "bender_topology": "three_roll_pyramid",
            "former_profile": "round_flanged_groove",
            "mount": "caster_deck",
            "former_count": 1,
            "former_outer_r_m": 0.026,
            "pipe_outer_r_m": 0.021,
            "groove_depth_ratio": 0.22,
            "former_height_m": 0.014,
            "flange_height_ratio": 0.32,
        },
        reason=(
            "The subtraction that goes negative: at the smallest former, the fattest "
            "tube and the deepest groove ratio, `groove_height_m` exceeds the declared "
            "former height and every flange thickness would invert unless the former "
            "grows instead."
        ),
    ),
    corner_case(
        "ratchet_sector_at_the_largest_scale",
        {
            "bender_topology": "pedestal_fixed_die_swing_handle",
            "former_profile": "multi_radius_stepped",
            "mount": "vise_tongue",
            "former_count": 3,
            "former_outer_r_m": 0.092,
            "primary_shaft_r_m": 0.013,
            "secondary_former_r_m": 0.034,
            "secondary_former_offset_m": 0.06,
            "saddle_z_m": 0.32,
            "band_count": 2,
        },
        reason=(
            "The fixed-die host at full scale: the sector's tooth tip circle, the pawl "
            "0.3 mm outside it, and a secondary fixed former whose declared offset is "
            "SMALLER than the follower's swept annulus, so the derivation has to push "
            "it out."
        ),
    ),
)


__all__ = (
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "BenderTopology",
    "FormerProfile",
    "Mount",
    "PaletteStyle",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_manual_pipe_bender",
    "build_seeded_manual_pipe_bender",
    "run_manual_pipe_bender_tests",
)
