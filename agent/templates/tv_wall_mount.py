# SPDX-License-Identifier: Apache-2.0

"""Source-backed procedural TV wall mount template.

The source records establish the stamped wall plate, sleeve pivots, open or enclosed
multi-stage arms, pierced VESA hardware, slotted rails, and lock details.  This module
re-expresses those families as ordinary functions; it never reads authoring files or
source records while building a seed.
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
    Cylinder,
    KnobGeometry,
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
    mesh_from_geometry,
    register_interface_mate,
)

ArmTopology = Literal[
    "articulating_frame",
    "dual_arm_full_motion",
    "fixed_low_profile_plate",
    "single_arm_full_motion",
    "tilt_only_bracket",
]
HeightAdjustment = Literal[
    "counterweighted_lift",
    "gas_spring_vertical_track",
    "toothed_lift_track",
]
ScreenMotion = Literal["portrait_roll_head", "push_pull_depth_carriage", "tilt_swivel_head"]
VesaInterface = Literal[
    "bow_tie_slotted_arms",
    "butterfly_plate",
    "crossed_rails",
    "four_independent_arms",
    "h_bracket_plate",
    "sliding_twin_rails",
    "universal_plate",
]


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "arm_topology",
            (
                "articulating_frame",
                "dual_arm_full_motion",
                "fixed_low_profile_plate",
                "single_arm_full_motion",
                "tilt_only_bracket",
            ),
            role="wall-to-head structural family",
        ),
        component_slot(
            "height_adjustment",
            ("counterweighted_lift", "gas_spring_vertical_track", "toothed_lift_track"),
            role="guided height mechanism",
        ),
        component_slot(
            "screen_motion",
            ("portrait_roll_head", "push_pull_depth_carriage", "tilt_swivel_head"),
            role="display-side motion family",
        ),
        component_slot(
            "vesa_interface",
            (
                "bow_tie_slotted_arms",
                "butterfly_plate",
                "crossed_rails",
                "four_independent_arms",
                "h_bracket_plate",
                "sliding_twin_rails",
                "universal_plate",
            ),
            role="display mounting boundary",
        ),
    )
)


@dataclass(frozen=True)
class Config:
    arm_topology: ArmTopology
    height_adjustment: HeightAdjustment
    screen_motion: ScreenMotion
    vesa_interface: VesaInterface
    arm_scale: float = 1.0
    screen_scale: float = 1.0
    motion_clearance: float = 0.006
    hole_spacing_scale: float = 1.0
    name: str = "tv_wall_mount"


@dataclass(frozen=True)
class ResolvedConfig:
    arm_topology: ArmTopology
    height_adjustment: HeightAdjustment
    screen_motion: ScreenMotion
    vesa_interface: VesaInterface
    wall_width: float
    wall_height: float
    rear_length: float
    front_length: float
    arm_span: float
    carrier_width: float
    carrier_height: float
    vesa_width: float
    vesa_height: float
    lift_height: float
    depth_travel: float
    roll_limit: float
    swivel_limit: float
    hole_spacing: float
    pivot_radius: float
    tilt_radius: float
    motion_clearance: float
    running_clearance: float
    wall_slide_travel: float
    name: str


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x5456_5741_4C4C)
    return Config(
        arm_topology=choices["arm_topology"],
        height_adjustment=choices["height_adjustment"],
        screen_motion=choices["screen_motion"],
        vesa_interface=choices["vesa_interface"],
        arm_scale=round(rng.uniform(0.90, 1.10), 4),
        screen_scale=round(rng.uniform(0.92, 1.08), 4),
        motion_clearance=round(rng.uniform(0.0055, 0.0085), 5),
        hole_spacing_scale=round(rng.uniform(0.94, 1.06), 4),
        name=f"tv_wall_mount_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "arm_topology": config.arm_topology,
            "height_adjustment": config.height_adjustment,
            "screen_motion": config.screen_motion,
            "vesa_interface": config.vesa_interface,
        }
    )
    arm_scale = _clamp(config.arm_scale, 0.86, 1.14)
    screen_scale = _clamp(config.screen_scale, 0.88, 1.12)
    clearance = _clamp(config.motion_clearance, 0.0045, 0.010)
    hole_scale = _clamp(config.hole_spacing_scale, 0.90, 1.10)
    base_span = {
        "articulating_frame": 0.285,
        "dual_arm_full_motion": 0.255,
        "fixed_low_profile_plate": 0.145,
        "single_arm_full_motion": 0.225,
        "tilt_only_bracket": 0.125,
    }[config.arm_topology]
    rear_ratio = (
        0.48 if config.arm_topology in {"dual_arm_full_motion", "articulating_frame"} else 0.52
    )
    rear_length = base_span * rear_ratio * arm_scale
    front_length = base_span * (1.0 - rear_ratio) * arm_scale
    if config.arm_topology == "single_arm_full_motion":
        rear_length = base_span * 0.46 * arm_scale
        front_length = base_span * 0.54 * arm_scale
    arm_span = rear_length + front_length
    wall_width = 0.235 * arm_scale
    wall_height = 0.210 * arm_scale
    carrier_width = 0.225 * screen_scale
    carrier_height = 0.172 * screen_scale
    vesa_width = 0.190 * screen_scale
    vesa_height = 0.135 * screen_scale
    lift_height = {
        "counterweighted_lift": 0.055,
        "gas_spring_vertical_track": 0.070,
        "toothed_lift_track": 0.060,
    }[config.height_adjustment] * screen_scale
    depth_travel = 0.052 * screen_scale
    # Head motion envelopes vary with the sampled screen scale (larger panels
    # sweep a tighter arc), staying inside the design-declared bounds and never
    # exceeding the head/fork clearance verified at the historical maxima.
    roll_limit = (
        _clamp(1.15 - (screen_scale - 0.88), 0.65, 1.57)
        if config.screen_motion == "portrait_roll_head"
        else 0.25
    )
    swivel_limit = (
        _clamp(1.05 - 0.75 * (screen_scale - 0.88), 0.70, 1.57)
        if config.screen_motion == "tilt_swivel_head"
        else 0.25
    )
    hole_spacing = (0.075 if config.vesa_interface == "universal_plate" else 0.085) * hole_scale
    pivot_radius = 0.0125 * arm_scale
    tilt_radius = 0.0105 * screen_scale
    # Derived running clearance for every bearing/shoe/pin fit: a seed-scaled
    # fraction of the sampled motion clearance, always inside the sub-millimetre
    # support band so mated parts stay supported without overlapping.
    running_clearance = _clamp(clearance * 0.08, 0.0004, 0.0008)
    # The complete wall-side carriage travels left/right between the plate's
    # side rails.  Keep its guide shoes inside the clear width at both limits.
    wall_slide_travel = min(
        0.050 * arm_scale,
        max(0.030, wall_width * 0.5 - 0.055 * arm_scale),
    )
    return ResolvedConfig(
        arm_topology=config.arm_topology,
        height_adjustment=config.height_adjustment,
        screen_motion=config.screen_motion,
        vesa_interface=config.vesa_interface,
        wall_width=wall_width,
        wall_height=wall_height,
        rear_length=rear_length,
        front_length=front_length,
        arm_span=arm_span,
        carrier_width=carrier_width,
        carrier_height=carrier_height,
        vesa_width=vesa_width,
        vesa_height=vesa_height,
        lift_height=lift_height,
        depth_travel=depth_travel,
        roll_limit=roll_limit,
        swivel_limit=swivel_limit,
        hole_spacing=hole_spacing,
        pivot_radius=pivot_radius,
        tilt_radius=tilt_radius,
        motion_clearance=clearance,
        running_clearance=running_clearance,
        wall_slide_travel=wall_slide_travel,
        name=config.name,
    )


def _mesh(shape: cq.Workplane, name: str, assets: AssetContext | None):
    return mesh_from_cadquery(
        shape.clean(), name, assets=assets, tolerance=0.00055, angular_tolerance=0.10
    )


def _box(size: tuple[float, float, float], center: tuple[float, float, float]) -> cq.Workplane:
    return cq.Workplane("XY").box(*size).translate(center)


def _cylinder_z(radius: float, length: float, center: tuple[float, float, float]) -> cq.Workplane:
    return (
        cq.Workplane("XY").cylinder(length, radius, centered=(True, True, True)).translate(center)
    )


def _cylinder_y(radius: float, length: float, center: tuple[float, float, float]) -> cq.Workplane:
    return (
        _cylinder_z(radius, length, (0.0, 0.0, 0.0))
        .rotate((0, 0, 0), (1, 0, 0), 90)
        .translate(center)
    )


def _cylinder_x(radius: float, length: float, center: tuple[float, float, float]) -> cq.Workplane:
    return (
        _cylinder_z(radius, length, (0.0, 0.0, 0.0))
        .rotate((0, 0, 0), (0, 1, 0), 90)
        .translate(center)
    )


def _slot_y(x: float, z: float, length: float, width: float, depth: float) -> cq.Workplane:
    slot = _box((width, depth, length), (x, 0.0, z))
    slot = slot.union(_cylinder_y(width * 0.5, depth, (x, 0.0, z - length * 0.5)))
    slot = slot.union(_cylinder_y(width * 0.5, depth, (x, 0.0, z + length * 0.5)))
    return slot


def _wall_plate_shape(r: ResolvedConfig) -> cq.Workplane:
    width, height, depth = r.wall_width, r.wall_height, 0.014
    rim = 0.026
    body = _box((width, depth, height), (0.0, 0.0, 0.0))
    opening = _box((width - 2.0 * rim, depth * 3.0, height - 2.0 * rim), (0.0, 0.0, 0.0))
    body = body.cut(opening)
    # No fixed center crossbar is added: the arm-side carriage spans the upper
    # and lower perimeter rails and is free to translate through the opening.
    for x in (-width * 0.36, width * 0.36):
        for z in (-height * 0.34, height * 0.34):
            body = body.cut(_slot_y(x, z, 0.025, 0.009, 0.045))
    return body


def _wall_mount_carriage_shape(r: ResolvedConfig) -> cq.Workplane:
    """Vertical carriage whose upper/lower clamp pads grip the plate's horizontal rails.

    The carriage frame origin sits 0.034 in front of the wall plate mid-plane
    (the mount-slide joint origin), so the plate's 0.014 depth occupies carriage
    y in [-0.041, -0.027].  The spine stays inside the plate opening; each rail
    is gripped by a front and a rear pad keeping one running clearance to the
    rail faces, joined outside the rail band by a bridge and web so no carriage
    solid penetrates the plate.
    """
    half_h = r.wall_height * 0.5
    c = r.running_clearance
    rim = 0.026  # plate perimeter rail band shared with _wall_plate_shape
    plate_front = -0.027
    plate_back = -0.041
    pad_half = 0.003
    # The pads grip the rail from outside the plate depth: the viewer-side pad
    # keeps one running clearance in front of the front face, the wall-side pad
    # one behind the back face.  Each pad reaches inward in z to overlap the
    # spine so the clamp is one connected solid.
    front_pad_y = plate_front + c + pad_half
    back_pad_y = plate_back - c - pad_half
    pad_z_inner = half_h - rim - c - 0.004
    pad_z_outer = half_h - 0.003
    pad_z_len = pad_z_outer - pad_z_inner
    pad_z_center = 0.5 * (pad_z_inner + pad_z_outer)
    shape = _box((0.032, 0.026, 2.0 * (half_h - rim - c)), (0.0, 0.0, 0.0))
    for sign in (-1.0, 1.0):
        rail_z_center = sign * pad_z_center
        shape = shape.union(_box((0.050, 0.006, pad_z_len), (0.0, front_pad_y, rail_z_center)))
        shape = shape.union(_box((0.050, 0.006, pad_z_len), (0.0, back_pad_y, rail_z_center)))
        # Bridge and web run in the opening band just inside the rail so they
        # tie the pads to the spine without sharing the rail solid volume.
        bridge_z = sign * (half_h - rim - c - 0.006)
        shape = shape.union(
            _box(
                (0.032, front_pad_y - back_pad_y, 0.012),
                (0.0, 0.5 * (front_pad_y + back_pad_y), bridge_z),
            )
        )
        shape = shape.union(_box((0.032, 0.034, 0.012), (0.0, -0.017, bridge_z)))
    # Forward yoke arms carry the wall swivel boss; the center arm stops one
    # running clearance short of the rear-arm pivot sleeve (outer radius 0.017).
    for z in (-0.028, 0.028):
        shape = shape.union(_box((0.034, 0.075, 0.010), (0.0, 0.038, z)))
    arm_top = 0.075 - 0.017 - c
    arm_height = arm_top - 0.0005
    shape = shape.union(_box((0.018, arm_height, 0.040), (0.0, 0.0005 + arm_height * 0.5, 0.0)))
    shape = shape.union(_cylinder_z(0.014, 0.048, (0.0, 0.075, 0.0)))
    return shape


def _link_bar(
    start: tuple[float, float], end: tuple[float, float], width: float, height: float
) -> cq.Workplane:
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    angle = math.degrees(math.atan2(dy, dx))
    bar = _box((length, width, height), ((start[0] + end[0]) * 0.5, (start[1] + end[1]) * 0.5, 0.0))
    return bar.rotate(
        ((start[0] + end[0]) * 0.5, (start[1] + end[1]) * 0.5, 0.0),
        ((start[0] + end[0]) * 0.5, (start[1] + end[1]) * 0.5, 1.0),
        angle,
    )


def _link_bar_xz(
    start: tuple[float, float], end: tuple[float, float], width: float, depth: float
) -> cq.Workplane:
    dx, dz = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dz)
    angle = math.degrees(math.atan2(dz, dx))
    center = ((start[0] + end[0]) * 0.5, 0.0, (start[1] + end[1]) * 0.5)
    return _box((length, depth, width), center).rotate(center, (center[0], 1.0, center[2]), -angle)


def _open_frame_link(
    length: float, bay_count: int, rail_half: float, *, start: float, end_margin: float
) -> cq.Workplane:
    """Source-004 style twin-cheek pressing with sparse diagonal reliefs."""
    shape = cq.Workplane("XY")
    end = length - end_margin
    for x in (-rail_half, rail_half):
        shape = shape.union(_box((0.008, end - start, 0.040), (x, (start + end) * 0.5, 0.0)))
    for y in (start, length * 0.40, length * 0.72, end):
        shape = shape.union(_box((2.0 * rail_half + 0.008, 0.013, 0.016), (0.0, y, 0.0)))
    bay = (end - start) / bay_count
    for index in range(bay_count):
        y0, y1 = start + index * bay, start + (index + 1) * bay
        x0, x1 = (-rail_half, rail_half) if index % 2 == 0 else (rail_half, -rail_half)
        shape = shape.union(_link_bar((x0, y0), (x1, y1), 0.007, 0.014))
    return shape


def _tapered_arm_cover(
    length: float,
    root_half: float,
    tip_half: float,
    *,
    start: float,
    end_margin: float,
) -> cq.Workplane:
    """Source-002 style single clean tapered shroud."""
    outline = [
        (-root_half * 0.72, start),
        (-root_half, start + 0.014),
        (-tip_half, length - end_margin - 0.008),
        (-tip_half * 0.38, length - end_margin),
        (tip_half * 0.38, length - end_margin),
        (tip_half, length - end_margin - 0.008),
        (root_half, start + 0.014),
        (root_half * 0.72, start),
    ]
    return cq.Workplane("XY").polyline(outline).close().extrude(0.018, both=True)


def _capsule_arm_link(
    length: float, width: float, depth: float, *, start: float, end_margin: float
) -> cq.Workplane:
    """Source-003 style cast link with restrained circular bosses."""
    end = length - end_margin
    return _box((width, end - start, depth), (0.0, (start + end) * 0.5, 0.0))


def _compact_arm_link(
    length: float,
    width: float = 0.044,
    *,
    start: float,
    end_margin: float,
) -> cq.Workplane:
    """Source-001 style short rectangular link with compact pivot bosses."""
    end = length - end_margin
    return _box((width, end - start, 0.028), (0.0, (start + end) * 0.5, 0.0))


def _arm_link_for_candidate(
    r: ResolvedConfig, length: float, *, start: float, end_margin: float
) -> cq.Workplane:
    if r.arm_topology == "articulating_frame":
        return _open_frame_link(length, 2, 0.025, start=start, end_margin=end_margin)
    if r.arm_topology == "dual_arm_full_motion":
        return _capsule_arm_link(length, 0.042, 0.030, start=start, end_margin=end_margin)
    if r.arm_topology == "single_arm_full_motion":
        return _tapered_arm_cover(length, 0.035, 0.024, start=start, end_margin=end_margin)
    if r.arm_topology == "fixed_low_profile_plate":
        return _capsule_arm_link(length, 0.038, 0.024, start=start, end_margin=end_margin)
    return _compact_arm_link(length, start=start, end_margin=end_margin)


def _front_arm_shape(r: ResolvedConfig) -> cq.Workplane:
    # The link root must stay one running clearance outside the rear elbow
    # sleeve (radius 0.017) and clear the clevis plate edge through the full
    # fold sweep, so the start offset is bounded below by those derived fits.
    start = _clamp(r.front_length * 0.28, 0.018 + r.running_clearance, 0.050)
    end_margin = min(0.010, r.front_length * 0.10)
    shape = _arm_link_for_candidate(r, r.front_length, start=start, end_margin=end_margin)
    # The arm terminates in one compact mounting shoulder.  The vertical guide
    # is a separate fixed part so its relationship to the moving carriage is
    # explicit in the articulation tree.
    shape = shape.union(_box((0.058, 0.034, 0.038), (0.0, r.front_length - 0.003, 0.0)))
    # Elbow cap discs straddle the clevis plates (outer face z = +/-0.025) by
    # one running clearance so the fold axis passes through front-arm hardware.
    # The disc radius stays inside the shoulder half-depth and clears the rear
    # sleeve (z +/-0.023) and clevis plates through the whole fold sweep.
    cap_z = 0.025 + r.running_clearance + 0.003
    cap_radius = 0.030
    for sign in (-1.0, 1.0):
        shape = shape.union(_cylinder_z(cap_radius, 0.006, (0.0, 0.0, sign * cap_z)))
        # Tie tab joins each cap disc to the elbow bearing neck (neck spans
        # y >= 0.017 + c, z +/-0.006) so the caps are one solid with the arm.
        tie_y0 = 0.017 + r.running_clearance
        shape = shape.union(
            _box(
                (0.016, 0.010, cap_z + 0.003),
                (0.0, tie_y0 + 0.005, sign * 0.5 * (cap_z + 0.003)),
            )
        )
    return shape


def _rear_arm_shape(r: ResolvedConfig) -> cq.Workplane:
    start = min(0.055, r.rear_length * 0.28)
    # The link tail must clear the front elbow bearing (outer radius 0.020) by
    # at least one running clearance at every fold angle.
    end_margin = _clamp(r.rear_length * 0.22, 0.020 + r.running_clearance, 0.040)
    return _arm_link_for_candidate(r, r.rear_length, start=start, end_margin=end_margin)


def _pivot_sleeve_with_neck(
    radius: float, sleeve_height: float, neck_length: float, neck_depth: float, *, bore: float
) -> cq.Workplane:
    """Hollow pivot sleeve: the bore runs on the mating boss with real radial clearance."""
    sleeve = _cylinder_z(radius, sleeve_height, (0.0, 0.0, 0.0)).cut(
        _cylinder_z(bore, sleeve_height + 0.012, (0.0, 0.0, 0.0))
    )
    # The neck starts one running clearance outside the boss radius (== bore).
    neck = _box((0.012, neck_length, neck_depth), (0.0, bore + neck_length * 0.5, 0.0))
    return sleeve.union(neck)


def _elbow_clevis_shape(r: ResolvedConfig) -> cq.Workplane:
    center_y = r.rear_length - 0.020
    shape = cq.Workplane("XY")
    for z in (-0.021, 0.021):
        shape = shape.union(_box((0.054, 0.050, 0.008), (0.0, center_y, z)))
    # A restrained center web makes the fork one load path with the arm body.
    shape = shape.union(_box((0.020, 0.016, 0.050), (0.0, r.rear_length - 0.030, 0.0)))
    return shape


def _height_track_shape(r: ResolvedConfig) -> cq.Workplane:
    """Fixed twin C-channel guide with a clear central carriage lane."""
    guide_height = r.lift_height + 0.074
    shape = cq.Workplane("XY")
    for sign in (-1.0, 1.0):
        x = sign * 0.034
        shape = shape.union(_box((0.006, 0.036, guide_height), (x, 0.023, 0.0)))
        # Rear/front inward lips form a real open vertical slot.  The moving
        # shoe runs between them without sharing any solid volume.
        for y in (0.009, 0.037):
            shape = shape.union(_box((0.014, 0.006, guide_height), (sign * 0.030, y, 0.0)))
    end_z = 0.5 * guide_height - 0.004
    for z in (-end_z, end_z):
        shape = shape.union(_box((0.074, 0.040, 0.008), (0.0, 0.023, z)))
    # A small rear mounting ear rests on the front arm's terminal shoulder with
    # one running clearance; it does not occupy the carriage lane.  The shoulder
    # top sits at y = -0.004 in this frame by construction of the track mount.
    c = r.running_clearance
    shoulder_top = -0.004
    ear_half = 0.007
    ear_y = shoulder_top + c + ear_half
    shape = shape.union(_box((0.046, 0.014, 0.026), (0.0, ear_y, 0.0)))
    shape = shape.union(_box((0.052, 0.006, 0.018), (0.0, ear_y + ear_half - 0.003, 0.0)))
    return shape


def _height_track_mechanism_shape(r: ResolvedConfig) -> cq.Workplane:
    """Fixed half of the selected lift mechanism, kept outside the guide lane."""
    guide_height = r.lift_height + 0.074
    c = r.running_clearance

    if r.height_adjustment == "counterweighted_lift":
        shape = cq.Workplane("XY")
        # Counterweight rods run one clearance plus their own radius outside the
        # arm shoulder (half width 0.029).
        rod_x = 0.029 + c + 0.006
        for x in (-rod_x, rod_x):
            shape = shape.union(_cylinder_z(0.006, guide_height * 0.70, (x, -0.004, -0.006)))
        top_z = guide_height * 0.34
        # The top box reaches 0.001 into the channel web (channels span
        # y 0.005..0.041) so the counterweight head is one solid with the
        # fixed track, while staying clear of every moving saddle feature
        # (moving boxes start at y >= 0.012).
        shape = shape.union(
            _box((2.0 * (rod_x + 0.007), 0.020, 0.010), (0.0, -0.004, top_z - 0.004))
        )
        shape = shape.union(_cylinder_y(0.008, 0.040, (0.0, -0.004, top_z)))
        return shape
    if r.height_adjustment == "gas_spring_vertical_track":
        spring_x = 0.046
        # The spring barrel is hollow so the moving rod telescopes with clearance.
        shape = _cylinder_z(0.006, guide_height * 0.60, (spring_x, 0.023, -0.014)).cut(
            _cylinder_z(0.0035 + c, guide_height * 0.60 + 0.012, (spring_x, 0.023, -0.014))
        )
        # The lower anchor block clamps the barrel: it starts one running
        # clearance outside the moving saddle shoe edge (x = 0.0295) and fuses
        # into the barrel outer face (spring_x + 0.006) so the spring is one
        # solid with the fixed track.
        anchor_min_x = 0.0295 + c
        anchor_max_x = spring_x + 0.006
        gap_center = 0.5 * (anchor_min_x + anchor_max_x)
        gap_half = 0.5 * (anchor_max_x - anchor_min_x)
        shape = shape.union(
            _box((2.0 * gap_half, 0.016, 0.012), (gap_center, 0.023, -guide_height * 0.30))
        )
        # The moving rod telescopes through the anchor at the lower travel
        # limit, so the anchor carries a running-clearance counterbore slightly
        # wider than the barrel bore itself.
        shape = shape.cut(
            _cylinder_z(0.0035 + c + 0.0005, 0.024, (spring_x, 0.023, -guide_height * 0.30))
        )
        return shape

    rack_x = 0.049
    shape = _box((0.006, 0.014, guide_height * 0.76), (rack_x, 0.023, 0.0))
    tooth_pitch = max(0.009, guide_height / 11.0)
    for index in range(-4, 5):
        shape = shape.union(_box((0.010, 0.016, 0.0035), (0.045, 0.023, index * tooth_pitch)))
    for z in (-guide_height * 0.36, guide_height * 0.36):
        shape = shape.union(_box((0.016, 0.016, 0.010), (0.041, 0.023, z)))
    return shape


def _height_carriage_shape(r: ResolvedConfig) -> cq.Workplane:
    """Moving saddle whose shoes run inside, but do not penetrate, the C channels."""
    shape = _box((0.044, 0.018, 0.034), (0.0, 0.051, 0.0))
    shape = shape.union(_box((0.040, 0.028, 0.018), (0.0, 0.037, 0.0)))
    shape = shape.union(_box((0.058, 0.008, 0.020), (0.0, 0.023, 0.0)))
    for x in (-0.027, 0.027):
        shape = shape.union(_box((0.005, 0.018, 0.026), (x, 0.023, 0.0)))
    # A single compact fork captures the transverse head barrel.  Both cheeks are
    # bored so the carriage pin passes through with real radial clearance.
    for x in (-0.034, 0.034):
        shape = shape.union(_box((0.007, 0.020, 0.038), (x, 0.068, 0.0)))
    # The tie bar stays one running clearance below the tilt barrel sweep:
    # the tilt axis sits at y = 0.076 in this frame with radius tilt_radius.
    cross_y = 0.076 - r.tilt_radius - r.running_clearance - 0.007
    shape = shape.union(_box((0.074, 0.014, 0.009), (0.0, cross_y, 0.0)))
    # Bore the fork cheeks one running clearance wider than the carriage pin so
    # the head tilt barrel can swing between them; the pin itself is re-added.
    shape = shape.cut(_cylinder_x(0.0061 + r.running_clearance, 0.076, (0.0, 0.076, 0.0)))
    shape = shape.union(_cylinder_x(0.0061, 0.076, (0.0, 0.076, 0.0)))
    # Retaining collars clamp the pin tips onto the outer cheek faces so the
    # pin is one solid with the saddle.  The inner face stays clear of the
    # head barrel ends (x = fork_inner - c = 0.0305 - c) by 0.006 + c.
    cheek_outer = 0.034 + 0.0035
    collar_cx = cheek_outer + 0.0011
    for x in (-collar_cx, collar_cx):
        shape = shape.union(_box((0.004, 0.015, 0.015), (x, 0.076, 0.0)))
    return shape


def _height_carriage_mechanism_shape(r: ResolvedConfig) -> cq.Workplane:
    """Moving half of the selected lift mechanism."""
    c = r.running_clearance
    if r.height_adjustment == "counterweighted_lift":
        shape = cq.Workplane("XY")
        for x in (-0.018, 0.018):
            shape = shape.union(_box((0.007, 0.014, 0.022), (x, 0.019, -0.016)))
        shape = shape.union(_box((0.044, 0.010, 0.010), (0.0, 0.022, -0.008)))
        return shape
    if r.height_adjustment == "gas_spring_vertical_track":
        spring_x = 0.046
        guide_height = r.lift_height + 0.074
        # Rod length keeps the rod inside the hollow barrel across the whole
        # lift: at the lower travel limit the rod bottom stays one running
        # clearance plus 2 mm above the barrel floor, so it never exits the
        # bore below.
        rod_length = 2.0 * (0.030 + 0.3 * guide_height - 0.5 * r.lift_height - c)
        rod_top_z = 0.018 + rod_length * 0.5
        shape = _cylinder_z(0.0035, rod_length, (spring_x, 0.023, 0.018))
        # Solids whose footprint covers the barrel annulus must stay one
        # running clearance above the barrel top even at the lower travel
        # limit; the slim tie rides inside the bore footprint (radius
        # 0.0035 + c) instead, so it may telescope through the bore region.
        barrel_top = -0.014 + 0.3 * guide_height
        collar_z0 = barrel_top + c + 0.5 * r.lift_height + 0.001
        tie_bottom = rod_top_z - 0.002
        tie_top = collar_z0 + 0.006
        shape = shape.union(
            _cylinder_z(
                0.003, tie_top - tie_bottom, (spring_x, 0.023, 0.5 * (tie_bottom + tie_top))
            )
        )
        shape = shape.union(_box((0.015, 0.024, 0.012), (spring_x, 0.023, collar_z0 + 0.006)))
        # The clevis plate runs one running clearance plus 1 mm above the
        # anchor block's top edge (y = 0.031), so it may sweep past the barrel
        # and anchor at any height without touching either.
        clevis_y = 0.047 + c
        clevis_top = collar_z0 + 0.008
        shape = shape.union(
            _box(
                (0.012, 0.030, clevis_top + 0.005),
                (spring_x, clevis_y, 0.5 * (clevis_top - 0.005)),
            )
        )
        shape = shape.union(_box((0.030, 0.012, 0.010), (0.032, 0.050, 0.0)))
        return shape
    # Toothed track: the pinion keeps one running clearance off the tooth tips
    # (tooth outer x = 0.050) while staying meshed in the rack plane.
    pinion_x = 0.050 + c + 0.008
    shape = _cylinder_y(0.008, 0.018, (pinion_x, 0.023, 0.0))
    shape = shape.union(_box((0.012, 0.030, 0.010), (pinion_x, 0.038, 0.0)))
    shape = shape.union(_box((0.041, 0.012, 0.010), (0.0365, 0.050, 0.0)))
    return shape


def _screen_head_shape(r: ResolvedConfig) -> cq.Workplane:
    """Compact source-style yoke between the arm tilt pin and VESA mechanism."""
    c = r.running_clearance
    # Fork cheek inner faces sit at x = +/-0.0305 on the height carriage; the
    # barrel keeps one running clearance to each face and runs one clearance
    # loose on the 0.0061 carriage pin.
    fork_inner = 0.034 - 0.0035
    barrel_half = fork_inner - c
    tilt_barrel = _cylinder_x(r.tilt_radius, 2.0 * barrel_half, (0.0, 0.0, 0.0)).cut(
        _cylinder_x(0.0061 + c, 2.0 * barrel_half + 0.012, (0.0, 0.0, 0.0))
    )
    neck = _box((0.030, 0.055, 0.026), (0.0, 0.030, 0.0))
    bridge = _box((0.066, 0.016, 0.030), (0.0, 0.058, 0.0))
    shape = tilt_barrel.union(neck).union(bridge)
    # Hub bores run one running clearance loose on the 0.0060 stage spindles.
    if r.screen_motion == "portrait_roll_head":
        roll_hub = _cylinder_y(0.016, 0.034, (0.0, 0.080, 0.0)).cut(
            _cylinder_y(0.0060 + c, 0.044, (0.0, 0.080, 0.0))
        )
        return shape.union(roll_hub)
    if r.screen_motion == "push_pull_depth_carriage":
        for x in (-0.031, 0.031):
            shape = shape.union(_box((0.007, 0.040, 0.052), (x, 0.070, 0.0)))
        return shape
    swivel_hub = _cylinder_z(0.015, 0.040, (0.0, 0.080, 0.0)).cut(
        _cylinder_z(0.0060 + c, 0.052, (0.0, 0.080, 0.0))
    )
    return shape.union(swivel_hub)


def _push_pull_parent_guide_shape(r: ResolvedConfig) -> cq.Workplane:
    guide_length = r.depth_travel + 0.026
    center_y = 0.074 + guide_length * 0.5
    shape = _box((0.070, 0.014, 0.024), (0.0, 0.074, 0.0))
    for x in (-0.022, 0.022):
        sleeve = _cylinder_y(0.0080, guide_length, (x, center_y, 0.0)).cut(
            _cylinder_y(0.0062, guide_length + 0.012, (x, center_y, 0.0))
        )
        shape = shape.union(sleeve)
    return shape


def _push_pull_stage_carriage_shape(r: ResolvedConfig) -> cq.Workplane:
    guide_length = r.depth_travel + 0.060
    c = r.running_clearance
    shape = _box((0.056, 0.016, 0.044), (0.0, 0.020, 0.0))
    # The end bridge transfers both guide rods into the compact VESA carrier.
    shape = shape.union(_box((0.052, 0.014, 0.018), (0.0, guide_length - 0.012, 0.0)))
    # Mid box reaches down into the base plate (base top y = 0.028) and up
    # into the end bridge underside so the whole carriage frame is one solid;
    # the bored holes keep the sleeve lane free.
    mid_height = guide_length - 0.012 - 0.026
    shape = shape.union(
        _box((0.034, mid_height, 0.032), (0.0, 0.5 * (0.026 + guide_length - 0.012), 0.0))
    )
    # Front lip stays beside the parent guide in depth, clear of its body.
    shape = shape.union(_box((0.052, 0.026, 0.012), (0.0, 0.006, 0.019)))
    # Every plate is relieved one running clearance wider than the fixed twin
    # sleeves (outer radius 0.0080) wherever the sleeves can pass.  The relief
    # stops below the end bridge: the fixed sleeves never reach higher than
    # depth_travel + 0.020 = guide_length - 0.040 (15mm below the relief top),
    # so the end bridge stays solid and the sliding rods fuse into it.
    for x in (-0.022, 0.022):
        shape = shape.cut(
            _cylinder_y(0.0080 + c, guide_length - 0.005, (x, 0.5 * guide_length - 0.0225, 0.0))
        )
    # The sliding rods run one running clearance inside the sleeve bores
    # (0.0062) and start one running clearance above the parent guide base box
    # top (head y = 0.081, i.e. stage-local y = 0.001).  Rod tips end inside
    # the solid end bridge so each rod is one solid with the carriage frame.
    rod_start = 0.001 + c
    rod_end = guide_length - 0.006
    rod_length = rod_end - rod_start
    for x in (-0.022, 0.022):
        shape = shape.union(
            _cylinder_y(0.0062 - c, rod_length, (x, 0.5 * (rod_start + rod_end), 0.0))
        )
    return shape


def _screen_stage_mount_shape(r: ResolvedConfig) -> cq.Workplane:
    """Small source-like carriage that directly supports the selected VESA plate."""
    half_w = 0.036
    half_h = 0.034
    mount_y = _screen_stage_mount_y(r)
    plate = _rounded_plate(half_w, half_h, 0.006).translate((0.0, mount_y, 0.0))
    connector_y = mount_y - 0.014
    connector_depth = 0.024
    connector_z = 0.0
    if r.screen_motion == "tilt_swivel_head":
        # Extend the connector over the swivel hub (outer radius 0.015,
        # z +/-0.020) so the swivel spindle flag can fuse in.  The connector
        # underside (y = mount_y - 0.028 = 0.016 + c) stays outside the hub
        # radius, so the extension never touches the head.
        connector_depth = 0.038
        connector_z = 0.007
    return plate.union(_box((0.026, 0.028, connector_depth), (0.0, connector_y, connector_z)))


def _screen_stage_mount_y(r: ResolvedConfig) -> float:
    if r.screen_motion == "push_pull_depth_carriage":
        return r.depth_travel + 0.074
    # The connector box hangs 0.028 below the mount line and must clear the
    # head hub (radius 0.016 about y = 0.080) by one running clearance:
    # 0.080 + mount_y - 0.028 >= 0.080 + 0.016 + c.
    return 0.028 + 0.016 + r.running_clearance


def _rounded_plate(half_w: float, half_h: float, thickness: float) -> cq.Workplane:
    radius = min(0.014, half_w * 0.18, half_h * 0.18)
    plate = _box((2.0 * half_w, thickness, 2.0 * (half_h - radius)), (0.0, 0.0, 0.0))
    plate = plate.union(_box((2.0 * (half_w - radius), thickness, 2.0 * half_h), (0.0, 0.0, 0.0)))
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            plate = plate.union(
                cq.Workplane("XZ")
                .center(sx * (half_w - radius), sz * (half_h - radius))
                .circle(radius)
                .extrude(thickness / 2.0, both=True)
            )
    return plate


def _capsule_slot_xz(
    start: tuple[float, float],
    end: tuple[float, float],
    width: float,
    depth: float,
) -> cq.Workplane:
    slot = _link_bar_xz(start, end, width, depth)
    for x, z in (start, end):
        slot = slot.union(_cylinder_y(width * 0.5, depth, (x, 0.0, z)))
    return slot


def _bow_tie_slotted_arm_shape(
    start: tuple[float, float], end: tuple[float, float], depth: float
) -> cq.Workplane:
    arm_width = 0.018
    shape = _link_bar_xz(start, end, arm_width, depth)
    shape = shape.union(
        cq.Workplane("XZ").center(*end).circle(arm_width * 0.72).extrude(depth / 2.0, both=True)
    )
    dx, dz = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dz)
    ux, uz = dx / length, dz / length
    slot_center = (end[0] - ux * 0.020, end[1] - uz * 0.020)
    half_slot = 0.010
    slot_start = (slot_center[0] - ux * half_slot, slot_center[1] - uz * half_slot)
    slot_end = (slot_center[0] + ux * half_slot, slot_center[1] + uz * half_slot)
    return shape.cut(_capsule_slot_xz(slot_start, slot_end, 0.006, depth + 0.012))


def _butterfly_plate_shape(half_w: float, half_h: float) -> cq.Workplane:
    shape = _box((0.050, 0.008, 0.054), (0.0, 0.0, 0.0))
    for sign in (-1.0, 1.0):
        outline = [
            (sign * 0.018, -0.020),
            (sign * 0.034, -0.020),
            (sign * (half_w * 0.72), -half_h),
            (sign * half_w, -half_h * 0.72),
            (sign * (half_w * 0.74), 0.0),
            (sign * half_w, half_h * 0.72),
            (sign * (half_w * 0.72), half_h),
            (sign * 0.034, 0.020),
            (sign * 0.018, 0.020),
        ]
        wing = cq.Workplane("XZ").polyline(outline).close().extrude(0.004, both=True)
        shape = shape.union(wing)
        for z in (-half_h * 0.72, half_h * 0.72):
            shape = shape.cut(_cylinder_y(0.0042, 0.020, (sign * half_w * 0.78, 0.0, z)))
    return shape


def _h_bracket_plate_shape(half_w: float, half_h: float) -> cq.Workplane:
    shape = _box((0.070, 0.008, 0.082), (0.0, 0.0, 0.0))
    for sign in (-1.0, 1.0):
        x = sign * half_w * 0.78
        shape = shape.union(_box((0.026, 0.010, 2.0 * half_h), (x, 0.0, 0.0)))
        for z in (-half_h * 0.70, -half_h * 0.24, half_h * 0.24, half_h * 0.70):
            shape = shape.cut(_cylinder_y(0.0042, 0.024, (x, 0.0, z)))
    for z in (-half_h * 0.66, half_h * 0.66):
        shape = shape.union(_box((2.0 * half_w * 0.78, 0.008, 0.018), (0.0, 0.0, z)))
    shape = shape.cut(_cylinder_y(0.011, 0.024, (0.0, 0.0, 0.0)))
    return shape


def _vesa_plate_shape(r: ResolvedConfig) -> cq.Workplane:
    half_w, half_h = r.vesa_width * 0.5, r.vesa_height * 0.5
    if r.vesa_interface == "universal_plate":
        outline = [
            (half_w, -half_h * 0.75),
            (half_w * 0.82, -half_h),
            (-half_w * 0.82, -half_h),
            (-half_w, -half_h * 0.75),
            (-half_w, half_h * 0.75),
            (-half_w * 0.82, half_h),
            (half_w * 0.82, half_h),
            (half_w, half_h * 0.75),
        ]
        shape = cq.Workplane("XZ").polyline(outline).close().extrude(0.003, both=True)
        for spacing in (r.hole_spacing, min(0.100 * r.hole_spacing / 0.075, r.vesa_height * 0.78)):
            for x in (-spacing * 0.5, spacing * 0.5):
                for z in (-spacing * 0.5, spacing * 0.5):
                    shape = shape.cut(_cylinder_y(0.0042, 0.014, (x, 0.0, z)))
        for x in (-half_w * 0.82, half_w * 0.82):
            shape = shape.cut(_slot_y(x, 0.0, 0.028, 0.008, 0.014).rotate((x, 0, 0), (x, 1, 0), 90))
        return shape
    if r.vesa_interface == "crossed_rails":
        shape = _rounded_plate(0.032, 0.028, 0.006)
        for sx, sz in ((-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)):
            start = (sx * 0.024, sz * 0.020)
            end = (sx * half_w * 0.88, sz * half_h * 0.88)
            shape = shape.union(_link_bar_xz(start, end, 0.013, 0.006))
            shape = shape.union(
                cq.Workplane("XZ").center(*end).circle(0.010).extrude(0.003, both=True)
            )
            shape = shape.cut(_cylinder_y(0.0038, 0.018, (end[0], 0.0, end[1])))
        return shape
    if r.vesa_interface == "sliding_twin_rails":
        # Source-004: a wide relieved carrier with upper/lower front-opening
        # C tracks supports two independently adjustable vertical slotted rails.
        # The return lips retain a larger shoe behind a narrow neck; none of the
        # moving shoe volume intersects the fixed track collision geometry.
        shape = _box((2.0 * half_w, 0.010, 2.0 * half_h * 0.76), (0.0, 0.0, 0.0))
        window_w = half_w * 0.54
        for x in (-half_w * 0.38, half_w * 0.38):
            shape = shape.cut(_box((window_w, 0.030, half_h * 0.74), (x, 0.0, 0.0)))
        for z in (-half_h * 0.88, half_h * 0.88):
            shape = shape.union(_box((2.0 * half_w, 0.004, 0.018), (0.0, -0.003, z)))
            for sign in (-1.0, 1.0):
                shape = shape.union(
                    _box((2.0 * half_w, 0.012, 0.003), (0.0, 0.005, z + sign * 0.0075))
                )
                shape = shape.union(
                    _box((2.0 * half_w, 0.003, 0.003), (0.0, 0.0095, z + sign * 0.0045))
                )
        shape = shape.union(_box((0.058, 0.014, 0.058), (0.0, 0.004, 0.0)))
        return shape
    if r.vesa_interface == "bow_tie_slotted_arms":
        shape = _rounded_plate(0.042, 0.040, 0.008)
        for sx, sz in ((-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)):
            start = (sx * 0.028, sz * 0.026)
            end = (sx * half_w * 0.92, sz * half_h * 0.92)
            shape = shape.union(_bow_tie_slotted_arm_shape(start, end, 0.010))
        return shape
    if r.vesa_interface == "butterfly_plate":
        return _butterfly_plate_shape(half_w, half_h)
    if r.vesa_interface == "h_bracket_plate":
        return _h_bracket_plate_shape(half_w, half_h)
    # Four separately adjustable arms around a small central carrier.
    shape = _rounded_plate(0.030, 0.024, 0.006)
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            end = (sx * half_w * 0.82, sz * half_h * 0.82)
            shape = shape.union(_link_bar_xz((0.0, 0.0), end, 0.010, 0.008))
            shape = shape.union(
                cq.Workplane("XZ").center(*end).circle(0.012).extrude(0.004, both=True)
            )
            shape = shape.cut(_cylinder_y(0.0038, 0.020, (end[0], 0.0, end[1])))
    return shape


def _sliding_rail_shape(r: ResolvedConfig) -> cq.Workplane:
    """Pierced TV-side rail web in its own joint-local frame."""
    x = 0.0
    rail_y = 0.019
    rail_height = r.vesa_height * 0.94
    rail = _box((0.018, 0.014, rail_height), (x, rail_y, 0.0))
    for hole_z in (-r.carrier_height * 0.28, 0.0, r.carrier_height * 0.28):
        rail = rail.cut(_slot_y(x, hole_z, 0.020, 0.007, 0.030).translate((0.0, rail_y, 0.0)))
    return rail


def _sliding_rail_hooks_shape(r: ResolvedConfig) -> cq.Workplane:
    """Clearance-fit captive shoes and necks for the carrier C tracks."""
    track_z = r.vesa_height * 0.5 * 0.88
    hooks = cq.Workplane("XY")
    for z in (-track_z, track_z):
        # The 10 mm shoe runs inside the 12 mm track cavity.  Its rear,
        # flange and return-lip clearances are each 1 mm.  A 4 mm neck
        # passes through the 6 mm mouth and joins the forward rail web.
        hooks = hooks.union(_box((0.024, 0.007, 0.010), (0.0, 0.0035, z)))
        hooks = hooks.union(_box((0.016, 0.0075, 0.004), (0.0, 0.01025, z)))
    return hooks


def _axis_mated_joint(
    model: ArticulatedObject,
    name: str,
    parent: str,
    child: str,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    limits: MotionLimits,
    *,
    continuous: bool = False,
    articulation_type: ArticulationType = ArticulationType.REVOLUTE,
    radius: float = 0.010,
):
    provider = AxisInterface(
        point=point,
        axis=axis,
        radial=(1.0, 0.0, 0.0) if axis != (1.0, 0.0, 0.0) else (0.0, 1.0, 0.0),
        radius=radius,
        name=f"{name}.provider",
    )
    consumer = AxisInterface(
        point=(0.0, 0.0, 0.0),
        axis=axis,
        radial=(1.0, 0.0, 0.0) if axis != (1.0, 0.0, 0.0) else (0.0, 1.0, 0.0),
        radius=radius * 0.72,
        name=f"{name}.consumer",
    )
    mate = mate_axes(provider, consumer, require_fit=True, radial_clearance=0.0005)
    joint = model.articulation(
        name,
        ArticulationType.CONTINUOUS if continuous else articulation_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
    )
    register_interface_mate(model, name, mate)
    return joint


def _add_screen_motion(
    model: ArticulatedObject, r: ResolvedConfig, screen_head: str, screen_stage: str
) -> None:
    if r.screen_motion == "portrait_roll_head":
        _axis_mated_joint(
            model,
            "screen_motion__portrait_roll_head__roll",
            screen_head,
            screen_stage,
            (0.0, 0.080, 0.0),
            (0.0, 1.0, 0.0),
            MotionLimits(lower=-r.roll_limit, upper=r.roll_limit, effort=18.0, velocity=0.8),
            radius=0.012,
        )
    elif r.screen_motion == "tilt_swivel_head":
        _axis_mated_joint(
            model,
            "screen_motion__tilt_swivel_head__swivel",
            screen_head,
            screen_stage,
            (0.0, 0.080, 0.0),
            (0.0, 0.0, 1.0),
            MotionLimits(lower=-r.swivel_limit, upper=r.swivel_limit, effort=22.0, velocity=0.8),
            radius=0.012,
        )
    else:
        model.articulation(
            "screen_motion__push_pull_depth_carriage__depth",
            ArticulationType.PRISMATIC,
            parent=screen_head,
            child=screen_stage,
            origin=Origin(xyz=(0.0, 0.080, 0.0)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(lower=0.0, upper=r.depth_travel, effort=28.0, velocity=0.06),
        )


def _build_arm_topology(
    model: ArticulatedObject, r: ResolvedConfig, material, assets: AssetContext | None
) -> tuple[str, str]:
    rear = model.part(
        "rear_arm", meta={"role": "source-backed multi-stage rear arm", "candidate": r.arm_topology}
    )
    rear.visual(
        _mesh(_rear_arm_shape(r), f"arm_topology__{r.arm_topology}__rear_arm", assets),
        material=material,
        name=f"arm_topology__{r.arm_topology}__rear_arm_shell",
        material_class_id="metal.paint_coated",
    )
    rear.visual(
        _mesh(
            _pivot_sleeve_with_neck(
                0.017,
                0.040,
                min(0.075, r.rear_length * 0.50),
                0.020,
                bore=0.014 + r.running_clearance,
            ),
            f"arm_topology__{r.arm_topology}__wall_pivot_sleeve",
            assets,
        ),
        material=material,
        name=f"arm_topology__{r.arm_topology}__wall_pivot_sleeve",
        material_class_id="metal.paint_coated",
    )
    rear.visual(
        _mesh(
            _elbow_clevis_shape(r),
            f"arm_topology__{r.arm_topology}__elbow_clevis",
            assets,
        ),
        material=material,
        name=f"arm_topology__{r.arm_topology}__elbow_clevis",
        material_class_id="metal.paint_coated",
    )
    rear.visual(
        Cylinder(radius=0.017, length=0.046),
        origin=Origin(xyz=(0.0, r.rear_length, 0.0)),
        material=material,
        name=f"arm_topology__{r.arm_topology}__elbow_sleeve",
        material_class_id="metal.paint_coated",
    )
    front = model.part(
        "front_arm",
        meta={"role": "source-backed multi-stage front arm", "candidate": r.arm_topology},
    )
    front.visual(
        _mesh(_front_arm_shape(r), f"arm_topology__{r.arm_topology}__front_arm", assets),
        material=material,
        name=f"arm_topology__{r.arm_topology}__front_arm_shell",
        material_class_id="metal.paint_coated",
    )
    front.visual(
        _mesh(
            _pivot_sleeve_with_neck(
                0.020,
                0.012,
                min(0.055, r.front_length * 0.34),
                0.012,
                bore=0.017 + r.running_clearance,
            ),
            f"arm_topology__{r.arm_topology}__elbow_bearing",
            assets,
        ),
        material=material,
        name=f"arm_topology__{r.arm_topology}__elbow_bearing",
        material_class_id="metal.paint_coated",
    )
    return rear.name, front.name


def _build_wall_mount_carriage(
    model: ArticulatedObject,
    r: ResolvedConfig,
    material,
    assets: AssetContext | None,
) -> str:
    carriage = model.part(
        "wall_mount_carriage",
        meta={"role": "horizontally sliding wall-plate mount carriage"},
    )
    carriage.visual(
        _mesh(_wall_mount_carriage_shape(r), "wall_plate__mount_slide__carriage", assets),
        material=material,
        name="wall_plate__mount_slide__carriage_body",
        material_class_id="metal.paint_coated",
    )
    guide_z = r.wall_height * 0.5 - 0.013
    # The plate front face is at carriage y = -0.027; the shoes run one
    # running clearance in front of it, spanning the full rail band in depth.
    shoe_y = -0.027 + r.running_clearance + 0.015
    for index, z in enumerate((-guide_z, guide_z)):
        carriage.visual(
            Cylinder(radius=0.006, length=0.030),
            origin=Origin(xyz=(0.0, shoe_y, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=material,
            name=f"wall_plate__mount_slide__guide_shoe_{index}",
            material_class_id="metal.paint_coated",
        )
    return carriage.name


def _build_height_carriage(
    model: ArticulatedObject, r: ResolvedConfig, material, accent, assets: AssetContext | None
):
    carriage = model.part(
        "height_carriage",
        meta={"role": "derived guided height carriage", "candidate": r.height_adjustment},
    )
    carriage.visual(
        _mesh(
            _height_carriage_shape(r),
            f"height_adjustment__{r.height_adjustment}__moving_saddle",
            assets,
        ),
        material=accent,
        name=f"height_adjustment__{r.height_adjustment}__moving_saddle",
        material_class_id="metal.steel_bare",
    )
    carriage.visual(
        _mesh(
            _height_carriage_mechanism_shape(r),
            f"height_adjustment__{r.height_adjustment}__moving_mechanism",
            assets,
        ),
        material=material,
        name=f"height_adjustment__{r.height_adjustment}__moving_mechanism",
        material_class_id="metal.paint_coated",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        carriage.visual(
            Cylinder(radius=0.002, length=0.020),
            origin=Origin(xyz=(sign * 0.029, 0.023, 0.0)),
            material=material,
            name=f"height_adjustment__{r.height_adjustment}__guide_roller_{index}",
            material_class_id="metal.paint_coated",
        )
    return carriage.name


def _build_height_track(
    model: ArticulatedObject,
    r: ResolvedConfig,
    material,
    accent,
    assets: AssetContext | None,
) -> str:
    track = model.part(
        "height_track",
        meta={"role": "fixed vertical guide", "candidate": r.height_adjustment},
    )
    track.visual(
        _mesh(
            _height_track_shape(r),
            f"height_adjustment__{r.height_adjustment}__guide_frame",
            assets,
        ),
        material=material,
        name=f"height_adjustment__{r.height_adjustment}__guide_frame",
        material_class_id="metal.paint_coated",
    )
    track.visual(
        _mesh(
            _height_track_mechanism_shape(r),
            f"height_adjustment__{r.height_adjustment}__fixed_mechanism",
            assets,
        ),
        material=accent,
        name=f"height_adjustment__{r.height_adjustment}__fixed_mechanism",
        material_class_id="metal.steel_galvanized",
    )
    return track.name


def _build_screen_parts(
    model: ArticulatedObject, r: ResolvedConfig, material, accent, assets: AssetContext | None
):
    head = model.part(
        "screen_head",
        meta={"role": "tilt yoke and motion envelope host", "candidate": r.screen_motion},
    )
    head.visual(
        _mesh(_screen_head_shape(r), f"screen_motion__{r.screen_motion}__head_yoke", assets),
        material=accent,
        name=f"screen_motion__{r.screen_motion}__head_yoke",
        material_class_id="metal.steel_bare",
    )
    if r.screen_motion == "push_pull_depth_carriage":
        head.visual(
            _mesh(
                _push_pull_parent_guide_shape(r),
                "screen_motion__push_pull_depth_carriage__parent_guide",
                assets,
            ),
            material=accent,
            name="screen_motion__push_pull_depth_carriage__parent_guide",
            material_class_id="metal.steel_bare",
        )
    stage = model.part(
        "screen_stage", meta={"role": "display motion stage", "candidate": r.screen_motion}
    )
    if r.screen_motion == "portrait_roll_head":
        # Spindle is offset upward: its tip passes the head roll hub face
        # (y = 0.017) to carry the fuse flag, while its bottom stays 2mm
        # above the head bridge top (stage-local y = -0.014).  A flag tab
        # fuses the spindle into the stage-mount connector (y min 0.016 + c)
        # while keeping one running clearance off the hub face.
        spindle = _cylinder_y(0.0060, 0.033, (0.0, 0.0045, 0.0))
        flag = _box((0.012, 0.006, 0.012), (0.0, 0.020 + r.running_clearance, 0.0))
        stage_hardware = spindle.union(flag)
        stage_hardware_name = "stage_roll_spindle"
    elif r.screen_motion == "tilt_swivel_head":
        # Spindle tips pass the head swivel hub (z +/-0.020); a flag tab fuses
        # the spindle into the extended stage-mount connector, staying one
        # running clearance above the hub rim (radial 0.015).
        spindle = _cylinder_z(0.0060, 0.052, (0.0, 0.0, 0.0))
        flag = _box(
            (0.012, 0.015 + r.running_clearance, 0.006 - r.running_clearance),
            (0.0, 0.0115 + 0.5 * r.running_clearance, 0.023 + 0.5 * r.running_clearance),
        )
        stage_hardware = spindle.union(flag)
        stage_hardware_name = "stage_swivel_spindle"
    else:
        stage_hardware = _push_pull_stage_carriage_shape(r)
        stage_hardware_name = "stage_depth_guide"
    stage.visual(
        _mesh(
            stage_hardware,
            f"screen_motion__{r.screen_motion}__{stage_hardware_name}",
            assets,
        ),
        material=material,
        name=f"screen_motion__{r.screen_motion}__{stage_hardware_name}",
        material_class_id="metal.paint_coated",
    )
    stage.visual(
        _mesh(
            _screen_stage_mount_shape(r),
            f"screen_motion__{r.screen_motion}__stage_mount",
            assets,
        ),
        material=accent,
        name=f"screen_motion__{r.screen_motion}__stage_mount",
        material_class_id="metal.steel_bare",
    )
    mount_y = _screen_stage_mount_y(r)
    for index, x in enumerate((-0.018, 0.018)):
        stage.visual(
            Cylinder(radius=0.0045, length=0.008),
            origin=Origin(xyz=(x, mount_y - 0.002, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=material,
            name=f"screen_motion__{r.screen_motion}__mount_fastener_{index}",
            material_class_id="metal.paint_coated",
        )
    return head.name, stage.name


def _build_vesa(
    model: ArticulatedObject, r: ResolvedConfig, material, accent, assets: AssetContext | None
):
    vesa = model.part(
        "vesa_mount", meta={"role": "real supporting VESA footprint", "candidate": r.vesa_interface}
    )
    # Uniform mounting pad under every candidate plate: its bottom (y = -0.005)
    # is the single deepest underside over the stage footprint, so candidates
    # whose own features reach -0.005 only outside the stage plate (h_bracket
    # columns) still present a continuous, sub-millimetre support gap.
    plate_shape = _vesa_plate_shape(r).union(_box((0.064, 0.004, 0.062), (0.0, -0.003, 0.0)))
    vesa.visual(
        _mesh(plate_shape, f"vesa_interface__{r.vesa_interface}__plate", assets),
        material=material,
        name=f"vesa_interface__{r.vesa_interface}__plate",
        material_class_id="metal.paint_coated",
    )
    rail_names: list[str] = []
    if r.vesa_interface == "sliding_twin_rails":
        for index in range(2):
            rail = model.part(
                f"vesa_rail_{index}",
                meta={"role": "independently sliding TV-side rail", "rail_index": index},
            )
            rail.visual(
                _mesh(
                    _sliding_rail_shape(r),
                    f"vesa_interface__{r.vesa_interface}__rail_{index}",
                    assets,
                ),
                material=accent,
                name=f"vesa_interface__{r.vesa_interface}__rail_web_{index}",
                material_class_id="metal.steel_galvanized",
            )
            rail.visual(
                _mesh(
                    _sliding_rail_hooks_shape(r),
                    f"vesa_interface__{r.vesa_interface}__track_hooks_{index}",
                    assets,
                ),
                material=accent,
                name=f"vesa_interface__{r.vesa_interface}__track_hooks_{index}",
                material_class_id="metal.steel_galvanized",
            )
            rail_names.append(rail.name)
    return vesa.name, rail_names


def build_tv_wall_mount(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    black = model.material("tv_mount_powder_black", rgba=(0.045, 0.050, 0.055, 1.0))
    edge = model.material("tv_mount_edge_steel", rgba=(0.16, 0.17, 0.18, 1.0))
    zinc = model.material("tv_mount_zinc", rgba=(0.52, 0.55, 0.57, 1.0))
    wall = model.part("wall_plate", meta={"role": "stamped wall mounting plate"})
    wall.visual(
        _mesh(_wall_plate_shape(r), "wall_plate_structure", assets),
        material=black,
        name="wall_plate__stamped_frame",
        material_class_id="metal.paint_coated",
    )
    for index, (x, z) in enumerate(
        (
            (-r.wall_width * 0.36, -r.wall_height * 0.34),
            (-r.wall_width * 0.36, r.wall_height * 0.34),
            (r.wall_width * 0.36, -r.wall_height * 0.34),
            (r.wall_width * 0.36, r.wall_height * 0.34),
        )
    ):
        wall.visual(
            Cylinder(radius=0.014, length=0.007),
            origin=Origin(xyz=(x, 0.0, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=zinc,
            name=f"wall_plate__fastener_{index}",
            material_class_id="metal.steel_galvanized",
        )
    wall_carriage_name = _build_wall_mount_carriage(model, r, black, assets)
    rear_name, front_name = _build_arm_topology(model, r, black, assets)
    height_track_name = _build_height_track(model, r, black, zinc, assets)
    carriage_name = _build_height_carriage(model, r, black, edge, assets)
    head_name, stage_name = _build_screen_parts(model, r, black, edge, assets)
    vesa_name, vesa_rail_names = _build_vesa(model, r, black, zinc, assets)

    _axis_mated_joint(
        model,
        "wall_plate__mount_slide",
        wall.name,
        wall_carriage_name,
        (0.0, 0.034, 0.0),
        (1.0, 0.0, 0.0),
        MotionLimits(
            lower=-r.wall_slide_travel,
            upper=r.wall_slide_travel,
            effort=32.0,
            velocity=0.05,
        ),
        articulation_type=ArticulationType.PRISMATIC,
        radius=0.010,
    )
    _axis_mated_joint(
        model,
        "arm_topology__wall_swivel",
        wall_carriage_name,
        rear_name,
        (0.0, 0.075, 0.0),
        (0.0, 0.0, 1.0),
        MotionLimits(
            lower=(
                -0.18
                if r.arm_topology == "tilt_only_bracket"
                else (-0.28 if r.arm_topology == "fixed_low_profile_plate" else -0.68)
            ),
            upper=(
                0.18
                if r.arm_topology == "tilt_only_bracket"
                else (0.28 if r.arm_topology == "fixed_low_profile_plate" else 0.68)
            ),
            effort=85.0,
            velocity=1.0,
        ),
        radius=r.pivot_radius,
    )
    _axis_mated_joint(
        model,
        "arm_topology__elbow_fold",
        rear_name,
        front_name,
        (0.0, r.rear_length, 0.0),
        (0.0, 0.0, 1.0),
        MotionLimits(
            lower=-0.14 if r.arm_topology == "tilt_only_bracket" else -0.40,
            upper=0.14 if r.arm_topology == "tilt_only_bracket" else 0.40,
            effort=70.0,
            velocity=1.0,
        ),
        radius=r.pivot_radius,
    )
    model.articulation(
        "height_adjustment__track_mount",
        ArticulationType.FIXED,
        parent=front_name,
        child=height_track_name,
        origin=Origin(xyz=(0.0, r.front_length + 0.018, 0.0)),
    )
    _axis_mated_joint(
        model,
        "height_adjustment__guided_slide",
        height_track_name,
        carriage_name,
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
        MotionLimits(
            lower=-r.lift_height * 0.5, upper=r.lift_height * 0.5, effort=25.0, velocity=0.06
        ),
        articulation_type=ArticulationType.PRISMATIC,
        radius=0.006,
    )
    _axis_mated_joint(
        model,
        "arm_topology__screen_tilt",
        carriage_name,
        head_name,
        (0.0, 0.076, 0.0),
        (1.0, 0.0, 0.0),
        MotionLimits(lower=-0.24, upper=0.24, effort=45.0, velocity=0.7),
        radius=r.tilt_radius,
    )
    _add_screen_motion(model, r, head_name, stage_name)

    stage_mount_y = _screen_stage_mount_y(r)
    host_plane = PlaneInterface(
        name=f"screen_motion__{r.screen_motion}__vesa_host",
        point=(0.0, stage_mount_y + 0.004, 0.0),
        normal=(0.0, 1.0, 0.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(0.072, 0.068),
    )
    consumer_plane = PlaneInterface(
        name=f"vesa_interface__{r.vesa_interface}__back",
        point=(0.0, 0.0, 0.0),
        normal=(0.0, -1.0, 0.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(0.046, 0.042),
    )
    # The uniform mounting pad bottom sits at vesa-local y = -0.005; lifting the
    # consumer back plane so the pad clears the stage plate top (mount_y + 0.003)
    # by exactly one running clearance gives a constant support gap for every
    # candidate. Host plane at mount_y + 0.004, so gap = 0.004 + clearance.
    vesa_gap = 0.004 + r.running_clearance
    vesa_mate = mate_planes(host_plane, consumer_plane, gap=vesa_gap, margin=r.motion_clearance)
    model.articulation(
        "vesa_interface__support_plane",
        ArticulationType.FIXED,
        parent=stage_name,
        child=vesa_name,
        origin=vesa_mate.origin,
    )
    if r.vesa_interface == "sliding_twin_rails":
        rail_spacing = r.vesa_width * 0.43
        rail_travel = 0.014 * (r.vesa_width / 0.190)
        for index, (rail_name, sign) in enumerate(zip(vesa_rail_names, (-1.0, 1.0))):
            _axis_mated_joint(
                model,
                f"vesa_interface__sliding_twin_rails__rail_slide_{index}",
                vesa_name,
                rail_name,
                (sign * rail_spacing, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                MotionLimits(
                    lower=-rail_travel if index == 0 else -2.0 * rail_travel,
                    upper=2.0 * rail_travel if index == 0 else rail_travel,
                    effort=25.0,
                    velocity=0.05,
                ),
                articulation_type=ArticulationType.PRISMATIC,
                radius=0.005,
            )
    for index, sign in enumerate((-1.0, 1.0)):
        knob = model.part(f"tilt_knob_{index}", meta={"role": "continuous tilt lock knob"})
        knob_rpy = (0.0, sign * math.pi / 2.0, 0.0)
        knob.visual(
            mesh_from_geometry(
                KnobGeometry(
                    0.022,
                    0.012,
                    body_style="lobed",
                    base_diameter=0.018,
                    top_diameter=0.021,
                    crown_radius=0.001,
                    center=False,
                ),
                f"lock__tilt_knob__{index}",
            ),
            origin=Origin(rpy=knob_rpy),
            material=edge,
            name=f"lock__tilt_knob__{index}__grip",
            material_class_id="metal.steel_bare",
        )
        _axis_mated_joint(
            model,
            f"lock__tilt_knob__{index}__turn",
            head_name,
            knob.name,
            # One running clearance outside the head bridge face (x = +/-0.033).
            (sign * (0.033 + r.running_clearance), 0.060, 0.0),
            (1.0, 0.0, 0.0),
            MotionLimits(effort=4.0, velocity=4.0),
            continuous=True,
            radius=0.010,
        )
    model.meta["slot_choices"] = [(name, getattr(r, name)) for name in TEMPLATE_DOMAIN.slot_names]
    model.meta["source_family"] = "pictureX/0611/tv_wall_mount"
    model.meta["derived_motion_envelope"] = {
        "arm_span": r.arm_span,
        "lift_height": r.lift_height,
        "depth_travel": r.depth_travel,
        "clearance": r.motion_clearance,
    }
    return model


def build_seeded_tv_wall_mount(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_tv_wall_mount(config_from_seed(seed), assets=assets)


def run_tv_wall_mount_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    screen_stage = object_model.get_part("screen_stage")
    stage_hardware_name = {
        "portrait_roll_head": "stage_roll_spindle",
        "tilt_swivel_head": "stage_swivel_spindle",
        "push_pull_depth_carriage": "stage_depth_guide",
    }[r.screen_motion]
    if r.vesa_interface == "sliding_twin_rails":
        for index in range(2):
            ctx.allow_isolated_part(
                object_model.get_part(f"vesa_rail_{index}"),
                reason=(
                    "The prismatic rail is retained by clearance-fit shoes inside the fixed "
                    "carrier C tracks; the 1 mm running clearance intentionally avoids "
                    "collision contact in the neutral pose."
                ),
            )
    for index in range(2):
        knob = object_model.get_part(f"tilt_knob_{index}")
        ctx.allow_isolated_part(
            knob,
            reason="The free-turning lock knob is retained on a threaded head stud with running clearance.",
        )
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    parts = {part.name for part in object_model.parts}
    joints = {joint.name: joint for joint in object_model.articulations}
    for part_name in (
        "wall_plate",
        "wall_mount_carriage",
        "rear_arm",
        "front_arm",
        "height_track",
        "height_carriage",
        "screen_head",
        "screen_stage",
        "vesa_mount",
    ):
        ctx.check(
            f"required part {part_name} exists", part_name in parts, details=str(sorted(parts))
        )
    for joint_name in (
        "wall_plate__mount_slide",
        "arm_topology__wall_swivel",
        "arm_topology__elbow_fold",
        "height_adjustment__track_mount",
        "height_adjustment__guided_slide",
        "arm_topology__screen_tilt",
    ):
        ctx.check(f"required joint {joint_name} exists", joint_name in joints)
    rotational = [
        joint
        for joint in joints.values()
        if joint.articulation_type in {ArticulationType.REVOLUTE, ArticulationType.CONTINUOUS}
    ]
    ctx.check(
        "every rotational joint is axis-mated",
        all(
            isinstance(joint.meta, dict) and "interface_mate" in joint.meta for joint in rotational
        ),
    )
    ctx.check(
        "guided height has finite edge limits",
        joints["height_adjustment__guided_slide"].motion_limits is not None
        and joints["height_adjustment__guided_slide"].motion_limits.lower
        < joints["height_adjustment__guided_slide"].motion_limits.upper,
    )
    height_joint = joints["height_adjustment__guided_slide"]
    ctx.check(
        "height carriage is a Z-axis child of the fixed track",
        height_joint.parent == "height_track"
        and height_joint.child == "height_carriage"
        and height_joint.articulation_type == ArticulationType.PRISMATIC
        and height_joint.axis == (0.0, 0.0, 1.0),
        details=(
            f"parent={height_joint.parent}, child={height_joint.child}, "
            f"type={height_joint.articulation_type}, axis={height_joint.axis}"
        ),
    )
    ctx.check(
        "wall mount slide has finite edge limits",
        joints["wall_plate__mount_slide"].motion_limits is not None
        and joints["wall_plate__mount_slide"].motion_limits.lower
        < joints["wall_plate__mount_slide"].motion_limits.upper,
    )
    stage_visuals = {visual.name for visual in screen_stage.visuals}
    ctx.check(
        "screen stage remains a compact source-like connector",
        {
            f"screen_motion__{r.screen_motion}__{stage_hardware_name}",
            f"screen_motion__{r.screen_motion}__stage_mount",
            f"screen_motion__{r.screen_motion}__mount_fastener_0",
            f"screen_motion__{r.screen_motion}__mount_fastener_1",
        }.issubset(stage_visuals)
        and len(stage_visuals) == 4,
        details=f"visuals={sorted(stage_visuals)}",
    )
    ctx.check(
        "VESA support host has derived capacity",
        r.carrier_width > r.vesa_width + 2.0 * r.motion_clearance,
    )
    if r.vesa_interface == "sliding_twin_rails":
        rail_parts = [object_model.get_part(f"vesa_rail_{index}") for index in range(2)]
        rail_joints = [
            joints[f"vesa_interface__sliding_twin_rails__rail_slide_{index}"] for index in range(2)
        ]
        ctx.check(
            "source twin-rail mount has exactly two independent sliding rails",
            len(rail_parts) == 2
            and all(joint.parent == "vesa_mount" for joint in rail_joints)
            and [joint.child for joint in rail_joints] == ["vesa_rail_0", "vesa_rail_1"]
            and all(
                joint.articulation_type == ArticulationType.PRISMATIC
                and joint.axis == (1.0, 0.0, 0.0)
                for joint in rail_joints
            ),
            details=(
                f"rails={[part.name for part in rail_parts]}, "
                f"joints={[(joint.parent, joint.child, joint.axis) for joint in rail_joints]}"
            ),
        )
    ctx.check(
        "slot choices recorded",
        object_model.meta.get("slot_choices")
        == [(name, getattr(r, name)) for name in TEMPLATE_DOMAIN.slot_names],
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "compact_low_profile_depth",
        {
            "arm_topology": "fixed_low_profile_plate",
            "height_adjustment": "gas_spring_vertical_track",
            "screen_motion": "push_pull_depth_carriage",
            "vesa_interface": "sliding_twin_rails",
            "arm_scale": 0.86,
            "screen_scale": 0.88,
        },
        reason="small support family with positive depth travel and compact carrier clearance",
    ),
    corner_case(
        "open_frame_three_rail_portrait",
        {
            "arm_topology": "articulating_frame",
            "height_adjustment": "toothed_lift_track",
            "screen_motion": "portrait_roll_head",
            "vesa_interface": "bow_tie_slotted_arms",
            "arm_scale": 1.14,
            "screen_scale": 1.12,
        },
        reason="maximum brace, rack, portrait-roll and N combination",
    ),
    corner_case(
        "single_arm_universal_head",
        {
            "arm_topology": "single_arm_full_motion",
            "height_adjustment": "counterweighted_lift",
            "screen_motion": "tilt_swivel_head",
            "vesa_interface": "universal_plate",
            "hole_spacing_scale": 1.10,
        },
        reason="full-motion sleeve arm with universal plate and tilt-swivel head",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "build_tv_wall_mount",
    "build_seeded_tv_wall_mount",
    "run_tv_wall_mount_tests",
]
