# SPDX-License-Identifier: Apache-2.0

"""Industrial / Blast door -- modular procedural template.

A heavy industrial blast / security door SET INTO A WALL: a grounded
board-formed concrete ``wall_frame`` (wall + proud dark-steel frame around a
clear opening) closed by one or more thick matte-steel leaves that operate on
the category-defining motion, plus a latch actuator on the active leaf.

Slot graph (pattern = mixed: root wall + operation child leaf(es) + control
child actuator + a ``leaf_form`` (3) axis + a ``hinge_count`` multiplicity axis):

    wall_frame (root; concrete wall + steel frame; opening width per operation)
        |- operation  (single_swing / double_swing / slide / vertical_lift)
        |      emits leaf part(s) + wall<->leaf joint + static wall hardware
        |- control    (lever_handle / crash_bar / handwheel)
               emits the actuator part parented to the active leaf

Adapted per AUTHORING.md §A/§B from the confirmed 5-star Blast door pool
(spec: specs_modular_v1/Industrial_Blast_door.md). Sources (model.py:Lx-Ly in
the spec Module Source Index):

  S1  origin 母本 rec_heavy-...afa2cf0b -- wall+frame, single flat swing leaf on a
      REVOLUTE hinge with N barrels, lever handle, window/lock/button, tests.
  S2  form_dished_leaf   -- convex barrel-vault dished leaf (3 form).
  S3  joint_crash_bar    -- PRISMATIC panic push bar control.
  S4  joint_wheel        -- REVOLUTE handwheel valve control.
  S5  mult_hinges_two    -- hinge_count multiplicity low.
  S6  mult_hinges_five   -- hinge_count multiplicity high.
  S7  skeleton_double_leaf -- biparting 2-leaf skeleton + astragal.
  S8  skeleton_sliding   -- sliding leaf on a head rail (PRISMATIC X).
  S9  skeleton_vertical_lift -- guillotine lift in C-channels (PRISMATIC Z).

Coordinate frame: X = along the wall, Y = wall thickness (viewer at -Y), Z = up,
floor at z = 0. The clear opening is centred on x = 0.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

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
    BezelGeometry,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


Operation = Literal["single_swing", "double_swing", "slide", "vertical_lift"]
Control = Literal["lever_handle", "crash_bar", "handwheel"]
LeafForm = Literal["flat_plate", "dished_leaf"]
BlastDoorPalette = Literal[
    "matte_black",
    "safety_hazard",
    "galvanized",
    "navy_bulkhead",
    "rust_oxide",
    "olive_military",
]

_SWING_OPS = ("single_swing", "double_swing")


# --------------------------------------------------------------------------- #
# Canonical dimensions (origin 母本 rec_heavy-...afa2cf0b)
# --------------------------------------------------------------------------- #

WALL_W = 3.40
WALL_T = 0.24
WALL_H = 2.60

# Single-leaf opening family (slide / vertical_lift share it).
OPEN_W_SINGLE = 0.96
LEAF_W_SINGLE = 1.04
# Double-leaf biparting opening family.
OPEN_W_DOUBLE = 1.92
LEAF_W_DOUBLE = 0.98

OPEN_H_BASE = 2.04
LEAF_H_BASE = 2.10
LEAF_T = 0.06

FRAME_PROUD = 0.02          # steel frame stands proud of the concrete front (y=0)
FRAME_DEPTH = 0.12
FRAME_JAMB_W = 0.08         # steel frame reveal width (per side)
FRAME_HEAD_H = 0.08         # steel frame head height above the opening

DOOR_Y = -0.066             # leaf mid-thickness plane (back clear in front of frame)
LEAF_FRONT = -LEAF_T / 2.0  # leaf front face in leaf-local frame
LEAF_Z0 = 0.01              # leaf bottom above floor

GAP_FROM_HINGE = 0.02       # leaf near edge gap from the pivot axis

# Feature offsets from the leaf CENTRE (dx) + base z heights (scaled by open_h).
WINDOW_DX, WINDOW_Z, WINDOW_W, WINDOW_H = -0.12, 1.55, 0.32, 0.20
BUTTON_DX, BUTTON_Z = 0.16, 1.58
LOCK_DX, LOCK_Z = 0.26, 1.30
HANDLE_DX, HANDLE_Z = 0.26, 1.05

DOME_RISE = 0.015           # dished-leaf barrel-vault protrusion (flat baseline)
PUSH_TRAVEL = 0.045         # crash-bar inward stroke
BAR_LENGTH = 0.60
BAR_TUBE_R = 0.018
BAR_STANDOFF = 0.11         # bar-tube stands well proud; tube stays clear of leaf
BEZEL_Y = -0.012            # bezel origin y: protrude the front, sit flush at back


# --------------------------------------------------------------------------- #
# Palettes (>=6 colorways; tokens shared so every .visual resolves)
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "matte_black": {
        "concrete": (0.62, 0.61, 0.58, 1.0),
        "frame_steel": (0.15, 0.16, 0.17, 1.0),
        "leaf_steel": (0.10, 0.10, 0.11, 1.0),
        "bezel_black": (0.06, 0.06, 0.07, 1.0),
        "glass": (0.62, 0.72, 0.76, 0.45),
        "stainless": (0.74, 0.75, 0.77, 1.0),
        "blue_button": (0.10, 0.38, 0.85, 1.0),
        "hinge_steel": (0.20, 0.21, 0.22, 1.0),
    },
    "safety_hazard": {
        "concrete": (0.60, 0.59, 0.56, 1.0),
        "frame_steel": (0.12, 0.12, 0.13, 1.0),
        "leaf_steel": (0.85, 0.62, 0.05, 1.0),
        "bezel_black": (0.08, 0.08, 0.08, 1.0),
        "glass": (0.62, 0.72, 0.76, 0.45),
        "stainless": (0.80, 0.81, 0.83, 1.0),
        "blue_button": (0.80, 0.10, 0.10, 1.0),
        "hinge_steel": (0.16, 0.16, 0.17, 1.0),
    },
    "galvanized": {
        "concrete": (0.66, 0.65, 0.63, 1.0),
        "frame_steel": (0.58, 0.60, 0.62, 1.0),
        "leaf_steel": (0.70, 0.72, 0.74, 1.0),
        "bezel_black": (0.20, 0.21, 0.22, 1.0),
        "glass": (0.60, 0.70, 0.76, 0.45),
        "stainless": (0.82, 0.84, 0.86, 1.0),
        "blue_button": (0.12, 0.40, 0.85, 1.0),
        "hinge_steel": (0.55, 0.57, 0.59, 1.0),
    },
    "navy_bulkhead": {
        "concrete": (0.58, 0.58, 0.57, 1.0),
        "frame_steel": (0.16, 0.20, 0.28, 1.0),
        "leaf_steel": (0.18, 0.24, 0.34, 1.0),
        "bezel_black": (0.07, 0.09, 0.12, 1.0),
        "glass": (0.60, 0.70, 0.76, 0.45),
        "stainless": (0.74, 0.76, 0.78, 1.0),
        "blue_button": (0.85, 0.68, 0.10, 1.0),
        "hinge_steel": (0.22, 0.26, 0.32, 1.0),
    },
    "rust_oxide": {
        "concrete": (0.60, 0.58, 0.55, 1.0),
        "frame_steel": (0.30, 0.16, 0.10, 1.0),
        "leaf_steel": (0.45, 0.22, 0.13, 1.0),
        "bezel_black": (0.14, 0.08, 0.05, 1.0),
        "glass": (0.58, 0.66, 0.70, 0.45),
        "stainless": (0.70, 0.66, 0.60, 1.0),
        "blue_button": (0.10, 0.40, 0.80, 1.0),
        "hinge_steel": (0.34, 0.20, 0.13, 1.0),
    },
    "olive_military": {
        "concrete": (0.58, 0.57, 0.52, 1.0),
        "frame_steel": (0.22, 0.24, 0.16, 1.0),
        "leaf_steel": (0.28, 0.31, 0.20, 1.0),
        "bezel_black": (0.10, 0.11, 0.08, 1.0),
        "glass": (0.58, 0.68, 0.66, 0.45),
        "stainless": (0.72, 0.73, 0.70, 1.0),
        "blue_button": (0.80, 0.20, 0.10, 1.0),
        "hinge_steel": (0.26, 0.28, 0.20, 1.0),
    },
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class IndustrialBlastDoorConfig:
    operation: Operation = "single_swing"
    control: Control = "lever_handle"
    leaf_form: LeafForm = "flat_plate"
    palette_style: BlastDoorPalette = "matte_black"

    hinge_count: int = 3   # barrel hinges per swing leaf; ignored for slide/lift

    open_h_scale: float = 1.0
    leaf_w_scale: float = 1.0
    dome_rise_scale: float = 1.0   # dished_leaf only
    swing_upper: float = 2.0       # swing REVOLUTE upper (rad)
    handwheel_turn: float = math.pi  # handwheel REVOLUTE upper (rad)


@dataclass(frozen=True)
class ResolvedIndustrialBlastDoorConfig:
    operation: Operation
    control: Control
    leaf_form: LeafForm
    palette_style: str

    hinge_count: int

    open_h_scale: float
    leaf_w_scale: float
    dome_rise_scale: float
    swing_upper: float
    handwheel_turn: float

    # Derived, single-sourced geometry (Contract 3c).
    open_w: float
    open_h: float
    leaf_w: float
    leaf_h: float
    frame_out_w: float
    frame_out_h: float
    slide_travel: float

    # Active (control-carrying) leaf identity.
    active_leaf: str
    active_sign: float     # +1 / -1 (mirror for the right leaf)

    palette: dict[str, tuple[float, float, float, float]]

    def feat_z(self, base_z: float) -> float:
        return base_z * self.open_h_scale


# --------------------------------------------------------------------------- #
# Seed-driven sampling (procedural-first)
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> IndustrialBlastDoorConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin 母本 combination (single_swing + hinge 3 +
    lever_handle + flat_plate, matte_black) as a documented regression anchor
    (a sparse override; every other seed is fully procedural).
    """
    if seed == 0:
        return IndustrialBlastDoorConfig()

    rng = random.Random(seed)

    operation: Operation = rng.choice(
        ("single_swing", "double_swing", "slide", "vertical_lift")
    )
    control: Control = rng.choice(("lever_handle", "crash_bar", "handwheel"))
    leaf_form: LeafForm = rng.choice(("flat_plate", "dished_leaf"))
    palette_style = rng.choice(PALETTE_NAMES)

    hinge_count = rng.choices((2, 3, 5), weights=(0.3, 0.5, 0.2))[0]

    open_h_scale = round(rng.uniform(0.94, 1.06), 4)
    leaf_w_scale = round(rng.uniform(0.96, 1.06), 4)
    dome_rise_scale = round(rng.uniform(0.7, 1.4), 4)
    swing_upper = round(rng.uniform(1.5, 2.1), 4)
    handwheel_turn = round(rng.uniform(2.2, math.pi), 4)

    return IndustrialBlastDoorConfig(
        operation=operation,
        control=control,
        leaf_form=leaf_form,
        palette_style=palette_style,
        hinge_count=hinge_count,
        open_h_scale=open_h_scale,
        leaf_w_scale=leaf_w_scale,
        dome_rise_scale=dome_rise_scale,
        swing_upper=swing_upper,
        handwheel_turn=handwheel_turn,
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(
    config: IndustrialBlastDoorConfig,
) -> ResolvedIndustrialBlastDoorConfig:
    if str(config.operation) not in {
        "single_swing",
        "double_swing",
        "slide",
        "vertical_lift",
    }:
        raise ValueError(f"Unsupported operation: {config.operation}")
    if str(config.control) not in {"lever_handle", "crash_bar", "handwheel"}:
        raise ValueError(f"Unsupported control: {config.control}")
    if str(config.leaf_form) not in {"flat_plate", "dished_leaf"}:
        raise ValueError(f"Unsupported leaf_form: {config.leaf_form}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    open_h_scale = _clamp(config.open_h_scale, 0.94, 1.06)
    leaf_w_scale = _clamp(config.leaf_w_scale, 0.96, 1.06)
    dome_rise_scale = _clamp(config.dome_rise_scale, 0.7, 1.4)
    swing_upper = _clamp(config.swing_upper, 1.5, 2.1)
    handwheel_turn = _clamp(config.handwheel_turn, 2.2, math.pi)

    # hinge_count only for swing operations.
    hinge_count = int(config.hinge_count) if int(config.hinge_count) in (2, 3, 5) else 3

    # Derived opening / frame / leaf dimensions (equation constraints).
    if config.operation == "double_swing":
        open_w = OPEN_W_DOUBLE * leaf_w_scale
        leaf_w = LEAF_W_DOUBLE * leaf_w_scale
    else:
        open_w = OPEN_W_SINGLE * leaf_w_scale
        leaf_w = LEAF_W_SINGLE * leaf_w_scale
    open_h = OPEN_H_BASE * open_h_scale
    leaf_h = LEAF_H_BASE * open_h_scale
    frame_out_w = open_w + 2.0 * FRAME_JAMB_W
    frame_out_h = open_h + FRAME_HEAD_H
    slide_travel = open_w + 0.24

    if config.operation == "double_swing":
        active_leaf = "door_leaf_right"
        active_sign = -1.0
    else:
        active_leaf = "door_leaf"
        active_sign = 1.0

    return ResolvedIndustrialBlastDoorConfig(
        operation=config.operation,
        control=config.control,
        leaf_form=config.leaf_form,
        palette_style=config.palette_style,
        hinge_count=hinge_count,
        open_h_scale=open_h_scale,
        leaf_w_scale=leaf_w_scale,
        dome_rise_scale=dome_rise_scale,
        swing_upper=swing_upper,
        handwheel_turn=handwheel_turn,
        open_w=open_w,
        open_h=open_h,
        leaf_w=leaf_w,
        leaf_h=leaf_h,
        frame_out_w=frame_out_w,
        frame_out_h=frame_out_h,
        slide_travel=slide_travel,
        active_leaf=active_leaf,
        active_sign=active_sign,
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #


def _box(part, *, x0, x1, y0, y1, z0, z1, material, name) -> None:
    """Axis-aligned box spanning [x0,x1]x[y0,y1]x[z0,z1]."""
    part.visual(
        Box((abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))),
        origin=Origin(xyz=((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0)),
        material=material,
        name=name, material_class_id=_material_class_id(material, ("concrete",), "concrete.formed_patterned", "metal.paint_coated"),
    )


def _front_y(r: ResolvedIndustrialBlastDoorConfig, dx: float) -> float:
    """Front surface y (leaf-local) at lateral offset ``dx`` from the leaf
    centre. Flat = -LEAF_T/2; dished = the convex barrel-vault arc (so applied
    face hardware hugs the realized surface across the 3 form / 5 dims -- Rule 4)."""
    if r.leaf_form != "dished_leaf":
        return -LEAF_T / 2.0
    rise = DOME_RISE * r.dome_rise_scale
    half = r.leaf_w / 2.0
    d = min(abs(dx), half)
    radius = (half * half + rise * rise) / (2.0 * rise)
    h = rise - radius + math.sqrt(max(radius * radius - d * d, 0.0))
    return -LEAF_T / 2.0 - h


def _seat_disc(r: ResolvedIndustrialBlastDoorConfig, dx: float, *, proud: float = 0.006):
    """Return (center_y, length) for a Y-axis face disc at offset ``dx`` that
    protrudes ``proud`` past the realized front surface and embeds into the
    leaf solid (so it never floats off a domed face)."""
    fy = _front_y(r, dx)
    front = fy - proud
    back = fy + 0.022
    return (front + back) / 2.0, (back - front)


def _hinge_zs(r: ResolvedIndustrialBlastDoorConfig) -> list[float]:
    """Evenly spaced barrel-hinge heights along the leaf (source-matched span)."""
    n = r.hinge_count
    lo, hi = 0.40 * r.open_h_scale, 1.70 * r.open_h_scale
    if n <= 1:
        return [(lo + hi) / 2.0]
    return [lo + (hi - lo) * i / (n - 1) for i in range(n)]


def _leaf_plate_mesh(r: ResolvedIndustrialBlastDoorConfig, center_x: float):
    """Leaf plate (3 form) with the viewing-window cut. flat_plate = box;
    dished_leaf = box + convex barrel-vault dome union (form_dished_leaf S2)."""
    leaf = (
        cq.Workplane("XY")
        .box(r.leaf_w, LEAF_T, r.leaf_h, centered=(True, True, False))
        .translate((center_x, 0.0, LEAF_Z0))
    )
    if r.leaf_form == "dished_leaf":
        rise = DOME_RISE * r.dome_rise_scale
        half_w = r.leaf_w / 2.0
        front_flat = -LEAF_T / 2.0
        peak = front_flat - rise
        dome = (
            cq.Workplane("XY")
            .moveTo(center_x - half_w, front_flat)
            .threePointArc((center_x, peak), (center_x + half_w, front_flat))
            .close()
            .extrude(r.leaf_h)
            .translate((0.0, 0.0, LEAF_Z0))
        )
        leaf = leaf.union(dome)

    window_cx = center_x + WINDOW_DX
    window_cut = (
        cq.Workplane("XY")
        .box(WINDOW_W + 0.02, LEAF_T + 2.0 * DOME_RISE + 0.06, WINDOW_H + 0.02)
        .translate((window_cx, 0.0, r.feat_z(WINDOW_Z)))
    )
    leaf = leaf.cut(window_cut)
    return mesh_from_cadquery(leaf, "door_leaf_plate")


def _build_leaf_visuals(part, r: ResolvedIndustrialBlastDoorConfig, *, center_x: float) -> None:
    """Leaf slab + window bezel/glass + button + lock (host visuals, Rule 1).
    ``center_x`` is the leaf centre in the leaf-part-local frame."""
    part.visual(_leaf_plate_mesh(r, center_x), material="leaf_steel", name="leaf_plate", material_class_id="metal.paint_coated")

    window_cx = center_x + WINDOW_DX
    wz = r.feat_z(WINDOW_Z)
    bezel = BezelGeometry(
        (WINDOW_W, WINDOW_H),
        (WINDOW_W + 0.10, WINDOW_H + 0.10),
        LEAF_T + 0.024,
        opening_shape="rect",
        outer_shape="rect",
    )
    part.visual(
        mesh_from_geometry(bezel, "window_bezel"),
        origin=Origin(xyz=(window_cx, BEZEL_Y, wz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="bezel_black",
        name="window_bezel", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Box((WINDOW_W + 0.03, 0.008, WINDOW_H + 0.03)),
        origin=Origin(xyz=(window_cx, 0.0, wz)),
        material="glass",
        name="window_glass", material_class_id=("glass.damaged_cracked" if r.palette_style == "rust_oxide" else "glass.clear_transparent"),
    )
    bcy, blen = _seat_disc(r, BUTTON_DX)
    part.visual(
        Cylinder(radius=0.021, length=blen),
        origin=Origin(xyz=(center_x + BUTTON_DX, bcy, r.feat_z(BUTTON_Z)),
                      rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="blue_button",
        name="blue_button", material_class_id="plastic.opaque_glossy_molded",
    )
    ecy, elen = _seat_disc(r, LOCK_DX)
    part.visual(
        Cylinder(radius=0.026, length=elen),
        origin=Origin(xyz=(center_x + LOCK_DX, ecy, r.feat_z(LOCK_Z)),
                      rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="stainless",
        name="lock_escutcheon", material_class_id="metal.stainless_matte",
    )
    lcy, llen = _seat_disc(r, LOCK_DX, proud=0.014)
    part.visual(
        Cylinder(radius=0.008, length=llen),
        origin=Origin(xyz=(center_x + LOCK_DX, lcy, r.feat_z(LOCK_Z)),
                      rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="frame_steel",
        name="lock_cylinder", material_class_id="metal.paint_coated",
    )


def _emit_swing_hardware(wall, door, r, *, hinge_x: float, sign: float) -> None:
    """N barrel hinges on the door + frame-side jamb tabs on the wall."""
    for i, hz in enumerate(_hinge_zs(r)):
        door.visual(
            Cylinder(radius=0.024, length=0.18),
            origin=Origin(xyz=(0.0, 0.0, hz)),
            material="hinge_steel",
            name=f"hinge_barrel_{i}", material_class_id="metal.steel_bare",
        )
        door.visual(
            Box((0.13, 0.014, 0.10)),
            origin=Origin(xyz=(sign * 0.055, LEAF_FRONT - 0.004, hz)),
            material="hinge_steel",
            name=f"hinge_strap_{i}", material_class_id="metal.steel_bare",
        )
        wall.visual(
            Box((0.062, 0.057, 0.030)),
            origin=Origin(xyz=(hinge_x - sign * 0.014, -0.0335, hz + 0.075)),
            material="frame_steel",
            name=f"hinge_tab_{door.name}_{i}", material_class_id="metal.paint_coated",
        )


# --------------------------------------------------------------------------- #
# Slot A -- wall_frame (root)
# --------------------------------------------------------------------------- #


def _wall_downstream(r: ResolvedIndustrialBlastDoorConfig) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="wall_frame",
        visual_name="steel_frame_top",
        face_side="negative_y",
        anchor_local=(0.0, -FRAME_PROUD, r.open_h),
        face_extents_uv=(r.open_w, 0.4),
        contact_tol=0.006,
    )


def _build_wall_frame(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialBlastDoorConfig = ctx.config  # type: ignore[assignment]
    wall = model.part("wall_frame")

    hw = WALL_W / 2.0
    ho = r.open_w / 2.0
    hf = r.frame_out_w / 2.0

    # --- board-formed concrete wall built as boxes around the opening ---
    _box(wall, x0=-hw, x1=hw, y0=0.0, y1=WALL_T, z0=r.open_h, z1=WALL_H,
         material="concrete", name="concrete_lintel")
    _box(wall, x0=-hw, x1=-ho, y0=0.0, y1=WALL_T, z0=0.0, z1=r.open_h,
         material="concrete", name="concrete_jamb_l")
    _box(wall, x0=ho, x1=hw, y0=0.0, y1=WALL_T, z0=0.0, z1=r.open_h,
         material="concrete", name="concrete_jamb_r")

    # --- proud steel frame (4 boxes forming a rectangle around the opening) ---
    fy0, fy1 = -FRAME_PROUD, -FRAME_PROUD + FRAME_DEPTH
    _box(wall, x0=-hf, x1=-ho, y0=fy0, y1=fy1, z0=0.0, z1=r.frame_out_h,
         material="frame_steel", name="steel_frame_left")
    _box(wall, x0=ho, x1=hf, y0=fy0, y1=fy1, z0=0.0, z1=r.frame_out_h,
         material="frame_steel", name="steel_frame_right")
    _box(wall, x0=-ho, x1=ho, y0=fy0, y1=fy1, z0=r.open_h, z1=r.frame_out_h,
         material="frame_steel", name="steel_frame_top")

    return ModuleBuild(
        module_name="wall_frame",
        parts_emitted=["wall_frame"],
        interfaces={"downstream": _wall_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot B -- operation (children of wall_frame)
# --------------------------------------------------------------------------- #


def _swing_hinge_x(r: ResolvedIndustrialBlastDoorConfig) -> float:
    """Single-leaf pivot axis x (leaf ends up centred on the opening)."""
    return -(GAP_FROM_HINGE + r.leaf_w / 2.0)


def _build_single_swing(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialBlastDoorConfig = ctx.config  # type: ignore[assignment]
    wall = model.get_part("wall_frame")

    door = model.part("door_leaf")
    center_x = GAP_FROM_HINGE + r.leaf_w / 2.0   # leaf centre in leaf-local frame
    _build_leaf_visuals(door, r, center_x=center_x)
    hinge_x = _swing_hinge_x(r)
    _emit_swing_hardware(wall, door, r, hinge_x=hinge_x, sign=1.0)

    model.articulation(
        "door_hinge", ArticulationType.REVOLUTE, parent=wall, child=door,
        origin=Origin(xyz=(hinge_x, DOOR_Y, 0.0)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=200.0, velocity=1.0, lower=0.0, upper=r.swing_upper),
    )
    return ModuleBuild(
        module_name="single_swing",
        parts_emitted=["door_leaf"],
        internal_articulations=["door_hinge"],
        interfaces={"downstream": _wall_downstream(r)},
    )


def _build_double_swing(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialBlastDoorConfig = ctx.config  # type: ignore[assignment]
    wall = model.get_part("wall_frame")

    # Each leaf free edge sits 0.02 short of x=0 (a 0.04 centre gap the astragal
    # bridges). Pivot axis = free-edge - leaf_w back toward the jamb.
    free_edge = 0.02
    parts, joints = [], []
    for side, sign in (("left", 1.0), ("right", -1.0)):
        name = f"door_leaf_{side}"
        door = model.part(name)
        center_x = sign * (r.leaf_w / 2.0 + GAP_FROM_HINGE)
        _build_leaf_visuals(door, r, center_x=center_x)
        # world free edge = hinge_x + sign*(GAP+leaf_w); we want it at sign*-free_edge
        hinge_x = sign * (-free_edge) - sign * (GAP_FROM_HINGE + r.leaf_w)
        _emit_swing_hardware(wall, door, r, hinge_x=hinge_x, sign=sign)

        # Left leaf carries the astragal bridging the centre gap.
        if side == "left":
            door.visual(
                Box((0.030, 0.008, r.leaf_h - 0.06)),
                origin=Origin(xyz=(GAP_FROM_HINGE + r.leaf_w + 0.006,
                                   LEAF_FRONT - 0.004,
                                   LEAF_Z0 + r.leaf_h / 2.0)),
                material="frame_steel",
                name="astragal", material_class_id="metal.paint_coated",
            )

        jn = f"door_hinge_{side}"
        model.articulation(
            jn, ArticulationType.REVOLUTE, parent=wall, child=door,
            origin=Origin(xyz=(hinge_x, DOOR_Y, 0.0)),
            axis=(0.0, 0.0, -sign),
            motion_limits=MotionLimits(effort=200.0, velocity=1.0, lower=0.0, upper=r.swing_upper),
        )
        parts.append(name)
        joints.append(jn)

    return ModuleBuild(
        module_name="double_swing",
        parts_emitted=parts,
        internal_articulations=joints,
        interfaces={"downstream": _wall_downstream(r)},
    )


def _build_slide(ctx: ModuleBuildContext) -> ModuleBuild:
    """Single leaf rolling +X on a slotted head rail (skeleton_sliding S8)."""
    model = ctx.model
    r: ResolvedIndustrialBlastDoorConfig = ctx.config  # type: ignore[assignment]
    wall = model.get_part("wall_frame")

    # --- static head rail + brackets on the wall ---
    rail_z = r.open_h + 0.14
    rail_len = r.open_w + r.slide_travel + 0.10
    _box(wall, x0=-r.open_w / 2.0 - 0.10, x1=-r.open_w / 2.0 - 0.10 + rail_len,
         y0=DOOR_Y - 0.033, y1=DOOR_Y + 0.033, z0=rail_z - 0.040, z1=rail_z + 0.040,
         material="frame_steel", name="head_rail")
    for i, bx in enumerate((-r.open_w / 2.0 + 0.10, r.open_w / 2.0 + 0.55)):
        _box(wall, x0=bx - 0.03, x1=bx + 0.03, y0=DOOR_Y, y1=0.0,
             z0=rail_z + 0.02, z1=rail_z + 0.08,
             material="frame_steel", name=f"rail_bracket_{i}")

    # --- leaf centred on the opening at rest ---
    door = model.part("door_leaf")
    _build_leaf_visuals(door, r, center_x=0.0)
    for i, hx in enumerate((-0.30, 0.30)):
        door.visual(
            Box((0.05, 0.012, 0.14)),
            origin=Origin(xyz=(hx, 0.0, r.leaf_h - 0.02)),
            material="frame_steel",
            name=f"hanger_stem_{i}", material_class_id="metal.paint_coated",
        )
        door.visual(
            Box((0.08, 0.050, 0.03)),
            origin=Origin(xyz=(hx, 0.0, r.leaf_h + 0.06)),
            material="frame_steel",
            name=f"trolley_{i}", material_class_id="metal.paint_coated",
        )

    model.articulation(
        "door_slide", ArticulationType.PRISMATIC, parent=wall, child=door,
        origin=Origin(xyz=(0.0, DOOR_Y, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=300.0, velocity=0.25, lower=0.0, upper=r.slide_travel),
    )
    return ModuleBuild(
        module_name="slide",
        parts_emitted=["door_leaf"],
        internal_articulations=["door_slide"],
        interfaces={"downstream": _wall_downstream(r)},
    )


def _build_vertical_lift(ctx: ModuleBuildContext) -> ModuleBuild:
    """Guillotine leaf rising +Z in two C-channel guides (S9)."""
    model = ctx.model
    r: ResolvedIndustrialBlastDoorConfig = ctx.config  # type: ignore[assignment]
    wall = model.get_part("wall_frame")

    # --- static C-channels OUTBOARD of the leaf edges, at the leaf's front
    #     y-plane (clear of the frame behind); web + 2 flanges each ---
    ch_top = r.open_h + 0.30
    x_edge = r.leaf_w / 2.0 + 0.05
    for i, sgn in enumerate((-1.0, 1.0)):
        xw = sgn * x_edge
        _box(wall, x0=xw - 0.012, x1=xw + 0.012, y0=DOOR_Y - 0.055, y1=DOOR_Y + 0.055,
             z0=0.0, z1=ch_top, material="frame_steel", name=f"guide_channel_{i}")
        for k, fy in enumerate((DOOR_Y - 0.045, DOOR_Y + 0.045)):
            _box(wall, x0=sgn * (r.leaf_w / 2.0 + 0.015), x1=xw + sgn * 0.012,
                 y0=fy - 0.010, y1=fy + 0.010, z0=0.0, z1=ch_top,
                 material="frame_steel", name=f"guide_flange_{i}_{k}")

    # --- leaf centred on the opening at rest; side runners reach into the
    #     channels (at the leaf front y-plane, clear of the frame) ---
    door = model.part("door_leaf")
    _build_leaf_visuals(door, r, center_x=0.0)
    for i, sgn in enumerate((-1.0, 1.0)):
        _box(door, x0=sgn * (r.leaf_w / 2.0 - 0.02), x1=sgn * (r.leaf_w / 2.0 + 0.06),
             y0=-0.015, y1=0.015, z0=LEAF_Z0 + 0.05, z1=LEAF_Z0 + r.leaf_h - 0.05,
             material="frame_steel", name=f"edge_runner_{i}")

    model.articulation(
        "door_lift", ArticulationType.PRISMATIC, parent=wall, child=door,
        origin=Origin(xyz=(0.0, DOOR_Y, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=500.0, velocity=0.3, lower=0.0, upper=r.open_h),
    )
    return ModuleBuild(
        module_name="vertical_lift",
        parts_emitted=["door_leaf"],
        internal_articulations=["door_lift"],
        interfaces={"downstream": _wall_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot C -- control (child of the active leaf)
# --------------------------------------------------------------------------- #


def _active_center_x(r: ResolvedIndustrialBlastDoorConfig) -> float:
    if r.operation in _SWING_OPS:
        return r.active_sign * (GAP_FROM_HINGE + r.leaf_w / 2.0)
    return 0.0


def _build_lever_handle(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialBlastDoorConfig = ctx.config  # type: ignore[assignment]
    leaf = model.get_part(r.active_leaf)
    cx = _active_center_x(r)
    hx = cx + r.active_sign * HANDLE_DX
    hz = r.feat_z(HANDLE_Z)

    rcy, rlen = _seat_disc(r, HANDLE_DX)
    leaf.visual(
        Cylinder(radius=0.032, length=rlen),
        origin=Origin(xyz=(hx, rcy, hz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="stainless", name="handle_rose", material_class_id="metal.stainless_matte",
    )

    lever = model.part("lever_handle")
    lever.visual(
        Cylinder(radius=0.014, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="stainless", name="spindle_hub", material_class_id="metal.stainless_matte",
    )
    lever.visual(
        Box((0.16, 0.022, 0.030)),
        origin=Origin(xyz=(-0.085, -0.020, 0.0)),
        material="stainless", name="lever_arm", material_class_id="metal.stainless_matte",
    )
    lever.visual(
        Sphere(radius=0.016),
        origin=Origin(xyz=(-0.165, -0.020, 0.0)),
        material="stainless", name="lever_tip", material_class_id="metal.stainless_matte",
    )

    model.articulation(
        "handle_spindle", ArticulationType.REVOLUTE, parent=leaf, child=lever,
        origin=Origin(xyz=(hx, LEAF_FRONT - 0.010, hz)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=3.0, lower=0.0, upper=0.9),
    )
    return ModuleBuild(
        module_name="lever_handle",
        parts_emitted=["lever_handle"],
        internal_articulations=["handle_spindle"],
        interfaces={"downstream": _wall_downstream(r)},
    )


def _build_handwheel(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialBlastDoorConfig = ctx.config  # type: ignore[assignment]
    leaf = model.get_part(r.active_leaf)
    cx = _active_center_x(r)
    hx = cx + r.active_sign * HANDLE_DX
    hz = r.feat_z(HANDLE_Z)

    rcy, rlen = _seat_disc(r, HANDLE_DX)
    leaf.visual(
        Cylinder(radius=0.030, length=rlen),
        origin=Origin(xyz=(hx, rcy, hz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="stainless", name="handle_rose", material_class_id="metal.stainless_matte",
    )

    wheel = model.part("lever_handle")
    WHEEL_R = 0.080
    TUBE_R = 0.009
    HUB_R = 0.016
    # Wheel plane stands well proud on its stem so the spokes clear the rose as
    # the leaf swings (spokes sweep the leaf-local XZ plane at this y).
    wheel_y = -0.035
    # Spindle hub along Y, from the wheel plane back into the leaf.
    wheel.visual(
        Cylinder(radius=HUB_R, length=0.055),
        origin=Origin(xyz=(0.0, -0.0075, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="stainless", name="spindle_hub", material_class_id="metal.stainless_matte",
    )
    # Rim ring in the leaf XZ plane (torus normal along Y).
    wheel.visual(
        mesh_from_geometry(
            TorusGeometry(WHEEL_R, TUBE_R, radial_segments=16, tubular_segments=24),
            "wheel_rim",
        ),
        origin=Origin(xyz=(0.0, wheel_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="stainless", name="wheel_rim", material_class_id="metal.stainless_matte",
    )
    # Three spokes hub->rim at 120deg in the XZ plane.
    mid_r = (HUB_R + (WHEEL_R - TUBE_R)) / 2.0
    spoke_len = (WHEEL_R - TUBE_R) - HUB_R + 0.006
    for i in range(3):
        theta = i * 2.0 * math.pi / 3.0
        wheel.visual(
            Cylinder(radius=0.007, length=spoke_len),
            origin=Origin(
                xyz=(mid_r * math.cos(theta), wheel_y, mid_r * math.sin(theta)),
                rpy=(0.0, math.pi / 2.0 - theta, 0.0),
            ),
            material="stainless", name=f"wheel_spoke_{i}", material_class_id="metal.stainless_matte",
        )

    model.articulation(
        "handle_spindle", ArticulationType.REVOLUTE, parent=leaf, child=wheel,
        origin=Origin(xyz=(hx, LEAF_FRONT - 0.010, hz)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=15.0, velocity=2.0, lower=0.0, upper=r.handwheel_turn),
    )
    return ModuleBuild(
        module_name="handwheel",
        parts_emitted=["lever_handle"],
        internal_articulations=["handle_spindle"],
        interfaces={"downstream": _wall_downstream(r)},
    )


def _build_crash_bar(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialBlastDoorConfig = ctx.config  # type: ignore[assignment]
    leaf = model.get_part(r.active_leaf)
    cx = _active_center_x(r)
    bz = r.feat_z(HANDLE_Z)

    # Door-face socket posts the bar brackets slide into (conformal to surface).
    scy, slen = _seat_disc(r, 0.25, proud=0.02)
    for i, sgn in enumerate((-1.0, 1.0)):
        leaf.visual(
            Box((0.050, slen, 0.060)),
            origin=Origin(xyz=(cx + sgn * 0.25, scy, bz)),
            material="stainless", name=f"bar_socket_{i}", material_class_id="metal.stainless_matte",
        )

    # push_bar-local frame origin is at the bar-tube centre (proud BAR_STANDOFF
    # in front of the leaf); +Y points back toward the leaf face.
    push = model.part("push_bar")
    push.visual(
        Cylinder(radius=BAR_TUBE_R, length=BAR_LENGTH),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="stainless", name="bar_tube", material_class_id="metal.stainless_matte",
    )
    # Brackets bridge from the bar back to the leaf face (into the sockets).
    brk_len = BAR_STANDOFF + 0.02
    for i, sgn in enumerate((-1.0, 1.0)):
        push.visual(
            Box((0.045, brk_len, 0.055)),
            origin=Origin(xyz=(sgn * 0.25, brk_len / 2.0, 0.0)),
            material="stainless", name=f"bracket_{i}", material_class_id="metal.stainless_matte",
        )

    model.articulation(
        "push_bar", ArticulationType.PRISMATIC, parent=leaf, child=push,
        origin=Origin(xyz=(cx, LEAF_FRONT - BAR_STANDOFF, bz)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.5, lower=0.0, upper=PUSH_TRAVEL),
    )
    return ModuleBuild(
        module_name="crash_bar",
        parts_emitted=["push_bar"],
        internal_articulations=["push_bar"],
        interfaces={"downstream": _wall_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Factory registries + assembly
# --------------------------------------------------------------------------- #

OPERATION_FACTORIES = {
    "single_swing": _build_single_swing,
    "double_swing": _build_double_swing,
    "slide": _build_slide,
    "vertical_lift": _build_vertical_lift,
}
CONTROL_FACTORIES = {
    "lever_handle": _build_lever_handle,
    "crash_bar": _build_crash_bar,
    "handwheel": _build_handwheel,
}


def _slots_for_config(r: ResolvedIndustrialBlastDoorConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="wall_frame",
                 candidates={"wall_frame": _build_wall_frame},
                 anchor_choice="wall_frame"),
        SlotSpec(slot_name="operation",
                 candidates={r.operation: OPERATION_FACTORIES[r.operation]},
                 anchor_choice=r.operation),
        SlotSpec(slot_name="control",
                 candidates={r.control: CONTROL_FACTORIES[r.control]},
                 anchor_choice=r.control),
    ]


def build_industrial_blast_door(
    config: IndustrialBlastDoorConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="industrial_blast_door", assets=assets)
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


def build_seeded_industrial_blast_door(seed: int) -> ArticulatedObject:
    return build_industrial_blast_door(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    hinge_axis = f"hinges_{r.hinge_count}" if r.operation in _SWING_OPS else "hinges_na"
    return [
        ("operation", r.operation),
        ("control", r.control),
        ("leaf_form", r.leaf_form),
        ("hinge_count", hinge_axis),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _leaf_names(r: ResolvedIndustrialBlastDoorConfig) -> list[str]:
    if r.operation == "double_swing":
        return ["door_leaf_left", "door_leaf_right"]
    return ["door_leaf"]


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject,
                      r: ResolvedIndustrialBlastDoorConfig) -> None:
    parts = {p.name for p in model.parts}
    wall = model.get_part("wall_frame")

    # Captured hinge: frame jamb tab wraps each door barrel on the pivot axis.
    if r.operation in _SWING_OPS:
        for leaf_name in _leaf_names(r):
            if leaf_name not in parts:
                continue
            leaf = model.get_part(leaf_name)
            for i in range(r.hinge_count):
                ctx.allow_overlap(wall, leaf, elem_a=f"hinge_tab_{leaf_name}_{i}",
                                  elem_b=f"hinge_barrel_{i}",
                                  reason="frame hinge lug wraps the knuckle barrel on the pivot axis")

    # Captured slide: hanger stems / trolleys ride in the head-rail channel.
    if r.operation == "slide" and "door_leaf" in parts:
        leaf = model.get_part("door_leaf")
        for i in range(2):
            for elem in (f"hanger_stem_{i}", f"trolley_{i}"):
                ctx.allow_overlap(wall, leaf, elem_a="head_rail", elem_b=elem,
                                  reason="hanger stem/trolley enters the head-rail channel to suspend the leaf")

    # Captured lift: leaf edge runners ride inside the C-channel guides.
    if r.operation == "vertical_lift" and "door_leaf" in parts:
        leaf = model.get_part("door_leaf")
        for i in range(2):
            ctx.allow_overlap(wall, leaf, elem_a=f"guide_channel_{i}", elem_b=f"edge_runner_{i}",
                              reason="leaf edge runner rides inside the C-channel guide rail")
            for k in range(2):
                ctx.allow_overlap(wall, leaf, elem_a=f"guide_flange_{i}_{k}", elem_b=f"edge_runner_{i}",
                                  reason="leaf edge runner captured between the C-channel flanges")

    # Control captured interfaces.
    if r.active_leaf in parts:
        leaf = model.get_part(r.active_leaf)
        if r.control in ("lever_handle", "handwheel") and "lever_handle" in parts:
            lever = model.get_part("lever_handle")
            for elem in ("handle_rose", "leaf_plate"):
                ctx.allow_overlap(leaf, lever, elem_a=elem, elem_b="spindle_hub",
                                  reason="handle spindle hub engages through the rose into the leaf bore")
        if r.control == "crash_bar" and "push_bar" in parts:
            push = model.get_part("push_bar")
            for i in range(2):
                ctx.allow_overlap(leaf, push, elem_a=f"bar_socket_{i}", elem_b=f"bracket_{i}",
                                  reason="crash-bar bracket slides into the door-face socket post")
                ctx.allow_overlap(leaf, push, elem_a=f"bar_socket_{i}", elem_b="bar_tube",
                                  reason="crash-bar tube seats against the door-face socket posts")
                ctx.allow_overlap(leaf, push, elem_a="leaf_plate", elem_b=f"bracket_{i}",
                                  reason="crash-bar bracket enters the leaf face when the bar is pushed in")


def _expect_operation(ctx, model, r) -> None:
    leaves = [p.name for p in model.parts if p.name.startswith("door_leaf")]
    if r.operation == "double_swing":
        ctx.check("two leaves present", len(leaves) == 2, details=str(leaves))
    else:
        ctx.check("one leaf present", len(leaves) == 1, details=str(leaves))

    if r.operation in _SWING_OPS:
        jn = "door_hinge" if r.operation == "single_swing" else "door_hinge_left"
        hinge = model.get_articulation(jn)
        ctx.check("operation joint revolute", hinge.articulation_type == ArticulationType.REVOLUTE)
        leaf = model.get_part(leaves[0] if r.operation == "single_swing" else "door_leaf_left")
        rest = ctx.part_world_aabb(leaf)
        with ctx.pose({hinge: min(1.3, r.swing_upper)}):
            swung = ctx.part_world_aabb(leaf)
        ok = rest is not None and swung is not None and swung[0][1] < rest[0][1] - 0.30
        ctx.check("leaf swings out toward viewer (-Y)", ok, details=f"rest={rest} swung={swung}")
    else:
        jn = "door_slide" if r.operation == "slide" else "door_lift"
        joint = model.get_articulation(jn)
        ctx.check("operation joint prismatic", joint.articulation_type == ArticulationType.PRISMATIC)
        leaf = model.get_part("door_leaf")
        rest = ctx.part_world_aabb(leaf)
        val = r.slide_travel * 0.8 if r.operation == "slide" else r.open_h * 0.8
        with ctx.pose({joint: val}):
            moved = ctx.part_world_aabb(leaf)
        ax = 0 if r.operation == "slide" else 2
        ok = rest is not None and moved is not None and (moved[0][ax] - rest[0][ax]) > 0.4
        ctx.check("leaf translates open", ok, details=f"axis={ax} rest={rest} moved={moved}")


def _expect_control(ctx, model, r) -> None:
    if r.control == "crash_bar":
        joint = model.get_articulation("push_bar")
        ctx.check("crash bar prismatic", joint.articulation_type == ArticulationType.PRISMATIC)
        push = model.get_part("push_bar")
        rest = ctx.part_world_aabb(push)
        with ctx.pose({joint: PUSH_TRAVEL}):
            pushed = ctx.part_world_aabb(push)
        ok = rest is not None and pushed is not None and (pushed[0][1] - rest[0][1]) > 0.01
        ctx.check("crash bar presses inward (+Y)", ok, details=f"rest={rest} pushed={pushed}")
        return

    joint = model.get_articulation("handle_spindle")
    ctx.check("control spindle revolute", joint.articulation_type == ArticulationType.REVOLUTE)
    lever = model.get_part("lever_handle")
    # wheel_rim is centred on the spin axis (invariant under rotation); measure
    # an off-axis spoke, which actually sweeps when the handwheel turns.
    elem = "wheel_spoke_0" if r.control == "handwheel" else "lever_tip"
    rest = ctx.part_element_world_aabb(lever, elem=elem)
    val = min(0.7, joint.motion_limits.upper) if joint.motion_limits else 0.7
    with ctx.pose({joint: val}):
        moved = ctx.part_element_world_aabb(lever, elem=elem)
    ca = None if rest is None else [(rest[0][i] + rest[1][i]) / 2.0 for i in range(3)]
    cb = None if moved is None else [(moved[0][i] + moved[1][i]) / 2.0 for i in range(3)]
    disp = 0.0 if ca is None or cb is None else math.dist(ca, cb)
    ctx.check(f"{r.control} actuator moves", disp > 0.02, details=f"displacement={disp:.4f}")


def run_industrial_blast_door_tests(
    model: ArticulatedObject,
    config: IndustrialBlastDoorConfig,
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

    _expect_operation(ctx, model, r)
    _expect_control(ctx, model, r)

    # Rule 5: dynamic collision across sampled joint poses.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "IndustrialBlastDoorConfig",
    "ResolvedIndustrialBlastDoorConfig",
    "Operation",
    "Control",
    "LeafForm",
    "BlastDoorPalette",
    "build_industrial_blast_door",
    "build_seeded_industrial_blast_door",
    "config_from_seed",
    "resolve_config",
    "run_industrial_blast_door_tests",
    "slot_choices_for_seed",
]


def _material_class_id(
    value: str,
    first_values: tuple[str, ...],
    first_id: str,
    second_id: str,
) -> str:
    return first_id if value in first_values else second_id
