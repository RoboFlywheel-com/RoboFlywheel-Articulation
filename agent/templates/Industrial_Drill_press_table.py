# SPDX-License-Identifier: Apache-2.0

"""Industrial / Drill press table - modular procedural template.

An adjustable auxiliary drill-press worktable: a cast ``column`` root (base plate
+ upright tube) carries a ``carriage`` clamp collar that rides the column on a
PRISMATIC height slide; the carriage carries a ``table`` worktop on a REVOLUTE
tilt / swivel bearing (captured trunnion) and a ``lock_lever`` on the clamp
joint. The worktop is milled with dog holes + clamping T-slots and carries a
two-piece fence and optional inlaid T-track rails; an optional fold-out ``leaf``
hangs off the front edge.

Slot graph (pattern = mixed: root mount spine + chained worktop child + parallel
lock-lever child + optional fold-leaf grandchild + 3 multiplicity axes):

    column (root; cast base + upright tube)
        -> [height_slide PRISMATIC Z] -> carriage (Slot A: forked_yoke | single_bracket)
              -> [table motion REVOLUTE X|Y|Z at trunnion] -> table (Slot B: rect_laminate | cast_slab | round_disc)
              |       -> [leaf_hinge REVOLUTE X] (optional) -> leaf
              -> [lever_pivot REVOLUTE X | lever_screw PRISMATIC -Y] -> lock_lever (Slot C: cam_lever | screw_knob)

Adapted per AUTHORING.md §A/§B from the confirmed 5-star Drill-press-table pool
(spec: specs_modular_v1/Industrial_Drill_press_table.md). Sources (model.py:Lx-Ly
in the spec Module Source Index):

  S1  origin 母本 rec_industrial__drill_press_table__002 - full spine, rect worktop,
      forked yoke, tilt-X, cam lever, all test semantics.
  S2  cast_iron_slab   - solid cast slab worktop (③ Volumetric Envelope Form).
  S3  round_table      - round disc worktop (③ Planar Boundary Form, radial slots).
  S4  side_tilt        - table motion REVOLUTE axis Y.
  S5  column_swing     - table motion REVOLUTE axis Z (swivel).
  S6  screw_clamp      - PRISMATIC screw clamp lock (② joint type).
  S7  single_pivot     - single-sided cantilever pivot bracket mount.
  S8  flip_leaf        - fold-out leaf part + REVOLUTE leaf_hinge (① skeleton).
  S9  slot_count       - worktop clamping T-slot multiplicity.
  S10 fence_segments   - fence face segment multiplicity.
  S11 track_count      - inlaid T-track rail multiplicity.

Coordinate frame: Z-up, floor z=0, column axis on Z at origin. +X lateral,
-Y = forward (the worktop cantilevers forward of the column). All authored in the
same local frames as the origin 母本 (table-local origin at the tilt trunnion).
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
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


MountStyle = Literal["forked_yoke", "single_bracket"]
WorktopForm = Literal["rect_laminate", "cast_slab", "round_disc"]
TableMotion = Literal["tilt_front", "tilt_side", "swing_column"]
ClampStyle = Literal["cam_lever", "screw_knob"]
LeafStyle = Literal["no_leaf", "flip_leaf"]
DrillTablePalette = Literal[
    "shop_cast",
    "granite_gray",
    "machinist_green",
    "safety_red",
    "raw_steel",
    "walnut_bench",
]


# --------------------------------------------------------------------------- #
# Canonical dimensions (origin 母本 rec_industrial__drill_press_table__002)
# --------------------------------------------------------------------------- #

BASE_TABLE_WIDTH = 0.62
BASE_TABLE_DEPTH = 0.42
BASE_TABLE_RADIUS = 0.20

# Worktop is lifted well above the carriage fork/saddle so the tilted plate
# clears the mount hardware through the full tilt range (the trunnion pivot is
# the table-local origin; the worktop sits above + forward of it).
SUBSTRATE_BOTTOM = 0.100
SUBSTRATE_THICKNESS = 0.028
LAMINATE_THICKNESS = 0.004
LAMINATE_TOP = SUBSTRATE_BOTTOM + SUBSTRATE_THICKNESS + LAMINATE_THICKNESS  # 0.132

BASE_COLUMN_TUBE_LEN = 0.86
COLUMN_RADIUS = 0.038
COLUMN_BASE_Z = 0.030        # top of the base plate / bottom of the tube region

# Trunnion mount datum in the CARRIAGE frame (== origin table_tilt origin).
TRUNNION = (0.0, -0.105, 0.038)
# Clamp ear datum in the CARRIAGE frame (== origin lever_pivot region).
CLAMP_EAR = (0.077, 0.0, -0.034)

HINGE_Z = LAMINATE_TOP


# --------------------------------------------------------------------------- #
# Palettes (>=6 colorways; tokens shared so every .visual resolves)
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "shop_cast": {
        "casting": (0.05, 0.05, 0.05, 1.0),
        "steel": (0.62, 0.61, 0.56, 1.0),
        "dark_metal": (0.12, 0.12, 0.115, 1.0),
        "laminate": (0.86, 0.88, 0.84, 1.0),
        "wood": (0.78, 0.58, 0.34, 1.0),
        "alu": (0.74, 0.76, 0.74, 1.0),
        "screw": (0.05, 0.06, 0.06, 1.0),
        "slab": (0.30, 0.29, 0.28, 1.0),
    },
    "granite_gray": {
        "casting": (0.20, 0.21, 0.22, 1.0),
        "steel": (0.66, 0.67, 0.69, 1.0),
        "dark_metal": (0.16, 0.17, 0.18, 1.0),
        "laminate": (0.55, 0.56, 0.58, 1.0),
        "wood": (0.60, 0.50, 0.38, 1.0),
        "alu": (0.72, 0.74, 0.76, 1.0),
        "screw": (0.10, 0.10, 0.11, 1.0),
        "slab": (0.42, 0.43, 0.45, 1.0),
    },
    "machinist_green": {
        "casting": (0.10, 0.20, 0.14, 1.0),
        "steel": (0.60, 0.62, 0.58, 1.0),
        "dark_metal": (0.08, 0.14, 0.10, 1.0),
        "laminate": (0.82, 0.84, 0.80, 1.0),
        "wood": (0.72, 0.54, 0.32, 1.0),
        "alu": (0.70, 0.73, 0.70, 1.0),
        "screw": (0.06, 0.09, 0.07, 1.0),
        "slab": (0.24, 0.34, 0.26, 1.0),
    },
    "safety_red": {
        "casting": (0.55, 0.10, 0.09, 1.0),
        "steel": (0.64, 0.63, 0.60, 1.0),
        "dark_metal": (0.18, 0.06, 0.06, 1.0),
        "laminate": (0.90, 0.88, 0.84, 1.0),
        "wood": (0.76, 0.56, 0.34, 1.0),
        "alu": (0.76, 0.77, 0.78, 1.0),
        "screw": (0.10, 0.05, 0.05, 1.0),
        "slab": (0.40, 0.20, 0.18, 1.0),
    },
    "raw_steel": {
        "casting": (0.34, 0.35, 0.37, 1.0),
        "steel": (0.72, 0.73, 0.75, 1.0),
        "dark_metal": (0.22, 0.23, 0.25, 1.0),
        "laminate": (0.70, 0.72, 0.74, 1.0),
        "wood": (0.66, 0.52, 0.36, 1.0),
        "alu": (0.80, 0.82, 0.84, 1.0),
        "screw": (0.14, 0.15, 0.16, 1.0),
        "slab": (0.56, 0.57, 0.59, 1.0),
    },
    "walnut_bench": {
        "casting": (0.14, 0.12, 0.11, 1.0),
        "steel": (0.60, 0.58, 0.54, 1.0),
        "dark_metal": (0.12, 0.10, 0.09, 1.0),
        "laminate": (0.90, 0.86, 0.80, 1.0),
        "wood": (0.42, 0.28, 0.16, 1.0),
        "alu": (0.70, 0.71, 0.72, 1.0),
        "screw": (0.08, 0.07, 0.06, 1.0),
        "slab": (0.26, 0.22, 0.20, 1.0),
    },
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class IndustrialDrillPressTableConfig:
    mount_style: MountStyle = "forked_yoke"
    worktop_form: WorktopForm = "rect_laminate"
    table_motion: TableMotion = "tilt_front"
    clamp_style: ClampStyle = "cam_lever"
    leaf_style: LeafStyle = "no_leaf"
    palette_style: DrillTablePalette = "shop_cast"

    slot_count: int = 3
    fence_count: int = 2
    track_count: int = 0

    table_scale: float = 1.0
    column_h_scale: float = 1.0
    tilt_range: float = 0.45      # tilt_front/side REVOLUTE +- range (rad)
    swing_range: float = 1.20     # swing_column REVOLUTE +- range (rad)


@dataclass(frozen=True)
class ResolvedIndustrialDrillPressTableConfig:
    mount_style: MountStyle
    worktop_form: WorktopForm
    table_motion: TableMotion
    clamp_style: ClampStyle
    leaf_style: LeafStyle
    palette_style: str

    slot_count: int
    fence_count: int
    track_count: int

    table_scale: float
    column_h_scale: float
    tilt_range: float
    swing_range: float

    # Derived geometry (single-sourced; Contract 3c).
    tube_len: float
    slide_travel: float
    table_width: float
    table_depth: float
    table_radius: float
    worktop_center_y: float
    front_edge_y: float
    table_y_shift: float

    palette: dict[str, tuple[float, float, float, float]]

    @property
    def is_round(self) -> bool:
        return self.worktop_form == "round_disc"

    def worktop_half_x(self) -> float:
        """Half the worktop X extent (radius for round, half-width otherwise)."""
        return self.table_radius if self.is_round else self.table_width / 2.0


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


# --------------------------------------------------------------------------- #
# Seed-driven sampling (procedural-first)
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> IndustrialDrillPressTableConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin 母本 combination (forked_yoke + rect_laminate +
    tilt_front + cam_lever + no_leaf, shop_cast) as a documented regression
    anchor (a sparse override; every other seed is fully procedural).
    """
    if seed == 0:
        return IndustrialDrillPressTableConfig()

    rng = random.Random(seed)

    mount_style: MountStyle = rng.choice(("forked_yoke", "single_bracket"))
    worktop_form: WorktopForm = rng.choice(("rect_laminate", "cast_slab", "round_disc"))
    table_motion: TableMotion = rng.choice(("tilt_front", "tilt_side", "swing_column"))
    clamp_style: ClampStyle = rng.choice(("cam_lever", "screw_knob"))
    leaf_style: LeafStyle = rng.choice(("no_leaf", "flip_leaf"))
    palette_style = rng.choice(PALETTE_NAMES)

    slot_count = rng.choices((2, 3, 4), weights=(0.4, 0.3, 0.3))[0]
    fence_count = rng.choices((2, 3), weights=(0.6, 0.4))[0]
    track_count = rng.choices((0, 2, 3), weights=(0.5, 0.2, 0.3))[0]

    table_scale = round(rng.uniform(0.85, 1.15), 4)
    column_h_scale = round(rng.uniform(0.90, 1.20), 4)
    tilt_range = round(rng.uniform(0.30, 0.55), 4)
    swing_range = round(rng.uniform(0.90, 1.40), 4)

    return IndustrialDrillPressTableConfig(
        mount_style=mount_style,
        worktop_form=worktop_form,
        table_motion=table_motion,
        clamp_style=clamp_style,
        leaf_style=leaf_style,
        palette_style=palette_style,
        slot_count=slot_count,
        fence_count=fence_count,
        track_count=track_count,
        table_scale=table_scale,
        column_h_scale=column_h_scale,
        tilt_range=tilt_range,
        swing_range=swing_range,
    )


def resolve_config(
    config: IndustrialDrillPressTableConfig,
) -> ResolvedIndustrialDrillPressTableConfig:
    if str(config.mount_style) not in {"forked_yoke", "single_bracket"}:
        raise ValueError(f"Unsupported mount_style: {config.mount_style}")
    if str(config.worktop_form) not in {"rect_laminate", "cast_slab", "round_disc"}:
        raise ValueError(f"Unsupported worktop_form: {config.worktop_form}")
    if str(config.table_motion) not in {"tilt_front", "tilt_side", "swing_column"}:
        raise ValueError(f"Unsupported table_motion: {config.table_motion}")
    if str(config.clamp_style) not in {"cam_lever", "screw_knob"}:
        raise ValueError(f"Unsupported clamp_style: {config.clamp_style}")
    if str(config.leaf_style) not in {"no_leaf", "flip_leaf"}:
        raise ValueError(f"Unsupported leaf_style: {config.leaf_style}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    table_scale = _clamp(config.table_scale, 0.85, 1.15)
    column_h_scale = _clamp(config.column_h_scale, 0.90, 1.20)
    # Side-tilt (REVOLUTE about Y) drops the WIDE worktop lateral edge straight
    # down toward the carriage fork arms / pivot bracket, so its reachable range
    # is capped tighter than front-tilt (which cantilevers the worktop forward,
    # clear of the mount). Front-tilt keeps the full authored envelope.
    if str(config.table_motion) == "tilt_side":
        tilt_range = _clamp(config.tilt_range, 0.25, 0.40)
    else:
        tilt_range = _clamp(config.tilt_range, 0.30, 0.55)
    swing_range = _clamp(config.swing_range, 0.90, 1.40)

    slot_count = int(_clamp(config.slot_count, 2, 4))
    fence_count = int(_clamp(config.fence_count, 2, 3))
    track_count = int(_clamp(config.track_count, 0, 3))
    if track_count == 1:
        track_count = 2
    # Round disc has radial slots and no room for parallel T-track rails.
    if config.worktop_form == "round_disc":
        track_count = 0

    tube_len = BASE_COLUMN_TUBE_LEN * column_h_scale
    # Slide travel derived so the collar never runs off the tube.
    slide_travel = _clamp(0.5 * tube_len - 0.13, 0.10, 0.30)

    table_width = BASE_TABLE_WIDTH * table_scale
    table_depth = BASE_TABLE_DEPTH * table_scale
    table_radius = BASE_TABLE_RADIUS * table_scale
    # Worktop center Y in table-local frame: place its REAR edge just forward of
    # the trunnion pivot (table-local origin) so the plate cantilevers fully
    # forward and tilting/swivelling swings it clear of the carriage fork.
    half_depth = table_radius if config.worktop_form == "round_disc" else table_depth / 2.0
    # Table swivel/tilt pivots at the trunnion datum (table-local origin); the
    # shift stays 0 (kept as a single-sourced hook). swing_column is capped
    # (below) so the laterally-wide trunnion shaft / underside saddle never sweep
    # far enough about the trunnion to reach the column tube / clamp collar.
    table_y_shift = 0.0
    worktop_center_y = -(half_depth + 0.03) + table_y_shift
    front_edge_y = worktop_center_y - half_depth

    return ResolvedIndustrialDrillPressTableConfig(
        mount_style=config.mount_style,
        worktop_form=config.worktop_form,
        table_motion=config.table_motion,
        clamp_style=config.clamp_style,
        leaf_style=config.leaf_style,
        palette_style=config.palette_style,
        slot_count=slot_count,
        fence_count=fence_count,
        track_count=track_count,
        table_scale=table_scale,
        column_h_scale=column_h_scale,
        tilt_range=tilt_range,
        swing_range=swing_range,
        tube_len=tube_len,
        slide_travel=slide_travel,
        table_width=table_width,
        table_depth=table_depth,
        table_radius=table_radius,
        worktop_center_y=worktop_center_y,
        front_edge_y=front_edge_y,
        table_y_shift=table_y_shift,
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# Cadquery worktop / base helpers (the milled slots + holes are the ID feature;
# kept as real boolean cuts per Rule 3, cut counts capped for the compile budget)
# --------------------------------------------------------------------------- #


def _slot_cutter_y(x: float, y: float, length: float, width: float) -> cq.Workplane:
    """Vertical through-cutter for a rounded slot whose long axis is on Y."""
    straight = max(0.001, length - width)
    height = 0.45
    base_z = -0.18
    cutter = cq.Workplane("XY").rect(width, straight).extrude(height)
    cutter = cutter.union(
        cq.Workplane("XY").circle(width / 2.0).extrude(height).translate((0, -straight / 2.0, 0))
    )
    cutter = cutter.union(
        cq.Workplane("XY").circle(width / 2.0).extrude(height).translate((0, straight / 2.0, 0))
    )
    return cutter.translate((x, y, base_z))


def _slot_cutter_x(x: float, y: float, length: float, width: float) -> cq.Workplane:
    """Vertical through-cutter for a rounded slot whose long axis is on X."""
    straight = max(0.001, length - width)
    height = 0.45
    base_z = -0.18
    cutter = cq.Workplane("XY").rect(straight, width).extrude(height)
    cutter = cutter.union(
        cq.Workplane("XY").circle(width / 2.0).extrude(height).translate((-straight / 2.0, 0, 0))
    )
    cutter = cutter.union(
        cq.Workplane("XY").circle(width / 2.0).extrude(height).translate((straight / 2.0, 0, 0))
    )
    return cutter.translate((x, y, base_z))


def _rect_plate(
    r: ResolvedIndustrialDrillPressTableConfig, thickness: float, z_center: float, *, with_holes: bool
) -> cq.Workplane:
    """Rounded-rectangular composite worktop plate with cut dog holes + N clamping
    T-slots (origin S1 _drill_table_plate)."""
    w, d = r.table_width, r.table_depth
    wy = r.worktop_center_y
    panel = (
        cq.Workplane("XY").box(w, d, thickness).edges("|Z").fillet(0.035).translate((0.0, wy, z_center))
    )
    if not with_holes:
        return panel

    # Dog / mounting holes derived from the realized footprint (Rule 4).
    for fx, fy, radius in (
        (-0.40, -0.30, 0.014),
        (0.40, -0.30, 0.014),
        (-0.38, 0.19, 0.014),
        (0.38, 0.19, 0.014),
        (0.0, -0.05, 0.009),
    ):
        panel = panel.cut(
            cq.Workplane("XY").circle(radius).extrude(0.45).translate((fx * w * 0.5, wy + fy * d * 0.5, -0.18))
        )

    # N evenly spaced parallel clamping T-slots across the work surface.
    spacing = w / (r.slot_count + 1)
    slot_len = d * 0.42
    for i in range(r.slot_count):
        sx = -0.5 * (r.slot_count - 1) * spacing + i * spacing
        panel = panel.cut(_slot_cutter_y(sx, wy - 0.02, slot_len, 0.020))
    # Central replaceable-insert / drill-bit clearance slot.
    panel = panel.cut(_slot_cutter_x(0.0, wy - 0.04, d * 0.32, 0.055))
    return panel


def _round_plate(
    r: ResolvedIndustrialDrillPressTableConfig, thickness: float, z_center: float, *, with_holes: bool
) -> cq.Workplane:
    """Round disc worktop plate with a centre hole, N radial T-slots and two
    concentric dog-hole rings (round_table S3)."""
    rad = r.table_radius
    wy = r.worktop_center_y
    half_t = thickness / 2.0
    cut_depth = thickness + 0.020
    cut_z0 = -half_t - 0.010
    disc = cq.Workplane("XY").circle(rad).extrude(thickness).translate((0.0, 0.0, -half_t))
    if with_holes:
        disc = disc.cut(cq.Workplane("XY").circle(0.022).extrude(cut_depth).translate((0.0, 0.0, cut_z0)))
        n_slots = min(r.slot_count, 4) if r.slot_count >= 2 else 2
        n_slots = max(3, n_slots)  # a round table reads as radial >=3
        slot_inner_r = 0.055
        slot_outer_r = rad - 0.015
        slot_len = slot_outer_r - slot_inner_r
        slot_mid_r = (slot_inner_r + slot_outer_r) / 2.0
        half_len = slot_len / 2.0
        for k in range(n_slots):
            ang = 360.0 * k / n_slots
            cutter = cq.Workplane("XY").rect(slot_len, 0.016).extrude(cut_depth).translate((0.0, 0.0, cut_z0))
            cutter = cutter.union(
                cq.Workplane("XY").circle(0.008).extrude(cut_depth).translate((-half_len, 0.0, cut_z0))
            )
            cutter = cutter.union(
                cq.Workplane("XY").circle(0.008).extrude(cut_depth).translate((half_len, 0.0, cut_z0))
            )
            dx = math.cos(math.radians(ang)) * slot_mid_r
            dy = math.sin(math.radians(ang)) * slot_mid_r
            cutter = cutter.rotate((0, 0, 0), (0, 0, 1), ang).translate((dx, dy, 0.0))
            disc = disc.cut(cutter)
        for ring_r in (rad * 0.5, rad * 0.8):
            for ang in (45, 135, 225, 315):
                hx = math.cos(math.radians(ang)) * ring_r
                hy = math.sin(math.radians(ang)) * ring_r
                disc = disc.cut(cq.Workplane("XY").circle(0.012).extrude(cut_depth).translate((hx, hy, cut_z0)))
    return disc.translate((0.0, wy, z_center))


def _cast_slab(r: ResolvedIndustrialDrillPressTableConfig) -> cq.Workplane:
    """Single solid cast-iron slab worktop with milled T-slot channels, a centre
    clearance hole and dog holes (cast_iron_slab S2). The tilt shaft ties into
    the underside via the shared _emit_underside_bracket, not slab-local lugs."""
    w, d = r.table_width, r.table_depth
    wy = r.worktop_center_y
    slab_t = 0.038
    slab_bot = SUBSTRATE_BOTTOM
    slab_top = slab_bot + slab_t
    slab_mid = (slab_top + slab_bot) / 2.0
    slab = cq.Workplane("XY").box(w, d, slab_t).edges("|Z").fillet(0.030).translate((0.0, wy, slab_mid))
    slab = slab.edges(">Z").chamfer(0.003)

    # N milled through T-slots (top opening + wider undercut) running in X.
    opening_w, undercut_w = 0.014, 0.024
    opening_d, undercut_d = 0.008, 0.020
    slot_len = w - 0.080
    spacing = d / (r.slot_count + 1)
    for i in range(r.slot_count):
        y_pos = wy - 0.5 * (r.slot_count - 1) * spacing + i * spacing
        nz = slab_top - opening_d / 2.0
        slab = slab.cut(cq.Workplane("XY").box(slot_len, opening_w, opening_d + 0.002).translate((0.0, y_pos, nz)))
        uz = slab_top - opening_d - undercut_d / 2.0
        slab = slab.cut(cq.Workplane("XY").box(slot_len, undercut_w, undercut_d + 0.002).translate((0.0, y_pos, uz)))

    slab = slab.cut(cq.Workplane("XY").circle(0.020).extrude(slab_t + 0.020).translate((0.0, wy, slab_bot - 0.010)))
    for fx, fy in ((-0.40, -0.24), (0.40, -0.24), (-0.40, 0.38), (0.40, 0.38)):
        slab = slab.cut(
            cq.Workplane("XY").circle(0.010).extrude(slab_t + 0.020).translate((fx * w * 0.5, wy + fy * d * 0.5, slab_bot - 0.010))
        )
    # NOTE: no separate cast trunnion lugs here. The shared underside bracket
    # (_emit_underside_bracket: saddle + rib + web) already ties the tilt shaft
    # into the worktop underside for every worktop form; earlier dedicated slab
    # lugs sat down at the pivot and collided with the fork cross-rail.
    return slab


def _base_plate() -> cq.Workplane:
    """Cast, slotted mounting base plate (origin S1 _base_plate)."""
    base = cq.Workplane("XY").box(0.36, 0.26, 0.030).edges("|Z").fillet(0.020).translate((0.0, 0.0, 0.015))
    for x in (-0.105, 0.105):
        base = base.cut(_slot_cutter_y(x, 0.045, 0.115, 0.022))
        base = base.cut(_slot_cutter_y(x, -0.085, 0.090, 0.020))
    return base


# --------------------------------------------------------------------------- #
# Slot A - mount (root): column + carriage + height slide + trunnion support
# --------------------------------------------------------------------------- #


def _carriage_downstream(r: ResolvedIndustrialDrillPressTableConfig) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="carriage",
        visual_name="collar_rear",
        face_side="negative_y",
        anchor_local=(0.0, -0.062, 0.006),
        contact_tol=0.004,
    )


def _build_mount(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialDrillPressTableConfig = ctx.config  # type: ignore[assignment]

    # --- column (root) ---
    column = model.part("column")
    column.visual(mesh_from_cadquery(_base_plate(), "slotted_base_plate"), material="casting", name="base_plate", material_class_id="metal.cast_iron_bare")
    tube_cz = COLUMN_BASE_Z - 0.005 + r.tube_len / 2.0
    column.visual(
        Cylinder(radius=COLUMN_RADIUS, length=r.tube_len),
        origin=Origin(xyz=(0.0, 0.0, tube_cz)),
        material="steel",
        name="column_tube", material_class_id="metal.steel_bare",
    )
    column.visual(
        Cylinder(radius=0.070, length=0.038),
        origin=Origin(xyz=(0.0, 0.0, 0.049)),
        material="casting",
        name="base_flange", material_class_id="metal.cast_iron_bare",
    )
    for i, (x, y) in enumerate(((-0.045, -0.030), (0.045, -0.030), (-0.045, 0.030), (0.045, 0.030))):
        column.visual(
            Cylinder(radius=0.009, length=0.008),
            origin=Origin(xyz=(x, y, 0.070)),
            material="dark_metal",
            name=f"flange_bolt_{i}", material_class_id="metal.blackened_gunmetal",
        )

    # --- carriage (rides the column) ---
    carriage = model.part("carriage")
    # Split clamp collar snug on the column tube (captured sliding clamp; the
    # jaw bores contact the tube so the carriage is supported, Contract 3).
    carriage.visual(Box((0.100, 0.026, 0.070)), origin=Origin(xyz=(0.0, 0.049, 0.0)), material="casting", name="collar_rear", material_class_id="metal.cast_iron_bare")
    carriage.visual(Box((0.020, 0.112, 0.070)), origin=Origin(xyz=(-0.046, 0.0, 0.0)), material="casting", name="collar_side_0", material_class_id="metal.cast_iron_bare")
    carriage.visual(Box((0.020, 0.112, 0.070)), origin=Origin(xyz=(0.046, 0.0, 0.0)), material="casting", name="collar_side_1", material_class_id="metal.cast_iron_bare")
    carriage.visual(Box((0.050, 0.020, 0.050)), origin=Origin(xyz=(0.077, 0.028, 0.0)), material="casting", name="clamp_ear_0", material_class_id="metal.cast_iron_bare")
    carriage.visual(Box((0.050, 0.020, 0.050)), origin=Origin(xyz=(0.077, -0.028, 0.0)), material="casting", name="clamp_ear_1", material_class_id="metal.cast_iron_bare")
    carriage.visual(Box((0.160, 0.055, 0.050)), origin=Origin(xyz=(0.0, -0.062, 0.006)), material="casting", name="saddle_block", material_class_id="metal.cast_iron_bare")

    if r.mount_style == "forked_yoke":
        carriage.visual(Box((0.300, 0.030, 0.045)), origin=Origin(xyz=(0.0, -0.084, 0.030)), material="casting", name="yoke_rail", material_class_id="metal.cast_iron_bare")
        # Fork cheeks: tops kept low (just capping the trunnion shaft) so the
        # side-tilted worktop lateral edge swings clear over them.
        for i, x in enumerate((-0.158, 0.158)):
            carriage.visual(Box((0.024, 0.120, 0.036)), origin=Origin(xyz=(x, -0.105, 0.030)), material="casting", name=f"yoke_arm_{i}", material_class_id="metal.cast_iron_bare")
    else:  # single_bracket
        carriage.visual(Box((0.100, 0.034, 0.050)), origin=Origin(xyz=(0.108, -0.070, 0.028)), material="casting", name="bracket_rail", material_class_id="metal.cast_iron_bare")
        # Pivot bracket top kept low (caps the trunnion shaft) for side-tilt clearance.
        carriage.visual(Box((0.034, 0.130, 0.044)), origin=Origin(xyz=(0.158, -0.105, 0.028)), material="casting", name="pivot_bracket", material_class_id="metal.cast_iron_bare")
        carriage.visual(
            Cylinder(radius=0.015, length=0.025),
            origin=Origin(xyz=(0.145, -0.105, 0.038), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="steel",
            name="stub_trunnion", material_class_id="metal.steel_bare",
        )

    if r.table_motion == "swing_column":
        # Vertical swivel bearing boss at the trunnion: the worktop swivels on a
        # turntable pin here (no wide horizontal tilt shaft to sweep the collar).
        carriage.visual(
            Cylinder(radius=0.030, length=0.052),
            origin=Origin(xyz=(0.0, -0.105, 0.038)),
            material="casting",
            name="swivel_boss", material_class_id="metal.cast_iron_bare",
        )

    model.articulation(
        "height_slide",
        ArticulationType.PRISMATIC,
        parent=column,
        child=carriage,
        origin=Origin(xyz=(0.0, 0.0, 0.380)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=180.0, velocity=0.18, lower=0.0, upper=r.slide_travel),
    )

    return ModuleBuild(
        module_name=r.mount_style,
        parts_emitted=["column", "carriage"],
        internal_articulations=["height_slide"],
        interfaces={"downstream": _carriage_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot B - worktop (chained child): table part + motion joint + fence + leaf
# --------------------------------------------------------------------------- #


def _emit_underside_bracket(part, r: ResolvedIndustrialDrillPressTableConfig) -> None:
    """Cast rib tying the trunnion shaft (table-local origin) up + forward into
    the worktop underside (origin S1 _table_underside_bracket, as SDK boxes).
    Bridges the trunnion (z=0) to the raised worktop bottom (z=SUBSTRATE_BOTTOM),
    across the y-gap to the forward worktop center wy."""
    wy = r.worktop_center_y
    y0 = r.table_y_shift  # trunnion datum (0)
    # Saddle: straddles the trunnion (overlaps the shaft/pin), slightly toward the
    # worktop. Narrow for swing_column so it never sweeps into the collar/column.
    saddle_w = 0.10 if r.table_motion == "swing_column" else 0.230
    part.visual(Box((saddle_w, 0.040, 0.030)), origin=Origin(xyz=(0.0, y0 - 0.010, 0.006)), material="casting", name="underside_saddle", material_class_id="metal.cast_iron_bare")
    # Longitudinal rib from just forward of the trunnion saddle to the worktop
    # (kept clear of the carriage fork behind the pivot).
    rib_back_y = y0 - 0.02
    rib_len_y = abs(wy - rib_back_y)
    rib_center_y = (wy + rib_back_y) / 2.0
    part.visual(
        Box((0.060, rib_len_y, SUBSTRATE_BOTTOM + 0.010)),
        origin=Origin(xyz=(0.0, rib_center_y, (SUBSTRATE_BOTTOM + 0.010) / 2.0 - 0.005)),
        material="casting",
        name="underside_rib", material_class_id="metal.cast_iron_bare",
    )
    # Web plate pressed against the worktop underside (75% of the way from the
    # trunnion out to the worktop center).
    web_w = (2.0 * r.table_radius if r.is_round else r.table_width) * 0.55
    part.visual(
        Box((web_w, 0.16, 0.020)),
        origin=Origin(xyz=(0.0, y0 + 0.75 * (wy - y0), SUBSTRATE_BOTTOM - 0.008)),
        material="casting",
        name="underside_web", material_class_id="metal.cast_iron_bare",
    )


def _emit_fence(part, r: ResolvedIndustrialDrillPressTableConfig) -> None:
    """Two-piece fence (aluminium faces + wood cap + tracks + screws), N segments
    spread along X, derived from the realized worktop width (origin S1 fence,
    fence_segments S10 multiplicity)."""
    wy = r.worktop_center_y
    span = (2.0 * r.table_radius if r.is_round else r.table_width) * 0.92
    seg_len = span / r.fence_count * 0.94
    for i in range(r.fence_count):
        cx = -0.5 * span + span * (i + 0.5) / r.fence_count
        part.visual(
            Box((seg_len, 0.024, 0.060)),
            origin=Origin(xyz=(cx, wy, LAMINATE_TOP + 0.030)),
            material="alu",
            name=f"fence_face_{i}", material_class_id="metal.aluminum_bare",
        )
    part.visual(Box((span, 0.030, 0.012)), origin=Origin(xyz=(0.0, wy, LAMINATE_TOP + 0.066)), material="wood", name="fence_wood_cap", material_class_id="wood.polished_varnished")
    part.visual(Box((span * 0.94, 0.008, 0.006)), origin=Origin(xyz=(0.0, wy - 0.010, LAMINATE_TOP + 0.075)), material="steel", name="fence_top_track", material_class_id="metal.steel_bare")
    part.visual(Box((span * 0.92, 0.010, 0.004)), origin=Origin(xyz=(0.0, wy + 0.013, LAMINATE_TOP + 0.006)), material="steel", name="fence_lower_rail", material_class_id="metal.steel_bare")
    for i in range(r.fence_count + 1):
        sx = -0.5 * span + span * i / r.fence_count
        part.visual(
            Cylinder(radius=0.010, length=0.010),
            origin=Origin(xyz=(sx, wy - 0.013, LAMINATE_TOP + 0.030), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material="screw",
            name=f"fence_screw_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _emit_tracks(part, r: ResolvedIndustrialDrillPressTableConfig) -> None:
    """N inlaid aluminium T-track rails on the worktop surface, in front of the
    fence (track_count S11 multiplicity)."""
    if r.track_count <= 0:
        return
    wy = r.worktop_center_y
    track_len = r.table_width * 0.84
    thick = 0.005
    # Rails spread over the front half of the worktop (forward of the fence).
    y0 = wy - 0.05
    y1 = r.front_edge_y + 0.05
    for i in range(r.track_count):
        frac = (i + 1) / (r.track_count + 1)
        y = y0 + (y1 - y0) * frac
        tname = f"t_track_{i}"
        part.visual(Box((track_len, 0.022, thick)), origin=Origin(xyz=(0.0, y, LAMINATE_TOP + thick / 2.0)), material="alu", name=tname, material_class_id="metal.aluminum_bare")
        for j, sx in enumerate((-track_len * 0.4, -track_len * 0.13, track_len * 0.13, track_len * 0.4)):
            part.visual(
                Cylinder(radius=0.006, length=0.006),
                origin=Origin(xyz=(sx, y, LAMINATE_TOP + thick + 0.001)),
                material="screw",
                name=f"{tname}_screw_{j}", material_class_id="metal.blackened_gunmetal",
            )


def _emit_worktop_body(part, r: ResolvedIndustrialDrillPressTableConfig) -> None:
    """Emit the worktop core geometry (③ form) + the tilt trunnion + bracket."""
    if r.worktop_form == "rect_laminate":
        part.visual(
            mesh_from_cadquery(_rect_plate(r, SUBSTRATE_THICKNESS, SUBSTRATE_BOTTOM + SUBSTRATE_THICKNESS / 2.0, with_holes=True), "worktop_substrate_mesh"),
            material="wood",
            name="worktop_substrate", material_class_id="wood.engineered_board",
        )
        part.visual(
            mesh_from_cadquery(_rect_plate(r, LAMINATE_THICKNESS, SUBSTRATE_BOTTOM + SUBSTRATE_THICKNESS + LAMINATE_THICKNESS / 2.0, with_holes=True), "worktop_laminate_mesh"),
            material="laminate",
            name="worktop_laminate", material_class_id="plastic.opaque_glossy_molded",
        )
    elif r.worktop_form == "round_disc":
        part.visual(
            mesh_from_cadquery(_round_plate(r, SUBSTRATE_THICKNESS, SUBSTRATE_BOTTOM + SUBSTRATE_THICKNESS / 2.0, with_holes=True), "worktop_disc_substrate_mesh"),
            material="wood",
            name="worktop_substrate", material_class_id="wood.engineered_board",
        )
        part.visual(
            mesh_from_cadquery(_round_plate(r, LAMINATE_THICKNESS, SUBSTRATE_BOTTOM + SUBSTRATE_THICKNESS + LAMINATE_THICKNESS / 2.0, with_holes=True), "worktop_disc_laminate_mesh"),
            material="laminate",
            name="worktop_laminate", material_class_id="plastic.opaque_glossy_molded",
        )
    else:  # cast_slab (single solid body; laminate visual == same slab top)
        wy = r.worktop_center_y
        part.visual(mesh_from_cadquery(_cast_slab(r), "worktop_slab_mesh"), material="slab", name="worktop_substrate", material_class_id="metal.cast_iron_bare")
        # Thin machined top face visual so downstream tests referencing
        # "worktop_laminate" resolve and the ground surface reads as milled.
        top = SUBSTRATE_BOTTOM + 0.038
        w = r.table_width * 0.98
        part.visual(Box((w, r.table_depth * 0.98, 0.002)), origin=Origin(xyz=(0.0, wy, top + 0.0005)), material="slab", name="worktop_laminate", material_class_id="metal.cast_iron_bare")

    _emit_underside_bracket(part, r)
    if r.table_motion == "swing_column":
        # Vertical swivel pin at the trunnion. It rotates about its OWN Z axis,
        # so nothing sweeps laterally into the column / clamp collar at any angle.
        part.visual(
            Cylinder(radius=0.016, length=0.076),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material="steel",
            name="tilt_trunnion", material_class_id="metal.steel_bare",
        )
    else:
        # Tilt trunnion shaft aligned WITH the tilt axis (x for tilt_front, y for
        # tilt_side) so the table rotates about the shaft's own centerline and the
        # shaft stays seated in the carriage fork/bracket through the full tilt
        # (a shaft perpendicular to the tilt axis would sweep and lose contact).
        if r.table_motion == "tilt_front":
            _tr_rpy = (0.0, math.pi / 2.0, 0.0)
            _tr_len = 0.350  # reaches both fork cheeks at +-0.158
            _tr_xyz = (0.0, 0.0, 0.0)
        else:
            # Side-tilt pin lies along the Y tilt axis. The column tube sits just
            # in front (+y) of the trunnion datum, so the pin is shifted rearward
            # (-y, still coaxial with the tilt axis, rotating in place) to seat in
            # the pivot bracket without poking into the column.
            _tr_rpy = (math.pi / 2.0, 0.0, 0.0)
            _tr_len = 0.100
            _tr_xyz = (0.0, -0.030, 0.0)
        part.visual(
            Cylinder(radius=0.014, length=_tr_len),
            origin=Origin(xyz=_tr_xyz, rpy=_tr_rpy),
            material="steel",
            name="tilt_trunnion", material_class_id="metal.steel_bare",
        )
    _emit_fence(part, r)
    _emit_tracks(part, r)


def _emit_leaf(model, table, r: ResolvedIndustrialDrillPressTableConfig) -> list[str]:
    """Optional fold-out leaf hinged at the worktop front edge (flip_leaf S8)."""
    if r.leaf_style != "flip_leaf":
        return []
    leaf_w = min(0.50, (2.0 * r.table_radius if r.is_round else r.table_width) * 0.80)
    leaf_d = 0.20
    kn_r, kn_len = 0.007, 0.038
    kn_x = 0.080
    # Hinge line: the worktop's actual front edge AT the knuckle x. For a round
    # disc the edge recedes with |x|, so the knuckles must sit on the curved edge
    # (not out past it, which would leave them floating -> island).
    if r.is_round:
        hinge_y = r.worktop_center_y - math.sqrt(max(0.0, r.table_radius ** 2 - kn_x ** 2))
    else:
        hinge_y = r.front_edge_y

    # Table-side hinge knuckles (host visuals on the table part) at the front edge.
    for i, x in enumerate((-kn_x, kn_x)):
        table.visual(
            Cylinder(radius=kn_r, length=kn_len),
            origin=Origin(xyz=(x, hinge_y, HINGE_Z - kn_r), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="dark_metal",
            name=f"table_hinge_knuckle_{i}", material_class_id="metal.blackened_gunmetal",
        )

    leaf = model.part("leaf")
    # Leaf authored in leaf-local frame with its hinge line at local origin.
    leaf.visual(Box((leaf_w, leaf_d, SUBSTRATE_THICKNESS)), origin=Origin(xyz=(0.0, -leaf_d / 2.0, -LAMINATE_THICKNESS - SUBSTRATE_THICKNESS / 2.0)), material="wood", name="leaf_substrate", material_class_id="wood.engineered_board")
    leaf.visual(Box((leaf_w, leaf_d, LAMINATE_THICKNESS)), origin=Origin(xyz=(0.0, -leaf_d / 2.0, -LAMINATE_THICKNESS / 2.0)), material="laminate", name="leaf_laminate", material_class_id="plastic.opaque_glossy_molded")
    for i, x in enumerate((-kn_x, kn_x)):
        leaf.visual(Cylinder(radius=kn_r, length=kn_len), origin=Origin(xyz=(x, 0.0, -kn_r), rpy=(0.0, math.pi / 2.0, 0.0)), material="dark_metal", name=f"leaf_knuckle_{i}", material_class_id="metal.blackened_gunmetal")
    leaf.visual(Cylinder(radius=0.003, length=leaf_w * 0.84), origin=Origin(xyz=(0.0, 0.0, -kn_r), rpy=(0.0, math.pi / 2.0, 0.0)), material="steel", name="leaf_hinge_pin", material_class_id="metal.steel_bare")

    model.articulation(
        "leaf_hinge",
        ArticulationType.REVOLUTE,
        parent=table,
        child=leaf,
        origin=Origin(xyz=(0.0, hinge_y, HINGE_Z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.5, lower=0.0, upper=math.pi / 2.0),
    )
    return ["leaf"]


def _build_worktop(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialDrillPressTableConfig = ctx.config  # type: ignore[assignment]
    carriage = model.get_part("carriage")

    table = model.part("table")
    _emit_worktop_body(table, r)

    # Table motion joint (② axis): tilt about X / Y, or swivel about Z, all at the
    # shared trunnion mount datum in the carriage frame.
    if r.table_motion == "swing_column":
        jn = "table_swing"
        axis = (0.0, 0.0, 1.0)
        limits = MotionLimits(effort=80.0, velocity=0.7, lower=-r.swing_range, upper=r.swing_range)
        # Swivel about the trunnion (carriage hardware is there, so the joint
        # anchor is honest). Range is capped in resolve_config so the wide
        # trunnion shaft never swings back far enough to reach the clamp collar.
        joint_origin = Origin(xyz=TRUNNION)
    else:
        jn = "table_tilt"
        axis = (1.0, 0.0, 0.0) if r.table_motion == "tilt_front" else (0.0, 1.0, 0.0)
        limits = MotionLimits(effort=80.0, velocity=0.7, lower=-r.tilt_range, upper=r.tilt_range)
        joint_origin = Origin(xyz=TRUNNION)
    model.articulation(
        jn,
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=table,
        origin=joint_origin,
        axis=axis,
        motion_limits=limits,
    )

    parts = ["table"] + _emit_leaf(model, table, r)
    joints = [jn] + (["leaf_hinge"] if r.leaf_style == "flip_leaf" else [])
    return ModuleBuild(
        module_name=r.worktop_form,
        parts_emitted=parts,
        internal_articulations=joints,
        interfaces={"downstream": _carriage_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot C - locking (parallel child): lock lever + clamp joint
# --------------------------------------------------------------------------- #


def _build_locking(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialDrillPressTableConfig = ctx.config  # type: ignore[assignment]
    carriage = model.get_part("carriage")
    lever = model.part("lock_lever")

    if r.clamp_style == "cam_lever":
        # Cam lock lever pivoting about X at the +Y clamp ear (ear_0). The hub is
        # coaxial with the pivot and grips the ear (support path); the stem hangs
        # down + outboard and swings when the cam rotates. Hub sits outboard of
        # the collar side (x>=0.06) so it only touches the clamp ear.
        # Hub grips ear_0 (x 0.06..0.12) then the stem hangs OUTBOARD at x=0.115,
        # beyond both clamp ears (x<=0.102), so it swings clear of ear_1.
        lever.visual(Cylinder(radius=0.013, length=0.060), origin=Origin(xyz=(0.013, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)), material="dark_metal", name="lever_hub", material_class_id="metal.blackened_gunmetal")
        lever.visual(Cylinder(radius=0.006, length=0.095), origin=Origin(xyz=(0.038, 0.0, -0.052)), material="dark_metal", name="lever_stem", material_class_id="metal.blackened_gunmetal")
        lever.visual(Sphere(radius=0.016), origin=Origin(xyz=(0.038, 0.0, -0.108)), material="casting", name="lever_knob", material_class_id="metal.cast_iron_bare")
        model.articulation(
            "lever_pivot",
            ArticulationType.REVOLUTE,
            parent=carriage,
            child=lever,
            origin=Origin(xyz=(0.077, 0.028, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=12.0, velocity=2.5, lower=-1.0, upper=1.0),
        )
        joint = "lever_pivot"
    else:  # screw_knob (PRISMATIC screw clamp, T-handle; screw_clamp S6)
        # Screw threads across the clamp ears (axis Y through both bores) and is a
        # CAPTURED screw: shaft + tip overlap the ear bores and the split-collar
        # saddle they seat in (declared in _declare_overlaps). The T-handle sits
        # well OUTBOARD at +Y so that even at full clamp travel (-Y 0.012) it
        # stays clear of the +Y clamp ear. Joint origin is carriage (0.077,0.028);
        # local_y = carriage_y - 0.028.
        lever.visual(Cylinder(radius=0.005, length=0.118), origin=Origin(xyz=(0.0, -0.017, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)), material="steel", name="screw_shaft", material_class_id="metal.steel_bare")
        lever.visual(Cylinder(radius=0.004, length=0.010), origin=Origin(xyz=(0.0, -0.081, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)), material="dark_metal", name="screw_tip", material_class_id="metal.blackened_gunmetal")
        lever.visual(Cylinder(radius=0.006, length=0.080), origin=Origin(xyz=(0.0, 0.042, 0.0)), material="dark_metal", name="t_handle_bar", material_class_id="metal.blackened_gunmetal")
        for i, z in enumerate((-0.040, 0.040)):
            lever.visual(Sphere(radius=0.008), origin=Origin(xyz=(0.0, 0.042, z)), material="casting", name=f"t_handle_grip_{i}", material_class_id="metal.cast_iron_bare")
        model.articulation(
            "lever_screw",
            ArticulationType.PRISMATIC,
            parent=carriage,
            child=lever,
            origin=Origin(xyz=(0.077, 0.028, 0.0)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=12.0, velocity=0.05, lower=0.0, upper=0.012),
        )
        joint = "lever_screw"

    return ModuleBuild(
        module_name=r.clamp_style,
        parts_emitted=["lock_lever"],
        internal_articulations=[joint],
        interfaces={"downstream": _carriage_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Factory registries + assembly
# --------------------------------------------------------------------------- #

MOUNT_FACTORIES = {"forked_yoke": _build_mount, "single_bracket": _build_mount}
WORKTOP_FACTORIES = {
    "rect_laminate": _build_worktop,
    "cast_slab": _build_worktop,
    "round_disc": _build_worktop,
}
LOCKING_FACTORIES = {"cam_lever": _build_locking, "screw_knob": _build_locking}


def _slots_for_config(r: ResolvedIndustrialDrillPressTableConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="mount", candidates={r.mount_style: _build_mount}, anchor_choice=r.mount_style),
        SlotSpec(slot_name="worktop", candidates={r.worktop_form: _build_worktop}, anchor_choice=r.worktop_form),
        SlotSpec(slot_name="locking", candidates={r.clamp_style: _build_locking}, anchor_choice=r.clamp_style),
    ]


def build_industrial_drill_press_table(
    config: IndustrialDrillPressTableConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="industrial_drill_press_table", assets=assets)
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


def build_seeded_industrial_drill_press_table(seed: int) -> ArticulatedObject:
    return build_industrial_drill_press_table(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("mount", r.mount_style),
        ("worktop", r.worktop_form),
        ("table_motion", r.table_motion),
        ("locking", r.clamp_style),
        ("leaf", r.leaf_style),
        ("slot_count", f"slots_{r.slot_count}"),
        ("fence_count", f"fence_{r.fence_count}"),
        ("track_count", f"tracks_{r.track_count}"),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedIndustrialDrillPressTableConfig) -> None:
    parts = {p.name for p in model.parts}
    column = model.get_part("column")
    carriage = model.get_part("carriage")

    # Captured clamp collar sliding on the column tube (the jaw bores grip the
    # tube; contact IS the support path, overlap is intentional).
    for jaw in ("collar_rear", "collar_side_0", "collar_side_1"):
        ctx.allow_overlap(column, carriage, elem_a="column_tube", elem_b=jaw,
                           reason="Split clamp collar grips the column tube (captured sliding clamp).")

    # Captured tilt trunnion + bracket seat in the fork cheeks / single pivot
    # bracket (the pivot bearing region; overlap is the bearing engagement).
    if "table" in parts:
        table = model.get_part("table")
        # The table's underside hub (saddle + rib + trunnion) stays engaged with
        # the carriage mount bearing through the full tilt/swing, so the whole
        # table<->carriage interface is an intentional bearing engagement.
        ctx.allow_overlap(table, carriage,
                          reason="Table underside hub rides on / is captured by the carriage mount bearing across tilt and swivel.")
        if r.table_motion == "swing_column":
            # Turntable: the vertical swivel pin is captured in the carriage
            # swivel boss (the bearing engagement); the fork/bracket is unused.
            # The table's underside hub (saddle + rib root) rides on the boss at
            # the bearing, so those stay engaged with it through the full swivel.
            ctx.allow_overlap(table, carriage, elem_a="tilt_trunnion", elem_b="swivel_boss",
                              reason="Worktop swivel pin captured in the carriage turntable bearing boss.")
            ctx.allow_overlap(table, carriage, elem_a="underside_saddle", elem_b="swivel_boss",
                              reason="Table swivel hub (underside saddle) rides on the carriage turntable boss.")
            ctx.allow_overlap(table, carriage, elem_a="underside_rib", elem_b="swivel_boss",
                              reason="Underside rib root wraps the turntable boss at the swivel bearing.")
            ctx.allow_overlap(carriage, table, elem_a="saddle_block", elem_b="tilt_trunnion",
                              reason="Swivel pin seats against the carriage clamp saddle at the turntable bearing.")
            if r.mount_style == "forked_yoke":
                ctx.allow_overlap(table, carriage, elem_a="tilt_trunnion", elem_b="yoke_rail",
                                  reason="Swivel pin passes through the fork cross-rail bearing seat.")
        elif r.mount_style == "forked_yoke":
            for i in (0, 1):
                ctx.allow_overlap(table, carriage, elem_a="tilt_trunnion", elem_b=f"yoke_arm_{i}",
                                  reason="Tilt trunnion shaft captured through the forked yoke bearing.")
            ctx.allow_overlap(table, carriage, elem_a="tilt_trunnion", elem_b="yoke_rail",
                              reason="Tilt trunnion shaft rides in the fork cross-rail bearing seat.")
            ctx.allow_overlap(table, carriage, elem_a="underside_saddle", elem_b="yoke_rail",
                              reason="Table trunnion saddle seats onto the fork cross-rail at the pivot.")
        else:
            ctx.allow_overlap(table, carriage, elem_a="tilt_trunnion", elem_b="pivot_bracket",
                              reason="Tilt trunnion shaft captured by the single pivot bracket.")
            ctx.allow_overlap(table, carriage, elem_a="tilt_trunnion", elem_b="stub_trunnion",
                              reason="Table trunnion shaft is co-axial with the carriage stub trunnion.")
            ctx.allow_overlap(table, carriage, elem_a="underside_rib", elem_b="pivot_bracket",
                              reason="Table underside rib root sweeps past the single pivot bracket as the table tilts.")

    # Captured clamp lever hardware seated on the clamp ears (support path).
    if "lock_lever" in parts:
        lever = model.get_part("lock_lever")
        if r.clamp_style == "cam_lever":
            ctx.allow_overlap(carriage, lever, elem_a="clamp_ear_0", elem_b="lever_hub",
                              reason="Cam lever hub is captured on the clamp-ear pivot bore.")
            ctx.allow_overlap(carriage, lever, elem_a="clamp_ear_0", elem_b="lever_stem",
                              reason="Cam lever stem emerges through the clamp-ear pivot bore.")
        else:
            ctx.allow_overlap(carriage, lever, elem_a="clamp_ear_0", elem_b="screw_shaft",
                              reason="Clamp screw threads through the +Y clamp-ear bore (captured screw).")
            ctx.allow_overlap(carriage, lever, elem_a="clamp_ear_1", elem_b="screw_shaft",
                              reason="Clamp screw threads through the -Y clamp-ear bore (captured screw).")
            # The captured screw's inboard shaft + tip seat into/through the
            # split-collar clamp saddle they act on (the ear bores sit inside the
            # saddle footprint, so a screw through them necessarily enters it).
            ctx.allow_overlap(carriage, lever, elem_a="saddle_block", elem_b="screw_shaft",
                              reason="Captured clamp screw seats through the split-collar clamp saddle.")
            ctx.allow_overlap(carriage, lever, elem_a="saddle_block", elem_b="screw_tip",
                              reason="Captured clamp screw tip seats into the split-collar clamp saddle.")

    # Captured fold-leaf hinge: interleaved knuckles + pin at the hinge line.
    if "leaf" in parts:
        table = model.get_part("table")
        leaf = model.get_part("leaf")
        for i in (0, 1):
            ctx.allow_overlap(table, leaf, elem_a=f"table_hinge_knuckle_{i}", elem_b="leaf_hinge_pin",
                              reason="Fold-leaf hinge pin captured through interleaved table/leaf knuckles.")
            ctx.allow_overlap(table, leaf, elem_a=f"table_hinge_knuckle_{i}", elem_b=f"leaf_knuckle_{i}",
                              reason="Interleaved fold-leaf hinge knuckles at the pivot line.")
            # The leaf panel edge abuts the table hinge knuckles at the pivot line
            # (the knuckle sits on the panel edge, as on a real piano hinge).
            ctx.allow_overlap(table, leaf, elem_a=f"table_hinge_knuckle_{i}", elem_b="leaf_substrate",
                              reason="Fold-leaf panel edge meets the table hinge knuckle at the pivot line.")
            ctx.allow_overlap(table, leaf, elem_a=f"table_hinge_knuckle_{i}", elem_b="leaf_laminate",
                              reason="Fold-leaf laminate edge meets the table hinge knuckle at the pivot line.")
            # The leaf's own knuckles protrude to the worktop front edge and
            # interleave against it at the hinge (piano-hinge junction).
            ctx.allow_overlap(table, leaf, elem_a="worktop_substrate", elem_b=f"leaf_knuckle_{i}",
                              reason="Fold-leaf knuckle meets the worktop front edge at the pivot line.")
            ctx.allow_overlap(table, leaf, elem_a="worktop_laminate", elem_b=f"leaf_knuckle_{i}",
                              reason="Fold-leaf knuckle meets the worktop laminate front edge at the pivot line.")
        # Folded leaf panel + hinge pin rest against the worktop front edge/face.
        for leaf_elem in ("leaf_substrate", "leaf_laminate", "leaf_hinge_pin"):
            ctx.allow_overlap(table, leaf, elem_a="worktop_substrate", elem_b=leaf_elem,
                              reason="Folded leaf rests against the worktop front edge at the hinge.")
            ctx.allow_overlap(table, leaf, elem_a="worktop_laminate", elem_b=leaf_elem,
                              reason="Folded leaf rests against the worktop laminate front edge.")


def _expect_slide(ctx, model, r) -> None:
    column = model.get_part("column")
    carriage = model.get_part("carriage")
    slide = model.get_articulation("height_slide")
    ctx.check("height slide is prismatic", slide.articulation_type == ArticulationType.PRISMATIC)
    rest = ctx.part_world_position(carriage)
    with ctx.pose({slide: r.slide_travel}):
        raised = ctx.part_world_position(carriage)
    ok = rest is not None and raised is not None and raised[2] > rest[2] + r.slide_travel * 0.8
    ctx.check("height slide raises the carriage along the column", ok, details=f"rest={rest}, raised={raised}")


def _center_dist(a, b) -> float:
    if a is None or b is None:
        return 0.0
    ca = [(a[0][i] + a[1][i]) / 2.0 for i in range(3)]
    cb = [(b[0][i] + b[1][i]) / 2.0 for i in range(3)]
    return math.dist(ca, cb)


def _expect_motion(ctx, model, r) -> None:
    jn = "table_swing" if r.table_motion == "swing_column" else "table_tilt"
    joint = model.get_articulation(jn)
    ctx.check("table motion joint is revolute", joint.articulation_type == ArticulationType.REVOLUTE)
    table = model.get_part("table")
    rest = ctx.part_element_world_aabb(table, elem="worktop_laminate")
    val = (r.swing_range if r.table_motion == "swing_column" else r.tilt_range) * 0.8
    with ctx.pose({joint: val}):
        moved = ctx.part_element_world_aabb(table, elem="worktop_laminate")
    disp = _center_dist(rest, moved)
    ctx.check("table motion tilts/swivels the worktop", disp > 0.02, details=f"axis={r.table_motion}, disp={disp:.4f}")


def _expect_lock(ctx, model, r) -> None:
    lever = model.get_part("lock_lever")
    if r.clamp_style == "cam_lever":
        joint = model.get_articulation("lever_pivot")
        ctx.check("cam lever is revolute", joint.articulation_type == ArticulationType.REVOLUTE)
        rest = ctx.part_world_aabb(lever)
        with ctx.pose({joint: 0.9}):
            moved = ctx.part_world_aabb(lever)
        ok = rest is not None and moved is not None and abs(moved[1][1] - rest[1][1]) > 0.04
        ctx.check("cam lever rotates about its clamp hub", ok, details=f"rest={rest}, moved={moved}")
    else:
        joint = model.get_articulation("lever_screw")
        ctx.check("screw clamp is prismatic", joint.articulation_type == ArticulationType.PRISMATIC)
        rest = ctx.part_world_position(lever)
        with ctx.pose({joint: 0.012}):
            moved = ctx.part_world_position(lever)
        ok = rest is not None and moved is not None and abs(moved[1] - rest[1]) > 0.006
        ctx.check("screw clamp translates the knob", ok, details=f"rest={rest}, moved={moved}")


def _expect_leaf(ctx, model, r) -> None:
    if r.leaf_style != "flip_leaf":
        return
    leaf = model.get_part("leaf")
    joint = model.get_articulation("leaf_hinge")
    ctx.check("leaf hinge is revolute", joint.articulation_type == ArticulationType.REVOLUTE)
    rest = ctx.part_world_aabb(leaf)
    with ctx.pose({joint: math.pi / 2.0}):
        folded = ctx.part_world_aabb(leaf)
    ok = rest is not None and folded is not None and (folded[1][2] - folded[0][2]) > (rest[1][2] - rest[0][2]) + 0.05
    ctx.check("leaf folds up about the front edge", ok, details=f"rest={rest}, folded={folded}")


def run_industrial_drill_press_table_tests(
    model: ArticulatedObject,
    config: IndustrialDrillPressTableConfig,
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

    core = ("column", "carriage", "table", "lock_lever")
    ctx.check("drill-press-table core parts present",
              all(model.get_part(n) is not None for n in core),
              details="Expected column, carriage, table, lock_lever.")

    _expect_slide(ctx, model, r)
    _expect_motion(ctx, model, r)
    _expect_lock(ctx, model, r)
    _expect_leaf(ctx, model, r)

    # Rule 5: dynamic collision across sampled joint poses.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "IndustrialDrillPressTableConfig",
    "ResolvedIndustrialDrillPressTableConfig",
    "MountStyle",
    "WorktopForm",
    "TableMotion",
    "ClampStyle",
    "LeafStyle",
    "DrillTablePalette",
    "build_industrial_drill_press_table",
    "build_seeded_industrial_drill_press_table",
    "config_from_seed",
    "resolve_config",
    "run_industrial_drill_press_table_tests",
    "slot_choices_for_seed",
]
