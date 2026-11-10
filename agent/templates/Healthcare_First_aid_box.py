# SPDX-License-Identifier: Apache-2.0

"""Healthcare_First_aid_box — modular procedural template.

Category identity: a PORTABLE first-aid hard case — a rigid (or softly rounded
vintage-tin) rounded-rectangular box with a hinged top lid, one/two front
draw-latches, an interior of lift-out / cantilever / stacked compartment trays,
and a carry handle (folding top loop OR fixed recessed end grips). Hand-carried,
sits on a surface. NOT a wall-mounted first-aid cabinet (that overlaps the
existing Science/First_aid_cabinet template and is deliberately excluded).

Canonical frame: WIDTH along X (centered), DEPTH along Y (centered, FRONT at -Y,
REAR at +Y), height along Z with the base bottom on z=0. The lid hinges at the
rear top edge (REVOLUTE -X) and seats on the base rim. Front draw-latches pivot
about +X. A folding carry handle pivots about +X on the lid top center.

Slots (parallel-children hub; `base` is the grounded root):
  Slot A lid       : single_top_lid | clamshell_dual (+ front_flap drawbridge)
  Slot B interior  : single_lift_tray | cantilever_tiers | stacked_trays(N)
  Slot C handle    : folding_top_handle | fixed_side_grips (base visuals)
  Slot D body_form : rigid_rect | rounded_tin  (③ Primary Form Family)
  multiplicity     : latch_count {1,2}; stacked tray_count {2,3}

HARD RULES honored:
  * Red-cross-on-white-field decal + FIRST-AID label band are parent.visual on
    the front face / flap (Rule 1), host-derived from the front plane (Rule 4).
  * Every non-FIXED joint (lid, flap, latches, tray lifts, folding handle)
    declares a MatingContract to real faces (Rule 2); the cantilever arm pivot
    and clamshell draw-latch are genuine captured pins/hooks (mating omitted,
    grandfathered per Rule 2) with element-scoped allow_overlap.
  * The source cadquery `_hollow_open_box` / `_three_wall_base` /
    `_domed_lid_shell` shells are kept (no Box downgrade) — Rule 3.
  * palette_style drives every material (Rule ⑥); 6 first-aid colorways.

Canonical spec: articraft_template_authoring/specs_modular_v1/Healthcare_First_aid_box.md
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Enum domains
# ---------------------------------------------------------------------------
LidModule = Literal["single_top_lid", "clamshell_dual"]
InteriorModule = Literal["single_lift_tray", "cantilever_tiers", "stacked_trays"]
HandleModule = Literal["folding_top_handle", "fixed_side_grips"]
BodyForm = Literal["rigid_rect", "rounded_tin"]
PaletteStyle = Literal[
    "red_white",
    "white_red",
    "safety_green",
    "medical_orange",
    "olive_tin",
    "clinical_blue",
]

LID_MODULES: tuple[LidModule, ...] = ("single_top_lid", "clamshell_dual")
LID_WEIGHTS = (0.72, 0.28)
INTERIOR_MODULES: tuple[InteriorModule, ...] = (
    "single_lift_tray",
    "cantilever_tiers",
    "stacked_trays",
)
INTERIOR_WEIGHTS = (0.42, 0.28, 0.30)
HANDLE_MODULES: tuple[HandleModule, ...] = ("folding_top_handle", "fixed_side_grips")
HANDLE_WEIGHTS = (0.62, 0.38)
BODY_FORMS: tuple[BodyForm, ...] = ("rigid_rect", "rounded_tin")
BODY_FORM_WEIGHTS = (0.60, 0.40)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "red_white",
    "white_red",
    "safety_green",
    "medical_orange",
    "olive_tin",
    "clinical_blue",
)
LATCH_COUNTS: tuple[int, ...] = (1, 2)
LATCH_COUNT_WEIGHTS = (0.30, 0.70)
STACK_COUNTS: tuple[int, ...] = (2, 3)
STACK_COUNT_WEIGHTS = (0.5, 0.5)

# ---------------------------------------------------------------------------
# Geometric constants (proportions / small absolute hardware dims).
# ---------------------------------------------------------------------------
WALL = 0.006
BOTTOM = 0.006
FLAT_LID_T = 0.034          # flat-form lid thickness
DOME_RISE = 0.012           # rounded-tin crown rise
TRAY_H = 0.030
TRAY_FLOOR = 0.004
TRAY_WALL = 0.003
BASE_H_NOMINAL = 0.185      # single_top_lid full-height base
CASE_H_NOMINAL = 0.22       # clamshell total (split base/lid)

# ---------------------------------------------------------------------------
# Palettes (per-seed). Keys drive EVERY .visual material.
# painted-metal body/lid + plastic tray + chrome/dark hardware + red/white
# cross decal (field = backing square, cross = the bars).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "red_white": {
        "body": (0.70, 0.11, 0.10, 1.0),
        "lid": (0.62, 0.09, 0.08, 1.0),
        "tray": (0.90, 0.90, 0.87, 1.0),
        "hardware": (0.80, 0.81, 0.83, 1.0),
        "dark": (0.06, 0.06, 0.06, 1.0),
        "field": (0.93, 0.93, 0.91, 1.0),
        "cross": (0.72, 0.08, 0.07, 1.0),
        "handle": (0.20, 0.20, 0.22, 1.0),
    },
    "white_red": {
        "body": (0.90, 0.90, 0.88, 1.0),
        "lid": (0.84, 0.84, 0.82, 1.0),
        "tray": (0.86, 0.88, 0.90, 1.0),
        "hardware": (0.78, 0.79, 0.81, 1.0),
        "dark": (0.10, 0.10, 0.10, 1.0),
        "field": (0.74, 0.08, 0.07, 1.0),
        "cross": (0.95, 0.95, 0.93, 1.0),
        "handle": (0.25, 0.25, 0.27, 1.0),
    },
    "safety_green": {
        "body": (0.15, 0.42, 0.22, 1.0),
        "lid": (0.13, 0.37, 0.19, 1.0),
        "tray": (0.88, 0.90, 0.86, 1.0),
        "hardware": (0.80, 0.81, 0.83, 1.0),
        "dark": (0.05, 0.10, 0.06, 1.0),
        "field": (0.93, 0.94, 0.90, 1.0),
        "cross": (0.72, 0.08, 0.07, 1.0),
        "handle": (0.18, 0.20, 0.18, 1.0),
    },
    "medical_orange": {
        "body": (0.86, 0.42, 0.06, 1.0),
        "lid": (0.78, 0.37, 0.05, 1.0),
        "tray": (0.92, 0.90, 0.85, 1.0),
        "hardware": (0.30, 0.30, 0.32, 1.0),
        "dark": (0.10, 0.06, 0.02, 1.0),
        "field": (0.94, 0.94, 0.91, 1.0),
        "cross": (0.72, 0.08, 0.07, 1.0),
        "handle": (0.20, 0.18, 0.16, 1.0),
    },
    "olive_tin": {
        "body": (0.42, 0.44, 0.30, 1.0),
        "lid": (0.40, 0.42, 0.28, 1.0),
        "tray": (0.82, 0.80, 0.72, 1.0),
        "hardware": (0.46, 0.44, 0.39, 1.0),
        "dark": (0.08, 0.08, 0.06, 1.0),
        "field": (0.86, 0.82, 0.70, 1.0),
        "cross": (0.55, 0.05, 0.04, 1.0),
        "handle": (0.40, 0.38, 0.34, 1.0),
    },
    "clinical_blue": {
        "body": (0.20, 0.38, 0.62, 1.0),
        "lid": (0.17, 0.33, 0.55, 1.0),
        "tray": (0.88, 0.90, 0.92, 1.0),
        "hardware": (0.80, 0.81, 0.83, 1.0),
        "dark": (0.05, 0.08, 0.12, 1.0),
        "field": (0.93, 0.94, 0.95, 1.0),
        "cross": (0.72, 0.08, 0.07, 1.0),
        "handle": (0.22, 0.24, 0.28, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Public + resolved config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FirstAidBoxConfig:
    lid_module: LidModule = "single_top_lid"
    interior_module: InteriorModule = "single_lift_tray"
    handle_module: HandleModule = "folding_top_handle"
    body_form: BodyForm = "rigid_rect"
    latch_count: int = 2
    tray_count: int = 3
    palette_style: PaletteStyle = "red_white"
    width_scale: float = 1.0
    depth_scale: float = 1.0
    height_scale: float = 1.0
    name: str = "reference_first_aid_box"


@dataclass(frozen=True)
class ResolvedFirstAidBoxConfig:
    lid_module: LidModule
    interior_module: InteriorModule
    handle_module: HandleModule
    body_form: BodyForm
    latch_count: int
    tray_count: int  # active count for stacked_trays; 1 single; 2 cantilever
    palette_style: PaletteStyle
    W: float
    D: float
    base_h: float
    lid_h: float
    radius: float
    fillet_tb: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# ---------------------------------------------------------------------------
# Compatibility gating.
# ---------------------------------------------------------------------------
def _gate(lid: LidModule, interior: InteriorModule) -> InteriorModule:
    # Cantilever tiers / stacked trays need a full-height base cavity; the
    # clamshell splits the case into shallow halves -> only a single lift tray
    # fits (matches the clamshell 5-star source, which had one tray).
    if lid == "clamshell_dual":
        return "single_lift_tray"
    return interior


# ---------------------------------------------------------------------------
# Procedural sampler (seed 0 not special).
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> FirstAidBoxConfig:
    rng = random.Random(seed)
    lid = rng.choices(LID_MODULES, weights=LID_WEIGHTS, k=1)[0]
    interior = rng.choices(INTERIOR_MODULES, weights=INTERIOR_WEIGHTS, k=1)[0]
    interior = _gate(lid, interior)
    handle = rng.choices(HANDLE_MODULES, weights=HANDLE_WEIGHTS, k=1)[0]
    body_form = rng.choices(BODY_FORMS, weights=BODY_FORM_WEIGHTS, k=1)[0]
    latch_count = rng.choices(LATCH_COUNTS, weights=LATCH_COUNT_WEIGHTS, k=1)[0]
    tray_count = rng.choices(STACK_COUNTS, weights=STACK_COUNT_WEIGHTS, k=1)[0]
    palette = rng.choice(PALETTE_STYLES)
    return FirstAidBoxConfig(
        lid_module=lid,
        interior_module=interior,
        handle_module=handle,
        body_form=body_form,
        latch_count=int(latch_count),
        tray_count=int(tray_count),
        palette_style=palette,
        width_scale=round(rng.uniform(0.90, 1.10), 3),
        depth_scale=round(rng.uniform(0.90, 1.10), 3),
        height_scale=round(rng.uniform(0.90, 1.10), 3),
        name=f"seeded_first_aid_box_{seed}",
    )


def resolve_config(config: FirstAidBoxConfig) -> ResolvedFirstAidBoxConfig:
    if config.lid_module not in LID_MODULES:
        raise ValueError(f"Unsupported lid_module: {config.lid_module}")
    if config.handle_module not in HANDLE_MODULES:
        raise ValueError(f"Unsupported handle_module: {config.handle_module}")
    if config.body_form not in BODY_FORMS:
        raise ValueError(f"Unsupported body_form: {config.body_form}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    interior = _gate(config.lid_module, config.interior_module)
    if interior not in INTERIOR_MODULES:
        raise ValueError(f"Unsupported interior_module: {interior}")

    latch_count = config.latch_count if config.latch_count in LATCH_COUNTS else 2
    if interior == "stacked_trays":
        tray_count = config.tray_count if config.tray_count in STACK_COUNTS else 3
    elif interior == "cantilever_tiers":
        tray_count = 2
    else:
        tray_count = 1

    w_scale = _clamp(config.width_scale, 0.90, 1.10)
    d_scale = _clamp(config.depth_scale, 0.90, 1.10)
    h_scale = _clamp(config.height_scale, 0.90, 1.10)

    W = round(0.30 * w_scale, 4)
    D = round(0.12 * d_scale, 4)

    radius = 0.020 if config.body_form == "rigid_rect" else 0.026
    fillet_tb = 0.0 if config.body_form == "rigid_rect" else 0.005

    if config.lid_module == "clamshell_dual":
        case_h = round(CASE_H_NOMINAL * h_scale, 4)
        base_h = round(case_h * 0.5, 4)
        lid_h = round(case_h * 0.5, 4)
    else:
        base_h = round(BASE_H_NOMINAL * h_scale, 4)
        lid_h = FLAT_LID_T if config.body_form == "rigid_rect" else (FLAT_LID_T + DOME_RISE)

    return ResolvedFirstAidBoxConfig(
        lid_module=config.lid_module,
        interior_module=interior,
        handle_module=config.handle_module,
        body_form=config.body_form,
        latch_count=latch_count,
        tray_count=tray_count,
        palette_style=config.palette_style,
        W=W,
        D=D,
        base_h=base_h,
        lid_h=lid_h,
        radius=radius,
        fillet_tb=fillet_tb,
        name=config.name or "first_aid_box",
    )


# ---------------------------------------------------------------------------
# slot_choices
# ---------------------------------------------------------------------------
def _slot_choices_for_resolved(r: ResolvedFirstAidBoxConfig) -> list[tuple[str, str]]:
    interior_label = r.interior_module
    if r.interior_module == "stacked_trays":
        interior_label = f"stacked_trays_{r.tray_count}"
    return [
        ("lid_module", r.lid_module),
        ("interior_module", interior_label),
        ("handle_module", r.handle_module),
        ("body_form", r.body_form),
        ("latch", f"draw_latch_x{r.latch_count}"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return _slot_choices_for_resolved(resolve_config(config_from_seed(seed)))


# ===========================================================================
# Geometry helpers (kept from the 5-star sources; no Box downgrade).
# ===========================================================================
def _rounded_slab(width: float, depth: float, height: float, radius: float, name: str):
    return mesh_from_geometry(
        ExtrudeGeometry(
            rounded_rect_profile(width, depth, radius, corner_segments=10),
            height,
            center=True,
        ),
        name,
    )


def _hollow_open_box(
    width: float,
    depth: float,
    height: float,
    wall: float,
    radius: float,
    name: str,
    *,
    open_face: str = ">Z",
    fillet_top_bottom: float = 0.0,
):
    """Rounded-rect container hollowed via a true CAD shell (open at one face)."""
    box = cq.Workplane("XY").box(width, depth, height).edges("|Z").fillet(radius)
    if fillet_top_bottom > 0.0:
        box = box.edges("#Z").fillet(fillet_top_bottom)
    shell = box.faces(open_face).shell(-wall)
    return mesh_from_cadquery(shell, name, tolerance=0.0008)


def _three_wall_base(
    width: float,
    depth: float,
    height: float,
    wall: float,
    radius: float,
    name: str,
):
    """Clamshell base: floor + back wall + two side walls (front + top open)."""
    outer = cq.Workplane("XY").box(width, depth, height).edges("|Z").fillet(radius)
    shelled = outer.faces(">Z").shell(-wall)
    cutter = (
        cq.Workplane("XY")
        .box(width + 0.010, wall + 0.006, height + 0.010)
        .translate((0.0, -(depth / 2.0 - wall / 2.0), 0.0))
    )
    return mesh_from_cadquery(shelled.cut(cutter), name, tolerance=0.0008)


def _domed_lid_shell(
    width: float,
    depth: float,
    skirt_height: float,
    dome_rise: float,
    wall: float,
    corner_radius: float,
    name: str,
):
    """Vintage-tin domed lid: rounded-rect skirt capped by a gentle dome crown."""
    total_h = skirt_height + dome_rise
    body = cq.Workplane("XY").box(width, depth, total_h).edges("|Z").fillet(corner_radius)
    dome_fillet = min(dome_rise * 1.1, depth * 0.35)
    body = body.edges(">Z").fillet(dome_fillet)
    shell = body.faces("<Z").shell(-wall)
    return mesh_from_cadquery(shell, name, tolerance=0.0008)


def _build_tray(part, mats, tw: float, td: float) -> None:
    """Open compartment tray: floor + perimeter rim + 3x2 dividers + finger pull."""
    wall_h = TRAY_H - TRAY_FLOOR
    wall_cz = TRAY_FLOOR + wall_h / 2.0
    hx = tw / 2.0
    hy = td / 2.0
    plastic = mats["tray"]
    part.visual(Box((tw, td, TRAY_FLOOR)), origin=Origin(xyz=(0.0, 0.0, TRAY_FLOOR / 2.0)),
                material=plastic, name="tray_floor", material_class_id="plastic.opaque_glossy_molded")
    part.visual(Box((TRAY_WALL, td, wall_h)),
                origin=Origin(xyz=(-(hx - TRAY_WALL / 2.0), 0.0, wall_cz)),
                material=plastic, name="tray_wall_left", material_class_id="plastic.opaque_glossy_molded")
    part.visual(Box((TRAY_WALL, td, wall_h)),
                origin=Origin(xyz=(hx - TRAY_WALL / 2.0, 0.0, wall_cz)),
                material=plastic, name="tray_wall_right", material_class_id="plastic.opaque_glossy_molded")
    part.visual(Box((tw, TRAY_WALL, wall_h)),
                origin=Origin(xyz=(0.0, -(hy - TRAY_WALL / 2.0), wall_cz)),
                material=plastic, name="tray_wall_front", material_class_id="plastic.opaque_glossy_molded")
    part.visual(Box((tw, TRAY_WALL, wall_h)),
                origin=Origin(xyz=(0.0, hy - TRAY_WALL / 2.0, wall_cz)),
                material=plastic, name="tray_wall_back", material_class_id="plastic.opaque_glossy_molded")
    interior_depth = td - 2.0 * TRAY_WALL
    interior_width = tw - 2.0 * TRAY_WALL
    for i, x in enumerate((-tw / 6.0, tw / 6.0)):
        part.visual(Box((TRAY_WALL, interior_depth, wall_h)),
                    origin=Origin(xyz=(x, 0.0, wall_cz)),
                    material=plastic, name=f"divider_col_{i}", material_class_id="plastic.opaque_glossy_molded")
    part.visual(Box((interior_width, TRAY_WALL, wall_h)),
                origin=Origin(xyz=(0.0, 0.0, wall_cz)),
                material=plastic, name="divider_row", material_class_id="plastic.opaque_glossy_molded")
    part.visual(Box((0.045, 0.005, 0.009)),
                origin=Origin(xyz=(0.0, -hy - 0.0015, TRAY_H - 0.006)),
                material=plastic, name="front_pull", material_class_id="plastic.opaque_glossy_molded")


def _add_medical_cross(part, mats, *, front_y: float, z_center: float, scale: float) -> None:
    """Red-cross-on-white-field decal fused as parent.visual on the front face.

    Host-derived: sits on the front plane ``front_y`` (the body/flap front), sized
    off the body height; hugs the flat front across ③/⑤ changes (Rule 4).
    """
    s = scale
    # White field backing square: straddles the front face (embeds into the wall
    # -> supported, not a floating island) while staying visible on the outside.
    part.visual(Box((0.120 * s, 0.0018, 0.120 * s)),
                origin=Origin(xyz=(0.0, front_y, z_center)),
                material=mats["field"], name="cross_field", appearance_only=AppearanceOnlySpec(kind="decal"))
    # Red cross bars, proud of the field (overlap it -> connected).
    part.visual(Box((0.034 * s, 0.0016, 0.090 * s)),
                origin=Origin(xyz=(0.0, front_y - 0.0009, z_center)),
                material=mats["cross"], name="cross_vertical", appearance_only=AppearanceOnlySpec(kind="decal"))
    part.visual(Box((0.090 * s, 0.0016, 0.034 * s)),
                origin=Origin(xyz=(0.0, front_y - 0.0010, z_center)),
                material=mats["cross"], name="cross_horizontal", appearance_only=AppearanceOnlySpec(kind="decal"))


def _latch_x_positions(count: int, W: float) -> list[float]:
    if count <= 1:
        return [0.0]
    xl = 0.074 * (W / 0.30)
    return [-xl, xl]


# ===========================================================================
# BASE hub (root part).
# ===========================================================================
def _build_base(model, r: ResolvedFirstAidBoxConfig, mats):
    W, D, base_h = r.W, r.D, r.base_h
    base = model.part("base")
    cream = mats["body"]
    dark = mats["dark"]
    metal = mats["hardware"]

    clamshell = r.lid_module == "clamshell_dual"
    base_seat = "base_shell" if clamshell else "base_wall"
    if clamshell:
        base.visual(
            _three_wall_base(W, D, base_h, WALL, r.radius, "base_shell"),
            origin=Origin(xyz=(0.0, 0.0, base_h / 2.0)),
            material=cream, name="base_shell", material_class_id="metal.paint_coated",
        )
    else:
        base.visual(
            _hollow_open_box(W, D, base_h, WALL, r.radius, "base_wall",
                             fillet_top_bottom=r.fillet_tb),
            origin=Origin(xyz=(0.0, 0.0, base_h / 2.0)),
            material=cream, name="base_wall", material_class_id="metal.paint_coated",
        )
    # Dark interior floor pad (reads as a hollow recess).
    base.visual(Box((W - 2.8 * WALL, D - 2.8 * WALL, 0.0012)),
                origin=Origin(xyz=(0.0, 0.0, WALL + 0.001)),
                material=dark, name="empty_compartment", material_class_id="plastic.opaque_generic")

    # Rear hinge barrel (lid pivot hardware). Embedded into the rear rim corner
    # so it stays connected across the rounded-tin top-edge fillet.
    base.visual(
        Cylinder(radius=0.005, length=W * 0.74),
        origin=Origin(xyz=(0.0, D / 2.0 - 0.003, base_h - 0.002), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=metal, name="rear_hinge_barrel", material_class_id="metal.stainless_matte",
    )

    # Medical cross decal (④) on the front face for the single-lid form; for the
    # clamshell it goes on the front_flap instead.
    if not clamshell:
        _add_medical_cross(base, mats, front_y=-D / 2.0, z_center=base_h * 0.55,
                           scale=_clamp(base_h / 0.185, 0.85, 1.15))

    # Front draw-latch strikes (single-lid: on the real front wall).
    if not clamshell:
        for i, x in enumerate(_latch_x_positions(r.latch_count, W)):
            base.visual(Box((0.040, 0.004, 0.020)),
                        origin=Origin(xyz=(x, -D / 2.0 - 0.002, base_h - 0.023)),
                        material=metal, name=f"latch_strike_{i}", material_class_id="metal.stainless_matte")

    # Clamshell: front-bottom hinge barrel (the flap is a bottom-hinged
    # drawbridge; its base attachment is this coaxial pin-in-barrel hinge).
    if clamshell:
        base.visual(
            Cylinder(radius=0.004, length=W * 0.74),
            origin=Origin(xyz=(0.0, -D / 2.0 + WALL + 0.004, BOTTOM + 0.004),
                          rpy=(0.0, math.pi / 2.0, 0.0)),
            material=metal, name="front_hinge_barrel", material_class_id="metal.stainless_matte",
        )
    return base, base_seat


# ===========================================================================
# SLOT C alt: fixed_side_grips — parent.visual on the base short ends.
# ===========================================================================
def _build_side_grips(base, r: ResolvedFirstAidBoxConfig, mats) -> None:
    W, base_h = r.W, r.base_h
    dark = mats["dark"]
    cream = mats["body"]
    metal = mats["hardware"]
    rd = 0.012      # recess depth (into end wall)
    rw = 0.058      # recess width (Y)
    rh = 0.026      # recess height (Z)
    bar_r = 0.0035
    bar_len = 0.048
    hz = base_h * 0.52
    for side, sx in (("left", -1.0), ("right", 1.0)):
        x_outer = sx * W / 2.0
        x_recess = x_outer - sx * (rd / 2.0 - 0.001)
        base.visual(Box((rd, rw, rh)), origin=Origin(xyz=(x_recess, 0.0, hz)),
                    material=dark, name=f"end_handle_recess_{side}", material_class_id="plastic.opaque_generic")
        base.visual(Box((0.004, rw + 0.012, rh + 0.012)),
                    origin=Origin(xyz=(x_outer + sx * 0.001, 0.0, hz)),
                    material=cream, name=f"end_handle_rim_{side}", material_class_id="metal.paint_coated")
        base.visual(Cylinder(radius=bar_r, length=bar_len),
                    origin=Origin(xyz=(x_recess, 0.0, hz), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=metal, name=f"end_handle_bar_{side}", material_class_id="metal.stainless_matte")


# ===========================================================================
# SLOT A: lid (+ optional clamshell front flap).
# ===========================================================================
def _build_lid_geometry(lid, r: ResolvedFirstAidBoxConfig, mats, *, latch_xs) -> str:
    """Populate the lid part. Local frame origin = rear hinge axis; lid extends
    toward -Y. Returns the seat visual name (the -Z face that meets the rim)."""
    W, D, lid_h = r.W, r.D, r.lid_h
    cream = mats["lid"]
    dark = mats["dark"]
    metal = mats["hardware"]
    if r.body_form == "rounded_tin":
        skirt_h = lid_h - DOME_RISE
        lid.visual(
            _domed_lid_shell(W, D, skirt_h, DOME_RISE, WALL, r.radius, "lid_dome"),
            origin=Origin(xyz=(0.0, -D / 2.0, lid_h / 2.0)),
            material=cream, name="lid_dome", material_class_id="metal.paint_coated",
        )
        seat = "lid_dome"
    else:
        lid.visual(
            _hollow_open_box(W, D, lid_h, WALL, r.radius, "lid_skirt", open_face="<Z"),
            origin=Origin(xyz=(0.0, -D / 2.0, lid_h / 2.0)),
            material=cream, name="lid_skirt", material_class_id="metal.paint_coated",
        )
        lid.visual(
            _rounded_slab(W, D, WALL, r.radius, "lid_top"),
            origin=Origin(xyz=(0.0, -D / 2.0, lid_h - WALL / 2.0)),
            material=cream, name="lid_top", material_class_id="metal.paint_coated",
        )
        seat = "lid_skirt"
    lid.visual(Box((W - 3.0 * WALL, D - 3.0 * WALL, 0.0012)),
               origin=Origin(xyz=(0.0, -D / 2.0, 0.0010)),
               material=dark, name="dark_lid_liner", material_class_id=("plastic.flexible_bubble_wrap" if r.body_form == "rigid_rect" else "plastic.opaque_generic"))
    # Latch keepers on the lid front (the draw-latch hooks over these).
    for i, x in enumerate(latch_xs):
        lid.visual(Box((0.044, 0.004, 0.018)),
                   origin=Origin(xyz=(x, -D - 0.002, 0.013)),
                   material=metal, name=f"latch_keeper_{i}", material_class_id="metal.stainless_matte")
    # Handle mounts (folding handle only): on the lid top center.
    if r.handle_module == "folding_top_handle":
        for i, x in enumerate((-0.105 * (W / 0.30), 0.105 * (W / 0.30))):
            lid.visual(Box((0.030, 0.020, 0.004)),
                       origin=Origin(xyz=(x, -D / 2.0, lid_h + 0.002)),
                       material=metal, name=f"handle_mount_{i}", material_class_id="metal.stainless_matte")
    return seat


def _build_lid(model, base, r, mats, *, base_seat, latch_xs, overlaps):
    D, base_h = r.D, r.base_h
    lid = model.part("lid")
    seat = _build_lid_geometry(lid, r, mats, latch_xs=latch_xs)
    origin = (0.0, D / 2.0, base_h)
    model.articulation(
        "base_to_lid",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lid,
        origin=Origin(xyz=origin),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=1.85),
        mating=MatingContract(
            parent_face_geometry=base_seat, parent_face_side="positive_z",
            child_face_geometry=seat, child_face_side="negative_z",
            contact_tol=0.006,
        ),
    )
    overlaps.append(("lid", "base", seat, base_seat,
                     "Closed lid rim seats on the base rim."))
    overlaps.append(("lid", "base", seat, "rear_hinge_barrel",
                     "Lid skirt laps the rear hinge barrel it pivots on."))
    return lid, seat


def _build_front_flap(model, base, r, mats, *, overlaps):
    W, D, base_h = r.W, r.D, r.base_h
    cream = mats["body"]
    metal = mats["hardware"]
    flap = model.part("front_flap")
    flap_h = base_h - BOTTOM - 0.002
    flap.visual(Box((W - 2.0 * WALL, WALL, flap_h)),
                origin=Origin(xyz=(0.0, WALL / 2.0, flap_h / 2.0 + BOTTOM)),
                material=cream, name="flap_panel", material_class_id="metal.paint_coated")
    # Medical cross on the flap outer face (clamshell decal host).
    _add_medical_cross(flap, mats, front_y=0.0, z_center=flap_h / 2.0 + BOTTOM,
                       scale=_clamp(base_h / 0.185, 0.75, 1.05))
    # Latch-catch tabs near the top of the flap inner face.
    for i, x in enumerate(_latch_x_positions(r.latch_count, W)):
        flap.visual(Box((0.040, 0.004, 0.016)),
                    origin=Origin(xyz=(x, WALL + 0.002, base_h - 0.018)),
                    material=metal, name=f"flap_catch_{i}", material_class_id="metal.stainless_matte")
    origin = (0.0, -D / 2.0, 0.0)
    # Bottom-hinged drawbridge: the flap pivots on the coaxial front_hinge_barrel
    # (a genuine pin-in-barrel hinge). No two flat faces are in contact, so the
    # MatingContract is omitted and grandfathered per AUTHORING Rule 2; the
    # captured-hinge overlap is declared element-scoped below.
    model.articulation(
        "base_to_front_flap",
        ArticulationType.REVOLUTE,
        parent=base,
        child=flap,
        origin=Origin(xyz=origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=2.0, lower=0.0, upper=1.50),
    )
    overlaps.append(("front_flap", "base", "flap_panel", "front_hinge_barrel",
                     "Flap laps the front hinge barrel it pivots on (captured pin)."))
    return flap


# ===========================================================================
# SLOT B: interior trays.
# ===========================================================================
def _tray_rest_levels(r: ResolvedFirstAidBoxConfig, n: int) -> list[float]:
    top = r.base_h - TRAY_H - 0.010
    if n <= 1:
        return [top]
    low = r.base_h * 0.24
    step = (top - low) / (n - 1)
    return [low + i * step for i in range(n)]


def _build_lift_trays(model, base, r, mats, *, overlaps, n: int):
    """single_lift_tray (n=1) or stacked_trays (n>=2): each PRISMATIC +z on ledges."""
    W, D, base_h = r.W, r.D, r.base_h
    cream = mats["body"]
    tw = W - 0.035
    td = D - 0.030
    levels = _tray_rest_levels(r, n)
    tray_parts = []
    for ti, rest_z in enumerate(levels):
        # Side ledges carrying this tray level.
        for si, x in enumerate((-(W / 2.0 - 0.016), (W / 2.0 - 0.016))):
            base.visual(Box((0.024, td + 0.004, 0.004)),
                        origin=Origin(xyz=(x, 0.0, rest_z - 0.002)),
                        material=cream, name=f"tray_ledge_{ti}_{si}", material_class_id="metal.paint_coated")
        tray = model.part(f"tray_{ti}")
        _build_tray(tray, mats, tw, td)
        travel = base_h + 0.012 - rest_z
        model.articulation(
            f"base_to_tray_{ti}",
            ArticulationType.PRISMATIC,
            parent=base,
            child=tray,
            origin=Origin(xyz=(0.0, 0.0, rest_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=4.0, velocity=0.6, lower=0.0, upper=travel),
            mating=MatingContract(
                parent_face_geometry=f"tray_ledge_{ti}_0", parent_face_side="positive_z",
                child_face_geometry="tray_floor", child_face_side="negative_z",
                contact_tol=0.004,
            ),
        )
        overlaps.append((f"tray_{ti}", "lid",
                         "sequenced: tray lifts out only after the lid is opened"))
        overlaps.append((f"tray_{ti}", "handle",
                         "sequenced: tray rises past the lid-mounted handle only after the lid opens"))
        tray_parts.append(f"tray_{ti}")
    # Stacked trays are removed top-down: lifting a lower tray clears only once
    # the trays above it are out.
    for a in range(len(tray_parts)):
        for b in range(a + 1, len(tray_parts)):
            overlaps.append((tray_parts[a], tray_parts[b],
                             "stacked trays removed top-down; lower clears after upper is out"))
    return tray_parts


def _build_cantilever(model, base, r, mats, *, overlaps):
    """cantilever_tiers: 2 link arms REVOLUTE +Y (tiered), tray FIXED to each tip."""
    W, D, base_h = r.W, r.D, r.base_h
    metal = mats["hardware"]
    arm_pivot_x = W / 2.0 - WALL - 0.004
    # Pivots tiered high enough that a fully fanned arm lifts its tray above the
    # rim; the trays still nest below the rim at rest.
    pivot_zs = (0.50 * base_h, 0.76 * base_h)
    arm_len = W * 0.34
    arm_w = 0.014
    arm_t = 0.003
    open_angle = 1.50
    tw = min(0.12, W * 0.40)
    td = D * 0.66
    tray_parts = []
    for i, pivot_z in enumerate(pivot_zs):
        # Pivot boss on the inner side wall (captured hinge housing).
        base.visual(Cylinder(radius=0.006, length=0.010),
                    origin=Origin(xyz=(arm_pivot_x, 0.0, pivot_z), rpy=(0.0, math.pi / 2.0, 0.0)),
                    material=metal, name=f"arm_pivot_boss_{i}", material_class_id="metal.stainless_matte")
        arm = model.part(f"tray_arm_{i}")
        arm.visual(Box((arm_len, arm_w, arm_t)),
                   origin=Origin(xyz=(-arm_len / 2.0, 0.0, 0.0)),
                   material=metal, name=f"arm_bar_{i}", material_class_id="metal.stainless_matte")
        arm.visual(Cylinder(radius=0.004, length=0.016),
                   origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                   material=metal, name=f"arm_pivot_pin_{i}", material_class_id="metal.stainless_matte")
        arm.visual(Box((0.030, arm_w, 0.004)),
                   origin=Origin(xyz=(-arm_len, 0.0, 0.003)),
                   material=metal, name=f"arm_cradle_{i}", material_class_id="metal.stainless_matte")
        # Captured-pin hinge: coaxial pin-in-boss -> mating omitted (grandfathered),
        # element-scoped allow_overlap declared instead (Rule 2).
        model.articulation(
            f"base_to_tray_arm_{i}",
            ArticulationType.REVOLUTE,
            parent=base,
            child=arm,
            origin=Origin(xyz=(arm_pivot_x, 0.0, pivot_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=5.0, velocity=1.5, lower=0.0, upper=open_angle),
        )
        overlaps.append(("base", f"tray_arm_{i}", f"arm_pivot_boss_{i}", f"arm_pivot_pin_{i}",
                         "Arm pivot pin is a captured hinge pin seated in its boss."))
        overlaps.append(("base", f"tray_arm_{i}", f"arm_pivot_boss_{i}", f"arm_bar_{i}",
                         "Arm root laps its pivot boss at the hinge as it swings."))
        # The fanning tray + arm sweep up past the rim, brushing the shell wall
        # (tackle-box cantilever mechanism) — a real sweep allowance.
        overlaps.append((f"tray_{i}", "base",
                         "cantilever tray sweeps up past the rim during fan-out"))
        overlaps.append((f"tray_arm_{i}", "base",
                         "cantilever arm sweeps up past the rim during fan-out"))
        # Tray FIXED on the arm tip (arm_cradle +z <-> tray_floor -z).
        tray = model.part(f"tray_{i}")
        _build_tray(tray, mats, tw, td)
        model.articulation(
            f"tray_arm_{i}_to_tray_{i}",
            ArticulationType.FIXED,
            parent=arm,
            child=tray,
            origin=Origin(xyz=(-arm_len, 0.0, 0.005)),
            mating=MatingContract(
                parent_face_geometry=f"arm_cradle_{i}", parent_face_side="positive_z",
                child_face_geometry="tray_floor", child_face_side="negative_z",
                contact_tol=0.006,
            ),
        )
        overlaps.append((f"tray_{i}", "lid",
                         "sequenced: cantilever tray fans out only after the lid is opened"))
        overlaps.append((f"tray_arm_{i}", "lid",
                         "sequenced: cantilever arm swings up only after the lid is opened"))
        # The folding handle rides on the lid; a fanning tray/arm clears it only
        # once the lid (and its handle) is swung open.
        overlaps.append((f"tray_{i}", "handle",
                         "sequenced: cantilever tray fans past the lid-mounted handle only after the lid opens"))
        overlaps.append((f"tray_arm_{i}", "handle",
                         "sequenced: cantilever arm swings past the lid-mounted handle only after the lid opens"))
        tray_parts.append((arm, tray))
    # The two tiered trays nest one above the other when folded; opening one arm
    # sweeps its tray past the other tier.
    overlaps.append(("tray_0", "tray_1",
                     "tiered cantilever trays nest/pass during fan-out (sequenced)"))
    overlaps.append(("tray_arm_0", "tray_1",
                     "lower arm sweeps past the upper tier during fan-out (sequenced)"))
    overlaps.append(("tray_arm_1", "tray_0",
                     "upper arm sweeps past the lower tier during fan-out (sequenced)"))
    overlaps.append(("tray_arm_0", "tray_arm_1",
                     "tiered arms share the side-wall pivot column and sweep past each other"))
    return tray_parts


# ===========================================================================
# SLOT C: folding carry handle (loop REVOLUTE +X on the lid top).
# ===========================================================================
def _build_folding_handle(model, lid, r, mats, *, overlaps):
    W, D, lid_h = r.W, r.D, r.lid_h
    metal = mats["hardware"]
    handle_mat = mats["handle"]
    handle = model.part("handle")
    hx = 0.105 * (W / 0.30)
    handle_geom = tube_from_spline_points(
        [
            (-hx, 0.0, 0.0),
            (-hx, 0.0, 0.052),
            (-0.74 * hx, 0.0, 0.078),
            (0.0, 0.0, 0.086),
            (0.74 * hx, 0.0, 0.078),
            (hx, 0.0, 0.052),
            (hx, 0.0, 0.0),
        ],
        radius=0.003,
        samples_per_segment=12,
        radial_segments=16,
        cap_ends=True,
    )
    handle.visual(mesh_from_geometry(handle_geom, "handle_loop"),
                  material=handle_mat, name="handle_loop", material_class_id="plastic.opaque_glossy_molded")
    for i, x in enumerate((-hx, hx)):
        handle.visual(Box((0.018, 0.014, 0.006)),
                      origin=Origin(xyz=(x, 0.0, 0.0)),
                      material=metal, name=f"handle_pivot_{i}", material_class_id="metal.stainless_matte")
    origin = (0.0, -D / 2.0, lid_h + 0.007)
    model.articulation(
        "lid_to_handle",
        ArticulationType.REVOLUTE,
        parent=lid,
        child=handle,
        origin=Origin(xyz=origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.5, lower=0.0, upper=1.45),
        mating=MatingContract(
            parent_face_geometry="handle_mount_0", parent_face_side="positive_z",
            child_face_geometry="handle_pivot_0", child_face_side="negative_z",
            contact_tol=0.006,
        ),
    )
    overlaps.append(("handle", "lid", "handle_pivot_0", "handle_mount_0",
                     "Handle pivot seats on its lid mount boss."))
    overlaps.append(("handle", "lid", "handle_pivot_1", "handle_mount_1",
                     "Handle pivot seats on its lid mount boss."))
    overlaps.append(("handle", "lid",
                     "folding handle lies against the lid top when folded down"))
    return handle


# ===========================================================================
# Front draw-latches (REVOLUTE +X on the base front).
# ===========================================================================
def _build_latches(model, base, r, mats, *, clamshell, overlaps):
    D, base_h = r.D, r.base_h
    metal = mats["hardware"]
    handle_mat = mats["handle"]
    for i, x in enumerate(_latch_x_positions(r.latch_count, r.W)):
        latch = model.part(f"latch_{i}")
        latch.visual(Box((0.030, 0.003, 0.052)),
                     origin=Origin(xyz=(0.0, 0.0, 0.026)),
                     material=metal, name="clasp_plate", material_class_id="metal.stainless_matte")
        latch.visual(Box((0.038, 0.004, 0.007)),
                     origin=Origin(xyz=(0.0, 0.0, 0.052)),
                     material=handle_mat, name="clasp_lip", material_class_id="plastic.opaque_glossy_molded")
        latch.visual(Cylinder(radius=0.004, length=0.036),
                     origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                     material=metal, name="clasp_pivot", material_class_id="metal.stainless_matte")
        origin = (x, -D / 2.0 - 0.0055, base_h - 0.040)
        kwargs: dict = {}
        if not clamshell:
            # Single-lid: real strike-plate face on the front wall.
            kwargs["mating"] = MatingContract(
                parent_face_geometry=f"latch_strike_{i}", parent_face_side="negative_y",
                child_face_geometry="clasp_plate", child_face_side="positive_y",
                contact_tol=0.006,
            )
        # Clamshell front is the flap; the draw-latch is a captured hook over the
        # lid keeper (no flat base face) -> mating omitted, grandfathered (Rule 2).
        model.articulation(
            f"base_to_latch_{i}",
            ArticulationType.REVOLUTE,
            parent=base,
            child=latch,
            origin=Origin(xyz=origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1.5, velocity=3.0, lower=0.0, upper=1.20),
            **kwargs,
        )
        if not clamshell:
            overlaps.append((f"latch_{i}", "base", "clasp_plate", f"latch_strike_{i}",
                             "Draw-latch plate seats against its front strike plate."))
        overlaps.append((f"latch_{i}", "lid", "clasp_lip", f"latch_keeper_{i}",
                         "Draw-latch hooks over the lid keeper when closed."))
        if clamshell:
            overlaps.append((f"latch_{i}", "front_flap",
                             "front draw-latch overlaps the flap edge region when released (sequenced)"))


# ===========================================================================
# Top-level build
# ===========================================================================
def build_first_aid_box(
    config: FirstAidBoxConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or FirstAidBoxConfig()
    r = resolve_config(cfg)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-first-aid-box-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)

    palette = PALETTES[r.palette_style]
    mats = {key: model.material(f"first_aid_{key}_{r.palette_style}", rgba=rgba)
            for key, rgba in palette.items()}

    clamshell = r.lid_module == "clamshell_dual"
    latch_xs = _latch_x_positions(r.latch_count, r.W)
    overlaps: list[tuple] = []

    base, base_seat = _build_base(model, r, mats)

    # Slot C alt: fixed side grips (parent.visual on base, no joint).
    if r.handle_module == "fixed_side_grips":
        _build_side_grips(base, r, mats)

    # Slot A: lid (+ clamshell front flap).
    lid, lid_seat = _build_lid(model, base, r, mats, base_seat=base_seat,
                               latch_xs=latch_xs, overlaps=overlaps)
    if clamshell:
        _build_front_flap(model, base, r, mats, overlaps=overlaps)

    # Slot B: interior.
    if r.interior_module == "cantilever_tiers":
        _build_cantilever(model, base, r, mats, overlaps=overlaps)
    elif r.interior_module == "stacked_trays":
        _build_lift_trays(model, base, r, mats, overlaps=overlaps, n=r.tray_count)
    else:
        _build_lift_trays(model, base, r, mats, overlaps=overlaps, n=1)

    # Slot C: folding handle (on lid).
    if r.handle_module == "folding_top_handle":
        _build_folding_handle(model, lid, r, mats, overlaps=overlaps)

    # Front draw-latches.
    _build_latches(model, base, r, mats, clamshell=clamshell, overlaps=overlaps)

    model.meta["slot_choices"] = _slot_choices_for_resolved(r)
    model.meta["_fa_overlaps"] = overlaps
    return model


def build_seeded_first_aid_box(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_first_aid_box(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _axis_is(joint, ax: tuple[float, float, float]) -> bool:
    return all(abs(joint.axis[k] - ax[k]) < 1e-6 for k in range(3))


def run_first_aid_box_tests(object_model: ArticulatedObject, config: FirstAidBoxConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}

    ctx.check("base part present", "base" in part_names)
    ctx.check("lid part present", "lid" in part_names)

    # Declare element-scoped / sequenced overlaps recorded during build.
    for spec in object_model.meta.get("_fa_overlaps", []):
        if len(spec) == 5:
            pa, pb, ea, eb, reason = spec
            if pa in part_names and pb in part_names:
                ctx.allow_overlap(object_model.get_part(pa), object_model.get_part(pb),
                                  elem_a=ea, elem_b=eb, reason=reason)
        else:
            pa, pb, reason = spec
            if pa in part_names and pb in part_names:
                ctx.allow_overlap(object_model.get_part(pa), object_model.get_part(pb),
                                  reason=reason)

    # Grounding: lowest geometry sits on the floor (base bottom on z=0).
    for i in range(r.latch_count):
        latch_name = f"latch_{i}"
        if latch_name in part_names:
            ctx.allow_isolated_part(
                object_model.get_part(latch_name),
                reason="latch flips open clear of the case and loses contact",
            )
    zmins = []
    for p in object_model.parts:
        ab = ctx.part_world_aabb(p)
        if ab is not None:
            zmins.append(ab[0][2])
    if zmins:
        ctx.check("case rests on the floor", abs(min(zmins)) <= 0.010,
                  details=f"zmin={min(zmins):.4f}")

    base = object_model.get_part("base")
    lid = object_model.get_part("lid")
    lid_joint = object_model.get_articulation("base_to_lid")

    # Lid: REVOLUTE about -X, hinged at the rear, opens upward.
    ctx.check("lid is revolute about -X",
              lid_joint.articulation_type == ArticulationType.REVOLUTE
              and _axis_is(lid_joint, (-1.0, 0.0, 0.0)), details=str(lid_joint.axis))
    ctx.check("lid hinge at rear edge", lid_joint.origin.xyz[1] > r.D * 0.40,
              details=f"hinge_y={lid_joint.origin.xyz[1]}")
    closed_lid = ctx.part_world_aabb(lid)
    with ctx.pose({lid_joint: 1.45}):
        open_lid = ctx.part_world_aabb(lid)
    if r.lid_module == "clamshell_dual":
        # Deep half-shell lid tips rearward about the rear hinge (front edge +y).
        ctx.check("clamshell lid opens rearward from rear hinge",
                  closed_lid is not None and open_lid is not None
                  and open_lid[0][1] > closed_lid[0][1] + 0.05,
                  details=f"closed={closed_lid}, open={open_lid}")
    else:
        ctx.check("lid opens upward from rear hinge",
                  closed_lid is not None and open_lid is not None
                  and open_lid[1][2] > closed_lid[1][2] + 0.06,
                  details=f"closed={closed_lid}, open={open_lid}")

    # Clamshell front flap: REVOLUTE +X, opens forward/down.
    if r.lid_module == "clamshell_dual":
        flap = object_model.get_part("front_flap")
        flap_joint = object_model.get_articulation("base_to_front_flap")
        ctx.check("front flap revolute about +X",
                  flap_joint.articulation_type == ArticulationType.REVOLUTE
                  and _axis_is(flap_joint, (1.0, 0.0, 0.0)), details=str(flap_joint.axis))
        closed_flap = ctx.part_element_world_aabb(flap, elem="flap_panel")
        with ctx.pose({flap_joint: 1.20}):
            open_flap = ctx.part_element_world_aabb(flap, elem="flap_panel")
        ctx.check("front flap opens forward (drawbridge)",
                  closed_flap is not None and open_flap is not None
                  and open_flap[0][1] < closed_flap[0][1] - 0.03,
                  details=f"closed={closed_flap}, open={open_flap}")

    # Interior trays.
    if r.interior_module == "cantilever_tiers":
        for i in range(2):
            arm_joint = object_model.get_articulation(f"base_to_tray_arm_{i}")
            ctx.check(f"tray_arm_{i} revolute about +Y",
                      arm_joint.articulation_type == ArticulationType.REVOLUTE
                      and _axis_is(arm_joint, (0.0, 1.0, 0.0)), details=str(arm_joint.axis))
            fix_joint = object_model.get_articulation(f"tray_arm_{i}_to_tray_{i}")
            ctx.check(f"tray_{i} fixed to arm",
                      fix_joint.articulation_type == ArticulationType.FIXED)
        # Opening an arm fans its tray up past the rim.
        tray0 = object_model.get_part("tray_0")
        arm_joint0 = object_model.get_articulation("base_to_tray_arm_0")
        rest0 = ctx.part_world_aabb(tray0)
        with ctx.pose({arm_joint0: arm_joint0.motion_limits.upper, lid_joint: 1.45}):
            open0 = ctx.part_world_aabb(tray0)
        ctx.check("cantilever tray fans up past the rim",
                  rest0 is not None and open0 is not None
                  and open0[1][2] > r.base_h + 0.010,
                  details=f"rest={rest0}, open={open0}")
    else:
        n = r.tray_count if r.interior_module == "stacked_trays" else 1
        ctx.check("tray count matches",
                  len([nm for nm in part_names if nm.startswith("tray_")]) == n,
                  details=f"expected {n}")
        for i in range(n):
            tj = object_model.get_articulation(f"base_to_tray_{i}")
            ctx.check(f"tray_{i} prismatic +z",
                      tj.articulation_type == ArticulationType.PRISMATIC
                      and _axis_is(tj, (0.0, 0.0, 1.0)), details=str(tj.axis))
        # Top tray lifts clear of the rim (with the lid open).
        top_tray = object_model.get_part(f"tray_{n - 1}")
        tj = object_model.get_articulation(f"base_to_tray_{n - 1}")
        rest = ctx.part_world_aabb(top_tray)
        with ctx.pose({lid_joint: 1.45, tj: tj.motion_limits.upper}):
            lifted = ctx.part_world_aabb(top_tray)
        ctx.check("lift tray clears the case rim",
                  rest is not None and lifted is not None
                  and lifted[0][2] > r.base_h + 0.004,
                  details=f"rest={rest}, lifted={lifted}, rim={r.base_h}")

    # Latches: count + revolute + flip-out motion.
    latch_parts = [nm for nm in part_names if nm.startswith("latch_")]
    ctx.check("latch count matches", len(latch_parts) == r.latch_count,
              details=f"expected {r.latch_count}, got {len(latch_parts)}")
    latch0 = object_model.get_part("latch_0")
    latch_joint0 = object_model.get_articulation("base_to_latch_0")
    ctx.check("latch revolute about +X",
              latch_joint0.articulation_type == ArticulationType.REVOLUTE
              and _axis_is(latch_joint0, (1.0, 0.0, 0.0)), details=str(latch_joint0.axis))
    closed_latch = ctx.part_world_aabb(latch0)
    with ctx.pose({latch_joint0: 0.95}):
        released_latch = ctx.part_world_aabb(latch0)
    ctx.check("latch clasp flips outward",
              closed_latch is not None and released_latch is not None
              and released_latch[0][1] < closed_latch[0][1] - 0.008,
              details=f"closed={closed_latch}, released={released_latch}")

    # Handle: folding loop lifts, or fixed side grips present.
    if r.handle_module == "folding_top_handle":
        handle = object_model.get_part("handle")
        hj = object_model.get_articulation("lid_to_handle")
        ctx.check("folding handle revolute about +X",
                  hj.articulation_type == ArticulationType.REVOLUTE
                  and _axis_is(hj, (1.0, 0.0, 0.0)), details=str(hj.axis))
        upright = ctx.part_element_world_aabb(handle, elem="handle_loop")
        with ctx.pose({hj: 1.30}):
            folded = ctx.part_element_world_aabb(handle, elem="handle_loop")
        ctx.check("folding handle swings down",
                  upright is not None and folded is not None
                  and folded[1][2] < upright[1][2] - 0.02,
                  details=f"upright={upright}, folded={folded}")
    else:
        ctx.check("fixed side grips present",
                  all(ctx.part_element_world_aabb(base, elem=f"end_handle_bar_{s}") is not None
                      for s in ("left", "right")))

    # Medical cross decal present (parent.visual, host-derived).
    cross_host = "front_flap" if r.lid_module == "clamshell_dual" else "base"
    ctx.check("medical cross decal present",
              ctx.part_element_world_aabb(object_model.get_part(cross_host),
                                          elem="cross_vertical") is not None)

    # Rule 5: full-travel sampled-pose overlap sweep + origin honesty.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = [
    "FirstAidBoxConfig",
    "ResolvedFirstAidBoxConfig",
    "build_first_aid_box",
    "build_seeded_first_aid_box",
    "config_from_seed",
    "resolve_config",
    "run_first_aid_box_tests",
    "slot_choices_for_seed",
]
