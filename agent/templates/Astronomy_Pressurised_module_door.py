# SPDX-License-Identifier: Apache-2.0

"""Astronomy / Pressurised module door — modular procedural template.

A pressurised-module EVA hatch / airlock door: a white cylindrical
pressurised-module ``airlock_shell`` (hull tube + end plate + raised hatch
collar + tan pressure seal + bolt ring + latch strikes + EVA handrails) closed
by a moving hatch, plus an inner locking handwheel, and optionally a radial
debris-cover shutter ring. Appendages parent directly to the shell
(parallel-children pattern):

  * closure  — one swing lid (flat, reinforced, or convex dome) on a REVOLUTE
               hinge, or two bi-parting half-leaves on twin REVOLUTE hinges;
               carries the inner REVOLUTE locking control.
  * debris covers — 0/6/8/12 independently-hinged panels around the collar.

Slot graph (pattern = mixed: root shell/aperture + parallel-children closure +
1 multiplicity axis ``cover_count`` + 3 decoration-count axes):

    shell_aperture (root; round / square / hex / octagonal aperture)
        |-- closure  (single_swing_lid / domed_swing_lid / double_leaf
        |             / reinforced_swing_lid) --> locking_control
        `-- debris_cover_i  (x cover_count)

Adapted per AUTHORING.md A/B from the confirmed 5-star pool
(spec: specs_modular_v1/Astronomy_Pressurised_module_door.md). Sources:

  S1  origin rec_a-round-eva-...d440cc9f  — round shell, single swing lid,
      handwheel, dogs/strikes/bolts, all test semantics.
  S2  bolt_ring_count   — bolt_count multiplicity.
  S3  latch_dog_count   — dog_count multiplicity (dogs + strikes paired).
  S4  spoke_count       — handwheel spoke_count multiplicity.
  S5  dome_lid          — convex spherical-cap dome lid (Volumetric Envelope).
  S6  square_hatch      — rounded-square aperture form (Planar Boundary).
  S7  double_leaf       — two bi-parting half-disc leaves (skeleton).
  S9  radial_covers     — radial debris-cover shutter ring (multiplicity).
  D1  octagonal aperture — local planar-boundary extension of the polygonal
      collar/opening family.
  D2  reinforced lid    — local structural extension of the source-backed flat
      swing lid with a raised stiffening web.
  D3  locking controls  — source handwheel plus crossbar and tri-grip controls
      sharing the same hub axis and locking function.

Coordinate frame: hull axis = +Z, hatch opening on top (+Z). The hull is
circular in every candidate; only the aperture/collar/seal/lid cross-section
prototype changes. All mirrored pieces straddle x=0 / y=0.
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
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


ApertureForm = Literal[
    "round_aperture",
    "square_aperture",
    "hex_aperture",
    "octagonal_aperture",
]
ClosureModule = Literal[
    "single_swing_lid",
    "reinforced_swing_lid",
    "domed_swing_lid",
    "double_leaf",
]
LockingControl = Literal["rim_handwheel", "crossbar_lock", "tri_grip_wheel"]
DoorPalette = Literal[
    "nasa_white",
    "iss_module",
    "soyuz_green",
    "bare_alloy",
    "charcoal_service",
    "copper_thermal",
]

_ROUND_ONLY_CLOSURES = ("domed_swing_lid", "double_leaf")


# --------------------------------------------------------------------------- #
# Canonical dimensions (origin rec_a-round-eva-...d440cc9f)
# --------------------------------------------------------------------------- #

BASE_HULL_R = 1.00       # airlock hull outer radius
HULL_WALL = 0.12
HULL_TOP = 1.00          # hull tube top z
PLATE_TOP = 1.06         # end plate top z
COLLAR_TOP = 1.24        # collar top z
SEAL_TOP = 1.245         # tan seal top face z

BASE_COLLAR_RO = 0.60    # hatch collar outer radius / lid radius
BASE_OPENING_RI = 0.50   # hatch opening radius

HINGE_Z = 1.28           # swing hinge pin height


# --------------------------------------------------------------------------- #
# Palettes (>=6 colorways; token set shared so every .visual resolves)
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "nasa_white": {
        "hull_white": (0.88, 0.88, 0.85, 1.0),
        "plate_grey": (0.74, 0.74, 0.72, 1.0),
        "seal_tan": (0.78, 0.64, 0.42, 1.0),
        "lid_tan": (0.76, 0.68, 0.52, 1.0),
        "metal_grey": (0.55, 0.56, 0.58, 1.0),
        "silver": (0.75, 0.76, 0.78, 1.0),
        "rail_gold": (0.82, 0.70, 0.42, 1.0),
        "hardware": (0.30, 0.30, 0.32, 1.0),
        "cover_white": (0.84, 0.84, 0.82, 1.0),
    },
    "iss_module": {
        "hull_white": (0.80, 0.81, 0.83, 1.0),
        "plate_grey": (0.62, 0.64, 0.68, 1.0),
        "seal_tan": (0.70, 0.58, 0.40, 1.0),
        "lid_tan": (0.68, 0.62, 0.50, 1.0),
        "metal_grey": (0.48, 0.50, 0.54, 1.0),
        "silver": (0.72, 0.74, 0.78, 1.0),
        "rail_gold": (0.86, 0.74, 0.36, 1.0),
        "hardware": (0.22, 0.23, 0.26, 1.0),
        "cover_white": (0.78, 0.79, 0.81, 1.0),
    },
    "soyuz_green": {
        "hull_white": (0.42, 0.48, 0.40, 1.0),
        "plate_grey": (0.34, 0.38, 0.33, 1.0),
        "seal_tan": (0.66, 0.55, 0.36, 1.0),
        "lid_tan": (0.52, 0.52, 0.40, 1.0),
        "metal_grey": (0.40, 0.42, 0.40, 1.0),
        "silver": (0.68, 0.70, 0.70, 1.0),
        "rail_gold": (0.74, 0.64, 0.34, 1.0),
        "hardware": (0.18, 0.20, 0.18, 1.0),
        "cover_white": (0.50, 0.55, 0.48, 1.0),
    },
    "bare_alloy": {
        "hull_white": (0.70, 0.71, 0.74, 1.0),
        "plate_grey": (0.58, 0.60, 0.64, 1.0),
        "seal_tan": (0.62, 0.52, 0.38, 1.0),
        "lid_tan": (0.66, 0.67, 0.70, 1.0),
        "metal_grey": (0.50, 0.52, 0.56, 1.0),
        "silver": (0.84, 0.86, 0.88, 1.0),
        "rail_gold": (0.78, 0.70, 0.46, 1.0),
        "hardware": (0.28, 0.29, 0.32, 1.0),
        "cover_white": (0.72, 0.73, 0.76, 1.0),
    },
    "charcoal_service": {
        "hull_white": (0.20, 0.21, 0.23, 1.0),
        "plate_grey": (0.16, 0.17, 0.19, 1.0),
        "seal_tan": (0.55, 0.46, 0.30, 1.0),
        "lid_tan": (0.28, 0.28, 0.30, 1.0),
        "metal_grey": (0.34, 0.35, 0.38, 1.0),
        "silver": (0.60, 0.62, 0.65, 1.0),
        "rail_gold": (0.66, 0.56, 0.30, 1.0),
        "hardware": (0.08, 0.08, 0.10, 1.0),
        "cover_white": (0.26, 0.27, 0.29, 1.0),
    },
    "copper_thermal": {
        "hull_white": (0.82, 0.80, 0.76, 1.0),
        "plate_grey": (0.60, 0.55, 0.48, 1.0),
        "seal_tan": (0.72, 0.58, 0.36, 1.0),
        "lid_tan": (0.74, 0.56, 0.34, 1.0),
        "metal_grey": (0.54, 0.46, 0.38, 1.0),
        "silver": (0.78, 0.70, 0.58, 1.0),
        "rail_gold": (0.80, 0.58, 0.24, 1.0),
        "hardware": (0.24, 0.18, 0.12, 1.0),
        "cover_white": (0.80, 0.72, 0.60, 1.0),
    },
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class AstronomyPressurisedModuleDoorConfig:
    aperture_form: ApertureForm = "round_aperture"
    closure_module: ClosureModule = "single_swing_lid"
    locking_control: LockingControl = "rim_handwheel"
    palette_style: DoorPalette = "nasa_white"

    cover_count: int = 0      # radial debris covers; 0 = none
    bolt_count: int = 12      # end-plate bolt ring
    dog_count: int = 8        # latch dogs (lid) + strikes (collar), paired
    spoke_count: int = 3      # handwheel spokes

    hull_radius_scale: float = 1.0
    collar_scale: float = 1.0
    lid_open: float = 1.90    # swing lid / leaf open angle (rad)
    dome_height: float = 0.15
    cover_open: float = 1.40


@dataclass(frozen=True)
class ResolvedDoorConfig:
    aperture_form: ApertureForm
    closure_module: ClosureModule
    locking_control: LockingControl
    palette_style: str

    cover_count: int
    bolt_count: int
    dog_count: int
    spoke_count: int

    hull_radius_scale: float
    collar_scale: float
    lid_open: float
    dome_height: float
    cover_open: float

    # Derived aperture / mounting envelope (single-sourced; Contract 3c).
    hull_r: float
    collar_ro: float
    opening_ri: float
    lid_r: float
    hinge_x: float           # swing hinge pin x (= lid disc local x)
    leaf_open: float         # double-leaf swing cap (< lid_open so leaves clear)
    cover_hinge_r: float     # debris-cover hinge ring radius
    cover_len: float         # debris-cover panel radial length (annulus-fit)

    palette: dict[str, tuple[float, float, float, float]]


# --------------------------------------------------------------------------- #
# Seed-driven sampling (procedural-first)
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> AstronomyPressurisedModuleDoorConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin 母本 combination (round aperture + single
    swing lid, 0 covers, 12 bolts / 8 dogs / 3 spokes, nasa_white) as a
    documented regression anchor; every other seed is fully procedural.
    """
    if seed == 0:
        return AstronomyPressurisedModuleDoorConfig()

    rng = random.Random(seed)

    aperture_form: ApertureForm = rng.choice(
        ("round_aperture", "square_aperture", "hex_aperture", "octagonal_aperture")
    )
    closure_module: ClosureModule = rng.choice(
        ("single_swing_lid", "reinforced_swing_lid", "domed_swing_lid", "double_leaf")
    )
    locking_control: LockingControl = rng.choice(
        ("rim_handwheel", "crossbar_lock", "tri_grip_wheel")
    )
    palette_style = rng.choice(PALETTE_NAMES)

    cover_count = rng.choices((0, 6, 8, 12), weights=(0.55, 0.15, 0.20, 0.10))[0]
    bolt_count = rng.choices((12, 24), weights=(0.6, 0.4))[0]
    dog_count = rng.choices((8, 12), weights=(0.6, 0.4))[0]
    spoke_count = rng.choices((3, 5), weights=(0.6, 0.4))[0]

    hull_radius_scale = round(rng.uniform(0.90, 1.10), 4)
    collar_scale = round(rng.uniform(0.90, 1.15), 4)
    lid_open = round(rng.uniform(1.55, 2.00), 4)
    dome_height = round(rng.uniform(0.10, 0.20), 4)
    cover_open = round(rng.uniform(1.20, 1.60), 4)

    return AstronomyPressurisedModuleDoorConfig(
        aperture_form=aperture_form,
        closure_module=closure_module,
        locking_control=locking_control,
        palette_style=palette_style,
        cover_count=cover_count,
        bolt_count=bolt_count,
        dog_count=dog_count,
        spoke_count=spoke_count,
        hull_radius_scale=hull_radius_scale,
        collar_scale=collar_scale,
        lid_open=lid_open,
        dome_height=dome_height,
        cover_open=cover_open,
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(config: AstronomyPressurisedModuleDoorConfig) -> ResolvedDoorConfig:
    if str(config.aperture_form) not in {
        "round_aperture",
        "square_aperture",
        "hex_aperture",
        "octagonal_aperture",
    }:
        raise ValueError(f"Unsupported aperture_form: {config.aperture_form}")
    if str(config.closure_module) not in {
        "single_swing_lid",
        "reinforced_swing_lid",
        "domed_swing_lid",
        "double_leaf",
    }:
        raise ValueError(f"Unsupported closure_module: {config.closure_module}")
    if str(config.locking_control) not in {
        "rim_handwheel",
        "crossbar_lock",
        "tri_grip_wheel",
    }:
        raise ValueError(f"Unsupported locking_control: {config.locking_control}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    hull_radius_scale = _clamp(config.hull_radius_scale, 0.90, 1.10)
    collar_scale = _clamp(config.collar_scale, 0.90, 1.15)
    lid_open = _clamp(config.lid_open, 1.55, 2.00)
    dome_height = _clamp(config.dome_height, 0.10, 0.20)
    cover_open = _clamp(config.cover_open, 1.20, 1.60)

    # Compatibility gating (§9): curved dome / half-disc leaves are demonstrated
    # only for the round aperture, so polygonal apertures use one of the two
    # aperture-adaptive flat swing lids.
    aperture_form = config.aperture_form
    closure_module = config.closure_module
    if aperture_form != "round_aperture" and closure_module in _ROUND_ONLY_CLOSURES:
        closure_module = (
            "reinforced_swing_lid"
            if closure_module == "double_leaf"
            else "single_swing_lid"
        )

    # Derived aperture / mounting envelope.
    hull_r = BASE_HULL_R * hull_radius_scale
    collar_ro = BASE_COLLAR_RO * collar_scale
    opening_ri = BASE_OPENING_RI * collar_scale
    lid_r = collar_ro
    # Swing hinge bracket stands well clear in -X so the closed dog ring (out to
    # ~collar_ro+0.075) never clips the bracket, even at dog_count=12.
    hinge_x = -(collar_ro + 0.18)
    # Double-leaf leaves are capped short of the swing-lid range so the outward
    # half-disc never sweeps into the -X/+X hinge brackets on the collar rim.
    leaf_open = min(lid_open, 1.50)
    # Radial debris-cover ring lives in the flat annulus between the collar rim
    # and the hull rim. The hinge sits just inside the rim; the panel reaches
    # inward but must clear the taller collar. Panel length adapts to the annulus
    # so its inner edge always keeps a margin off collar_ro (Contract 3c).
    cover_hinge_r = _clamp(hull_r - 0.05, collar_ro + 0.17, hull_r - 0.05)
    cover_len = _clamp(cover_hinge_r - (collar_ro + 0.07), 0.10, 0.24)

    # cover_count gating: the radial cover ring is demonstrated only with the
    # round aperture + a side-swing lid (radial_covers S9), whose single -X hinge
    # bracket the half-step-offset ring clears. Cap to {0,6,8} (12 packs a cover
    # too close to the bracket azimuth); non-round or bi-parting => no covers.
    cover_count = int(config.cover_count) if int(config.cover_count) in (0, 6, 8, 12) else 0
    if cover_count >= 12:
        cover_count = 8
    if aperture_form != "round_aperture" or closure_module not in (
        "single_swing_lid",
        "reinforced_swing_lid",
        "domed_swing_lid",
    ):
        cover_count = 0

    # dog_count gating: square rim uses a fixed 2-per-side (8) layout; the hex
    # rim uses exactly one dog/strike per face (6), aligned to the 6 flats so
    # every plate embeds in a receding hex face (no floating islands).
    dog_count = int(config.dog_count) if int(config.dog_count) in (8, 12) else 8
    if aperture_form == "square_aperture":
        dog_count = 8
    elif aperture_form == "hex_aperture":
        dog_count = 6
    elif aperture_form == "octagonal_aperture":
        dog_count = 8

    bolt_count = int(config.bolt_count) if int(config.bolt_count) in (12, 24) else 12
    spoke_count = int(config.spoke_count) if int(config.spoke_count) in (3, 5) else 3

    return ResolvedDoorConfig(
        aperture_form=aperture_form,
        closure_module=closure_module,
        locking_control=config.locking_control,
        palette_style=config.palette_style,
        cover_count=cover_count,
        bolt_count=bolt_count,
        dog_count=dog_count,
        spoke_count=spoke_count,
        hull_radius_scale=hull_radius_scale,
        collar_scale=collar_scale,
        lid_open=lid_open,
        dome_height=dome_height,
        cover_open=cover_open,
        hull_r=hull_r,
        collar_ro=collar_ro,
        opening_ri=opening_ri,
        lid_r=lid_r,
        hinge_x=hinge_x,
        leaf_open=leaf_open,
        cover_hinge_r=cover_hinge_r,
        cover_len=cover_len,
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# cadquery geometry helpers (adapted verbatim from the 5-star sources)
# --------------------------------------------------------------------------- #


def _ring(ro: float, ri: float, h: float) -> cq.Workplane:
    """Circular annular ring (origin S1 L49-50)."""
    return cq.Workplane("XY").circle(ro).circle(ri).extrude(h)


def _rounded_sq_solid(half: float, fillet_r: float, height: float) -> cq.Workplane:
    """Extruded rounded-square solid (square_hatch S6 L74-82)."""
    return (
        cq.Workplane("XY").rect(2 * half, 2 * half).extrude(height).edges("|Z").fillet(fillet_r)
    )


def _rounded_sq_ring(outer_half: float, outer_fillet: float, inner_half: float,
                     inner_fillet: float, height: float) -> cq.Workplane:
    """Rounded-square ring: outer minus inner (square_hatch S6 L85-104)."""
    outer = (
        cq.Workplane("XY").rect(2 * outer_half, 2 * outer_half).extrude(height)
        .edges("|Z").fillet(outer_fillet)
    )
    inner = (
        cq.Workplane("XY").rect(2 * inner_half, 2 * inner_half).extrude(height + 0.02)
        .edges("|Z").fillet(inner_fillet).translate((0, 0, -0.01))
    )
    return outer.cut(inner)


def _circle_with_sq_hole(circle_r: float, sq_half: float, sq_fillet: float,
                         height: float) -> cq.Workplane:
    """Circular plate with a rounded-square through-hole (square_hatch S6 L107-119)."""
    plate = cq.Workplane("XY").circle(circle_r).extrude(height)
    hole = (
        cq.Workplane("XY").rect(2 * sq_half, 2 * sq_half).extrude(height + 0.02)
        .edges("|Z").fillet(sq_fillet).translate((0, 0, -0.01))
    )
    return plate.cut(hole)


def _polygon_solid(sides: int, circum_r: float, height: float) -> cq.Workplane:
    """Regular polygon solid for the hexagonal/octagonal aperture family."""
    return cq.Workplane("XY").polygon(sides, 2.0 * circum_r).extrude(height)


def _polygon_ring(
    sides: int,
    outer_r: float,
    inner_r: float,
    height: float,
) -> cq.Workplane:
    """Regular-polygon ring: outer polygon minus inner polygon."""
    outer = cq.Workplane("XY").polygon(sides, 2.0 * outer_r).extrude(height)
    inner = (
        cq.Workplane("XY").polygon(sides, 2.0 * inner_r).extrude(height + 0.02)
        .translate((0, 0, -0.01))
    )
    return outer.cut(inner)


def _circle_with_polygon_hole(
    sides: int,
    circle_r: float,
    polygon_r: float,
    height: float,
) -> cq.Workplane:
    """Circular plate with a regular-polygon through-hole."""
    plate = cq.Workplane("XY").circle(circle_r).extrude(height)
    hole = (
        cq.Workplane("XY").polygon(sides, 2.0 * polygon_r).extrude(height + 0.02)
        .translate((0, 0, -0.01))
    )
    return plate.cut(hole)


def _half_disc(radius: float, thickness: float, side: int = 1) -> cq.Workplane:
    """Semicircular disc for one bi-parting leaf (double_leaf S7 L61-78)."""
    r = radius
    cx = -r if side > 0 else r
    return (
        cq.Workplane("XY").moveTo(cx, -r).threePointArc((0.0, 0.0), (cx, r))
        .lineTo(cx, -r).close().extrude(thickness)
    )


def _dome_cap_profile(rim_r: float, height: float, n_arc: int = 28) -> list[tuple[float, float]]:
    """(radius, z) profile for a solid spherical cap, base z=0, apex z=height
    (dome_lid S5 L52-68)."""
    R = (rim_r ** 2 + height ** 2) / (2.0 * height)
    theta_max = math.asin(min(1.0, rim_r / R))
    pts: list[tuple[float, float]] = [(0.0, 0.0), (rim_r, 0.0)]
    for i in range(1, n_arc + 1):
        t = theta_max * (1.0 - i / n_arc)
        r = R * math.sin(t)
        z = R * math.cos(t) - (R - height)
        pts.append((max(0.0, r), z))
    return pts


# radial debris-cover panel dims (radial_covers S9 L49-77)
COVER_LENGTH = 0.24
COVER_WIDTH = 0.20
COVER_THICK = 0.012


# --------------------------------------------------------------------------- #
# Rim / decoration placement helpers
# --------------------------------------------------------------------------- #


def _square_rim_positions(half_size: float) -> list[tuple[float, float, float]]:
    """8 (x, y, outward-angle) positions around a square perimeter, 2 per side
    (square_hatch S6 L122-143)."""
    s = half_size
    f = 1.0 / 3.0
    return [
        (s, s * f, 0.0), (s, -s * f, 0.0),
        (-s * f, -s, -math.pi / 2), (s * f, -s, -math.pi / 2),
        (-s, -s * f, math.pi), (-s, s * f, math.pi),
        (s * f, s, math.pi / 2), (-s * f, s, math.pi / 2),
    ]


def _radial_rim_positions(radius: float, count: int) -> list[tuple[float, float, float]]:
    """`count` (x, y, angle) positions on a circle, half-step offset (origin
    S1 L103/L175: 45*i + 22.5 == (360/n)*i + (360/n)/2)."""
    out = []
    for j in range(count):
        a = math.radians((360.0 / count) * j + (360.0 / count) / 2.0)
        out.append((radius * math.cos(a), radius * math.sin(a), a))
    return out


def _polygon_face_positions(
    sides: int,
    radius: float,
) -> list[tuple[float, float, float]]:
    """Positions on regular-polygon face midpoints."""
    out = []
    for j in range(sides):
        a = 2.0 * math.pi * j / sides
        out.append((radius * math.cos(a), radius * math.sin(a), a))
    return out


def _dog_strike_positions(r: ResolvedDoorConfig, at_radius: float) -> list[tuple[float, float, float]]:
    if r.aperture_form == "square_aperture":
        return _square_rim_positions(at_radius)
    if r.aperture_form == "hex_aperture":
        return _polygon_face_positions(6, at_radius)
    if r.aperture_form == "octagonal_aperture":
        return _polygon_face_positions(8, at_radius)
    return _radial_rim_positions(at_radius, r.dog_count)


def _collar_profile_ring(
    r: ResolvedDoorConfig,
    *,
    outer_offset: float,
    inner_offset: float,
    height: float,
) -> cq.Workplane:
    """Build a collar frame that follows the realized hatch boundary."""
    if r.aperture_form == "round_aperture":
        return _ring(
            r.collar_ro + outer_offset,
            r.collar_ro - inner_offset,
            height,
        )
    if r.aperture_form == "square_aperture":
        outer_half = r.collar_ro * 0.87 + outer_offset
        inner_half = r.collar_ro * 0.87 - inner_offset
        return _rounded_sq_ring(
            outer_half,
            0.10 * r.collar_scale + outer_offset * 0.35,
            inner_half,
            0.08 * r.collar_scale,
            height,
        )
    sides = 6 if r.aperture_form == "hex_aperture" else 8
    return _polygon_ring(
        sides,
        r.collar_ro + outer_offset,
        r.collar_ro - inner_offset,
        height,
    )


# --------------------------------------------------------------------------- #
# Slot A — shell_aperture (root, ③ Primary Form Family)
# --------------------------------------------------------------------------- #


def _shell_downstream(r: ResolvedDoorConfig) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="airlock_shell",
        visual_name="end_plate",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, PLATE_TOP),
        face_extents_uv=(2.0 * r.collar_ro, 2.0 * r.collar_ro),
        contact_tol=0.004,
    )


def _emit_shell_common(shell, r: ResolvedDoorConfig) -> None:
    """Circular hull + end plate + collar + seal + bolts + strikes + handrails,
    with the aperture cross-section prototype chosen by ``aperture_form``."""
    hull_r = r.hull_r
    collar_ro = r.collar_ro
    opening_ri = r.opening_ri

    # --- circular hull (invariant across aperture forms) ---
    shell.visual(
        mesh_from_cadquery(_ring(hull_r, hull_r - HULL_WALL, HULL_TOP), "hull_tube"),
        origin=Origin(), material="hull_white", name="hull_tube", material_class_id="metal.paint_coated",
    )
    shell.visual(
        Cylinder(radius=hull_r, length=0.05),
        origin=Origin(xyz=(0.0, 0.0, 0.025)), material="hull_white", name="hull_base_cap", material_class_id="metal.paint_coated",
    )
    shell.visual(
        mesh_from_cadquery(_ring(hull_r + 0.015, hull_r - 0.01, 0.05), "hull_seam"),
        origin=Origin(xyz=(0.0, 0.0, 0.55)), material="plate_grey", name="hull_seam", material_class_id="metal.aluminum_bare",
    )
    # Pressure-vessel frames and shallow longerons keep the module from reading
    # as a bare cylinder.  Every member embeds slightly into the hull wall.
    for i, z in enumerate((0.16, 0.88)):
        shell.visual(
            mesh_from_cadquery(
                _ring(hull_r + 0.012, hull_r - 0.012, 0.035),
                f"hull_frame_{i}",
            ),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material="plate_grey",
            name=f"hull_frame_{i}", material_class_id="metal.aluminum_bare",
        )
    for i in range(8):
        a = 2.0 * math.pi * i / 8.0
        shell.visual(
            Box((0.028, 0.055, 0.68)),
            origin=Origin(
                xyz=(
                    (hull_r + 0.002) * math.cos(a),
                    (hull_r + 0.002) * math.sin(a),
                    0.52,
                ),
                rpy=(0.0, 0.0, a),
            ),
            material="plate_grey",
            name=f"hull_longeron_{i}", material_class_id="metal.aluminum_bare",
        )
    for i, a_deg in enumerate((35.0, 145.0, 215.0, 325.0)):
        a = math.radians(a_deg)
        shell.visual(
            Box((0.022, 0.20, 0.24)),
            origin=Origin(
                xyz=(
                    (hull_r + 0.006) * math.cos(a),
                    (hull_r + 0.006) * math.sin(a),
                    0.64 if i % 2 == 0 else 0.34,
                ),
                rpy=(0.0, 0.0, a),
            ),
            material="hull_white",
            name=f"service_panel_{i}", material_class_id="metal.paint_coated",
        )

    # --- end plate (with the aperture opening) + collar + seal (③ prototype) ---
    if r.aperture_form == "round_aperture":
        end_plate = _ring(hull_r, opening_ri, PLATE_TOP - HULL_TOP)
        collar = _ring(collar_ro, opening_ri, COLLAR_TOP - PLATE_TOP)
        seal = _ring(collar_ro, opening_ri + 0.01, SEAL_TOP - COLLAR_TOP)
    elif r.aperture_form == "square_aperture":
        ap_half = opening_ri * 0.80          # square half-side of the opening
        ap_fillet = 0.08 * r.collar_scale
        collar_half = collar_ro * 0.87
        collar_fillet = 0.10 * r.collar_scale
        seal_inner = ap_half + 0.02
        end_plate = _circle_with_sq_hole(hull_r, ap_half, ap_fillet, PLATE_TOP - HULL_TOP)
        collar = _rounded_sq_ring(collar_half, collar_fillet, ap_half, ap_fillet,
                                  COLLAR_TOP - PLATE_TOP)
        seal = _rounded_sq_ring(collar_half - 0.02, collar_fillet, seal_inner,
                                ap_fillet, SEAL_TOP - COLLAR_TOP)
    else:
        sides = 6 if r.aperture_form == "hex_aperture" else 8
        end_plate = _circle_with_polygon_hole(
            sides, hull_r, opening_ri, PLATE_TOP - HULL_TOP
        )
        collar = _polygon_ring(
            sides, collar_ro, opening_ri, COLLAR_TOP - PLATE_TOP
        )
        seal = _polygon_ring(
            sides,
            collar_ro - 0.005,
            opening_ri + 0.01,
            SEAL_TOP - COLLAR_TOP,
        )

    shell.visual(mesh_from_cadquery(end_plate, "end_plate"),
                 origin=Origin(xyz=(0.0, 0.0, HULL_TOP)), material="plate_grey", name="end_plate", material_class_id="metal.aluminum_bare")
    shell.visual(mesh_from_cadquery(collar, "hatch_collar"),
                 origin=Origin(xyz=(0.0, 0.0, PLATE_TOP)), material="hull_white", name="hatch_collar", material_class_id="metal.paint_coated")
    shell.visual(mesh_from_cadquery(seal, "seal_ring"),
                 origin=Origin(xyz=(0.0, 0.0, COLLAR_TOP)), material="seal_tan", name="seal_ring", material_class_id="rubber.smooth_plain")
    # Layered pressure frame: lower band, top flange and radial gussets.
    shell.visual(
        mesh_from_cadquery(
            _collar_profile_ring(
                r,
                outer_offset=0.055,
                inner_offset=0.015,
                height=0.035,
            ),
            "collar_outer_band",
        ),
        origin=Origin(xyz=(0.0, 0.0, PLATE_TOP + 0.035)),
        material="plate_grey",
        name="collar_outer_band", material_class_id="metal.aluminum_bare",
    )
    shell.visual(
        mesh_from_cadquery(
            _collar_profile_ring(
                r,
                outer_offset=0.025,
                inner_offset=0.025,
                height=0.025,
            ),
            "collar_top_flange",
        ),
        origin=Origin(xyz=(0.0, 0.0, COLLAR_TOP - 0.012)),
        material="metal_grey",
        name="collar_top_flange", material_class_id="metal.stainless_matte",
    )
    if r.aperture_form == "square_aperture":
        gusset_positions = _square_rim_positions(collar_ro * 0.87 + 0.015)
    elif r.aperture_form in ("hex_aperture", "octagonal_aperture"):
        sides = 6 if r.aperture_form == "hex_aperture" else 8
        gusset_positions = _polygon_face_positions(
            sides,
            collar_ro * math.cos(math.pi / sides) - 0.015,
        )
    else:
        gusset_positions = _radial_rim_positions(collar_ro + 0.015, 12)
    for i, (gx, gy, a) in enumerate(gusset_positions):
        shell.visual(
            Box((0.055, 0.038, 0.075)),
            origin=Origin(
                xyz=(
                    gx,
                    gy,
                    PLATE_TOP + 0.045,
                ),
                rpy=(0.0, 0.0, a),
            ),
            material="metal_grey",
            name=f"collar_gusset_{i}", material_class_id="metal.stainless_matte",
        )

    # --- bolt ring on the end plate (④ decoration, host-derived radius) ---
    bolt_r = collar_ro + 0.20
    for i in range(r.bolt_count):
        a = math.radians((360.0 / r.bolt_count) * i)
        shell.visual(
            Cylinder(radius=0.020, length=0.03),
            origin=Origin(xyz=(bolt_r * math.cos(a), bolt_r * math.sin(a), PLATE_TOP + 0.01)),
            material="metal_grey", name=f"plate_bolt_{i}", material_class_id="metal.stainless_matte",
        )

    # --- latch strike plates on the collar exterior (④, paired with lid dogs) ---
    # Radial rings ride the realized rim: round just outside collar_ro; regular
    # polygons at the collar apothem so plates embed in the receding flat faces.
    if r.aperture_form == "square_aperture":
        strike_half = collar_ro * 0.87 + 0.015
    elif r.aperture_form in ("hex_aperture", "octagonal_aperture"):
        sides = 6 if r.aperture_form == "hex_aperture" else 8
        strike_half = collar_ro * math.cos(math.pi / sides) - 0.045
    else:
        strike_half = collar_ro + 0.015
    for i, (sx, sy, sa) in enumerate(_dog_strike_positions(r, strike_half)):
        shell.visual(
            Box((0.11, 0.08, 0.10)),
            origin=Origin(xyz=(sx, sy, 1.16), rpy=(0.0, 0.0, sa)),
            material="metal_grey", name=f"latch_strike_{i}", material_class_id="metal.stainless_matte",
        )

    # --- EVA grab handrails on the hull exterior (④) ---
    for i, a_deg in enumerate((130.0, 230.0)):
        a = math.radians(a_deg)
        ux, uy = math.cos(a), math.sin(a)
        for k, pz in enumerate((0.40, 0.80)):
            shell.visual(
                Cylinder(radius=0.016, length=0.08),
                origin=Origin(xyz=((hull_r + 0.03) * ux, (hull_r + 0.03) * uy, pz),
                              rpy=(0.0, math.pi / 2.0, a)),
                material="rail_gold", name=f"rail_post_{i}_{k}", material_class_id="metal.brass_polished",
            )
        shell.visual(
            Cylinder(radius=0.018, length=0.52),
            origin=Origin(xyz=((hull_r + 0.07) * ux, (hull_r + 0.07) * uy, 0.60)),
            material="rail_gold", name=f"handrail_{i}", material_class_id="metal.brass_polished",
        )


def _emit_debris_covers(model, shell, r: ResolvedDoorConfig) -> list[str]:
    """Radial debris-cover shutter ring (radial_covers S9 L267-323).

    N identical covers, one shared mesh each, on REVOLUTE tangent hinges around
    the collar. rest q=0 = flat on the end plate; positive q lifts the inner
    edge off the hull. Half-step angular offset keeps covers off the hinge side.
    """
    if r.cover_count <= 0:
        return []
    # Panels ride above the bolt-ring z-band; a short hinge boss on the plate
    # carries the pin so the joint origin sits on real shell geometry.
    cover_hinge_z = PLATE_TOP + 0.05
    boss_h = cover_hinge_z - PLATE_TOP
    lug_h = 0.05
    cover_len = r.cover_len

    panel_mesh = mesh_from_cadquery(cq.Workplane("XY").box(cover_len, COVER_WIDTH, COVER_THICK), "cover_panel")
    lug_mesh = mesh_from_cadquery(cq.Workplane("XY").box(0.030, 0.025, lug_h), "cover_lug")
    grip_mesh = mesh_from_cadquery(cq.Workplane("XY").box(0.040, 0.060, COVER_THICK * 1.8), "cover_grip")

    parts, joints = [], []
    for i in range(r.cover_count):
        a = 2.0 * math.pi * (i + 0.5) / r.cover_count
        hx = r.cover_hinge_r * math.cos(a)
        hy = r.cover_hinge_r * math.sin(a)
        # Hinge boss on the shell (origin-honesty: joint origin on the boss top).
        shell.visual(Cylinder(radius=0.030, length=boss_h),
                     origin=Origin(xyz=(hx, hy, PLATE_TOP + boss_h / 2.0)),
                     material="metal_grey", name=f"cover_boss_{i}", material_class_id="metal.stainless_matte")
        cover = model.part(f"debris_cover_{i}")
        cover.visual(panel_mesh, origin=Origin(xyz=(-cover_len / 2.0, 0.0, -COVER_THICK / 2.0)),
                     material="cover_white", name="panel", material_class_id="metal.paint_coated")
        # Hinge knuckle lugs centred on the pin (hinge level) so they never dip
        # into the end plate as the cover swings up.
        for k, y_off in enumerate((-COVER_WIDTH * 0.35, COVER_WIDTH * 0.35)):
            cover.visual(lug_mesh, origin=Origin(xyz=(0.015, y_off, 0.0)),
                         material="metal_grey", name=f"lug_{k}", material_class_id="metal.stainless_matte")
        cover.visual(Cylinder(radius=0.008, length=COVER_WIDTH * 0.80),
                     origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                     material="silver", name="hinge_pin", material_class_id="metal.brushed_silver")
        cover.visual(grip_mesh, origin=Origin(xyz=(-cover_len + 0.010, 0.0, 0.0)),
                     material="metal_grey", name="grip_tab", material_class_id="metal.stainless_matte")
        jn = f"cover_hinge_{i}"
        model.articulation(
            jn, ArticulationType.REVOLUTE, parent=shell, child=cover,
            origin=Origin(xyz=(hx, hy, cover_hinge_z), rpy=(0.0, 0.0, a)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=10.0, velocity=2.0, lower=0.0, upper=r.cover_open),
        )
        parts.append(cover.name)
        joints.append(jn)
    return parts


def _build_shell(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedDoorConfig = ctx.config  # type: ignore[assignment]
    shell = model.part("airlock_shell")
    _emit_shell_common(shell, r)
    cover_parts = _emit_debris_covers(model, shell, r)
    return ModuleBuild(
        module_name=r.aperture_form,
        parts_emitted=["airlock_shell", *cover_parts],
        interfaces={"downstream": _shell_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot B — closure (parallel children on the shell)
# --------------------------------------------------------------------------- #


def _lid_plate_visual(lid, r: ResolvedDoorConfig, *, cx: float, cz: float, thick: float,
                      name: str) -> None:
    """Flat lid plate matching the aperture cross-section prototype."""
    if r.aperture_form == "round_aperture":
        lid.visual(Cylinder(radius=r.lid_r, length=thick),
                   origin=Origin(xyz=(cx, 0.0, cz)), material="lid_tan", name=name, material_class_id="metal.paint_coated")
    elif r.aperture_form == "square_aperture":
        lid_half = r.collar_ro * 0.87
        lid.visual(mesh_from_cadquery(_rounded_sq_solid(lid_half, 0.10 * r.collar_scale, thick), name),
                   origin=Origin(xyz=(cx, 0.0, cz)), material="lid_tan", name=name, material_class_id="metal.paint_coated")
    else:
        sides = 6 if r.aperture_form == "hex_aperture" else 8
        lid.visual(mesh_from_cadquery(_polygon_solid(sides, r.lid_r, thick), name),
                   origin=Origin(xyz=(cx, 0.0, cz)), material="lid_tan", name=name, material_class_id="metal.paint_coated")


def _lid_seal_visual(lid, r: ResolvedDoorConfig, *, cx: float, cz: float, name: str) -> None:
    if r.aperture_form == "round_aperture":
        mesh = _ring(r.lid_r, r.opening_ri, 0.02)
    elif r.aperture_form == "square_aperture":
        lid_half = r.collar_ro * 0.87
        mesh = _rounded_sq_ring(lid_half, 0.10 * r.collar_scale, r.opening_ri * 0.80 + 0.02,
                                0.07 * r.collar_scale, 0.02)
    else:
        sides = 6 if r.aperture_form == "hex_aperture" else 8
        mesh = _polygon_ring(sides, r.lid_r, r.opening_ri + 0.01, 0.02)
    lid.visual(mesh_from_cadquery(mesh, name), origin=Origin(xyz=(cx, 0.0, cz)),
               material="seal_tan", name=name, material_class_id="rubber.smooth_plain")


def _emit_lid_dogs(lid, r: ResolvedDoorConfig, *, cx: float, cz: float) -> None:
    if r.aperture_form == "square_aperture":
        dog_half = r.collar_ro * 0.87 - 0.03
    elif r.aperture_form in ("hex_aperture", "octagonal_aperture"):
        sides = 6 if r.aperture_form == "hex_aperture" else 8
        dog_half = r.lid_r * math.cos(math.pi / sides) - 0.03
    else:
        dog_half = r.lid_r + 0.03
    for j, (dx, dy, da) in enumerate(_dog_strike_positions(r, dog_half)):
        lid.visual(Box((0.09, 0.06, 0.04)), origin=Origin(xyz=(cx + dx, dy, cz), rpy=(0.0, 0.0, da)),
                   material="metal_grey", name=f"latch_dog_{j}", material_class_id="metal.stainless_matte")


def _emit_swing_hinge_hardware(shell, r: ResolvedDoorConfig) -> None:
    """Side hinge bracket lugs + pin added to the shell (origin S1 L114-127)."""
    hx = r.hinge_x
    shell.visual(
        Box((0.22, 0.38, 0.035)),
        origin=Origin(xyz=(hx + 0.055, 0.0, PLATE_TOP + 0.014)),
        material="metal_grey",
        name="hinge_backing_plate", material_class_id="metal.stainless_matte",
    )
    for k, ly in enumerate((-0.11, 0.11)):
        shell.visual(Box((0.08, 0.05, 0.24)), origin=Origin(xyz=(hx, ly, 1.17)),
                     material="metal_grey", name=f"hinge_bracket_lug_{k}", material_class_id="metal.stainless_matte")
        shell.visual(
            Cylinder(radius=0.046, length=0.075),
            origin=Origin(
                xyz=(hx, ly, HINGE_Z),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material="hardware",
            name=f"hinge_knuckle_{k}", material_class_id="metal.blackened_gunmetal",
        )
    shell.visual(Cylinder(radius=0.020, length=0.34),
                 origin=Origin(xyz=(hx, 0.0, HINGE_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                 material="silver", name="hinge_pin", material_class_id="metal.brushed_silver")


def _emit_locking_control(
    model,
    parent_part,
    r: ResolvedDoorConfig,
    *,
    origin_xyz: tuple,
    spoke_len: float,
    rim_ro: float,
    rim_ri: float,
) -> str:
    """Emit one of three locking controls on the source-backed handwheel axis."""
    wheel = model.part("lock_handwheel")
    wheel.visual(Cylinder(radius=0.05, length=0.10), origin=Origin(xyz=(0.0, 0.0, 0.005)),
                 material="silver", name="wheel_hub", material_class_id="metal.brushed_silver")
    if r.locking_control == "rim_handwheel":
        for j in range(r.spoke_count):
            a = math.radians((360.0 / r.spoke_count) * j)
            wheel.visual(
                Box((spoke_len, 0.03, 0.025)),
                origin=Origin(xyz=(0.0, 0.0, -0.028), rpy=(0.0, 0.0, a)),
                material="silver",
                name=f"wheel_spoke_{j}", material_class_id="metal.brushed_silver",
            )
        wheel.visual(
            mesh_from_cadquery(_ring(rim_ro, rim_ri, 0.03), "wheel_rim"),
            origin=Origin(xyz=(0.0, 0.0, -0.05)),
            material="hardware",
            name="wheel_rim", material_class_id="metal.blackened_gunmetal",
        )
        # Full-size swing lids have room for projecting rim grips.  The
        # off-centre wheel on a half leaf deliberately omits them so the grips
        # cannot sweep through the leaf edge while the wheel turns.
        if parent_part.name == "hatch_lid":
            for j in range(3):
                a = 2.0 * math.pi * (j + 0.5) / 3.0
                grip_r = 0.5 * (rim_ro + rim_ri)
                wheel.visual(
                    Cylinder(radius=0.023, length=0.075),
                    origin=Origin(
                        xyz=(grip_r * math.cos(a), grip_r * math.sin(a), -0.025)
                    ),
                    material="silver",
                    name=f"wheel_grip_{j}", material_class_id="metal.brushed_silver",
                )
    elif r.locking_control == "crossbar_lock":
        # A long asymmetric crossbar makes the locking rotation mechanically
        # legible without introducing a second axis or an external guide rail.
        wheel.visual(
            Box((spoke_len, 0.055, 0.035)),
            origin=Origin(xyz=(0.0, 0.0, -0.032)),
            material="silver",
            name="wheel_spoke_0", material_class_id="metal.brushed_silver",
        )
        wheel.visual(
            Box((spoke_len * 0.38, 0.045, 0.030)),
            origin=Origin(
                xyz=(spoke_len * 0.10, 0.0, -0.055),
                rpy=(0.0, 0.0, math.pi / 2.0),
            ),
            material="hardware",
            name="crossbar_index_tab", material_class_id="metal.blackened_gunmetal",
        )
        for j, sx in enumerate((-1.0, 1.0)):
            wheel.visual(
                Cylinder(radius=0.038, length=0.075),
                origin=Origin(
                    xyz=(sx * spoke_len * 0.46, 0.0, -0.065),
                    rpy=(0.0, math.pi / 2.0, 0.0),
                ),
                material="hardware",
                name=f"crossbar_grip_{j}", material_class_id="metal.blackened_gunmetal",
            )
    else:  # tri_grip_wheel
        arm_len = spoke_len * 0.48
        for j in range(3):
            a = 2.0 * math.pi * j / 3.0
            wheel.visual(
                Box((arm_len, 0.038, 0.028)),
                origin=Origin(
                    xyz=(
                        0.5 * arm_len * math.cos(a),
                        0.5 * arm_len * math.sin(a),
                        -0.030,
                    ),
                    rpy=(0.0, 0.0, a),
                ),
                material="silver",
                name=f"wheel_spoke_{j}", material_class_id="metal.brushed_silver",
            )
            wheel.visual(
                Cylinder(radius=0.045, length=0.065),
                origin=Origin(
                    xyz=(
                        arm_len * math.cos(a),
                        arm_len * math.sin(a),
                        -0.060,
                    )
                ),
                material="hardware",
                name=f"tri_grip_{j}", material_class_id="metal.blackened_gunmetal",
            )

    model.articulation("handwheel_spin", ArticulationType.REVOLUTE, parent=parent_part, child=wheel,
                       origin=Origin(xyz=origin_xyz), axis=(0.0, 0.0, 1.0),
                       motion_limits=MotionLimits(effort=10.0, velocity=2.0, lower=-2.6, upper=2.6))
    return wheel.name


def _build_swing_lid(
    ctx: ModuleBuildContext,
    *,
    domed: bool,
    reinforced: bool = False,
) -> ModuleBuild:
    """Single swing lid (flat, reinforced, or convex dome) on a REVOLUTE hinge.

    Lid local frame: disc/dome centered at (hinge_x, 0, ~0); the hinge joint
    origin at (hinge_x, 0, HINGE_Z) bakes the open angle into its rpy so rest
    q=0 is the open pose, exactly as origin S1 (and dome_lid S5).
    """
    model = ctx.model
    r: ResolvedDoorConfig = ctx.config  # type: ignore[assignment]
    shell = model.get_part("airlock_shell")
    _emit_swing_hinge_hardware(shell, r)
    hx = r.hinge_x

    lid = model.part("hatch_lid")
    if domed:
        dome_mesh = mesh_from_geometry(
            LatheGeometry(_dome_cap_profile(r.lid_r, r.dome_height), segments=48), "lid_dome")
        lid.visual(dome_mesh, origin=Origin(xyz=(hx, 0.0, -0.01)), material="lid_tan", name="lid_dome", material_class_id="metal.paint_coated")
        lid.visual(Cylinder(radius=0.18, length=0.03),
                   origin=Origin(xyz=(hx, 0.0, -0.01 + r.dome_height + 0.015)),
                   material="plate_grey", name="lid_hub_boss", material_class_id="metal.aluminum_bare")
    else:
        _lid_plate_visual(lid, r, cx=hx, cz=0.015, thick=0.05, name="lid_disc")
        lid.visual(Cylinder(radius=r.lid_r * 0.83, length=0.03),
                   origin=Origin(xyz=(hx, 0.0, 0.055)), material="lid_tan", name="lid_dome_step", material_class_id="metal.paint_coated")
        lid.visual(Cylinder(radius=0.20, length=0.03),
                   origin=Origin(xyz=(hx, 0.0, 0.085)), material="plate_grey", name="lid_hub_boss", material_class_id="metal.aluminum_bare")
        if reinforced:
            web_ro = r.lid_r * 0.72
            web_ri = r.lid_r * 0.65
            lid.visual(
                mesh_from_cadquery(
                    _ring(web_ro, web_ri, 0.035),
                    "reinforcement_ring",
                ),
                origin=Origin(xyz=(hx, 0.0, 0.068)),
                material="metal_grey",
                name="reinforcement_ring", material_class_id="metal.stainless_matte",
            )
            for j in range(6):
                a = math.pi * j / 3.0
                lid.visual(
                    Box((r.lid_r * 1.46, 0.045, 0.038)),
                    origin=Origin(
                        xyz=(hx, 0.0, 0.087),
                        rpy=(0.0, 0.0, a),
                    ),
                    material="metal_grey",
                    name=f"reinforcement_rib_{j}", material_class_id="metal.stainless_matte",
                )
    _lid_seal_visual(lid, r, cx=hx, cz=-0.03, name="lid_seal_ring")
    _emit_lid_dogs(lid, r, cx=hx, cz=0.0)
    # Lid-side hinge lugs wrapping the shell pin + a strap that bridges from the
    # lugs (part-frame origin) into the disc inner edge. The strap length adapts
    # to the disc size so it stays connected across round / square / hex lids.
    for k, ly in enumerate((-0.05, 0.05)):
        lid.visual(Box((0.09, 0.04, 0.09)), origin=Origin(xyz=(0.0, ly, 0.0)),
                   material="metal_grey", name=f"lid_hinge_lug_{k}", material_class_id="metal.stainless_matte")
    # min local +x extent of the lid plate (hex uses apothem so the strap reaches
    # the nearest face); disc extends toward -x from there.
    disc_reach = r.lid_r if r.aperture_form == "round_aperture" else (
        r.collar_ro * 0.87 if r.aperture_form == "square_aperture" else r.lid_r * (math.sqrt(3.0) / 2.0)
    )
    disc_inner_x = hx + disc_reach
    strap_min = disc_inner_x - 0.03
    strap_max = 0.03
    lid.visual(Box((strap_max - strap_min, 0.12, 0.035)),
               origin=Origin(xyz=((strap_min + strap_max) / 2.0, 0.0, 0.0)),
               material="metal_grey", name="hinge_strap", material_class_id="metal.stainless_matte")

    model.articulation("hatch_hinge", ArticulationType.REVOLUTE, parent=shell, child=lid,
                       origin=Origin(xyz=(hx, 0.0, HINGE_Z), rpy=(0.0, r.lid_open, math.pi)),
                       axis=(0.0, 1.0, 0.0),
                       motion_limits=MotionLimits(effort=40.0, velocity=1.0, lower=-r.lid_open, upper=0.08))

    wheel = _emit_locking_control(
        model,
        lid,
        r,
        origin_xyz=(hx, 0.0, -0.03),
        spoke_len=r.lid_r * 1.10,
        rim_ro=r.lid_r * 0.57,
        rim_ri=r.lid_r * 0.50,
    )

    return ModuleBuild(
        module_name=(
            "domed_swing_lid"
            if domed
            else ("reinforced_swing_lid" if reinforced else "single_swing_lid")
        ),
        parts_emitted=["hatch_lid", wheel],
        internal_articulations=["hatch_hinge", "handwheel_spin"],
        interfaces={"downstream": _shell_downstream(r)},
    )


def _build_single_swing_lid(ctx: ModuleBuildContext) -> ModuleBuild:
    return _build_swing_lid(ctx, domed=False)


def _build_reinforced_swing_lid(ctx: ModuleBuildContext) -> ModuleBuild:
    return _build_swing_lid(ctx, domed=False, reinforced=True)


def _build_domed_swing_lid(ctx: ModuleBuildContext) -> ModuleBuild:
    return _build_swing_lid(ctx, domed=True)


def _build_double_leaf(ctx: ModuleBuildContext) -> ModuleBuild:
    """Two bi-parting half-disc leaves on twin side hinges (double_leaf S7).

    Gated to round aperture. rest q=0 = both closed meeting at centre; positive
    q swings each leaf outward. Handwheel is a child of hatch_leaf_0.
    """
    model = ctx.model
    r: ResolvedDoorConfig = ctx.config  # type: ignore[assignment]
    shell = model.get_part("airlock_shell")
    collar_ro = r.collar_ro
    leaf_recess = 0.05
    leaf_r = collar_ro - leaf_recess
    leaf_thick = 0.05
    hinge_z_leaf = COLLAR_TOP + 0.07
    # The leaf slab hangs entirely *below* the hinge axis (its top face on the
    # axis). Every disc point is then inboard (x<=pin) and low (z<=axis), so on
    # opening the slab swings purely up-and-inboard and never sweeps outboard-down
    # into the collar rim or the pin-carrying bracket (Contract 3c motion safety).
    leaf_z = -leaf_thick / 2.0

    # Leaf hinge bracket posts on the collar rim at +X and -X (added to shell).
    # The posts are widened inboard so they physically capture the hinge pin
    # (no floating pin island); the raised leaf never reaches this outboard band.
    bracket_z_bot = PLATE_TOP
    bracket_z_top = hinge_z_leaf + 0.06
    bracket_z_cen = (bracket_z_bot + bracket_z_top) / 2.0
    bracket_h = bracket_z_top - bracket_z_bot
    for i, (hx, off) in enumerate(((collar_ro, 0.10), (-collar_ro, -0.10))):
        bx = hx + off
        for k, ly_off in enumerate((-0.06, 0.06)):
            shell.visual(Box((0.14, 0.06, bracket_h)), origin=Origin(xyz=(bx, ly_off, bracket_z_cen)),
                         material="metal_grey", name=f"leaf_bracket_{i}_{k}", material_class_id="metal.stainless_matte")
        # Fat hinge pin ON the axis so the joint origin sits on real shell hardware
        # (origin-honesty); it reaches out to the brackets (no island) and the leaf
        # hinge lugs wrap it (captured pivot).
        shell.visual(Cylinder(radius=0.040, length=0.20),
                     origin=Origin(xyz=(hx, 0.0, hinge_z_leaf), rpy=(math.pi / 2.0, 0.0, 0.0)),
                     material="silver", name=f"leaf_pin_{i}", material_class_id="metal.brushed_silver")

    hinge_configs = [
        {"pos": (collar_ro, 0.0, hinge_z_leaf), "axis": (0.0, 1.0, 0.0)},
        {"pos": (-collar_ro, 0.0, hinge_z_leaf), "axis": (0.0, -1.0, 0.0)},
    ]
    leaves, joints = [], []
    for i in range(2):
        side = 1 if i == 0 else -1
        cfg = hinge_configs[i]
        leaf = model.part(f"hatch_leaf_{i}")
        leaves.append(leaf.name)
        # Recess the whole slab inboard so its curved apex stays clear of the pin;
        # the knuckle lugs bridge the small gap out to the captured pin.
        dx = -side * leaf_recess
        leaf.visual(mesh_from_cadquery(_half_disc(leaf_r, leaf_thick, side), f"leaf_disc_{i}"),
                    origin=Origin(xyz=(dx, 0.0, -leaf_thick / 2.0 + leaf_z)), material="lid_tan", name=f"leaf_disc_{i}", material_class_id="metal.paint_coated")
        leaf.visual(mesh_from_cadquery(_half_disc(leaf_r * 0.78, 0.012, side), f"leaf_step_{i}"),
                    origin=Origin(xyz=(dx, 0.0, leaf_thick / 2.0 + leaf_z)), material="lid_tan", name=f"leaf_step_{i}", material_class_id="metal.paint_coated")
        leaf.visual(mesh_from_cadquery(_half_disc(leaf_r * 0.86, 0.005, side), f"leaf_seal_{i}"),
                    origin=Origin(xyz=(dx, 0.0, -leaf_thick / 2.0 - 0.005 + leaf_z)), material="seal_tan", name=f"leaf_seal_{i}", material_class_id="rubber.smooth_plain")
        leaf.visual(Cylinder(radius=0.08, length=0.025),
                    origin=Origin(xyz=(-side * leaf_r * 0.55 + dx, 0.0, leaf_thick / 2.0 + 0.012 + 0.0125 + leaf_z)),
                    material="plate_grey", name=f"leaf_hub_{i}", material_class_id="metal.aluminum_bare")
        # latch dogs along the curved edge
        cx_disc = -side * leaf_r
        for j, td in enumerate((45, -45, 70, -70)):
            theta = math.radians(td if side > 0 else 180 - td)
            lx = cx_disc + leaf_r * math.cos(theta) + dx
            ly = leaf_r * math.sin(theta)
            leaf.visual(Box((0.08, 0.05, 0.04)), origin=Origin(xyz=(lx, ly, leaf_z), rpy=(0.0, 0.0, theta)),
                        material="metal_grey", name=f"leaf_latch_{i}_{j}", material_class_id="metal.stainless_matte")
        # Hinge knuckle lugs straddle the pin (local z~0) yet stay above the collar
        # through the swing; strap bridges from the lugs into the disc slab.
        for k, ly_off in enumerate((-0.06, 0.06)):
            leaf.visual(Box((0.10, 0.04, 0.06)), origin=Origin(xyz=(0.0, ly_off, 0.0)),
                        material="metal_grey", name=f"leaf_hinge_lug_{i}_{k}", material_class_id="metal.stainless_matte")
        leaf.visual(Box((0.12, 0.10, 0.05)), origin=Origin(xyz=(-side * 0.06, 0.0, leaf_z)),
                    material="metal_grey", name=f"leaf_hinge_strap_{i}", material_class_id="metal.stainless_matte")
        jn = f"leaf_hinge_{i}"
        model.articulation(jn, ArticulationType.REVOLUTE, parent=shell, child=leaf,
                           origin=Origin(xyz=cfg["pos"]), axis=cfg["axis"],
                           motion_limits=MotionLimits(effort=40.0, velocity=1.0, lower=0.0, upper=r.leaf_open))
        joints.append(jn)

    leaf0 = model.get_part("hatch_leaf_0")
    hw_x = -leaf_r * 0.55
    hw_z = -leaf_thick / 2.0 - 0.02
    wheel = _emit_locking_control(
        model,
        leaf0,
        r,
        origin_xyz=(hw_x, 0.0, hw_z),
        spoke_len=leaf_r * 0.62,
        rim_ro=leaf_r * 0.34,
        rim_ri=leaf_r * 0.28,
    )

    return ModuleBuild(
        module_name="double_leaf",
        parts_emitted=[*leaves, wheel],
        internal_articulations=[*joints, "handwheel_spin"],
        interfaces={"downstream": _shell_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Factory registries + assembly
# --------------------------------------------------------------------------- #

CLOSURE_FACTORIES = {
    "single_swing_lid": _build_single_swing_lid,
    "reinforced_swing_lid": _build_reinforced_swing_lid,
    "domed_swing_lid": _build_domed_swing_lid,
    "double_leaf": _build_double_leaf,
}


def _slots_for_config(r: ResolvedDoorConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="shell_aperture", candidates={r.aperture_form: _build_shell},
                 anchor_choice=r.aperture_form),
        SlotSpec(slot_name="closure",
                 candidates={r.closure_module: CLOSURE_FACTORIES[r.closure_module]},
                 anchor_choice=r.closure_module),
    ]


def build_astronomy_pressurised_module_door(
    config: AstronomyPressurisedModuleDoorConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="astronomy_pressurised_module_door", assets=assets)
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


def build_seeded_astronomy_pressurised_module_door(seed: int) -> ArticulatedObject:
    return build_astronomy_pressurised_module_door(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("shell_aperture", r.aperture_form),
        ("closure", r.closure_module),
        ("locking_control", r.locking_control),
        ("cover_count", f"covers_{r.cover_count}"),
        ("bolt_count", f"bolts_{r.bolt_count}"),
        ("dog_count", f"dogs_{r.dog_count}"),
        ("spoke_count", f"spokes_{r.spoke_count}"),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedDoorConfig) -> None:
    parts = {p.name for p in model.parts}

    def _ov(pa: str, pb: str, *, elem_a: str, elem_b: str, reason: str) -> None:
        if pa in parts and pb in parts:
            ctx.allow_overlap(model.get_part(pa), model.get_part(pb),
                              elem_a=elem_a, elem_b=elem_b, reason=reason)

    # Handwheel shaft hub seated through the lid / leaf disc.
    if "hatch_lid" in parts:
        disc_elem = "lid_dome" if r.closure_module == "domed_swing_lid" else "lid_disc"
        _ov("hatch_lid", "lock_handwheel", elem_a=disc_elem, elem_b="wheel_hub",
            reason="The handwheel shaft hub is seated through the lid.")
    if "hatch_leaf_0" in parts:
        _ov("hatch_leaf_0", "lock_handwheel", elem_a="leaf_disc_0", elem_b="wheel_hub",
            reason="The handwheel shaft hub is seated through leaf 0 disc.")
        _ov("hatch_leaf_0", "lock_handwheel", elem_a="leaf_step_0", elem_b="wheel_hub",
            reason="The handwheel shaft hub is seated through leaf 0 raised step.")
        _ov("hatch_leaf_0", "lock_handwheel", elem_a="leaf_seal_0", elem_b="wheel_hub",
            reason="The handwheel shaft hub passes through leaf 0 seal face.")

    # Swing hinge: captured pin inside the lid lugs; strap between bracket lugs.
    if r.closure_module in (
        "single_swing_lid",
        "reinforced_swing_lid",
        "domed_swing_lid",
    ) and "hatch_lid" in parts:
        for k in range(2):
            _ov("airlock_shell", "hatch_lid", elem_a="hinge_pin", elem_b=f"lid_hinge_lug_{k}",
                reason="The hinge pin is captured inside the lid hinge lugs.")
            _ov("airlock_shell", "hatch_lid", elem_a=f"hinge_bracket_lug_{k}", elem_b="hinge_strap",
                reason="The lid hinge strap nests between the bracket lugs at the pin.")
        _ov("airlock_shell", "hatch_lid", elem_a="hinge_pin", elem_b="hinge_strap",
            reason="The lid hinge strap wraps the captured hinge pin.")

    # Double leaf: each hinge lug wraps its bracket post + the captured hinge pin.
    if r.closure_module == "double_leaf":
        for i in range(2):
            for k in range(2):
                _ov("airlock_shell", f"hatch_leaf_{i}", elem_a=f"leaf_bracket_{i}_{k}",
                    elem_b=f"leaf_hinge_lug_{i}_{k}",
                    reason=f"Leaf {i} hinge lug wraps the bracket post on the collar rim.")
                _ov("airlock_shell", f"hatch_leaf_{i}", elem_a=f"leaf_pin_{i}",
                    elem_b=f"leaf_hinge_lug_{i}_{k}",
                    reason=f"Leaf {i} hinge lug is captured on the hinge pin.")
            _ov("airlock_shell", f"hatch_leaf_{i}", elem_a=f"leaf_pin_{i}", elem_b=f"leaf_disc_{i}",
                reason=f"Leaf {i} hinge pin runs through the leaf knuckle at the curved apex.")
            _ov("airlock_shell", f"hatch_leaf_{i}", elem_a=f"leaf_pin_{i}", elem_b=f"leaf_hinge_strap_{i}",
                reason=f"Leaf {i} hinge strap wraps the captured hinge pin.")

    # Debris covers: hinge boss + pin captured in the cover lugs / panel root.
    for i in range(r.cover_count):
        child = f"debris_cover_{i}"
        _ov("airlock_shell", child, elem_a=f"cover_boss_{i}", elem_b="panel",
            reason="Debris cover panel root pivots over the shell hinge boss.")
        _ov("airlock_shell", child, elem_a=f"cover_boss_{i}", elem_b="hinge_pin",
            reason="Debris cover hinge pin is captured on the shell hinge boss.")
        for k in range(2):
            _ov("airlock_shell", child, elem_a=f"cover_boss_{i}", elem_b=f"lug_{k}",
                reason="Debris cover hinge lug is captured on the shell hinge boss.")

def _center(aabb):
    if aabb is None:
        return None
    return tuple((aabb[0][i] + aabb[1][i]) / 2.0 for i in range(3))


def _expect_closure(ctx: TestContext, model: ArticulatedObject, r: ResolvedDoorConfig) -> None:
    shell = model.get_part("airlock_shell")

    # collar identity present
    collar = ctx.part_element_world_aabb(shell, elem="hatch_collar")
    ctx.check("raised hatch collar rings the opening", collar is not None and collar[1][2] > 1.2,
              details=f"collar={collar}")
    seal = ctx.part_element_world_aabb(shell, elem="seal_ring")
    ctx.check("tan pressure seal caps the collar",
              seal is not None and abs(seal[1][2] - SEAL_TOP) < 0.02, details=f"seal={seal}")
    strikes = [v for v in shell.visuals if v.name and v.name.startswith("latch_strike_")]
    expected_strikes = 8 if r.aperture_form == "square_aperture" else r.dog_count
    ctx.check("strike plate count matches dog_count", len(strikes) == expected_strikes,
              details=f"strikes={len(strikes)} expected={expected_strikes}")

    if r.closure_module in (
        "single_swing_lid",
        "reinforced_swing_lid",
        "domed_swing_lid",
    ):
        lid = model.get_part("hatch_lid")
        hinge = model.get_articulation("hatch_hinge")
        ctx.check("hatch hinge is revolute closing through -lid_open",
                  hinge.articulation_type == ArticulationType.REVOLUTE
                  and hinge.motion_limits is not None
                  and abs(hinge.motion_limits.lower + r.lid_open) < 1e-6,
                  details=str(hinge.motion_limits))
        disc_elem = "lid_dome" if r.closure_module == "domed_swing_lid" else "lid_disc"
        # closed pose: lid becomes concentric over the opening.
        with ctx.pose({hinge: -r.lid_open}):
            closed = ctx.part_element_world_aabb(lid, elem=disc_elem)
        lc = _center(closed)
        ctx.check("closed lid covers the opening concentrically",
                  lc is not None and math.hypot(lc[0], lc[1]) < 0.08, details=f"closed_center={lc}")
        dogs = [v for v in lid.visuals if v.name and v.name.startswith("latch_dog_")]
        ctx.check("lid dog count matches dog_count",
                  len(dogs) == (8 if r.aperture_form == "square_aperture" else r.dog_count),
                  details=str(len(dogs)))

    elif r.closure_module == "double_leaf":
        leaf0 = model.get_part("hatch_leaf_0")
        leaf1 = model.get_part("hatch_leaf_1")
        h0 = model.get_articulation("leaf_hinge_0")
        h1 = model.get_articulation("leaf_hinge_1")
        ctx.check("both leaf hinges revolute open outward",
                  h0.articulation_type == ArticulationType.REVOLUTE
                  and h1.articulation_type == ArticulationType.REVOLUTE
                  and h0.motion_limits.lower == 0.0 and h0.motion_limits.upper > 1.4,
                  details=f"{h0.motion_limits}, {h1.motion_limits}")
        # closed: leaves meet over the opening; open: free edges lift above seal.
        d0_rest = ctx.part_element_world_aabb(leaf0, elem="leaf_disc_0")
        with ctx.pose({h0: r.leaf_open, h1: r.leaf_open}):
            d0_open = ctx.part_element_world_aabb(leaf0, elem="leaf_disc_0")
            d1_open = ctx.part_element_world_aabb(leaf1, elem="leaf_disc_1")
        ctx.check("leaf 0 closed covers +X half of the opening",
                  d0_rest is not None and d0_rest[1][0] > 0.25 and d0_rest[1][2] > SEAL_TOP,
                  details=f"d0_rest={d0_rest}")
        ctx.check("leaf 0 opens (free edge lifts off the seal)",
                  d0_open is not None and d0_open[1][2] > SEAL_TOP + 0.3, details=f"d0_open={d0_open}")
        ctx.check("leaf 1 opens (free edge lifts off the seal)",
                  d1_open is not None and d1_open[1][2] > SEAL_TOP + 0.3, details=f"d1_open={d1_open}")

def _expect_handwheel(ctx: TestContext, model: ArticulatedObject) -> None:
    wheel = model.get_part("lock_handwheel")
    spin = model.get_articulation("handwheel_spin")
    ctx.check("handwheel spins (revolute)", spin.articulation_type == ArticulationType.REVOLUTE)
    rest = ctx.part_element_world_aabb(wheel, elem="wheel_spoke_0")
    with ctx.pose({spin: 1.0}):
        turned = ctx.part_element_world_aabb(wheel, elem="wheel_spoke_0")
    # The spoke reorients as the wheel spins; the lid may itself be rotated open,
    # so measure the largest AABB-width change over ALL axes (not just x).
    dims_changed = rest is not None and turned is not None and max(
        abs((rest[1][i] - rest[0][i]) - (turned[1][i] - turned[0][i])) for i in range(3)
    ) > 0.05
    ctx.check("turning the handwheel sweeps the spokes", dims_changed,
              details=f"rest={rest}, turned={turned}")


def _expect_covers(ctx: TestContext, model: ArticulatedObject, r: ResolvedDoorConfig) -> None:
    if r.cover_count <= 0:
        return
    covers = [model.get_part(f"debris_cover_{i}") for i in range(r.cover_count)]
    ctx.check("debris cover ring present", all(c is not None for c in covers),
              details=f"n={r.cover_count}")
    hinge0 = model.get_articulation("cover_hinge_0")
    ctx.check("cover hinges revolute", hinge0.articulation_type == ArticulationType.REVOLUTE)
    rest = ctx.part_element_world_aabb(covers[0], elem="panel")
    with ctx.pose({hinge0: r.cover_open}):
        opened = ctx.part_element_world_aabb(covers[0], elem="panel")
    rc = _center(rest)[2] if rest else 0.0
    oc = _center(opened)[2] if opened else 0.0
    ctx.check("cover swings up off the hull", oc > rc + 0.04, details=f"rest_z={rc:.3f} open_z={oc:.3f}")


def run_astronomy_pressurised_module_door_tests(
    model: ArticulatedObject,
    config: AstronomyPressurisedModuleDoorConfig,
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

    _expect_closure(ctx, model, r)
    _expect_handwheel(ctx, model)
    _expect_covers(ctx, model, r)

    # Rule 5: dynamic collision across sampled joint poses.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "AstronomyPressurisedModuleDoorConfig",
    "ResolvedDoorConfig",
    "ApertureForm",
    "ClosureModule",
    "DoorPalette",
    "build_astronomy_pressurised_module_door",
    "build_seeded_astronomy_pressurised_module_door",
    "config_from_seed",
    "resolve_config",
    "run_astronomy_pressurised_module_door_tests",
    "slot_choices_for_seed",
]
