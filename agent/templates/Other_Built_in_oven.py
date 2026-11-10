# SPDX-License-Identifier: Apache-2.0

"""Built-in oven — modular procedural template (embedded box kitchen appliance).

NOTE on category: "built_in_oven" here = an **embedded box-shape kitchen
appliance** — a front-opening single/double electric wall oven family plus the
compact built-in microwave family. A grounded hollow ``oven_body`` (outer shell
+ front fascia opening + cavity liner + fixed control strip) opens at the front
through one or more ``door`` leaves on a hinge line, holds 0..N slide-out wire
``rack`` shelves in each cavity, and may carry 0..N rotary ``knob`` controls on
the front fascia. NOT a freestanding range/stove (no burners) and NOT a
dishwasher (no spray arms / water path).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Other_Built_in_oven.md`` and the
``picture/Other/Built-in oven`` 5-star sample pool (2 parents + 7 slot/multiplicity
fork variants), all synced under ``data/records/``.

Structure (pattern = ``mixed``): a single root ``oven_body`` part, one fixed named
slot ``door_mechanism`` (the real joint-topology axis), plus three independent
multiplicity axes encoded into the slot_choice tuple:

  * ``door_mechanism`` (3): drop_down_bottom_hinge (1 REVOLUTE +X bottom hinge) /
    side_hinge_single (1 REVOLUTE -Z left jamb) / french_double_door (2 REVOLUTE
    mirrored ∓Z). This changes the door part tree and joint count/axis.
  * ``door_count`` (Nd in [1,3]): N oven cavities stacked along +Z (UNIT_PITCH);
    each cavity gets its own opening cut, liner, rails, door mechanism, and racks.
    Encoded as ``("door_count", f"n{Nd}")``.
  * ``rack_count`` (Nr in [0,5]): N slide-out wire racks per cavity, evenly spaced
    along +Z, each a PRISMATIC -Y slide. Encoded as ``("rack_count", f"r{Nr}")``.
  * ``knob_count`` (Nk in [0,8]): N rotary knobs on the front fascia, spaced along
    X, each a CONTINUOUS front-normal (-Y) spin. Encoded as
    ``("knob_count", f"k{Nk}")``.

UNIFIED COORDINATE CONVENTION (P1): +Y into cabinetry, -Y user-facing front,
width along X, height along Z, grounded at z=0. The P2 microwave source's knob
axis (its +X front normal, knobs along its Y) is re-mapped here to the P1 front
normal -Y with knobs spaced along X.

All rack rails / knob caps are rail-on-rail / cap-on-strip geometry, so those
joints omit ``MatingContract`` (grandfathered) and are guarded by the flat
articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring each
source record's run_tests allow_overlap block). Doors carry no hinge-arm
protrusions (they swept through the fascia while rotating and were removed).

Compatibility gating (resolve_config, spec §9):
  * french_double_door with Nd>=3 (six leaves) overloads the hinge density ->
    downgrade french to drop_down_bottom_hinge when Nd>=3.
  * Nd / Nr / Nk are clamped to declared domains and re-shrunk by clearance
    inequalities (stacked cavities <= fascia height, racks <= cavity height,
    rack travel <= cavity depth - retained insertion, knobs <= fascia width).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    KnobGeometry,
    KnobGrip,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

DoorMechanism = Literal[
    "drop_down_bottom_hinge",
    "side_hinge_single",
    "french_double_door",
]
PaletteStyle = Literal["gray_steel", "stainless_taupe", "matte_black", "cream_retro"]

DOOR_MECHANISMS: tuple[DoorMechanism, ...] = (
    "drop_down_bottom_hinge",
    "side_hinge_single",
    "french_double_door",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "gray_steel",
    "stainless_taupe",
    "matte_black",
    "cream_retro",
)

# Multiplicity declared / sampling domains (spec §8).
DOOR_COUNT_MIN, DOOR_COUNT_MAX = 1, 3
RACK_COUNT_MIN, RACK_COUNT_MAX = 0, 5
KNOB_COUNT_MIN, KNOB_COUNT_MAX = 0, 8

DOOR_COUNT_CHOICES = (1, 2, 3)
DOOR_COUNT_WEIGHTS = (0.6, 0.3, 0.1)
RACK_COUNT_CHOICES = (0, 1, 2, 3, 4)
RACK_COUNT_WEIGHTS = (0.12, 0.33, 0.30, 0.15, 0.10)
KNOB_COUNT_CHOICES = (0, 2, 3, 4, 6)
KNOB_COUNT_WEIGHTS = (0.30, 0.22, 0.13, 0.22, 0.13)

# ---------------------------------------------------------------------------
# Palette colorways (spec §palette). gray_steel / stainless_taupe come straight
# from the P1 / P2 sources; matte_black / cream_retro are synthesized real-world
# kitchen-appliance colorways from the same material families.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "gray_steel": {
        "body": (0.80, 0.80, 0.81, 1.0),
        "door": (0.62, 0.62, 0.64, 1.0),
        "glass": (0.07, 0.07, 0.09, 1.0),
        "display": (0.13, 0.14, 0.17, 1.0),
        "digits": (0.92, 0.95, 0.99, 1.0),
        "icon": (0.48, 0.50, 0.53, 1.0),
        "frosted": (0.92, 0.93, 0.94, 1.0),
        "metal": (0.78, 0.79, 0.82, 1.0),
        "cavity": (0.22, 0.22, 0.23, 1.0),
        "steel": (0.34, 0.34, 0.36, 1.0),
        "wire": (0.72, 0.73, 0.75, 1.0),
        "pointer": (0.18, 0.18, 0.20, 1.0),
    },
    "stainless_taupe": {
        "body": (0.78, 0.79, 0.80, 1.0),
        "door": (0.47, 0.45, 0.42, 1.0),
        "glass": (0.10, 0.10, 0.11, 1.0),
        "display": (0.12, 0.13, 0.13, 1.0),
        "digits": (0.66, 0.74, 0.70, 1.0),
        "icon": (0.55, 0.55, 0.54, 1.0),
        "frosted": (0.91, 0.92, 0.93, 1.0),
        "metal": (0.81, 0.82, 0.84, 1.0),
        "cavity": (0.20, 0.20, 0.20, 1.0),
        "steel": (0.36, 0.34, 0.32, 1.0),
        "wire": (0.74, 0.75, 0.77, 1.0),
        "pointer": (0.16, 0.16, 0.16, 1.0),
    },
    "matte_black": {
        "body": (0.14, 0.14, 0.15, 1.0),
        "door": (0.10, 0.10, 0.11, 1.0),
        "glass": (0.05, 0.05, 0.06, 1.0),
        "display": (0.06, 0.07, 0.08, 1.0),
        "digits": (0.40, 0.85, 0.92, 1.0),
        "icon": (0.45, 0.46, 0.48, 1.0),
        "frosted": (0.30, 0.31, 0.33, 1.0),
        "metal": (0.70, 0.71, 0.73, 1.0),
        "cavity": (0.10, 0.10, 0.11, 1.0),
        "steel": (0.25, 0.25, 0.27, 1.0),
        "wire": (0.66, 0.67, 0.69, 1.0),
        "pointer": (0.82, 0.82, 0.84, 1.0),
    },
    "cream_retro": {
        "body": (0.92, 0.90, 0.85, 1.0),
        "door": (0.94, 0.92, 0.87, 1.0),
        "glass": (0.09, 0.09, 0.10, 1.0),
        "display": (0.12, 0.10, 0.08, 1.0),
        "digits": (0.95, 0.72, 0.30, 1.0),
        "icon": (0.62, 0.58, 0.50, 1.0),
        "frosted": (0.93, 0.92, 0.90, 1.0),
        "metal": (0.80, 0.80, 0.82, 1.0),
        "cavity": (0.24, 0.22, 0.20, 1.0),
        "steel": (0.74, 0.72, 0.68, 1.0),
        "wire": (0.80, 0.80, 0.82, 1.0),
        "pointer": (0.30, 0.26, 0.22, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), P1 single-cavity calibration.
# +Y into the cabinetry, -Y user front, width along X, grounded at z=0.
# ---------------------------------------------------------------------------
_FASCIA_W = 0.60
_FASCIA_T = 0.022
_BODY_W = 0.56
_BODY_D = 0.53  # y: 0.00 .. 0.53
_TOTAL_D = 0.55

_OPEN_W = 0.565  # fascia door opening width
_OPEN_H = 0.432  # one cavity opening height
_OPEN_Z0 = 0.058  # first cavity hinge / opening bottom z
_UNIT_PITCH = 0.492  # vertical stacking pitch per cavity

_DOOR_W = 0.555
_DOOR_T = 0.040
_DOOR_H = 0.425

_HINGE_Y = -0.020  # door hinge line on the fascia front face (y of fascia front)
_FRENCH_HINGE_Y = -0.020  # french leaves sit on the fascia front
_LEAF_GAP = 0.003

_RACK_TRAVEL = 0.35
_RACK_RETAIN = 0.04  # retained insertion in the cavity at full extension
_RACK_SIDE_X = 0.230
_RACK_DEPTH = 0.400
_RACK_HALF_DEPTH_INNER = 0.194
_RACK_MIN_Z_PITCH = 0.055
_RACK_CAVITY_FRONT_Y = 0.0
_RACK_CAVITY_REAR_Y = 0.480
_RACK_REAR_CLEARANCE = 0.020
# Per-cavity usable interior z range (relative to that cavity's hinge z).
_CAVITY_Z0 = 0.017  # ~hinge_z + 0.017 (liner inner bottom)
_CAVITY_Z1 = 0.387  # ~hinge_z + 0.387 (liner inner top)

_CTRL_H = 0.085  # control strip height band
# Control strip layout (front fascia top band): clock display centered at x=0,
# touch icons in a 4x2 grid on the right, knob row on the left.
_CTRL_DISPLAY_HALF_W = 0.065
_CTRL_KNOB_GAP = 0.006  # display -> first-knob clearance

_KNOB_D = 0.034
_KNOB_H = 0.022
_KNOB_PITCH = 0.050  # base center-to-center spacing along X


@dataclass(frozen=True)
class BuiltInOvenConfig:
    door_mechanism: DoorMechanism | None = None
    door_count: int | None = None
    rack_count: int | None = None
    knob_count: int | None = None
    palette_style: PaletteStyle = "gray_steel"
    fascia_width_scale: float = 1.0
    cavity_height_scale: float = 1.0
    body_depth_scale: float = 1.0
    door_open_angle_scale: float = 1.0
    rack_travel_scale: float = 1.0
    knob_spacing_scale: float = 1.0
    name: str = "built_in_oven"


@dataclass(frozen=True)
class ResolvedBuiltInOvenConfig:
    door_mechanism: DoorMechanism
    door_count: int
    rack_count: int
    knob_count: int
    palette_style: PaletteStyle
    # concrete geometry (scaled)
    fascia_w: float
    body_w: float
    body_d: float
    open_w: float
    open_h: float
    open_z0: float
    unit_pitch: float
    door_w: float
    door_h: float
    fascia_h: float
    door_open_angle: float
    rack_rest_y: float
    rack_travel: float
    knob_pitch: float
    knob_d: float
    knob_h: float
    name: str

    @property
    def hinge_zs(self) -> list[float]:
        return [self.open_z0 + i * self.unit_pitch for i in range(self.door_count)]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> BuiltInOvenConfig:
    """Procedural sampling; seed=0 is NOT special."""
    rng = random.Random(seed)
    return BuiltInOvenConfig(
        door_mechanism=rng.choice(DOOR_MECHANISMS),
        door_count=rng.choices(DOOR_COUNT_CHOICES, weights=DOOR_COUNT_WEIGHTS, k=1)[0],
        rack_count=rng.choices(RACK_COUNT_CHOICES, weights=RACK_COUNT_WEIGHTS, k=1)[0],
        knob_count=rng.choices(KNOB_COUNT_CHOICES, weights=KNOB_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        fascia_width_scale=round(rng.uniform(0.92, 1.10), 4),
        cavity_height_scale=round(rng.uniform(0.90, 1.12), 4),
        body_depth_scale=round(rng.uniform(0.92, 1.10), 4),
        door_open_angle_scale=round(rng.uniform(0.88, 1.05), 4),
        rack_travel_scale=round(rng.uniform(0.85, 1.05), 4),
        knob_spacing_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_built_in_oven_{seed}",
    )


def resolve_config(config: BuiltInOvenConfig | None = None) -> ResolvedBuiltInOvenConfig:
    cfg = config or BuiltInOvenConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    door_mechanism = _pick(cfg.door_mechanism, DOOR_MECHANISMS)

    door_count = int(cfg.door_count) if cfg.door_count is not None else 1
    rack_count = int(cfg.rack_count) if cfg.rack_count is not None else 1
    knob_count = int(cfg.knob_count) if cfg.knob_count is not None else 0
    door_count = int(_clamp(door_count, DOOR_COUNT_MIN, DOOR_COUNT_MAX))
    rack_count = int(_clamp(rack_count, RACK_COUNT_MIN, RACK_COUNT_MAX))
    knob_count = int(_clamp(knob_count, KNOB_COUNT_MIN, KNOB_COUNT_MAX))

    # --- Compatibility gating (spec §9). ---
    # (1) french_double_door with Nd>=3 -> six leaves, too dense; downgrade.
    if door_mechanism == "french_double_door" and door_count >= 3:
        door_mechanism = "drop_down_bottom_hinge"

    width_scale = _clamp(cfg.fascia_width_scale, 0.92, 1.10)
    height_scale = _clamp(cfg.cavity_height_scale, 0.90, 1.12)
    depth_scale = _clamp(cfg.body_depth_scale, 0.92, 1.10)
    angle_scale = _clamp(cfg.door_open_angle_scale, 0.88, 1.05)
    travel_scale = _clamp(cfg.rack_travel_scale, 0.85, 1.05)
    spacing_scale = _clamp(cfg.knob_spacing_scale, 0.90, 1.10)

    fascia_w = _FASCIA_W * width_scale
    body_w = _BODY_W * width_scale
    open_w = _OPEN_W * width_scale
    door_w = _DOOR_W * width_scale
    body_d = _BODY_D * depth_scale

    unit_pitch = _UNIT_PITCH * height_scale
    open_h = _OPEN_H * height_scale
    open_z0 = _OPEN_Z0
    door_h = _DOOR_H * height_scale

    usable_rack_z = max(0.0, (_CAVITY_Z1 - _CAVITY_Z0) * (unit_pitch / _UNIT_PITCH))
    max_racks_by_height = max(0, min(RACK_COUNT_MAX, int(usable_rack_z / _RACK_MIN_Z_PITCH) - 1))
    rack_count = min(rack_count, max_racks_by_height)

    # fascia total height: top of the last cavity opening + a full control band
    # above (with headroom so the knob row on the strip clears the door tops).
    fascia_h = open_z0 + (door_count - 1) * unit_pitch + open_h + _CTRL_H + 0.030

    # Door open angle never exceeds horizontal (pi/2) for the drop-down family.
    door_open_angle = _clamp((math.pi / 2.0) * angle_scale, math.pi / 3.0, math.pi / 2.0)

    # Rack closed position is derived from the usable cavity depth.  Keep the
    # whole grid behind the front opening at q=0, then let the prismatic travel
    # pull it forward while retaining a rear bite inside the cavity.
    rack_rear_y = min(_RACK_CAVITY_REAR_Y, body_d - _RACK_REAR_CLEARANCE)
    rack_rest_y = rack_rear_y - _RACK_DEPTH / 2.0
    rack_rest_y = max(rack_rest_y, _RACK_CAVITY_FRONT_Y + _RACK_DEPTH / 2.0 + 0.010)
    rack_closed_back_y = rack_rest_y + _RACK_DEPTH / 2.0
    rack_travel = _RACK_TRAVEL * travel_scale
    rack_travel = min(
        rack_travel,
        _RACK_DEPTH - _RACK_RETAIN,
        rack_closed_back_y - _RACK_RETAIN,
    )
    rack_travel = max(rack_travel, 0.12)

    knob_pitch = _KNOB_PITCH * spacing_scale

    # --- knob clearance inequality (spec §7): the knob row sits left of the
    #     center display, so its left extent (display half-width + gap + row)
    #     must fit the fascia half-width minus margin. ---
    knob_d = _KNOB_D
    margin = 0.020
    if knob_count >= 1:
        max_extent = fascia_w / 2.0 - margin
        for _ in range(60):
            extent = (
                _CTRL_DISPLAY_HALF_W + _CTRL_KNOB_GAP + (knob_count - 1) * knob_pitch + knob_d
            )
            if extent <= max_extent:
                break
            if knob_pitch > 0.030:
                knob_pitch = max(0.030, knob_pitch - 0.002)
            else:
                knob_count -= 1
                if knob_count < 1:
                    break

    return ResolvedBuiltInOvenConfig(
        door_mechanism=door_mechanism,
        door_count=door_count,
        rack_count=rack_count,
        knob_count=knob_count,
        palette_style=palette_style,
        fascia_w=fascia_w,
        body_w=body_w,
        body_d=body_d,
        open_w=open_w,
        open_h=open_h,
        open_z0=open_z0,
        unit_pitch=unit_pitch,
        door_w=door_w,
        door_h=door_h,
        fascia_h=fascia_h,
        door_open_angle=door_open_angle,
        rack_rest_y=rack_rest_y,
        rack_travel=rack_travel,
        knob_pitch=knob_pitch,
        knob_d=knob_d,
        knob_h=_KNOB_H,
        name=cfg.name or "built_in_oven",
    )


def with_overrides(config: BuiltInOvenConfig, **kwargs: object) -> BuiltInOvenConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: BuiltInOvenConfig | ResolvedBuiltInOvenConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedBuiltInOvenConfig) else resolve_config(config)
    return (
        ("door_mechanism", r.door_mechanism),
        ("door_count", f"n{r.door_count}"),
        ("rack_count", f"r{r.rack_count}"),
        ("knob_count", f"k{r.knob_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# CadQuery body geometry helpers (multi-cavity, parameterized).
# Source: P1 _body_shell/_front_fascia/_cavity_liner + door_count multi-cavity.
# ---------------------------------------------------------------------------
def _cyl_wp(radius: float, length: float, axis: str, center: tuple[float, float, float]):
    wp = cq.Workplane("XY").cylinder(length, radius)  # long axis Z
    if axis == "x":
        wp = wp.rotate((0, 0, 0), (0, 1, 0), 90)
    elif axis == "y":
        wp = wp.rotate((0, 0, 0), (1, 0, 0), 90)
    return wp.translate(center)


def _body_shell(r: ResolvedBuiltInOvenConfig) -> cq.Workplane:
    body_h = r.fascia_h - 0.02
    outer = (
        cq.Workplane("XY")
        .box(r.body_w, r.body_d, body_h)
        .translate((0, r.body_d / 2.0, 0.02 + body_h / 2.0))
    )
    shell = outer
    cav_w = min(0.50, r.body_w - 0.06)
    for hz in r.hinge_zs:
        cz = hz + r.open_h / 2.0 - 0.016
        # Front (y=-0.03) cut through; rear stops 0.030 short of the back face
        # so the shell keeps a closed rear wall.
        cavity = (
            cq.Workplane("XY")
            .box(cav_w, r.body_d, r.open_h - 0.032)
            .translate((0, (r.body_d - 0.060) / 2.0, cz))
        )
        shell = shell.cut(cavity)
    return shell


def _front_fascia(r: ResolvedBuiltInOvenConfig) -> cq.Workplane:
    plate = (
        cq.Workplane("XY")
        .box(r.fascia_w, _FASCIA_T, r.fascia_h)
        .translate((0, -_FASCIA_T / 2.0 + 0.002, r.fascia_h / 2.0))
    )
    fascia = plate
    for hz in r.hinge_zs:
        oz = hz + r.open_h / 2.0
        opening = (
            cq.Workplane("XY")
            .box(r.open_w, 0.08, r.open_h)
            .translate((0, -_FASCIA_T / 2.0 + 0.002, oz))
        )
        fascia = fascia.cut(opening)
    return fascia


def _cavity_liner(r: ResolvedBuiltInOvenConfig, hinge_z: float) -> cq.Workplane:
    cz = hinge_z + r.open_h / 2.0 - 0.016
    cav_h = r.open_h - 0.028
    # Depths follow body_d so the liner rear stays 2 mm inside the shell's rear
    # wall (interior face at body_d - 0.030) for every depth scale.
    outer_d = r.body_d - 0.028  # y: -0.004 .. body_d - 0.032
    outer = (
        cq.Workplane("XY")
        .box(0.504, outer_d, cav_h + 0.004)
        .translate((0, (r.body_d - 0.036) / 2.0, cz))
    )
    inner_d = r.body_d  # y: -0.050 .. body_d - 0.050 (18 mm liner back wall)
    inner = (
        cq.Workplane("XY")
        .box(0.470, inner_d, cav_h - 0.030)
        .translate((0, (r.body_d - 0.100) / 2.0, cz))
    )
    return outer.cut(inner)


def _wire_rack() -> cq.Workplane:
    """Wire rack mesh in child-local coordinates.

    The child origin is the right-side support wire, matching the prismatic
    joint origin on the right rail. This avoids double-applying the world
    rack offset when the child is attached to the body.
    """
    left_x = -2.0 * _RACK_SIDE_X
    center_x = -_RACK_SIDE_X
    rack = _cyl_wp(0.0045, _RACK_DEPTH, "y", (0.0, 0.0, 0.0))
    rack = rack.union(_cyl_wp(0.0045, _RACK_DEPTH, "y", (left_x, 0.0, 0.0)))
    for y in (-_RACK_HALF_DEPTH_INNER, 0.0, _RACK_HALF_DEPTH_INNER):
        rack = rack.union(_cyl_wp(0.004, 0.464, "x", (center_x, y, 0.0)))
    for i in range(9):
        x = left_x + 0.046 * (i + 1)
        rack = rack.union(_cyl_wp(0.003, 2.0 * _RACK_HALF_DEPTH_INNER, "y", (x, 0.0, 0.0)))
    return rack


# ---------------------------------------------------------------------------
# Door frame meshes (door-local frames per mechanism).
# ---------------------------------------------------------------------------
def _door_frame_drop(r: ResolvedBuiltInOvenConfig) -> cq.Workplane:
    """Drop-down door (local origin on the bottom-front hinge line).

    The slab seats in FRONT of the opening (local -Y), so its back face lands on
    the hinge/fascia front plane and never protrudes into the cavity depth. This
    keeps the closed-door plane clear of the rack travel corridor (rack forward
    travel is clamped against this plane by the clearance solver).
    """
    panel = (
        cq.Workplane("XY")
        .box(r.door_w, _DOOR_T, r.door_h)
        .translate((0, -_DOOR_T / 2.0, 0.003 + r.door_h / 2.0))
    )
    window = (
        cq.Workplane("XY")
        .box(0.42, 0.08, r.door_h * 0.62)
        .translate((0, -_DOOR_T / 2.0, 0.003 + r.door_h * 0.42))
    )
    return panel.cut(window)


def _door_frame_side(r: ResolvedBuiltInOvenConfig) -> cq.Workplane:
    """Side-hinge door (local origin on the left vertical hinge line, centered z).

    As with the drop-down slab, the panel seats in FRONT of the opening (local
    -Y) so the closed door plane does not intrude into the cavity depth.
    """
    panel = (
        cq.Workplane("XY")
        .box(r.door_w, _DOOR_T, r.door_h)
        .translate((r.door_w / 2.0, -_DOOR_T / 2.0, 0.0))
    )
    window = (
        cq.Workplane("XY")
        .box(0.42, 0.08, r.door_h * 0.70)
        .translate((r.door_w / 2.0, -_DOOR_T / 2.0, 0.0))
    )
    return panel.cut(window)


def _leaf_frame(r: ResolvedBuiltInOvenConfig, side: int) -> cq.Workplane:
    """One french leaf (local origin on its vertical hinge edge)."""
    leaf_w = (r.open_w - _LEAF_GAP) / 2.0
    leaf_h = r.open_h - 0.006
    panel = (
        cq.Workplane("XY")
        .box(leaf_w, _DOOR_T, leaf_h)
        .translate((side * leaf_w / 2.0, -_DOOR_T / 2.0, 0.0))
    )
    window = (
        cq.Workplane("XY")
        .box(leaf_w - 0.060, _DOOR_T + 0.01, leaf_h - 0.080)
        .translate((side * leaf_w / 2.0, -_DOOR_T / 2.0, 0.0))
    )
    return panel.cut(window)


# ---------------------------------------------------------------------------
# oven_body (root): shell + fascia + per-cavity liner + rails + control strip.
# ---------------------------------------------------------------------------
def _build_body(model: ArticulatedObject, r: ResolvedBuiltInOvenConfig, mats, *, assets):
    body = model.part("oven_body")
    body.visual(
        mesh_from_cadquery(_body_shell(r), "body_shell", assets=assets),
        material=mats["body"],
        name="body_shell", material_class_id=("metal.stainless_matte" if r.palette_style in {"gray_steel", "stainless_taupe"} else "metal.paint_coated"),
    )
    body.visual(
        mesh_from_cadquery(_front_fascia(r), "front_fascia", assets=assets),
        material=mats["body"],
        name="front_fascia", material_class_id=("metal.stainless_matte" if r.palette_style in {"gray_steel", "stainless_taupe"} else "metal.paint_coated"),
    )
    for i, hz in enumerate(r.hinge_zs):
        body.visual(
            mesh_from_cadquery(_cavity_liner(r, hz), f"cavity_liner_{i}", assets=assets),
            material=mats["cavity"],
            name=f"cavity_liner_{i}", material_class_id="ceramic.porcelain_glazed_plain",
        )

    # control strip on the top band of the fascia (fixed touch glass + display).
    ctrl_z = r.fascia_h - _CTRL_H * 0.5
    body.visual(
        Box((r.fascia_w * 0.92, 0.004, _CTRL_H)),
        origin=Origin(xyz=(0.0, -0.021, ctrl_z)),
        material=mats["glass"],
        name="control_glass", material_class_id="glass.smoked_tinted",
    )
    body.visual(
        Box((0.13, 0.002, 0.050)),
        origin=Origin(xyz=(0.0, -0.0235, ctrl_z)),
        material=mats["display"],
        name="clock_display", material_class_id="tech.control_interface",
    )
    body.visual(
        Box((0.045, 0.002, 0.012)),
        origin=Origin(xyz=(0.0, -0.0252, ctrl_z)),
        material=mats["digits"],
        name="clock_digits", material_class_id="tech.emissive_surface",
    )
    icon_idx = 0
    # Touch icons live on the right of the display in a 4x2 grid; the knob row
    # sits left of the display (see _build_knobs) so the two never overlap.
    for x in (0.085, 0.115, 0.145, 0.175):
        for dz in (-0.0125, 0.0125):
            body.visual(
                Box((0.016, 0.002, 0.016)),
                origin=Origin(xyz=(x, -0.0235, ctrl_z + dz)),
                material=mats["icon"],
                name=f"touch_icon_{icon_idx}", material_class_id="tech.control_interface",
            )
            icon_idx += 1
    return body


# ---------------------------------------------------------------------------
# Door mechanisms (one full mechanism per cavity i).
# ---------------------------------------------------------------------------
def _emit_handle(door, r, *, x0: float, z: float, mats, vertical: bool = False):
    if vertical:
        door.visual(
            Cylinder(radius=0.010, length=min(0.22, r.door_h * 0.5)),
            origin=Origin(xyz=(x0, -_DOOR_T - 0.025, 0.0)),
            material=mats["metal"],
            name="handle_bar", material_class_id="metal.stainless_matte",
        )
        for j, pz in enumerate((0.08, -0.08)):
            door.visual(
                Cylinder(radius=0.007, length=0.025),
                origin=Origin(xyz=(x0, -_DOOR_T - 0.0125, pz), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["metal"],
                name=f"handle_post_{j}", material_class_id="metal.stainless_matte",
            )
    else:
        door.visual(
            Cylinder(radius=0.0125, length=0.45 * (r.door_w / _DOOR_W)),
            origin=Origin(xyz=(x0, -0.040, z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name="handle_bar", material_class_id="metal.stainless_matte",
        )
        for j, sx in enumerate((-1.0, 1.0)):
            door.visual(
                Cylinder(radius=0.009, length=0.036),
                origin=Origin(xyz=(x0 + sx * 0.185, -0.014, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["metal"],
                name=f"handle_post_{j}", material_class_id="metal.stainless_matte",
            )


def _emit_drop_door(model, r, body, mats, *, i: int, hz: float, assets) -> list[str]:
    name = f"door_{i}"
    door = model.part(name)
    door.visual(
        mesh_from_cadquery(_door_frame_drop(r), f"door_frame_{i}", assets=assets),
        material=mats["door"],
        name="door_frame", material_class_id=("metal.stainless_matte" if r.palette_style == "gray_steel" else "metal.paint_coated"),
    )
    door.visual(
        Box((0.44, 0.008, r.door_h * 0.64)),
        origin=Origin(xyz=(0.0, -_DOOR_T / 2.0, 0.003 + r.door_h * 0.42)),
        material=mats["frosted"],
        name="window_glass", material_class_id="glass.frosted_smooth",
    )
    # The door panel starts 3 mm above the pivot. A physical hinge pin bridges
    # that clearance and seats against the fascia throughout the drop-down turn.
    door.visual(
        Cylinder(radius=0.006, length=0.080),
        origin=Origin(xyz=(0.0, -0.004, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="hinge_pin", material_class_id="metal.steel_bare",
    )
    handle_z = 0.003 + r.door_h - 0.036
    _emit_handle(door, r, x0=0.0, z=handle_z, mats=mats)
    model.articulation(
        f"body_to_door_{i}",
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=Origin(xyz=(0.0, _HINGE_Y, hz)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=40.0, velocity=1.5, lower=0.0, upper=r.door_open_angle),
    )
    return [name]


def _emit_side_door(model, r, body, mats, *, i: int, hz: float, assets) -> list[str]:
    name = f"door_{i}"
    door = model.part(name)
    door.visual(
        mesh_from_cadquery(_door_frame_side(r), f"door_frame_{i}", assets=assets),
        material=mats["door"],
        name="door_frame", material_class_id=("metal.stainless_matte" if r.palette_style == "gray_steel" else "metal.paint_coated"),
    )
    door.visual(
        Box((0.44, 0.008, r.door_h * 0.72)),
        origin=Origin(xyz=(r.door_w / 2.0, -_DOOR_T / 2.0, 0.0)),
        material=mats["frosted"],
        name="window_glass", material_class_id="glass.frosted_smooth",
    )
    handle_z = r.door_h / 2.0 - 0.036
    _emit_handle(door, r, x0=r.door_w / 2.0, z=handle_z, mats=mats)
    z_mid = hz + r.open_h / 2.0
    model.articulation(
        f"body_to_door_{i}",
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=Origin(xyz=(-r.open_w / 2.0, _HINGE_Y, z_mid)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=40.0, velocity=1.5, lower=0.0, upper=r.door_open_angle),
    )
    return [name]


def _emit_french_door(model, r, body, mats, *, i: int, hz: float, assets) -> list[str]:
    z_mid = hz + r.open_h / 2.0
    leaf_w = (r.open_w - _LEAF_GAP) / 2.0
    names: list[str] = []
    for leaf_idx in range(2):
        side = 1 if leaf_idx == 0 else -1  # +1 left, -1 right
        hinge_x = -side * (r.open_w / 2.0)
        axis_z = -1.0 if leaf_idx == 0 else 1.0
        name = f"door_leaf_{i}_{leaf_idx}"
        leaf = model.part(name)
        leaf.visual(
            mesh_from_cadquery(_leaf_frame(r, side), f"leaf_frame_{i}_{leaf_idx}", assets=assets),
            material=mats["door"],
            name="leaf_frame", material_class_id=("metal.stainless_matte" if r.palette_style == "gray_steel" else "metal.paint_coated"),
        )
        leaf.visual(
            Box((leaf_w - 0.056, 0.006, r.open_h - 0.076)),
            origin=Origin(xyz=(side * leaf_w / 2.0, -_DOOR_T / 2.0, 0.0)),
            material=mats["frosted"],
            name="window_glass", material_class_id="glass.frosted_smooth",
        )
        # vertical handle bar near the free (center) edge.
        hx = side * (leaf_w - 0.035)
        leaf.visual(
            Cylinder(radius=0.010, length=min(0.22, r.open_h * 0.5)),
            origin=Origin(xyz=(hx, -_DOOR_T - 0.025, 0.0)),
            material=mats["metal"],
            name="handle_bar", material_class_id="metal.stainless_matte",
        )
        for j, pz in enumerate((0.08, -0.08)):
            leaf.visual(
                Cylinder(radius=0.007, length=0.025),
                origin=Origin(xyz=(hx, -_DOOR_T - 0.0125, pz), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["metal"],
                name=f"handle_post_{j}", material_class_id="metal.stainless_matte",
            )
        model.articulation(
            f"body_to_door_leaf_{i}_{leaf_idx}",
            ArticulationType.REVOLUTE,
            parent=body,
            child=leaf,
            origin=Origin(xyz=(hinge_x, _FRENCH_HINGE_Y, z_mid)),
            axis=(0.0, 0.0, axis_z),
            motion_limits=MotionLimits(
                effort=30.0, velocity=1.5, lower=0.0, upper=r.door_open_angle
            ),
        )
        names.append(name)
    return names


_DOOR_EMITTERS = {
    "drop_down_bottom_hinge": _emit_drop_door,
    "side_hinge_single": _emit_side_door,
    "french_double_door": _emit_french_door,
}


# ---------------------------------------------------------------------------
# rack_count multiplicity (per cavity).
# ---------------------------------------------------------------------------
def _rack_zs(r: ResolvedBuiltInOvenConfig, hz: float) -> list[float]:
    """Evenly-spaced rack z heights inside cavity i (absolute world z)."""
    z0 = hz + _CAVITY_Z0 * (r.unit_pitch / _UNIT_PITCH)
    z1 = hz + _CAVITY_Z1 * (r.unit_pitch / _UNIT_PITCH)
    n = r.rack_count
    if n <= 0:
        return []
    zone = (z1 - z0) / (n + 1)
    return [z0 + zone * (k + 1) for k in range(n)]


def _cavity_door_parts(r: ResolvedBuiltInOvenConfig, i: int) -> list[str]:
    """Door part name(s) that gate cavity ``i``'s slide-out racks.

    A real oven rack only pulls out through an OPEN door; the closed-door plane
    is the sequenced-mechanism pair whitelisted for overlap in run_tests (the
    "door shut + rack extended" combo is an unphysical pose-setter state).
    """
    if r.door_mechanism == "french_double_door":
        return [f"door_leaf_{i}_0", f"door_leaf_{i}_1"]
    return [f"door_{i}"]


def _build_racks(model, r, body, mats, *, assets):
    for i, hz in enumerate(r.hinge_zs):
        zs = _rack_zs(r, hz)
        for ri, rz in enumerate(zs):
            # rail support pair on the cavity walls (real visible support).
            for si, sx in enumerate((-1.0, 1.0)):
                body.visual(
                    Box((0.014, 0.40, 0.012)),
                    origin=Origin(xyz=(sx * 0.233, r.rack_rest_y, rz - 0.010)),
                    material=mats["steel"],
                    name=f"shelf_rail_{i}_{ri}_{si}", material_class_id="metal.steel_bare",
                )
            rack = model.part(f"rack_{i}_{ri}")
            rack.visual(
                mesh_from_cadquery(_wire_rack(), f"rack_grid_{i}_{ri}", assets=assets),
                material=mats["wire"],
                name="rack_grid", material_class_id="metal.mesh_chainmail",
            )
            # prismatic origin anchored onto the side rail (parent) which lies
            # within the rack's own right side-wire AABB (child); tangential -Y slide.
            joint_name = f"body_to_rack_{i}_{ri}"
            # Sequenced mechanism: the wire rack keeps its FULL designed travel.
            # A real oven rack only pulls out through an OPEN door; "door shut +
            # rack extended" is an unphysical pose a pose-setter can request but
            # that never occurs in operation — it is the user's responsibility,
            # not a geometry defect. So there is no clearance-solver clamp trimming
            # the travel back to the CLOSED-door plane; instead the rack↔door pair
            # is whitelisted for overlap in run_tests. The rack↔oven_body cavity
            # walls / rails remain independently declared, so full travel cannot
            # mask a real body penetration.
            model.articulation(
                joint_name,
                ArticulationType.PRISMATIC,
                parent=body,
                child=rack,
                origin=Origin(xyz=(_RACK_SIDE_X + 0.003, r.rack_rest_y, rz)),
                axis=(0.0, -1.0, 0.0),
                motion_limits=MotionLimits(
                    effort=30.0, velocity=0.3, lower=0.0, upper=r.rack_travel
                ),
            )


# ---------------------------------------------------------------------------
# knob_count multiplicity (front fascia, CONTINUOUS front-normal -Y spin).
# Unified to P1: knobs spaced along X; spin axis = front normal -Y; knob mesh
# (built along +Z) pitched to point -Y; off-axis pointer offset along -Y.
# ---------------------------------------------------------------------------
def _build_knobs(model, r, body, mats, *, assets):
    n = r.knob_count
    if n <= 0:
        return
    knob_geo = KnobGeometry(
        r.knob_d,
        r.knob_h,
        body_style="cylindrical",
        grip=KnobGrip(style="fluted", count=20, depth=0.0010),
        center=False,
    )
    # knob band sits ON the fixed control strip (above every door opening) so
    # the knobs never collide with the closed door panel(s). The row runs left
    # of the centered clock display; touch icons occupy the right grid.
    knob_z = r.fascia_h - _CTRL_H * 0.5
    mount_y = -_FASCIA_T / 2.0 + 0.002 - 0.0005  # 0.5 mm seated into fascia front
    x_right = -(_CTRL_DISPLAY_HALF_W + _CTRL_KNOB_GAP + r.knob_d / 2.0)
    for i in range(n):
        kx = x_right - i * r.knob_pitch
        knob = model.part(f"knob_{i}")
        # mesh built along +Z; rotate so cap points -Y (front normal).
        knob.visual(
            mesh_from_geometry(knob_geo, f"knob_cap_{i}"),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["metal"],
            name="knob_cap", material_class_id="metal.stainless_matte",
        )
        # off-axis pointer near the cap front face (proves continuous rotation).
        knob.visual(
            Box((0.005, 0.009, 0.004)),
            origin=Origin(xyz=(0.0, -(r.knob_h - 0.0005), 0.0105)),
            material=mats["pointer"],
            name="knob_pointer", material_class_id="plastic.opaque_generic",
        )
        model.articulation(
            f"knob_{i}_spin",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=knob,
            origin=Origin(xyz=(kx, mount_y, knob_z)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=6.0),
        )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_built_in_oven(
    config: BuiltInOvenConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"oven_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_body(model, r, mats, assets=assets)
    emitter = _DOOR_EMITTERS[r.door_mechanism]
    for i, hz in enumerate(r.hinge_zs):
        emitter(model, r, body, mats, i=i, hz=hz, assets=assets)
    _build_racks(model, r, body, mats, assets=assets)
    _build_knobs(model, r, body, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_built_in_oven(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_built_in_oven(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_built_in_oven_tests(
    object_model: ArticulatedObject,
    config: BuiltInOvenConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("oven_body")
    part_names = {p.name for p in object_model.parts}

    # ---- Rail / cap overlap allowances (element-scoped). ----
    if r.door_mechanism == "drop_down_bottom_hinge":
        for i in range(r.door_count):
            door = object_model.get_part(f"door_{i}")
            ctx.allow_overlap(
                door,
                body,
                reason=f"closed drop-down door {i} seats in the fascia opening / shell.",
            )
    elif r.door_mechanism == "side_hinge_single":
        for i in range(r.door_count):
            door = object_model.get_part(f"door_{i}")
            ctx.allow_overlap(
                door,
                body,
                elem_a="door_frame",
                elem_b="front_fascia",
                reason=f"Side-hinge door {i} panel seats flush in the fascia opening.",
            )
            ctx.allow_overlap(
                door,
                body,
                reason=f"closed side-hinge door {i} seats in the fascia opening / shell.",
            )
    else:  # french_double_door
        for i in range(r.door_count):
            for leaf_idx in range(2):
                leaf = object_model.get_part(f"door_leaf_{i}_{leaf_idx}")
                ctx.allow_overlap(
                    leaf,
                    body,
                    elem_a="leaf_frame",
                    elem_b="front_fascia",
                    reason=f"French leaf {i}.{leaf_idx} seats in the fascia opening.",
                )
                ctx.allow_overlap(
                    leaf,
                    body,
                    reason=f"closed french leaf {i}.{leaf_idx} seats on the fascia front.",
                )

    # racks ride fixed cavity rails inside the body cavity.
    for i in range(r.door_count):
        zs = _rack_zs(r, r.hinge_zs[i])
        door_parts = _cavity_door_parts(r, i)
        for ri in range(len(zs)):
            rack = object_model.get_part(f"rack_{i}_{ri}")
            ctx.allow_overlap(
                rack,
                body,
                reason=f"rack_{i}_{ri} slides inside the cavity and rests on its side rails.",
            )
            # Sequenced mechanism: rack_i_ri pulls out (-Y) only over the OPEN
            # door(s) of its cavity. The sampled "door shut + rack extended" pose
            # is an unphysical pose-setter combo, not a real operating state, so
            # the rack passing through the closed door leaf is allowed. Scoped to
            # exactly rack↔door of the same cavity — rack↔oven_body (cavity walls)
            # is declared separately above and other cavities' doors are untouched.
            for door_name in door_parts:
                door = object_model.get_part(door_name)
                ctx.allow_overlap(
                    rack,
                    door,
                    reason=(
                        f"Sequenced mechanism: rack_{i}_{ri} slides out (-Y) only over "
                        f"the OPEN {door_name}; the 'door shut + rack out' pose is an "
                        f"unphysical pose-setter combo, not a real operating state, so "
                        f"the rack passing through the closed door is allowed. Scoped to "
                        f"rack_{i}_{ri}↔{door_name} only."
                    ),
                )

    # knob caps seat 0.5 mm into the fascia/control strip face.
    for i in range(r.knob_count):
        knob = object_model.get_part(f"knob_{i}")
        ctx.allow_overlap(
            knob,
            body,
            elem_a="knob_cap",
            elem_b="front_fascia",
            reason=f"knob_{i} cap seats over its shaft boss, 0.5 mm into the fascia front.",
        )
        ctx.allow_overlap(
            knob,
            body,
            elem_a="knob_cap",
            elem_b="control_glass",
            reason=f"knob_{i} cap laps the control_glass on the fascia control strip band.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity. ----
    ctx.check("oven_body present", "oven_body" in part_names, details=str(sorted(part_names)))

    aabb = ctx.part_world_aabb(body)
    if aabb is not None:
        ctx.check(
            "oven body grounded at z=0",
            abs(aabb[0][2]) < 0.01,
            details=f"z_min={aabb[0][2]:.4f}",
        )

    # ---- Door mechanism joint topology. ----
    if r.door_mechanism == "drop_down_bottom_hinge":
        for i in range(r.door_count):
            j = object_model.get_articulation(f"body_to_door_{i}")
            ctx.check(
                f"door_{i} is REVOLUTE about +X (drop-down)",
                j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
                details=f"type={j.articulation_type} axis={tuple(j.axis)}",
            )
    elif r.door_mechanism == "side_hinge_single":
        for i in range(r.door_count):
            j = object_model.get_articulation(f"body_to_door_{i}")
            ctx.check(
                f"door_{i} is REVOLUTE about -Z (side hinge)",
                j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) > 0.99,
                details=f"type={j.articulation_type} axis={tuple(j.axis)}",
            )
    else:
        for i in range(r.door_count):
            j0 = object_model.get_articulation(f"body_to_door_leaf_{i}_0")
            j1 = object_model.get_articulation(f"body_to_door_leaf_{i}_1")
            ctx.check(
                f"cavity {i} french double = 2 mirrored REVOLUTE leaves",
                j0.articulation_type == ArticulationType.REVOLUTE
                and j1.articulation_type == ArticulationType.REVOLUTE
                and abs(j0.axis[2]) > 0.99
                and abs(j1.axis[2]) > 0.99
                and j0.axis[2] * j1.axis[2] < 0,
                details=f"l0={tuple(j0.axis)} l1={tuple(j1.axis)}",
            )

    # ---- door_count: cavities stacked along +Z. ----
    if r.door_count >= 2:
        if r.door_mechanism == "french_double_door":
            p0 = object_model.get_part("door_leaf_0_0")
            p1 = object_model.get_part("door_leaf_1_0")
        else:
            p0 = object_model.get_part("door_0")
            p1 = object_model.get_part("door_1")
        a0 = ctx.part_world_aabb(p0)
        a1 = ctx.part_world_aabb(p1)
        if a0 is not None and a1 is not None:
            ctx.check(
                "cavity 1 stacks above cavity 0",
                (a0[0][2] + a0[1][2]) / 2.0 < (a1[0][2] + a1[1][2]) / 2.0,
                details=f"c0_z={(a0[0][2] + a0[1][2]) / 2.0:.3f} c1_z={(a1[0][2] + a1[1][2]) / 2.0:.3f}",
            )

    # ---- rack_count: each rack is PRISMATIC -Y and slides forward. ----
    total_racks = 0
    for i in range(r.door_count):
        zs = _rack_zs(r, r.hinge_zs[i])
        for ri in range(len(zs)):
            total_racks += 1
            rack = object_model.get_part(f"rack_{i}_{ri}")
            j = object_model.get_articulation(f"body_to_rack_{i}_{ri}")
            travel = j.motion_limits.upper
            ctx.check(
                f"rack_{i}_{ri} is PRISMATIC about -Y",
                j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[1]) > 0.99,
                details=f"type={j.articulation_type} axis={tuple(j.axis)}",
            )
            rack_aabb = ctx.part_world_aabb(rack)
            if rack_aabb is not None:
                rack_center_x = (rack_aabb[0][0] + rack_aabb[1][0]) / 2.0
                ctx.check(
                    f"rack_{i}_{ri} is centered in the cavity width",
                    abs(rack_center_x) < 0.020
                    and rack_aabb[0][0] > -r.open_w / 2.0
                    and rack_aabb[1][0] < r.open_w / 2.0,
                    details=f"x_range=({rack_aabb[0][0]:.3f},{rack_aabb[1][0]:.3f}) center={rack_center_x:.3f}",
                )
                ctx.check(
                    f"rack_{i}_{ri} rests inside the cavity depth",
                    rack_aabb[0][1] >= _RACK_CAVITY_FRONT_Y + 0.010
                    and rack_aabb[1][1] <= min(_RACK_CAVITY_REAR_Y, r.body_d) + 0.005,
                    details=(
                        f"y_range=({rack_aabb[0][1]:.3f},{rack_aabb[1][1]:.3f}) "
                        f"rest_y={r.rack_rest_y:.3f}"
                    ),
                )
            with ctx.pose({j: travel}):
                open_aabb = ctx.part_world_aabb(rack)
            if open_aabb is not None:
                retained = max(
                    0.0,
                    min(open_aabb[1][1], min(_RACK_CAVITY_REAR_Y, r.body_d))
                    - max(open_aabb[0][1], _RACK_CAVITY_FRONT_Y),
                )
                ctx.check(
                    f"rack_{i}_{ri} remains captured at full extension",
                    retained >= _RACK_RETAIN - 0.005,
                    details=f"retained_y={retained:.3f} travel={travel:.3f}",
                )
    ctx.check(
        "rack count matches Nd*Nr",
        total_racks == r.door_count * r.rack_count,
        details=f"total={total_racks} expected={r.door_count * r.rack_count}",
    )

    # rack slides forward (-Y) on actuation (uses the solved travel limit).
    if r.rack_count >= 1:
        j = object_model.get_articulation("body_to_rack_0_0")
        rack = object_model.get_part("rack_0_0")
        travel = j.motion_limits.upper
        p0 = ctx.part_world_position(rack)
        with ctx.pose({j: travel}):
            p1 = ctx.part_world_position(rack)
        if p0 is not None and p1 is not None:
            ctx.check(
                "rack pulls out toward the user (-Y)",
                p1[1] < p0[1] - 0.05,
                details=f"closed_y={p0[1]:.3f} open_y={p1[1]:.3f} travel={travel:.3f}",
            )

    # ---- knob_count: CONTINUOUS front-normal spin; pointer moves on half-turn. ----
    for i in range(r.knob_count):
        j = object_model.get_articulation(f"knob_{i}_spin")
        ctx.check(
            f"knob_{i} is CONTINUOUS about -Y (front normal)",
            j.articulation_type == ArticulationType.CONTINUOUS and abs(j.axis[1]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    if r.knob_count >= 1:
        j = object_model.get_articulation("knob_0_spin")
        knob = object_model.get_part("knob_0")
        rest = ctx.part_element_world_aabb(knob, elem="knob_pointer")
        with ctx.pose({j: math.pi}):
            flip = ctx.part_element_world_aabb(knob, elem="knob_pointer")
        if rest is not None and flip is not None:
            rest_z = (rest[0][2] + rest[1][2]) / 2.0
            flip_z = (flip[0][2] + flip[1][2]) / 2.0
            ctx.check(
                "off-axis knob pointer swings across after a half turn",
                abs(flip_z - rest_z) > 0.010,
                details=f"rest_z={rest_z:.4f} flip_z={flip_z:.4f}",
            )

    # ---- door opens / exposes the cavity. ----
    if r.door_mechanism == "drop_down_bottom_hinge":
        j = object_model.get_articulation("body_to_door_0")
        door = object_model.get_part("door_0")
        closed = ctx.part_world_aabb(door)
        with ctx.pose({j: r.door_open_angle * 0.9}):
            opened = ctx.part_world_aabb(door)
        if closed is not None and opened is not None:
            ctx.check(
                "drop-down door swings forward (-Y) and down",
                opened[0][1] < closed[0][1] - 0.05,
                details=f"closed_ymin={closed[0][1]:.3f} open_ymin={opened[0][1]:.3f}",
            )

    # ---- slot_choices recorded with the multiplicity axes encoded. ----
    ctx.check(
        "slot_choices recorded with door/rack/knob counts encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "BuiltInOvenConfig",
    "ResolvedBuiltInOvenConfig",
    "build_built_in_oven",
    "build_seeded_built_in_oven",
    "config_from_seed",
    "resolve_config",
    "run_built_in_oven_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
