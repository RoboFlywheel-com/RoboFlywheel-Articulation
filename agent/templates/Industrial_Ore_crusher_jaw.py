# SPDX-License-Identifier: Apache-2.0

"""Industrial / Ore crusher (jaw) -- modular procedural template.

A single-eccentric jaw rock crusher: a heavy grounded ``frame`` (welded flat
side plates or a cast monobloc housing) holding, between a tilted fixed jaw
plate and a swinging movable jaw plate, a wedge crushing chamber. An eccentric
shaft spins a heavy flywheel + V-belt pulley (fed by a side motor pulley) and
drives the swing jaw through a short crushing stroke; a toggle back-linkage
(mechanical toggle plate / hydraulic cylinder / double-toggle pitman pair)
closes the loop to the frame seat.

Slot graph (pattern = mixed: root frame + 2 parallel-children slots + 3
multiplicity axes cross_member_count / flywheel_spoke_count / jaw_rib_count):

    frame (root; welded_plate_frame / cast_monobloc_frame; + fixed jaw welded|adjustable)
        |- drive  (spoked_flywheel / solid_disc_flywheel : eccentric shaft + flywheel + pulleys)
        |- crush  (single_toggle / dodge_pivot / double_toggle / hydraulic_toggle : swing jaw + linkage)

Adapted per AUTHORING.md SS A/B from the confirmed 5-star Ore-crusher pool
(spec: specs_modular_v1/Industrial_Ore_crusher_jaw.md). The single independent
crushing DOF is ``frame_to_swing_jaw`` REVOLUTE; every back-linkage part is a
Mimic of it, so the only independent sampled joints are the CONTINUOUS eccentric
shaft, the REVOLUTE crushing stroke, and (adjustable mode) the PRISMATIC fixed-
jaw setting ram. The eccentric shaft carries only rotationally-compact/outboard
visuals so its continuous spin never sweeps into the frame.

Coordinate frame: +X = rear (motor side), -X = front (fixed jaw), +Y = drive
pulley side, -Y = flywheel side, +Z = up.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from agent.templates._modular import (
    InterfaceSpec,
    ModuleBuild,
    ModuleBuildContext,
    SlotSpec,
    assemble,
)
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    BoxGeometry,
    CylinderGeometry,
    ExtrudeGeometry,
    LatheGeometry,
    MeshGeometry,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


FrameForm = Literal["welded_plate_frame", "cast_monobloc_frame"]
FlywheelForm = Literal["spoked_flywheel", "solid_disc_flywheel"]
CrushLinkage = Literal["single_toggle", "dodge_pivot", "double_toggle", "hydraulic_toggle"]
FixedJawMode = Literal["welded", "adjustable"]
CrusherPalette = Literal[
    "steel_orange",
    "blue_industrial",
    "green_machine",
    "red_oxide",
    "cat_yellow",
    "graphite_dark",
]


# --------------------------------------------------------------------------- #
# Canonical dimensions (origin bcb3073f)
# --------------------------------------------------------------------------- #

SIDE_PLATE_THICK = 0.07
SIDE_PLATE_Y = 0.635
SIDE_INNER = SIDE_PLATE_Y - SIDE_PLATE_THICK / 2.0  # 0.60
SIDE_TOP_Z = 1.55

SHAFT_X = 0.25
SHAFT_Z = 1.66
SHAFT_R = 0.095
ECC_BOSS_R = 0.115
HUB_OUTER_R = 0.20
HUB_BORE_R = 0.105
HUB_WIDTH = 1.00

JAW_STROKE = 0.025  # rad, nominal opening swing (scaled by jaw_stroke_scale)

FIXED_PLATE_CENTER = (-0.4075, 0.945)
FIXED_PLATE_LEN_HALF = 0.631
FIXED_PLATE_ANGLE = math.atan2(0.505, 1.15)  # ~0.4136 rad
FIXED_PLATE_THICK = 0.09

FRONT_WALL_THICK = 0.10
FRONT_WALL_SHIFT = FIXED_PLATE_THICK / 2.0 + FRONT_WALL_THICK / 2.0 - 0.004

RIB_R = 0.028

# Single-toggle back link (jaw-local frame, jaw origin at the eccentric shaft)
TOGGLE_SEAT_LOCAL = (0.26, -1.14)
TOGGLE_LEN = 0.34
TOGGLE_ROCKER_R = 0.032
TOGGLE_HALF_W = 0.26

MOTOR_PULLEY_POS = (1.02, 0.85, 0.585)
BELT_RATIO = 3.5

# Dodge-type bottom pivot
BOTTOM_PIVOT_X = 0.05
BOTTOM_PIVOT_Z = 0.38
ECC_REL_X = SHAFT_X - BOTTOM_PIVOT_X  # 0.20
ECC_REL_Z = SHAFT_Z - BOTTOM_PIVOT_Z  # 1.28
DODGE_TOGGLE_SEAT = (0.30, 0.72)

# Blake double-toggle
PIVOT_X = 0.10
PIVOT_Z = 1.58
PIVOT_BOSS_R = 0.075
PIVOT_BOSS_LEN = 0.12
ECCENTRIC_THROW = 0.025
PITMAN_HUB_R = 0.16
PITMAN_HUB_W = 0.52
PITMAN_BODY_X = 0.14
PITMAN_BODY_THICK = 0.10
PITMAN_BODY_WIDTH = 0.52
PITMAN_BODY_HEIGHT = 0.88
JAW_TOGGLE_X = 0.10
JAW_TOGGLE_Z = -0.90
FRAME_TOGGLE_SEAT = (0.85, 0.0, 0.68)
FRONT_TOGGLE_LEN = 0.17
REAR_TOGGLE_LEN = 0.41

# Cast monobloc frame
CAST_WALL = 0.10
CAST_INNER_HALF_W = SIDE_INNER  # 0.60
CAST_OUTER_HALF_W = CAST_INNER_HALF_W + CAST_WALL  # 0.70

# Fixed-jaw setting ram
FIXED_PLATE_TRAVEL = 0.028  # gated <= closed_gap - 0.02 in resolve_config

WELDED_WALL_VISUALS = ("flywheel_side_plate", "drive_side_plate", "front_wall", "rear_wall")


# --------------------------------------------------------------------------- #
# Palettes (>=6 colorways; tokens shared so every .visual resolves)
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "steel_orange": {
        "frame_gray": (0.58, 0.60, 0.63, 1.0),
        "steel_light": (0.74, 0.76, 0.78, 1.0),
        "jaw_orange": (0.86, 0.32, 0.10, 1.0),
        "wheel_gray": (0.42, 0.44, 0.47, 1.0),
        "shaft_steel": (0.55, 0.56, 0.58, 1.0),
        "motor_gray": (0.62, 0.64, 0.67, 1.0),
        "toggle_steel": (0.50, 0.52, 0.55, 1.0),
        "hydraulic_body": (0.28, 0.30, 0.34, 1.0),
    },
    "blue_industrial": {
        "frame_gray": (0.18, 0.32, 0.52, 1.0),
        "steel_light": (0.72, 0.75, 0.80, 1.0),
        "jaw_orange": (0.90, 0.74, 0.16, 1.0),
        "wheel_gray": (0.14, 0.24, 0.40, 1.0),
        "shaft_steel": (0.55, 0.57, 0.60, 1.0),
        "motor_gray": (0.22, 0.36, 0.56, 1.0),
        "toggle_steel": (0.40, 0.44, 0.50, 1.0),
        "hydraulic_body": (0.10, 0.16, 0.28, 1.0),
    },
    "green_machine": {
        "frame_gray": (0.20, 0.42, 0.28, 1.0),
        "steel_light": (0.72, 0.76, 0.72, 1.0),
        "jaw_orange": (0.88, 0.42, 0.12, 1.0),
        "wheel_gray": (0.16, 0.32, 0.22, 1.0),
        "shaft_steel": (0.54, 0.56, 0.54, 1.0),
        "motor_gray": (0.26, 0.46, 0.32, 1.0),
        "toggle_steel": (0.40, 0.48, 0.42, 1.0),
        "hydraulic_body": (0.10, 0.22, 0.14, 1.0),
    },
    "red_oxide": {
        "frame_gray": (0.52, 0.22, 0.16, 1.0),
        "steel_light": (0.78, 0.72, 0.70, 1.0),
        "jaw_orange": (0.20, 0.20, 0.22, 1.0),
        "wheel_gray": (0.40, 0.18, 0.13, 1.0),
        "shaft_steel": (0.58, 0.55, 0.54, 1.0),
        "motor_gray": (0.56, 0.28, 0.22, 1.0),
        "toggle_steel": (0.48, 0.40, 0.38, 1.0),
        "hydraulic_body": (0.26, 0.12, 0.09, 1.0),
    },
    "cat_yellow": {
        "frame_gray": (0.90, 0.72, 0.10, 1.0),
        "steel_light": (0.80, 0.80, 0.78, 1.0),
        "jaw_orange": (0.16, 0.16, 0.17, 1.0),
        "wheel_gray": (0.20, 0.20, 0.20, 1.0),
        "shaft_steel": (0.58, 0.58, 0.56, 1.0),
        "motor_gray": (0.82, 0.66, 0.12, 1.0),
        "toggle_steel": (0.35, 0.35, 0.34, 1.0),
        "hydraulic_body": (0.14, 0.14, 0.15, 1.0),
    },
    "graphite_dark": {
        "frame_gray": (0.22, 0.23, 0.25, 1.0),
        "steel_light": (0.60, 0.62, 0.65, 1.0),
        "jaw_orange": (0.84, 0.36, 0.12, 1.0),
        "wheel_gray": (0.16, 0.17, 0.18, 1.0),
        "shaft_steel": (0.44, 0.45, 0.47, 1.0),
        "motor_gray": (0.28, 0.29, 0.31, 1.0),
        "toggle_steel": (0.34, 0.35, 0.37, 1.0),
        "hydraulic_body": (0.10, 0.10, 0.12, 1.0),
    },
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class IndustrialOreCrusherJawConfig:
    frame_form: FrameForm = "welded_plate_frame"
    flywheel_form: FlywheelForm = "spoked_flywheel"
    crush_linkage: CrushLinkage = "single_toggle"
    fixed_jaw_mode: FixedJawMode = "welded"
    palette_style: CrusherPalette = "steel_orange"

    cross_member_count: int = 2
    flywheel_spoke_count: int = 6  # ignored for solid_disc_flywheel
    jaw_rib_count: int = 9

    jaw_stroke_scale: float = 1.0
    flywheel_scale: float = 1.0
    plate_gap_scale: float = 1.0


@dataclass(frozen=True)
class ResolvedIndustrialOreCrusherJawConfig:
    frame_form: FrameForm
    flywheel_form: FlywheelForm
    crush_linkage: CrushLinkage
    fixed_jaw_mode: FixedJawMode
    palette_style: str

    cross_member_count: int
    flywheel_spoke_count: int
    jaw_rib_count: int

    jaw_stroke_scale: float
    flywheel_scale: float
    plate_gap_scale: float

    # Derived
    jaw_stroke: float
    fixed_plate_standoff: float  # +normal outward shift of the fixed plate (m)
    fixed_plate_travel: float

    palette: dict[str, tuple[float, float, float, float]]


# --------------------------------------------------------------------------- #
# Seed-driven sampling (procedural-first)
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> IndustrialOreCrusherJawConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin (mother record) combination (welded plates + spoked
    flywheel x6 + single-toggle + welded fixed jaw + 9 ribs + 2 cross members,
    steel_orange) as a documented regression anchor; every other seed is fully
    procedural.
    """
    if seed == 0:
        return IndustrialOreCrusherJawConfig()

    rng = random.Random(seed)

    frame_form: FrameForm = rng.choice(("welded_plate_frame", "cast_monobloc_frame"))
    flywheel_form: FlywheelForm = rng.choice(("spoked_flywheel", "solid_disc_flywheel"))
    crush_linkage: CrushLinkage = rng.choice(
        ("single_toggle", "dodge_pivot", "double_toggle", "hydraulic_toggle")
    )
    fixed_jaw_mode: FixedJawMode = rng.choices(("welded", "adjustable"), weights=(0.6, 0.4))[0]
    palette_style = rng.choice(PALETTE_NAMES)

    cross_member_count = rng.choices((2, 3, 4), weights=(0.5, 0.2, 0.3))[0]
    flywheel_spoke_count = rng.choices((4, 6, 8), weights=(0.2, 0.5, 0.3))[0]
    jaw_rib_count = rng.choices((5, 7, 9), weights=(0.3, 0.2, 0.5))[0]

    jaw_stroke_scale = round(rng.uniform(0.8, 1.4), 4)
    flywheel_scale = round(rng.uniform(0.9, 1.2), 4)
    plate_gap_scale = round(rng.uniform(0.9, 1.25), 4)

    return IndustrialOreCrusherJawConfig(
        frame_form=frame_form,
        flywheel_form=flywheel_form,
        crush_linkage=crush_linkage,
        fixed_jaw_mode=fixed_jaw_mode,
        palette_style=palette_style,
        cross_member_count=cross_member_count,
        flywheel_spoke_count=flywheel_spoke_count,
        jaw_rib_count=jaw_rib_count,
        jaw_stroke_scale=jaw_stroke_scale,
        flywheel_scale=flywheel_scale,
        plate_gap_scale=plate_gap_scale,
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(
    config: IndustrialOreCrusherJawConfig,
) -> ResolvedIndustrialOreCrusherJawConfig:
    if str(config.frame_form) not in {"welded_plate_frame", "cast_monobloc_frame"}:
        raise ValueError(f"Unsupported frame_form: {config.frame_form}")
    if str(config.flywheel_form) not in {"spoked_flywheel", "solid_disc_flywheel"}:
        raise ValueError(f"Unsupported flywheel_form: {config.flywheel_form}")
    if str(config.crush_linkage) not in {
        "single_toggle",
        "dodge_pivot",
        "double_toggle",
        "hydraulic_toggle",
    }:
        raise ValueError(f"Unsupported crush_linkage: {config.crush_linkage}")
    if str(config.fixed_jaw_mode) not in {"welded", "adjustable"}:
        raise ValueError(f"Unsupported fixed_jaw_mode: {config.fixed_jaw_mode}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    cross_member_count = int(_clamp(config.cross_member_count, 2, 4))
    flywheel_spoke_count = int(_clamp(config.flywheel_spoke_count, 4, 8))
    jaw_rib_count = int(_clamp(config.jaw_rib_count, 5, 9))

    jaw_stroke_scale = _clamp(config.jaw_stroke_scale, 0.8, 1.4)
    flywheel_scale = _clamp(config.flywheel_scale, 0.9, 1.2)
    plate_gap_scale = _clamp(config.plate_gap_scale, 0.9, 1.25)

    jaw_stroke = min(JAW_STROKE * jaw_stroke_scale, 0.035)

    # plate_gap_scale nudges the fixed plate along its outward normal (away from
    # the chamber) so the nominal closed discharge gap widens for scale>1.
    fixed_plate_standoff = (plate_gap_scale - 1.0) * 0.04
    # Nominal closed gap ~0.05 m; ram travel gated so an advanced plate never
    # reaches the movable plate (inequality constraint, spec SS7).
    closed_gap = 0.05 + fixed_plate_standoff
    fixed_plate_travel = max(0.0, min(FIXED_PLATE_TRAVEL, closed_gap - 0.02))

    return ResolvedIndustrialOreCrusherJawConfig(
        frame_form=config.frame_form,
        flywheel_form=config.flywheel_form,
        crush_linkage=config.crush_linkage,
        fixed_jaw_mode=config.fixed_jaw_mode,
        palette_style=config.palette_style,
        cross_member_count=cross_member_count,
        flywheel_spoke_count=flywheel_spoke_count,
        jaw_rib_count=jaw_rib_count,
        jaw_stroke_scale=jaw_stroke_scale,
        flywheel_scale=flywheel_scale,
        plate_gap_scale=plate_gap_scale,
        jaw_stroke=jaw_stroke,
        fixed_plate_standoff=fixed_plate_standoff,
        fixed_plate_travel=fixed_plate_travel,
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# Geometry helpers (adapted from origin (mother record) + variants)
# --------------------------------------------------------------------------- #

_SIDE_PROFILE = [
    (-1.05, 0.115),
    (1.05, 0.115),
    (1.05, 0.85),
    (0.60, SIDE_TOP_Z),
    (-1.05, SIDE_TOP_Z),
]


def _box_at(size: tuple[float, float, float], center: tuple[float, float, float]) -> MeshGeometry:
    return BoxGeometry(size).translate(*center)


def _cyl_y(
    radius: float, length: float, center: tuple[float, float, float], segments: int = 32
) -> MeshGeometry:
    geo = CylinderGeometry(radius, length, radial_segments=segments)
    geo.rotate_x(math.pi / 2.0)
    return geo.translate(*center)


def _corrugation_ribs(
    geo: MeshGeometry, *, count: int, y0: float, span: float, x: float, z: float, rib_len: float
) -> None:
    spacing = span / (count - 1) if count > 1 else 0.0
    y_start = -span / 2.0 if count > 1 else 0.0
    _ = y0
    for i in range(count):
        yk = y_start + i * spacing
        rib = CylinderGeometry(RIB_R, rib_len, radial_segments=20)
        rib.translate(x, yk, z)
        geo.merge(rib)


def _side_plate_mesh(y_center: float) -> MeshGeometry:
    geo = ExtrudeGeometry(_SIDE_PROFILE, SIDE_PLATE_THICK, cap=True, center=True)
    geo.rotate_x(math.pi / 2.0)
    return geo.translate(0.0, y_center, 0.0)


def _cast_side_wall_mesh(y_center: float) -> MeshGeometry:
    geo = ExtrudeGeometry(_SIDE_PROFILE, CAST_WALL, cap=True, center=True)
    geo.rotate_x(math.pi / 2.0)
    return geo.translate(0.0, y_center, 0.0)


def _base_rails_mesh() -> MeshGeometry:
    geo = MeshGeometry()
    geo.merge(_box_at((2.10, 0.16, 0.12), (0.0, -SIDE_PLATE_Y, 0.06)))
    geo.merge(_box_at((2.10, 0.16, 0.12), (0.0, SIDE_PLATE_Y, 0.06)))
    geo.merge(_box_at((0.55, 0.90, 0.10), (1.025, 1.05, 0.05)))  # motor ground plate
    return geo


def _single_cross_member_mesh(xc: float) -> MeshGeometry:
    return _box_at((0.14, 1.28, 0.10), (xc, 0.0, 0.05))


def _front_wall_mesh() -> MeshGeometry:
    theta = FIXED_PLATE_ANGLE
    n = (math.cos(theta), 0.0, math.sin(theta))
    cx = FIXED_PLATE_CENTER[0] - FRONT_WALL_SHIFT * n[0]
    cz = FIXED_PLATE_CENTER[1] - FRONT_WALL_SHIFT * n[2]
    geo = BoxGeometry((FRONT_WALL_THICK, 2.0 * SIDE_INNER + 0.04, 1.34))
    geo.rotate_y(-theta)
    return geo.translate(cx, 0.0, cz)


def _rear_wall_mesh() -> MeshGeometry:
    return _box_at((0.10, 1.24, 0.755), (1.0, 0.0, 0.4925))


def _cast_housing_mesh() -> MeshGeometry:
    """Cast monobloc housing: thick volumetric side walls + integral bottom /
    front / rear walls + raised bearing bosses (Volumetric Envelope Form,
    adapted from cast_monobloc_frame S3 without cadquery booleans)."""
    geo = MeshGeometry()
    geo.merge(_cast_side_wall_mesh(-(CAST_INNER_HALF_W + CAST_WALL / 2.0)))
    geo.merge(_cast_side_wall_mesh(CAST_INNER_HALF_W + CAST_WALL / 2.0))
    # bottom connecting slab between the side walls
    geo.merge(_box_at((2.00, 2.0 * CAST_INNER_HALF_W, CAST_WALL), (0.0, 0.0, 0.115 + CAST_WALL / 2.0)))
    # integral tilted front wall + rear wall
    geo.merge(_front_wall_mesh())
    geo.merge(_rear_wall_mesh())
    # raised bearing bosses cast into the outer side walls
    for sign in (-1.0, 1.0):
        yc = sign * (CAST_OUTER_HALF_W + 0.015)
        geo.merge(_cyl_y(0.16, 0.03, (SHAFT_X, yc, SHAFT_Z)))
    return geo


def _toggle_seat_mesh(seat_x: float, z_hi: float, z_lo: float) -> MeshGeometry:
    geo = MeshGeometry()
    geo.merge(_box_at((0.22, 0.56, 0.05), (seat_x, 0.0, z_hi)))
    geo.merge(_box_at((0.22, 0.56, 0.045), (seat_x, 0.0, z_lo)))
    return geo


def _rod_bracket_mesh() -> MeshGeometry:
    geo = MeshGeometry()
    geo.merge(_box_at((0.16, 0.02, 0.18), (0.92, -0.04, 0.21)))
    geo.merge(_box_at((0.16, 0.02, 0.18), (0.92, 0.04, 0.21)))
    return geo


def _bearing_housings_mesh() -> MeshGeometry:
    geo = MeshGeometry()
    for sign in (-1.0, 1.0):
        yc = sign * SIDE_PLATE_Y
        geo.merge(_box_at((0.34, 0.18, 0.115), (SHAFT_X, yc, 1.6025)))
        geo.merge(_cyl_y(0.13, 0.18, (SHAFT_X, yc, SHAFT_Z)))
    return geo


def _motor_pedestal_mesh() -> MeshGeometry:
    geo = MeshGeometry()
    geo.merge(_box_at((0.36, 0.40, 0.29), (1.02, 1.19, 0.24)))
    geo.merge(_box_at((0.46, 0.56, 0.05), (1.02, 1.19, 0.40)))
    return geo


def _motor_mesh() -> MeshGeometry:
    x, z = 1.02, 0.585
    geo = MeshGeometry()
    geo.merge(_cyl_y(0.17, 0.50, (x, 1.19, z)))
    for yf in (1.02, 1.10, 1.18, 1.26, 1.34):
        geo.merge(_cyl_y(0.185, 0.012, (x, yf, z)))
    geo.merge(_cyl_y(0.145, 0.04, (x, 0.94, z)))
    geo.merge(_cyl_y(0.145, 0.04, (x, 1.44, z)))
    geo.merge(_box_at((0.14, 0.16, 0.10), (x, 1.19, 0.78)))
    geo.merge(_cyl_y(0.028, 0.07, (x, 0.915, z), segments=20))
    return geo


def _fixed_jaw_plate_mesh(rib_count: int, standoff: float) -> MeshGeometry:
    geo = MeshGeometry()
    geo.merge(BoxGeometry((FIXED_PLATE_THICK, 1.16, 2.0 * FIXED_PLATE_LEN_HALF)))
    _corrugation_ribs(
        geo, count=rib_count, y0=-0.52, span=1.04, x=FIXED_PLATE_THICK / 2.0, z=0.0, rib_len=1.20
    )
    geo.rotate_y(-FIXED_PLATE_ANGLE)
    theta = FIXED_PLATE_ANGLE
    # outward normal of the tilted crushing face points toward the chamber (+X);
    # standoff shifts the plate AWAY from the chamber to widen the closed gap.
    cx = FIXED_PLATE_CENTER[0] - standoff * math.cos(theta)
    cz = FIXED_PLATE_CENTER[1] - standoff * math.sin(theta)
    return geo.translate(cx, 0.0, cz)


def _adjustment_wedge_mesh() -> MeshGeometry:
    theta = FIXED_PLATE_ANGLE
    nx, nz = math.cos(theta), math.sin(theta)
    wall_cx = FIXED_PLATE_CENTER[0] - FRONT_WALL_SHIFT * nx
    wall_cz = FIXED_PLATE_CENTER[1] - FRONT_WALL_SHIFT * nz
    face_cx = wall_cx + (FRONT_WALL_THICK / 2.0) * nx
    face_cz = wall_cz + (FRONT_WALL_THICK / 2.0) * nz
    geo = MeshGeometry()
    carriage_thick = 0.022
    carriage = BoxGeometry((carriage_thick, 1.22, 1.32))
    carriage_cx = face_cx + (carriage_thick / 2.0) * nx
    carriage_cz = face_cz + (carriage_thick / 2.0) * nz
    carriage.rotate_y(-theta)
    carriage.translate(carriage_cx, 0.0, carriage_cz)
    geo.merge(carriage)
    ram_cx = face_cx + 0.04 * nx
    ram_cz = face_cz + 0.04 * nz - 0.08
    ram = BoxGeometry((0.08, 0.28, 0.14))
    ram.rotate_y(-theta)
    ram.translate(ram_cx, 0.0, ram_cz)
    geo.merge(ram)
    for yoff in (-0.09, 0.09):
        cyl = CylinderGeometry(0.025, 0.10, radial_segments=16)
        cyl.rotate_y(-theta)
        cyl.translate(ram_cx - 0.06 * nx, yoff, ram_cz - 0.06 * nz)
        geo.merge(cyl)
    return geo


# ---- drive layer ----------------------------------------------------------

def _eccentric_shaft_mesh() -> MeshGeometry:
    return _cyl_y(SHAFT_R, 2.10, (0.0, -0.05, 0.0))


def _eccentric_boss_mesh() -> MeshGeometry:
    return _cyl_y(ECC_BOSS_R, 0.88, (0.0, 0.0, 0.0))


def _flywheel_spoked_mesh(spoke_count: int, scale: float) -> MeshGeometry:
    ro = 0.55 * scale
    ri = 0.44 * scale
    geo = MeshGeometry()
    geo.merge(
        LatheGeometry.from_shell_profiles(
            [(ro, -0.08), (ro, 0.08)], [(ri, -0.08), (ri, 0.08)], segments=56
        )
    )
    for i in range(spoke_count):
        spoke = BoxGeometry((0.38 * scale, 0.075, 0.09))
        spoke.translate(0.28 * scale, 0.0, 0.0)
        spoke.rotate_z(i * 2.0 * math.pi / spoke_count)
        geo.merge(spoke)
    geo.merge(CylinderGeometry(0.14, 0.20, radial_segments=32))
    geo.rotate_x(math.pi / 2.0)
    return geo.translate(0.0, -0.95, 0.0)


def _flywheel_disc_mesh(scale: float) -> MeshGeometry:
    ro = 0.55 * scale
    ri = 0.50 * scale
    geo = MeshGeometry()
    geo.merge(CylinderGeometry(ri, 0.065, radial_segments=56))  # solid web disc
    geo.merge(
        LatheGeometry.from_shell_profiles(
            [(ro, -0.085), (ro, 0.085)], [(ri, -0.085), (ri, 0.085)], segments=56
        )
    )
    geo.merge(CylinderGeometry(0.16, 0.12, radial_segments=32))  # hub boss
    for zo in (-0.085, 0.085):
        chamfer = CylinderGeometry(ro - 0.01, 0.012, radial_segments=48)
        chamfer.translate(0.0, 0.0, zo)
        geo.merge(chamfer)
    geo.rotate_x(math.pi / 2.0)
    return geo.translate(0.0, -0.95, 0.0)


def _drive_pulley_mesh() -> MeshGeometry:
    geo = MeshGeometry()
    geo.merge(CylinderGeometry(0.34, 0.14, radial_segments=48))
    for zo in (-0.0575, 0.0575):
        cheek = CylinderGeometry(0.40, 0.025, radial_segments=48)
        cheek.translate(0.0, 0.0, zo)
        geo.merge(cheek)
    geo.merge(CylinderGeometry(0.12, 0.16, radial_segments=32))
    geo.rotate_x(math.pi / 2.0)
    return geo.translate(0.0, 0.85, 0.0)


def _motor_pulley_mesh() -> MeshGeometry:
    geo = MeshGeometry()
    geo.merge(CylinderGeometry(0.115, 0.10, radial_segments=32))
    for zo in (-0.045, 0.045):
        cheek = CylinderGeometry(0.135, 0.02, radial_segments=32)
        cheek.translate(0.0, 0.0, zo)
        geo.merge(cheek)
    geo.rotate_x(math.pi / 2.0)
    return geo


# ---- swing jaw meshes ------------------------------------------------------

def _pitman_hub_mesh() -> MeshGeometry:
    """Solid pitman bearing boss centered on the pivot axis (the eccentric shaft
    passes through it via a captured-bearing allow_overlap, exactly like the
    satellite gimbal barrel idiom). Solid so the REVOLUTE pivot axis touches
    child hardware (origin-honesty)."""
    geo = CylinderGeometry(HUB_OUTER_R, HUB_WIDTH, radial_segments=48)
    geo.rotate_x(math.pi / 2.0)
    return geo


def _single_pitman_body_mesh() -> MeshGeometry:
    profile = [
        (-0.185, -1.20),
        (-0.10, -1.30),
        (0.10, -1.30),
        (0.24, -1.18),
        (0.30, -0.78),
        (0.26, -0.40),
        (0.16, -0.14),
        (-0.185, -0.14),
    ]
    geo = ExtrudeGeometry(profile, 1.08, cap=True, center=True)
    geo.rotate_x(math.pi / 2.0)
    geo.merge(
        _box_at(
            (0.085, 2.0 * (TOGGLE_HALF_W + 0.01), 0.12),
            (0.2425, 0.0, TOGGLE_SEAT_LOCAL[1]),
        )
    )
    return geo


def _single_movable_plate_mesh(rib_count: int) -> MeshGeometry:
    geo = MeshGeometry()
    geo.merge(_box_at((0.07, 1.08, 1.22), (-0.21, 0.0, -0.63)))
    _corrugation_ribs(geo, count=rib_count, y0=-0.48, span=0.96, x=-0.245, z=-0.63, rib_len=1.18)
    return geo


def _single_tension_rod_mesh(start: tuple[float, float]) -> MeshGeometry:
    direction = (0.9246, -0.3807)
    length = 0.46
    theta = math.atan2(direction[0], direction[1])
    geo = MeshGeometry()
    geo.merge(_box_at((0.10, 0.10, 0.10), (start[0], 0.0, start[1])))
    rod = CylinderGeometry(0.02, length, radial_segments=16)
    rod.translate(0.0, 0.0, length / 2.0)
    rod.rotate_y(theta)
    rod.translate(start[0], 0.0, start[1])
    geo.merge(rod)
    for i in range(6):
        d = 0.23 + i * 0.028
        coil = TorusGeometry(0.034, 0.016, radial_segments=10, tubular_segments=24)
        coil.rotate_y(theta)
        coil.translate(start[0] + direction[0] * d, 0.0, start[1] + direction[1] * d)
        geo.merge(coil)
    washer = CylinderGeometry(0.055, 0.02, radial_segments=24)
    washer.rotate_y(theta)
    washer.translate(start[0] + direction[0] * 0.41, 0.0, start[1] + direction[1] * 0.41)
    geo.merge(washer)
    return geo


def _toggle_plate_mesh() -> MeshGeometry:
    geo = MeshGeometry()
    geo.merge(_box_at((0.32, 2.0 * TOGGLE_HALF_W, 0.056), (TOGGLE_LEN / 2.0, 0.0, 0.0)))
    for xr in (0.0, TOGGLE_LEN):
        rocker = CylinderGeometry(TOGGLE_ROCKER_R, 0.50, radial_segments=20)
        rocker.rotate_x(math.pi / 2.0)
        rocker.translate(xr, 0.0, 0.0)
        geo.merge(rocker)
    return geo


def _hydraulic_cylinder_mesh() -> MeshGeometry:
    geo = MeshGeometry()
    rod_r, barrel_r, gland_r, eye_r, eye_w, collar_r = 0.022, 0.036, 0.042, 0.035, 0.05, 0.030
    front_eye = CylinderGeometry(eye_r, eye_w, radial_segments=24)
    front_eye.rotate_x(math.pi / 2.0)
    geo.merge(front_eye)
    collar = CylinderGeometry(collar_r, 0.020, radial_segments=20)
    collar.rotate_y(math.pi / 2.0)
    collar.translate(0.045, 0.0, 0.0)
    geo.merge(collar)
    rod_x0, rod_len = 0.055, 0.095
    rod = CylinderGeometry(rod_r, rod_len, radial_segments=20)
    rod.rotate_y(math.pi / 2.0)
    rod.translate(rod_x0 + rod_len / 2.0, 0.0, 0.0)
    geo.merge(rod)
    gland_x0, gland_len = rod_x0 + rod_len, 0.025
    gland = CylinderGeometry(gland_r, gland_len, radial_segments=24)
    gland.rotate_y(math.pi / 2.0)
    gland.translate(gland_x0 + gland_len / 2.0, 0.0, 0.0)
    geo.merge(gland)
    barrel_x0, barrel_len = gland_x0 + gland_len, 0.14
    barrel = CylinderGeometry(barrel_r, barrel_len, radial_segments=28)
    barrel.rotate_y(math.pi / 2.0)
    barrel.translate(barrel_x0 + barrel_len / 2.0, 0.0, 0.0)
    geo.merge(barrel)
    cap = CylinderGeometry(barrel_r + 0.004, 0.014, radial_segments=28)
    cap.rotate_y(math.pi / 2.0)
    cap.translate(barrel_x0 + barrel_len + 0.007, 0.0, 0.0)
    geo.merge(cap)
    rear_eye = CylinderGeometry(eye_r, eye_w, radial_segments=24)
    rear_eye.rotate_x(math.pi / 2.0)
    rear_eye.translate(TOGGLE_LEN, 0.0, 0.0)
    geo.merge(rear_eye)
    for x_port in (0.21, 0.29):
        port = CylinderGeometry(0.013, 0.028, radial_segments=12)
        port.translate(x_port, 0.0, barrel_r + 0.014)
        geo.merge(port)
        cap_ft = CylinderGeometry(0.018, 0.010, radial_segments=6)
        cap_ft.translate(x_port, 0.0, barrel_r + 0.028 + 0.005)
        geo.merge(cap_ft)
    return geo


# ---- dodge-type swing jaw --------------------------------------------------

def _jaw_pivot_mount_mesh() -> MeshGeometry:
    geo = MeshGeometry()
    for sign in (-1.0, 1.0):
        yc = sign * (SIDE_INNER - 0.04)
        geo.merge(_cyl_y(0.11, 0.10, (BOTTOM_PIVOT_X, yc, BOTTOM_PIVOT_Z)))
    geo.merge(
        _box_at(
            (0.14, 2.0 * (SIDE_INNER - 0.04), 0.10),
            (BOTTOM_PIVOT_X, 0.0, BOTTOM_PIVOT_Z - 0.07),
        )
    )
    return geo


def _dodge_pitman_body_mesh() -> MeshGeometry:
    profile = [
        (-0.08, 0.05),
        (0.025, 0.18),
        (0.025, 1.05),
        (0.10, 1.22),
        (0.22, 1.28),
        (0.30, 1.15),
        (0.30, 0.75),
        (0.25, 0.30),
        (0.16, 0.05),
    ]
    geo = ExtrudeGeometry(profile, 1.08, cap=True, center=True)
    geo.rotate_x(math.pi / 2.0)
    geo.merge(
        _box_at(
            (0.085, 2.0 * (TOGGLE_HALF_W + 0.01), 0.12),
            (DODGE_TOGGLE_SEAT[0], 0.0, DODGE_TOGGLE_SEAT[1]),
        )
    )
    pivot_boss = CylinderGeometry(0.13, 0.90, radial_segments=32)
    pivot_boss.rotate_x(math.pi / 2.0)
    geo.merge(pivot_boss)
    return geo


def _dodge_hub_mesh() -> MeshGeometry:
    return _pitman_hub_mesh().translate(ECC_REL_X, 0.0, ECC_REL_Z)


def _dodge_movable_plate_mesh(rib_count: int) -> MeshGeometry:
    geo = MeshGeometry()
    geo.merge(_box_at((0.07, 1.08, 1.08), (-0.01, 0.0, 0.66)))
    _corrugation_ribs(geo, count=rib_count, y0=0.0, span=0.90, x=-0.045, z=0.66, rib_len=1.04)
    return geo


# ---- Blake double-toggle ---------------------------------------------------

def _pivot_bosses_mesh() -> MeshGeometry:
    geo = MeshGeometry()
    for sign in (-1.0, 1.0):
        yc = sign * (SIDE_INNER - PIVOT_BOSS_LEN / 2.0)
        geo.merge(_cyl_y(PIVOT_BOSS_R, PIVOT_BOSS_LEN, (PIVOT_X, yc, PIVOT_Z)))
    return geo


def _double_swing_jaw_body_mesh() -> MeshGeometry:
    profile = [
        (-0.01, 0.03),
        (-0.04, -0.02),
        (-0.03, -0.30),
        (-0.03, -0.80),
        (-0.02, -1.15),
        (0.08, -1.15),
        (0.08, -0.80),
        (0.06, -0.30),
    ]
    geo = ExtrudeGeometry(profile, 1.08, cap=True, center=True)
    geo.rotate_x(math.pi / 2.0)
    geo.merge(_box_at((0.12, 0.54, 0.10), (0.06, 0.0, JAW_TOGGLE_Z)))
    return geo


def _double_movable_plate_mesh(rib_count: int) -> MeshGeometry:
    # Lowered/shortened vs the single-toggle plate so its top stays below the
    # top pivot bosses (z_world ~1.49 < PIVOT_Z 1.58), clearing them.
    geo = MeshGeometry()
    geo.merge(_box_at((0.07, 1.08, 1.10), (-0.06, 0.0, -0.64)))
    _corrugation_ribs(geo, count=rib_count, y0=-0.48, span=0.90, x=-0.095, z=-0.64, rib_len=1.06)
    return geo


def _pitman_member_mesh() -> MeshGeometry:
    """Pitman member with the hub centered on the shaft axis (local origin)."""
    geo = MeshGeometry()
    geo.merge(_cyl_y(PITMAN_HUB_R, PITMAN_HUB_W, (0.0, 0.0, 0.0)))
    web_z_top = -PITMAN_HUB_R
    geo.merge(
        _box_at(
            (PITMAN_BODY_X + PITMAN_BODY_THICK * 0.5, PITMAN_BODY_WIDTH * 0.7, 0.08),
            (PITMAN_BODY_X * 0.5, 0.0, web_z_top - 0.04),
        )
    )
    body_center_z = web_z_top - 0.08 - PITMAN_BODY_HEIGHT / 2.0
    geo.merge(
        _box_at((PITMAN_BODY_THICK, PITMAN_BODY_WIDTH, PITMAN_BODY_HEIGHT), (PITMAN_BODY_X, 0.0, body_center_z))
    )
    seat_z = body_center_z - PITMAN_BODY_HEIGHT / 2.0 + 0.06
    front_block_x = PITMAN_BODY_X - PITMAN_BODY_THICK / 2.0 - 0.03
    geo.merge(_box_at((0.10, PITMAN_BODY_WIDTH + 0.04, 0.08), (front_block_x, 0.0, seat_z)))
    rear_block_x = PITMAN_BODY_X + PITMAN_BODY_THICK / 2.0 + 0.03
    geo.merge(_box_at((0.10, PITMAN_BODY_WIDTH + 0.04, 0.08), (rear_block_x, 0.0, seat_z)))
    return geo


def _toggle_bar_mesh(length: float, sign: float) -> MeshGeometry:
    geo = MeshGeometry()
    geo.merge(_box_at((abs(length), 0.48, 0.050), (sign * length / 2.0, 0.0, 0.0)))
    for xr in (0.0, sign * length):
        rocker = CylinderGeometry(TOGGLE_ROCKER_R, 0.50, radial_segments=20)
        rocker.rotate_x(math.pi / 2.0)
        rocker.translate(xr, 0.0, 0.0)
        geo.merge(rocker)
    return geo


# --------------------------------------------------------------------------- #
# Slot A -- frame (root)
# --------------------------------------------------------------------------- #


def _frame_downstream() -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="frame",
        visual_name="base_rails",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, 0.12),
        face_extents_uv=(2.10, 1.27),
        contact_tol=0.004,
    )


def _build_frame(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialOreCrusherJawConfig = ctx.config  # type: ignore[assignment]
    frame = model.part("frame")

    frame.visual(mesh_from_geometry(_base_rails_mesh(), "base_rails"), material="frame_gray", name="base_rails", material_class_id="metal.paint_coated")

    # multiplicity axis: evenly spaced base cross members between the rails.
    n = r.cross_member_count
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0.5
        xc = -0.88 + t * (0.88 - (-0.88))
        frame.visual(
            mesh_from_geometry(_single_cross_member_mesh(xc), f"cross_member_{i}"),
            material="frame_gray",
            name=f"cross_member_{i}", material_class_id="metal.paint_coated",
        )

    # frame form (Slot A form family)
    if r.frame_form == "welded_plate_frame":
        frame.visual(
            mesh_from_geometry(_side_plate_mesh(-SIDE_PLATE_Y), "flywheel_side_plate"),
            material="frame_gray", name="flywheel_side_plate", material_class_id="metal.paint_coated",
        )
        frame.visual(
            mesh_from_geometry(_side_plate_mesh(SIDE_PLATE_Y), "drive_side_plate"),
            material="frame_gray", name="drive_side_plate", material_class_id="metal.paint_coated",
        )
        frame.visual(mesh_from_geometry(_front_wall_mesh(), "front_wall"), material="frame_gray", name="front_wall", material_class_id="metal.paint_coated")
        frame.visual(mesh_from_geometry(_rear_wall_mesh(), "rear_wall"), material="frame_gray", name="rear_wall", material_class_id="metal.paint_coated")
    else:  # cast_monobloc_frame
        frame.visual(
            mesh_from_geometry(_cast_housing_mesh(), "cast_housing"),
            material="frame_gray", name="cast_housing", material_class_id="metal.cast_iron_bare",
        )

    frame.visual(
        mesh_from_geometry(_toggle_seat_mesh(0.89, 0.59, 0.4575), "toggle_seat"),
        material="frame_gray", name="toggle_seat", material_class_id="metal.paint_coated",
    )
    frame.visual(mesh_from_geometry(_rod_bracket_mesh(), "rod_bracket"), material="frame_gray", name="rod_bracket", material_class_id="metal.paint_coated")
    frame.visual(
        mesh_from_geometry(_bearing_housings_mesh(), "bearing_housings"),
        material="steel_light", name="bearing_housings", material_class_id="metal.cast_iron_bare",
    )
    frame.visual(
        mesh_from_geometry(_motor_pedestal_mesh(), "motor_pedestal"),
        material="frame_gray", name="motor_pedestal", material_class_id="metal.paint_coated",
    )
    frame.visual(mesh_from_geometry(_motor_mesh(), "motor_assembly"), material="motor_gray", name="motor_assembly", material_class_id="metal.paint_coated")

    parts = ["frame"]
    joints: list[str] = []
    # Fixed jaw plate: welded (frame visual, Rule 1) or adjustable (PRISMATIC part).
    if r.fixed_jaw_mode == "welded":
        frame.visual(
            mesh_from_geometry(_fixed_jaw_plate_mesh(r.jaw_rib_count, r.fixed_plate_standoff), "fixed_plate_welded"),
            material="jaw_orange", name="fixed_plate_welded", material_class_id="metal.steel_bare",
        )
    else:
        frame.visual(
            mesh_from_geometry(_adjustment_wedge_mesh(), "adjustment_wedge"),
            material="steel_light", name="adjustment_wedge", material_class_id="metal.steel_bare",
        )
        fixed_plate = model.part("fixed_jaw_plate")
        fixed_plate.visual(
            mesh_from_geometry(_fixed_jaw_plate_mesh(r.jaw_rib_count, r.fixed_plate_standoff), "fixed_plate_corrugated"),
            material="jaw_orange", name="fixed_plate_corrugated", material_class_id="metal.steel_bare",
        )
        adjust_axis = (math.cos(FIXED_PLATE_ANGLE), 0.0, math.sin(FIXED_PLATE_ANGLE))
        model.articulation(
            "frame_to_fixed_jaw_plate",
            ArticulationType.PRISMATIC,
            parent=frame, child=fixed_plate,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=adjust_axis,
            motion_limits=MotionLimits(effort=50000.0, velocity=0.005, lower=0.0, upper=r.fixed_plate_travel),
        )
        parts.append("fixed_jaw_plate")
        joints.append("frame_to_fixed_jaw_plate")

    return ModuleBuild(
        module_name=r.frame_form,
        parts_emitted=parts,
        internal_articulations=joints,
        interfaces={"downstream": _frame_downstream()},
    )


# --------------------------------------------------------------------------- #
# Slot B -- drive (parallel child on frame)
# --------------------------------------------------------------------------- #


def _build_drive(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialOreCrusherJawConfig = ctx.config  # type: ignore[assignment]
    frame = model.get_part("frame")

    shaft = model.part("eccentric_shaft")
    shaft.visual(mesh_from_geometry(_eccentric_shaft_mesh(), "shaft"), material="shaft_steel", name="shaft", material_class_id="metal.steel_bare")
    shaft.visual(mesh_from_geometry(_eccentric_boss_mesh(), "eccentric_boss"), material="shaft_steel", name="eccentric_boss", material_class_id="metal.steel_bare")
    if r.flywheel_form == "spoked_flywheel":
        fly = _flywheel_spoked_mesh(r.flywheel_spoke_count, r.flywheel_scale)
    else:
        fly = _flywheel_disc_mesh(r.flywheel_scale)
    shaft.visual(mesh_from_geometry(fly, "flywheel"), material="wheel_gray", name="flywheel", material_class_id="metal.cast_iron_bare")
    shaft.visual(mesh_from_geometry(_drive_pulley_mesh(), "drive_pulley"), material="wheel_gray", name="drive_pulley", material_class_id="metal.cast_iron_bare")
    model.articulation(
        "frame_to_eccentric_shaft",
        ArticulationType.CONTINUOUS,
        parent=frame, child=shaft,
        origin=Origin(xyz=(SHAFT_X, 0.0, SHAFT_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=30000.0, velocity=35.0),
    )

    motor_pulley = model.part("motor_pulley")
    motor_pulley.visual(mesh_from_geometry(_motor_pulley_mesh(), "pulley_body"), material="wheel_gray", name="pulley_body", material_class_id="metal.cast_iron_bare")
    model.articulation(
        "frame_to_motor_pulley",
        ArticulationType.CONTINUOUS,
        parent=frame, child=motor_pulley,
        origin=Origin(xyz=MOTOR_PULLEY_POS),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4000.0, velocity=120.0),
        mimic=Mimic(joint="frame_to_eccentric_shaft", multiplier=BELT_RATIO),
    )

    return ModuleBuild(
        module_name=r.flywheel_form,
        parts_emitted=["eccentric_shaft", "motor_pulley"],
        internal_articulations=["frame_to_eccentric_shaft", "frame_to_motor_pulley"],
        interfaces={"downstream": _frame_downstream()},
    )


# --------------------------------------------------------------------------- #
# Slot C -- crush mechanism (parallel child on frame)
# --------------------------------------------------------------------------- #


def _build_single_toggle(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialOreCrusherJawConfig = ctx.config  # type: ignore[assignment]
    frame = model.get_part("frame")

    swing = model.part("swing_jaw")
    swing.visual(mesh_from_geometry(_single_pitman_body_mesh(), "pitman_body"), material="frame_gray", name="pitman_body", material_class_id="metal.paint_coated")
    swing.visual(mesh_from_geometry(_pitman_hub_mesh(), "pitman_hub"), material="steel_light", name="pitman_hub", material_class_id="metal.steel_bare")
    swing.visual(
        mesh_from_geometry(_single_movable_plate_mesh(r.jaw_rib_count), "movable_plate_corrugated"),
        material="jaw_orange", name="movable_plate_corrugated", material_class_id="metal.steel_bare",
    )
    swing.visual(
        mesh_from_geometry(_single_tension_rod_mesh((0.14, -1.24)), "tension_rod_spring"),
        material="toggle_steel", name="tension_rod_spring", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "frame_to_swing_jaw",
        ArticulationType.REVOLUTE,
        parent=frame, child=swing,
        origin=Origin(xyz=(SHAFT_X, 0.0, SHAFT_Z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=60000.0, velocity=2.0, lower=0.0, upper=r.jaw_stroke),
    )

    toggle = model.part("toggle_plate")
    toggle.visual(mesh_from_geometry(_toggle_plate_mesh(), "toggle_body"), material="toggle_steel", name="toggle_body", material_class_id="metal.steel_bare")
    model.articulation(
        "swing_jaw_to_toggle_plate",
        ArticulationType.REVOLUTE,
        parent=swing, child=toggle,
        origin=Origin(xyz=(TOGGLE_SEAT_LOCAL[0], 0.0, TOGGLE_SEAT_LOCAL[1])),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=8000.0, velocity=2.0, lower=-0.06, upper=0.06),
        mimic=Mimic(joint="frame_to_swing_jaw", multiplier=-1.0),
    )

    return ModuleBuild(
        module_name="single_toggle",
        parts_emitted=["swing_jaw", "toggle_plate"],
        internal_articulations=["frame_to_swing_jaw", "swing_jaw_to_toggle_plate"],
        interfaces={"downstream": _frame_downstream()},
    )


def _build_hydraulic_toggle(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialOreCrusherJawConfig = ctx.config  # type: ignore[assignment]
    frame = model.get_part("frame")

    swing = model.part("swing_jaw")
    swing.visual(mesh_from_geometry(_single_pitman_body_mesh(), "pitman_body"), material="frame_gray", name="pitman_body", material_class_id="metal.paint_coated")
    swing.visual(mesh_from_geometry(_pitman_hub_mesh(), "pitman_hub"), material="steel_light", name="pitman_hub", material_class_id="metal.steel_bare")
    swing.visual(
        mesh_from_geometry(_single_movable_plate_mesh(r.jaw_rib_count), "movable_plate_corrugated"),
        material="jaw_orange", name="movable_plate_corrugated", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "frame_to_swing_jaw",
        ArticulationType.REVOLUTE,
        parent=frame, child=swing,
        origin=Origin(xyz=(SHAFT_X, 0.0, SHAFT_Z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=60000.0, velocity=2.0, lower=0.0, upper=r.jaw_stroke),
    )

    # PRISMATIC hydraulic tramp-relief cylinder (independent DOF, small stroke;
    # a prismatic cannot mimic a revolute source). Type PRISMATIC gives joint-type coverage.
    cyl = model.part("hydraulic_cylinder")
    cyl.visual(mesh_from_geometry(_hydraulic_cylinder_mesh(), "hydraulic_cylinder"), material="hydraulic_body", name="hydraulic_cylinder", material_class_id="metal.blackened_gunmetal")
    model.articulation(
        "swing_jaw_to_hydraulic_cylinder",
        ArticulationType.PRISMATIC,
        parent=swing, child=cyl,
        origin=Origin(xyz=(TOGGLE_SEAT_LOCAL[0], 0.0, TOGGLE_SEAT_LOCAL[1])),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=200000.0, velocity=0.10, lower=0.0, upper=0.02),
    )

    return ModuleBuild(
        module_name="hydraulic_toggle",
        parts_emitted=["swing_jaw", "hydraulic_cylinder"],
        internal_articulations=["frame_to_swing_jaw", "swing_jaw_to_hydraulic_cylinder"],
        interfaces={"downstream": _frame_downstream()},
    )


def _build_dodge_pivot(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialOreCrusherJawConfig = ctx.config  # type: ignore[assignment]
    frame = model.get_part("frame")
    # bottom pivot mount hardware appended to the frame (keeps frame form orthogonal)
    frame.visual(mesh_from_geometry(_jaw_pivot_mount_mesh(), "jaw_pivot_mount"), material="frame_gray", name="jaw_pivot_mount", material_class_id="metal.paint_coated")

    swing = model.part("swing_jaw")
    swing.visual(mesh_from_geometry(_dodge_pitman_body_mesh(), "pitman_body"), material="frame_gray", name="pitman_body", material_class_id="metal.paint_coated")
    swing.visual(mesh_from_geometry(_dodge_hub_mesh(), "pitman_hub"), material="steel_light", name="pitman_hub", material_class_id="metal.steel_bare")
    swing.visual(
        mesh_from_geometry(_dodge_movable_plate_mesh(r.jaw_rib_count), "movable_plate_corrugated"),
        material="jaw_orange", name="movable_plate_corrugated", material_class_id="metal.steel_bare",
    )
    swing.visual(
        mesh_from_geometry(_single_tension_rod_mesh((0.26, 0.35)), "tension_rod_spring"),
        material="toggle_steel", name="tension_rod_spring", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "frame_to_swing_jaw",
        ArticulationType.REVOLUTE,
        parent=frame, child=swing,
        origin=Origin(xyz=(BOTTOM_PIVOT_X, 0.0, BOTTOM_PIVOT_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=60000.0, velocity=2.0, lower=0.0, upper=r.jaw_stroke),
    )

    toggle = model.part("toggle_plate")
    toggle.visual(mesh_from_geometry(_toggle_plate_mesh(), "toggle_body"), material="toggle_steel", name="toggle_body", material_class_id="metal.steel_bare")
    model.articulation(
        "swing_jaw_to_toggle_plate",
        ArticulationType.REVOLUTE,
        parent=swing, child=toggle,
        origin=Origin(xyz=(DODGE_TOGGLE_SEAT[0], 0.0, DODGE_TOGGLE_SEAT[1])),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=8000.0, velocity=2.0, lower=-0.06, upper=0.06),
        mimic=Mimic(joint="frame_to_swing_jaw", multiplier=-1.0),
    )

    return ModuleBuild(
        module_name="dodge_pivot",
        parts_emitted=["swing_jaw", "toggle_plate"],
        internal_articulations=["frame_to_swing_jaw", "swing_jaw_to_toggle_plate"],
        interfaces={"downstream": _frame_downstream()},
    )


def _build_double_toggle(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialOreCrusherJawConfig = ctx.config  # type: ignore[assignment]
    frame = model.get_part("frame")
    frame.visual(mesh_from_geometry(_pivot_bosses_mesh(), "pivot_bosses"), material="steel_light", name="pivot_bosses", material_class_id="metal.steel_bare")

    # swing jaw hung from the top pivot
    swing = model.part("swing_jaw")
    swing.visual(mesh_from_geometry(_double_swing_jaw_body_mesh(), "swing_jaw_body"), material="frame_gray", name="swing_jaw_body", material_class_id="metal.paint_coated")
    swing.visual(
        mesh_from_geometry(_double_movable_plate_mesh(r.jaw_rib_count), "movable_plate_corrugated"),
        material="jaw_orange", name="movable_plate_corrugated", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "frame_to_swing_jaw",
        ArticulationType.REVOLUTE,
        parent=frame, child=swing,
        origin=Origin(xyz=(PIVOT_X, 0.0, PIVOT_Z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=60000.0, velocity=2.0, lower=0.0, upper=r.jaw_stroke),
    )

    # pitman member riding the eccentric boss; driven as a REVOLUTE mimic about
    # the shaft axis (decoupled from the CONTINUOUS flywheel spin, so it never
    # sweeps a full circle -- see spec Reject cases).
    pitman = model.part("pitman")
    pitman.visual(mesh_from_geometry(_pitman_member_mesh(), "pitman_member"), material="frame_gray", name="pitman_member", material_class_id="metal.paint_coated")
    model.articulation(
        "frame_to_pitman",
        ArticulationType.REVOLUTE,
        parent=frame, child=pitman,
        origin=Origin(xyz=(SHAFT_X, 0.0, SHAFT_Z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=40000.0, velocity=2.0, lower=-0.06, upper=0.06),
        mimic=Mimic(joint="frame_to_swing_jaw", multiplier=0.6),
    )

    front_toggle = model.part("front_toggle_plate")
    front_toggle.visual(mesh_from_geometry(_toggle_bar_mesh(FRONT_TOGGLE_LEN, 1.0), "front_toggle_body"), material="toggle_steel", name="front_toggle_body", material_class_id="metal.steel_bare")
    model.articulation(
        "swing_jaw_to_front_toggle",
        ArticulationType.REVOLUTE,
        parent=swing, child=front_toggle,
        origin=Origin(xyz=(JAW_TOGGLE_X, 0.0, JAW_TOGGLE_Z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=8000.0, velocity=2.0, lower=-0.06, upper=0.06),
        mimic=Mimic(joint="frame_to_swing_jaw", multiplier=-0.5),
    )

    rear_toggle = model.part("rear_toggle_plate")
    rear_toggle.visual(mesh_from_geometry(_toggle_bar_mesh(REAR_TOGGLE_LEN, -1.0), "rear_toggle_body"), material="toggle_steel", name="rear_toggle_body", material_class_id="metal.steel_bare")
    model.articulation(
        "frame_to_rear_toggle",
        ArticulationType.REVOLUTE,
        parent=frame, child=rear_toggle,
        origin=Origin(xyz=FRAME_TOGGLE_SEAT),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=8000.0, velocity=2.0, lower=-0.06, upper=0.06),
        mimic=Mimic(joint="frame_to_swing_jaw", multiplier=0.5),
    )

    return ModuleBuild(
        module_name="double_toggle",
        parts_emitted=["swing_jaw", "pitman", "front_toggle_plate", "rear_toggle_plate"],
        internal_articulations=[
            "frame_to_swing_jaw",
            "frame_to_pitman",
            "swing_jaw_to_front_toggle",
            "frame_to_rear_toggle",
        ],
        interfaces={"downstream": _frame_downstream()},
    )


# --------------------------------------------------------------------------- #
# Factory registries + assembly
# --------------------------------------------------------------------------- #

FRAME_FACTORIES = {
    "welded_plate_frame": _build_frame,
    "cast_monobloc_frame": _build_frame,
}
DRIVE_FACTORIES = {
    "spoked_flywheel": _build_drive,
    "solid_disc_flywheel": _build_drive,
}
CRUSH_FACTORIES = {
    "single_toggle": _build_single_toggle,
    "dodge_pivot": _build_dodge_pivot,
    "double_toggle": _build_double_toggle,
    "hydraulic_toggle": _build_hydraulic_toggle,
}


def _slots_for_config(r: ResolvedIndustrialOreCrusherJawConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="frame", candidates={r.frame_form: FRAME_FACTORIES[r.frame_form]}, anchor_choice=r.frame_form),
        SlotSpec(slot_name="drive", candidates={r.flywheel_form: DRIVE_FACTORIES[r.flywheel_form]}, anchor_choice=r.flywheel_form),
        SlotSpec(slot_name="crush", candidates={r.crush_linkage: CRUSH_FACTORIES[r.crush_linkage]}, anchor_choice=r.crush_linkage),
    ]


def build_industrial_ore_crusher_jaw(
    config: IndustrialOreCrusherJawConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="industrial_ore_crusher_jaw", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    assemble(
        model,
        slots=_slots_for_config(r),
        rng=random.Random(0),
        palette=r.palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    return model


def build_seeded_industrial_ore_crusher_jaw(seed: int) -> ArticulatedObject:
    return build_industrial_ore_crusher_jaw(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    spoke_axis = f"spokes_{r.flywheel_spoke_count}" if r.flywheel_form == "spoked_flywheel" else "spokes_na"
    return [
        ("frame", r.frame_form),
        ("fixed_jaw_mode", r.fixed_jaw_mode),
        ("cross_member_count", f"cross_{r.cross_member_count}"),
        ("drive", r.flywheel_form),
        ("flywheel_spoke_count", spoke_axis),
        ("crush", r.crush_linkage),
        ("jaw_rib_count", f"ribs_{r.jaw_rib_count}"),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedIndustrialOreCrusherJawConfig) -> None:
    parts = {p.name for p in model.parts}

    def _has_vis(part_name: str, vis: str) -> bool:
        if part_name not in parts:
            return False
        return any(v.name == vis for v in model.get_part(part_name).visuals)

    def _ov(a: str, b: str, *, elem_a: str, elem_b: str, reason: str) -> None:
        if a in parts and b in parts and _has_vis(a, elem_a) and _has_vis(b, elem_b):
            ctx.allow_overlap(a, b, elem_a=elem_a, elem_b=elem_b, reason=reason)

    frame_wall = "cast_housing" if r.frame_form == "cast_monobloc_frame" else "front_wall"

    # eccentric shaft captured in the frame pillow-block bearings
    _ov("eccentric_shaft", "frame", elem_a="shaft", elem_b="bearing_housings",
        reason="Eccentric shaft is captured inside the frame pillow-block bearings.")
    if r.frame_form == "cast_monobloc_frame":
        _ov("eccentric_shaft", "frame", elem_a="shaft", elem_b="cast_housing",
            reason="Eccentric shaft passes through the cast housing side walls at the bearing bosses.")

    # motor pulley pressed on the motor shaft stub
    _ov("motor_pulley", "frame", elem_a="pulley_body", elem_b="motor_assembly",
        reason="Motor pulley is pressed onto the motor shaft stub; coaxial.")

    # pitman/swing-jaw hub + body captured around the eccentric boss / shaft
    for hub_part, hub_vis in (
        ("swing_jaw", "pitman_hub"),
        ("swing_jaw", "pitman_body"),
        ("pitman", "pitman_member"),
    ):
        _ov(hub_part, "eccentric_shaft", elem_a=hub_vis, elem_b="eccentric_boss",
            reason="Eccentric boss is captured inside the pitman bearing bore; both rotate about the shaft axis.")
        _ov(hub_part, "eccentric_shaft", elem_a=hub_vis, elem_b="shaft",
            reason="Eccentric shaft passes through the pitman bearing bore.")

    # single/dodge toggle plate captured in the pitman pocket + frame seat
    _ov("toggle_plate", "swing_jaw", elem_a="toggle_body", elem_b="pitman_body",
        reason="Toggle front rocker seats in the pitman toggle pocket (captured rocker end).")
    _ov("toggle_plate", "frame", elem_a="toggle_body", elem_b="toggle_seat",
        reason="Toggle rear rocker seats in the frame toggle seat pocket.")

    # hydraulic cylinder captured in the pitman pocket + frame seat
    _ov("hydraulic_cylinder", "swing_jaw", elem_a="hydraulic_cylinder", elem_b="pitman_body",
        reason="Hydraulic cylinder front eye seats in the pitman toggle pocket.")
    _ov("hydraulic_cylinder", "frame", elem_a="hydraulic_cylinder", elem_b="toggle_seat",
        reason="Hydraulic cylinder rear eye is captured in the frame toggle seat.")

    # double-toggle front/rear toggle rockers captured in their seats
    _ov("front_toggle_plate", "swing_jaw", elem_a="front_toggle_body", elem_b="swing_jaw_body",
        reason="Front toggle near rocker seats in the swing-jaw toggle pocket.")
    _ov("front_toggle_plate", "pitman", elem_a="front_toggle_body", elem_b="pitman_member",
        reason="Front toggle far rocker seats in the pitman front seat block.")
    _ov("rear_toggle_plate", "pitman", elem_a="rear_toggle_body", elem_b="pitman_member",
        reason="Rear toggle near rocker seats in the pitman rear seat block.")
    _ov("rear_toggle_plate", "frame", elem_a="rear_toggle_body", elem_b="toggle_seat",
        reason="Rear toggle far rocker seats in the frame toggle seat.")
    _ov("pitman", "eccentric_shaft", elem_a="pitman_member", elem_b="shaft",
        reason="Eccentric shaft passes through the pitman body at the eccentric bearing.")
    # double-toggle crowded top-of-chamber bearing cluster: the eccentric boss,
    # the pitman bearing hub and the swing-jaw top pivot all share this region.
    _ov("swing_jaw", "eccentric_shaft", elem_a="swing_jaw_body", elem_b="eccentric_boss",
        reason="Swing-jaw top edge runs under the eccentric boss at the crowded pivot cluster.")
    _ov("swing_jaw", "eccentric_shaft", elem_a="swing_jaw_body", elem_b="shaft",
        reason="Eccentric shaft passes just above the swing-jaw top pivot.")
    _ov("pitman", "swing_jaw", elem_a="pitman_member", elem_b="swing_jaw_body",
        reason="Pitman bearing hub and the swing-jaw top pivot share the crowded bearing cluster.")
    _ov("front_toggle_plate", "rear_toggle_plate", elem_a="front_toggle_body", elem_b="rear_toggle_body",
        reason="Front and rear toggle rockers meet at the shared pitman seat blocks.")

    # dodge/double swing-jaw pivot boss captured in the frame pivot hardware
    _ov("swing_jaw", "frame", elem_a="pitman_body", elem_b="jaw_pivot_mount",
        reason="Dodge swing-jaw pivot boss sits in the frame bottom pivot mount.")
    _ov("swing_jaw", "frame", elem_a="swing_jaw_body", elem_b="pivot_bosses",
        reason="Double-toggle swing jaw hangs on the frame top pivot bosses.")

    # fixed-jaw setting ram: plate slides on the wedge carriage
    _ov("fixed_jaw_plate", "frame", elem_a="fixed_plate_corrugated", elem_b="adjustment_wedge",
        reason="Fixed jaw plate slides on the adjustment wedge carriage for wear/setting travel.")
    _ov("fixed_jaw_plate", "frame", elem_a="fixed_plate_corrugated", elem_b=frame_wall,
        reason="Fixed jaw plate seats against the tilted front wall (setting embed).")

    # cast monobloc housing is a closed cavity: the swing mechanism rides within
    # it (the welded flat-plate frame is open at the same locations). Mirrors the
    # cast_monobloc_frame source's declared allow_overlaps.
    if r.frame_form == "cast_monobloc_frame":
        for elem in (
            "pitman_body", "pitman_hub", "tension_rod_spring", "swing_jaw_body",
        ):
            _ov("swing_jaw", "frame", elem_a=elem, elem_b="cast_housing",
                reason="Swing jaw / pitman / tension rod sweeps within the cast housing cavity.")
        for child in ("toggle_plate", "pitman", "front_toggle_plate", "rear_toggle_plate"):
            body = {
                "toggle_plate": "toggle_body",
                "pitman": "pitman_member",
                "front_toggle_plate": "front_toggle_body",
                "rear_toggle_plate": "rear_toggle_body",
            }[child]
            _ov(child, "frame", elem_a=body, elem_b="cast_housing",
                reason="Back-linkage member rides within the cast housing cavity.")


def _swing_jaw_movable_elem() -> str:
    return "movable_plate_corrugated"


def _expect_mechanism(ctx: TestContext, model: ArticulatedObject, r: ResolvedIndustrialOreCrusherJawConfig) -> None:
    # drive: continuous eccentric shaft + belt mimic
    shaft_joint = model.get_articulation("frame_to_eccentric_shaft")
    ctx.check("eccentric shaft drive is continuous", shaft_joint.articulation_type == ArticulationType.CONTINUOUS)
    fly = model.get_part("eccentric_shaft").get_visual("flywheel")
    ctx.check("flywheel present on the eccentric shaft", fly is not None)

    # crush: revolute crushing stroke opens the discharge gap
    jaw_joint = model.get_articulation("frame_to_swing_jaw")
    ctx.check("crushing stroke is revolute", jaw_joint.articulation_type == ArticulationType.REVOLUTE)
    swing = model.get_part("swing_jaw")
    rest = ctx.part_element_world_aabb(swing, elem=_swing_jaw_movable_elem())
    with ctx.pose({jaw_joint: r.jaw_stroke}):
        opened = ctx.part_element_world_aabb(swing, elem=_swing_jaw_movable_elem())
    rest_cx = (rest[0][0] + rest[1][0]) / 2.0 if rest else None
    open_cx = (opened[0][0] + opened[1][0]) / 2.0 if opened else None
    ctx.check(
        "positive jaw stroke moves the movable plate (discharge opening)",
        rest_cx is not None and open_cx is not None and abs(open_cx - rest_cx) > 0.005,
        details=f"movable plate rest_cx={rest_cx}, open_cx={open_cx}",
    )

    # back-linkage type coverage per module
    if r.crush_linkage == "hydraulic_toggle":
        cj = model.get_articulation("swing_jaw_to_hydraulic_cylinder")
        ctx.check("hydraulic back link is prismatic", cj.articulation_type == ArticulationType.PRISMATIC)
    elif r.crush_linkage == "double_toggle":
        for jn in ("swing_jaw_to_front_toggle", "frame_to_rear_toggle"):
            j = model.get_articulation(jn)
            ctx.check(f"{jn} is revolute", j.articulation_type == ArticulationType.REVOLUTE)
        ctx.check("double-toggle adds a pitman member", "pitman" in {p.name for p in model.parts})
    else:
        tj = model.get_articulation("swing_jaw_to_toggle_plate")
        ctx.check("mechanical toggle plate is revolute", tj.articulation_type == ArticulationType.REVOLUTE)

    # fixed-jaw setting ram advances toward the chamber
    if r.fixed_jaw_mode == "adjustable":
        adj = model.get_articulation("frame_to_fixed_jaw_plate")
        ctx.check("fixed-jaw setting ram is prismatic", adj.articulation_type == ArticulationType.PRISMATIC)
        fp = model.get_part("fixed_jaw_plate")
        rest_p = ctx.part_element_world_aabb(fp, elem="fixed_plate_corrugated")
        if r.fixed_plate_travel > 0.001:
            with ctx.pose({adj: r.fixed_plate_travel}):
                adv_p = ctx.part_element_world_aabb(fp, elem="fixed_plate_corrugated")
            rcx = (rest_p[0][0] + rest_p[1][0]) / 2.0 if rest_p else None
            acx = (adv_p[0][0] + adv_p[1][0]) / 2.0 if adv_p else None
            ctx.check(
                "setting ram advances the fixed plate toward the chamber (+X)",
                rcx is not None and acx is not None and acx > rcx + 0.005,
                details=f"fixed plate rest_cx={rcx}, advanced_cx={acx}",
            )


def run_industrial_ore_crusher_jaw_tests(
    model: ArticulatedObject,
    config: IndustrialOreCrusherJawConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    _declare_overlaps(ctx, model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    _expect_mechanism(ctx, model, r)

    # Rule 5: dynamic collision across sampled joint poses (independent joints:
    # CONTINUOUS shaft, REVOLUTE crushing stroke, PRISMATIC setting ram).
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "IndustrialOreCrusherJawConfig",
    "ResolvedIndustrialOreCrusherJawConfig",
    "FrameForm",
    "FlywheelForm",
    "CrushLinkage",
    "FixedJawMode",
    "CrusherPalette",
    "build_industrial_ore_crusher_jaw",
    "build_seeded_industrial_ore_crusher_jaw",
    "config_from_seed",
    "resolve_config",
    "run_industrial_ore_crusher_jaw_tests",
    "slot_choices_for_seed",
]
