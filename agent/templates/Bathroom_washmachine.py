# SPDX-License-Identifier: Apache-2.0

"""Front-loading (drum) washing machine — modular procedural template.

pattern = parallel_children. The white-enamel cabinet ``body`` is the root and
carries several parallel child mechanisms that each mate to an independent face
or recess of the same chassis:

  fixed children (always present):
    drum  — CONTINUOUS spin about +X, recessed inside the cylindrical tub cavity.
    door  — REVOLUTE vertical (+Z) side hinge on the LEFT (+Y), swings ~100 deg.

  slot children (one module each per seed):
    Slot A door  : round_porthole_door / rounded_square_window / convex_porthole
                   (sets the door mesh family + front recess shape + HINGE_Y)
    Slot B control: single_dial_display / touch_panel_buttons / twin_dial_controls
                   (0, 1, or 2 CONTINUOUS dial joints)
    Slot C disp.  : pull_out_drawer (PRISMATIC) / flip_lid_tray (REVOLUTE lid)
    Slot D base   : flat_service_panel (no joint) / raised_plinth_flip_panel
                   (REVOLUTE bottom-edge flip-down panel + plinth + lowered feet)

  Slot A × B × C × D = 3 × 3 × 2 × 2 = 36 distinct topology combinations.

Coordinate convention (object-intrinsic frame), verbatim from all 7 5-star
sources:
  +X = out of the FRONT face, -X toward the back wall.
  +Z = up.  +Y = machine WIDTH; "left" of the front face = +Y.
Body ~0.60 W (Y) × 0.60 D (X) × 0.85 H (Z); back face x=0, front face x=FRONT_X.

5-star sources adapted (per AUTHORING.md §A Rule 3 — real cadquery /
BezelGeometry / KnobGeometry geometry kept, never downgraded to placeholders):
  parent  rec_white-front-loading…_3205b533 : body+drum+door core, round
          porthole door, single dial, pull-out drawer, flush service hatch
  rec_washmachine_var_square_window_door     : rounded-square gasket window
  rec_washmachine_var_convex_porthole_door   : chrome ring + convex dome + latch
  rec_washmachine_var_touch_panel_controls   : wide touch display + 5 buttons
  rec_washmachine_var_twin_dial_controls     : two smaller continuous dials
  rec_washmachine_var_flip_lid_dispenser     : fixed tray + revolute flip lid
  rec_washmachine_var_raised_plinth_panel    : plinth + revolute flip-down panel

__modular__ = True
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal, Optional

import cadquery as cq
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    BezelGeometry,
    Box,
    Inertial,
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


# ====================================================================== #
# Slot enums                                                             #
# ====================================================================== #

DoorModule = Literal["round_porthole_door", "rounded_square_window", "convex_porthole"]
ControlModule = Literal["single_dial_display", "touch_panel_buttons", "twin_dial_controls"]
DispenserModule = Literal["pull_out_drawer", "flip_lid_tray"]
BaseModule = Literal["flat_service_panel", "raised_plinth_flip_panel"]
PaletteStyle = Literal[
    "classic_white",
    "graphite_dark",
    "inox_silver",
    "matte_black",
    "champagne_gold",
    "retro_cream",
]

DOOR_MODULES: tuple[DoorModule, ...] = (
    "round_porthole_door",
    "rounded_square_window",
    "convex_porthole",
)
CONTROL_MODULES: tuple[ControlModule, ...] = (
    "single_dial_display",
    "touch_panel_buttons",
    "twin_dial_controls",
)
DISPENSER_MODULES: tuple[DispenserModule, ...] = ("pull_out_drawer", "flip_lid_tray")
BASE_MODULES: tuple[BaseModule, ...] = ("flat_service_panel", "raised_plinth_flip_panel")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_white",
    "graphite_dark",
    "inox_silver",
    "matte_black",
    "champagne_gold",
    "retro_cream",
)


# ====================================================================== #
# Palette colorways  (each picks body / frame / glass / drum / control)  #
# ====================================================================== #

# Material token set used by every module; resolved from a palette style.
PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "classic_white": {
        "body": (0.94, 0.94, 0.95, 1.0),
        "frame": (0.07, 0.07, 0.08, 1.0),       # bezel / gasket black
        "accent": (0.85, 0.86, 0.88, 1.0),      # chrome ring
        "glass": (0.18, 0.20, 0.24, 0.45),
        "drum": (0.72, 0.73, 0.76, 1.0),
        "control": (0.78, 0.79, 0.81, 1.0),     # dial metal
        "display": (0.05, 0.07, 0.10, 1.0),
        "panel": (0.86, 0.86, 0.88, 1.0),
        "plinth": (0.32, 0.33, 0.35, 1.0),
        "button": (0.12, 0.12, 0.14, 1.0),
    },
    "graphite_dark": {
        "body": (0.22, 0.23, 0.25, 1.0),
        "frame": (0.80, 0.82, 0.85, 1.0),       # chrome/silver frame
        "accent": (0.86, 0.88, 0.90, 1.0),
        "glass": (0.10, 0.11, 0.14, 0.50),
        "drum": (0.72, 0.73, 0.76, 1.0),
        "control": (0.70, 0.71, 0.74, 1.0),
        "display": (0.04, 0.05, 0.07, 1.0),
        "panel": (0.30, 0.31, 0.33, 1.0),
        "plinth": (0.14, 0.15, 0.16, 1.0),
        "button": (0.55, 0.56, 0.58, 1.0),
    },
    "inox_silver": {
        "body": (0.66, 0.68, 0.71, 1.0),        # brushed steel
        "frame": (0.07, 0.07, 0.08, 1.0),
        "accent": (0.82, 0.84, 0.87, 1.0),
        "glass": (0.18, 0.20, 0.24, 0.45),
        "drum": (0.74, 0.75, 0.78, 1.0),
        "control": (0.82, 0.83, 0.85, 1.0),     # polished dial
        "display": (0.05, 0.06, 0.08, 1.0),
        "panel": (0.58, 0.60, 0.63, 1.0),
        "plinth": (0.40, 0.42, 0.45, 1.0),
        "button": (0.15, 0.15, 0.17, 1.0),
    },
    "matte_black": {
        "body": (0.08, 0.08, 0.09, 1.0),
        "frame": (0.20, 0.20, 0.22, 1.0),       # dark-gray frame
        "accent": (0.80, 0.81, 0.83, 1.0),      # chrome accent
        "glass": (0.06, 0.07, 0.09, 0.55),
        "drum": (0.70, 0.71, 0.74, 1.0),
        "control": (0.74, 0.75, 0.77, 1.0),
        "display": (0.03, 0.04, 0.05, 1.0),
        "panel": (0.16, 0.16, 0.18, 1.0),
        "plinth": (0.05, 0.05, 0.06, 1.0),
        "button": (0.40, 0.40, 0.42, 1.0),
    },
    "champagne_gold": {
        "body": (0.86, 0.80, 0.66, 1.0),        # warm beige
        "frame": (0.55, 0.45, 0.30, 1.0),       # bronze frame
        "accent": (0.78, 0.66, 0.40, 1.0),
        "glass": (0.18, 0.20, 0.24, 0.45),
        "drum": (0.74, 0.74, 0.76, 1.0),
        "control": (0.80, 0.68, 0.40, 1.0),     # gold dial
        "display": (0.07, 0.07, 0.09, 1.0),
        "panel": (0.78, 0.72, 0.58, 1.0),
        "plinth": (0.46, 0.40, 0.28, 1.0),
        "button": (0.30, 0.26, 0.16, 1.0),
    },
    "retro_cream": {
        "body": (0.92, 0.88, 0.78, 1.0),        # cream
        "frame": (0.85, 0.86, 0.88, 1.0),       # chrome ring frame
        "accent": (0.88, 0.89, 0.91, 1.0),
        "glass": (0.16, 0.22, 0.30, 0.45),      # blue-tinted glass
        "drum": (0.74, 0.75, 0.78, 1.0),
        "control": (0.86, 0.84, 0.74, 1.0),     # cream/chrome controls
        "display": (0.06, 0.09, 0.12, 1.0),
        "panel": (0.86, 0.83, 0.74, 1.0),
        "plinth": (0.50, 0.48, 0.42, 1.0),
        "button": (0.20, 0.22, 0.26, 1.0),
    },
}


# ====================================================================== #
# Config                                                                 #
# ====================================================================== #


@dataclass(frozen=True)
class WashingMachineConfig:
    """Public, unclamped config (the sampler's raw draw)."""

    door_module: DoorModule = "round_porthole_door"
    control_module: ControlModule = "single_dial_display"
    dispenser_module: DispenserModule = "pull_out_drawer"
    base_module: BaseModule = "flat_service_panel"
    palette_style: PaletteStyle = "classic_white"

    body_width_scale: float = 1.0
    body_height_scale: float = 1.0
    body_depth_scale: float = 1.0

    door_open_angle_deg: float = 100.0
    drawer_travel: float = 0.150
    dispenser_open_angle_deg: float = 75.0
    panel_open_angle_deg: float = 75.0
    plinth_h: float = 0.12


@dataclass(frozen=True)
class ResolvedWashingMachineConfig:
    """Clamped, equation-resolved config consumed by the builder."""

    door_module: DoorModule
    control_module: ControlModule
    dispenser_module: DispenserModule
    base_module: BaseModule
    palette_style: PaletteStyle

    # body
    body_w: float
    body_d: float
    body_h: float
    front_x: float

    # door / tub (equation chain)
    door_cz: float
    door_cy: float
    opening_r: float
    tub_r: float
    tub_back_x: float
    drum_r: float
    drum_front_x: float
    drum_back_x: float

    # control panel band
    panel_z0: float
    panel_z1: float

    # detergent dispenser pocket (top-left front)
    disp_cy: float
    disp_w: float
    disp_h: float
    disp_cz: float
    drawer_depth: float
    drawer_travel: float

    # service hatch (bottom-right front)
    hatch_cy: float
    hatch_cz: float

    # joint ranges
    door_open_angle: float
    dispenser_open_angle: float
    panel_open_angle: float
    plinth_h: float


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# ---- Nominal master dimensions (parent L42-L75), pre-scale ---- #
_NOM_BODY_W = 0.60
_NOM_BODY_D = 0.60
_NOM_BODY_H = 0.85
_NOM_DOOR_CZ = 0.40
_NOM_DOOR_CY = -0.02
_NOM_OPENING_R = 0.165
_NOM_PANEL_Z0 = 0.715
_NOM_DISP_CY = 0.205
_NOM_DISP_W = 0.150
_NOM_DISP_H = 0.055
_NOM_DISP_CZ = 0.660
_NOM_DRAWER_DEPTH = 0.235
_NOM_HATCH_CY = -0.18
_NOM_HATCH_CZ = 0.115


def config_from_seed(seed: int) -> WashingMachineConfig:
    """Deterministic per-seed procedural sampling (seed 0 is not special).

    Weighted draw over the 4 slot enums with a mild bias toward the parent
    residential baseline (round porthole + single dial + drawer + flush hatch),
    so the common machine appears often while every combo remains reachable.
    """
    rng = random.Random(seed * 2654435761 + 12345)

    door_module = rng.choices(
        DOOR_MODULES, weights=(0.45, 0.30, 0.25), k=1
    )[0]
    control_module = rng.choices(
        CONTROL_MODULES, weights=(0.45, 0.27, 0.28), k=1
    )[0]
    dispenser_module = rng.choices(
        DISPENSER_MODULES, weights=(0.58, 0.42), k=1
    )[0]
    base_module = rng.choices(
        BASE_MODULES, weights=(0.55, 0.45), k=1
    )[0]
    palette_style = rng.choice(PALETTE_STYLES)

    body_width_scale = rng.uniform(0.92, 1.10)
    body_height_scale = rng.uniform(0.94, 1.08)
    body_depth_scale = rng.uniform(0.94, 1.06)

    door_open_angle_deg = rng.uniform(90.0, 105.0)
    drawer_travel = rng.uniform(0.12, 0.17)
    dispenser_open_angle_deg = rng.uniform(65.0, 80.0)
    panel_open_angle_deg = rng.uniform(65.0, 80.0)
    plinth_h = rng.uniform(0.10, 0.14)

    return WashingMachineConfig(
        door_module=door_module,
        control_module=control_module,
        dispenser_module=dispenser_module,
        base_module=base_module,
        palette_style=palette_style,
        body_width_scale=body_width_scale,
        body_height_scale=body_height_scale,
        body_depth_scale=body_depth_scale,
        door_open_angle_deg=door_open_angle_deg,
        drawer_travel=drawer_travel,
        dispenser_open_angle_deg=dispenser_open_angle_deg,
        panel_open_angle_deg=panel_open_angle_deg,
        plinth_h=plinth_h,
    )


def resolve_config(config: WashingMachineConfig) -> ResolvedWashingMachineConfig:
    """Clamp scales, run the opening_r→tub_r→drum_r equation chain, project the
    tub/opening inequalities, and resolve conditional dims by chosen module."""
    ws = _clamp(config.body_width_scale, 0.92, 1.10)
    hs = _clamp(config.body_height_scale, 0.94, 1.08)
    ds = _clamp(config.body_depth_scale, 0.94, 1.06)

    body_w = _NOM_BODY_W * ws
    body_d = _NOM_BODY_D * ds
    body_h = _NOM_BODY_H * hs
    front_x = body_d

    door_cz = _NOM_DOOR_CZ * hs
    door_cy = _NOM_DOOR_CY * ws

    # ---- opening_r → tub_r → drum_r equation chain ---- #
    opening_r = _clamp(_NOM_OPENING_R * ws, 0.14, 0.185)
    # The door recess (opening_r + 0.040) must fit in the front-face half-height
    # and half-width; shrink opening_r if it does not.
    max_recess = min(body_h / 2.0 - 0.02, body_w / 2.0 - 0.02)
    if opening_r + 0.040 > max_recess:
        opening_r = max(0.12, max_recess - 0.040)
    tub_r = opening_r + 0.040
    drum_r = tub_r - 0.030
    tub_back_x = 0.205 * ds
    drum_front_x = front_x - 0.045
    drum_back_x = tub_back_x + 0.02

    panel_z0 = _NOM_PANEL_Z0 * hs
    panel_z1 = body_h

    disp_cy = _NOM_DISP_CY * ws
    disp_w = _NOM_DISP_W
    disp_h = _NOM_DISP_H
    disp_cz = _NOM_DISP_CZ * hs
    drawer_depth = _NOM_DRAWER_DEPTH * ds
    # drawer travel ≤ drawer_depth - 0.05 so it never slides fully out.
    drawer_travel = _clamp(config.drawer_travel, 0.12, 0.17)
    drawer_travel = min(drawer_travel, drawer_depth - 0.05)

    hatch_cy = _NOM_HATCH_CY * ws
    hatch_cz = _NOM_HATCH_CZ * hs

    return ResolvedWashingMachineConfig(
        door_module=config.door_module,
        control_module=config.control_module,
        dispenser_module=config.dispenser_module,
        base_module=config.base_module,
        palette_style=config.palette_style,
        body_w=body_w,
        body_d=body_d,
        body_h=body_h,
        front_x=front_x,
        door_cz=door_cz,
        door_cy=door_cy,
        opening_r=opening_r,
        tub_r=tub_r,
        tub_back_x=tub_back_x,
        drum_r=drum_r,
        drum_front_x=drum_front_x,
        drum_back_x=drum_back_x,
        panel_z0=panel_z0,
        panel_z1=panel_z1,
        disp_cy=disp_cy,
        disp_w=disp_w,
        disp_h=disp_h,
        disp_cz=disp_cz,
        drawer_depth=drawer_depth,
        drawer_travel=drawer_travel,
        hatch_cy=hatch_cy,
        hatch_cz=hatch_cz,
        door_open_angle=math.radians(_clamp(config.door_open_angle_deg, 90.0, 105.0)),
        dispenser_open_angle=math.radians(_clamp(config.dispenser_open_angle_deg, 65.0, 80.0)),
        panel_open_angle=math.radians(_clamp(config.panel_open_angle_deg, 65.0, 80.0)),
        plinth_h=_clamp(config.plinth_h, 0.10, 0.14),
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Per-seed module picks consumed by the module_topology_diversity gate."""
    c = config_from_seed(seed)
    return [
        ("door", c.door_module),
        ("control", c.control_module),
        ("dispenser", c.dispenser_module),
        ("base", c.base_module),
    ]


# ====================================================================== #
# Geometry helpers — depend on the resolved config `r`                   #
# ====================================================================== #

# Frame half-width (left-edge Y offset of the door, sets HINGE_Y) per Slot A.
# Matches the 5★ square-window source ratio GASKET_SIZE/WINDOW_SIZE = 0.370/0.270.
_GASKET_SIZE_FACTOR = 1.37   # gasket outer side ≈ window_size * factor


def _door_frame_half_y(r: ResolvedWashingMachineConfig) -> float:
    """Left-edge Y offset of the chosen door module (in body-Y from door center).

    Always at least ``tub_r + 0.005`` so the hinge line sits OUTSIDE the
    cylindrical tub bore (which carves the body out to radius ``tub_r`` at the
    door center plane). Otherwise the body_to_door joint origin lands inside the
    tub void and fails the joint-origin-on-geometry baseline. Each module's frame
    rim is sized so it reaches the hinge (its half-extent == this offset).
    """
    floor = r.tub_r + 0.005
    if r.door_module == "round_porthole_door":
        return max(r.opening_r + 0.030, floor)
    if r.door_module == "convex_porthole":
        return max(r.opening_r + 0.040, floor)
    # rounded_square_window
    return max(_gasket_size(r) / 2.0, floor)


def _window_size(r: ResolvedWashingMachineConfig) -> float:
    return 2.0 * r.opening_r * 0.82


def _gasket_size(r: ResolvedWashingMachineConfig) -> float:
    return _window_size(r) * _GASKET_SIZE_FACTOR


def _body_solid(r: ResolvedWashingMachineConfig) -> cq.Workplane:
    """White cube body: cylindrical tub cavity along +X, a front door recess
    (circular or rounded-square per Slot A), and the dispenser pocket."""
    body = cq.Workplane("XY").box(r.body_d, r.body_w, r.body_h, centered=(False, True, False))

    # Tub cavity: cylinder along X, open at the front, floor at tub_back_x.
    tub = (
        cq.Workplane("ZY")
        .workplane(offset=-r.front_x)
        .center(r.door_cz, r.door_cy)
        .circle(r.tub_r)
        .extrude(r.front_x - r.tub_back_x)
    )
    body = body.cut(tub)

    # Door recess. For BOTH door families the recess is a circle inset relative
    # to the door frame's hinge-side rim, so the frame overhangs solid body at
    # the hinge line (the same geometry the round door uses successfully): the
    # body_to_door joint origin (at the frame rim) lands on the recess side wall,
    # never in carved-out void. The square gasket simply seats over the circular
    # recess (its flat back meets the front face outside the recess radius).
    if r.door_module == "rounded_square_window":
        # Recess only needs to clear the WINDOW opening (the see-through pane),
        # not the whole gasket footprint — the solid gasket frame seats flat on
        # the front face around it. Keeping the recess at ~window size leaves
        # solid body face under the hinge line (at the gasket rim), so the
        # body_to_door joint origin lands on real body geometry.
        win = _window_size(r)
        recess_side = win + 0.020
        recess_cr = max(0.010, win * 0.17)
        recess = (
            cq.Workplane("ZY")
            .workplane(offset=-r.front_x)
            .center(r.door_cz, r.door_cy)
            .rect(recess_side, recess_side)
            .extrude(0.035)
        )
        recess = recess.edges("|X").fillet(recess_cr)
        body = body.cut(recess)
    else:
        recess = (
            cq.Workplane("ZY")
            .workplane(offset=-r.front_x)
            .center(r.door_cz, r.door_cy)
            .circle(r.opening_r + 0.040)
            .extrude(0.035)
        )
        body = body.cut(recess)

    # Dispenser pocket — depth depends on Slot C (deep slot for drawer,
    # shallow recess for flip-lid tray).
    if r.dispenser_module == "pull_out_drawer":
        slot = (
            cq.Workplane("XY")
            .center(r.front_x - r.drawer_depth / 2.0, r.disp_cy)
            .rect(r.drawer_depth + 0.02, r.disp_w + 0.006)
            .extrude(r.disp_h + 0.006, both=True)
            .translate((0.0, 0.0, r.disp_cz))
        )
    else:
        depth = _DISPENSER_RECESS_DEPTH
        slot = (
            cq.Workplane("XY")
            .center(r.front_x - depth / 2.0, r.disp_cy)
            .rect(depth + 0.002, r.disp_w + 0.004)
            .extrude(r.disp_h + 0.004, both=True)
            .translate((0.0, 0.0, r.disp_cz))
        )
    body = body.cut(slot)

    return body


def _panel_inset(r: ResolvedWashingMachineConfig) -> cq.Workplane:
    """Recessed control-panel plate across the top front strip, with a sunken
    pocket whose size depends on Slot B."""
    plate = (
        cq.Workplane("XY")
        .center(r.front_x + 0.004, r.door_cy)
        .rect(0.012, r.body_w - 0.04)
        .extrude((r.panel_z1 - r.panel_z0) - 0.02, both=False)
        .translate((0.0, 0.0, r.panel_z0 + 0.01))
    )
    if r.control_module == "touch_panel_buttons":
        disp_w = _DISPLAY_W
        disp_h = _DISPLAY_H
        disp = (
            cq.Workplane("XY")
            .center(r.front_x + 0.0, 0.0)
            .rect(0.014, disp_w + 0.016)
            .extrude(disp_h + 0.016, both=False)
            .translate((0.0, 0.0, _DISPLAY_CZ(r) - (disp_h + 0.016) / 2.0))
        )
    elif r.control_module == "twin_dial_controls":
        disp = (
            cq.Workplane("XY")
            .center(r.front_x + 0.0, _TWIN_DISPLAY_CY)
            .rect(0.014, _TWIN_DISPLAY_W + 0.010)
            .extrude(_TWIN_DISPLAY_H + 0.010, both=False)
            .translate((0.0, 0.0, _DIAL_CZ(r) - (_TWIN_DISPLAY_H + 0.010) / 2.0))
        )
    else:  # single_dial_display
        disp = (
            cq.Workplane("XY")
            .center(r.front_x + 0.0, -0.075)
            .rect(0.014, 0.150)
            .extrude(0.046, both=False)
            .translate((0.0, 0.0, _DIAL_CZ(r) - 0.023))
        )
    return plate.cut(disp)


_DRUM_HUB_R = 0.018   # central spider-hub radius on the spin axis


def _drum_mesh(r: ResolvedWashingMachineConfig):
    """Stainless drum: open-front cylinder, back wall, 3 lifter ribs, a rear
    spider hub on the spin axis with a rearward drive-shaft stub, and a front
    bearing flange to the tub wall. Axis along X.

    The drum interior/front (door side) is left CLEAR of the central rod: the
    spider arms converge on a short hub boss against the REAR back wall and the
    shaft exits rearward (-X, toward the motor/pulley and the tub back panel),
    not forward toward the door.

    A ``cq.Workplane("ZY").extrude(L)`` grows in -X (verified), so the raw build
    has the rear back wall at local x=-length and the open front mouth at local
    x=0. After building we translate by +length so the LOCAL ORIGIN sits on the
    REAR hub boss (where the continuous body_to_drum spin-joint origin is
    anchored at world ``drum_back_x``); local x then runs [0, length] with x=0 =
    rear and x=length = front mouth.
    """
    length = r.drum_front_x - r.drum_back_x
    # x = -length .. 0 (rear .. front mouth) in the raw build frame.
    outer = cq.Workplane("ZY").circle(r.drum_r).extrude(length)
    inner = (
        cq.Workplane("ZY")
        .workplane(offset=-0.012)
        .circle(r.drum_r - 0.012)
        .extrude(length + 0.02)
    )
    drum = outer.cut(inner)
    # Rear hub boss: a SHORT boss against the back wall (raw x in [-length,
    # -length+0.030]) so the spider arms converge here and the spin-joint origin
    # (local origin, post-translate) lands on real drum hardware. The forward /
    # interior bore stays empty (no central rod toward the door). On a ZY plane,
    # offset=+length sets the start plane on the rear wall and extrude(-) grows
    # FORWARD (+X) into the drum.
    hub = (
        cq.Workplane("ZY")
        .workplane(offset=length)
        .circle(_DRUM_HUB_R)
        .extrude(-0.030)  # forward (+X) into the drum from the rear wall
    )
    drum = drum.union(hub)
    # Rearward drive-shaft stub: a thinner rod exiting the back wall outward in
    # -X toward the motor/pulley and the tub back panel (suggests the drive).
    # extrude(+) on this plane grows REARWARD (-X) out the back wall.
    shaft_len = (r.drum_back_x - r.tub_back_x) + 0.004  # reach the tub floor
    shaft = (
        cq.Workplane("ZY")
        .workplane(offset=length)
        .circle(_DRUM_HUB_R - 0.006)
        .extrude(shaft_len)  # rearward (-X) out the back wall toward the floor
    )
    drum = drum.union(shaft)
    # Three radial spider spokes at the REAR back wall connecting the hub boss to
    # the inner drum shell (so the hub is supported by real material, never a
    # free island).
    rib_r = r.drum_r - 0.012
    for ang in (0.0, 2 * math.pi / 3.0, 4 * math.pi / 3.0):
        # A thin bar spanning radius 0 -> rib_r in the back-wall plane, rotated
        # to angle `ang` about the X (spin) axis, seated against the rear wall
        # and growing forward (+X) so it ties into the hub boss + shell.
        spoke = (
            cq.Workplane("ZY")
            .workplane(offset=length)
            .center(0.0, rib_r / 2.0)
            .rect(0.010, rib_r + 0.006)
            .extrude(-0.014)  # forward (+X) off the rear wall into the boss
            .rotate((0, 0, 0), (1, 0, 0), math.degrees(ang))
        )
        drum = drum.union(spoke)
    # Front bearing flange reaching the tub wall (front mouth support, contact).
    flange = cq.Workplane("ZY").circle(r.tub_r - 0.002).extrude(0.008)
    flange_hole = (
        cq.Workplane("ZY").workplane(offset=-0.001).circle(r.drum_r - 0.012).extrude(0.010)
    )
    flange = flange.cut(flange_hole)
    drum = drum.union(flange)
    for ang in (0.0, 2 * math.pi / 3.0, 4 * math.pi / 3.0):
        y = (r.drum_r - 0.020) * math.cos(ang)
        z = (r.drum_r - 0.020) * math.sin(ang)
        rib = cq.Workplane("ZY").center(z, y).rect(0.018, 0.018).extrude(length - 0.03)
        drum = drum.union(rib)
    # Re-anchor the local origin onto the REAR hub boss: shift so the rear back
    # wall is at local x=0 (and the shaft stub now spans x in [-shaft_len, 0]).
    drum = drum.translate((length, 0.0, 0.0))
    return mesh_from_cadquery(drum, "drum_shell")


def _door_hinge_leaf_mesh():
    grip = (
        cq.Workplane("XY").center(0.014, 0.0).rect(0.028, 0.026).extrude(0.120, both=True)
    )
    return mesh_from_cadquery(grip, "door_hinge_leaf")


# ====================================================================== #
# Body + fixed children (drum, door)                                     #
# ====================================================================== #


def _tub_bearing_boss_mesh(r: ResolvedWashingMachineConfig):
    """Solid spindle-bearing boss on the spin axis, spanning the tub cavity from
    the floor forward to the drum mouth. The drum's continuous spin-joint origin
    (on the axis at the front lip) lands on this real body hardware, and the drum
    hub spins around it. Local frame: axis along +X, x in [0, span]."""
    span = r.drum_front_x - r.tub_back_x
    # Same ZY extrude convention as the drum mesh: local x runs [-span, 0], so
    # placed at the drum front lip the boss reaches back to the tub floor.
    boss = cq.Workplane("ZY").circle(_DRUM_HUB_R - 0.004).extrude(span)
    return mesh_from_cadquery(boss, "tub_bearing_boss")


def _build_body(model: ArticulatedObject, r: ResolvedWashingMachineConfig, mats: dict) -> None:
    body = model.part("body")
    body.visual(mesh_from_cadquery(_body_solid(r), "body_shell"), material=mats["body"], name="body_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_white", "graphite_dark", "matte_black", "champagne_gold", "retro_cream"} else "metal.stainless_matte"))
    body.visual(mesh_from_cadquery(_panel_inset(r), "panel_inset"), material=mats["panel"], name="panel_inset", material_class_id="plastic.opaque_glossy_molded")
    # Spindle-bearing boss on the spin axis (tub floor -> drum mouth) so the
    # body_to_drum joint origin sits on real body geometry.
    body.visual(
        _tub_bearing_boss_mesh(r),
        origin=Origin(xyz=(r.drum_front_x, r.door_cy, r.door_cz)),
        material=mats["drum"],
        name="tub_bearing_boss", material_class_id="metal.stainless_matte",
    )
    body.inertial = Inertial.from_geometry(
        Box((r.body_d, r.body_w, r.body_h)), mass=70.0,
        origin=Origin(xyz=(r.body_d / 2.0, 0.0, r.body_h / 2.0)),
    )


def _build_drum(model: ArticulatedObject, r: ResolvedWashingMachineConfig, mats: dict) -> None:
    body = model.get_part("body")
    drum = model.part("drum")
    drum.visual(_drum_mesh(r), material=mats["drum"], name="drum_shell", material_class_id="metal.stainless_matte")
    drum.inertial = Inertial.from_geometry(
        Box((r.drum_front_x - r.drum_back_x, 2 * r.drum_r, 2 * r.drum_r)), mass=8.0
    )
    model.articulation(
        "body_to_drum",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=drum,
        # Spin-joint origin on the REAR hub boss (drum local origin sits there):
        # parent side lands on the tub bearing boss (which spans to the rear
        # floor), child side lands on the rear hub boss. The shaft exits rearward.
        origin=Origin(xyz=(r.drum_back_x, r.door_cy, r.door_cz)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=15.0),
    )


# ---- Slot A door modules ---- #


def _door_bezel_mesh(r: ResolvedWashingMachineConfig):
    o = r.opening_r
    # Outer rim reaches the hinge line (= the door frame half-extent) so the
    # bezel always bridges from the glass out to the hinge_leaf on the body.
    outer = _door_frame_half_y(r)
    bez = BezelGeometry(
        (2 * o * 0.86, 2 * o * 0.86),
        (2 * outer, 2 * outer),
        0.060,
        opening_shape="circle",
        outer_shape="circle",
        face=None,
    )
    bez.rotate_y(math.pi / 2.0)
    return mesh_from_geometry(bez, "door_bezel")


def _door_round_glass_mesh(r: ResolvedWashingMachineConfig):
    glass = cq.Workplane("ZY").circle(r.opening_r * 0.90).extrude(0.010)
    return mesh_from_cadquery(glass, "door_glass")


def _door_gasket_mesh(r: ResolvedWashingMachineConfig):
    win = _window_size(r)
    gasket = 2.0 * _door_frame_half_y(r)  # outer rim reaches the hinge line
    bez = BezelGeometry(
        (win, win),
        (gasket, gasket),
        0.060,
        opening_shape="rounded_rect",
        outer_shape="rounded_rect",
        opening_corner_radius=win * 0.17,
        outer_corner_radius=gasket * 0.16,
        face=None,
    )
    bez.rotate_y(math.pi / 2.0)
    return mesh_from_geometry(bez, "door_gasket")


def _door_square_glass_mesh(r: ResolvedWashingMachineConfig):
    win = _window_size(r)
    glass_side = win + 0.008
    glass_cr = max(0.006, win * 0.17 - 0.010)
    glass = cq.Workplane("ZY").rect(glass_side, glass_side).extrude(0.010)
    glass = glass.edges("|X").fillet(glass_cr)
    return mesh_from_cadquery(glass, "door_glass")


def _door_chrome_ring_mesh(r: ResolvedWashingMachineConfig):
    o = r.opening_r
    ring_inner_r = o * 0.88 + 0.004
    ring_outer_r = _door_frame_half_y(r)  # outer rim reaches the hinge line
    ring_depth = 0.055
    outer = cq.Workplane("XY").circle(ring_outer_r).extrude(ring_depth)
    inner = cq.Workplane("XY").circle(ring_inner_r).extrude(ring_depth)
    ring = outer.cut(inner)
    ring = ring.translate((0, 0, -ring_depth / 2.0))
    ring = ring.rotate((0, 0, 0), (0, 1, 0), -90)
    return mesh_from_cadquery(ring, "door_chrome_ring")


def _porthole_glass_radius(r: ResolvedWashingMachineConfig) -> float:
    # Sized to overlap the chrome-ring inner wall (ring_inner = opening_r*0.88 +
    # 0.004) so the porthole glass is connected to the ring, never a free island.
    return r.opening_r * 0.88 + 0.012


def _door_porthole_disk_mesh(r: ResolvedWashingMachineConfig):
    """Flat tinted backing disk of the convex porthole — a clean single-component
    cylinder (like the round door's glass) that overlaps the chrome-ring inner
    wall so it is structurally connected."""
    glass_r = _porthole_glass_radius(r)
    disk = cq.Workplane("ZY").circle(glass_r).extrude(0.016)
    return mesh_from_cadquery(disk, "door_porthole_disk")


def _door_porthole_dome_mesh(r: ResolvedWashingMachineConfig):
    """Forward-bulging convex dome cap of the porthole, seated ON the backing
    disk (its flat back overlaps the disk). A separate visual so the curved mesh
    never has to fuse with the flat disk at the tessellation level; it stays
    supported because it embeds into the disk."""
    glass_r = _porthole_glass_radius(r) - 0.006
    bulge = 0.050
    R = (glass_r ** 2 + bulge ** 2) / (2.0 * bulge)
    sphere = cq.Workplane("XY").sphere(R)
    keep = cq.Workplane("XY").rect(R * 3, R * 3).extrude(bulge + 0.010).translate((0, 0, R - bulge - 0.010))
    cap = sphere.intersect(keep)
    limit_cyl = cq.Workplane("XY").circle(glass_r).extrude(bulge + 0.03).translate((0, 0, R - bulge - 0.016))
    cap = cap.intersect(limit_cyl)
    cap = cap.translate((0, 0, -(R - bulge)))
    cap = cap.rotate((0, 0, 0), (0, 1, 0), 90)
    return mesh_from_cadquery(cap, "door_porthole_dome")


def _door_latch_mesh():
    block = cq.Workplane("XY").box(0.030, 0.040, 0.060, centered=(True, True, True))
    notch = (
        cq.Workplane("XY").center(0.016, 0.0).box(0.014, 0.028, 0.030, centered=(True, True, True))
    )
    block = block.cut(notch)
    return mesh_from_cadquery(block, "door_latch")


def _build_door(model: ArticulatedObject, r: ResolvedWashingMachineConfig, mats: dict) -> list[tuple]:
    """Door part: shape per Slot A. Returns the list of intentional overlaps
    (part_a_name, part_b_name, elem_a, elem_b, reason)."""
    body = model.get_part("body")
    half_y = _door_frame_half_y(r)
    hinge_y = r.door_cy + half_y
    center_y = -half_y  # window center in door-local coords
    door = model.part("door")
    overlaps: list[tuple] = []

    # Body-side door hinge bracket: a vertical post on the cabinet front at the
    # hinge line. The cabinet hinge always mounts here, so the body_to_door joint
    # origin lands on real body geometry for every Slot-A door module. It extends
    # from a little proud of the front face back to BEHIND the door recess
    # back-wall, so it always embeds into the solid body shell (and is never an
    # island) regardless of how deep the recess is carved around it.

    if r.door_module == "round_porthole_door":
        door.visual(_door_bezel_mesh(r), origin=Origin(xyz=(0.0, center_y, 0.0)), material=mats["frame"], name="door_bezel", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_white", "inox_silver", "matte_black", "champagne_gold"} else "metal.chrome_polished"))
        door.visual(_door_round_glass_mesh(r), origin=Origin(xyz=(0.012, center_y, 0.0)), material=mats["glass"], name="door_glass", material_class_id="glass.smoked_tinted")
        frame_elem, glass_elem = "door_bezel", "door_glass"
    elif r.door_module == "rounded_square_window":
        door.visual(_door_gasket_mesh(r), origin=Origin(xyz=(0.0, center_y, 0.0)), material=mats["frame"], name="door_gasket", material_class_id="rubber.smooth_plain")
        door.visual(_door_square_glass_mesh(r), origin=Origin(xyz=(0.012, center_y, 0.0)), material=mats["glass"], name="door_glass", material_class_id="glass.smoked_tinted")
        frame_elem, glass_elem = "door_gasket", "door_glass"
    else:  # convex_porthole
        door.visual(_door_chrome_ring_mesh(r), origin=Origin(xyz=(0.0, center_y, 0.0)), material=mats["accent"], name="door_chrome_ring", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_white", "graphite_dark", "inox_silver", "matte_black", "retro_cream"} else "metal.brass_polished"))
        # Flat backing disk (overlaps the ring) + a separate forward-bulging dome
        # cap seated on it. Splitting the curved dome off the flat disk avoids the
        # curved-solid tessellation seam that the islands check would flag.
        door.visual(_door_porthole_disk_mesh(r), origin=Origin(xyz=(0.005, center_y, 0.0)), material=mats["glass"], name="door_porthole_disk", material_class_id="glass.smoked_tinted")
        door.visual(_door_porthole_dome_mesh(r), origin=Origin(xyz=(0.013, center_y, 0.0)), material=mats["glass"], name="door_porthole_dome", material_class_id="glass.smoked_tinted")
        door.visual(_door_latch_mesh(), origin=Origin(xyz=(0.025, 2.0 * center_y + 0.010, 0.0)), material=mats["control"], name="door_latch", material_class_id=("metal.brushed_silver" if r.palette_style in {"classic_white", "graphite_dark", "matte_black", "champagne_gold"} else "metal.chrome_polished"))
        frame_elem, glass_elem = "door_chrome_ring", "door_porthole_disk"

    door.visual(_door_hinge_leaf_mesh(), origin=Origin(xyz=(0.0, 0.0, 0.0)), material=mats["frame"], name="door_hinge_leaf", material_class_id="metal.stainless_matte")
    door.inertial = Inertial.from_geometry(
        Box((0.06, 2 * half_y, 2 * half_y)), mass=3.2,
        origin=Origin(xyz=(0.03, center_y, 0.0)),
    )
    model.articulation(
        "body_to_door",
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=Origin(xyz=(r.front_x - 0.005, hinge_y, r.door_cz)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=10.0, velocity=2.0, lower=0.0, upper=r.door_open_angle),
    )

    overlaps.append(("door", "body", frame_elem, "body_shell", "Door frame seats over the front opening recess of the body."))
    overlaps.append(("door", "body", "door_hinge_leaf", "body_shell", "Door hinge leaf is mounted against the front cabinet face."))
    overlaps.append(("door", "door", glass_elem, frame_elem, "Window glass seats into the door frame inner wall (intentional seat)."))
    if r.door_module == "convex_porthole":
        overlaps.append(("door", "door", "door_porthole_dome", "door_porthole_disk", "Convex dome cap is seated on (embedded into) the backing disk."))
    return overlaps


# ---- Slot B control modules ---- #

# single-dial display block
def _display_solid(r: ResolvedWashingMachineConfig) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .center(r.front_x - 0.001, -0.075)
        .rect(0.010, 0.140)
        .extrude(0.040, both=False)
        .translate((0.0, 0.0, _DIAL_CZ(r) - 0.020))
    )


def _DIAL_CZ(r: ResolvedWashingMachineConfig) -> float:
    return 0.785 * (r.body_h / _NOM_BODY_H)


def _DISPLAY_CZ(r: ResolvedWashingMachineConfig) -> float:
    return 0.790 * (r.body_h / _NOM_BODY_H)


_DIAL_CY = 0.055
_DISPLAY_W = 0.350
_DISPLAY_H = 0.065
_BUTTON_COUNT = 5
_BUTTON_D = 0.014
_BUTTON_T = 0.003
_BUTTON_SPACING = 0.040
_TWIN_DIAL_DIAMETER = 0.040
_TWIN_DIAL_HEIGHT = 0.018
_TWIN_DISPLAY_CY = -0.19
_TWIN_DISPLAY_W = 0.080
_TWIN_DISPLAY_H = 0.028


def _single_dial_knob():
    knob = KnobGeometry(
        0.060, 0.022,
        body_style="skirted",
        top_diameter=0.050,
        skirt=KnobSkirt(0.066, 0.005, flare=0.06, chamfer=0.0012),
        grip=KnobGrip(style="fluted", count=24, depth=0.0012),
        indicator=KnobIndicator(style="line", mode="raised", depth=0.0010),
    )
    knob.rotate_y(math.pi / 2.0)
    return mesh_from_geometry(knob, "dial_cap")


def _twin_dial_knob(name: str):
    d = _TWIN_DIAL_DIAMETER
    knob = KnobGeometry(
        d, _TWIN_DIAL_HEIGHT,
        body_style="skirted",
        top_diameter=d * 0.82,
        skirt=KnobSkirt(d * 1.10, 0.004, flare=0.05, chamfer=0.001),
        grip=KnobGrip(style="fluted", count=20, depth=0.001),
        indicator=KnobIndicator(style="line", mode="raised", depth=0.0008),
    )
    knob.rotate_y(math.pi / 2.0)
    return mesh_from_geometry(knob, name)


def _button_mesh(name: str):
    disk = cq.Workplane("ZY").circle(_BUTTON_D / 2.0).extrude(_BUTTON_T)
    return mesh_from_cadquery(disk, name)


def _build_control(model: ArticulatedObject, r: ResolvedWashingMachineConfig, mats: dict) -> list[tuple]:
    body = model.get_part("body")
    overlaps: list[tuple] = []
    dial_cz = _DIAL_CZ(r)

    if r.control_module == "single_dial_display":
        body.visual(mesh_from_cadquery(_display_solid(r), "display"), material=mats["display"], name="display", material_class_id="tech.emissive_surface")
        dial = model.part("dial")
        dial.visual(_single_dial_knob(), material=mats["control"], name="dial_cap", material_class_id=("metal.brushed_silver" if r.palette_style in {"classic_white", "graphite_dark", "matte_black", "champagne_gold"} else "metal.chrome_polished"))
        dial.inertial = Inertial.from_geometry(Box((0.022, 0.066, 0.066)), mass=0.05)
        model.articulation(
            "body_to_dial",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=dial,
            origin=Origin(xyz=(r.front_x - 0.001, _DIAL_CY, dial_cz)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=0.5, velocity=6.0),
        )
        overlaps.append(("dial", "body", "dial_cap", "panel_inset", "Dial base seats against the control-panel inset."))
        overlaps.append(("dial", "body", "dial_cap", "body_shell", "Dial shaft/back is recessed into the front face behind the panel."))

    elif r.control_module == "touch_panel_buttons":
        disp_cz = _DISPLAY_CZ(r)
        touch = (
            cq.Workplane("XY")
            .center(r.front_x - 0.001, 0.0)
            .rect(0.008, _DISPLAY_W)
            .extrude(_DISPLAY_H, both=False)
            .translate((0.0, 0.0, disp_cz - _DISPLAY_H / 2.0))
        )
        body.visual(mesh_from_cadquery(touch, "touch_display"), material=mats["display"], name="touch_display", material_class_id="tech.emissive_surface")
        button_cz = r.panel_z0 + 0.024
        for i in range(_BUTTON_COUNT):
            by = (i - (_BUTTON_COUNT - 1) / 2.0) * _BUTTON_SPACING
            body.visual(
                _button_mesh(f"button_{i}"),
                origin=Origin(xyz=(r.front_x + 0.002, by, button_cz)),
                material=mats["button"],
                name=f"button_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        # No dial articulation for the touch module.

    else:  # twin_dial_controls
        twin_disp = (
            cq.Workplane("XY")
            .center(r.front_x - 0.001, _TWIN_DISPLAY_CY)
            .rect(0.010, _TWIN_DISPLAY_W)
            .extrude(_TWIN_DISPLAY_H, both=False)
            .translate((0.0, 0.0, dial_cz - _TWIN_DISPLAY_H / 2.0))
        )
        body.visual(mesh_from_cadquery(twin_disp, "display"), material=mats["display"], name="display", material_class_id="tech.emissive_surface")
        for i, cy in enumerate((0.06, -0.06)):
            dial_part = model.part(f"dial_{i}")
            dial_part.visual(_twin_dial_knob(f"dial_{i}_cap"), material=mats["control"], name=f"dial_{i}_cap", material_class_id=("metal.brushed_silver" if r.palette_style in {"classic_white", "graphite_dark", "matte_black", "champagne_gold"} else "metal.chrome_polished"))
            dial_part.inertial = Inertial.from_geometry(
                Box((_TWIN_DIAL_HEIGHT, _TWIN_DIAL_DIAMETER * 1.10, _TWIN_DIAL_DIAMETER * 1.10)), mass=0.03
            )
            model.articulation(
                f"body_to_dial_{i}",
                ArticulationType.CONTINUOUS,
                parent=body,
                child=dial_part,
                origin=Origin(xyz=(r.front_x - 0.001, cy, dial_cz)),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=0.5, velocity=6.0),
            )
            overlaps.append((f"dial_{i}", "body", f"dial_{i}_cap", "panel_inset", "Dial base seats against the control-panel inset."))
            overlaps.append((f"dial_{i}", "body", f"dial_{i}_cap", "body_shell", "Dial shaft/back is recessed behind the panel."))

    return overlaps


# ---- Slot C dispenser modules ---- #

_DISPENSER_RECESS_DEPTH = 0.050   # shallow recess for the flip-lid tray
_DISPENSER_LID_T = 0.010


def _drawer_mesh(r: ResolvedWashingMachineConfig):
    depth = r.drawer_depth
    w = r.disp_w
    h = r.disp_h
    tray = cq.Workplane("XY").box(depth, w, h, centered=(False, True, True))
    cavity = (
        cq.Workplane("XY")
        .center(0.012, 0.0)
        .box(depth - 0.006, w - 0.016, h - 0.012, centered=(False, True, True))
        .translate((0.0, 0.0, 0.006))
    )
    tray = tray.cut(cavity)
    for yy in (-0.025, 0.025):
        wall = cq.Workplane("XY").center(depth / 2.0, yy).box(0.004, 0.004, h - 0.014, centered=(True, True, True))
        tray = tray.union(wall)
    front = (
        cq.Workplane("XY")
        .center(depth + 0.006, 0.0)
        .box(0.012, w + 0.010, h + 0.014, centered=(True, True, True))
    )
    tray = tray.union(front)
    return mesh_from_cadquery(tray, "drawer_tray")


def _dispenser_tray_mesh(r: ResolvedWashingMachineConfig):
    depth = _DISPENSER_RECESS_DEPTH
    w = r.disp_w
    h = r.disp_h
    base = cq.Workplane("XY").box(0.005, w - 0.006, h - 0.006, centered=(False, True, True))
    tray = base
    bottom = (
        cq.Workplane("XY").box(depth, 0.005, h - 0.006, centered=(False, True, True))
        .translate((0.0, -(w - 0.006) / 2.0 + 0.0025, 0.0))
    )
    tray = tray.union(bottom)
    top_wall = (
        cq.Workplane("XY").box(depth, 0.005, h - 0.006, centered=(False, True, True))
        .translate((0.0, (w - 0.006) / 2.0 - 0.0025, 0.0))
    )
    tray = tray.union(top_wall)
    floor = (
        cq.Workplane("XY").box(depth, w - 0.006, 0.005, centered=(False, True, False))
        .translate((0.0, 0.0, -(h - 0.006) / 2.0))
    )
    tray = tray.union(floor)
    for yy in (-0.025, 0.025):
        wall = (
            cq.Workplane("XY").box(depth - 0.006, 0.004, h - 0.010, centered=(False, True, True))
            .translate((0.003, yy, 0.0))
        )
        tray = tray.union(wall)
    return mesh_from_cadquery(tray, "dispenser_tray")


def _dispenser_lid_mesh(r: ResolvedWashingMachineConfig):
    w = r.disp_w
    h = r.disp_h
    panel = (
        cq.Workplane("XY")
        .box(_DISPENSER_LID_T, w + 0.002, h + 0.002, centered=(True, True, True))
        .translate((0.0, 0.0, -(h + 0.002) / 2.0))
    )
    grip = (
        cq.Workplane("XY")
        .box(0.014, 0.040, 0.008, centered=(True, True, True))
        .translate((0.0, 0.0, -(h + 0.002) + 0.004))
    )
    lid = panel.union(grip)
    return mesh_from_cadquery(lid, "dispenser_lid")


def _build_dispenser(model: ArticulatedObject, r: ResolvedWashingMachineConfig, mats: dict) -> list[tuple]:
    body = model.get_part("body")
    overlaps: list[tuple] = []

    if r.dispenser_module == "pull_out_drawer":
        drawer = model.part("drawer")
        drawer.visual(_drawer_mesh(r), material=mats["panel"], name="drawer_tray", material_class_id="plastic.opaque_glossy_molded")
        drawer.visual(
            Box((0.014, 0.060, 0.012)),
            origin=Origin(xyz=(r.drawer_depth + 0.014, 0.0, 0.0)),
            material=mats["frame"],
            name="drawer_pull", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_white", "inox_silver", "matte_black", "champagne_gold"} else "metal.chrome_polished"),
        )
        drawer.inertial = Inertial.from_geometry(
            Box((r.drawer_depth, r.disp_w, r.disp_h)), mass=0.6,
            origin=Origin(xyz=(r.drawer_depth / 2.0, 0.0, 0.0)),
        )
        model.articulation(
            "body_to_drawer",
            ArticulationType.PRISMATIC,
            parent=body,
            child=drawer,
            origin=Origin(xyz=(r.front_x - r.drawer_depth - 0.004, r.disp_cy, r.disp_cz)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=5.0, velocity=0.3, lower=0.0, upper=r.drawer_travel),
        )
        overlaps.append(("drawer", "body", "drawer_tray", "body_shell", "Detergent drawer tray slides inside its slot cut into the body."))

    else:  # flip_lid_tray
        depth = _DISPENSER_RECESS_DEPTH
        body.visual(
            _dispenser_tray_mesh(r),
            origin=Origin(xyz=(r.front_x - depth - 0.005, r.disp_cy, r.disp_cz)),
            material=mats["panel"],
            name="dispenser_tray", material_class_id="plastic.opaque_glossy_molded",
        )
        # Visible hinge barrel along the top edge of the recess: real flip-lid
        # hardware, and it puts solid body geometry exactly at the joint origin.
        hinge_z = r.disp_cz + r.disp_h / 2.0 + 0.006
        barrel = (
            cq.Workplane("XZ")
            .center(0.0, 0.0)
            .circle(0.006)
            .extrude(r.disp_w * 0.92, both=True)
        )
        body.visual(
            mesh_from_cadquery(barrel, "dispenser_hinge_barrel"),
            origin=Origin(xyz=(r.front_x - 0.004, r.disp_cy, hinge_z)),
            material=mats["frame"],
            name="dispenser_hinge_barrel", material_class_id="metal.stainless_matte",
        )
        lid_drop = hinge_z - (r.disp_cz + r.disp_h / 2.0)
        dispenser_lid = model.part("dispenser_lid")
        dispenser_lid.visual(
            _dispenser_lid_mesh(r),
            origin=Origin(xyz=(0.0, 0.0, -lid_drop)),
            material=mats["panel"],
            name="dispenser_lid_panel", material_class_id="plastic.opaque_glossy_molded",
        )
        dispenser_lid.inertial = Inertial.from_geometry(
            Box((_DISPENSER_LID_T, r.disp_w, r.disp_h)), mass=0.15,
            origin=Origin(xyz=(0.0, 0.0, -r.disp_h / 2.0 - lid_drop)),
        )
        model.articulation(
            "body_to_dispenser_lid",
            ArticulationType.REVOLUTE,
            parent=body,
            child=dispenser_lid,
            origin=Origin(xyz=(r.front_x - 0.004, r.disp_cy, hinge_z)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=r.dispenser_open_angle),
        )
        overlaps.append(("dispenser_lid", "body", "dispenser_lid_panel", "body_shell", "Flip-lid panel sits flush in the dispenser recess."))
        overlaps.append(("dispenser_lid", "body", "dispenser_lid_panel", "dispenser_tray", "Flip-lid panel seats over the fixed dispenser tray."))
        overlaps.append(("dispenser_lid", "body", "dispenser_lid_panel", "dispenser_hinge_barrel", "Flip-lid panel pivots on the hinge barrel."))

    return overlaps


# ---- Slot D base / service modules ---- #

_PANEL_W = 0.44
_PANEL_T = 0.010


def _plinth_solid(r: ResolvedWashingMachineConfig, panel_h: float, panel_hinge_z: float) -> cq.Workplane:
    plinth = (
        cq.Workplane("XY")
        .box(r.body_d, r.body_w, r.plinth_h + 0.005, centered=(False, True, False))
        .translate((0.0, 0.0, -r.plinth_h))
    )
    cut_cz = panel_hinge_z + (panel_h + 0.006) / 2.0
    cutout = (
        cq.Workplane("XY")
        .center(r.front_x - _PANEL_T / 2.0, 0.0)
        .box(_PANEL_T + 0.02, _PANEL_W + 0.006, panel_h + 0.006, centered=(True, True, True))
        .translate((0.0, 0.0, cut_cz))
    )
    return plinth.cut(cutout)


def _service_panel_mesh(panel_h: float) -> cq.Workplane:
    panel = (
        cq.Workplane("XY")
        .center(-_PANEL_T / 2.0, 0.0)
        .box(_PANEL_T, _PANEL_W, panel_h, centered=(True, True, False))
    )
    lip = (
        cq.Workplane("XY")
        .center(0.003, 0.0)
        .box(0.006, _PANEL_W - 0.06, 0.010, centered=(True, True, False))
        .translate((0.0, 0.0, panel_h - 0.014))
    )
    panel = panel.union(lip)
    for side in (-1, 1):
        pivot = (
            cq.Workplane("XY")
            .center(-_PANEL_T / 2.0, side * (_PANEL_W / 2.0 - 0.006))
            .box(_PANEL_T + 0.004, 0.014, 0.014, centered=(True, True, True))
        )
        panel = panel.union(pivot)
    return mesh_from_cadquery(panel, "service_panel")


def _build_base(model: ArticulatedObject, r: ResolvedWashingMachineConfig, mats: dict) -> list[tuple]:
    body = model.get_part("body")
    overlaps: list[tuple] = []

    if r.base_module == "flat_service_panel":
        # Keep the flush service hatch clear of the (possibly large) door frame
        # bottom: clamp its top below the lowest reach of the door envelope.
        half_y = _door_frame_half_y(r)
        door_bottom_z = r.door_cz - half_y
        hatch_w = 0.130
        hatch_top = min(r.hatch_cz + hatch_w / 2.0, door_bottom_z - 0.015)
        hatch_cz = hatch_top - hatch_w / 2.0
        # Push it toward the far -Y corner, also clear of the door's -Y edge.
        hatch_cy = min(r.hatch_cy, r.door_cy - half_y - hatch_w / 2.0 - 0.010)
        hatch_cy = max(hatch_cy, -(r.body_w / 2.0) + hatch_w / 2.0 + 0.015)
        body.visual(
            Box((0.010, hatch_w, hatch_w)),
            origin=Origin(xyz=(r.front_x - 0.003, hatch_cy, hatch_cz)),
            material=mats["panel"],
            name="service_hatch", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_white", "graphite_dark", "matte_black", "champagne_gold", "retro_cream"} else "metal.stainless_matte"),
        )
        for fy in (-0.24, 0.24):
            for fx in (0.07, r.body_d - 0.07):
                body.visual(
                    Box((0.05, 0.05, 0.02)),
                    origin=Origin(xyz=(fx, fy, -0.01)),
                    material=mats["frame"],
                    name=f"foot_{'f' if fx > r.body_d / 2 else 'r'}_{'p' if fy > 0 else 'n'}", material_class_id="rubber.smooth_plain",
                )

    else:  # raised_plinth_flip_panel
        panel_h = r.plinth_h - 0.020
        panel_hinge_z = -r.plinth_h + 0.008
        body.visual(mesh_from_cadquery(_plinth_solid(r, panel_h, panel_hinge_z), "plinth_base"), material=mats["plinth"], name="plinth_base", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_white", "graphite_dark", "matte_black", "champagne_gold", "retro_cream"} else "metal.stainless_matte"))
        for fy in (-0.24, 0.24):
            for fx in (0.07, r.body_d - 0.07):
                body.visual(
                    Box((0.05, 0.05, 0.02)),
                    origin=Origin(xyz=(fx, fy, -r.plinth_h - 0.01)),
                    material=mats["frame"],
                    name=f"foot_{'f' if fx > r.body_d / 2 else 'r'}_{'p' if fy > 0 else 'n'}", material_class_id="rubber.smooth_plain",
                )
        panel = model.part("service_panel")
        panel.visual(_service_panel_mesh(panel_h), material=mats["plinth"], name="service_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_white", "graphite_dark", "matte_black", "champagne_gold", "retro_cream"} else "metal.stainless_matte"))
        panel.inertial = Inertial.from_geometry(
            Box((_PANEL_T, _PANEL_W, panel_h)), mass=0.4,
            origin=Origin(xyz=(-_PANEL_T / 2.0, 0.0, panel_h / 2.0)),
        )
        model.articulation(
            "body_to_panel",
            ArticulationType.REVOLUTE,
            parent=body,
            child=panel,
            origin=Origin(xyz=(r.front_x, 0.0, panel_hinge_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=1.5, lower=0.0, upper=r.panel_open_angle),
        )
        overlaps.append(("service_panel", "body", "service_panel", "plinth_base", "Service panel seats in the plinth cutout."))

    return overlaps


# ====================================================================== #
# Build entry points                                                     #
# ====================================================================== #


def _resolve_palette(style: str) -> dict[str, tuple[float, float, float, float]]:
    return PALETTE_PRESETS.get(style, PALETTE_PRESETS["classic_white"])


# Module label that the run_tests function uses to replay overlaps.
_LAST_OVERLAPS: list[tuple] = []


def build_washing_machine(
    config: WashingMachineConfig, *, assets: Optional[AssetContext] = None
) -> ArticulatedObject:
    r = resolve_config(config)
    colors = _resolve_palette(r.palette_style)

    model = ArticulatedObject(name="front_load_washer")
    mats = {key: model.material(f"wm_{key}", rgba=rgba) for key, rgba in colors.items()}

    overlaps: list[tuple] = []
    _build_body(model, r, mats)
    _build_drum(model, r, mats)
    overlaps += _build_door(model, r, mats)
    overlaps += _build_control(model, r, mats)
    overlaps += _build_dispenser(model, r, mats)
    overlaps += _build_base(model, r, mats)

    # drum is always nested + retained by its spin joint.
    overlaps.append(("drum", "body", "drum_shell", "body_shell", "Drum is nested inside the hollow tub cavity bored into the body."))
    # Drum spider hub spins concentrically around the body's tub bearing boss.
    overlaps.append(("drum", "body", "drum_shell", "tub_bearing_boss", "Drum spider hub spins concentrically around the body spindle-bearing boss."))

    # Stash resolved config + overlaps on the model so run_tests can replay them.
    model._wm_resolved = r  # type: ignore[attr-defined]
    model._wm_overlaps = overlaps  # type: ignore[attr-defined]
    return model


def build_seeded_washing_machine(seed: int) -> ArticulatedObject:
    return build_washing_machine(config_from_seed(seed))


# ====================================================================== #
# Tests                                                                  #
# ====================================================================== #


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _center(aabb):
    mn, mx = aabb
    return ((mn[0] + mx[0]) / 2.0, (mn[1] + mx[1]) / 2.0, (mn[2] + mx[2]) / 2.0)


def run_washing_machine_tests(
    model: ArticulatedObject, config: WashingMachineConfig
) -> TestReport:
    ctx = TestContext(model)
    r: ResolvedWashingMachineConfig = getattr(model, "_wm_resolved", None) or resolve_config(config)
    overlaps: list[tuple] = getattr(model, "_wm_overlaps", [])

    body = model.get_part("body")
    drum = model.get_part("drum")
    door = model.get_part("door")

    # ---- Replay intentional overlaps gathered during build ---- #
    for (pa, pb, ea, eb, reason) in overlaps:
        ctx.allow_overlap(
            model.get_part(pa), model.get_part(pb), elem_a=ea, elem_b=eb, reason=reason
        )
    # Drum floats inside the tub cavity, retained by the continuous spin joint.
    ctx.allow_isolated_part(
        drum,
        reason="Drum is nested in the tub cavity with radial clearance; retained by the continuous body_to_drum spin joint.",
    )
    if "drawer" in {p.name for p in model.parts}:
        ctx.allow_isolated_part(
            model.get_part("drawer"),
            reason="detergent drawer slides out of the body and loses contact",
        )

    front_x = r.front_x

    # ---- Door at front face, covering the front opening ---- #
    door_pos = ctx.part_world_position(door)
    ctx.check(
        "door mounted at the front face",
        door_pos is not None and door_pos[0] > front_x - 0.05,
        details=f"door origin={door_pos}",
    )
    frame_elem = {
        "round_porthole_door": "door_bezel",
        "rounded_square_window": "door_gasket",
        "convex_porthole": "door_chrome_ring",
    }[r.door_module]
    ctx.expect_overlap(
        door, body, axes="yz", min_overlap=0.05,
        elem_a=frame_elem, elem_b="body_shell",
        name="door frame covers the front opening",
    )

    # ---- Drum recessed behind the door, fully inside the body ---- #
    drum_aabb = ctx.part_world_aabb(drum)
    ctx.check(
        "drum recessed behind the front face",
        drum_aabb is not None and drum_aabb[1][0] <= front_x - 0.010,
        details=f"drum max-x={None if drum_aabb is None else drum_aabb[1][0]}",
    )
    ctx.check(
        "drum stays inside the washer body",
        drum_aabb is not None
        and drum_aabb[0][0] >= r.tub_back_x - 0.02
        and drum_aabb[1][0] <= front_x - 0.010,
        details=f"drum x-span={None if drum_aabb is None else (drum_aabb[0][0], drum_aabb[1][0])}",
    )

    # ---- Drum spins about +X ---- #
    drum_joint = model.get_articulation("body_to_drum")
    rib0 = _ext(ctx.part_world_aabb(drum))
    with ctx.pose({drum_joint: math.pi / 2.0}):
        rib90 = _ext(ctx.part_world_aabb(drum))
    ctx.check(
        "drum spins about the front-back axis",
        abs(rib90[0] - rib0[0]) < 0.01,
        details=f"axial extent rest={rib0[0]:.4f} spun={rib90[0]:.4f}",
    )

    # ---- Door swings forward on a vertical (Z) hinge ---- #
    door_joint = model.get_articulation("body_to_door")
    closed = ctx.part_world_aabb(door)
    with ctx.pose({door_joint: r.door_open_angle}):
        opened = ctx.part_world_aabb(door)
    ctx.check(
        "door swings forward when opened",
        opened[1][0] > closed[1][0] + 0.06,
        details=f"closed max-x={closed[1][0]:.4f}, open max-x={opened[1][0]:.4f}",
    )
    ctx.check(
        "door hinge axis is vertical (Z extent preserved)",
        abs(_ext(opened)[2] - _ext(closed)[2]) < 0.03,
        details=f"closed z-ext={_ext(closed)[2]:.4f}, open z-ext={_ext(opened)[2]:.4f}",
    )
    hinge_closed = ctx.part_element_world_aabb(door, elem="door_hinge_leaf")
    with ctx.pose({door_joint: r.door_open_angle}):
        hinge_open = ctx.part_element_world_aabb(door, elem="door_hinge_leaf")
    hc = _center(hinge_closed)
    ho = _center(hinge_open)
    ctx.check(
        "visible left hinge leaf is the door pivot",
        hc[1] > r.door_cy
        and abs(ho[0] - hc[0]) < 0.04
        and abs(ho[1] - hc[1]) < 0.04,
        details=f"closed hinge center={hc}, open hinge center={ho}",
    )

    # ---- Slot B control checks ---- #
    if r.control_module == "single_dial_display":
        dial_joint = model.get_articulation("body_to_dial")
        di0 = _ext(ctx.part_world_aabb(model.get_part("dial")))
        with ctx.pose({dial_joint: math.pi / 2.0}):
            di90 = _ext(ctx.part_world_aabb(model.get_part("dial")))
        ctx.check(
            "dial spins about the front-facing axis",
            abs(di90[0] - di0[0]) < 0.008,
            details=f"dial axial extent rest={di0[0]:.4f} spun={di90[0]:.4f}",
        )
    elif r.control_module == "twin_dial_controls":
        d0 = ctx.part_world_position(model.get_part("dial_0"))
        d1 = ctx.part_world_position(model.get_part("dial_1"))
        ctx.check(
            "twin dials are laterally separated",
            abs(d0[1] - d1[1]) > _TWIN_DIAL_DIAMETER,
            details=f"dial_0 y={d0[1]:.4f}, dial_1 y={d1[1]:.4f}",
        )
        ctx.check(
            "twin dials are at equal height",
            abs(d0[2] - d1[2]) < 0.01,
            details=f"dial_0 z={d0[2]:.4f}, dial_1 z={d1[2]:.4f}",
        )
    else:  # touch_panel_buttons
        disp_aabb = ctx.part_element_world_aabb(body, elem="touch_display")
        disp_w = disp_aabb[1][1] - disp_aabb[0][1]
        ctx.check(
            "touch display is wide (>= 0.30 m)",
            disp_w >= 0.30,
            details=f"display width={disp_w:.3f} m",
        )

    # ---- Slot C dispenser checks ---- #
    if r.dispenser_module == "pull_out_drawer":
        drawer = model.get_part("drawer")
        drawer_joint = model.get_articulation("body_to_drawer")
        dr_rest = ctx.part_world_position(drawer)
        with ctx.pose({drawer_joint: r.drawer_travel}):
            dr_out = ctx.part_world_position(drawer)
        ctx.check(
            "detergent drawer slides out forward",
            dr_out[0] > dr_rest[0] + r.drawer_travel - 0.005,
            details=f"rest_x={dr_rest[0]:.4f}, out_x={dr_out[0]:.4f}",
        )
        ctx.expect_overlap(
            drawer, body, axes="x", min_overlap=0.05,
            elem_a="drawer_tray", elem_b="body_shell",
            name="drawer retained in its slot",
        )
    else:  # flip_lid_tray
        lid = model.get_part("dispenser_lid")
        lid_joint = model.get_articulation("body_to_dispenser_lid")
        l_closed = ctx.part_world_aabb(lid)
        with ctx.pose({lid_joint: r.dispenser_open_angle}):
            l_open = ctx.part_world_aabb(lid)
        ctx.check(
            "flip-lid opens forward (+X)",
            l_open[1][0] > l_closed[1][0] + 0.01,
            details=f"closed max-x={l_closed[1][0]:.4f}, open max-x={l_open[1][0]:.4f}",
        )

    # ---- Slot D base checks ---- #
    if r.base_module == "raised_plinth_flip_panel":
        panel = model.get_part("service_panel")
        panel_joint = model.get_articulation("body_to_panel")
        p_closed = ctx.part_world_aabb(panel)
        with ctx.pose({panel_joint: r.panel_open_angle}):
            p_open = ctx.part_world_aabb(panel)
        ctx.check(
            "service panel flips forward/down",
            p_open[1][0] > p_closed[1][0] + 0.01,
            details=f"closed max-x={p_closed[1][0]:.4f}, open max-x={p_open[1][0]:.4f}",
        )
        body_aabb = ctx.part_world_aabb(body)
        ctx.check(
            "feet drop with the plinth (body extends below z=0)",
            body_aabb is not None and body_aabb[0][2] < -r.plinth_h + 0.03,
            details=f"body min-z={None if body_aabb is None else body_aabb[0][2]:.4f}",
        )

    return ctx.report()


# Aliases the sweep harness may probe by generic name.
build = build_washing_machine
run_washing_machine_template_tests = run_washing_machine_tests
