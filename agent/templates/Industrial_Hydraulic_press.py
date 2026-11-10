# SPDX-License-Identifier: Apache-2.0

"""Industrial / Hydraulic press - modular procedural template.

A heavy fabricated-steel press ``frame`` (root) carries, under its top
crosshead / cantilever, a fixed hydraulic cylinder (hollow revolved shell +
gland ring + hose ports) and drives a vertical ``ram`` downward on a PRISMATIC
stroke (axis -Z, the category-defining joint) so a platen presses a workpiece
against a ``bed`` below. Operation is by a detached ``control_pedestal`` console
linked by flexible hydraulic hoses and a floor conduit.

Slot graph (pattern = mixed: root frame + 3 parallel-children slots + 2
multiplicity axes ``bed_pin_count`` / ``button_count``):

    frame (root; h_frame / h_frame_tubular / c_frame / four_post)
        |-- ram      (square_platen / round_platen)            PRISMATIC descent
        |-- bed      (fixed_bed / height_adjustable_bed / sliding_bolster_bed)
        \\-- control  (push_buttons xN / operating_lever)

Adapted per AUTHORING.md SS A/SS B from the confirmed 5-star Hydraulic-press
pool (spec: specs_modular_v1/Industrial_Hydraulic_press.md). Sources
(model.py:Lx-Ly cited in the spec Module Source Index):

  S1  origin rec_industrial__hydraulic_press__001 - H-frame box columns, fixed
      cylinder, FIXED bed, PRISMATIC square-platen ram, detached pedestal with
      3 PRISMATIC push buttons + hoses, all test semantics.
  S2  c_frame               - single rear-spine C-frame with cantilever.
  S3  four_post_frame       - four cylindrical corner guide posts.
  S4  tubular_columns       - round Cylinder columns.
  S5  round_platen          - round disc platen (Volumetric Envelope Form).
  S6  pin_adjustable_bed    - vertical PRISMATIC height-adjustable bed.
  S7  sliding_bolster_bed   - horizontal PRISMATIC sliding bolster + rails.
  S8  lever_valve_control   - REVOLUTE operating lever.
  S9  button_count          - button_count multiplicity (uniform helper).
  S10 bed_pin_count         - bed_pin_count multiplicity.

Coordinate frame: Z-up, floor z=0. Cylinder / ram / bed centered at x=y=0. +X =
toward the control console; -Y = operator side (front). Mirrored pieces
straddle y=0.
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
    mount_fixed,
)
from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    LatheGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
    tube_from_spline_points,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


FrameForm = Literal["h_frame", "h_frame_tubular", "c_frame", "four_post"]
PlatenModule = Literal["square_platen", "round_platen"]
BedModule = Literal["fixed_bed", "height_adjustable_bed", "sliding_bolster_bed"]
ControlModule = Literal["push_buttons", "operating_lever"]
PressPalette = Literal[
    "warm_gray_press",
    "machine_blue",
    "safety_orange",
    "hammertone_green",
    "graphite_dark",
    "bare_steel",
]

_H_FRAMES = ("h_frame", "h_frame_tubular")


# --------------------------------------------------------------------------- #
# Canonical dimensions (origin rec_industrial__hydraulic_press__001)
# --------------------------------------------------------------------------- #

PEDESTAL_X = 1.36           # detached console offset (origin frame_to_pedestal x)
CONDUIT_TOP_Z = 0.18        # conduit/plinth top the console base rests on (tall
                            # enough to reach every frame form's low base)
GAP_MARGIN = 0.045          # min platen<->bed clearance kept in any sampled pose

# Ram tooling geometry (local, part frame at the joint origin; visuals go -Z).
RAM_ROD_R = 0.100
RAM_PLATEN_FACE_Z = -0.555
RAM_PLATEN_FACE_HALF = 0.0175
BED_TOP_ABOVE_SEAT = 0.134  # replaceable_bed_plate top above the bed seat plane


# --------------------------------------------------------------------------- #
# Palettes (>=6 colorways; every token registered so each .visual resolves).
# Button / label / indicator colors stay semantic across palettes.
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "warm_gray_press": {
        "body": (0.55, 0.57, 0.56, 1.0),
        "dark": (0.20, 0.21, 0.20, 1.0),
        "edge": (0.38, 0.40, 0.39, 1.0),
        "steel": (0.78, 0.78, 0.74, 1.0),
        "polished": (0.86, 0.86, 0.82, 1.0),
    },
    "machine_blue": {
        "body": (0.19, 0.29, 0.46, 1.0),
        "dark": (0.10, 0.13, 0.20, 1.0),
        "edge": (0.14, 0.22, 0.36, 1.0),
        "steel": (0.72, 0.74, 0.77, 1.0),
        "polished": (0.84, 0.85, 0.87, 1.0),
    },
    "safety_orange": {
        "body": (0.82, 0.40, 0.10, 1.0),
        "dark": (0.16, 0.13, 0.11, 1.0),
        "edge": (0.55, 0.28, 0.09, 1.0),
        "steel": (0.74, 0.74, 0.72, 1.0),
        "polished": (0.86, 0.86, 0.83, 1.0),
    },
    "hammertone_green": {
        "body": (0.22, 0.36, 0.26, 1.0),
        "dark": (0.10, 0.15, 0.11, 1.0),
        "edge": (0.15, 0.26, 0.18, 1.0),
        "steel": (0.70, 0.72, 0.68, 1.0),
        "polished": (0.83, 0.84, 0.80, 1.0),
    },
    "graphite_dark": {
        "body": (0.22, 0.23, 0.24, 1.0),
        "dark": (0.07, 0.07, 0.08, 1.0),
        "edge": (0.14, 0.15, 0.16, 1.0),
        "steel": (0.60, 0.61, 0.63, 1.0),
        "polished": (0.80, 0.81, 0.83, 1.0),
    },
    "bare_steel": {
        "body": (0.66, 0.67, 0.68, 1.0),
        "dark": (0.28, 0.29, 0.30, 1.0),
        "edge": (0.50, 0.51, 0.52, 1.0),
        "steel": (0.82, 0.83, 0.82, 1.0),
        "polished": (0.90, 0.90, 0.88, 1.0),
    },
}

# Semantic (palette-independent) colors used everywhere.
SEMANTIC: dict[str, tuple[float, float, float, float]] = {
    "black": (0.02, 0.02, 0.02, 1.0),
    "yellow": (1.0, 0.72, 0.06, 1.0),
    "red": (0.85, 0.06, 0.04, 1.0),
    "green": (0.02, 0.55, 0.18, 1.0),
    "amber": (1.0, 0.55, 0.03, 1.0),
    "white": (0.92, 0.92, 0.86, 1.0),
    "blue": (0.08, 0.25, 0.72, 1.0),
}
PALETTE_NAMES = tuple(PALETTES.keys())
BUTTON_COLORS = ("green", "red", "amber", "blue", "white")


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class IndustrialHydraulicPressConfig:
    frame_form: FrameForm = "h_frame"
    platen_module: PlatenModule = "square_platen"
    bed_module: BedModule = "fixed_bed"
    control_module: ControlModule = "push_buttons"
    palette_style: PressPalette = "warm_gray_press"

    bed_pin_count: int = 3   # per column (frame decoration multiplicity)
    button_count: int = 3    # push_buttons only; ignored for operating_lever

    frame_height_scale: float = 1.0
    frame_width_scale: float = 1.0
    platen_scale: float = 1.0
    ram_travel: float = 0.16
    bed_raise: float = 0.08       # height_adjustable_bed only
    bed_lower: float = 0.045      # height_adjustable_bed only
    bolster_travel: float = 0.20  # sliding_bolster_bed only
    lever_range: float = 0.55     # operating_lever only


@dataclass(frozen=True)
class ResolvedIndustrialHydraulicPressConfig:
    frame_form: FrameForm
    platen_module: PlatenModule
    bed_module: BedModule
    control_module: ControlModule
    palette_style: str

    bed_pin_count: int
    button_count: int

    frame_height_scale: float
    frame_width_scale: float
    platen_scale: float
    ram_travel: float
    bed_raise: float
    bed_lower: float
    bolster_travel: float
    lever_range: float

    # Single-sourced datums (Contract 3c). Every slot derives its mounts here,
    # so frame form is orthogonal to ram / bed / control.
    crosshead_z: float
    crosshead_h: float
    col_center_z: float
    col_h: float
    sill_z: float
    flange_z: float
    cyl_center_z: float
    cyl_len: float
    gland_z: float
    cyl_axis_z: float      # ram PRISMATIC joint origin z
    bed_contact_z: float   # top of the frame bed ledge
    bed_seat_z: float      # where the bed_block bottom sits (rails raise it)
    col_x: float
    cross_w: float
    sill_w: float
    bed_x_scale: float     # bed width factor so the bed fits the column gap
    daylight_rest: float   # platen-bottom to bed-top clearance at rest

    palette: dict[str, tuple[float, float, float, float]]

    @property
    def ram_rest_platen_z(self) -> float:
        return self.cyl_axis_z + RAM_PLATEN_FACE_Z - RAM_PLATEN_FACE_HALF

    @property
    def bed_top_rest_z(self) -> float:
        return self.bed_seat_z + BED_TOP_ABOVE_SEAT


# --------------------------------------------------------------------------- #
# Seed-driven sampling (procedural-first)
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> IndustrialHydraulicPressConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin combination (h_frame + square_platen +
    fixed_bed + push_buttons x3, warm_gray_press) as a documented regression
    anchor (a sparse override; every other seed is fully procedural).
    """
    if seed == 0:
        return IndustrialHydraulicPressConfig()

    rng = random.Random(seed)

    frame_form: FrameForm = rng.choice(
        ("h_frame", "h_frame_tubular", "c_frame", "four_post")
    )
    platen_module: PlatenModule = rng.choice(("square_platen", "round_platen"))
    bed_module: BedModule = rng.choice(
        ("fixed_bed", "height_adjustable_bed", "sliding_bolster_bed")
    )
    control_module: ControlModule = rng.choice(("push_buttons", "operating_lever"))
    palette_style = rng.choice(PALETTE_NAMES)

    bed_pin_count = rng.choices((2, 3, 5), weights=(0.2, 0.5, 0.3))[0]
    button_count = rng.choices((3, 4, 5), weights=(0.5, 0.2, 0.3))[0]

    frame_height_scale = round(rng.uniform(0.95, 1.12), 4)
    frame_width_scale = round(rng.uniform(0.90, 1.15), 4)
    platen_scale = round(rng.uniform(0.85, 1.15), 4)
    ram_travel = round(rng.uniform(0.10, 0.16), 4)
    bed_raise = round(rng.uniform(0.05, 0.09), 4)
    bed_lower = round(rng.uniform(0.03, 0.05), 4)
    bolster_travel = round(rng.uniform(0.14, 0.22), 4)
    lever_range = round(rng.uniform(0.40, 0.60), 4)

    return IndustrialHydraulicPressConfig(
        frame_form=frame_form,
        platen_module=platen_module,
        bed_module=bed_module,
        control_module=control_module,
        palette_style=palette_style,
        bed_pin_count=bed_pin_count,
        button_count=button_count,
        frame_height_scale=frame_height_scale,
        frame_width_scale=frame_width_scale,
        platen_scale=platen_scale,
        ram_travel=ram_travel,
        bed_raise=bed_raise,
        bed_lower=bed_lower,
        bolster_travel=bolster_travel,
        lever_range=lever_range,
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(
    config: IndustrialHydraulicPressConfig,
) -> ResolvedIndustrialHydraulicPressConfig:
    if str(config.frame_form) not in {"h_frame", "h_frame_tubular", "c_frame", "four_post"}:
        raise ValueError(f"Unsupported frame_form: {config.frame_form}")
    if str(config.platen_module) not in {"square_platen", "round_platen"}:
        raise ValueError(f"Unsupported platen_module: {config.platen_module}")
    if str(config.bed_module) not in {
        "fixed_bed",
        "height_adjustable_bed",
        "sliding_bolster_bed",
    }:
        raise ValueError(f"Unsupported bed_module: {config.bed_module}")
    if str(config.control_module) not in {"push_buttons", "operating_lever"}:
        raise ValueError(f"Unsupported control_module: {config.control_module}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    h = _clamp(config.frame_height_scale, 0.95, 1.12)
    w = _clamp(config.frame_width_scale, 0.90, 1.15)
    platen_scale = _clamp(config.platen_scale, 0.85, 1.15)

    bed_pin_count = int(_clamp(config.bed_pin_count, 2, 5))
    button_count = int(_clamp(config.button_count, 3, 5))

    # --- vertical datums, chained so the crosshead sits ON the columns and the
    #     cylinder hangs from the crosshead at every height scale (avoids the
    #     members drifting apart as h varies) ---
    col_h = 1.62 * h
    col_center_z = 0.91 * h
    col_top = col_center_z + col_h / 2.0        # == 1.72h (also four_post posts top)
    crosshead_h = 0.36
    crosshead_z = col_top + crosshead_h / 2.0 - 0.04   # 4 cm seated onto columns
    crosshead_bottom = crosshead_z - crosshead_h / 2.0
    sill_z = 0.26 * h
    flange_z = crosshead_bottom - 0.01          # flange top embeds into crosshead
    cyl_len = 0.30
    cyl_center_z = crosshead_bottom - 0.17      # cylinder top overlaps flange
    gland_z = cyl_center_z - 0.15               # gland at the cylinder lower end
    cyl_axis_z = cyl_center_z                   # ram origin (prismatic: gauge-free)
    bed_contact_z = 0.575 * h

    col_x = 0.65 * w
    cross_w = 1.65 * w
    sill_w = 1.28 * w

    # Bed width fits the realized clear span between the columns/posts so the
    # (nominally 0.88-wide) bed never clips the frame at small width scales.
    # Inner obstruction is the inner_wear_plate (protrudes past the column face).
    if config.frame_form == "h_frame":
        clearance_half = col_x - 0.1755 - 0.02   # wear plate inner face - margin
    elif config.frame_form == "h_frame_tubular":
        clearance_half = col_x - 0.1525 - 0.02
    elif config.frame_form == "four_post":
        clearance_half = (col_x - 0.13) - 0.06 - 0.03
    else:  # c_frame is open at the sides
        clearance_half = 0.44
    bed_x_scale = _clamp(min(0.44, clearance_half) / 0.44, 0.74, 1.0)

    # Sliding bolster rides on rails ~18 mm proud of the ledge.
    bed_seat_z = bed_contact_z + (0.018 if config.bed_module == "sliding_bolster_bed" else 0.0)

    ram_rest_platen_z = cyl_axis_z + RAM_PLATEN_FACE_Z - RAM_PLATEN_FACE_HALF
    bed_top_rest_z = bed_seat_z + BED_TOP_ABOVE_SEAT
    daylight_rest = ram_rest_platen_z - bed_top_rest_z

    # --- travel feasibility (inequality projection so no sampled pose closes
    #     the platen-bed gap below GAP_MARGIN) ---
    if config.bed_module == "height_adjustable_bed":
        budget = daylight_rest - 0.08 - GAP_MARGIN  # reserve a min 0.08 ram stroke
        bed_raise = _clamp(config.bed_raise, 0.03, max(0.02, min(0.09, budget)))
        bed_lower = _clamp(config.bed_lower, 0.03, 0.05)
        ram_travel_max = daylight_rest - bed_raise - GAP_MARGIN
    else:
        bed_raise = 0.0
        bed_lower = 0.0
        ram_travel_max = daylight_rest - GAP_MARGIN
    ram_travel = _clamp(config.ram_travel, 0.08, max(0.08, min(0.16, ram_travel_max)))

    bolster_travel = (
        _clamp(config.bolster_travel, 0.14, 0.22)
        if config.bed_module == "sliding_bolster_bed"
        else 0.0
    )
    lever_range = (
        _clamp(config.lever_range, 0.40, 0.60)
        if config.control_module == "operating_lever"
        else 0.0
    )

    palette = dict(PALETTES[config.palette_style])
    palette.update(SEMANTIC)

    return ResolvedIndustrialHydraulicPressConfig(
        frame_form=config.frame_form,
        platen_module=config.platen_module,
        bed_module=config.bed_module,
        control_module=config.control_module,
        palette_style=config.palette_style,
        bed_pin_count=bed_pin_count,
        button_count=button_count,
        frame_height_scale=h,
        frame_width_scale=w,
        platen_scale=platen_scale,
        ram_travel=ram_travel,
        bed_raise=bed_raise,
        bed_lower=bed_lower,
        bolster_travel=bolster_travel,
        lever_range=lever_range,
        crosshead_z=crosshead_z,
        crosshead_h=crosshead_h,
        col_center_z=col_center_z,
        col_h=col_h,
        sill_z=sill_z,
        flange_z=flange_z,
        cyl_center_z=cyl_center_z,
        cyl_len=cyl_len,
        gland_z=gland_z,
        cyl_axis_z=cyl_axis_z,
        bed_contact_z=bed_contact_z,
        bed_seat_z=bed_seat_z,
        col_x=col_x,
        cross_w=cross_w,
        sill_w=sill_w,
        bed_x_scale=bed_x_scale,
        daylight_rest=daylight_rest,
        palette=palette,
    )


# --------------------------------------------------------------------------- #
# Shared meshes / geometry helpers
# --------------------------------------------------------------------------- #


def _hollow_tube_mesh(outer_r: float, inner_r: float, length: float, name: str, segments: int):
    """Hollow steel cylinder shell revolved as a LatheGeometry tube with annular
    end caps (faithful hollow shell; the origin used a cadquery boolean cut -
    same hollow-shell primitive family, revolved instead, per Rule 3)."""
    half = length / 2.0
    profile = [
        (inner_r, -half),
        (outer_r, -half),
        (outer_r, half),
        (inner_r, half),
        (inner_r, -half),
    ]
    return mesh_from_geometry(LatheGeometry(profile, segments=segments), name)


# --------------------------------------------------------------------------- #
# Slot A - frame (root, (3) Primary Form Family)
# --------------------------------------------------------------------------- #


def _bed_ledge_visual(r: ResolvedIndustrialHydraulicPressConfig) -> str:
    """Name of the central frame surface the bed_block bottom mates against and
    the fixed-bed FIXED origin sits on (single-sourced per form)."""
    return "bed_ledge_plate" if r.frame_form == "c_frame" else "bed_saddle"


def _emit_bed_saddle(frame, r, sill_top_z: float) -> None:
    """Central bolster support block bridging the sill up to the bed contact
    plane, so the bed seats on a real central surface and the FIXED bed joint
    origin at (0,0,bed_contact_z) lands on frame geometry (H-frame/four_post)."""
    top = r.bed_contact_z
    bottom = sill_top_z - 0.03  # embed into the sill so it is connected
    height = max(0.06, top - bottom)
    # Wide enough (x +-0.42) to overlap both side ledges so the whole
    # bed-support region is one connected block and the FIXED bed origin lands
    # on it at center.
    frame.visual(
        Box((0.84, 0.44, height)),
        origin=Origin(xyz=(0.0, 0.0, top - height / 2.0)),
        material="edge",
        name="bed_saddle", material_class_id="metal.paint_coated",
    )


def _frame_downstream(r: ResolvedIndustrialHydraulicPressConfig) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="frame",
        visual_name="cylinder_flange",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, r.bed_contact_z),
        contact_tol=0.004,
    )


def _emit_ledge(frame, r, name: str, x: float, size_xy: tuple[float, float], material: str) -> None:
    """A bed ledge whose TOP is exactly at r.bed_contact_z."""
    lx, ly = size_xy
    frame.visual(
        Box((lx, ly, 0.06)),
        origin=Origin(xyz=(x, 0.0, r.bed_contact_z - 0.03)),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _emit_bed_pins(frame, r, xs: list[float], face_y: float,
                   z0: float | None = None, step: float | None = None) -> None:
    """Adjustable bed-height locating pins on the column front faces
    (multiplicity axis, frame surface decoration - Rule 1 visuals)."""
    z0 = 0.53 * r.frame_height_scale if z0 is None else z0
    step = 0.09 * r.frame_height_scale if step is None else step
    for side, x in xs:
        for i in range(r.bed_pin_count):
            frame.visual(
                Cylinder(radius=0.020, length=0.032),
                origin=Origin(xyz=(x, face_y - 0.013, z0 + i * step), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material="dark",
                name=f"{side}_bed_pin_{i}", material_class_id="metal.blackened_gunmetal",
            )


def _emit_cylinder_and_ports(frame, r) -> None:
    """Fixed hydraulic cylinder shell + gland + manifold + hose ports (all forms,
    single-sourced positions). The manifold box bridges the cylinder to the
    crosshead and carries the ports facing the console."""
    frame.visual(
        Cylinder(radius=0.275, length=0.060),
        origin=Origin(xyz=(0.0, 0.0, r.flange_z)),
        material="steel",
        name="cylinder_flange", material_class_id="metal.steel_bare",
    )
    frame.visual(
        _hollow_tube_mesh(0.205, 0.098, r.cyl_len, "fixed_cylinder_shell", 48),
        origin=Origin(xyz=(0.0, 0.0, r.cyl_center_z)),
        material="steel",
        name="fixed_cylinder", material_class_id="metal.steel_bare",
    )
    frame.visual(
        _hollow_tube_mesh(0.150, 0.096, 0.040, "gland_ring_shell", 32),
        origin=Origin(xyz=(0.0, 0.0, r.gland_z)),
        material="dark",
        name="gland_ring", material_class_id="metal.blackened_gunmetal",
    )
    # Manifold + hose ports under the crosshead front, overlapping crosshead +
    # cylinder (identity detail; the flexible lines to the console are not
    # modelled to keep the detached-console assembly collision-clean).
    mani_z = r.crosshead_z - r.crosshead_h / 2.0 - 0.02
    frame.visual(
        Box((0.16, 0.30, 0.18)),
        origin=Origin(xyz=(0.26, -0.06, mani_z)),
        material="steel",
        name="hydraulic_manifold", material_class_id="metal.steel_bare",
    )
    frame.visual(
        Cylinder(radius=0.030, length=0.080),
        origin=Origin(xyz=(0.26, -0.22, mani_z + 0.02), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark",
        name="upper_hose_port", material_class_id="metal.blackened_gunmetal",
    )
    frame.visual(
        Cylinder(radius=0.024, length=0.080),
        origin=Origin(xyz=(0.26, -0.22, mani_z - 0.06), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark",
        name="lower_hose_port", material_class_id="metal.blackened_gunmetal",
    )


def _emit_control_conduit(frame, r) -> None:
    """Low floor raceway from the frame base to the console (carries the
    hydraulic lines). Overlaps the frame base near x in [0, col_x] for every
    form, and its far-top edge is where the console FIXES down (origin honesty
    on the frame side + geometric connectivity for the detached console)."""
    frame.visual(
        Box((PEDESTAL_X, 0.14, CONDUIT_TOP_Z)),
        origin=Origin(xyz=(PEDESTAL_X / 2.0, 0.0, CONDUIT_TOP_Z / 2.0)),
        material="dark",
        name="control_conduit", material_class_id="metal.blackened_gunmetal",
    )


def _emit_frame_decoration(frame, r, label_xs: list[float], face_y: float) -> None:
    """Bolted seams, logo plate and side warning labels straddling the front
    face ``face_y`` so each stays embedded in / touching the frame (Rule 1)."""
    for i, x in enumerate(label_xs):
        frame.visual(
            Box((0.055, 0.010, 0.070)),
            origin=Origin(xyz=(x, face_y, 1.05 * r.frame_height_scale)),
            material="yellow",
            name=f"warning_label_{i}", appearance_only=AppearanceOnlySpec(kind="decal"),
        )
        frame.visual(
            Box((0.020, 0.012, 0.035)),
            origin=Origin(xyz=(x, face_y - 0.006, 1.05 * r.frame_height_scale)),
            material="black",
            name=f"warning_mark_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        frame.visual(
            Cylinder(radius=0.024, length=0.030),
            origin=Origin(xyz=(x, face_y + 0.004, 1.40 * r.frame_height_scale), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="dark",
            name=f"column_bolt_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _build_frame(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialHydraulicPressConfig = ctx.config  # type: ignore[assignment]
    frame = model.part("frame")

    def fb(name, size, xyz, material="body", rpy=(0.0, 0.0, 0.0)):
        frame.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")

    def fc(name, radius, length, xyz, material="steel", rpy=(0.0, 0.0, 0.0)):
        frame.visual(Cylinder(radius=radius, length=length), origin=Origin(xyz=xyz, rpy=rpy),
                     material=material, name=name, material_class_id="metal.steel_bare")

    cx = r.col_x

    if r.frame_form in _H_FRAMES:
        tubular = r.frame_form == "h_frame_tubular"
        col_front_y = -0.15 if tubular else -0.25
        if tubular:
            fc("left_column", 0.15, r.col_h, (-cx, 0.0, r.col_center_z), "body")
            fc("right_column", 0.15, r.col_h, (cx, 0.0, r.col_center_z), "body")
        else:
            fb("left_column", (0.28, 0.50, r.col_h), (-cx, 0.0, r.col_center_z))
            fb("right_column", (0.28, 0.50, r.col_h), (cx, 0.0, r.col_center_z))
        fb("top_crosshead", (r.cross_w, 0.60, r.crosshead_h), (0.0, 0.0, r.crosshead_z))
        fb("rear_top_cap", (1.38 * r.frame_width_scale, 0.54, 0.08), (0.0, 0.03, r.crosshead_z + 0.20))
        fb("lower_sill", (r.sill_w, 0.56, 0.24), (0.0, 0.0, r.sill_z))
        for x, side in [(-cx, "left"), (cx, "right")]:
            fb(f"{side}_foot_pad", (0.48, 0.84, 0.12), (x, 0.0, 0.06))
            fb(f"{side}_front_flare", (0.16, 0.32, 0.45), (x, -0.30, 0.24), rpy=(math.radians(-10.0), 0.0, 0.0))
            fb(f"{side}_rear_flare", (0.16, 0.32, 0.45), (x, 0.30, 0.24), rpy=(math.radians(10.0), 0.0, 0.0))
            inset = math.copysign(0.135 if tubular else 0.158, x)
            fb(f"{side}_inner_wear_plate", (0.035, 0.34, 1.28), (x - inset, -0.002, 0.98 * r.frame_height_scale), "edge")
        _emit_ledge(frame, r, "left_bed_ledge", -0.435, (0.23, 0.50), "edge")
        _emit_ledge(frame, r, "right_bed_ledge", 0.435, (0.23, 0.50), "edge")
        _emit_bed_saddle(frame, r, r.sill_z + 0.12)
        pin_x = cx if tubular else cx - 0.145
        _emit_bed_pins(frame, r, [("left", -pin_x), ("right", pin_x)], col_front_y)
        _emit_frame_decoration(frame, r, [-cx, cx], col_front_y)

    elif r.frame_form == "c_frame":
        fb("rear_spine", (0.40, 0.44, 2.04 * r.frame_height_scale), (0.0, 0.52, 1.08 * r.frame_height_scale))
        fb("top_cantilever", (0.48, 1.04, r.crosshead_h), (0.0, 0.0, r.crosshead_z))
        fb("base_arm", (0.88, 0.92, 0.24), (0.0, 0.04, 0.23 * r.frame_height_scale))
        fb("base_foot", (0.60, 1.50, 0.12), (0.0, 0.18, 0.06))
        fb("front_flare", (0.50, 0.28, 0.38), (0.0, -0.54, 0.21), rpy=(math.radians(-10.0), 0.0, 0.0))
        fb("rear_flare", (0.50, 0.28, 0.38), (0.0, 0.82, 0.21), rpy=(math.radians(10.0), 0.0, 0.0))
        base_arm_top = 0.23 * r.frame_height_scale + 0.12
        bs_bot = base_arm_top - 0.03
        bs_top = r.bed_contact_z - 0.025  # just under the ledge plate
        fb("bed_support", (0.50, 0.62, bs_top - bs_bot), (0.0, 0.04, (bs_bot + bs_top) / 2.0))
        fb("spine_wear_plate", (0.36, 0.035, 1.60 * r.frame_height_scale), (0.0, 0.315, 1.0 * r.frame_height_scale), "edge")
        fb("top_rear_cap", (0.44, 0.50, 0.08), (0.0, 0.30, r.crosshead_z + 0.20))
        for i, (dx, dz) in enumerate([(-0.18, 0.0), (0.18, 0.0)]):
            fb(f"top_gusset_{i}", (0.04, 0.30, 0.30), (dx, 0.25, r.crosshead_z - 0.24), "edge",
               rpy=(math.radians(-25.0), 0.0, 0.0))
        # centered bed ledge plate + bed support riser front face for pins
        frame.visual(
            Box((0.78, 0.44, 0.025)),
            origin=Origin(xyz=(0.0, 0.0, r.bed_contact_z - 0.0125)),
            material="steel",
            name="bed_ledge_plate", material_class_id="metal.steel_bare",
        )
        # pins ride the bed_support front (y~-0.27) BELOW the bed so they clear
        # the bed body; face_y chosen so the pin root embeds into the support
        _emit_bed_pins(frame, r, [("center", 0.0)], -0.258,
                       z0=0.36 * r.frame_height_scale, step=0.042 * r.frame_height_scale)
        _emit_frame_decoration(frame, r, [0.205], 0.30)

    else:  # four_post
        fb("top_crosshead", (r.cross_w, 0.60, r.crosshead_h), (0.0, 0.0, r.crosshead_z))
        fb("rear_top_cap", (1.38 * r.frame_width_scale, 0.54, 0.08), (0.0, 0.03, r.crosshead_z + 0.20))
        fb("lower_sill", (r.sill_w, 0.56, 0.24), (0.0, 0.0, r.sill_z))
        # Posts span from below the sill top up to col_top (== crosshead seat),
        # so they overlap the sill AND carry the crosshead at every height scale.
        col_top = 1.72 * r.frame_height_scale
        post_h = col_top - (r.sill_z - 0.06)     # bottom embeds into the sill
        post_z = col_top - post_h / 2.0
        foot_h = r.sill_z + 0.06                  # floor up into the sill
        for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
            px, py = sx * (cx - 0.13), sy * 0.20
            fc(f"post_{i}", 0.060, post_h, (px, py, post_z), "steel")
            fc(f"post_{i}_top_collar", 0.075, 0.040, (px, py, col_top - 0.04), "steel")
            fc(f"post_{i}_bottom_collar", 0.075, 0.040, (px, py, r.sill_z + 0.16), "steel")
            fb(f"post_{i}_foot_pad", (0.18, 0.18, foot_h), (px, py, foot_h / 2.0))
        _emit_ledge(frame, r, "left_bed_ledge", -0.40, (0.06, 0.40), "edge")
        _emit_ledge(frame, r, "right_bed_ledge", 0.40, (0.06, 0.40), "edge")
        _emit_bed_saddle(frame, r, r.sill_z + 0.12)
        _emit_bed_pins(frame, r, [("left", -(cx - 0.13)), ("right", (cx - 0.13))], -0.26)
        _emit_frame_decoration(frame, r, [-(cx - 0.13), (cx - 0.13)], -0.26)

    _emit_cylinder_and_ports(frame, r)
    _emit_control_conduit(frame, r)

    return ModuleBuild(
        module_name=r.frame_form,
        parts_emitted=["frame"],
        interfaces={"downstream": _frame_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot B - ram (defining PRISMATIC descent, (3) tooling form)
# --------------------------------------------------------------------------- #


def _build_ram(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialHydraulicPressConfig = ctx.config  # type: ignore[assignment]
    frame = model.get_part("frame")
    ram = model.part("ram")

    ram.visual(Cylinder(radius=RAM_ROD_R, length=0.620), origin=Origin(xyz=(0.0, 0.0, -0.230)),
               material="polished", name="ram_rod", material_class_id="metal.chrome_polished")
    ram.visual(Cylinder(radius=0.135, length=0.090), origin=Origin(xyz=(0.0, 0.0, -0.425)),
               material="steel", name="ram_collared_head", material_class_id="metal.steel_bare")
    ram.visual(Cylinder(radius=0.155, length=0.070), origin=Origin(xyz=(0.0, 0.0, -0.505)),
               material="dark", name="press_platen", material_class_id="metal.blackened_gunmetal")
    ps = r.platen_scale
    if r.platen_module == "round_platen":
        ram.visual(Cylinder(radius=0.120 * ps, length=0.035),
                   origin=Origin(xyz=(0.0, 0.0, RAM_PLATEN_FACE_Z)),
                   material="dark", name="round_platen_disc", material_class_id="metal.blackened_gunmetal")
    else:
        ram.visual(Box((0.23 * ps, 0.23 * ps, 0.035)),
                   origin=Origin(xyz=(0.0, 0.0, RAM_PLATEN_FACE_Z)),
                   material="dark", name="square_platen_face", material_class_id="metal.blackened_gunmetal")

    model.articulation(
        "frame_to_ram",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=ram,
        origin=Origin(xyz=(0.0, 0.0, r.cyl_axis_z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=180000.0, velocity=0.08, lower=0.0, upper=r.ram_travel),
    )
    return ModuleBuild(
        module_name=r.platen_module,
        parts_emitted=["ram"],
        internal_articulations=["frame_to_ram"],
        interfaces={"downstream": _frame_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot C - bed (parallel child; (2) bed joint)
# --------------------------------------------------------------------------- #


def _emit_bed_visuals(bed, r) -> None:
    """Bed body seated so its bottom face is at local z=0 (== r.bed_seat_z world
    after the joint), hazard-striped front + replaceable plate (origin S1)."""
    sx = r.bed_x_scale
    bed.visual(Box((0.88 * sx, 0.48, 0.13)), origin=Origin(xyz=(0.0, 0.0, 0.065)), material="edge", name="bed_block", material_class_id="metal.paint_coated")
    bed.visual(Box((0.88 * sx, 0.035, 0.075)), origin=Origin(xyz=(0.0, -0.247, 0.107)), material="yellow", name="hazard_yellow", appearance_only=AppearanceOnlySpec(kind="overlay"))
    for i, x in enumerate([-0.37, -0.25, -0.13, -0.01, 0.11, 0.23, 0.35]):
        bed.visual(
            Box((0.045, 0.042, 0.105)),
            origin=Origin(xyz=(x * sx, -0.263, 0.108), rpy=(0.0, math.radians(23.0), 0.0)),
            material="black",
            name=f"hazard_black_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    bed.visual(Box((0.76 * sx, 0.38, 0.018)), origin=Origin(xyz=(0.0, 0.0, 0.125)), material="steel", name="replaceable_bed_plate", material_class_id="metal.steel_bare")
    bed.visual(Box((0.76 * sx, 0.018, 0.025)), origin=Origin(xyz=(0.0, -0.18, 0.139)), material="dark", name="front_bed_seam", material_class_id="metal.blackened_gunmetal")


def _build_fixed_bed(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialHydraulicPressConfig = ctx.config  # type: ignore[assignment]
    frame = model.get_part("frame")
    bed = model.part("bed")
    _emit_bed_visuals(bed, r)
    model.articulation(
        "frame_to_bed",
        ArticulationType.FIXED,
        parent=frame,
        child=bed,
        origin=Origin(xyz=(0.0, 0.0, r.bed_seat_z)),
        mating=MatingContract(
            parent_face_geometry=_bed_ledge_visual(r),
            parent_face_side="positive_z",
            child_face_geometry="bed_block",
            child_face_side="negative_z",
            contact_tol=0.006,
        ),
    )
    return ModuleBuild(
        module_name="fixed_bed",
        parts_emitted=["bed"],
        internal_articulations=["frame_to_bed"],
        interfaces={"downstream": _frame_downstream(r)},
    )


def _build_height_adjustable_bed(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialHydraulicPressConfig = ctx.config  # type: ignore[assignment]
    frame = model.get_part("frame")
    bed = model.part("bed")
    _emit_bed_visuals(bed, r)
    model.articulation(
        "frame_to_bed",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=bed,
        origin=Origin(xyz=(0.0, 0.0, r.bed_seat_z)),
        axis=(0.0, 0.0, 1.0),
        # Up-only: the bed rests on its central saddle/ledge at q=0 and pins UP to
        # reduce daylight; it cannot lower through its own support (source used a
        # small down travel too, dropped so the shelf-mounted bed never self-clips).
        motion_limits=MotionLimits(effort=50000.0, velocity=0.04, lower=0.0, upper=r.bed_raise),
    )
    return ModuleBuild(
        module_name="height_adjustable_bed",
        parts_emitted=["bed"],
        internal_articulations=["frame_to_bed"],
        interfaces={"downstream": _frame_downstream(r)},
    )


def _build_sliding_bolster_bed(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialHydraulicPressConfig = ctx.config  # type: ignore[assignment]
    frame = model.get_part("frame")

    # Bolster rails on the central bed support (x=+-0.32 sits on the saddle /
    # ledge plate for every frame form); the bed slides on them.
    for x, side in [(-0.32, "left"), (0.32, "right")]:
        frame.visual(
            Box((0.065, 0.52, 0.024)),
            origin=Origin(xyz=(x, 0.0, r.bed_contact_z + 0.006)),
            material="steel",
            name=f"{side}_bolster_rail", material_class_id="metal.steel_bare",
        )

    bed = model.part("bed")
    _emit_bed_visuals(bed, r)
    for x, side in [(-0.32, "left"), (0.32, "right")]:
        bed.visual(
            Box((0.075, 0.46, 0.012)),
            origin=Origin(xyz=(x, 0.0, -0.006)),
            material="dark",
            name=f"{side}_slide_shoe", material_class_id="metal.blackened_gunmetal",
        )
    model.articulation(
        "frame_to_bed",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=bed,
        origin=Origin(xyz=(0.0, 0.0, r.bed_seat_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=5000.0, velocity=0.05, lower=0.0, upper=r.bolster_travel),
    )
    return ModuleBuild(
        module_name="sliding_bolster_bed",
        parts_emitted=["bed"],
        internal_articulations=["frame_to_bed"],
        interfaces={"downstream": _frame_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot D - control (parallel child; detached console + (1)/(2) operator interface)
# --------------------------------------------------------------------------- #


def _emit_pedestal_visuals(pedestal, r) -> None:
    """Console cabinet, sloped panel, gauge, indicators, hose fittings, feet
    (all fused visuals, Rule 1). Authored around the console base at local z=0."""
    pedestal.visual(Box((0.38, 0.34, 0.62)), origin=Origin(xyz=(0.0, 0.0, 0.31)), material="body", name="cabinet_body", material_class_id="metal.paint_coated")
    pedestal.visual(Box((0.38, 0.34, 0.18)), origin=Origin(xyz=(0.0, 0.0, 0.71)), material="body", name="control_head", material_class_id="metal.paint_coated")
    pedestal.visual(Box((0.34, 0.026, 0.135)), origin=Origin(xyz=(0.0, -0.185, 0.76), rpy=(math.radians(-8.0), 0.0, 0.0)),
                    material="edge", name="sloped_panel", material_class_id="metal.paint_coated")
    pedestal.visual(Box((0.33, 0.012, 0.32)), origin=Origin(xyz=(0.0, -0.176, 0.44)), material="edge", name="front_door_seam", material_class_id="metal.paint_coated")
    pedestal.visual(Box((0.28, 0.010, 0.055)), origin=Origin(xyz=(0.0, -0.183, 0.45)), material="yellow", name="pedestal_warning_label", appearance_only=AppearanceOnlySpec(kind="decal"))
    for i, x in enumerate([-0.13, 0.13]):
        pedestal.visual(Box((0.055, 0.40, 0.080)), origin=Origin(xyz=(x, 0.0, 0.04)), material="body", name=f"pedestal_foot_{i}", material_class_id="metal.paint_coated")
    pedestal.visual(Cylinder(radius=0.045, length=0.018), origin=Origin(xyz=(-0.125, -0.199, 0.805), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material="dark", name="gauge_bezel", material_class_id="metal.blackened_gunmetal")
    pedestal.visual(Cylinder(radius=0.035, length=0.020), origin=Origin(xyz=(-0.125, -0.211, 0.805), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material="white", name="gauge_face", material_class_id="plastic.opaque_glossy_molded")
    pedestal.visual(Box((0.050, 0.006, 0.006)), origin=Origin(xyz=(-0.112, -0.224, 0.812), rpy=(0.0, 0.0, math.radians(-25.0))),
                    material="black", name="gauge_needle", appearance_only=AppearanceOnlySpec(kind="overlay"))
    for i, (x, mat) in enumerate([(-0.025, "green"), (0.035, "red"), (0.095, "amber")]):
        pedestal.visual(Sphere(radius=0.016), origin=Origin(xyz=(x, -0.197, 0.812)), material=mat, name=f"indicator_light_{i}", material_class_id="tech.emissive_surface")


def _emit_pedestal_and_mount(ctx: ModuleBuildContext, r) -> None:
    model = ctx.model
    pedestal = model.part("control_pedestal")
    _emit_pedestal_visuals(pedestal, r)

    # FIXED the console onto the floor conduit end (origin honesty on both sides).
    mount_fixed(
        model,
        joint_name="frame_to_pedestal",
        parent="frame",
        child="control_pedestal",
        parent_anchor=(PEDESTAL_X, 0.0, CONDUIT_TOP_Z),
        child_anchor=(0.0, 0.0, 0.0),
    )


def _build_push_buttons(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialHydraulicPressConfig = ctx.config  # type: ignore[assignment]
    _emit_pedestal_and_mount(ctx, r)
    pedestal = model.get_part("control_pedestal")

    n = r.button_count
    # Row starts right of the gauge (at x=-0.125) and extends rightward.
    x0 = -0.020
    parts, joints = [], []
    for i in range(n):
        name = f"button_{i}"
        button = model.part(name)
        button.visual(Cylinder(radius=0.021, length=0.018), origin=Origin(xyz=(0.0, -0.009, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                      material=BUTTON_COLORS[i % len(BUTTON_COLORS)], name="button_cap", material_class_id="plastic.opaque_glossy_molded")
        button.visual(Cylinder(radius=0.014, length=0.010), origin=Origin(xyz=(0.0, 0.002, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                      material="dark", name="button_stem", material_class_id="metal.blackened_gunmetal")
        jn = f"pedestal_to_{name}"
        model.articulation(
            jn, ArticulationType.PRISMATIC, parent=pedestal, child=button,
            origin=Origin(xyz=(x0 + i * 0.042, -0.205, 0.755)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=12.0, velocity=0.06, lower=0.0, upper=0.008),
        )
        parts.append(name)
        joints.append(jn)

    return ModuleBuild(
        module_name="push_buttons",
        parts_emitted=["control_pedestal", *parts],
        internal_articulations=["frame_to_pedestal", *joints],
        interfaces={"downstream": _frame_downstream(r)},
    )


def _build_operating_lever(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedIndustrialHydraulicPressConfig = ctx.config  # type: ignore[assignment]
    _emit_pedestal_and_mount(ctx, r)
    pedestal = model.get_part("control_pedestal")

    # Pivot boss on the sloped panel (pedestal visual).
    pedestal.visual(
        Cylinder(radius=0.014, length=0.068),
        origin=Origin(xyz=(0.030, -0.224, 0.760), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark", name="lever_pivot_boss", material_class_id="metal.blackened_gunmetal",
    )
    lever = model.part("operating_lever")
    lever.visual(Cylinder(radius=0.020, length=0.038), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                 material="steel", name="lever_collar", material_class_id="metal.steel_bare")
    lever.visual(Box((0.014, 0.010, 0.140)), origin=Origin(xyz=(0.0, 0.0, 0.080)), material="dark", name="lever_shaft", material_class_id="metal.blackened_gunmetal")
    lever.visual(Sphere(radius=0.022), origin=Origin(xyz=(0.0, 0.0, 0.160)), material="black", name="lever_grip", material_class_id="rubber.smooth_plain")
    model.articulation(
        "pedestal_to_lever", ArticulationType.REVOLUTE, parent=pedestal, child=lever,
        origin=Origin(xyz=(0.030, -0.260, 0.760)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=25.0, velocity=1.5, lower=-r.lever_range, upper=r.lever_range),
    )
    return ModuleBuild(
        module_name="operating_lever",
        parts_emitted=["control_pedestal", "operating_lever"],
        internal_articulations=["frame_to_pedestal", "pedestal_to_lever"],
        interfaces={"downstream": _frame_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Factory registries + assembly
# --------------------------------------------------------------------------- #

BED_FACTORIES = {
    "fixed_bed": _build_fixed_bed,
    "height_adjustable_bed": _build_height_adjustable_bed,
    "sliding_bolster_bed": _build_sliding_bolster_bed,
}
CONTROL_FACTORIES = {
    "push_buttons": _build_push_buttons,
    "operating_lever": _build_operating_lever,
}


def _slots_for_config(r: ResolvedIndustrialHydraulicPressConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="frame", candidates={r.frame_form: _build_frame}, anchor_choice=r.frame_form),
        SlotSpec(slot_name="ram", candidates={r.platen_module: _build_ram}, anchor_choice=r.platen_module),
        SlotSpec(slot_name="bed", candidates={r.bed_module: BED_FACTORIES[r.bed_module]}, anchor_choice=r.bed_module),
        SlotSpec(slot_name="control", candidates={r.control_module: CONTROL_FACTORIES[r.control_module]},
                 anchor_choice=r.control_module),
    ]


def build_industrial_hydraulic_press(
    config: IndustrialHydraulicPressConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="industrial_hydraulic_press", assets=assets)
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


def build_seeded_industrial_hydraulic_press(seed: int) -> ArticulatedObject:
    return build_industrial_hydraulic_press(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    button_axis = f"buttons_{r.button_count}" if r.control_module == "push_buttons" else "buttons_na"
    return [
        ("frame", r.frame_form),
        ("ram", r.platen_module),
        ("bed", r.bed_module),
        ("bed_pin_count", f"pins_{r.bed_pin_count}"),
        ("control", r.control_module),
        ("button_count", button_axis),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r) -> None:
    parts = {p.name for p in model.parts}
    frame = model.get_part("frame")

    # Ram rod captured through the cylinder shell + gland ring.
    ram = model.get_part("ram")
    ctx.allow_overlap(frame, ram, elem_a="fixed_cylinder", elem_b="ram_rod",
                      reason="The polished ram rod runs inside the fixed hydraulic cylinder bore.")
    ctx.allow_overlap(frame, ram, elem_a="gland_ring", elem_b="ram_rod",
                      reason="The ram rod is captured through the cylinder gland ring.")

    pedestal = model.get_part("control_pedestal")

    # Push buttons seated through the panel face (cap flush + stem through).
    for i in range(r.button_count):
        name = f"button_{i}"
        if name in parts:
            for elem in ("button_stem", "button_cap"):
                ctx.allow_overlap(model.get_part(name), pedestal, elem_a=elem, elem_b="sloped_panel",
                                  reason="The push button seats against/through the control-panel face.")
    # Operating lever collar/shaft root sweeping around its captured pivot boss.
    if "operating_lever" in parts:
        for elem in ("lever_collar", "lever_shaft"):
            ctx.allow_overlap(model.get_part("operating_lever"), pedestal, elem_a=elem, elem_b="lever_pivot_boss",
                              reason="The lever collar/shaft is captured over and sweeps around the pivot boss.")

    # Sliding bolster shoes riding on the frame rails.
    if r.bed_module == "sliding_bolster_bed":
        bed = model.get_part("bed")
        for side in ("left", "right"):
            ctx.allow_overlap(frame, bed, elem_a=f"{side}_bolster_rail", elem_b=f"{side}_slide_shoe",
                              reason="The bolster slide shoe rides on the frame bolster rail.")


def _center(aabb) -> list[float] | None:
    if aabb is None:
        return None
    return [(aabb[0][i] + aabb[1][i]) / 2.0 for i in range(3)]


def _dist(a, b) -> float:
    ca, cb = _center(a), _center(b)
    if ca is None or cb is None:
        return 0.0
    return math.dist(ca, cb)


def _expect_ram(ctx, model, r) -> None:
    ram_joint = model.get_articulation("frame_to_ram")
    ctx.check(
        "ram joint is a downward vertical prismatic",
        ram_joint.articulation_type == ArticulationType.PRISMATIC
        and abs(ram_joint.axis[2]) > 0.9 and ram_joint.axis[2] < 0.0
        and ram_joint.motion_limits is not None and ram_joint.motion_limits.upper is not None,
        details=f"type={ram_joint.articulation_type}, axis={ram_joint.axis}, limits={ram_joint.motion_limits}",
    )
    ram = model.get_part("ram")
    rest = ctx.part_world_position(ram)
    with ctx.pose({ram_joint: r.ram_travel}):
        lowered = ctx.part_world_position(ram)
    ok = rest is not None and lowered is not None and lowered[2] < rest[2] - r.ram_travel * 0.7
    ctx.check("positive ram travel descends the ram vertically", ok, details=f"rest={rest}, lowered={lowered}")


def _expect_bed(ctx, model, r) -> None:
    bed_joint = model.get_articulation("frame_to_bed")
    if r.bed_module == "fixed_bed":
        ctx.check("fixed bed is a FIXED joint", bed_joint.articulation_type == ArticulationType.FIXED,
                  details=f"type={bed_joint.articulation_type}")
        return
    ctx.check("moving bed is prismatic", bed_joint.articulation_type == ArticulationType.PRISMATIC,
              details=f"type={bed_joint.articulation_type}")
    bed = model.get_part("bed")
    rest = ctx.part_world_position(bed)
    if r.bed_module == "height_adjustable_bed":
        with ctx.pose({bed_joint: r.bed_raise}):
            moved = ctx.part_world_position(bed)
        ok = rest is not None and moved is not None and moved[2] > rest[2] + min(r.bed_raise * 0.6, 0.015)
        ctx.check("height-adjustable bed rises on positive travel", ok, details=f"rest={rest}, raised={moved}")
    else:  # sliding_bolster_bed
        with ctx.pose({bed_joint: r.bolster_travel}):
            moved = ctx.part_world_position(bed)
        ok = rest is not None and moved is not None and moved[1] < rest[1] - r.bolster_travel * 0.6
        ctx.check("sliding bolster moves toward the operator", ok, details=f"rest={rest}, slid={moved}")


def _expect_control(ctx, model, r) -> None:
    if r.control_module == "operating_lever":
        lever_joint = model.get_articulation("pedestal_to_lever")
        lever = model.get_part("operating_lever")
        ctx.check("operating lever is a bounded revolute",
                  lever_joint.articulation_type == ArticulationType.REVOLUTE
                  and lever_joint.motion_limits is not None
                  and lever_joint.motion_limits.lower is not None
                  and lever_joint.motion_limits.lower < 0.0 < lever_joint.motion_limits.upper,
                  details=f"type={lever_joint.articulation_type}, limits={lever_joint.motion_limits}")
        rest = ctx.part_element_world_aabb(lever, elem="lever_grip")
        with ctx.pose({lever_joint: r.lever_range}):
            tilted = ctx.part_element_world_aabb(lever, elem="lever_grip")
        ctx.check("lever grip swings when posed", _dist(rest, tilted) > 0.04,
                  details=f"displacement={_dist(rest, tilted):.4f}")
        return

    joints = [model.get_articulation(f"pedestal_to_button_{i}") for i in range(r.button_count)]
    ctx.check("push buttons are prismatic controls",
              all(j.articulation_type == ArticulationType.PRISMATIC and j.motion_limits and j.motion_limits.upper for j in joints),
              details=f"n_buttons={len(joints)}")
    b0 = model.get_part("button_0")
    j0 = joints[0]
    rest = ctx.part_world_position(b0)
    with ctx.pose({j0: 0.008}):
        pressed = ctx.part_world_position(b0)
    ctx.check("button depresses when posed",
              rest is not None and pressed is not None and abs(pressed[1] - rest[1]) > 0.003,
              details=f"rest={rest}, pressed={pressed}")


def run_industrial_hydraulic_press_tests(
    model: ArticulatedObject,
    config: IndustrialHydraulicPressConfig,
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

    frame_visuals = {v.name for v in model.get_part("frame").visuals}
    ctx.check("frame carries the fixed hydraulic cylinder + gland",
              {"fixed_cylinder", "gland_ring", "cylinder_flange"}.issubset(frame_visuals),
              details=f"frame visuals sample={sorted(frame_visuals)[:8]}")

    _expect_ram(ctx, model, r)
    _expect_bed(ctx, model, r)
    _expect_control(ctx, model, r)

    # Rule 5: dynamic collision across sampled joint poses.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "IndustrialHydraulicPressConfig",
    "ResolvedIndustrialHydraulicPressConfig",
    "FrameForm",
    "PlatenModule",
    "BedModule",
    "ControlModule",
    "PressPalette",
    "build_industrial_hydraulic_press",
    "build_seeded_industrial_hydraulic_press",
    "config_from_seed",
    "resolve_config",
    "run_industrial_hydraulic_press_tests",
    "slot_choices_for_seed",
]
