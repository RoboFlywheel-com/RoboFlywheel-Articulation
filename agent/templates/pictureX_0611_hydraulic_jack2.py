# SPDX-License-Identifier: Apache-2.0

"""Self-contained wheeled hydraulic floor (trolley) jack template.

One rigid ``jack_chassis`` root carries the side frames, the ram cylinder, the
front roller stubs and the rear station brackets.  The ``lift_arm`` is a
REVOLUTE (+x) child of the chassis at the rear pivot and is the only independent
lift joint.  The ``saddle_head`` is a REVOLUTE (+x) child of the arm nose
mimicking the arm at multiplier ``-1`` -- that is the real parallel linkage which
keeps a floor-jack head level through the whole lift, and it is what makes the
closed loop exact inside a URDF tree.  The ram piston is a PRISMATIC child of the
chassis mimicking the same driver, sliding inside a real cylinder bore.

Two ``front_roller`` wheels are CONTINUOUS (+x).  ``rear_station_count``
``wheel_station`` parts carry the rear on a cross beam that widens with the
station count, each station either a swivel caster (REVOLUTE kingpin about +z
plus a CONTINUOUS wheel) or a rigid roller (CONTINUOUS only).

Four component slots vary without touching the mechanism: ``saddle_head``,
``chassis_style``, ``pump_drive`` and ``wheel_station``.  No source-replay
import, no motion clamping, no whole-part overlap allowance.
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
    Cylinder,
    LatheGeometry,
    Mimic,
    MotionLimits,
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
)

SaddleHead = Literal["disc_saddle", "screw_post", "vee_cradle", "wide_platform"]
ChassisStyle = Literal["plate_frame", "low_profile", "boxed_frame"]
PumpDrive = Literal["lever_handle", "air_over_hydraulic"]
WheelStation = Literal["swivel_caster", "fixed_roller"]
PaletteStyle = Literal["jack_blue", "works_red", "graphite", "safety_yellow"]

SADDLE_HEADS: tuple[SaddleHead, ...] = ("disc_saddle", "screw_post", "vee_cradle", "wide_platform")
CHASSIS_STYLES: tuple[ChassisStyle, ...] = ("plate_frame", "low_profile", "boxed_frame")
PUMP_DRIVES: tuple[PumpDrive, ...] = ("lever_handle", "air_over_hydraulic")
WHEEL_STATIONS: tuple[WheelStation, ...] = ("swivel_caster", "fixed_roller")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("jack_blue", "works_red", "graphite", "safety_yellow")


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("saddle_head", SADDLE_HEADS),
        component_slot("chassis_style", CHASSIS_STYLES),
        component_slot("pump_drive", PUMP_DRIVES),
        component_slot("wheel_station", WHEEL_STATIONS),
        multiplicity_slot("rear_station_count", (2, 3, 4), item_slot="wheel_station"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "jack_blue": {
        "paint": (0.11, 0.26, 0.56, 1.0),
        "edge": (0.05, 0.14, 0.32, 1.0),
        "steel": (0.42, 0.45, 0.48, 1.0),
        "chrome": (0.74, 0.77, 0.80, 1.0),
        "dark": (0.08, 0.09, 0.10, 1.0),
        "rubber": (0.05, 0.05, 0.06, 1.0),
    },
    "works_red": {
        "paint": (0.70, 0.14, 0.12, 1.0),
        "edge": (0.44, 0.08, 0.07, 1.0),
        "steel": (0.38, 0.39, 0.41, 1.0),
        "chrome": (0.76, 0.78, 0.80, 1.0),
        "dark": (0.09, 0.08, 0.08, 1.0),
        "rubber": (0.06, 0.05, 0.05, 1.0),
    },
    "graphite": {
        "paint": (0.24, 0.25, 0.27, 1.0),
        "edge": (0.13, 0.14, 0.15, 1.0),
        "steel": (0.48, 0.50, 0.52, 1.0),
        "chrome": (0.80, 0.82, 0.84, 1.0),
        "dark": (0.07, 0.07, 0.08, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
    },
    "safety_yellow": {
        "paint": (0.92, 0.72, 0.10, 1.0),
        "edge": (0.62, 0.46, 0.05, 1.0),
        "steel": (0.36, 0.37, 0.39, 1.0),
        "chrome": (0.78, 0.80, 0.83, 1.0),
        "dark": (0.09, 0.09, 0.09, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
    },
}


# Lift-arm angle band.  The arm is AUTHORED at ARM0, so the driver runs
# 0 .. ARM1-ARM0 and its neutral pose is the fully-lowered jack.  ARM0 also has
# to lift the head's mount risers clear of the frame's top rail at rest: at
# 0.10 rad a short arm on a short chassis left them straddling the rolled edge.
ARM0 = 0.16
ARM1 = 0.88
RW = 0.038               # wheel radius
WHEEL_T = 0.024          # wheel width
# The frame underside clears the top of every wheel, so nothing spanning the
# track can sit inside a wheel; the kingpin drop follows from that.
CHASSIS_Z0 = 2.0 * RW + 0.026
CASTER_DROP = CHASSIS_Z0 - RW
# Wheels stand outboard of the frame skin, and a hanger/stub reaches out to
# within MOUNT of the wheel face: real bearing contact, no interpenetration.
WHEEL_X_OFFSET = 0.006 + WHEEL_T * 0.5 + 0.004
ARM_PLATE_T = 0.012
ARM_PLATE_H = 0.034
NOSE_R = 0.013           # arm nose tube radius
# The head hangs on two lugs bored CONCENTRIC with the nose tube, so contact
# with the arm survives the head counter-rotating through the whole lift; its
# body rides risers above the arm plate tops.
HEAD_LIFT = ARM_PLATE_H * 0.5 + 0.013
CHASSIS_PLATE_T = 0.012
CHASSIS_H = 0.076
# Minimum pitch between rear stations: a swivelling wheel sweeps a circle of
# radius RW about its kingpin, so neighbours need more than 2*RW between them.
STATION_PITCH = 0.105
PUMP_EAR_X = 0.022     # clevis ear centre offset in x
PUMP_EAR_T = 0.012     # clevis ear thickness in x
CLEVIS_PIN_LEN = 2.0 * (PUMP_EAR_X - PUMP_EAR_T * 0.5 + 0.0006)
# Sub-millimetre lap: a fitting laps its host by less than the collision
# tolerance so QC reads real contact without an overlap allowance.
MOUNT = 0.0006


@dataclass(frozen=True)
class Config:
    saddle_head: SaddleHead = "disc_saddle"
    chassis_style: ChassisStyle = "plate_frame"
    pump_drive: PumpDrive = "lever_handle"
    wheel_station: WheelStation = "swivel_caster"
    rear_station_count: int = 2
    chassis_len_m: float | None = None
    chassis_width_m: float | None = None
    arm_reach_ratio: float | None = None
    palette_style: PaletteStyle = "jack_blue"
    name: str = "pictureX_0611_hydraulic_jack2"


@dataclass(frozen=True)
class ResolvedConfig:
    saddle_head: SaddleHead
    chassis_style: ChassisStyle
    pump_drive: PumpDrive
    wheel_station: WheelStation
    rear_station_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    chassis_len_m: float
    chassis_width_m: float
    arm_reach_ratio: float
    arm_len_m: float
    arm_travel_rad: float
    lift_height_m: float
    side_x: float
    arm_x: float
    chassis_z0: float
    chassis_top_z: float
    pivot_y: float
    pivot_z: float
    front_axle_y: float
    rear_axle_y: float
    rear_track: float
    station_x: tuple[float, ...]
    ram_z: float
    ram_len_m: float
    ram_stroke_m: float
    handle_pivot_y: float
    handle_pivot_z: float
    handle_len_m: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0xF100_2ACC)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        saddle_head=choices["saddle_head"],
        chassis_style=choices["chassis_style"],
        pump_drive=choices["pump_drive"],
        wheel_station=choices["wheel_station"],
        rear_station_count=choices["rear_station_count"],
        chassis_len_m=round(rng.uniform(0.55, 1.05), 4),
        chassis_width_m=round(rng.uniform(0.22, 0.40), 4),
        arm_reach_ratio=round(rng.uniform(0.60, 0.82), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"hydraulic_jack2_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "saddle_head": config.saddle_head,
            "chassis_style": config.chassis_style,
            "pump_drive": config.pump_drive,
            "wheel_station": config.wheel_station,
            "rear_station_count": config.rear_station_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.chassis_len_m is not None and not 0.55 <= float(config.chassis_len_m) <= 1.05:
        raise ValueError("chassis_len_m must be in [0.55, 1.05]")
    if config.chassis_width_m is not None and not 0.22 <= float(config.chassis_width_m) <= 0.40:
        raise ValueError("chassis_width_m must be in [0.22, 0.40]")
    if config.arm_reach_ratio is not None and not 0.60 <= float(config.arm_reach_ratio) <= 0.82:
        raise ValueError("arm_reach_ratio must be in [0.60, 0.82]")

    length = _clamp(config.chassis_len_m, 0.55, 1.05) if config.chassis_len_m is not None else 0.80
    width = _clamp(config.chassis_width_m, 0.22, 0.40) if config.chassis_width_m is not None else 0.30
    ratio = _clamp(config.arm_reach_ratio, 0.60, 0.82) if config.arm_reach_ratio is not None else 0.70

    arm_len = length * ratio
    travel = ARM1 - ARM0
    lift = arm_len * (math.sin(ARM1) - math.sin(ARM0))

    side_x = width * 0.5 - CHASSIS_PLATE_T
    # Host adaptation: a boxed frame's side boxes reach 22 mm inboard of the
    # frame station, a plate frame only 6 mm, so the arm station follows the
    # real inner face rather than a fixed inset.
    inner_face = side_x - (0.022 if config.chassis_style == "boxed_frame" else 0.006)
    arm_x = inner_face - 0.016
    chassis_z0 = CHASSIS_Z0
    chassis_top = chassis_z0 + CHASSIS_H
    pivot_y = -length * 0.5 + 0.090
    pivot_z = chassis_z0 + 0.046
    front_axle_y = length * 0.5 - 0.055
    rear_axle_y = -length * 0.5 + 0.055

    n = int(config.rear_station_count)
    # Host adaptation: the rear cross beam widens so neighbouring swivel wheels
    # never sweep into each other, instead of cramming N stations into the frame.
    rear_track = max(width + 0.020, (n - 1) * STATION_PITCH + 0.060)
    if n == 1:
        xs = (0.0,)
    else:
        half = rear_track * 0.5 - 0.030
        xs = tuple(-half + 2.0 * half * i / (n - 1) for i in range(n))

    # Rod bottom laps the pan top by MOUNT: carried by it, not buried in it.
    ram_z = chassis_z0 + 0.012 + 0.0172 - MOUNT
    ram_len = length * 0.30
    ram_stroke = length * 0.10
    handle_pivot_y = -length * 0.5 + 0.048
    handle_pivot_z = chassis_top + 0.018
    handle_len = length * 0.62

    return ResolvedConfig(
        saddle_head=config.saddle_head,
        chassis_style=config.chassis_style,
        pump_drive=config.pump_drive,
        wheel_station=config.wheel_station,
        rear_station_count=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        chassis_len_m=length,
        chassis_width_m=width,
        arm_reach_ratio=ratio,
        arm_len_m=arm_len,
        arm_travel_rad=travel,
        lift_height_m=lift,
        side_x=side_x,
        arm_x=arm_x,
        chassis_z0=chassis_z0,
        chassis_top_z=chassis_top,
        pivot_y=pivot_y,
        pivot_z=pivot_z,
        front_axle_y=front_axle_y,
        rear_axle_y=rear_axle_y,
        rear_track=rear_track,
        station_x=xs,
        ram_z=ram_z,
        ram_len_m=ram_len,
        ram_stroke_m=ram_stroke,
        handle_pivot_y=handle_pivot_y,
        handle_pivot_z=handle_pivot_z,
        handle_len_m=handle_len,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("saddle_head", config.saddle_head),
        ("chassis_style", config.chassis_style),
        ("pump_drive", config.pump_drive),
        ("wheel_station", config.wheel_station),
        ("rear_station_count", config.rear_station_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"jack2_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"jack2_{r.palette_style}_{key}"
    return mats


def _tube(name: str, outer_r: float, inner_r: float, z0: float, z1: float, segments: int = 24):
    return mesh_from_geometry(
        LatheGeometry.from_shell_profiles(
            [(outer_r, z0), (outer_r, z1)],
            [(inner_r, z0), (inner_r, z1)],
            segments=segments,
        ),
        name,
    )


def _x_cyl(part, name: str, radius: float, length: float, xyz, material: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _y_cyl(part, name: str, radius: float, length: float, xyz, material: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    provider_radial: tuple[float, float, float],
    consumer_radial: tuple[float, float, float],
    effort: float,
    velocity: float,
    lower: float = 0.0,
    upper: float = 0.0,
    articulation_type: ArticulationType = ArticulationType.REVOLUTE,
    mimic: Mimic | None = None,
) -> None:
    provider = AxisInterface(name=f"{name}__provider", point=point, axis=axis, radial=provider_radial)
    consumer = AxisInterface(name=f"{name}__consumer", axis=axis, radial=consumer_radial)
    mate = mate_axes(provider, consumer)
    if articulation_type == ArticulationType.CONTINUOUS:
        limits = MotionLimits(effort=effort, velocity=velocity)
    else:
        limits = MotionLimits(lower=lower, upper=upper, effort=effort, velocity=velocity)
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


# --- chassis style candidates ----------------------------------------------
def _chassis_style_plate_frame_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    length = r.chassis_len_m
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * r.side_x
        frame.visual(
            Box((CHASSIS_PLATE_T, length, CHASSIS_H)),
            origin=Origin(xyz=(x, 0.0, r.chassis_z0 + CHASSIS_H * 0.5)),
            material=mats["paint"],
            name=f"chassis_style__plate_frame__side_{side}", material_class_id="metal.paint_coated",
        )
        # Rolled top edge of the pressed side plate.
        frame.visual(
            Box((CHASSIS_PLATE_T + 0.010, length, 0.009)),
            origin=Origin(xyz=(x - sx * 0.005, 0.0, r.chassis_top_z - 0.0045)),
            material=mats["edge"],
            name=f"chassis_style__plate_frame__rolled_edge_{side}", material_class_id="metal.paint_coated",
        )


def _chassis_style_low_profile_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    length = r.chassis_len_m
    low_h = CHASSIS_H * 0.66
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * r.side_x
        frame.visual(
            Box((CHASSIS_PLATE_T, length, low_h)),
            origin=Origin(xyz=(x, 0.0, r.chassis_z0 + low_h * 0.5)),
            material=mats["paint"],
            name=f"chassis_style__low_profile__side_{side}", material_class_id="metal.paint_coated",
        )
        # Raised rear hump carrying the arm pivot and the pump socket.
        frame.visual(
            Box((CHASSIS_PLATE_T, length * 0.34, CHASSIS_H)),
            origin=Origin(
                xyz=(x, -length * 0.5 + length * 0.17, r.chassis_z0 + CHASSIS_H * 0.5)
            ),
            material=mats["paint"],
            name=f"chassis_style__low_profile__rear_hump_{side}", material_class_id="metal.paint_coated",
        )
    # Tapered low nose reaching under a low sill; it laps the frame front so the
    # whole nose stays one solid with the pan.
    frame.visual(
        Box((2.0 * r.side_x, length * 0.16, 0.010)),
        origin=Origin(xyz=(0.0, length * 0.5 + length * 0.08 - 0.010, r.chassis_z0 + 0.005)),
        material=mats["edge"],
        name="chassis_style__low_profile__nose_deck", material_class_id="metal.paint_coated",
    )


def _chassis_style_boxed_frame_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    length = r.chassis_len_m
    for side, sx in enumerate((-1.0, 1.0)):
        x = sx * (r.side_x - 0.008)
        frame.visual(
            Box((0.028, length, CHASSIS_H)),
            origin=Origin(xyz=(x, 0.0, r.chassis_z0 + CHASSIS_H * 0.5)),
            material=mats["paint"],
            name=f"chassis_style__boxed_frame__side_box_{side}", material_class_id="metal.paint_coated",
        )
        frame.visual(
            Box((0.034, length * 0.9, 0.010)),
            origin=Origin(xyz=(x, 0.0, r.chassis_top_z - 0.005)),
            material=mats["edge"],
            name=f"chassis_style__boxed_frame__box_cap_{side}", material_class_id="metal.paint_coated",
        )
    # Deep cross decks tying the two boxes together.  They leave a central
    # corridor so the ram rod and its eye run clear, and stop below the band the
    # lift-arm plates sweep.
    for side, sx in enumerate((-1.0, 1.0)):
        inner = 0.034
        frame.visual(
            Box((r.side_x - inner, length * 0.36, 0.014)),
            origin=Origin(
                xyz=(sx * 0.5 * (r.side_x + inner), 0.0, r.chassis_z0 + 0.017)
            ),
            material=mats["edge"],
            name=f"chassis_style__boxed_frame__cross_deck_{side}", material_class_id="metal.paint_coated",
        )


_CHASSIS_BUILDERS = {
    "plate_frame": _chassis_style_plate_frame_build,
    "low_profile": _chassis_style_low_profile_build,
    "boxed_frame": _chassis_style_boxed_frame_build,
}


# --- chassis ----------------------------------------------------------------
def _build_chassis(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    frame = model.part("jack_chassis", meta={"role": "jack_chassis"})
    length = r.chassis_len_m
    # Floor pan tying both sides together; everything else laps into it.
    frame.visual(
        Box((2.0 * r.side_x + CHASSIS_PLATE_T, length, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, r.chassis_z0 + 0.006)),
        material=mats["steel"],
        name="chassis_floor_pan", material_class_id="metal.steel_bare",
    )
    _CHASSIS_BUILDERS[r.chassis_style](frame, r, mats)

    # Rear cross beam carrying the wheel stations; it widens with the count.
    frame.visual(
        Box((r.rear_track, 0.038, 0.018)),
        origin=Origin(xyz=(0.0, r.rear_axle_y, r.chassis_z0 + 0.007)),
        material=mats["edge"],
        name="rear_cross_beam", material_class_id="metal.paint_coated",
    )
    # Arm pivot lugs straddling the arm plates.
    lug_h = r.pivot_z - r.chassis_z0 + 0.024
    for side, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.012, 0.042, lug_h)),
            origin=Origin(
                xyz=(
                    sx * (r.arm_x + ARM_PLATE_T * 0.5 + 0.007),
                    r.pivot_y,
                    r.chassis_z0 + lug_h * 0.5,
                )
            ),
            material=mats["steel"],
            name=f"arm_pivot_lug_{side}", material_class_id="metal.steel_bare",
        )
    # Ram cylinder: a real bore the piston runs in, lying under the arm.
    frame.visual(
        _tube("ram_cylinder", 0.024, 0.018, 0.0, r.ram_len_m, 24),
        origin=Origin(
            xyz=(0.0, r.pivot_y + 0.030, r.ram_z),
            rpy=(-math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["dark"],
        name="ram_cylinder", material_class_id="metal.blackened_gunmetal",
    )
    _y_cyl(frame, "ram_cylinder_cap", 0.024, 0.014, (0.0, r.pivot_y + 0.026, r.ram_z), mats["dark"])
    # Rear bulkhead: the socket sits on the frame centreline, where a
    # low-profile side frame has nothing under it, so a real cross panel carries
    # it down to the floor pan.  It is behind the arm pivot, clear of the arm.
    frame.visual(
        Box((2.0 * r.side_x, 0.030, r.chassis_top_z - r.chassis_z0)),
        origin=Origin(
            xyz=(0.0, r.handle_pivot_y, 0.5 * (r.chassis_z0 + r.chassis_top_z))
        ),
        material=mats["steel"],
        name="rear_bulkhead", material_class_id="metal.steel_bare",
    )
    # Pump socket for the handle, on the rear cross member.
    socket_top = r.handle_pivot_z - 0.016
    socket_bot = r.chassis_top_z - 0.010
    socket_h = socket_top - socket_bot
    frame.visual(
        Box((0.062, 0.036, socket_h)),
        origin=Origin(
            xyz=(0.0, r.handle_pivot_y, socket_bot + socket_h * 0.5)
        ),
        material=mats["dark"],
        name="pump_socket_base", material_class_id="metal.blackened_gunmetal",
    )
    for side, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((PUMP_EAR_T, 0.032, 0.046)),
            origin=Origin(
                xyz=(sx * PUMP_EAR_X, r.handle_pivot_y, r.handle_pivot_z - 0.014)
            ),
            material=mats["dark"],
            name=f"pump_socket_ear_{side}", material_class_id="metal.blackened_gunmetal",
        )
    # Front roller hangers: a plate in the side-frame plane dropping to the
    # axle, plus a stub axle reaching out to MOUNT from the wheel's inner face.
    _add_wheel_hanger(frame, r, mats, r.front_axle_y, "front", outboard=True)
    return frame


def _add_wheel_hanger(frame, r: ResolvedConfig, mats: dict[str, str], y: float,
                      tag: str, *, outboard: bool, x_centre: float = 0.0) -> None:
    hang_top = r.chassis_z0 + 0.012
    hang_bot = RW - 0.012
    hang_h = hang_top - hang_bot
    stations = ((-1.0, 1.0) if outboard else (1.0,))
    for side, sx in enumerate(stations):
        plate_x = sx * r.side_x + (0.0 if outboard else x_centre)
        wheel_x = (
            sx * (r.side_x + WHEEL_X_OFFSET)
            if outboard
            else x_centre + sx * (WHEEL_T * 0.5 + 0.0056 + 0.005)
        )
        frame.visual(
            Box((0.012, 0.034, hang_h)),
            origin=Origin(xyz=(plate_x, y, hang_bot + hang_h * 0.5)),
            material=mats["steel"],
            name=f"{tag}_wheel_hanger_{side}", material_class_id="metal.steel_bare",
        )
        inner_face = abs(wheel_x - plate_x) - WHEEL_T * 0.5
        stub_len = inner_face - MOUNT + 0.008
        _x_cyl(
            frame,
            f"{tag}_stub_axle_{side}",
            0.009,
            stub_len,
            (plate_x + math.copysign(stub_len * 0.5 - 0.004, wheel_x - plate_x), y, RW),
            mats["chrome"],
        )


# --- wheels -----------------------------------------------------------------
def _wheel_visuals(part, mats: dict[str, str], prefix: str) -> None:
    _x_cyl(part, f"{prefix}_tyre", RW, WHEEL_T, (0.0, 0.0, 0.0), mats["rubber"])
    _x_cyl(part, f"{prefix}_hub", RW * 0.45, WHEEL_T - 0.004, (0.0, 0.0, 0.0), mats["chrome"])


def _build_front_rollers(model: ArticulatedObject, frame, r: ResolvedConfig,
                         mats: dict[str, str]) -> None:
    for side, sx in enumerate((-1.0, 1.0)):
        wheel = model.part(f"front_roller_{side}", meta={"role": "front_roller", "index": side})
        _wheel_visuals(wheel, mats, "front_roller")
        _axis_joint(
            model,
            name=f"chassis_to_front_roller_{side}",
            parent=frame,
            child=wheel,
            point=(sx * (r.side_x + WHEEL_X_OFFSET), r.front_axle_y, RW),
            axis=(1.0, 0.0, 0.0),
            provider_radial=(0.0, 0.0, 1.0),
            consumer_radial=(0.0, 0.0, 1.0),
            effort=60.0,
            velocity=12.0,
            articulation_type=ArticulationType.CONTINUOUS,
        )


def _add_rear_roller_hanger(frame, r: ResolvedConfig, mats: dict[str, str],
                            x: float, index: int) -> None:
    """Hanger plate beside a rigid rear roller, plus its stub axle.

    The plate stands outboard of the roller and reaches up to the rear cross
    beam; the stub axle bridges the remaining gap to within MOUNT of the roller
    face, so the roller is carried without any part spearing it.
    """
    hang_top = r.chassis_z0 + 0.012
    hang_bot = RW - 0.012
    hang_h = hang_top - hang_bot
    plate_x = x + WHEEL_T * 0.5 + MOUNT + 0.006 + 0.006
    frame.visual(
        Box((0.012, 0.034, hang_h)),
        origin=Origin(xyz=(plate_x, r.rear_axle_y, hang_bot + hang_h * 0.5)),
        material=mats["steel"],
        name=f"wheel_station__fixed_roller__stub_bracket_{index}", material_class_id="metal.steel_bare",
    )
    stub_len = (plate_x - x) - WHEEL_T * 0.5 - MOUNT + 0.008
    _x_cyl(
        frame,
        f"wheel_station__fixed_roller__stub_axle_{index}",
        0.009,
        stub_len,
        (plate_x - stub_len * 0.5 + 0.004, r.rear_axle_y, RW),
        mats["chrome"],
    )


def _build_rear_stations(model: ArticulatedObject, frame, r: ResolvedConfig,
                         mats: dict[str, str]) -> None:
    for index, x in enumerate(r.station_x):
        if r.wheel_station == "swivel_caster":
            # Bracket boss on the beam that the kingpin turns in.
            frame.visual(
                Box((0.054, 0.054, 0.016)),
                origin=Origin(xyz=(x, r.rear_axle_y, r.chassis_z0 + 0.008)),
                material=mats["steel"],
                name=f"wheel_station__swivel_caster__boss_{index}", material_class_id="metal.steel_bare",
            )
            yoke = model.part(
                f"wheel_station__swivel_caster__yoke_{index}",
                meta={"role": "wheel_station", "index": index},
            )
            yoke.visual(
                Box((0.048, 0.048, 0.012)),
                origin=Origin(xyz=(0.0, 0.0, -0.006 + MOUNT)),
                material=mats["steel"],
                name=f"wheel_station__swivel_caster__kingpin_plate_{index}", material_class_id="metal.steel_bare",
            )
            yoke.visual(
                Cylinder(radius=0.008, length=0.011),
                origin=Origin(xyz=(0.0, 0.0, -0.0035)),
                material=mats["chrome"],
                name=f"wheel_station__swivel_caster__kingpin_{index}", material_class_id="metal.chrome_polished",
            )
            # Two cheeks straddling the wheel with real axial clearance, down to
            # the axle at world z = RW (yoke-local z = RW - chassis_z0).
            cheek_h = CASTER_DROP + 0.014
            for side, sx in enumerate((-1.0, 1.0)):
                yoke.visual(
                    Box((0.010, 0.038, cheek_h)),
                    origin=Origin(
                        xyz=(
                            sx * (WHEEL_T * 0.5 + MOUNT + 0.005),
                            0.0,
                            -cheek_h * 0.5 - 0.003,
                        )
                    ),
                    material=mats["steel"],
                    name=f"wheel_station__swivel_caster__cheek_{index}_{side}", material_class_id="metal.steel_bare",
                )
            wheel = model.part(
                f"wheel_station__swivel_caster__wheel_{index}",
                meta={"role": "caster_wheel", "index": index},
            )
            _wheel_visuals(wheel, mats, "caster")
            _axis_joint(
                model,
                name=f"chassis_to_wheel_station_{index}",
                parent=frame,
                child=yoke,
                point=(x, r.rear_axle_y, r.chassis_z0),
                axis=(0.0, 0.0, 1.0),
                provider_radial=(0.0, 1.0, 0.0),
                consumer_radial=(0.0, 1.0, 0.0),
                lower=-math.pi,
                upper=math.pi,
                effort=40.0,
                velocity=6.0,
            )
            _axis_joint(
                model,
                name=f"wheel_station_{index}_spin",
                parent=yoke,
                child=wheel,
                point=(0.0, 0.0, RW - r.chassis_z0),
                axis=(1.0, 0.0, 0.0),
                provider_radial=(0.0, 0.0, 1.0),
                consumer_radial=(0.0, 0.0, 1.0),
                effort=60.0,
                velocity=12.0,
                articulation_type=ArticulationType.CONTINUOUS,
            )
        else:
            # A rigid roller on a stub bracket: the bracket is host geometry and
            # the station part is the roller, spinning on one CONTINUOUS axis.
            _add_rear_roller_hanger(frame, r, mats, x, index)
            roller = model.part(
                f"wheel_station__fixed_roller__roller_{index}",
                meta={"role": "wheel_station", "index": index},
            )
            _wheel_visuals(roller, mats, "roller")
            _x_cyl(
                roller,
                f"wheel_station__fixed_roller__flange_{index}",
                RW * 0.62,
                WHEEL_T - 0.004,
                (0.0, 0.0, 0.0),
                mats["steel"],
            )
            _axis_joint(
                model,
                name=f"chassis_to_wheel_station_{index}",
                parent=frame,
                child=roller,
                point=(x, r.rear_axle_y, RW),
                axis=(1.0, 0.0, 0.0),
                provider_radial=(0.0, 0.0, 1.0),
                consumer_radial=(0.0, 0.0, 1.0),
                effort=60.0,
                velocity=12.0,
                articulation_type=ArticulationType.CONTINUOUS,
            )


# --- saddle head candidates -------------------------------------------------
def _head_radius(r: ResolvedConfig) -> float:
    return min(0.052, r.chassis_width_m * 0.20)


def _saddle_head_disc_saddle_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    rad = _head_radius(r)
    part.visual(
        Cylinder(radius=rad, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.007 - MOUNT)),
        material=mats["chrome"],
        name="saddle_head__disc_saddle__disc", material_class_id="metal.chrome_polished",
    )
    part.visual(
        _tube("saddle_knurl", rad + 0.0015, rad - 0.005, 0.0, 0.008, 24),
        origin=Origin(xyz=(0.0, 0.0, 0.004 - MOUNT)),
        material=mats["steel"],
        name="saddle_head__disc_saddle__knurl", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=rad - 0.006, length=0.005),
        origin=Origin(xyz=(0.0, 0.0, 0.0145 - MOUNT)),
        material=mats["dark"],
        name="saddle_head__disc_saddle__face", material_class_id="metal.blackened_gunmetal",
    )


def _saddle_head_screw_post_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    rad = _head_radius(r)
    post = 0.055 + r.chassis_len_m * 0.06
    stem = rad * 0.46
    part.visual(
        Cylinder(radius=stem, length=post + MOUNT),
        origin=Origin(xyz=(0.0, 0.0, (post - MOUNT) * 0.5)),
        material=mats["chrome"],
        name="saddle_head__screw_post__post", material_class_id="metal.chrome_polished",
    )
    for i in range(6):
        z = post * (0.14 + 0.68 * i / 5.0)
        part.visual(
            _tube(f"post_thread_{i}", stem + 0.0015, stem - 0.0015, 0.0, 0.0025, 20),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=mats["chrome"],
            name=f"saddle_head__screw_post__thread_{i}", material_class_id="metal.chrome_polished",
        )
    part.visual(
        Box((rad * 1.6, rad * 1.6, 0.014)),
        origin=Origin(xyz=(0.0, 0.0, post * 0.26)),
        material=mats["steel"],
        name="saddle_head__screw_post__collar", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=rad, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, post - 0.005)),
        material=mats["dark"],
        name="saddle_head__screw_post__load_pad", material_class_id="metal.blackened_gunmetal",
    )


def _saddle_head_vee_cradle_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    width = _head_radius(r) * 2.6
    part.visual(
        Box((width, width * 0.72, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.006 - MOUNT)),
        material=mats["steel"],
        name="saddle_head__vee_cradle__base", material_class_id="metal.steel_bare",
    )
    tilt = 0.55
    cheek = width * 0.40
    half = cheek * 0.5
    dy = half * math.sin(tilt)
    z_c = 0.006 + half * math.cos(tilt)
    top_y = cheek * math.sin(tilt)
    top_z = 0.006 + cheek * math.cos(tilt)
    for i, sy in enumerate((-1.0, 1.0)):
        # Rotating about +x sends the cheek's far end toward -y, so the tilt
        # sign is the opposite of the side: each cheek's lower end lands at the
        # groove root inside the base plate and its top out at sy*top_y.
        part.visual(
            Box((width, 0.010, cheek)),
            origin=Origin(xyz=(0.0, sy * dy, z_c), rpy=(-sy * tilt, 0.0, 0.0)),
            material=mats["steel"],
            name=f"saddle_head__vee_cradle__cheek_{i}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Box((width, 0.012, 0.012)),
            origin=Origin(xyz=(0.0, sy * top_y, top_z)),
            material=mats["dark"],
            name=f"saddle_head__vee_cradle__lip_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _saddle_head_wide_platform_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    w = r.chassis_width_m * 0.88
    d = r.chassis_len_m * 0.22
    part.visual(
        Box((w, d, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.006 - MOUNT)),
        material=mats["paint"],
        name="saddle_head__wide_platform__deck", material_class_id="metal.paint_coated",
    )
    for i in range(4):
        y = -d * 0.34 + d * 0.68 * i / 3.0
        part.visual(
            Box((w * 0.9, 0.010, 0.008)),
            origin=Origin(xyz=(0.0, y, 0.014 - MOUNT)),
            material=mats["rubber"],
            name=f"saddle_head__wide_platform__grip_rib_{i}", material_class_id="rubber.smooth_plain",
        )
    for i, sy in enumerate((-1.0, 1.0)):
        part.visual(
            Box((w, 0.010, 0.022)),
            origin=Origin(xyz=(0.0, sy * (d * 0.5 - 0.005), -0.004 - MOUNT)),
            material=mats["edge"],
            name=f"saddle_head__wide_platform__turned_edge_{i}", material_class_id="metal.paint_coated",
        )


_HEAD_BUILDERS = {
    "disc_saddle": _saddle_head_disc_saddle_build,
    "screw_post": _saddle_head_screw_post_build,
    "vee_cradle": _saddle_head_vee_cradle_build,
    "wide_platform": _saddle_head_wide_platform_build,
}


# --- lift arm ---------------------------------------------------------------
def _build_lift_arm(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]):
    arm = model.part("lift_arm", meta={"role": "lift_arm"})
    a = r.arm_len_m
    cy = a * 0.5 * math.cos(ARM0)
    cz = a * 0.5 * math.sin(ARM0)
    for side, sx in enumerate((-1.0, 1.0)):
        arm.visual(
            Box((ARM_PLATE_T, a, ARM_PLATE_H)),
            origin=Origin(xyz=(sx * r.arm_x, cy, cz), rpy=(ARM0, 0.0, 0.0)),
            material=mats["paint"],
            name=f"lift_arm_plate_{side}", material_class_id="metal.paint_coated",
        )
    # Pivot pin journalled MOUNT past the inner face of the chassis lugs, plus
    # tie tubes that make the two plates one connected solid.
    _x_cyl(arm, "lift_arm_pivot_pin", 0.011,
           2.0 * (r.arm_x + ARM_PLATE_T * 0.5 + 0.007 - 0.006 + MOUNT),
           (0.0, 0.0, 0.0), mats["chrome"])
    _x_cyl(
        arm,
        "lift_arm_nose_tube",
        NOSE_R,
        2.0 * (r.arm_x + ARM_PLATE_T * 0.5 + MOUNT),
        (0.0, a * math.cos(ARM0), a * math.sin(ARM0)),
        mats["steel"],
    )
    _x_cyl(
        arm,
        "lift_arm_tie_tube",
        0.009,
        2.0 * (r.arm_x + ARM_PLATE_T * 0.5),
        (0.0, a * 0.55 * math.cos(ARM0), a * 0.55 * math.sin(ARM0)),
        mats["steel"],
    )
    _axis_joint(
        model,
        name="chassis_to_lift_arm",
        parent=frame,
        child=arm,
        point=(0.0, r.pivot_y, r.pivot_z),
        axis=(1.0, 0.0, 0.0),
        provider_radial=(0.0, 1.0, 0.0),
        consumer_radial=(0.0, 1.0, 0.0),
        lower=0.0,
        upper=r.arm_travel_rad,
        effort=22000.0,
        velocity=0.30,
    )

    head = model.part(
        f"saddle_head__{r.saddle_head}__head",
        meta={"role": "saddle_head"},
    )
    _HEAD_BUILDERS[r.saddle_head](head, r, mats)
    # Lift the head body clear of the arm it is bolted over.  The joint stays on
    # the nose-tube axis (that IS the pivot), so without this the head's base
    # plate would be buried inside the tube and the arm plates.
    for visual in head.visuals:
        vx, vy, vz = visual.origin.xyz
        visual.origin = Origin(xyz=(vx, vy, vz + HEAD_LIFT), rpy=visual.origin.rpy)
    # Bored lugs sitting ON the pivot axis, which the arm's nose tube journals
    # into.  Being concentric with the joint, they stay in contact at every
    # angle -- a flat strap resting on the arm tops lifts off as soon as the
    # head counter-rotates.  Risers carry the head body clear above the arm.
    riser_lo = -0.016
    for side, sx in enumerate((-1.0, 1.0)):
        head.visual(
            Box((0.010, 0.036, HEAD_LIFT - riser_lo)),
            origin=Origin(
                xyz=(
                    sx * (r.arm_x + ARM_PLATE_T * 0.5 + 0.005),
                    0.0,
                    0.5 * (riser_lo + HEAD_LIFT),
                )
            ),
            material=mats["steel"],
            name=f"head_mount_riser_{side}", material_class_id="metal.steel_bare",
        )
    head.visual(
        Box((2.0 * (r.arm_x + ARM_PLATE_T * 0.5 + 0.010), 0.040, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, HEAD_LIFT - 0.005)),
        material=mats["steel"],
        name="head_mount_strap", material_class_id="metal.steel_bare",
    )
    _axis_joint(
        model,
        name="lift_arm_to_saddle_head",
        parent=arm,
        child=head,
        point=(0.0, a * math.cos(ARM0), a * math.sin(ARM0)),
        axis=(1.0, 0.0, 0.0),
        provider_radial=(0.0, 1.0, 0.0),
        consumer_radial=(0.0, 1.0, 0.0),
        lower=-r.arm_travel_rad,
        upper=0.0,
        effort=22000.0,
        velocity=0.30,
        # The parallel linkage: the head counter-rotates exactly with the arm,
        # so a floor jack's saddle stays level through the whole lift.
        mimic=Mimic(joint="chassis_to_lift_arm", multiplier=-1.0),
    )
    return arm


# --- ram + pump drive -------------------------------------------------------
def _build_ram(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    piston = model.part("ram_piston", meta={"role": "ram_piston"})
    rod_len = r.ram_len_m * 0.80
    _y_cyl(piston, "ram_rod", 0.0172, rod_len, (0.0, rod_len * 0.5, 0.0), mats["chrome"])
    _y_cyl(piston, "ram_rod_eye", 0.020, 0.016, (0.0, rod_len - 0.005, 0.0), mats["steel"])
    model.articulation(
        "chassis_to_ram_piston",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=piston,
        origin=Origin(xyz=(0.0, r.pivot_y + 0.030, r.ram_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            lower=0.0, upper=r.ram_stroke_m, effort=40000.0, velocity=0.05
        ),
        meta={"positive_motion": "extends the ram rod out of its bore"},
    )


def _pump_drive_lever_handle_build(part, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    _x_cyl(part, "pump_drive__lever_handle__pivot_boss", 0.009, CLEVIS_PIN_LEN, (0.0, 0.0, 0.0),
           mats["chrome"])
    bar = r.handle_len_m
    ang = math.radians(40.0)
    part.visual(
        Box((0.020, bar, 0.018)),
        origin=Origin(
            xyz=(0.0, -bar * 0.5 * math.cos(ang), bar * 0.5 * math.sin(ang)),
            rpy=(-ang, 0.0, 0.0),
        ),
        material=mats["paint"],
        name="pump_drive__lever_handle__bar", material_class_id="metal.paint_coated",
    )
    grip = bar * 0.30
    part.visual(
        Box((0.030, grip, 0.028)),
        origin=Origin(
            xyz=(
                0.0,
                -(bar - grip * 0.5) * math.cos(ang),
                (bar - grip * 0.5) * math.sin(ang),
            ),
            rpy=(-ang, 0.0, 0.0),
        ),
        material=mats["rubber"],
        name="pump_drive__lever_handle__grip", material_class_id="rubber.smooth_plain",
    )


def _pump_drive_air_over_hydraulic_build(part, frame, r: ResolvedConfig,
                                         mats: dict[str, str]) -> None:
    _x_cyl(part, "pump_drive__air_over_hydraulic__pivot_boss", 0.009, CLEVIS_PIN_LEN, (0.0, 0.0, 0.0),
           mats["chrome"])
    bar = r.handle_len_m * 0.42
    ang = math.radians(30.0)
    part.visual(
        Box((0.024, bar, 0.020)),
        origin=Origin(
            xyz=(0.0, -bar * 0.5 * math.cos(ang), bar * 0.5 * math.sin(ang)),
            rpy=(-ang, 0.0, 0.0),
        ),
        material=mats["dark"],
        name="pump_drive__air_over_hydraulic__trigger", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((0.030, bar * 0.32, 0.026)),
        origin=Origin(
            xyz=(
                0.0,
                -(bar - bar * 0.16) * math.cos(ang),
                (bar - bar * 0.16) * math.sin(ang),
            ),
            rpy=(-ang, 0.0, 0.0),
        ),
        material=mats["rubber"],
        name="pump_drive__air_over_hydraulic__trigger_boot", material_class_id="rubber.smooth_plain",
    )
    # Host adaptation: the air can hangs OUTBOARD of the side plate.  On the
    # centreline it sat squarely in the band swept by the lift arm's full-width
    # tie tubes, so it is carried on a bracket off the frame side instead.
    can_r = 0.028
    can_x = r.side_x + can_r + 0.006
    can_y = r.pivot_y + r.ram_len_m * 0.5
    can_z = r.chassis_z0 + can_r
    can_len = r.chassis_len_m * 0.16
    frame.visual(
        Box((can_x - r.side_x + can_r, can_len * 0.5, 0.016)),
        origin=Origin(
            xyz=(0.5 * (r.side_x + can_x + can_r), can_y, r.chassis_z0 + 0.008)
        ),
        material=mats["edge"],
        name="pump_drive__air_over_hydraulic__can_bracket", material_class_id="metal.paint_coated",
    )
    frame.visual(
        Cylinder(radius=can_r, length=can_len),
        origin=Origin(xyz=(can_x, can_y, can_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="pump_drive__air_over_hydraulic__air_can", material_class_id="metal.steel_bare",
    )
    frame.visual(
        _tube("air_can_band", can_r + 0.0018, can_r - 0.002, 0.0, 0.012, 24),
        origin=Origin(xyz=(can_x, can_y, can_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["chrome"],
        name="pump_drive__air_over_hydraulic__air_can_band", material_class_id="metal.chrome_polished",
    )
    frame.visual(
        Cylinder(radius=0.013, length=0.022),
        origin=Origin(xyz=(can_x, can_y, can_z + can_r + 0.005)),
        material=mats["dark"],
        name="pump_drive__air_over_hydraulic__regulator_knob", material_class_id="metal.blackened_gunmetal",
    )


_PUMP_BUILDERS = {
    "lever_handle": _pump_drive_lever_handle_build,
    "air_over_hydraulic": _pump_drive_air_over_hydraulic_build,
}


def _build_pump(model: ArticulatedObject, frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    handle = model.part(
        f"pump_drive__{r.pump_drive}__handle",
        meta={"role": "pump_input"},
    )
    _PUMP_BUILDERS[r.pump_drive](handle, frame, r, mats)
    _axis_joint(
        model,
        name="chassis_to_pump_input",
        parent=frame,
        child=handle,
        point=(0.0, r.handle_pivot_y, r.handle_pivot_z),
        axis=(1.0, 0.0, 0.0),
        provider_radial=(0.0, 1.0, 0.0),
        consumer_radial=(0.0, 1.0, 0.0),
        lower=-0.30,
        upper=0.30,
        effort=400.0,
        velocity=2.4,
    )


# --- assembly ---------------------------------------------------------------
def build_picturex_0611_hydraulic_jack2(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_hydraulic_jack2",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "rear-pivoted lift arm with a level-keeping saddle linkage",
        },
    )
    mats = _materials(model, r)
    frame = _build_chassis(model, r, mats)
    _build_lift_arm(model, frame, r, mats)
    _build_ram(model, frame, r, mats)
    _build_pump(model, frame, r, mats)
    _build_front_rollers(model, frame, r, mats)
    _build_rear_stations(model, frame, r, mats)

    model.meta["risk_poses"] = (
        {"chassis_to_lift_arm": 0.0, "chassis_to_pump_input": 0.0},
        {"chassis_to_lift_arm": r.arm_travel_rad, "chassis_to_pump_input": 0.30},
        {"chassis_to_lift_arm": r.arm_travel_rad, "chassis_to_pump_input": -0.30},
    )
    model.meta["coupled_joint_pairs"] = (
        ("chassis_to_lift_arm", "chassis_to_pump_input"),
    )
    return model


def build_seeded_picturex_0611_hydraulic_jack2(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_hydraulic_jack2(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_hydraulic_jack2_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    chassis = _parts_by_role(model, "jack_chassis")
    arms = _parts_by_role(model, "lift_arm")
    heads = _parts_by_role(model, "saddle_head")
    pumps = _parts_by_role(model, "pump_input")
    fronts = _parts_by_role(model, "front_roller")
    stations = _parts_by_role(model, "wheel_station")

    joints = {j.name: j for j in model.articulations}
    arm_joint = joints.get("chassis_to_lift_arm")
    head_joint = joints.get("lift_arm_to_saddle_head")
    pump_joint = joints.get("chassis_to_pump_input")
    ram_joint = joints.get("chassis_to_ram_piston")
    station_joints = [
        joints.get(f"chassis_to_wheel_station_{i}") for i in range(r.rear_station_count)
    ]

    def _is_rev_x(j) -> bool:
        return (
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(abs(v), 6) for v in j.axis) == (1.0, 0.0, 0.0)
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
        )

    ctx.check(
        "category_anchor: rear-pivoted floor jack lift arm",
        len(chassis) == 1
        and len(arms) == 1
        and len(heads) == 1
        and len(pumps) == 1
        and len(fronts) == 2
        and len(stations) == r.rear_station_count
        and bool(model.root_parts())
        and model.root_parts()[0].name == "jack_chassis"
        and _is_rev_x(arm_joint)
        and arm_joint.parent == "jack_chassis"
        and getattr(arm_joint, "mimic", None) is None
        and _is_rev_x(pump_joint)
        and ram_joint is not None
        and ram_joint.articulation_type == ArticulationType.PRISMATIC
        and tuple(round(v, 6) for v in ram_joint.axis) == (0.0, 1.0, 0.0)
        and ram_joint.motion_limits.upper > ram_joint.motion_limits.lower
        and all(j is not None for j in station_joints),
        details=(
            f"chassis={len(chassis)} arms={len(arms)} heads={len(heads)} pumps={len(pumps)} "
            f"fronts={len(fronts)} stations={len(stations)}"
        ),
    )

    # The parallel linkage: the head counter-rotates with the arm at exactly -1,
    # so it must rise without tipping.
    head_part = heads[0]
    rest = ctx.part_world_aabb(head_part)
    with ctx.pose({arm_joint: arm_joint.motion_limits.upper}):
        raised = ctx.part_world_aabb(head_part)
    level_ok = (
        rest is not None
        and raised is not None
        and abs((raised[1][2] - raised[0][2]) - (rest[1][2] - rest[0][2])) < 1e-4
        and abs((raised[1][1] - raised[0][1]) - (rest[1][1] - rest[0][1])) < 1e-4
    )
    ctx.check(
        "category_anchor: load head stays level as the arm rises",
        _is_rev_x(head_joint)
        and getattr(head_joint.mimic, "joint", None) == "chassis_to_lift_arm"
        and abs(float(head_joint.mimic.multiplier) + 1.0) < 1e-9
        and level_ok
        and abs((raised[0][2] - rest[0][2]) - r.lift_height_m) < 2e-3,
        details=f"rest={rest} raised={raised} lift={r.lift_height_m} level_ok={level_ok}",
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    head_ok = {
        "disc_saddle": any("disc_saddle__knurl" in n for n in visual_names),
        "screw_post": any("screw_post__thread" in n for n in visual_names),
        "vee_cradle": any("vee_cradle__cheek" in n for n in visual_names),
        "wide_platform": any("wide_platform__grip_rib" in n for n in visual_names),
    }[r.saddle_head]
    ctx.check(
        "category_anchor: saddle_head identity", head_ok, details=f"saddle_head={r.saddle_head}"
    )

    chassis_ok = {
        "plate_frame": any("plate_frame__rolled_edge" in n for n in visual_names),
        "low_profile": any("low_profile__nose_deck" in n for n in visual_names),
        "boxed_frame": any("boxed_frame__cross_deck" in n for n in visual_names),
    }[r.chassis_style]
    ctx.check(
        "category_anchor: chassis_style identity", chassis_ok,
        details=f"chassis_style={r.chassis_style}",
    )

    pump_ok = {
        "lever_handle": any("lever_handle__grip" in n for n in visual_names),
        "air_over_hydraulic": any("air_over_hydraulic__air_can" in n for n in visual_names),
    }[r.pump_drive]
    ctx.check("category_anchor: pump_drive identity", pump_ok, details=f"pump_drive={r.pump_drive}")

    if r.wheel_station == "swivel_caster":
        spins = [joints.get(f"wheel_station_{i}_spin") for i in range(r.rear_station_count)]
        # A caster's vertical kingpin and its horizontal wheel axis are two
        # separate joints; they must never be collapsed into one.
        station_ok = all(
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(abs(v), 6) for v in j.axis) == (0.0, 0.0, 1.0)
            for j in station_joints
        ) and all(
            j is not None
            and j.articulation_type == ArticulationType.CONTINUOUS
            and tuple(round(abs(v), 6) for v in j.axis) == (1.0, 0.0, 0.0)
            for j in spins
        )
    else:
        station_ok = all(
            j is not None
            and j.articulation_type == ArticulationType.CONTINUOUS
            and tuple(round(abs(v), 6) for v in j.axis) == (1.0, 0.0, 0.0)
            for j in station_joints
        ) and not any(n.endswith("_spin") for n in joints)
    ctx.check(
        "category_anchor: wheel_station identity",
        station_ok
        and all(
            joints[f"chassis_to_front_roller_{i}"].articulation_type
            == ArticulationType.CONTINUOUS
            for i in range(2)
        ),
        details=f"wheel_station={r.wheel_station} n={r.rear_station_count}",
    )

    # Every wheel must actually reach the floor, or the jack would rock.  On a
    # swivel caster it is the WHEEL that touches down, not the yoke it hangs
    # from, so the ground-contacting part depends on the station candidate.
    ground_parts = list(fronts)
    if r.wheel_station == "swivel_caster":
        ground_parts += _parts_by_role(model, "caster_wheel")
    else:
        ground_parts += stations
    floor_ok = []
    for part in ground_parts:
        box = ctx.part_world_aabb(part)
        floor_ok.append(box is not None and -0.002 <= box[0][2] <= 0.006)
    ctx.check(
        "all wheels stand on the floor plane",
        all(floor_ok),
        details=f"floor_ok={floor_ok} parts={[p.name for p in ground_parts]}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "min_chassis_two_casters",
        {
            "saddle_head": "disc_saddle",
            "chassis_style": "boxed_frame",
            "pump_drive": "lever_handle",
            "wheel_station": "swivel_caster",
            "rear_station_count": 2,
            "chassis_len_m": 0.55,
            "chassis_width_m": 0.22,
            "arm_reach_ratio": 0.60,
        },
        reason="shortest, narrowest chassis with the shortest arm - tightest packaging",
    ),
    corner_case(
        "max_chassis_four_casters_platform",
        {
            "saddle_head": "wide_platform",
            "chassis_style": "low_profile",
            "pump_drive": "air_over_hydraulic",
            "wheel_station": "swivel_caster",
            "rear_station_count": 4,
            "chassis_len_m": 1.05,
            "chassis_width_m": 0.40,
            "arm_reach_ratio": 0.82,
        },
        reason="longest reach with four swivel casters on the widened rear beam",
    ),
    corner_case(
        "long_arm_narrow_rollers_screw",
        {
            "saddle_head": "screw_post",
            "chassis_style": "plate_frame",
            "pump_drive": "lever_handle",
            "wheel_station": "fixed_roller",
            "rear_station_count": 4,
            "chassis_len_m": 0.55,
            "chassis_width_m": 0.22,
            "arm_reach_ratio": 0.82,
        },
        reason="longest arm on the shortest chassis with four rollers on a beam wider than the frame",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_picturex_0611_hydraulic_jack2",
    "build_seeded_picturex_0611_hydraulic_jack2",
    "run_picturex_0611_hydraulic_jack2_tests",
]
