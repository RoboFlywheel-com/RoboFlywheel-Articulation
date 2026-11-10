# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for high-arc gooseneck (pre-rinse) kitchen faucets.

Derived from 62 five-star sources (2 parents + 60 converged copies) — two real
families merged:
  - parent A (brushed-gold single-hole)  : tapered column + side mixer lever +
    2-stage pull-down spray (PRISMATIC + Mimic) + touch display + dial knob.
  - parent B (gloss-black monobloc)      : cylindrical column + chrome base +
    horizontal cross-tube valve (dual pin levers) + fixed aerator spout.

Fixed identity backbone (NOT a slot): a tall inverted-U swan-neck gooseneck built
as a genuine SWEPT curved tube (riser -> smooth half-sine arch -> drop leg), apex
in [0.36, 0.50] m, reach in [0.12, 0.20] m, swivelling about the vertical column
axis (REVOLUTE, +Z). The arch is a curve sweep (mesh tube along a smooth 3D path)
— never downgraded to stacked straight Cylinders (AUTHORING.md §A Rule 3).

Topology slots (18 distinct cells = 3 handle x 2 outlet x 3 control):
  Slot A handle_form : side_lever (N in {1,2}) | cross_tube (N == 2)
  Slot B outlet_head : pull_down_spray (2 PRISMATIC + Mimic) | fixed_aerator (no joint)
  Slot C control     : touch_dial (REVOLUTE +Y) | flow_knob (REVOLUTE +X) | manual_none

Per-seed visual diversity (low topology ceiling -> this carries non-repetition):
  - palette_style x5 drives every material.
  - 4 appearance sub-axes (gooseneck_surface / outlet_head_profile / grip_texture /
    base_trim), each weighted rng.choice; pure parent.visual / surface / static
    weld decor — NO new joints, NO new part nodes, NOT counted in topology.
  - continuous arc params (riser / arc_radius -> reach / arc_aspect -> arc height /
    tube radius / tube taper) decouple arc height from arc width: semicircle <->
    pointed gothic arch <-> flat arch, sampled wide under apex/reach constraints.

Coordinate convention: +Z up, deck plane at z=0, reach (toward sink) along +X.
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    KnobGeometry,
    KnobGrip,
    MatingContract,
    MeshGeometry,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot enums + appearance sub-axis enums + palette
# --------------------------------------------------------------------------- #
HandleForm = Literal["side_lever", "cross_tube"]
OutletHead = Literal["pull_down_spray", "fixed_aerator"]
Control = Literal["touch_dial", "flow_knob", "manual_none"]
ColumnForm = Literal["tapered_cone", "cylindrical_disc"]
GooseneckSurface = Literal["smooth", "pre_rinse_spring", "ribbed_sleeve"]
OutletProfile = Literal["smooth_cone", "ribbed_barrel", "stepped_cylinder"]
GripTexture = Literal["fluted", "ribbed", "smooth"]
BaseTrim = Literal["none", "collar_ring", "escutcheon"]
PaletteStyle = Literal[
    "brushed_gold",
    "gloss_black",
    "polished_chrome",
    "brushed_stainless",
    "matte_gunmetal",
]

HANDLE_FORMS: tuple[HandleForm, ...] = ("side_lever", "cross_tube")
OUTLET_HEADS: tuple[OutletHead, ...] = ("pull_down_spray", "fixed_aerator")
CONTROLS: tuple[Control, ...] = ("touch_dial", "flow_knob", "manual_none")
GOOSENECK_SURFACES: tuple[GooseneckSurface, ...] = ("smooth", "pre_rinse_spring", "ribbed_sleeve")
OUTLET_PROFILES: tuple[OutletProfile, ...] = ("smooth_cone", "ribbed_barrel", "stepped_cylinder")
GRIP_TEXTURES: tuple[GripTexture, ...] = ("fluted", "ribbed", "smooth")
BASE_TRIMS: tuple[BaseTrim, ...] = ("none", "collar_ring", "escutcheon")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brushed_gold",
    "gloss_black",
    "polished_chrome",
    "brushed_stainless",
    "matte_gunmetal",
)

# Sampling weights (spec: defaults highest-frequency, real-sample-backed tails).
LEVER_N_WEIGHTS = (0.6, 0.4)  # side_lever: N=1 (single mixer) common, N=2 long tail
SURFACE_WEIGHTS = (0.55, 0.25, 0.20)  # smooth dominant
PROFILE_WEIGHTS = (0.50, 0.30, 0.20)
GRIP_WEIGHTS = (0.50, 0.25, 0.25)  # fluted dominant
TRIM_WEIGHTS = (0.50, 0.25, 0.25)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "brushed_gold": {
        "body": (0.83, 0.69, 0.36, 1.0),
        "accent": (0.91, 0.80, 0.48, 1.0),
        "dark": (0.07, 0.07, 0.08, 1.0),
        "hot": (0.86, 0.22, 0.18, 1.0),
        "cold": (0.20, 0.46, 0.86, 1.0),
    },
    "gloss_black": {
        "body": (0.05, 0.05, 0.06, 1.0),
        "accent": (0.13, 0.13, 0.15, 1.0),
        "dark": (0.02, 0.02, 0.02, 1.0),
        "hot": (0.86, 0.22, 0.18, 1.0),
        "cold": (0.20, 0.46, 0.86, 1.0),
    },
    "polished_chrome": {
        "body": (0.80, 0.82, 0.85, 1.0),
        "accent": (0.90, 0.92, 0.95, 1.0),
        "dark": (0.10, 0.10, 0.12, 1.0),
        "hot": (0.86, 0.22, 0.18, 1.0),
        "cold": (0.20, 0.46, 0.86, 1.0),
    },
    "brushed_stainless": {
        "body": (0.66, 0.67, 0.66, 1.0),
        "accent": (0.76, 0.77, 0.76, 1.0),
        "dark": (0.12, 0.12, 0.13, 1.0),
        "hot": (0.86, 0.22, 0.18, 1.0),
        "cold": (0.20, 0.46, 0.86, 1.0),
    },
    "matte_gunmetal": {
        "body": (0.30, 0.32, 0.34, 1.0),
        "accent": (0.42, 0.44, 0.46, 1.0),
        "dark": (0.08, 0.08, 0.09, 1.0),
        "hot": (0.86, 0.22, 0.18, 1.0),
        "cold": (0.20, 0.46, 0.86, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Base real-world dimensions (meters). Nominal apex ~ 0.386 m (mid identity band).
# --------------------------------------------------------------------------- #
COLUMN_R = 0.017          # column shaft radius
COLUMN_H = 0.200          # nominal column height -> swivel collar z
DECK_R = 0.030            # base flange radius
DECK_H = 0.010
COLLAR_R = 0.020          # swivel collar radius
COLLAR_H = 0.014
TUBE_R_BASE = 0.011       # gooseneck tube radius
ARC_R = 0.075             # base arc radius -> reach = 2*ARC_R nominal 0.15
RISER = 0.100             # straight riser segment above collar
DROP_LEG = 0.055          # gooseneck drop-leg length

APEX_MIN = 0.36
APEX_MAX = 0.50
REACH_MIN = 0.12
REACH_MAX = 0.20
AERATOR_INNER = 0.0045    # outlet bore inner radius (taper floor)
WALL_T = 0.0018

# Handle hardware.
LEVER_BOSS_R = 0.011
LEVER_BOSS_LEN = 0.016
PIN_LEN = 0.050
PIN_R = 0.0045
LEVER_CAP_D = 0.016       # lever-end knob DIAMETER
VALVE_Y = 0.016           # side_lever N=2 half-spacing (base)
CROSS_HALF = 0.050        # cross_tube half-length (base)
CROSS_R = 0.012           # cross_tube radius
CROSS_CAP_R = 0.014       # cross_tube end cap radius
LEVER_RANGE = (math.radians(-90.0), math.radians(45.0))  # vertical <-> forward

# Control hardware.
POD_R = 0.012
POD_LEN = 0.018
DIAL_D = 0.026            # touch dial DIAMETER
DIAL_H = 0.012
DISPLAY = (0.006, 0.020, 0.026)  # touch display box (x,y,z)
KNOB_D = 0.024            # flow knob DIAMETER
KNOB_H = 0.014
KNOB_BOSS_R = 0.009
KNOB_BOSS_LEN = 0.010
CTRL_RANGE = math.radians(135.0)
SWIVEL_RANGE = math.radians(100.0)

# Pull-down spray.
HOSE_R = 0.0085
HOSE_LEN = 0.048
HEAD_LEN = 0.052
HEAD_R = 0.013
STAGE_TRAVEL = 0.060     # per-stage prismatic travel (base); total = 2 x stage


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class HighArcGooseneckFaucetConfig:
    handle_form: HandleForm = "side_lever"
    handle_count: int = 1
    outlet_head: OutletHead = "fixed_aerator"
    control: Control = "manual_none"
    palette_style: PaletteStyle = "brushed_gold"
    gooseneck_surface: GooseneckSurface = "smooth"
    outlet_head_profile: OutletProfile = "smooth_cone"
    grip_texture: GripTexture = "fluted"
    base_trim: BaseTrim = "none"
    # continuous scales
    column_height_scale: float = 1.0
    riser_height_scale: float = 1.0
    arc_radius_scale: float = 1.0
    arc_aspect_scale: float = 1.0
    tube_radius_scale: float = 1.0
    tube_taper_ratio: float = 1.0
    spray_head_size_scale: float = 1.0
    handle_length_scale: float = 1.0
    handle_radius_scale: float = 1.0
    control_size_scale: float = 1.0
    valve_spacing_scale: float = 1.0
    pulldown_travel_scale: float = 1.0
    name: str = "high_arc_gooseneck_faucet"


@dataclass(frozen=True)
class ResolvedHighArcGooseneckFaucetConfig:
    handle_form: HandleForm
    handle_count: int
    outlet_head: OutletHead
    control: Control
    column_form: ColumnForm
    palette_style: PaletteStyle
    gooseneck_surface: GooseneckSurface
    outlet_head_profile: OutletProfile
    grip_texture: GripTexture
    base_trim: BaseTrim
    # concrete geometry
    swivel_z: float
    riser: float
    arc_reach: float
    arc_height: float
    tube_r: float
    outlet_tube_r: float
    apex_world: float
    drop_leg: float
    spray_head_scale: float
    handle_len: float
    handle_r: float
    control_scale: float
    valve_y: float
    cross_half: float
    stage_travel: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# --------------------------------------------------------------------------- #
# Procedural sampling
# --------------------------------------------------------------------------- #
def config_from_seed(seed: int) -> HighArcGooseneckFaucetConfig:
    rng = random.Random(seed)

    # (1) handle_form; (2) conditional handle_count
    handle_form: HandleForm = rng.choice(HANDLE_FORMS)
    if handle_form == "cross_tube":
        handle_count = 2  # horizontal cross-tube is inherently a dual valve body
    else:
        handle_count = rng.choices((1, 2), weights=LEVER_N_WEIGHTS, k=1)[0]

    # (3) outlet_head; (4) control
    outlet_head: OutletHead = rng.choice(OUTLET_HEADS)
    control: Control = rng.choice(CONTROLS)

    # (6) palette
    palette_style: PaletteStyle = rng.choice(PALETTE_STYLES)

    # (7) independent continuous scales
    column_height_scale = rng.uniform(0.78, 1.28)
    riser_height_scale = rng.uniform(0.72, 1.35)
    arc_radius_scale = rng.uniform(0.80, 1.32)
    arc_aspect_scale = rng.uniform(0.82, 1.32)
    tube_radius_scale = rng.uniform(0.82, 1.22)
    tube_taper_ratio = rng.uniform(0.70, 1.00)
    spray_head_size_scale = rng.uniform(0.82, 1.25)
    handle_length_scale = rng.uniform(0.80, 1.28)
    handle_radius_scale = rng.uniform(0.85, 1.22)
    control_size_scale = rng.uniform(0.85, 1.22)
    valve_spacing_scale = rng.uniform(0.80, 1.20)
    pulldown_travel_scale = rng.uniform(0.78, 1.25)

    # (8) appearance sub-axes (after sizes; weighted, defaults dominant)
    gooseneck_surface: GooseneckSurface = rng.choices(
        GOOSENECK_SURFACES, weights=SURFACE_WEIGHTS, k=1
    )[0]
    outlet_head_profile: OutletProfile = rng.choices(
        OUTLET_PROFILES, weights=PROFILE_WEIGHTS, k=1
    )[0]
    grip_texture: GripTexture = rng.choices(GRIP_TEXTURES, weights=GRIP_WEIGHTS, k=1)[0]
    base_trim: BaseTrim = rng.choices(BASE_TRIMS, weights=TRIM_WEIGHTS, k=1)[0]

    return HighArcGooseneckFaucetConfig(
        handle_form=handle_form,
        handle_count=handle_count,
        outlet_head=outlet_head,
        control=control,
        palette_style=palette_style,
        gooseneck_surface=gooseneck_surface,
        outlet_head_profile=outlet_head_profile,
        grip_texture=grip_texture,
        base_trim=base_trim,
        column_height_scale=column_height_scale,
        riser_height_scale=riser_height_scale,
        arc_radius_scale=arc_radius_scale,
        arc_aspect_scale=arc_aspect_scale,
        tube_radius_scale=tube_radius_scale,
        tube_taper_ratio=tube_taper_ratio,
        spray_head_size_scale=spray_head_size_scale,
        handle_length_scale=handle_length_scale,
        handle_radius_scale=handle_radius_scale,
        control_size_scale=control_size_scale,
        valve_spacing_scale=valve_spacing_scale,
        pulldown_travel_scale=pulldown_travel_scale,
    )


def resolve_config(
    config: HighArcGooseneckFaucetConfig,
) -> ResolvedHighArcGooseneckFaucetConfig:
    # (5) derive column_form from handle_form (cross => disc; lever => tapered)
    column_form: ColumnForm = (
        "cylindrical_disc" if config.handle_form == "cross_tube" else "tapered_cone"
    )

    # compatibility fallback: cross_tube must be N=2
    handle_count = config.handle_count
    if config.handle_form == "cross_tube":
        handle_count = 2
    handle_count = int(_clamp(handle_count, 1, 2))

    # independent sizes
    swivel_z = COLUMN_H * _clamp(config.column_height_scale, 0.78, 1.28)
    riser = RISER * _clamp(config.riser_height_scale, 0.72, 1.35)
    arc_reach = _clamp(2.0 * ARC_R * _clamp(config.arc_radius_scale, 0.80, 1.32), REACH_MIN, REACH_MAX)
    arc_height = ARC_R * _clamp(config.arc_aspect_scale, 0.82, 1.32)
    tube_r = TUBE_R_BASE * _clamp(config.tube_radius_scale, 0.82, 1.22)

    # apex equation + inequality projection (joint joint-scale of the height stack)
    apex = swivel_z + riser + arc_height + tube_r
    if apex < APEX_MIN or apex > APEX_MAX:
        target = _clamp(apex, APEX_MIN, APEX_MAX)
        adjustable = swivel_z + riser + arc_height
        if adjustable > 1e-6:
            f = (target - tube_r) / adjustable
            f = max(f, 0.1)
            swivel_z *= f
            riser *= f
            arc_height *= f
    apex_world = swivel_z + riser + arc_height + tube_r

    # outlet taper floor (bore must not degenerate)
    outlet_tube_r = tube_r * _clamp(config.tube_taper_ratio, 0.70, 1.00)
    outlet_tube_r = max(outlet_tube_r, AERATOR_INNER + WALL_T)

    # drop leg clamped so the outlet stays above deck
    drop_leg = min(DROP_LEG, (swivel_z + riser) - 0.16)
    drop_leg = max(drop_leg, 0.030)

    # conditional sizes
    spray_head_scale = _clamp(config.spray_head_size_scale, 0.82, 1.25)
    handle_len = PIN_LEN * _clamp(config.handle_length_scale, 0.80, 1.28)
    handle_r = PIN_R * _clamp(config.handle_radius_scale, 0.85, 1.22)
    control_scale = _clamp(config.control_size_scale, 0.85, 1.22)
    # dual side-lever pivots seat just OUTBOARD of the shaft surface (so the
    # uprising pin is not buried inside the column).
    valve_y = (COLUMN_R + 0.008) * _clamp(config.valve_spacing_scale, 0.80, 1.20)
    cross_half = CROSS_HALF * _clamp(config.valve_spacing_scale, 0.80, 1.20)
    stage_travel = STAGE_TRAVEL * _clamp(config.pulldown_travel_scale, 0.78, 1.25)

    return ResolvedHighArcGooseneckFaucetConfig(
        handle_form=config.handle_form,
        handle_count=handle_count,
        outlet_head=config.outlet_head,
        control=config.control,
        column_form=column_form,
        palette_style=config.palette_style,
        gooseneck_surface=config.gooseneck_surface,
        outlet_head_profile=config.outlet_head_profile,
        grip_texture=config.grip_texture,
        base_trim=config.base_trim,
        swivel_z=swivel_z,
        riser=riser,
        arc_reach=arc_reach,
        arc_height=arc_height,
        tube_r=tube_r,
        outlet_tube_r=outlet_tube_r,
        apex_world=apex_world,
        drop_leg=drop_leg,
        spray_head_scale=spray_head_scale,
        handle_len=handle_len,
        handle_r=handle_r,
        control_scale=control_scale,
        valve_y=valve_y,
        cross_half=cross_half,
        stage_travel=stage_travel,
        name=config.name,
    )


# --------------------------------------------------------------------------- #
# Slot choices (topology fingerprint — appearance sub-axes intentionally omitted)
# --------------------------------------------------------------------------- #
def slot_choices_for_config(
    r: ResolvedHighArcGooseneckFaucetConfig,
) -> tuple[tuple[str, str], ...]:
    return (
        ("handle_form", r.handle_form),
        ("handle_count", str(r.handle_count)),
        ("outlet_head", r.outlet_head),
        ("control", r.control),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Mesh helpers (swept tubes, rings, boxes) — sweeps are real curved paths.
# --------------------------------------------------------------------------- #
def _unit(v):
    length = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if length < 1e-9:
        return (0.0, 0.0, 1.0)
    return (v[0] / length, v[1] / length, v[2] / length)


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _combine(*geometries):
    vertices: list = []
    faces: list = []
    for geom in geometries:
        offset = len(vertices)
        vertices.extend(geom.vertices)
        faces.extend((a + offset, b + offset, c + offset) for a, b, c in geom.faces)
    return MeshGeometry(vertices=vertices, faces=faces)


def _translate(geom, dx, dy, dz):
    return MeshGeometry(
        vertices=[(x + dx, y + dy, z + dz) for (x, y, z) in geom.vertices],
        faces=list(geom.faces),
    )


def _variable_tube(points, outer_radii, inner_radii, segments=22):
    """Thin-wall tube mesh that can taper smoothly along a 3D path."""
    vertices: list = []
    faces: list = []
    rings = []
    n = len(points)
    for i, p in enumerate(points):
        if i == 0:
            tangent = (points[1][0] - p[0], points[1][1] - p[1], points[1][2] - p[2])
        elif i == n - 1:
            tangent = (p[0] - points[i - 1][0], p[1] - points[i - 1][1], p[2] - points[i - 1][2])
        else:
            tangent = (
                points[i + 1][0] - points[i - 1][0],
                points[i + 1][1] - points[i - 1][1],
                points[i + 1][2] - points[i - 1][2],
            )
        tangent = _unit(tangent)
        u = (1.0, 0.0, 0.0)
        if abs(tangent[0]) > 0.92:
            u = (0.0, 1.0, 0.0)
        v = _unit(_cross(tangent, u))
        u = _unit(_cross(v, tangent))
        outer = []
        inner = []
        for k in range(segments):
            a = 2.0 * math.pi * k / segments
            ca = math.cos(a)
            sa = math.sin(a)
            orad = outer_radii[i]
            irad = inner_radii[i]
            outer.append(len(vertices))
            vertices.append((
                p[0] + orad * (u[0] * ca + v[0] * sa),
                p[1] + orad * (u[1] * ca + v[1] * sa),
                p[2] + orad * (u[2] * ca + v[2] * sa),
            ))
            inner.append(len(vertices))
            vertices.append((
                p[0] + irad * (u[0] * ca + v[0] * sa),
                p[1] + irad * (u[1] * ca + v[1] * sa),
                p[2] + irad * (u[2] * ca + v[2] * sa),
            ))
        rings.append((outer, inner))
    for i in range(n - 1):
        outer0, inner0 = rings[i]
        outer1, inner1 = rings[i + 1]
        for k in range(segments):
            j = (k + 1) % segments
            faces.append((outer0[k], outer1[k], outer1[j]))
            faces.append((outer0[k], outer1[j], outer0[j]))
            faces.append((inner0[k], inner1[j], inner1[k]))
            faces.append((inner0[k], inner0[j], inner1[j]))
    for ring_index in (0, n - 1):
        outer, inner = rings[ring_index]
        for k in range(segments):
            j = (k + 1) % segments
            if ring_index == 0:
                faces.append((outer[k], inner[j], inner[k]))
                faces.append((outer[k], outer[j], inner[j]))
            else:
                faces.append((outer[k], inner[k], inner[j]))
                faces.append((outer[k], inner[j], outer[j]))
    return MeshGeometry(vertices=vertices, faces=faces)


def _tube(points, outer_radius, inner_radius=None, segments=22):
    inner_radius = inner_radius if inner_radius is not None else outer_radius * 0.55
    return _variable_tube(
        points,
        [outer_radius] * len(points),
        [inner_radius] * len(points),
        segments=segments,
    )


def _solid_tube(points, radii, segments=18):
    """Solid (no bore) swept tube — for thin wires / pins."""
    return _variable_tube(
        points,
        list(radii),
        [max(r * 0.001, 1e-5) for r in radii],
        segments=segments,
    )


def _annular(center, outer_radius, inner_radius, height, segments=28):
    cx, cy, z0 = center
    z1 = z0 + height
    vertices = []
    for z in (z0, z1):
        for r in (outer_radius, inner_radius):
            for k in range(segments):
                a = 2.0 * math.pi * k / segments
                vertices.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    faces = []
    bo, bi, to, ti = 0, segments, 2 * segments, 3 * segments
    for k in range(segments):
        j = (k + 1) % segments
        faces.append((bo + k, bo + j, to + j))
        faces.append((bo + k, to + j, to + k))
        faces.append((bi + k, ti + j, bi + j))
        faces.append((bi + k, ti + k, ti + j))
        faces.append((to + k, to + j, ti + j))
        faces.append((to + k, ti + j, ti + k))
        faces.append((bo + k, bi + j, bo + j))
        faces.append((bo + k, bi + k, bi + j))
    return MeshGeometry(vertices=vertices, faces=faces)


def _disc(center, radius, height, segments=28):
    return _annular(center, radius, max(radius * 0.0008, 1e-5), height, segments=segments)


def _cyl_along(p0, p1, radius, segments=18):
    """Solid cylinder between two 3D points (for bosses / cross tube)."""
    return _solid_tube([p0, p1], [radius, radius], segments=segments)


# --------------------------------------------------------------------------- #
# Gooseneck (fixed identity) — swept inverted-U swan neck.
# --------------------------------------------------------------------------- #
def _gooseneck_path(r: ResolvedHighArcGooseneckFaucetConfig):
    """Path points in spout-local frame (origin = swivel point at z=0)."""
    pts = []
    n_riser = 5
    for i in range(n_riser + 1):
        pts.append((0.0, 0.0, r.riser * i / n_riser))
    riser_pts = len(pts)
    n_arc = 26
    for i in range(1, n_arc + 1):
        t = i / n_arc
        x = r.arc_reach * (0.5 - 0.5 * math.cos(math.pi * t))
        z = r.riser + r.arc_height * math.sin(math.pi * t)
        pts.append((x, 0.0, z))
    n_drop = 4
    for i in range(1, n_drop + 1):
        t = i / n_drop
        pts.append((r.arc_reach, 0.0, r.riser - r.drop_leg * t))
    return pts, riser_pts


def _gooseneck_tube(r: ResolvedHighArcGooseneckFaucetConfig):
    pts, riser_pts = _gooseneck_path(r)
    n = len(pts)
    n_drop = 4
    outer_radii = []
    for i in range(n):
        if i >= n - n_drop:
            # taper down the drop leg toward the outlet
            t = (i - (n - n_drop - 1)) / n_drop
            outer_radii.append(r.tube_r + (r.outlet_tube_r - r.tube_r) * _clamp(t, 0.0, 1.0))
        else:
            outer_radii.append(r.tube_r)
    inner_radii = [max(rad - WALL_T, rad * 0.45) for rad in outer_radii]
    return _variable_tube(pts, outer_radii, inner_radii, segments=24), pts


def _pre_rinse_spring(r: ResolvedHighArcGooseneckFaucetConfig):
    """Helical pre-rinse spring wound around the straight riser segment.

    coil_r embeds slightly into the main tube so the wire is connected (no
    floating island); pure spout visual that swivels with the gooseneck.
    """
    wire_r = 0.0019
    coil_r = r.tube_r + wire_r * 0.5
    turns = 9
    per_turn = 22
    z0 = r.riser * 0.10
    z1 = r.riser * 0.92
    pts = []
    total = turns * per_turn
    for i in range(total + 1):
        frac = i / total
        ang = 2.0 * math.pi * turns * frac
        z = z0 + (z1 - z0) * frac
        pts.append((coil_r * math.cos(ang), coil_r * math.sin(ang), z))
    return _solid_tube(pts, [wire_r] * len(pts), segments=8)


def _ribbed_sleeve(r: ResolvedHighArcGooseneckFaucetConfig):
    """Threaded sleeve over a riser sub-segment: oscillating radius rings."""
    z0 = r.riser * 0.15
    z1 = r.riser * 0.78
    n = 40
    base_r = r.tube_r + 0.0015
    rib_amp = 0.0018
    pts = []
    orad = []
    for i in range(n + 1):
        t = i / n
        z = z0 + (z1 - z0) * t
        pts.append((0.0, 0.0, z))
        orad.append(base_r + rib_amp * (0.5 + 0.5 * math.cos(2.0 * math.pi * 7.0 * t)))
    irad = [r.tube_r - WALL_T * 0.3 for _ in pts]
    return _variable_tube(pts, orad, irad, segments=22)


def _head_profile_mesh(r: ResolvedHighArcGooseneckFaucetConfig, top_r: float):
    """Outlet head body, built downward from (0,0,0) to (0,0,-head_len)."""
    profile = r.outlet_head_profile
    scale = r.spray_head_scale
    head_len = HEAD_LEN * scale
    base_r = max(HEAD_R * scale, top_r + 0.002)
    n = 14
    pts = []
    orad = []
    for i in range(n + 1):
        t = i / n
        z = -head_len * t
        pts.append((0.0, 0.0, z))
        if profile == "smooth_cone":
            orad.append(top_r + (base_r - top_r) * t)
        elif profile == "ribbed_barrel":
            bulge = base_r * (1.0 + 0.06 * math.sin(math.pi * t))
            rib = 0.0010 * (0.5 + 0.5 * math.cos(2.0 * math.pi * 6.0 * t))
            orad.append(top_r + (bulge - top_r) * min(t * 1.6, 1.0) + rib)
        else:  # stepped_cylinder
            step = base_r if t < 0.45 else base_r * 1.18
            orad.append(top_r + (step - top_r) * min(t * 2.2, 1.0))
    irad = [max(rad - WALL_T, rad * 0.45) for rad in orad]
    body = _variable_tube(pts, orad, irad, segments=22)
    # aerator face disc at the bottom outlet
    tip = (0.0, 0.0, -head_len)
    aer = _annular(tip, orad[-1] * 0.92, AERATOR_INNER, -0.004, segments=22)
    return _combine(body, aer), head_len


# --------------------------------------------------------------------------- #
# Lever / knob caps with grip texture.
# --------------------------------------------------------------------------- #
def _grip_for(texture: GripTexture, count: int, depth: float):
    if texture == "smooth":
        return None
    return KnobGrip(style=texture, count=count, depth=depth, helix_angle_deg=0.0)


def _lever_cap_mesh(r: ResolvedHighArcGooseneckFaucetConfig, diameter: float):
    grip = _grip_for(r.grip_texture, 18, 0.0007)
    geom = KnobGeometry(diameter, diameter * 0.55, body_style="domed", grip=grip)
    return geom


# --------------------------------------------------------------------------- #
# Materials
# --------------------------------------------------------------------------- #
def _materials(model: ArticulatedObject, r: ResolvedHighArcGooseneckFaucetConfig):
    palette = PALETTES[r.palette_style]
    return {
        key: model.material(f"faucet_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }


def _inertial_cyl(radius: float, length: float, mass: float, z_center: float):
    return Inertial.from_geometry(
        Cylinder(radius=max(radius, 0.003), length=max(length, 0.006)),
        mass=mass,
        origin=Origin(xyz=(0.0, 0.0, z_center)),
    )


# --------------------------------------------------------------------------- #
# Column (root) — deck base, shaft, swivel collar, base trim, handle/control bosses.
# --------------------------------------------------------------------------- #
def _build_column(model: ArticulatedObject, r: ResolvedHighArcGooseneckFaucetConfig, mats):
    body = mats["body"]
    accent = mats["accent"]
    dark = mats["dark"]
    hot = mats["hot"]
    cold = mats["cold"]

    column = model.part("faucet_column")

    # deck flange (z 0..DECK_H) overlapping shaft base
    column.visual(
        mesh_from_geometry(_disc((0.0, 0.0, 0.0), DECK_R, DECK_H), "deck_flange"),
        material=accent,
        name="deck_flange", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
    )

    # shaft (tapered_cone vs cylindrical_disc visual; both rise to swivel_z)
    n = 10
    pts = []
    orad = []
    top_r = COLUMN_R * (0.80 if r.column_form == "tapered_cone" else 1.0)
    for i in range(n + 1):
        t = i / n
        pts.append((0.0, 0.0, DECK_H * 0.4 + (r.swivel_z - DECK_H * 0.4) * t))
        if r.column_form == "tapered_cone":
            orad.append(COLUMN_R + (top_r - COLUMN_R) * t)
        else:
            orad.append(COLUMN_R)
    irad = [max(rad - 0.004, 0.002) for rad in orad]
    column.visual(
        mesh_from_geometry(_variable_tube(pts, orad, irad, segments=26), "column_shaft"),
        material=body,
        name="column_shaft", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
    )
    if r.column_form == "cylindrical_disc":
        # chrome base disc characteristic of the monobloc family
        column.visual(
            mesh_from_geometry(_disc((0.0, 0.0, DECK_H), DECK_R * 0.78, 0.006), "base_disc"),
            material=accent,
            name="base_disc", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
        )

    # swivel collar at the top (kissing face for the gooseneck riser)
    column.visual(
        mesh_from_geometry(
            _disc((0.0, 0.0, r.swivel_z - COLLAR_H), COLLAR_R, COLLAR_H), "swivel_collar"
        ),
        material=accent,
        name="swivel_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
    )

    # base trim sub-axis
    if r.base_trim == "collar_ring":
        column.visual(
            mesh_from_geometry(
                _annular((0.0, 0.0, r.swivel_z - COLLAR_H - 0.006), COLLAR_R + 0.004, 0.010, 0.007),
                "collar_ring",
            ),
            material=accent,
            name="collar_ring", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
        )
    elif r.base_trim == "escutcheon":
        column.visual(
            mesh_from_geometry(_disc((0.0, 0.0, 0.0), DECK_R + 0.022, 0.005), "escutcheon"),
            material=accent,
            name="escutcheon", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
        )
        column.visual(
            mesh_from_geometry(_disc((0.0, 0.0, 0.005), DECK_R + 0.008, 0.006), "pedestal_step"),
            material=accent,
            name="pedestal_step", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
        )

    column.inertial = _inertial_cyl(COLUMN_R, r.swivel_z, 1.4, r.swivel_z / 2.0)
    return column


# --------------------------------------------------------------------------- #
# Gooseneck part + swivel + outlet head.
# --------------------------------------------------------------------------- #
def _build_gooseneck(model: ArticulatedObject, r: ResolvedHighArcGooseneckFaucetConfig, mats, column):
    body = mats["body"]
    accent = mats["accent"]

    tube_geom, pts = _gooseneck_tube(r)
    spout = model.part("gooseneck")
    spout.visual(
        mesh_from_geometry(tube_geom, "gooseneck_tube"),
        material=body,
        name="gooseneck_tube", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
    )

    # gooseneck surface sub-axis (welded spout visual, no joint, no new part)
    if r.gooseneck_surface == "pre_rinse_spring":
        spout.visual(
            mesh_from_geometry(_pre_rinse_spring(r), "pre_rinse_spring"),
            material=accent,
            name="pre_rinse_spring", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
        )
    elif r.gooseneck_surface == "ribbed_sleeve":
        spout.visual(
            mesh_from_geometry(_ribbed_sleeve(r), "ribbed_sleeve"),
            material=accent,
            name="ribbed_sleeve", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
        )

    outlet = pts[-1]  # (arc_reach, 0, riser - drop_leg)

    if r.outlet_head == "fixed_aerator":
        head_geom, head_len = _head_profile_mesh(r, r.outlet_tube_r)
        spout.visual(
            mesh_from_geometry(_translate(head_geom, outlet[0], outlet[1], outlet[2]), "outlet_head"),
            material=accent,
            name="outlet_head", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
        )

    spout.inertial = _inertial_cyl(r.tube_r, r.riser + r.arc_height, 0.6, (r.riser + r.arc_height) / 2.0)

    model.articulation(
        "column_to_gooseneck",
        ArticulationType.REVOLUTE,
        parent=column,
        child=spout,
        origin=Origin(xyz=(0.0, 0.0, r.swivel_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=6.0, velocity=1.0, lower=-SWIVEL_RANGE, upper=SWIVEL_RANGE),
        mating=MatingContract(
            parent_face_geometry="swivel_collar",
            parent_face_side="positive_z",
            child_face_geometry="gooseneck_tube",
            child_face_side="negative_z",
            contact_tol=0.005,
        ),
    )
    return spout, outlet


def _build_pull_down(model: ArticulatedObject, r: ResolvedHighArcGooseneckFaucetConfig, mats, spout, outlet):
    body = mats["body"]
    accent = mats["accent"]

    hose_len = HOSE_LEN
    # hose sleeve: built downward from its own origin (top), captured in the drop leg
    hose = model.part("spray_hose")
    hose_pts = [(0.0, 0.0, 0.006), (0.0, 0.0, -hose_len)]
    hose.visual(
        mesh_from_geometry(_tube(hose_pts, HOSE_R, HOSE_R - WALL_T), "spray_hose"),
        material=body,
        name="spray_hose", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
    )
    # coupling collar at the hose top — grips the drop-leg outer wall regardless
    # of taper so the pull-down stays connected to the gooseneck (no float).
    hose.visual(
        mesh_from_geometry(_disc((0.0, 0.0, 0.003), r.tube_r + 0.003, 0.008), "hose_collar"),
        material=accent,
        name="hose_collar", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
    )
    hose.inertial = _inertial_cyl(HOSE_R, hose_len, 0.12, -hose_len / 2.0)

    # spray head: built downward from its own origin (top)
    head = model.part("spray_head")
    head_geom, head_len = _head_profile_mesh(r, HOSE_R * 0.9)
    head.visual(
        mesh_from_geometry(head_geom, "spray_head"),
        material=accent,
        name="spray_head", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
    )
    head.inertial = _inertial_cyl(HEAD_R * r.spray_head_scale, head_len, 0.18, -head_len / 2.0)

    # hose_slide: gooseneck -> hose (PRISMATIC -Z), origin at the outlet point
    model.articulation(
        "hose_slide",
        ArticulationType.PRISMATIC,
        parent=spout,
        child=hose,
        origin=Origin(xyz=(outlet[0], outlet[1], outlet[2])),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=4.0, velocity=0.5, lower=0.0, upper=r.stage_travel),
        mimic=Mimic(joint="spray_pulldown", multiplier=1.0, offset=0.0),
    )
    # spray_pulldown: hose -> head (PRISMATIC -Z), origin at hose bottom (driver)
    model.articulation(
        "spray_pulldown",
        ArticulationType.PRISMATIC,
        parent=hose,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, -hose_len + 0.006)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=4.0, velocity=0.5, lower=0.0, upper=r.stage_travel),
    )
    return hose, head


# --------------------------------------------------------------------------- #
# Slot A: handle (pin levers on bosses / cross tube).
# --------------------------------------------------------------------------- #
def _build_lever(model: ArticulatedObject, r: ResolvedHighArcGooseneckFaucetConfig, mats, name: str):
    """One pin lever part; pivot at its local origin, pin rising +Z."""
    accent = mats["accent"]
    lever = model.part(name)
    # captured stub straddling the pivot (connects into the boss/cross tube)
    lever.visual(
        mesh_from_geometry(
            _cyl_along((0.0, -LEVER_BOSS_LEN * 0.6, 0.0), (0.0, LEVER_BOSS_LEN * 0.6, 0.0), r.handle_r * 1.3),
            "lever_stub",
        ),
        material=accent,
        name="lever_stub", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
    )
    # pin rising +Z
    lever.visual(
        mesh_from_geometry(_cyl_along((0.0, 0.0, 0.0), (0.0, 0.0, r.handle_len), r.handle_r), "lever_pin"),
        material=accent,
        name="lever_pin", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
    )
    # grip cap at the tip
    cap = _lever_cap_mesh(r, LEVER_CAP_D)
    lever.visual(
        mesh_from_geometry(cap, "lever_cap"),
        origin=Origin(xyz=(0.0, 0.0, r.handle_len)),
        material=accent,
        name="lever_cap", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
    )
    lever.inertial = _inertial_cyl(r.handle_r, r.handle_len, 0.06, r.handle_len / 2.0)
    return lever


def _shaft_r_at(r: ResolvedHighArcGooseneckFaucetConfig, z: float) -> float:
    """Outer radius of the tapered/cylindrical column shaft at height z."""
    top_r = COLUMN_R * (0.80 if r.column_form == "tapered_cone" else 1.0)
    z0 = DECK_H * 0.4
    t = _clamp((z - z0) / max(r.swivel_z - z0, 1e-6), 0.0, 1.0)
    return COLUMN_R + (top_r - COLUMN_R) * t


def _min_lever_mount(r: ResolvedHighArcGooseneckFaucetConfig, boss_z: float) -> float:
    """Outboard pivot offset that keeps the lever cap clear of the shaft.

    The tightest pose is the pin vertical (cap directly outboard of the shaft
    axis); use the shaft radius at the boss height (the widest the swept lever
    spans) plus the cap radius plus a visible margin.
    """
    return _shaft_r_at(r, boss_z) + LEVER_CAP_D * 0.5 + 0.004


def _build_handle(model: ArticulatedObject, r: ResolvedHighArcGooseneckFaucetConfig, mats, column):
    accent = mats["accent"]
    dark = mats["dark"]
    # Seat the valve bosses low enough that the upright lever cap clears the
    # swivel collar / collar_ring zone at the rest (vertical) pose.
    boss_z = min(0.52 * r.swivel_z, r.swivel_z - 0.035 - r.handle_len)
    boss_z = max(boss_z, 0.045)
    lever_names: list[str] = []
    pivots: list[str] = []

    if r.handle_form == "cross_tube":
        # horizontal cross tube through the column with matte end caps (shared)
        column.visual(
            mesh_from_geometry(
                _cyl_along((0.0, -r.cross_half, boss_z), (0.0, r.cross_half, boss_z), CROSS_R),
                "cross_tube",
            ),
            material=accent,
            name="cross_tube", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
        )
        for i, sign in enumerate((-1, 1)):
            column.visual(
                mesh_from_geometry(
                    _cyl_along(
                        (0.0, sign * r.cross_half, boss_z),
                        (0.0, sign * (r.cross_half + 0.005), boss_z),
                        CROSS_CAP_R,
                    ),
                    f"valve_end_cap_{i}",
                ),
                material=dark,
                name=f"valve_end_cap_{i}", material_class_id="metal.blackened_gunmetal",
            )
        positions = [(0.0, -r.cross_half, boss_z), (0.0, r.cross_half, boss_z)]
    else:
        # Push the side-lever pivots outboard so the pin + cap clear the tapered
        # shaft with a visible margin across the whole swing (they used to sit at
        # the shaft surface and read as clipping). cross_tube is already clear.
        mount = max(COLUMN_R + LEVER_BOSS_LEN * 0.5, _min_lever_mount(r, boss_z))
        if r.handle_count == 1:
            # single front mixer lever, boss on +X face
            column.visual(
                mesh_from_geometry(
                    _cyl_along((0.0, 0.0, boss_z), (mount, 0.0, boss_z), LEVER_BOSS_R),
                    "valve_boss_0",
                ),
                material=accent,
                name="valve_boss_0", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
            )
            positions = [(mount, 0.0, boss_z)]
        else:
            # dual side levers on +/-Y, bosses reach out to the clearance offset
            positions = []
            valve_y = max(r.valve_y, mount)
            for i, sign in enumerate((-1, 1)):
                by = sign * valve_y
                column.visual(
                    mesh_from_geometry(
                        _cyl_along((0.0, 0.0, boss_z), (0.0, by, boss_z), LEVER_BOSS_R),
                        f"valve_boss_{i}",
                    ),
                    material=accent,
                    name=f"valve_boss_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
                )
                positions.append((0.0, by, boss_z))

    for idx, pos in enumerate(positions):
        name = f"pin_lever_{idx}"
        lever = _build_lever(model, r, mats, name)
        joint = f"lever_pivot_{idx}"
        model.articulation(
            joint,
            ArticulationType.REVOLUTE,
            parent=column,
            child=lever,
            origin=Origin(xyz=pos),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(
                effort=4.0, velocity=1.0, lower=LEVER_RANGE[0], upper=LEVER_RANGE[1]
            ),
        )
        lever_names.append(name)
        pivots.append(joint)
    return lever_names, pivots


# --------------------------------------------------------------------------- #
# Slot C: control.
# --------------------------------------------------------------------------- #
def _build_control(model: ArticulatedObject, r: ResolvedHighArcGooseneckFaucetConfig, mats, column):
    if r.control == "manual_none":
        return None, None

    accent = mats["accent"]
    dark = mats["dark"]
    hot = mats["hot"]
    cold = mats["cold"]
    s = r.control_scale
    ctrl_z = 0.34 * r.swivel_z
    # Dual side-levers occupy BOTH +/-Y valve bosses, so the -Y control (pod/dial
    # or flow knob) shares that axis and interpenetrates the -Y boss at short-
    # column / large-control scale tails. Tuck the control into the clear band
    # between the deck top and the boss bottom, shrinking it only if that band is
    # tight. Same mount axis / joint / pointer -> no spin- or connectivity-test
    # impact.
    if r.handle_form == "side_lever" and r.handle_count == 2:
        boss_z = max(min(0.52 * r.swivel_z, r.swivel_z - 0.035 - r.handle_len), 0.045)
        boss_bottom = boss_z - LEVER_BOSS_R
        margin = 0.003
        gap = boss_bottom - DECK_H
        ctrl_half = max(KNOB_D, DIAL_D) * 0.5 * s
        if 2.0 * (ctrl_half + margin) > gap:
            s = max(s * (gap / 2.0 - margin) / max(ctrl_half, 1e-4), 0.55)
            ctrl_half = max(KNOB_D, DIAL_D) * 0.5 * s
        ctrl_z = min(ctrl_z, boss_bottom - margin - ctrl_half)
        ctrl_z = max(ctrl_z, DECK_H + margin + ctrl_half)

    if r.control == "touch_dial":
        # touch display embedded in the +X front face (protrudes ~3 mm), pod +
        # dial on -Y side (axis Y revolute). Display is the connective anchor;
        # icons overlap its protruding front face.
        disp_x = 0.008
        disp_cx = COLUMN_R - 0.001  # embeds ~5 mm, protrudes ~3 mm
        disp_front = disp_cx + disp_x * 0.5
        column.visual(
            mesh_from_geometry(
                _translate(_box_mesh(disp_x, DISPLAY[1] * s, DISPLAY[2] * s),
                           disp_cx, 0.0, ctrl_z),
                "touch_display",
            ),
            material=dark,
            name="touch_display", material_class_id="tech.control_interface",
        )
        column.visual(
            mesh_from_geometry(
                _translate(_box_mesh(0.003, 0.004 * s, 0.005 * s),
                           disp_front - 0.0008, 0.004 * s, ctrl_z + 0.006 * s),
                "hot_icon",
            ),
            material=hot,
            name="hot_icon", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        column.visual(
            mesh_from_geometry(
                _translate(_box_mesh(0.003, 0.004 * s, 0.005 * s),
                           disp_front - 0.0008, -0.004 * s, ctrl_z + 0.006 * s),
                "cold_icon",
            ),
            material=cold,
            name="cold_icon", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        # control pod (horizontal cylinder along -Y) embedded in the shaft
        pod_end = -(COLUMN_R + POD_LEN * s)
        column.visual(
            mesh_from_geometry(
                _cyl_along((0.0, 0.0, ctrl_z), (0.0, pod_end, ctrl_z), POD_R * s),
                "control_pod",
            ),
            material=accent,
            name="control_pod", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
        )
        # dial knob (axis Y) — knob built along local Z then laid onto -Y
        dial = model.part("dial_cap")
        grip = _grip_for(r.grip_texture, 24, 0.0008)
        dial_geom = KnobGeometry(DIAL_D * s, DIAL_H * s, body_style="cylindrical", grip=grip)
        dial.visual(
            mesh_from_geometry(dial_geom, "dial_cap"),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=accent,
            name="dial_cap", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
        )
        # off-axis pointer protruding past the rim so rotation is visible
        dial_r = DIAL_D * 0.5 * s
        dial.visual(
            mesh_from_geometry(
                _translate(_box_mesh(0.003, 0.003, 0.009), 0.0, 0.0, dial_r + 0.0015),
                "dial_pointer",
            ),
            material=dark,
            name="dial_pointer", material_class_id="metal.blackened_gunmetal",
        )
        dial.inertial = _inertial_cyl(DIAL_D * 0.5 * s, DIAL_H * s, 0.04, 0.0)
        model.articulation(
            "dial_knob",
            ArticulationType.REVOLUTE,
            parent=column,
            child=dial,
            origin=Origin(xyz=(0.0, pod_end, ctrl_z)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=-CTRL_RANGE, upper=CTRL_RANGE),
        )
        return "dial_cap", "dial_knob"

    # flow_knob: knob boss on -Y side, knob revolute about X
    knob_end = -(COLUMN_R + KNOB_BOSS_LEN * s)
    column.visual(
        mesh_from_geometry(
            _cyl_along((0.0, 0.0, ctrl_z), (0.0, knob_end, ctrl_z), KNOB_BOSS_R * s),
            "knob_boss",
        ),
        material=accent,
        name="knob_boss", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
    )
    knob = model.part("flow_knob")
    grip = _grip_for(r.grip_texture, 20, 0.0008)
    knob_geom = KnobGeometry(KNOB_D * s, KNOB_H * s, body_style="cylindrical", grip=grip)
    knob.visual(
        mesh_from_geometry(knob_geom, "flow_knob"),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=accent,
        name="flow_knob", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gloss_black", "polished_chrome", "brushed_stainless", "matte_gunmetal"} else "metal.brass_polished"),
    )
    knob_r = KNOB_D * 0.5 * s
    knob.visual(
        mesh_from_geometry(
            _translate(_box_mesh(0.003, 0.003, 0.009), 0.0, 0.0, knob_r + 0.0015),
            "knob_pointer",
        ),
        material=mats["dark"],
        name="knob_pointer", material_class_id="metal.blackened_gunmetal",
    )
    knob.inertial = _inertial_cyl(KNOB_D * 0.5 * s, KNOB_H * s, 0.04, 0.0)
    model.articulation(
        "knob_joint",
        ArticulationType.REVOLUTE,
        parent=column,
        child=knob,
        origin=Origin(xyz=(0.0, knob_end, ctrl_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=-CTRL_RANGE, upper=CTRL_RANGE),
    )
    return "flow_knob", "knob_joint"


def _box_mesh(sx, sy, sz):
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    v = [
        (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
        (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz),
    ]
    f = [
        (0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
        (0, 1, 5), (0, 5, 4), (2, 3, 7), (2, 7, 6),
        (1, 2, 6), (1, 6, 5), (0, 4, 7), (0, 7, 3),
    ]
    return MeshGeometry(vertices=v, faces=f)


# --------------------------------------------------------------------------- #
# Top-level build.
# --------------------------------------------------------------------------- #
def build_high_arc_gooseneck_faucet(
    config: HighArcGooseneckFaucetConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-faucet-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]

    mats = _materials(model, r)
    column = _build_column(model, r, mats)
    spout, outlet = _build_gooseneck(model, r, mats, column)
    if r.outlet_head == "pull_down_spray":
        _build_pull_down(model, r, mats, spout, outlet)
    _build_handle(model, r, mats, column)
    _build_control(model, r, mats, column)
    return model


def build_seeded_high_arc_gooseneck_faucet(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_high_arc_gooseneck_faucet(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Overlap allowances.
# --------------------------------------------------------------------------- #
def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedHighArcGooseneckFaucetConfig):
    parts = {p.name for p in model.parts}
    column = model.get_part("faucet_column")
    spout = model.get_part("gooseneck")

    # gooseneck riser seated on the swivel collar
    ctx.allow_overlap(
        spout, column, elem_a="gooseneck_tube", elem_b="swivel_collar",
        reason="Gooseneck riser base seats on (and slightly into) the swivel collar.",
    )

    # captured pin levers in their bosses / cross tube
    for idx in range(r.handle_count):
        lever = model.get_part(f"pin_lever_{idx}")
        if r.handle_form == "cross_tube":
            ctx.allow_overlap(
                lever, column, elem_a="lever_stub", elem_b="cross_tube",
                reason="Pin-lever stub is captured in the cross-tube valve body.",
            )
            ctx.allow_overlap(
                lever, column, elem_a="lever_stub", elem_b=f"valve_end_cap_{idx}",
                reason="Pin-lever stub straddles the cross-tube end cap (captured pin).",
            )
            ctx.allow_overlap(
                lever, column, elem_a="lever_pin", elem_b="cross_tube",
                reason="Pin-lever base emerges from the cross-tube valve body.",
            )
        else:
            ctx.allow_overlap(
                lever, column, elem_a="lever_stub", elem_b=f"valve_boss_{idx}",
                reason="Pin-lever stub is captured in the valve boss.",
            )
            ctx.allow_overlap(
                lever, column, elem_a="lever_pin", elem_b=f"valve_boss_{idx}",
                reason="Pin-lever base emerges from the valve boss.",
            )
            ctx.allow_overlap(
                lever, column, elem_a="lever_stub", elem_b="column_shaft",
                reason="Inboard pin-lever stub is captured against the column shaft.",
            )
            ctx.allow_overlap(
                lever, column, elem_a="lever_pin", elem_b="column_shaft",
                reason="Pin-lever base seats against the column shaft surface.",
            )

    # pull-down telescoping captures
    if r.outlet_head == "pull_down_spray":
        hose = model.get_part("spray_hose")
        head = model.get_part("spray_head")
        ctx.allow_overlap(
            hose, spout, elem_a="spray_hose", elem_b="gooseneck_tube",
            reason="Spray hose telescopes inside the gooseneck drop leg.",
        )
        ctx.allow_overlap(
            hose, spout, elem_a="hose_collar", elem_b="gooseneck_tube",
            reason="Hose coupling collar grips the gooseneck drop-leg outlet.",
        )
        ctx.allow_overlap(
            head, hose, elem_a="spray_head", elem_b="spray_hose",
            reason="Spray head telescopes inside the hose sleeve.",
        )

    # touch dial seated into its pod
    if r.control == "touch_dial" and "dial_cap" in parts:
        ctx.allow_overlap(
            model.get_part("dial_cap"), column, elem_a="dial_cap", elem_b="control_pod",
            reason="Dial cap is seated onto the control pod end.",
        )
    if r.control == "flow_knob" and "flow_knob" in parts:
        ctx.allow_overlap(
            model.get_part("flow_knob"), column, elem_a="flow_knob", elem_b="knob_boss",
            reason="Flow knob is seated onto the knob boss.",
        )


# --------------------------------------------------------------------------- #
# Tests.
# --------------------------------------------------------------------------- #
def run_high_arc_gooseneck_faucet_tests(
    object_model: ArticulatedObject, config: HighArcGooseneckFaucetConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlaps(ctx, object_model, r)

    if "spray_head" in {p.name for p in object_model.parts}:
        ctx.allow_isolated_part(
            object_model.get_part("spray_head"),
            reason="spray head pulls off the gooseneck end and loses contact",
        )
    if "spray_hose" in {p.name for p in object_model.parts}:
        ctx.allow_isolated_part(
            object_model.get_part("spray_hose"),
            reason="spray hose pulls down out of the gooseneck and loses contact",
        )

    part_names = {p.name for p in object_model.parts}
    joint_names = {a.name for a in object_model.articulations}
    column = object_model.get_part("faucet_column")
    spout = object_model.get_part("gooseneck")
    swivel = object_model.get_articulation("column_to_gooseneck")

    # --- Identity: column on deck, high-arc gooseneck on a Z swivel ---------- #
    col_bb = ctx.part_world_aabb(column)
    ctx.check(
        "column stands on the deck plane (z=0)",
        -0.004 <= col_bb[0][2] <= 0.012,
        details=f"column_min_z={col_bb[0][2]:.4f}",
    )
    ctx.check(
        "gooseneck swivels about the vertical column axis (REVOLUTE +Z)",
        swivel.articulation_type == ArticulationType.REVOLUTE and abs(swivel.axis[2]) > 0.99,
        details=f"type={swivel.articulation_type}, axis={swivel.axis}",
    )

    spout_bb = ctx.part_world_aabb(spout)
    apex_z = spout_bb[1][2]
    ctx.check(
        "gooseneck apex within the high-arc identity band [0.36, 0.50] m",
        APEX_MIN - 0.012 <= apex_z <= APEX_MAX + 0.012,
        details=f"apex_z={apex_z:.4f}",
    )
    reach_x = spout_bb[1][0]
    ctx.check(
        "gooseneck reaches forward over the sink [0.12, 0.20] m",
        REACH_MIN - 0.012 <= reach_x <= REACH_MAX + 0.02,
        details=f"reach_x={reach_x:.4f}",
    )

    # swivel actually rotates the outlet off the +X centerline
    rest = ctx.part_world_aabb(spout)
    rest_cy = 0.5 * (rest[0][1] + rest[1][1])
    with ctx.pose({swivel: SWIVEL_RANGE}):
        turned = ctx.part_world_aabb(spout)
        turned_cy = 0.5 * (turned[0][1] + turned[1][1])
    ctx.check(
        "swivelling the gooseneck swings the outlet sideways",
        abs(turned_cy - rest_cy) > 0.01,
        details=f"rest_cy={rest_cy:.4f}, turned_cy={turned_cy:.4f}",
    )

    # --- Slot A: handle topology -------------------------------------------- #
    lever_parts = sorted(n for n in part_names if n.startswith("pin_lever_"))
    ctx.check(
        f"handle emits {r.handle_count} pin lever part(s)",
        len(lever_parts) == r.handle_count,
        details=str(lever_parts),
    )
    if r.handle_form == "cross_tube":
        ctx.check(
            "cross_tube handle is a dual valve body (N=2)",
            r.handle_count == 2 and len(lever_parts) == 2,
            details=str(lever_parts),
        )
    for idx in range(r.handle_count):
        pivot = object_model.get_articulation(f"lever_pivot_{idx}")
        ctx.check(
            f"lever_pivot_{idx} is REVOLUTE about horizontal Y",
            pivot.articulation_type == ArticulationType.REVOLUTE and abs(pivot.axis[1]) > 0.99,
            details=f"type={pivot.articulation_type}, axis={pivot.axis}",
        )
        lever = object_model.get_part(f"pin_lever_{idx}")
        rest_pin = ctx.part_world_aabb(lever)
        rest_top = rest_pin[1][2]
        with ctx.pose({pivot: LEVER_RANGE[0]}):
            moved = ctx.part_world_aabb(lever)
        ctx.check(
            f"pin_lever_{idx} tilts down when actuated",
            moved[1][2] < rest_top - 0.004,
            details=f"rest_top={rest_top:.4f}, moved_top={moved[1][2]:.4f}",
        )

    # --- Slot B: outlet topology -------------------------------------------- #
    if r.outlet_head == "pull_down_spray":
        ctx.check(
            "pull_down emits spray_hose + spray_head parts",
            "spray_hose" in part_names and "spray_head" in part_names,
            details=str(sorted(part_names)),
        )
        hose_slide = object_model.get_articulation("hose_slide")
        pulldown = object_model.get_articulation("spray_pulldown")
        ctx.check(
            "both pull-down joints are PRISMATIC along -Z",
            hose_slide.articulation_type == ArticulationType.PRISMATIC
            and pulldown.articulation_type == ArticulationType.PRISMATIC
            and abs(hose_slide.axis[2] + 1.0) < 0.02
            and abs(pulldown.axis[2] + 1.0) < 0.02,
            details=f"hose={hose_slide.axis}, head={pulldown.axis}",
        )
        ctx.check(
            "hose_slide mimics spray_pulldown (telescoping x2)",
            hose_slide.mimic is not None and hose_slide.mimic.joint == "spray_pulldown",
            details=str(hose_slide.mimic),
        )
        # head drops when extended
        head = object_model.get_part("spray_head")
        rest_head = ctx.part_world_aabb(head)
        with ctx.pose({pulldown: r.stage_travel}):
            ext_head = ctx.part_world_aabb(head)
        ctx.check(
            "spray head pulls down when extended",
            ext_head[0][2] < rest_head[0][2] - 0.01,
            details=f"rest_z={rest_head[0][2]:.4f}, ext_z={ext_head[0][2]:.4f}",
        )
    else:
        ctx.check(
            "fixed_aerator: no pull-down parts/joints",
            "spray_hose" not in part_names and "spray_head" not in part_names
            and "hose_slide" not in joint_names and "spray_pulldown" not in joint_names,
            details=str(sorted(part_names)),
        )
        ctx.check(
            "fixed_aerator outlet head welded to the gooseneck",
            any(v.name == "outlet_head" for v in spout.visuals),
            details=str([v.name for v in spout.visuals]),
        )

    # --- Slot C: control topology ------------------------------------------- #
    if r.control == "touch_dial":
        dial = object_model.get_articulation("dial_knob")
        ctx.check(
            "touch_dial: dial_cap on a REVOLUTE about Y",
            "dial_cap" in part_names
            and dial.articulation_type == ArticulationType.REVOLUTE
            and abs(dial.axis[1]) > 0.99,
            details=f"axis={dial.axis}",
        )
        _check_spin(ctx, object_model, "dial_cap", dial)
    elif r.control == "flow_knob":
        knob = object_model.get_articulation("knob_joint")
        ctx.check(
            "flow_knob: knob on a REVOLUTE about X",
            "flow_knob" in part_names
            and knob.articulation_type == ArticulationType.REVOLUTE
            and abs(knob.axis[0]) > 0.99,
            details=f"axis={knob.axis}",
        )
        _check_spin(ctx, object_model, "flow_knob", knob)
    else:
        ctx.check(
            "manual_none: no electronic control parts/joints",
            "dial_cap" not in part_names and "flow_knob" not in part_names
            and "dial_knob" not in joint_names and "knob_joint" not in joint_names,
            details=str(sorted(part_names)),
        )

    return ctx.report()


def _check_spin(ctx: TestContext, model: ArticulatedObject, part_name: str, joint):
    """Off-axis pointer => the part AABB center shifts under rotation."""
    part = model.get_part(part_name)
    rest = ctx.part_world_aabb(part)
    rest_c = tuple(0.5 * (rest[0][i] + rest[1][i]) for i in range(3))
    with ctx.pose({joint: CTRL_RANGE}):
        spun = ctx.part_world_aabb(part)
        spun_c = tuple(0.5 * (spun[0][i] + spun[1][i]) for i in range(3))
    disp = math.sqrt(sum((spun_c[i] - rest_c[i]) ** 2 for i in range(3)))
    ctx.check(
        f"{part_name} visibly rotates (off-axis pointer displaces)",
        disp > 0.0008,
        details=f"aabb_center_disp={disp:.5f}",
    )


__all__ = [
    "HighArcGooseneckFaucetConfig",
    "ResolvedHighArcGooseneckFaucetConfig",
    "build_high_arc_gooseneck_faucet",
    "build_seeded_high_arc_gooseneck_faucet",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "run_high_arc_gooseneck_faucet_tests",
    "__modular__",
]
