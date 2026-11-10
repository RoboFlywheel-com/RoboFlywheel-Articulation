# SPDX-License-Identifier: Apache-2.0

"""Source-faithful hand-cranked sheet pasta makers on one shared chrome frame.

Every mechanism region of source 001 is a slot: the -X drive cheek carries the
transmission, the +X socket carries the crank, the -X lower boss carries the
thickness selector, the rear-top cradle carries the cutter stage, the bore column
carries N feed rollers and the base underside carries N table clamps.  The host
adapts locally to each choice; no combination is excluded.
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
    Sphere,
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

Transmission = Literal["open_pinion_pair", "exposed_twin_spur", "enclosed_gear_case"]
Crank = Literal["rigid_offset_crank", "folding_two_link_crank"]
ThicknessAdjust = Literal["fluted_rotary_dial", "indexed_detent_lever"]
CutterStage = Literal["fixed_twin_cutter", "removable_cassette", "single_narrow_module"]
FeedRollers = Literal["smooth_nip_roller"]
ClampScrews = Literal["tommy_bar_screw_clamp"]


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "transmission",
            ("open_pinion_pair", "exposed_twin_spur", "enclosed_gear_case"),
            role="source-backed crank-to-roller transmission on the -X drive cheek",
        ),
        component_slot(
            "crank",
            ("rigid_offset_crank", "folding_two_link_crank"),
            role="source-backed removable hand crank on the +X socket",
        ),
        component_slot(
            "thickness_adjust",
            ("fluted_rotary_dial", "indexed_detent_lever"),
            role="source-backed sheet-thickness selector on the -X lower boss",
        ),
        component_slot(
            "cutter_stage",
            ("fixed_twin_cutter", "removable_cassette", "single_narrow_module"),
            role="source-backed rear-top cutter stage and its host cradle",
        ),
        component_slot(
            "feed_rollers",
            ("smooth_nip_roller",),
            role="source-backed indexed sheet roller in the shared bore column",
        ),
        component_slot(
            "clamp_screws",
            ("tommy_bar_screw_clamp",),
            role="source-backed indexed under-frame table clamp",
        ),
        multiplicity_slot("feed_roller_count", (2, 3), item_slot="feed_rollers"),
        multiplicity_slot("clamp_screw_count", (1, 2), item_slot="clamp_screws"),
    )
)


@dataclass(frozen=True)
class Config:
    transmission: Transmission = "open_pinion_pair"
    crank: Crank = "rigid_offset_crank"
    thickness_adjust: ThicknessAdjust = "fluted_rotary_dial"
    cutter_stage: CutterStage = "fixed_twin_cutter"
    feed_rollers: FeedRollers = "smooth_nip_roller"
    clamp_screws: ClampScrews = "tommy_bar_screw_clamp"
    feed_roller_count: int = 2
    clamp_screw_count: int = 1
    scale: float = 1.0
    roller_radius_m: float = 0.0150
    nip_gap_m: float = 0.0040
    crank_reach_m: float = 0.0480
    grip_length_m: float = 0.0500
    disc_pitch_m: float = 0.0060
    cassette_lift_m: float = 0.0600
    fold_link_ratio: float = 0.50
    pinion_teeth: int = 18
    spur_teeth: int = 17
    dial_flutes: int = 32
    lever_detent_count: int = 7
    gear_case_depth_m: float = 0.0240
    clamp_drop_m: float = 0.0640
    name: str = "hand_operated_pasta_maker_with_rollers_and_crank"


@dataclass(frozen=True)
class ResolvedConfig:
    transmission: Transmission
    crank: Crank
    thickness_adjust: ThicknessAdjust
    cutter_stage: CutterStage
    feed_rollers: FeedRollers
    clamp_screws: ClampScrews
    feed_roller_count: int
    clamp_screw_count: int
    scale: float
    roller_radius_m: float
    nip_gap_m: float
    crank_reach_m: float
    grip_length_m: float
    disc_pitch_m: float
    cassette_lift_m: float
    fold_link_ratio: float
    pinion_teeth: int
    spur_teeth: int
    dial_flutes: int
    lever_detent_count: int
    gear_case_depth_m: float
    clamp_drop_m: float
    roller_r_m: float
    nip_center_distance_m: float
    idler_stack_height_m: float
    feed_axes_m: tuple[tuple[float, float], ...]
    feed_column_top_m: float
    cheek_front_peak_m: float
    cheek_rear_peak_m: float
    guard_z_m: float
    cutter_z_m: float
    cutter_disc_radius_m: float
    cutter_center_distance_m: float
    cutter_y0_m: float
    cutter_y1_m: float
    cassette_y_m: float
    module_y_m: float
    module_z_m: float
    rail_length_m: float
    nip_z_m: float
    adjust_y_m: float
    adjust_z_m: float
    socket_x_m: float
    clamp_x_m: tuple[float, ...]
    clamp_jaw_z_m: float
    spur_module_m: float
    case_front_x_m: float
    case_back_x_m: float
    case_y_lo_m: float
    case_y_hi_m: float
    case_z_lo_m: float
    case_z_hi_m: float
    cover_open_rad: float
    fold_sweep_rad: float
    lever_arc_rad: float
    dial_sweep_rad: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x5041_5354_4131)
    return Config(
        transmission=choices["transmission"],
        crank=choices["crank"],
        thickness_adjust=choices["thickness_adjust"],
        cutter_stage=choices["cutter_stage"],
        feed_rollers=choices["feed_rollers"],
        clamp_screws=choices["clamp_screws"],
        feed_roller_count=int(choices["feed_roller_count"]),
        clamp_screw_count=int(choices["clamp_screw_count"]),
        scale=round(rng.uniform(0.92, 1.10), 4),
        roller_radius_m=round(rng.uniform(0.0130, 0.0170), 5),
        nip_gap_m=round(rng.uniform(0.0020, 0.0060), 5),
        crank_reach_m=round(rng.uniform(0.038, 0.058), 5),
        grip_length_m=round(rng.uniform(0.040, 0.058), 5),
        disc_pitch_m=round(rng.uniform(0.0045, 0.0075), 5),
        cassette_lift_m=round(rng.uniform(0.045, 0.075), 5),
        fold_link_ratio=round(rng.uniform(0.40, 0.62), 4),
        pinion_teeth=rng.choice((16, 18, 20)),
        spur_teeth=rng.choice((15, 17, 19)),
        dial_flutes=rng.choice((24, 28, 32)),
        lever_detent_count=rng.choice((5, 7, 9)),
        gear_case_depth_m=round(rng.uniform(0.020, 0.030), 5),
        clamp_drop_m=round(rng.uniform(0.055, 0.075), 5),
        name=f"hand_operated_pasta_maker_seed_{seed}",
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, str]:
    return {
        "transmission": config.transmission,
        "crank": config.crank,
        "thickness_adjust": config.thickness_adjust,
        "cutter_stage": config.cutter_stage,
        "feed_rollers": config.feed_rollers,
        "clamp_screws": config.clamp_screws,
    }


def slot_choices_for_seed(seed: int) -> dict[str, str]:
    return slot_choices_for_config(config_from_seed(seed))


def _range(name: str, value: float, low: float, high: float) -> float:
    value = float(value)
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}], got {value}")
    return value


def _choice(name: str, value: int, allowed: tuple[int, ...]) -> int:
    value = int(value)
    if value not in allowed:
        raise ValueError(f"{name} must be one of {allowed}, got {value}")
    return value


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "transmission": config.transmission,
            "crank": config.crank,
            "thickness_adjust": config.thickness_adjust,
            "cutter_stage": config.cutter_stage,
            "feed_rollers": config.feed_rollers,
            "clamp_screws": config.clamp_screws,
            "feed_roller_count": int(config.feed_roller_count),
            "clamp_screw_count": int(config.clamp_screw_count),
        }
    )
    s = _range("scale", config.scale, 0.92, 1.10)
    roller_radius = _range("roller_radius_m", config.roller_radius_m, 0.0130, 0.0170)
    nip_gap = _range("nip_gap_m", config.nip_gap_m, 0.0020, 0.0060)
    reach = _range("crank_reach_m", config.crank_reach_m, 0.038, 0.058)
    grip_length = _range("grip_length_m", config.grip_length_m, 0.040, 0.058)
    disc_pitch = _range("disc_pitch_m", config.disc_pitch_m, 0.0045, 0.0075)
    cassette_lift = _range("cassette_lift_m", config.cassette_lift_m, 0.045, 0.075)
    fold_ratio = _range("fold_link_ratio", config.fold_link_ratio, 0.40, 0.62)
    gear_case_depth = _range("gear_case_depth_m", config.gear_case_depth_m, 0.020, 0.030)
    clamp_drop = _range("clamp_drop_m", config.clamp_drop_m, 0.055, 0.075)
    pinion_teeth = _choice("pinion_teeth", config.pinion_teeth, (16, 18, 20))
    spur_teeth = _choice("spur_teeth", config.spur_teeth, (15, 17, 19))
    dial_flutes = _choice("dial_flutes", config.dial_flutes, (24, 28, 32))
    detents = _choice("lever_detent_count", config.lever_detent_count, (5, 7, 9))
    feed_n = _choice("feed_roller_count", config.feed_roller_count, (2, 3))
    clamp_n = _choice("clamp_screw_count", config.clamp_screw_count, (1, 2))

    roller_r = roller_radius * s
    nip_gap_s = nip_gap * s
    centre = 2.0 * roller_r + nip_gap_s
    stack = math.sqrt(max((2.0 * roller_r + 0.001 * s) ** 2 - (centre / 2.0) ** 2, 1e-9))

    nip_z = 0.126 * s
    y_mid = -0.007 * s
    axes: list[tuple[float, float]] = [
        (y_mid - centre / 2.0, nip_z),
        (y_mid + centre / 2.0, nip_z),
    ]
    for k in range(2, feed_n):
        axes.append((y_mid, nip_z + (k - 1) * stack))
    column_top = max(z for _y, z in axes) + roller_r

    cheek_front_peak = max(0.154 * s, column_top + 0.008 * s)
    cheek_rear_peak = max(0.166 * s, column_top + 0.004 * s)
    guard_z = cheek_rear_peak - 0.003 * s
    cutter_z = guard_z - 0.022 * s

    disc_r = 0.70 * roller_r
    cutter_cd = 2.0 * disc_r + 0.005 * s
    cutter_y0 = 0.036 * s
    cutter_y1 = cutter_y0 + cutter_cd
    cassette_y = cutter_y0 + cutter_cd / 2.0
    module_y = cassette_y
    module_z = cutter_z - 0.008 * s
    rail_length = 0.014 * s + 0.35 * cassette_lift * s

    adjust_y = -0.058 * s
    adjust_z = 0.087 * s
    socket_x = 0.100 * s

    if clamp_n == 1:
        clamp_x = (0.056 * s,)
    else:
        half = 0.045 * s
        clamp_x = tuple(-half + 2.0 * half * i / (clamp_n - 1) for i in range(clamp_n))
    clamp_jaw_z = (0.014 - clamp_drop) * s

    # 1.5% module shrink plus real backlash keeps the meshed flanks clear.
    spur_module = 0.985 * centre / spur_teeth

    case_depth = gear_case_depth * s
    case_front_x = -0.101 * s - case_depth
    case_back_x = -0.099 * s
    case_y_lo = axes[0][0] - 0.024 * s
    case_y_hi = axes[1][0] + 0.024 * s
    case_z_lo = nip_z - 0.009 * s
    case_z_hi = column_top + 0.006 * s

    # The fold stops when the outer link's near end would reach the inner
    # link's near end: both rods are 0.0042 thick and keep 1.4 mm of air.
    inner_link = reach * fold_ratio * s
    near_outer = 0.010 * s
    near_inner = max(0.5 * inner_link, 0.007 * s)
    clearance = 0.0098 * s
    cosine = (near_outer**2 + near_inner**2 - clearance**2) / (
        2.0 * near_outer * near_inner
    )
    fold_sweep = min(2.2, math.pi - math.acos(max(-1.0, min(1.0, cosine))))
    lever_arc = 0.175 * (detents - 1)
    dial_sweep = 0.36 * (dial_flutes / 4.0)

    return ResolvedConfig(
        transmission=config.transmission,
        crank=config.crank,
        thickness_adjust=config.thickness_adjust,
        cutter_stage=config.cutter_stage,
        feed_rollers=config.feed_rollers,
        clamp_screws=config.clamp_screws,
        feed_roller_count=feed_n,
        clamp_screw_count=clamp_n,
        scale=s,
        roller_radius_m=roller_radius,
        nip_gap_m=nip_gap,
        crank_reach_m=reach,
        grip_length_m=grip_length,
        disc_pitch_m=disc_pitch,
        cassette_lift_m=cassette_lift,
        fold_link_ratio=fold_ratio,
        pinion_teeth=pinion_teeth,
        spur_teeth=spur_teeth,
        dial_flutes=dial_flutes,
        lever_detent_count=detents,
        gear_case_depth_m=gear_case_depth,
        clamp_drop_m=clamp_drop,
        roller_r_m=roller_r,
        nip_center_distance_m=centre,
        idler_stack_height_m=stack,
        feed_axes_m=tuple(axes),
        feed_column_top_m=column_top,
        cheek_front_peak_m=cheek_front_peak,
        cheek_rear_peak_m=cheek_rear_peak,
        guard_z_m=guard_z,
        cutter_z_m=cutter_z,
        cutter_disc_radius_m=disc_r,
        cutter_center_distance_m=cutter_cd,
        cutter_y0_m=cutter_y0,
        cutter_y1_m=cutter_y1,
        cassette_y_m=cassette_y,
        module_y_m=module_y,
        module_z_m=module_z,
        rail_length_m=rail_length,
        nip_z_m=nip_z,
        adjust_y_m=adjust_y,
        adjust_z_m=adjust_z,
        socket_x_m=socket_x,
        clamp_x_m=clamp_x,
        clamp_jaw_z_m=clamp_jaw_z,
        spur_module_m=spur_module,
        case_front_x_m=case_front_x,
        case_back_x_m=case_back_x,
        case_y_lo_m=case_y_lo,
        case_y_hi_m=case_y_hi,
        case_z_lo_m=case_z_lo,
        case_z_hi_m=case_z_hi,
        cover_open_rad=1.60,
        fold_sweep_rad=fold_sweep,
        lever_arc_rad=lever_arc,
        dial_sweep_rad=dial_sweep,
        name=config.name,
    )


AXLE_R = 0.0046
COLLAR_IN = 0.0052
COLLAR_OUT = 0.0090
BORE_R = 0.0062
BODY_HALF = 0.080
# Every host cross member terminates in free air, never inside the cheek solid:
# a cap that stops part-way through another solid leaves an internal face and the
# fused frame tessellates non-manifold, which makes FCL fall back to a
# conservative backend and report phantom overlaps.
SPAN = 0.1045
SLEEVE_IN = 0.0845
SLEEVE_OUT = 0.1055


def _mesh(shape: cq.Workplane, name: str):
    return mesh_from_cadquery(shape, name, tolerance=0.00045, angular_tolerance=0.10)


def _add_visual(part, shape: cq.Workplane, material, name: str) -> None:
    part.visual(_mesh(shape, f"pasta_maker_{name}"), material=material, name=name, material_class_id="metal.generic_plain")


def _materials(model: ArticulatedObject) -> dict[str, object]:
    return {
        "chrome": model.material("pasta_maker_chrome", rgba=(0.76, 0.79, 0.82, 1.0)),
        "polished": model.material("pasta_maker_polished_steel", rgba=(0.90, 0.92, 0.94, 1.0)),
        "dark": model.material("pasta_maker_dark_steel", rgba=(0.15, 0.16, 0.17, 1.0)),
        "black": model.material("pasta_maker_black_grip", rgba=(0.025, 0.030, 0.035, 1.0)),
    }


def _x_bar(x0: float, x1: float, y: float, z: float, radius: float) -> cq.Workplane:
    return (
        cq.Workplane("YZ")
        .center(y, z)
        .circle(radius)
        .extrude(x1 - x0)
        .translate((x0, 0.0, 0.0))
    )


def _x_ring(x0: float, length: float, y: float, z: float, outer: float, inner: float):
    return (
        cq.Workplane("YZ")
        .center(y, z)
        .circle(outer)
        .circle(inner)
        .extrude(length)
        .translate((x0, 0.0, 0.0))
    )


def _bent_rod(p0, p1, radius: float) -> cq.Workplane:
    direction = tuple(p1[i] - p0[i] for i in range(3))
    length = math.sqrt(sum(v * v for v in direction))
    plane = cq.Plane(origin=p0, normal=direction)
    return cq.Workplane(plane).circle(radius).extrude(length)


def _pinion(radius: float, width: float, x_center: float, teeth: int) -> cq.Workplane:
    points = []
    for i in range(teeth * 2):
        angle = math.tau * i / (teeth * 2)
        r = radius if i % 2 == 0 else radius * 0.86
        points.append((r * math.cos(angle), r * math.sin(angle)))
    return (
        cq.Workplane("YZ")
        .polyline(points)
        .close()
        .extrude(width / 2.0, both=True)
        .translate((x_center, 0.0, 0.0))
    )


def _cheek_profile(r: ResolvedConfig) -> list[tuple[float, float]]:
    s = r.scale
    y_rt = min(0.075 * s, max(0.030 * s, r.cutter_y1_m + 0.008 * s))
    return [
        (-0.074 * s, 0.004 * s),
        (0.078 * s, 0.004 * s),
        (0.078 * s, r.cutter_z_m - 0.006 * s),
        (y_rt, r.cheek_rear_peak_m - 0.006 * s),
        (0.018 * s, r.cheek_rear_peak_m),
        (-0.046 * s, r.cheek_front_peak_m),
        (-0.074 * s, 0.119 * s),
    ]


def _host_bore_centers(r: ResolvedConfig) -> list[tuple[float, float]]:
    centers = [(y, z) for y, z in r.feed_axes_m]
    centers.append((r.adjust_y_m, r.adjust_z_m))
    if r.cutter_stage == "fixed_twin_cutter":
        centers.append((r.cutter_y0_m, r.cutter_z_m))
        centers.append((r.cutter_y1_m, r.cutter_z_m))
    elif r.cutter_stage == "single_narrow_module":
        centers.append((r.module_y_m, r.module_z_m))
    return centers


def _collar_positions(r: ResolvedConfig) -> list[tuple[float, float]]:
    positions = [(y, z) for y, z in r.feed_axes_m]
    if r.cutter_stage == "fixed_twin_cutter":
        positions.append((r.cutter_y0_m, r.cutter_z_m))
        positions.append((r.cutter_y1_m, r.cutter_z_m))
    elif r.cutter_stage == "single_narrow_module":
        positions.append((r.module_y_m, r.module_z_m))
    return positions


def _cutter_host_adaptation(frame: cq.Workplane, r: ResolvedConfig) -> cq.Workplane:
    """Rewrite the rear-top host region for the selected cutter stage."""
    s = r.scale
    if r.cutter_stage == "fixed_twin_cutter":
        return frame.union(
            cq.Workplane("XY")
            .box(2.0 * SPAN * s, 0.010 * s, 0.006 * s)
            .translate((0.0, r.cutter_y1_m, r.guard_z_m))
        )
    if r.cutter_stage == "single_narrow_module":
        frame = frame.union(
            cq.Workplane("XY")
            .box(2.0 * SPAN * s, 0.010 * s, 0.006 * s)
            .translate((0.0, r.module_y_m + 0.016 * s, r.guard_z_m))
        )
        frame = frame.union(
            cq.Workplane("XY")
            .box(2.0 * SPAN * s, 0.010 * s, 0.004 * s)
            .translate(
                (
                    0.0,
                    r.module_y_m - 0.014 * s,
                    r.module_z_m - r.cutter_disc_radius_m - 0.005 * s,
                )
            )
        )
        return frame.union(
            _x_bar(
                -SPAN * s,
                SPAN * s,
                r.module_y_m,
                r.module_z_m + r.cutter_disc_radius_m + 0.006 * s,
                0.004 * s,
            )
        )
    # removable_cassette: no bores and no closed bridge, four keyed rail channels
    # emitted as ribs that pass right through the cheek.
    centre = 0.5 * (SLEEVE_IN + SLEEVE_OUT) * s
    depth = (SLEEVE_OUT - SLEEVE_IN) * s
    for y_c in (r.cutter_y0_m, r.cutter_y1_m):
        for side in (-1.0, 1.0):
            for offset in (-0.009 * s, 0.009 * s):
                frame = frame.union(
                    cq.Workplane("XY")
                    .box(depth, 0.003 * s, r.rail_length_m)
                    .translate(
                        (
                            side * centre,
                            y_c + offset,
                            r.cutter_z_m - 0.012 * s + r.rail_length_m / 2.0,
                        )
                    )
                )
    return frame


def _gear_case_shape(r: ResolvedConfig) -> cq.Workplane | None:
    """The bolted gear shell is host geometry; only its cover articulates.

    It is emitted as its own frame visual rather than fused into the body: the
    shell floor can land a fraction of a millimetre from the cutter cradle shelf,
    and near-coplanar faces make the fused solid tessellate non-manifold.  As a
    separate element it stays watertight and still counts as connected, because it
    passes right through the cheek.

    The shell is a closed box whose inboard end passes through the cheek and
    becomes a solid bearing block, bored per feed-roller shaft.
    """
    if r.transmission != "enclosed_gear_case":
        return None
    s = r.scale
    back_x = -SLEEVE_IN * s
    front_x = r.case_front_x_m
    wall = 0.0025 * s
    dx = back_x - front_x
    dy = r.case_y_hi_m - r.case_y_lo_m
    dz = r.case_z_hi_m - r.case_z_lo_m
    cy = 0.5 * (r.case_y_lo_m + r.case_y_hi_m)
    cz = 0.5 * (r.case_z_lo_m + r.case_z_hi_m)
    shell = (
        cq.Workplane("XY").box(dx, dy, dz).translate((0.5 * (front_x + back_x), cy, cz))
    )
    cavity_front = front_x - 0.001 * s
    cavity_back = -0.1035 * s
    shell = shell.cut(
        cq.Workplane("XY")
        .box(cavity_back - cavity_front, dy - 2.0 * wall, dz - 2.0 * wall)
        .translate((0.5 * (cavity_front + cavity_back), cy, cz))
    )
    # Bored bearing passages through the solid inboard block, one per shaft.
    for y, z in r.feed_axes_m:
        shell = shell.cut(
            _x_bar(cavity_back - 0.002 * s, back_x + 0.002 * s, y, z, COLLAR_IN * s)
        )
    # The bolted joint is expressed by fastener heads emitted as separate frame
    # primitives (see build_*); a flange box would have to end inside the cheek.
    for offset in (-0.030 * s, 0.030 * s):
        shell = shell.union(
            _x_bar(
                front_x - 0.0060 * s,
                front_x + 0.0040 * s,
                cy + offset,
                r.case_z_hi_m,
                0.0035 * s,
            )
        )
    return shell


def _detent_plate_shape(r: ResolvedConfig) -> cq.Workplane | None:
    """Notched detent plate standing free outboard of the selector sleeve, tied
    back through the cheek by a rib placed outside the lever's swept sector.

    Emitted as its own frame visual for the same reason as the gear case: keeping
    it out of the fused body avoids near-coplanar faces there."""
    if r.thickness_adjust != "indexed_detent_lever":
        return None
    s = r.scale
    plate_x0 = -0.1120 * s
    plate = (
        cq.Workplane("YZ")
        .center(r.adjust_y_m, r.adjust_z_m)
        .circle(0.018 * s)
        .extrude(0.003 * s)
        .translate((plate_x0, 0.0, 0.0))
    )
    plate = plate.cut(
        cq.Workplane("YZ")
        .center(r.adjust_y_m, r.adjust_z_m)
        .circle(0.0060 * s)
        .extrude(0.012 * s, both=True)
        .translate((plate_x0, 0.0, 0.0))
    )
    start_angle = math.pi / 2.0
    for i in range(r.lever_detent_count):
        angle = start_angle + r.lever_arc_rad * i / max(r.lever_detent_count - 1, 1)
        plate = plate.cut(
            cq.Workplane("YZ")
            .center(
                r.adjust_y_m + 0.014 * s * math.cos(angle),
                r.adjust_z_m + 0.014 * s * math.sin(angle),
            )
            .circle(0.0035 * s)
            .extrude(0.010 * s, both=True)
            .translate((plate_x0, 0.0, 0.0))
        )
    tab_x0 = plate_x0
    tab_x1 = -SLEEVE_IN * s
    plate = plate.union(
        cq.Workplane("XY")
        .box(tab_x1 - tab_x0, 0.008 * s, 0.008 * s)
        .translate(
            (
                0.5 * (tab_x0 + tab_x1),
                r.adjust_y_m + 0.0115 * s,
                r.adjust_z_m + 0.0115 * s,
            )
        )
    )
    return plate


def _clamp_host_adaptation(frame: cq.Workplane, r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    drop = r.clamp_drop_m * s
    y_cl = 0.055 * s
    top = 0.011 * s
    for x_c in r.clamp_x_m:
        bracket = (
            cq.Workplane("XY")
            .box(0.024 * s, 0.020 * s, drop)
            .translate((x_c, y_cl, top - drop / 2.0))
        )
        jaw = (
            cq.Workplane("XY")
            .box(0.044 * s, 0.030 * s, 0.012 * s)
            .translate((x_c, y_cl, r.clamp_jaw_z_m))
        )
        bore_bottom = r.clamp_jaw_z_m - 0.014 * s
        bore_top = 0.012 * s
        hole = (
            cq.Workplane("XY")
            .center(x_c, y_cl)
            .circle(0.0050 * s)
            .extrude(bore_top - bore_bottom)
            .translate((0.0, 0.0, bore_bottom))
        )
        frame = frame.union(bracket).union(jaw).cut(hole)
    return frame


def _frame_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    frame = (
        cq.Workplane("XY")
        .box(0.215 * s, 0.170 * s, 0.008 * s)
        .translate((0.0, 0.0, 0.004 * s))
    )

    blank = cq.Workplane("YZ").polyline(_cheek_profile(r)).close().extrude(0.007 * s, both=True)
    for y, z in _host_bore_centers(r):
        blank = blank.cut(
            cq.Workplane("YZ").center(y, z).circle(BORE_R * s).extrude(0.030 * s, both=True)
        )
    frame = frame.union(blank.translate((-0.094 * s, 0.0, 0.0)))
    frame = frame.union(blank.translate((0.094 * s, 0.0, 0.0)))

    # Polished front apron with its rolled lip, plus the structural rails.
    frame = frame.union(
        cq.Workplane("XY")
        .box(2.0 * SPAN * s, 0.010 * s, 0.086 * s)
        .translate((0.0, -0.064 * s, 0.083 * s))
    )
    frame = frame.union(_x_bar(-SPAN * s, SPAN * s, -0.062 * s, 0.133 * s, 0.006 * s))
    frame = frame.union(
        cq.Workplane("XY")
        .box(2.0 * SPAN * s, 0.018 * s, 0.026 * s)
        .translate((0.0, 0.059 * s, 0.025 * s))
    )
    rail_z = min(0.153 * s, r.cheek_front_peak_m - 0.008 * s)
    frame = frame.union(_x_bar(-SPAN * s, SPAN * s, -0.052 * s, rail_z, 0.005 * s))

    # Rear retention ears: through ribs on both cheeks, centre left open so a
    # cassette can be lifted straight out.
    if r.cutter_stage != "removable_cassette":
        ear_centre = 0.5 * (SLEEVE_IN + SLEEVE_OUT) * s
        ear_depth = (SLEEVE_OUT - SLEEVE_IN) * s
        for side in (-1.0, 1.0):
            frame = frame.union(
                cq.Workplane("XY")
                .box(ear_depth, 0.038 * s, 0.006 * s)
                .translate((side * ear_centre, 0.047 * s, r.guard_z_m))
            )

    frame = _cutter_host_adaptation(frame, r)

    # Through bearing sleeves for every shaft the host itself journals.
    sleeve_len = (SLEEVE_OUT - SLEEVE_IN) * s
    y0, z0 = r.feed_axes_m[0]
    for y, z in _collar_positions(r):
        if r.transmission != "enclosed_gear_case" or (y, z) not in r.feed_axes_m:
            frame = frame.union(
                _x_ring(-SLEEVE_OUT * s, sleeve_len, y, z, COLLAR_OUT * s, COLLAR_IN * s)
            )
        if (y, z) != (y0, z0):
            frame = frame.union(
                _x_ring(SLEEVE_IN * s, sleeve_len, y, z, COLLAR_OUT * s, COLLAR_IN * s)
            )

    # Hollow removable-crank socket sleeve and the thickness-selector sleeve.
    frame = frame.union(
        _x_ring(SLEEVE_IN * s, (0.114 - SLEEVE_IN) * s, y0, z0, 0.0100 * s, 0.0048 * s)
    )
    frame = frame.union(
        _x_ring(
            -SLEEVE_OUT * s, sleeve_len, r.adjust_y_m, r.adjust_z_m, 0.0100 * s, 0.0058 * s
        )
    )

    frame = _clamp_host_adaptation(frame, r)
    return frame


def _feed_rollers_smooth_nip_roller_build(
    model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, object], index: int
):
    s = r.scale
    part = model.part(
        f"feed_roller_{index}",
        meta={"role": "feed_roller", "feed_index": index, "driven": index == 0},
    )
    body = cq.Workplane("YZ").circle(r.roller_r_m).extrude(BODY_HALF * s, both=True)
    axle = (
        cq.Workplane("YZ")
        .circle(AXLE_R * s)
        .extrude(0.206 * s)
        .translate((-0.114 * s, 0.0, 0.0))
    )
    _add_visual(
        part,
        body.union(axle),
        mats["polished"],
        f"feed_rollers__smooth_nip_roller__shaft_{index}",
    )
    if r.transmission in {"open_pinion_pair", "enclosed_gear_case"}:
        _add_visual(
            part,
            _pinion(1.08 * r.roller_r_m, 0.006 * s, -0.112 * s, r.pinion_teeth),
            mats["dark"],
            f"feed_rollers__smooth_nip_roller__pinion_{index}",
        )
    return part


def _involute_tooth_profile(
    *, module: float, teeth: int, backlash: float, pressure_angle: float = 0.349066
) -> list[tuple[float, float]]:
    """Closed involute spur-gear profile in the YZ plane.

    The source fork used `SpurGear`, whose solid tessellates non-manifold and
    therefore forces the collision backend into its conservative fallback.  This
    keeps the same involute flank geometry (identical module, tooth count,
    pressure angle, addendum and dedendum) but emits it as one closed polyline so
    the extruded prism is watertight.
    """
    pitch_r = module * teeth / 2.0
    base_r = pitch_r * math.cos(pressure_angle)
    tip_r = pitch_r + module
    root_r = max(pitch_r - 1.25 * module, 0.35 * pitch_r)

    def involute(radius: float) -> float:
        if radius <= base_r:
            return 0.0
        ratio = min(1.0, base_r / radius)
        return math.sqrt((radius / base_r) ** 2 - 1.0) - math.acos(ratio)

    inv_pitch = involute(pitch_r)
    half_angle = math.pi / (2.0 * teeth) - backlash / (2.0 * pitch_r)
    flank_start = max(base_r, root_r) * 1.0002
    samples = 5
    radii = [
        flank_start + (tip_r - flank_start) * i / (samples - 1) for i in range(samples)
    ]

    step = math.tau / teeth
    root_limit = 0.44 * step

    def half_width(radius: float) -> float:
        return min(root_limit, half_angle - (involute(radius) - inv_pitch))

    raw: list[tuple[float, float]] = []
    for index in range(teeth):
        phi = index * step
        angles_radii = [(phi - half_width(flank_start), root_r)]
        angles_radii += [(phi - half_width(rad), rad) for rad in radii]
        angles_radii += [(phi + half_width(rad), rad) for rad in reversed(radii)]
        angles_radii += [(phi + half_width(flank_start), root_r)]
        angles_radii += [(phi + step / 2.0, root_r)]
        for angle, radius in angles_radii:
            raw.append((radius * math.cos(angle), radius * math.sin(angle)))

    points: list[tuple[float, float]] = []
    for point in raw:
        if points and math.dist(points[-1], point) < 1e-7:
            continue
        points.append(point)
    if len(points) > 1 and math.dist(points[0], points[-1]) < 1e-7:
        points.pop()
    return points


def _spur_gear_shape(r: ResolvedConfig, *, driven: bool) -> cq.Workplane:
    s = r.scale
    points = _involute_tooth_profile(
        module=r.spur_module_m, teeth=r.spur_teeth, backlash=0.0006 * s
    )
    if driven:
        # Half-tooth clocking so the flanks interleave instead of butting tip to tip.
        clock = math.pi / r.spur_teeth
        cos_c, sin_c = math.cos(clock), math.sin(clock)
        points = [(y * cos_c - z * sin_c, y * sin_c + z * cos_c) for y, z in points]
    body = (
        cq.Workplane("YZ").polyline(points).close().extrude(0.003 * s, both=True)
    )
    hub = _x_ring(0.001 * s, 0.008 * s, 0.0, 0.0, 0.0125 * s, 0.0052 * s)
    shape = body.union(hub)
    return shape.cut(_x_bar(-0.006 * s, 0.012 * s, 0.0, 0.0, 0.0052 * s))


def _transmission_open_pinion_pair_build(model, r, mats):
    """Pinions are visuals of the rollers they drive; nothing else is emitted."""
    return []


def _transmission_exposed_twin_spur_build(model, r, mats):
    extra = []
    for index, driven in enumerate((False, True)):
        part = model.part(
            f"transmission_gear_{index}",
            meta={"role": "transmission_gear", "gear_index": index, "driven": driven},
        )
        _add_visual(
            part,
            _spur_gear_shape(r, driven=driven),
            mats["dark"],
            f"transmission__exposed_twin_spur__gear_{index}",
        )
        extra.append(part)
    return extra


def _transmission_enclosed_gear_case_build(model, r, mats):
    """Shell is frame geometry (bolted rigid); only the access cover articulates."""
    s = r.scale
    cover = model.part("gear_case_cover", meta={"role": "gear_case_cover"})
    panel_h = (r.case_z_hi_m - r.case_z_lo_m) + 0.004 * s
    panel_w = (r.case_y_hi_m - r.case_y_lo_m) + 0.006 * s
    panel = (
        cq.Workplane("XY")
        .box(0.002 * s, panel_w, panel_h)
        .translate((-0.001 * s, 0.0, -panel_h / 2.0 - 0.002 * s))
    )
    for offset in (-0.010 * s, 0.010 * s):
        panel = panel.union(_x_bar(-0.0025 * s, 0.0025 * s, offset, 0.0, 0.0035 * s))
    panel = panel.union(
        cq.Workplane("XY")
        .box(0.006 * s, 0.018 * s, 0.010 * s)
        .translate((-0.004 * s, 0.0, -panel_h + 0.003 * s))
    )
    _add_visual(cover, panel, mats["chrome"], "transmission__enclosed_gear_case__cover")
    return [cover]


_TRANSMISSION_BUILDERS = {
    "open_pinion_pair": _transmission_open_pinion_pair_build,
    "exposed_twin_spur": _transmission_exposed_twin_spur_build,
    "enclosed_gear_case": _transmission_enclosed_gear_case_build,
}


def _grip_part(model, r: ResolvedConfig, mats):
    s = r.scale
    grip = model.part("crank_grip", meta={"role": "free_spinning_grip"})
    grip.visual(
        Cylinder(radius=0.009 * s, length=r.grip_length_m * s),
        origin=Origin(
            xyz=(r.grip_length_m * s / 2.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)
        ),
        material=mats["black"],
        name="crank__grip_barrel", material_class_id="plastic.opaque_glossy_molded",
    )
    grip.visual(
        Sphere(radius=0.009 * s),
        origin=Origin(xyz=(r.grip_length_m * s, 0.0, 0.0)),
        material=mats["black"],
        name="crank__grip_end", material_class_id="plastic.opaque_glossy_molded",
    )
    return grip


def _crank_rigid_offset_crank_build(model, r: ResolvedConfig, mats):
    s = r.scale
    reach = r.crank_reach_m * s
    tip = (0.032 * s, reach * 0.866, -reach * 0.5)
    crank = model.part("crank", meta={"role": "manual_drive", "crank_type": "rigid"})
    shape = _bent_rod((-0.001 * s, 0.0, 0.0), (0.032 * s, 0.0, 0.0), 0.0042 * s)
    shape = shape.union(_bent_rod((0.032 * s, 0.0, 0.0), tip, 0.0042 * s))
    shape = shape.union(_bent_rod(tip, (tip[0] + 0.012 * s, tip[1], tip[2]), 0.0038 * s))
    _add_visual(crank, shape, mats["chrome"], "crank__rigid_offset_crank__arm")
    grip = _grip_part(model, r, mats)
    return crank, None, grip, (tip[0] + 0.012 * s, tip[1], tip[2]), None


def _crank_folding_two_link_crank_build(model, r: ResolvedConfig, mats):
    """Two-link crank whose fold pivot is a real clevis: two inner cheeks
    straddle a bored outer eye, and a pin journals through both."""
    s = r.scale
    reach = r.crank_reach_m * s
    inner_len = reach * r.fold_link_ratio
    outer_len = reach - inner_len
    uy, uz = 0.866, -0.5
    bend = (0.026 * s, 0.0, 0.0)
    pivot = (0.026 * s, inner_len * uy, inner_len * uz)
    leg_start_r = 0.5 * inner_len
    leg_start = (0.026 * s, leg_start_r * uy, leg_start_r * uz)

    inner = model.part(
        "crank", meta={"role": "manual_drive", "crank_type": "folding_inner_link"}
    )
    shape = _bent_rod((-0.001 * s, 0.0, 0.0), bend, 0.0042 * s)
    shape = shape.union(_bent_rod(bend, leg_start, 0.0042 * s))
    # Clevis legs and their pivot bosses, both offset clear of the eye band.
    for side in (-1.0, 1.0):
        offset = side * 0.0055 * s
        shape = shape.union(
            _bent_rod(
                (leg_start[0] + offset, leg_start[1], leg_start[2]),
                (pivot[0] + offset, pivot[1], pivot[2]),
                0.0022 * s,
            )
        )
        lo = pivot[0] + (0.0033 * s if side > 0 else -0.0077 * s)
        shape = shape.union(_x_bar(lo, lo + 0.0044 * s, pivot[1], pivot[2], 0.0068 * s))
    _add_visual(inner, shape, mats["chrome"], "crank__folding_two_link_crank__inner")
    inner.visual(
        Cylinder(radius=0.0025 * s, length=0.018 * s),
        origin=Origin(xyz=pivot, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["dark"],
        name="crank__folding_two_link_crank__pivot_pin", material_class_id="metal.blackened_gunmetal",
    )

    outer = model.part(
        "crank_outer",
        meta={"role": "folding_drive_arm", "crank_type": "folding_outer_link"},
    )
    tip = (0.0, outer_len * uy, outer_len * uz)
    neck_start = (0.0, 0.0045 * s * uy, 0.0045 * s * uz)
    rod_start = (0.0, 0.010 * s * uy, 0.010 * s * uz)
    outer_shape = _x_ring(-0.0024 * s, 0.0048 * s, 0.0, 0.0, 0.0055 * s, 0.0031 * s)
    outer_shape = outer_shape.union(_bent_rod(neck_start, rod_start, 0.0024 * s))
    outer_shape = outer_shape.union(_bent_rod(rod_start, tip, 0.0042 * s))
    outer_shape = outer_shape.union(
        _bent_rod(tip, (tip[0] + 0.012 * s, tip[1], tip[2]), 0.0038 * s)
    )
    _add_visual(outer, outer_shape, mats["chrome"], "crank__folding_two_link_crank__outer")
    grip = _grip_part(model, r, mats)
    return inner, outer, grip, (tip[0] + 0.012 * s, tip[1], tip[2]), pivot


_CRANK_BUILDERS = {
    "rigid_offset_crank": _crank_rigid_offset_crank_build,
    "folding_two_link_crank": _crank_folding_two_link_crank_build,
}


def _thickness_adjust_fluted_rotary_dial_build(model, r: ResolvedConfig, mats):
    s = r.scale
    dial = model.part(
        "thickness_selector",
        meta={"role": "thickness_selector", "selector_type": "rotary_dial"},
    )
    points = []
    for i in range(r.dial_flutes):
        angle = math.tau * i / r.dial_flutes
        radius = 0.021 * s if i % 2 == 0 else 0.019 * s
        points.append((radius * math.cos(angle), radius * math.sin(angle)))
    knob = (
        cq.Workplane("YZ")
        .polyline(points)
        .close()
        .extrude(0.022 * s)
        .translate((-0.022 * s, 0.0, 0.0))
    )
    stem = (
        cq.Workplane("YZ")
        .circle(0.0052 * s)
        .extrude(0.018 * s)
        .translate((-0.002 * s, 0.0, 0.0))
    )
    face = (
        cq.Workplane("YZ")
        .circle(0.015 * s)
        .extrude(0.003 * s)
        .translate((-0.0245 * s, 0.0, 0.0))
    )
    _add_visual(
        dial,
        knob.union(stem).union(face),
        mats["chrome"],
        "thickness_adjust__fluted_rotary_dial__knob",
    )
    dial.visual(
        Sphere(radius=0.0023 * s),
        origin=Origin(xyz=(-0.024 * s, 0.0, 0.012 * s)),
        material=mats["dark"],
        name="thickness_adjust__fluted_rotary_dial__index_marker", material_class_id="metal.blackened_gunmetal",
    )
    return dial, MotionLimits(
        effort=8.0, velocity=2.0, lower=-r.dial_sweep_rad, upper=r.dial_sweep_rad
    )


def _thickness_adjust_indexed_detent_lever_build(model, r: ResolvedConfig, mats):
    """Lever local frame: +X points inboard toward the selector boss, so every
    element sits outboard of the frame detent plate except the captive stem."""
    s = r.scale
    lever = model.part(
        "thickness_selector",
        meta={
            "role": "thickness_selector",
            "selector_type": "detent_lever",
            "detents": r.lever_detent_count,
        },
    )
    # Captive stem: press fit in the boss bore, running clearance in the plate bore.
    stem = (
        cq.Workplane("YZ")
        .circle(0.0052 * s)
        .extrude(0.020 * s)
        .translate((-0.0060 * s, 0.0, 0.0))
    )
    hub = (
        cq.Workplane("YZ")
        .circle(0.013 * s)
        .extrude(0.0055 * s)
        .translate((-0.0110 * s, 0.0, 0.0))
    )
    arm = (
        cq.Workplane("XY")
        .box(0.007 * s, 0.003 * s, 0.048 * s)
        .translate((-0.00825 * s, 0.0, -0.024 * s))
    )
    grip = (
        cq.Workplane("XY")
        .box(0.014 * s, 0.008 * s, 0.012 * s)
        .translate((-0.00825 * s, 0.0, -0.044 * s))
    )
    # Detent pin on the hub face at the scallop radius; at joint value 0 it sits
    # in the first notch and at the upper limit in the last one.
    pin = (
        cq.Workplane("YZ")
        .center(0.0, 0.014 * s)
        .circle(0.0028 * s)
        .extrude(0.0050 * s)
        .translate((-0.0060 * s, 0.0, 0.0))
    )
    _add_visual(
        lever,
        stem.union(hub).union(arm).union(grip).union(pin),
        mats["chrome"],
        "thickness_adjust__indexed_detent_lever__lever",
    )
    return lever, MotionLimits(effort=10.0, velocity=2.0, lower=0.0, upper=r.lever_arc_rad)


_THICKNESS_BUILDERS = {
    "fluted_rotary_dial": _thickness_adjust_fluted_rotary_dial_build,
    "indexed_detent_lever": _thickness_adjust_indexed_detent_lever_build,
}


def _cutter_shaft(
    r: ResolvedConfig, *, half_len: float, axle_x0: float, axle_x1: float
) -> cq.Workplane:
    s = r.scale
    disc_r = r.cutter_disc_radius_m
    core = cq.Workplane("YZ").circle(0.78 * disc_r).extrude(half_len, both=True)
    axle = (
        cq.Workplane("YZ")
        .circle(AXLE_R * s)
        .extrude(axle_x1 - axle_x0)
        .translate((axle_x0, 0.0, 0.0))
    )
    shape = core.union(axle)
    pitch = r.disc_pitch_m * s
    usable = 2.0 * half_len - 0.006 * s
    count = max(6, int(usable / pitch))
    span = (count - 1) * pitch
    for i in range(count):
        x = -span / 2.0 + i * pitch
        shape = shape.union(
            cq.Workplane("YZ")
            .circle(disc_r)
            .extrude(0.0008 * s, both=True)
            .translate((x, 0.0, 0.0))
        )
    return shape


def _cutter_stage_fixed_twin_cutter_build(model, r: ResolvedConfig, mats):
    s = r.scale
    rollers = []
    for index in range(2):
        part = model.part(
            f"cutter_roller_{index}",
            meta={"role": "cutter_roller", "cutter_index": index, "mount": "fixed_bore"},
        )
        _add_visual(
            part,
            _cutter_shaft(r, half_len=BODY_HALF * s, axle_x0=-0.092 * s, axle_x1=0.118 * s),
            mats["polished"],
            f"cutter_stage__fixed_twin_cutter__shaft_{index}",
        )
        _add_visual(
            part,
            _pinion(1.16 * r.cutter_disc_radius_m, 0.006 * s, 0.114 * s, 16),
            mats["dark"],
            f"cutter_stage__fixed_twin_cutter__pinion_{index}",
        )
        rollers.append(part)
    return None, rollers


def _cassette_frame_shape(r: ResolvedConfig) -> cq.Workplane:
    s = r.scale
    half = r.cutter_center_distance_m / 2.0
    plate_x = 0.082 * s
    side_t = 0.003 * s
    y_extent = r.cutter_center_distance_m + 0.020 * s
    z_extent = 0.040 * s
    shape = cq.Workplane("XY").box(side_t, y_extent, z_extent).translate((-plate_x, 0.0, 0.0))
    shape = shape.union(
        cq.Workplane("XY").box(side_t, y_extent, z_extent).translate((plate_x, 0.0, 0.0))
    )
    shape = shape.union(
        cq.Workplane("XY")
        .box(2.0 * plate_x, y_extent, 0.004 * s)
        .translate((0.0, 0.0, z_extent / 2.0 - 0.002 * s))
    )
    shape = shape.union(
        cq.Workplane("XY")
        .box(0.060 * s, 0.008 * s, 0.006 * s)
        .translate((0.0, 0.0, z_extent / 2.0 + 0.001 * s))
    )
    shape = shape.union(
        cq.Workplane("XY")
        .box(2.0 * plate_x, 0.003 * s, 0.010 * s)
        .translate((0.0, -(y_extent / 2.0 - 0.002 * s), -0.008 * s))
    )
    shape = shape.union(
        cq.Workplane("XY")
        .box(2.0 * plate_x, 0.003 * s, 0.010 * s)
        .translate((0.0, y_extent / 2.0 - 0.002 * s, -0.008 * s))
    )
    for y_c in (-half, half):
        for side in (-1.0, 1.0):
            shape = shape.union(
                cq.Workplane("XY")
                .box(0.003 * s, 0.0144 * s, 0.024 * s)
                .translate((side * 0.0850 * s, y_c, 0.0))
            )
    for y_c in (-half, half):
        shape = shape.cut(
            cq.Workplane("YZ")
            .center(y_c, 0.0)
            .circle(0.0052 * s)
            .extrude(0.120 * s, both=True)
        )
    return shape


def _cutter_stage_removable_cassette_build(model, r: ResolvedConfig, mats):
    s = r.scale
    cassette = model.part(
        "cutter_cassette", meta={"role": "cutter_cassette", "keyed_lift_out": True}
    )
    _add_visual(
        cassette,
        _cassette_frame_shape(r),
        mats["chrome"],
        "cutter_stage__removable_cassette__cartridge",
    )
    rollers = []
    for index in range(2):
        part = model.part(
            f"cutter_roller_{index}",
            meta={"role": "cutter_roller", "cutter_index": index, "mount": "cassette"},
        )
        _add_visual(
            part,
            _cutter_shaft(r, half_len=0.076 * s, axle_x0=-0.0835 * s, axle_x1=0.0835 * s),
            mats["polished"],
            f"cutter_stage__removable_cassette__shaft_{index}",
        )
        rollers.append(part)
    return cassette, rollers


def _cutter_stage_single_narrow_module_build(model, r: ResolvedConfig, mats):
    s = r.scale
    part = model.part(
        "cutter_roller_0",
        meta={"role": "cutter_roller", "cutter_index": 0, "mount": "single_cradle"},
    )
    _add_visual(
        part,
        _cutter_shaft(r, half_len=0.048 * s, axle_x0=-0.092 * s, axle_x1=0.116 * s),
        mats["polished"],
        "cutter_stage__single_narrow_module__shaft",
    )
    _add_visual(
        part,
        _pinion(1.14 * r.cutter_disc_radius_m, 0.005 * s, 0.112 * s, 14),
        mats["dark"],
        "cutter_stage__single_narrow_module__driven_gear",
    )
    return None, [part]


_CUTTER_BUILDERS = {
    "fixed_twin_cutter": _cutter_stage_fixed_twin_cutter_build,
    "removable_cassette": _cutter_stage_removable_cassette_build,
    "single_narrow_module": _cutter_stage_single_narrow_module_build,
}


def _clamp_screws_tommy_bar_screw_clamp_build(model, r: ResolvedConfig, mats, index: int):
    s = r.scale
    drop = r.clamp_drop_m * s
    screw = model.part(
        f"clamp_screw_{index}",
        meta={"role": "table_clamp", "clamp_index": index, "screw_pitch_m": 0.0015},
    )
    screw.visual(
        Cylinder(radius=0.0047 * s, length=drop),
        origin=Origin(xyz=(0.0, 0.0, drop / 2.0 - 0.020 * s)),
        material=mats["dark"],
        name=f"clamp_screws__tommy_bar_screw_clamp__stem_{index}", material_class_id="metal.blackened_gunmetal",
    )
    screw.visual(
        Cylinder(radius=0.016 * s, length=0.004 * s),
        origin=Origin(xyz=(0.0, 0.0, drop - 0.020 * s)),
        material=mats["chrome"],
        name=f"clamp_screws__tommy_bar_screw_clamp__pad_{index}", material_class_id="metal.chrome_polished",
    )
    screw.visual(
        Box((0.050 * s, 0.006 * s, 0.006 * s)),
        origin=Origin(xyz=(0.0, 0.0, -0.016 * s)),
        material=mats["dark"],
        name=f"clamp_screws__tommy_bar_screw_clamp__tommy_bar_{index}", material_class_id="metal.blackened_gunmetal",
    )
    return screw


def _axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    radial: tuple[float, float, float],
    articulation_type: ArticulationType,
    limits: MotionLimits,
    mimic: Mimic | None = None,
    provider_name: str = "host.axis",
    consumer_name: str = "member.axis",
) -> None:
    mate = mate_axes(
        AxisInterface(name=provider_name, point=point, axis=axis, radial=radial),
        AxisInterface(name=consumer_name, point=(0.0, 0.0, 0.0), axis=axis, radial=radial),
    )
    model.articulation(
        name,
        articulation_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        mimic=mimic,
    )
    register_interface_mate(model, name, mate)


def build_hand_pasta_maker(
    config: Config,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "hand_operated_pasta_maker_with_rollers_and_crank",
            "slot_choices": tuple(slot_choices_for_config(r).items()),
            "feed_roller_count": r.feed_roller_count,
            "clamp_screw_count": r.clamp_screw_count,
            "source_pool_reviewed": "1 image / 9 rev_000001 models",
        },
    )
    mats = _materials(model)
    s = r.scale

    frame = model.part(
        "frame",
        meta={
            "role": "housing",
            "cutter_stage": r.cutter_stage,
            "transmission": r.transmission,
            "host_cutter_bores": r.cutter_stage != "removable_cassette",
            "host_cassette_rails": r.cutter_stage == "removable_cassette",
        },
    )
    _add_visual(frame, _frame_shape(r), mats["chrome"], "frame__shared_host__body")
    case_shape = _gear_case_shape(r)
    if case_shape is not None:
        _add_visual(
            frame,
            case_shape,
            mats["chrome"],
            "frame__enclosed_gear_case__shell",
        )
    plate_shape = _detent_plate_shape(r)
    if plate_shape is not None:
        _add_visual(
            frame,
            plate_shape,
            mats["dark"],
            "frame__indexed_detent_lever__detent_plate",
        )
    for side_index, x in enumerate((-0.102 * s, 0.102 * s)):
        for screw_index, (y, z) in enumerate(
            ((-0.050 * s, 0.043 * s), (0.060 * s, 0.040 * s))
        ):
            frame.visual(
                Cylinder(radius=0.0032 * s, length=0.0026 * s),
                origin=Origin(xyz=(x, y, z), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=mats["dark"],
                name=f"frame__shared_host__case_screw_{side_index}_{screw_index}", material_class_id="metal.blackened_gunmetal",
            )

    if r.transmission == "enclosed_gear_case":
        wall = 0.0025 * s
        cy = 0.5 * (r.case_y_lo_m + r.case_y_hi_m)
        cz = 0.5 * (r.case_z_lo_m + r.case_z_hi_m)
        dy_half = 0.5 * (r.case_y_hi_m - r.case_y_lo_m) - 0.5 * wall
        dz_half = 0.5 * (r.case_z_hi_m - r.case_z_lo_m) - 0.5 * wall
        for bolt_index, (dy_sign, dz_sign) in enumerate(
            ((-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0))
        ):
            frame.visual(
                Cylinder(radius=0.0025 * s, length=0.003 * s),
                origin=Origin(
                    xyz=(-0.101 * s, cy + dy_sign * dy_half, cz + dz_sign * dz_half),
                    rpy=(0.0, math.pi / 2.0, 0.0),
                ),
                material=mats["dark"],
                name=f"transmission__enclosed_gear_case__housing_bolt_{bolt_index}", material_class_id="metal.blackened_gunmetal",
            )

    crank_part, fold_arm, grip, grip_point, fold_pivot = _CRANK_BUILDERS[r.crank](
        model, r, mats
    )
    feed_parts = [
        _feed_rollers_smooth_nip_roller_build(model, r, mats, index)
        for index in range(r.feed_roller_count)
    ]
    selector, selector_limits = _THICKNESS_BUILDERS[r.thickness_adjust](model, r, mats)
    transmission_parts = _TRANSMISSION_BUILDERS[r.transmission](model, r, mats)
    cassette, cutter_rollers = _CUTTER_BUILDERS[r.cutter_stage](model, r, mats)
    clamp_parts = [
        _clamp_screws_tommy_bar_screw_clamp_build(model, r, mats, index)
        for index in range(r.clamp_screw_count)
    ]

    x_axis = (1.0, 0.0, 0.0)
    x_radial = (0.0, 0.0, 1.0)
    y0, z0 = r.feed_axes_m[0]

    _axis_joint(
        model,
        name="frame_to_crank",
        parent=frame,
        child=crank_part,
        point=(r.socket_x_m + 0.001 * s, y0, z0),
        axis=x_axis,
        radial=x_radial,
        articulation_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=25.0, velocity=5.0),
        provider_name="feed_rollers.drive_socket_axis",
        consumer_name="crank.crank_socket_axis",
    )
    if fold_arm is not None:
        _axis_joint(
            model,
            name="crank_to_fold_arm",
            parent=crank_part,
            child=fold_arm,
            point=fold_pivot,
            axis=x_axis,
            radial=x_radial,
            articulation_type=ArticulationType.REVOLUTE,
            limits=MotionLimits(effort=12.0, velocity=4.0, lower=0.0, upper=r.fold_sweep_rad),
            provider_name="crank.fold_pivot_axis",
            consumer_name="crank.fold_arm_axis",
        )
        grip_parent = fold_arm
    else:
        grip_parent = crank_part
    _axis_joint(
        model,
        name="crank_to_grip",
        parent=grip_parent,
        child=grip,
        point=grip_point,
        axis=x_axis,
        radial=x_radial,
        articulation_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=2.0, velocity=12.0),
        provider_name="crank.grip_axis",
        consumer_name="crank.grip_barrel_axis",
    )

    for index, part in enumerate(feed_parts):
        y, z = r.feed_axes_m[index]
        _axis_joint(
            model,
            name=f"frame_to_feed_roller_{index}",
            parent=frame,
            child=part,
            point=(0.0, y, z),
            axis=x_axis,
            radial=x_radial,
            articulation_type=ArticulationType.CONTINUOUS,
            limits=MotionLimits(effort=30.0, velocity=5.0),
            mimic=Mimic(joint="frame_to_crank", multiplier=-1.0 if index == 1 else 1.0),
            provider_name="feed_rollers.feed_column_bores",
            consumer_name=f"feed_rollers.roller_axis_{index}",
        )

    _axis_joint(
        model,
        name="frame_to_thickness_adjust",
        parent=frame,
        child=selector,
        point=(-0.1090 * s, r.adjust_y_m, r.adjust_z_m),
        axis=x_axis,
        radial=x_radial,
        articulation_type=ArticulationType.REVOLUTE,
        limits=selector_limits,
        provider_name="thickness_adjust.adjust_boss_axis",
        consumer_name="thickness_adjust.selector_axis",
    )

    if r.transmission == "exposed_twin_spur":
        for index, part in enumerate(transmission_parts):
            y, z = r.feed_axes_m[index]
            _axis_joint(
                model,
                name=f"frame_to_transmission_gear_{index}",
                parent=frame,
                child=part,
                point=(-0.116 * s, y, z),
                axis=x_axis,
                radial=x_radial,
                articulation_type=ArticulationType.CONTINUOUS,
                limits=MotionLimits(effort=25.0, velocity=5.0),
                mimic=Mimic(joint="frame_to_crank", multiplier=-1.0 if index == 1 else 1.0),
                provider_name="transmission.spur_mesh_axis",
                consumer_name=f"transmission.gear_axis_{index}",
            )
    elif r.transmission == "enclosed_gear_case":
        _axis_joint(
            model,
            name="frame_to_gear_case_cover",
            parent=frame,
            child=transmission_parts[0],
            point=(
                r.case_front_x_m - 0.0025 * s,
                (r.case_y_lo_m + r.case_y_hi_m) / 2.0,
                r.case_z_hi_m,
            ),
            axis=(0.0, 1.0, 0.0),
            radial=(0.0, 0.0, -1.0),
            articulation_type=ArticulationType.REVOLUTE,
            limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=r.cover_open_rad),
            provider_name="transmission.cover_hinge_axis",
            consumer_name="transmission.cover_axis",
        )

    if r.cutter_stage == "removable_cassette":
        _axis_joint(
            model,
            name="frame_to_cutter_cassette",
            parent=frame,
            child=cassette,
            point=(0.0, r.cassette_y_m, r.cutter_z_m),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            articulation_type=ArticulationType.PRISMATIC,
            limits=MotionLimits(
                effort=15.0, velocity=0.3, lower=0.0, upper=r.cassette_lift_m * s
            ),
            provider_name="cutter_stage.cassette_guide_rails",
            consumer_name="cutter_stage.cassette_axis",
        )
        half = r.cutter_center_distance_m / 2.0
        for index, part in enumerate(cutter_rollers):
            _axis_joint(
                model,
                name=f"cassette_to_cutter_roller_{index}",
                parent=cassette,
                child=part,
                point=(0.0, -half if index == 0 else half, 0.0),
                axis=x_axis,
                radial=x_radial,
                articulation_type=ArticulationType.CONTINUOUS,
                limits=MotionLimits(effort=20.0, velocity=6.0),
                mimic=Mimic(joint="frame_to_crank", multiplier=1.4 if index == 0 else -1.4),
                provider_name="cutter_stage.cassette_roller_bores",
                consumer_name=f"cutter_stage.cassette_roller_axis_{index}",
            )
    elif r.cutter_stage == "fixed_twin_cutter":
        for index, part in enumerate(cutter_rollers):
            y = r.cutter_y0_m if index == 0 else r.cutter_y1_m
            _axis_joint(
                model,
                name=f"frame_to_cutter_roller_{index}",
                parent=frame,
                child=part,
                point=(0.0, y, r.cutter_z_m),
                axis=x_axis,
                radial=x_radial,
                articulation_type=ArticulationType.CONTINUOUS,
                limits=MotionLimits(effort=20.0, velocity=6.0),
                mimic=Mimic(joint="frame_to_crank", multiplier=1.4 if index == 0 else -1.4),
                provider_name="cutter_stage.cutter_cradle_bores",
                consumer_name=f"cutter_stage.cutter_axis_{index}",
            )
    else:
        _axis_joint(
            model,
            name="frame_to_cutter_roller_0",
            parent=frame,
            child=cutter_rollers[0],
            point=(0.0, r.module_y_m, r.module_z_m),
            axis=x_axis,
            radial=x_radial,
            articulation_type=ArticulationType.CONTINUOUS,
            limits=MotionLimits(effort=20.0, velocity=6.0),
            mimic=Mimic(joint="frame_to_crank", multiplier=1.33),
            provider_name="cutter_stage.module_cradle_bore",
            consumer_name="cutter_stage.module_axis",
        )

    for index, screw in enumerate(clamp_parts):
        _axis_joint(
            model,
            name=f"frame_to_clamp_screw_{index}",
            parent=frame,
            child=screw,
            point=(r.clamp_x_m[index], 0.055 * s, r.clamp_jaw_z_m),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            articulation_type=ArticulationType.CONTINUOUS,
            limits=MotionLimits(effort=18.0, velocity=4.0),
            provider_name="clamp_screws.clamp_bracket_seat",
            consumer_name=f"clamp_screws.screw_axis_{index}",
        )

    return model


def _maybe_part(model: ArticulatedObject, name: str):
    try:
        return model.get_part(name)
    except Exception:
        return None


def _maybe_joint(model: ArticulatedObject, name: str):
    try:
        return model.get_articulation(name)
    except Exception:
        return None


def run_hand_pasta_maker_tests(model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    allow_islands = getattr(ctx, "allow_disconnected_islands", None)
    if callable(allow_islands):
        for part in model.parts:
            allow_islands(
                part,
                reason=(
                    "rigid manufactured sub-pieces (pinions, discs, pins, pads and tommy "
                    "bars) belong to one source sub-assembly"
                ),
            )
    for part in model.parts:
        if part.meta.get("role") in {
            "feed_roller",
            "cutter_roller",
            "cutter_cassette",
            "manual_drive",
            "folding_drive_arm",
            "free_spinning_grip",
            "thickness_selector",
            "table_clamp",
            "transmission_gear",
            "gear_case_cover",
        }:
            ctx.allow_isolated_part(
                part,
                reason="joint-retained rotating or sliding member with source running clearance",
            )
    ctx.check_model_valid()

    frame = _maybe_part(model, "frame")
    crank_joint = _maybe_joint(model, "frame_to_crank")
    adjust_joint = _maybe_joint(model, "frame_to_thickness_adjust")
    selector = _maybe_part(model, "thickness_selector")
    feed_parts = [_maybe_part(model, f"feed_roller_{i}") for i in range(r.feed_roller_count)]

    ctx.check(
        "hand pasta maker source identity",
        model.meta.get("category") == "hand_operated_pasta_maker_with_rollers_and_crank"
        and frame is not None
        and selector is not None
        and crank_joint is not None
        and adjust_joint is not None
        and all(part is not None for part in feed_parts)
        and frame.get_visual("frame__shared_host__body") is not None,
        details=f"parts={[p.name for p in model.parts]}",
    )
    ctx.check(
        "all selected slots are recorded",
        dict(model.meta.get("slot_choices", ())) == slot_choices_for_config(r)
        and model.meta.get("feed_roller_count") == r.feed_roller_count
        and model.meta.get("clamp_screw_count") == r.clamp_screw_count,
        details=f"slot_choices={model.meta.get('slot_choices')!r}",
    )

    feed_joints = [
        _maybe_joint(model, f"frame_to_feed_roller_{i}") for i in range(r.feed_roller_count)
    ]
    multipliers = [
        joint.mimic.multiplier if joint is not None and joint.mimic is not None else None
        for joint in feed_joints
    ]
    ctx.check(
        "feed rollers counter-rotate on the crank axis",
        crank_joint is not None
        and tuple(crank_joint.axis) == (1.0, 0.0, 0.0)
        and all(joint is not None for joint in feed_joints)
        and all(tuple(joint.axis) == (1.0, 0.0, 0.0) for joint in feed_joints)
        and all(joint.articulation_type == ArticulationType.CONTINUOUS for joint in feed_joints)
        and all(
            joint.mimic is not None and joint.mimic.joint == "frame_to_crank"
            for joint in feed_joints
        )
        and multipliers[0] == 1.0
        and multipliers[1] == -1.0
        and abs((r.feed_axes_m[1][0] - r.feed_axes_m[0][0]) - r.nip_center_distance_m) < 1e-9,
        details=(
            f"n={r.feed_roller_count}, multipliers={multipliers}, "
            f"centre={r.nip_center_distance_m:.6f}"
        ),
    )

    clamp_joints = [
        _maybe_joint(model, f"frame_to_clamp_screw_{i}") for i in range(r.clamp_screw_count)
    ]
    clamp_parts = [_maybe_part(model, f"clamp_screw_{i}") for i in range(r.clamp_screw_count)]
    bar_tops = []
    for index, part in enumerate(clamp_parts):
        if part is None:
            continue
        aabb = ctx.part_element_world_aabb(
            part, elem=f"clamp_screws__tommy_bar_screw_clamp__tommy_bar_{index}"
        )
        if aabb is not None:
            bar_tops.append(aabb[1][2])
    ctx.check(
        "clamp screws hang below the base",
        len(clamp_joints) == r.clamp_screw_count
        and all(joint is not None for joint in clamp_joints)
        and all(tuple(joint.axis) == (0.0, 0.0, 1.0) for joint in clamp_joints)
        and all(joint.articulation_type == ArticulationType.CONTINUOUS for joint in clamp_joints)
        and len(bar_tops) == r.clamp_screw_count
        and all(top < 0.0 for top in bar_tops)
        and len(set(r.clamp_x_m)) == r.clamp_screw_count,
        details=f"tommy_bar_tops={bar_tops}, x={r.clamp_x_m}",
    )

    if r.cutter_stage == "fixed_twin_cutter":
        rollers = [_maybe_part(model, f"cutter_roller_{i}") for i in range(2)]
        joints = [_maybe_joint(model, f"frame_to_cutter_roller_{i}") for i in range(2)]
        ok = (
            all(part is not None for part in rollers)
            and all(joint is not None for joint in joints)
            and all(tuple(joint.axis) == (1.0, 0.0, 0.0) for joint in joints)
            and _maybe_part(model, "cutter_cassette") is None
            and frame is not None
            and frame.meta.get("host_cutter_bores") is True
        )
        details = "fixed twin cutter in host bores"
    elif r.cutter_stage == "removable_cassette":
        cassette = _maybe_part(model, "cutter_cassette")
        lift = _maybe_joint(model, "frame_to_cutter_cassette")
        joints = [_maybe_joint(model, f"cassette_to_cutter_roller_{i}") for i in range(2)]
        ok = (
            cassette is not None
            and lift is not None
            and lift.articulation_type == ArticulationType.PRISMATIC
            and tuple(lift.axis) == (0.0, 0.0, 1.0)
            and lift.motion_limits is not None
            and abs(lift.motion_limits.upper - r.cassette_lift_m * r.scale) < 1e-9
            and all(joint is not None for joint in joints)
            and frame is not None
            and frame.meta.get("host_cassette_rails") is True
            and frame.meta.get("host_cutter_bores") is False
        )
        details = f"cassette lift={r.cassette_lift_m * r.scale:.5f}, rail={r.rail_length_m:.5f}"
    else:
        roller = _maybe_part(model, "cutter_roller_0")
        joint = _maybe_joint(model, "frame_to_cutter_roller_0")
        ok = (
            roller is not None
            and _maybe_part(model, "cutter_roller_1") is None
            and joint is not None
            and joint.mimic is not None
            and abs(joint.mimic.multiplier - 1.33) < 1e-9
            and frame is not None
            and frame.meta.get("host_cutter_bores") is True
        )
        details = "single narrow module in one cradle bore"
    ctx.check("cutter stage matches its host cradle", ok, details=details)

    ctx.fail_if_isolated_parts()
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "source_001_open_pinion_fixed_cutter",
        {
            "transmission": 'open_pinion_pair',
            "crank": 'rigid_offset_crank',
            "thickness_adjust": 'fluted_rotary_dial',
            "cutter_stage": 'fixed_twin_cutter',
            "feed_roller_count": 2,
            "clamp_screw_count": 1,
            "scale": 1.0,
            "roller_radius_m": 0.015,
            "nip_gap_m": 0.004,
            "crank_reach_m": 0.048,
            "grip_length_m": 0.05,
            "disc_pitch_m": 0.006,
            "cassette_lift_m": 0.06,
            "fold_link_ratio": 0.5,
            "pinion_teeth": 18,
            "spur_teeth": 17,
            "dial_flutes": 32,
            "lever_detent_count": 7,
            "gear_case_depth_m": 0.024,
            "clamp_drop_m": 0.064,
        },
        reason="source image 001 exactly: open pinions, rigid crank, fluted dial, twin cutter",
    ),
    corner_case(
        "cassette_three_roller_maximum",
        {
            "transmission": 'enclosed_gear_case',
            "crank": 'folding_two_link_crank',
            "thickness_adjust": 'indexed_detent_lever',
            "cutter_stage": 'removable_cassette',
            "feed_roller_count": 3,
            "clamp_screw_count": 2,
            "scale": 1.1,
            "roller_radius_m": 0.017,
            "nip_gap_m": 0.006,
            "crank_reach_m": 0.058,
            "grip_length_m": 0.058,
            "disc_pitch_m": 0.0075,
            "cassette_lift_m": 0.075,
            "fold_link_ratio": 0.62,
            "pinion_teeth": 20,
            "spur_teeth": 19,
            "dial_flutes": 24,
            "lever_detent_count": 9,
            "gear_case_depth_m": 0.03,
            "clamp_drop_m": 0.075,
        },
        reason="largest host, tallest roller column, deepest case, longest cassette lift",
    ),
    corner_case(
        "spur_drive_single_module_minimum",
        {
            "transmission": 'exposed_twin_spur',
            "crank": 'folding_two_link_crank',
            "thickness_adjust": 'indexed_detent_lever',
            "cutter_stage": 'single_narrow_module',
            "feed_roller_count": 2,
            "clamp_screw_count": 2,
            "scale": 0.92,
            "roller_radius_m": 0.013,
            "nip_gap_m": 0.002,
            "crank_reach_m": 0.038,
            "grip_length_m": 0.04,
            "disc_pitch_m": 0.0045,
            "cassette_lift_m": 0.045,
            "fold_link_ratio": 0.4,
            "pinion_teeth": 16,
            "spur_teeth": 15,
            "dial_flutes": 24,
            "lever_detent_count": 5,
            "gear_case_depth_m": 0.02,
            "clamp_drop_m": 0.055,
        },
        reason="smallest host, tightest nip, shortest fold link and finest cut",
    ),
    corner_case(
        "spur_drive_three_roller_cassette",
        {
            "transmission": 'exposed_twin_spur',
            "crank": 'rigid_offset_crank',
            "thickness_adjust": 'fluted_rotary_dial',
            "cutter_stage": 'removable_cassette',
            "feed_roller_count": 3,
            "clamp_screw_count": 1,
            "scale": 1.0,
            "roller_radius_m": 0.017,
            "nip_gap_m": 0.002,
            "crank_reach_m": 0.058,
            "grip_length_m": 0.04,
            "disc_pitch_m": 0.0045,
            "cassette_lift_m": 0.075,
            "fold_link_ratio": 0.5,
            "pinion_teeth": 18,
            "spur_teeth": 19,
            "dial_flutes": 28,
            "lever_detent_count": 7,
            "gear_case_depth_m": 0.02,
            "clamp_drop_m": 0.055,
        },
        reason="exposed gear mesh at the widest nip with a stacked idler and a lifting cassette",
    ),
    corner_case(
        "enclosed_case_single_module_small",
        {
            "transmission": 'enclosed_gear_case',
            "crank": 'rigid_offset_crank',
            "thickness_adjust": 'indexed_detent_lever',
            "cutter_stage": 'single_narrow_module',
            "feed_roller_count": 3,
            "clamp_screw_count": 2,
            "scale": 0.92,
            "roller_radius_m": 0.013,
            "nip_gap_m": 0.006,
            "crank_reach_m": 0.038,
            "grip_length_m": 0.058,
            "disc_pitch_m": 0.0075,
            "cassette_lift_m": 0.045,
            "fold_link_ratio": 0.4,
            "pinion_teeth": 20,
            "spur_teeth": 15,
            "dial_flutes": 32,
            "lever_detent_count": 9,
            "gear_case_depth_m": 0.03,
            "clamp_drop_m": 0.075,
        },
        reason="smallest host with the deepest case, a stacked idler and twin clamps",
    ),
    corner_case(
        "open_pinion_folding_cassette",
        {
            "transmission": 'open_pinion_pair',
            "crank": 'folding_two_link_crank',
            "thickness_adjust": 'fluted_rotary_dial',
            "cutter_stage": 'removable_cassette',
            "feed_roller_count": 2,
            "clamp_screw_count": 2,
            "scale": 1.1,
            "roller_radius_m": 0.013,
            "nip_gap_m": 0.006,
            "crank_reach_m": 0.058,
            "grip_length_m": 0.058,
            "disc_pitch_m": 0.0045,
            "cassette_lift_m": 0.075,
            "fold_link_ratio": 0.62,
            "pinion_teeth": 16,
            "spur_teeth": 17,
            "dial_flutes": 32,
            "lever_detent_count": 5,
            "gear_case_depth_m": 0.024,
            "clamp_drop_m": 0.064,
        },
        reason="longest folding crank sweep beside a fully lifted cassette",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_hand_pasta_maker",
    "config_from_seed",
    "resolve_config",
    "run_hand_pasta_maker_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
