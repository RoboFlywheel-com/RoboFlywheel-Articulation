# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Design-backed procedural template for category `serial_elbow_arm`.

Slots, candidates and evidence live in
`articraft_template_authoring/designs/serial_elbow_arm.json`, which is backed by
`articraft_template_authoring/source_maps/serial_elbow_arm.md` (38 reviewed
five-star records).

The joint topology is owned by `axis_family`; every other slot adapts to it.
Joint limits are *solved* from the mount envelope and the link lengths - the
deleted legacy template hardcoded three limit tuples and therefore swung the
upper link straight into its own base on every seed.
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    ExtrudeWithHolesGeometry,
    Inertial,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_geometry,
    register_interface_mate,
)

AxisFamily = Literal["pitch_clevis", "yaw_clevis", "yaw_stacked"]
Mount = Literal[
    "floor_pedestal_box",
    "floor_pedestal_round",
    "bench_clamp_plate",
    "wall_side_plate",
    "ceiling_underslung",
    "gantry_backbone",
    "open_frame_mast",
    "cast_housing_block",
]
BearingDetail = Literal[
    "plain_hub", "ring_and_cover", "outboard_boss_cap", "through_pin_span", "capped_seal_stack"
]
UpperLinkBody = Literal[
    "box_beam",
    "windowed_twin_plate",
    "box_section_tube",
    "dual_parallel_bars",
    "twin_rail_span",
    "i_beam_ribbed",
]
ForearmBody = Literal[
    "box_beam", "capsule_slotted_plate", "hollow_rect_tube", "twin_rail_span", "dogleg_plate_pair"
]
EndEffector = Literal[
    "bolted_round_flange",
    "square_tool_plate",
    "rubber_pad_face",
    "suction_cup",
    "clamped_tool_socket",
    "adapter_and_face",
    "bare_nose_tip",
]
TerminalBody = Literal["merged_into_forearm", "separate_fixed_part"]
PaletteStyle = Literal["industrial_gray", "painted_white", "safety_orange", "blue_anodised"]

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("axis_family", ("pitch_clevis", "yaw_clevis", "yaw_stacked")),
        component_slot(
            "mount",
            (
                "floor_pedestal_box",
                "floor_pedestal_round",
                "bench_clamp_plate",
                "wall_side_plate",
                "ceiling_underslung",
                "gantry_backbone",
                "open_frame_mast",
                "cast_housing_block",
            ),
        ),
        component_slot(
            "bearing_detail",
            (
                "plain_hub",
                "ring_and_cover",
                "outboard_boss_cap",
                "through_pin_span",
                "capped_seal_stack",
            ),
        ),
        component_slot(
            "upper_link_body",
            (
                "box_beam",
                "windowed_twin_plate",
                "box_section_tube",
                "dual_parallel_bars",
                "twin_rail_span",
                "i_beam_ribbed",
            ),
        ),
        component_slot(
            "forearm_body",
            (
                "box_beam",
                "capsule_slotted_plate",
                "hollow_rect_tube",
                "twin_rail_span",
                "dogleg_plate_pair",
            ),
        ),
        component_slot(
            "end_effector",
            (
                "bolted_round_flange",
                "square_tool_plate",
                "rubber_pad_face",
                "suction_cup",
                "clamped_tool_socket",
                "adapter_and_face",
                "bare_nose_tip",
            ),
        ),
        component_slot("terminal_body", ("merged_into_forearm", "separate_fixed_part")),
    )
)

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "industrial_gray": {
        "base": (0.45, 0.47, 0.49, 1.0),
        "link": (0.60, 0.62, 0.63, 1.0),
        "cover": (0.22, 0.23, 0.24, 1.0),
        "bolt": (0.10, 0.10, 0.11, 1.0),
        "soft": (0.05, 0.05, 0.05, 1.0),
    },
    "painted_white": {
        "base": (0.78, 0.76, 0.70, 1.0),
        "link": (0.86, 0.84, 0.78, 1.0),
        "cover": (0.30, 0.31, 0.32, 1.0),
        "bolt": (0.10, 0.10, 0.10, 1.0),
        "soft": (0.08, 0.08, 0.09, 1.0),
    },
    "safety_orange": {
        "base": (0.22, 0.24, 0.25, 1.0),
        "link": (0.90, 0.40, 0.12, 1.0),
        "cover": (0.12, 0.13, 0.14, 1.0),
        "bolt": (0.05, 0.05, 0.05, 1.0),
        "soft": (0.02, 0.02, 0.02, 1.0),
    },
    "blue_anodised": {
        "base": (0.16, 0.18, 0.20, 1.0),
        "link": (0.10, 0.28, 0.52, 1.0),
        "cover": (0.62, 0.64, 0.66, 1.0),
        "bolt": (0.06, 0.06, 0.07, 1.0),
        "soft": (0.03, 0.03, 0.03, 1.0),
    },
}

HALF_PI = math.pi / 2.0
# Straddle clearance per side. Kept at or below the 1 mm part-to-part support
# band so a hub in a clevis still reads as carried, never as floating.
BEARING_CLEARANCE = 0.0008
# Extra standoff used when solving joint limits against the mount envelope.
SWING_MARGIN = 0.020
# Fixed kink of the dogleg forearm candidate, taken from the source record.
DOGLEG_ANGLE = 0.26




@dataclass(frozen=True)
class Config:
    axis_family: AxisFamily = "pitch_clevis"
    mount: Mount = "floor_pedestal_box"
    bearing_detail: BearingDetail = "plain_hub"
    upper_link_body: UpperLinkBody = "box_beam"
    forearm_body: ForearmBody = "box_beam"
    end_effector: EndEffector = "bolted_round_flange"
    terminal_body: TerminalBody = "merged_into_forearm"
    total_reach_m: float = 0.62
    link_ratio: float = 0.54
    mount_height_m: float = 0.30
    section_scale: float = 1.0
    palette_style: PaletteStyle = "industrial_gray"
    name: str = "serial_elbow_arm"

# ---------------------------------------------------------------------------
# Axis-relative frame
#
# Every link is authored in (x, a, p):
#   x  along the link, from its own joint origin toward the next joint
#   a  along the joint axis        (pitch_clevis -> world Y, yaw_* -> world Z)
#   p  perpendicular to both       (pitch_clevis -> world Z, yaw_* -> world Y)
#
# This is the whole point of the ledger: a rib, a pair of bars or a pair of
# rails always spreads along `p`, never along `a`. Anything that spread along
# `a` would stick out of the clevis gap the hub has to live in.
# ---------------------------------------------------------------------------


def _is_pitch(r: "ResolvedConfig") -> bool:
    return r.axis_family == "pitch_clevis"


def _v(r: "ResolvedConfig", x: float, a: float, p: float) -> tuple[float, float, float]:
    """(x, along-axis, perpendicular) -> local xyz."""

    return (x, a, p) if _is_pitch(r) else (x, p, a)


def _sz(r: "ResolvedConfig", lx: float, la: float, lp: float) -> tuple[float, float, float]:
    """(length, along-axis, perpendicular) -> Box size."""

    return (lx, la, lp) if _is_pitch(r) else (lx, lp, la)


@dataclass(frozen=True)
class ResolvedConfig:
    axis_family: AxisFamily
    mount: Mount
    bearing_detail: BearingDetail
    upper_link_body: UpperLinkBody
    forearm_body: ForearmBody
    end_effector: EndEffector
    terminal_body: TerminalBody
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    name: str
    # link lengths
    total_reach: float
    upper_len: float
    forearm_len: float
    tool_len: float
    upper_body_x1: float
    fore_body_x0: float
    # sections, expressed in the axis-relative frame
    sec_a: float
    sec_p: float
    fsec_a: float
    fsec_p: float
    # the one clearance ledger: seats, gaps and keep-outs
    hub_r: float
    hub_half: float
    fore_hub_r: float
    fore_hub_half: float
    cheek_t: float
    disc_t: float
    riser_h: float
    stack_dir: float
    body_a: float
    fore_body_a: float
    drop_p: float
    fore_drop_p: float
    seat_span_z: float
    # mount frame
    mount_top_z: float
    mount_axis_x: float
    mount_envelope_half_x: float
    mount_envelope_half_y: float
    mount_deck_z: float
    mount_ceiling_z: float
    hangs_below: bool
    # solved joint limits
    shoulder_lower: float
    shoulder_upper: float
    elbow_lower: float
    elbow_upper: float
    # end effector
    ee_face_y: float
    ee_face_z: float
    ee_len: float
    wrist_y: float
    wrist_z: float


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x5345_5249_414C_4152)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        axis_family=choices["axis_family"],
        mount=choices["mount"],
        bearing_detail=choices["bearing_detail"],
        upper_link_body=choices["upper_link_body"],
        forearm_body=choices["forearm_body"],
        end_effector=choices["end_effector"],
        terminal_body=choices["terminal_body"],
        total_reach_m=round(rng.uniform(0.42, 1.05), 4),
        link_ratio=round(rng.uniform(0.46, 0.60), 4),
        mount_height_m=round(rng.uniform(0.16, 0.52), 4),
        section_scale=round(rng.uniform(0.85, 1.20), 4),
        palette_style=rng.choice(tuple(PALETTES)),
        name=f"serial_elbow_arm_seed_{int(seed)}",
    )


def _mount_hangs(mount: Mount) -> bool:
    return mount == "ceiling_underslung"


def _mount_frame(mount: Mount, mount_height: float, reach: float) -> tuple[float, float, float, float, bool]:
    """(mount_top_z, axis_x, envelope_half_x, envelope_half_y, hangs_below)."""

    foot = max(0.16, reach * 0.34)
    if mount in ("floor_pedestal_box", "floor_pedestal_round", "bench_clamp_plate"):
        return mount_height, 0.0, max(0.055, reach * 0.10), foot * 0.5, False
    if mount == "wall_side_plate":
        return mount_height, max(0.070, reach * 0.13), max(0.070, reach * 0.13), foot * 0.5, False
    if mount == "ceiling_underslung":
        return mount_height, 0.0, max(0.075, reach * 0.13), foot * 0.5, True
    if mount == "gantry_backbone":
        return mount_height, max(0.060, reach * 0.11), max(0.090, reach * 0.16), foot * 0.5, False
    if mount == "open_frame_mast":
        return mount_height, max(0.045, reach * 0.075), max(0.075, reach * 0.13), foot * 0.5, False
    return mount_height, 0.0, max(0.085, reach * 0.15), foot * 0.6, False


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "axis_family": config.axis_family,
            "mount": config.mount,
            "bearing_detail": config.bearing_detail,
            "upper_link_body": config.upper_link_body,
            "forearm_body": config.forearm_body,
            "end_effector": config.end_effector,
            "terminal_body": config.terminal_body,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")

    reach = _clamp(config.total_reach_m, 0.42, 1.05)
    ratio = _clamp(config.link_ratio, 0.46, 0.60)
    scale = _clamp(config.section_scale, 0.85, 1.20)
    mount_height = _clamp(config.mount_height_m, 0.16, 0.52)
    stacked = config.axis_family == "yaw_stacked"

    tool_len = max(0.045, reach * 0.11)
    upper_len = (reach - tool_len) * ratio
    forearm_len = (reach - tool_len) - upper_len

    # Sections live in the axis-relative frame from the start.
    sec_a = max(0.044, reach * 0.088) * scale
    sec_p = max(0.040, reach * 0.082) * scale
    fsec_a = sec_a * 0.80
    fsec_p = sec_p * 0.80

    cheek_t = max(0.007, sec_a * 0.16)
    disc_t = max(0.010, sec_a * 0.40)

    # --- the ledger -------------------------------------------------------
    # The hub spans the full body width along the axis, so the clevis gap it
    # needs is exactly the body it carries. `hub_half` is the single number the
    # seat, the cheeks, the keep-out and the mount deck are all derived from.
    hub_r = max(0.014, sec_p * 0.42)
    hub_half = max(sec_a, sec_p * 0.52) / 2.0
    fore_hub_r = max(0.012, fsec_p * 0.42)
    fore_hub_half = max(fsec_a, fsec_p * 0.52) / 2.0

    # How far the body reaches perpendicular to the axis, below the centreline.
    # Bounds every rib / flange / rail a body candidate may add.
    drop_p = sec_p * 0.80
    fore_drop_p = fsec_p * 0.80

    # Both link bodies stand off their shared elbow so the fold has somewhere to
    # close into. The upper side also has to clear the forearm hub itself.
    fore_body_x0 = max(fore_hub_r * 1.25, fsec_p * 0.55)
    upper_body_x1 = upper_len - max(fore_hub_r + 4.0 * BEARING_CLEARANCE, fore_body_x0)

    # How much lower than the joint line the forearm tip ends up.
    if config.forearm_body == "dogleg_plate_pair":
        dogleg_stub = max(fore_body_x0, fore_hub_r * 1.7, forearm_len * 0.18)
        tip_drop = (forearm_len - dogleg_stub) * math.sin(DOGLEG_ANGLE)
    else:
        tip_drop = 0.0

    riser_h = max(0.018, sec_p * 0.45) if stacked else 0.0
    # An underslung root carries the stack downward, exactly as the ceiling
    # source record does: seat above, riser below, links hanging.
    stack_dir = -1.0 if (stacked and _mount_hangs(config.mount)) else 1.0
    body_a = stack_dir * (hub_half + riser_h + sec_a / 2.0) if stacked else 0.0
    fore_body_a = stack_dir * (fore_hub_half + riser_h + fsec_a / 2.0) if stacked else 0.0

    # The upper link body must not enter the forearm hub's radial keep-out.
    if upper_body_x1 <= sec_p * 0.6:
        raise ValueError("upper link is too short to clear the elbow hub")

    mount_top_z, mount_axis_x, env_hx, env_hy, hangs = _mount_frame(
        config.mount, mount_height, reach
    )

    # How much room the parent must leave below (and above) the shoulder axis.
    # For pitch the mount sits perpendicular to the axis, so it clears the swept
    # body; for the yaw families it sits along the axis, so it clears the seat.
    if _is_pitch_family(config.axis_family):
        seat_span_z = drop_p + 4.0 * BEARING_CLEARANCE
    elif stacked:
        seat_span_z = hub_half + disc_t + riser_h + sec_a + 4.0 * BEARING_CLEARANCE
    else:
        seat_span_z = hub_half + cheek_t + 4.0 * BEARING_CLEARANCE
    mount_deck_z = mount_top_z - seat_span_z
    mount_ceiling_z = mount_top_z + seat_span_z

    # --- end effector footprint -------------------------------------------
    ee = config.end_effector
    if ee == "bolted_round_flange":
        ee_face_y = ee_face_z = max(0.048, reach * 0.105)
    elif ee == "square_tool_plate":
        ee_face_y, ee_face_z = max(0.058, reach * 0.135), max(0.050, reach * 0.115)
    elif ee == "rubber_pad_face":
        ee_face_y, ee_face_z = max(0.070, reach * 0.155), max(0.055, reach * 0.125)
    elif ee == "suction_cup":
        ee_face_y = ee_face_z = max(0.052, reach * 0.110)
    elif ee == "clamped_tool_socket":
        ee_face_y = ee_face_z = max(0.042, reach * 0.090)
    elif ee == "adapter_and_face":
        ee_face_y, ee_face_z = max(0.060, reach * 0.140), max(0.062, reach * 0.145)
    else:
        ee_face_y = ee_face_z = max(0.024, min(fsec_a, fsec_p) * 0.72)
    wrist_y = max(fsec_a, ee_face_y * 0.62)
    wrist_z = max(fsec_p, ee_face_z * 0.62)

    # --- solved joint limits ----------------------------------------------
    if _is_pitch_family(config.axis_family):
        # With axis (0,1,0) a positive angle swings the arm DOWN, so the two
        # limits are solved against different obstacles.
        reach_total = upper_len + forearm_len + tool_len
        ground_clear = 0.020

        def _edge_clearance(theta: float, headroom_z: float, edge: float) -> float:
            """Where the link's lower edge first crosses below the mount deck.

            The link is not a ray: its lower edge already sits `drop_p` below the
            axis at the root, so the crossing point has to be solved from the
            edge, not the centreline.
            """

            sin_t, cos_t = math.sin(theta), math.cos(theta)
            if sin_t <= 1e-6:
                return float("inf")
            depth = headroom_z - drop_p * cos_t
            if depth < 0.0:
                return -float("inf")
            return (depth / sin_t) * cos_t + drop_p * sin_t - edge

        def _swing_limit(headroom_z: float, overhead: bool) -> float:
            """Largest swing before the link's lower edge enters the mount box."""

            lim = []
            edge = max(env_hx - mount_axis_x, hub_r * 1.3) + SWING_MARGIN
            if edge > 1e-6:
                lo, hi = 0.0, 1.35
                if _edge_clearance(hi, headroom_z, edge) >= 0.0:
                    lim.append(hi)
                else:
                    for _ in range(40):
                        mid = (lo + hi) * 0.5
                        if _edge_clearance(mid, headroom_z, edge) >= 0.0:
                            lo = mid
                        else:
                            hi = mid
                    lim.append(lo * 0.96)
            else:
                lim.append(1.35)
            floor_room = mount_top_z - drop_p - tip_drop - ground_clear
            if not overhead and floor_room > 0.0:
                # ...and, going down, may not reach the floor.
                lim.append(math.asin(_clamp(floor_room / reach_total, 0.0, 1.0)))
            elif not overhead:
                lim.append(0.10)
            return _clamp(min(lim), 0.10, 1.35)

        if hangs:
            # Underslung: the chain hangs, so down is free and up meets the deck.
            shoulder_upper = 1.35
            shoulder_lower = -_swing_limit(seat_span_z, True)
        else:
            shoulder_upper = _swing_limit(seat_span_z, False)
            overhead = config.mount in ("gantry_backbone", "open_frame_mast")
            shoulder_lower = -(_swing_limit(seat_span_z, True) if overhead else 1.35)
    else:
        clear_y = env_hy + SWING_MARGIN + max(sec_a, sec_p) * 0.5
        if upper_len > clear_y:
            shoulder_lower = -_clamp(math.acos(_clamp(clear_y / upper_len, -1.0, 1.0)) * 0.94, 0.30, 2.35)
        else:
            shoulder_lower = -0.30
        shoulder_upper = -shoulder_lower

    # Folding the elbow brings the forearm back toward the base. The reach that
    # matters is the true tip radius from the elbow (a dogleg is longer than its
    # x-length), and the body half-width leads the tip into the envelope.
    fore_reach = math.hypot(forearm_len, tip_drop) + tool_len
    need_cos = (env_hx + SWING_MARGIN + fore_drop_p - mount_axis_x - upper_len) / max(fore_reach, 1e-6)
    fold = 2.30 if need_cos <= -1.0 else math.acos(_clamp(need_cos, -1.0, 1.0)) * 0.90
    # Folding also closes the forearm onto the upper link. Both bodies stop a
    # real distance short of the elbow; the smaller of those voids sets how far
    # the two centrelines may close before the sections touch.
    elbow_void = min(upper_len - upper_body_x1, fore_body_x0)
    half_sum = (sec_p + fsec_p) * 0.5 + 4.0 * BEARING_CLEARANCE
    fold_geom = math.pi - math.asin(_clamp(half_sum / max(elbow_void, 1e-6), 0.0, 1.0))
    fold = min(fold, fold_geom)
    if _is_pitch_family(config.axis_family) and not hangs:
        # Motion QC also samples coupled poses. Solve the fold from the shoulder's
        # most adverse angle, not from neutral, so shoulder-down plus elbow-fold
        # still keeps the forearm out of the mount box.
        for swing in (shoulder_upper, -shoulder_lower):
            span = env_hx + SWING_MARGIN + fore_drop_p - mount_axis_x - upper_len * math.cos(swing)
            ratio = span / max(fore_reach, 1e-6)
            if ratio <= -1.0:
                continue
            fold = min(fold, max(0.35, math.acos(_clamp(ratio, -1.0, 1.0)) - swing))
    fold = _clamp(fold, 0.35, 2.30)

    return ResolvedConfig(
        axis_family=config.axis_family,
        mount=config.mount,
        bearing_detail=config.bearing_detail,
        upper_link_body=config.upper_link_body,
        forearm_body=config.forearm_body,
        end_effector=config.end_effector,
        terminal_body=config.terminal_body,
        palette_style=config.palette_style,
        palette=PALETTES[config.palette_style],
        name=config.name or "serial_elbow_arm",
        total_reach=reach,
        upper_len=upper_len,
        forearm_len=forearm_len,
        tool_len=tool_len,
        upper_body_x1=upper_body_x1,
        fore_body_x0=fore_body_x0,
        sec_a=sec_a,
        sec_p=sec_p,
        fsec_a=fsec_a,
        fsec_p=fsec_p,
        hub_r=hub_r,
        hub_half=hub_half,
        fore_hub_r=fore_hub_r,
        fore_hub_half=fore_hub_half,
        cheek_t=cheek_t,
        disc_t=disc_t,
        riser_h=riser_h,
        stack_dir=stack_dir,
        body_a=body_a,
        fore_body_a=fore_body_a,
        drop_p=drop_p,
        fore_drop_p=fore_drop_p,
        seat_span_z=seat_span_z,
        mount_top_z=mount_top_z,
        mount_axis_x=mount_axis_x,
        mount_envelope_half_x=env_hx,
        mount_envelope_half_y=env_hy,
        mount_deck_z=mount_deck_z,
        mount_ceiling_z=mount_ceiling_z,
        hangs_below=hangs,
        shoulder_lower=shoulder_lower,
        shoulder_upper=shoulder_upper,
        elbow_lower=-fold,
        elbow_upper=fold,
        ee_face_y=ee_face_y,
        ee_face_z=ee_face_z,
        ee_len=tool_len,
        wrist_y=wrist_y,
        wrist_z=wrist_z,
    )


def _is_pitch_family(axis_family: str) -> bool:
    return axis_family == "pitch_clevis"


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, object]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return {
        "axis_family": r.axis_family,
        "mount": r.mount,
        "bearing_detail": r.bearing_detail,
        "upper_link_body": r.upper_link_body,
        "forearm_body": r.forearm_body,
        "end_effector": r.end_effector,
        "terminal_body": r.terminal_body,
    }


def slot_choices_for_seed(seed: int) -> dict[str, object]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# primitives
# ---------------------------------------------------------------------------


def _box(part, name, size, xyz, mat, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=mat, name=name, material_class_id="metal.paint_coated")


def _cyl(part, name, radius, length, xyz, mat, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length), origin=Origin(xyz=xyz, rpy=rpy), material=mat, name=name, material_class_id="metal.stainless_matte"
    )


def _axis_vec(r: ResolvedConfig) -> tuple[float, float, float]:
    return (0.0, 1.0, 0.0) if _is_pitch(r) else (0.0, 0.0, 1.0)


def _hub_rpy(r: ResolvedConfig) -> tuple[float, float, float]:
    """Local rpy that lays a Cylinder onto the active joint axis."""

    return (HALF_PI, 0.0, 0.0) if _is_pitch(r) else (0.0, 0.0, 0.0)


def _hardware_sides(r: ResolvedConfig) -> tuple[float, ...]:
    """A clevis straddles; a stacked seat has only a lower face."""

    return (-r.stack_dir,) if r.axis_family == "yaw_stacked" else (-1.0, 1.0)


def _rect_profile(ha: float, hb: float) -> list[tuple[float, float]]:
    return [(-ha, -hb), (ha, -hb), (ha, hb), (-ha, hb)]


def _capsule_profile(x0: float, x1: float, radius: float, segments: int = 14) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for i in range(segments + 1):
        ang = -HALF_PI + math.pi * i / segments
        pts.append((x1 + radius * math.cos(ang), radius * math.sin(ang)))
    for i in range(segments + 1):
        ang = HALF_PI + math.pi * i / segments
        pts.append((x0 + radius * math.cos(ang), radius * math.sin(ang)))
    return pts


def _circle_profile(cx: float, cy: float, radius: float, segments: int = 18) -> list[tuple[float, float]]:
    pts = [
        (cx + radius * math.cos(2.0 * math.pi * i / segments), cy + radius * math.sin(2.0 * math.pi * i / segments))
        for i in range(segments)
    ]
    pts.reverse()
    return pts


# ---------------------------------------------------------------------------
# mount candidates. Authored in world XYZ; every solid stays at or below
# `mount_deck_z` (or at/above `mount_ceiling_z` for the underslung root) so the
# swinging link is never buried in its own base.
# ---------------------------------------------------------------------------


def _mount_bolts(part, r, mats, hx: float, hy: float, top_z: float, prefix: str) -> None:
    """Bolt heads sunk into `top_z`, so they are never a floating island."""

    h = 0.007
    for ix, x in enumerate((-hx, hx)):
        for iy, y in enumerate((-hy, hy)):
            _cyl(part, f"{prefix}__bolt_{ix}{iy}", max(0.005, r.sec_p * 0.13), h,
                 (x, y, top_z + h * 0.15), mats["bolt"])


def _stack(part, r, mats, prefix, base_t, foot_xy, column, top_z):
    """Base plate -> column -> deck, all bounded by `top_z`."""

    fx, fy = foot_xy
    _box(part, f"{prefix}__base_plate", (fx, fy, base_t), (0.0, 0.0, base_t / 2.0), mats["base"])
    col_h = max(0.006, top_z - base_t)
    if column == "round":
        _cyl(part, f"{prefix}__column", r.mount_envelope_half_x * 0.92, col_h, (0.0, 0.0, base_t + col_h / 2.0), mats["base"])
    else:
        _box(part, f"{prefix}__column", (r.mount_envelope_half_x * 1.7, fy * 0.55, col_h),
             (0.0, 0.0, base_t + col_h / 2.0), mats["base"])
    return fx, fy, base_t


def _mount_floor_pedestal_box_build(part, r: ResolvedConfig, mats) -> None:
    p = "mount__floor_pedestal_box"
    t = max(0.014, r.sec_p * 0.30)
    fx, fy, t = _stack(part, r, mats, p, t, (r.mount_envelope_half_x * 2.4, r.mount_envelope_half_y * 2.0), "box", r.mount_deck_z)
    _mount_bolts(part, r, mats, fx * 0.38, fy * 0.34, t, p)


def _mount_floor_pedestal_round_build(part, r: ResolvedConfig, mats) -> None:
    p = "mount__floor_pedestal_round"
    t = max(0.014, r.sec_p * 0.30)
    fx = r.mount_envelope_half_x * 2.2
    _cyl(part, f"{p}__base_disk", fx / 2.0, t, (0.0, 0.0, t / 2.0), mats["base"])
    col_h = max(0.006, r.mount_deck_z - t)
    _cyl(part, f"{p}__round_column", r.mount_envelope_half_x * 0.92, col_h, (0.0, 0.0, t + col_h / 2.0), mats["base"])


def _mount_bench_clamp_plate_build(part, r: ResolvedConfig, mats) -> None:
    p = "mount__bench_clamp_plate"
    fx, fy = r.mount_envelope_half_x * 2.8, r.mount_envelope_half_y * 2.3
    slab = max(0.016, r.sec_p * 0.34)
    _box(part, f"{p}__bench_top", (fx * 1.25, fy * 1.25, slab), (0.0, 0.0, -slab / 2.0), mats["cover"])
    pt = max(0.010, r.sec_p * 0.22)
    _box(part, f"{p}__mounting_plate", (fx, fy, pt), (0.0, 0.0, pt / 2.0), mats["base"])
    _mount_bolts(part, r, mats, fx * 0.38, fy * 0.36, pt, p)
    col_h = max(0.006, r.mount_deck_z - pt)
    _cyl(part, f"{p}__base_column", r.mount_envelope_half_x * 0.85, col_h, (0.0, 0.0, pt + col_h / 2.0), mats["base"])


def _mount_wall_side_plate_build(part, r: ResolvedConfig, mats) -> None:
    p = "mount__wall_side_plate"
    pt = max(0.012, r.sec_p * 0.26)
    ph = max(0.20, r.total_reach * 0.62)
    pw = max(0.14, r.total_reach * 0.34)
    back_x = -r.mount_axis_x - pt / 2.0
    _box(part, f"{p}__wall_plate", (pt, pw, ph), (back_x, 0.0, r.mount_top_z), mats["base"])
    arm = max(0.004, r.mount_axis_x - r.seat_span_z)
    _box(part, f"{p}__shoulder_block", (arm, pw * 0.55, r.sec_p * 1.5),
         (back_x + pt / 2.0 + arm / 2.0, 0.0, r.mount_deck_z - r.sec_p * 0.75 + r.seat_span_z * 0.0), mats["base"])
    for i, y in enumerate((-pw * 0.30, pw * 0.30)):
        _box(part, f"{p}__side_rib_{i}", (arm * 0.9, r.cheek_t * 1.4, r.sec_p * 1.9),
             (back_x + pt / 2.0 + arm * 0.45, y, r.mount_deck_z - r.sec_p * 0.55), mats["base"])
    for i, z in enumerate((r.mount_top_z - ph * 0.34, r.mount_top_z + ph * 0.34)):
        for j, y in enumerate((-pw * 0.32, pw * 0.32)):
            _cyl(part, f"{p}__wall_bolt_{i}{j}", max(0.005, r.sec_p * 0.13), 0.007,
                 (back_x + pt / 2.0 - 0.0015, y, z), mats["bolt"], rpy=(0.0, HALF_PI, 0.0))


def _mount_ceiling_underslung_build(part, r: ResolvedConfig, mats) -> None:
    p = "mount__ceiling_underslung"
    t = max(0.014, r.sec_p * 0.30)
    fx, fy = r.mount_envelope_half_x * 2.4, r.mount_envelope_half_y * 2.0
    can_bot = r.mount_ceiling_z
    can_h = max(0.020, r.total_reach * 0.10)
    deck_z = can_bot + can_h
    _cyl(part, f"{p}__motor_can", r.mount_envelope_half_x * 0.92, can_h, (0.0, 0.0, can_bot + can_h / 2.0), mats["cover"])
    _box(part, f"{p}__ceiling_plate", (fx, fy, t), (0.0, 0.0, deck_z + t / 2.0), mats["cover"])
    _mount_bolts(part, r, mats, fx * 0.36, fy * 0.34, deck_z + t, p)


def _mount_gantry_backbone_build(part, r: ResolvedConfig, mats) -> None:
    p = "mount__gantry_backbone"
    t = max(0.016, r.sec_p * 0.34)
    fx, fy = r.mount_envelope_half_x * 2.0, r.mount_envelope_half_y * 2.0
    back_x = -r.mount_axis_x - r.mount_envelope_half_x * 0.55
    _box(part, f"{p}__base_foot", (fx, fy, t), (back_x, 0.0, t / 2.0), mats["base"])
    spine_top = r.mount_ceiling_z + max(0.03, r.total_reach * 0.08)
    spine_h = max(0.03, spine_top - t)
    _box(part, f"{p}__rear_backbone", (r.mount_envelope_half_x * 0.75, fy * 0.62, spine_h),
         (back_x, 0.0, t + spine_h / 2.0), mats["base"])
    _box(part, f"{p}__top_bridge", (r.mount_envelope_half_x * 1.9, fy * 0.66, r.sec_p * 0.40),
         (back_x + r.mount_envelope_half_x * 0.55, 0.0, spine_top + r.sec_p * 0.20), mats["base"])
    _box(part, f"{p}__rear_tie", (r.mount_envelope_half_x * 0.5, fy * 0.60, r.sec_p * 0.34),
         (back_x + r.mount_envelope_half_x * 0.25, 0.0, r.mount_deck_z - r.sec_p * 0.17), mats["base"])


def _mount_open_frame_mast_build(part, r: ResolvedConfig, mats) -> None:
    p = "mount__open_frame_mast"
    t = max(0.014, r.sec_p * 0.30)
    fx, fy = r.mount_envelope_half_x * 2.2, r.mount_envelope_half_y * 2.0
    back_x = -r.mount_axis_x - r.mount_envelope_half_x * 0.45
    _box(part, f"{p}__base_plate", (fx, fy, t), (back_x * 0.4, 0.0, t / 2.0), mats["base"])
    mast_top = r.mount_ceiling_z + max(0.02, r.total_reach * 0.05)
    mast_h = max(0.03, mast_top - t)
    _box(part, f"{p}__mast", (r.mount_envelope_half_x * 0.70, fy * 0.52, mast_h), (back_x, 0.0, t + mast_h / 2.0), mats["base"])
    _box(part, f"{p}__top_tie", (r.mount_envelope_half_x * 1.1, fy * 0.52, r.sec_p * 0.26),
         (back_x + r.mount_envelope_half_x * 0.20, 0.0, mast_top + r.sec_p * 0.13), mats["base"])
    _box(part, f"{p}__lower_brace", (r.mount_envelope_half_x * 0.9, fy * 0.52, r.sec_p * 0.30),
         (back_x + r.mount_envelope_half_x * 0.30, 0.0, r.mount_deck_z - r.sec_p * 0.15), mats["base"])


def _mount_cast_housing_block_build(part, r: ResolvedConfig, mats) -> None:
    p = "mount__cast_housing_block"
    t = max(0.018, r.sec_p * 0.36)
    fx, fy = r.mount_envelope_half_x * 2.3, r.mount_envelope_half_y * 2.2
    _box(part, f"{p}__base_plate", (fx, fy, t), (0.0, 0.0, t / 2.0), mats["base"])
    cast_h = max(0.008, r.mount_deck_z - t)
    _box(part, f"{p}__cast_pedestal", (r.mount_envelope_half_x * 1.55, fy * 0.72, cast_h), (0.0, 0.0, t + cast_h / 2.0), mats["base"])
    _mount_bolts(part, r, mats, fx * 0.38, fy * 0.36, t, p)


_MOUNT_BUILDERS = {
    "floor_pedestal_box": _mount_floor_pedestal_box_build,
    "floor_pedestal_round": _mount_floor_pedestal_round_build,
    "bench_clamp_plate": _mount_bench_clamp_plate_build,
    "wall_side_plate": _mount_wall_side_plate_build,
    "ceiling_underslung": _mount_ceiling_underslung_build,
    "gantry_backbone": _mount_gantry_backbone_build,
    "open_frame_mast": _mount_open_frame_mast_build,
    "cast_housing_block": _mount_cast_housing_block_build,
}


# ---------------------------------------------------------------------------
# axis_family - the bearing seat the parent presents to the child hub.
# `half` is the child hub's half-length along the axis; the seat face sits one
# contact band outside it, so the hub always reads as carried.
# ---------------------------------------------------------------------------


def _cheek_span(oz: float, radius: float, anchor_z: float | None) -> tuple[float, float]:
    """Vertical span of a cheek: from its anchor (if any) up past the axis."""

    top = oz + radius * 1.2
    bottom = oz - radius * 1.2
    if anchor_z is None:
        return bottom, top
    if anchor_z < bottom:
        return anchor_z, top
    if anchor_z > top:
        return bottom, anchor_z
    return bottom, top


def _axis_family_pitch_clevis_build(part, r, mats, origin, half, radius, tag, anchor_z=None) -> None:
    p = f"axis_family__pitch_clevis__{tag}"
    ox, oy, oz = origin
    d = half + BEARING_CLEARANCE + r.cheek_t / 2.0
    z0, z1 = _cheek_span(oz, radius, anchor_z)
    for i, sign in enumerate((-1.0, 1.0)):
        _box(part, f"{p}__cheek_{i}", (radius * 2.4, r.cheek_t, z1 - z0),
             (ox, oy + sign * d, (z0 + z1) * 0.5), mats["base"])
    _box(part, f"{p}__yoke_web", (radius * 1.1, 2.0 * d + r.cheek_t, radius * 1.0),
         (ox - radius * 1.65, oy, oz), mats["base"])


def _axis_family_yaw_clevis_build(part, r, mats, origin, half, radius, tag, anchor_z=None) -> None:
    p = f"axis_family__yaw_clevis__{tag}"
    ox, oy, oz = origin
    d = half + BEARING_CLEARANCE + r.cheek_t / 2.0
    for i, sign in enumerate((-1.0, 1.0)):
        _box(part, f"{p}__ear_{i}", (radius * 2.4, radius * 2.4, r.cheek_t), (ox, oy, oz + sign * d), mats["base"])
    _box(part, f"{p}__yoke_web", (radius * 1.1, radius * 1.0, 2.0 * d + r.cheek_t),
         (ox - radius * 1.65, oy, oz), mats["base"])
    if anchor_z is not None:
        # The outer ear grows into a post that reaches its anchor.
        outer = oz - (d + r.cheek_t / 2.0) if anchor_z < oz else oz + (d + r.cheek_t / 2.0)
        lo, hi = (anchor_z, outer) if anchor_z < outer else (outer, anchor_z)
        if hi - lo > 1e-6:
            _box(part, f"{p}__ear_post", (radius * 2.0, radius * 2.0, hi - lo),
                 (ox, oy, (lo + hi) * 0.5), mats["base"])


def _axis_family_yaw_stacked_build(part, r, mats, origin, half, radius, tag, anchor_z=None) -> None:
    p = f"axis_family__yaw_stacked__{tag}"
    ox, oy, oz = origin
    face = oz - r.stack_dir * (half + BEARING_CLEARANCE)
    back = face - r.stack_dir * r.disc_t
    if anchor_z is not None:
        back = anchor_z
    lo, hi = (back, face) if back < face else (face, back)
    _cyl(part, f"{p}__bearing_disc", radius * 1.65, max(hi - lo, r.disc_t),
         (ox, oy, (lo + hi) * 0.5), mats["base"])


_AXIS_SEAT_BUILDERS = {
    "pitch_clevis": _axis_family_pitch_clevis_build,
    "yaw_clevis": _axis_family_yaw_clevis_build,
    "yaw_stacked": _axis_family_yaw_stacked_build,
}


# ---------------------------------------------------------------------------
# bearing_detail - coaxial hardware, always outside the seat face
# ---------------------------------------------------------------------------


def _hw_centres(r, origin, half, thickness, stack=0.0):
    """Centres for coaxial hardware seated on the outer cheek face.

    `stack` is how far a second layer sits beyond the first. Each layer bites
    20% of its own thickness into what it is mounted on, so the part never
    contains a disconnected island.
    """

    ox, oy, oz = origin
    face = half + BEARING_CLEARANCE + r.cheek_t
    for i, sign in enumerate(_hardware_sides(r)):
        d = face + stack + thickness * 0.3
        yield i, sign, ((ox, oy + sign * d, oz) if _is_pitch(r) else (ox, oy, oz + sign * d))


def _bearing_detail_plain_hub_build(part, r, mats, origin, half, radius, tag) -> None:
    return None


def _bearing_detail_ring_and_cover_build(part, r, mats, origin, half, radius, tag) -> None:
    p = f"bearing_detail__ring_and_cover__{tag}"
    rpy = _hub_rpy(r)
    for i, _s, c in _hw_centres(r, origin, half, r.cheek_t * 0.85):
        _cyl(part, f"{p}__ring_{i}", radius * 1.55, r.cheek_t * 0.85, c, mats["cover"], rpy=rpy)
    for i, _s, c in _hw_centres(r, origin, half, r.cheek_t * 0.65, stack=r.cheek_t * 0.60):
        _cyl(part, f"{p}__cover_{i}", radius * 1.25, r.cheek_t * 0.65, c, mats["cover"], rpy=rpy)


def _bearing_detail_outboard_boss_cap_build(part, r, mats, origin, half, radius, tag) -> None:
    p = f"bearing_detail__outboard_boss_cap__{tag}"
    rpy = _hub_rpy(r)
    for i, _s, c in _hw_centres(r, origin, half, r.cheek_t * 1.05):
        _cyl(part, f"{p}__boss_{i}", radius * 1.45, r.cheek_t * 1.05, c, mats["base"], rpy=rpy)


def _bearing_detail_through_pin_span_build(part, r, mats, origin, half, radius, tag) -> None:
    p = f"bearing_detail__through_pin_span__{tag}"
    rpy = _hub_rpy(r)
    ox, oy, oz = origin
    # The hub is not bored, so a bar straight through it would be buried in the
    # child. The pin reads through its protruding ends outboard of each face.
    stub = r.cheek_t * 2.2
    for i, _s, c in _hw_centres(r, origin, half, stub):
        _cyl(part, f"{p}__pin_end_{i}", radius * 0.34, stub, c, mats["cover"], rpy=rpy)
    for i, _s, c in _hw_centres(r, origin, half, r.cheek_t * 0.70):
        _cyl(part, f"{p}__pin_cap_{i}", radius * 0.80, r.cheek_t * 0.7, c, mats["cover"], rpy=rpy)


def _bearing_detail_capped_seal_stack_build(part, r, mats, origin, half, radius, tag) -> None:
    p = f"bearing_detail__capped_seal_stack__{tag}"
    rpy = _hub_rpy(r)
    for i, _s, c in _hw_centres(r, origin, half, r.cheek_t * 0.85):
        _cyl(part, f"{p}__cap_{i}", radius * 1.42, r.cheek_t * 0.85, c, mats["base"], rpy=rpy)
    for i, _s, c in _hw_centres(r, origin, half, r.cheek_t * 0.40, stack=r.cheek_t * 0.60):
        _cyl(part, f"{p}__seal_{i}", radius * 0.98, r.cheek_t * 0.40, c, mats["cover"], rpy=rpy)


_BEARING_BUILDERS = {
    "plain_hub": _bearing_detail_plain_hub_build,
    "ring_and_cover": _bearing_detail_ring_and_cover_build,
    "outboard_boss_cap": _bearing_detail_outboard_boss_cap_build,
    "through_pin_span": _bearing_detail_through_pin_span_build,
    "capped_seal_stack": _bearing_detail_capped_seal_stack_build,
}


# ---------------------------------------------------------------------------
# link bodies. Authored in (x, a, p): every spread feature goes along `p`, so
# the body's extent along the joint axis is always exactly `sec_a` and the
# clevis gap derived from it always fits.
# ---------------------------------------------------------------------------


def _fore_span(r: ResolvedConfig) -> tuple[float, float, float]:
    """(x0, x1, centre) of the forearm body, standing off the elbow void."""

    x0 = r.fore_body_x0
    x1 = r.forearm_len
    return x0, x1, (x0 + x1) * 0.5


def _fore_neck(part, r: ResolvedConfig, mats) -> None:
    """Connects the forearm hub to its body across the elbow stand-off."""

    x0 = r.fore_body_x0
    _box(part, "forearm_body__root_neck", _sz(r, x0 * 1.1, r.fsec_a, r.fsec_p * 0.60),
         _v(r, x0 * 0.5, r.fore_body_a, 0.0), mats["link"])


def _elbow_seat_stem(part, r: ResolvedConfig, mats, origin) -> None:
    """Bridges the upper link body forward to the elbow seat."""

    span_a = 2.0 * (r.fore_hub_half + BEARING_CLEARANCE + r.cheek_t)
    # The stem may reach the cheeks but must stop outside the forearm hub's
    # radial keep-out, or it is buried in the part it carries.
    x0 = r.upper_body_x1 * 0.82
    x1 = r.upper_len - (r.fore_hub_r + 2.0 * BEARING_CLEARANCE)
    if x1 <= x0:
        return
    _box(part, "axis_family__elbow_stem",
         _sz(r, x1 - x0, max(span_a, r.sec_a * 0.6), max(r.fore_hub_r * 2.2, r.sec_p * 0.55)),
         _v(r, (x0 + x1) * 0.5, r.body_a, 0.0), mats["base"])


def _upper_neck(part, r: ResolvedConfig, mats) -> None:
    """Connects the upper link hub to whatever body candidate is active."""

    _box(part, "upper_link_body__root_neck",
         _sz(r, max(r.hub_r * 2.4, r.upper_body_x1 * 0.16), r.sec_a, r.sec_p * 0.66),
         _v(r, max(r.hub_r * 1.2, r.upper_body_x1 * 0.08), r.body_a, 0.0), mats["link"])


# x of each mount's load-bearing structure, so the yoke bridge knows how far it
# has to cantilever out to the joint axis.
_MOUNT_STRUCT_X = {
    "floor_pedestal_box": 0.0,
    "floor_pedestal_round": 0.0,
    "bench_clamp_plate": 0.0,
    "wall_side_plate": -1.0,
    "ceiling_underslung": 0.0,
    "gantry_backbone": -1.55,
    "open_frame_mast": -1.45,
    "cast_housing_block": 0.0,
}


def _mount_yoke_bridge(part, r: ResolvedConfig, mats) -> None:
    """Cantilevers the mount deck out to the shoulder axis."""

    struct_x = _MOUNT_STRUCT_X[r.mount] * r.mount_envelope_half_x
    axis_x = r.mount_axis_x
    x0, x1 = min(struct_x, axis_x) - r.hub_r * 0.6, max(struct_x, axis_x) + r.hub_r * 1.1
    width = 2.0 * (r.hub_half + BEARING_CLEARANCE + r.cheek_t)
    thick = max(0.010, r.sec_p * 0.28)
    z = (r.mount_ceiling_z + thick * 0.5) if r.hangs_below else (r.mount_deck_z - thick * 0.5)
    _box(part, "mount__yoke_bridge", (x1 - x0, max(width, r.hub_r * 2.2), thick),
         ((x0 + x1) * 0.5, 0.0, z), mats["base"])


def _root_hub(part, r: ResolvedConfig, mats, radius, half, body_a, prefix) -> None:
    _cyl(part, f"{prefix}__hub", radius, 2.0 * half, (0.0, 0.0, 0.0), mats["link"], rpy=_hub_rpy(r))
    if r.axis_family == "yaw_stacked" and r.riser_h > 0.0:
        over = 0.002
        _cyl(part, f"{prefix}__riser", radius * 0.82, r.riser_h + 2.0 * over,
             (0.0, 0.0, r.stack_dir * (half + r.riser_h / 2.0)), mats["link"])
    _ = body_a


def _upper_link_body_box_beam_build(part, r: ResolvedConfig, mats) -> None:
    p, ln, a = "upper_link_body__box_beam", r.upper_body_x1, r.body_a
    _box(part, f"{p}__main_beam", _sz(r, ln, r.sec_a, r.sec_p), _v(r, ln * 0.5, a, 0.0), mats["link"])
    _box(part, f"{p}__lower_rib", _sz(r, ln * 0.62, r.sec_a * 0.52, r.sec_p * 0.26),
         _v(r, ln * 0.47, a, -r.sec_p * 0.55), mats["link"])


def _upper_link_body_windowed_twin_plate_build(part, r: ResolvedConfig, mats) -> None:
    p, ln, a = "upper_link_body__windowed_twin_plate", r.upper_body_x1, r.body_a
    t = max(0.006, r.sec_a * 0.17)
    outer = _capsule_profile(r.sec_p * 0.5, ln - r.sec_p * 0.5, r.sec_p * 0.50)
    hole = _circle_profile(ln * 0.5, 0.0, r.sec_p * 0.24)
    geom = ExtrudeWithHolesGeometry(outer, [hole], t, center=True)
    geom.rotate_x(HALF_PI)
    if not _is_pitch(r):
        geom.rotate_x(HALF_PI)
    mesh = mesh_from_geometry(geom, f"{p}_plate")
    for i, sign in enumerate((-1.0, 1.0)):
        part.visual(mesh, origin=Origin(xyz=_v(r, 0.0, a + sign * (r.sec_a * 0.5 - t * 0.5), 0.0)),
                    material=mats["link"], name=f"{p}__side_plate_{i}", material_class_id="metal.paint_coated")
    _box(part, f"{p}__top_web", _sz(r, ln * 0.92, r.sec_a, r.sec_p * 0.16), _v(r, ln * 0.5, a, r.sec_p * 0.42), mats["cover"])
    _box(part, f"{p}__bottom_web", _sz(r, ln * 0.92, r.sec_a * 0.84, r.sec_p * 0.14), _v(r, ln * 0.5, a, -r.sec_p * 0.42), mats["cover"])


def _upper_link_body_box_section_tube_build(part, r: ResolvedConfig, mats) -> None:
    p, ln, a = "upper_link_body__box_section_tube", r.upper_body_x1, r.body_a
    cx = r.upper_body_x1 * 0.5
    wall = max(0.005, r.sec_p * 0.14)
    _box(part, f"{p}__top_wall", _sz(r, ln, r.sec_a, wall), _v(r, cx, a, r.sec_p / 2.0 - wall / 2.0), mats["link"])
    _box(part, f"{p}__bottom_wall", _sz(r, ln, r.sec_a, wall), _v(r, cx, a, -r.sec_p / 2.0 + wall / 2.0), mats["link"])
    for i, sign in enumerate((-1.0, 1.0)):
        _box(part, f"{p}__side_wall_{i}", _sz(r, ln, wall, r.sec_p),
             _v(r, cx, a + sign * (r.sec_a / 2.0 - wall / 2.0), 0.0), mats["link"])


def _upper_link_body_dual_parallel_bars_build(part, r: ResolvedConfig, mats) -> None:
    p, ln, a = "upper_link_body__dual_parallel_bars", r.upper_body_x1, r.body_a
    bh = max(0.010, r.sec_p * 0.26)
    for i, sign in enumerate((-1.0, 1.0)):
        _box(part, f"{p}__bar_{i}", _sz(r, ln, r.sec_a * 0.86, bh),
             _v(r, ln * 0.5, a, sign * (r.sec_p * 0.5 - bh * 0.5)), mats["link"])
    _box(part, f"{p}__tie_bar", _sz(r, ln, r.sec_a, r.sec_p * 0.18), _v(r, ln * 0.5, a, 0.0), mats["cover"])


def _upper_link_body_twin_rail_span_build(part, r: ResolvedConfig, mats) -> None:
    p, ln, a = "upper_link_body__twin_rail_span", r.upper_body_x1, r.body_a
    rh = max(0.009, r.sec_p * 0.22)
    for i, sign in enumerate((-1.0, 1.0)):
        _box(part, f"{p}__rail_{i}", _sz(r, ln, r.sec_a, rh),
             _v(r, ln * 0.5, a, sign * (r.sec_p * 0.5 - rh * 0.5)), mats["link"])
    _box(part, f"{p}__root_web", _sz(r, r.hub_r * 2.2, r.sec_a, r.sec_p * 0.62), _v(r, r.hub_r * 1.4, a, 0.0), mats["link"])
    _box(part, f"{p}__tip_web", _sz(r, r.hub_r * 2.0, r.sec_a, r.sec_p * 0.62), _v(r, ln - r.hub_r * 0.9, a, 0.0), mats["link"])


def _upper_link_body_i_beam_ribbed_build(part, r: ResolvedConfig, mats) -> None:
    p, ln, a = "upper_link_body__i_beam_ribbed", r.upper_body_x1, r.body_a
    _box(part, f"{p}__web", _sz(r, ln, r.sec_a * 0.40, r.sec_p * 0.94), _v(r, ln * 0.5, a, 0.0), mats["link"])
    for i, sign in enumerate((-1.0, 1.0)):
        _box(part, f"{p}__flange_{i}", _sz(r, ln, r.sec_a, r.sec_p * 0.20),
             _v(r, ln * 0.5, a, sign * r.sec_p * 0.38), mats["link"])
    _box(part, f"{p}__gusset", _sz(r, ln * 0.30, r.sec_a * 0.70, r.sec_p * 0.60), _v(r, ln * 0.20, a, 0.0), mats["cover"])


_UPPER_BUILDERS = {
    "box_beam": _upper_link_body_box_beam_build,
    "windowed_twin_plate": _upper_link_body_windowed_twin_plate_build,
    "box_section_tube": _upper_link_body_box_section_tube_build,
    "dual_parallel_bars": _upper_link_body_dual_parallel_bars_build,
    "twin_rail_span": _upper_link_body_twin_rail_span_build,
    "i_beam_ribbed": _upper_link_body_i_beam_ribbed_build,
}


def _dogleg_stub(r: ResolvedConfig) -> float:
    return max(r.fore_body_x0, r.fore_hub_r * 1.7, r.forearm_len * 0.18)


def _forearm_body_box_beam_build(part, r: ResolvedConfig, mats) -> None:
    p, a = "forearm_body__box_beam", r.fore_body_a
    _fore_neck(part, r, mats)
    x0, x1, cx = _fore_span(r)
    ln = x1 - x0
    _box(part, f"{p}__main_beam", _sz(r, ln, r.fsec_a, r.fsec_p), _v(r, cx, a, 0.0), mats["link"])
    _box(part, f"{p}__rib", _sz(r, ln * 0.62, r.fsec_a * 0.50, r.fsec_p * 0.26),
         _v(r, cx, a, -r.fsec_p * 0.55), mats["link"])


def _forearm_body_capsule_slotted_plate_build(part, r: ResolvedConfig, mats) -> None:
    p, a = "forearm_body__capsule_slotted_plate", r.fore_body_a
    _fore_neck(part, r, mats)
    x0, ln, _c = _fore_span(r)
    t = max(0.008, r.fsec_a * 0.62)
    # A capsule end bulges a full radius past its centre, so the profile has to
    # stop short of the wrist face or it grows through the tool.
    rad = r.fsec_p * 0.50
    wrist_t = max(0.012, r.tool_len * 0.26)
    x1 = max(x0 + rad * 1.2, ln - wrist_t - rad)
    outer = _capsule_profile(x0, x1, rad)
    slot = _capsule_profile(x0 + (x1 - x0) * 0.30, x0 + (x1 - x0) * 0.70, r.fsec_p * 0.18)
    slot.reverse()
    geom = ExtrudeWithHolesGeometry(outer, [slot], t, center=True)
    geom.rotate_x(HALF_PI)
    if not _is_pitch(r):
        geom.rotate_x(HALF_PI)
    part.visual(mesh_from_geometry(geom, f"{p}_plate"), origin=Origin(xyz=_v(r, 0.0, a, 0.0)),
                material=mats["link"], name=f"{p}__plate", material_class_id="metal.paint_coated")


def _forearm_body_hollow_rect_tube_build(part, r: ResolvedConfig, mats) -> None:
    p, a = "forearm_body__hollow_rect_tube", r.fore_body_a
    _fore_neck(part, r, mats)
    x0, x1, cx = _fore_span(r)
    ln = x1 - x0
    wall = max(0.004, r.fsec_p * 0.16)
    outer = _rect_profile(ln / 2.0, r.fsec_p / 2.0)
    inner = _rect_profile(ln / 2.0 + 0.002, r.fsec_p / 2.0 - wall)
    inner.reverse()
    geom = ExtrudeWithHolesGeometry(outer, [inner], r.fsec_a, center=True)
    geom.rotate_x(HALF_PI)
    if not _is_pitch(r):
        geom.rotate_x(HALF_PI)
    part.visual(mesh_from_geometry(geom, f"{p}_tube"), origin=Origin(xyz=_v(r, cx, a, 0.0)),
                material=mats["link"], name=f"{p}__tube", material_class_id="metal.paint_coated")


def _forearm_body_twin_rail_span_build(part, r: ResolvedConfig, mats) -> None:
    p, a = "forearm_body__twin_rail_span", r.fore_body_a
    _fore_neck(part, r, mats)
    x0, x1, cx = _fore_span(r)
    ln = x1 - x0
    rh = max(0.008, r.fsec_p * 0.28)
    for i, sign in enumerate((-1.0, 1.0)):
        _box(part, f"{p}__rail_{i}", _sz(r, ln, r.fsec_a, rh),
             _v(r, cx, a, sign * (r.fsec_p * 0.5 - rh * 0.5)), mats["link"])


def _forearm_body_dogleg_plate_pair_build(part, r: ResolvedConfig, mats) -> None:
    p, ln, a = "forearm_body__dogleg_plate_pair", r.forearm_len, r.fore_body_a
    t = max(0.006, r.fsec_a * 0.30)
    stub = _dogleg_stub(r)
    _fore_neck(part, r, mats)
    _box(part, f"{p}__root_stub", _sz(r, stub, r.fsec_a, r.fsec_p), _v(r, stub * 0.5, a, 0.0), mats["link"])
    seg = ln - stub
    # The rotated plate corner reaches past its own centreline, so the plate is
    # shortened by that overhang and the tip plane stays clear for the tool.
    seg_geo = max(stub * 0.5, seg - r.fsec_p * 0.55 * math.sin(DOGLEG_ANGLE))
    cx = stub + seg_geo * 0.5 * math.cos(DOGLEG_ANGLE)
    cp = -seg_geo * 0.5 * math.sin(DOGLEG_ANGLE)
    seg = seg_geo
    rpy = (0.0, DOGLEG_ANGLE, 0.0) if _is_pitch(r) else (0.0, 0.0, -DOGLEG_ANGLE)
    for i, sign in enumerate((-1.0, 1.0)):
        _box(part, f"{p}__plate_{i}", _sz(r, seg, t, r.fsec_p * 0.86),
             _v(r, cx, a + sign * (r.fsec_a * 0.5 - t * 0.5), cp), mats["link"], rpy=rpy)
    _box(part, f"{p}__centre_web", _sz(r, seg * 0.70, r.fsec_a * 0.60, r.fsec_p * 0.30),
         _v(r, cx, a, cp), mats["cover"], rpy=rpy)


_FOREARM_BUILDERS = {
    "box_beam": _forearm_body_box_beam_build,
    "capsule_slotted_plate": _forearm_body_capsule_slotted_plate_build,
    "hollow_rect_tube": _forearm_body_hollow_rect_tube_build,
    "twin_rail_span": _forearm_body_twin_rail_span_build,
    "dogleg_plate_pair": _forearm_body_dogleg_plate_pair_build,
}


def _forearm_tip(r: ResolvedConfig) -> tuple[float, float, float]:
    """Where the output face is carried, in forearm-local coordinates."""

    if r.forearm_body == "dogleg_plate_pair":
        stub = _dogleg_stub(r)
        seg = r.forearm_len - stub
        return _v(r, stub + seg * math.cos(DOGLEG_ANGLE), r.fore_body_a, -seg * math.sin(DOGLEG_ANGLE))
    return _v(r, r.forearm_len, r.fore_body_a, 0.0)


# ---------------------------------------------------------------------------
# end effector - authored from a local origin at the wrist face, growing +X
# ---------------------------------------------------------------------------


def _end_effector_bolted_round_flange_build(part, r, mats, o) -> None:
    p = "end_effector__bolted_round_flange"
    ox, oy, oz = o
    rad = r.ee_face_y * 0.5
    _cyl(part, f"{p}__flange", rad, r.ee_len * 0.30, (ox + r.ee_len * 0.15, oy, oz), mats["cover"], rpy=(0.0, HALF_PI, 0.0))
    for i in range(4):
        ang = math.pi / 4.0 + i * HALF_PI
        _cyl(part, f"{p}__bolt_{i}", rad * 0.13, r.ee_len * 0.16,
             (ox + r.ee_len * 0.36, oy + rad * 0.62 * math.cos(ang), oz + rad * 0.62 * math.sin(ang)),
             mats["bolt"], rpy=(0.0, HALF_PI, 0.0))


def _end_effector_square_tool_plate_build(part, r, mats, o) -> None:
    p = "end_effector__square_tool_plate"
    ox, oy, oz = o
    _box(part, f"{p}__plate", (r.ee_len * 0.34, r.ee_face_y, r.ee_face_z), (ox + r.ee_len * 0.17, oy, oz), mats["cover"])
    for i, (dy, dz) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
        _cyl(part, f"{p}__bolt_boss_{i}", r.ee_face_y * 0.10, r.ee_len * 0.16,
             (ox + r.ee_len * 0.42, oy + dy * r.ee_face_y * 0.31, oz + dz * r.ee_face_z * 0.30),
             mats["bolt"], rpy=(0.0, HALF_PI, 0.0))


def _end_effector_rubber_pad_face_build(part, r, mats, o) -> None:
    p = "end_effector__rubber_pad_face"
    ox, oy, oz = o
    _box(part, f"{p}__pad_body", (r.ee_len * 0.46, r.ee_face_y * 0.86, r.ee_face_z * 0.86), (ox + r.ee_len * 0.23, oy, oz), mats["cover"])
    _box(part, f"{p}__rubber_face", (r.ee_len * 0.16, r.ee_face_y, r.ee_face_z), (ox + r.ee_len * 0.54, oy, oz), mats["soft"])


def _end_effector_suction_cup_build(part, r, mats, o) -> None:
    p = "end_effector__suction_cup"
    ox, oy, oz = o
    _cyl(part, f"{p}__tool_flange", r.ee_face_y * 0.42, r.ee_len * 0.26, (ox + r.ee_len * 0.13, oy, oz), mats["cover"], rpy=(0.0, HALF_PI, 0.0))
    drop = r.ee_face_z * 1.05
    tube_bottom = oz - drop + 0.0015
    _cyl(part, f"{p}__vacuum_tube", r.ee_face_y * 0.13, drop, (ox + r.ee_len * 0.30, oy, oz - drop * 0.5 + 0.0015), mats["cover"])
    # The cup is seated onto the tube end, overlapping it, not hung off it.
    cup_h = r.ee_len * 0.20
    _cyl(part, f"{p}__cup", r.ee_face_y * 0.40, cup_h,
         (ox + r.ee_len * 0.30, oy, tube_bottom - cup_h * 0.5 + cup_h * 0.35), mats["soft"])


def _end_effector_clamped_tool_socket_build(part, r, mats, o) -> None:
    p = "end_effector__clamped_tool_socket"
    ox, oy, oz = o
    _cyl(part, f"{p}__socket", r.ee_face_y * 0.46, r.ee_len * 0.62, (ox + r.ee_len * 0.31, oy, oz), mats["cover"], rpy=(0.0, HALF_PI, 0.0))
    for i, sign in enumerate((-1.0, 1.0)):
        _cyl(part, f"{p}__clamp_screw_{i}", r.ee_face_y * 0.13, r.ee_face_y * 0.22,
             (ox + r.ee_len * 0.31, oy + sign * r.ee_face_y * 0.45, oz), mats["bolt"], rpy=(HALF_PI, 0.0, 0.0))
    _cyl(part, f"{p}__bore_plug", r.ee_face_y * 0.20, r.ee_len * 0.18, (ox + r.ee_len * 0.56, oy, oz), mats["soft"], rpy=(0.0, HALF_PI, 0.0))


def _end_effector_adapter_and_face_build(part, r, mats, o) -> None:
    p = "end_effector__adapter_and_face"
    ox, oy, oz = o
    _box(part, f"{p}__adapter", (r.ee_len * 0.52, r.ee_face_y * 0.62, r.ee_face_z * 0.66), (ox + r.ee_len * 0.26, oy, oz), mats["link"])
    _box(part, f"{p}__face_plate", (r.ee_len * 0.20, r.ee_face_y, r.ee_face_z), (ox + r.ee_len * 0.62, oy, oz), mats["cover"])


def _end_effector_bare_nose_tip_build(part, r, mats, o) -> None:
    p = "end_effector__bare_nose_tip"
    ox, oy, oz = o
    _box(part, f"{p}__nose_tip", (r.ee_len * 0.70, r.ee_face_y, r.ee_face_z), (ox + r.ee_len * 0.35, oy, oz), mats["link"])


_EE_BUILDERS = {
    "bolted_round_flange": _end_effector_bolted_round_flange_build,
    "square_tool_plate": _end_effector_square_tool_plate_build,
    "rubber_pad_face": _end_effector_rubber_pad_face_build,
    "suction_cup": _end_effector_suction_cup_build,
    "clamped_tool_socket": _end_effector_clamped_tool_socket_build,
    "adapter_and_face": _end_effector_adapter_and_face_build,
    "bare_nose_tip": _end_effector_bare_nose_tip_build,
}


def _wrist_block(r: ResolvedConfig) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Size and centre of the wrist block the output face bolts onto."""

    tx, ty, tz = _forearm_tip(r)
    thick = max(0.012, r.tool_len * 0.26)
    return (thick, r.wrist_y, r.wrist_z), (tx - thick * 0.5, ty, tz)


def _terminal_body_merged_into_forearm_build(model, forearm, r, mats):
    _EE_BUILDERS[r.end_effector](forearm, r, mats, _forearm_tip(r))
    return None


def _terminal_body_separate_fixed_part_build(model, forearm, r, mats):
    face = model.part("output_face")
    face.meta["role"] = "output_face"
    _EE_BUILDERS[r.end_effector](face, r, mats, (0.0, 0.0, 0.0))
    face.inertial = Inertial.from_geometry(
        Box((max(r.ee_len, 0.02), max(r.ee_face_y, 0.02), max(r.ee_face_z, 0.02))),
        mass=0.35,
        origin=Origin(xyz=(r.ee_len * 0.35, 0.0, 0.0)),
    )
    model.articulation(
        "forearm_to_output_face",
        ArticulationType.FIXED,
        parent=forearm,
        child=face,
        origin=Origin(xyz=_forearm_tip(r)),
    )
    return face


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


def _revolute(model, name, parent, child, point, axis, limits) -> None:
    provider = AxisInterface(name=f"{name}.provider", point=point, axis=axis, radial=(1.0, 0.0, 0.0))
    consumer = AxisInterface(name=f"{name}.consumer", point=(0.0, 0.0, 0.0), axis=axis, radial=(1.0, 0.0, 0.0))
    mate = mate_axes(provider, consumer)
    model.articulation(
        name, ArticulationType.REVOLUTE, parent=parent, child=child,
        origin=mate.origin, axis=mate.axis, motion_limits=limits,
    )
    register_interface_mate(model, name, mate)


def build_serial_elbow_arm(config: Config | None = None, *, assets: AssetContext | None = None) -> ArticulatedObject:
    config = config or Config()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-serial-elbow-arm-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {k: model.material(f"sea_{k}_{r.palette_style}", rgba=v) for k, v in r.palette.items()}
    model.meta["module_slots"] = slot_choices_for_config(r)

    axis = _axis_vec(r)
    shoulder_point = (r.mount_axis_x, 0.0, r.mount_top_z)

    root = model.part("root_mount")
    root.meta["role"] = "root_mount"
    _MOUNT_BUILDERS[r.mount](root, r, mats)
    _mount_yoke_bridge(root, r, mats)
    _AXIS_SEAT_BUILDERS[r.axis_family](
        root, r, mats, shoulder_point, r.hub_half, r.hub_r, "shoulder",
        anchor_z=(r.mount_ceiling_z if r.hangs_below else r.mount_deck_z),
    )
    _BEARING_BUILDERS[r.bearing_detail](root, r, mats, shoulder_point, r.hub_half, r.hub_r, "shoulder")
    root.inertial = Inertial.from_geometry(
        Box((max(r.mount_envelope_half_x * 2.2, 0.05), max(r.mount_envelope_half_y * 2.0, 0.05), max(r.mount_top_z, 0.05))),
        mass=9.0, origin=Origin(xyz=(0.0, 0.0, r.mount_top_z * 0.5)),
    )

    upper = model.part("upper_link")
    upper.meta["role"] = "upper_link"
    _root_hub(upper, r, mats, r.hub_r, r.hub_half, r.body_a, "upper_link_body__root")
    _upper_neck(upper, r, mats)
    _UPPER_BUILDERS[r.upper_link_body](upper, r, mats)
    elbow_local = _v(r, r.upper_len, r.body_a, 0.0)
    _elbow_seat_stem(upper, r, mats, elbow_local)
    _AXIS_SEAT_BUILDERS[r.axis_family](upper, r, mats, elbow_local, r.fore_hub_half, r.fore_hub_r, "elbow")
    _BEARING_BUILDERS[r.bearing_detail](upper, r, mats, elbow_local, r.fore_hub_half, r.fore_hub_r, "elbow")
    upper.inertial = Inertial.from_geometry(
        Box((max(r.upper_len, 0.05), max(r.sec_a, 0.02), max(r.sec_p, 0.02))),
        mass=3.6, origin=Origin(xyz=_v(r, r.upper_len * 0.5, r.body_a, 0.0)),
    )

    forearm = model.part("forearm")
    forearm.meta["role"] = "forearm"
    _root_hub(forearm, r, mats, r.fore_hub_r, r.fore_hub_half, r.fore_body_a, "forearm_body__root")
    _FOREARM_BUILDERS[r.forearm_body](forearm, r, mats)
    wsize, wcentre = _wrist_block(r)
    _box(forearm, "forearm_body__wrist_block", wsize, wcentre, mats["link"])
    forearm.inertial = Inertial.from_geometry(
        Box((max(r.forearm_len, 0.05), max(r.fsec_a, 0.02), max(r.fsec_p, 0.02))),
        mass=2.0, origin=Origin(xyz=_v(r, r.forearm_len * 0.5, r.fore_body_a, 0.0)),
    )

    if r.terminal_body == "separate_fixed_part":
        _terminal_body_separate_fixed_part_build(model, forearm, r, mats)
    else:
        _terminal_body_merged_into_forearm_build(model, forearm, r, mats)
        forearm.meta["carries_output_face"] = True

    _revolute(model, "shoulder_joint", root, upper, shoulder_point, axis,
              MotionLimits(effort=140.0, velocity=1.6, lower=r.shoulder_lower, upper=r.shoulder_upper))
    _revolute(model, "elbow_joint", upper, forearm, elbow_local, axis,
              MotionLimits(effort=85.0, velocity=1.9, lower=r.elbow_lower, upper=r.elbow_upper))
    return model


def build_seeded_serial_elbow_arm(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_serial_elbow_arm(config_from_seed(seed), assets=assets)


def _meshes_materialized(model: ArticulatedObject) -> bool:
    """False while the preflight probe is standing in for real mesh assets."""

    for part in model.parts:
        for visual in getattr(part, "visuals", []):
            filename = getattr(getattr(visual, "geometry", None), "filename", None)
            if filename and "__preflight_probe__" in str(filename):
                return False
    return True


def run_serial_elbow_arm_tests(model: ArticulatedObject, config: Config | None = None) -> TestReport:
    r = resolve_config(config or Config())
    ctx = TestContext(model)
    root = model.get_part("root_mount")
    upper = model.get_part("upper_link")
    forearm = model.get_part("forearm")
    shoulder = model.get_articulation("shoulder_joint")
    elbow = model.get_articulation("elbow_joint")

    ctx.check_model_valid()
    # Preflight intercepts mesh materialization and hands every mesh visual a
    # stub filename, so exact-collision QC has nothing to read. AUTHORING.md
    # defers mesh-asset, exact-collision and isolated-geometry checks to sweep;
    # they run in full there, where the meshes are real.
    meshes_ready = _meshes_materialized(model)
    if meshes_ready:
        ctx.fail_if_isolated_parts()
        ctx.warn_if_part_contains_disconnected_geometry_islands()
        ctx.fail_if_parts_overlap_in_current_pose()

    ctx.check(
        "category_anchor: shoulder and elbow are parallel revolute axes",
        shoulder.articulation_type == ArticulationType.REVOLUTE
        and elbow.articulation_type == ArticulationType.REVOLUTE
        and tuple(round(v, 6) for v in shoulder.axis) == tuple(round(v, 6) for v in elbow.axis),
        f"axes were {shoulder.axis} and {elbow.axis}",
    )
    if meshes_ready:
        ctx.expect_contact(upper, root, contact_tol=0.0015,
                           name="category_anchor: the upper link is carried by a real bearing interface")
        ctx.expect_contact(forearm, upper, contact_tol=0.0015,
                           name="category_anchor: the output face is carried at the forearm tip")

    root_aabb = ctx.part_world_aabb(root)
    ok, detail = True, ""
    for pose_name, pose in (
        ("shoulder_lower", {shoulder: r.shoulder_lower}),
        ("shoulder_upper", {shoulder: r.shoulder_upper}),
        ("elbow_lower", {elbow: r.elbow_lower}),
        ("elbow_upper", {elbow: r.elbow_upper}),
    ):
        with ctx.pose(pose):
            fa = ctx.part_world_aabb(forearm)
            if fa is None or root_aabb is None:
                continue
            ox = min(fa[1][0], root_aabb[1][0]) - max(fa[0][0], root_aabb[0][0])
            oy = min(fa[1][1], root_aabb[1][1]) - max(fa[0][1], root_aabb[0][1])
            oz = min(fa[1][2], root_aabb[1][2]) - max(fa[0][2], root_aabb[0][2])
            if ox > 0.0 and oy > 0.0 and oz > 0.0:
                ok = False
                detail += f"{pose_name}: forearm {fa} vs mount {root_aabb}; "
    ctx.check("category_anchor: the forearm clears the mount envelope over the whole shoulder range", ok, detail or "clear")
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "shortest_reach_biggest_mount_pitch",
        {"axis_family": "pitch_clevis", "mount": "cast_housing_block", "bearing_detail": "capped_seal_stack",
         "upper_link_body": "dual_parallel_bars", "forearm_body": "dogleg_plate_pair",
         "end_effector": "rubber_pad_face", "terminal_body": "separate_fixed_part",
         "total_reach_m": 0.42, "link_ratio": 0.46, "mount_height_m": 0.52, "section_scale": 1.20},
        reason="tightest swing clearance: shortest arm against the widest mount envelope",
    ),
    corner_case(
        "shortest_reach_gantry_yaw_clevis",
        {"axis_family": "yaw_clevis", "mount": "gantry_backbone", "bearing_detail": "through_pin_span",
         "upper_link_body": "windowed_twin_plate", "forearm_body": "capsule_slotted_plate",
         "end_effector": "suction_cup", "terminal_body": "merged_into_forearm",
         "total_reach_m": 0.42, "link_ratio": 0.60, "mount_height_m": 0.52, "section_scale": 1.20},
        reason="same capacity edge with the Z-separated clevis and an overhead backbone",
    ),
    corner_case(
        "underslung_yaw_stacked_longest",
        {"axis_family": "yaw_stacked", "mount": "ceiling_underslung", "bearing_detail": "ring_and_cover",
         "upper_link_body": "box_section_tube", "forearm_body": "hollow_rect_tube",
         "end_effector": "clamped_tool_socket", "terminal_body": "separate_fixed_part",
         "total_reach_m": 1.05, "link_ratio": 0.46, "mount_height_m": 0.16, "section_scale": 0.85},
        reason="inverted support direction at maximum reach and minimum section",
    ),
    corner_case(
        "wall_mounted_longest_thinnest",
        {"axis_family": "pitch_clevis", "mount": "wall_side_plate", "bearing_detail": "outboard_boss_cap",
         "upper_link_body": "i_beam_ribbed", "forearm_body": "twin_rail_span",
         "end_effector": "bare_nose_tip", "terminal_body": "merged_into_forearm",
         "total_reach_m": 1.05, "link_ratio": 0.60, "mount_height_m": 0.16, "section_scale": 0.85},
        reason="longest cantilever off a wall plate with the thinnest sections",
    ),
)

__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_seeded_serial_elbow_arm",
    "build_serial_elbow_arm",
    "config_from_seed",
    "resolve_config",
    "run_serial_elbow_arm_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
