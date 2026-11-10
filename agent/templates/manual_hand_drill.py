# SPDX-License-Identifier: Apache-2.0

"""Manual (hand-cranked) hand drill — modular template.

A compact geared "eggbeater" / breast hand drill: a grounded cast ``body``
frame carries a fore-aft ``spindle`` (CONTINUOUS +X) tipped by a ``chuck_sleeve``
(REVOLUTE +X), a side ``drive_gear`` (CONTINUOUS +Y) meshing the spindle pinion,
an offset ``crank`` (CONTINUOUS +Y) with a free-spinning ``crank_grip``
(CONTINUOUS +Y), and a ``speed_lever`` selector (REVOLUTE +Y or PRISMATIC +X).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/manual_hand_drill.md`` and the
``picture/0611/manual_hand_drill`` 5-star pool (1 origin + 8 slot forks), all
synced under ``data/records/``.

Structure (pattern = ``mixed``): the 7-part / 6-joint skeleton is fixed across
every fork; four slots swap the geometry of one layer each:

  * ``gear_train`` (4): open_spur_gear / single_pinion_crown / dual_pinion /
    enclosed_bevel — the drive wheel form (② mesh + ③ form).
  * ``grip_form`` (3, ③ Primary Form Family): straight_barrel_handle /
    pistol_grip / breast_plate — the rear hand grip authored as ``body`` visuals
    (Rule 1, non-moving).
  * ``speed_selection`` (3): pivot_lever / reversible_ratchet (REVOLUTE +Y) /
    sliding_two_speed (PRISMATIC +X) — ② joint-type axis.
  * ``chuck`` (2): keyed_geared_chuck / collet_chuck — the chuck-head form.

All continuous scaling is a global similarity ``frame_scale`` about the world
origin (every cadquery mesh gets ``unit_scale``; every primitive dim / origin /
joint origin / prismatic travel is ``× frame_scale``), so the gear mesh and every
clearance stay intact at every scale. ``crank_reach_scale`` lengthens the crank
arm and ``selector_travel_scale`` scales the selector range on top of it.

Gear-mesh, bearing-bore, and captured-pin overlaps are intentional and declared
element-scoped in ``run_manual_hand_drill_tests`` (mirroring each source record's
run_tests); those joints omit ``MatingContract`` (captured geometry, grandfathered).
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
    Box,
    Cylinder,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

GearTrain = Literal[
    "open_spur_gear", "single_pinion_crown", "dual_pinion", "enclosed_bevel"
]
GripForm = Literal["straight_barrel_handle", "pistol_grip", "breast_plate"]
SpeedSelection = Literal["pivot_lever", "reversible_ratchet", "sliding_two_speed"]
Chuck = Literal["keyed_geared_chuck", "collet_chuck"]
PaletteStyle = Literal[
    "cobalt_enamel",
    "oxblood_enamel",
    "black_japanned",
    "forest_green_enamel",
    "bare_cast_steel",
]

GEAR_TRAINS: tuple[GearTrain, ...] = (
    "open_spur_gear",
    "single_pinion_crown",
    "dual_pinion",
    "enclosed_bevel",
)
GRIP_FORMS: tuple[GripForm, ...] = (
    "straight_barrel_handle",
    "pistol_grip",
    "breast_plate",
)
SPEED_SELECTIONS: tuple[SpeedSelection, ...] = (
    "pivot_lever",
    "reversible_ratchet",
    "sliding_two_speed",
)
CHUCKS: tuple[Chuck, ...] = ("keyed_geared_chuck", "collet_chuck")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "cobalt_enamel",
    "oxblood_enamel",
    "black_japanned",
    "forest_green_enamel",
    "bare_cast_steel",
)

# Palette keys: frame (enamel/cast body), steel (bright metal), dark_steel
# (gears/shafts), wood (grip), wood_dark (endgrain). Every ``.visual(material=)``
# is driven by the sampled palette. cobalt_enamel == origin colorway.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "cobalt_enamel": {
        "frame": (0.055, 0.12, 0.42, 1.0),
        "steel": (0.70, 0.72, 0.73, 1.0),
        "dark_steel": (0.24, 0.25, 0.26, 1.0),
        "wood": (0.72, 0.25, 0.055, 1.0),
        "wood_dark": (0.44, 0.12, 0.025, 1.0),
    },
    "oxblood_enamel": {
        "frame": (0.40, 0.06, 0.08, 1.0),
        "steel": (0.70, 0.72, 0.73, 1.0),
        "dark_steel": (0.23, 0.24, 0.25, 1.0),
        "wood": (0.52, 0.29, 0.13, 1.0),
        "wood_dark": (0.30, 0.15, 0.06, 1.0),
    },
    "black_japanned": {
        "frame": (0.05, 0.05, 0.055, 1.0),
        "steel": (0.78, 0.62, 0.30, 1.0),  # bright brass hardware
        "dark_steel": (0.32, 0.23, 0.10, 1.0),  # dark brass
        "wood": (0.80, 0.62, 0.36, 1.0),  # beech
        "wood_dark": (0.55, 0.40, 0.22, 1.0),
    },
    "forest_green_enamel": {
        "frame": (0.06, 0.24, 0.12, 1.0),
        "steel": (0.70, 0.72, 0.73, 1.0),
        "dark_steel": (0.24, 0.25, 0.26, 1.0),
        "wood": (0.66, 0.34, 0.12, 1.0),
        "wood_dark": (0.40, 0.18, 0.06, 1.0),
    },
    "bare_cast_steel": {
        "frame": (0.42, 0.44, 0.46, 1.0),  # unpainted grey cast iron
        "steel": (0.79, 0.81, 0.83, 1.0),  # polished steel
        "dark_steel": (0.31, 0.32, 0.34, 1.0),
        "wood": (0.80, 0.66, 0.42, 1.0),  # light natural
        "wood_dark": (0.58, 0.44, 0.24, 1.0),
    },
}

# Nominal (frame_scale == 1) continuous-scale ranges.
FRAME_SCALE_RANGE = (0.90, 1.12)
CRANK_REACH_RANGE = (0.90, 1.18)
SELECTOR_TRAVEL_RANGE = (0.85, 1.15)

# Fixed geometry constants (meters), from the origin record model.py.
_CRANK_ENDPOINT_X = 0.061
_CRANK_ENDPOINT_Z = -0.043
_SLIDE_TRAVEL = 0.028  # sliding_two_speed guide length
_PIVOT_RANGE = 0.42
_RATCHET_RANGE = 0.48


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ManualHandDrillConfig:
    gear_train: GearTrain | None = None
    grip_form: GripForm | None = None
    speed_selection: SpeedSelection | None = None
    chuck: Chuck | None = None
    palette_style: PaletteStyle = "cobalt_enamel"
    frame_scale: float = 1.0
    crank_reach_scale: float = 1.0
    selector_travel_scale: float = 1.0
    name: str = "manual_hand_drill"


@dataclass(frozen=True)
class ResolvedManualHandDrillConfig:
    gear_train: GearTrain
    grip_form: GripForm
    speed_selection: SpeedSelection
    chuck: Chuck
    palette_style: PaletteStyle
    s: float  # frame_scale (global similarity factor)
    cr: float  # crank_reach_scale
    st: float  # selector_travel_scale
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> ManualHandDrillConfig:
    rng = random.Random(seed)
    return ManualHandDrillConfig(
        gear_train=rng.choice(GEAR_TRAINS),
        grip_form=rng.choice(GRIP_FORMS),
        speed_selection=rng.choice(SPEED_SELECTIONS),
        chuck=rng.choice(CHUCKS),
        palette_style=rng.choice(PALETTE_STYLES),
        frame_scale=round(rng.uniform(*FRAME_SCALE_RANGE), 4),
        crank_reach_scale=round(rng.uniform(*CRANK_REACH_RANGE), 4),
        selector_travel_scale=round(rng.uniform(*SELECTOR_TRAVEL_RANGE), 4),
        name=f"seeded_manual_hand_drill_{seed}",
    )


def resolve_config(
    config: ManualHandDrillConfig | None = None,
) -> ResolvedManualHandDrillConfig:
    cfg = config or ManualHandDrillConfig()
    s = _clamp(cfg.frame_scale, *FRAME_SCALE_RANGE)
    # inequality: crank reach floor so the grip orbit clears the wheel/body.
    cr = _clamp(cfg.crank_reach_scale, *CRANK_REACH_RANGE)
    st = _clamp(cfg.selector_travel_scale, *SELECTOR_TRAVEL_RANGE)
    return ResolvedManualHandDrillConfig(
        gear_train=_pick(cfg.gear_train, GEAR_TRAINS),
        grip_form=_pick(cfg.grip_form, GRIP_FORMS),
        speed_selection=_pick(cfg.speed_selection, SPEED_SELECTIONS),
        chuck=_pick(cfg.chuck, CHUCKS),
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        s=s,
        cr=cr,
        st=st,
        name=cfg.name or "manual_hand_drill",
    )


def slot_choices_for_config(
    config: ManualHandDrillConfig | ResolvedManualHandDrillConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedManualHandDrillConfig)
        else resolve_config(config)
    )
    return (
        ("gear_train", r.gear_train),
        ("grip_form", r.grip_form),
        ("speed_selection", r.speed_selection),
        ("chuck", r.chuck),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# cadquery primitive helpers (from origin model.py L23-52; nominal size — the
# global frame_scale is applied via unit_scale on the meshed result).
# ---------------------------------------------------------------------------
def _x_cylinder(radius, x0, x1, *, y=0.0, z=0.0) -> cq.Shape:
    return cq.Solid.makeCylinder(
        radius, x1 - x0, cq.Vector(x0, y, z), cq.Vector(1.0, 0.0, 0.0)
    )


def _y_cylinder(radius, y0, y1, *, x=0.0, z=0.0) -> cq.Shape:
    return cq.Solid.makeCylinder(
        radius, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0.0, 1.0, 0.0)
    )


def _build_cast_frame() -> cq.Shape:
    """Blue cast-iron drill frame with true spindle and gear-shaft bores.
    (origin L55-92)"""
    spindle_z = -0.050
    sleeve_outer = _x_cylinder(0.018, -0.078, 0.073, z=spindle_z)
    sleeve_bore = _x_cylinder(0.0084, -0.081, 0.076, z=spindle_z)
    sleeve = sleeve_outer.cut(sleeve_bore)

    gear_plate = _y_cylinder(0.045, -0.014, -0.001, z=0.015)
    gear_bore = _y_cylinder(0.0064, -0.018, 0.004, z=0.015)
    gear_plate = gear_plate.cut(gear_bore)

    bridge = cq.Solid.makeBox(0.058, 0.013, 0.068, cq.Vector(-0.029, -0.014, -0.050))
    bridge = bridge.cut(_x_cylinder(0.0084, -0.032, 0.032, z=spindle_z))

    rear_socket = _x_cylinder(0.014, 0.064, 0.112, z=spindle_z)
    socket_bore = _x_cylinder(0.0092, 0.061, 0.116, z=spindle_z)
    rear_socket = rear_socket.cut(socket_bore)

    upper_rib = cq.Solid.makeBox(0.052, 0.013, 0.013, cq.Vector(0.006, -0.014, 0.046))

    frame = sleeve.fuse(gear_plate).fuse(bridge).fuse(rear_socket).fuse(upper_rib)
    pinion_pocket = _x_cylinder(0.0150, -0.011, 0.011, z=spindle_z)
    full_gear_bore = _y_cylinder(0.0064, -0.020, 0.006, z=0.015)
    return frame.cut(pinion_pocket).cut(full_gear_bore)


def _build_toothed_wheel(
    *, root_radius, outer_radius, width, tooth_count, bore_radius, tooth_width
) -> cq.Shape:
    """Single connected gear/ribbed ring with a real through bore. (origin L95-132)"""
    body = cq.Solid.makeCylinder(
        root_radius, width, cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0)
    )
    radial_depth = outer_radius - root_radius
    for index in range(tooth_count):
        tooth = cq.Solid.makeBox(
            radial_depth + 0.0012,
            tooth_width,
            width,
            cq.Vector(root_radius - 0.0008, -tooth_width * 0.5, 0.0),
        )
        tooth = tooth.rotate(
            cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0), 360.0 * index / tooth_count
        )
        body = body.fuse(tooth)
    bore = cq.Solid.makeCylinder(
        bore_radius, width + 0.004, cq.Vector(0.0, 0.0, -0.002), cq.Vector(0.0, 0.0, 1.0)
    )
    return body.cut(bore)


def _build_single_pinion_drive_wheel() -> cq.Shape:
    """Spoked crown wheel with teeth on only the spindle-facing side.
    (single_pinion fork L136-174)"""
    wheel_y0, wheel_y1 = 0.023, 0.031
    rim = _y_cylinder(0.0470, wheel_y0, wheel_y1).cut(
        _y_cylinder(0.0340, wheel_y0 - 0.001, wheel_y1 + 0.001)
    )
    hub = _y_cylinder(0.0115, 0.019, 0.036)
    wheel = rim.fuse(hub)
    for index in range(6):
        spoke = cq.Solid.makeBox(
            0.027, wheel_y1 - wheel_y0, 0.007, cq.Vector(0.009, wheel_y0, -0.0035)
        ).rotate(cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0), 60.0 * index)
        wheel = wheel.fuse(spoke)
    for index in range(36):
        tooth = cq.Solid.makeBox(
            0.0095, 0.007, 0.0046, cq.Vector(0.0415, 0.0175, -0.0023)
        ).rotate(cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0), 10.0 * index)
        wheel = wheel.fuse(tooth)
    return wheel.cut(_y_cylinder(0.0053, 0.016, 0.039))


def _build_enclosed_bevel_housing() -> cq.Shape:
    """Hollow cast pod around the crown wheel with two real shaft bearings.
    (enclosed_bevel fork L135-153)"""
    outer = _y_cylinder(0.057, -0.002, 0.041, z=0.015)
    cavity = _y_cylinder(0.053, 0.002, 0.037, z=0.015)
    housing = outer.cut(cavity)
    shaft_bore = _y_cylinder(0.0064, -0.004, 0.044, z=0.015)
    pinion_relief = _x_cylinder(0.0160, -0.018, 0.018, z=-0.050)
    housing = housing.cut(shaft_bore).cut(pinion_relief)
    bearing_boss = _y_cylinder(0.0120, 0.041, 0.047, z=0.015)
    bearing_boss = bearing_boss.cut(_y_cylinder(0.0064, 0.040, 0.048, z=0.015))
    return housing.fuse(bearing_boss)


def _build_bevel_drive_wheel() -> cq.Shape:
    """Compact crown/bevel wheel sized to run inside the cast gear pod.
    (enclosed_bevel fork L156-195)"""
    width = 0.012
    body = cq.Solid.makeCone(
        0.044, 0.037, width, cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0)
    )
    hub = cq.Solid.makeCylinder(
        0.012, width + 0.006, cq.Vector(0.0, 0.0, -0.003), cq.Vector(0.0, 0.0, 1.0)
    )
    body = body.fuse(hub)
    for index in range(32):
        tooth = cq.Solid.makeBox(
            0.012, 0.0042, 0.006, cq.Vector(0.039, -0.0021, 0.0)
        ).rotate(cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0), 360.0 * index / 32)
        body = body.fuse(tooth)
    bore = cq.Solid.makeCylinder(
        0.0053, width + 0.010, cq.Vector(0.0, 0.0, -0.005), cq.Vector(0.0, 0.0, 1.0)
    )
    return body.cut(bore)


def _build_crank_arm(endpoint_x: float, endpoint_z: float) -> cq.Shape:
    """Offset crank arm from the gear boss to the grip eye. (origin L135-158)"""
    length = math.hypot(endpoint_x, endpoint_z)
    angle_deg = math.degrees(math.atan2(-endpoint_z, endpoint_x))
    arm = cq.Solid.makeBox(length, 0.007, 0.010, cq.Vector(0.0, -0.0035, -0.005))
    arm = arm.rotate(cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0), angle_deg)
    center_boss = _y_cylinder(0.0115, -0.004, 0.008)
    grip_eye = _y_cylinder(0.0095, -0.0035, 0.006, x=endpoint_x, z=endpoint_z)
    return arm.fuse(center_boss).fuse(grip_eye)


def _build_ratchet_selector_arm(endpoint_x: float, endpoint_z: float) -> cq.Shape:
    """Short stamped selector linking the pivot boss to the thumb paddle.
    (ratchet fork L161-183)"""
    length = math.hypot(endpoint_x, endpoint_z)
    angle_deg = math.degrees(math.atan2(-endpoint_z, endpoint_x))
    arm = cq.Solid.makeBox(length, 0.005, 0.006, cq.Vector(0.0, 0.0, -0.003)).rotate(
        cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0), angle_deg
    )
    root = _y_cylinder(0.0075, 0.0, 0.005)
    tip_web = _y_cylinder(0.0055, 0.0, 0.005, x=endpoint_x, z=endpoint_z)
    return arm.fuse(root).fuse(tip_web)


def _build_selector_mount() -> cq.Shape:
    """Cast guide with side rails and hard stops for a two-position slider.
    (sliding fork L189-221)"""
    base = cq.Solid.makeBox(0.050, 0.010, 0.020, cq.Vector(0.019, 0.014, -0.060))
    lower_rail = cq.Solid.makeBox(0.050, 0.005, 0.003, cq.Vector(0.019, 0.024, -0.060))
    upper_rail = cq.Solid.makeBox(0.050, 0.005, 0.003, cq.Vector(0.019, 0.024, -0.043))
    rear_stop = cq.Solid.makeBox(0.004, 0.005, 0.014, cq.Vector(0.019, 0.024, -0.057))
    front_stop = cq.Solid.makeBox(0.004, 0.005, 0.014, cq.Vector(0.065, 0.024, -0.057))
    return base.fuse(lower_rail).fuse(upper_rail).fuse(rear_stop).fuse(front_stop)


def _wood_handle_profile(radius: float, length: float):
    return [
        (0.000, 0.000),
        (radius * 0.72, 0.004),
        (radius * 0.94, 0.014),
        (radius, length * 0.28),
        (radius * 0.96, length * 0.66),
        (radius * 0.84, length * 0.90),
        (radius * 0.58, length * 0.985),
        (0.000, length),
    ]


def _wood_handle_mesh(name: str, *, radius: float, length: float):
    """Turned hardwood grip (origin L161-172). radius/length pre-scaled by caller."""
    return mesh_from_geometry(LatheGeometry(_wood_handle_profile(radius, length), segments=48), name)


def _pistol_grip_shape(radius: float) -> cq.Shape:
    """Lofted dropped pistol grip (pistol fork L168-192). radius nominal; unit_scale
    applied by caller."""
    sections = (
        (0.000, 0.000, radius * 0.80, radius * 0.80),
        (0.016, 0.000, radius * 0.86, radius * 0.84),
        (0.032, -0.012, radius * 0.96, radius * 1.08),
        (0.048, -0.037, radius * 1.04, radius * 1.28),
        (0.062, -0.069, radius * 1.08, radius * 1.36),
        (0.073, -0.100, radius * 1.00, radius * 1.25),
        (0.079, -0.119, radius * 1.13, radius * 1.08),
    )
    wires = []
    for x, z, half_y, half_z in sections:
        wire = cq.Workplane("YZ", origin=(x, 0.0, z)).ellipse(half_y, half_z).wire().val()
        wires.append(wire)
    return cq.Solid.makeLoft(wires, True)


def _breast_plate_mesh_shape() -> cq.Shape:
    """Short neck and broad oval hardwood pad (breast fork L177-191). Built in
    absolute drill coords about z=-0.050; unit_scale applied by caller."""
    neck = _x_cylinder(0.0135, 0.112, 0.149, z=-0.050)
    shoulder = _x_cylinder(0.020, 0.143, 0.153, z=-0.050)
    plate = (
        cq.Workplane("YZ", origin=(0.145, 0.0, -0.050))
        .ellipse(0.021, 0.028)
        .workplane(offset=0.009)
        .ellipse(0.044, 0.057)
        .workplane(offset=0.013)
        .ellipse(0.041, 0.054)
        .loft(combine=True)
        .val()
    )
    return neck.fuse(shoulder).fuse(plate)


def _breast_plate_end_shape() -> cq.Shape:
    return (
        cq.Workplane("YZ", origin=(0.167, 0.0, -0.050))
        .ellipse(0.0395, 0.0525)
        .extrude(0.0025)
        .val()
    )


def _keyed_chuck_nose_mesh():
    """Lathe-turned tapered chuck nose (origin L175-186)."""
    profile = [
        (0.0065, 0.000),
        (0.0105, 0.006),
        (0.0120, 0.014),
        (0.0110, 0.030),
        (0.0082, 0.044),
        (0.0048, 0.054),
        (0.0022, 0.061),
        (0.0000, 0.064),
    ]
    return mesh_from_geometry(LatheGeometry(profile, segments=48), "chuck_nose")


def _collet_nose_shape() -> cq.Shape:
    """Four-finger collet body with a through bore and exposed nose. (collet fork L175-214)"""
    rear_shank = cq.Solid.makeCylinder(
        0.0117, 0.031, cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0)
    )
    taper = cq.Solid.makeCone(
        0.0113, 0.0048, 0.033, cq.Vector(0.0, 0.0, 0.029), cq.Vector(0.0, 0.0, 1.0)
    )
    collet = rear_shank.fuse(taper)
    tool_bore = cq.Solid.makeCylinder(
        0.0022, 0.068, cq.Vector(0.0, 0.0, -0.002), cq.Vector(0.0, 0.0, 1.0)
    )
    collet = collet.cut(tool_bore)
    slot_x = cq.Solid.makeBox(0.0010, 0.028, 0.034, cq.Vector(-0.0005, -0.014, 0.031))
    slot_y = cq.Solid.makeBox(0.028, 0.0010, 0.034, cq.Vector(-0.014, -0.0005, 0.031))
    return collet.cut(slot_x).cut(slot_y)


def _build_collet_nut() -> cq.Shape:
    """Knurled tightening nut capturing the rear of the collet. (collet fork L218-260)"""
    nut = cq.Solid.makeCylinder(
        0.0148, 0.029, cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0)
    )
    rear_band = cq.Solid.makeCylinder(
        0.0163, 0.0045, cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0)
    )
    front_band = cq.Solid.makeCylinder(
        0.0157, 0.0045, cq.Vector(0.0, 0.0, 0.0245), cq.Vector(0.0, 0.0, 1.0)
    )
    nut = nut.fuse(rear_band).fuse(front_band)
    for index in range(28):
        rib = cq.Solid.makeBox(
            0.0020, 0.0020, 0.020, cq.Vector(0.0140, -0.0010, 0.0045)
        ).rotate(cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 0.0, 1.0), 360.0 * index / 28)
        nut = nut.fuse(rib)
    bore = cq.Solid.makeCylinder(
        0.01205, 0.033, cq.Vector(0.0, 0.0, -0.002), cq.Vector(0.0, 0.0, 1.0)
    )
    return nut.cut(bore)


# ---------------------------------------------------------------------------
# Origin scaling helper: every xyz literal is × frame_scale (s).
# ---------------------------------------------------------------------------
def _o(s: float, x: float = 0.0, y: float = 0.0, z: float = 0.0, rpy=(0.0, 0.0, 0.0)) -> Origin:
    return Origin(xyz=(x * s, y * s, z * s), rpy=rpy)


_RY = (0.0, math.pi / 2.0, 0.0)  # rotate +Y (X-cylinders)
_RX = (-math.pi / 2.0, 0.0, 0.0)  # rotate -X (Y-cylinders)


# ---------------------------------------------------------------------------
# Slot builders
# ---------------------------------------------------------------------------
def _build_body(model, r, mats) -> object:
    """Grounded body: cast frame + grip_form + selector_mount (+ bevel housing)."""
    s = r.s
    body = model.part("body")
    body.visual(
        mesh_from_cadquery(_build_cast_frame(), "cast_drill_frame", tolerance=0.0007, unit_scale=s),
        material=mats["frame"],
        name="cast_frame", material_class_id=("metal.paint_coated" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "black_japanned", "forest_green_enamel"} else "metal.cast_iron_bare"),
    )

    # --- grip_form (③ Primary Form Family) — non-moving body visuals (Rule 1). ---
    if r.grip_form == "pistol_grip":
        body.visual(
            Cylinder(radius=0.0145 * s, length=0.012 * s),
            origin=_o(s, 0.108, 0.0, -0.050, rpy=_RY),
            material=mats["steel"],
            name="handle_ferrule", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
        )
        body.visual(
            mesh_from_cadquery(_pistol_grip_shape(0.0160), "main_pistol_grip", tolerance=0.00045, unit_scale=s),
            origin=_o(s, 0.108, 0.0, -0.050),
            material=mats["wood"],
            name="main_handle", material_class_id="wood.polished_varnished",
        )
        body.visual(
            Cylinder(radius=0.0180 * s, length=0.004 * s),
            origin=_o(s, 0.188, 0.0, -0.170, rpy=(0.0, 2.84, 0.0)),
            material=mats["wood_dark"],
            name="main_handle_end", material_class_id="wood.walnut_dark",
        )
    elif r.grip_form == "breast_plate":
        body.visual(
            Cylinder(radius=0.0175 * s, length=0.014 * s),
            origin=_o(s, 0.105, 0.0, -0.050, rpy=_RY),
            material=mats["steel"],
            name="handle_ferrule", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
        )
        body.visual(
            mesh_from_cadquery(_breast_plate_mesh_shape(), "wood_breast_plate", tolerance=0.00065, unit_scale=s),
            material=mats["wood"],
            name="main_handle", material_class_id="wood.polished_varnished",
        )
        body.visual(
            mesh_from_cadquery(_breast_plate_end_shape(), "breast_plate_endgrain", tolerance=0.00055, unit_scale=s),
            material=mats["wood_dark"],
            name="main_handle_end", material_class_id="wood.walnut_dark",
        )
    else:  # straight_barrel_handle (origin)
        body.visual(
            Cylinder(radius=0.0165 * s, length=0.010 * s),
            origin=_o(s, 0.109, 0.0, -0.050, rpy=_RY),
            material=mats["steel"],
            name="handle_ferrule", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
        )
        body.visual(
            _wood_handle_mesh("main_wood_handle", radius=0.0165 * s, length=0.130 * s),
            origin=_o(s, 0.108, 0.0, -0.050, rpy=_RY),
            material=mats["wood"],
            name="main_handle", material_class_id="wood.polished_varnished",
        )
        body.visual(
            Cylinder(radius=0.0090 * s, length=0.003 * s),
            origin=_o(s, 0.238, 0.0, -0.050, rpy=_RY),
            material=mats["wood_dark"],
            name="main_handle_end", material_class_id="wood.walnut_dark",
        )

    # --- selector mount (sliding uses a cast guide; others a small cobalt boss). ---
    if r.speed_selection == "sliding_two_speed":
        body.visual(
            mesh_from_cadquery(_build_selector_mount(), "two_speed_selector_mount", tolerance=0.00045, unit_scale=s),
            material=mats["frame"],
            name="selector_mount", material_class_id=("metal.paint_coated" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "black_japanned", "forest_green_enamel"} else "metal.cast_iron_bare"),
        )
    elif r.speed_selection == "reversible_ratchet":
        body.visual(
            Cylinder(radius=0.0090 * s, length=0.014 * s),
            origin=_o(s, 0.050, 0.020, -0.050, rpy=_RX),
            material=mats["dark_steel"],
            name="selector_mount", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_aged"),
        )
    else:  # pivot_lever
        body.visual(
            Cylinder(radius=0.0080 * s, length=0.012 * s),
            origin=_o(s, 0.050, 0.020, -0.050, rpy=_RX),
            material=mats["frame"],
            name="selector_mount", material_class_id=("metal.paint_coated" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "black_japanned", "forest_green_enamel"} else "metal.cast_iron_bare"),
        )

    # --- enclosed bevel housing (extra body visual for that gear_train). ---
    if r.gear_train == "enclosed_bevel":
        body.visual(
            mesh_from_cadquery(_build_enclosed_bevel_housing(), "enclosed_bevel_housing", tolerance=0.00055, unit_scale=s),
            material=mats["frame"],
            name="enclosed_bevel_housing", material_class_id=("metal.paint_coated" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "black_japanned", "forest_green_enamel"} else "metal.cast_iron_bare"),
        )
    return body


def _build_drive_gear(model, r, mats) -> tuple[object, str]:
    """drive_gear part per gear_train. Returns (part, tooth_visual_name)."""
    s = r.s
    drive_gear = model.part("drive_gear")
    if r.gear_train == "single_pinion_crown":
        drive_gear.visual(
            mesh_from_cadquery(_build_single_pinion_drive_wheel(), "single_pinion_drive_wheel", tolerance=0.0004, unit_scale=s),
            material=mats["steel"],
            name="toothed_wheel", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
        )
        drive_gear.visual(Cylinder(radius=0.0090 * s, length=0.002 * s), origin=_o(s, 0.0, 0.037, 0.0, rpy=_RX), material=mats["frame"], name="blue_gear_face", material_class_id=("metal.paint_coated" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "black_japanned", "forest_green_enamel"} else "metal.cast_iron_bare"))
        drive_gear.visual(Cylinder(radius=0.0105 * s, length=0.014 * s), origin=_o(s, 0.0, 0.035, 0.0, rpy=_RX), material=mats["steel"], name="gear_hub", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"))
        tooth_name = "toothed_wheel"
    elif r.gear_train == "dual_pinion":
        for index, pinion_y in ((0, 0.015), (1, 0.027)):
            pinion = _build_toothed_wheel(root_radius=0.0450, outer_radius=0.0510, width=0.006, tooth_count=40, bore_radius=0.0053, tooth_width=0.0048)
            drive_gear.visual(
                mesh_from_cadquery(pinion, f"dual_drive_pinion_{index}", tolerance=0.00045, unit_scale=s),
                origin=_o(s, 0.0, pinion_y, 0.0, rpy=_RX),
                material=mats["steel"],
                name=f"drive_pinion_{index}", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
            )
        drive_gear.visual(Cylinder(radius=0.0385 * s, length=0.018 * s), origin=_o(s, 0.0, 0.022, 0.0, rpy=_RX), material=mats["frame"], name="pinion_bridge", material_class_id=("metal.paint_coated" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "black_japanned", "forest_green_enamel"} else "metal.cast_iron_bare"))
        drive_gear.visual(Cylinder(radius=0.0105 * s, length=0.016 * s), origin=_o(s, 0.0, 0.038, 0.0, rpy=_RX), material=mats["steel"], name="gear_hub", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"))
        tooth_name = "drive_pinion_0"
    elif r.gear_train == "enclosed_bevel":
        drive_gear.visual(
            mesh_from_cadquery(_build_bevel_drive_wheel(), "bevel_drive_gear", tolerance=0.00040, unit_scale=s),
            origin=_o(s, 0.0, 0.018, 0.0, rpy=_RX),
            material=mats["steel"],
            name="bevel_wheel", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
        )
        drive_gear.visual(Cylinder(radius=0.0300 * s, length=0.003 * s), origin=_o(s, 0.0, 0.027, 0.0, rpy=_RX), material=mats["frame"], name="bevel_backplate", material_class_id=("metal.paint_coated" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "black_japanned", "forest_green_enamel"} else "metal.cast_iron_bare"))
        drive_gear.visual(Cylinder(radius=0.0105 * s, length=0.012 * s), origin=_o(s, 0.0, 0.029, 0.0, rpy=_RX), material=mats["steel"], name="gear_hub", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"))
        tooth_name = "bevel_wheel"
    else:  # open_spur_gear (origin)
        large_gear = _build_toothed_wheel(root_radius=0.0450, outer_radius=0.0510, width=0.008, tooth_count=40, bore_radius=0.0053, tooth_width=0.0048)
        drive_gear.visual(
            mesh_from_cadquery(large_gear, "large_drive_gear", tolerance=0.00045, unit_scale=s),
            origin=_o(s, 0.0, 0.020, 0.0, rpy=_RX),
            material=mats["steel"],
            name="toothed_wheel", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
        )
        drive_gear.visual(Cylinder(radius=0.0385 * s, length=0.004 * s), origin=_o(s, 0.0, 0.030, 0.0, rpy=_RX), material=mats["frame"], name="blue_gear_face", material_class_id=("metal.paint_coated" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "black_japanned", "forest_green_enamel"} else "metal.cast_iron_bare"))
        drive_gear.visual(Cylinder(radius=0.0105 * s, length=0.014 * s), origin=_o(s, 0.0, 0.035, 0.0, rpy=_RX), material=mats["steel"], name="gear_hub", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"))
        tooth_name = "toothed_wheel"

    # Shared drive-gear hardware (shaft + thrust washer), all gear_trains.
    shaft_len = 0.068 if r.gear_train == "enclosed_bevel" else 0.048
    shaft_y = 0.016 if r.gear_train == "enclosed_bevel" else 0.006
    drive_gear.visual(Cylinder(radius=0.0052 * s, length=shaft_len * s), origin=_o(s, 0.0, shaft_y, 0.0, rpy=_RX), material=mats["dark_steel"], name="gear_shaft", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_aged"))
    drive_gear.visual(Cylinder(radius=0.0100 * s, length=0.002 * s), origin=_o(s, 0.0, 0.0, 0.0, rpy=_RX), material=mats["steel"], name="thrust_washer", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"))
    return drive_gear, tooth_name


def _build_spindle(model, r, mats) -> object:
    """spindle part: shaft + pinion + chuck nose (per chuck slot) + backstop."""
    s = r.s
    spindle = model.part("spindle")
    spindle.visual(Cylinder(radius=0.0065 * s, length=0.151 * s), origin=_o(s, -0.0025, 0.0, 0.0, rpy=_RY), material=mats["dark_steel"], name="spindle_shaft", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_aged"))
    pinion = _build_toothed_wheel(root_radius=0.0105, outer_radius=0.0135, width=0.010, tooth_count=14, bore_radius=0.0041, tooth_width=0.0040)
    spindle.visual(
        mesh_from_cadquery(pinion, "spindle_pinion", tolerance=0.00035, unit_scale=s),
        origin=_o(s, -0.005, 0.0, 0.0, rpy=_RY),
        material=mats["steel"],
        name="pinion_gear", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
    )
    if r.chuck == "collet_chuck":
        spindle.visual(
            mesh_from_cadquery(_collet_nose_shape(), "collet_chuck_nose", tolerance=0.00022, unit_scale=s),
            origin=_o(s, -0.075, 0.0, 0.0, rpy=(0.0, -math.pi / 2.0, 0.0)),
            material=mats["steel"],
            name="chuck_nose", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
        )
    else:  # keyed_geared_chuck
        spindle.visual(
            _keyed_chuck_nose_mesh() if s == 1.0 else mesh_from_geometry(
                LatheGeometry(
                    [(rr * s, zz * s) for rr, zz in (
                        (0.0065, 0.000), (0.0105, 0.006), (0.0120, 0.014), (0.0110, 0.030),
                        (0.0082, 0.044), (0.0048, 0.054), (0.0022, 0.061), (0.0000, 0.064),
                    )],
                    segments=48,
                ),
                "chuck_nose",
            ),
            origin=_o(s, -0.075, 0.0, 0.0, rpy=(0.0, -math.pi / 2.0, 0.0)),
            material=mats["steel"],
            name="chuck_nose", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
        )
    spindle.visual(Cylinder(radius=0.0150 * s, length=0.002 * s), origin=_o(s, -0.083, 0.0, 0.0, rpy=_RY), material=mats["dark_steel"], name="chuck_backstop", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_aged"))
    return spindle


def _build_chuck_sleeve(model, r, mats) -> object:
    s = r.s
    chuck_sleeve = model.part("chuck_sleeve")
    if r.chuck == "collet_chuck":
        chuck_sleeve.visual(
            mesh_from_cadquery(_build_collet_nut(), "collet_chuck_nut", tolerance=0.00024, unit_scale=s),
            origin=_o(s, 0.0, 0.0, 0.0, rpy=(0.0, -math.pi / 2.0, 0.0)),
            material=mats["steel"],
            name="knurled_sleeve", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
        )
    else:  # keyed_geared_chuck: knurled toothed ring
        chuck_ring = _build_toothed_wheel(root_radius=0.0150, outer_radius=0.0172, width=0.028, tooth_count=32, bore_radius=0.01225, tooth_width=0.0022)
        chuck_sleeve.visual(
            mesh_from_cadquery(chuck_ring, "knurled_chuck_sleeve", tolerance=0.00028, unit_scale=s),
            origin=_o(s, 0.0, 0.0, 0.0, rpy=(0.0, -math.pi / 2.0, 0.0)),
            material=mats["steel"],
            name="knurled_sleeve", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
        )
    return chuck_sleeve


def _build_crank(model, r, mats) -> tuple[object, float, float]:
    """crank part. Returns (part, endpoint_x_scaled, endpoint_z_scaled) for the
    grip joint origin. crank_reach_scale (cr) lengthens the arm; unit_scale (s)
    scales everything uniformly."""
    s, cr = r.s, r.cr
    ex_local = _CRANK_ENDPOINT_X * cr
    ez_local = _CRANK_ENDPOINT_Z * cr
    crank = model.part("crank")
    crank.visual(
        mesh_from_cadquery(_build_crank_arm(ex_local, ez_local), "offset_crank_arm", tolerance=0.00055, unit_scale=s),
        material=mats["steel"],
        name="crank_arm", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
    )
    crank.visual(Cylinder(radius=0.0060 * s, length=0.003 * s), origin=_o(s, 0.0, 0.0090, 0.0, rpy=_RX), material=mats["dark_steel"], name="crank_fastener", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_aged"))
    return crank, ex_local * s, ez_local * s


def _build_crank_grip(model, r, mats) -> object:
    s = r.s
    crank_grip = model.part("crank_grip")
    crank_grip.visual(Cylinder(radius=0.0042 * s, length=0.024 * s), origin=_o(s, 0.0, 0.012, 0.0, rpy=_RX), material=mats["dark_steel"], name="grip_axle", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_aged"))
    crank_grip.visual(
        _wood_handle_mesh("crank_wood_grip", radius=0.0115 * s, length=0.045 * s),
        origin=_o(s, 0.0, 0.018, 0.0, rpy=_RX),
        material=mats["wood"],
        name="wood_grip", material_class_id="wood.polished_varnished",
    )
    crank_grip.visual(Cylinder(radius=0.0065 * s, length=0.0025 * s), origin=_o(s, 0.0, 0.063, 0.0, rpy=_RX), material=mats["wood_dark"], name="grip_end", material_class_id="wood.walnut_dark")
    return crank_grip


def _build_speed_lever(model, r, mats) -> object:
    """speed_lever part per speed_selection slot."""
    s = r.s
    speed_lever = model.part("speed_lever")
    if r.speed_selection == "sliding_two_speed":
        speed_lever.visual(Box((0.014 * s, 0.005 * s, 0.010 * s)), origin=_o(s, 0.0, 0.0025, 0.0), material=mats["steel"], name="selector_boss", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"))
        speed_lever.visual(Box((0.005 * s, 0.014 * s, 0.006 * s)), origin=_o(s, 0.0, 0.011, 0.0), material=mats["frame"], name="selector_arm", material_class_id=("metal.paint_coated" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "black_japanned", "forest_green_enamel"} else "metal.cast_iron_bare"))
        speed_lever.visual(Cylinder(radius=0.0052 * s, length=0.018 * s), origin=_o(s, 0.0, 0.019, 0.0), material=mats["steel"], name="selector_tip", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"))
    elif r.speed_selection == "reversible_ratchet":
        speed_lever.visual(Cylinder(radius=0.0068 * s, length=0.008 * s), origin=_o(s, 0.0, 0.003, 0.0, rpy=_RX), material=mats["steel"], name="selector_boss", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"))
        speed_lever.visual(
            mesh_from_cadquery(_build_ratchet_selector_arm(0.022, 0.010), "ratchet_selector_arm", tolerance=0.0003, unit_scale=s),
            material=mats["steel"],
            name="selector_arm", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"),
        )
        speed_lever.visual(Cylinder(radius=0.0068 * s, length=0.010 * s), origin=_o(s, 0.022, 0.005, 0.010, rpy=_RX), material=mats["dark_steel"], name="selector_tip", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_aged"))
    else:  # pivot_lever (origin)
        speed_lever.visual(Cylinder(radius=0.0065 * s, length=0.008 * s), origin=_o(s, 0.0, 0.004, 0.0, rpy=_RX), material=mats["steel"], name="selector_boss", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"))
        speed_lever.visual(Box((0.006 * s, 0.006 * s, 0.027 * s)), origin=_o(s, 0.004, 0.0, -0.014), material=mats["frame"], name="selector_arm", material_class_id=("metal.paint_coated" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "black_japanned", "forest_green_enamel"} else "metal.cast_iron_bare"))
        speed_lever.visual(Cylinder(radius=0.0052 * s, length=0.012 * s), origin=_o(s, 0.004, 0.0, -0.031, rpy=(math.pi / 2.0, 0.0, 0.0)), material=mats["steel"], name="selector_tip", material_class_id=("metal.steel_bare" if r.palette_style in {"cobalt_enamel", "oxblood_enamel", "forest_green_enamel", "bare_cast_steel"} else "metal.brass_polished"))
    return speed_lever


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_manual_hand_drill(
    config: ManualHandDrillConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    s = r.s
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"mhd_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_body(model, r, mats)
    drive_gear, _tooth = _build_drive_gear(model, r, mats)
    spindle = _build_spindle(model, r, mats)
    chuck_sleeve = _build_chuck_sleeve(model, r, mats)
    crank, ex, ez = _build_crank(model, r, mats)
    crank_grip = _build_crank_grip(model, r, mats)
    speed_lever = _build_speed_lever(model, r, mats)

    model.articulation(
        "body_to_drive_gear", ArticulationType.CONTINUOUS, parent=body, child=drive_gear,
        origin=_o(s, 0.0, 0.0, 0.015), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=5.0),
    )
    model.articulation(
        "body_to_spindle", ArticulationType.CONTINUOUS, parent=body, child=spindle,
        origin=_o(s, 0.0, 0.0, -0.050), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=12.0),
    )
    model.articulation(
        "spindle_to_chuck_sleeve", ArticulationType.REVOLUTE, parent=spindle, child=chuck_sleeve,
        origin=_o(s, -0.084, 0.0, 0.0), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=4.0, lower=-math.pi, upper=math.pi),
    )
    # enclosed_bevel: the crank mounts on the front cover of the gearcase pod
    # (front face y≈0.047), so stand the crank proud to clear the housing.
    crank_mount_y = 0.052 if r.gear_train == "enclosed_bevel" else 0.046
    model.articulation(
        "drive_gear_to_crank", ArticulationType.CONTINUOUS, parent=drive_gear, child=crank,
        origin=_o(s, 0.0, crank_mount_y, 0.0), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=5.0),
    )
    model.articulation(
        "crank_to_grip", ArticulationType.CONTINUOUS, parent=crank, child=crank_grip,
        origin=Origin(xyz=(ex, 0.006 * s, ez)), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=10.0),
    )

    # speed_selection joint (② axis: REVOLUTE +Y vs PRISMATIC +X).
    if r.speed_selection == "sliding_two_speed":
        upper = _clamp(_SLIDE_TRAVEL * r.st, 0.016, _SLIDE_TRAVEL) * s
        model.articulation(
            "body_to_speed_lever", ArticulationType.PRISMATIC, parent=body, child=speed_lever,
            origin=_o(s, 0.030, 0.024, -0.050), axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=18.0, velocity=0.10, lower=0.0, upper=upper),
        )
    else:
        nominal = _RATCHET_RANGE if r.speed_selection == "reversible_ratchet" else _PIVOT_RANGE
        rng = _clamp(nominal * r.st, 0.22, 0.60)
        model.articulation(
            "body_to_speed_lever", ArticulationType.REVOLUTE, parent=body, child=speed_lever,
            origin=_o(s, 0.050, 0.026, -0.050), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=1.5, velocity=2.0, lower=-rng, upper=rng),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_manual_hand_drill(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_manual_hand_drill(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _declare_captured_overlaps(ctx, model, r, tooth_name: str) -> None:
    body = model.get_part("body")
    drive_gear = model.get_part("drive_gear")
    spindle = model.get_part("spindle")
    chuck_sleeve = model.get_part("chuck_sleeve")
    crank = model.get_part("crank")
    crank_grip = model.get_part("crank_grip")

    # (a) drive gear teeth mesh the spindle pinion.
    ctx.allow_overlap(drive_gear, spindle, elem_a=tooth_name, elem_b="pinion_gear",
                      reason="drive gear teeth mesh the spindle pinion.")
    # (b) spindle shaft rides the hollow cast bearing bore.
    ctx.allow_overlap(spindle, body, elem_a="spindle_shaft", elem_b="cast_frame",
                      reason="spindle shaft is captured by the cast bearing sleeve bore.")
    ctx.allow_overlap(spindle, body, elem_a="pinion_gear", elem_b="cast_frame",
                      reason="spindle pinion runs inside the frame pinion pocket.")
    # (c) drive gear shaft / thrust washer captured by the frame side plate.
    ctx.allow_overlap(drive_gear, body, elem_a="gear_shaft", elem_b="cast_frame",
                      reason="drive gear shaft passes through the side-plate bearing.")
    ctx.allow_overlap(drive_gear, body, elem_a="thrust_washer", elem_b="cast_frame",
                      reason="drive gear thrust washer seats against the side plate.")
    # (d) crank fastener captured on the gear hub.
    ctx.allow_overlap(crank, drive_gear, elem_a="crank_fastener", elem_b="gear_hub",
                      reason="crank fastener is captured on the drive gear hub.")
    # (e) grip axle captured in the crank grip eye.
    ctx.allow_overlap(crank_grip, crank, elem_a="grip_axle", elem_b="crank_arm",
                      reason="grip axle is captured in the crank arm grip eye.")
    # (e2) crank boss captures the drive gear shaft end.
    ctx.allow_overlap(crank, drive_gear, elem_a="crank_arm", elem_b="gear_shaft",
                      reason="crank centre boss captures the drive gear shaft.")
    # (f) chuck sleeve captures the spindle nose + backstop.
    ctx.allow_overlap(chuck_sleeve, spindle, elem_a="knurled_sleeve", elem_b="chuck_nose",
                      reason="chuck sleeve/nut captures the spindle chuck nose.")
    ctx.allow_overlap(chuck_sleeve, spindle, elem_a="knurled_sleeve", elem_b="chuck_backstop",
                      reason="chuck sleeve seats against the chuck backstop.")
    # (g) enclosed bevel wheel runs inside the cast housing.
    if r.gear_train == "enclosed_bevel":
        ctx.allow_overlap(drive_gear, body, elem_a="bevel_wheel", elem_b="enclosed_bevel_housing",
                          reason="bevel wheel runs inside the enclosed cast housing.")
        ctx.allow_overlap(drive_gear, body, elem_a="gear_shaft", elem_b="enclosed_bevel_housing",
                          reason="gear shaft runs through the housing bearings.")
    # (h) selector captured in its mount / guide.
    speed_lever = model.get_part("speed_lever")
    ctx.allow_overlap(speed_lever, body, elem_a="selector_boss", elem_b="selector_mount",
                      reason="selector boss/carriage is captured in the mount/guide.")


def run_manual_hand_drill_tests(
    object_model: ArticulatedObject,
    config: ManualHandDrillConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    tooth_name = {
        "single_pinion_crown": "toothed_wheel",
        "dual_pinion": "drive_pinion_0",
        "enclosed_bevel": "bevel_wheel",
        "open_spur_gear": "toothed_wheel",
    }[r.gear_train]
    _declare_captured_overlaps(ctx, object_model, r, tooth_name)

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()

    # ---- Structure / identity. ----
    part_names = {p.name for p in object_model.parts}
    expected = {"body", "drive_gear", "spindle", "chuck_sleeve", "crank", "crank_grip", "speed_lever"}
    ctx.check("7-part skeleton present", expected <= part_names, details=str(sorted(part_names)))

    # ---- Joint topology. ----
    for jn, jtype, axis in (
        ("body_to_drive_gear", ArticulationType.CONTINUOUS, (0.0, 1.0, 0.0)),
        ("body_to_spindle", ArticulationType.CONTINUOUS, (1.0, 0.0, 0.0)),
        ("spindle_to_chuck_sleeve", ArticulationType.REVOLUTE, (1.0, 0.0, 0.0)),
        ("drive_gear_to_crank", ArticulationType.CONTINUOUS, (0.0, 1.0, 0.0)),
        ("crank_to_grip", ArticulationType.CONTINUOUS, (0.0, 1.0, 0.0)),
    ):
        j = object_model.get_articulation(jn)
        ctx.check(f"{jn} type/axis", j.articulation_type == jtype and all(abs(a - b) < 1e-9 for a, b in zip(j.axis, axis)),
                  details=f"type={j.articulation_type} axis={tuple(j.axis)}")

    sel = object_model.get_articulation("body_to_speed_lever")
    if r.speed_selection == "sliding_two_speed":
        ctx.check("selector is PRISMATIC +X", sel.articulation_type == ArticulationType.PRISMATIC and abs(sel.axis[0]) > 0.99,
                  details=f"type={sel.articulation_type} axis={tuple(sel.axis)}")
    else:
        ctx.check("selector is REVOLUTE +Y", sel.articulation_type == ArticulationType.REVOLUTE and abs(sel.axis[1]) > 0.99,
                  details=f"type={sel.articulation_type} axis={tuple(sel.axis)}")

    # ---- Category proportions (from the origin run_tests). ----
    body = object_model.get_part("body")
    chuck_box = ctx.part_world_aabb(object_model.get_part("chuck_sleeve"))
    body_box = ctx.part_world_aabb(body)
    if chuck_box is not None and body_box is not None:
        ctx.check("chuck projects ahead of the cast body", chuck_box[0][0] < body_box[0][0] - 0.010 * r.s,
                  details=f"chuck={chuck_box} body={body_box}")

    # ---- Rule 5: sampled-pose motion + targeted checks. ----
    drive_j = object_model.get_articulation("body_to_drive_gear")
    crank_j = object_model.get_articulation("drive_gear_to_crank")
    spindle_j = object_model.get_articulation("body_to_spindle")
    chuck_j = object_model.get_articulation("spindle_to_chuck_sleeve")

    crank = object_model.get_part("crank")
    crank_grip = object_model.get_part("crank_grip")
    speed_lever = object_model.get_part("speed_lever")

    # crank orbit turns the free grip around the wheel.
    grip0 = ctx.part_world_position(crank_grip)
    with ctx.pose({drive_j: math.pi / 2.0, crank_j: math.pi / 2.0}):
        crank_turned = ctx.part_world_aabb(crank)
        grip1 = ctx.part_world_position(crank_grip)
    if grip0 is not None and grip1 is not None:
        moved = math.dist(grip0, grip1)
        ctx.check("crank orbit displaces the free grip", moved > 0.02 * r.s and crank_turned is not None,
                  details=f"grip moved {moved:.4f}")

    # spindle + chuck spin.
    with ctx.pose({spindle_j: math.pi / 2.0, chuck_j: 0.8}):
        ctx.check("spindle+chuck rotate without error", ctx.part_world_aabb(object_model.get_part("chuck_sleeve")) is not None)

    # selector travels within range. Measure an AABB corner (the part origin sits
    # on the rotation axis for the revolute selectors, so it never moves).
    lim = sel.motion_limits
    sel_target = (lim.upper or 0.0) if r.speed_selection == "sliding_two_speed" else (lim.upper or 0.42)
    box0 = ctx.part_world_aabb(speed_lever)
    with ctx.pose({sel: sel_target}):
        box1 = ctx.part_world_aabb(speed_lever)
    if box0 is not None and box1 is not None:
        corner_move = max(math.dist(box0[i], box1[i]) for i in (0, 1))
        ctx.check("selector actuates", corner_move > 0.001 * r.s, details=f"selector corner moved {corner_move:.5f}")

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    ctx.check("slot_choices recorded", tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
              details=str(object_model.meta.get("slot_choices")))

    return ctx.report()


__all__ = (
    "ManualHandDrillConfig",
    "ResolvedManualHandDrillConfig",
    "build_manual_hand_drill",
    "build_seeded_manual_hand_drill",
    "config_from_seed",
    "resolve_config",
    "run_manual_hand_drill_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
