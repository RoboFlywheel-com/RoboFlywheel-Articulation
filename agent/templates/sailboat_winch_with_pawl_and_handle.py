# SPDX-License-Identifier: Apache-2.0

"""Manual line winch (0611 / sailboat_winch_with_pawl_and_handle).

Design-backed rebuild.  Artifacts:

  * ``articraft_template_authoring/source_maps/sailboat_winch_with_pawl_and_handle.md``
  * ``articraft_template_authoring/designs/sailboat_winch_with_pawl_and_handle.json``
    (filled by ``scripts/design_fill/sailboat_winch_with_pawl_and_handle.py``)

Frame convention
----------------
``z=0`` is the mounting plane and the frame's base structure stands on it.  Every
rotating member is authored in a *drum frame* whose local ``+X`` is its rotation axis
and whose local origin is on that axis, which is what ``mate_axes`` +
``register_interface_mate`` require.  ``frame_family`` decides where that axis sits:

  * ``folded_twin_cheek`` / ``cantilever_front_cheek`` / ``bridged_side_plates`` put it on
    world ``+X`` through ``(0, 0, axis_lift_m)``, radial basis ``r1=+Y``, ``r2=+Z``;
  * ``vertical_capstan_deck`` puts it on world ``+Z``, radial basis ``r1=+X``, ``r2=+Y``.

``u`` below is always the axial coordinate along that axis measured from the drum centre.
The drum's axial stack runs, from ``-u`` to ``+u``: optional self-tailing crown, ``-u``
flange, grooved barrel, ``+u`` flange, optional reduction gears, ratchet ring — then the
far bearing plate, then the crank plane.  Putting the ratchet ring at the outboard end is
what lets the pawl bracket be a short boss on the plate face (source 002 L65-L71) instead
of a bracket reaching across the drum.

Why this file exists
--------------------
The legacy template lifted the drum axis by ``flange_radius + 0.020`` and then hung the
reduction pinion ``ratchet_tip + pinion_r`` *below* that axis, so the ratchet teeth cut
through the base plate and the pinion emerged underneath it — all of it suppressed by a
blanket of ``ctx.allow_overlap`` calls.  Here:

  * ``axis_lift_m`` (or ``pedestal_h_m`` on the capstan) is DERIVED from ``rotating_reach_m``,
    the full envelope of the active line takeup, ratchet and drive coupling;
  * the welded frame solid is then boolean-cut by every rotating member's swept band, so
    the drum bore, the reduction-gear window and the guard shroud's reliefs are real
    openings (MECHANICAL_PRIORS §4, §7);
  * every bore is ``shaft + bore_clearance_m`` (<= 0.8 mm, inside the 1 mm support gap), the
    gear mesh is a tangent pair separated by ``gear_backlash_m``, and the pawl seat is an
    arc cut concentric with the ratchet tip circle;
  * ``ctx.allow_overlap`` is never called.

Gears and ratchet rings are polyline tooth rings rather than involute ``SpurGear`` meshes.
Sources 002 (``_ratchet_wheel`` L97-L117) and 001 (``_toothed_disk`` L61-L88) build their
tooth rings exactly this way; 003's involute pair is the pool's slowest geometry and its
own two-speed fork had to widen the mesh tolerance to 2 mm because of it.
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
    Box,
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
    multiplicity_slot,
    register_interface_mate,
)

# --------------------------------------------------------------------------- #
# Domain
# --------------------------------------------------------------------------- #
FrameFamily = Literal[
    "folded_twin_cheek",
    "cantilever_front_cheek",
    "bridged_side_plates",
    "vertical_capstan_deck",
]
WebRelief = Literal["solid_web", "windowed_web", "enclosed_guard_shell"]
DriveCoupling = Literal[
    "direct_socket_drive",
    "single_reduction",
    "two_speed_reduction",
    "removable_spindle_socket",
]
HandleHead = Literal["spinning_sleeve_grip", "folding_double_grip", "ratcheting_lever_head"]
LineTakeup = Literal["grooved_barrel", "coaxial_strap_spool", "self_tailing_crown"]
RatchetPawl = Literal["hooked_lobe_pawl", "long_release_lever_pawl"]
PaletteStyle = Literal[
    "galvanized_blue",
    "matte_black_steel",
    "gold_zinc",
    "green_zinc",
    "red_black",
    "bright_marine",
]

FRAME_FAMILIES: tuple[FrameFamily, ...] = (
    "folded_twin_cheek",
    "cantilever_front_cheek",
    "bridged_side_plates",
    "vertical_capstan_deck",
)
WEB_RELIEFS: tuple[WebRelief, ...] = ("solid_web", "windowed_web", "enclosed_guard_shell")
DRIVE_COUPLINGS: tuple[DriveCoupling, ...] = (
    "direct_socket_drive",
    "single_reduction",
    "two_speed_reduction",
    "removable_spindle_socket",
)
HANDLE_HEADS: tuple[HandleHead, ...] = (
    "spinning_sleeve_grip",
    "folding_double_grip",
    "ratcheting_lever_head",
)
LINE_TAKEUPS: tuple[LineTakeup, ...] = (
    "grooved_barrel",
    "coaxial_strap_spool",
    "self_tailing_crown",
)
RATCHET_PAWLS: tuple[RatchetPawl, ...] = ("hooked_lobe_pawl", "long_release_lever_pawl")
PAWL_COUNTS: tuple[int, ...] = (1, 2, 3)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "galvanized_blue",
    "matte_black_steel",
    "gold_zinc",
    "green_zinc",
    "red_black",
    "bright_marine",
)

_REDUCTIONS = frozenset({"single_reduction", "two_speed_reduction"})
_VERTICAL = "vertical_capstan_deck"

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "frame_family",
            FRAME_FAMILIES,
            role="source-backed support frame and drum-axis orientation",
        ),
        component_slot(
            "web_relief",
            WEB_RELIEFS,
            role="source-backed treatment of the frame web between the bearing stations",
        ),
        component_slot(
            "drive_coupling",
            DRIVE_COUPLINGS,
            role="source-backed coupling from the hand crank to the drum",
        ),
        component_slot(
            "handle_head",
            HANDLE_HEADS,
            role="source-backed hand interface at the crank tip",
        ),
        component_slot(
            "line_takeup",
            LINE_TAKEUPS,
            role="source-backed line-handling body on the drum",
        ),
        component_slot(
            "ratchet_pawl",
            RATCHET_PAWLS,
            role="source-backed pawl body engaging the ratchet ring",
        ),
        multiplicity_slot("pawl_count", PAWL_COUNTS, item_slot="ratchet_pawl"),
    )
)

# Palette keys: frame chassis, drum barrel, dark ratchet/gear teeth, rubber grip,
# bright hardware (pins, collars, bolts) and a maker-label accent.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "galvanized_blue": {
        "frame": (0.68, 0.70, 0.69, 1.0),
        "drum": (0.80, 0.82, 0.81, 1.0),
        "gear": (0.25, 0.27, 0.27, 1.0),
        "grip": (0.08, 0.19, 0.78, 1.0),
        "hardware": (0.34, 0.36, 0.36, 1.0),
        "accent": (0.86, 0.72, 0.10, 1.0),
    },
    "matte_black_steel": {
        "frame": (0.10, 0.11, 0.12, 1.0),
        "drum": (0.66, 0.69, 0.71, 1.0),
        "gear": (0.12, 0.13, 0.14, 1.0),
        "grip": (0.03, 0.03, 0.035, 1.0),
        "hardware": (0.72, 0.74, 0.75, 1.0),
        "accent": (0.55, 0.57, 0.60, 1.0),
    },
    "gold_zinc": {
        "frame": (0.62, 0.65, 0.66, 1.0),
        "drum": (0.72, 0.56, 0.17, 1.0),
        "gear": (0.55, 0.44, 0.14, 1.0),
        "grip": (0.035, 0.04, 0.04, 1.0),
        "hardware": (0.74, 0.76, 0.76, 1.0),
        "accent": (0.18, 0.46, 0.66, 1.0),
    },
    "green_zinc": {
        "frame": (0.42, 0.48, 0.42, 1.0),
        "drum": (0.66, 0.69, 0.67, 1.0),
        "gear": (0.20, 0.24, 0.20, 1.0),
        "grip": (0.10, 0.42, 0.16, 1.0),
        "hardware": (0.74, 0.76, 0.74, 1.0),
        "accent": (0.84, 0.84, 0.80, 1.0),
    },
    "red_black": {
        "frame": (0.20, 0.21, 0.22, 1.0),
        "drum": (0.58, 0.60, 0.61, 1.0),
        "gear": (0.10, 0.10, 0.11, 1.0),
        "grip": (0.72, 0.10, 0.09, 1.0),
        "hardware": (0.76, 0.78, 0.80, 1.0),
        "accent": (0.84, 0.84, 0.84, 1.0),
    },
    "bright_marine": {
        "frame": (0.72, 0.74, 0.75, 1.0),
        "drum": (0.64, 0.66, 0.67, 1.0),
        "gear": (0.25, 0.27, 0.27, 1.0),
        "grip": (0.06, 0.30, 0.72, 1.0),
        "hardware": (0.34, 0.36, 0.37, 1.0),
        "accent": (0.84, 0.70, 0.10, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Config:
    frame_family: FrameFamily = "folded_twin_cheek"
    web_relief: WebRelief = "solid_web"
    drive_coupling: DriveCoupling = "direct_socket_drive"
    handle_head: HandleHead = "spinning_sleeve_grip"
    line_takeup: LineTakeup = "grooved_barrel"
    ratchet_pawl: RatchetPawl = "hooked_lobe_pawl"
    pawl_count: int = 1
    palette_style: PaletteStyle = "galvanized_blue"

    # frame_family
    base_plate_h_m: float = 0.010
    base_clearance_m: float = 0.014
    plate_thickness_m: float = 0.006
    plate_reach_ratio: float = 1.18
    flange_clearance_m: float = 0.0028
    running_clearance_m: float = 0.0015
    bore_clearance_m: float = 0.0007
    cheek_taper_ratio: float = 0.52
    tie_radius_m: float = 0.0045
    pedestal_ring_ratio: float = 0.84
    foot_width_ratio: float = 0.74
    bridge_span_ratio: float = 0.68
    spacer_count: int = 2
    deck_radius_ratio: float = 1.62
    pedestal_ratio: float = 0.70

    # web_relief
    web_boss_ratio: float = 1.85
    window_count: int = 5
    window_radius_ratio: float = 0.16
    guard_thickness_m: float = 0.0065
    guard_window_span_rad: float = 1.05

    # drive_coupling
    crank_reach_m: float = 0.082
    crank_arm_width_m: float = 0.014
    crank_gap_m: float = 0.011
    coupler_len_m: float = 0.016
    coupler_wall_m: float = 0.0050
    pinion_teeth: int = 12
    drum_gear_teeth: int = 32
    pinion_angle_rad: float = -0.73
    gear_backlash_m: float = 0.0010
    gear_thickness_m: float = 0.0080
    high_speed_pinion_teeth: int = 18
    stage_gap_m: float = 0.0055
    stem_across_m: float = 0.0095
    socket_depth_m: float = 0.026
    withdraw_travel_m: float = 0.014

    # handle_head
    grip_length_m: float = 0.068
    grip_radius_m: float = 0.0120
    grip_pin_radius_m: float = 0.0045
    retainer_radius_ratio: float = 1.14
    second_arm_ratio: float = 0.62
    fold_upper_rad: float = 1.45
    head_radius_m: float = 0.018
    lever_taper_ratio: float = 0.65
    selector_paddle_h_m: float = 0.011

    # line_takeup
    drum_radius_m: float = 0.034
    flange_radius_ratio: float = 1.46
    drum_width_m: float = 0.070
    spindle_radius_m: float = 0.0075
    flange_thickness_m: float = 0.0065
    groove_count: int = 7
    groove_depth_m: float = 0.0024
    spool_outer_ratio: float = 0.80
    spool_width_ratio: float = 0.70
    hub_radius_ratio: float = 0.52
    crown_teeth: int = 40
    crown_tip_ratio: float = 0.90
    stripper_thickness_m: float = 0.0045

    # ratchet_pawl
    ratchet_teeth: int = 22
    ratchet_tip_ratio: float = 1.10
    ratchet_root_ratio: float = 0.86
    ratchet_thickness_m: float = 0.0075
    pawl_ring_gap_m: float = 0.013
    pawl_width_m: float = 0.0070
    pawl_arc_span_rad: float = 1.00
    pawl_pin_radius_m: float = 0.0040
    lobe_radius_ratio: float = 0.70
    lever_reach_ratio: float = 2.3
    thumb_cap_len_m: float = 0.020

    name: str = "sailboat_winch_with_pawl_and_handle"


@dataclass(frozen=True)
class ResolvedConfig:
    frame_family: FrameFamily
    web_relief: WebRelief
    drive_coupling: DriveCoupling
    handle_head: HandleHead
    line_takeup: LineTakeup
    ratchet_pawl: RatchetPawl
    pawl_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]

    # independent, clamped
    base_plate_h_m: float
    base_clearance_m: float
    plate_thickness_m: float
    plate_reach_ratio: float
    flange_clearance_m: float
    running_clearance_m: float
    bore_clearance_m: float
    cheek_taper_ratio: float
    tie_radius_m: float
    pedestal_ring_ratio: float
    foot_width_ratio: float
    bridge_span_ratio: float
    spacer_count: int
    deck_radius_ratio: float
    pedestal_ratio: float
    web_boss_ratio: float
    window_count: int
    window_radius_ratio: float
    guard_thickness_m: float
    guard_window_span_rad: float
    crank_reach_m: float
    crank_arm_width_m: float
    crank_gap_m: float
    coupler_len_m: float
    coupler_wall_m: float
    pinion_teeth: int
    drum_gear_teeth: int
    pinion_angle_rad: float
    gear_backlash_m: float
    gear_thickness_m: float
    high_speed_pinion_teeth: int
    stage_gap_m: float
    stem_across_m: float
    socket_depth_m: float
    withdraw_travel_m: float
    grip_length_m: float
    grip_radius_m: float
    grip_pin_radius_m: float
    retainer_radius_ratio: float
    second_arm_ratio: float
    fold_upper_rad: float
    head_radius_m: float
    lever_taper_ratio: float
    selector_paddle_h_m: float
    drum_radius_m: float
    flange_radius_ratio: float
    drum_width_m: float
    spindle_radius_m: float
    flange_thickness_m: float
    groove_count: int
    groove_depth_m: float
    spool_outer_ratio: float
    spool_width_ratio: float
    hub_radius_ratio: float
    crown_teeth: int
    crown_tip_ratio: float
    stripper_thickness_m: float
    ratchet_teeth: int
    ratchet_tip_ratio: float
    ratchet_root_ratio: float
    ratchet_thickness_m: float
    pawl_ring_gap_m: float
    pawl_width_m: float
    pawl_arc_span_rad: float
    pawl_pin_radius_m: float
    lobe_radius_ratio: float
    lever_reach_ratio: float
    thumb_cap_len_m: float

    # derived
    vertical: bool
    reduction: bool
    removable: bool
    flange_radius_m: float
    ratchet_tip_r_m: float
    ratchet_root_r_m: float
    crown_thickness_m: float
    crown_tip_r_m: float
    crown_root_r_m: float
    spool_outer_r_m: float
    spool_width_m: float
    spool_hub_r_m: float
    spool_bore_r_m: float
    takeup_outer_r_m: float
    plate_gap_m: float
    pre_ratchet_gap_m: float
    ratchet_u_m: float
    gear_u_m: tuple[float, ...]
    gear_module_m: float
    drum_gear_tip_r_m: float
    pinion_tip_r_m: float
    high_speed_drum_gear_teeth: int
    high_speed_gear_tip_r_m: float
    high_speed_pinion_tip_r_m: float
    gear_center_distance_m: float
    pinion_shaft_r_m: float
    pinion_bore_boss_r_m: float
    pinion_low_reach_m: float
    max_drum_radius_m: float
    rotating_reach_m: float
    axis_lift_m: float
    pedestal_h_m: float
    drum_origin_z_m: float
    plate_reach_m: float
    plate_u_near_m: float
    plate_u_far_m: float
    drum_u_min_m: float
    drum_u_max_m: float
    spindle_u_min_m: float
    spindle_u_max_m: float
    crank_u_m: float
    crank_axis_v_m: float
    crank_axis_w_m: float
    pawl_ring_r_m: float
    pawl_pitch_rad: float
    pawl_angles_rad: tuple[float, ...]
    pawl_seat_r_m: float
    pawl_nose_half_w_m: float
    pawl_body_half_w_m: float
    pawl_bore_r_m: float
    pawl_boss_r_m: float
    pawl_travel_rad: float
    pawl_outer_reach_m: float
    ratchet_phase_rad: float
    deck_radius_m: float
    pedestal_outer_r_m: float
    pedestal_inner_r_m: float
    socket_bore_r_m: float
    retained_engagement_m: float
    grip_axis_u_m: float
    crank_origin_u_m: float
    fold_knuckle_len_m: float
    fold_knuckle_offset_m: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x5741_4E43_4801)
    return Config(
        frame_family=choices["frame_family"],
        web_relief=choices["web_relief"],
        drive_coupling=choices["drive_coupling"],
        handle_head=choices["handle_head"],
        line_takeup=choices["line_takeup"],
        ratchet_pawl=choices["ratchet_pawl"],
        pawl_count=int(choices["pawl_count"]),
        palette_style=rng.choice(PALETTE_STYLES),
        base_plate_h_m=round(rng.uniform(0.004, 0.022), 5),
        base_clearance_m=round(rng.uniform(0.006, 0.030), 5),
        plate_thickness_m=round(rng.uniform(0.004, 0.012), 5),
        plate_reach_ratio=round(rng.uniform(1.02, 1.38), 4),
        flange_clearance_m=round(rng.uniform(0.0018, 0.0045), 5),
        running_clearance_m=round(rng.uniform(0.0008, 0.0025), 5),
        bore_clearance_m=round(rng.uniform(0.0006, 0.0008), 5),
        cheek_taper_ratio=round(rng.uniform(0.30, 0.78), 4),
        tie_radius_m=round(rng.uniform(0.0032, 0.0062), 5),
        pedestal_ring_ratio=round(rng.uniform(0.62, 1.00), 4),
        foot_width_ratio=round(rng.uniform(0.55, 1.00), 4),
        bridge_span_ratio=round(rng.uniform(0.45, 0.95), 4),
        spacer_count=rng.choice((2, 3)),
        deck_radius_ratio=round(rng.uniform(1.30, 2.00), 4),
        pedestal_ratio=round(rng.uniform(0.50, 0.90), 4),
        web_boss_ratio=round(rng.uniform(1.35, 2.40), 4),
        window_count=rng.choice((3, 4, 5, 6)),
        window_radius_ratio=round(rng.uniform(0.10, 0.24), 4),
        guard_thickness_m=round(rng.uniform(0.0040, 0.0105), 5),
        guard_window_span_rad=round(rng.uniform(0.65, 1.75), 4),
        crank_reach_m=round(rng.uniform(0.055, 0.125), 5),
        crank_arm_width_m=round(rng.uniform(0.009, 0.020), 5),
        crank_gap_m=round(rng.uniform(0.006, 0.020), 5),
        coupler_len_m=round(rng.uniform(0.010, 0.024), 5),
        coupler_wall_m=round(rng.uniform(0.0030, 0.0075), 5),
        pinion_teeth=rng.choice((10, 12, 14)),
        drum_gear_teeth=rng.choice((28, 32, 36)),
        pinion_angle_rad=round(rng.uniform(-1.05, -0.42), 4),
        gear_backlash_m=round(rng.uniform(0.0006, 0.0016), 5),
        gear_thickness_m=round(rng.uniform(0.006, 0.010), 5),
        high_speed_pinion_teeth=rng.choice((16, 18, 20)),
        stage_gap_m=round(rng.uniform(0.0035, 0.0100), 5),
        stem_across_m=round(rng.uniform(0.0080, 0.0120), 5),
        socket_depth_m=round(rng.uniform(0.020, 0.034), 5),
        withdraw_travel_m=round(rng.uniform(0.010, 0.018), 5),
        grip_length_m=round(rng.uniform(0.050, 0.085), 5),
        grip_radius_m=round(rng.uniform(0.0100, 0.0145), 5),
        grip_pin_radius_m=round(rng.uniform(0.0035, 0.0055), 5),
        retainer_radius_ratio=round(rng.uniform(1.04, 1.38), 4),
        second_arm_ratio=round(rng.uniform(0.40, 1.00), 4),
        fold_upper_rad=round(rng.uniform(1.15, 1.62), 4),
        head_radius_m=round(rng.uniform(0.013, 0.025), 5),
        lever_taper_ratio=round(rng.uniform(0.42, 0.85), 4),
        selector_paddle_h_m=round(rng.uniform(0.007, 0.017), 5),
        drum_radius_m=round(rng.uniform(0.026, 0.046), 5),
        flange_radius_ratio=round(rng.uniform(1.24, 1.78), 4),
        drum_width_m=round(rng.uniform(0.052, 0.100), 5),
        spindle_radius_m=round(rng.uniform(0.0050, 0.0110), 5),
        flange_thickness_m=round(rng.uniform(0.0045, 0.0100), 5),
        groove_count=rng.choice((5, 6, 7, 8, 9)),
        groove_depth_m=round(rng.uniform(0.0015, 0.0034), 5),
        spool_outer_ratio=round(rng.uniform(0.66, 0.94), 4),
        spool_width_ratio=round(rng.uniform(0.55, 0.90), 4),
        hub_radius_ratio=round(rng.uniform(0.40, 0.66), 4),
        crown_teeth=rng.choice((28, 34, 40, 46)),
        crown_tip_ratio=round(rng.uniform(0.82, 1.02), 4),
        stripper_thickness_m=round(rng.uniform(0.0035, 0.0065), 5),
        ratchet_teeth=rng.choice((18, 22, 26, 30)),
        ratchet_tip_ratio=round(rng.uniform(1.02, 1.16), 4),
        ratchet_root_ratio=round(rng.uniform(0.80, 0.92), 4),
        ratchet_thickness_m=round(rng.uniform(0.005, 0.010), 5),
        pawl_ring_gap_m=round(rng.uniform(0.007, 0.020), 5),
        pawl_width_m=round(rng.uniform(0.0040, 0.0100), 5),
        pawl_arc_span_rad=round(rng.uniform(0.55, 1.50), 4),
        pawl_pin_radius_m=round(rng.uniform(0.0030, 0.0048), 5),
        lobe_radius_ratio=round(rng.uniform(0.50, 0.95), 4),
        lever_reach_ratio=round(rng.uniform(1.5, 3.2), 4),
        thumb_cap_len_m=round(rng.uniform(0.012, 0.030), 5),
        name=f"seeded_sailboat_winch_{seed}",
    )


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()

    frame_family = _pick(cfg.frame_family, FRAME_FAMILIES)
    web_relief = _pick(cfg.web_relief, WEB_RELIEFS)
    drive_coupling = _pick(cfg.drive_coupling, DRIVE_COUPLINGS)
    handle_head = _pick(cfg.handle_head, HANDLE_HEADS)
    line_takeup = _pick(cfg.line_takeup, LINE_TAKEUPS)
    ratchet_pawl = _pick(cfg.ratchet_pawl, RATCHET_PAWLS)
    pawl_count = int(_pick(int(cfg.pawl_count), PAWL_COUNTS))
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    vertical = frame_family == _VERTICAL
    reduction = drive_coupling in _REDUCTIONS
    two_speed = drive_coupling == "two_speed_reduction"
    removable = drive_coupling == "removable_spindle_socket"

    base_plate_h = _clamp(cfg.base_plate_h_m, 0.004, 0.022)
    base_clearance = _clamp(cfg.base_clearance_m, 0.006, 0.030)
    plate_t = _clamp(cfg.plate_thickness_m, 0.004, 0.012)
    plate_reach_ratio = _clamp(cfg.plate_reach_ratio, 1.02, 1.38)
    flange_clearance = _clamp(cfg.flange_clearance_m, 0.0018, 0.0045)
    running_clr = _clamp(cfg.running_clearance_m, 0.0008, 0.0025)
    bore_clr = _clamp(cfg.bore_clearance_m, 0.0006, 0.0008)
    cheek_taper = _clamp(cfg.cheek_taper_ratio, 0.30, 0.78)
    tie_r = _clamp(cfg.tie_radius_m, 0.0032, 0.0062)
    pedestal_ring_ratio = _clamp(cfg.pedestal_ring_ratio, 0.62, 1.00)
    foot_width_ratio = _clamp(cfg.foot_width_ratio, 0.55, 1.00)
    bridge_span_ratio = _clamp(cfg.bridge_span_ratio, 0.45, 0.95)
    spacer_count = int(_pick(int(cfg.spacer_count), (2, 3)))
    deck_radius_ratio = _clamp(cfg.deck_radius_ratio, 1.30, 2.00)
    pedestal_ratio = _clamp(cfg.pedestal_ratio, 0.50, 0.90)

    web_boss_ratio = _clamp(cfg.web_boss_ratio, 1.35, 2.40)
    window_count = int(_pick(int(cfg.window_count), (3, 4, 5, 6)))
    window_radius_ratio = _clamp(cfg.window_radius_ratio, 0.10, 0.24)
    guard_t = _clamp(cfg.guard_thickness_m, 0.0040, 0.0105)
    guard_span = _clamp(cfg.guard_window_span_rad, 0.65, 1.75)

    crank_reach = _clamp(cfg.crank_reach_m, 0.055, 0.125)
    crank_arm_w = _clamp(cfg.crank_arm_width_m, 0.009, 0.020)
    crank_gap = _clamp(cfg.crank_gap_m, 0.006, 0.020)
    coupler_len = _clamp(cfg.coupler_len_m, 0.010, 0.024)
    coupler_wall = _clamp(cfg.coupler_wall_m, 0.0030, 0.0075)
    pinion_teeth = int(_pick(int(cfg.pinion_teeth), (10, 12, 14)))
    drum_gear_teeth = int(_pick(int(cfg.drum_gear_teeth), (28, 32, 36)))
    pinion_angle = _clamp(cfg.pinion_angle_rad, -1.05, -0.42)
    gear_backlash = _clamp(cfg.gear_backlash_m, 0.0006, 0.0016)
    gear_t = _clamp(cfg.gear_thickness_m, 0.006, 0.010)
    hs_pinion_teeth = int(_pick(int(cfg.high_speed_pinion_teeth), (16, 18, 20)))
    stage_gap = _clamp(cfg.stage_gap_m, 0.0035, 0.0100)
    stem_across = _clamp(cfg.stem_across_m, 0.0080, 0.0120)
    socket_depth = _clamp(cfg.socket_depth_m, 0.020, 0.034)
    withdraw_travel = _clamp(cfg.withdraw_travel_m, 0.010, 0.018)

    grip_len = _clamp(cfg.grip_length_m, 0.050, 0.085)
    grip_r = _clamp(cfg.grip_radius_m, 0.0100, 0.0145)
    grip_pin_r = _clamp(cfg.grip_pin_radius_m, 0.0035, 0.0055)
    retainer_ratio = _clamp(cfg.retainer_radius_ratio, 1.04, 1.38)
    second_arm_ratio = _clamp(cfg.second_arm_ratio, 0.40, 1.00)
    fold_upper = _clamp(cfg.fold_upper_rad, 1.15, 1.62)
    head_r = _clamp(cfg.head_radius_m, 0.013, 0.025)
    lever_taper = _clamp(cfg.lever_taper_ratio, 0.42, 0.85)
    selector_h = _clamp(cfg.selector_paddle_h_m, 0.007, 0.017)

    drum_r = _clamp(cfg.drum_radius_m, 0.026, 0.046)
    flange_ratio = _clamp(cfg.flange_radius_ratio, 1.24, 1.78)
    drum_w = _clamp(cfg.drum_width_m, 0.052, 0.100)
    spindle_r = _clamp(cfg.spindle_radius_m, 0.0050, 0.0110)
    flange_t = _clamp(cfg.flange_thickness_m, 0.0045, 0.0100)
    groove_count = int(_pick(int(cfg.groove_count), (5, 6, 7, 8, 9)))
    groove_depth = _clamp(cfg.groove_depth_m, 0.0015, 0.0034)
    spool_outer_ratio = _clamp(cfg.spool_outer_ratio, 0.66, 0.94)
    spool_width_ratio = _clamp(cfg.spool_width_ratio, 0.55, 0.90)
    hub_ratio = _clamp(cfg.hub_radius_ratio, 0.40, 0.66)
    crown_teeth = int(_pick(int(cfg.crown_teeth), (28, 34, 40, 46)))
    crown_tip_ratio = _clamp(cfg.crown_tip_ratio, 0.82, 1.02)
    stripper_t = _clamp(cfg.stripper_thickness_m, 0.0035, 0.0065)

    ratchet_teeth = int(_pick(int(cfg.ratchet_teeth), (18, 22, 26, 30)))
    ratchet_tip_ratio = _clamp(cfg.ratchet_tip_ratio, 1.02, 1.16)
    ratchet_root_ratio = _clamp(cfg.ratchet_root_ratio, 0.80, 0.92)
    ratchet_t = _clamp(cfg.ratchet_thickness_m, 0.005, 0.010)
    pawl_ring_gap = _clamp(cfg.pawl_ring_gap_m, 0.007, 0.020)
    pawl_w = _clamp(cfg.pawl_width_m, 0.0040, 0.0100)
    pawl_arc_span = _clamp(cfg.pawl_arc_span_rad, 0.55, 1.50)
    pawl_pin_r = _clamp(cfg.pawl_pin_radius_m, 0.0030, 0.0048)
    lobe_ratio = _clamp(cfg.lobe_radius_ratio, 0.50, 0.95)
    lever_reach_ratio = _clamp(cfg.lever_reach_ratio, 1.5, 3.2)
    thumb_cap_len = _clamp(cfg.thumb_cap_len_m, 0.012, 0.030)

    # --- drum radial envelope ------------------------------------------------
    flange_r = drum_r * flange_ratio
    # A groove cut cannot outrun the barrel wall it is cut into.
    groove_depth = min(groove_depth, 0.35 * (flange_r - drum_r), 0.30 * drum_r)
    ratchet_tip_r = flange_r * ratchet_tip_ratio
    ratchet_root_r = ratchet_tip_r * ratchet_root_ratio
    crown_t = 0.55 * ratchet_t
    crown_tip_r = flange_r * crown_tip_ratio
    crown_root_r = crown_tip_r * 0.90
    spool_hub_r = hub_ratio * drum_r
    spool_bore_r = spool_hub_r + bore_clr
    spool_outer_r = max(spool_outer_ratio * flange_r, spool_bore_r + 0.010)
    spool_outer_r = min(spool_outer_r, flange_r - 0.0015)
    spool_w = spool_width_ratio * drum_w

    if line_takeup == "coaxial_strap_spool":
        takeup_outer_r = spool_outer_r
    else:
        takeup_outer_r = drum_r

    plate_gap = max(flange_clearance, running_clr + 0.0008)

    # --- reduction gears -----------------------------------------------------
    if reduction:
        gear_module = 2.0 * ratchet_tip_r / drum_gear_teeth
        drum_gear_tip_r = gear_module * (drum_gear_teeth / 2.0 + 1.0)
        pinion_tip_r = gear_module * (pinion_teeth / 2.0 + 1.0)
        gear_center_distance = drum_gear_tip_r + pinion_tip_r + gear_backlash
        # Source 003 L291 runs a 4.6 mm shaft under an 18 mm pinion (0.26); a fatter
        # shaft also pushes the frame's bearing collar further than 15 mm off the
        # crank axis, which no longer reads as a supported joint.
        pinion_shaft_r = min(max(0.0040, 0.26 * pinion_tip_r), 0.0105)
        pinion_bore_boss_r = 2.0 * (pinion_shaft_r + bore_clr)
        hs_pinion_tip_r = gear_module * (hs_pinion_teeth / 2.0 + 1.0)
        hs_gear_tip_target = gear_center_distance - gear_backlash - hs_pinion_tip_r
        hs_gear_teeth = max(16, int(round(2.0 * (hs_gear_tip_target / gear_module - 1.0))))
        hs_gear_tip_r = gear_module * (hs_gear_teeth / 2.0 + 1.0)
    else:
        gear_module = 0.0
        drum_gear_tip_r = 0.0
        pinion_tip_r = 0.0
        gear_center_distance = 0.0
        pinion_shaft_r = 0.0
        pinion_bore_boss_r = 0.0
        hs_pinion_tip_r = 0.0
        hs_gear_teeth = 0
        hs_gear_tip_r = 0.0

    # --- axial stack ---------------------------------------------------------
    gear_planes: list[float] = []
    stack_u = drum_w / 2.0 + flange_t
    if reduction:
        stack_u += plate_gap + gear_t / 2.0
        gear_planes.append(stack_u)
        stack_u += gear_t / 2.0
        if two_speed:
            stack_u += stage_gap + gear_t / 2.0
            gear_planes.append(stack_u)
            stack_u += gear_t / 2.0
    # The pawl body is coplanar with the ratchet ring, so the gap before the ring and
    # the far bearing station both have to make room for it.
    pawl_band_half = pawl_w / 2.0
    pre_ratchet_gap = max(plate_gap, pawl_band_half - ratchet_t / 2.0 + 0.0012)
    ratchet_u = stack_u + pre_ratchet_gap + ratchet_t / 2.0
    drum_u_max = ratchet_u + ratchet_t / 2.0
    drum_stack_hi = max(drum_u_max, ratchet_u + pawl_band_half + 0.0012)

    drum_u_min = -(drum_w / 2.0 + flange_t)
    crown_u = 0.0
    if line_takeup == "self_tailing_crown":
        crown_u = drum_u_min - plate_gap - crown_t / 2.0
        drum_u_min = crown_u - crown_t / 2.0

    plate_u_near = drum_u_min - plate_gap - plate_t / 2.0
    plate_u_far = drum_stack_hi + plate_gap + plate_t / 2.0

    # --- pawls ---------------------------------------------------------------
    # The pivot ring is floored so the pawl bracket, and (on the capstan) the post
    # that carries it, always clear the reduction gear tip circle.
    ring_gap = pawl_ring_gap
    if reduction:
        ring_gap = max(
            ring_gap,
            max(drum_gear_tip_r, hs_gear_tip_r) - ratchet_tip_r + running_clr + 0.002,
        )
    pawl_ring_r = ratchet_tip_r + ring_gap
    tooth_pitch_rad = 2.0 * math.pi / ratchet_teeth
    tooth_pitch_len = tooth_pitch_rad * ratchet_tip_r
    # A concentric seat wider than this dips into the tip circle when the pawl
    # swings; the bound keeps that dip under 1.5 mm.
    nose_half_w = min(0.60 * tooth_pitch_len, math.sqrt(0.0015 * 2.0 * ring_gap))
    nose_half_w = max(nose_half_w, 0.0020)
    if pawl_count > 1:
        min_pitch = (2.0 * nose_half_w + 0.004) / pawl_ring_r
        target_pitch = max(pawl_arc_span / (pawl_count - 1), min_pitch)
        steps = max(1, int(round(target_pitch / tooth_pitch_rad)))
        pawl_pitch = steps * tooth_pitch_rad
        while pawl_pitch < min_pitch:
            steps += 1
            pawl_pitch = steps * tooth_pitch_rad
    else:
        pawl_pitch = tooth_pitch_rad
    base_angle = math.pi / 2.0 - pawl_pitch * (pawl_count - 1) / 2.0
    pawl_angles = tuple(base_angle + i * pawl_pitch for i in range(pawl_count))
    pawl_body_half_w = min(0.014, max(nose_half_w + 0.0015, 0.40 * pawl_ring_r * pawl_pitch))
    pawl_bore_r = pawl_pin_r + bore_clr
    pawl_boss_r = 2.1 * pawl_pin_r
    pawl_seat_r = ratchet_tip_r + 0.0004
    if ratchet_pawl == "hooked_lobe_pawl":
        pawl_outer_reach = max(lobe_ratio * ring_gap, pawl_boss_r + 0.002)
    else:
        pawl_outer_reach = lever_reach_ratio * ring_gap + thumb_cap_len
    # Travel is bounded by the neighbouring pawl: two adjacent bodies swinging
    # toward each other close the gap by 2*reach*sin(travel), and a long release
    # lever closes it far faster than a compact lobe does.
    pawl_travel = 0.40
    if pawl_count > 1:
        room = (
            (pawl_ring_r + pawl_outer_reach) * pawl_pitch
            - 2.0 * pawl_body_half_w
            - 0.004
        )
        pawl_travel = max(
            0.08,
            min(
                0.40,
                math.asin(
                    _clamp(room / (2.0 * max(pawl_outer_reach, 1e-4)), 0.0, 0.99)
                ),
            ),
        )
    # A tooth crest is centred under every pawl at drum pose 0 because the pivot
    # pitch is an integer number of teeth.
    ratchet_phase = base_angle

    # --- host sizing ---------------------------------------------------------
    max_drum_radius = max(flange_r, ratchet_tip_r, takeup_outer_r, drum_gear_tip_r, hs_gear_tip_r)
    if not reduction:
        pinion_low_reach = 0.0
    elif vertical:
        # The capstan spends its clearance axially, so what matters radially is how
        # far the offset pinion stands out from the drum axis.
        pinion_low_reach = gear_center_distance + max(pinion_tip_r, hs_pinion_tip_r)
    else:
        pinion_low_reach = max(pinion_tip_r, hs_pinion_tip_r) + gear_center_distance * abs(
            math.sin(pinion_angle)
        )
    rotating_reach = max(max_drum_radius, pinion_low_reach)

    axis_lift = base_plate_h + base_clearance + rotating_reach
    pedestal_h = max(2.0 * plate_t, 0.012)

    plate_reach = plate_reach_ratio * rotating_reach
    plate_reach = max(plate_reach, pawl_ring_r + pawl_boss_r + 0.004)
    if reduction and not vertical:
        # The plate has to keep a continuous rim around the pinion window it is cut
        # for, otherwise the envelope cut severs the cheek into loose islands.
        plate_reach = max(
            plate_reach,
            gear_center_distance * math.cos(pinion_angle)
            + max(pinion_tip_r, hs_pinion_tip_r)
            + running_clr
            + 0.006,
        )
    deck_radius = max(deck_radius_ratio * rotating_reach, plate_reach)
    pedestal_outer_r = min(
        max(pedestal_ratio * rotating_reach, spindle_r + 0.010), deck_radius - 0.006
    )
    pedestal_inner_r = max(spindle_r + bore_clr, pedestal_outer_r * 0.55)

    if vertical:
        drum_origin_z = base_plate_h + pedestal_h + base_clearance - drum_u_min
        plate_u_near = drum_u_min - base_clearance - pedestal_h / 2.0
    else:
        drum_origin_z = axis_lift

    # --- crank station -------------------------------------------------------
    # Every crank feature — the coupling sleeve, the ratchet head, the folding
    # knuckle — has to clear the frame's outermost face, so the station is derived
    # from whichever of them reaches furthest inboard.
    crank_arm_half = crank_arm_w / 2.0
    fold_knuckle_r = max(grip_r * 0.80, grip_pin_r + bore_clr + 0.0025)
    crank_extra = crank_arm_half
    if drive_coupling == "direct_socket_drive":
        crank_extra = max(crank_extra, coupler_len + 0.002)
    if handle_head == "folding_double_grip":
        crank_extra = max(crank_extra, fold_knuckle_r + 0.0025)
    if handle_head == "ratcheting_lever_head":
        crank_extra = max(crank_extra, crank_arm_w * 0.45)
    frame_end_u = (
        drum_stack_hi + 0.004 if vertical else plate_u_far + plate_t / 2.0
    )
    crank_u = frame_end_u + crank_gap + crank_extra
    if removable:
        crank_u = max(crank_u, drum_u_max + socket_depth + 0.006 + crank_arm_half + 0.002)
    if reduction:
        crank_axis_v = gear_center_distance * math.cos(pinion_angle)
        crank_axis_w = gear_center_distance * math.sin(pinion_angle)
        if vertical:
            crank_axis_w = 0.0
            crank_axis_v = gear_center_distance
    else:
        crank_axis_v = 0.0
        crank_axis_w = 0.0

    # The crank's local origin sits inside its own body so the joint origin is never
    # far from the geometry it drives.
    if removable:
        stem_lo = drum_u_max + 0.006
        crank_origin_u = (stem_lo + crank_u) / 2.0
    else:
        crank_origin_u = frame_end_u + 0.004

    socket_bore_r = 0.5 * stem_across * math.sqrt(2.0) + bore_clr
    if removable:
        # The spindle wall has to survive the square bore, so the spindle grows to
        # the stem instead of the socket being clamped down below it (source 002
        # L120-L130 runs a 0.008 spindle around a 0.0095 stem).
        spindle_r = max(spindle_r, socket_bore_r + 0.0014)
        withdraw_travel = min(withdraw_travel, socket_depth - 0.008)
    retained_engagement = socket_depth - withdraw_travel

    # --- spindle -------------------------------------------------------------
    spindle_u_min = plate_u_near - plate_t / 2.0 - 0.004
    if removable:
        spindle_u_max = drum_u_max + socket_depth + 0.006
    elif drive_coupling == "direct_socket_drive":
        # The crank arm's root crosses the drive axis, so the spindle has to end
        # before it, not merely before the crank plane.
        spindle_u_max = crank_u - crank_arm_w * 0.31 - 0.0015
    else:
        spindle_u_max = frame_end_u + 0.004
    spindle_u_max = max(spindle_u_max, drum_u_max + 0.004)

    grip_axis_u = crank_u
    fold_knuckle_len = grip_r * 1.9
    crank_tip_half = (
        crank_arm_w / 2.0 * (lever_taper if handle_head == "ratcheting_lever_head" else 0.72)
    )
    fold_knuckle_offset = crank_tip_half + fold_knuckle_len / 2.0 + 0.0015

    return ResolvedConfig(
        frame_family=frame_family,
        web_relief=web_relief,
        drive_coupling=drive_coupling,
        handle_head=handle_head,
        line_takeup=line_takeup,
        ratchet_pawl=ratchet_pawl,
        pawl_count=pawl_count,
        palette_style=palette_style,
        palette=PALETTES[palette_style],
        base_plate_h_m=base_plate_h,
        base_clearance_m=base_clearance,
        plate_thickness_m=plate_t,
        plate_reach_ratio=plate_reach_ratio,
        flange_clearance_m=flange_clearance,
        running_clearance_m=running_clr,
        bore_clearance_m=bore_clr,
        cheek_taper_ratio=cheek_taper,
        tie_radius_m=tie_r,
        pedestal_ring_ratio=pedestal_ring_ratio,
        foot_width_ratio=foot_width_ratio,
        bridge_span_ratio=bridge_span_ratio,
        spacer_count=spacer_count,
        deck_radius_ratio=deck_radius_ratio,
        pedestal_ratio=pedestal_ratio,
        web_boss_ratio=web_boss_ratio,
        window_count=window_count,
        window_radius_ratio=window_radius_ratio,
        guard_thickness_m=guard_t,
        guard_window_span_rad=guard_span,
        crank_reach_m=crank_reach,
        crank_arm_width_m=crank_arm_w,
        crank_gap_m=crank_gap,
        coupler_len_m=coupler_len,
        coupler_wall_m=coupler_wall,
        pinion_teeth=pinion_teeth,
        drum_gear_teeth=drum_gear_teeth,
        pinion_angle_rad=pinion_angle,
        gear_backlash_m=gear_backlash,
        gear_thickness_m=gear_t,
        high_speed_pinion_teeth=hs_pinion_teeth,
        stage_gap_m=stage_gap,
        stem_across_m=stem_across,
        socket_depth_m=socket_depth,
        withdraw_travel_m=withdraw_travel,
        grip_length_m=grip_len,
        grip_radius_m=grip_r,
        grip_pin_radius_m=grip_pin_r,
        retainer_radius_ratio=retainer_ratio,
        second_arm_ratio=second_arm_ratio,
        fold_upper_rad=fold_upper,
        head_radius_m=head_r,
        lever_taper_ratio=lever_taper,
        selector_paddle_h_m=selector_h,
        drum_radius_m=drum_r,
        flange_radius_ratio=flange_ratio,
        drum_width_m=drum_w,
        spindle_radius_m=spindle_r,
        flange_thickness_m=flange_t,
        groove_count=groove_count,
        groove_depth_m=groove_depth,
        spool_outer_ratio=spool_outer_ratio,
        spool_width_ratio=spool_width_ratio,
        hub_radius_ratio=hub_ratio,
        crown_teeth=crown_teeth,
        crown_tip_ratio=crown_tip_ratio,
        stripper_thickness_m=stripper_t,
        ratchet_teeth=ratchet_teeth,
        ratchet_tip_ratio=ratchet_tip_ratio,
        ratchet_root_ratio=ratchet_root_ratio,
        ratchet_thickness_m=ratchet_t,
        pawl_ring_gap_m=ring_gap,
        pawl_width_m=pawl_w,
        pawl_arc_span_rad=pawl_arc_span,
        pawl_pin_radius_m=pawl_pin_r,
        lobe_radius_ratio=lobe_ratio,
        lever_reach_ratio=lever_reach_ratio,
        thumb_cap_len_m=thumb_cap_len,
        vertical=vertical,
        reduction=reduction,
        removable=removable,
        flange_radius_m=flange_r,
        ratchet_tip_r_m=ratchet_tip_r,
        ratchet_root_r_m=ratchet_root_r,
        crown_thickness_m=crown_t,
        crown_tip_r_m=crown_tip_r,
        crown_root_r_m=crown_root_r,
        spool_outer_r_m=spool_outer_r,
        spool_width_m=spool_w,
        spool_hub_r_m=spool_hub_r,
        spool_bore_r_m=spool_bore_r,
        takeup_outer_r_m=takeup_outer_r,
        plate_gap_m=plate_gap,
        pre_ratchet_gap_m=pre_ratchet_gap,
        ratchet_u_m=ratchet_u,
        gear_u_m=tuple(gear_planes),
        gear_module_m=gear_module,
        drum_gear_tip_r_m=drum_gear_tip_r,
        pinion_tip_r_m=pinion_tip_r,
        high_speed_drum_gear_teeth=hs_gear_teeth,
        high_speed_gear_tip_r_m=hs_gear_tip_r,
        high_speed_pinion_tip_r_m=hs_pinion_tip_r,
        gear_center_distance_m=gear_center_distance,
        pinion_shaft_r_m=pinion_shaft_r,
        pinion_bore_boss_r_m=pinion_bore_boss_r,
        pinion_low_reach_m=pinion_low_reach,
        max_drum_radius_m=max_drum_radius,
        rotating_reach_m=rotating_reach,
        axis_lift_m=axis_lift,
        pedestal_h_m=pedestal_h,
        drum_origin_z_m=drum_origin_z,
        plate_reach_m=plate_reach,
        plate_u_near_m=plate_u_near,
        plate_u_far_m=plate_u_far,
        drum_u_min_m=drum_u_min,
        drum_u_max_m=drum_u_max,
        spindle_u_min_m=spindle_u_min,
        spindle_u_max_m=spindle_u_max,
        crank_u_m=crank_u,
        crank_axis_v_m=crank_axis_v,
        crank_axis_w_m=crank_axis_w,
        pawl_ring_r_m=pawl_ring_r,
        pawl_pitch_rad=pawl_pitch,
        pawl_angles_rad=pawl_angles,
        pawl_seat_r_m=pawl_seat_r,
        pawl_nose_half_w_m=nose_half_w,
        pawl_body_half_w_m=pawl_body_half_w,
        pawl_bore_r_m=pawl_bore_r,
        pawl_boss_r_m=pawl_boss_r,
        pawl_travel_rad=pawl_travel,
        pawl_outer_reach_m=pawl_outer_reach,
        ratchet_phase_rad=ratchet_phase,
        deck_radius_m=deck_radius,
        pedestal_outer_r_m=pedestal_outer_r,
        pedestal_inner_r_m=pedestal_inner_r,
        socket_bore_r_m=socket_bore_r,
        retained_engagement_m=retained_engagement,
        grip_axis_u_m=grip_axis_u,
        crank_origin_u_m=crank_origin_u,
        fold_knuckle_len_m=fold_knuckle_len,
        fold_knuckle_offset_m=fold_knuckle_offset,
        name=cfg.name or "sailboat_winch_with_pawl_and_handle",
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, object]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return {
        "frame_family": r.frame_family,
        "web_relief": r.web_relief,
        "drive_coupling": r.drive_coupling,
        "handle_head": r.handle_head,
        "line_takeup": r.line_takeup,
        "ratchet_pawl": r.ratchet_pawl,
        "pawl_count": r.pawl_count,
    }


def slot_choices_for_seed(seed: int) -> dict[str, object]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Frame-agnostic axial helpers
# --------------------------------------------------------------------------- #
def _axis_dir(r: ResolvedConfig) -> tuple[float, float, float]:
    return (0.0, 0.0, 1.0) if r.vertical else (1.0, 0.0, 0.0)


def _r1(r: ResolvedConfig) -> tuple[float, float, float]:
    return (1.0, 0.0, 0.0) if r.vertical else (0.0, 1.0, 0.0)


def _r2(r: ResolvedConfig) -> tuple[float, float, float]:
    return (0.0, 1.0, 0.0) if r.vertical else (0.0, 0.0, 1.0)


def _world(r: ResolvedConfig, u: float, v: float, w: float) -> tuple[float, float, float]:
    if r.vertical:
        return (v, w, r.drum_origin_z_m + u)
    return (u, v, r.drum_origin_z_m + w)


def _radial(r: ResolvedConfig, angle: float) -> tuple[float, float, float]:
    r1 = _r1(r)
    r2 = _r2(r)
    return (
        r1[0] * math.cos(angle) + r2[0] * math.sin(angle),
        r1[1] * math.cos(angle) + r2[1] * math.sin(angle),
        r1[2] * math.cos(angle) + r2[2] * math.sin(angle),
    )


def _band(
    r: ResolvedConfig,
    *,
    u0: float,
    u1: float,
    radius: float,
    inner: float | None = None,
    v: float = 0.0,
    w: float = 0.0,
) -> cq.Workplane:
    """A cylinder/annulus in world space, aligned with the drum axis."""

    plane = "XY" if r.vertical else "YZ"
    wp = cq.Workplane(plane).circle(radius)
    if inner is not None and inner > 1e-6:
        wp = wp.circle(inner)
    solid = wp.extrude(u1 - u0)
    if r.vertical:
        return solid.translate((v, w, r.drum_origin_z_m + u0))
    return solid.translate((u0, v, r.drum_origin_z_m + w))


# --------------------------------------------------------------------------- #
# Drum-local CadQuery helpers (local +X is always the rotation axis)
# --------------------------------------------------------------------------- #
def _cyl_x(radius: float, length: float, xc: float = 0.0) -> cq.Workplane:
    return cq.Workplane("YZ").circle(radius).extrude(length).translate((xc - length / 2.0, 0.0, 0.0))


def _tube_x(ro: float, ri: float, length: float, xc: float = 0.0) -> cq.Workplane:
    return (
        cq.Workplane("YZ")
        .circle(ro)
        .circle(ri)
        .extrude(length)
        .translate((xc - length / 2.0, 0.0, 0.0))
    )


def _tooth_ring_x(
    *,
    tip_r: float,
    root_r: float,
    teeth: int,
    thickness: float,
    xc: float,
    bore_r: float,
    phase: float = 0.0,
    ratchet: bool = True,
) -> cq.Workplane:
    """Polyline tooth ring in the local YZ plane, extruded along local X.

    `phase` places a tooth crest centre at that angle, which is how the pawl seat
    and the gear mesh get a deterministic contact at pose 0.  `ratchet=True` gives
    the asymmetric sawtooth of source 002 `_ratchet_wheel`; `ratchet=False` gives a
    symmetric gear tooth.
    """

    pitch = 2.0 * math.pi / teeth
    if ratchet:
        profile = ((0.00, root_r), (0.62, tip_r), (0.78, tip_r), (0.86, root_r))
        crest_phase = 0.70
    else:
        profile = ((0.00, root_r), (0.22, tip_r), (0.48, tip_r), (0.70, root_r))
        crest_phase = 0.35
    start = phase - crest_phase * pitch
    points: list[tuple[float, float]] = []
    for index in range(teeth):
        base = start + index * pitch
        for fraction, radius in profile:
            angle = base + fraction * pitch
            points.append((radius * math.cos(angle), radius * math.sin(angle)))
    ring = (
        cq.Workplane("YZ")
        .polyline(points)
        .close()
        .extrude(thickness)
        .translate((xc - thickness / 2.0, 0.0, 0.0))
    )
    if bore_r > 1e-6:
        ring = ring.cut(_cyl_x(bore_r, thickness * 3.0, xc))
    return ring


def _plate_yz(
    r: ResolvedConfig,
    points: list[tuple[float, float]],
    thickness: float,
    xc: float,
) -> cq.Workplane:
    """Bearing-plate silhouette authored in the radial (r1, r2) plane and lifted onto
    the drum axis, so the profile's flat bottom lands on the base structure."""

    return (
        cq.Workplane("YZ")
        .polyline(points)
        .close()
        .extrude(thickness)
        .translate((xc - thickness / 2.0, 0.0, r.drum_origin_z_m))
    )


# Every running fit in this template is a sub-millimetre clearance (bores are
# `shaft + bore_clearance_m <= 0.8 mm`), so the tessellation sagitta has to stay well
# under that or the meshed bore chords eat the clearance and read as a collision.
_MESH_TOLERANCE = 0.00018


def _mesh(shape: cq.Workplane, name: str, tolerance: float = _MESH_TOLERANCE) -> object:
    return mesh_from_cadquery(
        shape, name, tolerance=min(tolerance, _MESH_TOLERANCE), angular_tolerance=0.06
    )


# --------------------------------------------------------------------------- #
# line_takeup -- drum body
# --------------------------------------------------------------------------- #
def _drum_barrel_shape(r: ResolvedConfig) -> cq.Workplane:
    half = r.drum_width_m / 2.0
    body = _cyl_x(r.drum_radius_m, r.drum_width_m, 0.0)
    body = body.union(_cyl_x(r.flange_radius_m, r.flange_thickness_m, half + r.flange_thickness_m / 2.0))
    body = body.union(
        _cyl_x(r.flange_radius_m, r.flange_thickness_m, -half - r.flange_thickness_m / 2.0)
    )
    return body


def _line_takeup_grooved_barrel_build(r: ResolvedConfig) -> cq.Workplane:
    """Grooves are CUT out of the barrel (source 002 `_drum_core` L88-L94), so the
    swept envelope is exactly `drum_radius_m`."""

    body = _drum_barrel_shape(r)
    half = r.drum_width_m / 2.0
    span = r.drum_width_m - 0.010
    if r.groove_count > 1 and span > 0.0:
        width = min(0.0032, span / (r.groove_count * 2.2))
        for index in range(r.groove_count):
            xg = -span / 2.0 + span * index / (r.groove_count - 1)
            cutter = _tube_x(
                r.drum_radius_m + 0.004,
                r.drum_radius_m - r.groove_depth_m,
                width,
                xg,
            )
            body = body.cut(cutter)
    # Rope anchor pin on the barrel, source 002 L333-L341.
    body = body.union(
        cq.Workplane("YZ")
        .center(r.drum_radius_m - r.groove_depth_m * 0.4, 0.0)
        .circle(0.0032)
        .extrude(0.006)
        .translate((-half + 0.010, 0.0, 0.0))
    )
    return body


def _line_takeup_coaxial_strap_spool_build(r: ResolvedConfig) -> cq.Workplane:
    """Source 001 L296-L336: the captured spool IS the working barrel, so the drum
    keeps only a plain drive hub between its flanges for the spool bore to ride."""

    half = r.drum_width_m / 2.0
    body = _cyl_x(r.spool_hub_r_m, r.drum_width_m + 0.004, 0.0)
    body = body.union(
        _cyl_x(r.flange_radius_m, r.flange_thickness_m, half + r.flange_thickness_m / 2.0)
    )
    body = body.union(
        _cyl_x(r.flange_radius_m, r.flange_thickness_m, -half - r.flange_thickness_m / 2.0)
    )
    return body


def _line_takeup_self_tailing_crown_build(r: ResolvedConfig) -> cq.Workplane:
    body = _line_takeup_grooved_barrel_build(r)
    crown_u = r.drum_u_min_m + r.crown_thickness_m / 2.0
    body = body.union(
        _tooth_ring_x(
            tip_r=r.crown_tip_r_m,
            root_r=r.crown_root_r_m,
            teeth=r.crown_teeth,
            thickness=r.crown_thickness_m,
            xc=crown_u,
            bore_r=0.0,
            ratchet=False,
        )
    )
    return body


_TAKEUP_BUILDERS = {
    "grooved_barrel": _line_takeup_grooved_barrel_build,
    "coaxial_strap_spool": _line_takeup_coaxial_strap_spool_build,
    "self_tailing_crown": _line_takeup_self_tailing_crown_build,
}


def _drum_shape(r: ResolvedConfig) -> cq.Workplane:
    body = _TAKEUP_BUILDERS[r.line_takeup](r)
    # Spindle across both bearing stations.
    body = body.union(
        _cyl_x(
            r.spindle_radius_m,
            r.spindle_u_max_m - r.spindle_u_min_m,
            (r.spindle_u_max_m + r.spindle_u_min_m) / 2.0,
        )
    )
    # Ratchet ring, phased so a crest sits under every pawl at pose 0.
    body = body.union(
        _tooth_ring_x(
            tip_r=r.ratchet_tip_r_m,
            root_r=r.ratchet_root_r_m,
            teeth=r.ratchet_teeth,
            thickness=r.ratchet_thickness_m,
            xc=r.ratchet_u_m,
            bore_r=0.0,
            phase=r.ratchet_phase_rad,
        )
    )
    # Reduction gears, phased toward the pinion so the mesh is deterministic.
    if r.reduction:
        gear_phase = r.pinion_angle_rad if not r.vertical else 0.0
        specs = [(r.gear_u_m[0], r.drum_gear_teeth, r.drum_gear_tip_r_m)]
        if r.drive_coupling == "two_speed_reduction" and len(r.gear_u_m) > 1:
            specs.append((r.gear_u_m[1], r.high_speed_drum_gear_teeth, r.high_speed_gear_tip_r_m))
        for gear_u, teeth, tip in specs:
            body = body.union(
                _tooth_ring_x(
                    tip_r=tip,
                    root_r=tip - 2.2 * r.gear_module_m,
                    teeth=teeth,
                    thickness=r.gear_thickness_m,
                    xc=gear_u,
                    bore_r=0.0,
                    phase=gear_phase,
                    ratchet=False,
                )
            )
    if r.removable:
        # Square socket bored into the outboard spindle end.
        socket = (
            cq.Workplane("YZ")
            .rect(r.socket_bore_r_m * 2.0 / math.sqrt(2.0) * 1.02, r.socket_bore_r_m * 2.0 / math.sqrt(2.0) * 1.02)
            .extrude(r.socket_depth_m + 0.004)
            .translate((r.spindle_u_max_m - r.socket_depth_m - 0.002, 0.0, 0.0))
        )
        body = body.cut(socket)
    return body


# --------------------------------------------------------------------------- #
# Envelope cutters -- the slots the frame has to give the moving parts
# --------------------------------------------------------------------------- #
def _rotating_envelopes(r: ResolvedConfig) -> list[cq.Workplane]:
    clr = r.running_clearance_m
    bands: list[cq.Workplane] = []
    half = r.drum_width_m / 2.0
    # barrel + both flanges + the two flange faces
    bands.append(
        _band(
            r,
            u0=-half - r.flange_thickness_m - clr,
            u1=half + r.flange_thickness_m + clr,
            radius=r.flange_radius_m + clr,
        )
    )
    # ratchet ring
    bands.append(
        _band(
            r,
            u0=r.ratchet_u_m - r.ratchet_thickness_m / 2.0 - clr,
            u1=r.ratchet_u_m + r.ratchet_thickness_m / 2.0 + clr,
            radius=r.ratchet_tip_r_m + clr,
        )
    )
    if r.line_takeup == "self_tailing_crown":
        crown_u = r.drum_u_min_m + r.crown_thickness_m / 2.0
        bands.append(
            _band(
                r,
                u0=crown_u - r.crown_thickness_m / 2.0 - clr,
                u1=crown_u + r.crown_thickness_m / 2.0 + clr,
                radius=r.crown_tip_r_m + clr,
            )
        )
    if r.line_takeup == "coaxial_strap_spool":
        bands.append(
            _band(
                r,
                u0=-r.spool_width_m / 2.0 - clr,
                u1=r.spool_width_m / 2.0 + clr,
                radius=r.spool_outer_r_m + clr,
            )
        )
    if r.reduction:
        specs = [(r.gear_u_m[0], r.drum_gear_tip_r_m, r.pinion_tip_r_m)]
        if r.drive_coupling == "two_speed_reduction" and len(r.gear_u_m) > 1:
            specs.append((r.gear_u_m[1], r.high_speed_gear_tip_r_m, r.high_speed_pinion_tip_r_m))
        for gear_u, gear_tip, pinion_tip in specs:
            bands.append(
                _band(
                    r,
                    u0=gear_u - r.gear_thickness_m / 2.0 - clr,
                    u1=gear_u + r.gear_thickness_m / 2.0 + clr,
                    radius=gear_tip + clr,
                )
            )
            bands.append(
                _band(
                    r,
                    u0=gear_u - r.gear_thickness_m / 2.0 - clr,
                    u1=gear_u + r.gear_thickness_m / 2.0 + clr,
                    radius=pinion_tip + clr,
                    v=r.crank_axis_v_m,
                    w=r.crank_axis_w_m,
                )
            )
        # pinion shaft bore through every frame plate it crosses
        bands.append(
            _band(
                r,
                u0=min(r.gear_u_m) - 0.03,
                u1=r.crank_u_m + 0.01,
                radius=r.pinion_shaft_r_m + r.bore_clearance_m,
                v=r.crank_axis_v_m,
                w=r.crank_axis_w_m,
            )
        )
    # spindle bore
    bands.append(
        _band(
            r,
            u0=r.spindle_u_min_m - 0.01,
            u1=r.spindle_u_max_m + 0.01,
            radius=r.spindle_radius_m + r.bore_clearance_m,
        )
    )
    if r.drive_coupling == "direct_socket_drive":
        # the coupling sleeve turns inside the frame's outboard bearing collar
        bands.append(
            _band(
                r,
                u0=r.crank_origin_u_m - 0.004,
                u1=r.crank_u_m + 0.02,
                radius=r.spindle_radius_m
                + r.bore_clearance_m
                + r.coupler_wall_m * 1.9
                + clr,
            )
        )
    return bands


def _cut_envelopes(solid: cq.Workplane, r: ResolvedConfig) -> cq.Workplane:
    for band in _rotating_envelopes(r):
        solid = solid.cut(band)
    return solid


# --------------------------------------------------------------------------- #
# frame_family
# --------------------------------------------------------------------------- #
def _plate_outline(r: ResolvedConfig, *, taper: float, crown: float) -> list[tuple[float, float]]:
    """Bearing-plate silhouette in the (r1, r2) radial plane, flat-bottomed on the
    base structure exactly as every horizontal source plate is."""

    reach = r.plate_reach_m
    floor = -(r.axis_lift_m - r.base_plate_h_m)
    top = reach * crown
    return [
        (-reach, floor),
        (reach, floor),
        (reach, top * 0.42),
        (reach * taper, top),
        (-reach * taper, top),
        (-reach, top * 0.42),
    ]


def _web_relief_solid_web_build(
    solid: cq.Workplane, r: ResolvedConfig, plate_u: list[float]
) -> cq.Workplane:
    """Continuous web with a raised bearing boss over each bore (source 002
    L252-L260 front bushing, 001 L210-L215 bearing collar)."""

    boss_r = r.web_boss_ratio * (r.spindle_radius_m + r.bore_clearance_m)
    if r.vertical:
        # On the deck family the boss sits in the pedestal's open centre, so it has to
        # reach the pedestal bore or it is a ring floating in the socket.
        boss_r = max(boss_r, r.pedestal_inner_r_m + 0.002)
    for u in plate_u:
        solid = solid.union(
            _band(
                r,
                u0=u - r.plate_thickness_m / 2.0 - 0.0025,
                u1=u + r.plate_thickness_m / 2.0 + 0.0025,
                radius=boss_r,
            )
        )
    return solid


def _web_relief_windowed_web_build(
    solid: cq.Workplane, r: ResolvedConfig, plate_u: list[float]
) -> cq.Workplane:
    """Circular lightening windows on a ring between the bore boss and the rim,
    leaving a continuous perimeter (open_cheek_reel fork L92-L107).

    The window radius is capped against the ring pitch as well as the rim, because
    windows that merge into each other leave hair-thin webs that survive in CAD and
    then fall apart into islands once the plate is tessellated.
    """

    boss_r = 1.9 * (r.spindle_radius_m + r.bore_clearance_m)
    if r.vertical:
        # the deck flange is the web here, and the pedestal keeps the bore boss
        solid = solid.union(
            _band(
                r,
                u0=plate_u[0] - r.plate_thickness_m / 2.0 - 0.0025,
                u1=plate_u[0] + r.plate_thickness_m / 2.0 + 0.0025,
                radius=max(boss_r, r.pedestal_inner_r_m + 0.002),
            )
        )
        bands = [
            (
                r.base_plate_h_m * 0.5 - r.drum_origin_z_m - r.base_plate_h_m,
                r.base_plate_h_m * 0.5 - r.drum_origin_z_m + r.base_plate_h_m,
            )
        ]
        inner_limit = r.pedestal_outer_r_m
        # windows stay inboard of the deck's fastener ring
        outer_limit = (r.pedestal_outer_r_m + r.deck_radius_m) / 2.0
    else:
        bands = [(u - r.plate_thickness_m, u + r.plate_thickness_m) for u in plate_u]
        inner_limit = boss_r
        outer_limit = r.plate_reach_m

    window_r = r.window_radius_ratio * outer_limit
    ring_r = min(
        outer_limit - window_r - 0.006,
        max((inner_limit + outer_limit) / 2.0, r.max_drum_radius_m * 0.60),
    )
    if ring_r <= inner_limit + window_r + 0.004:
        return solid
    # windows must not merge into their neighbours around the ring
    window_r = min(window_r, 0.40 * 2.0 * ring_r * math.sin(math.pi / r.window_count))
    window_r = min(window_r, ring_r - inner_limit - 0.004, outer_limit - ring_r - 0.006)
    if window_r < 0.004:
        return solid
    # Windows are clocked half a step off +r2 and any that would land on a pawl
    # gusset are skipped, so a lightening hole can never cut a pivot off its cheek.
    keep_out = (window_r + r.pawl_boss_r_m + 0.004) / max(ring_r, 1e-6)
    for index in range(r.window_count):
        angle = math.pi / 2.0 + 2.0 * math.pi * (index + 0.5) / r.window_count
        if any(
            abs(((angle - pawl + math.pi) % (2.0 * math.pi)) - math.pi) < keep_out
            for pawl in r.pawl_angles_rad
        ):
            continue
        for u0, u1 in bands:
            solid = solid.cut(
                _band(
                    r,
                    u0=u0,
                    u1=u1,
                    radius=window_r,
                    v=ring_r * math.cos(angle),
                    w=ring_r * math.sin(angle),
                )
            )
    return solid


def _web_relief_enclosed_guard_shell_build(
    solid: cq.Workplane, r: ResolvedConfig, plate_u: list[float]
) -> cq.Workplane:
    """Curved shroud around the drum with one angular fairlead window; the rotating
    envelopes are re-cut out of it afterwards, which is the correction the enclosed
    fork makes at L108-L112."""

    del plate_u
    guard_lo = r.drum_u_min_m - r.plate_gap_m
    if r.vertical:
        # the shroud becomes a skirt standing on the deck, which is also what carries it
        guard_lo = r.base_plate_h_m - r.drum_origin_z_m
    guard_hi = min(
        r.ratchet_u_m - r.ratchet_thickness_m / 2.0 - r.pre_ratchet_gap_m, r.drum_u_max_m
    )
    if guard_hi - guard_lo <= 0.010:
        return solid
    inner = r.max_drum_radius_m + r.running_clearance_m + 0.0015
    shell = _band(
        r,
        u0=guard_lo,
        u1=guard_hi,
        radius=inner + r.guard_thickness_m,
        inner=inner,
    )
    half = r.guard_window_span_rad / 2.0
    reach = inner + r.guard_thickness_m + 0.01
    window_pts = [(0.0, 0.0)]
    steps = 8
    for step in range(steps + 1):
        angle = -half + r.guard_window_span_rad * step / steps
        window_pts.append((reach * math.cos(angle), reach * math.sin(angle)))
    plane = "XY" if r.vertical else "YZ"
    window = (
        cq.Workplane(plane).polyline(window_pts).close().extrude(guard_hi - guard_lo + 0.004)
    )
    if r.vertical:
        window = window.translate((0.0, 0.0, r.drum_origin_z_m + guard_lo - 0.002))
    else:
        window = window.translate((guard_lo - 0.002, 0.0, r.drum_origin_z_m))
    return solid.union(shell.cut(window))


_WEB_BUILDERS = {
    "solid_web": _web_relief_solid_web_build,
    "windowed_web": _web_relief_windowed_web_build,
    "enclosed_guard_shell": _web_relief_enclosed_guard_shell_build,
}


def _apply_web_relief(solid: cq.Workplane, r: ResolvedConfig, plate_u: list[float]) -> cq.Workplane:
    return _WEB_BUILDERS[r.web_relief](solid, r, plate_u)


def _flange_span(r: ResolvedConfig) -> tuple[float, float, float]:
    """Axial span and radial half-width of the grounded mounting flange, shared by the
    frame builder, the bolt slots and the bolt heads so they can never drift apart."""

    lo = r.plate_u_near_m - r.plate_thickness_m / 2.0
    hi = r.plate_u_far_m + r.plate_thickness_m / 2.0
    if r.frame_family == "bridged_side_plates":
        span = r.plate_u_far_m - r.plate_u_near_m
        bridge = r.bridge_span_ratio * span
        mid = (r.plate_u_near_m + r.plate_u_far_m) / 2.0
        return mid - bridge / 2.0, mid + bridge / 2.0, r.plate_reach_m
    if r.frame_family == "cantilever_front_cheek":
        ring_r = min(
            max(r.pedestal_ring_ratio * r.plate_reach_m, r.max_drum_radius_m * 0.55),
            r.plate_reach_m,
        )
        return lo, hi, max(r.foot_width_ratio * r.plate_reach_m, ring_r * 0.75)
    return lo, hi, r.plate_reach_m


def _base_flange(r: ResolvedConfig, half_v: float, u0: float, u1: float) -> cq.Workplane:
    return cq.Workplane("XY").box(u1 - u0, 2.0 * half_v, r.base_plate_h_m).translate(
        ((u0 + u1) / 2.0, 0.0, r.base_plate_h_m / 2.0)
    )


def _bolt_slots(r: ResolvedConfig, half_v: float, u0: float, u1: float) -> list[cq.Workplane]:
    slots = []
    for u in (u0 + (u1 - u0) * 0.18, u0 + (u1 - u0) * 0.82):
        for v in (-half_v * 0.66, half_v * 0.66):
            slots.append(
                cq.Workplane("XY")
                .box(0.012, 0.026, r.base_plate_h_m * 3.0)
                .translate((u, v, r.base_plate_h_m / 2.0))
            )
    return slots


def _frame_family_folded_twin_cheek_build(r: ResolvedConfig) -> cq.Workplane:
    outline = _plate_outline(r, taper=r.cheek_taper_ratio, crown=1.0)
    solid = _plate_yz(r, outline, r.plate_thickness_m, r.plate_u_near_m)
    solid = solid.union(_plate_yz(r, outline, r.plate_thickness_m, r.plate_u_far_m))
    flange_lo, flange_hi, half_v = _flange_span(r)
    solid = solid.union(_base_flange(r, half_v, flange_lo, flange_hi))
    # The tie sits on the +r1 side, clear of the pawl arc, which is centred on +r2.
    tie_v = max(
        0.80 * r.plate_reach_m,
        r.max_drum_radius_m + r.running_clearance_m + r.tie_radius_m + 0.003,
    )
    tie_v = min(tie_v, r.plate_reach_m - r.tie_radius_m - 0.002)
    solid = solid.union(
        _band(
            r,
            u0=r.plate_u_near_m,
            u1=r.plate_u_far_m,
            radius=r.tie_radius_m,
            v=tie_v,
        )
    )
    for slot in _bolt_slots(r, half_v, flange_lo, flange_hi):
        solid = solid.cut(slot)
    return _apply_web_relief(solid, r, [r.plate_u_near_m, r.plate_u_far_m])


def _frame_family_cantilever_front_cheek_build(r: ResolvedConfig) -> cq.Workplane:
    outline = _plate_outline(r, taper=0.62, crown=1.0)
    solid = _plate_yz(r, outline, r.plate_thickness_m, r.plate_u_far_m)
    ring_r = max(r.pedestal_ring_ratio * r.plate_reach_m, r.max_drum_radius_m * 0.55)
    ring_r = min(ring_r, r.plate_reach_m)
    solid = solid.union(
        _band(
            r,
            u0=r.plate_u_near_m - r.plate_thickness_m / 2.0,
            u1=r.plate_u_near_m + r.plate_thickness_m / 2.0,
            radius=ring_r,
            inner=max(0.0, r.spindle_radius_m + r.bore_clearance_m),
        )
    )
    # stem web carrying the pedestal ring down to the mounting foot
    stem_h = r.axis_lift_m - r.base_plate_h_m
    solid = solid.union(
        cq.Workplane("XY")
        .box(r.plate_thickness_m * 1.6, ring_r * 1.3, stem_h)
        .translate((r.plate_u_near_m, 0.0, r.base_plate_h_m + stem_h / 2.0))
    )
    flange_lo, flange_hi, half_v = _flange_span(r)
    solid = solid.union(_base_flange(r, half_v, flange_lo, flange_hi))
    for slot in _bolt_slots(r, half_v, flange_lo, flange_hi):
        solid = solid.cut(slot)
    return _apply_web_relief(solid, r, [r.plate_u_far_m])


def _frame_family_bridged_side_plates_build(r: ResolvedConfig) -> cq.Workplane:
    outline = _plate_outline(r, taper=0.74, crown=0.92)
    solid = _plate_yz(r, outline, r.plate_thickness_m, r.plate_u_near_m)
    solid = solid.union(_plate_yz(r, outline, r.plate_thickness_m, r.plate_u_far_m))
    bridge_lo, bridge_hi, half_v = _flange_span(r)
    # A continuous narrow rail carries both bearing stations; the wide bridge pad
    # sits on it, which is what keeps the base one load path at any bridge span.
    solid = solid.union(
        _base_flange(
            r,
            half_v * 0.42,
            r.plate_u_near_m - r.plate_thickness_m / 2.0,
            r.plate_u_far_m + r.plate_thickness_m / 2.0,
        )
    )
    solid = solid.union(_base_flange(r, half_v, bridge_lo, bridge_hi))
    spacer_r = max(0.0045, r.tie_radius_m)
    lo = max(
        r.max_drum_radius_m + r.running_clearance_m + spacer_r + 0.003,
        r.plate_reach_m * 0.55,
    )
    # Spacer stations avoid the pawl arc around +r2 entirely (source 001 L236-L244
    # puts both of its spacers on the line of the drum axis, not above it).
    spacer_angles = (0.0, math.pi, -0.55)[: r.spacer_count]
    for angle in spacer_angles:
        radius = min(lo, r.plate_reach_m - spacer_r - 0.002)
        solid = solid.union(
            _band(
                r,
                u0=r.plate_u_near_m,
                u1=r.plate_u_far_m,
                radius=spacer_r,
                v=radius * math.cos(angle),
                w=radius * math.sin(angle),
            )
        )
    for slot in _bolt_slots(r, half_v, bridge_lo, bridge_hi):
        solid = solid.cut(slot)
    return _apply_web_relief(solid, r, [r.plate_u_near_m, r.plate_u_far_m])


def _frame_family_vertical_capstan_deck_build(r: ResolvedConfig) -> cq.Workplane:
    deck = cq.Workplane("XY").circle(r.deck_radius_m).extrude(r.base_plate_h_m)
    ped_outer = r.pedestal_outer_r_m
    ped_inner = r.pedestal_inner_r_m
    solid = deck.union(
        cq.Workplane("XY")
        .circle(ped_outer)
        .circle(ped_inner)
        .extrude(r.pedestal_h_m)
        .translate((0.0, 0.0, r.base_plate_h_m))
    )
    # four rotated deck fastener slots (capstan source L67-L82)
    for index in range(4):
        angle = math.pi / 4.0 + index * math.pi / 2.0
        radius = (ped_outer + r.deck_radius_m) / 2.0
        solid = solid.cut(
            cq.Workplane("XY")
            .box(0.012, 0.026, r.base_plate_h_m * 3.0)
            .rotate((0, 0, 0), (0, 0, 1), math.degrees(angle))
            .translate((radius * math.cos(angle), radius * math.sin(angle), r.base_plate_h_m / 2.0))
        )
    return _apply_web_relief(solid, r, [r.plate_u_near_m])


_FRAME_BUILDERS = {
    "folded_twin_cheek": _frame_family_folded_twin_cheek_build,
    "cantilever_front_cheek": _frame_family_cantilever_front_cheek_build,
    "bridged_side_plates": _frame_family_bridged_side_plates_build,
    "vertical_capstan_deck": _frame_family_vertical_capstan_deck_build,
}


def _pawl_support(solid: cq.Workplane, r: ResolvedConfig) -> cq.Workplane:
    """Pivot boss, pin and retaining washer per pawl.

    Everything lives axially OUTSIDE the pawl's own band, so the pawl body never
    shares material with its support and no swept cut is needed.
    """

    band_lo = r.ratchet_u_m - r.pawl_width_m / 2.0
    band_hi = r.ratchet_u_m + r.pawl_width_m / 2.0
    for index, angle in enumerate(r.pawl_angles_rad):
        v = r.pawl_ring_r_m * math.cos(angle)
        w = r.pawl_ring_r_m * math.sin(angle)
        if r.vertical:
            boss_lo = r.base_plate_h_m - r.drum_origin_z_m
            boss_hi = band_hi + 0.0006
            solid = solid.union(
                _band(r, u0=boss_lo, u1=band_lo - 0.0006, radius=r.pawl_boss_r_m, v=v, w=w)
            )
            solid = solid.union(
                _band(
                    r,
                    u0=band_lo - 0.004,
                    u1=boss_hi,
                    radius=r.pawl_pin_radius_m,
                    v=v,
                    w=w,
                )
            )
            solid = solid.union(
                _band(
                    r,
                    u0=boss_hi,
                    u1=boss_hi + 0.0022,
                    radius=r.pawl_boss_r_m * 0.85,
                    v=v,
                    w=w,
                )
            )
        else:
            plate_inner = r.plate_u_far_m - r.plate_thickness_m / 2.0
            # A gusset pad in the plate's own thickness carries the pivot out to the
            # ring, so the boss lands on the cheek whatever silhouette it has.
            inner_r = 0.5 * r.plate_reach_m
            outer_r = r.pawl_ring_r_m + r.pawl_boss_r_m
            if outer_r > inner_r + 0.004:
                pad = (
                    cq.Workplane("YZ")
                    .rect(outer_r - inner_r, 2.0 * r.pawl_boss_r_m)
                    .extrude(r.plate_thickness_m)
                    .translate((0.0, (inner_r + outer_r) / 2.0, 0.0))
                    .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), math.degrees(angle))
                    .translate(
                        (
                            r.plate_u_far_m - r.plate_thickness_m / 2.0,
                            0.0,
                            r.drum_origin_z_m,
                        )
                    )
                )
                solid = solid.union(pad)
            solid = solid.union(
                _band(r, u0=band_hi + 0.0006, u1=plate_inner, radius=r.pawl_boss_r_m, v=v, w=w)
            )
            solid = solid.union(
                _band(
                    r,
                    u0=band_lo - 0.0028,
                    u1=plate_inner,
                    radius=r.pawl_pin_radius_m,
                    v=v,
                    w=w,
                )
            )
            solid = solid.union(
                _band(
                    r,
                    u0=band_lo - 0.0028,
                    u1=band_lo - 0.0006,
                    radius=r.pawl_boss_r_m * 0.85,
                    v=v,
                    w=w,
                )
            )
    return solid


def _crank_bearing(solid: cq.Workplane, r: ResolvedConfig) -> cq.Workplane:
    """Frame hardware on the crank axis.

    A bearing-mounted crank has to be carried by the frame, so the frame reaches out
    to the crank's own station: a collar on the outer plate face for the cheek
    families (source 003 L210-L223 bearing collars), and a deck stanchion plus a top
    yoke for the capstan, whose crank sits above the drum instead of beside a plate.
    The stanchion stands clear of the pinion's own tip circle, because a column on
    the shaft centreline would be sliced apart by the gear-plane reliefs.
    """

    if r.removable:
        return solid
    collar_r = (
        (r.pinion_shaft_r_m if r.reduction else r.spindle_radius_m + r.coupler_wall_m * 1.9)
        + r.bore_clearance_m
        + 0.0035
    )
    if not r.vertical:
        u0 = r.plate_u_far_m - r.plate_thickness_m / 2.0
        u1 = r.crank_origin_u_m + 0.004
        if u1 > u0:
            solid = solid.union(
                _band(
                    r,
                    u0=u0,
                    u1=u1,
                    radius=collar_r,
                    v=r.crank_axis_v_m,
                    w=r.crank_axis_w_m,
                )
            )
        return solid

    axis_r = math.hypot(r.crank_axis_v_m, r.crank_axis_w_m)
    post_r = max(
        r.max_drum_radius_m + r.running_clearance_m + 0.012,
        axis_r + max(r.pinion_tip_r_m, r.high_speed_pinion_tip_r_m) + r.running_clearance_m + 0.012,
        collar_r + 0.010,
    )
    post_r = min(post_r, max(r.deck_radius_m - 0.006, collar_r + 0.008))
    bar_u0 = r.crank_origin_u_m - r.plate_thickness_m / 2.0
    bar_u1 = r.crank_origin_u_m + r.plate_thickness_m / 2.0
    solid = solid.union(
        _band(
            r,
            u0=r.base_plate_h_m - r.drum_origin_z_m,
            u1=bar_u1,
            radius=r.plate_thickness_m * 1.2,
            v=post_r,
            w=0.0,
        )
    )
    bar_len = post_r - axis_r
    if bar_len > 0.002:
        bar = cq.Workplane("XY").box(bar_len, r.plate_thickness_m * 2.4, bar_u1 - bar_u0)
        solid = solid.union(
            bar.translate(
                (
                    axis_r + bar_len / 2.0,
                    0.0,
                    r.drum_origin_z_m + (bar_u0 + bar_u1) / 2.0,
                )
            )
        )
    solid = solid.union(
        _band(
            r,
            u0=bar_u0,
            u1=bar_u1,
            radius=collar_r,
            v=r.crank_axis_v_m,
            w=r.crank_axis_w_m,
        )
    )
    return solid


def _stripper_bridge(solid: cq.Workplane, r: ResolvedConfig) -> cq.Workplane:
    """Fixed self-tailing stripper that clears the rotating crown (source fork
    L268-L301)."""

    if r.line_takeup != "self_tailing_crown":
        return solid
    standoff = r.crown_tip_r_m + r.running_clearance_m + 0.0015
    crown_u = r.drum_u_min_m + r.crown_thickness_m / 2.0
    u0 = crown_u - r.crown_thickness_m / 2.0 - r.plate_gap_m - r.stripper_thickness_m
    u1 = u0 + r.stripper_thickness_m
    if r.vertical:
        u0 = crown_u + r.crown_thickness_m / 2.0 + r.plate_gap_m
        u1 = u0 + r.stripper_thickness_m
    reach = max(r.plate_reach_m, standoff + r.stripper_thickness_m * 5.0 + 0.008)
    plane = "XY" if r.vertical else "YZ"
    pts = [
        (standoff * math.cos(0.35), standoff * math.sin(0.35)),
        (reach * math.cos(0.20), reach * math.sin(0.20)),
        (reach * math.cos(-0.30), reach * math.sin(-0.30)),
        (standoff * math.cos(-0.45), standoff * math.sin(-0.45)),
    ]
    blade = cq.Workplane(plane).polyline(pts).close().extrude(u1 - u0)
    if r.vertical:
        blade = blade.translate((0.0, 0.0, r.drum_origin_z_m + u0))
        # On the deck family there is no near plate to pin the blade to, so it gets a
        # real stanchion down to the deck (source fork L296-L301 pins its stripper to
        # the rear cheek for the same reason).
        leg_r = r.stripper_thickness_m * 1.6
        # Outside the crown's swept band, or the band cut would slice the leg in two.
        stand_at = min(standoff + leg_r + 0.0015, reach - leg_r - 0.002)
        blade = blade.union(
            _band(
                r,
                u0=r.base_plate_h_m - r.drum_origin_z_m,
                u1=u1,
                radius=leg_r,
                v=stand_at * math.cos(0.02),
                w=stand_at * math.sin(0.02),
            )
        )
    else:
        blade = blade.translate((u0, 0.0, r.drum_origin_z_m))
    return solid.union(blade)


def _build_frame(model: ArticulatedObject, r: ResolvedConfig):
    solid = _FRAME_BUILDERS[r.frame_family](r)
    solid = _pawl_support(solid, r)
    solid = _crank_bearing(solid, r)
    solid = _stripper_bridge(solid, r)
    solid = _cut_envelopes(solid, r)

    frame = model.part(
        "frame",
        meta={
            "role": "winch_frame",
            "frame_family": r.frame_family,
            "web_relief": r.web_relief,
        },
    )
    frame.visual(
        _mesh(solid, f"frame__{r.frame_family}__body", tolerance=0.0007),
        material="frame",
        name=f"frame__{r.frame_family}__body", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_blue", "matte_black_steel", "gold_zinc", "green_zinc", "red_black"} else "metal.stainless_matte"),
    )
    # Bright mounting-bolt heads in the flange slots.
    if r.vertical:
        bolt_r = (r.pedestal_outer_r_m + r.deck_radius_m) / 2.0
        stations = [
            (
                bolt_r * math.cos(math.pi / 4.0 + i * math.pi / 2.0),
                bolt_r * math.sin(math.pi / 4.0 + i * math.pi / 2.0),
            )
            for i in range(4)
        ]
    else:
        u0, u1, half_v = _flange_span(r)
        stations = [
            (u0 + (u1 - u0) * fu, half_v * 0.66 * fv)
            for fu in (0.18, 0.82)
            for fv in (-1.0, 1.0)
        ]
    for index, (a, b) in enumerate(stations):
        # The head is wider than the 12 mm slot it sits in, so it lands on the flange
        # instead of floating inside the opening.
        frame.visual(
            Cylinder(radius=0.0082, length=0.0040),
            origin=Origin(xyz=(a, b, r.base_plate_h_m - 0.0008)),
            material="hardware",
            name=f"frame__{r.frame_family}__mount_bolt_{index}", material_class_id="metal.stainless_matte",
        )
    return frame


# --------------------------------------------------------------------------- #
# ratchet_pawl bodies (authored about the pivot: +X axis, +Y radially outward)
# --------------------------------------------------------------------------- #
def _pawl_seat_cut(r: ResolvedConfig, thickness: float) -> cq.Workplane:
    """Arc concentric with the ratchet tip circle, so the seat rides the crests at
    a fixed `pawl_seat_r_m - ratchet_tip_r_m` clearance instead of digging in."""

    return (
        cq.Workplane("YZ")
        .center(-r.pawl_ring_r_m, 0.0)
        .circle(r.pawl_seat_r_m)
        .extrude(thickness * 3.0)
        .translate((-thickness * 1.5, 0.0, 0.0))
    )


def _ratchet_pawl_hooked_lobe_pawl_build(r: ResolvedConfig) -> cq.Workplane:
    """Compact stop: round pivot lobe plus a short hooked tooth (source 002
    `_pawl_body` L175-L206)."""

    t = r.pawl_width_m
    lobe_r = max(r.pawl_outer_reach_m, r.pawl_boss_r_m + 0.0015)
    body = cq.Workplane("YZ").circle(lobe_r).extrude(t).translate((-t / 2.0, 0.0, 0.0))
    nose_w = r.pawl_nose_half_w_m
    hook = (
        cq.Workplane("YZ")
        .polyline(
            [
                (-r.pawl_ring_gap_m - 0.002, -nose_w),
                (-r.pawl_ring_gap_m - 0.002, nose_w),
                (-lobe_r * 0.30, nose_w + 0.0022),
                (-lobe_r * 0.30, -nose_w - 0.0022),
            ]
        )
        .close()
        .extrude(t)
        .translate((-t / 2.0, 0.0, 0.0))
    )
    body = body.union(hook)
    body = body.cut(_pawl_seat_cut(r, t))
    body = body.cut(_cyl_x(r.pawl_bore_r_m, t * 3.0, 0.0))
    return body


def _ratchet_pawl_long_release_lever_pawl_build(r: ResolvedConfig) -> cq.Workplane:
    """Hooked tooth plus a long hand-release lever ending in a thumb cap (source
    003 `_build_pawl_shape` L142-L163)."""

    t = r.pawl_width_m
    nose_w = r.pawl_nose_half_w_m
    lever = r.lever_reach_ratio * r.pawl_ring_gap_m
    hub_r = max(r.pawl_boss_r_m + 0.0018, nose_w + 0.0022)
    body = cq.Workplane("YZ").circle(hub_r).extrude(t).translate((-t / 2.0, 0.0, 0.0))
    body = body.union(
        cq.Workplane("YZ")
        .polyline(
            [
                (-r.pawl_ring_gap_m - 0.002, -nose_w),
                (-r.pawl_ring_gap_m - 0.002, nose_w),
                (0.0, nose_w + 0.0022),
                (0.0, -nose_w - 0.0022),
            ]
        )
        .close()
        .extrude(t)
        .translate((-t / 2.0, 0.0, 0.0))
    )
    body = body.union(
        cq.Workplane("YZ")
        .polyline(
            [
                (0.0, -hub_r * 0.75),
                (0.0, hub_r * 0.75),
                (lever, hub_r * 0.42),
                (lever, -hub_r * 0.42),
            ]
        )
        .close()
        .extrude(t * 0.8)
        .translate((-t * 0.4, 0.0, 0.0))
    )
    body = body.cut(_pawl_seat_cut(r, t))
    body = body.cut(_cyl_x(r.pawl_bore_r_m, t * 3.0, 0.0))
    return body


_PAWL_BUILDERS = {
    "hooked_lobe_pawl": _ratchet_pawl_hooked_lobe_pawl_build,
    "long_release_lever_pawl": _ratchet_pawl_long_release_lever_pawl_build,
}


def _build_pawls(model: ArticulatedObject, r: ResolvedConfig, frame) -> list:
    shape = _PAWL_BUILDERS[r.ratchet_pawl](r)
    mesh = _mesh(shape, f"ratchet_pawl__{r.ratchet_pawl}__body", tolerance=0.00045)
    pawls = []
    for index, angle in enumerate(r.pawl_angles_rad):
        pawl = model.part(
            f"pawl_{index}",
            meta={"role": "ratchet_pawl", "pawl_index": index, "candidate": r.ratchet_pawl},
        )
        pawl.visual(
            mesh,
            material="hardware",
            name=f"ratchet_pawl__{r.ratchet_pawl}__body_{index}", material_class_id="metal.stainless_matte",
        )
        if r.ratchet_pawl == "long_release_lever_pawl":
            lever = r.lever_reach_ratio * r.pawl_ring_gap_m
            pawl.visual(
                Box((r.pawl_width_m * 1.4, r.thumb_cap_len_m, r.pawl_body_half_w_m * 1.3)),
                origin=Origin(xyz=(0.0, lever + r.thumb_cap_len_m / 2.0 - 0.0015, 0.0)),
                material="grip",
                name=f"ratchet_pawl__{r.ratchet_pawl}__thumb_cap_{index}", material_class_id="rubber.smooth_plain",
            )
        pivot = _world(
            r,
            r.ratchet_u_m,
            r.pawl_ring_r_m * math.cos(angle),
            r.pawl_ring_r_m * math.sin(angle),
        )
        mate = mate_axes(
            AxisInterface(
                name=f"frame.pawl_pivot_{index}",
                point=pivot,
                axis=_axis_dir(r),
                radial=_radial(r, angle),
                radius=r.pawl_bore_r_m,
            ),
            AxisInterface(
                name=f"pawl_{index}.bore",
                point=(0.0, 0.0, 0.0),
                axis=(1.0, 0.0, 0.0),
                radial=(0.0, 1.0, 0.0),
                radius=r.pawl_pin_radius_m,
            ),
        )
        joint = model.articulation(
            f"frame_to_pawl_{index}",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=pawl,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(
                lower=-r.pawl_travel_rad,
                upper=r.pawl_travel_rad,
                effort=10.0,
                velocity=6.0,
            ),
            meta={"role": "ratchet engagement and release"},
        )
        register_interface_mate(model, joint.name, mate)
        pawls.append(pawl)
    return pawls


# --------------------------------------------------------------------------- #
# drive_coupling + handle_head
# --------------------------------------------------------------------------- #
def _drive_coupling_direct_socket_drive_build(r: ResolvedConfig) -> cq.Workplane:
    """Bored coupling sleeve capturing the projecting drum spindle, plus a solid
    outboard stub (direct_drive fork L292-L316).  The sleeve runs all the way back to
    the frame's bearing face so the crank is carried, not cantilevered off nothing."""

    bore = r.spindle_radius_m + r.bore_clearance_m
    lo = r.crank_origin_u_m - 0.002
    hi = r.crank_u_m
    sleeve = _tube_x(bore + r.coupler_wall_m, bore, hi - lo, (hi + lo) / 2.0)
    grip_len = min(r.coupler_len_m, hi - lo)
    sleeve = sleeve.union(
        _tube_x(bore + r.coupler_wall_m * 1.9, bore, grip_len, hi - grip_len / 2.0)
    )
    stub = _cyl_x(bore + r.coupler_wall_m * 1.9, 0.010, r.crank_u_m + 0.005)
    return sleeve.union(stub)


def _reduction_pinion_shaft(r: ResolvedConfig, specs) -> cq.Workplane:
    """Pinion shaft plus one polyline pinion per stage, each phased toward the drum
    so the mesh contact is deterministic at pose 0."""

    shaft_lo = min(r.gear_u_m) - r.gear_thickness_m / 2.0 - 0.006
    shaft_hi = r.crank_u_m + r.crank_arm_width_m * 0.4
    body = _cyl_x(r.pinion_shaft_r_m, shaft_hi - shaft_lo, (shaft_hi + shaft_lo) / 2.0)
    phase = math.pi + (r.pinion_angle_rad if not r.vertical else 0.0)
    for gear_u, teeth, tip in specs:
        body = body.union(
            _tooth_ring_x(
                tip_r=tip,
                root_r=max(tip - 2.2 * r.gear_module_m, r.pinion_shaft_r_m + 0.0015),
                teeth=teeth,
                thickness=r.gear_thickness_m,
                xc=gear_u,
                bore_r=0.0,
                phase=phase,
                ratchet=False,
            )
        )
    return body


def _drive_coupling_single_reduction_build(r: ResolvedConfig) -> cq.Workplane:
    return _reduction_pinion_shaft(
        r, [(r.gear_u_m[0], r.pinion_teeth, r.pinion_tip_r_m)]
    )


def _drive_coupling_two_speed_reduction_build(r: ResolvedConfig) -> cq.Workplane:
    specs = [(r.gear_u_m[0], r.pinion_teeth, r.pinion_tip_r_m)]
    if len(r.gear_u_m) > 1:
        specs.append(
            (r.gear_u_m[1], r.high_speed_pinion_teeth, r.high_speed_pinion_tip_r_m)
        )
    return _reduction_pinion_shaft(r, specs)


def _drive_coupling_removable_spindle_socket_build(r: ResolvedConfig) -> cq.Workplane:
    """Square male stem sliding in the drum's spindle socket (source 002 L356-L367
    tightened by the removable fork L369-L378)."""

    stem_lo = r.spindle_u_max_m - r.socket_depth_m
    stem_hi = r.crank_u_m
    body = (
        cq.Workplane("YZ")
        .rect(r.stem_across_m, r.stem_across_m)
        .extrude(stem_hi - stem_lo)
        .translate((stem_lo, 0.0, 0.0))
    )
    # hex nut plus cap washer at the head
    body = body.union(
        cq.Workplane("YZ")
        .polygon(6, r.stem_across_m * 1.9)
        .extrude(0.005)
        .translate((r.crank_u_m + r.crank_arm_width_m * 0.32, 0.0, 0.0))
    )
    return body


def _crank_head_shape(r: ResolvedConfig) -> cq.Workplane:
    if r.handle_head == "ratcheting_lever_head":
        head = _cyl_x(r.head_radius_m, r.crank_arm_width_m * 0.75, r.crank_u_m)
        cover_x = r.crank_u_m + r.crank_arm_width_m * 0.42
        cover = _cyl_x(r.head_radius_m * 0.78, 0.0035, cover_x)
        # The boss and paddle start INSIDE the cover disc; starting at its outer face
        # would leave them as floating islands inside the crank part.
        stack_x = cover_x + 0.0008
        boss = (
            cq.Workplane("YZ")
            .polygon(6, r.head_radius_m * 0.42)
            .extrude(0.0028)
            .translate((stack_x, 0.0, 0.0))
        )
        paddle = (
            cq.Workplane("YZ")
            .polyline(
                [
                    (-0.004, r.head_radius_m * 0.20),
                    (0.004, r.head_radius_m * 0.20),
                    (0.006, r.head_radius_m * 0.20 + r.selector_paddle_h_m),
                    (-0.006, r.head_radius_m * 0.20 + r.selector_paddle_h_m),
                ]
            )
            .close()
            .extrude(0.0030)
            .translate((stack_x, 0.0, 0.0))
        )
        return head.union(cover).union(boss).union(paddle)
    return _cyl_x(max(r.crank_arm_width_m * 0.95, 0.011), r.crank_arm_width_m * 0.75, r.crank_u_m)


_DRIVE_BUILDERS = {
    "direct_socket_drive": _drive_coupling_direct_socket_drive_build,
    "single_reduction": _drive_coupling_single_reduction_build,
    "two_speed_reduction": _drive_coupling_two_speed_reduction_build,
    "removable_spindle_socket": _drive_coupling_removable_spindle_socket_build,
}


def _build_crank(model: ArticulatedObject, r: ResolvedConfig, frame, drum):
    """Crank authored in the drive frame: local +X is the drive axis, local +Y is r1
    and local +Z is r2, so the arm reaches "up" out of the radial plane."""

    crank = model.part(
        "crank",
        meta={
            "role": "hand_crank",
            "drive_coupling": r.drive_coupling,
            "handle_head": r.handle_head,
        },
    )
    body = _DRIVE_BUILDERS[r.drive_coupling](r)

    reach = r.crank_reach_m
    taper = r.lever_taper_ratio if r.handle_head == "ratcheting_lever_head" else 0.72
    half = r.crank_arm_width_m / 2.0
    arm = (
        cq.Workplane("YZ")
        .polyline(
            [
                (-half, 0.0),
                (-half * taper, reach),
                (half * taper, reach),
                (half, 0.0),
            ]
        )
        .close()
        .extrude(r.crank_arm_width_m * 0.62)
        .translate((r.crank_u_m - r.crank_arm_width_m * 0.31, 0.0, 0.0))
    )
    body = body.union(arm).union(_crank_head_shape(r))
    eye_r = max(r.grip_pin_radius_m * 2.1, half * 0.8)
    if r.handle_head != "folding_double_grip":
        body = body.union(
            _cyl_x(eye_r, r.crank_arm_width_m * 0.70, r.crank_u_m).translate((0.0, 0.0, reach))
        )

    if r.handle_head == "folding_double_grip":
        second = r.second_arm_ratio * reach
        body = body.union(
            cq.Workplane("YZ")
            .polyline(
                [
                    (-half, 0.0),
                    (-half * 0.72, -second),
                    (half * 0.72, -second),
                    (half, 0.0),
                ]
            )
            .close()
            .extrude(r.crank_arm_width_m * 0.62)
            .translate((r.crank_u_m - r.crank_arm_width_m * 0.31, 0.0, 0.0))
        )
        # Fixed second handhold on the mirrored eye, carried as crank visuals.
        body = body.union(
            _cyl_x(
                r.grip_pin_radius_m,
                r.grip_length_m * 0.9,
                r.crank_u_m + r.grip_length_m * 0.45,
            ).translate((0.0, 0.0, -second))
        )
        body = body.union(
            _tube_x(
                r.grip_radius_m,
                r.grip_pin_radius_m * 0.5,
                r.grip_length_m * 0.8,
                r.crank_u_m + r.grip_length_m * 0.45,
            ).translate((0.0, 0.0, -second))
        )
        # Fold pin on the in-plane axis perpendicular to the arm (local -Y). The
        # knuckle sits BESIDE the arm tip, not around it, so the two parts share no
        # material at any fold angle.
        pin_lo = -(r.fold_knuckle_offset_m + r.fold_knuckle_len_m / 2.0 + 0.0012)
        pin_hi = half * taper + 0.0012
        body = body.union(
            _cyl_x(r.grip_pin_radius_m, pin_hi - pin_lo, (pin_hi + pin_lo) / 2.0)
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 90.0)
            .translate((r.crank_u_m, 0.0, reach))
        )
    else:
        body = body.union(
            _cyl_x(
                r.grip_pin_radius_m,
                r.grip_length_m + 0.012,
                r.crank_u_m + (r.grip_length_m + 0.012) / 2.0,
            ).translate((0.0, 0.0, reach))
        )
        body = body.union(
            _cyl_x(
                r.grip_radius_m * r.retainer_radius_ratio,
                0.0022,
                r.crank_u_m + r.grip_length_m + 0.0109,
            ).translate((0.0, 0.0, reach))
        )

    # Everything above is authored on the shared axial ruler; shift it into the
    # crank's own local frame, whose origin is `crank_origin_u_m`.
    body = body.translate((-r.crank_origin_u_m, 0.0, 0.0))
    crank.visual(
        _mesh(body, f"drive_coupling__{r.drive_coupling}__crank", tolerance=0.00055),
        material="frame",
        name=f"drive_coupling__{r.drive_coupling}__crank", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"galvanized_blue", "matte_black_steel", "gold_zinc", "green_zinc", "red_black"} else "metal.stainless_matte"),
    )
    crank.visual(
        Box((r.crank_arm_width_m * 0.10, r.crank_arm_width_m * 0.5, reach * 0.62)),
        origin=Origin(
            xyz=(
                r.crank_u_m - r.crank_origin_u_m + r.crank_arm_width_m * 0.33,
                0.0,
                reach * 0.5,
            )
        ),
        material="accent",
        name=f"drive_coupling__{r.drive_coupling}__color_strip", material_class_id="metal.paint_coated",
    )

    if r.removable:
        joint = model.articulation(
            "drum_to_crank",
            ArticulationType.PRISMATIC,
            parent=drum,
            child=crank,
            origin=Origin(xyz=(r.crank_origin_u_m, 0.0, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                lower=0.0, upper=r.withdraw_travel_m, effort=80.0, velocity=0.2
            ),
            meta={"role": "removable crank withdrawal"},
        )
        return crank, joint

    if r.reduction:
        axis_point = _world(r, r.crank_origin_u_m, r.crank_axis_v_m, r.crank_axis_w_m)
        radius = r.pinion_shaft_r_m
    else:
        axis_point = _world(r, r.crank_origin_u_m, 0.0, 0.0)
        radius = r.spindle_radius_m + r.bore_clearance_m
    mate = mate_axes(
        AxisInterface(
            name="frame.crank_axis",
            point=axis_point,
            axis=_axis_dir(r),
            radial=_r1(r),
            radius=radius,
        ),
        AxisInterface(
            name="crank.drive_axis",
            point=(0.0, 0.0, 0.0),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 1.0, 0.0),
            radius=radius,
        ),
    )
    joint = model.articulation(
        "frame_to_crank",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=crank,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=80.0, velocity=4.0),
        meta={"role": "hand crank rotation"},
    )
    register_interface_mate(model, joint.name, mate)
    return crank, joint


def _handle_head_spinning_sleeve_grip_build(r: ResolvedConfig):
    """Open-ended tube sleeve with an end cap, free-spinning on the crank-tip pin
    (source 003 `_build_grip_shape` L166-L180)."""

    bore = r.grip_pin_radius_m + r.bore_clearance_m
    body = _tube_x(r.grip_radius_m, bore, r.grip_length_m, 0.0)
    body = body.union(
        _tube_x(r.grip_radius_m, bore, 0.0032, r.grip_length_m / 2.0 + 0.0016)
    )
    return (
        body,
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (
            r.crank_u_m - r.crank_origin_u_m + r.grip_length_m / 2.0 + 0.006,
            0.0,
            r.crank_reach_m,
        ),
        MotionLimits(effort=4.0, velocity=12.0),
        ArticulationType.CONTINUOUS,
    )


def _handle_head_ratcheting_lever_head_build(r: ResolvedConfig):
    """The lever head changes the crank profile, not the grip, so the grip itself is
    the same free-spinning sleeve pushed outboard of the thicker eye (ratcheting fork
    L390-L400)."""

    return _handle_head_spinning_sleeve_grip_build(r)


def _handle_head_folding_double_grip_build(r: ResolvedConfig):
    """Knuckle on the fold axis beside the arm tip plus a sleeve reaching outboard,
    on a bounded revolute instead of a spin (folding fork L400-L441, L480-L498)."""

    bore = r.grip_pin_radius_m + r.bore_clearance_m
    knuckle_r = max(r.grip_radius_m * 0.80, bore + 0.0025)
    knuckle = _tube_x(knuckle_r, bore, r.fold_knuckle_len_m, 0.0)
    sleeve = _cyl_x(
        r.grip_radius_m, r.grip_length_m, knuckle_r * 0.55 + r.grip_length_m / 2.0
    ).rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 90.0)
    return (
        knuckle.union(sleeve),
        (0.0, -1.0, 0.0),
        (1.0, 0.0, 0.0),
        (
            r.crank_u_m - r.crank_origin_u_m,
            -r.fold_knuckle_offset_m,
            r.crank_reach_m,
        ),
        MotionLimits(lower=0.0, upper=r.fold_upper_rad, effort=9.0, velocity=3.0),
        ArticulationType.REVOLUTE,
    )


_HANDLE_BUILDERS = {
    "spinning_sleeve_grip": _handle_head_spinning_sleeve_grip_build,
    "folding_double_grip": _handle_head_folding_double_grip_build,
    "ratcheting_lever_head": _handle_head_ratcheting_lever_head_build,
}


def _build_grip(model: ArticulatedObject, r: ResolvedConfig, crank):
    """The grip mate is solved in CRANK-local coordinates, because the joint origin a
    mate returns is the child frame expressed in its parent's frame."""

    grip = model.part("grip", meta={"role": "crank_grip", "handle_head": r.handle_head})
    body, provider_axis, provider_radial, point, limits, joint_type = _HANDLE_BUILDERS[
        r.handle_head
    ](r)
    grip.visual(
        _mesh(body, f"handle_head__{r.handle_head}__sleeve", tolerance=0.0005),
        material="grip",
        name=f"handle_head__{r.handle_head}__sleeve", material_class_id="rubber.smooth_plain",
    )
    mate = mate_axes(
        AxisInterface(
            name="crank.grip_pin",
            point=point,
            axis=provider_axis,
            radial=provider_radial,
            radius=r.grip_pin_radius_m + r.bore_clearance_m,
        ),
        AxisInterface(
            name="grip.bore",
            point=(0.0, 0.0, 0.0),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 1.0, 0.0),
            radius=r.grip_pin_radius_m,
        ),
    )
    joint = model.articulation(
        "crank_to_grip",
        joint_type,
        parent=crank,
        child=grip,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        meta={"role": "hand grip"},
    )
    register_interface_mate(model, joint.name, mate)
    return grip, joint


# --------------------------------------------------------------------------- #
# line_takeup -- captured spool
# --------------------------------------------------------------------------- #
def _build_spool(model: ArticulatedObject, r: ResolvedConfig, frame, drum_joint):
    spool = model.part("line_spool", meta={"role": "line_spool"})
    core = _tube_x(
        (r.spool_bore_r_m + r.spool_outer_r_m) / 2.0,
        r.spool_bore_r_m,
        r.spool_width_m,
        0.0,
    )
    wound = _tube_x(
        r.spool_outer_r_m,
        (r.spool_bore_r_m + r.spool_outer_r_m) / 2.0,
        r.spool_width_m * 0.92,
        0.0,
    )
    spool.visual(
        _mesh(core, "line_takeup__coaxial_strap_spool__core", tolerance=0.0005),
        material="drum",
        name="line_takeup__coaxial_strap_spool__core", material_class_id=("metal.stainless_matte" if r.palette_style in {"galvanized_blue", "matte_black_steel", "green_zinc", "red_black", "bright_marine"} else "metal.brass_polished"),
    )
    spool.visual(
        _mesh(wound, "line_takeup__coaxial_strap_spool__wound_layer", tolerance=0.0006),
        material="accent",
        name="line_takeup__coaxial_strap_spool__wound_layer", material_class_id="fabric.webbing",
    )
    mate = mate_axes(
        AxisInterface(
            name="frame.spool_axis",
            point=_world(r, 0.0, 0.0, 0.0),
            axis=_axis_dir(r),
            radial=_r1(r),
            radius=r.spool_bore_r_m,
        ),
        AxisInterface(
            name="line_spool.bore",
            point=(0.0, 0.0, 0.0),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 1.0, 0.0),
            radius=r.spool_hub_r_m,
        ),
    )
    joint = model.articulation(
        "frame_to_line_spool",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=spool,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            lower=-2.0 * math.pi, upper=2.0 * math.pi, effort=180.0, velocity=2.2
        ),
        mimic=Mimic(joint=drum_joint.name, multiplier=1.0, offset=0.0),
        meta={"role": "captured strap spool"},
    )
    register_interface_mate(model, joint.name, mate)
    return spool, joint


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_sailboat_winch_with_pawl_and_handle(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "sailboat_winch_with_pawl_and_handle",
            "slot_choices": tuple(slot_choices_for_config(r).items()),
            "pawl_count": r.pawl_count,
            "source_pool_reviewed": "16 workbench records / rev_000001",
        },
    )
    for key, rgba in r.palette.items():
        model.material(key, rgba=rgba)

    frame = _build_frame(model, r)

    drum = model.part(
        "drum", meta={"role": "line_drum", "line_takeup": r.line_takeup}
    )
    drum.visual(
        _mesh(_drum_shape(r), f"line_takeup__{r.line_takeup}__drum", tolerance=0.0006),
        material="drum",
        name=f"line_takeup__{r.line_takeup}__drum", material_class_id=("metal.stainless_matte" if r.palette_style in {"galvanized_blue", "matte_black_steel", "green_zinc", "red_black", "bright_marine"} else "metal.brass_polished"),
    )

    drum_mate = mate_axes(
        AxisInterface(
            name="frame.drum_bearing_axis",
            point=_world(r, 0.0, 0.0, 0.0),
            axis=_axis_dir(r),
            radial=_r1(r),
            radius=r.spindle_radius_m + r.bore_clearance_m,
        ),
        AxisInterface(
            name="drum.spindle",
            point=(0.0, 0.0, 0.0),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 1.0, 0.0),
            radius=r.spindle_radius_m,
        ),
    )
    drum_joint = model.articulation(
        "frame_to_drum",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=drum,
        origin=drum_mate.origin,
        axis=drum_mate.axis,
        motion_limits=MotionLimits(effort=140.0, velocity=3.0),
        meta={"role": "line drum rotation"},
    )
    register_interface_mate(model, drum_joint.name, drum_mate)

    if r.line_takeup == "coaxial_strap_spool":
        _build_spool(model, r, frame, drum_joint)

    crank, _ = _build_crank(model, r, frame, drum)
    _build_grip(model, r, crank)
    _build_pawls(model, r, frame)
    return model


def build_seeded_sailboat_winch_with_pawl_and_handle(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_sailboat_winch_with_pawl_and_handle(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Authored tests
# --------------------------------------------------------------------------- #
def _joint_world_axis(joint) -> tuple[float, float, float]:
    """World direction of a joint's rotation axis.

    ``mate_axes`` returns the axis in the CHILD frame, which is always local +X for
    every rotating member here, so the family's real orientation lives in the joint
    origin's rpy."""

    roll, pitch, yaw = joint.origin.rpy
    return (
        math.cos(yaw) * math.cos(pitch),
        math.sin(yaw) * math.cos(pitch),
        -math.sin(pitch),
    )


def _aabb_center(aabb):
    if aabb is None:
        return None
    low, high = aabb
    return tuple((low[i] + high[i]) / 2.0 for i in range(3))


def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def _meshes_materialized(model: ArticulatedObject) -> bool:
    for part in model.parts:
        for visual in getattr(part, "visuals", []):
            filename = getattr(getattr(visual, "geometry", None), "filename", None)
            if filename and "__preflight_probe__" in str(filename):
                return False
    return True


def run_sailboat_winch_with_pawl_and_handle_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    joints = {joint.name: joint for joint in model.articulations}
    exact = _meshes_materialized(model)

    frames = _parts_by_role(model, "winch_frame")
    drums = _parts_by_role(model, "line_drum")
    cranks = _parts_by_role(model, "hand_crank")
    grips = _parts_by_role(model, "crank_grip")
    pawls = _parts_by_role(model, "ratchet_pawl")
    spools = _parts_by_role(model, "line_spool")

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_interface_mate_mismatch()
    if exact:
        ctx.fail_if_part_contains_disconnected_geometry_islands()
        ctx.fail_if_parts_overlap_in_current_pose()
        ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    # --- category anchors ----------------------------------------------------
    ctx.check(
        "manual winch core part set",
        len(frames) == 1
        and len(drums) == 1
        and len(cranks) == 1
        and len(grips) == 1
        and len(pawls) == r.pawl_count
        and len(spools) == (1 if r.line_takeup == "coaxial_strap_spool" else 0),
        details=(
            f"frame={len(frames)} drum={len(drums)} crank={len(cranks)} grip={len(grips)} "
            f"pawls={len(pawls)}/{r.pawl_count} spool={len(spools)}"
        ),
    )
    drum_joint = joints.get("frame_to_drum")
    expected_axis = _axis_dir(r)
    drum_world_axis = None if drum_joint is None else _joint_world_axis(drum_joint)
    ctx.check(
        "drum turns about its bearing axis",
        drum_joint is not None
        and drum_joint.articulation_type == ArticulationType.CONTINUOUS
        and tuple(drum_joint.axis) == (1.0, 0.0, 0.0)
        and all(abs(drum_world_axis[i] - expected_axis[i]) < 1e-6 for i in range(3))
        and "interface_mate" in (drum_joint.meta or {}),
        details=f"child_axis={None if drum_joint is None else tuple(drum_joint.axis)} world={drum_world_axis} expected={expected_axis}",
    )

    engaged = True
    for index in range(r.pawl_count):
        joint = joints.get(f"frame_to_pawl_{index}")
        engaged &= joint is not None and joint.articulation_type == ArticulationType.REVOLUTE
        if joint is not None:
            world = _joint_world_axis(joint)
            engaged &= tuple(joint.axis) == (1.0, 0.0, 0.0)
            engaged &= all(abs(world[i] - expected_axis[i]) < 1e-6 for i in range(3))
        if exact and index < len(pawls):
            engaged &= ctx.expect_contact(
                pawls[index],
                drums[0],
                contact_tol=0.0012,
                name=f"pawl_{index} seats on the ratchet ring",
            )
    ctx.check(
        "every pawl engages the ratchet ring",
        engaged,
        details=(
            f"n={r.pawl_count} ring_r={r.pawl_ring_r_m:.4f} tip_r={r.ratchet_tip_r_m:.4f} "
            f"seat_r={r.pawl_seat_r_m:.4f} pitch={r.pawl_pitch_rad:.4f}"
        ),
    )

    # The derivation this rebuild exists for: nothing that turns can reach the
    # mounting structure.
    if r.vertical:
        clearance_ok = (
            r.drum_origin_z_m + r.drum_u_min_m - (r.base_plate_h_m + r.pedestal_h_m)
            >= r.base_clearance_m - 1e-9
        )
        detail = (
            f"lowest_rotating_z={r.drum_origin_z_m + r.drum_u_min_m:.4f} "
            f"pedestal_top={r.base_plate_h_m + r.pedestal_h_m:.4f}"
        )
    else:
        clearance_ok = (
            r.axis_lift_m - r.rotating_reach_m - r.base_plate_h_m >= r.base_clearance_m - 1e-9
        )
        detail = (
            f"axis_lift={r.axis_lift_m:.4f} rotating_reach={r.rotating_reach_m:.4f} "
            f"base_h={r.base_plate_h_m:.4f} clearance={r.base_clearance_m:.4f}"
        )
    ctx.check("no rotating member reaches the mounting structure", clearance_ok, details=detail)

    crank_joint = joints.get("frame_to_crank") or joints.get("drum_to_crank")
    if r.removable:
        outboard_ok = crank_joint is not None and crank_joint.parent == "drum"
    else:
        frame_end = (
            r.plate_u_near_m + r.plate_thickness_m / 2.0
            if r.vertical
            else r.plate_u_far_m + r.plate_thickness_m / 2.0
        )
        reference = r.drum_u_max_m if r.vertical else frame_end
        outboard_ok = r.crank_u_m - r.crank_arm_width_m * 0.31 > reference + 1e-9
    ctx.check(
        "crank is carried outboard of the frame",
        outboard_ok,
        details=f"crank_u={r.crank_u_m:.4f} plate_far={r.plate_u_far_m:.4f}",
    )

    if r.removable:
        withdraw = joints.get("drum_to_crank")
        socket_ok = withdraw is not None and r.retained_engagement_m >= 0.007 - 1e-9
        if exact and withdraw is not None:
            with ctx.pose({withdraw: r.withdraw_travel_m}):
                socket_ok &= ctx.expect_overlap(
                    cranks[0],
                    drums[0],
                    axes="x" if not r.vertical else "z",
                    min_overlap=0.006,
                    name="withdrawn crank keeps guided socket engagement",
                )
    else:
        socket_ok = True
    ctx.check(
        "removable crank keeps guided socket engagement",
        socket_ok,
        details=f"retained={r.retained_engagement_m:.4f} travel={r.withdraw_travel_m:.4f}",
    )

    if r.line_takeup == "coaxial_strap_spool":
        spool_joint = joints.get("frame_to_line_spool")
        spool_ok = (
            spool_joint is not None
            and spool_joint.mimic is not None
            and spool_joint.mimic.joint == "frame_to_drum"
            and abs(spool_joint.mimic.multiplier - 1.0) < 1e-9
        )
    else:
        spool_ok = "frame_to_line_spool" not in joints
    ctx.check(
        "captured spool follows the drum one to one",
        spool_ok,
        details=f"line_takeup={r.line_takeup}",
    )

    band_lo = r.ratchet_u_m - r.pawl_width_m / 2.0
    band_hi = r.ratchet_u_m + r.pawl_width_m / 2.0
    frame_inner = (
        r.drum_u_max_m + 0.020
        if r.vertical
        else r.plate_u_far_m - r.plate_thickness_m / 2.0
    )
    stack_below = r.ratchet_u_m - r.ratchet_thickness_m / 2.0 - r.pre_ratchet_gap_m
    # The nose swings clear of the tooth tips because the pivot lies OUTSIDE the tip
    # circle, so the nose radius grows monotonically with |phi|; adjacent bodies keep
    # their spacing because pawl_travel_rad is derived from the pivot pitch.
    nose_lift = (
        math.sqrt(
            r.pawl_ring_r_m**2
            + r.pawl_ring_gap_m**2
            - 2.0 * r.pawl_ring_r_m * r.pawl_ring_gap_m * math.cos(r.pawl_travel_rad)
        )
        - r.ratchet_tip_r_m
    )
    neighbour_room = (
        (r.pawl_ring_r_m + r.pawl_outer_reach_m) * r.pawl_pitch_rad
        - 2.0 * r.pawl_outer_reach_m * math.sin(r.pawl_travel_rad)
        - 2.0 * r.pawl_body_half_w_m
        if r.pawl_count > 1
        else 1.0
    )
    slot_ok = (
        band_hi + 0.0006 <= frame_inner + 1e-9
        and band_lo >= stack_below - 1e-9
        and r.pawl_travel_rad >= 0.05
        and nose_lift > 0.0
        and neighbour_room > -1e-9
    )
    for index in range(r.pawl_count):
        joint = joints.get(f"frame_to_pawl_{index}")
        if joint is None or index >= len(pawls):
            slot_ok = False
            continue
        if not exact:
            continue
        with ctx.pose({joint: r.pawl_travel_rad}):
            slot_ok &= ctx.part_world_aabb(pawls[index]) is not None
    ctx.check(
        "pawl swing stays inside its frame slot",
        slot_ok,
        details=(
            f"band=[{band_lo:.4f},{band_hi:.4f}] frame_inner={frame_inner:.4f} "
            f"stack_below={stack_below:.4f} travel=+/-{r.pawl_travel_rad:.3f} rad "
            f"nose_lift={nose_lift:.5f} room={neighbour_room:.5f}"
        ),
    )

    # --- derivation invariants ----------------------------------------------
    ctx.check(
        "bearing plates stay outboard of every drum disc",
        r.plate_u_near_m + r.plate_thickness_m / 2.0 <= r.drum_u_min_m - r.running_clearance_m
        and (
            r.vertical
            or r.plate_u_far_m - r.plate_thickness_m / 2.0
            >= r.drum_u_max_m + r.running_clearance_m
        ),
        details=(
            f"near={r.plate_u_near_m:.4f} far={r.plate_u_far_m:.4f} "
            f"drum=[{r.drum_u_min_m:.4f},{r.drum_u_max_m:.4f}]"
        ),
    )
    if r.reduction:
        mesh_gap = (
            r.gear_center_distance_m - r.drum_gear_tip_r_m - r.pinion_tip_r_m
        )
        ctx.check(
            "reduction gears are closely meshed without overlap",
            0.0 < mesh_gap <= 0.0018,
            details=f"tip_gap={mesh_gap:.5f} centre={r.gear_center_distance_m:.4f}",
        )
        if exact and cranks and drums:
            ctx.expect_contact(
                drums[0],
                cranks[0],
                contact_tol=max(0.0012, r.gear_backlash_m + 0.0006),
                name="reduction pinion stays meshed with the drum gear",
            )
    else:
        ctx.check(
            "reduction gears are closely meshed without overlap",
            not r.gear_u_m,
            details=f"drive_coupling={r.drive_coupling}",
        )
    ctx.check(
        "pawl pivots are spaced by whole ratchet teeth",
        r.pawl_count == 1
        or abs(
            r.pawl_pitch_rad / (2.0 * math.pi / r.ratchet_teeth)
            - round(r.pawl_pitch_rad / (2.0 * math.pi / r.ratchet_teeth))
        )
        < 1e-6,
        details=f"pitch={r.pawl_pitch_rad:.5f} tooth={2.0 * math.pi / r.ratchet_teeth:.5f}",
    )
    ctx.check(
        "the pawl seat rides the ratchet tip circle",
        0.0 < r.pawl_seat_r_m - r.ratchet_tip_r_m <= 0.0010
        and r.pawl_nose_half_w_m ** 2 / (2.0 * r.pawl_ring_gap_m) <= 0.0016,
        details=(
            f"seat={r.pawl_seat_r_m:.5f} tip={r.ratchet_tip_r_m:.5f} "
            f"nose_half_w={r.pawl_nose_half_w_m:.5f} gap={r.pawl_ring_gap_m:.5f}"
        ),
    )

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)
    return ctx.report()


# --------------------------------------------------------------------------- #
# High-risk cross-slot corners
# --------------------------------------------------------------------------- #
TEMPLATE_CORNERS = (
    corner_case(
        "capstan_two_speed_triple_lever",
        {
            "frame_family": "vertical_capstan_deck",
            "web_relief": "enclosed_guard_shell",
            "drive_coupling": "two_speed_reduction",
            "handle_head": "folding_double_grip",
            "line_takeup": "self_tailing_crown",
            "ratchet_pawl": "long_release_lever_pawl",
            "pawl_count": 3,
            "drum_radius_m": 0.046,
            "flange_radius_ratio": 1.78,
            "ratchet_tip_ratio": 1.16,
            "pawl_ring_gap_m": 0.007,
            "base_clearance_m": 0.006,
            "base_plate_h_m": 0.004,
            "crank_reach_m": 0.125,
        },
        reason=(
            "largest drum on the vertical deck with two gear planes, a shroud, the crown, "
            "the longest crank and three long release levers on the tightest pivot ring"
        ),
    ),
    corner_case(
        "smallest_cantilever_removable_spool",
        {
            "frame_family": "cantilever_front_cheek",
            "web_relief": "windowed_web",
            "drive_coupling": "removable_spindle_socket",
            "handle_head": "ratcheting_lever_head",
            "line_takeup": "coaxial_strap_spool",
            "ratchet_pawl": "hooked_lobe_pawl",
            "pawl_count": 1,
            "drum_radius_m": 0.026,
            "drum_width_m": 0.052,
            "flange_radius_ratio": 1.24,
            "plate_thickness_m": 0.004,
            "plate_reach_ratio": 1.02,
            "socket_depth_m": 0.020,
            "withdraw_travel_m": 0.018,
            "spool_outer_ratio": 0.94,
            "crank_reach_m": 0.055,
        },
        reason=(
            "smallest drum cantilevered on one plate, windows cut in the thinnest web, the "
            "shallowest socket at the longest withdrawal, and the widest spool inside the "
            "smallest flange"
        ),
    ),
    corner_case(
        "bridged_single_reduction_deep_pinion",
        {
            "frame_family": "bridged_side_plates",
            "web_relief": "enclosed_guard_shell",
            "drive_coupling": "single_reduction",
            "handle_head": "spinning_sleeve_grip",
            "line_takeup": "grooved_barrel",
            "ratchet_pawl": "long_release_lever_pawl",
            "pawl_count": 2,
            "pinion_angle_rad": -1.05,
            "drum_gear_teeth": 36,
            "pinion_teeth": 14,
            "base_clearance_m": 0.030,
            "bridge_span_ratio": 0.95,
            "drum_radius_m": 0.046,
            "flange_radius_ratio": 1.78,
        },
        reason=(
            "the pinion hangs at its steepest angle under the largest gear pair, which is "
            "exactly the combination the legacy template pushed through the base plate"
        ),
    ),
    corner_case(
        "folded_direct_drive_widest_guard",
        {
            "frame_family": "folded_twin_cheek",
            "web_relief": "enclosed_guard_shell",
            "drive_coupling": "direct_socket_drive",
            "handle_head": "folding_double_grip",
            "line_takeup": "self_tailing_crown",
            "ratchet_pawl": "hooked_lobe_pawl",
            "pawl_count": 3,
            "guard_thickness_m": 0.0105,
            "guard_window_span_rad": 1.75,
            "crown_tip_ratio": 1.02,
            "drum_width_m": 0.100,
            "second_arm_ratio": 1.00,
            "fold_upper_rad": 1.62,
        },
        reason=(
            "the thickest shroud with the widest fairlead around the widest drum, a crown at "
            "the flange radius, and a fully mirrored folding crank at maximum fold"
        ),
    ),
)


__all__ = [
    "Config",
    "PALETTES",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_sailboat_winch_with_pawl_and_handle",
    "build_seeded_sailboat_winch_with_pawl_and_handle",
    "config_from_seed",
    "resolve_config",
    "run_sailboat_winch_with_pawl_and_handle_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
