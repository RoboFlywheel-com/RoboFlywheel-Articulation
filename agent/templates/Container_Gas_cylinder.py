# SPDX-License-Identifier: Apache-2.0

"""Container / gas cylinder — modular procedural template (pressurized LPG / scuba tank).

Category identity: an upright thick-walled steel gas cylinder. The lathed body
shell (ROOT) rests on z=0 with its axis along +Z (foot transition -> straight
wall -> rounded shoulder -> dome -> neck boss; ``height >> diameter``). A brass
CadQuery valve (seat boss + valve block + side outlet spigot + rising stem) is
FIXED on the neck boss on the +Z axis — this is the fixed identity skeleton.
On top of the valve a closure mechanism articulates (the main motion). Around
the valve a top guard protects it, and the cylinder stands on one of three
base styles.

Three parallel slots (spec ``Container_Gas_cylinder.md``), all children of the
``body`` root (valve_closure chains body -> valve -> mechanism):

  * ``top_guard`` (4) — valve protection around/above the valve:
      - ring_on_struts: Torus top ring + 4 short struts (body visual, no joint).
      - solid_neck_collar: continuous stamped cup wall (lathe; body visual).
      - carry_handle_arch: inverted-U bow handle as a REVOLUTE +Y ``bow_guard``
        part swinging fore/aft, captured by two fixed ``bow_anchor_pad`` bosses.
      - vented_cage_shroud: top + bottom cage rings + N equiangular vertical
        ``cage_bar_{i}`` bars (body visuals). Carries the ``cage_bar_count``
        multiplicity axis (N in [3, 12]).
  * ``valve_closure`` (3) — the operated mechanism (>=1 non-fixed REVOLUTE each):
      - handwheel_valve: star handwheel REVOLUTE +Z (limit +-4pi), off-axis lug.
      - lever_clip_valve: self-closing lever REVOLUTE +Y (limit [0, 1.05]).
      - screw_bonnet_cap: domed screw cap REVOLUTE +Z (limit [0, 6pi]).
  * ``base`` (3) — how the cylinder stands:
      - foot_ring: dark steel skirt ring (one FIXED ``foot_ring`` part).
      - concave_recessed_base: integral dished base (no part / no joint).
      - n_feet_base: N equiangular stub feet (``foot_{i}`` parts, FIXED).
        Carries the secondary ``foot_count`` multiplicity (N in [3, 4]).

Continuous size/proportion variation (height/radius/guard-ring/travel scales)
lives in ``resolve_config`` as clamped params, never as slot candidates.
``palette_style`` (10 colorways + finish dimension) is palette-only and never
changes structure / slot / multiplicity.

Sources (articraft_data ``picture/Container/Gas cylinder`` 5-star pool): parent
``rec_red-...-5d5b07e2`` (body/valve/handwheel/collar/foot skeleton) plus qwen
forks ``solid_neck_collar`` / ``carry_handle_arch`` / ``vented_cage_shroud`` /
``cage_n6`` / ``cage_n8`` / ``lever_clip_valve`` / ``screw_bonnet_cap`` /
``concave_recessed_base`` / ``n_feet_base``.

Canonical spec:
``articraft_template_authoring/specs_modular_v1/Container_Gas_cylinder.md``
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    CylinderGeometry,
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    clamp_joint_limits,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
TopGuard = Literal[
    "ring_on_struts",
    "solid_neck_collar",
    "carry_handle_arch",
    "vented_cage_shroud",
]
ValveClosure = Literal[
    "handwheel_valve",
    "lever_clip_valve",
    "screw_bonnet_cap",
]
Base = Literal[
    "foot_ring",
    "concave_recessed_base",
    "n_feet_base",
]
PaletteStyle = Literal[
    "industrial_red_lpg",
    "industrial_blue_lpg",
    "industrial_grey_steel",
    "safety_yellow",
    "medical_white",
    "forest_green_propane",
    "galvanized_zinc",
    "brushed_steel_scuba",
    "matte_powder_coat",
    "weathered_scuffed",
]

TOP_GUARDS: tuple[TopGuard, ...] = (
    "ring_on_struts",
    "solid_neck_collar",
    "carry_handle_arch",
    "vented_cage_shroud",
)
VALVE_CLOSURES: tuple[ValveClosure, ...] = (
    "handwheel_valve",
    "lever_clip_valve",
    "screw_bonnet_cap",
)
BASES: tuple[Base, ...] = (
    "foot_ring",
    "concave_recessed_base",
    "n_feet_base",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "industrial_red_lpg",
    "industrial_blue_lpg",
    "industrial_grey_steel",
    "safety_yellow",
    "medical_white",
    "forest_green_propane",
    "galvanized_zinc",
    "brushed_steel_scuba",
    "matte_powder_coat",
    "weathered_scuffed",
)

# cage_bar_count multiplicity: N in [3, 12]; sweep weighted small (4/5/6 common).
CAGE_BAR_MIN = 3
CAGE_BAR_MAX = 12
_CAGE_BAR_WEIGHTED: tuple[int, ...] = (3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 8, 9, 10, 12)
# foot_count multiplicity: N in [3, 4]; N=3 common, N=4 occasional.
FOOT_MIN = 3
FOOT_MAX = 4
_FOOT_WEIGHTED: tuple[int, ...] = (3, 3, 3, 4)


# ---------------------------------------------------------------------------
# Palettes: each colorway resolves body / valve / guard / foot rgba + a finish
# dimension (surface treatment). The finish is appearance-only and never
# changes structure; it is recorded on the materials' names for downstream use.
# ---------------------------------------------------------------------------
_BRASS = (0.78, 0.62, 0.22, 1.0)
_CHROME = (0.80, 0.81, 0.83, 1.0)
_ZINC = (0.52, 0.55, 0.58, 1.0)
_BARE_STEEL = (0.62, 0.62, 0.64, 1.0)
_DARK_FOOT = (0.12, 0.12, 0.13, 1.0)
_HAZARD = (0.92, 0.80, 0.20, 1.0)


@dataclass(frozen=True)
class _Palette:
    finish: str
    body: tuple[float, float, float, float]
    valve: tuple[float, float, float, float]
    guard: tuple[float, float, float, float]
    foot: tuple[float, float, float, float]


PALETTES: dict[PaletteStyle, _Palette] = {
    "industrial_red_lpg": _Palette(
        "glossy_industrial_paint", (0.72, 0.16, 0.13, 1.0), _BRASS, _BARE_STEEL, _DARK_FOOT
    ),
    "industrial_blue_lpg": _Palette(
        "glossy_industrial_paint", (0.16, 0.28, 0.55, 1.0), _BRASS, _BARE_STEEL, _DARK_FOOT
    ),
    "industrial_grey_steel": _Palette(
        "glossy_industrial_paint", (0.62, 0.62, 0.64, 1.0), _BRASS, _BARE_STEEL, _DARK_FOOT
    ),
    "safety_yellow": _Palette(
        "glossy_industrial_paint", (0.86, 0.72, 0.14, 1.0), _ZINC, _BARE_STEEL, _DARK_FOOT
    ),
    "medical_white": _Palette(
        "glossy_industrial_paint", (0.92, 0.93, 0.94, 1.0), _CHROME, _BARE_STEEL, _DARK_FOOT
    ),
    "forest_green_propane": _Palette(
        "glossy_industrial_paint", (0.16, 0.40, 0.22, 1.0), _BRASS, _BARE_STEEL, _DARK_FOOT
    ),
    "galvanized_zinc": _Palette(
        "galvanized_zinc", (0.66, 0.68, 0.70, 1.0), _ZINC, (0.66, 0.68, 0.70, 1.0), _DARK_FOOT
    ),
    "brushed_steel_scuba": _Palette(
        "brushed_steel", (0.70, 0.71, 0.73, 1.0), _CHROME, (0.70, 0.71, 0.73, 1.0), _DARK_FOOT
    ),
    "matte_powder_coat": _Palette(
        "matte_powder_coat",
        (0.22, 0.23, 0.25, 1.0),
        _BARE_STEEL,
        (0.22, 0.23, 0.25, 1.0),
        _DARK_FOOT,
    ),
    "weathered_scuffed": _Palette(
        "weathered_scuffed", (0.72, 0.16, 0.13, 1.0), _BRASS, (0.46, 0.34, 0.24, 1.0), _DARK_FOOT
    ),
}


# ---------------------------------------------------------------------------
# Base nominal geometry (meters), from the parent skeleton. Scaled per build.
# ---------------------------------------------------------------------------
BODY_R = 0.150  # cylinder outer radius (~0.30 m dia)
FOOT_TOP_Z = 0.030  # top of the foot ring
WALL_TOP_Z = 0.330  # cylindrical wall ends / shoulder begins
SHOULDER_TOP_Z = 0.430  # top of the domed shoulder (neck starts)
NECK_TOP_Z = 0.470  # top of the brass valve neck boss
COLLAR_RING_Z = 0.500  # protective collar guard ring height
COLLAR_TOP_Z = 0.518  # solid neck collar wall top

VALVE_AXIS_Z = NECK_TOP_Z

# lever_clip_valve rest tilt: the self-closing lever rests angled UP and away from
# the body (closed) and is pressed DOWN toward horizontal to open. Resting it up
# keeps the whole swept band ABOVE the neck collar / cage / shell surface so the
# arm rotates in a plane clear of the body (real cylinder levers do); the exact
# per-config open limit is then solved by the clearance solver. Single source of
# truth for the rest tilt (mesh, joint origin rpy, and swing intent all read it).
LEVER_REST_TILT = 0.60  # radians the arm sits above horizontal at rest

# bow guard nominal dims (carry_handle_arch).
BOW_ANCHOR_Y = 0.105
BOW_ANCHOR_Z = SHOULDER_TOP_Z - 0.023
BOW_RISE = 0.185
BOW_BAR_R = 0.006

# n_feet stub foot nominal dims.
FOOT_H = 0.030
FOOT_WIDTH = 0.042
FOOT_DEPTH = 0.024

DISH_DEPTH = 0.025  # concave dished base center rise


@dataclass(frozen=True)
class ContainerGasCylinderConfig:
    top_guard: TopGuard = "ring_on_struts"
    valve_closure: ValveClosure = "handwheel_valve"
    base: Base = "foot_ring"
    cage_bar_count: int = 4
    foot_count: int = 3
    palette_style: PaletteStyle = "industrial_red_lpg"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    guard_ring_radius_scale: float = 1.0
    joint_travel_scale: float = 1.0
    name: str = "container_gas_cylinder"


@dataclass(frozen=True)
class ResolvedContainerGasCylinderConfig:
    top_guard: TopGuard
    valve_closure: ValveClosure
    base: Base
    cage_bar_count: int
    foot_count: int
    palette_style: PaletteStyle
    body_height_scale: float
    body_radius_scale: float
    guard_ring_radius_scale: float
    joint_travel_scale: float
    # derived geometry (world frame)
    body_r: float
    foot_top_z: float
    wall_top_z: float
    shoulder_top_z: float
    neck_top_z: float
    collar_ring_z: float
    collar_top_z: float
    valve_axis_z: float
    guard_ring_r: float  # GUARD_R (cage / collar / struts ring radius)
    bow_anchor_y: float
    bow_anchor_z: float
    bow_rise: float
    foot_r: float  # radial placement of n_feet centers
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerGasCylinderConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    top_guard = rng.choice(TOP_GUARDS)
    valve_closure = rng.choice(VALVE_CLOSURES)
    base = rng.choice(BASES)
    # cage_bar_count only meaningful for vented_cage_shroud (conditional axis).
    cage_bar_count = rng.choice(_CAGE_BAR_WEIGHTED) if top_guard == "vented_cage_shroud" else 4
    # foot_count only meaningful for n_feet_base (conditional secondary axis).
    foot_count = rng.choice(_FOOT_WEIGHTED) if base == "n_feet_base" else 3
    return ContainerGasCylinderConfig(
        top_guard=top_guard,
        valve_closure=valve_closure,
        base=base,
        cage_bar_count=cage_bar_count,
        foot_count=foot_count,
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.88, 1.15), 4),
        body_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        guard_ring_radius_scale=round(rng.uniform(0.92, 1.10), 4),
        joint_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_gas_cylinder_{seed}",
    )


def resolve_config(
    config: ContainerGasCylinderConfig | None = None,
) -> ResolvedContainerGasCylinderConfig:
    cfg = config or ContainerGasCylinderConfig()
    top_guard = _pick(cfg.top_guard, TOP_GUARDS)
    valve_closure = _pick(cfg.valve_closure, VALVE_CLOSURES)
    base = _pick(cfg.base, BASES)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    h_scale = _clamp(cfg.body_height_scale, 0.88, 1.15)
    r_scale = _clamp(cfg.body_radius_scale, 0.90, 1.12)
    gr_scale = _clamp(cfg.guard_ring_radius_scale, 0.92, 1.10)
    jt_scale = _clamp(cfg.joint_travel_scale, 0.85, 1.10)

    # cage_bar_count: clamp + only active for vented_cage_shroud.
    if top_guard == "vented_cage_shroud":
        cage_bar_count = int(_clamp(cfg.cage_bar_count, CAGE_BAR_MIN, CAGE_BAR_MAX))
    else:
        cage_bar_count = 4
    # foot_count: clamp + only active for n_feet_base.
    if base == "n_feet_base":
        foot_count = int(_clamp(cfg.foot_count, FOOT_MIN, FOOT_MAX))
    else:
        foot_count = 3

    body_r = BODY_R * r_scale

    # Height scaling lifts everything above the straight wall by the same factor
    # so the shoulder / dome / neck / guard mounts all rise together while the
    # base (foot transition) stays anchored at the ground.
    wall_top_z = WALL_TOP_Z * h_scale
    shoulder_top_z = wall_top_z + (SHOULDER_TOP_Z - WALL_TOP_Z) * h_scale
    neck_top_z = shoulder_top_z + (NECK_TOP_Z - SHOULDER_TOP_Z) * h_scale
    collar_ring_z = neck_top_z + (COLLAR_RING_Z - NECK_TOP_Z) * h_scale
    collar_top_z = neck_top_z + (COLLAR_TOP_Z - NECK_TOP_Z) * h_scale
    valve_axis_z = neck_top_z

    # GUARD_R equation: nominal 0.080 ring radius scaled by guard_ring_radius;
    # then projected so the guard still encircles the valve (>= valve outer +
    # clearance) and never reaches the body outer edge (<= body_r - margin).
    valve_outer_r = 0.026
    guard_ring_r = 0.080 * gr_scale
    guard_ring_r = max(guard_ring_r, valve_outer_r + 0.030)
    guard_ring_r = min(guard_ring_r, body_r - 0.020)

    # bow guard rise scaled with height so the swing clears the valve + closure.
    bow_anchor_z = shoulder_top_z - 0.023
    # The bow pivot (leg-end + pivot stub at radius ``bow_anchor_y`` on the +/-Y
    # line) must sit OUTSIDE the body shell wall, otherwise the bow tube would
    # penetrate the solid shell core at low height_scale (where the shell has not
    # yet tapered at this z) and trip the part-overlap check. The leg-end / stub
    # geometry has a vertical half-extent of one bow-tube radius, so its LOWEST
    # point reaches ``bow_anchor_z - BOW_BAR_R`` where the shell is WIDEST; evaluate
    # the shell radius there (not at the center z) and clear it by the tube radius
    # plus a margin. Capped so it never reaches the body outer edge.
    shell_r_at_bow = _shell_radius_at_z_tapered(
        br=body_r,
        wall_top_z=wall_top_z,
        shoulder_top_z=shoulder_top_z,
        z=bow_anchor_z - BOW_BAR_R,
    )
    bow_anchor_y = max(BOW_ANCHOR_Y, shell_r_at_bow + BOW_BAR_R + 0.010)
    bow_anchor_y = min(bow_anchor_y, body_r + 0.030)
    bow_rise = BOW_RISE * h_scale

    foot_r = body_r - 0.008

    return ResolvedContainerGasCylinderConfig(
        top_guard=top_guard,
        valve_closure=valve_closure,
        base=base,
        cage_bar_count=cage_bar_count,
        foot_count=foot_count,
        palette_style=palette,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        guard_ring_radius_scale=gr_scale,
        joint_travel_scale=jt_scale,
        body_r=body_r,
        foot_top_z=FOOT_TOP_Z,
        wall_top_z=wall_top_z,
        shoulder_top_z=shoulder_top_z,
        neck_top_z=neck_top_z,
        collar_ring_z=collar_ring_z,
        collar_top_z=collar_top_z,
        valve_axis_z=valve_axis_z,
        guard_ring_r=guard_ring_r,
        bow_anchor_y=bow_anchor_y,
        bow_anchor_z=bow_anchor_z,
        bow_rise=bow_rise,
        foot_r=foot_r,
        name=cfg.name or "container_gas_cylinder",
    )


def with_overrides(
    config: ContainerGasCylinderConfig, **kwargs: object
) -> ContainerGasCylinderConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerGasCylinderConfig | ResolvedContainerGasCylinderConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedContainerGasCylinderConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("top_guard", r.top_guard),
        ("valve_closure", r.valve_closure),
        ("base", r.base),
    ]
    # Multiplicity axes change topology equivalence class -> record them.
    if r.top_guard == "vented_cage_shroud":
        choices.append(("cage_bar_count", str(r.cage_bar_count)))
    if r.base == "n_feet_base":
        choices.append(("foot_count", str(r.foot_count)))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Fixed skeleton geometry: body shell (lathe) + brass valve (cadquery).
# ---------------------------------------------------------------------------
def _body_mesh(r: ResolvedContainerGasCylinderConfig) -> object:
    """Lathed steel cylinder shell of revolution about +Z.

    foot transition -> straight wall -> rounded shoulder -> dome -> neck boss.
    The ``concave_recessed_base`` variant swaps the flat base for a dished
    base whose outer rim sits at z=0 while the center is recessed upward."""
    br = r.body_r
    if r.base == "concave_recessed_base":
        profile = [
            (0.000, DISH_DEPTH),
            (br * 0.267, DISH_DEPTH - 0.002),
            (br * 0.533, DISH_DEPTH - 0.008),
            (br * 0.800, DISH_DEPTH - 0.016),
            (br - 0.005, 0.004),
            (br, 0.0),
            (br, 0.060),
            (br, r.wall_top_z),
            (br - 0.012, r.wall_top_z + 0.030),
            (br - 0.045, r.wall_top_z + 0.062),
            (br - 0.095, r.shoulder_top_z - 0.012),
            (0.052, r.shoulder_top_z),
            (0.034, r.neck_top_z),
            (0.000, r.neck_top_z),
        ]
    else:
        profile = [
            (0.000, FOOT_TOP_Z - 0.005),
            (br - 0.004, FOOT_TOP_Z),
            (br, 0.060),
            (br, r.wall_top_z),
            (br - 0.012, r.wall_top_z + 0.030),
            (br - 0.045, r.wall_top_z + 0.062),
            (br - 0.095, r.shoulder_top_z - 0.012),
            (0.052, r.shoulder_top_z),
            (0.034, r.neck_top_z),
            (0.000, r.neck_top_z),
        ]
    return mesh_from_geometry(LatheGeometry(profile, segments=64), "body_shell")


def _shell_radius_at_z_tapered(
    *, br: float, wall_top_z: float, shoulder_top_z: float, z: float
) -> float:
    """Outer radius of the body shell at height ``z`` from raw geometry scalars
    (no ResolvedConfig). Used inside ``resolve_config`` itself (before the resolved
    config exists) to anchor the bow pivot just outside the real shell surface."""
    taper = [
        (br, wall_top_z),
        (br - 0.012, wall_top_z + 0.030),
        (br - 0.045, wall_top_z + 0.062),
        (br - 0.095, shoulder_top_z - 0.012),
        (0.052, shoulder_top_z),
    ]
    if z <= wall_top_z:
        return br
    for (r0, z0), (r1, z1) in zip(taper, taper[1:]):
        if z0 <= z <= z1 and z1 > z0:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return taper[-1][0]


def _shell_radius_at_z(r: ResolvedContainerGasCylinderConfig, z: float) -> float:
    """Outer radius of the body shell at height ``z`` (straight-wall + shoulder
    taper; used to embed shoulder-mounted bosses into the real shell surface)."""
    return _shell_radius_at_z_tapered(
        br=r.body_r, wall_top_z=r.wall_top_z, shoulder_top_z=r.shoulder_top_z, z=z
    )


def _shell_z_for_radius(r: ResolvedContainerGasCylinderConfig, target_r: float) -> float:
    """Lowest shoulder height ``z`` where the shell outer radius has narrowed to
    ``target_r`` (used to anchor shoulder-mounted guards down onto the real shell
    wall so they embed instead of floating). Returns wall_top_z if the shell is
    never that narrow within the taper."""
    br = r.body_r
    taper = [
        (br, r.wall_top_z),
        (br - 0.012, r.wall_top_z + 0.030),
        (br - 0.045, r.wall_top_z + 0.062),
        (br - 0.095, r.shoulder_top_z - 0.012),
        (0.052, r.shoulder_top_z),
    ]
    for (r0, z0), (r1, z1) in zip(taper, taper[1:]):
        hi, lo = r0, r1
        if lo <= target_r <= hi and r0 != r1:
            return z0 + (z1 - z0) * (r0 - target_r) / (r0 - r1)
    return r.wall_top_z


def _valve_mesh() -> object:
    """Brass valve block (valve-local frame, origin at neck-boss seat).

    seat boss + valve block + +X side outlet spigot + spigot tip + rising stem.
    Identical to the parent skeleton (fixed, never re-skinned)."""
    body = cq.Workplane("XY").circle(0.026).extrude(0.022)
    body = body.union(cq.Workplane("XY").workplane(offset=0.022).circle(0.022).extrude(0.024))
    spigot = (
        cq.Workplane("YZ").workplane(offset=0.010).center(0.0, 0.034).circle(0.010).extrude(0.034)
    )
    body = body.union(spigot)
    tip = cq.Workplane("YZ").workplane(offset=0.040).center(0.0, 0.034).circle(0.012).extrude(0.006)
    body = body.union(tip)
    body = body.union(cq.Workplane("XY").workplane(offset=0.046).circle(0.007).extrude(0.020))
    return mesh_from_cadquery(body, "valve_body")


# ---------------------------------------------------------------------------
# Slot A: top_guard meshes (all centered on +Z axis in the body part frame).
# ---------------------------------------------------------------------------
def _collar_struts_mesh(r: ResolvedContainerGasCylinderConfig) -> object:
    """Open collar guard: a top torus ring + 4 struts that splay outward to land
    ON the body shell wall.

    Each strut runs from the top ring (radius ``ring_r``, z=collar_ring_z) down
    and outward to a base point embedded in the straight cylinder wall (radius
    ``body_r``, z=wall_top_z), so the collar physically contacts ``body_shell``
    (no disconnected-island warning) regardless of height/radius/guard scale."""
    ring_r = r.guard_ring_r
    geom = TorusGeometry(ring_r, 0.009, radial_segments=12, tubular_segments=48)
    geom.translate(0.0, 0.0, r.collar_ring_z)
    # Top end on the ring; bottom end driven INTO the straight wall so the strut
    # base overlaps the shell (radial penetration of ~0.004 m guarantees contact).
    top_z = r.collar_ring_z
    base_z = r.wall_top_z + 0.010
    base_r = r.body_r - 0.004
    dr = base_r - ring_r
    dz = top_z - base_z
    strut_len = math.sqrt(dr * dr + dz * dz)
    # Negative tilt: the +Z cylinder's TOP end leans toward the axis (the narrow
    # ring radius) while its BASE swings outward into the wide straight wall.
    tilt = -math.atan2(dr, dz)
    mid_r = (ring_r + base_r) / 2.0
    mid_z = (top_z + base_z) / 2.0
    for i in range(4):
        ang = i * math.pi / 2.0 + math.pi / 4.0
        strut = CylinderGeometry(0.006, strut_len, radial_segments=8)
        strut.rotate_y(tilt)
        strut.translate(mid_r, 0.0, mid_z)
        strut.rotate_z(ang)
        geom.merge(strut)
    return mesh_from_geometry(geom, "collar_guard")


def _neck_collar_mesh(r: ResolvedContainerGasCylinderConfig) -> object:
    """Solid stamped steel cup-wall neck collar (continuous lathe wall).

    The base flare is driven out to the body shell wall (``base_flare_r``) so the
    collar physically seats on / embeds in ``body_shell`` across the scale range
    (no floating island) before tapering up to the protective rolled lip."""
    outer_r = max(r.guard_ring_r - 0.020, 0.040)
    wall_t = 0.004
    inner_r = outer_r - wall_t
    top_z = r.collar_top_z
    # The shell narrows going up; drop the collar base DOWN to the height where
    # the shell is exactly as wide as the collar wall, then flare a touch past it
    # so the continuous wall embeds in / seats on the shoulder (no floating
    # island) across the scale range.
    flare_target_r = outer_r + 0.006
    base_z = min(r.shoulder_top_z - 0.012, _shell_z_for_radius(r, flare_target_r) + 0.004)
    base_flare_r = max(flare_target_r, _shell_radius_at_z(r, base_z) - 0.004)
    profile = [
        (inner_r - 0.003, base_z - 0.002),
        (base_flare_r, base_z - 0.002),
        (base_flare_r, base_z + 0.006),
        (outer_r + 0.002, base_z + 0.014),
        (outer_r, base_z + 0.025),
        (outer_r, top_z),
        (outer_r - 0.001, top_z + 0.003),
        (inner_r + 0.001, top_z + 0.003),
        (inner_r, top_z),
        (inner_r, base_z + 0.025),
        (inner_r - 0.003, base_z - 0.002),
    ]
    return mesh_from_geometry(LatheGeometry(profile, segments=64), "neck_collar")


def _cage_bottom_z(r: ResolvedContainerGasCylinderConfig) -> float:
    """Height of the cage bottom ring / cage-bar feet: dropped down onto the
    shell wall where it is wide enough for the bar feet to embed (not floating
    above the narrow shoulder)."""
    return min(r.shoulder_top_z - 0.020, _shell_z_for_radius(r, r.guard_ring_r) + 0.006)


def _cage_ring_mesh(r: ResolvedContainerGasCylinderConfig, z: float, name: str) -> object:
    geom = TorusGeometry(r.guard_ring_r, 0.007, radial_segments=12, tubular_segments=48)
    geom.translate(0.0, 0.0, z)
    return mesh_from_geometry(geom, name)


def _cage_bar_geometry(bar_r: float, height: float) -> CylinderGeometry:
    """Shared geometry helper: one vertical cage bar cylinder centered at origin."""
    return CylinderGeometry(bar_r, height, radial_segments=8)


def _cage_bar_mesh(r: ResolvedContainerGasCylinderConfig, i: int, n: int) -> object:
    """One cage bar at an equal-angle position around the guard ring.

    The upper run is vertical at ``guard_ring_r``; the foot splays outward to
    embed into the body shell wall so the cage physically contacts ``body_shell``
    (no floating island) across the whole scale range."""
    ang = i * 2.0 * math.pi / n
    ring_r = r.guard_ring_r
    top_z = r.collar_ring_z
    foot_z = _cage_bottom_z(r)
    foot_r = max(_shell_radius_at_z(r, foot_z) - 0.004, ring_r)
    if foot_r <= ring_r + 1e-9:
        # Shell already as wide as the ring here: a single vertical bar suffices.
        height = top_z - foot_z
        geom = _cage_bar_geometry(0.006, height)
        geom.translate(ring_r, 0.0, foot_z + height / 2.0)
    else:
        # Vertical upper run + an outward-splayed foot that lands on the shell.
        splay_z = min(0.045, top_z - foot_z)
        vert_h = (top_z - foot_z) - splay_z
        upper = _cage_bar_geometry(0.006, vert_h)
        upper.translate(ring_r, 0.0, foot_z + splay_z + vert_h / 2.0)
        dr = foot_r - ring_r
        foot_len = math.sqrt(dr * dr + splay_z * splay_z)
        tilt = -math.atan2(dr, splay_z)
        foot = _cage_bar_geometry(0.006, foot_len)
        foot.rotate_y(tilt)
        foot.translate((ring_r + foot_r) / 2.0, 0.0, foot_z + splay_z / 2.0)
        upper.merge(foot)
        geom = upper
    geom.rotate_z(ang)
    return mesh_from_geometry(geom, f"cage_bar_{i}")


def _bow_arch_centerline(r: ResolvedContainerGasCylinderConfig) -> list[tuple[float, float]]:
    """Bow arch tube centerline as ``(y, z)`` pairs in the bow pivot (child)
    frame (x is always 0 at rest — the arch lies in the Y-Z plane).

    Single source of truth for the arch shape: the mesh builder threads a tube
    through these points, and the swing-limit solver rotates them about the +Y
    pivot to derive how far the bow can swing before it dips into the shell."""
    anchor_y = r.bow_anchor_y
    peak_z = r.bow_rise
    # Arch authored with the +Y leg-end at child origin (0,0,0); the whole U is
    # shifted -anchor_y in Y so the -Y leg-end lands at (0,-2*anchor_y,0).
    s = -anchor_y
    return [
        (s + (-anchor_y), 0.0),
        (s + (-anchor_y + 0.002), 0.050),
        (s + (-0.082), 0.102),
        (s + (-0.048), peak_z - 0.020),
        (s + 0.000, peak_z),
        (s + 0.040, peak_z - 0.020),
        (s + 0.082, 0.102),
        (s + (anchor_y - 0.002), 0.050),
        (s + anchor_y, 0.0),
    ]


def _shell_outer_radius_full(r: ResolvedContainerGasCylinderConfig, z: float) -> float:
    """Outer radius of the body shell over the FULL upper profile (straight wall
    -> shoulder -> dome -> neck), returning 0 where no shell exists (below the
    ground or above the neck boss). Used by the bow swing-limit solver to test the
    arch against the real revolved surface (the shared ``_shell_radius_at_z``
    taper stops at the shoulder top and would over-report the dome/neck)."""
    if z <= 0.0 or z >= r.neck_top_z:
        return 0.0
    if z <= r.wall_top_z:
        return r.body_r
    prof = [
        (r.body_r, r.wall_top_z),
        (r.body_r - 0.012, r.wall_top_z + 0.030),
        (r.body_r - 0.045, r.wall_top_z + 0.062),
        (r.body_r - 0.095, r.shoulder_top_z - 0.012),
        (0.052, r.shoulder_top_z),
        (0.034, r.neck_top_z),
    ]
    for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
        if z0 <= z <= z1 and z1 > z0:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return 0.0


def _bow_swing_limit(
    r: ResolvedContainerGasCylinderConfig, base_swing: float, *, margin: float = 0.008
) -> float:
    """Largest symmetric bow swing (radians) keeping the arch tube clear of the
    shell surface by ``margin``.

    The bow pivots about +Y at ``(0, bow_anchor_y, bow_anchor_z)``. A rest arch
    point ``(0, y, z)`` rotates under joint angle ``theta`` to world
    ``(z*sin(theta), bow_anchor_y + y, bow_anchor_z + z*cos(theta))``; its
    horizontal distance from the cylinder axis must exceed the shell radius at
    that height (plus tube radius + margin). The clearance solver can't be used
    here because the +/-Y anchor pads are body elements that intentionally overlap
    the bow at every angle (a part-level distance query would read 0), so the
    limit is derived analytically against the shell profile instead. Symmetric:
    both swing directions are solved and the tighter magnitude is returned."""
    centerline = _bow_arch_centerline(r)
    # Densify each segment so the tube's mid-span (not just the authored knots) is
    # tested against the shell.
    dense: list[tuple[float, float]] = []
    for (y0, z0), (y1, z1) in zip(centerline, centerline[1:]):
        for k in range(13):
            t = k / 12.0
            dense.append((y0 + (y1 - y0) * t, z0 + (z1 - z0) * t))
    ay = r.bow_anchor_y
    az = r.bow_anchor_z
    reach = BOW_BAR_R + margin

    def clears(theta: float) -> bool:
        st, ct = math.sin(theta), math.cos(theta)
        for yi, zi in dense:
            world_z = az + zi * ct
            shell_r = _shell_outer_radius_full(r, world_z)
            if shell_r <= 0.0:
                continue  # no shell material at this height -> nothing to hit
            x = zi * st
            y = ay + yi
            if math.hypot(x, y) < shell_r + reach:
                return False
        return True

    def solve_dir(sign: float) -> float:
        step = base_swing / 48.0
        last = 0.0
        theta = 0.0
        while theta < base_swing:
            nxt = min(theta + step, base_swing)
            if clears(sign * nxt):
                last = nxt
                theta = nxt
                if nxt >= base_swing:
                    break
            else:
                lo, hi = last, nxt
                for _ in range(24):
                    mid = (lo + hi) / 2.0
                    if clears(sign * mid):
                        lo = mid
                    else:
                        hi = mid
                return lo
        return last

    return min(solve_dir(1.0), solve_dir(-1.0))


def _bow_guard_mesh(r: ResolvedContainerGasCylinderConfig) -> object:
    """Inverted-U carry-handle bow (tube spline) in the bow pivot frame.

    Authored so the pivot point (the +Y leg-end, which seats on the +Y anchor
    pad) is the child-link origin ``(0,0,0)`` and a short pivot cross-rod runs
    along -Y through that origin. This puts real child geometry AT the joint
    origin (``dist_child`` -> 0) and keeps the +Y rotation axis on the line
    joining the two anchor pads. The arch is shifted -Y by ``anchor_y`` so its
    far leg reaches the -Y pad. Legs stay wide enough to clear the closure rim."""
    arch_points = [(0.0, y, z) for y, z in _bow_arch_centerline(r)]
    bar = tube_from_spline_points(
        arch_points,
        radius=BOW_BAR_R,
        samples_per_segment=16,
        radial_segments=16,
        cap_ends=True,
    )
    # Short pivot stub with its INBOARD cap face exactly at the child origin
    # (0,0,0), extending OUTBOARD (+Y, away from the body axis) only. This puts
    # real child geometry AT the joint origin (dist_child -> 0) and lies along the
    # +Y rotation axis, WITHOUT running back through the body shell core toward the
    # axis (an inboard or full-diameter rod penetrated the solid shell at low
    # height_scale and tripped the part-overlap check). ``bow_anchor_y`` is resolved
    # to sit outside the shell wall, so an outboard-only stub stays fully clear of
    # the body; the anchor pads bridge inward to embed in the shell.
    stub_len = 0.016
    rod = CylinderGeometry(BOW_BAR_R, stub_len, radial_segments=12)
    rod.rotate_x(math.pi / 2.0)  # +Z cylinder -> along Y
    rod.translate(0.0, stub_len / 2.0, 0.0)  # inboard cap face at origin, body +Y
    bar.merge(rod)
    return mesh_from_geometry(bar, "bow_guard_tube")


def _bow_anchor_pad_mesh(name: str, sign: float, inner_r: float, outer_r: float) -> object:
    """Anchor-pad boss bridging the body shell shoulder (at ``inner_r``) out to
    the bow leg-end (at ``outer_r=anchor_y``) along the +/-Y pivot line.

    Built as a Y-axis cylinder so it physically embeds into ``body_shell`` (no
    floating island) while still presenting a real pad at the bow leg-end where
    the REVOLUTE origin sits. ``sign`` selects the +Y / -Y side."""
    length = max(outer_r - inner_r + 0.018, 0.024)
    pad = CylinderGeometry(0.0135, length, radial_segments=20)
    pad.rotate_x(math.pi / 2.0)  # +Z cylinder -> along Y
    # Center it so the outboard face reaches just past the pad center (outer_r)
    # and the inboard face penetrates the shell wall (inner_r - a few mm).
    center_y = sign * (outer_r - length / 2.0 + 0.009)
    pad.translate(0.0, center_y, 0.0)
    return mesh_from_geometry(pad, name)


# ---------------------------------------------------------------------------
# Slot B: valve_closure meshes (mechanism on top of the valve stem / block).
# ---------------------------------------------------------------------------
def _handwheel_mesh() -> object:
    """Star handwheel: hub + rim torus + 4 spokes + off-axis lug + tip knob."""
    geom = CylinderGeometry(0.009, 0.012, radial_segments=20)
    rim = TorusGeometry(0.028, 0.005, radial_segments=12, tubular_segments=36)
    geom.merge(rim)
    for i in range(4):
        ang = i * math.pi / 2.0
        spoke = CylinderGeometry(0.0035, 0.046, radial_segments=8).rotate_y(math.pi / 2.0)
        spoke.rotate_z(ang)
        geom.merge(spoke)
    lug = CylinderGeometry(0.0045, 0.034, radial_segments=10).rotate_y(math.pi / 2.0)
    lug.translate(0.038, 0.0, 0.0)
    geom.merge(lug)
    knob = CylinderGeometry(0.007, 0.016, radial_segments=12)
    knob.translate(0.052, 0.0, 0.0)
    geom.merge(knob)
    return mesh_from_geometry(geom, "handwheel")


def _lever_mesh() -> object:
    """Self-closing clip-on lever: pivot hub + +X arm + paddle grip + spring boss."""
    hub = cq.Workplane("XY").workplane(offset=-0.008).circle(0.012).extrude(0.020)
    arm = (
        cq.Workplane("XY")
        .workplane(offset=0.0)
        .center(0.036, 0.0)
        .rect(0.056, 0.010)
        .extrude(0.008)
    )
    hub = hub.union(arm)
    grip = (
        cq.Workplane("XY")
        .workplane(offset=-0.001)
        .center(0.070, 0.0)
        .rect(0.024, 0.020)
        .extrude(0.010)
    )
    hub = hub.union(grip)
    spring_boss = (
        cq.Workplane("XY").workplane(offset=0.001).center(-0.014, 0.0).circle(0.005).extrude(0.006)
    )
    hub = hub.union(spring_boss)
    return mesh_from_cadquery(hub, "lever")


def _bonnet_mesh() -> object:
    """Domed steel screw-cap bonnet: skirt + hemisphere dome + blind bore +
    6 grip ribs + +X indicator lug (breaks symmetry for rotation detection)."""
    outer_r = 0.022
    inner_r = 0.009
    skirt_h = 0.024
    dome_r = outer_r
    cap = cq.Workplane("XY").circle(outer_r).extrude(skirt_h)
    dome = (
        cq.Workplane("XZ")
        .moveTo(0.0, skirt_h)
        .lineTo(outer_r, skirt_h)
        .threePointArc(
            (outer_r * 0.707, skirt_h + dome_r * 0.707),
            (0.0, skirt_h + dome_r),
        )
        .close()
        .revolve(360, (0.0, skirt_h), (0.0, skirt_h + 1.0))
    )
    cap = cap.union(dome)
    bore_depth = skirt_h + dome_r - 0.005
    bore = cq.Workplane("XY").circle(inner_r).extrude(bore_depth)
    cap = cap.cut(bore)
    for i in range(6):
        ang = i * math.pi / 3.0 + math.pi / 6.0
        x = (outer_r + 0.001) * math.cos(ang)
        y = (outer_r + 0.001) * math.sin(ang)
        rib = (
            cq.Workplane("XY")
            .workplane(offset=0.004)
            .center(x, y)
            .circle(0.0015)
            .extrude(skirt_h - 0.008)
        )
        cap = cap.union(rib)
    lug = (
        cq.Workplane("YZ")
        .workplane(offset=outer_r - 0.003)
        .center(0.0, skirt_h * 0.55)
        .circle(0.003)
        .extrude(0.012)
    )
    cap = cap.union(lug)
    return mesh_from_cadquery(cap, "bonnet_cap")


# ---------------------------------------------------------------------------
# Slot C: base meshes.
# ---------------------------------------------------------------------------
def _foot_ring_mesh(
    r: ResolvedContainerGasCylinderConfig,
    x_offset: float = 0.0,
    z_offset: float = 0.0,
) -> object:
    """Dark steel foot-ring skirt at the cylinder base.

    ``x_offset`` / ``z_offset`` pre-shift the revolved ring so a downstream
    FIXED joint whose origin sits on the ring wall (off-axis, up at the foot
    transition where the body shell actually has geometry) re-centers it on the
    cylinder axis at z=0."""
    br = r.body_r
    profile = [
        (br - 0.018, 0.0),
        (br + 0.006, 0.0),
        (br + 0.006, FOOT_TOP_Z),
        (br - 0.004, FOOT_TOP_Z + 0.004),
        (br - 0.018, FOOT_TOP_Z - 0.004),
        (br - 0.018, 0.0),
    ]
    geom = LatheGeometry(profile, segments=64)
    if x_offset or z_offset:
        geom.translate(x_offset, 0.0, z_offset)
    return mesh_from_geometry(geom, "foot_ring")


def _stub_foot_mesh() -> object:
    """Short rounded stub foot block (foot-local: top at z=0, bottom at -FOOT_H).

    X = radial depth, Y = tangential width."""
    foot = cq.Workplane("XY").workplane(offset=-FOOT_H).rect(FOOT_DEPTH, FOOT_WIDTH).extrude(FOOT_H)
    foot = foot.edges("|Z").fillet(0.005)
    return mesh_from_cadquery(foot, "stub_foot")


# ---------------------------------------------------------------------------
# Slot emitters.
# ---------------------------------------------------------------------------
def _emit_top_guard(model, body, r, *, guard_mat) -> None:
    """top_guard slot. Fixed body visuals for ring/collar/cage; a REVOLUTE +Y
    bow_guard part (with two fixed anchor pads) for carry_handle_arch."""
    if r.top_guard == "ring_on_struts":
        body.visual(_collar_struts_mesh(r), material=guard_mat, name="collar_guard", material_class_id=("metal.steel_bare" if r.palette_style in {"industrial_red_lpg", "industrial_blue_lpg", "industrial_grey_steel", "safety_yellow", "medical_white", "forest_green_propane", "galvanized_zinc", "brushed_steel_scuba", "matte_powder_coat"} else "rust.painted_weathered"))
    elif r.top_guard == "solid_neck_collar":
        body.visual(_neck_collar_mesh(r), material=guard_mat, name="neck_collar", material_class_id=("metal.steel_bare" if r.palette_style in {"industrial_red_lpg", "industrial_blue_lpg", "industrial_grey_steel", "safety_yellow", "medical_white", "forest_green_propane", "galvanized_zinc", "brushed_steel_scuba", "matte_powder_coat"} else "rust.painted_weathered"))
    elif r.top_guard == "vented_cage_shroud":
        body.visual(
            _cage_ring_mesh(r, r.collar_ring_z, "cage_top_ring"),
            material=guard_mat,
            name="cage_top_ring", material_class_id=("metal.steel_bare" if r.palette_style in {"industrial_red_lpg", "industrial_blue_lpg", "industrial_grey_steel", "safety_yellow", "medical_white", "forest_green_propane", "galvanized_zinc", "brushed_steel_scuba", "matte_powder_coat"} else "rust.painted_weathered"),
        )
        cage_bottom_z = _cage_bottom_z(r)
        body.visual(
            _cage_ring_mesh(r, cage_bottom_z, "cage_bottom_ring"),
            material=guard_mat,
            name="cage_bottom_ring", material_class_id=("metal.steel_bare" if r.palette_style in {"industrial_red_lpg", "industrial_blue_lpg", "industrial_grey_steel", "safety_yellow", "medical_white", "forest_green_propane", "galvanized_zinc", "brushed_steel_scuba", "matte_powder_coat"} else "rust.painted_weathered"),
        )
        for i in range(r.cage_bar_count):
            body.visual(
                _cage_bar_mesh(r, i, r.cage_bar_count),
                material=guard_mat,
                name=f"cage_bar_{i}", material_class_id=("metal.steel_bare" if r.palette_style in {"industrial_red_lpg", "industrial_blue_lpg", "industrial_grey_steel", "safety_yellow", "medical_white", "forest_green_propane", "galvanized_zinc", "brushed_steel_scuba", "matte_powder_coat"} else "rust.painted_weathered"),
            )
    elif r.top_guard == "carry_handle_arch":
        # Two fixed anchor pads on the shoulder capture the bow ends. The pads
        # ARE real body geometry on the +Y pivot line so the REVOLUTE origin can
        # anchor on the +Y pad (off the hollow axis) and pass the origin check.
        # Shell radius at the pad height -> the pad boss spans from inside the
        # shell wall out to the bow leg-end, so it always embeds in body_shell.
        shell_r_at_pad = _shell_radius_at_z(r, r.bow_anchor_z)
        for i in range(2):
            sign = -1 + 2 * i
            body.visual(
                _bow_anchor_pad_mesh(
                    f"bow_anchor_pad_{i}",
                    sign=float(sign),
                    inner_r=shell_r_at_pad,
                    outer_r=r.bow_anchor_y,
                ),
                origin=Origin(xyz=(0.0, 0.0, r.bow_anchor_z)),
                material=guard_mat,
                name=f"bow_anchor_pad_{i}", material_class_id=("metal.steel_bare" if r.palette_style in {"industrial_red_lpg", "industrial_blue_lpg", "industrial_grey_steel", "safety_yellow", "medical_white", "forest_green_propane", "galvanized_zinc", "brushed_steel_scuba", "matte_powder_coat"} else "rust.painted_weathered"),
            )
        bow_guard = model.part("bow_guard")
        bow_guard.visual(_bow_guard_mesh(r), material=guard_mat, name="bow_guard_tube", material_class_id=("metal.steel_bare" if r.palette_style in {"industrial_red_lpg", "industrial_blue_lpg", "industrial_grey_steel", "safety_yellow", "medical_white", "forest_green_propane", "galvanized_zinc", "brushed_steel_scuba", "matte_powder_coat"} else "rust.painted_weathered"))
        bow_guard.inertial = Inertial.from_geometry(
            Cylinder(radius=BOW_BAR_R, length=2.0 * r.bow_anchor_y),
            mass=0.18,
            origin=Origin(xyz=(0.0, -r.bow_anchor_y, 0.0)),
        )
        # Fore/aft carry-handle swing. The author intent (0.55*pi*travel_scale)
        # reaches ~108deg at the top of the scale range, where the arch tilts far
        # enough to plunge into the shell; clamp to the largest swing that keeps
        # the arch tube clear of the shell surface (derived analytically because
        # the anchor pads intentionally overlap the bow and defeat a part-level
        # clearance query). Symmetric about the upright rest pose.
        base_swing = 0.55 * math.pi * r.joint_travel_scale
        swing = _bow_swing_limit(r, base_swing)
        # Origin on the +Y anchor pad (real geometry); child origin (0,0,0) is the
        # +Y leg-end / short pivot stub, so both dist_parent and dist_child are ~0.
        model.articulation(
            "body_to_bow_guard",
            ArticulationType.REVOLUTE,
            parent=body,
            child=bow_guard,
            origin=Origin(xyz=(0.0, r.bow_anchor_y, r.bow_anchor_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(lower=-swing, upper=swing, effort=4.0, velocity=2.0),
        )


def _emit_valve_closure(model, body, valve, r, *, valve_mat) -> None:
    """valve_closure slot. Each candidate is a REVOLUTE child of the valve."""
    if r.valve_closure == "handwheel_valve":
        handwheel = model.part("handwheel")
        handwheel.visual(_handwheel_mesh(), material=valve_mat, name="handwheel", material_class_id=("metal.brass_polished" if r.palette_style in {"industrial_red_lpg", "industrial_blue_lpg", "industrial_grey_steel", "safety_yellow", "forest_green_propane", "galvanized_zinc", "matte_powder_coat", "weathered_scuffed"} else "metal.chrome_polished"))
        handwheel.inertial = Inertial.from_geometry(Cylinder(radius=0.030, length=0.014), mass=0.05)
        model.articulation(
            "valve_to_handwheel",
            ArticulationType.REVOLUTE,
            parent=valve,
            child=handwheel,
            origin=Origin(xyz=(0.0, 0.0, 0.072)),  # valve-local: top of the stem
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=2.0, velocity=3.0, lower=-4.0 * math.pi, upper=4.0 * math.pi
            ),
        )
    elif r.valve_closure == "lever_clip_valve":
        lever = model.part("lever")
        lever.visual(_lever_mesh(), material=valve_mat, name="lever", material_class_id=("metal.brass_polished" if r.palette_style in {"industrial_red_lpg", "industrial_blue_lpg", "industrial_grey_steel", "safety_yellow", "forest_green_propane", "galvanized_zinc", "matte_powder_coat", "weathered_scuffed"} else "metal.chrome_polished"))
        lever.inertial = Inertial.from_geometry(
            Box((0.090, 0.020, 0.012)),
            mass=0.04,
            origin=Origin(xyz=(0.035, 0.0, 0.004)),
        )
        # Rest the arm tilted UP by LEVER_REST_TILT (origin rpy about the +Y pivot
        # axis) so at theta=0 it points up-and-out, clear of the guard/shell; a
        # positive theta (+Y) presses it DOWN toward horizontal to open. Because
        # rest is above horizontal, the swept band never dips into the body until
        # theta passes horizontal — the exact open limit vs. the neck collar / cage
        # / shell surface is derived by the clearance solver in the build entry
        # point (keepout=body), so no config plunges the lever into the cylinder.
        upper = 1.05 * r.joint_travel_scale
        model.articulation(
            "valve_to_lever",
            ArticulationType.REVOLUTE,
            parent=valve,
            child=lever,
            # valve-local: top of the stem, tilted up so the arm rests above the guard.
            origin=Origin(xyz=(0.0, 0.0, 0.072), rpy=(0.0, -LEVER_REST_TILT, 0.0)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=4.0, lower=0.0, upper=upper),
        )
    elif r.valve_closure == "screw_bonnet_cap":
        bonnet = model.part("bonnet")
        bonnet.visual(_bonnet_mesh(), material=valve_mat, name="bonnet_cap", material_class_id=("metal.brass_polished" if r.palette_style in {"industrial_red_lpg", "industrial_blue_lpg", "industrial_grey_steel", "safety_yellow", "forest_green_propane", "galvanized_zinc", "matte_powder_coat", "weathered_scuffed"} else "metal.chrome_polished"))
        bonnet.inertial = Inertial.from_geometry(Cylinder(radius=0.022, length=0.034), mass=0.06)
        model.articulation(
            "valve_to_bonnet",
            ArticulationType.REVOLUTE,
            parent=valve,
            child=bonnet,
            origin=Origin(xyz=(0.0, 0.0, 0.046)),  # valve-local: top of main block
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=6.0 * math.pi),
        )


def _emit_base(model, body, r, *, foot_mat) -> None:
    """base slot. foot_ring = 1 FIXED part; concave = none; n_feet = N FIXED parts."""
    if r.base == "foot_ring":
        # Anchor the FIXED joint origin on the foot-ring wall AT the foot
        # transition height (z=FOOT_TOP_Z) — real geometry on BOTH the body
        # shell base edge (the shell bottom sits at ~z=0.025-0.030, NOT z=0)
        # and the foot skirt — not the hollow axis center at z=0, so
        # fail_if_articulation_origin_far_from_geometry passes (dist_parent and
        # dist_child both within tol). The ring mesh is authored pre-shifted by
        # -origin so the joint translation lands it back centered on the
        # cylinder axis at z=0 (fence_cascade pattern).
        anchor_x = r.body_r - 0.006
        anchor_z = FOOT_TOP_Z
        foot = model.part("foot_ring")
        foot.visual(
            _foot_ring_mesh(r, x_offset=-anchor_x, z_offset=-anchor_z),
            material=foot_mat,
            name="foot_ring", material_class_id="metal.paint_coated",
        )
        foot.inertial = Inertial.from_geometry(
            Cylinder(radius=r.body_r, length=FOOT_TOP_Z),
            mass=1.2,
            origin=Origin(xyz=(-anchor_x, 0.0, -anchor_z + FOOT_TOP_Z / 2.0)),
        )
        model.articulation(
            "body_to_foot",
            ArticulationType.FIXED,
            parent=body,
            child=foot,
            origin=Origin(xyz=(anchor_x, 0.0, anchor_z)),
        )
    elif r.base == "concave_recessed_base":
        # No separate base part: the dished base is folded into the body shell.
        pass
    elif r.base == "n_feet_base":
        shared_foot_mesh = _stub_foot_mesh()
        for i in range(r.foot_count):
            theta = i * (2.0 * math.pi / r.foot_count)
            foot_part = model.part(f"foot_{i}")
            foot_part.visual(shared_foot_mesh, material=foot_mat, name="stub_foot", material_class_id="metal.paint_coated")
            foot_part.inertial = Inertial.from_geometry(
                Box((FOOT_DEPTH, FOOT_WIDTH, FOOT_H)),
                mass=0.3,
                origin=Origin(xyz=(0.0, 0.0, -FOOT_H / 2.0)),
            )
            model.articulation(
                f"body_to_foot_{i}",
                ArticulationType.FIXED,
                parent=body,
                child=foot_part,
                origin=Origin(
                    xyz=(r.foot_r * math.cos(theta), r.foot_r * math.sin(theta), FOOT_TOP_Z),
                    rpy=(0.0, 0.0, theta),
                ),
            )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_gas_cylinder(
    config: ContainerGasCylinderConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    body_mat = model.material(f"cgc_body_{r.palette_style}", rgba=pal.body)
    valve_mat = model.material(f"cgc_valve_{r.palette_style}", rgba=pal.valve)
    guard_mat = model.material(f"cgc_guard_{r.palette_style}", rgba=pal.guard)
    foot_mat = model.material(f"cgc_foot_{r.palette_style}", rgba=pal.foot)
    hazard_mat = model.material(f"cgc_hazard_{r.palette_style}", rgba=_HAZARD)

    # --- ROOT: lathed steel body shell (+ hazard label) --------------------
    body = model.part("body")
    body.visual(_body_mesh(r), material=body_mat, name="body_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_red_lpg", "industrial_blue_lpg", "industrial_grey_steel", "safety_yellow", "medical_white", "forest_green_propane", "galvanized_zinc", "brushed_steel_scuba", "matte_powder_coat"} else "rust.painted_weathered"))
    body.visual(
        Box((0.006, 0.075, 0.075)),
        origin=Origin(xyz=(r.body_r - 0.001, 0.0, 0.165), rpy=(math.pi / 4.0, 0.0, 0.0)),
        material=hazard_mat,
        name="hazard_label", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    body.inertial = Inertial.from_geometry(
        Cylinder(radius=r.body_r, length=r.wall_top_z),
        mass=12.0,
        origin=Origin(xyz=(0.0, 0.0, r.wall_top_z / 2.0)),
    )

    # --- top_guard ----------------------------------------------------------
    _emit_top_guard(model, body, r, guard_mat=guard_mat)

    # --- brass valve (fixed skeleton) on the neck boss ----------------------
    valve = model.part("valve")
    valve.visual(_valve_mesh(), material=valve_mat, name="valve_body", material_class_id=("metal.brass_polished" if r.palette_style in {"industrial_red_lpg", "industrial_blue_lpg", "industrial_grey_steel", "safety_yellow", "forest_green_propane", "galvanized_zinc", "matte_powder_coat", "weathered_scuffed"} else "metal.chrome_polished"))
    valve.inertial = Inertial.from_geometry(
        Cylinder(radius=0.026, length=0.046),
        mass=0.4,
        origin=Origin(xyz=(0.0, 0.0, 0.023)),
    )
    model.articulation(
        "body_to_valve",
        ArticulationType.FIXED,
        parent=body,
        child=valve,
        origin=Origin(xyz=(0.0, 0.0, r.valve_axis_z - 0.006)),
    )

    # --- valve_closure mechanism --------------------------------------------
    _emit_valve_closure(model, body, valve, r, valve_mat=valve_mat)

    # --- base ---------------------------------------------------------------
    _emit_base(model, body, r, foot_mat=foot_mat)

    # --- clearance-solved lever travel --------------------------------------
    # The self-closing lever presses DOWN toward the body; solve the open limit
    # against the body part (shell + neck collar + cage bars are all body
    # elements) so no config (tall shell dome, tight solid neck collar, cage
    # guard) lets the arm penetrate the cylinder. The lever/valve hub-bore fit is
    # intentional (declared element-scoped in the tests) and the valve is not in
    # the keep-out set, so only the real body surface constrains the swing.
    if r.valve_closure == "lever_clip_valve":
        clamp_joint_limits(model, "valve_to_lever", margin=0.008, keepout=["body"])

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_gas_cylinder(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_gas_cylinder(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (valve seat in neck boss, foot skirt over
# the base edge, lever clip over the stem, bonnet over the stem tip, bow pads
# capturing the bow ends) are declared element-scoped so the sweep's
# island/overlap checks pass; every mechanism action is exercised.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_gas_cylinder_tests(
    object_model: ArticulatedObject,
    config: ContainerGasCylinderConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("body")
    valve = object_model.get_part("valve")

    # ---- body: tall thick-walled cylinder with a domed top ----
    body_aabb = ctx.part_world_aabb(body)
    bext = _ext(body_aabb)
    # Category identity: height >> diameter. The strict relative invariant
    # (z-extent > diameter) is the real discriminator vs. squat cans / boxes; the
    # absolute floor is kept generous (well below the ~0.41 m that the low end of
    # body_height_scale=0.88 legitimately produces) so the scale range does not
    # trip it. The body z-extent runs from the foot transition up to the guard /
    # shell top, slightly under the resolved neck height.
    ctx.check(
        "cylinder body is tall (height > diameter)",
        bext[2] > 0.38 and bext[2] > max(bext[0], bext[1]),
        details=f"body extents={bext}",
    )
    # The cylinder body shell bottom-center sits just above the foot transition
    # (~z=0.025 on the standard profile); ground contact is the base part (foot
    # ring / stub feet) or the dished rim, asserted in the per-base block below.
    ctx.check(
        "body shell base is near the ground (foot transition height)",
        body_aabb[0][2] < 0.030,
        details=f"body min z={body_aabb[0][2]:.4f}",
    )
    shell = ctx.part_element_world_aabb(body, elem="body_shell")
    # The shell tops out at the neck boss (r.neck_top_z); assert it reaches near
    # that resolved height (allowing the height_scale range 0.88-1.15) rather
    # than a fixed floor that the low end of the scale would undershoot.
    ctx.check(
        "body shell reaches near full target height",
        shell is not None and shell[1][2] > r.neck_top_z - 0.020,
        details=f"shell top={shell[1] if shell else None}, neck_top_z={r.neck_top_z:.4f}",
    )

    # ---- valve fixed on top, on the axis, above the wall ----
    valve_pos = ctx.part_world_position(valve)
    ctx.check(
        "valve mounted on top of the cylinder, on the axis",
        valve_pos is not None
        and valve_pos[2] > r.wall_top_z
        and abs(valve_pos[0]) < 0.02
        and abs(valve_pos[1]) < 0.02,
        details=f"valve origin={valve_pos}",
    )
    ctx.allow_overlap(
        valve,
        body,
        elem_a="valve_body",
        elem_b="body_shell",
        reason="Brass valve seat boss is intentionally threaded into the steel neck boss.",
    )

    # ============================ top_guard =============================
    if r.top_guard == "ring_on_struts":
        guard_aabb = ctx.part_element_world_aabb(body, elem="collar_guard")
        ctx.check(
            "collar guard ring is above the valve (guards it)",
            guard_aabb is not None and guard_aabb[1][2] >= valve_pos[2],
            details=f"collar top z={guard_aabb[1][2] if guard_aabb else None}",
        )
        ctx.check(
            "collar ring encircles the valve",
            guard_aabb is not None and (guard_aabb[1][0] - guard_aabb[0][0]) > 0.10,
            details=f"collar x-span={guard_aabb[1][0] - guard_aabb[0][0] if guard_aabb else None}",
        )
    elif r.top_guard == "solid_neck_collar":
        guard_aabb = ctx.part_element_world_aabb(body, elem="neck_collar")
        ctx.allow_overlap(
            body,
            valve,
            elem_a="neck_collar",
            elem_b="valve_body",
            reason="The solid neck collar wall intentionally surrounds the valve body.",
        )
        ctx.check(
            "neck collar rises above the valve",
            guard_aabb is not None and guard_aabb[1][2] >= valve_pos[2],
            details=f"collar top z={guard_aabb[1][2] if guard_aabb else None}",
        )
    elif r.top_guard == "vented_cage_shroud":
        # Every cage bar visual exists.
        for i in range(r.cage_bar_count):
            ctx.check(
                f"cage_bar_{i} visual exists",
                body.get_visual(f"cage_bar_{i}") is not None,
                details=f"cage_bar_{i} not found",
            )
        top_ring = ctx.part_element_world_aabb(body, elem="cage_top_ring")
        ctx.check(
            "cage top ring is above the valve",
            top_ring is not None and top_ring[1][2] >= valve_pos[2],
            details=f"cage top z={top_ring[1][2] if top_ring else None}",
        )
    elif r.top_guard == "carry_handle_arch":
        bow = object_model.get_part("bow_guard")
        bow_joint = object_model.get_articulation("body_to_bow_guard")
        ctx.allow_overlap(
            bow,
            body,
            elem_a="bow_guard_tube",
            elem_b="bow_anchor_pad_0",
            reason="The bow handle end is captured by anchor pad 0.",
        )
        ctx.allow_overlap(
            bow,
            body,
            elem_a="bow_guard_tube",
            elem_b="bow_anchor_pad_1",
            reason="The bow handle end is captured by anchor pad 1.",
        )
        ctx.check(
            "body_to_bow_guard is REVOLUTE about +Y",
            bow_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(bow_joint.axis[1]) > 0.99,
            details=f"axis={bow_joint.axis}, type={bow_joint.articulation_type}",
        )
        # The bow swings fore/aft: at rest it arches up, swung the peak moves in x.
        # Pose to the derived (clamped) swing limit — the largest travel the shell
        # clearance permits — so the check tracks the real mechanism envelope.
        rest = ctx.part_world_aabb(bow)
        rest_cx = (rest[0][0] + rest[1][0]) / 2.0
        with ctx.pose({bow_joint: bow_joint.motion_limits.upper}):
            swung = ctx.part_world_aabb(bow)
            swung_cx = (swung[0][0] + swung[1][0]) / 2.0
        ctx.check(
            "bow guard swings fore/aft (peak moves in x)",
            abs(swung_cx - rest_cx) > 0.02,
            details=f"rest_cx={rest_cx:.4f}, swung_cx={swung_cx:.4f}",
        )
        # The clamped swing must remain a usable carry-handle motion (not clamped
        # to a sliver by a future geometry regression).
        ctx.check(
            "bow guard retains a usable swing after shell-clearance clamp",
            bow_joint.motion_limits.upper > 0.6,
            details=f"clamped swing={bow_joint.motion_limits.upper:.3f} rad",
        )

    # =========================== valve_closure ==========================
    if r.valve_closure == "handwheel_valve":
        handwheel = object_model.get_part("handwheel")
        wheel_joint = object_model.get_articulation("valve_to_handwheel")
        ctx.expect_contact(handwheel, valve, name="handwheel seated on valve stem")
        wheel_pos = ctx.part_world_position(handwheel)
        ctx.check(
            "handwheel on the valve axis, above the valve",
            wheel_pos is not None
            and abs(wheel_pos[0]) < 0.02
            and abs(wheel_pos[1]) < 0.02
            and wheel_pos[2] > valve_pos[2],
            details=f"handwheel origin={wheel_pos}",
        )
        ctx.check(
            "valve_to_handwheel is REVOLUTE about +Z",
            wheel_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(wheel_joint.axis[2]) > 0.99,
            details=f"axis={wheel_joint.axis}",
        )
        rest = ctx.part_world_aabb(handwheel)
        rest_xspan = rest[1][0] - rest[0][0]
        rest_yspan = rest[1][1] - rest[0][1]
        with ctx.pose({wheel_joint: math.pi / 2.0}):
            turn = ctx.part_world_aabb(handwheel)
            turn_xspan = turn[1][0] - turn[0][0]
            turn_yspan = turn[1][1] - turn[0][1]
        ctx.check(
            "handwheel quarter-turn rotates the off-axis lug",
            (rest_xspan > rest_yspan + 0.004) and (turn_yspan > turn_xspan + 0.004),
            details=f"rest=({rest_xspan:.3f},{rest_yspan:.3f}) turned=({turn_xspan:.3f},{turn_yspan:.3f})",
        )
    elif r.valve_closure == "lever_clip_valve":
        lever = object_model.get_part("lever")
        lever_joint = object_model.get_articulation("valve_to_lever")
        ctx.allow_overlap(
            lever,
            valve,
            elem_a="lever",
            elem_b="valve_body",
            reason="Clip-on lever hub bore intentionally wraps around the valve stem top.",
        )
        ctx.expect_contact(lever, valve, name="lever pivot hub seated on valve stem top")
        lever_pos = ctx.part_world_position(lever)
        ctx.check(
            "lever pivot is on the valve axis, above the valve",
            lever_pos is not None
            and abs(lever_pos[0]) < 0.02
            and abs(lever_pos[1]) < 0.02
            and lever_pos[2] > valve_pos[2],
            details=f"lever origin={lever_pos}",
        )
        ctx.check(
            "valve_to_lever joint axis is horizontal (no +Z component)",
            lever_joint.axis is not None and abs(lever_joint.axis[2]) < 0.01,
            details=f"axis={lever_joint.axis}",
        )
        rest_aabb = ctx.part_world_aabb(lever)
        rest_tip_z = (rest_aabb[0][2] + rest_aabb[1][2]) / 2.0
        # Press to the solver-clamped open limit (the real max travel vs. the body
        # surface); the up-tilted rest arm must drop when pressed toward horizontal.
        open_limit = lever_joint.motion_limits.upper
        with ctx.pose({lever_joint: open_limit}):
            open_aabb = ctx.part_world_aabb(lever)
        ctx.check(
            "lever pushed down drops the tip below rest (opens valve)",
            open_aabb[0][2] < rest_tip_z - 0.010,
            details=(
                f"rest_tip_z={rest_tip_z:.3f}, open_min_z={open_aabb[0][2]:.3f}, "
                f"open_limit={open_limit:.3f}"
            ),
        )
        # The solved travel must remain a meaningful lever motion (not clamped to a
        # sliver): guards against a future geometry regression that would leave the
        # arm with nowhere to swing.
        ctx.check(
            "lever retains a usable open swing after clearance solve",
            open_limit > 0.20,
            details=f"solved open limit={open_limit:.3f} rad",
        )
    elif r.valve_closure == "screw_bonnet_cap":
        bonnet = object_model.get_part("bonnet")
        bonnet_joint = object_model.get_articulation("valve_to_bonnet")
        ctx.allow_overlap(
            bonnet,
            valve,
            elem_a="bonnet_cap",
            elem_b="valve_body",
            reason="Valve stem tip is intentionally nested inside the bonnet dome ceiling.",
        )
        ctx.expect_contact(bonnet, valve, name="bonnet cap seated on valve body")
        bonnet_pos = ctx.part_world_position(bonnet)
        ctx.check(
            "bonnet on the valve axis, above the valve",
            bonnet_pos is not None
            and abs(bonnet_pos[0]) < 0.02
            and abs(bonnet_pos[1]) < 0.02
            and bonnet_pos[2] > valve_pos[2],
            details=f"bonnet origin={bonnet_pos}",
        )
        ctx.check(
            "valve_to_bonnet is REVOLUTE about +Z",
            bonnet_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(bonnet_joint.axis[2]) > 0.99,
            details=f"axis={bonnet_joint.axis}",
        )
        rest = ctx.part_world_aabb(bonnet)
        rest_xspan = rest[1][0] - rest[0][0]
        rest_yspan = rest[1][1] - rest[0][1]
        with ctx.pose({bonnet_joint: math.pi / 2.0}):
            turn = ctx.part_world_aabb(bonnet)
            turn_xspan = turn[1][0] - turn[0][0]
            turn_yspan = turn[1][1] - turn[0][1]
        ctx.check(
            "bonnet quarter-turn rotates the indicator lug",
            (rest_xspan > rest_yspan + 0.001) and (turn_yspan > turn_xspan + 0.001),
            details=f"rest=({rest_xspan:.4f},{rest_yspan:.4f}) turned=({turn_xspan:.4f},{turn_yspan:.4f})",
        )

    # ============================== base ===============================
    if r.base == "foot_ring":
        foot = object_model.get_part("foot_ring")
        foot_aabb = ctx.part_world_aabb(foot)
        ctx.check(
            "foot ring is at the base",
            foot_aabb is not None and foot_aabb[0][2] < 0.005 and foot_aabb[1][2] < 0.045,
            details=f"foot aabb z=({foot_aabb[0][2]:.3f},{foot_aabb[1][2]:.3f})",
        )
        ctx.allow_overlap(
            foot,
            body,
            elem_a="foot_ring",
            elem_b="body_shell",
            reason="Steel foot ring skirt is intentionally seated up around the cylinder base edge.",
        )
        ctx.expect_contact(foot, body, name="foot ring attached to cylinder base")
    elif r.base == "concave_recessed_base":
        part_names = [p.name for p in object_model.parts]
        ctx.check(
            "no separate foot_ring part exists (base is integral dished form)",
            "foot_ring" not in part_names,
            details=f"part names={part_names}",
        )
        ctx.check(
            "body outer rim rests on the ground",
            abs(body_aabb[0][2]) < 0.008,
            details=f"body min z={body_aabb[0][2]:.4f}",
        )
    elif r.base == "n_feet_base":
        for i in range(r.foot_count):
            foot_part = object_model.get_part(f"foot_{i}")
            fa = ctx.part_world_aabb(foot_part)
            ctx.check(
                f"foot_{i} stands on the ground",
                fa is not None and fa[0][2] < 0.006,
                details=f"foot_{i} min z={fa[0][2] if fa else None}",
            )
            ctx.allow_overlap(
                foot_part,
                body,
                elem_a="stub_foot",
                elem_b="body_shell",
                reason="Stub foot top is intentionally seated up against the cylinder base.",
            )
            ctx.expect_contact(foot_part, body, name=f"foot_{i} attached to cylinder base")

    # ---- at least one non-fixed valve mechanism joint exists ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed mechanism joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()
