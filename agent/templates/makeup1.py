# SPDX-License-Identifier: Apache-2.0

"""Source-backed articulated cosmetic compacts / pressed-powder palettes.

Rebuilt from the ``pictureX/0611/Makeup1`` pool: three origin records (nine-pan
compact, ten-well complexion palette, two-way cake compact with a front push
latch) plus nine directed forks. Four component slots -- ``case_form``,
``well_pattern``, ``closure`` and ``opening`` -- combine freely; the well field,
rim seat, hinge line, latch pocket and auxiliary mounts are all derived from the
selected case form, so there are no compatibility gates.
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
    MotionLimits,
    Origin,
    PlaneInterface,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mate_planes,
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

CaseForm = Literal["rounded_rectangle", "elongated_rectangle", "round_puck"]
WellPattern = Literal["orthogonal_grid", "radial_ring", "fan_sector"]
Closure = Literal["rear_hinge", "push_latch", "sliding_latch"]
Opening = Literal["single_lid", "second_hinged_tray", "fan_out_tray"]
Palette = Literal[
    "pearl_white",
    "satin_black",
    "blush_rose",
    "warm_taupe",
    "deep_plum",
    "mint_ivory",
]

CASE_FORMS: tuple[CaseForm, ...] = (
    "rounded_rectangle",
    "elongated_rectangle",
    "round_puck",
)
WELL_PATTERNS: tuple[WellPattern, ...] = (
    "orthogonal_grid",
    "radial_ring",
    "fan_sector",
)
CLOSURES: tuple[Closure, ...] = ("rear_hinge", "push_latch", "sliding_latch")
OPENINGS: tuple[Opening, ...] = ("single_lid", "second_hinged_tray", "fan_out_tray")
WELL_COUNTS: tuple[int, ...] = (4, 6, 9, 10, 12)
PALETTES: tuple[Palette, ...] = (
    "pearl_white",
    "satin_black",
    "blush_rose",
    "warm_taupe",
    "deep_plum",
    "mint_ivory",
)


TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("case_form", CASE_FORMS),
        component_slot("well_pattern", WELL_PATTERNS),
        component_slot("closure", CLOSURES),
        component_slot("opening", OPENINGS),
        multiplicity_slot("well_count", WELL_COUNTS, item_slot="well_pattern"),
    )
)


@dataclass(frozen=True)
class Config:
    case_form: CaseForm = "rounded_rectangle"
    well_pattern: WellPattern = "orthogonal_grid"
    closure: Closure = "rear_hinge"
    opening: Opening = "single_lid"
    well_count: int = 9
    palette: Palette = "pearl_white"
    case_width_m: float | None = None
    case_depth_m: float | None = None
    case_height_m: float | None = None
    puck_flat_ratio: float | None = None
    lid_open_rad: float | None = None
    thumb_catch_width_m: float | None = None
    latch_press_rad: float | None = None
    latch_travel_m: float | None = None
    pan_fill_ratio: float | None = None
    pan_depth_m: float | None = None
    aux_tray_depth_m: float | None = None
    aux_open_rad: float | None = None
    fan_sweep_rad: float | None = None
    fan_radius_ratio: float | None = None
    name: str = "makeup1"


@dataclass(frozen=True)
class ResolvedConfig:
    case_form: CaseForm
    well_pattern: WellPattern
    closure: Closure
    opening: Opening
    well_count: int
    palette: Palette
    case_width_m: float
    case_depth_m: float
    case_height_m: float
    puck_flat_ratio: float
    lid_open_rad: float
    thumb_catch_width_m: float
    latch_press_rad: float
    latch_travel_m: float
    pan_fill_ratio: float
    pan_depth_m: float
    aux_tray_depth_m: float
    aux_open_rad: float
    fan_sweep_rad: float
    fan_radius_ratio: float
    plan_kind: str
    case_plan_w_m: float
    case_plan_d_m: float
    puck_radius_m: float
    corner_r_m: float
    rear_flat_y_m: float
    front_flat_y_m: float
    wall_t_m: float
    field_margin_m: float
    floor_t_m: float
    deck_relief_m: float
    rim_top_z_m: float
    rim_w_m: float
    well_field_w_m: float
    well_field_d_m: float
    cavity_depth_m: float
    cavity_clearance_m: float
    cup_floor_t_m: float
    cup_wall_t_m: float
    seat_gap_m: float
    well_floor_z_m: float
    cake_top_z_m: float
    pan_across_m: float
    grid_cols: int
    grid_rows: int
    pan_pitch_x_m: float
    pan_pitch_y_m: float
    ring_rx_m: float
    ring_ry_m: float
    fan_span_rad: float
    fan_apex_y_m: float
    fan_inner_r_m: float
    fan_outer_r_m: float
    fan_wedge_rad: float
    knuckle_r_m: float
    knuckle_gap_m: float
    knuckle_len_m: float
    knuckle_x_m: float
    knuckle_axial_fit_m: float
    knuckle_axial_clearance_m: float
    collar_len_m: float
    rear_span_m: float
    aux_span_m: float
    aux_barrel_len_m: float
    hinge_pin_r_m: float
    pin_clearance_m: float
    pin_len_m: float
    barrel_len_m: float
    barrel_outer_r_m: float
    barrel_bore_r_m: float
    hinge_y_m: float
    hinge_z_m: float
    seat_interference_m: float
    lid_t_m: float
    lid_plan_w_m: float
    lid_plan_d_m: float
    lid_rear_local_y_m: float
    lid_front_local_y_m: float
    lid_recess_d_m: float
    lid_recess_inset_m: float
    mirror_t_m: float
    skirt_t_m: float
    skirt_clearance_m: float
    skirt_depth_m: float
    skirt_bottom_z_m: float
    cake_top_clearance_m: float
    pocket_w_m: float
    pocket_h_m: float
    pocket_center_x_m: float
    pocket_depth_m: float
    pocket_top_z_m: float
    pocket_bot_z_m: float
    pocket_margin_m: float
    pocket_relief_m: float
    catch_lip_h_m: float
    lid_lip_w_m: float
    lid_lip_out_m: float
    pivot_stub_r_m: float
    pivot_clearance_m: float
    rocker_bore_r_m: float
    rocker_w_m: float
    pivot_y_m: float
    pivot_z_m: float
    hook_top_z_m: float
    hook_arm_m: float
    hook_swing_m: float
    rail_len_m: float
    guide_clearance_m: float
    guide_slot_len_m: float
    aux_hinge_offset_m: float
    aux_hinge_floor_m: float
    aux_hinge_y_m: float
    aux_hinge_z_m: float
    aux_knuckle_r_m: float
    aux_knuckle_x_m: float
    aux_knuckle_len_m: float
    aux_pin_r_m: float
    aux_bore_r_m: float
    aux_tray_t_m: float
    aux_well_count: int
    aux_pan_across_m: float
    aux_cavity_depth_m: float
    aux_tray_pitch_m: float
    fan_pivot_inset_m: float
    fan_pivot_y_m: float
    fan_tray_outer_r_m: float
    fan_tray_inner_r_m: float
    fan_tray_t_m: float
    fan_half_rad: float
    pivot_post_r_m: float
    post_h_m: float
    name: str


_RANGES: dict[str, tuple[float, float]] = {
    "case_width_m": (0.085, 0.150),
    "case_depth_m": (0.060, 0.115),
    "case_height_m": (0.013, 0.024),
    "puck_flat_ratio": (0.04, 0.12),
    "lid_open_rad": (1.75, 2.15),
    "thumb_catch_width_m": (0.016, 0.036),
    "latch_press_rad": (0.14, 0.35),
    "latch_travel_m": (0.0030, 0.0065),
    "pan_fill_ratio": (0.60, 0.90),
    "pan_depth_m": (0.0035, 0.0070),
    "aux_tray_depth_m": (0.028, 0.052),
    "aux_open_rad": (1.35, 1.60),
    "fan_sweep_rad": (1.30, 2.05),
    "fan_radius_ratio": (0.90, 1.20),
}
_DEFAULTS: dict[str, float] = {name: 0.5 * (lo + hi) for name, (lo, hi) in _RANGES.items()}


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x4A17C1)
    return Config(
        case_form=choices["case_form"],
        well_pattern=choices["well_pattern"],
        closure=choices["closure"],
        opening=choices["opening"],
        well_count=choices["well_count"],
        palette=PALETTES[rng.randrange(len(PALETTES))],
        case_width_m=round(rng.uniform(0.085, 0.150), 4),
        case_depth_m=round(rng.uniform(0.060, 0.115), 4),
        case_height_m=round(rng.uniform(0.013, 0.024), 4),
        puck_flat_ratio=round(rng.uniform(0.04, 0.12), 4),
        lid_open_rad=round(rng.uniform(1.75, 2.15), 4),
        thumb_catch_width_m=round(rng.uniform(0.016, 0.036), 4),
        latch_press_rad=round(rng.uniform(0.14, 0.35), 4),
        latch_travel_m=round(rng.uniform(0.0030, 0.0065), 5),
        pan_fill_ratio=round(rng.uniform(0.60, 0.90), 4),
        pan_depth_m=round(rng.uniform(0.0035, 0.0070), 5),
        aux_tray_depth_m=round(rng.uniform(0.028, 0.052), 4),
        aux_open_rad=round(rng.uniform(1.35, 1.60), 4),
        fan_sweep_rad=round(rng.uniform(1.30, 2.05), 4),
        fan_radius_ratio=round(rng.uniform(0.90, 1.20), 4),
    )


def grid_shape(well_count: int) -> tuple[int, int]:
    """Column/row split used by the orthogonal well grid for each declared N."""

    table = {4: (2, 2), 6: (3, 2), 9: (3, 3), 10: (5, 2), 12: (4, 3)}
    if well_count in table:
        return table[well_count]
    cols = max(1, int(math.ceil(math.sqrt(float(well_count)))))
    rows = max(1, int(math.ceil(well_count / cols)))
    return cols, rows


def min_neighbour_gap(well_count: int, ring_rx_m: float, ring_ry_m: float) -> float:
    """Smallest centre-to-centre distance between adjacent pans on the ring."""

    if well_count < 2:
        return 2.0 * max(ring_rx_m, ring_ry_m)
    points = [
        (
            ring_rx_m * math.cos(2.0 * math.pi * index / well_count),
            ring_ry_m * math.sin(2.0 * math.pi * index / well_count),
        )
        for index in range(well_count)
    ]
    best = float("inf")
    for index in range(well_count):
        ax, ay = points[index]
        bx, by = points[(index + 1) % well_count]
        best = min(best, math.hypot(bx - ax, by - ay))
    return best


def _value(config: Config, name: str) -> float:
    raw = getattr(config, name)
    value = _DEFAULTS[name] if raw is None else float(raw)
    lo, hi = _RANGES[name]
    if not lo <= value <= hi:
        raise ValueError(f"{name} must be in [{lo}, {hi}]")
    return value


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "case_form": config.case_form,
            "well_pattern": config.well_pattern,
            "closure": config.closure,
            "opening": config.opening,
            "well_count": config.well_count,
        }
    )
    if config.palette not in PALETTES:
        raise ValueError(f"palette must be one of {PALETTES}")

    case_width = _value(config, "case_width_m")
    case_depth = _value(config, "case_depth_m")
    case_height = _value(config, "case_height_m")
    puck_flat_ratio = _value(config, "puck_flat_ratio")
    lid_open_rad = _value(config, "lid_open_rad")
    thumb_catch_width = _value(config, "thumb_catch_width_m")
    latch_press_rad = _value(config, "latch_press_rad")
    latch_travel = _value(config, "latch_travel_m")
    pan_fill_ratio = _value(config, "pan_fill_ratio")
    pan_depth = _value(config, "pan_depth_m")
    aux_tray_depth = _value(config, "aux_tray_depth_m")
    aux_open_rad = _value(config, "aux_open_rad")
    fan_sweep_rad = _value(config, "fan_sweep_rad")
    fan_radius_ratio = _value(config, "fan_radius_ratio")

    # --- primary plan family -------------------------------------------------
    wall_t = 0.0034
    field_margin = 0.0014
    floor_t = 0.0030
    deck_relief = 0.0009
    puck_radius = case_width / 2.0
    if config.case_form == "round_puck":
        plan_kind = "disc"
        plan_w = 2.0 * puck_radius
        plan_d = 2.0 * puck_radius
        corner_r = 0.0
        rear_flat_y = puck_radius * (1.0 - puck_flat_ratio)
        front_flat_y = -puck_radius * (1.0 - 0.5 * puck_flat_ratio)
        well_field_w = 1.414 * (rear_flat_y - wall_t - field_margin)
        well_field_d = well_field_w
    else:
        plan_kind = "rect"
        if config.case_form == "elongated_rectangle":
            plan_w = min(0.185, case_width * 1.20)
            plan_d = case_depth * 0.60
            corner_r = min(0.0040, 0.10 * min(plan_w, plan_d))
        else:
            plan_w = case_width
            plan_d = case_depth
            corner_r = min(0.0060, 0.16 * min(plan_w, plan_d))
        rear_flat_y = plan_d / 2.0
        front_flat_y = -plan_d / 2.0
        well_field_w = plan_w - 2.0 * wall_t - 2.0 * field_margin
        well_field_d = plan_d - 2.0 * wall_t - 2.0 * field_margin
    if min(well_field_w, well_field_d) < 0.010:
        raise ValueError("derived well field is too small for the pressed pan module")
    rim_top_z = case_height
    rim_w = wall_t

    # --- recessed well field -------------------------------------------------
    cup_floor_t = 0.0010
    cup_wall_t = 0.0007
    seat_gap = 0.0016
    cavity_clearance = 0.0004
    cavity_depth = pan_depth + cup_floor_t + seat_gap
    well_floor_z = case_height - cavity_depth
    if well_floor_z < floor_t:
        raise ValueError("case_height_m is too small for the derived well depth")
    cake_top_z = well_floor_z + cup_floor_t + pan_depth - 0.0004

    grid_cols, grid_rows = grid_shape(config.well_count)
    pan_pitch_x = well_field_w / float(grid_cols)
    pan_pitch_y = well_field_d / float(grid_rows)
    ring_rx = 0.30 * well_field_w
    ring_ry = 0.30 * well_field_d
    fan_span_rad = 2.20
    fan_apex_y = well_field_d / 2.0
    fan_outer_r = min(0.95 * well_field_d, 0.48 * well_field_w)
    fan_inner_r = 0.30 * fan_outer_r
    fan_wedge_rad = pan_fill_ratio * fan_span_rad / float(config.well_count)

    if config.well_pattern == "orthogonal_grid":
        pan_across = pan_fill_ratio * min(pan_pitch_x, pan_pitch_y)
    elif config.well_pattern == "radial_ring":
        pan_across = pan_fill_ratio * min(
            min_neighbour_gap(config.well_count, ring_rx, ring_ry),
            2.0 * (well_field_w / 2.0 - ring_rx),
            2.0 * (well_field_d / 2.0 - ring_ry),
        )
    else:
        pan_across = fan_wedge_rad * 0.5 * (fan_outer_r + fan_inner_r)
    pan_across = max(0.0042, pan_across)

    # --- hinge hardware ------------------------------------------------------
    knuckle_r = 0.0026
    knuckle_gap = 0.0007
    # The puck's rear face is a derived chord flat, so the hinge hardware must
    # stay inside that chord instead of hanging off the tangent circle.
    if plan_kind == "disc":
        rear_span = math.sqrt(max(1e-9, puck_radius**2 - rear_flat_y**2))
    else:
        rear_span = plan_w / 2.0
    knuckle_x = min(0.34 * plan_w, 0.62 * rear_span)
    knuckle_len = min(0.55 * rear_span, max(0.0060, 0.13 * plan_w))
    # Interleaved knuckles locate the cover barrel axially: the barrel exactly
    # fills the gap between them with a 30 um running fit on each end face.
    knuckle_axial_clearance = 0.0008
    knuckle_axial_fit = 1.0e-4
    hinge_pin_r = 0.0009
    pin_clearance = 0.0004
    pin_len = 2.0 * knuckle_x + knuckle_len - 0.0004
    barrel_len = 2.0 * knuckle_x - knuckle_len - 2.0 * knuckle_axial_clearance
    if barrel_len < 0.0035:
        raise ValueError("hinge knuckle layout leaves no room for the cover barrel")
    barrel_outer_r = 0.0024
    barrel_bore_r = hinge_pin_r + pin_clearance
    lid_t = 0.0034
    seat_interference = 4.0e-5
    hinge_y = rear_flat_y + knuckle_r + knuckle_gap
    hinge_z = case_height + lid_t / 2.0 - seat_interference

    # --- cover ---------------------------------------------------------------
    skirt_t = 0.0014
    skirt_clearance = 0.0006
    skirt_depth = min(0.0042, 0.32 * case_height)
    lid_plan_w = plan_w + 2.0 * (skirt_t + skirt_clearance)
    lid_plan_d = plan_d + skirt_t + skirt_clearance
    lid_rear_local_y = -(knuckle_r + knuckle_gap)
    lid_front_local_y = -(hinge_y + plan_d / 2.0 + skirt_t + skirt_clearance)
    lid_recess_d = 0.0012
    lid_recess_inset = skirt_t + skirt_clearance + 0.6 * wall_t
    mirror_t = 0.0006
    skirt_bottom_z = case_height - seat_interference - skirt_depth
    cake_top_clearance = rim_top_z - seat_interference - cake_top_z

    # --- front closure pocket ------------------------------------------------
    pocket_margin = 0.0016
    pocket_relief = 0.0022
    pocket_top_z = skirt_bottom_z - 0.0004
    pocket_depth = wall_t + pocket_relief
    guide_clearance = 0.0005
    rail_len = 0.0090
    guide_slot_len = rail_len + latch_travel + 2.0 * guide_clearance
    rocker_w = 0.0120
    if config.closure == "rear_hinge":
        pocket_w = thumb_catch_width + 2.0 * pocket_margin
        pocket_h = min(0.0060, pocket_top_z - 0.0016)
    elif config.closure == "push_latch":
        pocket_w = rocker_w + 2.0 * pocket_margin
        pocket_h = min(0.0080, pocket_top_z - 0.0014)
    else:
        pocket_w = guide_slot_len + 2.0 * pocket_margin
        pocket_h = min(0.0070, pocket_top_z - 0.0016)
    pocket_h = max(0.0030, pocket_h)
    pocket_center_x = 0.5 * latch_travel if config.closure == "sliding_latch" else 0.0
    pocket_bot_z = pocket_top_z - pocket_h
    catch_lip_h = 0.55 * pocket_h
    lid_lip_w = 0.0100 if config.closure == "push_latch" else 0.0032
    lid_lip_out = 0.0016

    pivot_stub_r = 0.0009
    pivot_clearance = 0.0004
    rocker_bore_r = pivot_stub_r + pivot_clearance
    pivot_y = front_flat_y + pocket_depth - 0.0028
    pivot_z = pocket_bot_z + 0.0030
    hook_top_z = skirt_bottom_z - 0.0007
    hook_arm = max(0.0020, hook_top_z - pivot_z)
    hook_swing = hook_arm * math.sin(latch_press_rad)

    # --- auxiliary opening trays --------------------------------------------
    aux_hinge_offset = 0.0145
    aux_hinge_floor = 0.0008
    aux_knuckle_r = 0.0022
    aux_pin_r = 0.0008
    aux_bore_r = aux_pin_r + pivot_clearance
    aux_hinge_y = front_flat_y - aux_hinge_offset
    aux_hinge_z = aux_knuckle_r + aux_hinge_floor
    if plan_kind == "disc":
        aux_span = math.sqrt(max(1e-9, puck_radius**2 - front_flat_y**2))
    else:
        aux_span = plan_w / 2.0
    aux_knuckle_x = min(0.30 * plan_w, 0.62 * aux_span)
    aux_knuckle_len = min(0.55 * aux_span, max(0.0060, 0.11 * plan_w))
    aux_barrel_len = max(
        0.0030, 2.0 * aux_knuckle_x - aux_knuckle_len - 2.0 * knuckle_axial_clearance
    )
    collar_len = 0.0014
    aux_tray_t = 0.0055
    aux_well_count = min(4, max(2, int(round(config.well_count / 3.0))))
    aux_cavity_depth = 0.0038
    fan_pivot_inset = 0.0120
    fan_pivot_y = rear_flat_y - fan_pivot_inset
    fan_tray_t = 0.0070
    fan_tray_outer_r = max(0.030, fan_radius_ratio * plan_d - fan_pivot_inset)
    fan_tray_inner_r = 0.26 * fan_tray_outer_r
    fan_half_rad = 0.62
    pivot_post_r = aux_bore_r - pivot_clearance
    post_h = 0.0060

    if config.opening == "fan_out_tray":
        aux_tray_pitch = (
            2.0 * fan_half_rad * 0.72 * (0.66 * fan_tray_outer_r) / float(aux_well_count)
        )
    else:
        aux_tray_pitch = (plan_w - 0.012) / float(aux_well_count)
    aux_pan_across = max(0.0040, min(pan_across, 0.90 * aux_tray_pitch))
    if config.opening == "second_hinged_tray":
        aux_pan_across = max(0.0040, min(aux_pan_across, 0.62 * aux_tray_depth))

    return ResolvedConfig(
        case_form=config.case_form,
        well_pattern=config.well_pattern,
        closure=config.closure,
        opening=config.opening,
        well_count=int(config.well_count),
        palette=config.palette,
        case_width_m=case_width,
        case_depth_m=case_depth,
        case_height_m=case_height,
        puck_flat_ratio=puck_flat_ratio,
        lid_open_rad=lid_open_rad,
        thumb_catch_width_m=thumb_catch_width,
        latch_press_rad=latch_press_rad,
        latch_travel_m=latch_travel,
        pan_fill_ratio=pan_fill_ratio,
        pan_depth_m=pan_depth,
        aux_tray_depth_m=aux_tray_depth,
        aux_open_rad=aux_open_rad,
        fan_sweep_rad=fan_sweep_rad,
        fan_radius_ratio=fan_radius_ratio,
        plan_kind=plan_kind,
        case_plan_w_m=plan_w,
        case_plan_d_m=plan_d,
        puck_radius_m=puck_radius,
        corner_r_m=corner_r,
        rear_flat_y_m=rear_flat_y,
        front_flat_y_m=front_flat_y,
        wall_t_m=wall_t,
        field_margin_m=field_margin,
        floor_t_m=floor_t,
        deck_relief_m=deck_relief,
        rim_top_z_m=rim_top_z,
        rim_w_m=rim_w,
        well_field_w_m=well_field_w,
        well_field_d_m=well_field_d,
        cavity_depth_m=cavity_depth,
        cavity_clearance_m=cavity_clearance,
        cup_floor_t_m=cup_floor_t,
        cup_wall_t_m=cup_wall_t,
        seat_gap_m=seat_gap,
        well_floor_z_m=well_floor_z,
        cake_top_z_m=cake_top_z,
        pan_across_m=pan_across,
        grid_cols=grid_cols,
        grid_rows=grid_rows,
        pan_pitch_x_m=pan_pitch_x,
        pan_pitch_y_m=pan_pitch_y,
        ring_rx_m=ring_rx,
        ring_ry_m=ring_ry,
        fan_span_rad=fan_span_rad,
        fan_apex_y_m=fan_apex_y,
        fan_inner_r_m=fan_inner_r,
        fan_outer_r_m=fan_outer_r,
        fan_wedge_rad=fan_wedge_rad,
        knuckle_r_m=knuckle_r,
        knuckle_gap_m=knuckle_gap,
        knuckle_len_m=knuckle_len,
        knuckle_x_m=knuckle_x,
        knuckle_axial_fit_m=knuckle_axial_fit,
        knuckle_axial_clearance_m=knuckle_axial_clearance,
        collar_len_m=collar_len,
        rear_span_m=rear_span,
        aux_span_m=aux_span,
        aux_barrel_len_m=aux_barrel_len,
        hinge_pin_r_m=hinge_pin_r,
        pin_clearance_m=pin_clearance,
        pin_len_m=pin_len,
        barrel_len_m=barrel_len,
        barrel_outer_r_m=barrel_outer_r,
        barrel_bore_r_m=barrel_bore_r,
        hinge_y_m=hinge_y,
        hinge_z_m=hinge_z,
        seat_interference_m=seat_interference,
        lid_t_m=lid_t,
        lid_plan_w_m=lid_plan_w,
        lid_plan_d_m=lid_plan_d,
        lid_rear_local_y_m=lid_rear_local_y,
        lid_front_local_y_m=lid_front_local_y,
        lid_recess_d_m=lid_recess_d,
        lid_recess_inset_m=lid_recess_inset,
        mirror_t_m=mirror_t,
        skirt_t_m=skirt_t,
        skirt_clearance_m=skirt_clearance,
        skirt_depth_m=skirt_depth,
        skirt_bottom_z_m=skirt_bottom_z,
        cake_top_clearance_m=cake_top_clearance,
        pocket_w_m=pocket_w,
        pocket_h_m=pocket_h,
        pocket_center_x_m=pocket_center_x,
        pocket_depth_m=pocket_depth,
        pocket_top_z_m=pocket_top_z,
        pocket_bot_z_m=pocket_bot_z,
        pocket_margin_m=pocket_margin,
        pocket_relief_m=pocket_relief,
        catch_lip_h_m=catch_lip_h,
        lid_lip_w_m=lid_lip_w,
        lid_lip_out_m=lid_lip_out,
        pivot_stub_r_m=pivot_stub_r,
        pivot_clearance_m=pivot_clearance,
        rocker_bore_r_m=rocker_bore_r,
        rocker_w_m=rocker_w,
        pivot_y_m=pivot_y,
        pivot_z_m=pivot_z,
        hook_top_z_m=hook_top_z,
        hook_arm_m=hook_arm,
        hook_swing_m=hook_swing,
        rail_len_m=rail_len,
        guide_clearance_m=guide_clearance,
        guide_slot_len_m=guide_slot_len,
        aux_hinge_offset_m=aux_hinge_offset,
        aux_hinge_floor_m=aux_hinge_floor,
        aux_hinge_y_m=aux_hinge_y,
        aux_hinge_z_m=aux_hinge_z,
        aux_knuckle_r_m=aux_knuckle_r,
        aux_knuckle_x_m=aux_knuckle_x,
        aux_knuckle_len_m=aux_knuckle_len,
        aux_pin_r_m=aux_pin_r,
        aux_bore_r_m=aux_bore_r,
        aux_tray_t_m=aux_tray_t,
        aux_well_count=aux_well_count,
        aux_pan_across_m=aux_pan_across,
        aux_cavity_depth_m=aux_cavity_depth,
        aux_tray_pitch_m=aux_tray_pitch,
        fan_pivot_inset_m=fan_pivot_inset,
        fan_pivot_y_m=fan_pivot_y,
        fan_tray_outer_r_m=fan_tray_outer_r,
        fan_tray_inner_r_m=fan_tray_inner_r,
        fan_tray_t_m=fan_tray_t,
        fan_half_rad=fan_half_rad,
        pivot_post_r_m=pivot_post_r,
        post_h_m=post_h,
        name=config.name,
    )


# ---------------------------------------------------------------------------
# palettes
# ---------------------------------------------------------------------------

_PALETTE_TABLE: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "pearl_white": {
        "shell": (0.90, 0.91, 0.91, 1.0),
        "deck": (0.85, 0.86, 0.86, 1.0),
        "cover": (0.94, 0.94, 0.92, 1.0),
        "trim": (0.74, 0.76, 0.77, 1.0),
        "metal": (0.62, 0.63, 0.64, 1.0),
        "mirror": (0.80, 0.84, 0.86, 1.0),
    },
    "satin_black": {
        "shell": (0.055, 0.052, 0.055, 1.0),
        "deck": (0.10, 0.10, 0.11, 1.0),
        "cover": (0.085, 0.082, 0.088, 1.0),
        "trim": (0.55, 0.56, 0.58, 1.0),
        "metal": (0.30, 0.31, 0.32, 1.0),
        "mirror": (0.78, 0.82, 0.83, 1.0),
    },
    "blush_rose": {
        "shell": (0.88, 0.68, 0.61, 1.0),
        "deck": (0.80, 0.60, 0.54, 1.0),
        "cover": (0.91, 0.74, 0.68, 1.0),
        "trim": (0.72, 0.43, 0.34, 1.0),
        "metal": (0.55, 0.35, 0.28, 1.0),
        "mirror": (0.82, 0.84, 0.85, 1.0),
    },
    "warm_taupe": {
        "shell": (0.47, 0.41, 0.36, 1.0),
        "deck": (0.39, 0.34, 0.30, 1.0),
        "cover": (0.55, 0.48, 0.42, 1.0),
        "trim": (0.78, 0.68, 0.45, 1.0),
        "metal": (0.44, 0.40, 0.35, 1.0),
        "mirror": (0.79, 0.82, 0.84, 1.0),
    },
    "deep_plum": {
        "shell": (0.26, 0.14, 0.23, 1.0),
        "deck": (0.20, 0.11, 0.18, 1.0),
        "cover": (0.33, 0.18, 0.29, 1.0),
        "trim": (0.72, 0.62, 0.72, 1.0),
        "metal": (0.38, 0.32, 0.38, 1.0),
        "mirror": (0.80, 0.83, 0.85, 1.0),
    },
    "mint_ivory": {
        "shell": (0.86, 0.90, 0.85, 1.0),
        "deck": (0.78, 0.84, 0.78, 1.0),
        "cover": (0.92, 0.95, 0.91, 1.0),
        "trim": (0.66, 0.74, 0.68, 1.0),
        "metal": (0.58, 0.62, 0.58, 1.0),
        "mirror": (0.81, 0.85, 0.84, 1.0),
    },
}

_SHADE_POOL: tuple[tuple[str, tuple[float, float, float, float]], ...] = (
    ("ivory_matte", (0.91, 0.88, 0.82, 1.0)),
    ("sand_matte", (0.62, 0.42, 0.30, 1.0)),
    ("caramel_matte", (0.48, 0.29, 0.20, 1.0)),
    ("peach_matte", (0.71, 0.46, 0.34, 1.0)),
    ("copper_glitter", (0.78, 0.43, 0.29, 1.0)),
    ("taupe_matte", (0.39, 0.27, 0.24, 1.0)),
    ("terracotta_matte", (0.49, 0.24, 0.16, 1.0)),
    ("coral_matte", (0.62, 0.27, 0.22, 1.0)),
    ("espresso_matte", (0.24, 0.16, 0.15, 1.0)),
    ("warm_peach", (0.88, 0.60, 0.36, 1.0)),
    ("pale_ivory", (0.94, 0.82, 0.58, 1.0)),
    ("golden_tan", (0.82, 0.49, 0.27, 1.0)),
    ("rose_tan", (0.78, 0.44, 0.34, 1.0)),
    ("mauve_blush", (0.68, 0.40, 0.38, 1.0)),
    ("deep_bronze", (0.55, 0.32, 0.18, 1.0)),
    ("soft_gold", (0.88, 0.72, 0.42, 1.0)),
)


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, object]:
    table = _PALETTE_TABLE[r.palette]
    mats: dict[str, object] = {
        key: model.material(f"{r.palette}_{key}", rgba=rgba) for key, rgba in table.items()
    }
    offset = PALETTES.index(r.palette) * 3
    shades = []
    for index in range(max(r.well_count, r.aux_well_count) + 2):
        name, rgba = _SHADE_POOL[(offset + index) % len(_SHADE_POOL)]
        shades.append(model.material(name, rgba=rgba))
    mats["shades"] = shades
    return mats


# ---------------------------------------------------------------------------
# plan / prism helpers
# ---------------------------------------------------------------------------


def _rounded_rect_points(
    width: float,
    depth: float,
    radius: float,
    *,
    cy: float = 0.0,
    segments: int = 6,
) -> list[tuple[float, float]]:
    half_w = width / 2.0
    half_d = depth / 2.0
    rad = max(0.0, min(radius, 0.49 * min(width, depth)))
    if rad <= 1e-6:
        return [
            (-half_w, cy - half_d),
            (half_w, cy - half_d),
            (half_w, cy + half_d),
            (-half_w, cy + half_d),
        ]
    corners = (
        (half_w - rad, half_d - rad, 0.0),
        (-(half_w - rad), half_d - rad, math.pi / 2.0),
        (-(half_w - rad), -(half_d - rad), math.pi),
        (half_w - rad, -(half_d - rad), 3.0 * math.pi / 2.0),
    )
    points: list[tuple[float, float]] = []
    for cx, corner_cy, start in corners:
        for step in range(segments + 1):
            angle = start + (math.pi / 2.0) * step / float(segments)
            points.append((cx + rad * math.cos(angle), cy + corner_cy + rad * math.sin(angle)))
    return points


@dataclass(frozen=True)
class _Plan:
    kind: str
    width: float
    depth: float
    cy: float
    corner_r: float

    def inset(self, delta: float) -> "_Plan":
        return _Plan(
            self.kind,
            max(0.0016, self.width - 2.0 * delta),
            max(0.0016, self.depth - 2.0 * delta),
            self.cy,
            max(0.0004, self.corner_r - delta),
        )

    def prism(self, z0: float, height: float) -> cq.Workplane:
        workplane = cq.Workplane("XY").workplane(offset=z0)
        if self.kind == "disc":
            return workplane.center(0.0, self.cy).circle(self.width / 2.0).extrude(height)
        points = _rounded_rect_points(self.width, self.depth, self.corner_r, cy=self.cy)
        return workplane.polyline(points).close().extrude(height)


def _case_plan(r: ResolvedConfig, *, grow: float = 0.0) -> _Plan:
    return _Plan(
        r.plan_kind,
        r.case_plan_w_m + 2.0 * grow,
        r.case_plan_d_m + 2.0 * grow,
        0.0,
        r.corner_r_m + grow,
    )


def _box_tool(
    size: tuple[float, float, float],
    center: tuple[float, float, float],
) -> cq.Workplane:
    return cq.Workplane("XY").box(size[0], size[1], size[2]).translate(center)


def _compound_tool(shapes: list[cq.Workplane]) -> cq.Workplane | None:
    values: list[object] = []
    for shape in shapes:
        values.extend(shape.vals())
    if not values:
        return None
    return cq.Workplane("XY").newObject(values)


def _place(shape: cq.Workplane, x: float, y: float, yaw: float) -> cq.Workplane:
    placed = shape
    if abs(yaw) > 1e-9:
        placed = placed.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(yaw))
    return placed.translate((x, y, 0.0))


def _x_cylinder(radius: float, length: float) -> cq.Workplane:
    return cq.Workplane("YZ").circle(radius).extrude(length / 2.0, both=True)


def _sector_points(
    inner_r: float,
    outer_r: float,
    half_angle: float,
    *,
    segments: int = 8,
) -> list[tuple[float, float]]:
    """Annular sector pointing toward local -Y with its apex at the local origin."""

    points: list[tuple[float, float]] = []
    for step in range(segments + 1):
        angle = -half_angle + 2.0 * half_angle * step / float(segments)
        points.append((outer_r * math.sin(angle), -outer_r * math.cos(angle)))
    for step in range(segments + 1):
        angle = half_angle - 2.0 * half_angle * step / float(segments)
        points.append((inner_r * math.sin(angle), -inner_r * math.cos(angle)))
    return points


def _sector_prism(
    inner_r: float,
    outer_r: float,
    half_angle: float,
    z0: float,
    height: float,
) -> cq.Workplane:
    points = _sector_points(inner_r, outer_r, half_angle)
    return cq.Workplane("XY").workplane(offset=z0).polyline(points).close().extrude(height)


# ---------------------------------------------------------------------------
# well pattern geometry
# ---------------------------------------------------------------------------


def _well_placements(r: ResolvedConfig) -> list[tuple[float, float, float]]:
    """(x, y, yaw) of each pan's local frame origin, in case coordinates."""

    if r.well_pattern == "orthogonal_grid":
        placements: list[tuple[float, float, float]] = []
        for row in range(r.grid_rows):
            for col in range(r.grid_cols):
                if len(placements) >= r.well_count:
                    break
                x = (col - (r.grid_cols - 1) / 2.0) * r.pan_pitch_x_m
                y = ((r.grid_rows - 1) / 2.0 - row) * r.pan_pitch_y_m
                placements.append((x, y, 0.0))
        return placements
    if r.well_pattern == "radial_ring":
        return [
            (
                r.ring_rx_m * math.cos(2.0 * math.pi * index / r.well_count),
                r.ring_ry_m * math.sin(2.0 * math.pi * index / r.well_count),
                0.0,
            )
            for index in range(r.well_count)
        ]
    fan: list[tuple[float, float, float]] = []
    for index in range(r.well_count):
        fraction = (index + 0.5) / float(r.well_count) - 0.5
        fan.append((0.0, r.fan_apex_y_m, fraction * r.fan_span_rad))
    return fan


def _well_cup_shape(r: ResolvedConfig) -> cq.Workplane:
    """One pan cup: a real hollow liner with a floor, walls and an open rim."""

    height = r.cup_floor_t_m + r.pan_depth_m
    if r.well_pattern == "radial_ring":
        outer = cq.Workplane("XY").circle(r.pan_across_m / 2.0).extrude(height)
        inner = (
            cq.Workplane("XY")
            .workplane(offset=r.cup_floor_t_m)
            .circle(max(0.0006, r.pan_across_m / 2.0 - r.cup_wall_t_m))
            .extrude(height)
        )
        return outer.cut(inner)
    if r.well_pattern == "fan_sector":
        half = r.fan_wedge_rad / 2.0
        outer = _sector_prism(r.fan_inner_r_m, r.fan_outer_r_m, half, 0.0, height)
        inner_half = max(0.020, half - r.cup_wall_t_m / max(0.004, r.fan_outer_r_m))
        inner = _sector_prism(
            r.fan_inner_r_m + r.cup_wall_t_m,
            r.fan_outer_r_m - r.cup_wall_t_m,
            min(half * 0.94, inner_half),
            r.cup_floor_t_m,
            height,
        )
        return outer.cut(inner)
    plan = _Plan("rect", r.pan_across_m, r.pan_across_m, 0.0, 0.20 * r.pan_across_m)
    outer = plan.prism(0.0, height)
    inner = plan.inset(r.cup_wall_t_m).prism(r.cup_floor_t_m, height)
    return outer.cut(inner)


def _well_cake_shape(r: ResolvedConfig) -> cq.Workplane:
    """One pressed cake: a three-station pressing with a raised centre crown."""

    base_z = r.cup_floor_t_m
    body_h = max(0.0010, r.pan_depth_m - 0.0004)
    step_h = max(0.0003, 0.22 * body_h)
    mid_h = max(0.0003, 0.20 * body_h)
    lower_h = max(0.0004, body_h - step_h - mid_h)
    if r.well_pattern == "radial_ring":
        radius = max(0.0006, r.pan_across_m / 2.0 - r.cup_wall_t_m - 0.0002)
        cake = cq.Workplane("XY").workplane(offset=base_z).circle(radius).extrude(lower_h)
        mid = (
            cq.Workplane("XY")
            .workplane(offset=base_z + lower_h)
            .circle(radius * 0.94)
            .extrude(mid_h)
        )
        crown = (
            cq.Workplane("XY")
            .workplane(offset=base_z + lower_h + mid_h)
            .circle(radius * 0.62)
            .extrude(step_h)
        )
        return cake.union(mid).union(crown)
    if r.well_pattern == "fan_sector":
        half = r.fan_wedge_rad / 2.0
        inner_r = r.fan_inner_r_m + r.cup_wall_t_m + 0.0002
        outer_r = max(inner_r + 0.0018, r.fan_outer_r_m - r.cup_wall_t_m - 0.0002)
        half_in = max(0.015, half * 0.88)
        cake = _sector_prism(inner_r, outer_r, half_in, base_z, lower_h)
        mid = _sector_prism(
            inner_r + 0.0003,
            outer_r - 0.0003,
            half_in * 0.92,
            base_z + lower_h,
            mid_h,
        )
        crown = _sector_prism(
            inner_r + 0.0009,
            outer_r - 0.0009,
            half_in * 0.66,
            base_z + lower_h + mid_h,
            step_h,
        )
        return cake.union(mid).union(crown)
    across = max(0.0016, r.pan_across_m - 2.0 * r.cup_wall_t_m - 0.0004)
    lower = _Plan("rect", across, across, 0.0, 0.18 * across)
    cake = lower.prism(base_z, lower_h)
    mid = lower.inset(0.04 * across).prism(base_z + lower_h, mid_h)
    crown = lower.inset(0.18 * across).prism(base_z + lower_h + mid_h, step_h)
    return cake.union(mid).union(crown)


def _well_cavity_shapes(r: ResolvedConfig) -> list[cq.Workplane]:
    """Real recesses cut into the case deck, one per well."""

    depth = r.cavity_depth_m + 0.0015
    shapes: list[cq.Workplane] = []
    for x, y, yaw in _well_placements(r):
        if r.well_pattern == "radial_ring":
            shape = (
                cq.Workplane("XY")
                .workplane(offset=r.well_floor_z_m)
                .circle(r.pan_across_m / 2.0 + r.cavity_clearance_m)
                .extrude(depth)
            )
        elif r.well_pattern == "fan_sector":
            half = r.fan_wedge_rad / 2.0
            shape = _sector_prism(
                max(0.0015, r.fan_inner_r_m - r.cavity_clearance_m),
                r.fan_outer_r_m + r.cavity_clearance_m,
                half * 1.05,
                r.well_floor_z_m,
                depth,
            )
        else:
            side = r.pan_across_m + 2.0 * r.cavity_clearance_m
            shape = _Plan("rect", side, side, 0.0, 0.20 * side).prism(r.well_floor_z_m, depth)
        shapes.append(_place(shape, x, y, yaw))
    return shapes


# ---------------------------------------------------------------------------
# case shell
# ---------------------------------------------------------------------------


def _closure_pocket_tools(r: ResolvedConfig) -> list[cq.Workplane]:
    tools: list[cq.Workplane] = [
        _box_tool(
            (r.pocket_w_m, 2.0 * r.pocket_depth_m, r.pocket_h_m),
            (
                r.pocket_center_x_m,
                r.front_flat_y_m,
                0.5 * (r.pocket_bot_z_m + r.pocket_top_z_m),
            ),
        )
    ]
    if r.closure == "sliding_latch":
        tools.append(
            _box_tool(
                (
                    r.guide_slot_len_m,
                    2.0 * r.pocket_depth_m + 0.004,
                    0.0026 + 2.0 * r.guide_clearance_m,
                ),
                (
                    r.pocket_center_x_m,
                    r.front_flat_y_m + 0.5 * r.pocket_depth_m,
                    r.pocket_bot_z_m + 0.5 * r.pocket_h_m,
                ),
            )
        )
    return tools


def _case_shell_solid(r: ResolvedConfig) -> cq.Workplane:
    plan = _case_plan(r)
    body = plan.prism(0.0, r.case_height_m)

    if r.plan_kind == "disc":
        span = 4.0 * r.puck_radius_m
        body = body.cut(
            _box_tool(
                (span, span, span),
                (0.0, r.rear_flat_y_m + span / 2.0, r.case_height_m / 2.0),
            )
        )
        body = body.cut(
            _box_tool(
                (span, span, span),
                (0.0, r.front_flat_y_m - span / 2.0, r.case_height_m / 2.0),
            )
        )
        deck_radius = r.rear_flat_y_m - r.wall_t_m
        deck_plan = _Plan("disc", 2.0 * deck_radius, 2.0 * deck_radius, 0.0, 0.0)
    else:
        deck_plan = plan.inset(r.wall_t_m)

    body = body.cut(deck_plan.prism(r.case_height_m - r.deck_relief_m, r.deck_relief_m + 0.002))

    cavities = _compound_tool(_well_cavity_shapes(r))
    if cavities is not None:
        body = body.cut(cavities)

    pocket = _compound_tool(_closure_pocket_tools(r))
    if pocket is not None:
        body = body.cut(pocket)

    if r.opening == "fan_out_tray":
        body = body.cut(
            cq.Workplane("XY")
            .workplane(offset=-0.001)
            .center(0.0, r.fan_pivot_y_m)
            .circle(r.pivot_post_r_m + 0.0012)
            .extrude(0.0014)
        )
    return body


def _case_hinge_hardware(case: object, r: ResolvedConfig, mats: dict[str, object]) -> None:
    for index, sign in enumerate((-1.0, 1.0)):
        case.visual(
            Cylinder(radius=r.knuckle_r_m, length=r.knuckle_len_m),
            origin=Origin(
                xyz=(sign * r.knuckle_x_m, r.hinge_y_m, r.hinge_z_m),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["shell"],
            name=f"case__hinge_knuckle_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    # Two moulded bosses bridge the rear wall to each knuckle. They sit outside
    # the cover barrel's axial band and below the closed cover, so the knuckles
    # are real supported hardware rather than floating cylinders.
    boss_top = r.hinge_z_m - r.knuckle_r_m + 0.0004
    boss_depth = r.hinge_y_m - r.rear_flat_y_m + 0.0016
    for index, sign in enumerate((-1.0, 1.0)):
        case.visual(
            Box((r.knuckle_len_m, boss_depth, 0.0016)),
            origin=Origin(
                xyz=(
                    sign * r.knuckle_x_m,
                    0.5 * (r.rear_flat_y_m - 0.0016 + r.hinge_y_m),
                    boss_top - 0.0008,
                )
            ),
            material=mats["shell"],
            name=f"case__hinge_boss_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    rail_rear_y = r.hinge_y_m - r.barrel_outer_r_m - 0.0006
    case.visual(
        Box(
            (
                2.0 * r.knuckle_x_m + r.knuckle_len_m,
                rail_rear_y - r.rear_flat_y_m + 0.0016,
                0.0016,
            )
        ),
        origin=Origin(
            xyz=(
                0.0,
                0.5 * (r.rear_flat_y_m - 0.0016 + rail_rear_y),
                boss_top - 0.0008,
            )
        ),
        material=mats["shell"],
        name="case__hinge_rail", material_class_id="plastic.opaque_glossy_molded",
    )
    case.visual(
        Cylinder(radius=r.hinge_pin_r_m, length=r.pin_len_m),
        origin=Origin(
            xyz=(0.0, r.hinge_y_m, r.hinge_z_m),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["metal"],
        name="case__hinge_pin", material_class_id="metal.stainless_matte",
    )


def _case_rim_trim(case: object, r: ResolvedConfig, mats: dict[str, object]) -> None:
    plan = _case_plan(r)
    outer = plan.inset(0.0004)
    inner = plan.inset(r.wall_t_m - 0.0005)
    ring = outer.prism(r.case_height_m - 0.0006, 0.0006).cut(
        inner.prism(r.case_height_m - 0.0012, 0.0025)
    )
    case.visual(
        mesh_from_cadquery(ring, "makeup1_rim_trim", tolerance=0.00025),
        material=mats["trim"],
        name="case__rim_trim", material_class_id="metal.paint_coated",
    )


def _case_shell_visual(
    case: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    local_name: str,
) -> None:
    case.visual(
        mesh_from_cadquery(
            _case_shell_solid(r),
            f"makeup1_case_{r.case_form}",
            tolerance=0.00035,
        ),
        material=mats["shell"],
        name=local_name, material_class_id="plastic.opaque_glossy_molded",
    )


def _case_form_rounded_rectangle_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    _case_shell_visual(case, r, mats, "case_form__rounded_rectangle__shell")
    _case_rim_trim(case, r, mats)
    _case_hinge_hardware(case, r, mats)


def _case_form_elongated_rectangle_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    _case_shell_visual(case, r, mats, "case_form__elongated_rectangle__shell")
    _case_rim_trim(case, r, mats)
    pad_w = min(0.014, 0.10 * r.case_plan_w_m)
    pad_d = min(0.010, 0.45 * r.case_plan_d_m)
    for index, sign in enumerate((-1.0, 1.0)):
        pad = _Plan("rect", pad_w, pad_d, 0.0, 0.0012).prism(
            r.case_height_m - r.deck_relief_m, r.deck_relief_m
        )
        pad = pad.translate(
            (
                sign * (r.case_plan_w_m / 2.0 - r.wall_t_m - pad_w / 2.0 - 0.0005),
                0.0,
                0.0,
            )
        )
        case.visual(
            mesh_from_cadquery(pad, f"makeup1_end_pad_{index}", tolerance=0.00025),
            material=mats["trim"],
            name=f"case_form__elongated_rectangle__end_pad_{index}", material_class_id="metal.paint_coated",
        )
    _case_hinge_hardware(case, r, mats)


def _case_form_round_puck_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    _case_shell_visual(case, r, mats, "case_form__round_puck__shell")
    _case_rim_trim(case, r, mats)
    flat_depth = r.puck_radius_m - r.rear_flat_y_m
    chord = 2.0 * math.sqrt(max(1e-8, r.puck_radius_m**2 - r.rear_flat_y_m**2))
    pad = _box_tool(
        (max(0.006, 0.8 * chord), 0.0016, 0.0024),
        (0.0, r.rear_flat_y_m - 0.0008, r.case_height_m - 0.0012),
    )
    case.visual(
        mesh_from_cadquery(pad, "makeup1_puck_hinge_pad", tolerance=0.00025),
        material=mats["trim"],
        name="case_form__round_puck__hinge_chord_pad", material_class_id="metal.paint_coated",
    )
    front_pad = _box_tool(
        (max(0.006, 0.55 * chord), 0.0014, 0.0020),
        (
            0.0,
            r.front_flat_y_m + 0.0007 + flat_depth * 0.0,
            max(0.0016, 0.35 * r.pocket_bot_z_m),
        ),
    )
    case.visual(
        mesh_from_cadquery(front_pad, "makeup1_puck_front_pad", tolerance=0.00025),
        material=mats["trim"],
        name="case_form__round_puck__latch_chord_pad", material_class_id="metal.paint_coated",
    )
    _case_hinge_hardware(case, r, mats)


# ---------------------------------------------------------------------------
# well pattern builders
# ---------------------------------------------------------------------------


def _emit_wells(
    case: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    candidate: str,
) -> None:
    cup_mesh = mesh_from_cadquery(
        _well_cup_shape(r),
        f"makeup1_pan_cup_{r.well_pattern}",
        tolerance=0.00010,
    )
    cake_mesh = mesh_from_cadquery(
        _well_cake_shape(r),
        f"makeup1_pressed_cake_{r.well_pattern}",
        tolerance=0.00010,
    )
    shades = mats["shades"]
    for index, (x, y, yaw) in enumerate(_well_placements(r)):
        origin = Origin(xyz=(x, y, r.well_floor_z_m), rpy=(0.0, 0.0, yaw))
        case.visual(
            cup_mesh,
            origin=origin,
            material=mats["trim"],
            name=f"well_pattern__{candidate}__cup_{index}", material_class_id="metal.aluminum_bare",
        )
        case.visual(
            cake_mesh,
            origin=origin,
            material=shades[index % len(shades)],
            name=f"well_pattern__{candidate}__cake_{index}", material_class_id="organic.wax",
        )


def _well_pattern_orthogonal_grid_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    _emit_wells(case, r, mats, "orthogonal_grid")


def _well_pattern_radial_ring_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    _emit_wells(case, r, mats, "radial_ring")


def _well_pattern_fan_sector_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    _emit_wells(case, r, mats, "fan_sector")


# ---------------------------------------------------------------------------
# cover
# ---------------------------------------------------------------------------


def _lid_plan(r: ResolvedConfig) -> _Plan:
    if r.plan_kind == "disc":
        radius = r.puck_radius_m + r.skirt_t_m + r.skirt_clearance_m
        return _Plan("disc", 2.0 * radius, 2.0 * radius, -r.hinge_y_m, 0.0)
    center_y = 0.5 * (r.lid_rear_local_y_m + r.lid_front_local_y_m)
    return _Plan(
        "rect",
        r.lid_plan_w_m,
        r.lid_plan_d_m,
        center_y,
        r.corner_r_m + r.skirt_t_m + r.skirt_clearance_m,
    )


def _lid_solid(r: ResolvedConfig) -> cq.Workplane:
    plan = _lid_plan(r)
    span = 3.0 * (r.case_plan_d_m + r.case_plan_w_m)
    panel = plan.prism(-r.lid_t_m / 2.0, r.lid_t_m)
    panel = panel.cut(_box_tool((span, span, span), (0.0, r.lid_rear_local_y_m + span / 2.0, 0.0)))
    recess = plan.inset(r.lid_recess_inset_m).prism(
        -r.lid_t_m / 2.0 - 0.0002, r.lid_recess_d_m + 0.0002
    )
    panel = panel.cut(recess)

    skirt = plan.prism(-r.lid_t_m / 2.0 - r.skirt_depth_m, r.skirt_depth_m).cut(
        plan.inset(r.skirt_t_m).prism(
            -r.lid_t_m / 2.0 - r.skirt_depth_m - 0.001, r.skirt_depth_m + 0.002
        )
    )
    skirt = skirt.cut(
        _box_tool(
            (span, span, span),
            (0.0, r.lid_rear_local_y_m - 0.0018 + span / 2.0, 0.0),
        )
    )
    panel = panel.union(skirt)

    barrel = _x_cylinder(r.barrel_outer_r_m, r.barrel_len_m).cut(
        _x_cylinder(r.barrel_bore_r_m, r.barrel_len_m + 0.002)
    )
    bridge = _box_tool(
        (
            r.barrel_len_m - 0.0016,
            abs(r.lid_rear_local_y_m) + r.barrel_outer_r_m,
            0.0018,
        ),
        (
            0.0,
            0.5 * (r.lid_rear_local_y_m - r.barrel_outer_r_m),
            -r.lid_t_m / 2.0 + 0.0009,
        ),
    )
    assembled = panel.union(barrel).union(bridge)
    return assembled.cut(_x_cylinder(r.barrel_bore_r_m, r.barrel_len_m + 0.006))


def _thrust_collar(outer_r: float, bore_r: float, length: float) -> cq.Workplane:
    """A bored collar that locates a barrel axially against its knuckle face."""

    return _x_cylinder(outer_r, length).cut(_x_cylinder(bore_r, length + 0.002))


def _lid_inner_layers(lid: object, r: ResolvedConfig, mats: dict[str, object]) -> None:
    plan = _lid_plan(r)
    recess = plan.inset(r.lid_recess_inset_m)
    ceiling = -r.lid_t_m / 2.0 + r.lid_recess_d_m
    span = 3.0 * (r.case_plan_d_m + r.case_plan_w_m)
    rear_cut = _box_tool((span, span, span), (0.0, r.lid_rear_local_y_m + span / 2.0, 0.0))
    mirror = recess.inset(0.0008).prism(ceiling - r.mirror_t_m, r.mirror_t_m)
    mirror = mirror.cut(rear_cut)
    lid.visual(
        mesh_from_cadquery(mirror, "makeup1_cover_mirror", tolerance=0.00025),
        material=mats["mirror"],
        name="lid__mirror_plate", material_class_id="glass.mirror",
    )
    bezel = recess.prism(-r.lid_t_m / 2.0, 0.0005).cut(
        recess.inset(0.0010).prism(-r.lid_t_m / 2.0 - 0.001, 0.004)
    )
    bezel = bezel.cut(rear_cut)
    lid.visual(
        mesh_from_cadquery(bezel, "makeup1_cover_bezel", tolerance=0.00025),
        material=mats["trim"],
        name="lid__mirror_bezel", material_class_id="metal.paint_coated",
    )


def _new_lid(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, object]) -> object:
    lid = model.part(
        "lid",
        meta={
            "role": "lid",
            "seats_on_case_rim": True,
            "captured_pin_bore": True,
            "lid_plan_w_m": r.lid_plan_w_m,
        },
    )
    lid.visual(
        mesh_from_cadquery(_lid_solid(r), "makeup1_cover_shell", tolerance=0.00035),
        material=mats["cover"],
        name="lid__cover_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    _lid_inner_layers(lid, r, mats)
    # The interleaved knuckles locate the cover axially: a bored collar on each
    # barrel end bears on its knuckle face while the barrel itself keeps a real
    # 0.8 mm axial clearance and the pin keeps its radial clearance.
    face_x = r.knuckle_x_m - r.knuckle_len_m / 2.0
    collar = _thrust_collar(r.barrel_outer_r_m, r.barrel_bore_r_m, r.collar_len_m)
    for index, sign in enumerate((-1.0, 1.0)):
        lid.visual(
            mesh_from_cadquery(
                collar.translate(
                    (
                        sign * (face_x - r.collar_len_m / 2.0 + r.knuckle_axial_fit_m),
                        0.0,
                        0.0,
                    )
                ),
                f"makeup1_cover_thrust_collar_{index}",
                tolerance=0.00010,
            ),
            material=mats["metal"],
            name=f"lid__hinge_thrust_collar_{index}", material_class_id="metal.stainless_matte",
        )
    return lid


# ---------------------------------------------------------------------------
# closure builders
# ---------------------------------------------------------------------------


def _lid_catch_lip(
    lid: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    local_name: str,
) -> None:
    lip = _box_tool(
        (r.lid_lip_w_m, r.lid_lip_out_m, 0.0018),
        (
            0.0,
            r.lid_front_local_y_m + r.lid_lip_out_m / 2.0 - 0.0002,
            -r.lid_t_m / 2.0 - r.skirt_depth_m + 0.0009,
        ),
    )
    lid.visual(
        mesh_from_cadquery(lip, f"makeup1_{local_name}", tolerance=0.00020),
        material=mats["metal"],
        name=local_name, material_class_id="metal.stainless_matte",
    )


def _closure_rear_hinge_build(
    model: ArticulatedObject,
    case: object,
    lid: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> tuple[object | None, str, tuple[float, float, float] | None]:
    lip = _box_tool(
        (r.thumb_catch_width_m, 0.0014, r.catch_lip_h_m),
        (0.0, r.front_flat_y_m + 0.0009, r.pocket_bot_z_m + r.catch_lip_h_m / 2.0),
    )
    case.visual(
        mesh_from_cadquery(lip, "makeup1_thumb_catch_lip", tolerance=0.00020),
        material=mats["trim"],
        name="closure__rear_hinge__catch_lip", material_class_id="metal.paint_coated",
    )
    tab = _box_tool(
        (r.thumb_catch_width_m + 0.004, 0.0016, 0.0016),
        (
            0.0,
            r.lid_front_local_y_m + 0.0006,
            -r.lid_t_m / 2.0 - r.skirt_depth_m + 0.0008,
        ),
    )
    lid.visual(
        mesh_from_cadquery(tab, "makeup1_lid_thumb_tab", tolerance=0.00020),
        material=mats["cover"],
        name="closure__rear_hinge__lid_thumb_tab", material_class_id="plastic.opaque_glossy_molded",
    )
    return None, "", None


def _closure_push_latch_build(
    model: ArticulatedObject,
    case: object,
    lid: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> tuple[object | None, str, tuple[float, float, float] | None]:
    _lid_catch_lip(lid, r, mats, "closure__push_latch__lid_strike")
    stub_x = r.pocket_w_m / 2.0 - 0.0008
    for index, sign in enumerate((-1.0, 1.0)):
        case.visual(
            Cylinder(radius=r.pivot_stub_r_m, length=0.0032),
            origin=Origin(
                xyz=(sign * stub_x, r.pivot_y_m, r.pivot_z_m),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["metal"],
            name=f"closure__push_latch__pivot_stub_{index}", material_class_id="metal.stainless_matte",
        )

    latch = model.part(
        "latch",
        meta={
            "role": "latch",
            "slot": "closure",
            "candidate": "push_latch",
            "captured_bore": True,
            "hook_swing_m": r.hook_swing_m,
        },
    )
    hub = _x_cylinder(0.0022, r.pocket_w_m - 2.0 * r.knuckle_axial_clearance_m)
    arm_front = r.front_flat_y_m - 0.0035
    arm_span = r.pivot_y_m - arm_front
    arm = _box_tool(
        (0.0080, arm_span, 0.0018),
        (0.0, 0.5 * (arm_front + r.pivot_y_m) - r.pivot_y_m, 0.0),
    )
    hook_h = 0.0015
    hook = _box_tool(
        (0.0100, 0.0025, r.hook_arm_m),
        (0.0, arm_front + 0.00125 - r.pivot_y_m, r.hook_arm_m / 2.0),
    )
    hook_tip = _box_tool(
        (0.0100, 0.0030, hook_h),
        (0.0, arm_front + 0.0022 - r.pivot_y_m, r.hook_arm_m - hook_h / 2.0),
    )
    button = _box_tool(
        (r.rocker_w_m, 0.0028, 0.0016),
        (0.0, r.front_flat_y_m - 0.0018 - r.pivot_y_m, -0.0010),
    )
    body = hub.union(arm).union(hook).union(hook_tip).union(button)
    body = body.cut(_x_cylinder(r.rocker_bore_r_m, r.pocket_w_m + 0.006))
    latch.visual(
        mesh_from_cadquery(body, "makeup1_push_latch_rocker", tolerance=0.00022),
        material=mats["metal"],
        name="closure__push_latch__rocker", material_class_id="metal.stainless_matte",
    )
    wall_x = r.pocket_w_m / 2.0
    pivot_collar = _thrust_collar(0.0020, r.rocker_bore_r_m, r.collar_len_m)
    for index, sign in enumerate((-1.0, 1.0)):
        latch.visual(
            mesh_from_cadquery(
                pivot_collar.translate(
                    (
                        sign * (wall_x - r.collar_len_m / 2.0 + r.knuckle_axial_fit_m),
                        0.0,
                        0.0,
                    )
                ),
                f"makeup1_push_latch_collar_{index}",
                tolerance=0.00010,
            ),
            material=mats["metal"],
            name=f"closure__push_latch__pivot_collar_{index}", material_class_id="metal.stainless_matte",
        )
    return latch, "latch_press", (0.0, r.pivot_y_m, r.pivot_z_m)


def _closure_sliding_latch_build(
    model: ArticulatedObject,
    case: object,
    lid: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> tuple[object | None, str, tuple[float, float, float] | None]:
    _lid_catch_lip(lid, r, mats, "closure__sliding_latch__lid_catch_lip")
    guide_z = r.pocket_bot_z_m + 0.5 * r.pocket_h_m
    for index, sign in enumerate((-1.0, 1.0)):
        case.visual(
            Box((0.0020, r.pocket_depth_m - 0.0006, 0.0022)),
            origin=Origin(
                xyz=(
                    r.pocket_center_x_m + sign * (r.pocket_w_m / 2.0 - 0.0006),
                    r.front_flat_y_m + 0.5 * r.pocket_depth_m,
                    guide_z,
                )
            ),
            material=mats["metal"],
            name=f"closure__sliding_latch__guide_rib_{index}", material_class_id="metal.stainless_matte",
        )
    # The slider rides on a real moulded runner ledge along the whole travel;
    # the rail's underside rests on it instead of floating inside the slot.
    runner_depth = r.pocket_depth_m + 0.0030
    case.visual(
        Box((r.guide_slot_len_m, runner_depth, 0.0012)),
        origin=Origin(
            xyz=(
                r.pocket_center_x_m,
                r.front_flat_y_m + 0.5 * runner_depth,
                guide_z - 0.0013 + 0.00003 - 0.0006,
            )
        ),
        material=mats["metal"],
        name="closure__sliding_latch__guide_runner", material_class_id="metal.stainless_matte",
    )

    latch = model.part(
        "latch",
        meta={
            "role": "latch",
            "slot": "closure",
            "candidate": "sliding_latch",
            "guided_slot": True,
            "latch_travel_m": r.latch_travel_m,
        },
    )
    thumb = _Plan("rect", 0.0140, 0.0026, 0.0, 0.0008).prism(-0.0013, 0.0026)
    thumb = thumb.translate((0.0, r.front_flat_y_m - 0.0018, guide_z))
    rail = _box_tool(
        (r.rail_len_m, r.pocket_depth_m + 0.0016, 0.0026),
        (
            0.0,
            r.front_flat_y_m + 0.5 * (r.pocket_depth_m + 0.0016) - 0.0016,
            guide_z,
        ),
    )
    hook = _box_tool(
        (0.0020, 0.0034, max(0.0010, r.hook_top_z_m - guide_z)),
        (0.0, r.front_flat_y_m - 0.0026, 0.5 * (guide_z + r.hook_top_z_m)),
    )
    hook_tip = _box_tool(
        (0.0020, 0.0040, 0.0014),
        (0.0, r.front_flat_y_m - 0.0030, r.hook_top_z_m - 0.0007),
    )
    body = thumb.union(rail).union(hook).union(hook_tip)
    latch.visual(
        mesh_from_cadquery(body, "makeup1_sliding_latch", tolerance=0.00022),
        material=mats["metal"],
        name="closure__sliding_latch__slider", material_class_id="metal.stainless_matte",
    )
    return latch, "latch_slide", (0.0, 0.0, 0.0)


# ---------------------------------------------------------------------------
# opening builders
# ---------------------------------------------------------------------------


def _aux_cup_and_cake(r: ResolvedConfig) -> tuple[cq.Workplane, cq.Workplane]:
    radius = r.aux_pan_across_m / 2.0
    height = max(0.0018, r.aux_cavity_depth_m - 0.0004)
    floor = 0.0007
    cup = cq.Workplane("XY").circle(radius).extrude(height)
    cup = cup.cut(
        cq.Workplane("XY")
        .workplane(offset=floor)
        .circle(max(0.0005, radius - r.cup_wall_t_m))
        .extrude(height)
    )
    cake_r = max(0.0004, radius - r.cup_wall_t_m - 0.0002)
    cake_h = max(0.0008, height - floor - 0.0003)
    cake = cq.Workplane("XY").workplane(offset=floor).circle(cake_r).extrude(cake_h)
    crown = (
        cq.Workplane("XY")
        .workplane(offset=floor + cake_h)
        .circle(cake_r * 0.66)
        .extrude(max(0.0003, 0.22 * cake_h))
    )
    return cup, cake.union(crown)


def _emit_aux_wells(
    tray: object,
    r: ResolvedConfig,
    mats: dict[str, object],
    candidate: str,
    placements: list[tuple[float, float, float]],
) -> None:
    cup_shape, cake_shape = _aux_cup_and_cake(r)
    cup_mesh = mesh_from_cadquery(cup_shape, f"makeup1_aux_cup_{candidate}", tolerance=0.00010)
    cake_mesh = mesh_from_cadquery(cake_shape, f"makeup1_aux_cake_{candidate}", tolerance=0.00010)
    shades = mats["shades"]
    for index, (x, y, z) in enumerate(placements):
        origin = Origin(xyz=(x, y, z))
        tray.visual(
            cup_mesh,
            origin=origin,
            material=mats["trim"],
            name=f"opening__{candidate}__aux_cup_{index}", material_class_id="metal.aluminum_bare",
        )
        tray.visual(
            cake_mesh,
            origin=origin,
            material=shades[(index + 2) % len(shades)],
            name=f"opening__{candidate}__aux_cake_{index}", material_class_id="organic.wax",
        )


def _opening_single_lid_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> tuple[object | None, str, tuple[float, float, float] | None, tuple[float, float, float]]:
    boss = _box_tool(
        (min(0.020, 0.18 * r.case_plan_w_m), 0.0016, 0.0020),
        (0.0, r.front_flat_y_m - 0.0006, max(0.0018, 0.30 * r.pocket_bot_z_m)),
    )
    case.visual(
        mesh_from_cadquery(boss, "makeup1_single_lid_front_boss", tolerance=0.00020),
        material=mats["deck"],
        name="opening__single_lid__solid_front_boss", material_class_id="plastic.opaque_glossy_molded",
    )
    return None, "", None, (-1.0, 0.0, 0.0)


def _front_tray_solid(r: ResolvedConfig) -> cq.Workplane:
    depth = r.aux_tray_depth_m
    width = max(0.020, r.case_plan_w_m - 0.004)
    half_t = r.aux_tray_t_m / 2.0
    body_center_y = -(0.0032 + depth / 2.0)
    plan = _Plan("rect", width, depth, body_center_y, min(0.0030, 0.10 * depth))
    tray = plan.prism(-half_t, r.aux_tray_t_m)
    wall_h = 0.0016
    rim = plan.prism(half_t, wall_h).cut(plan.inset(0.0012).prism(half_t - 0.0010, wall_h + 0.002))
    tray = tray.union(rim)
    tray = tray.cut(
        plan.inset(0.0012).prism(
            half_t - r.aux_cavity_depth_m, r.aux_cavity_depth_m + wall_h + 0.001
        )
    )
    barrel = _x_cylinder(r.aux_knuckle_r_m, r.aux_barrel_len_m)
    bridge = _box_tool(
        (max(0.0026, r.aux_barrel_len_m - 0.0012), 0.0042, 0.0016),
        (0.0, -0.0023, 0.0),
    )
    assembled = tray.union(barrel).union(bridge)
    return assembled.cut(_x_cylinder(r.aux_bore_r_m, r.aux_barrel_len_m + 0.006))


def _opening_second_hinged_tray_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> tuple[object | None, str, tuple[float, float, float] | None, tuple[float, float, float]]:
    for index, sign in enumerate((-1.0, 1.0)):
        case.visual(
            Cylinder(radius=r.aux_knuckle_r_m, length=r.aux_knuckle_len_m),
            origin=Origin(
                xyz=(sign * r.aux_knuckle_x_m, r.aux_hinge_y_m, r.aux_hinge_z_m),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["shell"],
            name=f"opening__second_hinged_tray__front_knuckle_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        case.visual(
            Box((r.aux_knuckle_len_m, r.aux_hinge_offset_m, 0.0026)),
            origin=Origin(
                xyz=(
                    sign * r.aux_knuckle_x_m,
                    r.front_flat_y_m - r.aux_hinge_offset_m / 2.0 + 0.0005,
                    r.aux_hinge_z_m,
                )
            ),
            material=mats["shell"],
            name=f"opening__second_hinged_tray__front_tab_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    case.visual(
        Cylinder(
            radius=r.aux_pin_r_m,
            length=2.0 * r.aux_knuckle_x_m + r.aux_knuckle_len_m,
        ),
        origin=Origin(
            xyz=(0.0, r.aux_hinge_y_m, r.aux_hinge_z_m),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["metal"],
        name="opening__second_hinged_tray__front_pin", material_class_id="metal.stainless_matte",
    )

    tray = model.part(
        "front_tray",
        meta={
            "role": "front_tray",
            "slot": "opening",
            "candidate": "second_hinged_tray",
            "welled_tray": True,
            "aux_well_count": r.aux_well_count,
        },
    )
    tray.visual(
        mesh_from_cadquery(_front_tray_solid(r), "makeup1_front_tray_shell", tolerance=0.00030),
        material=mats["shell"],
        name="opening__second_hinged_tray__tray_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    well_z = r.aux_tray_t_m / 2.0 - r.aux_cavity_depth_m
    placements = [
        (
            (index - (r.aux_well_count - 1) / 2.0) * r.aux_tray_pitch_m,
            -(0.0032 + r.aux_tray_depth_m / 2.0),
            well_z,
        )
        for index in range(r.aux_well_count)
    ]
    _emit_aux_wells(tray, r, mats, "second_hinged_tray", placements)
    aux_face_x = r.aux_knuckle_x_m - r.aux_knuckle_len_m / 2.0
    aux_collar = _thrust_collar(r.aux_knuckle_r_m, r.aux_bore_r_m, r.collar_len_m)
    for index, sign in enumerate((-1.0, 1.0)):
        tray.visual(
            mesh_from_cadquery(
                aux_collar.translate(
                    (
                        sign * (aux_face_x - r.collar_len_m / 2.0 + r.knuckle_axial_fit_m),
                        0.0,
                        0.0,
                    )
                ),
                f"makeup1_front_tray_collar_{index}",
                tolerance=0.00010,
            ),
            material=mats["metal"],
            name=f"opening__second_hinged_tray__thrust_collar_{index}", material_class_id="metal.stainless_matte",
        )
    return (
        tray,
        "front_tray_hinge",
        (0.0, r.aux_hinge_y_m, r.aux_hinge_z_m),
        (-1.0, 0.0, 0.0),
    )


def _fan_tray_solid(r: ResolvedConfig) -> cq.Workplane:
    top = r.seat_interference_m
    tray = _sector_prism(
        r.fan_tray_inner_r_m,
        r.fan_tray_outer_r_m,
        r.fan_half_rad,
        top - r.fan_tray_t_m,
        r.fan_tray_t_m,
    )
    hub = (
        cq.Workplane("XY")
        .workplane(offset=top - r.fan_tray_t_m)
        .circle(r.fan_tray_inner_r_m + 0.0030)
        .extrude(r.fan_tray_t_m)
    )
    tray = tray.union(hub)
    tray = tray.cut(
        cq.Workplane("XY")
        .workplane(offset=top - r.fan_tray_t_m - 0.001)
        .circle(r.aux_bore_r_m)
        .extrude(r.fan_tray_t_m + 0.002)
    )
    tray = tray.cut(
        _sector_prism(
            r.fan_tray_inner_r_m + 0.0045,
            r.fan_tray_outer_r_m - 0.0025,
            r.fan_half_rad * 0.86,
            top - r.aux_cavity_depth_m,
            r.aux_cavity_depth_m + 0.001,
        )
    )
    return tray


def _opening_fan_out_tray_build(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> tuple[object | None, str, tuple[float, float, float] | None, tuple[float, float, float]]:
    case.visual(
        Cylinder(radius=r.pivot_post_r_m, length=r.post_h_m),
        origin=Origin(xyz=(0.0, r.fan_pivot_y_m, -r.post_h_m / 2.0 + 0.0009)),
        material=mats["metal"],
        name="opening__fan_out_tray__pivot_post", material_class_id="metal.stainless_matte",
    )
    case.visual(
        Box((min(0.020, 0.20 * r.case_plan_w_m), 0.0060, 0.0014)),
        origin=Origin(xyz=(0.0, r.fan_pivot_y_m, 0.0016)),
        material=mats["deck"],
        name="opening__fan_out_tray__pivot_boss", material_class_id="plastic.opaque_glossy_molded",
    )

    tray = model.part(
        "fan_tray",
        meta={
            "role": "fan_tray",
            "slot": "opening",
            "candidate": "fan_out_tray",
            "vertical_pivot": True,
            "aux_well_count": r.aux_well_count,
        },
    )
    tray.visual(
        mesh_from_cadquery(_fan_tray_solid(r), "makeup1_fan_tray_shell", tolerance=0.00030),
        material=mats["shell"],
        name="opening__fan_out_tray__tray_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    ring_r = 0.66 * r.fan_tray_outer_r_m
    well_z = r.seat_interference_m - r.aux_cavity_depth_m
    span = 2.0 * r.fan_half_rad * 0.72
    placements = []
    for index in range(r.aux_well_count):
        fraction = (index + 0.5) / float(r.aux_well_count) - 0.5
        angle = fraction * span
        placements.append((ring_r * math.sin(angle), -ring_r * math.cos(angle), well_z))
    _emit_aux_wells(tray, r, mats, "fan_out_tray", placements)
    return (
        tray,
        "fan_tray_pivot",
        (0.0, r.fan_pivot_y_m, 0.0),
        (0.0, 0.0, 1.0),
    )


_CASE_BUILDERS = {
    "rounded_rectangle": _case_form_rounded_rectangle_build,
    "elongated_rectangle": _case_form_elongated_rectangle_build,
    "round_puck": _case_form_round_puck_build,
}
_WELL_BUILDERS = {
    "orthogonal_grid": _well_pattern_orthogonal_grid_build,
    "radial_ring": _well_pattern_radial_ring_build,
    "fan_sector": _well_pattern_fan_sector_build,
}
_CLOSURE_BUILDERS = {
    "rear_hinge": _closure_rear_hinge_build,
    "push_latch": _closure_push_latch_build,
    "sliding_latch": _closure_sliding_latch_build,
}
_OPENING_BUILDERS = {
    "single_lid": _opening_single_lid_build,
    "second_hinged_tray": _opening_second_hinged_tray_build,
    "fan_out_tray": _opening_fan_out_tray_build,
}


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


def _axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent: object,
    child: object,
    provider_name: str,
    consumer_name: str,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    radial: tuple[float, float, float],
    provider_radius: float,
    consumer_radius: float,
    articulation_type: ArticulationType,
    limits: MotionLimits,
) -> None:
    mate = mate_axes(
        AxisInterface(
            name=provider_name,
            point=point,
            axis=axis,
            radial=radial,
            radius=provider_radius,
        ),
        AxisInterface(
            name=consumer_name,
            axis=axis,
            radial=radial,
            radius=consumer_radius,
        ),
    )
    model.articulation(
        name,
        articulation_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
    )
    register_interface_mate(model, name, mate)


def _solve_lid_seat(r: ResolvedConfig) -> float:
    """Solve the closed-cover seat against the real rim footprint."""

    provider = PlaneInterface(
        name="case_form.lid_seat",
        point=(0.0, 0.0, r.rim_top_z_m),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.case_plan_w_m, r.case_plan_d_m),
    )
    consumer = PlaneInterface(
        name="closure.lid_seat",
        point=(0.0, 0.0, 0.0),
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.case_plan_w_m - 0.0004, r.case_plan_d_m - 0.0004),
    )
    mate = mate_planes(provider, consumer, gap=-r.seat_interference_m)
    return float(mate.origin.xyz[2])


def build_makeup1(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config if config is not None else Config())
    seat_z = _solve_lid_seat(r)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "makeup1",
            "slot_choices": (
                ("case_form", r.case_form),
                ("well_pattern", r.well_pattern),
                ("closure", r.closure),
                ("opening", r.opening),
                ("well_count", r.well_count),
            ),
            "source_identity": (
                "moulded cosmetic compact: recessed pressed-pan deck, hinged mirror "
                "cover, front closure hardware and optional auxiliary trays"
            ),
            "derived_clearances": {
                "cavity_depth_m": r.cavity_depth_m,
                "cake_top_clearance_m": r.cake_top_clearance_m,
                "barrel_bore_r_m": r.barrel_bore_r_m,
                "hinge_pin_r_m": r.hinge_pin_r_m,
                "lid_seat_z_m": seat_z,
            },
        },
    )
    mats = _materials(model, r)
    case = model.part(
        "case",
        meta={
            "role": "case",
            "recessed_well_deck": True,
            "well_count": r.well_count,
            "case_plan_w_m": r.case_plan_w_m,
            "case_plan_d_m": r.case_plan_d_m,
        },
    )
    _CASE_BUILDERS[r.case_form](model, case, r, mats)
    _WELL_BUILDERS[r.well_pattern](model, case, r, mats)
    lid = _new_lid(model, r, mats)
    latch, latch_joint, latch_point = _CLOSURE_BUILDERS[r.closure](model, case, lid, r, mats)
    tray, tray_joint, tray_point, tray_axis = _OPENING_BUILDERS[r.opening](model, case, r, mats)

    _axis_joint(
        model,
        name="lid_hinge",
        parent=case,
        child=lid,
        provider_name="case_form.hinge_axis",
        consumer_name="closure.lid_hinge_axis",
        point=(0.0, r.hinge_y_m, r.hinge_z_m),
        axis=(-1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        provider_radius=r.hinge_pin_r_m,
        consumer_radius=r.barrel_bore_r_m,
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=1.4, velocity=2.2, lower=0.0, upper=r.lid_open_rad),
    )

    if latch is not None and r.closure == "push_latch":
        _axis_joint(
            model,
            name=latch_joint,
            parent=case,
            child=latch,
            provider_name="case_form.latch_pocket",
            consumer_name="closure.latch_pivot_axis",
            point=latch_point or (0.0, 0.0, 0.0),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            provider_radius=r.pivot_stub_r_m,
            consumer_radius=r.rocker_bore_r_m,
            articulation_type=ArticulationType.REVOLUTE,
            limits=MotionLimits(effort=3.0, velocity=1.5, lower=0.0, upper=r.latch_press_rad),
        )
    elif latch is not None:
        model.articulation(
            latch_joint,
            ArticulationType.PRISMATIC,
            parent=case,
            child=latch,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=3.0, velocity=0.05, lower=0.0, upper=r.latch_travel_m
            ),
            meta={"mechanism": "front_sliding_latch_in_guided_slot"},
        )

    if tray is not None and r.opening == "second_hinged_tray":
        _axis_joint(
            model,
            name=tray_joint,
            parent=case,
            child=tray,
            provider_name="case_form.aux_mount",
            consumer_name="opening.aux_mount",
            point=tray_point or (0.0, 0.0, 0.0),
            axis=tray_axis,
            radial=(0.0, 0.0, 1.0),
            provider_radius=r.aux_pin_r_m,
            consumer_radius=r.aux_bore_r_m,
            articulation_type=ArticulationType.REVOLUTE,
            limits=MotionLimits(effort=0.8, velocity=2.0, lower=0.0, upper=r.aux_open_rad),
        )
    elif tray is not None:
        _axis_joint(
            model,
            name=tray_joint,
            parent=case,
            child=tray,
            provider_name="case_form.aux_mount",
            consumer_name="opening.aux_mount",
            point=tray_point or (0.0, 0.0, 0.0),
            axis=tray_axis,
            radial=(0.0, 1.0, 0.0),
            provider_radius=r.pivot_post_r_m,
            consumer_radius=r.aux_bore_r_m,
            articulation_type=ArticulationType.REVOLUTE,
            limits=MotionLimits(effort=0.8, velocity=2.0, lower=0.0, upper=r.fan_sweep_rad),
        )
    return model


# ---------------------------------------------------------------------------
# author tests
# ---------------------------------------------------------------------------


def _parts_by_role(model: ArticulatedObject, role: str) -> list[object]:
    return [part for part in model.parts if part.meta.get("role") == role]


def run_makeup1_tests(model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    cases = _parts_by_role(model, "case")
    lids = _parts_by_role(model, "lid")
    latches = _parts_by_role(model, "latch")
    front_trays = _parts_by_role(model, "front_tray")
    fan_trays = _parts_by_role(model, "fan_tray")
    case = cases[0] if cases else None
    lid = lids[0] if lids else None
    hinge = model.get_articulation("lid_hinge")

    expected_parts = 2 + (0 if r.closure == "rear_hinge" else 1)
    expected_parts += 0 if r.opening == "single_lid" else 1
    expected_joints = expected_parts - 1
    ctx.check(
        "category_anchor: makeup compact identity",
        len(cases) == 1
        and len(lids) == 1
        and case is not None
        and lid is not None
        and len(model.parts) == expected_parts
        and len(model.articulations) == expected_joints
        and case.meta.get("recessed_well_deck") is True
        and model.root_parts() == [case]
        and hinge is not None
        and hinge.articulation_type == ArticulationType.REVOLUTE
        and hinge.parent == "case"
        and hinge.child == "lid"
        and tuple(round(float(value), 6) for value in hinge.axis) == (-1.0, 0.0, 0.0),
        details=(
            f"parts={[part.name for part in model.parts]}, "
            f"joints={[joint.name for joint in model.articulations]}, "
            f"expected_parts={expected_parts}"
        ),
    )

    cup_names = [f"well_pattern__{r.well_pattern}__cup_{i}" for i in range(r.well_count)]
    cake_names = [f"well_pattern__{r.well_pattern}__cake_{i}" for i in range(r.well_count)]
    cups_present = case is not None and all(case.get_visual(name) is not None for name in cup_names)
    cakes_present = case is not None and all(
        case.get_visual(name) is not None for name in cake_names
    )
    ctx.check(
        "category_anchor: pressed pan field is a real cup and cake sub-assembly",
        cups_present
        and cakes_present
        and r.cavity_depth_m > r.pan_depth_m
        and r.well_floor_z_m >= r.floor_t_m
        and r.cake_top_z_m < r.rim_top_z_m - 0.0008
        and r.pan_across_m > 2.5 * r.cup_wall_t_m,
        details=(
            f"pattern={r.well_pattern}, N={r.well_count}, "
            f"cavity_depth={r.cavity_depth_m:.5f}, well_floor={r.well_floor_z_m:.5f}, "
            f"cake_top={r.cake_top_z_m:.5f}, rim={r.rim_top_z_m:.5f}, "
            f"pan_across={r.pan_across_m:.5f}"
        ),
    )

    case_aabb = ctx.part_world_aabb(case) if case is not None else None
    lid_aabb = ctx.part_world_aabb(lid) if lid is not None else None
    covers_footprint = (
        case_aabb is not None
        and lid_aabb is not None
        and lid_aabb[1][0] - lid_aabb[0][0] >= 0.95 * r.case_plan_w_m
        and lid_aabb[0][2] <= r.rim_top_z_m + 1e-4
        and lid_aabb[1][2] <= r.rim_top_z_m + r.lid_t_m + 1e-3
    )
    ctx.check(
        "category_anchor: hinged cover closes onto the case rim",
        covers_footprint
        and r.cake_top_clearance_m >= 0.0008
        and r.skirt_bottom_z_m < r.rim_top_z_m
        and r.skirt_bottom_z_m > 0.35 * r.rim_top_z_m
        and r.barrel_bore_r_m - r.hinge_pin_r_m >= 0.00035
        and r.barrel_len_m > 2.0 * r.barrel_outer_r_m
        and hinge is not None
        and hinge.motion_limits is not None
        and abs(hinge.motion_limits.lower) < 1e-9
        and abs(hinge.motion_limits.upper - r.lid_open_rad) < 1e-9,
        details=(
            f"case_aabb={case_aabb}, lid_aabb={lid_aabb}, "
            f"cake_clearance={r.cake_top_clearance_m:.5f}, "
            f"pin_clearance={r.barrel_bore_r_m - r.hinge_pin_r_m:.5f}"
        ),
    )

    latch = latches[0] if latches else None
    if r.closure == "rear_hinge":
        closure_ok = (
            not latches
            and case is not None
            and case.get_visual("closure__rear_hinge__catch_lip") is not None
            and lid is not None
            and lid.get_visual("closure__rear_hinge__lid_thumb_tab") is not None
            and r.pocket_w_m > r.thumb_catch_width_m
            and r.pocket_h_m >= 0.0030
        )
        closure_details = f"pocket=({r.pocket_w_m:.5f}, {r.pocket_h_m:.5f})"
    elif r.closure == "push_latch":
        press = model.get_articulation("latch_press")
        closure_ok = (
            latch is not None
            and press is not None
            and press.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(float(value), 6) for value in press.axis) == (1.0, 0.0, 0.0)
            and press.motion_limits is not None
            and abs(press.motion_limits.upper - r.latch_press_rad) < 1e-9
            and r.rocker_bore_r_m - r.pivot_stub_r_m >= 0.00035
            and case is not None
            and case.get_visual("closure__push_latch__pivot_stub_0") is not None
            and case.get_visual("closure__push_latch__pivot_stub_1") is not None
            and lid is not None
            and lid.get_visual("closure__push_latch__lid_strike") is not None
            and r.hook_swing_m >= 0.0004
            and r.pocket_w_m > r.rocker_w_m
        )
        closure_details = (
            f"press={press}, bore_clearance="
            f"{r.rocker_bore_r_m - r.pivot_stub_r_m:.5f}, swing={r.hook_swing_m:.5f}"
        )
    else:
        slide = model.get_articulation("latch_slide")
        closure_ok = (
            latch is not None
            and slide is not None
            and slide.articulation_type == ArticulationType.PRISMATIC
            and tuple(round(float(value), 6) for value in slide.axis) == (1.0, 0.0, 0.0)
            and slide.motion_limits is not None
            and abs(slide.motion_limits.lower) < 1e-9
            and abs(slide.motion_limits.upper - r.latch_travel_m) < 1e-9
            and r.guide_slot_len_m > r.rail_len_m + r.latch_travel_m
            and case is not None
            and case.get_visual("closure__sliding_latch__guide_rib_0") is not None
            and lid is not None
            and lid.get_visual("closure__sliding_latch__lid_catch_lip") is not None
            and r.latch_travel_m > r.lid_lip_w_m / 2.0 + 0.0010
        )
        closure_details = (
            f"slide={slide}, slot={r.guide_slot_len_m:.5f}, "
            f"rail={r.rail_len_m:.5f}, travel={r.latch_travel_m:.5f}"
        )
    ctx.check(
        "category_anchor: closure hardware is captured with real clearance",
        closure_ok,
        details=f"closure={r.closure}, {closure_details}",
    )

    if r.opening == "single_lid":
        ctx.check(
            "category_anchor: single-lid opening has one moving cover",
            not front_trays
            and not fan_trays
            and case is not None
            and case.get_visual("opening__single_lid__solid_front_boss") is not None
            and len([j for j in model.articulations if j.child == "lid"]) == 1,
            details=f"joints={[joint.name for joint in model.articulations]}",
        )
    elif r.opening == "second_hinged_tray":
        tray = front_trays[0] if front_trays else None
        tray_hinge = model.get_articulation("front_tray_hinge")
        aux_cups = [f"opening__second_hinged_tray__aux_cup_{i}" for i in range(r.aux_well_count)]
        aux_cakes = [f"opening__second_hinged_tray__aux_cake_{i}" for i in range(r.aux_well_count)]
        tray_aabb = ctx.part_world_aabb(tray) if tray is not None else None
        ahead_of_cover = (
            tray_aabb is not None
            and lid_aabb is not None
            and tray_aabb[1][1] < lid_aabb[0][1] - 0.0015
        )
        upright_aabb = None
        if tray is not None and tray_hinge is not None:
            with ctx.pose({tray_hinge: r.aux_open_rad}):
                upright_aabb = ctx.part_world_aabb(tray)
        upright_ok = (
            upright_aabb is not None
            and lid_aabb is not None
            and tray_aabb is not None
            and upright_aabb[1][1] < lid_aabb[0][1] - 0.0010
            and upright_aabb[1][2] > tray_aabb[1][2] + 0.010
        )
        ctx.check(
            "category_anchor: front hinged tray is a real welled tray on its own hinge",
            tray is not None
            and tray_hinge is not None
            and tray_hinge.articulation_type == ArticulationType.REVOLUTE
            and tray_hinge.parent == "case"
            and tuple(round(float(value), 6) for value in tray_hinge.axis) == (-1.0, 0.0, 0.0)
            and all(tray.get_visual(name) is not None for name in aux_cups)
            and all(tray.get_visual(name) is not None for name in aux_cakes)
            and r.aux_bore_r_m - r.aux_pin_r_m >= 0.00035
            and ahead_of_cover
            and upright_ok,
            details=(
                f"tray_aabb={tray_aabb}, upright_aabb={upright_aabb}, "
                f"lid_aabb={lid_aabb}, aux_wells={r.aux_well_count}"
            ),
        )
    else:
        tray = fan_trays[0] if fan_trays else None
        pivot = model.get_articulation("fan_tray_pivot")
        aux_cups = [f"opening__fan_out_tray__aux_cup_{i}" for i in range(r.aux_well_count)]
        stowed = ctx.part_world_aabb(tray) if tray is not None else None
        swung = None
        if tray is not None and pivot is not None:
            with ctx.pose({pivot: r.fan_sweep_rad}):
                swung = ctx.part_world_aabb(tray)
        swings_clear = (
            stowed is not None
            and swung is not None
            and stowed[1][2] <= 1e-4
            and swung[1][2] <= 1e-4
            and max(abs(swung[0][0] - stowed[0][0]), abs(swung[1][0] - stowed[1][0])) > 0.010
        )
        ctx.check(
            "category_anchor: fan-out tray swings on a real vertical pivot",
            tray is not None
            and pivot is not None
            and pivot.articulation_type == ArticulationType.REVOLUTE
            and pivot.parent == "case"
            and tuple(round(float(value), 6) for value in pivot.axis) == (0.0, 0.0, 1.0)
            and all(tray.get_visual(name) is not None for name in aux_cups)
            and case is not None
            and case.get_visual("opening__fan_out_tray__pivot_post") is not None
            and r.aux_bore_r_m - r.pivot_post_r_m >= 0.00035
            and swings_clear,
            details=(
                f"stowed={stowed}, swung={swung}, "
                f"bore_clearance={r.aux_bore_r_m - r.pivot_post_r_m:.5f}"
            ),
        )

    placements = _well_placements(r)
    if r.well_pattern == "fan_sector":
        inside_field = r.fan_outer_r_m <= r.well_field_d_m + 1e-6
    else:
        inside_field = all(
            abs(x) + r.pan_across_m / 2.0 <= r.well_field_w_m / 2.0 + 1e-6
            and abs(y) + r.pan_across_m / 2.0 <= r.well_field_d_m / 2.0 + 1e-6
            for x, y, _yaw in placements
        )
    ctx.check(
        "every well stays inside the derived well field",
        len(placements) == r.well_count and inside_field and r.well_field_d_m > 0.008,
        details=(
            f"field=({r.well_field_w_m:.5f}, {r.well_field_d_m:.5f}), "
            f"pan_across={r.pan_across_m:.5f}, placements={len(placements)}"
        ),
    )

    open_aabb = None
    if lid is not None and hinge is not None:
        with ctx.pose({hinge: r.lid_open_rad}):
            open_aabb = ctx.part_world_aabb(lid)
    ctx.check(
        "cover hinge lifts the cover clear of the well deck",
        open_aabb is not None
        and lid_aabb is not None
        and open_aabb[1][2] > lid_aabb[1][2] + 0.5 * r.case_plan_d_m,
        details=f"closed={lid_aabb}, open={open_aabb}",
    )

    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "puck_twelve_fan_push_latch_front_tray",
        {
            "case_form": "round_puck",
            "well_pattern": "fan_sector",
            "closure": "push_latch",
            "opening": "second_hinged_tray",
            "well_count": 12,
            "case_width_m": 0.150,
            "case_depth_m": 0.115,
            "case_height_m": 0.024,
            "puck_flat_ratio": 0.12,
            "lid_open_rad": 2.15,
            "latch_press_rad": 0.35,
            "pan_fill_ratio": 0.90,
            "pan_depth_m": 0.0070,
            "aux_tray_depth_m": 0.052,
            "aux_open_rad": 1.60,
        },
        reason="largest puck with the deepest wells, the widest fan and both extra mechanisms",
    ),
    corner_case(
        "smallest_puck_twelve_radial_sliding_latch",
        {
            "case_form": "round_puck",
            "well_pattern": "radial_ring",
            "closure": "sliding_latch",
            "opening": "fan_out_tray",
            "well_count": 12,
            "case_width_m": 0.085,
            "case_depth_m": 0.060,
            "case_height_m": 0.013,
            "puck_flat_ratio": 0.04,
            "lid_open_rad": 1.75,
            "latch_travel_m": 0.0030,
            "pan_fill_ratio": 0.90,
            "pan_depth_m": 0.0070,
            "fan_sweep_rad": 2.05,
            "fan_radius_ratio": 1.20,
        },
        reason="tightest host with the maximum well count and the widest fan-out sweep",
    ),
    corner_case(
        "elongated_twelve_grid_push_latch",
        {
            "case_form": "elongated_rectangle",
            "well_pattern": "orthogonal_grid",
            "closure": "push_latch",
            "opening": "second_hinged_tray",
            "well_count": 12,
            "case_width_m": 0.150,
            "case_depth_m": 0.115,
            "case_height_m": 0.013,
            "lid_open_rad": 2.15,
            "latch_press_rad": 0.14,
            "pan_fill_ratio": 0.60,
            "pan_depth_m": 0.0035,
            "aux_tray_depth_m": 0.028,
            "aux_open_rad": 1.35,
        },
        reason="shallowest elongated deck hosting a 4x3 grid plus the front fold-out tray",
    ),
    corner_case(
        "elongated_four_fan_sliding_latch",
        {
            "case_form": "elongated_rectangle",
            "well_pattern": "fan_sector",
            "closure": "sliding_latch",
            "opening": "fan_out_tray",
            "well_count": 4,
            "case_width_m": 0.085,
            "case_depth_m": 0.115,
            "case_height_m": 0.020,
            "lid_open_rad": 1.90,
            "latch_travel_m": 0.0065,
            "pan_fill_ratio": 0.60,
            "pan_depth_m": 0.0050,
            "fan_sweep_rad": 1.30,
            "fan_radius_ratio": 0.90,
        },
        reason="minimum well count with the widest fan wedges on a shallow elongated host",
    ),
    corner_case(
        "rounded_ten_radial_rear_hinge_wide_catch",
        {
            "case_form": "rounded_rectangle",
            "well_pattern": "radial_ring",
            "closure": "rear_hinge",
            "opening": "single_lid",
            "well_count": 10,
            "case_width_m": 0.150,
            "case_depth_m": 0.115,
            "case_height_m": 0.013,
            "lid_open_rad": 2.15,
            "thumb_catch_width_m": 0.036,
            "pan_fill_ratio": 0.90,
            "pan_depth_m": 0.0070,
        },
        reason="thinnest body with the widest thumb catch and the deepest radial wells",
    ),
    corner_case(
        "rounded_four_grid_rear_hinge_narrow_catch",
        {
            "case_form": "rounded_rectangle",
            "well_pattern": "orthogonal_grid",
            "closure": "rear_hinge",
            "opening": "fan_out_tray",
            "well_count": 4,
            "case_width_m": 0.085,
            "case_depth_m": 0.060,
            "case_height_m": 0.024,
            "lid_open_rad": 1.75,
            "thumb_catch_width_m": 0.016,
            "pan_fill_ratio": 0.60,
            "pan_depth_m": 0.0035,
            "fan_sweep_rad": 1.30,
            "fan_radius_ratio": 0.90,
        },
        reason="smallest deepest body with the narrowest catch and the shallowest wells",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_makeup1",
    "config_from_seed",
    "grid_shape",
    "min_neighbour_gap",
    "resolve_config",
    "run_makeup1_tests",
]
