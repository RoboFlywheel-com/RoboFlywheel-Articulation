# SPDX-License-Identifier: Apache-2.0

"""Desk-clamp mounted adjustable forearm supports (pictureX/0611).

The category host is always the same screw clamp: a folded C-frame, a jaw guided
on two rails, a threaded spindle and a self-aligning pressure shoe.  Two slots
vary: the adjustable structure carried on the clamp head (`support_linkage`) and
the rest head at its far end (`pad_head`).

Source evidence lives in
`articraft_template_authoring/source_maps/pictureX_0611_ergonomic_clamp_with_adjustable.md`.
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
    register_interface_mate,
)

SupportLinkage = Literal[
    "plain_arm",
    "ratchet_elbow",
    "gas_spring_arm",
    "linear_rail",
    "parallel_linkage",
    "rotary_column",
]
PadHead = Literal[
    "tilt_saddle",
    "ball_socket",
    "split_pad",
    "deep_cradle",
    "quick_release",
]
BaseReach = Literal["fixed_mount", "edge_track"]
ClampActuation = Literal["screw_spindle", "overcenter_cam"]

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "support_linkage",
            (
                "plain_arm",
                "ratchet_elbow",
                "gas_spring_arm",
                "linear_rail",
                "parallel_linkage",
                "rotary_column",
            ),
            role="source-backed adjustable structure between clamp and rest",
        ),
        component_slot(
            "pad_head",
            ("tilt_saddle", "ball_socket", "split_pad", "deep_cradle", "quick_release"),
            role="source-backed forearm rest head",
        ),
        component_slot(
            "base_reach",
            ("fixed_mount", "edge_track"),
            role="source-backed reach interface between the clamp frame and the support base",
        ),
        component_slot(
            "clamp_actuation",
            ("screw_spindle", "overcenter_cam"),
            role="source-backed desk-clamp actuation driving the guided jaw",
        ),
    )
)

# Reference rest pitch of the rising arm family, taken from the source records.
_REST_PITCH = 0.62
# Column-family candidates stand the first link vertically instead.
_COLUMN_CANDIDATES = frozenset({"rotary_column"})


@dataclass(frozen=True)
class Config:
    support_linkage: SupportLinkage = "plain_arm"
    pad_head: PadHead = "tilt_saddle"
    base_reach: BaseReach = "fixed_mount"
    clamp_actuation: ClampActuation = "screw_spindle"
    clamp_span_m: float = 0.092
    frame_depth_m: float = 0.050
    throat_gap_m: float = 0.047
    arm_reach_m: float = 0.204
    pad_length_m: float = 0.190
    pad_radius_m: float = 0.072
    name: str = "ergonomic_clamp_with_adjustable"


@dataclass(frozen=True)
class ResolvedConfig:
    support_linkage: SupportLinkage
    pad_head: PadHead
    base_reach: BaseReach
    clamp_actuation: ClampActuation
    clamp_span_m: float
    frame_depth_m: float
    throat_gap_m: float
    arm_reach_m: float
    pad_length_m: float
    pad_radius_m: float
    name: str
    # derived clamp geometry
    jaw_z_m: float
    plate_bottom_m: float
    frame_top_m: float
    elbow_z_m: float
    elbow_x_m: float
    screw_x_m: float
    rail_z0_m: float
    rail_z1_m: float
    travel_up_m: float
    travel_dn_m: float
    block_hy_m: float
    window_hy_m: float
    rail_y_m: float
    clevis_y_m: float
    barrel_len_m: float
    arm_hy_m: float
    # derived head geometry
    post_height_m: float
    pad_width_m: float
    # derived reach-interface geometry
    track_rail_x_m: float
    track_rail_z_m: float
    track_stroke_m: float
    host_x_off_m: float
    host_z_off_m: float


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x0611_C1A3_9F17)
    return Config(
        support_linkage=choices["support_linkage"],
        pad_head=choices["pad_head"],
        base_reach=choices["base_reach"],
        clamp_actuation=choices["clamp_actuation"],
        clamp_span_m=round(rng.uniform(0.076, 0.102), 5),
        frame_depth_m=round(rng.uniform(0.043, 0.059), 5),
        throat_gap_m=round(rng.uniform(0.039, 0.057), 5),
        arm_reach_m=round(rng.uniform(0.158, 0.242), 5),
        pad_length_m=round(rng.uniform(0.164, 0.210), 5),
        pad_radius_m=round(rng.uniform(0.059, 0.081), 5),
        name=f"ergonomic_clamp_with_adjustable_seed_{seed}",
    )


def _require_range(name: str, value: float, minimum: float, maximum: float) -> float:
    value = float(value)
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be in [{minimum}, {maximum}], got {value}")
    return value


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "support_linkage": config.support_linkage,
            "pad_head": config.pad_head,
            "base_reach": config.base_reach,
            "clamp_actuation": config.clamp_actuation,
        }
    )
    span = _require_range("clamp_span_m", config.clamp_span_m, 0.072, 0.104)
    depth = _require_range("frame_depth_m", config.frame_depth_m, 0.042, 0.060)
    throat = _require_range("throat_gap_m", config.throat_gap_m, 0.038, 0.058)
    reach = _require_range("arm_reach_m", config.arm_reach_m, 0.155, 0.245)
    pad_len = _require_range("pad_length_m", config.pad_length_m, 0.162, 0.212)
    pad_r = _require_range("pad_radius_m", config.pad_radius_m, 0.058, 0.082)

    jaw_z = 0.075
    plate_bottom = jaw_z + 0.035 + throat
    block_hy = 0.36 * depth - 0.0055
    # Host adaptation for the reach interface: the edge track carries the whole
    # support base on a lateral carriage, so the elbow moves out in front of the
    # guided jaw and every support/pad body follows it.
    track_rail_x = 0.030
    track_stroke = round(0.30 * span + 0.008, 5)
    on_track = config.base_reach == "edge_track"
    elbow_x = 0.045 + (0.030 if on_track else 0.0)
    elbow_z = plate_bottom - 0.033
    track_rail_z = elbow_z + 0.050
    return ResolvedConfig(
        support_linkage=config.support_linkage,
        pad_head=config.pad_head,
        base_reach=config.base_reach,
        clamp_actuation=config.clamp_actuation,
        clamp_span_m=span,
        frame_depth_m=depth,
        throat_gap_m=throat,
        arm_reach_m=reach,
        pad_length_m=pad_len,
        pad_radius_m=pad_r,
        name=config.name,
        jaw_z_m=jaw_z,
        plate_bottom_m=plate_bottom,
        frame_top_m=plate_bottom + 0.022,
        elbow_z_m=elbow_z,
        elbow_x_m=elbow_x,
        screw_x_m=-0.49 * span,
        rail_z0_m=0.039,
        rail_z1_m=plate_bottom - 0.035,
        travel_up_m=throat - 0.008,
        travel_dn_m=-0.012,
        block_hy_m=block_hy,
        window_hy_m=block_hy + 0.004,
        rail_y_m=0.36 * depth,
        clevis_y_m=0.36 * depth + 0.009,
        barrel_len_m=2.0 * (0.36 * depth + 0.002) - 0.0008,
        arm_hy_m=0.36 * depth - 0.0005,
        post_height_m=0.030 + 0.24 * pad_len,
        pad_width_m=1.62 * pad_r,
        track_rail_x_m=track_rail_x,
        track_rail_z_m=track_rail_z,
        track_stroke_m=track_stroke,
        host_x_off_m=-track_rail_x if on_track else 0.0,
        host_z_off_m=-track_rail_z if on_track else 0.0,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, str]:
    return {
        "support_linkage": config.support_linkage,
        "pad_head": config.pad_head,
        "base_reach": config.base_reach,
        "clamp_actuation": config.clamp_actuation,
    }


def slot_choices_for_seed(seed: int) -> dict[str, str]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject) -> dict[str, object]:
    return {
        "powder": model.material("clamp_powder_black", rgba=(0.055, 0.060, 0.065, 1.0)),
        "steel": model.material("clamp_satin_steel", rgba=(0.54, 0.56, 0.58, 1.0)),
        "dark": model.material("clamp_dark_steel", rgba=(0.18, 0.19, 0.20, 1.0)),
        "polymer": model.material("clamp_charcoal_polymer", rgba=(0.075, 0.080, 0.085, 1.0)),
        "rubber": model.material("clamp_soft_rubber", rgba=(0.025, 0.027, 0.029, 1.0)),
        "liner": model.material("clamp_pad_liner", rgba=(0.11, 0.115, 0.12, 1.0)),
    }


# ---------------------------------------------------------------------------
# shared CadQuery profiles
# ---------------------------------------------------------------------------


def _side_extrusion(profile: list[tuple[float, float]], depth: float) -> cq.Workplane:
    """Extrude an X/Z side profile symmetrically through Y."""

    return cq.Workplane("XZ").polyline(profile).close().extrude(depth * 0.5, both=True)


def _clamp_frame_shape(r: ResolvedConfig) -> cq.Workplane:
    """One continuous folded C-frame with a real guide window through its web."""

    span = r.clamp_span_m
    profile = [
        (-span, r.frame_top_m),
        (0.002, r.frame_top_m),
        (0.002, 0.044),
        (0.004, 0.044),
        (0.004, 0.022),
        (-0.020, 0.022),
        (-0.020, 0.044),
        (-0.018, 0.044),
        (-0.018, r.plate_bottom_m),
        (-span, r.plate_bottom_m),
    ]
    frame = _side_extrusion(profile, r.frame_depth_m)
    window_z0 = r.jaw_z_m + r.travel_dn_m - 0.014
    window_z1 = r.jaw_z_m + r.travel_up_m + 0.014
    window = (
        cq.Workplane("XY")
        .box(0.034, 2.0 * r.window_hy_m, window_z1 - window_z0)
        .translate((-0.006, 0.0, 0.5 * (window_z0 + window_z1)))
    )
    return frame.cut(window)


def _jaw_carrier_shape(r: ResolvedConfig) -> cq.Workplane:
    """Jaw arm with a real vertical spindle bore instead of a solid block."""

    length = 0.034 - r.screw_x_m
    centre_x = 0.5 * (r.screw_x_m - 0.012 + 0.022)
    carrier = (
        cq.Workplane("XY")
        .box(length, 2.0 * r.block_hy_m, 0.018)
        .translate((centre_x, 0.0, -0.001))
    )
    bore = (
        cq.Workplane("XY")
        .center(r.screw_x_m - 0.012, 0.0)
        .circle(0.0060)
        .extrude(0.030, both=True)
    )
    return carrier.cut(bore)


def _thread_nut_shape() -> cq.Workplane:
    return cq.Workplane("XY").circle(0.0125).circle(0.0060).extrude(0.009, both=True)


def _fork_cheeks_shape(
    *,
    half_gap: float,
    cheek_t: float,
    cheek_w: float,
    cheek_top: float,
    bore_radius: float,
    axis: str = "y",
) -> cq.Workplane:
    """Two bored cheeks joined by a web below the pin, forming one solid fork.

    The web is placed clear of the bore so the mating pin never shares a volume
    with it, and the cheeks are grown down to the web so the fork is a single
    connected island that can seat on its host post or beam.
    """

    web_top = -(bore_radius + 0.0015)
    web_z = web_top - 0.005
    cheek_bottom = web_z - 0.005
    cheek_h = cheek_top - cheek_bottom
    cheek_dz = 0.5 * (cheek_top + cheek_bottom)
    result: cq.Workplane | None = None
    for sign in (-1.0, 1.0):
        if axis == "y":
            cheek = cq.Workplane("XY").box(cheek_w, cheek_t, cheek_h)
            cheek = cheek.translate((0.0, sign * (half_gap + 0.5 * cheek_t), cheek_dz))
            bore = (
                cq.Workplane("XZ")
                .circle(bore_radius)
                .extrude(half_gap + cheek_t + 0.002, both=True)
            )
        else:
            cheek = cq.Workplane("XY").box(cheek_t, cheek_w, cheek_h)
            cheek = cheek.translate((sign * (half_gap + 0.5 * cheek_t), 0.0, cheek_dz))
            bore = (
                cq.Workplane("YZ")
                .circle(bore_radius)
                .extrude(half_gap + cheek_t + 0.002, both=True)
            )
        cheek = cheek.cut(bore)
        result = cheek if result is None else result.union(cheek)
    assert result is not None
    span = 2.0 * (half_gap + cheek_t)
    if axis == "y":
        web = cq.Workplane("XY").box(cheek_w, span, 0.010).translate((0.0, 0.0, web_z))
    else:
        web = cq.Workplane("XY").box(span, cheek_w, 0.010).translate((0.0, 0.0, web_z))
    return result.union(web)


def _arm_housing_shape(r: ResolvedConfig, reach: float) -> cq.Workplane:
    """Moulded polymer link: the tapered side profile of 001.png."""

    k = reach / 0.204
    profile = [
        (-0.006 * k, -0.018),
        (0.026 * k, -0.030),
        (0.166 * k, -0.015),
        (0.202 * k, -0.002),
        (0.204 * k, 0.011),
        (0.181 * k, 0.026),
        (0.036 * k, 0.020),
        (0.004 * k, 0.012),
    ]
    return _side_extrusion(profile, 2.0 * r.arm_hy_m)


def _arm_plate_shape(r: ResolvedConfig, reach: float) -> cq.Workplane:
    """Skeletal twin-plate steel arm with real lightening holes."""

    profile = [
        (-0.010, -0.024),
        (0.030, -0.032),
        (reach - 0.020, -0.012),
        (reach, -0.002),
        (reach, 0.012),
        (reach - 0.030, 0.024),
        (0.040, 0.026),
        (0.004, 0.016),
    ]
    plate_t = 0.005
    result: cq.Workplane | None = None
    for sign in (-1.0, 1.0):
        plate = (
            cq.Workplane("XZ")
            .polyline(profile)
            .close()
            .extrude(plate_t * 0.5, both=True)
            .translate((0.0, sign * (r.arm_hy_m - 0.5 * plate_t), 0.0))
        )
        holes = max(2, int(reach / 0.055))
        for index in range(holes):
            x = 0.055 + (reach - 0.100) * (index + 0.5) / holes
            plate = plate.cut(
                cq.Workplane("XZ")
                .center(x, 0.000)
                .circle(0.011)
                .extrude(plate_t, both=True)
                .translate((0.0, sign * (r.arm_hy_m - 0.5 * plate_t), 0.0))
            )
        result = plate if result is None else result.union(plate)
    assert result is not None
    tie = (
        cq.Workplane("XY")
        .box(reach * 0.86, 2.0 * r.arm_hy_m - 0.002, 0.008)
        .translate((reach * 0.48, 0.0, -0.020))
    )
    return result.union(tie)


def _arm_tube_shape(r: ResolvedConfig, reach: float) -> cq.Workplane:
    """Round tubular arm with cast end lugs; the gas-strut family section."""

    radius = min(r.arm_hy_m * 0.92, 0.019)
    tube = (
        cq.Workplane("YZ")
        .circle(radius)
        .circle(radius - 0.004)
        .extrude(reach + 0.014)
        .translate((-0.004, 0.0, -0.004))
    )
    for x in (0.004, reach + 0.004):
        lug = (
            cq.Workplane("YZ")
            .rect(2.0 * r.arm_hy_m, 0.030)
            .extrude(0.018)
            .translate((x - 0.009, 0.0, -0.004))
            .edges("|X")
            .fillet(0.007)
        )
        tube = tube.union(lug)
    return tube


def _arm_beam_shape(r: ResolvedConfig, reach: float) -> cq.Workplane:
    """Hollow box-section beam with an integral top rail land."""

    width = 2.0 * r.arm_hy_m - 0.004
    outer = (
        cq.Workplane("YZ")
        .rect(width, 0.034)
        .extrude(reach + 0.016)
        .translate((-0.008, 0.0, -0.006))
    )
    inner = (
        cq.Workplane("YZ")
        .rect(width - 0.010, 0.024)
        .extrude(reach + 0.020)
        .translate((-0.010, 0.0, -0.006))
    )
    beam = outer.cut(inner)
    land = (
        cq.Workplane("XY")
        .box(reach + 0.010, width * 0.92, 0.012)
        .translate((0.5 * reach, 0.0, 0.017))
    )
    return beam.union(land)


_ARM_BODY_SHAPES = {
    "plain_arm": _arm_housing_shape,
    "ratchet_elbow": _arm_plate_shape,
    "gas_spring_arm": _arm_tube_shape,
    "linear_rail": _arm_beam_shape,
}
_ARM_REST_PITCH = {
    "plain_arm": 0.62,
    "ratchet_elbow": 0.50,
    "gas_spring_arm": 0.72,
    "linear_rail": 0.55,
}
_ARM_MATERIAL = {
    "plain_arm": "polymer",
    "ratchet_elbow": "steel",
    "gas_spring_arm": "dark",
    "linear_rail": "polymer",
}


def _link_bar_shape(length: float, height: float, depth: float,
                    end_bore: float | None = None) -> cq.Workplane:
    """Flat linkage bar with a real bored far end, used by the parallel family."""

    profile = [
        (-0.012, -0.5 * height),
        (length + 0.012, -0.5 * height * 0.72),
        (length + 0.012, 0.5 * height * 0.72),
        (-0.012, 0.5 * height),
    ]
    bar = _side_extrusion(profile, depth)
    bar = bar.union(cq.Workplane("XZ").circle(0.5 * height).extrude(0.5 * depth, both=True))
    end_boss = 0.36 * height if end_bore is None else max(0.36 * height, end_bore + 0.005)
    bar = bar.union(
        cq.Workplane("XZ")
        .center(length, 0.0)
        .circle(end_boss)
        .extrude(0.5 * depth, both=True)
    )
    if end_bore is not None:
        bar = bar.cut(
            cq.Workplane("XZ")
            .center(length, 0.0)
            .circle(end_bore)
            .extrude(depth, both=True)
        )
    return bar


def _column_post_shape(height: float) -> cq.Workplane:
    """Turned column with a real stepped shoulder and a hollow top socket."""

    post = (
        cq.Workplane("XY")
        .circle(0.0165)
        .extrude(height)
        .faces(">Z")
        .workplane()
        .circle(0.0075)
        .cutBlind(-0.020)
    )
    shoulder = cq.Workplane("XY").circle(0.0230).extrude(0.008)
    return post.union(shoulder)


def _sliding_collar_shape() -> cq.Workplane:
    """Split collar bored to run on the column with real running clearance."""

    collar = cq.Workplane("XY").circle(0.0265).extrude(0.020, both=True)
    bore = cq.Workplane("XY").circle(0.0173).extrude(0.030, both=True)
    relief = (
        cq.Workplane("XY")
        .box(0.008, 0.060, 0.024)
        .translate((0.026, 0.0, 0.0))
    )
    return collar.cut(bore).cut(relief)


def _radial_arm_shape(length: float, depth: float) -> cq.Workplane:
    profile = [
        (-0.011, -0.013),
        (length * 0.55, -0.011),
        (length + 0.012, -0.006),
        (length + 0.012, 0.006),
        (length * 0.55, 0.012),
        (-0.011, 0.014),
    ]
    arm = _side_extrusion(profile, depth)
    return arm.union(cq.Workplane("XZ").circle(0.0125).extrude(0.5 * depth, both=True))


def _sector_teeth_shape() -> cq.Workplane:
    """Ratchet sector with visible asymmetric teeth, profile in the XZ plane."""

    root_r, tip_r, inner_r = 0.028, 0.037, 0.016
    num_teeth = 7
    half_arc = math.radians(30.0)
    pitch = (2.0 * half_arc) / num_teeth
    pts: list[tuple[float, float]] = []
    for i in range(num_teeth):
        a0 = -half_arc + i * pitch
        pts.append((root_r * math.sin(a0), root_r * math.cos(a0)))
        a1 = a0 + pitch * 0.15
        pts.append((tip_r * math.sin(a1), tip_r * math.cos(a1)))
        a2 = a0 + pitch * 0.40
        pts.append((tip_r * math.sin(a2), tip_r * math.cos(a2)))
        a3 = a0 + pitch * 0.50
        pts.append((root_r * math.sin(a3), root_r * math.cos(a3)))
    pts.append((root_r * math.sin(half_arc), root_r * math.cos(half_arc)))
    n_inner = 14
    for i in range(n_inner + 1):
        a = half_arc - i * (2.0 * half_arc) / n_inner
        pts.append((inner_r * math.sin(a), inner_r * math.cos(a)))
    wp = cq.Workplane("XZ").moveTo(pts[0][0], pts[0][1])
    for point in pts[1:]:
        wp = wp.lineTo(point[0], point[1])
    return wp.close().extrude(0.0035, both=True)


def _pawl_shape() -> cq.Workplane:
    body = cq.Workplane("XZ").box(0.032, 0.011, 0.005).translate((0.010, 0.0, 0.0))
    tooth = cq.Workplane("XZ").box(0.006, 0.010, 0.005).translate((-0.008, 0.0, -0.008))
    boss = cq.Workplane("XZ").circle(0.006).circle(0.0032).extrude(0.0035, both=True)
    return body.union(tooth).union(boss)


def _saddle_shell(outer_radius: float, thickness: float, length: float,
                  width: float, *, depth_ratio: float = 1.0,
                  taper: float = 0.0) -> cq.Workplane:
    """A clipped annular cylinder produces a genuinely concave trough.

    `depth_ratio` sets how deep the channel is (a narrow deep forearm trough
    versus a shallow dished palm rest) and `taper` waists the plan toward one
    end, so the three head candidates do not share one section.
    """

    inner_radius = outer_radius - thickness
    centre_z = outer_radius - 0.006
    ring = (
        cq.Workplane("YZ")
        .circle(outer_radius)
        .circle(inner_radius)
        .extrude(length * 0.5, both=True)
        .translate((0.0, 0.0, centre_z))
    )
    clip_h = 0.032 * depth_ratio
    clip = cq.Workplane("XY").box(length, width, clip_h).translate((0.0, 0.0, 0.5 * clip_h))
    shell = ring.intersect(clip)
    if taper > 0.0:
        wedge = (
            cq.Workplane("XY")
            .polyline(
                [
                    (0.5 * length + 0.004, 0.5 * width + 0.01),
                    (0.5 * length + 0.004, -0.5 * width - 0.01),
                    (-0.5 * length - 0.004, -0.5 * width * taper),
                    (-0.5 * length - 0.004, 0.5 * width * taper),
                ]
            )
            .close()
            .extrude(0.060, both=True)
        )
        shell = shell.intersect(wedge)
    return shell


# ---------------------------------------------------------------------------
# clamp host
# ---------------------------------------------------------------------------


def _build_clamp(model: ArticulatedObject, r: ResolvedConfig, mats) -> object:
    """Build the always-present screw clamp and return its frame part."""

    frame = model.part("clamp__frame", meta={"role": "clamp_frame"})
    frame.visual(
        mesh_from_cadquery(_clamp_frame_shape(r), "clamp__frame_web", tolerance=0.0008),
        material=mats["powder"],
        name="clamp__frame__c_frame", material_class_id="metal.paint_coated",
    )
    frame.visual(
        Cylinder(radius=0.020, length=0.006),
        origin=Origin(xyz=(r.screw_x_m, 0.0, r.plate_bottom_m - 0.002)),
        material=mats["rubber"],
        name="clamp__frame__fixed_jaw_pad", material_class_id="rubber.smooth_plain",
    )
    rail_centre = 0.5 * (r.rail_z0_m + r.rail_z1_m)
    rail_len = r.rail_z1_m - r.rail_z0_m
    for index, sign in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.024, 0.010, rail_len)),
            origin=Origin(xyz=(0.012, sign * r.rail_y_m, rail_centre)),
            material=mats["dark"],
            name=f"clamp__frame__guide_rail_{index}", material_class_id="metal.blackened_gunmetal",
        )
    host = _BASE_REACH_BUILDERS[r.base_reach](model, r, mats, frame)
    _build_head_mount(model, r, mats, host)
    return frame


def _host_point(r: ResolvedConfig, x: float, y: float, z: float) -> tuple[float, float, float]:
    """Express a world head-mount coordinate in the arm host's local frame."""

    return (x + r.host_x_off_m, y, z + r.host_z_off_m)


def _support_host(model: ArticulatedObject, r: ResolvedConfig):
    """The part every support candidate is pinned to: frame, or reach carriage."""

    if r.base_reach == "edge_track":
        return model.get_part("base_reach__edge_track__carriage")
    return model.get_part("clamp__frame")


def _base_reach_fixed_mount_build(model: ArticulatedObject, r: ResolvedConfig, mats, frame):
    """001.png: the support base is pinned straight to the clamp frame head."""

    return frame


def _base_reach_edge_track_build(model: ArticulatedObject, r: ResolvedConfig, mats, frame):
    """desk_edge_track fork L402-L446: a captured carriage on a desk-edge rail.

    Two rails stand clear in front of the guided jaw on a pair of side arms, and
    the carriage that carries the whole support base slides along them.
    """

    rail_x = r.track_rail_x_m
    rail_z = r.track_rail_z_m
    half_len = r.track_stroke_m + 0.030
    # The rail head stands above the guided-jaw envelope and behind the elbow,
    # so neither the coarse jaw nor the swept support arm can reach it.
    frame.visual(
        Box((0.034, 0.030, 0.014)),
        origin=Origin(xyz=(0.017, 0.0, rail_z)),
        material=mats["powder"],
        name="clamp__frame__track_bracket", material_class_id="metal.paint_coated",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        frame.visual(
            Cylinder(radius=0.005, length=2.0 * half_len),
            origin=Origin(
                xyz=(rail_x, 0.0, rail_z + sign * 0.012),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["dark"],
            name=f"clamp__frame__track_rail_{index}", material_class_id="metal.blackened_gunmetal",
        )

    carriage = model.part(
        "base_reach__edge_track__carriage",
        meta={"role": "reach_carriage", "candidate": "edge_track"},
    )
    carriage.visual(
        Box((0.012, 0.048, 0.040)),
        origin=Origin(xyz=(0.0115, 0.0, 0.0)),
        material=mats["powder"],
        name="base_reach__edge_track__carriage__slide_plate", material_class_id="metal.paint_coated",
    )
    drop = rail_z - r.elbow_z_m
    for index, sign in enumerate((-1.0, 1.0)):
        carriage.visual(
            Box((0.014, 0.048, 0.008)),
            origin=Origin(xyz=(0.0, 0.0, sign * 0.0215)),
            material=mats["dark"],
            name=f"base_reach__edge_track__carriage__rail_lip_{index}", material_class_id="metal.blackened_gunmetal",
        )
        # Both drop legs run outboard of the arm body, in the same planes as the
        # clevis cheeks, so the swept rising arm never meets them.
        carriage.visual(
            Box((0.014, 0.014, drop + 0.006)),
            origin=Origin(
                xyz=(0.020, sign * r.clevis_y_m, -0.5 * drop + 0.002)
            ),
            material=mats["powder"],
            name=f"base_reach__edge_track__carriage__drop_leg_{index}", material_class_id="metal.paint_coated",
        )
        carriage.visual(
            Box((0.030, 0.014, 0.014)),
            origin=Origin(
                xyz=(0.032, sign * r.clevis_y_m, -drop)
            ),
            material=mats["powder"],
            name=f"base_reach__edge_track__carriage__elbow_arm_{index}", material_class_id="metal.paint_coated",
        )
    model.articulation(
        "base_reach__edge_track__carriage_slide",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=carriage,
        origin=Origin(xyz=(rail_x, 0.0, rail_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=400.0,
            velocity=0.10,
            lower=-r.track_stroke_m,
            upper=r.track_stroke_m,
        ),
        meta={"mechanism": "desk-edge lateral reach carriage"},
    )
    return carriage


_BASE_REACH_BUILDERS = {
    "fixed_mount": _base_reach_fixed_mount_build,
    "edge_track": _base_reach_edge_track_build,
}


def _build_head_mount(model: ArticulatedObject, r: ResolvedConfig, mats, host) -> None:
    """Host adaptation: a side clevis for arm families, a socket for columns."""

    prefix = host.name
    if r.support_linkage in _COLUMN_CANDIDATES:
        # The shelf clears the whole guided-jaw travel envelope before the
        # column socket starts, so the coarse jaw never runs into the column.
        shelf_z = r.jaw_z_m + r.travel_up_m + 0.025
        shelf_x0 = 0.020 - 0.034 if r.base_reach == "fixed_mount" else r.track_rail_x_m
        shelf_x1 = r.elbow_x_m + 0.034
        shelf_point = _host_point(r, 0.5 * (shelf_x0 + shelf_x1), 0.0, shelf_z)
        host.visual(
            Box((shelf_x1 - shelf_x0, 2.0 * r.rail_y_m + 0.010, 0.016)),
            origin=Origin(xyz=shelf_point),
            material=mats["powder"],
            name=f"{prefix}__column_shelf", material_class_id="metal.paint_coated",
        )
        host.visual(
            Cylinder(radius=0.0230, length=0.018),
            origin=Origin(xyz=_host_point(r, r.elbow_x_m, 0.0, shelf_z + 0.017)),
            material=mats["dark"],
            name=f"{prefix}__column_socket", material_class_id="metal.blackened_gunmetal",
        )
        return
    for index, sign in enumerate((-1.0, 1.0)):
        host.visual(
            Box((0.042, 0.014, 0.046)),
            origin=Origin(
                xyz=_host_point(r, r.elbow_x_m, sign * r.clevis_y_m, r.elbow_z_m)
            ),
            material=mats["powder"],
            name=f"{prefix}__arm_clevis_{index}", material_class_id="metal.paint_coated",
        )
        host.visual(
            Cylinder(radius=0.015, length=0.014),
            origin=Origin(
                xyz=_host_point(r, r.elbow_x_m, sign * r.clevis_y_m, r.elbow_z_m),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["powder"],
            name=f"{prefix}__arm_boss_{index}", material_class_id="metal.paint_coated",
        )
    if r.support_linkage == "ratchet_elbow":
        host.visual(
            mesh_from_cadquery(_sector_teeth_shape(), f"{prefix}__sector", tolerance=0.0006),
            origin=Origin(
                xyz=_host_point(r, r.elbow_x_m, r.clevis_y_m + 0.0065, r.elbow_z_m)
            ),
            material=mats["steel"],
            name=f"{prefix}__sector_teeth", material_class_id="metal.stainless_matte",
        )


def _build_jaw(model: ArticulatedObject, r: ResolvedConfig, mats, frame):
    """The guided coarse jaw, shared by both clamp actuations."""

    jaw = model.part("clamp__movable_jaw", meta={"role": "clamp_jaw"})
    jaw.visual(
        Box((0.020, 2.0 * r.block_hy_m, 0.034)),
        origin=Origin(),
        material=mats["dark"],
        name="clamp__movable_jaw__guide_block", material_class_id="metal.blackened_gunmetal",
    )
    jaw.visual(
        mesh_from_cadquery(_jaw_carrier_shape(r), "clamp__jaw_carrier", tolerance=0.0006),
        material=mats["powder"],
        name="clamp__movable_jaw__carrier", material_class_id="metal.paint_coated",
    )
    model.articulation(
        "clamp__jaw_slide",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=jaw,
        origin=Origin(xyz=(0.012, 0.0, r.jaw_z_m)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=900.0, velocity=0.08, lower=r.travel_dn_m, upper=r.travel_up_m
        ),
        meta={"mechanism": "guided coarse jaw adjustment"},
    )
    return jaw


def _add_pressure_shoe(model, r, mats, *, parent, seat_point, prefix: str):
    """The self-aligning pressure shoe carried by whichever actuation drives it."""

    shoe = model.part("clamp__pressure_pad", meta={"role": "clamp_shoe"})
    shoe.visual(
        Sphere(radius=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
        material=mats["steel"],
        name="clamp__pressure_pad__ball", material_class_id="metal.stainless_matte",
    )
    shoe.visual(
        Cylinder(radius=0.018, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.009)),
        material=mats["dark"],
        name="clamp__pressure_pad__plate", material_class_id="metal.blackened_gunmetal",
    )
    shoe.visual(
        Cylinder(radius=0.017, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, 0.014)),
        material=mats["rubber"],
        name="clamp__pressure_pad__face", material_class_id="rubber.smooth_plain",
    )
    shoe_provider = AxisInterface(
        name=f"{prefix}.shoe_seat",
        point=seat_point,
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.006,
    )
    shoe_consumer = AxisInterface(
        name="clamp.shoe_ball",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0058,
    )
    shoe_mate = mate_axes(shoe_provider, shoe_consumer)
    model.articulation(
        "clamp__pressure_pad_pivot",
        ArticulationType.REVOLUTE,
        parent=parent,
        child=shoe,
        origin=shoe_mate.origin,
        axis=shoe_mate.axis,
        motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=-0.18, upper=0.18),
        meta={"mechanism": "self-aligning pressure shoe"},
    )
    register_interface_mate(model, "clamp__pressure_pad_pivot", shoe_mate)
    return shoe


def _clamp_actuation_screw_spindle_build(
    model: ArticulatedObject, r: ResolvedConfig, mats, frame
) -> None:
    """001.png L189-L376: threaded spindle in a nut on the guided jaw."""

    jaw = _build_jaw(model, r, mats, frame)
    jaw.visual(
        mesh_from_cadquery(_thread_nut_shape(), "clamp__thread_nut", tolerance=0.0005),
        origin=Origin(xyz=(r.screw_x_m - 0.012, 0.0, -0.001)),
        material=mats["dark"],
        name="clamp__movable_jaw__thread_nut", material_class_id="metal.blackened_gunmetal",
    )

    spindle = model.part("clamp__spindle", meta={"role": "clamp_screw"})
    shaft_len = 0.132
    spindle.visual(
        Cylinder(radius=0.0048, length=shaft_len),
        origin=Origin(xyz=(0.0, 0.0, -0.5 * shaft_len)),
        material=mats["steel"],
        name="clamp__spindle__screw_shaft", material_class_id="metal.stainless_matte",
    )
    for index in range(5):
        spindle.visual(
            Cylinder(radius=0.0064, length=0.0025),
            origin=Origin(xyz=(0.0, 0.0, -0.020 - 0.016 * index)),
            material=mats["dark"],
            name=f"clamp__spindle__thread_crest_{index}", material_class_id="metal.blackened_gunmetal",
        )
    spindle.visual(
        Sphere(radius=0.010),
        origin=Origin(xyz=(0.0, 0.0, -shaft_len - 0.004)),
        material=mats["polymer"],
        name="clamp__spindle__handle_hub", material_class_id="plastic.opaque_glossy_molded",
    )
    spindle.visual(
        Cylinder(radius=0.0045, length=0.072),
        origin=Origin(xyz=(0.0, 0.0, -shaft_len - 0.004), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["dark"],
        name="clamp__spindle__tommy_bar", material_class_id="metal.blackened_gunmetal",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        spindle.visual(
            Sphere(radius=0.007),
            origin=Origin(xyz=(sign * 0.036, 0.0, -shaft_len - 0.004)),
            material=mats["polymer"],
            name=f"clamp__spindle__handle_end_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    spindle_provider = AxisInterface(
        name="clamp.spindle_bore",
        point=(r.screw_x_m - 0.012, 0.0, 0.012),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0060,
    )
    spindle_consumer = AxisInterface(
        name="clamp.spindle_shank",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0048,
    )
    spindle_mate = mate_axes(spindle_provider, spindle_consumer)
    model.articulation(
        "clamp__spindle_turn",
        ArticulationType.CONTINUOUS,
        parent=jaw,
        child=spindle,
        origin=spindle_mate.origin,
        axis=spindle_mate.axis,
        motion_limits=MotionLimits(effort=30.0, velocity=8.0),
        meta={"mechanism": "threaded fine-clamp screw"},
    )
    register_interface_mate(model, "clamp__spindle_turn", spindle_mate)

    _add_pressure_shoe(
        model, r, mats, parent=spindle, seat_point=(0.0, 0.0, 0.002), prefix="clamp"
    )


def _clamp_actuation_overcenter_cam_build(
    model: ArticulatedObject, r: ResolvedConfig, mats, frame
) -> None:
    """overcenter_cam fork L332-L440: a cam lever and follower link replace the screw.

    The lever hangs below the guided jaw and swings down, so its whole envelope
    stays clear of the throat, the frame web and the support head above.
    """

    jaw = _build_jaw(model, r, mats, frame)
    screw_x = r.screw_x_m - 0.012  # jaw-local X of the clamping axis
    follower_pivot = (screw_x + 0.000, 0.0, -0.004)
    cam_pivot = (screw_x - 0.030, 0.0, -0.026)
    # Two side rails cast off the jaw carrier carry both pivots and leave a
    # clear central channel for the lever and the follower link to swing in.
    for index, sign in enumerate((-1.0, 1.0)):
        jaw.visual(
            Box((0.058, 0.010, 0.020)),
            origin=Origin(xyz=(screw_x - 0.024, sign * 0.013, -0.008)),
            material=mats["powder"],
            name=f"clamp__movable_jaw__cam_rail_{index}", material_class_id="metal.paint_coated",
        )
        for name, point in (("follower", follower_pivot), ("cam", cam_pivot)):
            jaw.visual(
                Box((0.018, 0.006, 0.018)),
                origin=Origin(
                    xyz=(point[0], sign * 0.014, point[2] + 0.005)
                ),
                material=mats["powder"],
                name=f"clamp__movable_jaw__{name}_cheek_{index}", material_class_id="metal.paint_coated",
            )

    lever = model.part("clamp__cam_lever", meta={"role": "clamp_cam_lever"})
    lever.visual(
        Cylinder(radius=0.0050, length=0.021),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="clamp__cam_lever__pivot_shaft", material_class_id="metal.stainless_matte",
    )
    lever.visual(
        Box((0.012, 0.010, 0.008)),
        origin=Origin(xyz=(0.009, 0.0, 0.0)),
        material=mats["dark"],
        name="clamp__cam_lever__lobe", material_class_id="metal.blackened_gunmetal",
    )
    lever.visual(
        Box((0.042, 0.012, 0.010)),
        origin=Origin(xyz=(-0.021, 0.0, 0.0)),
        material=mats["polymer"],
        name="clamp__cam_lever__arm", material_class_id="plastic.opaque_glossy_molded",
    )
    lever.visual(
        Cylinder(radius=0.0075, length=0.020),
        origin=Origin(xyz=(-0.044, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["rubber"],
        name="clamp__cam_lever__grip", material_class_id="rubber.smooth_plain",
    )
    lever.visual(
        Sphere(radius=0.0040),
        origin=Origin(xyz=(0.009, 0.0, -0.007)),
        material=mats["steel"],
        name="clamp__cam_lever__overcentre_detent", material_class_id="metal.stainless_matte",
    )
    lever_provider = AxisInterface(
        name="clamp.cam_boss",
        point=cam_pivot,
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0053,
    )
    lever_consumer = AxisInterface(
        name="clamp.cam_shaft",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0050,
    )
    lever_mate = mate_axes(lever_provider, lever_consumer)
    model.articulation(
        "clamp__cam_lever_swing",
        ArticulationType.REVOLUTE,
        parent=jaw,
        child=lever,
        origin=lever_mate.origin,
        axis=lever_mate.axis,
        motion_limits=MotionLimits(effort=40.0, velocity=4.0, lower=-0.75, upper=0.0),
        meta={"mechanism": "over-centre cam lever fine clamp"},
    )
    register_interface_mate(model, "clamp__cam_lever_swing", lever_mate)

    follower = model.part("clamp__cam_follower", meta={"role": "clamp_follower"})
    follower.visual(
        Cylinder(radius=0.0045, length=0.021),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="clamp__cam_follower__pivot_barrel", material_class_id="metal.stainless_matte",
    )
    follower.visual(
        Box((0.026, 0.013, 0.008)),
        origin=Origin(xyz=(-0.011, 0.0, 0.002)),
        material=mats["dark"],
        name="clamp__cam_follower__link", material_class_id="metal.blackened_gunmetal",
    )
    follower.visual(
        Cylinder(radius=0.0040, length=0.011),
        origin=Origin(xyz=(-0.020, 0.0, -0.001), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="clamp__cam_follower__roller", material_class_id="metal.stainless_matte",
    )
    follower.visual(
        Cylinder(radius=0.0050, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, 0.010)),
        material=mats["dark"],
        name="clamp__cam_follower__pad_stem", material_class_id="metal.blackened_gunmetal",
    )
    follower_provider = AxisInterface(
        name="clamp.follower_boss",
        point=follower_pivot,
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0048,
    )
    follower_consumer = AxisInterface(
        name="clamp.follower_barrel",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0045,
    )
    follower_mate = mate_axes(follower_provider, follower_consumer)
    model.articulation(
        "clamp__follower_pivot",
        ArticulationType.REVOLUTE,
        parent=jaw,
        child=follower,
        origin=follower_mate.origin,
        axis=follower_mate.axis,
        motion_limits=MotionLimits(effort=25.0, velocity=3.0, lower=-0.10, upper=0.10),
        meta={"mechanism": "cam-driven follower link"},
    )
    register_interface_mate(model, "clamp__follower_pivot", follower_mate)

    _add_pressure_shoe(
        model, r, mats, parent=follower, seat_point=(0.0, 0.0, 0.018), prefix="clamp.follower"
    )


_CLAMP_ACTUATION_BUILDERS = {
    "screw_spindle": _clamp_actuation_screw_spindle_build,
    "overcenter_cam": _clamp_actuation_overcenter_cam_build,
}


# ---------------------------------------------------------------------------
# grip controls shared by every support candidate
# ---------------------------------------------------------------------------


def _add_grip_controls(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats,
    *,
    grip_part,
    prefix: str,
    trigger_x: float,
    release_x: float,
    body_z: float,
    half_depth: float,
) -> None:
    """Squeeze trigger and thumb release carried by the graspable link."""

    cheek_y = half_depth - 0.002
    for index, sign in enumerate((-1.0, 1.0)):
        grip_part.visual(
            Box((0.024, 0.006, 0.026)),
            origin=Origin(xyz=(trigger_x, sign * cheek_y, body_z - 0.019)),
            material=mats["polymer"],
            name=f"{prefix}__trigger_cheek_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    grip_part.visual(
        Cylinder(radius=0.009, length=0.010),
        origin=Origin(
            xyz=(release_x, half_depth - 0.002, body_z + 0.008),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["dark"],
        name=f"{prefix}__release_boss", material_class_id="metal.blackened_gunmetal",
    )

    trigger = model.part(f"{prefix}__trigger", meta={"role": "adjust_control"})
    trigger.visual(
        Cylinder(radius=0.006, length=2.0 * (cheek_y - 0.003) - 0.0008),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__trigger__barrel", material_class_id="metal.blackened_gunmetal",
    )
    trigger.visual(
        Box((0.018, 0.012, 0.044)),
        origin=Origin(xyz=(-0.003, 0.0, -0.025), rpy=(0.0, -0.16, 0.0)),
        material=mats["polymer"],
        name=f"{prefix}__trigger__grip", material_class_id="plastic.opaque_glossy_molded",
    )
    trigger.visual(
        Box((0.020, 0.014, 0.010)),
        origin=Origin(xyz=(0.004, 0.0, -0.048)),
        material=mats["rubber"],
        name=f"{prefix}__trigger__tip", material_class_id="rubber.smooth_plain",
    )
    trigger_provider = AxisInterface(
        name=f"{prefix}.trigger_seat",
        point=(trigger_x, 0.0, body_z - 0.030),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0062,
    )
    trigger_consumer = AxisInterface(
        name=f"{prefix}.trigger_barrel",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.006,
    )
    trigger_mate = mate_axes(trigger_provider, trigger_consumer)
    model.articulation(
        f"{prefix}__trigger_squeeze",
        ArticulationType.REVOLUTE,
        parent=grip_part,
        child=trigger,
        origin=trigger_mate.origin,
        axis=trigger_mate.axis,
        motion_limits=MotionLimits(effort=5.0, velocity=3.0, lower=0.0, upper=0.28),
        meta={"mechanism": "squeeze trigger for the adjustment lock"},
    )
    register_interface_mate(model, f"{prefix}__trigger_squeeze", trigger_mate)

    release = model.part(f"{prefix}__release_lever", meta={"role": "adjust_control"})
    release.visual(
        Cylinder(radius=0.0065, length=0.008),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__release_lever__barrel", material_class_id="metal.blackened_gunmetal",
    )
    release.visual(
        Box((0.030, 0.010, 0.010)),
        origin=Origin(xyz=(0.015, 0.0, 0.003), rpy=(0.0, -0.14, 0.0)),
        material=mats["polymer"],
        name=f"{prefix}__release_lever__tab", material_class_id="plastic.opaque_glossy_molded",
    )
    release.visual(
        Sphere(radius=0.007),
        origin=Origin(xyz=(0.030, 0.0, 0.006)),
        material=mats["rubber"],
        name=f"{prefix}__release_lever__tip", material_class_id="rubber.smooth_plain",
    )
    release_provider = AxisInterface(
        name=f"{prefix}.release_seat",
        point=(release_x, half_depth + 0.008, body_z + 0.008),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0068,
    )
    release_consumer = AxisInterface(
        name=f"{prefix}.release_barrel",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0065,
    )
    release_mate = mate_axes(release_provider, release_consumer)
    model.articulation(
        f"{prefix}__release_flick",
        ArticulationType.REVOLUTE,
        parent=grip_part,
        child=release,
        origin=release_mate.origin,
        axis=release_mate.axis,
        motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=-0.18, upper=0.26),
        meta={"mechanism": "independent thumb release"},
    )
    register_interface_mate(model, f"{prefix}__release_flick", release_mate)


def _add_seat_pad(part, mats, *, name: str, point: tuple[float, float, float],
                  pitch: float) -> None:
    """Machined boss coaxial with the wrist column; its top face carries the collar.

    The boss must follow the same axis as the collar, otherwise a pitched link
    would drive a vertical collar straight through a link-aligned pad.
    """

    length = 0.030
    ux, uz = math.sin(pitch), math.cos(pitch)
    offset = 0.004 + 0.5 * length
    part.visual(
        Cylinder(radius=0.016, length=length),
        origin=Origin(
            xyz=(point[0] - ux * offset, point[1], point[2] - uz * offset),
            rpy=(0.0, pitch, 0.0),
        ),
        material=mats["dark"],
        name=name, material_class_id="metal.blackened_gunmetal",
    )


def _gas_cylinder_shape(body_len: float) -> cq.Workplane:
    """Real gas-spring tube: a closed base and a bore that accepts the rod."""

    tube = (
        cq.Workplane("YZ")
        .circle(0.0115)
        .extrude(body_len)
        .translate((0.0, 0.0, 0.0))
    )
    bore = (
        cq.Workplane("YZ")
        .circle(0.0066)
        .extrude(body_len)
        .translate((0.008, 0.0, 0.0))
    )
    return tube.cut(bore)


def _elbow_axis_mate(r: ResolvedConfig, *, prefix: str, bore_radius: float,
                     spin: float = _REST_PITCH):
    provider = AxisInterface(
        name="clamp.elbow_axis",
        point=_host_point(r, r.elbow_x_m, 0.0, r.elbow_z_m),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.015,
    )
    consumer = AxisInterface(
        name=f"{prefix}.elbow_bore",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=bore_radius,
    )
    return mate_axes(provider, consumer, spin=spin)


def _add_rising_arm(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats,
    *,
    candidate: str,
    reach: float,
):
    """The rising arm.  Each candidate has its own body section; a shared spine
    and head riser carry the controls and the head seat so the mechanics stay
    identical while the visible arm really changes."""

    prefix = f"support_linkage__{candidate}"
    arm = model.part(f"{prefix}__arm", meta={"role": "support_arm", "candidate": candidate})
    arm.visual(
        mesh_from_cadquery(
            _ARM_BODY_SHAPES[candidate](r, reach), f"{prefix}__arm_body", tolerance=0.0008
        ),
        material=mats[_ARM_MATERIAL[candidate]],
        name=f"{prefix}__arm__housing", material_class_id=("plastic.opaque_glossy_molded" if r.support_linkage in {"plain_arm", "linear_rail"} else "metal.blackened_gunmetal"),
    )
    arm.visual(
        Cylinder(radius=0.016, length=r.barrel_len_m),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__arm__base_barrel", material_class_id="metal.blackened_gunmetal",
    )
    arm.visual(
        Box((reach + 0.020, 2.0 * r.arm_hy_m - 0.002, 0.026)),
        origin=Origin(xyz=(reach * 0.5 - 0.005, 0.0, -0.007)),
        material=mats["dark"],
        name=f"{prefix}__arm__spine", material_class_id="metal.blackened_gunmetal",
    )
    arm.visual(
        Box((0.050, 2.0 * r.arm_hy_m * 0.82, 0.030)),
        origin=Origin(xyz=(reach * 0.90, 0.0, 0.008)),
        material=mats["dark"],
        name=f"{prefix}__arm__head_riser", material_class_id="metal.blackened_gunmetal",
    )
    for index, factor in enumerate((0.12, 0.86, 0.96)):
        arm.visual(
            Cylinder(radius=0.006, length=2.0 * r.arm_hy_m + 0.004),
            origin=Origin(xyz=(reach * factor, 0.0, 0.000), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["steel"],
            name=f"{prefix}__arm__pivot_fastener_{index}", material_class_id="metal.stainless_matte",
        )
    mate = _elbow_axis_mate(
        r, prefix=prefix, bore_radius=0.0148, spin=_ARM_REST_PITCH[candidate]
    )
    joint = f"{prefix}__arm_pitch"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=_support_host(model, r),
        child=arm,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=120.0, velocity=1.2, lower=-0.28, upper=0.38),
        meta={"mechanism": "rising support arm"},
    )
    register_interface_mate(model, joint, mate)
    return arm


def _seat(part, point: tuple[float, float, float], pitch: float) -> dict:
    return {"part": part, "point": point, "pitch": pitch}


# ---------------------------------------------------------------------------
# support_linkage candidates
# ---------------------------------------------------------------------------


def _support_linkage_plain_arm_build(model, r, mats):
    candidate = "plain_arm"
    prefix = f"support_linkage__{candidate}"
    reach = r.arm_reach_m
    arm = _add_rising_arm(model, r, mats, candidate=candidate, reach=reach)
    _add_grip_controls(
        model, r, mats, grip_part=arm, prefix=prefix,
        trigger_x=reach * 0.25, release_x=reach * 0.42, body_z=-0.008,
        half_depth=r.arm_hy_m,
    )
    seat = (reach * 0.90, 0.0, 0.046)
    _add_seat_pad(
        arm, mats, name=f"{prefix}__arm__head_seat_pad", point=seat,
        pitch=_ARM_REST_PITCH[candidate],
    )
    return _seat(arm, seat, _ARM_REST_PITCH[candidate])


def _support_linkage_ratchet_elbow_build(model, r, mats):
    candidate = "ratchet_elbow"
    prefix = f"support_linkage__{candidate}"
    reach = r.arm_reach_m
    arm = _add_rising_arm(model, r, mats, candidate=candidate, reach=reach)
    _add_grip_controls(
        model, r, mats, grip_part=arm, prefix=prefix,
        trigger_x=reach * 0.25, release_x=reach * 0.42, body_z=-0.008,
        half_depth=r.arm_hy_m,
    )
    # The sector sits on the outer clevis cheek; the pawl runs in the next plane
    # outboard of it so the tooth crowns stay adjacent instead of interpenetrating.
    pawl_y = r.clevis_y_m + 0.0165
    pawl_x, pawl_z = 0.046, 0.008
    pawl = model.part(f"{prefix}__pawl", meta={"role": "index_pawl", "candidate": candidate})
    pawl.visual(
        mesh_from_cadquery(_pawl_shape(), f"{prefix}__pawl_body", tolerance=0.0005),
        material=mats["steel"],
        name=f"{prefix}__pawl__body", material_class_id="metal.stainless_matte",
    )
    pawl.visual(
        Cylinder(radius=0.003, length=0.008),
        origin=Origin(xyz=(0.028, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__pawl__spring_nub", material_class_id="metal.blackened_gunmetal",
    )
    boss_len = pawl_y - r.arm_hy_m + 0.004
    arm.visual(
        Cylinder(radius=0.0062, length=boss_len),
        origin=Origin(
            xyz=(pawl_x, r.arm_hy_m + 0.5 * boss_len - 0.002, pawl_z),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["dark"],
        name=f"{prefix}__arm__pawl_boss", material_class_id="metal.blackened_gunmetal",
    )
    provider = AxisInterface(
        name=f"{prefix}.pawl_seat",
        point=(pawl_x, pawl_y, pawl_z),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0062,
    )
    consumer = AxisInterface(
        name=f"{prefix}.pawl_bore",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0032,
    )
    mate = mate_axes(provider, consumer)
    joint = f"{prefix}__pawl_engage"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=arm,
        child=pawl,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=4.0, velocity=5.0, lower=-0.16, upper=0.20),
        meta={"mechanism": "ratchet pawl engaging the frame sector"},
    )
    register_interface_mate(model, joint, mate)
    seat = (reach * 0.90, 0.0, 0.046)
    _add_seat_pad(
        arm, mats, name=f"{prefix}__arm__head_seat_pad", point=seat,
        pitch=_ARM_REST_PITCH[candidate],
    )
    return _seat(arm, seat, _ARM_REST_PITCH[candidate])


def _support_linkage_gas_spring_arm_build(model, r, mats):
    candidate = "gas_spring_arm"
    prefix = f"support_linkage__{candidate}"
    reach = r.arm_reach_m
    arm = _add_rising_arm(model, r, mats, candidate=candidate, reach=reach)
    _add_grip_controls(
        model, r, mats, grip_part=arm, prefix=prefix,
        trigger_x=reach * 0.25, release_x=reach * 0.42, body_z=-0.008,
        half_depth=r.arm_hy_m,
    )

    # The strut runs outboard of both clevis cheeks so it never shares a volume
    # with the rising arm, the guided jaw or the trigger.
    strut_y = r.clevis_y_m + 0.004
    strut_pivot_y = r.clevis_y_m + 0.0325
    cylinder = model.part(
        f"{prefix}__gas_cylinder", meta={"role": "support_link", "candidate": candidate}
    )
    body_len = 0.078
    cylinder.visual(
        mesh_from_cadquery(
            _gas_cylinder_shape(body_len), f"{prefix}__gas_tube", tolerance=0.0006
        ),
        material=mats["dark"],
        name=f"{prefix}__gas_cylinder__body", material_class_id="metal.blackened_gunmetal",
    )
    cylinder.visual(
        Cylinder(radius=0.0075, length=0.012),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__gas_cylinder__eye", material_class_id="metal.stainless_matte",
    )
    host = _support_host(model, r)
    host.visual(
        Box((0.030, 0.012, 0.052)),
        origin=Origin(xyz=_host_point(r, r.elbow_x_m - 0.004, strut_y, r.elbow_z_m - 0.020)),
        material=mats["powder"],
        name=f"{host.name}__strut_bracket", material_class_id="metal.paint_coated",
    )
    host.visual(
        Cylinder(radius=0.0072, length=0.010),
        origin=Origin(
            xyz=_host_point(
                r, r.elbow_x_m - 0.004, r.clevis_y_m + 0.015, r.elbow_z_m - 0.038
            ),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["dark"],
        name=f"{host.name}__strut_boss", material_class_id="metal.blackened_gunmetal",
    )
    provider = AxisInterface(
        name="clamp.strut_seat",
        point=_host_point(r, r.elbow_x_m - 0.004, strut_pivot_y, r.elbow_z_m - 0.038),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0072,
    )
    consumer = AxisInterface(
        name=f"{prefix}.strut_eye",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0070,
    )
    mate = mate_axes(provider, consumer, spin=0.80)
    joint = f"{prefix}__gas_spring_base_pivot"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=host,
        child=cylinder,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=60.0, velocity=1.2, lower=-0.20, upper=0.20),
        meta={"mechanism": "gas-spring base pivot"},
    )
    register_interface_mate(model, joint, mate)

    piston = model.part(
        f"{prefix}__gas_piston", meta={"role": "support_link", "candidate": candidate}
    )
    piston.visual(
        Cylinder(radius=0.0058, length=0.076),
        origin=Origin(xyz=(0.010, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__gas_piston__rod", material_class_id="metal.stainless_matte",
    )
    piston.visual(
        Sphere(radius=0.0082),
        origin=Origin(xyz=(0.048, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__gas_piston__eye", material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        f"{prefix}__gas_spring_extension",
        ArticulationType.PRISMATIC,
        parent=cylinder,
        child=piston,
        origin=Origin(xyz=(body_len - 0.012, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=400.0, velocity=0.2, lower=-0.010, upper=0.014),
        meta={"mechanism": "gas-spring stroke"},
    )
    seat = (reach * 0.90, 0.0, 0.046)
    _add_seat_pad(
        arm, mats, name=f"{prefix}__arm__head_seat_pad", point=seat,
        pitch=_ARM_REST_PITCH[candidate],
    )
    return _seat(arm, seat, _ARM_REST_PITCH[candidate])


def _support_linkage_linear_rail_build(model, r, mats):
    candidate = "linear_rail"
    prefix = f"support_linkage__{candidate}"
    reach = r.arm_reach_m
    arm_reach = reach * 0.74
    arm = _add_rising_arm(model, r, mats, candidate=candidate, reach=arm_reach)
    _add_grip_controls(
        model, r, mats, grip_part=arm, prefix=prefix,
        trigger_x=arm_reach * 0.25, release_x=arm_reach * 0.44, body_z=-0.008,
        half_depth=r.arm_hy_m,
    )
    rail_len = arm_reach * 0.62
    rail_x = arm_reach * 0.58
    for index, sign in enumerate((-1.0, 1.0)):
        arm.visual(
            Box((rail_len, 0.007, 0.010)),
            origin=Origin(xyz=(rail_x, sign * (r.arm_hy_m - 0.004), 0.024)),
            material=mats["steel"],
            name=f"{prefix}__arm__slide_rail_{index}", material_class_id="metal.stainless_matte",
        )

    carriage = model.part(
        f"{prefix}__carriage", meta={"role": "support_link", "candidate": candidate}
    )
    carriage.visual(
        Box((0.062, 2.0 * (r.arm_hy_m + 0.001), 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.036)),
        material=mats["polymer"],
        name=f"{prefix}__carriage__body", material_class_id="plastic.opaque_glossy_molded",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        carriage.visual(
            Box((0.058, 0.008, 0.030)),
            origin=Origin(xyz=(0.0, sign * (r.arm_hy_m + 0.0035), 0.026)),
            material=mats["dark"],
            name=f"{prefix}__carriage__shoe_{index}", material_class_id="metal.blackened_gunmetal",
        )
    travel = max(0.014, rail_len * 0.5 - 0.036)
    model.articulation(
        f"{prefix}__carriage_slide",
        ArticulationType.PRISMATIC,
        parent=arm,
        child=carriage,
        origin=Origin(xyz=(rail_x, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=90.0, velocity=0.2, lower=-travel, upper=travel),
        meta={"mechanism": "reach carriage on the arm rail"},
    )
    seat = (0.0, 0.0, 0.056)
    _add_seat_pad(
        carriage, mats, name=f"{prefix}__carriage__head_seat_pad", point=seat,
        pitch=_ARM_REST_PITCH[candidate],
    )
    return _seat(carriage, seat, _ARM_REST_PITCH[candidate])


def _support_linkage_parallel_linkage_build(model, r, mats):
    candidate = "parallel_linkage"
    prefix = f"support_linkage__{candidate}"
    reach = r.arm_reach_m
    link_len = reach * 0.84
    depth = 2.0 * r.arm_hy_m - 0.012
    half_depth = 0.5 * depth

    upper = model.part(
        f"{prefix}__upper_link", meta={"role": "support_arm", "candidate": candidate}
    )
    upper.visual(
        mesh_from_cadquery(
            _link_bar_shape(link_len, 0.026, depth, end_bore=0.0112),
            f"{prefix}__upper_bar",
            tolerance=0.0007,
        ),
        material=mats["polymer"],
        name=f"{prefix}__upper_link__bar", material_class_id="plastic.opaque_glossy_molded",
    )
    upper.visual(
        Cylinder(radius=0.0148, length=r.barrel_len_m),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__upper_link__barrel", material_class_id="metal.blackened_gunmetal",
    )
    upper_mate = _elbow_axis_mate(r, prefix=f"{prefix}.upper", bore_radius=0.0148)
    upper_joint = f"{prefix}__upper_link_pitch"
    model.articulation(
        upper_joint,
        ArticulationType.REVOLUTE,
        parent=_support_host(model, r),
        child=upper,
        origin=upper_mate.origin,
        axis=upper_mate.axis,
        motion_limits=MotionLimits(effort=140.0, velocity=1.2, lower=-0.22, upper=0.30),
        meta={"mechanism": "upper parallel bar"},
    )
    register_interface_mate(model, upper_joint, upper_mate)
    _add_grip_controls(
        model, r, mats, grip_part=upper, prefix=prefix,
        trigger_x=link_len * 0.88, release_x=link_len * 0.78, body_z=-0.002,
        half_depth=half_depth,
    )

    # The lower bar is a source-faithful free parallel member: it is pinned to a
    # forked frame gusset well forward of the guided jaw and stops short of the
    # carriage so nothing shares a volume with the grip controls.
    lower_len = link_len * 0.66
    lower_x = r.elbow_x_m + 0.016
    lower_z = r.elbow_z_m - 0.038
    host = _support_host(model, r)
    for index, sign in enumerate((-1.0, 1.0)):
        host.visual(
            Box((0.028, 0.008, 0.044)),
            origin=Origin(
                xyz=_host_point(
                    r, lower_x, sign * (r.clevis_y_m - 0.0065), r.elbow_z_m - 0.026
                )
            ),
            material=mats["powder"],
            name=f"{host.name}__lower_link_cheek_{index}", material_class_id="metal.paint_coated",
        )
    lower = model.part(
        f"{prefix}__lower_link", meta={"role": "support_link", "candidate": candidate}
    )
    lower.visual(
        mesh_from_cadquery(
            _link_bar_shape(lower_len, 0.020, depth * 0.72),
            f"{prefix}__lower_bar",
            tolerance=0.0007,
        ),
        material=mats["dark"],
        name=f"{prefix}__lower_link__bar", material_class_id="metal.blackened_gunmetal",
    )
    lower.visual(
        Cylinder(radius=0.0088, length=2.0 * (r.clevis_y_m - 0.0105) - 0.0008),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__lower_link__barrel", material_class_id="metal.stainless_matte",
    )
    lower_provider = AxisInterface(
        name="clamp.lower_link_seat",
        point=_host_point(r, lower_x, 0.0, lower_z),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0090,
    )
    lower_consumer = AxisInterface(
        name=f"{prefix}.lower_bore",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0088,
    )
    lower_mate = mate_axes(lower_provider, lower_consumer, spin=_REST_PITCH)
    lower_joint = f"{prefix}__lower_link_pitch"
    model.articulation(
        lower_joint,
        ArticulationType.REVOLUTE,
        parent=host,
        child=lower,
        origin=lower_mate.origin,
        axis=lower_mate.axis,
        motion_limits=MotionLimits(effort=140.0, velocity=1.2, lower=-0.22, upper=0.30),
        mimic=Mimic(joint=upper_joint, multiplier=1.0, offset=0.0),
        meta={"mechanism": "lower parallel bar driven by the upper bar"},
    )
    register_interface_mate(model, lower_joint, lower_mate)

    carriage = model.part(
        f"{prefix}__carriage", meta={"role": "support_link", "candidate": candidate}
    )
    carriage.visual(
        Box((0.030, depth + 0.016, 0.034)),
        origin=Origin(xyz=(0.0, 0.0, 0.031)),
        material=mats["polymer"],
        name=f"{prefix}__carriage__body", material_class_id="plastic.opaque_glossy_molded",
    )
    carriage.visual(
        Cylinder(radius=0.0105, length=depth + 0.014),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__carriage__knuckle", material_class_id="metal.blackened_gunmetal",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        carriage.visual(
            Box((0.024, 0.006, 0.032)),
            origin=Origin(xyz=(0.0, sign * (0.5 * depth + 0.005), 0.015)),
            material=mats["dark"],
            name=f"{prefix}__carriage__cheek_{index}", material_class_id="metal.blackened_gunmetal",
        )
    carriage_provider = AxisInterface(
        name=f"{prefix}.carriage_seat",
        point=(link_len, 0.0, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0112,
    )
    carriage_consumer = AxisInterface(
        name=f"{prefix}.carriage_bore",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0105,
    )
    carriage_mate = mate_axes(carriage_provider, carriage_consumer, spin=-_REST_PITCH)
    carriage_joint = f"{prefix}__carriage_level"
    model.articulation(
        carriage_joint,
        ArticulationType.REVOLUTE,
        parent=upper,
        child=carriage,
        origin=carriage_mate.origin,
        axis=carriage_mate.axis,
        motion_limits=MotionLimits(effort=90.0, velocity=1.2, lower=-0.24, upper=0.24),
        meta={"mechanism": "self-levelling linkage carriage"},
    )
    register_interface_mate(model, carriage_joint, carriage_mate)
    seat = (0.0, 0.0, 0.052)
    _add_seat_pad(
        carriage, mats, name=f"{prefix}__carriage__head_seat_pad", point=seat, pitch=0.0
    )
    return _seat(carriage, seat, 0.0)


def _support_linkage_rotary_column_build(model, r, mats):
    candidate = "rotary_column"
    prefix = f"support_linkage__{candidate}"
    reach = r.arm_reach_m
    column_h = 0.118
    depth = 2.0 * r.arm_hy_m - 0.006

    column = model.part(
        f"{prefix}__column", meta={"role": "support_arm", "candidate": candidate}
    )
    column.visual(
        mesh_from_cadquery(
            _column_post_shape(column_h), f"{prefix}__column_post", tolerance=0.0007
        ),
        material=mats["powder"],
        name=f"{prefix}__column__post", material_class_id="metal.paint_coated",
    )
    host = _support_host(model, r)
    provider = AxisInterface(
        name="clamp.column_socket",
        point=_host_point(r, r.elbow_x_m, 0.0, r.jaw_z_m + r.travel_up_m + 0.051),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0230,
    )
    consumer = AxisInterface(
        name=f"{prefix}.column_spigot",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0230,
    )
    mate = mate_axes(provider, consumer)
    joint = f"{prefix}__column_rotate"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=host,
        child=column,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=60.0, velocity=1.6, lower=-1.10, upper=1.10),
        meta={"mechanism": "vertical column yaw"},
    )
    register_interface_mate(model, joint, mate)

    collar = model.part(
        f"{prefix}__collar", meta={"role": "support_link", "candidate": candidate}
    )
    collar.visual(
        mesh_from_cadquery(_sliding_collar_shape(), f"{prefix}__collar_body", tolerance=0.0006),
        material=mats["dark"],
        name=f"{prefix}__collar__body", material_class_id="metal.blackened_gunmetal",
    )
    collar_mid = column_h * 0.58
    collar_travel = column_h * 0.20
    model.articulation(
        f"{prefix}__collar_slide",
        ArticulationType.PRISMATIC,
        parent=column,
        child=collar,
        origin=Origin(xyz=(0.0, 0.0, collar_mid)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=200.0, velocity=0.2, lower=-collar_travel, upper=collar_travel
        ),
        meta={"mechanism": "height collar on the column"},
    )

    arm_len = reach * 0.78
    radial = model.part(
        f"{prefix}__radial_arm", meta={"role": "support_link", "candidate": candidate}
    )
    radial.visual(
        mesh_from_cadquery(
            _radial_arm_shape(arm_len, depth), f"{prefix}__radial_body", tolerance=0.0007
        ),
        material=mats["polymer"],
        name=f"{prefix}__radial_arm__body", material_class_id="plastic.opaque_glossy_molded",
    )
    radial.visual(
        Cylinder(radius=0.0122, length=0.026),
        origin=Origin(),
        material=mats["dark"],
        name=f"{prefix}__radial_arm__hub", material_class_id="metal.blackened_gunmetal",
    )
    radial_provider = AxisInterface(
        name=f"{prefix}.radial_seat",
        point=(0.0392, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0128,
    )
    radial_consumer = AxisInterface(
        name=f"{prefix}.radial_bore",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0125,
    )
    radial_mate = mate_axes(radial_provider, radial_consumer)
    radial_joint = f"{prefix}__arm_swing"
    model.articulation(
        radial_joint,
        ArticulationType.REVOLUTE,
        parent=collar,
        child=radial,
        origin=radial_mate.origin,
        axis=radial_mate.axis,
        motion_limits=MotionLimits(effort=70.0, velocity=1.4, lower=-0.90, upper=0.90),
        meta={"mechanism": "radial swing arm"},
    )
    register_interface_mate(model, radial_joint, radial_mate)
    _add_grip_controls(
        model, r, mats, grip_part=radial, prefix=prefix,
        trigger_x=arm_len * 0.42, release_x=arm_len * 0.60, body_z=-0.002,
        half_depth=0.5 * depth,
    )
    seat = (arm_len, 0.0, 0.026)
    _add_seat_pad(
        radial, mats, name=f"{prefix}__radial_arm__head_seat_pad", point=seat, pitch=0.0
    )
    return _seat(radial, seat, 0.0)


_SUPPORT_BUILDERS = {
    "plain_arm": _support_linkage_plain_arm_build,
    "ratchet_elbow": _support_linkage_ratchet_elbow_build,
    "gas_spring_arm": _support_linkage_gas_spring_arm_build,
    "linear_rail": _support_linkage_linear_rail_build,
    "parallel_linkage": _support_linkage_parallel_linkage_build,
    "rotary_column": _support_linkage_rotary_column_build,
}


# ---------------------------------------------------------------------------
# pad_head candidates
# ---------------------------------------------------------------------------


def _add_wrist(model, r, mats, seat: dict, *, candidate: str):
    """Vertical swivel collar and upright post shared by every head candidate."""

    prefix = f"pad_head__{candidate}"
    theta = seat["pitch"]
    point = seat["point"]
    wrist = model.part(
        f"{prefix}__wrist", meta={"role": "support_wrist", "candidate": candidate}
    )
    wrist.visual(
        Cylinder(radius=0.015, length=0.024),
        origin=Origin(xyz=(0.0, 0.0, 0.008)),
        material=mats["dark"],
        name=f"{prefix}__wrist__collar", material_class_id="metal.blackened_gunmetal",
    )
    post_h = r.post_height_m
    wrist.visual(
        Cylinder(radius=0.0105, length=post_h - 0.024),
        origin=Origin(xyz=(0.0, 0.0, 0.018 + 0.5 * (post_h - 0.024))),
        material=mats["powder"],
        name=f"{prefix}__wrist__upright_post", material_class_id="metal.paint_coated",
    )
    provider = AxisInterface(
        name=f"{prefix}.wrist_seat",
        point=point,
        axis=(math.sin(theta), 0.0, math.cos(theta)),
        radial=(math.cos(theta), 0.0, -math.sin(theta)),
        radius=0.0152,
    )
    consumer = AxisInterface(
        name=f"{prefix}.wrist_collar",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.015,
    )
    mate = mate_axes(provider, consumer)
    joint = f"{prefix}__wrist_swivel"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=seat["part"],
        child=wrist,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=25.0, velocity=1.5, lower=-0.60, upper=0.60),
        meta={"mechanism": "horizontal forearm-support swivel"},
    )
    register_interface_mate(model, joint, mate)
    return wrist, post_h


def _add_saddle_visuals(part, r, mats, *, prefix: str, local: str, length: float,
                        radius: float, pin_radius: float,
                        bolster_z: float = 0.046) -> None:
    width = min(r.pad_width_m, 2.0 * radius * 0.94)
    part.visual(
        Box((0.040, 0.030, 0.024)),
        origin=Origin(xyz=(0.0, 0.0, 0.011)),
        material=mats["dark"],
        name=f"{prefix}__{local}__mount", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=pin_radius, length=0.052),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__{local}__trunnion_pin", material_class_id="metal.stainless_matte",
    )
    part.visual(
        mesh_from_cadquery(
            _saddle_shell(radius, 0.008, length, width),
            f"{prefix}__{local}_shell",
            tolerance=0.0009,
        ),
        origin=Origin(xyz=(0.010, 0.0, 0.020)),
        material=mats["polymer"],
        name=f"{prefix}__{local}__saddle_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        mesh_from_cadquery(
            _saddle_shell(radius - 0.008, 0.006, length - 0.008, width - 0.010),
            f"{prefix}__{local}_liner",
            tolerance=0.0009,
        ),
        origin=Origin(xyz=(0.010, 0.0, 0.0204)),
        material=mats["liner"],
        name=f"{prefix}__{local}__saddle_liner", material_class_id="fabric.flexible_foam",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        part.visual(
            Box((0.024, width * 0.82, 0.018)),
            origin=Origin(
                xyz=(0.010 + sign * (0.5 * length - 0.013), 0.0, bolster_z),
                rpy=(0.0, sign * 0.18, 0.0),
            ),
            material=mats["liner"],
            name=f"{prefix}__{local}__bolster_{index}", material_class_id="fabric.flexible_foam",
        )


def _add_pad_fork(wrist, mats, *, prefix: str, post_h: float, half_gap: float,
                  bore_radius: float) -> None:
    wrist.visual(
        mesh_from_cadquery(
            _fork_cheeks_shape(
                half_gap=half_gap,
                cheek_t=0.007,
                cheek_w=0.026,
                cheek_top=0.005,
                bore_radius=bore_radius,
            ),
            f"{prefix}__wrist_fork",
            tolerance=0.0005,
        ),
        origin=Origin(xyz=(0.0, 0.0, post_h)),
        material=mats["dark"],
        name=f"{prefix}__wrist__pad_fork", material_class_id="metal.blackened_gunmetal",
    )


def _pad_head_tilt_saddle_build(model, r, mats, seat):
    candidate = "tilt_saddle"
    prefix = f"pad_head__{candidate}"
    wrist, post_h = _add_wrist(model, r, mats, seat, candidate=candidate)
    _add_pad_fork(wrist, mats, prefix=prefix, post_h=post_h, half_gap=0.022, bore_radius=0.0108)

    pad = model.part(f"{prefix}__pad", meta={"role": "forearm_rest", "candidate": candidate})
    _add_saddle_visuals(
        pad, r, mats, prefix=prefix, local="pad",
        length=r.pad_length_m, radius=r.pad_radius_m, pin_radius=0.0100,
    )
    provider = AxisInterface(
        name=f"{prefix}.pad_fork",
        point=(0.0, 0.0, post_h),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0108,
    )
    consumer = AxisInterface(
        name=f"{prefix}.pad_pin",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0100,
    )
    mate = mate_axes(provider, consumer)
    joint = f"{prefix}__pad_tilt"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=wrist,
        child=pad,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=35.0, velocity=1.2, lower=-0.30, upper=0.30),
        meta={"mechanism": "self-levelling concave support pad"},
    )
    register_interface_mate(model, joint, mate)
    return pad


def _pad_head_ball_socket_build(model, r, mats, seat):
    candidate = "ball_socket"
    prefix = f"pad_head__{candidate}"
    wrist, post_h = _add_wrist(model, r, mats, seat, candidate=candidate)
    _add_pad_fork(wrist, mats, prefix=prefix, post_h=post_h, half_gap=0.020, bore_radius=0.0098)

    gimbal = model.part(
        f"{prefix}__gimbal", meta={"role": "pad_gimbal", "candidate": candidate}
    )
    gimbal.visual(
        Cylinder(radius=0.0090, length=0.048),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__gimbal__pitch_pin", material_class_id="metal.stainless_matte",
    )
    gimbal.visual(
        Sphere(radius=0.0145),
        origin=Origin(xyz=(0.0, 0.0, 0.008)),
        material=mats["dark"],
        name=f"{prefix}__gimbal__ball", material_class_id="metal.blackened_gunmetal",
    )
    gimbal.visual(
        mesh_from_cadquery(
            _fork_cheeks_shape(
                half_gap=0.019,
                cheek_t=0.007,
                cheek_w=0.024,
                cheek_top=0.005,
                bore_radius=0.0098,
                axis="x",
            ),
            f"{prefix}__gimbal_fork",
            tolerance=0.0005,
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.026)),
        material=mats["dark"],
        name=f"{prefix}__gimbal__roll_fork", material_class_id="metal.blackened_gunmetal",
    )
    pitch_provider = AxisInterface(
        name=f"{prefix}.pitch_fork",
        point=(0.0, 0.0, post_h),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0098,
    )
    pitch_consumer = AxisInterface(
        name=f"{prefix}.pitch_pin",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0090,
    )
    pitch_mate = mate_axes(pitch_provider, pitch_consumer)
    pitch_joint = f"{prefix}__pad_ball_pitch"
    model.articulation(
        pitch_joint,
        ArticulationType.REVOLUTE,
        parent=wrist,
        child=gimbal,
        origin=pitch_mate.origin,
        axis=pitch_mate.axis,
        motion_limits=MotionLimits(effort=30.0, velocity=1.2, lower=-0.26, upper=0.26),
        meta={"mechanism": "ball-socket pitch axis"},
    )
    register_interface_mate(model, pitch_joint, pitch_mate)

    pad = model.part(f"{prefix}__pad", meta={"role": "forearm_rest", "candidate": candidate})
    pad.visual(
        Cylinder(radius=0.0090, length=0.046),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__pad__roll_pin", material_class_id="metal.stainless_matte",
    )
    pad.visual(
        Box((0.040, 0.030, 0.024)),
        origin=Origin(xyz=(0.0, 0.0, 0.011)),
        material=mats["dark"],
        name=f"{prefix}__pad__mount", material_class_id="metal.blackened_gunmetal",
    )
    width = min(r.pad_width_m, 2.0 * r.pad_radius_m * 0.94)
    pad.visual(
        mesh_from_cadquery(
            _saddle_shell(
                r.pad_radius_m * 1.34, 0.008, r.pad_length_m * 0.86, width * 1.06,
                depth_ratio=0.62,
            ),
            f"{prefix}__pad_shell",
            tolerance=0.0009,
        ),
        origin=Origin(xyz=(0.010, 0.0, 0.020)),
        material=mats["polymer"],
        name=f"{prefix}__pad__saddle_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    pad.visual(
        mesh_from_cadquery(
            _saddle_shell(
                r.pad_radius_m * 1.34 - 0.008, 0.006, r.pad_length_m * 0.86 - 0.008,
                width * 1.06 - 0.010, depth_ratio=0.62,
            ),
            f"{prefix}__pad_liner",
            tolerance=0.0009,
        ),
        origin=Origin(xyz=(0.010, 0.0, 0.0204)),
        material=mats["liner"],
        name=f"{prefix}__pad__saddle_liner", material_class_id="fabric.flexible_foam",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        pad.visual(
            Box((0.024, width * 0.82, 0.018)),
            origin=Origin(
                xyz=(0.010 + sign * (0.5 * r.pad_length_m - 0.013), 0.0, 0.0338),
                rpy=(0.0, sign * 0.18, 0.0),
            ),
            material=mats["liner"],
            name=f"{prefix}__pad__bolster_{index}", material_class_id="fabric.flexible_foam",
        )
    roll_provider = AxisInterface(
        name=f"{prefix}.roll_fork",
        point=(0.0, 0.0, 0.026),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0098,
    )
    roll_consumer = AxisInterface(
        name=f"{prefix}.roll_pin",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0090,
    )
    roll_mate = mate_axes(roll_provider, roll_consumer)
    roll_joint = f"{prefix}__pad_ball_roll"
    model.articulation(
        roll_joint,
        ArticulationType.REVOLUTE,
        parent=gimbal,
        child=pad,
        origin=roll_mate.origin,
        axis=roll_mate.axis,
        motion_limits=MotionLimits(effort=30.0, velocity=1.2, lower=-0.22, upper=0.22),
        meta={"mechanism": "ball-socket roll axis"},
    )
    register_interface_mate(model, roll_joint, roll_mate)
    return pad


def _pad_head_split_pad_build(model, r, mats, seat):
    candidate = "split_pad"
    prefix = f"pad_head__{candidate}"
    wrist, post_h = _add_wrist(model, r, mats, seat, candidate=candidate)
    _add_pad_fork(wrist, mats, prefix=prefix, post_h=post_h, half_gap=0.022, bore_radius=0.0108)

    yoke = model.part(f"{prefix}__yoke", meta={"role": "pad_yoke", "candidate": candidate})
    yoke.visual(
        Cylinder(radius=0.0100, length=0.052),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__yoke__trunnion_pin", material_class_id="metal.stainless_matte",
    )
    arm_len = r.pad_length_m * 0.30
    yoke.visual(
        Box((arm_len * 2.0, 0.028, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.010)),
        material=mats["dark"],
        name=f"{prefix}__yoke__beam", material_class_id="metal.blackened_gunmetal",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        yoke.visual(
            mesh_from_cadquery(
                _fork_cheeks_shape(
                    half_gap=0.019,
                    cheek_t=0.006,
                    cheek_w=0.022,
                    cheek_top=0.005,
                    bore_radius=0.0092,
                ),
                f"{prefix}__yoke_fork_{index}",
                tolerance=0.0005,
            ),
            origin=Origin(xyz=(sign * arm_len, 0.0, 0.022)),
            material=mats["dark"],
            name=f"{prefix}__yoke__fork_{index}", material_class_id="metal.blackened_gunmetal",
        )
    yoke_provider = AxisInterface(
        name=f"{prefix}.yoke_fork",
        point=(0.0, 0.0, post_h),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0108,
    )
    yoke_consumer = AxisInterface(
        name=f"{prefix}.yoke_pin",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0100,
    )
    yoke_mate = mate_axes(yoke_provider, yoke_consumer)
    yoke_joint = f"{prefix}__yoke_tilt"
    model.articulation(
        yoke_joint,
        ArticulationType.REVOLUTE,
        parent=wrist,
        child=yoke,
        origin=yoke_mate.origin,
        axis=yoke_mate.axis,
        motion_limits=MotionLimits(effort=35.0, velocity=1.2, lower=-0.24, upper=0.24),
        meta={"mechanism": "split-pad yoke tilt"},
    )
    register_interface_mate(model, yoke_joint, yoke_mate)

    specs = (
        ("pad", 1.0, r.pad_length_m * 0.56, r.pad_radius_m, "forearm_rest"),
        ("wrist_pad", -1.0, r.pad_length_m * 0.30, r.pad_radius_m * 0.80, "wrist_rest"),
    )
    pads = []
    for local, sign, length, radius, role in specs:
        part = model.part(f"{prefix}__{local}", meta={"role": role, "candidate": candidate})
        width = min(r.pad_width_m, 2.0 * radius * 0.94)
        part.visual(
            Cylinder(radius=0.0092, length=0.044),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["steel"],
            name=f"{prefix}__{local}__trunnion_pin", material_class_id="metal.stainless_matte",
        )
        part.visual(
            Box((0.032, 0.026, 0.024)),
            origin=Origin(xyz=(0.0, 0.0, 0.011)),
            material=mats["dark"],
            name=f"{prefix}__{local}__mount", material_class_id="metal.blackened_gunmetal",
        )
        part.visual(
            mesh_from_cadquery(
                _saddle_shell(radius, 0.008, length, width, taper=0.66),
                f"{prefix}__{local}_shell",
                tolerance=0.0009,
            ),
            origin=Origin(xyz=(0.0, 0.0, 0.020)),
            material=mats["polymer"],
            name=f"{prefix}__{local}__saddle_shell", material_class_id="plastic.opaque_glossy_molded",
        )
        part.visual(
            mesh_from_cadquery(
                _saddle_shell(
                    radius - 0.008, 0.006, length - 0.008, width - 0.010, taper=0.66
                ),
                f"{prefix}__{local}_liner",
                tolerance=0.0009,
            ),
            origin=Origin(xyz=(0.0, 0.0, 0.0204)),
            material=mats["liner"],
            name=f"{prefix}__{local}__saddle_liner", material_class_id="fabric.flexible_foam",
        )
        provider = AxisInterface(
            name=f"{prefix}.{local}_fork",
            point=(sign * arm_len, 0.0, 0.022),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            radius=0.0092,
        )
        consumer = AxisInterface(
            name=f"{prefix}.{local}_pin",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            radius=0.0092,
        )
        mate = mate_axes(provider, consumer)
        joint = f"{prefix}__{local}_tilt"
        model.articulation(
            joint,
            ArticulationType.REVOLUTE,
            parent=yoke,
            child=part,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(effort=30.0, velocity=1.2, lower=-0.24, upper=0.24),
            meta={"mechanism": f"{local} tilt"},
        )
        register_interface_mate(model, joint, mate)
        pads.append(part)
    return pads[0]


def _cradle_shell(radius: float, length: float, width: float,
                  wall: float) -> cq.Workplane:
    """Deep U-section forearm cradle with raised side bolsters.

    deep_cradle_pad fork L103-L137: a continuous U channel whose outer walls
    rise well above the curved floor, instead of the shallow open saddle trough.
    """

    half_l = 0.5 * length
    hw = 0.5 * width
    lip = hw * 1.05
    depth = 0.36 * radius
    top = 0.56 * radius
    outer = (
        cq.Workplane("YZ")
        .moveTo(-hw, top)
        .lineTo(-lip, 0.10 * top)
        .threePointArc((-0.66 * lip, -0.78 * depth), (0.0, -depth))
        .threePointArc((0.66 * lip, -0.78 * depth), (lip, 0.10 * top))
        .lineTo(hw, top)
        .close()
        .extrude(half_l, both=True)
    )
    cavity = (
        cq.Workplane("YZ")
        .moveTo(-(hw - wall), top + 0.006)
        .lineTo(-(lip - wall), 0.10 * top + wall)
        .threePointArc(
            (-0.66 * (lip - wall), -0.78 * depth + wall), (0.0, -depth + wall)
        )
        .threePointArc(
            (0.66 * (lip - wall), -0.78 * depth + wall), (lip - wall, 0.10 * top + wall)
        )
        .lineTo(hw - wall, top + 0.006)
        .close()
        .extrude(half_l + 0.002, both=True)
    )
    return outer.cut(cavity)


def _pad_head_deep_cradle_build(model, r, mats, seat):
    """deep_cradle_pad fork: the shallow saddle becomes a deep contoured cradle."""

    candidate = "deep_cradle"
    prefix = f"pad_head__{candidate}"
    wrist, post_h = _add_wrist(model, r, mats, seat, candidate=candidate)
    _add_pad_fork(wrist, mats, prefix=prefix, post_h=post_h, half_gap=0.022, bore_radius=0.0108)

    pad = model.part(f"{prefix}__pad", meta={"role": "forearm_rest", "candidate": candidate})
    pad.visual(
        Box((0.040, 0.030, 0.024)),
        origin=Origin(xyz=(0.0, 0.0, 0.011)),
        material=mats["dark"],
        name=f"{prefix}__pad__mount", material_class_id="metal.blackened_gunmetal",
    )
    pad.visual(
        Cylinder(radius=0.0100, length=0.052),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__pad__trunnion_pin", material_class_id="metal.stainless_matte",
    )
    width = min(r.pad_width_m, 2.0 * r.pad_radius_m * 0.94)
    wall = max(0.005, 0.11 * r.pad_radius_m)
    depth = 0.36 * r.pad_radius_m
    floor_z = 0.020 + depth
    pad.visual(
        mesh_from_cadquery(
            _cradle_shell(r.pad_radius_m, r.pad_length_m, width, wall),
            f"{prefix}__cradle_shell",
            tolerance=0.0009,
        ),
        origin=Origin(xyz=(0.010, 0.0, floor_z)),
        material=mats["polymer"],
        name=f"{prefix}__pad__cradle_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    pad.visual(
        mesh_from_cadquery(
            _cradle_shell(
                r.pad_radius_m - wall,
                r.pad_length_m - 0.012,
                width - 2.0 * wall,
                max(0.004, 0.6 * wall),
            ),
            f"{prefix}__cradle_liner",
            tolerance=0.0009,
        ),
        origin=Origin(xyz=(0.010, 0.0, floor_z + 0.4 * wall)),
        material=mats["liner"],
        name=f"{prefix}__pad__cradle_liner", material_class_id="fabric.flexible_foam",
    )
    # Fore and aft end walls close the open channel and tie shell and liner
    # into one connected body, exactly as the fork builds them.
    half_len = 0.5 * r.pad_length_m
    for index, sign in enumerate((-1.0, 1.0)):
        pad.visual(
            Box((0.014, width * 0.90, 0.56 * r.pad_radius_m + depth)),
            origin=Origin(
                xyz=(
                    0.010 + sign * (half_len - 0.008),
                    0.0,
                    floor_z + 0.5 * (0.56 * r.pad_radius_m - depth),
                )
            ),
            material=mats["polymer"],
            name=f"{prefix}__pad__end_wall_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    provider = AxisInterface(
        name=f"{prefix}.pad_fork",
        point=(0.0, 0.0, post_h),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0108,
    )
    consumer = AxisInterface(
        name=f"{prefix}.pad_pin",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0100,
    )
    mate = mate_axes(provider, consumer)
    joint = f"{prefix}__pad_tilt"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=wrist,
        child=pad,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=35.0, velocity=1.2, lower=-0.28, upper=0.28),
        meta={"mechanism": "deep contoured forearm cradle"},
    )
    register_interface_mate(model, joint, mate)
    return pad


def _pad_head_quick_release_build(model, r, mats, seat):
    """quick_release_pad fork L619-L716: dovetail carriage plus cam lock."""

    candidate = "quick_release"
    prefix = f"pad_head__{candidate}"
    wrist, post_h = _add_wrist(model, r, mats, seat, candidate=candidate)
    plate_z = post_h - 0.008
    wrist.visual(
        Box((0.044, 0.084, 0.010)),
        origin=Origin(xyz=(0.0, 0.014, plate_z)),
        material=mats["dark"],
        name=f"{prefix}__wrist__dovetail_plate", material_class_id="metal.blackened_gunmetal",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        # The rails run along the insertion direction, so the carriage keeps the
        # same section engaged at every point of its travel.
        wrist.visual(
            Box((0.007, 0.084, 0.007)),
            origin=Origin(xyz=(sign * 0.0185, 0.014, plate_z + 0.0085)),
            material=mats["steel"],
            name=f"{prefix}__wrist__dovetail_rail_{index}", material_class_id="metal.stainless_matte",
        )

    carriage = model.part(
        f"{prefix}__carriage", meta={"role": "pad_carriage", "candidate": candidate}
    )
    carriage.visual(
        Box((0.052, 0.040, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__carriage__body", material_class_id="metal.blackened_gunmetal",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        carriage.visual(
            Box((0.008, 0.040, 0.022)),
            origin=Origin(xyz=(sign * 0.0265, 0.0, -0.008)),
            material=mats["dark"],
            name=f"{prefix}__carriage__groove_lip_{index}", material_class_id="metal.blackened_gunmetal",
        )
    carriage.visual(
        mesh_from_cadquery(
            _fork_cheeks_shape(
                half_gap=0.014,
                cheek_t=0.006,
                cheek_w=0.026,
                cheek_top=0.005,
                bore_radius=0.0108,
            ),
            f"{prefix}__carriage_fork",
            tolerance=0.0005,
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.018)),
        material=mats["dark"],
        name=f"{prefix}__carriage__pad_fork", material_class_id="metal.blackened_gunmetal",
    )
    carriage.visual(
        Box((0.008, 0.038, 0.012)),
        origin=Origin(xyz=(-0.018, 0.0, 0.008)),
        material=mats["dark"],
        name=f"{prefix}__carriage__stop_rib", material_class_id="metal.blackened_gunmetal",
    )
    carriage.visual(
        Cylinder(radius=0.005, length=0.010),
        origin=Origin(xyz=(0.018, 0.0, 0.008), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__carriage__cam_boss", material_class_id="metal.blackened_gunmetal",
    )
    slide_joint = f"{prefix}__dovetail_slide"
    model.articulation(
        slide_joint,
        ArticulationType.PRISMATIC,
        parent=wrist,
        child=carriage,
        origin=Origin(xyz=(0.0, 0.0, plate_z + 0.018)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=40.0, velocity=0.15, lower=0.0, upper=0.028),
        meta={"mechanism": "quick-release dovetail insertion slide"},
    )

    cam = model.part(
        f"{prefix}__cam_lock", meta={"role": "pad_cam_lock", "candidate": candidate}
    )
    cam.visual(
        Cylinder(radius=0.0040, length=0.012),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__cam_lock__shaft", material_class_id="metal.stainless_matte",
    )
    cam.visual(
        Box((0.010, 0.007, 0.014)),
        origin=Origin(xyz=(0.005, 0.0, 0.0)),
        material=mats["polymer"],
        name=f"{prefix}__cam_lock__lobe", material_class_id="plastic.opaque_glossy_molded",
    )
    cam.visual(
        Box((0.020, 0.006, 0.006)),
        origin=Origin(xyz=(0.018, 0.0, 0.0)),
        material=mats["rubber"],
        name=f"{prefix}__cam_lock__lever_tip", material_class_id="rubber.smooth_plain",
    )
    cam_provider = AxisInterface(
        name=f"{prefix}.cam_boss",
        point=(0.018, 0.0, 0.008),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.005,
    )
    cam_consumer = AxisInterface(
        name=f"{prefix}.cam_shaft",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0040,
    )
    cam_mate = mate_axes(cam_provider, cam_consumer)
    cam_joint = f"{prefix}__cam_lock_flick"
    model.articulation(
        cam_joint,
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=cam,
        origin=cam_mate.origin,
        axis=cam_mate.axis,
        motion_limits=MotionLimits(effort=3.0, velocity=5.0, lower=-0.45, upper=0.45),
        meta={"mechanism": "dovetail cam-lock lever"},
    )
    register_interface_mate(model, cam_joint, cam_mate)

    pad = model.part(f"{prefix}__pad", meta={"role": "forearm_rest", "candidate": candidate})
    _add_saddle_visuals(
        pad, r, mats, prefix=prefix, local="pad",
        length=r.pad_length_m, radius=r.pad_radius_m, pin_radius=0.0100,
    )
    pad_provider = AxisInterface(
        name=f"{prefix}.carriage_trunnion",
        point=(0.0, 0.0, 0.018),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0100,
    )
    pad_consumer = AxisInterface(
        name=f"{prefix}.pad_pin",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0100,
    )
    pad_mate = mate_axes(pad_provider, pad_consumer)
    pad_joint = f"{prefix}__pad_tilt"
    model.articulation(
        pad_joint,
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=pad,
        origin=pad_mate.origin,
        axis=pad_mate.axis,
        motion_limits=MotionLimits(effort=35.0, velocity=1.2, lower=-0.26, upper=0.26),
        meta={"mechanism": "removable pad on the release carriage"},
    )
    register_interface_mate(model, pad_joint, pad_mate)
    return pad


_PAD_BUILDERS = {
    "tilt_saddle": _pad_head_tilt_saddle_build,
    "ball_socket": _pad_head_ball_socket_build,
    "split_pad": _pad_head_split_pad_build,
    "deep_cradle": _pad_head_deep_cradle_build,
    "quick_release": _pad_head_quick_release_build,
}


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


def build_picturex_0611_ergonomic_clamp_with_adjustable(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model)
    frame = _build_clamp(model, r, mats)
    _CLAMP_ACTUATION_BUILDERS[r.clamp_actuation](model, r, mats, frame)
    seat = _SUPPORT_BUILDERS[r.support_linkage](model, r, mats)
    _PAD_BUILDERS[r.pad_head](model, r, mats, seat)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["source_family"] = "pictureX/0611/ergonomic_clamp_with_adjustable"
    return model


def build_seeded_picturex_0611_ergonomic_clamp_with_adjustable(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_picturex_0611_ergonomic_clamp_with_adjustable(
        config_from_seed(seed), assets=assets
    )


def _centre(box):
    if box is None:
        return None
    return tuple(0.5 * (box[0][i] + box[1][i]) for i in range(3))


def _elem_box(ctx, part, elem):
    """World AABB of one primitive visual; mesh visuals are deliberately avoided
    so the same author tests run under mesh-free preflight and under sweep."""

    return ctx.part_element_world_aabb(part, elem=elem)


def run_picturex_0611_ergonomic_clamp_with_adjustable_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()

    roles: dict[str | None, list] = {}
    for part in object_model.parts:
        roles.setdefault(part.meta.get("role"), []).append(part)

    if r.clamp_actuation == "screw_spindle":
        actuation_ok = (
            len(roles.get("clamp_screw", [])) == 1
            and not roles.get("clamp_cam_lever")
            and not roles.get("clamp_follower")
        )
    else:
        actuation_ok = (
            len(roles.get("clamp_cam_lever", [])) == 1
            and len(roles.get("clamp_follower", [])) == 1
            and not roles.get("clamp_screw")
        )
    ctx.check(
        "clamp keeps the source screw clamp inventory",
        len(roles.get("clamp_frame", [])) == 1
        and len(roles.get("clamp_jaw", [])) == 1
        and len(roles.get("clamp_shoe", [])) == 1
        and actuation_ok,
        details=f"roles={sorted(str(k) for k in roles)}, actuation={r.clamp_actuation}",
    )
    ctx.check(
        "domain choices are recorded",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )

    frame = object_model.get_part("clamp__frame")
    jaw = object_model.get_part("clamp__movable_jaw")
    shoe = object_model.get_part("clamp__pressure_pad")
    jaw_slide = object_model.get_articulation("clamp__jaw_slide")

    def throat_gap() -> float | None:
        top = _elem_box(ctx, frame, "clamp__frame__fixed_jaw_pad")
        bottom = _elem_box(ctx, shoe, "clamp__pressure_pad__face")
        if top is None or bottom is None:
            return None
        return top[0][2] - bottom[1][2]

    rest_gap = throat_gap()
    with ctx.pose({jaw_slide: r.travel_up_m}):
        closed_gap = throat_gap()
    ctx.check(
        "clamp throat opens and closes on the source screw axis",
        rest_gap is not None
        and closed_gap is not None
        and abs(rest_gap - r.throat_gap_m) < 0.005
        and 0.003 < closed_gap < 0.014
        and closed_gap < rest_gap - 0.020,
        details=f"rest_gap={rest_gap}, closed_gap={closed_gap}, target={r.throat_gap_m}",
    )

    block = _elem_box(ctx, jaw, "clamp__movable_jaw__guide_block")
    rail = _elem_box(ctx, frame, "clamp__frame__guide_rail_0")
    ctx.check(
        "guided jaw keeps real engagement with the frame rails",
        block is not None
        and rail is not None
        and min(block[1][2], rail[1][2]) - max(block[0][2], rail[0][2]) > 0.015
        and block[0][1] >= rail[1][1] - 1e-6,
        details=f"block={block}, rail={rail}",
    )

    support_parts = roles.get("support_arm", [])
    ctx.check(
        "one source-backed support structure carries the head",
        len(support_parts) == 1
        and support_parts[0].meta.get("candidate") == r.support_linkage,
        details=f"support={[part.name for part in support_parts]}",
    )

    carriage_parts = roles.get("reach_carriage", [])
    ctx.check(
        "reach interface matches the selected base",
        len(carriage_parts) == (1 if r.base_reach == "edge_track" else 0),
        details=f"base_reach={r.base_reach}, carriages={[p.name for p in carriage_parts]}",
    )
    if r.base_reach == "edge_track":
        slide = object_model.get_articulation("base_reach__edge_track__carriage_slide")
        rest_arm = _centre(ctx.part_world_aabb(support_parts[0]))
        with ctx.pose({slide: slide.motion_limits.upper}):
            slid_arm = _centre(ctx.part_world_aabb(support_parts[0]))
        ctx.check(
            "edge-track carriage really moves the support base along the desk edge",
            rest_arm is not None
            and slid_arm is not None
            and abs(slid_arm[1] - rest_arm[1] - r.track_stroke_m) < 0.002
            and abs(slid_arm[2] - rest_arm[2]) < 0.002,
            details=f"rest={rest_arm}, slid={slid_arm}, stroke={r.track_stroke_m}",
        )

    wrist_parts = roles.get("support_wrist", [])
    rest_parts = roles.get("forearm_rest", [])
    ctx.check(
        "forearm rest is a concave saddle above the support",
        len(wrist_parts) == 1 and len(rest_parts) == 1,
        details=f"wrist={len(wrist_parts)}, rest={len(rest_parts)}",
    )
    pad = rest_parts[0] if rest_parts else None
    pad_aabb = ctx.part_world_aabb(pad) if pad is not None else None
    pad_size = (
        None if pad_aabb is None else tuple(pad_aabb[1][i] - pad_aabb[0][i] for i in range(3))
    )
    expected_len = r.pad_length_m if r.pad_head != "split_pad" else r.pad_length_m * 0.56
    ctx.check(
        "forearm rest keeps the source trough footprint",
        pad_size is not None
        and pad_size[0] > expected_len * 0.70
        and pad_size[1] > 2.0 * r.pad_radius_m * 0.50,
        details=f"pad_size={pad_size}, expected_len={expected_len}",
    )
    if pad is not None:
        ctx.expect_origin_gap(
            pad,
            frame,
            axis="z",
            min_gap=0.08,
            name="support holds the rest above the clamp head",
        )

    for joint in object_model.articulations:
        if joint.articulation_type is ArticulationType.REVOLUTE:
            limits = joint.motion_limits
            ctx.check(
                f"{joint.name} keeps a real bounded range",
                limits is not None
                and limits.lower is not None
                and limits.upper is not None
                and limits.upper > limits.lower,
                details=f"limits={limits}",
            )

    swivel = object_model.get_articulation(f"pad_head__{r.pad_head}__wrist_swivel")
    rest_pad = _centre(ctx.part_world_aabb(pad)) if pad is not None else None
    with ctx.pose({swivel: swivel.motion_limits.upper}):
        swung_pad = _centre(ctx.part_world_aabb(pad)) if pad is not None else None
    ctx.check(
        "wrist swivel turns the rest about a vertical axis",
        rest_pad is not None
        and swung_pad is not None
        and abs(swung_pad[1] - rest_pad[1]) > 0.004
        and abs(swung_pad[2] - rest_pad[2]) < 0.025,
        details=f"rest={rest_pad}, swung={swung_pad}",
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "smallest_clamp_and_shortest_reach",
        {
            "clamp_span_m": 0.072,
            "frame_depth_m": 0.042,
            "throat_gap_m": 0.038,
            "arm_reach_m": 0.155,
            "pad_length_m": 0.162,
            "pad_radius_m": 0.058,
        },
        reason="tightest frame cheeks, shortest support and smallest trough together",
    ),
    corner_case(
        "largest_clamp_and_longest_reach",
        {
            "clamp_span_m": 0.104,
            "frame_depth_m": 0.060,
            "throat_gap_m": 0.058,
            "arm_reach_m": 0.245,
            "pad_length_m": 0.212,
            "pad_radius_m": 0.082,
        },
        reason="widest frame, deepest throat, longest support and largest trough together",
    ),
    corner_case(
        "wide_throat_with_short_support",
        {
            "throat_gap_m": 0.058,
            "arm_reach_m": 0.155,
            "pad_length_m": 0.212,
            "pad_radius_m": 0.082,
            "frame_depth_m": 0.042,
        },
        reason="largest rest on the shortest support over the deepest throat",
    ),
    corner_case(
        "narrow_frame_with_longest_support",
        {
            "clamp_span_m": 0.072,
            "frame_depth_m": 0.042,
            "throat_gap_m": 0.038,
            "arm_reach_m": 0.245,
            "pad_length_m": 0.162,
            "pad_radius_m": 0.058,
        },
        reason="thinnest cheeks carrying the longest support",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_picturex_0611_ergonomic_clamp_with_adjustable",
    "build_seeded_picturex_0611_ergonomic_clamp_with_adjustable",
    "config_from_seed",
    "resolve_config",
    "run_picturex_0611_ergonomic_clamp_with_adjustable_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
