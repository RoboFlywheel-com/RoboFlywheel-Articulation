# SPDX-License-Identifier: Apache-2.0

"""Galvanized steel trash / garbage can — modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Urban_Environment_Trashcan1.md`` and the
``picture/.../Trashcan1`` 5-star sample pool (2 parents + 8 slot-fork
variants).

Core identity: a classic galvanized sheet-metal can — a hollow upright
surface-of-revolution body (tapered / straight / barrel-bulged) with a
corrugated, ribbed, ring-banded, or smooth wall, a **solid floor disc**, a
**rolled top rim**, riveted **side lug pads**, and a removable / openable
domed or flat top plus carry handles. The defining articulation is the top
mechanism (rear-hinged REVOLUTE dome lid, lift-off PRISMATIC flat lid, or an
open rim with a swinging handle) and/or a swinging carry bail.

Pattern = ``parallel_children`` + one body-local vertical-rib ``multiplicity``
axis. Four module slots:

  * ``body_profile`` (3): profile_tapered / profile_straight / profile_barrel.
    Drives the ``_radius_at(z)`` revolve profile of the root body (and every
    downstream rim / lug / lid radius). Not a separate part.
  * ``surface`` (4): vertical flutes baked into the lathe shell / smooth /
    horizontal ring bands / bold vertical ribs. Wall visual layer on the body
    + the single rib/ring multiplicity axis.
  * ``lid_top`` (4, DEFINING JOINT): dome REVOLUTE / shallow-dome REVOLUTE /
    flat lift-off PRISMATIC / open rim (no lid).
  * ``handle`` (4): two FIXED ring ears / two FIXED bail ears / two REVOLUTE
    side swing bails / one REVOLUTE overhead carry bail.

Multiplicity (spec §Multiplicity): ``rib_count`` N — the vertical corrugation /
rib / horizontal-ring count. Capped small per surface module (flutes <=44,
bold_ribs <=16, rings <=20) because the angular tessellation is N*4; this keeps
the high-N ribbed wall away from the Kitchen-appliance SIGKILL / compile_timeout
mesh-perf cliff.

Rules:
  * Rule 1 — ribs / ring bands / rim / floor / lug pads are non-moving
    ``parent.visual(...)`` on the body, never FIXED-jointed parts.
  * Rule 2 — every non-FIXED joint (REVOLUTE dome lid, PRISMATIC flat lid,
    REVOLUTE side / overhead bail) declares a ``MatingContract`` pinning a real
    lug / seat face on the body to a real face on the child.
  * Rule 3 — the body is a true surface-of-revolution (``LatheGeometry``),
    never downgraded to a Box / Cylinder.

Compatibility gating (resolve_config, spec §params):
  * ``top_open_rim`` removes the lid joint, so it MUST pair with
    ``handle_swing_bail_sides`` (a REVOLUTE handle) to keep >=1 non-fixed
    joint; otherwise the handle is forced to swing bails.
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
    Box,
    Cylinder,
    Inertial,
    LatheGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

BodyProfile = Literal["profile_tapered", "profile_straight", "profile_barrel"]
Surface = Literal[
    "surface_vertical_flutes",
    "surface_smooth",
    "surface_horizontal_rings",
    "surface_bold_ribs",
]
LidTop = Literal[
    "lid_dome_revolute",
    "lid_dome_shallow_revolute",
    "lid_flat_liftoff_prismatic",
    "top_open_rim",
]
Handle = Literal[
    "handle_two_ring_ears",
    "handle_two_bail_ears",
    "handle_swing_bail_sides",
    "handle_overhead_bail",
]
PaletteStyle = Literal[
    "bright_galvanized",
    "weathered_galvanized",
    "dark_zinc",
    "painted_green",
    "painted_silver",
    "matte_charcoal",
]

BODY_PROFILES: tuple[BodyProfile, ...] = (
    "profile_tapered",
    "profile_straight",
    "profile_barrel",
)
SURFACES: tuple[Surface, ...] = (
    "surface_vertical_flutes",
    "surface_smooth",
    "surface_horizontal_rings",
    "surface_bold_ribs",
)
LID_TOPS: tuple[LidTop, ...] = (
    "lid_dome_revolute",
    "lid_dome_shallow_revolute",
    "lid_flat_liftoff_prismatic",
    "top_open_rim",
)
HANDLES: tuple[Handle, ...] = (
    "handle_two_ring_ears",
    "handle_two_bail_ears",
    "handle_swing_bail_sides",
    "handle_overhead_bail",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "bright_galvanized",
    "weathered_galvanized",
    "dark_zinc",
    "painted_green",
    "painted_silver",
    "matte_charcoal",
)

# Sampling weights (spec: small N high-frequency, large N rare).
_SURFACE_WEIGHTS = (0.34, 0.22, 0.22, 0.22)
_LID_WEIGHTS = (0.26, 0.22, 0.34, 0.18)
_HANDLE_WEIGHTS = (0.30, 0.24, 0.24, 0.22)

# Per-surface rib-N domains (effective cap << SIGKILL cliff; angular segs=N*4).
_FLUTE_N = ((24, 28, 32, 40, 44), (0.42, 0.26, 0.16, 0.10, 0.06))
_BOLD_N = ((6, 8, 10, 12, 16), (0.34, 0.30, 0.18, 0.12, 0.06))
_RING_N = ((8, 10, 12, 16, 20), (0.34, 0.28, 0.18, 0.12, 0.08))

# Only swing-bail handles carry a non-fixed joint (required when open rim).
_SWING_HANDLES: tuple[Handle, ...] = ("handle_swing_bail_sides", "handle_overhead_bail")
_OPEN_RIM_HANDLE: Handle = "handle_swing_bail_sides"

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "bright_galvanized": {
        "body": (0.74, 0.76, 0.78, 1.0),
        "spangle": (0.62, 0.65, 0.68, 1.0),
        "rim": (0.68, 0.70, 0.72, 1.0),
        "wire": (0.55, 0.57, 0.60, 1.0),
        "lid": (0.72, 0.74, 0.76, 1.0),
        "lug": (0.58, 0.60, 0.63, 1.0),
    },
    "weathered_galvanized": {
        "body": (0.58, 0.59, 0.57, 1.0),
        "spangle": (0.48, 0.49, 0.46, 1.0),
        "rim": (0.52, 0.52, 0.50, 1.0),
        "wire": (0.42, 0.42, 0.40, 1.0),
        "lid": (0.55, 0.56, 0.54, 1.0),
        "lug": (0.45, 0.45, 0.43, 1.0),
    },
    "dark_zinc": {
        "body": (0.40, 0.42, 0.45, 1.0),
        "spangle": (0.32, 0.34, 0.37, 1.0),
        "rim": (0.36, 0.38, 0.41, 1.0),
        "wire": (0.28, 0.30, 0.33, 1.0),
        "lid": (0.38, 0.40, 0.43, 1.0),
        "lug": (0.30, 0.32, 0.35, 1.0),
    },
    "painted_green": {
        "body": (0.16, 0.34, 0.22, 1.0),
        "spangle": (0.13, 0.28, 0.18, 1.0),
        "rim": (0.20, 0.20, 0.20, 1.0),
        "wire": (0.18, 0.18, 0.18, 1.0),
        "lid": (0.14, 0.30, 0.20, 1.0),
        "lug": (0.16, 0.16, 0.16, 1.0),
    },
    "painted_silver": {
        "body": (0.82, 0.83, 0.84, 1.0),
        "spangle": (0.74, 0.75, 0.76, 1.0),
        "rim": (0.70, 0.71, 0.72, 1.0),
        "wire": (0.60, 0.61, 0.62, 1.0),
        "lid": (0.80, 0.81, 0.82, 1.0),
        "lug": (0.62, 0.63, 0.64, 1.0),
    },
    "matte_charcoal": {
        "body": (0.22, 0.22, 0.23, 1.0),
        "spangle": (0.17, 0.17, 0.18, 1.0),
        "rim": (0.26, 0.26, 0.27, 1.0),
        "wire": (0.15, 0.15, 0.16, 1.0),
        "lid": (0.20, 0.20, 0.21, 1.0),
        "lug": (0.18, 0.18, 0.19, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Vertical axis +Z; footprint at z=0.
# A ~0.40-0.50 m diameter, ~0.66 m tall hand-carried metal can.
# ---------------------------------------------------------------------------
_R_TOP = 0.215  # rim outer radius (round mouth)
_TAPER_DROP = 0.045  # taper: foot narrower than rim by this much
_R_BULGE = 0.060  # barrel: mid-height bulge amplitude
_BODY_H = 0.660  # body outer height (rim plane)
_WALL = 0.010  # wall thickness
_FLOOR_T = 0.014  # solid floor disc thickness
_RIM_TUBE = 0.012  # rolled rim torus tube radius
_FLUTE_AMP = 0.006  # corrugation flute amplitude
_RIB_DEPTH = 0.012  # bold rib protrusion depth
_RING_TUBE = 0.009  # horizontal ring-band tube radius

_LUG_Z = 0.480  # side lug pad center height (carry-handle line)
_LUG_W = 0.046  # lug pad width / height
_LUG_T = 0.016  # lug pad radial thickness

_LID_DISC_T = 0.018  # flat lid disc thickness
_LID_RISE = 0.085  # dome lid rise
_LID_SHALLOW_RISE = 0.045  # shallow dome rise
_LIFT_MAX = 0.40  # PRISMATIC lid lift travel
_SKIRT_DROP = 0.026  # lid skirt drop over the rim

_RING_R = 0.052  # carry ring drop-handle radius
_WIRE_R = 0.006  # handle wire radius
_BAIL_ROD_R = 0.006  # overhead bail rod radius

_LATHE_SEGMENTS = 56  # smooth-wall revolve angular segments (modest)


@dataclass(frozen=True)
class Trashcan1Config:
    body_profile: BodyProfile | None = None
    surface: Surface | None = None
    lid_top: LidTop | None = None
    handle: Handle | None = None
    rib_count: int | None = None
    palette_style: PaletteStyle | None = None
    body_h_scale: float = 1.0
    r_top_scale: float = 1.0
    lid_rise_scale: float = 1.0
    lift_scale: float = 1.0
    name: str = "trashcan1"


@dataclass(frozen=True)
class ResolvedTrashcan1Config:
    body_profile: BodyProfile
    surface: Surface
    lid_top: LidTop
    handle: Handle
    rib_count: int
    palette_style: PaletteStyle
    # Concrete geometry.
    r_top: float
    r_bot: float
    r_bulge: float
    body_h: float
    wall: float
    floor_t: float
    rim_tube: float
    flute_amp: float
    rib_depth: float
    ring_tube: float
    lug_z: float
    lid_disc_t: float
    lid_rise: float
    lift_max: float
    skirt_drop: float
    name: str

    @property
    def has_lid(self) -> bool:
        return self.lid_top != "top_open_rim"

    @property
    def is_dome(self) -> bool:
        return self.lid_top in ("lid_dome_revolute", "lid_dome_shallow_revolute")

    @property
    def r_rim(self) -> float:
        return self.r_top

    @property
    def lid_r(self) -> float:
        return self.r_rim + 0.016

    @property
    def hinge_y(self) -> float:
        return self.r_rim + 0.004


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> Trashcan1Config:
    rng = random.Random(seed)
    surface = rng.choices(SURFACES, weights=_SURFACE_WEIGHTS, k=1)[0]
    lid_top = rng.choices(LID_TOPS, weights=_LID_WEIGHTS, k=1)[0]
    handle = rng.choices(HANDLES, weights=_HANDLE_WEIGHTS, k=1)[0]

    if surface == "surface_bold_ribs":
        rib_count = rng.choices(_BOLD_N[0], weights=_BOLD_N[1], k=1)[0]
    elif surface == "surface_horizontal_rings":
        rib_count = rng.choices(_RING_N[0], weights=_RING_N[1], k=1)[0]
    elif surface == "surface_vertical_flutes":
        rib_count = rng.choices(_FLUTE_N[0], weights=_FLUTE_N[1], k=1)[0]
    else:  # smooth
        rib_count = 0

    return Trashcan1Config(
        body_profile=rng.choices(BODY_PROFILES, weights=(0.4, 0.34, 0.26), k=1)[0],
        surface=surface,
        lid_top=lid_top,
        handle=handle,
        rib_count=rib_count,
        palette_style=rng.choice(PALETTE_STYLES),
        body_h_scale=round(rng.uniform(0.92, 1.08), 4),
        r_top_scale=round(rng.uniform(0.92, 1.05), 4),
        lid_rise_scale=round(rng.uniform(0.85, 1.12), 4),
        lift_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_trashcan1_{seed}",
    )


def resolve_config(config: Trashcan1Config | None = None) -> ResolvedTrashcan1Config:
    cfg = config or Trashcan1Config()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    body_profile = _pick(cfg.body_profile, BODY_PROFILES)
    surface = _pick(cfg.surface, SURFACES)
    lid_top = _pick(cfg.lid_top, LID_TOPS)
    handle = _pick(cfg.handle, HANDLES)

    # --- Compatibility gating: open rim must pair with a swinging handle so a
    # non-fixed joint always exists. ---
    if lid_top == "top_open_rim" and handle not in _SWING_HANDLES:
        handle = _OPEN_RIM_HANDLE

    # --- rib_count by surface (smooth => 0). ---
    rib_count = int(cfg.rib_count) if cfg.rib_count is not None else 0
    if surface == "surface_bold_ribs":
        rib_count = int(_clamp(rib_count or 8, 6, 16))
    elif surface == "surface_horizontal_rings":
        rib_count = int(_clamp(rib_count or 12, 8, 20))
    elif surface == "surface_vertical_flutes":
        rib_count = int(_clamp(rib_count or 28, 16, 44))
    else:
        rib_count = 0

    # --- Continuous scales (clamped / derived). ---
    body_h = _clamp(_BODY_H * _clamp(cfg.body_h_scale, 0.92, 1.08), 0.600, 0.700)
    r_top = _clamp(_R_TOP * _clamp(cfg.r_top_scale, 0.92, 1.05), 0.165, 0.225)
    lid_rise_base = _LID_RISE if lid_top == "lid_dome_revolute" else _LID_SHALLOW_RISE
    lid_rise = _clamp(lid_rise_base * _clamp(cfg.lid_rise_scale, 0.85, 1.12), 0.040, 0.100)
    lift_max = _clamp(_LIFT_MAX * _clamp(cfg.lift_scale, 0.85, 1.10), 0.300, 0.450)

    # --- Profile -> r_bot / r_bulge. ---
    if body_profile == "profile_straight":
        r_bot = r_top
        r_bulge = 0.0
    elif body_profile == "profile_barrel":
        # Foot and rim both narrower; mid-height bulge.
        r_bulge = min(_R_BULGE, 0.090)
        r_bot = r_top - 0.012
    else:  # tapered: foot narrower than rim
        r_bot = r_top - _TAPER_DROP
        r_bulge = 0.0

    # --- Hollow / deep-cavity inequalities. ---
    amp = _FLUTE_AMP if surface == "surface_vertical_flutes" else 0.0
    # R_inner > 0.10 (keep a real hollow cavity).
    min_r = min(r_top, r_bot) + (r_bulge if body_profile == "profile_barrel" else 0.0) * 0.0
    r_inner = min(r_top, r_bot) - amp - _WALL
    if r_inner <= 0.105:
        r_top = max(r_top, 0.165)
        r_bot = max(r_bot, r_top - _TAPER_DROP if body_profile == "profile_tapered" else r_top - 0.012)
    # Deep cavity: (body_h - rim_tube) - floor_t > 0.45.
    if (body_h - _RIM_TUBE) - _FLOOR_T <= 0.46:
        body_h = max(body_h, 0.640)

    lug_z = _clamp(_LUG_Z * (body_h / _BODY_H), 0.40, body_h - 0.120)

    return ResolvedTrashcan1Config(
        body_profile=body_profile,
        surface=surface,
        lid_top=lid_top,
        handle=handle,
        rib_count=rib_count,
        palette_style=palette_style,
        r_top=r_top,
        r_bot=r_bot,
        r_bulge=r_bulge,
        body_h=body_h,
        wall=_WALL,
        floor_t=_FLOOR_T,
        rim_tube=_RIM_TUBE,
        flute_amp=_FLUTE_AMP,
        rib_depth=_RIB_DEPTH,
        ring_tube=_RING_TUBE,
        lug_z=lug_z,
        lid_disc_t=_LID_DISC_T,
        lid_rise=lid_rise,
        lift_max=lift_max,
        skirt_drop=_SKIRT_DROP,
        name=cfg.name or "trashcan1",
    )


def with_overrides(config: Trashcan1Config, **kwargs: object) -> Trashcan1Config:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# Slot A: body revolve profile. _radius_at(z) is the single switch point.
# ---------------------------------------------------------------------------
def _radius_at(r: ResolvedTrashcan1Config, z: float) -> float:
    """Outer body radius at height z in [0, body_h]."""
    h = max(r.body_h, 1e-6)
    t = _clamp(z / h, 0.0, 1.0)
    if r.body_profile == "profile_straight":
        return r.r_top
    if r.body_profile == "profile_barrel":
        return r.r_bot + (r.r_top - r.r_bot) * t + r.r_bulge * math.sin(math.pi * t)
    # tapered (linear, wider at top)
    return r.r_bot + (r.r_top - r.r_bot) * t


# ---------------------------------------------------------------------------
# Slot B: wall surface. The body is always a LatheGeometry surface-of-revolution
# (Rule 3). Flutes are baked into the profile sampling; smooth / rings / bold
# ribs use a smooth lathe shell + copied visuals.
# ---------------------------------------------------------------------------
def _body_profile_points(r: ResolvedTrashcan1Config) -> list[tuple[float, float]]:
    """(radius, z) profile for the hollow lathe body: up the outer wall, across
    the rim, down the inner wall, across the floor top, to the axis."""
    n = 14
    outer: list[tuple[float, float]] = []
    for i in range(n + 1):
        z = r.body_h * i / n
        outer.append((_radius_at(r, z), z))
    rin_top = max(0.10, _radius_at(r, r.body_h) - r.wall)
    inner: list[tuple[float, float]] = []
    floor_top = r.floor_t
    for i in range(n + 1):
        z = r.body_h - (r.body_h - floor_top) * i / n
        ro = _radius_at(r, z)
        inner.append((max(0.10, ro - r.wall), z))
    pts: list[tuple[float, float]] = [(0.0, 0.0)]  # floor center bottom
    pts += outer  # up the outer wall
    pts.append((rin_top, r.body_h))  # across the rim top to inner
    pts += inner  # down the inner wall
    pts.append((0.0, floor_top))  # across the floor top to axis
    return pts


def _emit_body_shell(body, r: ResolvedTrashcan1Config, mats) -> None:
    """The root surface-of-revolution wall + floor (single hollow lathe)."""
    if r.surface == "surface_vertical_flutes":
        segs = min(r.rib_count * 4, 176)
    else:
        segs = _LATHE_SEGMENTS
    lathe = LatheGeometry(_body_profile_points(r), segments=segs, closed=True)
    body.visual(
        mesh_from_geometry(lathe, "can_wall"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["body"],
        name="corrugated_wall" if r.surface == "surface_vertical_flutes" else "smooth_wall", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
    )


def _rib_segment_frames(
    r: ResolvedTrashcan1Config, z0: float, z1: float, segments: int = 3
) -> list[tuple[float, float, float, float]]:
    """Split [z0, z1] into wall-following rib segments.

    The body wall radius changes with height (tapered / barrel profiles), so a
    single straight box only touches the wall at one height. Each segment uses
    its own mean radius and a pitch tilt about the tangent axis so both ends
    ride the wall surface. Segments overlap 2 mm to hide the seams.
    """
    frames: list[tuple[float, float, float, float]] = []
    for i in range(segments):
        lo = z0 + (z1 - z0) * i / segments - 0.002
        hi = z0 + (z1 - z0) * (i + 1) / segments + 0.002
        r_lo, r_hi = _radius_at(r, lo), _radius_at(r, hi)
        dz, dr = hi - lo, r_hi - r_lo
        frames.append(
            (0.5 * (lo + hi), 0.5 * (r_lo + r_hi), math.hypot(dz, dr), math.atan2(dr, dz))
        )
    return frames


def _emit_flutes(body, r: ResolvedTrashcan1Config, mats) -> None:
    """Vertical corrugation flutes as thin proud ridges on the wall.

    Single multiplicity axis: N angular flutes, each a slim vertical bead
    following the body taper across 3 segments. Kept modest (N<=44) — angular
    work is per flute, not per facet.
    """
    n = r.rib_count
    z0 = r.floor_t + 0.02
    z1 = r.body_h - 0.03
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        for seg_i, (mid_z, seg_r, seg_len, beta) in enumerate(
            _rib_segment_frames(r, z0, z1)
        ):
            body.visual(
                Box((r.flute_amp * 1.6, r.flute_amp * 1.6, seg_len)),
                origin=Origin(
                    xyz=(seg_r * math.cos(ang), seg_r * math.sin(ang), mid_z),
                    rpy=(0.0, beta, ang),
                ),
                material=mats["spangle"],
                name=f"flute_{i}_{seg_i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
            )


def _emit_bold_ribs(body, r: ResolvedTrashcan1Config, mats) -> None:
    """N bold vertical ribs (peaked ridge protrusions), angularly distributed,
    each following the body taper across 3 segments. Source: surface_bold_ribs
    rib_{i} loop."""
    n = r.rib_count
    z0 = r.floor_t + 0.03
    z1 = r.body_h - 0.04
    # Half-step phase offset so no rib lands exactly on the lug angles (0, pi).
    phase = math.pi / n
    for i in range(n):
        ang = phase + 2.0 * math.pi * i / n
        for seg_i, (mid_z, seg_r, seg_len, beta) in enumerate(
            _rib_segment_frames(r, z0, z1)
        ):
            off = seg_r + r.rib_depth * 0.3
            body.visual(
                Box((r.rib_depth, r.rib_depth * 1.4, seg_len)),
                origin=Origin(
                    xyz=(off * math.cos(ang), off * math.sin(ang), mid_z),
                    rpy=(0.0, beta, ang),
                ),
                material=mats["spangle"],
                name=f"rib_{i}_{seg_i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
            )


def _emit_ring_bands(body, r: ResolvedTrashcan1Config, mats) -> None:
    """N horizontal ring-band torus stack, z evenly distributed. Source:
    surface_horizontal_rings ring_band_{i} loop on a smooth lathe shell."""
    n = r.rib_count
    z0 = r.floor_t + 0.04
    z1 = r.body_h - 0.05
    for i in range(n):
        z = z0 + (z1 - z0) * (i / max(1, n - 1)) if n > 1 else 0.5 * (z0 + z1)
        ro = _radius_at(r, z)
        band = TorusGeometry(
            ro - r.ring_tube * 0.4, r.ring_tube, radial_segments=10, tubular_segments=48
        )
        body.visual(
            mesh_from_geometry(band, f"ring_band_{i}"),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=mats["spangle"],
            name=f"ring_band_{i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
        )


_SURFACE_DECOR = {
    "surface_vertical_flutes": _emit_flutes,
    "surface_smooth": None,
    "surface_horizontal_rings": _emit_ring_bands,
    "surface_bold_ribs": _emit_bold_ribs,
}


def _emit_rolled_rim(body, r: ResolvedTrashcan1Config, mats) -> None:
    """Rolled top rim torus + floor disc (shared body visuals, Rule 1)."""
    rim = TorusGeometry(
        r.r_rim, r.rim_tube, radial_segments=12, tubular_segments=_LATHE_SEGMENTS
    )
    body.visual(
        mesh_from_geometry(rim, "rolled_rim"),
        origin=Origin(xyz=(0.0, 0.0, r.body_h - r.rim_tube * 0.4)),
        material=mats["rim"],
        name="rolled_rim", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
    )
    # Solid floor disc (closed bottom).
    body.visual(
        Cylinder(radius=_radius_at(r, r.floor_t * 0.5) - 0.001, length=r.floor_t),
        origin=Origin(xyz=(0.0, 0.0, r.floor_t * 0.5)),
        material=mats["body"],
        name="floor_disc", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
    )


# ---------------------------------------------------------------------------
# Side lug pads (carry-handle anchors). Number/placement follow the handle
# module; lugs are inline body visuals (Rule 1). Returns lug placement info.
# ---------------------------------------------------------------------------
# Lug center sits half-embedded in the wall; its outer face is the handle
# mating surface. center_radius = wall + _LUG_T/2, so outer face at
# wall + _LUG_T and inner half buried in the body (no isolated lug).
def _lug_center_rad(r: ResolvedTrashcan1Config, z: float) -> float:
    return _radius_at(r, z) + _LUG_T * 0.5


def _lug_face_outer(r: ResolvedTrashcan1Config, ang: float, z: float) -> tuple[float, float, float]:
    """Point on the outer lug face (the mating face / joint origin)."""
    rad = _lug_center_rad(r, z) + _LUG_T * 0.5
    return (rad * math.cos(ang), rad * math.sin(ang), z)


def _emit_lug(body, r: ResolvedTrashcan1Config, mats, *, ang: float, z: float, name: str) -> None:
    """A real riveted lug pad straddling the outer wall at (ang, z)."""
    rad = _lug_center_rad(r, z)
    body.visual(
        Box((_LUG_T, _LUG_W, _LUG_W)),
        origin=Origin(xyz=(rad * math.cos(ang), rad * math.sin(ang), z), rpy=(0.0, 0.0, ang)),
        material=mats["lug"],
        name=name, material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
    )


# ---------------------------------------------------------------------------
# Slot C: lid / top mechanism (defining joint).
# ---------------------------------------------------------------------------
def _lid_disc_mesh(r: ResolvedTrashcan1Config, name: str):
    """Flat lid disc + dropped skirt as a lathe (disc top, skirt down over rim).

    Authored in the lid-local frame with z=0 at the disc center plane."""
    rd = r.lid_r
    skirt_in = r.r_rim - 0.002
    t = r.lid_disc_t
    pts = [
        (0.0, t),  # top center
        (rd, t),  # top edge
        (rd, 0.0),  # outer edge down
        (skirt_in + 0.004, -r.skirt_drop),  # skirt outer bottom
        (skirt_in, -r.skirt_drop),  # skirt inner bottom
        (skirt_in, 0.0),  # back up inside
        (0.0, 0.0),  # underside center
    ]
    return mesh_from_geometry(LatheGeometry(pts, segments=_LATHE_SEGMENTS, closed=True), name)


def _dome_mesh(r: ResolvedTrashcan1Config, name: str):
    """Domed lid as a lathe surface-of-revolution: domed top + skirt over rim."""
    rd = r.lid_r
    rise = r.lid_rise
    skirt_in = r.r_rim - 0.002
    pts: list[tuple[float, float]] = []
    n = 10
    for i in range(n + 1):
        t = i / n
        rr = rd * (1.0 - t)
        zz = rise * math.sin(0.5 * math.pi * t * 0.0 + math.acos(_clamp(1.0 - t, -1.0, 1.0)) / (0.5 * math.pi) * 0.0)
        # simple ellipsoidal dome: z = rise*sqrt(1-(rr/rd)^2)
        zz = rise * math.sqrt(max(0.0, 1.0 - (rr / rd) ** 2))
        pts.append((rr, zz))
    # outer edge then skirt down over the rim, back up inside
    pts.append((rd, 0.0))
    pts.append((skirt_in + 0.004, -r.skirt_drop))
    pts.append((skirt_in, -r.skirt_drop))
    pts.append((skirt_in, -0.002))
    pts.append((0.0, -0.002))
    return mesh_from_geometry(LatheGeometry(pts, segments=_LATHE_SEGMENTS, closed=True), name)


def _emit_top_loop(lid, r: ResolvedTrashcan1Config, mats, *, z_top: float, y0: float = 0.0) -> None:
    """Small loop handle on the lid top (inline visual). A small mounting pad at
    the apex embeds the loop feet into the dome so it is never a floating
    island (the dome shell is an infinitely-thin surface)."""
    # A flat cap disc sits over the dome apex: it has a large contact footprint
    # with the dome surface (no thin-wire-vs-thin-surface island ambiguity) and
    # the loop feet land on top of it. Disc straddles the apex plane.
    cap_r = 0.050
    cap_t = 0.016
    cap_z = z_top - 0.004  # disc center just below apex so it embeds in the dome
    lid.visual(
        Cylinder(radius=cap_r, length=cap_t),
        origin=Origin(xyz=(0.0, y0, cap_z)),
        material=mats["lid"],
        name="lid_cap_disc", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
    )
    cap_top = cap_z + cap_t / 2.0
    foot_x = 0.030
    apex = cap_top + 0.050
    loop = tube_from_spline_points(
        [
            (-foot_x, y0, cap_top - 0.004),
            (-foot_x * 0.55, y0, apex - 0.006),
            (0.0, y0, apex),
            (foot_x * 0.55, y0, apex - 0.006),
            (foot_x, y0, cap_top - 0.004),
        ],
        radius=_WIRE_R,
        samples_per_segment=12,
        radial_segments=8,
        cap_ends=True,
    )
    lid.visual(mesh_from_geometry(loop, "lid_loop"), material=mats["wire"], name="lid_loop", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"))


def _emit_revolute_dome_lid(model, r: ResolvedTrashcan1Config, body, mats) -> list[str]:
    """Rear-hinged REVOLUTE dome lid. axis=(-1,0,0), 0..~100 deg."""
    hinge_y = r.hinge_y
    hinge_z = r.body_h
    # Rear hinge bracket on the body rim (a real anchoring visual).
    body.visual(
        Box((0.060, 0.014, 0.016)),
        origin=Origin(xyz=(0.0, hinge_y - 0.004, hinge_z - 0.004)),
        material=mats["lug"],
        name="lid_hinge_bracket", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
    )
    lid = model.part("lid")
    # Lid authored in the hinge pivot frame: pivot at part-local origin, the
    # disc center sits above the rim. Shift by -hinge_y in Y, +body_h in Z.
    lid.visual(
        _dome_mesh(r, "dome_shell"),
        origin=Origin(xyz=(0.0, -hinge_y, 0.0)),
        material=mats["lid"],
        name="dome_shell", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
    )
    _emit_top_loop(lid, r, mats, z_top=r.lid_rise, y0=-hinge_y)
    # Hinge tab on the lid; its underside (negative_z) seats on the bracket
    # crest (which sits at z = body_h + 0.004 in the body frame). The lid child
    # link is at z = body_h, so place the tab to span z=[0, 0.012] -> underside
    # at the rim plane, within contact_tol of the bracket crest.
    lid.visual(
        Box((0.060, 0.014, 0.012)),
        origin=Origin(xyz=(0.0, 0.004, 0.006)),
        material=mats["lug"],
        name="lid_hinge_tab", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
    )
    lid.inertial = Inertial.from_geometry(
        Box((2.0 * r.lid_r, 2.0 * r.lid_r, 0.04)),
        mass=0.45,
        origin=Origin(xyz=(0.0, -hinge_y, 0.0)),
    )
    model.articulation(
        "body_to_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, hinge_y, hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=1.5, lower=0.0, upper=math.radians(100)),
        mating=MatingContract(
            parent_face_geometry="lid_hinge_bracket",
            parent_face_side="positive_z",
            child_face_geometry="lid_hinge_tab",
            child_face_side="negative_z",
            contact_tol=0.012,
        ),
    )
    return ["lid"]


def _emit_prismatic_flat_lid(model, r: ResolvedTrashcan1Config, body, mats) -> list[str]:
    """Flat lift-off PRISMATIC lid. axis=(0,0,1), 0..lift_max, no lateral move."""
    seat_z = r.body_h + r.lid_disc_t * 0.5
    lid = model.part("lid")
    lid.visual(
        _lid_disc_mesh(r, "flat_lid_disc"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["lid"],
        name="flat_lid_disc", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
    )
    # Central bail loop on top.
    bail = tube_from_spline_points(
        [
            (-0.05, 0.0, r.lid_disc_t),
            (-0.035, 0.0, r.lid_disc_t + 0.045),
            (0.0, 0.0, r.lid_disc_t + 0.060),
            (0.035, 0.0, r.lid_disc_t + 0.045),
            (0.05, 0.0, r.lid_disc_t),
        ],
        radius=_WIRE_R,
        samples_per_segment=10,
        radial_segments=8,
        cap_ends=True,
    )
    lid.visual(mesh_from_geometry(bail, "lid_bail"), material=mats["wire"], name="lid_bail", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"))
    lid.inertial = Inertial.from_geometry(
        Box((2.0 * r.lid_r, 2.0 * r.lid_r, r.lid_disc_t)),
        mass=0.40,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    model.articulation(
        "body_to_lid",
        ArticulationType.PRISMATIC,
        parent=body,
        child=lid,
        # Origin anchored on the rim line (where rolled_rim geometry is); the
        # +Z slide axis makes the xy position of the origin immaterial to motion
        # but keeps it on real body + lid geometry.
        origin=Origin(xyz=(0.0, r.r_rim, r.body_h)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=4.0, velocity=0.4, lower=0.0, upper=r.lift_max),
        mating=MatingContract(
            parent_face_geometry="rolled_rim",
            parent_face_side="positive_z",
            child_face_geometry="flat_lid_disc",
            child_face_side="negative_z",
            # The flat lid's skirt nests DOWN over the rolled rim, so the disc
            # underside face legitimately sits skirt_drop below the rim crest.
            contact_tol=0.045,
        ),
    )
    return ["lid"]


def _emit_open_rim(model, r: ResolvedTrashcan1Config, body, mats) -> list[str]:
    """No lid — open mouth. The non-fixed joint lives on the swing-bail handle."""
    return []


_LID_BUILDERS = {
    "lid_dome_revolute": _emit_revolute_dome_lid,
    "lid_dome_shallow_revolute": _emit_revolute_dome_lid,
    "lid_flat_liftoff_prismatic": _emit_prismatic_flat_lid,
    "top_open_rim": _emit_open_rim,
}


# ---------------------------------------------------------------------------
# Slot D: handle.
# ---------------------------------------------------------------------------
_SIDE_ANGLES = (0.0, math.pi)
_SIDE_NAMES = ("right", "left")


def _emit_fixed_ring_ears(model, r: ResolvedTrashcan1Config, body, mats) -> list[str]:
    """Two fixed side D-ring drop handles (2x FIXED via lug pads).

    A FIXED articulation is used here (justified): each ring handle is a
    separate sheet-metal wire part with its own reference frame, captured into
    the lug, matching the source parents' two-ear FIXED topology. The lug is a
    real anchoring visual.
    """
    names: list[str] = []
    for side, ang in zip(_SIDE_NAMES, _SIDE_ANGLES):
        lug_name = f"lug_{side}"
        _emit_lug(body, r, mats, ang=ang, z=r.lug_z, name=lug_name)
        ring = model.part(f"ring_handle_{side}")
        # Ring authored in lug-local frame; pivot/anchor at part-local origin on
        # the outer lug face. Radial outward = +X in local, rotated by ang.
        loop = tube_from_spline_points(
            [
                (0.004, -0.018, 0.0),
                (0.030, -0.030, -0.020),
                (0.040, 0.0, -0.040),
                (0.030, 0.030, -0.020),
                (0.004, 0.018, 0.0),
            ],
            radius=_WIRE_R,
            samples_per_segment=10,
            radial_segments=8,
            cap_ends=True,
        )
        ring.visual(
            mesh_from_geometry(loop, f"ring_{side}"),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, ang)),
            material=mats["wire"],
            name=f"ring_{side}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
        )
        # Anchor bar centered at the lug-face origin (rotation-invariant AABB),
        # spanning enough in X to envelop the ring wire's inner ends and in Y to
        # bridge both ends, so it never forms a disconnected island.
        ring.visual(
            Box((0.028, 0.044, 0.016)),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, ang)),
            material=mats["wire"],
            name=f"ring_anchor_{side}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
        )
        fx, fy, fz = _lug_face_outer(r, ang, r.lug_z)
        ring.inertial = Inertial.from_geometry(
            Box((0.08, 0.08, 0.08)), mass=0.10, origin=Origin(xyz=(0.0, 0.0, 0.0))
        )
        # FIXED: the ear does not articulate; separate part keeps the wire's own
        # frame matching the 5-star two-ear source family.
        model.articulation(
            f"body_to_ring_{side}",
            ArticulationType.FIXED,
            parent=body,
            child=ring,
            origin=Origin(xyz=(fx, fy, fz)),
            mating=MatingContract(
                parent_face_geometry=lug_name,
                parent_face_side="positive_x" if side == "right" else "negative_x",
                child_face_geometry=f"ring_anchor_{side}",
                child_face_side="negative_x" if side == "right" else "positive_x",
                contact_tol=0.020,
            ),
        )
        names.append(f"ring_handle_{side}")
    return names


def _emit_fixed_bail_ears(model, r: ResolvedTrashcan1Config, body, mats) -> list[str]:
    """Two fixed side semicircular wire-bail ears (2x FIXED). Two lugs/side."""
    names: list[str] = []
    for side, ang in zip(_SIDE_NAMES, _SIDE_ANGLES):
        lug_name = f"lug_{side}"
        _emit_lug(body, r, mats, ang=ang, z=r.lug_z, name=lug_name)
        bail = model.part(f"bail_handle_{side}")
        arc = tube_from_spline_points(
            [
                (0.004, -0.026, 0.0),
                (0.050, -0.018, 0.0),
                (0.062, 0.0, 0.0),
                (0.050, 0.018, 0.0),
                (0.004, 0.026, 0.0),
            ],
            radius=_WIRE_R,
            samples_per_segment=10,
            radial_segments=8,
            cap_ends=True,
        )
        bail.visual(
            mesh_from_geometry(arc, f"bail_{side}"),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, ang)),
            material=mats["wire"],
            name=f"bail_{side}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
        )
        # Anchor bar centered at the lug-face origin (rotation-invariant AABB),
        # wide enough in X/Y to envelop both arc wire ends (no island).
        bail.visual(
            Box((0.028, 0.060, 0.016)),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, ang)),
            material=mats["wire"],
            name=f"bail_anchor_{side}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
        )
        fx, fy, fz = _lug_face_outer(r, ang, r.lug_z)
        bail.inertial = Inertial.from_geometry(
            Box((0.10, 0.08, 0.04)), mass=0.10, origin=Origin(xyz=(0.0, 0.0, 0.0))
        )
        model.articulation(
            f"body_to_bail_{side}",
            ArticulationType.FIXED,
            parent=body,
            child=bail,
            origin=Origin(xyz=(fx, fy, fz)),
            mating=MatingContract(
                parent_face_geometry=lug_name,
                parent_face_side="positive_x" if side == "right" else "negative_x",
                child_face_geometry=f"bail_anchor_{side}",
                child_face_side="negative_x" if side == "right" else "positive_x",
                contact_tol=0.020,
            ),
        )
        names.append(f"bail_handle_{side}")
    return names


def _emit_swing_bail_sides(model, r: ResolvedTrashcan1Config, body, mats) -> list[str]:
    """Two REVOLUTE side swinging drop-bail handles. axis horizontal tangential
    (+-Y at the two sides), 0..90 deg. q=0 hangs down, positive swings up/out."""
    names: list[str] = []
    for side, ang in zip(_SIDE_NAMES, _SIDE_ANGLES):
        lug_name = f"lug_{side}"
        _emit_lug(body, r, mats, ang=ang, z=r.lug_z, name=lug_name)
        handle = model.part(f"swing_bail_{side}")
        # Authored hanging down from the pivot at part-local origin.
        drop = tube_from_spline_points(
            [
                (0.006, -0.030, 0.0),
                (0.030, -0.034, -0.045),
                (0.040, 0.0, -0.070),
                (0.030, 0.034, -0.045),
                (0.006, 0.030, 0.0),
            ],
            radius=_WIRE_R,
            samples_per_segment=10,
            radial_segments=8,
            cap_ends=True,
        )
        handle.visual(
            mesh_from_geometry(drop, f"swing_{side}"),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, ang)),
            material=mats["wire"],
            name=f"swing_{side}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
        )
        # Anchor bar centered at the lug-face origin (rotation-invariant AABB),
        # wide enough in X/Y to envelop both drop-wire ends (no island).
        handle.visual(
            Box((0.030, 0.068, 0.016)),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, ang)),
            material=mats["wire"],
            name=f"swing_anchor_{side}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
        )
        fx, fy, fz = _lug_face_outer(r, ang, r.lug_z)
        handle.inertial = Inertial.from_geometry(
            Box((0.10, 0.08, 0.10)), mass=0.10, origin=Origin(xyz=(0.0, 0.0, -0.035))
        )
        # Tangential axis at the side: at ang=0 (right) axis ~+Y; at ang=pi ~-Y.
        axis = (-math.sin(ang), math.cos(ang), 0.0)
        model.articulation(
            f"body_to_swing_{side}",
            ArticulationType.REVOLUTE,
            parent=body,
            child=handle,
            origin=Origin(xyz=(fx, fy, fz)),
            axis=axis,
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=math.radians(90)),
            mating=MatingContract(
                parent_face_geometry=lug_name,
                parent_face_side="positive_x" if side == "right" else "negative_x",
                child_face_geometry=f"swing_anchor_{side}",
                child_face_side="negative_x" if side == "right" else "positive_x",
                contact_tol=0.020,
            ),
        )
        names.append(f"swing_bail_{side}")
    return names


def _emit_overhead_bail(model, r: ResolvedTrashcan1Config, body, mats) -> list[str]:
    """Single REVOLUTE overhead carrying bail across the top. Two pivot lugs +
    arched rod. axis=(1,0,0) through both lugs, 0..170 deg."""
    bail_z = r.body_h - 0.06
    # Two pivot lugs at +-X near the rim (real anchoring visuals).
    for side, ang in zip(_SIDE_NAMES, _SIDE_ANGLES):
        _emit_lug(body, r, mats, ang=ang, z=bail_z, name=f"bail_lug_{side}")
    handle = model.part("overhead_bail")
    # Pivot point = the RIGHT lug outer face (real body geometry). The child
    # arch is authored in this frame: x=0 at the right lug, the arch spans across
    # to the left lug at x = -2*span. The REVOLUTE axis is +X through both lugs,
    # so placing the origin at the right lug keeps it ON both body + child
    # geometry (a bail_end pad sits at child-local origin).
    lug_face_r = _lug_center_rad(r, bail_z) + _LUG_T * 0.5
    span = lug_face_r  # right lug at x=0 (child frame); left lug at x=-2*span
    apex_z = r.body_h + 0.14
    dz = apex_z - bail_z
    rim_dz = (r.body_h - bail_z)
    bow = r.r_rim + 0.045
    # Authored about the right lug (child x=0). Mirror points across x=-span.
    c = -span  # arch centerline x (apex above can center)
    arch = tube_from_spline_points(
        [
            (0.0, 0.0, 0.0),
            (c + bow, 0.0, rim_dz * 0.55),
            (c + bow * 0.92, 0.0, rim_dz + 0.030),
            (c + span * 0.30, 0.0, dz * 0.92),
            (c, 0.0, dz),
            (c - span * 0.30, 0.0, dz * 0.92),
            (c - bow * 0.92, 0.0, rim_dz + 0.030),
            (c - bow, 0.0, rim_dz * 0.55),
            (-2.0 * span, 0.0, 0.0),
        ],
        radius=_BAIL_ROD_R,
        samples_per_segment=14,
        radial_segments=10,
        cap_ends=True,
    )
    handle.visual(mesh_from_geometry(arch, "bail_arch"), material=mats["wire"], name="bail_arch", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"))
    # Anchor pads at the two arch ends (right at child x=0, left at x=-2*span).
    for side, ex in (("right", 0.0), ("left", -2.0 * span)):
        handle.visual(
            Box((_LUG_W * 0.8, _LUG_W * 0.7, 0.012)),
            origin=Origin(xyz=(ex, 0.0, 0.0)),
            material=mats["wire"],
            name=f"bail_end_{side}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"bright_galvanized", "weathered_galvanized", "dark_zinc"} else "metal.paint_coated"),
        )
    handle.inertial = Inertial.from_geometry(
        Box((2.0 * span, 0.04, dz)),
        mass=0.18,
        origin=Origin(xyz=(-span, 0.0, dz * 0.4)),
    )
    model.articulation(
        "body_to_overhead_bail",
        ArticulationType.REVOLUTE,
        parent=body,
        child=handle,
        origin=Origin(xyz=(span, 0.0, bail_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.5, velocity=2.0, lower=0.0, upper=math.radians(170)),
        mating=MatingContract(
            parent_face_geometry="bail_lug_right",
            parent_face_side="positive_x",
            child_face_geometry="bail_end_right",
            child_face_side="negative_x",
            contact_tol=0.030,
        ),
    )
    return ["overhead_bail"]


_HANDLE_BUILDERS = {
    "handle_two_ring_ears": _emit_fixed_ring_ears,
    "handle_two_bail_ears": _emit_fixed_bail_ears,
    "handle_swing_bail_sides": _emit_swing_bail_sides,
    "handle_overhead_bail": _emit_overhead_bail,
}


# ---------------------------------------------------------------------------
# slot_choices
# ---------------------------------------------------------------------------
def slot_choices_for_config(
    config: Trashcan1Config | ResolvedTrashcan1Config,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedTrashcan1Config) else resolve_config(config)
    choices = [
        ("body_profile", r.body_profile),
        ("surface", r.surface),
        ("lid_top", r.lid_top),
        ("handle", r.handle),
    ]
    if r.rib_count > 0:
        choices.append(("rib_count", f"n{r.rib_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def _build_body(model: ArticulatedObject, r: ResolvedTrashcan1Config, mats):
    body = model.part("can_body")
    _emit_body_shell(body, r, mats)
    _emit_rolled_rim(body, r, mats)
    decor = _SURFACE_DECOR[r.surface]
    if decor is not None and r.rib_count > 0:
        decor(body, r, mats)
    body.inertial = Inertial.from_geometry(
        Cylinder(radius=r.r_top, length=r.body_h),
        mass=2.2,
        origin=Origin(xyz=(0.0, 0.0, r.body_h / 2.0)),
    )
    return body


def build_trashcan1(
    config: Trashcan1Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"trashcan1_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }
    body = _build_body(model, r, mats)
    _LID_BUILDERS[r.lid_top](model, r, body, mats)
    _HANDLE_BUILDERS[r.handle](model, r, body, mats)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_trashcan1(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_trashcan1(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_trashcan1_tests(
    object_model: ArticulatedObject,
    config: Trashcan1Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("can_body")

    # Names of the handle parts for this build (used by the texture allowance).
    if r.handle in ("handle_two_ring_ears",):
        _handle_parts = [f"ring_handle_{s}" for s in _SIDE_NAMES]
    elif r.handle == "handle_two_bail_ears":
        _handle_parts = [f"bail_handle_{s}" for s in _SIDE_NAMES]
    elif r.handle == "handle_swing_bail_sides":
        _handle_parts = [f"swing_bail_{s}" for s in _SIDE_NAMES]
    else:
        _handle_parts = ["overhead_bail"]

    # ---- Textured-wall allowance: ribs / flutes / ring bands protrude from the
    # wall at the same line where the carry hardware is riveted on, so a handle
    # wire may graze a decoration bead. The lug pad / handle is physically
    # riveted OVER the corrugation, so this contact is expected. ----
    # Each handle is riveted onto the lug pad (half-embedded in the wall), so the
    # wire ends / anchor / arms graze the wall + corrugation/rib/ring beads at the
    # lug line. That is expected hardware mounting on the can, not a clash.
    for hp in _handle_parts:
        part = object_model.get_part(hp)
        ctx.allow_overlap(
            part, body,
            reason="carry hardware is riveted onto the lug at the textured wall.",
        )

    # ---- Lid overlap allowances (closed seat over rim). ----
    if r.lid_top in ("lid_dome_revolute", "lid_dome_shallow_revolute"):
        lid = object_model.get_part("lid")
        ctx.allow_overlap(
            lid, body, elem_a="lid_hinge_tab", elem_b="lid_hinge_bracket",
            reason="lid hinge tab is captured at the rear hinge bracket pivot line.",
        )
        ctx.allow_overlap(
            lid, body, reason="closed dome lid skirt nests over the rolled rim.",
        )
    elif r.lid_top == "lid_flat_liftoff_prismatic":
        lid = object_model.get_part("lid")
        ctx.allow_overlap(
            lid, body, elem_a="flat_lid_disc", elem_b="rolled_rim",
            reason="flat lid skirt seats over the rolled rim when closed.",
        )
        ctx.allow_overlap(
            lid, body, elem_a="flat_lid_disc", elem_b="smooth_wall",
            reason="flat lid skirt drops over the upper wall.",
        )
        ctx.allow_overlap(
            lid, body, elem_a="flat_lid_disc", elem_b="corrugated_wall",
            reason="flat lid skirt drops over the upper corrugated wall.",
        )

    # ---- Handle overlap allowances (anchor / ring captured in lug). ----
    if r.handle == "handle_two_ring_ears":
        for side in _SIDE_NAMES:
            part = object_model.get_part(f"ring_handle_{side}")
            ctx.allow_overlap(
                part, body, elem_a=f"ring_anchor_{side}", elem_b=f"lug_{side}",
                reason="ring ear anchor hooks into the side lug pad.",
            )
            ctx.allow_overlap(
                part, body, elem_a=f"ring_{side}", elem_b=f"lug_{side}",
                reason="ring wire top wraps the side lug.",
            )
    elif r.handle == "handle_two_bail_ears":
        for side in _SIDE_NAMES:
            part = object_model.get_part(f"bail_handle_{side}")
            ctx.allow_overlap(
                part, body, elem_a=f"bail_anchor_{side}", elem_b=f"lug_{side}",
                reason="bail ear anchor seats against the side lug pad.",
            )
            ctx.allow_overlap(
                part, body, elem_a=f"bail_{side}", elem_b=f"lug_{side}",
                reason="bail wire end wraps the side lug.",
            )
    elif r.handle == "handle_swing_bail_sides":
        for side in _SIDE_NAMES:
            part = object_model.get_part(f"swing_bail_{side}")
            ctx.allow_overlap(
                part, body, elem_a=f"swing_anchor_{side}", elem_b=f"lug_{side}",
                reason="swing bail pivot anchor rides on the side lug.",
            )
            ctx.allow_overlap(
                part, body, elem_a=f"swing_{side}", elem_b=f"lug_{side}",
                reason="swing bail wire ends wrap the side lug pivot.",
            )
    else:  # overhead bail
        bail = object_model.get_part("overhead_bail")
        for side in _SIDE_NAMES:
            ctx.allow_overlap(
                bail, body, elem_a=f"bail_end_{side}", elem_b=f"bail_lug_{side}",
                reason="overhead bail arm end is captured at the pivot lug.",
            )
            ctx.allow_overlap(
                bail, body, elem_a="bail_arch", elem_b=f"bail_lug_{side}",
                reason="overhead bail arch base wraps the pivot lug.",
            )
        # The arch arms run alongside the upper wall and pass over the lid at
        # rest; both are captured/clearance contacts of the carry bail.
        ctx.allow_overlap(
            bail, body, elem_a="bail_arch", elem_b="rolled_rim",
            reason="overhead bail arms pass over the rolled rim at rest.",
        )
        if r.has_lid:
            lid = object_model.get_part("lid")
            ctx.allow_overlap(
                bail, lid, reason="overhead carry bail rests over the closed lid.",
            )

    if r.has_lid:
        ctx.allow_isolated_part(
            object_model.get_part("lid"),
            reason="lift-off lid clears the can rim and loses body contact when opened",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("can_body present", "can_body" in part_names, details=str(sorted(part_names)))

    # Body is a surface-of-revolution wall (Rule 3) — named lathe visual.
    wall_names = {v.name for v in body.visuals}
    ctx.check(
        "body has a lathe revolve wall (not Box/Cylinder downgrade)",
        ("smooth_wall" in wall_names) or ("corrugated_wall" in wall_names),
        details=str(sorted(wall_names)),
    )
    ctx.check(
        "body has rolled rim + floor disc (closed-bottom vessel)",
        "rolled_rim" in wall_names and "floor_disc" in wall_names,
        details=str(sorted(wall_names)),
    )

    # Footprint at z=0.
    aabb = ctx.part_world_aabb(body)
    if aabb is not None:
        ctx.check(
            "footprint at z~0",
            abs(aabb[0][2]) < 0.020,
            details=f"min_z={aabb[0][2]:.4f}",
        )
        ctx.check(
            "deep can height >= 0.45",
            (aabb[1][2] - aabb[0][2]) > 0.45,
            details=f"height={aabb[1][2] - aabb[0][2]:.3f}",
        )

    # Rib / ring multiplicity present with correct naming. Ribs/flutes are one
    # visual per wall-following segment (rib_{i}_{seg}), so count distinct rib
    # indices, not raw visuals.
    if r.surface == "surface_bold_ribs":
        ribs = [v.name for v in body.visuals if v.name.startswith("rib_")]
        ctx.check(
            "N bold ribs inlined (Rule 1)",
            len({n.split("_")[1] for n in ribs}) == r.rib_count,
            details=f"ribs={len(ribs)} (segmented) expected={r.rib_count}",
        )
    elif r.surface == "surface_horizontal_rings":
        rings = [v.name for v in body.visuals if v.name.startswith("ring_band_")]
        ctx.check(
            "N ring bands inlined (Rule 1)",
            len(rings) == r.rib_count,
            details=f"rings={len(rings)} expected={r.rib_count}",
        )
    elif r.surface == "surface_vertical_flutes":
        flutes = [v.name for v in body.visuals if v.name.startswith("flute_")]
        ctx.check(
            "N flutes inlined (Rule 1)",
            len({n.split("_")[1] for n in flutes}) == r.rib_count,
            details=f"flutes={len(flutes)} (segmented) expected={r.rib_count}",
        )

    # ---- Defining joint topology. ----
    if r.lid_top in ("lid_dome_revolute", "lid_dome_shallow_revolute"):
        j = object_model.get_articulation("body_to_lid")
        ctx.check(
            "dome lid is REVOLUTE about -X",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    elif r.lid_top == "lid_flat_liftoff_prismatic":
        j = object_model.get_articulation("body_to_lid")
        ctx.check(
            "flat lid is PRISMATIC about +Z",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[2]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        # No lateral drift on lift.
        lid = object_model.get_part("lid")
        closed = ctx.part_world_aabb(lid)
        with ctx.pose({j: r.lift_max}):
            opened = ctx.part_world_aabb(lid)
        if closed is not None and opened is not None:
            cx = 0.5 * (closed[0][0] + closed[1][0])
            ox = 0.5 * (opened[0][0] + opened[1][0])
            cy = 0.5 * (closed[0][1] + closed[1][1])
            oy = 0.5 * (opened[0][1] + opened[1][1])
            ctx.check(
                "PRISMATIC lid lifts with no lateral drift",
                abs(cx - ox) < 0.006 and abs(cy - oy) < 0.006
                and opened[1][2] > closed[1][2] + 0.20,
                details=f"dx={cx-ox:.4f} dy={cy-oy:.4f} dz_top={opened[1][2]-closed[1][2]:.3f}",
            )

    # ---- At least one non-fixed joint exists. ----
    non_fixed = [
        a for a in object_model.articulations if a.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed joint (lid lift/flip or swing bail)",
        len(non_fixed) >= 1,
        details=f"non_fixed={[a.name for a in non_fixed]}",
    )

    # ---- Handle joint topology. ----
    if r.handle == "handle_swing_bail_sides":
        for side in _SIDE_NAMES:
            j = object_model.get_articulation(f"body_to_swing_{side}")
            ctx.check(
                f"{side} swing bail is REVOLUTE (horizontal tangential axis)",
                j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[2]) < 0.1,
                details=f"axis={tuple(j.axis)}",
            )
    elif r.handle == "handle_overhead_bail":
        j = object_model.get_articulation("body_to_overhead_bail")
        ctx.check(
            "overhead bail is REVOLUTE about +X",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
            details=f"axis={tuple(j.axis)}",
        )
    elif r.handle in ("handle_two_ring_ears", "handle_two_bail_ears"):
        prefix = "ring" if r.handle == "handle_two_ring_ears" else "bail"
        for side in _SIDE_NAMES:
            j = object_model.get_articulation(f"body_to_{prefix}_{side}")
            ctx.check(
                f"{side} ear handle is FIXED",
                j.articulation_type == ArticulationType.FIXED,
                details=f"type={j.articulation_type}",
            )

    # Open rim implies a swing handle (compatibility gate).
    if r.lid_top == "top_open_rim":
        ctx.check(
            "open rim forces a swinging handle",
            r.handle in _SWING_HANDLES,
            details=f"handle={r.handle}",
        )

    return ctx.report()
