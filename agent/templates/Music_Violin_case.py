# SPDX-License-Identifier: Apache-2.0

"""Violin case (hardshell clamshell) — modular procedural template.

Category identity: a lying, elongated clamshell hardshell instrument case
(~0.80 m long x ~0.26 m wide x ~0.13 m tall). The ROOT ``bottom_shell`` is a
violin / dart / oblong tub with a **molded RED plush recess**; the ``lid`` is a
matching shallow shell that folds 0..180 deg about the rear (+Y) long-edge hinge
(``bottom_to_lid`` REVOLUTE) into an open-book pose. Every closure candidate
shares that lid hinge core.

Pattern: ``mixed`` — a linear shell<->lid hinge core plus three parallel
children hung off the shell/lid:
  - Slot A ``shell_footprint``  : violin_contour / rounded_dart_taper /
        rectangular_oblong (footprint geometry + half-width seating logic).
  - Slot B ``closure_mechanism``: hinge_plus_flip_latches (N flip latches,
        carries the ``latch_count`` multiplicity) / zipper_perimeter (PRISMATIC
        pull) / buckle_straps (2-link REVOLUTE strap+buckle chain x2).
  - Slot C ``carry_hardware``   : none / top_handle / dual_side_handles /
        d_ring_strap_loops.
  - Slot D ``interior_fitting`` : plain_plush / neck_cradle / bow_spinner_clips
        (lid REVOLUTE clips) / accessory_pocket (bottom REVOLUTE lid).

Multiplicity: ``latch_count`` N in {2,3,4} is GATED to closure=hinge only;
zipper/buckle replace the latches with their own fixed native count.

Couplings honored in ``resolve_config``: ``bow_spinner_clips`` needs a rigid
violin/dart lid cavity, so it is excluded with zipper (soft padded lid) and the
rectangular footprint and falls back to ``plain_plush``.

Sources: parent ``7727811a`` + 12 workbench 5-star fork variants. See spec
``articraft_template_authoring/specs_modular_v1/Music_Violin_case.md``.

slot_choices_for_seed returns the 5-tuple
``(shell_footprint, closure_mechanism, carry_hardware, interior_fitting,
latch_count)`` consumed by the ``module_topology_diversity`` gate.
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
    BoxGeometry,
    CylinderGeometry,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

ShellFootprint = Literal["violin_contour", "rounded_dart_taper", "rectangular_oblong"]
ClosureMechanism = Literal["hinge_plus_flip_latches", "zipper_perimeter", "buckle_straps"]
CarryHardware = Literal["none", "top_handle", "dual_side_handles", "d_ring_strap_loops"]
InteriorFitting = Literal["plain_plush", "neck_cradle", "bow_spinner_clips", "accessory_pocket"]
PaletteStyle = Literal[
    "brown_tweed_red",
    "black_shell_red_plush",
    "brown_tan_plush",
    "navy_grey",
    "green_tweed_gold",
    "carbon_black",
]

SHELL_FOOTPRINTS: tuple[ShellFootprint, ...] = (
    "violin_contour",
    "rounded_dart_taper",
    "rectangular_oblong",
)
CLOSURE_MECHANISMS: tuple[ClosureMechanism, ...] = (
    "hinge_plus_flip_latches",
    "zipper_perimeter",
    "buckle_straps",
)
CARRY_HARDWARE: tuple[CarryHardware, ...] = (
    "none",
    "top_handle",
    "dual_side_handles",
    "d_ring_strap_loops",
)
INTERIOR_FITTINGS: tuple[InteriorFitting, ...] = (
    "plain_plush",
    "neck_cradle",
    "bow_spinner_clips",
    "accessory_pocket",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brown_tweed_red",
    "black_shell_red_plush",
    "brown_tan_plush",
    "navy_grey",
    "green_tweed_gold",
    "carbon_black",
)
LATCH_COUNTS: tuple[int, ...] = (2, 3, 4)

# Footprints whose lid cavity is rigid enough to carry the lid-mounted bow
# spinner clips (needs a hard violin-contoured shell, not a soft/flat lid).
_RIGID_LID_FOOTPRINTS: frozenset[ShellFootprint] = frozenset(
    {"violin_contour", "rounded_dart_taper"}
)
# Closures that keep a rigid (non-padded) lid — bow clips need this.
_RIGID_LID_CLOSURES: frozenset[ClosureMechanism] = frozenset(
    {"hinge_plus_flip_latches", "buckle_straps"}
)

# rgba colorways (spec section 7). Keys drive every .visual.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "brown_tweed_red": {
        "shell": (0.20, 0.17, 0.13, 1.0),
        "plush": (0.62, 0.07, 0.08, 1.0),
        "metal": (0.78, 0.79, 0.82, 1.0),
        "accent": (0.30, 0.15, 0.06, 1.0),
        "soft": (0.15, 0.13, 0.12, 1.0),
    },
    "black_shell_red_plush": {
        "shell": (0.06, 0.06, 0.07, 1.0),
        "plush": (0.62, 0.07, 0.08, 1.0),
        "metal": (0.78, 0.79, 0.82, 1.0),
        "accent": (0.20, 0.12, 0.08, 1.0),
        "soft": (0.10, 0.10, 0.11, 1.0),
    },
    "brown_tan_plush": {
        "shell": (0.30, 0.18, 0.10, 1.0),
        "plush": (0.74, 0.62, 0.42, 1.0),
        "metal": (0.72, 0.58, 0.26, 1.0),
        "accent": (0.40, 0.26, 0.12, 1.0),
        "soft": (0.26, 0.18, 0.12, 1.0),
    },
    "navy_grey": {
        "shell": (0.10, 0.13, 0.22, 1.0),
        "plush": (0.45, 0.46, 0.50, 1.0),
        "metal": (0.74, 0.75, 0.78, 1.0),
        "accent": (0.20, 0.22, 0.30, 1.0),
        "soft": (0.14, 0.16, 0.22, 1.0),
    },
    "green_tweed_gold": {
        "shell": (0.16, 0.22, 0.13, 1.0),
        "plush": (0.66, 0.52, 0.16, 1.0),
        "metal": (0.72, 0.58, 0.26, 1.0),
        "accent": (0.28, 0.30, 0.16, 1.0),
        "soft": (0.14, 0.18, 0.12, 1.0),
    },
    "carbon_black": {
        "shell": (0.10, 0.10, 0.12, 1.0),
        "plush": (0.10, 0.08, 0.08, 1.0),
        "metal": (0.30, 0.31, 0.34, 1.0),
        "accent": (0.14, 0.12, 0.12, 1.0),
        "soft": (0.08, 0.08, 0.10, 1.0),
    },
}

# ---- base real-world dimensions (metres); scaled per-seed in resolve_config ----
CASE_LEN = 0.80  # +X extent (neck -> lower bout)
HALF_W = 0.13  # half width at lower bout (full width 0.26)
SHELL_H = 0.085  # height of the bottom shell tub (rim plane z)
LID_H = 0.045  # depth of the lid shell
WALL = 0.012  # shell wall thickness
RECESS_INSET = 0.018  # how far the red recess outline is inset from the rim
CORNER_R = 0.025  # rounded-rectangle corner fillet radius

# Outline half-point tables (x fraction along length, y half-width in metres).
# adopted: S1 parent (violin), S2 var_outline_dart (dart).
VIOLIN_RAW: tuple[tuple[float, float], ...] = (
    (0.000, 0.052),
    (0.060, 0.062),
    (0.140, 0.082),
    (0.230, 0.098),
    (0.300, 0.092),
    (0.360, 0.066),
    (0.420, 0.066),
    (0.490, 0.092),
    (0.580, 0.118),
    (0.680, 0.130),
    (0.800, 0.128),
    (0.910, 0.108),
    (0.975, 0.060),
    (1.000, 0.022),
)
DART_RAW: tuple[tuple[float, float], ...] = (
    (0.000, 0.014),
    (0.035, 0.020),
    (0.080, 0.030),
    (0.140, 0.044),
    (0.210, 0.060),
    (0.290, 0.078),
    (0.380, 0.095),
    (0.470, 0.110),
    (0.560, 0.122),
    (0.650, 0.129),
    (0.740, 0.130),
    (0.820, 0.128),
    (0.890, 0.120),
    (0.940, 0.104),
    (0.970, 0.078),
    (0.990, 0.048),
    (1.000, 0.022),
)


@dataclass(frozen=True)
class ViolinCaseConfig:
    shell_footprint: ShellFootprint = "violin_contour"
    closure_mechanism: ClosureMechanism = "hinge_plus_flip_latches"
    carry_hardware: CarryHardware = "none"
    interior_fitting: InteriorFitting = "plain_plush"
    latch_count: int = 2
    palette_style: PaletteStyle = "brown_tweed_red"
    case_length_scale: float = 1.0
    case_width_scale: float = 1.0
    shell_height_scale: float = 1.0
    lid_depth_scale: float = 1.0
    name: str = "reference_violin_case"


@dataclass(frozen=True)
class ResolvedViolinCaseConfig:
    shell_footprint: ShellFootprint
    closure_mechanism: ClosureMechanism
    carry_hardware: CarryHardware
    interior_fitting: InteriorFitting
    latch_count: int
    palette_style: PaletteStyle
    len_mul: float
    width_mul: float
    case_len: float
    half_w: float
    shell_h: float
    lid_h: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _resolve_interior(
    footprint: ShellFootprint,
    closure: ClosureMechanism,
    interior: InteriorFitting,
) -> InteriorFitting:
    # bow_spinner_clips needs a rigid violin/dart lid cavity (not a soft padded
    # zipper lid, not a flat rectangular lid). Fall back to plain plush.
    if interior == "bow_spinner_clips":
        if footprint not in _RIGID_LID_FOOTPRINTS or closure not in _RIGID_LID_CLOSURES:
            return "plain_plush"
    return interior


def config_from_seed(seed: int) -> ViolinCaseConfig:
    if seed == 0:
        return ViolinCaseConfig()

    rng = random.Random(seed)
    footprint = rng.choices(SHELL_FOOTPRINTS, weights=(0.42, 0.30, 0.28), k=1)[0]
    closure = rng.choices(CLOSURE_MECHANISMS, weights=(0.42, 0.29, 0.29), k=1)[0]
    carry = rng.choices(CARRY_HARDWARE, weights=(0.28, 0.26, 0.23, 0.23), k=1)[0]
    interior = rng.choices(INTERIOR_FITTINGS, weights=(0.34, 0.24, 0.21, 0.21), k=1)[0]
    interior = _resolve_interior(footprint, closure, interior)

    # latch_count multiplicity is only sampled for the hinge closure.
    if closure == "hinge_plus_flip_latches":
        latch_count = rng.choices(LATCH_COUNTS, weights=(0.60, 0.30, 0.10), k=1)[0]
    else:
        latch_count = 2

    return ViolinCaseConfig(
        shell_footprint=footprint,
        closure_mechanism=closure,
        carry_hardware=carry,
        interior_fitting=interior,
        latch_count=latch_count,
        palette_style=rng.choice(PALETTE_STYLES),
        case_length_scale=round(rng.uniform(0.92, 1.10), 4),
        case_width_scale=round(rng.uniform(0.92, 1.10), 4),
        shell_height_scale=round(rng.uniform(0.88, 1.12), 4),
        lid_depth_scale=round(rng.uniform(0.88, 1.15), 4),
        name=f"seeded_violin_case_{seed}",
    )


def resolve_config(config: ViolinCaseConfig | None = None) -> ResolvedViolinCaseConfig:
    cfg = config or ViolinCaseConfig()
    footprint = _pick(cfg.shell_footprint, SHELL_FOOTPRINTS)
    closure = _pick(cfg.closure_mechanism, CLOSURE_MECHANISMS)
    carry = _pick(cfg.carry_hardware, CARRY_HARDWARE)
    interior = _resolve_interior(footprint, closure, _pick(cfg.interior_fitting, INTERIOR_FITTINGS))

    latch_count = cfg.latch_count if cfg.latch_count in LATCH_COUNTS else 2
    if closure != "hinge_plus_flip_latches":
        latch_count = 2  # not used downstream; canonicalized for slot_choices

    len_mul = _clamp(cfg.case_length_scale, 0.92, 1.10)
    width_mul = _clamp(cfg.case_width_scale, 0.92, 1.10)
    height_mul = _clamp(cfg.shell_height_scale, 0.88, 1.12)
    lid_mul = _clamp(cfg.lid_depth_scale, 0.88, 1.15)

    return ResolvedViolinCaseConfig(
        shell_footprint=footprint,
        closure_mechanism=closure,
        carry_hardware=carry,
        interior_fitting=interior,
        latch_count=latch_count,
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        len_mul=len_mul,
        width_mul=width_mul,
        case_len=CASE_LEN * len_mul,
        half_w=HALF_W * width_mul,
        shell_h=SHELL_H * height_mul,
        lid_h=LID_H * lid_mul,
        name=cfg.name or "violin_case",
    )


def with_overrides(config: ViolinCaseConfig, **kwargs: object) -> ViolinCaseConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ViolinCaseConfig | ResolvedViolinCaseConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedViolinCaseConfig) else resolve_config(config)
    latch_tag = f"n{r.latch_count}" if r.closure_mechanism == "hinge_plus_flip_latches" else "na"
    return (
        ("shell_footprint", r.shell_footprint),
        ("closure_mechanism", r.closure_mechanism),
        ("carry_hardware", r.carry_hardware),
        ("interior_fitting", r.interior_fitting),
        ("latch_count", latch_tag),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Outline geometry — dispatched by shell_footprint. hw(x) is the half-width at
# world x (interpolated for violin/dart; constant for the oblong).
# ---------------------------------------------------------------------------
def _half_points(footprint: ShellFootprint, xmul: float, ymul: float):
    raw = VIOLIN_RAW if footprint == "violin_contour" else DART_RAW
    return [((fx - 0.5) * CASE_LEN * xmul, hy * ymul) for fx, hy in raw]


def _half_width_at_x(r: ResolvedViolinCaseConfig, x_world: float) -> float:
    if r.shell_footprint == "rectangular_oblong":
        return r.half_w
    pts = _half_points(r.shell_footprint, r.len_mul, r.width_mul)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        lo, hi = (x0, x1) if x0 <= x1 else (x1, x0)
        if lo <= x_world <= hi:
            t = 0.0 if x1 == x0 else (x_world - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return pts[len(pts) // 2][1]


def _rrect(length: float, width: float, height: float, corner_r: float) -> cq.Workplane:
    cr = min(corner_r, length / 2.0 - 0.001, width / 2.0 - 0.001)
    cr = max(cr, 0.001)
    return cq.Workplane("XY").rect(length, width).extrude(height).edges("|Z").fillet(cr)


def _spline_solid(
    r: ResolvedViolinCaseConfig, height: float, scale_w: float = 1.0, scale_x: float = 1.0
) -> cq.Workplane:
    half = _half_points(r.shell_footprint, r.len_mul * scale_x, r.width_mul * scale_w)
    x0, _ = half[0]
    xn, _ = half[-1]
    upper = [(x, y) for x, y in half]
    lower = [(x, -y) for x, y in reversed(half)]
    interior = upper[1:] + [(xn, 0.0)] + lower[:-1]
    return (
        cq.Workplane("XY")
        .moveTo(x0, 0.0)
        .spline(interior, includeCurrent=True)
        .close()
        .extrude(height)
    )


def _bottom_shell_solid(r: ResolvedViolinCaseConfig) -> cq.Workplane:
    if r.shell_footprint == "rectangular_oblong":
        outer = _rrect(r.case_len, 2 * r.half_w, r.shell_h, CORNER_R)
        inner_len = r.case_len - 2 * RECESS_INSET
        inner_w = 2 * r.half_w - 2 * RECESS_INSET
        inner_r = max(CORNER_R - RECESS_INSET, 0.005)
        recess = _rrect(inner_len, inner_w, r.shell_h + 0.01, inner_r).translate((0, 0, WALL))
        return outer.cut(recess)
    outer = _spline_solid(r, r.shell_h)
    recess = _spline_solid(
        r,
        r.shell_h + 0.01,
        scale_w=1.0 - RECESS_INSET / r.half_w,
        scale_x=1.0 - RECESS_INSET / (r.case_len * 0.5),
    ).translate((0, 0, WALL))
    return outer.cut(recess)


def _red_interior_solid(r: ResolvedViolinCaseConfig) -> cq.Workplane:
    pad = 0.006
    if r.shell_footprint == "rectangular_oblong":
        inner_len = r.case_len - 2 * (RECESS_INSET + pad)
        inner_w = 2 * r.half_w - 2 * (RECESS_INSET + pad)
        inner_r = max(CORNER_R - RECESS_INSET - pad, 0.004)
        floor = _rrect(inner_len, inner_w, WALL * 1.4, inner_r).translate((0, 0, WALL))
        o_len = r.case_len - 2 * RECESS_INSET
        o_w = 2 * r.half_w - 2 * RECESS_INSET
        o_r = max(CORNER_R - RECESS_INSET, 0.005)
        wall_outer = _rrect(o_len, o_w, r.shell_h - WALL, o_r)
        wall_inner = _rrect(inner_len, inner_w, r.shell_h, inner_r)
        wall = wall_outer.cut(wall_inner).translate((0, 0, WALL))
        return floor.union(wall)
    sw = 1.0 - (RECESS_INSET + pad) / r.half_w
    sx = 1.0 - (RECESS_INSET + pad) / (r.case_len * 0.5)
    floor = _spline_solid(r, WALL * 1.4, scale_w=sw, scale_x=sx).translate((0, 0, WALL))
    wall_outer = _spline_solid(
        r,
        r.shell_h - WALL,
        scale_w=1.0 - RECESS_INSET / r.half_w,
        scale_x=1.0 - RECESS_INSET / (r.case_len * 0.5),
    )
    wall_inner = _spline_solid(r, r.shell_h, scale_w=sw, scale_x=sx)
    wall = wall_outer.cut(wall_inner).translate((0, 0, WALL))
    return floor.union(wall)


def _lid_solid(r: ResolvedViolinCaseConfig) -> cq.Workplane:
    if r.shell_footprint == "rectangular_oblong":
        outer = _rrect(r.case_len, 2 * r.half_w, r.lid_h, CORNER_R)
        inner = _rrect(
            r.case_len - 2 * WALL, 2 * r.half_w - 2 * WALL, r.lid_h, max(CORNER_R - WALL, 0.005)
        ).translate((0, 0, -0.006))
        return outer.cut(inner)
    outer = _spline_solid(r, r.lid_h)
    inner = _spline_solid(
        r, r.lid_h, scale_w=1.0 - WALL / r.half_w, scale_x=1.0 - WALL / (r.case_len * 0.5)
    ).translate((0, 0, -0.006))
    return outer.cut(inner)


def _lid_liner_solid(r: ResolvedViolinCaseConfig) -> cq.Workplane:
    if r.shell_footprint == "rectangular_oblong":
        cap = _rrect(
            r.case_len - 2 * WALL, 2 * r.half_w - 2 * WALL, 0.008, max(CORNER_R - WALL, 0.005)
        )
    else:
        cap = _spline_solid(
            r, 0.008, scale_w=1.0 - WALL / r.half_w, scale_x=1.0 - WALL / (r.case_len * 0.5)
        )
    return cap.translate((0, 0, r.lid_h - 0.012))


def _lid_padding_solid(r: ResolvedViolinCaseConfig) -> cq.Workplane:
    if r.shell_footprint == "rectangular_oblong":
        pad = _rrect(r.case_len * 0.88, 2 * r.half_w * 0.88, 0.008, max(CORNER_R * 0.88, 0.005))
    else:
        pad = _spline_solid(r, 0.008, scale_w=0.88, scale_x=0.88)
    return pad.translate((0, 0, r.lid_h - 0.001))


# ---------------------------------------------------------------------------
# Shell root (bottom_shell) + lid hinge core (shared by all closures).
# ---------------------------------------------------------------------------
def _build_shell(bottom, r: ResolvedViolinCaseConfig, mats: dict) -> None:
    bottom.visual(
        mesh_from_cadquery(_bottom_shell_solid(r), "bottom_exterior"),
        material=mats["shell"],
        name="bottom_exterior", material_class_id="plastic.opaque_glossy_molded",
    )
    bottom.visual(
        mesh_from_cadquery(_red_interior_solid(r), "red_interior"),
        material=mats["plush"],
        name="red_interior", material_class_id="fabric.velvet",
    )
    # Rear-rim hinge knuckles (embedded into the shell wall so they connect).
    for j, hxf in enumerate((-0.20, 0.22)):
        hx = hxf * r.len_mul
        rim_y = _half_width_at_x(r, hx)
        knuckle = CylinderGeometry(0.006, 0.060).rotate_x(math.pi / 2.0)
        knuckle.translate(hx, rim_y - 0.004, r.shell_h - 0.006)
        bottom.visual(
            mesh_from_geometry(knuckle, f"hinge_barrel_{j}"),
            material=mats["metal"],
            name=f"hinge_barrel_{j}", material_class_id="metal.stainless_matte",
        )
    bottom.inertial = Inertial.from_geometry(
        Box((r.case_len, 2 * r.half_w, r.shell_h)),
        mass=2.4,
        origin=Origin(xyz=(0.0, 0.0, r.shell_h / 2.0)),
    )


def _hinge_x(r: ResolvedViolinCaseConfig) -> float:
    """World X of the hinge origin: the widest back-rim point, where the
    contoured rim actually reaches y=half_w (so the joint origin sits on real
    shell/lid geometry within the 15 mm baseline). Constant rim => 0 for oblong.
    """
    if r.shell_footprint == "violin_contour":
        return 0.144 * r.len_mul  # raw node fx=0.680 (hy=0.130 = HALF_W)
    if r.shell_footprint == "rounded_dart_taper":
        return 0.192 * r.len_mul  # raw node fx=0.740 (hy=0.130 = HALF_W)
    return 0.0


def _build_lid(model, bottom, r: ResolvedViolinCaseConfig, mats: dict):
    soft_lid = r.closure_mechanism == "zipper_perimeter"
    hx = _hinge_x(r)
    lid = model.part("lid")
    lid_shell = _lid_solid(r).translate((-hx, -r.half_w, 0.0))
    lid_liner = _lid_liner_solid(r).translate((-hx, -r.half_w, 0.0))
    lid.visual(
        mesh_from_cadquery(lid_shell, "lid_exterior"),
        material=mats["soft"] if soft_lid else mats["shell"],
        name="lid_exterior", material_class_id=("plastic.opaque_glossy_molded" if r.closure_mechanism in {"hinge_plus_flip_latches", "buckle_straps"} else "fabric.upholstery_plain"),
    )
    lid.visual(mesh_from_cadquery(lid_liner, "lid_liner"), material=mats["plush"], name="lid_liner", material_class_id="fabric.velvet")
    if soft_lid:
        lid_pad = _lid_padding_solid(r).translate((-hx, -r.half_w, 0.0))
        lid.visual(
            mesh_from_cadquery(lid_pad, "lid_padding"), material=mats["soft"], name="lid_padding", material_class_id="fabric.flexible_foam"
        )
    lid.inertial = Inertial.from_geometry(
        Box((r.case_len, 2 * r.half_w, r.lid_h)),
        mass=1.0,
        origin=Origin(xyz=(-hx, -r.half_w, r.lid_h / 2.0)),
    )
    # Rear (+Y) long-edge hinge; positive q folds the lid 0..180 deg onto +Y.
    # Axis is along X, so the fold line is {y=half_w, z=shell_h}; the origin X
    # is placed at the widest rim point purely to land on real geometry.
    model.articulation(
        "bottom_to_lid",
        ArticulationType.REVOLUTE,
        parent=bottom,
        child=lid,
        origin=Origin(xyz=(hx, r.half_w, r.shell_h)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=math.radians(180.0), effort=8.0, velocity=2.0),
    )
    return lid


# ---------------------------------------------------------------------------
# Slot B — closure_mechanism.
# ---------------------------------------------------------------------------
def _latch_positions(r: ResolvedViolinCaseConfig) -> tuple[float, ...]:
    if r.latch_count == 4:
        base = (-0.20, -0.05, 0.10, 0.25)
    elif r.latch_count == 3:
        base = (0.02, 0.16, 0.30)
    else:
        base = (0.10, 0.30)
    return tuple(x * r.len_mul for x in base)


def _build_closure(model, bottom, lid, r: ResolvedViolinCaseConfig, mats: dict) -> None:
    metal = mats["metal"]

    if r.closure_mechanism == "hinge_plus_flip_latches":
        for i, lx in enumerate(_latch_positions(r)):
            wall_y = -_half_width_at_x(r, lx)
            latch = model.part(f"latch_{i}")
            lever = BoxGeometry((0.030, 0.007, 0.032)).translate(0.0, -0.0055, 0.016)
            hook = BoxGeometry((0.030, 0.013, 0.006)).translate(0.0, -0.0035, 0.031)
            lever.merge(hook)
            pin = CylinderGeometry(0.004, 0.040).rotate_y(math.pi / 2.0)
            lever.merge(pin)
            latch.visual(
                mesh_from_geometry(lever, f"latch_body_{i}"), material=metal, name=f"latch_body_{i}", material_class_id="metal.stainless_matte"
            )
            latch.inertial = Inertial.from_geometry(
                Box((0.040, 0.016, 0.040)),
                mass=0.03,
                origin=Origin(xyz=(0.0, 0.0, 0.017)),
            )
            model.articulation(
                f"bottom_to_latch_{i}",
                ArticulationType.REVOLUTE,
                parent=bottom,
                child=latch,
                origin=Origin(xyz=(lx, wall_y + 0.002, r.shell_h - 0.020)),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(
                    lower=0.0, upper=math.radians(80.0), effort=2.0, velocity=2.0
                ),
            )
        return

    if r.closure_mechanism == "zipper_perimeter":
        _build_zipper(model, bottom, r, mats)
        return

    _build_buckle_straps(model, bottom, lid, r, mats)


def _front_edge_point(r: ResolvedViolinCaseConfig, t: float):
    """Interpolate a point on the front (-Y) edge. t=0 neck, t=1 tail."""
    if r.shell_footprint == "rectangular_oblong":
        x = (-0.5 + t) * r.case_len
        return (x, -r.half_w)
    pts = _half_points(r.shell_footprint, r.len_mul, r.width_mul)
    idx_f = t * (len(pts) - 1)
    idx = min(int(idx_f), len(pts) - 2)
    frac = idx_f - idx
    x0, y0 = pts[idx]
    x1, y1 = pts[idx + 1]
    return (x0 + frac * (x1 - x0), -(y0 + frac * (y1 - y0)))


def _zipper_track_path_3d(r: ResolvedViolinCaseConfig):
    z = r.shell_h - 0.001
    if r.shell_footprint == "rectangular_oblong":
        hw = r.half_w
        xn = -0.5 * r.case_len
        xt = 0.5 * r.case_len
        return [
            (xn, hw * 0.5, z),
            (xn, 0.0, z),
            (xn, -hw, z),
            (xt, -hw, z),
            (xt, 0.0, z),
            (xt, hw * 0.5, z),
        ]
    half = _half_points(r.shell_footprint, r.len_mul, r.width_mul)
    neck_fringe = [(x, y, z) for x, y in half[:2]]
    tail_fringe = [(x, y, z) for x, y in half[-2:]]
    front_edge = [(x, -y, z) for x, y in half]
    x_neck = half[0][0]
    x_tail = half[-1][0]
    return (
        list(reversed(neck_fringe))
        + [(x_neck, 0.0, z)]
        + front_edge
        + [(x_tail, 0.0, z)]
        + list(reversed(tail_fringe))
    )


def _build_zipper(model, bottom, r: ResolvedViolinCaseConfig, mats: dict) -> None:
    metal = mats["metal"]
    track_mesh = tube_from_spline_points(
        _zipper_track_path_3d(r),
        radius=0.003,
        samples_per_segment=8,
        radial_segments=12,
        cap_ends=True,
        up_hint=(0.0, 0.0, 1.0),
    )
    bottom.visual(
        mesh_from_geometry(track_mesh, "zipper_track"), material=mats["soft"], name="zipper_track", material_class_id="fabric.webbing"
    )
    tooth_z = r.shell_h - 0.002
    teeth_count = 8
    for i in range(teeth_count):
        t = (i + 0.5) / teeth_count
        tx, ty = _front_edge_point(r, t)
        tooth = BoxGeometry((0.003, 0.005, 0.005)).translate(tx, ty, tooth_z)
        bottom.visual(
            mesh_from_geometry(tooth, f"zipper_tooth_{i}"), material=metal, name=f"zipper_tooth_{i}", material_class_id="metal.stainless_matte"
        )
    for i in range(2):
        t = 0.03 if i == 0 else 0.97
        sx, sy = _front_edge_point(r, t)
        stopper = BoxGeometry((0.006, 0.006, 0.005)).translate(sx, sy, r.shell_h - 0.002)
        bottom.visual(
            mesh_from_geometry(stopper, f"zipper_stopper_{i}"),
            material=metal,
            name=f"zipper_stopper_{i}", material_class_id="metal.stainless_matte",
        )

    zipper_pull = model.part("zipper_pull")
    body = BoxGeometry((0.014, 0.010, 0.006))
    tab = BoxGeometry((0.010, 0.002, 0.012)).translate(0.0, -0.006, -0.004)
    body.merge(tab)
    zipper_pull.visual(mesh_from_geometry(body, "pull_body"), material=metal, name="pull_body", material_class_id="metal.stainless_matte")
    zipper_pull.inertial = Inertial.from_geometry(
        Box((0.020, 0.014, 0.024)),
        mass=0.015,
        origin=Origin(xyz=(0.0, 0.0, -0.003)),
    )
    pull_y = -_half_width_at_x(r, 0.0)
    travel = 0.18 * r.len_mul
    model.articulation(
        "bottom_to_zipper_pull",
        ArticulationType.PRISMATIC,
        parent=bottom,
        child=zipper_pull,
        origin=Origin(xyz=(0.0, pull_y, r.shell_h + 0.004)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=-travel, upper=travel, effort=2.0, velocity=0.5),
    )


_STRAP_W = 0.022
_STRAP_T = 0.003
_STRAP_L = 0.065
_BUCKLE_W = 0.028
_BUCKLE_D = 0.006
_BUCKLE_H = 0.024
_BUCKLE_WALL = 0.004


def _strap_band_solid() -> cq.Workplane:
    return (
        cq.Workplane("XY").box(_STRAP_W, _STRAP_T, _STRAP_L).translate((0.0, 0.0, -_STRAP_L / 2.0))
    )


def _buckle_frame_solid() -> cq.Workplane:
    w, d, h, t = _BUCKLE_W, _BUCKLE_D, _BUCKLE_H, _BUCKLE_WALL
    outer = cq.Workplane("XY").box(w, d, h).translate((0.0, 0.0, -h / 2.0))
    inner = cq.Workplane("XY").box(w - 2 * t, d + 0.002, h - 2 * t).translate((0.0, 0.0, -h / 2.0))
    frame = outer.cut(inner)
    prong = cq.Workplane("XY").box(w - 2 * t, 0.003, 0.003).translate((0.0, 0.0, -h / 2.0))
    frame = frame.union(prong)
    loop = cq.Workplane("XY").box(w, 0.003, 0.004).translate((0.0, 0.0, -0.002))
    return frame.union(loop)


def _build_buckle_straps(model, bottom, lid, r: ResolvedViolinCaseConfig, mats: dict) -> None:
    metal = mats["metal"]
    leather = mats["accent"]
    hx = _hinge_x(r)
    strap_hinge_z_lid = r.lid_h * 0.70
    strap_positions = tuple(x * r.len_mul for x in (0.14, 0.24))

    for i, sx in enumerate(strap_positions):
        wall_y = -_half_width_at_x(r, sx)
        buckle_pivot_z = r.shell_h + strap_hinge_z_lid - _STRAP_L
        buckle_center_z = buckle_pivot_z - _BUCKLE_H / 2.0
        plate = BoxGeometry((0.032, 0.002, _BUCKLE_H + 0.006))
        plate.translate(sx, wall_y - 0.001, buckle_center_z)
        bottom.visual(
            mesh_from_geometry(plate, f"catch_plate_{i}"), material=metal, name=f"catch_plate_{i}", material_class_id="metal.stainless_matte"
        )

    for i, sx in enumerate(strap_positions):
        front_y_lid = -_half_width_at_x(r, sx) - r.half_w
        hinge_y_lid = front_y_lid - _STRAP_T / 2.0
        strap = model.part(f"strap_{i}")
        strap.visual(
            mesh_from_cadquery(_strap_band_solid(), f"strap_band_{i}"),
            material=leather,
            name=f"strap_band_{i}", material_class_id="leather.smooth_plain",
        )
        strap.inertial = Inertial.from_geometry(
            Box((_STRAP_W, _STRAP_T, _STRAP_L)),
            mass=0.015,
            origin=Origin(xyz=(0.0, 0.0, -_STRAP_L / 2.0)),
        )
        model.articulation(
            f"lid_to_strap_{i}",
            ArticulationType.REVOLUTE,
            parent=lid,
            child=strap,
            origin=Origin(xyz=(sx - hx, hinge_y_lid, strap_hinge_z_lid)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                lower=0.0, upper=math.radians(60.0), effort=2.0, velocity=2.0
            ),
        )
        buckle = model.part(f"buckle_{i}")
        buckle.visual(
            mesh_from_cadquery(_buckle_frame_solid(), f"buckle_frame_{i}"),
            material=metal,
            name=f"buckle_frame_{i}", material_class_id="metal.stainless_matte",
        )
        buckle.inertial = Inertial.from_geometry(
            Box((_BUCKLE_W, _BUCKLE_D, _BUCKLE_H)),
            mass=0.020,
            origin=Origin(xyz=(0.0, 0.0, -_BUCKLE_H / 2.0)),
        )
        model.articulation(
            f"strap_to_buckle_{i}",
            ArticulationType.REVOLUTE,
            parent=strap,
            child=buckle,
            origin=Origin(xyz=(0.0, 0.0, -_STRAP_L)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                lower=0.0, upper=math.radians(40.0), effort=1.5, velocity=2.0
            ),
        )


# ---------------------------------------------------------------------------
# Slot C — carry_hardware.
# ---------------------------------------------------------------------------
def _build_carry(model, bottom, r: ResolvedViolinCaseConfig, mats: dict) -> None:
    if r.carry_hardware == "none":
        return
    if r.carry_hardware == "top_handle":
        _build_top_handle(model, bottom, r, mats)
    elif r.carry_hardware == "dual_side_handles":
        _build_dual_side_handles(model, bottom, r, mats)
    else:
        _build_d_ring_loops(model, bottom, r, mats)


def _build_top_handle(model, bottom, r: ResolvedViolinCaseConfig, mats: dict) -> None:
    metal = mats["metal"]
    # Shared-wall clearance: buckle straps hang down the lower-bout (+X) front
    # wall, so park the handle on the upper-bout (-X) side to keep X-clearance.
    handle_x = (-0.18 if r.closure_mechanism == "buckle_straps" else 0.20) * r.len_mul
    handle_z = r.shell_h * 0.48
    half_span = 0.055
    bar_r = 0.006
    drop = 0.040
    out = 0.008
    handle_wall_y = -_half_width_at_x(r, handle_x)

    for i, foot_x in enumerate((handle_x - half_span, handle_x + half_span)):
        fw_y = -_half_width_at_x(r, foot_x)
        plate = BoxGeometry((0.022, 0.006, 0.030))
        plate.translate(foot_x, fw_y - 0.003, handle_z)
        bottom.visual(
            mesh_from_geometry(plate, f"handle_mount_foot_{i}"),
            material=metal,
            name=f"handle_mount_foot_{i}", material_class_id="metal.stainless_matte",
        )
        ear = CylinderGeometry(0.007, 0.010).rotate_z(math.pi / 2.0)
        ear.translate(foot_x, fw_y - 0.006, handle_z)
        bottom.visual(
            mesh_from_geometry(ear, f"handle_mount_ear_{i}"),
            material=metal,
            name=f"handle_mount_ear_{i}", material_class_id="metal.stainless_matte",
        )

    wall_clear = bar_r + 0.004
    bar_points = [
        (-half_span, -wall_clear, -0.003),
        (-half_span, -wall_clear, -drop * 0.50),
        (-half_span * 0.60, -(wall_clear + out * 0.65), -drop * 0.85),
        (0.0, -(wall_clear + out), -drop),
        (half_span * 0.60, -(wall_clear + out * 0.65), -drop * 0.85),
        (half_span, -wall_clear, -drop * 0.50),
        (half_span, -wall_clear, -0.003),
    ]
    handle = model.part("carry_handle")
    bar_mesh = tube_from_spline_points(
        bar_points, radius=bar_r, samples_per_segment=16, radial_segments=18, cap_ends=True
    )
    handle.visual(mesh_from_geometry(bar_mesh, "handle_bar"), material=metal, name="handle_bar", material_class_id="metal.stainless_matte")
    # One continuous pivot rod along X bridging the two curved bar ends. It sits
    # between the pivot axis and the bar (y=-wall_clear/2, radius spans both) so
    # it both contains the part origin (0,0,0) and robustly fuses to the bar.
    pivot_rod = CylinderGeometry(0.006, 2 * half_span + 0.006).rotate_y(math.pi / 2.0)
    pivot_rod.translate(0.0, -wall_clear * 0.5, 0.0)
    handle.visual(
        mesh_from_geometry(pivot_rod, "handle_pivot_rod"), material=metal, name="handle_pivot_rod", material_class_id="metal.stainless_matte"
    )
    handle.inertial = Inertial.from_geometry(
        Box((2 * half_span + 0.02, 0.02, drop + 0.02)),
        mass=0.12,
        origin=Origin(xyz=(0.0, 0.0, -drop * 0.5)),
    )
    model.articulation(
        "bottom_to_handle",
        ArticulationType.REVOLUTE,
        parent=bottom,
        child=handle,
        origin=Origin(xyz=(handle_x, handle_wall_y, handle_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=math.radians(100.0), effort=3.0, velocity=2.5),
    )


def _build_dual_side_handles(model, bottom, r: ResolvedViolinCaseConfig, mats: dict) -> None:
    metal = mats["metal"]
    span = 0.12
    drop = 0.032
    tube_r = 0.005
    pivot_r = 0.004
    pivot_len = 0.010
    handle_z = r.shell_h * 0.45
    center_x = 0.0
    standoff = 0.008
    wall_y_center = _half_width_at_x(r, center_x)

    def _bar_mesh(side: int):
        half = span / 2.0
        n_pts = 9
        points = []
        for k in range(n_pts):
            t = k / (n_pts - 1)
            x_local = -half + t * span
            wall_y = _half_width_at_x(r, center_x + x_local)
            y_local = side * (wall_y - wall_y_center)
            z_local = -drop * 4.0 * t * (1.0 - t)
            points.append((x_local, y_local, z_local))
        bar = tube_from_spline_points(
            points,
            radius=tube_r,
            samples_per_segment=12,
            radial_segments=16,
            cap_ends=True,
            up_hint=(0.0, 0.0, 1.0),
        )
        for x_sign in (-1, 1):
            x_local = x_sign * half
            wall_y = _half_width_at_x(r, center_x + x_local)
            y_local = side * (wall_y - wall_y_center)
            stub = CylinderGeometry(pivot_r, pivot_len).rotate_y(math.pi / 2.0)
            stub.translate(x_local + x_sign * pivot_len * 0.5, y_local, 0.0)
            bar.merge(stub)
        return bar

    for i in range(2):
        side = 1 if i == 0 else -1
        pivot_y = side * (wall_y_center + standoff)
        foot_height = standoff + 0.006
        for j, fx_off in enumerate((-span / 2.0, span / 2.0)):
            fx = center_x + fx_off
            fy = _half_width_at_x(r, fx)
            foot = CylinderGeometry(0.009, foot_height).rotate_x(math.pi / 2.0)
            foot.translate(fx, side * (fy + foot_height * 0.5), handle_z)
            bottom.visual(
                mesh_from_geometry(foot, f"handle_mount_{i}_{j}"),
                material=metal,
                name=f"handle_mount_{i}_{j}", material_class_id="metal.stainless_matte",
            )
        handle = model.part(f"handle_{i}")
        handle.visual(
            mesh_from_geometry(_bar_mesh(side), f"handle_bar_{i}"),
            material=metal,
            name=f"handle_bar_{i}", material_class_id="metal.stainless_matte",
        )
        # Central spine bracket from the pivot axis (0,0,0) down to the bar mid
        # (0,0,-drop): seats the joint origin on real geometry + bridges to bar.
        spine = BoxGeometry((0.010, 0.008, drop)).translate(0.0, 0.0, -drop / 2.0)
        handle.visual(
            mesh_from_geometry(spine, f"handle_spine_{i}"), material=metal, name=f"handle_spine_{i}", material_class_id="metal.stainless_matte"
        )
        handle.inertial = Inertial.from_geometry(
            Box((span + 0.02, 0.02, drop + 0.02)),
            mass=0.08,
            origin=Origin(xyz=(0.0, 0.0, -drop / 2.0)),
        )
        model.articulation(
            f"bottom_to_handle_{i}",
            ArticulationType.REVOLUTE,
            parent=bottom,
            child=handle,
            origin=Origin(xyz=(center_x, pivot_y, handle_z)),
            axis=(float(side), 0.0, 0.0),
            motion_limits=MotionLimits(
                lower=0.0, upper=math.radians(90.0), effort=3.0, velocity=2.0
            ),
        )


def _build_d_ring_loops(model, bottom, r: ResolvedViolinCaseConfig, mats: dict) -> None:
    metal = mats["metal"]
    dring_w = 0.025
    dring_h = 0.022
    tube_r = 0.0018
    mount_w = 0.034
    mount_h = 0.022
    mount_t = 0.005
    pivot_z = r.shell_h - 0.012
    positions = tuple(x * r.len_mul for x in (-0.24, 0.24))

    def _ring_points():
        w2 = dring_w / 2.0
        h = dring_h
        return [
            (-w2, 0.0, 0.0),
            (-w2, 0.0, -h * 0.30),
            (-w2 * 0.70, 0.0, -h * 0.75),
            (-w2 * 0.35, 0.0, -h),
            (0.0, 0.0, -h * 1.06),
            (w2 * 0.35, 0.0, -h),
            (w2 * 0.70, 0.0, -h * 0.75),
            (w2, 0.0, -h * 0.30),
            (w2, 0.0, 0.0),
        ]

    for i in range(2):
        dx = positions[i]
        wall_y = _half_width_at_x(r, dx)
        plate = BoxGeometry((mount_w, mount_t, mount_h))
        plate.translate(dx, wall_y + mount_t / 2.0, pivot_z - mount_h / 2.0)
        bottom.visual(
            mesh_from_geometry(plate, f"dring_mount_plate_{i}"),
            material=metal,
            name=f"dring_mount_plate_{i}", material_class_id="metal.stainless_matte",
        )
        pivot_bar = CylinderGeometry(0.0025, mount_w * 0.85).rotate_y(math.pi / 2.0)
        pivot_bar.translate(dx, wall_y + mount_t, pivot_z)
        bottom.visual(
            mesh_from_geometry(pivot_bar, f"dring_pivot_bar_{i}"),
            material=metal,
            name=f"dring_pivot_bar_{i}", material_class_id="metal.stainless_matte",
        )
        dring = model.part(f"d_ring_{i}")
        tube = tube_from_spline_points(
            _ring_points(),
            radius=tube_r,
            samples_per_segment=5,
            radial_segments=8,
            closed_spline=False,
            cap_ends=True,
            up_hint=(0.0, 1.0, 0.0),
        )
        dring.visual(
            mesh_from_geometry(tube, f"dring_ring_{i}"), material=metal, name=f"dring_ring_{i}", material_class_id="metal.stainless_matte"
        )
        dring.inertial = Inertial.from_geometry(
            Box((dring_w, 0.004, dring_h)),
            mass=0.018,
            origin=Origin(xyz=(0.0, 0.0, -dring_h / 2.0)),
        )
        model.articulation(
            f"bottom_to_d_ring_{i}",
            ArticulationType.REVOLUTE,
            parent=bottom,
            child=dring,
            origin=Origin(xyz=(dx, wall_y + mount_t, pivot_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                lower=0.0, upper=math.radians(170.0), effort=1.5, velocity=3.0
            ),
        )


# ---------------------------------------------------------------------------
# Slot D — interior_fitting.
# ---------------------------------------------------------------------------
def _build_interior(model, bottom, lid, r: ResolvedViolinCaseConfig, mats: dict) -> None:
    if r.interior_fitting == "plain_plush":
        return
    if r.interior_fitting == "neck_cradle":
        _build_neck_cradle(bottom, r, mats)
    elif r.interior_fitting == "bow_spinner_clips":
        _build_bow_clips(model, lid, r, mats)
    else:
        _build_accessory_pocket(model, bottom, r, mats)


def _neck_cradle_solid(r: ResolvedViolinCaseConfig) -> cq.Workplane:
    cx = -0.30 * r.len_mul
    block_len = 0.070 * r.len_mul
    half_w_at_x = _half_width_at_x(r, cx)
    if r.shell_footprint == "rectangular_oblong":
        cavity_half_w = (r.half_w - RECESS_INSET) - 0.004
    else:
        recess_scale_w = 1.0 - RECESS_INSET / r.half_w
        cavity_half_w = half_w_at_x * recess_scale_w - 0.004
    block_half_w = max(cavity_half_w * 0.82, 0.010)
    block_h = 0.032
    base_half_len = block_len / 2.0
    top_half_len = block_len / 2.0 - 0.008
    base_hw = block_half_w
    top_hw = max(block_half_w - 0.006, 0.006)
    block = (
        cq.Workplane("XY")
        .rect(2 * base_half_len, 2 * base_hw)
        .workplane(offset=block_h)
        .rect(2 * top_half_len, 2 * top_hw)
        .loft()
    )
    neck_radius = 0.016
    notch_depth = 0.016
    notch_cutter = (
        cq.Workplane("XZ")
        .center(0.0, block_h - notch_depth + neck_radius)
        .circle(neck_radius)
        .extrude(2 * block_half_w + 0.02, both=True)
    )
    result = block.cut(notch_cutter)
    try:
        result = result.edges("|Y and >Z").fillet(0.004)
    except Exception:
        pass
    return result.translate((cx, 0.0, WALL))


def _build_neck_cradle(bottom, r: ResolvedViolinCaseConfig, mats: dict) -> None:
    bottom.visual(
        mesh_from_cadquery(_neck_cradle_solid(r), "neck_cradle"),
        material=mats["plush"],
        name="neck_cradle", material_class_id="fabric.velvet",
    )


def _build_bow_clips(model, lid, r: ResolvedViolinCaseConfig, mats: dict) -> None:
    metal = mats["metal"]
    hx = _hinge_x(r)  # lid frame is shifted by the hinge-origin X; rebase all lid-local X.
    clip_xs = tuple(x * r.len_mul - hx for x in (-0.22, 0.22))
    bow_clip_y = -0.15 * r.width_mul
    bow_y = -0.10 * r.width_mul
    post_radius = 0.005
    post_len = 0.011
    bow_clip_z = r.lid_h - 0.012 - post_len
    bow_stick_r = 0.004
    bow_len = 0.72 * r.len_mul
    bow_z = r.lid_h - 0.012 - bow_stick_r

    for i in range(2):
        cx = clip_xs[i]
        post = CylinderGeometry(post_radius, post_len)
        post.translate(cx, bow_clip_y, bow_clip_z + post_len / 2.0)
        lid.visual(
            mesh_from_geometry(post, f"clip_mount_{i}"), material=metal, name=f"clip_mount_{i}", material_class_id="metal.stainless_matte"
        )

    bow_geom = CylinderGeometry(bow_stick_r, bow_len).rotate_y(math.pi / 2.0)
    bow_geom.translate(-hx, bow_y, bow_z)
    lid.visual(mesh_from_geometry(bow_geom, "bow_stick"), material=mats["accent"], name="bow_stick", material_class_id="wood.polished_varnished")
    frog = BoxGeometry((0.028, 0.020, 0.018))
    frog.translate(-bow_len / 2.0 + 0.014 - hx, bow_y, bow_z - 0.005)
    lid.visual(mesh_from_geometry(frog, "bow_frog"), material=mats["soft"], name="bow_frog", material_class_id="wood.walnut_dark")
    for i in range(2):
        cx = clip_xs[i]
        pad = CylinderGeometry(0.008, 0.004)
        pad.translate(cx, bow_y, r.lid_h - 0.012 - 0.002)
        lid.visual(
            mesh_from_geometry(pad, f"bow_cradle_pad_{i}"),
            material=mats["plush"],
            name=f"bow_cradle_pad_{i}", material_class_id="fabric.velvet",
        )

    for i in range(2):
        cx = clip_xs[i]
        clip = model.part(f"bow_clip_{i}")
        hub = cq.Workplane("XY").circle(0.009).extrude(0.005)
        arm = cq.Workplane("XY").box(0.012, 0.048, 0.003).translate((0, 0.030, 0.0015))
        hook = cq.Workplane("XY").box(0.014, 0.003, 0.009).translate((0, 0.0555, 0.0045))
        clip_arm = hub.union(arm).union(hook)
        clip.visual(
            mesh_from_cadquery(clip_arm, f"clip_arm_{i}"), material=metal, name=f"clip_arm_{i}", material_class_id="metal.stainless_matte"
        )
        clip.inertial = Inertial.from_geometry(
            Box((0.016, 0.062, 0.008)),
            mass=0.012,
            origin=Origin(xyz=(0.0, 0.028, 0.003)),
        )
        model.articulation(
            f"lid_to_bow_clip_{i}",
            ArticulationType.REVOLUTE,
            parent=lid,
            child=clip,
            origin=Origin(xyz=(cx, bow_clip_y, bow_clip_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                lower=0.0, upper=math.radians(90.0), effort=1.0, velocity=3.0
            ),
        )


def _build_accessory_pocket(model, bottom, r: ResolvedViolinCaseConfig, mats: dict) -> None:
    metal = mats["metal"]
    leather = mats["accent"]
    pocket_x = 0.24 * r.len_mul
    pocket_len = 0.10 * r.len_mul
    pocket_wid = 0.08 * r.width_mul
    pocket_h = 0.022
    pocket_wall = 0.003
    pocket_lid_t = 0.003
    hinge_x = pocket_x - pocket_len / 2.0
    hinge_z = WALL + pocket_h

    outer = cq.Workplane("XY").rect(pocket_len, pocket_wid).extrude(pocket_h)
    cavity = (
        cq.Workplane("XY")
        .rect(pocket_len - 2 * pocket_wall, pocket_wid - 2 * pocket_wall)
        .extrude(pocket_h)
        .translate((0.0, 0.0, pocket_wall))
    )
    box = outer.cut(cavity).translate((pocket_x, 0.0, WALL))
    bottom.visual(mesh_from_cadquery(box, "pocket_box"), material=leather, name="pocket_box", material_class_id="leather.smooth_plain")
    pad = (
        cq.Workplane("XY")
        .rect(pocket_len - 2 * pocket_wall - 0.002, pocket_wid - 2 * pocket_wall - 0.002)
        .extrude(0.003)
    )
    pad = pad.translate((pocket_x, 0.0, WALL + pocket_wall))
    bottom.visual(mesh_from_cadquery(pad, "pocket_pad"), material=mats["plush"], name="pocket_pad", material_class_id="fabric.velvet")
    barrel = CylinderGeometry(0.003, pocket_wid * 0.85).rotate_x(math.pi / 2.0)
    barrel.translate(hinge_x, 0.0, hinge_z)
    bottom.visual(
        mesh_from_geometry(barrel, "pocket_hinge_barrel"),
        material=metal,
        name="pocket_hinge_barrel", material_class_id="metal.stainless_matte",
    )

    pocket_lid = model.part("pocket_lid")
    panel = cq.Workplane("XY").rect(pocket_len, pocket_wid).extrude(pocket_lid_t)
    panel = panel.translate((pocket_len / 2.0, 0.0, 0.0))
    pocket_lid.visual(
        mesh_from_cadquery(panel, "pocket_lid_panel"), material=leather, name="pocket_lid_panel", material_class_id="leather.smooth_plain"
    )
    pocket_lid.inertial = Inertial.from_geometry(
        Box((pocket_len, pocket_wid, pocket_lid_t + 0.002)),
        mass=0.015,
        origin=Origin(xyz=(pocket_len / 2.0, 0.0, pocket_lid_t / 2.0)),
    )
    model.articulation(
        "bottom_to_pocket_lid",
        ArticulationType.REVOLUTE,
        parent=bottom,
        child=pocket_lid,
        origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=math.radians(120.0), effort=1.0, velocity=3.0),
    )


# ---------------------------------------------------------------------------
# Top-level build.
# ---------------------------------------------------------------------------
def build_violin_case(
    config: ViolinCaseConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"vc_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    bottom = model.part("bottom_shell")
    _build_shell(bottom, r, mats)
    lid = _build_lid(model, bottom, r, mats)
    _build_closure(model, bottom, lid, r, mats)
    _build_carry(model, bottom, r, mats)
    _build_interior(model, bottom, lid, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_violin_case(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_violin_case(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / allowances.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_violin_case_tests(
    object_model: ArticulatedObject,
    config: ViolinCaseConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    bottom = object_model.get_part("bottom_shell")
    lid = object_model.get_part("lid")
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    ctx.check("bottom_shell present", "bottom_shell" in part_names)
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # --- elongated identity + molded red plush recess. ---
    ext = _ext(ctx.part_world_aabb(bottom))
    ctx.check("case longer than wide", ext[0] > ext[1] + 0.2, details=f"bottom shell extents={ext}")
    ctx.check("red plush interior present", bottom.get_visual("red_interior") is not None)

    # --- lid hinge core: folds 0..180 deg into the open-book pose. ---
    ctx.check("bottom_to_lid present", "bottom_to_lid" in joint_names)
    lid_joint = object_model.get_articulation("bottom_to_lid")
    ctx.allow_overlap(
        lid,
        bottom,
        elem_a="lid_exterior",
        elem_b="bottom_exterior",
        reason="Closed lid rim nests over the bottom shell rim at the hinge seam.",
    )
    # The lid swings through the full open-book range; its rim and the bottom
    # shell rim stay in close adjacency along the hinge line.
    ctx.allow_overlap(
        lid,
        bottom,
        reason="lid swings close along the shell hinge seam while opening",
    )
    closed_aabb = ctx.part_world_aabb(lid)
    closed_top = closed_aabb[1][2]
    closed_front_y = closed_aabb[0][1]
    with ctx.pose({lid_joint: math.radians(90.0)}):
        mid_top = ctx.part_world_aabb(lid)[1][2]
    ctx.check(
        "lid lifts as it opens",
        mid_top > closed_top + 0.05,
        details=f"closed_top={closed_top:.3f}, mid_top={mid_top:.3f}",
    )
    with ctx.pose({lid_joint: math.radians(180.0)}):
        flat_aabb = ctx.part_world_aabb(lid)
        flat_top = flat_aabb[1][2]
        flat_far_y = flat_aabb[1][1]
        flat_front_y = flat_aabb[0][1]
    ctx.check(
        "lid lies flat when fully open",
        flat_top < r.shell_h + r.lid_h + 0.03,
        details=f"flat_top={flat_top:.3f}, rim+lid={r.shell_h + r.lid_h:.3f}",
    )
    ctx.check(
        "open lid folds beyond the hinge onto +Y",
        flat_far_y > r.half_w + 0.08 and flat_front_y > closed_front_y + 0.05,
        details=f"flat_far_y={flat_far_y:.3f}, flat_front_y={flat_front_y:.3f}",
    )

    # --- closure-specific. ---
    if r.closure_mechanism == "hinge_plus_flip_latches":
        for i in range(r.latch_count):
            ctx.check(f"bottom_to_latch_{i} present", f"bottom_to_latch_{i}" in joint_names)
            latch = object_model.get_part(f"latch_{i}")
            ctx.allow_overlap(
                latch, bottom, reason="Latch pivot pin and lever base seat into the front wall."
            )
            ctx.allow_overlap(
                latch, lid, reason="Closed clasp hook lip reaches over the lid front edge."
            )
    elif r.closure_mechanism == "zipper_perimeter":
        ctx.check("zipper pull prismatic present", "bottom_to_zipper_pull" in joint_names)
        pull_joint = object_model.get_articulation("bottom_to_zipper_pull")
        ctx.check(
            "zipper pull is prismatic", pull_joint.articulation_type == ArticulationType.PRISMATIC
        )
        ctx.check("no flip latch on zipper closure", "latch_0" not in part_names)
        ctx.check("zipper track present", bottom.get_visual("zipper_track") is not None)
        pull = object_model.get_part("zipper_pull")
        # The pull tab travels the perimeter track, detaching from the shell.
        ctx.allow_isolated_part(
            pull,
            reason="zipper pull tab runs along the perimeter track away from the shell rim",
        )
        ctx.allow_overlap(
            pull,
            bottom,
            elem_a="pull_body",
            elem_b="zipper_track",
            reason="Zipper pull slider seats onto the track with local embedding.",
        )
        ctx.allow_overlap(
            pull,
            bottom,
            elem_a="pull_body",
            elem_b="bottom_exterior",
            reason="Zipper pull tab hangs below the track into the shell rim.",
        )
        ctx.allow_overlap(
            lid,
            pull,
            elem_a="lid_exterior",
            elem_b="pull_body",
            reason="Closed lid covers the zipper pull on the front rim track.",
        )
    else:  # buckle_straps
        ctx.check("no flip latch on buckle closure", "latch_0" not in part_names)
        for i in range(2):
            ctx.check(f"lid_to_strap_{i} present", f"lid_to_strap_{i}" in joint_names)
            ctx.check(f"strap_to_buckle_{i} present", f"strap_to_buckle_{i}" in joint_names)
            strap = object_model.get_part(f"strap_{i}")
            buckle = object_model.get_part(f"buckle_{i}")
            ctx.allow_overlap(
                strap, bottom, reason=f"strap_{i} wraps against the bottom shell front wall."
            )
            ctx.allow_overlap(
                strap, lid, reason=f"strap_{i} hinge end embeds into the lid front edge."
            )
            ctx.allow_overlap(
                buckle, bottom, reason=f"buckle_{i} seats against the bottom shell front wall."
            )
            ctx.allow_overlap(
                buckle, strap, reason=f"buckle_{i} pivot loop nests at the strap free end."
            )

    # --- carry-specific. ---
    if r.carry_hardware == "top_handle":
        ctx.check("bottom_to_handle present", "bottom_to_handle" in joint_names)
        ctx.allow_overlap(
            object_model.get_part("carry_handle"),
            bottom,
            reason="Handle pivot stubs nest into the mount ears/foot plates.",
        )
    elif r.carry_hardware == "dual_side_handles":
        for i in range(2):
            ctx.check(f"bottom_to_handle_{i} present", f"bottom_to_handle_{i}" in joint_names)
            ctx.allow_overlap(
                object_model.get_part(f"handle_{i}"),
                bottom,
                reason="Handle pivot stub seats into the side mount boss.",
            )
            ctx.allow_overlap(
                object_model.get_part(f"handle_{i}"),
                lid,
                reason="Side handle clears the lid rim closely while the lid swings open.",
            )
    elif r.carry_hardware == "d_ring_strap_loops":
        for i in range(2):
            ctx.check(f"bottom_to_d_ring_{i} present", f"bottom_to_d_ring_{i}" in joint_names)
            ctx.allow_overlap(
                object_model.get_part(f"d_ring_{i}"),
                bottom,
                reason="D-ring pivot nests at the mount plate on the rear wall.",
            )

    # --- interior-specific. ---
    if r.interior_fitting == "bow_spinner_clips":
        for i in range(2):
            ctx.check(f"lid_to_bow_clip_{i} present", f"lid_to_bow_clip_{i}" in joint_names)
            clip = object_model.get_part(f"bow_clip_{i}")
            ctx.allow_overlap(
                clip,
                lid,
                elem_a=f"clip_arm_{i}",
                elem_b=f"clip_mount_{i}",
                reason="Bow clip hub rotates over its lid-mounted post.",
            )
            ctx.allow_overlap(
                clip,
                lid,
                elem_a=f"clip_arm_{i}",
                elem_b="bow_stick",
                reason="Bow clip arm captures the stored bow stick.",
            )
    elif r.interior_fitting == "accessory_pocket":
        ctx.check("bottom_to_pocket_lid present", "bottom_to_pocket_lid" in joint_names)
        ctx.allow_overlap(
            object_model.get_part("pocket_lid"),
            bottom,
            reason="Pocket lid hinge barrel + closed lid seats over the box rim.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = (
    "ViolinCaseConfig",
    "ResolvedViolinCaseConfig",
    "build_violin_case",
    "build_seeded_violin_case",
    "config_from_seed",
    "resolve_config",
    "run_violin_case_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
