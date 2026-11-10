# SPDX-License-Identifier: Apache-2.0

"""Agricultural hand cultivator (walk-behind wheel-hoe) modular template.

Structure family (pattern = ``mixed``): a single rigid ``frame`` root part (long
handles + steel fork/braces + rear working head + axle hardware + rivets, all
FIXED so they are inlined as ``frame.visual(...)`` per AUTHORING §A Rule 1) and
ONE separate ``tine_wheel`` part joined by the sole non-fixed joint
``wheel_axle`` (CONTINUOUS, axis (0,1,0), origin (0,0,axle_z)).  The wheel hub
captures the frame ``axle_pin`` (element-scoped ``allow_overlap`` — grandfathered
pin-through-hub, no MatingContract, Rule 2).

Three named module axes vary structure (each a slot registered into
``slot_choices``):

  * ``working_head`` (5, the ③ Primary Form Family star): spring_tine_claws /
    rigid_tines (Volumetric Envelope swept tubes) · stirrup_hoe / sweep (Planar
    Boundary flat blades) · ridger (Macro Surface Construction moldboard shell).
  * ``ground_wheel`` (3): spoked_iron (_torus_y rims + N spokes) / solid_disc
    (iron disc plate) / pneumatic (SDK WheelGeometry + TireGeometry).
  * ``handle_config`` (2): double_straight twin handles / single_central tiller.

Multiplicity: ``n_tines`` in [3,9] — the rear tine count, emitted as a loop of
identical FIXED visuals on ``rake_crossbar``; CONDITIONAL, present only for the
tine heads {spring_tine_claws, rigid_tines}. Secondary ``n_spokes`` in [6,16]
covers only spoked_iron. N never counts toward structural distinctness.

Sourced from ``specs_modular_v1/hand_cultivator.md`` and the 10 5-star samples
(1 origin + 9 slot-fork variants) synced under ``data/records/``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    BoltPattern,
    Cylinder,
    MeshGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireShoulder,
    TireSidewall,
    TireTread,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

WorkingHead = Literal["spring_tine_claws", "rigid_tines", "stirrup_hoe", "sweep", "ridger"]
GroundWheel = Literal["spoked_iron", "solid_disc", "pneumatic"]
HandleConfig = Literal["double_straight", "single_central"]
PaletteStyle = Literal[
    "rusted_iron", "painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"
]

WORKING_HEADS: tuple[WorkingHead, ...] = (
    "spring_tine_claws",
    "rigid_tines",
    "stirrup_hoe",
    "sweep",
    "ridger",
)
GROUND_WHEELS: tuple[GroundWheel, ...] = ("spoked_iron", "solid_disc", "pneumatic")
HANDLE_CONFIGS: tuple[HandleConfig, ...] = ("double_straight", "single_central")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "rusted_iron",
    "painted_green",
    "painted_red",
    "galvanized",
    "blued_steel",
    "planet_jr",
)

# Tine heads carry the n_tines multiplicity; blade heads are single-blade.
TINE_HEADS: tuple[WorkingHead, ...] = ("spring_tine_claws", "rigid_tines")

N_TINES_MIN, N_TINES_MAX = 3, 9
# spec §8: 5 typical, small N high-frequency, large N long tail.
_N_TINES_CHOICES = (3, 5, 7, 9)
_N_TINES_WEIGHTS = (0.30, 0.40, 0.20, 0.10)

N_SPOKES_MIN, N_SPOKES_MAX = 6, 16
_N_SPOKES_CHOICES = (6, 8, 12, 16)
_N_SPOKES_WEIGHTS = (0.30, 0.40, 0.20, 0.10)

# ---------------------------------------------------------------------------
# Palettes (⑥). Each: wood handle + rubber grip + frame steel (palette main) +
# wheel metal + head-blade metal + dark hardware + spring-steel tint + bright
# worn edge + black tire rubber. Material families: metal + wood + rubber (>=3).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "rusted_iron": {
        "wood": (0.78, 0.64, 0.42, 1.0),
        "grip": (0.035, 0.038, 0.035, 1.0),
        "metal": (0.53, 0.26, 0.13, 1.0),
        "wheel": (0.50, 0.25, 0.13, 1.0),
        "blade": (0.55, 0.28, 0.15, 1.0),
        "dark": (0.055, 0.050, 0.045, 1.0),
        "spring": (0.12, 0.14, 0.15, 1.0),
        "worn": (0.72, 0.70, 0.64, 1.0),
        "tire": (0.05, 0.05, 0.055, 1.0),
    },
    "painted_green": {
        "wood": (0.72, 0.57, 0.36, 1.0),
        "grip": (0.03, 0.03, 0.03, 1.0),
        "metal": (0.15, 0.42, 0.23, 1.0),
        "wheel": (0.14, 0.40, 0.22, 1.0),
        "blade": (0.17, 0.45, 0.25, 1.0),
        "dark": (0.06, 0.09, 0.07, 1.0),
        "spring": (0.10, 0.22, 0.14, 1.0),
        "worn": (0.78, 0.78, 0.72, 1.0),
        "tire": (0.05, 0.05, 0.055, 1.0),
    },
    "painted_red": {
        "wood": (0.74, 0.58, 0.36, 1.0),
        "grip": (0.03, 0.03, 0.03, 1.0),
        "metal": (0.62, 0.13, 0.11, 1.0),
        "wheel": (0.58, 0.12, 0.10, 1.0),
        "blade": (0.66, 0.16, 0.13, 1.0),
        "dark": (0.10, 0.05, 0.05, 1.0),
        "spring": (0.28, 0.10, 0.10, 1.0),
        "worn": (0.80, 0.78, 0.72, 1.0),
        "tire": (0.05, 0.05, 0.055, 1.0),
    },
    "galvanized": {
        "wood": (0.80, 0.67, 0.45, 1.0),
        "grip": (0.05, 0.05, 0.05, 1.0),
        "metal": (0.66, 0.68, 0.70, 1.0),
        "wheel": (0.63, 0.66, 0.68, 1.0),
        "blade": (0.70, 0.72, 0.74, 1.0),
        "dark": (0.28, 0.30, 0.32, 1.0),
        "spring": (0.42, 0.45, 0.48, 1.0),
        "worn": (0.86, 0.87, 0.88, 1.0),
        "tire": (0.06, 0.06, 0.065, 1.0),
    },
    "blued_steel": {
        "wood": (0.62, 0.47, 0.28, 1.0),
        "grip": (0.03, 0.03, 0.035, 1.0),
        "metal": (0.16, 0.19, 0.26, 1.0),
        "wheel": (0.15, 0.18, 0.25, 1.0),
        "blade": (0.19, 0.23, 0.30, 1.0),
        "dark": (0.05, 0.06, 0.08, 1.0),
        "spring": (0.10, 0.12, 0.17, 1.0),
        "worn": (0.74, 0.77, 0.82, 1.0),
        "tire": (0.05, 0.05, 0.055, 1.0),
    },
    "planet_jr": {
        "wood": (0.74, 0.60, 0.38, 1.0),
        "grip": (0.03, 0.03, 0.03, 1.0),
        "metal": (0.14, 0.40, 0.22, 1.0),
        "wheel": (0.85, 0.72, 0.12, 1.0),  # signature yellow wheel
        "blade": (0.16, 0.44, 0.24, 1.0),
        "dark": (0.06, 0.08, 0.06, 1.0),
        "spring": (0.10, 0.22, 0.14, 1.0),
        "worn": (0.80, 0.79, 0.70, 1.0),
        "tire": (0.05, 0.05, 0.055, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Fixed frame reference geometry (meters). Rear (x<0) holds head + operator;
# the wheel sits at the front (x=0) on the axle line. These match the origin
# record so head coordinates can be adopted verbatim (Rule 3).
# ---------------------------------------------------------------------------
BASE_WHEEL_R = 0.300
AXLE_GROUND_OFFSET = 0.030  # wheel bottom clearance (constant across scale)

RAIL_Y = 0.074  # side_rail y offset (fork straddles the wheel plane)
RAIL_MID_X = -0.34
HEAD_X = -0.72  # side_rail rear / head_crossbar x
HEAD_Z = 0.18
HEAD_Y = 0.055  # side_rail rear y = head_crossbar half span
NECK_X = -0.88  # rake_crossbar x (working-head root)
NECK_Z = 0.125
CB_HALF = 0.22  # rake_crossbar half span
TINE_MARGIN = 0.02  # keep tine row inside the crossbar ends


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class HandCultivatorConfig:
    working_head: WorkingHead | None = None
    ground_wheel: GroundWheel | None = None
    handle_config: HandleConfig | None = None
    palette_style: PaletteStyle = "rusted_iron"
    n_tines: int | None = None
    n_spokes: int | None = None
    wheel_radius_scale: float = 1.0
    handle_len_scale: float = 1.0
    handle_spread_scale: float = 1.0
    head_depth_scale: float = 1.0
    tine_spacing_scale: float = 1.0
    name: str = "hand_cultivator"


@dataclass(frozen=True)
class ResolvedHandCultivatorConfig:
    working_head: WorkingHead
    ground_wheel: GroundWheel
    handle_config: HandleConfig
    palette_style: PaletteStyle
    n_tines: int
    n_spokes: int
    wheel_r: float
    axle_z: float
    handle_len_scale: float
    handle_spread_scale: float
    head_depth_scale: float
    tine_half_span: float
    central_base_z: float
    name: str

    @property
    def is_tine_head(self) -> bool:
        return self.working_head in TINE_HEADS


def config_from_seed(seed: int) -> HandCultivatorConfig:
    rng = random.Random(seed)
    return HandCultivatorConfig(
        working_head=rng.choice(WORKING_HEADS),
        ground_wheel=rng.choice(GROUND_WHEELS),
        handle_config=rng.choice(HANDLE_CONFIGS),
        palette_style=rng.choice(PALETTE_STYLES),
        n_tines=rng.choices(_N_TINES_CHOICES, weights=_N_TINES_WEIGHTS, k=1)[0],
        n_spokes=rng.choices(_N_SPOKES_CHOICES, weights=_N_SPOKES_WEIGHTS, k=1)[0],
        wheel_radius_scale=round(rng.uniform(0.82, 1.30), 4),
        handle_len_scale=round(rng.uniform(0.88, 1.15), 4),
        handle_spread_scale=round(rng.uniform(0.85, 1.20), 4),
        head_depth_scale=round(rng.uniform(0.85, 1.20), 4),
        tine_spacing_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_hand_cultivator_{seed}",
    )


def resolve_config(config: HandCultivatorConfig | None = None) -> ResolvedHandCultivatorConfig:
    cfg = config or HandCultivatorConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    working_head = _pick(cfg.working_head, WORKING_HEADS)
    ground_wheel = _pick(cfg.ground_wheel, GROUND_WHEELS)
    handle_config = _pick(cfg.handle_config, HANDLE_CONFIGS)

    n_tines = int(cfg.n_tines) if cfg.n_tines is not None else 5
    n_tines = int(_clamp(n_tines, N_TINES_MIN, N_TINES_MAX))
    n_spokes = int(cfg.n_spokes) if cfg.n_spokes is not None else 8
    n_spokes = int(_clamp(n_spokes, N_SPOKES_MIN, N_SPOKES_MAX))

    wheel_radius_scale = _clamp(cfg.wheel_radius_scale, 0.82, 1.30)
    handle_len_scale = _clamp(cfg.handle_len_scale, 0.88, 1.15)
    handle_spread_scale = _clamp(cfg.handle_spread_scale, 0.85, 1.20)
    head_depth_scale = _clamp(cfg.head_depth_scale, 0.85, 1.20)
    tine_spacing_scale = _clamp(cfg.tine_spacing_scale, 0.85, 1.15)

    wheel_r = BASE_WHEEL_R * wheel_radius_scale
    axle_z = wheel_r + AXLE_GROUND_OFFSET

    # Inequality (spec §7): tine row must fit inside the crossbar.
    tine_half_span = _clamp(0.18 * tine_spacing_scale, 0.06, CB_HALF - TINE_MARGIN)

    # Inequality (spec §7): a single central handle must start above the wheel
    # top (axle_z + wheel_r) + clearance, else it fouls the spinning wheel.
    wheel_top = axle_z + wheel_r
    central_base_z = max(0.72, wheel_top + 0.09)

    return ResolvedHandCultivatorConfig(
        working_head=working_head,
        ground_wheel=ground_wheel,
        handle_config=handle_config,
        palette_style=palette_style,
        n_tines=n_tines,
        n_spokes=n_spokes,
        wheel_r=wheel_r,
        axle_z=axle_z,
        handle_len_scale=handle_len_scale,
        handle_spread_scale=handle_spread_scale,
        head_depth_scale=head_depth_scale,
        tine_half_span=tine_half_span,
        central_base_z=central_base_z,
        name=cfg.name or "hand_cultivator",
    )


def with_overrides(config: HandCultivatorConfig, **kwargs: object) -> HandCultivatorConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: HandCultivatorConfig | ResolvedHandCultivatorConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedHandCultivatorConfig) else resolve_config(config)
    tine_tag = f"n{r.n_tines}" if r.is_tine_head else "n0"
    spoke_tag = f"s{r.n_spokes}" if r.ground_wheel == "spoked_iron" else "s0"
    return (
        ("working_head", r.working_head),
        ("ground_wheel", r.ground_wheel),
        ("handle_config", r.handle_config),
        ("n_tines", tine_tag),
        ("n_spokes", spoke_tag),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Mesh helpers (primitives preserved from the 5-star sources, Rule 3).
# ---------------------------------------------------------------------------
def _torus_y(
    major_radius: float, tube_radius: float, *, major_segments: int = 72, tube_segments: int = 12
) -> MeshGeometry:
    """Round-section iron hoop in the local XZ plane, spinning about local Y."""
    geom = MeshGeometry()
    for i in range(major_segments):
        theta = 2.0 * math.pi * i / major_segments
        radial = (math.cos(theta), 0.0, math.sin(theta))
        for j in range(tube_segments):
            phi = 2.0 * math.pi * j / tube_segments
            r = major_radius + tube_radius * math.cos(phi)
            geom.add_vertex(r * radial[0], tube_radius * math.sin(phi), r * radial[2])
    for i in range(major_segments):
        ni = (i + 1) % major_segments
        for j in range(tube_segments):
            nj = (j + 1) % tube_segments
            a = i * tube_segments + j
            b = ni * tube_segments + j
            c = ni * tube_segments + nj
            d = i * tube_segments + nj
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
    return geom


def _straight_tube(points, radius: float, *, radial_segments: int = 12) -> MeshGeometry:
    return tube_from_spline_points(
        points,
        radius=radius,
        samples_per_segment=8,
        radial_segments=radial_segments,
        cap_ends=True,
    )


def _wheel_spoke(angle: float, inner: float, outer: float) -> MeshGeometry:
    c, s = math.cos(angle), math.sin(angle)
    return _straight_tube(
        [(inner * c, 0.0, inner * s), (outer * c, 0.0, outer * s)], 0.0065, radial_segments=10
    )


def _wheel_lug(angle: float, wheel_r: float) -> MeshGeometry:
    """A short curved hoe lug embedded in the rim/tread and protruding outward."""
    c, s = math.cos(angle), math.sin(angle)
    tangent = (-s, 0.0, c)
    radial = (c, 0.0, s)
    r0, r1, r2 = wheel_r * 0.98, wheel_r * 1.055, wheel_r * 1.14
    t1, t2 = wheel_r * 0.047, wheel_r * 0.087
    start = (r0 * radial[0], 0.0, r0 * radial[2])
    mid = (r1 * radial[0] + t1 * tangent[0], 0.0, r1 * radial[2] + t1 * tangent[2])
    tip = (r2 * radial[0] + t2 * tangent[0], 0.0, r2 * radial[2] + t2 * tangent[2])
    return _straight_tube([start, mid, tip], wheel_r * 0.018, radial_segments=10)


def _lug_tip(angle: float, wheel_r: float) -> MeshGeometry:
    """Worn bright cap on a lug tip (makes the spinning wheel asymmetric)."""
    c, s = math.cos(angle), math.sin(angle)
    tangent = (-s, 0.0, c)
    radial = (c, 0.0, s)
    ra, rb = wheel_r * 1.11, wheel_r * 1.17
    ta, tb = wheel_r * 0.06, wheel_r * 0.093
    start = (ra * radial[0] + ta * tangent[0], 0.0, ra * radial[2] + ta * tangent[2])
    end = (rb * radial[0] + tb * tangent[0], 0.0, rb * radial[2] + tb * tangent[2])
    return _straight_tube([start, end], wheel_r * 0.02, radial_segments=8)


def _flat_plate(width_y: float, height_z: float, thickness_x: float) -> MeshGeometry:
    """Thin flat plate: thin along X, wide along Y, tall along Z (stirrup blade)."""
    g = MeshGeometry()
    hx, hy, hz = thickness_x / 2, width_y / 2, height_z / 2
    g.add_vertex(-hx, -hy, -hz)
    g.add_vertex(hx, -hy, -hz)
    g.add_vertex(-hx, hy, -hz)
    g.add_vertex(hx, hy, -hz)
    g.add_vertex(-hx, -hy, hz)
    g.add_vertex(hx, -hy, hz)
    g.add_vertex(-hx, hy, hz)
    g.add_vertex(hx, hy, hz)
    g.add_face(0, 2, 1)
    g.add_face(2, 3, 1)
    g.add_face(4, 5, 6)
    g.add_face(5, 7, 6)
    g.add_face(0, 1, 4)
    g.add_face(1, 5, 4)
    g.add_face(2, 6, 3)
    g.add_face(6, 7, 3)
    g.add_face(0, 4, 2)
    g.add_face(4, 6, 2)
    g.add_face(1, 3, 5)
    g.add_face(3, 7, 5)
    return g


def _duckfoot_sweep(base_z: float) -> MeshGeometry:
    """Wide V-shaped duckfoot sweep blade (mesh). Point faces +X; wings sweep -X.
    The blade sits at ``base_z`` (the shank bottom) so the two shank-mount
    vertices (5,6) meet the shank cap; z offsets are relative to the nominal
    0.038 blade plane so the whole plate hangs off ``base_z``."""
    geom = MeshGeometry()
    t = 0.003

    def zz(z: float) -> float:
        return base_z + (z - 0.038)

    profile = [
        (-0.76, 0.00, zz(0.042)),
        (-0.86, -0.10, zz(0.040)),
        (-1.00, -0.22, zz(0.036)),
        (-0.96, -0.16, zz(0.038)),
        (-0.92, -0.04, zz(0.042)),
        (-0.88, -0.010, zz(0.042)),
        (-0.88, 0.010, zz(0.042)),
        (-0.92, 0.04, zz(0.042)),
        (-0.96, 0.16, zz(0.038)),
        (-1.00, 0.22, zz(0.036)),
        (-0.86, 0.10, zz(0.040)),
    ]
    n = len(profile)
    for x, y, z in profile:
        geom.add_vertex(x, y, z + t)
    for x, y, z in profile:
        geom.add_vertex(x, y, z - t)
    for i in range(1, n - 1):
        geom.add_face(0, i, i + 1)
    for i in range(1, n - 1):
        geom.add_face(n, n + i + 1, n + i)
    for i in range(n):
        ni = (i + 1) % n
        geom.add_face(i, ni, n + ni)
        geom.add_face(i, n + ni, n + i)
    return geom


def _ridger_moldboard_surface() -> MeshGeometry:
    """Compound V-wing moldboard surface (Macro Surface Construction)."""
    geom = MeshGeometry()
    nu, nv = 14, 12
    thickness = 0.004

    def surface_point(u: float, v: float):
        x = -0.76 + u * (-1.04 - (-0.76))
        half_width = 0.003 + (u**0.7) * 0.197
        y = v * half_width
        base_z = 0.052 - u * 0.006
        wing_rise = (u**1.3) * (abs(v) ** 1.5) * 0.108
        return (x, y, base_z + wing_rise)

    top_grid: list[list[int]] = []
    for ui in range(nu + 1):
        u = ui / nu
        row: list[int] = []
        for vi in range(nv + 1):
            v = -1.0 + 2.0 * vi / nv
            x, y, z = surface_point(u, v)
            row.append(geom.add_vertex(x, y, z))
        top_grid.append(row)
    bot_grid: list[list[int]] = []
    for ui in range(nu + 1):
        u = ui / nu
        row = []
        for vi in range(nv + 1):
            v = -1.0 + 2.0 * vi / nv
            x, y, z = surface_point(u, v)
            row.append(geom.add_vertex(x, y, z - thickness))
        bot_grid.append(row)
    for ui in range(nu):
        for vi in range(nv):
            a, b = top_grid[ui][vi], top_grid[ui][vi + 1]
            c, d = top_grid[ui + 1][vi + 1], top_grid[ui + 1][vi]
            geom.add_face(a, d, c)
            geom.add_face(a, c, b)
    for ui in range(nu):
        for vi in range(nv):
            a, b = bot_grid[ui][vi], bot_grid[ui][vi + 1]
            c, d = bot_grid[ui + 1][vi + 1], bot_grid[ui + 1][vi]
            geom.add_face(a, c, d)
            geom.add_face(a, b, c)
    for ui in range(nu):
        ta, tb = top_grid[ui][0], top_grid[ui + 1][0]
        ba, bb = bot_grid[ui][0], bot_grid[ui + 1][0]
        geom.add_face(ta, ba, bb)
        geom.add_face(ta, bb, tb)
    for ui in range(nu):
        ta, tb = top_grid[ui][nv], top_grid[ui + 1][nv]
        ba, bb = bot_grid[ui][nv], bot_grid[ui + 1][nv]
        geom.add_face(ta, tb, bb)
        geom.add_face(ta, bb, ba)
    for vi in range(nv):
        ta, tb = top_grid[0][vi], top_grid[0][vi + 1]
        ba, bb = bot_grid[0][vi], bot_grid[0][vi + 1]
        geom.add_face(ta, tb, bb)
        geom.add_face(ta, bb, ba)
    for vi in range(nv):
        ta, tb = top_grid[nu][vi], top_grid[nu][vi + 1]
        ba, bb = bot_grid[nu][vi], bot_grid[nu][vi + 1]
        geom.add_face(ta, bb, tb)
        geom.add_face(ta, ba, bb)
    return geom


def _ridger_share_edge() -> MeshGeometry:
    left = _straight_tube(
        [(-0.76, 0.0, 0.048), (-0.80, -0.052, 0.052), (-0.84, -0.105, 0.060), (-0.88, -0.158, 0.080)],
        0.0055,
        radial_segments=8,
    )
    right = _straight_tube(
        [(-0.76, 0.0, 0.048), (-0.80, 0.052, 0.052), (-0.84, 0.105, 0.060), (-0.88, 0.158, 0.080)],
        0.0055,
        radial_segments=8,
    )
    return left.merge(right)


def _ridger_central_spine() -> MeshGeometry:
    return _straight_tube(
        [(-0.78, 0.0, 0.044), (-0.86, 0.0, 0.042), (-0.94, 0.0, 0.048), (-1.02, 0.0, 0.058)],
        0.006,
        radial_segments=8,
    )


def _depth_pts(points, hd: float):
    """Scale each point's offset from the NECK root by ``hd`` (head depth)."""
    return [
        (NECK_X + (px - NECK_X) * hd, py, NECK_Z + (pz - NECK_Z) * hd) for (px, py, pz) in points
    ]


# ---------------------------------------------------------------------------
# Frame skeleton (root part). Every member shares control points with a
# neighbour so the single frame part is connected within 1µm (template-sweep
# promotes part-internal islands to a hard fail).
# ---------------------------------------------------------------------------
def _rail_mid_z(r: ResolvedHandCultivatorConfig) -> float:
    return (r.axle_z + HEAD_Z) * 0.5 + 0.04


def _build_frame_skeleton(frame, r: ResolvedHandCultivatorConfig, mats) -> None:
    mid_z = _rail_mid_z(r)
    # Twin side rails: front on the axle line, rear on the head crossbar.
    for s, sy in ((0, -1.0), (1, 1.0)):
        frame.visual(
            mesh_from_geometry(
                _straight_tube(
                    [(0.0, sy * RAIL_Y, r.axle_z), (RAIL_MID_X, sy * RAIL_Y, mid_z), (HEAD_X, sy * HEAD_Y, HEAD_Z)],
                    0.0105,
                ),
                f"side_rail_{s}",
            ),
            material=mats["metal"],
            name=f"side_rail_{s}", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
        )
    # Head crossbar spanning the two side-rail rear endpoints exactly.
    frame.visual(
        mesh_from_geometry(
            _straight_tube([(HEAD_X, -HEAD_Y, HEAD_Z), (HEAD_X, HEAD_Y, HEAD_Z)], 0.012), "head_crossbar"
        ),
        material=mats["metal"],
        name="head_crossbar", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    # Rake neck (head crossbar center -> rake crossbar center).
    frame.visual(
        mesh_from_geometry(_straight_tube([(HEAD_X, 0.0, HEAD_Z), (NECK_X, 0.0, NECK_Z)], 0.012), "rake_neck"),
        material=mats["metal"],
        name="rake_neck", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    # Rake crossbar (working-head root); passes through the rake-neck rear end.
    frame.visual(
        mesh_from_geometry(
            _straight_tube([(NECK_X, -CB_HALF, NECK_Z), (NECK_X, CB_HALF, NECK_Z)], 0.011), "rake_crossbar"
        ),
        material=mats["metal"],
        name="rake_crossbar", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    # Axle pin along Y at the axle center; captured by the wheel hub. Touches
    # both side-rail front endpoints (which sit on the pin axis).
    frame.visual(
        Cylinder(radius=0.009, length=0.220),
        origin=Origin(xyz=(0.0, 0.0, r.axle_z), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name="axle_pin", material_class_id="metal.blackened_gunmetal",
    )
    for k, y in ((0, -0.116), (1, 0.116)):
        frame.visual(
            Cylinder(radius=0.020, length=0.020),
            origin=Origin(xyz=(0.0, y, r.axle_z), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=mats["dark"],
            name=f"axle_nut_{k}", material_class_id="metal.blackened_gunmetal",
        )
    # Raised bolt-head rivets (④), each embedded on a real crossbar/rail member.
    bolt_pts = [
        (HEAD_X, -HEAD_Y, HEAD_Z),
        (HEAD_X, HEAD_Y, HEAD_Z),
        (NECK_X, -0.20, NECK_Z),
        (NECK_X, 0.20, NECK_Z),
        (RAIL_MID_X, -RAIL_Y, mid_z),
        (RAIL_MID_X, RAIL_Y, mid_z),
    ]
    for i, loc in enumerate(bolt_pts):
        frame.visual(Sphere(radius=0.011), origin=Origin(xyz=loc), material=mats["dark"], name=f"bolt_head_{i}", material_class_id="metal.blackened_gunmetal")


# ---------------------------------------------------------------------------
# Handle modules (Slot C). All FIXED visuals on the frame.
# ---------------------------------------------------------------------------
def _build_double_handle(frame, r: ResolvedHandCultivatorConfig, mats) -> None:
    mid_z = _rail_mid_z(r)
    hl, hs = r.handle_len_scale, r.handle_spread_scale
    y_top = 0.18 * hs
    clamp_pts: list[tuple[float, float, float]] = []
    for s, sy in ((0, -1.0), (1, 1.0)):
        base = (-0.30, sy * 0.085, 0.55)
        p1 = (-0.60, sy * 0.82 * y_top, 0.55 + 0.26 * hl)
        p2 = (-0.98, sy * 0.94 * y_top, 0.55 + 0.52 * hl)
        p3 = (-1.42 * (0.7 + 0.3 * hl), sy * y_top, 0.55 + 0.72 * hl)
        handle_pts = [base, p1, p2, p3]
        clamp_pts.append(p1)
        # Upright strap: side-rail mid -> handle base (shared endpoints).
        frame.visual(
            mesh_from_geometry(
                _straight_tube([(RAIL_MID_X, sy * RAIL_Y, mid_z), base], 0.0085), f"upright_strap_{s}"
            ),
            material=mats["metal"],
            name=f"upright_strap_{s}", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
        )
        frame.visual(
            mesh_from_geometry(_straight_tube(handle_pts, 0.021, radial_segments=14), f"wood_handle_{s}"),
            material=mats["wood"],
            name=f"wood_handle_{s}", material_class_id="wood.natural_generic",
        )
        frame.visual(
            mesh_from_geometry(_straight_tube(handle_pts[-2:], 0.024, radial_segments=14), f"rubber_grip_{s}"),
            material=mats["grip"],
            name=f"rubber_grip_{s}", material_class_id="rubber.smooth_plain",
        )
    # Handle clamp bar tying the two handles at their lower knee (shared points).
    frame.visual(
        mesh_from_geometry(_straight_tube([clamp_pts[0], clamp_pts[1]], 0.012), "handle_clamp_bar"),
        material=mats["metal"],
        name="handle_clamp_bar", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )


def _build_single_handle(frame, r: ResolvedHandCultivatorConfig, mats) -> None:
    mid_z = _rail_mid_z(r)
    hl = r.handle_len_scale
    base_z = r.central_base_z
    base = (-0.40, 0.0, base_z)
    handle_pts = [
        base,
        (-0.70, 0.0, base_z + 0.18 * hl),
        (-1.05, 0.0, base_z + 0.42 * hl),
        (-1.42 * (0.7 + 0.3 * hl), 0.0, base_z + 0.62 * hl),
    ]
    # Two upright straps converge from the side rails to the central base.
    for s, sy in ((0, -1.0), (1, 1.0)):
        frame.visual(
            mesh_from_geometry(
                _straight_tube([(RAIL_MID_X, sy * RAIL_Y, mid_z), base], 0.0085), f"upright_strap_{s}"
            ),
            material=mats["metal"],
            name=f"upright_strap_{s}", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
        )
    frame.visual(
        mesh_from_geometry(_straight_tube(handle_pts, 0.024, radial_segments=14), "central_handle"),
        material=mats["wood"],
        name="central_handle", material_class_id="wood.natural_generic",
    )
    frame.visual(
        mesh_from_geometry(_straight_tube(handle_pts[-2:], 0.028, radial_segments=14), "rubber_grip"),
        material=mats["grip"],
        name="rubber_grip", material_class_id="rubber.smooth_plain",
    )
    # Shaft collar clamping the handle base to the straps.
    frame.visual(
        Cylinder(radius=0.028, length=0.05),
        origin=Origin(xyz=(-0.40, 0.0, base_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["dark"],
        name="shaft_collar", material_class_id="metal.blackened_gunmetal",
    )


# ---------------------------------------------------------------------------
# Working-head modules (Slot A / ③). All FIXED visuals on the frame.
# ---------------------------------------------------------------------------
def _build_spring_claws(frame, r: ResolvedHandCultivatorConfig, mats) -> None:
    hd = r.head_depth_scale
    span = r.tine_half_span
    n = r.n_tines
    for i in range(n):
        y = -span + (2.0 * span) * i / (n - 1)
        claw = _depth_pts(
            [(NECK_X, y, NECK_Z), (-0.98, y, 0.105), (-1.06, y, 0.055), (-1.11, y, 0.090)], hd
        )
        frame.visual(
            mesh_from_geometry(_straight_tube(claw, 0.0055, radial_segments=10), f"spring_claw_{i}"),
            material=mats["spring"],
            name=f"spring_claw_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
        )
        frame.visual(
            mesh_from_geometry(_straight_tube(claw[-2:], 0.0062, radial_segments=10), f"worn_claw_tip_{i}"),
            material=mats["worn"],
            name=f"worn_claw_tip_{i}", material_class_id="metal.generic_scratched",
        )


def _build_rigid_tines(frame, r: ResolvedHandCultivatorConfig, mats) -> None:
    hd = r.head_depth_scale
    span = r.tine_half_span
    n = r.n_tines
    length = 0.15 * hd
    for i in range(n):
        y = -span + (2.0 * span) * i / (n - 1)
        frame.visual(
            mesh_from_geometry(
                _straight_tube([(NECK_X, y, NECK_Z), (NECK_X, y, NECK_Z - length)], 0.006, radial_segments=10),
                f"rigid_tine_{i}",
            ),
            material=mats["blade"],
            name=f"rigid_tine_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
        )
        frame.visual(
            mesh_from_geometry(
                _straight_tube(
                    [(NECK_X, y, NECK_Z - length + 0.035), (NECK_X, y, NECK_Z - length)], 0.007, radial_segments=10
                ),
                f"rigid_tine_tip_{i}",
            ),
            material=mats["worn"],
            name=f"rigid_tine_tip_{i}", material_class_id="metal.generic_scratched",
        )


def _build_stirrup(frame, r: ResolvedHandCultivatorConfig, mats) -> None:
    hd = r.head_depth_scale
    # Pivot bolt on the rake crossbar.
    frame.visual(
        Cylinder(radius=0.010, length=0.20),
        origin=Origin(xyz=(NECK_X, 0.0, NECK_Z), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name="stirrup_pivot_bolt", material_class_id="metal.blackened_gunmetal",
    )
    # The arm bottom endpoint is one shared quantity; the bottom bar, blade, and
    # cutting edge all derive from it so they never drift apart (Contract 3c).
    arm_bot_x, _, arm_bot_z = _depth_pts([(-0.96, 0.0, 0.015)], hd)[0]
    for s, ysign in ((0, -1.0), (1, 1.0)):
        arm = _depth_pts(
            [(NECK_X, ysign * 0.09, NECK_Z), (-0.92, ysign * 0.09, 0.06), (-0.96, ysign * 0.09, 0.015)], hd
        )
        frame.visual(
            mesh_from_geometry(_straight_tube(arm, 0.0065, radial_segments=10), f"stirrup_arm_{s}"),
            material=mats["blade"],
            name=f"stirrup_arm_{s}", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
        )
    frame.visual(
        mesh_from_geometry(
            _straight_tube([(arm_bot_x, -0.09, arm_bot_z), (arm_bot_x, 0.09, arm_bot_z)], 0.0065, radial_segments=10),
            "stirrup_bottom_bar",
        ),
        material=mats["blade"],
        name="stirrup_bottom_bar", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    frame.visual(
        mesh_from_geometry(_flat_plate(0.18, 0.045, 0.003), "stirrup_blade"),
        origin=Origin(xyz=(arm_bot_x, 0.0, arm_bot_z - 0.018)),
        material=mats["blade"],
        name="stirrup_blade", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    frame.visual(
        mesh_from_geometry(_flat_plate(0.175, 0.005, 0.0035), "stirrup_cutting_edge"),
        origin=Origin(xyz=(arm_bot_x, 0.0, arm_bot_z - 0.040)),
        material=mats["worn"],
        name="stirrup_cutting_edge", material_class_id="metal.generic_scratched",
    )


def _build_sweep(frame, r: ResolvedHandCultivatorConfig, mats) -> None:
    hd = r.head_depth_scale
    # Single shared quantity: the blade plane == the shank bottom (Contract 3c).
    blade_z = NECK_Z - 0.087 * hd
    frame.visual(
        mesh_from_geometry(
            _straight_tube([(NECK_X, 0.0, NECK_Z), (NECK_X, 0.0, blade_z)], 0.011, radial_segments=12),
            "sweep_shank",
        ),
        material=mats["blade"],
        name="sweep_shank", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    frame.visual(
        Cylinder(radius=0.018, length=0.022),
        origin=Origin(xyz=(NECK_X, 0.0, NECK_Z - 0.005)),
        material=mats["dark"],
        name="shank_collar", material_class_id="metal.blackened_gunmetal",
    )
    frame.visual(
        mesh_from_geometry(_duckfoot_sweep(blade_z), "sweep_blade"),
        material=mats["blade"],
        name="sweep_blade", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    frame.visual(
        mesh_from_geometry(
            _straight_tube([(-0.76, 0.0, blade_z + 0.004), (-0.82, 0.0, blade_z + 0.003)], 0.006, radial_segments=10),
            "sweep_worn_edge",
        ),
        material=mats["worn"],
        name="sweep_worn_edge", material_class_id="metal.generic_scratched",
    )


def _build_ridger(frame, r: ResolvedHandCultivatorConfig, mats) -> None:
    # Frog bracket on the rake crossbar, then gussets down to the moldboard.
    frame.visual(
        mesh_from_geometry(
            _straight_tube([(NECK_X, -0.04, NECK_Z), (NECK_X, 0.04, NECK_Z)], 0.009), "moldboard_brace"
        ),
        material=mats["metal"],
        name="moldboard_brace", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    for s, y in ((0, -0.028), (1, 0.028)):
        frame.visual(
            mesh_from_geometry(
                _straight_tube([(NECK_X, y, NECK_Z - 0.003), (NECK_X, y * 0.5, 0.048)], 0.005, radial_segments=10),
                f"frog_gusset_{s}",
            ),
            material=mats["metal"],
            name=f"frog_gusset_{s}", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
        )
    frame.visual(
        mesh_from_geometry(_ridger_moldboard_surface(), "ridger_moldboard"),
        material=mats["blade"],
        name="ridger_moldboard", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    frame.visual(
        mesh_from_geometry(_ridger_share_edge(), "ridger_share_edge"),
        material=mats["worn"],
        name="ridger_share_edge", material_class_id="metal.generic_scratched",
    )
    frame.visual(
        mesh_from_geometry(_ridger_central_spine(), "ridger_spine"),
        material=mats["spring"],
        name="ridger_spine", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )


_HANDLE_BUILDERS = {
    "double_straight": _build_double_handle,
    "single_central": _build_single_handle,
}
_HEAD_BUILDERS = {
    "spring_tine_claws": _build_spring_claws,
    "rigid_tines": _build_rigid_tines,
    "stirrup_hoe": _build_stirrup,
    "sweep": _build_sweep,
    "ridger": _build_ridger,
}


# ---------------------------------------------------------------------------
# Ground-wheel modules (Slot B). The one moving part (tine_wheel).
# ---------------------------------------------------------------------------
def _emit_lugs(wheel, r: ResolvedHandCultivatorConfig, mats) -> None:
    for i in range(10):
        angle = 2.0 * math.pi * i / 10.0 + 0.16
        wheel.visual(
            mesh_from_geometry(_wheel_lug(angle, r.wheel_r), f"wheel_lug_{i}"),
            material=mats["wheel"],
            name=f"wheel_lug_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
        )
        if i in (0, 3, 6):
            wheel.visual(
                mesh_from_geometry(_lug_tip(angle, r.wheel_r), f"tine_tip_{i}"),
                material=mats["worn"],
                name=f"tine_tip_{i}", material_class_id="metal.generic_scratched",
            )


def _build_spoked_iron(wheel, r: ResolvedHandCultivatorConfig, mats) -> None:
    wr = r.wheel_r
    wheel.visual(mesh_from_geometry(_torus_y(wr, wr * 0.04), "outer_iron_rim"), material=mats["wheel"], name="outer_iron_rim", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"))
    wheel.visual(
        mesh_from_geometry(_torus_y(wr * 0.68, wr * 0.022, major_segments=60, tube_segments=10), "inner_iron_rim"),
        material=mats["wheel"],
        name="inner_iron_rim", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    wheel.visual(
        Cylinder(radius=0.036, length=0.074),
        origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["wheel"],
        name="hub_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    for i in range(r.n_spokes):
        angle = 2.0 * math.pi * i / r.n_spokes
        wheel.visual(
            mesh_from_geometry(_wheel_spoke(angle, 0.032, wr * 0.973), f"wheel_spoke_{i}"),
            material=mats["wheel"],
            name=f"wheel_spoke_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
        )
    _emit_lugs(wheel, r, mats)


def _build_solid_disc(wheel, r: ResolvedHandCultivatorConfig, mats) -> None:
    wr = r.wheel_r
    wheel.visual(mesh_from_geometry(_torus_y(wr, wr * 0.04), "outer_iron_rim"), material=mats["wheel"], name="outer_iron_rim", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"))
    wheel.visual(
        Cylinder(radius=wr * 0.967, length=0.008),
        origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["wheel"],
        name="iron_disc", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    wheel.visual(
        Cylinder(radius=0.036, length=0.074),
        origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["wheel"],
        name="hub_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    _emit_lugs(wheel, r, mats)


def _build_pneumatic(wheel, r: ResolvedHandCultivatorConfig, mats) -> None:
    wr = r.wheel_r
    steel_r = wr * 0.63
    steel_wheel_geom = WheelGeometry(
        steel_r,
        0.068,
        rim=WheelRim(inner_radius=steel_r * 0.78, flange_height=0.010, flange_thickness=0.004, bead_seat_depth=0.004),
        hub=WheelHub(
            radius=0.038,
            width=0.068,
            cap_style="flat",
            bolt_pattern=BoltPattern(count=4, circle_diameter=0.052, hole_diameter=0.006),
        ),
        spokes=WheelSpokes(style="split_y", count=5, thickness=0.005, window_radius=0.014),
    )
    wheel.visual(
        mesh_from_geometry(steel_wheel_geom, "steel_wheel"),
        origin=Origin(rpy=(0.0, 0.0, math.pi / 2.0)),
        material=mats["wheel"],
        name="steel_wheel", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    # Tire section width is FIXED (not scaled with radius) so the tire always
    # fits between the fork side rails (inner faces at ±(RAIL_Y-0.0105)=±0.0635);
    # tire y-extent == width/2, so 0.098 -> ±0.049 leaves a safe clearance.
    rubber_tire_geom = TireGeometry(
        wr,
        0.098,
        inner_radius=steel_r * 0.98,
        carcass=TireCarcass(belt_width_ratio=0.68, sidewall_bulge=0.05),
        tread=TireTread(style="block", depth=0.010, count=12, land_ratio=0.55),
        sidewall=TireSidewall(style="rounded", bulge=0.04),
        shoulder=TireShoulder(width=0.008, radius=0.004),
    )
    wheel.visual(
        mesh_from_geometry(rubber_tire_geom, "rubber_tire"),
        origin=Origin(rpy=(0.0, 0.0, math.pi / 2.0)),
        material=mats["tire"],
        name="rubber_tire", material_class_id="rubber.directional_grooved",
    )
    # Solid steel hub sleeve: the WheelGeometry hub carries a central bore, so a
    # thin axle pin would sit in air. This sleeve fills the bore (overlaps the
    # steel wheel) and gives the captured axle pin real contact.
    wheel.visual(
        Cylinder(radius=0.036, length=0.074),
        origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["wheel"],
        name="hub_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"painted_green", "painted_red", "galvanized", "blued_steel", "planet_jr"} else "metal.steel_rusted"),
    )
    _emit_lugs(wheel, r, mats)


_WHEEL_BUILDERS = {
    "spoked_iron": _build_spoked_iron,
    "solid_disc": _build_solid_disc,
    "pneumatic": _build_pneumatic,
}

# The wheel-part element the axle pin is captured inside (per wheel type).
_WHEEL_HUB_ELEM = {
    "spoked_iron": ("hub_shell",),
    "solid_disc": ("hub_shell", "iron_disc"),
    "pneumatic": ("hub_shell", "steel_wheel"),
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_hand_cultivator(
    config: HandCultivatorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={"category": "Agricultural", "small_class": "Hand cultivator"},
    )
    mats = {
        key: model.material(f"hc_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    frame = model.part("frame")
    _build_frame_skeleton(frame, r, mats)
    _HANDLE_BUILDERS[r.handle_config](frame, r, mats)
    _HEAD_BUILDERS[r.working_head](frame, r, mats)

    wheel = model.part("tine_wheel")
    _WHEEL_BUILDERS[r.ground_wheel](wheel, r, mats)

    model.articulation(
        "wheel_axle",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=wheel,
        origin=Origin(xyz=(0.0, 0.0, r.axle_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=18.0),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_hand_cultivator(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_hand_cultivator(config_from_seed(seed), assets=assets)


def _aabb_center(aabb):
    lo, hi = aabb
    return tuple((lo[i] + hi[i]) * 0.5 for i in range(3))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_hand_cultivator_tests(
    object_model: ArticulatedObject,
    config: HandCultivatorConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    wheel = object_model.get_part("tine_wheel")
    axle = object_model.get_articulation("wheel_axle")
    frame_vis = {v.name for v in frame.visuals}
    wheel_vis = {v.name for v in wheel.visuals}

    # Captured pin-through-hub (element-scoped; grandfathered, no MatingContract).
    for elem_b in _WHEEL_HUB_ELEM[r.ground_wheel]:
        ctx.allow_overlap(
            frame,
            wheel,
            elem_a="axle_pin",
            elem_b=elem_b,
            reason="The dark axle pin is captured inside the rotating wheel hub bore.",
        )

    # ---- Baseline geometry / connectivity. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure. ----
    ctx.check(
        "small class is hand cultivator",
        object_model.meta.get("small_class") == "Hand cultivator" and "cultivator" in object_model.name,
        details=str(object_model.meta),
    )
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "frame + tine_wheel parts present",
        {"frame", "tine_wheel"} <= part_names,
        details=str(sorted(part_names)),
    )
    ctx.check(
        "wheel_axle is the sole CONTINUOUS spin about +Y",
        axle.articulation_type == ArticulationType.CONTINUOUS and abs(axle.axis[1]) > 0.99,
        details=f"type={axle.articulation_type} axis={tuple(axle.axis)}",
    )

    # ---- Working-head realization (Slot A / ③). ----
    head_visual = {
        "spring_tine_claws": "spring_claw_0",
        "rigid_tines": "rigid_tine_0",
        "stirrup_hoe": "stirrup_blade",
        "sweep": "sweep_blade",
        "ridger": "ridger_moldboard",
    }[r.working_head]
    ctx.check(
        f"working_head '{r.working_head}' emits {head_visual}",
        head_visual in frame_vis,
        details=f"visuals lack {head_visual}",
    )

    # ---- Tine multiplicity (conditional on tine heads). ----
    if r.is_tine_head:
        prefix = "spring_claw_" if r.working_head == "spring_tine_claws" else "rigid_tine_"
        tine_names = [v.name for v in frame.visuals if v.name.startswith(prefix) and "tip" not in v.name]
        ctx.check(
            f"exactly N={r.n_tines} tines on rake_crossbar",
            len(tine_names) == r.n_tines,
            details=f"found {sorted(tine_names)} expected N={r.n_tines}",
        )
        # Tine row fits inside the crossbar span (inequality proven from dims).
        ctx.check(
            "tine row fits inside rake_crossbar",
            r.tine_half_span <= CB_HALF - TINE_MARGIN + 1e-9,
            details=f"half_span={r.tine_half_span:.4f} limit={CB_HALF - TINE_MARGIN:.4f}",
        )
    else:
        no_tine = [v.name for v in frame.visuals if v.name.startswith(("spring_claw_", "rigid_tine_"))]
        ctx.check(
            "blade head emits no loop tines",
            not no_tine,
            details=f"unexpected tines {no_tine}",
        )

    # ---- Wheel realization (Slot B) + spoke multiplicity. ----
    wheel_visual = {
        "spoked_iron": "wheel_spoke_0",
        "solid_disc": "iron_disc",
        "pneumatic": "rubber_tire",
    }[r.ground_wheel]
    ctx.check(
        f"ground_wheel '{r.ground_wheel}' emits {wheel_visual}",
        wheel_visual in wheel_vis,
        details=f"wheel lacks {wheel_visual}",
    )
    if r.ground_wheel == "spoked_iron":
        spokes = [v.name for v in wheel.visuals if v.name.startswith("wheel_spoke_")]
        ctx.check(
            f"spoked wheel has N={r.n_spokes} spokes",
            len(spokes) == r.n_spokes,
            details=f"found {len(spokes)} expected {r.n_spokes}",
        )

    # ---- Handle realization (Slot C). ----
    if r.handle_config == "double_straight":
        ctx.check(
            "double handle has twin wood handles",
            {"wood_handle_0", "wood_handle_1"} <= frame_vis,
            details="missing wood_handle_{0,1}",
        )
    else:
        ctx.check(
            "single handle has one central shaft",
            "central_handle" in frame_vis and "wood_handle_0" not in frame_vis,
            details="missing central_handle",
        )

    # ---- Walk-behind proportions. ----
    frame_box = ctx.part_world_aabb(frame)
    wheel_box = ctx.part_world_aabb(wheel)
    if frame_box is not None and wheel_box is not None:
        ctx.check(
            "cultivator has walk-behind proportions",
            frame_box[0][0] < -1.1
            and frame_box[1][2] > 1.0
            and (wheel_box[1][2] - wheel_box[0][2]) > 0.45,
            details=f"frame={frame_box}, wheel={wheel_box}",
        )
        ctx.check(
            "wheel rests near the ground",
            wheel_box[0][2] < 0.06,
            details=f"wheel_zmin={wheel_box[0][2]:.4f}",
        )

    # ---- Rule 5: continuous spin — full-turn clearance + visible rotation. ----
    rest = ctx.part_element_world_aabb(wheel, elem="wheel_lug_0")
    with ctx.pose({axle: 1.1}):
        moved = ctx.part_element_world_aabb(wheel, elem="wheel_lug_0")
    rc = _aabb_center(rest) if rest is not None else None
    mc = _aabb_center(moved) if moved is not None else None
    ctx.check(
        "wheel visibly rotates about the axle",
        rc is not None and mc is not None and abs(rc[0] - mc[0]) + abs(rc[2] - mc[2]) > 0.06,
        details=f"rest={rc}, moved={mc}",
    )
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "HandCultivatorConfig",
    "ResolvedHandCultivatorConfig",
    "build_hand_cultivator",
    "build_seeded_hand_cultivator",
    "config_from_seed",
    "resolve_config",
    "run_hand_cultivator_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
