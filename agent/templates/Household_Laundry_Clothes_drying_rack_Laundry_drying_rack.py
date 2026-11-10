# SPDX-License-Identifier: Apache-2.0

"""Self-contained ``Household_Laundry_Clothes_drying_rack_Laundry_drying_rack`` template.

Rebuilt from the picture origin record and the four accepted forks listed in
``articraft_template_authoring/source_maps/Household_Laundry_Clothes_drying_rack_Laundry_drying_rack.md``.

Category identity: one freestanding household laundry drying rack.  A single rigid
horizontal spine is the assembly root; folding leg frames hinge off it and reach the
floor, and drying wings hinge or slide off its side rails so the rack opens to a much
wider span than its folded footprint.  Six independent structural axes:

* ``leg_family``     - crossed scissor legs, converging A-legs, or vertical posts on
  a transverse foot bar.
* ``wing_form``      - a parallel bar ladder, a woven mesh grid shelf, a comb of
  cantilever clip fingers, or a single plain extension arm.
* ``wing_motion``    - a fold-up REVOLUTE hinge, or a telescoping PRISMATIC slide.
* ``ground_contact`` - rubber pads, swivel caster wheels, or floor-length skid bars.
* ``hanger_type``    - wire triangle hangers, clip trouser bars, or multi-clip sock
  rings, hanging on the top rail and free to sway.
* ``spine_extra``    - a scissor stiffener, a shoe cradle rung, or a towel hoop rail.

Coordinate frame: the spine is the assembly root and stands in world coordinates with
the floor at z = 0.  +X runs the spine's length, +Y is the rack's depth, and the top
rail sits at ``spine_height_m``.  Both faces are symmetric about the XZ plane, so the
gallery camera at +X/-Y sees a full silhouette.

Mechanism note: every hinge in this template is a real captured knuckle.  A moving
member carries open knuckle rings that run on the fixed rail with an authored radial
clearance, instead of declaring its own tube coaxial with the rail and suppressing the
result - ``ctx.allow_overlap`` is never called.

This file is the only runtime truth.  It imports the stdlib and the Articraft ``sdk``
only.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    CylinderGeometry,
    MeshGeometry,
    MotionLimits,
    MotionProperties,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
    tube_from_spline_points,
)

LegFamily = Literal["scissor_x_legs", "a_frame_legs", "post_base_legs"]
WingForm = Literal["parallel_bar_wing", "mesh_grid_wing", "comb_clip_wing", "single_rail_arm"]
WingMotion = Literal["fold_hinge", "telescope_slide"]
GroundContact = Literal["rubber_foot_pads", "swivel_caster_wheels", "skid_bar_feet"]
HangerType = Literal["wire_triangle", "clip_trouser_bar", "sock_clip_ring"]
SpineExtra = Literal["scissor_brace", "shoe_cradle_rung", "towel_hoop_rail"]

LEG_FAMILIES: tuple[LegFamily, ...] = ("scissor_x_legs", "a_frame_legs", "post_base_legs")
WING_FORMS: tuple[WingForm, ...] = (
    "parallel_bar_wing",
    "mesh_grid_wing",
    "comb_clip_wing",
    "single_rail_arm",
)
WING_MOTIONS: tuple[WingMotion, ...] = ("fold_hinge", "telescope_slide")
GROUND_CONTACTS: tuple[GroundContact, ...] = (
    "rubber_foot_pads",
    "swivel_caster_wheels",
    "skid_bar_feet",
)
HANGER_TYPES: tuple[HangerType, ...] = ("wire_triangle", "clip_trouser_bar", "sock_clip_ring")
SPINE_EXTRAS: tuple[SpineExtra, ...] = ("scissor_brace", "shoe_cradle_rung", "towel_hoop_rail")

BAR_COUNTS: tuple[int, ...] = (4, 5, 6, 7, 8, 9, 10)
WING_TIER_COUNTS: tuple[int, ...] = (1, 2)
LEG_FRAME_COUNTS: tuple[int, ...] = (2, 3)
HANGER_COUNTS: tuple[int, ...] = (2, 3, 4, 5, 6)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("leg_family", LEG_FAMILIES, role="leg_frame"),
        component_slot("wing_form", WING_FORMS, role="drying_wing"),
        component_slot("wing_motion", WING_MOTIONS, role="wing_kinematics"),
        component_slot("ground_contact", GROUND_CONTACTS, role="floor_interface"),
        component_slot("hanger_type", HANGER_TYPES, role="hanger"),
        component_slot("spine_extra", SPINE_EXTRAS, role="spine_accessory"),
        multiplicity_slot("bar_count", BAR_COUNTS, role="drying_bar", item_slot="wing_form"),
        multiplicity_slot(
            "wing_tier_count", WING_TIER_COUNTS, role="wing_tier", item_slot="wing_form"
        ),
        multiplicity_slot(
            "leg_frame_count", LEG_FRAME_COUNTS, role="leg_frame", item_slot="leg_family"
        ),
        multiplicity_slot("hanger_count", HANGER_COUNTS, role="hanger", item_slot="hanger_type"),
    )
)

# Independent parameter bands.  Every bound is a real rack dimension; the source
# pool's own numbers (1.76 m spine, 1.075 m top rail, 0.36 m depth, 0.48 m wing
# reach, 0.025 m caster) all sit inside them.
_SPINE_LENGTH_RANGE = (1.200, 2.100)
_SPINE_HEIGHT_RANGE = (0.860, 1.280)
_SPINE_DEPTH_RANGE = (0.260, 0.460)
_TUBE_RADIUS_RANGE = (0.0080, 0.0160)
_LEG_SPREAD_RANGE = (0.240, 0.620)
_WING_REACH_RANGE = (0.260, 0.580)
_WING_RISE_RANGE = (0.200, 0.620)
_FOLD_UPPER_RANGE = (0.550, 1.000)
_TELESCOPE_STROKE_RANGE = (0.100, 0.350)
_CONTACT_SIZE_RANGE = (0.0140, 0.0380)
_HANGER_DROP_RANGE = (0.400, 0.900)
_HANGER_WIDTH_RANGE = (0.450, 0.950)
_ACCESSORY_SPAN_RANGE = (0.180, 0.550)

# Spine station ratios, read straight off the origin record's rail table
# (model.py:L228-L279 with its top rail at z = 1.075).
_R_WING_RAIL_Z = 1.035 / 1.075
_R_LOWER_RAIL_Z = 0.785 / 1.075
_R_LOWER_BAR_Z = 0.800 / 1.075
_R_LEG_HINGE_Z = 0.775 / 1.075
_R_LOWER_BAR_Y = 0.270 / 0.180
_R_LEG_HINGE_Y = 0.285 / 0.180

_TIER_SCALE = 0.60  # var_wing_count L235-L252: the lower tier is a 0.60 copy
_KNUCKLE_CLEAR = 0.0008  # radial running fit at every captured hinge
_WELD = 0.0006  # deliberate intra-part overlap, four orders over the 1e-6 gate
_CENTRE_CLEAR = 0.055  # opposing wings may not meet over the spine centreline
_TIER_CLEAR = 0.045  # a raised lower wing stays this far under the upper wing


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class Config:
    leg_family: LegFamily = "scissor_x_legs"
    wing_form: WingForm = "parallel_bar_wing"
    wing_motion: WingMotion = "fold_hinge"
    ground_contact: GroundContact = "rubber_foot_pads"
    hanger_type: HangerType = "wire_triangle"
    spine_extra: SpineExtra = "scissor_brace"
    bar_count: int = 6
    wing_tier_count: int = 1
    leg_frame_count: int = 2
    hanger_count: int = 3
    spine_length_m: float | None = None
    spine_height_m: float | None = None
    spine_depth_m: float | None = None
    tube_radius_m: float | None = None
    leg_spread_ratio: float | None = None
    wing_reach_m: float | None = None
    wing_rise_ratio: float | None = None
    fold_upper_ratio: float | None = None
    telescope_stroke_ratio: float | None = None
    contact_size_m: float | None = None
    hanger_drop_ratio: float | None = None
    hanger_width_ratio: float | None = None
    accessory_span_ratio: float | None = None
    name: str = "freestanding_laundry_drying_rack"


@dataclass(frozen=True)
class ResolvedConfig:
    leg_family: LegFamily
    wing_form: WingForm
    wing_motion: WingMotion
    ground_contact: GroundContact
    hanger_type: HangerType
    spine_extra: SpineExtra
    bar_count: int
    wing_tier_count: int
    leg_frame_count: int
    hanger_count: int
    spine_length_m: float
    spine_height_m: float
    spine_depth_m: float
    tube_radius_m: float
    leg_spread_ratio: float
    wing_reach_m: float
    wing_rise_ratio: float
    fold_upper_ratio: float
    telescope_stroke_ratio: float
    contact_size_m: float
    hanger_drop_ratio: float
    hanger_width_ratio: float
    accessory_span_ratio: float
    # derived - spine
    half_length_m: float
    end_station_m: float
    z_top_m: float
    z_wing_rail_m: float
    z_lower_rail_m: float
    z_lower_bar_m: float
    z_leg_hinge_m: float
    top_rail_radius_m: float
    contact_headroom_m: float
    y_wing_rail_m: float
    y_lower_bar_m: float
    y_leg_hinge_m: float
    # derived - legs
    leg_drop_m: float
    leg_spread_m: float
    leg_fold_rad: float
    leg_station_pitch_m: float
    post_foot_half_m: float
    leg_stations_m: tuple[tuple[float, float], ...]  # (y station, hinge z)
    # derived - wings
    wing_rise_m: float
    # (y_rail, z_rail, reach, rise, fold_up, fold_down)
    tier_specs: tuple[tuple[float, float, float, float, float, float], ...]
    fold_lower_rad: float
    telescope_stroke_m: float
    # derived - hangers
    hanger_drop_m: float
    hanger_width_m: float
    hanger_pitch_m: float
    hanger_sway_rad: float
    hanger_stations_m: tuple[float, ...]
    # derived - accessory
    accessory_span_m: float
    cradle_root_y_m: float
    cradle_tip_y_m: float
    cradle_drop_m: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x5D2A17)
    length = rng.uniform(*_SPINE_LENGTH_RANGE)
    # A rack is much longer than it is deep; keep the sampled depth in the source
    # pool's aspect band (1.76 m over 0.36 m) instead of taking the cross product.
    depth_low = max(_SPINE_DEPTH_RANGE[0], length / 6.40)
    depth_high = min(_SPINE_DEPTH_RANGE[1], length / 3.60)
    if depth_low > depth_high:
        depth_low = depth_high = _clamp(length / 4.90, *_SPINE_DEPTH_RANGE)
    return Config(
        leg_family=choices["leg_family"],
        wing_form=choices["wing_form"],
        wing_motion=choices["wing_motion"],
        ground_contact=choices["ground_contact"],
        hanger_type=choices["hanger_type"],
        spine_extra=choices["spine_extra"],
        bar_count=int(choices["bar_count"]),
        wing_tier_count=int(choices["wing_tier_count"]),
        leg_frame_count=int(choices["leg_frame_count"]),
        hanger_count=int(choices["hanger_count"]),
        spine_length_m=round(length, 5),
        spine_height_m=round(rng.uniform(*_SPINE_HEIGHT_RANGE), 5),
        spine_depth_m=round(rng.uniform(depth_low, depth_high), 5),
        tube_radius_m=round(rng.uniform(*_TUBE_RADIUS_RANGE), 5),
        leg_spread_ratio=round(rng.uniform(*_LEG_SPREAD_RANGE), 5),
        wing_reach_m=round(rng.uniform(*_WING_REACH_RANGE), 5),
        wing_rise_ratio=round(rng.uniform(*_WING_RISE_RANGE), 5),
        fold_upper_ratio=round(rng.uniform(*_FOLD_UPPER_RANGE), 5),
        telescope_stroke_ratio=round(rng.uniform(*_TELESCOPE_STROKE_RANGE), 5),
        contact_size_m=round(rng.uniform(*_CONTACT_SIZE_RANGE), 5),
        hanger_drop_ratio=round(rng.uniform(*_HANGER_DROP_RANGE), 5),
        hanger_width_ratio=round(rng.uniform(*_HANGER_WIDTH_RANGE), 5),
        accessory_span_ratio=round(rng.uniform(*_ACCESSORY_SPAN_RANGE), 5),
    )


def _range_check(name: str, value: float, bounds: tuple[float, float]) -> None:
    low, high = bounds
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}], got {value}")


def _wing_outward(reach: float, rise: float, q: float) -> float:
    """Outward offset of the wing tip from its own hinge rail at swing angle q."""
    return reach * math.cos(q) - rise * math.sin(q)


def _wing_upward(reach: float, rise: float, q: float) -> float:
    """Height of the wing tip above its own hinge rail at swing angle q."""
    return reach * math.sin(q) + rise * math.cos(q)


def _bisect_largest(clear, low: float, high: float, *, floor: float) -> float:
    """Largest value in [low, high] that still satisfies `clear`, by bisection."""
    if clear(high):
        return high
    for _ in range(40):
        mid = (low + high) / 2.0
        if clear(mid):
            low = mid
        else:
            high = mid
    return max(low, floor)


def _solve_fold_upper(
    *,
    reach: float,
    rise: float,
    y_rail: float,
    upper_tier: tuple[tuple[tuple[float, float], tuple[float, float]], ...] | None,
    tip_margin: float,
    carrier: float,
) -> float:
    """Largest safe raise angle for one wing tier.

    Two stops, both real: opposing wings may never meet over the spine centreline,
    and a raised lower tier may never reach the upper tier's underside.  Solved by
    bisection on the tip trajectory rather than copied from the source's fixed
    0.85 rad, which was authored for one spine size only.
    """

    def clear(q: float) -> bool:
        out = _wing_outward(reach, rise, q)
        if y_rail + out < _CENTRE_CLEAR:
            return False
        if upper_tier is not None:
            # Both ends are in the LOWER tier's own rail frame.
            tip = (y_rail + out, _wing_upward(reach, rise, q))
            root = (y_rail + carrier * math.cos(q), carrier * math.sin(q))
            for upper in upper_tier:
                if _segment_distance_2d(root, tip, upper[0], upper[1]) < _TIER_CLEAR + tip_margin:
                    return False
        return True

    return _bisect_largest(clear, 0.0, 1.150, floor=0.0)


def _segment_distance_2d(a0, a1, b0, b1) -> float:
    """Shortest distance between two 2-D segments, used in the rack's YZ section."""

    def point_to_segment(p, s0, s1) -> float:
        dy, dz = s1[0] - s0[0], s1[1] - s0[1]
        denom = dy * dy + dz * dz
        if denom <= 1.0e-12:
            return math.hypot(p[0] - s0[0], p[1] - s0[1])
        t = _clamp(((p[0] - s0[0]) * dy + (p[1] - s0[1]) * dz) / denom, 0.0, 1.0)
        return math.hypot(p[0] - (s0[0] + t * dy), p[1] - (s0[1] + t * dz))

    d1 = (a1[0] - a0[0], a1[1] - a0[1])
    d2 = (b1[0] - b0[0], b1[1] - b0[1])
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cross) > 1.0e-12:
        rel = (b0[0] - a0[0], b0[1] - a0[1])
        t = (rel[0] * d2[1] - rel[1] * d2[0]) / cross
        u = (rel[0] * d1[1] - rel[1] * d1[0]) / cross
        if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
            return 0.0
    return min(
        point_to_segment(a0, b0, b1),
        point_to_segment(a1, b0, b1),
        point_to_segment(b0, a0, a1),
        point_to_segment(b1, a0, a1),
    )


def _solve_leg_fold(
    *,
    stations: tuple[tuple[float, float], ...],
    spread_ratio: float,
    contact_headroom: float,
    obstacles: tuple[tuple[tuple[float, float], tuple[float, float]], ...],
    clearance: float,
    foot_half: float,
    stand: float,
) -> float:
    """Largest fold angle every leg frame can take without meeting anything.

    Positive q swings the feet outward and up, flattening the rack - the source's own
    direction (the origin and var_caster_wheels both assert the feet RISE).  The source
    stops at a fixed 0.95 rad, which is safe only for its own two opposed frames.  With
    a declared leg_frame_count a third frame shares a side, and motion QC poses one
    joint at its limit while its neighbours stay at rest, so the real stop is a
    clearance problem in the rack's YZ section: the swinging frame is one segment from
    its hinge to its foot, every other frame at rest is another, and the spine's own
    rails are point obstacles.
    """
    frames = []
    for y_station, hinge_z in stations:
        sign = 1.0 if y_station > 1.0e-6 else -1.0
        drop = hinge_z - contact_headroom
        frames.append((y_station, hinge_z, sign, drop, drop * spread_ratio))

    def frame_shape(y_i, z_i, sign, drop, spread, q):
        """Hinge-to-foot diagonal plus the transverse foot bar, both at fold angle q."""
        foot = (
            y_i + sign * (spread * math.cos(q) + drop * math.sin(q)),
            z_i + spread * math.sin(q) - drop * math.cos(q),
        )
        # post_base_legs lands on a transverse foot bar, which is horizontal in the
        # frame's own coordinates and therefore tilts with the fold.  The other two
        # families tie their tips along X, which never appears in this section.
        bar_dir = (math.cos(q), sign * math.sin(q))
        bar = (
            (foot[0] - bar_dir[0] * foot_half, foot[1] - bar_dir[1] * foot_half),
            (foot[0] + bar_dir[0] * foot_half, foot[1] + bar_dir[1] * foot_half),
        )
        # The top cross tube rides at the frame's stand-off from the hinge axis.
        cross = (y_i + sign * stand * math.cos(q), z_i + stand * math.sin(q))
        return (((y_i, z_i), foot), bar, (cross, cross))

    limit = 1.150
    for index, (y_i, z_i, sign, drop, spread) in enumerate(frames):
        rest: list[tuple[tuple[float, float], tuple[float, float]]] = []
        for j, (y_j, z_j, s_j, dr_j, sp_j) in enumerate(frames):
            if j != index:
                rest.extend(frame_shape(y_j, z_j, s_j, dr_j, sp_j, 0.0))
        # The frame's own hinge rail and its own spine strut are excluded: its knuckles
        # legitimately wrap the one, and the other stands at an x station no knuckle
        # occupies.  Everything else on the spine is a real obstacle.
        rest.extend(other for other in obstacles if not _touches(other, (y_i, z_i)))

        def clear(
            q: float, y_i=y_i, z_i=z_i, sign=sign, drop=drop, spread=spread, rest=rest
        ) -> bool:
            for moving in frame_shape(y_i, z_i, sign, drop, spread, q):
                for other in rest:
                    if _segment_distance_2d(moving[0], moving[1], other[0], other[1]) < clearance:
                        return False
            return True

        if not clear(0.0):
            # The rest pose itself is the stop; fold no further than the build allows.
            limit = min(limit, 0.150)
            continue
        limit = min(limit, _bisect_largest(clear, 0.0, limit, floor=0.150))
    return _clamp(limit, 0.150, 1.150)


def _touches(segment, point, tol: float = 1.0e-6) -> bool:
    return any(abs(end[0] - point[0]) < tol and abs(end[1] - point[1]) < tol for end in segment)


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "leg_family": config.leg_family,
            "wing_form": config.wing_form,
            "wing_motion": config.wing_motion,
            "ground_contact": config.ground_contact,
            "hanger_type": config.hanger_type,
            "spine_extra": config.spine_extra,
            "bar_count": int(config.bar_count),
            "wing_tier_count": int(config.wing_tier_count),
            "leg_frame_count": int(config.leg_frame_count),
            "hanger_count": int(config.hanger_count),
        }
    )
    length = 1.760 if config.spine_length_m is None else float(config.spine_length_m)
    height = 1.075 if config.spine_height_m is None else float(config.spine_height_m)
    depth = 0.360 if config.spine_depth_m is None else float(config.spine_depth_m)
    tube = 0.0120 if config.tube_radius_m is None else float(config.tube_radius_m)
    spread = 0.423 if config.leg_spread_ratio is None else float(config.leg_spread_ratio)
    reach = 0.480 if config.wing_reach_m is None else float(config.wing_reach_m)
    rise_ratio = 0.427 if config.wing_rise_ratio is None else float(config.wing_rise_ratio)
    fold_ratio = 0.780 if config.fold_upper_ratio is None else float(config.fold_upper_ratio)
    stroke_ratio = (
        0.256 if config.telescope_stroke_ratio is None else float(config.telescope_stroke_ratio)
    )
    contact = 0.0250 if config.contact_size_m is None else float(config.contact_size_m)
    drop_ratio = 0.700 if config.hanger_drop_ratio is None else float(config.hanger_drop_ratio)
    width_ratio = 0.780 if config.hanger_width_ratio is None else float(config.hanger_width_ratio)
    span_ratio = (
        0.380 if config.accessory_span_ratio is None else float(config.accessory_span_ratio)
    )

    _range_check("spine_length_m", length, _SPINE_LENGTH_RANGE)
    _range_check("spine_height_m", height, _SPINE_HEIGHT_RANGE)
    _range_check("spine_depth_m", depth, _SPINE_DEPTH_RANGE)
    _range_check("tube_radius_m", tube, _TUBE_RADIUS_RANGE)
    _range_check("leg_spread_ratio", spread, _LEG_SPREAD_RANGE)
    _range_check("wing_reach_m", reach, _WING_REACH_RANGE)
    _range_check("wing_rise_ratio", rise_ratio, _WING_RISE_RANGE)
    _range_check("fold_upper_ratio", fold_ratio, _FOLD_UPPER_RANGE)
    _range_check("telescope_stroke_ratio", stroke_ratio, _TELESCOPE_STROKE_RANGE)
    _range_check("contact_size_m", contact, _CONTACT_SIZE_RANGE)
    _range_check("hanger_drop_ratio", drop_ratio, _HANGER_DROP_RANGE)
    _range_check("hanger_width_ratio", width_ratio, _HANGER_WIDTH_RANGE)
    _range_check("accessory_span_ratio", span_ratio, _ACCESSORY_SPAN_RANGE)

    half = length / 2.0
    end_station = half * 0.985
    z_top = height
    z_wing_rail = height * _R_WING_RAIL_Z
    z_lower_rail = height * _R_LOWER_RAIL_Z
    z_lower_bar = height * _R_LOWER_BAR_Z
    y_wing_rail = depth / 2.0
    y_lower_bar = y_wing_rail * _R_LOWER_BAR_Y

    # A hanger hook has to wrap the top rail and still put wire within the joint-origin
    # tolerance of the rail axis, which caps the rail at a hanger-rail diameter.  Real
    # racks do exactly this: the garment rail is lighter stock than the frame.
    top_rail_radius = min(tube, 0.0130)

    # The leg hinge rail hangs below the lower bar.  The origin record puts it 25 mm away
    # (L236-L237 vs L169) and gets away with it only because its legs declare an overlap
    # allowance; a real captured knuckle needs its own ring outside the lower bar's stock.
    leg_ring_outer = tube * 1.60 + _KNUCKLE_CLEAR
    wing_ring_outer = tube * 1.68 + _KNUCKLE_CLEAR
    leg_rail_gap = max(leg_ring_outer + wing_ring_outer + 0.006, tube * 4.6)
    y_leg_hinge = y_lower_bar
    z_leg_hinge = height * _R_LOWER_BAR_Z - leg_rail_gap

    # A caster hangs BELOW the leg tube on its own fork, so the leg gives up two radii
    # plus the fork rather than the pad's single thickness.  Every candidate still lands
    # the rack on z = 0.
    contact_headroom = (
        2.0 * contact + tube * 1.60 if config.ground_contact == "swivel_caster_wheels" else contact
    )
    leg_drop = z_leg_hinge - contact_headroom
    leg_spread = leg_drop * spread
    # Leg stations walk the spine evenly.  With N = 2 this reproduces the origin's
    # front/rear pair; the middle station of N = 3 lands on the centreline, which is
    # the mid-span leg var_leg_support_count L298-L306 builds.  That source drops the
    # centreline hinge 20 mm so its top tube clears the spine's own lower towel rail,
    # which sits on the same centreline; the drop is derived here from the tube stock
    # rather than copied, so it holds for every rail diameter.
    offsets = tuple(
        -1.0 + 2.0 * index / (int(config.leg_frame_count) - 1)
        for index in range(int(config.leg_frame_count))
    )
    cradle_root_y = 0.0
    cradle_tip_y = y_lower_bar * 0.45
    cradle_drop = min((half * span_ratio) * 0.42, (z_lower_rail - contact_headroom) * 0.35)
    leg_clearance = leg_ring_outer + tube + 0.004
    centre_obstruction = cradle_drop if config.spine_extra == "shoe_cradle_rung" else 0.0
    centre_drop = max(
        0.0, leg_clearance + 0.002 + centre_obstruction - (z_lower_rail - z_leg_hinge)
    )
    leg_stations = tuple(
        (
            round(y_leg_hinge * offset, 6),
            round(z_leg_hinge - (centre_drop if abs(offset) < 1.0e-6 else 0.0), 6),
        )
        for offset in offsets
    )
    leg_station_pitch = (
        2.0 * y_leg_hinge / max(int(config.leg_frame_count) - 1, 1)
        if int(config.leg_frame_count) > 1
        else 2.0 * y_leg_hinge
    )

    rise = reach * rise_ratio
    # The lower tier's own size comes from the headroom between the two spine rails and
    # nothing else, so the two tiers can be solved in one direction each instead of
    # chasing each other: size the lower wing, bound the upper wing's descent against it,
    # then bound the lower wing's raise against the upper wing at that descent.
    # Rest shapes of every leg frame in the rack's YZ section, so a descending wing can
    # be stopped against real structure instead of an approximated outward face.
    leg_stand = tube * 1.26 + _KNUCKLE_CLEAR + tube * 1.20
    leg_rest_shapes: list[tuple[tuple[float, float], tuple[float, float]]] = []
    for station_y, station_z in leg_stations:
        sign_leg = 1.0 if station_y > 1.0e-6 else -1.0
        station_drop = station_z - contact_headroom
        leg_rest_shapes.append(
            (
                (station_y, station_z),
                (station_y + sign_leg * station_drop * spread, station_z - station_drop),
            )
        )
        cross = (station_y + sign_leg * leg_stand, station_z)
        leg_rest_shapes.append((cross, cross))

    two_tiers = int(config.wing_tier_count) >= 2
    cap_margin = tube * 1.6
    headroom = max((z_wing_rail - z_lower_bar) - _TIER_CLEAR - cap_margin, 0.010)
    lower_reach = reach * _TIER_SCALE
    lower_rise = min(rise * _TIER_SCALE, max(headroom * 0.50, lower_reach * 0.08))
    lower_rest = (
        (y_lower_bar, z_lower_bar),
        (y_lower_bar + lower_reach, z_lower_bar + lower_rise),
    )

    tier_down: dict[int, float] = {}
    for tier_index, (tier_y, tier_z, t_reach, t_rise) in enumerate(
        (
            (y_wing_rail, z_wing_rail, reach, rise),
            (y_lower_bar, z_lower_bar, lower_reach, lower_rise),
        )
    ):
        if tier_index == 1 and not two_tiers:
            continue
        tier_stop = -0.200
        wing_carrier = tube * 2.44 + _KNUCKLE_CLEAR
        wing_leg_clear = tube * 2.0 + 0.008
        for step in range(1, 91):
            q = -0.010 * step
            carrier_pt = (
                tier_y + wing_carrier * math.cos(q),
                tier_z + wing_carrier * math.sin(q),
            )
            tip = (
                tier_y + _wing_outward(t_reach, t_rise, q),
                tier_z + _wing_upward(t_reach, t_rise, q),
            )
            if tip[1] <= contact_headroom:
                break
            # Stop A: any leg frame at rest, taken as its own hinge-to-foot diagonal plus
            # the top cross tube standing off its hinge axis.  The whole wing member is
            # tested, not just its tip: on a two-tier rack it is the lower wing's INNER
            # carrier that reaches the leg's cross tube first.
            blocked = False
            for wing_sign in (1.0, -1.0):
                seg_a = (carrier_pt[0] * wing_sign, carrier_pt[1])
                seg_b = (tip[0] * wing_sign, tip[1])
                for leg_shape in leg_rest_shapes:
                    if (
                        _segment_distance_2d(seg_a, seg_b, leg_shape[0], leg_shape[1])
                        < wing_leg_clear
                    ):
                        blocked = True
                        break
                if blocked:
                    break
            if blocked:
                break
            # Stop B: for the upper wing, the lower tier sitting at rest beneath it.
            if two_tiers and tier_index == 0:
                if (
                    _segment_distance_2d(carrier_pt, tip, lower_rest[0], lower_rest[1])
                    < _TIER_CLEAR + cap_margin
                ):
                    break
            tier_stop = q
        tier_down[tier_index] = _clamp(tier_stop, -0.900, -0.150)
    fold_lower = tier_down[0]

    cap_margin = tube * 1.6
    wing_carrier_off = tube * 2.44 + _KNUCKLE_CLEAR
    upper_fold_max = _solve_fold_upper(
        reach=reach,
        rise=rise,
        y_rail=y_wing_rail,
        upper_tier=None,
        tip_margin=cap_margin,
        carrier=wing_carrier_off,
    )
    tiers: list[tuple[float, float, float, float, float]] = [
        (
            y_wing_rail,
            z_wing_rail,
            reach,
            rise,
            round(0.220 + (upper_fold_max - 0.220) * fold_ratio, 6),
            tier_down[0],
        )
    ]
    if int(config.wing_tier_count) >= 2:
        # The upper wing at its own lowest pose, expressed in the lower tier's rail frame.
        dz = z_wing_rail - z_lower_bar
        upper_top = tiers[0][4]
        upper_poses = []
        for index in range(7):
            q_u = tier_down[0] + (upper_top - tier_down[0]) * index / 6.0
            upper_poses.append(
                (
                    (
                        y_wing_rail + wing_carrier_off * math.cos(q_u),
                        dz + wing_carrier_off * math.sin(q_u),
                    ),
                    (
                        y_wing_rail + _wing_outward(reach, rise, q_u),
                        dz + _wing_upward(reach, rise, q_u),
                    ),
                )
            )
        upper_low = tuple(upper_poses)
        lower_fold_max = _solve_fold_upper(
            reach=lower_reach,
            rise=lower_rise,
            y_rail=y_lower_bar,
            upper_tier=upper_low,
            tip_margin=cap_margin,
            carrier=wing_carrier_off,
        )
        tiers.append(
            (
                y_lower_bar,
                z_lower_bar,
                lower_reach,
                lower_rise,
                round(lower_fold_max, 6),
                tier_down[1],
            )
        )

    # Folding down, the wing tip swings outward and slightly below its rail; the stop
    # is the leg frame's own outward face at that height, not a fixed source constant.

    # The spine's whole YZ section, because a folding frame sweeps across all of it.
    spine_obstacles: list[tuple[tuple[float, float], tuple[float, float]]] = [
        ((0.0, z_top), (0.0, z_lower_rail)),  # centre post
        ((-y_wing_rail, z_wing_rail), (y_wing_rail, z_wing_rail)),  # end top cross
        ((-y_lower_bar, z_lower_bar), (y_lower_bar, z_lower_bar)),  # end lower cross
        ((y_wing_rail, z_wing_rail), (y_lower_bar, z_lower_bar)),  # front end strut
        ((-y_wing_rail, z_wing_rail), (-y_lower_bar, z_lower_bar)),  # rear end strut
    ]
    for station_y, station_z in leg_stations:
        root_z = z_lower_rail if abs(station_y) < 1.0e-6 else z_lower_bar
        spine_obstacles.append(((station_y, root_z), (station_y, station_z)))
    # The shoe cradle hangs under the spine on the centreline, so a centreline leg
    # station drops below it (see centre_drop above) and the fold solver sees it too.
    if config.spine_extra == "shoe_cradle_rung":
        for sign_y in (1.0, -1.0):
            spine_obstacles.append(
                (
                    (cradle_root_y * sign_y, z_lower_rail),
                    (cradle_tip_y * sign_y, z_lower_rail - cradle_drop),
                )
            )
    # A folding leg also has to clear the drying wings hanging beside it.  The wings'
    # own down stop was solved against the legs at rest, so the leg's up stop is solved
    # against the wings at their lowest pose - one direction each, no circularity.
    for tier_y, tier_z, t_reach, t_rise, _tier_up, tier_dn in tiers:
        wing_q = tier_dn if config.wing_motion == "fold_hinge" else 0.0
        # The wing's own inner carrier tube stands off its rail and swings with it, so it
        # is a separate obstacle from the wing surface running out to the tip.
        carrier = tube * 2.44 + _KNUCKLE_CLEAR
        carrier_pt = (
            tier_y + carrier * math.cos(wing_q),
            tier_z + carrier * math.sin(wing_q),
        )
        tip_pt = (
            tier_y + _wing_outward(t_reach, t_rise, wing_q),
            tier_z + _wing_upward(t_reach, t_rise, wing_q),
        )
        for sign_y in (1.0, -1.0):
            spine_obstacles.append(
                (
                    ((carrier_pt[0]) * sign_y, carrier_pt[1]),
                    ((carrier_pt[0]) * sign_y, carrier_pt[1]),
                )
            )
            spine_obstacles.append(
                (((carrier_pt[0]) * sign_y, carrier_pt[1]), ((tip_pt[0]) * sign_y, tip_pt[1]))
            )

    post_foot_half = _clamp(
        (z_leg_hinge - contact_headroom) * 0.10, tube * 4.0, leg_station_pitch * 0.30
    )
    leg_fold = _solve_leg_fold(
        stations=leg_stations,
        spread_ratio=spread,
        contact_headroom=contact_headroom,
        obstacles=tuple(spine_obstacles),
        clearance=leg_clearance,
        stand=tube * 1.26 + _KNUCKLE_CLEAR + tube * 1.20,
        foot_half=max(
            post_foot_half if config.leg_family == "post_base_legs" else 0.0,
            contact_headroom * 0.9,
        ),
    )

    telescope_stroke = length * stroke_ratio

    # A hanger's body is not its whole envelope: the clip carriers hang below the bar
    # and stand proud of it, and the sway joint swings that envelope sideways between
    # the two wing hinge rails.  Both stops are derived from the envelope, not assumed.
    hanger_wire = max(tube * 0.30, 0.0022)
    hanger_lateral = max(depth / 2.0 - tube - 0.008, 0.006)
    # The body plus its clips has to sit between the two wing hinge rails at rest, and the
    # clip size follows the body width, so the band is solved rather than assumed.
    _MIN_SWAY = 0.030
    hanger_usable_width = max(depth - 2.0 * tube - 0.014, 0.040)
    hanger_width = hanger_usable_width * width_ratio
    hanger_clip = max(hanger_width * 0.07, hanger_wire * 3.0)
    hanger_headroom = max(z_top - z_lower_rail - 0.030 - hanger_clip * 1.8, 0.030)
    hanger_drop = hanger_headroom * drop_ratio
    # The body plus its clips has to stay between the two wing hinge rails not only at
    # rest but through the smallest sway worth calling a joint, and the clip size follows
    # the body width, so the band is solved rather than assumed.
    for _ in range(30):
        hanger_clip = max(hanger_width * 0.07, hanger_wire * 3.0)
        hanger_headroom = max(z_top - z_lower_rail - 0.030 - hanger_clip * 1.8, 0.030)
        hanger_drop = hanger_headroom * drop_ratio
        swept = (hanger_width / 2.0 + hanger_clip) * math.cos(_MIN_SWAY) + (
            hanger_drop + hanger_clip * 1.8
        ) * math.sin(_MIN_SWAY)
        if swept <= hanger_lateral - 0.003:
            break
        hanger_width *= 0.92
    hanger_run = end_station * 2.0 * 0.86
    hanger_pitch = hanger_run / float(int(config.hanger_count))
    hanger_stations = tuple(
        round(-hanger_run / 2.0 + hanger_pitch * (index + 0.5), 6)
        for index in range(int(config.hanger_count))
    )

    # Sway is bounded by the lateral clearance to the wing hinge rails.  A hanger's
    # outermost point does not sit on the centreline, so the swing that reaches a rail is
    # the ARC from that point's rest angle: over every point (L, h) of the body the swept
    # offset is `L*cos(s) + h*sin(s)`, worst at the widest L and the deepest h, which is
    # `hypot(L, h) * sin(s + atan2(L, h))`.  The sock ring is the binding form - its clip
    # arms fan out horizontally from a hub that already hangs most of the drop.
    hanger_reach = hanger_width / 2.0 + hanger_clip
    hanger_depth = hanger_drop + hanger_clip * 1.8
    hanger_envelope = math.hypot(hanger_reach, hanger_depth)
    hanger_rest_angle = math.atan2(hanger_reach, hanger_depth)
    hanger_sway = math.asin(_clamp((hanger_lateral - 0.003) / max(hanger_envelope, 1e-6), 0.0, 1.0))
    hanger_sway = _clamp(hanger_sway - hanger_rest_angle, _MIN_SWAY, 0.26)

    accessory_span = half * span_ratio

    return ResolvedConfig(
        leg_family=config.leg_family,
        wing_form=config.wing_form,
        wing_motion=config.wing_motion,
        ground_contact=config.ground_contact,
        hanger_type=config.hanger_type,
        spine_extra=config.spine_extra,
        bar_count=int(config.bar_count),
        wing_tier_count=int(config.wing_tier_count),
        leg_frame_count=int(config.leg_frame_count),
        hanger_count=int(config.hanger_count),
        spine_length_m=length,
        spine_height_m=height,
        spine_depth_m=depth,
        tube_radius_m=tube,
        leg_spread_ratio=spread,
        wing_reach_m=reach,
        wing_rise_ratio=rise_ratio,
        fold_upper_ratio=fold_ratio,
        telescope_stroke_ratio=stroke_ratio,
        contact_size_m=contact,
        hanger_drop_ratio=drop_ratio,
        hanger_width_ratio=width_ratio,
        accessory_span_ratio=span_ratio,
        half_length_m=half,
        end_station_m=end_station,
        z_top_m=z_top,
        z_wing_rail_m=z_wing_rail,
        z_lower_rail_m=z_lower_rail,
        z_lower_bar_m=z_lower_bar,
        z_leg_hinge_m=z_leg_hinge,
        top_rail_radius_m=top_rail_radius,
        contact_headroom_m=contact_headroom,
        y_wing_rail_m=y_wing_rail,
        y_lower_bar_m=y_lower_bar,
        y_leg_hinge_m=y_leg_hinge,
        leg_drop_m=leg_drop,
        leg_spread_m=leg_spread,
        leg_fold_rad=leg_fold,
        leg_station_pitch_m=leg_station_pitch,
        post_foot_half_m=post_foot_half,
        leg_stations_m=leg_stations,
        wing_rise_m=rise,
        tier_specs=tuple(tiers),
        fold_lower_rad=fold_lower,
        telescope_stroke_m=telescope_stroke,
        hanger_drop_m=hanger_drop,
        hanger_width_m=hanger_width,
        hanger_pitch_m=hanger_pitch,
        hanger_sway_rad=hanger_sway,
        hanger_stations_m=hanger_stations,
        accessory_span_m=accessory_span,
        cradle_root_y_m=cradle_root_y,
        cradle_tip_y_m=cradle_tip_y,
        cradle_drop_m=cradle_drop,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("leg_family", config.leg_family),
        ("wing_form", config.wing_form),
        ("wing_motion", config.wing_motion),
        ("ground_contact", config.ground_contact),
        ("hanger_type", config.hanger_type),
        ("spine_extra", config.spine_extra),
        ("bar_count", int(config.bar_count)),
        ("wing_tier_count", int(config.wing_tier_count)),
        ("leg_frame_count", int(config.leg_frame_count)),
        ("hanger_count", int(config.hanger_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Materials and tube primitives (origin record model.py:L34-L104)
# --------------------------------------------------------------------------- #
def _materials(model: ArticulatedObject, seed_tint: int) -> dict[str, str]:
    frames = (
        (0.72, 0.74, 0.74),
        (0.88, 0.89, 0.90),
        (0.36, 0.38, 0.40),
        (0.80, 0.72, 0.60),
    )
    frame_rgb = frames[seed_tint % len(frames)]
    model.material("rack_tube", rgba=(*frame_rgb, 1.0))
    model.material("dark_fitting", rgba=(0.08, 0.085, 0.085, 1.0))
    model.material("black_plastic", rgba=(0.05, 0.05, 0.05, 1.0))
    model.material("pale_fitting", rgba=(0.78, 0.80, 0.80, 1.0))
    model.material("hanger_wire", rgba=(0.38, 0.37, 0.35, 1.0))
    return {
        "tube": "rack_tube",
        "fitting": "dark_fitting",
        "black": "black_plastic",
        "pale": "pale_fitting",
        "hanger": "hanger_wire",
    }


def _cylinder_between(start, end, radius: float, *, radial_segments: int = 16) -> MeshGeometry:
    """Closed circular tube between two local points."""
    p0 = (float(start[0]), float(start[1]), float(start[2]))
    p1 = (float(end[0]), float(end[1]), float(end[2]))
    vx, vy, vz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    length = math.sqrt(vx * vx + vy * vy + vz * vz)
    if length <= 1.0e-8:
        raise ValueError("tube endpoints must be distinct")
    geom = CylinderGeometry(radius, length, radial_segments=radial_segments, closed=True)
    direction = (vx / length, vy / length, vz / length)
    angle = math.acos(_clamp(direction[2], -1.0, 1.0))
    axis = (-direction[1], direction[0], 0.0)
    axis_len = math.sqrt(axis[0] * axis[0] + axis[1] * axis[1])
    if axis_len > 1.0e-8:
        geom.rotate((axis[0] / axis_len, axis[1] / axis_len, 0.0), angle)
    elif direction[2] < 0.0:
        geom.rotate((1.0, 0.0, 0.0), math.pi)
    geom.translate((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0, (p0[2] + p1[2]) / 2.0)
    return geom


def _merged(segments, *, radial_segments: int = 16) -> MeshGeometry:
    merged = MeshGeometry()
    for start, end, radius in segments:
        merged.merge(_cylinder_between(start, end, radius, radial_segments=radial_segments))
    return merged


def _frame_visual(part, name: str, segments, material: str, *, radial_segments: int = 16) -> None:
    part.visual(
        mesh_from_geometry(_merged(segments, radial_segments=radial_segments), name),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _knuckle_segments(x: float, ring_radius: float, wire: float, attach: tuple[float, float]):
    """One open hinge knuckle: a C of chords that runs on the fixed rail.

    `attach` is the (y, z) station of the member's own tube in the same local frame.
    The C wraps the rail with a `_KNUCKLE_CLEAR` running fit, its gap faces away from
    that tube, and a bridge ties the ring to the tube so the member is one connected
    body.  Nothing is coaxial with the rail, which is what replaces the source pool's
    `allow_overlap` on this interface.
    """
    phi = math.atan2(attach[0], attach[1])
    segments = []
    steps = 8
    start_angle = phi + math.radians(210.0)
    sweep = math.radians(300.0)
    step_angle = sweep / steps
    overlap = min(step_angle * 0.45, wire / max(ring_radius, 1.0e-6))

    def ring_point(angle: float) -> tuple[float, float, float]:
        return (x, ring_radius * math.sin(angle), ring_radius * math.cos(angle))

    for index in range(steps):
        a0 = start_angle + step_angle * index
        a1 = a0 + step_angle
        lo = a0 if index == 0 else a0 - overlap
        hi = a1 if index == steps - 1 else a1 + overlap
        segments.append((ring_point(lo), ring_point(hi), wire))
    bridge_root = (x, ring_radius * math.sin(phi), ring_radius * math.cos(phi))
    segments.append((bridge_root, (x, attach[0], attach[1]), wire))
    return segments


# --------------------------------------------------------------------------- #
# Spine (template core - origin record model.py:L228-L279)
# --------------------------------------------------------------------------- #
def _build_spine(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    spine = model.part("main_frame", meta={"role": "spine"})
    end = r.end_station_m
    t = r.tube_radius_m
    segments = [
        ((-end, 0.0, r.z_top_m), (end, 0.0, r.z_top_m), r.top_rail_radius_m),
        ((-end, 0.0, r.z_lower_rail_m), (end, 0.0, r.z_lower_rail_m), t),
    ]
    for sign in (1.0, -1.0):
        y_wing = r.y_wing_rail_m * sign
        y_bar = r.y_lower_bar_m * sign
        segments.append(((-end, y_wing, r.z_wing_rail_m), (end, y_wing, r.z_wing_rail_m), t))
        segments.append(((-end, y_bar, r.z_lower_bar_m), (end, y_bar, r.z_lower_bar_m), t))
    # Leg hinge rails, one per declared leg station.
    for station, hinge_z in r.leg_stations_m:
        segments.append(((-end, station, hinge_z), (end, station, hinge_z), t * 0.92))
    # End cross members and centre posts tie every rail into one rigid body.
    for x in (-end, end):
        segments.append(
            (
                (x, -r.y_wing_rail_m, r.z_wing_rail_m),
                (x, r.y_wing_rail_m, r.z_wing_rail_m),
                t * 0.84,
            )
        )
        segments.append(
            (
                (x, -r.y_lower_bar_m, r.z_lower_bar_m),
                (x, r.y_lower_bar_m, r.z_lower_bar_m),
                t * 0.84,
            )
        )
        segments.append(((x, 0.0, r.z_top_m), (x, 0.0, r.z_lower_rail_m), t * 0.84))
        segments.append(
            ((x, r.y_wing_rail_m, r.z_wing_rail_m), (x, r.y_lower_bar_m, r.z_lower_bar_m), t * 0.75)
        )
        segments.append(
            (
                (x, -r.y_wing_rail_m, r.z_wing_rail_m),
                (x, -r.y_lower_bar_m, r.z_lower_bar_m),
                t * 0.75,
            )
        )
        for station, hinge_z in r.leg_stations_m:
            if abs(station) < 1.0e-6:
                segments.append(((x, 0.0, r.z_lower_rail_m), (x, 0.0, hinge_z), t * 0.7))
            else:
                near_y = r.y_lower_bar_m if station > 0.0 else -r.y_lower_bar_m
                segments.append(((x, near_y, r.z_lower_bar_m), (x, station, hinge_z), t * 0.7))
    _frame_visual(spine, "spine_tube_frame", segments, mats["tube"], radial_segments=18)

    cap = t * 2.3
    for x in (-end, end):
        for y, z in ((0.0, r.z_top_m), (0.0, r.z_lower_rail_m)):
            spine.visual(
                Box((cap, cap, cap)),
                origin=Origin(xyz=(x + (cap * 0.30 if x > 0 else -cap * 0.30), y, z)),
                material=mats["black"],
                name=f"end_cap_{'p' if x > 0 else 'm'}_{y:+.3f}_{z:+.3f}".replace(".", "_"), material_class_id="plastic.opaque_glossy_molded",
            )
    return spine


# --------------------------------------------------------------------------- #
# leg_family candidates
# --------------------------------------------------------------------------- #
_NEST_INSET = 0.93  # folding members stop short of the spine's own end frames


def _leg_common(r: ResolvedConfig):
    """Shared leg geometry facts: hinge span, tube stock and knuckle ring radius."""
    hx = r.end_station_m * _NEST_INSET
    t = r.tube_radius_m
    ring = t * 0.92 + _KNUCKLE_CLEAR + t * 0.34
    return hx, t, ring


def _leg_knuckles(r: ResolvedConfig, ring: float, wire: float, attach: tuple[float, float]):
    """Four knuckles per leg frame, evenly spread so long racks stay stiff."""
    hx = r.end_station_m * _NEST_INSET
    segments = []
    for index in range(4):
        x = -hx * 0.94 + (hx * 1.88) * index / 3.0
        segments.extend(_knuckle_segments(x, ring, wire, attach))
    return segments


def _leg_family_scissor_x_legs_build(
    model, r: ResolvedConfig, mats, *, name: str, y_sign: float, drop: float
):
    """Origin record model.py:L137-L172 - a splayed pair crossing its opposite frame."""
    hx, t, ring = _leg_common(r)
    part = model.part(name, meta={"role": "leg_frame", "leg_family": "scissor_x_legs"})
    stand = ring + t * 1.20
    spread = drop * r.leg_spread_ratio * y_sign
    top_y = stand * y_sign
    segments = list(_leg_knuckles(r, ring, t * 0.34, (top_y, 0.0)))
    segments.append(((-hx, top_y, 0.0), (hx, top_y, 0.0), t * 0.92))
    for x in (-hx, hx):
        segments.append(((x, top_y, 0.0), (x, spread, -drop), t))
    segments.append(((-hx, spread, -drop), (hx, spread, -drop), t * 0.78))
    mid_y = top_y + (spread - top_y) * 0.5
    segments.append(((-hx, mid_y, -drop * 0.5), (hx, mid_y, -drop * 0.5), t * 0.62))
    _frame_visual(part, "leg_tube_frame", segments, mats["tube"], radial_segments=12)
    tips = ((-hx, spread, -drop), (hx, spread, -drop))
    return part, tips


def _leg_family_a_frame_legs_build(
    model, r: ResolvedConfig, mats, *, name: str, y_sign: float, drop: float
):
    """Reference 002.png - the pair converges to a narrow foot and closes at the floor."""
    hx, t, ring = _leg_common(r)
    part = model.part(name, meta={"role": "leg_frame", "leg_family": "a_frame_legs"})
    stand = ring + t * 1.20
    spread = drop * r.leg_spread_ratio * y_sign
    top_y = stand * y_sign
    foot_hx = hx * 0.44
    segments = list(_leg_knuckles(r, ring, t * 0.34, (top_y, 0.0)))
    segments.append(((-hx, top_y, 0.0), (hx, top_y, 0.0), t * 0.92))
    for x_top, x_foot in ((-hx, -foot_hx), (hx, foot_hx)):
        segments.append(((x_top, top_y, 0.0), (x_foot, spread, -drop), t))
    # Floor-level tie bar: the closed base of the A, absent from the scissor frame.
    segments.append(((-foot_hx, spread, -drop), (foot_hx, spread, -drop), t * 0.86))
    mid_y = top_y + (spread - top_y) * 0.55
    segments.append(((-hx * 0.72, mid_y, -drop * 0.55), (hx * 0.72, mid_y, -drop * 0.55), t * 0.62))
    _frame_visual(part, "leg_tube_frame", segments, mats["tube"], radial_segments=12)
    tips = ((-foot_hx, spread, -drop), (foot_hx, spread, -drop))
    return part, tips


def _leg_family_post_base_legs_build(
    model, r: ResolvedConfig, mats, *, name: str, y_sign: float, drop: float
):
    """Reference 001.png - one vertical post per end landing on a transverse foot bar."""
    hx, t, ring = _leg_common(r)
    part = model.part(name, meta={"role": "leg_frame", "leg_family": "post_base_legs"})
    stand = ring + t * 1.20
    top_y = stand * y_sign
    spread = drop * r.leg_spread_ratio
    post_y = top_y + (spread * 0.22) * y_sign
    foot_half = r.post_foot_half_m
    segments = list(_leg_knuckles(r, ring, t * 0.34, (top_y, 0.0)))
    segments.append(((-hx, top_y, 0.0), (hx, top_y, 0.0), t * 0.92))
    for x in (-hx, hx):
        segments.append(((x, top_y, 0.0), (x, post_y, -drop), t * 1.22))
        segments.append(((x, post_y - foot_half, -drop), (x, post_y + foot_half, -drop), t * 0.80))
    _frame_visual(part, "leg_tube_frame", segments, mats["tube"], radial_segments=12)
    tips = ((-hx, post_y, -drop), (hx, post_y, -drop))
    return part, tips


_LEG_BUILDERS = {
    "scissor_x_legs": _leg_family_scissor_x_legs_build,
    "a_frame_legs": _leg_family_a_frame_legs_build,
    "post_base_legs": _leg_family_post_base_legs_build,
}


# --------------------------------------------------------------------------- #
# ground_contact candidates
# --------------------------------------------------------------------------- #
def _ground_contact_rubber_foot_pads_build(model, r, mats, part, tips, *, prefix: str):
    """Origin record model.py:L156-L162 - a moulded cap over each tube end."""
    size = r.contact_size_m
    for index, (x, y, z) in enumerate(tips):
        part.visual(
            Box((size * 2.6, size * 1.8, size)),
            origin=Origin(xyz=(x, y, z - size / 2.0 + _WELD)),
            material=mats["black"],
            name=f"{prefix}__rubber_foot_{index}", material_class_id="rubber.smooth_plain",
        )
    return []


def _ground_contact_skid_bar_feet_build(model, r, mats, part, tips, *, prefix: str):
    """Reference 002.png - one floor-length bar per frame instead of point pads."""
    size = r.contact_size_m
    (x0, y0, z0), (x1, y1, z1) = tips
    segments = [((x0, y0, z0 - size / 2.0), (x1, y1, z1 - size / 2.0), size / 2.0)]
    part.visual(
        mesh_from_geometry(_merged(segments, radial_segments=14), f"{prefix}__skid_bar"),
        material=mats["black"],
        name=f"{prefix}__skid_bar", material_class_id="rubber.smooth_plain",
    )
    for index, (x, y, z) in enumerate(tips):
        part.visual(
            Box((size * 1.1, size * 1.5, size * 1.2)),
            origin=Origin(xyz=(x, y, z - size / 2.0)),
            material=mats["black"],
            name=f"{prefix}__skid_cap_{index}", material_class_id="rubber.smooth_plain",
        )
    return []


def _ground_contact_swivel_caster_wheels_build(model, r, mats, part, tips, *, prefix: str):
    """var_caster_wheels model.py:L161-L195 - a rolling part on each leg tip."""
    radius = r.contact_size_m
    width = max(radius * 0.72, 0.010)
    joints: list[str] = []
    for index, (x, y, z) in enumerate(tips):
        wheel = model.part(
            f"{prefix}__caster_wheel_{index}",
            meta={"role": "caster_wheel"},
        )
        # Deviation from var_caster_wheels L161-L195, recorded in the SourceMap: its
        # `WheelGeometry` is bored through, and the bored solid tessellates into two
        # geometry components at every size in this template's caster band (measured
        # 2026-08-01 across radius 0.014-0.038 m, with and without rim flange and bead
        # seat).  The intra-part connectivity gate rejects that, and no external bridge
        # closes it.  A caster this small is a solid disc anyway, so the wheel is one
        # welded body: a running tread plus a proud hub boss on both faces.
        wheel.visual(
            mesh_from_geometry(
                _merged(
                    [
                        ((-width * 0.5, 0.0, 0.0), (width * 0.5, 0.0, 0.0), radius),
                        ((-width * 0.62, 0.0, 0.0), (width * 0.62, 0.0, 0.0), radius * 0.42),
                    ],
                    radial_segments=22,
                ),
                f"caster_wheel_{index}",
            ),
            material=mats["fitting"],
            name=f"caster_wheel_{index}", material_class_id="rubber.smooth_plain",
        )
        # The leg tube stops above the wheel; a fork straddles it and reaches the hub
        # boss on two stub axles, so the two parts share no solid at any pose.
        axle_z = z - (r.contact_headroom_m - radius)
        cheek_x = width * 0.70 + r.tube_radius_m * 1.00
        fork = [
            ((x - cheek_x, y, z), (x - cheek_x, y, axle_z), r.tube_radius_m * 0.50),
            ((x + cheek_x, y, z), (x + cheek_x, y, axle_z), r.tube_radius_m * 0.50),
            ((x - cheek_x, y, z), (x + cheek_x, y, z), r.tube_radius_m * 0.50),
            ((x - cheek_x, y, axle_z), (x - width * 0.66, y, axle_z), radius * 0.15),
            ((x + cheek_x, y, axle_z), (x + width * 0.66, y, axle_z), radius * 0.15),
        ]
        part.visual(
            mesh_from_geometry(_merged(fork, radial_segments=12), f"{prefix}__caster_fork_{index}"),
            material=mats["fitting"],
            name=f"{prefix}__caster_fork_{index}", material_class_id="metal.blackened_gunmetal",
        )
        joint = f"{prefix}__to_caster_wheel_{index}"
        provider = AxisInterface(
            name=f"{joint}__provider",
            point=(x, y, axle_z),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=radius * 0.17 + _KNUCKLE_CLEAR,
        )
        consumer = AxisInterface(
            name=f"{joint}__consumer",
            point=(0.0, 0.0, 0.0),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=radius * 0.17,
        )
        mate = mate_axes(provider, consumer)
        model.articulation(
            joint,
            ArticulationType.CONTINUOUS,
            parent=part,
            child=wheel,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(effort=2.0, velocity=10.0),
            motion_properties=MotionProperties(damping=0.4, friction=0.2),
            meta={"mechanism": "caster roll"},
        )
        register_interface_mate(model, joint, mate)
        joints.append(joint)
    return joints


_GROUND_BUILDERS = {
    "rubber_foot_pads": _ground_contact_rubber_foot_pads_build,
    "swivel_caster_wheels": _ground_contact_swivel_caster_wheels_build,
    "skid_bar_feet": _ground_contact_skid_bar_feet_build,
}


# --------------------------------------------------------------------------- #
# wing_form candidates
#
# Every wing is authored in a child frame whose origin sits ON its hinge rail with
# +X along the rail.  Local +Y is outboard for that side, so the same builder serves
# both sides and the joint axis carries the sign.
# --------------------------------------------------------------------------- #
def _wing_common(r: ResolvedConfig, reach_m: float, rise_m: float, y_sign: float):
    t = r.tube_radius_m
    ring = t + _KNUCKLE_CLEAR + t * 0.34
    stand = (ring + t * 1.10) * y_sign
    return (r.end_station_m * _NEST_INSET, t, ring, stand, reach_m * y_sign, rise_m)


def _wing_carrier_segments(r: ResolvedConfig, reach_m: float, rise_m: float, y_sign: float):
    """Knuckles plus the inner carrier tube every wing surface is built on."""
    hx, t, ring, stand, reach, rise = _wing_common(r, reach_m, rise_m, y_sign)
    slide = r.telescope_stroke_m if r.wing_motion == "telescope_slide" else 0.0
    lo, hi = (-hx * 0.94, hx * 0.94 - slide) if y_sign > 0.0 else (-hx * 0.94 + slide, hx * 0.94)
    segments = list()
    for index in range(4):
        x = lo + (hi - lo) * index / 3.0
        segments.extend(_knuckle_segments(x, ring, t * 0.34, (stand, 0.0)))
    segments.append(((-hx, stand, 0.0), (hx, stand, 0.0), t * 0.80))
    return segments


def _wing_form_parallel_bar_wing_build(
    model, r, mats, *, name: str, reach: float, rise: float, y_sign: float
):
    """var_bar_count model.py:L182-L207 - a ladder of individually named bars."""
    hx, t, ring, stand, reach, rise = _wing_common(r, reach, rise, y_sign)
    part = model.part(name, meta={"role": "drying_wing", "wing_form": "parallel_bar_wing"})
    segments = _wing_carrier_segments(r, reach, rise, y_sign)
    for x in (-hx, hx):
        segments.append(((x, stand, 0.0), (x, reach, rise), t * 0.86))
    for index in range(r.bar_count):
        frac = 0.0 if r.bar_count == 1 else index / float(r.bar_count - 1)
        frac = 0.12 + 0.88 * frac
        y = stand + (reach - stand) * frac
        z = rise * frac
        radius = t * 0.92 if index in (0, r.bar_count - 1) else t * 0.66
        segments.append(((-hx, y, z), (hx, y, z), radius))
    _frame_visual(part, "wing_tube_frame", segments, mats["tube"], radial_segments=13)
    _wing_end_caps(part, r, mats, hx, reach, rise, name)
    return part


def _wing_form_mesh_grid_wing_build(
    model, r, mats, *, name: str, reach: float, rise: float, y_sign: float
):
    """var_mesh_shelf model.py:L194-L238 - a closed frame filled with a woven lattice."""
    hx, t, ring, stand, reach, rise = _wing_common(r, reach, rise, y_sign)
    part = model.part(name, meta={"role": "drying_wing", "wing_form": "mesh_grid_wing"})
    segments = _wing_carrier_segments(r, reach, rise, y_sign)
    for x in (-hx, hx):
        segments.append(((x, stand, 0.0), (x, reach, rise), t * 0.86))
    segments.append(((-hx, reach, rise), (hx, reach, rise), t * 0.92))
    _frame_visual(part, "wing_tube_frame", segments, mats["tube"], radial_segments=13)

    wire = max(t * 0.24, 0.0018)
    grid = MeshGeometry()
    cross_x = hx
    lo, hi = 0.06, 0.96
    for index in range(r.bar_count):
        frac = lo + (hi - lo) * (index + 0.5) / float(r.bar_count)
        y = stand + (reach - stand) * frac
        z = rise * frac
        grid.merge(_cylinder_between((-cross_x, y, z), (cross_x, y, z), wire, radial_segments=9))
    long_count = max(4, int(round(r.bar_count * 1.7)))
    y_lo, z_lo = stand + (reach - stand) * lo, rise * lo
    y_hi, z_hi = stand + (reach - stand) * hi, rise * hi
    for index in range(long_count):
        x = -cross_x + 2.0 * cross_x * (index + 0.5) / float(long_count)
        grid.merge(_cylinder_between((x, y_lo, z_lo), (x, y_hi, z_hi), wire, radial_segments=9))
    part.visual(mesh_from_geometry(grid, "wing_grid"), material=mats["tube"], name="wing_grid", material_class_id="metal.mesh_chainmail")
    _wing_end_caps(part, r, mats, hx, reach, rise, name)
    return part


def _wing_form_comb_clip_wing_build(
    model, r, mats, *, name: str, reach: float, rise: float, y_sign: float
):
    """Reference 002.png - fingers cantilever inboard off one outer rail."""
    hx, t, ring, stand, reach, rise = _wing_common(r, reach, rise, y_sign)
    part = model.part(name, meta={"role": "drying_wing", "wing_form": "comb_clip_wing"})
    segments = _wing_carrier_segments(r, reach, rise, y_sign)
    for x in (-hx, hx):
        segments.append(((x, stand, 0.0), (x, reach, rise), t * 0.86))
    segments.append(((-hx, reach, rise), (hx, reach, rise), t * 1.00))
    finger_frac = 0.52
    y_free = reach + (stand - reach) * finger_frac
    z_free = rise + (0.0 - rise) * finger_frac
    for index in range(r.bar_count):
        x = -hx * 0.88 + (hx * 1.76) * (index + 0.5) / float(r.bar_count)
        segments.append(((x, reach, rise), (x, y_free, z_free), t * 0.52))
    _frame_visual(part, "wing_tube_frame", segments, mats["tube"], radial_segments=12)
    clip = t * 1.5
    for index in range(r.bar_count):
        x = -hx * 0.88 + (hx * 1.76) * (index + 0.5) / float(r.bar_count)
        part.visual(
            Box((clip * 0.8, clip, clip * 1.4)),
            origin=Origin(xyz=(x, y_free, z_free)),
            material=mats["black"],
            name=f"comb_clip_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    _wing_end_caps(part, r, mats, hx, reach, rise, name)
    return part


def _wing_form_single_rail_arm_build(
    model, r, mats, *, name: str, reach: float, rise: float, y_sign: float
):
    """Reference 001.png - one plain extension rail on two end struts."""
    hx, t, ring, stand, reach, rise = _wing_common(r, reach, rise, y_sign)
    part = model.part(name, meta={"role": "drying_wing", "wing_form": "single_rail_arm"})
    segments = _wing_carrier_segments(r, reach, rise, y_sign)
    for x in (-hx, hx):
        segments.append(((x, stand, 0.0), (x, reach, rise), t * 1.05))
    segments.append(((-hx, reach, rise), (hx, reach, rise), t * 1.15))
    # Small drop hooks under the free rail: the only thing hung on a plain arm.
    hook_drop = max(rise * 0.22, t * 3.0)
    hook_span = hook_drop * 0.55 * y_sign
    for index in range(r.bar_count):
        x = -hx * 0.84 + (hx * 1.68) * (index + 0.5) / float(r.bar_count)
        segments.append(((x, reach, rise), (x, reach, rise - hook_drop), t * 0.34))
        segments.append(
            ((x, reach, rise - hook_drop), (x, reach - hook_span, rise - hook_drop), t * 0.34)
        )
    _frame_visual(part, "wing_tube_frame", segments, mats["tube"], radial_segments=12)
    _wing_end_caps(part, r, mats, hx, reach, rise, name)
    return part


def _wing_end_caps(part, r, mats, hx: float, reach: float, rise: float, name: str) -> None:
    cap = r.tube_radius_m * 2.2
    for index, x in enumerate((-hx, hx)):
        part.visual(
            Box((cap, cap, cap)),
            origin=Origin(xyz=(x + (cap * 0.3 if x > 0 else -cap * 0.3), reach, rise)),
            material=mats["black"],
            name=f"wing_outer_cap_{index}", material_class_id="plastic.opaque_glossy_molded",
        )


_WING_BUILDERS = {
    "parallel_bar_wing": _wing_form_parallel_bar_wing_build,
    "mesh_grid_wing": _wing_form_mesh_grid_wing_build,
    "comb_clip_wing": _wing_form_comb_clip_wing_build,
    "single_rail_arm": _wing_form_single_rail_arm_build,
}


# --------------------------------------------------------------------------- #
# wing_motion candidates
# --------------------------------------------------------------------------- #
def _wing_motion_fold_hinge_build(
    model,
    r,
    spine,
    wing,
    *,
    joint: str,
    y_rail: float,
    z_rail: float,
    y_sign: float,
    fold_up: float,
    fold_down: float,
):
    """Origin record model.py:L209-L217 - a transverse REVOLUTE on the hinge rail."""
    axis = (y_sign, 0.0, 0.0)
    provider = AxisInterface(
        name=f"{joint}__provider",
        point=(0.0, y_rail * y_sign, z_rail),
        axis=axis,
        radial=(0.0, 0.0, -1.0),
        radius=r.tube_radius_m + _KNUCKLE_CLEAR,
    )
    consumer = AxisInterface(
        name=f"{joint}__consumer",
        point=(0.0, 0.0, 0.0),
        axis=axis,
        radial=(0.0, 0.0, -1.0),
        radius=r.tube_radius_m,
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=spine,
        child=wing,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=8.0, velocity=1.2, lower=fold_down, upper=fold_up),
        motion_properties=MotionProperties(damping=1.2, friction=0.6),
        meta={"mechanism": "drying wing hinge"},
    )
    register_interface_mate(model, joint, mate)
    return joint


def _wing_motion_telescope_slide_build(
    model,
    r,
    spine,
    wing,
    *,
    joint: str,
    y_rail: float,
    z_rail: float,
    y_sign: float,
    fold_up: float,
    fold_down: float,
):
    """var_prismatic_extension model.py:L210-L218 - a slide along the spine's length."""
    model.articulation(
        joint,
        ArticulationType.PRISMATIC,
        parent=spine,
        child=wing,
        origin=Origin(xyz=(0.0, y_rail * y_sign, z_rail)),
        axis=(y_sign, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=20.0, velocity=0.25, lower=0.0, upper=r.telescope_stroke_m
        ),
        motion_properties=MotionProperties(damping=2.0, friction=1.2),
        meta={"mechanism": "drying wing slide"},
    )
    return joint


_WING_MOTION_BUILDERS = {
    "fold_hinge": _wing_motion_fold_hinge_build,
    "telescope_slide": _wing_motion_telescope_slide_build,
}


# --------------------------------------------------------------------------- #
# hanger_type candidates
#
# The child frame origin is on the top rail with +X along it, so the hook wraps the
# rail at a running fit and the body hangs into -Z.  Reproduces the origin record's
# `_hanger_geometry` (model.py:L106-L134), which the pool defines and never builds.
# --------------------------------------------------------------------------- #
def _hanger_hook(r: ResolvedConfig, wire: float) -> MeshGeometry:
    ring = r.top_rail_radius_m + wire + _KNUCKLE_CLEAR
    points = []
    for index in range(9):
        angle = -0.58 * math.pi + (1.16 * math.pi) * index / 8.0
        points.append((0.0, ring * math.sin(angle), ring * math.cos(angle)))
    points.append((0.0, 0.0, -ring - wire * 2.0))
    return tube_from_spline_points(
        points, radius=wire, samples_per_segment=6, radial_segments=9, cap_ends=True
    )


def _hanger_type_wire_triangle_build(model, r, mats, *, name: str):
    """Origin record model.py:L106-L134 - shoulder slopes closed by a bottom rail."""
    part = model.part(name, meta={"role": "hanger", "hanger_type": "wire_triangle"})
    wire = max(r.tube_radius_m * 0.30, 0.0022)
    geom = _hanger_hook(r, wire)
    neck = -(r.top_rail_radius_m + wire + _KNUCKLE_CLEAR) - wire * 2.0
    half = r.hanger_width_m / 2.0
    bottom = neck - r.hanger_drop_m
    geom.merge(
        _merged(
            [
                ((0.0, 0.0, neck), (0.0, -half, bottom), wire),
                ((0.0, 0.0, neck), (0.0, half, bottom), wire),
                ((0.0, -half, bottom), (0.0, half, bottom), wire),
                (
                    (0.0, -half * 0.57, neck - r.hanger_drop_m * 0.55),
                    (0.0, half * 0.57, neck - r.hanger_drop_m * 0.55),
                    wire * 0.8,
                ),
            ],
            radial_segments=9,
        )
    )
    part.visual(
        mesh_from_geometry(geom, "hanger_body"), material=mats["hanger"], name="hanger_body", material_class_id="metal.steel_bare"
    )
    return part


def _hanger_type_clip_trouser_bar_build(model, r, mats, *, name: str):
    """Reference 001.png - a straight clamp bar on a narrow stem, no shoulders."""
    part = model.part(name, meta={"role": "hanger", "hanger_type": "clip_trouser_bar"})
    wire = max(r.tube_radius_m * 0.30, 0.0022)
    geom = _hanger_hook(r, wire)
    neck = -(r.top_rail_radius_m + wire + _KNUCKLE_CLEAR) - wire * 2.0
    half = r.hanger_width_m / 2.0
    bar_z = neck - r.hanger_drop_m
    geom.merge(
        _merged(
            [
                ((0.0, 0.0, neck), (0.0, 0.0, bar_z), wire * 1.15),
                ((0.0, -half, bar_z), (0.0, half, bar_z), wire * 1.15),
                (
                    (0.0, -half * 0.62, bar_z),
                    (0.0, -half * 0.62, neck * 0.35 + bar_z * 0.65),
                    wire * 0.7,
                ),
                (
                    (0.0, half * 0.62, bar_z),
                    (0.0, half * 0.62, neck * 0.35 + bar_z * 0.65),
                    wire * 0.7,
                ),
            ],
            radial_segments=9,
        )
    )
    part.visual(
        mesh_from_geometry(geom, "hanger_body"), material=mats["hanger"], name="hanger_body", material_class_id="metal.steel_bare"
    )
    clip = max(r.hanger_width_m * 0.07, wire * 3.0)
    for index, sign in enumerate((-1.0, 1.0)):
        part.visual(
            Box((clip * 0.7, clip * 0.9, clip * 2.0)),
            origin=Origin(xyz=(0.0, half * 0.78 * sign, bar_z - clip * 0.55)),
            material=mats["black"],
            name=f"trouser_clip_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    return part


def _hanger_type_sock_clip_ring_build(model, r, mats, *, name: str):
    """Reference 002.png - a hub with radial clip arms fanning in the rail's normal plane."""
    part = model.part(name, meta={"role": "hanger", "hanger_type": "sock_clip_ring"})
    wire = max(r.tube_radius_m * 0.28, 0.0020)
    geom = _hanger_hook(r, wire)
    neck = -(r.top_rail_radius_m + wire + _KNUCKLE_CLEAR) - wire * 2.0
    arm_len = min(r.hanger_width_m / 2.0, r.hanger_drop_m * 0.92)
    hub_z = neck - r.hanger_drop_m + arm_len
    hub_r = max(arm_len * 0.16, wire * 2.4)
    geom.merge(
        _merged([((0.0, 0.0, neck), (0.0, 0.0, hub_z + hub_r), wire * 1.15)], radial_segments=9)
    )
    ring_points = []
    for index in range(13):
        angle = 2.0 * math.pi * index / 12.0
        ring_points.append((0.0, hub_r * math.cos(angle), hub_z + hub_r * math.sin(angle)))
    geom.merge(
        _merged(
            [(ring_points[i], ring_points[i + 1], wire * 0.9) for i in range(12)], radial_segments=8
        )
    )
    arm_count = 6
    arm_ends = []
    for index in range(arm_count):
        angle = math.pi * (0.14 + 0.72 * index / (arm_count - 1)) + math.pi / 2.0
        end = (0.0, arm_len * math.cos(angle), hub_z + arm_len * math.sin(angle))
        geom.merge(
            _merged(
                [
                    (
                        (0.0, hub_r * math.cos(angle), hub_z + hub_r * math.sin(angle)),
                        end,
                        wire * 0.85,
                    )
                ],
                radial_segments=8,
            )
        )
        arm_ends.append(end)
    part.visual(
        mesh_from_geometry(geom, "hanger_body"), material=mats["hanger"], name="hanger_body", material_class_id="metal.steel_bare"
    )
    clip = max(arm_len * 0.13, wire * 2.6)
    for index, end in enumerate(arm_ends):
        part.visual(
            Box((clip * 0.7, clip * 0.9, clip * 1.6)),
            origin=Origin(xyz=(end[0], end[1], end[2] - clip * 0.4)),
            material=mats["black"],
            name=f"sock_clip_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    return part


_HANGER_BUILDERS = {
    "wire_triangle": _hanger_type_wire_triangle_build,
    "clip_trouser_bar": _hanger_type_clip_trouser_bar_build,
    "sock_clip_ring": _hanger_type_sock_clip_ring_build,
}


# --------------------------------------------------------------------------- #
# spine_extra candidates (built into the spine part)
# --------------------------------------------------------------------------- #
def _spine_extra_scissor_brace_build(model, r, mats, spine):
    """Origin record model.py:L281-L295 - crossing diagonals stiffening the spine.

    The source runs each diagonal's upper end onto the centreline at the top rail.
    That station is where the hangers hang, and hanger_type is an independent slot,
    so the upper rivet is carried out to a fraction of the lower bar's offset - the
    local host adaptation the full-combination rule requires.
    """
    t = r.tube_radius_m
    end = r.end_station_m
    # Both ends land on the lower bars, which is the one pair of spine rails nothing
    # rides: the wing hinge rails carry the wings and the top rail carries the hangers,
    # and spine_extra has to combine with every candidate of both slots.  The two
    # diagonals still cross, so the brace reads as the source's scissor stiffener.
    span = end * (0.40 + 0.40 * (r.accessory_span_ratio - 0.180) / (0.550 - 0.180))
    segments = []
    for sign in (1.0, -1.0):
        segments.append(
            (
                (-span, r.y_lower_bar_m * sign, r.z_lower_bar_m),
                (span, -r.y_lower_bar_m * sign, r.z_lower_bar_m),
                t * 0.50,
            )
        )
    spine.visual(
        mesh_from_geometry(_merged(segments, radial_segments=10), "spine_scissor_brace"),
        material=mats["fitting"],
        name="spine_scissor_brace", material_class_id="metal.blackened_gunmetal",
    )
    rivet = t * 1.5
    for index, (x, y, z) in enumerate(
        (
            (-span, r.y_lower_bar_m, r.z_lower_bar_m),
            (span, r.y_lower_bar_m, r.z_lower_bar_m),
            (-span, -r.y_lower_bar_m, r.z_lower_bar_m),
            (span, -r.y_lower_bar_m, r.z_lower_bar_m),
        )
    ):
        spine.visual(
            Box((rivet * 2.0, rivet, rivet)),
            origin=Origin(xyz=(x, y, z)),
            material=mats["fitting"],
            name=f"brace_rivet_{index}", material_class_id="metal.blackened_gunmetal",
        )


def _spine_extra_shoe_cradle_rung_build(model, r, mats, spine):
    """Reference 002.png - an angled shoe pocket hung under the lower rail."""
    t = r.tube_radius_m
    end = r.end_station_m
    drop = r.cradle_drop_m
    segments = []
    for sign in (1.0, -1.0):
        y_root = r.cradle_root_y_m * sign
        y_tip = r.cradle_tip_y_m * sign
        segments.append(
            (
                (-end * 0.62, y_root, r.z_lower_rail_m),
                (-end * 0.62, y_tip, r.z_lower_rail_m - drop),
                t * 0.62,
            )
        )
        segments.append(
            (
                (end * 0.62, y_root, r.z_lower_rail_m),
                (end * 0.62, y_tip, r.z_lower_rail_m - drop),
                t * 0.62,
            )
        )
        segments.append(
            (
                (-end * 0.62, y_tip, r.z_lower_rail_m - drop),
                (end * 0.62, y_tip, r.z_lower_rail_m - drop),
                t * 0.70,
            )
        )
        # Upturned lip that makes it a pocket rather than a shelf edge.
        segments.append(
            (
                (-end * 0.62, y_tip, r.z_lower_rail_m - drop),
                (-end * 0.62, y_tip, r.z_lower_rail_m - drop * 0.55),
                t * 0.50,
            )
        )
        segments.append(
            (
                (end * 0.62, y_tip, r.z_lower_rail_m - drop),
                (end * 0.62, y_tip, r.z_lower_rail_m - drop * 0.55),
                t * 0.50,
            )
        )
    spine.visual(
        mesh_from_geometry(_merged(segments, radial_segments=11), "spine_shoe_cradle"),
        material=mats["tube"],
        name="spine_shoe_cradle", material_class_id="metal.paint_coated",
    )


def _spine_extra_towel_hoop_rail_build(model, r, mats, spine):
    """Reference 001.png - a hoop projecting past the frame end for a draped towel."""
    t = r.tube_radius_m
    end = r.end_station_m
    out = r.accessory_span_m * 0.34
    segments = []
    for sign in (1.0, -1.0):
        x0 = end * sign
        x1 = (end + out) * sign
        for y_sign in (1.0, -1.0):
            y = r.y_wing_rail_m * 0.62 * y_sign
            segments.append(((x0, y, r.z_lower_bar_m), (x1, y, r.z_lower_bar_m), t * 0.72))
        segments.append(
            (
                (x1, -r.y_wing_rail_m * 0.62, r.z_lower_bar_m),
                (x1, r.y_wing_rail_m * 0.62, r.z_lower_bar_m),
                t * 0.72,
            )
        )
    spine.visual(
        mesh_from_geometry(_merged(segments, radial_segments=11), "spine_towel_hoop"),
        material=mats["tube"],
        name="spine_towel_hoop", material_class_id="metal.paint_coated",
    )
    cap = t * 2.0
    for index, sign in enumerate((1.0, -1.0)):
        spine.visual(
            Box((cap, cap, cap)),
            origin=Origin(xyz=((end + out) * sign, 0.0, r.z_lower_bar_m)),
            material=mats["black"],
            name=f"towel_hoop_cap_{index}", material_class_id="plastic.opaque_glossy_molded",
        )


_SPINE_EXTRA_BUILDERS = {
    "scissor_brace": _spine_extra_scissor_brace_build,
    "shoe_cradle_rung": _spine_extra_shoe_cradle_rung_build,
    "towel_hoop_rail": _spine_extra_towel_hoop_rail_build,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_household_laundry_clothes_drying_rack_laundry_drying_rack(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    resolved_config = config or config_from_seed(0)
    r = resolve_config(resolved_config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "Household_Laundry_Clothes_drying_rack_Laundry_drying_rack",
            "identified_object": "freestanding folding laundry drying rack",
            "slot_choices": slot_choices_for_config(r),
            "source_layout": "one rigid spine over folding legs, with drying wings on its side rails",
        },
    )
    tint = abs(hash((r.leg_family, r.wing_form, r.spine_extra))) % 4
    mats = _materials(model, tint)
    spine = _build_spine(model, r, mats)
    _SPINE_EXTRA_BUILDERS[r.spine_extra](model, r, mats, spine)

    leg_builder = _LEG_BUILDERS[r.leg_family]
    ground_builder = _GROUND_BUILDERS[r.ground_contact]
    for index, (station, hinge_z) in enumerate(r.leg_stations_m):
        y_sign = 1.0 if station > 1.0e-6 else -1.0
        name = f"leg_family__{r.leg_family}__frame_{index}"
        drop = hinge_z - r.contact_headroom_m
        part, tips = leg_builder(model, r, mats, name=name, y_sign=y_sign, drop=drop)
        joint = f"spine_to_leg_{index}"
        provider = AxisInterface(
            name=f"{joint}__provider",
            point=(0.0, station, hinge_z),
            axis=(y_sign, 0.0, 0.0),
            radial=(0.0, 0.0, -1.0),
            radius=r.tube_radius_m * 0.92 + _KNUCKLE_CLEAR,
        )
        consumer = AxisInterface(
            name=f"{joint}__consumer",
            point=(0.0, 0.0, 0.0),
            axis=(y_sign, 0.0, 0.0),
            radial=(0.0, 0.0, -1.0),
            radius=r.tube_radius_m * 0.92,
        )
        mate = mate_axes(provider, consumer)
        model.articulation(
            joint,
            ArticulationType.REVOLUTE,
            parent=spine,
            child=part,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(effort=12.0, velocity=1.5, lower=0.0, upper=r.leg_fold_rad),
            motion_properties=MotionProperties(damping=1.6, friction=0.9),
            meta={"mechanism": "leg fold hinge"},
        )
        register_interface_mate(model, joint, mate)
        ground_builder(model, r, mats, part, tips, prefix=name)

    wing_builder = _WING_BUILDERS[r.wing_form]
    motion_builder = _WING_MOTION_BUILDERS[r.wing_motion]
    for tier, (y_rail, z_rail, tier_reach, tier_rise, fold_up, fold_down) in enumerate(
        r.tier_specs
    ):
        for side, y_sign in (("front", 1.0), ("rear", -1.0)):
            name = f"wing_form__{r.wing_form}__tier{tier}_{side}"
            wing = wing_builder(
                model, r, mats, name=name, reach=tier_reach, rise=tier_rise, y_sign=y_sign
            )
            motion_builder(
                model,
                r,
                spine,
                wing,
                joint=f"spine_to_wing_t{tier}_{side}",
                y_rail=y_rail,
                z_rail=z_rail,
                y_sign=y_sign,
                fold_up=fold_up,
                fold_down=fold_down,
            )

    hanger_builder = _HANGER_BUILDERS[r.hanger_type]
    for index, station in enumerate(r.hanger_stations_m):
        name = f"hanger_type__{r.hanger_type}__hanger_{index}"
        hanger = hanger_builder(model, r, mats, name=name)
        joint = f"rail_to_hanger_{index}"
        provider = AxisInterface(
            name=f"{joint}__provider",
            point=(station, 0.0, r.z_top_m),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, -1.0),
            radius=r.top_rail_radius_m + _KNUCKLE_CLEAR,
        )
        consumer = AxisInterface(
            name=f"{joint}__consumer",
            point=(0.0, 0.0, 0.0),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, -1.0),
            radius=r.top_rail_radius_m,
        )
        mate = mate_axes(provider, consumer)
        model.articulation(
            joint,
            ArticulationType.REVOLUTE,
            parent=spine,
            child=hanger,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(
                effort=1.0, velocity=2.0, lower=-r.hanger_sway_rad, upper=r.hanger_sway_rad
            ),
            motion_properties=MotionProperties(damping=0.3, friction=0.15),
            meta={"mechanism": "hanger sway"},
        )
        register_interface_mate(model, joint, mate)

    return model


# --------------------------------------------------------------------------- #
# Author tests / category anchors
# --------------------------------------------------------------------------- #
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def run_household_laundry_clothes_drying_rack_laundry_drying_rack_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    spines = _parts_by_role(model, "spine")
    legs = _parts_by_role(model, "leg_frame")
    wings = _parts_by_role(model, "drying_wing")
    hangers = _parts_by_role(model, "hanger")
    wheels = _parts_by_role(model, "caster_wheel")

    ctx.check(
        "category_anchor: one rigid spine carries every folding support",
        len(spines) == 1 and len(legs) == r.leg_frame_count,
        details=f"spines={[p.name for p in spines]}, legs={[p.name for p in legs]}",
    )

    leg_joints = [j for j in model.articulations if j.meta.get("mechanism") == "leg fold hinge"]
    ctx.check(
        "category_anchor: every leg frame folds on its own transverse hinge",
        len(leg_joints) == r.leg_frame_count
        and all(j.articulation_type == ArticulationType.REVOLUTE for j in leg_joints)
        and all(abs(abs(j.axis[0]) - 1.0) < 1.0e-6 for j in leg_joints)
        and len({j.child for j in leg_joints}) == r.leg_frame_count,
        details=f"joints={[(j.name, j.child, j.axis) for j in leg_joints]}",
    )

    floor_reach = []
    for part in legs:
        box = ctx.part_world_aabb(part)
        if box is not None:
            floor_reach.append(box[0][2])
    ctx.check(
        "category_anchor: the legs reach the floor under the spine",
        len(floor_reach) == r.leg_frame_count
        and max(floor_reach) < r.z_lower_rail_m * 0.45
        and min(floor_reach) > -0.012,
        details=f"leg minimum z per frame={floor_reach}, lower rail={r.z_lower_rail_m:.4f}",
    )

    expected_wings = 2 * r.wing_tier_count
    wing_joints = [
        j
        for j in model.articulations
        if j.meta.get("mechanism") in {"drying wing hinge", "drying wing slide"}
    ]
    ctx.check(
        "category_anchor: every drying wing hangs on a spine rail",
        len(wings) == expected_wings
        and len(wing_joints) == expected_wings
        and all(j.parent == "main_frame" for j in wing_joints)
        and len({j.child for j in wing_joints}) == expected_wings,
        details=f"wings={[p.name for p in wings]}, joints={[j.name for j in wing_joints]}",
    )

    expected_type = (
        ArticulationType.REVOLUTE if r.wing_motion == "fold_hinge" else ArticulationType.PRISMATIC
    )
    # Travel is measured across the joint's whole range, not from rest: a lower tier's
    # useful swing is downward (it hangs under the upper wing), and an upper tier's is up.
    opened = []
    thresholds = []
    for index, joint in enumerate(wing_joints):
        child = model.get_part(joint.child)
        with ctx.pose({joint: joint.motion_limits.lower}):
            low = ctx.part_world_aabb(child)
        with ctx.pose({joint: joint.motion_limits.upper}):
            high = ctx.part_world_aabb(child)
        if low is not None and high is not None:
            opened.append(max(abs(high[0][axis] - low[0][axis]) for axis in range(3)))
        tier_reach = r.tier_specs[index // 2][2]
        thresholds.append(max(0.010, tier_reach * 0.10))
    ctx.check(
        "category_anchor: the wings open to a wider span than the folded rack",
        all(j.articulation_type == expected_type for j in wing_joints)
        and len(opened) == expected_wings
        and all(travel > limit for travel, limit in zip(opened, thresholds)),
        details=f"motion={r.wing_motion}, travel per wing={opened}, required={thresholds}",
    )

    hanger_joints = [j for j in model.articulations if j.meta.get("mechanism") == "hanger sway"]
    ctx.check(
        "category_anchor: every hanger hangs on the spine top rail and can sway",
        len(hangers) == r.hanger_count
        and len(hanger_joints) == r.hanger_count
        and all(j.articulation_type == ArticulationType.REVOLUTE for j in hanger_joints)
        and all(abs(abs(j.axis[0]) - 1.0) < 1.0e-6 for j in hanger_joints)
        and all(abs(j.origin.xyz[2] - r.z_top_m) < 1.0e-6 for j in hanger_joints)
        and len({j.child for j in hanger_joints}) == r.hanger_count,
        details=f"hangers={[p.name for p in hangers]}, joints={[j.name for j in hanger_joints]}",
    )

    swept = r.hanger_width_m * math.sin(r.hanger_sway_rad) + r.hanger_drop_m * (
        1.0 - math.cos(r.hanger_sway_rad)
    )
    ctx.check(
        "category_anchor: neighbouring hangers stay clear at full sway",
        r.hanger_pitch_m > max(r.tube_radius_m * 4.0, 0.030) and swept < r.hanger_pitch_m * 4.0,
        details=f"pitch={r.hanger_pitch_m:.4f}, hanger sway envelope={swept:.4f}",
    )

    # The floor interface is whatever the selected candidate puts under the leg tips:
    # the pads and skid bars belong to the leg part, the casters are their own parts.
    # Every candidate has to land the rack on z = 0 and nothing may sink below it.
    contact_parts = list(legs) + list(wheels) if wheels else list(legs)
    contact_z = [
        box[0][2]
        for box in (ctx.part_world_aabb(part) for part in contact_parts)
        if box is not None
    ]
    per_frame_low = [
        box[0][2] for box in (ctx.part_world_aabb(part) for part in legs) if box is not None
    ]
    expected_wheels = 2 * r.leg_frame_count if r.ground_contact == "swivel_caster_wheels" else 0
    ctx.check(
        "category_anchor: every leg tip meets the floor at the same height",
        len(wheels) == expected_wheels
        and len(contact_z) == len(contact_parts)
        and len(per_frame_low) == r.leg_frame_count
        and -0.010 <= min(contact_z) <= 0.008
        and max(per_frame_low) <= r.contact_size_m + 0.012,
        details=(
            f"contact={r.ground_contact}, wheels={len(wheels)}, lowest={min(contact_z, default=None)}, "
            f"per-frame low={per_frame_low}, contact size={r.contact_size_m:.4f}"
        ),
    )

    if r.ground_contact == "swivel_caster_wheels":
        wheel_joints = [j for j in model.articulations if j.meta.get("mechanism") == "caster roll"]
        ctx.check(
            "every caster rolls about its own hub on a continuous joint",
            len(wheel_joints) == expected_wheels
            and all(j.articulation_type == ArticulationType.CONTINUOUS for j in wheel_joints)
            and all(abs(abs(j.axis[0]) - 1.0) < 1.0e-6 for j in wheel_joints),
            details=f"joints={[(j.name, j.axis) for j in wheel_joints]}",
        )

    ctx.check(
        "the rack keeps a source-like long-and-shallow planform",
        3.40 <= r.spine_length_m / r.spine_depth_m <= 6.60,
        details=f"length={r.spine_length_m:.4f}, depth={r.spine_depth_m:.4f}",
    )
    ctx.check(
        "the drying wings reach outboard of the spine's own depth",
        r.wing_reach_m > r.spine_depth_m * 0.55,
        details=f"reach={r.wing_reach_m:.4f}, depth={r.spine_depth_m:.4f}",
    )
    if r.wing_motion == "fold_hinge":
        for y_rail, z_rail, tier_reach, tier_rise, fold_up, _fold_down in r.tier_specs:
            out = _wing_outward(tier_reach, tier_rise, fold_up)
            ctx.check(
                f"raised wings at tier z={z_rail:.3f} stay clear of the spine centreline",
                y_rail + out >= _CENTRE_CLEAR - 1.0e-6,
                details=f"tip offset at upper limit={y_rail + out:.4f}, required={_CENTRE_CLEAR}",
            )
    else:
        ctx.check(
            "the telescoping wings stay engaged with their rail at full extension",
            r.telescope_stroke_m < r.end_station_m * 1.10,
            details=f"stroke={r.telescope_stroke_m:.4f}, rail half length={r.end_station_m:.4f}",
        )

    for hanger in hangers:
        ctx.allow_isolated_part(
            hanger,
            reason=(
                "The hanger is carried by its rail pivot on an authored running clearance, "
                "which is how a hanger sits on a rail."
            ),
        )
    for wheel in wheels:
        ctx.allow_isolated_part(
            wheel,
            reason="The caster is carried by its stub axle inside the wheel bore on a running fit.",
        )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "longest_tallest_rack_three_legs_two_tiers",
        {
            "leg_family": "scissor_x_legs",
            "wing_form": "parallel_bar_wing",
            "wing_motion": "fold_hinge",
            "ground_contact": "swivel_caster_wheels",
            "hanger_type": "wire_triangle",
            "spine_extra": "scissor_brace",
            "bar_count": 10,
            "wing_tier_count": 2,
            "leg_frame_count": 3,
            "hanger_count": 6,
            "spine_length_m": 2.100,
            "spine_height_m": 1.280,
            "spine_depth_m": 0.460,
            "tube_radius_m": 0.0160,
            "leg_spread_ratio": 0.620,
            "wing_reach_m": 0.580,
            "wing_rise_ratio": 0.620,
            "fold_upper_ratio": 1.000,
            "contact_size_m": 0.0380,
            "hanger_drop_ratio": 0.900,
            "hanger_width_ratio": 0.950,
            "accessory_span_ratio": 0.550,
        },
        reason="every dimension, count and ratio at its declared maximum on rolling casters",
    ),
    corner_case(
        "smallest_rack_minimum_counts",
        {
            "leg_family": "post_base_legs",
            "wing_form": "single_rail_arm",
            "wing_motion": "fold_hinge",
            "ground_contact": "rubber_foot_pads",
            "hanger_type": "clip_trouser_bar",
            "spine_extra": "towel_hoop_rail",
            "bar_count": 4,
            "wing_tier_count": 1,
            "leg_frame_count": 2,
            "hanger_count": 2,
            "spine_length_m": 1.200,
            "spine_height_m": 0.860,
            "spine_depth_m": 0.260,
            "tube_radius_m": 0.0080,
            "leg_spread_ratio": 0.240,
            "wing_reach_m": 0.260,
            "wing_rise_ratio": 0.200,
            "fold_upper_ratio": 0.550,
            "contact_size_m": 0.0140,
            "hanger_drop_ratio": 0.400,
            "hanger_width_ratio": 0.450,
            "accessory_span_ratio": 0.180,
        },
        reason="every dimension, count and ratio at its declared minimum",
    ),
    corner_case(
        "widest_wings_on_the_shallowest_spine",
        {
            "leg_family": "a_frame_legs",
            "wing_form": "mesh_grid_wing",
            "wing_motion": "fold_hinge",
            "ground_contact": "skid_bar_feet",
            "hanger_type": "sock_clip_ring",
            "spine_extra": "shoe_cradle_rung",
            "bar_count": 10,
            "wing_tier_count": 2,
            "leg_frame_count": 3,
            "hanger_count": 6,
            "spine_length_m": 1.200,
            "spine_height_m": 0.860,
            "spine_depth_m": 0.260,
            "tube_radius_m": 0.0160,
            "wing_reach_m": 0.580,
            "wing_rise_ratio": 0.620,
            "fold_upper_ratio": 1.000,
            "hanger_drop_ratio": 0.900,
            "hanger_width_ratio": 0.950,
        },
        reason="the deepest wing pair folding up over the narrowest spine, where the "
        "centreline stop and the tier-to-tier stop both bind",
    ),
    corner_case(
        "full_telescope_stroke_on_the_longest_spine",
        {
            "leg_family": "scissor_x_legs",
            "wing_form": "comb_clip_wing",
            "wing_motion": "telescope_slide",
            "ground_contact": "swivel_caster_wheels",
            "hanger_type": "sock_clip_ring",
            "spine_extra": "scissor_brace",
            "bar_count": 10,
            "wing_tier_count": 2,
            "leg_frame_count": 3,
            "hanger_count": 6,
            "spine_length_m": 2.100,
            "spine_depth_m": 0.460,
            "telescope_stroke_ratio": 0.350,
            "contact_size_m": 0.0380,
        },
        reason="the longest slide stroke, where rail engagement at full extension binds",
    ),
    corner_case(
        "shortest_telescope_stroke",
        {
            "wing_motion": "telescope_slide",
            "wing_form": "mesh_grid_wing",
            "ground_contact": "skid_bar_feet",
            "hanger_type": "clip_trouser_bar",
            "spine_extra": "shoe_cradle_rung",
            "leg_family": "post_base_legs",
            "bar_count": 4,
            "wing_tier_count": 2,
            "leg_frame_count": 2,
            "hanger_count": 2,
            "spine_length_m": 1.200,
            "spine_depth_m": 0.280,
            "telescope_stroke_ratio": 0.100,
            "contact_size_m": 0.0140,
        },
        reason="the shortest declared slide stroke still has to move every wing",
    ),
    corner_case(
        "tallest_narrowest_with_maximum_legs_and_pads",
        {
            "leg_family": "a_frame_legs",
            "wing_form": "comb_clip_wing",
            "wing_motion": "fold_hinge",
            "ground_contact": "rubber_foot_pads",
            "hanger_type": "wire_triangle",
            "spine_extra": "towel_hoop_rail",
            "bar_count": 4,
            "wing_tier_count": 1,
            "leg_frame_count": 3,
            "hanger_count": 6,
            "spine_height_m": 1.280,
            "spine_length_m": 1.200,
            "spine_depth_m": 0.260,
            "tube_radius_m": 0.0080,
            "leg_spread_ratio": 0.240,
            "wing_reach_m": 0.260,
            "wing_rise_ratio": 0.200,
            "accessory_span_ratio": 0.550,
            "hanger_drop_ratio": 0.400,
            "hanger_width_ratio": 0.450,
        },
        reason="the tallest, narrowest rack on the least leg spread, where the mid-span "
        "leg station and the hanger headroom are both tightest",
    ),
    corner_case(
        "post_legs_on_skid_bars_with_widest_spread",
        {
            "leg_family": "post_base_legs",
            "wing_form": "parallel_bar_wing",
            "wing_motion": "fold_hinge",
            "ground_contact": "skid_bar_feet",
            "hanger_type": "sock_clip_ring",
            "spine_extra": "scissor_brace",
            "bar_count": 7,
            "wing_tier_count": 2,
            "leg_frame_count": 2,
            "hanger_count": 4,
            "leg_spread_ratio": 0.620,
            "contact_size_m": 0.0380,
            "spine_depth_m": 0.460,
            "spine_length_m": 2.100,
            "accessory_span_ratio": 0.180,
            "telescope_stroke_ratio": 0.350,
            "fold_upper_ratio": 0.550,
        },
        reason="vertical posts pushed to the widest foot offset and the deepest skid bar",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_household_laundry_clothes_drying_rack_laundry_drying_rack",
    "config_from_seed",
    "resolve_config",
    "run_household_laundry_clothes_drying_rack_laundry_drying_rack_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
