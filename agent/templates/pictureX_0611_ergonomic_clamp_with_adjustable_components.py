# SPDX-License-Identifier: Apache-2.0

"""Desk-clamp laptop/work tray arms (pictureX/0611).

The category host is always the same: a screw clamp C-frame, an upright post
with a lock knob, and a height carriage locked by a second knob.  Three slots
vary: the number of screw stations (`clamp_form`), the adjustable structure
between carriage and head (`arm_form`), and the tray head (`tray_head`).

Source evidence lives in
`articraft_template_authoring/source_maps/pictureX_0611_ergonomic_clamp_with_adjustable_components.md`.
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

ClampForm = Literal["single_screw", "dual_screw", "overcenter_cam"]
ArmForm = Literal[
    "two_link_arm", "telescoping_boom", "scissor_linkage", "gas_spring_parallelogram"
]
TrayHead = Literal[
    "fixed_tilt_tray", "sliding_rails", "quick_release_dovetail", "foldaway_hinge"
]
TrayWidth = Literal["fixed_deck", "sliding_side_rails"]
TiltLock = Literal["friction_handle", "sector_pawl"]

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "clamp_form",
            ("single_screw", "dual_screw", "overcenter_cam"),
            role="source-backed desk-clamp station layout and actuation",
        ),
        component_slot(
            "arm_form",
            (
                "two_link_arm",
                "telescoping_boom",
                "scissor_linkage",
                "gas_spring_parallelogram",
            ),
            role="source-backed adjustable arm structure",
        ),
        component_slot(
            "tray_head",
            (
                "fixed_tilt_tray",
                "sliding_rails",
                "quick_release_dovetail",
                "foldaway_hinge",
            ),
            role="source-backed tray head",
        ),
        component_slot(
            "tray_width",
            ("fixed_deck", "sliding_side_rails"),
            role="source-backed tray width interface",
        ),
        component_slot(
            "tilt_lock",
            ("friction_handle", "sector_pawl"),
            role="source-backed tray tilt lock",
        ),
    )
)

_PARALLEL_CANDIDATES = frozenset({"gas_spring_parallelogram"})


@dataclass(frozen=True)
class Config:
    clamp_form: ClampForm = "single_screw"
    arm_form: ArmForm = "two_link_arm"
    tray_head: TrayHead = "fixed_tilt_tray"
    tray_width: TrayWidth = "fixed_deck"
    tilt_lock: TiltLock = "friction_handle"
    clamp_throat_m: float = 0.046
    clamp_width_m: float = 0.062
    post_height_m: float = 0.180
    arm_reach_m: float = 0.230
    tray_width_m: float = 0.240
    tray_depth_m: float = 0.185
    name: str = "ergonomic_clamp_with_adjustable_components"


@dataclass(frozen=True)
class ResolvedConfig:
    clamp_form: ClampForm
    arm_form: ArmForm
    tray_head: TrayHead
    tray_width: TrayWidth
    tilt_lock: TiltLock
    clamp_throat_m: float
    clamp_width_m: float
    post_height_m: float
    arm_reach_m: float
    tray_width_m: float
    tray_depth_m: float
    name: str
    # derived host geometry
    frame_front_m: float
    frame_back_m: float
    plate_top_m: float
    beam_top_m: float
    station_x_m: tuple[float, ...]
    spindle_up_m: float
    spindle_dn_m: float
    post_x_m: float
    post_top_m: float
    carriage_mid_m: float
    carriage_travel_m: float
    shoulder_x_m: float


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x0611_C0A7_3B51)
    return Config(
        clamp_form=choices["clamp_form"],
        arm_form=choices["arm_form"],
        tray_head=choices["tray_head"],
        tray_width=choices["tray_width"],
        tilt_lock=choices["tilt_lock"],
        clamp_throat_m=round(rng.uniform(0.040, 0.060), 5),
        clamp_width_m=round(rng.uniform(0.054, 0.084), 5),
        post_height_m=round(rng.uniform(0.136, 0.224), 5),
        arm_reach_m=round(rng.uniform(0.176, 0.294), 5),
        tray_width_m=round(rng.uniform(0.196, 0.294), 5),
        tray_depth_m=round(rng.uniform(0.154, 0.226), 5),
        name=f"ergonomic_clamp_with_adjustable_components_seed_{seed}",
    )


def _require_range(name: str, value: float, minimum: float, maximum: float) -> float:
    value = float(value)
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be in [{minimum}, {maximum}], got {value}")
    return value


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "clamp_form": config.clamp_form,
            "arm_form": config.arm_form,
            "tray_head": config.tray_head,
            "tray_width": config.tray_width,
            "tilt_lock": config.tilt_lock,
        }
    )
    throat = _require_range("clamp_throat_m", config.clamp_throat_m, 0.038, 0.062)
    width = _require_range("clamp_width_m", config.clamp_width_m, 0.052, 0.086)
    post_h = _require_range("post_height_m", config.post_height_m, 0.130, 0.230)
    reach = _require_range("arm_reach_m", config.arm_reach_m, 0.170, 0.300)
    tray_w = _require_range("tray_width_m", config.tray_width_m, 0.190, 0.300)
    tray_d = _require_range("tray_depth_m", config.tray_depth_m, 0.150, 0.230)

    frame_back = -0.092 if config.clamp_form != "dual_screw" else -0.128
    stations = (-0.052,) if config.clamp_form != "dual_screw" else (-0.032, -0.096)
    plate_top = throat + 0.014
    post_x = 0.034
    return ResolvedConfig(
        clamp_form=config.clamp_form,
        arm_form=config.arm_form,
        tray_head=config.tray_head,
        tray_width=config.tray_width,
        tilt_lock=config.tilt_lock,
        clamp_throat_m=throat,
        clamp_width_m=width,
        post_height_m=post_h,
        arm_reach_m=reach,
        tray_width_m=tray_w,
        tray_depth_m=tray_d,
        name=config.name,
        frame_front_m=0.050,
        frame_back_m=frame_back,
        plate_top_m=plate_top,
        beam_top_m=0.0,
        station_x_m=stations,
        spindle_up_m=throat - 0.025,
        spindle_dn_m=-0.010,
        post_x_m=post_x,
        post_top_m=plate_top + post_h,
        carriage_mid_m=plate_top + post_h * 0.58,
        carriage_travel_m=post_h * 0.22,
        shoulder_x_m=post_x + 0.034,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, str]:
    return {
        "clamp_form": config.clamp_form,
        "arm_form": config.arm_form,
        "tray_head": config.tray_head,
        "tray_width": config.tray_width,
        "tilt_lock": config.tilt_lock,
    }


def slot_choices_for_seed(seed: int) -> dict[str, str]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject) -> dict[str, object]:
    return {
        "powder": model.material("tray_arm_powder_black", rgba=(0.070, 0.074, 0.078, 1.0)),
        "steel": model.material("tray_arm_satin_steel", rgba=(0.56, 0.58, 0.60, 1.0)),
        "dark": model.material("tray_arm_dark_steel", rgba=(0.19, 0.20, 0.21, 1.0)),
        "polymer": model.material("tray_arm_charcoal_polymer", rgba=(0.090, 0.094, 0.098, 1.0)),
        "rubber": model.material("tray_arm_soft_rubber", rgba=(0.030, 0.032, 0.034, 1.0)),
        "deck": model.material("tray_arm_deck_grey", rgba=(0.28, 0.29, 0.30, 1.0)),
    }


# ---------------------------------------------------------------------------
# shared CadQuery profiles
# ---------------------------------------------------------------------------


def _clamp_frame_shape(r: ResolvedConfig) -> cq.Workplane:
    """Folded C-frame with a real throat and a bored hole per screw station."""

    back, front = r.frame_back_m, r.frame_front_m
    profile = [
        (back, r.plate_top_m),
        (front, r.plate_top_m),
        (front, -0.014),
        (back, -0.014),
        (back, 0.0),
        (0.030, 0.0),
        (0.030, r.clamp_throat_m),
        (back, r.clamp_throat_m),
    ]
    frame = (
        cq.Workplane("XZ")
        .polyline(profile)
        .close()
        .extrude(r.clamp_width_m * 0.5, both=True)
    )
    for station in r.station_x_m:
        frame = frame.cut(
            cq.Workplane("XY")
            .center(station, 0.0)
            .circle(0.0063)
            .extrude(0.040, both=True)
        )
    return frame


def _fork_shape(
    *,
    half_gap: float,
    cheek_t: float,
    cheek_w: float,
    cheek_top: float,
    bore_radius: float,
    axis: str = "y",
    web_clearance: float = 0.0,
) -> cq.Workplane:
    """Two bored cheeks joined by a web below the pin: one connected fork."""

    web_top = -max(bore_radius + 0.0015, web_clearance)
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


def _swing_bar_shape(
    length: float,
    width: float,
    thickness: float,
    *,
    hub_outer: float,
    hub_bore: float,
    end_outer: float | None = None,
) -> cq.Workplane:
    """Flat horizontal swing link with a bored hub and an optional end boss."""

    half = 0.5 * width
    profile = [
        (0.0, -half),
        (length, -half * 0.78),
        (length, half * 0.78),
        (0.0, half),
    ]
    bar = (
        cq.Workplane("XY")
        .polyline(profile)
        .close()
        .extrude(thickness * 0.5, both=True)
    )
    bar = bar.union(
        cq.Workplane("XY").circle(hub_outer).extrude(thickness * 0.5, both=True)
    )
    if end_outer is not None:
        bar = bar.union(
            cq.Workplane("XY")
            .center(length, 0.0)
            .circle(end_outer)
            .extrude(thickness * 0.5, both=True)
        )
    bar = bar.cut(cq.Workplane("XY").circle(hub_bore).extrude(thickness, both=True))
    return bar


def _rect_tube_shape(length: float, w: float, h: float, wall: float) -> cq.Workplane:
    """Genuinely hollow rectangular boom section along +X."""

    outer = (
        cq.Workplane("YZ").rect(w, h).extrude(length).translate((0.0, 0.0, 0.0))
    )
    inner = (
        cq.Workplane("YZ")
        .rect(w - 2.0 * wall, h - 2.0 * wall)
        .extrude(length + 0.004)
        .translate((-0.002, 0.0, 0.0))
    )
    return outer.cut(inner)


def _collar_shape(outer: float, bore: float, height: float) -> cq.Workplane:
    """Split clamp collar bored to run on the upright post."""

    collar = cq.Workplane("XY").circle(outer).extrude(height * 0.5, both=True)
    collar = collar.cut(
        cq.Workplane("XY").circle(bore).extrude(height, both=True)
    )
    relief = (
        cq.Workplane("XY")
        .box(0.006, 2.2 * outer, height * 0.45)
        .translate((-outer + 0.003, 0.0, 0.0))
    )
    return collar.cut(relief)


def _tray_deck_shape(width: float, depth: float, style: str) -> cq.Workplane:
    """Deck plate.  Each head family has its own real surface treatment: a
    round-hole perforated field with a front lip, a long-slotted field between
    side edge rails, or a solid plate inside a three-sided rim."""

    deck = cq.Workplane("XY").box(depth, width, 0.009)
    if style == "fixed_tilt_tray":
        columns = max(3, int(width / 0.034))
        rows = max(2, int(depth / 0.036))
        for row in range(rows):
            for col in range(columns):
                x = -0.5 * depth + depth * (row + 0.5) / rows
                y = -0.5 * width + width * (col + 0.5) / columns
                deck = deck.cut(
                    cq.Workplane("XY")
                    .center(x, y)
                    .circle(0.0072)
                    .extrude(0.020, both=True)
                )
        lip = (
            cq.Workplane("XY")
            .box(0.010, width, 0.020)
            .translate((0.5 * depth - 0.005, 0.0, 0.0095))
        )
        return deck.union(lip)

    if style == "sliding_rails":
        columns = max(3, int(width / 0.052))
        for col in range(columns):
            y = -0.5 * width + width * (col + 0.5) / columns
            deck = deck.cut(
                cq.Workplane("XY")
                .box(depth * 0.64, 0.014, 0.020)
                .translate((0.0, y, 0.0))
            )
        for sign in (-1.0, 1.0):
            rail = (
                cq.Workplane("XY")
                .box(depth, 0.012, 0.022)
                .translate((0.0, sign * (0.5 * width - 0.006), 0.0105))
            )
            deck = deck.union(rail)
        return deck

    rim: cq.Workplane = deck
    for dx, dy, sx, sy in (
        (0.5 * depth - 0.005, 0.0, 0.010, width),
        (0.0, 0.5 * width - 0.005, depth, 0.010),
        (0.0, -(0.5 * width - 0.005), depth, 0.010),
    ):
        rim = rim.union(
            cq.Workplane("XY").box(sx, sy, 0.024).translate((dx, dy, 0.0115))
        )
    notch = (
        cq.Workplane("XY")
        .box(0.020, width * 0.22, 0.040)
        .translate((-0.5 * depth + 0.006, 0.0, 0.012))
    )
    return rim.cut(notch)


def _dovetail_rail_shape(length: float) -> cq.Workplane:
    """Male dovetail rail (wider at its base) extruded along +X."""

    profile = [(-0.016, 0.0), (0.016, 0.0), (0.010, 0.012), (-0.010, 0.012)]
    return cq.Workplane("YZ").polyline(profile).close().extrude(length)


def _dovetail_channel_shape(length: float) -> cq.Workplane:
    """Female dovetail block: a saddle with the mating channel cut out."""

    block = (
        cq.Workplane("YZ")
        .rect(0.052, 0.026)
        .extrude(length)
        .translate((0.0, 0.0, 0.011))
    )
    channel = [
        (-0.0168, -0.002),
        (0.0168, -0.002),
        (0.0108, 0.0128),
        (-0.0108, 0.0128),
    ]
    cut = (
        cq.Workplane("YZ")
        .polyline(channel)
        .close()
        .extrude(length + 0.006)
        .translate((-0.003, 0.0, 0.0))
    )
    return block.cut(cut)


# ---------------------------------------------------------------------------
# host: clamp, post and height carriage
# ---------------------------------------------------------------------------


def _add_seat_pad(part, mats, *, name: str, point: tuple[float, float, float],
                  radius: float = 0.017, length: float = 0.026) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=(point[0], point[1], point[2] - 0.004 - 0.5 * length)),
        material=mats["dark"],
        name=name, material_class_id="metal.blackened_gunmetal",
    )


def _build_clamp(model: ArticulatedObject, r: ResolvedConfig, mats):
    frame = model.part("clamp__frame", meta={"role": "clamp_frame"})
    frame.visual(
        mesh_from_cadquery(_clamp_frame_shape(r), "clamp__frame_web", tolerance=0.0008),
        material=mats["powder"],
        name="clamp__frame__c_frame", material_class_id="metal.paint_coated",
    )
    for index, station in enumerate(r.station_x_m):
        frame.visual(
            Cylinder(radius=0.017, length=0.005),
            origin=Origin(xyz=(station, 0.0, r.clamp_throat_m + 0.0015)),
            material=mats["rubber"],
            name=f"clamp__frame__jaw_pad_{index}", material_class_id="rubber.smooth_plain",
        )
    # Upright post with a base collar; every source carries the same column.
    frame.visual(
        Cylinder(radius=0.016, length=r.post_height_m),
        origin=Origin(xyz=(r.post_x_m, 0.0, r.plate_top_m + 0.5 * r.post_height_m)),
        material=mats["steel"],
        name="clamp__frame__upright_post", material_class_id="metal.steel_bare",
    )
    frame.visual(
        Cylinder(radius=0.023, length=0.012),
        origin=Origin(xyz=(r.post_x_m, 0.0, r.plate_top_m + 0.006)),
        material=mats["powder"],
        name="clamp__frame__post_base", material_class_id="metal.paint_coated",
    )
    frame.visual(
        Cylinder(radius=0.009, length=0.012),
        origin=Origin(
            xyz=(r.post_x_m - 0.019, 0.0, r.plate_top_m + 0.014),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["dark"],
        name="clamp__frame__post_lock_boss", material_class_id="metal.blackened_gunmetal",
    )
    return frame


def _build_clamp_screws(model: ArticulatedObject, r: ResolvedConfig, mats, frame) -> None:
    for index, station in enumerate(r.station_x_m):
        spindle = model.part(
            f"clamp__spindle_{index}", meta={"role": "clamp_screw", "station": index}
        )
        spindle.visual(
            Cylinder(radius=0.0055, length=0.079),
            origin=Origin(xyz=(0.0, 0.0, -0.0225)),
            material=mats["steel"],
            name=f"clamp__spindle_{index}__shaft", material_class_id="metal.steel_bare",
        )
        for crest in range(4):
            spindle.visual(
                Cylinder(radius=0.0070, length=0.0022),
                origin=Origin(xyz=(0.0, 0.0, -0.020 - 0.008 * crest)),
                material=mats["dark"],
                name=f"clamp__spindle_{index}__thread_crest_{crest}", material_class_id="metal.blackened_gunmetal",
            )
        spindle.visual(
            Cylinder(radius=0.011, length=0.010),
            origin=Origin(xyz=(0.0, 0.0, -0.060)),
            material=mats["polymer"],
            name=f"clamp__spindle_{index}__handle_hub", material_class_id="plastic.opaque_generic",
        )
        for wing, sign in enumerate((-1.0, 1.0)):
            spindle.visual(
                Box((0.020, 0.007, 0.014)),
                origin=Origin(xyz=(sign * 0.019, 0.0, -0.060)),
                material=mats["polymer"],
                name=f"clamp__spindle_{index}__wing_{wing}", material_class_id="plastic.opaque_generic",
            )
        model.articulation(
            f"clamp__spindle_adjust_{index}",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=spindle,
            origin=Origin(xyz=(station, 0.0, r.beam_top_m)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=900.0,
                velocity=0.05,
                lower=r.spindle_dn_m,
                upper=r.spindle_up_m,
            ),
            meta={"mechanism": "screw clamp travel"},
        )

        shoe = model.part(
            f"clamp__pressure_pad_{index}", meta={"role": "clamp_shoe", "station": index}
        )
        shoe.visual(
            Cylinder(radius=0.016, length=0.006),
            origin=Origin(xyz=(0.0, 0.0, 0.003)),
            material=mats["dark"],
            name=f"clamp__pressure_pad_{index}__plate", material_class_id="metal.blackened_gunmetal",
        )
        shoe.visual(
            Cylinder(radius=0.015, length=0.003),
            origin=Origin(xyz=(0.0, 0.0, 0.0075)),
            material=mats["rubber"],
            name=f"clamp__pressure_pad_{index}__face", material_class_id="rubber.smooth_plain",
        )
        provider = AxisInterface(
            name=f"clamp.shoe_seat_{index}",
            point=(0.0, 0.0, 0.010),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=0.0055,
        )
        consumer = AxisInterface(
            name=f"clamp.shoe_hub_{index}",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=0.0055,
        )
        mate = mate_axes(provider, consumer)
        joint = f"clamp__pad_swivel_{index}"
        model.articulation(
            joint,
            ArticulationType.CONTINUOUS,
            parent=spindle,
            child=shoe,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(effort=20.0, velocity=6.0),
            meta={"mechanism": "self-aligning pressure shoe"},
        )
        register_interface_mate(model, joint, mate)


def _build_column(model: ArticulatedObject, r: ResolvedConfig, mats, frame):
    """Post lock knob plus the height carriage and its own lock knob."""

    post_lock = model.part("clamp__post_lock", meta={"role": "post_lock"})
    post_lock.visual(
        Cylinder(radius=0.013, length=0.014),
        origin=Origin(xyz=(-0.007, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["polymer"],
        name="clamp__post_lock__knob", material_class_id="plastic.opaque_generic",
    )
    post_lock.visual(
        Cylinder(radius=0.0085, length=0.005),
        origin=Origin(xyz=(-0.0165, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name="clamp__post_lock__grip_ring", material_class_id="metal.steel_bare",
    )
    lock_provider = AxisInterface(
        name="clamp.post_lock_seat",
        point=(r.post_x_m - 0.025, 0.0, r.plate_top_m + 0.014),
        axis=(-1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.009,
    )
    lock_consumer = AxisInterface(
        name="clamp.post_lock_stem",
        point=(0.0, 0.0, 0.0),
        axis=(-1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0055,
    )
    lock_mate = mate_axes(lock_provider, lock_consumer)
    model.articulation(
        "clamp__post_lock_turn",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=post_lock,
        origin=lock_mate.origin,
        axis=lock_mate.axis,
        motion_limits=MotionLimits(effort=12.0, velocity=6.0),
        meta={"mechanism": "post clamp lock"},
    )
    register_interface_mate(model, "clamp__post_lock_turn", lock_mate)

    carriage = model.part("clamp__carriage", meta={"role": "height_carriage"})
    carriage.visual(
        mesh_from_cadquery(
            _collar_shape(0.026, 0.0168, 0.044), "clamp__carriage_collar", tolerance=0.0006
        ),
        material=mats["powder"],
        name="clamp__carriage__collar", material_class_id="metal.paint_coated",
    )
    carriage.visual(
        Box((0.030, 0.034, 0.014)),
        origin=Origin(xyz=(0.030, 0.0, -0.024)),
        material=mats["powder"],
        name="clamp__carriage__shoulder_block", material_class_id="metal.paint_coated",
    )
    model.articulation(
        "clamp__carriage_height",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=carriage,
        origin=Origin(xyz=(r.post_x_m, 0.0, r.carriage_mid_m)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=400.0,
            velocity=0.1,
            lower=-r.carriage_travel_m,
            upper=r.carriage_travel_m,
        ),
        meta={"mechanism": "height carriage on the upright post"},
    )

    carriage_lock = model.part("clamp__carriage_lock", meta={"role": "carriage_lock"})
    carriage_lock.visual(
        Cylinder(radius=0.013, length=0.014),
        origin=Origin(xyz=(0.0, 0.007, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["polymer"],
        name="clamp__carriage_lock__knob", material_class_id="plastic.opaque_generic",
    )
    carriage_lock.visual(
        Cylinder(radius=0.0085, length=0.005),
        origin=Origin(xyz=(0.0, 0.0165, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="clamp__carriage_lock__grip_ring", material_class_id="metal.steel_bare",
    )
    carriage.visual(
        Cylinder(radius=0.009, length=0.012),
        origin=Origin(xyz=(0.0, 0.024, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name="clamp__carriage__lock_boss", material_class_id="metal.blackened_gunmetal",
    )
    ck_provider = AxisInterface(
        name="clamp.carriage_lock_seat",
        point=(0.0, 0.030, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.009,
    )
    ck_consumer = AxisInterface(
        name="clamp.carriage_lock_stem",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0055,
    )
    ck_mate = mate_axes(ck_provider, ck_consumer)
    model.articulation(
        "clamp__carriage_lock_turn",
        ArticulationType.CONTINUOUS,
        parent=carriage,
        child=carriage_lock,
        origin=ck_mate.origin,
        axis=ck_mate.axis,
        motion_limits=MotionLimits(effort=12.0, velocity=6.0),
        meta={"mechanism": "height carriage lock"},
    )
    register_interface_mate(model, "clamp__carriage_lock_turn", ck_mate)
    _add_shoulder_mount(carriage, r, mats)
    return carriage


def _add_shoulder_mount(carriage, r: ResolvedConfig, mats) -> None:
    """Host adaptation: a vertical spigot for swing arms, a clevis for the
    vertical-plane parallelogram."""

    if r.arm_form in _PARALLEL_CANDIDATES:
        carriage.visual(
            mesh_from_cadquery(
                _fork_shape(
                    half_gap=0.014,
                    cheek_t=0.007,
                    cheek_w=0.030,
                    cheek_top=0.006,
                    bore_radius=0.0098,
                    web_clearance=0.020,
                ),
                "clamp__carriage_clevis",
                tolerance=0.0005,
            ),
            origin=Origin(xyz=(0.044, 0.0, 0.006)),
            material=mats["dark"],
            name="clamp__carriage__shoulder_clevis", material_class_id="metal.blackened_gunmetal",
        )
        return
    carriage.visual(
        Cylinder(radius=0.013, length=0.052),
        origin=Origin(xyz=(0.044, 0.0, -0.008)),
        material=mats["dark"],
        name="clamp__carriage__shoulder_spigot", material_class_id="metal.blackened_gunmetal",
    )


def _seat(part, point, *, extra=None) -> dict:
    return {"part": part, "point": point, "extra": extra or {}}


# ---------------------------------------------------------------------------
# arm_form candidates
# ---------------------------------------------------------------------------


def _shoulder_axis_mate(r: ResolvedConfig, *, prefix: str):
    provider = AxisInterface(
        name="carriage.shoulder_spigot",
        point=(0.044, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.013,
    )
    consumer = AxisInterface(
        name=f"{prefix}.shoulder_bore",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0138,
    )
    return mate_axes(provider, consumer)


def _arm_form_two_link_arm_build(model, r, mats):
    candidate = "two_link_arm"
    prefix = f"arm_form__{candidate}"
    carriage = model.get_part("clamp__carriage")
    l1 = r.arm_reach_m * 0.52
    l2 = r.arm_reach_m * 0.48

    primary = model.part(
        f"{prefix}__primary", meta={"role": "support_arm", "candidate": candidate}
    )
    primary.visual(
        mesh_from_cadquery(
            _swing_bar_shape(l1, 0.034, 0.016, hub_outer=0.021, hub_bore=0.0138),
            f"{prefix}__primary_bar",
            tolerance=0.0007,
        ),
        material=mats["polymer"],
        name=f"{prefix}__primary__bar", material_class_id="plastic.opaque_generic",
    )
    primary.visual(
        Cylinder(radius=0.0115, length=0.052),
        origin=Origin(xyz=(l1, 0.0, 0.010)),
        material=mats["dark"],
        name=f"{prefix}__primary__elbow_spigot", material_class_id="metal.blackened_gunmetal",
    )
    mate = _shoulder_axis_mate(r, prefix=prefix)
    joint = f"{prefix}__carriage_to_arm"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=primary,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=90.0, velocity=1.4, lower=-0.60, upper=0.60),
        meta={"mechanism": "shoulder swing"},
    )
    register_interface_mate(model, joint, mate)

    secondary = model.part(
        f"{prefix}__secondary", meta={"role": "support_link", "candidate": candidate}
    )
    secondary.visual(
        mesh_from_cadquery(
            _swing_bar_shape(l2, 0.030, 0.016, hub_outer=0.019, hub_bore=0.0123),
            f"{prefix}__secondary_bar",
            tolerance=0.0007,
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.026)),
        material=mats["polymer"],
        name=f"{prefix}__secondary__bar", material_class_id="plastic.opaque_generic",
    )
    elbow_provider = AxisInterface(
        name=f"{prefix}.elbow_spigot",
        point=(l1, 0.0, 0.026),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0115,
    )
    elbow_consumer = AxisInterface(
        name=f"{prefix}.elbow_bore",
        point=(0.0, 0.0, 0.026),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0123,
    )
    elbow_mate = mate_axes(elbow_provider, elbow_consumer)
    elbow_joint = f"{prefix}__arm_elbow"
    model.articulation(
        elbow_joint,
        ArticulationType.REVOLUTE,
        parent=primary,
        child=secondary,
        origin=elbow_mate.origin,
        axis=elbow_mate.axis,
        motion_limits=MotionLimits(effort=70.0, velocity=1.4, lower=-0.60, upper=0.60),
        meta={"mechanism": "arm elbow"},
    )
    register_interface_mate(model, elbow_joint, elbow_mate)
    seat = (l2, 0.0, 0.038)
    _add_seat_pad(secondary, mats, name=f"{prefix}__secondary__head_seat_pad", point=seat)
    return _seat(secondary, seat)


def _arm_form_telescoping_boom_build(model, r, mats):
    candidate = "telescoping_boom"
    prefix = f"arm_form__{candidate}"
    carriage = model.get_part("clamp__carriage")
    tube_start = 0.024
    outer_len = r.arm_reach_m * 0.58
    inner_len = outer_len * 0.74
    stroke = r.arm_reach_m * 0.14

    outer = model.part(
        f"{prefix}__outer_boom", meta={"role": "support_arm", "candidate": candidate}
    )
    outer.visual(
        mesh_from_cadquery(
            _rect_tube_shape(outer_len, 0.040, 0.030, 0.0045),
            f"{prefix}__outer_tube",
            tolerance=0.0007,
        ),
        origin=Origin(xyz=(tube_start, 0.0, 0.0)),
        material=mats["polymer"],
        name=f"{prefix}__outer_boom__tube", material_class_id="plastic.opaque_generic",
    )
    outer.visual(
        mesh_from_cadquery(
            _swing_bar_shape(tube_start + 0.006, 0.036, 0.030, hub_outer=0.021,
                             hub_bore=0.0138),
            f"{prefix}__outer_hub",
            tolerance=0.0007,
        ),
        material=mats["dark"],
        name=f"{prefix}__outer_boom__hub", material_class_id="metal.blackened_gunmetal",
    )
    mate = _shoulder_axis_mate(r, prefix=prefix)
    joint = f"{prefix}__carriage_to_arm"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=outer,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=90.0, velocity=1.4, lower=-0.60, upper=0.60),
        meta={"mechanism": "shoulder swing"},
    )
    register_interface_mate(model, joint, mate)

    inner = model.part(
        f"{prefix}__inner_boom", meta={"role": "support_link", "candidate": candidate}
    )
    inner.visual(
        mesh_from_cadquery(
            _rect_tube_shape(inner_len, 0.030, 0.020, 0.0040),
            f"{prefix}__inner_tube",
            tolerance=0.0007,
        ),
        material=mats["dark"],
        name=f"{prefix}__inner_boom__tube", material_class_id="metal.blackened_gunmetal",
    )
    inner.visual(
        Box((0.030, 0.034, 0.024)),
        origin=Origin(xyz=(inner_len + 0.013, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__inner_boom__end_block", material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        f"{prefix}__arm_telescope",
        ArticulationType.PRISMATIC,
        parent=outer,
        child=inner,
        origin=Origin(xyz=(tube_start + outer_len - inner_len + 0.004, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=250.0, velocity=0.2, lower=0.0, upper=stroke),
        meta={"mechanism": "telescope stroke"},
    )
    seat = (inner_len + 0.018, 0.0, 0.024)
    _add_seat_pad(inner, mats, name=f"{prefix}__inner_boom__head_seat_pad", point=seat)
    return _seat(inner, seat)


def _arm_form_scissor_linkage_build(model, r, mats):
    candidate = "scissor_linkage"
    prefix = f"arm_form__{candidate}"
    carriage = model.get_part("clamp__carriage")
    link_len = r.arm_reach_m * 0.66

    lower = model.part(
        f"{prefix}__lower_link", meta={"role": "support_arm", "candidate": candidate}
    )
    lower.visual(
        mesh_from_cadquery(
            _swing_bar_shape(
                link_len, 0.032, 0.014, hub_outer=0.021, hub_bore=0.0138,
                end_outer=0.017,
            ),
            f"{prefix}__lower_bar",
            tolerance=0.0007,
        ),
        material=mats["polymer"],
        name=f"{prefix}__lower_link__bar", material_class_id="plastic.opaque_generic",
    )
    lower.visual(
        Cylinder(radius=0.0110, length=0.048),
        origin=Origin(xyz=(link_len * 0.52, 0.0, 0.014)),
        material=mats["dark"],
        name=f"{prefix}__lower_link__cross_spigot", material_class_id="metal.blackened_gunmetal",
    )
    mate = _shoulder_axis_mate(r, prefix=prefix)
    joint = f"{prefix}__carriage_to_scissor"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=lower,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=90.0, velocity=1.4, lower=-0.55, upper=0.55),
        meta={"mechanism": "scissor base swing"},
    )
    register_interface_mate(model, joint, mate)

    upper = model.part(
        f"{prefix}__upper_link", meta={"role": "support_link", "candidate": candidate}
    )
    upper.visual(
        mesh_from_cadquery(
            _swing_bar_shape(link_len, 0.028, 0.014, hub_outer=0.019, hub_bore=0.0118),
            f"{prefix}__upper_bar",
            tolerance=0.0007,
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.024)),
        material=mats["polymer"],
        name=f"{prefix}__upper_link__bar", material_class_id="plastic.opaque_generic",
    )
    cross_provider = AxisInterface(
        name=f"{prefix}.cross_spigot",
        point=(link_len * 0.52, 0.0, 0.024),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0110,
    )
    cross_consumer = AxisInterface(
        name=f"{prefix}.cross_bore",
        point=(0.0, 0.0, 0.024),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0118,
    )
    cross_mate = mate_axes(cross_provider, cross_consumer)
    cross_joint = f"{prefix}__scissor_cross"
    model.articulation(
        cross_joint,
        ArticulationType.REVOLUTE,
        parent=lower,
        child=upper,
        origin=cross_mate.origin,
        axis=cross_mate.axis,
        motion_limits=MotionLimits(effort=70.0, velocity=1.4, lower=-0.55, upper=0.55),
        meta={"mechanism": "scissor crossing pivot"},
    )
    register_interface_mate(model, cross_joint, cross_mate)
    seat = (link_len, 0.0, 0.036)
    _add_seat_pad(upper, mats, name=f"{prefix}__upper_link__head_seat_pad", point=seat)
    return _seat(upper, seat)


def _arm_form_gas_spring_parallelogram_build(model, r, mats):
    candidate = "gas_spring_parallelogram"
    prefix = f"arm_form__{candidate}"
    carriage = model.get_part("clamp__carriage")
    lift = 0.30
    l1 = r.arm_reach_m * 0.52
    l2 = r.arm_reach_m * 0.50

    lower = model.part(
        f"{prefix}__lower_link", meta={"role": "support_arm", "candidate": candidate}
    )
    lower.visual(
        mesh_from_cadquery(
            _swing_bar_shape(l1, 0.030, 0.020, hub_outer=0.017, hub_bore=0.0060),
            f"{prefix}__lower_bar",
            tolerance=0.0007,
        ),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["polymer"],
        name=f"{prefix}__lower_link__bar", material_class_id="plastic.opaque_generic",
    )
    lower.visual(
        Cylinder(radius=0.0096, length=0.040),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__lower_link__shoulder_pin", material_class_id="metal.steel_bare",
    )
    provider = AxisInterface(
        name="carriage.shoulder_clevis",
        point=(0.044, 0.0, 0.006),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0098,
    )
    consumer = AxisInterface(
        name=f"{prefix}.shoulder_pin",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0096,
    )
    mate = mate_axes(provider, consumer, spin=lift)
    joint = f"{prefix}__shoulder_lift"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=lower,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=160.0, velocity=1.2, lower=-0.24, upper=0.24),
        meta={"mechanism": "parallelogram shoulder lift"},
    )
    register_interface_mate(model, joint, mate)

    lower.visual(
        Cylinder(radius=0.0090, length=0.070),
        origin=Origin(xyz=(l1, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__lower_link__elbow_pin", material_class_id="metal.blackened_gunmetal",
    )
    upper = model.part(
        f"{prefix}__upper_link", meta={"role": "support_link", "candidate": candidate}
    )
    upper.visual(
        mesh_from_cadquery(
            _swing_bar_shape(l2, 0.026, 0.018, hub_outer=0.016, hub_bore=0.0098),
            f"{prefix}__upper_bar",
            tolerance=0.0007,
        ),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["polymer"],
        name=f"{prefix}__upper_link__bar", material_class_id="plastic.opaque_generic",
    )
    up_provider = AxisInterface(
        name=f"{prefix}.elbow_pin",
        point=(l1, 0.0, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0090,
    )
    up_consumer = AxisInterface(
        name=f"{prefix}.elbow_bore",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0098,
    )
    up_mate = mate_axes(up_provider, up_consumer, spin=-lift, axial_offset=-0.024)
    up_joint = f"{prefix}__upper_link_hinge"
    model.articulation(
        up_joint,
        ArticulationType.REVOLUTE,
        parent=lower,
        child=upper,
        origin=up_mate.origin,
        axis=up_mate.axis,
        motion_limits=MotionLimits(effort=120.0, velocity=1.2, lower=-0.24, upper=0.24),
        meta={"mechanism": "parallelogram upper hinge"},
    )
    register_interface_mate(model, up_joint, up_mate)

    # Gas strut, outboard of the links so it never shares their volume.
    # The strut bracket hangs off the collar well behind the shoulder pin, so
    # the strut runs in its own plane clear of both parallelogram bars.
    carriage.visual(
        Box((0.024, 0.032, 0.032)),
        origin=Origin(xyz=(0.018, -0.030, -0.010)),
        material=mats["powder"],
        name="clamp__carriage__strut_bracket", material_class_id="metal.paint_coated",
    )
    carriage.visual(
        Cylinder(radius=0.0072, length=0.012),
        origin=Origin(xyz=(0.018, -0.052, -0.018), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name="clamp__carriage__strut_boss", material_class_id="metal.blackened_gunmetal",
    )
    cylinder = model.part(
        f"{prefix}__gas_cylinder", meta={"role": "support_link", "candidate": candidate}
    )
    body_len = 0.070
    cylinder.visual(
        mesh_from_cadquery(
            _gas_tube_shape(body_len), f"{prefix}__gas_tube", tolerance=0.0006
        ),
        material=mats["dark"],
        name=f"{prefix}__gas_cylinder__body", material_class_id="metal.blackened_gunmetal",
    )
    cylinder.visual(
        Cylinder(radius=0.0072, length=0.012),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__gas_cylinder__eye", material_class_id="metal.steel_bare",
    )
    strut_provider = AxisInterface(
        name="carriage.strut_seat",
        point=(0.018, -0.0705, -0.018),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0072,
    )
    strut_consumer = AxisInterface(
        name=f"{prefix}.strut_eye",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0070,
    )
    strut_mate = mate_axes(strut_provider, strut_consumer, spin=0.72)
    strut_joint = f"{prefix}__gas_spring_base"
    model.articulation(
        strut_joint,
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=cylinder,
        origin=strut_mate.origin,
        axis=strut_mate.axis,
        motion_limits=MotionLimits(effort=60.0, velocity=1.2, lower=-0.18, upper=0.18),
        meta={"mechanism": "gas-spring base pivot"},
    )
    register_interface_mate(model, strut_joint, strut_mate)

    piston = model.part(
        f"{prefix}__gas_piston", meta={"role": "support_link", "candidate": candidate}
    )
    piston.visual(
        Cylinder(radius=0.0058, length=0.070),
        origin=Origin(xyz=(0.006, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__gas_piston__rod", material_class_id="metal.steel_bare",
    )
    piston.visual(
        Sphere(radius=0.0082),
        origin=Origin(xyz=(0.039, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__gas_piston__eye", material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        f"{prefix}__gas_spring_extend",
        ArticulationType.PRISMATIC,
        parent=cylinder,
        child=piston,
        origin=Origin(xyz=(body_len - 0.014, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=400.0, velocity=0.2, lower=-0.010, upper=0.014),
        meta={"mechanism": "gas-spring stroke"},
    )
    seat = (l2, 0.0, 0.024)
    _add_seat_pad(upper, mats, name=f"{prefix}__upper_link__head_seat_pad", point=seat)
    return _seat(upper, seat)


def _gas_tube_shape(body_len: float) -> cq.Workplane:
    tube = cq.Workplane("YZ").circle(0.0115).extrude(body_len)
    bore = cq.Workplane("YZ").circle(0.0066).extrude(body_len).translate((0.008, 0.0, 0.0))
    return tube.cut(bore)


_ARM_BUILDERS = {
    "two_link_arm": _arm_form_two_link_arm_build,
    "telescoping_boom": _arm_form_telescoping_boom_build,
    "scissor_linkage": _arm_form_scissor_linkage_build,
    "gas_spring_parallelogram": _arm_form_gas_spring_parallelogram_build,
}


# ---------------------------------------------------------------------------
# tray_head candidates
# ---------------------------------------------------------------------------


_YOKE_POST_H = 0.066


def _add_yoke(model, r, mats, seat, *, candidate: str, post_top: float):
    """Vertical head-yaw yoke shared by every tray head."""

    prefix = f"tray_head__{candidate}"
    yoke = model.part(f"{prefix}__yoke", meta={"role": "tray_yoke", "candidate": candidate})
    yoke.visual(
        Cylinder(radius=0.016, length=0.024),
        origin=Origin(xyz=(0.0, 0.0, 0.008)),
        material=mats["dark"],
        name=f"{prefix}__yoke__collar", material_class_id="metal.blackened_gunmetal",
    )
    yoke.visual(
        Cylinder(radius=0.0115, length=post_top - 0.018),
        origin=Origin(xyz=(0.0, 0.0, 0.018 + 0.5 * (post_top - 0.018))),
        material=mats["powder"],
        name=f"{prefix}__yoke__post", material_class_id="metal.paint_coated",
    )
    provider = AxisInterface(
        name=f"{prefix}.head_seat",
        point=seat["point"],
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0162,
    )
    consumer = AxisInterface(
        name=f"{prefix}.yoke_collar",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.016,
    )
    mate = mate_axes(provider, consumer)
    joint = f"{prefix}__head_yaw"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=seat["part"],
        child=yoke,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=40.0, velocity=1.4, lower=-0.55, upper=0.55),
        meta={"mechanism": "tray head yaw"},
    )
    register_interface_mate(model, joint, mate)
    return yoke


def _add_tilt_lock(model, r, mats, *, prefix: str, parent, tray, pin_point) -> None:
    """The tray tilt is either friction-held or indexed by a sector and pawl."""

    if r.tilt_lock == "friction_handle":
        parent.visual(
            Cylinder(radius=0.0130, length=0.016),
            origin=Origin(
                xyz=(pin_point[0], 0.033, pin_point[2]),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["steel"],
            name=f"{prefix}__tilt_lock__handle_stem", material_class_id="metal.steel_bare",
        )
        parent.visual(
            Cylinder(radius=0.0175, length=0.012),
            origin=Origin(
                xyz=(pin_point[0], 0.045, pin_point[2]),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["polymer"],
            name=f"{prefix}__tilt_lock__handle_knob", material_class_id="plastic.opaque_generic",
        )
        return

    # Toothed sector on the tilt carrier, sprung pawl on the tray itself.
    parent.visual(
        Cylinder(radius=0.026, length=0.006),
        origin=Origin(
            xyz=(pin_point[0], 0.032, pin_point[2]),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["steel"],
        name=f"{prefix}__tilt_lock__sector_plate", material_class_id="metal.steel_bare",
    )
    for index in range(7):
        angle = -0.42 + 0.14 * index
        parent.visual(
            Box((0.008, 0.006, 0.005)),
            origin=Origin(
                xyz=(
                    pin_point[0] + 0.0275 * math.cos(angle),
                    0.032,
                    pin_point[2] - 0.0275 * math.sin(angle),
                ),
                rpy=(0.0, angle, 0.0),
            ),
            material=mats["steel"],
            name=f"{prefix}__tilt_lock__sector_tooth_{index}", material_class_id="metal.steel_bare",
        )
    pawl = model.part(
        f"{prefix}__tilt_pawl", meta={"role": "tilt_pawl", "candidate": r.tilt_lock}
    )
    pawl.visual(
        Cylinder(radius=0.0042, length=0.010),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__tilt_pawl__pivot_pin", material_class_id="metal.steel_bare",
    )
    pawl.visual(
        Box((0.030, 0.007, 0.008)),
        origin=Origin(xyz=(-0.015, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__tilt_pawl__arm", material_class_id="metal.blackened_gunmetal",
    )
    pawl.visual(
        Box((0.008, 0.008, 0.009)),
        origin=Origin(xyz=(-0.029, -0.0025, -0.004)),
        material=mats["steel"],
        name=f"{prefix}__tilt_pawl__tooth", material_class_id="metal.steel_bare",
    )
    pawl.visual(
        Cylinder(radius=0.0055, length=0.014),
        origin=Origin(xyz=(0.006, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["polymer"],
        name=f"{prefix}__tilt_pawl__release_grip", material_class_id="plastic.opaque_generic",
    )
    tray.visual(
        Box((0.010, 0.007, 0.030)),
        origin=Origin(xyz=(0.052, 0.0445, 0.019)),
        material=mats["dark"],
        name=f"{prefix}__tray__pawl_boss", material_class_id="metal.blackened_gunmetal",
    )
    tray.visual(
        Box((0.048, 0.036, 0.008)),
        origin=Origin(xyz=(0.034, 0.028, 0.032)),
        material=mats["dark"],
        name=f"{prefix}__tray__pawl_bracket", material_class_id="metal.blackened_gunmetal",
    )
    provider = AxisInterface(
        name=f"{prefix}.pawl_boss",
        point=(0.052, 0.0445, 0.014),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0045,
    )
    consumer = AxisInterface(
        name=f"{prefix}.pawl_pin",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0042,
    )
    mate = mate_axes(provider, consumer)
    joint = f"{prefix}__pawl_release"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=tray,
        child=pawl,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=5.0, velocity=4.0, lower=0.0, upper=0.40),
        meta={"mechanism": "tilt sector pawl release"},
    )
    register_interface_mate(model, joint, mate)


def _add_width_rails(model, r, mats, *, prefix: str, tray) -> None:
    """width_adjustable_tray fork: two captured side rails under the deck."""

    if r.tray_width != "sliding_side_rails":
        return
    stroke = 0.028
    for index, sign in enumerate((-1.0, 1.0)):
        rail = model.part(
            f"{prefix}__side_rail_{index}",
            meta={"role": "tray_side_rail", "station": index},
        )
        rail.visual(
            Box((r.tray_depth_m * 0.70, 0.058, 0.008)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["steel"],
            name=f"{prefix}__side_rail_{index}__blade", material_class_id="metal.steel_bare",
        )
        rail.visual(
            Box((r.tray_depth_m * 0.70, 0.008, 0.014)),
            origin=Origin(xyz=(0.0, sign * 0.029, 0.007)),
            material=mats["dark"],
            name=f"{prefix}__side_rail_{index}__edge_lip", material_class_id="metal.blackened_gunmetal",
        )
        model.articulation(
            f"{prefix}__side_rail_slide_{index}",
            ArticulationType.PRISMATIC,
            parent=tray,
            child=rail,
            origin=Origin(
                xyz=(0.0, sign * (0.5 * r.tray_width_m - 0.020), 0.0335)
            ),
            axis=(0.0, sign, 0.0),
            motion_limits=MotionLimits(effort=60.0, velocity=0.2, lower=0.0, upper=stroke),
            meta={"mechanism": "tray width adjustment"},
        )


def _add_tray(model, r, mats, *, prefix: str, parent, pin_point, joint_name: str,
              bore_radius: float, pin_radius: float, deck_dx: float = 0.0,
              tilt_limits: tuple[float, float] = (-0.22, 0.22)):
    """One perforated deck on a tilt pin, lifted clear of its carrier."""

    tray = model.part(f"{prefix}__tray", meta={"role": "work_tray"})
    tray.visual(
        Cylinder(radius=pin_radius, length=0.052),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__tray__tilt_pin", material_class_id="metal.steel_bare",
    )
    mount_back = -0.022 if deck_dx == 0.0 else -0.006
    tray.visual(
        Box((deck_dx + 0.022 - mount_back, 0.032, 0.038)),
        origin=Origin(xyz=(0.5 * (deck_dx + 0.022 + mount_back), 0.0, 0.019)),
        material=mats["dark"],
        name=f"{prefix}__tray__mount", material_class_id="metal.blackened_gunmetal",
    )
    tray.visual(
        mesh_from_cadquery(
            _tray_deck_shape(r.tray_width_m, r.tray_depth_m, prefix.split("__")[1]),
            f"{prefix}__tray_deck",
            tolerance=0.0010,
        ),
        origin=Origin(xyz=(deck_dx, 0.0, 0.042)),
        material=mats["deck"],
        name=f"{prefix}__tray__deck", material_class_id="metal.patterned_sheet_panel",
    )
    provider = AxisInterface(
        name=f"{prefix}.tray_fork",
        point=pin_point,
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=bore_radius,
    )
    consumer = AxisInterface(
        name=f"{prefix}.tray_pin",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=pin_radius,
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=tray,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=60.0, velocity=1.2, lower=tilt_limits[0], upper=tilt_limits[1]
        ),
        meta={"mechanism": "tray tilt"},
    )
    register_interface_mate(model, joint_name, mate)
    _add_tilt_lock(model, r, mats, prefix=prefix, parent=parent, tray=tray,
                   pin_point=pin_point)
    _add_width_rails(model, r, mats, prefix=prefix, tray=tray)
    return tray


def _tray_head_fixed_tilt_tray_build(model, r, mats, seat):
    candidate = "fixed_tilt_tray"
    prefix = f"tray_head__{candidate}"
    yoke = _add_yoke(model, r, mats, seat, candidate=candidate, post_top=0.050)
    yoke.visual(
        mesh_from_cadquery(
            _fork_shape(
                half_gap=0.022, cheek_t=0.007, cheek_w=0.028,
                cheek_top=0.005, bore_radius=0.0108,
            ),
            f"{prefix}__yoke_fork",
            tolerance=0.0005,
        ),
        origin=Origin(xyz=(0.0, 0.0, _YOKE_POST_H)),
        material=mats["dark"],
        name=f"{prefix}__yoke__tray_fork", material_class_id="metal.blackened_gunmetal",
    )
    return _add_tray(
        model, r, mats, prefix=prefix, parent=yoke,
        pin_point=(0.0, 0.0, _YOKE_POST_H), joint_name=f"{prefix}__tray_tilt",
        bore_radius=0.0108, pin_radius=0.0100,
    )


def _rail_block_shape() -> cq.Workplane:
    """Carriage block bored for two guide rods with real running clearance."""

    block = cq.Workplane("XY").box(0.052, 0.070, 0.024)
    for sign in (-1.0, 1.0):
        block = block.cut(
            cq.Workplane("YZ")
            .circle(0.0063)
            .extrude(0.040, both=True)
            .translate((0.0, sign * 0.026, 0.0))
        )
    stem = cq.Workplane("XY").box(0.034, 0.038, 0.026).translate((0.0, 0.0, 0.023))
    return block.union(stem)


def _tray_head_sliding_rails_build(model, r, mats, seat):
    candidate = "sliding_rails"
    prefix = f"tray_head__{candidate}"
    yoke = _add_yoke(model, r, mats, seat, candidate=candidate, post_top=0.050)
    rail_len = 0.132
    rail_z = 0.070
    for index, sign in enumerate((-1.0, 1.0)):
        yoke.visual(
            Cylinder(radius=0.0055, length=rail_len),
            origin=Origin(
                xyz=(0.0, sign * 0.026, rail_z), rpy=(0.0, math.pi / 2.0, 0.0)
            ),
            material=mats["steel"],
            name=f"{prefix}__yoke__guide_rod_{index}", material_class_id="metal.steel_bare",
        )
    yoke.visual(
        Box((rail_len, 0.030, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, 0.045)),
        material=mats["dark"],
        name=f"{prefix}__yoke__rail_spine", material_class_id="metal.blackened_gunmetal",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        yoke.visual(
            Box((0.010, 0.062, 0.030)),
            origin=Origin(xyz=(sign * (0.5 * rail_len - 0.006), 0.0, 0.055)),
            material=mats["dark"],
            name=f"{prefix}__yoke__rail_bracket_{index}", material_class_id="metal.blackened_gunmetal",
        )

    carriage = model.part(
        f"{prefix}__rail_carriage", meta={"role": "tray_link", "candidate": candidate}
    )
    carriage.visual(
        mesh_from_cadquery(
            _rail_block_shape(), f"{prefix}__rail_block", tolerance=0.0006
        ),
        material=mats["polymer"],
        name=f"{prefix}__rail_carriage__block", material_class_id="plastic.opaque_generic",
    )
    carriage.visual(
        mesh_from_cadquery(
            _fork_shape(
                half_gap=0.022, cheek_t=0.007, cheek_w=0.028,
                cheek_top=0.005, bore_radius=0.0108,
            ),
            f"{prefix}__carriage_fork",
            tolerance=0.0005,
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.048)),
        material=mats["dark"],
        name=f"{prefix}__rail_carriage__tray_fork", material_class_id="metal.blackened_gunmetal",
    )
    # The latch runs in its own plane outboard of the block and the rods.
    carriage.visual(
        Box((0.024, 0.032, 0.010)),
        origin=Origin(xyz=(0.020, 0.042, -0.010)),
        material=mats["dark"],
        name=f"{prefix}__rail_carriage__latch_bracket", material_class_id="metal.blackened_gunmetal",
    )
    carriage.visual(
        mesh_from_cadquery(
            _fork_shape(
                half_gap=0.008, cheek_t=0.005, cheek_w=0.018,
                cheek_top=0.004, bore_radius=0.0053,
            ),
            f"{prefix}__latch_fork",
            tolerance=0.0005,
        ),
        origin=Origin(xyz=(0.026, 0.048, 0.008)),
        material=mats["dark"],
        name=f"{prefix}__rail_carriage__latch_fork", material_class_id="metal.blackened_gunmetal",
    )
    stroke = 0.026
    model.articulation(
        f"{prefix}__tray_slide",
        ArticulationType.PRISMATIC,
        parent=yoke,
        child=carriage,
        origin=Origin(xyz=(0.0, 0.0, rail_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.2, lower=-stroke, upper=stroke),
        meta={"mechanism": "tray reach slide"},
    )

    latch = model.part(
        f"{prefix}__slide_latch", meta={"role": "tray_link", "candidate": candidate}
    )
    latch.visual(
        Cylinder(radius=0.0048, length=0.014),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__slide_latch__pin", material_class_id="metal.steel_bare",
    )
    latch.visual(
        Box((0.032, 0.010, 0.008)),
        origin=Origin(xyz=(-0.017, 0.0, -0.002), rpy=(0.0, 0.14, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__slide_latch__pawl", material_class_id="metal.blackened_gunmetal",
    )
    latch_provider = AxisInterface(
        name=f"{prefix}.latch_fork",
        point=(0.026, 0.048, 0.008),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0053,
    )
    latch_consumer = AxisInterface(
        name=f"{prefix}.latch_pin",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0048,
    )
    latch_mate = mate_axes(latch_provider, latch_consumer)
    latch_joint = f"{prefix}__slide_latch_pivot"
    model.articulation(
        latch_joint,
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=latch,
        origin=latch_mate.origin,
        axis=latch_mate.axis,
        motion_limits=MotionLimits(effort=5.0, velocity=4.0, lower=-0.14, upper=0.14),
        meta={"mechanism": "slide latch pawl"},
    )
    register_interface_mate(model, latch_joint, latch_mate)

    return _add_tray(
        model, r, mats, prefix=prefix, parent=carriage,
        pin_point=(0.0, 0.0, 0.048), joint_name=f"{prefix}__tray_tilt",
        bore_radius=0.0108, pin_radius=0.0100,
    )


def _tray_head_quick_release_dovetail_build(model, r, mats, seat):
    candidate = "quick_release_dovetail"
    prefix = f"tray_head__{candidate}"
    yoke = _add_yoke(model, r, mats, seat, candidate=candidate, post_top=0.058)
    rail_len = 0.128
    rail_z = _YOKE_POST_H
    yoke.visual(
        mesh_from_cadquery(
            _dovetail_rail_shape(rail_len), f"{prefix}__dovetail_rail", tolerance=0.0006
        ),
        origin=Origin(xyz=(-0.5 * rail_len, 0.0, rail_z)),
        material=mats["steel"],
        name=f"{prefix}__yoke__dovetail_rail", material_class_id="metal.steel_bare",
    )
    yoke.visual(
        Box((rail_len, 0.030, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, rail_z - 0.003)),
        material=mats["dark"],
        name=f"{prefix}__yoke__rail_spine", material_class_id="metal.blackened_gunmetal",
    )

    carriage = model.part(
        f"{prefix}__dovetail_carriage", meta={"role": "tray_link", "candidate": candidate}
    )
    carriage.visual(
        mesh_from_cadquery(
            _dovetail_channel_shape(0.056),
            f"{prefix}__dovetail_block",
            tolerance=0.0006,
        ),
        origin=Origin(xyz=(-0.028, 0.0, 0.0)),
        material=mats["polymer"],
        name=f"{prefix}__dovetail_carriage__block", material_class_id="plastic.opaque_generic",
    )
    carriage.visual(
        mesh_from_cadquery(
            _fork_shape(
                half_gap=0.022, cheek_t=0.007, cheek_w=0.028,
                cheek_top=0.005, bore_radius=0.0108,
            ),
            f"{prefix}__carriage_fork",
            tolerance=0.0005,
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.044)),
        material=mats["dark"],
        name=f"{prefix}__dovetail_carriage__tray_fork", material_class_id="metal.blackened_gunmetal",
    )
    carriage.visual(
        Box((0.020, 0.024, 0.014)),
        origin=Origin(xyz=(0.0, 0.032, 0.016)),
        material=mats["dark"],
        name=f"{prefix}__dovetail_carriage__lock_bracket", material_class_id="metal.blackened_gunmetal",
    )
    carriage.visual(
        mesh_from_cadquery(
            _fork_shape(
                half_gap=0.008, cheek_t=0.005, cheek_w=0.018,
                cheek_top=0.004, bore_radius=0.0053, axis="x",
            ),
            f"{prefix}__lock_fork",
            tolerance=0.0005,
        ),
        origin=Origin(xyz=(0.0, 0.042, 0.020)),
        material=mats["dark"],
        name=f"{prefix}__dovetail_carriage__lock_fork", material_class_id="metal.blackened_gunmetal",
    )
    stroke = 0.026
    model.articulation(
        f"{prefix}__dovetail_slide",
        ArticulationType.PRISMATIC,
        parent=yoke,
        child=carriage,
        origin=Origin(xyz=(0.0, 0.0, rail_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.2, lower=-stroke, upper=stroke),
        meta={"mechanism": "quick-release dovetail stroke"},
    )

    lock = model.part(
        f"{prefix}__lock_lever", meta={"role": "tray_link", "candidate": candidate}
    )
    lock.visual(
        Cylinder(radius=0.0048, length=0.012),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__lock_lever__pin", material_class_id="metal.steel_bare",
    )
    lock.visual(
        Box((0.009, 0.032, 0.008)),
        origin=Origin(xyz=(0.0, 0.017, 0.0)),
        material=mats["dark"],
        name=f"{prefix}__lock_lever__tab", material_class_id="metal.blackened_gunmetal",
    )
    lock_provider = AxisInterface(
        name=f"{prefix}.lock_fork",
        point=(0.0, 0.042, 0.020),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0053,
    )
    lock_consumer = AxisInterface(
        name=f"{prefix}.lock_pin",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0048,
    )
    lock_mate = mate_axes(lock_provider, lock_consumer)
    lock_joint = f"{prefix}__lock_lever_pivot"
    model.articulation(
        lock_joint,
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=lock,
        origin=lock_mate.origin,
        axis=lock_mate.axis,
        motion_limits=MotionLimits(effort=6.0, velocity=4.0, lower=-0.22, upper=0.22),
        meta={"mechanism": "dovetail lock lever"},
    )
    register_interface_mate(model, lock_joint, lock_mate)

    return _add_tray(
        model, r, mats, prefix=prefix, parent=carriage,
        pin_point=(0.0, 0.0, 0.044), joint_name=f"{prefix}__tray_tilt",
        bore_radius=0.0108, pin_radius=0.0100,
    )


def _tray_head_foldaway_hinge_build(model, r, mats, seat):
    """foldaway_tray_hinge fork L370-L470: the deck parks vertically on a rear hinge."""

    candidate = "foldaway_hinge"
    prefix = f"tray_head__{candidate}"
    yoke = _add_yoke(model, r, mats, seat, candidate=candidate, post_top=0.054)
    hinge_z = _YOKE_POST_H
    yoke.visual(
        Box((0.036, 0.044, 0.010)),
        origin=Origin(xyz=(-0.020, 0.0, hinge_z - 0.020)),
        material=mats["powder"],
        name=f"{prefix}__yoke__fold_bracket", material_class_id="metal.paint_coated",
    )
    yoke.visual(
        mesh_from_cadquery(
            _fork_shape(
                half_gap=0.022, cheek_t=0.007, cheek_w=0.030,
                cheek_top=0.006, bore_radius=0.0108,
            ),
            f"{prefix}__fold_fork",
            tolerance=0.0005,
        ),
        origin=Origin(xyz=(0.0, 0.0, hinge_z)),
        material=mats["dark"],
        name=f"{prefix}__yoke__fold_fork", material_class_id="metal.blackened_gunmetal",
    )
    yoke.visual(
        Cylinder(radius=0.019, length=0.005),
        origin=Origin(xyz=(0.0, -0.0305, hinge_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name=f"{prefix}__yoke__detent_plate", material_class_id="metal.steel_bare",
    )
    for index, angle in enumerate((0.0, -0.72, -1.42)):
        yoke.visual(
            Cylinder(radius=0.0035, length=0.006),
            origin=Origin(
                xyz=(
                    0.0155 * math.cos(angle),
                    -0.0345,
                    hinge_z - 0.0155 * math.sin(angle),
                ),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["polymer"],
            name=f"{prefix}__yoke__detent_boss_{index}", material_class_id="plastic.opaque_generic",
        )
    # The hinge sits at the deck's rear edge, so parking the deck swings it up
    # and back instead of down into the arm.
    return _add_tray(
        model, r, mats, prefix=prefix, parent=yoke,
        pin_point=(0.0, 0.0, hinge_z), joint_name=f"{prefix}__tray_fold",
        bore_radius=0.0108, pin_radius=0.0100,
        deck_dx=0.5 * r.tray_depth_m - 0.010,
        tilt_limits=(-1.35, 0.0),
    )


_TRAY_BUILDERS = {
    "fixed_tilt_tray": _tray_head_fixed_tilt_tray_build,
    "sliding_rails": _tray_head_sliding_rails_build,
    "quick_release_dovetail": _tray_head_quick_release_dovetail_build,
    "foldaway_hinge": _tray_head_foldaway_hinge_build,
}


_CLAMP_BUILDERS: dict[str, object] = {}


def _clamp_form_single_screw_build(model, r, mats, frame):
    _build_clamp_screws(model, r, mats, frame)


def _clamp_form_dual_screw_build(model, r, mats, frame):
    _build_clamp_screws(model, r, mats, frame)


def _clamp_form_overcenter_cam_build(model, r, mats, frame):
    """overcenter_cam fork L118-L236: a cam lever drives the jaw instead of a screw."""

    station = r.station_x_m[0]
    follower = model.part(
        "clamp__cam_follower", meta={"role": "clamp_follower", "station": 0}
    )
    follower.visual(
        Cylinder(radius=0.0055, length=0.072),
        origin=Origin(xyz=(0.0, 0.0, -0.027)),
        material=mats["steel"],
        name="clamp__cam_follower__stem", material_class_id="metal.steel_bare",
    )
    follower.visual(
        Box((0.034, 0.034, 0.016)),
        origin=Origin(xyz=(0.0, 0.0, -0.055)),
        material=mats["dark"],
        name="clamp__cam_follower__carriage", material_class_id="metal.blackened_gunmetal",
    )
    follower.visual(
        Cylinder(radius=0.006, length=0.024),
        origin=Origin(xyz=(-0.022, 0.0, -0.060), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="clamp__cam_follower__roller", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "clamp__cam_follower_slide_0",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=follower,
        origin=Origin(xyz=(station, 0.0, r.beam_top_m)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=900.0, velocity=0.05, lower=r.spindle_dn_m, upper=r.spindle_up_m
        ),
        meta={"mechanism": "cam-driven clamp travel"},
    )

    shoe = model.part(
        "clamp__pressure_pad_0", meta={"role": "clamp_shoe", "station": 0}
    )
    shoe.visual(
        Cylinder(radius=0.016, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
        material=mats["dark"],
        name="clamp__pressure_pad_0__plate", material_class_id="metal.blackened_gunmetal",
    )
    shoe.visual(
        Cylinder(radius=0.015, length=0.003),
        origin=Origin(xyz=(0.0, 0.0, 0.0075)),
        material=mats["rubber"],
        name="clamp__pressure_pad_0__face", material_class_id="rubber.smooth_plain",
    )
    shoe_provider = AxisInterface(
        name="clamp.cam_shoe_seat",
        point=(0.0, 0.0, 0.010),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0055,
    )
    shoe_consumer = AxisInterface(
        name="clamp.cam_shoe_hub",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0055,
    )
    shoe_mate = mate_axes(shoe_provider, shoe_consumer)
    model.articulation(
        "clamp__pad_swivel_0",
        ArticulationType.CONTINUOUS,
        parent=follower,
        child=shoe,
        origin=shoe_mate.origin,
        axis=shoe_mate.axis,
        motion_limits=MotionLimits(effort=20.0, velocity=6.0),
        meta={"mechanism": "self-aligning pressure shoe"},
    )
    register_interface_mate(model, "clamp__pad_swivel_0", shoe_mate)

    pivot = (station - 0.050, 0.0, -0.064)
    for index, sign in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.020, 0.007, 0.070)),
            origin=Origin(xyz=(pivot[0], sign * 0.013, -0.032)),
            material=mats["powder"],
            name=f"clamp__frame__cam_cheek_{index}", material_class_id="metal.paint_coated",
        )
    lever = model.part("clamp__cam_lever", meta={"role": "clamp_cam_lever"})
    lever.visual(
        Cylinder(radius=0.0055, length=0.021),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="clamp__cam_lever__pivot_shaft", material_class_id="metal.steel_bare",
    )
    lever.visual(
        Box((0.020, 0.012, 0.012)),
        origin=Origin(xyz=(0.011, 0.0, 0.003)),
        material=mats["dark"],
        name="clamp__cam_lever__lobe", material_class_id="metal.blackened_gunmetal",
    )
    lever.visual(
        Box((0.052, 0.014, 0.010)),
        origin=Origin(xyz=(-0.026, 0.0, -0.004)),
        material=mats["polymer"],
        name="clamp__cam_lever__arm", material_class_id="plastic.opaque_generic",
    )
    lever.visual(
        Cylinder(radius=0.0085, length=0.022),
        origin=Origin(xyz=(-0.054, 0.0, -0.004), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["rubber"],
        name="clamp__cam_lever__grip", material_class_id="rubber.smooth_plain",
    )
    lever_provider = AxisInterface(
        name="clamp.cam_pivot",
        point=pivot,
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0058,
    )
    lever_consumer = AxisInterface(
        name="clamp.cam_shaft",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0055,
    )
    lever_mate = mate_axes(lever_provider, lever_consumer)
    model.articulation(
        "clamp__cam_lever_swing",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=lever,
        origin=lever_mate.origin,
        axis=lever_mate.axis,
        motion_limits=MotionLimits(effort=45.0, velocity=2.0, lower=-1.25, upper=0.0),
        meta={"mechanism": "over-centre cam clamp lever"},
    )
    register_interface_mate(model, "clamp__cam_lever_swing", lever_mate)


_CLAMP_BUILDERS = {
    "single_screw": _clamp_form_single_screw_build,
    "dual_screw": _clamp_form_dual_screw_build,
    "overcenter_cam": _clamp_form_overcenter_cam_build,
}


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


def build_picturex_0611_ergonomic_clamp_with_adjustable_components(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model)
    frame = _build_clamp(model, r, mats)
    _CLAMP_BUILDERS[r.clamp_form](model, r, mats, frame)
    _build_column(model, r, mats, frame)
    seat = _ARM_BUILDERS[r.arm_form](model, r, mats)
    _TRAY_BUILDERS[r.tray_head](model, r, mats, seat)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["source_family"] = "pictureX/0611/ergonomic_clamp_with_adjustable_components"
    return model


def build_seeded_picturex_0611_ergonomic_clamp_with_adjustable_components(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_picturex_0611_ergonomic_clamp_with_adjustable_components(
        config_from_seed(seed), assets=assets
    )


def _centre(box):
    if box is None:
        return None
    return tuple(0.5 * (box[0][i] + box[1][i]) for i in range(3))


def run_picturex_0611_ergonomic_clamp_with_adjustable_components_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()

    roles: dict[str | None, list] = {}
    for part in object_model.parts:
        roles.setdefault(part.meta.get("role"), []).append(part)

    expected_stations = len(r.station_x_m)
    cam_clamp = r.clamp_form == "overcenter_cam"
    expected_screws = 0 if cam_clamp else expected_stations
    ctx.check(
        "clamp keeps one screw station per source throat",
        len(roles.get("clamp_frame", [])) == 1
        and len(roles.get("clamp_screw", [])) == expected_screws
        and len(roles.get("clamp_shoe", [])) == expected_stations
        and len(roles.get("clamp_cam_lever", [])) == (1 if cam_clamp else 0)
        and len(roles.get("clamp_follower", [])) == (1 if cam_clamp else 0),
        details=(
            f"stations={expected_stations}, screws={len(roles.get('clamp_screw', []))}, "
            f"shoes={len(roles.get('clamp_shoe', []))}, form={r.clamp_form}"
        ),
    )
    ctx.check(
        "post and height carriage are always present",
        len(roles.get("height_carriage", [])) == 1
        and len(roles.get("post_lock", [])) == 1
        and len(roles.get("carriage_lock", [])) == 1,
    )
    ctx.check(
        "domain choices are recorded",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )

    frame = object_model.get_part("clamp__frame")
    carriage = object_model.get_part("clamp__carriage")

    for index in range(expected_stations):
        shoe = object_model.get_part(f"clamp__pressure_pad_{index}")
        adjust = object_model.get_articulation(
            f"clamp__cam_follower_slide_{index}" if cam_clamp
            else f"clamp__spindle_adjust_{index}"
        )
        top = ctx.part_element_world_aabb(frame, elem=f"clamp__frame__jaw_pad_{index}")
        bottom = ctx.part_element_world_aabb(shoe, elem=f"clamp__pressure_pad_{index}__face")
        rest_gap = None if top is None or bottom is None else top[0][2] - bottom[1][2]
        with ctx.pose({adjust: adjust.motion_limits.upper}):
            top_c = ctx.part_element_world_aabb(frame, elem=f"clamp__frame__jaw_pad_{index}")
            bot_c = ctx.part_element_world_aabb(
                shoe, elem=f"clamp__pressure_pad_{index}__face"
            )
            closed_gap = None if top_c is None or bot_c is None else top_c[0][2] - bot_c[1][2]
        ctx.check(
            f"clamp station {index} closes its throat on the source screw axis",
            rest_gap is not None
            and closed_gap is not None
            and rest_gap > 0.008
            and closed_gap < rest_gap - 0.006
            and closed_gap > -0.001,
            details=f"rest={rest_gap}, closed={closed_gap}",
        )

    height = object_model.get_articulation("clamp__carriage_height")
    low = _centre(ctx.part_world_aabb(carriage))
    with ctx.pose({height: height.motion_limits.upper}):
        high = _centre(ctx.part_world_aabb(carriage))
    ctx.check(
        "height carriage rises along the upright post",
        low is not None
        and high is not None
        and high[2] > low[2] + 0.010
        and abs(high[0] - low[0]) < 0.002,
        details=f"low={low}, high={high}",
    )

    arms = roles.get("support_arm", [])
    ctx.check(
        "one source-backed arm structure carries the head",
        len(arms) == 1 and arms[0].meta.get("candidate") == r.arm_form,
        details=f"arms={[part.name for part in arms]}",
    )

    yokes = roles.get("tray_yoke", [])
    trays = roles.get("work_tray", [])
    ctx.check(
        "tray head keeps one yaw yoke and one work tray",
        len(yokes) == 1 and len(trays) == 1,
        details=f"yokes={len(yokes)}, trays={len(trays)}",
    )
    tray = trays[0] if trays else None
    deck = (
        ctx.part_element_world_aabb(tray, elem=f"tray_head__{r.tray_head}__tray__mount")
        if tray is not None
        else None
    )
    tray_aabb = ctx.part_world_aabb(tray) if tray is not None else None
    tray_size = (
        None if tray_aabb is None else tuple(tray_aabb[1][i] - tray_aabb[0][i] for i in range(3))
    )
    ctx.check(
        "work tray keeps the source deck footprint",
        tray_size is not None
        and tray_size[1] > r.tray_width_m * 0.80
        and tray_size[0] > r.tray_depth_m * 0.70,
        details=f"tray_size={tray_size}, deck={deck}",
    )
    if tray is not None:
        ctx.expect_origin_gap(
            tray,
            frame,
            axis="z",
            min_gap=0.05,
            name="the arm holds the tray above the clamp head",
        )

    rails = roles.get("tray_side_rail", [])
    ctx.check(
        "tray width interface matches the selected deck",
        len(rails) == (2 if r.tray_width == "sliding_side_rails" else 0),
        details=f"tray_width={r.tray_width}, rails={[part.name for part in rails]}",
    )
    if rails:
        slide = object_model.get_articulation(
            f"tray_head__{r.tray_head}__side_rail_slide_0"
        )
        narrow = _centre(ctx.part_world_aabb(rails[0]))
        with ctx.pose({slide: slide.motion_limits.upper}):
            wide = _centre(ctx.part_world_aabb(rails[0]))
        ctx.check(
            "side rails really widen the tray support",
            narrow is not None and wide is not None and abs(wide[1] - narrow[1]) > 0.020,
            details=f"narrow={narrow}, wide={wide}",
        )
    pawls = roles.get("tilt_pawl", [])
    ctx.check(
        "tray tilt lock matches the selected mechanism",
        len(pawls) == (1 if r.tilt_lock == "sector_pawl" else 0),
        details=f"tilt_lock={r.tilt_lock}, pawls={[part.name for part in pawls]}",
    )

    yaw = object_model.get_articulation(f"tray_head__{r.tray_head}__head_yaw")
    rest_box = ctx.part_world_aabb(tray) if tray is not None else None
    with ctx.pose({yaw: yaw.motion_limits.upper}):
        swung_box = ctx.part_world_aabb(tray) if tray is not None else None
    # The deck is centred on the yaw axis, so a turned head is proved by the
    # swept plan extent changing while the deck stays at the same height.
    rest_span = None if rest_box is None else rest_box[1][1] - rest_box[0][1]
    swung_span = None if swung_box is None else swung_box[1][1] - swung_box[0][1]
    ctx.check(
        "head yaw turns the tray about a vertical axis",
        rest_span is not None
        and swung_span is not None
        and abs(swung_span - rest_span) > 0.010
        and abs(_centre(swung_box)[2] - _centre(rest_box)[2]) < 0.020,
        details=f"rest_span={rest_span}, swung_span={swung_span}",
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
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "smallest_clamp_shortest_arm_smallest_tray",
        {
            "clamp_throat_m": 0.038,
            "clamp_width_m": 0.052,
            "post_height_m": 0.130,
            "arm_reach_m": 0.170,
            "tray_width_m": 0.190,
            "tray_depth_m": 0.150,
        },
        reason="tightest frame, shortest post and arm and the smallest deck together",
    ),
    corner_case(
        "largest_clamp_longest_arm_largest_tray",
        {
            "clamp_throat_m": 0.062,
            "clamp_width_m": 0.086,
            "post_height_m": 0.230,
            "arm_reach_m": 0.300,
            "tray_width_m": 0.300,
            "tray_depth_m": 0.230,
        },
        reason="widest frame, tallest post, longest arm and the largest deck together",
    ),
    corner_case(
        "largest_tray_on_shortest_arm",
        {
            "clamp_throat_m": 0.062,
            "clamp_width_m": 0.052,
            "post_height_m": 0.130,
            "arm_reach_m": 0.170,
            "tray_width_m": 0.300,
            "tray_depth_m": 0.230,
        },
        reason="the heaviest deck overhang on the shortest support",
    ),
    corner_case(
        "tallest_post_with_smallest_tray",
        {
            "clamp_throat_m": 0.038,
            "clamp_width_m": 0.086,
            "post_height_m": 0.230,
            "arm_reach_m": 0.300,
            "tray_width_m": 0.190,
            "tray_depth_m": 0.150,
        },
        reason="longest carriage stroke with the longest arm and the smallest deck",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_picturex_0611_ergonomic_clamp_with_adjustable_components",
    "build_seeded_picturex_0611_ergonomic_clamp_with_adjustable_components",
    "config_from_seed",
    "resolve_config",
    "run_picturex_0611_ergonomic_clamp_with_adjustable_components_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
