# SPDX-License-Identifier: Apache-2.0

"""Stylized countertop microwave oven — modular procedural template.

NOTE on the slug name: ``microwave`` here = **countertop microwave oven** (a
stylized box with a hinged/sliding front door + a rotating turntable + a right
control strip), NOT a toaster oven, NOT a built-in/wall oven (those have their
own slugs). The structure family is a chamfered ``body`` shell (root, grounded
on four feet) whose front-left three quarters are cut into a dark cooking
cavity and whose right quarter holds a control panel, plus a front ``door`` (or
``drawer``) mechanism, a cavity ``turntable`` (or fixed flatbed glass floor),
and an optional interior wire ``shelf_rack``.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Kitchen_Microwave.md`` and the
``picture/Kitchen/Microwave`` 5-star sample pool (1 parent + 7 slot-fork
variants), all synced under ``data/records/``.

Structure (pattern = ``parallel_children``): a single root ``body`` part, with
four named module axes attaching as parallel children / inline visuals:

  * ``door_mechanism`` (4): the front opening mechanism — side_hinge (1 REVOLUTE
    -Z, vertical), drop_down (1 REVOLUTE +X, bottom horizontal), top_hinge
    (1 REVOLUTE -X, top horizontal), drawer_prismatic (1 PRISMATIC -Y; renames
    the part ``drawer`` and *reparents the turntable onto the drawer*).
  * ``turntable`` (2): rotating (1 CONTINUOUS +Z glass plate on a drive hub) /
    flatbed (a fixed glass floor inlined as a body visual, no joint).
  * ``control`` (3): membrane (a charcoal strip, no joint, Rule 1) /
    rotary_dials (2 skirted KnobGeometry knobs, 2 REVOLUTE -Y, 0..270 deg) /
    touch_glass (a recessed dark glass pane + backing + touch marks, no joint).
  * ``interior_rack`` (2): none / shelf (a mid-level wire grid, 1 FIXED joint,
    resting on body cavity-wall support ledges).

Defining motion (always >= 1 non-fixed joint): the door REVOLUTE (or drawer
PRISMATIC) plus the turntable CONTINUOUS; rotary_dials adds 2 REVOLUTE; the
rack FIXED joint never counts as the defining motion.

All hinge pins / sliders / floor-seats / knob bases are captured / seated
geometry, so those joints omit ``MatingContract`` (grandfathered) and are
guarded by the flat articulation-origin baseline + element-scoped
``allow_overlap`` (mirroring each source record's run_tests allow_overlap
block, esp. the drawer's outer_shell <-> drawer_tray nesting).

Compatibility gating (resolve_config, spec §9):
  * door=drawer reparents the turntable (and, for flatbed, the fixed glass
    floor) onto the drawer so they travel with it.
  * door=drawer forces interior_rack=none (rack supports anchor body cavity
    walls; rack x drawer interference is not vetted -> conservative gate).
  * the turntable parent / origin is *derived* from the door choice, not a gate.
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
    KnobBore,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    KnobSkirt,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

DoorMechanism = Literal["side_hinge", "drop_down", "top_hinge", "drawer_prismatic"]
Turntable = Literal["rotating", "flatbed"]
Control = Literal["membrane", "rotary_dials", "touch_glass"]
InteriorRack = Literal["none", "shelf"]
PaletteStyle = Literal[
    "pale_blue_gray",
    "white_appliance",
    "black_appliance",
    "stainless_steel",
    "cream_retro",
]

DOOR_MECHANISMS: tuple[DoorMechanism, ...] = (
    "side_hinge",
    "drop_down",
    "top_hinge",
    "drawer_prismatic",
)
TURNTABLES: tuple[Turntable, ...] = ("rotating", "flatbed")
CONTROLS: tuple[Control, ...] = ("membrane", "rotary_dials", "touch_glass")
INTERIOR_RACKS: tuple[InteriorRack, ...] = ("none", "shelf")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "pale_blue_gray",
    "white_appliance",
    "black_appliance",
    "stainless_steel",
    "cream_retro",
)

# Coarse tessellation for the cadquery shell/door meshes: they are simple
# chamfered boxes with one or two cuts, so a loose linear+angular deflection
# keeps the mesh light under parallel sweep load without changing topology.
_MESH_TOL = 0.0025
_MESH_ANG = 0.4

# ----------------------------------------------------------------------------
# Palette colorways (spec §7). Every .visual(material=...) is driven from one
# of these per-seed maps. Keys are role tokens; values are rgba.
# ----------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "pale_blue_gray": {
        "shell": (0.70, 0.76, 0.80, 1.0),
        "door": (0.17, 0.18, 0.20, 1.0),
        "window": (0.055, 0.055, 0.065, 1.0),
        "cavity": (0.09, 0.09, 0.10, 1.0),
        "foot": (0.21, 0.22, 0.24, 1.0),
        "handle": (0.70, 0.76, 0.80, 1.0),
        "panel": (0.17, 0.18, 0.20, 1.0),
        "glass": (0.60, 0.64, 0.66, 1.0),
        "hub": (0.25, 0.26, 0.28, 1.0),
        "rail": (0.45, 0.47, 0.50, 1.0),
        "knob": (0.22, 0.23, 0.25, 1.0),
        "accent": (0.55, 0.58, 0.62, 1.0),
        "wire": (0.45, 0.47, 0.50, 1.0),
    },
    "white_appliance": {
        "shell": (0.93, 0.93, 0.94, 1.0),
        "door": (0.14, 0.14, 0.16, 1.0),
        "window": (0.05, 0.05, 0.06, 1.0),
        "cavity": (0.10, 0.10, 0.11, 1.0),
        "foot": (0.20, 0.20, 0.22, 1.0),
        "handle": (0.66, 0.68, 0.70, 1.0),
        "panel": (0.16, 0.16, 0.18, 1.0),
        "glass": (0.58, 0.60, 0.62, 1.0),
        "hub": (0.30, 0.31, 0.33, 1.0),
        "rail": (0.55, 0.57, 0.60, 1.0),
        "knob": (0.20, 0.20, 0.22, 1.0),
        "accent": (0.62, 0.64, 0.66, 1.0),
        "wire": (0.55, 0.57, 0.60, 1.0),
    },
    "black_appliance": {
        "shell": (0.085, 0.085, 0.095, 1.0),
        "door": (0.045, 0.045, 0.055, 1.0),
        "window": (0.02, 0.02, 0.03, 1.0),
        "cavity": (0.06, 0.06, 0.07, 1.0),
        "foot": (0.14, 0.14, 0.16, 1.0),
        "handle": (0.62, 0.64, 0.66, 1.0),
        "panel": (0.10, 0.10, 0.12, 1.0),
        "glass": (0.40, 0.42, 0.45, 1.0),
        "hub": (0.20, 0.21, 0.23, 1.0),
        "rail": (0.50, 0.52, 0.55, 1.0),
        "knob": (0.16, 0.16, 0.18, 1.0),
        "accent": (0.58, 0.60, 0.63, 1.0),
        "wire": (0.50, 0.52, 0.55, 1.0),
    },
    "stainless_steel": {
        "shell": (0.62, 0.64, 0.66, 1.0),
        "door": (0.10, 0.10, 0.12, 1.0),
        "window": (0.03, 0.03, 0.04, 1.0),
        "cavity": (0.09, 0.09, 0.10, 1.0),
        "foot": (0.30, 0.31, 0.33, 1.0),
        "handle": (0.74, 0.76, 0.78, 1.0),
        "panel": (0.12, 0.12, 0.14, 1.0),
        "glass": (0.52, 0.55, 0.57, 1.0),
        "hub": (0.40, 0.42, 0.44, 1.0),
        "rail": (0.66, 0.68, 0.70, 1.0),
        "knob": (0.18, 0.18, 0.20, 1.0),
        "accent": (0.72, 0.74, 0.76, 1.0),
        "wire": (0.66, 0.68, 0.70, 1.0),
    },
    "cream_retro": {
        "shell": (0.92, 0.88, 0.78, 1.0),
        "door": (0.30, 0.26, 0.22, 1.0),
        "window": (0.08, 0.07, 0.06, 1.0),
        "cavity": (0.11, 0.10, 0.09, 1.0),
        "foot": (0.40, 0.36, 0.30, 1.0),
        "handle": (0.80, 0.82, 0.84, 1.0),
        "panel": (0.86, 0.80, 0.68, 1.0),
        "glass": (0.62, 0.64, 0.62, 1.0),
        "hub": (0.42, 0.40, 0.36, 1.0),
        "rail": (0.78, 0.80, 0.82, 1.0),
        "knob": (0.34, 0.30, 0.26, 1.0),
        "accent": (0.80, 0.82, 0.84, 1.0),
        "wire": (0.78, 0.80, 0.82, 1.0),
    },
}

# ----------------------------------------------------------------------------
# Base real-world dimensions (meters). World frame: x=width, y=depth (front
# face toward -Y), z=up. From the parent record (b2de7afe).
# ----------------------------------------------------------------------------
BODY_W = 0.52
BODY_D = 0.38
TOTAL_H = 0.32

FOOT_H = 0.022
FOOT_SIZE = (0.06, 0.05, FOOT_H + 0.0005)

# Cooking cavity (cut through the front face, behind the door).
CAV_W = 0.32
CAV_H = 0.20
CAV_X = -0.04
CAV_Z0 = 0.07
CAV_BACK_Y = 0.09
LINER_T = 0.004

# Door / drawer front panel (covers the left ~3/4 of the front face).
DOOR_W = 0.38
DOOR_H = 0.255
DOOR_T = 0.022
DOOR_X0 = -0.245  # left edge of the door
DOOR_CZ = 0.1725  # z-center of the closed door / drawer panel

# Control panel strip (right quarter, inset into the front face).
PANEL_CX = 0.20
PANEL_W = 0.088
PANEL_H = 0.253

# Turntable.
HUB_R = 0.032
HUB_H = 0.012
PLATE_R = 0.13
PLATE_T = 0.008

# Drawer geometry.
TRAY_W = 0.28
TRAY_DEPTH = 0.28
TRAY_T = 0.006
SLIDE_TRAVEL = 0.22
RAIL_W = 0.008
RAIL_H = 0.012
RAIL_DEPTH = 0.26
RAIL_CZ = 0.15

# Flatbed glass floor.
FB_W = 0.29
FB_D = 0.24
FB_T = 0.006

# Rotary knobs.
KNOB_DIAMETER = 0.038
KNOB_HEIGHT = 0.018
KNOB_SKIRT_DIAMETER = 0.046
KNOB_UPPER_RAD = math.radians(270.0)

# Wire shelf rack.
FRAME_RAIL = 0.005
WIRE_D = 0.003
RACK_FRAME_W = 0.27
RACK_FRAME_D = 0.24
SUPPORT_W = 0.025
SUPPORT_H = 0.006

# Continuous-parameter scale ranges (spec §7).
_BODY_W_RANGE = (0.90, 1.15)
_BODY_D_RANGE = (0.90, 1.15)
_BODY_H_RANGE = (0.88, 1.18)
_DOOR_ANGLE_RANGE = (0.85, 1.08)
_DRAWER_TRAVEL_RANGE = (0.80, 1.10)
_KNOB_SIZE_RANGE = (0.85, 1.20)
_CROSS_WIRE_RANGE = (6, 14)
_LONG_WIRE_RANGE = (3, 6)


@dataclass(frozen=True)
class MicrowaveConfig:
    door_mechanism: DoorMechanism | None = None
    turntable: Turntable | None = None
    control: Control | None = None
    interior_rack: InteriorRack | None = None
    palette_style: PaletteStyle = "pale_blue_gray"
    body_width_scale: float = 1.0
    body_depth_scale: float = 1.0
    body_height_scale: float = 1.0
    door_open_angle_scale: float = 1.0
    drawer_travel_scale: float = 1.0
    knob_size_scale: float = 1.0
    cross_wire_count: int | None = None
    long_wire_count: int | None = None
    name: str = "microwave"


@dataclass(frozen=True)
class ResolvedMicrowaveConfig:
    door_mechanism: DoorMechanism
    turntable: Turntable
    control: Control
    interior_rack: InteriorRack
    palette_style: PaletteStyle

    # Scaled geometry.
    body_w: float
    body_d: float
    total_h: float
    shell_h: float
    shell_cz: float
    front_y: float
    cav_w: float
    cav_h: float
    cav_z0: float
    cav_z1: float
    cav_back_y: float
    door_w: float
    door_h: float
    door_x0: float
    door_cz: float
    panel_cx: float
    panel_w: float
    panel_h: float
    floor_top_z: float
    tt_x: float
    tt_y: float
    plate_r: float

    # Resolved motion / derived members.
    door_open_angle: float  # radians (REVOLUTE doors)
    drawer_travel: float  # m (drawer)
    knob_diameter: float
    knob_skirt_diameter: float
    cross_wire_count: int
    long_wire_count: int
    rack_frame_w: float
    rack_bottom_z: float
    rack_yc: float
    turntable_on_drawer: bool  # turntable / flatbed travel with the drawer
    name: str

    @property
    def is_drawer(self) -> bool:
        return self.door_mechanism == "drawer_prismatic"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> MicrowaveConfig:
    rng = random.Random(seed)
    return MicrowaveConfig(
        door_mechanism=rng.choice(DOOR_MECHANISMS),
        turntable=rng.choice(TURNTABLES),
        control=rng.choice(CONTROLS),
        interior_rack=rng.choice(INTERIOR_RACKS),
        palette_style=rng.choice(PALETTE_STYLES),
        body_width_scale=round(rng.uniform(*_BODY_W_RANGE), 4),
        body_depth_scale=round(rng.uniform(*_BODY_D_RANGE), 4),
        body_height_scale=round(rng.uniform(*_BODY_H_RANGE), 4),
        door_open_angle_scale=round(rng.uniform(*_DOOR_ANGLE_RANGE), 4),
        drawer_travel_scale=round(rng.uniform(*_DRAWER_TRAVEL_RANGE), 4),
        knob_size_scale=round(rng.uniform(*_KNOB_SIZE_RANGE), 4),
        cross_wire_count=rng.randint(*_CROSS_WIRE_RANGE),
        long_wire_count=rng.randint(*_LONG_WIRE_RANGE),
        name=f"seeded_microwave_{seed}",
    )


def resolve_config(config: MicrowaveConfig | None = None) -> ResolvedMicrowaveConfig:
    cfg = config or MicrowaveConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    door_mechanism = _pick(cfg.door_mechanism, DOOR_MECHANISMS)
    turntable = _pick(cfg.turntable, TURNTABLES)
    control = _pick(cfg.control, CONTROLS)
    interior_rack = _pick(cfg.interior_rack, INTERIOR_RACKS)

    is_drawer = door_mechanism == "drawer_prismatic"

    # --- Compatibility gating (spec §9). ---
    # (2) rack supports anchor body cavity walls; rack x drawer interference is
    #     not vetted -> conservative gate: door=drawer forces rack=none.
    if is_drawer and interior_rack == "shelf":
        interior_rack = "none"

    # (1) door=drawer reparents the turntable (and the flatbed glass floor) onto
    #     the drawer so it travels with the drawer (derived, not a gate).
    turntable_on_drawer = is_drawer

    # --- Body scales (independent) -> derived cavity / door / panel. ---
    w_scale = _clamp(cfg.body_width_scale, *_BODY_W_RANGE)
    d_scale = _clamp(cfg.body_depth_scale, *_BODY_D_RANGE)
    h_scale = _clamp(cfg.body_height_scale, *_BODY_H_RANGE)

    body_w = BODY_W * w_scale
    body_d = BODY_D * d_scale
    total_h = TOTAL_H * h_scale
    shell_h = total_h - FOOT_H
    shell_cz = FOOT_H + shell_h / 2.0
    front_y = -body_d / 2.0

    # Cavity / liner derive from body scale, kept inside the footprint.
    cav_w = CAV_W * w_scale
    cav_h = CAV_H * h_scale
    cav_x = CAV_X * w_scale
    cav_z0 = CAV_Z0 * h_scale
    cav_z1 = cav_z0 + cav_h
    cav_back_y = CAV_BACK_Y * d_scale

    # Inequality: cavity must stay inside the body footprint with a wall margin.
    wall_margin = 0.03
    max_cav_w = body_w - 2.0 * wall_margin
    if cav_w > max_cav_w:
        cav_w = max_cav_w
    # Inequality: cavity height must fit inside the shell net interior.
    max_cav_h = shell_h - 2.0 * 0.035
    if cav_h > max_cav_h:
        cav_h = max_cav_h
        cav_z1 = cav_z0 + cav_h

    door_w = DOOR_W * w_scale
    door_h = DOOR_H * h_scale
    door_x0 = DOOR_X0 * w_scale
    door_cz = (cav_z0 + cav_z1) / 2.0  # door center tracks the cavity center

    # Inequality: the closed door must cover the cavity opening (door W/H >=
    # cavity opening + margin). The door already nominally exceeds the cavity;
    # enforce it after scaling so anisotropic scales can't shrink it below.
    if door_w < cav_w + 0.04:
        door_w = cav_w + 0.04
    if door_h < cav_h + 0.04:
        door_h = cav_h + 0.04

    panel_cx = PANEL_CX * w_scale
    panel_w = PANEL_W * w_scale
    panel_h = PANEL_H * h_scale

    floor_top_z = cav_z0 + LINER_T - 0.0005
    tt_x = cav_x
    tt_y = (front_y + cav_back_y) / 2.0

    # Turntable plate radius clamped so it fits in the cavity width AND clears
    # the cavity back wall / front opening along depth (the plate is centered at
    # tt_y, so its reach must stay inside [front_y, cav_back_y] with a margin).
    cav_depth_half = (cav_back_y - front_y) / 2.0
    plate_r = min(PLATE_R, cav_w / 2.0 - 0.02, cav_depth_half - 0.012)

    # --- Conditional motion params. ---
    angle_scale = _clamp(cfg.door_open_angle_scale, *_DOOR_ANGLE_RANGE)
    if door_mechanism == "drop_down":
        base_angle = math.radians(90.0)
    else:  # side_hinge / top_hinge
        base_angle = math.radians(100.0)
    door_open_angle = _clamp(base_angle * angle_scale, math.radians(60.0), math.pi * 0.95)

    travel_scale = _clamp(cfg.drawer_travel_scale, *_DRAWER_TRAVEL_RANGE)
    drawer_travel = SLIDE_TRAVEL * travel_scale
    # Inequality: travel must not exceed the rail and must keep the tray inserted
    # (>= 0.10 m overlap). Tray depth TRAY_DEPTH, rail depth RAIL_DEPTH.
    drawer_travel = _clamp(drawer_travel, 0.12, min(RAIL_DEPTH - 0.02, TRAY_DEPTH - 0.10))

    knob_scale = _clamp(cfg.knob_size_scale, *_KNOB_SIZE_RANGE)
    knob_diameter = KNOB_DIAMETER * knob_scale
    knob_skirt_diameter = KNOB_SKIRT_DIAMETER * knob_scale
    # Inequality: the two stacked knobs must not overlap vertically. Knob spacing
    # is fixed (~0.11 m apart); cap the skirt so the gap stays positive.
    knob_skirt_diameter = min(knob_skirt_diameter, 0.090)

    cross_n = int(_clamp(cfg.cross_wire_count or 10, *_CROSS_WIRE_RANGE))
    long_n = int(_clamp(cfg.long_wire_count or 4, *_LONG_WIRE_RANGE))

    rack_bottom_z = cav_z0 + cav_h * 0.5
    rack_yc = tt_y

    # Rack frame width tracks the cavity so its side rails always overlap the
    # support ledges (the supports' inner edges sit at this half-width from the
    # rack mount center tt_x); a small +overlap keeps the rail seated on top.
    support_inner_half = cav_w / 2.0 - LINER_T - (SUPPORT_W - 0.001)
    rack_frame_w = 2.0 * (support_inner_half + 0.006)

    # Inequality: the rack must clear the turntable plate top by >= 0.03 m. The
    # rack only exists alongside rotating/flatbed (rack x drawer is gated out).
    plate_top_z = floor_top_z + HUB_H + PLATE_T
    if interior_rack == "shelf" and turntable == "rotating":
        if rack_bottom_z - plate_top_z < 0.03:
            # Lift the rack to clear; cap at the cavity ceiling minus a margin.
            lifted = plate_top_z + 0.03
            rack_bottom_z = min(lifted, cav_z1 - 0.02)
            if rack_bottom_z - plate_top_z < 0.03:
                # Cavity is too short -> drop the rack rather than collide.
                interior_rack = "none"

    return ResolvedMicrowaveConfig(
        door_mechanism=door_mechanism,
        turntable=turntable,
        control=control,
        interior_rack=interior_rack,
        palette_style=palette_style,
        body_w=body_w,
        body_d=body_d,
        total_h=total_h,
        shell_h=shell_h,
        shell_cz=shell_cz,
        front_y=front_y,
        cav_w=cav_w,
        cav_h=cav_h,
        cav_z0=cav_z0,
        cav_z1=cav_z1,
        cav_back_y=cav_back_y,
        door_w=door_w,
        door_h=door_h,
        door_x0=door_x0,
        door_cz=door_cz,
        panel_cx=panel_cx,
        panel_w=panel_w,
        panel_h=panel_h,
        floor_top_z=floor_top_z,
        tt_x=tt_x,
        tt_y=tt_y,
        plate_r=plate_r,
        door_open_angle=door_open_angle,
        drawer_travel=drawer_travel,
        knob_diameter=knob_diameter,
        knob_skirt_diameter=knob_skirt_diameter,
        cross_wire_count=cross_n,
        long_wire_count=long_n,
        rack_frame_w=rack_frame_w,
        rack_bottom_z=rack_bottom_z,
        rack_yc=rack_yc,
        turntable_on_drawer=turntable_on_drawer,
        name=cfg.name or "microwave",
    )


def slot_choices_for_config(
    config: MicrowaveConfig | ResolvedMicrowaveConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedMicrowaveConfig) else resolve_config(config)
    return (
        ("door_mechanism", r.door_mechanism),
        ("turntable", r.turntable),
        ("control", r.control),
        ("interior_rack", r.interior_rack),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ----------------------------------------------------------------------------
# Mesh helpers (parameterized from the source helpers; primitive types kept).
# ----------------------------------------------------------------------------
def _shell_solid(r: ResolvedMicrowaveConfig, *, deepen_cavity: bool) -> cq.Workplane:
    """Chamfered outer shell with cavity opening and control-panel recess.

    Parent ``_shell_solid`` (b2de7afe L92-115). The drawer variant deepens the
    cavity cut (drawer L114-118) so the tray slides cleanly inside.

    The cavity cut is derived from the resolved front/back planes: the old fixed
    reach (depth 0.30 @ y=-0.06) stops short of the front face whenever
    body_depth_scale ≳ 1.105, sealing the cavity behind a solid front panel
    (PV_A seed_0000). The drawer keeps its larger forward overtravel.
    """
    shell = (
        cq.Workplane("XY")
        .box(r.body_w, r.body_d, r.shell_h)
        .translate((0.0, 0.0, r.shell_cz))
        .edges()
        .chamfer(0.012)
    )
    front_cut_y = r.front_y - (0.12 if deepen_cavity else 0.02)
    back_cut_y = r.cav_back_y
    cavity = (
        cq.Workplane("XY")
        .box(r.cav_w, back_cut_y - front_cut_y, r.cav_h)
        .translate((r.tt_x, (back_cut_y + front_cut_y) / 2.0, (r.cav_z0 + r.cav_z1) / 2.0))
    )
    shell = shell.cut(cavity)
    recess = (
        cq.Workplane("XY")
        .box(r.panel_w + 0.002, 0.012, r.panel_h + 0.002)
        .translate((r.panel_cx, r.front_y, r.door_cz))
    )
    shell = shell.cut(recess)
    # Regression guard: the cavity cut must break through the front face. A
    # face BoundingBox still spans a face's holes, so compare AREAS: the total
    # front-plane (-Y) face area must drop by (most of) the cavity opening.
    front_area = sum(
        f.Area()
        for f in shell.val().Faces()
        if f.normalAt().y < -0.99 and abs(f.Center().y - r.front_y) < 1e-3
    )
    sealed_area = (r.body_w - 0.024) * (r.shell_h - 0.024)   # chamfered front
    opening_area = r.cav_w * r.cav_h
    if front_area > sealed_area - 0.5 * opening_area:
        raise RuntimeError(
            "cavity cut failed to open the front face: front-plane area "
            f"{front_area:.4f} m^2 still ≈ sealed {sealed_area:.4f} "
            f"(opening needs ≈{opening_area:.4f})"
        )
    return shell


def _door_solid(r: ResolvedMicrowaveConfig, *, hinge: str) -> cq.Workplane:
    """Door frame mesh in the hinge-local frame.

    ``hinge`` selects the origin convention so the part frame origin sits on the
    hinge line (the joint origin), per the three REVOLUTE source variants:
      * ``side``: origin at the left-front vertical edge (parent L118-138).
      * ``bottom``: origin at the bottom-center, door extends +Z (drop_down).
      * ``top``: origin at the top-center, door extends -Z (top_hinge).
    """
    dw, dh, dt = r.door_w, r.door_h, DOOR_T
    if hinge == "side":
        # Origin on the left-front vertical edge at the shell face; the door
        # extends along +X (width) and toward -Y (front), so its back face sits
        # at local y=0 (on the shell) and the front face at y=-dt.
        door = (
            cq.Workplane("XY")
            .box(dw, dt, dh)
            .translate((dw / 2.0, -dt / 2.0, 0.0))
            .edges()
            .chamfer(0.003)
        )
        pocket = (
            cq.Workplane("XY")
            .box(dw * 0.79, 0.018, dh * 0.71)
            .translate((dw / 2.0, -dt, 0.0))
        )
    elif hinge == "bottom":
        door = (
            cq.Workplane("XY")
            .box(dw, dt, dh)
            .translate((0.0, -dt / 2.0, dh / 2.0))
            .edges()
            .chamfer(0.003)
        )
        # Window pocket kept in the lower 60% of the door so the top band stays
        # solid for the horizontal handle bar + its standoffs.
        pocket = (
            cq.Workplane("XY")
            .box(dw * 0.79, 0.016, dh * 0.58)
            .translate((0.0, -dt + 0.007, dh * 0.40))
        )
    else:  # top
        door = (
            cq.Workplane("XY")
            .box(dw, dt, dh)
            .translate((0.0, -dt / 2.0, -dh / 2.0))
            .edges()
            .chamfer(0.003)
        )
        pocket = (
            cq.Workplane("XY")
            .box(dw * 0.79, 0.018, dh * 0.71)
            .translate((0.0, -dt, -dh / 2.0))
        )
    return door.cut(pocket)


def _drawer_front_solid(r: ResolvedMicrowaveConfig) -> cq.Workplane:
    """Drawer front panel mesh in the drawer-local frame (drawer L130-152).

    Origin at the articulation point (panel center at the body front face); the
    panel extends symmetrically in Z and forward in -Y.
    """
    dw, dh, dt = r.door_w, r.door_h, DOOR_T
    frame = (
        cq.Workplane("XY")
        .box(dw, dt, dh)
        .translate((0.0, -dt / 2.0, 0.0))
        .edges("|Y")
        .chamfer(0.003)
    )
    pocket = (
        cq.Workplane("XY")
        .box(dw * 0.79, 0.009, dh * 0.71)
        .translate((0.0, -dt + 0.0045, 0.0))
    )
    return frame.cut(pocket)


def _knob_mesh(r: ResolvedMicrowaveConfig, name: str) -> object:
    """Skirted appliance rotary dial knob mesh (rotary_dials L166-184).

    KnobGeometry is aligned to local +Z with base at z=0 (center=False); the
    visual rpy=(pi/2,0,0) rotates +Z to -Y so the knob protrudes outward.
    """
    geom = KnobGeometry(
        r.knob_diameter,
        KNOB_HEIGHT,
        body_style="skirted",
        top_diameter=r.knob_diameter * 0.84,
        skirt=KnobSkirt(r.knob_skirt_diameter, 0.005, flare=0.06, chamfer=0.001),
        grip=KnobGrip(style="fluted", count=16, depth=0.0012),
        indicator=KnobIndicator(style="line", mode="engraved", depth=0.0008),
        bore=KnobBore(style="d_shaft", diameter=0.006, flat_depth=0.001),
        center=False,
    )
    return mesh_from_geometry(geom, name)


def _rack_wire(length: float, along: str = "x") -> Box:
    """Thin wire bar for the shelf-rack grid (rack L160-167)."""
    d = WIRE_D
    if along == "x":
        return Box((length, d, d))
    if along == "y":
        return Box((d, length, d))
    return Box((d, d, length))


# ----------------------------------------------------------------------------
# Body (root). Shell mesh + cavity liners + control panel + feet + per-choice
# body-side visuals (guide rails for drawer, support ledges for shelf).
# ----------------------------------------------------------------------------
def _build_body(model: ArticulatedObject, r: ResolvedMicrowaveConfig, mats, *, assets):
    body = model.part("body")
    body.visual(
        mesh_from_cadquery(
            _shell_solid(r, deepen_cavity=r.is_drawer),
            "microwave_shell",
            assets=assets,
            tolerance=_MESH_TOL,
            angular_tolerance=_MESH_ANG,
        ),
        material=mats["shell"],
        name="outer_shell", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_steel" else "metal.paint_coated"),
    )

    # Dark cavity liner panels (slightly embedded into the cut shell walls).
    liner_y_c = (r.front_y + r.cav_back_y) / 2.0 - 0.002
    liner_d = (r.cav_back_y - r.front_y) - 0.004
    liner_w = r.cav_w - 0.002
    liner_h = r.cav_h - 0.002
    cz0, cz1 = r.cav_z0, r.cav_z1
    cz_mid = (cz0 + cz1) / 2.0
    body.visual(
        Box((liner_w, liner_d, LINER_T)),
        origin=Origin(xyz=(r.tt_x, liner_y_c, cz0 + LINER_T / 2.0 - 0.0005)),
        material=mats["cavity"],
        name="cavity_floor", material_class_id="metal.paint_coated",
    )
    body.visual(
        Box((liner_w, liner_d, LINER_T)),
        origin=Origin(xyz=(r.tt_x, liner_y_c, cz1 - LINER_T / 2.0 + 0.0005)),
        material=mats["cavity"],
        name="cavity_ceiling", material_class_id="metal.paint_coated",
    )
    # The back wall liner is grown a little in X/Z and extended ~2.5 mm forward
    # (-Y) so it positively overlaps the floor / ceiling / side liners (whose
    # back edge is at liner_y_c + liner_d/2) instead of only touching them
    # edge-to-edge — otherwise it reads as a disconnected island, esp. when the
    # drawer's deeper cavity cut removes the shell just in front of it. The
    # plate radius is clamped to clear this thin wall, so no plate clash.
    back_wall_t = LINER_T + 0.0035
    back_wall_back_y = r.cav_back_y + 0.0005
    body.visual(
        Box((liner_w + 0.008, back_wall_t, liner_h + 0.008)),
        origin=Origin(xyz=(r.tt_x, back_wall_back_y - back_wall_t / 2.0, cz_mid)),
        material=mats["cavity"],
        name="cavity_back_wall", material_class_id="metal.paint_coated",
    )
    body.visual(
        Box((LINER_T, liner_d, liner_h)),
        origin=Origin(
            xyz=(r.tt_x - r.cav_w / 2.0 + LINER_T / 2.0 - 0.0005, liner_y_c, cz_mid)
        ),
        material=mats["cavity"],
        name="cavity_left_wall", material_class_id="metal.paint_coated",
    )
    body.visual(
        Box((LINER_T, liner_d, liner_h)),
        origin=Origin(
            xyz=(r.tt_x + r.cav_w / 2.0 - LINER_T / 2.0 + 0.0005, liner_y_c, cz_mid)
        ),
        material=mats["cavity"],
        name="cavity_right_wall", material_class_id="metal.paint_coated",
    )

    # Four dark block feet, grounding the unit at z=0.
    fx = 0.20 * (r.body_w / BODY_W)
    fy = 0.135 * (r.body_d / BODY_D)
    for i, (sx, sy) in enumerate([(-fx, -fy), (fx, -fy), (-fx, fy), (fx, fy)]):
        body.visual(
            Box(FOOT_SIZE),
            origin=Origin(xyz=(sx, sy, FOOT_SIZE[2] / 2.0)),
            material=mats["foot"],
            name=f"foot_{i}", material_class_id="rubber.smooth_plain",
        )

    # Drawer guide rails on the inner cavity walls (slide mechanism detail).
    # Rail top sits 0.5 mm under the tray lip bottom (cav_z0 + 0.012), so the
    # lips ride the rails at every drawer pose (contact, not overlap).
    if r.is_drawer:
        rail_y_c = (r.front_y + r.cav_back_y) / 2.0
        rail_cz = r.cav_z0 + 0.0055
        for i, x_sign in enumerate([-1.0, 1.0]):
            rail_cx = r.tt_x + x_sign * (r.cav_w / 2.0 - LINER_T - RAIL_W / 2.0 + 0.0005)
            body.visual(
                Box((RAIL_W, RAIL_DEPTH, RAIL_H)),
                origin=Origin(xyz=(rail_cx, rail_y_c, rail_cz)),
                material=mats["rail"],
                name=f"guide_rail_{i}", material_class_id="metal.steel_galvanized",
            )

    # Rack support ledges on the cavity side walls.
    if r.interior_rack == "shelf":
        support_z_c = r.rack_bottom_z - SUPPORT_H / 2.0
        cav_left_inner = r.tt_x - r.cav_w / 2.0 + LINER_T
        cav_right_inner = r.tt_x + r.cav_w / 2.0 - LINER_T
        left_x = cav_left_inner - 0.001 + SUPPORT_W / 2.0
        right_x = cav_right_inner + 0.001 - SUPPORT_W / 2.0
        for tag, sx in (("left", left_x), ("right", right_x)):
            body.visual(
                Box((SUPPORT_W, RACK_FRAME_D, SUPPORT_H)),
                origin=Origin(xyz=(sx, r.rack_yc, support_z_c)),
                material=mats["panel"],
                name=f"rack_support_{tag}", material_class_id="metal.paint_coated",
            )
    return body


# ----------------------------------------------------------------------------
# Slot C: control (membrane / rotary_dials / touch_glass). Membrane + touch are
# body inline visuals (Rule 1); rotary_dials adds 2 REVOLUTE knob parts.
# ----------------------------------------------------------------------------
def _emit_control(model, r: ResolvedMicrowaveConfig, body, mats, *, assets):
    panel_cy = r.front_y + 0.0045
    if r.control == "membrane":
        body.visual(
            Box((r.panel_w, 0.004, r.panel_h)),
            origin=Origin(xyz=(r.panel_cx, panel_cy, r.door_cz)),
            material=mats["panel"],
            name="control_panel", material_class_id="tech.control_interface",
        )
        return
    if r.control == "touch_glass":
        glass_t = 0.003
        glass_front_y = r.front_y + 0.002
        body.visual(
            Box((r.panel_w - 0.004, glass_t, r.panel_h - 0.004)),
            origin=Origin(xyz=(r.panel_cx, glass_front_y + glass_t / 2.0, r.door_cz)),
            material=mats["window"],
            name="touch_glass_panel", material_class_id="glass.smoked_tinted",
        )
        backing_front_y = glass_front_y + glass_t
        backing_back_y = r.front_y + 0.0125
        backing_t = backing_back_y - backing_front_y
        body.visual(
            Box((r.panel_w - 0.002, backing_t, r.panel_h - 0.002)),
            origin=Origin(
                xyz=(r.panel_cx, (backing_front_y + backing_back_y) / 2.0, r.door_cz)
            ),
            material=mats["panel"],
            name="touch_panel_backing", material_class_id="plastic.opaque_generic",
        )
        for i, dy in enumerate([-r.panel_h * 0.24, 0.0, r.panel_h * 0.24]):
            body.visual(
                Box((0.030, 0.001, 0.004)),
                origin=Origin(xyz=(r.panel_cx, glass_front_y + 0.0002, r.door_cz + dy)),
                material=mats["accent"],
                name=f"touch_mark_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        return

    # rotary_dials: a charcoal backing strip + 2 skirted knobs (2 REVOLUTE -Y).
    body.visual(
        Box((r.panel_w, 0.004, r.panel_h)),
        origin=Origin(xyz=(r.panel_cx, panel_cy, r.door_cz)),
        material=mats["panel"],
        name="control_panel", material_class_id="tech.control_interface",
    )
    panel_front_y = panel_cy - 0.002
    knob_specs = [
        ("power_knob", r.door_cz + r.panel_h * 0.22),
        ("timer_knob", r.door_cz - r.panel_h * 0.22),
    ]
    for knob_name, knob_z in knob_specs:
        knob_part = model.part(knob_name)
        knob_part.visual(
            _knob_mesh(r, f"{knob_name}_cap"),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["knob"],
            name=f"{knob_name}_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        # Off-center pointer tab on the knob outer face (rotation proof).
        knob_part.visual(
            Box((0.008, 0.003, 0.004)),
            origin=Origin(xyz=(0.014, -KNOB_HEIGHT, 0.0)),
            material=mats["accent"],
            name=f"{knob_name}_pointer", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            f"{knob_name}_dial",
            ArticulationType.REVOLUTE,
            parent=body,
            child=knob_part,
            origin=Origin(xyz=(r.panel_cx, panel_front_y, knob_z)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(
                effort=3.0, velocity=4.0, lower=0.0, upper=KNOB_UPPER_RAD
            ),
        )


# ----------------------------------------------------------------------------
# Slot A: door_mechanism. side/drop/top share the `door` part + `_door_solid`
# (just the origin convention + hinge axis differ); drawer renames to `drawer`.
# ----------------------------------------------------------------------------
def _emit_door(model, r: ResolvedMicrowaveConfig, body, mats, *, assets) -> str:
    if r.door_mechanism == "drawer_prismatic":
        return _emit_drawer(model, r, body, mats, assets=assets)

    door = model.part("door")
    if r.door_mechanism == "side_hinge":
        hinge_conv = "side"
    elif r.door_mechanism == "drop_down":
        hinge_conv = "bottom"
    else:
        hinge_conv = "top"

    door.visual(
        mesh_from_cadquery(
            _door_solid(r, hinge=hinge_conv),
            "microwave_door",
            assets=assets,
            tolerance=_MESH_TOL,
            angular_tolerance=_MESH_ANG,
        ),
        material=mats["door"],
        name="door_frame", material_class_id="plastic.opaque_glossy_molded",
    )

    dw, dh, dt = r.door_w, r.door_h, DOOR_T
    if r.door_mechanism == "side_hinge":
        # Local +X door; back face at local y=0 (seats on the shell), front face
        # at y=-dt; full-height vertical handle. Origin Y on the shell face.
        door.visual(
            Box((dw * 0.78, 0.004, dh * 0.70)),
            origin=Origin(xyz=(dw / 2.0, -dt + 0.0105, 0.0)),
            material=mats["window"],
            name="window_glass", material_class_id="glass.smoked_tinted",
        )
        bar_x = dw - 0.028
        door.visual(
            Box((0.018, 0.014, dh)),
            origin=Origin(xyz=(bar_x, -dt - 0.019, 0.0)),
            material=mats["handle"],
            name="handle_bar", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_steel" else "metal.paint_coated"),
        )
        for tag, sz in (("top", dh * 0.42), ("bottom", -dh * 0.42)):
            door.visual(
                Box((0.018, 0.013, 0.024)),
                origin=Origin(xyz=(bar_x, -dt - 0.006, sz)),
                material=mats["handle"],
                name=f"handle_standoff_{tag}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_steel" else "metal.paint_coated"),
            )
        door_cz = r.door_cz
        model.articulation(
            "door_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=door,
            origin=Origin(xyz=(r.door_x0, r.front_y, door_cz)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(
                effort=8.0, velocity=2.0, lower=0.0, upper=r.door_open_angle
            ),
        )
    elif r.door_mechanism == "drop_down":
        # Local frame: origin at the door bottom-center; door extends +Z. The
        # window sits in the lower band (matching the recessed pocket), leaving
        # the top band solid for the handle.
        door.visual(
            Box((dw * 0.78, 0.004, dh * 0.56)),
            origin=Origin(xyz=(0.0, -0.009, dh * 0.40)),
            material=mats["window"],
            name="window_glass", material_class_id="glass.smoked_tinted",
        )
        handle_z = dh - 0.040  # below the top chamfer so standoffs reach solid
        handle_y = -dt - 0.021
        door.visual(
            Box((dw * 0.79, 0.018, 0.014)),
            origin=Origin(xyz=(0.0, handle_y, handle_z)),
            material=mats["handle"],
            name="handle_bar", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_steel" else "metal.paint_coated"),
        )
        # Standoffs bridge the door front into the handle bar; they embed ~5 mm
        # into the door (clearing the 3 mm front-edge chamfer) and overlap the
        # bar so the handle group is not a disconnected island.
        for i, sx in enumerate([-dw * 0.32, dw * 0.32]):
            door.visual(
                Box((0.024, 0.026, 0.018)),
                origin=Origin(xyz=(sx, -dt - 0.005, handle_z)),
                material=mats["handle"],
                name=f"handle_standoff_{i}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_steel" else "metal.paint_coated"),
            )
        door_cx = r.door_x0 + dw / 2.0
        door_bottom_z = r.door_cz - dh / 2.0
        model.articulation(
            "door_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=door,
            origin=Origin(xyz=(door_cx, r.front_y, door_bottom_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=8.0, velocity=2.0, lower=0.0, upper=r.door_open_angle
            ),
        )
    else:  # top_hinge
        # Local frame: origin at the door top-center; door extends -Z.
        door.visual(
            Box((dw * 0.78, 0.004, dh * 0.70)),
            origin=Origin(xyz=(0.0, -dt + 0.0105, -dh / 2.0)),
            material=mats["window"],
            name="window_glass", material_class_id="glass.smoked_tinted",
        )
        bar_x = dw / 2.0 - 0.028
        bar_y = -dt - 0.019
        door.visual(
            Box((0.018, 0.014, dh)),
            origin=Origin(xyz=(bar_x, bar_y, -dh / 2.0)),
            material=mats["handle"],
            name="handle_bar", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_steel" else "metal.paint_coated"),
        )
        for i, z_pos in enumerate([-0.0195, -(dh - 0.0195)]):
            door.visual(
                Box((0.018, 0.013, 0.024)),
                origin=Origin(xyz=(bar_x, -dt - 0.006, z_pos)),
                material=mats["handle"],
                name=f"handle_standoff_{i}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_steel" else "metal.paint_coated"),
            )
        hinge_x = r.door_x0 + dw / 2.0
        hinge_z = r.door_cz + dh / 2.0
        model.articulation(
            "door_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=door,
            origin=Origin(xyz=(hinge_x, r.front_y, hinge_z)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=8.0, velocity=2.0, lower=0.0, upper=r.door_open_angle
            ),
        )
    return "door"


def _emit_drawer(model, r: ResolvedMicrowaveConfig, body, mats, *, assets) -> str:
    drawer = model.part("drawer")
    dw, dh, dt = r.door_w, r.door_h, DOOR_T
    # The slide origin is anchored on the cavity floor liner front edge (solid
    # body geometry), so all drawer child visuals are authored about a local Z
    # that maps the panel center back up to door_cz (panel_local_z) and the tray
    # down to the cavity floor.
    panel_local_z = r.door_cz - r.floor_top_z
    drawer.visual(
        mesh_from_cadquery(
            _drawer_front_solid(r),
            "drawer_front_panel",
            assets=assets,
            tolerance=_MESH_TOL,
            angular_tolerance=_MESH_ANG,
        ),
        origin=Origin(xyz=(0.0, 0.0, panel_local_z)),
        material=mats["door"],
        name="drawer_frame", material_class_id="plastic.opaque_glossy_molded",
    )
    drawer.visual(
        Box((dw * 0.78, 0.004, dh * 0.70)),
        origin=Origin(xyz=(0.0, -dt + 0.0105, panel_local_z)),
        material=mats["window"],
        name="window_glass", material_class_id="glass.smoked_tinted",
    )
    bar_x = dw / 2.0 - 0.028
    bar_y = -dt - 0.019
    drawer.visual(
        Box((0.018, 0.014, dh)),
        origin=Origin(xyz=(bar_x, bar_y, panel_local_z)),
        material=mats["handle"],
        name="handle_bar", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_steel" else "metal.paint_coated"),
    )
    for i, dz in enumerate([dh * 0.42, -dh * 0.42]):
        drawer.visual(
            Box((0.018, 0.013, 0.024)),
            origin=Origin(xyz=(bar_x, -dt - 0.006, panel_local_z + dz)),
            material=mats["handle"],
            name=f"handle_standoff_{i}", material_class_id=("metal.stainless_matte" if r.palette_style == "stainless_steel" else "metal.paint_coated"),
        )
    # Flat tray extending backward into the cavity (drawer L261-275). The tray
    # bottom rests just above the cavity floor (local z near 0). The tray width
    # tracks the cavity so the side lips always land on the wall-mounted guide
    # rails (the old TRAY_W cap left the lips short of the rails for wide
    # cavities, and the fixed rail height floated ~45 mm above the lips -- the
    # drawer then had NO body contact at full travel and read as disconnected).
    tray_w = r.cav_w - 0.02
    tray_local_z = (r.cav_z0 + 0.015) - r.floor_top_z
    drawer.visual(
        Box((tray_w, TRAY_DEPTH, TRAY_T)),
        origin=Origin(xyz=(0.0, TRAY_DEPTH / 2.0, tray_local_z)),
        material=mats["cavity"],
        name="drawer_tray", material_class_id="metal.paint_coated",
    )
    for i, x_sign in enumerate([-1.0, 1.0]):
        lip_x = x_sign * (tray_w / 2.0 - 0.003)
        drawer.visual(
            Box((0.006, TRAY_DEPTH, 0.014)),
            origin=Origin(xyz=(lip_x, TRAY_DEPTH / 2.0, tray_local_z + 0.004)),
            material=mats["rail"],
            name=f"tray_lip_{i}", material_class_id="metal.steel_galvanized",
        )
    model.articulation(
        "drawer_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=drawer,
        origin=Origin(xyz=(r.tt_x, r.front_y, r.floor_top_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=40.0, velocity=0.5, lower=0.0, upper=r.drawer_travel
        ),
    )
    return "drawer"


# ----------------------------------------------------------------------------
# Slot B: turntable (rotating / flatbed). rotating = CONTINUOUS part; flatbed =
# body (or drawer) inline visual. Parent is derived from the door choice.
# ----------------------------------------------------------------------------
def _emit_turntable(model, r: ResolvedMicrowaveConfig, body, mats, drawer_name: str | None):
    if r.turntable == "flatbed":
        _emit_flatbed(r, body, model, mats, drawer_name)
        return

    turntable = model.part("turntable")
    turntable.visual(
        Cylinder(radius=HUB_R, length=HUB_H),
        origin=Origin(xyz=(0.0, 0.0, HUB_H / 2.0)),
        material=mats["hub"],
        name="drive_hub", material_class_id="plastic.opaque_glossy_molded",
    )
    for k in range(3):
        ang = k * 2.0 * math.pi / 3.0
        r_c = 0.026
        turntable.visual(
            Box((0.04, 0.012, 0.008)),
            origin=Origin(
                xyz=(r_c * math.cos(ang), r_c * math.sin(ang), 0.008),
                rpy=(0.0, 0.0, ang),
            ),
            material=mats["hub"],
            name=f"coupler_rib_{k}", material_class_id="plastic.opaque_glossy_molded",
        )
    turntable.visual(
        Cylinder(radius=r.plate_r, length=PLATE_T),
        origin=Origin(xyz=(0.0, 0.0, HUB_H + PLATE_T / 2.0)),
        material=mats["glass"],
        name="glass_plate", material_class_id="glass.clear_transparent",
    )

    if r.turntable_on_drawer and drawer_name is not None:
        # Reparented onto the drawer; rides on the drawer tray (drawer L319-329).
        # The drawer frame origin sits on the cavity floor, so the tray local Z
        # mirrors _emit_drawer's tray placement.
        tray_local_z = (r.cav_z0 + 0.015) - r.floor_top_z
        tt_origin_z = tray_local_z + TRAY_T / 2.0
        model.articulation(
            "turntable_spin",
            ArticulationType.CONTINUOUS,
            parent=model.get_part(drawer_name),
            child=turntable,
            origin=Origin(xyz=(0.0, TRAY_DEPTH / 2.0, tt_origin_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=3.0),
        )
    else:
        model.articulation(
            "turntable_spin",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=turntable,
            origin=Origin(xyz=(r.tt_x, r.tt_y, r.floor_top_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=3.0),
        )


def _emit_flatbed(r: ResolvedMicrowaveConfig, body, model, mats, drawer_name: str | None):
    """Fixed glass floor as an inline visual (flatbed L183-188).

    When the door is a drawer, the glass floor reparents onto the drawer tray
    so it travels with the drawer (spec §9 (1)); else it sits on the body
    cavity floor liner.
    """
    fb_w = min(FB_W, r.cav_w - 0.02)
    fb_d = min(FB_D, (r.cav_back_y - r.front_y) - 0.04)
    if r.turntable_on_drawer and drawer_name is not None:
        drawer = model.get_part(drawer_name)
        tray_local_z = (r.cav_z0 + 0.015) - r.floor_top_z
        drawer.visual(
            Box((fb_w, fb_d, FB_T)),
            origin=Origin(xyz=(0.0, TRAY_DEPTH / 2.0, tray_local_z + TRAY_T / 2.0 + FB_T / 2.0)),
            material=mats["glass"],
            name="flatbed_glass", material_class_id="glass.frosted_smooth",
        )
    else:
        body.visual(
            Box((fb_w, fb_d, FB_T)),
            origin=Origin(xyz=(r.tt_x, r.tt_y, r.floor_top_z + FB_T / 2.0)),
            material=mats["glass"],
            name="flatbed_glass", material_class_id="glass.frosted_smooth",
        )


# ----------------------------------------------------------------------------
# Slot D: interior_rack (shelf). FIXED wire-grid rack on the support ledges.
# ----------------------------------------------------------------------------
def _emit_rack(model, r: ResolvedMicrowaveConfig, body, mats):
    if r.interior_rack != "shelf":
        return
    rack = model.part("shelf_rack")
    frame_w = r.rack_frame_w
    z_c = FRAME_RAIL / 2.0
    # The FIXED origin is anchored on the LEFT support ledge top (solid body
    # geometry) instead of the cavity-center void, so the joint origin lies on
    # parent geometry (Rule 2). The rack visuals are authored about a local X
    # offset (xo) so the rack still re-centers on the cavity center tt_x in the
    # world; the left side rail then sits right at the local origin (ledge).
    cav_left_inner = r.tt_x - r.cav_w / 2.0 + LINER_T
    ledge_x = cav_left_inner - 0.001 + SUPPORT_W / 2.0
    xo = r.tt_x - ledge_x
    rack.visual(
        Box((frame_w, FRAME_RAIL, FRAME_RAIL)),
        origin=Origin(xyz=(xo, -RACK_FRAME_D / 2.0 + FRAME_RAIL / 2.0, z_c)),
        material=mats["wire"],
        name="frame_front", material_class_id="metal.chrome_polished",
    )
    rack.visual(
        Box((frame_w, FRAME_RAIL, FRAME_RAIL)),
        origin=Origin(xyz=(xo, RACK_FRAME_D / 2.0 - FRAME_RAIL / 2.0, z_c)),
        material=mats["wire"],
        name="frame_back", material_class_id="metal.chrome_polished",
    )
    inner_d = RACK_FRAME_D - 2.0 * FRAME_RAIL
    inner_w = frame_w - 2.0 * FRAME_RAIL
    rack.visual(
        Box((FRAME_RAIL, inner_d, FRAME_RAIL)),
        origin=Origin(xyz=(xo - frame_w / 2.0 + FRAME_RAIL / 2.0, 0.0, z_c)),
        material=mats["wire"],
        name="frame_left", material_class_id="metal.chrome_polished",
    )
    rack.visual(
        Box((FRAME_RAIL, inner_d, FRAME_RAIL)),
        origin=Origin(xyz=(xo + frame_w / 2.0 - FRAME_RAIL / 2.0, 0.0, z_c)),
        material=mats["wire"],
        name="frame_right", material_class_id="metal.chrome_polished",
    )
    n_cross = r.cross_wire_count
    for i in range(n_cross):
        y_local = -inner_d / 2.0 + (i + 1) * inner_d / (n_cross + 1)
        rack.visual(
            _rack_wire(inner_w, along="x"),
            origin=Origin(xyz=(xo, y_local, z_c)),
            material=mats["wire"],
            name=f"cross_wire_{i}", material_class_id="metal.chrome_polished",
        )
    n_long = r.long_wire_count
    for i in range(n_long):
        x_local = -inner_w / 2.0 + (i + 1) * inner_w / (n_long + 1)
        rack.visual(
            _rack_wire(inner_d, along="y"),
            origin=Origin(xyz=(xo + x_local, 0.0, z_c)),
            material=mats["wire"],
            name=f"long_wire_{i}", material_class_id="metal.chrome_polished",
        )
    model.articulation(
        "body_to_rack",
        ArticulationType.FIXED,
        parent=body,
        child=rack,
        origin=Origin(xyz=(ledge_x, r.rack_yc, r.rack_bottom_z - 0.0005)),
    )


# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------
def build_microwave(
    config: MicrowaveConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    """Build the microwave; when an asset context is given but no asset session
    is active (standalone build/test), activate one rooted at the same asset
    root so geometry meshes (knobs) land next to the cadquery meshes instead of
    an ephemeral /tmp session."""
    from sdk._core.v0.assets import (
        AssetSession,
        activate_asset_session,
        current_asset_session,
    )

    if assets is not None and current_asset_session() is None:
        session = AssetSession(assets.asset_root, mesh_subdir=assets.mesh_subdir)
        with activate_asset_session(session):
            return _build_microwave(config, assets=assets)
    return _build_microwave(config, assets=assets)


def _build_microwave(
    config: MicrowaveConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"microwave_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_body(model, r, mats, assets=assets)
    _emit_control(model, r, body, mats, assets=assets)
    door_name = _emit_door(model, r, body, mats, assets=assets)
    drawer_name = door_name if door_name == "drawer" else None
    _emit_turntable(model, r, body, mats, drawer_name)
    _emit_rack(model, r, body, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_microwave(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_microwave(config_from_seed(seed), assets=assets)


# ----------------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------------
def run_microwave_tests(
    object_model: ArticulatedObject,
    config: MicrowaveConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")

    # ---- Captured-overlap allowances (element-scoped). ----
    if r.is_drawer:
        drawer = object_model.get_part("drawer")
        ctx.allow_overlap(
            body, drawer,
            elem_a="outer_shell", elem_b="drawer_tray",
            reason="The drawer tray slides inside the cooking cavity; the shell "
            "mesh encloses the cavity void as a solid-proxy outer member.",
        )
        for i in range(2):
            ctx.allow_overlap(
                body, drawer,
                elem_a="outer_shell", elem_b=f"tray_lip_{i}",
                reason="Tray side lip is a slide-rail contact strip nested inside "
                "the cavity shell.",
            )
        # The tray (and its side lips) nest inside the lined cavity, so they may
        # graze the cavity liner panels (back / side / floor) when closed; these
        # are captured nested-slider contacts (mirror the outer_shell allowance).
        for liner in ("cavity_back_wall", "cavity_left_wall", "cavity_right_wall",
                      "cavity_floor"):
            for tray_elem in ("drawer_tray", "tray_lip_0", "tray_lip_1"):
                ctx.allow_overlap(
                    body, drawer,
                    elem_a=liner, elem_b=tray_elem,
                    reason="The drawer tray / lip nests inside the lined cooking "
                    "cavity (captured nested-slider contact with the liner).",
                )
        if r.turntable == "rotating":
            ctx.allow_overlap(
                drawer, object_model.get_part("turntable"),
                reason="The turntable hub seats on the drawer tray (captured seat).",
            )

    # ---- Baseline structural checks. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Overall size and grounding. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("body part present", "body" in part_names, details=str(sorted(part_names)))
    body_aabb = ctx.part_world_aabb(body)
    if body_aabb is not None:
        ctx.check(
            "feet ground the unit at z=0",
            abs(body_aabb[0][2]) < 1e-3,
            details=f"zmin={body_aabb[0][2]}",
        )
        ctx.check(
            "body footprint roughly matches the scaled width/depth",
            abs((body_aabb[1][0] - body_aabb[0][0]) - r.body_w) < 0.03
            and abs((body_aabb[1][1] - body_aabb[0][1]) - r.body_d) < 0.03,
            details=f"body aabb={body_aabb}",
        )

    # ---- Door / drawer joint topology + closed pose + actuation. ----
    if r.door_mechanism == "side_hinge":
        hinge = object_model.get_articulation("door_hinge")
        door = object_model.get_part("door")
        ctx.check(
            "side_hinge door is REVOLUTE about a vertical (-Z) axis",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(abs(hinge.axis[2]) - 1.0) < 1e-6,
            details=f"type={hinge.articulation_type} axis={tuple(hinge.axis)}",
        )
        ctx.expect_gap(
            body, door, axis="y", max_gap=0.006, max_penetration=0.002,
            name="closed side-hinge door seats against the body front",
        )
        closed = ctx.part_world_aabb(door)
        with ctx.pose({hinge: r.door_open_angle}):
            opened = ctx.part_world_aabb(door)
        if closed is not None and opened is not None:
            ctx.check(
                "side-hinge door swings outward in front of the oven",
                opened[0][1] < closed[0][1] - 0.10,
                details=f"closed_ymin={closed[0][1]:.3f} open_ymin={opened[0][1]:.3f}",
            )
    elif r.door_mechanism == "drop_down":
        hinge = object_model.get_articulation("door_hinge")
        door = object_model.get_part("door")
        ctx.check(
            "drop_down door is REVOLUTE about a horizontal (+X) axis",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[0] - 1.0) < 1e-6
            and abs(hinge.axis[1]) < 1e-6 and abs(hinge.axis[2]) < 1e-6,
            details=f"type={hinge.articulation_type} axis={tuple(hinge.axis)}",
        )
        ctx.expect_gap(
            body, door, axis="y", max_gap=0.006, max_penetration=0.002,
            name="closed drop-down door seats against the body front",
        )
        closed = ctx.part_world_aabb(door)
        with ctx.pose({hinge: r.door_open_angle}):
            opened = ctx.part_world_aabb(door)
        if closed is not None and opened is not None:
            ctx.check(
                "drop-down door top drops well below the closed height",
                opened[1][2] < closed[1][2] - 0.10,
                details=f"closed_top={closed[1][2]:.3f} open_top={opened[1][2]:.3f}",
            )
    elif r.door_mechanism == "top_hinge":
        hinge = object_model.get_articulation("door_hinge")
        door = object_model.get_part("door")
        ctx.check(
            "top_hinge door is REVOLUTE about a horizontal (-X) axis",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(abs(hinge.axis[0]) - 1.0) < 1e-6
            and abs(hinge.axis[1]) < 1e-6 and abs(hinge.axis[2]) < 1e-6,
            details=f"type={hinge.articulation_type} axis={tuple(hinge.axis)}",
        )
        ctx.expect_gap(
            body, door, axis="y", max_gap=0.006, max_penetration=0.002,
            name="closed top-hinge door seats against the body front",
        )
        closed = ctx.part_world_aabb(door)
        with ctx.pose({hinge: r.door_open_angle}):
            opened = ctx.part_world_aabb(door)
        if closed is not None and opened is not None:
            ctx.check(
                "top-hinge door swings upward above the body top",
                opened[1][2] > closed[1][2] + 0.03,
                details=f"closed_top={closed[1][2]:.3f} open_top={opened[1][2]:.3f}",
            )
    else:  # drawer_prismatic
        slide = object_model.get_articulation("drawer_slide")
        drawer = object_model.get_part("drawer")
        ctx.check(
            "drawer is PRISMATIC along -Y",
            slide.articulation_type == ArticulationType.PRISMATIC
            and abs(slide.axis[1] - (-1.0)) < 1e-6
            and abs(slide.axis[0]) < 1e-6 and abs(slide.axis[2]) < 1e-6,
            details=f"type={slide.articulation_type} axis={tuple(slide.axis)}",
        )
        frame_aabb = ctx.part_element_world_aabb(drawer, elem="drawer_frame")
        if frame_aabb is not None:
            ctx.check(
                "closed drawer front panel seats at the body front face",
                abs(frame_aabb[1][1] - r.front_y) < 0.006,
                details=f"frame max_y={frame_aabb[1][1]:.4f} FRONT_Y={r.front_y:.4f}",
            )
        ctx.expect_within(
            drawer, body, axes="x", elem_a="drawer_tray", margin=0.005,
            name="tray stays within cavity width when closed",
        )
        ctx.expect_overlap(
            body, drawer, axes="y", elem_a="outer_shell", elem_b="drawer_tray",
            min_overlap=0.10, name="tray remains inserted in cavity when closed",
        )
        rest_pos = ctx.part_world_position(drawer)
        with ctx.pose({slide: r.drawer_travel}):
            ext_pos = ctx.part_world_position(drawer)
        if rest_pos is not None and ext_pos is not None:
            ctx.check(
                "drawer pulls outward along -Y when extended",
                ext_pos[1] < rest_pos[1] - 0.10,
                details=f"rest_y={rest_pos[1]:.3f} ext_y={ext_pos[1]:.3f}",
            )
        # Guide rails on the body cavity walls.
        ctx.check(
            "guide rails exist on both cavity walls",
            ctx.part_element_world_aabb(body, elem="guide_rail_0") is not None
            and ctx.part_element_world_aabb(body, elem="guide_rail_1") is not None,
            details="guide_rail_0/1",
        )

    # ---- Cavity opening regression: the shell front must be OPEN over the
    # cavity rectangle (PV_A seed_0000 shipped a sealed front panel when the
    # depth scale pushed the front face past the fixed cavity-cut reach). ----
    shell_path = None
    for item in getattr(body, "visuals", []) or []:
        geom = getattr(item, "geometry", None)
        if getattr(item, "name", None) == "outer_shell" and hasattr(geom, "filename"):
            from sdk._core.v0.assets import resolve_mesh_path

            shell_path = resolve_mesh_path(geom.filename, assets=ctx._asset_root())
            break
    if shell_path is not None and shell_path.exists():
        verts, faces = [], []
        for line in shell_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("v "):
                p = line.split()
                verts.append((float(p[1]), float(p[2]), float(p[3])))
            elif line.startswith("f "):
                idx = []
                for tok in line.split()[1:]:
                    i = int(tok.split("/")[0])
                    idx.append(i - 1 if i > 0 else len(verts) + i)
                faces.append(idx)
        ox0, ox1 = r.tt_x - r.cav_w / 2.0 + 0.03, r.tt_x + r.cav_w / 2.0 - 0.03
        oz0, oz1 = r.cav_z0 + 0.03, r.cav_z1 - 0.03
        blocking = 0
        for f in faces:
            pts = [verts[i] for i in f if 0 <= i < len(verts)]
            if len(pts) < 3 or not all(abs(p[1] - r.front_y) < 0.002 for p in pts):
                continue
            fxs = [p[0] for p in pts]
            fzs = [p[2] for p in pts]
            if max(fxs) > ox0 and min(fxs) < ox1 and max(fzs) > oz0 and min(fzs) < oz1:
                blocking += 1
        ctx.check(
            "cavity opening reaches the shell front face",
            blocking == 0,
            details=f"{blocking} front-plane faces block the cavity opening",
        )

    # ---- Turntable topology. ----
    if r.turntable == "rotating":
        spin = object_model.get_articulation("turntable_spin")
        turntable = object_model.get_part("turntable")
        ctx.check(
            "turntable_spin is CONTINUOUS about +Z with no lower limit",
            spin.articulation_type == ArticulationType.CONTINUOUS
            and abs(spin.axis[2] - 1.0) < 1e-6
            and (spin.motion_limits is None or spin.motion_limits.lower is None),
            details=f"type={spin.articulation_type} axis={tuple(spin.axis)}",
        )
        if r.turntable_on_drawer:
            ctx.check(
                "turntable is reparented onto the drawer",
                spin.parent == "drawer",
                details=f"parent={spin.parent}",
            )
            slide = object_model.get_articulation("drawer_slide")
            tt_closed = ctx.part_world_aabb(turntable)
            with ctx.pose({slide: r.drawer_travel}):
                tt_open = ctx.part_world_aabb(turntable)
            if tt_closed is not None and tt_open is not None:
                ctx.check(
                    "turntable travels with the drawer when extended",
                    tt_open[0][1] < tt_closed[0][1] - 0.10,
                    details=f"closed_ymin={tt_closed[0][1]:.3f} open_ymin={tt_open[0][1]:.3f}",
                )
        else:
            ctx.check(
                "turntable is parented to the body",
                spin.parent == "body",
                details=f"parent={spin.parent}",
            )
            ctx.expect_gap(
                turntable, body, axis="z", min_gap=0.0, max_gap=0.003,
                positive_elem="drive_hub", negative_elem="cavity_floor",
                name="drive hub rests on the cavity floor",
            )
        # Off-axis coupler rib proves rotation actually moves geometry.
        rib_rest = ctx.part_element_world_aabb(turntable, elem="coupler_rib_0")
        with ctx.pose({spin: math.pi / 2.0}):
            rib_spun = ctx.part_element_world_aabb(turntable, elem="coupler_rib_0")
        if rib_rest is not None and rib_spun is not None:
            ctx.check(
                "spinning the turntable moves the off-axis coupler rib",
                abs(
                    (rib_spun[1][1] + rib_spun[0][1]) / 2.0
                    - (rib_rest[1][1] + rib_rest[0][1]) / 2.0
                )
                > 0.015,
                details=f"rest={rib_rest}, spun={rib_spun}",
            )
    else:  # flatbed
        ctx.check(
            "flatbed has no rotating turntable part",
            "turntable" not in part_names,
            details=str(sorted(part_names)),
        )
        ctx.check(
            "flatbed has no turntable_spin joint",
            "turntable_spin" not in {a.name for a in object_model.articulations},
            details=str(sorted(a.name for a in object_model.articulations)),
        )
        carrier = object_model.get_part("drawer") if r.turntable_on_drawer else body
        fb_aabb = ctx.part_element_world_aabb(carrier, elem="flatbed_glass")
        ctx.check(
            "flatbed glass floor is a thin panel present in the cavity",
            fb_aabb is not None and (fb_aabb[1][2] - fb_aabb[0][2]) < 0.012,
            details=f"flatbed aabb={fb_aabb}",
        )

    # ---- Control topology. ----
    joint_names = {a.name for a in object_model.articulations}
    if r.control == "rotary_dials":
        for knob_name in ("power_knob", "timer_knob"):
            ctx.check(
                f"{knob_name} part present",
                knob_name in part_names,
                details=str(sorted(part_names)),
            )
            knob_joint = object_model.get_articulation(f"{knob_name}_dial")
            ctx.check(
                f"{knob_name}_dial is REVOLUTE about -Y with 0..270 deg range",
                knob_joint.articulation_type == ArticulationType.REVOLUTE
                and abs(knob_joint.axis[1] - (-1.0)) < 1e-6
                and knob_joint.motion_limits is not None
                and abs(knob_joint.motion_limits.upper - KNOB_UPPER_RAD) < 1e-6,
                details=f"axis={tuple(knob_joint.axis)} limits={knob_joint.motion_limits}",
            )
            # Rotation moves the off-center pointer (rotation proof).
            knob = object_model.get_part(knob_name)
            ptr_rest = ctx.part_element_world_aabb(knob, elem=f"{knob_name}_pointer")
            with ctx.pose({knob_joint: math.pi}):
                ptr_half = ctx.part_element_world_aabb(knob, elem=f"{knob_name}_pointer")
            if ptr_rest is not None and ptr_half is not None:
                ctx.check(
                    f"{knob_name} rotation moves the off-center pointer",
                    abs(
                        (ptr_half[1][0] + ptr_half[0][0]) / 2.0
                        - (ptr_rest[1][0] + ptr_rest[0][0]) / 2.0
                    )
                    > 0.010,
                    details=f"rest={ptr_rest}, half={ptr_half}",
                )
        ctx.expect_gap(
            object_model.get_part("power_knob"),
            object_model.get_part("timer_knob"),
            axis="z", min_gap=0.005,
            name="the two knobs are vertically separated",
        )
    else:
        ctx.check(
            f"{r.control} control adds no rotary-dial joint (Rule 1)",
            "power_knob_dial" not in joint_names and "timer_knob_dial" not in joint_names,
            details=str(sorted(joint_names)),
        )
        ctx.check(
            f"{r.control} control adds no knob part (Rule 1)",
            "power_knob" not in part_names and "timer_knob" not in part_names,
            details=str(sorted(part_names)),
        )

    # ---- Interior rack topology. ----
    if r.interior_rack == "shelf":
        ctx.check("shelf_rack part present", "shelf_rack" in part_names, details="")
        rack_joint = object_model.get_articulation("body_to_rack")
        ctx.check(
            "shelf rack is FIXED to the body",
            rack_joint.articulation_type == ArticulationType.FIXED,
            details=f"type={rack_joint.articulation_type}",
        )
        rack = object_model.get_part("shelf_rack")
        if r.turntable == "rotating":
            ctx.expect_gap(
                rack, object_model.get_part("turntable"), axis="z", min_gap=0.02,
                name="shelf rack clears the turntable below",
            )
    else:
        ctx.check(
            "no rack: body_to_rack joint absent",
            "body_to_rack" not in joint_names,
            details=str(sorted(joint_names)),
        )

    # ---- At least one non-fixed joint (defining motion). ----
    non_fixed = [
        a for a in object_model.articulations
        if a.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed (defining-motion) joint",
        len(non_fixed) >= 1,
        details=f"non_fixed={[a.name for a in non_fixed]}",
    )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded matching resolve",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "MicrowaveConfig",
    "ResolvedMicrowaveConfig",
    "build_microwave",
    "build_seeded_microwave",
    "config_from_seed",
    "resolve_config",
    "run_microwave_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
