# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template — wire_stripper (Electrical_Wiring / Wire stripper).

FORM-DOMINATED: the ③ ``mechanism_family`` slot swaps the whole part tree +
joint topology across three families (different joint graphs):

- ``manual_notch_plier`` / ``fixed_hole_gauge``  (A skeleton, meters via MM):
  ``fixed_arm``(root) + ``moving_arm`` + ``lock_latch``; joints
  ``pivot_squeeze`` REVOLUTE(+Z) + ``latch_pivot`` REVOLUTE(-Z). Tool in XY
  plane (+X nose, Y opening, Z thickness), pivot at origin; arms authored
  closed then counter-rotated ±DELTA into the open rest pose. Geometry is all
  CadQuery boolean: ``_a_poly_solid`` / ``_a_circle_solid`` /
  ``_a_cut_edge_circles`` carve real graduated notch/gauge cuts + nose
  serrations; grips are catmull-rom spline lofts + fillet (never Box).
- ``auto_selfadjust``  (B skeleton, meters direct): ``fixed_arm``(root body) +
  ``moving_arm``(crossed lever) + ``wire_stop_slider`` (+ optional
  ``gripping_jaw`` clamp part); joints ``arm_pivot`` REVOLUTE(+Z) +
  ``wire_stop_slide`` PRISMATIC(+X) (+ optional ``clamp_pinch`` REVOLUTE mimic).
  Geometry = stamped-plate ExtrudeGeometry, outboard head cheeks, connected
  ergonomic overmolds, BoxGeometry/Cylinder hardware, and a spline coil spring.
  Both the plate and its overmould are offset from one shared handle spine
  (``_B_HANDLE_SPINES``), so a handle candidate bends the steel rather than
  raking rubber past a shank that stayed put.

Slots (registered in ``slot_choices``): ③ ``mechanism_family`` (3) ·
``handle_form`` (5, family-gated: 2 on the A skeleton, 3 on B) · ``jaw_feature``
(7, family-gated: 3 manual / 2 gauge / 2 auto) · ② ``auto_clamp_dof`` (2, auto
only) · ① ``gauge_station`` N (all three families: manual 3-8, gauge 3-7, auto
3-6 stripping dies).  core_domain = 22, raw_domain = 104.  ``palette_style``
(5 realistic colorways) drives every material and counts toward neither.

Sources: origin A ``rec_a-…a2129614`` + origin B ``rec_an-…e60caa10`` + forks
fixed_hole_gauge / crimp_die_station / gauge_n6 / pistol_grip / auto_clamp_jaw.
The extrapolated candidates (``offset_kick_plier``, ``inline_slim``,
``notch_bolt_shear``, ``gauge_slot_plate``, ``clamp_vgroove_die``) have no source
record of their own; they are documented as extrapolations in the SourceMap.
The pivot is captured-pin geometry (shaft through the moving lap / crossed hub),
so the pivot joint omits MatingContract (grandfathered) and is guarded by the
flat 0.015 articulation-origin baseline + element-scoped ``allow_overlap``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal, Optional

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    BoxGeometry,
    Cylinder,
    CylinderGeometry,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    sample_catmull_rom_spline_2d,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot vocabularies
# ---------------------------------------------------------------------------
MechanismFamily = Literal["manual_notch_plier", "fixed_hole_gauge", "auto_selfadjust"]
HandleForm = Literal[
    "straight_plier", "offset_kick_plier",          # A skeleton
    "angled_offset", "pistol_grip", "inline_slim",  # B skeleton
]
JawFeature = Literal[
    "notch_cutter", "notch_crimp_die", "notch_bolt_shear",  # manual
    "gauge_hole_plate", "gauge_slot_plate",                 # gauge
    "clamp_screw", "clamp_vgroove_die",                     # auto
]
AutoClampDof = Literal["abstracted", "real_clamp_joint"]
PaletteStyle = Literal["yellow_black", "red_black", "gunmetal", "blue_black", "safety_orange"]

FAMILIES: tuple[MechanismFamily, ...] = (
    "manual_notch_plier",
    "fixed_hole_gauge",
    "auto_selfadjust",
)
A_FAMILIES: tuple[MechanismFamily, ...] = ("manual_notch_plier", "fixed_hole_gauge")
A_HANDLES: tuple[HandleForm, ...] = ("straight_plier", "offset_kick_plier")
B_HANDLES: tuple[HandleForm, ...] = ("angled_offset", "pistol_grip", "inline_slim")
MANUAL_JAWS: tuple[JawFeature, ...] = ("notch_cutter", "notch_crimp_die", "notch_bolt_shear")
GAUGE_JAWS: tuple[JawFeature, ...] = ("gauge_hole_plate", "gauge_slot_plate")
AUTO_JAWS: tuple[JawFeature, ...] = ("clamp_screw", "clamp_vgroove_die")
# Outboard kick added to the A-family handle past the shank root (mm/mm ramp).
HANDLE_KICKS: dict[str, float] = {"straight_plier": 0.0, "offset_kick_plier": 0.108}
# gauge_station N is now a real multiplicity axis in all three families.
N_RANGE: dict[MechanismFamily, tuple[int, int]] = {
    "manual_notch_plier": (3, 8),
    "fixed_hole_gauge": (3, 7),
    "auto_selfadjust": (3, 6),
}
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "yellow_black",
    "red_black",
    "gunmetal",
    "blue_black",
    "safety_orange",
)

# Semantic material keys used across BOTH families; every .visual() material is
# mats[<key>] so palette_style recolors the whole swept output.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "yellow_black": {
        "steel_body": (0.14, 0.145, 0.15, 1.0),
        "steel_bright": (0.80, 0.82, 0.84, 1.0),
        "grip_main": (0.95, 0.76, 0.05, 1.0),
        "grip_dark": (0.055, 0.055, 0.06, 1.0),
        "spring": (0.24, 0.24, 0.26, 1.0),
        "hardware": (0.10, 0.10, 0.11, 1.0),
        "brass": (0.72, 0.58, 0.25, 1.0),
        "jaw": (0.14, 0.14, 0.15, 1.0),
        "slider": (0.85, 0.10, 0.09, 1.0),
    },
    "red_black": {
        "steel_body": (0.10, 0.10, 0.11, 1.0),
        "steel_bright": (0.75, 0.77, 0.80, 1.0),
        "grip_main": (0.78, 0.08, 0.07, 1.0),
        "grip_dark": (0.05, 0.05, 0.05, 1.0),
        "spring": (0.25, 0.26, 0.28, 1.0),
        "hardware": (0.10, 0.10, 0.11, 1.0),
        "brass": (0.72, 0.58, 0.25, 1.0),
        "jaw": (0.14, 0.14, 0.15, 1.0),
        "slider": (0.85, 0.10, 0.09, 1.0),
    },
    "gunmetal": {
        "steel_body": (0.28, 0.29, 0.31, 1.0),
        "steel_bright": (0.66, 0.68, 0.72, 1.0),
        "grip_main": (0.34, 0.35, 0.38, 1.0),
        "grip_dark": (0.08, 0.08, 0.09, 1.0),
        "spring": (0.30, 0.31, 0.33, 1.0),
        "hardware": (0.12, 0.12, 0.13, 1.0),
        "brass": (0.70, 0.60, 0.30, 1.0),
        "jaw": (0.18, 0.18, 0.20, 1.0),
        "slider": (0.55, 0.12, 0.10, 1.0),
    },
    "blue_black": {
        "steel_body": (0.16, 0.17, 0.19, 1.0),
        "steel_bright": (0.78, 0.80, 0.84, 1.0),
        "grip_main": (0.10, 0.24, 0.55, 1.0),
        "grip_dark": (0.05, 0.05, 0.06, 1.0),
        "spring": (0.24, 0.24, 0.26, 1.0),
        "hardware": (0.10, 0.10, 0.11, 1.0),
        "brass": (0.72, 0.58, 0.25, 1.0),
        "jaw": (0.14, 0.14, 0.15, 1.0),
        "slider": (0.90, 0.72, 0.10, 1.0),
    },
    "safety_orange": {
        "steel_body": (0.15, 0.155, 0.16, 1.0),
        "steel_bright": (0.82, 0.84, 0.86, 1.0),
        "grip_main": (0.95, 0.42, 0.10, 1.0),
        "grip_dark": (0.10, 0.10, 0.11, 1.0),
        "spring": (0.24, 0.24, 0.26, 1.0),
        "hardware": (0.08, 0.08, 0.09, 1.0),
        "brass": (0.72, 0.58, 0.25, 1.0),
        "jaw": (0.14, 0.14, 0.15, 1.0),
        "slider": (0.15, 0.15, 0.16, 1.0),
    },
}

# ---------------------------------------------------------------------------
# A-family (manual / gauge) constants — millimetre numbers scaled by `mm`.
# ---------------------------------------------------------------------------
T_STEEL = 6.0
Z_TOP = T_STEEL / 2.0
Z_BOT = -T_STEEL / 2.0
LAP_GAP = 0.30
BOSS_R = 12.0
PIN_BORE_R = 2.9
PIN_SHAFT_R = PIN_BORE_R + 0.15
PLATE_HOLE_R = 3.3
SHANK_SLOPE = 8.5 / 35.4
HOLE_CY = 7.5
CRIMP_SPECS = [(16.5, 2.6), (22.0, 2.3)]
CRIMP_DIE_SPECS = [(17.5, 2.4), (22.5, 1.9)]
MESH_TOL = 0.00015
MESH_ANG = 0.25
DELTA_BASE = 0.19

# ---------------------------------------------------------------------------
# B-family (auto) constants — meters direct.
# ---------------------------------------------------------------------------
PLATE_T = 0.003
BODY_PLATE_ZC = -0.0017
LEVER_PLATE_ZC = 0.0017
SQUEEZE_BASE = 0.10
SLIDE_MAX = 0.008
CLAMP_ANGLE = 0.04

# Head plan geometry.  The two stamped halves overlap across the centreline
# behind HEAD_WINDOW_X0 and only part into a real wire slot in front of it, so
# the head reads as solid steel instead of one full-length see-through slit.
HEAD_WINDOW_X0 = 0.0435
HEAD_WEB_Y = -0.0038
HEAD_FACE_Y = 0.0010

# Pivot.  The stamped hub is the wide disc; the chrome button is a rivet head
# just large enough to capture the bore, not a cap wider than the plate itself.
PIVOT_BOSS_R = 0.0165
PIVOT_BORE_R = 0.0105
PIVOT_SHAFT_R = 0.0090
PIVOT_CAP_R = 0.0110

# Handle spines.  Every handle candidate bends the *steel* centreline here and
# the overmould is emitted from the same nodes, so a grip can never drift off
# its shank the way a separately-raked slab did.  Nodes are
# ``(x, centre y, plate half width)`` for the body (-Y) arm with x descending
# from the pivot; the lever arm is the y-mirror.
#
# Every spine opens with a steep fan-out segment straight behind the head.  A
# crossed-lever stripper really does splay there, and it is also what buys the
# two overmoulds their clearance: with a single shallow rake the arms are still
# closer than one grip width at x=-0.035, which is exactly why the source fork
# had to shove its rubber outboard of the steel to keep the handles apart.
_SHANK_X0 = -0.0105
_B_HANDLE_SPINES: dict[str, tuple[tuple[float, float, float], ...]] = {
    # source B: fan-out, then one shallow outward rake to the tail
    "angled_offset": (
        (_SHANK_X0, 0.0, 0.0105),
        (-0.0400, -0.0195, 0.0100),
        (-0.1400, -0.0352, 0.0084),
    ),
    # pistol fork, repaired: the steel now kicks at the knuckle instead of the
    # overmould leaving a straight shank behind
    "pistol_grip": (
        (_SHANK_X0, 0.0, 0.0105),
        (-0.0400, -0.0195, 0.0100),
        (-0.0700, -0.0262, 0.0098),
        (-0.1380, -0.0555, 0.0104),
    ),
    # compact automatic stripper: long, slim, nearly inline handles
    "inline_slim": (
        (_SHANK_X0, 0.0, 0.0100),
        (-0.0380, -0.0175, 0.0094),
        (-0.1420, -0.0262, 0.0074),
    ),
}
_B_GRIP_STYLES: dict[str, dict[str, float]] = {
    "angled_offset": {"thickness": 0.0128, "proud": 0.0022,
                      "overlap": 0.004, "cap_len": 0.020, "cap_proud": 0.0044, "palm": 0.0},
    "pistol_grip": {"thickness": 0.0150, "proud": 0.0026,
                    "overlap": 0.005, "cap_len": 0.018, "cap_proud": 0.0050, "palm": 0.0078},
    "inline_slim": {"thickness": 0.0112, "proud": 0.0018,
                    "overlap": 0.004, "cap_len": 0.022, "cap_proud": 0.0038, "palm": 0.0},
}
# Minimum plan clearance the two overmoulds must keep at the grip root.
GRIP_ROOT_CLEARANCE = 0.003
# Serrated cutter teeth on the inner shank edge (ported from source B).
_B_TEETH_X0, _B_TEETH_PITCH, _B_TEETH_N, _B_TEETH_DEPTH = -0.0196, 0.0072, 5, 0.0045


@dataclass(frozen=True)
class WireStripperConfig:
    mechanism_family: Optional[MechanismFamily] = None
    handle_form: Optional[HandleForm] = None
    jaw_feature: Optional[JawFeature] = None
    auto_clamp_dof: Optional[AutoClampDof] = None
    gauge_count: Optional[int] = None
    palette_style: PaletteStyle = "yellow_black"
    open_angle_scale: float = 1.0
    overall_scale: float = 1.0
    name: str = "wire_stripper"


@dataclass(frozen=True)
class ResolvedWireStripperConfig:
    mechanism_family: MechanismFamily
    handle_form: HandleForm
    jaw_feature: JawFeature
    auto_clamp_dof: AutoClampDof
    gauge_count: int
    palette_style: PaletteStyle
    delta: float
    q_close: float
    squeeze_max: float
    mm_scale: float
    name: str

    @property
    def is_auto(self) -> bool:
        return self.mechanism_family == "auto_selfadjust"

    @property
    def is_gauge(self) -> bool:
        return self.mechanism_family == "fixed_hole_gauge"


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# config_from_seed — procedural weighted sampling (seed 0 not special).
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> WireStripperConfig:
    rng = random.Random(seed)
    family = rng.choices(FAMILIES, weights=[4, 2, 3], k=1)[0]
    if family == "auto_selfadjust":
        handle = rng.choices(B_HANDLES, weights=[4, 3, 2], k=1)[0]
        jaw = rng.choices(AUTO_JAWS, weights=[3, 2], k=1)[0]
        dof = rng.choices(["abstracted", "real_clamp_joint"], weights=[3, 2], k=1)[0]
        gauge = rng.choices([3, 4, 5, 6], weights=[3, 5, 4, 2], k=1)[0]
    else:
        handle = rng.choices(A_HANDLES, weights=[3, 2], k=1)[0]
        dof = "abstracted"
        if family == "manual_notch_plier":
            jaw = rng.choices(MANUAL_JAWS, weights=[3, 2, 2], k=1)[0]
            gauge = rng.choices([3, 4, 5, 6, 7, 8], weights=[3, 5, 4, 3, 1, 1], k=1)[0]
        else:
            jaw = rng.choices(GAUGE_JAWS, weights=[3, 2], k=1)[0]
            gauge = rng.choices([3, 4, 5, 6, 7], weights=[3, 4, 4, 2, 1], k=1)[0]
    return WireStripperConfig(
        mechanism_family=family,
        handle_form=handle,
        jaw_feature=jaw,
        auto_clamp_dof=dof,
        gauge_count=gauge,
        palette_style=rng.choice(PALETTE_STYLES),
        open_angle_scale=round(rng.uniform(0.90, 1.10), 4),
        overall_scale=round(rng.uniform(0.92, 1.08), 4),
        name=f"seeded_wire_stripper_{seed}",
    )


def resolve_config(config: WireStripperConfig | None = None) -> ResolvedWireStripperConfig:
    cfg = config or WireStripperConfig()
    family = _pick(cfg.mechanism_family, FAMILIES)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)
    open_scale = _clamp(cfg.open_angle_scale, 0.90, 1.10)

    n_lo, n_hi = N_RANGE[family]
    gauge = int(_clamp(cfg.gauge_count if cfg.gauge_count else 4, n_lo, n_hi))

    if family == "auto_selfadjust":
        handle = _pick(cfg.handle_form, B_HANDLES)
        jaw = _pick(cfg.jaw_feature, AUTO_JAWS)
        dof = cfg.auto_clamp_dof if cfg.auto_clamp_dof in ("abstracted", "real_clamp_joint") else "abstracted"
        squeeze_max = _clamp(SQUEEZE_BASE * open_scale, 0.09, 0.11)
        delta = 0.0
        q_close = 0.0
        mm_scale = 1.0
    else:
        handle = _pick(cfg.handle_form, A_HANDLES)
        dof = "abstracted"
        jaw = _pick(cfg.jaw_feature, MANUAL_JAWS if family == "manual_notch_plier" else GAUGE_JAWS)
        delta = _clamp(DELTA_BASE * open_scale, 0.16, 0.215)
        q_close = 2.0 * delta - 0.02
        squeeze_max = 0.0
        mm_scale = _clamp(cfg.overall_scale, 0.92, 1.08)

    return ResolvedWireStripperConfig(
        mechanism_family=family,
        handle_form=handle,
        jaw_feature=jaw,
        auto_clamp_dof=dof,
        gauge_count=gauge,
        palette_style=palette,
        delta=delta,
        q_close=q_close,
        squeeze_max=squeeze_max,
        mm_scale=mm_scale,
        name=cfg.name or "wire_stripper",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedWireStripperConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("mechanism_family", r.mechanism_family),
        ("handle_form", r.handle_form),
        ("jaw_feature", r.jaw_feature),
    ]
    if r.is_auto:
        choices.append(("auto_clamp_dof", r.auto_clamp_dof))
    choices.append(("gauge_station", f"gauge_n{r.gauge_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# gauge-station multiplicity spec generators (ascending-radius invariant).
# ---------------------------------------------------------------------------
def _a_notch_specs(n: int, x0: float = 26.0, x1: float = 47.0) -> list[tuple[float, float]]:
    """N graduated stripping notches (x centre mm, cut radius mm), ascending.

    ``x0`` shifts the station outboard when a bolt-shear rail occupies the
    pivot-side stretch of the blade line.
    """
    r0, r1 = 0.72, 2.15
    specs = []
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0.0
        specs.append((round(x0 + t * (x1 - x0), 3), round(r0 + t * (r1 - r0), 3)))
    return specs


def _a_awg_specs(n: int) -> list[tuple[float, float]]:
    """N drilled AWG gauge holes (x centre mm, hole radius mm), ascending.

    Sized to pass the *insulated* conductor, which is what a gauge plate is
    actually bored for; the earlier 0.34-1.28 mm conductor radii were correct
    for bare copper but rendered as invisible pinholes on a 200 mm tool.
    """
    x0, dx = 25.0, 7.0
    r0, r1 = 0.85, 2.55
    specs = []
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0.0
        specs.append((round(x0 + i * dx, 3), round(r0 + t * (r1 - r0), 3)))
    return specs


# Threaded bolt-shear station on the pivot side of the blade line (ascending).
BOLT_SHEAR_SPECS = [(14.5, 1.45), (18.8, 1.80), (23.1, 2.15)]


# ---------------------------------------------------------------------------
# A-family CadQuery helpers (port of origin A + gauge/crimp forks). `mm`
# threads a uniform overall_scale so every coordinate scales together.
# ---------------------------------------------------------------------------
def _rot2(p, a):
    c, s = math.cos(a), math.sin(a)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def _a_mirror(pts):
    return [(x, -y) for (x, y) in reversed(pts)]


def _a_poly_solid(pts_mm, z0, z1, mm):
    pts = [(x * mm, y * mm) for (x, y) in pts_mm]
    return cq.Workplane("XY", origin=(0.0, 0.0, z0 * mm)).polyline(pts).close().extrude((z1 - z0) * mm)


def _a_circle_solid(cx, cy, r, z0, z1, mm):
    return cq.Workplane("XY", origin=(cx * mm, cy * mm, z0 * mm)).circle(r * mm).extrude((z1 - z0) * mm)


def _a_cut_edge_circles(solid, specs, mm):
    for (x, r) in specs:
        solid = solid.cut(_a_circle_solid(x, 0.0, r, -20.0, 20.0, mm))
    return solid


def _shank_top_y(x):
    return -1.5 + SHANK_SLOPE * (x + 12.6)


def _shank_bot_y(x):
    return -9.5 + SHANK_SLOPE * (x + 12.6)


def _teeth_pts(x0=54.0, n=8, pitch=2.75, depth=1.0):
    pts = []
    for i in range(n):
        xa = x0 + i * pitch
        pts.append((xa + pitch * 0.5, depth))
        pts.append((xa + pitch, 0.0))
    return pts


def _jaw_profile():
    pts = [(13.0, 0.0), (54.0, 0.0)]
    pts += _teeth_pts()
    pts += [
        (79.3, 0.35), (80.2, 1.1),
        (76.5, 3.0), (66.0, 6.2), (56.0, 9.8), (50.0, 12.2),
        (46.0, 14.6), (40.0, 15.2), (24.0, 15.2), (16.0, 15.0),
        (13.0, 12.0),
    ]
    return pts


def _blade_face_profile():
    return [(13.6, 0.0), (48.0, 0.0), (46.0, 13.9), (40.0, 14.5),
            (24.0, 14.5), (16.4, 14.3), (13.6, 11.6)]


def _nose_face_profile():
    pts = [(50.5, 0.0), (54.0, 0.0)]
    pts += _teeth_pts()
    pts += [(79.0, 0.35), (79.6, 0.95), (76.2, 2.7), (66.0, 5.9), (56.0, 9.4), (50.5, 11.6)]
    return pts


def _shank_profile_a():
    return [(-12.6, -1.5), (-48.0, -10.0), (-48.0, -18.0), (-12.6, -9.5)]


def _a_kick(pts, kick):
    """Ramp the handle outboard past the shank root.  An offset handle has to
    bend the *steel* here as well as the overmould, so grip, colour split and
    outline all take the same ramp and stay one continuous handle."""
    if not kick:
        return list(pts)
    hinge = -46.0
    return [(x, y - kick * max(0.0, hinge - x)) for (x, y) in pts]


def _grip_profile_a():
    bottom_raw = [
        (-120.0, -20.0), (-122.5, -24.0), (-122.0, -29.0), (-118.0, -33.0),
        (-110.0, -33.8), (-90.0, -30.5), (-70.0, -26.5), (-52.0, -23.0), (-46.0, -22.0),
    ]
    bottom = sample_catmull_rom_spline_2d(bottom_raw, samples_per_segment=5)
    return [(-46.0, -8.0), (-80.0, -12.3)] + [(x, y) for (x, y) in bottom]


_SPLIT_LINE = [(-43.0, -19.3), (-70.0, -23.0), (-95.0, -27.5), (-114.0, -30.0), (-126.0, -25.0)]


def _region_below(line_pts):
    return list(line_pts) + [(-126.0, -70.0), (-43.0, -70.0)]


def _region_above(line_pts):
    return list(line_pts) + [(-126.0, 40.0), (-43.0, 40.0)]


def _collar_profile():
    return [
        (-15.0, _shank_top_y(-15.0) + 1.0),
        (-21.0, _shank_top_y(-21.0) + 1.0),
        (-21.0, _shank_bot_y(-21.0) - 1.0),
        (-15.0, _shank_bot_y(-15.0) - 1.0),
    ]


def _gauge_plate_profile():
    return [
        (13.0, 0.0), (72.0, 0.0), (76.0, 1.5), (77.5, 4.0), (77.5, 8.0),
        (76.0, 11.0), (72.0, 14.0), (50.0, 15.2), (24.0, 15.2), (16.0, 15.0), (13.0, 12.0),
    ]


def _pressure_jaw_profile():
    return [
        (13.0, 0.0), (72.0, 0.0), (75.0, -1.0), (76.0, -3.5), (76.0, -7.5),
        (75.0, -10.0), (72.0, -12.5), (50.0, -13.5), (24.0, -13.5), (16.0, -13.0), (13.0, -10.5),
    ]


def _a_build_jaw_plate(cut_specs, mm):
    solid = _a_poly_solid(_jaw_profile(), Z_BOT, Z_TOP, mm)
    v0 = solid.val().Volume()
    solid = _a_cut_edge_circles(solid, cut_specs, mm)
    v1 = solid.val().Volume()
    return solid, v0, v1


def _a_build_blade_face(cut_specs, mm):
    solid = _a_poly_solid(_blade_face_profile(), Z_TOP - 0.2, Z_TOP + 0.5, mm)
    return _a_cut_edge_circles(solid, cut_specs, mm)


def _a_build_nose_face(mm):
    return _a_poly_solid(_nose_face_profile(), Z_TOP - 0.2, Z_TOP + 0.5, mm)


def _a_gauge_neck(r):
    """Throat half-width of an open gauge slot for a hole of radius ``r``."""
    return 0.55 * r


def _a_cut_gauge_stations(solid, specs, mm, slotted):
    """Bore the graduated gauge stations.  ``slotted`` opens each bore to the
    working edge through a narrower throat, so wire can be laid in from the
    jaw line instead of threaded through a closed hole."""
    for (x, r) in specs:
        solid = solid.cut(_a_circle_solid(x, HOLE_CY, r, -20.0, 20.0, mm))
        if slotted:
            neck = _a_gauge_neck(r)
            throat = [(x - neck, -1.0), (x + neck, -1.0), (x + neck, HOLE_CY), (x - neck, HOLE_CY)]
            solid = solid.cut(_a_poly_solid(throat, -20.0, 20.0, mm))
    return solid


def _a_gauge_expected_volume(specs, mm, slotted):
    total = 0.0
    for (x, r) in specs:
        total += math.pi * (r * mm) ** 2 * (T_STEEL * mm)
        if slotted:
            open_len = max(0.0, HOLE_CY - r)
            total += 2.0 * _a_gauge_neck(r) * mm * open_len * mm * (T_STEEL * mm)
    return total


def _a_build_gauge_plate(specs, mm, slotted):
    solid = _a_poly_solid(_gauge_plate_profile(), Z_BOT, Z_TOP, mm)
    v0 = solid.val().Volume()
    solid = _a_cut_gauge_stations(solid, specs, mm, slotted)
    v1 = solid.val().Volume()
    return solid, v0, v1


def _a_build_gauge_face(specs, mm, slotted):
    solid = _a_poly_solid(_gauge_plate_profile(), Z_TOP - 0.2, Z_TOP + 0.5, mm)
    return _a_cut_gauge_stations(solid, specs, mm, slotted)


def _a_build_pressure_jaw(mm):
    return _a_poly_solid(_pressure_jaw_profile(), Z_BOT, Z_TOP, mm)


def _a_build_pressure_face(mm):
    return _a_poly_solid(_pressure_jaw_profile(), Z_TOP - 0.2, Z_TOP + 0.5, mm)


def _a_build_crimp_die_block(mirrored, mm):
    x0, x1 = 14.5, 25.5
    if not mirrored:
        y0, y1 = 0.0, 12.0
    else:
        y0, y1 = -12.0, 0.0
    z0, z1 = Z_TOP - 0.2, Z_TOP + 1.0
    block = _a_poly_solid([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, mm)
    for (cx, r) in CRIMP_DIE_SPECS:
        block = block.cut(_a_circle_solid(cx, 0.0, r, z0 - 1.0, z1 + 1.0, mm))
    try:
        block = block.edges(">Z").fillet(0.4 * mm)
    except Exception:
        try:
            block = block.edges(">Z").chamfer(0.3 * mm)
        except Exception:
            pass
    return block


def _a_build_shear_rail(mirrored, mm):
    """Proud threaded rail carrying the bolt-shear stations on the pivot side
    of the blade line.  The bores are cut through it so the shear holes read as
    one continuous station with the plate underneath."""
    x0, x1 = 12.0, 26.6
    if not mirrored:
        y0, y1 = 0.0, 10.5
    else:
        y0, y1 = -10.5, 0.0
    z0, z1 = Z_TOP - 0.2, Z_TOP + 1.2
    rail = _a_poly_solid([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, mm)
    for (cx, r) in BOLT_SHEAR_SPECS:
        rail = rail.cut(_a_circle_solid(cx, 0.0, r + 0.45, z0 - 1.0, z1 + 1.0, mm))
    try:
        rail = rail.edges(">Z").fillet(0.5 * mm)
    except Exception:
        try:
            rail = rail.edges(">Z").chamfer(0.35 * mm)
        except Exception:
            pass
    return rail


def _a_build_fixed_lap(mm):
    z0, z1 = Z_BOT, -LAP_GAP / 2.0
    disc = _a_circle_solid(0.0, 0.0, BOSS_R, z0, z1, mm)
    jaw_tab = _a_poly_solid([(9.0, 0.8), (16.0, 0.8), (16.0, 13.5), (9.0, 13.5)], z0, z1, mm)
    shank_tab = _a_poly_solid([(-16.0, -9.5), (-9.0, -9.5), (-9.0, -0.8), (-16.0, -0.8)], z0, z1, mm)
    return disc.union(jaw_tab).union(shank_tab)


def _a_build_moving_lap(mm):
    z0, z1 = LAP_GAP / 2.0, Z_TOP
    disc = _a_circle_solid(0.0, 0.0, BOSS_R, z0, z1, mm)
    disc = disc.cut(_a_circle_solid(0.0, 0.0, PIN_BORE_R, -20.0, 20.0, mm))
    jaw_tab = _a_poly_solid([(9.0, -13.5), (16.0, -13.5), (16.0, -0.8), (9.0, -0.8)], z0, z1, mm)
    shank_tab = _a_poly_solid([(-16.0, 0.8), (-9.0, 0.8), (-9.0, 9.5), (-16.0, 9.5)], z0, z1, mm)
    return disc.union(jaw_tab).union(shank_tab)


def _a_soften(solid, r_mm, mm):
    for sel in (">Z", "<Z"):
        try:
            solid = solid.edges(sel).fillet(r_mm * mm)
        except Exception:
            try:
                solid = solid.edges(sel).chamfer(0.6 * r_mm * mm)
            except Exception:
                pass
    return solid


def _a_build_grip_pair(mirrored, mm, kick=0.0):
    grip_pts = _a_kick(_grip_profile_a(), kick)
    split = _a_kick(_SPLIT_LINE, kick)
    split_low = [(x, y - 1.0) for (x, y) in split]
    if mirrored:
        grip_pts = _a_mirror(grip_pts)
        below = _a_poly_solid(_a_mirror(_region_below(split_low)), -9.0, 9.0, mm)
        above = _a_poly_solid(_a_mirror(_region_above(split)), -9.0, 9.0, mm)
    else:
        below = _a_poly_solid(_region_below(split_low), -9.0, 9.0, mm)
        above = _a_poly_solid(_region_above(split), -9.0, 9.0, mm)
    yellow = _a_poly_solid(grip_pts, -7.0, 7.0, mm).cut(below)
    black = _a_poly_solid(grip_pts, -7.6, 7.6, mm).cut(above)
    return _a_soften(yellow, 1.8, mm), _a_soften(black, 1.8, mm)


def _a_build_pivot_plate(mm):
    plate = cq.Workplane("XY", origin=(0.0, 0.0, 2.9 * mm)).ellipse(11.0 * mm, 8.0 * mm).extrude(0.5 * mm)
    plate = plate.cut(_a_circle_solid(0.0, 0.0, PLATE_HOLE_R, -20.0, 20.0, mm))
    slot = _a_poly_solid([(4.3, -1.2), (8.3, -1.2), (8.3, 1.2), (4.3, 1.2)], -20.0, 20.0, mm)
    slot = slot.union(_a_circle_solid(4.3, 0.0, 1.2, -20.0, 20.0, mm))
    slot = slot.union(_a_circle_solid(8.3, 0.0, 1.2, -20.0, 20.0, mm))
    return plate.cut(slot)


def _a_build_pivot_pin(mm):
    flange = CylinderGeometry(5.0 * mm, 1.4 * mm, radial_segments=40)
    flange.translate(0.0, 0.0, -3.5 * mm)
    shaft = CylinderGeometry(PIN_SHAFT_R * mm, 7.62 * mm, radial_segments=40)
    shaft.translate(0.0, 0.0, -0.19 * mm)
    head = CylinderGeometry(4.6 * mm, 1.4 * mm, radial_segments=40)
    head.translate(0.0, 0.0, 4.2 * mm)
    return flange.merge(shaft).merge(head)


def _a_spring_anchor(delta):
    return _rot2((-40.0, _shank_top_y(-40.0)), delta)


def _a_build_spring(delta, mm):
    bx, by = _a_spring_anchor(delta)
    seat = CylinderGeometry(5.5 * mm, 4.5 * mm, radial_segments=32)
    seat.rotate_x(math.pi / 2.0)
    seat.translate(bx * mm, (by - 0.75) * mm, 0.0)
    coil_r, wire_r, turns = 4.2, 1.05, 6.5
    # coil length tracks the opening so its free end still reaches the moving handle.
    s0, s1 = 1.0, 26.5 * (delta / DELTA_BASE)
    n = int(turns * 16)
    pts = []
    for i in range(n + 1):
        t = i / n
        s = s0 + t * (s1 - s0)
        th = 2.0 * math.pi * turns * t
        pts.append(((bx + coil_r * math.cos(th)) * mm, (by + s) * mm, (coil_r * math.sin(th)) * mm))
    coil = tube_from_spline_points(pts, radius=wire_r * mm, samples_per_segment=2, radial_segments=12, cap_ends=True)
    return seat.merge(coil)


def _a_build_latch(mm):
    pad = cq.Workplane("XY").box(9.0 * mm, 6.7 * mm, 3.5 * mm)
    try:
        pad = pad.edges("|Z").fillet(1.5 * mm)
    except Exception:
        pass
    pad = pad.translate((4.0 * mm, -0.35 * mm, 1.75 * mm))
    hook = cq.Workplane("XY").box(4.0 * mm, 4.5 * mm, 4.5 * mm).translate((3.5 * mm, -5.25 * mm, 0.25 * mm))
    latch = pad.union(hook)
    for cx in (1.8, 4.0, 6.2):
        rib = cq.Workplane("XY").box(0.9 * mm, 6.3 * mm, 0.9 * mm).translate((cx * mm, -0.35 * mm, 3.65 * mm))
        latch = latch.union(rib)
    return latch


def _acq(solid, mesh_name):
    return mesh_from_cadquery(solid, mesh_name, tolerance=MESH_TOL, angular_tolerance=MESH_ANG)


# ---------------------------------------------------------------------------
# A-family assembly (manual_notch_plier / fixed_hole_gauge).
# ---------------------------------------------------------------------------
def _build_A_family(model: ArticulatedObject, r: ResolvedWireStripperConfig, mats) -> None:
    mm = 0.001 * r.mm_scale
    delta, q_close = r.delta, r.q_close
    open_fixed = Origin(rpy=(0.0, 0.0, delta))
    open_moving = Origin(rpy=(0.0, 0.0, -delta))
    kick = HANDLE_KICKS[r.handle_form]
    slotted = r.jaw_feature == "gauge_slot_plate"
    shear = r.jaw_feature == "notch_bolt_shear"

    fixed = model.part("fixed_arm")

    if r.is_gauge:
        specs = _a_awg_specs(r.gauge_count)
        gauge, v0, v1 = _a_build_gauge_plate(specs, mm, slotted)
        removed = v0 - v1
        expected = _a_gauge_expected_volume(specs, mm, slotted)
        fixed.visual(_acq(gauge, "fixed_gauge_plate"), origin=open_fixed, material=mats["steel_body"], name="gauge_plate", material_class_id="metal.paint_coated")
        fixed.visual(_acq(_a_build_gauge_face(specs, mm, slotted), "fixed_gauge_face"), origin=open_fixed, material=mats["steel_bright"], name="gauge_face", material_class_id="metal.stainless_matte")
    else:
        specs = _a_notch_specs(r.gauge_count, x0=28.0 if shear else 26.0)
        if shear:
            cut = list(BOLT_SHEAR_SPECS) + specs
        elif r.jaw_feature == "notch_cutter":
            cut = CRIMP_SPECS + specs
        else:
            cut = list(specs)
        jaw, v0, v1 = _a_build_jaw_plate(cut, mm)
        removed = v0 - v1
        expected = sum(0.5 * math.pi * (rr * mm) ** 2 * (T_STEEL * mm) for _, rr in cut)
        fixed.visual(_acq(jaw, "fixed_jaw_plate"), origin=open_fixed, material=mats["steel_body"], name="jaw_plate", material_class_id="metal.paint_coated")
        fixed.visual(_acq(_a_build_blade_face(cut, mm), "fixed_blade_face"), origin=open_fixed, material=mats["steel_bright"], name="blade_face", material_class_id="metal.stainless_matte")
        fixed.visual(_acq(_a_build_nose_face(mm), "fixed_nose_face"), origin=open_fixed, material=mats["steel_bright"], name="nose_face", material_class_id="metal.stainless_matte")
        if r.jaw_feature == "notch_crimp_die":
            fixed.visual(_acq(_a_build_crimp_die_block(False, mm), "fixed_crimp_die"), origin=open_fixed, material=mats["steel_bright"], name="crimp_die", material_class_id="metal.stainless_matte")
        elif shear:
            fixed.visual(_acq(_a_build_shear_rail(False, mm), "fixed_shear_rail"), origin=open_fixed, material=mats["steel_bright"], name="shear_rail", material_class_id="metal.stainless_matte")

    fixed.visual(_acq(_a_build_fixed_lap(mm), "fixed_lap_plate"), origin=open_fixed, material=mats["steel_body"], name="lap_plate", material_class_id="metal.paint_coated")
    fixed.visual(_acq(_a_poly_solid(_shank_profile_a(), Z_BOT, Z_TOP, mm), "fixed_arm_shank"), origin=open_fixed, material=mats["steel_body"], name="arm_shank", material_class_id="metal.paint_coated")
    grip_y, grip_b = _a_build_grip_pair(False, mm, kick)
    fixed.visual(_acq(grip_y, "fixed_grip_body"), origin=open_fixed, material=mats["grip_main"], name="grip_body", material_class_id="rubber.smooth_plain")
    fixed.visual(_acq(grip_b, "fixed_grip_overmold"), origin=open_fixed, material=mats["grip_dark"], name="grip_overmold", material_class_id="rubber.smooth_plain")
    fixed.visual(_acq(_a_poly_solid(_collar_profile(), -4.0, 4.0, mm), "fixed_grip_collar"), origin=open_fixed, material=mats["grip_main"], name="grip_collar", material_class_id="rubber.smooth_plain")
    fixed.visual(mesh_from_geometry(_a_build_pivot_pin(mm), "pivot_pin"), origin=open_fixed, material=mats["hardware"], name="pivot_pin", material_class_id="metal.blackened_gunmetal")
    fixed.visual(mesh_from_geometry(_a_build_spring(delta, mm), "handle_spring"), material=mats["spring"], name="handle_spring", material_class_id="metal.steel_bare")

    moving = model.part("moving_arm")
    if r.is_gauge:
        moving.visual(_acq(_a_build_pressure_jaw(mm), "moving_pressure_jaw"), origin=open_moving, material=mats["steel_body"], name="pressure_jaw", material_class_id="metal.paint_coated")
        moving.visual(_acq(_a_build_pressure_face(mm), "moving_pressure_face"), origin=open_moving, material=mats["steel_bright"], name="pressure_face", material_class_id="metal.stainless_matte")
    else:
        jaw_m = _a_poly_solid(_a_mirror(_jaw_profile()), Z_BOT, Z_TOP, mm)
        jaw_m = _a_cut_edge_circles(jaw_m, cut, mm)
        moving.visual(_acq(jaw_m, "moving_jaw_plate"), origin=open_moving, material=mats["steel_body"], name="jaw_plate", material_class_id="metal.paint_coated")
        blade_m = _a_poly_solid(_a_mirror(_blade_face_profile()), Z_TOP - 0.2, Z_TOP + 0.5, mm)
        blade_m = _a_cut_edge_circles(blade_m, cut, mm)
        moving.visual(_acq(blade_m, "moving_blade_face"), origin=open_moving, material=mats["steel_bright"], name="blade_face", material_class_id="metal.stainless_matte")
        moving.visual(_acq(_a_poly_solid(_a_mirror(_nose_face_profile()), Z_TOP - 0.2, Z_TOP + 0.5, mm), "moving_nose_face"), origin=open_moving, material=mats["steel_bright"], name="nose_face", material_class_id="metal.stainless_matte")
        if r.jaw_feature == "notch_crimp_die":
            moving.visual(_acq(_a_build_crimp_die_block(True, mm), "moving_crimp_die"), origin=open_moving, material=mats["steel_bright"], name="crimp_die", material_class_id="metal.stainless_matte")
        elif shear:
            moving.visual(_acq(_a_build_shear_rail(True, mm), "moving_shear_rail"), origin=open_moving, material=mats["steel_bright"], name="shear_rail", material_class_id="metal.stainless_matte")

    moving.visual(_acq(_a_build_moving_lap(mm), "moving_lap_plate"), origin=open_moving, material=mats["steel_body"], name="lap_plate", material_class_id="metal.paint_coated")
    moving.visual(_acq(_a_poly_solid(_a_mirror(_shank_profile_a()), Z_BOT, Z_TOP, mm), "moving_arm_shank"), origin=open_moving, material=mats["steel_body"], name="arm_shank", material_class_id="metal.paint_coated")
    grip_ym, grip_bm = _a_build_grip_pair(True, mm, kick)
    moving.visual(_acq(grip_ym, "moving_grip_body"), origin=open_moving, material=mats["grip_main"], name="grip_body", material_class_id="rubber.smooth_plain")
    moving.visual(_acq(grip_bm, "moving_grip_overmold"), origin=open_moving, material=mats["grip_dark"], name="grip_overmold", material_class_id="rubber.smooth_plain")
    moving.visual(_acq(_a_poly_solid(_a_mirror(_collar_profile()), -4.0, 4.0, mm), "moving_grip_collar"), origin=open_moving, material=mats["grip_main"], name="grip_collar", material_class_id="rubber.smooth_plain")
    moving.visual(_acq(_a_build_pivot_plate(mm), "pivot_plate"), origin=open_moving, material=mats["steel_bright"], name="pivot_plate", material_class_id="metal.stainless_matte")

    latch = model.part("lock_latch")
    latch.visual(_acq(_a_build_latch(mm), "latch_body"), material=mats["hardware"], name="latch_body", material_class_id="metal.blackened_gunmetal")

    model.articulation(
        "pivot_squeeze", ArticulationType.REVOLUTE, parent=fixed, child=moving,
        origin=Origin(xyz=(0.0, 0.0, 0.0)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=4.0, lower=0.0, upper=q_close),
    )
    latch_xy = _rot2((-31.0, 5.5), -delta)
    model.articulation(
        "latch_pivot", ArticulationType.REVOLUTE, parent=moving, child=latch,
        origin=Origin(xyz=(latch_xy[0] * mm, latch_xy[1] * mm, Z_TOP * mm), rpy=(0.0, 0.0, -delta)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=3.0, velocity=3.0, lower=0.0, upper=0.45),
    )

    model.meta["jaw_removed_volume"] = removed
    model.meta["jaw_expected_volume"] = expected
    model.meta["gauge_specs"] = specs


# ---------------------------------------------------------------------------
# B-family helpers (port of origin B + pistol_grip / auto_clamp forks).
# ---------------------------------------------------------------------------
def _b_spine(handle_form):
    return _B_HANDLE_SPINES.get(handle_form, _B_HANDLE_SPINES["angled_offset"])


def _b_spine_at(spine, x):
    """Interpolate ``(centre y, plate half width)`` on a handle spine at ``x``."""
    if x >= spine[0][0]:
        return spine[0][1], spine[0][2]
    for (xa, ya, ha), (xb, yb, hb) in zip(spine, spine[1:]):
        if x >= xb:
            t = (x - xa) / (xb - xa)
            return ya + t * (yb - ya), ha + t * (hb - ha)
    return spine[-1][1], spine[-1][2]


def _b_spine_segments(spine, x_start):
    """Spine segments outboard of ``x_start`` as ``(cx, cy, angle, length, half_w)``."""
    y0, h0 = _b_spine_at(spine, x_start)
    nodes = [(x_start, y0, h0)] + [node for node in spine if node[0] < x_start]
    segments = []
    for (xa, ya, ha), (xb, yb, hb) in zip(nodes, nodes[1:]):
        dx, dy = xb - xa, yb - ya
        segments.append((
            (xa + xb) * 0.5, (ya + yb) * 0.5,
            math.atan2(dy, dx), math.hypot(dx, dy), (ha + hb) * 0.5,
        ))
    return segments


def _b_ccw(points):
    area = 0.0
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        area += x0 * y1 - x1 * y0
    return points if area > 0.0 else list(reversed(points))


def _b_mirror(points):
    return [(x, -y) for (x, y) in points]


def _b_circle(radius, n=48):
    return [(radius * math.cos(2.0 * math.pi * i / n), radius * math.sin(2.0 * math.pi * i / n)) for i in range(n)]


def _b_head_half_profile():
    """Head half plate.  Behind the jaw window the half reaches across the
    centreline, so the two stacked halves close the plan-view slot; only the
    jaw window itself stays open as the real wire slot."""
    return [
        (0.011, HEAD_WEB_Y), (HEAD_WINDOW_X0, HEAD_WEB_Y),
        (HEAD_WINDOW_X0, HEAD_FACE_Y), (0.078, HEAD_FACE_Y),
        (0.078, 0.0245), (0.048, 0.029), (0.016, 0.0215), (0.011, 0.0165),
    ]


def _b_shank_profile(spine):
    """Stamped handle shank: plate edges offset from the handle spine, with the
    source cutter serrations on the inner (centreline-facing) edge."""
    inner = [(spine[0][0], spine[0][1] + spine[0][2])]
    y_gap, h_gap = _b_spine_at(spine, -0.016)
    inner.append((-0.016, y_gap + h_gap))
    for i in range(_B_TEETH_N):
        x_dip = _B_TEETH_X0 - i * _B_TEETH_PITCH
        x_ret = _B_TEETH_X0 - 0.0036 - i * _B_TEETH_PITCH
        y_d, h_d = _b_spine_at(spine, x_dip)
        inner.append((x_dip, y_d + h_d - _B_TEETH_DEPTH))
        y_r, h_r = _b_spine_at(spine, x_ret)
        inner.append((x_ret, y_r + h_r))
    x_last = _B_TEETH_X0 - 0.0036 - (_B_TEETH_N - 1) * _B_TEETH_PITCH
    inner.extend((x, y + h) for (x, y, h) in spine if x < x_last)
    outer = [(x, y - h) for (x, y, h) in reversed(spine)]
    return outer + inner


def _b_plate_mesh(spine, mirror):
    head = _b_head_half_profile()
    shank = _b_shank_profile(spine)
    if mirror:
        head = _b_mirror(head)
        shank = _b_mirror(shank)
    zc = LEVER_PLATE_ZC if mirror else BODY_PLATE_ZC
    plate = ExtrudeGeometry(_b_ccw(head), PLATE_T, cap=True, center=True)
    boss_t = PLATE_T + 0.00004
    if mirror:
        boss = ExtrudeWithHolesGeometry(_b_ccw(_b_circle(PIVOT_BOSS_R)), [_b_ccw(_b_circle(PIVOT_BORE_R))], boss_t, cap=True, center=True)
    else:
        boss = CylinderGeometry(PIVOT_BOSS_R, boss_t, radial_segments=48)
    plate.merge(boss)
    plate.merge(ExtrudeGeometry(_b_ccw(shank), PLATE_T, cap=True, center=True))
    plate.translate(0.0, 0.0, zc)
    return plate


def _b_head_cheek_mesh(mirror):
    """Outboard stamped cheek tying pivot, jaw cassette, and arm together."""
    profile = [
        (0.0085, HEAD_WEB_Y),
        (HEAD_WINDOW_X0, HEAD_WEB_Y),
        (HEAD_WINDOW_X0, HEAD_FACE_Y),
        (0.0860, HEAD_FACE_Y),
        (0.0880, 0.0225),
        (0.0780, 0.0285),
        (0.0520, 0.0330),
        (0.0240, 0.0250),
        (0.0085, 0.0160),
    ]
    if mirror:
        profile = _b_mirror(profile)
    cheek = ExtrudeGeometry(_b_ccw(profile), 0.0024, cap=True, center=True)
    cheek.translate(0.0, 0.0, 0.00435 if mirror else -0.00435)
    return cheek


def _b_grip_slab(length, width, thickness, center, angle, radius=0.005):
    slab = ExtrudeGeometry(_b_ccw(rounded_rect_profile(length, width, radius)), thickness, cap=True, center=True)
    slab.rotate_z(angle)
    slab.translate(*center)
    return slab


def _b_spring_mesh():
    x0, x1 = 0.016, 0.0225
    turns = 4.0
    n = 40
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = 2.0 * math.pi * turns * t
        pts.append((x0 + (x1 - x0) * t, 0.0105 + 0.0022 * math.cos(ang), 0.0045 + 0.0022 * math.sin(ang)))
    return tube_from_spline_points(pts, radius=0.0008, samples_per_segment=2, radial_segments=8, cap_ends=True)


def _b_die_specs(n):
    """N graduated stripping dies on the jaw face: ``(x centre, half width, depth)``.

    Half width is the conductor half-diameter the die is cut for, so a closed
    pair forms a graduated ascending opening — the gauge station that makes the
    auto family read as a STRIPPER rather than a pair of smooth clamp blocks.
    """
    x0, x1 = 0.0505, 0.0715
    w0, w1 = 0.00050, 0.00145
    specs = []
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0.0
        w = w0 + t * (w1 - w0)
        x = x0 + t * (x1 - x0) if n > 1 else (x0 + x1) * 0.5
        specs.append((round(x, 5), round(w, 5), round(1.75 * w, 5)))
    return specs


def _b_die_pad_profile(specs, sign, y_face, y_back, x_lo, x_hi, square):
    """Jaw pad whose facing edge carries the graduated dies.  ``square`` swaps
    the V dies for the stepped square-shoulder pockets of a die cassette."""
    pts = [(x_lo, y_back * sign), (x_hi, y_back * sign), (x_hi, y_face * sign)]
    for (cx, w, d) in reversed(specs):
        if square:
            pts.append((cx + w, y_face * sign))
            pts.append((cx + w, (y_face + d) * sign))
            pts.append((cx - w, (y_face + d) * sign))
            pts.append((cx - w, y_face * sign))
        else:
            pts.append((cx + w, y_face * sign))
            pts.append((cx, (y_face + d) * sign))
            pts.append((cx - w, y_face * sign))
    pts.append((x_lo, y_face * sign))
    return pts


def _b_polygon_area(points):
    total = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
        total += x0 * y1 - x1 * y0
    return abs(total) * 0.5


def _b_die_pad_mesh(specs, sign, square):
    """Die pad solid.  A cassette (``square``) stands proud of the jaw block;
    an integral pad (``V``) is flush with it.  Returns the mesh plus the plan
    area the dies actually removed, so an author test can prove the station is
    cut material rather than a painted-on face."""
    thickness = 0.0085 if square else 0.0060
    y_face, y_back, x_lo, x_hi = 0.0008, 0.0052, 0.0495, 0.0735
    profile = _b_die_pad_profile(specs, sign, y_face, y_back, x_lo, x_hi, square)
    blank = (x_hi - x_lo) * (y_back - y_face)
    removed = blank - _b_polygon_area(profile)
    pad = ExtrudeGeometry(_b_ccw(profile), thickness, cap=True, center=True)
    pad.translate(0.0, 0.0, 0.0090)
    return pad, removed * thickness


def _b_emit_grips(part, side, handle_form, mats):
    """Overmould emitted from the same spine as the steel, so every segment of
    rubber sits centred on its own shank instead of floating outboard of it."""
    spine = _b_spine(handle_form)
    style = _B_GRIP_STYLES[handle_form]
    is_body = side == "body"
    sy = 1.0 if is_body else -1.0  # spines are authored for the body (-Y) arm
    za = -1.0 if is_body else 1.0
    grip_t = style["thickness"]
    segments = _b_spine_segments(spine, spine[1][0])

    long_i = max(range(len(segments)), key=lambda i: segments[i][3])
    for i, (cx, cy, ang, seg_len, half_w) in enumerate(segments):
        width = 2.0 * half_w + style["proud"]
        name = "grip_body" if i == long_i else f"grip_neck_{i}"
        part.visual(
            mesh_from_geometry(
                _b_grip_slab(seg_len + style["overlap"], width, grip_t,
                             (cx, sy * cy, za * 0.0016), sy * ang,
                             radius=min(0.008, 0.45 * width, 0.45 * (seg_len + style["overlap"]))),
                f"{side}_{name}"),
            material=mats["grip_main"], name=name, material_class_id="rubber.smooth_plain")

    lcx, lcy, lang, llen, lhw = segments[long_i]
    inlay_w = min(0.0085, 2.0 * lhw - 0.006)
    part.visual(
        mesh_from_geometry(
            _b_grip_slab(0.62 * llen, inlay_w, 0.0022,
                         (lcx, sy * lcy, za * (0.0016 + grip_t * 0.5 - 0.0004)), sy * lang,
                         radius=0.4 * inlay_w),
            f"{side}_grip_inlay"),
        material=mats["grip_dark"], name="grip_inlay", material_class_id="rubber.smooth_plain")

    tx, ty, thw = spine[-1]
    ux, uy = math.cos(lang), math.sin(lang)
    if ux > 0.0:  # keep the unit vector pointing outboard (-X)
        ux, uy = -ux, -uy
    if style["palm"] > 0.0:
        part.visual(
            mesh_from_geometry(
                _b_grip_slab(0.036, 2.0 * thw + style["palm"], grip_t + 0.0018,
                             (tx - 0.020 * ux, sy * (ty - 0.020 * uy), za * 0.0016), sy * lang,
                             radius=0.010),
                f"{side}_palm_swell"),
            material=mats["grip_main"], name="palm_swell", material_class_id="rubber.smooth_plain")
    part.visual(
        mesh_from_geometry(
            _b_grip_slab(style["cap_len"], 2.0 * thw + style["cap_proud"], grip_t + 0.0014,
                         (tx - 0.002 * ux, sy * (ty - 0.002 * uy), za * 0.0016), sy * lang,
                         radius=0.006),
            f"{side}_grip_tip"),
        material=mats["grip_dark"], name="grip_tip", material_class_id="rubber.smooth_plain")


def _b_emit_gripping_jaw(part, die_specs, cassette, mats, *, offset, pad_mat):
    """Fixed gripping jaw block, die pad and brass tension screw.

    ``offset`` is subtracted from every anchor so the same jaw can be emitted
    either inside the body part or on the ``gripping_jaw`` clamp part, whose
    frame is the ``clamp_pinch`` pin.
    """
    ox, oy, oz = offset
    jaw = BoxGeometry((0.030, 0.0205, 0.0100)).translate(0.061 - ox, 0.01375 - oy, 0.0090 - oz)
    part.visual(mesh_from_geometry(jaw, "gripping_jaw"), material=mats["jaw"], name="gripping_jaw", material_class_id="metal.blackened_gunmetal")
    pad, removed = _b_die_pad_mesh(die_specs, 1.0, cassette)
    pad.translate(-ox, -oy, -oz)
    part.visual(mesh_from_geometry(pad, "gripping_jaw_pad"), material=pad_mat, name="gripping_jaw_pad", material_class_id="metal.stainless_matte")
    if cassette:
        for i, sx in enumerate((0.0535, 0.0685)):
            part.visual(Cylinder(radius=0.0026, length=0.0022),
                        origin=Origin(xyz=(sx - ox, 0.0088 - oy, 0.0142 - oz)),
                        material=mats["hardware"], name=f"die_cap_screw_{i}", material_class_id="metal.blackened_gunmetal")
    part.visual(Cylinder(radius=0.0055, length=0.0050),
                origin=Origin(xyz=(0.052 - ox, 0.0145 - oy, 0.0160 - oz)),
                material=mats["brass"], name="tension_screw_head", material_class_id="metal.brass_polished")
    part.visual(Cylinder(radius=0.0038, length=0.0025),
                origin=Origin(xyz=(0.052 - ox, 0.0145 - oy, 0.01975 - oz)),
                material=mats["brass"], name="tension_screw_tip", material_class_id="metal.brass_polished")
    return removed


# ---------------------------------------------------------------------------
# B-family assembly (auto_selfadjust).
# ---------------------------------------------------------------------------
def _build_B_family(model: ArticulatedObject, r: ResolvedWireStripperConfig, mats) -> None:
    squeeze = r.squeeze_max
    real_clamp = r.auto_clamp_dof == "real_clamp_joint"
    cassette = r.jaw_feature == "clamp_vgroove_die"
    spine = _b_spine(r.handle_form)
    die_specs = _b_die_specs(r.gauge_count)
    # Hardened die faces are bright steel on both jaw candidates.  Leaving the
    # V dies in the dark spring grey of the source pad hid the whole station
    # against the black jaw block, which is what made the head read as two
    # featureless clamp bricks in the first place.
    pad_mat = mats["steel_bright"]
    rivet_y, _ = _b_spine_at(spine, -0.0225)

    body = model.part("fixed_arm")
    body.visual(mesh_from_geometry(_b_plate_mesh(spine, False), "body_plate"), material=mats["steel_body"], name="body_plate", material_class_id="metal.paint_coated")
    body.visual(mesh_from_geometry(_b_head_cheek_mesh(False), "body_head_cheek"), material=mats["steel_body"], name="head_cheek", material_class_id="metal.paint_coated")

    # outboard guide riser (carries / straddles the moving lever plate)
    riser = BoxGeometry((0.030, 0.009, 0.0051)).translate(0.061, 0.0195, 0.00195)
    body.visual(mesh_from_geometry(riser, "gripping_jaw_riser"), material=mats["jaw"], name="gripping_jaw_riser", material_class_id="metal.blackened_gunmetal")

    if not real_clamp:
        die_removed = _b_emit_gripping_jaw(body, die_specs, cassette, mats, offset=(0.0, 0.0, 0.0), pad_mat=pad_mat)

    rail = BoxGeometry((0.024, 0.004, 0.0032)).translate(0.032, 0.0105, 0.0010)
    body.visual(mesh_from_geometry(rail, "slider_rail"), material=mats["spring"], name="slider_rail", material_class_id="metal.steel_bare")
    body.visual(Cylinder(radius=0.0015, length=0.0081), origin=Origin(xyz=(0.0155, 0.0115, 0.00345)), material=mats["steel_bright"], name="spring_post", material_class_id="metal.stainless_matte")
    body.visual(mesh_from_geometry(_b_spring_mesh(), "stop_spring"), material=mats["spring"], name="stop_spring", material_class_id="metal.steel_bare")
    body.visual(Cylinder(radius=PIVOT_SHAFT_R, length=0.0120), origin=Origin(xyz=(0.0, 0.0, 0.0)), material=mats["steel_bright"], name="pivot_shaft", material_class_id="metal.chrome_polished")
    body.visual(Cylinder(radius=PIVOT_CAP_R, length=0.0030), origin=Origin(xyz=(0.0, 0.0, 0.0053)), material=mats["steel_bright"], name="pivot_button_cap", material_class_id="metal.chrome_polished")
    body.visual(Cylinder(radius=PIVOT_CAP_R, length=0.0030), origin=Origin(xyz=(0.0, 0.0, -0.0053)), material=mats["steel_bright"], name="pivot_rear_cap", material_class_id="metal.chrome_polished")
    body.visual(Cylinder(radius=0.0025, length=0.0016), origin=Origin(xyz=(-0.0225, rivet_y, 0.0002)), material=mats["steel_bright"], name="shank_rivet", material_class_id="metal.chrome_polished")
    _b_emit_grips(body, "body", r.handle_form, mats)

    lever = model.part("moving_arm")
    lever.visual(mesh_from_geometry(_b_plate_mesh(spine, True), "lever_plate"), material=mats["steel_body"], name="lever_plate", material_class_id="metal.paint_coated")
    lever.visual(mesh_from_geometry(_b_head_cheek_mesh(True), "lever_head_cheek"), material=mats["steel_body"], name="head_cheek", material_class_id="metal.paint_coated")
    s_jaw = BoxGeometry((0.030, 0.0205, 0.0112)).translate(0.061, -0.013750, 0.0084)
    s_jaw.rotate_z(-squeeze)
    lever.visual(mesh_from_geometry(s_jaw, "stripping_jaw"), material=mats["jaw"], name="stripping_jaw", material_class_id="metal.blackened_gunmetal")
    s_pad, _ = _b_die_pad_mesh(die_specs, -1.0, cassette)
    s_pad.rotate_z(-squeeze)
    lever.visual(mesh_from_geometry(s_pad, "stripping_jaw_pad"), material=pad_mat, name="stripping_jaw_pad", material_class_id="metal.stainless_matte")
    if cassette:
        for i, sx in enumerate((0.0535, 0.0685)):
            screw = Cylinder(radius=0.0026, length=0.0022)
            lever.visual(screw, origin=Origin(xyz=(sx, -0.0088, 0.0142)), material=mats["hardware"], name=f"die_cap_screw_{i}", material_class_id="metal.blackened_gunmetal")
    for i, (rx, ry) in enumerate([(0.024, -0.019), (0.032, -0.020)]):
        lever.visual(Cylinder(radius=0.0035, length=0.0022), origin=Origin(xyz=(rx, ry, 0.0029)), material=mats["steel_bright"], name=f"head_rivet_{i}", material_class_id="metal.chrome_polished")
    lever.visual(Cylinder(radius=0.0025, length=0.0016), origin=Origin(xyz=(-0.0225, -rivet_y, 0.0036)), material=mats["steel_bright"], name="shank_rivet", material_class_id="metal.chrome_polished")
    _b_emit_grips(lever, "lever", r.handle_form, mats)

    slider = model.part("wire_stop_slider")
    s_block = BoxGeometry((0.012, 0.012, 0.0062)).translate(0.0, 0.0, 0.0056)
    slider.visual(mesh_from_geometry(s_block, "slider_body"), material=mats["slider"], name="slider_body", material_class_id="plastic.opaque_glossy_molded")
    s_tab = BoxGeometry((0.003, 0.012, 0.0055)).translate(0.0045, 0.0, 0.01075)
    slider.visual(mesh_from_geometry(s_tab, "slider_tab"), material=mats["slider"], name="slider_tab", material_class_id="plastic.opaque_glossy_molded")
    for sign, tag in ((-1.0, "inner"), (1.0, "outer")):
        skirt = BoxGeometry((0.012, 0.0036, 0.0026)).translate(0.0, sign * 0.0042, 0.0018)
        slider.visual(mesh_from_geometry(skirt, f"slider_skirt_{tag}"), material=mats["slider"], name=f"slider_skirt_{tag}", material_class_id="plastic.opaque_glossy_molded")

    if real_clamp:
        pin = (0.046, 0.019, 0.004)
        gj = model.part("gripping_jaw")
        die_removed = _b_emit_gripping_jaw(gj, die_specs, cassette, mats, offset=pin, pad_mat=pad_mat)

    model.articulation(
        "arm_pivot", ArticulationType.REVOLUTE, parent=body, child=lever,
        origin=Origin(xyz=(0.0, 0.0, 0.0)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=3.0, lower=0.0, upper=squeeze),
    )
    model.articulation(
        "wire_stop_slide", ArticulationType.PRISMATIC, parent=body, child=slider,
        origin=Origin(xyz=(0.030, 0.0105, 0.0)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=0.05, lower=0.0, upper=SLIDE_MAX),
    )
    model.meta["gauge_specs"] = die_specs
    model.meta["die_removed_volume"] = die_removed
    model.meta["die_expected_volume"] = sum(
        w * d for (_, w, d) in die_specs) * (0.0085 if cassette else 0.0060) * (2.0 if cassette else 1.0)
    if real_clamp:
        model.articulation(
            "clamp_pinch", ArticulationType.REVOLUTE, parent=body, child=gj,
            origin=Origin(xyz=pin), axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=30.0, velocity=2.0, lower=0.0, upper=CLAMP_ANGLE),
            mimic=Mimic(joint="arm_pivot", multiplier=CLAMP_ANGLE / squeeze, offset=0.0),
        )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_wire_stripper(config: WireStripperConfig | None = None, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {key: model.material(f"ws_{key}_{r.palette_style}", rgba=rgba) for key, rgba in palette.items()}

    if r.is_auto:
        _build_B_family(model, r, mats)
    else:
        _build_A_family(model, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_wire_stripper(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_wire_stripper(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _aabb_center(aabb):
    return tuple((aabb[0][i] + aabb[1][i]) * 0.5 for i in range(3))


def _run_A_tests(object_model, r, ctx):
    fixed = object_model.get_part("fixed_arm")
    moving = object_model.get_part("moving_arm")
    latch = object_model.get_part("lock_latch")
    squeeze = object_model.get_articulation("pivot_squeeze")
    latch_joint = object_model.get_articulation("latch_pivot")

    # Intentional captured-pin / spring / latch overlaps (rest pose is clean).
    ctx.allow_overlap(fixed, moving, elem_a="handle_spring", elem_b="arm_shank",
                      reason="Rigid coil-spring proxy is compressed by the moving handle when squeezed.")
    ctx.allow_overlap(fixed, moving, elem_a="handle_spring", elem_b="grip_body",
                      reason="Spring free end meets the moving grip when the handles are squeezed shut.")
    ctx.allow_overlap(latch, fixed, elem_a="latch_body", elem_b="arm_shank",
                      reason="Lock latch hook engages the opposite handle when flipped while closed.")
    ctx.allow_overlap(fixed, moving, elem_a="pivot_pin", elem_b="lap_plate",
                      reason="Captured pivot pin: axisymmetric bushing fit inside the moving lap bore.")

    aabbs = [ctx.part_world_aabb(p) for p in (fixed, moving, latch)]
    lo = [min(a[0][i] for a in aabbs) for i in range(3)]
    hi = [max(a[1][i] for a in aabbs) for i in range(3)]
    length, width, thick = hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]
    ctx.check("overall length plausible", 0.160 <= length <= 0.235, details=f"length={length:.4f}")
    ctx.check("open-tool width plausible", 0.060 <= width <= 0.150, details=f"width={width:.4f}")
    ctx.check("tool thickness plausible", 0.010 <= thick <= 0.024, details=f"thick={thick:.4f}")

    ctx.expect_contact(fixed, moving, contact_tol=8e-4, name="arms mate at the lap joint pivot")
    ctx.expect_overlap(fixed, moving, axes="xy", elem_a="pivot_pin", elem_b="lap_plate", min_overlap=0.003,
                       name="pivot pin passes through the moving lap plate")

    lim = squeeze.motion_limits
    ctx.check("squeeze REVOLUTE +Z with range",
              squeeze.articulation_type == ArticulationType.REVOLUTE
              and tuple(round(abs(c), 3) for c in squeeze.axis) == (0.0, 0.0, 1.0)
              and lim is not None and abs(lim.lower) < 1e-9 and lim.upper > lim.lower,
              details=f"type={squeeze.articulation_type} axis={tuple(round(c,3) for c in squeeze.axis)}")

    if r.is_gauge:
        open_a, open_b = "gauge_plate", "pressure_jaw"
    else:
        open_a = open_b = "nose_face"
    ctx.expect_gap(fixed, moving, axis="y", positive_elem=open_a, negative_elem=open_b,
                   min_gap=0.004, max_gap=0.06, name="jaws are open at rest")

    rest_center = _aabb_center(ctx.part_world_aabb(moving))
    with ctx.pose({squeeze: r.q_close}):
        ctx.expect_contact(fixed, moving, elem_a=open_a, elem_b=open_b, contact_tol=0.004,
                           name="jaws nearly meet when squeezed")
        closed_center = _aabb_center(ctx.part_world_aabb(moving))
    disp = math.dist(rest_center, closed_center)
    ctx.check("squeeze visibly swings the moving arm", disp >= 0.004, details=f"disp={disp:.4f}")

    specs = object_model.meta.get("gauge_specs", [])
    ctx.check("gauge stations ascending radius",
              len(specs) == r.gauge_count and all(specs[i][1] < specs[i + 1][1] for i in range(len(specs) - 1)),
              details=f"radii={[rr for _, rr in specs]}")
    removed = object_model.meta.get("jaw_removed_volume", 0.0)
    expected = object_model.meta.get("jaw_expected_volume", 0.0)
    ctx.check("gauge/notch cuts removed real material",
              0.55 * expected <= removed <= 1.45 * expected,
              details=f"removed={removed:.3e} expected~{expected:.3e}")

    ctx.expect_contact(fixed, moving, elem_a="handle_spring", contact_tol=0.008,
                       name="spring free end reaches near the moving handle")

    ctx.expect_contact(latch, moving, contact_tol=2e-3, name="latch seats on the moving handle face")
    latch_rest = _aabb_center(ctx.part_world_aabb(latch))
    with ctx.pose({latch_joint: 0.45}):
        latch_flip = _aabb_center(ctx.part_world_aabb(latch))
    ctx.check("lock latch flips on its pivot", math.dist(latch_rest, latch_flip) >= 0.0010,
              details=f"latch disp={math.dist(latch_rest, latch_flip):.5f}")

    if r.jaw_feature == "notch_crimp_die":
        ctx.check("crimp-die station present on both arms",
                  fixed.get_visual("crimp_die") is not None and moving.get_visual("crimp_die") is not None,
                  details="dedicated crimp_die visuals expected")
    if r.jaw_feature == "notch_bolt_shear":
        ctx.check("bolt-shear rail present on both arms",
                  fixed.get_visual("shear_rail") is not None and moving.get_visual("shear_rail") is not None,
                  details="dedicated shear_rail visuals expected")
    if r.is_gauge:
        gauge_aabb = ctx.part_element_world_aabb(fixed, elem="gauge_plate")
        ctx.check("gauge stations are legible on the plate",
                  specs and specs[-1][1] >= 2.0 and gauge_aabb is not None,
                  details=f"largest station radius={specs[-1][1] if specs else 0.0} mm")


def _run_B_tests(object_model, r, ctx):
    body = object_model.get_part("fixed_arm")
    lever = object_model.get_part("moving_arm")
    slider = object_model.get_part("wire_stop_slider")
    pivot = object_model.get_articulation("arm_pivot")
    slide = object_model.get_articulation("wire_stop_slide")
    real_clamp = r.auto_clamp_dof == "real_clamp_joint"
    grip_jaw_part = object_model.get_part("gripping_jaw") if real_clamp else body

    ctx.allow_overlap(slider, body, elem_a="slider_body", elem_b="slider_rail",
                      reason="Slider seats 0.1mm into the rail top (captured sliding fit of the wire-length stop).")
    if real_clamp:
        ctx.allow_overlap(grip_jaw_part, body, elem_a="gripping_jaw", elem_b="gripping_jaw_riser",
                          reason="Gripping jaw seats into the riser top (captured revolute guide fit of the self-adjusting clamp).")

    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for part in object_model.parts:
        aabb = ctx.part_world_aabb(part)
        if aabb is None:
            continue
        for k in range(3):
            lo[k] = min(lo[k], aabb[0][k])
            hi[k] = max(hi[k], aabb[1][k])
    ext = [hi[k] - lo[k] for k in range(3)]
    ctx.check("tool envelope plausible for a hand stripper",
              0.19 <= ext[0] <= 0.24 and 0.06 <= ext[1] <= 0.19 and 0.018 <= ext[2] <= 0.04,
              details=f"extents={ext}")

    ctx.check("arm_pivot REVOLUTE +Z with range",
              pivot.articulation_type == ArticulationType.REVOLUTE
              and tuple(round(abs(c), 3) for c in pivot.axis) == (0.0, 0.0, 1.0)
              and pivot.motion_limits is not None and pivot.motion_limits.upper > pivot.motion_limits.lower,
              details=f"type={pivot.articulation_type}")
    ctx.check("wire_stop_slide PRISMATIC +X",
              slide.articulation_type == ArticulationType.PRISMATIC
              and tuple(round(abs(c), 3) for c in slide.axis) == (1.0, 0.0, 0.0),
              details=f"type={slide.articulation_type} axis={tuple(round(c,3) for c in slide.axis)}")

    # Measure the swing on a real material point at the handle tip.  The
    # whole-part AABB centre is a poor proxy: a long arm lying nearly along X
    # barely moves its bounding box under a 0.09 rad rotation even though the
    # tip travels 13 mm, so the old centre metric read as a frozen joint.
    rest_tip = _aabb_center(ctx.part_element_world_aabb(lever, elem="grip_tip"))
    rest_grip = ctx.part_element_world_aabb(lever, elem="grip_body")
    rest_grip_cy = (rest_grip[0][1] + rest_grip[1][1]) * 0.5

    ctx.expect_gap(grip_jaw_part, lever, axis="y", positive_elem="gripping_jaw_pad", negative_elem="stripping_jaw_pad",
                   min_gap=0.003, name="jaw wire slot is open at rest")
    with ctx.pose({pivot: r.squeeze_max}):
        sq_tip = _aabb_center(ctx.part_element_world_aabb(lever, elem="grip_tip"))
        tip_travel = math.dist(rest_tip, sq_tip)
        ctx.check("squeezing swings the lever handle tip", tip_travel >= 0.008,
                  details=f"tip_travel={tip_travel:.5f}")
        sq_grip = ctx.part_element_world_aabb(lever, elem="grip_body")
        sq_grip_cy = (sq_grip[0][1] + sq_grip[1][1]) * 0.5
        ctx.check("squeeze swings the lever grip toward the body grip", rest_grip_cy - sq_grip_cy >= 0.005,
                  details=f"rest_cy={rest_grip_cy:.5f} sq_cy={sq_grip_cy:.5f}")
        ctx.expect_gap(grip_jaw_part, lever, axis="y", positive_elem="gripping_jaw_pad", negative_elem="stripping_jaw_pad",
                       min_gap=-0.001 if real_clamp else 0.0005, max_gap=0.003,
                       name="squeeze closes the wire slot without jaw contact")

    screw = ctx.part_element_world_aabb(grip_jaw_part, elem="tension_screw_head")
    ctx.check("brass tension screw sits proud on the head",
              screw is not None and screw[1][2] >= 0.018 and 0.04 <= (screw[0][0] + screw[1][0]) * 0.5 <= 0.08,
              details=f"screw aabb={screw}")

    # The overmould must sit ON its shank.  The previous build placed it from an
    # independent rake and it drifted ~8 mm outboard of the steel, so each handle
    # read as two prongs.  Assert the shank centreline runs down the middle of
    # the grip rather than trusting the two angles to agree.
    spine = _b_spine(r.handle_form)
    for arm, sign, label in ((body, 1.0, "body"), (lever, -1.0, "lever")):
        gb = ctx.part_element_world_aabb(arm, elem="grip_body")
        gx = (gb[0][0] + gb[1][0]) * 0.5
        gcy = (gb[0][1] + gb[1][1]) * 0.5
        half = (gb[1][1] - gb[0][1]) * 0.5
        shank_y = sign * _b_spine_at(spine, gx)[0]
        ctx.check(f"{label} overmould stays centred on its shank",
                  half > 0.0 and abs(gcy - shank_y) <= 0.30 * half,
                  details=f"grip_cy={gcy:.5f} shank_cy={shank_y:.5f} half={half:.5f}")
    root_elem = "grip_neck_0" if len(spine) > 3 else "grip_body"
    ctx.expect_gap(lever, body, axis="y", positive_elem=root_elem, negative_elem=root_elem,
                   min_gap=GRIP_ROOT_CLEARANCE,
                   name="the two overmoulds clear each other at the grip root")
    specs = object_model.meta.get("gauge_specs", [])
    ctx.check("stripping dies ascending and counted",
              len(specs) == r.gauge_count
              and all(specs[i][1] < specs[i + 1][1] for i in range(len(specs) - 1)),
              details=f"widths={[w for _, w, _ in specs]}")
    die_removed = object_model.meta.get("die_removed_volume", 0.0)
    die_expected = object_model.meta.get("die_expected_volume", 0.0)
    ctx.check("die station is cut into the jaw pads, not painted on",
              die_expected > 0.0 and 0.6 * die_expected <= die_removed <= 1.4 * die_expected,
              details=f"removed={die_removed:.3e} expected~{die_expected:.3e}")
    for elem, owner in (("gripping_jaw_pad", grip_jaw_part), ("stripping_jaw_pad", lever)):
        pad = ctx.part_element_world_aabb(owner, elem=elem)
        ctx.check(f"{elem} spans the die station",
                  pad is not None and (pad[1][0] - pad[0][0]) >= 0.020,
                  details=f"pad aabb={pad}")
    if r.jaw_feature == "clamp_vgroove_die":
        ctx.check("die cassette is retained by cap screws",
                  grip_jaw_part.get_visual("die_cap_screw_0") is not None
                  and lever.get_visual("die_cap_screw_1") is not None,
                  details="dedicated die_cap_screw visuals expected")

    ctx.expect_contact(slider, body, elem_a="slider_body", elem_b="slider_rail", name="slider rides on the rail")
    rest_s = ctx.part_world_aabb(slider)
    rest_sx = (rest_s[0][0] + rest_s[1][0]) * 0.5
    ctx.expect_overlap(slider, body, axes="x", elem_b="slider_rail", min_overlap=0.005, name="slider engages the rail at rest")
    with ctx.pose({slide: SLIDE_MAX}):
        out_s = ctx.part_world_aabb(slider)
        out_sx = (out_s[0][0] + out_s[1][0]) * 0.5
        ctx.check("wire stop slider slides toward the jaws", out_sx - rest_sx >= 0.006,
                  details=f"rest_sx={rest_sx:.5f} out_sx={out_sx:.5f}")
        ctx.expect_overlap(slider, body, axes="x", elem_b="slider_rail", min_overlap=0.005, name="slider stays engaged at full travel")
        ctx.expect_gap(grip_jaw_part, slider, axis="x", positive_elem="gripping_jaw", min_gap=0.0005,
                       name="slider stops short of the gripping jaw")
    ctx.expect_gap(slider, body, axis="x", negative_elem="stop_spring", min_gap=0.0, max_gap=0.003,
                   name="coil spring free end reaches the slider tail")

    if real_clamp:
        clamp = object_model.get_articulation("clamp_pinch")
        ctx.check("clamp_pinch is a REVOLUTE mimic DOF",
                  clamp.articulation_type == ArticulationType.REVOLUTE and clamp.motion_limits is not None
                  and clamp.motion_limits.upper > clamp.motion_limits.lower,
                  details=f"type={clamp.articulation_type}")
        rest_pad = ctx.part_element_world_aabb(grip_jaw_part, elem="gripping_jaw_pad")
        rest_pad_cy = (rest_pad[0][1] + rest_pad[1][1]) * 0.5
        with ctx.pose({pivot: r.squeeze_max}):
            sq_pad = ctx.part_element_world_aabb(grip_jaw_part, elem="gripping_jaw_pad")
            sq_pad_cy = (sq_pad[0][1] + sq_pad[1][1]) * 0.5
            ctx.check("squeeze drives clamp_pinch to close the gripping jaw", rest_pad_cy - sq_pad_cy >= 0.0005,
                      details=f"rest_cy={rest_pad_cy:.5f} sq_cy={sq_pad_cy:.5f}")


def run_wire_stripper_tests(object_model: ArticulatedObject, config: WireStripperConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    if r.is_auto:
        _run_B_tests(object_model, r, ctx)
    else:
        _run_A_tests(object_model, r, ctx)

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    ctx.check("slot_choices recorded",
              tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
              details=str(object_model.meta.get("slot_choices")))
    return ctx.report()


__all__ = (
    "WireStripperConfig",
    "ResolvedWireStripperConfig",
    "build_wire_stripper",
    "build_seeded_wire_stripper",
    "config_from_seed",
    "resolve_config",
    "run_wire_stripper_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
